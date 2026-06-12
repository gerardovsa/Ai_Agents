# Supabase Database Architecture

**Last Updated:** January 19, 2026  
**Version:** 2.1.0  
**Database:** Supabase PostgreSQL 15+  
**Connection Pooler:** PgBouncer (Transaction Mode, Port 6543)  
**Pool Size:** 3-15 per schema (reduced Jan 18, 2026)  
**Region:** Singapore (ap-southeast-1)  
**Total Schemas:** 4 (ai_infrastructure, sessions, synergy_sessions, public)

> **📘 CONSOLIDATED DOCUMENTATION**  
> This is the **master database documentation** consolidating schema architecture, connection pooling, migration patterns, and troubleshooting. Supersedes 40+ scattered database files.

---

## 🎯 Quick Reference

### Environment Detection

```python
# Production (Supabase PostgreSQL)
USE_SUPABASE=true
SUPABASE_DB_URL=postgresql://postgres:password@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
POOL_ENABLED=true

# Local Development (SQLite - DEPRECATED)
USE_SUPABASE=false
DATABASE_PATH=data/ai_infrastructure.db
```

### Connection Methods

```python
from AI_infrastructure.shared.database_utils import (
    get_ai_infrastructure_connection,
    get_sessions_connection,
    get_synergy_sessions_connection,
    execute_query
)

# Method 1: Context Manager (Recommended)
with get_sessions_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM threads WHERE user_id=%s", (user_id,))
    threads = cursor.fetchall()

# Method 2: execute_query Helper (Simplest)
threads = execute_query(
    "SELECT * FROM sessions.threads WHERE user_id=%s",
    (user_id,),
    fetch_mode='all'
)

# Method 3: Manual (Legacy - Avoid)
conn = get_sessions_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM threads")
results = cursor.fetchall()
conn.close()  # ⚠️ Must remember to close!
```

---

## 🗄️ Schema Architecture

### Four-Schema System

The platform uses **schema isolation** to separate concerns and prevent naming conflicts:

```
┌─────────────────────────────────────────────────────────────┐
│                    Supabase PostgreSQL                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  📁 ai_infrastructure (19 tables)                            │
│     └── Users, Auth, OAuth, Credentials, Preferences         │
│                                                               │
│  📁 sessions (9 tables)                                       │
│     └── Threads, Messages, Thread Assignments                │
│                                                               │
│  📁 synergy_sessions (2 tables)                              │
│     └── Kanban Cards, Internal Docs                          │
│                                                               │
│  📁 public (7 tables)                                         │
│     └── Visual Automations, Workflows, Schedules             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Schema 1: ai_infrastructure (19 Tables)

**Purpose:** User management, authentication, OAuth, platform credentials, automation

### Core Tables

#### `users` - User Accounts
```sql
CREATE TABLE ai_infrastructure.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

**Usage:** Authentication, user identification across all features

---

#### `user_sessions` - Active Login Sessions
```sql
CREATE TABLE ai_infrastructure.user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    device_info JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Usage:** JWT token validation, multi-device session management

---

#### `oauth_tokens` - OAuth Access/Refresh Tokens
```sql
CREATE TABLE ai_infrastructure.oauth_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- 'google', 'microsoft'
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_type VARCHAR(50),
    expires_at TIMESTAMP,
    scope TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, platform)
);
```

**Platforms:**
- `google` - Gmail, Drive, Calendar, Docs, Sheets
- `microsoft` - Outlook, OneDrive, Word, Excel

**Token Refresh:** Automatic via APScheduler (every 55 minutes)

---

#### `user_platform_credentials` - API Credentials Storage
```sql
CREATE TABLE ai_infrastructure.user_platform_credentials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(100) NOT NULL, -- 'xero', 'shopify', 'inhouse_print'
    connection_string TEXT, -- For database connections
    client_id VARCHAR(255),
    client_secret VARCHAR(255),
    api_key TEXT,
    metadata JSONB, -- Additional platform-specific config
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, platform)
);
```

**Platforms:**
- `xero` - Accounting integration
- `shopify` - E-commerce
- `inhouse_print` - Fred SQL Server database
- `stripe` - Payment processing
- `salesforce` - CRM integration

**Security:** Credentials auto-injected into tools by registry (never exposed to AI)

---

#### `user_preferences` - User Personalization
```sql
CREATE TABLE ai_infrastructure.user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    theme VARCHAR(50) DEFAULT 'light', -- 'light', 'dark', 'high-contrast'
    default_ai_model VARCHAR(50) DEFAULT 'claude-3-5-sonnet',
    agent_slug VARCHAR(50), -- Default agent location
    sidebar_collapsed BOOLEAN DEFAULT false,
    auto_save BOOLEAN DEFAULT true,
    preferences JSONB, -- Additional settings
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Usage:** Store user UI preferences, restore on login

---

#### `prompt_library` - Saved Prompts
```sql
CREATE TABLE ai_infrastructure.prompt_library (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    is_public BOOLEAN DEFAULT false,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Usage:** Quick prompts, templates, reusable instructions

---

#### `device_registry` - Multi-Device Management
```sql
CREATE TABLE ai_infrastructure.device_registry (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    device_name VARCHAR(255),
    browser_info JSONB,
    locked_threads TEXT[], -- Array of thread_slugs locked by this device
    last_seen TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Usage:** Prevent concurrent edits, track active devices

---

#### `workspaces` - Team Workspaces
```sql
CREATE TABLE ai_infrastructure.workspaces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    description TEXT,
    settings JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Usage:** Multi-user team collaboration (future feature)

---

#### `workspace_users` - Team Membership
```sql
CREATE TABLE ai_infrastructure.workspace_users (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member', -- 'owner', 'admin', 'member', 'viewer'
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);
```

---

#### `automation_executions` - Automation Run History
```sql
CREATE TABLE ai_infrastructure.automation_executions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    automation_id INTEGER,
    status VARCHAR(50), -- 'running', 'completed', 'failed'
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    output JSONB,
    error_message TEXT
);
```

**Usage:** Track workflow executions, debug failures

---

### Additional Tables

| Table | Purpose |
|-------|---------|
| `account_link_requests` | Account linking tokens |
| `thread_lock_history` | Device lock audit log |
| `user_account_links` | Account linking relationships |
| `user_gmail_accounts` | Gmail account storage |
| `user_prompt_preferences` | Prompt preferences |
| `workspace_invitations` | Workspace invite tokens |
| `scheduled_tasks` | AI automation scheduler |
| `thread_assignments` | Thread location tracking (migrated to sessions schema) |

---

## 📊 Schema 2: sessions (9 Tables)

**Purpose:** Thread management, messages, conversation storage

### Core Tables

#### `threads` - Conversation Threads
```sql
CREATE TABLE sessions.threads (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL, -- URL-safe identifier
    title VARCHAR(500),
    user_id INTEGER NOT NULL, -- FK to ai_infrastructure.users(id)
    agent VARCHAR(50), -- 'prime', 'agent-1', 'agent-2', etc.
    ai_model VARCHAR(50) DEFAULT 'claude-3-5-sonnet',
    system_prompt TEXT,
    synergy_card_id INTEGER, -- Soft FK to synergy_sessions.synergy_sessions(id)
    workflow_slug VARCHAR(100), -- Soft FK to public.visual_automations(slug)
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_threads_user_id ON sessions.threads(user_id);
CREATE INDEX idx_threads_slug ON sessions.threads(slug);
CREATE INDEX idx_threads_agent ON sessions.threads(agent);
```

**Key Fields:**
- `slug` - Unique thread identifier (e.g., `th_a3f8b2c1_1733049600`)
- `agent` - Location: `prime`, `agent-1` through `agent-26` (Alpha → Zulu)
- `synergy_card_id` - Link to Kanban card (bidirectional)
- `workflow_slug` - Link to automation workflow
- `tags` - Categorization for filtering

---

#### `messages` - Chat Messages
```sql
CREATE TABLE sessions.messages (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER REFERENCES threads(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    tool_results JSONB, -- Tool execution results
    thinking_content TEXT, -- Claude extended thinking
    token_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_thread_id ON sessions.messages(thread_id);
CREATE INDEX idx_messages_created_at ON sessions.messages(created_at);
```

**Message Types:**
- `user` - User input
- `assistant` - AI response
- `system` - System notifications

**Tool Results Structure:**
```json
{
  "tool_use_id": "toolu_123",
  "tool_name": "xero_get_invoices",
  "tool_input": {"status": "PAID"},
  "tool_result": {"success": true, "data": [...]}
}
```

---

#### `thread_assignments` - Thread Locations
```sql
CREATE TABLE sessions.thread_assignments (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER REFERENCES threads(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,
    location VARCHAR(50) NOT NULL, -- 'prime', 'agent-1', 'agent-2', etc.
    email_thread_id VARCHAR(255), -- For communication hub threads
    email_subject TEXT,
    email_participants JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(thread_id, user_id)
);

CREATE INDEX idx_thread_assignments_user_id ON sessions.thread_assignments(user_id);
CREATE INDEX idx_thread_assignments_location ON sessions.thread_assignments(location);
```

**Usage:** Track where threads are displayed (Prime vs Agent columns)

---

#### `thread_shares` - Thread Sharing Permissions
```sql
CREATE TABLE sessions.thread_shares (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER REFERENCES threads(id) ON DELETE CASCADE,
    shared_by_user_id INTEGER NOT NULL,
    shared_with_user_id INTEGER NOT NULL,
    permission VARCHAR(50) DEFAULT 'view', -- 'view', 'edit'
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(thread_id, shared_with_user_id)
);
```

**Usage:** Multi-user thread collaboration (future feature)

---

### Additional Tables

| Table | Purpose |
|-------|---------|
| `api_sessions` | API session tracking |
| `saved_threads` | Archived thread backups |
| `sessions` | UI context sessions |
| `thread_users` | Thread access control |
| `user_sessions` | User session tokens (duplicate of ai_infrastructure?) |

---

## 📊 Schema 3: synergy_sessions (2 Tables)

**Purpose:** Synergy Kanban board for project management

#### `synergy_sessions` - Kanban Cards
```sql
CREATE TABLE synergy_sessions.synergy_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    priority VARCHAR(20), -- 'low', 'medium', 'high', 'urgent'
    milestone VARCHAR(100),
    status VARCHAR(50) DEFAULT 'backlog', -- 'backlog', 'in-progress', 'completed'
    tags TEXT[],
    linked_thread_ids INTEGER[], -- Bidirectional link to sessions.threads
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_synergy_user_id ON synergy_sessions.synergy_sessions(user_id);
CREATE INDEX idx_synergy_status ON synergy_sessions.synergy_sessions(status);
CREATE INDEX idx_synergy_priority ON synergy_sessions.synergy_sessions(priority);
```

**Bidirectional Linking:**
- Thread → Synergy: `sessions.threads.synergy_card_id`
- Synergy → Threads: `synergy_sessions.synergy_sessions.linked_thread_ids[]`

---

#### `synergy_internal_docs` - Rich-Text Documents
```sql
CREATE TABLE synergy_sessions.synergy_internal_docs (
    id SERIAL PRIMARY KEY,
    card_id INTEGER REFERENCES synergy_sessions(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    format VARCHAR(50) DEFAULT 'markdown', -- 'markdown', 'html'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Usage:** Attach detailed documentation to Kanban cards

---

## 📊 Schema 4: public (7 Tables)

**Purpose:** Visual automation workflows

#### `visual_automations` - Canvas Workflows
```sql
CREATE TABLE public.visual_automations (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL,
    definition JSONB NOT NULL, -- Node graph, connections, configs
    description TEXT,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Definition Structure:**
```json
{
  "nodes": [
    {"id": "node1", "type": "trigger", "config": {...}},
    {"id": "node2", "type": "ai_agent", "config": {...}}
  ],
  "connections": [
    {"from": "node1", "to": "node2"}
  ]
}
```

---

#### `workflow_executions` - Workflow Runs
```sql
CREATE TABLE public.workflow_executions (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES visual_automations(id) ON DELETE CASCADE,
    status VARCHAR(50), -- 'running', 'completed', 'failed'
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    output JSONB,
    error_message TEXT
);
```

---

#### `workflow_schedules` - Cron Schedules
```sql
CREATE TABLE public.workflow_schedules (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES visual_automations(id) ON DELETE CASCADE,
    cron_expression VARCHAR(100) NOT NULL, -- '0 9 * * *' = Daily at 9am
    timezone VARCHAR(50) DEFAULT 'Australia/Sydney',
    is_active BOOLEAN DEFAULT true,
    last_run TIMESTAMP,
    next_run TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### Additional Tables

| Table | Purpose |
|-------|---------|
| `automation_workflows` | Legacy workflow definitions |
| `workflow_node_library` | Custom node library |
| `workflow_templates` | Workflow templates |
| `automation_executions` | Execution history (duplicate?) |

---

## 🔌 Connection Pooling Architecture

### PgBouncer Configuration

```python
# Supabase PgBouncer Settings
POOL_MODE = 'transaction'  # Best for Flask/serverless
MAX_CLIENT_CONN = 20       # Max concurrent Flask connections
DEFAULT_POOL_SIZE = 5      # Connections per database
RESERVE_POOL_SIZE = 2      # Emergency connections
```

**Connection String:**
```bash
postgresql://postgres:password@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
#                                                                        ^^^^
#                                                                        Port 6543 = Transaction mode
```

**Port Differences:**
- **Port 5432** - Direct connection (no pooling)
- **Port 6543** - PgBouncer transaction mode (recommended)

---

### Pool Management

**Implementation:** `AI_infrastructure/shared/database_utils.py`

```python
import psycopg2
from psycopg2 import pool

# Initialize connection pools (one per schema)
ai_infrastructure_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=4,
    maxconn=12,
    host="aws-0-ap-southeast-1.pooler.supabase.com",
    port=6543,
    database="postgres",
    user="postgres",
    password=os.getenv('SUPABASE_DB_PASSWORD'),
    options="-c search_path=ai_infrastructure,public"
)

sessions_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=4,
    maxconn=12,
    # ... same config, different search_path
    options="-c search_path=sessions,public"
)

synergy_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=4,
    maxconn=12,
    # ... same config, different search_path
    options="-c search_path=synergy_sessions,public"
)
```

**Benefits:**
- **Fast:** Reuse connections (100x faster than creating new)
- **Thread-safe:** Handles concurrent Flask requests
- **Leak detection:** Automatic monitoring
- **Auto-return:** Connections return to pool on close

---

### Schema Isolation Pattern

```python
def get_ai_infrastructure_connection():
    """Get connection with ai_infrastructure schema in search path."""
    conn = ai_infrastructure_pool.getconn()
    conn.cursor_factory = psycopg2.extras.RealDictCursor
    return conn

def get_sessions_connection():
    """Get connection with sessions schema in search path."""
    conn = sessions_pool.getconn()
    conn.cursor_factory = psycopg2.extras.RealDictCursor
    return conn

def get_synergy_sessions_connection():
    """Get connection with synergy_sessions schema in search path."""
    conn = synergy_pool.getconn()
    conn.cursor_factory = psycopg2.extras.RealDictCursor
    return conn
```

**Search Path Behavior:**
```sql
-- With search_path=sessions,public
SELECT * FROM threads;  -- Resolves to sessions.threads
SELECT * FROM users;    -- ERROR: No users table in sessions schema

-- Must use fully qualified name
SELECT * FROM ai_infrastructure.users;  -- ✅ Works
```

---

## 🛠️ Database Utilities

### execute_query() - Universal Interface

**File:** `AI_infrastructure/shared/database_utils.py`

```python
def execute_query(query, params=(), fetch_mode='all', schema='sessions'):
    """
    Execute SQL query with automatic connection management.
    
    Args:
        query (str): SQL query with %s placeholders
        params (tuple): Parameter values
        fetch_mode (str): 'all', 'one', 'value', or None (for INSERT/UPDATE)
        schema (str): 'sessions', 'ai_infrastructure', 'synergy_sessions'
    
    Returns:
        list|dict|value|None: Query results based on fetch_mode
    """
    # Get connection for specified schema
    if schema == 'ai_infrastructure':
        conn = get_ai_infrastructure_connection()
    elif schema == 'synergy_sessions':
        conn = get_synergy_sessions_connection()
    else:
        conn = get_sessions_connection()
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if fetch_mode == 'all':
            result = cursor.fetchall()
        elif fetch_mode == 'one':
            result = cursor.fetchone()
        elif fetch_mode == 'value':
            row = cursor.fetchone()
            result = row[0] if row else None
        else:
            conn.commit()
            result = None
        
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()  # Returns to pool
```

**Usage Examples:**

```python
# Fetch all rows
threads = execute_query(
    "SELECT * FROM threads WHERE user_id=%s",
    (user_id,),
    fetch_mode='all'
)

# Fetch single row
user = execute_query(
    "SELECT * FROM ai_infrastructure.users WHERE id=%s",
    (user_id,),
    fetch_mode='one',
    schema='ai_infrastructure'
)

# Fetch single value
count = execute_query(
    "SELECT COUNT(*) FROM messages WHERE thread_id=%s",
    (thread_id,),
    fetch_mode='value'
)

# Insert/Update (no fetch)
execute_query(
    "INSERT INTO threads (slug, title, user_id) VALUES (%s, %s, %s)",
    (slug, title, user_id)
)
```

---

## 🔄 Migration Patterns

### Migration File Structure

**Location:** `AI_infrastructure/migrations/`

**Naming Convention:**
```
001_initial_schema.sql
002_add_oauth_tokens.sql
003_add_thread_assignments.sql
...
025_add_workspace_features.sql
```

### Idempotent Migration Pattern

**All migrations must be idempotent** (safe to run multiple times):

```sql
-- ✅ CORRECT: Idempotent migration
CREATE TABLE IF NOT EXISTS sessions.threads (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add column only if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema='sessions' 
        AND table_name='threads' 
        AND column_name='synergy_card_id'
    ) THEN
        ALTER TABLE sessions.threads ADD COLUMN synergy_card_id INTEGER;
    END IF;
END $$;

-- ❌ WRONG: Not idempotent
CREATE TABLE sessions.threads (...);  -- Fails if table exists
ALTER TABLE sessions.threads ADD COLUMN synergy_card_id INTEGER;  -- Fails if column exists
```

### Running Migrations

**Method 1: Manual (Supabase Dashboard)**
```sql
-- Copy migration SQL
-- Go to: Supabase Dashboard → SQL Editor
-- Paste and execute
```

**Method 2: Python Script**
```python
# AI_infrastructure/migrations/run_migration.py
from AI_infrastructure.shared.database_utils import execute_query

with open('025_add_workspace_features.sql', 'r') as f:
    migration_sql = f.read()

execute_query(migration_sql, schema='ai_infrastructure')
print("Migration complete!")
```

**Method 3: Automated (CI/CD)**
```yaml
# .github/workflows/deploy.yml
- name: Run Migrations
  run: |
    python AI_infrastructure/migrations/run_all_migrations.py
```

---

## 🔍 Common Queries

### User Management

```python
# Get user by email
user = execute_query(
    "SELECT * FROM ai_infrastructure.users WHERE email=%s",
    (email,),
    fetch_mode='one',
    schema='ai_infrastructure'
)

# Get user's OAuth tokens
tokens = execute_query(
    """
    SELECT platform, access_token, expires_at
    FROM ai_infrastructure.oauth_tokens
    WHERE user_id=%s AND expires_at > NOW()
    """,
    (user_id,),
    fetch_mode='all',
    schema='ai_infrastructure'
)

# Get user's platform credentials
credentials = execute_query(
    """
    SELECT platform, connection_string, client_id, metadata
    FROM ai_infrastructure.user_platform_credentials
    WHERE user_id=%s
    """,
    (user_id,),
    fetch_mode='all',
    schema='ai_infrastructure'
)
```

### Thread Management

```python
# Get all threads for user
threads = execute_query(
    """
    SELECT t.*, 
           (SELECT COUNT(*) FROM messages WHERE thread_id=t.id) as message_count
    FROM sessions.threads t
    WHERE t.user_id=%s
    ORDER BY t.updated_at DESC
    """,
    (user_id,),
    fetch_mode='all'
)

# Get thread with messages
thread_data = execute_query(
    """
    SELECT 
        t.*,
        json_agg(m ORDER BY m.created_at) as messages
    FROM sessions.threads t
    LEFT JOIN sessions.messages m ON m.thread_id=t.id
    WHERE t.slug=%s
    GROUP BY t.id
    """,
    (thread_slug,),
    fetch_mode='one'
)

# Get threads in specific agent column
agent_threads = execute_query(
    """
    SELECT t.*
    FROM sessions.threads t
    JOIN sessions.thread_assignments ta ON ta.thread_id=t.id
    WHERE ta.user_id=%s AND ta.location=%s
    """,
    (user_id, 'agent-3'),
    fetch_mode='all'
)
```

### Synergy Dashboard

```python
# Get Kanban cards with linked threads
cards = execute_query(
    """
    SELECT 
        s.*,
        (SELECT json_agg(t) 
         FROM sessions.threads t 
         WHERE t.id = ANY(s.linked_thread_ids)) as linked_threads
    FROM synergy_sessions.synergy_sessions s
    WHERE s.user_id=%s
    ORDER BY 
        CASE s.priority
            WHEN 'urgent' THEN 1
            WHEN 'high' THEN 2
            WHEN 'medium' THEN 3
            WHEN 'low' THEN 4
        END,
        s.created_at DESC
    """,
    (user_id,),
    fetch_mode='all',
    schema='synergy_sessions'
)

# Get card with internal docs
card = execute_query(
    """
    SELECT 
        s.*,
        d.content as doc_content
    FROM synergy_sessions.synergy_sessions s
    LEFT JOIN synergy_sessions.synergy_internal_docs d ON d.card_id=s.id
    WHERE s.id=%s
    """,
    (card_id,),
    fetch_mode='one',
    schema='synergy_sessions'
)
```

### Automation Workflows

```python
# Get active workflows
workflows = execute_query(
    """
    SELECT 
        va.*,
        ws.cron_expression,
        ws.next_run
    FROM public.visual_automations va
    LEFT JOIN public.workflow_schedules ws ON ws.workflow_id=va.id
    WHERE va.user_id=%s AND va.is_active=true
    """,
    (user_id,),
    fetch_mode='all',
    schema='public'
)

# Get workflow execution history
executions = execute_query(
    """
    SELECT *
    FROM public.workflow_executions
    WHERE workflow_id=%s
    ORDER BY started_at DESC
    LIMIT 50
    """,
    (workflow_id,),
    fetch_mode='all',
    schema='public'
)
```

---

## 🐛 Troubleshooting

### Issue: "relation does not exist"

**Symptom:**
```
psycopg2.errors.UndefinedTable: relation "threads" does not exist
```

**Cause:** Missing schema prefix or wrong search_path

**Solutions:**

```python
# Solution 1: Use fully qualified table name
execute_query("SELECT * FROM sessions.threads WHERE id=%s", (id,))

# Solution 2: Use correct connection function
conn = get_sessions_connection()  # Sets search_path=sessions,public
cursor = conn.cursor()
cursor.execute("SELECT * FROM threads WHERE id=%s", (id,))  # Now works
```

---

### Issue: Connection pool exhausted

**Symptom:**
```
PoolError: connection pool exhausted
```

**Cause:** Connections not being returned to pool

**Diagnosis:**
```python
from AI_infrastructure.shared.database_utils import log_pool_usage

log_pool_usage()
# Shows: ai_infrastructure pool: 12/12 connections in use, 5 waiting
```

**Solutions:**

```python
# ❌ WRONG: Forgot to close connection
def get_user(user_id):
    conn = get_ai_infrastructure_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    return cursor.fetchone()
    # conn never closed - LEAK!

# ✅ CORRECT: Use context manager
def get_user(user_id):
    with get_ai_infrastructure_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        return cursor.fetchone()
    # conn automatically returned to pool

# ✅ CORRECT: Manual close
def get_user(user_id):
    conn = get_ai_infrastructure_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        return cursor.fetchone()
    finally:
        conn.close()  # Always returns to pool
```

**Emergency Fix:**
```python
# Restart Flask server to reset pools
# Or increase pool size in database_utils.py:
ai_infrastructure_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=4,
    maxconn=20  # Increased from 12
)
```

---

### Issue: Cursor not RealDictCursor

**Symptom:**
```python
user = cursor.fetchone()
print(user['email'])  # TypeError: tuple indices must be integers
```

**Cause:** Connection created without RealDictCursor factory

**Solution:**
```python
# ❌ WRONG: No cursor factory
conn = ai_infrastructure_pool.getconn()

# ✅ CORRECT: Set cursor factory
conn = ai_infrastructure_pool.getconn()
conn.cursor_factory = psycopg2.extras.RealDictCursor

# ✅ BEST: Use connection function (does this automatically)
conn = get_ai_infrastructure_connection()
```

---

### Issue: Schema isolation broken

**Symptom:**
```python
# In sessions schema connection
cursor.execute("SELECT * FROM users")
# psycopg2.errors.UndefinedTable: relation "users" does not exist
```

**Cause:** `users` table is in `ai_infrastructure` schema, not `sessions`

**Solutions:**

```python
# Solution 1: Use fully qualified name
cursor.execute("SELECT * FROM ai_infrastructure.users WHERE id=%s", (id,))

# Solution 2: Use correct connection
conn = get_ai_infrastructure_connection()  # Not sessions connection
cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE id=%s", (id,))
```

---

### Issue: Migration not idempotent

**Symptom:**
```sql
CREATE TABLE sessions.threads (...);
-- ERROR: relation "threads" already exists
```

**Cause:** Migration ran twice without IF NOT EXISTS

**Solution:**
```sql
-- ✅ Make migration idempotent
CREATE TABLE IF NOT EXISTS sessions.threads (...);

-- For ALTER TABLE:
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='threads' AND column_name='new_column') THEN
        ALTER TABLE sessions.threads ADD COLUMN new_column TEXT;
    END IF;
END $$;
```

---

## 📈 Performance Optimization

### Indexing Strategy

```sql
-- Thread lookup by user
CREATE INDEX idx_threads_user_id ON sessions.threads(user_id);

-- Thread lookup by slug (unique identifier)
CREATE INDEX idx_threads_slug ON sessions.threads(slug);

-- Messages by thread (most common query)
CREATE INDEX idx_messages_thread_id ON sessions.messages(thread_id);

-- Recent messages
CREATE INDEX idx_messages_created_at ON sessions.messages(created_at DESC);

-- Thread assignments by user and location
CREATE INDEX idx_thread_assignments_user_id ON sessions.thread_assignments(user_id);
CREATE INDEX idx_thread_assignments_location ON sessions.thread_assignments(location);

-- Synergy cards by user and status
CREATE INDEX idx_synergy_user_id ON synergy_sessions.synergy_sessions(user_id);
CREATE INDEX idx_synergy_status ON synergy_sessions.synergy_sessions(status);
```

**Impact:**
- Thread lookup: 500ms → 5ms (100x faster)
- Message fetch: 800ms → 15ms (53x faster)
- User threads: 1.2s → 10ms (120x faster)

---

### Query Optimization

**Avoid N+1 Queries:**

```python
# ❌ BAD: N+1 queries (1 + N)
threads = execute_query("SELECT * FROM threads WHERE user_id=%s", (user_id,))
for thread in threads:
    messages = execute_query("SELECT * FROM messages WHERE thread_id=%s", (thread['id'],))
    thread['messages'] = messages
# Total queries: 1 + len(threads)

# ✅ GOOD: Single query with JOIN
threads_with_messages = execute_query("""
    SELECT 
        t.*,
        json_agg(m ORDER BY m.created_at) as messages
    FROM sessions.threads t
    LEFT JOIN sessions.messages m ON m.thread_id=t.id
    WHERE t.user_id=%s
    GROUP BY t.id
""", (user_id,))
# Total queries: 1
```

---

### Connection Pool Size Reduction (January 18, 2026)

**Problem:** Connection pool exhaustion on Render deployment with 4 schemas × 30 connections = 120 total

**Root Cause:** Supabase free tier limits connections, excessive pool sizes caused failures

**Solution:** Reduced pool sizes to prevent exhaustion:

```python
# File: AI_infrastructure/shared/database_utils.py, Line ~80
# BEFORE (BROKEN):
POOL_CONFIG = {
    'minconn': 5,
    'maxconn': 30  # ❌ 4 schemas × 30 = 120 connections
}

# AFTER (FIXED):
POOL_CONFIG = {
    'minconn': 3,   # ✅ Conservative minimum
    'maxconn': 15   # ✅ 4 schemas × 15 = 60 total (safe)
}
```

**Pool Sizes by Schema:**
- `ai_infrastructure`: 3-15 connections
- `sessions`: 3-15 connections  
- `synergy_sessions`: 3-15 connections
- `public`: 3-15 connections
- **Total:** 12-60 connections (was 20-120)

**Impact:**
- Eliminated 502 Bad Gateway errors
- Improved connection reuse (less overhead)
- More stable production deployment
- Better resource utilization

**Files Modified:**
- `AI_infrastructure/shared/database_utils.py` (Line ~80)

**Status:** ✅ COMPLETE (Jan 18, 2026)

---

### Connection Pooling Best Practices

```python
# ✅ DO: Use context managers
with get_sessions_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM threads")
    threads = cursor.fetchall()

# ✅ DO: Use execute_query() for simple queries
threads = execute_query("SELECT * FROM threads WHERE user_id=%s", (user_id,))

# ❌ DON'T: Create direct connections
conn = psycopg2.connect(...)  # Bypasses pool - SLOW!

# ❌ DON'T: Forget to close connections
conn = get_sessions_connection()
cursor = conn.cursor()
# ... do work ...
# conn never closed - LEAK!
```

---

## 🔐 Security Best Practices

### SQL Injection Prevention

```python
# ❌ DANGEROUS: String interpolation
user_id = request.args.get('user_id')
query = f"SELECT * FROM users WHERE id={user_id}"  # SQL INJECTION RISK!
execute_query(query)

# ✅ SAFE: Parameterized queries
user_id = request.args.get('user_id')
execute_query("SELECT * FROM users WHERE id=%s", (user_id,))
```

**Rule:** Always use `%s` placeholders and pass parameters as tuple

---

### Credential Security

```python
# ✅ CORRECT: Credentials stored encrypted in database
credentials = execute_query(
    "SELECT * FROM ai_infrastructure.user_platform_credentials WHERE user_id=%s",
    (user_id,),
    schema='ai_infrastructure'
)

# ✅ CORRECT: Credentials auto-injected by tool registry (never exposed to AI)
@tool_executor()
def xero_get_invoices(status: str, **kwargs):
    user_id = kwargs.get('_user_id')
    credentials = kwargs.get('_injected_credentials')  # Auto-injected
    # Use credentials to call API
```

---

### Row-Level Security (Future)

```sql
-- Enable RLS on threads table
ALTER TABLE sessions.threads ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own threads
CREATE POLICY user_threads_policy ON sessions.threads
    FOR SELECT
    USING (user_id = current_setting('app.current_user_id')::INTEGER);

-- Policy: Users can only insert their own threads
CREATE POLICY user_threads_insert_policy ON sessions.threads
    FOR INSERT
    WITH CHECK (user_id = current_setting('app.current_user_id')::INTEGER);
```

**Status:** Not yet implemented (planned for Q2 2026)

---

## 📚 Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Overall system architecture
- [MODULES.md](MODULES.md) - Plugin system architecture
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment procedures
- `.github/copilot-instructions.md` - Development guidelines
- `AI_infrastructure/migrations/` - Migration SQL files

---

## 🎓 Learning Resources

### Key Files to Study

1. **`AI_infrastructure/shared/database_utils.py`** (1,130 lines)
   - Connection pooling implementation
   - execute_query() universal interface
   - Schema management functions

2. **`AI_infrastructure/migrations/`** (25+ files)
   - Migration patterns and best practices
   - Table creation examples
   - Index optimization

3. **`AI_infrastructure/routes/*_routes.py`** (70+ files)
   - Real-world database query examples
   - Error handling patterns
   - Transaction management

### Common Patterns

**Pattern 1: Simple Query**
```python
from AI_infrastructure.shared.database_utils import execute_query

users = execute_query(
    "SELECT * FROM ai_infrastructure.users WHERE role=%s",
    ('admin',),
    fetch_mode='all',
    schema='ai_infrastructure'
)
```

**Pattern 2: Insert with Return**
```python
thread_id = execute_query(
    "INSERT INTO sessions.threads (slug, title, user_id) VALUES (%s, %s, %s) RETURNING id",
    (slug, title, user_id),
    fetch_mode='value'
)
```

**Pattern 3: Transaction**
```python
with get_sessions_connection() as conn:
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO threads (...) VALUES (...)")
        thread_id = cursor.fetchone()['id']
        
        cursor.execute("INSERT INTO messages (...) VALUES (...)", (thread_id, ...))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
```

---

## 📊 Database Statistics (Production)

**Last Updated:** January 18, 2026

| Metric | Value |
|--------|-------|
| **Total Tables** | 37 |
| **Total Schemas** | 4 |
| **Database Size** | ~150 MB |
| **Active Connections** | 8-15 (of 60 max) |
| **Query Performance** | Avg 15ms |
| **Connection Pool Usage** | 40-60% |
| **Backup Frequency** | Daily (Supabase automatic) |

---

## 🗓️ Maintenance Schedule

### Daily
- ✅ Automatic Supabase backups (retained 7 days)
- ✅ Connection pool monitoring (APScheduler)

### Weekly
- Check slow query log (Supabase Dashboard → Performance)
- Review connection pool usage (`log_pool_usage()`)
- Verify index usage

### Monthly
- Database size check
- Vacuum analyze (Supabase handles automatically)
- Review and archive old threads (>6 months)

### Quarterly
- Schema review and optimization
- Migration consolidation
- Index optimization review

---

**Last Updated:** January 18, 2026  
**Document Version:** 1.0  
**Maintained By:** Valor Studio AI Development Team

---

## 📋 Files Consolidated

This document consolidates the following 40+ database documentation files:

- COMPLETE_DATABASE_ARCHITECTURE.md
- CONNECTION_TRACE_SUMMARY_DEC14.md
- DATABASE_ARCHITECTURE_DEC4_2025.md
- SUPABASE_CONNECTION_VERIFICATION_DEC14.md
- SUPABASE_SCHEMA_FIX_COMPLETE.md
- SUPABASE_QUICK_REFERENCE.md
- DATABASE_CONNECTIONS_UPDATE_COMPLETE.md
- DATABASE_CONNECTION_AUDIT.md
- DATABASE_CONNECTION_STATUS.md
- FIX_SUPABASE_CONNECTION.md
- RENDER_SUPABASE_CONNECTION_FIX.md
- SUPABASE_CREDENTIALS_COMPLETE.md
- SUPABASE_SINGLE_SOURCE_TRUTH_ARCHITECTURE.md
- DATABASE_CURSOR_MANAGEMENT.md
- DATABASE_FIX_COMPLETE_SUMMARY.md
- SUPABASE_REALTIME_SETUP_COMPLETE.md
- SUPABASE_TOOLS_COMPLETE.md
- DATA_MIGRATION_COMPLETE.md
- [And 22+ more database-related files]
