# 🚨 URGENT: Fix Database Corruption NOW

## Problem
```
sqlite3.DatabaseError: database disk image is malformed
```

## Root Cause
- **Multiple concurrent requests** hitting the database
- **No connection pooling** - each request opens new connection
- **WAL mode issues** - Write-Ahead Log not checkpointing properly

## IMMEDIATE FIX (Do This Now)

### Step 1: Stop Flask Server
```powershell
# Press Ctrl+C in the BISTART terminal
# Or in new terminal:
cd C:\Users\gpoli\GIT\AI_agents
Get-Process -Name python | Where-Object {$_.Path -like "*AI_agents*"} | Stop-Process -Force
```

### Step 2: Run Database Fix
```powershell
python fix_database_malformed.py
```

This will:
- ✅ Backup current database
- ✅ Checkpoint WAL mode
- ✅ Dump and rebuild database
- ✅ Verify integrity
- ✅ Replace corrupted file

### Step 3: Restart Flask
```powershell
BISTART
```

## Long-Term Fix (Prevent Recurrence)

The real issue is **concurrent database access without proper connection handling**.

### Option A: Add Connection Pooling (RECOMMENDED)

Edit `AI_infrastructure/utils/database_helpers.py`:

```python
import sqlite3
from contextlib import contextmanager
import threading

# Connection pool
_local_storage = threading.local()

@contextmanager
def get_db_connection(db_path, timeout=30.0):
    """
    Thread-safe database connection with timeout
    
    Args:
        db_path: Path to database file
        timeout: Connection timeout (default 30 seconds)
    """
    # Check if we already have a connection in this thread
    if not hasattr(_local_storage, 'connections'):
        _local_storage.connections = {}
    
    # Reuse existing connection for this thread and database
    cache_key = str(db_path)
    if cache_key in _local_storage.connections:
        conn = _local_storage.connections[cache_key]
        yield conn
        return
    
    # Create new connection
    conn = sqlite3.connect(str(db_path), timeout=timeout, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    
    # Enable WAL mode for better concurrency
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')  # Faster, still safe
    conn.execute('PRAGMA temp_store=MEMORY')   # Faster temp operations
    
    _local_storage.connections[cache_key] = conn
    
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        # Don't close - keep in pool
        pass

def execute_sqlite_query(db_path, query, params=None):
    """Execute query with connection pooling"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        else:
            conn.commit()
            return cursor.rowcount
```

### Option B: Add Request Queue (ALTERNATIVE)

Add this to `flask_app.py`:

```python
import queue
import threading

# Database request queue
db_queue = queue.Queue(maxsize=100)

def db_worker():
    """Process database requests sequentially"""
    while True:
        try:
            func, args, kwargs, result_queue = db_queue.get(timeout=1)
            try:
                result = func(*args, **kwargs)
                result_queue.put(('success', result))
            except Exception as e:
                result_queue.put(('error', e))
            finally:
                db_queue.task_done()
        except queue.Empty:
            continue

# Start DB worker thread
db_thread = threading.Thread(target=db_worker, daemon=True)
db_thread.start()

def execute_in_db_thread(func, *args, **kwargs):
    """Execute database function in dedicated thread"""
    result_queue = queue.Queue()
    db_queue.put((func, args, kwargs, result_queue))
    status, result = result_queue.get(timeout=30)
    
    if status == 'error':
        raise result
    return result
```

### Option C: Switch to PostgreSQL (BEST LONG-TERM)

SQLite has limitations with concurrent writes. For production:

1. Install PostgreSQL
2. Update connection strings
3. Migrate data

See: `INSTALL_POSTGRESQL.md` (already exists in In_House_SQL folder)

## Prevention Tips

1. **Always use connection pooling** - Don't open new connection per request
2. **Enable WAL mode** - Better concurrency: `PRAGMA journal_mode=WAL`
3. **Use timeouts** - Prevent deadlocks: `timeout=30.0`
4. **Batch operations** - Reduce number of transactions
5. **Regular checkpoints** - Clear WAL file: `PRAGMA wal_checkpoint(TRUNCATE)`

## Quick Test After Fix

```powershell
# Test database is working
python -c "import sqlite3; conn = sqlite3.connect('data/sessions.db'); print('✅ Database OK'); conn.close()"

# Start server
BISTART

# In browser, check if threads load without errors
```

## Monitoring

Watch for these in logs:
- ❌ `database disk image is malformed`
- ❌ `database is locked`
- ❌ `unable to open database file`
- ⚠️ `Task queue depth is X` (high numbers = too many concurrent requests)

If you see these, implement connection pooling immediately!

## Files to Update

1. `AI_infrastructure/utils/database_helpers.py` - Add connection pooling
2. `AI_infrastructure/routes/thread_routes.py` - Use pooled connections
3. `AI_infrastructure/flask_app.py` - Add DB worker thread (optional)

---

**TL;DR:**
1. Stop Flask: `Ctrl+C` or kill python process
2. Fix DB: `python fix_database_malformed.py`
3. Restart: `BISTART`
4. Implement connection pooling to prevent recurrence
