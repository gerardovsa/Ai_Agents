# Xero Connection Requirements - What You Need

**Date:** November 13, 2025  
**Purpose:** Explain Xero authentication requirements for AI agent integration

---

## Quick Answer: What You Need to Connect to Xero

Xero uses **OAuth 2.0** authentication. You need:

1. **Client ID** (public identifier for your app)
2. **Client Secret** (private key - keep secret!)
3. **Tenant ID** (organization ID - obtained after authentication)
4. **Access Token** (temporary token - auto-refreshed)

---

## Current Setup in Your System

### Your Xero Configuration (3 Businesses)

Based on your `xero_routes.py`, you have **3 separate Xero connections**:

```python
BUSINESS_CONFIGS = {
    1: {
        'name': 'InHouse Print',
        'client_id_env': 'XERO_PRINT_CLIENT_ID',
        'client_secret_env': 'XERO_PRINT_CLIENT_SECRET',
        'color': '#00509E'
    },
    2: {
        'name': 'InHouse Publishing',
        'client_id_env': 'XERO_PUB_CLIENT_ID',
        'client_secret_env': 'XERO_PUB_CLIENT_SECRET',
        'color': '#7B2D26'
    },
    3: {
        'name': 'InHouse Signs',
        'client_id_env': 'XERO_SIGNS_CLIENT_ID',
        'client_secret_env': 'XERO_SIGNS_CLIENT_SECRET',
        'color': '#F7941D'
    }
}
```

### Required Environment Variables in `.env.master`

You need **6 environment variables** (2 per business):

```bash
# InHouse Print (Business 1)
XERO_PRINT_CLIENT_ID=your_xero_client_id_here
XERO_PRINT_CLIENT_SECRET=your_xero_client_secret_here

# InHouse Publishing (Business 2)
XERO_PUB_CLIENT_ID=your_xero_client_id_here
XERO_PUB_CLIENT_SECRET=your_xero_client_secret_here

# InHouse Signs (Business 3)
XERO_SIGNS_CLIENT_ID=your_xero_client_id_here
XERO_SIGNS_CLIENT_SECRET=your_xero_client_secret_here
```

---

## How Xero Authentication Works (Your Current System)

### Flow Overview

```
1. Your AI Agent needs to access Xero
   ↓
2. XeroAPIClient gets Client ID + Secret from .env.master
   ↓
3. Requests access token from Xero OAuth2 server
   POST https://identity.xero.com/connect/token
   ↓
4. Receives access token (valid for 30 minutes)
   ↓
5. Gets tenant ID (organization ID)
   GET https://api.xero.com/connections
   ↓
6. Makes API calls with:
   - Authorization: Bearer {access_token}
   - Xero-tenant-id: {tenant_id}
   ↓
7. Token auto-refreshes when expired
```

### Token Lifecycle

```python
# Your system automatically handles tokens:

1. First request → Get new token
2. Token cached for 29 minutes
3. Second request → Use cached token
4. Token expires → Auto-refresh
5. No manual token management needed!
```

---

## What Each Component Does

### 1. Client ID (Public Identifier)

- **What it is:** Like a username for your Xero app
- **Example:** `A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6`
- **Security:** Public, can be visible in code
- **Where to get:** Xero Developer Portal → My Apps → Your App → Configuration

### 2. Client Secret (Private Key)

- **What it is:** Like a password for your Xero app
- **Example:** `Z9Y8X7W6V5U4T3S2R1Q0P9O8N7M6L5K4`
- **Security:** ⚠️ NEVER commit to Git, keep in .env.master only
- **Where to get:** Xero Developer Portal → My Apps → Your App → Configuration

### 3. Access Token (Temporary Authorization)

- **What it is:** Short-lived token proving you're authorized
- **Example:** `eyJhbGciOiJSUzI1NiIsImtpZCI6...` (JWT token)
- **Lifetime:** 30 minutes
- **Security:** Auto-refreshed by your XeroAPIClient
- **How it's obtained:** Automatically via Client Credentials flow

### 4. Tenant ID (Organization Identifier)

- **What it is:** Unique ID for each Xero organization
- **Example:** `a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6` (UUID format)
- **Where it's used:** Required header in every API call: `Xero-tenant-id`
- **How it's obtained:** Automatically from `/connections` endpoint

---

## OAuth 2.0 Flow Types

### Current: Client Credentials Flow (Machine-to-Machine)

Your system uses **Client Credentials** flow:

```python
# What your XeroAPIClient does:
payload = {
    'grant_type': 'client_credentials',  # ← Client credentials flow
    'client_id': self.client_id,
    'client_secret': self.client_secret,
    'scope': 'accounting.transactions accounting.contacts accounting.settings'
}

response = requests.post('https://identity.xero.com/connect/token', data=payload)
access_token = response.json()['access_token']
```

**Pros:**
- ✅ No user interaction needed
- ✅ Works for server-to-server apps
- ✅ Auto-refreshes tokens
- ✅ Simple to implement

**Cons:**
- ❌ Requires app to be approved by Xero
- ❌ Limited to specific scopes
- ❌ Can't access user-specific data

### Alternative: Authorization Code Flow (User Login)

For apps that need user login (not your current setup):

```python
# Step 1: Redirect user to Xero login
authorization_url = (
    'https://login.xero.com/identity/connect/authorize'
    '?response_type=code'
    '&client_id=YOUR_CLIENT_ID'
    '&redirect_uri=YOUR_REDIRECT_URI'
    '&scope=offline_access accounting.transactions'
    '&state=random_state'
)

# Step 2: User logs in, Xero redirects back with code
# http://your-app.com/callback?code=AUTH_CODE&state=random_state

# Step 3: Exchange code for tokens
payload = {
    'grant_type': 'authorization_code',
    'code': auth_code,
    'redirect_uri': redirect_uri,
    'client_id': client_id,
    'client_secret': client_secret
}

response = requests.post('https://identity.xero.com/connect/token', data=payload)
tokens = response.json()
# {
#   'access_token': '...',
#   'refresh_token': '...',  # Can refresh for new tokens
#   'expires_in': 1800
# }
```

**Pros:**
- ✅ Access user-specific data
- ✅ Can request any scope
- ✅ Refresh tokens last 60 days
- ✅ More secure (user approves access)

**Cons:**
- ❌ Requires user interaction
- ❌ More complex to implement
- ❌ Need to store refresh tokens securely

---

## Required OAuth Scopes

Your current scopes (in `xero_routes.py`):

```python
'scope': 'accounting.transactions accounting.contacts accounting.settings'
```

### Scopes You'll Need for Comprehensive Toolkit

Based on the **XERO_COMPREHENSIVE_TOOLKIT_ANALYSIS.md**:

```
# Core Scopes
offline_access                          # Refresh tokens (auth code flow only)
openid profile email                    # User info (auth code flow only)

# Accounting Scopes (YOU HAVE THESE)
accounting.transactions                 # Invoices, bills, payments ✅
accounting.contacts                     # Contacts ✅
accounting.settings                     # Accounts, tracking categories ✅

# Additional Accounting Scopes (YOU NEED THESE)
accounting.reports.read                 # Financial reports (P&L, Balance Sheet)
accounting.journals.read                # Journal entries
accounting.attachments                  # File attachments to invoices/contacts

# Asset Scopes
assets                                  # Fixed assets management
assets.read                             # Read-only assets

# Files Scopes
files                                   # Files API (document management)
files.read                              # Read-only files

# Projects Scopes
projects                                # Projects API (time tracking)
projects.read                           # Read-only projects

# Payroll Scopes (if needed)
payroll.employees                       # Employees
payroll.payruns                         # Pay runs
payroll.payslip                         # Payslips
payroll.timesheets                      # Timesheets
payroll.settings                        # Payroll settings

# Finance Scopes (advanced)
finance.statements.read                 # Financial statements
finance.accountingactivity.read         # Account activity
finance.cashvalidation.read             # Cash validation
```

**To expand your toolkit, update your scope to:**

```python
scope = (
    'accounting.transactions '
    'accounting.contacts '
    'accounting.settings '
    'accounting.reports.read '         # NEW - for reports
    'accounting.journals.read '        # NEW - for journals
    'accounting.attachments '          # NEW - for file attachments
    'files '                           # NEW - for Files API
    'projects '                        # NEW - for Projects API
    'assets '                          # NEW - for Assets API
)
```

---

## Token Storage & Security

### Current: In-Memory Cache (Development Only)

```python
TOKEN_CACHE = {}  # In xero_routes.py
```

**⚠️ WARNING:** This is fine for development but loses tokens on restart!

### Production: Store in Database

For production AI agent system, store tokens in your database:

```python
# Store in user_platform_credentials table
INSERT INTO user_platform_credentials (
    user_id,
    platform,
    access_token,
    refresh_token,    -- If using auth code flow
    token_expiry,
    tenant_id,
    created_at,
    updated_at
) VALUES (
    1,
    'xero',
    'eyJhbGciOiJSUzI1NiIs...',
    'Z9Y8X7W6V5U4T3S2R1Q0...',  -- Optional
    '2025-11-13 15:30:00',
    'a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6',
    NOW(),
    NOW()
);
```

### Token Refresh Strategy

```python
def get_valid_token(user_id, business_id):
    """Get valid access token, refresh if needed"""
    # 1. Get token from database
    token_data = db.query("""
        SELECT access_token, token_expiry, refresh_token
        FROM user_platform_credentials
        WHERE user_id = ? AND platform = 'xero'
    """, user_id)
    
    # 2. Check if expired
    if token_data['token_expiry'] < datetime.now():
        # 3. Refresh token
        new_token = refresh_xero_token(
            token_data['refresh_token'],
            client_id,
            client_secret
        )
        
        # 4. Update database
        db.execute("""
            UPDATE user_platform_credentials
            SET access_token = ?,
                token_expiry = ?,
                updated_at = NOW()
            WHERE user_id = ? AND platform = 'xero'
        """, new_token['access_token'], new_expiry, user_id)
        
        return new_token['access_token']
    
    # 5. Return cached token
    return token_data['access_token']
```

---

## How to Get Xero Credentials

### Step 1: Create Xero Developer Account

1. Go to https://developer.xero.com/
2. Sign up with your Xero account
3. Click "My Apps" in top menu

### Step 2: Create App

1. Click "New app" button
2. Choose app type:
   - **Private App** - For your own use only (simpler)
   - **Public App** - For distributing to other users
3. Fill in app details:
   - **App name:** "AI Agents Integration" (or your choice)
   - **Company or application URL:** Your company website
   - **Redirect URI:** `http://localhost:5001/api/xero/callback` (if using auth code flow)
   - **Scopes:** Select all scopes you need (see above)

### Step 3: Get Credentials

1. After creating app, go to **Configuration** tab
2. Copy **Client ID** → Add to `.env.master` as `XERO_PRINT_CLIENT_ID`
3. Click **Generate a secret** → Copy → Add to `.env.master` as `XERO_PRINT_CLIENT_SECRET`
4. Repeat for each business (Print, Publishing, Signs)

### Step 4: Test Connection

```python
# Run your test script
python test_xero_module.py

# Should see:
# ✅ 6 Xero credentials configured
# ✅ Connection to Xero successful
# ✅ Token obtained and cached
```

---

## Troubleshooting Common Issues

### Issue 1: "Invalid client credentials"

**Cause:** Client ID or Secret is wrong

**Fix:**
1. Check `.env.master` has correct values
2. Verify no extra spaces or quotes
3. Regenerate secret in Xero Developer Portal if needed

### Issue 2: "Insufficient scope"

**Cause:** Your app doesn't have permission for that API

**Fix:**
1. Go to Xero Developer Portal → Your App → Configuration
2. Add required scopes
3. Reconnect (may require re-authorization)

### Issue 3: "No Xero organizations found"

**Cause:** No organizations connected to your app

**Fix:**
1. Log into Xero with organization account
2. Go to Settings → Connected Apps
3. Authorize your app to access organization

### Issue 4: "Token expired"

**Cause:** Access token expired (30 min lifetime)

**Fix:**
- Your `XeroAPIClient` should auto-refresh
- Check token cache is working
- Verify `get_access_token()` is being called

---

## Summary: What You Actually Need

### Minimal Setup (Current System)

```bash
# .env.master
XERO_PRINT_CLIENT_ID=your_client_id_here
XERO_PRINT_CLIENT_SECRET=your_client_secret_here
XERO_PUB_CLIENT_ID=your_client_id_here
XERO_PUB_CLIENT_SECRET=your_client_secret_here
XERO_SIGNS_CLIENT_ID=your_client_id_here
XERO_SIGNS_CLIENT_SECRET=your_client_secret_here
```

### Everything Else is Automatic

✅ Access tokens - Auto-generated  
✅ Tenant IDs - Auto-fetched  
✅ Token refresh - Auto-handled  
✅ API calls - Auto-authenticated  

### For AI Agent Tool System

Update `credential_injector.py` to inject Xero tokens:

```python
def get_xero_credentials(self, user_id: int, business_id: int = 1) -> Dict[str, str]:
    """Get Xero credentials for user"""
    # Get from database or generate new token
    xero_client = XeroAPIClient(business_id)
    access_token = xero_client.get_access_token()
    tenant_id = xero_client.get_tenant_id()
    
    return {
        'access_token': access_token,
        'tenant_id': tenant_id,
        'business_id': business_id
    }
```

Then tools can use:

```python
def xero_get_invoices(**kwargs):
    """Get invoices from Xero"""
    # Credentials injected automatically
    access_token = kwargs.get('access_token')
    tenant_id = kwargs.get('tenant_id')
    
    # Make API call
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Xero-tenant-id': tenant_id
    }
    response = requests.get(
        'https://api.xero.com/api.xro/2.0/Invoices',
        headers=headers
    )
    return response.json()
```

---

## Additional Resources

- **Xero OAuth 2.0 Guide:** https://developer.xero.com/documentation/guides/oauth2/overview
- **Xero API Reference:** https://developer.xero.com/documentation/api/api-overview
- **Xero Developer Portal:** https://developer.xero.com/app/manage
- **OAuth 2.0 Playground:** https://developer.xero.com/documentation/guides/oauth2/auth-flow

---

**Last Updated:** November 13, 2025  
**Status:** Complete  
**Your Current Setup:** Client Credentials flow with 3 businesses configured
