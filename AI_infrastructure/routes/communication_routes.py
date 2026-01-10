"""
FILE: AI_infrastructure/routes/communication_routes.py
PURPOSE: Communication Hub backend routes - Unified API for Gmail and Outlook

FIXED: 2025-01-XX - Critical cursor leak repair
CHANGES:
- Fixed get_thread_emails() - added proper cursor management
- Added cursor = None and conn = None initialization
- Added try/finally block for guaranteed cleanup
- Added cursor.close() BEFORE conn.close()
- All other functions already safe (use external wrappers)

FEATURES:
- List connected accounts (Gmail + Outlook)
- Unified inbox from multiple providers
- Send emails via selected account
- Search emails across accounts
- Mark as read/unread
- Delete emails

DEPENDENCIES:
- Flask Blueprint
- CredentialInjector (for OAuth credentials)
- gmail.py (Gmail API wrapper)
- microsoft_outlook_tools.py (Outlook API wrapper)

EXPORTS:
- communication_bp (Flask Blueprint)

ROUTES:
- GET  /api/communication-hub/accounts - List connected email accounts
- GET  /api/communication-hub/emails - List emails from selected account(s)
- GET  /api/communication-hub/emails/<id> - Get full email content
- POST /api/communication-hub/send - Send email via selected account
- POST /api/communication-hub/emails/<id>/read - Mark email as read
- POST /api/communication-hub/emails/<id>/unread - Mark email as unread
- GET  /api/communication-hub/search - Search emails across accounts
- DELETE /api/communication-hub/emails/<id> - Delete email

LAST MODIFIED: 2025-11-10 - Initial creation
"""

from flask import Blueprint, request, jsonify
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# ✅ FIX: Import CredentialInjector instead of UserAuthManager (same as agent routes)
sys.path.insert(0, str(Path(__file__).parent.parent))
from auth.user_auth import UserAuthManager
from auth.user_auth import require_auth

from google_workspace.gmail import (
    gmail_list_messages, 
    gmail_get_message,  # Used to fetch full message details (already imported)
    gmail_get_attachment,  # NEW: Download Gmail attachments
    gmail_send_email,
    gmail_mark_as_read,
    gmail_delete_message,
    gmail_search_messages
)

# Setup logging
from utils.logger_config import setup_logger, log_warning, log_init
logger = setup_logger('routes.communication_routes')

# 🔒 Circuit breaker to prevent cascading failures
from AI_infrastructure.shared.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError

# Create circuit breakers for each OAuth provider
gmail_circuit = CircuitBreaker(
    name='gmail_oauth_check',
    failure_threshold=3,      # Open after 3 failures (prevents pool exhaustion)
    recovery_timeout=30,      # Try again after 30 seconds
    expected_exception=Exception
)

outlook_circuit = CircuitBreaker(
    name='outlook_oauth_check',
    failure_threshold=3,
    recovery_timeout=30,
    expected_exception=Exception
)

# Microsoft Outlook imports
try:
    from tools.implementations.microsoft_outlook_tools import (
        microsoft_outlook_list_messages,
        microsoft_outlook_get_message,
        microsoft_outlook_send_email
    )
    OUTLOOK_AVAILABLE = True
except ImportError:
    log_warning(logger, "Microsoft Outlook tools not available")
    OUTLOOK_AVAILABLE = False

# Create Blueprint
communication_bp = Blueprint('communication', __name__, url_prefix='/api/communication-hub')

# Initialize UserAuthManager for credential checks
auth_manager = UserAuthManager()


@communication_bp.route('/accounts', methods=['GET'])
@require_auth
def get_accounts():
    """
    Get all connected email accounts for logged-in user
    Uses CredentialInjector to check oauth_tokens table
    
    Returns:
        JSON with list of connected accounts (Gmail, Outlook) with OAuth status
    
    ✅ NO DATABASE OPERATIONS - Safe (uses auth_manager)
    """
    # Prefer the authenticated user from @require_auth decorator
    user_data = getattr(request, 'user', None)
    if user_data:
        user_id = user_data.get('user_id')
    else:
        user_id = request.args.get('user_id', 1, type=int)

    print(f"[Communication Hub] 📧 Getting accounts for user_id={user_id}")
    
    accounts = []
    
    # ✅ FIX: Check Google OAuth credentials FROM ai_infrastructure.oauth_tokens table
    try:
        google_creds = auth_manager.get_user_google_oauth_credentials(user_id)
        if google_creds:
            # Get email from token metadata or use default
            email = google_creds.get('email', google_creds.get('client_id', 'Gmail Account'))
            accounts.append({
                'id': 'gmail',
                'provider': 'gmail',
                'email': email,
                'name': 'Gmail',
                'connected': True,
                'has_oauth': True
            })
            print(f"[Communication Hub] ✅ Found Google OAuth for user {user_id}: {email}")
        else:
            print(f"[Communication Hub] ⚠️  No Google OAuth tokens for user {user_id}")
    except Exception as e:
        logger.error(f"[Communication Hub] ❌ Error checking Gmail credentials: {e}")
        print(f"[Communication Hub] ❌ Error checking Gmail credentials: {e}")
    
    # ✅ FIX: Check Microsoft OAuth credentials FROM ai_infrastructure.oauth_tokens table
    if OUTLOOK_AVAILABLE:
        try:
            microsoft_creds = auth_manager.get_user_microsoft_oauth_credentials(user_id)
            if microsoft_creds:
                # Get email from token metadata or use default
                email = microsoft_creds.get('email', microsoft_creds.get('microsoft_email', 'Outlook Account'))
                accounts.append({
                    'id': 'outlook',
                    'provider': 'outlook',
                    'email': email,
                    'name': 'Outlook',
                    'connected': True,
                    'has_oauth': True
                })
                print(f"[Communication Hub] ✅ Found Microsoft OAuth for user {user_id}: {email}")
            else:
                print(f"[Communication Hub] ⚠️  No Microsoft OAuth tokens for user {user_id}")
        except Exception as e:
            logger.error(f"[Communication Hub] ❌ Error checking Outlook credentials: {e}")
            print(f"[Communication Hub] ❌ Error checking Outlook credentials: {e}")
    
    print(f"[Communication Hub] 📋 Returning {len(accounts)} account(s)")
    
    return jsonify({
        'success': True,
        'accounts': accounts,
        'count': len(accounts),
        'user_id': user_id
    })


@communication_bp.route('/emails', methods=['GET'])
@require_auth
def list_emails():
    """
    List emails from selected account(s)
    
    Query params:
        - user_id: User ID (default: 1)
        - account: Account ID ('all', 'gmail', 'outlook')
        - limit: Max emails to return (default: 50)
    
    Returns:
        JSON with unified list of emails
    
    ✅ NO DATABASE OPERATIONS - Safe (uses gmail/outlook wrappers)
    """
    # Prefer authenticated user
    user_data = getattr(request, 'user', None)
    if user_data:
        user_id = user_data.get('user_id')
    else:
        user_id = request.args.get('user_id', 1, type=int)
    account = request.args.get('account', 'all')
    limit = request.args.get('limit', 50, type=int)
    
    print(f"[Communication Hub] 📬 Listing emails: user_id={user_id}, account={account}, limit={limit}")
    
    # ✅ FIRST: Check which accounts user has connected (with circuit breaker protection)
    has_google = False
    has_microsoft = False
    
    # 🔒 Check Google OAuth with circuit breaker
    try:
        @gmail_circuit.call
        def check_google_oauth():
            return auth_manager.get_user_google_oauth_credentials(user_id)
        
        google_creds = check_google_oauth()
        has_google = google_creds is not None
        print(f"[Communication Hub] 🔍 User {user_id} has Google OAuth: {has_google}")
    except CircuitBreakerOpenError as e:
        print(f"[Communication Hub] 🚫 Gmail circuit breaker OPEN: {e}")
        has_google = False
    except Exception as e:
        print(f"[Communication Hub] ⚠️  Error checking Google OAuth: {e}")
        has_google = False
    
    # 🔒 Check Microsoft OAuth with circuit breaker
    try:
        @outlook_circuit.call
        def check_microsoft_oauth():
            return auth_manager.get_user_microsoft_oauth_credentials(user_id)
        
        microsoft_creds = check_microsoft_oauth()
        has_microsoft = microsoft_creds is not None
        print(f"[Communication Hub] 🔍 User {user_id} has Microsoft OAuth: {has_microsoft}")
    except CircuitBreakerOpenError as e:
        print(f"[Communication Hub] 🚫 Outlook circuit breaker OPEN: {e}")
        has_microsoft = False
    except Exception as e:
        print(f"[Communication Hub] ⚠️  Error checking Microsoft OAuth: {e}")
        has_microsoft = False
    
    emails = []
    
    # ✅ Gmail: ONLY try if user has Google OAuth credentials
    if account in ['all', 'gmail'] and has_google:
        try:
            print(f"[Communication Hub] 📧 Fetching Gmail messages for user {user_id}...")
            
            # ✅ FIX: Pass _user_id and _injected_credentials flag (NOT credentials dict)
            # The Gmail service will fetch credentials from database using UserAuthManager
            gmail_result = gmail_list_messages(
                max_results=limit,
                _user_id=user_id,
                _injected_credentials=True
            )
            
            # gmail_list_messages returns {'messages': [], 'count': N, 'next_page_token': ...}
            # NOT {'success': True, ...} - check for 'messages' key instead
            if 'messages' in gmail_result:
                gmail_count = len(gmail_result.get('messages', []))
                print(f"[Communication Hub] ✅ Got {gmail_count} Gmail message IDs")
                
                # ⚡ PARALLEL FETCH: Get all message details at once using ThreadPoolExecutor
                from concurrent.futures import ThreadPoolExecutor, as_completed
                import time
                
                # ✅ FIX: Pass user_id to each worker (they'll use database credentials)
                def fetch_single_message(msg_summary, uid):
                    """Fetch a single message metadata using database credentials"""
                    try:
                        msg = gmail_get_message(
                            message_id=msg_summary['id'],
                            format='metadata',
                            _user_id=uid,
                            _injected_credentials=True
                        )
                        
                        # Parse message headers
                        headers = {h['name'].lower(): h['value'] for h in msg.get('payload', {}).get('headers', [])}
                        
                        return {
                            'id': f"gmail_{msg['id']}",
                            'provider': 'gmail',
                            'from': headers.get('from', 'Unknown'),
                            'to': headers.get('to', ''),
                            'subject': headers.get('subject', 'No Subject'),
                            'date': headers.get('date', ''),
                            'is_read': 'UNREAD' not in msg.get('labelIds', []),
                            'snippet': msg.get('snippet', ''),
                            'has_attachments': any(p.get('filename') for p in msg.get('payload', {}).get('parts', [])),
                            'thread_id': msg.get('threadId')  # ✅ Gmail conversation threading
                        }
                    except Exception as msg_err:
                        print(f"[Communication Hub] ⚠️  Failed to fetch message {msg_summary['id']}: {msg_err}")
                        return None
                
                # Execute all fetches in parallel (max 10 workers to respect connection pool limits)
                start_time = time.time()
                with ThreadPoolExecutor(max_workers=10) as executor:
                    # Submit all tasks at once with user_id
                    future_to_msg = {executor.submit(fetch_single_message, msg, user_id): msg for msg in gmail_result.get('messages', [])}
                    
                    # Collect results as they complete
                    for future in as_completed(future_to_msg):
                        result = future.result()
                        if result:
                            emails.append(result)
                
                elapsed = time.time() - start_time
                print(f"[Communication Hub] ⚡ Fetched {len(emails)} emails in {elapsed:.2f}s (parallel)")
            else:
                print(f"[Communication Hub] ⚠️  Gmail returned unexpected format: {list(gmail_result.keys())}")
        except Exception as e:
            print(f"[Communication Hub] ❌ Gmail error: {e}")
            import traceback
            traceback.print_exc()
    elif account in ['all', 'gmail'] and not has_google:
        print(f"[Communication Hub] ⏭️  Skipping Gmail - user {user_id} has no Google OAuth credentials")
    
    # ✅ Outlook: ONLY try if user has Microsoft OAuth credentials
    if account in ['all', 'outlook'] and has_microsoft and OUTLOOK_AVAILABLE:
        try:
            print(f"[Communication Hub] 📧 Fetching Outlook messages for user {user_id}...")
            outlook_result = microsoft_outlook_list_messages(
                max_results=limit,
                _user_id=user_id,
                _injected_credentials=True
            )
            
            if outlook_result.get('success'):
                outlook_count = len(outlook_result.get('messages', []))
                print(f"[Communication Hub] ✅ Got {outlook_count} Outlook message(s)")
                for msg in outlook_result.get('messages', []):
                    from_addr = msg.get('from', {})
                    if isinstance(from_addr, dict):
                        from_email = from_addr.get('emailAddress', {}).get('address', 'Unknown')
                    else:
                        from_email = str(from_addr)
                    
                    emails.append({
                        'id': f"outlook_{msg['id']}",
                        'provider': 'outlook',
                        'from': from_email,
                        'to': msg.get('toRecipients', [{}])[0].get('emailAddress', {}).get('address', '') if msg.get('toRecipients') else '',
                        'subject': msg.get('subject', 'No Subject'),
                        'date': msg.get('receivedDateTime', ''),
                        'is_read': msg.get('isRead', False),
                        'snippet': msg.get('bodyPreview', ''),
                        'has_attachments': msg.get('hasAttachments', False),
                        'thread_id': msg.get('conversationId')  # ✅ Outlook conversation threading
                    })
            else:
                print(f"[Communication Hub] ⚠️  Outlook returned no messages or error: {outlook_result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"[Communication Hub] ❌ Outlook error: {e}")
            import traceback
            traceback.print_exc()
    
    # Sort by date (newest first)
    emails.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    print(f"[Communication Hub] 📊 Returning {len(emails)} total email(s)")
    
    return jsonify({
        'success': True,
        'emails': emails,
        'count': len(emails)
    })


@communication_bp.route('/emails/<email_id>', methods=['GET'])
@require_auth
def get_email(email_id):
    """
    Get full email content with body parsing
    
    Args:
        email_id: Email ID in format 'provider_id' (e.g., 'gmail_12345')
    
    Returns:
        JSON with full email content including body_text and body_html
    
    ✅ NO DATABASE OPERATIONS - Safe (uses gmail/outlook wrappers)
    """
    user_data = getattr(request, 'user', None)
    if user_data:
        user_id = user_data.get('user_id')
    else:
        user_id = request.args.get('user_id', 1, type=int)
    
    try:
        # Parse provider and message ID with validation
        if '_' not in email_id:
            return jsonify({
                'success': False,
                'error': f'Invalid email ID format: {email_id}. Expected format: provider_messageId'
            }), 400
        
        provider, message_id = email_id.split('_', 1)
        
        if provider not in ['gmail', 'outlook']:
            return jsonify({
                'success': False,
                'error': f'Unsupported email provider: {provider}. Supported: gmail, outlook'
            }), 400
        
        if provider == 'gmail':
            # Fetch COMPLETE message with format='full' to get full body content (not truncated)
            # format='full' returns full message including body data (vs 'metadata' or 'minimal')
            msg = gmail_get_message(
                message_id=message_id,
                format='full',  # CRITICAL: 'full' gets complete body, 'metadata' only headers, 'minimal' is truncated
                _user_id=user_id,
                _injected_credentials=True
            )
            
            # Parse headers
            headers = {h['name'].lower(): h['value'] for h in msg.get('payload', {}).get('headers', [])}
            
            # Parse body content
            import base64
            body_text = ''
            body_html = ''
            attachments_list = []
            
            def parse_parts(parts):
                """Recursively parse MIME parts for body and attachments"""
                text = ''
                html = ''
                atts = []
                for part in parts:
                    mime_type = part.get('mimeType', '')
                    filename = part.get('filename', '')
                    
                    # Check if this is an attachment
                    if filename and part.get('body', {}).get('attachmentId'):
                        # 🎯 FILTER: Skip inline attachments (email footers/signature images)
                        headers = part.get('headers', [])
                        is_inline = False
                        has_content_id = False
                        
                        for header in headers:
                            header_name = header.get('name', '').lower()
                            if header_name == 'content-disposition' and 'inline' in header.get('value', '').lower():
                                is_inline = True
                            elif header_name == 'content-id':
                                has_content_id = True
                        
                        # Skip inline attachments (footer images, signatures)
                        if is_inline or has_content_id:
                            continue
                        
                        atts.append({
                            'id': part.get('body', {}).get('attachmentId'),
                            'name': filename,
                            'mimeType': mime_type,
                            'size': part.get('body', {}).get('size', 0)
                        })
                    elif mime_type == 'text/plain':
                        data = part.get('body', {}).get('data', '')
                        if data:
                            text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    elif mime_type == 'text/html':
                        data = part.get('body', {}).get('data', '')
                        if data:
                            html = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    elif 'parts' in part:
                        # Multipart message - recurse
                        sub_text, sub_html, sub_atts = parse_parts(part['parts'])
                        text = text or sub_text
                        html = html or sub_html
                        atts.extend(sub_atts)
                return text, html, atts
            
            # Check if single part or multipart
            payload = msg.get('payload', {})
            if 'parts' in payload:
                body_text, body_html, attachments_list = parse_parts(payload['parts'])
            else:
                # Single part message
                mime_type = payload.get('mimeType', '')
                data = payload.get('body', {}).get('data', '')
                if data:
                    decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    if mime_type == 'text/html':
                        body_html = decoded
                    else:
                        body_text = decoded
            
            print(f"\n🔍 [GMAIL DEBUG] Message ID: {message_id}")
            print(f"🔍 [GMAIL DEBUG] Body text length: {len(body_text)}")
            print(f"🔍 [GMAIL DEBUG] Body HTML length: {len(body_html)}")
            print(f"🔍 [GMAIL DEBUG] Attachments count: {len(attachments_list)}")
            if attachments_list:
                print(f"🔍 [GMAIL DEBUG] Attachment details:")
                for att in attachments_list:
                    print(f"  - {att['name']} ({att.get('size', 0)} bytes, {att.get('mimeType', 'unknown')})")
            
            return jsonify({
                'success': True,
                'email': {
                    'id': email_id,
                    'provider': 'gmail',
                    'from': headers.get('from', 'Unknown'),
                    'to': headers.get('to', ''),
                    'subject': headers.get('subject', 'No Subject'),
                    'date': headers.get('date', ''),
                    'body_text': body_text,
                    'body_html': body_html,
                    'snippet': msg.get('snippet', ''),
                    'attachments': attachments_list,  # ✅ Parsed attachment metadata
                    'has_attachments': len(attachments_list) > 0
                }
            })
        
        elif provider == 'outlook':
            # Check if Outlook tools are available
            if not OUTLOOK_AVAILABLE:
                return jsonify({
                    'success': False,
                    'error': 'Outlook email viewing is currently unavailable. Microsoft Outlook tools failed to load. Please check server logs or contact your administrator.',
                    'provider': provider,
                    'outlook_available': OUTLOOK_AVAILABLE
                }), 503
            
            # 🔍 DEBUG: Log Outlook email fetch attempt
            print(f"\n🔍 [COMMUNICATION ROUTES] Fetching Outlook email:")
            print(f"   - Email ID: {email_id}")
            print(f"   - Message ID: {message_id}")
            print(f"   - User ID: {user_id}")
            
            # Request message WITH attachments expanded to get full attachment metadata
            result = microsoft_outlook_get_message(
                message_id=message_id,
                include_attachments=True,  # ✅ CRITICAL: Expand attachments to get full data
                _user_id=user_id,
                _injected_credentials=True
            )
            if result.get('success'):
                email_data = result.get('message', {})
                from_addr = email_data.get('from', {})
                from_email = from_addr.get('emailAddress', {}).get('address', 'Unknown') if isinstance(from_addr, dict) else str(from_addr)
                
                # Outlook body content - use uniqueBody (full content) if available, fallback to body
                unique_body = email_data.get('uniqueBody', {})
                body = email_data.get('body', {})
                
                # Prefer uniqueBody (contains full message without quoted replies/truncation)
                if unique_body and unique_body.get('content'):
                    content = unique_body.get('content', '')
                    content_type = unique_body.get('contentType', 'text')
                else:
                    content = body.get('content', '')
                    content_type = body.get('contentType', 'text')
                
                # 🔍 DEBUG: Log what we're about to send to frontend
                print(f"\n🔍 [COMMUNICATION ROUTES DEBUG] Email ID: {email_id}")
                print(f"🔍 [COMMUNICATION ROUTES DEBUG] Using uniqueBody: {bool(unique_body and unique_body.get('content'))}")
                print(f"🔍 [COMMUNICATION ROUTES DEBUG] Content length: {len(content)}")
                print(f"🔍 [COMMUNICATION ROUTES DEBUG] Content type: {content_type}")
                print(f"🔍 [COMMUNICATION ROUTES DEBUG] bodyPreview length: {len(email_data.get('bodyPreview', ''))}")
                print(f"🔍 [COMMUNICATION ROUTES DEBUG] Body length: {len(body.get('content', ''))}")
                print(f"🔍 [COMMUNICATION ROUTES DEBUG] UniqueBody length: {len(unique_body.get('content', ''))}")
                print(f"🔍 [COMMUNICATION ROUTES DEBUG] Attachments count: {len(email_data.get('attachments', []))}")
                print(f"🔍 [COMMUNICATION ROUTES DEBUG] Content first 200: {content[:200]}")
                print(f"🔍 [COMMUNICATION ROUTES DEBUG] Content last 200: {content[-200:]}")
                
                # Parse attachments metadata
                attachments = email_data.get('attachments', [])
                attachment_list = []
                inline_filtered = 0
                
                for att in attachments:
                    # 🎯 FILTER: Skip inline attachments (email footers/signature images)
                    is_inline = att.get('isInline', False)
                    has_content_id = att.get('contentId') is not None
                    
                    if is_inline or has_content_id:
                        inline_filtered += 1
                        continue  # Skip email footer/signature images
                    
                    attachment_list.append({
                        'id': att.get('id'),
                        'name': att.get('name'),
                        'contentType': att.get('contentType'),
                        'size': att.get('size'),
                        'isInline': False  # Guaranteed false at this point
                    })
                
                if inline_filtered > 0:
                    print(f"🎯 [INLINE FILTER] Excluded {inline_filtered} inline attachment(s) from preview")
                
                if attachment_list:
                    print(f"🔍 [COMMUNICATION ROUTES DEBUG] Attachment details:")
                    for att in attachment_list:
                        print(f"  - {att['name']} ({att.get('size', 0)} bytes, {att.get('contentType', 'unknown')})")
                
                return jsonify({
                    'success': True,
                    'email': {
                        'id': email_id,
                        'provider': 'outlook',
                        'from': from_email,
                        'to': email_data.get('toRecipients', [{}])[0].get('emailAddress', {}).get('address', '') if email_data.get('toRecipients') else '',
                        'subject': email_data.get('subject', 'No Subject'),
                        'date': email_data.get('receivedDateTime', ''),
                        'body_text': content if content_type == 'text' else '',
                        'body_html': content if content_type == 'html' else '',
                        'snippet': email_data.get('bodyPreview', ''),
                        'attachments': attachment_list,  # ✅ Parsed attachment metadata
                        'has_attachments': len(attachment_list) > 0
                    }
                })
            else:
                # Outlook API call failed
                error_msg = result.get('error', 'Unknown error')
                print(f"❌ [COMMUNICATION ROUTES] Outlook API failed: {error_msg}")
                print(f"❌ [COMMUNICATION ROUTES] Full result: {result}")
                return jsonify({
                    'success': False,
                    'error': f'Failed to fetch Outlook email: {error_msg}',
                    'provider': provider,
                    'email_id': email_id
                }), 500
        
        # If we reach here, provider matched but email fetch failed
        return jsonify({
            'success': False,
            'error': f'Email not found or access denied for provider "{provider}". The email may have been deleted or you may not have permission to view it.',
            'provider': provider
        }), 404
    
    except Exception as e:
        print(f"\n❌❌❌ [COMMUNICATION ROUTES] EXCEPTION in get_email() ❌❌❌")
        print(f"❌ Email ID: {email_id}")
        print(f"❌ Provider: {provider if 'provider' in locals() else 'UNKNOWN'}")
        print(f"❌ Message ID: {message_id if 'message_id' in locals() else 'UNKNOWN'}")
        print(f"❌ User ID: {user_id}")
        print(f"❌ Exception type: {type(e).__name__}")
        print(f"❌ Exception message: {str(e)}")
        print(f"❌ Full traceback:")
        import traceback
        traceback.print_exc()
        print(f"❌❌❌ END EXCEPTION ❌❌❌\n")
        return jsonify({
            'success': False,
            'error': f'{type(e).__name__}: {str(e)}' if str(e) else f'{type(e).__name__} (no message)'
        }), 500


# DISABLED FOR SECURITY: Email sending endpoint commented out (Dec 3, 2025)
# Microsoft Outlook email sending must be done manually from Outlook application
# Drafts can still be created via microsoft_outlook_create_draft tool

# @communication_bp.route('/send', methods=['POST'])
# @require_auth
# def send_email():
#     """
#     DISABLED: Send email via selected account
#     
#     This endpoint is disabled for security reasons. Microsoft Outlook emails
#     cannot be sent programmatically - only drafts can be created.
#     
#     Request body:
#         - from: Account ID ('gmail' or 'outlook')
#         - to: Recipient email address
#         - cc: CC recipients (optional)
#         - subject: Email subject
#         - body: Email body
#         - user_id: User ID (optional, default: 1)
#     
#     Returns:
#         JSON with success status
#     """
#     data = request.json
#     # Prefer authenticated user; allow override for compatibility
#     user_data = getattr(request, 'user', None)
#     if user_data:
#         user_id = user_data.get('user_id')
#     else:
#         user_id = data.get('user_id', 1)
#     account = data.get('from')
#     to = data.get('to')
#     cc = data.get('cc', '')
#     subject = data.get('subject')
#     body = data.get('body')
#     
#     if not all([account, to, subject, body]):
#         return jsonify({
#             'success': False,
#             'error': 'Missing required fields: from, to, subject, body'
#         }), 400
#     
#     try:
#         if account == 'gmail':
#             result = gmail_send_email(
#                 to=to,
#                 subject=subject,
#                 body=body,
#                 cc=cc if cc else None,
#                 _user_id=user_id,
#                 _injected_credentials=True
#             )
#             
#             return jsonify(result)
#         
#         elif account == 'outlook' and OUTLOOK_AVAILABLE:
#             # Convert 'to' to list if string
#             to_list = [to] if isinstance(to, str) else to
#             cc_list = [cc] if cc and isinstance(cc, str) else (cc if cc else None)
#             
#             result = microsoft_outlook_send_email(
#                 to=to_list,
#                 subject=subject,
#                 body=body,
#                 cc=cc_list,
#                 _user_id=user_id,
#                 _injected_credentials=True
#             )
#             
#             return jsonify(result)
#         
#         return jsonify({
#             'success': False,
#             'error': f'Invalid account: {account}'
#         }), 400
#     
#     except Exception as e:
#         print(f"[Communication Hub] Error sending email: {e}")
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500


@communication_bp.route('/emails/<email_id>/markdown', methods=['GET'])
@require_auth
def get_email_as_markdown(email_id):
    """
    Get email formatted as compact markdown for AI consumption
    
    Returns:
        {
            'markdown': 'formatted email content',
            'metadata': {...}
        }
    
    ✅ NO DATABASE OPERATIONS - Safe (uses gmail/outlook wrappers)
    """
    user_data = getattr(request, 'user', None)
    if user_data:
        user_id = user_data.get('user_id')
    else:
        user_id = request.args.get('user_id', 1, type=int)
    
    try:
        # Get full email content
        provider, message_id = email_id.split('_', 1)
        
        if provider == 'gmail':
            email_data = gmail_get_message(
                message_id=message_id,
                _user_id=user_id,
                _injected_credentials=True
            )
        elif provider == 'outlook':
            email_data = outlook_get_message(
                message_id=message_id,
                _user_id=user_id,
                _injected_credentials=True
            )
        else:
            return jsonify({'error': 'Unsupported provider'}), 400
        
        # Format as markdown
        markdown = format_email_as_markdown(email_data)
        
        return jsonify({
            'success': True,
            'markdown': markdown,
            'metadata': {
                'email_id': email_id,
                'subject': email_data.get('subject'),
                'from': email_data.get('from'),
                'date': email_data.get('date'),
                'provider': provider
            }
        })
        
    except Exception as e:
        print(f"[Communication Hub] Error formatting email as markdown: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def format_email_as_markdown(email_data):
    """
    Format email data as compact markdown for AI consumption
    
    Args:
        email_data: Dictionary with email fields
    
    Returns:
        Markdown-formatted string
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    import re
    
    markdown = "# Email Details\n\n"
    
    markdown += f"**From:** {email_data.get('from', 'N/A')}\n"
    markdown += f"**To:** {email_data.get('to', 'N/A')}\n"
    
    if email_data.get('cc'):
        markdown += f"**CC:** {email_data.get('cc')}\n"
    
    markdown += f"**Subject:** {email_data.get('subject', 'No Subject')}\n"
    markdown += f"**Date:** {email_data.get('date', 'N/A')}\n"
    markdown += f"**Account:** {email_data.get('provider', 'N/A')}\n"
    
    # Attachments (listed but not included)
    attachments = email_data.get('attachments', [])
    if attachments and len(attachments) > 0:
        markdown += f"\n**Attachments:** ({len(attachments)} files)\n"
        for att in attachments:
            filename = att.get('filename', att.get('name', 'Unnamed'))
            mime_type = att.get('mimeType', att.get('contentType', 'unknown'))
            markdown += f"  - {filename} ({mime_type})\n"
        markdown += "\n*Note: Attachment contents not included in context.*\n"
    
    markdown += "\n---\n\n"
    
    # Email body
    body_text = email_data.get('body_text', '')
    body_html = email_data.get('body_html', '')
    
    if body_text:
        markdown += "## Email Content\n\n"
        markdown += body_text + "\n"
    elif body_html:
        # Strip HTML tags
        text_content = re.sub(r'<style[^>]*>.*?</style>', '', body_html, flags=re.DOTALL)
        text_content = re.sub(r'<script[^>]*>.*?</script>', '', text_content, flags=re.DOTALL)
        text_content = re.sub(r'<[^>]+>', ' ', text_content)
        text_content = text_content.replace('&nbsp;', ' ')
        text_content = text_content.replace('&amp;', '&')
        text_content = text_content.replace('&lt;', '<')
        text_content = text_content.replace('&gt;', '>')
        text_content = text_content.replace('&quot;', '"')
        text_content = text_content.replace('&#39;', "'")
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        markdown += "## Email Content\n\n"
        markdown += text_content + "\n"
    else:
        markdown += "## Email Content\n\n*No content available*\n"
    
    return markdown


@communication_bp.route('/emails/<email_id>/read', methods=['POST'])
@require_auth
def mark_email_as_read(email_id):
    """
    Mark email as read
    
    ✅ NO DATABASE OPERATIONS - Safe (uses gmail/outlook wrappers)
    """
    user_data = getattr(request, 'user', None)
    if user_data:
        user_id = user_data.get('user_id')
    else:
        user_id = request.args.get('user_id', 1, type=int)
    
    try:
        provider, message_id = email_id.split('_', 1)
        
        if provider == 'gmail':
            result = gmail_mark_as_read(
                message_id=message_id,
                _user_id=user_id,
                _injected_credentials=True
            )
            return jsonify(result)
        
        elif provider == 'outlook':
            if not OUTLOOK_AVAILABLE:
                return jsonify({
                    'success': False,
                    'error': 'Outlook tools not available'
                }), 503
            # TODO: Implement Outlook mark as read
            return jsonify({
                'success': True,
                'message': 'Outlook mark as read not yet implemented'
            })
        
        return jsonify({
            'success': False,
            'error': 'Provider not supported'
        }), 400
    
    except Exception as e:
        print(f"[Communication Hub] Error marking as read: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@communication_bp.route('/emails/<email_id>/unread', methods=['POST'])
@require_auth
def mark_email_as_unread(email_id):
    """
    Mark email as unread
    
    ✅ NO DATABASE OPERATIONS - Safe (uses gmail/outlook wrappers)
    """
    user_data = getattr(request, 'user', None)
    if user_data:
        user_id = user_data.get('user_id')
    else:
        user_id = request.args.get('user_id', 1, type=int)
    
    try:
        provider, message_id = email_id.split('_', 1)
        
        if provider == 'gmail':
            # TODO: Implement gmail_mark_as_unread
            return jsonify({
                'success': True,
                'message': 'Gmail mark as unread not yet implemented'
            })
        
        elif provider == 'outlook':
            if not OUTLOOK_AVAILABLE:
                return jsonify({
                    'success': False,
                    'error': 'Outlook tools not available'
                }), 503
            # TODO: Implement Outlook mark as unread
            return jsonify({
                'success': True,
                'message': 'Outlook mark as unread not yet implemented'
            })
        
        return jsonify({
            'success': False,
            'error': 'Provider not supported'
        }), 400
    
    except Exception as e:
        print(f"[Communication Hub] Error marking as unread: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@communication_bp.route('/search', methods=['GET'])
@require_auth
def search_emails():
    """
    Search emails across all accounts
    
    Query params:
        - q: Search query
        - user_id: User ID (default: 1)
        - limit: Max results (default: 50)
    
    Returns:
        JSON with matching emails
    
    ✅ NO DATABASE OPERATIONS - Safe (uses gmail/outlook wrappers)
    """
    user_data = getattr(request, 'user', None)
    if user_data:
        user_id = user_data.get('user_id')
    else:
        user_id = request.args.get('user_id', 1, type=int)
    query = request.args.get('q', '')
    limit = request.args.get('limit', 50, type=int)
    
    if not query:
        return jsonify({
            'success': False,
            'error': 'Search query required'
        }), 400
    
    emails = []
    
    # Gmail search
    try:
        gmail_result = gmail_search_messages(
            query=query,
            max_results=limit,
            _user_id=user_id,
            _injected_credentials=True
        )
        
        if gmail_result.get('success'):
            for msg in gmail_result.get('messages', []):
                emails.append({
                    'id': f"gmail_{msg['id']}",
                    'provider': 'gmail',
                    'from': msg.get('from', 'Unknown'),
                    'subject': msg.get('subject', 'No Subject'),
                    'date': msg.get('date', ''),
                    'snippet': msg.get('snippet', '')
                })
    except Exception as e:
        print(f"[Communication Hub] Gmail search error: {e}")
    
    # TODO: Implement Outlook search
    
    return jsonify({
        'success': True,
        'emails': emails,
        'count': len(emails)
    })


@communication_bp.route('/emails/<email_id>', methods=['DELETE'])
@require_auth
def delete_email(email_id):
    """
    Delete email
    
    ✅ NO DATABASE OPERATIONS - Safe (uses gmail/outlook wrappers)
    """
    user_data = getattr(request, 'user', None)
    if user_data:
        user_id = user_data.get('user_id')
    else:
        user_id = request.args.get('user_id', 1, type=int)
    
    try:
        provider, message_id = email_id.split('_', 1)
        
        if provider == 'gmail':
            result = gmail_delete_message(
                message_id=message_id,
                _user_id=user_id,
                _injected_credentials=True
            )
            return jsonify(result)
        
        elif provider == 'outlook':
            if not OUTLOOK_AVAILABLE:
                return jsonify({
                    'success': False,
                    'error': 'Outlook tools not available'
                }), 503
            # TODO: Implement Outlook delete
            return jsonify({
                'success': True,
                'message': 'Outlook delete not yet implemented'
            })
        
        return jsonify({
            'success': False,
            'error': 'Provider not supported'
        }), 400
    
    except Exception as e:
        print(f"[Communication Hub] Error deleting email: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Health check endpoint
@communication_bp.route('/threads/<thread_slug>/emails', methods=['GET'])
def get_thread_emails(thread_slug):
    """
    Get all emails associated with a thread
    
    Query Params:
    - user_id: User ID (required)
    
    Returns:
    - List of email objects in the thread
    
    FIXED: Added proper cursor management with try/finally block
    """
    cursor = None  # ✅ CRITICAL: Initialize before try
    conn = None
    
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'user_id is required'}), 400
        
        print(f"[Communication Hub] Fetching emails for thread: {thread_slug}, user: {user_id}")
        
        # Query threads table for email data (email stored in columns: email_thread_id, email_subject, email_participants)
        from shared.database_utils import get_database_connection
        
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                
                # Get email data from thread columns
                cursor.execute("""
                    SELECT email_thread_id, email_subject, email_participants, created_at
                    FROM sessions.threads
                    WHERE thread_slug = %s AND user_id = %s AND email_thread_id IS NOT NULL
                """, (thread_slug, user_id))
                
                thread_row = cursor.fetchone()
        
        if not thread_row:
            return jsonify({
                'success': True,
                'emails': [],
                'count': 0,
                'message': 'No emails found in thread'
            })
        
        # Fetch full email content (AFTER database closed)
        email_id, subject, participants, created_at = thread_row
        
        try:
            # Fetch full email (reuse existing logic)
            # Extract provider from email_id format (gmail_xxx or outlook_xxx)
            if email_id.startswith('gmail_'):
                provider = 'gmail'
                actual_id = email_id.replace('gmail_', '')
                
                # Get Google credentials
                google_creds = auth_manager.get_user_google_oauth_credentials(user_id)
                if google_creds:
                    # Fetch email from Gmail
                    email_result = gmail_get_message(
                        message_id=actual_id,
                        _user_id=user_id,
                        _injected_credentials=True,
                        access_token=google_creds.get('access_token'),
                        refresh_token=google_creds.get('refresh_token'),
                        token_uri=google_creds.get('token_uri')
                    )
                    
                    if email_result.get('success'):
                        email_data = email_result.get('message', {})
                        email_data['id'] = email_id
                        email_data['provider'] = 'gmail'
                        
                        return jsonify({
                            'success': True,
                            'emails': [email_data],
                            'count': 1,
                            'thread_slug': thread_slug
                        })
            
            elif email_id.startswith('outlook_'):
                provider = 'outlook'
                actual_id = email_id.replace('outlook_', '')
                
                # Get Microsoft credentials
                microsoft_creds = auth_manager.get_user_microsoft_oauth_credentials(user_id)
                if microsoft_creds and OUTLOOK_AVAILABLE:
                    # Fetch email from Outlook
                    from Microsoft_365_Connection.microsoft_outlook_tools import microsoft_outlook_get_message
                    
                    email_result = microsoft_outlook_get_message(
                        message_id=actual_id,
                        _user_id=user_id,
                        _injected_credentials=True,
                        access_token=microsoft_creds.get('access_token')
                    )
                    
                    if email_result.get('success'):
                        email_data = email_result.get('message', {})
                        email_data['id'] = email_id
                        email_data['provider'] = 'outlook'
                        
                        return jsonify({
                            'success': True,
                            'emails': [email_data],
                            'count': 1,
                            'thread_slug': thread_slug
                        })
        
        except Exception as email_error:
            print(f"[Communication Hub] Error fetching email {email_id}: {email_error}")
        
        # Fallback: return basic email info from thread data
        return jsonify({
            'success': True,
            'emails': [{
                'id': email_id,
                'subject': subject,
                'participants': participants,
                'created_at': created_at.isoformat() if created_at else None
            }],
            'count': 1,
            'thread_slug': thread_slug
        })
    
    except Exception as e:
        print(f"[Communication Hub] Error fetching thread emails: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        # ✅ CRITICAL: GUARANTEED cleanup
        try:
            if 'cursor' in locals() and cursor:
                cursor.close()
        except Exception as e:
            print(f"⚠️ Error closing cursor: {e}")
        try:
            if 'conn' in locals() and conn:
                conn.close()
        except Exception as e:
            print(f"⚠️ Error closing connection: {e}")


@communication_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    return jsonify({
        'success': True,
        'service': 'Communication Hub',
        'status': 'operational',
        'outlook_available': OUTLOOK_AVAILABLE
    })


# Debug route: show credential presence for authenticated user
@communication_bp.route('/debug/credentials', methods=['GET'])
@require_auth
def debug_credentials():
    """
    Return whether Google and Microsoft credentials are present for the logged-in user
    
    ✅ NO DATABASE OPERATIONS - Safe (uses auth_manager)
    """
    user_data = getattr(request, 'user', None)
    if not user_data:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401

    user_id = user_data.get('user_id')

    google_creds = None
    microsoft_creds = None

    try:
        google_creds = auth_manager.get_user_google_oauth_credentials(user_id)
    except Exception as e:
        print(f"[Communication Hub] Debug: get_user_google_oauth_credentials error: {e}")

    try:
        microsoft_creds = auth_manager.get_user_microsoft_oauth_credentials(user_id)
    except Exception as e:
        print(f"[Communication Hub] Debug: get_user_microsoft_oauth_credentials error: {e}")

    return jsonify({
        'success': True,
        'user_id': user_id,
        'google_present': bool(google_creds),
        'microsoft_present': bool(microsoft_creds)
    })


@communication_bp.route('/email-thread-mappings', methods=['GET'])
@require_auth
def get_email_thread_mappings():
    """
    Load all email-to-thread mappings for authenticated user.
    
    Used on page refresh to restore emailThreads state.
    Queries sessions.threads table (email_thread_id column already exists).
    
    ✅ SAFE: Read-only query with proper connection management
    
    Returns:
        {
            "success": true,
            "mappings": {
                "gmail_123": "thread-abc-def",
                "outlook_456": "thread-xyz-789"
            },
            "count": 2
        }
    """
    user_data = getattr(request, 'user', None)
    if not user_data:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    user_id = user_data.get('user_id')
    
    try:
        from shared.database_utils import execute_query
        
        # Query sessions.threads table for email-to-thread mappings
        # The table already has email_thread_id, email_subject, email_participants columns
        # ✅ FIX (Jan 4, 2026): ONLY return threads that have agents assigned
        rows = execute_query("""
            SELECT email_thread_id, thread_slug, location
            FROM sessions.threads
            WHERE user_id = %s 
              AND email_thread_id IS NOT NULL
              AND location IS NOT NULL
              AND location != 'unassigned'
              AND location != ''
            ORDER BY updated_at DESC
        """, (user_id,), fetch_mode='all')
        
        # Build mapping dictionary (rows are dicts from RealDictCursor)
        mappings = {}
        for row in rows:
            email_id = row['email_thread_id']
            thread_slug = row['thread_slug']
            if email_id and thread_slug:
                mappings[email_id] = thread_slug
        
        logger.info(f"[Communication Hub] Loaded {len(mappings)} email-thread mappings from sessions.threads for user {user_id}")
        
        return jsonify({
            'success': True,
            'mappings': mappings,
            'count': len(mappings)
        })
        
    except Exception as e:
        logger.error(f"[Communication Hub] Failed to load email-thread mappings: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    # ✅ NO finally block needed - execute_query() handles connection cleanup via context managers


# ==================== ATTACHMENT ENDPOINTS ====================

@communication_bp.route('/gmail/attachment', methods=['GET'])
@require_auth
def download_gmail_attachment():
    """
    Download Gmail attachment
    
    Query Params:
        message_id: Gmail message ID
        attachment_id: Attachment ID from Gmail API
        user_id: User ID (optional, uses authenticated user)
    
    Returns:
        Binary attachment data with appropriate content-type
    
    ✅ NO DATABASE OPERATIONS - Safe (uses gmail_get_attachment wrapper)
    """
    user_data = getattr(request, 'user', None)
    if user_data:
        user_id = user_data.get('user_id')
    else:
        user_id = request.args.get('user_id', 1, type=int)
    
    message_id = request.args.get('message_id')
    attachment_id = request.args.get('attachment_id')
    
    if not message_id or not attachment_id:
        return jsonify({
            'success': False,
            'error': 'Missing message_id or attachment_id'
        }), 400
    
    # Strip provider prefix from message_id (gmail_XXX → XXX)
    if message_id.startswith('gmail_'):
        message_id = message_id.replace('gmail_', '', 1)
    
    try:
        # Get attachment from Gmail API
        result = gmail_get_attachment(
            message_id=message_id,
            attachment_id=attachment_id,
            _user_id=user_id,
            _injected_credentials=True
        )
        
        # Get filename from message metadata
        message = gmail_get_message(
            message_id=message_id,
            format='metadata',
            _user_id=user_id,
            _injected_credentials=True
        )
        
        filename = 'attachment'
        content_type = 'application/octet-stream'
        
        if message and 'payload' in message:
            parts = message['payload'].get('parts', [])
            for part in parts:
                if part.get('body', {}).get('attachmentId') == attachment_id:
                    filename = part.get('filename', 'attachment')
                    content_type = part.get('mimeType', 'application/octet-stream')
                    break
        
        # Return binary data
        from flask import Response
        return Response(
            result['data'],
            mimetype=content_type,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': str(result['size'])
            }
        )
        
    except Exception as e:
        logger.error(f"[Communication Hub] Failed to download Gmail attachment: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@communication_bp.route('/outlook/attachment', methods=['GET'])
@require_auth
def download_outlook_attachment():
    """
    Download Outlook attachment
    
    Query Params:
        message_id: Outlook message ID
        attachment_id: Attachment ID from Outlook API
        user_id: User ID (optional, uses authenticated user)
    
    Returns:
        Binary attachment data with appropriate content-type
    
    ✅ NO DATABASE OPERATIONS - Safe (uses Microsoft365Client)
    """
    if not OUTLOOK_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Outlook integration not available'
        }), 503
    
    user_data = getattr(request, 'user', None)
    if user_data:
        user_id = user_data.get('user_id')
    else:
        user_id = request.args.get('user_id', 1, type=int)
    
    message_id = request.args.get('message_id')
    attachment_id = request.args.get('attachment_id')
    
    if not message_id or not attachment_id:
        return jsonify({
            'success': False,
            'error': 'Missing message_id or attachment_id'
        }), 400
    
    # Strip provider prefix from message_id (outlook_XXX → XXX)
    if message_id.startswith('outlook_'):
        message_id = message_id.replace('outlook_', '', 1)
    
    try:
        from tools.implementations.microsoft_outlook_tools import MicrosoftOutlookTools
        
        outlook = MicrosoftOutlookTools()
        result = outlook.outlook_download_attachment(
            message_id=message_id,
            attachment_id=attachment_id,
            save_to_disk=False,  # Return base64 for browser download
            _user_id=user_id,
            _injected_credentials=True
        )
        
        if not result.get('success'):
            return jsonify(result), 500
        
        # Decode base64 content
        import base64
        content = base64.b64decode(result['content'])
        
        # Return binary data
        from flask import Response
        return Response(
            content,
            mimetype=result.get('content_type', 'application/octet-stream'),
            headers={
                'Content-Disposition': f'attachment; filename="{result.get("name", "attachment")}"',
                'Content-Length': str(result.get('size', len(content)))
            }
        )
        
    except Exception as e:
        logger.error(f"[Communication Hub] Failed to download Outlook attachment: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@communication_bp.route('/extract-document-text', methods=['POST'])
@require_auth
def extract_document_text():
    """
    Extract text from Word/PowerPoint documents
    
    Request Body:
        {
            "email_id": "gmail_123" or "outlook_456",
            "attachment_id": "attachment_id_string",
            "user_id": 1,
            "provider": "gmail" or "outlook"
        }
    
    Returns:
        {
            "success": true,
            "text": "Extracted text content...",
            "filename": "document.docx",
            "size": 50000
        }
    
    Supports: .docx, .pptx (requires python-docx, python-pptx)
    Text limit: 50KB to prevent token overflow
    
    ✅ NO DATABASE OPERATIONS - Safe (downloads attachment and extracts text)
    """
    user_data = getattr(request, 'user', None)
    if user_data:
        user_id = user_data.get('user_id')
    else:
        data = request.json
        user_id = data.get('user_id', 1)
    
    data = request.json
    email_id = data.get('email_id')
    attachment_id = data.get('attachment_id')
    provider = data.get('provider', 'gmail')
    
    if not email_id or not attachment_id:
        return jsonify({
            'success': False,
            'error': 'Missing email_id or attachment_id'
        }), 400
    
    try:
        import tempfile
        import os
        
        # Download attachment first
        if provider == 'gmail':
            message_id = email_id.replace('gmail_', '')
            att_result = gmail_get_attachment(
                message_id=message_id,
                attachment_id=attachment_id,
                _user_id=user_id,
                _injected_credentials=True
            )
            attachment_data = att_result['data']
            
            # Get filename
            message = gmail_get_message(
                message_id=message_id,
                format='metadata',
                _user_id=user_id,
                _injected_credentials=True
            )
            filename = 'document'
            if message and 'payload' in message:
                parts = message['payload'].get('parts', [])
                for part in parts:
                    if part.get('body', {}).get('attachmentId') == attachment_id:
                        filename = part.get('filename', 'document')
                        break
        else:
            # Outlook
            from tools.implementations.microsoft_outlook_tools import MicrosoftOutlookTools
            outlook = MicrosoftOutlookTools()
            result = outlook.outlook_download_attachment(
                message_id=email_id.replace('outlook_', ''),
                attachment_id=attachment_id,
                save_to_disk=False,  # Need base64 for text extraction
                _user_id=user_id,
                _injected_credentials=True
            )
            import base64
            attachment_data = base64.b64decode(result['content'])
            filename = result.get('name', 'document')
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            tmp.write(attachment_data)
            tmp_path = tmp.name
        
        try:
            # Extract text based on file type
            filename_lower = filename.lower()
            text = ''
            
            if filename_lower.endswith('.docx'):
                import docx
                doc = docx.Document(tmp_path)
                text = '\n'.join([para.text for para in doc.paragraphs])
            
            elif filename_lower.endswith('.pptx'):
                from pptx import Presentation
                prs = Presentation(tmp_path)
                slides_text = []
                for i, slide in enumerate(prs.slides, 1):
                    slide_text = f"Slide {i}:\n"
                    for shape in slide.shapes:
                        if hasattr(shape, 'text'):
                            slide_text += shape.text + '\n'
                    slides_text.append(slide_text)
                text = '\n'.join(slides_text)
            
            else:
                return jsonify({
                    'success': False,
                    'error': f'Unsupported file type: {filename}'
                }), 400
            
            # Limit to 50KB
            max_chars = 50 * 1024
            if len(text) > max_chars:
                text = text[:max_chars] + '\n\n[Text truncated - exceeded 50KB limit]'
            
            return jsonify({
                'success': True,
                'text': text,
                'filename': filename,
                'size': len(text)
            })
        
        finally:
            # Clean up temp file
            try:
                os.remove(tmp_path)
            except:
                pass
    
    except ImportError as e:
        logger.error(f"[Communication Hub] Missing library for document extraction: {e}")
        return jsonify({
            'success': False,
            'error': 'Document extraction libraries not installed (python-docx, python-pptx required)'
        }), 500
    
    except Exception as e:
        logger.error(f"[Communication Hub] Failed to extract document text: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@communication_bp.route('/extract-spreadsheet-text', methods=['POST'])
@require_auth
def extract_spreadsheet_text():
    """
    Extract data from Excel spreadsheets
    
    Request Body:
        {
            "email_id": "gmail_123" or "outlook_456",
            "attachment_id": "attachment_id_string",
            "user_id": 1,
            "provider": "gmail" or "outlook"
        }
    
    Returns:
        {
            "success": true,
            "text": "CSV-formatted data...",
            "filename": "spreadsheet.xlsx",
            "sheets": ["Sheet1", "Sheet2"],
            "rows": 100
        }
    
    Supports: .xlsx, .xls (requires openpyxl, xlrd)
    Row limit: 100 rows to prevent token overflow
    
    ✅ NO DATABASE OPERATIONS - Safe (downloads attachment and extracts data)
    """
    user_data = getattr(request, 'user', None)
    if user_data:
        user_id = user_data.get('user_id')
    else:
        data = request.json
        user_id = data.get('user_id', 1)
    
    data = request.json
    email_id = data.get('email_id')
    attachment_id = data.get('attachment_id')
    provider = data.get('provider', 'gmail')
    
    if not email_id or not attachment_id:
        return jsonify({
            'success': False,
            'error': 'Missing email_id or attachment_id'
        }), 400
    
    try:
        import tempfile
        import os
        
        # Download attachment first
        if provider == 'gmail':
            message_id = email_id.replace('gmail_', '')
            att_result = gmail_get_attachment(
                message_id=message_id,
                attachment_id=attachment_id,
                _user_id=user_id,
                _injected_credentials=True
            )
            attachment_data = att_result['data']
            
            # Get filename
            message = gmail_get_message(
                message_id=message_id,
                format='metadata',
                _user_id=user_id,
                _injected_credentials=True
            )
            filename = 'spreadsheet'
            if message and 'payload' in message:
                parts = message['payload'].get('parts', [])
                for part in parts:
                    if part.get('body', {}).get('attachmentId') == attachment_id:
                        filename = part.get('filename', 'spreadsheet')
                        break
        else:
            # Outlook
            from tools.implementations.microsoft_outlook_tools import MicrosoftOutlookTools
            outlook = MicrosoftOutlookTools()
            result = outlook.outlook_download_attachment(
                message_id=email_id.replace('outlook_', ''),
                attachment_id=attachment_id,
                save_to_disk=False,  # Need base64 for spreadsheet extraction
                _user_id=user_id,
                _injected_credentials=True
            )
            import base64
            attachment_data = base64.b64decode(result['content'])
            filename = result.get('name', 'spreadsheet')
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            tmp.write(attachment_data)
            tmp_path = tmp.name
        
        try:
            # Extract data based on file type
            filename_lower = filename.lower()
            sheets_text = []
            sheet_names = []
            total_rows = 0
            
            if filename_lower.endswith('.xlsx'):
                import openpyxl
                wb = openpyxl.load_workbook(tmp_path, data_only=True)
                
                for sheet_name in wb.sheetnames:
                    ws = wb[sheet_name]
                    sheet_names.append(sheet_name)
                    
                    sheet_text = f"Sheet: {sheet_name}\n\n"
                    rows = []
                    
                    for row_num, row in enumerate(ws.iter_rows(values_only=True), 1):
                        if row_num > 100:  # Limit to 100 rows
                            break
                        # Convert row to strings, handle None
                        row_values = [str(cell) if cell is not None else '' for cell in row]
                        rows.append(','.join(row_values))
                        total_rows += 1
                    
                    sheet_text += '\n'.join(rows)
                    sheets_text.append(sheet_text)
            
            elif filename_lower.endswith('.xls'):
                import xlrd
                wb = xlrd.open_workbook(tmp_path)
                
                for sheet in wb.sheets():
                    sheet_names.append(sheet.name)
                    
                    sheet_text = f"Sheet: {sheet.name}\n\n"
                    rows = []
                    
                    for row_num in range(min(sheet.nrows, 100)):
                        row_values = [str(cell.value) for cell in sheet.row(row_num)]
                        rows.append(','.join(row_values))
                        total_rows += 1
                    
                    sheet_text += '\n'.join(rows)
                    sheets_text.append(sheet_text)
            
            else:
                return jsonify({
                    'success': False,
                    'error': f'Unsupported file type: {filename}'
                }), 400
            
            text = '\n\n'.join(sheets_text)
            
            return jsonify({
                'success': True,
                'text': text,
                'filename': filename,
                'sheets': sheet_names,
                'rows': total_rows
            })
        
        finally:
            # Clean up temp file
            try:
                os.remove(tmp_path)
            except:
                pass
    
    except ImportError as e:
        logger.error(f"[Communication Hub] Missing library for spreadsheet extraction: {e}")
        return jsonify({
            'success': False,
            'error': 'Spreadsheet extraction libraries not installed (openpyxl, xlrd required)'
        }), 500
    
    except Exception as e:
        logger.error(f"[Communication Hub] Failed to extract spreadsheet text: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# 🛡️ Global error handlers for Communication Hub Blueprint
@communication_bp.errorhandler(500)
def handle_internal_error(error):
    """Handle internal server errors with proper JSON response"""
    logger.error(f"[Communication Hub] Internal error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error - check server logs',
        'type': 'internal_error'
    }), 500


@communication_bp.errorhandler(Exception)
def handle_unexpected_error(error):
    """Catch-all handler for unexpected errors"""
    logger.error(f"[Communication Hub] Unexpected error: {error}")
    import traceback
    traceback.print_exc()
    return jsonify({
        'success': False,
        'error': str(error),
        'type': 'unexpected_error'
    }), 500


# Log module initialization
log_init(logger, "Communication Hub Routes loaded successfully")