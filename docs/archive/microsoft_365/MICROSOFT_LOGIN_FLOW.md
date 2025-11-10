# 🔷 Microsoft 365 Login - Visual Flow Diagram

## Complete Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER CLICKS BUTTON                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Frontend: signInWithMicrosoft()                                        │
│  ├─ Calls: GET /api/auth/microsoft/login                               │
│  └─ Receives: { authorization_url: "https://login.microsoft..." }      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Backend: microsoft_login() route                                       │
│  ├─ Generates CSRF state token                                         │
│  ├─ Builds OAuth authorization URL                                     │
│  │   Scopes: openid, profile, email, User.Read, Mail.Read...          │
│  └─ Returns URL to frontend                                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Frontend: Redirects to Microsoft                                       │
│  └─ window.location.href = authorization_url                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    MICROSOFT LOGIN PAGE                                 │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ 🔷 Sign in to your Microsoft account                              │ │
│  │                                                                    │ │
│  │ Email: _______________________                                    │ │
│  │ Password: _____________________                                   │ │
│  │                                                                    │ │
│  │ [ Sign In ]                                                        │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  User enters Microsoft credentials                                      │
│  (Outlook.com, Hotmail, Office 365, etc.)                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    MICROSOFT CONSENT SCREEN                             │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ 🔷 Valor AI Platform wants to:                                    │ │
│  │                                                                    │ │
│  │ ✓ View your basic profile (name, email)                          │ │
│  │ ✓ Read your email                                                 │ │
│  │ ✓ Send email as you                                               │ │
│  │ ✓ Read your calendars                                             │ │
│  │ ✓ Access your files in OneDrive                                   │ │
│  │                                                                    │ │
│  │ [ Accept ]  [ Cancel ]                                             │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  User clicks Accept to grant permissions                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Microsoft: Redirects back to app                                       │
│  └─ GET /api/auth/microsoft/callback?code=AUTH_CODE&state=STATE        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Backend: microsoft_callback() route                                    │
│  ├─ Verifies state (CSRF protection)                                   │
│  ├─ Exchanges authorization code for tokens                            │
│  │   POST https://login.microsoftonline.com/common/oauth2/v2.0/token  │
│  │   ├─ access_token: "eyJ0eXAiOiJKV1..."                             │
│  │   ├─ refresh_token: "0.AX..."                                      │
│  │   └─ expires_in: 3600                                              │
│  └─ Gets user profile from Microsoft Graph                             │
│      GET https://graph.microsoft.com/v1.0/me                           │
│      Returns: { id, email, displayName, ... }                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Backend: Check if user exists                                          │
│  └─ Query: SELECT * FROM users WHERE email = 'user@microsoft.com'      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
            User Exists?                     New User?
                    │                               │
                    ▼                               ▼
    ┌──────────────────────────┐    ┌──────────────────────────┐
    │  LOGIN EXISTING USER     │    │  AUTO-REGISTER USER      │
    │  ├─ Update Microsoft     │    │  ├─ Create user record   │
    │  │  tokens                    │    │  │  (no password)       │
    │  ├─ Create JWT session   │    │  ├─ Store Microsoft      │
    │  └─ Generate token       │    │  │  tokens                    │
    └──────────────────────────┘    │  ├─ Create JWT session   │
                    │                │  └─ Generate token       │
                    │                └──────────────────────────┘
                    │                               │
                    └───────────────┬───────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Backend: Store Microsoft tokens in database                            │
│  ├─ Table: user_platform_credentials                                   │
│  ├─ platform: 'microsoft365'                                           │
│  ├─ credential_key: 'access_token'                                     │
│  ├─ credential_value: access_token                                     │
│  └─ metadata: { refresh_token, expires_at, microsoft_id }             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Backend: Redirect to frontend with JWT                                 │
│  └─ Redirect: /?microsoft_login=success&token=JWT_TOKEN                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Frontend: Handle callback                                              │
│  ├─ Parse URL parameters                                               │
│  ├─ Extract JWT token                                                  │
│  ├─ Store in UserAuth.token                                            │
│  ├─ Store in localStorage                                              │
│  └─ Call UserAuth.showMainApp()                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Frontend: Load user profile                                            │
│  ├─ GET /api/auth/profile (with JWT token)                            │
│  ├─ Populate user dropdown                                             │
│  │   - Username                                                        │
│  │   - Email                                                           │
│  │   - Role badge                                                      │
│  │   - Microsoft connection status ✅                                  │
│  └─ Show profile button in header                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Frontend: Hide login overlay, show dashboard                           │
│  └─ User is now logged in! 🎉                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Token Lifecycle

```
┌──────────────────────────────────────────────────────────────────┐
│  ACCESS TOKEN LIFECYCLE                                          │
└──────────────────────────────────────────────────────────────────┘

Initial Login
├─ Microsoft issues access_token (expires in 1 hour)
├─ Microsoft issues refresh_token (long-lived)
├─ Backend stores both in database
└─ Access token used for Microsoft Graph API calls

After 1 Hour (Token Expired)
├─ API call fails with 401 Unauthorized
├─ Backend detects expired token
├─ Backend calls Microsoft with refresh_token
├─ Microsoft issues new access_token
├─ Backend updates database
└─ Retry original API call

User Session
├─ JWT session token (expires in 24 hours)
├─ Stored in localStorage
├─ Sent with every API request (Authorization: Bearer)
└─ Automatically re-login if expired
```

---

## Database Schema

```sql
-- Users table (main user accounts)
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,    -- Empty for OAuth users
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP,
    metadata TEXT                    -- JSON: { auth_provider: 'microsoft', full_name: '...' }
);

-- Platform credentials (Microsoft tokens)
CREATE TABLE user_platform_credentials (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,          -- 'microsoft365'
    credential_type TEXT NOT NULL,   -- 'oauth'
    credential_key TEXT NOT NULL,    -- 'access_token'
    credential_value TEXT NOT NULL,  -- actual token
    metadata TEXT,                   -- JSON: { refresh_token, expires_at, microsoft_id, microsoft_email }
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- User sessions (JWT tokens)
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,      -- JWT token
    created_at TIMESTAMP,
    expires_at TIMESTAMP,            -- 24 hours from creation
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Example Data:**

```sql
-- User record
INSERT INTO users VALUES (
    1,
    'john_doe',
    'john.doe@outlook.com',
    '<empty_hash>',
    'user',
    '2025-10-28 10:00:00',
    '{"auth_provider": "microsoft", "full_name": "John Doe", "microsoft_id": "abc123"}'
);

-- Microsoft tokens
INSERT INTO user_platform_credentials VALUES (
    1,
    1,                                  -- user_id
    'microsoft365',                     -- platform
    'oauth',                            -- credential_type
    'access_token',                     -- credential_key
    'eyJ0eXAiOiJKV1QiLCJub...',         -- credential_value
    '{
        "refresh_token": "0.AX...",
        "expires_at": "2025-10-28T11:00:00",
        "microsoft_id": "abc123",
        "microsoft_email": "john.doe@outlook.com"
    }',
    '2025-10-28 10:00:00',
    '2025-10-28 10:00:00'
);

-- Session token
INSERT INTO user_sessions VALUES (
    1,
    1,                                  -- user_id
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',  -- JWT
    '2025-10-28 10:00:00',
    '2025-10-29 10:00:00'               -- 24 hours later
);
```

---

## API Endpoints

```
┌─────────────────────────────────────────────────────────────────┐
│  MICROSOFT AUTHENTICATION ROUTES                                │
└─────────────────────────────────────────────────────────────────┘

GET /api/auth/microsoft/login
├─ Purpose: Initiate Microsoft OAuth login
├─ Headers: None
├─ Response: { success: true, authorization_url: "https://..." }
└─ Frontend: Redirect user to authorization_url

GET /api/auth/microsoft/callback?code=...&state=...
├─ Purpose: Handle OAuth callback from Microsoft
├─ Parameters: code (authorization code), state (CSRF token)
├─ Process:
│  ├─ Verify state
│  ├─ Exchange code for tokens
│  ├─ Get user profile
│  ├─ Create/login user
│  └─ Create JWT session
└─ Redirect: /?microsoft_login=success&token=JWT

POST /api/auth/microsoft/link
├─ Purpose: Link Microsoft account to existing user
├─ Headers: Authorization: Bearer JWT_TOKEN
├─ Response: { success: true, authorization_url: "https://..." }
└─ Frontend: Redirect user to authorization_url

GET /api/auth/microsoft/link-callback?code=...&state=...
├─ Purpose: Handle link callback
├─ Process: Same as login but for existing user
└─ Redirect: /?microsoft_linked=success

GET /api/auth/microsoft/status
├─ Purpose: Check if user has Microsoft connected
├─ Headers: Authorization: Bearer JWT_TOKEN
├─ Response: {
│     success: true,
│     connected: true,
│     microsoft_email: "user@outlook.com",
│     connected_at: "2025-10-28T10:00:00"
│  }
└─ Used by: Profile dropdown to show status
```

---

## Security Features

```
┌──────────────────────────────────────────────────────────────────┐
│  SECURITY MEASURES                                               │
└──────────────────────────────────────────────────────────────────┘

✅ CSRF Protection
   ├─ Random state parameter generated per session
   ├─ Stored in Flask session
   ├─ Verified on callback
   └─ Prevents cross-site request forgery

✅ Token Security
   ├─ Access tokens stored in database (not client-side)
   ├─ Refresh tokens encrypted in metadata
   ├─ JWT secrets in environment variables
   └─ Session tokens expire after 24 hours

✅ OAuth Best Practices
   ├─ Authorization code flow (most secure)
   ├─ PKCE support (future enhancement)
   ├─ Scope-based permissions
   └─ Token refresh without re-login

✅ Database Security
   ├─ Foreign key constraints
   ├─ Unique constraints on emails/tokens
   ├─ No plaintext passwords for OAuth users
   └─ Automatic session cleanup

✅ HTTPS Requirements (Production)
   ├─ All OAuth redirects must use HTTPS
   ├─ Token transmission encrypted
   ├─ Man-in-the-middle protection
   └─ Azure AD enforces HTTPS in production
```

---

## Error Handling

```
┌──────────────────────────────────────────────────────────────────┐
│  COMMON ERRORS & SOLUTIONS                                       │
└──────────────────────────────────────────────────────────────────┘

❌ "Invalid redirect URI"
   Solution: Check Azure AD redirect URI matches:
   http://localhost:4000/api/auth/microsoft/callback

❌ "Invalid client secret"
   Solution: Regenerate client secret in Azure portal

❌ "State parameter mismatch"
   Solution: CSRF protection - user may have refreshed page
   User should restart login flow

❌ "Token expired"
   Solution: Automatic - refresh token used to get new access token

❌ "User not found"
   Solution: Auto-registration creates new user

❌ "Email already exists"
   Solution: User logged in automatically if email matches

❌ "Permission denied"
   Solution: User declined consent - need to retry login
```

---

**This visual guide shows the complete Microsoft 365 login flow from button click to successful authentication! 🔷✨**
