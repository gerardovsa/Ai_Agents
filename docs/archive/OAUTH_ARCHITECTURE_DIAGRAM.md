# OAuth Architecture - Visual Diagram

## Complete OAuth Flow (Database OAuth - Fix #13)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER AUTHENTICATION                         │
└─────────────────────────────────────────────────────────────────────┘

[Frontend Web App]
       │
       │ 1. Click "Login with Google"
       ▼
[/api/auth/google/login] (google_auth_routes_V2_FIXED.py)
       │
       │ 2. Redirect to Google consent screen
       ▼
[Google OAuth Consent]
  - Grant permissions
  - Click "Allow"
       │
       │ 3. Google redirects back with auth code
       ▼
[/api/auth/google/callback] (google_auth_routes_V2_FIXED.py)
       │
       │ 4. Exchange auth code for tokens
       │ POST to https://oauth2.googleapis.com/token
       ▼
[OAuth Tokens Received]
  - access_token (1 hour)
  - refresh_token (never expires)
  - expires_at (timestamp)
       │
       │ 5. Store in database
       ▼
┌───────────────────────────────────────────┐
│  DATABASE: ai_infrastructure.db           │
│  TABLE: oauth_tokens                      │
│  ┌─────────────────────────────────────┐  │
│  │ id: 1                               │  │
│  │ user_id: 1                          │  │
│  │ platform: 'google'                  │  │
│  │ access_token: 'ya29.a0...'         │  │
│  │ refresh_token: '1//0g...'          │  │
│  │ expires_at: '2025-11-01 15:00:00'  │  │
│  │ email: 'user@example.com'          │  │
│  │ scope: 'gmail calendar tasks...'   │  │
│  └─────────────────────────────────────┘  │
└───────────────────────────────────────────┘
       │
       │ 6. Create JWT session token
       ▼
[Return to Frontend]
  - JWT token stored in localStorage
  - User logged in successfully

┌─────────────────────────────────────────────────────────────────────┐
│                         TOOL EXECUTION                              │
└─────────────────────────────────────────────────────────────────────┘

[User sends chat message]
  "List my Gmail messages"
       │
       │ + JWT token in Authorization header
       ▼
[Flask Route: /api/agent/chat] (agent_routes_v4.py)
       │
       │ 1. OAuth middleware validates JWT
       ▼
[@oauth_required decorator]
       │
       │ 2. Extract user_id from JWT
       │ g.user_id = 1
       ▼
[Agent Worker] (agent_worker.py)
       │
       │ 3. Claude API selects tool
       │ Tool: gmail_list_messages
       ▼
[Tool Execution]
  Parameters:
    - max_results: 10
    - _user_id: 1 (injected)
    - _injected_credentials: True (injected)
       │
       │ 4. Call tool function
       ▼
[gmail_list_messages(max_results=10, _user_id=1)]
       │
       │ 5. Tool needs Google API service
       ▼
[credential_injector.py]
  create_google_service_with_user_credentials(
    user_id=1,
    service_name='gmail',
    version='v1'
  )
       │
       │ 6. Query database for tokens
       ▼
┌───────────────────────────────────────────┐
│  DATABASE: ai_infrastructure.db           │
│  QUERY:                                   │
│  SELECT access_token, refresh_token       │
│  FROM oauth_tokens                        │
│  WHERE user_id = 1 AND platform = 'google'│
│  ORDER BY updated_at DESC LIMIT 1         │
└───────────────────────────────────────────┘
       │
       │ 7. Create Google API Credentials object
       ▼
[google.oauth2.credentials.Credentials]
  - token: 'ya29.a0...'
  - refresh_token: '1//0g...'
  - token_uri: 'https://oauth2.googleapis.com/token'
  - client_id: 'xxx.apps.googleusercontent.com'
  - client_secret: 'GOCSPX-...'
  - scopes: ['https://www.googleapis.com/auth/gmail.readonly']
       │
       │ 8. Build Gmail service
       ▼
[googleapiclient.discovery.build('gmail', 'v1', credentials=...)]
       │
       │ 9. Execute API call
       ▼
[service.users().messages().list(userId='me', maxResults=10).execute()]
       │
       │ 10. Return user's personal emails
       ▼
[Response]
{
  "messages": [
    {"id": "18c...", "subject": "Meeting Tomorrow"},
    {"id": "18d...", "subject": "Invoice #12345"},
    ...
  ]
}
       │
       │ 11. Return to agent
       ▼
[Agent formats response]
  "You have 10 messages. The most recent is from..."
       │
       │ 12. Stream to frontend
       ▼
[User sees response in chat]
```

---

## File Architecture Map

```
AI_agents/
│
├── 🔐 ACTIVE OAUTH ROUTES (Flask Blueprints)
│   ├── AI_infrastructure/routes/
│   │   ├── google_auth_routes_V2_FIXED.py ✅ ACTIVE
│   │   │   └── Blueprint: google_auth_bp
│   │   │       ├── /api/auth/google/login
│   │   │       ├── /api/auth/google/callback
│   │   │       ├── /api/auth/google/status
│   │   │       └── /api/auth/google/revoke
│   │   │
│   │   ├── microsoft_auth_routes_V2_FIXED.py ✅ ACTIVE
│   │   │   └── Blueprint: microsoft_auth_bp
│   │   │       ├── /api/auth/microsoft/login
│   │   │       ├── /api/auth/microsoft/callback
│   │   │       ├── /api/auth/microsoft/status
│   │   │       └── /api/auth/microsoft/revoke
│   │   │
│   │   └── oauth_routes.py ⚠️ LEGACY (DELETE)
│   │       └── Old Google OAuth (file-based)
│   │
│   └── routes/ (OLD LOCATION)
│       └── microsoft_auth_routes.py ⚠️ LEGACY (DELETE)
│           └── Old Microsoft OAuth (wrong schema)
│
├── 🔧 ACTIVE AUTH INFRASTRUCTURE
│   ├── AI_infrastructure/auth/
│   │   ├── user_auth.py ✅ ACTIVE
│   │   │   └── UserAuthManager class
│   │   │       ├── JWT generation
│   │   │       ├── User registration/login
│   │   │       ├── Session management
│   │   │       └── Gmail account loading
│   │   │
│   │   └── credential_injector.py ✅ ACTIVE
│   │       └── OAuth credential injection
│   │           ├── create_google_service_with_user_credentials()
│   │           ├── Queries oauth_tokens table
│   │           └── Returns Google API service object
│   │
│   └── AI_infrastructure/config/
│       └── oauth_config.py ✅ ACTIVE
│           └── OAUTH_PROVIDERS dict
│               ├── Google config
│               ├── Microsoft config
│               └── Loads from .env.master
│
├── 🗂️ OAUTH MANAGERS (Provider-Specific)
│   ├── google_workspace/
│   │   ├── oauth_manager.py ⚠️ LEGACY (PHASING OUT)
│   │   │   └── File-based OAuth (credentials_desktop.json)
│   │   │       ├── Uses token files
│   │   │       └── Not multi-tenant
│   │   │
│   │   └── oauth_credential_loader.py ⚠️ REDUNDANT
│   │       └── Database OAuth loader (lower level)
│   │           └── Use credential_injector.py instead
│   │
│   └── Microsoft_365_Connection/
│       └── microsoft365_oauth_manager.py ✅ ACTIVE
│           └── Microsoft365OAuthManager class
│               ├── Build auth URLs
│               ├── Exchange tokens
│               └── Refresh tokens
│
├── 🛠️ UTILITIES
│   ├── get_auth_token.py ✅ UTILITY (CLI)
│   │   └── Generate JWT tokens for testing
│   │       └── Usage: python get_auth_token.py user@example.com
│   │
│   └── google-auth.js ⚠️ FRONTEND ONLY
│       └── Chrome extension OAuth
│           └── Separate from backend OAuth
│
└── 💾 DATABASE
    └── data/ai_infrastructure.db ✅ ACTIVE
        ├── oauth_tokens (24 columns)
        ├── users
        ├── user_sessions
        └── user_profile
```

---

## OAuth System Layers

```
┌────────────────────────────────────────────────────────┐
│                    LAYER 1: ROUTES                     │
│  Flask blueprints handling OAuth callbacks             │
│  - google_auth_routes_V2_FIXED.py                      │
│  - microsoft_auth_routes_V2_FIXED.py                   │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│                  LAYER 2: MANAGERS                     │
│  OAuth flow utilities (token exchange, refresh)        │
│  - microsoft365_oauth_manager.py                       │
│  - oauth_manager.py (legacy file-based)                │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│                 LAYER 3: CONFIGURATION                 │
│  OAuth provider credentials and settings               │
│  - oauth_config.py (loads from .env.master)            │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│                  LAYER 4: DATABASE                     │
│  Token storage and user management                     │
│  - oauth_tokens table (access/refresh tokens)          │
│  - users table (user accounts)                         │
│  - user_sessions table (JWT tokens)                    │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│               LAYER 5: AUTHENTICATION                  │
│  JWT validation and user identification                │
│  - user_auth.py (UserAuthManager)                      │
│  - @oauth_required middleware decorator                │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│             LAYER 6: CREDENTIAL INJECTION              │
│  Inject user OAuth tokens into tool calls              │
│  - credential_injector.py                              │
│  - create_google_service_with_user_credentials()       │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│                  LAYER 7: TOOLS                        │
│  Google Workspace tools using injected credentials     │
│  - gmail_list_messages(_user_id=1)                     │
│  - google_calendar_list_calendars(_user_id=1)          │
│  - google_tasks_list_task_lists(_user_id=1)            │
└────────────────────────────────────────────────────────┘
```

---

## OAuth Token Flow States

```
STATE 1: USER NOT LOGGED IN
┌──────────────────────────┐
│ No JWT token             │
│ No oauth_tokens record   │
│ Tools fail: "Not auth"   │
└──────────────────────────┘

STATE 2: USER LOGGING IN
┌──────────────────────────┐
│ OAuth flow initiated     │
│ Redirected to Google     │
│ Waiting for consent...   │
└──────────────────────────┘

STATE 3: USER LOGGED IN (FRESH TOKEN)
┌──────────────────────────────────────┐
│ JWT token: valid                     │
│ OAuth token: valid (expires in 1hr)  │
│ Tools: Working ✅                    │
└──────────────────────────────────────┘

STATE 4: ACCESS TOKEN EXPIRED (AUTO REFRESH)
┌──────────────────────────────────────┐
│ JWT token: valid                     │
│ OAuth token: expired                 │
│ Refresh token: valid                 │
│ → Auto-refresh access token          │
│ → Update oauth_tokens table          │
│ → Tools continue working ✅          │
└──────────────────────────────────────┘

STATE 5: REFRESH TOKEN EXPIRED (RE-AUTH NEEDED)
┌──────────────────────────────────────┐
│ JWT token: valid                     │
│ OAuth token: expired                 │
│ Refresh token: expired/revoked       │
│ → User must re-login                 │
│ → Tools fail: "Re-auth required" ❌  │
└──────────────────────────────────────┘
```

---

## OAuth Scopes by Provider

### Google Workspace (google_auth_routes_V2_FIXED.py)

```
Scope: https://www.googleapis.com/auth/gmail.readonly
  └─> Read Gmail messages

Scope: https://www.googleapis.com/auth/gmail.send
  └─> Send Gmail messages

Scope: https://www.googleapis.com/auth/gmail.compose
  └─> Create Gmail drafts

Scope: https://www.googleapis.com/auth/drive
  └─> Full Google Drive access

Scope: https://www.googleapis.com/auth/calendar
  └─> Full Google Calendar access

Scope: https://www.googleapis.com/auth/documents
  └─> Full Google Docs access

Scope: https://www.googleapis.com/auth/spreadsheets
  └─> Full Google Sheets access

Scope: https://www.googleapis.com/auth/forms
  └─> Full Google Forms access

Scope: https://www.googleapis.com/auth/tasks
  └─> Full Google Tasks access
```

### Microsoft 365 (microsoft_auth_routes_V2_FIXED.py)

```
Scope: User.Read
  └─> Read user profile

Scope: Mail.Read
  └─> Read emails

Scope: Mail.Send
  └─> Send emails

Scope: Mail.ReadWrite
  └─> Full email access

Scope: Calendars.ReadWrite
  └─> Full calendar access

Scope: Tasks.ReadWrite
  └─> To Do tasks access

Scope: Files.ReadWrite.All
  └─> Full OneDrive access

Scope: Team.ReadBasic.All
  └─> Read team info

Scope: Chat.ReadWrite
  └─> Teams chat access
```

---

## File Cleanup Checklist

### ✅ Keep These (Active)
- `AI_infrastructure/routes/google_auth_routes_V2_FIXED.py`
- `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py`
- `AI_infrastructure/auth/user_auth.py`
- `AI_infrastructure/auth/credential_injector.py`
- `AI_infrastructure/config/oauth_config.py`
- `Microsoft_365_Connection/microsoft365_oauth_manager.py`
- `get_auth_token.py` (CLI utility)
- `google-auth.js` (Chrome extension only)

### ⚠️ Phase Out These (Legacy)
- `google_workspace/oauth_manager.py` (file-based OAuth)
- `google_workspace/oauth_credential_loader.py` (redundant)

### ❌ Delete These (Not Used)
- `AI_infrastructure/routes/oauth_routes.py` (old Google OAuth)
- `routes/microsoft_auth_routes.py` (old Microsoft OAuth)

---

**Summary:** 12 OAuth files → 8 active (6 core + 2 utilities) + 2 phasing out + 2 to delete
