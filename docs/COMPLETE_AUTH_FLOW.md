# 🔐 Complete Authentication Flow - Google & Microsoft 365

## 📋 Table of Contents

1. [Google OAuth Flow](#google-oauth-flow)
2. [Microsoft 365 OAuth Flow](#microsoft-365-oauth-flow)
3. [Profile Display Flow](#profile-display-flow)
4. [Database Schema](#database-schema)
5. [Function Call Chain](#function-call-chain)

---

## 🔵 Google OAuth Flow

### **Step 1: User Clicks "Sign in with Google"**

**Frontend** (`business-ai-platform-v2.html`)
```javascript
// User clicks button
<button onclick="window.location.href='${API_BASE_URL}/api/auth/google/login'">
    Sign in with Google
</button>
```

**Parameters Sent:**
- None (redirects to backend)

---

### **Step 2: Backend Initiates OAuth**

**Backend** (`google_auth_routes.py:152`)
```python
@google_auth_bp.route('/login')
def google_login():
    # Generate CSRF protection state
    state = secrets.token_urlsafe(32)
    session['google_oauth_state'] = state
    
    # Build authorization URL
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': GOOGLE_REDIRECT_URI,  # http://localhost:5001/api/auth/google/callback
        'response_type': 'code',
        'scope': ' '.join(GOOGLE_SCOPES),
        'state': state,
        'access_type': 'offline',
        'prompt': 'consent'  # ✅ Shows account picker
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{query}"
    return redirect(auth_url)
```

**Parameters:**
- `client_id`: From `GOOGLE_CLIENT_ID` env var
- `redirect_uri`: `http://localhost:5001/api/auth/google/callback`
- `scope`: `openid email profile https://www.googleapis.com/auth/gmail.send ...`
- `state`: Random 32-byte token (CSRF protection)
- `access_type`: `offline` (requests refresh token)
- `prompt`: `consent` (forces account picker)

**Redirects To:** `https://accounts.google.com/o/oauth2/v2/auth?...`

---

### **Step 3: User Authorizes on Google**

**User Actions:**
1. **Account Picker Appears** (due to `prompt=consent`)
2. User selects Google account
3. User grants permissions
4. Google redirects back to callback

**Google Redirects To:**
```
http://localhost:5001/api/auth/google/callback?code=4/XXXX&state=YYYY
```

**Parameters:**
- `code`: Authorization code (single-use)
- `state`: CSRF token (must match session)

---

### **Step 4: Backend Exchanges Code for Tokens**

**Backend** (`google_auth_routes.py:183`)
```python
@google_auth_bp.route('/callback')
def google_callback():
    # Verify state (CSRF protection)
    state = request.args.get('state')
    stored_state = session.get('google_oauth_state')
    if state != stored_state:
        return redirect('/?error=invalid_state')
    
    # Get authorization code
    code = request.args.get('code')
    
    # Exchange code for tokens
    token_data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
    tokens = token_response.json()
    
    access_token = tokens['access_token']      # Short-lived (~1 hour)
    refresh_token = tokens.get('refresh_token')  # Long-lived (optional)
    expires_in = tokens['expires_in']          # 3600 seconds
```

**API Call:**
- **URL**: `https://oauth2.googleapis.com/token`
- **Method**: POST
- **Body**: `code`, `client_id`, `client_secret`, `redirect_uri`, `grant_type`

**Response:**
```json
{
    "access_token": "ya29.a0AfH6SMBx...",
    "refresh_token": "1//0gXXXX",
    "expires_in": 3600,
    "token_type": "Bearer",
    "scope": "openid email profile..."
}
```

---

### **Step 5: Fetch Google User Profile**

**Backend** (`google_auth_routes.py:235`)
```python
# Get user profile from Google
headers = {'Authorization': f'Bearer {access_token}'}
profile_response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
profile = profile_response.json()

email = profile['email']          # john@gmail.com
name = profile['name']            # John Doe
google_id = profile['id']         # 123456789
picture = profile.get('picture')  # https://...
```

**API Call:**
- **URL**: `https://www.googleapis.com/oauth2/v2/userinfo`
- **Method**: GET
- **Headers**: `Authorization: Bearer {access_token}`

**Response:**
```json
{
    "id": "123456789",
    "email": "john@gmail.com",
    "verified_email": true,
    "name": "John Doe",
    "given_name": "John",
    "family_name": "Doe",
    "picture": "https://lh3.googleusercontent.com/..."
}
```

---

### **Step 6: Store User in Database**

**Backend** (`google_auth_routes.py:245`)
```python
# Check if user exists
user_id = get_user_id_by_email(email)

if user_id:
    # Existing user
    cursor.execute('SELECT id, username, email, role FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    username = user['username']
    role = user['role']
else:
    # Auto-register new user
    username = email.split('@')[0]
    cursor.execute(
        'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
        (username, email, 'oauth_google', 'user')
    )
    user_id = cursor.lastrowid
    role = 'user'
```

**Database Operations:**

1. **Check if user exists** (by email)
   - Query: `SELECT id FROM users WHERE email = ?`
   - If exists: Load user data
   - If not exists: Create new user

2. **Insert into `users` table:**
```sql
INSERT INTO users (username, email, password_hash, role) 
VALUES ('john', 'john@gmail.com', 'oauth_google', 'user')
```

**Fields:**
- `username`: From email prefix (`john@gmail.com` → `john`)
- `email`: User's Google email
- `password_hash`: `'oauth_google'` (special marker, no password)
- `role`: `'user'` (default role)

---

### **Step 7: Store Google Credentials**

**Backend** (`google_auth_routes.py:270`)
```python
import json

# Store access token
cursor.execute('''
    INSERT OR REPLACE INTO user_platform_credentials 
    (user_id, platform, credential_type, credential_key, credential_value, is_active, metadata, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
''', (
    user_id, 
    'google',              # Platform
    'oauth',               # Credential type
    'access_token',        # Credential key
    access_token,          # The token
    1,                     # Active
    json.dumps({           # Metadata
        'expires_in': expires_in,
        'profile': profile,
        'created_at': datetime.utcnow().isoformat()
    })
))

# Store refresh token if available
if refresh_token:
    cursor.execute('''
        INSERT OR REPLACE INTO user_platform_credentials 
        (user_id, platform, credential_type, credential_key, credential_value, is_active, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (user_id, 'google', 'oauth', 'refresh_token', refresh_token, 1))
```

**Database Operations:**

1. **Insert access token:**
```sql
INSERT OR REPLACE INTO user_platform_credentials (
    user_id, 
    platform, 
    credential_type, 
    credential_key, 
    credential_value, 
    is_active, 
    metadata, 
    updated_at
) VALUES (
    1,
    'google',
    'oauth',
    'access_token',
    'ya29.a0AfH6SMBx...',
    1,
    '{"expires_in": 3600, "profile": {...}, "created_at": "2025-10-29T10:30:00"}',
    CURRENT_TIMESTAMP
)
```

2. **Insert refresh token:**
```sql
INSERT OR REPLACE INTO user_platform_credentials (
    user_id, 
    platform, 
    credential_type, 
    credential_key, 
    credential_value, 
    is_active, 
    updated_at
) VALUES (
    1,
    'google',
    'oauth',
    'refresh_token',
    '1//0gXXXX',
    1,
    CURRENT_TIMESTAMP
)
```

---

### **Step 8: Generate JWT Token**

**Backend** (`google_auth_routes.py:290`)
```python
# Generate JWT token for frontend session
jwt_token = generate_jwt_token({
    'id': user_id,
    'username': username,
    'email': email,
    'role': role
})
```

**Function** (`auth/user_auth.py:150`)
```python
def generate_jwt_token(user_data):
    payload = {
        'user_id': user_data['id'],
        'username': user_data['username'],
        'email': user_data['email'],
        'role': user_data['role'],
        'exp': datetime.utcnow() + timedelta(days=30)  # Expires in 30 days
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token
```

**JWT Payload:**
```json
{
    "user_id": 1,
    "username": "john",
    "email": "john@gmail.com",
    "role": "user",
    "exp": 1735560000
}
```

---

### **Step 9: Redirect to Frontend**

**Backend** (`google_auth_routes.py:295`)
```python
# Redirect to main app with JWT token
return redirect(f'http://localhost:5001/?token={jwt_token}')
```

**Redirect URL:**
```
http://localhost:5001/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImpvaG4iLCJlbWFpbCI6ImpvaG5AZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJleHAiOjE3MzU1NjAwMDB9.XXXXX
```

---

## 🔷 Microsoft 365 OAuth Flow

### **Step 1: User Clicks "Sign in with Microsoft 365"**

**Frontend** (`business-ai-platform-v2.html`)
```javascript
// User clicks button
<button onclick="window.location.href='${API_BASE_URL}/api/auth/microsoft/login'">
    Sign in with Microsoft 365
</button>
```

**Parameters Sent:**
- None (redirects to backend)

---

### **Step 2: Backend Initiates OAuth**

**Backend** (`microsoft_auth_routes.py:170`)
```python
@microsoft_auth_bp.route('/login', methods=['GET'])
def microsoft_login():
    # Generate CSRF protection state
    state = secrets.token_urlsafe(32)
    session['microsoft_oauth_state'] = state
    
    # Get redirect URI
    redirect_uri = request.url_root.rstrip('/') + '/api/auth/microsoft/callback'
    
    # Get Microsoft authorization URL
    auth_url = get_microsoft_auth_url(redirect_uri=redirect_uri, state=state)
    
    return redirect(auth_url)
```

**Helper Function** (`microsoft365_oauth_manager.py:115`)
```python
def get_authorization_url(self, redirect_uri, state=None, scopes=None):
    params = {
        'client_id': self.client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'response_mode': 'query',
        'scope': ' '.join(scopes or self.scopes),
        'state': state,
        'prompt': 'select_account'  # ✅ ADDED - Forces account picker
    }
    
    query = urllib.parse.urlencode(params)
    auth_url = f"{self.auth_endpoint}?{query}"
    return auth_url
```

**Parameters:**
- `client_id`: From `MICROSOFT_CLIENT_ID` env var
- `redirect_uri`: `http://localhost:5001/api/auth/microsoft/callback`
- `scope`: `openid email profile User.Read Mail.Read Calendar.Read ...`
- `state`: Random 32-byte token (CSRF protection)
- `prompt`: `select_account` (forces account picker) ✅ **THIS IS THE FIX**

**Redirects To:** `https://login.microsoftonline.com/common/oauth2/v2.0/authorize?...`

---

### **Step 3: User Authorizes on Microsoft**

**User Actions:**
1. **Account Picker Appears** (due to `prompt=select_account`) ✅
2. User selects Microsoft account
3. User grants permissions
4. Microsoft redirects back to callback

**Microsoft Redirects To:**
```
http://localhost:5001/api/auth/microsoft/callback?code=M.XXXX&state=YYYY
```

**Parameters:**
- `code`: Authorization code (single-use)
- `state`: CSRF token (must match session)

---

### **Step 4: Backend Exchanges Code for Tokens**

**Backend** (`microsoft_auth_routes.py:231`)
```python
@microsoft_auth_bp.route('/callback', methods=['GET'])
def microsoft_callback():
    # Verify state (CSRF protection)
    state = request.args.get('state')
    stored_state = session.get('microsoft_oauth_state')
    if state != stored_state:
        return jsonify({'error': 'Invalid state'}), 400
    
    # Get authorization code
    code = request.args.get('code')
    
    # Exchange code for tokens and get profile
    redirect_uri = request.url_root.rstrip('/') + '/api/auth/microsoft/callback'
    auth_result = authenticate_user_with_microsoft(code, redirect_uri)
    
    profile = auth_result['profile']
    tokens = auth_result['tokens']
```

**Helper Function** (`microsoft_auth_routes.py:40`)
```python
def authenticate_user_with_microsoft(code, redirect_uri):
    # Exchange code for tokens
    token_data = {
        'client_id': MICROSOFT_CLIENT_ID,
        'client_secret': MICROSOFT_CLIENT_SECRET,
        'code': code,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    token_response = requests.post(MICROSOFT_TOKEN_URL, data=token_data)
    tokens = token_response.json()
    
    access_token = tokens['access_token']
    refresh_token = tokens.get('refresh_token')
    expires_in = tokens.get('expires_in', 3600)
```

**API Call:**
- **URL**: `https://login.microsoftonline.com/common/oauth2/v2.0/token`
- **Method**: POST
- **Body**: `code`, `client_id`, `client_secret`, `redirect_uri`, `grant_type`

**Response:**
```json
{
    "token_type": "Bearer",
    "scope": "User.Read Mail.Read Calendar.Read...",
    "expires_in": 3600,
    "access_token": "eyJ0eXAiOiJKV1QiLCJub25jZSI6...",
    "refresh_token": "M.R3_BAY.-CXXXXXXX"
}
```

---

### **Step 5: Fetch Microsoft User Profile**

**Helper Function** (`microsoft_auth_routes.py:60`)
```python
# Get user profile from Microsoft Graph
headers = {'Authorization': f'Bearer {access_token}'}
profile_response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
profile_data = profile_response.json()

profile = {
    'id': profile_data.get('id'),                    # Microsoft ID
    'email': profile_data.get('mail') or profile_data.get('userPrincipalName'),
    'display_name': profile_data.get('displayName'),  # ✅ ADDED
    'first_name': profile_data.get('givenName'),
    'last_name': profile_data.get('surname')
}

return {
    'success': True,
    'profile': profile,
    'tokens': {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': expires_in
    }
}
```

**API Call:**
- **URL**: `https://graph.microsoft.com/v1.0/me`
- **Method**: GET
- **Headers**: `Authorization: Bearer {access_token}`

**Response:**
```json
{
    "id": "abc123-def456-ghi789",
    "displayName": "John Doe",
    "givenName": "John",
    "surname": "Doe",
    "mail": "john@company.com",
    "userPrincipalName": "john@company.onmicrosoft.com"
}
```

---

### **Step 6: Store User in Database**

**Backend** (`microsoft_auth_routes.py:280`)
```python
# Check if user exists
user_id = get_user_id_by_email(profile['email'])

if user_id:
    # Existing user
    user = db_get_user_by_id(user_id)
    username = user['username']
    role = user['role']
else:
    # Auto-register new user
    username = profile['email'].split('@')[0]
    
    user = db_create_user(
        email=profile['email'],
        username=username,
        role='user'
    )
    user_id = user['id']
```

**Database Function** (`microsoft_auth_routes.py:130`)
```python
def db_create_user(email, username, role='user'):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role, created_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (username, email, 'oauth_microsoft', role))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        'id': user_id,
        'username': username,
        'email': email,
        'role': role
    }
```

**Database Operations:**

1. **Check if user exists** (by email)
   - Query: `SELECT id FROM users WHERE email = ?`
   - If exists: Load user data
   - If not exists: Create new user

2. **Insert into `users` table:**
```sql
INSERT INTO users (username, email, password_hash, role, created_at) 
VALUES ('john', 'john@company.com', 'oauth_microsoft', 'user', CURRENT_TIMESTAMP)
```

**Fields:**
- `username`: From email prefix
- `email`: User's Microsoft email
- `password_hash`: `'oauth_microsoft'` (special marker)
- `role`: `'user'` (default role)

---

### **Step 7: Store Microsoft Credentials**

**Backend** (`microsoft_auth_routes.py:295`)
```python
# Store Microsoft tokens
db_store_microsoft_tokens(
    user_id=user['id'],
    access_token=tokens['access_token'],
    refresh_token=tokens.get('refresh_token', ''),
    expires_in=tokens.get('expires_in', 3600),
    microsoft_id=profile.get('id'),
    microsoft_email=profile.get('email'),
    display_name=profile.get('display_name')  # ✅ ADDED
)
```

**Database Function** (`microsoft_auth_routes.py:80`)
```python
def db_store_microsoft_tokens(user_id, access_token, refresh_token, expires_in, 
                               microsoft_id=None, microsoft_email=None, display_name=None):
    import json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build metadata with profile info
    metadata = {
        'expires_in': expires_in,
        'created_at': datetime.now().isoformat()
    }
    if microsoft_id:
        metadata['microsoft_id'] = microsoft_id
    if microsoft_email:
        metadata['microsoft_email'] = microsoft_email
    if display_name:
        metadata['display_name'] = display_name  # ✅ STORED HERE
    
    # Store access token with profile metadata
    cursor.execute('''
        INSERT OR REPLACE INTO user_platform_credentials 
        (user_id, platform, credential_type, credential_key, credential_value, is_active, metadata, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (user_id, 'microsoft365', 'oauth', 'access_token', access_token, 1, json.dumps(metadata)))
    
    # Store refresh token if available
    if refresh_token:
        cursor.execute('''
            INSERT OR REPLACE INTO user_platform_credentials 
            (user_id, platform, credential_type, credential_key, credential_value, is_active, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, 'microsoft365', 'oauth', 'refresh_token', refresh_token, 1))
    
    conn.commit()
    conn.close()
```

**Database Operations:**

1. **Insert access token:**
```sql
INSERT OR REPLACE INTO user_platform_credentials (
    user_id, 
    platform, 
    credential_type, 
    credential_key, 
    credential_value, 
    is_active, 
    metadata, 
    updated_at
) VALUES (
    1,
    'microsoft365',
    'oauth',
    'access_token',
    'eyJ0eXAiOiJKV1QiLCJub25jZSI6...',
    1,
    '{"expires_in": 3600, "created_at": "2025-10-29T10:30:00", "microsoft_id": "abc123", "microsoft_email": "john@company.com", "display_name": "John Doe"}',
    CURRENT_TIMESTAMP
)
```

2. **Insert refresh token:**
```sql
INSERT OR REPLACE INTO user_platform_credentials (
    user_id, 
    platform, 
    credential_type, 
    credential_key, 
    credential_value, 
    is_active, 
    updated_at
) VALUES (
    1,
    'microsoft365',
    'oauth',
    'refresh_token',
    'M.R3_BAY.-CXXXXXXX',
    1,
    CURRENT_TIMESTAMP
)
```

---

### **Step 8: Generate JWT Token**

**Backend** (`microsoft_auth_routes.py:310`)
```python
# Create JWT session token
jwt_token = db_create_jwt_token(user['id'], user['email'])
```

**Database Function** (`microsoft_auth_routes.py:150`)
```python
def db_create_jwt_token(user_id, email):
    import jwt
    from datetime import datetime, timedelta
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user details
    cursor.execute('SELECT username, role FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    # Generate JWT
    payload = {
        'user_id': user_id,
        'email': email,
        'username': row[0],
        'role': row[1],
        'exp': datetime.utcnow() + timedelta(days=30)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token
```

**JWT Payload:**
```json
{
    "user_id": 1,
    "username": "john",
    "email": "john@company.com",
    "role": "user",
    "exp": 1735560000
}
```

---

### **Step 9: Redirect to Frontend**

**Backend** (`microsoft_auth_routes.py:320`)
```python
# Redirect to frontend with token
return redirect(f"http://localhost:5001/?token={jwt_token}")
```

**Redirect URL:**
```
http://localhost:5001/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImpvaG4iLCJlbWFpbCI6ImpvaG5AY29tcGFueS5jb20iLCJyb2xlIjoidXNlciIsImV4cCI6MTczNTU2MDAwMH0.XXXXX
```

---

## 🎨 Profile Display Flow

### **Step 10: Frontend Receives JWT Token**

**Frontend** (`business-ai-platform-v2.html:9200`)
```javascript
// On page load, check for token in URL
window.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
        // Store token
        UserAuth.token = token;
        localStorage.setItem('authToken', token);
        
        // Load user profile
        await loadUserProfile();
        
        // Clean URL (remove token)
        window.history.replaceState({}, document.title, window.location.pathname);
    }
});
```

**Parameters:**
- `token`: JWT token from URL parameter

**Actions:**
1. Extract `token` from URL
2. Store in `UserAuth.token` (global variable)
3. Store in `localStorage` for persistence
4. Call `loadUserProfile()`
5. Remove token from URL (security)

---

### **Step 11: Fetch User Profile**

**Frontend** (`business-ai-platform-v2.html:9345`)
```javascript
async function loadUserProfile() {
    console.log('🔧 Loading user profile...');
    
    try {
        // Fetch profile from backend
        const response = await fetch(`${API_BASE_URL}/api/auth/profile`, {
            headers: {
                'Authorization': `Bearer ${UserAuth.token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            const profile = data.profile;
            
            // Save to UserAuth
            UserAuth.user = profile;
            localStorage.setItem('userProfile', JSON.stringify(profile));
            
            // Update UI elements
            const authPlatform = profile.auth_platform;  // 'google' | 'microsoft' | null
            
            // Load platform-specific profile
            if (authPlatform === 'microsoft') {
                await loadMicrosoft365Profile();  // ✅ CALLS MICROSOFT PROFILE LOADER
            } else if (authPlatform === 'google') {
                await loadGoogleWorkspaceProfile();  // Google profile loader
            }
        }
    } catch (error) {
        console.error('❌ Failed to load user profile:', error);
    }
}
```

**API Call:**
- **URL**: `${API_BASE_URL}/api/auth/profile`
- **Method**: GET
- **Headers**: `Authorization: Bearer {jwt_token}`

---

### **Step 12: Backend Returns User Profile**

**Backend** (`auth_routes.py:216`)
```python
@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    try:
        user_id = request.user['user_id']
        
        # Determine authentication platform based on password_hash
        conn = sqlite3.connect('AI_infrastructure/ai_infrastructure.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()
        conn.close()
        
        auth_platform = None
        if user_row and user_row['password_hash']:
            if user_row['password_hash'] == 'oauth_google':
                auth_platform = 'google'
            elif user_row['password_hash'] == 'oauth_microsoft':
                auth_platform = 'microsoft'  # ✅ DETECTS MICROSOFT USER
        
        return jsonify({
            'success': True,
            'profile': {
                **request.user,
                'auth_platform': auth_platform  # ✅ RETURNS PLATFORM
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Response:**
```json
{
    "success": true,
    "profile": {
        "user_id": 1,
        "username": "john",
        "email": "john@company.com",
        "role": "user",
        "auth_platform": "microsoft"  // ✅ KEY FIELD
    }
}
```

---

### **Step 13: Load Microsoft 365 Profile (Frontend)**

**Frontend** (`business-ai-platform-v2.html:9650`)
```javascript
async function loadMicrosoft365Profile() {
    console.log('🔧 Loading Microsoft 365 profile...');
    
    try {
        // Fetch Microsoft status
        const response = await fetch(`${API_BASE_URL}/api/auth/microsoft/status`, {
            headers: {
                'Authorization': `Bearer ${UserAuth.token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success && data.connected) {
            const displayName = data.display_name || 'Microsoft User';
            const email = data.microsoft_email || '';
            
            // Update dropdown UI
            const statusEl = document.getElementById('microsoft365Status');
            if (statusEl) {
                statusEl.innerHTML = `
                    <div style="display: flex; flex-direction: column; gap: 2px;">
                        <span style="color: var(--success-color);">✅ ${displayName}</span>
                        ${email ? `<span style="font-size: 11px; color: var(--text-muted);">${email}</span>` : ''}
                    </div>
                `;
            }
            
            // Mark all services as connected
            updateMicrosoft365ServicesStatus(true);
        }
    } catch (error) {
        console.error('❌ Failed to load Microsoft 365 profile:', error);
    }
}
```

**API Call:**
- **URL**: `${API_BASE_URL}/api/auth/microsoft/status`
- **Method**: GET
- **Headers**: `Authorization: Bearer {jwt_token}`

---

### **Step 14: Backend Returns Microsoft Status**

**Backend** (`microsoft_auth_routes.py:514`)
```python
@microsoft_auth_bp.route('/status', methods=['GET'])
def microsoft_status():
    try:
        # Get current user from JWT
        auth_header = request.headers.get('Authorization')
        jwt_token = auth_header.split(' ')[1]
        user = user_auth_manager.verify_session(jwt_token)
        
        if not user:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        
        # Check Microsoft connection
        microsoft_data = user_auth_manager.get_microsoft_tokens(user['id'])
        
        if microsoft_data:
            # Get profile info from metadata
            microsoft_email = microsoft_data.get('microsoft_email')
            microsoft_id = microsoft_data.get('microsoft_id')
            display_name = microsoft_data.get('display_name', microsoft_email)  # ✅ EXTRACTED
            
            return jsonify({
                'success': True,
                'connected': True,
                'microsoft_email': microsoft_email,
                'microsoft_id': microsoft_id,
                'display_name': display_name,  # ✅ RETURNED
                'avatar_url': f"https://graph.microsoft.com/v1.0/users/{microsoft_id}/photo/$value",
                'token_expires_at': microsoft_data.get('expires_at'),
                'connected_at': microsoft_data.get('created_at')
            })
        else:
            return jsonify({'success': True, 'connected': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Database Query** (`user_auth.py:870`)
```python
def get_microsoft_tokens(self, user_id: int) -> Optional[Dict]:
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT credential_value, metadata, created_at
            FROM user_platform_credentials
            WHERE user_id = ? AND platform = 'microsoft365' AND credential_key = 'access_token'
        ''', (user_id,))
        
        row = cursor.fetchone()
        
        if row:
            access_token = row[0]
            metadata = json.loads(row[1])
            created_at = row[2]
            
            return {
                'access_token': access_token,
                'refresh_token': metadata.get('refresh_token'),
                'expires_at': metadata.get('expires_at'),
                'microsoft_id': metadata.get('microsoft_id'),
                'microsoft_email': metadata.get('microsoft_email'),
                'display_name': metadata.get('display_name'),  # ✅ EXTRACTED FROM METADATA
                'created_at': created_at
            }
        
        return None
```

**Response:**
```json
{
    "success": true,
    "connected": true,
    "microsoft_email": "john@company.com",
    "microsoft_id": "abc123-def456-ghi789",
    "display_name": "John Doe",  // ✅ KEY FIELD
    "avatar_url": "https://graph.microsoft.com/v1.0/users/abc123-def456-ghi789/photo/$value",
    "token_expires_at": "2025-10-29T11:30:00",
    "connected_at": "2025-10-29T10:30:00"
}
```

---

### **Step 15: Update UI with Profile**

**Frontend** (`business-ai-platform-v2.html:9680`)
```javascript
// UI is updated in Step 13 (loadMicrosoft365Profile)

// Result in dropdown:
/*
Microsoft 365 OAuth
✅ John Doe
john@company.com
*/
```

---

## 📊 Database Schema

### **Table: `users`**

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,  -- 'oauth_google' or 'oauth_microsoft' for OAuth users
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Example Rows:**

| id | username | email | password_hash | role | created_at |
|----|----------|-------|---------------|------|------------|
| 1 | john | john@gmail.com | oauth_google | user | 2025-10-29 10:00:00 |
| 2 | jane | jane@company.com | oauth_microsoft | user | 2025-10-29 10:30:00 |

---

### **Table: `user_platform_credentials`**

```sql
CREATE TABLE user_platform_credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,  -- 'google', 'microsoft365', 'slack', etc.
    credential_type TEXT NOT NULL,  -- 'oauth', 'api_key', 'smtp', etc.
    credential_key TEXT NOT NULL,  -- 'access_token', 'refresh_token', 'api_key'
    credential_value TEXT NOT NULL,  -- Encrypted token/key
    is_active INTEGER DEFAULT 1,
    metadata TEXT,  -- JSON with profile info, expiry, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, platform, credential_type, credential_key)
);
```

**Example Rows (Google):**

| id | user_id | platform | credential_type | credential_key | credential_value | metadata |
|----|---------|----------|----------------|----------------|------------------|----------|
| 1 | 1 | google | oauth | access_token | ya29.a0AfH6SMBx... | {"expires_in": 3600, "profile": {...}} |
| 2 | 1 | google | oauth | refresh_token | 1//0gXXXX | null |

**Example Rows (Microsoft):**

| id | user_id | platform | credential_type | credential_key | credential_value | metadata |
|----|---------|----------|----------------|----------------|------------------|----------|
| 3 | 2 | microsoft365 | oauth | access_token | eyJ0eXAiOiJKV1QiLCJub25jZSI6... | {"expires_in": 3600, "microsoft_id": "abc123", "microsoft_email": "jane@company.com", "display_name": "Jane Doe"} |
| 4 | 2 | microsoft365 | oauth | refresh_token | M.R3_BAY.-CXXXXXXX | null |

---

## 🔗 Function Call Chain

### **Google OAuth - Complete Chain**

```
1. User clicks button
   ↓
2. frontend: window.location.href = '/api/auth/google/login'
   ↓
3. backend: google_login() → redirect to Google
   ↓
4. User authorizes on Google
   ↓
5. Google: redirect to /api/auth/google/callback?code=XXX
   ↓
6. backend: google_callback()
   ├── Exchange code for tokens (POST to Google)
   ├── Fetch profile (GET from Google)
   ├── Store user in users table
   ├── Store tokens in user_platform_credentials
   ├── Generate JWT token
   └── redirect(f'/?token={jwt_token}')
   ↓
7. frontend: DOMContentLoaded event
   ├── Extract token from URL
   ├── Store token in localStorage
   └── loadUserProfile()
       ↓
8. frontend: loadUserProfile()
   ├── fetch('/api/auth/profile')
   ├── backend: get_profile() → returns auth_platform='google'
   └── loadGoogleWorkspaceProfile()  (if implemented)
   ↓
9. UI updates with profile info
```

---

### **Microsoft OAuth - Complete Chain**

```
1. User clicks button
   ↓
2. frontend: window.location.href = '/api/auth/microsoft/login'
   ↓
3. backend: microsoft_login() 
   ├── get_microsoft_auth_url(redirect_uri, state)
   │   └── microsoft365_oauth_manager.get_authorization_url()
   │       └── params['prompt'] = 'select_account'  ✅ ACCOUNT PICKER
   └── redirect to Microsoft
   ↓
4. User authorizes on Microsoft (account picker shown ✅)
   ↓
5. Microsoft: redirect to /api/auth/microsoft/callback?code=XXX
   ↓
6. backend: microsoft_callback()
   ├── authenticate_user_with_microsoft(code, redirect_uri)
   │   ├── Exchange code for tokens (POST to Microsoft)
   │   └── Fetch profile (GET from Microsoft Graph)
   │       └── profile['display_name'] = profile_data.get('displayName')  ✅
   ├── db_create_user() or db_get_user_by_id()
   ├── db_store_microsoft_tokens()
   │   └── metadata['display_name'] = display_name  ✅ STORED
   ├── db_create_jwt_token()
   └── redirect(f'/?token={jwt_token}')
   ↓
7. frontend: DOMContentLoaded event
   ├── Extract token from URL
   ├── Store token in localStorage
   └── loadUserProfile()
       ↓
8. frontend: loadUserProfile()
   ├── fetch('/api/auth/profile')
   ├── backend: get_profile() → returns auth_platform='microsoft'  ✅
   └── loadMicrosoft365Profile()  ✅ CALLS MICROSOFT LOADER
       ↓
9. frontend: loadMicrosoft365Profile()
   ├── fetch('/api/auth/microsoft/status')
   ├── backend: microsoft_status()
   │   ├── user_auth_manager.get_microsoft_tokens(user_id)
   │   │   └── metadata.get('display_name')  ✅ EXTRACTED
   │   └── return display_name, microsoft_email, microsoft_id
   └── Update UI with profile
       └── statusEl.innerHTML = '✅ John Doe\njohn@company.com'  ✅
   ↓
10. UI updates with full profile info ✅
```

---

## 🎯 Key Differences

| Aspect | Google OAuth | Microsoft OAuth |
|--------|-------------|-----------------|
| **Account Picker** | `prompt=consent` | `prompt=select_account` ✅ |
| **Token Endpoint** | `https://oauth2.googleapis.com/token` | `https://login.microsoftonline.com/common/oauth2/v2.0/token` |
| **Profile Endpoint** | `https://www.googleapis.com/oauth2/v2/userinfo` | `https://graph.microsoft.com/v1.0/me` |
| **Profile Fields** | `email`, `name`, `id`, `picture` | `displayName`, `mail`, `id`, `userPrincipalName` ✅ |
| **Password Hash** | `oauth_google` | `oauth_microsoft` |
| **Platform Name** | `google` | `microsoft365` |
| **Status Endpoint** | Not implemented | `/api/auth/microsoft/status` ✅ |
| **Frontend Loader** | `loadGoogleWorkspaceProfile()` | `loadMicrosoft365Profile()` ✅ |

---

## ✅ Recent Fixes Applied

### **Backend Fix: Extract `display_name` from metadata**

**File:** `AI_infrastructure/auth/user_auth.py:902`

```python
# BEFORE:
return {
    'access_token': access_token,
    'refresh_token': metadata.get('refresh_token'),
    'expires_at': metadata.get('expires_at'),
    'microsoft_id': metadata.get('microsoft_id'),
    'microsoft_email': metadata.get('microsoft_email'),
    'created_at': created_at
}

# AFTER: ✅
return {
    'access_token': access_token,
    'refresh_token': metadata.get('refresh_token'),
    'expires_at': metadata.get('expires_at'),
    'microsoft_id': metadata.get('microsoft_id'),
    'microsoft_email': metadata.get('microsoft_email'),
    'display_name': metadata.get('display_name'),  # ✅ ADDED
    'created_at': created_at
}
```

---

### **Frontend Fix: Add profile loader function**

**File:** `UI/business-ai-platform-v2.html:9650`

```javascript
// NEW FUNCTION: ✅
async function loadMicrosoft365Profile() {
    const response = await fetch(`${API_BASE_URL}/api/auth/microsoft/status`, {
        headers: { 'Authorization': `Bearer ${UserAuth.token}` }
    });
    
    const data = await response.json();
    
    if (data.success && data.connected) {
        const displayName = data.display_name || 'Microsoft User';
        const email = data.microsoft_email || '';
        
        // Update UI
        const statusEl = document.getElementById('microsoft365Status');
        statusEl.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 2px;">
                <span style="color: var(--success-color);">✅ ${displayName}</span>
                ${email ? `<span style="font-size: 11px;">${email}</span>` : ''}
            </div>
        `;
        
        updateMicrosoft365ServicesStatus(true);
    }
}
```

---

### **Frontend Fix: Call loader in profile flow**

**File:** `UI/business-ai-platform-v2.html:9495`

```javascript
// BEFORE:
if (authPlatform === 'microsoft') {
    microsoft365Status.innerHTML = '✅ Connected';
    updateMicrosoft365ServicesStatus(true);
}

// AFTER: ✅
if (authPlatform === 'microsoft') {
    await loadMicrosoft365Profile();  // ✅ FETCH & DISPLAY PROFILE
}
```

---

## 📝 Summary

**Google OAuth Flow:**
- ✅ Account picker works (`prompt=consent`)
- ✅ Profile stored in metadata
- ✅ No status endpoint needed (can be added)

**Microsoft OAuth Flow:**
- ✅ Account picker works (`prompt=select_account`) **[FIXED]**
- ✅ Profile stored in metadata (`display_name`) **[FIXED]**
- ✅ Status endpoint returns profile **[FIXED]**
- ✅ Frontend displays profile **[FIXED]**

**Both flows now:**
1. Show account picker ✅
2. Store user profile ✅
3. Display connected account ✅
4. Persist credentials ✅

---

**Last Updated:** October 29, 2025  
**Version:** 1.0.0  
**Status:** ✅ Complete
