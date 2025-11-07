# Database Schema Reference - CORE DOCUMENTATION

**Version:** 1.0.0  
**Last Updated:** January 2025  
**Database:** ai_infrastructure.db (SQLite)

---

## Table of Contents

1. [Overview](#overview)
2. [Users & Authentication](#users--authentication)
3. [Platform Credentials](#platform-credentials)
4. [Workspaces](#workspaces)
5. [Account Linking](#account-linking)
6. [Kanban Sync](#kanban-sync)
7. [Indexes](#indexes)
8. [Relationships](#relationships)
9. [Usage Examples](#usage-examples)

---

## Overview

The AI Agents infrastructure uses SQLite for storing user data, authentication, and platform integrations. This document serves as the **single source of truth** for the database schema.

**Total Tables:** 9 core tables  
**Foreign Keys:** Enabled for referential integrity  
**Indexes:** 6 performance indexes

---

## Users & Authentication

### Table: `users`

Core user accounts table.

**Columns:**
- `id` - INTEGER PRIMARY KEY - Unique user identifier
- `username` - TEXT UNIQUE NOT NULL - Login username
- `email` - TEXT UNIQUE NOT NULL - User email address
- `password_hash` - TEXT - SHA-256 hashed password
- `role` - TEXT DEFAULT 'user' - User role (user/admin/guest)
- `primary_gmail` - TEXT - Primary Gmail address for integrations
- `created_at` - TEXT DEFAULT CURRENT_TIMESTAMP - Account creation time
- `last_active` - TEXT - Last activity timestamp
- `metadata` - TEXT - JSON metadata (preferences, settings)
- `is_primary` - INTEGER DEFAULT 0 - Primary account flag

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    role TEXT DEFAULT 'user',
    primary_gmail TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_active TEXT,
    metadata TEXT,
    is_primary INTEGER DEFAULT 0
)
```

**Usage:**
- Authentication and user management
- Role-based access control
- Activity tracking

---

### Table: `user_sessions`

Session management with token-based authentication.

**Columns:**
- `id` - INTEGER PRIMARY KEY - Session identifier
- `user_id` - INTEGER NOT NULL - References users(id)
- `token` - TEXT UNIQUE NOT NULL - Session token (32-byte URL-safe)
- `created_at` - TEXT DEFAULT CURRENT_TIMESTAMP - Session start
- `expires_at` - TEXT NOT NULL - Expiry timestamp (default 24h)
- `ip_address` - TEXT - Client IP address
- `user_agent` - TEXT - Browser/client info

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
```

**Usage:**
- Secure token-based sessions
- Automatic expiry (default 24 hours)
- Session cleanup and maintenance

---

## Platform Credentials

### Table: `user_platform_credentials`

Stores OAuth tokens for platform integrations.

**Columns:**
- `id` - INTEGER PRIMARY KEY - Credential ID
- `user_id` - INTEGER NOT NULL - References users(id)
- `platform` - TEXT NOT NULL - Platform name (google/microsoft/github)
- `credential_type` - TEXT NOT NULL - Type (oauth/api_key/service_account)
- `access_token` - TEXT - OAuth access token
- `refresh_token` - TEXT - OAuth refresh token
- `token_expiry` - TEXT - Token expiration time
- `credential_data` - TEXT - JSON credential data
- `created_at` - TEXT DEFAULT CURRENT_TIMESTAMP - Creation time
- `updated_at` - TEXT DEFAULT CURRENT_TIMESTAMP - Last update

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS user_platform_credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,
    credential_type TEXT NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    token_expiry TEXT,
    credential_data TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, platform)
)
```

**Usage:**
- Google OAuth credentials
- Microsoft Graph API tokens
- GitHub integration
- Token refresh management

---

### Table: `user_gmail_accounts`

Gmail-specific account credentials.

**Columns:**
- `id` - INTEGER PRIMARY KEY - Account ID
- `user_id` - INTEGER NOT NULL - References users(id)
- `gmail_address` - TEXT UNIQUE NOT NULL - Gmail email address
- `access_token` - TEXT - OAuth access token
- `refresh_token` - TEXT - OAuth refresh token
- `token_expiry` - TEXT - Token expiration
- `is_primary` - INTEGER DEFAULT 0 - Primary Gmail flag
- `created_at` - TEXT DEFAULT CURRENT_TIMESTAMP - Creation time
- `updated_at` - TEXT DEFAULT CURRENT_TIMESTAMP - Last update

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS user_gmail_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    gmail_address TEXT UNIQUE NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    token_expiry TEXT,
    is_primary INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
```

**Usage:**
- Gmail API access
- Multiple Gmail accounts per user
- Primary Gmail designation

---

### Table: `user_email_aliases`

Email aliases for Gmail accounts.

**Columns:**
- `id` - INTEGER PRIMARY KEY - Alias ID
- `gmail_account_id` - INTEGER NOT NULL - References user_gmail_accounts(id)
- `user_id` - INTEGER NOT NULL - References users(id)
- `alias_email` - TEXT UNIQUE NOT NULL - Alias email address
- `is_active` - INTEGER DEFAULT 1 - Active flag
- `created_at` - TEXT DEFAULT CURRENT_TIMESTAMP - Creation time
- `updated_at` - TEXT DEFAULT CURRENT_TIMESTAMP - Last update
- `metadata` - TEXT - JSON metadata

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS user_email_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gmail_account_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    alias_email TEXT UNIQUE NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY (gmail_account_id) REFERENCES user_gmail_accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
```

**Usage:**
- Send-as aliases for Gmail
- Multiple sender identities
- Alias management

---

## Workspaces

### Table: `workspaces`

User workspaces for organization.

**Columns:**
- `id` - INTEGER PRIMARY KEY - Workspace ID
- `user_id` - INTEGER NOT NULL - References users(id)
- `name` - TEXT NOT NULL - Workspace name
- `description` - TEXT - Workspace description
- `created_at` - TEXT DEFAULT CURRENT_TIMESTAMP - Creation time
- `settings` - TEXT - JSON settings

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS workspaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    settings TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
```

**Usage:**
- Organize user work into workspaces
- Workspace-specific settings
- Multi-workspace support

---

## Account Linking

### Table: `user_account_links`

Links between different user accounts.

**Columns:**
- `id` - INTEGER PRIMARY KEY - Link ID
- `master_user_id` - INTEGER NOT NULL - Master account (references users)
- `linked_user_id` - INTEGER NOT NULL - Linked account (references users)
- `link_type` - TEXT NOT NULL - Link type (gmail/microsoft/github)
- `platform_email` - TEXT - Platform email address
- `is_active` - INTEGER DEFAULT 1 - Active flag
- `created_at` - TEXT DEFAULT CURRENT_TIMESTAMP - Creation time
- `last_synced` - TEXT - Last sync timestamp
- `metadata` - TEXT - JSON metadata

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS user_account_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    master_user_id INTEGER NOT NULL,
    linked_user_id INTEGER NOT NULL,
    link_type TEXT NOT NULL,
    platform_email TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_synced TEXT,
    metadata TEXT,
    FOREIGN KEY (master_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (linked_user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(master_user_id, linked_user_id, link_type)
)
```

**Usage:**
- Link multiple platform accounts
- Sync data across accounts
- Account relationship management

---

### Table: `account_link_requests`

Pending account link requests.

**Columns:**
- `id` - INTEGER PRIMARY KEY - Request ID
- `requesting_user_id` - INTEGER NOT NULL - Requester (references users)
- `target_user_id` - INTEGER NOT NULL - Target user (references users)
- `link_type` - TEXT NOT NULL - Link type
- `status` - TEXT DEFAULT 'pending' - Status (pending/approved/rejected)
- `created_at` - TEXT DEFAULT CURRENT_TIMESTAMP - Creation time
- `expires_at` - TEXT - Request expiry
- `metadata` - TEXT - JSON metadata

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS account_link_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requesting_user_id INTEGER NOT NULL,
    target_user_id INTEGER NOT NULL,
    link_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT,
    metadata TEXT,
    FOREIGN KEY (requesting_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (target_user_id) REFERENCES users(id) ON DELETE CASCADE
)
```

**Usage:**
- Request account linking
- Approval workflow
- Link expiry management

---

## Kanban Sync

### Table: `kanban_task_links`

Bidirectional task synchronization between platforms.

**Columns:**
- `id` - INTEGER PRIMARY KEY - Link ID
- `user_id` - INTEGER NOT NULL - References users(id)
- `google_task_id` - TEXT - Google Tasks ID
- `microsoft_task_id` - TEXT - Microsoft To Do ID
- `github_issue_id` - TEXT - GitHub Issue ID
- `task_title` - TEXT - Task title
- `task_description` - TEXT - Task description
- `status` - TEXT - Task status
- `priority` - TEXT - Task priority
- `due_date` - TEXT - Due date
- `created_at` - TEXT DEFAULT CURRENT_TIMESTAMP - Creation time
- `updated_at` - TEXT DEFAULT CURRENT_TIMESTAMP - Last update
- `last_synced_google` - TEXT - Last Google sync
- `last_synced_microsoft` - TEXT - Last Microsoft sync
- `last_synced_github` - TEXT - Last GitHub sync
- `sync_status` - TEXT - Sync status
- `conflict_data` - TEXT - Conflict resolution data
- `labels` - TEXT - Task labels (JSON)
- `metadata` - TEXT - Additional metadata (JSON)

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS kanban_task_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    google_task_id TEXT,
    microsoft_task_id TEXT,
    github_issue_id TEXT,
    task_title TEXT,
    task_description TEXT,
    status TEXT,
    priority TEXT,
    due_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_synced_google TEXT,
    last_synced_microsoft TEXT,
    last_synced_github TEXT,
    sync_status TEXT,
    conflict_data TEXT,
    labels TEXT,
    metadata TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
```

**Usage:**
- Sync tasks across Google, Microsoft, GitHub
- Bidirectional synchronization
- Conflict detection and resolution
- Universal task management

---

## Indexes

Performance indexes for common queries:

```sql
-- User lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Session lookups
CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(token);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);

-- Platform credentials
CREATE INDEX IF NOT EXISTS idx_credentials_user_platform 
    ON user_platform_credentials(user_id, platform);

-- Gmail accounts
CREATE INDEX IF NOT EXISTS idx_gmail_user_id ON user_gmail_accounts(user_id);

-- Kanban sync
CREATE INDEX IF NOT EXISTS idx_kanban_user_id ON kanban_task_links(user_id);
```

---

## Relationships

### Foreign Key Relationships:

```
users (1) ──→ (many) user_sessions
users (1) ──→ (many) user_platform_credentials
users (1) ──→ (many) user_gmail_accounts
users (1) ──→ (many) user_email_aliases
users (1) ──→ (many) workspaces
users (1) ──→ (many) user_account_links (as master)
users (1) ──→ (many) user_account_links (as linked)
users (1) ──→ (many) account_link_requests (as requester)
users (1) ──→ (many) account_link_requests (as target)
users (1) ──→ (many) kanban_task_links

user_gmail_accounts (1) ──→ (many) user_email_aliases
```

### Cascade Deletes:
All foreign keys use `ON DELETE CASCADE`, ensuring:
- Deleting a user removes all their sessions, credentials, and data
- Deleting a Gmail account removes all its aliases
- Referential integrity maintained automatically

---

## Usage Examples

### Create a new user:
```python
from AI_infrastructure.database_toolkit import UserManager

users = UserManager()
user_id = users.create_user(
    username="john_doe",
    email="john@example.com",
    password="secret123",
    role="user"
)
```

### Create a session:
```python
from AI_infrastructure.database_toolkit import SessionManager

sessions = SessionManager()
token = sessions.create_session(user_id=1, expiry_hours=24)
```

### Add platform credentials:
```python
users = UserManager()
users.add_platform_credential(
    user_id=1,
    platform="google",
    credential_type="oauth",
    access_token="ya29...",
    refresh_token="1//...",
    token_expiry="2025-01-15T12:00:00Z"
)
```

### Query with CLI:
```bash
# View schema
python -m AI_infrastructure.database_toolkit.cli schema --view

# List users
python -m AI_infrastructure.database_toolkit.cli users --list

# Run health check
python -m AI_infrastructure.database_toolkit.cli health

# Execute custom query
python -m AI_infrastructure.database_toolkit.cli query "SELECT * FROM users LIMIT 5"
```

---

## Migration Guide

### Creating all tables:
```python
from AI_infrastructure.database_toolkit import SchemaManager

schema = SchemaManager()
schema.create_all_tables()
```

### Checking for missing tables:
```python
missing = schema.check_missing_tables()
if missing:
    print(f"Missing tables: {', '.join(missing)}")
```

### Exporting schema:
```python
schema.export_schema("database_schema.json")
```

---

## Maintenance

### Session cleanup:
```python
from AI_infrastructure.database_toolkit import SessionManager

sessions = SessionManager()
deleted = sessions.cleanup_expired_sessions()
print(f"Cleaned up {deleted} expired sessions")
```

### Database health check:
```python
from AI_infrastructure.database_toolkit import Diagnostics

diag = Diagnostics()
results = diag.run_full_health_check()
```

---

**End of CORE Schema Documentation**

For toolkit usage, see: `AI_infrastructure/database_toolkit/README.md`  
For implementation details, see: `AI_infrastructure/database_toolkit/schema_manager.py`
