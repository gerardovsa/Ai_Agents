# 📋 Kanban Integration - Complete Documentation

## Overview

The Kanban Integration bridges task management with AI agent execution, allowing Kanban board sessions to be assigned to AI agents for automated processing. This creates a seamless workflow where tasks move through columns as agents work on them.

**Key Features:**
- Kanban session CRUD operations
- AI agent assignment to sessions
- Status synchronization between Kanban and agents
- Bridge table for session-agent linking
- Real-time status updates
- Persistent storage in SQLite

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database Schema](#database-schema)
3. [API Reference](#api-reference)
4. [Agent Assignment](#agent-assignment)
5. [Status Synchronization](#status-synchronization)
6. [Usage Examples](#usage-examples)
7. [Integration with UI](#integration-with-ui)
8. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### Component Structure

```
Kanban Integration
├── routes/
│   └── kanban_routes.py          # API endpoints (kanban_bp)
├── core/
│   ├── unified_session_manager.py # Session persistence
│   └── agent_state_manager.py     # Agent state tracking
└── data/
    ├── synergy_sessions.db        # Kanban database
    └── ai_infrastructure.db       # AI agent database
```

### Data Flow

```
User Creates Session → Kanban DB (synergy_sessions.db)
        ↓
User Assigns to Agent → Bridge Table (session_agents)
        ↓
Agent Processes Task → AI Infrastructure DB
        ↓
Status Sync Back → Kanban DB (status updated)
        ↓
UI Updates → Real-time display
```

### Integration Pattern

```
Kanban Board (UI) ←→ Kanban Routes (API) ←→ Kanban DB
                              ↕
                    Agent Routes (API) ←→ Agent State Manager
                              ↕
                         AI Client (Process Task)
```

---

## Database Schema

### Kanban Database (synergy_sessions.db)

**sessions table:**
```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,              -- UUID
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',     -- active | archived | completed
    kanban_column TEXT DEFAULT 'todo', -- todo | in-progress | done
    priority TEXT DEFAULT 'medium',   -- low | medium | high | urgent
    assigned_to TEXT,                 -- Agent ID (if assigned)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT                     -- JSON for custom fields
);
```

**session_agents bridge table:**
```sql
CREATE TABLE session_agents (
    session_id TEXT,
    agent_id TEXT,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'assigned',   -- assigned | working | completed | failed
    result TEXT,                      -- JSON result from agent
    PRIMARY KEY (session_id, agent_id),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

### AI Infrastructure Database (ai_infrastructure.db)

**threads table:**
```sql
CREATE TABLE threads (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    agent_id TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    metadata TEXT
);
```

**messages table:**
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT,
    role TEXT,                        -- user | assistant | system
    content TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (thread_id) REFERENCES threads(id)
);
```

---

## API Reference

### POST /api/kanban/sessions

Create a new Kanban session.

**Request Body:**
```json
{
    "title": "Session Title",
    "description": "Session description",
    "priority": "high",
    "kanban_column": "todo",
    "metadata": {
        "tags": ["ai", "automation"],
        "due_date": "2025-11-01"
    }
}
```

**Response:**
```json
{
    "success": true,
    "session": {
        "id": "session-uuid-123",
        "title": "Session Title",
        "status": "active",
        "kanban_column": "todo",
        "priority": "high",
        "created_at": "2025-10-29T10:00:00Z"
    }
}
```

---

### GET /api/kanban/sessions

List all Kanban sessions.

**Query Parameters:**
- `status` (string) - Filter by status (active, archived, completed)
- `column` (string) - Filter by column (todo, in-progress, done)
- `limit` (int) - Max results (default: 100)

**Response:**
```json
{
    "success": true,
    "sessions": [
        {
            "id": "session-uuid-123",
            "title": "Session Title",
            "status": "active",
            "kanban_column": "todo",
            "priority": "high",
            "assigned_to": null,
            "created_at": "2025-10-29T10:00:00Z"
        }
    ],
    "total": 1
}
```

---

### GET /api/kanban/sessions/:id

Get a specific session by ID.

**Path Parameters:**
- `id` (string) - Session UUID

**Response:**
```json
{
    "success": true,
    "session": {
        "id": "session-uuid-123",
        "title": "Session Title",
        "description": "Detailed description",
        "status": "active",
        "kanban_column": "in-progress",
        "priority": "high",
        "assigned_to": "data-agent",
        "created_at": "2025-10-29T10:00:00Z",
        "updated_at": "2025-10-29T10:30:00Z",
        "metadata": {
            "tags": ["ai", "automation"]
        }
    }
}
```

---

### PATCH /api/kanban/sessions/:id

Update a session.

**Path Parameters:**
- `id` (string) - Session UUID

**Request Body:**
```json
{
    "title": "Updated Title",
    "kanban_column": "in-progress",
    "priority": "urgent",
    "metadata": {
        "notes": "Updated by AI"
    }
}
```

**Response:**
```json
{
    "success": true,
    "session": {
        "id": "session-uuid-123",
        "title": "Updated Title",
        "kanban_column": "in-progress",
        "priority": "urgent",
        "updated_at": "2025-10-29T11:00:00Z"
    }
}
```

---

### DELETE /api/kanban/sessions/:id

Delete a session (soft delete - sets status to archived).

**Path Parameters:**
- `id` (string) - Session UUID

**Response:**
```json
{
    "success": true,
    "message": "Session archived"
}
```

---

### POST /api/kanban/sessions/:id/assign-agent

Assign a session to an AI agent for processing.

**Path Parameters:**
- `id` (string) - Session UUID

**Request Body:**
```json
{
    "agent_id": "data-agent",
    "instructions": "Process this task and provide recommendations"
}
```

**Response:**
```json
{
    "success": true,
    "assignment": {
        "session_id": "session-uuid-123",
        "agent_id": "data-agent",
        "assigned_at": "2025-10-29T12:00:00Z",
        "status": "assigned"
    },
    "message": "Session assigned to agent"
}
```

**What happens:**
1. Session marked as assigned to agent
2. Entry created in `session_agents` bridge table
3. Agent can now process the session
4. Status syncs back to Kanban automatically

---

### GET /api/kanban/sessions/:id/agent-status

Get the status of agent work on a session.

**Path Parameters:**
- `id` (string) - Session UUID

**Response:**
```json
{
    "success": true,
    "session_id": "session-uuid-123",
    "agent_id": "data-agent",
    "status": "working",
    "progress": {
        "started_at": "2025-10-29T12:00:00Z",
        "messages_exchanged": 5,
        "tools_used": ["gmail_send", "google_docs_create"],
        "current_activity": "Creating document"
    }
}
```

---

### PATCH /api/kanban/sessions/:id/sync-from-agent

Sync session status from agent work.

**Path Parameters:**
- `id` (string) - Session UUID

**Response:**
```json
{
    "success": true,
    "session": {
        "id": "session-uuid-123",
        "kanban_column": "done",
        "status": "completed",
        "updated_at": "2025-10-29T13:00:00Z"
    },
    "agent_result": {
        "completed_at": "2025-10-29T13:00:00Z",
        "summary": "Task completed successfully",
        "artifacts": ["doc-id-123", "email-msg-456"]
    }
}
```

---

## Agent Assignment

### Assignment Flow

```
1. User creates Kanban session
   POST /api/kanban/sessions
   
2. User assigns session to agent
   POST /api/kanban/sessions/:id/assign-agent
   
3. Agent starts processing
   - Loads session data
   - Executes tasks
   - Updates status
   
4. Status syncs back to Kanban
   PATCH /api/kanban/sessions/:id/sync-from-agent
   
5. Kanban column updated automatically
   - "todo" → "in-progress" (when agent starts)
   - "in-progress" → "done" (when agent completes)
```

### Assignment Example

```javascript
// 1. Create session
const createResponse = await fetch('http://localhost:4000/api/kanban/sessions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        title: "Process Sales Report",
        description: "Analyze sales data and send report to management",
        priority: "high"
    })
});

const { session } = await createResponse.json();

// 2. Assign to agent
const assignResponse = await fetch(
    `http://localhost:4000/api/kanban/sessions/${session.id}/assign-agent`,
    {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            agent_id: "data-agent",
            instructions: "Analyze the sales data and create a comprehensive report"
        })
    }
);

// 3. Agent processes automatically
// 4. Check status periodically
const checkStatus = async () => {
    const statusResponse = await fetch(
        `http://localhost:4000/api/kanban/sessions/${session.id}/agent-status`
    );
    const status = await statusResponse.json();
    console.log(status);
};

setInterval(checkStatus, 5000); // Check every 5 seconds
```

---

## Status Synchronization

### Automatic Sync

Status changes are automatically synchronized:

**Agent Status → Kanban Column:**
- Agent starts → `kanban_column = "in-progress"`
- Agent completes → `kanban_column = "done"`
- Agent errors → `status = "failed"`, column unchanged

**Kanban Action → Agent Status:**
- Move to "in-progress" → Signal agent to start
- Move to "done" manually → Mark agent task as completed
- Archive session → Stop agent if running

### Manual Sync

Force synchronization:

```javascript
const syncResponse = await fetch(
    `http://localhost:4000/api/kanban/sessions/${sessionId}/sync-from-agent`,
    { method: 'PATCH' }
);

const { session, agent_result } = await syncResponse.json();
console.log('Session updated:', session);
console.log('Agent result:', agent_result);
```

---

## Usage Examples

### Example 1: Simple Task Assignment

```javascript
async function assignSimpleTask() {
    // Create session
    const session = await fetch('http://localhost:4000/api/kanban/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: "Send Weekly Report",
            description: "Send weekly sales report to management@company.com"
        })
    }).then(r => r.json());
    
    // Assign to agent
    await fetch(`http://localhost:4000/api/kanban/sessions/${session.session.id}/assign-agent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            agent_id: "data-agent",
            instructions: "Compile and send the weekly sales report"
        })
    });
    
    console.log('Task assigned to agent');
}
```

### Example 2: Monitor Progress

```javascript
async function monitorProgress(sessionId) {
    const checkStatus = async () => {
        const response = await fetch(
            `http://localhost:4000/api/kanban/sessions/${sessionId}/agent-status`
        );
        const status = await response.json();
        
        if (status.status === 'completed') {
            console.log(' Task completed!');
            console.log('Result:', status.agent_result);
            clearInterval(interval);
        } else if (status.status === 'failed') {
            console.error(' Task failed:', status.error);
            clearInterval(interval);
        } else {
            console.log('🔄 In progress:', status.progress);
        }
    };
    
    const interval = setInterval(checkStatus, 3000);
}
```

### Example 3: Batch Processing

```javascript
async function batchProcess(tasks) {
    // Create multiple sessions
    const sessions = await Promise.all(
        tasks.map(task => 
            fetch('http://localhost:4000/api/kanban/sessions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(task)
            }).then(r => r.json())
        )
    );
    
    // Assign all to agents
    await Promise.all(
        sessions.map(({ session }) =>
            fetch(`http://localhost:4000/api/kanban/sessions/${session.id}/assign-agent`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    agent_id: "data-agent",
                    instructions: "Process this task"
                })
            })
        )
    );
    
    console.log(` ${sessions.length} tasks assigned to agents`);
}
```

---

## Integration with UI

### Kanban Board UI

The UI (e.g., `business-ai-platform-v2.html`) integrates with the API:

```javascript
// Fetch and display sessions
async function loadKanbanBoard() {
    const response = await fetch('http://localhost:4000/api/kanban/sessions');
    const { sessions } = await response.json();
    
    // Group by column
    const columns = {
        todo: sessions.filter(s => s.kanban_column === 'todo'),
        'in-progress': sessions.filter(s => s.kanban_column === 'in-progress'),
        done: sessions.filter(s => s.kanban_column === 'done')
    };
    
    // Render each column
    renderColumn('todo', columns.todo);
    renderColumn('in-progress', columns['in-progress']);
    renderColumn('done', columns.done);
}

// Drag and drop to move between columns
function onCardDrop(sessionId, newColumn) {
    fetch(`http://localhost:4000/api/kanban/sessions/${sessionId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ kanban_column: newColumn })
    });
}

// Assign to agent button
function onAssignToAgent(sessionId) {
    fetch(`http://localhost:4000/api/kanban/sessions/${sessionId}/assign-agent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            agent_id: "data-agent",
            instructions: "Process this task"
        })
    });
}
```

---

## Troubleshooting

### Issue: Session Not Found

**Symptoms:** 404 error when accessing session

**Solutions:**
1. Verify session ID:
```bash
curl http://localhost:4000/api/kanban/sessions
```

2. Check database:
```python
import sqlite3
conn = sqlite3.connect('data/synergy_sessions.db')
cursor = conn.cursor()
cursor.execute("SELECT id, title FROM sessions")
print(cursor.fetchall())
```

---

### Issue: Agent Assignment Fails

**Symptoms:** Assignment returns error

**Solutions:**
1. Verify agent is available:
```bash
curl http://localhost:4000/api/agent/data-agent/status
```

2. Check bridge table:
```python
cursor.execute("SELECT * FROM session_agents WHERE session_id = ?", (session_id,))
print(cursor.fetchall())
```

---

### Issue: Status Not Syncing

**Symptoms:** Kanban column doesn't update when agent completes

**Solutions:**
1. Force sync:
```bash
curl -X PATCH http://localhost:4000/api/kanban/sessions/SESSION_ID/sync-from-agent
```

2. Check agent status:
```bash
curl http://localhost:4000/api/agent/data-agent/status
```

---

**Last Updated:** October 29, 2025  
**Version:** 2.0.0  
**Status:**  Production Ready
