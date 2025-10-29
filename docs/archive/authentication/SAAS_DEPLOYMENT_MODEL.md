# 🏢 SaaS Deployment Model - Multi-Tenant Architecture

## 🎯 The Critical Question

**"If clients authenticate with their own emails, do I still need my service account?"**

**Answer: YES! You need BOTH - Here's why...**

---

## 🔑 Two-Tier Authentication (Both Required!)

### Tier 1: Service Account (YOURS - Backend Infrastructure)

**What it's for:**
- Backend infrastructure operations
- Platform-wide functionality
- System operations that don't need client data
- Default fallback authentication

**Examples of Service Account Usage:**
```python
# 1. Platform Health Checks
def check_workspace_connectivity():
    """Verify Google Workspace APIs are accessible"""
    service = build_calendar_service()  # Service account
    # Check if APIs are working
    
# 2. Platform Analytics
def get_platform_usage_stats():
    """Track platform-wide metrics"""
    # Count total documents created across all clients
    # Service account doesn't access client data, just platform data

# 3. System Monitoring
def verify_api_quotas():
    """Check if we're hitting rate limits"""
    service = build_gmail_service()  # Service account
    # Monitor API usage

# 4. Default Testing
CHAT Create a test document  # No user specified
# Uses service account for YOUR testing
```

**Where it lives:**
```
Render.com Environment Variables:
├── GOOGLE_APPLICATION_CREDENTIALS=/opt/render/.../credentials.json
├── SERVICE_ACCOUNT_EMAIL=vsa-anythingllm@...
└── (Available to ALL instances/containers)
```

---

### Tier 2: OAuth Tokens (CLIENTS - Personal Data Access)

**What it's for:**
- Accessing client's personal Google Workspace data
- Creating files in client's Drive
- Sending emails from client's Gmail
- Managing client's Calendar/Tasks

**Examples of OAuth Usage:**
```python
# 1. Client Creates Document
# Client: john@company-a.com logs in
# Client: "Create a marketing plan"
create_document("Marketing Plan", user_email="john@company-a.com")
# Uses: john@company-a.com's OAuth token
# Creates: In JOHN'S Google Drive
# Owner: john@company-a.com

# 2. Client Sends Email
# Client: sarah@company-b.com logs in
# Client: "Send email to client about proposal"
send_email(to="client@external.com", user_email="sarah@company-b.com")
# Uses: sarah@company-b.com's OAuth token
# Sends: From SARAH'S Gmail
# Appears in: Sarah's Sent folder

# 3. Client Manages Calendar
# Client: mike@company-c.com logs in
# Client: "Schedule meeting for next Tuesday"
create_event("Team Meeting", user_email="mike@company-c.com")
# Uses: mike@company-c.com's OAuth token
# Creates: In MIKE'S Calendar
```

**Where it lives:**
```
PostgreSQL Database on Render:
├── oauth_tokens table
│   ├── user_email: john@company-a.com
│   │   └── token_encrypted: {...}
│   ├── user_email: sarah@company-b.com
│   │   └── token_encrypted: {...}
│   └── user_email: mike@company-c.com
│       └── token_encrypted: {...}
```

---

## 🏗️ Complete Multi-Tenant Architecture

### Your Render.com Setup

```
┌─────────────────────────────────────────────────────────────┐
│  Render.com - Your Hosted Platform                          │
│  https://your-platform.onrender.com                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🔐 YOUR Service Account (Platform Infrastructure)          │
│     vsa-anythingllm@...iam.gserviceaccount.com              │
│     ├── Used for: Backend operations                        │
│     ├── Stored in: Environment variables                    │
│     └── Access to: YOUR Google Workspace                    │
│                                                              │
│  💾 PostgreSQL Database (Client OAuth Tokens)               │
│     ├── john@company-a.com → token_encrypted                │
│     ├── sarah@company-b.com → token_encrypted               │
│     ├── mike@company-c.com → token_encrypted                │
│     └── ... (unlimited clients)                             │
│                                                              │
│  🔧 Flask App (routes.py)                                   │
│     ├── /signup (Create account)                            │
│     ├── /login (Authenticate user)                          │
│     ├── /oauth/start (Begin Google OAuth)                   │
│     ├── /oauth2callback (Complete OAuth)                    │
│     └── /api/chat (AI agent requests)                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Client Onboarding Flow

### Step-by-Step: How a Client Gets Started

```
1️⃣  Client Visits Your Platform
    https://your-platform.onrender.com
    
    ┌─────────────────────────────┐
    │  Welcome to AI Platform     │
    │                             │
    │  [Sign Up] [Log In]        │
    └─────────────────────────────┘

2️⃣  Client Creates Account
    POST /signup
    {
        "email": "john@company-a.com",
        "password": "...",
        "name": "John Smith"
    }
    
    Database: Create user record
    users table:
    ├── email: john@company-a.com
    ├── password_hash: ...
    ├── oauth_connected: false  ← Not connected yet
    └── created_at: 2025-10-28

3️⃣  Client Logs In
    POST /login
    {
        "email": "john@company-a.com",
        "password": "..."
    }
    
    Flask Session:
    session['user_email'] = 'john@company-a.com'
    session['logged_in'] = True

4️⃣  Platform Prompts: "Connect Google Workspace"
    
    ┌─────────────────────────────────────────┐
    │  Connect Your Google Workspace          │
    │                                         │
    │  To use AI features, please connect     │
    │  your Google account:                   │
    │                                         │
    │  [Connect Google Workspace]             │
    └─────────────────────────────────────────┘
    
    Client clicks button → Redirects to:
    /oauth/workspace/start

5️⃣  OAuth Flow Begins
    
    @app.route('/oauth/workspace/start')
    def oauth_workspace_start():
        # Get logged-in user
        user_email = session.get('user_email')
        
        # Create OAuth flow with UNIFIED scopes
        flow = Flow.from_client_secrets_file(
            'credentials_web.json',
            scopes=UNIFIED_SCOPES  # Gmail, Calendar, Tasks, Forms, Docs, Sheets, Slides, Drive
        )
        
        # Redirect URI (back to your platform)
        flow.redirect_uri = 'https://your-platform.onrender.com/oauth2callback'
        
        # Generate Google authorization URL
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        # Save state for security verification
        session['oauth_state'] = state
        
        # Redirect user to Google
        return redirect(authorization_url)

6️⃣  Google Authorization Screen
    
    Browser redirects to Google:
    https://accounts.google.com/o/oauth2/auth?...
    
    ┌──────────────────────────────────────────┐
    │  🔐 Sign in with Google                  │
    │                                          │
    │  john@company-a.com ▼                   │
    │                                          │
    │  "Your Platform" wants to access:        │
    │                                          │
    │  ✅ Gmail (read, send, modify)          │
    │  ✅ Calendar (read, create events)      │
    │  ✅ Tasks (read, create tasks)          │
    │  ✅ Forms (create, read responses)      │
    │  ✅ Docs (create, edit documents)       │
    │  ✅ Sheets (create, edit sheets)        │
    │  ✅ Slides (create, edit slides)        │
    │  ✅ Drive (manage files)                │
    │                                          │
    │  [ Cancel ]  [ Allow ]                   │
    └──────────────────────────────────────────┘
    
    Client clicks [Allow]

7️⃣  OAuth Callback (Token Exchange)
    
    Google redirects back to your platform:
    https://your-platform.onrender.com/oauth2callback?code=...&state=...
    
    @app.route('/oauth2callback')
    def oauth_callback():
        # Verify state (security check)
        if request.args.get('state') != session.get('oauth_state'):
            return "Invalid state", 400
        
        # Get logged-in user
        user_email = session.get('user_email')
        
        # Exchange authorization code for token
        flow = Flow.from_client_secrets_file(
            'credentials_web.json',
            scopes=UNIFIED_SCOPES,
            state=session['oauth_state']
        )
        flow.redirect_uri = 'https://your-platform.onrender.com/oauth2callback'
        flow.fetch_token(authorization_response=request.url)
        
        # Get credentials (access token, refresh token)
        credentials = flow.credentials
        
        # Encrypt token for security
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat()
        }
        encrypted_token = encrypt_token(json.dumps(token_data))
        
        # Store in database
        db.execute('''
            INSERT INTO oauth_tokens (user_email, token_encrypted, expires_at, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_email) 
            DO UPDATE SET token_encrypted = excluded.token_encrypted,
                          expires_at = excluded.expires_at,
                          updated_at = CURRENT_TIMESTAMP
        ''', (user_email, encrypted_token, credentials.expiry, datetime.now()))
        
        # Update user record
        db.execute('''
            UPDATE users
            SET oauth_connected = true
            WHERE email = ?
        ''', (user_email,))
        
        return redirect('/dashboard?success=Google Workspace connected!')

8️⃣  Client Uses Platform
    
    Client is now fully connected!
    
    ┌─────────────────────────────────────────┐
    │  AI Platform Dashboard                  │
    │                                         │
    │  👤 john@company-a.com                  │
    │  ✅ Google Workspace Connected          │
    │                                         │
    │  💬 Chat with AI:                       │
    │  [Create a marketing plan document]     │
    │                            [Send]       │
    └─────────────────────────────────────────┘
    
    Client types: "Create a marketing plan document"
    
    POST /api/chat
    {
        "message": "Create a marketing plan document",
        "user_email": "john@company-a.com"  ← From session
    }
    
    Backend:
    def handle_chat(message, user_email):
        # Load client's OAuth token from database
        token = load_oauth_token(user_email)
        
        # Use client's token to create document
        doc = create_document(
            "Marketing Plan",
            user_email=user_email  ← Uses JOHN'S token
        )
        
        # Document created in JOHN'S Google Drive!
        return f"Created document: {doc['title']}"
```

---

## 💾 Database Schema

### Complete Multi-Tenant Database Structure

```sql
-- Users table (Platform accounts)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    oauth_connected BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OAuth tokens table (Client Google Workspace access)
CREATE TABLE oauth_tokens (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) UNIQUE NOT NULL,
    token_encrypted TEXT NOT NULL,  -- Encrypted with Fernet
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- Usage tracking (Optional - for analytics)
CREATE TABLE usage_logs (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    action VARCHAR(100),  -- 'create_document', 'send_email', etc.
    resource_type VARCHAR(50),  -- 'document', 'email', 'event'
    resource_id VARCHAR(255),  -- Document ID, Message ID, etc.
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);
```

---

## 🔐 When to Use What?

### Decision Matrix

| Operation | Who | Authentication | Example |
|-----------|-----|----------------|---------|
| **Client creates doc** | John | John's OAuth | `create_document("Plan", user_email="john@company-a.com")` |
| **Client sends email** | Sarah | Sarah's OAuth | `send_email("hi", user_email="sarah@company-b.com")` |
| **Client reads Gmail** | Mike | Mike's OAuth | `get_messages(user_email="mike@company-c.com")` |
| **Platform health check** | System | Service Account | `check_api_status()` (no user_email) |
| **Your testing** | You | Service Account | `CHAT Create test doc` (desktop mode) |
| **Platform analytics** | System | Service Account | `count_total_documents()` (aggregate data) |

---

## 🎯 Why You STILL Need Service Account

### Service Account Use Cases (Even with Client OAuth)

1. **Platform Operations**
   ```python
   # Check if Google APIs are accessible
   def platform_health_check():
       try:
           service = build_calendar_service()  # Service account
           service.calendarList().list().execute()
           return {"status": "healthy"}
       except Exception as e:
           return {"status": "unhealthy", "error": str(e)}
   ```

2. **Your Testing**
   ```bash
   # You can test features without OAuth
   BISTART
   CHAT Create a test document
   # Uses: YOUR service account
   # Quick testing without OAuth flow
   ```

3. **Default Fallback**
   ```python
   def create_document(title, user_email=None):
       if user_email:
           # Client mode: Use their OAuth
           service = build_oauth_service('docs', user_email=user_email)
       else:
           # Fallback: Use service account
           service = build_docs_service()  # Service account
   ```

4. **Background Jobs**
   ```python
   # Scheduled task: Clean up expired tokens
   @scheduler.task('daily')
   def cleanup_expired_tokens():
       # Uses service account to query database
       # Doesn't need client OAuth
       db.execute("DELETE FROM oauth_tokens WHERE expires_at < NOW()")
   ```

---

## 🏢 Multi-Tenant Isolation

### How Client Data Stays Separate

```
Client A (john@company-a.com):
├── OAuth Token A (encrypted in database)
├── Creates document → Uses Token A → Saved in John's Drive
├── Sends email → Uses Token A → From John's Gmail
└── ❌ CANNOT access Sarah's or Mike's data

Client B (sarah@company-b.com):
├── OAuth Token B (encrypted in database)
├── Creates document → Uses Token B → Saved in Sarah's Drive
├── Sends email → Uses Token B → From Sarah's Gmail
└── ❌ CANNOT access John's or Mike's data

Client C (mike@company-c.com):
├── OAuth Token C (encrypted in database)
├── Creates document → Uses Token C → Saved in Mike's Drive
├── Sends email → Uses Token C → From Mike's Gmail
└── ❌ CANNOT access John's or Sarah's data
```

**Isolation guaranteed by:**
- Each client has separate OAuth token
- Token loaded based on `session['user_email']`
- API calls use the authenticated user's token
- No cross-client data leakage possible

---

## 🚀 Deployment Architecture

### Your Render.com Setup

```
┌─────────────────────────────────────────────────────────────┐
│  Render.com Web Service                                     │
│  Instance Type: Standard (auto-scaling)                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📦 Environment Variables:                                  │
│     GOOGLE_APPLICATION_CREDENTIALS=/opt/.../credentials.json│
│     SERVICE_ACCOUNT_EMAIL=vsa-anythingllm@...               │
│     GOOGLE_OAUTH_MODE=web                                   │
│     GOOGLE_OAUTH_CREDENTIALS_FILE_WEB=/opt/.../creds_web.json│
│     DATABASE_URL=postgresql://...                           │
│     ENCRYPTION_KEY=<your-secret-key>                        │
│     SESSION_SECRET=<your-session-secret>                    │
│                                                              │
│  🗄️  PostgreSQL Database (Managed by Render):              │
│     ├── users table (client accounts)                       │
│     ├── oauth_tokens table (client Google Workspace access) │
│     └── usage_logs table (analytics)                        │
│                                                              │
│  🔐 Files Uploaded to Render:                               │
│     ├── credentials.json (Service account - YOUR backend)   │
│     └── credentials_web.json (OAuth app - CLIENT auth)      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 💰 Scaling & Costs

### Client Count vs Storage

| Clients | OAuth Tokens in DB | Your Drive Storage | Client Drive Storage |
|---------|-------------------|-------------------|---------------------|
| 1 client | 1 token (~2KB) | Empty | Client's 15GB |
| 10 clients | 10 tokens (~20KB) | Empty | Each client's 15GB |
| 100 clients | 100 tokens (~200KB) | Empty | Each client's 15GB |
| 1,000 clients | 1,000 tokens (~2MB) | Empty | Each client's 15GB |
| 10,000 clients | 10,000 tokens (~20MB) | Empty | Each client's 15GB |

**Your costs:**
- Database storage: ~2KB per client (negligible)
- Your Google Drive: Empty (no client files)
- API quotas: Shared across all clients (monitor usage)

**Client benefits:**
- Their files in THEIR Drive
- Uses THEIR storage quota
- They own all documents
- Can export/delete at any time

---

## ✅ Final Answer to Your Question

### "Do clients just authenticate when they create profiles?"

**YES! Here's the complete flow:**

1. **Client signs up** on your platform (email + password)
   - Creates account in YOUR database
   - No Google connection yet

2. **Client clicks "Connect Google Workspace"**
   - Redirects to Google OAuth consent screen
   - Client authorizes your app
   - Token saved in YOUR database

3. **Client uses AI features**
   - "Create a document" → Uses THEIR token → In THEIR Drive
   - "Send an email" → Uses THEIR token → From THEIR Gmail
   - "Schedule event" → Uses THEIR token → In THEIR Calendar

### "Do I need my service account at all?"

**YES! For:**
- Platform backend operations
- Your testing (desktop mode)
- Default fallback
- System health checks
- Platform analytics (aggregate data, not client data)

### "I will be hosting it for them on instances"

**Perfect! On Render.com:**
- ONE web service (Flask app)
- ONE PostgreSQL database (stores all client tokens)
- ONE service account (YOUR backend)
- MANY client OAuth tokens (one per client)

---

## 🎯 Summary

**Multi-Tenant SaaS Model:**
```
Your Platform (Render.com):
├── YOUR Service Account (backend infrastructure)
├── Client A's OAuth Token (john@company-a.com)
├── Client B's OAuth Token (sarah@company-b.com)
├── Client C's OAuth Token (mike@company-c.com)
└── ... (unlimited clients)

Each client:
✅ Creates profile with email
✅ Authenticates Google Workspace (OAuth)
✅ Token stored in YOUR database (encrypted)
✅ Files created in THEIR Drive
✅ Complete data isolation
```

**You need BOTH:**
- ✅ **Service Account** = Platform backend operations
- ✅ **OAuth Tokens** = Client personal data access

---

**Last Updated:** October 28, 2025  
**Status:** Complete SaaS Architecture - Ready to Deploy
