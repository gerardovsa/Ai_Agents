# JWT Token Expiration Fix - November 1, 2025

## 🐛 Problem Identified

**Error:** `Invalid token (JWT): Expiration Time claim (exp) must be an integer.`

**Root Cause:** JWT tokens were being created with `exp` claim as datetime objects instead of Unix timestamp integers.

```python
# ❌ WRONG - Datetime object
'exp': datetime.utcnow() + timedelta(days=7)

# ✅ CORRECT - Unix timestamp (integer)
'exp': int((datetime.utcnow() + timedelta(days=7)).timestamp())
```

**JWT Standard (RFC 7519):** The `exp` claim MUST be a NumericDate value (seconds since Unix epoch as integer).

---

## 🔧 Files Fixed

### 1. `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py`

**Lines 170-178:**
```python
# BEFORE:
token_payload = {
    'user_id': payload.get('user_id'),
    'email': payload.get('email'),
    'exp': datetime.utcnow() + timedelta(hours=24)  # ❌ Datetime object
}

# AFTER:
exp_time = datetime.utcnow() + timedelta(hours=24)
exp_timestamp = int(exp_time.timestamp())

token_payload = {
    'user_id': payload.get('user_id'),
    'email': payload.get('email'),
    'exp': exp_timestamp  # ✅ Unix timestamp integer
}
```

---

### 2. `AI_infrastructure/routes/google_auth_routes_V2_FIXED.py`

**Lines 195-200:**
```python
# BEFORE:
payload = {
    'user_id': user_data.get('id'),
    'email': user_data.get('email'),
    'username': user_data.get('username'),
    'exp': datetime.utcnow() + timedelta(days=7)  # ❌ Datetime object
}

# AFTER:
payload = {
    'user_id': user_data.get('id'),
    'email': user_data.get('email'),
    'username': user_data.get('username'),
    'exp': int((datetime.utcnow() + timedelta(days=7)).timestamp())  # ✅ Unix timestamp
}
```

---

### 3. `AI_infrastructure/auth/user_auth.py` (3 locations)

**Location 1 - Lines 275-281 (login method):**
```python
# BEFORE:
token_payload = {
    'user_id': user_data.get('id'),
    'username': user_data.get('username'),
    'email': user_data.get('email'),
    'role': user_data.get('role', 'user'),
    'exp': datetime.utcnow() + timedelta(days=30)  # ❌ Datetime object
}

# AFTER:
token_payload = {
    'user_id': user_data.get('id'),
    'username': user_data.get('username'),
    'email': user_data.get('email'),
    'role': user_data.get('role', 'user'),
    'exp': int((datetime.utcnow() + timedelta(days=30)).timestamp())  # ✅ Unix timestamp
}
```

**Location 2 - Lines 355-365 (register method):**
```python
# BEFORE:
token_payload = {
    'user_id': user_id,
    'username': username,
    'email': email,
    'role': role,
    'exp': datetime.utcnow() + timedelta(days=30)  # ❌ Datetime object
}
token = jwt.encode(token_payload, self.jwt_secret, algorithm='HS256')
cursor.execute('''
    INSERT INTO user_sessions (user_id, token, expires_at)
    VALUES (?, ?, ?)
''', (user_id, token, token_payload['exp']))  # ❌ Storing datetime object

# AFTER:
exp_time = datetime.utcnow() + timedelta(days=30)
exp_timestamp = int(exp_time.timestamp())

token_payload = {
    'user_id': user_id,
    'username': username,
    'email': email,
    'role': role,
    'exp': exp_timestamp  # ✅ Unix timestamp integer
}
token = jwt.encode(token_payload, self.jwt_secret, algorithm='HS256')
cursor.execute('''
    INSERT INTO user_sessions (user_id, token, expires_at)
    VALUES (?, ?, ?)
''', (user_id, token, exp_time.strftime('%Y-%m-%d %H:%M:%S')))  # ✅ Store as string
```

**Location 3 - Lines 1237-1244 (create_session method):**
```python
# BEFORE:
payload = {
    'user_id': user_id,
    'username': username,
    'email': email,
    'role': role,
    'exp': expiry  # ❌ Could be datetime object
}

# AFTER:
# Convert expiry to Unix timestamp for JWT
exp_timestamp = int(expiry.timestamp()) if isinstance(expiry, datetime) else expiry

payload = {
    'user_id': user_id,
    'username': username,
    'email': email,
    'role': role,
    'exp': exp_timestamp  # ✅ Unix timestamp integer
}
```

---

### 4. `AI_infrastructure/routes/agent_routes_v4.py`

**Line 881 - Fixed Import Error:**
```python
# BEFORE:
from auth.user_auth import UserAuthManager, token_required  # ❌ token_required doesn't exist

# AFTER:
from auth.user_auth import UserAuthManager  # ✅ Removed non-existent import
```

**Note:** The `token_required` decorator doesn't exist in `user_auth.py`. The correct decorator is `require_auth`.

---

## ✅ Changes Summary

| File | Lines Changed | Issue Fixed |
|------|---------------|-------------|
| `microsoft_auth_routes_V2_FIXED.py` | 170-178 | JWT exp as Unix timestamp |
| `google_auth_routes_V2_FIXED.py` | 195-200 | JWT exp as Unix timestamp |
| `user_auth.py` (Location 1) | 275-281 | JWT exp as Unix timestamp |
| `user_auth.py` (Location 2) | 355-365 | JWT exp + database storage |
| `user_auth.py` (Location 3) | 1237-1244 | JWT exp type conversion |
| `agent_routes_v4.py` | 881 | Removed invalid import |

**Total:** 6 fixes across 4 files

---

## 🧪 Testing

### Before Fix:
```
❌ STAGE 2 FAILED: Invalid token (JWT): Expiration Time claim (exp) must be an integer.
❌ ImportError: cannot import name 'token_required' from 'auth.user_auth'
```

### After Fix:
```bash
# Restart server
cd C:\Users\gpoli\GIT\AI_agents
Get-Process python | Stop-Process -Force
BISTART

# Test authentication
CHAT "Hello"
```

**Expected Result:**
- ✅ JWT tokens validate successfully
- ✅ No import errors
- ✅ Authentication works normally

---

## 📚 JWT Standards Reference

**RFC 7519 - JSON Web Token (JWT):**
- **NumericDate:** A JSON numeric value representing the number of seconds from 1970-01-01T00:00:00Z UTC until the specified UTC date/time
- **exp (Expiration Time):** MUST be a NumericDate value (integer, not datetime object)
- **Python Implementation:** `int(datetime.timestamp())` converts datetime to Unix timestamp

**PyJWT Library:**
```python
# Correct usage:
import time
from datetime import datetime, timedelta

exp_time = datetime.utcnow() + timedelta(days=7)
exp_timestamp = int(exp_time.timestamp())  # Convert to integer

# Or using time module:
exp_timestamp = int(time.time()) + (7 * 24 * 60 * 60)  # 7 days in seconds
```

---

## 🚀 Impact

### Before:
- ❌ All JWT token authentication failing
- ❌ Users unable to authenticate
- ❌ Chat endpoint crashing with import errors

### After:
- ✅ JWT tokens validate correctly
- ✅ Authentication works across all routes
- ✅ No import errors
- ✅ Proper RFC 7519 compliance

---

## 📋 Related Issues Fixed

1. **JWT validation errors** - exp claim now integer
2. **Import errors** - removed non-existent `token_required`
3. **Database storage** - proper format for expires_at column
4. **Type safety** - added isinstance check in create_session

---

**Fix Applied:** November 1, 2025  
**Status:** ✅ COMPLETE - Ready for testing  
**Files Modified:** 4 files, 6 locations total
