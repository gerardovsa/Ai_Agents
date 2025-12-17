# Chat Sidebar HTML Template

## Add this HTML to business-ai-platform-v2.html (after account-sidebar section)

```html
<!-- ==================== CHAT SIDEBAR - WhatsApp Style ==================== -->
<div id="chat-sidebar" class="chat-sidebar collapsed">
    
    <!-- CHAT LIST VIEW -->
    <div id="chat-list-view">
        <!-- Header -->
        <div class="chat-sidebar-header">
            <div class="chat-header-left">
                <div class="chat-header-title">
                    <i class="fas fa-comments"></i>
                    <h3>Messages</h3>
                </div>
            </div>
            <div class="chat-header-right">
                <button class="chat-header-btn" onclick="ChatSidebar.close()" title="Close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
        
        <!-- Search Bar -->
        <div class="chat-search-bar">
            <div class="chat-search-input-wrapper">
                <i class="fas fa-search"></i>
                <input type="text" id="chat-search-input" placeholder="Search conversations...">
            </div>
        </div>
        
        <!-- Chat List -->
        <div class="chat-list-container" id="chat-list-container">
            <!-- Populated dynamically by ChatSidebar.refreshChatList() -->
        </div>
    </div>
    
    <!-- CONVERSATION VIEW -->
    <div id="chat-conversation-view">
        <!-- Header -->
        <div class="chat-sidebar-header">
            <div class="chat-header-left">
                <button class="chat-back-btn" onclick="ChatSidebar.showChatList()">
                    <i class="fas fa-arrow-left"></i>
                </button>
                <div class="chat-conversation-user">
                    <span class="chat-conversation-user-name" id="conv-user-name">User Name</span>
                    <span class="chat-conversation-user-device" id="conv-user-device">Windows • Online</span>
                </div>
            </div>
            <div class="chat-header-right">
                <button class="chat-header-btn voice-call" onclick="ChatSidebar.startVoiceCall()" title="Voice Call">
                    <i class="fas fa-phone"></i>
                </button>
                <button class="chat-header-btn" onclick="ChatSidebar.showChatList()" title="Back">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
        
        <!-- Messages Container -->
        <div class="chat-messages-container" id="chat-messages-container">
            <!-- Messages populated dynamically -->
        </div>
        
        <!-- Typing Indicator -->
        <div class="chat-typing-indicator" id="chat-typing-indicator">
            <span class="chat-typing-text">User is typing</span>
            <span class="chat-typing-dots">
                <span>.</span><span>.</span><span>.</span>
            </span>
        </div>
        
        <!-- Message Input -->
        <div class="chat-message-input-container">
            <textarea 
                id="chat-message-input" 
                placeholder="Type a message..." 
                rows="1"
                style="height: auto;"></textarea>
            <button class="chat-send-btn" onclick="ChatSidebar.sendMessage()">
                <i class="fas fa-paper-plane"></i>
            </button>
        </div>
    </div>
    
    <!-- VOICE CALL VIEW -->
    <div id="chat-call-view">
        <div class="chat-call-avatar">
            <img src="/api/user/avatar/default" alt="User" id="chat-call-avatar">
        </div>
        
        <div class="chat-call-user-name" id="chat-call-user-name">User Name</div>
        <div class="chat-call-status" id="chat-call-status">Calling...</div>
        <div class="chat-call-timer" id="chat-call-timer">00:00</div>
        
        <div class="chat-call-controls">
            <button class="chat-call-btn mute" id="chat-mute-btn" onclick="ChatSidebar.toggleMute()" title="Mute">
                <i class="fas fa-microphone"></i>
            </button>
            
            <button class="chat-call-btn end" onclick="ChatSidebar.endCall()" title="End Call">
                <i class="fas fa-phone-slash"></i>
            </button>
        </div>
        
        <!-- Hidden audio element for remote stream -->
        <audio id="chat-remote-audio" autoplay></audio>
    </div>
</div>

<!-- CHAT SIDEBAR TOGGLE BUTTON -->
<button class="chat-sidebar-toggle" onclick="ChatSidebar.toggle()" title="Messages">
    <i class="fas fa-comments"></i>
    <span class="chat-unread-badge" id="chat-unread-badge" style="display: none;">0</span>
</button>
```

## Add these script and CSS links to <head> section:

```html
<!-- Chat Sidebar CSS -->
<link rel="stylesheet" href="shared/css/chat-sidebar.css">

<!-- Chat Sidebar JavaScript -->
<script src="shared/js/chat-sidebar.js"></script>
```

## Backend API Endpoints Needed

Add these endpoints to flask_app.py:

```python
@app.route('/api/messages/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations for current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get conversations with last message and unread count
    conversations = message_service.get_user_conversations(user_id)
    
    return jsonify({'conversations': conversations})

@app.route('/api/messages/mark-read', methods=['POST'])
def mark_conversation_read():
    """Mark all messages in a conversation as read"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    other_user_id = data.get('user_id')
    
    if not other_user_id:
        return jsonify({'error': 'Missing user_id'}), 400
    
    # Mark all messages from other_user_id as read
    message_service.mark_conversation_read(user_id, other_user_id)
    
    return jsonify({'success': True})

@app.route('/api/messages/<message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Delete a message"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Verify message belongs to user
    message = message_service.get_message(message_id)
    if not message or message['from_user_id'] != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    
    message_service.delete_message(message_id)
    
    return jsonify({'success': True})

@app.route('/api/user/avatar/<user_id>', methods=['GET'])
def get_user_avatar(user_id):
    """Get user avatar image"""
    # Return default avatar or user's custom avatar
    # For now, redirect to a default avatar service
    return redirect(f'https://ui-avatars.com/api/?name={user_id}&background=4A9EFF&color=fff&size=128')
```

## WebSocket Events for Voice Calling

Add these to flask_app.py SocketIO handlers:

```python
@socketio.on('voice_call_offer')
def handle_voice_call_offer(data):
    """Forward voice call offer to recipient"""
    to_user_id = data.get('to_user_id')
    offer = data.get('offer')
    
    if not to_user_id or not offer:
        return
    
    # Get sender info
    from_user_id = session.get('user_id')
    from_user_name = session.get('username', 'Unknown User')
    
    # Forward to recipient
    emit('voice_call_offer', {
        'from_user_id': from_user_id,
        'from_user_name': from_user_name,
        'offer': offer
    }, room=f'user_{to_user_id}')
    
    logger.info(f"Voice call offer from {from_user_id} to {to_user_id}")

@socketio.on('voice_call_answer')
def handle_voice_call_answer(data):
    """Forward voice call answer to caller"""
    to_user_id = data.get('to_user_id')
    answer = data.get('answer')
    
    if not to_user_id or not answer:
        return
    
    from_user_id = session.get('user_id')
    
    # Forward to caller
    emit('voice_call_answer', {
        'from_user_id': from_user_id,
        'answer': answer
    }, room=f'user_{to_user_id}')
    
    logger.info(f"Voice call answer from {from_user_id} to {to_user_id}")

@socketio.on('voice_call_ice_candidate')
def handle_ice_candidate(data):
    """Forward ICE candidate to peer"""
    to_user_id = data.get('to_user_id')
    candidate = data.get('candidate')
    
    if not to_user_id or not candidate:
        return
    
    from_user_id = session.get('user_id')
    
    # Forward to peer
    emit('voice_call_ice_candidate', {
        'from_user_id': from_user_id,
        'candidate': candidate
    }, room=f'user_{to_user_id}')

@socketio.on('voice_call_ended')
def handle_voice_call_ended(data):
    """Forward call end notification"""
    to_user_id = data.get('to_user_id')
    reason = data.get('reason', 'ended')
    
    if not to_user_id:
        return
    
    from_user_id = session.get('user_id')
    
    # Forward to peer
    emit('voice_call_ended', {
        'from_user_id': from_user_id,
        'reason': reason
    }, room=f'user_{to_user_id}')
    
    logger.info(f"Voice call ended: {from_user_id} -> {to_user_id} ({reason})")
```

## Database Schema Updates

Add to message_service.py:

```python
def get_user_conversations(self, user_id):
    """Get all conversations with last message and unread count"""
    with self.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT
                    CASE 
                        WHEN from_user_id = %s THEN to_user_id
                        ELSE from_user_id
                    END as user_id,
                    (SELECT username FROM users WHERE id = 
                        CASE 
                            WHEN from_user_id = %s THEN to_user_id
                            ELSE from_user_id
                        END
                    ) as user_name,
                    (SELECT message FROM messages m2 
                     WHERE (m2.from_user_id = user_id AND m2.to_user_id = %s)
                        OR (m2.from_user_id = %s AND m2.to_user_id = user_id)
                     ORDER BY m2.timestamp DESC LIMIT 1
                    ) as last_message,
                    (SELECT timestamp FROM messages m2 
                     WHERE (m2.from_user_id = user_id AND m2.to_user_id = %s)
                        OR (m2.from_user_id = %s AND m2.to_user_id = user_id)
                     ORDER BY m2.timestamp DESC LIMIT 1
                    ) as last_message_time,
                    (SELECT COUNT(*) FROM messages m2 
                     WHERE m2.from_user_id = user_id 
                       AND m2.to_user_id = %s
                       AND NOT (%s = ANY(m2.read_by))
                    ) as unread_count
                FROM messages
                WHERE from_user_id = %s OR to_user_id = %s
                ORDER BY last_message_time DESC
            """, (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id))
            
            return cur.fetchall()

def mark_conversation_read(self, user_id, other_user_id):
    """Mark all messages from other_user_id as read"""
    with self.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE messages
                SET read_by = array_append(read_by, %s)
                WHERE from_user_id = %s 
                  AND to_user_id = %s
                  AND NOT (%s = ANY(read_by))
            """, (user_id, other_user_id, user_id, user_id))
            conn.commit()
```

## Features Included

✅ **WhatsApp-Style Chat Interface**
- Message bubbles (sent/received)
- Chat list with avatars
- Online/offline indicators
- Unread message counts
- Search conversations

✅ **Message Actions**
- Copy message text
- Reply to message
- Delete message (sender only)
- Message timestamps
- Read receipts (✓ delivered, ✓✓ read)

✅ **Voice Calling**
- WebRTC peer-to-peer voice calls
- Call controls (mute, end call)
- Call timer
- Incoming call notifications

✅ **Real-time Features**
- Typing indicators
- Online/offline status
- Instant message delivery
- Read receipt updates

✅ **Moveable Sidebar**
- Smooth slide-in animation
- Collapsible toggle button
- Unread badge on toggle
- Responsive design

## Usage

```javascript
// Open chat sidebar
ChatSidebar.toggle();

// Open conversation with specific user
ChatSidebar.openConversation(userId, userName, device);

// Start voice call
ChatSidebar.startVoiceCall();

// Send message
ChatSidebar.sendMessage();

// Copy message
ChatSidebar.copyMessage(messageId);
```
