# 🎯 MIGRATION REFERENCE CARD
**Quick Lookup - Print This Out!**

---

## 📍 DOCUMENT LOCATIONS

All documents in: `C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure\`

```
├── MIGRATION_DOCUMENTATION_SUMMARY.md      ← START HERE (this explains all 3)
├── MIGRATION_QUICK_START.md                ← DAILY GUIDE (your action plan)
├── ROUTES_API_MIGRATION_CHECKLIST.md       ← BIG PICTURE (overview)
└── ROUTES_COMPLETE_INVENTORY.md            ← DETAILED SPECS (reference while coding)
```

---

## 🔴 YOUR 4 UIs

### UI #1: Data Agent Chat ⭐ START HERE
- **Endpoints**: 5-7
- **Time**: 1 week
- **Difficulty**: ⭐ Easy
- **File**: `templates/data_agent_chat.html`
- **Priority**: Get working first

### UI #2: Single Agent Viewer
- **Endpoints**: 8-10
- **Time**: 1.5 weeks
- **Difficulty**: ⭐⭐ Medium
- **File**: `templates/single_agent_viewer.html`
- **Priority**: After Data Agent

### UI #3: Triple Agent
- **Endpoints**: 12-15
- **Time**: 2 weeks
- **Difficulty**: ⭐⭐⭐ Hard
- **Notes**: 3 agents running concurrently
- **Priority**: After Single Agent

### UI #4: Stock Management ⭐ MOST COMPLEX
- **Endpoints**: 15+
- **Time**: 2-3 weeks
- **Difficulty**: ⭐⭐⭐ Hard
- **File**: `templates/stock_management.html` (8,599 lines!)
- **Priority**: But highest business value

---

## 📡 YOUR 20+ ENDPOINTS (Quick Reference)

### Agent Control (5 endpoints)
```
POST   /agent/<id>/start          Start execution
GET    /stream/<id>               SSE real-time stream
GET    /agent/<id>/status         Poll status
GET    /agent/<id>/history        Get conversation
POST   /agent/<id>/clear          Clear history
```

### Stock Chat (2 endpoints)
```
POST   /api/stock/chat-with-document    Upload PDF + chat
POST   /api/stock/chat-message          Send text message
```

### Stock Data (3 endpoints)
```
GET    /api/stock/master               Get stock list
GET    /api/stock/master-unified       Get with analytics
GET    /api/stock/ai-extracted-analytics  Get usage data
```

### Stock Invoice (3 endpoints)
```
POST   /api/stock/process-invoice      Extract invoice
POST   /api/stock/import-invoice       Import to database
POST   /api/stock/approve-items        Approve items
```

### Thread Management (6 endpoints)
```
GET    /api/threads/list               List conversations
POST   /api/threads/save               Save conversation
GET    /api/threads/load/<file>        Load conversation
DELETE /api/threads/delete/<file>      Delete conversation
GET    /api/threads/search             Search threads
GET    /api/threads/stats              Get stats
```

### Session Management (2 endpoints)
```
POST   /api/sessions/mark-read/<id>    Mark read
POST   /api/threads/autosave           Setup autosave
```

### Export (3 endpoints)
```
POST   /api/export/session/<id>        Export session
POST   /api/export/query/<name>        Export query results
GET    /api/export/queries/list        List exports
```

---

## 🛠️ KEY FILES TO MODIFY

### This Week
```
G_Folder/AI_infrastructure/routes/agent_routes.py
  → Add implementations for /agent/<id>/start, /stream/<id>

G_Folder/AI_infrastructure/core/prompts/ [NEW DIRECTORY]
  → Create and add system prompts
  → single_agent_prompt.py
  → stock_ai_prompt.py
  → triple_agent_prompts.py
```

### Next Weeks
```
G_Folder/AI_infrastructure/routes/stock_routes.py
  → Add /api/stock/* endpoints

G_Folder/AI_infrastructure/routes/thread_routes.py
  → Add /api/threads/* endpoints

G_Folder/AI_infrastructure/routes/export_routes.py
  → Add /api/export/* endpoints

G_Folder/AI_infrastructure/core/tools/ [NEW DIRECTORY]
  → agent_tools.py
  → stock_tools.py
  → export_tools.py
```

---

## 💻 COMMAND REFERENCE

### Start New Flask
```powershell
cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure
python flask_app.py
# Opens on http://localhost:5001
```

### Test Endpoints
```bash
# Test /agent/<id>/start
curl -X POST http://localhost:5001/agent/1/start \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello","context":"single_agent"}'

# Test /stream/<id>
curl "http://localhost:5001/stream/1?session_id=<UUID_FROM_ABOVE>"
```

### Copy System Prompt
```bash
# From old Flask (lines to copy):
# file: G_Folder/Quote_Calculator/AI_Quote_Agent/web_interface/flask_triple_agent_app.py
# get_single_agent_system_prompt()    → lines 178-550
# get_stock_ai_system_prompt()        → lines 551-1580
# get_triple_agent_system_prompt()    → lines 1192-1236
```

---

## 📋 THIS WEEK'S SPRINT (5 Days)

```
Monday (Day 1):
  [ ] Create /core/prompts/ directory
  [ ] Copy system prompts from old Flask
  [ ] Test prompts load

Tuesday (Day 2):
  [ ] Implement /agent/<id>/start endpoint
  [ ] Implement /stream/<id> SSE endpoint
  [ ] Test with curl

Wednesday (Day 3):
  [ ] Implement /agent/<id>/status endpoint
  [ ] Implement /agent/<id>/history endpoint
  [ ] Implement /agent/<id>/clear endpoint

Thursday (Day 4):
  [ ] Migrate data_agent_chat.html template
  [ ] Update JavaScript fetch calls
  [ ] Test end-to-end

Friday (Day 5):
  [ ] Bug fixes
  [ ] Documentation
  [ ] Plan next week
```

---

## 🎯 SUCCESS CHECKPOINTS

### By End of Day 1
- ✅ System prompts copied
- ✅ /core/prompts/ working
- ✅ All prompts load without errors

### By End of Day 2
- ✅ /agent/<id>/start working
- ✅ /stream/<id> streaming
- ✅ Can see real-time updates

### By End of Day 3
- ✅ All 5 agent endpoints working
- ✅ Status, history, clear all functional

### By End of Day 4
- ✅ Data Agent Chat UI loads
- ✅ Can send message
- ✅ Can receive response
- ✅ Can save conversation

### By End of Week
- ✅ Data Agent Chat FULLY WORKING
- ✅ All 7 endpoints functional
- ✅ Ready to move to Stock Management

---

## ⚡ COMMON TASKS

### Copy Function from Old Flask
```python
# OLD: G_Folder/Quote_Calculator/AI_Quote_Agent/web_interface/flask_triple_agent_app.py
def get_single_agent_system_prompt():
    return """..."""

# NEW: G_Folder/AI_infrastructure/core/prompts/single_agent_prompt.py
def get_single_agent_system_prompt():
    return """..."""

# IMPORT in routes:
from core.prompts.single_agent_prompt import get_single_agent_system_prompt
```

### Create SSE Response
```python
@app.route('/stream/<agent_id>')
def stream(agent_id):
    queue = session_manager.get_queue(session_id)
    
    def generate():
        while True:
            try:
                msg = queue.get(timeout=30)
                yield f"data: {json.dumps(msg)}\n\n"
                if msg.get('type') in ['complete', 'error']:
                    break
            except Empty:
                break
    
    return Response(generate(), mimetype='text/event-stream')
```

### Connect to SSE in JavaScript
```javascript
const eventSource = new EventSource(`/stream/1?session_id=${sessionId}`);

eventSource.onmessage = (event) => {
    const log = JSON.parse(event.data);
    // Handle message
};

eventSource.onerror = () => eventSource.close();
```

---

## 🚨 GOTCHAS & FIXES

| Problem | Cause | Fix |
|---------|-------|-----|
| Module not found | Directory missing | Create `__init__.py` in directory |
| SSE not streaming | Using fetch instead of EventSource | Use `new EventSource()` |
| Queue timeout | Thread not running | Check `thread.is_alive()` |
| Prompts missing | Wrong import path | Use `from core.prompts.xyz import ...` |
| No session | Session not created | Call `session_manager.create_session()` |
| Stream hangs | Message not ending stream | Send `{'type': 'complete'}` |

---

## 📞 KEY NUMBERS

| Metric | Value |
|--------|-------|
| Total endpoints | 20+ |
| UI templates | 4 |
| System prompts | 3 |
| Estimated total time | 80-120 hours |
| Working weeks | 3-4 weeks |
| Daily sprint (Day 1-5) | 2-3 hours/day |
| Longest endpoint | `/api/stock/master` (complex query) |
| Most complex UI | Stock Management (8,599 lines) |
| Easiest starting point | Data Agent Chat |
| Success rate | High (clear specs provided) |

---

## 📚 DOCUMENT QUICK LINKS

**Print/Bookmark These:**

1. **MIGRATION_QUICK_START.md**
   - Your daily reference
   - Check this every morning
   - Has code templates to copy-paste

2. **ROUTES_COMPLETE_INVENTORY.md**
   - While coding each endpoint
   - Has request/response examples
   - Has implementation code

3. **ROUTES_API_MIGRATION_CHECKLIST.md**
   - Check off as you go
   - Understand architecture
   - See dependencies

4. **MIGRATION_DOCUMENTATION_SUMMARY.md** (this one)
   - Quick reference
   - Print it out
   - Keep by your desk

---

## ✅ READY TO START?

### Checklist Before You Begin
- [ ] Read MIGRATION_QUICK_START.md (20 min)
- [ ] Decide: Which UI first? (Data Agent Chat recommended)
- [ ] New Flask running? (port 5001)
- [ ] Can you access http://localhost:5001/ ?
- [ ] Know which system prompt to copy first?
- [ ] Have 2-3 hours free for Day 1?

### First Action
```
1. Open MIGRATION_QUICK_START.md
2. Follow "TODAY'S ACTION ITEMS" section
3. Complete Task 1 (15 min) - Read files
4. Complete Task 2 (5 min) - Decide priority
5. Complete Task 3 (10 min) - Verify Flask running
6. Start Day 1 tasks
```

---

**This Card**: Reference v1.0  
**Created**: October 23, 2025  
**Print & Keep Handy!**

