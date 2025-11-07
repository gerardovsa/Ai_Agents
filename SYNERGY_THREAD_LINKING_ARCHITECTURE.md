# Synergy ↔ Thread Bidirectional Linking Architecture

## Database Schema Understanding

### Synergy Sessions Database (synergy_sessions.db)

**Table: `synergy_sessions`**

```sql
CREATE TABLE synergy_sessions (
    session_id TEXT PRIMARY KEY,              -- e.g., "sess_20251107_1234_project"
    title TEXT NOT NULL,
    description TEXT,
    platforms_involved TEXT,                  -- JSON array
    status TEXT DEFAULT 'active',
    priority TEXT DEFAULT 'medium',
    kanban_column TEXT DEFAULT 'backlog',
    tags TEXT,                                -- JSON array
    documents TEXT,                           -- JSON array
    links TEXT,                               -- JSON array
    next_steps TEXT,                          -- JSON array
    assignees TEXT,                           -- JSON array
    recent_activity TEXT,                     -- JSON array
    checklist TEXT,                           -- JSON array
    due_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_active TEXT DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT,
    google_task_id TEXT,
    google_calendar_id TEXT,
    microsoft_todo_id TEXT,
    thread_ids TEXT,                          -- ✨ JSON array of linked thread IDs
    assigned_agents TEXT                      -- ✨ JSON array of agent names
)
```

**Key Fields for Thread Linking:**
- `thread_ids` - JSON array: `["thread_123", "thread_456", "thread_789"]`
- `assigned_agents` - JSON array: `["Prime Agent", "Research Agent", "Data Agent"]`

---

### Threads Database (sessions.db)

**Table: `threads`**

```sql
CREATE TABLE threads (
    thread_slug TEXT PRIMARY KEY,             -- e.g., "1731234567890"
    workspace_id TEXT,
    user_id INTEGER,
    name TEXT,                                -- Thread title
    created_at TEXT,
    updated_at TEXT,
    metadata TEXT,                            -- JSON object
    tags TEXT,                                -- JSON array
    synergy_card_id TEXT,                     -- ✨ Single Synergy session link
    parent_thread_id TEXT,
    branch_point_message_id TEXT,
    branch_name TEXT,
    summary TEXT,
    summary_generated_at TEXT,
    location TEXT                             -- Agent assignment: 'prime', 'agent2', etc.
)
```

**Key Fields for Synergy Linking:**
- `synergy_card_id` - Single session ID: `"sess_20251107_1234_project"`
- `location` - Agent assignment: `"prime"`, `"agent2"`, `"bravo"`, etc.
- `tags` - JSON array: `["urgent", "research", "finance"]`

---

## Linking Architecture

### One-to-Many Relationship

```
┌─────────────────────────────────────┐
│   SYNERGY SESSION                   │
│   sess_20251107_budget_review       │
│                                     │
│   thread_ids: [                     │
│     "1731234567890",     ◄──────────┼──┐
│     "1731234567999",     ◄──────────┼──┤
│     "1731235678000"      ◄──────────┼──┤
│   ]                                 │  │
│                                     │  │
│   assigned_agents: [                │  │
│     "Prime Agent",                  │  │
│     "Research Agent"                │  │
│   ]                                 │  │
└─────────────────────────────────────┘  │
                                         │
                                         │
    ┌────────────────────────────────────┤
    │                                    │
    ▼                                    ▼
┌─────────────────────┐      ┌─────────────────────┐
│   THREAD            │      │   THREAD            │
│   1731234567890     │      │   1731234567999     │
│                     │      │                     │
│   name: "Budget Q4" │      │   name: "Revenue"   │
│   location: "prime" │      │   location: "agent2"│
│   synergy_card_id:  │      │   synergy_card_id:  │
│   "sess_20251...──┐ │      │   "sess_20251...──┐ │
└───────────────────┼─┘      └───────────────────┼─┘
                    │                            │
                    └────────────┬───────────────┘
                                 │
                                 │ BOTH POINT BACK
                                 ▼
                    ┌────────────────────────┐
                    │  SYNERGY SESSION       │
                    │  sess_20251107_budget  │
                    └────────────────────────┘
```

**Key Insight:**
- **Synergy → Threads**: One session can link to MANY threads (array)
- **Thread → Synergy**: One thread can link to ONE session (single ID)
- **Bidirectional**: Both sides store the link

---

## API Endpoints

### Synergy Routes (`/api/synergy/`)

1. **GET `/api/synergy/sessions`** - Simple session list for dropdowns
   ```json
   [
     {
       "session_id": "sess_20251107_1234_budget",
       "title": "Q4 Budget Review",
       "project": "Finance",
       "column": "in-progress"
     }
   ]
   ```

2. **POST `/api/synergy/create`** - Create session with thread links
   ```json
   {
     "title": "Email Campaign Project",
     "description": "Multi-platform automation",
     "thread_ids": ["1731234567890", "1731234567999"],
     "assigned_agents": ["Email Agent", "Research Agent"]
   }
   ```

3. **PATCH `/api/synergy/<session_id>`** - Update session including threads
   ```json
   {
     "updates": {
       "thread_ids": ["1731234567890", "1731234567999", "1731235678000"],
       "assigned_agents": ["Prime Agent", "Bravo Agent"]
     }
   }
   ```

### Thread Routes (`/api/threads/`)

1. **POST `/api/threads/create`** - Create thread with Synergy link
   ```json
   {
     "user_id": 1,
     "title": "Budget Analysis Thread",
     "tags": ["urgent", "finance"],
     "synergy_card_id": "sess_20251107_1234_budget",
     "location": "prime"
   }
   ```

2. **POST `/api/threads/save`** - Save thread with Synergy link
   ```json
   {
     "thread_id": "1731234567890",
     "name": "Budget Analysis",
     "synergy_card_id": "sess_20251107_1234_budget"
   }
   ```

---

## New Chat Modal Implementation

### Modal Workflow

1. **User clicks "Start New Chat"**
2. **Modal opens with form:**
   - Thread Title (required)
   - Tags (optional, multi-select)
   - Synergy Session (optional, dropdown)
   - Agent Assignment (from location param)

3. **On Save:**
   - Create thread in `sessions.db` with `synergy_card_id`
   - If Synergy linked, update Synergy session to add thread ID
   - Update Synergy's `assigned_agents` array if agent not already listed

4. **Result:**
   - Thread created and loaded
   - Synergy session updated bidirectionally
   - Both databases synchronized

---

## Bidirectional Sync Logic

### When Creating Thread WITH Synergy Link

```javascript
async function createThreadWithSynergy(title, tags, synergySessionId, location) {
    // 1. Create thread
    const threadResponse = await fetch('/api/threads/create', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            user_id: 1,
            title: title,
            tags: tags,
            synergy_card_id: synergySessionId,  // ✨ Link to Synergy
            location: location
        })
    });
    
    const threadData = await threadResponse.json();
    const newThreadId = threadData.thread.id;
    
    // 2. Update Synergy session to add this thread
    if (synergySessionId) {
        // Get current session data
        const sessionResponse = await fetch(`/api/synergy/${synergySessionId}`);
        const sessionData = await sessionResponse.json();
        const session = sessionData.session;
        
        // Add thread ID to array
        const threadIds = JSON.parse(session.thread_ids || '[]');
        if (!threadIds.includes(newThreadId)) {
            threadIds.push(newThreadId);
        }
        
        // Add agent to array
        const agentName = getAgentDisplayName(location);  // e.g., "Prime Agent"
        const assignedAgents = JSON.parse(session.assigned_agents || '[]');
        if (!assignedAgents.includes(agentName)) {
            assignedAgents.push(agentName);
        }
        
        // Update Synergy session
        await fetch(`/api/synergy/${synergySessionId}`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                updates: {
                    thread_ids: threadIds,
                    assigned_agents: assignedAgents
                }
            })
        });
    }
    
    return threadData.thread;
}
```

### When Unlinking Thread FROM Synergy

```javascript
async function unlinkThreadFromSynergy(threadId, synergySessionId) {
    // 1. Remove synergy_card_id from thread
    await fetch('/api/threads/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            thread_id: threadId,
            synergy_card_id: null  // ✨ Remove link
        })
    });
    
    // 2. Remove thread ID from Synergy session
    const sessionResponse = await fetch(`/api/synergy/${synergySessionId}`);
    const sessionData = await sessionResponse.json();
    const session = sessionData.session;
    
    const threadIds = JSON.parse(session.thread_ids || '[]');
    const updatedThreadIds = threadIds.filter(id => id !== threadId);
    
    await fetch(`/api/synergy/${synergySessionId}`, {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            updates: {
                thread_ids: updatedThreadIds
            }
        })
    });
}
```

---

## Frontend Display

### Thread Header (Showing Synergy Link)

```html
<div class="thread-header-info">
    <h2>Budget Analysis Q4</h2>
    
    <div class="thread-metadata">
        <span>📨 5 msg</span>
        <span>📅 11/7/2025</span>
        <span>🕐 9:52 PM</span>
    </div>
    
    <div class="thread-tags">
        <span class="tag">🏷️ urgent</span>
        <span class="tag">🏷️ finance</span>
    </div>
    
    <!-- ✨ Synergy Link Display -->
    <div class="thread-synergy-link">
        <span class="synergy-badge">
            🎯 <a href="#" onclick="openSynergySession('sess_20251107_budget')">
                Q4 Budget Review
            </a>
            <button onclick="unlinkFromSynergy()">✕</button>
        </span>
    </div>
</div>
```

### Synergy Card (Showing Linked Threads)

```html
<div class="synergy-card">
    <div class="card-header">
        <h3>Q4 Budget Review</h3>
    </div>
    
    <div class="card-body">
        <p>Multi-agent budget analysis session</p>
    </div>
    
    <!-- ✨ Linked Threads Section -->
    <div class="card-linked-threads">
        <h4>💬 Linked Threads (3)</h4>
        <div class="thread-item" onclick="loadThread('1731234567890')">
            <span class="thread-icon">📨</span>
            <span class="thread-name">Budget Analysis Q4</span>
            <span class="thread-agent">Prime</span>
        </div>
        <div class="thread-item" onclick="loadThread('1731234567999')">
            <span class="thread-icon">📨</span>
            <span class="thread-name">Revenue Forecast</span>
            <span class="thread-agent">Agent-2</span>
        </div>
        <div class="thread-item" onclick="loadThread('1731235678000')">
            <span class="thread-icon">📨</span>
            <span class="thread-name">Expense Review</span>
            <span class="thread-agent">Bravo</span>
        </div>
    </div>
    
    <!-- ✨ Assigned Agents Section -->
    <div class="card-assigned-agents">
        <h4>🤖 Active Agents (3)</h4>
        <div class="agent-item">
            <span class="agent-status">🟢</span>
            <span class="agent-name">Prime Agent</span>
        </div>
        <div class="agent-item">
            <span class="agent-status">🔵</span>
            <span class="agent-name">Agent-2</span>
        </div>
        <div class="agent-item">
            <span class="agent-status">🟣</span>
            <span class="agent-name">Bravo Agent</span>
        </div>
    </div>
</div>
```

---

## Implementation Checklist

### Backend (Already Complete ✅)
- [x] Synergy DB has `thread_ids` and `assigned_agents` columns
- [x] Threads DB has `synergy_card_id` column
- [x] `/api/synergy/sessions` endpoint for dropdown
- [x] `/api/synergy/create` accepts thread_ids and assigned_agents
- [x] `/api/synergy/<id>` PATCH accepts thread_ids and assigned_agents
- [x] `/api/threads/create` accepts synergy_card_id
- [x] `/api/threads/save` accepts synergy_card_id

### Frontend (To Implement)
- [ ] New Chat Modal HTML structure
- [ ] New Chat Modal CSS (dark mode)
- [ ] Fetch Synergy sessions for dropdown
- [ ] Create thread with bidirectional sync
- [ ] Thread header Synergy link display
- [ ] Synergy card linked threads display
- [ ] Unlink functionality (both directions)

---

## Next Steps

1. **Create New Chat Modal** with:
   - Title input
   - Tag selector (reuse existing)
   - Synergy dropdown (from `/api/synergy/sessions`)
   - Auto-sync on creation

2. **Update Thread Header** to show:
   - Compact metadata with icons
   - Tag pills
   - Synergy link badge (clickable)

3. **Update Synergy Cards** to show:
   - Linked threads list (clickable)
   - Assigned agents list with status

4. **Add Backend Route** (optional optimization):
   - `GET /api/synergy/<session_id>/threads` - Get all linked threads with details
   - Returns threads with names, locations, message counts

**Ready to implement the New Chat Modal!**
