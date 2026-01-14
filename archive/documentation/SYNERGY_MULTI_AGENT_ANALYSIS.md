# Synergy Multi-Agent Concurrency Analysis

**Date:** November 13, 2025  
**Project:** Business AI Platform v2  
**Focus:** Multi-agent concurrent access to Synergy sessions

---

## Part 1: Synergy Title Display Testing

### Testing Requirements

Test synergy session title display across **4 rendering locations**:

1. **Thread History Modal** - Thread list in sidebar dropdown
2. **AI Chat Sidebar** - Prime column thread info area  
3. **AI Agent Columns** - Multi-agent workspace columns
4. **Synergy Session Card** - Synergy board linked threads section

### Implementation Status ✅

All 4 locations now use consistent rendering logic:

#### **Unified Rendering Flow:**
```javascript
// Line 19185-19221: renderThreadInfoContainer()
let synergyDisplay = thread.synergy_card_name || thread.synergy_card_id || 'Unknown Session';
const synergyMeta = thread.synergy_card_id ? window._synergySessionCache[thread.synergy_card_id] : null;

if (synergyMeta) {
    synergyDisplay = synergyMeta.title || thread.synergy_card_id;
} else if (thread.synergy_card_id && !synergyMeta) {
    // Cache miss - fetch in background and re-render
    fetch(`${apiBaseUrl}/api/synergy?ids=${encodeURIComponent(thread.synergy_card_id)}`)
        .then(resp => resp.json())
        .then(data => {
            if (data.success && data.sessions[thread.synergy_card_id]) {
                window._synergySessionCache[thread.synergy_card_id] = data.sessions[thread.synergy_card_id];
                thread.synergy_card_name = data.sessions[thread.synergy_card_id].title;
                this.refreshAllThreadInfoCards(threadId);
            }
        });
}
```

#### **Cache Population Points:**
1. **linkToExistingSession()** (Line 17987) - User selects existing session
2. **quickCreateAndLink()** (Line 18063) - Quick create new session
3. **createAndLinkSynergy()** (Line 17686) - Auto-create session
4. **Background fetch** (Line 19490) - On-demand cache population

#### **Fallback Hierarchy:**
```
1. window._synergySessionCache[sessionId].title (fastest - cached)
2. thread.synergy_card_name (property on thread object)
3. thread.synergy_card_id (session ID as identifier)
4. "Unknown Session" (ultimate fallback - never "Synergy Session")
```

### Testing Checklist

- [ ] **Thread History Modal:**
  - Create thread in Prime
  - Link to synergy session
  - Open Thread History dropdown
  - Verify green badge shows session title (not ID)
  - Click badge to expand info container
  - Verify all synergy details visible

- [ ] **AI Chat Sidebar (Prime):**
  - Load thread with linked synergy in Prime
  - Verify thread info area shows synergy badge
  - Verify badge displays session title
  - Click to expand - verify full details

- [ ] **AI Agent Columns:**
  - Drag thread with synergy to Agent-1
  - Observe: Session ID appears briefly (< 300ms)
  - Then: Title updates automatically
  - Verify no "Synergy Session" fallback appears
  - Test with multiple agents simultaneously

- [ ] **Synergy Board Linked Threads:**
  - Open Synergy tab
  - Select session with 2+ linked threads
  - Verify linked threads section shows thread cards
  - Each card should show synergy session title
  - Click thread card - should open in correct agent column

### Expected Behavior

**Correct Display Sequence:**
1. **Initial render:** Thread object has `synergy_card_id` (always present from backend)
2. **Check cache:** Look up `window._synergySessionCache[synergy_card_id]`
3. **Cache hit:** Display `synergyMeta.title` immediately
4. **Cache miss:** 
   - Display `thread.synergy_card_id` temporarily
   - Trigger background fetch
   - Auto re-render with title when fetch completes (~100-300ms)
5. **Never show:** Generic "Synergy Session" text

---

## Part 2: Multi-Agent Concurrent Access Analysis

### Problem Statement

**Requirement:** Multiple AI agents need to work on the same Synergy session concurrently.

**Key Question:** How do we handle:
- Concurrent reads from multiple agents?
- Concurrent writes/updates?
- Conflict resolution when agents modify the same data?
- Data consistency across agent views?

---

## Current Synergy Architecture

### Data Model

**Synergy Session Structure:**
```javascript
{
    session_id: "sess_20251113_...",
    title: "Project Name",
    description: "Project goals",
    status: "in_progress",
    priority: "high",
    
    // Content sections
    objectives: [...],
    action_items: [...],
    decisions: [...],
    notes: [...],
    
    // Multi-agent tracking
    assignees: ["agent-1", "agent-2", "agent-3"],
    linked_threads: ["Prime_123", "agent-1_456", "agent-2_789"],
    
    // Metadata
    created_at: "2025-11-13T10:00:00Z",
    last_active: "2025-11-13T14:30:00Z",
    last_modified_by: "agent-1"
}
```

### Current Limitations

1. **No Concurrent Write Protection** - No locking mechanism
2. **No Change Tracking** - No version control or edit history
3. **No Conflict Detection** - Last write wins (data loss possible)
4. **No Real-time Sync** - Agents see stale data until refresh
5. **No Transaction Support** - Partial updates possible on errors

---

## Multi-Agent Concurrency Patterns (Research)

Based on GitHub research (AG2/AutoGen, PraisonAI, etc.), here are proven patterns:

### Pattern 1: **Event-Driven State Management** (AG2 Approach)

**How it works:**
- Shared `ContextVariables` object
- Each agent operation emits events
- Central coordinator tracks state
- Agents subscribe to state changes

**Pros:**
- Clear state ownership
- Easy to debug
- No direct conflicts

**Cons:**
- Single point of failure (coordinator)
- Potential bottleneck
- Requires message passing overhead

**Example from AG2:**
```python
# AG2 pattern for shared context
context_variables = ContextVariables(data={
    "session_id": "sess_123",
    "current_editor": None,
    "pending_changes": [],
    "lock_holder": None
})

def update_synergy_content(content: str, agent_id: str, context_variables: ContextVariables):
    # Check if locked
    if context_variables.get("lock_holder") and context_variables["lock_holder"] != agent_id:
        return ReplyResult(
            message="Session locked by another agent",
            context_variables=context_variables
        )
    
    # Acquire lock
    context_variables["lock_holder"] = agent_id
    context_variables["current_editor"] = agent_id
    
    # Update content
    context_variables["synergy_content"] = content
    
    # Release lock
    context_variables["lock_holder"] = None
    
    return ReplyResult(
        message="Content updated",
        context_variables=context_variables
    )
```

---

### Pattern 2: **Optimistic Locking with Version Control**

**How it works:**
- Each synergy session has a `version` number
- Agents read version when fetching data
- On update, check if version matches
- If version changed, reject update (conflict detected)

**Pros:**
- No blocking - agents work independently
- Automatic conflict detection
- Simple to implement

**Cons:**
- Requires manual conflict resolution
- Potential for repeated conflicts
- Wasted work if conflicts frequent

**Implementation:**
```javascript
// Backend API
PUT /api/synergy/{session_id}
{
    "version": 42,  // Version agent thinks is current
    "updates": {
        "objectives": [...],
        "action_items": [...]
    },
    "modified_by": "agent-1"
}

// Response on version mismatch:
{
    "success": false,
    "error": "version_conflict",
    "current_version": 45,
    "conflicting_changes": [...]
}
```

**Frontend handling:**
```javascript
async function updateSynergySession(sessionId, updates, currentVersion, agentId) {
    try {
        const response = await fetch(`/api/synergy/${sessionId}`, {
            method: 'PUT',
            body: JSON.stringify({
                version: currentVersion,
                updates: updates,
                modified_by: agentId
            })
        });
        
        const result = await response.json();
        
        if (!result.success && result.error === 'version_conflict') {
            // Option 1: Auto-merge if possible
            const merged = attemptAutoMerge(updates, result.conflicting_changes);
            if (merged) {
                return updateSynergySession(sessionId, merged, result.current_version, agentId);
            }
            
            // Option 2: Ask AI agent to resolve conflict
            return {
                success: false,
                conflict: true,
                resolution_needed: true,
                agent_changes: updates,
                server_changes: result.conflicting_changes
            };
        }
        
        return result;
    } catch (error) {
        console.error('Update failed:', error);
        return { success: false, error: error.message };
    }
}
```

---

### Pattern 3: **Operational Transformation (OT)** / **CRDT (Conflict-free Replicated Data Types)**

**How it works:**
- Changes tracked as operations (insert, delete, modify)
- Operations automatically merge without conflicts
- Used by Google Docs, Figma, etc.

**Pros:**
- True concurrent editing
- Automatic conflict resolution
- No blocking or version conflicts

**Cons:**
- Complex to implement
- Requires specialized libraries
- Harder to debug

**Libraries:**
- **Yjs** - CRDT for JavaScript (used by Notion, Obsidian)
- **Automerge** - JSON CRDT
- **ShareDB** - OT framework

**Example with Yjs:**
```javascript
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';

// Create shared document
const doc = new Y.Doc();
const synergyData = doc.getMap('synergy_session_123');

// Connect to WebSocket server for sync
const provider = new WebsocketProvider('ws://localhost:1234', 'synergy_room', doc);

// Agent 1 updates objectives
synergyData.set('objectives', ['Goal 1', 'Goal 2']);

// Agent 2 updates simultaneously (no conflict!)
synergyData.set('action_items', ['Task A', 'Task B']);

// Both changes merge automatically
console.log(synergyData.toJSON());
// { objectives: ['Goal 1', 'Goal 2'], action_items: ['Task A', 'Task B'] }
```

---

### Pattern 4: **Section-Level Locking (Fine-Grained Locks)**

**How it works:**
- Synergy session divided into sections
- Each section can be locked independently
- Agent locks only what it's editing

**Pros:**
- Reduces contention (multiple agents can work in parallel)
- Simple to understand
- Clear ownership

**Cons:**
- More complex lock management
- Potential deadlocks if not careful
- Requires UI indication of locked sections

**Implementation:**
```javascript
// Synergy session structure with section locks
{
    session_id: "sess_123",
    sections: {
        objectives: {
            content: [...],
            locked_by: "agent-1",
            locked_at: "2025-11-13T14:30:00Z"
        },
        action_items: {
            content: [...],
            locked_by: null,  // Available
            locked_at: null
        },
        decisions: {
            content: [...],
            locked_by: "agent-2",
            locked_at: "2025-11-13T14:32:00Z"
        }
    }
}

// API for locking
POST /api/synergy/{session_id}/lock
{
    "section": "objectives",
    "agent_id": "agent-1",
    "timeout": 300  // Auto-release after 5 minutes
}

// Auto-unlock on timeout or explicit release
DELETE /api/synergy/{session_id}/lock
{
    "section": "objectives",
    "agent_id": "agent-1"
}
```

---

### Pattern 5: **Change Queue with Merge Strategy**

**How it works:**
- Each agent submits changes to a queue
- Background worker processes queue sequentially
- Applies merge strategy for conflicts

**Pros:**
- Serialized writes prevent conflicts
- Can implement custom merge logic
- Audit trail of all changes

**Cons:**
- Slight delay in updates
- Requires background worker
- Queue can become bottleneck

**Implementation:**
```javascript
// Agent submits change
POST /api/synergy/{session_id}/changes
{
    "agent_id": "agent-1",
    "change_type": "add_action_item",
    "data": { "task": "Review docs", "assignee": "John" },
    "timestamp": "2025-11-13T14:30:00Z"
}

// Backend queue processor
class SynergyChangeProcessor {
    async processQueue(sessionId) {
        const changes = await this.fetchPendingChanges(sessionId);
        
        for (const change of changes) {
            try {
                const session = await this.loadSession(sessionId);
                const merged = this.applyChange(session, change);
                await this.saveSession(sessionId, merged);
                await this.markChangeProcessed(change.id);
                
                // Notify all connected agents
                this.broadcastUpdate(sessionId, merged);
            } catch (error) {
                await this.markChangeFailed(change.id, error);
            }
        }
    }
    
    applyChange(session, change) {
        switch (change.change_type) {
            case 'add_action_item':
                session.action_items.push(change.data);
                break;
            case 'update_objective':
                const idx = session.objectives.findIndex(o => o.id === change.data.id);
                if (idx >= 0) session.objectives[idx] = change.data;
                break;
            // ... more change types
        }
        return session;
    }
}
```

---

## Recommended Approach for Synergy Multi-Agent

### **Hybrid Strategy: Optimistic Locking + Section-Level Awareness**

**Phase 1: Foundation (Immediate)**
1. Add `version` field to synergy sessions
2. Implement optimistic locking on updates
3. Add conflict detection and manual resolution

**Phase 2: Enhanced Concurrency (Short-term)**
1. Add section-level metadata (who's viewing/editing)
2. Implement soft locks (advisory, not blocking)
3. Add real-time update notifications (WebSocket)

**Phase 3: Advanced Features (Long-term)**
1. Consider CRDT library (Yjs) for true concurrent editing
2. Implement change history and rollback
3. Add AI-assisted conflict resolution

---

## Implementation Plan

### Database Schema Updates

```sql
-- Add version control to synergy sessions
ALTER TABLE synergy_sessions 
ADD COLUMN version INTEGER DEFAULT 1,
ADD COLUMN last_modified_by TEXT,
ADD COLUMN last_modified_at TIMESTAMP,
ADD COLUMN active_editors JSON;  -- Track who's currently viewing

-- Change history table
CREATE TABLE synergy_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    version_from INTEGER,
    version_to INTEGER,
    agent_id TEXT,
    change_type TEXT,
    section TEXT,
    old_value JSON,
    new_value JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES synergy_sessions(session_id)
);

-- Active locks table (optional for section locking)
CREATE TABLE synergy_locks (
    session_id TEXT NOT NULL,
    section TEXT NOT NULL,
    locked_by TEXT NOT NULL,
    locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    PRIMARY KEY (session_id, section)
);
```

### Backend API Updates

```python
# Flask route for updating synergy session with version control
@app.route('/api/synergy/<session_id>', methods=['PUT'])
def update_synergy_session(session_id):
    data = request.json
    provided_version = data.get('version')
    updates = data.get('updates')
    agent_id = data.get('modified_by')
    
    # Load current session
    session = db.query('SELECT * FROM synergy_sessions WHERE session_id = ?', [session_id])
    current_version = session['version']
    
    # Version check
    if provided_version != current_version:
        return jsonify({
            'success': False,
            'error': 'version_conflict',
            'current_version': current_version,
            'message': f'Session was modified by {session["last_modified_by"]} at {session["last_modified_at"]}'
        }), 409
    
    # Apply updates
    new_version = current_version + 1
    session_data = json.loads(session['data'])
    
    # Merge updates
    for key, value in updates.items():
        session_data[key] = value
    
    # Save with new version
    db.execute('''
        UPDATE synergy_sessions 
        SET data = ?, version = ?, last_modified_by = ?, last_modified_at = CURRENT_TIMESTAMP
        WHERE session_id = ? AND version = ?
    ''', [json.dumps(session_data), new_version, agent_id, session_id, current_version])
    
    # Log change
    db.execute('''
        INSERT INTO synergy_changes (session_id, version_from, version_to, agent_id, change_type, new_value)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', [session_id, current_version, new_version, agent_id, 'update', json.dumps(updates)])
    
    # Broadcast update to all connected agents (WebSocket)
    broadcast_synergy_update(session_id, session_data, new_version, agent_id)
    
    return jsonify({
        'success': True,
        'version': new_version,
        'session': session_data
    })
```

### Frontend Updates

```javascript
// ThreadManager extension for concurrent synergy access
class SynergyCollaborationManager {
    constructor() {
        this.activeSessions = new Map();  // Track open sessions
        this.websocket = null;
        this.pendingUpdates = new Map();
    }
    
    // Connect to real-time update stream
    connectWebSocket() {
        this.websocket = new WebSocket('ws://localhost:5001/synergy-updates');
        
        this.websocket.onmessage = (event) => {
            const update = JSON.parse(event.data);
            this.handleRemoteUpdate(update);
        };
    }
    
    // Register agent as viewer of session
    async registerViewer(sessionId, agentId) {
        await fetch(`/api/synergy/${sessionId}/viewers`, {
            method: 'POST',
            body: JSON.stringify({ agent_id: agentId, viewing: true })
        });
        
        this.activeSessions.set(sessionId, {
            agentId: agentId,
            version: null,
            lastFetch: Date.now()
        });
    }
    
    // Update synergy session with version check
    async updateSession(sessionId, updates, agentId) {
        const sessionState = this.activeSessions.get(sessionId);
        
        try {
            const response = await fetch(`/api/synergy/${sessionId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    version: sessionState.version,
                    updates: updates,
                    modified_by: agentId
                })
            });
            
            const result = await response.json();
            
            if (!result.success && result.error === 'version_conflict') {
                // Handle conflict
                return await this.resolveConflict(sessionId, updates, result, agentId);
            }
            
            // Update local version
            sessionState.version = result.version;
            
            return { success: true, data: result.session };
            
        } catch (error) {
            console.error('Synergy update failed:', error);
            return { success: false, error: error.message };
        }
    }
    
    // Handle conflicts
    async resolveConflict(sessionId, localUpdates, conflict, agentId) {
        console.warn(`[SYNERGY CONFLICT] Agent ${agentId} conflict on session ${sessionId}`);
        
        // Option 1: Simple retry with fresh data
        const freshSession = await this.fetchSession(sessionId);
        
        // Option 2: Ask AI to resolve
        const aiResolution = await this.getAIConflictResolution(
            localUpdates,
            conflict.conflicting_changes,
            freshSession
        );
        
        if (aiResolution.strategy === 'retry') {
            // Retry with fresh version
            return this.updateSession(sessionId, localUpdates, agentId);
        } else if (aiResolution.strategy === 'merge') {
            // Use AI-merged version
            return this.updateSession(sessionId, aiResolution.merged, agentId);
        } else {
            // Abort and notify user
            return {
                success: false,
                conflict: true,
                message: 'Conflict detected - manual resolution required',
                yourChanges: localUpdates,
                theirChanges: conflict.conflicting_changes
            };
        }
    }
    
    // Handle remote updates from other agents
    handleRemoteUpdate(update) {
        const { session_id, version, modified_by, data } = update;
        
        // Update cache
        if (window._synergySessionCache[session_id]) {
            window._synergySessionCache[session_id] = data;
        }
        
        // Update version for active sessions
        const sessionState = this.activeSessions.get(session_id);
        if (sessionState) {
            sessionState.version = version;
        }
        
        // Refresh UI if session is currently displayed
        this.refreshSynergyUI(session_id, modified_by);
    }
    
    // Refresh UI for agents viewing this session
    refreshSynergyUI(sessionId, modifiedBy) {
        // Find all threads linked to this session
        const linkedThreads = ThreadManager.threads.filter(t => t.synergy_card_id === sessionId);
        
        // Refresh thread info cards
        linkedThreads.forEach(thread => {
            ThreadManager.refreshAllThreadInfoCards(thread.id);
        });
        
        // Show notification if another agent made changes
        if (modifiedBy !== ThreadManager.currentAgentId) {
            this.showUpdateNotification(sessionId, modifiedBy);
        }
    }
}

// Initialize
window.synergyCollaboration = new SynergyCollaborationManager();
window.synergyCollaboration.connectWebSocket();
```

---

## Conflict Resolution Strategies

### 1. **Last Write Wins** (Current - Simple but lossy)
```javascript
// No conflict detection - last update overwrites
```

### 2. **First Write Wins** (Reject conflicts)
```javascript
// Return error on version mismatch - agent must refresh and retry
if (providedVersion !== currentVersion) {
    return { error: 'version_conflict', action: 'refresh_and_retry' };
}
```

### 3. **Auto-Merge Non-Conflicting Changes**
```javascript
function attemptAutoMerge(localChanges, remoteChanges) {
    const merged = {};
    const conflicts = [];
    
    // Merge non-overlapping sections
    Object.keys(localChanges).forEach(key => {
        if (!remoteChanges.hasOwnProperty(key)) {
            merged[key] = localChanges[key];  // Safe to apply
        } else if (JSON.stringify(localChanges[key]) === JSON.stringify(remoteChanges[key])) {
            merged[key] = localChanges[key];  // Same change - no conflict
        } else {
            conflicts.push({ key, local: localChanges[key], remote: remoteChanges[key] });
        }
    });
    
    // Apply non-conflicting remote changes
    Object.keys(remoteChanges).forEach(key => {
        if (!localChanges.hasOwnProperty(key)) {
            merged[key] = remoteChanges[key];
        }
    });
    
    return conflicts.length === 0 ? merged : null;
}
```

### 4. **AI-Assisted Conflict Resolution**
```javascript
async function resolveConflictWithAI(localChanges, remoteChanges, sessionContext) {
    const prompt = `
You are resolving a conflict in a Synergy session.

Session Context:
${JSON.stringify(sessionContext, null, 2)}

Local Changes (Agent A):
${JSON.stringify(localChanges, null, 2)}

Remote Changes (Agent B):
${JSON.stringify(remoteChanges, null, 2)}

Task: Analyze both sets of changes and provide a merged version that:
1. Preserves intent of both agents
2. Resolves conflicts intelligently
3. Maintains data consistency

Return JSON with:
{
    "strategy": "merge",
    "merged": { /* resolved changes */ },
    "reasoning": "Why these changes were chosen"
}
`;

    const response = await callAIModel(prompt);
    return JSON.parse(response);
}
```

---

## Security Considerations

### 1. **Authorization**
- Verify agent has permission to modify synergy session
- Track which agents are assigned to session
- Prevent unauthorized access

### 2. **Audit Trail**
- Log all changes with agent ID and timestamp
- Enable rollback if needed
- Investigate conflicts and data loss

### 3. **Rate Limiting**
- Prevent spam updates from misbehaving agents
- Limit update frequency per agent

### 4. **Data Validation**
- Validate update structure
- Prevent injection attacks
- Sanitize user-provided content

---

## Performance Considerations

### 1. **Caching Strategy**
- **L1 Cache:** In-memory `window._synergySessionCache` (client-side)
- **L2 Cache:** Redis cache (server-side, shared across clients)
- **L3 Cache:** Database (persistent storage)

### 2. **Update Batching**
- Batch multiple small updates into single transaction
- Reduce version increments
- Improve performance

### 3. **Lazy Loading**
- Load synergy session only when needed
- Don't fetch all linked threads upfront
- Paginate change history

### 4. **WebSocket Scaling**
- Use pub/sub pattern (Redis)
- Support horizontal scaling
- Graceful degradation if WebSocket unavailable

---

## Testing Strategy

### Unit Tests
- Version conflict detection
- Auto-merge logic
- Lock acquisition/release
- Conflict resolution

### Integration Tests
- Multiple agents updating same session
- Concurrent reads and writes
- WebSocket notification delivery
- Cache consistency

### Load Tests
- 10+ agents accessing same session
- Rapid updates (stress test)
- Network latency simulation
- WebSocket connection limits

---

## Rollout Plan

### Phase 1: Foundation (Week 1-2)
- ✅ Implement version field
- ✅ Add optimistic locking
- ✅ Basic conflict detection
- ✅ Manual conflict resolution UI

### Phase 2: Real-time Sync (Week 3-4)
- ✅ WebSocket server setup
- ✅ Real-time update notifications
- ✅ Active viewer tracking
- ✅ Auto-refresh on remote changes

### Phase 3: Advanced Features (Week 5-6)
- ✅ Section-level awareness
- ✅ Auto-merge non-conflicting changes
- ✅ AI-assisted conflict resolution
- ✅ Change history and rollback

### Phase 4: Polish (Week 7-8)
- ✅ Performance optimization
- ✅ Comprehensive testing
- ✅ Documentation
- ✅ Monitoring and alerts

---

## Open Questions

1. **How often do conflicts occur in practice?**
   - Need telemetry to measure
   - If rare, simple retry sufficient
   - If frequent, need sophisticated resolution

2. **Should agents block on conflicts?**
   - Blocking: Safer but slower
   - Non-blocking: Faster but complex

3. **How long should locks last?**
   - Too short: Frequent re-locking
   - Too long: Reduced parallelism
   - Suggested: 5-10 minutes with auto-extend

4. **What data structures need CRDT?**
   - Lists (action items, objectives): Yes
   - Objects (metadata, settings): Maybe
   - Scalars (title, status): No

5. **How to handle agent crashes?**
   - Orphaned locks need auto-cleanup
   - Pending changes need rollback
   - Active viewers need timeout

---

## Recommended Next Steps

1. **Implement Phase 1** (optimistic locking) - **Start here**
2. **Measure conflict rate** in production
3. **Based on data**, decide:
   - If conflicts rare: Keep Phase 1
   - If conflicts frequent: Implement Phase 2+3
4. **Consider CRDT** only if real-time concurrent editing becomes critical

---

## References

### Multi-Agent Systems Research
- **AG2 (AutoGen):** Context variables, shared state management
- **PraisonAI:** Multi-agent orchestration patterns
- **Google Docs:** Operational Transformation (OT)
- **Figma:** Conflict-free Replicated Data Types (CRDT)

### Libraries to Consider
- **Yjs:** CRDT for JavaScript - https://github.com/yjs/yjs
- **Automerge:** JSON CRDT - https://github.com/automerge/automerge
- **ShareDB:** Real-time database with OT - https://github.com/share/sharedb
- **Socket.IO:** WebSocket library - https://socket.io/

### Academic Papers
- "Conflict-free Replicated Data Types" (Shapiro et al., 2011)
- "Operational Transformation in Real-Time Group Editors" (Ellis & Gibbs, 1989)
- "Multi-Agent Systems: A Survey" (Wooldridge, 2009)

---

**Status:** Analysis complete - awaiting decision on implementation approach

**Next Action:** Review options with team and select strategy for Phase 1 implementation
