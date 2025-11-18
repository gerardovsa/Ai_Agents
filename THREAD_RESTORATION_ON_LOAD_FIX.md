# Thread Restoration on Page Load - Current Behavior & Fix Needed

**Date:** November 18, 2025  
**Issue:** Threads assigned to agents aren't being restored on page load  
**Root Cause:** Using `/api/thread-assignments` endpoint instead of `thread.location` field

---

## 🔍 Current Page Load Flow

### 1. DOMContentLoaded Event (Line 17561)
```javascript
document.addEventListener('DOMContentLoaded', async () => {
    const isAuthenticated = await UserAuth.checkExistingSession();
    if (isAuthenticated) {
        await UserAuth.showMainApp();
    }
});
```

### 2. showMainApp() → initializeMainApp() (Line 32109)
```javascript
await window.initializeMainApp();
```

### 3. initializeMainApp() Calls ThreadManager.init() (Line 17435)
```javascript
await ThreadManager.init();

// THEN restores thread assignments:
if (typeof MultiAgent !== 'undefined' && MultiAgent.restoreThreadAssignments) {
    MultiAgent.restoreThreadAssignments();
}
```

### 4. ThreadManager.init() Sequence (Line 25707)
```javascript
async init() {
    await this.ensureCorrectUserData();
    await this.loadThreadsFromBackend();  // ← Loads threads with location field
    this.initRealtimeSubscription();
    
    // Auto-load MOST RECENT thread into Prime (if any exist)
    if (this.threads.length > 0) {
        this.currentThreadId = this.threads[0].id;
        // Load into Prime chat...
    }
}
```

### 5. loadThreadsFromBackend() (Line 27461)
```javascript
// Loads from: GET /api/threads/list?user_id=1
// Response includes:
{
    "threads": [
        {
            "id": "1763344637195",
            "title": "TEST 17th",
            "location": "agent-8",  // ✅ HAS LOCATION FIELD
            "message_count": 0,
            "messages": []
        }
    ]
}

// Maps to:
this.threads = threads.map(thread => ({
    location: thread.location || thread.agent || 'prime',  // ✅ PRESERVED
    agent: location === 'prime' ? null : location,
    // ...
}));
```

### 6. MultiAgent.restoreThreadAssignments() (Line 30616)
```javascript
// ❌ PROBLEM: Fetches AGAIN from different endpoint
const response = await fetch('/api/thread-assignments?user_id=1');
// Returns: { "agent-8": "1763344637195" }

// Then finds thread and loads it:
const thread = this.threads.find(t => t.id === sessionId);
MultiAgent.loadThreadIntoAgent(agentIndex, thread);
```

---

## ❌ The Problem

### Issue 1: Redundant API Call
- Threads already loaded with `location` field from `/api/threads/list`
- `restoreThreadAssignments()` makes ANOTHER call to `/api/thread-assignments`
- Two sources of truth for same data

### Issue 2: Different Data Structure
```javascript
// /api/threads/list returns:
thread.location = "agent-8"

// /api/thread-assignments returns:
assignments = { "agent-8": "1763344637195" }
```

### Issue 3: Prime Auto-Load Conflict
```javascript
// ThreadManager.init() loads FIRST thread into Prime:
if (this.threads.length > 0) {
    this.currentThreadId = this.threads[0].id;
    // Loads messages into Prime...
}

// BUT if that thread's location is "agent-8", it should NOT be in Prime!
// It should be in Agent-8 column!
```

---

## ✅ The Fix

### Solution: Use `thread.location` Field Directly

Replace `restoreThreadAssignments()` to use the thread's own `location` property:

```javascript
async restoreThreadAssignments() {
    console.log('🔧 [RESTORE] Starting thread assignment restoration from thread locations...');

    try {
        // Wait for MultiAgent to be ready
        if (typeof MultiAgent === 'undefined') {
            console.warn('⚠️ [RESTORE] MultiAgent not available yet, waiting...');
            await new Promise(resolve => setTimeout(resolve, 500));
        }

        // ✅ USE THREAD.LOCATION FIELD (already loaded from /api/threads/list)
        // This is the single source of truth from sessions.threads.location column
        const threadsInAgents = this.threads.filter(t => 
            t.location && 
            t.location !== 'prime' && 
            t.location.startsWith('agent-')
        );

        console.log(`📦 [RESTORE] Found ${threadsInAgents.length} threads assigned to agents`);
        
        if (threadsInAgents.length === 0) {
            console.log('ℹ️ [RESTORE] No threads in agent columns to restore');
            return;
        }

        // Log what we're restoring
        threadsInAgents.forEach(t => {
            console.log(`  📍 Thread "${t.title}" → ${t.location} (${t.message_count || 0} messages)`);
        });

        // Restore each thread to its assigned agent column
        for (const thread of threadsInAgents) {
            const location = thread.location;
            const agentId = parseInt(location.replace('agent-', ''));

            console.log(`🔧 [RESTORE] Restoring thread "${thread.title}" to ${location}...`);

            try {
                // Load into MultiAgent with full rendering
                if (typeof MultiAgent !== 'undefined') {
                    // Load thread WITH messages
                    await MultiAgent.loadThreadIntoAgent(agentId, thread);

                    // Update agent header info card
                    MultiAgent.updateAgentHeader(agentId);

                    console.log(`✅ [RESTORE] Thread "${thread.title}" restored to ${location}`);
                }
            } catch (error) {
                console.error(`❌ [RESTORE] Failed to restore thread "${thread.title}":`, error);
            }

            // Small delay to prevent UI blocking
            await new Promise(resolve => setTimeout(resolve, 50));
        }

        // Refresh thread list to show all agent badges
        this.renderThreadList();

        console.log(`✅ [RESTORE] All ${threadsInAgents.length} thread assignments restored`);

    } catch (error) {
        console.error('❌ [RESTORE] Error restoring thread assignments:', error);
    }
}
```

### Benefits:
1. ✅ Single source of truth (`thread.location` field)
2. ✅ No redundant API call
3. ✅ Simpler logic (filter threads by location)
4. ✅ Consistent with Realtime updates (which also use `location` field)

---

## 🔧 Additional Fix Needed: Prime Auto-Load

### Current Problem:
```javascript
// ThreadManager.init() ALWAYS loads first thread into Prime:
if (this.threads.length > 0) {
    this.currentThreadId = this.threads[0].id;
    // Load into Prime...
}
```

**Issue:** If the first thread has `location = "agent-8"`, it should NOT be loaded into Prime!

### Solution:
```javascript
async init() {
    await this.ensureCorrectUserData();
    await this.loadThreadsFromBackend();
    this.initRealtimeSubscription();

    // ✅ FIXED: Only auto-load threads that belong in Prime
    if (this.threads.length > 0) {
        // Find first thread that belongs in Prime
        const primeThread = this.threads.find(t => !t.location || t.location === 'prime');
        
        if (primeThread) {
            this.currentThreadId = primeThread.id;
            const thread = this.getCurrentThread();

            if (thread && thread.messages && thread.messages.length > 0) {
                console.log(`[DATA] Auto-loading Prime thread with ${thread.messages.length} messages`);

                // Load messages into chat
                const messagesContainer = document.getElementById('ai-chat-messages');
                if (messagesContainer) {
                    messagesContainer.innerHTML = '';
                    thread.messages.forEach(msg => {
                        addChatMessage(msg.role, msg.content);
                    });
                }

                // Update AppState
                if (typeof AppState !== 'undefined') {
                    AppState.chatMessages = [...thread.messages];
                    AppState.sessionId = thread.id;
                }

                // Update Prime header
                this.updatePrimeHeader(thread);

                // Show Prime input wrapper
                const primeInputWrapper = document.querySelector('.ai-chat-input-wrapper');
                if (primeInputWrapper) {
                    primeInputWrapper.style.display = 'flex';
                }
            }
        } else {
            console.log('ℹ️ No threads in Prime - all threads in agents');
            this.showStartNewChatButton('ai-chat-messages', 'prime');
        }
    } else {
        console.log('ℹ️ No existing threads');
        this.showStartNewChatButton('ai-chat-messages', 'prime');
    }
}
```

---

## 📊 Complete On-Load Flow (After Fix)

### Correct Sequence:

```
1. DOMContentLoaded
   ↓
2. UserAuth.checkExistingSession()
   ↓
3. UserAuth.showMainApp()
   ↓
4. initializeMainApp()
   ↓
5. ThreadManager.init()
   ↓
   5a. Load threads from /api/threads/list (WITH location field)
   5b. Find first thread with location='prime'
   5c. Load ONLY that thread into Prime
   ↓
6. MultiAgent.restoreThreadAssignments()
   ↓
   6a. Filter threads WHERE location LIKE 'agent-%'
   6b. For each: MultiAgent.loadThreadIntoAgent(agentId, thread)
   6c. Render messages in agent chat column
   6d. Update agent header info card
   ↓
7. Result:
   ✅ Prime: Shows thread with location='prime' (if any)
   ✅ Agent-8: Shows thread with location='agent-8' (with messages rendered)
   ✅ Agent-5: Shows thread with location='agent-5' (with messages rendered)
   ✅ Other agents: Show "Start New Chat" button
```

---

## 🧪 Testing After Fix

### Test 1: Thread in Agent-8
**Setup:**
- Thread "TEST 17th" has `location = "agent-8"`
- 5 messages in thread

**Expected on page load:**
```
Prime: Empty (shows "Start New Chat")
Agent-8: Thread "TEST 17th" loaded
  - Thread info card shows title, meta, links
  - Chat messages rendered (5 messages visible)
  - Input area enabled
```

### Test 2: One Thread in Prime, One in Agent
**Setup:**
- Thread A: `location = "prime"`, 10 messages
- Thread B: `location = "agent-5"`, 3 messages

**Expected:**
```
Prime: Thread A loaded (10 messages visible)
Agent-5: Thread B loaded (3 messages visible)
Other agents: Empty
```

### Test 3: All Threads in Agents (None in Prime)
**Setup:**
- Thread A: `location = "agent-1"`
- Thread B: `location = "agent-8"`
- NO threads with `location = "prime"`

**Expected:**
```
Prime: Empty (shows "Start New Chat" button)
Agent-1: Thread A loaded
Agent-8: Thread B loaded
```

---

## 🎯 Summary

### Current Behavior (BROKEN):
- ❌ Loads first thread into Prime (regardless of location)
- ❌ Makes redundant API call to `/api/thread-assignments`
- ❌ Two sources of truth for thread locations
- ❌ Agent columns empty on load (threads not restored)

### Fixed Behavior (CORRECT):
- ✅ Loads only Prime threads into Prime
- ✅ Uses single source: `thread.location` field
- ✅ No redundant API calls
- ✅ Agent columns restored with messages on load
- ✅ Consistent with Realtime updates

### Files to Modify:
1. **Line 30616** - `restoreThreadAssignments()` - Use `thread.location` filter
2. **Line 25707** - `ThreadManager.init()` - Only auto-load Prime threads

---

**Status:** Analysis complete, fix ready to implement  
**Impact:** Threads will correctly load into agent columns on page refresh  
**Priority:** HIGH - Core functionality for multi-agent workflow
