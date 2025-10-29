# 🎯 Agent Endpoints Migration Guide - NEW Flask

**Date**: October 23, 2025  
**Target**: Migrate ONLY Triple Agent endpoints to NEW Flask  
**Status**: Stock AI Chat endpoint DELETED - Do NOT migrate  

---

## ⚠️ CRITICAL: What NOT to Migrate

### ❌ DELETED from OLD Flask:
- `/api/stock/chat-with-document-stream` (POST) - **REMOVED October 23, 2025**
- Reason: Redundant with `/agent/<id>/start` which already supports files
- **DO NOT bring any Stock AI Chat-specific code to NEW Flask**

### ❌ DO NOT Migrate These Patterns:
- Stock AI Chat rendering logic
- Stock AI Chat message bubbles
- Stock AI Chat-specific streaming
- `run_stock_agent_worker()` function
- Any Stock-specific UI handling

### ✅ What Stock AI Chat WILL Use:
- **Standard endpoints**: `/agent/stock_ai/start` + `/stream/stock_ai`
- **Same as Triple Agent**: No special treatment
- **Frontend update needed**: stock_management.html will be updated later

---

## 🎯 What TO Migrate: Triple Agent Endpoints Only

### Core Endpoints (4 endpoints):

1. **`/agent/<agent_id>/start`** (POST) - Start any agent
2. **`/stream/<agent_id>`** (GET) - Stream results via SSE
3. **`/agent/<agent_id>/status`** (GET) - Get agent status
4. **`/agent/<agent_id>/history`** (GET) - Get conversation history

### Optional Endpoints (2 endpoints):

5. **`/agent/<agent_id>/clear`** (POST) - Clear conversation
6. **`/api/agent/chat-with-document-stream`** (POST) - Single Agent Viewer document chat

---

## 📋 Migration Plan

### Phase 1: Core Agent Engine (HIGH PRIORITY)

**Endpoint 1: `/agent/<agent_id>/start`** (POST)
- **Location**: agent_routes.py
- **Lines in OLD Flask**: 1375-1516 (141 lines)
- **What it does**: Starts ToolUseAgent in background thread
- **Supports**: JSON (text) and FormData (files)
- **Thread safety**: Execution locks per agent
- **Returns**: `{"status": "started", "session_id": "..."}`

**Key Functions to Adapt**:
```python
# FROM OLD Flask (DO adapt for NEW Flask)
get_or_create_agent_state(agent_id, session_id)  # Agent state management
get_or_create_execution_lock(agent_id, session_id)  # Thread safety
run_agent_worker(agent_id, prompt, file_data, lock, session_id)  # ToolUseAgent worker

# REPLACE WITH (NEW Flask equivalents)
session_manager.get_session(session_id)  # Use unified session manager
ai_client.create_message(...)  # Use unified AI client
# Create similar worker function using NEW Flask's unified components
```

---

**Endpoint 2: `/stream/<agent_id>`** (GET)
- **Location**: agent_routes.py
- **Lines in OLD Flask**: 1516-1606 (90 lines)
- **What it does**: SSE streaming from agent queue
- **Returns**: `text/event-stream`
- **Timeout**: 30 seconds with keepalive
- **Event types**: thinking, tool_use, response, complete, error

**Key Functions to Adapt**:
```python
# FROM OLD Flask
def stream_agent(agent_id):
    state = get_or_create_agent_state(agent_id, session_id)
    queue = state['queue']
    
    def generate():
        while True:
            event = queue.get(timeout=30)
            yield f"data: {json.dumps(event)}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

# ADAPT FOR NEW Flask
# Same pattern but use unified_session_manager for state
```

---

### Phase 2: Agent Management (MEDIUM PRIORITY)

**Endpoint 3: `/agent/<agent_id>/status`** (GET)
- **Lines in OLD Flask**: 1606-1622 (16 lines)
- **Simple**: Returns agent status from state
```python
{
    "agent_id": "1",
    "name": "Data Navigator",
    "status": "idle",  # or "running"
    "conversation_length": 5,
    "session_id": "..."
}
```

**Endpoint 4: `/agent/<agent_id>/history`** (GET)
- **Lines in OLD Flask**: 1622-1636 (14 lines)
- **Simple**: Returns conversation array from state
```python
{
    "agent_id": "1",
    "conversation": [
        {"role": "user", "content": "...", "timestamp": "..."},
        {"role": "assistant", "content": "...", "timestamp": "..."}
    ],
    "session_id": "..."
}
```

---

### Phase 3: Optional Features (LOW PRIORITY)

**Endpoint 5: `/agent/<agent_id>/clear`** (POST)
- **Lines in OLD Flask**: 1636-1650 (14 lines)
- **Simple**: Clears conversation array
- **Error**: 400 if agent is running

**Endpoint 6: `/api/agent/chat-with-document-stream`** (POST)
- **Lines in OLD Flask**: 3115-3300 (185 lines)
- **For**: Single Agent Viewer document chat
- **Optional**: Can be added later if Single Agent Viewer needs it
- **Alternative**: Single Agent Viewer can use `/agent/single_viewer/start` + `/stream/single_viewer`

---

## 🔧 Implementation Steps

### Step 1: Create Agent State Manager (NEW Flask)
**File**: `AI_infrastructure/core/agent_state_manager.py` (NEW FILE)

```python
"""
Agent State Manager - Manages agent execution state
Replaces OLD Flask's get_or_create_agent_state() pattern
"""
import threading
from queue import Queue
from datetime import datetime

class AgentStateManager:
    def __init__(self):
        self.agents = {}  # agent_id -> state dict
        self.locks = {}   # agent_id -> threading.Lock
    
    def get_or_create_state(self, agent_id, session_id):
        """Get or create agent state (thread-safe)"""
        key = f"{agent_id}_{session_id}"
        
        if key not in self.agents:
            self.agents[key] = {
                'agent_id': agent_id,
                'session_id': session_id,
                'status': 'idle',
                'conversation': [],
                'queue': Queue(),
                'last_activity': datetime.now(),
                'context': 'triple_agent'  # or 'single_viewer'
            }
            self.locks[key] = threading.Lock()
        
        return self.agents[key]
    
    def get_lock(self, agent_id, session_id):
        """Get execution lock for agent"""
        key = f"{agent_id}_{session_id}"
        if key not in self.locks:
            self.locks[key] = threading.Lock()
        return self.locks[key]

# Global instance
agent_state_manager = AgentStateManager()
```

---

### Step 2: Create Agent Worker (NEW Flask)
**File**: `AI_infrastructure/core/agent_worker.py` (NEW FILE)

```python
"""
Agent Worker - Background thread that runs ToolUseAgent
"""
from core.tool_use_agent import ToolUseAgent
from core.unified_ai_client import ai_client

def run_agent_worker(agent_id, prompt, file_data, lock, session_id, queue):
    """
    Background worker that executes ToolUseAgent
    
    Args:
        agent_id: Agent identifier (1, 2, 3, stock_ai, single_viewer)
        prompt: User prompt text
        file_data: List of file dicts with filename, content_type, data
        lock: threading.Lock for thread safety
        session_id: Session ID
        queue: Queue for SSE events
    """
    try:
        # Build content blocks from files
        content_blocks = []
        for file_info in file_data:
            # ... (convert to content blocks)
        
        # Add text prompt
        content_blocks.append({"type": "text", "text": prompt})
        
        # Create ToolUseAgent
        agent = ToolUseAgent(
            agent_id=agent_id,
            ai_client=ai_client,
            session_id=session_id
        )
        
        # Execute with streaming
        for event in agent.execute_with_streaming(content_blocks):
            queue.put(event)
        
        # Signal completion
        queue.put({'type': 'complete', 'result': agent.final_response})
        
    except Exception as e:
        queue.put({'type': 'error', 'error': str(e)})
    
    finally:
        lock.release()
```

---

### Step 3: Implement Routes (NEW Flask)
**File**: `AI_infrastructure/routes/agent_routes.py` (MODIFY EXISTING)

```python
"""
Agent Routes Blueprint - Triple Agent endpoints
"""
from flask import Blueprint, request, jsonify, Response
from core.agent_state_manager import agent_state_manager
from core.agent_worker import run_agent_worker
import threading
import json

agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/<agent_id>/start', methods=['POST'])
def start_agent(agent_id):
    """
    Start agent with text or files
    
    POST /api/agent/1/start
    
    JSON: {"prompt": "text"}
    FormData: {prompt: "text", files: [file1, file2]}
    """
    # Extract session_id
    session_id = request.form.get('session_id') or request.json.get('session_id')
    if not session_id:
        from core.unified_session_manager import session_manager
        session_id = session_manager.create_session('triple_agent')
    
    # Get agent state
    state = agent_state_manager.get_or_create_state(agent_id, session_id)
    
    # Check if already running
    if state['status'] == 'running':
        return jsonify({'error': 'Agent already running'}), 400
    
    # Get execution lock (thread safety)
    lock = agent_state_manager.get_lock(agent_id, session_id)
    if not lock.acquire(blocking=False):
        return jsonify({'error': 'Agent is busy'}), 400
    
    # Extract prompt and files
    if request.content_type and 'multipart/form-data' in request.content_type:
        prompt = request.form.get('prompt', '')
        files = request.files.getlist('files')
        
        # Read file bytes NOW (before request context closes)
        file_data = []
        for file in files:
            file_data.append({
                'filename': file.filename,
                'content_type': file.content_type,
                'data': file.read()
            })
    else:
        data = request.get_json() or {}
        prompt = data.get('prompt', '')
        file_data = []
    
    if not prompt and not file_data:
        lock.release()
        return jsonify({'error': 'Prompt or files required'}), 400
    
    # Update state
    state['status'] = 'running'
    state['conversation'].append({
        'role': 'user',
        'content': prompt,
        'files': len(file_data),
        'timestamp': datetime.now().isoformat()
    })
    
    # Launch worker thread
    queue = state['queue']
    worker = threading.Thread(
        target=run_agent_worker,
        args=(agent_id, prompt, file_data, lock, session_id, queue),
        daemon=True
    )
    worker.start()
    
    return jsonify({
        'status': 'started',
        'agent_id': agent_id,
        'session_id': session_id
    })


@agent_bp.route('/<agent_id>/stream', methods=['GET'])
def stream_agent(agent_id):
    """
    SSE stream from agent queue
    
    GET /api/agent/1/stream
    """
    session_id = request.args.get('session_id')
    state = agent_state_manager.get_or_create_state(agent_id, session_id)
    queue = state['queue']
    
    def generate():
        while True:
            try:
                event = queue.get(timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
                
                if event.get('type') in ['complete', 'error']:
                    state['status'] = 'idle'
                    break
            except Empty:
                # Keepalive
                yield f": keepalive\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


@agent_bp.route('/<agent_id>/status', methods=['GET'])
def get_agent_status(agent_id):
    """Get agent status"""
    session_id = request.args.get('session_id')
    state = agent_state_manager.get_or_create_state(agent_id, session_id)
    
    return jsonify({
        'agent_id': agent_id,
        'status': state['status'],
        'conversation_length': len(state['conversation']),
        'session_id': session_id
    })


@agent_bp.route('/<agent_id>/history', methods=['GET'])
def get_agent_history(agent_id):
    """Get conversation history"""
    session_id = request.args.get('session_id')
    state = agent_state_manager.get_or_create_state(agent_id, session_id)
    
    return jsonify({
        'agent_id': agent_id,
        'conversation': state['conversation'],
        'session_id': session_id
    })


@agent_bp.route('/<agent_id>/clear', methods=['POST'])
def clear_agent(agent_id):
    """Clear conversation"""
    session_id = request.args.get('session_id')
    state = agent_state_manager.get_or_create_state(agent_id, session_id)
    
    if state['status'] == 'running':
        return jsonify({'error': 'Cannot clear while running'}), 400
    
    state['conversation'] = []
    return jsonify({'status': 'cleared'})
```

---

### Step 4: Register Blueprint (NEW Flask)
**File**: `AI_infrastructure/flask_app.py` (MODIFY EXISTING)

```python
from routes.agent_routes import agent_bp

# Register with /api/agent prefix (NOT /agent)
app.register_blueprint(agent_bp, url_prefix='/api/agent')
```

---

### Step 5: Test Triple Agent UI

```powershell
# Start NEW Flask
RESTARTNEW

# Test Triple Agent
Start-Process http://localhost:5001/triple-agent

# Test each agent:
# 1. Agent 1 (Data Navigator) - Enter prompt → Should call /api/agent/1/start
# 2. Agent 2 (Query Expert) - Enter prompt → Should call /api/agent/2/start
# 3. Agent 3 (Calculator) - Enter prompt → Should call /api/agent/3/start

# Verify SSE streams working
# Should see real-time thinking/tool/response bubbles
```

---

## 📝 Summary

### What We're Migrating:
✅ `/agent/<id>/start` - Universal agent start (text + files)  
✅ `/stream/<id>` - Universal SSE streaming  
✅ `/agent/<id>/status` - Agent status  
✅ `/agent/<id>/history` - Conversation history  
✅ `/agent/<id>/clear` - Clear conversation  

### What We're NOT Migrating:
❌ `/api/stock/chat-with-document-stream` - **DELETED**  
❌ Stock AI Chat-specific rendering  
❌ Stock AI Chat message bubbles  
❌ Stock AI Chat-specific streaming logic  
❌ `run_stock_agent_worker()` function  

### Stock AI Chat Will Use:
- Same endpoints as Triple Agent
- `/agent/stock_ai/start` + `/stream/stock_ai`
- Frontend update needed (later)

---

## 🎯 Next Steps

1. **Create 3 new files** in NEW Flask:
   - `core/agent_state_manager.py` (agent state)
   - `core/agent_worker.py` (background worker)
   - Update `routes/agent_routes.py` (endpoints)

2. **Test with Triple Agent UI** at http://localhost:5001/triple-agent

3. **Later**: Update Stock Management UI to use standard endpoints

**Estimated Time**: 2-3 hours for full implementation + testing

---

**Ready to start?** Begin with `agent_state_manager.py` - it's the foundation for everything else!
