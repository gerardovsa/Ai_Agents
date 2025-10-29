# Thread Management Implementation Summary

## 🎯 Overview

This document outlines the implementation of a comprehensive thread/message management system for the Business AI Platform, inspired by AnythingLLM's architecture.

## 📊 Database Schema Enhancement

### New Tables Created

#### 1. **`workspaces`** - Organization Container
```sql
CREATE TABLE workspaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    metadata TEXT  -- JSON: {default_llm, temperature, etc}
);
```

**Purpose:** Group related threads into workspaces for organization

#### 2. **`threads`** - Conversation Threads
```sql
CREATE TABLE threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_slug TEXT UNIQUE NOT NULL,
    workspace_id INTEGER,
    user_id INTEGER,
    name TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    metadata TEXT,  -- JSON: {tags, pinned, etc}
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);
```

**Purpose:** Individual conversation threads within workspaces

#### 3. **`messages`** - Enhanced Message Storage
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER NOT NULL,
    thread_id INTEGER,
    session_id TEXT,
    role TEXT NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    prompt TEXT,  -- Original prompt for assistant responses
    response_data TEXT,  -- JSON: full response metadata
    user_id INTEGER,
    api_session_id TEXT,
    include BOOLEAN DEFAULT 1,  -- Include in LLM context
    feedback_score INTEGER,  -- 1=thumbs up, 0=down, NULL=none
    tool_calls TEXT,  -- JSON: tool execution details
    tokens_used INTEGER,
    response_time_ms INTEGER,
    embedding_vector TEXT,  -- JSON: vector embedding
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    metadata TEXT,  -- JSON: {edited, source, etc}
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
    FOREIGN KEY (thread_id) REFERENCES threads(id),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

**Key Fields:**
- **`include`**: Controls whether message appears in LLM context
  - `1` = included (visible to AI)
  - `0` = excluded (hidden from AI but preserved in database)
- **`feedback_score`**: User rating system
  - `1` = thumbs up
  - `0` = thumbs down
  - `NULL` = no rating
- **`tool_calls`**: JSON array of tool execution details
- **`tokens_used`**: Track token consumption per message
- **`response_time_ms`**: Performance metrics

#### 4. **`users`** - User Management
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    role TEXT DEFAULT 'user',  -- 'admin', 'user', 'readonly'
    created_at TIMESTAMP,
    last_active TIMESTAMP,
    metadata TEXT  -- JSON: preferences
);
```

#### 5. **`api_sessions`** - API Session Tracking
```sql
CREATE TABLE api_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_session_id TEXT UNIQUE NOT NULL,
    workspace_id INTEGER,
    created_at TIMESTAMP,
    last_active TIMESTAMP,
    metadata TEXT,  -- JSON: {ip_address, user_agent}
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);
```

### Performance Indexes
- `idx_messages_workspace` - Messages by workspace
- `idx_messages_thread` - Messages by thread
- `idx_messages_session` - Messages by session
- `idx_messages_role` - Messages by role
- `idx_messages_include` - Filter included/excluded messages
- `idx_messages_created` - Time-based queries
- `idx_threads_workspace` - Threads by workspace
- `idx_threads_slug` - Thread lookup

### Views for Easy Querying

#### `v_messages_with_context`
```sql
CREATE VIEW v_messages_with_context AS
SELECT 
    m.id, m.role, m.content, m.include, m.feedback_score,
    m.created_at, t.name as thread_name, t.thread_slug,
    w.name as workspace_name, w.slug as workspace_slug,
    u.username, m.tokens_used, m.response_time_ms
FROM messages m
LEFT JOIN threads t ON m.thread_id = t.id
LEFT JOIN workspaces w ON m.workspace_id = w.id
LEFT JOIN users u ON m.user_id = u.id
ORDER BY m.created_at DESC;
```

#### `v_thread_summary`
```sql
CREATE VIEW v_thread_summary AS
SELECT 
    t.id, t.thread_slug, t.name, t.created_at, t.updated_at,
    w.name as workspace_name,
    COUNT(m.id) as message_count,
    SUM(CASE WHEN m.include = 1 THEN 1 ELSE 0 END) as active_messages,
    SUM(m.tokens_used) as total_tokens,
    MAX(m.created_at) as last_message_at
FROM threads t
LEFT JOIN workspaces w ON t.workspace_id = w.id
LEFT JOIN messages m ON t.id = m.thread_id
GROUP BY t.id, t.thread_slug, t.name, t.created_at, t.updated_at, w.name
ORDER BY t.updated_at DESC;
```

## 🔧 API Endpoints

### Workspace Management

#### `GET /api/threads/workspaces`
List all workspaces
```json
Response: {
  "workspaces": [
    {
      "id": 1,
      "slug": "default",
      "name": "Default Workspace",
      "description": "Main workspace",
      "created_at": "2025-10-27T...",
      "updated_at": "2025-10-27T...",
      "metadata": {}
    }
  ]
}
```

### Thread Management

#### `GET /api/threads/{workspace_slug}/threads`
List threads in workspace
```
Query Params:
  - limit: Max threads to return (default: 50)
  - offset: Pagination offset (default: 0)

Response: {
  "threads": [
    {
      "id": 1,
      "thread_slug": "new-chat-1730000000",
      "workspace_slug": "default",
      "name": "New Chat",
      "message_count": 5,
      "active_messages": 5,
      "total_tokens": 250,
      "created_at": "2025-10-27T...",
      "updated_at": "2025-10-27T..."
    }
  ]
}
```

#### `POST /api/threads/{workspace_slug}/threads`
Create new thread
```json
Request: {
  "name": "Customer Support Chat",
  "user_id": 1,
  "metadata": { "priority": "high" }
}

Response: {
  "id": 2,
  "thread_slug": "customer-support-chat-1730000001",
  "workspace_slug": "default",
  "name": "Customer Support Chat",
  "created_at": "2025-10-27T...",
  "message_count": 0
}
```

#### `GET /api/threads/{workspace_slug}/threads/{thread_slug}`
Get thread details
```json
Response: {
  "id": 1,
  "thread_slug": "new-chat-1730000000",
  "workspace_slug": "default",
  "name": "New Chat",
  "message_count": 5,
  "created_at": "2025-10-27T...",
  "updated_at": "2025-10-27T..."
}
```

#### `DELETE /api/threads/{workspace_slug}/threads/{thread_slug}`
Delete thread and all messages
```json
Response: {
  "message": "Thread deleted"
}
```

### Message Management

#### `GET /api/threads/{workspace_slug}/threads/{thread_slug}/messages`
Get thread messages
```
Query Params:
  - include_only: Only return included messages (default: true)
  - limit: Max messages (default: 100)
  - offset: Pagination offset (default: 0)

Response: {
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Hello!",
      "include": true,
      "feedback_score": null,
      "tool_calls": [],
      "tokens_used": 10,
      "response_time_ms": null,
      "created_at": "2025-10-27T..."
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "Hi! How can I help?",
      "prompt": "Hello!",
      "include": true,
      "feedback_score": 1,
      "tool_calls": [],
      "tokens_used": 15,
      "response_time_ms": 1250,
      "created_at": "2025-10-27T..."
    }
  ]
}
```

#### `POST /api/threads/{workspace_slug}/threads/{thread_slug}/messages`
Add message to thread
```json
Request: {
  "role": "user",
  "content": "What's the weather?",
  "include": true,
  "metadata": { "source": "web" }
}

Response: {
  "id": 3,
  "role": "user",
  "content": "What's the weather?",
  "include": true,
  "created_at": "2025-10-27T..."
}
```

#### `POST /api/threads/{workspace_slug}/threads/{thread_slug}/reset`
Reset thread context (hide all messages from LLM)
```json
Response: {
  "message": "Reset 5 messages"
}
```

#### `GET /api/threads/{workspace_slug}/threads/{thread_slug}/stats`
Get thread statistics
```json
Response: {
  "thread_name": "New Chat",
  "thread_slug": "new-chat-1730000000",
  "total_messages": 10,
  "active_messages": 8,
  "user_messages": 5,
  "assistant_messages": 5,
  "total_tokens": 500,
  "avg_response_time": 1250.5,
  "thumbs_up": 3,
  "thumbs_down": 1,
  "created_at": "2025-10-27T...",
  "updated_at": "2025-10-27T..."
}
```

#### `POST /api/threads/messages/{message_id}/feedback`
Update message feedback
```json
Request: {
  "score": 1  // 1=thumbs up, 0=thumbs down, null=no rating
}

Response: {
  "message": "Feedback updated"
}
```

## 🎨 Frontend Enhancements

### 1. **Dynamic Main Content Resizing**

When user drags the AI chat panel border, the main content area automatically adjusts its width:

```javascript
// Update main content margin to accommodate chat panel width
if (mainContent && !document.body.classList.contains('chat-collapsed')) {
    mainContent.style.marginRight = newWidth + 'px';
}

// Persist width across sessions
localStorage.setItem('ai_chat_panel_width', currentWidth);
```

**CSS Changes:**
```css
.main-content {
    transition: margin-right 0.1s ease;
}

body:not(.chat-collapsed) .main-content {
    margin-right: var(--chat-panel-width, 400px);
}
```

### 2. **Enhanced ThreadManager**

Updated localStorage structure:
```javascript
{
  id: "1730000000000",
  thread_slug: "new-chat-1730000000",
  workspace_slug: "default",
  title: "First 50 chars of first user message...",
  messages: [
    {
      role: "user",
      content: "...",
      include: true,
      feedback_score: null,
      tokens_used: 10,
      response_time_ms: null,
      tool_calls: [],
      created_at: "2025-10-27T...",
      metadata: {}
    }
  ],
  created: "2025-10-27T10:00:00.000Z",
  updated: "2025-10-27T10:05:00.000Z",
  metadata: {
    tags: ["support", "urgent"],
    pinned: false,
    total_tokens: 250
  }
}
```

### 3. **Backend Sync**

ThreadManager now syncs with backend database:
```javascript
// Save thread to backend
async saveThreadToBackend(thread) {
    const response = await fetch(`${API_BASE_URL}/api/threads/default/threads`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: thread.title,
            metadata: thread.metadata
        })
    });
    return await response.json();
}

// Save messages to backend
async saveMessageToBackend(threadSlug, message) {
    const response = await fetch(
        `${API_BASE_URL}/api/threads/default/threads/${threadSlug}/messages`,
        {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(message)
        }
    );
    return await response.json();
}
```

## 📈 Key Features

### 1. **Message Include/Exclude**
- Hide messages from LLM context without deleting
- Useful for "reset conversation" functionality
- Preserves chat history for audit purposes

### 2. **Feedback System**
- Thumbs up/down on any message
- Track user satisfaction
- Identify problematic responses

### 3. **Tool Call Tracking**
- Record which tools were used
- Store tool execution results
- Performance analytics

### 4. **Token Tracking**
- Monitor token usage per message
- Calculate conversation cost
- Optimize prompt engineering

### 5. **Response Time Metrics**
- Track AI response latency
- Identify performance bottlenecks
- Compare model speeds

### 6. **Thread Statistics**
- Total messages vs active messages
- Average response time
- Feedback summary
- Token consumption

## 🚀 Upgrade Instructions

### 1. Run Database Upgrade
```bash
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
python upgrade_database.py
```

**What it does:**
- ✅ Backs up existing database
- ✅ Creates new tables
- ✅ Migrates existing session data
- ✅ Creates indexes for performance
- ✅ Creates views for easy querying

### 2. Integrate Thread Manager API

In your main Flask app:
```python
from AI_infrastructure.thread_manager import ThreadManager, create_thread_api_routes

# Initialize thread manager
thread_manager = ThreadManager()

# Add API routes
create_thread_api_routes(app, thread_manager)

# Start server
app.run(port=4000)
```

### 3. Update Frontend

The HTML file already has:
- ✅ Dynamic content resizing
- ✅ Enhanced ThreadManager with metadata
- ✅ Auto-save to localStorage
- ✅ Copy buttons (rendered + raw)

To enable backend sync, add:
```javascript
ThreadManager.enableBackendSync = true;
ThreadManager.apiBaseUrl = 'http://localhost:4000';
```

## 📚 Migration Notes

### Existing Data Preservation
- All existing sessions are migrated to `messages` table
- `session_id` links preserved for backward compatibility
- Default workspace created automatically
- No data loss during upgrade

### Breaking Changes
None! The upgrade is backward compatible:
- Old `sessions` table remains untouched
- New tables work alongside existing structure
- Frontend can continue using localStorage
- Backend sync is optional enhancement

## 🎯 Usage Examples

### Example 1: Create Thread and Add Messages
```python
from AI_infrastructure.thread_manager import ThreadManager

tm = ThreadManager()

# Create thread
thread = tm.create_thread('default', 'Customer Support Chat')

# Add user message
tm.add_message(
    'default',
    thread['thread_slug'],
    'user',
    'I need help with my order',
    include=True
)

# Add assistant response with tool calls
tm.add_message(
    'default',
    thread['thread_slug'],
    'assistant',
    'I found your order #12345',
    prompt='I need help with my order',
    tool_calls=[{
        'tool': 'woocommerce_get_orders',
        'args': {'email': 'user@example.com'},
        'result': {'order_id': 12345}
    }],
    tokens_used=50,
    response_time_ms=1250,
    include=True
)

# Get thread statistics
stats = tm.get_thread_statistics('default', thread['thread_slug'])
print(f"Total tokens: {stats['total_tokens']}")
print(f"Avg response time: {stats['avg_response_time']}ms")
```

### Example 2: Hide Old Messages
```python
# Reset thread context (hide all messages from LLM)
count = tm.reset_thread_context('default', 'customer-support-chat-1730000000')
print(f"Hidden {count} messages")

# Messages still in database but won't be sent to LLM
messages = tm.get_messages('default', 'customer-support-chat-1730000000', include_only=False)
print(f"Total messages (including hidden): {len(messages)}")
```

### Example 3: Track Feedback
```python
# User gives thumbs up to message
tm.update_message_feedback(message_id=42, feedback_score=1)

# Get statistics
stats = tm.get_thread_statistics('default', 'my-thread')
print(f"Thumbs up: {stats['thumbs_up']}")
print(f"Thumbs down: {stats['thumbs_down']}")
```

## 🔮 Future Enhancements

### Planned Features
1. **Vector Embeddings**: Store message embeddings for semantic search
2. **Message Branching**: Support conversation forks (edit history)
3. **Export/Import**: Bulk thread export to JSON/CSV
4. **Advanced Search**: Full-text search across messages
5. **Analytics Dashboard**: Visual analytics for thread metrics
6. **Workspace Sharing**: Multi-user workspace permissions
7. **Message Templates**: Save/reuse common prompts
8. **Auto-tagging**: AI-powered conversation categorization

### Performance Optimizations
- Message pagination (already implemented)
- Lazy loading for long threads
- Background indexing for search
- Connection pooling for concurrent requests

## ✅ Summary

This implementation provides:
- ✅ **Comprehensive thread management** inspired by AnythingLLM
- ✅ **Enhanced message tracking** with metadata and metrics
- ✅ **Flexible context control** (include/exclude messages)
- ✅ **Feedback system** for quality tracking
- ✅ **Tool execution logging** for debugging
- ✅ **Performance metrics** (tokens, response time)
- ✅ **Backward compatible** with existing sessions
- ✅ **RESTful API** for frontend integration
- ✅ **Database views** for easy querying
- ✅ **Auto-migration** from old structure

The system is production-ready and can scale to handle thousands of threads and millions of messages efficiently!
