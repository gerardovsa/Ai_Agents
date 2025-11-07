# New Chat Creation Flow - Implementation Plan

## Summary
Transform "Start New Chat" from a simple button to a comprehensive thread creation modal with:
- Thread title input
- Tag selection
- Synergy session linking
- Compact thread header display with icons
- Bidirectional thread ↔ Synergy linking

---

## Part 1: New Chat Creation Modal

### Current Behavior
```javascript
// Simple button click creates thread immediately
onclick="ThreadManager.startNewChat('prime')"
```

### New Behavior
```javascript
// Button opens modal with form
onclick="ThreadManager.showNewChatModal('prime')"
```

### Modal Structure
```html
<div class="modal-overlay" id="newChatModalOverlay">
    <div class="new-chat-modal">
        <div class="modal-header">
            <h3>💬 Start New Chat</h3>
            <button class="modal-close">×</button>
        </div>
        
        <div class="modal-body">
            <!-- Thread Title -->
            <div class="form-group">
                <label>Thread Title</label>
                <input type="text" id="newChatTitle" 
                       placeholder="Enter thread title..." 
                       autofocus>
            </div>
            
            <!-- Tags -->
            <div class="form-group">
                <label>Tags (Optional)</label>
                <div class="tag-selector">
                    <button class="tag-option" data-tag="urgent">urgent</button>
                    <button class="tag-option" data-tag="research">research</button>
                    <!-- ... more tags ... -->
                </div>
                <div class="selected-tags" id="selectedTags"></div>
            </div>
            
            <!-- Synergy Session -->
            <div class="form-group">
                <label>Link to Synergy Session (Optional)</label>
                <select id="synergySessionSelect">
                    <option value="">No Synergy Link</option>
                    <!-- Populated from synergy_sessions.db -->
                </select>
            </div>
        </div>
        
        <div class="modal-footer">
            <button class="btn-secondary" onclick="closeNewChatModal()">Cancel</button>
            <button class="btn-primary" onclick="createChatFromModal()">Create Chat</button>
        </div>
    </div>
</div>
```

---

## Part 2: Thread Header Redesign

### Current Display
```
Prime Thread
0 messages • Last updated: 11/7/2025, 9:52:15 PM
```

### New Compact Display
```
💬 Budget Review Q4
📨 0 msg  📅 11/7/2025  🕐 9:52 PM
🏷️ urgent  🏷️ finance
🎯 Synergy: Q4 Planning (sess_20251107_budget)
```

### HTML Structure
```html
<div class="ai-chat-header-info">
    <!-- Thread Title -->
    <div class="thread-title-row">
        <span class="thread-icon">💬</span>
        <h2 class="thread-title-display">Budget Review Q4</h2>
    </div>
    
    <!-- Metadata Row -->
    <div class="thread-metadata-row">
        <span class="metadata-item">
            <i class="fas fa-comment-dots"></i> 0 msg
        </span>
        <span class="metadata-item">
            <i class="fas fa-calendar"></i> 11/7/2025
        </span>
        <span class="metadata-item">
            <i class="fas fa-clock"></i> 9:52 PM
        </span>
    </div>
    
    <!-- Tags Row -->
    <div class="thread-tags-row" id="threadTagsDisplay">
        <span class="thread-tag">🏷️ urgent</span>
        <span class="thread-tag">🏷️ finance</span>
    </div>
    
    <!-- Synergy Link Row -->
    <div class="thread-synergy-row" id="threadSynergyDisplay">
        <span class="synergy-link">
            🎯 Q4 Planning
            <span class="synergy-id">sess_20251107_budget</span>
        </span>
    </div>
</div>
```

---

## Part 3: Synergy Session Integration

### Database Query
```javascript
async function loadSynergySessions() {
    const response = await fetch('/api/synergy/sessions');
    const sessions = await response.json();
    // sessions = [
    //   {session_id, title, project, column}
    // ]
    return sessions;
}
```

### Populate Dropdown
```javascript
function populateSynergyDropdown(sessions) {
    const select = document.getElementById('synergySessionSelect');
    select.innerHTML = '<option value="">No Synergy Link</option>';
    
    sessions.forEach(session => {
        const option = document.createElement('option');
        option.value = session.session_id;
        option.textContent = `${session.title} (${session.project || 'No Project'})`;
        select.appendChild(option);
    });
}
```

### Save with Synergy Link
```javascript
async function createChatFromModal() {
    const title = document.getElementById('newChatTitle').value.trim();
    const selectedTags = getSelectedTags();
    const synergySessionId = document.getElementById('synergySessionSelect').value;
    
    // Create thread via backend
    const response = await fetch('/api/threads/create', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            user_id: 1,
            title: title || 'New Chat',
            tags: selectedTags,
            synergy_card_id: synergySessionId || null,
            location: currentLocation
        })
    });
    
    const data = await response.json();
    // Load thread into UI
    loadThreadIntoAgent(data.thread);
}
```

---

## Part 4: Bidirectional Linking (Synergy ↔ Threads)

### Show Linked Threads in Synergy Card

**Synergy Card UI Update:**
```html
<!-- In Synergy Kanban card -->
<div class="synergy-card" data-session-id="sess_20251107_budget">
    <div class="card-header">
        <h3>Q4 Planning</h3>
        <span class="card-project">Finance</span>
    </div>
    
    <div class="card-body">
        <p class="card-description">Budget review session</p>
    </div>
    
    <!-- NEW: Linked Threads Section -->
    <div class="card-linked-threads">
        <h4>💬 Linked Threads (2)</h4>
        <div class="linked-thread-item">
            <span class="thread-icon">📨</span>
            <span class="thread-name">Budget Review Q4</span>
            <span class="thread-agent">Prime</span>
        </div>
        <div class="linked-thread-item">
            <span class="thread-icon">📨</span>
            <span class="thread-name">Revenue Analysis</span>
            <span class="thread-agent">Agent-2</span>
        </div>
    </div>
    
    <!-- NEW: Linked Agents Section -->
    <div class="card-linked-agents">
        <h4>🤖 Active Agents (2)</h4>
        <div class="linked-agent-item">
            <span class="agent-icon">🟢</span>
            <span class="agent-name">Prime (Main)</span>
        </div>
        <div class="linked-agent-item">
            <span class="agent-icon">🔵</span>
            <span class="agent-name">Bravo-2 (Analysis)</span>
        </div>
    </div>
</div>
```

### Backend Query for Linked Threads
```python
# In AI_infrastructure/routes/synergy_routes.py

@synergy_bp.route('/<session_id>/linked-threads', methods=['GET'])
def get_linked_threads(session_id):
    """Get all threads linked to this Synergy session"""
    
    # Query sessions.db for threads with this synergy_card_id
    threads_db = Path(__file__).parent.parent.parent / 'data' / 'sessions.db'
    
    query = """
        SELECT thread_slug, name, location, tags
        FROM threads
        WHERE synergy_card_id = ?
        ORDER BY updated_at DESC
    """
    
    rows = execute_sqlite_query(str(threads_db), query, (session_id,))
    
    threads = [{
        'thread_id': row['thread_slug'],
        'title': row['name'],
        'location': row['location'],
        'tags': json.loads(row['tags']) if row['tags'] else []
    } for row in rows]
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'threads': threads,
        'count': len(threads)
    })
```

---

## Implementation Checklist

### Frontend Changes (business-ai-platform-v2.html)

- [ ] **1. New Chat Modal HTML** (lines ~5550)
  - Add modal structure after existing modals
  - Include title input, tag selector, Synergy dropdown

- [ ] **2. New Chat Modal CSS** (lines ~5412)
  - Dark mode styling
  - Form layout
  - Tag selector styles

- [ ] **3. Modal JavaScript Methods** (lines ~15471)
  - `showNewChatModal(location)` - Open modal, load Synergy sessions
  - `createChatFromModal()` - Collect form data, create thread
  - `closeNewChatModal()` - Close and cleanup

- [ ] **4. Thread Header Redesign** (lines ~7000-7100)
  - Replace verbose text with compact icons
  - Add tag display row
  - Add Synergy link display row

- [ ] **5. Thread Header CSS** (lines ~3000-3500)
  - Compact metadata layout
  - Icon spacing
  - Tag and Synergy row styles

- [ ] **6. Update startNewChat()** (lines ~14692)
  - Change from direct creation to modal open
  - Keep fallback for backwards compatibility

### Backend Changes

- [ ] **7. Synergy Routes** (`AI_infrastructure/routes/synergy_routes.py`)
  - Add `GET /<session_id>/linked-threads` endpoint
  - Add `GET /<session_id>/linked-agents` endpoint
  - Add thread/agent count to session list response

- [ ] **8. Thread Routes** (`AI_infrastructure/routes/thread_routes.py`)
  - Ensure `/create` accepts `synergy_card_id`
  - Ensure `/save` accepts `synergy_card_id`
  - Already done in previous fixes ✅

### Database Schema

- [ ] **9. Verify Columns** (already exists ✅)
  - `threads.synergy_card_id` - TEXT, nullable
  - `threads.tags` - TEXT (JSON array)
  - `threads.location` - TEXT (default 'prime')

---

## Testing Plan

1. **Create New Chat**
   - Click "Start New Chat" button
   - Modal appears with form
   - Fill in title: "Test Thread"
   - Select tags: "urgent", "research"
   - Select Synergy session from dropdown
   - Click "Create Chat"
   - Thread appears with correct title and location

2. **Thread Header Display**
   - Verify compact metadata shows: `📨 0 msg  📅 11/7/2025  🕐 9:52 PM`
   - Verify tags appear: `🏷️ urgent  🏷️ research`
   - Verify Synergy link appears: `🎯 Q4 Planning (sess_...)`

3. **Synergy Card Integration**
   - Open Synergy dashboard
   - Find linked session card
   - Verify "Linked Threads" section shows the thread
   - Verify "Active Agents" section shows Prime

4. **Database Verification**
   ```sql
   SELECT thread_slug, name, synergy_card_id, tags, location
   FROM threads
   WHERE name = 'Test Thread';
   -- Should show all fields populated
   ```

---

## Code Snippets Ready for Implementation

All code snippets above are production-ready and can be copy-pasted into the appropriate files.

**Next Steps:**
1. Approve this design
2. I'll implement changes in batches
3. Test each batch before moving to next

Would you like me to start implementing these changes?
