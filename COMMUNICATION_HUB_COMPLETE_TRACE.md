# Communication Hub - Complete System Trace 🔍

**Date:** December 20, 2025  
**Purpose:** Forward and backward trace of ALL Communication Hub tabs (Gmail, Outlook, and future providers)  
**Architecture:** Unified inbox with provider-agnostic frontend and backend

---

## 🎯 System Architecture Overview

### **Three-Layer Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND LAYER (JavaScript)                                 │
│ UI/modules_internal/communication-hub/                      │
│ communication-hub-v4-modern.js                              │
├─────────────────────────────────────────────────────────────┤
│ - Unified inbox interface (Tabulator table)                 │
│ - Account filter dropdown: ALL | GMAIL | OUTLOOK            │
│ - Email tagging system (green/orange/red)                   │
│ - Drag-and-drop to AI columns                               │
│ - Email composition with provider selection                 │
│ - Thread view and search                                    │
└─────────────────────────────────────────────────────────────┘
                           ↓ HTTP REST API ↓
┌─────────────────────────────────────────────────────────────┐
│ BACKEND LAYER (Flask)                                       │
│ AI_infrastructure/routes/communication_routes.py            │
├─────────────────────────────────────────────────────────────┤
│ - GET  /api/communication-hub/accounts                      │
│ - GET  /api/communication-hub/emails?account=all|gmail|...  │
│ - POST /api/communication-hub/send                          │
│ - POST /api/communication-hub/emails/<id>/read              │
│ - GET  /api/communication-hub/search                        │
└─────────────────────────────────────────────────────────────┘
                           ↓ Python API Wrappers ↓
┌─────────────────────────────────────────────────────────────┐
│ PROVIDER LAYER (OAuth APIs)                                 │
├─────────────────────────────────────────────────────────────┤
│ GMAIL:   google_workspace/gmail.py (45 functions)           │
│          - gmail_list_messages(), gmail_get_message()        │
│          - gmail_send_email(), gmail_mark_as_read()          │
│                                                              │
│ OUTLOOK: tools/implementations/microsoft_outlook_tools.py   │
│          - microsoft_outlook_list_messages()                 │
│          - microsoft_outlook_send_email()                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Tab Structure (Frontend)

### **Main Module Container**
```
#communication-main-container (shown when module active)
├── Sub-tab buttons (4 tabs):
│   ├── 🔹 Unified Inbox (default active)
│   ├── 🔹 Compose
│   ├── 🔹 Threads
│   └── 🔹 Search
└── Sub-tab content containers:
    ├── #communication-hub-subtab-unified-inbox
    ├── #communication-hub-subtab-compose
    ├── #communication-hub-subtab-threads
    └── #communication-hub-subtab-search
```

### **Tab 1: Unified Inbox (Lines 385-497)**

**Purpose:** Display all emails from Gmail + Outlook in single table

**UI Components:**
- **Stat Cards (4):**
  - Total Emails
  - Gmail Count (`#gmail-count`)
  - Outlook Count (`#outlook-count`)
  - Unread Count (`#unread-count`)

- **Toolbar (renderToolbar - Lines 499-570):**
  - **Tag Buttons:** Clear, Green, Orange, Red
  - **Account Filter:** `<select id="accountSelector">`
    - Option: `value="all"` → "All Accounts"
    - Option: `value="gmail"` → "Gmail Only"
    - Option: `value="outlook"` → "Outlook Only"
  - **Limit Selector:** `<select id="email-limit">`
    - Options: 20, 50, 100, 200
  - **Refresh Button:** `data-action="refresh"`
  - **Export Buttons:** Excel, CSV, PDF
  - **Send to AI Button:** Opens dropdown with AI columns

- **Email Table:** Tabulator.js (`#email-table-container`)
  - Columns: Tag, From, Subject, Date, Actions
  - Row selection with checkboxes
  - Drag-and-drop support
  - Right-click context menu

**Data Flow (Inbox Tab):**
```
1. USER ACTION: Selects account filter (all/gmail/outlook)
2. USER ACTION: Clicks "Refresh" button
   ↓
3. FRONTEND: fetchEmails() called (Lines 1137-1202)
   - Gets user_id from window.UserAuth.user.id
   - Reads accountSelector value: 'all', 'gmail', or 'outlook'
   - Reads email-limit value: 20, 50, 100, or 200
   ↓
4. API CALL: GET /api/communication-hub/emails
   - Query params: user_id=12, account=all, limit=50
   ↓
5. BACKEND: list_emails() route (Lines 151-280)
   - @require_auth validates JWT token → user_id=12
   - Checks which accounts user has connected:
     * has_google = auth_manager.get_user_google_oauth_credentials(12)
     * has_microsoft = auth_manager.get_user_microsoft_oauth_credentials(12)
   ↓
6. PROVIDER CALLS (Parallel):
   
   IF account='all' OR account='gmail' AND has_google:
     └─> gmail_list_messages(max_results=50, _user_id=12)
         ├─> Returns: {'messages': [{id, threadId}, ...], 'count': N}
         ├─> For each message:
         │   └─> gmail_get_message(id, format='metadata', _user_id=12)
         │       └─> Parses headers: from, to, subject, date
         └─> Builds email objects with 'gmail_' prefix
   
   IF account='all' OR account='outlook' AND has_microsoft:
     └─> microsoft_outlook_list_messages(max_results=50, _user_id=12)
         └─> Returns: {'messages': [...], 'success': True}
         └─> Builds email objects with 'outlook_' prefix
   ↓
7. BACKEND: Sorts by date (newest first)
   - Returns: {success: true, emails: [...], count: N}
   ↓
8. FRONTEND: Receives emails array
   - Updates stat cards (total, gmail count, outlook count, unread)
   - Populates Tabulator table
   - Shows "Loaded X emails" message
   - Enables drag-and-drop
   - Enables right-click context menu
```

### **Tab 2: Compose (Lines 572-750)**

**Purpose:** Compose and send emails via Gmail or Outlook

**UI Components:**
- **Account Selector:** `<select id="compose-account">`
  - Options dynamically populated from connected accounts
  - Example: "gerardo@vetsuccessacademy.com (gmail)"
  - Example: "user@company.com (outlook)"

- **Email Form:**
  - To: `<input id="compose-to">` (email addresses, comma-separated)
  - Subject: `<input id="compose-subject">`
  - Body: `<textarea id="compose-body">` (rich text editor)
  - Attachments: File upload (future feature)

- **Buttons:**
  - Save Draft
  - Send Email

**Data Flow (Compose Tab):**
```
1. USER ACTION: Selects sending account from dropdown
2. USER ACTION: Fills To, Subject, Body fields
3. USER ACTION: Clicks "Send Email"
   ↓
4. FRONTEND: sendEmail() called (Lines 1843-1920)
   - Gets user_id from window.UserAuth.user.id
   - Reads compose-account value: 'gmail' or 'outlook'
   - Validates required fields
   ↓
5. API CALL: POST /api/communication-hub/send
   - Body: {
       user_id: 12,
       provider: 'gmail',
       to: ['recipient@example.com'],
       subject: 'Email Subject',
       body: 'Email body text',
       cc: [],
       bcc: []
     }
   ↓
6. BACKEND: send_email() route (Lines 360-455)
   - @require_auth validates user_id
   - Routes to correct provider:
   
   IF provider='gmail':
     └─> gmail_send_email(
           to='recipient@example.com',
           subject='Email Subject',
           body='Email body text',
           _user_id=12,
           _injected_credentials=True
         )
         └─> Uses user 12's Gmail OAuth tokens
         └─> Calls Gmail API: users().messages().send()
   
   IF provider='outlook':
     └─> microsoft_outlook_send_email(
           to='recipient@example.com',
           subject='Email Subject',
           body='Email body text',
           _user_id=12,
           _injected_credentials=True
         )
         └─> Uses user 12's Microsoft Graph OAuth tokens
         └─> Calls Microsoft Graph API: POST /me/sendMail
   ↓
7. BACKEND: Returns {success: true, message_id: '...'}
   ↓
8. FRONTEND: Shows success notification
   - Clears compose form
   - Optional: Switches to Unified Inbox tab
```

### **Tab 3: Threads (Lines 752-850)**

**Purpose:** View email threads (conversations grouped by subject/participants)

**UI Components:**
- Thread list with grouping
- Participant avatars
- Message count badges
- Last message preview

**Data Flow:** (Similar to Unified Inbox but with threading logic)

### **Tab 4: Search (Lines 852-950)**

**Purpose:** Full-text search across all email providers

**UI Components:**
- Search input field
- Advanced filters (date range, sender, has attachments)
- Search results table (same format as Unified Inbox)

**Data Flow (Search Tab):**
```
1. USER ACTION: Enters search query "invoice 2024"
2. USER ACTION: Clicks "Search" button
   ↓
3. FRONTEND: performSearch() called
   ↓
4. API CALL: GET /api/communication-hub/search
   - Query params: user_id=12, query='invoice 2024', account=all
   ↓
5. BACKEND: search_emails() route (Lines 550-650)
   - Calls gmail_search_messages(query='invoice 2024')
   - Calls microsoft_outlook_search_messages(query='invoice 2024')
   - Merges results
   - Returns unified search results
   ↓
6. FRONTEND: Displays results in table
```

---

## 🔄 Complete Data Flow Trace

### **FORWARD TRACE: User Loads Unified Inbox**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PAGE LOAD                                                 │
└─────────────────────────────────────────────────────────────┘
User clicks "Communication Hub" in sidebar
   ↓
ModuleLoader.loadModule('communication-hub')
   ↓
communication-hub-v4-modern.js loaded
   ↓
initialize() called (Lines 145-207)
   ├─> Utilities injected: dom, api, storage, events, log
   ├─> State initialized: emails=[], accounts=[], selectedEmails=Set()
   ├─> Container created: #communication-main-container
   ├─> Sub-tabs rendered:
   │   ├─> renderUnifiedInbox() → HTML injected
   │   ├─> renderCompose() → Form built
   │   ├─> renderThreads() → Thread view
   │   └─> renderSearch() → Search interface
   └─> initModule() called

┌─────────────────────────────────────────────────────────────┐
│ 2. INITIAL LOAD                                              │
└─────────────────────────────────────────────────────────────┘
initModule() (Lines 1067-1135)
   ↓
fetchAccounts() called (Lines 1089-1133)
   ├─> Gets user_id from window.UserAuth.user.id → 12
   ├─> API CALL: GET /api/communication-hub/accounts?user_id=12
   │   ↓
   │   BACKEND: get_accounts() route (Lines 81-149)
   │   ├─> @require_auth validates JWT → user_id=12
   │   ├─> auth_manager.get_user_google_oauth_credentials(12)
   │   │   └─> Queries: ai_infrastructure.oauth_tokens
   │   │       WHERE user_id=12 AND platform='google'
   │   │       └─> Found: access_token, refresh_token, email
   │   │           └─> Accounts array += {id:'gmail', provider:'gmail', 
   │   │                                  email:'gerardo@vetsuccessacademy.com'}
   │   │
   │   ├─> auth_manager.get_user_microsoft_oauth_credentials(12)
   │   │   └─> Queries: ai_infrastructure.oauth_tokens
   │   │       WHERE user_id=12 AND platform='microsoft'
   │   │       └─> Found/Not Found → Add to accounts if exists
   │   │
   │   └─> Returns: {success: true, accounts: [...], count: N}
   │
   └─> Updates: this.state.accounts = [...]
       └─> Enables account selector dropdown
       └─> Populates compose account options

┌─────────────────────────────────────────────────────────────┐
│ 3. USER REFRESHES INBOX                                      │
└─────────────────────────────────────────────────────────────┘
User clicks "Refresh" button
   ↓
Event handler: data-action="refresh" (Lines 305-310)
   ↓
fetchEmails() called (Lines 1137-1202)
   ├─> Gets user_id from window.UserAuth.user.id → 12
   ├─> Reads accountSelector.value → 'all' (default)
   ├─> Reads email-limit.value → 50 (default)
   │
   ├─> Shows loading state (#inbox-loading)
   │
   ├─> API CALL: GET /api/communication-hub/emails
   │   ?user_id=12&account=all&limit=50
   │   ↓
   │   BACKEND: list_emails() route (Lines 151-280)
   │   ├─> @require_auth: user_id=12 validated from JWT
   │   ├─> has_google = check oauth_tokens table → TRUE
   │   ├─> has_microsoft = check oauth_tokens table → FALSE (for this user)
   │   │
   │   ├─> ══════════════════════════════════════════════════
   │   │   GMAIL PROVIDER CALL (account='all' and has_google=TRUE)
   │   │   ══════════════════════════════════════════════════
   │   ├─> gmail_list_messages(max_results=50, _user_id=12, _injected_credentials=True)
   │   │   │
   │   │   └─> google_workspace/gmail.py (Lines 218-246)
   │   │       ├─> _get_gmail_service(_user_id=12)
   │   │       │   └─> auth_manager.get_user_google_oauth_credentials(12)
   │   │       │       └─> Returns: {access_token, refresh_token, token_uri, ...}
   │   │       │       └─> Creates: Credentials object
   │   │       │       └─> Builds: gmail service (Gmail API v1)
   │   │       │
   │   │       ├─> service.users().messages().list(userId='me', maxResults=50)
   │   │       │   └─> Returns: {'messages': [{id, threadId}, ...], 'nextPageToken'}
   │   │       │
   │   │       └─> Returns: {
   │   │             'messages': [
   │   │               {id: 'abc123', threadId: 'xyz456'},
   │   │               {id: 'def789', threadId: 'xyz456'},
   │   │               ...
   │   │             ],
   │   │             'count': 50
   │   │           }
   │   │
   │   ├─> For each message in gmail_result['messages']:
   │   │   │
   │   │   └─> gmail_get_message(message_id='abc123', format='metadata', _user_id=12)
   │   │       │
   │   │       └─> google_workspace/gmail.py (Lines 248-265)
   │   │           ├─> service.users().messages().get(id='abc123', format='metadata')
   │   │           │   └─> Returns: {
   │   │           │         id: 'abc123',
   │   │           │         threadId: 'xyz456',
   │   │           │         labelIds: ['INBOX', 'UNREAD'],
   │   │           │         snippet: 'Email preview text...',
   │   │           │         payload: {
   │   │           │           headers: [
   │   │           │             {name: 'From', value: 'sender@example.com'},
   │   │           │             {name: 'To', value: 'gerardo@vetsuccessacademy.com'},
   │   │           │             {name: 'Subject', value: 'Email subject'},
   │   │           │             {name: 'Date', value: 'Tue, 20 Dec 2025 10:30:00'}
   │   │           │           ]
   │   │           │         }
   │   │           │       }
   │   │           │
   │   │           ├─> Parse headers into dict:
   │   │           │   headers = {
   │   │           │     'from': 'sender@example.com',
   │   │           │     'to': 'gerardo@vetsuccessacademy.com',
   │   │           │     'subject': 'Email subject',
   │   │           │     'date': 'Tue, 20 Dec 2025 10:30:00'
   │   │           │   }
   │   │           │
   │   │           └─> Build email object:
   │   │               emails.append({
   │   │                 'id': 'gmail_abc123',
   │   │                 'provider': 'gmail',
   │   │                 'from': 'sender@example.com',
   │   │                 'to': 'gerardo@vetsuccessacademy.com',
   │   │                 'subject': 'Email subject',
   │   │                 'date': 'Tue, 20 Dec 2025 10:30:00',
   │   │                 'is_read': False, (UNREAD in labelIds)
   │   │                 'snippet': 'Email preview text...',
   │   │                 'has_attachments': False
   │   │               })
   │   │
   │   ├─> ══════════════════════════════════════════════════
   │   │   OUTLOOK PROVIDER CALL (IF has_microsoft=TRUE)
   │   │   ══════════════════════════════════════════════════
   │   └─> (Skipped for user 12 - no Microsoft OAuth tokens)
   │
   │   ├─> Sort emails by date (newest first)
   │   │
   │   └─> Returns: {
   │         success: true,
   │         emails: [
   │           {id: 'gmail_abc123', provider: 'gmail', from: '...', ...},
   │           {id: 'gmail_def789', provider: 'gmail', from: '...', ...},
   │           ...
   │         ],
   │         count: 50
   │       }
   │
   ├─> FRONTEND: Receives response
   │   ├─> this.state.emails = response.emails (50 emails)
   │   ├─> Updates stat cards:
   │   │   ├─> #total-emails-count = 50
   │   │   ├─> #gmail-count = 50
   │   │   ├─> #outlook-count = 0
   │   │   └─> #unread-count = (count where is_read=false)
   │   │
   │   ├─> createEmailTable() called (Lines 1200-1340)
   │   │   └─> Creates Tabulator table with columns:
   │   │       ├─> Tag (checkbox + color indicator)
   │   │       ├─> From (sender email)
   │   │       ├─> Subject (clickable)
   │   │       ├─> Date (formatted)
   │   │       └─> Actions (preview, delete, mark read)
   │   │
   │   ├─> Hides loading state
   │   ├─> Shows table container
   │   │
   │   └─> Enables interactions:
   │       ├─> setupEmailDragAndDrop() - Drag to AI columns
   │       ├─> setupContextMenu() - Right-click menu
   │       └─> setupRowEvents() - Click to preview

┌─────────────────────────────────────────────────────────────┐
│ 4. USER SENDS EMAILS TO AI COLUMN                            │
└─────────────────────────────────────────────────────────────┘
User selects 3 emails (checkboxes)
User clicks "Send to AI ▼" button
   ↓
showAIDestinationDropdown() called (Lines 1377-1470)
   ├─> Scans DOM for AI columns:
   │   ├─> #ai-chat-input (AI Prime)
   │   └─> .agent-column-container (Agent 1, Agent 2, ...)
   │
   ├─> Builds dropdown menu:
   │   ├─> ⭐ AI Prime [3] (blue icon)
   │   ├─> 🤖 Agent 1 [3] (purple icon)
   │   └─> 🤖 Agent 2 [3] (purple icon)
   │
   └─> User clicks "⭐ AI Prime"
       ↓
       sendSelectedToAIColumn('prime') called (Lines 1470-1570)
       ├─> Gets user_id from window.UserAuth.user.id → 12
       ├─> Gets selected emails: ['gmail_abc123', 'gmail_def789', 'gmail_ghi012']
       │
       ├─> API CALL: POST /api/threads/create
       │   Body: {
       │     user_id: 12,
       │     name: 'Emails: Subject of first email',
       │     location: 'prime',
       │     initial_message: '📧 Email 1...\n📧 Email 2...\n📧 Email 3...'
       │   }
       │   ↓
       │   BACKEND: create_thread() route
       │   ├─> INSERT INTO sessions.threads (user_id, name, location, ...)
       │   └─> Returns: {success: true, thread_slug: '1734789456123'}
       │
       ├─> For each selected email:
       │   │
       │   └─> assignEmailToThread('gmail_abc123', '1734789456123')
       │       │
       │       └─> API CALL: POST /api/thread-assignments/email
       │           Body: {
       │             user_id: 12,
       │             thread_slug: '1734789456123',
       │             email_thread_id: 'gmail_abc123',
       │             email_subject: 'Email subject',
       │             email_participants: '["sender@example.com", "gerardo@vetsuccessacademy.com"]'
       │           }
       │           ↓
       │           BACKEND: assign_email_to_thread() route (Lines 750-816)
       │           ├─> UPDATE sessions.threads
       │           │   SET email_thread_id='gmail_abc123',
       │           │       email_subject='Email subject',
       │           │       email_participants='[...]'
       │           │   WHERE thread_slug='1734789456123' AND user_id=12
       │           │
       │           └─> Returns: {success: true, thread_slug: '...'}
       │
       ├─> Emits event: 'open-thread'
       │   └─> ThreadManager opens thread in AI Prime sidebar
       │
       └─> Clears email selection
           └─> Shows success notification: "3 emails assigned to AI Prime"
```

### **BACKWARD TRACE: Email Badge on ThreadInfo Card**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. THREAD CARD RENDERING                                     │
└─────────────────────────────────────────────────────────────┘
ThreadManager loads thread: thread_slug='1734789456123'
   ↓
ThreadCardRegistry.renderBadges(thread, config) called
   ↓
Iterates through registered badge renderers (priority order)
   ├─> Priority 10: Synergy Session badges
   ├─> Priority 20: Workflow badges
   ├─> Priority 30: Automation badges
   ├─> Priority 40: EMAIL THREAD BADGES ← THIS ONE
   └─> Priority 50: Internal doc badges

┌─────────────────────────────────────────────────────────────┐
│ 2. EMAIL BADGE RENDERER CALLED                               │
└─────────────────────────────────────────────────────────────┘
UI/modules_internal/thread-cards/email-thread-integration.js
   ↓
window.EmailThreadIntegration.renderThreadBadge(thread, config)
   (Lines 20-120)
   ├─> Checks: thread.email_thread_id exists?
   │   └─> YES: 'gmail_abc123'
   │
   ├─> Checks: thread.email_subject exists?
   │   └─> YES: 'Email subject'
   │
   ├─> Checks: thread.email_participants exists?
   │   └─> YES: '["sender@example.com", "gerardo@vetsuccessacademy.com"]'
   │   └─> Parse JSON: participants = ['sender@example.com', '...']
   │
   ├─> Builds badge HTML:
   │   <div class="thread-badge" data-type="email-thread" 
   │        style="background: #f59e0b; border-left: 3px solid #d97706;">
   │     <span class="badge-icon">
   │       <i class="fas fa-envelope"></i>
   │     </span>
   │     <div class="badge-content">
   │       <div class="badge-title">Email Thread</div>
   │       <div class="badge-subtitle">Email subject</div>
   │       <div class="badge-meta">2 participants</div>
   │     </div>
   │     <button class="badge-action" onclick="openEmailThread(...)">
   │       <i class="fas fa-external-link-alt"></i>
   │     </button>
   │     <button class="badge-action" onclick="unlinkEmailThread(...)">
   │       <i class="fas fa-times"></i>
   │     </button>
   │   </div>
   │
   └─> Returns badge HTML to ThreadCardRegistry

┌─────────────────────────────────────────────────────────────┐
│ 3. USER CLICKS EMAIL BADGE                                   │
└─────────────────────────────────────────────────────────────┘
User clicks amber email badge on thread card
   ↓
window.EmailThreadIntegration.openEmailThread('gmail_abc123', event)
   (Lines 123-155)
   ├─> Emits event: 'switch-to-module'
   │   └─> Data: { moduleId: 'communication-hub' }
   │       └─> ModuleLoader activates Communication Hub
   │
   ├─> Waits for module to load (500ms delay)
   │
   └─> Sets filter in Communication Hub:
       ├─> Search for email ID: 'gmail_abc123'
       └─> Highlights matching row in table
           └─> Scrolls to email
               └─> Shows preview panel
```

---

## 🔌 Provider Integration Points

### **Gmail Provider**

**Location:** `google_workspace/gmail.py` (1,821 lines)

**Key Functions:**
- `gmail_list_messages(max_results, query, label_ids, **kwargs)` - List emails
- `gmail_get_message(message_id, format, **kwargs)` - Get email details
- `gmail_send_email(to, subject, body, **kwargs)` - Send email
- `gmail_mark_as_read(message_id, **kwargs)` - Mark as read
- `gmail_delete_message(message_id, **kwargs)` - Delete email
- `gmail_search_messages(query, max_results, **kwargs)` - Search

**Authentication:**
- Uses `_get_gmail_service(_user_id, _injected_credentials)` (Lines 32-108)
- Retrieves OAuth tokens from `ai_infrastructure.oauth_tokens` table
- Creates Google API credentials object
- Builds Gmail API v1 service

### **Outlook Provider**

**Location:** `tools/implementations/microsoft_outlook_tools.py`

**Key Functions:**
- `microsoft_outlook_list_messages(max_results, **kwargs)` - List emails
- `microsoft_outlook_get_message(message_id, **kwargs)` - Get email
- `microsoft_outlook_send_email(to, subject, body, **kwargs)` - Send
- `microsoft_outlook_mark_as_read(message_id, **kwargs)` - Mark read

**Authentication:**
- Uses Microsoft Graph API OAuth tokens
- Retrieved from `ai_infrastructure.oauth_tokens` table (platform='microsoft')
- Calls: `https://graph.microsoft.com/v1.0/me/messages`

### **Adding New Providers (e.g., Yahoo, ProtonMail)**

**Step 1: Create Provider Module**
```python
# tools/implementations/yahoo_mail_tools.py

def yahoo_list_messages(max_results=10, **kwargs):
    """List messages from Yahoo Mail"""
    _user_id = kwargs.get('_user_id')
    
    # Get OAuth tokens from database
    from AI_infrastructure.auth.user_auth import UserAuthManager
    auth_manager = UserAuthManager()
    creds = auth_manager.get_user_yahoo_oauth_credentials(_user_id)
    
    # Call Yahoo Mail API
    response = requests.get(
        'https://api.mail.yahoo.com/ws/v1/messages',
        headers={'Authorization': f'Bearer {creds["access_token"]}'},
        params={'max': max_results}
    )
    
    return {
        'messages': response.json()['messages'],
        'count': len(response.json()['messages'])
    }
```

**Step 2: Add to Backend Routes**
```python
# AI_infrastructure/routes/communication_routes.py

from tools.implementations.yahoo_mail_tools import yahoo_list_messages

@communication_bp.route('/emails', methods=['GET'])
def list_emails():
    # ... existing code ...
    
    # Yahoo: ONLY try if user has Yahoo OAuth credentials
    if account in ['all', 'yahoo'] and has_yahoo:
        yahoo_result = yahoo_list_messages(max_results=limit, _user_id=user_id)
        for msg in yahoo_result.get('messages', []):
            emails.append({
                'id': f"yahoo_{msg['id']}",
                'provider': 'yahoo',
                'from': msg.get('from'),
                'subject': msg.get('subject'),
                # ...
            })
```

**Step 3: Add to Frontend Dropdown**
```javascript
// communication-hub-v4-modern.js
renderToolbar() {
    return `
        <select id="accountSelector">
            <option value="all">All Accounts</option>
            <option value="gmail">Gmail Only</option>
            <option value="outlook">Outlook Only</option>
            <option value="yahoo">Yahoo Only</option>  <!-- ADD THIS -->
        </select>
    `;
}
```

**Step 4: Add to Stat Cards**
```javascript
// Update initModule() to count Yahoo emails
const yahooCount = this.state.emails.filter(e => e.provider === 'yahoo').length;
document.getElementById('yahoo-count').textContent = yahooCount;
```

---

## 🗄️ Database Schema

### **OAuth Tokens Table**
```sql
ai_infrastructure.oauth_tokens
├── id (primary key)
├── user_id (foreign key → users.id)
├── platform (text: 'google', 'microsoft', 'yahoo', etc.)
├── access_token (encrypted text)
├── refresh_token (encrypted text)
├── expires_at (timestamp)
├── email (text - account email address)
├── scope (text - OAuth scopes)
├── is_active (boolean)
└── created_at, updated_at

INDEX: user_id + platform (unique)
```

### **Thread Assignment Table (Email Linkage)**
```sql
sessions.threads
├── thread_slug (primary key)
├── user_id (foreign key)
├── name (thread title)
├── location (text: 'prime', 'agent-1', etc.)
├── email_thread_id (text NULL) ← Email ID (gmail_abc123)
├── email_subject (text NULL) ← Email subject
├── email_participants (text NULL) ← JSON array of participants
├── synergy_card_id (text NULL)
├── workflow_slug (text NULL)
├── automation_slug (text NULL)
├── internal_doc_slug (text NULL)
└── created_at, updated_at

INDEX: email_thread_id (WHERE NOT NULL)
```

---

## 📋 Testing Checklist

### **Gmail Integration**
- [ ] Fetch accounts: GET /api/communication-hub/accounts
- [ ] List emails: GET /api/communication-hub/emails?account=gmail
- [ ] Get email details: Click email row → Preview panel
- [ ] Send email: Compose tab → Select Gmail account → Send
- [ ] Mark as read: Actions column → Mark read
- [ ] Search emails: Search tab → Query "invoice"
- [ ] Tag emails: Select emails → Click Green/Orange/Red
- [ ] Send to AI: Select emails → "Send to AI" → Select column
- [ ] Email badge: Thread card shows amber email badge

### **Outlook Integration** (If user has Microsoft OAuth)
- [ ] Fetch accounts: Shows Outlook account in list
- [ ] List emails: Filter dropdown → "Outlook Only"
- [ ] Send email: Compose tab → Select Outlook account
- [ ] Mixed inbox: Filter → "All Accounts" shows Gmail + Outlook

### **Multi-Provider Testing**
- [ ] Stat cards: Counts update correctly (Total, Gmail, Outlook, Unread)
- [ ] Account filter: All/Gmail/Outlook filtering works
- [ ] Email table: Provider column shows 'gmail' or 'outlook'
- [ ] Drag and drop: Works for all providers
- [ ] Export: Excel/CSV/PDF includes all providers

---

## 🎯 Key Takeaways

### **Unified Architecture**
- ✅ Single frontend module handles ALL email providers
- ✅ Single backend route handles ALL email providers
- ✅ Account filter dropdown switches between providers
- ✅ Easy to add new providers (3 files to modify)

### **Provider Agnostic**
- ✅ Email objects normalized to common format
- ✅ Provider-specific IDs prefixed: `gmail_`, `outlook_`, `yahoo_`
- ✅ UI doesn't care about provider internals
- ✅ Badge system works for all providers

### **Authentication**
- ✅ Each user has separate OAuth tokens per provider
- ✅ Tokens stored in `ai_infrastructure.oauth_tokens` table
- ✅ Backend auto-checks which providers user has connected
- ✅ Frontend only shows connected accounts in dropdowns

### **Data Flow Pattern**
```
Frontend (account filter) → Backend (route to providers) → Provider APIs
     ↓                              ↓                            ↓
 Tabulator table            OAuth token retrieval        Gmail/Outlook/Yahoo API
     ↓                              ↓                            ↓
 User actions               Normalize response           Return raw email data
     ↓                              ↓                            ↓
 Send to AI column          Update database              Encrypted storage
```

---

**Status:** ✅ COMPLETE - All tabs traced forward and backward  
**Next:** Restart Flask server and test end-to-end email workflow

