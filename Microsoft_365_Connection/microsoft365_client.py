"""
Microsoft 365 API Client for InHouse Print Management System

This module provides Python integration with Microsoft 365 services:
- OneDrive for Business (file storage and sharing)
- Microsoft Graph API (Office documents, emails, calendars)
- Office document creation and manipulation
- SharePoint integration

Features:
- OAuth2 authentication with Microsoft Identity Platform
- OneDrive file upload/download/management
- Create Word, Excel, PowerPoint documents
- Email sending via Microsoft Graph
- Calendar management
- User and group management

Author: InHouse Print Development Team
Date: October 17, 2025
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, BinaryIO
import logging
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Microsoft365Client:
    """
    Microsoft 365 API Client for InHouse Print System
    
    Handles OAuth2 authentication and API requests to Microsoft Graph API
    """
    
    # Microsoft Graph API endpoints
    BASE_URL = "https://graph.microsoft.com/v1.0"
    AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Microsoft 365 client
        
        Args:
            config_path: Path to database-config.json (optional)
        """
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        
        # Load configuration
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'config', 'database-config.json'
            )
        
        self._load_config(config_path)
        
    def _load_config(self, config_path: str):
        """Load Microsoft 365 credentials from configuration file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Get Microsoft 365 config (you'll need to add this to database-config.json)
            m365_config = config.get('ExternalAPIs', {}).get('Microsoft365', {})
            
            self.client_id = m365_config.get('ClientId', os.environ.get('M365_CLIENT_ID'))
            self.client_secret = m365_config.get('ClientSecret', os.environ.get('M365_CLIENT_SECRET'))
            self.tenant_id = m365_config.get('TenantId', 'common')
            
            if not self.client_id or not self.client_secret:
                logger.warning("Missing Microsoft 365 credentials. Set M365_CLIENT_ID and M365_CLIENT_SECRET environment variables.")
            
            logger.info(f"Loaded Microsoft 365 config (Tenant: {self.tenant_id})")
            
        except Exception as e:
            logger.error(f"Failed to load Microsoft 365 config: {e}")
            raise
    
    def get_authorization_url(self, redirect_uri: str, state: Optional[str] = None) -> str:
        """
        Generate OAuth2 authorization URL for user consent
        
        PERMISSIONS: Read + Create for emails and documents
        - Read emails (to extract quote requests)
        - Create/upload files to OneDrive
        - Send emails
        - Create Office documents
        - Manage calendar
        
        Args:
            redirect_uri: Callback URL after authorization
            state: Optional state parameter for security
            
        Returns:
            Authorization URL to redirect user to
        """
        scopes = [
            'Files.ReadWrite.All',      # OneDrive: Read + Create files
            'Sites.ReadWrite.All',      # SharePoint: Read + Create
            'Mail.ReadWrite',           # Email: Read + Send (for quote requests)
            'Mail.Send',                # Send emails
            'Calendars.ReadWrite',      # Calendar: Read + Create events
            'User.Read',                # User profile
            'offline_access'            # Refresh token
        ]
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': ' '.join(scopes),
            'state': state or 'default_state',
            'response_mode': 'query'
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        auth_url = self.AUTH_URL.replace('/common/', f'/{self.tenant_id}/')
        return f"{auth_url}?{query_string}"
    
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from callback
            redirect_uri: Same redirect URI used in authorization
            
        Returns:
            Token response with access_token, refresh_token, etc.
        """
        token_url = self.TOKEN_URL.replace('/common/', f'/{self.tenant_id}/')
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self._update_tokens(token_data)
        
        return token_data
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh expired access token using refresh token
        
        Returns:
            New token response
        """
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        token_url = self.TOKEN_URL.replace('/common/', f'/{self.tenant_id}/')
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self._update_tokens(token_data)
        
        logger.info("Access token refreshed successfully")
        return token_data
    
    def _update_tokens(self, token_data: Dict[str, Any]):
        """Update internal token storage"""
        self.access_token = token_data.get('access_token')
        self.refresh_token = token_data.get('refresh_token')
        
        expires_in = token_data.get('expires_in', 3600)
        self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
    
    def _ensure_valid_token(self):
        """Ensure access token is valid, refresh if needed"""
        if not self.access_token:
            raise ValueError("No access token. Please authenticate first.")
        
        if self.token_expiry and datetime.now() >= self.token_expiry:
            logger.info("Token expired, refreshing...")
            self.refresh_access_token()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """
        Make authenticated API request to Microsoft Graph
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint path
            **kwargs: Additional request parameters
            
        Returns:
            JSON response or raw response
        """
        self._ensure_valid_token()
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = kwargs.pop('headers', {})
        headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        })
        
        # Don't set Content-Type for file uploads
        if 'files' not in kwargs and 'data' not in kwargs:
            headers['Content-Type'] = 'application/json'
        
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        
        # Return raw response for file downloads
        if kwargs.get('stream'):
            return response
        
        # Try to parse JSON, otherwise return text
        try:
            return response.json()
        except:
            return response.text
    
    # ==================== USER OPERATIONS ====================
    
    def get_me(self) -> Dict[str, Any]:
        """
        Get current authenticated user's profile
        
        Returns:
            User profile dictionary
        """
        return self._make_request('GET', '/me')
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get specific user by ID or email
        
        Args:
            user_id: User ID or email address
            
        Returns:
            User profile dictionary
        """
        return self._make_request('GET', f'/users/{user_id}')
    
    # ==================== ONEDRIVE OPERATIONS ====================
    
    def get_drive(self) -> Dict[str, Any]:
        """
        Get current user's OneDrive information
        
        Returns:
            Drive information dictionary
        """
        return self._make_request('GET', '/me/drive')
    
    def list_drive_items(self, folder_path: str = 'root') -> List[Dict[str, Any]]:
        """
        List items in OneDrive folder
        
        Args:
            folder_path: Folder path or 'root' for root folder
            
        Returns:
            List of drive items
        """
        if folder_path == 'root':
            endpoint = '/me/drive/root/children'
        else:
            endpoint = f'/me/drive/root:/{folder_path}:/children'
        
        response = self._make_request('GET', endpoint)
        return response.get('value', [])
    
    def create_folder(self, folder_name: str, parent_path: str = 'root') -> Dict[str, Any]:
        """
        Create folder in OneDrive
        
        Args:
            folder_name: Name of folder to create
            parent_path: Parent folder path or 'root'
            
        Returns:
            Created folder information
        """
        if parent_path == 'root':
            endpoint = '/me/drive/root/children'
        else:
            endpoint = f'/me/drive/root:/{parent_path}:/children'
        
        data = {
            'name': folder_name,
            'folder': {},
            '@microsoft.graph.conflictBehavior': 'rename'
        }
        
        return self._make_request('POST', endpoint, json=data)
    
    def upload_file(self, 
                   file_path: str, 
                   destination_path: str,
                   conflict_behavior: str = 'replace') -> Dict[str, Any]:
        """
        Upload file to OneDrive
        
        Args:
            file_path: Local file path to upload
            destination_path: Destination path in OneDrive (e.g., 'Documents/invoice.pdf')
            conflict_behavior: 'replace', 'rename', or 'fail'
            
        Returns:
            Uploaded file information
        """
        endpoint = f'/me/drive/root:/{destination_path}:/content'
        
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        headers = {
            'Content-Type': 'application/octet-stream'
        }
        
        return self._make_request('PUT', endpoint, data=file_content, headers=headers)
    
    def upload_file_content(self,
                           file_content: bytes,
                           destination_path: str,
                           conflict_behavior: str = 'replace') -> Dict[str, Any]:
        """
        Upload file content directly to OneDrive
        
        Args:
            file_content: File content as bytes
            destination_path: Destination path in OneDrive
            conflict_behavior: 'replace', 'rename', or 'fail'
            
        Returns:
            Uploaded file information
        """
        endpoint = f'/me/drive/root:/{destination_path}:/content'
        
        headers = {
            'Content-Type': 'application/octet-stream'
        }
        
        return self._make_request('PUT', endpoint, data=file_content, headers=headers)
    
    def download_file(self, file_path: str, save_to: str) -> str:
        """
        Download file from OneDrive
        
        Args:
            file_path: File path in OneDrive
            save_to: Local path to save file
            
        Returns:
            Local file path where file was saved
        """
        endpoint = f'/me/drive/root:/{file_path}:/content'
        
        response = self._make_request('GET', endpoint, stream=True)
        
        with open(save_to, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Downloaded file to: {save_to}")
        return save_to
    
    def download_file_content(self, file_path: str) -> bytes:
        """
        Download file content from OneDrive
        
        Args:
            file_path: File path in OneDrive
            
        Returns:
            File content as bytes
        """
        endpoint = f'/me/drive/root:/{file_path}:/content'
        
        response = self._make_request('GET', endpoint, stream=True)
        return response.content
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from OneDrive
        
        Args:
            file_path: File path in OneDrive
            
        Returns:
            True if successful
        """
        endpoint = f'/me/drive/root:/{file_path}'
        
        self._make_request('DELETE', endpoint)
        logger.info(f"Deleted file: {file_path}")
        return True
    
    def create_share_link(self, file_path: str, link_type: str = 'view') -> str:
        """
        Create sharing link for OneDrive file
        
        Args:
            file_path: File path in OneDrive
            link_type: 'view' or 'edit'
            
        Returns:
            Sharing URL
        """
        endpoint = f'/me/drive/root:/{file_path}:/createLink'
        
        data = {
            'type': link_type,
            'scope': 'anonymous'
        }
        
        response = self._make_request('POST', endpoint, json=data)
        return response.get('link', {}).get('webUrl', '')
    
    # ==================== OFFICE DOCUMENT CREATION ====================
    
    def create_word_document(self, 
                            file_name: str,
                            content: str,
                            destination_path: str = 'Documents') -> Dict[str, Any]:
        """
        Create Word document in OneDrive
        
        Args:
            file_name: Document name (e.g., 'Invoice.docx')
            content: Document content (plain text or HTML)
            destination_path: Folder path in OneDrive
            
        Returns:
            Created document information
        """
        # Create simple Word document using Office Open XML
        from io import BytesIO
        import zipfile
        
        # Create basic DOCX structure
        docx_buffer = BytesIO()
        with zipfile.ZipFile(docx_buffer, 'w', zipfile.ZIP_DEFLATED) as docx:
            # Add [Content_Types].xml
            content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''
            docx.writestr('[Content_Types].xml', content_types)
            
            # Add _rels/.rels
            rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
            docx.writestr('_rels/.rels', rels)
            
            # Add word/document.xml with content
            document_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <w:p>
            <w:r>
                <w:t>{content}</w:t>
            </w:r>
        </w:p>
    </w:body>
</w:document>'''
            docx.writestr('word/document.xml', document_xml)
        
        # Upload to OneDrive
        file_path = f"{destination_path}/{file_name}"
        return self.upload_file_content(docx_buffer.getvalue(), file_path)
    
    def create_excel_spreadsheet(self,
                                 file_name: str,
                                 data: List[List[Any]],
                                 destination_path: str = 'Documents') -> Dict[str, Any]:
        """
        Create Excel spreadsheet in OneDrive
        
        Args:
            file_name: Spreadsheet name (e.g., 'Report.xlsx')
            data: 2D list of cell values [[row1], [row2], ...]
            destination_path: Folder path in OneDrive
            
        Returns:
            Created spreadsheet information
        """
        try:
            import openpyxl
            from openpyxl import Workbook
            
            # Create workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Sheet1"
            
            # Add data
            for row in data:
                ws.append(row)
            
            # Save to buffer
            buffer = BytesIO()
            wb.save(buffer)
            buffer.seek(0)
            
            # Upload to OneDrive
            file_path = f"{destination_path}/{file_name}"
            return self.upload_file_content(buffer.getvalue(), file_path)
            
        except ImportError:
            logger.error("openpyxl not installed. Install with: pip install openpyxl")
            raise
    
    # ==================== EMAIL OPERATIONS ====================
    
    def get_emails(self,
                   folder: str = 'inbox',
                   top: int = 50,
                   filter_query: Optional[str] = None,
                   search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get emails from mailbox
        
        Args:
            folder: Folder name ('inbox', 'sentitems', 'drafts', etc.)
            top: Number of emails to retrieve (max 999)
            filter_query: OData filter (e.g., "isRead eq false")
            search_query: Search keywords (e.g., "quote request")
            
        Returns:
            List of email messages
        """
        endpoint = f'/me/mailFolders/{folder}/messages'
        
        params = {'$top': top, '$orderby': 'receivedDateTime desc'}
        
        if filter_query:
            params['$filter'] = filter_query
        
        if search_query:
            params['$search'] = f'"{search_query}"'
        
        response = self._make_request('GET', endpoint, params=params)
        return response.get('value', [])
    
    def get_email_by_id(self, message_id: str) -> Dict[str, Any]:
        """
        Get specific email by ID
        
        Args:
            message_id: Email message ID
            
        Returns:
            Email message details
        """
        endpoint = f'/me/messages/{message_id}'
        return self._make_request('GET', endpoint)
    
    def get_unread_emails(self, top: int = 50) -> List[Dict[str, Any]]:
        """
        Get unread emails from inbox
        
        Args:
            top: Number of emails to retrieve
            
        Returns:
            List of unread email messages
        """
        return self.get_emails(
            folder='inbox',
            top=top,
            filter_query='isRead eq false'
        )
    
    def search_emails_for_quotes(self, 
                                 keywords: Optional[List[str]] = None,
                                 top: int = 100) -> List[Dict[str, Any]]:
        """
        Search emails for quote requests
        
        Common keywords: quote, quotation, price, estimate, proposal
        
        Args:
            keywords: List of keywords to search for
            top: Number of results to return
            
        Returns:
            List of emails matching quote request keywords
        """
        if keywords is None:
            keywords = ['quote', 'quotation', 'price quote', 'estimate', 'proposal', 'pricing']
        
        # Search using Microsoft Graph search
        search_query = ' OR '.join(keywords)
        
        return self.get_emails(
            folder='inbox',
            top=top,
            search_query=search_query
        )
    
    def get_email_attachments(self, message_id: str) -> List[Dict[str, Any]]:
        """
        Get attachments from email
        
        Args:
            message_id: Email message ID
            
        Returns:
            List of attachments
        """
        endpoint = f'/me/messages/{message_id}/attachments'
        response = self._make_request('GET', endpoint)
        return response.get('value', [])
    
    def download_email_attachment(self, 
                                  message_id: str,
                                  attachment_id: str,
                                  save_to: str) -> str:
        """
        Download email attachment
        
        Args:
            message_id: Email message ID
            attachment_id: Attachment ID
            save_to: Local path to save attachment
            
        Returns:
            Local file path where attachment was saved
        """
        endpoint = f'/me/messages/{message_id}/attachments/{attachment_id}'
        attachment = self._make_request('GET', endpoint)
        
        # Decode base64 content
        import base64
        content = base64.b64decode(attachment.get('contentBytes', ''))
        
        with open(save_to, 'wb') as f:
            f.write(content)
        
        logger.info(f"Downloaded attachment to: {save_to}")
        return save_to
    
    def mark_email_as_read(self, message_id: str) -> bool:
        """
        Mark email as read
        
        Args:
            message_id: Email message ID
            
        Returns:
            True if successful
        """
        endpoint = f'/me/messages/{message_id}'
        data = {'isRead': True}
        
        self._make_request('PATCH', endpoint, json=data)
        logger.info(f"Marked email {message_id} as read")
        return True
    
    def get_email_by_id_parsed(self, message_id: str, include_attachments: bool = True) -> Dict[str, Any]:
        """
        Get email with AI-OPTIMIZED parsing (clean text, parsed attachments)
        
        This is the Outlook/Microsoft 365 equivalent of Gmail's gmail_get_message_parsed().
        Uses the universal email parser from AI_infrastructure.
        
        Args:
            message_id: Email message ID
            include_attachments: Whether to download and parse attachments
        
        Returns:
            {
                'id': str,
                'thread_id': str (conversationId),
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
                        'parsed_content': str (PDF/Word/Excel as text)
                    }
                ],
                'token_estimate': int
            }
        """
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent / 'AI_infrastructure'))
        from core.email_parser import UniversalEmailParser
        
        # Get message with attachments if requested
        if include_attachments:
            expand = '$expand=attachments'
        else:
            expand = ''
        
        endpoint = f'/me/messages/{message_id}'
        if expand:
            endpoint += f'?{expand}'
        
        raw_message = self._make_request('GET', endpoint)
        
        # Parse using universal parser
        parser = UniversalEmailParser()
        parsed = parser.parse_outlook_message(
            raw_message,
            download_attachments=include_attachments
        )
        
        return parsed
    
    def get_thread_parsed(self, 
                          conversation_id: str,
                          max_messages: int = 20) -> Dict[str, Any]:
        """
        Get email thread/conversation with timeline and parsed content
        
        This is the Outlook equivalent of Gmail's gmail_get_thread_parsed().
        
        Args:
            conversation_id: Conversation ID (thread ID)
            max_messages: Max messages to fetch
        
        Returns:
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
                        'full_message_id': str
                    }
                ],
                'token_estimate': int
            }
        """
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent / 'AI_infrastructure'))
        from core.email_parser import UniversalEmailParser
        
        # Get all messages in conversation
        endpoint = f'/me/messages?$filter=conversationId eq \'{conversation_id}\'&$top={max_messages}&$orderby=receivedDateTime asc'
        response = self._make_request('GET', endpoint)
        messages = response.get('value', [])
        
        # Parse each message
        parser = UniversalEmailParser()
        parsed_messages = [
            parser.parse_outlook_message(msg, download_attachments=False)
            for msg in messages
        ]
        
        # Build timeline
        timeline = parser.parse_email_thread_timeline(parsed_messages)
        
        return timeline
    
    def move_email_to_folder(self, message_id: str, folder_name: str) -> Dict[str, Any]:
        """
        Move email to different folder
        
        Args:
            message_id: Email message ID
            folder_name: Destination folder name ('archive', 'junk', etc.)
            
        Returns:
            Updated message information
        """
        # Get folder ID
        folders_response = self._make_request('GET', '/me/mailFolders')
        folders = folders_response.get('value', [])
        
        folder_id = None
        for folder in folders:
            if folder['displayName'].lower() == folder_name.lower():
                folder_id = folder['id']
                break
        
        if not folder_id:
            raise ValueError(f"Folder '{folder_name}' not found")
        
        endpoint = f'/me/messages/{message_id}/move'
        data = {'destinationId': folder_id}
        
        return self._make_request('POST', endpoint, json=data)
    
    def reply_to_email(self,
                      message_id: str,
                      reply_body: str,
                      body_type: str = 'HTML') -> bool:
        """
        Reply to email
        
        Args:
            message_id: Email message ID to reply to
            reply_body: Reply message body
            body_type: 'HTML' or 'Text'
            
        Returns:
            True if sent successfully
        """
        endpoint = f'/me/messages/{message_id}/reply'
        
        data = {
            'message': {
                'body': {
                    'contentType': body_type,
                    'content': reply_body
                }
            }
        }
        
        self._make_request('POST', endpoint, json=data)
        logger.info(f"Replied to email {message_id}")
        return True
    
    def send_email(self,
                  to_addresses: List[str],
                  subject: str,
                  body: str,
                  body_type: str = 'HTML',
                  cc_addresses: Optional[List[str]] = None,
                  attachments: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Send email via Microsoft Graph
        
        Args:
            to_addresses: List of recipient email addresses
            subject: Email subject
            body: Email body (HTML or Text)
            body_type: 'HTML' or 'Text'
            cc_addresses: Optional CC recipients
            attachments: Optional list of attachments
            
        Returns:
            True if sent successfully
        """
        to_recipients = [{'emailAddress': {'address': addr}} for addr in to_addresses]
        
        message = {
            'subject': subject,
            'body': {
                'contentType': body_type,
                'content': body
            },
            'toRecipients': to_recipients
        }
        
        if cc_addresses:
            message['ccRecipients'] = [{'emailAddress': {'address': addr}} for addr in cc_addresses]
        
        if attachments:
            message['attachments'] = attachments
        
        data = {'message': message}
        
        self._make_request('POST', '/me/sendMail', json=data)
        logger.info(f"Email sent to: {', '.join(to_addresses)}")
        return True
    
    # ==================== CALENDAR OPERATIONS ====================
    
    def get_calendar_events(self,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get calendar events
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of calendar events
        """
        endpoint = '/me/calendar/events'
        
        params = {}
        if start_date and end_date:
            params['$filter'] = f"start/dateTime ge '{start_date.isoformat()}' and end/dateTime le '{end_date.isoformat()}'"
        
        response = self._make_request('GET', endpoint, params=params)
        return response.get('value', [])
    
    def create_calendar_event(self,
                             subject: str,
                             start_time: datetime,
                             end_time: datetime,
                             location: Optional[str] = None,
                             body: Optional[str] = None,
                             attendees: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create calendar event
        
        Args:
            subject: Event title
            start_time: Event start datetime
            end_time: Event end datetime
            location: Optional location
            body: Optional event description
            attendees: Optional list of attendee emails
            
        Returns:
            Created event information
        """
        event_data = {
            'subject': subject,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Australia/Sydney'
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Australia/Sydney'
            }
        }
        
        if location:
            event_data['location'] = {'displayName': location}
        
        if body:
            event_data['body'] = {'contentType': 'HTML', 'content': body}
        
        if attendees:
            event_data['attendees'] = [
                {
                    'emailAddress': {'address': email},
                    'type': 'required'
                }
                for email in attendees
            ]
        
        return self._make_request('POST', '/me/calendar/events', json=event_data)


if __name__ == "__main__":
    """
    Example usage and testing
    """
    print("Microsoft 365 Client Module Loaded")
    print("=" * 60)
    
    # Initialize client
    try:
        client = Microsoft365Client()
        print(f"✓ Initialized Microsoft 365 client")
        print(f"  Tenant ID: {client.tenant_id}")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        print("\nSet environment variables:")
        print("  M365_CLIENT_ID=your_client_id")
        print("  M365_CLIENT_SECRET=your_client_secret")
    
    print("\n" + "=" * 60)
    print("Available features:")
    print("  ✓ OneDrive file management")
    print("  ✓ Office document creation (Word, Excel)")
    print("  ✓ Email sending via Graph API")
    print("  ✓ Calendar management")
    print("  ✓ User profile access")
    print("=" * 60)
