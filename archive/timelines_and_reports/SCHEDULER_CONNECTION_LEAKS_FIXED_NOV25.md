# Scheduler Connection Leaks Fixed - November 25, 2025

## Critical Bug: Connection Pool Exhaustion

**Error**: `ConnectionError: Connection pool exhausted for 'ai_infrastructure'. Leaked connections: 4`

**Impact**:
- ❌ Scheduler failing every minute (`_check_pending_approvals`)
- ❌ `/api/prompts/library/db` returning 500 errors
- ❌ `/api/automation/list` returning 500 errors
- ❌ `/api/auth/verify` returning 401 errors
- ❌ Flask unable to serve requests after pool exhaustion

---

## Root Cause Analysis

The `AI_infrastructure/scheduler.py` file had **5 functions** with connection leaks:

### Leak 1: `update_task()` - Line 552
```python
# BEFORE (leaked connection):
# Get updated task and reschedule
conn = get_connection('ai_infrastructure')
cursor = conn.cursor()
cursor.execute('SELECT * FROM scheduled_tasks WHERE task_id = %s', (task_id,))
task = cursor.fetchone()
conn.close()  # ← This was OUTSIDE the try block, could be skipped!
```

**Problem**: If `_schedule_task()` raised an exception, `conn.close()` would never execute.

### Leak 2: `delete_task()` - Line 573
```python
# BEFORE (leaked connection):
conn = get_connection('ai_infrastructure')
cursor = conn.cursor()
cursor.execute('DELETE FROM scheduled_tasks WHERE task_id = %s', (task_id,))
conn.commit()
conn.close()  # ← No try/finally, could fail before this line
```

**Problem**: If `cursor.execute()` or `conn.commit()` raised exception, connection never closed.

### Leak 3: `get_task()` - Line 584
```python
# BEFORE (leaked connection):
conn = get_connection('ai_infrastructure')
cursor = conn.cursor()
cursor.execute('SELECT * FROM scheduled_tasks WHERE task_id = %s', (task_id,))
task = cursor.fetchone()
conn.close()  # ← No try/finally protection
```

**Problem**: Any exception before `conn.close()` leaked the connection.

### Leak 4: `list_tasks()` - Line 594
```python
# BEFORE (leaked connection):
conn = get_connection('ai_infrastructure')
cursor = conn.cursor()

query = 'SELECT * FROM scheduled_tasks WHERE 1=1'
params = []

if filters:
    # ... filter logic ...

cursor.execute(query, params)
tasks = cursor.fetchall()
conn.close()  # ← Not guaranteed to execute
```

**Problem**: Exception during query execution or filter building leaked connection.

### Leak 5: `get_execution_history()` - Line 622
```python
# BEFORE (leaked connection):
conn = get_connection('ai_infrastructure')
cursor = conn.cursor()

cursor.execute('''
    SELECT * FROM task_executions 
    WHERE task_id = %s 
    ORDER BY started_at DESC 
    LIMIT %s
''', (task_id, limit))

executions = cursor.fetchall()
conn.close()  # ← No try/finally block
```

**Problem**: Database errors during query execution leaked connection.

---

## Fixes Applied

All 5 functions now use proper try/finally blocks:

### Fix 1: `update_task()` - Lines 543-570
```python
# AFTER (leak-proof):
conn2 = None
try:
    conn2 = get_connection('ai_infrastructure')
    cursor = conn2.cursor()
    cursor.execute('SELECT * FROM scheduled_tasks WHERE task_id = %s', (task_id,))
    task = cursor.fetchone()
    
    if task:
        self._schedule_task(dict(task))
finally:
    if conn2:
        conn2.close()  # ✅ ALWAYS executes
```

### Fix 2: `delete_task()` - Lines 572-591
```python
# AFTER (leak-proof):
conn = None
try:
    conn = get_connection('ai_infrastructure')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM scheduled_tasks WHERE task_id = %s', (task_id,))
    conn.commit()
    
    logger.info(f"Deleted task: {task_id}")
    return True
finally:
    if conn:
        conn.close()  # ✅ ALWAYS executes
```

### Fix 3: `get_task()` - Lines 593-605
```python
# AFTER (leak-proof):
conn = None
try:
    conn = get_connection('ai_infrastructure')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM scheduled_tasks WHERE task_id = %s', (task_id,))
    task = cursor.fetchone()
    
    return dict(task) if task else None
finally:
    if conn:
        conn.close()  # ✅ ALWAYS executes
```

### Fix 4: `list_tasks()` - Lines 607-635
```python
# AFTER (leak-proof):
conn = None
try:
    conn = get_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    query = 'SELECT * FROM scheduled_tasks WHERE 1=1'
    params = []
    
    if filters:
        # ... filter logic ...
    
    cursor.execute(query, params)
    tasks = cursor.fetchall()
    
    return [dict(task) for task in tasks]
finally:
    if conn:
        conn.close()  # ✅ ALWAYS executes
```

### Fix 5: `get_execution_history()` - Lines 636-654
```python
# AFTER (leak-proof):
conn = None
try:
    conn = get_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM task_executions 
        WHERE task_id = %s 
        ORDER BY started_at DESC 
        LIMIT %s
    ''', (task_id, limit))
    
    executions = cursor.fetchall()
    
    return [dict(execution) for execution in executions]
finally:
    if conn:
        conn.close()  # ✅ ALWAYS executes
```

---

## Connection Leak Pattern Summary

**Common Pattern (WRONG)**:
```python
conn = get_connection()
cursor = conn.cursor()
cursor.execute(...)
conn.close()  # ← Can be skipped if exception occurs!
```

**Correct Pattern (RIGHT)**:
```python
conn = None
try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(...)
    # ... do work ...
    return result
finally:
    if conn:
        conn.close()  # ✅ Python guarantees this runs before return
```

---

## Testing & Verification

### Before Fix:
```
[POOL] Pool configuration for 'ai_infrastructure':
  - minconn=1, maxconn=2 (Supabase Nano limit: 60)
  - Total pools: 1
  - Total potential connections: 2
  - Leaked connections: 4  ❌
  - Status: EXHAUSTED ❌
```

### After Fix (Expected):
```
[POOL] Pool configuration for 'ai_infrastructure':
  - minconn=1, maxconn=2
  - Total pools: 1
  - Total potential connections: 2
  - Leaked connections: 0  ✅
  - Status: HEALTHY ✅
```

---

## Files Modified

**File**: `AI_infrastructure/scheduler.py`  
**Lines Changed**: 543-654 (5 functions fixed)  
**Changes**:
1. Line 543-570: Fixed `update_task()` connection leak
2. Line 572-591: Fixed `delete_task()` connection leak
3. Line 593-605: Fixed `get_task()` connection leak
4. Line 607-635: Fixed `list_tasks()` connection leak
5. Line 636-654: Fixed `get_execution_history()` connection leak

---

## Expected Impact

### ✅ Immediate Fixes:
1. Scheduler runs without errors every minute
2. `/api/prompts/library/db` endpoint returns 200 OK
3. `/api/automation/list` endpoint returns 200 OK
4. `/api/auth/verify` endpoint returns valid responses
5. No more "Connection pool exhausted" errors

### ✅ Long-term Benefits:
1. Flask server stable under load
2. Scheduler can run for days without exhausting pool
3. Proper resource cleanup in all code paths
4. Follows best practices for connection management

---

## Related Fixes

This is the **3rd connection leak fix** in this series:

1. **Nov 24**: Fixed `automation_routes.py` - 2 leaked connections
2. **Nov 24**: Fixed `user_auth.py` verify_token() - 2 leaked connections
3. **Nov 25**: Fixed `scheduler.py` - 4 leaked connections (THIS FIX)

**Total connections fixed**: 8 leaked connections across 3 files

---

## Restart Instructions

```powershell
# Stop Flask
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait for connections to close
Start-Sleep -Seconds 5

# Restart Flask
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
BISTART
```

Expected logs after restart:
```
✅ [POOL] Created connection pool for 'ai_infrastructure' (1-2 connections)
✅ [POOL] Total pools: 1
✅ [POOL] Total potential connections: 2 (Supabase Nano limit: 60)
```

No more `Connection pool exhausted` errors! 🎉

---

## Status: ✅ COMPLETE

All 5 connection leaks in scheduler.py fixed. Ready for testing after Flask restart.
