# Remaining File-Based OAuth References - Complete List

**Date**: November 3, 2025  
**Found**: 18 references in Python files (+ many in documentation)

## Python Files with File-Based OAuth References

### 1. ✅ ALREADY FIXED
- `google_workspace/google_tasks.py` - All file fallbacks removed (470+ lines deleted)

### 2. ❌ NEEDS FIXING - Active Code

#### `google_workspace/oauth_manager.py` (5 references)
**Status**: Still has deprecated file-based OAuth functions  
**Used by**: `gmail.py`, `google_calendar.py`, test scripts  
**Lines**:
- Line 33: `from google_auth_oauthlib.flow import InstalledAppFlow`
- Line 132: `'credentials_desktop.json'`
- Line 151: `'credentials_web.json'`  
- Line 255: `InstalledAppFlow.from_client_secrets_file`
- Line 404: `InstalledAppFlow.from_client_secrets_file`

**Functions to remove**:
- `get_oauth_config()` - Returns file paths
- `build_gmail_oauth_service()` - File-based OAuth
- `build_calendar_oauth_service()` - File-based OAuth
- `authenticate_all_services()` - File-based OAuth

#### `google_workspace/gmail.py` (1 reference)
**Status**: Has fallback to file-based OAuth  
**Line 92**: `return build_gmail_oauth_service(user_email=user_email)`  
**Action**: Remove fallback, throw error like google_tasks.py does

#### `google_workspace/google_calendar.py` (1+ reference)
**Status**: Likely has fallback to file-based OAuth (same pattern as gmail.py)  
**Action**: Remove fallback, throw error

#### `AI_infrastructure/routes/oauth_routes.py` (3 references)
**Status**: OLD file-based OAuth routes (NOT IMPORTED ANYWHERE!)  
**Lines**:
- Line 20: `from google_workspace.oauth_manager import UNIFIED_SCOPES, get_oauth_config`
- Line 47: `'OAuth not configured. Missing credentials_web.json'`
- Line 59: `flow = Flow.from_client_secrets_file`  
- Line 116: `flow = Flow.from_client_secrets_file`

**Action**: This file is DEPRECATED and not used. Can be deleted or archived.

### 3. ⚠️ TEST/VERIFICATION SCRIPTS - Low Priority

#### `testing_tools/verify_fix_14_oauth_cleanup.py` (4 references)
**Status**: Verification script checking for credentials_desktop.json warnings  
**Action**: Keep as-is (it's testing that warnings exist)

#### `scripts/testing/test_unified_oauth.py` (1 reference)  
**Status**: Test script with setup instructions  
**Line 117**: `print("   1. Make sure credentials_desktop.json exists")`  
**Action**: Update to mention database OAuth instead

#### `scripts/testing/test_oauth_all.py` (2 references)
**Status**: Test script importing from oauth_manager  
**Action**: Update to use database OAuth directly

## Recommended Fix Order

### Phase 1: Remove File Fallbacks in Core Tools ✅ HIGH PRIORITY

1. ✅ **DONE**: `google_workspace/google_tasks.py` - Removed all file fallbacks

2. **TODO**: `google_workspace/gmail.py`
   ```python
   # REMOVE this fallback (line 92):
   return build_gmail_oauth_service(user_email=user_email)
   
   # REPLACE with:
   raise Exception(
       "❌ Gmail requires database OAuth!\n"
       "Credentials must be in: data/ai_infrastructure.db\n"
       "Authenticate at: http://localhost:5001/auth/google/login"
   )
   ```

3. **TODO**: `google_workspace/google_calendar.py`
   - Same fix as gmail.py
   - Remove any `build_calendar_oauth_service` fallback

### Phase 2: Mark oauth_manager.py as Deprecated ✅ MEDIUM PRIORITY

**File**: `google_workspace/oauth_manager.py`

Option A: **Delete deprecated functions**
- Remove `get_oauth_config()`
- Remove `build_gmail_oauth_service()`
- Remove `build_calendar_oauth_service()`
- Remove `authenticate_all_services()`
- Keep only `UNIFIED_SCOPES` (if still needed)

Option B: **Add strong deprecation notices**
```python
def build_gmail_oauth_service():
    raise NotImplementedError(
        "❌ DEPRECATED: File-based OAuth is no longer supported!\n"
        "Use: from AI_infrastructure.auth.credential_injector import create_google_service_with_user_credentials"
    )
```

### Phase 3: Archive/Delete Old OAuth Routes ⚠️ LOW PRIORITY

**File**: `AI_infrastructure/routes/oauth_routes.py`
- Not imported anywhere
- Can be moved to `docs/archive/` or deleted

### Phase 4: Update Test Scripts ⚠️ LOW PRIORITY

- `scripts/testing/test_unified_oauth.py` - Update instructions
- `scripts/testing/test_oauth_all.py` - Use database OAuth

## Documentation References (Informational Only)

50+ matches in .md files - These are **documentation** and don't need fixing:
- `FILE_OAUTH_REMOVAL_COMPLETE.md` - Documents the removal ✅
- `FIX_14_*.md` - Historical fix documentation ✅
- `OAUTH_*.md` - Architecture/guide documentation ✅

These files DOCUMENT the old system and the migration - keep as-is for historical reference.

## Summary

**Active code references: 10 total**
- ✅ **1 fixed**: google_tasks.py
- ❌ **5 need fixing**: gmail.py, google_calendar.py, oauth_manager.py
- ⚠️ **4 low priority**: oauth_routes.py (not used), test scripts

**Next actions:**
1. Fix gmail.py fallback
2. Fix google_calendar.py fallback  
3. Deprecate oauth_manager.py functions
4. Archive oauth_routes.py

**After fixes:**
- ALL Google Workspace tools will use database OAuth ONLY
- NO file-based OAuth anywhere in active code
- Clear error messages directing users to authenticate via web UI
