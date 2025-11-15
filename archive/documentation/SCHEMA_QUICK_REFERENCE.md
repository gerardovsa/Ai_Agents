# Database Schema - Quick Reference Card

**Use this for instant lookups during code analysis**

---

## 🗄️ Database Locations

```
data/
├── sessions.db              # Threads, messages, users
├── ai_infrastructure.db     # OAuth, credentials, sessions  
└── synergy_sessions.db      # Synergy multi-agent sessions
```

---

## 📋 Most-Used Tables

### `sessions.db` → `threads`
```sql
id                      INTEGER PRIMARY KEY
thread_slug             TEXT NOT NULL UNIQUE  -- "1762411564661"
user_id                 INTEGER
name                    TEXT NOT NULL         -- Thread title
location                TEXT DEFAULT 'prime'  -- 'prime', 'agent-1', etc.
metadata                TEXT                  -- JSON
tags                    TEXT DEFAULT '[]'     -- JSON array
synergy_card_id         TEXT
parent_thread_id        TEXT                  -- For branching
created_at, updated_at  TIMESTAMP
```

### `sessions.db` → `messages`
```sql
id              INTEGER PRIMARY KEY
thread_id       INTEGER               -- FK to threads.id
session_id      TEXT                  -- Thread identifier
role            TEXT NOT NULL         -- 'user', 'assistant', 'system'
content         TEXT NOT NULL         -- Message text
user_id         INTEGER
include         BOOLEAN DEFAULT 1     -- Include in context?
tool_calls      TEXT                  -- JSON array
metadata        TEXT                  -- JSON
created_at      TIMESTAMP
```

### `sessions.db` → `users`
```sql
id              INTEGER PRIMARY KEY
username        TEXT NOT NULL UNIQUE
email           TEXT UNIQUE
role            TEXT DEFAULT 'user'
metadata        TEXT                  -- ⚠️ CRITICAL: Contains thread_assignments
last_active     TIMESTAMP
```

**metadata JSON structure:**
```json
{
  "thread_assignments": {
    "agent-1": "1762411564661",
    "agent-2": "1762525766686"
  }
}
```

### `ai_infrastructure.db` → `oauth_tokens`
```sql
id              INTEGER PRIMARY KEY
user_id         INTEGER NOT NULL
platform        TEXT NOT NULL         -- 'google', 'microsoft', etc.
access_token    TEXT
refresh_token   TEXT
token_expiry    TIMESTAMP
scopes          TEXT                  -- JSON array
created_at      TIMESTAMP
```

---

## ⚡ Quick Queries

### Get Thread Assignments
```python
cursor.execute("SELECT metadata FROM users WHERE id = ?", [user_id])
metadata = json.loads(cursor.fetchone()['metadata'] or '{}')
assignments = metadata.get('thread_assignments', {})
```

### Get Thread with Message Count
```python
cursor.execute("""
    SELECT t.*, COUNT(m.id) as msg_count
    FROM threads t
    LEFT JOIN messages m ON t.id = m.thread_id
    WHERE t.thread_slug = ?
    GROUP BY t.id
""", [thread_slug])
```

### Get User's Threads
```python
cursor.execute("""
    SELECT * FROM threads 
    WHERE user_id = ? 
    ORDER BY updated_at DESC
""", [user_id])
```

### Get Thread Messages
```python
cursor.execute("""
    SELECT * FROM messages 
    WHERE thread_id = ? 
    ORDER BY created_at ASC
""", [thread_id])
```

---

## 🚨 Common Mistakes

### ❌ WRONG
```python
# Using thread_assignments table (it's empty!)
cursor.execute("SELECT * FROM thread_assignments WHERE user_id = ?", [user_id])

# Wrong database path
conn = sqlite3.connect('AI_infrastructure/sessions.db')

# Thread ID as integer
thread_id = 1762411564661  # ❌ Will fail

# Missing json.loads()
assignments = row['metadata']  # ❌ Returns string, not dict
```

### ✅ CORRECT
```python
# Using users.metadata JSON
cursor.execute("SELECT metadata FROM users WHERE id = ?", [user_id])
metadata = json.loads(cursor.fetchone()['metadata'])
assignments = metadata.get('thread_assignments', {})

# Correct database path
conn = sqlite3.connect('data/sessions.db')

# Thread ID as string
thread_id = "1762411564661"  # ✅ Correct

# Parse JSON
assignments = json.loads(row['metadata'] or '{}')  # ✅ Correct
```

---

## 🔑 Key Data Types

| Column Type | Python Type | Example |
|-------------|-------------|---------|
| `thread_slug` | `str` | `"1762411564661"` |
| `metadata` | `str` (JSON) | `'{"key": "value"}'` |
| `tags` | `str` (JSON) | `'["tag1", "tag2"]'` |
| `location` | `str` | `"prime"`, `"agent-1"` |
| `include` | `int` (0/1) | `1` = True, `0` = False |
| `created_at` | `str` | `"2025-11-08 20:00:00"` |

---

## 📊 Row Counts (as of Nov 8, 2025)

| Database | Table | Rows | Purpose |
|----------|-------|------|---------|
| sessions.db | threads | 20 | Conversation threads |
| sessions.db | messages | 460 | Chat messages |
| sessions.db | users | 2 | User accounts (IDs: 1, 14) |
| ai_infrastructure.db | oauth_tokens | 5 | OAuth credentials |
| ai_infrastructure.db | user_sessions | 338 | Login sessions |
| ai_infrastructure.db | thread_assignments | **0** | ⚠️ NOT USED |

---

## 🎯 Thread Assignment Truth

**WHERE assignments are stored:**
- ✅ `sessions.db` → `users.metadata` → `thread_assignments` (JSON)

**WHERE assignments are NOT stored:**
- ❌ `ai_infrastructure.db` → `thread_assignments` table (EMPTY)

**How to access:**
```python
# Step 1: Get user metadata
cursor.execute("SELECT metadata FROM users WHERE id = ?", [user_id])
row = cursor.fetchone()

# Step 2: Parse JSON
metadata = json.loads(row['metadata'] or '{}')

# Step 3: Extract assignments
assignments = metadata.get('thread_assignments', {})
# Result: {"agent-1": "1762411564661", "agent-2": "..."}
```

---

## 🔍 Index Hints

**Use these columns in WHERE for fast queries:**
- `threads`: `thread_slug` (UNIQUE), `user_id`, `location`
- `messages`: `thread_id`, `session_id`, `user_id`, `role`
- `users`: `username` (UNIQUE), `email` (UNIQUE)
- `oauth_tokens`: `user_id`, `platform`

---

## 📁 File Locations

- **Full schemas:** `DATABASE_SCHEMAS.json` (JSON)
- **Full docs:** `DATABASE_SCHEMAS.md` (1,697 lines)
- **Summary:** `DATABASE_SCHEMAS_SUMMARY.md`
- **This card:** `SCHEMA_QUICK_REFERENCE.md`
- **Validator:** `validate_code_against_schemas.py`

---

**Last Updated:** November 8, 2025  
**Status:** ✅ Complete and verified
