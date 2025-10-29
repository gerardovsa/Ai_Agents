# 🏗️ Session Orchestration Architecture

## System Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ Chat Window  │  │ Kanban Board │  │ Session List │            │
│  │              │  │              │  │              │            │
│  │ 💬 Messages  │  │ 📊 Columns   │  │ 📋 Active    │            │
│  │ 📎 Files     │  │ 🎯 Tasks     │  │ ⏸️  Paused   │            │
│  │ [Resume] →   │  │ Drag & Drop  │  │ ✅ Complete  │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└─────────────────────────────┬──────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────┐
│                         API LAYER                                  │
│  /api/sessions/create           POST   Create new session          │
│  /api/sessions/:id/messages     POST   Add message                 │
│  /api/sessions/:id/tasks        POST   Create task                 │
│  /api/sessions/:id/resume       GET    Get resume context          │
│  /api/sessions/kanban           GET    Get Kanban board            │
│  /api/sessions/active           GET    List active sessions        │
│  /api/sessions/:id/move         PATCH  Move Kanban column          │
└─────────────────────────────┬──────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────┐
│                    SESSION ORCHESTRATOR                            │
│                    (Core Intelligence)                             │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ Session Manager                                           │    │
│  │ • Create/Update/Delete sessions                          │    │
│  │ • Track conversation history                             │    │
│  │ • Store context (messages, files, work)                  │    │
│  │ • Manage session lifecycle                               │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ Task Linker                                               │    │
│  │ • Link tasks to sessions                                 │    │
│  │ • Store session ID in Google Tasks notes (JSON)          │    │
│  │ • Track next steps                                       │    │
│  │ • Sync task status                                       │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ Kanban Manager                                            │    │
│  │ • Organize sessions in columns                           │    │
│  │ • Move between: backlog → in_progress → review → done    │    │
│  │ • Priority sorting                                       │    │
│  │ • Status tracking                                        │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ Resume Engine                                             │    │
│  │ • Generate comprehensive context prompts                 │    │
│  │ • Load conversation history                              │    │
│  │ • Retrieve created resources                             │    │
│  │ • Prepare AI with full memory                            │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬──────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────┐
│                    PROACTIVE AI SYSTEM                             │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ Event Trigger System                                      │    │
│  │ • Monitor task deadlines                                 │    │
│  │ • Check session activity                                 │    │
│  │ • Detect stuck work                                      │    │
│  │ • Daily/weekly triggers                                  │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ Notification Generator                                    │    │
│  │ • Create session-aware notifications                     │    │
│  │ • Include context summary                                │    │
│  │ • Generate "Resume" button with session_id               │    │
│  │ • Format for email/push/browser                          │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬──────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────┐
│                    STORAGE & INTEGRATION                           │
│                                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Database   │  │ Google Tasks│  │ AI Personal │              │
│  │             │  │             │  │    Tasks    │              │
│  │ Sessions    │  │ User Tasks  │  │ AI Work     │              │
│  │ Messages    │  │ + Session ID│  │ + Memory    │              │
│  │ Resources   │  │ in notes    │  │             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└────────────────────────────────────────────────────────────────────┘
```

## Data Flow: Complete Workflow

### 1. User Starts New Work

```
User Types Message
      │
      ▼
┌─────────────────────┐
│ "Help me create     │
│ email campaign"     │
└─────────────────────┘
      │
      ▼
Session Orchestrator.create_session()
      │
      ├─→ Generate unique session_id
      ├─→ Store initial message
      ├─→ Set status: 'active'
      ├─→ Kanban: 'in_progress'
      │
      ▼
┌─────────────────────────────────────┐
│ Session Object Created              │
│ ID: sess_20251028_john_email_camp   │
│ Status: active                      │
│ Messages: [user message]            │
│ Context: {}                         │
└─────────────────────────────────────┘
```

### 2. AI Works in Session

```
AI Processes Message
      │
      ▼
Uses Tools (gmail, docs, etc.)
      │
      ▼
Session Orchestrator.add_message_to_session()
      │
      ├─→ Store AI response
      ├─→ Track tools used
      ├─→ Record created resources
      ├─→ Update last_active timestamp
      │
      ▼
┌─────────────────────────────────────┐
│ Session Updated                     │
│ Messages: [user, AI, user, AI...]   │
│ Tools Used: [gmail_send, docs...]   │
│ Resources: [doc_url, sheet_url...]  │
│ Topics: [email, marketing...]       │
└─────────────────────────────────────┘
```

### 3. AI Creates Task

```
AI Determines Work Needed
      │
      ▼
Session Orchestrator.create_task_for_session()
      │
      ├─→ Build task title with session reference
      ├─→ Create JSON payload with full context
      ├─→ Call ai_create_task() (Google Tasks API)
      ├─→ Store task_id in session
      ├─→ Create event trigger for deadline
      │
      ▼
┌─────────────────────────────────────────────────────┐
│ Google Task Created                                 │
│ ID: task_abc123                                     │
│ Title: "🔴 Send emails [Session: Email Campaign]"  │
│ Notes: {                                            │
│   "session_id": "sess_...",                         │
│   "context": {...},                                 │
│   "next_steps": [...]                               │
│ }                                                   │
│ Due: 2025-10-30T14:00:00Z                          │
└─────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│ Event Trigger Created               │
│ Type: DEADLINE_APPROACHING          │
│ Fires: 24h before due               │
│ Payload: {session_id, task_id}      │
└─────────────────────────────────────┘
```

### 4. Time Passes (User Leaves)

```
User Closes Browser
      │
      ▼
Session Persists in Memory/Database
      │
      ├─→ Status: 'active' (not paused)
      ├─→ Kanban: 'in_progress'
      ├─→ Associated Tasks: [task_abc123]
      ├─→ Last Active: 2025-10-28T10:30:00
      │
      ▼
Background Event Monitor Running
      │
      └─→ Checks every 60 seconds
          for triggers ready to fire
```

### 5. Deadline Approaching (Proactive Notification)

```
Event Monitor Detects Trigger
      │
      ▼
24 Hours Before Deadline
      │
      ▼
Event Trigger System.check_triggers()
      │
      └─→ Returns: [trigger_for_session_abc]
      │
      ▼
Session Orchestrator.get_session_notification_message()
      │
      ├─→ Load session context
      ├─→ Format notification with:
      │   • Task title
      │   • Time remaining
      │   • Next steps
      │   • Resources created
      │   • Resume button with session_id
      │
      ▼
┌─────────────────────────────────────────────────┐
│ Notification Sent to User                       │
│ "⏰ Task due in 24h in 'Email Campaign'"        │
│ [Resume Session →] ← Click opens session        │
└─────────────────────────────────────────────────┘
```

### 6. User Clicks Resume

```
User Clicks "Resume Session" Button
      │
      ▼
Frontend: GET /api/sessions/{session_id}/resume
      │
      ▼
Session Orchestrator.get_session_resume_prompt()
      │
      ├─→ Load complete session object
      ├─→ Build comprehensive prompt with:
      │   • Session title, status, priority
      │   • Conversation summary
      │   • All messages (last 5)
      │   • Tools used
      │   • Resources created
      │   • Next steps
      │   • Instructions for AI
      │
      ▼
┌─────────────────────────────────────────────────┐
│ AI Receives Resume Context                      │
│                                                 │
│ "RESUMING CONVERSATION SESSION                  │
│  Session: Email Marketing Campaign              │
│  Last active: 3 days ago                        │
│  Summary: Created 5 email templates             │
│  Next: Send test batch                          │
│  Resources: [Email Templates Doc]               │
│  Recent messages: [...]"                        │
└─────────────────────────────────────────────────┘
      │
      ▼
AI Generates Response With Full Memory
      │
      └─→ "I'm back to continue our email campaign!
          Last time we created templates. Let's send
          the test batch now..."
```

## Component Interaction Diagram

```
┌──────────────┐         ┌──────────────────┐         ┌──────────────┐
│              │         │                  │         │              │
│    USER      │◄────────┤  SESSION ORCH.   │────────►│  GOOGLE TASKS│
│              │         │                  │         │              │
└──────┬───────┘         └────────┬─────────┘         └──────────────┘
       │                          │
       │ 1. Start conversation    │
       ├─────────────────────────►│
       │                          │ 2. Create session
       │                          │ 3. Store context
       │                          │
       │ 4. AI responds           │
       │◄─────────────────────────┤
       │                          │
       │ 5. AI creates task       │
       │                          ├──────────────────────────►
       │                          │ 6. Task with session_id
       │                          │
       │ (Time passes)            │
       │                          │
       │                          ▼
       │                   ┌──────────────┐
       │                   │ EVENT SYSTEM │
       │                   │ (monitors)   │
       │                   └──────┬───────┘
       │                          │
       │ 7. Notification          │ 8. Deadline trigger
       │◄─────────────────────────┤    fires
       │   "Task due in 24h"      │
       │   [Resume] button        │
       │                          │
       │ 9. Click resume          │
       ├─────────────────────────►│
       │                          │ 10. Load session
       │                          │ 11. Build context
       │ 12. Full context to AI   │
       │◄─────────────────────────┤
       │                          │
       │ 13. AI continues work    │
       │◄─────────────────────────┤
       │     (with full memory!)  │
       │                          │
```

## Session State Machine

```
                    create_session()
                          │
                          ▼
                    ┌──────────┐
                    │  ACTIVE  │◄──────────┐
                    └────┬─────┘           │
                         │                 │
          add_message()  │  pause()        │ resume()
          create_task()  │                 │
                         │                 │
                         ▼                 │
                    ┌──────────┐           │
                    │  PAUSED  ├───────────┘
                    └────┬─────┘
                         │
           move_to_done()│
                         │
                         ▼
                    ┌──────────┐
                    │COMPLETED │
                    └──────────┘
```

## Kanban State Machine

```
    create_session()
          │
          ▼
    ┌──────────┐
    │ BACKLOG  │
    └────┬─────┘
         │ start_work()
         ▼
    ┌──────────┐
    │IN_PROGRESS│
    └────┬─────┘
         │ submit_for_review()
         ▼
    ┌──────────┐
    │  REVIEW  │
    └────┬─────┘
         │ complete()
         ▼
    ┌──────────┐
    │   DONE   │
    └──────────┘
```

## Database Schema (Production)

```sql
-- Sessions table
CREATE TABLE conversation_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    status VARCHAR(50) DEFAULT 'active',
    project_name VARCHAR(255),
    kanban_column VARCHAR(50) DEFAULT 'in_progress',
    priority VARCHAR(20) DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags JSON,
    
    INDEX idx_user_status (user_id, status),
    INDEX idx_project (project_name),
    INDEX idx_kanban (kanban_column)
);

-- Messages table (conversation history)
CREATE TABLE session_messages (
    message_id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    tools_used JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES conversation_sessions(session_id)
        ON DELETE CASCADE,
    INDEX idx_session_time (session_id, timestamp)
);

-- Resources created in session
CREATE TABLE session_resources (
    resource_id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- 'doc', 'sheet', 'email', etc.
    title VARCHAR(500),
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES conversation_sessions(session_id)
        ON DELETE CASCADE
);

-- Tasks linked to sessions
CREATE TABLE session_tasks (
    task_id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    google_task_id VARCHAR(255),  -- ID in Google Tasks
    title VARCHAR(500) NOT NULL,
    due_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium',
    next_steps JSON,
    
    FOREIGN KEY (session_id) REFERENCES conversation_sessions(session_id)
        ON DELETE CASCADE
);
```

## Integration Points

### With Existing Systems

```
Session Orchestrator
        │
        ├─→ Context Engine (user profiles, temporal awareness)
        ├─→ Event Trigger System (deadline monitoring)
        ├─→ AI Personal Tasks (AI's own work tracking)
        ├─→ Google Tasks API (task storage)
        ├─→ Agent Routes (AI conversation endpoints)
        └─→ Notification System (email, push, browser)
```

### API Integration Flow

```python
# In agent_routes.py

from core.session_orchestrator import get_session_orchestrator

@app.route('/api/agent/chat', methods=['POST'])
def agent_chat():
    data = request.json
    user_id = get_user_id()
    message = data['message']
    session_id = data.get('session_id')  # Optional: resume existing
    
    orchestrator = get_session_orchestrator()
    
    # Create or load session
    if not session_id:
        session_id = orchestrator.create_session(
            user_id=user_id,
            title=extract_title(message),
            initial_message=message
        )
    else:
        # Resuming existing session
        resume_context = orchestrator.get_session_resume_prompt(session_id)
        # Prepend to system prompt
        
    # Add user message
    orchestrator.add_message_to_session(session_id, 'user', message)
    
    # Call AI (with session context)
    ai_response = call_ai(message, session_context)
    
    # Add AI response
    orchestrator.add_message_to_session(
        session_id, 
        'assistant', 
        ai_response,
        tools_used=extract_tools(ai_response)
    )
    
    return {
        'session_id': session_id,
        'response': ai_response
    }
```

## Performance Considerations

### Caching Strategy

```
┌─────────────────────────────────────┐
│ In-Memory Cache (Redis)             │
│ • Active sessions (last 24h)        │
│ • Recent messages (last 50/session) │
│ • User's active sessions list       │
│ TTL: 24 hours                       │
└─────────────────────────────────────┘
         │
         ▼ (on miss)
┌─────────────────────────────────────┐
│ Database (PostgreSQL/MongoDB)       │
│ • All sessions                      │
│ • Complete message history          │
│ • Resources, tasks                  │
│ Persistent storage                  │
└─────────────────────────────────────┘
```

### Scalability

- **Horizontal**: Multiple orchestrator instances (stateless)
- **Session storage**: Distributed database (sharded by user_id)
- **Event monitoring**: Background workers (one per region)
- **Notifications**: Queue-based (RabbitMQ, AWS SQS)

## Security Considerations

1. **Session ID validation**: Verify user owns session
2. **Message encryption**: Encrypt sensitive content in DB
3. **Access control**: User can only access their sessions
4. **Task linking**: Verify task belongs to user before linking
5. **Rate limiting**: Prevent session spam creation

---

**Created:** October 28, 2025  
**Status:** ✅ Architecture Complete  
**Implementation:** Session Orchestrator code ready (`session_orchestrator.py`)
