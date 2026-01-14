# AI Infrastructure API Reference

**Complete API documentation for unified session manager and Anthropic client**

---

## Table of Contents
1. [UnifiedSessionManager](#unifiedsessionmanager)
2. [UnifiedAnthropicClient](#unifiedanthropicclient)
3. [Flask Integration](#flask-integration)
4. [SSE Event Format](#sse-event-format)

---

## UnifiedSessionManager

**Location**: `AI_infrastructure/core/unified_session_manager.py`

Single source of truth for session management with SQLite persistence.

### Initialization

```python
from core.unified_session_manager import session_manager

# Singleton instance - already initialized
# Uses: AI_infrastructure/sessions.db
```

### Methods

#### `create_session(ui_context, agent_id=None)`

Create new session with unique ID.

**Parameters:**
- `ui_context` (str): UI context identifier
  - `'stock_chat'` - Stock AI Chat
  - `'data_agent_chat'` - Data Agent Chat
  - `'single_viewer'` - Single Agent Viewer
  - `'triple_agent'` - Triple Agent Interface
- `agent_id` (str, optional): Agent ID for Triple Agent ('1', '2', '3')

**Returns:** `str` - UUID session ID

**Example:**
```python
# Create session for Stock Chat
session_id = session_manager.create_session('stock_chat')
# Returns: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'

# Create session for Triple Agent #2
session_id = session_manager.create_session('triple_agent', agent_id='2')
```

---

#### `get_session(session_id)`

Retrieve session data.

**Parameters:**
- `session_id` (str): UUID session ID

**Returns:** `dict` or `None`

**Session Structure:**
```python
{
    'session_id': 'uuid-string',
    'ui_context': 'stock_chat',
    'agent_id': None or '1'|'2'|'3',
    'conversation': [
        {'role': 'user', 'content': 'Hello'},
        {'role': 'assistant', 'content': 'Hi!'}
    ],
    'created_at': '2025-10-23T10:30:00',
    'updated_at': '2025-10-23T10:31:00'
}
```

**Example:**
```python
session = session_manager.get_session('abc-123')

if session:
    print(f"UI: {session['ui_context']}")
    print(f"Messages: {len(session['conversation'])}")
else:
    print("Session not found")
```

---

#### `update_conversation(session_id, conversation)`

Update conversation history for session.

**Parameters:**
- `session_id` (str): UUID session ID
- `conversation` (list): List of message dicts

**Returns:** `bool` - True if successful

**Example:**
```python
conversation = [
    {'role': 'user', 'content': 'Show me stocks'},
    {'role': 'assistant', 'content': 'Here are the stocks...'}
]

success = session_manager.update_conversation(session_id, conversation)
```

---

#### `get_queue(session_id)`

Get SSE queue for session (used for streaming events).

**Parameters:**
- `session_id` (str): UUID session ID

**Returns:** `Queue` - Thread-safe queue instance

**Example:**
```python
queue = session_manager.get_queue(session_id)

# Put event in queue
queue.put({
    'type': 'content_block_delta',
    'index': 0,
    'delta': {'text': 'Hello'}
})

# Get event from queue (in SSE stream)
event = queue.get(timeout=30)
```

---

#### `get_lock(session_id)`

Get execution lock for session (prevents concurrent requests).

**Parameters:**
- `session_id` (str): UUID session ID

**Returns:** `threading.Lock` - Thread lock instance

**Example:**
```python
lock = session_manager.get_lock(session_id)

# Check if locked
if lock.locked():
    return jsonify({'error': 'Already processing'}), 409

# Use lock
with lock:
    # Process request
    pass
```

---

#### `cleanup_inactive_sessions(hours=24)`

Remove old inactive sessions.

**Parameters:**
- `hours` (int, optional): Remove sessions older than this (default: 24)

**Returns:** `int` - Number of sessions removed

**Example:**
```python
# Cleanup sessions older than 7 days
removed = session_manager.cleanup_inactive_sessions(hours=168)
print(f"Removed {removed} old sessions")
```

---

## UnifiedAnthropicClient

**Location**: `AI_infrastructure/core/unified_anthropic_client.py`

Single reusable Anthropic client with system prompt routing.

### Initialization

```python
from core.unified_anthropic_client import init_anthropic_client

config_path = 'config/database-config.json'
anthropic_client = init_anthropic_client(config_path)

# Singleton instance - reuse across all requests
```

### Methods

#### `process_streaming(session_id, session_data, prompt, files=None, sse_callback=None)`

Process user prompt with Anthropic API and stream response.

**Parameters:**
- `session_id` (str): UUID session ID
- `session_data` (dict): Session dict from session_manager
- `prompt` (str): User message
- `files` (list, optional): Uploaded files (for Vision API)
- `sse_callback` (callable, optional): Function to call with SSE events

**Returns:** `list` - Updated conversation with AI response

**Example:**
```python
import asyncio

async def example():
    session = session_manager.get_session(session_id)
    queue = session_manager.get_queue(session_id)
    
    # Process with streaming
    updated_conversation = await anthropic_client.process_streaming(
        session_id=session_id,
        session_data=session,
        prompt='Show me all stocks',
        sse_callback=lambda event: queue.put(event)
    )
    
    # Save updated conversation
    session_manager.update_conversation(session_id, updated_conversation)
    
    return updated_conversation

# Run in event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
conversation = loop.run_until_complete(example())
```

---

#### `_convert_event_to_sse(event)`

Convert Anthropic event to SSE format (internal method).

**Parameters:**
- `event`: Anthropic stream event

**Returns:** `dict` - SSE event dict

**SSE Event Types:**
- `content_block_start` - New content block starting
- `content_block_delta` - Incremental content update
- `content_block_stop` - Content block finished
- `tool_result` - Tool execution result
- `done` - Message complete

---

#### `_handle_tool_use(tool_use)`

Execute server-side tool (internal method).

**Parameters:**
- `tool_use` (dict): Tool use block from Anthropic

**Returns:** `dict` - Tool result

**Example Tool Use:**
```python
tool_use = {
    'id': 'tool-123',
    'name': 'execute_sql_query',
    'input': {
        'connection_id': 'pgsql://server/db',
        'query': 'SELECT * FROM stocks',
        'query_name': 'List Stocks'
    }
}

result = anthropic_client._handle_tool_use(tool_use)
# Returns: {'tool_use_id': 'tool-123', 'content': 'Query results...'}
```

---

### System Prompts

System prompts automatically selected based on `ui_context`:

| UI Context | Method | Description |
|------------|--------|-------------|
| `stock_chat` | `_get_stock_chat_prompt()` | Stock management AI |
| `data_agent_chat` | `_get_data_agent_prompt()` | SQL/data analysis AI |
| `single_viewer` | `_get_single_viewer_prompt()` | Single agent viewer |
| `triple_agent` | `_get_triple_agent_prompt(agent_id)` | Triple agent (1, 2, or 3) |

**Example:**
```python
# Automatically selected based on session ui_context
session = session_manager.get_session(session_id)
ui_context = session['ui_context']

# Client selects correct prompt internally
# Stock Chat → _get_stock_chat_prompt()
# Data Agent → _get_data_agent_prompt()
```

---

## Flask Integration

**Location**: `AI_infrastructure/flask_integration.py`

Clean Flask routes using unified infrastructure.

### Setup

```python
from flask import Flask
from AI_infrastructure.flask_integration import create_unified_routes

app = Flask(__name__)
create_unified_routes(app, config_path='config/database-config.json')
```

### Endpoints

#### `POST /api/session/create`

Create new session.

**Request JSON:**
```json
{
    "ui_context": "stock_chat",
    "agent_id": "2"
}
```

**Response JSON:**
```json
{
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Example:**
```javascript
const response = await fetch('/api/session/create', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ui_context: 'stock_chat'})
});

const data = await response.json();
const sessionId = data.session_id;
```

---

#### `POST /api/chat/send`

Send message to AI.

**Request JSON:**
```json
{
    "session_id": "uuid-string",
    "prompt": "Show me all stocks"
}
```

**Request FormData (for file uploads):**
```javascript
const formData = new FormData();
formData.append('session_id', sessionId);
formData.append('prompt', 'Analyze this invoice');
formData.append('files', fileInput.files[0]);

await fetch('/api/chat/send', {
    method: 'POST',
    body: formData
});
```

**Response JSON:**
```json
{
    "status": "processing",
    "session_id": "uuid-string"
}
```

---

#### `GET /api/stream/<session_id>`

Stream SSE events.

**Response**: Server-Sent Events (text/event-stream)

**Example:**
```javascript
const eventSource = new EventSource(`/api/stream/${sessionId}`);

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'content_block_delta') {
        // Append text to UI
        appendText(data.delta.text);
    } else if (data.type === 'done') {
        // Close stream
        eventSource.close();
    }
};
```

---

### Legacy Endpoints (Compatibility)

These redirect to new API for backward compatibility:

- `POST /stock/chat` → `/api/chat/send` (auto-creates session)
- `POST /data-agent/chat` → `/api/chat/send`
- `POST /agent/<agent_id>/start` → `/api/chat/send`

---

## SSE Event Format

All SSE events follow this structure (compatible with existing frontend):

### content_block_start

```json
{
    "type": "content_block_start",
    "index": 0,
    "content_type": "text"
}
```

### content_block_delta

```json
{
    "type": "content_block_delta",
    "index": 0,
    "delta": {
        "type": "text_delta",
        "text": "Hello "
    }
}
```

### content_block_stop

```json
{
    "type": "content_block_stop",
    "index": 0
}
```

### tool_result

```json
{
    "type": "tool_result",
    "tool_name": "execute_sql_query",
    "result": "Query executed successfully",
    "status": "success"
}
```

### done

```json
{
    "type": "done"
}
```

### error

```json
{
    "type": "error",
    "message": "Error description"
}
```

### ping (keepalive)

```json
{
    "type": "ping"
}
```

---

## Error Handling

### Session Errors

```python
session = session_manager.get_session('invalid-id')
# Returns: None

if not session:
    return jsonify({'error': 'Invalid session'}), 404
```

### Lock Errors

```python
lock = session_manager.get_lock(session_id)

if lock.locked():
    return jsonify({'error': 'Already processing a request'}), 409
```

### API Errors

```python
try:
    conversation = await anthropic_client.process_streaming(...)
except Exception as e:
    queue.put({'type': 'error', 'message': str(e)})
```

---

## Best Practices

### 1. Always Check Session Exists

```python
session = session_manager.get_session(session_id)
if not session:
    return jsonify({'error': 'Invalid session'}), 404
```

### 2. Use Lock for Concurrent Requests

```python
lock = session_manager.get_lock(session_id)

if lock.locked():
    return jsonify({'error': 'Busy'}), 409

with lock:
    # Process request
    pass
```

### 3. Update Conversation After Processing

```python
updated_conversation = await anthropic_client.process_streaming(...)

session_manager.update_conversation(session_id, updated_conversation)
```

### 4. Cleanup Old Sessions Periodically

```python
# In background task or cron job
session_manager.cleanup_inactive_sessions(hours=24)
```

### 5. Reuse Anthropic Client

```python
#  GOOD - Reuse singleton
anthropic_client = init_anthropic_client(config_path)

#  BAD - Creating new client each time
client = Anthropic(api_key=...)  # Avoid!
```

---

## Performance Optimization

### Session Manager

- **Cache**: Active sessions cached in memory (instant lookup)
- **Database**: Inactive sessions persisted to SQLite
- **Cleanup**: Auto-cleanup prevents database bloat

### Anthropic Client

- **Singleton**: Single client instance reused (fast)
- **Async**: Async/await for non-blocking operations
- **Streaming**: SSE streaming for real-time responses

### Queues

- **Thread-safe**: Queue per session (no blocking)
- **Timeout**: 30-second timeout prevents hangs
- **Keepalive**: Ping events prevent connection timeout

---

## Troubleshooting

### Issue: ModuleNotFoundError

**Fix:** Add AI_infrastructure to path
```python
import sys
sys.path.insert(0, 'path/to/AI_infrastructure')
```

### Issue: Database Locked

**Fix:** Restart Flask server (closes all connections)

### Issue: Session Not Persisting

**Fix:** Verify `update_conversation()` called after processing
```python
session_manager.update_conversation(session_id, updated_conversation)
```

### Issue: SSE Not Streaming

**Fix:** Verify mimetype
```python
return Response(generate(), mimetype='text/event-stream')
```

---

## Testing

See `AI_infrastructure/tests/` for complete test suite:

```bash
# Run all tests
pytest AI_infrastructure/tests/ -v

# Test session manager
pytest AI_infrastructure/tests/test_session_manager.py -v

# Test Anthropic client
pytest AI_infrastructure/tests/test_anthropic_client.py -v

# Test integration
pytest AI_infrastructure/tests/test_integration.py -v
```

---

**API Reference Complete!**

For migration guide, see `MIGRATION_GUIDE.md`
