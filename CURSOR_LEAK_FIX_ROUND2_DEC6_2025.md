# Cursor Leak Fix - Round 2 - December 6, 2025

## Summary
Fixed **ALL cursor leaks** in `thread_assignment_routes.py` that were causing connection pool exhaustion. The cursors were being created but never closed, preventing connections from being returned to the pool.

## Root Cause
In psycopg2 connection pooling, when you call `cursor = conn.cursor()`, the cursor MUST be explicitly closed with `cursor.close()` or used as a context manager (`with conn.cursor() as cursor:`) before the connection can be returned to the pool.

### Why This Matters
```python
# ❌ BAD - Cursor leak (connection stays busy)
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
# Connection returned to pool BUT cursor still open = LEAK!

# ✅ GOOD - Cursor auto-closes
with get_db_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        conn.commit()
    # Cursor closed here
# Connection cleanly returned to pool
```

## Files Fixed

### `AI_infrastructure/routes/thread_assignment_routes.py`
Fixed **8 cursor leaks** in the following functions:

1. **`enforce_thread_assignment_rules()`** (line 84)
   - Added cursor context manager
   - Wrapped entire function's DB operations in cursor context

2. **`get_thread_assignments()`** (line 236)
   - Fixed indentation bug where cursor context closed too early
   - Moved all SQL operations inside cursor context

3. **`save_thread_assignments()`** (line 324)
   - Added cursor context manager
   - All DB operations now properly scoped

4. **`clear_location()`** (line 538)
   - Added cursor context manager
   - JSON operations and updates properly scoped

5. **`get_thread_location()`** (line 611)
   - Added cursor context manager
   - Location lookup operations properly scoped

6. **`validate_assignments()`** (line 673)
   - Added cursor context manager
   - Duplicate detection and fixes properly scoped

7. **`assign_email_thread()`** (line 775)
   - Added cursor context manager
   - Email metadata updates properly scoped

8. **`unlink_email_thread()`** (line 842)
   - Added cursor context manager
   - Email unlink operations properly scoped

## Error Pattern (Before Fix)

```
======================================================================
 [POOL] CONNECTION POOL EXHAUSTED - LEAKED CONNECTIONS DETECTED
======================================================================
Schema: sessions
Pool stats:
  Acquired: 42
  Returned: 40
  LEAKED: 2

 SOLUTION:
  1. Check code for missing conn.close() calls
  2. Use context managers: with get_database_connection() as conn:
  3. Restart application to reset pool
======================================================================
```

## Fix Pattern Applied

### Before (❌ Leaks cursor):
```python
with get_db_connection() as conn:
    cursor = conn.cursor()
    
    sql, params = convert_sql_placeholders(...)
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    
    # Process rows...
    conn.commit()
# Cursor NEVER CLOSED - connection can't be returned!
```

### After (✅ No leak):
```python
with get_db_connection() as conn:
    with conn.cursor() as cursor:
        sql, params = convert_sql_placeholders(...)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        # Process rows...
        conn.commit()
    # ✅ Cursor auto-closed
# ✅ Connection cleanly returned to pool
```

## Testing

### Expected Results
1. **No more "connection pool exhausted" errors**
2. **Pool stats show: Acquired == Returned (no leaks)**
3. **Application can handle 50+ concurrent requests without pool exhaustion**

### Commands to Test
```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

Then in browser:
1. Open http://localhost:5001
2. Login with Google OAuth
3. Load multiple threads quickly (frontend auto-loads on startup)
4. Check terminal logs for pool stats

### Expected Logs
```
 [POOL] Got connection from pool for 'sessions' (wait: 0.5ms)
 [POOL] Got connection from pool for 'sessions' (wait: 0.6ms)
 [POOL] Got connection from pool for 'sessions' (wait: 0.7ms)
# NO MORE "connection pool exhausted" errors!
```

## Related Files

### Context Managers in Database Layer
- `AI_infrastructure/shared/database_utils.py`
  - Line 661-665: `DatabaseCursor.__enter__()` and `__exit__()` methods
  - Line 674-678: `DatabaseConnection.cursor()` returns DatabaseCursor wrapper
  - Line 695-700: Connection context manager implementation

### Previous Fixes
- `CURSOR_LEAK_FIX_DEC6_2025.md` - Fixed thread_routes.py cursor leaks (Round 1)
- `DATABASE_CURSOR_MANAGEMENT.md` - DatabaseCursor wrapper documentation

## Code Archaeology Notes

### Why Were Cursors Not Being Closed?

1. **Context Manager Misunderstanding**: The code properly used `with get_db_connection() as conn:` for connections, but didn't realize cursors ALSO need context managers

2. **DatabaseCursor Wrapper**: The `DatabaseCursor` class in `database_utils.py` HAS `__enter__` and `__exit__` methods (lines 661-665), making it usable as a context manager, but this wasn't being utilized

3. **Indentation Bugs**: In `get_thread_assignments()`, the cursor context manager closed too early (only wrapped the logger.info statement), leaving the actual SQL execution outside the context

4. **Silent Failure**: Cursor leaks don't throw errors immediately - they gradually exhaust the pool until new requests start failing with "connection pool exhausted"

## Prevention Guidelines

### Always Use This Pattern:
```python
def some_database_function():
    with get_db_connection('schema_name') as conn:
        with conn.cursor() as cursor:
            # ALL database operations here
            cursor.execute(sql, params)
            result = cursor.fetchall()
            conn.commit()
        # Cursor auto-closes here
    # Connection auto-closes here
    
    # Process results OUTSIDE db context
    return result
```

### Never Do This:
```python
def bad_database_function():
    with get_db_connection('schema_name') as conn:
        cursor = conn.cursor()  # ❌ NO! Must use 'with'
        cursor.execute(sql, params)
        result = cursor.fetchall()
        # cursor.close() missing!
    # Connection returned with open cursor = LEAK
    return result
```

## Verification Checklist

- [x] All cursor creation uses context managers
- [x] No `cursor = conn.cursor()` without `with`
- [x] All DB operations inside cursor context
- [x] Commit happens before cursor closes
- [x] No syntax errors (Python compiles)
- [x] All functions maintain proper indentation
- [ ] Test with BISTART and verify no pool exhaustion
- [ ] Monitor pool stats after 50+ thread loads

## Impact

**Severity**: CRITICAL - Application unusable after ~40-50 requests  
**Scope**: ALL thread assignment operations  
**Resolution**: Complete - All 8 cursor leaks fixed  
**Testing Required**: YES - Need to verify with real traffic  

---

**Next Steps:**
1. Restart Flask with `BISTART`
2. Load multiple threads rapidly
3. Monitor terminal for pool stats
4. Confirm NO "connection pool exhausted" errors
5. If successful, document in main README
