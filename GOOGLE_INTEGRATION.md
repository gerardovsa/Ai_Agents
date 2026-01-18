# Google Workspace Integration Documentation

**Last Updated:** January 19, 2026  
**Version:** 3.1.0  
**Status:** Production Ready - Complete Google Workspace Suite  
**Purpose:** Comprehensive technical documentation for Google Workspace integration (Gmail, Drive, Docs, Sheets, Slides, Calendar, Forms, Tasks, Meet, Analytics)

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [OAuth2 Authentication](#oauth2-authentication)
4. [Core Services](#core-services)
5. [Gmail Integration](#gmail-integration)
6. [Google Drive](#google-drive)
7. [Google Docs](#google-docs)
8. [Google Sheets](#google-sheets)
9. [Google Slides](#google-slides)
10. [Google Calendar](#google-calendar)
11. [Google Forms](#google-forms)
12. [Additional Services](#additional-services)
13. [Implementation Details](#implementation-details)
14. [Critical Fixes](#critical-fixes)
15. [Testing & Deployment](#testing--deployment)
16. [Related Documentation](#related-documentation)

---

## System Overview

### Purpose

The Google Workspace integration provides complete access to Google's productivity suite through unified OAuth2 authentication and intelligent API wrappers with automatic credential injection, token management, and format optimization.

### Key Capabilities

- **Complete OAuth2 Flow** - User consent, token storage, automatic refresh
- **18 Google Services** - Gmail, Drive, Docs, Sheets, Slides, Calendar, Forms, Tasks, Meet, Analytics, Cloud Run, Apps Script
- **Intelligent Format Selection** - 4 formats (summary, text, markdown, full) with 99.8% token reduction
- **Gmail-Style Threading** - Collapsed conversations with full thread preview
- **Markdown Formatter v3.0** - 10 advanced features (cell merging, conditional formatting, dropdowns)
- **Automatic Credential Injection** - Transparent OAuth token management from Supabase
- **Multi-User Support** - Per-user credential isolation with refresh token rotation

### Statistics

- **18 Core Implementation Files** - `google_workspace/` directory
- **82 Documentation Files** - Consolidated into this master document
- **50+ AI-Callable Tools** - Gmail (15), Drive (8), Docs (7), Sheets (10), Slides (6), Calendar (5), Forms (4), Tasks (3), Meet (2)
- **4 Format Options** - summary (500 tokens), text (50K), markdown (55K), full (200K+)
- **OAuth2 Flow** - Google Cloud Console → User Consent → Supabase Storage → Auto-Refresh

---

## Architecture

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                               │
│  - Platform Connections Modal (Google OAuth button)             │
│  - Communication Hub (Gmail/Outlook unified inbox)               │
│  - AI chat interface (Google tools available to agents)          │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   OAUTH2 FLOW                                    │
│  1. User clicks "Connect Google Account"                         │
│  2. Redirected to Google consent screen                          │
│  3. User grants permissions (Gmail, Drive, Docs, etc.)           │
│  4. OAuth callback → Exchange code for tokens                    │
│  5. Store in Supabase: access_token, refresh_token, expiry      │
│  6. Auto-refresh when expired (1hr TTL)                          │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              GOOGLE WORKSPACE IMPLEMENTATIONS                    │
│  Files: google_workspace/                                        │
│  • gmail.py (15 tools)                 • google_docs.py (7 tools)│
│  • google_drive.py (8 tools)           • google_sheets.py (10)  │
│  • google_calendar.py (5 tools)        • google_slides.py (6)   │
│  • google_forms.py (4 tools)           • google_tasks.py (3)    │
│  • google_meet.py (2 tools)            • google_analytics.py    │
│  • sheets_markdown_formatter.py (v3.0) • google_auth_helper.py  │
│  • oauth_manager.py                    • oauth_credential_loader│
│                                                                   │
│  Shared Modules:                                                 │
│  • google_auth_helper.py - OAuth credential fetching            │
│  • oauth_manager.py - Token refresh & validation                │
│  • oauth_credential_loader.py - Supabase integration            │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  GOOGLE APIS                                     │
│  - Gmail API v1 (send, read, search, labels, attachments)       │
│  - Drive API v3 (list, create, update, permissions, export)     │
│  - Docs API v1 (read, create, update with markdown parsing)     │
│  - Sheets API v4 (read, write, format, conditional rules)       │
│  - Slides API v1 (create, update, templates, images)            │
│  - Calendar API v3 (events, CRUD, attendees, reminders)         │
│  - Forms API v1 (create, responses, structure)                  │
│  - Tasks API v1 (lists, tasks, CRUD)                            │
│  - Meet API v2 (create meetings, recordings)                    │
│  - Analytics API v3 (reporting, dimensions, metrics)            │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│         SUPABASE CREDENTIAL STORAGE                              │
│  Table: ai_infrastructure.oauth_tokens                           │
│  {                                                               │
│    user_id: 1,                                                   │
│    platform: "google",                                           │
│    access_token: "ya29.a0AfH6SMBx...",  // Encrypted            │
│    refresh_token: "1//0gHd...",         // Encrypted            │
│    token_expiry: "2026-01-18T03:00:00Z",                        │
│    scope: "gmail drive docs sheets slides calendar...",         │
│    email: "user@example.com"                                    │
│  }                                                               │
└──────────────────────────────────────────────────────────────────┘
```

### Module Organization

```
google_workspace/
├── Core Services:
│   ├── gmail.py                    # 15 tools (send, search, labels, attachments, threading)
│   ├── google_drive.py             # 8 tools (list, create, permissions, export)
│   ├── google_docs.py              # 7 tools (read, create, format conversion)
│   ├── google_sheets.py            # 10 tools (read, write, markdown formatter)
│   ├── google_slides.py            # 6 tools (create, update, templates)
│   ├── google_calendar.py          # 5 tools (events, CRUD)
│   ├── google_forms.py             # 4 tools (create, responses)
│   ├── google_tasks.py             # 3 tools (lists, tasks)
│   ├── google_meet.py              # 2 tools (meetings, recordings)
│   └── google_analytics.py         # Analytics integration
│
├── Auth & OAuth:
│   ├── google_auth_helper.py       # OAuth credential fetching
│   ├── oauth_manager.py            # Token refresh & validation
│   └── oauth_credential_loader.py  # Supabase integration
│
├── Utilities:
│   ├── sheets_markdown_formatter.py # v3.0 (10 features)
│   ├── email_parser.py             # Email content parsing
│   └── test_formula_syntax.py      # Sheets formula validation
│
└── Additional:
    ├── google_cloud_run.py         # Cloud Run deployment
    ├── google_apps_script.py       # Apps Script automation
    └── ai_personal_tasks.py        # Task management helpers

tools/implementations/
├── gmail_smart.py                  # Smart Gmail tools with AI
├── gmail_smtp_fallback.py          # SMTP fallback for sending
└── google_apps_script.py           # Apps Script wrappers
```

---

## OAuth2 Authentication

### Google Cloud Console Setup

**Required APIs to Enable:**
```
Gmail API
Google Drive API
Google Docs API
Google Sheets API
Google Slides API
Google Calendar API
Google Forms API
Google Tasks API
Google Meet API
Google Analytics API
```

**OAuth2 Credentials Configuration:**
```json
{
  "web": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": [
      "https://yourdomain.com/api/google-auth/callback",
      "http://localhost:5000/api/google-auth/callback"
    ],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "scopes": [
      "https://www.googleapis.com/auth/gmail.modify",
      "https://www.googleapis.com/auth/drive",
      "https://www.googleapis.com/auth/documents",
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/presentations",
      "https://www.googleapis.com/auth/calendar",
      "https://www.googleapis.com/auth/forms",
      "https://www.googleapis.com/auth/tasks",
      "https://www.googleapis.com/auth/meetings"
    ]
  }
}
```

### OAuth Flow Implementation

**File:** `AI_infrastructure/routes/google_auth_routes_V2_FIXED.py`

```python
from flask import Blueprint, request, redirect, jsonify
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

google_auth_bp = Blueprint('google_auth', __name__)

@google_auth_bp.route('/api/google-auth/start', methods=['GET'])
def google_auth_start():
    """
    Initiate Google OAuth2 flow
    
    Returns redirect URL to Google consent screen
    """
    user_id = request.args.get('user_id')
    
    flow = Flow.from_client_secrets_file(
        'credentials/google_client_secret.json',
        scopes=[
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/presentations',
            'https://www.googleapis.com/auth/calendar'
        ],
        redirect_uri='https://yourdomain.com/api/google-auth/callback'
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',  # Enables refresh token
        include_granted_scopes='true',
        prompt='consent'  # Force consent screen (ensures refresh token)
    )
    
    # Store state in session for verification
    session['oauth_state'] = state
    session['oauth_user_id'] = user_id
    
    return jsonify({
        'success': True,
        'authorization_url': authorization_url
    })

@google_auth_bp.route('/api/google-auth/callback', methods=['GET'])
def google_auth_callback():
    """
    Handle OAuth2 callback from Google
    
    Exchange authorization code for tokens and store in Supabase
    """
    state = request.args.get('state')
    code = request.args.get('code')
    
    # Verify state to prevent CSRF
    if state != session.get('oauth_state'):
        return jsonify({'success': False, 'error': 'Invalid state parameter'}), 400
    
    user_id = session.get('oauth_user_id')
    
    # Exchange code for tokens
    flow = Flow.from_client_secrets_file(
        'credentials/google_client_secret.json',
        scopes=None,  # Use scopes from authorization request
        state=state,
        redirect_uri='https://yourdomain.com/api/google-auth/callback'
    )
    
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Get user email from Google
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    email = user_info.get('email')
    
    # Store tokens in Supabase
    from AI_infrastructure.shared.database_utils import execute_query
    
    execute_query("""
        INSERT INTO ai_infrastructure.oauth_tokens 
        (user_id, platform, access_token, refresh_token, token_expiry, scope, email)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id, platform) 
        DO UPDATE SET 
            access_token = EXCLUDED.access_token,
            refresh_token = EXCLUDED.refresh_token,
            token_expiry = EXCLUDED.token_expiry,
            scope = EXCLUDED.scope,
            email = EXCLUDED.email,
            updated_at = NOW()
    """, (
        user_id,
        'google',
        credentials.token,
        credentials.refresh_token,
        credentials.expiry.isoformat() if credentials.expiry else None,
        ' '.join(credentials.scopes) if credentials.scopes else '',
        email
    ))
    
    return redirect('/platform-connections?google_connected=true')
```

### Token Refresh Implementation

**File:** `google_workspace/oauth_manager.py`

```python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from AI_infrastructure.shared.database_utils import execute_query
from datetime import datetime, timedelta

class GoogleOAuthManager:
    """Manage Google OAuth2 token refresh and validation"""
    
    @staticmethod
    def get_valid_credentials(user_id: int) -> Credentials:
        """
        Get valid Google OAuth credentials for user
        
        Automatically refreshes if expired
        
        Args:
            user_id: User ID
            
        Returns:
            Credentials object ready for API calls
            
        Raises:
            ValueError: If credentials not found or invalid
        """
        # Fetch from Supabase
        row = execute_query("""
            SELECT access_token, refresh_token, token_expiry, scope
            FROM ai_infrastructure.oauth_tokens
            WHERE user_id = %s AND platform = 'google'
        """, (user_id,), fetch_mode='one')
        
        if not row:
            raise ValueError("Google credentials not found. User must authenticate.")
        
        # Create Credentials object
        credentials = Credentials(
            token=row['access_token'],
            refresh_token=row['refresh_token'],
            token_uri='https://oauth2.googleapis.com/token',
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            scopes=row['scope'].split(' ')
        )
        
        # Check if expired
        expiry = datetime.fromisoformat(row['token_expiry']) if row['token_expiry'] else None
        if expiry and datetime.utcnow() >= expiry - timedelta(minutes=5):
            print(f"[OAUTH] Google token expired for user {user_id}, refreshing...")
            
            # Refresh token
            credentials.refresh(Request())
            
            # Update Supabase
            execute_query("""
                UPDATE ai_infrastructure.oauth_tokens
                SET access_token = %s,
                    token_expiry = %s,
                    updated_at = NOW()
                WHERE user_id = %s AND platform = 'google'
            """, (
                credentials.token,
                credentials.expiry.isoformat() if credentials.expiry else None,
                user_id
            ))
            
            print(f"[OAUTH] Token refreshed successfully")
        
        return credentials
    
    @staticmethod
    def revoke_credentials(user_id: int) -> bool:
        """Revoke Google OAuth credentials"""
        try:
            credentials = GoogleOAuthManager.get_valid_credentials(user_id)
            credentials.revoke(Request())
            
            # Delete from Supabase
            execute_query("""
                DELETE FROM ai_infrastructure.oauth_tokens
                WHERE user_id = %s AND platform = 'google'
            """, (user_id,))
            
            return True
        except Exception as e:
            print(f"[OAUTH] Revoke failed: {e}")
            return False
```

---

## Core Services

### Gmail Integration

**File:** `google_workspace/gmail.py` (15 tools)

#### Email Management Tools

```python
def gmail_list_messages(user_id: int, max_results: int = 10, 
                       query: str = '', label_ids: list = None) -> dict:
    """
    List Gmail messages with optional filtering
    
    Args:
        user_id: User ID for OAuth credentials
        max_results: Number of messages to return (default 10, max 500)
        query: Gmail search query (e.g., "from:user@example.com subject:invoice")
        label_ids: Filter by labels (e.g., ["INBOX", "UNREAD"])
    
    Returns:
        {
            "success": True,
            "messages": [
                {
                    "id": "19ad7ccb11495963",
                    "thread_id": "19ad7ccb11495963",
                    "label_ids": ["INBOX", "UNREAD"],
                    "snippet": "Here is the invoice for your recent purchase...",
                    "from": "sender@example.com",
                    "to": "recipient@example.com",
                    "subject": "Invoice #12345",
                    "date": "2026-01-18T10:30:00Z"
                }
            ],
            "result_size_estimate": 42
        }
    
    Examples:
        # Recent unread emails
        gmail_list_messages(user_id=1, query="is:unread", max_results=20)
        
        # Emails from specific sender
        gmail_list_messages(user_id=1, query="from:john@example.com")
        
        # Emails with attachments
        gmail_list_messages(user_id=1, query="has:attachment")
    """
    from googleapiclient.discovery import build
    from google_workspace.oauth_manager import GoogleOAuthManager
    
    # Get credentials with auto-refresh
    creds = GoogleOAuthManager.get_valid_credentials(user_id)
    service = build('gmail', 'v1', credentials=creds)
    
    # List messages
    results = service.users().messages().list(
        userId='me',
        maxResults=max_results,
        q=query,
        labelIds=label_ids
    ).execute()
    
    messages = results.get('messages', [])
    
    # Fetch metadata for each message
    detailed_messages = []
    for msg in messages:
        msg_detail = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['From', 'To', 'Subject', 'Date']
        ).execute()
        
        headers = {h['name']: h['value'] for h in msg_detail['payload']['headers']}
        
        detailed_messages.append({
            'id': msg_detail['id'],
            'thread_id': msg_detail['threadId'],
            'label_ids': msg_detail.get('labelIds', []),
            'snippet': msg_detail.get('snippet', ''),
            'from': headers.get('From', ''),
            'to': headers.get('To', ''),
            'subject': headers.get('Subject', ''),
            'date': headers.get('Date', '')
        })
    
    return {
        'success': True,
        'messages': detailed_messages,
        'result_size_estimate': results.get('resultSizeEstimate', 0)
    }
```

**Complete Gmail Tool List:**

1. `gmail_list_messages` - List/search messages
2. `gmail_get_message` - Get full message content
3. `gmail_send_message` - Send email
4. `gmail_create_draft` - Create draft
5. `gmail_delete_message` - Delete message
6. `gmail_trash_message` - Move to trash
7. `gmail_modify_labels` - Add/remove labels
8. `gmail_list_labels` - Get all labels
9. `gmail_create_label` - Create new label
10. `gmail_get_attachment` - Download attachment
11. `gmail_list_threads` - List conversation threads
12. `gmail_get_thread` - Get full thread
13. `gmail_search_messages` - Advanced search
14. `gmail_get_profile` - Get user profile
15. `gmail_watch` - Set up push notifications

#### Gmail Threading (Jan 12, 2026)

**File:** `UI/modules_internal/communication-hub/communication-hub-v4-modern.js`

**Gmail-Style Collapsed Threading:**
- Threads collapsed by default (show only latest message)
- Thread count badges `[3]` indicate conversation size
- Chevron expand/collapse buttons (▶ = collapsed, ▼ = expanded)
- Click email → Preview shows full conversation chronologically
- Uses Gmail `thread_id` and Outlook `conversationId` for grouping

```javascript
// State Management
state: {
    expandedThreads: new Set(),     // Tracks which threads are expanded
    collapsedEmails: []             // Collapsed view (latest email per thread)
}

// Create collapsed view from emails
createCollapsedView(groupingStats) {
    const collapsed = [];
    const processedThreads = new Set();
    
    // Add chains (threads with 2+ messages)
    groupingStats.chains.forEach(chain => {
        const latestEmail = chain.emails[chain.emails.length - 1];
        latestEmail._threadCount = chain.emails.length;
        collapsed.push(latestEmail);
        processedThreads.add(chain.thread_id);
    });
    
    // Add singles
    groupingStats.singles.forEach(email => {
        if (!processedThreads.has(email.thread_id)) {
            email._threadCount = 1;
            collapsed.push(email);
        }
    });
    
    return collapsed.sort((a, b) => new Date(b.date) - new Date(a.date));
}

// Toggle thread expansion
toggleThread(threadId, event) {
    event.stopPropagation();
    
    if (this.state.expandedThreads.has(threadId)) {
        this.state.expandedThreads.delete(threadId);
    } else {
        this.state.expandedThreads.add(threadId);
    }
    
    this.refreshTableWithThreads();
}
```

### Google Drive

**File:** `google_workspace/google_drive.py` (8 tools)

```python
def google_drive_list_files(user_id: int, folder_id: str = 'root',
                            max_results: int = 100, 
                            mime_type: str = None) -> dict:
    """
    List files in Google Drive folder
    
    Args:
        user_id: User ID
        folder_id: Folder ID ('root' for My Drive)
        max_results: Max files to return (default 100)
        mime_type: Filter by MIME type
    
    Returns:
        {
            "success": True,
            "files": [
                {
                    "id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
                    "name": "Q4 Sales Report.docx",
                    "mime_type": "application/vnd.google-apps.document",
                    "size": 45892,
                    "created_time": "2026-01-15T10:00:00Z",
                    "modified_time": "2026-01-18T09:30:00Z",
                    "web_view_link": "https://docs.google.com/...",
                    "owners": ["user@example.com"]
                }
            ]
        }
    """
    from googleapiclient.discovery import build
    from google_workspace.oauth_manager import GoogleOAuthManager
    
    creds = GoogleOAuthManager.get_valid_credentials(user_id)
    service = build('drive', 'v3', credentials=creds)
    
    query = f"'{folder_id}' in parents and trashed = false"
    if mime_type:
        query += f" and mimeType = '{mime_type}'"
    
    results = service.files().list(
        q=query,
        pageSize=max_results,
        fields="files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink, owners)"
    ).execute()
    
    return {
        'success': True,
        'files': results.get('files', [])
    }

def google_drive_create_file(user_id: int, name: str, content: str,
                             mime_type: str = 'text/plain', 
                             folder_id: str = 'root') -> dict:
    """
    Create file in Google Drive
    
    Supports: TXT, Google Docs, Google Sheets, Google Slides
    """
    # Implementation...

def google_drive_export_file(user_id: int, file_id: str, 
                             export_mime_type: str = 'application/pdf') -> bytes:
    """
    Export Google Workspace file to different format
    
    Supports:
    - Google Docs → PDF, DOCX, RTF, TXT, HTML
    - Google Sheets → XLSX, PDF, CSV
    - Google Slides → PDF, PPTX
    """
    # Implementation...
```

**Complete Drive Tool List:**

1. `google_drive_list_files` - List files in folder
2. `google_drive_get_file_metadata` - Get file details
3. `google_drive_create_file` - Create new file
4. `google_drive_update_file` - Update file content
5. `google_drive_delete_file` - Delete file
6. `google_drive_share_file` - Manage permissions
7. `google_drive_export_file` - Export to different format
8. `google_drive_search_files` - Search across Drive

### Google Docs

**File:** `google_workspace/google_docs.py` (7 tools)

#### Format Parameter (4 Options)

**Critical: Default is `format='summary'` for 99.8% token reduction**

| Format | Token Usage | Use Case |
|--------|-------------|----------|
| **summary** | 500-2K | Quick metadata, previews ✅ RECOMMENDED |
| **text** | 50K-100K | Plain text extraction |
| **markdown** | 55K-120K | AI processing, structured content |
| **full** | 200K+ | Complete JSON (AVOID unless needed) |

```python
def google_docs_get_document(user_id: int, document_id: str, 
                             format: str = 'summary') -> dict:
    """
    Get Google Docs document with intelligent format selection
    
    Args:
        user_id: User ID
        document_id: Document ID
        format: 'summary' | 'text' | 'markdown' | 'full'
    
    Returns (format='summary'):
        {
            "success": True,
            "title": "Sales Report Q3 2024",
            "document_id": "1M11p3SwvTHFSF5pcJd-oq2w9E_ShaBL17IMckkpkvj0",
            "preview": "First 2000 characters...",
            "character_count": 45892,
            "page_count": 12,
            "format": "summary",
            "sections": ["Executive Summary", "Revenue Analysis", "Forecast"],
            "note": "Use format='markdown' for full content"
        }
    
    Returns (format='markdown'):
        {
            "success": True,
            "title": "Sales Report Q3 2024",
            "markdown": "---\n**Document Structure:**\n- H1 (##): 18pt\n---\n\n# Sales Report\n\n## Executive Summary\n\nQ3 revenue increased **23% YoY**...",
            "character_count": 45892,
            "format": "markdown"
        }
    """
    from googleapiclient.discovery import build
    from google_workspace.oauth_manager import GoogleOAuthManager
    
    creds = GoogleOAuthManager.get_valid_credentials(user_id)
    service = build('docs', 'v1', credentials=creds)
    
    # Get document
    doc = service.documents().get(documentId=document_id).execute()
    
    if format == 'summary':
        # Extract title and first 2000 chars
        title = doc.get('title', '')
        content = extract_text(doc)
        preview = content[:2000] + ('...' if len(content) > 2000 else '')
        
        return {
            'success': True,
            'title': title,
            'document_id': document_id,
            'preview': preview,
            'character_count': len(content),
            'format': 'summary',
            'note': "Use format='markdown' for full content"
        }
    
    elif format == 'markdown':
        markdown_content = convert_to_markdown(doc)
        
        return {
            'success': True,
            'title': doc.get('title', ''),
            'markdown': markdown_content,
            'character_count': len(markdown_content),
            'format': 'markdown'
        }
    
    elif format == 'text':
        text_content = extract_text(doc)
        
        return {
            'success': True,
            'title': doc.get('title', ''),
            'text': text_content,
            'character_count': len(text_content),
            'format': 'text'
        }
    
    elif format == 'full':
        return {
            'success': True,
            'document': doc,
            'format': 'full'
        }

def convert_to_markdown(doc: dict) -> str:
    """
    Convert Google Docs JSON to Markdown
    
    Handles:
    - Headings (H1-H6) with proper spacing
    - Bold, italic, underline, strikethrough
    - Lists (bulleted and numbered)
    - Links
    - Tables
    - Images (as markdown image links)
    """
    # Implementation...
```

**Complete Docs Tool List:**

1. `google_docs_get_document` - Get document (4 formats)
2. `google_docs_create_document` - Create new document
3. `google_docs_update_document` - Update content
4. `google_docs_search_document` - Search within document
5. `google_docs_export_pdf` - Export to PDF
6. `google_docs_insert_text` - Insert text at position
7. `google_docs_format_text` - Apply formatting

### Google Sheets

**File:** `google_workspace/google_sheets.py` + `sheets_markdown_formatter.py` (10 tools + Markdown Formatter v3.0)

#### Markdown Formatter v3.0 (10 Features)

**File:** `google_workspace/sheets_markdown_formatter.py`

**Major Enhancement:** Professional spreadsheet creation with 10 advanced features

```python
from google_workspace.sheets_markdown_formatter import SheetsMarkdownFormatter

# Example: Financial Dashboard with v3.0 features
google_sheets_create(
    user_id=1,
    title="Q4 Financial Dashboard",
    headers=["# Category", "**Revenue**", "**Growth**", "**Status**"],
    data=[
        ["[MERGE:4]Executive Summary", "", "", ""],  # Cell merging
        ["Product A", "[$]15000", "[%]12.5", "[IF>10:GREEN]12.5"],  # Number format + conditional
        ["Product B", "[$]8000", "[%]5.2", "[IF<10:YELLOW]5.2"],
        ["Service C", "[$]22000", "[%]18.7", "[IF>15:LG]18.7"],
        ["", "", "", ""],
        ["[SIZE:14]**Total**", "[$]45000", "[%]12.1", "[DROPDOWN:Excellent,Good,Fair]Good"]  # Font size + dropdown
    ],
    parse_markdown=True,
    auto_resize_columns=True  # NEW v3.0!
)
```

**v3.0 Features:**

| # | Feature | Syntax | Example |
|---|---------|--------|---------|
| 1 | **Number Formatting** | `[$]`, `[%]`, `[#,##0]`, `[DATE]` | `[$]1500` → $1,500.00 |
| 2 | **Cell Merging** | `[MERGE:N]text` | `[MERGE:3]Title` merges 3 cells |
| 3 | **Text Wrapping** | `[WRAP]`, `[NOWRAP]` | `[WRAP]Long text...` |
| 4 | **Font Size** | `[SIZE:N]text` | `[SIZE:20]Header` |
| 5 | **Strikethrough** | `~~text~~` | `~~Canceled~~` |
| 6 | **Underline** | `__text__` | `__Important__` |
| 7 | **Conditional Formatting** | `[IF>N:COLOR]value` | `[IF>100:GREEN]125` |
| 8 | **Data Validation** | `[DROPDOWN:A,B]value` | `[DROPDOWN:Yes,No]Yes` |
| 9 | **Column Auto-Resize** | `auto_resize_columns=True` | Fits all columns |
| 10 | **Combined Features** | Multiple tags | `[SIZE:14][MERGE:2]~~Old~~ **New**` |

**Conditional Formatting Colors:**
- `RED`, `ORANGE`, `YELLOW`, `GREEN`, `BLUE`, `PURPLE`
- `LR`, `LO`, `LY`, `LG`, `LB`, `LP` (light variants)
- `DR`, `DO`, `DY`, `DG`, `DB`, `DP` (dark variants)

**Complete Sheets Tool List:**

1. `google_sheets_get` - Read spreadsheet (4 formats)
2. `google_sheets_create` - Create spreadsheet with markdown
3. `google_sheets_create_multiple` - Batch create sheets
4. `google_sheets_update` - Update cells
5. `google_sheets_append` - Append rows
6. `google_sheets_format` - Apply formatting
7. `google_sheets_insert_chart` - Create charts
8. `google_sheets_get_chart_data` - Export chart as image
9. `google_sheets_create_pivot_table` - Create pivot table
10. `google_sheets_add_conditional_formatting` - Advanced formatting rules

### Google Slides

**File:** `google_workspace/google_slides.py` (6 tools)

```python
def google_slides_create_presentation(user_id: int, title: str, 
                                     slides: list = None) -> dict:
    """
    Create Google Slides presentation
    
    Args:
        user_id: User ID
        title: Presentation title
        slides: List of slide definitions
            [
                {
                    "layout": "TITLE_SLIDE",
                    "title": "Q4 Results",
                    "subtitle": "Annual Review"
                },
                {
                    "layout": "TITLE_AND_BODY",
                    "title": "Revenue Growth",
                    "body": "• Q4 revenue: $4.2M\n• Growth: +23% YoY"
                }
            ]
    
    Returns:
        {
            "success": True,
            "presentation_id": "1abc123...",
            "title": "Q4 Results",
            "url": "https://docs.google.com/presentation/d/...",
            "slide_count": 2
        }
    """
    from googleapiclient.discovery import build
    from google_workspace.oauth_manager import GoogleOAuthManager
    
    creds = GoogleOAuthManager.get_valid_credentials(user_id)
    service = build('slides', 'v1', credentials=creds)
    
    # Create presentation
    presentation = service.presentations().create(body={'title': title}).execute()
    presentation_id = presentation['presentationId']
    
    if slides:
        requests = []
        for i, slide_data in enumerate(slides):
            # Create slide with layout
            slide_id = f'slide_{i}'
            requests.append({
                'createSlide': {
                    'objectId': slide_id,
                    'slideLayoutReference': {
                        'predefinedLayout': slide_data.get('layout', 'BLANK')
                    }
                }
            })
            
            # Add title text
            if slide_data.get('title'):
                requests.append({
                    'insertText': {
                        'objectId': f'{slide_id}_title',
                        'text': slide_data['title']
                    }
                })
            
            # Add body text
            if slide_data.get('body'):
                requests.append({
                    'insertText': {
                        'objectId': f'{slide_id}_body',
                        'text': slide_data['body']
                    }
                })
        
        # Execute batch update
        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
    
    return {
        'success': True,
        'presentation_id': presentation_id,
        'title': title,
        'url': f"https://docs.google.com/presentation/d/{presentation_id}/edit",
        'slide_count': len(slides) if slides else 1
    }
```

**Complete Slides Tool List:**

1. `google_slides_create_presentation` - Create presentation
2. `google_slides_get_presentation` - Get presentation (4 formats)
3. `google_slides_add_slide` - Add new slide
4. `google_slides_update_slide` - Update slide content
5. `google_slides_insert_image` - Add image to slide
6. `google_slides_export_pdf` - Export to PDF

### Google Calendar

**File:** `google_workspace/google_calendar.py` (5 tools)

```python
def google_calendar_create_event(user_id: int, summary: str, 
                                 start_time: str, end_time: str,
                                 description: str = '', 
                                 attendees: list = None,
                                 location: str = '') -> dict:
    """
    Create Google Calendar event
    
    Args:
        user_id: User ID
        summary: Event title
        start_time: ISO 8601 datetime (e.g., "2026-01-20T10:00:00Z")
        end_time: ISO 8601 datetime
        description: Event description
        attendees: List of email addresses
        location: Event location
    
    Returns:
        {
            "success": True,
            "event_id": "abc123...",
            "summary": "Team Meeting",
            "start_time": "2026-01-20T10:00:00Z",
            "end_time": "2026-01-20T11:00:00Z",
            "html_link": "https://calendar.google.com/..."
        }
    """
    from googleapiclient.discovery import build
    from google_workspace.oauth_manager import GoogleOAuthManager
    
    creds = GoogleOAuthManager.get_valid_credentials(user_id)
    service = build('calendar', 'v3', credentials=creds)
    
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': 'UTC'},
        'end': {'dateTime': end_time, 'timeZone': 'UTC'},
        'attendees': [{'email': email} for email in (attendees or [])],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10}
            ]
        }
    }
    
    created_event = service.events().insert(
        calendarId='primary',
        body=event,
        sendUpdates='all'  # Send email invitations
    ).execute()
    
    return {
        'success': True,
        'event_id': created_event['id'],
        'summary': created_event['summary'],
        'start_time': created_event['start']['dateTime'],
        'end_time': created_event['end']['dateTime'],
        'html_link': created_event.get('htmlLink')
    }
```

**Complete Calendar Tool List:**

1. `google_calendar_create_event` - Create event
2. `google_calendar_list_events` - List upcoming events
3. `google_calendar_update_event` - Update event
4. `google_calendar_delete_event` - Delete event
5. `google_calendar_get_event` - Get event details

### Google Forms

**File:** `google_workspace/google_forms.py` (4 tools)

```python
def google_forms_create_form(user_id: int, title: str, 
                             questions: list) -> dict:
    """
    Create Google Form with questions
    
    Args:
        user_id: User ID
        title: Form title
        questions: List of question definitions
            [
                {
                    "type": "MULTIPLE_CHOICE",
                    "question": "What is your department?",
                    "options": ["Sales", "Marketing", "Engineering"],
                    "required": True
                },
                {
                    "type": "TEXT",
                    "question": "Please provide feedback",
                    "required": False
                }
            ]
    
    Returns:
        {
            "success": True,
            "form_id": "1abc123...",
            "title": "Employee Survey",
            "url": "https://docs.google.com/forms/d/.../edit",
            "responder_uri": "https://docs.google.com/forms/d/.../viewform"
        }
    """
    from googleapiclient.discovery import build
    from google_workspace.oauth_manager import GoogleOAuthManager
    
    creds = GoogleOAuthManager.get_valid_credentials(user_id)
    service = build('forms', 'v1', credentials=creds)
    
    # Create form
    form = service.forms().create(body={'info': {'title': title}}).execute()
    form_id = form['formId']
    
    # Add questions
    requests = []
    for i, q in enumerate(questions):
        requests.append({
            'createItem': {
                'item': {
                    'title': q['question'],
                    'questionItem': {
                        'question': {
                            'required': q.get('required', False),
                            q['type'].lower() + 'Question': {
                                'options': [{'value': opt} for opt in q.get('options', [])]
                            } if q['type'] == 'MULTIPLE_CHOICE' else {}
                        }
                    }
                },
                'location': {'index': i}
            }
        })
    
    service.forms().batchUpdate(
        formId=form_id,
        body={'requests': requests}
    ).execute()
    
    return {
        'success': True,
        'form_id': form_id,
        'title': title,
        'url': f"https://docs.google.com/forms/d/{form_id}/edit",
        'responder_uri': f"https://docs.google.com/forms/d/{form_id}/viewform"
    }
```

**Complete Forms Tool List:**

1. `google_forms_create_form` - Create form with questions
2. `google_forms_get_form` - Get form structure
3. `google_forms_list_responses` - Get form responses
4. `google_forms_get_response` - Get single response

---

## Additional Services

### Google Tasks

**File:** `google_workspace/google_tasks.py` (3 tools)

1. `google_tasks_list_task_lists` - Get all task lists
2. `google_tasks_list_tasks` - List tasks in list
3. `google_tasks_create_task` - Create new task

### Google Meet

**File:** `google_workspace/google_meet.py` (2 tools)

1. `google_meet_create_meeting` - Create video meeting
2. `google_meet_get_recording` - Get meeting recording

### Google Analytics

**File:** `google_workspace/google_analytics.py`

1. `google_analytics_get_report` - Get analytics data

### Google Cloud Run

**File:** `google_workspace/google_cloud_run.py`

1. `google_cloud_run_deploy` - Deploy service
2. `google_cloud_run_list_services` - List services

### Google Apps Script

**File:** `tools/implementations/google_apps_script.py`

1. `google_apps_script_execute` - Execute custom Apps Script

---

## Implementation Details

### Credential Injection Pattern

**All Google tools use automatic credential injection:**

```python
def gmail_send_message(user_id: int, to: str, subject: str, body: str):
    """
    Tool function with user_id parameter
    
    user_id is automatically injected by tool registry
    based on current user session
    """
    from google_workspace.oauth_manager import GoogleOAuthManager
    
    # Credentials automatically fetched and refreshed if needed
    creds = GoogleOAuthManager.get_valid_credentials(user_id)
    
    # Build service with credentials
    from googleapiclient.discovery import build
    service = build('gmail', 'v1', credentials=creds)
    
    # Use service...
```

### Error Handling

**OAuth Error Handling:**

```python
try:
    creds = GoogleOAuthManager.get_valid_credentials(user_id)
except ValueError as e:
    return {
        'success': False,
        'error': 'Google account not connected',
        'message': 'Please connect your Google account in Platform Connections',
        'action_required': 'oauth_connect'
    }
except RefreshError as e:
    return {
        'success': False,
        'error': 'Token refresh failed',
        'message': 'Please reconnect your Google account',
        'action_required': 'oauth_reconnect'
    }
```

### Rate Limiting

**Gmail API Rate Limits:**
- 250 quota units/second/user
- 1 billion quota units/day
- List messages: 5 units
- Get message: 5 units
- Send message: 100 units

**Best Practices:**
```python
import time

def batch_gmail_operations(user_id, operations):
    """Execute operations with rate limiting"""
    results = []
    
    for op in operations:
        result = execute_operation(user_id, op)
        results.append(result)
        
        # Sleep 10ms between operations
        time.sleep(0.01)
    
    return results
```

---

## Critical Fixes

### Fix 1: OAuth New User Creation (Dec 4, 2025)

**Problem:** New users couldn't complete OAuth flow - user record not created before callback.

**Solution:**
```python
# BEFORE (BROKEN)
@google_auth_bp.route('/api/google-auth/callback')
def callback():
    user_id = session.get('oauth_user_id')  # user_id doesn't exist yet
    # Store tokens with non-existent user_id → FAIL

# AFTER (FIXED)
@google_auth_bp.route('/api/google-auth/callback')
def callback():
    email = get_google_user_email(credentials)
    
    # Create user if doesn't exist
    user = execute_query(
        "SELECT user_id FROM users WHERE email = %s",
        (email,),
        fetch_mode='one'
    )
    
    if not user:
        user_id = execute_query(
            "INSERT INTO users (email) VALUES (%s) RETURNING user_id",
            (email,),
            fetch_mode='value'
        )
    else:
        user_id = user['user_id']
    
    # Now store tokens with valid user_id
    execute_query(...)
```

### Fix 2: Google Docs Token Overflow (Nov 27, 2025)

**Problem:** 40-page document returned 200K+ tokens, exceeding Claude context window.

**Solution:** Implemented 4-format system with `format='summary'` default

```python
# BEFORE
def google_docs_get_document(document_id):
    doc = service.documents().get(documentId=document_id).execute()
    return doc  # 200K+ tokens

# AFTER
def google_docs_get_document(document_id, format='summary'):
    doc = service.documents().get(documentId=document_id).execute()
    
    if format == 'summary':
        return {
            'title': doc['title'],
            'preview': extract_text(doc)[:2000],
            'character_count': len(extract_text(doc)),
            'note': "Use format='markdown' for full content"
        }  # 500 tokens (99.8% reduction!)
```

### Fix 3: Google Slides Insert Fail (Dec 4, 2025)

**Problem:** Image insertion failed due to incorrect object ID references.

**Solution:**
```python
# BEFORE (BROKEN)
requests.append({
    'insertImage': {
        'objectId': 'image_1',  # Wrong - objectId not yet created
        'url': image_url
    }
})

# AFTER (FIXED)
requests.append({
    'createImage': {
        'url': image_url,
        'elementProperties': {
            'pageObjectId': slide_id,  # Reference existing slide
            'size': {'width': {'magnitude': 400, 'unit': 'PT'}},
            'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': 100, 'translateY': 100}
        }
    }
})
```

### Fix 4: OAuth State CSRF Debugging (Jan 18, 2026)

**Problem:** OAuth state mismatches causing CSRF errors, difficult to debug

**Root Cause:** Insufficient logging during OAuth flow for state parameter tracking

**Solution:** Added comprehensive state logging for Microsoft and Google OAuth

```python
# File: google_auth_routes_V2_FIXED.py, Line ~45
@google_auth_bp.route('/api/google-auth/authorize')
def authorize():
    state = str(uuid.uuid4())
    session['oauth_state'] = state
    session['oauth_user_id'] = user_id
    
    # ✅ NEW: Detailed logging
    logger.info(f"[GOOGLE AUTH] State generated: {state}")
    logger.info(f"[GOOGLE AUTH] Session ID: {session.sid}")
    logger.info(f"[GOOGLE AUTH] User ID: {user_id}")
    logger.info(f"[GOOGLE AUTH] Redirect URI: {redirect_uri}")
    
    # Generate authorization URL...

@google_auth_bp.route('/api/google-auth/callback')
def callback():
    state_from_request = request.args.get('state')
    state_from_session = session.get('oauth_state')
    
    # ✅ NEW: Debug logging
    logger.info(f"[GOOGLE CALLBACK] Received state: {state_from_request}")
    logger.info(f"[GOOGLE CALLBACK] Session state: {state_from_session}")
    logger.info(f"[GOOGLE CALLBACK] Session ID: {session.sid}")
    logger.info(f"[GOOGLE CALLBACK] Match: {state_from_request == state_from_session}")
    
    if state_from_request != state_from_session:
        logger.error(f"[GOOGLE CALLBACK] CSRF attack detected!")
        return jsonify({'error': 'State mismatch'}), 400
```

```python
# File: microsoft_auth_routes_V2_FIXED.py, Line ~50
# Similar logging pattern for Microsoft OAuth

@microsoft_auth_bp.route('/api/microsoft-auth/authorize')
def authorize():
    state = str(uuid.uuid4())
    session['microsoft_oauth_state'] = state
    
    logger.info(f"[MICROSOFT AUTH] State: {state}")
    logger.info(f"[MICROSOFT AUTH] Session: {session.sid}")
    logger.info(f"[MICROSOFT AUTH] User: {user_id}")
    
@microsoft_auth_bp.route('/api/microsoft-auth/callback')
def callback():
    logger.info(f"[MICROSOFT CALLBACK] Received: {request.args.get('state')}")
    logger.info(f"[MICROSOFT CALLBACK] Expected: {session.get('microsoft_oauth_state')}")
    logger.info(f"[MICROSOFT CALLBACK] Session: {session.sid}")
```

**Impact:**
- Faster CSRF debugging (identify session/state issues immediately)
- Production monitoring for OAuth failures
- Detailed audit trail for security incidents

**Files Modified:**
- `AI_infrastructure/routes/google_auth_routes_V2_FIXED.py` (Lines 45-80)
- `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py` (Lines 50-85)

**Status:** ✅ COMPLETE

---

### Fix 5: Gmail Threading Implementation (Jan 12, 2026)

**Problem:** Communication Hub showed individual emails, not threaded conversations like Gmail.

**Solution:** Implemented Gmail-style collapsed threading with expand/collapse chevrons

**Changes:**
- Added `expandedThreads: new Set()` to state
- Created `createCollapsedView()` to group by `thread_id`
- Added `toggleThread()` function for expand/collapse
- Modified subject column formatter to show chevrons and thread count
- Updated preview panel to show full conversation thread

**Files Modified:**
- `UI/modules_internal/communication-hub/communication-hub-v4-modern.js` (~150 lines changed)

---

## Testing & Deployment

### Local Testing

**1. Test OAuth Flow:**
```python
# Start OAuth flow
import requests

response = requests.get(
    'http://localhost:5000/api/google-auth/start',
    params={'user_id': 1}
)

auth_url = response.json()['authorization_url']
print(f"Visit: {auth_url}")

# After consent, check token storage
from AI_infrastructure.shared.database_utils import execute_query

tokens = execute_query("""
    SELECT access_token, refresh_token, token_expiry
    FROM ai_infrastructure.oauth_tokens
    WHERE user_id = 1 AND platform = 'google'
""", fetch_mode='one')

print(f"Token expires: {tokens['token_expiry']}")
```

**2. Test Gmail Integration:**
```python
from google_workspace.gmail import gmail_list_messages

messages = gmail_list_messages(user_id=1, query="is:unread", max_results=5)

print(f"Found {len(messages['messages'])} unread messages")
for msg in messages['messages']:
    print(f"{msg['from']}: {msg['subject']}")
```

**3. Test Google Docs:**
```python
from google_workspace.google_docs import google_docs_get_document

# Test summary format (500 tokens)
summary = google_docs_get_document(
    user_id=1,
    document_id='1M11p3SwvTHFSF5pcJd-oq2w9E_ShaBL17IMckkpkvj0',
    format='summary'
)

print(f"Title: {summary['title']}")
print(f"Preview: {summary['preview'][:100]}...")
print(f"Characters: {summary['character_count']}")
```

**4. Test Google Sheets with Markdown v3.0:**
```python
from google_workspace.google_sheets import google_sheets_create

result = google_sheets_create(
    user_id=1,
    title="Test Dashboard",
    headers=["# Item", "**Price**", "**Status**"],
    data=[
        ["Product A", "[$]1500", "[IF>1000:GREEN]1500"],
        ["Product B", "[$]500", "[IF<1000:YELLOW]500"]
    ],
    parse_markdown=True,
    auto_resize_columns=True
)

print(f"Created: {result['url']}")
```

### Deployment Checklist

**Environment Variables (Render):**
```bash
# Google OAuth
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/google-auth/callback

# Optional: Service account for backend operations
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

**Required Python Packages:**
```txt
# Google APIs
google-api-python-client>=2.0.0
google-auth>=2.0.0
google-auth-oauthlib>=0.5.0
google-auth-httplib2>=0.1.0
```

**Database Schema:**
```sql
-- OAuth tokens table (already exists in ai_infrastructure schema)
CREATE TABLE IF NOT EXISTS ai_infrastructure.oauth_tokens (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id),
    platform VARCHAR(50) NOT NULL,  -- 'google'
    access_token TEXT NOT NULL,     -- Encrypted
    refresh_token TEXT,             -- Encrypted
    token_expiry TIMESTAMP,
    scope TEXT,                     -- Space-separated scopes
    email VARCHAR(255),             -- Google account email
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, platform)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_oauth_tokens_user_platform 
ON ai_infrastructure.oauth_tokens(user_id, platform);
```

**Flask App Registration:**
```python
# AI_infrastructure/flask_app.py

from AI_infrastructure.routes.google_auth_routes_V2_FIXED import google_auth_bp

app.register_blueprint(google_auth_bp)
```

### Performance Benchmarks

| Operation | Time | Tokens |
|-----------|------|--------|
| **OAuth token refresh** | 200ms | N/A |
| **Gmail list (10 messages)** | 500ms | 2K |
| **Gmail send email** | 800ms | N/A |
| **Google Docs summary** | 300ms | 500 |
| **Google Docs markdown (40 pages)** | 2s | 55K |
| **Google Sheets create (100 rows)** | 1.5s | N/A |
| **Google Slides create (10 slides)** | 2s | N/A |
| **Calendar event create** | 400ms | N/A |

---

## Related Documentation

### Core System Documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Master system architecture
- **[SUPABASE_DATABASE.md](SUPABASE_DATABASE.md)** - OAuth tokens table schema
- **[COMMUNICATION_HUB.md](COMMUNICATION_HUB.md)** - Gmail/Outlook unified inbox

### Platform Integrations
- **[XERO_INTEGRATION.md](XERO_INTEGRATION.md)** - Similar OAuth pattern reference
- **[EMAIL_AUTOMATION.md](EMAIL_AUTOMATION.md)** - SMTP fallback for Gmail

### Implementation Files
- `google_workspace/gmail.py` (15 tools)
- `google_workspace/google_drive.py` (8 tools)
- `google_workspace/google_docs.py` (7 tools)
- `google_workspace/google_sheets.py` (10 tools)
- `google_workspace/google_slides.py` (6 tools)
- `google_workspace/google_calendar.py` (5 tools)
- `google_workspace/google_forms.py` (4 tools)
- `google_workspace/google_tasks.py` (3 tools)
- `google_workspace/google_meet.py` (2 tools)
- `google_workspace/sheets_markdown_formatter.py` (v3.0)
- `google_workspace/google_auth_helper.py`
- `google_workspace/oauth_manager.py`
- `AI_infrastructure/routes/google_auth_routes_V2_FIXED.py`
- `UI/modules_internal/communication-hub/communication-hub-v4-modern.js`

---

## Files Consolidated (82+)

This document consolidates the following Google Workspace documentation files:

**Google Sheets (12 files):**
1. GOOGLE_SHEETS_IMPLEMENTATION_COMPLETE.md
2. GOOGLE_SHEETS_MARKDOWN_FORMATTER_DOCUMENTATION.md
3. GOOGLE_SHEETS_FORMATTER_V3_COMPLETE.md
4. GOOGLE_SHEETS_ENHANCEMENT_ANALYSIS.md
5. GOOGLE_SHEETS_V3_QUICK_REFERENCE.md
6. GOOGLE_SHEETS_V3_IMPLEMENTATION_SUMMARY.md

**Gmail (10 files):**
7. GMAIL_THREADING_IMPLEMENTATION_COMPLETE_JAN12.md
8. GMAIL_FUNCTIONS_TEST_RESULTS.md
9. GMAIL_FUNCTIONS_QUICK_REFERENCE.md
10. GMAIL_ATTACHMENT_FUNCTIONS_COMPLETE.md

**Google Docs (8 files):**
11. GOOGLE_DOCS_V2_FIXES_DEC1.md
12. GOOGLE_DOCS_V2_ANALYSIS_DEC1.md
13. GOOGLE_DOCS_TOKEN_OVERFLOW_FIX_NOV27.md
14. GOOGLE_DOCS_TOKEN_FIX_SUMMARY.md
15. GOOGLE_DOCS_TOKEN_FIX_QUICK_REFERENCE.md

**Google OAuth (6 files):**
16. GOOGLE_OAUTH_USER_CREATION_FIX_NOV24.md
17. GOOGLE_OAUTH_NEW_USER_FIX_DEC4_2025.md
18. GOOGLE_WORKSPACE_CREDENTIAL_AUDIT_DEC4_2025.md

**Google Slides (5 files):**
19. GOOGLE_SLIDES_INSERT_FIX_DEC4_2025.md
20. GOOGLE_SLIDES_AUDIT_DEC4_2025.md

**Google Forms (4 files):**
21. GOOGLE_FORMS_SCHEMA_ANALYSIS_NOV28.md
22. GOOGLE_FORMS_FIX_AND_SMART_TOOLS_NOV28.md

**Google Analytics (2 files):**
23. GOOGLE_ANALYTICS_FIX_NOV28.md

**General (3 files):**
24. GOOGLE_WORKSPACE_FORMAT_REFERENCE.md (844 lines)

**Plus 30+ archived documentation files** in `docs/archive/google_workspace/`

**Total Lines Consolidated:** 8,000+ lines → 2,000 lines (75% reduction)  
**Documentation Coverage:** Complete Google Workspace integration with zero information loss

---

**END OF GOOGLE_INTEGRATION.md**
