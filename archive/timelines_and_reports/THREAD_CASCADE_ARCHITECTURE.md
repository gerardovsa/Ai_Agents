# Thread Assignment Cascade Architecture

**Date**: November 17, 2025  
**Status**: Implementation Guide  
**Purpose**: Implement database-first cascade pattern for thread assignments

---

## 🎯 Core Principle: Database is Source of Truth

**RULE**: Database ALWAYS updated FIRST, then UI cascades from database state.

```
┌─────────────────────────────────────────────────────────────┐
│  OLD PATTERN (BROKEN - UI/DB Mismatch)                     │
├─────────────────────────────────────────────────────────────┤
│  User Action → Update UI → Maybe Update Database           │
│  Result: Thread shows in Prime UI but DB says "agent-1"    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  NEW PATTERN (CASCADE - Database-First)                     │
├─────────────────────────────────────────────────────────────┤
│  User Action → Update Database → Cascade UI Updates         │
│  Result: DB and UI always in sync                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 sessions.threads Table - Single Source of Truth

**Table**: `sessions.threads`  
**Primary Key**: `id` (integer, auto-increment)  
**Unique Key**: `thread_slug` (text, unique)

### Core Fields (Always Required)
```sql
id                    INTEGER PRIMARY KEY      -- Internal ID
thread_slug           TEXT NOT NULL UNIQUE     -- External ID (used in UI)
name                  TEXT NOT NULL            -- Thread title
user_id               INTEGER                  -- Owner
created_at            TIMESTAMP                -- Creation time
updated_at            TIMESTAMP                -- Last modification
```

### Location & Assignment Fields
```sql
location              TEXT                     -- 'prime', 'agent-1', 'agent-2', 'agent-3'
workspace_id          INTEGER                  -- Workspace context
archived              INTEGER DEFAULT 0        -- 0=active, 1=archived
```

### UI Link Fields (Slugs for External Systems)
```sql
-- Synergy Session Link
synergy_card_id       TEXT                     -- Synergy session ID (UUID or slug)

-- Workflow Link
workflow_slug         TEXT                     -- Workflow identifier
workflow_title        TEXT                     -- Workflow display name

-- Internal Documentation Link
internal_doc_slug     TEXT                     -- Internal doc identifier
internal_doc_title    TEXT                     -- Internal doc display name
```

### Thread Management Fields
```sql
-- Branching/Forking
parent_thread_id      INTEGER                  -- Parent thread ID (for forks)
branch_name           TEXT                     -- Branch label
branch_point_message_id TEXT                   -- Message ID where branch occurred

-- Metadata
tags                  TEXT                     -- JSON array of tags
metadata              TEXT                     -- JSON object for custom data
token_count           INTEGER DEFAULT 0        -- Total tokens used

-- Locking (for collaborative editing)
locked_to_device_id   TEXT DEFAULT 'NULL'      -- Device ID holding lock
locked_at             TIMESTAMP                -- Lock acquisition time
lock_mode             TEXT DEFAULT 'unlocked'  -- 'unlocked', 'editing', 'readonly'
```

---

## 🔄 Cascade Pattern Implementation

### Phase 1: Database Update (ALWAYS FIRST)

```javascript
async function updateThreadLocation(threadId, newLocation) {
    // 1. UPDATE DATABASE FIRST
    const response = await fetch('/api/thread-assignments/assign', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            user_id: AppState.userId,
            session_id: threadId,
            location: newLocation
        })
    });
    
    if (!response.ok) {
        throw new Error('Database update failed');
    }
    
    const result = await response.json();
    
    // 2. CASCADE UI UPDATES (only after DB success)
    await cascadeUIUpdates(threadId, newLocation, result);
    
    return result;
}
```

### Phase 2: Cascade UI Updates (AFTER Database)

```javascript
async function cascadeUIUpdates(threadId, newLocation, dbResult) {
    const thread = ThreadManager.threads.find(t => t.id === threadId);
    if (!thread) return;
    
    // 2A. Clear OLD location UI
    if (dbResult.assignment.previous_location) {
        await clearLocationUI(dbResult.assignment.previous_location, threadId);
    }
    
    // 2B. Update thread object (in-memory state)
    thread.location = newLocation;
    thread.updated = new Date().toISOString();
    
    // 2C. Render NEW location UI
    await renderLocationUI(newLocation, threadId);
    
    // 2D. Refresh thread list sidebar
    ThreadManager.renderThreadList();
    
    // 2E. Update all thread-info cards (Prime + Agents + Synergy)
    ThreadManager.refreshAllThreadInfoCards(threadId);
}
```

### Phase 3: Clear Old Location UI

```javascript
async function clearLocationUI(oldLocation, threadId) {
    if (oldLocation === 'prime') {
        // Clear Prime panel
        AppState.sessionId = null;
        AppState.chatMessages = [];
        const messagesContainer = document.getElementById('ai-chat-messages');
        if (messagesContainer) messagesContainer.innerHTML = '';
        
        // Show welcome message
        const welcomeContainer = document.getElementById('prime-welcome-container');
        if (welcomeContainer) welcomeContainer.style.display = 'block';
        
    } else if (oldLocation.startsWith('agent-')) {
        // Clear Agent column
        const agentId = parseInt(oldLocation.replace('agent-', ''));
        MultiAgent.clearLoadedThread(agentId);
        
        // Update agent header to show "no thread"
        const headerEl = document.getElementById(`thread-info-${agentId}`);
        if (headerEl) {
            headerEl.innerHTML = ThreadManager.renderThreadInfoContainer(oldLocation, null, true);
        }
    }
    
    console.log(`✅ [CASCADE] Cleared UI for ${oldLocation}`);
}
```

### Phase 4: Render New Location UI

```javascript
async function renderLocationUI(newLocation, threadId) {
    const thread = ThreadManager.threads.find(t => t.id === threadId);
    if (!thread) return;
    
    if (newLocation === 'prime') {
        // Load thread in Prime
        await ThreadManager._loadThreadInPrimeUI(threadId);
        
    } else if (newLocation.startsWith('agent-')) {
        // Load thread in Agent column
        const agentId = parseInt(newLocation.replace('agent-', ''));
        await MultiAgent.loadThreadIntoAgent(agentId, thread);
    }
    
    console.log(`✅ [CASCADE] Rendered UI for ${newLocation}`);
}
```

---

## 🛠️ Implementation Fixes

### Fix 1: Update `assignThread()` - Database-First Pattern

**File**: `UI/business-ai-platform-v2.html`  
**Function**: `ThreadManager.assignThread()` (~Line 22622)

```javascript
async assignThread(threadId, location) {
    console.log(`📍 [assignThread] START: ${threadId} → ${location}`);
    
    try {
        // PHASE 1: UPDATE DATABASE FIRST
        const response = await fetch('/api/thread-assignments/assign', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: AppState.userId || 1,
                session_id: threadId,
                location: location || 'prime'
            })
        });
        
        if (!response.ok) {
            throw new Error(`Database update failed: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log(`✅ [assignThread] Database updated:`, data.assignment);
        
        // PHASE 2: CASCADE UI UPDATES (only after DB success)
        await this._cascadeThreadAssignment(threadId, location, data.assignment);
        
        return data;
        
    } catch (error) {
        console.error(`❌ [assignThread] Failed:`, error);
        if (typeof showNotification === 'function') {
            showNotification(`Failed to assign thread: ${error.message}`, 'error', 3000);
        }
        throw error;
    }
}

// New helper function: Cascade UI updates after database update
async _cascadeThreadAssignment(threadId, newLocation, assignment) {
    console.log(`🔄 [CASCADE] Starting UI updates for thread ${threadId}`);
    
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        console.warn(`[CASCADE] Thread not found: ${threadId}`);
        return;
    }
    
    // STEP 1: Clear OLD location UI
    if (assignment.previous_location) {
        console.log(`🧹 [CASCADE] Clearing ${assignment.previous_location}`);
        await this._clearLocationUI(assignment.previous_location, threadId);
    }
    
    // STEP 2: Handle DISPLACED thread (if any)
    if (assignment.displaced_thread) {
        console.log(`🔄 [CASCADE] Handling displaced thread: ${assignment.displaced_thread}`);
        const displacedThread = this.threads.find(t => t.id === assignment.displaced_thread);
        if (displacedThread) {
            // Displaced thread goes to Prime (backend already updated location)
            displacedThread.location = 'prime';
            displacedThread.agent = null;
            displacedThread.updated = new Date().toISOString();
            
            // Clear displaced thread from agent UI
            await this._clearLocationUI(newLocation, assignment.displaced_thread);
        }
    }
    
    // STEP 3: Update thread object (in-memory state)
    thread.location = newLocation;
    thread.agent = newLocation === 'prime' ? null : newLocation;
    thread.updated = new Date().toISOString();
    console.log(`✅ [CASCADE] Updated thread object: location=${newLocation}`);
    
    // STEP 4: Refresh UI components
    this.renderThreadList();  // Update sidebar
    this.refreshAllThreadInfoCards(threadId);  // Update thread-info cards
    
    console.log(`✅ [CASCADE] Complete for thread ${threadId}`);
}

// New helper function: Clear UI for old location
async _clearLocationUI(location, threadId) {
    if (location === 'prime') {
        // Clear Prime panel ONLY if this thread is loaded
        if (AppState.sessionId === threadId) {
            AppState.sessionId = null;
            AppState.chatMessages = [];
            
            const messagesContainer = document.getElementById('ai-chat-messages');
            if (messagesContainer) {
                messagesContainer.querySelectorAll('[data-processor-initialized]').forEach(bubble => {
                    if (bubble.processor && typeof bubble.processor.cleanup === 'function') {
                        bubble.processor.cleanup();
                    }
                });
                messagesContainer.innerHTML = '';
            }
            
            // Show welcome message
            const welcomeContainer = document.getElementById('prime-welcome-container');
            if (welcomeContainer) welcomeContainer.style.display = 'block';
            
            // Update Prime header
            const primeThreadInfo = document.getElementById('thread-info-prime');
            if (primeThreadInfo) {
                primeThreadInfo.innerHTML = this.renderThreadInfoContainer('prime', null, false);
            }
            
            console.log(`✅ [CASCADE] Cleared Prime UI (thread ${threadId})`);
        }
        
    } else if (location.startsWith('agent-')) {
        // Clear Agent column
        const agentId = parseInt(location.replace('agent-', ''));
        
        if (typeof MultiAgent !== 'undefined') {
            const loadedThread = MultiAgent.agents[agentId]?.loadedThread;
            
            // Clear ONLY if this thread is loaded in this agent
            if (loadedThread && loadedThread.threadId === threadId) {
                MultiAgent.clearLoadedThread(agentId);
                
                // Update agent header to show "no thread"
                const headerEl = document.getElementById(`thread-info-${agentId}`);
                if (headerEl) {
                    headerEl.innerHTML = this.renderThreadInfoContainer(location, null, true);
                }
                
                console.log(`✅ [CASCADE] Cleared ${location} UI (thread ${threadId})`);
            }
        }
    }
}
```

---

### Fix 2: Update `loadThreadInPrime()` - Use Cascade Pattern

**File**: `UI/business-ai-platform-v2.html`  
**Function**: `ThreadManager.loadThreadInPrime()` (~Line 24019)

```javascript
async loadThreadInPrime(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        console.error(`[loadThreadInPrime] Thread not found: ${threadId}`);
        return;
    }
    
    // PHASE 1: UPDATE DATABASE FIRST (assign to Prime)
    console.log(`🔄 [loadThreadInPrime] Assigning thread to Prime: ${threadId}`);
    
    try {
        // This updates database and cascades UI changes
        await this.assignThread(threadId, 'prime');
        console.log(`✅ [loadThreadInPrime] Database updated, now loading UI`);
        
    } catch (error) {
        console.error(`❌ [loadThreadInPrime] Failed to assign thread:`, error);
        return;  // Don't proceed if database update fails
    }
    
    // PHASE 2: LOAD THREAD IN PRIME UI (after database success)
    await this._loadThreadInPrimeUI(threadId);
}

// Extract UI loading logic to separate function (no database updates here)
async _loadThreadInPrimeUI(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;
    
    console.log(`🖥️ [_loadThreadInPrimeUI] Loading UI for thread: ${threadId}`);
    
    this.currentThreadId = threadId;
    
    // Clear attached files
    console.log('[CLEAN] Clearing attached files on thread switch...');
    if (window.clearChatAttachedFiles) {
        window.clearChatAttachedFiles();
    }
    
    // Clear messages container
    const messagesContainer = document.getElementById('ai-chat-messages');
    if (messagesContainer) {
        // Clean up processors
        messagesContainer.querySelectorAll('[data-processor-initialized]').forEach(bubble => {
            if (bubble.processor && typeof bubble.processor.cleanup === 'function') {
                bubble.processor.cleanup();
            }
        });
        messagesContainer.innerHTML = '';
    }
    
    // Ensure messages is always an array
    if (!Array.isArray(thread.messages)) {
        thread.messages = [];
    }
    
    // Hide welcome container
    const welcomeContainer = document.getElementById('prime-welcome-container');
    if (welcomeContainer) {
        welcomeContainer.style.display = 'none';
        console.log('[WELCOME] Hidden when thread loaded');
    }
    
    // Load messages from backend if not in memory
    if (!thread.messages || thread.messages.length === 0) {
        if (thread.message_count > 0) {
            console.log(`[THREAD LOAD] Loading ${thread.message_count} messages from backend...`);
            
            try {
                const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/${threadId}`);
                const data = await response.json();
                
                if (data.success && data.thread && data.thread.conversation) {
                    const updatedThread = this.threads.find(t => t.id === threadId);
                    if (updatedThread) {
                        updatedThread.messages = data.thread.conversation;
                        data.thread.conversation.forEach(msg => {
                            addChatMessage(msg.role, msg.content);
                        });
                        
                        // Update AppState
                        if (typeof AppState !== 'undefined') {
                            AppState.chatMessages = [...updatedThread.messages];
                            AppState.sessionId = threadId;
                        }
                    }
                }
            } catch (error) {
                console.error('[THREAD LOAD] Failed to load messages:', error);
            }
        }
    } else {
        // Messages already in memory
        if (Array.isArray(thread.messages) && thread.messages.length > 0) {
            thread.messages.forEach(msg => {
                addChatMessage(msg.role, msg.content);
            });
            
            // Update AppState
            if (typeof AppState !== 'undefined') {
                AppState.chatMessages = [...thread.messages];
                AppState.sessionId = threadId;
            }
        }
    }
    
    // Update Prime header
    this.updatePrimeHeader(threadId);
    this.syncAppState(threadId);
    
    // Show Prime input wrapper
    const primeInputWrapper = document.querySelector('.ai-chat-input-wrapper');
    if (primeInputWrapper) {
        primeInputWrapper.style.display = 'flex';
        console.log('[UI] Showed Prime input wrapper (thread switched)');
    }
    
    const primeSendBtn = document.querySelector('.ai-chat-send-btn');
    if (primeSendBtn) {
        primeSendBtn.disabled = false;
        primeSendBtn.style.opacity = '1';
        primeSendBtn.style.cursor = 'pointer';
    }
    
    console.log(`[ENABLED] Input enabled for Prime`);
    
    this.renderThreadList();
    this.closeThreadMenu();
}
```

---

### Fix 3: Update `switchThread()` - Always Use Database-First

**File**: `UI/business-ai-platform-v2.html`  
**Function**: `ThreadManager.switchThread()` (~Line 23986)

```javascript
async switchThread(threadId, forceSwitch = false) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        console.warn(`[switchThread] Thread not found: ${threadId}`);
        return;
    }
    
    console.log(`🔄 [switchThread] Switching to thread ${threadId}, force=${forceSwitch}`);
    
    // Check thread assignment via backend (more accurate than thread.agent)
    if (!forceSwitch) {
        const location = await this.getThreadLocation(threadId);
        
        // If assigned to an agent (not Prime), show options modal
        if (location && location.startsWith('agent-')) {
            const agentIdMatch = location.match(/agent-(\d+)/);
            if (agentIdMatch) {
                const agentId = parseInt(agentIdMatch[1]);
                const threadItem = document.querySelector(`[data-thread-id="${threadId}"]`);
                
                console.log(`📍 [switchThread] Thread ${threadId} is assigned to ${location}, showing inline options`);
                
                // Show assignment options modal (user chooses action)
                if (threadItem) {
                    this.showThreadAssignmentOptions(threadId, agentId, threadItem);
                }
                return; // Don't proceed with normal switch
            }
        }
        
        // If assigned to Prime or no assignment, load directly in Prime
        console.log(`✅ [switchThread] Thread ${threadId} location: ${location || 'none'}, loading in Prime`);
    }
    
    // Load thread in Prime (assignThread() handles database update)
    await this.loadThreadInPrime(threadId);
}
```

---

### Fix 4: Update `openThreadInPrime()` - Remove Force Mode

**File**: `UI/business-ai-platform-v2.html`  
**Function**: `ThreadManager.openThreadInPrime()` (~Line 24319)

```javascript
async openThreadInPrime(threadId) {
    console.log('📖 [openThreadInPrime] Opening thread in Prime AI:', threadId);
    
    // Switch to Prime tab
    const primeTab = document.querySelector('[data-chat-id="prime"]');
    if (primeTab) primeTab.click();
    
    // Use proper switchThread (checks location, shows modal if needed)
    await this.switchThread(threadId);
    
    this.closeThreadMenu();
    
    if (typeof showNotification === 'function') {
        showNotification('Thread opened in Prime AI', 'success', 2000);
    }
}
```

---

### Fix 5: Update `loadThreadIntoAgent()` - Database-First

**File**: `UI/business-ai-platform-v2.html`  
**Function**: `MultiAgent.loadThreadIntoAgent()` (~Line 19366)

```javascript
async loadThreadIntoAgent(agentId, thread) {
    console.log(`📥 [loadThreadIntoAgent] Loading thread "${thread.title}" into agent ${agentId}`);
    
    // PHASE 1: UPDATE DATABASE FIRST (assign to agent)
    const location = `agent-${agentId}`;
    
    try {
        await ThreadManager.assignThread(thread.id, location);
        console.log(`✅ [loadThreadIntoAgent] Database updated, thread assigned to ${location}`);
        
    } catch (error) {
        console.error(`❌ [loadThreadIntoAgent] Failed to assign thread:`, error);
        return;  // Don't proceed if database update fails
    }
    
    // PHASE 2: LOAD THREAD IN AGENT UI (after database success)
    await this._loadThreadIntoAgentUI(agentId, thread);
}

// Extract UI loading logic (no database updates here)
async _loadThreadIntoAgentUI(agentId, thread) {
    console.log(`🖥️ [_loadThreadIntoAgentUI] Loading UI for agent ${agentId}`);
    
    // Get messages container
    const messagesContainer = document.querySelector(`#agent-${agentId} .agent-messages-container`);
    if (!messagesContainer) {
        console.error(`[_loadThreadIntoAgentUI] Messages container not found for agent ${agentId}`);
        return;
    }
    
    // Clear container
    messagesContainer.innerHTML = '';
    
    // Render messages
    if (thread.messages && thread.messages.length > 0) {
        thread.messages.forEach(msg => {
            this._renderAgentMessage(agentId, msg.role, msg.content);
        });
    } else {
        // Load messages from backend if not in memory
        if (thread.message_count > 0) {
            console.log(`[AGENT LOAD] Loading ${thread.message_count} messages from backend...`);
            
            try {
                const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/${thread.id}`);
                const data = await response.json();
                
                if (data.success && data.thread && data.thread.conversation) {
                    thread.messages = data.thread.conversation;
                    data.thread.conversation.forEach(msg => {
                        this._renderAgentMessage(agentId, msg.role, msg.content);
                    });
                }
            } catch (error) {
                console.error('[AGENT LOAD] Failed to load messages:', error);
            }
        }
    }
    
    // Update agent state
    if (!this.agents[agentId]) {
        this.agents[agentId] = {};
    }
    this.agents[agentId].loadedThread = {
        threadId: thread.id,
        title: thread.title,
        messages: thread.messages || []
    };
    
    // Update thread-info header
    const threadInfoEl = document.getElementById(`thread-info-${agentId}`);
    if (threadInfoEl && typeof ThreadManager !== 'undefined') {
        threadInfoEl.innerHTML = ThreadManager.renderThreadInfoContainer(`agent-${agentId}`, thread.id, true);
    }
    
    // Enable agent input
    const agentInput = document.querySelector(`#agent-${agentId} .agent-input-area textarea`);
    if (agentInput) {
        agentInput.disabled = false;
        agentInput.placeholder = `Message ${this.getAgentName(agentId)}...`;
    }
    
    const agentSendBtn = document.querySelector(`#agent-${agentId} .agent-send-btn`);
    if (agentSendBtn) {
        agentSendBtn.disabled = false;
        agentSendBtn.style.opacity = '1';
        agentSendBtn.style.cursor = 'pointer';
    }
    
    console.log(`✅ [_loadThreadIntoAgentUI] Agent ${agentId} UI loaded with thread ${thread.id}`);
}
```

---

## 🔄 PostgreSQL Realtime & Triggers

### Option 1: PostgreSQL NOTIFY/LISTEN (Lightweight)

**Backend**: Listen for database changes and push via WebSocket

```python
# AI_infrastructure/routes/thread_routes.py

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_thread_change_trigger():
    """Setup PostgreSQL trigger to notify on thread changes"""
    conn = get_database_connection('sessions')
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Create trigger function
    cursor.execute("""
        CREATE OR REPLACE FUNCTION notify_thread_change()
        RETURNS trigger AS $$
        BEGIN
            PERFORM pg_notify(
                'thread_changes',
                json_build_object(
                    'thread_id', NEW.thread_slug,
                    'location', NEW.location,
                    'updated_at', NEW.updated_at::text
                )::text
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger
    cursor.execute("""
        DROP TRIGGER IF EXISTS thread_change_trigger ON sessions.threads;
        CREATE TRIGGER thread_change_trigger
        AFTER UPDATE OF location ON sessions.threads
        FOR EACH ROW
        EXECUTE FUNCTION notify_thread_change();
    """)
    
    conn.close()
    print("✅ Thread change trigger created")


# Listen for notifications
def listen_for_thread_changes():
    """Background thread to listen for database notifications"""
    conn = psycopg2.connect(get_database_connection_string('sessions'))
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute("LISTEN thread_changes;")
    
    print("🔔 Listening for thread changes...")
    
    while True:
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            payload = json.loads(notify.payload)
            
            # Push to all connected WebSocket clients
            broadcast_thread_change(payload)
            print(f"📢 Broadcast: Thread {payload['thread_id']} → {payload['location']}")
```

**Frontend**: Listen for WebSocket updates and refresh UI

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:5001/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'thread_change') {
        console.log(`🔔 [REALTIME] Thread ${data.thread_id} moved to ${data.location}`);
        
        // Refresh thread info cards
        ThreadManager.refreshAllThreadInfoCards(data.thread_id);
        
        // Refresh thread list
        ThreadManager.renderThreadList();
    }
};
```

---

### Option 2: Supabase Realtime (If Using Supabase)

```javascript
// Subscribe to thread changes
const threadChanges = supabase
    .channel('thread-changes')
    .on(
        'postgres_changes',
        {
            event: 'UPDATE',
            schema: 'sessions',
            table: 'threads',
            filter: `location=neq.NULL`
        },
        (payload) => {
            console.log(`🔔 [REALTIME] Thread ${payload.new.thread_slug} → ${payload.new.location}`);
            
            // Update UI
            ThreadManager.refreshAllThreadInfoCards(payload.new.thread_slug);
            ThreadManager.renderThreadList();
        }
    )
    .subscribe();
```

---

### Option 3: Polling (Simple, No Websocket)

```javascript
// Poll for thread updates every 5 seconds
setInterval(async () => {
    // Only check threads currently loaded in UI
    const loadedThreadIds = [
        AppState.sessionId,  // Prime thread
        ...Object.values(MultiAgent.agents)
            .filter(a => a.loadedThread)
            .map(a => a.loadedThread.threadId)
    ].filter(Boolean);
    
    if (loadedThreadIds.length === 0) return;
    
    // Fetch latest thread locations from backend
    const response = await fetch('/api/thread-assignments/check', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({thread_ids: loadedThreadIds})
    });
    
    const data = await response.json();
    
    // Compare with current UI state
    data.threads.forEach(thread => {
        const expectedLocation = thread.location;
        const actualLocation = ThreadManager.getThreadCurrentLocation(thread.thread_slug);
        
        if (expectedLocation !== actualLocation) {
            console.warn(`⚠️ [SYNC] Thread ${thread.thread_slug} out of sync!`);
            console.log(`  Expected: ${expectedLocation}, Actual: ${actualLocation}`);
            
            // Auto-fix: Cascade updates
            ThreadManager.assignThread(thread.thread_slug, expectedLocation);
        }
    });
}, 5000);
```

---

## 📋 Migration Checklist

### Backend Changes
- [ ] Add `location` column to `sessions.threads` table (already exists)
- [ ] Update `/api/thread-assignments/assign` endpoint (already exists)
- [ ] Add `/api/thread-assignments/check` endpoint for polling
- [ ] (Optional) Setup PostgreSQL NOTIFY/LISTEN trigger
- [ ] (Optional) Add WebSocket support for realtime updates

### Frontend Changes
- [ ] Update `ThreadManager.assignThread()` - Database-first pattern
- [ ] Update `ThreadManager.loadThreadInPrime()` - Call assignThread() first
- [ ] Update `ThreadManager.switchThread()` - Remove forceSwitch bypass
- [ ] Update `ThreadManager.openThreadInPrime()` - Remove force mode
- [ ] Update `MultiAgent.loadThreadIntoAgent()` - Database-first pattern
- [ ] Add `ThreadManager._cascadeThreadAssignment()` helper
- [ ] Add `ThreadManager._clearLocationUI()` helper
- [ ] Add `ThreadManager._loadThreadInPrimeUI()` helper (extract existing code)
- [ ] Add `MultiAgent._loadThreadIntoAgentUI()` helper (extract existing code)
- [ ] (Optional) Add WebSocket listener for realtime updates
- [ ] (Optional) Add polling for thread location sync

### Testing
- [ ] Test: Drag thread from Prime to Agent-1 (database updated first, UI cascades)
- [ ] Test: Double-click thread in Agent-1 (shows modal, updates database on confirm)
- [ ] Test: Drag thread from Agent-1 to Agent-2 (displacement works correctly)
- [ ] Test: Load thread via URL (deep link assigns to Prime first)
- [ ] Test: Multiple users editing same thread (location changes propagate via realtime)
- [ ] Test: Browser refresh (UI loads from database state)
- [ ] Test: Verify database with SQL queries after each action

---

## 🎯 Benefits of Cascade Architecture

### 1. **Single Source of Truth**
- Database is ALWAYS authoritative
- No UI/DB mismatches
- Easy to debug (just check database)

### 2. **Auditability**
- All changes logged in database
- Can track thread movements over time
- Can implement "undo" by reverting database state

### 3. **Multi-Device Sync**
- User opens thread on Desktop → assigns to Agent-1
- User switches to Laptop → sees thread in Agent-1 (loaded from DB)
- Realtime updates keep all devices in sync

### 4. **Consistency Across UI Components**
- Thread list sidebar → reads from database
- Thread-info cards → read from database
- Agent columns → read from database
- All show same location (no stale state)

### 5. **Simplified Debugging**
- Problem: Thread showing in wrong location
- Solution: Check database → `SELECT location FROM sessions.threads WHERE thread_slug='XXX'`
- Fix: Update database → UI automatically cascades

---

## 🔍 Verification SQL Queries

```sql
-- Check thread location
SELECT thread_slug, name, location, updated_at 
FROM sessions.threads 
WHERE thread_slug = 'YOUR_THREAD_ID';

-- Check all assigned threads
SELECT thread_slug, name, location 
FROM sessions.threads 
WHERE location IS NOT NULL 
AND location != 'prime'
ORDER BY updated_at DESC;

-- Check thread assignment history (if using thread_assignments table)
SELECT thread_slug, location, assigned_at, updated_at 
FROM sessions.thread_assignments 
WHERE thread_slug = 'YOUR_THREAD_ID' 
ORDER BY updated_at DESC;

-- Find threads in multiple locations (should be zero!)
SELECT thread_slug, COUNT(DISTINCT location) as location_count
FROM sessions.threads
WHERE location IS NOT NULL
GROUP BY thread_slug
HAVING COUNT(DISTINCT location) > 1;
```

---

## 📚 Summary

**Before**: UI updates, maybe database updates, mismatch chaos  
**After**: Database updates FIRST, UI cascades automatically, perfect sync

**Key Pattern**: `assignThread()` → Database → Cascade → UI

**Benefit**: One thread, one place, always in sync, no exceptions.

---

**Status**: Ready for Implementation  
**Next Steps**: Apply fixes to `business-ai-platform-v2.html` and test cascade pattern
