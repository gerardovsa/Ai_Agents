# 🚀 ROUTES MIGRATION QUICK START
**Get Started Today - October 23, 2025**

---

## ✅ YOUR SITUATION

**What You Have:**
- ✅ NEW Flask app ready (port 5001)
- ✅ Core AI infrastructure built
- ✅ Basic route skeletons created
- ⏳ 20+ endpoints need full implementation
- ⏳ 4 UIs need to migrate

**What You Need:**
1. Complete endpoint implementations
2. System prompts extracted
3. Tool functions organized
4. HTML templates migrated
5. JavaScript client code updated

---

## 🎯 TODAY'S ACTION ITEMS (Before End of Day)

### Task 1: Read Key Files (15 min)
These files explain how the new infrastructure works:

```bash
# Read these to understand architecture:
1. G_Folder/AI_infrastructure/core/unified_ai_client.py
   - How AI execution works
   
2. G_Folder/AI_infrastructure/core/unified_session_manager.py
   - How sessions are managed
   
3. G_Folder/AI_infrastructure/routes/agent_routes.py
   - Current skeleton implementation
```

### Task 2: Decide Testing Priority (5 min)
**Question**: Which UI should work FIRST?

**Recommendation**: Start with **Data Agent Chat** (simplest)
- ✅ Fewest endpoints (5-6 needed)
- ✅ Simpler than Stock Management
- ✅ Good proof-of-concept
- ✅ Then scale to Stock Management

**Alternative**: Start with **Stock Management** (most important)
- More complex (15+ endpoints)
- But highest business value
- Can move faster if you're motivated

**My Recommendation**: DO DATA AGENT CHAT FIRST
- 1 week to get fully working
- Then Stock Management (2 weeks)
- Then polish remaining (1 week)

### Task 3: Run Setup Check (10 min)
Verify new Flask is working:

```powershell
# Terminal 1: Start new Flask
cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure
python flask_app.py
# Should say: "Running on http://localhost:5001"

# Terminal 2: Test endpoints exist
curl http://localhost:5001/
curl http://localhost:5001/viewer
curl http://localhost:5001/chat
curl http://localhost:5001/stock
```

---

## 📊 THIS WEEK'S PLAN (5-Day Sprint)

### 🔴 DAY 1 (Monday): Foundation
**Goal**: Get system prompts organized

- [ ] Create `/core/prompts/` directory
- [ ] Copy system prompts from old Flask:
  - `get_single_agent_system_prompt()` → `single_agent_prompt.py`
  - `get_stock_ai_system_prompt()` → `stock_ai_prompt.py`
  - `get_triple_agent_system_prompt()` → `triple_agent_prompts.py`
- [ ] Create test: Can you load all prompts?

**File to Create:**
```
G_Folder/AI_infrastructure/core/prompts/
├── __init__.py
├── single_agent_prompt.py       # ~800 lines from old Flask
├── stock_ai_prompt.py           # ~1000 lines from old Flask
└── triple_agent_prompts.py      # ~400 lines from old Flask
```

**Time**: 2-3 hours

---

### 🟡 DAY 2 (Tuesday): Core Endpoints
**Goal**: Implement agent execution endpoints

- [ ] Implement `/agent/<id>/start` endpoint
- [ ] Implement `/stream/<id>` SSE streaming endpoint
- [ ] Test with Data Agent Chat UI
- [ ] Debug streaming in browser

**File to Edit:**
```
G_Folder/AI_infrastructure/routes/agent_routes.py
# Add full implementation of:
# - /start (POST)
# - /stream (GET)
```

**Time**: 3-4 hours

---

### 🟡 DAY 3 (Wednesday): Agent Management
**Goal**: Complete agent lifecycle endpoints

- [ ] Implement `/agent/<id>/status` endpoint
- [ ] Implement `/agent/<id>/history` endpoint
- [ ] Implement `/agent/<id>/clear` endpoint
- [ ] Test all 3 endpoints

**File to Edit:**
```
G_Folder/AI_infrastructure/routes/agent_routes.py
# Add:
# - /status (GET)
# - /history (GET)
# - /clear (POST)
```

**Time**: 2-3 hours

---

### 🟢 DAY 4 (Thursday): Data Agent Chat UI
**Goal**: Get Data Agent Chat working end-to-end

- [ ] Verify HTML template loads
- [ ] Update JavaScript to call new endpoints
- [ ] Test sending message → getting response
- [ ] Test conversation history
- [ ] Test save/load conversation

**Files to Update:**
```
templates/data_agent_chat.html
# Update JavaScript fetch calls:
# - /agent/1/start → new endpoint
# - /stream/1 → new endpoint
# - /api/threads/list → new endpoint (stub OK)
```

**Time**: 3-4 hours

---

### 🟢 DAY 5 (Friday): Testing & Polish
**Goal**: Get Data Agent Chat fully working

- [ ] End-to-end testing
- [ ] Fix any bugs
- [ ] Document what works
- [ ] Plan Stock Management migration

**Time**: 2-3 hours

---

## 📋 IMMEDIATE TO-DO LIST (Copy & Use)

```
PRIORITY 1 - THIS WEEK:
☐ Day 1: Create system prompts directory + copy functions
☐ Day 1: Test prompts load correctly
☐ Day 2: Implement /agent/<id>/start endpoint
☐ Day 2: Implement /stream/<id> SSE endpoint
☐ Day 3: Implement /agent/<id>/status endpoint
☐ Day 3: Implement /agent/<id>/history endpoint
☐ Day 3: Implement /agent/<id>/clear endpoint
☐ Day 4: Migrate data_agent_chat.html template
☐ Day 4: Update JavaScript client code
☐ Day 4: Test Data Agent Chat end-to-end
☐ Day 5: Fix bugs, document progress

PRIORITY 2 - NEXT WEEK:
☐ Implement Stock Management endpoints
☐ Implement Stock Chat with documents
☐ Implement stock data queries
☐ Migrate stock_management.html template

PRIORITY 3 - FOLLOWING WEEK:
☐ Implement thread management endpoints
☐ Implement export endpoints
☐ Polish UI/UX
☐ Final testing & deployment
```

---

## 🔧 CODE TEMPLATES

### Template 1: Copy System Prompt Function

From: `G_Folder/Quote_Calculator/AI_Quote_Agent/web_interface/flask_triple_agent_app.py`

**What to copy**: Lines 178-550 (get_single_agent_system_prompt function)

**Where to put it**: `G_Folder/AI_infrastructure/core/prompts/single_agent_prompt.py`

```python
# G_Folder/AI_infrastructure/core/prompts/single_agent_prompt.py

def get_single_agent_system_prompt():
    """Return system prompt for single agent mode"""
    return """
    [ENTIRE FUNCTION BODY FROM OLD FLASK]
    ...
    """

# Usage in routes:
from core.prompts.single_agent_prompt import get_single_agent_system_prompt

system_prompt = get_single_agent_system_prompt()
```

---

### Template 2: Implement /agent/<id>/start Endpoint

```python
# G_Folder/AI_infrastructure/routes/agent_routes.py

@agent_bp.route('/<agent_id>/start', methods=['POST'])
def agent_start(agent_id):
    """Start agent execution"""
    try:
        data = request.json or {}
        
        # Get or create session
        session_id = data.get('session_id')
        if not session_id:
            session_id = session_manager.create_session(ui_context='agent')
        
        # Get session & queue
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        prompt = data.get('prompt', '').strip()
        if not prompt:
            return jsonify({'error': 'Missing prompt'}), 400
        
        # Get system prompt based on context
        context = data.get('context', 'triple_agent')
        if context == 'single_agent':
            from core.prompts.single_agent_prompt import get_single_agent_system_prompt
            system_prompt = get_single_agent_system_prompt()
        else:
            from core.prompts.triple_agent_prompts import get_triple_agent_system_prompt
            system_prompt = get_triple_agent_system_prompt(agent_id)
        
        # Start agent in background thread
        def run_agent():
            try:
                result = ai_client.process_streaming(
                    session_id=session_id,
                    agent_id=agent_id,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    context=context
                )
                session['last_result'] = result
            except Exception as e:
                session['error'] = str(e)
        
        thread = threading.Thread(target=run_agent, daemon=False)
        thread.start()
        
        return jsonify({
            'session_id': session_id,
            'message_id': str(uuid.uuid4()),
            'status': 'started',
            'agent_id': agent_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

### Template 3: Implement /stream/<id> SSE Endpoint

```python
# G_Folder/AI_infrastructure/routes/agent_routes.py

@agent_bp.route('/stream/<agent_id>', methods=['GET'])
def stream(agent_id):
    """Stream agent response via SSE"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'Missing session_id'}), 400
    
    # Get queue from session manager
    queue = session_manager.get_queue(session_id)
    
    def generate():
        """Generator for SSE stream"""
        timeout_count = 0
        max_timeout = 3
        
        while True:
            try:
                # Get message from queue (blocking with timeout)
                log_entry = queue.get(timeout=30)
                timeout_count = 0  # Reset timeout counter
                
                # Send as SSE format
                yield f"data: {json.dumps(log_entry)}\n\n"
                
                # Check for completion
                if log_entry.get('type') in ['complete', 'error']:
                    break
                    
            except Empty:
                timeout_count += 1
                if timeout_count >= max_timeout:
                    yield f"data: {json.dumps({'type': 'timeout'})}\n\n"
                    break
                # Send keep-alive
                yield f": keep-alive\n\n"
    
    return Response(generate(), mimetype='text/event-stream')
```

---

### Template 4: Update JavaScript Client

```javascript
// In templates/data_agent_chat.html

// OLD (calling old Flask):
// const response = await fetch('/agent/1/start', {...})

// NEW (calling new Flask):
async function sendMessage(userInput) {
    try {
        // Step 1: Start agent execution
        const startResponse = await fetch('/agent/1/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                session_id: currentSessionId,
                prompt: userInput,
                context: 'single_agent'
            })
        });
        
        const startResult = await startResponse.json();
        currentSessionId = startResult.session_id;
        
        // Step 2: Connect to SSE stream
        connectToStream(currentSessionId, 1);
        
    } catch (error) {
        console.error('Error:', error);
    }
}

function connectToStream(sessionId, agentId) {
    const eventSource = new EventSource(`/stream/${agentId}?session_id=${sessionId}`);
    
    eventSource.onmessage = function(event) {
        const log = JSON.parse(event.data);
        
        switch(log.type) {
            case 'content_block_delta':
                addTextToChat(log.text);
                break;
            case 'tool_start':
                showToolRunning(log.tool_name);
                break;
            case 'complete':
                markChatComplete();
                eventSource.close();
                break;
            case 'error':
                showError(log.error);
                eventSource.close();
                break;
        }
    };
    
    eventSource.onerror = () => {
        console.error('Stream error');
        eventSource.close();
    };
}
```

---

## 🧪 TESTING CHECKLIST

### Test 1: Prompts Load (5 min)
```powershell
# In Python REPL or test file:
from core.prompts.single_agent_prompt import get_single_agent_system_prompt
prompt = get_single_agent_system_prompt()
print(f"Loaded {len(prompt)} character prompt")
# Should print: "Loaded 8234 character prompt"
```

### Test 2: Start Agent (10 min)
```bash
# Terminal:
curl -X POST http://localhost:5001/agent/1/start \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What are top selling products?",
    "context": "single_agent"
  }'

# Should return:
# {"session_id": "uuid", "message_id": "msg-uuid", "status": "started"}
```

### Test 3: SSE Stream (10 min)
```bash
# In another terminal, after starting agent:
curl "http://localhost:5001/stream/1?session_id=<THE_UUID_FROM_ABOVE>"

# Should stream messages like:
# data: {"type": "content_block_delta", "text": "Based"}
# data: {"type": "content_block_delta", "text": " on"}
# data: {"type": "complete", "final_response": "Full response..."}
```

### Test 4: Data Agent Chat UI (20 min)
1. Open browser: `http://localhost:5001/chat`
2. Type message: "Show me top 5 products"
3. Click Send
4. Watch for:
   - Message appears in chat
   - Agent is "thinking" indicator
   - Response streams in
   - Full message appears

---

## 🚨 COMMON ISSUES & FIXES

### Issue: "No module named core.prompts"
**Fix**: Create the file first
```bash
touch G_Folder/AI_infrastructure/core/prompts/__init__.py
```

### Issue: SSE stream not connecting
**Fix**: Check EventSource usage in JavaScript
```javascript
// ✅ CORRECT
const eventSource = new EventSource(`/stream/1?session_id=${id}`);

// ❌ WRONG - Won't work with EventSource
await fetch(`/stream/1?session_id=${id}`)
```

### Issue: "Queue.get timeout"
**Fix**: Ensure agent thread started correctly
```python
# Debug: Check if thread started
thread.start()
time.sleep(0.5)  # Give thread time to start
print(f"Thread alive: {thread.is_alive()}")
```

---

## 📞 QUESTIONS TO ANSWER

**Before you start, answer these:**

1. **Which UI first?**
   - [ ] Data Agent Chat (simpler, 5 endpoints)
   - [ ] Stock Management (complex, 15+ endpoints)
   - [ ] Single Agent Viewer (medium, 8 endpoints)

2. **How much time have you got this week?**
   - [ ] 5-10 hours (Phase 1 foundation)
   - [ ] 10-20 hours (Endpoints + UI)
   - [ ] 20+ hours (Full migration)

3. **Should I:**
   - [ ] Copy-paste old code as-is
   - [ ] Refactor while migrating
   - [ ] Mix of both

4. **Database:**
   - [ ] Keep using SQLite `stock_data.db`
   - [ ] Keep using SQL Server
   - [ ] Add PostgreSQL

---

## ✅ SUCCESS CRITERIA

**Week 1 Success**: You have...
- ✅ Data Agent Chat UI fully working
- ✅ Can send message → get response
- ✅ Can save/load conversations
- ✅ All 5 endpoints working

**Week 2 Success**: You have...
- ✅ Stock Management UI migrated
- ✅ Stock chat with documents
- ✅ All stock endpoints working
- ✅ Invoice processing integrated

**Week 3+ Success**: You have...
- ✅ All 4 UIs fully working
- ✅ All 20+ endpoints complete
- ✅ Old Flask app deprecated
- ✅ Ready for production

---

## 🎯 YOUR NEXT STEPS (Right Now!)

1. **Next 10 min**: Read this document completely
2. **Next 30 min**: Read the 2 reference documents:
   - `ROUTES_API_MIGRATION_CHECKLIST.md`
   - `ROUTES_COMPLETE_INVENTORY.md`
3. **Next 60 min**: Set up dev environment
   - Start new Flask: `python flask_app.py`
   - Test it's running: `curl http://localhost:5001/`
4. **Next 2 hours**: Start Day 1 tasks
   - Create prompts directory
   - Copy first system prompt function
   - Test it loads

**Goal**: By end of day, you should have:
- ✅ System prompts organized in new directory
- ✅ All prompts loading without errors
- ✅ Understanding of architecture
- ✅ Ready to start implementing endpoints tomorrow

---

**Document Version**: 1.0  
**Created**: October 23, 2025  
**Estimated Total Time**: 3-4 weeks for full migration

Good luck! 🚀

