# Complete Login Function Flow Trace
**Date:** November 8, 2025  
**Purpose:** Document where and how new users are added to the system

---

## 📋 Table of Contents
1. [Login Methods](#login-methods)
2. [Microsoft OAuth Flow (printing@inhouseprint.com.au)](#microsoft-oauth-flow)
3. [Google OAuth Flow](#google-oauth-flow)
4. [Traditional Login](#traditional-login)
5. [Where Users Are Created](#where-users-are-created)
6. [Database Tables](#database-tables)

---

## 🔐 Login Methods

The platform supports **3 login methods**:

1. **Microsoft 365 OAuth** (printing@inhouseprint.com.au used this)
2. **Google OAuth**
3. **Traditional Username/Password**

---

## 🔷 Microsoft OAuth Flow (printing@inhouseprint.com.au)

### Frontend (business-ai-platform-v2.html)

**Step 1: User clicks "Sign in with Microsoft 365"**

```javascript
// Line 5918 in business-ai-platform-v2.html
<button type="button" class="oauth-btn microsoft" onclick="signInWithMicrosoft()">
    <i class="fab fa-microsoft"></i>
    <span>Sign in with Microsoft 365</span>
</button>

// Line 8129-8132
function signInWithMicrosoft() {
    console.log('🔷 Initiating Microsoft 365 OAuth login...');
    const backendUrl = window.API_BASE_URL || 'http://localhost:5001';
    window.location.href = `${backendUrl}/api/auth/microsoft/login`;
}
```

**Redirects to:** `http://localhost:5001/api/auth/microsoft/login`

---

### Backend (Flask Routes)

**Step 2: Microsoft Login Endpoint**

**File:** `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py`

```python
# Line 227-285
@microsoft_auth_bp.route('/login', methods=['GET'])
def microsoft_login():
    """
    Initiate Microsoft 365 OAuth login
    
    GET /api/auth/microsoft/login?force_consent=true
    """
    # Generate CSRF state
    state = secrets.token_urlsafe(32)
    session['microsoft_oauth_state'] = state
    
    # Get redirect URI
    redirect_uri = request.url_root.rstrip('/') + '/api/auth/microsoft/callback'
    
    # Get Microsoft authorization URL with ALL scopes
    auth_url = get_microsoft_auth_url(
        redirect_uri=redirect_uri, 
        state=state, 
        prompt='select_account',
        scopes=MICROSOFT_SCOPES
    )
    
    return redirect(auth_url)
```

**Redirects to:** Microsoft's login page (login.microsoftonline.com)

---

**Step 3: User logs in at Microsoft**

User enters credentials at Microsoft's login page.

Microsoft redirects back to: `http://localhost:5001/api/auth/microsoft/callback?code=...&state=...`

---

**Step 4: Microsoft Callback (WHERE USERS ARE CREATED!)**

```python
# Line 288-450+
@microsoft_auth_bp.route('/callback', methods=['GET'])
def microsoft_callback():
    """
    Microsoft OAuth callback endpoint (FIXED VERSION)
    
    This is where NEW USERS are automatically created!
    """
    
    # STEP 1: Verify state (CSRF protection)
    state = request.args.get('state')
    stored_state = session.get('microsoft_oauth_state')
    if state != stored_state:
        return error
    
    # STEP 2: Get authorization code
    code = request.args.get('code')
    
    # STEP 3: Exchange code for tokens
    redirect_uri = request.url_root.rstrip('/') + '/api/auth/microsoft/callback'
    auth_result = authenticate_user_with_microsoft(code, redirect_uri)
    
    profile = auth_result['profile']
    tokens = auth_result['tokens']
    
    # Extract user info
    email = profile.get('email', profile.get('userPrincipalName', ''))
    display_name = profile.get('display_name', profile.get('displayName', ''))
    microsoft_id = profile.get('id', '')
    
    # STEP 4: Get or CREATE user ← THIS IS THE KEY!
    user_id = get_user_id_by_email(email)
    
    if user_id:
        # Existing user
        user = get_user_by_id(user_id)
        logger.info(f"Existing user found: {user['username']} (ID: {user_id})")
    else:
        # ✅ NEW USER - AUTO-REGISTER HERE! ✅
        logger.info(f"🆕 New user - auto-registering: {email}")
        username = email.split('@')[0]  # "printing" from "printing@inhouseprint.com.au"
        
        # ✅ THIS IS WHERE THE USER IS CREATED! ✅
        user = create_user(email=email, username=username, role='user')
        
        if not user:
            return error
        
        user_id = user['id']
        logger.info(f"✅ User created: {user['username']} (ID: {user_id})")
    
    # STEP 5: Store OAuth tokens in database
    cursor.execute('''
        INSERT OR REPLACE INTO oauth_tokens (
            user_id,
            platform,
            access_token,
            refresh_token,
            token_type,
            expires_at,
            scope,
            is_valid,
            profile_name,
            profile_email,
            provider_user_id,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        'microsoft',
        access_token,
        refresh_token,
        token_type,
        expires_at,
        granted_scopes,
        1,  # is_valid
        display_name,
        email,
        microsoft_id,
        now_str,
        now_str
    ))
    
    # STEP 6: Generate JWT token
    jwt_payload = {
        'user_id': user_id,
        'email': email,
        'username': user['username']
    }
    jwt_token = generate_jwt_token(jwt_payload)
    
    # STEP 7: Redirect to frontend with token
    return_url = session.get('microsoft_return_url', '/')
    redirect_url = f"{return_url}?token={jwt_token}"
    
    return redirect(redirect_url)
```

---

### 🎯 THE CREATE_USER FUNCTION (Where Users Are Actually Inserted)

**File:** `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py`  
**Lines:** 166-183

```python
def create_user(email: str, username: str, role: str = 'user'):
    """
    Create new user in database
    
    THIS IS WHERE NEW USERS ARE INSERTED INTO THE DATABASE!
    
    Database: data/ai_infrastructure.db
    Table: users
    """
    try:
        conn = get_db_connection()  # Connects to data/ai_infrastructure.db
        cursor = conn.cursor()
        
        # ✅ INSERT INTO users table
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            username,              # e.g., "printing"
            email,                 # e.g., "printing@inhouseprint.com.au"
            'oauth_microsoft',     # Special marker (no actual password)
            role,                  # 'user' (or 'admin')
            datetime.now().isoformat()  # Current timestamp
        ))
        
        user_id = cursor.lastrowid  # Get auto-generated ID
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Created new user: {email} (ID: {user_id})")
        return get_user_by_email(email)  # Return full user object
        
    except Exception as e:
        logger.error(f"❌ Error creating user: {e}")
        return None
```

**Database Location:** `C:\Users\gpoli\GIT\AI_agents\data\ai_infrastructure.db`

**Table:** `users`

**Columns Inserted:**
- `id` - Auto-generated integer (PRIMARY KEY)
- `username` - Extracted from email (e.g., "printing")
- `email` - Full email address (e.g., "printing@inhouseprint.com.au")
- `password_hash` - Set to "oauth_microsoft" (not a real password)
- `role` - Set to "user" (could be "admin" for master accounts)
- `created_at` - ISO timestamp (e.g., "2025-11-07T13:48:31.976261")

---

### Backend Returns to Frontend

**Step 5: Frontend receives JWT token**

```javascript
// Line 18740-18799 in business-ai-platform-v2.html
async function initializeApp() {
    // Check for OAuth callback token in URL
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');  // JWT token from backend
    
    if (token) {
        console.log('✅ OAuth successful, token received');
        
        // Store token in localStorage
        localStorage.setItem('authToken', token);
        UserAuth.token = token;
        
        // Load user profile from backend
        await loadUserProfile();
        
        // Mark OAuth as connected
        const userProfile = UserAuth.user;
        const authPlatform = userProfile.auth_platform;
        
        if (authPlatform === 'microsoft') {
            localStorage.setItem('oauth_connected_microsoft', 'true');
        }
        
        // Show main app
        await UserAuth.showMainApp();
        
        // Clean URL (remove ?token=...)
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}
```

**User is now logged in!**

---

## 🟢 Google OAuth Flow

**Same pattern as Microsoft OAuth:**

1. **Frontend:** `signInWithGoogle()` → redirects to `/api/auth/google/login`
2. **Backend:** `google_auth_routes_V2_FIXED.py` → `/login` endpoint
3. **Google:** User logs in at Google
4. **Backend:** `/callback` endpoint → **creates user if new**
5. **Frontend:** Receives JWT token → logged in

**File:** `AI_infrastructure/routes/google_auth_routes_V2_FIXED.py`

**Same create_user() pattern:**
```python
# In Google callback
user_id = get_user_id_by_email(email)
if not user_id:
    # NEW USER - auto-register
    username = email.split('@')[0]
    user = create_user(email=email, username=username, role='user')
    user_id = user['id']
```

---

## 🔑 Traditional Login (Username/Password)

**File:** `AI_infrastructure/routes/auth_routes.py`

**Registration Endpoint:**

```python
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register new user
    
    POST /api/auth/register
    {
        "username": "gerardo",
        "email": "gerardo@vetsuccessacademy.com",
        "password": "secure_password",
        "role": "admin"  // Optional
    }
    """
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')
    
    result = user_auth_manager.register_user(
        username=username,
        email=email,
        password=password,
        role=role
    )
    
    return jsonify(result), 201
```

**This inserts into the SAME `users` table** but with:
- `password_hash` = bcrypt hashed password (not "oauth_microsoft")
- Manual registration required (not automatic like OAuth)

---

## 📊 Where Users Are Created (Summary)

| Login Method | File | Function | Database | Table |
|--------------|------|----------|----------|-------|
| **Microsoft OAuth** | `microsoft_auth_routes_V2_FIXED.py` | `create_user()` (line 166) | `data/ai_infrastructure.db` | `users` |
| **Google OAuth** | `google_auth_routes_V2_FIXED.py` | `create_user()` (similar) | `data/ai_infrastructure.db` | `users` |
| **Username/Password** | `auth_routes.py` | `register_user()` (via auth manager) | `data/ai_infrastructure.db` | `users` |

**All 3 methods insert into the SAME database and table!**

---

## 🗄️ Database Tables

### Primary Database: `data/ai_infrastructure.db`

**Table: `users`**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Auto-generated user ID |
| `username` | TEXT NOT NULL | Username (e.g., "printing") |
| `email` | TEXT NOT NULL | Email address (UNIQUE) |
| `password_hash` | TEXT NOT NULL | Bcrypt hash OR "oauth_microsoft" OR "oauth_google" |
| `role` | TEXT | "user" or "admin" |
| `primary_gmail` | TEXT | Primary Gmail (optional) |
| `created_at` | TIMESTAMP | Creation timestamp |
| `last_active` | TIMESTAMP | Last login time |
| `metadata` | TEXT | JSON metadata |
| `is_primary` | BOOLEAN | Is primary account (for linking) |
| `allowed_dashboards` | TEXT | JSON array of allowed dashboards |
| `has_google_oauth` | BOOLEAN | Has Google OAuth linked |
| `has_microsoft_oauth` | BOOLEAN | Has Microsoft OAuth linked |
| `is_active` | BOOLEAN | Account active status |

**Table: `oauth_tokens`**

Stores OAuth access tokens for Google and Microsoft:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Token ID |
| `user_id` | INTEGER | Foreign key to users table |
| `platform` | TEXT | "google" or "microsoft" |
| `access_token` | TEXT | OAuth access token |
| `refresh_token` | TEXT | OAuth refresh token |
| `token_type` | TEXT | "Bearer" |
| `expires_at` | TIMESTAMP | Token expiration |
| `scope` | TEXT | Granted scopes |
| `is_valid` | BOOLEAN | Token validity |
| `profile_name` | TEXT | User's display name |
| `profile_email` | TEXT | User's email |
| `provider_user_id` | TEXT | Provider's user ID |
| `created_at` | TIMESTAMP | Token creation time |
| `updated_at` | TIMESTAMP | Last token update |

---

### Secondary Database: `data/sessions.db`

**Table: `users`** (separate copy for thread management)

This database is used for thread/message storage. Users must be **synced** from `ai_infrastructure.db` to `sessions.db`.

**Sync Script:** `sync_printing_user_to_sessions.py` (we created this)

---

## 🔄 User Creation Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER CLICKS LOGIN BUTTON                     │
│           (Microsoft / Google / Username+Password)               │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (JavaScript)                         │
│  • signInWithMicrosoft() / signInWithGoogle()                   │
│  • Redirects to: /api/auth/microsoft/login                      │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│             BACKEND - Login Endpoint (Flask)                     │
│  • Generates CSRF state token                                    │
│  • Redirects to Microsoft/Google OAuth page                      │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              USER LOGS IN AT MICROSOFT/GOOGLE                    │
│  • User enters credentials                                       │
│  • Microsoft/Google validates                                    │
│  • Redirects to: /api/auth/microsoft/callback?code=...          │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│         BACKEND - Callback Endpoint (Flask)  ★ KEY ★            │
│                                                                   │
│  1. Verify CSRF state                                            │
│  2. Exchange code for access tokens                              │
│  3. Get user profile from Microsoft/Google Graph API            │
│  4. Extract email (e.g., printing@inhouseprint.com.au)          │
│                                                                   │
│  5. Check if user exists:                                        │
│     user_id = get_user_id_by_email(email)                       │
│                                                                   │
│     IF NOT EXISTS:                                               │
│       ┌────────────────────────────────────────────┐            │
│       │ ✅ CREATE NEW USER (AUTO-REGISTER)        │            │
│       │                                             │            │
│       │  username = email.split('@')[0]            │            │
│       │  create_user(email, username, role='user') │            │
│       │                                             │            │
│       │  INSERT INTO users (                       │            │
│       │    username = "printing",                  │            │
│       │    email = "printing@inhouseprint.com.au", │            │
│       │    password_hash = "oauth_microsoft",      │            │
│       │    role = "user",                          │            │
│       │    created_at = now()                      │            │
│       │  )                                          │            │
│       │                                             │            │
│       │  user_id = 14 (auto-generated)             │            │
│       └────────────────────────────────────────────┘            │
│                                                                   │
│  6. Store OAuth tokens in oauth_tokens table                     │
│  7. Generate JWT token for session                               │
│  8. Redirect to frontend with token:                             │
│     /?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...            │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              FRONTEND - Receives JWT Token                       │
│  • localStorage.setItem('authToken', token)                      │
│  • await loadUserProfile()                                       │
│  • UserAuth.showMainApp()                                        │
│  • USER IS NOW LOGGED IN!                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Takeaways

1. **Auto-Registration**: New users are **automatically created** during OAuth callback
2. **No manual registration needed**: User logs in with Microsoft/Google → account created
3. **Single database**: All users go into `data/ai_infrastructure.db` → `users` table
4. **Sync required**: Users must be synced to `sessions.db` for thread persistence
5. **Password field**: Set to "oauth_microsoft" or "oauth_google" (not a real password)
6. **User ID assignment**: Auto-incremented (e.g., User 14 for printing@inhouseprint.com.au)

---

## 📝 For printing@inhouseprint.com.au Specifically

**What happened on November 7, 2025:**

1. User clicked "Sign in with Microsoft 365" in browser
2. Redirected to Microsoft login page
3. Entered Microsoft credentials
4. Microsoft redirected back to Flask backend
5. **Backend auto-created user** in `ai_infrastructure.db`:
   - User ID: **14**
   - Username: **printing**
   - Email: **printing@inhouseprint.com.au**
   - Password: **oauth_microsoft** (marker, not real password)
   - Created: **2025-11-07T13:48:31.976261**
6. User logged in successfully
7. **BUT** user didn't exist in `sessions.db` (used for threads)
8. **We fixed this** by running `sync_printing_user_to_sessions.py`
9. **We transferred threads** from User 1 to User 14

**User is now fully set up and can see all 6 threads!**

---

## 🛠️ Scripts Created (November 8, 2025)

| Script | Purpose |
|--------|---------|
| `search_ai_infrastructure_user.py` | Search for user in ai_infrastructure.db |
| `sync_printing_user_to_sessions.py` | Sync user from ai_infrastructure.db to sessions.db |
| `check_thread_ownership.py` | Check which user owns which threads |
| `transfer_threads_to_printing.py` | Transfer all threads to User 14 |
| `update_thread_assignments.py` | Transfer thread assignments (agent columns) |
| `verify_printing_user_complete.py` | Final verification of complete setup |

**All scripts executed successfully on November 8, 2025.**

---

## ✅ Status: COMPLETE

- ✅ User exists in ai_infrastructure.db (User ID 14)
- ✅ User synced to sessions.db (User ID 14)
- ✅ 6 threads transferred to User 14
- ✅ 3 thread assignments transferred
- ✅ OAuth tokens stored in oauth_tokens table
- ✅ Backend API tested and working
- ✅ Ready for browser testing

**printing@inhouseprint.com.au is fully configured!**

---

**End of Login Flow Trace**
