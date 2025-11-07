# Hybrid Approach - Quick Implementation Guide
**TL;DR for Implementing 6 InHouse Tools**

---

## 📋 What We're Building

**Goal:** Add 6 intelligent InHouse Print tools instead of 15 predefined ones

**Tools:**
1. `inhouse_get_query_library_catalog` - Browse 50+ SQL queries
2. `inhouse_execute_sql` - Execute custom SQL with schema knowledge
3. `inhouse_get_calculator_requirements` - Learn calculator parameters dynamically
4. `inhouse_calculate_quote` - Calculate product quotes
5. `inhouse_query_stock_levels` - Check inventory
6. `inhouse_get_reorder_alerts` - Get stock shortage alerts

**Result:** AI agent gets SQL freedom + calculator intelligence (622 → 628 tools)

---

## ⚡ Implementation Checklist

### ✅ Phase 1: Create Schema (1 hour)
- [ ] Create `UI/external/modules/quote-calculator/schema/inhouse_tools.json`
- [ ] Add 6 tool definitions (meta + action tools)
- [ ] Test: `python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print(len([t for t in r.tools if 'inhouse' in t]))"`
- [ ] Expected: `6`

### ✅ Phase 2: Create Wrapper (2 hours)
- [ ] Create `UI/external/modules/quote-calculator/implementations/inhouse_wrapper.py`
- [ ] Implement singleton `_get_agent()` pattern
- [ ] Add 6 wrapper functions routing to backend `tool_use_agent.py`
- [ ] Test: `python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); result = r.execute_tool('inhouse_get_query_library_catalog'); print(len(result['queries']))"`
- [ ] Expected: `50+`

### ✅ Phase 3: Verify Registry (15 min)
- [ ] Test all 6 tools load: `python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print(f'Total: {len(r.tools)}')"`
- [ ] Expected: `628 tools (622 + 6)`
- [ ] Test tool execution for each tool
- [ ] Verify Anthropic format conversion

### ✅ Phase 4: Create Viki Prompt (1 hour)
- [ ] Create `AI_infrastructure/prompts/viki_inhouse_agent.txt`
- [ ] Include: SQL schema corrections, workflow guide, tool usage examples
- [ ] Test: `Test-Path "AI_infrastructure\prompts\viki_inhouse_agent.txt"`

### ✅ Phase 5: Add Context Routing (1 hour)
- [ ] Modify `AI_infrastructure/core/agent_worker.py` line ~309
- [ ] Add `if context == 'quote_agent': prompt_name = 'viki_inhouse_agent'`
- [ ] Test: Start Flask and check logs for context routing message

### ✅ Phase 6: Add Flask Route (1 hour)
- [ ] Add `/api/agent/quote` route in `agent_routes_v4.py`
- [ ] Route calls `agent_worker` with `context='quote_agent'`
- [ ] Test: `curl -X POST http://localhost:5001/api/agent/quote -H "Content-Type: application/json" -d '{"message": "Get query catalog"}'`

### ✅ Phase 7: End-to-End Testing (2 hours)
- [ ] Test 1: Registry loads 628 tools
- [ ] Test 2: Query catalog returns 50+ queries
- [ ] Test 3: SQL execution works
- [ ] Test 4: Calculator requirements returns parameters
- [ ] Test 5: Quote calculation returns pricing
- [ ] Test 6: Stock levels works
- [ ] Test 7: Reorder alerts works
- [ ] Test 8: Flask route responds correctly
- [ ] Test 9: End-to-end quote flow completes
- [ ] Test 10: Context routing uses Viki prompt

---

## 🎯 Key Design Decisions

### Why 6 Tools Instead of 15?
- **Meta-tools** (3) give AI discovery capability:
  - Browse 50+ queries without 50 tool definitions
  - Execute ANY SQL query (not limited to predefined)
  - Learn calculator requirements dynamically

- **Action tools** (3) optimize common operations:
  - Calculate quotes (core functionality)
  - Check stock (faster than SQL)
  - Get alerts (dashboard feature)

### Why Singleton Pattern?
- ToolUseAgent initialization is expensive:
  - Database connections (SQL Server + SQLite)
  - 6,277-line calculator
  - 5,042-line query library
- Singleton creates once, reuses forever

### Why Context Routing?
- Quote requests need specialized knowledge:
  - SQL schema corrections (500+ lines)
  - Calculator workflows
  - TicketNotes extraction patterns
- Viki prompt provides this domain expertise

---

## 📂 Files to Create/Modify

### Create (3 files):
1. `UI/external/modules/quote-calculator/schema/inhouse_tools.json` (6 tool definitions)
2. `UI/external/modules/quote-calculator/implementations/inhouse_wrapper.py` (singleton + 6 functions)
3. `AI_infrastructure/prompts/viki_inhouse_agent.txt` (SQL guidance + workflow)

### Modify (2 files):
1. `AI_infrastructure/core/agent_worker.py` (add context routing, ~5 lines)
2. `AI_infrastructure/routes/agent_routes_v4.py` (add /quote route, ~100 lines)

**Reuse (no changes needed):**
- All backend files in `UI/external/modules/quote-calculator/backend/`
- `tool_use_agent.py` used as library via wrapper

---

## 🧪 Quick Test Commands

```powershell
# Test 1: Check tool count
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print(f'Tools: {len(r.tools)} (should be 628)')"

# Test 2: Query catalog
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); result = r.execute_tool('inhouse_get_query_library_catalog'); print(f'Queries: {len(result[\"queries\"])}')"

# Test 3: Calculate quote
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); result = r.execute_tool('inhouse_calculate_quote', product_type='business_cards', parameters={'quantity':1000, 'stock_type':'satin_350gsm', 'sides':2, 'celloglaze':'2_side_matt', 'artworks':1}); print(f'Quote: \${result.get(\"cost_inc_gst\", 0):.2f}')"

# Test 4: Flask route
curl -X POST http://localhost:5001/api/agent/quote -H "Content-Type: application/json" -d "{\"message\": \"Quote for 1000 business cards\"}"
```

---

## ⚠️ Troubleshooting

**Issue:** Tools not loading (less than 628)
- Check `inhouse_tools.json` exists in `schema/` folder
- Verify JSON is valid (use JSONLint)
- Check `inhouse_wrapper.py` exists in `implementations/` folder
- Restart Flask server

**Issue:** Tool execution fails
- Check backend path is correct in `inhouse_wrapper.py`
- Verify `database-config.json` exists
- Check SQL Server FredDEV is accessible
- Check `stock_data.db` exists in backend/

**Issue:** Context routing not working
- Check `viki_inhouse_agent.txt` exists in `prompts/`
- Verify agent_worker.py modification around line 309
- Check Flask logs for "Using InHouse Print context"
- Test with `context='quote_agent'` parameter

**Issue:** Flask route 404
- Verify route is registered in `agent_routes_v4.py`
- Check blueprint is registered in `flask_app.py`
- Restart Flask server
- Check route: `http://localhost:5001/api/agent/quote`

---

## 🔄 Rollback Plan (if needed)

```powershell
# Remove 3 new files
Remove-Item "UI\external\modules\quote-calculator\schema\inhouse_tools.json"
Remove-Item "UI\external\modules\quote-calculator\implementations\inhouse_wrapper.py"
Remove-Item "AI_infrastructure\prompts\viki_inhouse_agent.txt"

# Revert agent_worker.py (git checkout or manual)
# Revert agent_routes_v4.py (git checkout or manual)

# Restart Flask
cd AI_infrastructure
python flask_app.py

# Verify rollback
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print(f'Tools: {len(r.tools)} (should be 622)')"
```

---

## 📊 Success Metrics

Integration is complete when:
- ✅ Registry shows 628 tools (622 + 6)
- ✅ All 6 tools execute successfully
- ✅ Flask `/quote` route responds
- ✅ Context routing uses Viki prompt
- ✅ End-to-end quote flow completes
- ✅ No errors in Flask logs

---

## 🚀 Timeline

| Phase | Time | Cumulative |
|-------|------|------------|
| 1. Schema | 1 hour | 1 hour |
| 2. Wrapper | 2 hours | 3 hours |
| 3. Registry Test | 15 min | 3.25 hours |
| 4. Viki Prompt | 1 hour | 4.25 hours |
| 5. Context Routing | 1 hour | 5.25 hours |
| 6. Flask Route | 1 hour | 6.25 hours |
| 7. Testing | 2 hours | **8.25 hours** |

**Recommended:** 2 days (4 hours each)
- Day 1: Phases 1-4 (infrastructure)
- Day 2: Phases 5-7 (integration + testing)

---

## 📚 Full Documentation

See `HYBRID_INTEGRATION_IMPLEMENTATION_PLAN.md` for:
- Complete code examples for all 3 new files
- Detailed test suite (10 tests)
- Error handling patterns
- Rollback procedures
- Example AI flows

See `HYBRID_APPROACH_6_TOOLS.md` for:
- Tool design rationale
- Example AI agent flows
- Why 6 tools vs 15
- Business use cases

---

**Ready to implement?** Start with Phase 1! 🚀

**Last Updated:** November 4, 2025  
**Status:** Implementation Guide Complete
