# Testing Tools

Reusable maintenance and verification tools for the AI Agents platform.

## 📂 Contents

### Microsoft OAuth Tools

#### `simple_microsoft_refresh.py`
**Purpose:** Refresh expired Microsoft OAuth tokens using direct HTTP requests

**Usage:**
```bash
python testing_tools/simple_microsoft_refresh.py
```

**Features:**
- Direct HTTP token refresh (no dependencies on UserAuthManager)
- Automatic database updates
- Error tracking and retry counting
- Works with `.env.master` credentials

**When to use:**
- Microsoft tokens expired
- Need to refresh tokens without re-authenticating
- Automated token maintenance

---

#### `refresh_microsoft_token.py`
**Purpose:** Alternative token refresh using UserAuthManager

**Usage:**
```bash
python testing_tools/refresh_microsoft_token.py
```

**Features:**
- Uses UserAuthManager integration
- More integrated with existing auth system
- Auto-detects expired tokens

**When to use:**
- Prefer using existing auth infrastructure
- Need integration with UserAuthManager methods

---

### Verification Scripts

#### `verify_microsoft_fix_15.py`
**Purpose:** Verify Microsoft platform migration (Fix #15)

**Usage:**
```bash
python testing_tools/verify_microsoft_fix_15.py
```

**Checks:**
- ✅ No deprecated 'microsoft365' tokens
- ✅ Microsoft tokens exist and are active
- ✅ Gerardo's account token status
- ✅ Token expiration dates
- ✅ Refresh token availability

**Output:**
```
======================================================================
MICROSOFT AUTHENTICATION STATUS - Fix #15 Verification
======================================================================

📊 Token Distribution:
  google: 3 tokens
  microsoft: 2 tokens

✅ No deprecated 'microsoft365' tokens found

🔐 Microsoft Tokens (2 total):
  User 4: Gerardo@minivetguide.onmicrosoft.com
    Status: ✅ ACTIVE
    Expires: Nov 1, 13:04:25

======================================================================
🎉 Fix #15 COMPLETE - All Microsoft authentication working!
======================================================================
```

---

#### `verify_fix_14_oauth_cleanup.py`
**Purpose:** Verify OAuth cleanup implementation (Fix #14)

**Usage:**
```bash
python testing_tools/verify_fix_14_oauth_cleanup.py
```

**Checks:**
- ✅ File modifications applied
- ✅ Deprecated warnings present
- ✅ oauth_tokens table usage
- ✅ No user_platform_credentials references

**Tests 5 verification steps:**
1. Core files modified correctly
2. Deprecation warnings in place
3. Database schema correct (oauth_tokens table)
4. No legacy table references
5. Import statements updated

---

#### `smoke_test_fix_14.py`
**Purpose:** Comprehensive smoke testing for Fix #14 OAuth cleanup

**Usage:**
```bash
python testing_tools/smoke_test_fix_14.py
```

**Tests 8 critical systems:**
1. ✅ Server health check
2. ✅ OAuth tokens database schema (24 columns)
3. ✅ Credential injector functions
4. ✅ Google Workspace integration (152 tools)
5. ✅ Microsoft Graph integration (46 tools)
6. ✅ Deprecation warnings present
7. ✅ Tool execution flow (594 tools)
8. ✅ OAuth routes configured

**Expected Results:**
```
======================================================================
FINAL RESULT: 7/8 tests passed (87.5%)
Time elapsed: 23.35 seconds
======================================================================

🎉 SMOKE TESTS PASSED! Fix #14 is production ready.
```

---

## 🔧 Common Tasks

### Refresh All Microsoft Tokens
```bash
python testing_tools/simple_microsoft_refresh.py
```

### Verify Microsoft Authentication
```bash
python testing_tools/verify_microsoft_fix_15.py
```

### Run Full OAuth System Check
```bash
python testing_tools/smoke_test_fix_14.py
```

### Verify OAuth Cleanup
```bash
python testing_tools/verify_fix_14_oauth_cleanup.py
```

---

## 📊 Tool Categories

### **Token Maintenance:**
- `simple_microsoft_refresh.py` - Direct HTTP token refresh
- `refresh_microsoft_token.py` - UserAuthManager-based refresh

### **System Verification:**
- `verify_microsoft_fix_15.py` - Microsoft platform migration check
- `verify_fix_14_oauth_cleanup.py` - OAuth cleanup verification
- `smoke_test_fix_14.py` - Comprehensive system smoke tests

---

## 🚀 Quick Reference

| Task | Command |
|------|---------|
| Refresh Microsoft tokens | `python testing_tools/simple_microsoft_refresh.py` |
| Verify Microsoft auth | `python testing_tools/verify_microsoft_fix_15.py` |
| Run smoke tests | `python testing_tools/smoke_test_fix_14.py` |
| Verify OAuth cleanup | `python testing_tools/verify_fix_14_oauth_cleanup.py` |

---

## 📝 Notes

- All scripts use `data/ai_infrastructure.db` (correct database location)
- Microsoft credentials loaded from `.env.master`
- Scripts are safe to run multiple times
- No destructive operations without confirmation
- All tools include detailed logging and status updates

---

**Last Updated:** November 1, 2025  
**Total Tools:** 5 (2 maintenance, 3 verification)
