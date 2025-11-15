# OAuth Authentication Flow - Complete Analysis (November 14, 2025)

## 🔴 THE ROOT PROBLEMS

### Problem 1: Authorization Code Already Redeemed ❌
**Error:** `AADSTS54005: OAuth2 Authorization code was already redeemed`

**Root Cause:** Code is used TWICE in the same request

**Where:**
1. **First use (CORRECT):** Line 383 in `microsoft_auth_routes_V2_FIXED.py`
   ```python
   auth_result = authenticate_user_with_microsoft(code, redirect_uri)
   ```
   This calls `exchange_code_for_tokens(code)` → ✅ Code consumed

2. **Second use (BUG):** Inside `authenticate_user_with_microsoft()` at line 481
   ```python
   microsoft_oauth_manager.store_tokens(user_email, token_result)
   ```
   This stores to FILE system, not database

**The Flow:**
```
User authorizes → Microsoft sends code=ABC123
    ↓
microsoft_auth_routes.py line 383: authenticate_user_with_microsoft(code="ABC123")
    ↓
    → microsoft365_oauth_manager.exchange_code_for_tokens(code="ABC123")
        → POST to https://login.microsoftonline.com/common/oauth2/v2.0/token
        → ✅ Returns access_token, refresh_token
        → Code ABC123 is now CONSUMED (can't reuse)
    ↓
    → microsoft365_oauth_manager.get_user_profile(access_token)
        → ✅ Returns user email, name, etc.
    ↓
    → microsoft365_oauth_manager.store_tokens(email, tokens)
        → Writes to FILE: microsoft_365_tokens/email_at_domain.json
        → ⚠️ NOT stored in database!
    ↓
Returns to microsoft_auth_routes.py with tokens
    ↓
Line 410-426: Try to create user in database
    ↓
    create_user(email, username) → Returns user dict or None
    ↓
    if not user:
        return {"error": "Failed to create user"} ❌
```

---

### Problem 2: Users Table Missing password_hash Column ❌
**Error:** `Failed to create user`

**Root Cause:** Schema mismatch between:
1. **user_auth.py** (lines 154-165): Creates `password_hash TEXT NOT NULL`
2. **microsoft_auth_routes.py** (line 196): INSERT requires `password_hash`

**The Issue:**
```python
# user_auth.py _init_tables() creates:
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,    ← REQUIRED!
    role TEXT DEFAULT 'user',
    ...
)

# microsoft_auth_routes.py create_user() inserts:
INSERT INTO users (username, email, password_hash, role, created_at)
VALUES (?, ?, ?, ?, ?)
```

**But on Render:** The table doesn't exist yet, OR it was created without `NOT NULL` constraint on `password_hash`!

---

### Problem 3: Database Initialization Race Condition ⚠️
**Error:** Multiple initialization points creating schema conflicts

**Locations that create tables:**

1. **user_auth.py line 146** - `_init_tables()` called by `UserAuthManager.__init__()`
   - Creates: `users`, `user_gmail_accounts`, `user_sessions`, `user_platform_credentials`, `workspaces`
   - Does NOT create: `oauth_tokens`

2. **microsoft_auth_routes.py line 256** - `init_db()` called on module import
   - Creates: `oauth_tokens` (24 columns)
   - Does NOT create: `users`

3. **google_auth_routes.py line ???** - Similar `init_db()` 
   - Creates: `oauth_tokens` (potentially different schema)

**The Race Condition:**
```
Gunicorn starts with 2 workers:
    ↓
Worker 1: Import microsoft_auth_routes → init_db() → Create oauth_tokens
Worker 2: Import user_auth → _init_tables() → Create users
    ↓
PROBLEM: No coordination between workers
RESULT: Tables created in random order, potential schema conflicts
```

---

## 📊 CURRENT DATABASE SCHEMA (What SHOULD Exist)

### users table (from user_auth.py)
```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,           -- ⚠️ NOT NULL!
    role TEXT DEFAULT 'user',
    primary_gmail TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);
```

### oauth_tokens table (from microsoft_auth_routes.py)
```sql
CREATE TABLE IF NOT EXISTS oauth_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,                -- 'microsoft' or 'google'
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_type TEXT DEFAULT 'Bearer',
    expires_at TIMESTAMP,
    scope TEXT,
    is_valid INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1,
    auto_refresh_enabled INTEGER DEFAULT 1,
    last_refreshed_at TIMESTAMP,
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email TEXT,                            -- User's email from OAuth provider
    profile_name TEXT,
    profile_picture_url TEXT,
    profile_data TEXT,
    granted_scopes TEXT,
    auth_method TEXT DEFAULT 'oauth2',
    metadata TEXT,
    UNIQUE(user_id, platform),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## 🔧 THE CORRECT OAUTH FLOW (What SHOULD Happen)

### Step 1: User Clicks "Login with Microsoft"
```
Frontend → GET /api/auth/microsoft/login
    ↓
microsoft_auth_routes.py line 263-280
    ↓
Generate state token → Store in session
    ↓
Redirect to: https://login.microsoftonline.com/common/oauth2/v2.0/authorize?
    client_id=...
    redirect_uri=https://ai-agents-backend-singapore.onrender.com/api/auth/microsoft/callback
    scope=openid profile email User.Read Mail.Read Mail.Send
    state=random_token_12345
```

### Step 2: User Authorizes on Microsoft
```
Microsoft authorization page
    ↓
User clicks "Accept"
    ↓
Microsoft redirects to: https://ai-agents-backend-singapore.onrender.com/api/auth/microsoft/callback?
    code=ABC123_authorization_code
    state=random_token_12345
```

### Step 3: Exchange Code for Tokens (ONCE!)
```
microsoft_auth_routes.py line 383
    ↓
authenticate_user_with_microsoft(code="ABC123", redirect_uri="...")
    ↓
    microsoft365_oauth_manager.exchange_code_for_tokens(code="ABC123")
        ↓
        POST https://login.microsoftonline.com/common/oauth2/v2.0/token
        Body: {
            grant_type: "authorization_code",
            code: "ABC123",
            redirect_uri: "...",
            client_id: "...",
            client_secret: "..."
        }
        ↓
        Response: {
            access_token: "eyJ0eXAi...",
            refresh_token: "0.AXoA...",
            expires_in: 3599,
            token_type: "Bearer"
        }
        ↓
        ⚠️ CODE "ABC123" IS NOW CONSUMED - CANNOT REUSE!
```

### Step 4: Get User Profile
```
microsoft365_oauth_manager.get_user_profile(access_token)
    ↓
    GET https://graph.microsoft.com/v1.0/me
    Headers: Authorization: Bearer eyJ0eXAi...
    ↓
    Response: {
        id: "a1b2c3d4...",
        email: "user@company.com",
        displayName: "John Doe"
    }
```

### Step 5: Check if User Exists in Database
```
get_user_id_by_email("user@company.com")
    ↓
    SELECT id FROM users WHERE email = 'user@company.com'
    ↓
    If EXISTS: user_id = 5
    If NOT EXISTS: user_id = None
```

### Step 6: Create User if New
```
If user_id is None:
    ↓
    create_user(email="user@company.com", username="user", role="user")
        ↓
        Check if email already exists (duplicate check)
        Check if username already exists (collision check)
        ↓
        INSERT INTO users (username, email, password_hash, role, created_at)
        VALUES ('user', 'user@company.com', 'oauth_microsoft', 'user', CURRENT_TIMESTAMP)
        ↓
        ⚠️ PROBLEM: password_hash is NOT NULL!
        ⚠️ SOLUTION: Use 'oauth_microsoft' as placeholder
        ↓
        user_id = cursor.lastrowid
        ↓
        Return user dict: {id: 10, username: 'user', email: 'user@company.com', ...}
```

### Step 7: Store OAuth Tokens in Database
```
INSERT OR REPLACE INTO oauth_tokens (
    user_id,
    platform,
    access_token,
    refresh_token,
    token_type,
    expires_at,
    scope,
    email,
    profile_name,
    metadata,
    ...
) VALUES (
    10,                                    -- user_id
    'microsoft',                           -- platform
    'eyJ0eXAi...',                        -- access_token
    '0.AXoA...',                          -- refresh_token
    'Bearer',                             -- token_type
    '2025-11-14 13:23:09',               -- expires_at (now + 3599 seconds)
    'openid profile email User.Read...',  -- scope
    'user@company.com',                   -- email
    'John Doe',                           -- profile_name
    '{"microsoft_id": "a1b2c3d4..."}',   -- metadata (JSON)
    ...
)
```

### Step 8: Generate JWT Token for Session
```
generate_jwt_token({user_id: 10, email: 'user@company.com'})
    ↓
    payload = {
        user_id: 10,
        email: 'user@company.com',
        exp: 1700000000  # Unix timestamp (now + 24 hours)
    }
    ↓
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    ↓
    Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Step 9: Store Session in Database
```
INSERT INTO user_sessions (user_id, token, ip_address, user_agent, expires_at)
VALUES (10, 'eyJhbGciOi...', '203.12.34.56', 'Mozilla/5.0...', '2025-11-15 12:23:09')
```

### Step 10: Redirect to Frontend with JWT
```
Redirect to: https://ai-agents-backend-singapore.onrender.com/?
    token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    success=true

Frontend receives token → Store in localStorage → Load user profile
```

---

## 🐛 WHAT'S ACTUALLY HAPPENING (The Bugs)

### Actual Flow on Render:
```
1. User clicks "Login with Microsoft" ✅
2. Redirect to Microsoft ✅
3. User authorizes ✅
4. Microsoft redirects with code=ABC123 ✅
5. authenticate_user_with_microsoft(code="ABC123") ✅
    → exchange_code_for_tokens(code="ABC123") ✅ CODE CONSUMED
    → get_user_profile(access_token) ✅
    → store_tokens(email, tokens) ✅ Stored to FILE (not database!)
6. Returns to callback route ✅
7. get_user_id_by_email("user@company.com") → None (new user)
8. create_user(email, username) → Tries to INSERT
    → ❌ ERROR: users table doesn't exist OR
    → ❌ ERROR: password_hash NOT NULL constraint violation
    → Returns None
9. if not user: return {"error": "Failed to create user"} ❌
10. User sees error message ❌
```

---

## 🔧 THE FIXES NEEDED

### Fix 1: Ensure users Table Exists (CRITICAL)
**File:** `AI_infrastructure/flask_app.py`

**Current code (line 136):**
```python
# Initialize user authentication tables (users, oauth_tokens, etc.)
try:
    from auth.user_auth import user_auth_manager
    log_success(logger, f"User authentication tables initialized at {user_auth_manager.db_path}")
except Exception as e:
    log_error(logger, f"Failed to initialize user authentication: {e}")
```

**Problem:** This only creates tables from `user_auth.py`, NOT `oauth_tokens`!

**Solution:** Add oauth_tokens table to user_auth._init_tables()

---

### Fix 2: Make password_hash Optional for OAuth
**File:** `AI_infrastructure/auth/user_auth.py`

**Change:**
```sql
-- FROM:
password_hash TEXT NOT NULL,

-- TO:
password_hash TEXT,  -- NULL allowed for OAuth users
```

**Or keep NOT NULL and always use 'oauth_microsoft' / 'oauth_google' as placeholder**

---

### Fix 3: Remove Duplicate Token Storage
**File:** `Microsoft_365_Connection/microsoft365_oauth_manager.py`

**Option A:** Remove file-based storage (line 481)
```python
# REMOVE THIS:
microsoft_oauth_manager.store_tokens(user_email, token_result)
```

**Option B:** Keep file storage but don't fail if database storage fails

---

### Fix 4: Consolidate Table Initialization
**Create:** `AI_infrastructure/auth/init_all_tables.py`

```python
def init_all_auth_tables():
    """Initialize ALL authentication tables in correct order"""
    # 1. Create users table (must exist first - foreign keys depend on it)
    # 2. Create oauth_tokens table (depends on users)
    # 3. Create user_sessions table (depends on users)
    # 4. Create user_gmail_accounts table (depends on users)
    # 5. Create user_platform_credentials table (depends on users)
    # 6. Create workspaces table (depends on users)
```

**Call from:** `flask_app.py` ONCE on startup, BEFORE any routes load

---

## ✅ VERIFICATION CHECKLIST

### On Render Logs:
- [ ] See: "User authentication tables initialized"
- [ ] See: "oauth_tokens table initialized"
- [ ] No errors during table creation
- [ ] No "database is locked" errors

### Test OAuth Flow:
- [ ] Click "Login with Microsoft"
- [ ] Authorize on Microsoft
- [ ] Callback receives authorization code
- [ ] Code exchanged for tokens (only once!)
- [ ] User profile retrieved
- [ ] User created in database (or existing user found)
- [ ] OAuth tokens stored in database
- [ ] JWT token generated
- [ ] Session stored
- [ ] Redirect to frontend with token
- [ ] Frontend loads user profile

### Database Checks:
```sql
-- Check users table exists
SELECT name FROM sqlite_master WHERE type='table' AND name='users';

-- Check oauth_tokens table exists
SELECT name FROM sqlite_master WHERE type='table' AND name='oauth_tokens';

-- Check user was created
SELECT * FROM users WHERE email = 'user@company.com';

-- Check OAuth tokens stored
SELECT * FROM oauth_tokens WHERE user_id = 10;

-- Check session stored
SELECT * FROM user_sessions WHERE user_id = 10;
```

---

## 🎯 IMMEDIATE ACTION ITEMS

1. **Move oauth_tokens table creation to user_auth.py** (with users table)
2. **Make password_hash nullable** or always use 'oauth_microsoft' placeholder
3. **Remove duplicate token storage** (file vs database)
4. **Test locally first** before pushing to Render
5. **Add comprehensive logging** to trace exact failure point

---

**Status:** ANALYSIS COMPLETE - Ready to implement fixes
**Next:** Implement fixes and test locally
