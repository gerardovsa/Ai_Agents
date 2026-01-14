# 📡 COMPLETE ROUTES INVENTORY
**All 20+ Endpoints Detailed Specifications**
**October 23, 2025**

---

## 📊 ENDPOINT OVERVIEW TABLE

| Category | Route | Method | Status | Priority | UI Dependency |
|----------|-------|--------|--------|----------|------------------|
| **UI Templates** | `/` | GET | ✅ DONE | ⭐ | All |
| | `/viewer` | GET | ✅ DONE | ⭐ | Single Agent, Triple Agent |
| | `/chat` | GET | ✅ DONE | ⭐ | Data Agent Chat |
| | `/stock` | GET | ✅ DONE | ⭐⭐⭐ | Stock Management |
| **Agent Execution** | `/agent/<id>/start` | POST | ⏳ TODO | ⭐⭐⭐ | All Agents |
| | `/stream/<id>` | GET | ⏳ TODO | ⭐⭐⭐ | All Agents (SSE) |
| | `/agent/<id>/status` | GET | ⏳ TODO | ⭐⭐ | Single Agent, Triple |
| | `/agent/<id>/history` | GET | ⏳ TODO | ⭐⭐ | Single Agent, Triple |
| | `/agent/<id>/clear` | POST | ⏳ TODO | ⭐⭐ | Single Agent, Triple |
| **Stock Chat** | `/api/stock/chat-with-document` | POST | ⏳ TODO | ⭐⭐⭐ | Stock Management |
| | `/api/stock/chat-message` | POST | ⏳ TODO | ⭐⭐⭐ | Stock Management |
| **Stock Data** | `/api/stock/master` | GET | ⏳ TODO | ⭐⭐⭐ | Stock Management |
| | `/api/stock/master-unified` | GET | ⏳ TODO | ⭐⭐⭐ | Stock Management |
| | `/api/stock/ai-extracted-analytics` | GET | ⏳ TODO | ⭐⭐ | Stock Management |
| **Stock Invoice** | `/api/stock/process-invoice` | POST | ⏳ TODO | ⭐⭐ | Stock Management |
| | `/api/stock/import-invoice` | POST | ⏳ TODO | ⭐⭐ | Stock Management |
| | `/api/stock/approve-items` | POST | ⏳ TODO | ⭐⭐ | Stock Management |
| **Threads** | `/api/threads/list` | GET | ⏳ TODO | ⭐⭐ | Data Agent Chat |
| | `/api/threads/save` | POST | ⏳ TODO | ⭐⭐ | Data Agent Chat |
| | `/api/threads/load/<filename>` | GET | ⏳ TODO | ⭐⭐ | Data Agent Chat |
| | `/api/threads/delete/<filename>` | DELETE | ⏳ TODO | ⭐⭐ | Data Agent Chat |
| | `/api/threads/search` | GET | ⏳ TODO | ⭐ | Data Agent Chat |
| | `/api/threads/stats` | GET | ⏳ TODO | ⭐ | Data Agent Chat |
| **Sessions** | `/api/sessions/mark-read/<id>` | POST | ⏳ TODO | ⭐ | Data Agent Chat |
| | `/api/threads/autosave` | POST | ⏳ TODO | ⭐ | Data Agent Chat |
| **Export** | `/api/export/session/<id>` | POST | ⏳ TODO | ⭐⭐ | Data Agent Chat |
| | `/api/export/query/<name>` | POST | ⏳ TODO | ⭐⭐ | Data Agent Chat |
| | `/api/export/queries/list` | GET | ⏳ TODO | ⭐ | Data Agent Chat |

---

## 🔍 DETAILED ENDPOINT SPECIFICATIONS

### 🏠 UI TEMPLATES (Template Serving)

---

#### ✅ GET `/`
**Purpose**: Serve index/home page  
**Status**: DONE in new Flask  
**Return**: HTML template

```python
# Location: flask_app.py
@app.route('/')
def index():
    return render_template('index.html')
```

---

#### ✅ GET `/viewer`
**Purpose**: Serve Single Agent Viewer + Triple Agent interface  
**Status**: DONE in new Flask  
**HTML File**: `templates/single_agent_viewer.html` (8,599 lines)  
**Return**: HTML template

```python
# Location: flask_app.py
@app.route('/viewer')
def viewer():
    return render_template('single_agent_viewer.html')
```

---

#### ✅ GET `/chat`
**Purpose**: Serve Data Agent Chat interface  
**Status**: DONE in new Flask  
**HTML File**: `templates/data_agent_chat.html`  
**Return**: HTML template

```python
# Location: flask_app.py
@app.route('/chat')
def chat():
    return render_template('data_agent_chat.html')
```

---

#### ✅ GET `/stock`
**Purpose**: Serve Stock Management interface  
**Status**: DONE in new Flask  
**HTML File**: `templates/stock_management.html` (8,599 lines)  
**Return**: HTML template

```python
# Location: flask_app.py
@app.route('/stock')
def stock_management():
    return render_template('stock_management.html')
```

---

### 🤖 AGENT EXECUTION CORE (Agent Control)

---

#### ⏳ POST `/agent/<agent_id>/start`
**Purpose**: Start agent execution with user prompt  
**Status**: SKELETON EXISTS in agent_routes.py (needs implementation)  
**Priority**: ⭐⭐⭐ CRITICAL

**Request:**
```json
{
    "session_id": "uuid-string",        // Optional - creates new if missing
    "prompt": "User message",            // Required
    "context": "triple_agent|single_agent",  // Optional, default: triple_agent
    "provider": "anthropic|openai|deepseek" // Optional, default: anthropic
}
```

**Response Success:**
```json
{
    "session_id": "uuid-string",
    "message_id": "msg-uuid",
    "status": "started",
    "agent_name": "Agent 1"
}
```

**Response Error:**
```json
{
    "error": "Missing required prompt",
    "status": 400
}
```

**Backend Implementation:**
```python
@agent_bp.route('/start', methods=['POST'])
def agent_start():
    data = request.json
    
    # Get or create session
    session_id = session_manager.get_or_create_session(data.get('session_id'))
    
    # Start agent execution in background thread
    thread = threading.Thread(
        target=run_agent_worker,
        args=(
            data['agent_id'],
            session_id,
            data['prompt'],
            data.get('context', 'triple_agent')
        ),
        daemon=False
    )
    thread.start()
    
    return jsonify({
        'session_id': session_id,
        'message_id': str(uuid.uuid4()),
        'status': 'started'
    })
```

**JavaScript (Client Side):**
```javascript
// From: data_agent_chat.html or single_agent_viewer.html
const response = await fetch('/agent/1/start', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        session_id: currentSessionId,
        prompt: userInput,
        context: 'single_agent'
    })
});
const result = await response.json();
sessionId = result.session_id;  // Save for streaming
```

---

#### ⏳ GET `/stream/<agent_id>`
**Purpose**: Server-Sent Events (SSE) stream for real-time agent response  
**Status**: SKELETON EXISTS (needs implementation)  
**Priority**: ⭐⭐⭐ CRITICAL

**Request Query Params:**
```
GET /stream/1?session_id=uuid-string
```

**Response Type**: `text/event-stream` (not JSON)

**SSE Message Format:**
Each message is a JSON object prefixed with `data:`:

```
data: {"type": "message_start", "message_id": "msg-1", "model": "claude-sonnet-4"}
data: {"type": "content_block_delta", "delta_type": "text_delta", "text": "Hello"}
data: {"type": "content_block_delta", "delta_type": "text_delta", "text": ", world!"}
data: {"type": "tool_start", "tool_name": "query_database", "tool_input": "SELECT ..."}
data: {"type": "tool_result", "tool_name": "query_database", "result": "[{...}]"}
data: {"type": "message_stop", "stop_reason": "end_turn"}
data: {"type": "complete", "final_response": "Full final message text"}
```

**Backend Implementation:**
```python
@app.route('/stream/<agent_id>')
def stream(agent_id):
    session_id = request.args.get('session_id')
    state = get_or_create_agent_state(agent_id, session_id)
    queue = state['queue']
    
    def generate():
        timeout_seconds = 30
        while True:
            try:
                log_entry = queue.get(timeout=timeout_seconds)
                
                # Convert to SSE format
                yield f"data: {json.dumps(log_entry)}\n\n"
                
                # Check for completion
                if log_entry.get('type') in ['complete', 'error']:
                    break
            except Empty:
                yield f"data: {json.dumps({'type': 'timeout'})}\n\n"
                break
    
    return Response(generate(), mimetype='text/event-stream')
```

**JavaScript (Client Side - Stock Management):**
```javascript
function connectToStream(sessionId, agentId) {
    const eventSource = new EventSource(`/stream/${agentId}?session_id=${sessionId}`);
    
    eventSource.onmessage = function(event) {
        const log = JSON.parse(event.data);
        
        if (log.type === 'content_block_delta') {
            // Add text to chat
            updateMessageText(log.text);
        } else if (log.type === 'tool_start') {
            // Show tool is running
            showToolIndicator(log.tool_name);
        } else if (log.type === 'tool_result') {
            // Show tool result
            displayToolResult(log.tool_name, log.result);
        } else if (log.type === 'complete') {
            // Mark as complete
            markMessageComplete();
            eventSource.close();
        }
    };
    
    eventSource.onerror = () => eventSource.close();
}
```

---

#### ⏳ GET `/agent/<agent_id>/status`
**Purpose**: Poll current agent status  
**Status**: SKELETON EXISTS  
**Priority**: ⭐⭐ HIGH

**Request Query Params:**
```
GET /agent/1/status?session_id=uuid-string
```

**Response:**
```json
{
    "agent_id": "1",
    "session_id": "uuid-string",
    "status": "running|idle|error",
    "is_running": true,
    "current_tool": "query_database",
    "message_count": 12,
    "queue_size": 3,
    "last_update": "2025-10-23T14:30:45Z",
    "current_message_id": "msg-12"
}
```

**Implementation:**
```python
@agent_bp.route('/<agent_id>/status', methods=['GET'])
def get_status(agent_id):
    session_id = request.args.get('session_id')
    state = get_or_create_agent_state(agent_id, session_id)
    
    return jsonify({
        'agent_id': agent_id,
        'session_id': session_id,
        'status': 'running' if state['is_running'] else 'idle',
        'is_running': state['is_running'],
        'queue_size': state['queue'].qsize(),
        'current_tool': state.get('current_tool'),
        'message_count': len(state['conversation'])
    })
```

---

#### ⏳ GET `/agent/<agent_id>/history`
**Purpose**: Get full conversation history for an agent session  
**Status**: SKELETON EXISTS  
**Priority**: ⭐⭐ HIGH

**Request Query Params:**
```
GET /agent/1/history?session_id=uuid-string&limit=50&offset=0
```

**Response:**
```json
{
    "session_id": "uuid-string",
    "agent_id": "1",
    "total_messages": 156,
    "messages": [
        {
            "role": "user",
            "content": "What are the top selling products?",
            "timestamp": "2025-10-23T14:00:00Z",
            "message_id": "msg-1"
        },
        {
            "role": "assistant",
            "content": "Based on recent data...",
            "timestamp": "2025-10-23T14:00:05Z",
            "message_id": "msg-2",
            "tool_calls": [
                {
                    "tool_name": "query_database",
                    "tool_input": {"query": "SELECT TOP 10..."},
                    "tool_result": "[...]"
                }
            ]
        }
    ]
}
```

**Implementation:**
```python
@agent_bp.route('/<agent_id>/history', methods=['GET'])
def get_history(agent_id):
    session_id = request.args.get('session_id')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    state = get_or_create_agent_state(agent_id, session_id)
    conversation = state['conversation']
    
    return jsonify({
        'session_id': session_id,
        'agent_id': agent_id,
        'total_messages': len(conversation),
        'messages': conversation[offset:offset+limit]
    })
```

---

#### ⏳ POST `/agent/<agent_id>/clear`
**Purpose**: Clear conversation history for an agent session  
**Status**: SKELETON EXISTS  
**Priority**: ⭐⭐ HIGH

**Request:**
```json
{
    "session_id": "uuid-string"
}
```

**Response:**
```json
{
    "status": "cleared",
    "session_id": "uuid-string",
    "messages_deleted": 156
}
```

**Implementation:**
```python
@agent_bp.route('/<agent_id>/clear', methods=['POST'])
def clear_history(agent_id):
    data = request.json or {}
    session_id = data.get('session_id')
    
    state = get_or_create_agent_state(agent_id, session_id)
    msg_count = len(state['conversation'])
    
    state['conversation'] = []
    state['queue'] = Queue()
    
    return jsonify({
        'status': 'cleared',
        'session_id': session_id,
        'messages_deleted': msg_count
    })
```

---

### 📊 STOCK CHAT & DOCUMENTS

---

#### ⏳ POST `/api/stock/chat-with-document`
**Purpose**: Upload PDF/image + send message to stock AI  
**Status**: NOT DONE  
**Priority**: ⭐⭐⭐ CRITICAL

**Used By**: Stock Management UI (document attachment feature)

**Request:**
```
POST /api/stock/chat-with-document

Headers:
Content-Type: multipart/form-data

Body:
{
    "session_id": "uuid-string" (optional),
    "prompt": "What's the total cost?",
    "files": [File, File, ...]  // PDF/JPG/PNG
    "supplier_hint": "Spicers" (optional)
}
```

**Response:**
```json
{
    "session_id": "uuid-string",
    "message_id": "msg-1",
    "files_processed": 3,
    "analysis": "Based on the invoices...",
    "extracted_data": {
        "invoices": [
            {
                "supplier": "Spicers Paper",
                "total": "$2,847.50",
                "items": [
                    {"description": "Satin 350gsm", "qty": 5000, "price": "$145"}
                ]
            }
        ]
    },
    "suggestions": [
        "Update Stock #44 price to $145",
        "Consider supplier negotiation..."
    ]
}
```

**Backend Implementation:**
```python
@stock_bp.route('/chat-with-document', methods=['POST'])
def chat_with_document():
    from tools.invoice_processor import InvoiceProcessor
    
    session_id = request.form.get('session_id')
    if not session_id:
        session_id = session_manager.create_session(ui_context='stock_chat_document')
    
    prompt = request.form.get('prompt', '')
    files = request.files.getlist('files')
    supplier_hint = request.form.get('supplier_hint', '')
    
    # Validate files
    if not files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    # Process invoice documents
    processor = InvoiceProcessor()
    invoice_data = processor.extract_invoice_data(files)
    
    # Compare to existing stocks
    comparison = processor.compare_with_existing_stocks(invoice_data)
    
    # Ask Claude about it
    ai_prompt = f"""
    User Question: {prompt}
    
    Extracted Invoices:
    {json.dumps(invoice_data, indent=2)}
    
    Stock Matches:
    {json.dumps(comparison, indent=2)}
    """
    
    response = ai_client.process_streaming(
        session_id=session_id,
        prompt=ai_prompt,
        context='stock_ai'
    )
    
    return jsonify({
        'session_id': session_id,
        'analysis': response.get('final_response'),
        'extracted_data': invoice_data,
        'files_processed': len(files)
    })
```

---

#### ⏳ POST `/api/stock/chat-message`
**Purpose**: Send text message to stock AI (without documents)  
**Status**: NOT DONE  
**Priority**: ⭐⭐⭐ CRITICAL

**Used By**: Stock Management UI (chat tab)

**Request:**
```json
{
    "session_id": "uuid-string",
    "prompt": "What stocks have low inventory?"
}
```

**Response:** SSE stream (same as `/stream/<agent_id>`)

---

### 📦 STOCK DATA APIs

---

#### ⏳ GET `/api/stock/master`
**Purpose**: Get master stock list from SQL Server  
**Status**: NOT DONE  
**Priority**: ⭐⭐⭐ CRITICAL

**Used By**: Stock Management UI (Stock Master tab)

**Request Query Params:**
```
GET /api/stock/master?filter=active&limit=100&offset=0
```

**Response:**
```json
{
    "total_count": 215,
    "returned": 100,
    "stocks": [
        {
            "stock_id": "44",
            "name": "Satin 350gsm 320x450mm",
            "supplier_name": "Spicers Paper",
            "product_code": "110219",
            "cost_per_thousand": 145.00,
            "markup": 1.35,
            "is_active": 1,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2025-10-20T14:22:00Z"
        }
    ]
}
```

**Implementation:**
```python
@stock_bp.route('/master', methods=['GET'])
def get_stock_master():
    filter_type = request.args.get('filter', 'active')  # active|all
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    # Query SQLite unified_stocks
    db = sqlite3.connect('G_Folder/Quote_Calculator/stocks/stock_data.db')
    query = "SELECT * FROM unified_stocks"
    
    if filter_type == 'active':
        query += " WHERE is_active = 1"
    
    query += f" ORDER BY stock_id ASC LIMIT {limit} OFFSET {offset}"
    
    cursor = db.execute(query)
    stocks = [dict(row) for row in cursor.fetchall()]
    
    return jsonify({
        'stocks': stocks,
        'returned': len(stocks),
        'limit': limit,
        'offset': offset
    })
```

---

#### ⏳ GET `/api/stock/master-unified`
**Purpose**: Get unified stock list with usage analytics  
**Status**: NOT DONE  
**Priority**: ⭐⭐⭐ CRITICAL

**Used By**: Stock Management UI (analysis tabs)

**Request Query Params:**
```
GET /api/stock/master-unified?filter=active&days=180&limit=100
```

**Response:**
```json
{
    "total_count": 215,
    "stocks": [
        {
            "stock_id": "44",
            "name": "Satin 350gsm 320x450mm",
            "supplier_name": "Spicers Paper",
            "usage_6_months": 156,
            "average_qty_per_job": 3200,
            "last_used_date": "2025-10-22T09:15:00Z",
            "demand_level": "high",  // high|medium|low|none
            "is_active": 1
        }
    ]
}
```

---

#### ⏳ GET `/api/stock/ai-extracted-analytics`
**Purpose**: Get stock usage analytics from extracted jobs  
**Status**: NOT DONE  
**Priority**: ⭐⭐ HIGH

**Used By**: Stock Management UI (analytics/reporting)

**Request Query Params:**
```
GET /api/stock/ai-extracted-analytics?days=90&industry_filter=&limit=50
```

**Response:**
```json
{
    "total_records": 1326,
    "filtered_records": 456,
    "date_range": {
        "start": "2025-07-24",
        "end": "2025-10-22",
        "days": 90
    },
    "analytics": [
        {
            "stock_id": "44",
            "stock_name": "Satin 350gsm",
            "usage_count": 156,
            "total_sheets": 499200,
            "average_qty_per_job": 3200,
            "jobs": ["71584", "71585", "71586"],
            "supplier_name": "Spicers Paper",
            "product_code": "110219",
            "last_used": "2025-10-22"
        }
    ]
}
```

---

### 💰 STOCK INVOICE PROCESSING

---

#### ⏳ POST `/api/stock/process-invoice`
**Purpose**: Upload invoice, extract data with Claude Vision  
**Status**: NOT DONE  
**Priority**: ⭐⭐ HIGH

**Used By**: Stock Management UI (Invoice Processing tab)

**Request:**
```
POST /api/stock/process-invoice

Headers:
Content-Type: multipart/form-data

Body:
{
    "file": <File>,           // PDF or image
    "supplier_hint": "Spicers"  // Optional
}
```

**Response:**
```json
{
    "invoice_data": {
        "supplier_name": "Spicers Paper",
        "invoice_number": "INV-123456",
        "invoice_date": "2025-10-20",
        "total_amount": "2847.50",
        "line_items": [
            {
                "description": "Satin 350gsm 320x450mm",
                "quantity": 5000,
                "unit_price": 145.00,
                "total": 725.00
            }
        ]
    },
    "comparison": {
        "matched_items": 3,
        "new_items": 1,
        "price_changes": [
            {
                "stock_id": 44,
                "old_price": 140.00,
                "new_price": 145.00,
                "change_percent": 3.6
            }
        ]
    }
}
```

---

#### ⏳ POST `/api/stock/import-invoice`
**Purpose**: Import invoice data to database  
**Status**: NOT DONE  
**Priority**: ⭐⭐ HIGH

**Request:**
```json
{
    "invoice_data": {...},
    "items_to_import": [0, 1, 2],  // Indices of items
    "auto_approve": false
}
```

**Response:**
```json
{
    "status": "imported",
    "imported_count": 3,
    "updated_count": 1,
    "skipped_count": 0,
    "new_stocks_created": [
        {"stock_id": "AUTO_001", "name": "New Product"}
    ]
}
```

---

#### ⏳ POST `/api/stock/approve-items`
**Purpose**: Approve specific items for import  
**Status**: NOT DONE  
**Priority**: ⭐⭐ HIGH

**Request:**
```json
{
    "invoice_id": "uuid",
    "selected_items": [0, 1, 2]
}
```

**Response:**
```json
{
    "status": "approved",
    "approved_count": 3
}
```

---

### 💬 THREAD/CONVERSATION MANAGEMENT

---

#### ⏳ GET `/api/threads/list`
**Purpose**: Get list of saved conversations  
**Status**: NOT DONE  
**Priority**: ⭐⭐ HIGH

**Used By**: Data Agent Chat UI (sidebar)

**Request Query Params:**
```
GET /api/threads/list?limit=50&offset=0&interface_type=data_agent_chat&agent_name=Data+Agent
```

**Response:**
```json
{
    "total_count": 342,
    "threads": [
        {
            "thread_id": "uuid-1",
            "title": "Sales Analysis Q4",
            "created_at": "2025-10-20T14:30:00Z",
            "updated_at": "2025-10-23T09:15:00Z",
            "message_count": 23,
            "interface_type": "data_agent_chat",
            "agent_name": "Data Agent",
            "preview": "What were the top products..."
        }
    ]
}
```

---

#### ⏳ POST `/api/threads/save`
**Purpose**: Save conversation thread  
**Status**: NOT DONE  
**Priority**: ⭐⭐ HIGH

**Request:**
```json
{
    "conversation": [...messages...],
    "title": "Sales Analysis Q4",
    "agent_id": "1",
    "thread_id": "uuid" (optional - for updates)
}
```

**Response:**
```json
{
    "thread_id": "uuid-new",
    "saved_at": "2025-10-23T14:30:45Z",
    "message_count": 23
}
```

---

#### ⏳ GET `/api/threads/load/<filename>`
**Purpose**: Load saved conversation  
**Status**: NOT DONE  
**Priority**: ⭐⭐ HIGH

**Response:**
```json
{
    "thread_id": "uuid",
    "title": "Sales Analysis Q4",
    "conversation": [...messages...],
    "metadata": {
        "created_at": "2025-10-20T14:30:00Z",
        "updated_at": "2025-10-23T09:15:00Z",
        "agent_name": "Data Agent"
    }
}
```

---

#### ⏳ DELETE `/api/threads/delete/<filename>`
**Purpose**: Delete saved conversation  
**Status**: NOT DONE  
**Priority**: ⭐⭐ HIGH

**Response:**
```json
{
    "status": "deleted",
    "thread_id": "uuid",
    "deleted_at": "2025-10-23T14:30:45Z"
}
```

---

#### ⏳ GET `/api/threads/search`
**Purpose**: Search saved conversations  
**Status**: NOT DONE  
**Priority**: ⭐ LOW

**Request Query Params:**
```
GET /api/threads/search?q=sales&limit=20
```

**Response:**
```json
{
    "query": "sales",
    "total_found": 8,
    "results": [
        {
            "thread_id": "uuid",
            "title": "Sales Analysis Q4",
            "relevance_score": 0.95,
            "preview": "...top products this quarter..."
        }
    ]
}
```

---

#### ⏳ GET `/api/threads/stats`
**Purpose**: Get thread statistics  
**Status**: NOT DONE  
**Priority**: ⭐ LOW

**Response:**
```json
{
    "total_threads": 342,
    "total_messages": 8904,
    "average_messages_per_thread": 26,
    "active_sessions": 5,
    "most_recent_thread": "2025-10-23T14:30:00Z",
    "threads_by_interface": {
        "data_agent_chat": 215,
        "single_agent_viewer": 87,
        "triple_agent": 40
    }
}
```

---

### 🔧 SESSION MANAGEMENT

---

#### ⏳ POST `/api/sessions/mark-read/<session_id>`
**Purpose**: Mark session as read  
**Status**: NOT DONE  
**Priority**: ⭐ LOW

**Response:**
```json
{
    "status": "marked_read",
    "session_id": "uuid",
    "marked_at": "2025-10-23T14:30:45Z"
}
```

---

#### ⏳ POST `/api/threads/autosave`
**Purpose**: Enable/configure autosave  
**Status**: NOT DONE  
**Priority**: ⭐ LOW

**Request:**
```json
{
    "agent_id": "1",
    "enable": true,
    "save_interval": 60  // seconds
}
```

**Response:**
```json
{
    "status": "configured",
    "autosave_enabled": true,
    "save_interval": 60
}
```

---

### 📤 EXPORT ENDPOINTS

---

#### ⏳ POST `/api/export/session/<agent_id>`
**Purpose**: Export conversation as file  
**Status**: NOT DONE  
**Priority**: ⭐⭐ HIGH

**Request:**
```json
{
    "session_id": "uuid",
    "format": "json|csv|pdf",
    "include_metadata": true
}
```

**Response:**
- **JSON**: `{conversation, metadata}`
- **CSV**: Rows with role, timestamp, content
- **PDF**: Formatted document

**Example:**
```json
{
    "download_url": "/downloads/session-uuid.json",
    "filename": "conversation-20251023.json",
    "size_bytes": 45823,
    "message_count": 156
}
```

---

#### ⏳ POST `/api/export/query/<query_name>`
**Purpose**: Export query results as file  
**Status**: NOT DONE  
**Priority**: ⭐⭐ HIGH

**Request:**
```json
{
    "format": "json|csv|excel",
    "filters": {...}
}
```

**Response:**
```json
{
    "download_url": "/downloads/query-results.csv",
    "filename": "top-products-q4.csv",
    "row_count": 156
}
```

---

#### ⏳ GET `/api/export/queries/list`
**Purpose**: Get list of available export queries  
**Status**: NOT DONE  
**Priority**: ⭐ LOW

**Response:**
```json
{
    "available_queries": [
        {
            "query_name": "top_products",
            "title": "Top 20 Products",
            "file_count": 3,
            "last_exported": "2025-10-22"
        }
    ]
}
```

---

## 🧠 TOOLS REFERENCED BY ENDPOINTS

### Stock Data Tools
```python
# tools/stock_tools.py
def query_stock_levels(filters={}, limit=100):
    """Get current stock levels"""
    
def get_reorder_alerts():
    """Get stocks below reorder point"""
    
def get_supplier_comparison(stock_id):
    """Compare suppliers for one stock"""
    
def get_stock_usage_analytics(days=90):
    """Get usage patterns from extracted_jobs"""
```

### Agent Tools
```python
# tools/agent_tools.py
def query_database_sql(query):
    """Execute custom SQL queries"""
    
def get_available_queries():
    """List pre-built queries"""
    
def get_query_from_library(query_name, params):
    """Execute pre-built query"""
    
def get_calculator_requirements(product_type):
    """Get params needed for quote calculator"""
    
def calculate_business_cards(qty, stock, options):
    """Calculate BC quote"""
```

### Document/Invoice Tools
```python
# tools/invoice_processor.py
class InvoiceProcessor:
    def extract_invoice_data(self, files):
        """Extract from PDF/image using Claude Vision"""
        
    def compare_with_existing_stocks(self, invoice_data):
        """Match to database stocks"""
        
    def import_to_stock_database(self, invoice_data):
        """Create/update stocks"""
```

---

## 📋 MIGRATION WORKFLOW

### Step 1: Create Route Files
```bash
# Create empty route files
touch G_Folder/AI_infrastructure/routes/stock_routes.py
touch G_Folder/AI_infrastructure/routes/thread_routes.py
touch G_Folder/AI_infrastructure/routes/export_routes.py
```

### Step 2: Extract System Prompts
```bash
# From old Flask, copy these functions to new infrastructure
# Location: G_Folder/AI_infrastructure/core/prompts/
# - get_single_agent_system_prompt()
# - get_stock_ai_system_prompt()
# - get_triple_agent_system_prompt()
```

### Step 3: Create Tool Modules
```bash
# New files needed:
# G_Folder/AI_infrastructure/core/tools/agent_tools.py
# G_Folder/AI_infrastructure/core/tools/stock_tools.py
# G_Folder/AI_infrastructure/core/tools/export_tools.py
```

### Step 4: Implement Endpoints (Priority Order)
1. ✅ Template serving (DONE)
2. Agent execution (`/agent/<id>/start`, `/stream/<id>`)
3. Agent management (`/agent/<id>/status`, `/history`, `/clear`)
4. Stock data APIs (`/api/stock/master`, `/chat-with-document`)
5. Stock invoice (`/api/stock/process-invoice`, `/import-invoice`)
6. Thread management (`/api/threads/*`)
7. Export functions (`/api/export/*`)

---

**Document Version**: 1.0  
**Created**: October 23, 2025  
**Total Endpoints**: 20+  
**Estimated Implementation Time**: 3-4 weeks

