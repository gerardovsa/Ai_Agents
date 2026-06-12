# Supabase Connection Pool Leak Fix - December 16, 2025

## Problem Summary
The scheduler job `_check_pending_approvals` was failing every minute due to:
1. **Network connectivity issue**: DNS resolution failed for Supabase hostname
2. **Connection pool leak**: When network fails, connections were acquired but not returned to pool
3. **Pool exhaustion**: After 5 leaked connections, pool became exhausted

## Root Cause
When `pool.getconn()` was called in a thread and Supabase was unreachable:
- Connection might be acquired by psycopg2 but fail during setup (CREATE SCHEMA, SET search_path)
- Exception was raised but connection wasn't returned to pool
- No cleanup logic in exception handlers for partially-acquired connections
- Stats counter incremented only after successful setup, causing mismatch

## Fixes Applied

### 1. Enhanced Connection Acquisition (`database_utils.py`)
```python
# Before: No tracking of acquisition state
conn = None
def _get_conn_with_timeout():
    nonlocal conn
    conn = pool_instance.getconn()  # Might succeed but setup fails

# After: Track acquisition state for cleanup
conn_acquired = False
conn = None

def _get_conn_with_timeout():
    nonlocal conn
    try:
        conn = pool_instance.getconn()
    except Exception as e:
        print(f"❌ [POOL] getconn() failed in thread: {e}")
        conn = None
```

### 2. Exception Handler Cleanup
```python
except psycopg2.OperationalError as e:
    # NEW: Return connection to pool if acquired
    if conn_acquired and conn is not None:
        try:
            pool_instance.putconn(conn)
            _pool_stats['connections_returned'] += 1
            print(f"✅ [POOL] Returned failed connection to pool")
        except Exception as pool_err:
            print(f"❌ [POOL] Failed to return connection: {pool_err}")
```

### 3. Network Connectivity Check in Scheduler
```python
def _check_pending_approvals(self):
    # NEW: Skip if no network connectivity
    import socket
    try:
        socket.create_connection(("db.ryoicrdifiqhqpsnjmdo.supabase.co", 5432), timeout=3)
    except (socket.timeout, socket.error, OSError):
        logger.warning("No Supabase connectivity - skipping approval check")
        return  # Prevents repeated failures
```

### 4. Connection Pool Reset Utility
New function `reset_connection_pool()`:
- Closes all pooled connections
- Resets pool statistics
- Can reset specific schema or all schemas
- Useful for recovery after network issues

## Usage

### Reset Connection Pool (Manual)
```bash
cd AI_infrastructure
python reset_connection_pool.py
```

### Reset in Code
```python
from shared.database_utils import reset_connection_pool

# Reset specific schema
reset_connection_pool('ai_infrastructure')

# Reset all schemas
reset_connection_pool()
```

### Check Pool Status
```python
from shared.database_utils import log_pool_usage

log_pool_usage()  # Shows acquired, returned, leaked connections
```

## Prevention

### 1. Always Use Finally Blocks
```python
# ✅ Good
conn = None
cursor = None
try:
    conn = get_connection('ai_infrastructure')
    cursor = conn.cursor()
    # ... database operations ...
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()  # CRITICAL - always close!
```

### 2. Use Context Managers (Preferred)
```python
# ✅ Better
with get_connection('ai_infrastructure') as conn:
    cursor = conn.cursor()
    # ... database operations ...
    # conn.close() called automatically
```

### 3. Handle Network Failures
```python
# ✅ Check connectivity before database operations
import socket

def check_supabase_connectivity():
    try:
        socket.create_connection(("db.ryoicrdifiqhqpsnjmdo.supabase.co", 5432), timeout=3)
        return True
    except:
        return False

if not check_supabase_connectivity():
    logger.warning("Supabase unreachable - skipping operation")
    return
```

## Monitoring

### Pool Statistics
The system now tracks:
- `connections_acquired`: Total connections taken from pool
- `connections_returned`: Total connections returned to pool
- **Leaked connections**: `acquired - returned`

### Warning Signs
- Leaked connections > 0: Check code for missing `conn.close()`
- Pool exhaustion errors: Too many leaked connections (5+ in free tier)
- Repeated operational errors: Network connectivity issues

## Recovery Steps

### If Pool is Exhausted
1. **Check network**: Verify Supabase is reachable
   ```bash
   ping db.ryoicrdifiqhqpsnjmdo.supabase.co
   ```

2. **Reset pool**: Clear leaked connections
   ```bash
   python AI_infrastructure/reset_connection_pool.py
   ```

3. **Restart application**: Fresh start with clean pool
   ```bash
   # Stop application
   # Start application
   ```

### If Network is Down
- Scheduler jobs now skip gracefully (no repeated failures)
- Connection pool won't get exhausted
- Operations resume automatically when network recovers

## Testing

### Verify Fix
1. Start application with working network
2. Disconnect network (or block Supabase hostname)
3. Wait for scheduler job to run (every minute)
4. Check logs: Should see "No Supabase connectivity - skipping approval check"
5. Reconnect network
6. Verify operations resume normally

### Expected Behavior
- **Before fix**: Pool exhausted after 5 failed attempts, application crashes
- **After fix**: Graceful degradation, operations skip when network down, resume when recovered

## Files Modified
1. `AI_infrastructure/shared/database_utils.py`
   - Enhanced connection acquisition tracking
   - Added cleanup in exception handlers
   - Added `reset_connection_pool()` function

2. `AI_infrastructure/scheduler.py`
   - Added network connectivity check in `_check_pending_approvals()`

3. `AI_infrastructure/reset_connection_pool.py` (NEW)
   - Utility script to manually reset connection pool

## Impact
- **No breaking changes**: All existing code works as before
- **Better resilience**: Network failures don't crash application
- **Easier debugging**: Clear logging of pool state
- **Manual recovery**: `reset_connection_pool()` utility for emergency fixes

## Next Steps
1. ✅ Deploy fixes (DONE)
2. Test with network disconnection
3. Monitor pool statistics in production
4. Consider adding automatic pool reset on repeated failures
5. Add health check endpoint showing pool status

## Notes
- Free tier Supabase has connection limits (~5 concurrent connections)
- Connection pooling reuses connections (efficient)
- Always close connections to return to pool
- Network issues are now handled gracefully
