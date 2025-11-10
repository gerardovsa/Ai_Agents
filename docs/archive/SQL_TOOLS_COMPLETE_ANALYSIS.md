# SQL Database Tools - Complete Analysis & Implementation Plan

**Date:** November 3, 2025  
**Status:** ⚠️ Partially Working - Needs db_connector connection fix

---

## Executive Summary

The SQL database tools are **90% implemented** but failing at connection time because `db_connector` module can't be imported from the expected location.

### Current Status:
- ✅ **5 SQL tools defined** in schemas
- ✅ **Implementation exists** in `tools/implementations/sql_database.py`
- ✅ **G_Folder modules exist** (db_connector, query_library, calculator, stock_tools)
- ❌ **Import failing** - `db_connector` not found in expected path
- ❌ **Path mismatch** - Looking in wrong G_Folder location

---

## Architecture Overview

```
AI Agent Request
      ↓
tools/implementations/sql_database.py (Wrapper)
      ↓
Import from: C:\Users\gpoli\GIT\In_House_SQL\
      ├── db_connector.py          (Database connection - SQL Server via pyodbc)
      ├── query_library.py         (5,042 lines - 100+ pre-built queries)
      ├── complete_calculator_implementation.py  (Quote calculator)
      └── stock_database_tools.py  (Stock inventory tools)
      ↓
SQL Server Database (via ODBC Driver 17/18)
```

---

## File Locations

### Source Files (In_House_SQL Project):

| File | Location | Lines | Purpose |
|------|----------|-------|---------|
| `db_connector.py` | `C:\Users\gpoli\GIT\In_House_SQL\` | 333 | SQL Server connection via pyodbc |
| `query_library.py` | `C:\Users\gpoli\GIT\In_House_SQL\` (via UI/external/modules/quote-calculator/ORIGINAL/) | 5,042 | 100+ pre-built BI queries |
| `complete_calculator_implementation.py` | In_House_SQL project | Large | Quote calculation engine |
| `stock_database_tools.py` | In_House_SQL project | Medium | Inventory management |

### AI_agents Implementation:

| File | Location | Lines | Purpose |
|------|----------|-------|---------|
| `sql_database.py` | `AI_agents/tools/implementations/` | 516 | Wrapper that imports G_Folder modules |
| `sql_database_tools.json` | `AI_agents/tools/schemas/` | ~400 | Tool definitions for registry |
| `database-config.json` | Multiple locations | Small | Database connection config |

---

## The Problem - Path Mismatch

### What sql_database.py Is Looking For:
```python
gfolder_path = root_dir.parent / "In_House_SQL" / "G_Folder"
calculator_path = gfolder_path / "Quote_Calculator"
core_path = calculator_path / "AI_Quote_Agent" / "core"
```

**Expected:** `C:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator\AI_Quote_Agent\core\`

### What Actually Exists:
```
C:\Users\gpoli\GIT\In_House_SQL\
├── db_connector.py                    ← HERE!
├── query_library.py (via UI path)     ← HERE!
└── complete_calculator_implementation.py
```

**Actual files are in root In_House_SQL directory, NOT in G_Folder subdirectory!**

---

## Available Tools (Already Defined)

### 1. db_execute_query
**Purpose:** Execute any query from the 100+ query library  
**Parameters:**
- `query_name` (required) - Name of query from library
- `parameters` (optional) - Dict of query parameters

**Example Queries Available:**
- `sales_trend_by_month` - Monthly revenue trends
- `revenue_by_product_type` - Product performance
- `top_customers_by_revenue` - Best customers
- `inventory_turnover_analysis` - Stock efficiency
- `profit_margin_by_product` - Profitability analysis
- 100+ more in query_library.py!

### 2. db_get_available_queries
**Purpose:** List all queries in the library with descriptions  
**Parameters:** None  
**Returns:** Catalog of 100+ queries with metadata

### 3. db_get_business_summary
**Purpose:** Get high-level business KPIs  
**Parameters:** None  
**Returns:**
- Total orders
- Active orders
- Total clients
- Job tickets today
- Publishing projects

### 4. db_calculate_quote
**Purpose:** Calculate printing quote with Shopify pricing  
**Parameters:**
- `product_type` - business_cards, flyers, booklets, etc.
- `quantity` - Number of items
- `specifications` - Dict with specs (stock, finish, etc.)

### 5. db_get_stock_levels
**Purpose:** Get current inventory levels and reorder alerts  
**Parameters:**
- `stock_type` (optional) - Filter by stock type
- `low_stock_only` (optional) - Show only low stock items

---

## The 100+ Query Library

The `query_library.py` file (5,042 lines!) contains:

### Sales & Revenue (20+ queries):
- Monthly/weekly/daily sales trends
- Revenue by product type
- Revenue by customer segment
- Profit margin analysis
- Sales forecasting

### Customer Analytics (15+ queries):
- Top customers by revenue
- Customer lifetime value
- Customer retention analysis
- Customer acquisition cost
- Churn prediction

### Inventory Management (15+ queries):
- Stock levels and turnover
- Reorder recommendations
- Slow-moving items
- Out-of-stock analysis
- Stock valuation

### Operational Metrics (20+ queries):
- Production efficiency
- Job ticket analysis
- Turnaround time tracking
- Quality control metrics
- Equipment utilization

### Financial Reports (15+ queries):
- Profit & loss statements
- Cash flow analysis
- Outstanding invoices
- Payment collection rates
- Cost analysis

### Product Performance (15+ queries):
- Best-selling products
- Product profitability
- Product lifecycle analysis
- Cross-sell opportunities
- Product mix optimization

---

## Database Schema (SQL Server)

### Key Tables:
- **Orders** - Customer orders with OrderID, ClientID, OrderDate, TotalPrice
- **JobTickets** - Production jobs linked to orders
- **Clients** - Customer information
- **StockItems** - Inventory tracking
- **PublishingProject** - Publishing-specific projects
- **Products** - Product catalog
- **Invoices** - Billing records

### Connection Details:
- **Type:** Microsoft SQL Server
- **Driver:** ODBC Driver 17/18 for SQL Server
- **Connection:** pyodbc with parameterized queries
- **Config:** `database-config.json` stores credentials

---

## Implementation Fix Required

### Option 1: Fix Path (Quickest - 5 minutes)

Update `sql_database.py` lines 27-31:

```python
# BEFORE (Wrong):
gfolder_path = root_dir.parent / "In_House_SQL" / "G_Folder"
calculator_path = gfolder_path / "Quote_Calculator"
core_path = calculator_path / "AI_Quote_Agent" / "core"

# AFTER (Correct):
inhouse_sql_path = root_dir.parent / "In_House_SQL"
# Modules are in different locations:
# - db_connector.py is in root In_House_SQL/
# - query_library.py is in UI/external/modules/quote-calculator/ORIGINAL/
# - Other modules in various subdirectories
```

### Option 2: Create Unified Import Path (Better - 15 minutes)

Create a new wrapper that finds modules dynamically:

```python
def _find_module_path(module_name: str) -> Optional[Path]:
    """Dynamically find module in In_House_SQL project"""
    search_paths = [
        inhouse_sql_path,  # Root
        inhouse_sql_path / "G_Folder" / "Quote_Calculator",
        inhouse_sql_path / "UI" / "external" / "modules" / "quote-calculator" / "ORIGINAL",
        # ... other possible locations
    ]
    
    for path in search_paths:
        module_file = path / f"{module_name}.py"
        if module_file.exists():
            return path
    
    return None
```

### Option 3: Copy Files to AI_agents (Not Recommended)

Would create code duplication - BAD for maintenance.

---

## Testing Plan

Once path fix is applied:

### 1. Test Connection:
```python
from tools.registry_v3 import get_registry

registry = get_registry()

# Test 1: Get business summary
result = registry.execute_tool('db_get_business_summary')
print(result)

# Expected: {'total_orders': 1234, 'active_orders': 56, ...}
```

### 2. Test Query Execution:
```python
# Test 2: Execute a query
result = registry.execute_tool(
    'db_execute_query',
    query_name='sales_trend_by_month',
    parameters={'months': 6}
)
print(result)

# Expected: DataFrame with Month, TotalRevenue, OrderCount, etc.
```

### 3. Test Calculator:
```python
# Test 3: Calculate quote
result = registry.execute_tool(
    'db_calculate_quote',
    product_type='business_cards',
    quantity=1000,
    specifications={
        'stock_type': '350GSM Satin',
        'double_sided': True
    }
)
print(result)

# Expected: {'total_price': 125.00, 'per_unit': 0.125, ...}
```

### 4. Test Stock Tools:
```python
# Test 4: Get stock levels
result = registry.execute_tool(
    'db_get_stock_levels',
    low_stock_only=True
)
print(result)

# Expected: List of low stock items with reorder recommendations
```

---

## Integration with AI Agent Workflow

### Current 3-Step Workflow:
1. **Discover** - `search_tools("database")` → finds db_* tools
2. **Learn** - `get_tool_schema("db_execute_query")` → gets parameters
3. **Execute** - `execute_tool("db_execute_query", query_name="sales_trend_by_month", parameters={...})`

### Example AI Conversation:

**User:** "What were our sales last month?"

**AI Workflow:**
```
1. search_tools("sales") 
   → Finds: db_execute_query

2. get_tool_schema("db_execute_query")
   → Parameters: query_name, parameters

3. db_get_available_queries()
   → Finds: "monthly_revenue_trend"

4. execute_tool("db_execute_query", 
                query_name="monthly_revenue_trend",
                parameters={"months": 1})
   → Returns: Sales data for last month

5. AI responds: "Last month's sales were $X with Y orders..."
```

---

## Benefits Once Working

### For Business Users:
- ✅ Natural language queries: "Who are my top 10 customers?"
- ✅ Instant reports: "Show me inventory that needs reordering"
- ✅ Trend analysis: "What's our sales trend over the last 6 months?"
- ✅ Quote generation: "Quote 1000 business cards, double-sided, 350GSM"

### For Developers:
- ✅ 100+ pre-built, tested queries
- ✅ No SQL knowledge required to use
- ✅ Parameterized queries (SQL injection safe)
- ✅ Consistent error handling
- ✅ Built-in visualization metadata

### For AI Agent:
- ✅ Structured data access
- ✅ Query discovery system
- ✅ Parameter validation
- ✅ Result formatting

---

## Next Steps

### Immediate (Now):
1. ✅ Fix path in `sql_database.py` to find In_House_SQL modules
2. ✅ Test database connection
3. ✅ Verify all 5 tools load correctly

### Short-term (Today):
4. ✅ Test each tool with sample data
5. ✅ Add error handling for common issues
6. ✅ Document query catalog for AI agent
7. ✅ Create usage examples

### Medium-term (This Week):
8. ✅ Add more tools from query_library
9. ✅ Create visualization tools
10. ✅ Add caching for frequently-used queries
11. ✅ Performance optimization

---

## Conclusion

The SQL database tools are **ALMOST READY** - just need the import path fixed. Once that's done, you'll have:

- 🔥 **5 powerful database tools** 
- 🔥 **100+ pre-built queries**
- 🔥 **Quote calculator integration**
- 🔥 **Stock management**
- 🔥 **Business intelligence**

All accessible via natural language through the AI agent!

**Should I fix the import paths now?**
