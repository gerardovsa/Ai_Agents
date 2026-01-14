# 🔄 V4 Integration Complete Guide
## Combining V4 Modular Architecture + In_House_SQL Patterns

**Created:** October 30, 2025  
**Integrates:** V4_MODULAR_ARCHITECTURE.md + MIGRATION_GUIDE_INHOUSEPRINT_TO_AI_AGENTS.md

---

## 📋 Executive Summary

**Problem:** Two excellent architectural plans exist:
1. **V4 Modular Architecture** - Synchronous, modular, comprehensive logging
2. **In_House_SQL Migration Guide** - Asynchronous, session persistence, background workers

**Solution:** **Integrate both** into a hybrid system that supports:
- ✅ **Synchronous mode** (fast, direct response) for simple queries
- ✅ **Asynchronous mode** (background worker) for complex workflows
- ✅ **V4 modular components** (13 small modules with logging)
- ✅ **In_House_SQL patterns** (session persistence, SSE streaming, file uploads)

---

## 🏗️ Integrated Architecture

### Folder Structure (21 Modules)

```
AI_infrastructure/
├── routes/
│   ├── agent_routes_v4.py          # 4 endpoints (sync + async)
│   └── __init__.py
│
├── core/  (10 modules)
│   ├── __init__.py
│   │
│   ├── # V4 MODULAR COMPONENTS (Original)
│   ├── tool_executor.py            # ToolExecutor class
│   ├── tool_processor.py           # Tool call processing
│   ├── conversation_manager.py     # Synchronous multi-turn loop
│   ├── session_handler.py          # Session CRUD (basic)
│   ├── response_serializer.py      # Response formatting
│   │
│   └── # IN_HOUSE_SQL PATTERNS (Added)
│       ├── unified_session_manager.py  # SQLite + cache
│       ├── agent_state_manager.py      # Queue + locks
│       ├── agent_worker.py             # Background thread (uses V4 modules)
│       ├── session_persistence.py      # Load/save conversations
│       └── unified_ai_client.py        # Anthropic client wrapper
│
├── builders/  (4 modules)
│   ├── __init__.py
│   ├── user_profile_builder.py     # Fetch user data
│   ├── system_prompt_builder.py    # Build comprehensive prompt
│   ├── tool_schema_converter.py    # Convert to Anthropic format
│   └── credential_fetcher.py       # OAuth credentials
│
├── meta_tools/  (4 modules)
│   ├── __init__.py
│   ├── platform_tools_lister.py    # list_platform_tools
│   ├── platform_guide_provider.py  # get_platform_guide
│   ├── workflow_instructor.py      # get_workflow_instructions
│   └── smart_tool_instructor.py    # get_smart_tool_instructions
│
├── utils/  (7 modules)
│   ├── __init__.py
│   │
│   ├── # V4 UTILITIES (Original)
│   ├── logger.py                   # Comprehensive logging ⭐
│   ├── error_handler.py            # Error recovery
│   ├── validators.py               # Input validation
│   ├── formatters.py               # Response formatting
│   │
│   └── # IN_HOUSE_SQL UTILITIES (Added)
│       ├── file_encoding.py        # Base64, file validation
│       └── response_helpers.py     # success_response(), error_response()
│
└── config/  (2 modules)
    ├── __init__.py
    ├── logging_config.py           # Logging settings
    └── constants.py                # MAX_TURNS, etc.
```

**Total:** 21 modules (13 V4 + 8 In_House_SQL)

---

## 🔀 Dual-Mode Operation

### Mode 1: Synchronous (Fast, Direct Response)

**Use Cases:**
- Quick queries ("List my Gmail messages")
- Single-tool calls
- No file uploads
- Fast response required

**Endpoint:** `POST /api/agent/v4/chat`

**Flow:**
```
User Request
    ↓
agent_routes_v4.chat_sync()
    ↓
ConversationManager.handle_chat()  ← V4 modular component
    ├─ UserProfileBuilder.build()
    ├─ SystemPromptBuilder.build()
    ├─ ToolExecutor.execute_tool()  ← V4 credential injection
    └─ SessionHandler.save_session()
    ↓
Return JSON response (10-120 seconds)
```

**Characteristics:**
- ✅ V4 comprehensive logging
- ✅ V4 modular components
- ✅ Direct response (no queue)
- ❌ Blocks Flask thread (but fast for simple tasks)

---

### Mode 2: Asynchronous (Background Worker)

**Use Cases:**
- Complex multi-tool workflows
- File uploads (PDFs, images)
- Long-running tasks
- Multiple concurrent users

**Endpoints:** 
- Start: `POST /api/agent/v4/chat/async/start`
- Stream: `GET /api/agent/v4/chat/async/stream/<session_id>`

**Flow:**
```
User Request
    ↓
agent_routes_v4.chat_async_start()
    ├─ load_or_create_session()  ← In_House_SQL persistence
    ├─ Get queue + lock           ← In_House_SQL state manager
    ├─ Spawn background thread
    └─ Return 200 immediately (50ms)
    
Background Thread: run_agent_worker()
    ├─ Initialize V4 modules:
    │  ├─ ToolExecutor
    │  ├─ UserProfileBuilder
    │  └─ SystemPromptBuilder
    ├─ Multi-turn loop (max 10)
    │  ├─ Call Anthropic (interleaved thinking)
    │  ├─ Execute tools (V4 ToolExecutor)
    │  └─ Queue.put(events)  ← In_House_SQL streaming
    ├─ save_conversation()  ← In_House_SQL persistence
    └─ Release lock
    
Browser: SSE stream
    ↓
agent_routes_v4.chat_async_stream()
    ├─ Get queue
    ├─ queue.get(timeout=30)
    └─ Yield SSE events
```

**Characteristics:**
- ✅ V4 comprehensive logging
- ✅ V4 modular components
- ✅ In_House_SQL patterns (queue, threading, SSE)
- ✅ Session persistence (SQLite)
- ✅ File upload support
- ✅ Interleaved thinking
- ✅ Non-blocking Flask thread

---

## 📊 Component Integration Matrix

| Component | Source | V4 Integration | In_House_SQL Integration |
|-----------|--------|---------------|-------------------------|
| **ToolExecutor** | V4 Modular | ✅ Used directly | ✅ Called from agent_worker.py |
| **ConversationManager** | V4 Modular | ✅ Sync endpoint | ⚠️ Not used in async (replaced by agent_worker.py) |
| **UserProfileBuilder** | V4 Modular | ✅ Both modes | ✅ Called from agent_worker.py |
| **SystemPromptBuilder** | V4 Modular | ✅ Both modes | ✅ Called from agent_worker.py |
| **Logger** | V4 Modular | ✅ All modules | ✅ All modules |
| **UnifiedSessionManager** | In_House_SQL | ✅ Async mode | ✅ SQLite persistence |
| **agent_worker.py** | In_House_SQL | ✅ Uses V4 modules | ✅ Background execution |
| **file_encoding.py** | In_House_SQL | ✅ Async mode | ✅ File uploads |

---

## 🚀 Implementation Roadmap

### Phase 1: V4 Modular Foundation (2.5 hours)
**Goal:** Implement 13 V4 modules with comprehensive logging

**Steps:**
1. ✅ Create folder structure
2. ✅ Implement `utils/logger.py` (centralized logging)
3. ✅ Extract `core/tool_executor.py` from agent_routes_v4.py
4. ✅ Extract `core/tool_processor.py`
5. ✅ Extract `core/session_handler.py`
6. ✅ Extract `core/response_serializer.py`
7. ✅ Create `builders/user_profile_builder.py`
8. ✅ Create `builders/system_prompt_builder.py`
9. ✅ Create `builders/tool_schema_converter.py`
10. ✅ Create `builders/credential_fetcher.py`
11. ✅ Create `core/conversation_manager.py` (orchestrator)
12. ✅ Create 4 meta_tools modules
13. ✅ Simplify `routes/agent_routes_v4.py` (sync endpoint only)

**Testing:**
```python
# Test each module independently
pytest tests/test_tool_executor.py -v
pytest tests/test_user_profile_builder.py -v
pytest tests/test_system_prompt_builder.py -v
# ... etc
```

**Result:** Working synchronous system with excellent logging

---

### Phase 2: In_House_SQL Integration (1.5 hours)
**Goal:** Add async support with session persistence

**Steps:**
1. ✅ Copy 5 core files from In_House_SQL:
   - `core/unified_session_manager.py`
   - `core/agent_state_manager.py`
   - `core/session_persistence.py`
   - `utils/file_encoding.py`
   - `utils/response_helpers.py`

2. ✅ Create `core/agent_worker.py` (adapted version):
   - Uses V4 ToolExecutor (not ToolUseAgent)
   - Uses V4 UserProfileBuilder, SystemPromptBuilder
   - Uses V4 logger (`get_logger()`)
   - Implements In_House_SQL patterns (queue, threading)

3. ✅ Update `routes/agent_routes_v4.py`:
   - Add `/chat/async/start` endpoint
   - Add `/chat/async/stream/<session_id>` endpoint
   - Keep `/chat` (sync) endpoint

4. ✅ Create `data/sessions.db` directory

**Testing:**
```powershell
# Test async endpoints
curl -X POST http://localhost:5001/api/agent/v4/chat/async/start `
    -H "Content-Type: application/json" `
    -d '{"message": "Test", "user_id": 1}'

# Get session_id from response, then stream:
curl http://localhost:5001/api/agent/v4/chat/async/stream/<session_id>
```

**Result:** Dual-mode system (sync + async)

---

## 📝 Updated Module Specifications

### core/agent_worker.py (New - Hybrid)

**Responsibilities:**
1. Background thread execution
2. Uses V4 modular components
3. Implements In_House_SQL patterns
4. Streams events to queue

**Dependencies:**
- V4: ToolExecutor, UserProfileBuilder, SystemPromptBuilder, Logger
- In_House_SQL: Queue, threading.Lock, session_persistence

**Key Methods:**
```python
def run_agent_worker(
    agent_id: str,
    prompt: str,
    file_data: Optional[List[Dict]],  # ← In_House_SQL
    lock: threading.Lock,              # ← In_House_SQL
    session_id: str,                   # ← In_House_SQL
    queue: Queue,                      # ← In_House_SQL
    conversation_history: Optional[List[Dict]],  # ← In_House_SQL
    context: str,
    ai_client,
    user_id: Optional[int]             # ← V4 credential injection
):
    """
    Background worker flow:
    1. Build content blocks from files (In_House_SQL)
    2. Initialize V4 modules (ToolExecutor, ProfileBuilder, etc.)
    3. Multi-turn loop (V4 logic + In_House_SQL streaming)
    4. Save conversation (In_House_SQL persistence)
    5. Release lock (In_House_SQL)
    """
```

---

### routes/agent_routes_v4.py (Updated - 4 Endpoints)

**Endpoints:**
1. `POST /chat` - Synchronous (V4 modular)
2. `POST /chat/async/start` - Start async (In_House_SQL pattern)
3. `GET /chat/async/stream/<session_id>` - SSE stream (In_House_SQL pattern)
4. `GET /session/<session_id>` - Get session data

**Example Usage:**

**Synchronous:**
```javascript
// Fast queries, single tools
fetch('/api/agent/v4/chat', {
    method: 'POST',
    body: JSON.stringify({
        message: "List my Gmail messages",
        session_id: "abc123",
        user_id: 1
    })
})
.then(r => r.json())
.then(data => {
    console.log(data.response);  // Direct response
});
```

**Asynchronous:**
```javascript
// Complex workflows, file uploads
const formData = new FormData();
formData.append('message', 'Analyze these invoices');
formData.append('files', file1);
formData.append('files', file2);
formData.append('user_id', '1');

// Start processing
const start = await fetch('/api/agent/v4/chat/async/start', {
    method: 'POST',
    body: formData
});
const {session_id} = await start.json();

// Stream events
const eventSource = new EventSource(
    `/api/agent/v4/chat/async/stream/${session_id}`
);

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'thinking_block') {
        console.log('💭 Thinking:', data.content);
    } else if (data.type === 'tool_use') {
        console.log('🔧 Tool:', data.tool_name);
    } else if (data.type === 'text_block') {
        console.log('📄 Response:', data.content);
    } else if (data.type === 'complete') {
        console.log('✅ Done:', data.result);
        eventSource.close();
    }
};
```

---

## 🧪 Testing Strategy

### Test V4 Modules Independently
```python
# tests/test_tool_executor.py
from core.tool_executor import ToolExecutor

def test_validation():
    executor = ToolExecutor()
    is_valid, error = executor.validate_tool_call("gmail_send_email", {
        "to": "test@example.com",
        "subject": "Test"
    })
    assert is_valid

def test_credential_injection():
    executor = ToolExecutor()
    params = executor.inject_credentials(
        {"to": "test@example.com"},
        user_id=1,
        credentials={"access_token": "abc"}
    )
    assert "_user_id" in params
    assert params["_user_id"] == 1
```

### Test Async Integration
```python
# tests/test_async_integration.py
import requests
import time

def test_async_workflow():
    # Start processing
    response = requests.post('http://localhost:5001/api/agent/v4/chat/async/start', json={
        "message": "Test async",
        "user_id": 1
    })
    assert response.status_code == 200
    
    data = response.json()
    assert data['success']
    session_id = data['session_id']
    
    # Stream events (first 5 seconds)
    events = []
    start_time = time.time()
    
    with requests.get(
        f'http://localhost:5001/api/agent/v4/chat/async/stream/{session_id}',
        stream=True
    ) as r:
        for line in r.iter_lines():
            if time.time() - start_time > 5:
                break
            if line.startswith(b'data: '):
                event = json.loads(line[6:])
                events.append(event)
    
    # Verify events received
    assert len(events) > 0
    assert any(e['type'] == 'thinking' for e in events)
```

---

## 📊 Performance Comparison

| Metric | Sync (V4) | Async (Integrated) |
|--------|-----------|-------------------|
| **Request latency** | 10-120s (blocking) | <100ms (non-blocking) |
| **Server capacity** | 1 request at a time | 50+ concurrent sessions |
| **File uploads** | ❌ Not supported | ✅ Full support |
| **Session persistence** | ⚠️ Basic | ✅ SQLite + cache |
| **Thinking display** | ⚠️ Limited | ✅ Interleaved (beta) |
| **Logging** | ✅ Comprehensive | ✅ Comprehensive |
| **Modularity** | ✅ 13 modules | ✅ 21 modules |
| **Use case** | Simple queries | Complex workflows |

---

## ✅ Integration Checklist

### Phase 1: V4 Modular Foundation
- [ ] Create folder structure (core, builders, meta_tools, utils, config)
- [ ] Implement `utils/logger.py` (centralized logging)
- [ ] Extract `core/tool_executor.py`
- [ ] Extract `core/tool_processor.py`
- [ ] Extract `core/session_handler.py`
- [ ] Extract `core/response_serializer.py`
- [ ] Create `builders/user_profile_builder.py`
- [ ] Create `builders/system_prompt_builder.py`
- [ ] Create `builders/tool_schema_converter.py`
- [ ] Create `builders/credential_fetcher.py`
- [ ] Create `core/conversation_manager.py`
- [ ] Create 4 meta_tools modules
- [ ] Update `routes/agent_routes_v4.py` (sync endpoint)
- [ ] Test all modules independently
- [ ] Test sync endpoint end-to-end

### Phase 2: In_House_SQL Integration
- [ ] Copy `core/unified_session_manager.py`
- [ ] Copy `core/agent_state_manager.py`
- [ ] Copy `core/session_persistence.py`
- [ ] Copy `utils/file_encoding.py`
- [ ] Copy `utils/response_helpers.py`
- [ ] Create `core/agent_worker.py` (uses V4 modules)
- [ ] Update `routes/agent_routes_v4.py` (add async endpoints)
- [ ] Create `data/sessions.db` directory
- [ ] Test async start endpoint
- [ ] Test SSE stream endpoint
- [ ] Test file upload workflow
- [ ] Test session persistence
- [ ] Test interleaved thinking

### Phase 3: Deployment
- [ ] Update Flask app to register agent_v4_bp
- [ ] Update frontend to support both modes
- [ ] Monitor logs for errors
- [ ] Benchmark performance (sync vs async)
- [ ] Document API for users

---

## 🎯 Summary

**Integrated Solution:**
- ✅ **V4 Modular Architecture** (13 modules, comprehensive logging)
- ✅ **In_House_SQL Patterns** (async, session persistence, SSE, files)
- ✅ **Dual-mode operation** (sync for fast, async for complex)
- ✅ **21 total modules** (vs 1 monolithic file)
- ✅ **Best of both worlds** (modularity + async capabilities)

**Benefits:**
1. **Easy troubleshooting** - V4 logging shows exact module failures
2. **Easy testing** - Each module tested independently
3. **Easy maintenance** - Update one module safely
4. **Easy extension** - Add new modules without breaking existing
5. **Production-ready** - Async handles complex workflows + file uploads
6. **Session persistence** - Survives Flask restarts
7. **Non-blocking** - Async mode doesn't block Flask thread

**Timeline:**
- Phase 1 (V4 Modular): 2.5 hours
- Phase 2 (Integration): 1.5 hours
- **Total: 4 hours** to complete integration

---

**Next Steps:**
1. Implement Phase 1 (V4 Modular Foundation)
2. Test each module
3. Implement Phase 2 (In_House_SQL Integration)
4. Test async workflows
5. Deploy to production

**Ready to begin implementation?**






agent_routes_v4.py (Add Async Endpoints)
``` python

"""
V4 Agent Routes - Enhanced with Async Support
Supports BOTH synchronous (fast) and asynchronous (background) modes
"""

from flask import Blueprint, request, jsonify, Response
from utils.logger import get_logger
from core.conversation_manager import ConversationManager
from core.agent_worker import run_agent_worker  # ← NEW: Background worker
from core.agent_state_manager import agent_state_manager  # ← NEW
from core.session_persistence import load_or_create_session  # ← NEW
from utils.file_encoding import process_file_uploads, FileValidationError  # ← NEW
import threading
from queue import Empty
import json

logger = get_logger(__name__)
agent_bp = Blueprint('agent_v4', __name__)

# ============================================================
# SYNCHRONOUS ENDPOINT (Original V4 - Fast, Direct Response)
# ============================================================

@agent_bp.route('/chat', methods=['POST'])
def chat_sync():
    """
    Synchronous chat - Returns response immediately
    Use for: Quick queries, single-tool calls, simple tasks
    """
    logger.info("📨 Received SYNC chat request")
    
    try:
        data = request.get_json()
        message = data.get('message')
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        
        # Delegate to conversation manager (synchronous)
        manager = ConversationManager()
        response = manager.handle_chat(message, session_id, user_id)
        
        logger.info(f"✅ Sync chat completed: {len(response.get('tools_used', []))} tools")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Sync chat failed: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# ============================================================
# ASYNCHRONOUS ENDPOINTS (New - Background Worker Pattern)
# ============================================================

@agent_bp.route('/chat/async/start', methods=['POST'])
def chat_async_start():
    """
    Start async chat in background thread
    Use for: Complex multi-tool workflows, file uploads, long-running tasks
    
    Request (JSON):
    {
        "message": "...",
        "session_id": "uuid" (optional),
        "user_id": 1
    }
    
    Request (FormData with files):
    - message
    - session_id (optional)
    - user_id
    - files[] (multiple uploads)
    
    Returns:
    {
        "success": true,
        "session_id": "uuid",
        "status": "processing"
    }
    """
    logger.info("📨 Received ASYNC chat start request")
    
    try:
        # Determine request type
        is_form_data = request.content_type and 'multipart/form-data' in request.content_type
        
        if is_form_data:
            # File upload workflow
            session_id = request.form.get('session_id')
            message = request.form.get('message', '')
            user_id = int(request.form.get('user_id', 0))
            
            files = request.files.getlist('files')
            if not files:
                return jsonify({"error": "No files uploaded"}), 400
            
            try:
                file_data = process_file_uploads(files)
            except FileValidationError as e:
                return jsonify({"error": str(e)}), 400
        else:
            # Text-only workflow
            data = request.json or {}
            session_id = data.get('session_id')
            message = data.get('message', '')
            user_id = data.get('user_id', 0)
            file_data = None
        
        if not message:
            return jsonify({"error": "Missing 'message'"}), 400
        
        # Load or create session (with conversation history)
        logger.debug("📂 Loading/creating session...")
        state = load_or_create_session(
            agent_id='agent_v4',
            session_id=session_id,
            ui_context='agent_v4'
        )
        session_id = state['session_id']
        
        # Get execution lock and queue
        lock = agent_state_manager.get_lock('agent_v4', session_id)
        queue = agent_state_manager.get_queue('agent_v4', session_id)
        
        # Get AI client
        from core.unified_ai_client import get_ai_client
        ai_client = get_ai_client()
        
        # Start background worker
        logger.info(f"🚀 Spawning background worker: session={session_id[:8]}")
        threading.Thread(
            target=run_agent_worker,
            args=(
                'agent_v4',
                message,
                file_data,
                lock,
                session_id,
                queue,
                state['conversation'],
                'agent_v4',
                ai_client,
                user_id
            ),
            daemon=True
        ).start()
        
        logger.info(f"✅ Async chat started: session={session_id[:8]}")
        return jsonify({
            'success': True,
            'session_id': session_id,
            'status': 'processing',
            'files_uploaded': len(file_data) if file_data else 0
        })
        
    except Exception as e:
        logger.error(f"❌ Async start failed: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@agent_bp.route('/chat/async/stream/<session_id>', methods=['GET'])
def chat_async_stream(session_id):
    """
    SSE stream for async chat
    
    Returns:
        text/event-stream with events:
        - thinking_block
        - tool_use
        - tool_result
        - text_block
        - complete
        - error
    """
    logger.info(f"📡 Starting SSE stream: session={session_id[:8]}")
    
    queue = agent_state_manager.get_queue('agent_v4', session_id)
    
    def generate():
        timeout_count = 0
        max_timeout = 3
        
        while True:
            try:
                # Blocking read with timeout
                log_entry = queue.get(timeout=30)
                timeout_count = 0
                
                # Send as SSE
                yield f"data: {json.dumps(log_entry)}\n\n"
                
                # Check for completion
                if log_entry.get('type') in ['complete', 'error']:
                    logger.info(f"✅ Stream complete: {log_entry.get('type')}")
                    break
                
            except Empty:
                timeout_count += 1
                if timeout_count >= max_timeout:
                    logger.warning(f"⏱️ Stream timeout: session={session_id[:8]}")
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
# UTILITY ENDPOINTS
# ============================================================

@agent_bp.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session data including conversation history"""
    from core.unified_session_manager import session_manager
    
    session_data = session_manager.get_session(session_id)
    if not session_data:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify({'success': True, 'session': session_data})


@agent_bp.route('/tools', methods=['GET'])
def list_tools():
    """List available tools"""
    # Implementation...


@agent_bp.route('/status', methods=['GET'])
def status():
    """Health check"""
    return jsonify({
        'status': 'operational',
        'endpoints': {
            'sync': '/chat',
            'async_start': '/chat/async/start',
            'async_stream': '/chat/async/stream/<session_id>',
            'session': '/session/<session_id>'
        }
    })


```

Key Changes:

✅ 3 endpoints instead of 1: /chat (sync), /chat/async/start, /chat/async/stream
✅ File upload support via process_file_uploads()
✅ Session persistence via load_or_create_session()
✅ Background worker via agent_worker.py
✅ SSE streaming via queue-based events







 agent_worker.py (New - Uses V4 Modules)

``` python

"""
Agent Worker - Background thread that uses V4 modular components
Integrates: ToolExecutor, ConversationManager, V4 logging
"""

import json
import threading
from typing import List, Dict, Any, Optional
from queue import Queue
import base64

from utils.logger import get_logger
from core.tool_executor import ToolExecutor  # ← V4 module
from core.session_handler import SessionHandler  # ← V4 module
from builders.user_profile_builder import UserProfileBuilder  # ← V4 module
from builders.system_prompt_builder import SystemPromptBuilder  # ← V4 module
from config.constants import MAX_TURNS

logger = get_logger(__name__)


def run_agent_worker(
    agent_id: str,
    prompt: str,
    file_data: Optional[List[Dict[str, Any]]],
    lock: threading.Lock,
    session_id: str,
    queue: Queue,
    conversation_history: Optional[List[Dict]] = None,
    context: str = 'agent_v4',
    ai_client = None,
    user_id: Optional[int] = None
):
    """
    Background worker that uses V4 modular components
    
    Flow:
    1. Build content blocks from files
    2. Initialize V4 modules (ToolExecutor, UserProfileBuilder, etc.)
    3. Multi-turn loop with Claude
    4. Stream events to queue
    5. Save conversation
    6. Release lock
    """
    
    logger.info(f"🧵 Agent worker started: session={session_id[:8]}, user={user_id}")
    
    try:
        # Build content blocks from files
        content_blocks = []
        
        if file_data:
            for file_info in file_data:
                filename = file_info.get('filename', 'unknown')
                content_type = file_info.get('content_type', 'application/octet-stream')
                file_bytes = file_info.get('data', b'')
                
                # Base64 encode
                encoded_data = base64.b64encode(file_bytes).decode('utf-8')
                
                # Determine block type
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
                
                logger.info(f"📎 Added {block_type}: {filename}")
        
        # Add text prompt
        if prompt:
            content_blocks.append({
                'type': 'text',
                'text': prompt
            })
        
        # Initialize V4 modules
        logger.debug("🔧 Initializing V4 modules...")
        tool_executor = ToolExecutor()
        session_handler = SessionHandler()
        profile_builder = UserProfileBuilder()
        prompt_builder = SystemPromptBuilder()
        
        # Build user profile
        logger.debug("👤 Building user profile...")
        profile = profile_builder.build(user_id)
        logger.debug(f"✅ Profile: {profile.get('username', 'unknown')}")
        
        # Build system prompt
        logger.debug("📝 Building system prompt...")
        system_prompt = prompt_builder.build(profile)
        logger.debug(f"✅ System prompt: {len(system_prompt)} chars")
        
        # Build messages array
        messages = conversation_history or []
        messages.append({
            'role': 'user',
            'content': content_blocks if content_blocks else prompt
        })
        
        # Multi-turn loop
        logger.info(f"🔄 Starting multi-turn loop (max {MAX_TURNS} turns)")
        tool_calls = 0
        thinking_tokens = 0
        
        for turn in range(MAX_TURNS):
            logger.info(f"📍 Turn {turn + 1}/{MAX_TURNS}")
            
            queue.put({
                'type': 'thinking',
                'content': f'Processing turn {turn + 1}...'
            })
            
            # Call Anthropic API
            logger.debug("🤖 Calling Claude API...")
            response = ai_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=16000,
                temperature=1.0,
                
                # Interleaved thinking
                thinking={
                    "type": "enabled",
                    "budget_tokens": 10000
                },
                extra_headers={
                    "anthropic-beta": "interleaved-thinking-2025-05-14"
                },
                
                # Tools from registry
                tools=tool_executor.registry.get_tool_schemas(),
                tool_choice={"type": "auto"},
                
                system=system_prompt,
                messages=messages
            )
            
            logger.debug(f"✅ Claude responded: stop_reason={response.stop_reason}")
            
            # Track thinking tokens
            thinking_tokens += response.usage.input_tokens + response.usage.output_tokens
            
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
                    logger.debug(f"💭 Thinking: {len(block.thinking)} chars")
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
                    
                    logger.info(f"🔧 Tool use: {tool_name}")
                    queue.put({
                        'type': 'tool_use',
                        'tool_name': tool_name,
                        'input': tool_input
                    })
                    
                    # Execute tool with V4 ToolExecutor
                    try:
                        tool_result = tool_executor.execute_tool(
                            tool_name=tool_name,
                            parameters=tool_input,
                            user_id=user_id,
                            credentials=profile.get('credentials')
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
                        logger.error(f"❌ Tool execution failed: {e}")
                        queue.put({
                            'type': 'tool_result',
                            'tool_name': tool_name,
                            'success': False,
                            'error': str(e)
                        })
                
                elif block.type == "text":
                    # Text response
                    queue.put({
                        'type': 'text_block',
                        'content': block.text
                    })
                    logger.debug(f"📄 Text: {len(block.text)} chars")
                    assistant_message.append({
                        'type': 'text',
                        'text': block.text
                    })
            
            # Check if done
            if not has_tool_use or response.stop_reason != "tool_use":
                logger.info(f"✅ Conversation complete after {turn + 1} turns")
                
                # Extract final response
                final_text = ''.join(
                    b['text'] for b in assistant_message if b.get('type') == 'text'
                )
                
                # Save conversation
                messages.append({
                    'role': 'assistant',
                    'content': final_text
                })
                
                logger.debug("💾 Saving conversation...")
                from core.session_persistence import save_conversation
                save_conversation('agent_v4', session_id, messages)
                
                # Signal completion
                queue.put({
                    'type': 'complete',
                    'result': final_text,
                    'session_id': session_id,
                    'tool_calls': tool_calls,
                    'thinking_tokens': thinking_tokens
                })
                
                logger.info(f"🎉 Worker complete: {tool_calls} tools, {thinking_tokens} tokens")
                break
        
    except Exception as e:
        logger.error(f"❌ Worker failed: {e}", exc_info=True)
        queue.put({
            'type': 'error',
            'error': str(e)
        })
    
    finally:
        # Release lock
        try:
            lock.release()
            logger.debug("🔓 Lock released")
        except Exception as e:
            logger.error(f"❌ Lock release error: {e}")
```
Key Integration:

✅ Uses V4 ToolExecutor (not In_House_SQL ToolUseAgent)
✅ Uses V4 UserProfileBuilder, SystemPromptBuilder
✅ Uses V4 logging system (get_logger())
✅ Implements In_House_SQL patterns (queue, threading, SSE)
✅ Supports interleaved thinking (beta header)
✅ Handles file uploads (base64 encoding)



``` python
