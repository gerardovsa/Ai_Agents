"""
FILE: AI_infrastructure/routes/communication_routes.py
PURPOSE: Communication Hub backend routes - Unified API for Gmail and Outlook

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
    gmail_get_message, 
    gmail_send_email,
    gmail_mark_as_read,
    gmail_delete_message,
    gmail_search_messages
)

# Setup logging
from utils.logger_config import setup_logger, log_warning, log_init
logger = setup_logger('routes.communication_routes')

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
    
    # ✅ FIRST: Check which accounts user has connected
    has_google = False
    has_microsoft = False
    
    try:
        google_creds = auth_manager.get_user_google_oauth_credentials(user_id)
        has_google = google_creds is not None
        print(f"[Communication Hub] 🔍 User {user_id} has Google OAuth: {has_google}")
    except Exception as e:
        print(f"[Communication Hub] ⚠️  Error checking Google OAuth: {e}")
    
    try:
        microsoft_creds = auth_manager.get_user_microsoft_oauth_credentials(user_id)
        has_microsoft = microsoft_creds is not None
        print(f"[Communication Hub] 🔍 User {user_id} has Microsoft OAuth: {has_microsoft}")
    except Exception as e:
        print(f"[Communication Hub] ⚠️  Error checking Microsoft OAuth: {e}")
    
    emails = []
    
    # ✅ Gmail: ONLY try if user has Google OAuth credentials
    if account in ['all', 'gmail'] and has_google:
        try:
            print(f"[Communication Hub] 📧 Fetching Gmail messages for user {user_id}...")
            gmail_result = gmail_list_messages(
                max_results=limit,
                _user_id=user_id,
                _injected_credentials=True
            )
            
            if gmail_result.get('success'):
                gmail_count = len(gmail_result.get('messages', []))
                print(f"[Communication Hub] ✅ Got {gmail_count} Gmail message(s)")
                for msg in gmail_result.get('messages', []):
                    emails.append({
                        'id': f"gmail_{msg['id']}",
                        'provider': 'gmail',
                        'from': msg.get('from', 'Unknown'),
                        'to': msg.get('to', ''),
                        'subject': msg.get('subject', 'No Subject'),
                        'date': msg.get('date', ''),
                        'is_read': 'UNREAD' not in msg.get('labelIds', []),
                        'snippet': msg.get('snippet', ''),
                        'has_attachments': len(msg.get('attachments', [])) > 0
                    })
            else:
                print(f"[Communication Hub] ⚠️  Gmail returned no messages or error: {gmail_result.get('error', 'Unknown')}")
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
                        'has_attachments': msg.get('hasAttachments', False)
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
    Get full email content
    
    Args:
        email_id: Email ID in format 'provider_id' (e.g., 'gmail_12345')
    
    Returns:
        JSON with full email content
    """
    user_data = getattr(request, 'user', None)
    if user_data:
        user_id = user_data.get('user_id')
    else:
        user_id = request.args.get('user_id', 1, type=int)
    
    try:
        # Parse provider and message ID
        provider, message_id = email_id.split('_', 1)
        
        if provider == 'gmail':
            result = gmail_get_message(
                message_id=message_id,
                _user_id=user_id,
                _injected_credentials=True
            )
            
            if result.get('success'):
                email_data = result.get('message', {})
                return jsonify({
                    'success': True,
                    'email': {
                        'id': email_id,
                        'provider': 'gmail',
                        'from': email_data.get('from', 'Unknown'),
                        'to': email_data.get('to', ''),
                        'subject': email_data.get('subject', 'No Subject'),
                        'date': email_data.get('date', ''),
                        'body_text': email_data.get('body_text', ''),
                        'body_html': email_data.get('body_html', ''),
                        'snippet': email_data.get('snippet', ''),
                        'attachments': email_data.get('attachments', [])
                    }
                })
        
        elif provider == 'outlook' and OUTLOOK_AVAILABLE:
            result = microsoft_outlook_get_message(
                message_id=message_id,
                _user_id=user_id,
                _injected_credentials=True
            )
            
            if result.get('success'):
                email_data = result.get('message', {})
                from_addr = email_data.get('from', {})
                from_email = from_addr.get('emailAddress', {}).get('address', 'Unknown') if isinstance(from_addr, dict) else str(from_addr)
                
                return jsonify({
                    'success': True,
                    'email': {
                        'id': email_id,
                        'provider': 'outlook',
                        'from': from_email,
                        'to': email_data.get('toRecipients', [{}])[0].get('emailAddress', {}).get('address', '') if email_data.get('toRecipients') else '',
                        'subject': email_data.get('subject', 'No Subject'),
                        'date': email_data.get('receivedDateTime', ''),
                        'body_text': email_data.get('body', {}).get('content', ''),
                        'body_html': email_data.get('body', {}).get('content', ''),
                        'snippet': email_data.get('bodyPreview', ''),
                        'attachments': email_data.get('attachments', [])
                    }
                })
        
        return jsonify({
            'success': False,
            'error': 'Provider not supported or email not found'
        })
    
    except Exception as e:
        print(f"[Communication Hub] Error fetching email: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@communication_bp.route('/send', methods=['POST'])
@require_auth
def send_email():
    """
    Send email via selected account
    
    Request body:
        - from: Account ID ('gmail' or 'outlook')
        - to: Recipient email address
        - cc: CC recipients (optional)
        - subject: Email subject
        - body: Email body
        - user_id: User ID (optional, default: 1)
    
    Returns:
        JSON with success status
    """
    data = request.json
    # Prefer authenticated user; allow override for compatibility
    user_data = getattr(request, 'user', None)
    if user_data:
        user_id = user_data.get('user_id')
    else:
        user_id = data.get('user_id', 1)
    account = data.get('from')
    to = data.get('to')
    cc = data.get('cc', '')
    subject = data.get('subject')
    body = data.get('body')
    
    if not all([account, to, subject, body]):
        return jsonify({
            'success': False,
            'error': 'Missing required fields: from, to, subject, body'
        }), 400
    
    try:
        if account == 'gmail':
            result = gmail_send_email(
                to=to,
                subject=subject,
                body=body,
                cc=cc if cc else None,
                _user_id=user_id,
                _injected_credentials=True
            )
            
            return jsonify(result)
        
        elif account == 'outlook' and OUTLOOK_AVAILABLE:
            # Convert 'to' to list if string
            to_list = [to] if isinstance(to, str) else to
            cc_list = [cc] if cc and isinstance(cc, str) else (cc if cc else None)
            
            result = microsoft_outlook_send_email(
                to=to_list,
                subject=subject,
                body=body,
                cc=cc_list,
                _user_id=user_id,
                _injected_credentials=True
            )
            
            return jsonify(result)
        
        return jsonify({
            'success': False,
            'error': f'Invalid account: {account}'
        }), 400
    
    except Exception as e:
        print(f"[Communication Hub] Error sending email: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@communication_bp.route('/emails/<email_id>/read', methods=['POST'])
@require_auth
def mark_email_as_read(email_id):
    """Mark email as read"""
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
        
        elif provider == 'outlook' and OUTLOOK_AVAILABLE:
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
    """Mark email as unread"""
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
        
        elif provider == 'outlook' and OUTLOOK_AVAILABLE:
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
    """Delete email"""
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
        
        elif provider == 'outlook' and OUTLOOK_AVAILABLE:
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
@communication_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
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
    """Return whether Google and Microsoft credentials are present for the logged-in user"""
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


# Log module initialization
log_init(logger, "Communication Hub Routes loaded successfully")
