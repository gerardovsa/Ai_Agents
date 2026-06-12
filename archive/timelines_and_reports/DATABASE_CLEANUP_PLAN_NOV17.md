# Database Schema Cleanup - November 17, 2025

## Summary of Changes

### ✅ Tables to REMOVE

1. **`sessions.thread_assignments`** - Redundant (location stored in threads.location)
2. **`sessions.saved_threads`** - Legacy table (replaced by sessions.threads)
3. **`sessions.users`** - Moved to ai_infrastructure.users

### ✅ Columns to ADD to `sessions.threads`

1. **`thread_lock_user_id`** - INTEGER (user who locked the thread)
2. **`automation_slug`** - TEXT (automation identifier)
3. **`automation_title`** - TEXT (automation display name)

### ✅ Columns to REMOVE from `sessions.threads`

1. **`locked_to_device_id`** - TEXT (replaced by thread_lock_user_id)
2. **`lock_mode`** - TEXT (simplified to locked/unlocked based on thread_lock_user_id)

---

## New Schema for `sessions.threads`

```sql
CREATE TABLE sessions.threads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  thread_slug TEXT NOT NULL UNIQUE,
  
  -- Ownership & Context
  workspace_id INTEGER,
  user_id INTEGER,
  
  -- Basic Info
  name TEXT NOT NULL,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  
  -- Location & Assignment (CASCADE PATTERN - Single Source of Truth)
  location TEXT,  -- 'prime', 'agent-1', 'agent-2', 'agent-3', NULL
  
  -- Thread Management
  archived INTEGER DEFAULT 0,
  token_count INTEGER DEFAULT 0,
  
  -- Locking (SIMPLIFIED)
  thread_lock_user_id INTEGER,  -- NULL = unlocked, user_id = locked by that user
  locked_at TIMESTAMP,
  
  -- UI Links (External Systems)
  synergy_card_id TEXT,           -- Synergy session UUID/slug
  workflow_slug TEXT,             -- Workflow identifier
  workflow_title TEXT,            -- Workflow display name
  internal_doc_slug TEXT,         -- Internal documentation slug
  internal_doc_title TEXT,        -- Internal documentation title
  automation_slug TEXT,           -- Automation identifier (NEW)
  automation_title TEXT,          -- Automation display name (NEW)
  
  -- Branching/Forking
  parent_thread_id INTEGER,       -- Parent thread ID (for forks)
  branch_name TEXT,               -- Branch label
  branch_point_message_id TEXT,   -- Message ID where branch occurred
  
  -- Metadata
  tags TEXT,                      -- JSON array of tags
  metadata TEXT                   -- JSON object for custom data
);
```

---

## Migration SQL

### Step 1: Add New Columns to `sessions.threads`

```sql
-- Add thread locking column (user-based)
ALTER TABLE sessions.threads ADD COLUMN thread_lock_user_id INTEGER;

-- Add automation fields
ALTER TABLE sessions.threads ADD COLUMN automation_slug TEXT;
ALTER TABLE sessions.threads ADD COLUMN automation_title TEXT;
```

### Step 2: Migrate Existing Lock Data (if any)

```sql
-- If you have existing locks in locked_to_device_id, you could migrate them
-- But since device IDs aren't user IDs, it's better to clear them
-- All threads will start unlocked

-- Ensure all threads are unlocked initially
UPDATE sessions.threads 
SET thread_lock_user_id = NULL,
    locked_at = NULL
WHERE thread_lock_user_id IS NOT NULL 
   OR locked_at IS NOT NULL;
```

### Step 3: Drop Old Columns (Optional - Do After Testing)

```sql
-- Drop old lock columns (SQLite doesn't support DROP COLUMN easily)
-- Instead, create new table without old columns and migrate data
-- This is optional - old columns can remain for backwards compatibility

-- For now, you can just ignore locked_to_device_id and lock_mode columns
-- They will be NULL and unused
```

### Step 4: Drop Redundant Tables

```sql
-- Drop thread_assignments table (location now in threads.location)
DROP TABLE IF EXISTS sessions.thread_assignments;

-- Drop saved_threads table (replaced by sessions.threads)
DROP TABLE IF EXISTS sessions.saved_threads;

-- Drop users table from sessions schema (use ai_infrastructure.users instead)
DROP TABLE IF EXISTS sessions.users;
```

---

## Backend Code Changes Required

### 1. Update `thread_assignment_routes.py`

**Current**: Stores assignments in `ai_infrastructure.users.metadata` JSON  
**New**: Directly updates `sessions.threads.location` column

**Changes**:
- Remove metadata JSON manipulation
- Direct UPDATE to threads.location
- Simpler, faster, more reliable

### 2. Update Thread Lock Logic

**Old Columns**:
```python
# Old approach (device-based)
locked_to_device_id TEXT
lock_mode TEXT  # 'unlocked', 'editing', 'readonly'
```

**New Columns**:
```python
# New approach (user-based)
thread_lock_user_id INTEGER  # NULL = unlocked, user_id = locked
locked_at TIMESTAMP
```

**Lock Check Logic**:
```python
def is_thread_locked(thread_id):
    """Check if thread is locked"""
    cursor.execute("""
        SELECT thread_lock_user_id, locked_at 
        FROM sessions.threads 
        WHERE thread_slug = %s
    """, [thread_id])
    
    row = cursor.fetchone()
    if not row or row[0] is None:
        return False  # Unlocked
    
    # Check if lock is stale (older than 30 minutes)
    from datetime import datetime, timedelta
    if row[1]:
        lock_time = datetime.fromisoformat(row[1])
        if datetime.now() - lock_time > timedelta(minutes=30):
            # Auto-release stale lock
            unlock_thread(thread_id)
            return False
    
    return True  # Locked

def lock_thread(thread_id, user_id):
    """Lock thread for editing"""
    cursor.execute("""
        UPDATE sessions.threads 
        SET thread_lock_user_id = %s,
            locked_at = CURRENT_TIMESTAMP
        WHERE thread_slug = %s
    """, [user_id, thread_id])

def unlock_thread(thread_id):
    """Unlock thread"""
    cursor.execute("""
        UPDATE sessions.threads 
        SET thread_lock_user_id = NULL,
            locked_at = NULL
        WHERE thread_slug = %s
    """, [thread_id])
```

### 3. Remove References to Deleted Tables

**Files to Update**:
- `AI_infrastructure/routes/thread_routes.py` - Remove saved_threads queries
- `AI_infrastructure/routes/thread_assignment_routes.py` - Remove thread_assignments logic
- Any legacy code referencing sessions.users

---

## Frontend Changes Required

### 1. Update Thread Lock UI

**Show Lock Status in Thread-Info Card**:
```javascript
// In renderThreadInfoContainer()
if (thread.thread_lock_user_id) {
    const lockUserName = await getUserName(thread.thread_lock_user_id);
    const lockTime = new Date(thread.locked_at).toLocaleTimeString();
    
    html += `
        <div class="thread-lock-indicator">
            <i class="fas fa-lock"></i>
            <span>Locked by ${lockUserName} at ${lockTime}</span>
        </div>
    `;
}
```

### 2. Lock/Unlock Functions

```javascript
async function lockThread(threadId) {
    const response = await fetch('/api/threads/lock', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            thread_id: threadId,
            user_id: AppState.userId
        })
    });
    
    const data = await response.json();
    if (data.success) {
        showNotification('Thread locked', 'success');
        // Refresh thread info
        ThreadManager.refreshAllThreadInfoCards(threadId);
    }
}

async function unlockThread(threadId) {
    const response = await fetch('/api/threads/unlock', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            thread_id: threadId
        })
    });
    
    const data = await response.json();
    if (data.success) {
        showNotification('Thread unlocked', 'success');
        ThreadManager.refreshAllThreadInfoCards(threadId);
    }
}
```

### 3. Automation Link Display

**Show Automation Badge in Thread-Info Card**:
```javascript
// In renderThreadInfoContainer(), add automation pill
${thread.automation_slug ? `
    <div class="thread-item-automation" style="background: #f59e0b15; border: 1px solid #f59e0b; border-radius: 8px; padding: 8px;">
        <button class="automation-badge" style="background: #f59e0b; color: white; border: none; padding: 6px 12px; border-radius: 6px; display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer;"
            onclick="event.stopPropagation(); ThreadManager.openAutomation('${thread.automation_slug}')"
            title="${thread.automation_title || thread.automation_slug}">
            <i class="fas fa-robot"></i> ${thread.automation_title || thread.automation_slug}
        </button>
    </div>
` : ''}
```

---

## Benefits of These Changes

### ✅ Simplified Architecture
- **Before**: 3 tables for thread data (threads, saved_threads, thread_assignments)
- **After**: 1 table (threads) - single source of truth

### ✅ Better Locking
- **Before**: Device-based locks (what if same user on different device?)
- **After**: User-based locks (works across devices)

### ✅ Future-Proof
- **Automation Fields**: Ready for automation system integration
- **Cleaner Schema**: Easier to maintain and extend

### ✅ Cascade Pattern Ready
- **Single Location Column**: Perfect for database-first cascade pattern
- **No JSON Metadata**: Direct column access (faster queries)

---

## Migration Checklist

### Backend Changes
- [ ] Add new columns to sessions.threads (thread_lock_user_id, automation_slug, automation_title)
- [ ] Update thread_assignment_routes.py to use threads.location directly
- [ ] Add lock/unlock endpoints to thread_routes.py
- [ ] Remove saved_threads references from thread_routes.py
- [ ] Test thread assignment with new schema

### Frontend Changes
- [ ] Update thread-info card to show lock status
- [ ] Add lock/unlock buttons to thread actions
- [ ] Add automation badge display
- [ ] Test locking UI
- [ ] Test automation link display

### Database Cleanup
- [ ] Run migration SQL (add columns)
- [ ] Drop thread_assignments table
- [ ] Drop saved_threads table
- [ ] Drop sessions.users table (use ai_infrastructure.users)

### Testing
- [ ] Test thread assignment (drag & drop)
- [ ] Test thread locking (lock/unlock)
- [ ] Test automation links (display & navigation)
- [ ] Verify no references to deleted tables
- [ ] Run SQL queries to verify schema

---

## SQL Verification Queries

```sql
-- Verify new columns exist
PRAGMA table_info(sessions.threads);

-- Check thread locations
SELECT thread_slug, location, thread_lock_user_id, automation_slug
FROM sessions.threads
WHERE location IS NOT NULL
ORDER BY updated_at DESC
LIMIT 10;

-- Check for locked threads
SELECT thread_slug, name, thread_lock_user_id, locked_at
FROM sessions.threads
WHERE thread_lock_user_id IS NOT NULL;

-- Check for automation links
SELECT thread_slug, name, automation_slug, automation_title
FROM sessions.threads
WHERE automation_slug IS NOT NULL;

-- Verify deleted tables are gone
SELECT name FROM sqlite_master 
WHERE type='table' 
AND name IN ('thread_assignments', 'saved_threads', 'users');
-- Should return 0 rows
```

---

## Rollback Plan (If Needed)

If something breaks, you can rollback:

```sql
-- Restore thread_assignments table (if you have backup)
-- CREATE TABLE sessions.thread_assignments (...);

-- Restore saved_threads table (if you have backup)
-- CREATE TABLE sessions.saved_threads (...);

-- Remove new columns (SQLite doesn't support DROP COLUMN easily)
-- Better to just leave them NULL and fix the code
```

---

**Status**: Ready for Implementation  
**Estimated Time**: 2-3 hours (backend + frontend + testing)  
**Risk**: Low (cascade pattern already implemented, this simplifies it further)
