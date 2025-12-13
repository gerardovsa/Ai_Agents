// ============================================================
// MESSAGE TIMESTAMPS - UI Display Implementation
// ============================================================
// Purpose: Display timestamps on message bubbles
// Location: UI/modules_internal/agents/prime_ai_chat.js
// Date: December 13, 2025
// ============================================================

// STEP 1: Update API Response to Include created_at
// ============================================================

// In backend (Python - combined_agent_worker.py or wherever you fetch messages):
/*
messages_data = [
    {
        "id": msg.id,
        "role": msg.role,
        "content": msg.content,
        "created_at": msg.created_at.isoformat() if msg.created_at else None,  # ← Add this
        "tool_calls": msg.tool_calls,
        ...
    }
    for msg in messages
]
*/

// STEP 2: Add Timestamp Display to Message Bubbles
// ============================================================

// Function to format timestamp
function formatMessageTimestamp(createdAt) {
    if (!createdAt) return '';
    
    const timestamp = new Date(createdAt);
    const now = new Date();
    const diffMs = now - timestamp;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    // Today: Show time only
    if (diffDays === 0) {
        return timestamp.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }
    
    // Yesterday
    if (diffDays === 1) {
        return 'Yesterday ' + timestamp.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }
    
    // This week: Show day + time
    if (diffDays < 7) {
        return timestamp.toLocaleDateString('en-US', {
            weekday: 'short',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }
    
    // Older: Show date + time
    return timestamp.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

// Function to get relative time (optional - for "2 mins ago" style)
function getRelativeTime(createdAt) {
    if (!createdAt) return '';
    
    const timestamp = new Date(createdAt);
    const now = new Date();
    const diffMs = now - timestamp;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffSecs < 60) return 'Just now';
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    
    return timestamp.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
    });
}

// STEP 3: Add Timestamp to Message Bubble HTML
// ============================================================

// OPTION A: Timestamp in bubble header (recommended)
function createMessageBubble(message) {
    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${message.role}-message`;
    bubble.dataset.messageId = message.id;
    
    // Create header with timestamp
    const header = document.createElement('div');
    header.className = 'message-header';
    
    const role = document.createElement('span');
    role.className = 'message-role';
    role.textContent = message.role === 'user' ? 'You' : 'AI';
    
    const timestamp = document.createElement('span');
    timestamp.className = 'message-timestamp';
    timestamp.textContent = formatMessageTimestamp(message.created_at);
    timestamp.title = message.created_at; // Full timestamp on hover
    
    header.appendChild(role);
    header.appendChild(timestamp);
    
    // Create content
    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = marked.parse(message.content);
    
    bubble.appendChild(header);
    bubble.appendChild(content);
    
    return bubble;
}

// OPTION B: Timestamp as small badge in corner
function createMessageBubbleWithBadge(message) {
    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${message.role}-message`;
    bubble.dataset.messageId = message.id;
    bubble.style.position = 'relative';
    
    // Timestamp badge
    const timestamp = document.createElement('div');
    timestamp.className = 'message-timestamp-badge';
    timestamp.textContent = formatMessageTimestamp(message.created_at);
    timestamp.title = message.created_at; // Full timestamp on hover
    
    // Content
    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = marked.parse(message.content);
    
    bubble.appendChild(timestamp);
    bubble.appendChild(content);
    
    return bubble;
}

// STEP 4: CSS Styles for Timestamps
// ============================================================

const timestampStyles = `
/* OPTION A: Header Style */
.message-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    padding-bottom: 4px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.message-role {
    font-weight: 600;
    font-size: 0.9em;
    color: rgba(255, 255, 255, 0.9);
}

.message-timestamp {
    font-size: 0.75em;
    color: rgba(255, 255, 255, 0.5);
    font-weight: 400;
}

/* OPTION B: Badge Style */
.message-timestamp-badge {
    position: absolute;
    top: 8px;
    right: 8px;
    font-size: 0.7em;
    color: rgba(255, 255, 255, 0.4);
    background: rgba(0, 0, 0, 0.2);
    padding: 2px 6px;
    border-radius: 3px;
    font-weight: 400;
    pointer-events: none;
    z-index: 1;
}

/* Hover effect for timestamp */
.message-timestamp:hover,
.message-timestamp-badge:hover {
    color: rgba(255, 255, 255, 0.8);
    cursor: help;
}

/* User message timestamp (different color) */
.user-message .message-timestamp {
    color: rgba(99, 102, 241, 0.7);  /* Indigo tint */
}

.user-message .message-timestamp-badge {
    color: rgba(99, 102, 241, 0.6);
    background: rgba(99, 102, 241, 0.1);
}

/* AI message timestamp */
.assistant-message .message-timestamp {
    color: rgba(139, 92, 246, 0.7);  /* Purple tint */
}

.assistant-message .message-timestamp-badge {
    color: rgba(139, 92, 246, 0.6);
    background: rgba(139, 92, 246, 0.1);
}
`;

// STEP 5: Integration Example
// ============================================================

// When loading conversation history:
async function loadConversationHistory(threadId) {
    const response = await fetch(`/api/threads/${threadId}/messages`);
    const messages = await response.json();
    
    const container = document.getElementById('messages-container');
    container.innerHTML = '';
    
    messages.forEach(message => {
        const bubble = createMessageBubble(message);  // ← Now includes timestamp
        container.appendChild(bubble);
    });
    
    // Auto-update relative times every minute
    setInterval(() => {
        document.querySelectorAll('.message-timestamp').forEach(el => {
            const messageId = el.closest('.message-bubble').dataset.messageId;
            const message = messages.find(m => m.id === messageId);
            if (message?.created_at) {
                el.textContent = formatMessageTimestamp(message.created_at);
            }
        });
    }, 60000);  // Update every 60 seconds
}

// When new message is added (streaming):
function addStreamingMessage(role, content, createdAt) {
    const message = {
        id: Date.now(),  // Temporary ID
        role: role,
        content: content,
        created_at: createdAt || new Date().toISOString()  // ← Use current time if not provided
    };
    
    const bubble = createMessageBubble(message);
    document.getElementById('messages-container').appendChild(bubble);
    
    return bubble;
}

// STEP 6: Backend API Update Example (Python)
// ============================================================

/*
# In combined_agent_worker.py or your message fetching function:

@app.route('/api/threads/<int:thread_id>/messages', methods=['GET'])
def get_thread_messages(thread_id):
    messages = db.session.query(Message).filter_by(thread_id=thread_id).order_by(Message.created_at).all()
    
    return jsonify([
        {
            'id': msg.id,
            'thread_id': msg.thread_id,
            'role': msg.role,
            'content': msg.content,
            'created_at': msg.created_at.isoformat() if msg.created_at else None,  # ← Add this
            'tool_calls': msg.tool_calls,
            'include': msg.include
        }
        for msg in messages
    ])
*/

// ============================================================
// QUICK TEST
// ============================================================

// Test timestamp formatting in browser console:
console.log('Just now:', formatMessageTimestamp(new Date().toISOString()));
console.log('5 mins ago:', formatMessageTimestamp(new Date(Date.now() - 5*60000).toISOString()));
console.log('2 hours ago:', formatMessageTimestamp(new Date(Date.now() - 2*3600000).toISOString()));
console.log('Yesterday:', formatMessageTimestamp(new Date(Date.now() - 24*3600000).toISOString()));
console.log('Last week:', formatMessageTimestamp(new Date(Date.now() - 7*24*3600000).toISOString()));

// Test relative time:
console.log('Relative (30s ago):', getRelativeTime(new Date(Date.now() - 30000).toISOString()));
console.log('Relative (5m ago):', getRelativeTime(new Date(Date.now() - 5*60000).toISOString()));
console.log('Relative (2h ago):', getRelativeTime(new Date(Date.now() - 2*3600000).toISOString()));
