# Render.com Supabase Connection Fixes - November 16, 2025

## Critical Bugs Fixed

### 1. PostgreSQL Syntax Error in Automation Routes ✅ FIXED
**File:** `AI_infrastructure/routes/automation_routes.py` (line 76)

**Error:**
```
❌ Error initializing automation tables: near "FROM": syntax error
```

**Root Cause:**
Invalid PostgreSQL syntax: `SELECT FROM information_schema.tables`

**Fix:**
Changed to valid syntax: `SELECT 1 FROM information_schema.tables`

```python
# BEFORE (INVALID):
cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'visual_automations'
    )
""")

# AFTER (FIXED):
cursor.execute("""
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'visual_automations'
    )
""")
```

---

### 2. Wrong Database Type Detection in Flask App ✅ FIXED
**File:** `AI_infrastructure/flask_app.py` (line 170)

**Error:**
```
ERROR: no such table: pg_tables
sqlite3.OperationalError: no such table: pg_tables
```

**Root Cause:**
Code was checking `type(conn).__name__ == 'Connection'` to detect SQLite, but:
- SQLite returns `DatabaseConnection` (wrapped class)
- Code defaulted to PostgreSQL query on SQLite connection
- Tried to query `pg_tables` table which doesn't exist in SQLite

**Fix:**
Use `is_using_supabase()` function instead of checking connection type:

```python
# BEFORE (BROKEN):
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table'" 
    if str(type(conn).__name__) == 'Connection' 
    else "SELECT tablename FROM pg_tables WHERE schemaname = 'ai_infrastructure'"
)

# AFTER (FIXED):
from shared.database_utils import is_using_supabase
if is_using_supabase():
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'ai_infrastructure'")
else:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
```

---

### 3. SQLite Fallback Disabled for Debugging ✅ CHANGED
**File:** `AI_infrastructure/shared/database_utils.py` (line 172-180)

**Issue:**
When Supabase connection failed on Render, code was silently falling back to SQLite on persistent disk (`/data/ai_infrastructure.db`). This masked the real Supabase connection issue.

**Change:**
Commented out SQLite fallback and added clear error messages:

```python
# BEFORE:
except Exception as e:
    print(f"⚠️  [DB] Supabase connection failed: {e}")
    print(f"⚠️  [DB] Falling back to SQLite on persistent disk")
    # Fall through to SQLite fallback
    pass

# AFTER:
except Exception as e:
    print(f"❌ [DB] Supabase connection failed: {e}")
    print(f"❌ [DB] CANNOT PROCEED - SQLite fallback disabled for debugging")
    print(f"❌ [DB] Check SUPABASE_DB_URL in environment variables")
    raise ConnectionError(f"Supabase connection failed: {e}")
    
    # SQLITE FALLBACK COMMENTED OUT FOR DEBUGGING
```

**Additional Safety Check:**
Added explicit check to prevent SQLite usage on Render:

```python
# Check if running on Render - FORCE Supabase connection
if os.getenv('RENDER') == 'true':
    raise ConnectionError(
        "Running on Render but Supabase connection failed. "
        "SQLite fallback disabled for debugging. "
        "Check SUPABASE_DB_URL and USE_SUPABASE environment variables."
    )
```

---

## Expected Behavior After Deploy

### ✅ Success Case (Supabase connects):
```
🔷 [DB] Connected to Supabase PostgreSQL (schema: ai_infrastructure)
✅ Automation tables exist in PostgreSQL
INFO:flask_app: [SUCCESS] Database tables verified: X tables found
```

### ❌ Failure Case (Supabase connection issue):
```
❌ [DB] Supabase connection failed: connection to server at "db.ryoicrdifiqhqpsnjmdo.supabase.co" failed
❌ [DB] CANNOT PROCEED - SQLite fallback disabled for debugging
❌ [DB] Check SUPABASE_DB_URL in environment variables
ConnectionError: Supabase connection failed: ...
```

This will make it **immediately obvious** if there's a Supabase configuration issue.

---

## Supabase Connection Checklist

Verify these environment variables are set on Render:

1. ✅ **USE_SUPABASE=true**
   - Enables Supabase mode in `is_using_supabase()`

2. ✅ **SUPABASE_DB_URL**
   - Must be **Session Pooler URL** (IPv4 compatible)
   - Format: `postgresql://postgres.PROJECT:[PASSWORD]@aws-X-region.pooler.supabase.com:5432/postgres`
   - **NOT** the direct database URL (IPv6)

3. ✅ **RENDER=true**
   - Automatically set by Render
   - Triggers Render-specific behavior

---

## Network Troubleshooting

If you see this error:
```
connection to server at "db.ryoicrdifiqhqpsnjmdo.supabase.co" (2406:da1c:f42:ae0f:fd62:38dc:c9dd:8beb), 
port 6543 failed: Network is unreachable
```

**Root Cause:** Using IPv6 direct connection URL instead of IPv4 Session Pooler

**Solution:**
1. Go to Supabase Project Settings → Database
2. Copy **Session Pooler** connection string (port 5432, IPv4)
3. Update `SUPABASE_DB_URL` on Render
4. Redeploy

**Session Pooler Benefits:**
- IPv4 compatible (Render doesn't support IPv6)
- Connection pooling (better performance)
- Transaction mode (recommended for web apps)

---

## Testing Locally

To test Supabase connection locally (without fallback):

```powershell
# Set environment variables
$env:USE_SUPABASE="true"
$env:SUPABASE_DB_URL="postgresql://postgres.PROJECT:[PASSWORD]@aws-X-region.pooler.supabase.com:5432/postgres"

# Start Flask
cd C:\Users\gpoli\GIT\AI_agents
BISTART

# Expected output:
# 🔷 [DB] Connected to Supabase PostgreSQL (schema: ai_infrastructure)
```

---

## Deployment Steps

1. **Commit the fixes:**
   ```powershell
   cd C:\Users\gpoli\GIT\AI_agents
   git add AI_infrastructure/routes/automation_routes.py
   git add AI_infrastructure/flask_app.py
   git add AI_infrastructure/shared/database_utils.py
   git commit -m "Fix Render Supabase connection: PostgreSQL syntax error, database type detection, disable SQLite fallback"
   git push origin v6
   ```

2. **Verify Render environment variables:**
   - `USE_SUPABASE=true`
   - `SUPABASE_DB_URL=postgresql://...pooler.supabase.com:5432/...`

3. **Deploy on Render:**
   - Render will auto-deploy from v6 branch
   - Watch logs for connection messages

4. **Expected log output (success):**
   ```
   🔷 [DB] Connected to Supabase PostgreSQL (schema: ai_infrastructure)
   ✅ Automation tables exist in PostgreSQL
   [SUCCESS] Database tables verified: X tables found
   ```

5. **If connection fails:**
   - Check `SUPABASE_DB_URL` is Session Pooler URL
   - Check Supabase allows connections from Render IPs
   - Check password is correct
   - Review Render logs for specific error

---

## Files Modified

| File | Lines Changed | Description |
|------|---------------|-------------|
| `AI_infrastructure/routes/automation_routes.py` | 76 | Fixed PostgreSQL syntax: `SELECT FROM` → `SELECT 1 FROM` |
| `AI_infrastructure/flask_app.py` | 170-173 | Fixed database type detection using `is_using_supabase()` |
| `AI_infrastructure/shared/database_utils.py` | 172-200 | Disabled SQLite fallback, added clear error messages |

---

## Re-enabling SQLite Fallback (Future)

Once Supabase connection is working, you can re-enable the fallback:

1. Uncomment lines 176-178 in `database_utils.py`
2. Remove the `raise ConnectionError` on line 175
3. Remove the Render check on lines 182-188
4. Change "LOCAL DEV" message back to allow fallback

**Current strategy: Keep fallback disabled until Supabase connection is verified working.**

---

## Status

- ✅ PostgreSQL syntax error fixed
- ✅ Database type detection fixed
- ✅ SQLite fallback disabled for debugging
- ⏳ Awaiting deployment to Render
- ⏳ Awaiting Supabase connection verification

**Next Steps:**
1. Commit and push changes
2. Deploy to Render
3. Check logs for successful Supabase connection
4. Once working, optionally re-enable SQLite fallback

---

**Document Created:** November 16, 2025  
**Branch:** v6  
**Status:** Ready for deployment
