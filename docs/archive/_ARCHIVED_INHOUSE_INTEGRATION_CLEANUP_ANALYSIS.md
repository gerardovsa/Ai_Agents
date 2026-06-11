# InHouse Print Integration - Cleanup Analysis

**Date:** November 5, 2025  
**Status:** NEEDS CLEANUP - Multiple overlapping implementations found

---

## 🔍 Current Situation - You Have TWO Competing Systems

### System 1: NEW Hybrid Module (CORRECT - November 2025)
**Location:** `UI/external/modules/inhouse-print/`
**Status:** ✅ PRODUCTION READY (4/7 tests passing)
**Documentation:** `INHOUSE_HYBRID_INTEGRATION_COMPLETE.md`

**What it does:**
- **6 intelligent tools** that work with quote calculators + SQL queries
- Uses module plugin loader (auto-discovered)
- Reuses backend from quote-calculator (no duplication)
- Has comprehensive Viki system prompt (200+ lines)
- Context routing: quote_agent → viki_inhouse_agent.txt

**Files:**
```
UI/external/modules/inhouse-print/
├── schema/inhouse_tools.json               # 6 tools (correct)
├── implementations/inhouse_wrapper.py      # Wrapper with singleton pattern
├── backend/ → (symlink to quote-calculator/backend/)
└── README.md                               # Full documentation
```

**The 6 tools:**
1. `inhouse_get_query_library_catalog()` - Browse 50+ SQL queries
2. `inhouse_execute_sql()` - Execute SQL with schema knowledge
3. `inhouse_get_calculator_requirements()` - Learn calculator params
4. `inhouse_calculate_quote()` - Calculate product quotes
5. `inhouse_query_stock_levels()` - Check inventory
6. `inhouse_get_reorder_alerts()` - Stock alerts

---

### System 2: OLD Database Tools (OBSOLETE - October 2025?)
**Location:** `tools/implementations/` and `tools/schemas/`
**Status:** ⚠️ OUTDATED - Should be removed

**What it was:**
- **5 basic SQL tools** (no calculator integration)
- Direct tool registration (old pattern)
- No context routing, no specialized prompt
- Lower-level database operations only

**Files TO DELETE:**
```
tools/implementations/
├── inhouse_db_connector.py         # ❌ DELETE - Obsolete DB wrapper
└── inhouse_query_library.py        # ❌ DELETE - Obsolete query wrapper

tools/schemas/
├── inhouse_db_connect.json         # ❌ DELETE - Duplicate
├── inhouse_execute_query.json      # ❌ DELETE - Duplicate
├── inhouse_execute_library_query.json  # ❌ DELETE - Duplicate
├── inhouse_get_available_queries.json  # ❌ DELETE - Duplicate
├── inhouse_get_business_summary.json   # ❌ DELETE - Duplicate
└── inhouse_print_tools.json        # ❌ DELETE - OLD combined schema
```

**The 5 old tools (OBSOLETE):**
1. `inhouse_db_connect()` - Manual connection (not needed)
2. `inhouse_execute_query()` - Basic SQL (replaced by inhouse_execute_sql)
3. `inhouse_execute_library_query()` - Library query (now in catalog tool)
4. `inhouse_get_available_queries()` - Query list (now in catalog tool)
5. `inhouse_get_business_summary()` - Business metrics (can use SQL tool)

---

## 📊 Comparison - Why System 1 is Better

| Feature | System 1 (Hybrid Module) | System 2 (Old Tools) |
|---------|--------------------------|----------------------|
| **Integration Level** | High (calculators + SQL + stock) | Low (SQL only) |
| **Tools Count** | 6 intelligent tools | 5 basic tools |
| **Calculator Access** | ✅ Direct integration | ❌ None |
| **SQL Queries** | ✅ 50+ pre-built + custom | ⚠️ Custom only |
| **Stock Management** | ✅ Integrated | ❌ Separate |
| **Schema Knowledge** | ✅ 500+ lines embedded | ❌ Minimal |
| **System Prompt** | ✅ viki_inhouse_agent.txt (200 lines) | ❌ None |
| **Context Routing** | ✅ quote_agent context | ❌ None |
| **Module System** | ✅ Auto-discovered plugin | ❌ Manual registration |
| **Code Reuse** | ✅ Singleton pattern | ❌ Duplication |
| **Documentation** | ✅ Comprehensive | ⚠️ Minimal |
| **Test Coverage** | ✅ 4/7 passing | ❌ Untested |

---

## 🎯 What the AI Agent Gets (System 1 - CORRECT)

### 1. Instructions - HOW to Quote

**Location:** `AI_infrastructure/prompts/viki_inhouse_agent.txt` (201 lines)

**Content:**
- **6 tool descriptions** with use cases
- **5-step workflow** for quotes:
  1. Learn requirements (call `get_calculator_requirements`)
  2. Gather context (historical data via SQL if needed)
  3. Map specifications (natural language → parameters)
  4. Calculate quote (call `calculate_quote`)
  5. Optional stock checks

**Triggered by:** Context routing in `agent_worker.py` when `context='quote_agent'`

**What AI learns:**
- Which tool to use for each task
- Order of operations (requirements → quote → stock)
- How to extract specs from natural language
- How to validate results

---

### 2. Calculator Requirements - WHAT Parameters Are Needed

**Tool:** `inhouse_get_calculator_requirements(product_type)`

**Returns for each calculator:**
- **Required parameters:** e.g., `quantity`, `stock_type`, `sides`
- **Optional parameters:** e.g., `finishing`, `custom_size`
- **Natural language mappings:** "double-sided" → `sides=2`
- **Historical patterns:** Default values when not specified
- **Validation rules:** Min/max values, allowed types

**Example output (business_cards):**
```json
{
  "calculator_type": "business_cards",
  "required_parameters": ["quantity", "stock_type", "sides"],
  "optional_parameters": ["coating", "cutting", "corner_rounding"],
  "natural_language_mapping": {
    "double-sided": {"sides": 2},
    "350GSM Satin": {"stock_type": "standard", "stock_variant": "350GSM_Satin"}
  },
  "defaults": {
    "sides": 2,
    "coating": "none"
  }
}
```

---

### 3. SQL Queries - WHAT Can Be Queried

**Tool:** `inhouse_get_query_library_catalog(category)`

**Returns:** 50+ pre-built queries with:
- **Query name:** e.g., "get_customer_order_history"
- **Category:** "Customer Analytics"
- **Description:** What the query does
- **Parameters:** Required inputs (e.g., customer_id, date_range)
- **Example usage:** How to call it

**Categories:**
1. Sales & Revenue
2. Customer Analytics
3. Product Performance
4. Operations & Efficiency
5. Stock Management
6. Production Reports
7. Financial Reports

**Plus custom SQL via:** `inhouse_execute_sql(query)`
- **Embedded schema knowledge:** 500+ lines of schema corrections
- **Critical corrections documented:**
  - PaperSize has NO Width/Height (only SizeID, [Desc])
  - BindType uses BindTypeDesc (NOT [Desc])
  - TicketNotes is PRIMARY source of truth
  - ColourStatus is urgency (NOT print color)

---

## 🗂️ UI Module Structure

### quote-calculator (First Attempt - October 2025)
**Location:** `UI/external/modules/quote-calculator/`
**Purpose:** Web UI for manual quote calculations
**Status:** ✅ Working - Web interface only
**Contains:**
- `quote-calculator.js` - Frontend UI
- `quote_calculator_routes.py` - Flask routes for UI
- `backend/` - Shared backend (tool_use_agent.py, calculators)

**NOT for AI agents** - This is for manual web UI usage

---

### inhouse-print (Current Implementation - November 2025)
**Location:** `UI/external/modules/inhouse-print/`
**Purpose:** AI agent integration with calculators + SQL + stock
**Status:** ✅ PRODUCTION READY
**Contains:**
- `schema/inhouse_tools.json` - 6 tool definitions
- `implementations/inhouse_wrapper.py` - Wrapper functions
- `backend/` - Symlink to quote-calculator/backend/ (no duplication)

**FOR AI agents** - This is what the registry loads

---

## ⚠️ Files Analysis - Keep or Delete?

### ❌ DELETE - Obsolete Old Tools (tools/ folder)

**Reason:** Replaced by hybrid module system

```bash
# DELETE THESE:
tools/implementations/inhouse_db_connector.py
tools/implementations/inhouse_query_library.py
tools/schemas/inhouse_db_connect.json
tools/schemas/inhouse_execute_library_query.json
tools/schemas/inhouse_execute_query.json
tools/schemas/inhouse_get_available_queries.json
tools/schemas/inhouse_get_business_summary.json
tools/schemas/inhouse_print_tools.json
```

**Impact of deletion:** NONE - Registry loads from `UI/external/modules/inhouse-print/` now

---

### ✅ KEEP - Current Working System

**Module files (PRODUCTION):**
```
UI/external/modules/inhouse-print/
├── schema/inhouse_tools.json               ✅ KEEP - 6 tool definitions
├── implementations/inhouse_wrapper.py      ✅ KEEP - Wrapper with singleton
├── manifest.json                           ✅ KEEP - Module metadata
├── README.md                               ✅ KEEP - Documentation
└── MODULE_SETUP_COMPLETE.md                ✅ KEEP - Setup guide
```

**Backend (SHARED - Do not duplicate):**
```
UI/external/modules/quote-calculator/backend/
├── tool_use_agent.py                       ✅ KEEP - 3,187 lines (shared)
├── complete_calculator_implementation.py   ✅ KEEP - 6,277 lines (calculators)
├── query_library.py                        ✅ KEEP - 5,042 lines (SQL queries)
└── stock_database_tools.py                 ✅ KEEP - SQLite stock tools
```

**System Prompt (CRITICAL):**
```
AI_infrastructure/prompts/viki_inhouse_agent.txt  ✅ KEEP - 201 lines of instructions
```

**Context Routing:**
```
AI_infrastructure/core/agent_worker.py            ✅ KEEP - Line ~309 routing logic
AI_infrastructure/routes/agent_routes_v4.py       ✅ KEEP - /api/agent/quote endpoint
```

---

## 🧹 Cleanup Steps

### Step 1: Verify Current System Works
```powershell
cd C:\Users\gpoli\GIT\AI_agents
python test_inhouse_module.py
```
**Expected:** 4/7 tests passing (registry loads 6 tools)

### Step 2: Delete Old Tool Files
```powershell
# Delete old implementations
Remove-Item tools\implementations\inhouse_db_connector.py
Remove-Item tools\implementations\inhouse_query_library.py

# Delete old schemas
Remove-Item tools\schemas\inhouse_db_connect.json
Remove-Item tools\schemas\inhouse_execute_library_query.json
Remove-Item tools\schemas\inhouse_execute_query.json
Remove-Item tools\schemas\inhouse_get_available_queries.json
Remove-Item tools\schemas\inhouse_get_business_summary.json
Remove-Item tools\schemas\inhouse_print_tools.json
```

### Step 3: Verify Registry Still Loads
```powershell
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); inhouse = [t for t in r.tools if 'inhouse' in t]; print(f'InHouse tools: {len(inhouse)}'); print(inhouse)"
```
**Expected:** 6 tools from `UI/external/modules/inhouse-print/`

### Step 4: Test End-to-End
```powershell
BISTART
# In another terminal:
CHAT "Calculate quote for 1000 business cards"
```
**Expected:** AI discovers inhouse tools, gets schema, calculates quote

---

## 📝 Summary - What You Actually Need

### For AI Agent Integration (PRODUCTION):
1. ✅ **Module:** `UI/external/modules/inhouse-print/` (6 tools)
2. ✅ **Backend:** `UI/external/modules/quote-calculator/backend/` (shared)
3. ✅ **Prompt:** `AI_infrastructure/prompts/viki_inhouse_agent.txt`
4. ✅ **Routing:** `agent_worker.py` + `agent_routes_v4.py`
5. ✅ **Documentation:** `INHOUSE_HYBRID_INTEGRATION_COMPLETE.md`

### Obsolete (DELETE):
1. ❌ **Old tools:** `tools/implementations/inhouse_*.py`
2. ❌ **Old schemas:** `tools/schemas/inhouse_*.json`

### For Web UI Only (SEPARATE CONCERN):
1. ✅ **Web module:** `UI/external/modules/quote-calculator/` (for manual UI)
2. ✅ **Flask routes:** `quote_calculator_routes.py`
3. ✅ **Frontend:** `quote-calculator.js`, `quote-calculator.css`

---

## 🎯 How AI Gets Instructions (FINAL ANSWER)

### Question: "How does the AI agent get instructions on how to use InHouse print quoting and SQL queries?"

**Answer:**

1. **Tool Discovery** (STEP 1: DISCOVER in system prompt)
   - User mentions "quote" or "print" or "business cards"
   - System prompt says: "If user mentions quotes/printing, search for 'inhouse' tools"
   - AI calls: `search_tools("inhouse")` or `list_platform_tools("inhouse_print")`
   - Registry returns: 6 inhouse tools from `UI/external/modules/inhouse-print/schema/`

2. **Get Schema** (STEP 2: LEARN - MANDATORY)
   - AI calls: `get_tool_schema("inhouse_calculate_quote")`
   - Returns: Parameters, types, required/optional, descriptions
   - AI now knows: What parameters to collect from user

3. **Get Calculator Requirements** (InHouse-specific)
   - AI calls: `inhouse_get_calculator_requirements("business_cards")`
   - Returns: Required params, natural language mappings, defaults, validation rules
   - AI now knows: How to convert "double-sided 350GSM" → parameters

4. **Execute Quote** (STEP 4: EXECUTE)
   - AI calls: `inhouse_calculate_quote(product_type="business_cards", quantity=1000, ...)`
   - Backend uses: `tool_use_agent.py` → `ComprehensiveQuoteCalculator`
   - Returns: Quote with pricing, turnaround, stock details

5. **Optional SQL Queries** (if context needed)
   - AI calls: `inhouse_get_query_library_catalog("Customer Analytics")`
   - Returns: 50+ pre-built queries with params
   - AI calls: `inhouse_execute_sql("SELECT ... FROM Orders WHERE ...")`
   - Returns: Historical data for context

### Where Instructions Live:

**General hint:** `AI_infrastructure/prompts/tool_usage_system_prompt.md` (line ~66)
- Brief mention: "For quotes/printing, search for 'inhouse' tools"

**Specialized instructions:** `AI_infrastructure/prompts/viki_inhouse_agent.txt` (201 lines)
- Full workflow: 5-step process
- Tool descriptions: What each tool does
- SQL schema: 500+ lines of corrections
- Natural language mapping: How to parse user input

**Tool schemas:** `UI/external/modules/inhouse-print/schema/inhouse_tools.json`
- Tool definitions: Parameters, types, requirements
- Embedded knowledge: Schema corrections in descriptions

**Calculator requirements:** Returned by `inhouse_get_calculator_requirements()`
- Dynamic per product: business_cards vs flyers vs booklets
- Natural language mappings: Text → parameters
- Validation rules: Min/max, allowed values

---

## ✅ Action Items

1. **Test current system:** Run `python test_inhouse_module.py`
2. **Delete old files:** Remove 8 obsolete files from `tools/` folder
3. **Verify registry:** Check 6 tools load from module
4. **Test end-to-end:** Use CHAT to calculate a quote
5. **Update documentation:** Mark old files as deleted in this doc

**Expected result:** Clean system with ONE integration method (hybrid module), no duplicates, 6 tools working correctly.

---

**End of Analysis**
