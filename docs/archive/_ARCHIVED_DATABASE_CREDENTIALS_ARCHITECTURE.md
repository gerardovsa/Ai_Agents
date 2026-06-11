# Database Credentials Architecture

**Purpose:** Explains the dual-table authentication system and why both `oauth_tokens` and `user_platform_credentials` tables exist.

**Created:** November 15, 2025  
**Status:** Production Architecture Documentation

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication Tables](#authentication-tables)
3. [Why Two Tables?](#why-two-tables)
4. [Use Cases](#use-cases)
5. [Implementation Guide](#implementation-guide)
6. [Security Considerations](#security-considerations)

---

## Overview

The AI Agents platform uses **two separate tables** for storing authentication credentials:

1. **`oauth_tokens`** - OAuth 2.0 tokens (Google, Microsoft, Facebook)
2. **`user_platform_credentials`** - API keys, secrets, and non-OAuth credentials

This separation follows the **Separation of Concerns** principle and accommodates different authentication patterns.

---

## Authentication Tables

### 1. `oauth_tokens` Table

**Database:** `ai_infrastructure.db`  
**Status:** ✅ Active (5 records as of Nov 2025)  
**Purpose:** OAuth 2.0 token lifecycle management

#### Schema:

```sql
CREATE TABLE oauth_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,               -- 'google', 'microsoft', 'facebook'
    access_token TEXT NOT NULL,           -- Short-lived (1 hour)
    refresh_token TEXT,                   -- Long-lived (permanent until revoked)
    token_type TEXT,                      -- 'Bearer'
    expires_at TIMESTAMP,                 -- Token expiration
    scope TEXT,                           -- Granted permissions
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    last_refreshed_at TIMESTAMP,
    
    -- Additional OAuth metadata
    email TEXT,
    account_identifier TEXT,
    account_name TEXT,
    is_primary_account BOOLEAN,
    auto_refresh_enabled BOOLEAN,
    granted_scopes TEXT,
    metadata TEXT,                        -- JSON: profile data, picture, etc.
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### Characteristics:

- **Expires:** ✅ Yes (typically 1 hour)
- **Auto-Refresh:** ✅ Yes (via refresh_token)
- **User Consent:** ✅ Yes (OAuth popup flow)
- **Scope-Based:** ✅ Yes (read/write permissions)
- **Managed By:** OAuth provider (Google, Microsoft)

#### Example Record:

```json
{
  "user_id": 1,
  "platform": "google",
  "access_token": "ya29.a0ATi6K2vd3IKqWwWc2d7LtzYw...",
  "refresh_token": "1//0g9mekHrIb5_6CgYIARAAGBASNwF...",
  "expires_at": "2025-11-13 03:31:43",
  "email": "printing@inhouseprint.com.au",
  "scope": "https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/drive"
}
```

#### Platforms Supported:

- Google Workspace (Gmail, Drive, Docs, Sheets, Calendar)
- Microsoft 365 (Outlook, OneDrive, Teams, SharePoint)
- Facebook (future)
- LinkedIn (future)

---

### 2. `user_platform_credentials` Table

**Database:** `ai_infrastructure.db`  
**Status:** ⚠️ Unused (0 records - reserved for future use)  
**Purpose:** Non-OAuth API keys and custom credentials

#### Schema:

```sql
CREATE TABLE user_platform_credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,               -- 'stripe', 'sendgrid', 'aws', 'github'
    credential_type TEXT NOT NULL,        -- 'api_key', 'secret', 'token', 'password'
    credential_key TEXT NOT NULL,         -- Public key (e.g., Stripe publishable key)
    credential_value TEXT NOT NULL,       -- Private key (encrypted)
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,                        -- JSON: environment, region, etc.
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, platform, credential_type)
);
```

#### Characteristics:

- **Expires:** ❌ No (permanent until manually revoked)
- **Auto-Refresh:** ❌ No (static credentials)
- **User Consent:** ❌ No (user provides directly)
- **Scope-Based:** ❌ No (usually full platform access)
- **Managed By:** User or admin

#### Example Record (Hypothetical):

```json
{
  "user_id": 1,
  "platform": "stripe",
  "credential_type": "api_key",
  "credential_key": "pk_live_51K...",
  "credential_value": "sk_live_51K...",  // ENCRYPTED
  "metadata": {
    "environment": "production",
    "stripe_account_id": "acct_1K...",
    "webhook_secret": "whsec_..."
  }
}
```

#### Platforms Intended For:

- **Payment Processors:** Stripe, PayPal, Square
- **Email Services:** SendGrid, Mailgun, AWS SES
- **SMS Services:** Twilio, Nexmo
- **Cloud Storage:** AWS S3, Azure Blob, DigitalOcean Spaces
- **Version Control:** GitHub personal access tokens
- **Chat Platforms:** Slack bot tokens, Discord webhooks
- **Database Access:** MySQL, PostgreSQL user credentials
- **Custom APIs:** Any REST API with bearer tokens

---

## Why Two Tables?

### Different Authentication Patterns:

| Aspect | OAuth (`oauth_tokens`) | API Keys (`user_platform_credentials`) |
|--------|------------------------|----------------------------------------|
| **Flow** | User redirected to provider → consent screen → callback | User enters key directly in settings |
| **Lifetime** | Short (1 hour) + refresh token | Long (years or permanent) |
| **Refresh** | Automatic (background) | Manual replacement |
| **Revocation** | User can revoke in Google/Microsoft settings | User deletes from platform dashboard |
| **Security** | Provider manages security | Application manages security |
| **Use Case** | User-facing integrations (Gmail, Docs) | Backend integrations (Stripe, AWS) |

### Real-World Example:

**Scenario:** User wants to:
1. Send emails via Gmail → Uses `oauth_tokens` (Google OAuth)
2. Process payments via Stripe → Uses `user_platform_credentials` (Stripe API key)

**Why not merge?**

- OAuth tokens **expire hourly** and need refresh logic
- API keys are **static** and don't expire
- OAuth has **scopes** (read/write permissions)
- API keys have **full access** or none
- Mixing them creates confusion and bugs

---

## Use Cases

### Current Use (Nov 2025):

✅ **`oauth_tokens`** - Active with 5 records:
- Google Workspace integration (3 accounts)
- Microsoft 365 integration (2 accounts)
- Powers 281 tools in registry
- Automated email, docs, calendar, sheets

❌ **`user_platform_credentials`** - Reserved (0 records):
- Awaiting non-OAuth integrations
- Table exists but unused

### Future Use Cases:

#### 1. **Multi-Tenant SaaS (Multiple Print Shop Franchises)**

Each franchise owner needs:

**OAuth Tokens:**
- Their Gmail for customer notifications
- Their Google Drive for file storage
- Their Microsoft account for team collaboration

**API Credentials:**
- Their own Stripe account for payments
- Their own Shopify store credentials
- Their own warehouse database access
- Their own SendGrid account for transactional emails

**Why Both Tables:**
- OAuth → Personal email/docs access (user-facing)
- API Keys → Business systems access (backend)

#### 2. **Enterprise Customers with Custom Integrations**

Customer wants to:
- Use their corporate Gmail (OAuth)
- Connect to their internal database (credentials)
- Send SMS via their Twilio account (API key)
- Store files in their AWS S3 bucket (access key)

**Implementation:**
```python
# Fetch OAuth token
google_token = get_google_credentials(user_id)

# Fetch API credentials
twilio_creds = get_platform_credentials(user_id, 'twilio')
aws_creds = get_platform_credentials(user_id, 'aws')
```

#### 3. **White-Label Deployment**

Reselling the platform to other businesses:
- Each client brings their own API keys
- Each client uses their own payment processor
- Each client has their own email service
- Platform owner doesn't handle their payments/emails

**Requirement:** Per-user API credentials → `user_platform_credentials`

#### 4. **Developer API Access**

Power users who want to:
- Use their GitHub personal access token
- Deploy to their Heroku account
- Manage their Docker registry
- Access their custom REST APIs

**Storage:** `user_platform_credentials` with type `personal_access_token`

---

## Implementation Guide

### Adding OAuth Integration (Use `oauth_tokens`):

```python
# In routes/oauth_routes.py

@app.route('/api/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    # Exchange code for tokens
    tokens = exchange_code_for_token(request.args.get('code'))
    
    # Store in oauth_tokens table
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO oauth_tokens 
        (user_id, platform, access_token, refresh_token, expires_at, email, scope)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        'google',
        tokens['access_token'],
        tokens['refresh_token'],
        tokens['expires_at'],
        tokens['email'],
        tokens['scope']
    ))
    
    conn.commit()
```

### Adding API Key Integration (Use `user_platform_credentials`):

```python
# In routes/settings_routes.py

@app.route('/api/settings/credentials/add', methods=['POST'])
def add_api_credentials():
    """Add user API credentials"""
    data = request.json
    
    # Encrypt the secret
    encrypted_value = encrypt_credential(data['credential_value'])
    
    # Store in user_platform_credentials table
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO user_platform_credentials
        (user_id, platform, credential_type, credential_key, credential_value, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        data['platform'],      # 'stripe', 'sendgrid', etc.
        data['type'],          # 'api_key', 'secret', etc.
        data['public_key'],    # pk_live_...
        encrypted_value,       # Encrypted sk_live_...
        json.dumps(data.get('metadata', {}))
    ))
    
    conn.commit()
    
    return success_response({'message': 'Credentials added successfully'})
```

### Fetching Credentials (Credential Injector):

```python
# In AI_infrastructure/auth/credential_injector.py

class CredentialInjector:
    """Inject credentials into tool calls"""
    
    def get_google_credentials(self, user_id: int):
        """Get Google OAuth token from oauth_tokens table"""
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT access_token, refresh_token, expires_at
            FROM oauth_tokens
            WHERE user_id = ? AND platform = 'google'
            ORDER BY updated_at DESC
            LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        return {
            'access_token': row['access_token'],
            'refresh_token': row['refresh_token'],
            'token_expiry': row['expires_at']
        }
    
    def get_platform_credentials(self, user_id: int, platform: str):
        """Get API credentials from user_platform_credentials table"""
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT credential_key, credential_value, metadata
            FROM user_platform_credentials
            WHERE user_id = ? AND platform = ? AND is_active = 1
        """, (user_id, platform))
        
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return {
            'api_key': row['credential_key'],
            'api_secret': decrypt_credential(row['credential_value']),
            'metadata': json.loads(row['metadata'])
        }
```

---

## Security Considerations

### `oauth_tokens` Security:

1. **Token Encryption:** Store encrypted in database (optional - tokens expire anyway)
2. **Scope Limitation:** Request minimal scopes needed
3. **Automatic Refresh:** Background job refreshes expiring tokens
4. **Revocation:** User can revoke in Google/Microsoft settings
5. **HTTPS Only:** OAuth callbacks must use HTTPS in production

### `user_platform_credentials` Security:

1. **MUST Encrypt:** Use AES-256 encryption for `credential_value`
2. **Separate Encryption Keys:** Don't store encryption key in code
3. **Key Rotation:** Regularly rotate encryption keys
4. **Access Logging:** Log when credentials are accessed
5. **User Verification:** Require password/2FA before showing credentials

#### Example Encryption:

```python
from cryptography.fernet import Fernet
import os

# Load encryption key from environment (NOT in code!)
ENCRYPTION_KEY = os.getenv('CREDENTIAL_ENCRYPTION_KEY')
cipher = Fernet(ENCRYPTION_KEY.encode())

def encrypt_credential(value: str) -> str:
    """Encrypt API key/secret"""
    return cipher.encrypt(value.encode()).decode()

def decrypt_credential(encrypted: str) -> str:
    """Decrypt API key/secret"""
    return cipher.decrypt(encrypted.encode()).decode()
```

**CRITICAL:** Never commit `CREDENTIAL_ENCRYPTION_KEY` to git!

---

## Migration Path

### If You Need to Use `user_platform_credentials`:

**Step 1:** Enable encryption
```python
# Add to .env.master (NEVER commit this!)
CREDENTIAL_ENCRYPTION_KEY=<generate with: Fernet.generate_key()>
```

**Step 2:** Create settings UI
```javascript
// In UI/settings/credentials.html
<form id="add-credentials-form">
  <select name="platform">
    <option value="stripe">Stripe</option>
    <option value="sendgrid">SendGrid</option>
    <option value="aws">AWS</option>
  </select>
  <input type="text" name="api_key" placeholder="Public Key">
  <input type="password" name="api_secret" placeholder="Secret Key">
  <button type="submit">Add Credentials</button>
</form>
```

**Step 3:** Add API endpoint (see Implementation Guide above)

**Step 4:** Update credential injector to fetch from both tables

**Step 5:** Document which tools use which table

---

## Summary

### Decision Matrix:

**Use `oauth_tokens` when:**
- ✅ Platform supports OAuth 2.0 (Google, Microsoft, Facebook)
- ✅ Need user consent for access
- ✅ Tokens expire and need refresh
- ✅ Scope-based permissions

**Use `user_platform_credentials` when:**
- ✅ Platform uses API keys (Stripe, SendGrid, AWS)
- ✅ Static credentials (no expiry)
- ✅ Per-user custom credentials
- ✅ Backend-to-backend authentication

### Current Status (Nov 2025):

| Table | Records | Status | Action |
|-------|---------|--------|--------|
| `oauth_tokens` | 5 | ✅ Active | Keep - Essential |
| `user_platform_credentials` | 0 | ⚠️ Reserved | Keep - Future use |

### Recommendation:

**✅ KEEP BOTH TABLES**

- `oauth_tokens` is critical for current functionality
- `user_platform_credentials` provides future flexibility
- Minimal cost (empty table)
- Avoiding future migration work

---

## References

- **Credential Injector:** `AI_infrastructure/auth/credential_injector.py`
- **OAuth Routes:** `AI_infrastructure/routes/oauth_routes.py`
- **Database Schema:** `AI_infrastructure/migrations/`
- **Security Guidelines:** `docs/SECURITY_BEST_PRACTICES.md`

---

**Last Updated:** November 15, 2025  
**Maintainer:** AI Agents Development Team  
**Version:** 1.0
