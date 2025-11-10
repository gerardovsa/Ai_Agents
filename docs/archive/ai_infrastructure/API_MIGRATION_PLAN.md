# 🏗️ API Routes Migration & Refactoring Plan

**Date**: October 23, 2025  
**Goal**: Migrate all API endpoints from OLD Flask to NEW Flask with clean architecture  
**Status**: 📋 PLANNING PHASE  

---

## 🎯 Overview

**Current State**:
- OLD Flask: 3,000+ lines monolithic file with all routes mixed together
- NEW Flask: Modular architecture with separate route blueprints (partial implementation)

**Target State**:
- All routes organized in `AI_infrastructure/routes/` folder
- Each UI gets dedicated route file
- Clean separation of concerns
- Complete migration from OLD to NEW Flask

---

## 📁 Route Organization Strategy

### Current Routes Structure (NEW Flask):
```
AI_infrastructure/routes/
├── stock_routes.py         ✅ Exists (partial - 8 endpoints)
├── agent_routes.py         ✅ Exists (partial - 7 endpoints)
└── [MISSING FILES]
```

### Target Routes Structure:
```
AI_infrastructure/routes/
├── stock_routes.py         📝 Expand - Stock Management UI
├── agent_routes.py         📝 Expand - Data Agent, Single Viewer, Triple Agent
├── invoice_routes.py       🆕 Create - Invoice processing
├── shopify_routes.py       🆕 Create - Shopify integration
├── export_routes.py        🆕 Create - Export/download endpoints
├── analytics_routes.py     🆕 Create - Analytics and reporting
└── health_routes.py        🆕 Create - Health checks, system status
```

---

## 📊 Endpoint Inventory (OLD Flask)

### 1. Stock Management Routes (15+ endpoints)
**Source**: Lines 1700-2900 in flask_triple_agent_app.py

| Endpoint | Method | Status | Priority |
|----------|--------|--------|----------|
| `/api/stock/chat` | POST | ✅ Done | - |
| `/api/stock/chat-with-document` | POST | ✅ Done | - |
| `/api/stock/stream/<session_id>` | GET | ✅ Done | - |
| `/api/stock/master-unified` | GET | ❌ Missing | HIGH |
| `/api/stock/usage-analytics` | GET | ⚠️ Stub | HIGH |
| `/api/stock/ai-extracted-analytics` | GET | ❌ Missing | HIGH |
| `/api/stock/process-invoice` | POST | ❌ Missing | HIGH |
| `/api/stock/approve-items` | POST | ❌ Missing | MEDIUM |
| `/api/stock/import-invoice` | POST | ❌ Missing | MEDIUM |
| `/api/stock/create-session` | POST | ❌ Missing | HIGH |
| `/api/stock/list-threads` | GET | ❌ Missing | HIGH |
| `/api/stock/load-thread/<id>` | GET | ❌ Missing | HIGH |
| `/api/stock/list-tables` | GET | ❌ Missing | MEDIUM |
| `/api/stock/chat-with-document-stream` | POST | ❌ Missing | LOW |

**Lines to Copy**: 1700-2900 (~1,200 lines)

### 2. Agent Routes (12+ endpoints)
**Source**: Lines 1363-1700 in flask_triple_agent_app.py

| Endpoint | Method | Status | Priority |
|----------|--------|--------|----------|
| `/chat` | GET | ❌ Missing | HIGH |
| `/agent/<agent_id>/start` | POST | ❌ Missing | HIGH |
| `/stream/<agent_id>` | GET | ❌ Missing | HIGH |
| `/agent/<agent_id>/status` | GET | ❌ Missing | MEDIUM |
| `/agent/<agent_id>/history` | GET | ❌ Missing | MEDIUM |
| `/agent/<agent_id>/clear` | POST | ❌ Missing | MEDIUM |
| `/api/agent/chat-with-document-stream` | POST | ❌ Missing | HIGH |
| `/api/data-agent/chat` | POST | ⚠️ Partial | HIGH |
| `/api/single-viewer/chat` | POST | ⚠️ Partial | HIGH |
| `/api/triple-agent/<id>/chat` | POST | ⚠️ Partial | HIGH |

**Lines to Copy**: 1363-1700 (~340 lines)

### 3. Invoice Processing Routes (8 endpoints)
**Source**: Lines 2200-2500 in flask_triple_agent_app.py

| Endpoint | Method | Status | Priority |
|----------|--------|--------|----------|
| `/api/invoice/upload` | POST | ❌ Missing | MEDIUM |
| `/api/invoice/process` | POST | ❌ Missing | MEDIUM |
| `/api/invoice/extract` | POST | ❌ Missing | MEDIUM |
| `/api/invoice/compare` | POST | ❌ Missing | MEDIUM |
| `/api/invoice/import` | POST | ❌ Missing | MEDIUM |

**Lines to Copy**: ~300 lines

### 4. Shopify Routes (10+ endpoints)
**Source**: Lines 900-1200 in flask_triple_agent_app.py

| Endpoint | Method | Status | Priority |
|----------|--------|--------|----------|
| `/api/shopify/webhook` | POST | ❌ Missing | LOW |
| `/api/shopify/orders` | GET | ❌ Missing | LOW |
| `/api/shopify/dashboard/*` | GET | ❌ Missing | LOW |

**Lines to Copy**: ~300 lines

### 5. Export/Download Routes (5 endpoints)
**Source**: Lines 2100-2300 in flask_triple_agent_app.py

| Endpoint | Method | Status | Priority |
|----------|--------|--------|----------|
| `/api/export/session/<agent_id>` | POST | ❌ Missing | MEDIUM |
| `/api/export/csv` | POST | ❌ Missing | LOW |
| `/api/export/json` | POST | ❌ Missing | LOW |

**Lines to Copy**: ~200 lines

---

## 🚀 Migration Strategy

### Phase 1: High Priority (Essential for UIs to Work)
**Timeline**: 2-3 hours  
**Goal**: Get all UIs functional on NEW Flask

**Endpoints to Migrate**:

**Stock Routes** (stock_routes.py):
1. `/api/stock/master-unified` - Stock inventory list
2. `/api/stock/create-session` - Create chat session
3. `/api/stock/list-threads` - List conversations
4. `/api/stock/load-thread/<id>` - Load conversation
5. `/api/stock/ai-extracted-analytics` - Job analytics

**Agent Routes** (agent_routes.py):
1. `/chat` - Triple Agent chat page
2. `/agent/<agent_id>/start` - Start agent conversation
3. `/stream/<agent_id>` - SSE streaming for agents
4. `/agent/<agent_id>/history` - Get agent history
5. `/api/agent/chat-with-document-stream` - Document upload streaming

### Phase 2: Medium Priority (Enhanced Features)
**Timeline**: 1-2 hours  
**Goal**: Full Stock Management features

**Endpoints to Migrate**:

**Stock Routes**:
1. `/api/stock/process-invoice` - Invoice processing
2. `/api/stock/approve-items` - Approve invoice items
3. `/api/stock/import-invoice` - Import to database

**Export Routes** (NEW FILE):
1. `/api/export/session/<agent_id>` - Export conversations

### Phase 3: Low Priority (Nice to Have)
**Timeline**: 1 hour  
**Goal**: Complete feature parity

**Endpoints to Migrate**:
- Shopify webhooks
- CSV/JSON exports
- Advanced analytics

---

## 🛠️ Refactoring Approach

### Step 1: Copy & Adapt (Not Direct Copy)
```python
# OLD Flask pattern:
@app.route('/api/stock/master-unified', methods=['GET'])
def get_stock_master_unified():
    # 50 lines of code
    # Direct database access
    # In-memory session state
    
# NEW Flask pattern:
@stock_bp.route('/master-unified', methods=['GET'])
def get_stock_master_unified():
    # Use unified_session_manager for sessions
    # Use unified_ai_client for AI calls
    # Same business logic
```

### Step 2: Update Dependencies
```python
# Remove OLD imports:
from anthropic import Anthropic  # ❌
from some_old_module import old_function  # ❌

# Add NEW imports:
from core.unified_session_manager import session_manager  # ✅
from core.unified_ai_client import ai_client  # ✅
```

### Step 3: Test Each Route
```powershell
# After migrating each endpoint:
Invoke-WebRequest -Uri http://localhost:5001/api/stock/master-unified -Method GET
```

---

## 📝 Implementation Checklist

### Preparation (10 minutes):
- [ ] Stop all Flask processes
- [ ] Backup OLD Flask file
- [ ] Create git branch: `feature/api-migration`

### Phase 1 - Stock Routes (1 hour):
- [ ] Copy `/api/stock/master-unified` → Adapt to unified architecture
- [ ] Copy `/api/stock/create-session` → Use session_manager
- [ ] Copy `/api/stock/list-threads` → Use session_manager
- [ ] Copy `/api/stock/load-thread` → Use session_manager
- [ ] Copy `/api/stock/ai-extracted-analytics` → Database query
- [ ] Test all 5 endpoints with curl/Postman
- [ ] Test Stock Management UI in browser

### Phase 1 - Agent Routes (1 hour):
- [ ] Copy `/chat` → Adapt for Triple Agent
- [ ] Copy `/agent/<id>/start` → Use session_manager
- [ ] Copy `/stream/<id>` → SSE with unified queue
- [ ] Copy `/agent/<id>/history` → Use session_manager
- [ ] Copy `/api/agent/chat-with-document-stream` → Vision support
- [ ] Test all 5 endpoints
- [ ] Test Triple Agent UI
- [ ] Test Single Agent Viewer
- [ ] Test Data Agent Chat

### Phase 2 - Invoice Routes (1 hour):
- [ ] Create `invoice_routes.py`
- [ ] Copy invoice processing endpoints
- [ ] Register blueprint in flask_app.py
- [ ] Test invoice upload/processing

### Phase 3 - Export Routes (30 minutes):
- [ ] Create `export_routes.py`
- [ ] Copy export endpoints
- [ ] Test CSV/JSON downloads

### Testing (30 minutes):
- [ ] Test all UIs side-by-side (OLD vs NEW Flask)
- [ ] Verify feature parity
- [ ] Performance testing
- [ ] Error handling

### Documentation (15 minutes):
- [ ] Update API_MIGRATION_COMPLETE.md
- [ ] Create endpoint reference guide
- [ ] Update UI_CONNECTION_COMPLETE_SUMMARY.md

---

## 🧪 Testing Strategy

### Test 1: Health Check
```powershell
Invoke-WebRequest -Uri http://localhost:5001/health
# Should return: {"status": "healthy", ...}
```

### Test 2: Each Endpoint
```powershell
# Stock endpoints
Invoke-WebRequest -Uri http://localhost:5001/api/stock/master-unified
Invoke-WebRequest -Uri http://localhost:5001/api/stock/list-threads

# Agent endpoints
Invoke-WebRequest -Uri http://localhost:5001/chat
Invoke-WebRequest -Uri http://localhost:5001/agent/1/status
```

### Test 3: UI Integration
```
1. Open Stock Management: http://localhost:5001/stock-management
2. Click Stock AI Chat → Test chat
3. Click Stock Master → Test inventory list
4. Click Invoice Processing → Test upload

5. Open Triple Agent: http://localhost:5001/triple-agent
6. Test Agent 1, 2, 3

7. Open Single Agent: http://localhost:5001/single-agent-viewer
8. Test chat functionality
```

### Test 4: Side-by-Side Comparison
```powershell
# Terminal 1: OLD Flask
cd G_Folder ; .\restart_servers.ps1

# Terminal 2: NEW Flask
RESTARTNEW

# Compare:
# OLD: http://localhost:5000/stock-management
# NEW: http://localhost:5001/stock-management
```

---

## 📊 Estimated Timeline

| Phase | Tasks | Time | Running Total |
|-------|-------|------|---------------|
| **Prep** | Backup, branch | 10 min | 10 min |
| **Phase 1 - Stock** | 5 endpoints + testing | 1 hr | 1h 10m |
| **Phase 1 - Agent** | 5 endpoints + testing | 1 hr | 2h 10m |
| **Phase 2 - Invoice** | 3 endpoints | 1 hr | 3h 10m |
| **Phase 3 - Export** | 2 endpoints | 30 min | 3h 40m |
| **Testing** | Full integration | 30 min | 4h 10m |
| **Docs** | Update guides | 15 min | 4h 25m |

**Total**: ~4.5 hours for complete migration

---

## 🎯 Success Criteria

### Minimum (Phase 1):
- ✅ All 3 UIs load from NEW Flask
- ✅ Stock AI Chat works
- ✅ Triple Agent works
- ✅ Single Agent works
- ✅ Basic stock inventory visible

### Target (Phase 1 + 2):
- ✅ Full Stock Management features
- ✅ Invoice processing works
- ✅ Thread management works
- ✅ File uploads work

### Ideal (All Phases):
- ✅ Feature parity with OLD Flask
- ✅ All endpoints migrated
- ✅ Shopify integration working
- ✅ Export features working

---

## 💡 Next Steps

**Choose Your Approach**:

### Option 1: Quick Win (1 hour)
Focus on Phase 1 HIGH priority endpoints only. Get UIs working with basic features.

### Option 2: Complete Migration (4 hours)
Full migration of all endpoints. Complete feature parity.

### Option 3: Incremental (30 min sessions)
Migrate 2-3 endpoints per session over several days.

---

## 🚨 Important Notes

### Don't Direct Copy!
OLD Flask uses different patterns - adapt to NEW architecture:
- Use `session_manager` instead of in-memory state
- Use `ai_client` instead of direct Anthropic API
- Use blueprints with proper URL prefixes
- Add proper error handling

### Test As You Go!
After each endpoint migration, test immediately before moving to next one.

### Keep OLD Flask Working!
Don't delete or break OLD Flask during migration - it's your reference and fallback.

---

**Ready to start?** 

1. **Quick approach**: I can migrate Phase 1 High Priority endpoints (2 hours)
2. **Full approach**: Complete migration in one session (4 hours)
3. **Show me how**: I'll do the first endpoint as an example

Which would you prefer?
