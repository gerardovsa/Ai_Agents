# Code Update Checklist - Thread Schema Migration

**Date**: November 17, 2025  
**Status**: Migration Complete - Code Updates Required

---

## ✅ Database Migration: COMPLETE

- [x] Added `thread_lock_user_id` column
- [x] Added `automation_slug` column  
- [x] Added `automation_title` column
- [x] Verified columns exist in threads table

---

## 📋 FILES THAT NEED UPDATING

### 1. Device Lock Routes (CRITICAL - Uses Old Lock Columns)

**File**: `AI_infrastructure/routes/device_lock_routes.py`  
**Issue**: Uses `locked_to_device_id` and `lock_mode` (deprecated)  
**Required Changes**:

```python
# OLD CODE (lines 130-133):
UPDATE sessions.threads 
SET locked_to_device_id = %s,
    locked_at = %s,
    lock_mode = 'locked'

# NEW CODE:
UPDATE sessions.threads 
SET thread_lock_user_id = %s,
    locked_at = %s

# OLD CODE (lines 176, 184):
SELECT locked_to_device_id, user_id
locked_device = thread[0]['locked_to_device_id']

# NEW CODE:
SELECT thread_lock_user_id, user_id
locked_user = thread[0]['thread_lock_user_id']

# OLD CODE (lines 198-200):
SET locked_to_device_id = NULL,
    locked_at = NULL,
    lock_mode = 'unlocked'

# NEW CODE:
SET thread_lock_user_id = NULL,
    locked_at = NULL

# OLD CODE (line 232):
SELECT locked_to_device_id, locked_at, lock_mode, user_id

# NEW CODE:
SELECT thread_lock_user_id, locked_at, user_id
```

**Action**: Replace all device lock logic with user lock logic using `ThreadInfo` model.

---

### 2. Thread Routes (Add Automation Fields)

**File**: `AI_infrastructure/routes/thread_routes.py`  
**Issue**: INSERT/UPDATE queries don't include new automation fields  
**Lines**: 87, 273, 847, 1587, 1635

**Required Changes**:

```python
# Add to INSERT queries (line 87):
INSERT INTO sessions.threads (
    thread_slug, workspace_id, name, user_id, created_at, updated_at,
    location, tags, synergy_card_id,
    workflow_slug, workflow_title,
    internal_doc_slug, internal_doc_title,
    automation_slug, automation_title  # ADD THESE
)

# Add to UPDATE metadata query (line 273):
UPDATE sessions.threads SET
    workflow_slug = %s,
    workflow_title = %s,
    internal_doc_slug = %s,
    internal_doc_title = %s,
    automation_slug = %s,        # ADD THIS
    automation_title = %s,       # ADD THIS
    updated_at = CURRENT_TIMESTAMP
WHERE thread_slug = %s

# Add to SELECT queries (line 172):
SELECT 
    t.thread_slug, t.name, t.user_id, t.created_at, t.updated_at,
    t.location, t.tags, t.synergy_card_id,
    t.parent_thread_id, t.branch_name, t.archived, t.branch_point_message_id,
    t.token_count,
    t.workflow_slug, t.workflow_title,
    t.internal_doc_slug, t.internal_doc_title,
    t.automation_slug, t.automation_title,  # ADD THESE
    t.metadata
```

**Action**: Use `ThreadInfo` model for all queries (see `AI_infrastructure/models/thread_info.py`).

---

### 3. Thread Assignment Routes (Simplify - Direct Column Update)

**File**: `AI_infrastructure/routes/thread_assignment_routes.py`  
**Issue**: Stores assignments in `users.metadata` JSON (complex, slow)  
**Lines**: 108-188 (entire `enforce_thread_assignment_rules` function)

**Required Changes**:

```python
# OLD APPROACH: JSON metadata in users table
metadata = json.loads(row[0] or '{}')
assignments = metadata.get('thread_assignments', {})
# ... complex JSON manipulation ...
metadata['thread_assignments'] = assignments
UPDATE ai_infrastructure.users SET metadata = %s

# NEW APPROACH: Direct column update (MUCH SIMPLER)
def enforce_thread_assignment_rules(user_id, session_id, location):
    """Simplified version using threads.location column"""
    conn = get_database_connection('sessions')
    cursor = conn.cursor()
    
    # Get previous location
    cursor.execute("""
        SELECT location FROM sessions.threads 
        WHERE thread_slug = %s
    """, [session_id])
    
    row = cursor.fetchone()
    previous_location = row[0] if row else None
    
    # Check for displaced thread (agent can only have one thread)
    displaced_thread = None
    if location and location.startswith('agent-'):
        cursor.execute("""
            SELECT thread_slug FROM sessions.threads 
            WHERE location = %s AND thread_slug != %s
        """, [location, session_id])
        
        displaced_row = cursor.fetchone()
        if displaced_row:
            displaced_thread = displaced_row[0]
            # Move displaced thread to Prime
            cursor.execute("""
                UPDATE sessions.threads 
                SET location = 'prime', updated_at = CURRENT_TIMESTAMP
                WHERE thread_slug = %s
            """, [displaced_thread])
    
    # Update thread location
    cursor.execute("""
        UPDATE sessions.threads 
        SET location = %s, updated_at = CURRENT_TIMESTAMP
        WHERE thread_slug = %s
    """, [location, session_id])
    
    conn.commit()
    conn.close()
    
    return {
        'previous_location': previous_location,
        'displaced_thread': displaced_thread,
        'new_location': location
    }
```

**Action**: Replace entire `enforce_thread_assignment_rules()` function with simplified version.

---

### 4. Synergy Routes (Add Automation Field)

**File**: `AI_infrastructure/routes/synergy_routes.py`  
**Issue**: UPDATE query doesn't include automation fields  
**Line**: 649

**Required Changes**:

```python
# OLD CODE:
UPDATE sessions.threads 
SET synergy_card_id = %s
WHERE thread_slug = %s

# NEW CODE (add automation support):
UPDATE sessions.threads 
SET synergy_card_id = %s,
    automation_slug = %s,        # NEW
    automation_title = %s,       # NEW
    updated_at = CURRENT_TIMESTAMP
WHERE thread_slug = %s
```

**Action**: Add automation fields to bidirectional linking query.

---

### 5. Thread Manager (Modernize)

**File**: `AI_infrastructure/threads/thread_manager.py`  
**Issue**: Uses old ThreadManager class, should use ThreadInfo model  
**Lines**: 150, 334, 385, 432

**Required Changes**:

```python
# Import new universal model
from AI_infrastructure.models.thread_info import (
    ThreadInfo, 
    get_thread_by_slug,
    get_all_threads,
    update_thread_location,
    lock_thread,
    unlock_thread
)

# Replace all direct SQL with ThreadInfo methods
# Example:
def get_thread(self, thread_slug: str) -> Optional[ThreadInfo]:
    cursor = self.db_connection.cursor()
    thread = get_thread_by_slug(cursor, thread_slug)
    return thread

def list_threads(self, user_id: int) -> List[ThreadInfo]:
    cursor = self.db_connection.cursor()
    threads = get_all_threads(cursor, user_id)
    return threads
```

**Action**: Refactor to use `ThreadInfo` model throughout.

---

### 6. Frontend - ThreadManager (Add New Fields)

**File**: `UI/business-ai-platform-v2.html`  
**Function**: `ThreadManager.renderThreadInfoContainer()` (~line 25139)

**Required Changes**:

```javascript
// Add automation badge (after workflow badge)
${thread.automation_slug ? `
    <div class="thread-item-automation" style="background: #f59e0b15; border: 1px solid #f59e0b; border-radius: 8px; padding: 8px;">
        <button class="automation-badge" 
            style="background: #f59e0b; color: white; border: none; padding: 6px 12px; border-radius: 6px; display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer;"
            onclick="event.stopPropagation(); ThreadManager.openAutomation('${safeEscape(thread.automation_slug)}')"
            title="${safeEscape(thread.automation_title || thread.automation_slug)}">
            <i class="fas fa-robot"></i> ${safeEscape(thread.automation_title || thread.automation_slug)}
        </button>
    </div>
` : ''}

// Add lock indicator (in header row)
${thread.is_locked ? `
    <div class="thread-lock-indicator" style="display: flex; align-items: center; gap: 6px; padding: 4px 8px; background: #ef444415; border: 1px solid #ef4444; border-radius: 6px;">
        <i class="fas fa-lock" style="color: #ef4444; font-size: 11px;"></i>
        <span style="font-size: 11px; color: #ef4444;">
            ${thread.locked_by_username || 'Locked'}
        </span>
    </div>
` : ''}
```

**Action**: Add automation and lock UI to thread-info card.

---

### 7. Frontend - Lock/Unlock Functions

**File**: `UI/business-ai-platform-v2.html`  
**Add New Functions**:

```javascript
// Add to ThreadManager object
async lockThread(threadId) {
    try {
        const response = await fetch('/api/threads/lock', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                thread_id: threadId,
                user_id: AppState.userId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Thread locked', 'success', 2000);
            this.refreshAllThreadInfoCards(threadId);
        } else {
            showNotification(`Lock failed: ${data.error}`, 'error', 3000);
        }
    } catch (error) {
        console.error('Lock error:', error);
        showNotification('Failed to lock thread', 'error', 3000);
    }
},

async unlockThread(threadId) {
    try {
        const response = await fetch('/api/threads/unlock', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                thread_id: threadId,
                user_id: AppState.userId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Thread unlocked', 'success', 2000);
            this.refreshAllThreadInfoCards(threadId);
        } else {
            showNotification(`Unlock failed: ${data.error}`, 'error', 3000);
        }
    } catch (error) {
        console.error('Unlock error:', error);
        showNotification('Failed to unlock thread', 'error', 3000);
    }
},

async openAutomation(automationSlug) {
    console.log('Opening automation:', automationSlug);
    // TODO: Implement automation viewer
    showNotification(`Automation: ${automationSlug}`, 'info', 2000);
}
```

**Action**: Add lock/unlock functions to ThreadManager.

---

### 8. Backend - Add Lock/Unlock Endpoints

**File**: `AI_infrastructure/routes/thread_routes.py`  
**Add New Routes**:

```python
@thread_bp.route('/lock', methods=['POST'])
def lock_thread_route():
    """Lock thread for editing"""
    from AI_infrastructure.models.thread_info import lock_thread
    
    data = request.json
    thread_id = data.get('thread_id')
    user_id = data.get('user_id')
    
    if not thread_id or not user_id:
        return jsonify({'success': False, 'error': 'thread_id and user_id required'}), 400
    
    conn = get_database_connection('sessions')
    cursor = conn.cursor()
    
    success = lock_thread(cursor, thread_id, user_id)
    conn.commit()
    conn.close()
    
    if success:
        return jsonify({'success': True, 'message': 'Thread locked'})
    else:
        return jsonify({'success': False, 'error': 'Thread already locked by another user'}), 409


@thread_bp.route('/unlock', methods=['POST'])
def unlock_thread_route():
    """Unlock thread"""
    from AI_infrastructure.models.thread_info import unlock_thread
    
    data = request.json
    thread_id = data.get('thread_id')
    user_id = data.get('user_id')  # Optional - if not provided, force unlock
    
    if not thread_id:
        return jsonify({'success': False, 'error': 'thread_id required'}), 400
    
    conn = get_database_connection('sessions')
    cursor = conn.cursor()
    
    success = unlock_thread(cursor, thread_id, user_id)
    conn.commit()
    conn.close()
    
    if success:
        return jsonify({'success': True, 'message': 'Thread unlocked'})
    else:
        return jsonify({'success': False, 'error': 'Not authorized to unlock'}), 403
```

**Action**: Add lock/unlock endpoints to thread_routes.py.

---

## 🎯 PRIORITY ORDER

### High Priority (Breaking Changes)
1. **device_lock_routes.py** - Uses deprecated columns (app will break)
2. **thread_assignment_routes.py** - Simplify to use threads.location directly
3. **thread_routes.py** - Add lock/unlock endpoints

### Medium Priority (Feature Additions)
4. **thread_routes.py** - Add automation fields to INSERT/UPDATE
5. **synergy_routes.py** - Add automation support
6. **business-ai-platform-v2.html** - Add lock/unlock UI
7. **business-ai-platform-v2.html** - Add automation badge UI

### Low Priority (Modernization)
8. **thread_manager.py** - Refactor to use ThreadInfo model
9. **Other routes** - Gradually adopt ThreadInfo model

---

## 📊 Testing Checklist

After updates:

- [ ] Test thread locking (lock/unlock via UI)
- [ ] Test thread assignment (drag & drop still works)
- [ ] Test automation linking (add automation_slug to thread)
- [ ] Verify no errors in console
- [ ] Check database has correct values
- [ ] Test with multiple users (lock conflicts)

---

## 📚 Documentation

- **Universal Model**: `AI_infrastructure/models/thread_info.py`
- **Schema**: `data/sessions_schema.sql`
- **Migration**: `data/migrations/20251117_cleanup_schema.sql`
- **Cascade Pattern**: `THREAD_CASCADE_ARCHITECTURE.md`

---

**Status**: Ready for code updates  
**Estimated Time**: 2-3 hours for all updates  
**Risk**: Medium (breaking changes in device_lock_routes.py)
