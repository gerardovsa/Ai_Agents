# AI Infrastructure Migration Guide

**Complete step-by-step guide to swapping from old architecture to new unified system**

---

## Table of Contents
1. [Overview](#overview)
2. [Pre-Migration Checklist](#pre-migration-checklist)
3. [Testing New System](#testing-new-system)
4. [Migration Steps](#migration-steps)
5. [Rollback Procedure](#rollback-procedure)
6. [Verification](#verification)

---

## Overview

### What's Changing

**Before (Old Architecture):**
- 4 separate session dictionaries: `agent_states`, `agent_sessions`, `active_sessions`, `agent_execution_locks`
- Multiple Anthropic client instances (new client per request)
- Duplicate system prompts in each endpoint
- Overlapping SSE streaming logic

**After (New Architecture):**
- Single `UnifiedSessionManager` with SQLite persistence
- Single `UnifiedAnthropicClient` instance (reusable)
- System prompts centralized by UI context
- Unified SSE streaming via `/api/stream/<session_id>`

### Benefits
 **Simpler code**: 1 session manager instead of 4 dicts  
 **Better performance**: Reuse Anthropic client (avoid re-initialization)  
 **Persistence**: Sessions survive server restarts (SQLite)  
 **Thread-safe**: Proper Queue and Lock management  
 **Maintainable**: System prompts in one place  
 **Testable**: Complete test suite included

---

## Pre-Migration Checklist

### 1. Backup Current System

```powershell
# Backup entire G_Folder
cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item -Path "." -Destination "../G_Folder_BACKUP_$timestamp" -Recurse -Exclude @("__pycache__", "*.pyc", ".venv")

Write-Host " Backup created: G_Folder_BACKUP_$timestamp"
```

### 2. Backup Flask App

```powershell
# Backup flask_triple_agent_app.py
cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator\AI_Quote_Agent\web_interface
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item flask_triple_agent_app.py "flask_triple_agent_app_BACKUP_$timestamp.py"

Write-Host " Flask app backed up"
```

### 3. Verify Tests Pass

```powershell
cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder

# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio

# Run all tests
python -m pytest AI_infrastructure/tests/ -v

# Expected output:
# test_session_manager.py::test_create_session PASSED
# test_session_manager.py::test_update_conversation PASSED
# test_anthropic_client.py::test_initialization PASSED
# test_integration.py::test_complete_chat_flow PASSED
# ... (more tests)
# ========== X passed in Y seconds ==========
```

**CRITICAL**: ALL tests must pass before migration!

---

## Testing New System

### Option 1: Side-by-Side Testing (Recommended)

Run new system on different port WITHOUT touching active system:

```python
# Create test_new_system.py in AI_infrastructure folder
from flask import Flask
from flask_integration import create_unified_routes

app = Flask(__name__)
create_unified_routes(app, config_path='../config/database-config.json')

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Different port!
```

```powershell
# Run test server
cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure
python test_new_system.py

# Server runs on http://localhost:5001
# Active system still running on http://localhost:5000
```

Test endpoints manually:
```powershell
# Create session
curl -X POST http://localhost:5001/api/session/create `
  -H "Content-Type: application/json" `
  -d '{"ui_context": "stock_chat"}'

# Response: {"session_id": "uuid-here"}

# Send message
curl -X POST http://localhost:5001/api/chat/send `
  -H "Content-Type: application/json" `
  -d '{"session_id": "uuid-here", "prompt": "Hello"}'

# Response: {"status": "processing", "session_id": "uuid-here"}

# Stream response (open in browser)
# http://localhost:5001/api/stream/uuid-here
```

### Option 2: Automated Testing

```powershell
cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder

# Run integration tests
python -m pytest AI_infrastructure/tests/test_integration.py -v

# Run all tests with coverage
python -m pytest AI_infrastructure/tests/ --cov=AI_infrastructure --cov-report=term-missing
```

---

## Migration Steps

### Step 1: Update Flask App Imports

**File**: `flask_triple_agent_app.py`

**Find (around line 30-50):**
```python
from anthropic import Anthropic
import uuid
from queue import Queue
import threading

# Old session management
agent_states = {}
agent_sessions = {}
active_sessions = {}
agent_execution_locks = {}
```

**Replace with:**
```python
from anthropic import Anthropic
import uuid
from queue import Queue
import threading

# NEW: Import unified infrastructure
import sys
import os
ai_infra_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'AI_infrastructure')
sys.path.insert(0, ai_infra_path)

from core.unified_session_manager import session_manager
from core.unified_anthropic_client import init_anthropic_client

# Initialize Anthropic client once
config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'database-config.json')
anthropic_client = init_anthropic_client(config_path)

print("[FlaskApp]  Unified AI infrastructure initialized")
```

### Step 2: Replace Stock Chat Endpoint

**Find endpoint (around line 1800-2000):**
```python
@app.route('/stock/chat', methods=['POST'])
def stock_chat():
    # OLD: Complex session management logic
    session_id = request.form.get('session_id') or str(uuid.uuid4())
    
    if session_id not in active_sessions:
        active_sessions[session_id] = {
            'queue': Queue(),
            'conversation': [],
            'lock': threading.Lock()
        }
    # ... 100+ lines of code
```

**Replace with:**
```python
@app.route('/stock/chat', methods=['POST'])
def stock_chat():
    """Stock AI Chat - Uses unified infrastructure"""
    
    # Get or create session
    session_id = request.form.get('session_id')
    if not session_id or not session_manager.get_session(session_id):
        session_id = session_manager.create_session('stock_chat')
    
    prompt = request.form.get('prompt', '')
    files = request.files.getlist('files') if request.files else None
    
    # Get execution lock
    lock = session_manager.get_lock(session_id)
    if lock.locked():
        return jsonify({'error': 'Already processing'}), 409
    
    # Get session data
    session = session_manager.get_session(session_id)
    queue = session_manager.get_queue(session_id)
    
    # Start background processing
    def process():
        with lock:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                updated_conversation = loop.run_until_complete(
                    anthropic_client.process_streaming(
                        session_id=session_id,
                        session_data=session,
                        prompt=prompt,
                        files=files,
                        sse_callback=lambda event: queue.put(event)
                    )
                )
                
                session_manager.update_conversation(session_id, updated_conversation)
                
            except Exception as e:
                print(f"[StockChat] Error: {e}")
                queue.put({'type': 'error', 'message': str(e)})
    
    threading.Thread(target=process, daemon=True).start()
    
    return jsonify({'status': 'processing', 'session_id': session_id})
```

### Step 3: Replace Stock Chat Stream Endpoint

**Find (around line 2100):**
```python
@app.route('/stock/stream')
def stock_stream():
    session_id = request.args.get('session_id')
    
    if session_id not in active_sessions:
        return Response("Invalid session", status=404)
    
    queue = active_sessions[session_id]['queue']
    # ... streaming logic
```

**Replace with:**
```python
@app.route('/stock/stream')
def stock_stream():
    """Stock AI Chat stream - Uses unified infrastructure"""
    session_id = request.args.get('session_id')
    
    if not session_manager.get_session(session_id):
        return Response("Invalid session", status=404)
    
    queue = session_manager.get_queue(session_id)
    
    def generate():
        try:
            while True:
                try:
                    from queue import Empty
                    event = queue.get(timeout=30)
                    
                    if event.get('type') in ['done', 'complete']:
                        yield f"data: {json.dumps(event)}\n\n"
                        break
                    
                    yield f"data: {json.dumps(event)}\n\n"
                
                except Empty:
                    yield f"data: {json.dumps({'type': 'ping'})}\n\n"
        
        except GeneratorExit:
            print(f"[Stream] Client disconnected: {session_id}")
    
    return Response(generate(), mimetype='text/event-stream')
```

### Step 4: Repeat for Other Endpoints

Apply same pattern to:
- `/data-agent/chat` and `/data-agent/stream`
- `/agent/<agent_id>/start` and `/stream/<agent_id>`
- `/single-viewer/chat` and `/single-viewer/stream`

### Step 5: Remove Old Session Dicts

**Find and DELETE (around line 50-100):**
```python
agent_states = {}
agent_sessions = {}
active_sessions = {}
agent_execution_locks = {}
```

These are now replaced by `session_manager` singleton.

### Step 6: Restart Flask Server

```powershell
cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder
.\restart_servers.ps1
```

Watch for initialization message:
```
[FlaskApp]  Unified AI infrastructure initialized
[SessionManager] Initialized with database: sessions.db
[AnthropicClient] Initialized with model: claude-sonnet-4-5-20250929
```

---

## Rollback Procedure

If issues occur, rollback is simple:

### Quick Rollback

```powershell
# Stop Flask server
Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.MainWindowTitle -like "*flask*"} | Stop-Process -Force

# Restore backup
cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator\AI_Quote_Agent\web_interface
Copy-Item "flask_triple_agent_app_BACKUP_YYYYMMDD_HHMMSS.py" "flask_triple_agent_app.py" -Force

# Restart server
cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder
.\restart_servers.ps1
```

### Full Rollback (if needed)

```powershell
# Restore entire G_Folder from backup
cd C:\Users\gpoli\GIT\In_House_SQL
Remove-Item -Path "G_Folder" -Recurse -Force
Copy-Item -Path "G_Folder_BACKUP_YYYYMMDD_HHMMSS" -Destination "G_Folder" -Recurse

# Restart
cd G_Folder
.\restart_servers.ps1
```

---

## Verification

### 1. Test Each UI

**Stock AI Chat:**
1. Navigate to http://localhost:5000/stock-management
2. Click "Stock AI Chat" column
3. Type message: "Show me all stocks"
4. Verify response streams correctly
5. Upload PDF invoice
6. Verify file analysis works

**Data Agent Chat:**
1. Navigate to http://localhost:5000/data-agent-chat
2. Type query: "Show recent jobs"
3. Verify SQL generation works
4. Check charts render (Plotly)
5. Check diagrams render (Mermaid)

**Triple Agent:**
1. Navigate to http://localhost:5000/
2. Click each agent tab (1, 2, 3)
3. Test message in each
4. Verify streaming works

**Single Viewer:**
1. Navigate to http://localhost:5000/single-viewer
2. Test query
3. Verify response

### 2. Check Session Persistence

```powershell
# Test session survives restart

# 1. Start conversation in Stock Chat
# 2. Note session ID from browser console
# 3. Restart Flask server
cd G_Folder ; .\restart_servers.ps1

# 4. Check session exists in database
cd AI_infrastructure
python -c "
from core.unified_session_manager import session_manager
session = session_manager.get_session('YOUR-SESSION-ID-HERE')
print(f'Session exists: {session is not None}')
print(f'Conversation length: {len(session.get(\"conversation\", []))}')
"
```

### 3. Check Database

```powershell
# Verify sessions.db created
cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure

# Check database
sqlite3 sessions.db "SELECT COUNT(*) as total_sessions FROM sessions;"
sqlite3 sessions.db "SELECT session_id, ui_context, created_at FROM sessions ORDER BY created_at DESC LIMIT 5;"
```

### 4. Performance Check

Monitor console output for:
```
[AnthropicClient] ✓ Reusing existing client (fast!)
[SessionManager] ✓ Cache hit for session abc-123 (instant)
```

Should NOT see:
```
[AnthropicClient] Creating new client instance... (SLOW - should only happen once!)
```

### 5. Error Monitoring

Check for any errors in Flask console:
```
[SessionManager] ERROR: ...  ← Should not appear
[AnthropicClient] ERROR: ...  ← Should not appear
```

---

## Success Criteria

Migration is successful when:

 All 4 UIs work correctly (Stock Chat, Data Agent, Triple Agent, Single Viewer)  
 SSE streaming works (messages appear incrementally)  
 File uploads work (PDFs, images)  
 Charts render (Plotly)  
 Diagrams render (Mermaid)  
 Sessions persist across restarts  
 No errors in Flask console  
 Performance is same or better  
 Database `sessions.db` created and populated  
 Only ONE Anthropic client initialized (check console)

---

## Common Issues

### Issue 1: Import Errors

**Error**: `ModuleNotFoundError: No module named 'core'`

**Fix**:
```python
# Add AI_infrastructure to path
import sys
import os
ai_infra_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'AI_infrastructure')
sys.path.insert(0, ai_infra_path)
```

### Issue 2: Session Not Found

**Error**: `Invalid session`

**Fix**: Create session first
```javascript
// Frontend: Always create session if none exists
if (!sessionId) {
    const response = await fetch('/api/session/create', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ui_context: 'stock_chat'})
    });
    const data = await response.json();
    sessionId = data.session_id;
}
```

### Issue 3: SSE Not Streaming

**Error**: Events arrive all at once instead of streaming

**Fix**: Verify `Response` has correct mimetype
```python
return Response(generate(), mimetype='text/event-stream')
```

### Issue 4: Database Locked

**Error**: `sqlite3.OperationalError: database is locked`

**Fix**: Close old connections
```python
# session_manager automatically handles this
# But if issues persist, restart Flask server
```

---

## Post-Migration Cleanup

After successful migration:

```powershell
# Optional: Remove old backup files after 1 week of stable operation
cd C:\Users\gpoli\GIT\In_House_SQL
Remove-Item -Path "G_Folder_BACKUP_*" -Recurse -Force

cd G_Folder\Quote_Calculator\AI_Quote_Agent\web_interface
Remove-Item "flask_triple_agent_app_BACKUP_*.py"
```

---

## Support

If issues occur:
1. Check Flask console for errors
2. Check browser console for errors
3. Review test results: `pytest AI_infrastructure/tests/ -v`
4. Rollback if needed (see Rollback Procedure)
5. Contact development team with error logs

---

**Migration complete!** 🎉

New architecture is now active with:
- Single session manager
- Single Anthropic client
- Persistent sessions
- Unified streaming
- Complete test coverage
