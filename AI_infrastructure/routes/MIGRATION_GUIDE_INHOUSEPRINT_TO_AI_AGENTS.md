# 🚀 Technical Migration Guide: In_House_SQL → AI_agents Platform
## Comprehensive Architecture Transfer for agent_routes_v4.py

**Created:** October 30, 2025  
**Purpose:** Transfer proven patterns from In_House_SQL G_Folder AI infrastructure to AI_agents  
**Target:** agent_routes_v4.py rebuild with enhanced architecture  
**Audience:** AI Agent Developers

---

## 📋 Executive Summary

This guide documents the migration of battle-tested patterns from the **In_House_SQL G_Folder AI Infrastructure** (production-ready ToolUseAgent system) to the **AI_agents platform** (281-tool registry system). The goal is to enhance `agent_routes_v4.py` with:

1. **Background worker architecture** for tool execution
2. **Queue-based SSE streaming** with proper buffering
3. **Session persistence** across server restarts
4. **Interleaved thinking** support (beta API)
5. **File upload handling** with proper content blocks
6. **Multi-turn conversation** management with 10-turn limits

---

## 🏗️ Architecture Comparison

### Current AI_agents Architecture (Pre-Migration)

```
┌─────────────────────────────────────────────────────────┐
│ USER REQUEST → /api/agent/chat (POST)                  │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ AGENT_ROUTES.PY (handle_main_chat)                      │
│ ├─ Load ToolRegistry (281 tools)                        │
│ ├─ Send to Anthropic API                                │
│ ├─ Parse response (text, thinking, tool_use blocks)     │
│ ├─ Execute tools: tool_registry.execute_tool()          │
│ ├─ Add tool_result to messages                          │
│ └─ Yield SSE events via generator                       │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ SSE STREAM (Generator) → Browser                         │
│ data: {"type":"thinking_block","content":"..."}         │
│ data: {"type":"tool_use","tool_name":"..."}             │
│ data: {"type":"text_block","content":"..."}             │
└─────────────────────────────────────────────────────────┘

CHARACTERISTICS:
Direct SSE streaming (no buffering)
Synchronous tool execution in route
281 tools with credential injection
 No session persistence
 No background worker
 No interleaved thinking support
 Generator blocks Flask thread
```

### Target In_House_SQL Architecture (Post-Migration)

```
┌─────────────────────────────────────────────────────────┐
│ USER REQUEST → /api/agent/<id>/start (POST)            │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ AGENT_ROUTES.PY (start_agent)                           │
│ ├─ Load/Create session (SQLite persistence)             │
│ ├─ Get execution lock + queue                           │
│ ├─ Spawn background thread: run_agent_worker()          │
│ └─ Return 200 immediately (non-blocking)                │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌──────────────────┐   ┌────────────────────────────────┐
│ BROWSER          │   │ BACKGROUND THREAD              │
│ /stream/<id>     │   │ (agent_worker.py)              │
│ (GET)            │   │                                │
│                  │   │ ├─ Initialize ToolUseAgent     │
│ ← SSE events ←───┼───┤ ├─ process_request() loop      │
│   from queue     │   │ │  ├─ Send to Anthropic API   │
│                  │   │ │  ├─ Parse thinking blocks   │
│                  │   │ │  ├─ Execute tools internally│
│                  │   │ │  ├─ Continue multi-turn     │
│                  │   │ │  └─ Max 10 turns            │
│                  │   │ ├─ Queue events via callback  │
│                  │   │ └─ Save conversation (SQLite) │
└──────────────────┘   └────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────────┐
                    │ QUEUE (in-memory cache)   │
                    │ [{type: 'thinking', ...}, │
                    │  {type: 'tool_use', ...}, │
                    │  {type: 'complete', ...}] │
                    └───────────────────────────┘

CHARACTERISTICS:
Background worker (non-blocking)
Queue-based SSE streaming
Session persistence (SQLite)
Interleaved thinking (beta API)
Multi-turn loop (10-turn max)
File upload support
Thread-safe execution locks
```

---

## 🔑 Key Components to Migrate

### 1. **UnifiedSessionManager** (Session Persistence)

**Location:** `G_Folder/AI_infrastructure/core/unified_session_manager.py`

**Purpose:** SQLite-backed session storage with in-memory cache

**Features:**
- **SQLite Persistence** - Survives Flask restarts
- **In-memory Cache** - Fast access for active sessions
- **Queue Management** - SSE event queues per session
- **Thread-Safe Locks** - Prevent concurrent AI requests
- **Automatic Cleanup** - Remove stale sessions

**Schema:**
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    ui_context TEXT NOT NULL,          -- 'triple_agent', 'single_viewer', etc.
    agent_id TEXT,                     -- '1', '2', '3', 'stock_ai', etc.
    created_at TIMESTAMP,
    last_active TIMESTAMP,
    conversation TEXT,                 -- JSON array
    metadata TEXT                      -- JSON object
)
```

**Key Methods:**
```python
class UnifiedSessionManager:
    def create_session(self, ui_context: str, agent_id: Optional[str]) -> str:
        """Create new session with UUID, return session_id"""
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data (cache → DB fallback)"""
    
    def update_conversation(self, session_id: str, conversation: List[Dict]):
        """Save conversation to SQLite"""
    
    def get_queue(self, session_id: str) -> Queue:
        """Get or create SSE queue for session"""
    
    def get_lock(self, session_id: str) -> threading.Lock:
        """Get or create execution lock for session"""
    
    def cleanup_inactive_sessions(self, max_age_hours: int = 24):
        """Remove old sessions from cache and DB"""
```

**Integration Points:**
- Used by `agent_routes.py` to load/create sessions
- Used by `agent_worker.py` to save conversation history
- Used by SSE stream endpoint to get queues

**Migration to AI_agents:**
```python
# NEW FILE: AI_agents/AI_infrastructure/core/unified_session_manager.py
# Copy entire file, modify imports:
# - Change: from config import Config
# - To: from AI_infrastructure.config import Config
# 
# Update db_path default:
# - From: 'data/sessions.db'
# - To: 'AI_infrastructure/data/sessions.db'
```

---

### 2. **AgentWorker** (Background Tool Execution)

**Location:** `G_Folder/AI_infrastructure/core/agent_worker.py`

**Purpose:** Background thread that executes ToolUseAgent without blocking Flask

**Architecture:**
```python
def run_agent_worker(
    agent_id: str,
    prompt: str,
    file_data: List[Dict[str, Any]],  # File uploads
    lock: threading.Lock,              # Execution lock
    session_id: str,
    queue: Queue,                      # SSE event queue
    conversation_history: Optional[List[Dict]] = None,
    context: str = 'triple_agent',
    ai_client = None                   # Anthropic client
):
    """
    Background worker flow:
    1. Build content blocks from files
    2. Initialize ToolUseAgent with log_callback
    3. Call agent.process_request() (multi-turn loop)
    4. Stream events to queue via callback
    5. Save conversation to SQLite
    6. Release lock when done
    """
```

**Key Features:**

1. **File Processing**
```python
# Convert file uploads to Claude content blocks
for file_info in file_data:
    filename = file_info.get('filename')
    content_type = file_info.get('content_type')
    file_bytes = file_info.get('data')
    
    # Base64 encode
    encoded_data = base64.b64encode(file_bytes).decode('utf-8')
    
    # Determine block type
    if content_type == 'application/pdf':
        block_type = 'document'
    elif content_type.startswith('image/'):
        block_type = 'image'
    
    content_blocks.append({
        'type': block_type,
        'source': {
            'type': 'base64',
            'media_type': content_type,
            'data': encoded_data
        }
    })
```

2. **ToolUseAgent Integration**
```python
# Initialize with log callback for SSE streaming
def log_callback(log_entry: dict):
    """Stream ToolUseAgent logs to SSE queue"""
    event_type = log_entry.get('type')
    
    if event_type == 'thinking':
        queue.put({'type': 'thinking', 'content': log_entry['content']})
    elif event_type == 'tool_use':
        queue.put({'type': 'tool_use', 'tool_name': log_entry['tool_name']})
    elif event_type == 'tool_result':
        queue.put({'type': 'tool_result', 'output': log_entry['output']})
    elif event_type == 'response':
        queue.put({'type': 'response', 'content': log_entry['content']})

agent = ToolUseAgent(config_path, log_callback=log_callback)

# Execute multi-turn loop
result = agent.process_request(
    customer_message=prompt,
    max_turns=10,
    conversation_history=conversation_history,
    content_blocks=content_blocks
)
```

3. **Conversation Persistence**
```python
# Save conversation after AI responds
from core.session_persistence import save_conversation

updated_conversation = conversation_history or []
updated_conversation.append({'role': 'user', 'content': prompt})
updated_conversation.append({'role': 'assistant', 'content': final_response})

save_conversation(agent_id, session_id, updated_conversation)
```

4. **Completion Signaling**
```python
# Signal completion via queue
queue.put({
    'type': 'complete',
    'result': final_response,
    'session_id': session_id,
    'tool_calls': result.get('tool_calls', 0),
    'thinking_tokens': result.get('thinking_tokens', 0)
})
```

**Migration to AI_agents:**
```python
# NEW FILE: AI_agents/AI_infrastructure/core/agent_worker.py
# MODIFICATIONS NEEDED:
# 
# 1. Replace ToolUseAgent with ToolRegistry execution:
#    - Remove: from tool_use_agent import ToolUseAgent
#    - Add: from tools.registry import ToolRegistry
# 
# 2. Implement tool execution loop:
#    messages = conversation_history + [{'role': 'user', 'content': content_blocks}]
#    
#    for turn in range(max_turns):
#        response = ai_client.messages.create(
#            model="claude-3-7-sonnet-20250219",
#            max_tokens=16000,
#            thinking={"type": "enabled", "budget_tokens": 10000},
#            extra_headers={"anthropic-beta": "interleaved-thinking-2025-05-14"},
#            tools=tool_registry.get_tool_schemas(),
#            messages=messages
#        )
#        
#        # Stream thinking blocks
#        for block in response.content:
#            if block.type == "thinking":
#                queue.put({'type': 'thinking', 'content': block.thinking})
#            elif block.type == "tool_use":
#                queue.put({'type': 'tool_use', 'tool_name': block.name})
#                
#                # Execute tool with credential injection
#                tool_result = tool_registry.execute_tool(
#                    tool_name=block.name,
#                    user_id=user_id,  # ← Credential injection
#                    **block.input
#                )
#                
#                queue.put({'type': 'tool_result', 'output': tool_result})
#                
#                # Add to messages for next turn
#                messages.append({'role': 'assistant', 'content': response.content})
#                messages.append({
#                    'role': 'user',
#                    'content': [{
#                        'type': 'tool_result',
#                        'tool_use_id': block.id,
#                        'content': json.dumps(tool_result)
#                    }]
#                })
#        
#        # Check if done (no tool_use blocks)
#        if not any(b.type == 'tool_use' for b in response.content):
#            break
```

---

### 3. **Agent Routes** (REST API Endpoints)

**Location:** `G_Folder/AI_infrastructure/routes/agent_routes.py`

**Purpose:** Flask Blueprint with 2 core endpoints

**Endpoint 1: Start Agent (POST)**
```python
@agent_bp.route('/agent/<agent_id>/start', methods=['POST'])
def start_agent(agent_id):
    """
    Start agent in background thread
    
    Request:
        - JSON: {"session_id": "uuid", "message": "text"}
        - OR FormData: session_id, message, files[]
    
    Returns:
        {
            "success": true,
            "session_id": "uuid",
            "agent_id": "1",
            "status": "processing"
        }
    
    Flow:
        1. Parse request (JSON or FormData)
        2. Load/create session (SQLite)
        3. Get lock + queue
        4. Spawn background thread
        5. Return 200 immediately
    """
    
    # Determine request type
    is_form_data = 'multipart/form-data' in request.content_type
    
    if is_form_data:
        # File upload workflow
        session_id = request.form.get('session_id')
        prompt = request.form.get('message')
        files = request.files.getlist('files')
        
        # Process files
        from utils.file_encoding import process_file_uploads
        content_blocks = process_file_uploads(files)
    else:
        # Text-only workflow
        data = request.json or {}
        session_id = data.get('session_id')
        prompt = data.get('message')
        content_blocks = None
    
    # Load or create session (with conversation history)
    from core.session_persistence import load_or_create_session
    state = load_or_create_session(
        agent_id=agent_id,
        session_id=session_id,
        ui_context='triple_agent'  # or 'single_viewer', etc.
    )
    session_id = state['session_id']
    
    # Get execution primitives
    lock = agent_state_manager.get_lock(agent_id, session_id)
    queue = agent_state_manager.get_queue(agent_id, session_id)
    
    # Get AI client
    ai_client = current_app.config.get('AI_CLIENT')
    
    # Spawn background worker
    threading.Thread(
        target=run_agent_worker,
        args=(
            agent_id, 
            prompt, 
            content_blocks,  # file_data or None
            lock, 
            session_id, 
            queue,
            state['conversation'],  # conversation history
            state.get('context', 'triple_agent'),
            ai_client
        ),
        daemon=True
    ).start()
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'agent_id': agent_id,
        'status': 'processing',
        'files_uploaded': len(content_blocks) if content_blocks else 0
    })
```

**Endpoint 2: SSE Stream (GET)**
```python
@agent_bp.route('/stream/<agent_id>', methods=['GET'])
def stream_agent(agent_id):
    """
    Server-Sent Events stream
    
    Query params:
        ?session_id=uuid (required)
    
    Returns:
        text/event-stream with format:
        data: {"type":"thinking","content":"..."}
        data: {"type":"tool_use","tool_name":"..."}
        data: {"type":"complete","result":"..."}
    
    Flow:
        1. Get session_id from query params
        2. Get queue from session manager
        3. Read queue with timeout
        4. Yield SSE events
        5. Exit on 'complete' or timeout
    """
    
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'error': 'Missing session_id'}), 400
    
    # Get queue from session manager
    queue = agent_state_manager.get_queue(agent_id, session_id)
    
    def generate():
        """SSE generator function"""
        timeout_count = 0
        max_timeout = 3  # 3 x 30s = 90s total timeout
        
        while True:
            try:
                # Blocking read with 30s timeout
                log_entry = queue.get(timeout=30)
                timeout_count = 0  # Reset on success
                
                # Send as SSE format
                yield f"data: {json.dumps(log_entry)}\n\n"
                
                # Check for completion
                if log_entry['type'] == 'complete':
                    break
                
            except Empty:
                # Timeout - check if too many
                timeout_count += 1
                if timeout_count >= max_timeout:
                    yield f"data: {json.dumps({'type': 'timeout'})}\n\n"
                    break
    
    # Return SSE stream
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'  # Disable nginx buffering
        }
    )
```

**Migration to AI_agents:**
```python
# MODIFY: AI_agents/AI_infrastructure/routes/agent_routes_v4.py
# 
# CHANGES NEEDED:
# 1. Add session persistence imports
# 2. Replace direct tool execution with background worker
# 3. Split into 2 endpoints (start + stream)
# 4. Add queue-based SSE streaming
# 
# See detailed code in Section 5: Implementation Template
```

---

### 4. **File Upload Handling** (Content Block Encoding)

**Location:** `G_Folder/AI_infrastructure/utils/file_encoding.py`

**Purpose:** Base64 encoding, file validation, media type detection

**Key Functions:**

1. **File Validation**
```python
MAX_FILE_SIZE = 32 * 1024 * 1024  # 32MB

def validate_file_size(filename: str, size: int):
    """Validate file size"""
    if size > MAX_FILE_SIZE:
        raise FileValidationError(
            f"File '{filename}' too large ({size} bytes). "
            f"Max: {MAX_FILE_SIZE / (1024 * 1024):.1f} MB"
        )
```

2. **Media Type Detection**
```python
def guess_media_type(filename: str) -> str:
    """Guess MIME type from extension"""
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.pdf'):
        return 'application/pdf'
    elif filename_lower.endswith(('.jpg', '.jpeg')):
        return 'image/jpeg'
    elif filename_lower.endswith('.png'):
        return 'image/png'
    elif filename_lower.endswith('.gif'):
        return 'image/gif'
    elif filename_lower.endswith('.webp'):
        return 'image/webp'
    else:
        return 'application/octet-stream'
```

3. **Content Block Builder**
```python
def build_content_block(filename: str, data: bytes, 
                       media_type: Optional[str] = None) -> dict:
    """
    Build Claude API content block
    
    Returns:
        {
            "type": "document" | "image",
            "source": {
                "type": "base64",
                "media_type": "application/pdf" | "image/jpeg",
                "data": "base64_encoded_string"
            }
        }
    """
    # Guess media type if not provided
    if not media_type:
        media_type = guess_media_type(filename)
    
    # Validate size
    validate_file_size(filename, len(data))
    
    # Encode to base64
    encoded_data = base64.b64encode(data).decode('utf-8')
    
    # Determine block type
    if media_type == 'application/pdf':
        block_type = 'document'
    elif media_type.startswith('image/'):
        block_type = 'image'
    else:
        block_type = 'document'
    
    return {
        'type': block_type,
        'source': {
            'type': 'base64',
            'media_type': media_type,
            'data': encoded_data
        }
    }
```

4. **Flask Integration**
```python
def process_file_uploads(files) -> list:
    """
    Process Flask file uploads
    
    Args:
        files: request.files.getlist('files')
    
    Returns:
        List of content blocks
    """
    content_blocks = []
    
    for file in files:
        filename = file.filename
        media_type = file.content_type
        file_bytes = file.read()
        
        content_block = build_content_block(filename, file_bytes, media_type)
        content_blocks.append(content_block)
    
    return content_blocks
```

**Migration to AI_agents:**
```python
# NEW FILE: AI_agents/AI_infrastructure/utils/file_encoding.py
# Copy entire file - no modifications needed
```

---

### 5. **Interleaved Thinking** (Extended Thinking Beta)

**Location:** `G_Folder/Quote_Calculator/AI_Quote_Agent/core/tool_use_agent.py` (lines 1735-1750)

**Purpose:** Enable thinking blocks throughout multi-turn tool use

**Implementation:**
```python
response = self.client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=16000,
    temperature=1.0,
    
    # EXTENDED THINKING with INTERLEAVED THINKING
    thinking={
        "type": "enabled",
        "budget_tokens": 10000  # Up to 10k tokens for thinking
    },
    
    # CRITICAL: Interleaved thinking beta header
    # This allows thinking blocks to appear between tool uses
    extra_headers={
        "anthropic-beta": "interleaved-thinking-2025-05-14"
    },
    
    # Tool definitions
    tools=self._get_tool_definitions(),
    
    # Tool choice (must be 'auto' or 'none' with thinking)
    tool_choice={"type": "auto"},
    
    system=system_prompt,
    messages=self.messages
)
```

**Response Parsing:**
```python
# Parse response content blocks
for block in response.content:
    if block.type == "thinking":
        # Thinking block (interleaved with other blocks)
        self._log_callback({
            'type': 'thinking',
            'content': block.thinking
        })
    
    elif block.type == "tool_use":
        # Tool use block
        self._log_callback({
            'type': 'tool_use',
            'tool_name': block.name,
            'input': block.input
        })
        
        # Execute tool
        tool_result = self._execute_tool(block.name, block.input)
        
        self._log_callback({
            'type': 'tool_result',
            'tool_name': block.name,
            'output': tool_result
        })
    
    elif block.type == "text":
        # Text block (final response)
        self._log_callback({
            'type': 'response',
            'content': block.text
        })
```

**Benefits:**
- Thinking visible throughout tool execution
- Better debugging of AI reasoning
- Improved user experience (shows AI is "thinking")
- Works with tools (not blocked by tool_choice)

**Cost:**
- ~10,000 thinking tokens per request (~$0.03 per request)
- Formula: thinking_cost = 10000 * ($3.00 / 1M tokens)

**Migration to AI_agents:**
```python
# MODIFY: AI_agents/AI_infrastructure/core/agent_worker.py
# 
# In tool execution loop, add thinking parameters:
response = ai_client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=16000,
    temperature=1.0,
    
    # ADD THINKING
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    
    # ADD BETA HEADER
    extra_headers={
        "anthropic-beta": "interleaved-thinking-2025-05-14"
    },
    
    tools=tool_registry.get_tool_schemas(),
    tool_choice={"type": "auto"},
    messages=messages
)

# PARSE THINKING BLOCKS
for block in response.content:
    if block.type == "thinking":
        queue.put({
            'type': 'thinking_block',
            'content': block.thinking
        })
```

---

## 📝 Implementation Template for agent_routes_v4.py

### File Structure

```
AI_agents/
├── AI_infrastructure/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── unified_session_manager.py  # ← NEW (copy from In_House_SQL)
│   │   ├── agent_state_manager.py      # ← NEW (copy from In_House_SQL)
│   │   ├── agent_worker.py             # ← NEW (adapt from In_House_SQL)
│   │   └── session_persistence.py      # ← NEW (copy from In_House_SQL)
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_encoding.py            # ← NEW (copy from In_House_SQL)
│   │   └── response_helpers.py         # ← NEW (copy from In_House_SQL)
│   ├── routes/
│   │   ├── agent_routes_v4.py          # ← MODIFY (use new architecture)
│   │   └── ...
│   └── data/
│       └── sessions.db                  # ← AUTO-CREATED by UnifiedSessionManager
```

### Step-by-Step Migration

#### Step 1: Copy Core Files

```powershell
# Copy session manager
Copy-Item `
    "C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure\core\unified_session_manager.py" `
    "C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\core\unified_session_manager.py"

# Copy agent state manager
Copy-Item `
    "C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure\core\agent_state_manager.py" `
    "C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\core\agent_state_manager.py"

# Copy session persistence
Copy-Item `
    "C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure\core\session_persistence.py" `
    "C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\core\session_persistence.py"

# Copy file encoding utils
Copy-Item `
    "C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure\utils\file_encoding.py" `
    "C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\utils\file_encoding.py"

# Copy response helpers
Copy-Item `
    "C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure\utils\response_helpers.py" `
    "C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\utils\response_helpers.py"
```

#### Step 2: Create agent_worker.py (Adapted Version)

```python
# FILE: AI_agents/AI_infrastructure/core/agent_worker.py
"""
Agent Worker - Background thread for tool execution
Adapted from In_House_SQL with ToolRegistry integration
"""

import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from queue import Queue
import threading
import base64

# Import AI_agents tools
from tools.registry import ToolRegistry

# Get registry instance
tool_registry = ToolRegistry()


def run_agent_worker(
    agent_id: str,
    prompt: str,
    file_data: Optional[List[Dict[str, Any]]],
    lock: threading.Lock,
    session_id: str,
    queue: Queue,
    conversation_history: Optional[List[Dict]] = None,
    context: str = 'agent',
    ai_client = None,
    user_id: Optional[int] = None  # ← For credential injection
):
    """
    Background worker that executes tools via ToolRegistry
    
    Args:
        agent_id: Agent identifier
        prompt: User prompt text
        file_data: List of file dicts with {filename, content_type, data}
        lock: Threading lock
        session_id: Session ID
        queue: Queue for SSE events
        conversation_history: Previous conversation
        context: UI context
        ai_client: Anthropic client
        user_id: User ID for credential injection
    """
    
    log_prefix = f"[Agent Worker {agent_id}]"
    
    try:
        print(f"{log_prefix} Starting for session {session_id[:8]}...")
        
        # Build content blocks from files
        content_blocks = []
        
        if file_data:
            for file_info in file_data:
                filename = file_info.get('filename', 'unknown')
                content_type = file_info.get('content_type', 'application/octet-stream')
                file_bytes = file_info.get('data', b'')
                
                # Encode to base64
                encoded_data = base64.b64encode(file_bytes).decode('utf-8')
                
                # Determine content block type
                if content_type == 'application/pdf':
                    block_type = 'document'
                elif content_type.startswith('image/'):
                    block_type = 'image'
                else:
                    block_type = 'document'
                
                content_blocks.append({
                    'type': block_type,
                    'source': {
                        'type': 'base64',
                        'media_type': content_type,
                        'data': encoded_data
                    }
                })
                
                print(f"{log_prefix} Added {block_type}: {filename}")
        
        # Add text prompt
        if prompt:
            content_blocks.append({
                'type': 'text',
                'text': prompt
            })
        
        # Build messages array
        messages = conversation_history or []
        messages.append({
            'role': 'user',
            'content': content_blocks if content_blocks else prompt
        })
        
        # Multi-turn tool execution loop
        max_turns = 10
        tool_calls = 0
        thinking_tokens = 0
        
        for turn in range(max_turns):
            print(f"{log_prefix} Turn {turn + 1}/{max_turns}")
            
            # Send thinking event
            queue.put({
                'type': 'thinking',
                'content': f'Processing turn {turn + 1}...'
            })
            
            # Call Anthropic API
            response = ai_client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=16000,
                temperature=1.0,
                
                # INTERLEAVED THINKING
                thinking={
                    "type": "enabled",
                    "budget_tokens": 10000
                },
                extra_headers={
                    "anthropic-beta": "interleaved-thinking-2025-05-14"
                },
                
                # TOOLS
                tools=tool_registry.get_tool_schemas(),
                tool_choice={"type": "auto"},
                
                messages=messages
            )
            
            # Track thinking tokens
            usage = response.usage
            thinking_tokens += usage.input_tokens + usage.output_tokens
            
            # Parse content blocks
            has_tool_use = False
            assistant_message = []
            
            for block in response.content:
                if block.type == "thinking":
                    # Thinking block
                    queue.put({
                        'type': 'thinking_block',
                        'content': block.thinking
                    })
                    assistant_message.append({
                        'type': 'thinking',
                        'thinking': block.thinking
                    })
                
                elif block.type == "tool_use":
                    # Tool use block
                    has_tool_use = True
                    tool_calls += 1
                    
                    tool_name = block.name
                    tool_input = block.input
                    
                    queue.put({
                        'type': 'tool_use',
                        'tool_name': tool_name,
                        'input': tool_input
                    })
                    
                    # Execute tool with credential injection
                    try:
                        tool_result = tool_registry.execute_tool(
                            tool_name=tool_name,
                            user_id=user_id,  # ← Credential injection
                            **tool_input
                        )
                        
                        queue.put({
                            'type': 'tool_result',
                            'tool_name': tool_name,
                            'success': True,
                            'output': tool_result
                        })
                        
                        # Add to messages
                        assistant_message.append({
                            'type': 'tool_use',
                            'id': block.id,
                            'name': tool_name,
                            'input': tool_input
                        })
                        
                        # Tool result message
                        messages.append({
                            'role': 'assistant',
                            'content': assistant_message
                        })
                        messages.append({
                            'role': 'user',
                            'content': [{
                                'type': 'tool_result',
                                'tool_use_id': block.id,
                                'content': json.dumps(tool_result)
                            }]
                        })
                        
                    except Exception as e:
                        queue.put({
                            'type': 'tool_result',
                            'tool_name': tool_name,
                            'success': False,
                            'error': str(e)
                        })
                        print(f"{log_prefix} Tool error: {e}")
                
                elif block.type == "text":
                    # Text response
                    queue.put({
                        'type': 'text_block',
                        'content': block.text
                    })
                    assistant_message.append({
                        'type': 'text',
                        'text': block.text
                    })
            
            # Check if done (no tool use)
            if not has_tool_use:
                # Final response
                final_text = ''.join(
                    b['text'] for b in assistant_message if b.get('type') == 'text'
                )
                
                # Save conversation
                messages.append({
                    'role': 'assistant',
                    'content': final_text
                })
                
                from core.session_persistence import save_conversation
                save_conversation(agent_id, session_id, messages)
                
                # Signal completion
                queue.put({
                    'type': 'complete',
                    'result': final_text,
                    'session_id': session_id,
                    'tool_calls': tool_calls,
                    'thinking_tokens': thinking_tokens
                })
                
                print(f"{log_prefix} Complete ({tool_calls} tools, {thinking_tokens} tokens)")
                break
        
    except Exception as e:
        print(f"{log_prefix} Error: {e}")
        import traceback
        traceback.print_exc()
        queue.put({
            'type': 'error',
            'error': str(e)
        })
    
    finally:
        # Release lock
        try:
            lock.release()
            print(f"{log_prefix} Lock released")
        except Exception as e:
            print(f"{log_prefix} Lock release error: {e}")
```

#### Step 3: Update agent_routes_v4.py

```python
# FILE: AI_agents/AI_infrastructure/routes/agent_routes_v4.py
"""
Agent Routes V4 - Enhanced with In_House_SQL patterns
- Background worker architecture
- Queue-based SSE streaming
- Session persistence
- Interleaved thinking support
- File upload handling
"""

import json
import logging
import threading
from typing import Dict, Any, Optional
from pathlib import Path
from flask import Blueprint, request, Response, jsonify, current_app
from queue import Empty

# Core infrastructure
from AI_infrastructure.core.unified_session_manager import session_manager
from AI_infrastructure.core.agent_state_manager import agent_state_manager
from AI_infrastructure.core.agent_worker import run_agent_worker
from AI_infrastructure.core.session_persistence import load_or_create_session

# Utilities
from AI_infrastructure.utils.file_encoding import process_file_uploads, FileValidationError
from AI_infrastructure.utils.response_helpers import success_response, error_response

# Tools
from tools.registry import ToolRegistry

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
agent_bp = Blueprint('agent_v4', __name__, url_prefix='/api/agent')

# Initialize tool registry
tool_registry = ToolRegistry()
logger.info(f"Agent Routes V4 initialized ({len(tool_registry.tools)} tools)")


# ============================================================
# ENDPOINT 1: START AGENT (Background Worker)
# ============================================================

@agent_bp.route('/<agent_id>/start', methods=['POST'])
def start_agent(agent_id):
    """
    Start agent in background thread
    
    agent_id: '1' | '2' | '3' | 'data' | 'single'
    
    Request (JSON):
    {
        "session_id": "uuid" (optional),
        "message": "User prompt",
        "user_id": 1 (optional, for credential injection)
    }
    
    Request (FormData with files):
    - session_id (optional)
    - message
    - files[] (multiple uploads)
    - user_id (optional)
    
    Returns:
    {
        "success": true,
        "session_id": "uuid",
        "agent_id": "1",
        "status": "processing",
        "files_uploaded": 2
    }
    """
    try:
        # Determine request type
        is_form_data = request.content_type and 'multipart/form-data' in request.content_type
        
        if is_form_data:
            # File upload workflow
            session_id = request.form.get('session_id')
            prompt = request.form.get('message', '')
            user_id = request.form.get('user_id')
            
            # Process file uploads
            files = request.files.getlist('files')
            if not files:
                return error_response("No files uploaded", 400)
            
            try:
                content_blocks = process_file_uploads(files)
                file_data = content_blocks
            except FileValidationError as e:
                return error_response(str(e), 400)
        else:
            # Text-only workflow
            data = request.json or {}
            session_id = data.get('session_id')
            prompt = data.get('message', '')
            user_id = data.get('user_id')
            file_data = None
        
        # Validate prompt
        if not prompt:
            return error_response("Missing 'message' in request", 400)
        
        # Convert user_id to int if present
        if user_id:
            try:
                user_id = int(user_id)
            except (ValueError, TypeError):
                return error_response("Invalid user_id", 400)
        
        # Load or create session (with conversation history)
        state = load_or_create_session(
            agent_id=agent_id,
            session_id=session_id,
            ui_context='agent_v4'
        )
        session_id = state['session_id']
        
        # Get execution lock and queue
        lock = agent_state_manager.get_lock(agent_id, session_id)
        queue = agent_state_manager.get_queue(agent_id, session_id)
        
        # Update status
        agent_state_manager.update_status(agent_id, session_id, 'processing')
        
        # Get AI client
        ai_client = current_app.config.get('AI_CLIENT')
        if ai_client is None:
            from AI_infrastructure.core.unified_ai_client import initialize_ai_client
            from AI_infrastructure.config import Config
            ai_client = initialize_ai_client(str(Config.DB_CONFIG_PATH))
            current_app.config['AI_CLIENT'] = ai_client
        
        # Start background worker
        threading.Thread(
            target=run_agent_worker,
            args=(
                agent_id,
                prompt,
                file_data,
                lock,
                session_id,
                queue,
                state['conversation'],
                state.get('context', 'agent_v4'),
                ai_client,
                user_id  # ← Credential injection
            ),
            daemon=True
        ).start()
        
        return success_response({
            'session_id': session_id,
            'agent_id': agent_id,
            'status': 'processing',
            'files_uploaded': len(file_data) if file_data else 0
        })
    
    except Exception as e:
        logger.error(f"Agent start failed: {e}", exc_info=True)
        return error_response(f"Agent start failed: {str(e)}", 500)


# ============================================================
# ENDPOINT 2: SSE STREAM (Queue-based)
# ============================================================

@agent_bp.route('/stream/<agent_id>', methods=['GET'])
def stream_agent(agent_id):
    """
    Server-Sent Events stream
    
    Query params:
        ?session_id=uuid (required)
    
    agent_id: '1' | '2' | '3' | 'data' | 'single'
    
    Returns:
        text/event-stream with events:
        - thinking_block
        - tool_use
        - tool_result
        - text_block
        - complete
        - error
    """
    session_id = request.args.get('session_id')
    
    if not session_id:
        return error_response("Missing session_id", 400)
    
    # Get queue
    queue = agent_state_manager.get_queue(agent_id, session_id)
    
    def generate():
        """SSE generator function"""
        timeout_count = 0
        max_timeout = 3  # 3 x 30s = 90s total
        
        while True:
            try:
                # Blocking read with timeout
                log_entry = queue.get(timeout=30)
                timeout_count = 0
                
                # Send as SSE format
                yield f"data: {json.dumps(log_entry)}\n\n"
                
                # Check for completion
                if log_entry.get('type') in ['complete', 'error']:
                    break
                
            except Empty:
                # Timeout
                timeout_count += 1
                if timeout_count >= max_timeout:
                    yield f"data: {json.dumps({'type': 'timeout'})}\n\n"
                    break
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


# ============================================================
# ENDPOINT 3: GET SESSION (Conversation History)
# ============================================================

@agent_bp.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """
    Get session data including conversation history
    
    Returns:
    {
        "success": true,
        "session": {
            "session_id": "uuid",
            "agent_id": "1",
            "conversation": [...],
            "created_at": "2025-10-30T12:00:00",
            "last_active": "2025-10-30T12:05:00"
        }
    }
    """
    try:
        session_data = session_manager.get_session(session_id)
        
        if not session_data:
            return error_response("Session not found", 404)
        
        return success_response({'session': session_data})
    
    except Exception as e:
        logger.error(f"Get session failed: {e}", exc_info=True)
        return error_response(f"Get session failed: {str(e)}", 500)


# ============================================================
# ENDPOINT 4: DELETE SESSION
# ============================================================

@agent_bp.route('/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    Delete session (clear conversation history)
    
    Returns:
    {
        "success": true,
        "message": "Session deleted"
    }
    """
    try:
        session_manager.delete_session(session_id)
        return success_response({'message': 'Session deleted'})
    
    except Exception as e:
        logger.error(f"Delete session failed: {e}", exc_info=True)
        return error_response(f"Delete session failed: {str(e)}", 500)
```

#### Step 4: Register Blueprint in Flask App

```python
# FILE: AI_agents/AI_infrastructure/flask_app.py

# Import new blueprint
from routes.agent_routes_v4 import agent_bp as agent_v4_bp

# Register blueprint
app.register_blueprint(agent_v4_bp, url_prefix='/api/agent/v4')

# Or replace old agent routes:
# app.register_blueprint(agent_v4_bp, url_prefix='/api/agent')
```

---

## 🧪 Testing the Migration

### Test 1: Session Persistence

```powershell
# Start Flask server
cd C:\Users\gpoli\GIT\AI_agents
BISTART

# Test session creation
$response = Invoke-RestMethod -Method POST -Uri "http://localhost:5001/api/agent/v4/1/start" `
    -ContentType "application/json" `
    -Body '{"message": "Hello, test session persistence"}'

$sessionId = $response.session_id
Write-Host "Session ID: $sessionId"

# Test SSE stream
$events = @()
$streamUrl = "http://localhost:5001/api/agent/v4/stream/1?session_id=$sessionId"
# (Open in browser or use curl to see events)

# Test session retrieval
$session = Invoke-RestMethod -Method GET -Uri "http://localhost:5001/api/agent/v4/session/$sessionId"
Write-Host "Conversation history: $($session.session.conversation.Count) messages"
```

### Test 2: File Upload

```powershell
# Create test file
"Test content" | Out-File -FilePath "test.txt"

# Upload file
$form = @{
    message = "Analyze this file"
    files = Get-Item "test.txt"
    user_id = "1"
}

$response = Invoke-WebRequest -Method POST -Uri "http://localhost:5001/api/agent/v4/1/start" `
    -Form $form

$result = $response.Content | ConvertFrom-Json
Write-Host "Files uploaded: $($result.files_uploaded)"
```

### Test 3: Interleaved Thinking

```powershell
# Start agent with complex task requiring thinking
$response = Invoke-RestMethod -Method POST -Uri "http://localhost:5001/api/agent/v4/1/start" `
    -ContentType "application/json" `
    -Body '{"message": "Use multiple tools to analyze this complex problem..."}'

# Check SSE stream for thinking_block events
# Should see:
# data: {"type":"thinking_block","content":"Let me think about this..."}
# data: {"type":"tool_use","tool_name":"search_google"}
# data: {"type":"thinking_block","content":"Based on search results..."}
# data: {"type":"tool_use","tool_name":"calculate"}
# data: {"type":"complete","result":"..."}
```

---

## 📊 Performance Comparison

| Metric | Old (agent_routes.py) | New (agent_routes_v4.py) |
|--------|----------------------|--------------------------|
| **Request latency** | 10-120s (blocking) | <100ms (non-blocking) |
| **Server threads** | 1 per request | 1 main + N background |
| **Session persistence** |  None | SQLite |
| **Multi-turn support** | ⚠️ Manual | 10-turn loop |
| **Thinking visibility** | ⚠️ Limited | Interleaved |
| **File uploads** | ⚠️ Basic | Full support |
| **Error recovery** | ⚠️ Request fails | Session survives |
| **Concurrent requests** | ⚠️ Blocked | Queued per session |

---

## 🔒 Security Considerations

### Credential Injection

**Old Pattern (AI_agents):**
```python
# User credentials injected in route
tool_result = tool_registry.execute_tool(
    tool_name=tool_name,
    user_id=user_id,  # ← Route has access to user_id
    **tool_input
)
```

**New Pattern (Background Worker):**
```python
# User credentials passed to background worker
threading.Thread(
    target=run_agent_worker,
    args=(
        agent_id,
        prompt,
        file_data,
        lock,
        session_id,
        queue,
        conversation_history,
        context,
        ai_client,
        user_id  # ← Passed to worker
    ),
    daemon=True
).start()

# Worker has access to user_id for credential injection
tool_result = tool_registry.execute_tool(
    tool_name=tool_name,
    user_id=user_id,  # ← Available in worker
    **tool_input
)
```

**Security Notes:**
- user_id validated in route (before background thread)
- Session ID prevents cross-user access
- Execution locks prevent concurrent requests
- SQLite database has file permissions
- ⚠️ Background threads run with Flask process privileges
- ⚠️ File uploads stored in memory (32MB limit)

---

## 🚀 Deployment Checklist

### Pre-Deployment

- [ ] Copy 5 core files from In_House_SQL:
  - [ ] `unified_session_manager.py`
  - [ ] `agent_state_manager.py`
  - [ ] `session_persistence.py`
  - [ ] `file_encoding.py`
  - [ ] `response_helpers.py`

- [ ] Create `agent_worker.py` with ToolRegistry integration

- [ ] Update `agent_routes_v4.py` with new endpoints

- [ ] Register blueprint in `flask_app.py`

- [ ] Create `data/sessions.db` directory

### Testing

- [ ] Test session creation
- [ ] Test SSE streaming
- [ ] Test file uploads
- [ ] Test thinking blocks
- [ ] Test multi-turn conversations
- [ ] Test session persistence (restart server)
- [ ] Test error handling
- [ ] Test concurrent requests

### Post-Deployment

- [ ] Monitor `sessions.db` size
- [ ] Set up session cleanup cron job
- [ ] Monitor background thread count
- [ ] Check memory usage (file uploads)
- [ ] Review thinking token costs
- [ ] Update frontend to use new endpoints

---

## 📚 Additional Resources

### Documentation Files (In_House_SQL)

1. **`TOOLUSEAGENT_INTEGRATION_COMPLETE.md`** - ToolUseAgent integration guide
2. **`AGENT_ENDPOINTS_COMPLETE_REFERENCE.md`** - Complete endpoint documentation
3. **`SESSION_THREAD_ARCHITECTURE.md`** - Session management architecture
4. **`UI_CONNECTION_COMPLETE_SUMMARY.md`** - Frontend integration guide
5. **`ANTHROPIC_API_EXPLAINED.md`** - Anthropic API usage patterns

### Key Differences Summary

| Feature | In_House_SQL | AI_agents (Target) |
|---------|--------------|-------------------|
| **Tool System** | ToolUseAgent (embedded) | ToolRegistry (281 tools) |
| **Architecture** | Background worker | Background worker |
| **Session Persistence** | SQLite | SQLite |
| **Thinking** | Interleaved | Interleaved |
| **File Uploads** | Full support | Full support |
| **Credential Injection** | N/A | user_id parameter |

---

## 🎯 Next Steps

1. **Phase 1:** Copy core files and test session manager
2. **Phase 2:** Implement agent_worker.py with ToolRegistry
3. **Phase 3:** Update agent_routes_v4.py with new endpoints
4. **Phase 4:** Test file uploads and SSE streaming
5. **Phase 5:** Enable interleaved thinking
6. **Phase 6:** Update frontend to use new endpoints
7. **Phase 7:** Deploy to production

---

## 📝 Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-30 | Initial migration guide created | AI Agent |

---

**END OF MIGRATION GUIDE**

For questions or issues, refer to:
- In_House_SQL: `C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure\`
- AI_agents: `C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\`
