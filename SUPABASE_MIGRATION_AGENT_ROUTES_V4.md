# Supabase Migration: agent_routes_v4.py

**Date:** November 20, 2025  
**Status:** ✅ **COMPLETE**

## Overview

Migrated `agent_routes_v4.py` from SQLite-specific operations to Supabase-compatible database operations using the existing `get_database_connection()` abstraction layer.

---

## Changes Made

### **Before (SQLite-only):**
- Used `execute_sqlite_update()` with file paths
- Used `get_sessions_database_path()` to get SQLite file paths
- Passed database file paths to `ThreadManager()`

### **After (Supabase-compatible):**
- Uses `get_database_connection()` which auto-detects SQLite vs Supabase
- Direct connection management with proper commit/close
- `ThreadManager()` uses internal `get_database_connection()` call

---

## Specific Changes

### **Change #1: Auto-save thread after completion (Lines 1416-1433)**

**OLD CODE:**
```python
from utils.database_helpers import execute_sqlite_update, get_sessions_database_path

db_path = get_sessions_database_path()
update_query = """
    UPDATE sessions.threads 
    SET updated_at = CURRENT_TIMESTAMP
    WHERE thread_slug = %s
"""
params = [thread_slug]
execute_sqlite_update(db_path, update_query, params)
```

**NEW CODE:**
```python
# Uses get_database_connection (auto-detects Supabase/SQLite)
conn = get_database_connection('sessions')
cursor = conn.cursor()

update_query = """
    UPDATE threads 
    SET updated_at = CURRENT_TIMESTAMP
    WHERE thread_slug = %s
"""

cursor.execute(update_query, (thread_slug,))
conn.commit()
cursor.close()
conn.close()
```

**Benefits:**
- Works with both SQLite (local dev) and Supabase (Render)
- Proper connection lifecycle (commit/close)
- Removed `sessions.` schema prefix (handled by search_path)

---

### **Change #2: ThreadManager initialization (Lines 1920-1926)**

**OLD CODE:**
```python
from thread_manager import ThreadManager
from utils.database_helpers import get_sessions_database_path

thread_mgr = ThreadManager(get_sessions_database_path())
```

**NEW CODE:**
```python
from thread_manager import ThreadManager

thread_mgr = ThreadManager()  # Uses get_database_connection() internally
```

**Benefits:**
- Removed unnecessary import
- `ThreadManager._get_connection()` already uses `get_database_connection()`
- Simpler, cleaner code

---

## Already Supabase-Compatible

These sections were **already correct** and didn't need changes:

### ✅ **Thread context loading (Line 1139)**
```python
conn = get_database_connection('sessions')
cursor = conn.cursor()

cursor.execute("""
    SELECT synergy_card_id, workflow_slug, automation_slug, internal_doc_slug
    FROM threads 
    WHERE thread_slug = %s
    LIMIT 1
""", (str(thread_slug),))
```

### ✅ **Synergy session loading (Line 1167)**
```python
conn = get_database_connection('synergy_sessions')
cursor = conn.cursor()

cursor.execute("""
    SELECT title, description, project_name, priority, status
    FROM synergy_sessions.synergy_sessions 
    WHERE session_id = %s
""", (synergy_card_id,))
```

---

## How It Works

### **Database Auto-Detection**

The `get_database_connection()` function automatically detects the environment:

```python
from shared.database_utils import get_database_connection, is_using_supabase

# Auto-detects based on environment variables
if is_using_supabase():
    # Returns psycopg2.Connection (PostgreSQL/Supabase)
    # Uses connection pooling for performance
    conn = get_supabase_connection(schema_name)
else:
    # Returns sqlite3.Connection (Local dev)
    # Uses data/{db_name}.db file
    conn = get_sqlite_connection(db_path)
```

**Environment Detection:**
- **Local Dev**: `USE_SUPABASE` not set → SQLite (`data/sessions.db`)
- **Render Deploy**: `USE_SUPABASE=true` → Supabase PostgreSQL

---

## Testing

### **Local Development (SQLite)**
```powershell
# Ensure USE_SUPABASE is NOT set
$env:USE_SUPABASE = $null

# Start Flask server
cd C:\Users\gpoli\GIT\AI_agents
BISTART

# Test agent streaming
# Open browser: http://localhost:5001
# Send message to agent → Should save to data/sessions.db
```

### **Render Deployment (Supabase)**
```bash
# Environment variables set on Render:
USE_SUPABASE=true
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Deploy to Render → Should use Supabase connection pool
```

### **Verify Database Operations**

**Check thread auto-save:**
```sql
-- SQLite (local)
SELECT thread_slug, updated_at FROM threads ORDER BY updated_at DESC LIMIT 10;

-- Supabase (Render)
SELECT thread_slug, updated_at FROM sessions.threads ORDER BY updated_at DESC LIMIT 10;
```

**Check message saves:**
```sql
-- SQLite (local)
SELECT thread_slug, role, created_at FROM messages ORDER BY created_at DESC LIMIT 20;

-- Supabase (Render)
SELECT thread_slug, role, created_at FROM sessions.messages ORDER BY created_at DESC LIMIT 20;
```

---

## Remaining SQLite-Specific Code (Other Files)

These files may still have SQLite-specific code and should be reviewed:

### ⚠️ **Files to Check:**

1. **`AI_infrastructure/thread_manager.py`**
   - Uses `get_database_connection()` ✅
   - But has `sqlite3.Row` for row_factory (may need adjustment for Supabase)

2. **`AI_infrastructure/core/session_database.py`**
   - **NOT USED** - Has full implementation but never called
   - If activated, needs Supabase migration

3. **`AI_infrastructure/core/session_persistence.py`**
   - **IN-MEMORY ONLY** - Doesn't use database at all
   - Should be replaced with `unified_session_manager.py` calls

4. **`AI_infrastructure/core/session_handler.py`**
   - **IN-MEMORY ONLY** - No persistence
   - Should use `unified_session_manager.py` instead

5. **`AI_infrastructure/utils/database_helpers.py`**
   - May have SQLite-specific helper functions
   - Check `execute_sqlite_update()`, `execute_sqlite_query()` usage

---

## Migration Checklist

- [x] Replace `execute_sqlite_update()` with `get_database_connection()`
- [x] Remove `get_sessions_database_path()` imports
- [x] Update ThreadManager initialization
- [x] Remove schema prefixes (`sessions.threads` → `threads`)
- [x] Use tuple parameters `(param,)` instead of list `[param]`
- [ ] Test locally with SQLite
- [ ] Test on Render with Supabase
- [ ] Verify thread auto-save works
- [ ] Verify message persistence works
- [ ] Check connection pooling metrics (Supabase)

---

## Performance Notes

### **Connection Pooling (Supabase)**
- `get_database_connection()` uses connection pooling for Supabase
- Connections are reused, not created fresh each time
- Pool stats tracked: `connections_acquired`, `total_wait_time`
- Default pool size: 10 connections (configurable)

### **SQLite Optimizations (Local)**
- WAL mode enabled for concurrent access
- 64MB cache size
- Memory temp store
- Synchronous=NORMAL for speed

---

## Key Takeaways

1. **`get_database_connection()` is the ONLY way to get connections**
   - Never use `sqlite3.connect()` directly
   - Never use `psycopg2.connect()` directly
   - Always use `get_database_connection(db_name)`

2. **Schema prefixes handled automatically**
   - SQLite: No schema concept, uses database name
   - Supabase: `SET search_path TO {schema}, public` applied automatically
   - Write queries without schema prefix: `UPDATE threads` (not `UPDATE sessions.threads`)

3. **Parameter style is consistent**
   - Both SQLite and Supabase use `%s` placeholders
   - Pass parameters as tuple: `cursor.execute(query, (param1, param2))`

4. **Always close connections**
   - SQLite: File handles released
   - Supabase: Connections returned to pool

---

## Next Steps

1. **Test the changes locally:**
   ```powershell
   cd C:\Users\gpoli\GIT\AI_agents
   BISTART
   # Send messages to agents → Check data/sessions.db
   ```

2. **Deploy to Render:**
   ```bash
   git add AI_infrastructure/routes/agent_routes_v4.py
   git commit -m "Migrate agent_routes_v4 to Supabase-compatible operations"
   git push origin v6
   # Render auto-deploys → Uses Supabase
   ```

3. **Monitor Supabase connection pool:**
   ```python
   # Check pool stats in logs
   print(f"Pool connections acquired: {_pool_stats['connections_acquired']}")
   print(f"Average wait time: {_pool_stats['total_wait_time'] / _pool_stats['connections_acquired']}ms")
   ```

4. **Review other files for SQLite-specific code** (see list above)

---

## Support

If issues arise:
- **Local SQLite errors**: Check `data/sessions.db` exists and has proper schema
- **Supabase connection errors**: Verify `SUPABASE_URL` and `SUPABASE_KEY` env vars
- **Schema errors**: Check `SET search_path` is applied (logged at connection)
- **Performance issues**: Monitor connection pool stats and adjust pool size

**Contact:** GitHub Copilot (Claude Sonnet 4.5)  
**Documentation:** `SUPABASE_MIGRATION_AGENT_ROUTES_V4.md`
