# Synergy Sessions Real-Time Collaboration System
## Design Document - December 17, 2025

## 🎯 Vision: Asana-like Multiplayer Editing

Transform Synergy sessions into a fully collaborative workspace where multiple users can edit simultaneously without conflicts.

---

## 📊 Current State Analysis

### What Exists
✅ **WebSocket Infrastructure** (`synergy-realtime.js`)
- Socket.IO connection to Flask backend
- Room-based presence system
- User session tracking with display names
- Device identification

✅ **Inline Editing** (`synergy-inline-edit.js`)
- ContentEditable fields for milestones/tasks/documents
- Save/cancel functionality
- API persistence
- Context-aware editing (sidebar/dashboard/popup)

✅ **Thread Lock System** (NEW - Just Implemented)
- Lock/unlock threads in Agent columns & Prime
- Visual indicators (red border, lock banner)
- Real-time sync across sessions
- Input disabling with scroll preservation

### What's Missing
❌ **Session-Level Collaboration**
- No indication when someone else is viewing/editing a session
- No field-level locking
- No real-time field updates
- No conflict resolution
- No collaborative editing indicators

---

## 🏗️ Proposed Architecture

### 1. Presence System Enhancement

**Add to `synergy-realtime.js`:**

```javascript
// Track who's viewing which sessions
_activeSessionViewers = {}; // { session_id: [{ user_id, display_name, device }] }

// Announce session viewing
announceSessionView(sessionId) {
    if (!this.isConnected()) return;
    
    this.socket.emit('session_viewing', {
        session_id: sessionId,
        user_id: this._getUserId(),
        display_name: this._getSessionDisplayName(),
        device: this._getDeviceInfo(),
        session_token: this._generateSessionToken(),
        timestamp: new Date().toISOString()
    });
}

// Stop viewing session
announceSessionLeave(sessionId) {
    this.socket.emit('session_leave', {
        session_id: sessionId,
        session_token: this._generateSessionToken()
    });
}
```

**Backend Handler (`flask_app.py`):**

```python
@socketio.on('session_viewing', namespace='/ws/synergy')
def handle_session_viewing(data):
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    
    # Broadcast to others viewing this session
    emit('session_viewer_joined', {
        'session_id': session_id,
        'user_id': user_id,
        'display_name': data.get('display_name'),
        'device': data.get('device'),
        'timestamp': data.get('timestamp')
    }, room=f'session_{session_id}', skip_sid=request.sid)
    
    # Join session room
    join_room(f'session_{session_id}')
```

---

### 2. Field-Level Locking (Like Notion/Linear)

**Locking Strategy:**
- **Soft Lock**: Visual indicator only (non-blocking)
- **Hard Lock**: Prevents editing (blocking)
- **Auto-Release**: Lock released after 30s of inactivity

**Visual Indicators:**

```css
/* Field being edited by another user */
.field-locked-by-other {
    border: 2px solid #3b82f6;
    background: rgba(59, 130, 246, 0.05);
    position: relative;
}

.field-locked-by-other::before {
    content: attr(data-locked-by);
    position: absolute;
    top: -20px;
    left: 0;
    font-size: 10px;
    color: #3b82f6;
    font-weight: 500;
    background: white;
    padding: 2px 6px;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Field being edited by me */
.field-editing-by-me {
    border: 2px solid #10b981;
    background: rgba(16, 185, 129, 0.05);
}

/* Presence avatars on card */
.session-viewers {
    position: absolute;
    top: 8px;
    right: 40px;
    display: flex;
    gap: 4px;
}

.viewer-avatar {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: var(--primary-color);
    color: white;
    font-size: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    border: 2px solid white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
```

**JavaScript Implementation:**

```javascript
// In synergy-inline-edit.js
class SynergyInlineEditClass {
    constructor() {
        this.fieldLocks = {}; // { field_id: { user_id, display_name, timestamp } }
        this.lockTimeouts = {}; // Auto-release timers
    }
    
    async lockField(sessionId, fieldName) {
        const fieldId = `${sessionId}_${fieldName}`;
        
        // Check if already locked
        if (this.fieldLocks[fieldId]) {
            const lock = this.fieldLocks[fieldId];
            const isMe = lock.session_token === window.SynergyRealtime.sessionToken;
            
            if (!isMe) {
                this.showFieldLockedWarning(fieldName, lock.display_name);
                return false;
            }
        }
        
        // Request lock from server
        const response = await fetch(`${this.API_BASE_URL}/api/synergy/lock-field`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                field_name: fieldName,
                user_id: window.UserAuth?.user_id,
                display_name: window.SynergyRealtime?._getSessionDisplayName(),
                session_token: window.SynergyRealtime?.sessionToken
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Lock acquired
            this.fieldLocks[fieldId] = result.lock;
            this.startLockHeartbeat(fieldId);
            
            // Broadcast to other sessions
            if (window.SynergyRealtime?.socket) {
                window.SynergyRealtime.socket.emit('field_locked', {
                    session_id: sessionId,
                    field_name: fieldName,
                    lock: result.lock
                });
            }
            
            return true;
        } else {
            // Lock denied (someone else has it)
            this.showFieldLockedWarning(fieldName, result.locked_by);
            return false;
        }
    }
    
    startLockHeartbeat(fieldId) {
        // Clear existing timeout
        if (this.lockTimeouts[fieldId]) {
            clearTimeout(this.lockTimeouts[fieldId]);
        }
        
        // Auto-release after 30 seconds of no activity
        this.lockTimeouts[fieldId] = setTimeout(() => {
            this.releaseFieldLock(fieldId);
        }, 30000);
    }
    
    async releaseFieldLock(fieldId) {
        const lock = this.fieldLocks[fieldId];
        if (!lock) return;
        
        // Release on server
        await fetch(`${this.API_BASE_URL}/api/synergy/release-field-lock`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                field_id: fieldId,
                session_token: lock.session_token
            })
        });
        
        // Broadcast release
        if (window.SynergyRealtime?.socket) {
            window.SynergyRealtime.socket.emit('field_unlocked', {
                field_id: fieldId
            });
        }
        
        delete this.fieldLocks[fieldId];
        delete this.lockTimeouts[fieldId];
    }
}
```

---

### 3. Real-Time Field Updates (Operational Transformation)

**When user edits a field:**

```javascript
// In synergy-inline-edit.js
editMilestone(sessionId, milestoneId) {
    const field = document.querySelector(`[data-milestone-id="${milestoneId}"] .title`);
    
    // Acquire lock first
    const canEdit = await this.lockField(sessionId, `milestone_${milestoneId}_title`);
    if (!canEdit) return;
    
    // Enable contenteditable
    field.setAttribute('contenteditable', 'true');
    field.classList.add('field-editing-by-me');
    
    // Listen for changes and broadcast
    field.addEventListener('input', debounce(() => {
        this.broadcastFieldChange(sessionId, 'milestone_title', field.textContent);
    }, 300));
}

broadcastFieldChange(sessionId, fieldName, value) {
    if (!window.SynergyRealtime?.socket) return;
    
    window.SynergyRealtime.socket.emit('field_updated', {
        session_id: sessionId,
        field_name: fieldName,
        value: value,
        timestamp: new Date().toISOString(),
        session_token: window.SynergyRealtime.sessionToken
    });
}
```

**Receive updates from others:**

```javascript
// Socket.IO listener
socket.on('field_updated', (data) => {
    // Don't apply own changes
    if (data.session_token === window.SynergyRealtime.sessionToken) return;
    
    // Find field and update (if not currently editing)
    const field = document.querySelector(`[data-field="${data.field_name}"]`);
    if (!field || field.getAttribute('contenteditable') === 'true') return;
    
    // Apply update with visual feedback
    field.classList.add('field-updating');
    field.textContent = data.value;
    
    setTimeout(() => {
        field.classList.remove('field-updating');
    }, 500);
});
```

---

### 4. Presence Indicators on Cards

**Show Avatars of Active Viewers:**

```javascript
// Add to synergy-board-init.js renderCard()
renderCard(session) {
    // ... existing card HTML ...
    
    // Add presence container
    const presenceHTML = `
        <div class="session-viewers" data-session-id="${session.session_id}">
            <!-- Populated by updateSessionViewers() -->
        </div>
    `;
    
    // Inject into card header
}

// Update viewer avatars
updateSessionViewers(sessionId, viewers) {
    const container = document.querySelector(`[data-session-id="${sessionId}"] .session-viewers`);
    if (!container) return;
    
    container.innerHTML = viewers.map(viewer => {
        const initials = viewer.display_name
            .split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .substring(0, 2);
        
        const color = this.getViewerColor(viewer.user_id);
        
        return `
            <div class="viewer-avatar" 
                 style="background: ${color}"
                 title="${viewer.display_name} (${viewer.device})">
                ${initials}
            </div>
        `;
    }).join('');
}

getViewerColor(userId) {
    const colors = [
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
        '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'
    ];
    const hash = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[hash % colors.length];
}
```

---

### 5. Conflict Resolution

**Last-Write-Wins with Timestamps:**

```javascript
applyFieldUpdate(fieldId, value, timestamp) {
    const currentTimestamp = this.fieldTimestamps[fieldId];
    
    // Only apply if newer
    if (!currentTimestamp || new Date(timestamp) > new Date(currentTimestamp)) {
        const field = document.querySelector(`[data-field-id="${fieldId}"]`);
        if (field && field.getAttribute('contenteditable') !== 'true') {
            field.textContent = value;
            this.fieldTimestamps[fieldId] = timestamp;
        }
    } else {
        console.log(`[SYNERGY] Ignored older update for field ${fieldId}`);
    }
}
```

---

## 📋 Implementation Checklist

### Phase 1: Presence System (Week 1)
- [ ] Add session_viewing/session_leave Socket.IO events
- [ ] Backend handlers for session rooms
- [ ] Viewer avatar display on cards
- [ ] Color-coded presence indicators

### Phase 2: Field Locking (Week 2)
- [ ] Field lock/unlock API endpoints
- [ ] Lock state tracking (backend Redis/memory)
- [ ] Visual lock indicators (blue border, tooltip)
- [ ] Lock auto-release after 30s inactivity

### Phase 3: Real-Time Sync (Week 3)
- [ ] field_updated Socket.IO event
- [ ] Debounced field change broadcasting
- [ ] Optimistic UI updates
- [ ] Conflict resolution with timestamps

### Phase 4: Polish & UX (Week 4)
- [ ] Smooth animations for field updates
- [ ] Toast notifications ("John is editing")
- [ ] Keyboard shortcuts (Cmd+S to save)
- [ ] Activity feed (who changed what)

---

## 🎨 User Experience Flow

### Scenario: Two Users Edit Same Session

**User A Opens Session:**
1. Clicks on "Project Apollo" card
2. Session opens in popup modal
3. Socket.IO: `session_viewing` emitted
4. User A's avatar appears on card (for others)

**User B Opens Same Session:**
1. Clicks on "Project Apollo" card
2. Sees User A's avatar in top-right
3. Both users see each other in real-time

**User A Edits Title:**
1. Clicks on title field
2. Socket.IO: `field_locked` (title)
3. User B sees blue border around title: "Locked by Alice"
4. User A types "Project Apollo 2.0"
5. Socket.IO: `field_updated` (debounced 300ms)
6. User B's UI updates in real-time

**User B Edits Description (Different Field):**
1. Clicks on description field
2. No conflict (different field)
3. Both users edit simultaneously
4. Changes sync in real-time

**Conflict Scenario:**
1. User A has title locked, editing
2. User B tries to click title
3. Shows tooltip: "Alice is editing this field"
4. User B must wait or edit different field

---

## 🔧 Technical Considerations

### Performance
- **Debouncing**: 300ms delay prevents excessive Socket.IO traffic
- **Delta Updates**: Send only changed values, not full objects
- **Connection Pooling**: Reuse Socket.IO connection for all events

### Security
- **User Authentication**: Validate session tokens
- **Field Permissions**: Check user has edit access before locking
- **Rate Limiting**: Prevent spam (max 10 updates/sec per user)

### Scalability
- **Redis for Locks**: Store field locks in Redis (expires 30s)
- **Room-Based Broadcasting**: Only send updates to users viewing that session
- **Horizontal Scaling**: Socket.IO sticky sessions with Redis adapter

---

## 📚 Inspiration Sources

**Asana**: Field-level locking, presence avatars, activity feed
**Notion**: Inline editing, smooth animations, conflict resolution
**Linear**: Optimistic UI, keyboard shortcuts, minimal latency
**Monday.com**: Column-based editing, visual cursors, real-time sync
**Figma**: Multiplayer cursors, collaborative editing patterns

---

## 🚀 Next Steps

1. **Review & Approve** this design
2. **Implement Phase 1** (Presence system)
3. **Test with 2-3 users** simultaneously
4. **Iterate based on feedback**
5. **Roll out Phases 2-4** incrementally

**Estimated Timeline**: 4 weeks for full implementation
**Priority**: High (enables true collaboration)
