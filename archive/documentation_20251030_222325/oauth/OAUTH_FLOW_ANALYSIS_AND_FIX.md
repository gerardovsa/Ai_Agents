# 🔴 CRITICAL: OAuth Flow Analysis & Complete Fix

**Date:** October 30, 2025  
**Issue:** OAuth keeps failing, user keeps re-authorizing, credentials not stored correctly  
**Root Cause:** OAuth routes writing to WRONG table with WRONG schema

---

## 🔍 Current Broken Flow

### What Happens When User Clicks "Connect Google":

```
1. User clicks "Connect Google" in UI
   ↓
2. google_auth_routes.py /login endpoint called
   ↓
3. Redirects to Google consent screen
   ↓
4. User approves (gives permissions)
   ↓
5. Google redirects back to /callback
   ↓
6. Callback exchanges code for tokens
   ↓
7.  PROBLEM: Writes to user_platform_credentials table (OLD/WRONG)
   ↓
8. Stores data in WRONG columns:
   - credential_type = 'oauth'
   - credential_key = 'access_token' 
   - credential_value = 'ya29.a0...'
   ↓
9.  PROBLEM: Tools look in oauth_tokens table (NEW/CORRECT)
   ↓
10.  Result: Tools can't find credentials → "Not connected"
```

---

## 📊 Database Table Comparison

###  OLD TABLE: user_platform_credentials (WRONG - what auth routes use)
```sql
CREATE TABLE user_platform_credentials (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    platform TEXT,              -- 'google', 'microsoft'
    credential_type TEXT,       -- 'oauth', 'api_key'
    credential_key TEXT,        -- 'access_token', 'refresh_token'
    credential_value TEXT,      -- Actual token value
    is_active INTEGER,
    metadata TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### NEW TABLE: oauth_tokens (CORRECT - what tools expect)
```sql
CREATE TABLE oauth_tokens (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,           -- 'google', 'microsoft', 'microsoft365'
    access_token TEXT NOT NULL,       -- Direct column for access token
    refresh_token TEXT,               -- Direct column for refresh token
    token_type TEXT DEFAULT 'Bearer',
    expires_at TIMESTAMP,             -- Token expiration time
    scopes TEXT,                      -- Space-separated scopes
    is_valid INTEGER DEFAULT 1,       -- Is token currently valid
    is_active INTEGER DEFAULT 1,      -- Is this credential active
    auto_refresh_enabled INTEGER DEFAULT 1,
    last_refreshed_at TIMESTAMP,
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Profile data
    email TEXT,
    profile_name TEXT,
    profile_picture_url TEXT,
    profile_data TEXT,                -- JSON blob
    
    -- Metadata
    granted_scopes TEXT,              -- Scopes user actually granted
    auth_method TEXT,                 -- 'oauth2', 'service_account'
    
    UNIQUE(user_id, platform),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
```

---

## 🔧 Files That Need Fixing

### 1. Google OAuth Routes (HIGH PRIORITY)
**File:** `AI_infrastructure/routes/google_auth_routes.py`

**Problems:**
- Line 288: `INSERT INTO user_platform_credentials` 
- Line 300: `INSERT INTO user_platform_credentials` 
- Uses wrong column names: `credential_type`, `credential_key`, `credential_value`
- Missing required columns: `expires_at`, `scopes`, `email`, etc.

**Needs:**
- Change to `INSERT INTO oauth_tokens`
- Use correct column names
- Store all 24 columns properly

### 2. Microsoft OAuth Routes (HIGH PRIORITY)
**File:** `AI_infrastructure/routes/microsoft_auth_routes.py`

**Likely has same problems** (need to verify)

### 3. Credential Fetcher (May need updates)
**File:** `AI_infrastructure/auth/credential_fetcher.py` or similar

**Should:**
- Query `oauth_tokens` table
- Return tokens in format tools expect
- Handle token refresh automatically

---

## 🎯 Complete Fix Plan

### Phase 1: Update Google OAuth Routes (30 min)

**Changes to `google_auth_routes.py`:**

1. **Update callback function** (lines 250-310):
   - Change table name: `user_platform_credentials` → `oauth_tokens`
   - Change INSERT query to use oauth_tokens schema
   - Calculate `expires_at` timestamp
   - Store all required columns

2. **Update refresh token function** (lines 350-400):
   - Query oauth_tokens table
   - Update with correct column names

3. **Add status endpoint** (new):
   - Check oauth_tokens for user credentials
   - Return connection status

**NEW INSERT Query:**
```python
cursor.execute('''
    INSERT OR REPLACE INTO oauth_tokens 
    (user_id, platform, access_token, refresh_token, token_type,
     expires_at, scopes, email, profile_name, profile_data,
     is_valid, is_active, auto_refresh_enabled, granted_scopes,
     auth_method, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
''', (
    user_id,
    'google',
    access_token,
    refresh_token,
    'Bearer',
    expires_at,  # Calculated from expires_in
    ' '.join(GOOGLE_SCOPES),  # Requested scopes
    email,
    name,
    json.dumps(profile),  # Full profile data
    1,  # is_valid
    1,  # is_active
    1,  # auto_refresh_enabled
    tokens.get('scope', ' '.join(GOOGLE_SCOPES)),  # Granted scopes
    'oauth2',
))
```

### Phase 2: Update Microsoft OAuth Routes (30 min)

**Same changes for Microsoft:**
- Update to use oauth_tokens table
- Update column names
- Store all required fields

### Phase 3: Update UI Status Display (15 min)

**File:** `business-ai-platform-v2.html` (or module file)

**Changes:**
- Update status check endpoint to query oauth_tokens
- Display email from oauth_tokens.email column
- Show last_refreshed_at timestamp

### Phase 4: Testing (30 min)

1. **Delete old credentials:**
   ```sql
   DELETE FROM user_platform_credentials WHERE platform = 'google';
   DELETE FROM oauth_tokens WHERE platform = 'google';
   ```

2. **Fresh authorization:**
   - Click "Connect Google"
   - Complete OAuth flow
   - Verify data in oauth_tokens table

3. **Test tool execution:**
   - Send Gmail query to AI
   - Verify credentials fetched from oauth_tokens
   - Verify tool executes successfully

4. **Test refresh:**
   - Set expires_at to past time
   - Trigger tool execution
   - Verify token auto-refreshes

---

## 📝 Complete Rewritten google_auth_routes.py

I will create a completely new version with:
- Writes to oauth_tokens table
- Uses correct column names
- Stores all 24 columns
- Proper error handling
- Token refresh logic
- Status checking
- Clean code structure
- Aligned with V2 architecture

---

## Success Criteria

After fix, this should work:

1. **User clicks "Connect Google"** → OAuth flow starts
2. **User approves** → Tokens saved to oauth_tokens table
3. **Check database:**
   ```sql
   SELECT * FROM oauth_tokens WHERE user_id = 1 AND platform = 'google';
   ```
   Should show: access_token, refresh_token, email, expires_at, etc.

4. **UI shows:** "Connected" with email address
5. **AI tool call:** "List my Gmail messages"
6. **Tools fetch from oauth_tokens** → Find credentials
7. **Gmail API called** → Returns real emails
8. **AI responds** → With actual email data

**NO MORE RE-AUTHORIZATION NEEDED!** 🎉

---

## 🚀 Next Steps

1. I will rewrite `google_auth_routes.py` completely
2. Update `microsoft_auth_routes.py` similarly
3. Test with fresh authorization
4. Verify tools can access credentials
5. Document the fixed flow

---

**Status:** Ready to implement complete fix
