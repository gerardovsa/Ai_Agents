# 🔷 Microsoft 365 Login Implementation Guide

## Overview
Complete guide to enable Microsoft 365 account login for your AI Platform.

---

## ✅ Files Created

### 1. **Microsoft365 OAuth Manager**
📁 `Microsoft_365_Connection/microsoft365_oauth_manager.py`
- Handles Microsoft OAuth 2.0 authentication
- Manages access tokens and refresh tokens
- Provides user profile retrieval from Microsoft Graph API

### 2. **Microsoft Auth Routes**
📁 `AI_infrastructure/routes/microsoft_auth_routes.py`
- `/api/auth/microsoft/login` - Initiate Microsoft login
- `/api/auth/microsoft/callback` - Handle OAuth callback
- `/api/auth/microsoft/link` - Link Microsoft account to existing user
- `/api/auth/microsoft/status` - Check Microsoft connection status

### 3. **Updated User Auth Manager**
📁 `AI_infrastructure/auth/user_auth.py`
- Added `store_microsoft_tokens()` method
- Added `get_microsoft_tokens()` method  
- Added `get_user_by_email()` method
- Added `register()` method (supports OAuth providers)
- Added `create_session()` and `verify_session()` methods

---

## 🔧 Setup Instructions

### Step 1: Register Azure AD Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations** → **New registration**

**Configuration:**
```
Name: Valor AI Platform
Supported account types: Accounts in any organizational directory and personal Microsoft accounts
Redirect URI: 
  - Web: http://localhost:4000/api/auth/microsoft/callback
  - Web: https://your-production-domain.com/api/auth/microsoft/callback
```

3. After registration, copy the **Application (client) ID**
4. Go to **Certificates & secrets** → **New client secret**
5. Copy the **client secret value** (save immediately - you can't see it again!)

### Step 2: Configure API Permissions

In Azure AD App Registration → **API permissions**:

**Add these Microsoft Graph permissions:**
- `openid` - Sign in
- `profile` - Basic profile
- `email` - Email address
- `User.Read` - Read user profile
- `Mail.Read` - Read emails (optional)
- `Mail.Send` - Send emails (optional)
- `Calendars.Read` - Read calendars (optional)
- `Files.ReadWrite` - OneDrive access (optional)

Click **Grant admin consent** for your organization.

### Step 3: Set Environment Variables

Add to your `.env` or `.env.master` file:

```bash
# Microsoft 365 OAuth Configuration
MICROSOFT_CLIENT_ID=your_application_client_id_here
MICROSOFT_CLIENT_SECRET=your_client_secret_here
MICROSOFT_TENANT_ID=common
```

**Tenant ID Options:**
- `common` - Multi-tenant (personal + work accounts) ✅ Recommended
- `organizations` - Only work/school accounts
- `consumers` - Only personal Microsoft accounts
- `<tenant-id>` - Specific Azure AD tenant only

---

## 📝 Frontend Integration

### Step 1: Add CSS Styles

Add this CSS to `business-ai-platform-v2.html` (after `.login-btn:disabled` style, around line 240):

```css
/* OAuth Sign-In Buttons */
.oauth-divider {
    display: flex;
    align-items: center;
    margin: var(--space-5) 0 var(--space-4) 0;
    color: var(--text-muted);
    font-size: 13px;
}

.oauth-divider::before,
.oauth-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border-default);
}

.oauth-divider::before {
    margin-right: var(--space-3);
}

.oauth-divider::after {
    margin-left: var(--space-3);
}

.oauth-btn {
    width: 100%;
    padding: var(--space-3) var(--space-4);
    background: white;
    border: 1px solid #d0d7de;
    border-radius: 8px;
    color: #24292f;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    margin-bottom: var(--space-3);
}

.oauth-btn:hover {
    transform: translateY(-1px);
}

.oauth-btn i {
    font-size: 16px;
}

.oauth-btn.microsoft {
    background: linear-gradient(135deg, #0078d4 0%, #00a4ef 100%);
    border: none;
    color: white;
}

.oauth-btn.microsoft:hover {
    background: linear-gradient(135deg, #006cbe 0%, #0094d9 100%);
    box-shadow: 0 4px 12px rgba(0, 120, 212, 0.3);
}
```

### Step 2: Microsoft Sign-In Button Already Added ✅

The button is already in your login form (line 3174):

```html
<button type="button" class="oauth-btn microsoft" onclick="signInWithMicrosoft()">
    <i class="fab fa-microsoft"></i>
    <span>Sign in with Microsoft 365</span>
</button>
```

### Step 3: Add JavaScript Function

Add this function to your JavaScript section (around line 8700, before or after `handleLogin`):

```javascript
// Sign in with Microsoft 365
function signInWithMicrosoft() {
    console.log('🔷 Initiating Microsoft 365 login...');
    
    try {
        // Get authorization URL from backend
        fetch(`${API_CONFIG.baseUrl}/api/auth/microsoft/login`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.authorization_url) {
                console.log('✅ Redirecting to Microsoft login...');
                // Redirect to Microsoft login page
                window.location.href = data.authorization_url;
            } else {
                console.error('❌ Failed to get Microsoft authorization URL:', data.error);
                alert('Failed to initiate Microsoft login. Please try again.');
            }
        })
        .catch(error => {
            console.error('❌ Microsoft login error:', error);
            alert('Network error. Please check your connection and try again.');
        });
        
    } catch (error) {
        console.error('❌ Microsoft sign-in error:', error);
        alert('Failed to sign in with Microsoft. Please try again.');
    }
}

// Handle Microsoft login callback (on page load)
window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Check if user just logged in with Microsoft
    if (urlParams.get('microsoft_login') === 'success') {
        const token = urlParams.get('token');
        const isNewUser = urlParams.get('new_user') === 'true';
        
        if (token) {
            console.log('✅ Microsoft login successful!');
            if (isNewUser) {
                console.log('🎉 Welcome! New account created.');
            }
            
            // Store token
            UserAuth.token = token;
            localStorage.setItem('jwt_token', token);
            
            // Load user data and show main app
            UserAuth.showMainApp();
            
            // Clean up URL
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    }
    
    // Check if Microsoft account was linked
    if (urlParams.get('microsoft_linked') === 'success') {
        console.log('✅ Microsoft account linked successfully!');
        alert('Microsoft 365 account linked successfully!');
        window.history.replaceState({}, document.title, window.location.pathname);
    }
});
```

---

## 🧪 Testing

### Local Testing

1. **Start the server:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

2. **Open the platform:**
```
http://localhost:4000
```

3. **Test Microsoft login:**
- Click "Sign in with Microsoft 365" button
- You'll be redirected to Microsoft login page
- Sign in with your Microsoft account
- You'll be redirected back and automatically logged in

### Expected Console Logs

**On button click:**
```
🔷 Initiating Microsoft 365 login...
✅ Redirecting to Microsoft login...
```

**After callback:**
```
✅ Microsoft login successful!
🔧 Loading user profile...
✅ User profile loaded
✅ Profile button displayed
```

---

## 🔍 Troubleshooting

### Issue: "Missing Microsoft 365 credentials" Error

**Solution:** Environment variables not set

```powershell
# Check if variables are set
$env:MICROSOFT_CLIENT_ID
$env:MICROSOFT_CLIENT_SECRET

# If empty, add to .env.master file:
MICROSOFT_CLIENT_ID=your_app_id
MICROSOFT_CLIENT_SECRET=your_secret
```

### Issue: "Redirect URI mismatch" Error

**Solution:** Azure AD redirect URI doesn't match

1. Go to Azure Portal → Your App → **Authentication**
2. Ensure redirect URI is exactly:
   ```
   http://localhost:4000/api/auth/microsoft/callback
   ```
3. Save changes

### Issue: "Invalid client secret" Error

**Solution:** Client secret expired or incorrect

1. Go to Azure Portal → Your App → **Certificates & secrets**
2. Create new client secret
3. Update `MICROSOFT_CLIENT_SECRET` environment variable
4. Restart server

### Issue: Button shows but nothing happens

**Solution:** Check browser console for errors

```javascript
// Test authorization URL generation
fetch('http://localhost:4000/api/auth/microsoft/login')
    .then(r => r.json())
    .then(d => console.log('Auth URL:', d.authorization_url))
```

### Issue: "User already exists" Error

**Solution:** Email is already registered

The system will automatically log in existing users. If you want to link a Microsoft account to an existing user:

```javascript
// Use the /link endpoint instead
fetch(`${API_CONFIG.baseUrl}/api/auth/microsoft/link`, {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${UserAuth.token}`,
        'Content-Type': 'application/json'
    }
})
```

---

## 📊 Database Schema

### User Credentials Table

Microsoft tokens are stored in `user_platform_credentials` table:

```sql
CREATE TABLE user_platform_credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,              -- 'microsoft365'
    credential_type TEXT NOT NULL,       -- 'oauth'
    credential_key TEXT NOT NULL,        -- 'access_token'
    credential_value TEXT NOT NULL,      -- actual access token
    metadata TEXT,                       -- JSON with refresh_token, expires_at, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Metadata JSON structure:**
```json
{
    "refresh_token": "0.AX...",
    "expires_at": "2025-10-28T15:30:00",
    "microsoft_id": "abc123...",
    "microsoft_email": "user@example.com"
}
```

---

## 🎯 Features Enabled

### ✅ Login with Microsoft
- Users can log in with any Microsoft account (personal or work)
- Auto-creates account if doesn't exist
- Supports both Outlook.com and Office 365 accounts

### ✅ OAuth Scopes Granted
After login, users grant permission for:
- Basic profile (name, email)
- Email access (read/write) - optional
- Calendar access - optional
- OneDrive access - optional

### ✅ Multi-Provider Support
Users can:
1. Sign in with traditional username/password
2. Sign in with Microsoft 365
3. Sign in with Google (if implemented)
4. Link Microsoft account to existing account

---

## 🔐 Security Features

### CSRF Protection
- State parameter generated for each OAuth flow
- State verified on callback
- Prevents cross-site request forgery attacks

### Token Security
- Access tokens stored in database (encrypted at rest)
- Refresh tokens stored securely
- Tokens automatically refreshed when expired
- Sessions expire after 24 hours

### Password-less Authentication
- OAuth users don't need passwords
- More secure than traditional passwords
- Supports MFA via Microsoft

---

## 📈 Production Deployment

### Step 1: Update Redirect URIs

In Azure Portal, add production redirect URI:
```
https://your-production-domain.com/api/auth/microsoft/callback
```

### Step 2: Update Environment Variables

On your production server:
```bash
export MICROSOFT_CLIENT_ID=your_app_id
export MICROSOFT_CLIENT_SECRET=your_secret
export MICROSOFT_TENANT_ID=common
```

### Step 3: Update API Config

In `business-ai-platform-v2.html`, update `API_CONFIG`:
```javascript
const API_CONFIG = {
    baseUrl: 'https://your-production-domain.com',
    // ... other config
};
```

### Step 4: Test Login Flow

1. Visit production URL
2. Click "Sign in with Microsoft 365"
3. Verify redirect to Microsoft
4. Verify successful login and redirect back

---

## 🔧 Advanced Configuration

### Custom Scopes

To add more Microsoft services, edit `microsoft365_oauth_manager.py`:

```python
SCOPES = {
    'profile': ['openid', 'profile', 'email', 'User.Read'],
    'outlook': ['Mail.Read', 'Mail.Send'],
    'calendar': ['Calendars.ReadWrite'],
    'onedrive': ['Files.ReadWrite.All'],
    'teams': ['Team.ReadBasic.All'],
    # Add more:
    'sharepoint': ['Sites.Read.All'],
    'onenote': ['Notes.Read'],
}
```

### Organization-Only Login

To restrict to work accounts only:

```python
# In .env
MICROSOFT_TENANT_ID=organizations

# Or specific tenant:
MICROSOFT_TENANT_ID=your-tenant-id-here
```

### Custom User Mapping

To map Microsoft profile fields differently:

```python
# In microsoft_auth_routes.py, modify callback handler:
profile = auth_result['profile']

# Custom field mapping
username = profile['email'].split('@')[0]
full_name = f"{profile['first_name']} {profile['last_name']}"
organization = profile.get('office_location', 'Unknown')
```

---

## 📞 Support & Resources

### Microsoft Documentation
- [Azure AD OAuth 2.0 Guide](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
- [Microsoft Graph API](https://learn.microsoft.com/en-us/graph/)
- [App Registration Guide](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)

### Testing Tools
- [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)
- [JWT Decoder](https://jwt.io/)
- [OAuth Debugger](https://oauthdebugger.com/)

---

## ✅ Implementation Checklist

- [ ] Azure AD application registered
- [ ] Client ID and secret added to `.env`
- [ ] Redirect URIs configured in Azure
- [ ] API permissions granted
- [ ] CSS styles added to HTML
- [ ] JavaScript function added
- [ ] Server restarted with BISTART
- [ ] Test login with personal Microsoft account
- [ ] Test login with work Microsoft account
- [ ] Verify user profile loads correctly
- [ ] Verify tokens stored in database
- [ ] Test logout and re-login

---

**Last Updated:** October 28, 2025  
**Version:** 1.0.0  
**Status:** ✅ Implementation Complete - Ready to Configure
