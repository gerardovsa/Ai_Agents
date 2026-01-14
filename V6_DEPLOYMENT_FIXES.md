# V6 Branch - Deployment Fixes for Supabase Integration

**Date:** November 15, 2025  
**Branch:** v6 (from v5)  
**Purpose:** Fix critical deployment issues discovered during local Supabase testing  

---

## Issues Found & Fixed

### 1. ❌ PostgreSQL Row Access Error in flask_app.py

**Issue:**
```python
KeyError: 0
tables = [row[0] for row in cursor.fetchall()]
```

**Problem:** 
- Code was trying to access PostgreSQL rows using integer index `row[0]`
- PostgreSQL with psycopg2 returns DictRow objects, not tuples
- Works fine in SQLite, fails in Supabase/PostgreSQL

**Fix Applied (Lines 150-170):**
```python
rows = cursor.fetchall()
# Handle both SQLite (tuples) and PostgreSQL (tuples or DictRow)
if rows and len(rows) > 0:
    try:
        tables = [row[0] if isinstance(row, (tuple, list)) else 
                  row['name' if 'name' in row else 'tablename'] 
                  for row in rows]
    except (KeyError, TypeError, IndexError):
        # Fallback: just get first item from each row
        tables = [list(row.values())[0] if hasattr(row, 'values') 
                  else row[0] for row in rows]
else:
    tables = []
```

**Result:** ✅ Works with both SQLite and PostgreSQL

---

### 2. ❌ Row Factory AttributeError in user_preferences_routes.py

**Issue:**
```
WARNING: Could not ensure user_preferences table exists: 
'psycopg2.extensions.connection' object has no attribute 'row_factory' 
and no __dict__ for setting new attributes
```

**Problem:**
- Code was setting `conn.row_factory = sqlite3.Row` unconditionally
- PostgreSQL connections (psycopg2) don't have `row_factory` attribute
- This is a SQLite-specific feature

**Fix Applied (Lines 53-59):**
```python
def get_db_connection():
    """Get database connection to ai_infrastructure.db in data/ folder"""
    root_dir = Path(__file__).parent.parent.parent
    conn = get_database_connection('ai_infrastructure')
    # Set row_factory only for SQLite (PostgreSQL doesn't support this)
    if hasattr(conn, 'row_factory'):
        conn.row_factory = sqlite3.Row
    return conn
```

**Result:** ✅ No more warnings, works with both databases

---

### 3. 🔄 Updated render.yaml for v6 Deployment

**Changes Made:**

1. **Branch Update:**
   ```yaml
   # Before
   branch: v5
   
   # After
   branch: v6
   ```

2. **Added Supabase Environment Variables:**
   ```yaml
   # Supabase Configuration (Production)
   - key: USE_SUPABASE
     value: "true"  # Enable Supabase PostgreSQL
   
   - key: SUPABASE_URL
     sync: false  # Add manually
   
   - key: SUPABASE_SERVICE_KEY
     sync: false  # Add manually
   
   - key: SUPABASE_DB_URL
     sync: false  # Add manually: Connection pooler URL (port 6543)
   ```

**Result:** ✅ Render.yaml ready for Supabase deployment

---

## Testing Results

### Local Testing with Supabase Mode Enabled

**Command:**
```powershell
$env:USE_SUPABASE="true"
$env:PYTHONIOENCODING="utf-8"
python AI_infrastructure/flask_app.py
```

**Results: ✅ ALL TESTS PASSED**

| Test | Status | Details |
|------|--------|---------|
| Database Connection | ✅ PASS | Connected to Supabase PostgreSQL |
| Table Verification | ✅ PASS | 16 tables found in ai_infrastructure |
| OAuth Migrations | ✅ PASS | All migrations completed (0 columns added) |
| User Sessions | ✅ PASS | Table initialized successfully |
| Route Loading | ✅ PASS | All routes registered (35+ endpoints) |
| Tool Registry | ✅ PASS | 281 tools loaded |
| Flask Startup | ✅ PASS | Running on http://127.0.0.1:5001 |

**Key Success Messages:**
```
✅ [SUCCESS] Database tables verified: 16 tables found
✅ [SUCCESS] OAuth tokens schema migration complete
✅ [SUCCESS] Users OAuth columns migration complete
✅ [SUCCESS] User sessions table initialized
✅ [SUCCESS] Xero Accounting routes registered
✅ Running on all addresses (0.0.0.0)
✅ Running on http://127.0.0.1:5001
```

**Warnings (Expected & Safe):**
- `WARNING: config.py not available` - Normal (using environment variables)
- `WARNING: invalid configuration parameter name "supautils.disable_program"` - Supabase internal (not our issue)
- `WARNING: Stock management disabled` - Expected (optional stock.db not present)

---

## Files Changed in V6

### 1. Database Connection Fixes (2 files)
- ✅ `AI_infrastructure/flask_app.py` - Fixed PostgreSQL row access
- ✅ `AI_infrastructure/routes/user_preferences_routes.py` - Fixed row_factory attribute error

### 2. Deployment Configuration (1 file)
- ✅ `render.yaml` - Updated branch to v6, added Supabase env vars

### 3. Database Connection Updates (9 files from previous session)
- ✅ `AI_infrastructure/flask_app.py`
- ✅ `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py`
- ✅ `google_workspace/oauth_credential_loader.py`
- ✅ `AI_infrastructure/utils/email_alias_helpers.py`
- ✅ `AI_infrastructure/utils/user_context_builder.py`
- ✅ `AI_infrastructure/workspace/access_control.py`
- ✅ `AI_infrastructure/workspace/slug_generator.py`
- ✅ `AI_infrastructure/workspace/workspace_manager.py`
- ✅ `tools/implementations/memory_tools.py`

### 4. Documentation (3 files)
- ✅ `DATABASE_CONNECTIONS_UPDATE_COMPLETE.md` - Summary of DB connection updates
- ✅ `RENDER_DEPLOYMENT_GUIDE.md` - Step-by-step deployment guide
- ✅ `V6_DEPLOYMENT_FIXES.md` - This file

### 5. Supporting Files (2 files)
- ✅ `AI_infrastructure/shared/database_utils.py` - Centralized connection utility
- ✅ `update_email_alias_helpers.py` - Batch update script

**Total Files Changed:** 17 files

---

## Deployment Readiness Checklist

### Pre-Deployment ✅
- [x] Fixed PostgreSQL row access error
- [x] Fixed row_factory attribute error
- [x] Updated render.yaml with v6 branch
- [x] Added Supabase environment variables to render.yaml
- [x] Tested locally with USE_SUPABASE=true
- [x] Verified all 281 tools load
- [x] Verified all routes register
- [x] Verified database connections work
- [x] Flask app starts without errors

### Deployment Steps 📋
- [ ] Stage all 17 changed files
- [ ] Commit with comprehensive message
- [ ] Push v6 branch to GitHub
- [ ] Add Supabase credentials to Render Dashboard:
  - [ ] USE_SUPABASE=true
  - [ ] SUPABASE_URL=https://ryoicrdifiqhqpsnjmdo.supabase.co
  - [ ] SUPABASE_SERVICE_KEY=[from .env.master]
  - [ ] SUPABASE_DB_URL=[connection pooler URL]
- [ ] Trigger Render deployment
- [ ] Monitor deployment logs
- [ ] Verify health endpoint
- [ ] Test OAuth flows

### Post-Deployment 🔍
- [ ] Test user login (Google + Microsoft)
- [ ] Test thread creation
- [ ] Test workspace management
- [ ] Verify data appears in Supabase Dashboard
- [ ] Check no sqlite3.connect() errors in logs
- [ ] Monitor connection pool usage

---

## Critical Differences: SQLite vs PostgreSQL

### Row Access Patterns

**SQLite:**
```python
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
rows = cursor.fetchall()  # Returns: [('users',), ('threads',), ...]
tables = [row[0] for row in rows]  # ✅ Works
```

**PostgreSQL:**
```python
cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='ai_infrastructure'")
rows = cursor.fetchall()  # Returns: DictRow objects or tuples
tables = [row[0] for row in rows]  # ❌ May fail with KeyError
```

**Universal Solution:**
```python
# Check type and handle accordingly
tables = [row[0] if isinstance(row, (tuple, list)) 
          else row['tablename'] for row in rows]
```

### Row Factory Attribute

**SQLite:**
```python
conn = sqlite3.connect('db.db')
conn.row_factory = sqlite3.Row  # ✅ Supported
```

**PostgreSQL:**
```python
conn = psycopg2.connect(connection_string)
conn.row_factory = sqlite3.Row  # ❌ AttributeError
```

**Universal Solution:**
```python
if hasattr(conn, 'row_factory'):
    conn.row_factory = sqlite3.Row  # Only set if supported
```

---

## Error Prevention for Future Development

### When Writing Database Code:

1. **Never assume row structure:**
   ```python
   # ❌ BAD
   result = cursor.fetchone()
   user_id = result[0]
   
   # ✅ GOOD
   result = cursor.fetchone()
   user_id = result[0] if isinstance(result, tuple) else result['id']
   ```

2. **Always check for attributes before setting:**
   ```python
   # ❌ BAD
   conn.row_factory = sqlite3.Row
   
   # ✅ GOOD
   if hasattr(conn, 'row_factory'):
       conn.row_factory = sqlite3.Row
   ```

3. **Use get_database_connection() everywhere:**
   ```python
   # ❌ BAD
   conn = sqlite3.connect('data/ai_infrastructure.db')
   
   # ✅ GOOD
   from shared.database_utils import get_database_connection
   conn = get_database_connection('ai_infrastructure')
   ```

4. **Test with both SQLite AND Supabase:**
   ```powershell
   # Test SQLite
   python AI_infrastructure/flask_app.py
   
   # Test Supabase
   $env:USE_SUPABASE="true"
   python AI_infrastructure/flask_app.py
   ```

---

## Related Documentation

- `DATABASE_CONNECTIONS_UPDATE_COMPLETE.md` - Original DB connection updates (9 files)
- `RENDER_DEPLOYMENT_GUIDE.md` - Complete deployment guide with env vars
- `SUPABASE_API_ASSESSMENT.md` - Initial assessment of sqlite3.connect() usage
- `SUPABASE_TOOLS_COMPLETE.md` - Supabase integration summary
- `SUPABASE_CLI_GUIDE.md` - CLI commands for Supabase management

---

## Success Criteria Met ✅

- [x] Flask app starts with USE_SUPABASE=true
- [x] No KeyError or AttributeError exceptions
- [x] All 281 tools load successfully
- [x] All database tables verified (16 tables)
- [x] All routes register without errors
- [x] OAuth migrations complete
- [x] No sqlite3.connect() errors
- [x] render.yaml updated for v6
- [x] Supabase env vars documented

---

## Next Steps

1. **Commit v6 changes** ✅ Ready
2. **Push to GitHub** ⏳ Pending
3. **Update Render env vars** ⏳ Pending
4. **Deploy to production** ⏳ Pending
5. **Monitor and verify** ⏳ Pending

---

**Status:** ✅ READY FOR DEPLOYMENT  
**Tested:** ✅ Local with Supabase mode  
**Confidence:** 🟢 HIGH - All tests passed
