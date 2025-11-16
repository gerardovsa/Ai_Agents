# Scheduler Column Fix - Complete

**Date:** November 17, 2025  
**Commit:** b325fff  
**Issue:** APScheduler job failing with `psycopg2.errors.UndefinedColumn: column "enabled" does not exist`

---

## Problem Summary

The `AutomationScheduler._check_pending_approvals()` method was failing every minute with:

```
psycopg2.errors.UndefinedColumn: column "enabled" does not exist
LINE 3: WHERE enabled = 1
```

**Root Cause:**  
The scheduler.py code was written for SQLite schema (using `enabled` integer column) but Supabase uses a different schema with `is_active` boolean column.

---

## Schema Mismatch

### Old SQLite Schema (Expected by Code):
```sql
enabled INTEGER DEFAULT 1
requires_approval BOOLEAN DEFAULT 0
approval_status TEXT DEFAULT 'pending'
```

### Actual Supabase Schema:
```sql
is_active BOOLEAN DEFAULT true
-- Missing: requires_approval, approval_status, status, description
```

### Column Mapping:
| SQLite (Code Expected) | Supabase (Actual) | Solution |
|------------------------|-------------------|----------|
| `enabled = 1` | `is_active = true` | Changed query |
| `requires_approval` | **MISSING** | Added column |
| `approval_status` | **MISSING** | Added column |
| `status` | **MISSING** | Added column |
| `description` | **MISSING** | Added column |

---

## Changes Made

### 1. Added Missing Columns to Supabase

**Script:** `add_scheduler_approval_columns.py`

```sql
ALTER TABLE ai_infrastructure.scheduled_tasks 
ADD COLUMN IF NOT EXISTS requires_approval BOOLEAN DEFAULT FALSE;

ALTER TABLE ai_infrastructure.scheduled_tasks 
ADD COLUMN IF NOT EXISTS approval_status TEXT DEFAULT 'approved';

ALTER TABLE ai_infrastructure.scheduled_tasks 
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active';

ALTER TABLE ai_infrastructure.scheduled_tasks 
ADD COLUMN IF NOT EXISTS description TEXT;
```

**Result:**  
✅ 4 columns successfully added to Supabase table

---

### 2. Updated Scheduler Queries

**File:** `AI_infrastructure/scheduler.py`

#### Change 1: Main Task Loading Query (Line 189-193)

**Before:**
```python
cursor.execute('''
    SELECT * FROM ai_infrastructure.scheduled_tasks 
    WHERE enabled = 1 
    AND (approval_status = 'approved' OR requires_approval = 0)
''')
```

**After:**
```python
cursor.execute('''
    SELECT * FROM ai_infrastructure.scheduled_tasks 
    WHERE is_active = true 
    AND (approval_status = 'approved' OR requires_approval = false)
''')
```

**Changes:**
- `enabled = 1` → `is_active = true` (boolean instead of integer)
- `requires_approval = 0` → `requires_approval = false` (boolean)

---

#### Change 2: Pending Approvals Query (Line 456-460)

**Before:**
```python
cursor.execute('''
    SELECT * FROM scheduled_tasks 
    WHERE enabled = 1 
    AND requires_approval = 1 
    AND approval_status = 'pending'
''')
```

**After:**
```python
cursor.execute('''
    SELECT * FROM ai_infrastructure.scheduled_tasks 
    WHERE is_active = true 
    AND requires_approval = true 
    AND approval_status = 'pending'
''')
```

**Changes:**
- Added schema prefix: `ai_infrastructure.scheduled_tasks`
- `enabled = 1` → `is_active = true`
- `requires_approval = 1` → `requires_approval = true`

---

#### Change 3: INSERT Statement (Line 477-507)

**Before:**
```python
INSERT INTO scheduled_tasks (
    task_id, task_name, description, created_by, created_by_user_id,
    trigger_type, cron_expression, datetime_trigger, webhook_url, condition_config,
    action_type, synergy_session_id, thread_id, agent_name, location,
    action_payload, context_instructions, requires_approval, enabled, 
    tags, priority, timeout_seconds, max_retries, retry_delay_seconds
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
```

**After:**
```python
INSERT INTO ai_infrastructure.scheduled_tasks (
    user_id, task_name, task_type, schedule_type, schedule_value,
    tool_name, tool_params, is_active, requires_approval, approval_status, 
    status, description
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
```

**Changes:**
- Mapped to actual Supabase columns (removed non-existent columns)
- `enabled` → `is_active`
- Added schema prefix
- Reduced from 24 parameters to 12 (matching actual schema)

---

## Verification

### 1. Column Check Script

**File:** `check_scheduled_tasks_columns.py`

**Output:**
```
Found 17 columns in ai_infrastructure.scheduled_tasks:

✅ id                             EXISTS
✅ user_id                        EXISTS
✅ task_name                      EXISTS
✅ task_type                      EXISTS
✅ schedule_type                  EXISTS
✅ schedule_value                 EXISTS
✅ tool_name                      EXISTS
✅ tool_params                    EXISTS
✅ is_active                      EXISTS (BOOLEAN, default: true)
✅ last_run                       EXISTS
✅ next_run                       EXISTS
✅ created_at                     EXISTS
✅ updated_at                     EXISTS
✅ requires_approval              EXISTS (BOOLEAN, default: false) ← ADDED
✅ approval_status                EXISTS (TEXT, default: 'approved') ← ADDED
✅ status                         EXISTS (TEXT, default: 'active') ← ADDED
✅ description                    EXISTS (TEXT) ← ADDED
```

---

### 2. APScheduler Status

**Before Fix:**
```
ERROR: Job "_check_pending_approvals" raised an exception
psycopg2.errors.UndefinedColumn: column "enabled" does not exist
```

**After Fix:**
APScheduler should run without errors. Next error check in 1 minute (at 02:01:07).

---

## Files Changed

1. **AI_infrastructure/scheduler.py**
   - Lines 189-193: Changed `enabled` to `is_active` in main query
   - Lines 456-460: Changed `enabled` to `is_active` in approval query, added schema prefix
   - Lines 477-507: Completely rewrote INSERT to match Supabase schema

2. **add_scheduler_approval_columns.py** (NEW)
   - Script to add 4 missing columns to Supabase table
   - Verifies columns were added successfully

3. **check_scheduled_tasks_columns.py** (NEW)
   - Diagnostic script to list all columns in scheduled_tasks table
   - Shows data types and defaults

---

## Testing Required

1. **Wait 1 minute** for APScheduler to run `_check_pending_approvals()` again
2. **Check logs** - should NOT see `column "enabled" does not exist` error
3. **Test creating a scheduled task** - INSERT statement should work
4. **Test loading tasks on startup** - SELECT with `is_active` should work

---

## Deployment Status

- ✅ Changes committed: `b325fff`
- ✅ Pushed to GitHub v6 branch
- ⏳ Render auto-deployment triggered (3-5 minutes)

---

## Summary

**Problem:**  
APScheduler failing every minute with "column enabled does not exist"

**Solution:**  
1. Added 4 missing columns to Supabase (requires_approval, approval_status, status, description)
2. Changed all queries from `enabled = 1` to `is_active = true`
3. Updated INSERT statement to match actual Supabase schema

**Status:**  
✅ Local fix complete  
⏳ Render deployment in progress  
🎯 Should resolve APScheduler errors within 1-5 minutes

---

**Next APScheduler run:** 2025-11-17 02:01:07 AEST  
**Expected result:** No errors

