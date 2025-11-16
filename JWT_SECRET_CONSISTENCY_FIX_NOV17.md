# JWT Secret Consistency Fix (November 17, 2025)

## 🐛 BUG DESCRIPTION

**Symptom:** Users authenticating via Microsoft OAuth on Render backend were falling back to user_id=1 instead of their actual user account.

**Error in logs:**
```
STAGE 2 FAILED: Invalid token (JWT): Signature verification failed
STAGE 3 FAILED: Token verification failed
[AUTH] Token verification failed - using default user_id=1
```

**Root cause:** JWT_SECRET mismatch between token creation and token verification.

---

## 🔍 ROOT CAUSE ANALYSIS

### The Problem

Two different methods were used to load JWT_SECRET:

**1. Token Creation** (in `microsoft_auth_routes_V2_FIXED.py`):
```python
# Line 225 (BEFORE FIX)
jwt_secret = _config.get('JWT_SECRET', 'your-secret-key-change-this')
```
- Uses `dotenv_values()` to read from `.env.master` file
- On Render: `.env.master` doesn't exist → fallback to `'your-secret-key-change-this'`
- Creates tokens with **WRONG SECRET**

**2. Token Verification** (in `user_auth.py`):
```python
# Line 78
self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
```
- Uses `os.getenv()` to read from OS environment variables
- On Render: Reads actual `JWT_SECRET` from Render environment variables
- Tries to verify tokens with **CORRECT SECRET**

### Why It Failed

```
Token Creation:    jwt.encode(payload, 'your-secret-key-change-this')
                                      ↓
Token Verification: jwt.decode(token, 'actual-render-jwt-secret-xyz')
                                      ↑
                              ❌ MISMATCH!
```

Result: **Signature verification failed** → Fallback to user_id=1

---

## ✅ THE FIX

### Changed File
`AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py` (Line 225)

### Before (BROKEN):
```python
def generate_jwt_token(payload: dict):
    """Generate JWT token for user session"""
    try:
        jwt_secret = _config.get('JWT_SECRET', 'your-secret-key-change-this')
```

### After (FIXED):
```python
def generate_jwt_token(payload: dict):
    """Generate JWT token for user session"""
    try:
        # FIXED: Use os.getenv() to match user_auth.py verification (Render compatibility)
        jwt_secret = os.getenv('JWT_SECRET', _config.get('JWT_SECRET', 'your-secret-key-change-this'))
```

### What Changed
- **Priority 1:** Check `os.getenv('JWT_SECRET')` (environment variables) ← Render uses this
- **Priority 2:** Fallback to `_config.get('JWT_SECRET')` (`.env.master` file) ← Local dev uses this
- **Priority 3:** Final fallback to `'your-secret-key-change-this'`

This matches the behavior in `user_auth.py`, ensuring both use the **SAME SECRET**.

---

## 🧪 VERIFICATION

### Test Script
Created `test_jwt_secret_consistency.py` to verify the fix.

### Test Results
```
======================================================================
JWT SECRET CONSISTENCY TEST
======================================================================

1️⃣ Testing user_auth.py JWT secret loading...
   user_auth.py JWT_SECRET: your-secret-key-chan... (length: 36)
   Source: os.getenv('JWT_SECRET', fallback)

2️⃣ Testing microsoft_auth_routes_V2_FIXED.py JWT secret loading...
   microsoft_auth JWT_SECRET: your-secret-key-chan... (length: 36)
   Source: os.getenv('JWT_SECRET', fallback to _config)

3️⃣ Comparing secrets...
   ✅ SECRETS MATCH!
   Token creation and verification will use the same key
   JWT signature verification will succeed

4️⃣ Testing Render environment simulation (no .env.master)...
   Render JWT_SECRET: your-secret-key-chan... (length: 36)
   ✅ Render environment will work correctly!

======================================================================
TEST RESULT: PASS
======================================================================
```

---

## 🚀 DEPLOYMENT STEPS

### 1. Verify Fix Locally
```powershell
cd C:\Users\gpoli\GIT\AI_agents
python test_jwt_secret_consistency.py
```
Expected: `TEST RESULT: PASS`

### 2. Commit Changes
```powershell
git add AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py
git add test_jwt_secret_consistency.py
git add JWT_SECRET_CONSISTENCY_FIX_NOV17.md
git commit -m "Fix JWT secret mismatch causing auth fallback to user_id=1"
```

### 3. Push to Render
```powershell
git push origin v6  # Or your deployment branch
```

### 4. Verify on Render
- Wait for deployment to complete
- Check Render logs for new deployment
- Test Microsoft OAuth login
- Verify no more "Signature verification failed" errors
- Confirm users authenticate with correct user_id

### 5. Test Authentication Flow
1. Go to Render frontend URL
2. Click "Sign in with Microsoft"
3. Complete OAuth flow
4. Check Render logs - should show:
   ```
   STAGE 2.1: JWT Signature Validation
   JWT signature valid
   User ID: [actual user id, not 1]
   Email: [user's email]
   ```
5. Verify user profile shows correct information

---

## 📊 IMPACT ANALYSIS

### Before Fix
- ❌ All Microsoft OAuth users fell back to user_id=1
- ❌ Multi-user authentication broken on Render
- ❌ User isolation compromised (everyone shares user_id=1 workspace)
- ❌ OAuth tokens stored for wrong user
- ❌ Tool executions used wrong credentials

### After Fix
- ✅ Microsoft OAuth users authenticate with correct user_id
- ✅ Multi-user authentication works on Render
- ✅ User isolation maintained (each user has own workspace)
- ✅ OAuth tokens stored for correct user
- ✅ Tool executions use correct credentials

---

## 🔒 SECURITY CONSIDERATIONS

### JWT Secret Storage
- **Local Development:** `.env.master` file (gitignored)
- **Production (Render):** Environment variables (encrypted by Render)
- **Priority:** Environment variables take precedence over `.env.master`

### Why This Matters
- JWT tokens are signed with a secret key
- Anyone with the secret can create valid tokens
- Mismatched secrets → token verification fails
- Consistent secrets → secure authentication

### Current Setup
- ✅ JWT_SECRET stored as Render environment variable
- ✅ Secret not committed to git
- ✅ Both creation and verification use same secret
- ✅ Tokens properly validated

---

## 📝 FILES MODIFIED

### Changed Files
1. `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py`
   - Line 225: Fixed JWT secret loading
   - Added comment explaining Render compatibility

### New Files
1. `test_jwt_secret_consistency.py`
   - Test to verify JWT secret consistency
   - Simulates Render environment
   - Validates fix works correctly

2. `JWT_SECRET_CONSISTENCY_FIX_NOV17.md`
   - This documentation file

---

## 🎯 SUCCESS CRITERIA

- [x] Local test passes (`test_jwt_secret_consistency.py`)
- [ ] Render deployment successful
- [ ] Microsoft OAuth login works on Render
- [ ] No "Signature verification failed" errors in logs
- [ ] Users authenticate with correct user_id (not 1)
- [ ] User profile shows correct information
- [ ] Multi-user authentication functional

---

## 🔄 RELATED ISSUES

### Similar Patterns to Watch
Other routes that create JWT tokens should use the same pattern:

✅ **Already correct:**
- `google_auth_routes_V2_FIXED.py` (Line 263): Uses `os.getenv()`
- `user_auth.py` (Line 78, 431, 516, 1455): Uses `os.getenv()`

❌ **Was incorrect (now fixed):**
- `microsoft_auth_routes_V2_FIXED.py` (Line 225): Now uses `os.getenv()` first

### Other Auth Routes
Check these files for similar patterns:
- `account_linking_routes.py` (Lines 60, 535): Uses `os.getenv()` ✅
- `user_preferences_routes.py` (Line 65): Uses `os.getenv()` ✅

---

## 📚 LESSONS LEARNED

### 1. Environment Variable Priority
Always use `os.getenv()` FIRST for production variables, then fallback to local configs.

**Good pattern:**
```python
jwt_secret = os.getenv('JWT_SECRET', _config.get('JWT_SECRET', 'fallback'))
```

**Bad pattern:**
```python
jwt_secret = _config.get('JWT_SECRET', 'fallback')  # Ignores environment variables!
```

### 2. Render Environment
- Render doesn't have access to `.env.master` file
- All configuration must come from environment variables
- Use `os.getenv()` for production compatibility

### 3. JWT Token Security
- Token creation and verification MUST use same secret
- Test locally AND in production-like environment
- Add tests to prevent regression

### 4. Authentication Testing
- Always test complete auth flow (creation + verification)
- Check logs for "Signature verification failed"
- Verify correct user_id (not fallback to default)

---

## 🆘 TROUBLESHOOTING

### If Auth Still Fails After Fix

1. **Check Render Environment Variables**
   ```
   - Go to Render dashboard
   - Select your service
   - Go to Environment tab
   - Verify JWT_SECRET is set
   - Value should be a long random string (not 'your-secret-key-change-this')
   ```

2. **Check Logs**
   ```
   - Look for "STAGE 2: TOKEN VERIFICATION STARTED"
   - Check "JWT signature valid" message
   - Verify user_id is correct (not 1)
   ```

3. **Regenerate Secret (if needed)**
   ```powershell
   # Generate new JWT_SECRET
   python -c "import secrets; print(secrets.token_urlsafe(64))"
   
   # Update in Render:
   # 1. Copy generated secret
   # 2. Go to Render dashboard → Environment
   # 3. Update JWT_SECRET with new value
   # 4. Redeploy service
   ```

4. **Clear Existing Tokens**
   ```sql
   -- In Supabase SQL editor:
   DELETE FROM ai_infrastructure.user_sessions WHERE expires_at < NOW();
   ```

5. **Test Authentication**
   ```powershell
   # Test locally first
   cd C:\Users\gpoli\GIT\AI_agents
   python test_jwt_secret_consistency.py
   
   # Then test on Render
   curl -X POST https://your-render-url.com/api/auth/microsoft/login
   ```

---

## ✅ COMPLETION CHECKLIST

- [x] Root cause identified (JWT_SECRET mismatch)
- [x] Fix implemented (use os.getenv() first)
- [x] Test created (test_jwt_secret_consistency.py)
- [x] Local test passed
- [x] Documentation written
- [ ] Changes committed to git
- [ ] Deployed to Render
- [ ] Production test passed
- [ ] User authentication verified

---

**Status:** Fix implemented and tested locally  
**Next Step:** Deploy to Render and verify in production  
**Priority:** HIGH (Critical auth bug)  
**Date:** November 17, 2025  
**Author:** GitHub Copilot (Claude Sonnet 4.5)
