# 🤖 Agent System - Complete Documentation

## Overview

The Agent System is the core orchestration engine for AI conversations, streaming responses, tool execution, and state management. It supports multiple agents working in parallel with real-time streaming, tool calling across 281+ tools, and persistent session storage.

**Key Features:**
- Multi-agent orchestration (Data Agent, Triple Agents, Stock AI)
- Real-time streaming with Server-Sent Events (SSE)
- Tool execution across 19+ platforms
- Session persistence with SQLite
- State management across agent lifecycle
- Authentication-protected endpoints

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Agent Lifecycle](#agent-lifecycle)
3. [API Reference](#api-reference)
4. [Streaming Protocol](#streaming-protocol)
5. [Tool Execution](#tool-execution)
6. [State Management](#state-management)
7. [Session Persistence](#session-persistence)
8. [Authentication](#authentication)
9. [Usage Examples](#usage-examples)
10. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### Component Structure

```
Agent System
├── flask_app.py              # Flask app initialization
├── routes/
│   └── agent_routes.py       # API endpoints (agent_bp blueprint)
├── core/
│   ├── agent_state_manager.py      # State management
│   ├── agent_worker.py             # Background worker threads
│   ├── unified_session_manager.py  # Session persistence
│   └── unified_ai_client.py        # Multi-provider AI client
└── utils/
    ├── response_helpers.py         # SSE & JSON helpers
    └── file_encoding.py            # File upload processing
```

### Data Flow

```
Client Request → Flask Route (agent_routes.py)
                      ↓
              State Manager (stores agent state)
                      ↓
              Agent Worker Thread (background processing)
                      ↓
              AI Client (Anthropic/OpenAI/DeepSeek)
                      ↓
              Tool Execution (if tools called)
                      ↓
              SSE Stream → Client (real-time updates)
                      ↓
              Session Manager (persist conversation)
```

### State Management

**Agent States:**
- `running` - Active streaming in progress
- `idle` - Agent waiting for input
- `stopped` - Agent manually stopped
- `error` - Error occurred during processing

**State Storage:**
```python
{
    "agent_id": "unique-uuid",
    "status": "running",
    "thread_id": "thread-uuid",
    "messages": [...],
    "queue": Queue(),
    "worker_thread": Thread()
}
```

---

## Agent Lifecycle

### 1. **Initialization**

**Endpoint:** `POST /api/agent/{agent_id}/start`

```javascript
const response = await fetch('http://localhost:4000/api/agent/data-agent/start', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer <token>'
    },
    body: JSON.stringify({
        message: "What tools are available?",
        thread_id: "optional-existing-thread",
        files: [] // Optional file uploads
    })
});
```

**What happens:**
1. Authentication validates user
2. State manager creates new agent state
3. Session manager loads/creates thread
4. Background worker thread starts
5. AI client begins processing
6. SSE stream URL returned to client

### 2. **Streaming**

**Endpoint:** `GET /api/agent/{agent_id}/stream`

```javascript
const eventSource = new EventSource(
    'http://localhost:4000/api/agent/data-agent/stream'
);

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'content') {
        // Append text content
        console.log(data.content);
    } else if (data.type === 'tool_use') {
        // Tool execution started
        console.log('Tool:', data.tool_name);
    } else if (data.type === 'tool_result') {
        // Tool execution completed
        console.log('Result:', data.result);
    } else if (data.type === 'done') {
        // Stream completed
        eventSource.close();
    }
};
```

**Event Types:**
- `content` - Text content chunk
- `tool_use` - Tool execution request
- `tool_result` - Tool execution result
- `error` - Error occurred
- `done` - Stream completed

### 3. **Status Checking**

**Endpoint:** `GET /api/agent/{agent_id}/status`

```javascript
const status = await fetch('http://localhost:4000/api/agent/data-agent/status')
    .then(r => r.json());

console.log(status);
// {
//     "success": true,
//     "agent_id": "data-agent",
//     "status": "running",
//     "thread_id": "thread-uuid",
//     "message_count": 5
// }
```

### 4. **Stopping**

**Endpoint:** `POST /api/agent/{agent_id}/stop`

```javascript
await fetch('http://localhost:4000/api/agent/data-agent/stop', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer <token>' }
});
```

### 5. **Cleanup**

**Endpoint:** `POST /api/agent/{agent_id}/clear`

```javascript
await fetch('http://localhost:4000/api/agent/data-agent/clear', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer <token>' }
});
```

**What happens:**
1. Worker thread stopped gracefully
2. State removed from memory
3. Session persisted to database
4. Resources released

---

## API Reference

### POST /api/agent/{agent_id}/start

Start an agent conversation with streaming.

**Authentication:** Required (Bearer token)

**Path Parameters:**
- `agent_id` (string) - Agent identifier (`data-agent`, `agent1`, `agent2`, `agent3`, `stock-ai`)

**Request Body:**
```json
{
    "message": "Your prompt here",
    "thread_id": "optional-uuid",
    "files": [
        {
            "filename": "data.csv",
            "content": "base64-encoded-content",
            "mime_type": "text/csv"
        }
    ]
}
```

**Response:**
```json
{
    "success": true,
    "agent_id": "data-agent",
    "thread_id": "thread-uuid",
    "stream_url": "/api/agent/data-agent/stream",
    "message": "Agent started"
}
```

**Error Response:**
```json
{
    "success": false,
    "error": "Agent already running"
}
```

---

### GET /api/agent/{agent_id}/stream

Stream agent responses via Server-Sent Events.

**Authentication:** Not required (authenticated via session)

**Path Parameters:**
- `agent_id` (string) - Agent identifier

**Response:** SSE stream with events:

```
event: message
data: {"type": "content", "content": "Hello"}

event: message
data: {"type": "tool_use", "tool_name": "search", "input": {...}}

event: message
data: {"type": "tool_result", "result": {...}}

event: message
data: {"type": "done"}
```

---

### GET /api/agent/{agent_id}/status

Get current agent status.

**Authentication:** Required

**Path Parameters:**
- `agent_id` (string) - Agent identifier

**Response:**
```json
{
    "success": true,
    "agent_id": "data-agent",
    "status": "running",
    "thread_id": "thread-uuid",
    "message_count": 5,
    "is_streaming": true
}
```

---

### POST /api/agent/{agent_id}/stop

Stop a running agent.

**Authentication:** Required

**Path Parameters:**
- `agent_id` (string) - Agent identifier

**Response:**
```json
{
    "success": true,
    "message": "Agent stopped"
}
```

---

### POST /api/agent/{agent_id}/clear

Clear agent state and cleanup resources.

**Authentication:** Required

**Path Parameters:**
- `agent_id` (string) - Agent identifier

**Response:**
```json
{
    "success": true,
    "message": "Agent state cleared"
}
```

---

### GET /api/agent/tools

List all available tools.

**Authentication:** Required

**Response:**
```json
{
    "success": true,
    "tools": [
        {
            "name": "gmail_send",
            "platform": "gmail",
            "description": "Send an email",
            "parameters": {
                "to": "string",
                "subject": "string",
                "body": "string"
            }
        }
    ],
    "total": 281,
    "platforms": ["gmail", "slack", "woocommerce", ...],
    "by_platform": {
        "gmail": 29,
        "slack": 24,
        "woocommerce": 29
    }
}
```

---

## Streaming Protocol

### Server-Sent Events (SSE)

The agent system uses SSE for real-time streaming:

**Event Structure:**
```javascript
{
    "type": "content" | "tool_use" | "tool_result" | "error" | "done",
    "content": "text content (for type=content)",
    "tool_name": "tool name (for type=tool_use)",
    "input": {...}, // Tool input (for type=tool_use)
    "result": {...}, // Tool result (for type=tool_result)
    "error": "error message (for type=error)"
}
```

### Client Implementation

```javascript
function connectToAgent(agentId) {
    const eventSource = new EventSource(
        `http://localhost:4000/api/agent/${agentId}/stream`
    );
    
    let fullResponse = '';
    
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        switch(data.type) {
            case 'content':
                fullResponse += data.content;
                updateUI(fullResponse);
                break;
                
            case 'tool_use':
                showToolExecution(data.tool_name, data.input);
                break;
                
            case 'tool_result':
                showToolResult(data.result);
                break;
                
            case 'error':
                handleError(data.error);
                eventSource.close();
                break;
                
            case 'done':
                finalizeResponse(fullResponse);
                eventSource.close();
                break;
        }
    };
    
    eventSource.onerror = (error) => {
        console.error('SSE error:', error);
        eventSource.close();
    };
    
    return eventSource;
}
```

---

## Tool Execution

### Tool Discovery

Tools are registered via the `ToolRegistry` class:

```python
from tools.registry import ToolRegistry

registry = ToolRegistry()
print(f"Loaded {len(registry.tools)} tools")

# Get tools by platform
gmail_tools = registry.get_tools_by_platform('gmail')
```

### Tool Execution Flow

```
1. AI decides to use tool → Returns tool_use block
2. Agent worker extracts tool name & input
3. ToolRegistry.execute_tool(name, input) called
4. Platform-specific tool executed
5. Result returned to AI
6. AI continues with result
```

### Tool Implementation Example

```python
# tools/implementations/gmail_tools.py

def gmail_send(to, subject, body):
    """
    Send an email via Gmail
    
    Args:
        to (str): Recipient email
        subject (str): Email subject
        body (str): Email body (HTML supported)
    
    Returns:
        dict: Success status and message ID
    """
    # Implementation here
    return {
        "success": True,
        "message_id": "msg-123"
    }

# Register tool
registry.register_tool(
    name="gmail_send",
    platform="gmail",
    function=gmail_send,
    description="Send an email via Gmail",
    parameters={
        "to": "string",
        "subject": "string",
        "body": "string"
    }
)
```

---

## State Management

### AgentStateManager

Central state management for all agents:

```python
from core.agent_state_manager import agent_state_manager

# Create agent state
agent_state_manager.create_agent("data-agent", thread_id="thread-123")

# Get state
state = agent_state_manager.get_state("data-agent")

# Update status
agent_state_manager.update_status("data-agent", "running")

# Add message
agent_state_manager.add_message("data-agent", {
    "role": "user",
    "content": "Hello"
})

# Stop agent
agent_state_manager.stop_agent("data-agent")

# Cleanup
agent_state_manager.clear_agent("data-agent")
```

### State Structure

```python
{
    "agent_id": "data-agent",
    "status": "running",  # running | idle | stopped | error
    "thread_id": "thread-uuid",
    "messages": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ],
    "queue": Queue(),  # For streaming chunks
    "worker_thread": Thread(),  # Background processor
    "created_at": "2025-10-29T10:00:00Z",
    "updated_at": "2025-10-29T10:05:00Z"
}
```

---

## Session Persistence

### UnifiedSessionManager

Handles conversation storage in SQLite:

```python
from core.unified_session_manager import session_manager

# Create/load session
thread_id = session_manager.create_or_load_session(
    agent_id="data-agent",
    user_id="user-123"
)

# Add message
session_manager.add_message(
    thread_id=thread_id,
    role="user",
    content="Hello"
)

# Get history
messages = session_manager.get_messages(thread_id)

# List all sessions for user
sessions = session_manager.list_user_sessions(user_id="user-123")
```

### Database Schema

```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    agent_id TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    metadata TEXT  -- JSON
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    role TEXT,  -- user | assistant | system
    content TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

---

## Authentication

All agent endpoints (except `/stream`) require authentication:

```python
from auth.user_auth import require_auth

@agent_bp.route('/agent/<agent_id>/start', methods=['POST'])
@require_auth
def start_agent(agent_id):
    # User authenticated, proceed
    pass
```

### Authentication Flow

```javascript
// 1. Login to get token
const loginResponse = await fetch('http://localhost:4000/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email: "user@example.com",
        password: "password"
    })
});

const { token } = await loginResponse.json();

// 2. Use token for agent requests
const agentResponse = await fetch('http://localhost:4000/api/agent/data-agent/start', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ message: "Hello" })
});
```

---

## Usage Examples

### Example 1: Simple Conversation

```javascript
async function simpleConversation() {
    // 1. Start agent
    const startResponse = await fetch('http://localhost:4000/api/agent/data-agent/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({
            message: "What tools do you have access to?"
        })
    });
    
    const { agent_id, stream_url } = await startResponse.json();
    
    // 2. Connect to stream
    const eventSource = new EventSource(`http://localhost:4000${stream_url}`);
    
    let response = '';
    
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'content') {
            response += data.content;
            console.log(response);
        } else if (data.type === 'done') {
            console.log('Complete:', response);
            eventSource.close();
        }
    };
}
```

### Example 2: Tool Execution

```javascript
async function executeTools() {
    const startResponse = await fetch('http://localhost:4000/api/agent/data-agent/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({
            message: "Send an email to john@example.com with subject 'Test' and body 'Hello!'"
        })
    });
    
    const { stream_url } = await startResponse.json();
    const eventSource = new EventSource(`http://localhost:4000${stream_url}`);
    
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'tool_use') {
            console.log('Executing tool:', data.tool_name);
            console.log('Input:', data.input);
        } else if (data.type === 'tool_result') {
            console.log('Tool result:', data.result);
        } else if (data.type === 'done') {
            eventSource.close();
        }
    };
}
```

### Example 3: Multi-Agent Conversation

```javascript
async function multiAgent() {
    // Start 3 agents in parallel
    const agents = ['agent1', 'agent2', 'agent3'];
    
    for (const agentId of agents) {
        const response = await fetch(`http://localhost:4000/api/agent/${agentId}/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify({
                message: `You are ${agentId}. Collaborate with other agents.`
            })
        });
        
        const { stream_url } = await response.json();
        
        // Connect each agent to its stream
        connectToStream(agentId, stream_url);
    }
}
```

---

## Troubleshooting

### Issue: Agent Not Responding

**Symptoms:** Stream connects but no data received

**Solutions:**
1. Check agent status:
```javascript
const status = await fetch('http://localhost:4000/api/agent/data-agent/status')
    .then(r => r.json());
console.log(status);
```

2. Verify worker thread is running:
```python
# In Flask logs
print(agent_state_manager.get_state("data-agent"))
```

3. Check AI client configuration:
```python
# In Flask
print(app.config['AI_CLIENT'].list_providers())
```

---

### Issue: Tool Execution Fails

**Symptoms:** `tool_result` shows error

**Solutions:**
1. List available tools:
```bash
curl http://localhost:4000/api/agent/tools
```

2. Check tool registry:
```python
from tools.registry import ToolRegistry
registry = ToolRegistry()
print(registry.get_tool('tool_name'))
```

3. Test tool directly:
```python
result = registry.execute_tool('tool_name', {'param': 'value'})
print(result)
```

---

### Issue: Stream Disconnects

**Symptoms:** EventSource closes unexpectedly

**Solutions:**
1. Check for timeout (default 30 seconds):
```python
# In flask_app.py
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
```

2. Implement reconnection:
```javascript
function connectWithRetry(agentId, maxRetries = 3) {
    let retries = 0;
    
    function connect() {
        const eventSource = new EventSource(`/api/agent/${agentId}/stream`);
        
        eventSource.onerror = () => {
            eventSource.close();
            if (retries < maxRetries) {
                retries++;
                setTimeout(connect, 1000 * retries);
            }
        };
        
        return eventSource;
    }
    
    return connect();
}
```

---

### Issue: Memory Leak

**Symptoms:** Server memory grows over time

**Solutions:**
1. Ensure agents are cleaned up:
```javascript
// Always call clear when done
await fetch(`http://localhost:4000/api/agent/${agentId}/clear`, {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + token }
});
```

2. Check for orphaned threads:
```python
# In Flask logs
import threading
print(f"Active threads: {threading.active_count()}")
```

3. Restart server periodically if needed:
```powershell
BISTOP
BISTART
```

---

## Performance

### Metrics

**Typical Performance:**
- Agent initialization: < 100ms
- First token: 200-500ms
- Streaming rate: 50-100 tokens/second
- Tool execution: 100-2000ms (varies by platform)

**Resource Usage:**
- Memory per agent: ~50MB
- CPU per agent: 5-15%
- Max concurrent agents: 10+ (depends on hardware)

### Optimization Tips

1. **Reuse threads** when possible (don't clear immediately)
2. **Batch tool calls** for efficiency
3. **Use caching** for repeated queries
4. **Limit message history** to last 10-20 messages
5. **Close streams** promptly when done

---

**Last Updated:** October 29, 2025  
**Version:** 2.0.0  
**Status:**  Production Ready
