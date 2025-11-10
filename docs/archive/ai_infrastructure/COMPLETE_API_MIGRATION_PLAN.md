# 🚀 COMPLETE Flask API Migration Plan - NEW Flask

**Date**: October 23, 2025  
**Scope**: Migrate ALL endpoints from OLD Flask EXCEPT deleted Stock AI Chat endpoint  
**Total Endpoints**: ~55 endpoints across 7 categories  

---

## 📊 Complete Endpoint Inventory

### Category 1: Agent Endpoints (6 endpoints) - HIGH PRIORITY
**Blueprint**: `routes/agent_routes.py`

1. ✅ `/agent/<agent_id>/start` (POST) - Start agent with files/text
2. ✅ `/stream/<agent_id>` (GET) - SSE streaming (already partial)
3. `/agent/<agent_id>/status` (GET) - Get agent status
4. `/agent/<agent_id>/history` (GET) - Get conversation history
5. `/agent/<agent_id>/clear` (POST) - Clear conversation
6. `/api/agent/chat-with-document-stream` (POST) - Document chat with SSE

**❌ SKIP**: `/api/stock/chat-with-document-stream` (DELETED October 23, 2025)

---

### Category 2: Thread Management (8 endpoints) - MEDIUM PRIORITY
**Blueprint**: `routes/thread_routes.py` (NEW)

7. `/api/threads/list` (GET) - List saved threads
8. `/api/threads/save` (POST) - Save thread
9. `/api/sessions/mark-read/<session_id>` (POST) - Mark session as read
10. `/api/threads/load/<filename>` (GET) - Load thread
11. `/api/threads/delete/<filename>` (DELETE) - Delete thread
12. `/api/threads/search` (GET) - Search threads
13. `/api/threads/stats` (GET) - Thread statistics
14. `/api/threads/autosave` (POST) - Auto-save thread

---

### Category 3: Stock Master & Core (15 endpoints) - HIGH PRIORITY
**Blueprint**: `routes/stock_routes.py` (EXPAND EXISTING)

15. ✅ `/api/stock/master` (GET) - Stock master list (already in stock_routes.py)
16. `/api/stock/master-unified` (GET) - Unified stock list (SQLite)
17. ✅ `/api/stock/update` (POST) - Update stock (already in stock_routes.py)
18. `/api/stock/update-unified` (POST) - Update unified stock (SQLite)
19. `/api/stock/create-session` (POST) - Create chat session
20. `/api/stock/list-tables` (GET) - List database tables
21. `/api/stock/list-threads` (GET) - List chat threads
22. `/api/stock/load-thread/<session_id>` (GET) - Load thread
23. `/api/stock/ai-query` (POST) - AI query execution
24. `/api/stock/search` (GET) - Search stocks
25. `/api/stock/reorder-recommendation/<int:stock_id>` (GET) - Reorder recommendation
26. `/api/stock/reorder-alerts` (GET) - Reorder alerts
27. `/api/stock/production-data` (GET) - Production orders
28. `/api/stock/process-production-orders` (POST) - Process production
29. `/api/stock/click-costs` (GET) - Click costs (pricing)

---

### Category 4: Stock Analytics (4 endpoints) - MEDIUM PRIORITY
**Blueprint**: `routes/stock_analytics_routes.py` (NEW)

30. `/api/stock/usage-analytics` (GET) - Stock usage analytics
31. `/api/stock/profit-analysis` (GET) - Profit analysis
32. `/api/stock/client-preferences` (GET) - Client preferences
33. `/api/stock/ai-extracted-analytics` (GET) - AI-extracted job analytics

---

### Category 5: Invoice Processing (3 endpoints) - HIGH PRIORITY
**Blueprint**: `routes/invoice_routes.py` (NEW)

34. `/api/stock/process-invoice` (POST) - Process invoice with Claude Vision
35. `/api/stock/import-invoice` (POST) - Import invoice to database
36. `/api/stock/approve-items` (POST) - Approve invoice items

---

### Category 6: SQLite Editor (4 endpoints) - LOW PRIORITY
**Blueprint**: `routes/sqlite_routes.py` (NEW)

37. `/api/sqlite/schema` (GET) - Get database schema
38. `/api/sqlite/execute` (POST) - Execute SQL query
39. `/api/sqlite/table-data` (GET) - Get table data
40. `/api/sqlite/update-rows` (POST) - Update rows

---

### Category 7: Pricing Management (12 endpoints) - MEDIUM PRIORITY
**Blueprint**: `routes/pricing_routes.py` (NEW)

41. `/api/pricing/stock-costs` (GET) - Get stock costs
42. `/api/pricing/stock-costs` (POST) - Update stock costs
43. `/api/pricing/profit-margins` (GET) - Get profit margins
44. `/api/pricing/profit-margins` (POST) - Update profit margins
45. `/api/pricing/markup-rules` (GET) - Get markup rules
46. `/api/pricing/markup-rules` (POST) - Update markup rules
47. `/api/pricing/click-costs` (GET) - Get click costs (duplicate)
48. `/api/pricing/click-costs` (POST) - Update click costs
49. `/api/pricing/bulk-adjust` (POST) - Bulk price adjustment
50. `/api/stock/click-costs/update` (POST) - Update click costs (alias)
51. `/api/stock/profit-margins` (GET) - Get profit margins (alias)
52. `/api/stock/pricing/click-costs` (GET) - Click costs (alias)

---

### Category 8: Export & Queries (3 endpoints) - LOW PRIORITY
**Blueprint**: `routes/export_routes.py` (NEW)

53. `/api/export/session/<agent_id>` (POST) - Export agent session
54. `/api/export/query/<query_name>` (POST) - Execute export query
55. `/api/export/queries/list` (GET) - List available queries

---

## 🎯 Migration Priority Phases

### Phase 1: CRITICAL (Day 1 - 4 hours)
**Make Triple Agent + Stock Management work**

1. **Agent Endpoints** (agent_routes.py):
   - `/agent/<id>/start` (POST) - Already has basic, upgrade to full ToolUseAgent
   - `/stream/<id>` (GET) - Already exists, upgrade to full SSE
   - `/agent/<id>/status` (GET) - NEW
   - `/agent/<id>/history` (GET) - NEW
   - `/agent/<id>/clear` (POST) - NEW

2. **Stock Core** (stock_routes.py):
   - `/api/stock/master-unified` (GET) - NEW (SQLite stocks)
   - `/api/stock/update-unified` (POST) - NEW (update SQLite)
   - `/api/stock/create-session` (POST) - NEW
   - `/api/stock/list-threads` (GET) - NEW
   - `/api/stock/load-thread/<session_id>` (GET) - NEW

**Test**: Triple Agent + Stock Management UI functional

---

### Phase 2: ESSENTIAL (Day 2 - 3 hours)
**Analytics + Invoice Processing**

3. **Stock Analytics** (stock_analytics_routes.py):
   - `/api/stock/usage-analytics` (GET) - Stock usage charts
   - `/api/stock/ai-extracted-analytics` (GET) - AI job extraction data

4. **Invoice Processing** (invoice_routes.py):
   - `/api/stock/process-invoice` (POST) - Claude Vision extraction
   - `/api/stock/import-invoice` (POST) - Import to database
   - `/api/stock/approve-items` (POST) - Approval workflow

**Test**: Stock usage analytics + invoice upload working

---

### Phase 3: FEATURES (Day 3 - 2 hours)
**Thread Management + Pricing**

5. **Thread Management** (thread_routes.py):
   - `/api/threads/list` (GET)
   - `/api/threads/save` (POST)
   - `/api/threads/load/<filename>` (GET)
   - `/api/threads/delete/<filename>` (DELETE)

6. **Pricing Management** (pricing_routes.py):
   - `/api/pricing/stock-costs` (GET/POST)
   - `/api/pricing/profit-margins` (GET/POST)
   - `/api/pricing/markup-rules` (GET/POST)

**Test**: Save/load threads + edit pricing

---

### Phase 4: OPTIONAL (Day 4 - 1 hour)
**SQLite Editor + Exports**

7. **SQLite Editor** (sqlite_routes.py):
   - `/api/sqlite/schema` (GET)
   - `/api/sqlite/execute` (POST)
   - `/api/sqlite/table-data` (GET)

8. **Export Functions** (export_routes.py):
   - `/api/export/session/<agent_id>` (POST)
   - `/api/export/query/<query_name>` (POST)

**Test**: SQLite editor + export buttons

---

## 📁 File Structure for NEW Flask

```
AI_infrastructure/
├── flask_app.py                      # Main app (blueprint registration)
├── core/
│   ├── unified_ai_client.py          # ✅ Already exists
│   ├── unified_session_manager.py    # ✅ Already exists
│   ├── agent_state_manager.py        # NEW - Agent state tracking
│   ├── agent_worker.py                # NEW - ToolUseAgent worker
│   └── tool_use_agent.py             # ✅ Already exists (verify location)
├── routes/
│   ├── agent_routes.py               # ⚠️ Exists but needs expansion
│   ├── stock_routes.py               # ⚠️ Exists but needs expansion
│   ├── thread_routes.py              # NEW - Thread management
│   ├── stock_analytics_routes.py     # NEW - Analytics endpoints
│   ├── invoice_routes.py             # NEW - Invoice processing
│   ├── sqlite_routes.py              # NEW - SQLite editor
│   ├── pricing_routes.py             # NEW - Pricing management
│   └── export_routes.py              # NEW - Export functions
└── utils/
    ├── database_helpers.py           # NEW - DB connection helpers
    ├── file_encoding.py               # NEW - File upload helpers
    └── response_helpers.py           # NEW - JSON response formatting
```

---

## 🔧 Implementation Strategy

### Step 1: Create Foundation Files (1 hour)
```python
# core/agent_state_manager.py - Agent state tracking
# core/agent_worker.py - ToolUseAgent background worker
# utils/database_helpers.py - SQLite/SQL Server connections
# utils/file_encoding.py - Base64 encoding, file validation
# utils/response_helpers.py - Standardized JSON responses
```

### Step 2: Expand Existing Routes (2 hours)
```python
# routes/agent_routes.py - Add 5 agent endpoints
# routes/stock_routes.py - Add 10 stock endpoints
```

### Step 3: Create New Route Blueprints (3 hours)
```python
# routes/thread_routes.py - 8 endpoints
# routes/stock_analytics_routes.py - 4 endpoints
# routes/invoice_routes.py - 3 endpoints
```

### Step 4: Optional Features (2 hours)
```python
# routes/sqlite_routes.py - 4 endpoints
# routes/pricing_routes.py - 12 endpoints
# routes/export_routes.py - 3 endpoints
```

### Step 5: Register All Blueprints (10 minutes)
```python
# flask_app.py
from routes.agent_routes import agent_bp
from routes.stock_routes import stock_bp
from routes.thread_routes import thread_bp
from routes.stock_analytics_routes import analytics_bp
from routes.invoice_routes import invoice_bp
from routes.sqlite_routes import sqlite_bp
from routes.pricing_routes import pricing_bp
from routes.export_routes import export_bp

app.register_blueprint(agent_bp, url_prefix='/api/agent')
app.register_blueprint(stock_bp, url_prefix='/api/stock')
app.register_blueprint(thread_bp, url_prefix='/api/threads')
app.register_blueprint(analytics_bp, url_prefix='/api/stock')
app.register_blueprint(invoice_bp, url_prefix='/api/stock')
app.register_blueprint(sqlite_bp, url_prefix='/api/sqlite')
app.register_blueprint(pricing_bp, url_prefix='/api/pricing')
app.register_blueprint(export_bp, url_prefix='/api/export')
```

---

## ✅ Endpoint Migration Checklist

### Phase 1 (CRITICAL) - 15 endpoints:
- [ ] `/agent/<id>/start` (POST) - Upgrade to full ToolUseAgent
- [ ] `/stream/<id>` (GET) - Upgrade to full SSE
- [ ] `/agent/<id>/status` (GET)
- [ ] `/agent/<id>/history` (GET)
- [ ] `/agent/<id>/clear` (POST)
- [ ] `/api/stock/master-unified` (GET)
- [ ] `/api/stock/update-unified` (POST)
- [ ] `/api/stock/create-session` (POST)
- [ ] `/api/stock/list-threads` (GET)
- [ ] `/api/stock/load-thread/<session_id>` (GET)
- [ ] `/api/stock/ai-query` (POST)
- [ ] `/api/stock/list-tables` (GET)
- [ ] `/api/stock/search` (GET)
- [ ] `/api/stock/reorder-alerts` (GET)
- [ ] `/api/stock/production-data` (GET)

### Phase 2 (ESSENTIAL) - 7 endpoints:
- [ ] `/api/stock/usage-analytics` (GET)
- [ ] `/api/stock/ai-extracted-analytics` (GET)
- [ ] `/api/stock/process-invoice` (POST)
- [ ] `/api/stock/import-invoice` (POST)
- [ ] `/api/stock/approve-items` (POST)
- [ ] `/api/stock/profit-analysis` (GET)
- [ ] `/api/stock/client-preferences` (GET)

### Phase 3 (FEATURES) - 20 endpoints:
- [ ] All 8 thread management endpoints
- [ ] All 12 pricing management endpoints

### Phase 4 (OPTIONAL) - 7 endpoints:
- [ ] All 4 SQLite editor endpoints
- [ ] All 3 export endpoints

---

## 📝 Migration Notes

### What to SKIP:
❌ `/api/stock/chat-with-document-stream` (POST) - **DELETED October 23, 2025**

### Consolidation Opportunities:
- Merge duplicate click-costs endpoints (3 aliases → 1 endpoint)
- Merge duplicate profit-margins endpoints (2 aliases → 1 endpoint)
- Standardize pricing endpoint structure

### Testing Strategy:
1. **After Phase 1**: Test Triple Agent + Stock Management UI
2. **After Phase 2**: Test analytics charts + invoice upload
3. **After Phase 3**: Test thread save/load + pricing edits
4. **After Phase 4**: Test SQLite editor + export buttons

---

## 🎯 Total Effort Estimate

| Phase | Endpoints | Time | Priority |
|-------|-----------|------|----------|
| Phase 1 | 15 | 4 hours | CRITICAL |
| Phase 2 | 7 | 3 hours | ESSENTIAL |
| Phase 3 | 20 | 2 hours | FEATURES |
| Phase 4 | 7 | 1 hour | OPTIONAL |
| **Total** | **49** | **10 hours** | - |

*Note: 55 total endpoints minus 6 duplicates/aliases = 49 unique endpoints to migrate*

---

## 🚀 Next Steps

1. **Start with Phase 1** (agent + stock core endpoints)
2. **Test Triple Agent UI** after Phase 1
3. **Continue with Phase 2** (analytics + invoice)
4. **Test Stock Management UI** after Phase 2
5. **Phase 3 & 4 can be done as needed**

**Ready to begin?** Start with creating the foundation files (agent_state_manager.py, agent_worker.py, database_helpers.py)!
