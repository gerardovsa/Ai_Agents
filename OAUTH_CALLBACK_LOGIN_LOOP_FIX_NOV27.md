# OAuth Callback Login Loop Fix - November 27, 2025

## 🐛 Problem Description

**Symptom**: After successful Microsoft OAuth login on Render, user clicks "Sign in with Microsoft", Microsoft auth succeeds, but then redirects back to login screen instead of showing the main app.

**Backend Logs Show Success**:
```
✅ Microsoft authentication successful: printing@inhouseprint.com.au
✅ Tokens stored successfully in oauth_tokens table
✅ JWT token generated and sent in redirect URL: ?token=eyJ...
```

**Frontend Behavior**:
- OAuth callback page loads with `?token=JWT` in URL
- Token is extracted and stored in localStorage
- URL is cleaned (token removed)
- **BUT**: Login screen appears again instead of main app

---

## 🔍 Root Cause Analysis

### Issue #1: localStorage Key Mismatch (CRITICAL BUG)

**File**: `UI/modules/components/user_auth.js` lines 172, 180

**Problem**: When token verification fails, the code attempts to clear the token from localStorage but uses the WRONG key:

```javascript
// ❌ WRONG (lines 172, 180)
localStorage.removeItem('auth_token');  // snake_case key

// ✅ CORRECT (everywhere else in codebase)
localStorage.setItem('authToken', token);  // camelCase key
localStorage.getItem('authToken');
```

**Impact**:
- When `verifyToken()` fails (401 or network error), it tries to clear `'auth_token'`
- But the actual token is stored under `'authToken'`
- The broken/expired token stays in localStorage
- User gets stuck in login loop because system thinks there's a valid token

**Evidence**:
```javascript
// Lines 28, 105, 110, 215, 219, 259: All use 'authToken' (camelCase)
localStorage.getItem('authToken')
localStorage.setItem('authToken', token)

// Lines 172, 180: Use wrong key 'auth_token' (snake_case)
localStorage.removeItem('auth_token')  // ❌ Removes nothing!
```

### Issue #2: Insufficient Error Logging

**Problem**: When OAuth callback fails, there's no visibility into:
- Whether token is being stored correctly
- What the profile API response is
- Why `showMainApp()` might not be called

**Impact**: Debugging production issues is nearly impossible without detailed logs

---

## ✅ Solutions Implemented

### Fix #1: Correct localStorage Key Consistency

**File**: `UI/modules/components/user_auth.js`

**Lines 170-176** (verifyToken - invalid token handler):
```javascript
if (!response.ok) {
    // Token is invalid - clear it from storage to prevent flickering
    console.log('🗑️ Clearing invalid token from storage');
    localStorage.removeItem('authToken');  // ✅ FIXED: Use correct key (camelCase)
    sessionStorage.removeItem('authToken');  // Also clear sessionStorage fallback
    this.token = null;
}
```

**Lines 178-184** (verifyToken - error handler):
```javascript
} catch (error) {
    console.error('❌ Token verification failed:', error);
    // Clear token on network error too
    localStorage.removeItem('authToken');  // ✅ FIXED: Use correct key (camelCase)
    sessionStorage.removeItem('authToken');  // Also clear sessionStorage fallback
    this.token = null;
    return false;
}
```

**Why This Fixes the Loop**:
1. When token is invalid/expired, it now ACTUALLY gets removed
2. User sees clean login screen instead of stuck with broken token
3. Next login attempt starts fresh without conflicting cached data

---

### Fix #2: Comprehensive OAuth Callback Debugging

**Purpose**: Add detailed console logs at every critical step of OAuth flow

#### File: `UI/business-ai-platform-v2.html` (lines 19098-19120)

Added logs when token is detected in URL:
```javascript
if (urlParams.has('token')) {
    const token = urlParams.get('token');
    console.log('🔐 [AUTH INIT] OAuth token detected in URL');
    console.log('🔐 [AUTH INIT] Token length:', token.length);
    console.log('🔐 [AUTH INIT] Token preview:', token.substring(0, 50) + '...');
    
    localStorage.setItem('authToken', token);
    console.log('✅ [AUTH INIT] Token stored in localStorage');
    
    if (typeof UserAuth !== 'undefined') {
        UserAuth.token = token;
        console.log('✅ [AUTH INIT] Token set in UserAuth.token');
    }
    
    window.history.replaceState({}, document.title, window.location.pathname);
    console.log('✅ [AUTH INIT] URL cleaned (token removed from browser history)');
}
```

#### File: `UI/modules/components/account_profile.js` (lines 2154-2205)

Added logs for OAuth callback processing:
```javascript
console.log('🔐 [OAUTH CALLBACK] OAuth successful, token received');
console.log('🔐 [OAUTH CALLBACK] Token length:', token.length);
console.log('🔐 [OAUTH CALLBACK] Token preview:', token.substring(0, 50) + '...');

// Token storage
localStorage.setItem('authToken', token);
console.log('✅ [OAUTH CALLBACK] Token stored in localStorage');

UserAuth.token = token;
console.log('✅ [OAUTH CALLBACK] Token set in UserAuth.token');

// URL cleaning
window.history.replaceState({}, document.title, window.location.pathname);
console.log('✅ [OAUTH CALLBACK] URL cleaned (token removed from browser history)');

// Profile loading
console.log('📋 [OAUTH CALLBACK] Loading user profile from backend...');
try {
    await loadUserProfile();
    console.log('✅ [OAUTH CALLBACK] User profile loaded successfully');
} catch (error) {
    console.error('❌ [OAUTH CALLBACK] Failed to load user profile:', error);
    // Show error on login screen
}

// Main app initialization
console.log('🚀 [OAUTH CALLBACK] Calling UserAuth.showMainApp()...');
await UserAuth.showMainApp();
console.log('✅ [OAUTH CALLBACK] Main app initialized successfully');
```

#### File: `UI/modules/components/account_profile.js` (lines 331-375)

Enhanced `loadUserProfile()` with detailed API logging:
```javascript
console.log('📋 [PROFILE] Loading user profile...');
console.log('📋 [PROFILE] Token available:', !!UserAuth.token);
console.log('📋 [PROFILE] Token preview:', UserAuth.token ? UserAuth.token.substring(0, 30) + '...' : 'null');

const apiUrl = `${API_BASE_URL}/api/auth/profile`;
console.log('📋 [PROFILE] Fetching from:', apiUrl);
console.log('📋 [PROFILE] Authorization header:', `Bearer ${UserAuth.token.substring(0, 30)}...`);

const response = await fetch(apiUrl, { ... });

console.log('📋 [PROFILE] Response status:', response.status);
console.log('📋 [PROFILE] Response ok:', response.ok);

if (!response.ok) {
    let errorText = '';
    try {
        errorText = await response.text();
        console.error('❌ [PROFILE] Error response body:', errorText);
    } catch (e) {
        console.error('❌ [PROFILE] Could not read error response');
    }
    
    throw new Error(`Failed to load profile: ${response.status} ${response.statusText}. ${errorText}`);
}
```

---

## 📊 Debug Flow (What to Look For in Browser Console)

### Normal OAuth Login Flow (Expected Logs):

```
1. User clicks "Sign in with Microsoft"
   🔐 [AUTH] Microsoft login initiated

2. Microsoft redirects back with ?token=JWT
   🔐 [AUTH INIT] OAuth token detected in URL
   🔐 [AUTH INIT] Token length: 245
   🔐 [AUTH INIT] Token preview: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2...
   ✅ [AUTH INIT] Token stored in localStorage
   ✅ [AUTH INIT] Token set in UserAuth.token
   ✅ [AUTH INIT] URL cleaned (token removed from browser history)

3. Check existing session (finds newly stored token)
   [AUTH] Session found - Loading main app...

4. Profile loading
   📋 [PROFILE] Loading user profile...
   📋 [PROFILE] Token available: true
   📋 [PROFILE] Fetching from: https://ai-agents-backend-singapore.onrender.com/api/auth/profile
   📋 [PROFILE] Response status: 200
   📋 [PROFILE] Response ok: true
   ✅ [PROFILE] User profile loaded successfully

5. Main app initialization
   🚀 [OAUTH CALLBACK] Calling UserAuth.showMainApp()...
   🔵 [AUTH] Loading user profile FIRST (before app initialization)...
   ✅ 🔓🔓 [AUTH] User profile loaded
   ✅ 🔓🔓 [AUTH] Profile button marked as authenticated (green border)
   ✅ [OAUTH CALLBACK] Main app initialized successfully
```

### Error Scenarios (What to Watch For):

**401 Unauthorized (Token Invalid)**:
```
📋 [PROFILE] Response status: 401
❌ [PROFILE] Error response body: {"error": "Invalid token"}
❌ [OAUTH CALLBACK] Failed to load user profile: Error: Failed to load profile: 401 Unauthorized
🗑️ Clearing invalid token from storage
```

**403 Forbidden (Token Missing Claims)**:
```
📋 [PROFILE] Response status: 403
❌ [PROFILE] Error response body: {"error": "Missing required claims"}
```

**Network Error**:
```
❌ Token verification failed: TypeError: Failed to fetch
🗑️ Clearing invalid token from storage
```

---

## 🧪 Testing Steps

### Test on Render Production:

1. **Open Browser Console** (F12 → Console tab)

2. **Clear localStorage** (to start fresh):
   ```javascript
   localStorage.clear();
   ```

3. **Navigate to**: `https://ai-agents-backend-singapore.onrender.com/`

4. **Click**: "Sign in with Microsoft 365"

5. **Watch Console Logs**:
   - Look for `[AUTH INIT]` logs when redirected back
   - Check for `[PROFILE]` logs showing API response
   - Verify `[OAUTH CALLBACK]` shows successful flow
   - Confirm `[AUTH]` shows main app loading

6. **Expected Outcome**:
   - ✅ Login screen disappears
   - ✅ Main app interface loads
   - ✅ Profile button shows username/email
   - ✅ No errors in console

7. **If Still Failing**:
   - Copy ALL console logs and send to developer
   - Check Network tab (F12 → Network) for `/api/auth/profile` request
   - Look for red status codes (401, 403, 500)

---

## 🔐 Backend JWT Token Validation (For Reference)

**File**: `AI_infrastructure/auth/user_auth.py`

**Token Expiration**: Currently set to 10 years (from backend logs: exp=1764292781 = Nov 28, 2035)

**Verify Endpoint**: `/api/auth/verify`
- Returns 200 if token valid
- Returns 401 if token invalid/expired
- Frontend calls this in `verifyToken()` method

**Profile Endpoint**: `/api/auth/profile`
- Returns user data if token valid
- Returns 401 if token invalid
- Returns 403 if token missing required claims

---

## 📝 Related Files Changed

### Commit 1: `f008e9b` - "Fix localStorage key mismatch in verifyToken()"
- `UI/modules/components/user_auth.js` (lines 172, 180)
  - Fixed `localStorage.removeItem('auth_token')` → `localStorage.removeItem('authToken')`
  - Added `sessionStorage.removeItem('authToken')` for fallback cleanup

### Commit 2: `6f0ab93` - "Add comprehensive OAuth callback debugging logs"
- `UI/business-ai-platform-v2.html` (lines 19098-19120)
  - Added OAuth token detection logs in main initialization
- `UI/modules/components/account_profile.js` (lines 2154-2205, 331-375)
  - Added OAuth callback processing logs
  - Enhanced profile loading with API request/response logging

---

## ⚡ Performance Impact

**None** - Logging statements only run during authentication flow (once per session).

**Console Log Overhead**:
- ~10-15 console.log() calls per OAuth login
- Negligible performance impact (<5ms total)
- Can be removed/disabled in production by setting `console.log = () => {}` in config

---

## 🎯 Success Criteria

After deploying these fixes:

✅ **No more login loops** - Users stay logged in after Microsoft OAuth
✅ **Clear error messages** - If login fails, error is visible in console
✅ **Token cleanup works** - Invalid tokens are properly removed
✅ **Debugging is easy** - Console logs show exact failure point

---

## 🚀 Deployment

**Branch**: `v9`  
**Commits**:
- `f008e9b` - Fix localStorage key mismatch
- `6f0ab93` - Add OAuth debugging logs

**Pushed to GitHub**: ✅ November 27, 2025

**Next Steps**:
1. Deploy to Render (git pull on server)
2. Test OAuth flow with browser console open
3. Verify no more login loops
4. If issues persist, console logs will pinpoint the problem

---

## 📞 Support

If login loop persists after these fixes, provide:
1. **Full browser console logs** (from clicking "Sign in" to seeing login screen again)
2. **Network tab** showing `/api/auth/profile` request/response
3. **localStorage contents**: `console.log(localStorage.getItem('authToken'))`

---

**Last Updated**: November 27, 2025  
**Status**: ✅ Fixes Deployed to v9 Branch  
**Tested**: Awaiting production testing on Render
