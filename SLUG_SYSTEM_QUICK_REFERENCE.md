# Slug System Quick Reference Guide

## 🎯 TL;DR - What You Need to Know

**Slugs connect threads to workflows, Synergy sessions, and internal docs.**  
**Pills are the visual indicators (🟢 green = Synergy, 🟠 orange = Workflow).**  
**Always use `syncThreadLocationEverywhere()` to keep everything in sync.**

---

## 📋 Quick Command Reference

### Link Workflow to Thread:

```javascript
await ThreadManager.linkWorkflow(threadId, workflowId, workflowName);
// Result: Orange pill appears everywhere
```

### Link Synergy to Thread:

```javascript
await ThreadManager.linkSynergy(threadId, synergyId, synergyName);
// Result: Green pill appears everywhere
```

### Move Thread (Pills Persist):

```javascript
await ThreadManager.syncThreadLocationEverywhere(threadId, 'agent-2');
// Result: Thread moves, pills stay
```

### Unlink Workflow:

```javascript
await ThreadManager.unlinkWorkflow(threadId, workflowId);
// Result: Orange pill disappears, green pill stays
```

### Unlink Synergy:

```javascript
await ThreadManager.unlinkSynergy(threadId, synergyId);
// Result: Green pill disappears, orange pill stays
```

---

## 🎨 Pill Colors & Meanings

| Pill | Color | Icon | Meaning |
|------|-------|------|---------|
| 🟢 **Synergy** | Green `#10b981` | `fa-link` | Thread linked to Synergy multi-session |
| 🟠 **Workflow** | Orange `#f97316` | `fa-robot` | Thread linked to automation workflow |
| 🔵 **Custom** | Blue (varies) | Custom | Future extensibility |

---

## 📊 Database Fields

### threads Table:

```sql
workflow_id        TEXT    -- Workflow identifier
workflow_name      TEXT    -- Display name for workflow
synergy_card_id    TEXT    -- Synergy session identifier
synergy_card_name  TEXT    -- Display name for Synergy session
location           TEXT    -- 'prime' | 'agent-1' | 'agent-2' | ...
```

---

## 🔄 Master Sync Function

### syncThreadLocationEverywhere()

**Purpose:** Update thread location AND pills across all UI components

**Parameters:**
```javascript
syncThreadLocationEverywhere(threadId, newLocation, options = {})
```

**Options:**
- `addLinks: ['synergy', 'workflow']` - Add pills
- `removeLinks: ['synergy', 'workflow']` - Remove pills
- `preserveLinks: true` - Keep existing pills (default)
- `synergySessionId: 'id'` - Set Synergy ID
- `synergySessionName: 'name'` - Set Synergy name
- `workflowId: 'id'` - Set workflow ID
- `workflowName: 'name'` - Set workflow name

**Example:**
```javascript
await ThreadManager.syncThreadLocationEverywhere(threadId, 'agent-2', {
    addLinks: ['workflow'],
    workflowId: 'wf_123',
    workflowName: 'React Setup'
});
```

---

## ⚡ Common Patterns

### Pattern 1: AI Assigns Thread with Slugs

```python
# Backend (Python)
result = assign_and_activate_agent_with_slugs(
    target_agent='Alpha',
    thread_title='E-Commerce Frontend',
    instructions='Build React app...',
    slugs={
        'workflow_slug': 'react-frontend-workflow',
        'internal_doc_slug': 'react-architecture-guide'
    },
    auto_trigger=True,
    open_ui=True
)
```

### Pattern 2: User Drags Workflow Slug

```javascript
// Drop handler
textarea.addEventListener('drop', (e) => {
    const workflowSlug = e.dataTransfer.getData('workflow-slug');
    const workflowId = e.dataTransfer.getData('workflow-id');
    
    // Link workflow to current thread
    const thread = MultiAgent.loadedThreads[agentId];
    if (thread) {
        ThreadManager.linkWorkflow(thread.id, workflowId, workflowSlug);
    }
});
```

### Pattern 3: User Drags Thread to Agent

```javascript
// Drop handler
agentColumn.addEventListener('drop', async (e) => {
    const threadId = e.dataTransfer.getData('text/plain');
    
    // Move thread (pills persist automatically)
    await ThreadManager.syncThreadLocationEverywhere(threadId, `agent-${agentId}`);
});
```

---

## 🚨 Common Mistakes (Avoid These!)

### ❌ WRONG: Manual Updates

```javascript
// DON'T DO THIS
thread.agent = 'agent-2';
ThreadManager.assignThread(threadId, 'agent-2');
ThreadManager.renderThreadList();
// Pills might not update!
```

### ✅ CORRECT: Use Master Sync

```javascript
// DO THIS
await ThreadManager.syncThreadLocationEverywhere(threadId, 'agent-2');
// Everything updates automatically
```

---

### ❌ WRONG: Forgetting addLinks

```javascript
// DON'T DO THIS
await ThreadManager.syncThreadLocationEverywhere(threadId, 'agent-2', {
    workflowId: 'wf_123',
    workflowName: 'React'
});
// Pill might not appear!
```

### ✅ CORRECT: Include addLinks

```javascript
// DO THIS
await ThreadManager.syncThreadLocationEverywhere(threadId, 'agent-2', {
    addLinks: ['workflow'],
    workflowId: 'wf_123',
    workflowName: 'React'
});
// Pill appears everywhere
```

---

### ❌ WRONG: Clearing All Linkages

```javascript
// DON'T DO THIS
thread.workflow_id = null;
thread.synergy_card_id = null;
// Both pills gone!
```

### ✅ CORRECT: Selective Unlinking

```javascript
// DO THIS
await ThreadManager.unlinkWorkflow(threadId, 'wf_123');
// Only workflow pill gone, Synergy pill intact
```

---

## 🔍 Debugging Commands

### Check Thread Object:

```javascript
const thread = ThreadManager.threads.find(t => t.id === 'THREAD_ID');
console.log({
    location: thread.agent,
    workflow: thread.workflow_id,
    synergy: thread.synergy_card_id
});
```

### Check Database:

```sql
SELECT thread_slug, location, workflow_id, synergy_card_id
FROM sessions.threads
WHERE thread_slug = 'THREAD_ID';
```

### Check Pills in DOM:

```javascript
document.querySelectorAll('.thread-pill-workflow').length; // Orange pills
document.querySelectorAll('.thread-pill-synergy').length;  // Green pills
```

---

## 📝 Test Your Changes

```powershell
# Run test suite
python test_slug_synchronization.py

# Expected: 10/10 tests passing
```

---

## 📖 Full Documentation

- **Complete Guide:** `SLUG_SYNC_FIXES_COMPLETE.md`
- **Architecture Analysis:** `AGENT_FLOW_ANALYSIS.md`
- **Thread Sync:** `THREAD_LOCATION_SYNC_COMPLETE.md`

---

## ✅ Rules to Remember

1. **Pills are location-agnostic** - They follow the thread
2. **Always use master sync** - Don't manually update
3. **Unlink selectively** - One pill at a time
4. **Test with test suite** - Ensure nothing breaks
5. **Check all 4 locations** - Sidebar, Prime, Agents, Synergy

---

**Last Updated:** November 17, 2025  
**Status:** ✅ Production Ready
