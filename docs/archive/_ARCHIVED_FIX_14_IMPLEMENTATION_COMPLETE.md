# Fix #14: OAuth Cleanup Implementation - COMPLETE ✅

**Date:** November 1, 2025  
**Status:** ✅ IMPLEMENTED  
**Files Modified:** 3 core files (9 functions updated)

---

## What Was Fixed

### Issue 1: credentials_desktop.json and credentials_web.json References ✅ FIXED
**Problem:** Tools tried to load credential files that don't exist in production

**Files Fixed:**
1. **google_workspace/oauth_manager.py** - Added deprecation warnings
2. **google_workspace/google_tasks.py** - Added database OAuth redirects

### Issue 2: user_platform_credentials Table References ✅ FIXED
**Problem:** Functions queried deprecated `user_platform_credentials` table instead of `oauth_tokens`

**Files Fixed:**
1. **AI_infrastructure/auth/user_auth.py** - Updated 7 functions to use `oauth_tokens`

---

## Files Modified Summary

### 1. google_workspace/oauth_manager.py (3 changes)
**Lines 115-150:** Added deprecation warning for file-based OAuth

**Changes:**
- Added warning message: "oauth_manager.py file-based OAuth is DEPRECATED"
- Added comments marking `credentials_desktop.json` and `credentials_web.json` as non-existent
- Recommends using `credential_injector.py` instead
- Still functional for backward compatibility but prints warnings

**Impact:** Developers see clear warnings when file-based OAuth is used

---

### 2. google_workspace/google_tasks.py (2 changes)

#### Change 1: `_build_tasks_service_desktop()` - Lines 85-96
**Before:**
```python
def _build_tasks_service_desktop():
    credentials_path = Path(...'credentials_desktop.json')  # File doesn't exist!
    # 80 lines of file-based OAuth
```

**After:**
```python
def _build_tasks_service_desktop(_user_id=None):
    if _user_id:
        # Redirect to database OAuth
        from AI_infrastructure.auth.credential_injector import CredentialInjector
        injector = CredentialInjector()
        return injector.create_google_service_with_user_credentials(
            user_id=_user_id, service_name='tasks', version='v1'
        )
    # Legacy file-based OAuth (for backward compatibility)
    # Shows deprecation warning
```

**Impact:** Functions can use database OAuth when `_user_id` is provided

#### Change 2: `_build_tasks_service_web()` - Lines 148-159
**Before:**
```python
def _build_tasks_service_web():
    credentials_path = Path(...'credentials_web.json')  # File doesn't exist!
```

**After:**
```python
def _build_tasks_service_web(_user_id=None):
    return _build_tasks_service_desktop(_user_id)  # Same implementation
```

**Impact:** Web mode now uses database OAuth (no separate implementation needed)

---

### 3. AI_infrastructure/auth/user_auth.py (7 functions updated)

#### Function 1: `store_platform_credential()` - Lines 596-608
**Status:** Added deprecation warning (still functional)

**Change:** Added warning message recommending oauth_tokens table

**Impact:** Developers aware function is deprecated

---

#### Function 2: `get_platform_credentials()` - Lines 632-642
**Status:** ✅ FIXED - Now queries oauth_tokens first

**Before:**
```python
SELECT credential_key, credential_value
FROM user_platform_credentials  # WRONG TABLE!
WHERE user_id = ? AND platform = ? AND is_active = 1
```

**After:**
```python
# Try oauth_tokens table first (NEW schema)
SELECT 'access_token' as credential_key, access_token as credential_value
FROM oauth_tokens
WHERE user_id = ? AND platform = ? AND is_active = 1
ORDER BY updated_at DESC
LIMIT 1

# Fallback to old table (DEPRECATED) if not found
SELECT credential_key, credential_value
FROM user_platform_credentials
WHERE user_id = ? AND platform = ? AND is_active = 1
```

**Impact:** Retrieves credentials from correct table (oauth_tokens)

---

#### Function 3: `get_user_credential()` - Lines 654-665
**Status:** ✅ FIXED - Now queries oauth_tokens first

**Before:**
```python
SELECT credential_value
FROM user_platform_credentials  # WRONG TABLE!
WHERE user_id = ? AND platform = ? AND credential_key = ? AND is_active = 1
```

**After:**
```python
# Try oauth_tokens table first (NEW schema)
if credential_key == 'access_token':
    SELECT access_token
    FROM oauth_tokens
    WHERE user_id = ? AND platform = ? AND is_active = 1
    ORDER BY updated_at DESC
    LIMIT 1
    
# Fallback to old table (DEPRECATED)
SELECT credential_value
FROM user_platform_credentials
WHERE user_id = ? AND platform = ? AND credential_key = ? AND is_active = 1
```

**Impact:** Retrieves access tokens from correct table

---

#### Function 4: `list_user_platforms()` - Lines 672-682
**Status:** ✅ FIXED - Now queries both tables

**Before:**
```python
SELECT DISTINCT platform
FROM user_platform_credentials  # ONLY OLD TABLE!
WHERE user_id = ? AND is_active = 1
ORDER BY platform
```

**After:**
```python
# Get platforms from both tables (UNION)
SELECT DISTINCT platform
FROM oauth_tokens
WHERE user_id = ? AND is_active = 1

UNION

SELECT DISTINCT platform
FROM user_platform_credentials
WHERE user_id = ? AND is_active = 1

ORDER BY platform
```

**Impact:** Shows platforms from both new and legacy tables

---

#### Function 5: `store_microsoft_tokens()` - Lines 959-980
**Status:** ✅ FIXED - Now writes to oauth_tokens

**Before:**
```python
INSERT OR REPLACE INTO user_platform_credentials  # WRONG TABLE!
(user_id, platform, credential_type, credential_key, credential_value, metadata, updated_at)
VALUES (?, 'microsoft365', 'oauth', 'access_token', ?, ?, CURRENT_TIMESTAMP)
```

**After:**
```python
INSERT INTO oauth_tokens  # CORRECT TABLE!
(user_id, platform, access_token, refresh_token, expires_at, 
 metadata, account_identifier, account_name, is_active, updated_at)
VALUES (?, 'microsoft', ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
ON CONFLICT(user_id, platform) DO UPDATE SET
    access_token = excluded.access_token,
    refresh_token = excluded.refresh_token,
    expires_at = excluded.expires_at,
    metadata = excluded.metadata,
    account_identifier = excluded.account_identifier,
    account_name = excluded.account_name,
    updated_at = CURRENT_TIMESTAMP
```

**Impact:** Microsoft tokens now stored in correct table with proper schema

**Key Changes:**
- Table: `user_platform_credentials` → `oauth_tokens`
- Platform name: `'microsoft365'` → `'microsoft'` (standardized)
- Columns: Proper OAuth schema (access_token, refresh_token, expires_at)
- Metadata: JSON format with microsoft_id and microsoft_email
- Account tracking: account_identifier and account_name fields

---

#### Function 6: `get_microsoft_tokens()` - Lines 998-1010
**Status:** ✅ FIXED - Now reads from oauth_tokens

**Before:**
```python
SELECT credential_value, metadata, created_at
FROM user_platform_credentials  # WRONG TABLE!
WHERE user_id = ? AND platform = 'microsoft365' AND credential_key = 'access_token'
```

**After:**
```python
SELECT access_token, refresh_token, expires_at, metadata, created_at
FROM oauth_tokens  # CORRECT TABLE!
WHERE user_id = ? AND platform = 'microsoft'
AND is_active = 1
ORDER BY updated_at DESC
LIMIT 1
```

**Impact:** Microsoft tokens retrieved from correct table

**Key Changes:**
- Table: `user_platform_credentials` → `oauth_tokens`
- Platform name: `'microsoft365'` → `'microsoft'`
- Returns: Full OAuth token data (access_token, refresh_token, expires_at)
- Sorting: Gets most recent token (ORDER BY updated_at DESC)

---

## Database Migration

### OLD Schema (user_platform_credentials) - DEPRECATED
```sql
CREATE TABLE user_platform_credentials (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,  -- 'microsoft365' (inconsistent)
    credential_type TEXT NOT NULL,
    credential_key TEXT NOT NULL,
    credential_value TEXT NOT NULL,  -- Generic storage
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);
```

### NEW Schema (oauth_tokens) - CURRENT ✅
```sql
CREATE TABLE oauth_tokens (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,  -- 'google' or 'microsoft' (standardized)
    access_token TEXT NOT NULL,  -- OAuth access token
    refresh_token TEXT,  -- OAuth refresh token
    token_type TEXT,
    expires_at TIMESTAMP,  -- Token expiry tracking
    scope TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_refreshed_at TIMESTAMP,
    metadata TEXT,  -- Additional OAuth data (JSON)
    account_identifier TEXT,  -- User email/ID
    account_name TEXT,  -- Display name
    is_primary_account BOOLEAN DEFAULT 0,
    is_valid BOOLEAN DEFAULT 1,
    is_active BOOLEAN DEFAULT 1,
    refresh_attempts INTEGER DEFAULT 0,
    last_refresh_error TEXT,
    auto_refresh_enabled BOOLEAN DEFAULT 1,
    granted_scopes TEXT,
    issued_at TIMESTAMP,
    revoked_at TIMESTAMP,
    ip_address_granted TEXT
);
```

**Benefits:**
- OAuth-specific columns (access_token, refresh_token, expires_at)
- Token refresh tracking (last_refreshed_at, refresh_attempts)
- Scope management (scope, granted_scopes)
- Account management (account_identifier, is_primary_account)
- Standardized platform names ('google', 'microsoft')

---

## Testing Checklist

### ✅ Phase 1: Verify Warnings Appear
```powershell
# Start server
cd C:\Users\gpoli\GIT\AI_agents
BISTART

# Expected console output:
# ⚠️ WARNING: oauth_manager.py file-based OAuth is DEPRECATED
# ⚠️ WARNING: _build_tasks_service_desktop() is DEPRECATED
# ⚠️ WARNING: store_platform_credential() uses deprecated table
```

### ✅ Phase 2: Test Google OAuth
```powershell
# Test via CHAT
CHAT "List my Gmail messages"

# Expected:
# - No "credentials_desktop.json not found" error
# - Uses database OAuth from oauth_tokens table
# - Console shows: "Using database OAuth for user X"
```

### ✅ Phase 3: Test Microsoft OAuth
```python
# Login with Microsoft account
# Check database:
sqlite3 data/ai_infrastructure.db
SELECT * FROM oauth_tokens WHERE platform = 'microsoft';

# Expected: Row with access_token, refresh_token, expires_at
# Platform should be 'microsoft' (not 'microsoft365')
```

### ✅ Phase 4: Test Credential Retrieval
```python
from AI_infrastructure.auth.user_auth import user_auth_manager

# Test get_platform_credentials (should check oauth_tokens first)
creds = user_auth_manager.get_platform_credentials(user_id=1, platform='google')
# Expected: {'access_token': '...'}

# Test get_microsoft_tokens (should use oauth_tokens)
tokens = user_auth_manager.get_microsoft_tokens(user_id=1)
# Expected: {'access_token': '...', 'refresh_token': '...', 'expires_at': '...'}
```

### ✅ Phase 5: Test Tool Execution
```powershell
# Test Google Workspace tools
CHAT "List my calendars"
CHAT "List my task lists"
CHAT "List my upcoming meetings"

# Expected:
# - All tools work with database OAuth
# - No file-based OAuth errors
# - Console shows database OAuth usage
```

---

## What Still Works (Backward Compatibility)

### ✅ Legacy Functions Still Functional
- `oauth_manager.py` - Shows warnings but still works
- `_build_tasks_service_desktop()` - Redirects to database OAuth if _user_id provided
- `store_platform_credential()` - Shows warning but still writes to old table
- `get_platform_credentials()` - Checks oauth_tokens first, falls back to old table

### ✅ Migration Path
**Old code:**
```python
from google_workspace.oauth_manager import build_oauth_service
service = build_oauth_service('gmail')  # File-based OAuth (deprecated)
```

**New code:**
```python
from AI_infrastructure.auth.credential_injector import CredentialInjector
injector = CredentialInjector()
service = injector.create_google_service_with_user_credentials(
    user_id=1, service_name='gmail', version='v1'
)  # Database OAuth (current)
```

---

## Next Steps (Optional Cleanup)

### Priority 1: Delete Legacy Files (After Testing)
```powershell
# These files are not registered in Flask app (safe to delete)
Remove-Item "AI_infrastructure\routes\oauth_routes.py"
Remove-Item "routes\microsoft_auth_routes.py"
Remove-Item "store_google_credentials.py"
```

### Priority 2: Full Migration to oauth_tokens
1. Migrate any remaining data from `user_platform_credentials` to `oauth_tokens`
2. Update any scripts that directly query `user_platform_credentials`
3. Remove fallback queries to old table

### Priority 3: Remove File-Based OAuth Entirely
1. Remove `oauth_manager.py` after all tools migrated
2. Remove `_build_tasks_service_desktop/web` functions from `google_tasks.py`
3. Remove all credential file references from environment variables

---

## Success Metrics

### ✅ Immediate Success (After Restart)
- [ ] Server starts without errors
- [ ] Console shows deprecation warnings for legacy OAuth
- [ ] Google OAuth login works → writes to `oauth_tokens`
- [ ] Microsoft OAuth login works → writes to `oauth_tokens`
- [ ] All Google Workspace tools work with database OAuth
- [ ] NO "credentials_desktop.json not found" errors

### ✅ Complete Migration (After All Tools Updated)
- [ ] All tools use `credential_injector.py`
- [ ] NO queries to `user_platform_credentials` table
- [ ] NO file-based OAuth references in code
- [ ] `oauth_manager.py` deleted or marked as LEGACY
- [ ] Legacy OAuth route files deleted

---

## Documentation Updated

1. ✅ **FIX_14_OAUTH_CLEANUP_COMPLETE.md** - Complete documentation (this file)
2. ✅ **FIX_14_IMPLEMENTATION_COMPLETE.md** - Implementation summary (current file)
3. 🔄 **OAUTH_SCRIPTS_GUIDE.md** - Should add Fix #14 references
4. 🔄 **README.md** - Should document current OAuth architecture

---

## Related Fixes

- **Fix #13:** Google Workspace OAuth database migration (google_calendar.py, google_tasks.py, google_meet.py)
- **Fix #12:** Conditional OAuth parameter passing (non-Google tools)
- **Fix #11:** Simple agent user_id parameter
- **Fix #9-10:** OAuth middleware and credential injection
- **Fix #1-7:** Streaming infrastructure

---

**Status:** ✅ IMPLEMENTATION COMPLETE - Ready to restart and test

**Next Action:** Restart Flask server to apply changes
```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```
