# 🚀 COMPLETE API/ROUTES MIGRATION CHECKLIST
**AI Infrastructure Refactoring - October 23, 2025**

---

## 📋 EXECUTIVE SUMMARY

You have **4 UIs** and **20+ API endpoints** that need to migrate from:
- **OLD**: `flask_triple_agent_app.py` (port 5000) - Monolithic 5,850 lines
- **NEW**: Clean modular architecture in `G_Folder/AI_infrastructure/`

**Current Status:**
- ✅ New Flask framework ready (flask_app.py on port 5001)
- ✅ Core AI infrastructure built (unified_ai_client, session_manager)
- ✅ Basic agent & stock routes created
- ⏳ **60+ endpoints/tools still needed**

---

## 🎯 4 PRIMARY UIs TO MIGRATE

### UI #1: STOCK MANAGEMENT (8,599 lines HTML)
**File**: `stock_management.html`
**Location**: Served from OLD Flask `/stock` route
**Dependencies**: Heavy JavaScript, drag-drop, file uploads, real-time updates

**Key API Endpoints Used:**
- `/api/stock/chat-with-document` ← Upload PDFs
- `/api/stock/chat-message` ← Send chat messages  
- `/stream/<agent_id>` ← SSE streaming
- `/api/stock/master` ← Get stock data
- `/api/stock/master-unified` ← Unified stock data
- `/api/stock/ai-extracted-analytics` ← Stock analytics
- Custom endpoints (invoice processing, pricing, etc.)

**Priority**: ⭐⭐⭐ **CRITICAL** - Most complex, most used

---

### UI #2: SINGLE AGENT VIEWER
**File**: `single_agent_viewer.html`
**Location**: Served from OLD Flask `/viewer` route
**Dependencies**: Real-time agent execution, SSE streaming, tool visualization

**Key API Endpoints Used:**
- `/agent/<agent_id>/start` ← POST start execution
- `/stream/<agent_id>` ← SSE event stream
- `/agent/<agent_id>/status` ← GET agent status
- `/agent/<agent_id>/history` ← GET conversation history
- `/agent/<agent_id>/clear` ← POST clear history

**Priority**: ⭐⭐⭐ **CRITICAL** - Core agent functionality

---

### UI #3: TRIPLE AGENT (Email Assistant)
**File**: Part of `/viewer`, same endpoints as Single Agent
**Location**: Served from OLD Flask `/viewer` route
**Dependencies**: 3 concurrent agents (1=Data/Query, 2=Support, 3=Quote), SSE streaming

**Key API Endpoints Used:**
- `/agent/1/start`, `/agent/2/start`, `/agent/3/start` ← POST start each agent
- `/stream/1`, `/stream/2`, `/stream/3` ← SSE streams (concurrent)
- `/agent/{1,2,3}/status` ← Monitor all 3
- `/agent/{1,2,3}/history` ← Get histories
- `/agent/{1,2,3}/clear` ← Clear each

**Priority**: ⭐⭐⭐ **CRITICAL** - Email workflow backbone

---

### UI #4: DATA AGENT CHAT
**File**: `data_agent_chat.html`
**Location**: Served from OLD Flask `/chat` route
**Dependencies**: Document attachment, conversation history, export functions

**Key API Endpoints Used:**
- `/agent/1/start` ← POST send message
- `/stream/1` ← SSE stream response
- `/agent/1/history` ← GET chat history
- `/api/agent/chat-with-document` ← Upload docs
- `/api/threads/list` ← GET saved conversations
- `/api/threads/save` ← POST save conversation
- `/api/threads/load/<filename>` ← GET load conversation
- `/api/export/session/<agent_id>` ← POST export

**Priority**: ⭐⭐ **HIGH** - Secondary workflow

---

## 📡 COMPLETE ENDPOINT MAPPING

### Category 1: UI Routes (Template Serving)
These serve the HTML templates. You've already done this in new Flask:

```
✅ GET  /                    → index.html (home page)
✅ GET  /viewer              → single_agent_viewer.html
✅ GET  /chat                → data_agent_chat.html
✅ GET  /stock               → stock_management.html
```

**Status**: DONE in new Flask

---

### Category 2: Agent Execution (Core AI)

#### 2.1 Agent Lifecycle
```
⏳ POST /agent/<agent_id>/start
   Input:  session_id, prompt, context (triple_agent|single_agent), files[]
   Output: session_id, status, message_id
   
⏳ GET  /stream/<agent_id>
   Input:  session_id (query param)
   Output: SSE stream (Content-Type: text/event-stream)
           Sends: message chunks, tool calls, results, completion
   
⏳ GET  /agent/<agent_id>/status
   Input:  session_id (query param)
   Output: {status, running, queue_size, current_message}
   
⏳ GET  /agent/<agent_id>/history
   Input:  session_id (query param), limit (default 50)
   Output: [{role, content, timestamp, tool_calls}]
   
⏳ POST /agent/<agent_id>/clear
   Input:  session_id (query param)
   Output: {status: cleared}
```

**Status**: PARTIALLY DONE (agent_routes.py has skeleton)
**Work**: Implement SSE streaming, thread safety, system prompts

---

#### 2.2 Agent Configuration (System Prompts)
```
⏳ GET  /api/agent/config
   Output: {
     "single_agent": {sys_prompt, tools, examples},
     "triple_agent": {agent_1_sys_prompt, agent_2_sys_prompt, ...},
     "stock_ai": {sys_prompt, tools}
   }
```

**Status**: NOT DONE
**Work**: Extract system prompts from old Flask, make endpoints

---

### Category 3: Stock Management APIs

#### 3.1 Stock Chat & Documents
```
⏳ POST /api/stock/chat-with-document
   Input:  session_id, prompt, files[] (PDF/image), supplier_hint
   Output: {analysis, extracted_data, suggestions}
   
⏳ POST /api/stock/chat-message
   Input:  session_id, prompt
   Output: SSE stream or JSON response
```

**Status**: NOT DONE
**Work**: Implement document processor, Claude Vision integration

---

#### 3.2 Stock Data Endpoints
```
⏳ GET  /api/stock/master
   Input:  filter (active|all), limit, offset
   Output: [{stock_id, name, supplier, cost, markup, usage_count}]
   
⏳ GET  /api/stock/master-unified
   Input:  filter, limit, offset
   Output: [{stock_id, name, supplier, cost, usage_6m, demand_level}]
   
⏳ GET  /api/stock/ai-extracted-analytics
   Input:  days (7|30|90|9999), industry_filter
   Output: [{stock_id, usage_count, avg_qty, last_used, supplier}]
```

**Status**: NOT DONE
**Work**: Query unified_stocks table, aggregate usage data

---

#### 3.3 Stock Invoice Processing
```
⏳ POST /api/stock/process-invoice
   Input:  file (PDF/image), supplier_hint
   Output: {invoice_data, matched_stocks, new_items, price_changes}
   
⏳ POST /api/stock/import-invoice
   Input:  invoice_data, items_to_import, auto_approve
   Output: {imported_count, updated_count, skipped_count}
   
⏳ POST /api/stock/approve-items
   Input:  invoice_id, selected_items
   Output: {success, import_results}
```

**Status**: NOT DONE
**Work**: Implement invoice extraction system, stock import logic

---

### Category 4: Thread/Conversation Management

#### 4.1 Thread CRUD
```
⏳ GET  /api/threads/list
   Input:  limit, offset, source, interface_type, agent_name
   Output: [{thread_id, title, updated_at, interface_type}]
   
⏳ POST /api/threads/save
   Input:  conversation, title, agent_id, thread_id (optional)
   Output: {thread_id, saved_at}
   
⏳ GET  /api/threads/load/<filename>
   Input:  filename
   Output: {conversation, title, metadata}
   
⏳ DELETE /api/threads/delete/<filename>
   Input:  filename
   Output: {status: deleted}
   
⏳ GET  /api/threads/search
   Input:  q (search query), limit
   Output: [{thread_id, title, snippet, relevance_score}]
```

**Status**: NOT DONE
**Work**: Implement thread database/file storage, search logic

---

#### 4.2 Thread Utilities
```
⏳ POST /api/sessions/mark-read/<session_id>
   Output: {status: marked_read}
   
⏳ GET  /api/threads/stats
   Output: {total_threads, active_sessions, avg_turns}
   
⏳ POST /api/threads/autosave
   Input:  agent_id, conversation, auto_save_interval
   Output: {autosave_enabled, save_frequency}
```

**Status**: NOT DONE
**Work**: Implement session tracking, stats collection

---

### Category 5: Export Functions

#### 5.1 Session Export
```
⏳ POST /api/export/session/<agent_id>
   Input:  format (json|csv|pdf), session_id
   Output: File download or {download_url}
```

**Status**: NOT DONE
**Work**: Implement export formatters

---

#### 5.2 Query Export
```
⏳ POST /api/export/query/<query_name>
   Input:  format (json|csv|excel)
   Output: File download
   
⏳ GET  /api/export/queries/list
   Output: {available_queries, file_counts}
```

**Status**: NOT DONE
**Work**: Implement query execution, result formatting

---

## 🛠️ TOOLS TO REFACTOR/BRING ACROSS

### Priority 1: Core AI Tools (Used by all UIs)

```
From: G_Folder/Quote_Calculator/AI_Quote_Agent/core/tool_use_agent.py

✅ AI Agent Framework - ALREADY IMPORTED
   - ToolUseAgent class
   - message_callback system
   - streaming support
   
⏳ DATABASE TOOLS:
   - query_stock_levels() 
   - get_reorder_alerts()
   - get_production_pricing()
   - query_database_sql()
   
⏳ BUSINESS LOGIC TOOLS:
   - calculate_business_cards()
   - calculate_flyers()
   - calculate_perfect_bound_books()
   - calculate_booklets()
   - get_available_queries()
   - get_query_from_library()
   - get_calculator_requirements()
   
⏳ DATA TOOLS:
   - get_invoice_data()
   - compare_invoice_to_stock()
   - import_stock_from_invoice()
   
⏳ UTILITIES:
   - format_currency()
   - format_date()
   - escape_sql()
```

**Status**: Partially in place (ToolUseAgent exists)
**Work**: Extract remaining tools to modular files in `/core/tools/`

---

### Priority 2: Stock-Specific Tools

```
From: G_Folder/tools/invoice_processor.py

✅ InvoiceProcessor CLASS (Exists)
   - extract_invoice_data()
   - compare_with_existing_stocks()
   - import_to_stock_database()
   - process_invoice_batch()
   
⏳ STOCK QUERY TOOLS:
   - get_unified_stocks_by_filter()
   - get_stock_usage_analytics()
   - get_reorder_alerts()
   - get_supplier_comparison()
   
⏳ STOCK UPDATE TOOLS:
   - update_stock_level()
   - update_stock_record()
   - update_job_record()
```

**Status**: Partially exists
**Work**: Refactor to modular tools, create endpoints

---

### Priority 3: System Prompts

```
From: flask_triple_agent_app.py

⏳ get_single_agent_system_prompt()          [~800 lines]
⏳ get_stock_ai_system_prompt()              [~1000 lines]
⏳ get_triple_agent_system_prompt(agent_id)  [~400 lines]
```

**Status**: NOT IN NEW INFRASTRUCTURE
**Work**: Extract to `/core/prompts/` directory

---

## 📁 SUGGESTED FILE ORGANIZATION

```
G_Folder/AI_infrastructure/

routes/
├── __init__.py
├── agent_routes.py          ← Already exists (skeleton)
├── stock_routes.py          ← Already exists (skeleton)
├── thread_routes.py         ← NEW: Thread management
├── export_routes.py         ← NEW: Export functions
└── config_routes.py         ← NEW: Config/system prompts

core/
├── unified_ai_client.py      ← Already exists
├── unified_session_manager.py ← Already exists
├── unified_config.py         ← NEW: Config management
│
├── tools/
│   ├── __init__.py
│   ├── agent_tools.py        ← NEW: Database, query, calc tools
│   ├── stock_tools.py        ← NEW: Stock-specific tools
│   ├── export_tools.py       ← NEW: Export formatters
│   ├── invoice_processor.py  ← COPY from tools/
│   └── document_processor.py ← NEW: Claude Vision integration
│
├── prompts/
│   ├── __init__.py
│   ├── single_agent_prompt.py ← NEW: Extract from old Flask
│   ├── stock_ai_prompt.py     ← NEW: Extract from old Flask
│   └── triple_agent_prompts.py ← NEW: Extract from old Flask
│
└── sessions/
    ├── thread_manager.py      ← Conversation storage
    └── thread_history.py      ← Already exists (partial)

templates/
├── index.html
├── single_agent_viewer.html   ← MIGRATE from old Flask
├── data_agent_chat.html       ← MIGRATE from old Flask
├── stock_management.html      ← MIGRATE from old Flask (HUGE)
└── base.html                  ← NEW: Common layout

static/
├── css/
│   ├── stock_management.css
│   └── agent_viewer.css
└── js/
    ├── stock_manager.js
    ├── agent_client.js
    └── sse_client.js

API_MIGRATION_CHECKLIST.md     ← YOU ARE HERE
ROUTES_COMPLETE_INVENTORY.md   ← NEW: ALL endpoints + details
```

---

## 🚀 PHASED IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Week 1)
- [ ] Extract system prompts to `/core/prompts/`
- [ ] Create tool modules in `/core/tools/`
- [ ] Implement thread management routes
- [ ] Test basic agent execution

### Phase 2: Stock Management (Week 2)
- [ ] Implement stock data endpoints
- [ ] Implement stock chat endpoints
- [ ] Integrate document processor
- [ ] Test stock UI migration

### Phase 3: Export & Utilities (Week 3)
- [ ] Implement export endpoints
- [ ] Implement thread CRUD routes
- [ ] Create config endpoints
- [ ] Polish error handling

### Phase 4: Testing & Deployment (Week 4)
- [ ] Integration testing (all 4 UIs)
- [ ] Performance testing (SSE streaming)
- [ ] Security audit
- [ ] Deployment to production

---

## ✅ MIGRATION CHECKLIST BY ENDPOINT

### Quick Reference: Check off as you migrate

#### UI Routes (Template Serving)
- [x] GET  /                    → Index
- [x] GET  /viewer              → Single Agent Viewer
- [x] GET  /chat                → Data Agent Chat
- [x] GET  /stock               → Stock Management

#### Agent Execution
- [ ] POST /agent/<id>/start    → Start agent execution
- [ ] GET  /stream/<id>         → SSE stream
- [ ] GET  /agent/<id>/status   → Get agent status
- [ ] GET  /agent/<id>/history  → Get conversation history
- [ ] POST /agent/<id>/clear    → Clear conversation

#### Stock Management
- [ ] POST /api/stock/chat-with-document   → Upload & analyze
- [ ] POST /api/stock/chat-message         → Send message
- [ ] GET  /api/stock/master               → Get stock master
- [ ] GET  /api/stock/master-unified       → Get unified stocks
- [ ] GET  /api/stock/ai-extracted-analytics → Get analytics

#### Stock Invoice Processing
- [ ] POST /api/stock/process-invoice      → Extract invoice
- [ ] POST /api/stock/import-invoice       → Import invoice
- [ ] POST /api/stock/approve-items        → Approve items

#### Thread Management
- [ ] GET  /api/threads/list               → List threads
- [ ] POST /api/threads/save               → Save thread
- [ ] GET  /api/threads/load/<filename>    → Load thread
- [ ] DELETE /api/threads/delete/<filename> → Delete thread
- [ ] GET  /api/threads/search             → Search threads
- [ ] GET  /api/threads/stats              → Get stats

#### Session Management
- [ ] POST /api/sessions/mark-read/<id>    → Mark read
- [ ] POST /api/threads/autosave           → Setup autosave

#### Export
- [ ] POST /api/export/session/<id>        → Export session
- [ ] POST /api/export/query/<name>        → Export query
- [ ] GET  /api/export/queries/list        → List exports

---

## 🔗 DEPENDENCIES & IMPORTS

### Required Files to Copy/Reference
```python
# From old Flask that you'll reference:
from G_Folder.Quote_Calculator.AI_Quote_Agent.core.tool_use_agent import ToolUseAgent
from G_Folder.tools.invoice_processor import InvoiceProcessor
from G_Folder.Quote_Calculator.stocks.stock_database_cli import StockDatabaseCLI

# From new infrastructure (already built):
from core.unified_ai_client import ai_client
from core.unified_session_manager import session_manager
```

---

## 🎯 NEXT IMMEDIATE STEPS

1. **TODAY:**
   - [ ] Read `/G_Folder/AI_infrastructure/core/unified_ai_client.py` → Understand AI execution
   - [ ] Read `/G_Folder/AI_infrastructure/core/unified_session_manager.py` → Understand session handling
   - [ ] Check existing tool definitions in new infrastructure

2. **THIS WEEK:**
   - [ ] Create `/core/tools/` directory structure
   - [ ] Extract system prompts to `/core/prompts/`
   - [ ] Implement `/routes/thread_routes.py`
   - [ ] Test Stock Management UI with new Flask

3. **CHECKLIST:**
   - [ ] Which 4 UIs should I test first? (Recommend: Stock Management first)
   - [ ] What's your current database connection? (SQLite? SQL Server?)
   - [ ] Do you want copy-paste strategy or full refactor? (Recommend: Copy-paste Phase 1, refactor Phase 2)

---

## 📞 QUESTIONS FOR YOU

1. **Testing Priority**: Which UI do you want working first?
   - Stock Management (most complex, most used)
   - Single Agent Viewer (core agent functionality)
   - Data Agent Chat (simpler, good for testing)
   - Triple Agent (complex, 3 concurrent streams)

2. **Database Strategy**: 
   - Keep using SQLite `stock_data.db`?
   - Keep using SQL Server for production data?

3. **Timeline**:
   - How quickly do you need all 4 UIs working?
   - Is it OK to have partial functionality while migrating?

4. **Tools**:
   - Should I copy all tools from old Flask as-is, or refactor while migrating?

---

**Document Version**: 1.0  
**Created**: October 23, 2025  
**Last Updated**: October 23, 2025

