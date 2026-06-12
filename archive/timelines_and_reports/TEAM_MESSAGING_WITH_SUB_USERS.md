# Team Messaging with Sub-Users
## Leveraging Existing Display Names + Sub-User System

---

## 🎯 THE SOLUTION

You **already have everything needed**! Here's how to enable team messaging:

### ✅ What You Already Have:

1. **Display Names** (`display_name` column in `users` table)
   - Stored per-session in localStorage: `session_display_name`
   - Saved to backend: `/api/auth/update-display-name`
   - Shows as "Bob (Windows)", "Sarah (Mac)", etc.

2. **Sub-User System** (`user_management_routes.py`)
   - Parent-child user hierarchy
   - Sub-users linked via `parent_user_id`
   - Permissions, allowed_tools, data_access_scope
   - `/api/users/sub-users` endpoints

3. **Session Tokens** (`synergy-realtime.js`)
   - Unique per browser tab: `session_token`
   - Used for presence tracking
   - Stored in `this.sessionToken`

---

## 🏗️ Architecture: Use **BOTH** Systems Together

### Current Problem:
```
Team shares user_id = 5 (Admin account)
├─ Bob (Mac) - Can't message Sarah
├─ Sarah (Windows) - Can't message Bob
└─ John (iPhone) - Can't message teammates
❌ All messages go to user_id=5 (no filtering)
```

### Solution: Add `display_name` and `session_token` to messages

```sql
-- Messages table already exists, just add columns:
ALTER TABLE ai_infrastructure.messages
ADD COLUMN sender_display_name TEXT,
ADD COLUMN recipient_display_name TEXT,
ADD COLUMN sender_session_token TEXT,
ADD COLUMN recipient_session_token TEXT;
```

---

## 📊 Message Routing Logic

### 1. **Private Message** (Person-to-Person within same user-id)

```javascript
// Bob (Mac) sends to Sarah (Windows)
{
    sender_user_id: 5,
    sender_display_name: "Bob (Mac)",
    sender_session_token: "abc123",
    
    recipient_user_id: 5,  // SAME user-id
    recipient_display_name: "Sarah (Windows)",  // FILTER BY THIS
    recipient_session_token: null,  // Or specific token if known
    
    message_type: "private"  // NEW
}
```

**Backend Routing:**
```python
# Emit to ONLY sessions matching recipient_display_name
socketio.emit('new_message', message_data, 
    room=f'user_{recipient_user_id}_display_{recipient_display_name}')
```

### 2. **Broadcast to Team** (All people on same user-id)

```javascript
// Bob broadcasts to entire team (all using user_id=5)
{
    sender_user_id: 5,
    sender_display_name: "Bob (Mac)",
    
    recipient_user_id: 5,  // SAME user-id
    recipient_display_name: null,  // NULL = broadcast to all
    
    message_type: "broadcast"
}
```

**Backend Routing:**
```python
# Emit to ALL sessions of this user
socketio.emit('new_message', message_data, room=f'user_{recipient_user_id}')
```

### 3. **Cross-User Message** (Normal messaging between different users)

```javascript
// Bob (user_id=5) sends to Alice (user_id=8)
{
    sender_user_id: 5,
    sender_display_name: "Bob (Mac)",
    
    recipient_user_id: 8,  // DIFFERENT user-id
    recipient_display_name: null,  // Don't care, different account
    
    message_type: "cross_user"
}
```

**Backend Routing:**
```python
# Emit to ALL sessions of recipient user (normal behavior)
socketio.emit('new_message', message_data, room=f'user_{recipient_user_id}')
```

---

## 🎨 UI Changes

### Chat Sidebar - Show Team Members

```javascript
// Get list of active display names for current user
async getTeamMembers() {
    const userId = this._getUserId();
    
    // Query active sessions with display names
    const response = await fetch(`${API_BASE_URL}/api/presence/team-members/${userId}`);
    const data = await response.json();
    
    // Returns:
    // [
    //     { display_name: "Bob (Mac)", session_token: "abc123", online: true },
    //     { display_name: "Sarah (Windows)", session_token: "def456", online: true },
    //     { display_name: "John (iPhone)", session_token: "ghi789", online: false }
    // ]
    
    return data.team_members;
}
```

### Conversation List - Separate Team from External Users

```html
<!-- Chat Sidebar -->
<div class="chat-sidebar">
    <div class="chat-header">
        <h3>Messages</h3>
    </div>
    
    <!-- Team Section -->
    <div class="chat-section">
        <div class="chat-section-title">👥 Your Team (Admin)</div>
        <div class="chat-list">
            <div class="chat-item" data-user-id="5" data-display-name="Bob (Mac)">
                <span class="status-dot online"></span>
                Bob (Mac)
                <span class="unread-badge">2</span>
            </div>
            <div class="chat-item" data-user-id="5" data-display-name="Sarah (Windows)">
                <span class="status-dot online"></span>
                Sarah (Windows)
            </div>
        </div>
    </div>
    
    <!-- External Users Section -->
    <div class="chat-section">
        <div class="chat-section-title">💬 Other Users</div>
        <div class="chat-list">
            <div class="chat-item" data-user-id="8" data-display-name="Alice">
                <span class="status-dot offline"></span>
                Alice
            </div>
        </div>
    </div>
    
    <!-- Broadcast Button -->
    <button class="broadcast-btn">
        📢 Broadcast to Team
    </button>
</div>
```

---

## 🔧 Implementation Steps

### Step 1: Update Database Schema (2 minutes)

```sql
-- Add display_name columns to messages table
ALTER TABLE ai_infrastructure.messages
ADD COLUMN sender_display_name TEXT,
ADD COLUMN recipient_display_name TEXT,
ADD COLUMN sender_session_token TEXT,
ADD COLUMN recipient_session_token TEXT,
ADD COLUMN message_type TEXT DEFAULT 'cross_user';  -- 'private' | 'broadcast' | 'cross_user'

-- Create index for fast filtering
CREATE INDEX idx_messages_recipient_display ON ai_infrastructure.messages(recipient_user_id, recipient_display_name);
CREATE INDEX idx_messages_team ON ai_infrastructure.messages(recipient_user_id) WHERE recipient_display_name IS NULL;
```

### Step 2: Update `message_service.py` (10 minutes)

```python
# AI_infrastructure/message_service.py

def save_message(self, sender_id, recipient_id, message_text, 
                 sender_display_name=None, recipient_display_name=None,
                 sender_session_token=None, recipient_session_token=None,
                 message_type='cross_user'):
    """
    Save message with display name filtering for team messaging
    
    Args:
        sender_display_name: "Bob (Mac)" - for team identification
        recipient_display_name: "Sarah (Windows)" or None (broadcast)
        message_type: 'private' | 'broadcast' | 'cross_user'
    """
    with get_database_connection('ai_infrastructure') as conn:
        cursor = conn.cursor()
        
        sql, params = convert_sql_placeholders('''
            INSERT INTO ai_infrastructure.messages 
            (sender_id, recipient_id, message_text, 
             sender_display_name, recipient_display_name,
             sender_session_token, recipient_session_token,
             message_type, created_at, delivered_to, read_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), '[]'::jsonb, '[]'::jsonb)
            RETURNING id
        ''', (sender_id, recipient_id, message_text,
              sender_display_name, recipient_display_name,
              sender_session_token, recipient_session_token,
              message_type))
        
        cursor.execute(sql, params)
        message_id = cursor.fetchone()['id']
        conn.commit()
        
        return message_id


def get_user_conversations(self, user_id):
    """Get conversation list including team members"""
    with get_database_connection('ai_infrastructure') as conn:
        cursor = conn.cursor()
        
        sql, params = convert_sql_placeholders('''
            SELECT DISTINCT
                CASE 
                    WHEN sender_id = %s THEN recipient_id
                    ELSE sender_id
                END as other_user_id,
                
                CASE 
                    WHEN sender_id = %s THEN recipient_display_name
                    ELSE sender_display_name
                END as other_display_name,
                
                MAX(created_at) as last_message_time,
                
                COUNT(*) FILTER (
                    WHERE recipient_id = %s 
                    AND NOT (%s = ANY(read_by))
                ) as unread_count,
                
                -- Determine if this is a teammate (same user_id, different display_name)
                CASE 
                    WHEN sender_id = %s AND recipient_id = %s THEN 'team'
                    ELSE 'external'
                END as conversation_type
                
            FROM ai_infrastructure.messages
            WHERE sender_id = %s OR recipient_id = %s
            GROUP BY other_user_id, other_display_name, conversation_type
            ORDER BY last_message_time DESC
        ''', (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id))
        
        cursor.execute(sql, params)
        return cursor.fetchall()


def get_message_history(self, user_id, other_user_id, other_display_name=None, limit=50):
    """
    Get message history with optional display_name filtering
    
    If other_display_name provided: Show ONLY messages with that person (team member)
    If other_display_name is None: Show ALL messages with that user_id (external user)
    """
    with get_database_connection('ai_infrastructure') as conn:
        cursor = conn.cursor()
        
        if other_display_name:
            # Team member - filter by display_name
            sql, params = convert_sql_placeholders('''
                SELECT * FROM ai_infrastructure.messages
                WHERE (
                    (sender_id = %s AND recipient_id = %s AND recipient_display_name = %s)
                    OR
                    (sender_id = %s AND recipient_id = %s AND sender_display_name = %s)
                )
                OR (
                    -- Include broadcast messages to team
                    recipient_id = %s AND recipient_display_name IS NULL AND message_type = 'broadcast'
                )
                ORDER BY created_at DESC
                LIMIT %s
            ''', (user_id, other_user_id, other_display_name,
                  other_user_id, user_id, other_display_name,
                  user_id, limit))
        else:
            # External user - show all messages (normal behavior)
            sql, params = convert_sql_placeholders('''
                SELECT * FROM ai_infrastructure.messages
                WHERE (sender_id = %s AND recipient_id = %s)
                   OR (sender_id = %s AND recipient_id = %s)
                ORDER BY created_at DESC
                LIMIT %s
            ''', (user_id, other_user_id, other_user_id, user_id, limit))
        
        cursor.execute(sql, params)
        return cursor.fetchall()
```

### Step 3: Update WebSocket Handlers in `flask_app.py` (15 minutes)

```python
# AI_infrastructure/flask_app.py

@socketio.on('send_message', namespace='/ws/synergy')
def handle_send_message(data):
    """
    Send message with display_name routing
    
    data = {
        "recipient_user_id": 5,
        "recipient_display_name": "Sarah (Windows)",  # Optional
        "message_text": "Hello Sarah",
        "message_type": "private"  # or "broadcast" or "cross_user"
    }
    """
    sender_id = get_user_id_from_session()  # Your existing auth
    sender_display_name = data.get('sender_display_name')
    sender_session_token = data.get('sender_session_token')
    
    recipient_id = data.get('recipient_user_id')
    recipient_display_name = data.get('recipient_display_name')  # NEW
    recipient_session_token = data.get('recipient_session_token')
    
    message_text = data.get('message_text')
    message_type = data.get('message_type', 'cross_user')
    
    # Save to database
    message_id = message_service.save_message(
        sender_id=sender_id,
        recipient_id=recipient_id,
        message_text=message_text,
        sender_display_name=sender_display_name,
        recipient_display_name=recipient_display_name,
        sender_session_token=sender_session_token,
        recipient_session_token=recipient_session_token,
        message_type=message_type
    )
    
    # Build message payload
    message_data = {
        'id': message_id,
        'sender_id': sender_id,
        'sender_display_name': sender_display_name,
        'recipient_id': recipient_id,
        'recipient_display_name': recipient_display_name,
        'message_text': message_text,
        'message_type': message_type,
        'created_at': datetime.now().isoformat()
    }
    
    # Route based on message type
    if message_type == 'private' and recipient_display_name:
        # Private message to specific team member
        # Emit to ONLY sessions with matching display_name
        for session_id in active_sessions.get(recipient_id, []):
            session_data = get_session_data(session_id)
            if session_data.get('display_name') == recipient_display_name:
                emit('new_message', message_data, room=session_id, namespace='/ws/synergy')
    
    elif message_type == 'broadcast' or (message_type == 'private' and not recipient_display_name):
        # Broadcast to all sessions of recipient user
        emit('new_message', message_data, room=f'user_{recipient_id}', namespace='/ws/synergy')
    
    else:
        # Cross-user message (normal behavior)
        emit('new_message', message_data, room=f'user_{recipient_id}', namespace='/ws/synergy')
    
    return {'success': True, 'message_id': message_id}


# NEW: Endpoint to get team members
@app.route('/api/presence/team-members/<int:user_id>', methods=['GET'])
def get_team_members(user_id):
    """
    Get list of active display names for a user
    Returns team members (same user_id, different display_names)
    """
    team_members = []
    
    # Get all active sessions for this user
    for session_id in active_sessions.get(user_id, []):
        session_data = get_session_data(session_id)
        
        display_name = session_data.get('display_name')
        session_token = session_data.get('session_token')
        is_online = session_data.get('last_seen', 0) > (time.time() - 300)  # 5 min
        
        if display_name:
            team_members.append({
                'display_name': display_name,
                'session_token': session_token,
                'online': is_online
            })
    
    return jsonify({
        'success': True,
        'team_members': team_members
    })
```

### Step 4: Update `chat-sidebar.js` (20 minutes)

```javascript
// UI/shared/js/chat-sidebar.js

const ChatSidebar = {
    currentConversation: null,  // { userId, displayName, conversationType }
    
    async loadConversations() {
        const userId = this._getUserId();
        const response = await fetch(`${API_BASE_URL}/api/messages/conversations/${userId}`);
        const data = await response.json();
        
        // Separate team from external
        const teamConvs = data.conversations.filter(c => c.conversation_type === 'team');
        const externalConvs = data.conversations.filter(c => c.conversation_type === 'external');
        
        this.renderConversationList(teamConvs, externalConvs);
    },
    
    renderConversationList(teamConvs, externalConvs) {
        const listEl = document.getElementById('chat-conversation-list');
        
        let html = '';
        
        // Team section
        if (teamConvs.length > 0) {
            html += `
                <div class="chat-section">
                    <div class="chat-section-title">👥 Your Team</div>
                    ${teamConvs.map(conv => this.renderConversationItem(conv)).join('')}
                </div>
            `;
        }
        
        // External section
        if (externalConvs.length > 0) {
            html += `
                <div class="chat-section">
                    <div class="chat-section-title">💬 Other Users</div>
                    ${externalConvs.map(conv => this.renderConversationItem(conv)).join('')}
                </div>
            `;
        }
        
        // Broadcast button (only if team exists)
        if (teamConvs.length > 0) {
            html += `
                <button class="chat-broadcast-btn" onclick="ChatSidebar.openBroadcast()">
                    📢 Broadcast to Team
                </button>
            `;
        }
        
        listEl.innerHTML = html;
    },
    
    renderConversationItem(conv) {
        const isOnline = conv.online || false;
        const unreadBadge = conv.unread_count > 0 
            ? `<span class="chat-unread-badge">${conv.unread_count}</span>` 
            : '';
        
        return `
            <div class="chat-item" 
                 onclick="ChatSidebar.openConversation(${conv.other_user_id}, '${conv.other_display_name || ''}', '${conv.conversation_type}')">
                <span class="chat-status-dot ${isOnline ? 'online' : 'offline'}"></span>
                <span class="chat-item-name">${conv.other_display_name || conv.username}</span>
                ${unreadBadge}
            </div>
        `;
    },
    
    openConversation(userId, displayName, conversationType) {
        this.currentConversation = {
            userId: userId,
            displayName: displayName,
            conversationType: conversationType
        };
        
        this.loadMessageHistory();
        this.showChatView();
    },
    
    async loadMessageHistory() {
        const { userId, displayName } = this.currentConversation;
        const myUserId = this._getUserId();
        
        const url = displayName 
            ? `${API_BASE_URL}/api/messages/history/${myUserId}/${userId}?display_name=${encodeURIComponent(displayName)}`
            : `${API_BASE_URL}/api/messages/history/${myUserId}/${userId}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        this.renderMessages(data.messages);
    },
    
    sendMessage(messageText) {
        const { userId, displayName, conversationType } = this.currentConversation;
        
        const messageData = {
            recipient_user_id: userId,
            recipient_display_name: displayName,  // NEW
            message_text: messageText,
            sender_display_name: this._getDisplayName(),  // NEW
            sender_session_token: this._getSessionToken(),  // NEW
            message_type: conversationType === 'team' ? 'private' : 'cross_user'  // NEW
        };
        
        window.SynergyRealtime.socket.emit('send_message', messageData);
    },
    
    openBroadcast() {
        this.currentConversation = {
            userId: this._getUserId(),  // Same user
            displayName: null,  // NULL = broadcast
            conversationType: 'broadcast'
        };
        
        this.showChatView();
    },
    
    _getDisplayName() {
        return localStorage.getItem('session_display_name') || 'Unknown';
    },
    
    _getSessionToken() {
        return window.SynergyRealtime?.sessionToken || null;
    }
};
```

---

## 🎬 Usage Scenarios

### Scenario 1: Team Chat (Same User-ID)

**Setup:**
- User-ID: 5 (Admin account)
- Bob (Mac): display_name = "Bob (Mac)"
- Sarah (Windows): display_name = "Sarah (Windows)"

**Bob sends private message to Sarah:**
```javascript
{
    sender_user_id: 5,
    sender_display_name: "Bob (Mac)",
    recipient_user_id: 5,  // SAME
    recipient_display_name: "Sarah (Windows)",  // FILTER
    message_type: "private"
}
```

**Result:** Only Sarah's Windows browser receives message

---

### Scenario 2: Team Broadcast

**Bob broadcasts to entire team:**
```javascript
{
    sender_user_id: 5,
    sender_display_name: "Bob (Mac)",
    recipient_user_id: 5,
    recipient_display_name: null,  // NULL = all
    message_type: "broadcast"
}
```

**Result:** All sessions (Bob's Mac, Sarah's Windows, John's iPhone) receive message

---

### Scenario 3: External User Chat

**Bob (user_id=5) messages Alice (user_id=8):**
```javascript
{
    sender_user_id: 5,
    sender_display_name: "Bob (Mac)",
    recipient_user_id: 8,  // DIFFERENT
    recipient_display_name: null,
    message_type: "cross_user"
}
```

**Result:** All Alice's sessions receive message (normal behavior)

---

## 📊 Conversation List Query Example

```sql
-- Get conversations for user_id=5
SELECT 
    -- Who is the "other" person in this conversation?
    CASE 
        WHEN sender_id = 5 THEN recipient_id
        ELSE sender_id
    END as other_user_id,
    
    -- What is their display name?
    CASE 
        WHEN sender_id = 5 THEN recipient_display_name
        ELSE sender_display_name
    END as other_display_name,
    
    -- Is this a teammate or external user?
    CASE 
        WHEN sender_id = 5 AND recipient_id = 5 THEN 'team'
        ELSE 'external'
    END as conversation_type,
    
    -- Latest message time
    MAX(created_at) as last_message_time,
    
    -- Unread count
    COUNT(*) FILTER (
        WHERE recipient_id = 5 
        AND NOT (5 = ANY(read_by))
    ) as unread_count

FROM ai_infrastructure.messages
WHERE sender_id = 5 OR recipient_id = 5
GROUP BY other_user_id, other_display_name, conversation_type
ORDER BY last_message_time DESC;
```

**Results:**
```
other_user_id | other_display_name | conversation_type | unread_count
5             | "Sarah (Windows)"  | team              | 3
5             | "John (iPhone)"    | team              | 0
8             | null               | external          | 1
12            | null               | external          | 0
```

---

## ✅ Benefits

1. **Team Messaging** - Team members can message each other privately
2. **Broadcast to Team** - Send announcements to all team members
3. **External User Messaging** - Normal messaging with other accounts
4. **Display Name Identity** - Uses existing display_name system
5. **No New Tables** - Just add columns to messages table
6. **Backward Compatible** - Existing messages still work (display_name is NULL)

---

## 🎯 Summary

### Three Message Types:

1. **Private** (team member to team member)
   - Same `user_id`, different `display_name`
   - Filtered by `recipient_display_name`

2. **Broadcast** (to all team)
   - Same `user_id`, `display_name` is NULL
   - Delivered to ALL sessions

3. **Cross-User** (external user)
   - Different `user_id`
   - Normal messaging behavior

### Key Columns:

- `sender_display_name` - Who sent it ("Bob (Mac)")
- `recipient_display_name` - Who should receive it ("Sarah (Windows)" or NULL for broadcast)
- `message_type` - 'private' | 'broadcast' | 'cross_user'

### UI Sections:

- **👥 Your Team** - Same user-id, different display names
- **💬 Other Users** - Different user-ids
- **📢 Broadcast Button** - Send to all team members

---

**This leverages your existing infrastructure - no new systems needed!**
