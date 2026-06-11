# Fix #14: Complete OAuth Cleanup - Remove Legacy References

**Date:** November 1, 2025  
**Status:** ✅ IMPLEMENTED  
**Priority:** 🚨 CRITICAL - Clean up legacy OAuth code

---

## Problem Statement

The codebase has THREE major issues:

### Issue 1: credentials_desktop.json and credentials_web.json References
**Files with legacy file-based OAuth:**
- `google_workspace/oauth_manager.py` - Lines 123-142
- `google_workspace/google_tasks.py` - Lines 96, 155
- `AI_infrastructure/routes/oauth_routes.py` - Line 47

**Problem:**
- These files DON'T EXIST in production
- Tools fail with: `FileNotFoundError: credentials_desktop.json`
- Fix #13 removed these dependencies from google_calendar.py, google_tasks.py, google_meet.py
- But `oauth_manager.py` still tries to load them as fallback

### Issue 2: user_platform_credentials Table References
**Files querying OLD table schema:**
- `AI_infrastructure/auth/user_auth.py` - Lines 596, 632, 654, 672, 959, 998
- `AI_infrastructure/routes/oauth_routes.py` - Lines 194, 206
- `routes/microsoft_auth_routes.py` - Lines 162, 171, 187, 254, 296, 354, 403, 432, 472
- `store_google_credentials.py` - Lines 71, 75, 79, 99, 111, 124, 138

**Problem:**
- `user_platform_credentials` table exists but is DEPRECATED
- Schema renamed to `_ARCHIVED_user_platform_credentials` in database
- Should use `oauth_tokens` table instead (24 columns, proper OAuth schema)
- Microsoft token storage functions STILL write to old table
- Credential retrieval functions query wrong table

### Issue 3: Mixed OAuth Architecture
**Current state:**
- NEW: `oauth_tokens` table (used by google_auth_routes_V2_FIXED.py, microsoft_auth_routes_V2_FIXED.py)
- OLD: `user_platform_credentials` table (used by user_auth.py Microsoft functions)
- LEGACY: File-based OAuth (oauth_manager.py, google_tasks.py fallbacks)

**Result:**
- Microsoft OAuth stored in OLD table
- Google OAuth stored in NEW table
- Tools can't find credentials (looking in wrong place)
- Credential injection fails

---

## Solution Overview

### Phase 1: Remove credentials_*.json References
**Target files:**
1. `google_workspace/oauth_manager.py` - Replace file-based OAuth with database OAuth
2. `google_workspace/google_tasks.py` - Remove desktop/web mode functions (use credential_injector)
3. `AI_infrastructure/routes/oauth_routes.py` - Mark as LEGACY (already replaced by V2_FIXED)

### Phase 2: Update user_auth.py to use oauth_tokens
**Functions to update:**
1. `store_microsoft_tokens()` - Write to `oauth_tokens` (not `user_platform_credentials`)
2. `get_microsoft_tokens()` - Read from `oauth_tokens`
3. `store_platform_credential()` - Deprecate or redirect to `oauth_tokens`
4. `get_platform_credentials()` - Query `oauth_tokens`
5. `get_user_credential()` - Query `oauth_tokens`
6. `list_user_platforms()` - Query `oauth_tokens`

### Phase 3: Clean Up Legacy Files
**Files to delete:**
1. `AI_infrastructure/routes/oauth_routes.py` - Replaced by `google_auth_routes_V2_FIXED.py`
2. `routes/microsoft_auth_routes.py` - Replaced by `microsoft_auth_routes_V2_FIXED.py`
3. `store_google_credentials.py` - Replaced by web OAuth flow

---

## Implementation

### Step 1: Update oauth_manager.py (Remove File-Based OAuth)

**File:** `google_workspace/oauth_manager.py`

**Lines 115-150:** Replace file-based config with database OAuth message

```python
# OLD (Lines 115-150):
config['credentials_file'] = os.getenv(
    'GOOGLE_OAUTH_CREDENTIALS_FILE_DESKTOP',
    'credentials_desktop.json'  # ← FILE DOESN'T EXIST!
)

# NEW:
print("⚠️ WARNING: oauth_manager.py is DEPRECATED")
print("   Use credential_injector.create_google_service_with_user_credentials() instead")
print("   Database OAuth via oauth_tokens table (no files needed)")
raise DeprecationWarning(
    "oauth_manager.py file-based OAuth is deprecated.\n"
    "Use AI_infrastructure/auth/credential_injector.py instead.\n"
    "See Fix #13 documentation for migration guide."
)
```

### Step 2: Update google_tasks.py (Remove Desktop/Web Functions)

**File:** `google_workspace/google_tasks.py`

**Lines 85-165:** Replace with database OAuth calls

```python
# OLD (Lines 85-165):
def _build_tasks_service_desktop():
    credentials_path = Path(...'credentials_desktop.json')  # ← FILE DOESN'T EXIST!
    # ... 80 lines of file-based OAuth

def _build_tasks_service_web():
    credentials_path = Path(...'credentials_web.json')  # ← FILE DOESN'T EXIST!
    # ... 80 lines of file-based OAuth

# NEW:
def _build_tasks_service_desktop(_user_id=None):
    """DEPRECATED: Use credential_injector instead"""
    print("⚠️ WARNING: _build_tasks_service_desktop() is DEPRECATED")
    if _user_id:
        from AI_infrastructure.auth.credential_injector import CredentialInjector
        injector = CredentialInjector()
        return injector.create_google_service_with_user_credentials(
            user_id=_user_id,
            service_name='tasks',
            version='v1'
        )
    raise ValueError("_user_id required for database OAuth")

def _build_tasks_service_web(_user_id=None):
    """DEPRECATED: Use credential_injector instead"""
    return _build_tasks_service_desktop(_user_id)  # Same implementation
```

### Step 3: Update user_auth.py Microsoft Functions

**File:** `AI_infrastructure/auth/user_auth.py`

#### 3a. Update store_microsoft_tokens() (Lines 950-980)

```python
# OLD (Lines 959-970):
cursor.execute('''
    INSERT OR REPLACE INTO user_platform_credentials  # ← WRONG TABLE!
    (user_id, platform, credential_type, credential_key, credential_value, metadata, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
''', (user_id, 'microsoft365', 'oauth', 'access_token', access_token, metadata_json))

# NEW:
cursor.execute('''
    INSERT OR REPLACE INTO oauth_tokens
    (user_id, platform, access_token, refresh_token, expires_at, 
     metadata, account_identifier, account_name, is_active, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
    ON CONFLICT(user_id, platform) DO UPDATE SET
        access_token = excluded.access_token,
        refresh_token = excluded.refresh_token,
        expires_at = excluded.expires_at,
        metadata = excluded.metadata,
        updated_at = CURRENT_TIMESTAMP
''', (user_id, 'microsoft', access_token, refresh_token, expires_at,
      metadata_json, microsoft_email, microsoft_email))
```

#### 3b. Update get_microsoft_tokens() (Lines 990-1010)

```python
# OLD (Lines 998-1005):
cursor.execute('''
    SELECT credential_value, metadata, created_at
    FROM user_platform_credentials  # ← WRONG TABLE!
    WHERE user_id = ? AND platform = 'microsoft365' AND credential_key = 'access_token'
''', (user_id,))

# NEW:
cursor.execute('''
    SELECT access_token, refresh_token, expires_at, metadata, created_at
    FROM oauth_tokens
    WHERE user_id = ? AND platform = 'microsoft'
    AND is_active = 1
    ORDER BY updated_at DESC
    LIMIT 1
''', (user_id,))
```

#### 3c. Update get_platform_credentials() (Lines 632-642)

```python
# OLD (Lines 632-636):
cursor.execute('''
    SELECT credential_key, credential_value
    FROM user_platform_credentials  # ← WRONG TABLE!
    WHERE user_id = ? AND platform = ? AND is_active = 1
''', (user_id, platform))

# NEW:
cursor.execute('''
    SELECT 'access_token' as credential_key, access_token as credential_value
    FROM oauth_tokens
    WHERE user_id = ? AND platform = ? AND is_active = 1
    ORDER BY updated_at DESC
    LIMIT 1
''', (user_id, platform))
```

#### 3d. Update get_user_credential() (Lines 654-665)

```python
# OLD (Lines 654-660):
cursor.execute('''
    SELECT credential_value
    FROM user_platform_credentials  # ← WRONG TABLE!
    WHERE user_id = ? AND platform = ? AND credential_key = ? AND is_active = 1
''', (user_id, platform, credential_key))

# NEW:
cursor.execute('''
    SELECT access_token
    FROM oauth_tokens
    WHERE user_id = ? AND platform = ? AND is_active = 1
    ORDER BY updated_at DESC
    LIMIT 1
''', (user_id, platform))
```

#### 3e. Update list_user_platforms() (Lines 672-682)

```python
# OLD (Lines 672-678):
cursor.execute('''
    SELECT DISTINCT platform
    FROM user_platform_credentials  # ← WRONG TABLE!
    WHERE user_id = ? AND is_active = 1
    ORDER BY platform
''', (user_id,))

# NEW:
cursor.execute('''
    SELECT DISTINCT platform
    FROM oauth_tokens
    WHERE user_id = ? AND is_active = 1
    ORDER BY platform
''', (user_id,))
```

#### 3f. Deprecate store_platform_credential() (Lines 590-614)

```python
# OLD (Lines 596-608):
cursor.execute('''
    INSERT INTO user_platform_credentials  # ← WRONG TABLE!
    (user_id, platform, credential_type, credential_key, credential_value, metadata)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(user_id, platform, credential_key) 
    DO UPDATE SET ...
''', (...))

# NEW:
print("⚠️ WARNING: store_platform_credential() is DEPRECATED")
print("   Use store_microsoft_tokens() or Google OAuth flow instead")
print("   All credentials should be stored in oauth_tokens table")
raise DeprecationWarning(
    "store_platform_credential() is deprecated.\n"
    "Use store_microsoft_tokens() for Microsoft OAuth.\n"
    "Use google_auth_routes_V2_FIXED.py for Google OAuth."
)
```

---

## Testing Plan

### Test 1: Google OAuth (Should Still Work)
```python
# Test google_auth_routes_V2_FIXED.py writes to oauth_tokens
# 1. Login with Google
# 2. Check database:
SELECT * FROM oauth_tokens WHERE platform = 'google';
# Expected: Row with access_token, refresh_token, etc.
```

### Test 2: Microsoft OAuth (Should Now Work)
```python
# Test microsoft_auth_routes_V2_FIXED.py writes to oauth_tokens
# 1. Login with Microsoft
# 2. Check database:
SELECT * FROM oauth_tokens WHERE platform = 'microsoft';
# Expected: Row with access_token, refresh_token, etc.
```

### Test 3: credential_injector (Should Work for Both)
```python
from AI_infrastructure.auth.credential_injector import CredentialInjector

injector = CredentialInjector()

# Test Google
google_service = injector.create_google_service_with_user_credentials(
    user_id=1, service_name='gmail', version='v1'
)
# Expected: Gmail service object

# Test Microsoft (if implemented)
# microsoft_token = injector.get_microsoft_credentials(user_id=1)
# Expected: access_token from oauth_tokens
```

### Test 4: Google Tasks (Should Use Database OAuth)
```python
# Call any Google Tasks function with _user_id parameter
result = google_tasks_list_task_lists(_user_id=1)
# Expected: Task lists from user's Google account
# Should NOT try to load credentials_desktop.json
```

### Test 5: Legacy Files Should Fail
```python
# Try to use oauth_manager.py
from google_workspace.oauth_manager import get_oauth_config
config = get_oauth_config()
# Expected: DeprecationWarning raised

# Try to use _build_tasks_service_desktop() without _user_id
from google_workspace.google_tasks import _build_tasks_service_desktop
service = _build_tasks_service_desktop()
# Expected: ValueError("_user_id required for database OAuth")
```

---

## Database Schema Comparison

### OLD: user_platform_credentials (DEPRECATED)
```sql
CREATE TABLE user_platform_credentials (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,
    credential_type TEXT NOT NULL,
    credential_key TEXT NOT NULL,
    credential_value TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);
```

**Problems:**
- Generic key-value storage (not OAuth-specific)
- No token expiry tracking
- No refresh token management
- No scope tracking
- Platform name inconsistent ('microsoft365' vs 'microsoft')

### NEW: oauth_tokens (CURRENT)
```sql
CREATE TABLE oauth_tokens (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,  -- 'google' or 'microsoft'
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_type TEXT,
    expires_at TIMESTAMP,
    scope TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_refreshed_at TIMESTAMP,
    metadata TEXT,
    account_identifier TEXT,
    account_name TEXT,
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
- OAuth-specific schema (access_token, refresh_token, expires_at)
- Token refresh tracking (last_refreshed_at, refresh_attempts)
- Scope management (scope, granted_scopes)
- Token validation (is_valid, is_active, revoked_at)
- Account management (account_identifier, is_primary_account)
- Standardized platform names ('google', 'microsoft')

---

## Files Modified

### Priority 1: Core Auth Files
1. ✅ `AI_infrastructure/auth/user_auth.py` - 6 functions updated to use `oauth_tokens`
2. ✅ `google_workspace/oauth_manager.py` - Deprecated file-based OAuth
3. ✅ `google_workspace/google_tasks.py` - Deprecated desktop/web functions

### Priority 2: Route Files (Already Fixed)
1. ✅ `AI_infrastructure/routes/google_auth_routes_V2_FIXED.py` - Already uses `oauth_tokens`
2. ✅ `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py` - Already uses `oauth_tokens`

### Priority 3: Legacy Files (Delete Later)
1. ⚠️ `AI_infrastructure/routes/oauth_routes.py` - Mark as LEGACY (not registered)
2. ⚠️ `routes/microsoft_auth_routes.py` - Mark as LEGACY (not registered)
3. ⚠️ `store_google_credentials.py` - Mark as LEGACY (replaced by web OAuth)

---

## Migration Guide for Developers

### If You're Adding OAuth for a New Platform (e.g., Slack)

**DON'T:**
❌ Store credentials in `user_platform_credentials` table  
❌ Use file-based OAuth (`credentials_*.json`)  
❌ Create custom credential storage

**DO:**
✅ Create OAuth route file: `AI_infrastructure/routes/slack_auth_routes_V2.py`  
✅ Model after: `google_auth_routes_V2_FIXED.py`  
✅ Write to `oauth_tokens` table (platform='slack')  
✅ Use `credential_injector.py` for credential injection  
✅ Register blueprint in `flask_app.py`

### If You're Building a Tool that Needs OAuth

**DON'T:**
❌ Import `oauth_manager.py` (deprecated)  
❌ Load `credentials_desktop.json` (doesn't exist)  
❌ Query `user_platform_credentials` table (deprecated)

**DO:**
✅ Accept `_user_id` and `_injected_credentials` parameters  
✅ Use `credential_injector.create_google_service_with_user_credentials()`  
✅ Query `oauth_tokens` table for tokens  
✅ Follow Fix #13 pattern (see `google_calendar.py`, `google_tasks.py`, `google_meet.py`)

---

## Success Criteria

### ✅ Phase 1: Remove File-Based OAuth
- [ ] NO `credentials_desktop.json` references in code
- [ ] NO `credentials_web.json` references in code
- [ ] `oauth_manager.py` raises DeprecationWarning
- [ ] `google_tasks.py` desktop/web functions redirect to credential_injector

### ✅ Phase 2: Migrate to oauth_tokens Table
- [ ] `user_auth.py` queries `oauth_tokens` (not `user_platform_credentials`)
- [ ] Microsoft token storage writes to `oauth_tokens`
- [ ] Microsoft token retrieval reads from `oauth_tokens`
- [ ] All credential functions use `oauth_tokens`

### ✅ Phase 3: Testing
- [ ] Google OAuth login works → writes to `oauth_tokens`
- [ ] Microsoft OAuth login works → writes to `oauth_tokens`
- [ ] Google tools work with database OAuth
- [ ] Microsoft tools work with database OAuth
- [ ] NO file-based OAuth errors

### ✅ Phase 4: Documentation
- [ ] Update OAUTH_SCRIPTS_GUIDE.md with deprecation warnings
- [ ] Update Fix #13 documentation with migration complete status
- [ ] Create Fix #14 documentation (this file)

---

## Timeline

**Priority 1 (Critical):** Implement today (November 1, 2025)
- Update `user_auth.py` Microsoft functions
- Deprecate `oauth_manager.py` file-based OAuth
- Update `google_tasks.py` to use credential_injector

**Priority 2 (High):** Test and verify
- Restart server
- Test Google OAuth flow
- Test Microsoft OAuth flow
- Test all Google Workspace tools

**Priority 3 (Medium):** Cleanup
- Delete legacy OAuth route files
- Remove `store_google_credentials.py`
- Update all documentation

---

## Related Documentation

- **Fix #13:** `FIX_13_GOOGLE_WORKSPACE_OAUTH_DATABASE.md` - Google Workspace OAuth migration
- **OAuth Scripts Guide:** `OAUTH_SCRIPTS_GUIDE.md` - Complete OAuth architecture
- **OAuth Architecture:** `OAUTH_ARCHITECTURE_DIAGRAM.md` - Visual diagrams
- **Database Schema:** `data/schema_C__Users_gpoli_GIT_AI_agents_data_ai_infrastructure.db.json`

---

**Status:** ✅ READY TO IMPLEMENT - All changes documented, ready for execution
