# UI Console Errors Analysis & Fixes

**Date:** November 14, 2025  
**Status:** 🔧 IN PROGRESS  
**Branch:** v5

---

## 🚨 Critical Issues Found

### 1. ✅ FIXED - Missing token_polling.js (404 Error)
**Error:**
```
GET https://ai-agents-backend-singapore.onrender.com/token_polling.js 
net::ERR_ABORTED 404 (Not Found)
```

**Root Cause:** Script reference in HTML but file doesn't exist

**Fix Applied (Commit 721e694):**
- Removed `<script src="token_polling.js"></script>` from HTML
- Functionality now integrated into auth module

---

### 2. ⚠️ IN PROGRESS - Duplicate HTML Element IDs

**Errors:**
```
[DOM] Found 2 elements with non-unique id #prompt-form
[DOM] Found 2 elements with non-unique id #prompt-title
[DOM] Found 2 elements with non-unique id #prompt-category
[DOM] Found 2 elements with non-unique id #prompt-visibility
[DOM] Found 2 elements with non-unique id #prompt-short-desc
[DOM] Found 2 elements with non-unique id #prompt-tags
[DOM] Found 2 elements with non-unique id #prompt-text
[DOM] Found 2 elements with non-unique id #type-full
[DOM] Found 2 elements with non-unique id #type-quick
```

**Root Cause:** 
- Prompt Library modal HTML exists in TWO places:
  1. Static HTML in `business-ai-platform-v2.html` (lines ~34115-34242)
  2. Dynamically injected by `prompt-library.js` module

**Fix Required:**
- Remove duplicate static HTML modal
- Keep only the JavaScript-injected version
- JavaScript injection ensures proper initialization order

**Files to Modify:**
- `UI/business-ai-platform-v2.html` - Remove lines 34115-34242

---

### 3. 🔴 CRITICAL - 500 Internal Server Error on Thread Assignments

**Error:**
```
GET https://ai-agents-backend-singapore.onrender.com/api/thread-assignments/list?user_id=1
500 (Internal Server Error)
```

**Appears:** 2 times in console (once on page load, once after OAuth failure)

**Impact:** Prevents multi-agent system from loading thread assignments

**Root Cause:** Likely database error or missing table on Render

**Fix Required:**
- Check if `thread_assignments` table exists in `/data/ai_infrastructure.db`
- Verify table schema matches code expectations
- Add error handling in backend route

**Backend File:** `AI_infrastructure/routes/thread_assignment_routes.py`

---

### 4. 🔴 CRITICAL - 401 Unauthorized on User Profile

**Error:**
```
GET https://ai-agents-backend-singapore.onrender.com/api/auth/profile
401 (Unauthorized)
```

**Impact:** User authentication fails, no user data loaded

**Related Warning:**
```
⚠️ [USER CHECK] Failed to fetch profile from backend
❌ [THREADS] Cannot load threads: user_id not available
⚠️ [THREADS] UserAuth.user: null
```

**Root Cause:** 
- OAuth authentication failing (redirected with `?error=oauth_failed`)
- No valid JWT token in request
- Session not established

**Fix Required:**
1. Verify OAuth redirects use HTTPS (already fixed in commit d060c78)
2. Check JWT token generation and storage
3. Verify `/api/auth/profile` route requires valid token
4. Check if OAuth callback properly creates session

**Backend Files:**
- `AI_infrastructure/routes/auth_routes.py` - Profile endpoint
- `AI_infrastructure/routes/google_auth_routes_V2_FIXED.py` - OAuth callback
- `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py` - OAuth callback

---

### 5. 🔴 CRITICAL - OAuth Failure Redirect

**URL:** `?error=oauth_failed`

**Indicates:** OAuth flow failed before or during token exchange

**Possible Causes:**
1. ❌ redirect_uri mismatch (should be fixed with HTTPS changes)
2. ❌ Invalid client credentials
3. ❌ User denied permission
4. ❌ Token exchange failed
5. ❌ Database error storing OAuth tokens

**Verification Steps:**
```bash
# Test Google OAuth login
curl -v https://ai-agents-backend-singapore.onrender.com/api/auth/google/login

# Test Microsoft OAuth login
curl -v https://ai-agents-backend-singapore.onrender.com/api/auth/microsoft/login

# Check if redirect_uri in response uses HTTPS
# Should see: redirect_uri=https://ai-agents-backend-singapore.onrender.com/...
```

---

## 📋 Fix Priority Order

1. **✅ HIGH - Remove duplicate prompt modal** (prevents DOM conflicts)
2. **🔴 CRITICAL - Fix 500 error on /api/thread-assignments/list** (blocks multi-agent)
3. **🔴 CRITICAL - Fix 401 error on /api/auth/profile** (blocks user auth)
4. **🔴 CRITICAL - Debug OAuth failure** (blocks all authentication)

---

## 🔧 Detailed Fix Plan

### Fix #1: Remove Duplicate Prompt Modal (IN PROGRESS)

**Step 1:** Remove static HTML modal from `UI/business-ai-platform-v2.html`

**Lines to remove:** ~34115-34242

**Replace with:**
```html
<!-- ==================== PROMPT LIBRARY MODAL ==================== -->
<!-- Modal is dynamically injected by prompt-library.js module -->
<!-- This prevents duplicate IDs and ensures proper initialization -->
```

**Verification:**
```javascript
// After fix, this should return 1 (not 2)
document.querySelectorAll('#prompt-form').length
document.querySelectorAll('#prompt-title').length
```

---

### Fix #2: Fix Thread Assignments 500 Error

**Check database table:**
```bash
# On Render
sqlite3 /data/ai_infrastructure.db "SELECT name FROM sqlite_master WHERE type='table' AND name='thread_assignments';"
```

**Check route error handling:**
```python
# AI_infrastructure/routes/thread_assignment_routes.py
@thread_assignment_bp.route('/list', methods=['GET'])
def get_thread_assignments():
    try:
        user_id = request.args.get('user_id')
        # ... existing code ...
        return jsonify(assignments)
    except Exception as e:
        logger.error(f"Error fetching thread assignments: {e}")
        return jsonify({'error': str(e), 'assignments': []}), 200  # Return empty instead of 500
```

---

### Fix #3: Fix User Profile 401 Error

**Add better error logging:**
```python
# AI_infrastructure/routes/auth_routes.py
@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    try:
        # Log the incoming request
        logger.info(f"Profile request headers: {dict(request.headers)}")
        
        # Check for token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            logger.warning("No authorization token provided")
            return jsonify({'error': 'No token provided'}), 401
        
        # ... rest of code ...
    except Exception as e:
        logger.error(f"Profile fetch error: {e}")
        return jsonify({'error': str(e)}), 500
```

---

### Fix #4: Debug OAuth Failure

**Check OAuth callback logs on Render:**
```bash
# Look for these log messages:
# - "OAuth callback received with code"
# - "Token exchange successful"
# - "User authenticated successfully"
# - Any error messages with full stack trace
```

**Common issues:**
1. **HTTPS mismatch** - Already fixed (commit d060c78)
2. **Token storage failure** - Check if `oauth_tokens` table exists
3. **Scope mismatch** - Verify requested scopes match Google/Azure console
4. **Expired credentials** - Check if client secrets are valid

---

## 🧪 Testing Checklist

After fixes applied:

### UI Tests:
- [ ] No 404 errors in console
- [ ] No duplicate ID warnings in console
- [ ] Prompt library modal opens correctly
- [ ] Only ONE prompt form exists in DOM

### Backend Tests:
- [ ] `/api/thread-assignments/list?user_id=1` returns 200
- [ ] `/api/auth/profile` with valid token returns 200
- [ ] Google OAuth login redirects with HTTPS
- [ ] Microsoft OAuth login redirects with HTTPS
- [ ] OAuth callback creates valid session
- [ ] JWT token stored in localStorage
- [ ] User data loaded successfully

### Integration Tests:
- [ ] Can authenticate with Google
- [ ] Can authenticate with Microsoft
- [ ] Multi-agent columns load properly
- [ ] Thread assignments display correctly
- [ ] No errors in browser console
- [ ] No 500 errors in Render logs

---

## 📝 Files Modified (Current Session)

1. `UI/business-ai-platform-v2.html` 
   - ✅ Removed token_polling.js reference
   - ⚠️ IN PROGRESS: Removing duplicate modal

2. `AI_infrastructure/routes/google_auth_routes_V2_FIXED.py`
   - ✅ Fixed HTTPS redirects (commit d060c78)

3. `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py`
   - ✅ Fixed HTTPS redirects (commit d060c78)

4. `AI_infrastructure/routes/oauth_routes.py`
   - ✅ Fixed HTTPS redirects (commit d060c78)

---

## 🚀 Next Steps

1. **Complete duplicate modal removal**
2. **Test locally** to verify no duplicate ID errors
3. **Fix thread assignments 500 error**
4. **Add OAuth debug logging**
5. **Deploy to Render**
6. **Monitor logs** for OAuth flow
7. **Test authentication** end-to-end

---

**Status:** Partial fixes committed. Monitoring Render deployment for OAuth and backend errors.

**Latest Commits:**
- `721e694` - Fix: Remove missing token_polling.js (404 error)
- `c42aea2` - Add comprehensive documentation for Render deployment fixes
- `d060c78` - Fix OAuth redirects to use HTTPS on Render
- `7f8dab0` - Fix CRITICAL SyntaxError in user_auth.py
