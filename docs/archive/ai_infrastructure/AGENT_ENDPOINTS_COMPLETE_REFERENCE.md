# 📋 Complete Agent Endpoints Reference

**Date**: October 23, 2025  
**Source**: OLD Flask (`flask_triple_agent_app.py`)  
**Purpose**: Map all agent-related endpoints for migration to NEW Flask  

---

## 🎯 Overview

The OLD Flask app has **3 categories** of agent endpoints:

1. **🎨 UI Routes** - Serve HTML pages (6 routes)
2. **🤖 AI Backend API** - Process AI requests (8 routes)
3. **📊 Data Management API** - History, status, export (4 routes)

**Total**: 18 agent-related endpoints

---

## 📁 Category 1: UI Routes (HTML Pages)

These endpoints **serve HTML templates** for different AI interfaces.

### 1. `/chat` (GET)
**Purpose**: Serve Data Agent Chat UI  
**Template**: `data_agent_chat.html`  
**Description**: Single-column transparent chat interface for database queries  
**Used By**: Data Agent Chat page  
**Line**: 1363

```python
@app.route('/chat')
def data_agent_chat():
    """Serve the clean Data Agent chat (single column, transparent background)"""
    return render_template('data_agent_chat.html')
```

**Status in NEW Flask**: ❌ Missing  
**Priority**: HIGH (UI won't load without this)

---

### 2. `/` (GET) - Default Home
**Purpose**: Serve Triple Agent UI (3 parallel agents)  
**Template**: `triple_agent.html`  
**Description**: Main interface with 3 AI agents running in parallel  
**Used By**: Triple Agent page (home page)  
**Line**: ~100

**Status in NEW Flask**: ✅ Added (in flask_app.py as `/triple-agent` and `/`)  
**Priority**: DONE

---

### 3. `/stock` (GET)
**Purpose**: Serve Stock Management UI  
**Template**: `stock_management.html`  
**Description**: Stock inventory + AI chat interface  
**Used By**: Stock Management page  
**Line**: 1369

```python
@app.route('/stock')
def stock_management():
    """Serve the stock management page"""
    return render_template('stock_management.html')
```

**Status in NEW Flask**: ✅ Added (in flask_app.py as `/stock-management`)  
**Priority**: DONE

---

### 4. `/single-agent-viewer` (GET) - IMPLIED
**Purpose**: Serve Single Agent Viewer UI  
**Template**: `single_agent_viewer.html`  
**Description**: Single AI agent with database tools  
**Used By**: Single Agent Viewer page  

**Status in NEW Flask**: ✅ Added (in flask_app.py)  
**Priority**: DONE

---

## ⚠️ IMPORTANT: Stock AI Chat Endpoint REMOVED

**Date**: October 23, 2025  
**Deleted**: `/api/stock/chat-with-document-stream` (POST)  
**Reason**: Redundant with `/agent/<id>/start` which already supports files  

**Stock AI Chat now uses**:
- `/agent/stock_ai/start` (POST) - Start with files/text
- `/stream/stock_ai` (GET) - Stream results via SSE

**Do NOT migrate Stock AI Chat-specific code to NEW Flask!**

---

## 📁 Category 2: AI Backend API (Core Processing)

These endpoints **process AI requests** and return results via SSE streaming.

### 5. `/agent/<agent_id>/start` (POST)
**Purpose**: Start an AI agent conversation  
**Used By**: Triple Agent UI (all 3 agents)  
**Line**: 1375

**What it does**:
1. Receives user prompt (text + optional file uploads)
2. Creates isolated thread for agent processing
3. Initializes agent state (conversation history, queue, locks)
4. Launches background worker thread with ToolUseAgent
5. Returns `{"status": "started", "session_id": "..."}`

**Request**:
```json
POST /agent/1/start
Content-Type: application/json OR multipart/form-data

// JSON (text-only):
{
  "prompt": "Calculate cost of 1000 business cards",
  "context": "triple_agent"
}

// FormData (with files):
{
  "prompt": "Analyze this invoice",
  "files": [file1.pdf, file2.jpg],
  "context": "triple_agent"
}
```

**Response**:
```json
{
  "status": "started",
  "agent_id": "1",
  "agent_name": "Data Navigator",
  "session_id": "uuid-here"
}
```

**Features**:
- ✅ Thread-safe execution locks (prevents race conditions)
- ✅ Isolated queues per agent (no cross-talk)
- ✅ File upload support (PDFs, images)
- ✅ Context switching (triple_agent vs single_viewer)
- ✅ Conversation history tracking

**Status in NEW Flask**: ❌ Missing  
**Priority**: **HIGH** (Triple Agent won't work without this)

---

### 6. `/stream/<agent_id>` (GET)
**Purpose**: Server-Sent Events (SSE) stream for real-time agent responses  
**Used By**: Triple Agent UI (all 3 agents)  
**Line**: 1516

**What it does**:
1. Opens persistent SSE connection
2. Reads from agent's isolated queue
3. Streams log entries, thinking blocks, tool use, responses
4. Sends keepalive every 30s to prevent timeout
5. Closes when agent completes or errors

**Request**:
```
GET /stream/1
Accept: text/event-stream
```

**Response Stream**:
```
data: {"type": "connected", "agent_id": "1", "session_id": "..."}

data: {"type": "thinking", "content": "I need to calculate..."}

data: {"type": "tool_use", "tool": "calculate_business_cards", "params": {...}}

data: {"type": "response", "content": "The cost is $145.00"}

data: {"type": "complete"}

: keepalive (every 30s)
```

**Features**:
- ✅ Isolated per agent (no cross-contamination)
- ✅ JSON-safe serialization (handles Decimal, datetime)
- ✅ Keepalive prevents connection drops
- ✅ Automatic cleanup on complete/error

**Status in NEW Flask**: ⚠️ Partial (basic stream exists in agent_routes.py)  
**Priority**: **HIGH** (Need full ToolUseAgent integration)

---

### 7. `/api/agent/chat-with-document-stream` (POST)
**Purpose**: Agent chat with file uploads + SSE streaming  
**Used By**: Single Agent Viewer (document analysis)  
**Line**: 3115

**What it does**:
1. Accepts file uploads (PDFs, images)
2. Encodes files to base64 content blocks
3. Sends to Claude Vision API via ToolUseAgent
4. Streams response via SSE
5. Persists conversation to database

**Request**:
```
POST /api/agent/chat-with-document-stream
Content-Type: multipart/form-data

message: "What's the total on this invoice?"
files: [invoice.pdf]
session_id: "uuid" (optional)
agent_id: "1" (optional)
```

**Response Stream**:
```
data: {"type": "start", "session_id": "...", "files": 1}

data: {"type": "thinking", "content": "Analyzing invoice..."}

data: {"type": "response", "content": "Total: $2,847.50"}

data: {"type": "complete", "result": "..."}
```

**Features**:
- ✅ Multi-file support (PDFs + images)
- ✅ Claude Vision API integration
- ✅ SSE streaming
- ✅ Database persistence
- ✅ Session management

**Status in NEW Flask**: ❌ Missing  
**Priority**: **HIGH** (Single Agent Viewer needs this)

---

## 📁 Category 3: Data Management API (Status & History)

These endpoints **manage agent state** (history, status, export).

### 8. `/agent/<agent_id>/status` (GET)
**Purpose**: Get current agent status  
**Used By**: Triple Agent UI (status indicators)  
**Line**: 1606

**What it does**:
- Returns agent name, status (idle/running), conversation length

**Request**:
```
GET /agent/1/status
```

**Response**:
```json
{
  "agent_id": "1",
  "name": "Data Navigator",
  "status": "idle",
  "conversation_length": 5,
  "session_id": "uuid"
}
```

**Status in NEW Flask**: ❌ Missing  
**Priority**: MEDIUM (UI works without but shows no status)

---

### 9. `/agent/<agent_id>/history` (GET)
**Purpose**: Get conversation history for agent  
**Used By**: Triple Agent UI (load previous conversations)  
**Line**: 1622

**What it does**:
- Returns full conversation array with timestamps

**Request**:
```
GET /agent/1/history
```

**Response**:
```json
{
  "agent_id": "1",
  "conversation": [
    {"role": "user", "content": "Hello", "timestamp": "2025-10-23T..."},
    {"role": "assistant", "content": "Hi!", "timestamp": "2025-10-23T..."}
  ],
  "session_id": "uuid"
}
```

**Status in NEW Flask**: ❌ Missing  
**Priority**: MEDIUM (conversations won't persist)

---

### 10. `/agent/<agent_id>/clear` (POST)
**Purpose**: Clear conversation history  
**Used By**: Triple Agent UI (reset button)  
**Line**: 1636

**What it does**:
- Clears conversation array
- Only works if agent is idle (not running)

**Request**:
```
POST /agent/1/clear
```

**Response**:
```json
{
  "status": "cleared",
  "session_id": "uuid"
}
```

**Status in NEW Flask**: ❌ Missing  
**Priority**: LOW (nice to have)

---

### 11. `/api/export/session/<agent_id>` (POST)
**Purpose**: Export agent session data for analysis  
**Used By**: Triple Agent UI (export button)  
**Line**: 2158

**What it does**:
- Captures messages, queries, results
- Returns structure for client-side export

**Request**:
```
POST /api/export/session/1
```

**Response**:
```json
{
  "success": true,
  "session_id": "uuid",
  "message": "Export endpoint ready"
}
```

**Status in NEW Flask**: ❌ Missing  
**Priority**: LOW (not essential)

---

## 📊 Summary Table

| # | Endpoint | Method | Category | Purpose | Used By | Priority | Status |
|---|----------|--------|----------|---------|---------|----------|--------|
| 1 | `/chat` | GET | UI | Serve Data Agent UI | Data Agent Chat | HIGH | ❌ Missing |
| 2 | `/` | GET | UI | Serve Triple Agent UI | Triple Agent | HIGH | ✅ Done |
| 3 | `/stock` | GET | UI | Serve Stock UI | Stock Management | HIGH | ✅ Done |
| 4 | `/single-agent-viewer` | GET | UI | Serve Single Viewer | Single Agent | HIGH | ✅ Done |
| 5 | `/agent/<id>/start` | POST | AI | Start agent processing | Triple Agent | **HIGH** | ❌ Missing |
| 6 | `/stream/<id>` | GET | AI | SSE streaming | Triple Agent | **HIGH** | ⚠️ Partial |
| 7 | `/api/agent/chat-with-document-stream` | POST | AI | Document chat + SSE | Single Agent | MEDIUM | ❌ Missing |
| 8 | `/agent/<id>/status` | GET | Data | Get agent status | Triple Agent | MEDIUM | ❌ Missing |
| 9 | `/agent/<id>/history` | GET | Data | Get conversation | Triple Agent | MEDIUM | ❌ Missing |
| 10 | `/agent/<id>/clear` | POST | Data | Clear conversation | Triple Agent | LOW | ❌ Missing |
| 11 | `/api/export/session/<id>` | POST | Data | Export session | Triple Agent | LOW | ❌ Missing |

**DELETED from OLD Flask (October 23, 2025)**:
- `/api/stock/chat-with-document-stream` (POST) - Redundant, removed
- Stock AI Chat now uses standard `/agent/stock_ai/start` + `/stream/stock_ai`

---

## 🎯 Migration Priority

### **CRITICAL (UI won't work without these)**:
1. `/agent/<agent_id>/start` (POST) - Start agent conversations
2. `/stream/<agent_id>` (GET) - SSE streaming (upgrade existing)
3. `/api/agent/chat-with-document-stream` (POST) - File uploads
4. `/chat` (GET) - Serve Data Agent UI

### **HIGH (Essential features)**:
5. `/agent/<agent_id>/history` (GET) - Load conversations
6. `/agent/<agent_id>/status` (GET) - Status indicators

### **MEDIUM (Nice to have)**:
7. `/agent/<agent_id>/clear` (POST) - Reset conversations
8. `/api/export/session/<agent_id>` (POST) - Export functionality

---

## 🔑 Key Concepts

### UI Routes vs API Routes:
- **UI Routes** (`/chat`, `/stock`, `/`) → Serve HTML pages
- **API Routes** (`/agent/*/start`, `/stream/*`) → Process AI requests

### Agent Architecture:
```
Triple Agent (3 parallel agents)
├── Agent 1 (Data Navigator)
│   ├── Own thread
│   ├── Own queue (isolated)
│   ├── Own ToolUseAgent instance
│   └── Own conversation history
├── Agent 2 (Query Expert)
│   └── ... (same isolation)
└── Agent 3 (Calculator)
    └── ... (same isolation)
```

### Session Management:
- Each agent has a **session_id** (persists across requests)
- Session stores: conversation history, status, queue, locks
- Sessions are **isolated** (Agent 1's session ≠ Agent 2's session)

### SSE Streaming:
- **Client connects** → `/stream/1`
- **Server sends events** → `data: {...}\n\n`
- **Types**: thinking, tool_use, response, complete, error
- **Keepalive**: `: keepalive\n\n` every 30s

---

## 💡 Next Steps

**To migrate agents to NEW Flask**:

1. **Copy UI routes** (5 minutes)
   - Add `/chat` route to flask_app.py

2. **Implement core AI endpoints** (2 hours)
   - `/agent/<id>/start` - Adapt to unified_ai_client
   - `/stream/<id>` - Upgrade existing
   - `/api/agent/chat-with-document-stream` - Add Vision support

3. **Add data management** (30 minutes)
   - `/agent/<id>/status` - Use session_manager
   - `/agent/<id>/history` - Use session_manager
   - `/agent/<id>/clear` - Simple clear function

4. **Test each UI** (30 minutes)
   - Triple Agent
   - Single Agent Viewer
   - Data Agent Chat

---

**Total Endpoints**: 11 (4 UI routes + 3 core AI + 4 data management)  
**Estimated Migration Time**: 3 hours  
**Critical Path**: Routes 1, 5, 6, 7 (UI + core AI)

---

**Ready to migrate?** Start with the CRITICAL routes (#1, #5, #6, #7) to get all UIs functional!
