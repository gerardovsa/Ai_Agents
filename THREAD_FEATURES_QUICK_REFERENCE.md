# Thread Features Quick Reference

## Assignment Triggers - All 9 Scenarios

| Action | Function Call | Result |
|--------|---------------|--------|
| Create new thread | `createNewThread()` | Assigns to Prime |
| Switch thread | `ThreadManager.switchThread(id)` | Updates to Prime |
| Load in agent | `MultiAgent.loadThreadIntoAgent(id, thread)` | Assigns to agent-X |
| Start chat in agent | `ThreadManager.startNewChat('agent-2')` | Assigns to agent-2 |
| Delete thread | `ThreadManager.deleteThread(id)` | Unassigns (null) |
| Close column | `closeAgentColumn(id)` | Keeps assignment |
| Auto-save complete | Stream finishes | No change |
| History menu | `switchThread()` + modal | User chooses |
| Drag-drop | (Future) | Will update |

## Message Schema

```javascript
const message = ThreadManager.createMessage('user', 'Hello', {
    attachments: [{filename: 'doc.pdf', url: '...'}],
    tool_calls: [{tool_name: 'gmail_send', result: {...}}],
    thinking_blocks: [{content: 'Analyzing...'}],
    feedback: [{content: 'Focus on legal emails'}],
    tokens: {prompt: 1500, completion: 800, total: 2300},
    model: 'claude-3-5-sonnet',
    response_time_ms: 3450
});
```

## Branching

```javascript
// Branch from specific message
await ThreadManager.branchThread(
    'thread-abc-123',              // Source thread ID
    'msg-1699564123456-abc123',    // Message to branch from
    'Legal Analysis Branch'         // Branch name
);
// Modal appears: Choose Prime or Agent location
```

## Tags

```javascript
// Show tag modal
ThreadManager.showTagModal('thread-abc-123');

// Add tags programmatically
await ThreadManager.addTags('thread-abc-123', ['feature', 'backend', 'high']);

// Remove tag
await ThreadManager.removeTag('thread-abc-123', 'high');

// Toggle tag
await ThreadManager.toggleTag('thread-abc-123', 'urgent');
```

### Available Tags:

- **Work Type:** feature, bug, research, documentation, planning, review
- **Area:** backend, frontend, database, api, ui-ux, infrastructure
- **Priority:** urgent, high, medium, low
- **Status:** active, blocked, waiting, paused, completed

## Synergy Integration

```javascript
// Show Synergy card picker
await ThreadManager.showSynergyCardPicker('thread-abc-123');

// Link directly
await ThreadManager.linkToSynergyCard('thread-abc-123', 'session-xyz-789');

// Unlink
await ThreadManager.unlinkFromSynergyCard('thread-abc-123');
```

## Database Migration

```powershell
# Run migration to add new columns
cd C:\Users\gpoli\GIT\AI_agents
python AI_infrastructure/migrations/run_thread_features_migration.py
```

## UI Integration

### Add Tag Button:
```html
<button onclick="ThreadManager.showTagModal('${thread.id}')" title="Tags">
    <i class="fas fa-tags"></i>
</button>
```

### Add Synergy Button:
```html
<button onclick="ThreadManager.showSynergyCardPicker('${thread.id}')" title="Link to Synergy">
    <i class="fas fa-project-diagram"></i>
</button>
```

### Add Branch Button (in message):
```html
<button onclick="ThreadManager.branchThread('${threadId}', '${messageId}', 'Branch')" title="Branch">
    <i class="fas fa-code-branch"></i>
</button>
```

### Display Tags:
```html
<div class="thread-tags">
    ${thread.tags?.map(tag => `<span class="tag">${tag}</span>`).join('') || ''}
</div>
```

### Display Synergy Badge:
```html
${thread.synergy_card_id ? `
    <span class="synergy-badge">
        <i class="fas fa-project-diagram"></i> Linked
    </span>
` : ''}
```

## Testing Commands

```javascript
// Console testing
const thread = ThreadManager.threads[0];

// Test tagging
await ThreadManager.addTags(thread.id, ['feature', 'urgent']);
console.log(thread.tags);

// Test branching
const branchId = await ThreadManager.branchThread(thread.id, thread.messages[2].message_id, 'Test Branch');
console.log('New branch:', branchId);

// Test Synergy linking
await ThreadManager.linkToSynergyCard(thread.id, 'session-123');
console.log('Linked:', thread.synergy_card_id);
```

## Backend Updates Needed

### thread_routes.py - /save endpoint:
```python
tags = json.dumps(data.get('tags', []))
synergy_card_id = data.get('synergy_card_id')
parent_thread_id = data.get('parent_thread_id')
branch_point_message_id = data.get('branch_point_message_id')
branch_name = data.get('branch_name')
summary = data.get('summary')
```

### thread_routes.py - /create endpoint:
```python
# Accept branching parameters
parent_thread_id = data.get('parent_thread_id')
branch_point_message_id = data.get('branch_point_message_id')
branch_name = data.get('branch_name')
```

## Verification

```powershell
# Check database schema
sqlite3 data/sessions.db "PRAGMA table_info(saved_threads);"

# Check for new columns
sqlite3 data/sessions.db "SELECT name FROM pragma_table_info('saved_threads') WHERE name IN ('tags', 'synergy_card_id', 'parent_thread_id');"

# Check indexes
sqlite3 data/sessions.db "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='saved_threads';"
```

## Troubleshooting

**Tags not saving:**
- Check `thread.tags` is array before saving
- Verify backend saves `tags` column as JSON string
- Check console for errors in `saveThreadToBackend()`

**Branch modal not appearing:**
- Check `branchThread()` returns valid thread ID
- Verify `showBranchLocationModal()` is called
- Check CSS for `.branch-location-modal` is loaded

**Synergy picker empty:**
- Verify `/api/synergy/sessions` endpoint exists
- Check response format: `[{session_id, title, project, column}]`
- Look for errors in browser console

**Assignment not updating:**
- Check `/api/thread-assignments/assign` returns success
- Verify `user_id` is correct (default: 1)
- Check `location` format: 'prime', 'agent-1', 'agent-2', etc.

---

**Quick Start:** Run migration → Update backend → Test in browser console → Add UI buttons
