# Centralized Thread Assignment - Quick Reference

**Status:** ✅ Production Ready | **File:** `UI/business-ai-platform-v2.html`

## TL;DR

**Problem:** Threads could exist in multiple locations (Prime + agent columns) simultaneously.

**Solution:** Centralized localStorage key `thread_assignments` enforces **one thread per location, one location per thread**.

## Core API (ThreadManager)

### Get/Set Assignments
```javascript
// Get all assignments
const assignments = ThreadManager.getThreadAssignments();
// Returns: {"prime": "thread-123", "agent-1": "thread-456", "agent-2": null}

// Save assignments
ThreadManager.saveThreadAssignments(assignments);
```

### Assign Thread (Exclusive)
```javascript
// Assign thread to location (removes from any previous location)
ThreadManager.assignThread('thread-123', 'agent-1');

// Unassign thread (remove from current location)
ThreadManager.unassignThread('thread-123');
```

### Query Assignments
```javascript
// Where is this thread?
const location = ThreadManager.getThreadLocation('thread-123');
// Returns: 'prime' | 'agent-1' | 'agent-2' | ... | null

// What's at this location?
const threadId = ThreadManager.getThreadAtLocation('agent-1');
// Returns: 'thread-123' | null
```

### Validation & Debugging
```javascript
// Validate and auto-fix inconsistencies
const result = ThreadManager.validateAssignments();
// Returns: { valid: boolean, errors: string[], fixed: boolean, assignments: {} }

// Clear all assignments (reset)
ThreadManager.clearAllAssignments();
```

## Integration Points

### 1. sendToAgent() - Drag & Drop
```javascript
// Checks for conflicts, clears existing thread at target
const existingThread = this.getThreadAtLocation(`agent-${agentId}`);
if (existingThread && existingThread !== threadId) {
    MultiAgent.clearLoadedThread(agentId);
}
// Assign after successful load
this.assignThread(threadId, `agent-${agentId}`);
```

### 2. moveToPrime() - Move Thread to Prime
```javascript
// Update AppState
AppState.sessionId = threadInfo.threadId;
// Update centralized tracker
ThreadManager.assignThread(threadInfo.threadId, 'prime');
```

### 3. switchThread() - Switch Thread in Prime
```javascript
// Update AppState
AppState.sessionId = threadId;
// Update tracker
this.assignThread(threadId, 'prime');
```

### 4. initMultiAgent() - Page Load
```javascript
// Load assignments as authoritative source
const assignments = ThreadManager.getThreadAssignments();

// Restore each thread to its assigned location
Object.entries(assignments).forEach(([location, threadId]) => {
    if (location === 'prime') {
        // Restore to Prime panel
    } else if (location.startsWith('agent-')) {
        // Restore to agent column
    }
});

// Validate after 500ms
setTimeout(() => {
    ThreadManager.validateAssignments();
}, 500);
```

## Data Structure

### localStorage['thread_assignments']
```json
{
  "prime": "1762192...",      // Thread in Prime panel
  "agent-1": "1762193...",    // Thread in Alpha-1
  "agent-2": null,            // Bravo-2 empty
  "agent-3": "1762194..."     // Thread in Charlie-3
}
```

## Rules Enforced

1. ✅ **One thread per location** - Each location has max 1 thread
2. ✅ **One location per thread** - Each thread exists in only 1 location
3. ✅ **Exclusive assignment** - Assigning to new location removes from old
4. ✅ **Conflict resolution** - New assignment clears old thread at target
5. ✅ **Persistence** - Survives page refresh via localStorage

## Testing Commands

```javascript
// View all assignments
console.table(ThreadManager.getThreadAssignments());

// Find thread
ThreadManager.getThreadLocation('thread-id');  // Returns location

// Check location
ThreadManager.getThreadAtLocation('agent-1');  // Returns thread ID

// Validate
ThreadManager.validateAssignments();  // Auto-fix issues

// Reset (nuclear option)
ThreadManager.clearAllAssignments();
location.reload();
```

## Console Logging

All operations log to console with prefixes:
- `[ThreadManager]` - Assignment operations
- `[Multi-Agent]` - Thread movement
- `🔍` - Validation
- `✅` - Success
- `⚠️` - Warnings
- `❌` - Errors

## Quick Debugging

**Thread in multiple places?**
```javascript
ThreadManager.validateAssignments();  // Auto-fixes
```

**Thread not loading after refresh?**
```javascript
// Check assignments
console.log(ThreadManager.getThreadAssignments());
// Should match thread locations on screen
```

**Want to reset everything?**
```javascript
ThreadManager.clearAllAssignments();
localStorage.removeItem('multi_agent_state');
localStorage.removeItem('chat_threads');
location.reload();
```

## Migration

**Old System:** `MultiAgent.loadedThreads` + `thread.agent` property  
**New System:** `thread_assignments` localStorage key (authoritative)

**Migration happens automatically** on first page load. Old format detected and migrated to centralized tracker.

## Benefits

- 🎯 **Single source of truth** - No more state conflicts
- 🔒 **Data consistency** - Automatic conflict resolution
- 🔄 **Self-healing** - Validation auto-fixes inconsistencies
- 📦 **Persistent** - State survives page refresh
- 🐛 **Debuggable** - Easy localStorage inspection

## File Locations

**Main File:** `UI/business-ai-platform-v2.html`

**Modified Functions:**
- ThreadManager.getThreadAssignments() - Line 11950
- ThreadManager.assignThread() - Line 11964
- ThreadManager.validateAssignments() - Line 12029
- ThreadManager.sendToAgent() - Line 12438
- MultiAgent.moveToPrime() - Line 9673
- ThreadManager.switchThread() - Line 12042
- initMultiAgent() - Line 10032

---

**Need more details?** See `CENTRALIZED_THREAD_ASSIGNMENT_COMPLETE.md`
