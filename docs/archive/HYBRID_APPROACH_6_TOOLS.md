# Hybrid Approach - 6 InHouse Tools
**Recommended implementation for G_FOLDER integration**

---

## Tool Definitions (6 tools total)

### **META-TOOLS (3 tools - Discovery & Flexibility)**

#### 1. `inhouse_get_query_library_catalog`
**Purpose:** Browse 50+ pre-built SQL queries with descriptions and parameters

**Parameters:** 
- `category` (optional): Filter by category (Sales & Revenue, Customer Analytics, etc.)

**Returns:**
```json
{
  "queries": [
    {
      "name": "customer_order_history",
      "category": "Customer Analytics",
      "description": "Get customer's order history with specifications",
      "parameters": ["customer_name", "months_back"],
      "example": "Find what John ordered in last 6 months"
    },
    // ... 50+ more queries
  ]
}
```

**Use Case:** AI discovers what queries are available before deciding what data to fetch

---

#### 2. `inhouse_execute_sql`
**Purpose:** Execute custom SQL with embedded schema knowledge (500+ lines)

**Parameters:**
- `query` (string): SQL query to execute

**Schema Guidance (Embedded in Tool Description):**
```sql
-- CRITICAL CORRECTIONS:
-- PaperSize: NO Width/Height columns! Only SizeID and [Desc]
-- BindType: Uses BindTypeDesc (NOT [Desc]!)
-- ColourStatus: Production urgency (NOT print color!)
-- TicketNotes: PRIMARY source of truth when structured columns NULL

-- CORRECT QUERY TEMPLATE:
SELECT TOP 20
    jt.TicketNotes AS ProductionNotes,  -- PRIMARY source
    ps.[Desc] AS PaperSize,              -- "A4", "BC - 90x55"
    bt.BindTypeDesc AS BindType,         -- NOT bt.[Desc]!
    jt.QTY, jt.Cost, o.ClientName
FROM JobTickets jt
JOIN Orders o ON jt.OrderID = o.OrderID
LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
WHERE o.ClientName LIKE '%[name]%'
ORDER BY o.OrderDate DESC
```

**Returns:** Query results as JSON array

**Use Case:** AI constructs custom SQL for complex analysis or data not in query library

---

#### 3. `inhouse_get_calculator_requirements`
**Purpose:** Get complete guidance for using each calculator

**Parameters:**
- `product_type` (string): business_cards, flyers, perfect_bound_books, etc.

**Returns:**
```json
{
  "product_type": "business_cards",
  "parameters": {
    "quantity": {
      "type": "integer",
      "required": true,
      "common_values": [250, 500, 1000, 2000, 5000]
    },
    "stock_type": {
      "type": "string",
      "required": true,
      "options": ["satin_300gsm", "satin_350gsm", "kingkong_420gsm", "ecostar_350gsm"]
    },
    // ... all parameters
  },
  "natural_language_mapping": {
    "350gsm satin": "satin_350gsm",
    "matt cello both sides": "celloglaze='2_side_matt'",
    "double sided": "sides=2"
  },
  "historical_patterns": {
    "most_common": {
      "stock_type": "satin_350gsm",
      "celloglaze": "2_side_matt"
    }
  },
  "extraction_strategy": "Parse TicketNotes for: '350gsm', 'Satin', 'Matt Cello', 'Double sided'"
}
```

**Use Case:** AI learns how to use calculator + how to extract specs from database

---

### **ACTION TOOLS (3 tools - High-Use Operations)**

#### 4. `inhouse_calculate_quote`
**Purpose:** Execute quote calculation (routes to GOD or Shopify calculators)

**Parameters:**
- `product_type` (string): Calculator type
- `parameters` (object): Product-specific parameters from requirements tool

**Returns:**
```json
{
  "success": true,
  "cost_ex_gst": 98.00,
  "cost_inc_gst": 107.80,
  "cost_to_business": 65.23,
  "profit_margin": 32.77,
  "specifications": { /* full specs */ },
  "breakdown": { /* cost breakdown */ }
}
```

**Use Case:** Calculate quotes after gathering specifications

---

#### 5. `inhouse_query_stock_levels`
**Purpose:** Quick inventory check (avoids SQL query + parsing)

**Parameters:**
- `filters` (object, optional):
  - `stock_type` (string): e.g., "Satin"
  - `gsm` (integer): e.g., 350
  - `status` (string): "critical" | "low" | "ok"

**Returns:**
```json
{
  "stocks": [
    {
      "stock_id": 44,
      "description": "Satin 350GSM",
      "current_level": 5000,
      "reorder_point": 2000,
      "critical_level": 500,
      "status": "ok"
    }
  ]
}
```

**Use Case:** Quick stock checks without SQL knowledge

---

#### 6. `inhouse_get_reorder_alerts`
**Purpose:** Quick stock shortage alerts

**Parameters:** None

**Returns:**
```json
{
  "alerts": [
    {
      "stock_id": 12,
      "description": "Gloss 300GSM",
      "current_level": 450,
      "reorder_point": 2000,
      "alert_level": "CRITICAL",
      "alert_date": "2025-11-03"
    }
  ],
  "critical_count": 2,
  "warning_count": 5
}
```

**Use Case:** Quick dashboard of stock issues

---

## Why These 6 Tools?

### Meta-Tools Rationale:
1. **`get_query_library_catalog`**: AI discovers 50+ queries without 50 tool definitions
2. **`execute_sql`**: AI can query anything, not limited to predefined queries
3. **`get_calculator_requirements`**: AI learns how to use calculators dynamically

### Action-Tools Rationale:
4. **`calculate_quote`**: Core functionality - used in 80% of requests
5. **`query_stock_levels`**: High-use, faster than SQL (1 call vs query + parse)
6. **`get_reorder_alerts`**: Dashboard feature, saves SQL complexity

### Tools We DIDN'T Include (and why):
- ❌ `get_available_queries`: Redundant (catalog returns same info)
- ❌ `get_query_from_library`: AI can use catalog + execute_sql
- ❌ `get_stock_transactions`: Low-use, can use execute_sql if needed
- ❌ `update_stock_level`: WRITE operation - keep separate/restricted
- ❌ `get_production_pricing`: Can query via execute_sql
- ❌ `update_stock_record`: WRITE operation - keep separate
- ❌ `update_job_record`: WRITE operation - keep separate
- ❌ `query_ai_extracted_jobs`: Can use execute_sql

---

## Example AI Agent Flows

### Flow 1: Simple Quote Request
```
User: "Quote for 1000 business cards"

AI: inhouse_get_calculator_requirements('business_cards')
    → Learns: needs quantity, stock_type, sides, celloglaze, artworks

AI: inhouse_calculate_quote('business_cards', {
      quantity: 1000,
      stock_type: 'satin_350gsm',  // Default from historical patterns
      sides: 2,
      celloglaze: 'none',
      artworks: 1
    })
    → Gets: $107.80 inc GST

Response: "Premium Business Cards (350GSM Satin, double-sided): $107.80 inc GST"
```

### Flow 2: Quote with Historical Context
```
User: "Quote for John's usual business cards, 2000 this time"

AI: inhouse_get_query_library_catalog()
    → Discovers: customer_order_history query available

AI: inhouse_execute_sql(
      "SELECT TOP 5 jt.TicketNotes, jt.QTY 
       FROM JobTickets jt JOIN Orders o ON jt.OrderID = o.OrderID
       WHERE o.ClientName LIKE '%John%' 
       AND jt.ShortJobDesc LIKE '%business card%'
       ORDER BY o.OrderDate DESC"
    )
    → Gets: Previous orders with specifications in TicketNotes

AI: Extracts from TicketNotes: "350gsm Satin, Matt Cello Both Sides, Double sided"

AI: inhouse_get_calculator_requirements('business_cards')
    → Maps: "Matt Cello Both Sides" → celloglaze='2_side_matt'

AI: inhouse_calculate_quote('business_cards', {
      quantity: 2000,
      stock_type: 'satin_350gsm',
      sides: 2,
      celloglaze: '2_side_matt',
      artworks: 1
    })
    → Gets: $189.50 inc GST

Response: "Based on John's previous orders (350GSM Satin with Matt Cello both sides), 
          2,000 cards will be $189.50 inc GST (vs previous 1,000 @ $107.80)"
```

### Flow 3: Quote with Stock Check
```
User: "Quote for 5000 cards and tell me if we have enough stock"

AI: inhouse_calculate_quote('business_cards', {...})
    → Gets: $445.00 inc GST

AI: Knows from quote: Uses 350GSM Satin stock

AI: inhouse_query_stock_levels({stock_type: 'Satin', gsm: 350})
    → Gets: current_level=5000 sheets, status='ok'

Response: "Quote: $445.00 inc GST. Stock check: 5,000 sheets of 350GSM Satin 
          available (sufficient for order). Note: This will consume most available 
          stock - consider reordering soon."
```

### Flow 4: Complex Analysis
```
User: "Compare my last 3 booklet orders and quote for 500 units matching the most expensive one"

AI: inhouse_get_query_library_catalog()
    → Discovers: product_performance_detail query

AI: inhouse_execute_sql(
      "SELECT TOP 3 jt.TicketNotes, jt.Cost, jt.Pages, jt.QTY
       FROM JobTickets jt JOIN Orders o ON jt.OrderID = o.OrderID  
       WHERE o.ClientName LIKE '%[user]%'
       AND jt.ShortJobDesc LIKE '%booklet%'
       ORDER BY jt.Cost DESC"
    )
    → Gets: 3 booklet orders with specifications

AI: Analyzes: Most expensive had 32pp, 300GSM cover, 150GSM internal, cello

AI: inhouse_get_calculator_requirements('booklets')
    → Maps specifications to parameters

AI: inhouse_calculate_quote('booklets', {
      quantity: 500,
      pages: 32,
      cover_gsm: 300,
      internal_gsm: 150,
      cello_required: true,
      // ... extracted specs
    })
    → Gets: $1,245.00 inc GST

Response: "Your last 3 booklet orders:
          1. 32pp, 300GSM cover, cello: $2,890 (1000 units)
          2. 24pp, 250GSM cover: $1,540 (500 units)  
          3. 16pp, 300GSM cover: $980 (500 units)
          
          Matching specifications #1 for 500 units: $1,245.00 inc GST"
```

---

## Implementation Files

### 1. Schema File: `inhouse_tools.json`
```json
{
  "platform": "inhouse_print",
  "description": "InHouse Print specialized tools with SQL capability and quote calculation",
  "tools": [
    {
      "name": "inhouse_get_query_library_catalog",
      "description": "Get catalog of 50+ pre-built SQL queries...",
      "parameters": {
        "type": "object",
        "properties": {
          "category": {
            "type": "string",
            "description": "Optional category filter"
          }
        },
        "required": []
      }
    },
    {
      "name": "inhouse_execute_sql",
      "description": "Execute SQL with embedded schema knowledge (500+ lines)...",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "SQL query to execute"
          }
        },
        "required": ["query"]
      }
    },
    // ... 4 more tools
  ]
}
```

### 2. Wrapper File: `inhouse_wrapper.py`
```python
"""
InHouse Print Hybrid Tools Wrapper
6 tools: 3 meta-tools + 3 action tools
"""

import sys
import os

backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)
from tool_use_agent import ToolUseAgent

_agent_instance = None

def _get_agent():
    global _agent_instance
    if _agent_instance is None:
        config_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 
            'config', 'database-config.json'
        )
        _agent_instance = ToolUseAgent(config_path)
    return _agent_instance

# META-TOOLS
def inhouse_get_query_library_catalog(category: str = None, **kwargs):
    """Get catalog of 50+ SQL queries"""
    agent = _get_agent()
    return agent._execute_client_tool('get_available_queries', {'category': category})

def inhouse_execute_sql(query: str, **kwargs):
    """Execute SQL with schema knowledge"""
    agent = _get_agent()
    return agent._execute_client_tool('execute_sql', {'query': query})

def inhouse_get_calculator_requirements(product_type: str, **kwargs):
    """Get calculator parameter guidance"""
    agent = _get_agent()
    return agent._execute_client_tool('get_calculator_requirements', {'product_type': product_type})

# ACTION TOOLS
def inhouse_calculate_quote(product_type: str, parameters: dict, **kwargs):
    """Calculate quote"""
    agent = _get_agent()
    return agent._execute_client_tool('calculate_quote', {'product_type': product_type, 'parameters': parameters})

def inhouse_query_stock_levels(filters: dict = None, **kwargs):
    """Quick stock check"""
    agent = _get_agent()
    return agent._execute_client_tool('query_stock_levels', {'filters': filters or {}})

def inhouse_get_reorder_alerts(**kwargs):
    """Quick stock alerts"""
    agent = _get_agent()
    return agent._execute_client_tool('get_reorder_alerts', {})
```

---

## Benefits Summary

### vs Option 1 (15 tools):
✅ **60% fewer tools** (6 vs 15) = faster discovery  
✅ **More flexible** - AI can query anything via SQL  
✅ **Smarter AI** - learns from query catalog, not just executes  

### vs Option 2 (4 meta-tools only):
✅ **Faster for common tasks** - stock check is 1 call not SQL + parse  
✅ **Better UX** - quick actions don't need SQL knowledge  
✅ **Reduced API calls** - action tools are optimized shortcuts  

### General Benefits:
✅ **Query Library integrated** - 50+ queries via catalog (not 50 tools!)  
✅ **SQL freedom** - AI can construct custom queries for complex analysis  
✅ **Calculator guidance** - AI learns requirements dynamically  
✅ **Best performance** - Meta-tools for flexibility, action tools for speed  

---

## Recommended System Prompt Addition

```python
system_prompt = """You are Viki, an AI quote assistant for InHouse Print...

**InHouse Print Tools (6 tools):**

META-TOOLS (Discovery & Flexibility):
1. inhouse_get_query_library_catalog() - Browse 50+ pre-built SQL queries
2. inhouse_execute_sql(query) - Run custom SQL with schema knowledge
3. inhouse_get_calculator_requirements(product_type) - Learn calculator usage

ACTION TOOLS (Quick Operations):
4. inhouse_calculate_quote(product_type, parameters) - Calculate quote
5. inhouse_query_stock_levels(filters) - Check inventory
6. inhouse_get_reorder_alerts() - Get stock alerts

**WORKFLOW for Quotes:**
1. ALWAYS call get_calculator_requirements FIRST (learn what you need)
2. Query historical data with execute_sql OR query_library_catalog
3. Extract specifications from TicketNotes field (PRIMARY source)
4. Map to calculator parameters using guidance from step 1
5. Calculate quote with validated parameters
6. Optionally check stock levels if material availability matters

**SQL CAPABILITIES:**
- You have FULL SQL access via inhouse_execute_sql
- Use query_library_catalog to discover 50+ pre-built queries
- Database has 500+ lines of schema corrections embedded in execute_sql tool
- TicketNotes is PRIMARY source when structured columns NULL

**SMART APPROACH:**
- Browse query catalog before building custom SQL
- Combine tools creatively (quote + stock check in parallel)
- Use historical patterns from get_calculator_requirements
"""
```

---

**RECOMMENDATION: Implement Hybrid Approach (6 tools)**

This gives you the best of both worlds:
- Intelligence and flexibility of meta-tools
- Speed and convenience of action tools
- Fewer tools than full plugin (faster discovery)
- More capability than meta-tools alone (optimized shortcuts)

Ready to implement? 🚀

---

**Last Updated:** November 4, 2025  
**Status:** Recommended Approach Defined  
**Next:** Create inhouse_tools.json with 6 tool definitions
