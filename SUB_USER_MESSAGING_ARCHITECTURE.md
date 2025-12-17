# Sub-User Messaging Architecture
## Team Messaging for Shared User-IDs

**DATE:** December 17, 2025  
**PURPOSE:** Enable private messaging between team members sharing same user-id  
**KEY INSIGHT:** Display name becomes "sub-user" identity within a user-id

---

## 🎯 The Problem

**Current Issue:**
- Team shares user_id=5 (e.g., "Admin" account)
- 3 people: Alice (Desktop), Bob (MacBook), Carol (iPhone)
- All have display names: "Alice (Windows)", "Bob (Mac)", "Carol (iPhone)"
- Messages route to user_id=5 → **ALL 3 receive** (no privacy!)
- Alice can't privately message Bob
- No way to filter who sees what

**What Teams Need:**
1. **Private messaging** between sub-users (Alice → Bob only)
2. **Broadcast messaging** to all sub-users + other users
3. **Filter conversations** by sub-user (display_name)
4. **See who sent** each message (display_name, not just user_id)

---

## 🏗️ Proposed Architecture

### Identifier Hierarchy:

```
user_id (Account Level)
└─ display_name (Sub-User Level)
   └─ session_token (Browser Session Level)
      └─ device_id (Browser Fingerprint)
```

**Example:**
```
user_id = 5 ("Admin" account)
├─ Alice (Windows)
│  ├─ session_abc123 (Desktop Chrome)
│  └─ session_def456 (Desktop Firefox)
├─ Bob (Mac)
│  └─ session_ghi789 (MacBook Safari)
└─ Carol (iPhone)
   └─ session_jkl012 (iPhone Safari)
```

### Message Routing Levels:

| Target Type | Routes To | Use Case |
|-------------|-----------|----------|
| **Sub-User (Private)** | Specific display_name only | Alice → Bob (Carol doesn't see) |
| **User Broadcast** | All display_names in user_id | Message all team members |
| **Cross-User** | Different user_id | Admin team → Manager team |
| **Global Broadcast** | All users | System announcements |

---

## 📊 Database Schema Updates

### Messages Table (Add Columns):

```sql
ALTER TABLE realtime_messages ADD COLUMN sender_display_name VARCHAR(100);
ALTER TABLE realtime_messages ADD COLUMN recipient_display_name VARCHAR(100);
ALTER TABLE realtime_messages ADD COLUMN sender_session_token VARCHAR(100);
ALTER TABLE realtime_messages ADD COLUMN recipient_session_token VARCHAR(100);
```

### Message Record Example:

```json
{
  "message_id": 12345,
  "sender_user_id": 5,
  "sender_display_name": "Alice (Windows)",
  "sender_session_token": "session_abc123",
  
  "recipient_user_id": 5,  // Same user-id!
  "recipient_display_name": "Bob (Mac)",  // Specific sub-user
  "recipient_session_token": null,  // Or specific session
  
  "message_type": "private",  // NEW: private | broadcast | cross_user
  "message_text": "Hey Bob, can you check the report?",
  "room": "synergy_board",
  "created_at": "2025-12-17T10:30:00Z"
}
```

---

## 🔄 Message Routing Logic

### 1. Private Sub-User Message

**Scenario:** Alice → Bob (both user_id=5)

```python
# Message structure
{
    "sender_user_id": 5,
    "sender_display_name": "Alice (Windows)",
    "recipient_user_id": 5,  # Same user!
    "recipient_display_name": "Bob (Mac)",  # Specific sub-user
    "message_type": "private"
}

# Routing logic
if message_type == 'private' and recipient_display_name:
    # Find Bob's active sessions
    bob_sessions = [
        session for session in active_users[5]
        if session['display_name'] == "Bob (Mac)"
    ]
    
    # Emit only to Bob's sessions
    for session in bob_sessions:
        emit('new_message', message, room=session['sid'])
```

### 2. User Broadcast (All Sub-Users)

**Scenario:** Alice → All team members (Alice, Bob, Carol)

```python
# Message structure
{
    "sender_user_id": 5,
    "sender_display_name": "Alice (Windows)",
    "recipient_user_id": 5,  # Same user
    "recipient_display_name": null,  # Broadcast to all
    "message_type": "broadcast"
}

# Routing logic
if message_type == 'broadcast' and not recipient_display_name:
    # Emit to ALL sessions of user_id=5
    emit('new_message', message, room=f'user_{user_id}')
```

### 3. Cross-User Message

**Scenario:** Alice (user_id=5) → Manager (user_id=7)

```python
# Message structure
{
    "sender_user_id": 5,
    "sender_display_name": "Alice (Windows)",
    "recipient_user_id": 7,  # Different user
    "recipient_display_name": null,  # All sub-users of user 7
    "message_type": "cross_user"
}

# Routing logic
if recipient_user_id != sender_user_id:
    # Emit to ALL sessions of user_id=7
    emit('new_message', message, room=f'user_{recipient_user_id}')
```

---

## 🎨 UI Changes

### Chat Sidebar - Sub-User Selection

**Before (Current):**
```
[Chat Sidebar]
┌─────────────────────┐
│ Conversations       │
├─────────────────────┤
│ 👤 Manager Team     │  ← user_id=7 (all sub-users)
│ 👤 Sales Team       │  ← user_id=9 (all sub-users)
└─────────────────────┘
```

**After (Sub-User Support):**
```
[Chat Sidebar]
┌─────────────────────────────┐
│ Conversations               │
├─────────────────────────────┤
│ 👤 Admin Team (Broadcast)   │  ← user_id=5 (all)
│   ├─ Alice (Windows) [ME]   │  ← Sub-user (private)
│   ├─ Bob (Mac) 🟢           │  ← Sub-user (private)
│   └─ Carol (iPhone) 🔴      │  ← Sub-user (offline)
│                              │
│ 👤 Manager Team             │  ← user_id=7
│   ├─ Broadcast              │  ← All managers
│   ├─ Dave (Windows) 🟢      │  ← Private to Dave
│   └─ Eve (Mac) 🟢           │  ← Private to Eve
└─────────────────────────────┘
```

### Conversation View Header:

```
┌─────────────────────────────────────┐
│ 💬 Bob (Mac) - Private              │  ← Private sub-user
│    Part of: Admin Team              │  ← Parent user-id
│    [Voice Call] [Video] [...]       │
├─────────────────────────────────────┤
│ Messages                            │
```

OR

```
┌─────────────────────────────────────┐
│ 💬 Admin Team - Broadcast           │  ← All sub-users
│    Members: Alice, Bob, Carol       │  ← Sub-user list
│    [Voice Call All] [...]           │
├─────────────────────────────────────┤
│ Messages                            │
```

---

## 🔧 Implementation Changes

### 1. Update `message_service.py`

**Add Sub-User Parameters:**

```python
def save_message(
    self,
    sender_user_id: int,
    message_text: str,
    sender_display_name: str,  # NEW
    sender_session_token: str,  # NEW
    message_type: str = 'private',  # NEW: private | broadcast | cross_user
    recipient_user_id: Optional[int] = None,
    recipient_display_name: Optional[str] = None,  # NEW
    recipient_session_token: Optional[str] = None,  # NEW
    room: str = 'synergy_board',
    metadata: Optional[Dict] = None
) -> Optional[int]:
    """Save message with sub-user routing"""
    
    cursor.execute("""
        INSERT INTO realtime_messages (
            sender_user_id,
            sender_display_name,
            sender_session_token,
            recipient_user_id,
            recipient_display_name,
            recipient_session_token,
            message_type,
            message_text,
            room,
            metadata,
            created_at,
            delivered_to,
            read_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), ARRAY[]::jsonb[], ARRAY[]::jsonb[])
        RETURNING message_id
    """, (
        sender_user_id,
        sender_display_name,
        sender_session_token,
        recipient_user_id,
        recipient_display_name,
        recipient_session_token,
        message_type,
        message_text,
        room,
        json.dumps(metadata or {})
    ))
```

**Add Sub-User Conversation List:**

```python
def get_user_conversations(
    self,
    user_id: int,
    display_name: Optional[str] = None  # NEW: Filter by sub-user
) -> List[Dict]:
    """
    Get conversation list for user, optionally filtered by display_name
    
    Args:
        user_id: User ID
        display_name: Optional sub-user filter (e.g., "Bob (Mac)")
    
    Returns:
        List of conversations with:
        - Broadcast conversations (all sub-users)
        - Private conversations (specific display_name)
    """
    
    cursor.execute("""
        SELECT DISTINCT
            CASE
                WHEN rm.sender_user_id = %s THEN rm.recipient_user_id
                ELSE rm.sender_user_id
            END as other_user_id,
            
            CASE
                WHEN rm.sender_user_id = %s THEN rm.recipient_display_name
                ELSE rm.sender_display_name
            END as other_display_name,
            
            MAX(rm.created_at) as last_message_time,
            
            COUNT(CASE 
                WHEN rm.recipient_user_id = %s 
                AND rm.recipient_display_name = %s
                AND NOT (rm.read_by @> ARRAY[jsonb_build_object('user_id', %s, 'display_name', %s)])
                THEN 1 
            END) as unread_count,
            
            rm.message_type
            
        FROM realtime_messages rm
        WHERE 
            (rm.sender_user_id = %s OR rm.recipient_user_id = %s)
            AND (
                -- Messages TO this sub-user (private)
                (rm.recipient_display_name = %s AND rm.message_type = 'private')
                OR
                -- Messages FROM this sub-user
                (rm.sender_display_name = %s)
                OR
                -- Broadcast messages to this user (any sub-user)
                (rm.recipient_user_id = %s AND rm.recipient_display_name IS NULL)
            )
        GROUP BY other_user_id, other_display_name, rm.message_type
        ORDER BY last_message_time DESC
    """, (
        user_id, user_id, user_id, display_name, user_id, display_name,
        user_id, user_id, display_name, display_name, user_id
    ))
```

### 2. Update `chat-sidebar.js`

**Add Sub-User Selection:**

```javascript
// Conversation structure
const conversation = {
    userId: 5,
    displayName: "Bob (Mac)",  // NEW: Specific sub-user
    messageType: "private",    // NEW: private | broadcast | cross_user
    isSubUser: true,           // NEW: Same user-id, different display_name
    parentUserId: 5            // NEW: Parent user account
};

// Send message with sub-user routing
sendMessage: function(messageText) {
    const currentConv = this.currentConversation;
    
    const messageData = {
        sender_user_id: this._getUserId(),
        sender_display_name: this._getDisplayName(),
        sender_session_token: this._getSessionToken(),
        
        recipient_user_id: currentConv.userId,
        recipient_display_name: currentConv.displayName,  // NEW
        recipient_session_token: null,  // Or specific session
        
        message_type: currentConv.messageType,  // NEW
        message_text: messageText,
        room: 'synergy_board'
    };
    
    SynergyRealtime.sendDirectMessage(messageData);
}
```

**Add Sub-User List UI:**

```javascript
renderConversationList: function(conversations) {
    // Group by user_id
    const grouped = {};
    
    conversations.forEach(conv => {
        if (!grouped[conv.userId]) {
            grouped[conv.userId] = {
                userId: conv.userId,
                subUsers: [],
                broadcast: null
            };
        }
        
        if (conv.messageType === 'broadcast') {
            grouped[conv.userId].broadcast = conv;
        } else {
            grouped[conv.userId].subUsers.push(conv);
        }
    });
    
    // Render with expand/collapse
    html += `
        <div class="chat-user-group">
            <div class="chat-user-header" onclick="ChatSidebar.toggleUserGroup(${userId})">
                👤 ${userName} - Broadcast
                <span class="chat-expand-icon">▼</span>
            </div>
            <div class="chat-sub-users" id="subusers-${userId}">
                ${subUsers.map(sub => `
                    <div class="chat-sub-user-item" onclick="ChatSidebar.openSubUserChat(${userId}, '${sub.displayName}')">
                        ├─ ${sub.displayName}
                        ${sub.online ? '🟢' : '🔴'}
                        ${sub.unreadCount > 0 ? `<span class="badge">${sub.unreadCount}</span>` : ''}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}
```

### 3. Update WebSocket Handler `flask_app.py`

**Route by Display Name:**

```python
@socketio.on('direct_message', namespace='/ws/synergy')
def ws_synergy_direct_message(data):
    """Handle direct message with sub-user routing"""
    
    sender_user_id = data.get('sender_user_id')
    sender_display_name = data.get('sender_display_name')
    sender_session_token = data.get('sender_session_token')
    
    recipient_user_id = data.get('recipient_user_id')
    recipient_display_name = data.get('recipient_display_name')
    message_type = data.get('message_type', 'private')
    
    # Save to database
    message_id = message_service.save_message(
        sender_user_id=sender_user_id,
        sender_display_name=sender_display_name,
        sender_session_token=sender_session_token,
        recipient_user_id=recipient_user_id,
        recipient_display_name=recipient_display_name,
        message_type=message_type,
        message_text=data.get('message_text'),
        room=data.get('room', 'synergy_board')
    )
    
    # Route based on message_type
    if message_type == 'private' and recipient_display_name:
        # PRIVATE: Send only to sessions with matching display_name
        target_sessions = []
        
        if recipient_user_id in active_users:
            for session_token, session_info in active_users[recipient_user_id].items():
                if session_info.get('display_name') == recipient_display_name:
                    target_sessions.append(session_info.get('sid'))
        
        # Emit to specific sessions only
        for sid in target_sessions:
            emit('new_message', {
                'message_id': message_id,
                'sender_user_id': sender_user_id,
                'sender_display_name': sender_display_name,
                'message_text': data.get('message_text'),
                'message_type': 'private',
                'timestamp': datetime.now().isoformat()
            }, room=sid)
        
        log_info(logger, f"[WS] Private message {message_id}: {sender_display_name} → {recipient_display_name} ({len(target_sessions)} sessions)")
    
    elif message_type == 'broadcast':
        # BROADCAST: Send to ALL sessions of user_id
        emit('new_message', {
            'message_id': message_id,
            'sender_user_id': sender_user_id,
            'sender_display_name': sender_display_name,
            'message_text': data.get('message_text'),
            'message_type': 'broadcast',
            'timestamp': datetime.now().isoformat()
        }, room=f'user_{recipient_user_id}')
        
        log_info(logger, f"[WS] Broadcast message {message_id}: {sender_display_name} → all of user {recipient_user_id}")
    
    else:
        # CROSS-USER: Send to all sessions of different user
        emit('new_message', {
            'message_id': message_id,
            'sender_user_id': sender_user_id,
            'sender_display_name': sender_display_name,
            'message_text': data.get('message_text'),
            'message_type': 'cross_user',
            'timestamp': datetime.now().isoformat()
        }, room=f'user_{recipient_user_id}')
        
        log_info(logger, f"[WS] Cross-user message {message_id}: user {sender_user_id} → user {recipient_user_id}")
```

---

## 🎬 Usage Scenarios

### Scenario 1: Private Sub-User Chat

**Setup:**
- User ID: 5 (Admin account)
- Alice (Windows): Desktop browser
- Bob (Mac): MacBook browser
- Carol (iPhone): iPhone Safari

**Action:** Alice wants to privately ask Bob a question

```javascript
// Alice clicks on "Bob (Mac)" in sub-user list
ChatSidebar.openConversation({
    userId: 5,
    displayName: "Bob (Mac)",
    messageType: "private",
    isSubUser: true
});

// Alice types: "Hey Bob, can you review the report?"
// System sends:
{
    sender_user_id: 5,
    sender_display_name: "Alice (Windows)",
    recipient_user_id: 5,  // Same user!
    recipient_display_name: "Bob (Mac)",  // Only Bob
    message_type: "private"
}

// Result: Only Bob sees the message, Carol does NOT
```

### Scenario 2: Team Broadcast

**Action:** Alice wants to notify entire Admin team

```javascript
// Alice clicks on "Admin Team - Broadcast"
ChatSidebar.openConversation({
    userId: 5,
    displayName: null,  // No specific sub-user
    messageType: "broadcast",
    isSubUser: false
});

// Alice types: "Team meeting in 10 minutes!"
// System sends:
{
    sender_user_id: 5,
    sender_display_name: "Alice (Windows)",
    recipient_user_id: 5,
    recipient_display_name: null,  // All sub-users
    message_type: "broadcast"
}

// Result: Alice, Bob, AND Carol all see the message
```

### Scenario 3: Cross-Team Message

**Action:** Alice (Admin team) messages Dave (Manager team)

```javascript
// Alice clicks on "Manager Team"
ChatSidebar.openConversation({
    userId: 7,  // Different user-id
    displayName: null,  // All managers
    messageType: "cross_user",
    isSubUser: false
});

// Alice types: "Quarterly report is ready"
// System sends:
{
    sender_user_id: 5,
    sender_display_name: "Alice (Windows)",
    recipient_user_id: 7,  // Different user
    recipient_display_name: null,  // All of user 7
    message_type: "cross_user"
}

// Result: All managers (Dave, Eve) receive message
```

### Scenario 4: Voice Call Sub-User

**Action:** Alice calls Bob specifically (not Carol)

```javascript
// Alice clicks phone icon in "Bob (Mac)" conversation
ChatSidebar.startVoiceCall({
    userId: 5,
    displayName: "Bob (Mac)",
    sessionToken: "session_ghi789"  // Bob's specific session
});

// System sends WebRTC offer ONLY to Bob's sessions
// Carol does NOT get call notification
```

---

## 📊 Conversation List Query

**SQL Query for Sub-User Conversations:**

```sql
-- Get all conversations for Alice (Windows) in user_id=5

SELECT DISTINCT
    rm.sender_user_id,
    rm.sender_display_name,
    rm.recipient_user_id,
    rm.recipient_display_name,
    rm.message_type,
    MAX(rm.created_at) as last_message_at,
    COUNT(*) FILTER (
        WHERE rm.recipient_display_name = 'Alice (Windows)'
        AND NOT (rm.read_by @> jsonb_build_object('display_name', 'Alice (Windows)'))
    ) as unread_count
FROM realtime_messages rm
WHERE
    -- Messages TO Alice (private)
    (rm.recipient_user_id = 5 AND rm.recipient_display_name = 'Alice (Windows)')
    OR
    -- Messages FROM Alice
    (rm.sender_user_id = 5 AND rm.sender_display_name = 'Alice (Windows)')
    OR
    -- Broadcast TO user 5 (any sub-user)
    (rm.recipient_user_id = 5 AND rm.recipient_display_name IS NULL)
GROUP BY
    rm.sender_user_id,
    rm.sender_display_name,
    rm.recipient_user_id,
    rm.recipient_display_name,
    rm.message_type
ORDER BY last_message_at DESC;
```

**Result:**

```
| sender | sender_display | recipient | recipient_display | type      | last_msg           | unread |
|--------|----------------|-----------|-------------------|-----------|--------------------|--------|
| 5      | Bob (Mac)      | 5         | Alice (Windows)   | private   | 2025-12-17 10:30   | 2      |
| 5      | Carol (iPhone) | 5         | NULL              | broadcast | 2025-12-17 09:15   | 0      |
| 7      | Dave (Windows) | 5         | NULL              | cross_user| 2025-12-17 08:00   | 1      |
```

---

## 🎨 CSS Updates

```css
/* Sub-user conversation list */
.chat-user-group {
    margin-bottom: 8px;
}

.chat-user-header {
    padding: 12px;
    background: rgba(255,255,255,0.05);
    border-radius: 8px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
}

.chat-user-header:hover {
    background: rgba(255,255,255,0.08);
}

.chat-expand-icon {
    transition: transform 0.2s;
    font-size: 12px;
}

.chat-user-group.expanded .chat-expand-icon {
    transform: rotate(180deg);
}

.chat-sub-users {
    padding-left: 12px;
    margin-top: 4px;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}

.chat-user-group.expanded .chat-sub-users {
    max-height: 500px;
}

.chat-sub-user-item {
    padding: 8px 12px;
    margin: 2px 0;
    cursor: pointer;
    border-radius: 6px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: rgba(255,255,255,0.8);
}

.chat-sub-user-item:hover {
    background: rgba(255,255,255,0.05);
}

.chat-sub-user-item.active {
    background: rgba(74,144,226,0.2);
    color: #4a90e2;
}

/* Message type indicator */
.chat-message-type {
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 10px;
    margin-left: 8px;
}

.chat-message-type.private {
    background: rgba(156,39,176,0.2);
    color: #9c27b0;
}

.chat-message-type.broadcast {
    background: rgba(255,152,0,0.2);
    color: #ff9800;
}

.chat-message-type.cross-user {
    background: rgba(76,175,80,0.2);
    color: #4caf50;
}
```

---

## ✅ Migration Steps

### Step 1: Database Migration

```sql
-- Add new columns
ALTER TABLE realtime_messages 
ADD COLUMN sender_display_name VARCHAR(100),
ADD COLUMN sender_session_token VARCHAR(100),
ADD COLUMN recipient_display_name VARCHAR(100),
ADD COLUMN recipient_session_token VARCHAR(100);

-- Update existing messages (backfill)
UPDATE realtime_messages 
SET 
    sender_display_name = 'Legacy User',
    message_type = 'broadcast'
WHERE sender_display_name IS NULL;

-- Create index for sub-user queries
CREATE INDEX idx_messages_recipient_display 
ON realtime_messages(recipient_user_id, recipient_display_name);

CREATE INDEX idx_messages_sender_display 
ON realtime_messages(sender_user_id, sender_display_name);
```

### Step 2: Update Message Service

```bash
# Update message_service.py with new parameters
# Add get_user_conversations with display_name filter
# Add get_sub_users(user_id) method
```

### Step 3: Update Frontend

```bash
# Update chat-sidebar.js with sub-user UI
# Add conversation grouping by user_id
# Add expand/collapse for sub-user lists
# Update sendMessage with display_name routing
```

### Step 4: Update WebSocket Handler

```bash
# Update ws_synergy_direct_message with display_name routing
# Add session lookup by display_name
# Add emit logic for private/broadcast/cross-user
```

### Step 5: Test Scenarios

```bash
# Test 1: Private sub-user message (Alice → Bob)
# Test 2: Broadcast to team (Alice → All)
# Test 3: Cross-user message (Alice → Dave)
# Test 4: Voice call to sub-user (Alice calls Bob)
# Test 5: Read receipts across sub-users
```

---

## 🚀 Benefits

✅ **Privacy:** Team members can have private conversations  
✅ **Flexibility:** Choose private or broadcast per message  
✅ **Clarity:** Always know WHO sent message (display_name)  
✅ **Filtering:** View conversations by sub-user  
✅ **Scalability:** Works with any number of sub-users per user-id  
✅ **Backwards Compatible:** Existing messages work as broadcast  

---

## 📝 API Examples

### Send Private Sub-User Message:

```javascript
SynergyRealtime.sendDirectMessage({
    sender_user_id: 5,
    sender_display_name: "Alice (Windows)",
    sender_session_token: "session_abc123",
    recipient_user_id: 5,
    recipient_display_name: "Bob (Mac)",  // PRIVATE to Bob
    message_type: "private",
    message_text: "Hey Bob, quick question"
});
```

### Send Broadcast to Team:

```javascript
SynergyRealtime.sendDirectMessage({
    sender_user_id: 5,
    sender_display_name: "Alice (Windows)",
    sender_session_token: "session_abc123",
    recipient_user_id: 5,
    recipient_display_name: null,  // BROADCAST to all
    message_type: "broadcast",
    message_text: "Team meeting in 10 mins"
});
```

### Get Sub-User Conversations:

```javascript
fetch('/api/messages/conversations?user_id=5&display_name=Alice%20(Windows)')
    .then(r => r.json())
    .then(conversations => {
        // Returns:
        // [
        //   { userId: 5, displayName: "Bob (Mac)", type: "private", unread: 2 },
        //   { userId: 5, displayName: null, type: "broadcast", unread: 0 },
        //   { userId: 7, displayName: null, type: "cross_user", unread: 1 }
        // ]
    });
```

---

## 🎯 Summary

**Key Changes:**

1. **Database:** Add `sender_display_name`, `recipient_display_name`, `message_type` columns
2. **Message Service:** Filter by display_name in queries
3. **WebSocket:** Route to specific sessions by display_name (private) or all sessions (broadcast)
4. **UI:** Expand/collapse sub-user lists, show message type indicators
5. **Routing:** Three levels - private (sub-user), broadcast (user), cross-user (different user-id)

**Display Name = Sub-User Identity** within a user-id!

**Team messaging problem SOLVED!** ✅

