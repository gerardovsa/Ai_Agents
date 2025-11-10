# 🔌 Connecting UIs to NEW Flask App - Implementation Plan

**Date**: October 23, 2025  
**Status**: 🚧 IN PROGRESS  
**NEW Flask**: Port 5001 (`AI_infrastructure/flask_app.py`)  
**OLD Flask**: Port 5000 (`flask_triple_agent_app.py`)  

---

## 🎯 Goal

Connect existing HTML UIs to the NEW Flask app so they work seamlessly with the unified architecture.

---

## 📋 Current Status

### ✅ What's Working in NEW Flask:
- `/api/stock/chat` - Stock AI chat (POST)
- `/api/stock/chat-with-document` - Stock AI with files (POST)
- `/api/stock/stream/<session_id>` - SSE streaming (GET)
- `/api/stock/inventory` - Stock inventory (GET) - stub
- `/api/stock/usage-analytics` - Usage analytics (GET) - stub
- `/health` - Health check

### ❌ What's Missing:
- HTML template serving (no routes to serve stock_management.html, etc.)
- Many stock API endpoints (master-unified, process-invoice, list-threads, etc.)
- Agent routes (/api/agent/...)
- Static file serving

### 📁 UIs to Connect:
1. **Stock Management** - `stock_management.html` (10,000+ lines)
2. **Single Agent Viewer** - `single_agent_viewer.html`
3. **Triple Agent** - `triple_agent.html`
4. **Data Agent Chat** - `data_agent_chat.html`

---

## 🚀 Implementation Strategy

### Phase 1: Add Template Serving (15 minutes)
Add routes to NEW Flask to serve HTML templates from OLD Flask's templates folder.

### Phase 2: Test Basic Connection (10 minutes)
Verify Stock Management UI loads and can connect to NEW Flask endpoints.

### Phase 3: Add Missing Endpoints (1-2 hours)
Migrate missing API endpoints from OLD Flask to NEW Flask architecture.

### Phase 4: Test All Features (30 minutes)
Comprehensive testing of all UI features.

---

## 📝 Step-by-Step Implementation

### Step 1: Add Template Serving to NEW Flask

**File**: `AI_infrastructure/flask_app.py`

**Add after line 50 (after health check):**

```python
# ============================================================================
# TEMPLATE SERVING - Connect to existing HTML UIs
# ============================================================================

# Serve stock management UI
@app.route('/stock-management')
def serve_stock_management():
    """Serve Stock Management HTML UI"""
    template_path = Path(__file__).parent.parent / 'Quote_Calculator' / 'AI_Quote_Agent' / 'web_interface' / 'templates' / 'stock_management.html'
    return send_from_directory(template_path.parent, template_path.name)

# Serve single agent viewer
@app.route('/single-agent-viewer')
@app.route('/data-agent-chat')
def serve_single_agent_viewer():
    """Serve Single Agent Viewer HTML UI"""
    template_path = Path(__file__).parent.parent / 'Quote_Calculator' / 'AI_Quote_Agent' / 'web_interface' / 'templates' / 'single_agent_viewer.html'
    return send_from_directory(template_path.parent, template_path.name)

# Serve triple agent UI
@app.route('/triple-agent')
@app.route('/')  # Default route
def serve_triple_agent():
    """Serve Triple Agent HTML UI"""
    template_path = Path(__file__).parent.parent / 'Quote_Calculator' / 'AI_Quote_Agent' / 'web_interface' / 'templates' / 'triple_agent.html'
    return send_from_directory(template_path.parent, template_path.name)

# Serve static files (JS, CSS)
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (JS, CSS, images)"""
    static_path = Path(__file__).parent.parent / 'Quote_Calculator' / 'AI_Quote_Agent' / 'web_interface' / 'static'
    return send_from_directory(static_path, filename)
```

---

### Step 2: Add Missing Stock API Endpoints

**File**: `AI_infrastructure/routes/stock_routes.py`

**Add these endpoints (copy from OLD Flask):**

```python
@stock_bp.route('/master-unified', methods=['GET'])
def get_stock_master_unified():
    """Get unified stock master data (SQLite)"""
    # TODO: Implement - connect to stock_data.db
    pass

@stock_bp.route('/process-invoice', methods=['POST'])
def process_invoice():
    """Process invoice with Claude Vision"""
    # TODO: Implement - use ai_client with vision
    pass

@stock_bp.route('/create-session', methods=['POST'])
def create_session():
    """Create new chat session"""
    session_id = session_manager.create_session(ui_context='stock_chat')
    return jsonify({'session_id': session_id})

@stock_bp.route('/list-threads', methods=['GET'])
def list_threads():
    """List all conversation threads"""
    # TODO: Implement - query session manager
    pass

@stock_bp.route('/load-thread/<session_id>', methods=['GET'])
def load_thread(session_id):
    """Load conversation thread"""
    session = session_manager.get_session(session_id)
    if session:
        return jsonify(session)
    return jsonify({'error': 'Session not found'}), 404

@stock_bp.route('/ai-extracted-analytics', methods=['GET'])
def get_ai_extracted_analytics():
    """Get AI extracted job analytics"""
    # TODO: Implement - connect to extracted_jobs table
    pass
```

---

### Step 3: Add Agent Routes

**File**: `AI_infrastructure/routes/agent_routes.py`

**Check what's already there and add missing endpoints:**

```python
@agent_bp.route('/chat', methods=['POST'])
def agent_chat():
    """Generic agent chat endpoint"""
    # TODO: Implement
    pass

@agent_bp.route('/chat-with-document', methods=['POST'])
def agent_chat_with_document():
    """Agent chat with document uploads"""
    # TODO: Implement - similar to stock chat with documents
    pass

@agent_bp.route('/chat-with-document-stream', methods=['POST'])
def agent_chat_with_document_stream():
    """Agent chat with streaming response"""
    # TODO: Implement
    pass
```

---

## 🧪 Testing Plan

### Test 1: Health Check
```powershell
Invoke-WebRequest -Uri http://localhost:5001/health -UseBasicParsing
```

**Expected**: `{"status": "healthy", ...}`

### Test 2: Template Serving
```powershell
Invoke-WebRequest -Uri http://localhost:5001/stock-management -UseBasicParsing
```

**Expected**: HTML content loads

### Test 3: Stock Chat
```powershell
$body = @{
    prompt = "Hello, test message"
    provider = "anthropic"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:5001/api/stock/chat `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

**Expected**: `{"status": "processing", "session_id": "..."}`

### Test 4: UI in Browser
1. Open: http://localhost:5001/stock-management
2. Click "Stock AI Chat"
3. Send test message
4. Verify streaming works

---

## 📊 Migration Checklist

### Flask App Updates:
- [ ] Add template serving routes
- [ ] Add static file serving
- [ ] Update CORS settings if needed

### Stock Routes (stock_routes.py):
- [x] `/api/stock/chat` (exists)
- [x] `/api/stock/chat-with-document` (exists)
- [x] `/api/stock/stream/<session_id>` (exists)
- [ ] `/api/stock/master-unified`
- [ ] `/api/stock/process-invoice`
- [ ] `/api/stock/create-session`
- [ ] `/api/stock/list-threads`
- [ ] `/api/stock/load-thread/<session_id>`
- [ ] `/api/stock/ai-extracted-analytics`
- [ ] `/api/stock/usage-analytics` (stub exists, needs implementation)
- [ ] `/api/stock/list-tables`

### Agent Routes (agent_routes.py):
- [ ] `/api/agent/chat`
- [ ] `/api/agent/chat-with-document`
- [ ] `/api/agent/chat-with-document-stream`
- [ ] `/api/agent/<agent_id>/start`
- [ ] `/stream/<agent_id>`

### Testing:
- [ ] Stock Management UI loads
- [ ] Stock AI Chat works
- [ ] File uploads work
- [ ] Streaming works
- [ ] Session management works
- [ ] Invoice processing works

---

## 🎯 Quick Start (For Now)

### Option 1: Simple Test (No Code Changes)
Keep both Flask apps running and test side-by-side:
- OLD Flask: http://localhost:5000 (production)
- NEW Flask: http://localhost:5001 (testing health endpoint)

### Option 2: Add Template Serving Only
Just add template routes to NEW Flask, test if UIs load (endpoints will 404 but UI loads).

### Option 3: Full Migration (This Guide)
Follow all steps above to fully connect UIs to NEW Flask.

---

## 🔧 Next Steps

**Immediate** (Choose one):
1. **Quick Win**: Add template serving routes → Test UI loading
2. **Partial**: Add template serving + basic endpoints → Test Stock AI Chat
3. **Full**: Complete all steps → Full migration

**Recommended**: Start with Option 1 (Quick Win) to verify template serving works, then incrementally add endpoints.

---

## 📝 Notes

- NEW Flask runs on port 5001 (OLD Flask on 5000)
- Both can run simultaneously for safe testing
- UIs use relative paths (`/api/...`) so they'll connect to whatever port serves them
- No changes needed to HTML files (they'll automatically use NEW Flask's port when served from NEW Flask)

---

**Ready to proceed?** Let me know which option you want to start with!
