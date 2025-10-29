# 🎯 Unified Task Management System - Database Design & Integration

**Date:** October 28, 2025  
**Status:** ✅ Architecture Design Complete  
**Goal:** Integrate Kanban Board with Google Tasks & Microsoft 365 To Do

---

## 📊 Executive Summary

This document outlines the database architecture and integration strategy to enable the Synergy Dashboard Kanban board to **bidirectionally sync** with both:
- **Google Tasks** (existing integration)
- **Microsoft 365 To Do** (new integration)

This creates a **unified task management hub** where users can:
1. Manage tasks from both platforms in one Kanban board
2. Sync task status changes bidirectionally
3. Track agents working on tasks from either platform
4. Maintain data consistency across all three systems

---

## 🏗️ Current Architecture Analysis

### **Existing Systems**

#### **1. Synergy Dashboard (Kanban Board)**
- **Database:** `synergy_sessions.db`
- **Table:** `sessions`
- **Storage:** SQLite with JSON fields
- **Sync:** Google Tasks/Calendar via service account
- **UI:** 4-column Kanban (Backlog → In Progress → Review → Done)

#### **2. Google Tasks Integration**
- **Tools:** 12 operations (create, list, update, complete, delete, etc.)
- **Smart Features:** Bulk operations, project creation, priority organization
- **Authentication:** OAuth 2.0 with refresh tokens
- **API:** Google Tasks API v1

#### **3. Microsoft 365 To Do Integration**
- **Tools:** 11 operations (create, list, update, complete, delete, etc.)
- **Planner Support:** Team task management with buckets
- **Authentication:** OAuth 2.0 (Azure AD)
- **API:** Microsoft Graph API

---

## 🗄️ Enhanced Database Schema

### **Primary Table: `sessions` (Current)**

```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    project_name TEXT,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'active',
    kanban_column TEXT DEFAULT 'backlog',
    due_date TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    assignees TEXT,                    -- JSON array
    tags TEXT,                         -- JSON array
    notes TEXT,
    documents TEXT,                    -- JSON array
    links TEXT,                        -- JSON array
    next_steps TEXT,                   -- JSON array
    checklist TEXT,                    -- JSON array
    google_task_id TEXT,               -- ✅ EXISTS
    google_calendar_event_id TEXT,    -- ✅ EXISTS
    session_data TEXT                  -- JSON object (flexible)
);
```

### **🆕 NEW TABLE: `task_sync_metadata`**

Store bidirectional sync information for all external task systems:

```sql
CREATE TABLE task_sync_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,                    -- Links to sessions.session_id
    
    -- Platform Identification
    platform TEXT NOT NULL,                       -- 'google_tasks', 'microsoft_todo', 'microsoft_planner'
    platform_task_id TEXT NOT NULL,              -- External task ID
    platform_list_id TEXT,                       -- Task list/bucket ID
    
    -- Sync Management
    sync_status TEXT DEFAULT 'synced',           -- 'synced', 'pending', 'conflict', 'error'
    last_synced_at TEXT,                         -- ISO 8601 timestamp
    last_modified_at TEXT,                       -- Last modification time
    sync_direction TEXT,                         -- 'from_platform', 'to_platform', 'bidirectional'
    
    -- Platform-Specific Data
    platform_data TEXT,                          -- JSON: Store platform-specific fields
    
    -- Conflict Resolution
    local_version TEXT,                          -- Hash/version of local data
    remote_version TEXT,                         -- Hash/version of remote data
    conflict_data TEXT,                          -- JSON: Conflict details if any
    
    -- Metadata
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    
    -- Indexes for performance
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    UNIQUE(platform, platform_task_id)           -- Prevent duplicate sync entries
);

CREATE INDEX idx_sync_session ON task_sync_metadata(session_id);
CREATE INDEX idx_sync_platform ON task_sync_metadata(platform, platform_task_id);
CREATE INDEX idx_sync_status ON task_sync_metadata(sync_status);
```

### **🆕 NEW TABLE: `sync_operations_log`**

Track all sync operations for debugging and audit:

```sql
CREATE TABLE sync_operations_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    operation_type TEXT NOT NULL,                -- 'create', 'update', 'delete', 'sync'
    direction TEXT NOT NULL,                     -- 'inbound', 'outbound'
    status TEXT NOT NULL,                        -- 'success', 'failed', 'partial'
    changes_summary TEXT,                        -- JSON: What changed
    error_message TEXT,                          -- Error details if failed
    timestamp TEXT NOT NULL,
    
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_sync_log_timestamp ON sync_operations_log(timestamp DESC);
CREATE INDEX idx_sync_log_platform ON sync_operations_log(platform);
CREATE INDEX idx_sync_log_status ON sync_operations_log(status);
```

### **🆕 NEW TABLE: `platform_credentials`**

Store per-user OAuth credentials securely:

```sql
CREATE TABLE platform_credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    platform TEXT NOT NULL,                      -- 'google', 'microsoft'
    
    -- OAuth Tokens
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expiry TEXT,                           -- ISO 8601 timestamp
    
    -- Platform Identifiers
    platform_user_id TEXT,                       -- User's ID on the platform
    email TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT 1,
    last_auth_at TEXT,
    
    -- Metadata
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    
    UNIQUE(user_id, platform)
);

CREATE INDEX idx_credentials_user ON platform_credentials(user_id);
CREATE INDEX idx_credentials_platform ON platform_credentials(platform);
```

### **🆕 NEW TABLE: `agent_task_assignments`**

Track which agents are working on which tasks:

```sql
CREATE TABLE agent_task_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,                    -- Links to sessions.session_id
    agent_id INTEGER NOT NULL,                   -- MultiAgent.nextAgentId
    agent_name TEXT NOT NULL,                    -- e.g., 'Alpha-1'
    
    -- Assignment Details
    thread_id TEXT,                              -- Current thread assignment
    status TEXT DEFAULT 'assigned',              -- 'assigned', 'working', 'paused', 'completed'
    
    -- Timing
    assigned_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    
    -- Metrics
    message_count INTEGER DEFAULT 0,
    tools_used TEXT,                             -- JSON array
    
    -- Metadata
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_agent_assignments_session ON agent_task_assignments(session_id);
CREATE INDEX idx_agent_assignments_agent ON agent_task_assignments(agent_id);
CREATE INDEX idx_agent_assignments_status ON agent_task_assignments(status);
```

---

## 🔄 Bidirectional Sync Architecture

### **Sync Flow Diagram**

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYNERGY KANBAN BOARD                         │
│                  (Master Data Store)                            │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Backlog  │  │In Progress│  │  Review  │  │   Done   │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
│       ↕              ↕              ↕              ↕           │
└─────────────────────────────────────────────────────────────────┘
                       ↕                    ↕
          ┌────────────┴─────────┬──────────┴──────────┐
          ↓                      ↓                       ↓
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  GOOGLE TASKS    │   │ MICROSOFT TO DO  │   │      AGENTS      │
│                  │   │                  │   │                  │
│  • Task Lists    │   │  • Task Lists    │   │  • Alpha-1       │
│  • Tasks         │   │  • Tasks         │   │  • Bravo-2       │
│  • Subtasks      │   │  • Importance    │   │  • Charlie-3     │
│  • Due Dates     │   │  • Reminders     │   │                  │
│  • Notes         │   │  • Categories    │   │  Working on      │
│  • Status        │   │  • Status        │   │  tasks from      │
│                  │   │                  │   │  any platform    │
└──────────────────┘   └──────────────────┘   └──────────────────┘
```

### **Sync Strategy**

#### **1. Initial Sync (Import Tasks)**

When user connects a platform:

```python
# Pseudo-code
async def initial_sync(platform, user_credentials):
    """Import all tasks from platform into Kanban board"""
    
    if platform == 'google_tasks':
        tasks = google_tasks_list_all()
    elif platform == 'microsoft_todo':
        tasks = microsoft_todo_list_all()
    
    for task in tasks:
        # Check if already exists
        existing = get_sync_metadata(platform, task.id)
        
        if not existing:
            # Create new Kanban card
            session = create_session_from_task(task, platform)
            
            # Create sync metadata
            create_sync_metadata({
                'session_id': session.session_id,
                'platform': platform,
                'platform_task_id': task.id,
                'sync_status': 'synced',
                'sync_direction': 'bidirectional'
            })
            
            log_sync_operation('create', 'inbound', 'success')
```

#### **2. Continuous Sync (Webhook/Polling)**

**Inbound Changes (Platform → Kanban):**

```python
async def sync_from_platform(platform, task_id):
    """Sync changes from external platform to Kanban"""
    
    # Get platform task
    if platform == 'google_tasks':
        platform_task = google_tasks_get_task(task_id)
    elif platform == 'microsoft_todo':
        platform_task = microsoft_todo_get_task(task_id)
    
    # Find corresponding session
    sync_meta = get_sync_metadata(platform, task_id)
    if not sync_meta:
        return  # New task - handle via initial_sync
    
    session = get_session(sync_meta.session_id)
    
    # Detect conflicts
    if has_local_changes(session, sync_meta.last_synced_at):
        handle_conflict(session, platform_task, sync_meta)
        return
    
    # Apply changes
    update_session_from_task(session, platform_task)
    
    # Update sync metadata
    update_sync_metadata(sync_meta, {
        'last_synced_at': now(),
        'remote_version': hash(platform_task)
    })
    
    log_sync_operation('update', 'inbound', 'success')
```

**Outbound Changes (Kanban → Platform):**

```python
async def sync_to_platform(session_id):
    """Sync Kanban changes to external platforms"""
    
    session = get_session(session_id)
    sync_metas = get_all_sync_metadata(session_id)
    
    for sync_meta in sync_metas:
        platform = sync_meta.platform
        
        # Get current platform state
        if platform == 'google_tasks':
            platform_task = google_tasks_get_task(sync_meta.platform_task_id)
            update_func = google_tasks_update_task
        elif platform == 'microsoft_todo':
            platform_task = microsoft_todo_get_task(sync_meta.platform_task_id)
            update_func = microsoft_todo_update_task
        
        # Detect conflicts
        if has_remote_changes(platform_task, sync_meta.last_synced_at):
            handle_conflict(session, platform_task, sync_meta)
            continue
        
        # Prepare updates
        updates = map_session_to_task(session, platform)
        
        # Push to platform
        result = update_func(sync_meta.platform_task_id, updates)
        
        # Update sync metadata
        update_sync_metadata(sync_meta, {
            'last_synced_at': now(),
            'local_version': hash(session)
        })
        
        log_sync_operation('update', 'outbound', 'success')
```

#### **3. Conflict Resolution**

When both sides have changes:

```python
def handle_conflict(session, platform_task, sync_meta):
    """Resolve sync conflicts"""
    
    conflict = {
        'local_changes': get_changes(session, sync_meta.last_synced_at),
        'remote_changes': get_changes(platform_task, sync_meta.last_synced_at),
        'timestamp': now()
    }
    
    # Store conflict
    update_sync_metadata(sync_meta, {
        'sync_status': 'conflict',
        'conflict_data': json.dumps(conflict)
    })
    
    # Resolution strategies:
    # 1. Last-write-wins (by timestamp)
    # 2. Manual review (show in UI)
    # 3. Merge changes (field-level)
    
    # Default: Last-write-wins
    if session.updated_at > platform_task.updated_at:
        # Local wins - push to platform
        sync_to_platform(session.session_id)
    else:
        # Remote wins - pull from platform
        sync_from_platform(sync_meta.platform, sync_meta.platform_task_id)
```

---

## 🔌 Field Mapping Between Systems

### **Kanban ↔ Google Tasks**

| Kanban Field | Google Tasks Field | Mapping Logic |
|---|---|---|
| `title` | `title` | Direct mapping |
| `description` | `notes` | Direct mapping |
| `status` | `status` | 'active'→'needsAction', 'completed'→'completed' |
| `kanban_column` | N/A (custom) | Store in `notes` as metadata |
| `priority` | N/A (custom) | Use title prefix [HIGH]/[MEDIUM]/[LOW] |
| `due_date` | `due` | ISO 8601 format |
| `assignees` | N/A | Store in `notes` |
| `tags` | N/A | Store in `notes` |
| `next_steps` | Subtasks | Create as child tasks |
| `checklist` | Subtasks | Create as child tasks |

### **Kanban ↔ Microsoft To Do**

| Kanban Field | Microsoft To Do Field | Mapping Logic |
|---|---|---|
| `title` | `title` | Direct mapping |
| `description` | `body.content` | HTML/plain text |
| `status` | `status` | 'active'→'notStarted', 'completed'→'completed' |
| `kanban_column` | N/A (custom) | Store in `body` as metadata |
| `priority` | `importance` | 'high'→'high', 'medium'→'normal', 'low'→'low' |
| `due_date` | `dueDateTime` | ISO 8601 format |
| `assignees` | N/A (To Do is personal) | Store in `body` |
| `tags` | `categories` | Direct mapping (array) |
| `next_steps` | Checklist items | Use `checklistItems` |
| `checklist` | Checklist items | Use `checklistItems` |
| `reminder` | `reminderDateTime` | ISO 8601 format |

### **Microsoft Planner Support**

For team collaboration (Planner):

| Kanban Field | Planner Field | Mapping Logic |
|---|---|---|
| `kanban_column` | `bucketId` | Map columns to buckets |
| `assignees` | `assignments` | Direct mapping |
| `priority` | `priority` | 0-10 scale |
| `checklist` | `checklist` | Direct mapping |
| `documents` | `references` | Link attachments |

---

## 🚀 Implementation Plan

### **Phase 1: Database Enhancement (Week 1)**

**Goal:** Add new tables and migration scripts

**Tasks:**
1. ✅ Create migration script: `migrations/001_add_task_sync.sql`
2. ✅ Add `task_sync_metadata` table
3. ✅ Add `sync_operations_log` table
4. ✅ Add `platform_credentials` table
5. ✅ Add `agent_task_assignments` table
6. ✅ Create indexes for performance
7. ✅ Test migration with existing data

**Deliverables:**
```sql
-- migrations/001_add_task_sync.sql
-- All CREATE TABLE statements
-- All CREATE INDEX statements
-- Sample data insertion
```

### **Phase 2: Backend Sync Engine (Week 2)**

**Goal:** Build bidirectional sync logic

**Tasks:**
1. Create `TaskSyncManager` class
2. Implement `initial_sync()` for Google Tasks
3. Implement `initial_sync()` for Microsoft To Do
4. Implement `sync_from_platform()`
5. Implement `sync_to_platform()`
6. Implement `handle_conflict()`
7. Add field mapping functions
8. Add error handling and retry logic
9. Create sync API endpoints
10. Add WebSocket notifications for real-time updates

**Deliverables:**
```python
# synergy_task_sync.py
class TaskSyncManager:
    async def initial_sync(platform, credentials)
    async def sync_from_platform(platform, task_id)
    async def sync_to_platform(session_id)
    def handle_conflict(session, platform_task, sync_meta)
    def map_session_to_google_task(session)
    def map_session_to_microsoft_task(session)
    def map_google_task_to_session(task)
    def map_microsoft_task_to_session(task)
```

### **Phase 3: Frontend Integration (Week 3)**

**Goal:** UI for platform connection and sync management

**Tasks:**
1. Add "Connect Platform" button to Synergy Dashboard
2. Create OAuth flow for Google Tasks
3. Create OAuth flow for Microsoft 365
4. Show sync status indicators on cards
5. Add platform icons to cards (G icon / M icon)
6. Show conflict resolution UI
7. Add sync settings panel
8. Real-time sync status updates via WebSocket

**UI Components:**

```javascript
// Platform Connection Modal
<div id="platform-connection-modal">
    <h3>Connect Task Management Platform</h3>
    <button onclick="connectGoogleTasks()">
        <img src="google-icon.svg" />
        Connect Google Tasks
    </button>
    <button onclick="connectMicrosoft365()">
        <img src="microsoft-icon.svg" />
        Connect Microsoft 365 To Do
    </button>
</div>

// Sync Status Indicator on Card
<div class="card-sync-status">
    <span class="sync-badge google-tasks synced" title="Synced with Google Tasks">
        <i class="fab fa-google"></i>
    </span>
    <span class="sync-badge microsoft-todo synced" title="Synced with Microsoft To Do">
        <i class="fab fa-microsoft"></i>
    </span>
</div>

// Conflict Resolution UI
<div class="sync-conflict-panel">
    <h4>Sync Conflict Detected</h4>
    <div class="conflict-comparison">
        <div class="local-version">
            <h5>Your Changes (Kanban)</h5>
            <p>Title: Q4 Campaign - Updated</p>
            <p>Due: Nov 1, 2025</p>
        </div>
        <div class="remote-version">
            <h5>Platform Changes (Google Tasks)</h5>
            <p>Title: Q4 Campaign - Revised</p>
            <p>Due: Nov 3, 2025</p>
        </div>
    </div>
    <div class="conflict-actions">
        <button onclick="resolveConflict('keep_local')">Keep My Changes</button>
        <button onclick="resolveConflict('keep_remote')">Use Platform Version</button>
        <button onclick="resolveConflict('merge')">Merge Both</button>
    </div>
</div>
```

### **Phase 4: Agent Integration (Week 4)**

**Goal:** Connect agents to unified task system

**Tasks:**
1. Update `MultiAgent.activateAgent()` to check for task assignments
2. Create `assignAgentToTask(session_id, agent_id)`
3. Update agent cards when working on synced tasks
4. Show platform icons on agent panels
5. Track agent performance per platform
6. Enable agents to update tasks across platforms

**Agent Enhancement:**

```javascript
// When agent starts working on a task
async function assignAgentToTask(sessionId, agentId) {
    // Create agent assignment record
    const assignment = await fetch('/api/agents/assign', {
        method: 'POST',
        body: JSON.stringify({
            session_id: sessionId,
            agent_id: agentId,
            agent_name: MultiAgent.getAgentName(agentId)
        })
    });
    
    // Update Kanban card
    synergyBoard.updateAgentCard(agentId, {
        kanban_column: 'in_progress',
        status: 'working',
        assigned_task: sessionId
    });
    
    // Show platform sync status
    const syncMeta = await fetch(`/api/sync/metadata/${sessionId}`);
    if (syncMeta.platforms.includes('google_tasks')) {
        showPlatformBadge(agentId, 'google');
    }
    if (syncMeta.platforms.includes('microsoft_todo')) {
        showPlatformBadge(agentId, 'microsoft');
    }
}

// When agent completes a task
async function completeAgentTask(sessionId, agentId) {
    // Update session status
    await synergyBoard.updateSession(sessionId, {
        status: 'completed',
        kanban_column: 'done'
    });
    
    // Trigger sync to all connected platforms
    await fetch(`/api/sync/complete/${sessionId}`, {
        method: 'POST'
    });
    
    // Update agent assignment
    await fetch(`/api/agents/assignment/${agentId}/complete`, {
        method: 'POST'
    });
}
```

---

## 📊 Sync API Endpoints

### **Platform Management**

```python
# Connect platform
POST /api/sync/connect
Body: {
    "platform": "google_tasks" | "microsoft_todo",
    "auth_code": "...",  # OAuth authorization code
    "user_id": "user123"
}
Response: {
    "success": true,
    "credential_id": 123,
    "email": "user@example.com"
}

# Disconnect platform
DELETE /api/sync/disconnect/{platform}
Response: { "success": true }

# Get connected platforms
GET /api/sync/platforms
Response: {
    "platforms": [
        {
            "platform": "google_tasks",
            "connected": true,
            "last_sync": "2025-10-28T10:30:00Z",
            "task_count": 45
        },
        {
            "platform": "microsoft_todo",
            "connected": true,
            "last_sync": "2025-10-28T10:25:00Z",
            "task_count": 23
        }
    ]
}
```

### **Sync Operations**

```python
# Initial sync (import all tasks)
POST /api/sync/initial/{platform}
Response: {
    "imported": 45,
    "skipped": 2,
    "duration_ms": 3500
}

# Manual sync trigger
POST /api/sync/trigger/{session_id}
Response: {
    "synced_platforms": ["google_tasks", "microsoft_todo"],
    "status": "success"
}

# Get sync status
GET /api/sync/status/{session_id}
Response: {
    "session_id": "sess_123",
    "sync_metadata": [
        {
            "platform": "google_tasks",
            "sync_status": "synced",
            "last_synced_at": "2025-10-28T10:30:00Z"
        }
    ]
}

# Resolve conflict
POST /api/sync/conflict/resolve
Body: {
    "session_id": "sess_123",
    "platform": "google_tasks",
    "resolution": "keep_local" | "keep_remote" | "merge"
}
Response: { "success": true }
```

### **Agent Integration**

```python
# Assign agent to task
POST /api/agents/assign
Body: {
    "session_id": "sess_123",
    "agent_id": 1,
    "agent_name": "Alpha-1"
}
Response: {
    "assignment_id": 456,
    "platforms": ["google_tasks"]  # Task is synced with these platforms
}

# Get agent assignments
GET /api/agents/{agent_id}/assignments
Response: {
    "assignments": [
        {
            "session_id": "sess_123",
            "status": "working",
            "platforms": ["google_tasks", "microsoft_todo"]
        }
    ]
}
```

---

## 🎯 What This Enables

### **For Users**

✅ **Unified Task View**
- See all tasks from Google Tasks & Microsoft 365 To Do in one Kanban board
- No need to switch between platforms
- Visual workflow management across all task sources

✅ **Bidirectional Sync**
- Changes in Kanban reflect immediately in Google Tasks
- Changes in Microsoft To Do appear in Kanban
- Work from any platform, data stays synced

✅ **Conflict-Free Collaboration**
- Smart conflict detection and resolution
- Never lose data from either side
- Clear visual indicators for sync status

✅ **Agent-Powered Task Execution**
- Assign AI agents to tasks from any platform
- Agents can update tasks across all connected platforms
- Track agent performance on external tasks

### **For Google Tasks Users**

✅ **Enhanced Visualization**
- Kanban board view instead of plain lists
- Rich metadata (documents, links, checklists)
- Project timeline view
- Statistics and analytics

✅ **Additional Features**
- Drag-drop task organization
- Card expansion with full details
- Resume session functionality
- Google Docs/Sheets integration within cards

✅ **AI Agent Integration**
- Agents can work on Google Tasks
- Automatic task completion tracking
- Performance metrics per task

### **For Microsoft 365 To Do Users**

✅ **Cross-Platform Access**
- Access Microsoft tasks from non-Microsoft interface
- Work alongside Google Tasks seamlessly
- Maintain importance levels and categories

✅ **Team Collaboration (Planner)**
- Manage Planner buckets as Kanban columns
- Track team task assignments
- Sync with Microsoft Teams

✅ **Enhanced Checklist Support**
- Visual checklist display
- Progress indicators
- Subtask management

### **For Multi-Agent System**

✅ **Platform-Agnostic Task Assignment**
- Assign agents to tasks from any platform
- Agents work regardless of task source
- Unified agent performance tracking

✅ **Intelligent Task Distribution**
- AI can prioritize tasks from multiple sources
- Balance workload across platforms
- Smart task recommendations

✅ **Comprehensive Activity Logging**
- Track which agent worked on which platform task
- Performance analytics per platform
- Tool usage statistics

---

## 🔐 Security & Privacy

### **OAuth Token Management**

```python
# Secure token storage
from cryptography.fernet import Fernet

class SecureCredentialStore:
    def __init__(self):
        # Load encryption key from environment
        self.cipher = Fernet(os.getenv('ENCRYPTION_KEY').encode())
    
    def store_tokens(self, user_id, platform, tokens):
        """Encrypt and store OAuth tokens"""
        encrypted_access = self.cipher.encrypt(tokens['access_token'].encode())
        encrypted_refresh = self.cipher.encrypt(tokens['refresh_token'].encode())
        
        # Store in database
        save_credentials({
            'user_id': user_id,
            'platform': platform,
            'access_token': encrypted_access.decode(),
            'refresh_token': encrypted_refresh.decode()
        })
    
    def get_tokens(self, user_id, platform):
        """Retrieve and decrypt OAuth tokens"""
        creds = load_credentials(user_id, platform)
        
        return {
            'access_token': self.cipher.decrypt(creds['access_token'].encode()).decode(),
            'refresh_token': self.cipher.decrypt(creds['refresh_token'].encode()).decode()
        }
```

### **Data Privacy**

- ✅ All OAuth tokens encrypted at rest
- ✅ Tokens stored per-user (multi-tenant support)
- ✅ Tokens auto-refresh before expiry
- ✅ Secure HTTPS communication only
- ✅ No data shared between users
- ✅ Audit log for all sync operations

---

## 📈 Performance Optimization

### **Efficient Sync Strategy**

```python
# Batch operations
async def batch_sync_sessions(session_ids, platform):
    """Sync multiple sessions in one API call"""
    
    tasks = []
    for session_id in session_ids:
        tasks.append(sync_to_platform(session_id, platform))
    
    # Run in parallel with concurrency limit
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        'success': sum(1 for r in results if not isinstance(r, Exception)),
        'failed': sum(1 for r in results if isinstance(r, Exception))
    }

# Smart polling (only check changed tasks)
def get_tasks_to_sync(platform, since_timestamp):
    """Only fetch tasks modified since last sync"""
    
    if platform == 'google_tasks':
        # Google Tasks supports updatedMin parameter
        return google_tasks_list(updated_min=since_timestamp)
    
    elif platform == 'microsoft_todo':
        # Microsoft Graph supports delta queries
        return microsoft_todo_delta(since_timestamp)
```

### **Caching Strategy**

```python
from functools import lru_cache
from datetime import datetime, timedelta

class SyncCache:
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)
    
    def get_platform_tasks(self, platform):
        """Get cached platform tasks"""
        cache_key = f"{platform}_tasks"
        
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                return data
        
        # Cache miss - fetch from platform
        tasks = self.fetch_from_platform(platform)
        self.cache[cache_key] = (tasks, datetime.now())
        return tasks
```

---

## 🧪 Testing Strategy

### **Unit Tests**

```python
# test_task_sync.py

def test_google_task_to_session_mapping():
    """Test Google Tasks → Kanban mapping"""
    google_task = {
        'id': 'task_123',
        'title': 'Test Task',
        'notes': 'Description',
        'status': 'needsAction',
        'due': '2025-10-30T17:00:00.000Z'
    }
    
    session = map_google_task_to_session(google_task)
    
    assert session['title'] == 'Test Task'
    assert session['description'] == 'Description'
    assert session['status'] == 'active'
    assert session['due_date'] == '2025-10-30T17:00:00.000Z'

def test_microsoft_task_to_session_mapping():
    """Test Microsoft To Do → Kanban mapping"""
    ms_task = {
        'id': 'AAMkAGI...',
        'title': 'Test Task',
        'body': {'content': 'Description'},
        'importance': 'high',
        'dueDateTime': {'dateTime': '2025-10-30T17:00:00', 'timeZone': 'UTC'}
    }
    
    session = map_microsoft_task_to_session(ms_task)
    
    assert session['title'] == 'Test Task'
    assert session['priority'] == 'high'

def test_conflict_detection():
    """Test conflict detection logic"""
    session = {
        'updated_at': '2025-10-28T10:30:00Z',
        'title': 'Local Title'
    }
    
    platform_task = {
        'updated_at': '2025-10-28T10:35:00Z',
        'title': 'Remote Title'
    }
    
    assert has_conflict(session, platform_task, '2025-10-28T10:00:00Z')
```

### **Integration Tests**

```python
# test_sync_integration.py

async def test_full_sync_workflow():
    """Test complete sync workflow"""
    
    # 1. Connect platform
    result = await connect_platform('google_tasks', auth_code='...')
    assert result['success']
    
    # 2. Initial sync
    imported = await initial_sync('google_tasks')
    assert imported['imported'] > 0
    
    # 3. Modify task in Kanban
    await update_session('sess_123', {'title': 'Updated Title'})
    
    # 4. Sync to platform
    await sync_to_platform('sess_123')
    
    # 5. Verify on platform
    task = await google_tasks_get_task('task_123')
    assert task['title'] == 'Updated Title'
```

---

## 📚 Documentation

### **User Guide Topics**

1. **Getting Started**
   - Connecting Google Tasks
   - Connecting Microsoft 365 To Do
   - Initial sync process

2. **Daily Usage**
   - Creating tasks in Kanban (auto-syncs)
   - Updating tasks in external platforms
   - Understanding sync indicators

3. **Agent Integration**
   - Assigning agents to tasks
   - Tracking agent progress
   - Reviewing agent-completed tasks

4. **Troubleshooting**
   - Handling sync conflicts
   - Re-authenticating platforms
   - Sync error recovery

### **Developer Documentation**

1. **API Reference**
   - All sync endpoints
   - Request/response schemas
   - Error codes

2. **Database Schema**
   - Table structures
   - Relationships
   - Indexes

3. **Field Mapping Reference**
   - Google Tasks ↔ Kanban
   - Microsoft To Do ↔ Kanban
   - Custom field handling

---

## 🎉 Success Metrics

### **Phase 1 Success Criteria**
- ✅ Database migration completes without errors
- ✅ All tables created with proper indexes
- ✅ Existing data preserved

### **Phase 2 Success Criteria**
- ✅ Initial sync imports 100% of tasks from both platforms
- ✅ Bidirectional sync maintains consistency (99%+ accuracy)
- ✅ Conflict resolution works correctly
- ✅ Sync completes within 5 seconds for 100 tasks

### **Phase 3 Success Criteria**
- ✅ OAuth flows work smoothly for both platforms
- ✅ Real-time sync indicators update within 2 seconds
- ✅ UI clearly shows which platforms are connected
- ✅ Conflict resolution UI is intuitive

### **Phase 4 Success Criteria**
- ✅ Agents successfully work on tasks from any platform
- ✅ Agent task completion syncs to all platforms
- ✅ Agent performance metrics tracked per platform
- ✅ 100% of agent actions logged

---

## 🚀 Next Steps

### **Immediate Actions**

1. **Review this design document** with the team
2. **Approve database schema changes**
3. **Set up OAuth apps**:
   - Google Cloud Console project
   - Azure AD app registration
4. **Create development environment** with test accounts
5. **Begin Phase 1 implementation**

### **Week 1 Deliverables**

- [ ] Migration script: `001_add_task_sync.sql`
- [ ] Database backup procedure
- [ ] Test data set for both platforms
- [ ] OAuth credentials (dev environment)

Would you like me to proceed with implementing Phase 1 (Database Enhancement)? I can create the migration SQL file and update the synergy_backend.py to support the new tables.
