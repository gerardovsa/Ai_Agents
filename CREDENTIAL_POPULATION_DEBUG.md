# 🔧 Quick Fix - Credential Population Debug

**Date:** November 29, 2025  
**Issue:** GET /api/auth/credentials/<platform> returning 500 errors  
**Status:** 🔍 DEBUGGING

---

## What I Found

Your browser console shows:
```
GET http://localhost:5001/api/auth/credentials/pinecone 500 (INTERNAL SERVER ERROR)
GET http://localhost:5001/api/auth/credentials/openai 500 (INTERNAL SERVER ERROR)
```

This means the endpoint exists but is crashing on execution.

---

## What I Did

**Added debug logging to the GET endpoint:**

```python
print(f"🔍 [GET CREDENTIALS] Platform: {platform}")
print(f"🔍 [GET CREDENTIALS] Request.user: {getattr(request, 'user', 'NOT SET')}")
print(f"✅ [GET CREDENTIALS] User ID: {user_id}")
print(f"✅ [GET CREDENTIALS] Retrieved credentials: {bool(creds)}")
```

**Added better error handling:**
- Check if `request.user` exists
- Check if `user_id` exists in `request.user`
- Return 401 if authentication issues
- Log exact error details

---

## Next Steps - PLEASE TRY NOW

1. **Refresh the browser page** (F5)

2. **Open Account Settings → Connections tab**

3. **Check the Flask terminal window for debug output**

You should see either:

**Success case:**
```
🔍 [GET CREDENTIALS] Platform: pinecone
🔍 [GET CREDENTIALS] Request.user: {'user_id': 12, 'email': 'gpoli@inhouse.net.au', ...}
✅ [GET CREDENTIALS] User ID: 12
✅ [GET CREDENTIALS] Retrieved credentials: True
```

**Error case:**
```
❌ [GET CREDENTIALS] request.user not set by @require_auth
OR
❌ [GET CREDENTIALS] No user_id in request.user: {...}
```

4. **Send me the output** from the Flask terminal and I'll fix it immediately

---

## Possible Issues

**Issue 1: @require_auth not working**
- The decorator might not be setting `request.user`
- Need to check decorator implementation

**Issue 2: user_id field name mismatch**
- Might be `user_id` vs `id`
- I added fallback: `request.user.get('user_id') or request.user.get('id')`

**Issue 3: Database connection issue**
- Credentials might exist but query is failing
- Debug logs will show if we got past user_id check

---

## Files Modified

- `auth_routes.py` (Lines 568-608) - Added comprehensive debug logging

---

**PLEASE TEST NOW and send me the Flask terminal output!** 🔍
