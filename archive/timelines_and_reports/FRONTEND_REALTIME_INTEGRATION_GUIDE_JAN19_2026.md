# Frontend Real-Time Collaboration Integration Guide
**Date:** January 19, 2026  
**For:** Frontend developers implementing team collaboration features

---

## 🎯 Quick Start (3 Changes Required)

### 1. Add user_id to WebSocket Connection

**Location:** Where you initialize Socket.IO client

**Before:**
```javascript
const socket = io('/ws/synergy', {
    transports: ['websocket']
});
```

**After:**
```javascript
const socket = io('/ws/synergy', {
    transports: ['websocket'],
    query: {
        user_id: window.currentUserId  // ✅ Add this
    }
});
```

---

### 2. Send Socket ID in Streaming Requests

**Location:** Where you call `/api/agents/v4/stream/{agent_id}`

**Before:**
```javascript
const response = await fetch(`/api/agents/v4/stream/${agentId}?thread_slug=${threadSlug}`);
```

**After:**
```javascript
const response = await fetch(`/api/agents/v4/stream/${agentId}?thread_slug=${threadSlug}`, {
    headers: {
        'X-Socket-ID': socket.id  // ✅ Add this header
    }
});
```

**Why:** Prevents sender from receiving their own message (skip_sid parameter)

---

### 3. Listen for Real-Time Updates

**Location:** Add new WebSocket event listener

```javascript
socket.on('agent_thread_updated', (payload) => {
    console.log('Team member updated thread:', payload);
    
    // Payload structure:
    // {
    //     agent_id: 'agent_id',
    //     thread_slug: 'xyz',
    //     user_id: 14,
    //     message_count: 5,
    //     timestamp: 1737322000000
    // }
    
    // Refresh AI agent column if thread matches
    if (payload.thread_slug === currentThreadSlug && payload.user_id === window.currentUserId) {
        refreshAgentMessages(payload.thread_slug);
    }
});
```

---

## 📖 Complete Implementation Example

```javascript
// =========================================
// 1. Initialize WebSocket with user_id
// =========================================
const socket = io('/ws/synergy', {
    transports: ['websocket'],
    query: {
        user_id: window.currentUserId  // Get from session/state
    }
});

// =========================================
// 2. Handle Connection Events
// =========================================
socket.on('connected', (data) => {
    console.log('✅ WebSocket connected:', data);
    // data.user_id === window.currentUserId
    // data.client_id === socket.id
});

socket.on('disconnect', () => {
    console.warn('⚠️ WebSocket disconnected');
    showConnectionWarning();
});

socket.on('reconnect', () => {
    console.log('🔄 WebSocket reconnected');
    hideConnectionWarning();
});

// =========================================
// 3. Listen for Team Member Updates
// =========================================
socket.on('agent_thread_updated', (payload) => {
    console.log('📡 Team member updated thread:', payload);
    
    // Only refresh if:
    // 1. It's the current thread we're viewing
    // 2. It's for our user_id (same team)
    if (payload.thread_slug === getCurrentThreadSlug() && 
        payload.user_id === window.currentUserId) {
        
        // Option A: Refresh entire agent column
        refreshAgentColumn(payload.thread_slug);
        
        // Option B: Show notification banner
        showNotification(`Team member added message (${payload.message_count} total)`);
        
        // Option C: Auto-scroll to new message
        loadNewMessages(payload.thread_slug, payload.message_count);
    }
});

// =========================================
// 4. Send AI Agent Request with Socket ID
// =========================================
async function streamAgentMessage(agentId, threadSlug, userMessage) {
    try {
        const response = await fetch(`/api/agents/v4/stream/${agentId}?thread_slug=${threadSlug}`, {
            method: 'GET',
            headers: {
                'X-Socket-ID': socket.id  // ✅ CRITICAL: Include socket ID
            }
        });
        
        if (!response.ok) {
            throw new Error(`Stream failed: ${response.status}`);
        }
        
        // Process SSE stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const {done, value} = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.substring(6));
                    handleStreamEvent(data);
                }
            }
        }
        
    } catch (error) {
        console.error('Stream error:', error);
        showError('Failed to send message');
    }
}

// =========================================
// 5. Handle Stream Events
// =========================================
function handleStreamEvent(event) {
    switch(event.type) {
        case 'start':
            showTypingIndicator();
            break;
            
        case 'content':
            appendMessageChunk(event.content);
            break;
            
        case 'tool_use':
            showToolUsage(event.tool_name);
            break;
            
        case 'conversation_sync':
            // Backend broadcasted update - team members will receive it
            console.log('📡 Backend broadcasted sync to team');
            break;
            
        case 'complete':
            hideTypingIndicator();
            finalizeMessage(event);
            break;
            
        case 'error':
            hideTypingIndicator();
            showError(event.error);
            break;
    }
}
```

---

## 🧪 Testing Your Implementation

### Test 1: Single User (No Duplicates)

```javascript
// Open Console
console.log('Socket ID:', socket.id);
console.log('User ID:', window.currentUserId);

// Send message
streamAgentMessage('agent_id', 'thread_slug', 'Hello');

// ✅ PASS: Message appears once in UI
// ❌ FAIL: Message appears twice (missing X-Socket-ID header)
```

---

### Test 2: Team Collaboration (Real-Time Sync)

```javascript
// Computer A (Team Member 1):
// 1. Open browser, login as user_id=14
// 2. Open AI agent thread
// 3. Send message: "Test from Computer A"
// 4. Watch console: "📡 Backend broadcasted sync to team"

// Computer B (Team Member 2):
// 1. Open browser, login as user_id=14 (same user!)
// 2. Open SAME AI agent thread
// 3. Watch console: "📡 Team member updated thread: {...}"
// 4. ✅ PASS: Message from Computer A appears in < 1 second
```

---

### Test 3: WebSocket Connection Verification

```javascript
// Check connection status
if (socket.connected) {
    console.log('✅ WebSocket connected');
    console.log('Socket ID:', socket.id);
    console.log('User ID from connection:', socket.io.opts.query.user_id);
} else {
    console.error('❌ WebSocket NOT connected');
}

// Check event listeners
console.log('Registered events:', socket.listeners('agent_thread_updated').length);
// Should be: 1 (listener registered)
```

---

## 🐛 Common Issues & Fixes

### Issue 1: "Messages appear twice (duplicate)"

**Cause:** Missing `X-Socket-ID` header in streaming request

**Fix:**
```javascript
// Add header to fetch request
headers: {
    'X-Socket-ID': socket.id  // ✅ This prevents echo
}
```

**Verify:**
```javascript
// Check backend logs for:
[STREAM] 🔧 Captured app context and sender_sid: {socket.id}
```

---

### Issue 2: "Team members don't see each other's messages"

**Cause:** Missing `user_id` in WebSocket connection query

**Fix:**
```javascript
const socket = io('/ws/synergy', {
    transports: ['websocket'],
    query: {
        user_id: window.currentUserId  // ✅ Add this
    }
});
```

**Verify:**
```javascript
// Check backend logs for:
[WS] Client {client_id} auto-joined rooms: user_{user_id}, command_center
```

---

### Issue 3: "WebSocket connects but no events received"

**Cause:** Event listener not registered or socket disconnected

**Fix:**
```javascript
// Ensure listener is registered AFTER connection
socket.on('connected', (data) => {
    console.log('✅ Connected, now listening for updates');
    
    // Register listener here (or globally)
    socket.on('agent_thread_updated', (payload) => {
        console.log('📡 Update received:', payload);
    });
});
```

**Verify:**
```javascript
// Check Socket.IO debug mode
localStorage.setItem('debug', 'socket.io-client:socket');
// Reload page, check console for Socket.IO debug logs
```

---

### Issue 4: "WebSocket disconnects frequently"

**Cause:** Network issues, browser throttling, or server timeout

**Fix:**
```javascript
const socket = io('/ws/synergy', {
    transports: ['websocket'],
    query: { user_id: window.currentUserId },
    reconnection: true,  // ✅ Enable auto-reconnect
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    timeout: 20000
});

// Handle reconnection
socket.on('reconnect', (attemptNumber) => {
    console.log(`🔄 Reconnected after ${attemptNumber} attempts`);
    // Refresh data if needed
    refreshCurrentThread();
});

socket.on('reconnect_failed', () => {
    console.error('❌ Failed to reconnect after 5 attempts');
    showError('Lost connection to server. Please refresh page.');
});
```

---

## 📊 Event Payload Reference

### WebSocket Event: `agent_thread_updated`

**When Triggered:**
- Team member sends AI agent message
- AI agent completes response
- Thread is updated by any team member

**Payload Structure:**
```javascript
{
    agent_id: string,        // e.g., "agent_id"
    thread_slug: string,     // e.g., "xyz123"
    user_id: number,         // e.g., 14
    message_count: number,   // e.g., 5 (total messages in thread)
    timestamp: number        // e.g., 1737322000000 (epoch milliseconds)
}
```

**Usage:**
```javascript
socket.on('agent_thread_updated', ({agent_id, thread_slug, user_id, message_count, timestamp}) => {
    // Filter by user_id to only show updates for your team
    if (user_id === window.currentUserId) {
        console.log(`Thread ${thread_slug} updated by team member (${message_count} messages)`);
        refreshThread(thread_slug);
    }
});
```

---

### SSE Event: `conversation_sync`

**When Triggered:**
- Backend saves conversation to database
- Triggers WebSocket broadcast to team members

**Payload Structure:**
```javascript
{
    type: "conversation_sync",
    message_count: number,  // Total messages in conversation
    session_id: string      // Thread slug
}
```

**Usage:**
```javascript
// In SSE stream handler
if (event.type === 'conversation_sync') {
    console.log('📡 Backend broadcasted update to team');
    // Team members will receive WebSocket event automatically
    // No action needed in sender's browser
}
```

---

## 🔐 Security Considerations

### User ID Validation

**Current State:**
- ✅ `user_id` sent in query param (temporary)
- ⚠️ **TODO:** Add Flask-Login authentication (backend work)

**What You Should Do:**
```javascript
// Ensure user_id comes from authenticated session
const getUserId = () => {
    // Option A: From global state (set by backend on page load)
    return window.currentUserId;
    
    // Option B: From session storage (set after login)
    return parseInt(sessionStorage.getItem('user_id'));
    
    // ❌ NEVER hardcode or allow user input:
    // const userId = prompt('Enter user ID'); // ❌ INSECURE
};
```

---

### Socket ID Protection

**Current State:**
- ✅ Socket ID sent in HTTP header (secure)
- ✅ Backend uses skip_sid to prevent message echo

**What You Should Do:**
```javascript
// Always get socket.id from Socket.IO client (secure)
headers: {
    'X-Socket-ID': socket.id  // ✅ Auto-generated by Socket.IO
}

// ❌ NEVER hardcode or allow user input:
headers: {
    'X-Socket-ID': 'custom-id'  // ❌ Won't work, backend expects real socket ID
}
```

---

## 📚 Additional Resources

### Socket.IO Client Documentation:
- https://socket.io/docs/v4/client-api/
- Event listeners: `socket.on(event, callback)`
- Connection status: `socket.connected`
- Disconnect: `socket.disconnect()`

### SSE (Server-Sent Events) Guide:
- https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
- Fetch API streaming: `response.body.getReader()`

### Debugging Tools:

```javascript
// Enable Socket.IO debug mode
localStorage.setItem('debug', 'socket.io-client:socket');
// Reload page, check console for detailed logs

// Check WebSocket connection in DevTools
// Chrome: Network tab → Filter: WS → Select connection → View frames

// Monitor SSE stream
// Network tab → Filter: EventStream → Select request → View response
```

---

## ✅ Integration Checklist

- [ ] Added `user_id` to WebSocket connection query
- [ ] Added `X-Socket-ID` header to streaming requests
- [ ] Registered `agent_thread_updated` event listener
- [ ] Implemented refresh logic when team member updates thread
- [ ] Tested single-user scenario (no duplicate messages)
- [ ] Tested multi-user scenario (real-time sync works)
- [ ] Tested reconnection handling
- [ ] Verified WebSocket connection status indicator
- [ ] Added error handling for connection failures
- [ ] Documented code with comments

---

**Questions?** Contact backend team or refer to:
- `REALTIME_COLLABORATION_IMPLEMENTED_JAN19_2026.md` - Full backend implementation details
- `.github/copilot-instructions.md` - Project architecture overview

---

**Last Updated:** January 19, 2026  
**Status:** Production-Ready ✅
