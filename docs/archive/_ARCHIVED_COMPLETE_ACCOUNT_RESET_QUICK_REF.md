# Complete Account Reset - Quick Reference

## What Changed?

### 🔴 NEW RED BUTTON: "Complete Account Reset"
- **Location:** User profile dropdown (top right)
- **Appearance:** Red gradient with warning icon
- **Action:** Completely deletes user and recreates via OAuth

---

## Two Fixes Implemented

### 1. Fixed 500 Error on Microsoft Status
**Problem:** `/api/auth/microsoft/status` endpoint crashed with 500 error  
**Cause:** Used `request.user_id` (doesn't exist)  
**Fix:** Changed to `request.user.get('user_id')`  
**Status:** ✅ Fixed

### 2. Complete Account Reset (Nuclear Option)
**Problem:** Consent screen not appearing during re-auth  
**Cause:** OAuth providers cache consent per user  
**Fix:** Delete entire user → Create fresh user on next OAuth  
**Status:** ✅ Implemented & Tested (4/4 tests pass)

---

## What It Does

```
Click Button → Confirm → Delete User → Redirect OAuth → Consent Screen → Fresh User
```

### Step-by-Step:
1. **Click** red "Complete Account Reset" button
2. **Confirm** deletion (strong warning shown)
3. **DELETE** user from database (completely removed)
4. **DELETE** all OAuth tokens
5. **DELETE** all platform credentials
6. **Revoke** tokens with OAuth provider API
7. **Redirect** to OAuth with `force_consent=true`
8. **Show** consent screen (new user = new authorization)
9. **Create** fresh user after OAuth approval
10. **Login** with new JWT token

---

## Test Before Using

```powershell
# 1. Run test suite
cd c:\Users\gpoli\GIT\AI_agents
python test_complete_reset.py

# Expected: 4/4 tests pass

# 2. Restart Flask
BISTART

# 3. Test in browser
# - Login as Gerardo@minivetguide.onmicrosoft.com
# - Click profile dropdown
# - Verify RED button appears
# - Verify no 500 errors
```

---

## Files Modified

| File | Changes |
|------|---------|
| `auth_routes.py` | Added `complete_reset` parameter, user deletion logic |
| `microsoft_auth_routes_V2_FIXED.py` | Fixed `request.user_id` → `request.user.get('user_id')` |
| `business-ai-platform-v2.html` | Changed button to RED, added `complete_reset: true` |

---

## Backend API

### Endpoint: POST /api/auth/revoke-tokens

**Request:**
```json
{
  "platform": "microsoft",
  "complete_reset": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "User account completely reset",
  "complete_reset": true,
  "tokens_deleted": 1,
  "user_deleted": 1,
  "provider_revoked": true
}
```

---

## Normal vs Complete Reset

### Normal Reset (`complete_reset: false`):
- Deletes tokens for specific platform
- Updates user flags
- Keeps user record
- User ID stays same

### Complete Reset (`complete_reset: true`):
- Deletes entire user from database
- Deletes ALL tokens (all platforms)
- Deletes ALL credentials
- User ID changes (new user)

---

## Why This Works

| Method | Forces Consent? | Why? |
|--------|----------------|------|
| Token revocation | ❌ No | Provider caches consent per user |
| `prompt=consent` | ⚠️ Maybe | Org policies override |
| Delete + Recreate | ✅ Best chance | New user = new authorization |

---

## Test Results

```
✅ PASS - User exists in database
✅ PASS - Backend complete_reset endpoint
✅ PASS - Microsoft status endpoint fix
✅ PASS - Frontend complete_reset parameter

📈 Results: 4/4 tests passed (100%)
```

---

## Quick Testing

### Check User Before Reset:
```sql
SELECT * FROM users WHERE email = 'Gerardo@minivetguide.onmicrosoft.com';
-- Should return: ID 4, username 'Gerardo'
```

### Trigger Reset:
1. Click RED button
2. Confirm deletion

### Check User After Reset:
```sql
SELECT * FROM users WHERE email = 'Gerardo@minivetguide.onmicrosoft.com';
-- Should return: NULL (user deleted)
```

### Re-authenticate:
1. OAuth redirect happens automatically
2. Login with Microsoft
3. **Consent screen should appear**
4. Accept permissions

### Check New User:
```sql
SELECT * FROM users WHERE email = 'Gerardo@minivetguide.onmicrosoft.com';
-- Should return: NEW ID (5+), fresh created_at timestamp
```

---

## Warning ⚠️

### This is DESTRUCTIVE:
- ✅ Completely deletes user
- ✅ Cannot undo
- ✅ All data lost
- ✅ User ID changes
- ✅ Must re-authenticate

### Use Only When:
- OAuth authentication broken
- Need to force consent screen
- Testing OAuth flow
- Resetting corrupted user data

---

## Full Documentation

See: `COMPLETE_ACCOUNT_RESET_IMPLEMENTATION.md` for complete details.

---

**Status:** ✅ Ready for Testing  
**Last Updated:** November 2025  
**Test Results:** 4/4 passing (100%)
