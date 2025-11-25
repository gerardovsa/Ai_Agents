# OAuth Connection Leak Fix - November 25, 2025

## Problem

**Render.com deployment showing "Invalid state parameter" error** during Microsoft OAuth login.

### Root Cause

Connection pool exhaustion due to **multiple connection leaks** in the OAuth flow:

1. **OAuth state storage** (`/api/auth/microsoft/login` - line 384)
2. **Return URL storage** (`/api/auth/microsoft/login` - line 423)
3. **OAuth state validation** (`/api/auth/microsoft/callback` - line 489)
4. **Thread listing** (`/api/threads/list` - line 322)

### Why "Invalid state parameter"?

1. User clicks "Sign in with Microsoft 365"
2. Backend tries to store OAuth state in database
3. **Connection leak** → pool exhausted (2/2 connections used)
4. OAuth callback tries to retrieve state from database
5. **Database query fails** due to no available connections
6. Exception caught, `stored_state` remains `None`
7. State validation fails: `state != stored_state`
8. Returns `{"error": "Invalid state parameter", "success": false}`

## Files Fixed

### 1. `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py`

**Fix 1: OAuth state storage (line 384)**
```python
# BEFORE:
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    conn.close()  # ❌ Never reached if exception before here
except Exception as e:
    logger.warning(f"Failed to store OAuth state: {e}")

# AFTER:
conn = None  # ✅ Initialize outside try block
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()  # Don't close here anymore
except Exception as e:
    logger.warning(f"Failed to store OAuth state: {e}")
finally:
    if conn:
        conn.close()  # ✅ Always closes connection
```

**Fix 2: Return URL storage (line 423)** - Same pattern

**Fix 3: OAuth state validation (line 489)** - Same pattern (MOST CRITICAL)

### 2. `AI_infrastructure/routes/thread_routes.py`

**Fix 4: Thread listing (line 322)**
```python
# BEFORE:
@thread_bp.route('/list', methods=['GET'])
def list_threads():
    try:
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        # ... query execution ...
        cursor.close()
        conn.close()  # ❌ Never reached if exception
        return success_response(...)
    except Exception as e:
        return error_response(...)  # ❌ Connection never closed!

# AFTER:
@thread_bp.route('/list', methods=['GET'])
def list_threads():
    conn = None  # ✅ Initialize outside try block
    try:
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        # ... query execution ...
        return success_response(...)
    except Exception as e:
        return error_response(...)
    finally:
        if conn:
            conn.close()  # ✅ Always closes connection
```

## Pattern: Connection Leak

### ❌ WRONG (causes leaks):
```python
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    # ... database operations ...
    conn.commit()
    conn.close()  # ❌ Skipped if exception raised above
except Exception as e:
    # Handle error
    # ❌ Connection never closed!
```

### ✅ CORRECT (prevents leaks):
```python
conn = None  # ✅ Initialize outside try for finally access
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    # ... database operations ...
    conn.commit()  # Don't close here
except Exception as e:
    # Handle error
finally:
    if conn:
        conn.close()  # ✅ Always closes, even after exception
```

## Testing

### Before Fix (Render):
```
GET /api/auth/microsoft/callback?code=...&state=... 400 BAD REQUEST
Response: {"error": "Invalid state parameter", "success": false}

Console error: "Connection pool exhausted for 'sessions'. Leaked connections: 2"
```

### After Fix (Expected):
```
GET /api/auth/microsoft/callback?code=...&state=... 302 REDIRECT
Redirect to: /?token=eyJ...
User successfully authenticated
```

### Local Testing:
1. Restart Flask: `BISTART`
2. Open `http://localhost:5001`
3. Click "Sign in with Microsoft 365"
4. Complete OAuth flow
5. ✅ Should redirect with token, no state errors

### Render Testing:
1. Wait for auto-deploy from GitHub push (2-3 minutes)
2. Open `https://ai-agents-backend-singapore.onrender.com/`
3. Click "Sign in with Microsoft 365"
4. Complete OAuth flow
5. ✅ Should authenticate successfully

## Impact

**Files with connection leaks found:**
- `microsoft_auth_routes_V2_FIXED.py`: **11 database connections** (3 fixed, 8 remaining)
- `thread_routes.py`: **19 database connections** (1 fixed, 18 remaining)
- `thread_assignment_routes.py`: **1 connection leak** (already fixed in previous commit)

**Priority:**
1. ✅ **CRITICAL (Fixed)**: OAuth flow (prevents authentication)
2. ✅ **HIGH (Fixed)**: Thread listing (prevents UI load)
3. ⚠️ **MEDIUM (Pending)**: Remaining 26 connection leaks in other endpoints

## Next Steps

1. ✅ OAuth authentication should work on Render
2. ✅ Thread listing should work on Render
3. ⏳ Test actual Render deployment after auto-deploy completes
4. 🔜 Fix remaining 26 connection leaks in follow-up commits

## Related Files

- `CONNECTION_LEAK_FIX_NOV25.md` - Previous fix for thread assignment routes
- `RENDER_AUTH_ISSUE_DIAGNOSIS.md` - OAuth troubleshooting guide
- `DATABASE_PATH_FIX_COMPLETE.md` - Supabase PostgreSQL migration docs

---

**Deployed:** November 25, 2025  
**Commit:** 14dd19c  
**Status:** Pushed to GitHub v9 branch (auto-deploys to Render)
