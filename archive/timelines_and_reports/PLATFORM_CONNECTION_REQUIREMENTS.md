# 🔌 Platform Connection Requirements for AI Agents

**Date:** November 28, 2025  
**Purpose:** Complete guide for what AI agents need to connect to each platform  
**Status:** ✅ Active Reference Document

---

## 📋 Overview

For AI agents to use tools that interact with external platforms (Slack, Pinecone, Stripe, etc.), they need **credentials** that grant API access. This document explains:
- What type of authentication each platform requires
- Where credentials are stored in the database
- How the credential injection system works
- What users must provide for each platform

---

## 🏗️ Architecture Overview

### Credential Flow: User → Database → AI Agent → Platform API

```
┌─────────────────┐
│ 1. USER SETUP   │  User adds credentials via Account Settings → Connections
└────────┬────────┘
         ↓
┌──────────────────────────────────────────────┐
│ 2. DATABASE STORAGE (Supabase PostgreSQL)   │
│                                              │
│ A. oauth_tokens table                       │
│    - Google Workspace (OAuth 2.0)           │
│    - Microsoft 365 (OAuth 2.0)              │
│    - Xero (OAuth 2.0)                       │
│                                              │
│ B. user_platform_credentials table          │
│    - Slack (Bot Token)                      │
│    - Pinecone (API Key + Environment)       │
│    - Stripe (API Key + Environment)         │
│    - OpenAI (API Key)                       │
│    - Anthropic (API Key)                    │
│    - Twilio (Account SID + Auth Token)      │
│    - Shopify (API Key + Store URL)          │
│    - PayPal, AssemblyAI, Cloudflare, etc.   │
└────────┬─────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 3. CREDENTIAL INJECTION              │
│    (AI_infrastructure/auth/          │
│     credential_injector.py)          │
│                                      │
│ - Tool execution triggered           │
│ - System detects tool platform      │
│ - Queries database for user creds   │
│ - Injects into tool kwargs           │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 4. TOOL EXECUTION                    │
│    (tools/implementations/)          │
│                                      │
│ - Tool receives credentials          │
│ - Initializes API client             │
│ - Executes API call                  │
│ - Returns result to AI agent         │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 5. API CALL TO PLATFORM              │
│    (External Service)                │
│                                      │
│ - Slack API                          │
│ - Pinecone API                       │
│ - Stripe API                         │
│ - etc.                               │
└──────────────────────────────────────┘
```

---

## 🔐 Authentication Types

### 1. OAuth 2.0 (Two-Way Connection)

**Platforms:** Google Workspace, Microsoft 365, Xero, GitHub (future), Slack (future)

**Storage:** `ai_infrastructure.oauth_tokens` table

**What Users Provide:**
- Nothing directly! They click "Connect" button and authorize via browser
- OAuth flow redirects to platform's authorization page
- User grants permissions (scopes)
- Platform returns access token + refresh token
- System stores tokens in database

**Database Columns:**
```sql
CREATE TABLE ai_infrastructure.oauth_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    platform VARCHAR(50),          -- 'google', 'microsoft', 'xero'
    access_token TEXT,             -- Bearer token for API calls
    refresh_token TEXT,            -- Used to get new access tokens
    token_expiry TIMESTAMP,        -- When access token expires
    scope TEXT,                    -- Granted permissions
    email VARCHAR(255),            -- Connected account email
    is_active BOOLEAN DEFAULT TRUE,
    is_valid BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Credential Injection Example (Google):**
```python
# credential_injector.py
def create_google_service_with_user_credentials(user_id: int, service_name: str):
    # Query oauth_tokens table
    cursor.execute("""
        SELECT access_token, refresh_token, token_expiry
        FROM ai_infrastructure.oauth_tokens
        WHERE user_id = %s AND platform = 'google'
    """, (user_id,))
    
    # Create Google Credentials object
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri='https://oauth2.googleapis.com/token'
    )
    
    # Build API service (gmail, calendar, drive, etc.)
    service = build(service_name, 'v1', credentials=creds)
    return service
```

**What AI Agents Get:**
- For Gmail: `gmail_service` (authenticated Google API client)
- For Calendar: `calendar_service`
- For Microsoft: `headers` dict with `Authorization: Bearer {token}`

**Token Refresh:**
- Access tokens expire (usually 1 hour)
- System automatically refreshes using refresh_token
- New tokens saved back to database
- Happens transparently during tool execution

---

### 2. API Key Authentication

**Platforms:** Pinecone, OpenAI, Anthropic, Stripe, Twilio, PayPal, AssemblyAI, Cloudflare, Render, etc.

**Storage:** `ai_infrastructure.user_platform_credentials` table (JSONB `credentials` column)

**What Users Provide:**
- Platform-specific API key(s)
- Additional configuration (environment, endpoints, etc.)

**Database Columns:**
```sql
CREATE TABLE ai_infrastructure.user_platform_credentials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    platform VARCHAR(50),              -- 'pinecone', 'openai', 'stripe', etc.
    credential_type VARCHAR(20),       -- 'api_key', 'database'
    credential_key VARCHAR(255),       -- Friendly name (e.g., "Production API")
    credential_value TEXT,             -- Deprecated (use credentials JSONB)
    credentials JSONB,                 -- 🔑 MAIN STORAGE (platform-specific JSON)
    metadata JSONB,                    -- Additional info
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**JSONB Credentials Format (Platform-Specific):**

#### Pinecone
```json
{
  "api_key": "pcsk_...",
  "index_name": "inhouseprint",
  "environment": "us-east-1",
  "namespace": ""
}
```

#### OpenAI
```json
{
  "api_key": "sk-proj-...",
  "model": "text-embedding-ada-002",
  "dimensions": 1536,
  "organization_id": "org-..."
}
```

#### Stripe
```json
{
  "api_key": "sk_test_... or sk_live_...",
  "environment": "test | production",
  "webhook_secret": "whsec_..."
}
```

#### Twilio
```json
{
  "account_sid": "ACxxxxxxxxxxxxx",
  "auth_token": "your_auth_token",
  "phone_number": "+1234567890"
}
```

#### Slack (Bot Token)
```json
{
  "bot_token": "xoxb-...",
  "app_id": "A1234567890",
  "workspace_id": "T1234567890"
}
```

#### Shopify
```json
{
  "api_key": "shpat_...",
  "store_url": "yourstore.myshopify.com",
  "api_version": "2024-01"
}
```

**Credential Injection Example (Pinecone):**
```python
# pinecone_tools.py
def _get_pinecone_client(user_id: int, **kwargs):
    # Get credentials from JSONB column
    auth_manager = UserAuthManager()
    creds = auth_manager.get_platform_credentials(user_id, 'pinecone')
    
    # Extract values from JSONB
    api_key = creds['api_key']
    index_name = creds['index_name']
    
    # Initialize Pinecone client
    from pinecone import Pinecone
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    
    return index
```

**What AI Agents Get:**
- API-ready credentials directly from JSONB
- Tools initialize platform-specific clients
- Full access to platform APIs

---

### 3. Database Connections

**Platforms:** SQL Server, PostgreSQL (Supabase), InHousePrint SQL

**Storage:** `ai_infrastructure.user_platform_credentials` table (JSONB `credentials` column)

**What Users Provide:**
- Host (IP address or hostname)
- Port (1433 for SQL Server, 5432 for PostgreSQL)
- Database name
- Username
- Password
- Optional: SSL/TLS certificate

**JSONB Credentials Format:**
```json
{
  "host": "3.25.76.138",
  "port": 1433,
  "database": "InHousePrint",
  "username": "sa",
  "password": "encrypted_password",
  "driver": "ODBC Driver 17 for SQL Server",
  "encryption": "yes",
  "trust_server_certificate": "yes"
}
```

**Credential Injection Example:**
```python
# sql_database.py
def _get_db_connection(user_id: int, **kwargs):
    auth_manager = UserAuthManager()
    creds = auth_manager.get_platform_credentials(user_id, 'inhouseprint_sql')
    
    import pyodbc
    connection_string = (
        f"DRIVER={creds['driver']};"
        f"SERVER={creds['host']},{creds['port']};"
        f"DATABASE={creds['database']};"
        f"UID={creds['username']};"
        f"PWD={creds['password']};"
    )
    
    conn = pyodbc.connect(connection_string)
    return conn
```

---

## 🔌 Platform-by-Platform Requirements

### ✅ FULLY IMPLEMENTED (7 platforms)

#### 1. **Google Workspace** (OAuth 2.0)
- **What Users Need:** Google account with appropriate permissions
- **Setup Process:** Click "Connect Google Workspace" → Authorize in browser
- **Stored In:** `oauth_tokens` table
- **Injected As:** `gmail_service`, `calendar_service`, `drive_service`, etc.
- **Tools Available:** Gmail (19), Calendar (11), Tasks (9), Forms (41), Drive (18), Docs (19), Sheets (39), Slides (16), Meet (8)
- **Token Refresh:** Automatic (uses refresh_token)

#### 2. **Microsoft 365** (OAuth 2.0)
- **What Users Need:** Microsoft 365 account with admin consent (for organization)
- **Setup Process:** Click "Connect Microsoft 365" → Authorize in Azure
- **Stored In:** `oauth_tokens` table
- **Injected As:** `headers` dict with Bearer token
- **Tools Available:** Outlook (15), Calendar (10), Excel (23), Word (11), Teams (12), SharePoint (9), OneDrive (14), OneNote (8), To Do (9)
- **Token Refresh:** Automatic (uses refresh_token)

#### 3. **Pinecone** (API Key)
- **What Users Need:** Pinecone account, API key, index name, environment
- **Setup Process:** Add via Connections modal → Enter API key + index name
- **Stored In:** `user_platform_credentials` table (JSONB)
- **Injected As:** `Pinecone` client object
- **Tools Available:** 8 tools (query, upsert, delete, fetch, update, stats, namespaces, upload document)
- **Additional:** Requires OpenAI API key for embeddings

#### 4. **OpenAI** (API Key)
- **What Users Need:** OpenAI account, API key from platform.openai.com
- **Setup Process:** Add via Connections modal → Enter API key
- **Stored In:** `user_platform_credentials` table (JSONB)
- **Injected As:** API key string (set as `openai.api_key`)
- **Tools Available:** Used by Pinecone for embeddings, AI tools for completions
- **Cost:** Pay-per-use (GPT-4 > GPT-3.5 > embeddings)

#### 5. **Anthropic** (API Key)
- **What Users Need:** Anthropic account, API key from console.anthropic.com
- **Setup Process:** Add via Connections modal → Enter API key
- **Stored In:** `user_platform_credentials` table (JSONB)
- **Injected As:** API key string
- **Tools Available:** Claude AI model calls (200K context window)
- **Cost:** Pay-per-use (Claude Opus > Sonnet > Haiku)

#### 6. **Xero** (OAuth 2.0 + Webhooks)
- **What Users Need:** Xero account, developer app created, OAuth configured
- **Setup Process:** Create app in Xero Developer Portal → Configure redirect URI → Click Connect
- **Stored In:** `oauth_tokens` table
- **Injected As:** `headers` dict with Bearer token
- **Tools Available:** Accounting APIs (invoices, contacts, payments, etc.)
- **CRITICAL:** Requires webhook setup for real-time data (not just OAuth!)

#### 7. **InHousePrint SQL** (Database)
- **What Users Need:** Database credentials (host, port, username, password)
- **Setup Process:** Add via Connections modal → Enter database details
- **Stored In:** `user_platform_credentials` table (JSONB)
- **Injected As:** `pyodbc.Connection` object
- **Tools Available:** SQL query execution, calculator tools

---

### 🔜 READY TO IMPLEMENT (Need User Credentials)

#### 8. **Slack** (Bot Token)
**Current Status:** Tools exist but need credential injection update

**What Users Need:**
1. Slack workspace (admin access)
2. Create Slack App at api.slack.com/apps
3. Install app to workspace
4. Copy Bot User OAuth Token (starts with `xoxb-`)

**Credentials Format:**
```json
{
  "bot_token": "xoxb-XXXX-XXXX-XXXXXXXXXXXXXXXXXXXX",
  "app_id": "A1234567890",
  "workspace_id": "T1234567890",
  "workspace_name": "My Company"
}
```

**Current Code:**
```python
# slack.py (OLD - reads from environment variable)
def __init__(self):
    self.client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
```

**Needed Change:**
```python
# slack.py (NEW - credential injection)
def _get_slack_client(user_id: int, **kwargs):
    auth_manager = UserAuthManager()
    creds = auth_manager.get_platform_credentials(user_id, 'slack')
    
    from slack_sdk import WebClient
    client = WebClient(token=creds['bot_token'])
    return client

def slack_post_message(channel: str, text: str, **kwargs):
    user_id = kwargs.get('_user_id')
    client = _get_slack_client(user_id)
    return client.chat_postMessage(channel=channel, text=text)
```

**Tools Available:** 8 tools (post message, update, delete, list channels, create channel, invite, upload file, add reaction)

---

#### 9. **Stripe** (API Key)
**Current Status:** Tools exist, likely already have credential injection

**What Users Need:**
1. Stripe account at stripe.com
2. Go to Dashboard → Developers → API keys
3. Choose Test or Live mode
4. Copy Secret Key (starts with `sk_test_` or `sk_live_`)

**Credentials Format:**
```json
{
  "api_key": "sk_test_XXXXXXXXXXXXXXXXXXXX",
  "environment": "test",
  "webhook_secret": "whsec_XXXXXXXXXXXXXXXXXXXX"
}
```

**Tools Available:** 9 tools (create customer, charge, refund, list payments, subscriptions, etc.)

---

#### 10. **Twilio** (Account SID + Auth Token)
**Current Status:** Tools exist, need credential injection

**What Users Need:**
1. Twilio account at twilio.com/console
2. Copy Account SID (starts with `AC`)
3. Copy Auth Token (click "Show" to reveal)
4. Buy phone number ($1-2/month)

**Credentials Format:**
```json
{
  "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "auth_token": "your_auth_token_here",
  "phone_number": "+1234567890"
}
```

**Tools Available:** SMS, voice calls, phone number management

---

#### 11. **Shopify** (API Key + Store URL)
**Current Status:** Tools may exist, need verification

**What Users Need:**
1. Shopify store (store owner or staff account)
2. Go to Admin → Apps → Develop apps
3. Create app → Configure Admin API scopes
4. Install app → Copy Admin API access token

**Credentials Format:**
```json
{
  "api_key": "shpat_1234567890abcdef",
  "store_url": "yourstore.myshopify.com",
  "api_version": "2024-01"
}
```

**Tools Available:** Products, orders, customers, inventory management

---

#### 12-20. **Other API Key Platforms**
- **PayPal:** API credentials from developer.paypal.com
- **AssemblyAI:** API key from assemblyai.com (speech-to-text)
- **Cloudflare:** API token from dash.cloudflare.com
- **Render:** API key from render.com (deployment platform)
- **CloudConvert:** API key from cloudconvert.com (file conversion)
- **Google Analytics:** OAuth or API key
- **Google Cloud Run:** Service account JSON or OAuth
- **Ngrok:** Auth token from ngrok.com (tunneling)
- **Resend:** API key from resend.com (email)
- **WooCommerce:** API key + secret from WooCommerce site

All follow similar pattern:
1. User creates account on platform
2. User generates API key in platform settings
3. User adds credentials via Connections modal
4. Stored in `user_platform_credentials` JSONB column
5. Injected into tools during execution

---

## 🛠️ How Credential Injection Works

### Step-by-Step Flow

#### 1. User Executes Tool via AI Agent
```
User: "Send a Slack message to #general saying 'Hello team!'"
```

#### 2. Agent Worker Identifies Tool
```python
# agent_worker.py
tool_name = 'slack_post_message'
tool_params = {
    'channel': '#general',
    'text': 'Hello team!'
}
```

#### 3. Registry Adds User Context
```python
# registry_v3.py - execute_tool()
result = registry.execute_tool(
    'slack_post_message',
    user_id=14,  # ← User ID from session
    _injected_credentials=True,  # ← Enable injection
    channel='#general',
    text='Hello team!'
)
```

#### 4. Credential Injector Queries Database
```python
# credential_injector.py
def inject_user_credentials_into_tool(user_id, tool_name, tool_function, tool_params):
    # Detect platform from tool name prefix
    if tool_name.startswith('slack_'):
        # Query user_platform_credentials table
        creds = auth_manager.get_platform_credentials(user_id, 'slack')
        # Add to kwargs
        tool_params['_slack_bot_token'] = creds['bot_token']
```

#### 5. Tool Implementation Uses Credentials
```python
# slack.py
def slack_post_message(channel, text, **kwargs):
    # Extract injected credential
    bot_token = kwargs.get('_slack_bot_token')
    
    # Initialize Slack client
    from slack_sdk import WebClient
    client = WebClient(token=bot_token)
    
    # Execute API call
    response = client.chat_postMessage(
        channel=channel,
        text=text
    )
    
    return response
```

#### 6. Result Returns to AI Agent
```python
{
    "success": True,
    "message_ts": "1732789456.123456",
    "channel": "C1234567890",
    "text": "Hello team!"
}
```

---

## 📊 Database Schema Reference

### oauth_tokens Table
```sql
CREATE TABLE ai_infrastructure.oauth_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES ai_infrastructure.users(id),
    platform VARCHAR(50) NOT NULL,        -- 'google', 'microsoft', 'xero'
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expiry TIMESTAMP,
    scope TEXT,
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_valid BOOLEAN DEFAULT TRUE,
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_refreshed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_oauth_tokens_user_platform ON ai_infrastructure.oauth_tokens(user_id, platform);
CREATE INDEX idx_oauth_tokens_expiry ON ai_infrastructure.oauth_tokens(token_expiry);
```

### user_platform_credentials Table
```sql
CREATE TABLE ai_infrastructure.user_platform_credentials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES ai_infrastructure.users(id),
    platform VARCHAR(50) NOT NULL,            -- 'pinecone', 'openai', 'stripe', 'slack', etc.
    credential_type VARCHAR(20) NOT NULL,     -- 'api_key', 'database'
    credential_key VARCHAR(255) NOT NULL,     -- Friendly name
    credential_value TEXT,                    -- Deprecated (legacy single value)
    credentials JSONB NOT NULL,               -- 🔑 Platform-specific JSON (api_key, config, etc.)
    metadata JSONB,                           -- Additional info (created date, notes, etc.)
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_platform_creds_user_platform ON ai_infrastructure.user_platform_credentials(user_id, platform);
CREATE INDEX idx_platform_creds_active ON ai_infrastructure.user_platform_credentials(is_active);
```

---

## 🔍 Checking What's Connected

### Via API
```bash
GET /api/connections
Authorization: Bearer {jwt_token}

Response:
{
  "connections": [
    {
      "id": "oauth_3",
      "platform": "google",
      "credential_type": "oauth",
      "is_active": true,
      "metadata": {
        "email": "user@example.com",
        "scope": "gmail calendar drive"
      }
    },
    {
      "id": "platform_7",
      "platform": "pinecone",
      "credential_type": "api_key",
      "is_active": true,
      "metadata": {
        "index_name": "inhouseprint",
        "environment": "us-east-1"
      }
    }
  ],
  "total_count": 2
}
```

### Via Python
```python
from AI_infrastructure.auth.user_auth import UserAuthManager

auth_manager = UserAuthManager()

# Get all platforms for user
platforms = auth_manager.get_user_platforms(user_id=14)
print(f"Connected platforms: {platforms}")
# Output: ['google', 'microsoft', 'pinecone', 'openai', 'xero', 'inhouseprint_sql']

# Get specific platform credentials
pinecone_creds = auth_manager.get_platform_credentials(user_id=14, platform='pinecone')
print(f"Pinecone config: {pinecone_creds}")
# Output: {'api_key': 'pcsk_...', 'index_name': 'inhouseprint', 'environment': 'us-east-1'}
```

### Via Database Query
```sql
-- OAuth platforms
SELECT 
    platform, 
    email, 
    is_active, 
    token_expiry,
    last_refreshed_at
FROM ai_infrastructure.oauth_tokens
WHERE user_id = 14;

-- API key platforms
SELECT 
    platform, 
    credential_type,
    credential_key,
    credentials->>'api_key' AS api_key_prefix,
    is_active
FROM ai_infrastructure.user_platform_credentials
WHERE user_id = 14;
```

---

## 🚨 Common Issues & Troubleshooting

### Issue 1: "Platform credentials not found"
**Cause:** User hasn't added credentials for that platform  
**Solution:** Go to Account Settings → Connections → Add Connection

### Issue 2: "OAuth token expired"
**Cause:** Access token expired and refresh failed  
**Solution:** System should auto-refresh, but user may need to re-authorize  
**Check:** Look at `is_valid` column in `oauth_tokens` table

### Issue 3: "Invalid API key"
**Cause:** Wrong API key, or key was revoked  
**Solution:** Update credentials in Connections modal  
**Debug:** Test API key directly in platform's API explorer

### Issue 4: "Slack: not_authed error"
**Cause:** Bot token not injected or invalid  
**Solution:** 
1. Check token exists in `user_platform_credentials`
2. Verify token starts with `xoxb-`
3. Ensure tool receives `_user_id` parameter

### Issue 5: "Pinecone: index not found"
**Cause:** Index name wrong or doesn't exist  
**Solution:** 
1. Check index name in Pinecone console
2. Update `index_name` in JSONB credentials
3. Ensure index is in correct environment (us-east-1, etc.)

---

## 🎯 Next Steps for Platform Enablement

### For Slack, Stripe, Twilio, Shopify:

1. **Update Tool Implementations**
   - Replace `os.getenv('PLATFORM_TOKEN')` with credential injection
   - Add `_get_platform_client(user_id, **kwargs)` helper function
   - Extract credentials from `auth_manager.get_platform_credentials()`

2. **Test Credential Storage**
   - Add platform via Connections modal
   - Verify JSONB data structure matches expected format
   - Query `user_platform_credentials` table to confirm

3. **Test Tool Execution**
   - Execute tool with `user_id` and `_injected_credentials=True`
   - Verify API call succeeds
   - Check for proper error handling if credentials missing

4. **Update Documentation**
   - Add platform guidance to Add Connection Modal
   - Document credential requirements
   - Provide setup instructions with links

### Implementation Template:
```python
# tools/implementations/platform.py

from AI_infrastructure.auth.user_auth import UserAuthManager

class PlatformToolsError(Exception):
    pass

def _get_platform_client(user_id: int, **kwargs):
    """Get authenticated platform client"""
    auth_manager = UserAuthManager()
    creds = auth_manager.get_platform_credentials(user_id, 'platform_name')
    
    if not creds or 'api_key' not in creds:
        raise PlatformToolsError(
            "Platform credentials not found. "
            "Please configure in Account Settings → Connections."
        )
    
    # Initialize platform-specific client
    from platform_sdk import Client
    client = Client(api_key=creds['api_key'])
    
    return client

def platform_do_something(param1: str, **kwargs) -> dict:
    """Execute platform action"""
    # Get user_id from kwargs (injected by registry)
    user_id = kwargs.get('_user_id')
    if not user_id:
        raise PlatformToolsError("User authentication required")
    
    # Get authenticated client
    client = _get_platform_client(user_id, **kwargs)
    
    # Execute API call
    result = client.do_something(param1)
    
    return {
        'success': True,
        'data': result
    }
```

---

## 📝 Summary

**For AI agents to connect to platforms, users must:**

1. **OAuth Platforms (Google, Microsoft, Xero):**
   - Click "Connect" button
   - Authorize in browser
   - System stores tokens automatically

2. **API Key Platforms (Slack, Pinecone, Stripe, etc.):**
   - Create account on platform
   - Generate API key in platform settings
   - Add credentials via Connections modal
   - System stores in JSONB format

3. **Database Platforms:**
   - Have database credentials (host, port, user, pass)
   - Add via Connections modal
   - System stores securely

**System automatically:**
- Detects which platform tool needs
- Queries database for user's credentials
- Injects credentials into tool execution
- Refreshes OAuth tokens when expired
- Handles errors gracefully

**Current Status:**
- ✅ 7 platforms fully working (Google, Microsoft, Pinecone, OpenAI, Anthropic, Xero, InHousePrint SQL)
- 🔜 13+ platforms ready (need credential injection code updates)
- 📊 All stored in PostgreSQL (Supabase)
- 🔒 Secure storage with JSONB for flexibility

---

**Last Updated:** November 28, 2025  
**Maintainer:** Gerard Polovina  
**Related Docs:** 
- `PLATFORM_CREDENTIALS_UI_COMPLETE.md`
- `PLATFORM_CREDENTIALS_UX_IMPROVEMENTS.md`
- `AI_infrastructure/auth/credential_injector.py`
