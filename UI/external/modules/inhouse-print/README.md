# InHouse Print Tools Module
**Hybrid Approach - 6 Intelligent Tools for SQL + Quote Management**

---

## Overview

This module provides InHouse Print capabilities to the AI agent using a **hybrid approach**:
- **3 meta-tools** for discovery and SQL flexibility
- **3 action tools** for optimized common operations

**Result:** AI gets SQL query freedom + intelligent calculator usage (not hardcoded)

---

## Tools (6 total)

### Meta-Tools (Discovery & Flexibility)

#### 1. `inhouse_get_query_library_catalog`
- Browse 50+ pre-built SQL queries
- Filter by category (Sales, Customers, Products, Stock, etc.)
- Get query parameters and examples
- Use before executing custom SQL

#### 2. `inhouse_execute_sql`
- Execute custom SQL against InHousePrintDB (SQL Server FredDEV)
- Embedded 500+ lines of schema corrections
- CRITICAL corrections: PaperSize has NO Width/Height, BindType uses BindTypeDesc, TicketNotes is PRIMARY source
- Always use `TOP 20` for safety

#### 3. `inhouse_get_calculator_requirements`
- Learn calculator parameters dynamically (not hardcoded)
- Get natural language → parameter mappings
- See historical patterns (most common values)
- Understand extraction strategies for TicketNotes

### Action Tools (Optimized Shortcuts)

#### 4. `inhouse_calculate_quote`
- Calculate quotes for all product types
- Routes to GOD calculator (flyers, business cards) or Shopify calculators
- Returns: cost_ex_gst, cost_inc_gst, cost_to_business, profit_margin, breakdown

#### 5. `inhouse_query_stock_levels`
- Quick inventory check (faster than SQL)
- Filter by stock_type, GSM, status
- Returns: current_level, reorder_point, critical_level, status

#### 6. `inhouse_get_reorder_alerts`
- Dashboard of stock shortages
- Returns: critical_count, warning_count, alert details
- Proactive stock management

---

## Architecture

```
inhouse-print/
├── manifest.json                   Module metadata
├── README.md                       This file
│
├── schema/
│   └── inhouse_tools.json          6 tool definitions (Anthropic format)
│
├── implementations/
│   └── inhouse_wrapper.py          Singleton pattern + 6 wrapper functions
│
└── backend/                        (Points to quote-calculator/backend)
    └── README.md                   Backend location info
```

**Backend files** are in `../quote-calculator/backend/` (reused, not duplicated)

---

## How It Works

### 1. Registry Auto-Discovery
- `registry_v3.py` scans `UI/external/modules/*/schema/*.json`
- Finds `inhouse_tools.json` and loads 6 tools
- Total tools: 622 → 628

### 2. Singleton Pattern
- First tool call creates `ToolUseAgent` instance
- Expensive initialization done once:
  - SQL Server connection (FredDEV)
  - SQLite connection (stock_data.db)
  - Calculator (6,277 lines)
  - Query library (5,042 lines)
- All subsequent calls reuse same instance

### 3. Wrapper Functions
- 6 Python functions in `inhouse_wrapper.py`
- Each routes to `agent._execute_client_tool(tool_name, params)`
- Backend handles actual execution

### 4. Context Routing
- Quote requests use `context='quote_agent'`
- Routes to Viki prompt (`viki_inhouse_agent.txt`)
- Viki has SQL schema knowledge + calculator workflows

---

## Integration Points

### Flask Route
- `/api/agent/quote` - Quote assistant endpoint
- Calls `agent_worker` with `context='quote_agent'`
- Uses Viki system prompt

### System Prompt
- **General requests:** `data_agent_chat` (default)
- **Quote requests:** `viki_inhouse_agent` (SQL + calculator guidance)
- Located: `AI_infrastructure/prompts/viki_inhouse_agent.txt`

### Agent Worker
- `agent_worker.py` checks `context` parameter
- If `context == 'quote_agent'`: loads Viki prompt
- Otherwise: loads default data_agent prompt

---

## Example AI Flows

### Flow 1: Simple Quote
```
User: "Quote for 1000 business cards"

AI:
1. inhouse_get_calculator_requirements('business_cards')
   → Learns: needs quantity, stock_type, sides, celloglaze, artworks
   → Historical: satin_350gsm + 2_side_matt most common

2. inhouse_calculate_quote('business_cards', {
     quantity: 1000,
     stock_type: 'satin_350gsm',
     sides: 2,
     celloglaze: '2_side_matt',
     artworks: 1
   })
   → Returns: $107.80 inc GST

Response: "Premium Business Cards (350GSM Satin, Matt Cello both sides): $107.80 inc GST"
```

### Flow 2: Quote with Historical Context
```
User: "Quote for John's usual business cards, 2000 this time"

AI:
1. inhouse_get_query_library_catalog()
   → Finds: customer_order_history query

2. inhouse_execute_sql(
     "SELECT TOP 5 jt.TicketNotes, jt.QTY
      FROM JobTickets jt
      JOIN Orders o ON jt.OrderID = o.OrderID
      WHERE o.ClientName LIKE '%John%'
      ORDER BY o.OrderDate DESC"
   )
   → Returns: "350gsm Satin, Matt Cello Both Sides, Double sided"

3. inhouse_get_calculator_requirements('business_cards')
   → Maps: "Matt Cello Both Sides" → celloglaze='2_side_matt'

4. inhouse_calculate_quote(...)
   → Returns: $189.50 inc GST

Response: "Based on John's previous orders (350GSM Satin with Matt Cello both sides), 
          2,000 cards will be $189.50 inc GST. His previous 1,000 order was $107.80."
```

### Flow 3: Quote with Stock Check
```
User: "Quote for 5000 cards and check stock"

AI:
1. inhouse_calculate_quote(...) → $445.00 inc GST
2. inhouse_query_stock_levels({stock_type: 'Satin', gsm: 350})
   → Returns: 5,000 sheets available, status: 'ok'

Response: "Quote: $445.00 inc GST. Stock: 5,000 sheets of 350GSM Satin available 
          (sufficient). Note: This will use most stock - consider reordering."
```

---

## Testing

### Test 1: Verify Tools Load
```powershell
cd C:\Users\gpoli\GIT\AI_agents
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); inhouse = [t for t in r.tools if 'inhouse' in t]; print(f'InHouse tools: {len(inhouse)}'); print(inhouse)"
```
**Expected:** `InHouse tools: 6`

### Test 2: Query Catalog
```powershell
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); result = r.execute_tool('inhouse_get_query_library_catalog'); print(f'Queries: {len(result[\"queries\"])}')"
```
**Expected:** `Queries: 50+`

### Test 3: Calculate Quote
```powershell
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); result = r.execute_tool('inhouse_calculate_quote', product_type='business_cards', parameters={'quantity':1000, 'stock_type':'satin_350gsm', 'sides':2, 'celloglaze':'2_side_matt', 'artworks':1}); print(f'Quote: \${result.get(\"cost_inc_gst\", 0):.2f}')"
```
**Expected:** `Quote: $107.80`

### Test 4: Flask Route
```powershell
curl -X POST http://localhost:5001/api/agent/quote -H "Content-Type: application/json" -d "{\"message\": \"Get query catalog\"}"
```
**Expected:** AI returns query catalog via `inhouse_get_query_library_catalog`

---

## Benefits

### vs 15-Tool Plugin:
✅ **60% fewer tools** (6 vs 15) = faster discovery  
✅ **SQL freedom** - AI can query anything, not just predefined  
✅ **Dynamic learning** - calculator requirements not hardcoded  
✅ **More intelligent** - AI learns from query catalog  

### vs 4 Meta-Tools Only:
✅ **Faster common operations** - stock check = 1 call (not SQL + parse)  
✅ **Better UX** - optimized shortcuts for frequent tasks  
✅ **Reduced API calls** - action tools are optimized  

---

## Dependencies

### Python Packages
- `anthropic` - AI SDK
- `pyodbc` - SQL Server connection
- `sqlite3` - Stock database
- `pandas` - Data manipulation

### Databases
- **SQL Server:** `FredDEV` (InHousePrintDB) - Orders, JobTickets, Products
- **SQLite:** `stock_data.db` - Inventory (219 AI-extracted jobs)

### Configuration
- `config/database-config.json` - Database connection settings

---

## Troubleshooting

**Issue:** Tools not loading
- Check `inhouse_tools.json` exists in `schema/`
- Verify JSON is valid
- Restart Flask server

**Issue:** Tool execution fails
- Check `database-config.json` exists
- Verify SQL Server FredDEV is accessible
- Check `stock_data.db` exists in backend

**Issue:** Context routing not working
- Check `viki_inhouse_agent.txt` exists in `prompts/`
- Verify agent_worker.py has context routing
- Check Flask logs for "Using InHouse Print context"

---

## Documentation

- **Implementation Plan:** `HYBRID_INTEGRATION_IMPLEMENTATION_PLAN.md` (836 lines)
- **Quick Guide:** `HYBRID_APPROACH_QUICK_GUIDE.md` (checklist)
- **Tool Design:** `HYBRID_APPROACH_6_TOOLS.md` (rationale + examples)
- **Dependencies:** `G_FOLDER_KEY_DEPENDENCIES.md` (15 files mapped)

---

## Status

✅ **Module structure created**  
⏳ **Schema file pending** (Phase 1)  
⏳ **Wrapper file pending** (Phase 2)  
⏳ **System prompt pending** (Phase 4)  
⏳ **Flask integration pending** (Phase 5-6)  
⏳ **Testing pending** (Phase 7)  

**Next:** Create `schema/inhouse_tools.json` with 6 tool definitions

---

**Created:** November 4, 2025  
**Version:** 1.0.0  
**Status:** Module structure complete, implementation pending
