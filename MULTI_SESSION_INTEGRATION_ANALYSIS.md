# Multi-Session Chat Integration with Device Lock & Presence System

## Date: December 17, 2025

---

## 🎯 Critical Question: Multi-Session Same User-ID

**Scenario:** Team using the same user-id on different devices
- User logs in as "admin" on Desktop (Windows)
- Same user logs in as "admin" on Laptop (Mac)
- Same user logs in as "admin" on Phone (iPhone)

**Question:** How does chat sidebar handle this?

---

## 🔍 Analysis: Three Independent Systems

Your platform has **THREE SEPARATE SYSTEMS** that work together:

### 1. Device Lock System (EXISTING - Database)
**Purpose:** Prevent editing conflicts on threads  
**Location:** `agent-js.js` lines 814-920  
**Storage:** Database `sessions.threads` table  
**Identifier:** `device_id` (browser fingerprint)

```javascript
// Device Lock Flow
User A locks thread → Database: SET locked_by_device = 'device_abc123'
User B tries to edit → Blocked: "Locked by User A (Windows)"
User A unlocks → Database: SET locked_by_device = NULL
```

**How It Works:**
- Lock stored in PostgreSQL database
- Identified by `device_id` from browser fingerprint
- Shows lock banner with **device info** (Windows, Mac, iPhone)
- Disables input but allows scrolling
- Red pulsing border on locked columns

### 2. Presence System (EXISTING - Socket.IO In-Memory)
**Purpose:** Show WHO is viewing WHICH agent column  
**Location:** `synergy-realtime.js` + `agent-js.js`  
**Storage:** Socket.IO server memory (room subscriptions)  
**Identifier:** `session_token` + `display_name` + `device`

```javascript
// Presence Flow
User A views Alpha-3 → Emits: viewing_agent('Alpha-3')
Server → Broadcasts to room: user_viewing_agent
All clients → Highlight Alpha-3 column border for User A
User A switches to Bravo-5 → Previous highlight cleared
```

**How It Works:**
- Real-time via WebSocket
- Each session gets unique `session_token`
- Display name from localStorage: `session_display_name`
- Device info: Windows, Mac, iPhone, Android
- Colored borders around agent columns
- Badge shows "User A (Windows) viewing"

### 3. Chat Sidebar (NEW - This Implementation)
**Purpose:** Direct messaging and voice calls  
**Location:** `chat-sidebar.js` + `chat-sidebar.css`  
**Storage:** Database messages + WebSocket delivery  
**Identifier:** `user_id` + `session_token` for routing

```javascript
// Chat Flow
User A (Desktop) sends to User B → Database: INSERT message
Server → Emits to ALL sessions of User B (Desktop + Phone)
User B Desktop → Shows toast + updates chat list
User B Phone → Shows toast + updates chat list
```

---

## 🔗 How They Integrate for Multi-Session Same User-ID

### Scenario: Admin user on 3 devices

```
USER: admin (user_id = 5)
├─ Session 1: Windows Desktop (session_token: abc123)
├─ Session 2: MacBook (session_token: def456)
└─ Session 3: iPhone (session_token: ghi789)
```

### 1. Device Lock Behavior

**When Admin (Desktop) locks thread:**
```sql
UPDATE sessions SET locked_by_device = 'device_abc123', 
                    locked_by_name = 'Admin (Windows)'
WHERE thread_id = 42;
```

**Result on ALL Admin sessions:**
- Desktop (lock holder): ✅ Can edit, shows "You have locked this thread"
- MacBook: ❌ Input disabled, shows "Locked by Admin (Windows)"
- iPhone: ❌ Input disabled, shows "Locked by Admin (Windows)"

**Why?** Device lock checks `device_id`, not `user_id`. Each browser has unique device fingerprint.

### 2. Presence System Behavior

**When Admin (Desktop) views Alpha-3:**
```javascript
socket.emit('viewing_agent', { 
    agent_id: 'Alpha-3', 
    session_token: 'abc123',
    display_name: 'Admin (Windows)' 
});
```

**Result visible to ALL users (including other Admin sessions):**
- Alpha-3 column gets blue border
- Badge shows "Admin (Windows) viewing"
- MacBook session sees: "Admin (Windows)" in badge
- iPhone session sees: "Admin (Windows)" in badge

**Why?** Presence broadcasts to ALL users, including same user on different devices. This is intentional - teams need to know which device is looking where.

### 3. Chat Sidebar Behavior

**When User B sends message to Admin (user_id = 5):**
```javascript
socket.emit('send_direct_message', {
    to_user_id: 5,
    message: 'Hey admin, check this out'
});
```

**Backend routing:**
```python
# flask_app.py - send_direct_message handler
@socketio.on('send_direct_message')
def handle_direct_message(data):
    to_user_id = data['to_user_id']
    
    # Emit to ALL sessions of this user
    emit('direct_message_received', message_data, 
         room=f'user_{to_user_id}')  # Targets ALL sessions
```

**Result on ALL Admin sessions:**
- Desktop: Toast notification + chat list updated
- MacBook: Toast notification + chat list updated  
- iPhone: Toast notification + chat list updated

**Why?** Messages route by `user_id`, not `session_token`. If you send to user 5, ALL devices logged in as user 5 receive it.

---

## 🎨 Display Name System Integration

### How Display Names Work

**Storage:** `localStorage.setItem('session_display_name', name)`

**Per-Session Identity:**
```javascript
// synergy-realtime.js line 506
_getSessionDisplayName() {
    let name = localStorage.getItem('session_display_name');
    
    if (!name) {
        // First time on this device
        const userName = UserAuth.user?.username || UserAuth.user?.email;
        const device = this._getDeviceInfo(); // "Windows", "Mac", etc.
        name = `${userName} (${device})`;
        localStorage.setItem('session_display_name', name);
    }
    
    return name; // "Admin (Windows)"
}
```

**Where It's Used:**

1. **Presence Badges** - Shows who's viewing agent columns
   ```javascript
   Badge text: "Admin (Windows) viewing"
   ```

2. **Device Lock Banners** - Shows who locked the thread
   ```javascript
   Banner text: "Locked by Admin (Windows)"
   ```

3. **Chat Messages** - Shows sender identity
   ```javascript
   Message bubble: "Admin (Windows): Hey team..."
   ```

4. **Online User List** - Shows all sessions in chat sidebar
   ```javascript
   Chat List:
   ├─ Admin (Windows) [online]
   ├─ Admin (Mac) [online]
   └─ Admin (iPhone) [online]
   ```

---

## 🔧 Implementation Details

### Chat Sidebar Multi-Session Support

**Key Code in `chat-sidebar.js`:**

```javascript
// Line 150 - WebSocket listeners
window.addEventListener('synergy:direct_message', (e) => {
    this.handleIncomingMessage(e.detail, 'direct');
});

// Line 320 - Handle incoming message
handleIncomingMessage(messageData, type) {
    // Check if message is for active conversation
    if (this.activeConversation === messageData.from_user_id) {
        this.appendMessageBubble(messageData);
        this.markMessageRead(messageData.message_id);
    } else {
        // Update unread count
        this.unreadCount++;
        this.updateUnreadBadge();
    }
    
    // Refresh chat list
    this.refreshChatList();
}
```

**What Happens:**
1. Message sent to user_id (not session_token)
2. Backend emits to room `user_{user_id}` (all sessions)
3. Each session receives event independently
4. Each session updates its own UI
5. Read receipts track which session read it

### Voice Call Multi-Session Handling

**Problem:** User A calls User B, but User B has 3 devices online.

**Solution:** First session to accept wins.

```javascript
// chat-sidebar.js line 450
handleCallOffer(data) {
    const accept = confirm(`Incoming call from ${data.from_user_name}. Accept?`);
    
    if (!accept) {
        // Reject - emits to caller
        socket.emit('voice_call_ended', { 
            to_user_id: data.from_user_id,
            reason: 'rejected' 
        });
        return;
    }
    
    // Accept - emits answer, other sessions ignore
    this.setupWebRTC(data);
}
```

**Flow:**
1. User A calls User B (user_id = 5)
2. Backend emits `voice_call_offer` to room `user_5`
3. All 3 of User B's devices show alert
4. User B accepts on iPhone first
5. iPhone emits `voice_call_answer` back to User A
6. Desktop/MacBook sessions either:
   - Dismiss alert manually, OR
   - Auto-hide when call is answered (add this logic)

**Recommended Enhancement:**
```javascript
// When answer is sent, notify other sessions to hide alert
socket.on('voice_call_answered', (data) => {
    if (data.answered_by_session !== this.sessionToken) {
        // Hide call alert - another session answered
        this.hideCallAlert();
    }
});
```

---

## 🚨 Potential Issues & Solutions

### Issue 1: Message Read Receipts

**Problem:** If Admin reads message on Desktop, does iPhone show as read?

**Current Behavior:**
```python
# message_service.py
def mark_read(message_id, user_id):
    UPDATE messages 
    SET read_by = array_append(read_by, user_id)
    WHERE message_id = message_id
```

**Issue:** Only stores `user_id`, not `session_token`. So if ANY session reads it, ALL sessions show as read.

**Solution Options:**

**Option A: Keep it simple (current)**
- Any session reads → All sessions show read
- Benefit: Simpler, matches WhatsApp web behavior
- User doesn't need to mark read on each device

**Option B: Per-session read tracking**
```python
# Store session tokens instead
SET read_by_sessions = array_append(read_by_sessions, session_token)
```
- Each session tracks separately
- More complex, more data
- Matches email behavior (read on phone ≠ read on desktop)

**Recommendation:** Keep Option A. Users expect cross-device sync.

### Issue 2: Typing Indicators

**Problem:** If Admin types on Desktop, do other Admin sessions show "You are typing"?

**Current Behavior:**
```javascript
// chat-sidebar.js line 180
messageInput.addEventListener('input', () => {
    socket.emit('typing_start', {
        user_id: getUserId(),
        user_name: getUserName(),
        recipient_id: this.activeConversation
    });
});
```

**Issue:** Broadcasts typing from ALL Admin sessions to recipient.

**Solution:** Already handled correctly!
```javascript
// chat-sidebar.js line 585
showTypingIndicator(userName, userId) {
    // Only show if typing user is NOT current active conversation
    if (this.activeConversation !== userId) return;
    
    // Only show typing for OTHER users, not self
    if (userId === SynergyRealtime._getUserId()) return;
    
    // Show indicator
}
```

The `userId === currentUserId` check prevents showing "You are typing" to yourself across sessions.

### Issue 3: Online Status

**Problem:** How to show all sessions of same user in chat sidebar?

**Current Behavior:**
```javascript
// chat-sidebar.js line 730
appendChatListItem(conversation) {
    // Shows single entry per user_id
    // Only shows if ANY session is online
}
```

**Issue:** Can't distinguish between sessions in chat list.

**Solution:** Add expandable session list:

```javascript
// Enhanced chat list item
<div class="chat-list-item" data-user-id="5">
    <div class="chat-list-avatar">
        <img src="...">
        <span class="online-indicator online"></span>
        <span class="session-count">3</span> <!-- NEW -->
    </div>
    <div class="chat-list-info">
        <div class="chat-list-name">Admin</div>
        <div class="chat-list-sessions"> <!-- NEW -->
            <span class="session-badge">Windows</span>
            <span class="session-badge">Mac</span>
            <span class="session-badge">iPhone</span>
        </div>
    </div>
</div>
```

**Implementation:**
```javascript
// Get all sessions for user
async getUserSessions(userId) {
    const response = await fetch(`/api/users/${userId}/sessions`);
    return response.json(); // [{device: 'Windows', online: true}, ...]
}
```

---

## 📊 Data Flow Diagrams

### Message Flow (Multi-Session Same User)

```
SENDER (User B)                    SERVER                    RECEIVER (Admin - 3 devices)
     │                                │                              │
     │  Send message to user_id=5     │                              │
     ├───────────────────────────────>│                              │
     │                                │  INSERT INTO messages        │
     │                                │  WHERE to_user_id = 5        │
     │                                │                              │
     │                                │  Emit to room 'user_5'       │
     │                                ├─────────────────────────────>│ Desktop (session_abc)
     │                                │                              ├─> Toast shown
     │                                │                              ├─> Chat list updated
     │                                │                              │
     │                                ├─────────────────────────────>│ MacBook (session_def)
     │                                │                              ├─> Toast shown
     │                                │                              ├─> Chat list updated
     │                                │                              │
     │                                ├─────────────────────────────>│ iPhone (session_ghi)
     │                                │                              ├─> Toast shown
     │                                │                              ├─> Chat list updated
     │                                │                              │
     │                                │  Desktop reads message       │
     │                                │<─────────────────────────────┤ mark_message_read(msg_id, user_id=5)
     │                                │                              │
     │                                │  UPDATE read_by = [5]        │
     │                                │  (All sessions show read)    │
     │                                │                              │
     │  Receive read receipt          │                              │
     │<───────────────────────────────┤  emit 'message_read'         │
     │  ✓✓ Message read               │  to room 'user_B'            │
```

### Presence Flow (Multi-Session Same User)

```
ADMIN Desktop                      SERVER                    OTHER USERS
     │                                │                              │
     │  viewing_agent('Alpha-3')      │                              │
     │  session: abc123               │                              │
     │  name: Admin (Windows)         │                              │
     ├───────────────────────────────>│                              │
     │                                │                              │
     │                                │  Broadcast to ALL users      │
     │                                ├─────────────────────────────>│ User B
     │                                │                              ├─> Show "Admin (Windows)"
     │                                │                              ├─> Blue border on Alpha-3
     │                                │                              │
     │                                ├─────────────────────────────>│ Admin MacBook
     │                                │                              ├─> Show "Admin (Windows)"
     │                                │                              ├─> Blue border on Alpha-3
     │                                │                              ├─> (sees own other session)
     │                                │                              │
     │                                ├─────────────────────────────>│ Admin iPhone
     │                                │                              ├─> Show "Admin (Windows)"
     │                                │                              ├─> Blue border on Alpha-3
```

### Device Lock Flow (Multi-Session Same User)

```
ADMIN Desktop                      DATABASE                  ADMIN MacBook
     │                                │                              │
     │  Lock thread_id=42             │                              │
     │  device_id: abc123             │                              │
     ├───────────────────────────────>│                              │
     │                                │  UPDATE sessions             │
     │                                │  SET locked_by_device='abc'  │
     │                                │      locked_by_name='Admin(Win)'
     │                                │                              │
     │                                │  Emit 'thread_locked'        │
     │                                ├─────────────────────────────>│
     │                                │  to room 'user_5'            │
     │                                │                              │
     │                                │                              ├─> Check device_id
     │                                │                              ├─> NOT me (device_def)
     │                                │                              ├─> Show lock banner
     │                                │                              ├─> Red pulsing border
     │                                │                              ├─> Disable input
     │                                │                              │
     │  Unlock thread                 │                              │
     ├───────────────────────────────>│                              │
     │                                │  UPDATE SET locked_by=NULL   │
     │                                │                              │
     │                                │  Emit 'thread_unlocked'      │
     │                                ├─────────────────────────────>│
     │                                │                              ├─> Remove lock banner
     │                                │                              ├─> Remove red border
     │                                │                              ├─> Enable input
```

---

## ✅ Recommendations

### 1. Keep Current Design
**Why:** Multi-session already works correctly!
- Messages route by user_id ✓
- Each session gets own UI state ✓
- Display names differentiate devices ✓
- Device lock prevents conflicts ✓

### 2. Add Session List in Chat
**Enhancement:** Show all user sessions in chat sidebar

```javascript
// New method in chat-sidebar.js
showUserSessions(userId) {
    // Expand user to show:
    // - Admin (Windows) - Online
    // - Admin (Mac) - Online  
    // - Admin (iPhone) - Last seen 5m ago
}
```

### 3. Voice Call Session Selection
**Enhancement:** Let caller choose which device to call

```javascript
// When clicking call button, show device picker
<div class="device-picker">
    <p>Call Admin on:</p>
    <button>Windows (Desktop)</button>
    <button>Mac (MacBook)</button>
    <button>iPhone</button>
    <button>All Devices</button> <!-- Rings all -->
</div>
```

### 4. Smart Read Receipt Sync
**Enhancement:** Auto-sync read status across sessions

```javascript
// When one session reads message
socket.on('message_read_by_session', (data) => {
    if (data.user_id === currentUserId) {
        // Same user, different session read it
        // Auto-mark as read locally
        this.markLocalMessageRead(data.message_id);
    }
});
```

---

## 🎯 Summary

### Your Current System is SOLID:

✅ **Device Lock** - Prevents edit conflicts using device fingerprints  
✅ **Presence** - Shows real-time viewing using session tokens  
✅ **Chat** - Routes messages by user_id, delivered to all sessions  
✅ **Display Names** - Shows device info (Windows, Mac, iPhone)  
✅ **Multi-Session** - Already fully supported!

### They Work Together Like This:

```
Same User, Multiple Devices:
├─ Device Lock: Uses device_id (unique per browser)
│  └─ Locks are device-specific, not user-specific
│
├─ Presence: Uses session_token (unique per browser tab)
│  └─ Each session broadcasts its own presence
│
└─ Chat: Uses user_id (shared across all sessions)
   └─ Messages delivered to ALL user sessions
```

### No Conflicts Because:

1. **Lock** = Device-level (prevents editing by OTHER devices)
2. **Presence** = Session-level (shows WHO is viewing WHERE)
3. **Chat** = User-level (messages to USER, not device)

---

## 📝 Integration Checklist

- [x] Display names include device info
- [x] Messages route to all user sessions
- [x] Device lock prevents cross-device conflicts
- [x] Presence shows all active sessions
- [ ] **TODO:** Show session list in chat sidebar
- [ ] **TODO:** Device picker for voice calls
- [ ] **TODO:** Auto-sync read receipts across sessions

---

**Bottom Line:** Your multi-session architecture is already solid. The chat sidebar integrates seamlessly with existing device lock and presence systems. Each serves a different purpose and they don't conflict.
