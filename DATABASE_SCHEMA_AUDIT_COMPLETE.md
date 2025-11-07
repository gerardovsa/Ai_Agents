# Database Schema Audit - Complete Analysis

**Date:** November 8, 2025  
**Status:** CRITICAL ISSUES FOUND  
**Databases Analyzed:** 4 (ai_infrastructure.db, sessions.db, synergy_sessions.db, kanban_analytics.db)

---

## EXECUTIVE SUMMARY

### Critical Issues Found:
1. ❌ **MISSING TABLE**: `thread_assignments` table does NOT exist in `ai_infrastructure.db`
2. ✅ **COLUMNS EXIST**: `thread_ids` and `assigned_agents` columns ARE in `synergy_sessions.db` 
3. ⚠️ **DUPLICATE TABLES**: `sessions` table exists in BOTH `sessions.db` AND `synergy_sessions.db`
4. ⚠️ **DUPLICATE TABLES**: `saved_threads` table exists in `sessions.db` but `threads` table also exists
5. ⚠️ **INCONSISTENT NAMING**: Thread ID stored as different field names across databases

### Impact:
- Thread assignments are NOT persisting (no table to store them)
- Frontend calling non-existent `/api/thread-assignments/assign` endpoint
- Browser refresh loses all thread-to-agent assignments
- Synergy card updates may fail due to schema mismatches

---

## DATABASE 1: ai_infrastructure.db ❌ CRITICAL ISSUE

### Tables Found: 10
1. `_ARCHIVED_user_gmail_accounts` (archived)
2. `_ARCHIVED_user_platform_credentials` (archived)
3. `sqlite_sequence` (system)
4. `user_platform_credentials` (active)
5. `user_preferences` (active)
6. `user_sessions` (active)
7. `users` (active)
8. `workspaces` (active)

### ❌ MISSING TABLE: `thread_assignments`

**EXPECTED SCHEMA:**
```sql
CREATE TABLE thread_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    location TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, location)
);
```

**WHY IT'S CRITICAL:**
- Frontend code calls `POST /api/thread-assignments/assign`
- Frontend code calls `GET /api/thread-assignments?user_id=1`
- Backend API endpoints expect this table to exist
- Without it, ALL thread assignments are lost on browser refresh

**CURRENT STATE:**
- Thread assignments stored ONLY in localStorage
- localStorage can be cleared by browser
- No persistence across devices
- No multi-user support

**FIX REQUIRED:**
```sql
-- Create the missing table
CREATE TABLE thread_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    location TEXT NOT NULL,  -- 'prime', 'agent-1', 'agent-2', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, location)  -- One thread per location per user
);

-- Create index for fast lookups
CREATE INDEX idx_thread_assignments_user ON thread_assignments(user_id);
CREATE INDEX idx_thread_assignments_session ON thread_assignments(session_id);
CREATE INDEX idx_thread_assignments_location ON thread_assignments(user_id, location);
```

---

## DATABASE 2: sessions.db ✅ MOSTLY CORRECT

### Tables Found: 6
1. `api_sessions` - API session tracking
2. `messages` - Individual messages (linked to threads)
3. `saved_threads` - Thread metadata and conversation history
4. `sessions` - Session management
5. `sqlite_sequence` - System table
6. `threads` - Thread metadata (newer format)

### ✅ GOOD: `threads` Table Schema

**Current Schema:**
```sql
CREATE TABLE threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_slug TEXT NOT NULL UNIQUE,
    workspace_id INTEGER,
    user_id INTEGER,
    name TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    metadata TEXT,
    tags TEXT,
    synergy_card_id TEXT,
    parent_thread_id TEXT,
    branch_point_message_id TEXT,
    branch_name TEXT,
    summary TEXT,
    summary_generated_at TEXT
);
```

**Pros:**
- Has `synergy_card_id` column ✅
- Has `tags` column ✅
- Has branching support (`parent_thread_id`, `branch_point_message_id`) ✅
- Has `summary` for AI-generated summaries ✅

**Cons:**
- ⚠️ NO `agent` or `location` column (assignment not stored here)
- ⚠️ NO `archived` column (archived threads may use metadata JSON)
- ⚠️ `metadata` is TEXT (JSON blob) - hard to query

### ⚠️ DUPLICATE: `saved_threads` Table

**Purpose:** Appears to be older format for thread storage

**Schema Differences:**
- `saved_threads` uses `thread_id` as PRIMARY KEY (TEXT)
- `threads` uses `id` as PRIMARY KEY (INTEGER) + `thread_slug` (TEXT)
- `saved_threads` has `location` column (agent assignment) ✅
- `threads` does NOT have `location` column ❌

**Recommendation:**
- **Option A:** Migrate all data from `saved_threads` → `threads` table
- **Option B:** Add `location` column to `threads` table
- **Option C:** Use `thread_assignments` table for assignments (RECOMMENDED)

### ✅ GOOD: `messages` Table Schema

**Schema:**
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER NOT NULL,
    thread_id INTEGER,
    session_id TEXT,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    prompt TEXT,
    response_data TEXT,
    user_id INTEGER,
    api_session_id TEXT,
    include BOOLEAN,
    feedback_score INTEGER,
    tool_calls TEXT,
    tokens_used INTEGER,
    response_time_ms INTEGER,
    embedding_vector TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    metadata TEXT
);
```

**Pros:**
- Rich metadata (tokens, response time, feedback) ✅
- Tool call tracking ✅
- Embedding vector support (for semantic search) ✅
- Links to both `thread_id` (integer) and `session_id` (text) ✅

---

## DATABASE 3: synergy_sessions.db ✅ FIXED

### Tables Found: 2
1. `sessions` - Legacy Synergy sessions
2. `synergy_sessions` - Current Synergy sessions

### ✅ FIXED: `synergy_sessions` Table Schema

**Current Schema (AFTER FIX):**
```sql
CREATE TABLE synergy_sessions (
    session_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    platforms_involved TEXT,
    status TEXT,
    kanban_column TEXT,
    priority TEXT,
    due_date TEXT,
    created_at TEXT,
    updated_at TEXT,
    assignees TEXT,
    tags TEXT,
    notes TEXT,
    documents TEXT,
    links TEXT,
    next_steps TEXT,
    checklist TEXT,
    google_task_id TEXT,
    google_calendar_event_id TEXT,
    google_calendar_id TEXT,
    microsoft_todo_id TEXT,
    thread_ids TEXT,          -- ✅ PRESENT
    assigned_agents TEXT      -- ✅ PRESENT
);
```

**Pros:**
- `thread_ids` column exists ✅
- `assigned_agents` column exists ✅
- Rich metadata (priority, status, tags, notes) ✅
- Integration fields (Google Tasks, Calendar, Microsoft To-Do) ✅

**Storage Format:**
- `thread_ids`: JSON array of thread IDs: `["thread-123", "thread-456"]`
- `assigned_agents`: JSON array of agent names: `["Prime Agent", "Agent Alpha-1"]`

**Cons:**
- ⚠️ Using TEXT columns for JSON arrays (harder to query)
- ⚠️ No foreign key constraints to `threads` table
- ⚠️ No cascade delete if thread deleted

### ⚠️ DUPLICATE: `sessions` Table (Legacy)

**Purpose:** Appears to be older format for Synergy sessions

**Schema Differences:**
- `sessions` table is simpler (fewer fields)
- `synergy_sessions` table is richer (more integrations)
- Both have same `session_id` primary key

**Recommendation:**
- Deprecate `sessions` table
- Migrate all data to `synergy_sessions` table
- Drop `sessions` table after migration

---

## DATABASE 4: kanban_analytics.db ✅ SEPARATE SYSTEM

### Tables Found: 13
1. `ai_predictions` - AI-powered delivery predictions
2. `clients` - Client data
3. `dependency_tracking` - Task dependencies
4. `invoices` - Invoice management
5. `invoice_items` - Invoice line items
6. `milestones` - Project milestones
7. `payments` - Payment tracking
8. `projects` - Project data
9. `sqlite_sequence` - System table
10. `tickets` - Kanban tickets
11. `time_tracking` - Time logging
12. `user_activity` - User activity logs
13. `workflows` - Workflow definitions

### Analysis:
- **Purpose:** Separate business management system
- **NOT RELATED** to AI agent threads or Synergy sessions
- **CORRECT DESIGN:** Keep separate for data isolation
- **No action needed** for thread persistence issues

---

## CRITICAL FIXES REQUIRED

### Fix 1: Create `thread_assignments` Table ❌ URGENT

**Location:** `ai_infrastructure.db`

**SQL Migration:**
```sql
-- Create thread assignments table
CREATE TABLE IF NOT EXISTS thread_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    location TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, location)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_thread_assignments_user 
ON thread_assignments(user_id);

CREATE INDEX IF NOT EXISTS idx_thread_assignments_session 
ON thread_assignments(session_id);

CREATE INDEX IF NOT EXISTS idx_thread_assignments_location 
ON thread_assignments(user_id, location);

-- Create trigger to update updated_at
CREATE TRIGGER IF NOT EXISTS update_thread_assignments_timestamp
AFTER UPDATE ON thread_assignments
FOR EACH ROW
BEGIN
    UPDATE thread_assignments 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;
```

**Why This Fixes Persistence:**
- Stores thread assignments in database (not localStorage)
- Survives browser refresh
- Supports multi-device sync
- Supports multi-user assignments

**Backend API Endpoints Required:**
```python
# AI_infrastructure/routes/thread_assignment_routes.py

@app.route('/api/thread-assignments/assign', methods=['POST'])
def assign_thread():
    # POST { user_id, session_id, location }
    # UPSERT thread assignment (replace if location already occupied)
    # Return { success, assignment, displaced_thread }

@app.route('/api/thread-assignments', methods=['GET'])
def get_assignments():
    # GET ?user_id=1
    # Return { success, assignments: { 'prime': 'thread-123', 'agent-1': 'thread-456' } }

@app.route('/api/thread-assignments/validate', methods=['GET'])
def validate_assignments():
    # GET ?user_id=1
    # Check for orphaned threads, duplicate assignments
    # Return { valid, errors, fixed_count }
```

---

### Fix 2: Add Location Column to `threads` Table ⚠️ OPTIONAL

**Location:** `sessions.db`

**SQL Migration:**
```sql
-- Add location column to threads table
ALTER TABLE threads ADD COLUMN location TEXT DEFAULT NULL;

-- Create index
CREATE INDEX IF NOT EXISTS idx_threads_location ON threads(location);

-- Migrate data from saved_threads if needed
UPDATE threads 
SET location = (
    SELECT location 
    FROM saved_threads 
    WHERE saved_threads.session_id = threads.thread_slug
)
WHERE EXISTS (
    SELECT 1 
    FROM saved_threads 
    WHERE saved_threads.session_id = threads.thread_slug
);
```

**Why This Is Optional:**
- Thread assignments SHOULD be in `thread_assignments` table (separation of concerns)
- But having `location` in `threads` table provides denormalized cache
- Faster queries (no JOIN needed)
- Easier debugging

---

### Fix 3: Consolidate Thread Tables ⚠️ MEDIUM PRIORITY

**Location:** `sessions.db`

**Options:**

**Option A: Migrate saved_threads → threads**
```sql
-- Migrate all threads from saved_threads to threads
INSERT OR IGNORE INTO threads (
    thread_slug, user_id, name, created_at, updated_at, 
    tags, synergy_card_id, metadata
)
SELECT 
    session_id, 
    user_id, 
    thread_name, 
    created_at, 
    last_updated,
    tags,
    synergy_card_id,
    json_object(
        'agent_id', agent_id,
        'location', location,
        'message_count', message_count,
        'conversation', conversation
    )
FROM saved_threads;

-- Drop old table after verification
DROP TABLE saved_threads;
```

**Option B: Keep Both (Not Recommended)**
- Requires dual writes to both tables
- Data consistency issues
- More complex queries

---

## RECOMMENDED IMPLEMENTATION PLAN

### Phase 1: Immediate Fixes (TODAY) ❌ CRITICAL

1. **Create Migration Script:**
   ```powershell
   # AI_infrastructure/migrations/001_create_thread_assignments.py
   ```

2. **Create `thread_assignments` Table:**
   ```python
   import sqlite3
   
   conn = sqlite3.connect('data/ai_infrastructure.db')
   cursor = conn.cursor()
   
   cursor.execute('''
       CREATE TABLE IF NOT EXISTS thread_assignments (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           user_id INTEGER NOT NULL,
           session_id TEXT NOT NULL,
           location TEXT NOT NULL,
           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
           updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
           UNIQUE(user_id, location)
       )
   ''')
   
   conn.commit()
   conn.close()
   print("✅ thread_assignments table created")
   ```

3. **Create Backend API Routes:**
   - `POST /api/thread-assignments/assign`
   - `GET /api/thread-assignments`
   - `GET /api/thread-assignments/validate`

4. **Test Thread Persistence:**
   - Create thread in Prime
   - Assign to Agent Alpha-1
   - Refresh browser
   - Verify thread still assigned to Alpha-1

### Phase 2: Schema Improvements (THIS WEEK) ⚠️ HIGH

1. **Add `location` Column to `threads` Table:**
   - Migration script
   - Update backend INSERT statements
   - Update frontend to send location

2. **Migrate `saved_threads` → `threads`:**
   - Data migration script
   - Verify all data migrated
   - Drop `saved_threads` table

3. **Deprecate Legacy `sessions` Table in synergy_sessions.db:**
   - Migrate data to `synergy_sessions` table
   - Update backend queries
   - Drop `sessions` table

### Phase 3: Optimization (NEXT WEEK) ✅ NICE-TO-HAVE

1. **Add Foreign Key Constraints:**
   ```sql
   -- Requires SQLite with foreign_keys enabled
   PRAGMA foreign_keys = ON;
   
   -- Add FK from thread_assignments to threads
   -- (Need to recreate table to add FK in SQLite)
   ```

2. **Add Cascade Deletes:**
   - Delete thread → Delete assignments
   - Delete thread → Remove from Synergy cards

3. **Add Indexes for Performance:**
   - Composite indexes on common queries
   - Full-text search indexes on thread content

---

## VERIFICATION QUERIES

### Check if `thread_assignments` Table Exists:
```sql
SELECT name FROM sqlite_master 
WHERE type='table' AND name='thread_assignments';
```

**Expected:** 1 row if table exists, 0 rows if missing

### Check Synergy Columns:
```sql
PRAGMA table_info(synergy_sessions);
```

**Expected:** Should see rows for `thread_ids` and `assigned_agents`

### Count Thread Assignments:
```sql
SELECT COUNT(*) FROM thread_assignments;
```

**Expected:** Number of active thread assignments

### View All Assignments:
```sql
SELECT 
    ta.id,
    ta.user_id,
    ta.session_id,
    ta.location,
    t.name as thread_name,
    ta.created_at,
    ta.updated_at
FROM thread_assignments ta
LEFT JOIN threads t ON t.thread_slug = ta.session_id
ORDER BY ta.updated_at DESC;
```

---

## TESTING SCRIPT

Create `test_database_schemas.py`:

```python
import sqlite3
import json
from pathlib import Path

def check_database(db_path, expected_tables):
    """Check if database has expected tables"""
    print(f"\n{'='*60}")
    print(f"Checking: {db_path}")
    print(f"{'='*60}")
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n✅ Found {len(tables)} tables:")
    for table in tables:
        print(f"   - {table}")
    
    # Check expected tables
    missing = []
    for expected in expected_tables:
        if expected not in tables:
            missing.append(expected)
    
    if missing:
        print(f"\n❌ Missing tables: {missing}")
    else:
        print(f"\n✅ All expected tables present")
    
    conn.close()
    return len(missing) == 0

# Run checks
results = []

results.append(check_database(
    'data/ai_infrastructure.db',
    ['thread_assignments', 'users', 'user_platform_credentials']
))

results.append(check_database(
    'data/sessions.db',
    ['threads', 'messages']
))

results.append(check_database(
    'data/synergy_sessions.db',
    ['synergy_sessions']
))

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"Passed: {sum(results)}/{len(results)} databases")

if all(results):
    print("✅ ALL CHECKS PASSED")
else:
    print("❌ SOME CHECKS FAILED - Review output above")
```

---

## STATUS SUMMARY

| Database | Status | Critical Issues | Action Required |
|----------|--------|----------------|-----------------|
| `ai_infrastructure.db` | ❌ BROKEN | Missing `thread_assignments` table | Create table immediately |
| `sessions.db` | ⚠️ NEEDS WORK | Duplicate tables, missing columns | Migrate and consolidate |
| `synergy_sessions.db` | ✅ FIXED | Columns present, duplicate table | Deprecate legacy table |
| `kanban_analytics.db` | ✅ CORRECT | None | No action needed |

---

## NEXT STEPS

1. **IMMEDIATE (Today):**
   - ✅ Run migration to create `thread_assignments` table
   - ✅ Test thread persistence after browser refresh
   - ✅ Verify Synergy card shows thread IDs and agents

2. **THIS WEEK:**
   - ⚠️ Add `location` column to `threads` table
   - ⚠️ Migrate `saved_threads` → `threads`
   - ⚠️ Create backend API routes for thread assignments

3. **NEXT WEEK:**
   - ✅ Add foreign key constraints
   - ✅ Add cascade deletes
   - ✅ Optimize indexes

---

**Status:** ❌ CRITICAL FIX REQUIRED  
**Priority:** P0 (Blocking)  
**Estimated Time:** 2-4 hours for Phase 1  
**Files to Create:** 
- `AI_infrastructure/migrations/001_create_thread_assignments.sql`
- `AI_infrastructure/routes/thread_assignment_routes.py`
- `test_database_schemas.py`
