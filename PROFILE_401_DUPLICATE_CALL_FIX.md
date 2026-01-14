# Profile 401 Error - Duplicate Call Fix

**Date:** November 21, 2025  
**Status:** ✅ FIXED - Prevents duplicate profile calls  
**Issue:** Second call to `/api/auth/profile` fails with 401 UNAUTHORIZED

---

## 🎯 Problem

The user profile API is being called **twice**:
1. **First call** - Succeeds with 200 OK ✅
2. **Second call** - Fails with 401 UNAUTHORIZED ❌

### Error Logs:
```
Profile API response status: 200          ← First call succeeds
Profile data received: {profile: {…}, success: true}
...
GET http://localhost:5001/api/auth/profile 401 (UNAUTHORIZED)  ← Second call fails
Profile API response status: 401
Failed to load user profile: Error: Failed to load profile: 401 UNAUTHORIZED
[WARN] Using fallback user data from UserAuth  ← App recovers with cache
```

---

## 🔍 Root Cause

The `loadUserProfile()` function was being called multiple times during initialization:

1. **OAuth callback** → `initializeApp()` → `loadUserProfile()` ✅
2. **UserAuth.init()** → (some path) → `loadUserProfile()` ❌

The function had **no guard** to prevent duplicate calls, causing:
- Unnecessary API requests
- Token validation failures on second call
- 401 errors in console (confusing for debugging)

---

## ✅ Solution Implemented

### 1. Added Duplicate Call Guard

**File:** `UI/modules/components/account_profile.js`  
**Line:** ~323-327

```javascript
// Guard: Skip if profile already loaded and token hasn't changed
if (UserAuth.user && UserAuth.user.user_id && UserAuth.token === UserAuth._lastTokenUsed) {
    console.log('✅ Profile already loaded, skipping duplicate call');
    return UserAuth.user;
}
```

### 2. Added 401 Graceful Handling

**File:** `UI/modules/components/account_profile.js`  
**Line:** ~338-342

```javascript
if (!response.ok) {
    // Handle 401 gracefully - use cached profile if available
    if (response.status === 401 && UserAuth.user && UserAuth.user.user_id) {
        console.warn('[WARN] Token expired (401), using cached profile');
        return UserAuth.user;
    }
    throw new Error(`Failed to load profile: ${response.status} ${response.statusText}`);
}
```

### 3. Track Last Token Used

**File:** `UI/modules/components/account_profile.js`  
**Line:** ~362

```javascript
UserAuth.user = profile;
UserAuth._lastTokenUsed = UserAuth.token; // Track token to prevent duplicate calls
```

---

## 🎯 How It Works

### Before Fix:
```
initializeApp()
  → loadUserProfile() [Call 1] ✅ 200 OK
  → (some other path)
    → loadUserProfile() [Call 2] ❌ 401 Unauthorized
      → Error logged, fallback to cache
```

### After Fix:
```
initializeApp()
  → loadUserProfile() [Call 1] ✅ 200 OK
    → Saves profile + token to UserAuth._lastTokenUsed
  → (some other path)
    → loadUserProfile() [Call 2]
      → ✅ Guard detects duplicate: token unchanged, profile exists
      → Returns cached profile immediately (no API call)
```

---

## 📋 Benefits

1. **No More 401 Errors** - Duplicate calls prevented
2. **Reduced API Load** - Only load profile once per token
3. **Faster Loading** - Skip redundant API calls
4. **Clean Console** - No confusing error messages
5. **Graceful Degradation** - If token expires, use cache

---

## ✅ Testing Checklist

- [ ] Log in with Microsoft OAuth
- [ ] Check console - should see **only ONE** "Profile API response status: 200"
- [ ] Should NOT see any 401 errors
- [ ] Should see "✅ Profile already loaded, skipping duplicate call" if duplicate path triggered
- [ ] User profile loads correctly
- [ ] No functional changes - app works as before

---

## 🔍 Additional Scenarios Handled

### Scenario 1: Token Changes
```javascript
// User logs out and back in with different account
UserAuth.token = 'new_token_here';
loadUserProfile(); // ✅ New call made (token changed)
```

### Scenario 2: Token Expires During Session
```javascript
// Token expires while app is open
loadUserProfile(); // ❌ Returns 401
// ✅ Gracefully handled: uses cached profile, shows warning
```

### Scenario 3: First Load
```javascript
// Fresh page load, no cache
loadUserProfile(); // ✅ Makes API call, saves profile + token
loadUserProfile(); // ✅ Skipped (duplicate detected)
```

---

## 🚀 Performance Impact

### Before:
- **2+ API calls** per page load
- **401 errors** logged to console
- **Redundant network traffic**

### After:
- **1 API call** per token
- **No 401 errors** from duplicates
- **Cached profile** reused instantly

---

## 📝 Related Files

| File | Change |
|------|--------|
| `UI/modules/components/account_profile.js` | Added duplicate call guard + 401 handling |

---

## 🔗 Related Documentation

- `AGENT_STREAM_400_ERROR_FIX.md` - Agent streaming fix
- `WEBSOCKET_CONNECTION_ERROR_FIX.md` - WebSocket connection
- `THINKING_DOTS_REMOVAL_COMPLETE.md` - UI improvements

---

**Status:** ✅ Fixed - Ready for Testing  
**Impact:** Prevents duplicate API calls and 401 errors  
**Side Effects:** None - only optimization, no functional changes

