"""
Gmail API Tool Implementations
================================

Implements Gmail operations for sending, reading, managing emails and labels.

Authentication: Uses OAuth 2.0 for personal Gmail access
Mode: Supports 'desktop' (local testing) and 'web' (production deployment)
"""

import os
import sys
import base64
import mimetypes
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    
    # Suppress Google API discovery cache warning (harmless but verbose)
    import logging
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
    
    HAS_GMAIL_API = True
except ImportError:
    HAS_GMAIL_API = False
    print("⚠️ Gmail API dependencies not available")


def _get_gmail_service(user_email=None, _user_id=None, _injected_credentials=None, **kwargs):
    """
    Get authenticated Gmail API service using OAuth 2.0
    
    ✅ NEW: Supports credential injection from database
    
    Args:
        user_email: Optional user email for multi-user deployments
        _user_id: User ID for credential injection (from tool registry)
        _injected_credentials: Flag indicating credentials will be injected
        **kwargs: Additional parameters (captured and ignored)
    
    Returns:
        Authenticated Gmail service
    
    Note:
        - WITH _user_id: Uses user's OAuth tokens from database (web mode)
        - WITHOUT _user_id: Falls back to desktop OAuth (local testing)
    """
    if not HAS_GMAIL_API:
        raise Exception("Gmail API not available - install google-api-python-client")
    
    # ✅ NEW: If user_id provided, use database credentials
    if _user_id and _injected_credentials:
        print(f"🔑 Using database credentials for user {_user_id}")
        try:
            # Import credential retrieval function
            sys.path.insert(0, str(Path(__file__).parent.parent / 'AI_infrastructure'))
            from auth.user_auth import UserAuthManager
            
            # Get user's Google OAuth credentials
            auth_manager = UserAuthManager()
            cred_dict = auth_manager.get_user_google_oauth_credentials(_user_id)
            
            if not cred_dict:
                raise Exception(f"User {_user_id} does not have Google OAuth credentials. Please sign in with Google first.")
            
            # Build service from database credentials
            credentials = Credentials(
                token=cred_dict['access_token'],
                refresh_token=cred_dict.get('refresh_token'),
                token_uri=cred_dict['token_uri'],
                client_id=cred_dict['client_id'],
                client_secret=cred_dict['client_secret'],
                scopes=cred_dict['scopes']
            )
            
            service = build('gmail', 'v1', credentials=credentials)
            # Reduced logging verbosity - only log in debug mode
            # print(f"✅ Gmail service created with user {_user_id}'s credentials")
            return service
            
        except Exception as e:
            print(f"❌ Failed to use database credentials: {e}")
            raise
    
    # No credentials provided - throw clear error
    raise Exception(
        "❌ Gmail tool called directly without credentials!\n\n"
        "🤖 AI AGENT: You MUST call Gmail tools through the execute_tool meta-tool.\n"
        "❌ WRONG: gmail_delete_message(message_id='xxx')\n"
        "✅ CORRECT: execute_tool(tool_name='gmail_delete_message', message_id='xxx')\n\n"
        "WHY: Gmail requires OAuth credentials that are injected by execute_tool.\n"
        "Direct calls bypass credential injection and will always fail.\n\n"
        "For users: All credentials are stored in data/ai_infrastructure.db (oauth_tokens table)\n"
        "To authenticate, visit: http://localhost:5001/auth/google/login\n\n"
        f"Debug info: _user_id={_user_id}, _injected_credentials={_injected_credentials}\n"
    )


# ==================== EMAIL SENDING ====================

def gmail_send_email(to, subject, body, cc=None, bcc=None, attachments=None, **kwargs):
    """Send an email via Gmail
    
    ✅ Supports credential injection via **kwargs (_user_id, _injected_credentials)
    """
    try:
        service = _get_gmail_service(**kwargs)
        
        # Convert lists to comma-separated strings (AI agents may pass lists)
        if isinstance(to, list):
            to = ', '.join(to)
        if isinstance(cc, list):
            cc = ', '.join(cc)
        if isinstance(bcc, list):
            bcc = ', '.join(bcc)
        
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc
        
        # Add body
        message.attach(MIMEText(body, 'plain'))
        
        # Add attachments if provided
        if attachments:
            for file_path in attachments:
                with open(file_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
                    message.attach(part)
        
        # Send
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        result = service.users().messages().send(userId='me', body={'raw': raw}).execute()
        
        return {
            'message_id': result['id'],
            'thread_id': result['threadId']
        }
    
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        raise


def gmail_create_draft(to, subject, body, cc=None, bcc=None, **kwargs):
    """Create a draft email
    
    ✅ Supports credential injection via **kwargs
    """
    try:
        service = _get_gmail_service(**kwargs)
        
        # Convert lists to comma-separated strings (AI agents may pass lists)
        if isinstance(to, list):
            to = ', '.join(to)
        if isinstance(cc, list):
            cc = ', '.join(cc)
        if isinstance(bcc, list):
            bcc = ', '.join(bcc)
        
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc
        
        message.attach(MIMEText(body, 'plain'))
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        draft = {'message': {'raw': raw}}
        
        result = service.users().drafts().create(userId='me', body=draft).execute()
        
        return {
            'draft_id': result['id'],
            'message_id': result['message']['id']
        }
    
    except Exception as e:
        print(f"❌ Failed to create draft: {e}")
        raise


def gmail_send_draft(draft_id, **kwargs):
    """Send an existing draft
    
    ✅ Supports credential injection via **kwargs
    """
    try:
        service = _get_gmail_service(**kwargs)
        result = service.users().drafts().send(userId='me', body={'id': draft_id}).execute()
        
        return {
            'message_id': result['id'],
            'thread_id': result['threadId']
        }
    
    except Exception as e:
        print(f"❌ Failed to send draft: {e}")
        raise


# ==================== EMAIL READING ====================

def gmail_list_messages(max_results=10, query=None, label_ids=None, **kwargs):
    """List messages in mailbox
    
    ✅ Supports credential injection via **kwargs
    """
    try:
        service = _get_gmail_service(**kwargs)
        
        params = {'userId': 'me', 'maxResults': max_results}
        if query:
            params['q'] = query
        if label_ids:
            params['labelIds'] = label_ids
        
        result = service.users().messages().list(**params).execute()
        messages = result.get('messages', [])
        
        return {
            'messages': messages,
            'count': len(messages),
            'next_page_token': result.get('nextPageToken')
        }
    
    except Exception as e:
        print(f"❌ Failed to list messages: {e}")
        raise


def gmail_get_message(message_id, format='metadata', **kwargs):
    """
    Get a specific message by ID
    
    Args:
        message_id: Gmail message ID
        format: 'metadata' (default - lightweight, recommended for browsing),
                'minimal' (IDs only),
                'full' (complete message - LARGE, use only when user asks for full content)
        **kwargs: Credential injection (_user_id, _injected_credentials)
    
    Returns:
        Message object with varying detail based on format
        
    WARNING: format='full' can return 10k+ tokens per message for emails with
             HTML bodies, attachments, and headers. Use 'metadata' for browsing.
    """
    try:
        service = _get_gmail_service(**kwargs)
        message = service.users().messages().get(userId='me', id=message_id, format=format).execute()
        
        return message
    
    except Exception as e:
        print(f"❌ Failed to get message: {e}")
        raise


def gmail_get_message_parsed(message_id, include_attachments=True, output_format='json', **kwargs):
    """
    Get message with AI-OPTIMIZED parsing (clean text, no raw base64)
    
    This function:
    - Fetches message with format='full'
    - Parses MIME structure using universal parser
    - Extracts clean text from HTML emails
    - Downloads and parses attachments (PDF -> text, Word -> text, Excel -> CSV)
    - Returns structured JSON or PDF ready for Claude
    
    Args:
        message_id: Gmail message ID
        include_attachments: Whether to download and parse attachments (default True)
        output_format: 'json' (default) or 'pdf' (for Claude document API)
        **kwargs: Credential injection (_user_id, _injected_credentials)
    
    Returns:
        If output_format='json':
            {
                'id': str,
                'thread_id': str,
                'from': {'name': str, 'email': str},
                'to': [{'name': str, 'email': str}],
                'subject': str,
                'date': str (ISO format),
                'body_text': str (clean text, HTML converted),
                'attachments': [
                    {
                        'filename': str,
                        'content_type': str,
                        'size_bytes': int,
                        'parsed_content': str (text extracted from PDF/Word/Excel)
                    }
                ],
                'token_estimate': int (rough token count)
            }
        
        If output_format='pdf':
            bytes (PDF ready for Claude document API)
    
    Example:
        # Get clean email for AI analysis (JSON)
        parsed = gmail_get_message_parsed('msg_abc123', include_attachments=True)
        print(parsed['body_text'])  # Clean text, not HTML!
        
        # Get email as PDF for Claude
        pdf_bytes = gmail_get_message_parsed('msg_abc123', output_format='pdf')
        pdf_base64 = base64.b64encode(pdf_bytes).decode()
    """
    try:
        # Import universal parser from infrastructure
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent / 'AI_infrastructure'))
        from core.email_parser import UniversalEmailParser
        
        # Get full message (yes, with all MIME data)
        service = _get_gmail_service(**kwargs)
        raw_message = service.users().messages().get(
            userId='me', 
            id=message_id, 
            format='full'
        ).execute()
        
        # Parse using universal parser
        parser = UniversalEmailParser()
        parsed = parser.parse_gmail_message(
            raw_message, 
            download_attachments=include_attachments
        )
        
        # Convert to requested format
        return parser.prepare_for_claude(parsed, output_format=output_format)
    
    except Exception as e:
        print(f"❌ Failed to parse message: {e}")
        raise


def gmail_get_thread_parsed(thread_id, max_messages=20, output_format='json', **kwargs):
    """
    Get entire email thread with timeline and parsed content
    
    This reconstructs conversation flow with:
    - Chronological message order
    - Participant list
    - Clean text for each message
    - Thread position markers
    
    Args:
        thread_id: Gmail thread ID
        max_messages: Max messages to fetch (default 20)
        output_format: 'json' (default) or 'pdf' (for Claude document API)
        **kwargs: Credential injection
    
    Returns:
        If output_format='json':
            {
                'thread_id': str,
                'subject': str,
                'participants': [{'name': str, 'email': str}],
                'start_date': str,
                'last_date': str,
                'message_count': int,
                'messages': [
                    {
                        'position': 1,
                        'from': {'name': str, 'email': str},
                        'date': str,
                        'body_text': str (preview),
                        'full_message_id': str (use gmail_get_message_parsed for full content)
                    }
                ],
                'token_estimate': int
            }
        
        If output_format='pdf':
            bytes (PDF ready for Claude document API with entire thread)
    """
    try:
        # Import universal parser from infrastructure
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent / 'AI_infrastructure'))
        from core.email_parser import UniversalEmailParser
        
        service = _get_gmail_service(**kwargs)
        
        # Get thread with all messages
        thread = service.users().threads().get(
            userId='me',
            id=thread_id,
            format='full'
        ).execute()
        
        messages = thread.get('messages', [])[:max_messages]
        
        # Parse each message
        parser = UniversalEmailParser()
        parsed_messages = [
            parser.parse_gmail_message(msg, download_attachments=True) 
            for msg in messages
        ]
        
        # Convert to requested format
        if output_format == 'json':
            # Build timeline for JSON output
            timeline = parser.parse_email_thread_timeline(parsed_messages)
            return timeline
        else:
            # Return PDF bytes (full messages with attachments)
            return parser.prepare_for_claude(parsed_messages, output_format=output_format)
    
    except Exception as e:
        print(f"❌ Failed to parse thread: {e}")
        raise


def gmail_get_attachment(message_id, attachment_id, **kwargs):
    """Get an attachment from a message"""
    try:
        service = _get_gmail_service(**kwargs)
        attachment = service.users().messages().attachments().get(
            userId='me',
            messageId=message_id,
            id=attachment_id
        ).execute()
        
        # Decode attachment data
        data = base64.urlsafe_b64decode(attachment['data'])
        
        return {
            'data': data,
            'size': attachment['size']
        }
    
    except Exception as e:
        print(f"❌ Failed to get attachment: {e}")
        raise


# ==================== EMAIL MANAGEMENT ====================

def gmail_delete_message(message_id, **kwargs):
    """Delete a message (move to trash)"""
    try:
        service = _get_gmail_service(**kwargs)
        service.users().messages().trash(userId='me', id=message_id).execute()
        
        return {'deleted': True, 'message_id': message_id}
    
    except Exception as e:
        print(f"❌ Failed to delete message: {e}")
        raise


def gmail_modify_message(message_id, add_label_ids=None, remove_label_ids=None, **kwargs):
    """Modify message labels"""
    try:
        service = _get_gmail_service(**kwargs)
        
        body = {}
        if add_label_ids:
            body['addLabelIds'] = add_label_ids
        if remove_label_ids:
            body['removeLabelIds'] = remove_label_ids
        
        result = service.users().messages().modify(userId='me', id=message_id, body=body).execute()
        
        return result
    
    except Exception as e:
        print(f"❌ Failed to modify message: {e}")
        raise


def gmail_mark_as_read(message_id, **kwargs):
    """Mark message as read"""
    return gmail_modify_message(message_id, remove_label_ids=['UNREAD'], **kwargs)


def gmail_mark_as_unread(message_id, **kwargs):
    """Mark message as unread"""
    return gmail_modify_message(message_id, add_label_ids=['UNREAD'], **kwargs)


def gmail_archive_message(message_id, **kwargs):
    """Archive a message (remove from inbox)"""
    return gmail_modify_message(message_id, remove_label_ids=['INBOX'], **kwargs)


def gmail_unarchive_message(message_id, **kwargs):
    """Unarchive a message (add to inbox)"""
    return gmail_modify_message(message_id, add_label_ids=['INBOX'], **kwargs)


# ==================== LABELS ====================

def gmail_list_labels(**kwargs):
    """List all labels"""
    try:
        service = _get_gmail_service(**kwargs)
        result = service.users().labels().list(userId='me').execute()
        labels = result.get('labels', [])
        
        return {'labels': labels, 'count': len(labels)}
    
    except Exception as e:
        print(f"❌ Failed to list labels: {e}")
        raise


def gmail_create_label(name, label_list_visibility='labelShow', message_list_visibility='show', **kwargs):
    """Create a new label"""
    try:
        service = _get_gmail_service(**kwargs)
        
        label = {
            'name': name,
            'labelListVisibility': label_list_visibility,
            'messageListVisibility': message_list_visibility
        }
        
        result = service.users().labels().create(userId='me', body=label).execute()
        
        return result
    
    except Exception as e:
        print(f"❌ Failed to create label: {e}")
        raise


def gmail_update_label(label_id, name=None, label_list_visibility=None, message_list_visibility=None, **kwargs):
    """Update a label"""
    try:
        service = _get_gmail_service(**kwargs)
        
        label = {}
        if name:
            label['name'] = name
        if label_list_visibility:
            label['labelListVisibility'] = label_list_visibility
        if message_list_visibility:
            label['messageListVisibility'] = message_list_visibility
        
        result = service.users().labels().update(userId='me', id=label_id, body=label).execute()
        
        return result
    
    except Exception as e:
        print(f"❌ Failed to update label: {e}")
        raise


def gmail_delete_label(label_id, **kwargs):
    """Delete a label"""
    try:
        service = _get_gmail_service(**kwargs)
        service.users().labels().delete(userId='me', id=label_id).execute()
        
        return {'deleted': True, 'label_id': label_id}
    
    except Exception as e:
        print(f"❌ Failed to delete label: {e}")
        raise


# ==================== FILTERS ====================

def gmail_create_filter(criteria, action, **kwargs):
    """Create a mail filter"""
    try:
        service = _get_gmail_service(**kwargs)
        
        filter_body = {
            'criteria': criteria,
            'action': action
        }
        
        result = service.users().settings().filters().create(userId='me', body=filter_body).execute()
        
        return result
    
    except Exception as e:
        print(f"❌ Failed to create filter: {e}")
        raise


def gmail_list_filters(**kwargs):
    """List all filters"""
    try:
        service = _get_gmail_service(**kwargs)
        result = service.users().settings().filters().list(userId='me').execute()
        filters = result.get('filter', [])
        
        return {'filters': filters, 'count': len(filters)}
    
    except Exception as e:
        print(f"❌ Failed to list filters: {e}")
        raise


def gmail_delete_filter(filter_id, **kwargs):
    """Delete a filter"""
    try:
        service = _get_gmail_service(**kwargs)
        service.users().settings().filters().delete(userId='me', id=filter_id).execute()
        
        return {'deleted': True, 'filter_id': filter_id}
    
    except Exception as e:
        print(f"❌ Failed to delete filter: {e}")
        raise


# ==================== PROFILE & INFO ====================

def gmail_get_profile(**kwargs):
    """Get Gmail profile information"""
    try:
        service = _get_gmail_service(**kwargs)
        profile = service.users().getProfile(userId='me').execute()
        
        return profile
    
    except Exception as e:
        print(f"❌ Failed to get profile: {e}")
        raise


# ==================== SEARCH ====================

def gmail_search_messages(query, max_results=10, **kwargs):
    """Search messages with query"""
    return gmail_list_messages(max_results=max_results, query=query, **kwargs)


# ==================== BATCH OPERATIONS ====================

def gmail_batch_delete(message_ids, **kwargs):
    """Delete multiple messages"""
    try:
        service = _get_gmail_service(**kwargs)
        service.users().messages().batchDelete(userId='me', body={'ids': message_ids}).execute()
        
        return {'deleted': len(message_ids), 'message_ids': message_ids}
    
    except Exception as e:
        print(f"❌ Failed to batch delete: {e}")
        raise


def gmail_batch_modify(message_ids, add_label_ids=None, remove_label_ids=None, **kwargs):
    """Modify multiple messages"""
    try:
        service = _get_gmail_service(**kwargs)
        
        body = {'ids': message_ids}
        if add_label_ids:
            body['addLabelIds'] = add_label_ids
        if remove_label_ids:
            body['removeLabelIds'] = remove_label_ids
        
        service.users().messages().batchModify(userId='me', body=body).execute()
        
        return {'modified': len(message_ids), 'message_ids': message_ids}
    
    except Exception as e:
        print(f"❌ Failed to batch modify: {e}")
        raise


# ==================== WATCH / PUSH NOTIFICATIONS ====================

def gmail_watch_mailbox(topic_name, label_ids=None, **kwargs):
    """Watch mailbox for changes"""
    try:
        service = _get_gmail_service(**kwargs)
        
        request = {'topicName': topic_name}
        if label_ids:
            request['labelIds'] = label_ids
        
        result = service.users().watch(userId='me', body=request).execute()
        
        return result
    
    except Exception as e:
        print(f"❌ Failed to watch mailbox: {e}")
        raise


def gmail_stop_watch(**kwargs):
    """Stop watching mailbox"""
    try:
        service = _get_gmail_service()
        service.users().stop(userId='me').execute()
        
        return {'stopped': True}
    
    except Exception as e:
        print(f"❌ Failed to stop watch: {e}")
        raise


# ==================== THREADS ====================

def gmail_get_thread(thread_id, format='full', **kwargs):
    """Get a conversation thread
    
    ✅ Supports credential injection via **kwargs
    """
    try:
        service = _get_gmail_service(**kwargs)
        thread = service.users().threads().get(userId='me', id=thread_id, format=format).execute()
        
        return thread
    
    except Exception as e:
        print(f"❌ Failed to get thread: {e}")
        raise


def gmail_list_threads(max_results=10, query=None, **kwargs):
    """List conversation threads"""
    try:
        service = _get_gmail_service()
        
        params = {'userId': 'me', 'maxResults': max_results}
        if query:
            params['q'] = query
        
        result = service.users().threads().list(**params).execute()
        threads = result.get('threads', [])
        
        return {
            'threads': threads,
            'count': len(threads),
            'next_page_token': result.get('nextPageToken')
        }
    
    except Exception as e:
        print(f"❌ Failed to list threads: {e}")
        raise


def gmail_trash_thread(thread_id, **kwargs):
    """Move thread to trash"""
    try:
        service = _get_gmail_service()
        service.users().threads().trash(userId='me', id=thread_id).execute()
        
        return {'trashed': True, 'thread_id': thread_id}
    
    except Exception as e:
        print(f"❌ Failed to trash thread: {e}")
        raise


# ==================== HISTORY ====================

def gmail_get_history(start_history_id, max_results=100, label_id=None, **kwargs):
    """Get mailbox history"""
    try:
        service = _get_gmail_service()
        
        params = {
            'userId': 'me',
            'startHistoryId': start_history_id,
            'maxResults': max_results
        }
        if label_id:
            params['labelId'] = label_id
        
        result = service.users().history().list(**params).execute()
        
        return result
    
    except Exception as e:
        print(f"❌ Failed to get history: {e}")
        raise


# ==================== SMTP EMAIL SENDING ====================

def gmail_send_email_smtp(from_email, to, subject, body, cc=None, bcc=None, **kwargs):
    """
    Send email via SMTP from specific Gmail account.
    Works with any Gmail account using app passwords.
    
    Args:
        from_email: Sender email address (e.g., 'gpoli1982@gmail.com', 'gerardo@vetsuccessacademy.com')
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        cc: Optional CC recipients (comma-separated string)
        bcc: Optional BCC recipients (comma-separated string)
    
    Returns:
        dict: Success status and email details
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    try:
        # Get app password from environment based on email
        app_password = None
        
        if from_email == os.getenv('PERSONAL_EMAIL'):
            app_password = os.getenv('PERSONAL_EMAIL_APP_PASSWORD')
        elif from_email == os.getenv('WORK_EMAIL'):
            app_password = os.getenv('WORK_EMAIL_APP_PASSWORD')
        elif from_email == os.getenv('GERARDO_MVG_EMAIL'):
            app_password = os.getenv('GERARDO_MVG_PASSWORD')
        elif from_email == 'minivetguide@gmail.com':  # Corrected email
            app_password = os.getenv('MVG_EMAIL_APP_PASSWORD')
        elif from_email == os.getenv('MVG_MARKETING_EMAIL'):
            app_password = os.getenv('MVG_MARKETING_PASSWORD')
        else:
            raise ValueError(f"❌ No app password configured for {from_email}. Available accounts: {os.getenv('PERSONAL_EMAIL')}, {os.getenv('WORK_EMAIL')}, {os.getenv('GERARDO_MVG_EMAIL')}, minivetguide@gmail.com, {os.getenv('MVG_MARKETING_EMAIL')}")
        
        if not app_password:
            raise ValueError(f"❌ App password not found in environment for {from_email}")
        
        # Create message
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to
        
        if cc:
            msg['Cc'] = cc
        if bcc:
            msg['Bcc'] = bcc
        
        # Attach body
        msg.attach(MIMEText(body, 'plain'))
        
        # Send via Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(from_email, app_password)
            smtp.send_message(msg)
        
        print(f"✅ Email sent successfully from {from_email} to {to}")
        
        return {
            'success': True,
            'from': from_email,
            'to': to,
            'cc': cc,
            'bcc': bcc,
            'subject': subject,
            'method': 'SMTP'
        }
    
    except Exception as e:
        error_msg = f"❌ Failed to send email via SMTP: {str(e)}"
        print(error_msg)
        return {
            'success': False,
            'error': str(e),
            'from': from_email,
            'to': to
        }


def gmail_send_email_smtp_html(from_email, to, subject, html_body, plain_body=None, cc=None, bcc=None, **kwargs):
    """
    Send HTML email via SMTP from specific Gmail account.
    
    Args:
        from_email: Sender email address
        to: Recipient email address
        subject: Email subject
        html_body: Email body in HTML format
        plain_body: Optional plain text fallback
        cc: Optional CC recipients
        bcc: Optional BCC recipients
    
    Returns:
        dict: Success status and email details
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    try:
        # Get app password
        app_password = None
        
        if from_email == os.getenv('PERSONAL_EMAIL'):
            app_password = os.getenv('PERSONAL_EMAIL_APP_PASSWORD')
        elif from_email == os.getenv('WORK_EMAIL'):
            app_password = os.getenv('WORK_EMAIL_APP_PASSWORD')
        elif from_email == os.getenv('GERARDO_MVG_EMAIL'):
            app_password = os.getenv('GERARDO_MVG_PASSWORD')
        elif from_email == 'minivetguide@gmail.com':
            app_password = os.getenv('MVG_EMAIL_APP_PASSWORD')
        elif from_email == os.getenv('MVG_MARKETING_EMAIL'):
            app_password = os.getenv('MVG_MARKETING_PASSWORD')
        else:
            raise ValueError(f"❌ No app password configured for {from_email}")
        
        if not app_password:
            raise ValueError(f"❌ App password not found in environment for {from_email}")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to
        
        if cc:
            msg['Cc'] = cc
        if bcc:
            msg['Bcc'] = bcc
        
        # Attach plain text and HTML versions
        if plain_body:
            msg.attach(MIMEText(plain_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send via Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(from_email, app_password)
            smtp.send_message(msg)
        
        print(f"✅ HTML email sent successfully from {from_email} to {to}")
        
        return {
            'success': True,
            'from': from_email,
            'to': to,
            'cc': cc,
            'bcc': bcc,
            'subject': subject,
            'method': 'SMTP',
            'format': 'HTML'
        }
    
    except Exception as e:
        error_msg = f"❌ Failed to send HTML email via SMTP: {str(e)}"
        print(error_msg)
        return {
            'success': False,
            'error': str(e),
            'from': from_email,
            'to': to
        }


def gmail_list_available_accounts(**kwargs):
    """
    List all Gmail accounts available for sending via SMTP.
    
    Returns:
        dict: Available email accounts with their configuration status
    """
    accounts = {
        'personal': {
            'email': os.getenv('PERSONAL_EMAIL'),
            'has_password': bool(os.getenv('PERSONAL_EMAIL_APP_PASSWORD')),
            'description': 'Personal Gmail account'
        },
        'work': {
            'email': os.getenv('WORK_EMAIL'),
            'has_password': bool(os.getenv('WORK_EMAIL_APP_PASSWORD')),
            'description': 'Work email (Vet Success Academy)'
        },
        'minivet_gerardo': {
            'email': os.getenv('GERARDO_MVG_EMAIL'),
            'has_password': bool(os.getenv('GERARDO_MVG_PASSWORD')),
            'description': 'MiniVet Guide (Gerardo)'
        },
        'minivet_main': {
            'email': 'minivetguide@gmail.com',
            'has_password': bool(os.getenv('MVG_EMAIL_PASSWORD')),
            'description': 'MiniVet Guide main account'
        },
        'minivet_marketing': {
            'email': os.getenv('MVG_MARKETING_EMAIL'),
            'has_password': bool(os.getenv('MVG_EMAIL_PASSWORD')),
            'description': 'MiniVet Guide marketing'
        }
    }
    
    # Filter to only configured accounts
    configured = {k: v for k, v in accounts.items() if v['email'] and v['has_password']}
    
    print(f"✅ Found {len(configured)} configured email accounts")
    for key, account in configured.items():
        print(f"   • {account['email']} - {account['description']}")
    
    return {
        'total': len(configured),
        'accounts': configured
    }


# ==================== GMAIL SMART BUNDLED TOOLS ====================

def gmail_ai_smart_compose_and_send(prompt, recipients, cc=None, bcc=None, 
                                    tone="professional", send_immediately=True,
                                    attachments=None, create_calendar_event=False, **kwargs):
    """
    🤖 SMART TOOL: AI-powered email composition and sending in ONE call.
    
    Takes a natural language prompt and generates a complete, professional email.
    Optionally creates calendar events from the email content.
    
    Args:
        prompt (str): Natural language description of what to write
                     Example: "Follow up with John about yesterday's product launch meeting"
        recipients (list): Email addresses to send to
        cc (list, optional): CC recipients
        bcc (list, optional): BCC recipients
        tone (str): Email tone - "professional", "casual", "formal", "friendly"
        send_immediately (bool): If True, sends email. If False, creates draft.
        attachments (list, optional): File paths to attach
        create_calendar_event (bool): If True, extracts date/time from email and creates Google Calendar event
    
    Returns:
        dict: {
            'email_sent': bool,
            'message_id': str,
            'subject': str,
            'body': str (generated content),
            'calendar_event_id': str (if create_calendar_event=True),
            'draft_id': str (if send_immediately=False)
        }
    
    Use Cases:
        - "Follow up with client about proposal"
        - "Thank the team for Q4 performance"
        - "Apologize to customer for order #12345 delay"
        - "Schedule meeting with john@co.com for next week"
    """
    try:
        import openai
        from datetime import datetime
        
        # Get OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception("OPENAI_API_KEY not found in environment")
        
        openai.api_key = api_key
        
        print(f"🤖 Generating email with AI (tone: {tone})...")
        
        # Create AI prompt for email generation
        system_prompt = f"""You are an expert email writer. Generate professional emails based on user requests.
        
Tone: {tone}
Output format: JSON with 'subject' and 'body' fields.
The body should be complete with greeting, content, and signature.
If the prompt mentions dates/times for meetings, include them clearly in the email.

Example output:
{{
  "subject": "Follow-up: Product Launch Discussion",
  "body": "Hi John,\\n\\nI wanted to follow up on our product launch meeting yesterday...\\n\\nBest regards"
}}"""
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # Parse AI response
        import json
        email_data = json.loads(response.choices[0].message.content)
        subject = email_data.get('subject', 'No Subject')
        body = email_data.get('body', '')
        
        print(f"✅ Generated email: '{subject}'")
        
        # Send or create draft
        if send_immediately:
            print(f"📧 Sending to {len(recipients)} recipient(s)...")
            result = gmail_send_email(
                to=', '.join(recipients),
                subject=subject,
                body=body,
                cc=', '.join(cc) if cc else None,
                bcc=', '.join(bcc) if bcc else None,
                attachments=attachments
            )
            
            response_data = {
                'email_sent': True,
                'message_id': result['message_id'],
                'thread_id': result['thread_id'],
                'subject': subject,
                'body': body,
                'recipients': recipients
            }
        else:
            print(f"📝 Creating draft...")
            result = gmail_create_draft(
                to=', '.join(recipients),
                subject=subject,
                body=body,
                cc=', '.join(cc) if cc else None,
                bcc=', '.join(bcc) if bcc else None
            )
            
            response_data = {
                'email_sent': False,
                'draft_id': result['id'],
                'subject': subject,
                'body': body,
                'recipients': recipients
            }
        
        # Create calendar event if requested
        if create_calendar_event:
            try:
                # Extract date/time from email using AI
                print("📅 Extracting calendar event from email...")
                event_prompt = f"Extract meeting date, time, and title from this email. Return JSON with 'date', 'time', 'title', 'duration_minutes'. Email: {body}"
                
                event_response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Extract calendar event details. Return JSON only."},
                        {"role": "user", "content": event_prompt}
                    ],
                    temperature=0.3
                )
                
                event_data = json.loads(event_response.choices[0].message.content)
                
                # Create calendar event (would integrate with google_calendar.py)
                from google_workspace import google_calendar
                calendar_result = google_calendar.create_event(
                    summary=event_data.get('title', subject),
                    start_time=f"{event_data['date']}T{event_data['time']}:00",
                    duration_minutes=event_data.get('duration_minutes', 60),
                    attendees=[{'email': r} for r in recipients]
                )
                
                response_data['calendar_event_id'] = calendar_result['id']
                response_data['calendar_event_link'] = calendar_result['htmlLink']
                print(f"✅ Calendar event created: {calendar_result['id']}")
                
            except Exception as e:
                print(f"⚠️ Could not create calendar event: {e}")
                response_data['calendar_event_error'] = str(e)
        
        return response_data
        
    except Exception as e:
        print(f"❌ Failed to compose and send email: {e}")
        raise


def gmail_smart_bulk_send_personalized(template, recipients_data, subject_template,
                                        cc=None, bcc=None, delay_seconds=2, **kwargs):
    """
    📧 SMART TOOL: Send personalized bulk emails with mail merge in ONE call.
    
    Send customized emails to multiple recipients using template variables.
    Each email is personalized with recipient-specific data.
    
    Args:
        template (str): Email body template with {{variables}}
                       Example: "Hi {{name}}, your order {{order_id}} is ready!"
        recipients_data (list): Array of recipient objects with email and variables
                               Example: [
                                   {"email": "john@co.com", "name": "John", "order_id": "12345"},
                                   {"email": "sarah@co.com", "name": "Sarah", "order_id": "12346"}
                               ]
        subject_template (str): Email subject with {{variables}}
                               Example: "Your Order {{order_id}} Update"
        cc (list, optional): CC recipients for ALL emails
        bcc (list, optional): BCC recipients for ALL emails
        delay_seconds (int): Seconds to wait between sends (avoid rate limits)
    
    Returns:
        dict: {
            'total_sent': int,
            'successful': list of email addresses,
            'failed': list of {email, error},
            'sent_messages': list of message IDs
        }
    
    Use Cases:
        - Send 50 customers their personalized invoices
        - Email team members their individual performance reports
        - Send new hires their custom onboarding instructions
        - Bulk outreach with personalized content
    """
    try:
        import time
        import re
        
        print(f"📧 Sending personalized emails to {len(recipients_data)} recipients...")
        
        successful = []
        failed = []
        sent_messages = []
        
        for i, recipient in enumerate(recipients_data):
            try:
                email = recipient.get('email')
                if not email:
                    raise Exception("Missing email address")
                
                # Replace template variables with recipient data
                personalized_body = template
                personalized_subject = subject_template
                
                for key, value in recipient.items():
                    if key != 'email':
                        personalized_body = personalized_body.replace(f"{{{{{key}}}}}", str(value))
                        personalized_subject = personalized_subject.replace(f"{{{{{key}}}}}", str(value))
                
                print(f"  [{i+1}/{len(recipients_data)}] Sending to {email}...")
                
                # Send email
                result = gmail_send_email(
                    to=email,
                    subject=personalized_subject,
                    body=personalized_body,
                    cc=', '.join(cc) if cc else None,
                    bcc=', '.join(bcc) if bcc else None
                )
                
                successful.append(email)
                sent_messages.append(result['message_id'])
                
                # Delay between sends to avoid rate limits
                if i < len(recipients_data) - 1:
                    time.sleep(delay_seconds)
                
            except Exception as e:
                print(f"  ❌ Failed to send to {recipient.get('email', 'unknown')}: {e}")
                failed.append({'email': recipient.get('email'), 'error': str(e)})
        
        print(f"✅ Bulk send complete: {len(successful)} sent, {len(failed)} failed")
        
        return {
            'total_sent': len(successful),
            'total_failed': len(failed),
            'successful': successful,
            'failed': failed,
            'sent_messages': sent_messages
        }
        
    except Exception as e:
        print(f"❌ Bulk send failed: {e}")
        raise


def gmail_smart_bulk_read_summarize_prioritize(query="is:unread", max_messages=50,
                                               summarize=True, prioritize=True,
                                               create_spreadsheet=False, **kwargs):
    """
    📖 SMART TOOL: Bulk read, summarize, and prioritize emails in ONE call.
    
    Reads multiple emails, generates AI summaries, prioritizes by importance,
    and optionally creates a Google Spreadsheet with recommended actions.
    
    Args:
        query (str): Gmail search query (default: "is:unread")
                    Examples: "from:client.com", "has:attachment", "newer_than:7d"
        max_messages (int): Maximum number of messages to process
        summarize (bool): Generate AI summaries for each email
        prioritize (bool): Assign priority scores (1-5, 5=urgent)
        create_spreadsheet (bool): Create Google Sheets with results and recommended actions
    
    Returns:
        dict: {
            'total_processed': int,
            'emails': list of {
                'message_id': str,
                'from': str,
                'subject': str,
                'date': str,
                'summary': str (if summarize=True),
                'priority': int (if prioritize=True, 1-5 scale),
                'recommended_action': str,
                'labels': list
            },
            'spreadsheet_id': str (if create_spreadsheet=True),
            'spreadsheet_url': str (if create_spreadsheet=True)
        }
    
    Use Cases:
        - "Process my 200 unread emails and tell me what's urgent"
        - "Summarize all emails from clients this week"
        - "Read all emails with attachments and prioritize"
        - "Create spreadsheet of all unread emails with recommended actions"
    """
    try:
        import openai
        from datetime import datetime
        
        print(f"📖 Reading and analyzing emails (query: {query})...")
        
        # Search for messages
        messages = gmail_search_messages(query=query, max_results=max_messages)
        
        if not messages.get('messages'):
            print("ℹ️ No messages found")
            return {'total_processed': 0, 'emails': []}
        
        print(f"Found {len(messages['messages'])} messages. Processing...")
        
        processed_emails = []
        
        for i, msg_summary in enumerate(messages['messages']):
            try:
                # Get full message
                msg = gmail_get_message(msg_summary['id'], format='full')
                
                headers = {h['name']: h['value'] for h in msg['payload']['headers']}
                from_email = headers.get('From', 'Unknown')
                subject = headers.get('Subject', 'No Subject')
                date = headers.get('Date', '')
                
                # Get email body
                body = ""
                if 'parts' in msg['payload']:
                    for part in msg['payload']['parts']:
                        if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break
                elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                    body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
                
                # Truncate body for AI processing (first 500 chars)
                body_preview = body[:500] if body else "No body content"
                
                email_data = {
                    'message_id': msg['id'],
                    'thread_id': msg['threadId'],
                    'from': from_email,
                    'subject': subject,
                    'date': date,
                    'body_preview': body_preview,
                    'labels': msg.get('labelIds', [])
                }
                
                # AI Summarization
                if summarize:
                    try:
                        api_key = os.getenv('OPENAI_API_KEY')
                        if api_key:
                            openai.api_key = api_key
                            
                            summary_response = openai.ChatCompletion.create(
                                model="gpt-4",
                                messages=[
                                    {"role": "system", "content": "Summarize this email in 1-2 sentences. Be concise."},
                                    {"role": "user", "content": f"From: {from_email}\nSubject: {subject}\n\n{body_preview}"}
                                ],
                                max_tokens=100,
                                temperature=0.3
                            )
                            
                            email_data['summary'] = summary_response.choices[0].message.content.strip()
                    except Exception as e:
                        email_data['summary'] = f"Summary unavailable: {e}"
                
                # AI Prioritization
                if prioritize:
                    try:
                        api_key = os.getenv('OPENAI_API_KEY')
                        if api_key:
                            openai.api_key = api_key
                            
                            priority_response = openai.ChatCompletion.create(
                                model="gpt-4",
                                messages=[
                                    {"role": "system", "content": "Rate email urgency 1-5 (5=urgent, 1=low). Return only the number and recommended action. Format: '5|Reply immediately' or '2|Archive'"},
                                    {"role": "user", "content": f"From: {from_email}\nSubject: {subject}\n\n{body_preview}"}
                                ],
                                max_tokens=50,
                                temperature=0.3
                            )
                            
                            priority_text = priority_response.choices[0].message.content.strip()
                            parts = priority_text.split('|')
                            email_data['priority'] = int(parts[0]) if parts[0].isdigit() else 3
                            email_data['recommended_action'] = parts[1] if len(parts) > 1 else "Review"
                    except Exception as e:
                        email_data['priority'] = 3
                        email_data['recommended_action'] = "Review"
                
                processed_emails.append(email_data)
                
                print(f"  [{i+1}/{len(messages['messages'])}] Processed: {subject[:50]}...")
                
            except Exception as e:
                print(f"  ⚠️ Error processing message {msg_summary['id']}: {e}")
        
        # Sort by priority (highest first)
        if prioritize:
            processed_emails.sort(key=lambda x: x.get('priority', 0), reverse=True)
        
        print(f"✅ Processed {len(processed_emails)} emails")
        
        # Create spreadsheet if requested
        spreadsheet_data = {}
        if create_spreadsheet and processed_emails:
            try:
                from google_workspace import gsheets
                
                print("📊 Creating spreadsheet with results...")
                
                # Prepare data for spreadsheet
                headers = ['Priority', 'From', 'Subject', 'Date', 'Summary', 'Recommended Action', 'Message ID']
                rows = [headers]
                
                for email in processed_emails:
                    rows.append([
                        email.get('priority', ''),
                        email.get('from', ''),
                        email.get('subject', ''),
                        email.get('date', ''),
                        email.get('summary', ''),
                        email.get('recommended_action', ''),
                        email.get('message_id', '')
                    ])
                
                # Create spreadsheet
                result = gsheets.gsheets_create_complete_spreadsheet(
                    title=f"Email Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    data=rows,
                    bold_headers=True,
                    freeze_header_row=True
                )
                
                spreadsheet_data = {
                    'spreadsheet_id': result['spreadsheet_id'],
                    'spreadsheet_url': result['spreadsheet_url']
                }
                
                print(f"✅ Spreadsheet created: {result['spreadsheet_url']}")
                
            except Exception as e:
                print(f"⚠️ Could not create spreadsheet: {e}")
                spreadsheet_data['error'] = str(e)
        
        return {
            'total_processed': len(processed_emails),
            'emails': processed_emails,
            **spreadsheet_data
        }
        
    except Exception as e:
        print(f"❌ Bulk read/summarize failed: {e}")
        raise


def gmail_smart_auto_reply_draft_creator(message_ids, response_type="acknowledge",
                                         tone="professional", custom_instructions=None,
                                         create_drafts=True, **kwargs):
    """
    💬 SMART TOOL: Auto-generate reply drafts for multiple emails in ONE call.
    
    Analyzes emails and creates AI-generated reply drafts with appropriate responses.
    
    Args:
        message_ids (list): List of Gmail message IDs to reply to
        response_type (str): Type of response - "acknowledge", "answer", "decline", "accept", "custom"
        tone (str): Response tone - "professional", "casual", "formal", "friendly"
        custom_instructions (str, optional): Additional instructions for AI
                                           Example: "Mention our support hours are 9-5 EST"
        create_drafts (bool): If True, creates drafts. If False, just returns generated text.
    
    Returns:
        dict: {
            'total_processed': int,
            'replies': list of {
                'original_message_id': str,
                'original_subject': str,
                'original_from': str,
                'generated_reply': str,
                'draft_id': str (if create_drafts=True)
            }
        }
    
    Use Cases:
        - "Create reply drafts for all support emails"
        - "Auto-respond to meeting requests with availability"
        - "Generate acknowledgment replies for all customer orders"
        - "Draft responses to all unread emails from clients"
    """
    try:
        import openai
        
        print(f"💬 Generating replies for {len(message_ids)} emails...")
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception("OPENAI_API_KEY not found")
        
        openai.api_key = api_key
        
        replies = []
        
        for i, message_id in enumerate(message_ids):
            try:
                # Get original message
                msg = gmail_get_message(message_id, format='full')
                
                headers = {h['name']: h['value'] for h in msg['payload']['headers']}
                from_email = headers.get('From', 'Unknown')
                subject = headers.get('Subject', 'No Subject')
                
                # Get body
                body = ""
                if 'parts' in msg['payload']:
                    for part in msg['payload']['parts']:
                        if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break
                elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                    body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
                
                body_preview = body[:800] if body else ""
                
                print(f"  [{i+1}/{len(message_ids)}] Generating reply for: {subject[:50]}...")
                
                # Generate AI response
                system_prompt = f"""Generate an email reply.
Response type: {response_type}
Tone: {tone}
{f'Custom instructions: {custom_instructions}' if custom_instructions else ''}

Return JSON with 'subject' and 'body' fields."""
                
                user_prompt = f"""Original email:
From: {from_email}
Subject: {subject}

{body_preview}

Generate an appropriate reply."""
                
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )
                
                import json
                reply_data = json.loads(response.choices[0].message.content)
                
                reply_subject = reply_data.get('subject', f"Re: {subject}")
                reply_body = reply_data.get('body', '')
                
                reply_info = {
                    'original_message_id': message_id,
                    'original_subject': subject,
                    'original_from': from_email,
                    'generated_subject': reply_subject,
                    'generated_reply': reply_body
                }
                
                # Create draft if requested
                if create_drafts:
                    draft_result = gmail_create_draft(
                        to=from_email,
                        subject=reply_subject,
                        body=reply_body
                    )
                    reply_info['draft_id'] = draft_result['id']
                    print(f"    ✅ Draft created: {draft_result['id']}")
                
                replies.append(reply_info)
                
            except Exception as e:
                print(f"  ❌ Error processing message {message_id}: {e}")
                replies.append({
                    'original_message_id': message_id,
                    'error': str(e)
                })
        
        print(f"✅ Generated {len(replies)} replies")
        
        return {
            'total_processed': len(replies),
            'replies': replies
        }
        
    except Exception as e:
        print(f"❌ Auto-reply generation failed: {e}")
        raise


def gmail_smart_inbox_organizer_cleaner(action="organize", categories=None, 
                                        rules=None, process_existing=True,
                                        archive_older_than_days=None,
                                        delete_spam=False, **kwargs):
    """
    🗂️ SMART TOOL: Organize, clean, and auto-filter inbox in ONE call.
    
    Analyzes inbox, creates labels, applies filters, archives old emails,
    and organizes messages automatically.
    
    Args:
        action (str): Action to perform - "organize", "cleanup", "auto_filter", "full"
        categories (list, optional): Label categories to create
                                    Example: ["Clients", "Internal", "Newsletters", "Urgent"]
        rules (list, optional): Filtering rules
                               Example: [
                                   {"from": "team@co.com", "label": "Team", "archive": False},
                                   {"subject_contains": "invoice", "label": "Invoices", "important": True},
                                   {"from_domain": "newsletter.com", "label": "News", "archive": True}
                               ]
        process_existing (bool): Apply rules to existing emails
        archive_older_than_days (int, optional): Archive emails older than N days
        delete_spam (bool): Permanently delete emails in Spam folder
    
    Returns:
        dict: {
            'labels_created': list of label names,
            'filters_created': int,
            'emails_processed': int,
            'emails_archived': int,
            'emails_deleted': int,
            'organization_summary': dict
        }
    
    Use Cases:
        - "Organize my inbox - create labels and filter emails"
        - "Clean up inbox - archive old emails, delete spam"
        - "Set up auto-labeling for client emails"
        - "Create filters for all team emails and newsletters"
    """
    try:
        print(f"🗂️ Starting inbox organization (action: {action})...")
        
        labels_created = []
        filters_created = 0
        emails_processed = 0
        emails_archived = 0
        emails_deleted = 0
        
        # Create labels if specified
        if categories:
            print(f"Creating {len(categories)} labels...")
            for category in categories:
                try:
                    result = gmail_create_label(name=category)
                    labels_created.append(category)
                    print(f"  ✅ Created label: {category}")
                except Exception as e:
                    # Label might already exist
                    print(f"  ℹ️ Label '{category}' may already exist: {e}")
                    labels_created.append(f"{category} (existing)")
        
        # Create filters if rules specified
        if rules:
            print(f"Creating {len(rules)} filters...")
            
            # First, get label IDs
            existing_labels = gmail_list_labels()
            label_map = {label['name']: label['id'] for label in existing_labels['labels']}
            
            for rule in rules:
                try:
                    # Build criteria
                    criteria = {}
                    if 'from' in rule:
                        criteria['from'] = rule['from']
                    if 'subject_contains' in rule:
                        criteria['subject'] = rule['subject_contains']
                    if 'from_domain' in rule:
                        criteria['from'] = f"@{rule['from_domain']}"
                    
                    # Build action
                    action_obj = {}
                    if 'label' in rule and rule['label'] in label_map:
                        action_obj['addLabelIds'] = [label_map[rule['label']]]
                    if rule.get('archive'):
                        action_obj['removeLabelIds'] = ['INBOX']
                    if rule.get('important'):
                        action_obj['addLabelIds'] = action_obj.get('addLabelIds', []) + ['IMPORTANT']
                    
                    # Create filter
                    gmail_create_filter(criteria=criteria, action=action_obj)
                    filters_created += 1
                    print(f"  ✅ Created filter: {criteria}")
                    
                except Exception as e:
                    print(f"  ⚠️ Could not create filter: {e}")
        
        # Process existing emails if requested
        if process_existing and rules:
            print("Processing existing emails...")
            
            for rule in rules:
                try:
                    # Build search query from rule
                    query_parts = []
                    if 'from' in rule:
                        query_parts.append(f"from:{rule['from']}")
                    if 'subject_contains' in rule:
                        query_parts.append(f"subject:{rule['subject_contains']}")
                    if 'from_domain' in rule:
                        query_parts.append(f"from:@{rule['from_domain']}")
                    
                    query = ' '.join(query_parts)
                    
                    # Search for matching emails
                    messages = gmail_search_messages(query=query, max_results=100)
                    
                    if messages.get('messages'):
                        # Get label ID
                        label_id = label_map.get(rule.get('label'))
                        
                        # Apply actions to matched emails
                        for msg in messages['messages']:
                            try:
                                add_labels = [label_id] if label_id else []
                                remove_labels = ['INBOX'] if rule.get('archive') else []
                                
                                gmail_modify_message(
                                    message_id=msg['id'],
                                    add_label_ids=add_labels,
                                    remove_label_ids=remove_labels
                                )
                                
                                emails_processed += 1
                                if rule.get('archive'):
                                    emails_archived += 1
                                    
                            except Exception as e:
                                print(f"    ⚠️ Could not modify message: {e}")
                        
                        print(f"  ✅ Processed {len(messages['messages'])} emails for rule: {query}")
                        
                except Exception as e:
                    print(f"  ⚠️ Error processing rule: {e}")
        
        # Archive old emails if specified
        if archive_older_than_days:
            print(f"Archiving emails older than {archive_older_than_days} days...")
            try:
                query = f"older_than:{archive_older_than_days}d in:inbox"
                old_messages = gmail_search_messages(query=query, max_results=500)
                
                if old_messages.get('messages'):
                    archived_count = 0
                    for msg in old_messages['messages']:
                        try:
                            gmail_archive_message(msg['id'])
                            archived_count += 1
                        except Exception as e:
                            print(f"    ⚠️ Could not archive message: {e}")
                    
                    emails_archived += archived_count
                    print(f"  ✅ Archived {archived_count} old emails")
                    
            except Exception as e:
                print(f"  ⚠️ Error archiving old emails: {e}")
        
        # Delete spam if requested
        if delete_spam:
            print("Deleting spam emails...")
            try:
                spam_messages = gmail_search_messages(query="in:spam", max_results=500)
                
                if spam_messages.get('messages'):
                    deleted_count = 0
                    for msg in spam_messages['messages']:
                        try:
                            gmail_delete_message(msg['id'])
                            deleted_count += 1
                        except Exception as e:
                            print(f"    ⚠️ Could not delete message: {e}")
                    
                    emails_deleted = deleted_count
                    print(f"  ✅ Deleted {deleted_count} spam emails")
                    
            except Exception as e:
                print(f"  ⚠️ Error deleting spam: {e}")
        
        print(f"✅ Inbox organization complete!")
        
        return {
            'labels_created': labels_created,
            'filters_created': filters_created,
            'emails_processed': emails_processed,
            'emails_archived': emails_archived,
            'emails_deleted': emails_deleted,
            'organization_summary': {
                'total_labels': len(labels_created),
                'total_filters': filters_created,
                'total_emails_organized': emails_processed
            }
        }
        
    except Exception as e:
        print(f"❌ Inbox organization failed: {e}")
        raise
