# Thread Endpoints Database Connection Analysis

**Generated:** November 23, 2025  
**Purpose:** Complete analysis of all thread-related endpoints and their database connections

---

## Overview

The AI Agents platform has **3 main thread route files** managing conversations across multiple AI agents:

1. **`thread_routes.py`** - Core thread CRUD operations (create, read, update, delete)
2. **`thread_assignment_routes.py`** - Thread assignment to agents (Prime, agent-1, agent-2, etc.)
3. **`thread_sharing_routes.py`** - Thread collaboration and sharing

---

## Database Architecture

### Connection Pattern

**ALL routes use Supabase PostgreSQL via connection pooling:**

```python
from shared.database_utils import get_database_connection, get_sessions_connection

# Two schemas used:
conn = get_database_connection('sessions')      # For threads, messages
conn = get_sessions_connection()               # Shortcut for sessions schema
```

### Key Tables

#### 1. `sessions.threads` (Primary table)
```sql
CREATE TABLE sessions.threads (
  id INTEGER PRIMARY KEY,                    -- Auto-increment internal ID
  thread_slug TEXT UNIQUE NOT NULL,          -- User-facing ID (timestamp)
  user_id INTEGER,                           -- Owner
  name TEXT,                                 -- Thread title
  location TEXT,                             -- WHERE it's displayed (prime, agent-1, etc.)
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  metadata TEXT,                             -- JSON metadata
  tags TEXT,                                 -- JSON array
  synergy_card_id TEXT,                      -- Link to Synergy card
  parent_thread_id INTEGER,                  -- For branching
  branch_name TEXT,
  branch_point_message_id TEXT,
  archived INTEGER DEFAULT 0,
  token_count INTEGER DEFAULT 0,
  locked_to_device_id TEXT,                  -- Device locking
  locked_at TIMESTAMP,
  lock_mode TEXT DEFAULT 'unlocked',
  workflow_slug TEXT,                        -- Link to automation
  workflow_title TEXT,
  internal_doc_slug TEXT,                    -- Link to internal doc
  internal_doc_title TEXT,
  automation_slug TEXT,
  automation_title TEXT
)
```

**CRITICAL:** `location` column stores UI placement:
- `'prime'` - Main AI interface
- `'agent-1'` through `'agent-26'` - Multi-agent columns
- `'stock_ai'` - Stock management agent
- `'data_agent'` - Data analysis agent
- `'single_viewer'` - Single thread viewer

#### 2. `sessions.messages` (Thread content)
```sql
CREATE TABLE sessions.messages (
  id INTEGER PRIMARY KEY,
  thread_id INTEGER,                         -- FK to threads.id (internal ID)
  role TEXT,                                 -- 'user', 'assistant', 'system'
  content JSONB,                             -- Message content
  timestamp TIMESTAMP,
  user_id INTEGER,
  session_id TEXT,                           -- Thread slug (for compatibility)
  tool_calls TEXT,                           -- Tool usage JSON
  tokens_used INTEGER,
  model TEXT,
  metadata TEXT
)
```

#### 3. `ai_infrastructure.users` (User metadata)
```sql
-- users.metadata column stores legacy thread assignments (JSON)
{
  "thread_assignments": {
    "agent-1": "1763856372531",
    "agent-2": "1763816340198"
  }
}
```

**NOTE:** `sessions.threads.location` is now the **single source of truth** for assignments. `users.metadata` kept for backward compatibility.

---

## File 1: `thread_routes.py` (1944 lines)

### Purpose
Core thread management - CRUD operations for conversations

### Database Connection Pattern
```python
conn = get_database_connection('sessions')  # Always uses sessions schema
cursor = conn.cursor()                      # RealDictCursor (returns dicts)
```

### Endpoints (17 total)

#### 1. **POST** `/api/threads/create`
**Purpose:** Create new thread  
**Database:**
```python
# Query: sessions.threads table
INSERT INTO sessions.threads (
    thread_slug, workspace_id, name, user_id, created_at, updated_at,
    metadata, location, tags, synergy_card_id,
    parent_thread_id, branch_point_message_id, branch_name
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
RETURNING id
```
**Returns:** `{"success": true, "thread": {...}}`

---

#### 2. **GET** `/api/threads/list`
**Purpose:** List all user's threads  
**Database:**
```python
# Query: sessions.threads with optional filters
SELECT * FROM sessions.threads
WHERE user_id = %s
  AND archived = 0
ORDER BY updated_at DESC
LIMIT %s
```
**Returns:** `{"success": true, "threads": [...]}`

---

#### 3. **GET** `/api/threads/search`
**Purpose:** Search threads by title/content  
**Database:**
```python
# Query: sessions.threads with ILIKE search
SELECT * FROM sessions.threads
WHERE user_id = %s
  AND name ILIKE %s
ORDER BY updated_at DESC
```
**Returns:** `{"success": true, "threads": [...]}`

---

#### 4. **GET** `/api/threads/load/<thread_id>`
**Purpose:** Load thread messages  
**Database:**
```python
# Step 1: Get thread metadata
SELECT * FROM sessions.threads WHERE thread_slug = %s

# Step 2: Get messages
SELECT * FROM sessions.messages
WHERE thread_id = %s  -- Uses internal ID from step 1
ORDER BY timestamp ASC
```
**Returns:** `{"success": true, "thread": {...}, "messages": [...]}`

---

#### 5. **DELETE** `/api/threads/<thread_id>`
**Purpose:** Delete thread and messages  
**Database:**
```python
# Step 1: Get internal ID
SELECT id FROM sessions.threads WHERE thread_slug = %s

# Step 2: Delete messages first (FK constraint)
DELETE FROM sessions.messages WHERE thread_id = %s

# Step 3: Delete thread
DELETE FROM sessions.threads WHERE id = %s
```
**Returns:** `{"success": true, "deleted": true}`

---

#### 6. **POST** `/api/threads/save`
**Purpose:** Save/update thread (legacy saved_threads table)  
**Database:**
```python
# Query: sessions.saved_threads table (legacy)
INSERT INTO sessions.saved_threads (
    thread_id, agent_id, session_id, user_id, location,
    thread_name, conversation, message_count, ...
) VALUES (...)
ON CONFLICT (thread_id) DO UPDATE SET ...
```
**Returns:** `{"success": true, "saved": true}`

---

#### 7. **PUT** `/api/threads/<thread_id>`
**Purpose:** Update thread metadata (title, tags, etc.)  
**Database:**
```python
# Query: sessions.threads update
UPDATE sessions.threads
SET name = %s,
    tags = %s,
    metadata = %s,
    updated_at = NOW()
WHERE thread_slug = %s
```
**Returns:** `{"success": true, "updated": true}`

---

#### 8. **POST** `/api/threads/<thread_id>/archive`
**Purpose:** Archive thread  
**Database:**
```python
UPDATE sessions.threads
SET archived = 1, updated_at = NOW()
WHERE thread_slug = %s
```

---

#### 9. **POST** `/api/threads/<thread_id>/unarchive`
**Purpose:** Restore archived thread  
**Database:**
```python
UPDATE sessions.threads
SET archived = 0, updated_at = NOW()
WHERE thread_slug = %s
```

---

#### 10. **GET** `/api/threads/stats`
**Purpose:** Get thread statistics  
**Database:**
```python
# Multiple queries:
SELECT COUNT(*) FROM sessions.threads WHERE user_id = %s
SELECT COUNT(*) FROM sessions.threads WHERE user_id = %s AND archived = 1
SELECT COUNT(*) FROM sessions.messages WHERE user_id = %s
```

---

#### 11. **POST** `/api/threads/autosave`
**Purpose:** Auto-save thread during conversation  
**Database:**
```python
# Similar to /save but with auto-save flag
INSERT INTO sessions.saved_threads (...)
ON CONFLICT DO UPDATE ...
```

---

#### 12. **POST** `/api/threads/<thread_id>/lock`
**Purpose:** Lock thread to specific device  
**Database:**
```python
UPDATE sessions.threads
SET locked_to_device_id = %s,
    lock_mode = 'locked',
    locked_at = %s
WHERE thread_slug = %s
```

---

#### 13. **POST** `/api/threads/<thread_id>/unlock`
**Purpose:** Unlock thread  
**Database:**
```python
UPDATE sessions.threads
SET locked_to_device_id = NULL,
    lock_mode = 'unlocked',
    locked_at = NULL
WHERE thread_slug = %s
```

---

#### 14. **GET** `/api/threads/<thread_id>/lock-status`
**Purpose:** Check if thread is locked  
**Database:**
```python
SELECT locked_to_device_id, lock_mode, locked_at
FROM sessions.threads
WHERE thread_slug = %s
```

---

#### 15. **POST** `/api/threads/<thread_id>/messages`
**Purpose:** Add message to thread  
**Database:**
```python
# Step 1: Get internal thread ID
SELECT id FROM sessions.threads WHERE thread_slug = %s

# Step 2: Insert message
INSERT INTO sessions.messages (
    thread_id, role, content, timestamp, user_id, session_id
) VALUES (%s, %s, %s, %s, %s, %s)
```

---

#### 16. **GET** `/api/threads/<thread_id>/messages`
**Purpose:** Get thread messages only  
**Database:**
```python
# Step 1: Get internal ID
SELECT id FROM sessions.threads WHERE thread_slug = %s

# Step 2: Get messages
SELECT * FROM sessions.messages
WHERE thread_id = %s
ORDER BY timestamp ASC
```

---

#### 17. **POST** `/api/threads/<thread_id>/link-to-user`
**Purpose:** Link thread to user (assignment)  
**Database:**
```python
# Updates both locations:
# 1. sessions.threads.location
UPDATE sessions.threads
SET location = %s, updated_at = NOW()
WHERE thread_slug = %s

# 2. ai_infrastructure.users.metadata (legacy)
UPDATE ai_infrastructure.users
SET metadata = %s
WHERE id = %s
```

---

## File 2: `thread_assignment_routes.py` (708 lines)

### Purpose
Manage WHERE threads are displayed in the UI (Prime, agent-1, agent-2, etc.)

### Database Connection Pattern
```python
def get_db_connection():
    return get_sessions_connection()  # Sessions schema

# Queries BOTH schemas:
# - ai_infrastructure.users (metadata column - legacy)
# - sessions.threads (location column - NEW single source of truth)
```

### Key Insight: Dual Storage System

**NEW (Single Source of Truth):**
```sql
-- sessions.threads.location column
UPDATE sessions.threads SET location = 'agent-1' WHERE thread_slug = '1763856372531'
```

**LEGACY (Backward Compatibility):**
```sql
-- ai_infrastructure.users.metadata JSON
UPDATE ai_infrastructure.users
SET metadata = '{"thread_assignments": {"agent-1": "1763856372531"}}'
WHERE id = 14
```

### Endpoints (10 total)

#### 1. **GET** `/api/thread-assignments`
**Alias:** `/api/thread-assignments/list`  
**Purpose:** Get all thread assignments for user  
**Database:**
```python
# Query: sessions.threads WHERE location is an agent
SELECT thread_slug, location
FROM sessions.threads
WHERE user_id = %s
  AND location IS NOT NULL
  AND location != 'prime'
ORDER BY updated_at DESC
```
**Returns:**
```json
{
  "success": true,
  "assignments": {
    "agent-1": "1763856372531",
    "agent-2": "1763816340198"
  }
}
```

**Bug Fix (Nov 23, 2025):**  
Changed from tuple access `row[0]` to dict access `row['thread_slug']` because RealDictCursor returns dictionaries.

---

#### 2. **POST** `/api/thread-assignments`
**Purpose:** Save thread assignment (assign thread to agent)  
**Database:**
```python
# Step 1: Check if user exists
SELECT id FROM ai_infrastructure.users WHERE id = %s

# Step 2: Get current metadata
SELECT metadata FROM ai_infrastructure.users WHERE id = %s

# Step 3: Update BOTH locations
# 3a. Update users.metadata (legacy)
UPDATE ai_infrastructure.users
SET metadata = %s  -- JSON with thread_assignments
WHERE id = %s

# 3b. Update threads.location (single source of truth)
UPDATE sessions.threads
SET location = %s, updated_at = NOW()
WHERE thread_slug = %s AND user_id = %s
```

**Enforcement Rules:**
- Only ONE thread per agent location
- If assigning to occupied location, old thread moves to 'prime'
- Prime is implicit (any thread not in an agent)

---

#### 3. **POST** `/api/thread-assignments/assign`
**Purpose:** Assign thread to specific location  
**Database:** Same as endpoint #2

---

#### 4. **POST** `/api/agent/threads/<thread_id>/assign`
**Purpose:** Assign by thread ID (REST-style)  
**Database:** Same as endpoint #2

---

#### 5. **POST** `/api/thread-assignments/clear/<location>`
**Purpose:** Remove thread from agent location (move to prime)  
**Database:**
```python
# Step 1: Get current assignments from metadata
SELECT metadata FROM ai_infrastructure.users WHERE id = %s

# Step 2: Update metadata (remove from JSON)
UPDATE ai_infrastructure.users SET metadata = %s WHERE id = %s

# Step 3: Update threads.location to 'prime'
UPDATE sessions.threads
SET location = 'prime', updated_at = NOW()
WHERE thread_slug = %s AND user_id = %s
```

---

#### 6. **GET** `/api/thread-assignments/location/<session_id>`
**Purpose:** Get current location of specific thread  
**Database:**
```python
# Query metadata JSON
SELECT metadata FROM ai_infrastructure.users WHERE id = %s
# Then parse JSON to find which agent has this thread
```

---

#### 7. **POST** `/api/thread-assignments/validate`
**Purpose:** Validate assignment structure  
**Database:**
```python
# Check all assigned threads exist
SELECT metadata FROM ai_infrastructure.users WHERE id = %s

# For each assigned thread, verify exists:
UPDATE sessions.threads
SET location = 'prime'
WHERE thread_slug = %s
  AND user_id = %s
  AND (
    location IS NULL
    OR location NOT IN ('agent-1', 'agent-2', ...)
  )
```

---

## File 3: `thread_sharing_routes.py` (435 lines)

### Purpose
Thread collaboration - share threads with other users

### Database Connection Pattern
```python
# Uses ThreadSharingManager class which connects to:
# - sessions.threads
# - sessions.thread_shares (share records)
# - sessions.thread_users (collaborators)
```

### Related Tables

#### `sessions.thread_shares`
```sql
CREATE TABLE sessions.thread_shares (
  id INTEGER PRIMARY KEY,
  thread_id INTEGER,                -- FK to threads.id
  shared_by INTEGER,                -- User who shared
  shared_with INTEGER,              -- User receiving share
  permission TEXT,                  -- 'view', 'edit', 'admin'
  share_type TEXT,                  -- 'direct', 'link', 'email'
  shared_at TIMESTAMP,
  expires_at TIMESTAMP,
  access_count INTEGER DEFAULT 0,
  revoked INTEGER DEFAULT 0,
  share_link TEXT                   -- Shareable URL
)
```

#### `sessions.thread_users`
```sql
CREATE TABLE sessions.thread_users (
  id INTEGER PRIMARY KEY,
  thread_id INTEGER,                -- FK to threads.id
  user_id INTEGER,                  -- Collaborator
  permission TEXT,                  -- 'view', 'edit', 'admin'
  added_at TIMESTAMP,
  is_owner INTEGER DEFAULT 0
)
```

### Endpoints (7 total)

#### 1. **POST** `/api/threads/<thread_slug>/share`
**Purpose:** Share thread with user  
**Database:**
```python
INSERT INTO sessions.thread_shares (
    thread_id, shared_by, shared_with, permission, share_type, shared_at
) VALUES (%s, %s, %s, %s, 'direct', NOW())

INSERT INTO sessions.thread_users (
    thread_id, user_id, permission, added_at
) VALUES (%s, %s, %s, NOW())
```

---

#### 2. **POST** `/api/threads/<thread_slug>/share-email`
**Purpose:** Share via email invitation  
**Database:** Same as #1 + email notification

---

#### 3. **POST** `/api/thread-shares/accept/<token>`
**Purpose:** Accept share invitation  
**Database:**
```python
# Validate token, then:
INSERT INTO sessions.thread_users (
    thread_id, user_id, permission
) VALUES (%s, %s, %s)

UPDATE sessions.thread_shares
SET access_count = access_count + 1,
    last_accessed = NOW()
WHERE share_link = %s
```

---

#### 4. **DELETE** `/api/threads/<thread_slug>/share/<user_id>`
**Purpose:** Revoke user access  
**Database:**
```python
UPDATE sessions.thread_shares
SET revoked = 1, revoked_at = NOW()
WHERE thread_id = %s AND shared_with = %s

DELETE FROM sessions.thread_users
WHERE thread_id = %s AND user_id = %s
```

---

#### 5. **GET** `/api/threads/<thread_slug>/collaborators`
**Purpose:** List who has access  
**Database:**
```python
SELECT tu.*, u.username, u.email
FROM sessions.thread_users tu
JOIN ai_infrastructure.users u ON tu.user_id = u.id
WHERE tu.thread_id = %s
```

---

#### 6. **GET** `/api/my-shared-threads`
**Purpose:** List threads shared with me  
**Database:**
```python
SELECT t.*, ts.permission
FROM sessions.threads t
JOIN sessions.thread_users tu ON t.id = tu.thread_id
WHERE tu.user_id = %s AND tu.is_owner = 0
```

---

#### 7. **PUT** `/api/threads/<thread_slug>/share/<user_id>`
**Purpose:** Update share permissions  
**Database:**
```python
UPDATE sessions.thread_users
SET permission = %s
WHERE thread_id = %s AND user_id = %s
```

---

## Database Connection Summary

### Connection Patterns Used

1. **Direct Connection (Most Common)**
```python
conn = get_database_connection('sessions')
cursor = conn.cursor()  # RealDictCursor
try:
    cursor.execute("SELECT ...")
    rows = cursor.fetchall()
    # rows = list of dicts: [{'id': 1, 'name': 'Thread'}, ...]
finally:
    conn.close()  # Returns to pool
```

2. **Shortcut Helper**
```python
conn = get_sessions_connection()  # Same as get_database_connection('sessions')
```

3. **Multi-Schema Access**
```python
# Same connection can query both schemas:
cursor.execute("SELECT * FROM sessions.threads ...")
cursor.execute("SELECT * FROM ai_infrastructure.users ...")
```

### Connection Pool Details

**Source:** `shared/database_utils.py`

```python
# Pool created per schema:
POOLS = {
    'sessions': SimpleConnectionPool(minconn=1, maxconn=2, dsn=SUPABASE_DB_URL),
    'ai_infrastructure': SimpleConnectionPool(minconn=1, maxconn=2, dsn=SUPABASE_DB_URL),
    'synergy_sessions': SimpleConnectionPool(minconn=1, maxconn=2, dsn=SUPABASE_DB_URL)
}

# Wrapper layers:
# PooledConnection → DatabaseConnection → DatabaseCursor (RealDictCursor)
```

**Key Features:**
- Auto-converts `?` placeholders to `%s` (PostgreSQL)
- Returns RealDictCursor (dict-like rows)
- Auto-closes connections (returns to pool)
- Schema prefixes required: `sessions.threads`, `ai_infrastructure.users`

---

## Critical Bugs Fixed (November 2025)

### Bug #1: KeyError: 0 in thread_assignment_routes.py

**Problem:**
```python
# WRONG - RealDictCursor returns dicts, not tuples!
for row in rows:
    thread_slug = str(row[0])  # KeyError: 0
    location = row[1]          # KeyError: 1
```

**Fix:**
```python
# CORRECT - Use dict key access
for row in rows:
    thread_slug = str(row['thread_slug'])
    location = row['location']
```

**Error Message:** `"Error getting thread assignments: 0"`  
**Cause:** `str(KeyError(0))` returns `"0"`

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER CREATES/USES THREAD                     │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              POST /api/threads/create                           │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ 1. Generate thread_slug (timestamp)                       │ │
│  │ 2. INSERT INTO sessions.threads                           │ │
│  │    (thread_slug, user_id, name, location='prime')         │ │
│  │ 3. Return thread object                                   │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│         USER ASSIGNS THREAD TO AGENT                            │
│              POST /api/thread-assignments                       │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ 1. Check if location occupied                             │ │
│  │ 2. If occupied, move old thread to 'prime'                │ │
│  │ 3. UPDATE sessions.threads SET location = 'agent-1'       │ │
│  │ 4. UPDATE ai_infrastructure.users.metadata (legacy)       │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│             USER SENDS MESSAGE                                  │
│              POST /api/agent/chat                               │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ 1. Get thread internal ID from thread_slug                │ │
│  │ 2. INSERT INTO sessions.messages                          │ │
│  │    (thread_id, role='user', content)                      │ │
│  │ 3. Process AI response                                    │ │
│  │ 4. INSERT INTO sessions.messages                          │ │
│  │    (thread_id, role='assistant', content)                 │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│             USER LOADS THREAD                                   │
│              GET /api/threads/load/<thread_id>                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ 1. SELECT * FROM sessions.threads WHERE thread_slug = ?   │ │
│  │ 2. SELECT * FROM sessions.messages WHERE thread_id = ?    │ │
│  │ 3. Return thread + messages                               │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Location Values Reference

### Valid Location Values in `sessions.threads.location`

| Location | Description | UI Display |
|----------|-------------|------------|
| `prime` | Main AI interface | Center panel |
| `agent-1` to `agent-26` | Multi-agent columns | Left sidebar columns |
| `stock_ai` | Stock management | Dedicated module |
| `data_agent` | Data analysis | Dedicated module |
| `single_viewer` | Single thread view | Full-screen mode |
| `NULL` | Unassigned | Defaults to prime |

### Thread Assignment Logic

1. **Create thread** → location = `'prime'`
2. **Assign to agent** → location = `'agent-1'` (etc.)
3. **Clear assignment** → location = `'prime'`
4. **Delete thread** → Removed from database

---

## Performance Considerations

### Connection Pooling
- **Pool size:** 1-2 connections per schema
- **Supabase limit:** 60 connections (Nano tier)
- **Reuse:** Connections returned to pool after use

### Query Optimization
- Indexed columns: `user_id`, `thread_slug`, `location`
- Avoid N+1 queries: Use JOINs where possible
- Use LIMIT for large result sets

### Common Patterns

**Good:**
```python
# Single query with JOIN
SELECT t.*, COUNT(m.id) as message_count
FROM sessions.threads t
LEFT JOIN sessions.messages m ON t.id = m.thread_id
WHERE t.user_id = %s
GROUP BY t.id
```

**Bad:**
```python
# N+1 query pattern
threads = cursor.execute("SELECT * FROM sessions.threads WHERE user_id = %s")
for thread in threads:
    # Separate query for each thread!
    cursor.execute("SELECT COUNT(*) FROM sessions.messages WHERE thread_id = %s", [thread['id']])
```

---

## Testing Checklist

When modifying thread endpoints:

- [ ] Test with RealDictCursor (dict access, not tuple)
- [ ] Test thread assignment enforcement (one per location)
- [ ] Test prime fallback (unassigned threads)
- [ ] Test branch creation (parent_thread_id)
- [ ] Test message insertion (FK constraints)
- [ ] Test thread deletion (cascade to messages)
- [ ] Test location updates (both tables)
- [ ] Test connection pool (no leaks)
- [ ] Test PostgreSQL placeholders (`%s` not `?`)
- [ ] Test schema prefixes (`sessions.threads`)

---

## Common Errors & Solutions

### Error: "KeyError: 0"
**Cause:** Accessing RealDictCursor result as tuple  
**Solution:** Use dict keys: `row['column_name']`

### Error: "column thread_slug does not exist"
**Cause:** Missing schema prefix  
**Solution:** Use `sessions.threads`, not `threads`

### Error: "connection pool exhausted"
**Cause:** Not closing connections  
**Solution:** Always use `finally: conn.close()`

### Error: "syntax error at or near '%s'"
**Cause:** Using SQLite placeholders in PostgreSQL  
**Solution:** Use `%s` not `?`

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Files** | 3 |
| **Total Endpoints** | 34 |
| **Database Schemas** | 2 (sessions, ai_infrastructure) |
| **Primary Tables** | 5 (threads, messages, saved_threads, thread_shares, thread_users) |
| **Connection Pattern** | Pooled PostgreSQL (Supabase) |
| **Cursor Type** | RealDictCursor (dict results) |
| **Location Values** | 30+ (prime, agent-1..26, stock_ai, etc.) |

**Key Insight:** All thread operations now use `sessions.threads.location` as the single source of truth for UI placement, with `users.metadata` maintained for backward compatibility only.

---

**Last Updated:** November 23, 2025  
**Status:** Production Analysis - All Endpoints Documented
