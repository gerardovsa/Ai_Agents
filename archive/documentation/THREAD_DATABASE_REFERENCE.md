# Thread Database Structure Reference

## 📊 Database Overview

### 🗄️ **Primary Databases**
1. **`data/sessions.db`** - Main threads, messages, assignments
2. **`data/ai_infrastructure.db`** - Users, OAuth, credentials  
3. **`data/synergy_sessions.db`** - Synergy card integration

---

## 🔑 Critical Thread Identification (MUST UNDERSTAND!)

### **Two Different IDs Per Thread:**

```
┌─────────────────────────────────────────────────────────────┐
│ THREAD RECORD IN DATABASE                                   │
├─────────────────────────────────────────────────────────────┤
│ threads.id = 2                  ← Internal DB ID (auto-inc) │
│ threads.thread_slug = '1762664086386'  ← PRIMARY ID (EVERYWHERE!) │
└─────────────────────────────────────────────────────────────┘
```

**✅ ARCHITECTURE DECISION: Use `thread_slug` as Primary Identifier**

**⚠️ CRITICAL DISTINCTIONS:**

| Context | ID Used | Example | Purpose |
|---------|---------|---------|---------|
| **Frontend (UI)** | `thread_slug` ✅ | `'1762664086386'` | User-facing thread ID |
| **API Parameters** | `thread_slug` ✅ | `'1762664086386'` | All API endpoints |
| **Thread Assignments** | `thread_slug` ✅ | `'1762664086386'` | Location tracking |
| **Synergy Sessions** | `thread_slug` ✅ | `'1762664086386'` | External integrations |
| **Database JOINs** | `id` ⚠️ | `2` | Internal FK only (hidden) |
| **Messages FK** | `id` ⚠️ | `2` | Links to threads.id internally |

**Golden Rule:** `thread_slug` is the primary identifier everywhere EXCEPT internal database foreign key relationships.

---

## 📋 Table: `threads` (sessions.db)

**Purpose:** Main thread/conversation storage

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| **`id`** | INTEGER (PK) | **Internal database ID** | `1`, `2`, `3` |
| **`thread_slug`** | TEXT (UNIQUE) | **External ID (used in UI)** | `'1762664086386'` |
| `user_id` | INTEGER | Owner user ID | `12` |
| `title` | TEXT | Display title | `'Untitled Thread'` |
| `name` | TEXT | Thread name | `'Smart toot test'` |
| `location` | TEXT | Current location | `'prime'`, `'agent-1'` |
| `agent_id` | TEXT | Assigned agent | `'prime'`, `'agent-1'` |
| `message_count` | INTEGER | Number of messages | `0`, `5`, `20` |
| `synergy_card_id` | TEXT | Linked Synergy session | `'sess_20251103_...'` |
| `tags` | TEXT (JSON) | Thread tags | `'["urgent", "bug"]'` |
| `metadata` | TEXT (JSON) | Additional data | `'{}'` |
| `parent_thread_id` | TEXT | For branched threads | `'1762663889170'` |
| `branch_point_message_id` | TEXT | Message where branched | `'msg_123'` |
| `branch_name` | TEXT | Branch label | `'Alternative approach'` |
| `archived` | INTEGER (BOOL) | Archive status | `0` or `1` |
| `created_at` | TIMESTAMP | Creation time | `'2025-11-09 14:51:29'` |
| `updated_at` | TIMESTAMP | Last update | `'2025-11-09 15:00:06'` |

**Current Data:**
```sql
SELECT id, thread_slug, name, message_count, location FROM threads;
-- Results:
-- id=1, thread_slug='1762663889170', name='Smart toot test', messages=0, location='prime'
-- id=2, thread_slug='1762664086386', name='Smart toot test', messages=0, location='prime'  
-- id=3, thread_slug='1762664406832', name='Smart toot test', messages=0, location='prime'
```

---

## 💬 Table: `messages` (sessions.db)

**Purpose:** Individual messages within threads

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| **`id`** | INTEGER (PK) | Message database ID | `1`, `2`, `3` |
| **`thread_id`** | INTEGER (FK) | **Links to `threads.id`** ⚠️ | `2` (NOT '1762664086386'!) |
| `role` | TEXT | Message sender | `'user'`, `'assistant'` |
| `content` | TEXT | Message text | `'Hello, how are you?'` |
| `timestamp` | TIMESTAMP | When sent | `'2025-11-09 15:05:00'` |
| `response_time` | REAL | AI response time (ms) | `1234.56` |

**⚠️ CRITICAL:** Messages link via `threads.id` (the internal ID), NOT `thread_slug`!

**Current Status:** ❌ **0 messages in database** (this is why UI shows 0 messages)

**Correct Query:**
```sql
-- ✅ CORRECT: Join on threads.id
SELECT m.* FROM messages m
JOIN threads t ON m.thread_id = t.id
WHERE t.thread_slug = '1762664086386';

-- ❌ WRONG: This will fail
SELECT * FROM messages WHERE thread_id = '1762664086386';
```

---

## 📍 Table: `thread_assignments` (sessions.db)

**Purpose:** Track which thread is in which location (Prime/Agent columns)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `id` | INTEGER (PK) | Assignment ID | `1`, `2`, `3` |
| `user_id` | INTEGER | User who owns thread | `12` |
| **`thread_slug`** | TEXT | **Thread ID (uses slug!)** | `'1762664086386'` |
| `location` | TEXT | Where thread is displayed | `'prime'`, `'agent-1'`, `'agent-2'` |
| `assigned_at` | TIMESTAMP | When assigned | `'2025-11-09 14:54:46'` |
| `updated_at` | TIMESTAMP | Last location change | `'2025-11-09 15:00:00'` |
| `metadata` | TEXT (JSON) | Extra data | `'{}'` |

**Current Status:** ❌ **0 assignments** (threads exist but no location tracking)

**Note:** This table uses `thread_slug` (not `threads.id`) because it's tracking UI state

---

## 🔗 Table: `synergy_sessions` (synergy_sessions.db)

**Purpose:** Synergy card → threads mapping

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| **`session_id`** | TEXT (PK) | Synergy card ID | `'sess_20251103_0906_veterinary'` |
| `title` | TEXT | Card title | `'Vet Practice Management'` |
| **`thread_ids`** | TEXT (JSON) | **Array of thread_slugs** | `'["1762663889170", "1762664086386"]'` |
| `status` | TEXT | Card status | `'active'`, `'completed'` |
| `kanban_column` | TEXT | Board column | `'in_progress'`, `'done'` |
| `tags` | TEXT (JSON) | Card tags | `'["urgent", "bug"]'` |
| `assigned_agents` | TEXT (JSON) | Agent assignments | `'["agent-1"]'` |

**Current Data:** 11 Synergy sessions exist, but `thread_ids` is NULL for all

---

## 🔄 Data Flow & Relationships

### **Frontend → Database Mapping:**

```
┌───────────────────────────────────────────────────────────────┐
│ FRONTEND (JavaScript)                                         │
├───────────────────────────────────────────────────────────────┤
│ thread.id = '1762664086386'  ← This is actually thread_slug! │
│ thread.title = 'Smart toot test'                              │
│ thread.messages = [...array of message objects...]            │
│ thread.message_count = 5                                      │
│ thread.location = 'prime'                                     │
└───────────────────────────────────────────────────────────────┘
                           ↓
                    API CALL
                           ↓
┌───────────────────────────────────────────────────────────────┐
│ BACKEND (Python/Flask)                                        │
├───────────────────────────────────────────────────────────────┤
│ thread_slug = request.json['thread_id']  # '1762664086386'   │
│                                                               │
│ # Look up internal ID                                        │
│ SELECT id FROM threads WHERE thread_slug = '1762664086386'   │
│ → internal_id = 2                                            │
│                                                               │
│ # Save messages using internal ID                            │
│ INSERT INTO messages (thread_id, role, content)              │
│ VALUES (2, 'user', 'Hello')  ← Uses id=2, not thread_slug!  │
└───────────────────────────────────────────────────────────────┘
```

---

## 🔍 Common Queries

### 1. **Get Thread with Message Count**
```sql
SELECT 
    t.id,
    t.thread_slug,
    t.name,
    t.location,
    COUNT(m.id) as message_count
FROM threads t
LEFT JOIN messages m ON m.thread_id = t.id
WHERE t.thread_slug = '1762664086386'
GROUP BY t.id;
```

### 2. **Get All Messages for a Thread**
```sql
SELECT m.*
FROM messages m
JOIN threads t ON m.thread_id = t.id
WHERE t.thread_slug = '1762664086386'
ORDER BY m.timestamp ASC;
```

### 3. **Get Thread Location**
```sql
SELECT location
FROM thread_assignments
WHERE thread_slug = '1762664086386'
  AND user_id = 12;
```

### 4. **Get Threads Linked to Synergy Card**
```sql
SELECT 
    s.session_id,
    s.title,
    s.thread_ids,
    json_extract(s.thread_ids, '$') as thread_array
FROM synergy_sessions s
WHERE s.session_id = 'sess_20251103_0906_veterinary';
```

### 5. **List All Threads for User**
```sql
SELECT 
    t.thread_slug,
    t.name,
    t.location,
    COUNT(m.id) as msg_count,
    t.updated_at
FROM threads t
LEFT JOIN messages m ON m.thread_id = t.id
WHERE t.user_id = 12
GROUP BY t.id
ORDER BY t.updated_at DESC;
```

---

## ⚠️ Common Mistakes

### ❌ **Wrong: Using thread_slug in message JOIN**
```sql
SELECT * FROM messages WHERE thread_id = '1762664086386';
-- FAILS: thread_id is INTEGER (id), not TEXT (thread_slug)
```

### ✅ **Correct: Using internal id**
```sql
SELECT m.* FROM messages m
JOIN threads t ON m.thread_id = t.id
WHERE t.thread_slug = '1762664086386';
```

### ❌ **Wrong: Passing thread_slug to backend as ID**
```python
# Backend receiving frontend's thread.id (which is thread_slug)
thread_id = request.json['thread_id']  # '1762664086386'

# Don't do this:
INSERT INTO messages (thread_id, ...) VALUES (thread_id, ...)
# FAILS: Expects integer, got string
```

### ✅ **Correct: Look up internal ID first**
```python
thread_slug = request.json['thread_id']  # '1762664086386'

# Get internal ID
result = db.execute(
    "SELECT id FROM threads WHERE thread_slug = ?",
    (thread_slug,)
)
internal_id = result[0]['id']  # 2

# Now insert message
db.execute(
    "INSERT INTO messages (thread_id, ...) VALUES (?, ...)",
    (internal_id, ...)
)
```

---

## 🐛 Current Issues (as of Nov 9, 2025)

1. ✅ **Threads exist** - 3 threads in database
2. ❌ **NO MESSAGES** - messages table is empty (0 rows)
3. ❌ **NO ASSIGNMENTS** - thread_assignments table is empty
4. ❌ **NO SYNERGY LINKS** - thread_ids column is NULL in all synergy_sessions

**This explains why:**
- Thread list shows "0 msgs" for all threads
- Switching threads doesn't load any messages  
- Thread locations aren't persisted across refreshes

---

## 📝 Summary for Developers

**Quick Reference:**

| What You Want | Table | Column | Type | Example |
|---------------|-------|--------|------|---------|
| User-facing thread ID | `threads` | `thread_slug` | TEXT | `'1762664086386'` |
| Internal database ID | `threads` | `id` | INTEGER | `2` |
| Thread title/name | `threads` | `name` | TEXT | `'Smart toot test'` |
| Message content | `messages` | `content` | TEXT | `'Hello'` |
| Message → Thread link | `messages` | `thread_id` | INTEGER | `2` (links to `threads.id`) |
| Thread location | `thread_assignments` | `location` | TEXT | `'prime'`, `'agent-1'` |
| Synergy → Threads | `synergy_sessions` | `thread_ids` | JSON | `["1762664086386"]` |

**Golden Rules:**
1. Frontend uses `thread_slug` as `thread.id`
2. Database JOINs use `threads.id` (internal integer)
3. Always look up internal ID before inserting messages
4. Thread assignments use `thread_slug` (not internal ID)
5. Synergy session links use JSON array of `thread_slug` values
