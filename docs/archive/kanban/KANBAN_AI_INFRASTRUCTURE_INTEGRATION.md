# 🔗 Kanban Board & AI Infrastructure Integration Guide

**Date:** October 28, 2025  
**Purpose:** Comprehensive guide to how Synergy Kanban Board integrates with AI Infrastructure

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  Synergy Kanban Board (Frontend)                                │
│  - Drag & drop task management                                  │
│  - Real-time collaboration via WebSocket                        │
│  - Task creation/editing/deletion                               │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND API LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  synergy_backend.py (Port 4000)                                 │
│  ├─ REST API (/api/sessions/*)                                  │
│  ├─ WebSocket (/ws/synergy)                                     │
│  └─ Task Sync Routes (/api/sync/*)  ← NEW INTEGRATION          │
└───────┬───────────────────────────────────────────┬─────────────┘
        │                                           │
        ▼                                           ▼
┌─────────────────────┐                  ┌──────────────────────┐
│  SYNERGY DATABASE   │                  │  TASK SYNC ENGINE    │
│  (SQLite)           │                  │                      │
│                     │                  │  task_sync_routes.py │
│  synergy_sessions.db│◄─────────────────┤  + mapper            │
│                     │                  │  + tool_registry     │
│  Tables:            │                  └──────────┬───────────┘
│  • sessions         │                             │
│  • task_sync_meta.. │                             │
│  • sync_operations..│                             │
│  • platform_creds   │                             │
│  • agent_task_ass.. │                             │
│  • sync_config      │                             │
└─────────────────────┘                             │
                                                    │
        ┌───────────────────────────────────────────┤
        │                                           │
        ▼                                           ▼
┌─────────────────────┐              ┌──────────────────────────┐
│  GOOGLE WORKSPACE   │              │  MICROSOFT 365           │
│                     │              │                          │
│  • Google Tasks     │              │  • Microsoft To Do       │
│  • Google Calendar  │              │  • Planner               │
│                     │              │                          │
└─────────────────────┘              └──────────────────────────┘
```

---

## 🗄️ Database Integration

### **Current State: TWO SEPARATE DATABASES**

```
AI_agents/
├── data/
│   └── synergy_sessions.db          ← Kanban Board Database
│
└── AI_infrastructure/
    └── ai_infrastructure.db          ← AI Agent System Database
```

### **Why Two Databases?**

1. **Separation of Concerns**
   - `synergy_sessions.db` = Task/Project Management (User-facing)
   - `ai_infrastructure.db` = Agent System (Backend automation)

2. **Independent Evolution**
   - Synergy can be updated without breaking AI infrastructure
   - AI system can scale independently

3. **Security**
   - User tasks isolated from system internals
   - Different access patterns and permissions

---

## 🔗 How They Connect

### **Option 1: Current Architecture (Separate Databases)**

**Connection Method:** API-based integration through shared backend

```python
# In AI_infrastructure routes (agent_routes.py)
import requests

def assign_task_to_agent(agent_id, task_details):
    """AI Infrastructure can CREATE tasks in Synergy DB"""
    
    # Call Synergy API to create Kanban card
    response = requests.post(
        'http://localhost:4000/api/sessions/create',
        json={
            'title': task_details['title'],
            'description': task_details['description'],
            'priority': 'high',
            'assignees': [agent_id],
            'project_name': 'AI Agent Work'
        }
    )
    
    if response.status_code == 201:
        kanban_session = response.json()
        session_id = kanban_session['session_id']
        
        # Store session_id in AI Infrastructure DB
        # to track which Kanban card belongs to this agent task
        cursor.execute('''
            INSERT INTO agent_tasks (agent_id, kanban_session_id, status)
            VALUES (?, ?, 'assigned')
        ''', (agent_id, session_id))
        
        return session_id
```

**Reverse Connection:** Synergy can query AI Infrastructure

```python
# In synergy_backend.py
import sqlite3

def get_agent_for_task(session_id):
    """Check if any AI agent is assigned to this task"""
    
    ai_db = sqlite3.connect('../AI_infrastructure/ai_infrastructure.db')
    cursor = ai_db.cursor()
    
    cursor.execute('''
        SELECT agent_id, agent_name, status 
        FROM agent_tasks 
        WHERE kanban_session_id = ?
    ''', (session_id,))
    
    agent = cursor.fetchone()
    ai_db.close()
    
    return agent if agent else None
```

---

### **Option 2: RECOMMENDED - Unified Cross-Database Integration**

Create a **bridge table** in AI Infrastructure DB:

```sql
-- In AI_infrastructure/ai_infrastructure.db

CREATE TABLE IF NOT EXISTS kanban_task_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- AI Infrastructure side
    agent_id TEXT NOT NULL,
    agent_name TEXT,
    work_session_id TEXT,  -- From AI infrastructure
    
    -- Synergy Kanban side
    kanban_session_id TEXT NOT NULL,  -- Links to synergy_sessions.db
    kanban_title TEXT,
    kanban_status TEXT,
    
    -- Sync metadata
    sync_direction TEXT DEFAULT 'ai_to_kanban',  -- ai_to_kanban, kanban_to_ai, bidirectional
    last_synced_at TEXT,
    sync_status TEXT DEFAULT 'active',  -- active, paused, completed, error
    
    -- Timestamps
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_kanban_links_agent ON kanban_task_links(agent_id);
CREATE INDEX idx_kanban_links_session ON kanban_task_links(kanban_session_id);
```

---

## 🔄 Integration Workflow Examples

### **Example 1: AI Agent Creates Task in Kanban**

```python
# File: AI_infrastructure/routes/agent_routes.py

@agent_bp.route('/agent/<agent_id>/create_kanban_task', methods=['POST'])
def agent_create_kanban_task(agent_id):
    """AI Agent creates a task in Kanban board"""
    
    data = request.json
    
    # Step 1: Create task in Synergy Kanban DB
    synergy_response = requests.post(
        'http://localhost:4000/api/sessions/create',
        json={
            'title': data['title'],
            'description': data['description'],
            'priority': data.get('priority', 'medium'),
            'status': 'active',
            'kanban_column': 'backlog',
            'assignees': [f"AI Agent: {agent_id}"],
            'tags': ['ai-generated', 'agent-work'],
            'project_name': data.get('project', 'AI Agent Tasks')
        }
    )
    
    if synergy_response.status_code != 201:
        return jsonify({'error': 'Failed to create Kanban task'}), 500
    
    kanban_data = synergy_response.json()
    kanban_session_id = kanban_data['session_id']
    
    # Step 2: Create link in AI Infrastructure DB
    ai_db = get_db_connection()  # Connects to ai_infrastructure.db
    cursor = ai_db.cursor()
    
    cursor.execute('''
        INSERT INTO kanban_task_links 
        (agent_id, agent_name, kanban_session_id, kanban_title, kanban_status, sync_direction)
        VALUES (?, ?, ?, ?, ?, 'ai_to_kanban')
    ''', (agent_id, data.get('agent_name', 'Agent'), kanban_session_id, data['title'], 'backlog'))
    
    ai_db.commit()
    ai_db.close()
    
    return jsonify({
        'success': True,
        'kanban_session_id': kanban_session_id,
        'message': 'Task created in Kanban and linked to agent'
    }), 201
```

### **Example 2: Kanban Task Assigned to AI Agent**

```python
# File: synergy_backend.py (add new endpoint)

@app.route('/api/sessions/<session_id>/assign_to_agent', methods=['POST'])
def assign_task_to_ai_agent(session_id):
    """Assign Kanban task to an AI agent for automated work"""
    
    data = request.json
    agent_id = data.get('agent_id')
    
    # Step 1: Get task from Synergy DB
    conn = get_db_connection()  # synergy_sessions.db
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
    task = cursor.fetchone()
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Step 2: Create assignment in AI Infrastructure
    ai_response = requests.post(
        'http://localhost:5000/api/agent/assign_task',  # AI Infrastructure runs on 5000
        json={
            'agent_id': agent_id,
            'task_id': session_id,
            'task_title': task['title'],
            'task_description': task['description'],
            'priority': task['priority']
        }
    )
    
    if ai_response.status_code == 200:
        # Update task in Synergy DB to show agent assignment
        cursor.execute('''
            UPDATE sessions 
            SET assignees = json_insert(assignees, '$[#]', ?),
                updated_at = ?
            WHERE session_id = ?
        ''', (f"AI Agent: {agent_id}", datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Task assigned to AI Agent {agent_id}'
        }), 200
    else:
        conn.close()
        return jsonify({'error': 'Failed to assign to agent'}), 500
```

### **Example 3: Sync Task Status Between Systems**

```python
# File: sync_bridge.py (NEW FILE - Bridge between systems)

import sqlite3
import requests
from datetime import datetime

class KanbanAIBridge:
    """Bridge between Synergy Kanban and AI Infrastructure"""
    
    def __init__(self):
        self.synergy_db_path = 'data/synergy_sessions.db'
        self.ai_db_path = 'AI_infrastructure/ai_infrastructure.db'
    
    def sync_task_status(self, kanban_session_id):
        """Sync task status from Kanban to AI Infrastructure"""
        
        # Get task status from Synergy
        synergy_conn = sqlite3.connect(self.synergy_db_path)
        synergy_cursor = synergy_conn.cursor()
        synergy_cursor.execute(
            'SELECT status, kanban_column FROM sessions WHERE session_id = ?',
            (kanban_session_id,)
        )
        task = synergy_cursor.fetchone()
        synergy_conn.close()
        
        if not task:
            return {'error': 'Task not found'}
        
        status, column = task
        
        # Update AI Infrastructure DB
        ai_conn = sqlite3.connect(self.ai_db_path)
        ai_cursor = ai_conn.cursor()
        
        ai_cursor.execute('''
            UPDATE kanban_task_links 
            SET kanban_status = ?,
                last_synced_at = ?
            WHERE kanban_session_id = ?
        ''', (column, datetime.now().isoformat(), kanban_session_id))
        
        ai_conn.commit()
        ai_conn.close()
        
        return {'success': True, 'status': column}
    
    def sync_agent_progress_to_kanban(self, agent_id):
        """Update Kanban board with agent progress"""
        
        # Get agent tasks from AI Infrastructure
        ai_conn = sqlite3.connect(self.ai_db_path)
        ai_cursor = ai_conn.cursor()
        ai_cursor.execute('''
            SELECT kanban_session_id, sync_status 
            FROM kanban_task_links 
            WHERE agent_id = ? AND sync_status = 'active'
        ''', (agent_id,))
        
        agent_tasks = ai_cursor.fetchall()
        ai_conn.close()
        
        # Update each task in Synergy
        for session_id, status in agent_tasks:
            requests.patch(
                f'http://localhost:4000/api/sessions/{session_id}',
                json={
                    'notes': f'Agent {agent_id} working on this task...',
                    'updated_at': datetime.now().isoformat()
                }
            )
        
        return {'success': True, 'updated_count': len(agent_tasks)}
```

---

## 🎯 Platform Sync Integration

### **How Google Tasks/Microsoft To Do Connects**

```
USER KANBAN BOARD
      ↓
synergy_sessions.db (sessions table)
      ↓
POST /api/sync/bidirectional/{session_id}
      ↓
┌─────────────────────────────────────────┐
│  task_sync_routes.py                    │
│  1. Read from sessions table            │
│  2. Convert via UniversalTaskMapper     │
│  3. Call Google/Microsoft APIs          │
│  4. Store sync_metadata in DB           │
└─────────────────────────────────────────┘
      ↓
task_sync_metadata table
(platform, platform_task_id, sync_status)
```

**Example Flow:**

```python
# User creates task in Kanban UI
# Frontend calls: POST /api/sessions/create
# Creates row in sessions table

# User clicks "Sync to Google Tasks"
# Frontend calls: POST /api/sync/google-tasks/create
# With: {"session_id": "20251028_1400_task123"}

# Backend flow:
# 1. Read from sessions table (synergy_sessions.db)
session = get_from_sessions_table(session_id)

# 2. Convert to Google Tasks format
google_task = mapper.kanban_to_google_task(session)

# 3. Create via Google Tasks API
result = tool_registry.execute_tool('google_tasks_create_task', 
    title=google_task['title'],
    notes=google_task['notes'],
    due=google_task['due']
)

# 4. Store sync metadata (SAME DATABASE)
cursor.execute('''
    INSERT INTO task_sync_metadata 
    (session_id, platform, platform_task_id, sync_status)
    VALUES (?, 'google_tasks', ?, 'synced')
''', (session_id, result['task']['id']))
```

---

## 🔧 Implementation Plan

### **Phase 1: Current State (DONE ✅)**
- ✅ Synergy Kanban database with task sync tables
- ✅ Task sync routes integrated
- ✅ Universal mapper for Google/Microsoft

### **Phase 2: AI Infrastructure Bridge (RECOMMENDED NEXT)**

Create the bridge:

```python
# File: AI_infrastructure/migrations/add_kanban_bridge.sql

CREATE TABLE IF NOT EXISTS kanban_task_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    kanban_session_id TEXT NOT NULL UNIQUE,
    sync_direction TEXT DEFAULT 'bidirectional',
    last_synced_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_kanban_links_agent ON kanban_task_links(agent_id);
```

Add to `AI_infrastructure/routes/agent_routes.py`:

```python
@agent_bp.route('/agent/<agent_id>/kanban_tasks', methods=['GET'])
def get_agent_kanban_tasks(agent_id):
    """Get all Kanban tasks assigned to this agent"""
    
    # Query bridge table
    cursor.execute('''
        SELECT kanban_session_id 
        FROM kanban_task_links 
        WHERE agent_id = ?
    ''', (agent_id,))
    
    session_ids = [row[0] for row in cursor.fetchall()]
    
    # Fetch tasks from Synergy API
    tasks = []
    for session_id in session_ids:
        response = requests.get(f'http://localhost:4000/api/sessions/{session_id}')
        if response.status_code == 200:
            tasks.append(response.json())
    
    return jsonify({'tasks': tasks}), 200
```

### **Phase 3: Real-time Sync (Future)**

WebSocket bridge between systems:

```python
# File: websocket_bridge.py

from flask_socketio import SocketIO, emit
import requests

# Connect to both systems
synergy_socket = SocketIO(message_queue='redis://localhost:6379/0')
ai_socket = SocketIO(message_queue='redis://localhost:6379/1')

@synergy_socket.on('task_updated')
def handle_task_update(data):
    """When Kanban task updates, notify AI Infrastructure"""
    session_id = data['session_id']
    
    # Check if task is linked to an agent
    agent = get_agent_for_task(session_id)
    if agent:
        # Notify AI Infrastructure
        ai_socket.emit('kanban_task_updated', {
            'agent_id': agent['agent_id'],
            'session_id': session_id,
            'status': data['status']
        })
```

---

## 📊 Data Flow Summary

### **Three-Layer Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: USER INTERFACE                                │
│  - Kanban Board UI (drag & drop)                        │
│  - Task creation/editing                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 2: TASK MANAGEMENT (Synergy)                     │
│  synergy_sessions.db                                    │
│  - sessions (Kanban cards)                              │
│  - task_sync_metadata (Google/Microsoft sync)           │
│                                                          │
│  APIs:                                                   │
│  - /api/sessions/* (CRUD)                               │
│  - /api/sync/* (Platform sync)  ← NEW                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 3: AI AUTOMATION (AI Infrastructure)             │
│  ai_infrastructure.db                                   │
│  - agent_sessions (Agent work)                          │
│  - kanban_task_links (Bridge to Synergy) ← TO ADD       │
│                                                          │
│  APIs:                                                   │
│  - /api/agent/* (Agent management)                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Quick Start Integration

**1. Add bridge table to AI Infrastructure:**

```bash
cd AI_infrastructure
python migrations/add_kanban_bridge.py
```

**2. Test cross-database query:**

```python
# In Python console
import sqlite3

# Query both databases
synergy = sqlite3.connect('data/synergy_sessions.db')
ai = sqlite3.connect('AI_infrastructure/ai_infrastructure.db')

# Get all Kanban tasks
kanban_tasks = synergy.execute('SELECT session_id, title FROM sessions').fetchall()

# Get all agent sessions  
agent_sessions = ai.execute('SELECT agent_id, agent_name FROM agent_sessions').fetchall()

print(f"Kanban tasks: {len(kanban_tasks)}")
print(f"Agent sessions: {len(agent_sessions)}")
```

**3. Create integration endpoint:**

```python
# Add to synergy_backend.py

@app.route('/api/integration/ai_agents', methods=['GET'])
def list_available_ai_agents():
    """Get list of AI agents from AI Infrastructure"""
    try:
        response = requests.get('http://localhost:5000/api/agent/list')
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': 'Failed to fetch agents'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## 🚀 Benefits of This Architecture

1. **✅ Loose Coupling**
   - Systems can evolve independently
   - Easy to replace/upgrade components

2. **✅ Scalability**
   - Synergy handles user-facing tasks
   - AI Infrastructure handles background processing
   - Each can scale separately

3. **✅ Security**
   - User data isolated from system internals
   - Different permission models

4. **✅ Flexibility**
   - Can add more databases (analytics, logging)
   - Can integrate additional systems (Jira, Trello, etc.)

5. **✅ Testability**
   - Each system can be tested in isolation
   - Mock APIs for integration testing

---

## 📝 Summary

**Current State:**
- ✅ Synergy Kanban (port 4000) with `synergy_sessions.db`
- ✅ Task sync to Google/Microsoft integrated
- ✅ AI Infrastructure (port 5000) with `ai_infrastructure.db` (separate)

**Integration Method:**
- API-based communication between systems
- Bridge table in AI Infrastructure to track Kanban links
- Shared task IDs for cross-referencing

**Next Step:**
Create `kanban_task_links` table in AI Infrastructure to enable bidirectional task assignment and status tracking!
