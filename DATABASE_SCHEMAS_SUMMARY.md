# Database Schemas - Quick Reference

**Generated:** 2025-11-08
**Purpose:** Quick reference for AI agent to cross-check code against actual database structure

---

## Overview

### Database Locations
- **sessions.db**: `C:\Users\gpoli\GIT\AI_agents\data\sessions.db` (8 tables, 650 rows)
- **ai_infrastructure.db**: `C:\Users\gpoli\GIT\AI_agents\data\ai_infrastructure.db` (16 tables, 385 rows)
- **synergy_sessions.db**: `C:\Users\gpoli\GIT\AI_agents\data\synergy_sessions.db` (2 tables, 20 rows)

---

## CRITICAL: Thread Assignment Storage

**⚠️ IMPORTANT:** Thread assignments are stored in **TWO PLACES**:

### 1. **Primary Storage** - `sessions.db` → `users.metadata` (JSON)
- **Table:** `users` 
- **Column:** `metadata` (TEXT, JSON format)
- **Structure:** `{"thread_assignments": {"agent-1": "session_id", "agent-2": "session_id"}}`
- **Used by:** `/api/thread-assignments/*` endpoints
- **Status:** ✅ ACTIVE (current system)

**Example:**
```json
{
  "id": 1,
  "username": "default_user",
  "metadata": "{\"thread_assignments\": {\"agent-2\": \"1762411564661\"}}"
}
```

### 2. **Legacy Table** - `ai_infrastructure.db` → `thread_assignments`
- **Table:** `thread_assignments`
- **Status:** ⚠️ EMPTY (not currently used, may be legacy)
- **Schema:**
  - `id` INTEGER PRIMARY KEY
  - `user_id` INTEGER NOT NULL
  - `session_id` TEXT NOT NULL
  - `location` TEXT NOT NULL (e.g., 'agent-1', 'agent-2', 'prime')
  - `created_at`, `updated_at` TIMESTAMP
  - UNIQUE constraint on `(user_id, location)`

**Note:** Code comments mention this table but it's empty. Assignments actually use `users.metadata` JSON column.

---

## sessions.db - Key Tables

### Table: `threads`
**Purpose:** Store conversation threads

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | PK | - | Auto-increment primary key |
| `thread_slug` | TEXT | NOT NULL | - | Unique thread identifier (timestamp-based) |
| `workspace_id` | INTEGER | NULL | - | Workspace reference |
| `user_id` | INTEGER | NULL | - | Owner user ID |
| `name` | TEXT | NOT NULL | - | Thread title/name |
| `created_at` | TIMESTAMP | NULL | CURRENT_TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | NULL | CURRENT_TIMESTAMP | Last update time |
| `metadata` | TEXT | NULL | - | JSON metadata |
| `tags` | TEXT | NULL | '[]' | JSON array of tags |
| `synergy_card_id` | TEXT | NULL | NULL | Link to Synergy card |
| `parent_thread_id` | TEXT | NULL | NULL | Parent thread for branching |
| `branch_point_message_id` | TEXT | NULL | NULL | Message where branch occurred |
| `branch_name` | TEXT | NULL | NULL | Branch name |
| `summary` | TEXT | NULL | NULL | Thread summary |
| `summary_generated_at` | TEXT | NULL | NULL | When summary was created |
| `location` | TEXT | NULL | 'prime' | Thread location (prime, agent-1, etc.) |

**Indexes:**
- `thread_slug` (UNIQUE)
- `user_id`, `workspace_id`, `location`, `created_at`, `parent_thread_id`, `synergy_card_id`

**Current Count:** 20 rows

---

### Table: `messages`
**Purpose:** Store individual messages in threads

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | PK | - | Auto-increment primary key |
| `workspace_id` | INTEGER | NOT NULL | - | Workspace reference |
| `thread_id` | INTEGER | NULL | - | Thread reference (FK to threads.id) |
| `session_id` | TEXT | NULL | - | Session identifier |
| `role` | TEXT | NOT NULL | - | 'user', 'assistant', 'system' |
| `content` | TEXT | NOT NULL | - | Message content |
| `prompt` | TEXT | NULL | - | Original prompt (if role=user) |
| `response_data` | TEXT | NULL | - | Full response data (JSON) |
| `user_id` | INTEGER | NULL | - | Message author |
| `api_session_id` | TEXT | NULL | - | API session reference |
| `include` | BOOLEAN | NULL | 1 | Include in context (default true) |
| `feedback_score` | INTEGER | NULL | - | User feedback rating |
| `tool_calls` | TEXT | NULL | - | JSON array of tool calls |
| `tokens_used` | INTEGER | NULL | - | Token count |
| `response_time_ms` | INTEGER | NULL | - | Response time in milliseconds |
| `embedding_vector` | TEXT | NULL | - | Message embedding |
| `created_at` | TIMESTAMP | NULL | CURRENT_TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | NULL | CURRENT_TIMESTAMP | Last update |
| `metadata` | TEXT | NULL | - | JSON metadata |

**Indexes:**
- `workspace_id`, `thread_id`, `session_id`, `user_id`, `role`, `include`, `created_at`

**Current Count:** 460 rows

---

### Table: `users`
**Purpose:** Store user accounts and metadata (including thread assignments)

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | PK | - | Auto-increment primary key |
| `username` | TEXT | NOT NULL | - | Unique username |
| `email` | TEXT | NULL | - | User email (unique) |
| `role` | TEXT | NULL | 'user' | User role (admin, user) |
| `created_at` | TIMESTAMP | NULL | CURRENT_TIMESTAMP | Account creation |
| `last_active` | TIMESTAMP | NULL | CURRENT_TIMESTAMP | Last activity |
| `metadata` | TEXT | NULL | - | **JSON metadata (includes thread_assignments)** |

**Indexes:**
- `username` (UNIQUE)
- `email` (UNIQUE)

**Current Count:** 2 rows

**metadata JSON Structure:**
```json
{
  "thread_assignments": {
    "agent-1": "1762411564661",
    "agent-2": "1762525766686",
    "agent-3": "1762530418975"
  }
}
```

---

### Table: `workspaces`
**Purpose:** Store workspace definitions

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | PK | - | Auto-increment primary key |
| `slug` | TEXT | NOT NULL | - | Workspace slug/identifier |
| `name` | TEXT | NOT NULL | - | Workspace name |
| `description` | TEXT | NULL | - | Workspace description |
| `created_at` | TIMESTAMP | NULL | CURRENT_TIMESTAMP | Creation time |

**Current Count:** 1 row

---

## ai_infrastructure.db - Key Tables

### Table: `oauth_tokens`
**Purpose:** Store OAuth tokens for platform integrations

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | PK | - | Auto-increment primary key |
| `user_id` | INTEGER | NOT NULL | - | User reference |
| `platform` | TEXT | NOT NULL | - | Platform name (google, microsoft, etc.) |
| `access_token` | TEXT | NULL | - | OAuth access token |
| `refresh_token` | TEXT | NULL | - | OAuth refresh token |
| `token_uri` | TEXT | NULL | - | Token endpoint URI |
| `client_id` | TEXT | NULL | - | OAuth client ID |
| `client_secret` | TEXT | NULL | - | OAuth client secret |
| `scopes` | TEXT | NULL | - | JSON array of scopes |
| `token_expiry` | TIMESTAMP | NULL | - | Token expiration time |
| `created_at` | TIMESTAMP | NULL | CURRENT_TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | NULL | CURRENT_TIMESTAMP | Last update |

**Indexes:**
- `(user_id, platform)` (UNIQUE)

**Current Count:** 5 rows

---

### Table: `user_platform_credentials`
**Purpose:** Store platform credentials (non-OAuth)

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | PK | - | Auto-increment primary key |
| `user_id` | INTEGER | NOT NULL | - | User reference |
| `platform` | TEXT | NOT NULL | - | Platform name |
| `credential_type` | TEXT | NOT NULL | - | Type (api_key, oauth, etc.) |
| `credential_key` | TEXT | NOT NULL | - | Credential identifier |
| `credential_value` | TEXT | NOT NULL | - | Credential value (encrypted) |
| `is_active` | BOOLEAN | NULL | 1 | Is credential active |
| `created_at` | TIMESTAMP | NULL | CURRENT_TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | NULL | CURRENT_TIMESTAMP | Last update |
| `metadata` | TEXT | NULL | - | JSON metadata |

**Indexes:**
- `(user_id, platform, credential_key)` (UNIQUE)

**Current Count:** 2 rows

---

### Table: `user_sessions`
**Purpose:** Track user login sessions

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | PK | - | Auto-increment primary key |
| `user_id` | INTEGER | NOT NULL | - | User reference |
| `session_token` | TEXT | NOT NULL | - | Unique session token |
| `ip_address` | TEXT | NULL | - | Client IP address |
| `user_agent` | TEXT | NULL | - | Client user agent |
| `created_at` | TIMESTAMP | NULL | CURRENT_TIMESTAMP | Session start |
| `last_active` | TIMESTAMP | NULL | CURRENT_TIMESTAMP | Last activity |
| `expires_at` | TIMESTAMP | NULL | - | Session expiration |
| `is_active` | BOOLEAN | NULL | 1 | Is session active |

**Indexes:**
- `session_token` (UNIQUE)
- `user_id`

**Current Count:** 338 rows

---

## synergy_sessions.db - Key Tables

### Table: `synergy_sessions`
**Purpose:** Store Synergy multi-agent sessions

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | PK | - | Auto-increment primary key |
| `session_id` | TEXT | NOT NULL | - | Unique session identifier |
| `title` | TEXT | NULL | - | Session title |
| `agent_1_thread_id` | TEXT | NULL | - | Thread ID for Agent 1 |
| `agent_2_thread_id` | TEXT | NULL | - | Thread ID for Agent 2 |
| `agent_3_thread_id` | TEXT | NULL | - | Thread ID for Agent 3 |
| `active_agent` | TEXT | NULL | - | Currently active agent |
| `created_at` | TEXT | NULL | - | Creation timestamp |
| `updated_at` | TEXT | NULL | - | Last update timestamp |
| `metadata` | TEXT | NULL | - | JSON metadata |

**Current Count:** 15 rows

---

## Common Code Patterns

### Thread Assignment Lookups
```python
# CORRECT - Fetch from users.metadata
cursor.execute("SELECT metadata FROM users WHERE id = ?", [user_id])
row = cursor.fetchone()
metadata = json.loads(row['metadata'])
assignments = metadata.get('thread_assignments', {})
# assignments = {"agent-1": "1762411564661", ...}
```

### Thread Queries
```python
# Get thread by slug
cursor.execute("SELECT * FROM threads WHERE thread_slug = ?", [thread_slug])

# Get threads for user
cursor.execute("SELECT * FROM threads WHERE user_id = ? ORDER BY updated_at DESC", [user_id])

# Get thread with messages
cursor.execute("""
    SELECT t.*, COUNT(m.id) as message_count 
    FROM threads t 
    LEFT JOIN messages m ON t.id = m.thread_id 
    WHERE t.thread_slug = ?
    GROUP BY t.id
""", [thread_slug])
```

### User Metadata Updates
```python
# Update thread assignments
cursor.execute("SELECT metadata FROM users WHERE id = ?", [user_id])
metadata = json.loads(cursor.fetchone()['metadata'] or '{}')
metadata['thread_assignments'] = {"agent-1": "session_id"}
cursor.execute("UPDATE users SET metadata = ? WHERE id = ?", 
               [json.dumps(metadata), user_id])
```

---

## Key Insights for Code Analysis

1. **Thread assignments are JSON-based**, not a separate table (despite `thread_assignments` table existing)
2. **Thread IDs are timestamp-based strings**, not integers (e.g., "1762411564661")
3. **Location can be**: 'prime', 'agent-1', 'agent-2', 'agent-3', etc.
4. **Metadata columns are JSON strings**, require `json.loads()` to parse
5. **Multiple indexes exist** on frequently queried columns (user_id, thread_slug, session_id)
6. **OAuth tokens** stored in `ai_infrastructure.db`, not `sessions.db`
7. **Two users exist**: ID 1 (admin) and ID 14 (printing)

---

## Files Generated
- **DATABASE_SCHEMAS.json** - Complete machine-readable schema (all details)
- **DATABASE_SCHEMAS.md** - Complete human-readable schema (1697 lines)
- **DATABASE_SCHEMAS_SUMMARY.md** - This quick reference guide

**Last Updated:** 2025-11-08
