# Hybrid Approach Integration Plan - Implementation Guide
**6 InHouse Tools + Context-Aware Routing**

---

## 🎯 Executive Summary

**Goal:** Integrate G_FOLDER's InHouse Print capabilities into AI_agents with 6 intelligent tools instead of 15

**Strategy:** Hybrid approach - 3 meta-tools (SQL + discovery) + 3 action tools (optimized shortcuts)

**Impact:**
- ✅ AI gets SQL query capability (50+ pre-built queries + custom SQL)
- ✅ AI learns calculator requirements dynamically (not hardcoded)
- ✅ 60% fewer tools than full plugin (6 vs 15) = faster discovery
- ✅ Context-aware routing (quote requests → Viki prompt with SQL guidance)

**Timeline:** 6-8 hours across 7 phases

---

## 📊 Architecture Overview

### Current State (622 tools)
```
AI_agents Registry V3
├── 584 static tools (from schemas/)
├── 38 module plugins (existing)
└── Progressive loading (5 meta-tools → 622 full)

G_FOLDER (separate)
└── tool_use_agent.py (15 tools, standalone)
```

### Target State (628 tools)
```
AI_agents Registry V3
├── 584 static tools
├── 38 existing module plugins
├── 6 InHouse tools (NEW - hybrid approach)
│   ├── META-TOOLS (3):
│   │   ├── inhouse_get_query_library_catalog  (browse 50+ queries)
│   │   ├── inhouse_execute_sql                 (custom SQL with schema)
│   │   └── inhouse_get_calculator_requirements (parameter guidance)
│   └── ACTION-TOOLS (3):
│       ├── inhouse_calculate_quote             (quote calculation)
│       ├── inhouse_query_stock_levels          (inventory check)
│       └── inhouse_get_reorder_alerts          (stock alerts)
└── Context routing: quote_agent → Viki prompt
```

---

## 🗂️ File Structure After Integration

```
AI_agents/
├── tools/
│   ├── registry_v3.py                    (UNCHANGED - auto-discovers new tools)
│   └── schemas/                          (existing schemas)
│
├── UI/external/modules/quote-calculator/
│   ├── schema/
│   │   └── inhouse_tools.json            ✨ NEW - 6 tool definitions
│   │
│   ├── implementations/
│   │   └── inhouse_wrapper.py            ✨ NEW - wrapper with singleton pattern
│   │
│   └── backend/                          (UNCHANGED - existing G_FOLDER files)
│       ├── tool_use_agent.py             (3,187 lines - reused as library)
│       ├── complete_calculator_implementation.py
│       ├── query_library.py              (50+ queries)
│       ├── db_connector.py
│       └── [all other backend files]
│
├── AI_infrastructure/
│   ├── prompts/
│   │   ├── data_agent.txt                (existing - general AI)
│   │   └── viki_inhouse_agent.txt        ✨ NEW - quote agent with SQL guidance
│   │
│   ├── core/
│   │   └── agent_worker.py               🔧 MODIFY - add context parameter
│   │
│   └── routes/
│       └── agent_routes.py               🔧 MODIFY - add /api/agent/quote route
│
└── config/
    └── database-config.json              (UNCHANGED - G_FOLDER uses this)
```

**Files to Create:** 3 (inhouse_tools.json, inhouse_wrapper.py, viki_inhouse_agent.txt)  
**Files to Modify:** 2 (agent_worker.py, agent_routes.py)  
**Files Reused:** All backend files (no changes needed)

---

## 📝 Implementation Phases (6-8 hours)

### Phase 1: Create Schema (inhouse_tools.json) - 1 hour

**File:** `UI/external/modules/quote-calculator/schema/inhouse_tools.json`

**Content:**
```json
{
  "platform": "inhouse_print",
  "description": "InHouse Print specialized tools with SQL query capability, quote calculation, and inventory management",
  "tools": [
    {
      "name": "inhouse_get_query_library_catalog",
      "description": "Get catalog of 50+ pre-built SQL queries for InHouse Print database with parameter requirements and usage examples. Use this to discover available queries before executing SQL.",
      "platform": "inhouse_print",
      "parameters": {
        "type": "object",
        "properties": {
          "category": {
            "type": "string",
            "description": "Optional filter: 'Sales & Revenue', 'Customer Analytics', 'Product Performance', 'Operations & Efficiency', 'Stock Management', 'Production Reports', 'Financial Reports'"
          }
        },
        "required": []
      },
      "returns": {
        "type": "object",
        "description": "List of queries with name, category, description, parameters, and examples"
      }
    },
    {
      "name": "inhouse_execute_sql",
      "description": "Execute SQL query against InHousePrintDB (FredDEV) with embedded schema knowledge (500+ lines of corrections). CRITICAL SCHEMA CORRECTIONS: PaperSize has NO Width/Height columns (only SizeID and [Desc]), BindType uses BindTypeDesc (NOT [Desc]!), ColourStatus is production urgency (NOT print color), TicketNotes is PRIMARY source of truth when structured columns are NULL. Always JOIN Orders (o), JobTickets (jt), PaperSize (ps), BindType (bt). Use TOP 20 to limit results.",
      "platform": "inhouse_print",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "SQL query to execute (use TOP 20 for safety)"
          }
        },
        "required": ["query"]
      },
      "returns": {
        "type": "array",
        "description": "Query results as array of row objects"
      }
    },
    {
      "name": "inhouse_get_calculator_requirements",
      "description": "Get complete parameter requirements, natural language mappings, historical patterns, and extraction strategies for each calculator type. ALWAYS call this FIRST before calculating quotes to learn what parameters are needed.",
      "platform": "inhouse_print",
      "parameters": {
        "type": "object",
        "properties": {
          "product_type": {
            "type": "string",
            "description": "Calculator type: business_cards, flyers, perfect_bound_books, corflute_signs, booklets, wire_bound, spiral_bound, premium_business_cards, economical_business_cards, folded_flyers"
          }
        },
        "required": ["product_type"]
      },
      "returns": {
        "type": "object",
        "description": "Complete guidance including parameters (with types, required flags, options), natural_language_mapping (text→parameters), historical_patterns (common values), extraction_strategy (how to parse TicketNotes)"
      }
    },
    {
      "name": "inhouse_calculate_quote",
      "description": "Calculate quote for InHouse Print products. Routes to appropriate calculator (GOD calculator for flyers/business_cards, Shopify calculators for specialized products). Always call get_calculator_requirements FIRST to validate parameters.",
      "platform": "inhouse_print",
      "parameters": {
        "type": "object",
        "properties": {
          "product_type": {
            "type": "string",
            "description": "Product type matching calculator requirements"
          },
          "parameters": {
            "type": "object",
            "description": "Product-specific parameters from get_calculator_requirements"
          }
        },
        "required": ["product_type", "parameters"]
      },
      "returns": {
        "type": "object",
        "description": "Quote with cost_ex_gst, cost_inc_gst, cost_to_business, profit_margin, specifications, breakdown"
      }
    },
    {
      "name": "inhouse_query_stock_levels",
      "description": "Quick inventory check for paper/material stock levels. Faster than SQL query for common stock checks. Returns current levels, reorder points, and status (critical/low/ok).",
      "platform": "inhouse_print",
      "parameters": {
        "type": "object",
        "properties": {
          "filters": {
            "type": "object",
            "description": "Optional filters: stock_type (e.g., 'Satin'), gsm (e.g., 350), status ('critical'|'low'|'ok')"
          }
        },
        "required": []
      },
      "returns": {
        "type": "object",
        "description": "Array of stocks with stock_id, description, current_level, reorder_point, critical_level, status"
      }
    },
    {
      "name": "inhouse_get_reorder_alerts",
      "description": "Quick dashboard of stock shortage alerts. Returns list of stocks below reorder point with alert levels (CRITICAL/WARNING). Use this for proactive stock management.",
      "platform": "inhouse_print",
      "parameters": {
        "type": "object",
        "properties": {},
        "required": []
      },
      "returns": {
        "type": "object",
        "description": "Alerts array with stock_id, description, current_level, reorder_point, alert_level, alert_date, plus critical_count and warning_count totals"
      }
    }
  ]
}
```

**Test:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); inhouse = [t for t in r.tools if 'inhouse' in t]; print(f'Loaded {len(inhouse)} InHouse tools'); print(inhouse)"
```

Expected: `Loaded 6 InHouse tools`

---

### Phase 2: Create Wrapper (inhouse_wrapper.py) - 2 hours

**File:** `UI/external/modules/quote-calculator/implementations/inhouse_wrapper.py`

**Content:**
```python
"""
InHouse Print Hybrid Tools Wrapper
Bridges AI_agents registry to G_FOLDER backend via singleton pattern

ARCHITECTURE:
- Singleton ToolUseAgent (expensive db/calculator initialization once)
- 6 wrapper functions (3 meta + 3 action tools)
- Routes to backend tool_use_agent.py._execute_client_tool()
- Uses existing backend files unchanged (library pattern)

TOOLS:
META (Discovery & Flexibility):
- inhouse_get_query_library_catalog: Browse 50+ queries
- inhouse_execute_sql: Custom SQL with schema knowledge
- inhouse_get_calculator_requirements: Parameter guidance

ACTION (Optimized Shortcuts):
- inhouse_calculate_quote: Quote calculation
- inhouse_query_stock_levels: Inventory check
- inhouse_get_reorder_alerts: Stock alerts
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add backend to path
current_dir = Path(__file__).parent
backend_path = current_dir.parent / 'backend'
sys.path.insert(0, str(backend_path))

from tool_use_agent import ToolUseAgent

# Singleton instance
_agent_instance = None


def _get_agent() -> ToolUseAgent:
    """
    Get singleton ToolUseAgent instance
    
    Initializes once with:
    - InHousePrintDB connection (SQL Server FredDEV)
    - ComprehensiveQuoteCalculator (6,277 lines)
    - QueryLibrary (50+ queries, 5,042 lines)
    - StockDatabaseTools (SQLite stock_data.db)
    - Anthropic client (for AI features)
    """
    global _agent_instance
    if _agent_instance is None:
        # Path to database-config.json
        config_path = Path(__file__).parent.parent.parent.parent.parent / 'config' / 'database-config.json'
        
        if not config_path.exists():
            raise FileNotFoundError(f"Database config not found: {config_path}")
        
        _agent_instance = ToolUseAgent(str(config_path))
    
    return _agent_instance


# ============================================================================
# META-TOOLS (Discovery & Flexibility)
# ============================================================================

def inhouse_get_query_library_catalog(category: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Get catalog of 50+ pre-built SQL queries
    
    Returns list of available queries with:
    - name: Query identifier
    - category: Sales & Revenue, Customer Analytics, etc.
    - description: What the query does
    - parameters: Required parameters
    - example: Usage example
    
    Use this to discover queries before executing SQL.
    
    Args:
        category: Optional filter (Sales & Revenue, Customer Analytics, etc.)
        **kwargs: Credential injection (not used for InHouse tools)
    
    Returns:
        {
            "queries": [
                {
                    "name": "customer_order_history",
                    "category": "Customer Analytics",
                    "description": "Get customer's order history...",
                    "parameters": ["customer_name", "months_back"],
                    "example": "Find what John ordered..."
                },
                ...
            ]
        }
    """
    agent = _get_agent()
    return agent._execute_client_tool('get_available_queries', {'category': category})


def inhouse_execute_sql(query: str, **kwargs) -> List[Dict[str, Any]]:
    """
    Execute SQL query with embedded schema knowledge
    
    CRITICAL SCHEMA CORRECTIONS (embedded in backend):
    - PaperSize: NO Width/Height columns! Only SizeID and [Desc]
    - BindType: Uses BindTypeDesc (NOT [Desc]!)
    - ColourStatus: Production urgency (NOT print color!)
    - TicketNotes: PRIMARY source when structured columns NULL
    
    CORRECT QUERY PATTERN:
    SELECT TOP 20
        jt.TicketNotes AS ProductionNotes,
        ps.[Desc] AS PaperSize,
        bt.BindTypeDesc AS BindType,
        jt.QTY, jt.Cost, o.ClientName
    FROM JobTickets jt
    JOIN Orders o ON jt.OrderID = o.OrderID
    LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
    LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
    WHERE o.ClientName LIKE '%[name]%'
    ORDER BY o.OrderDate DESC
    
    Args:
        query: SQL query to execute (use TOP 20 for safety)
        **kwargs: Credential injection (not used)
    
    Returns:
        Array of row objects (dicts)
    
    Raises:
        Exception: If SQL error or connection failure
    """
    agent = _get_agent()
    return agent._execute_client_tool('execute_sql', {'query': query})


def inhouse_get_calculator_requirements(product_type: str, **kwargs) -> Dict[str, Any]:
    """
    Get parameter requirements for calculator
    
    ALWAYS call this FIRST before calculating quotes!
    
    Returns:
    - parameters: Dict of param_name → {type, required, options, default, common_values}
    - natural_language_mapping: Text phrases → parameter values
    - historical_patterns: Most common parameter combinations
    - extraction_strategy: How to parse TicketNotes for this product
    
    Args:
        product_type: business_cards, flyers, perfect_bound_books, etc.
        **kwargs: Credential injection (not used)
    
    Returns:
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
                    "options": ["satin_300gsm", "satin_350gsm", ...]
                },
                ...
            },
            "natural_language_mapping": {
                "350gsm satin": "satin_350gsm",
                "matt cello both sides": "celloglaze='2_side_matt'",
                ...
            },
            "historical_patterns": {
                "most_common": {
                    "stock_type": "satin_350gsm",
                    "celloglaze": "2_side_matt"
                }
            },
            "extraction_strategy": "Parse TicketNotes for: '350gsm', 'Satin', ..."
        }
    """
    agent = _get_agent()
    return agent._execute_client_tool('get_calculator_requirements', {'product_type': product_type})


# ============================================================================
# ACTION TOOLS (Optimized Shortcuts)
# ============================================================================

def inhouse_calculate_quote(product_type: str, parameters: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Calculate quote for InHouse Print product
    
    Routes to appropriate calculator:
    - GOD calculator: flyers, business_cards (universal parameters)
    - Shopify calculators: wire_bound, spiral_bound, perfect_bound_books, etc.
    
    WORKFLOW:
    1. Call get_calculator_requirements(product_type) FIRST
    2. Validate all required parameters are provided
    3. Call this function with validated parameters
    
    Args:
        product_type: Calculator type (from get_calculator_requirements)
        parameters: Product-specific parameters (validated against requirements)
        **kwargs: Credential injection (not used)
    
    Returns:
        {
            "success": true,
            "cost_ex_gst": 98.00,
            "cost_inc_gst": 107.80,
            "cost_to_business": 65.23,
            "profit_margin": 32.77,
            "specifications": {
                "quantity": 1000,
                "stock_type": "satin_350gsm",
                ...
            },
            "breakdown": {
                "material_cost": 45.20,
                "labor_cost": 15.03,
                "overhead": 5.00
            }
        }
    
    Raises:
        Exception: If calculator error or invalid parameters
    """
    agent = _get_agent()
    return agent._execute_client_tool('calculate_quote', {
        'product_type': product_type,
        'parameters': parameters
    })


def inhouse_query_stock_levels(filters: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
    """
    Quick inventory check
    
    Faster than SQL for common stock queries.
    Returns current levels, reorder points, critical levels, and status.
    
    Args:
        filters: Optional filters
            - stock_type (str): e.g., "Satin", "Gloss"
            - gsm (int): e.g., 350, 300
            - status (str): "critical" | "low" | "ok"
        **kwargs: Credential injection (not used)
    
    Returns:
        {
            "stocks": [
                {
                    "stock_id": 44,
                    "description": "Satin 350GSM",
                    "current_level": 5000,
                    "reorder_point": 2000,
                    "critical_level": 500,
                    "status": "ok"
                },
                ...
            ]
        }
    """
    agent = _get_agent()
    return agent._execute_client_tool('query_stock_levels', {'filters': filters or {}})


def inhouse_get_reorder_alerts(**kwargs) -> Dict[str, Any]:
    """
    Quick stock shortage alerts
    
    Returns stocks below reorder point with alert levels.
    Use for proactive stock management dashboard.
    
    Args:
        **kwargs: Credential injection (not used)
    
    Returns:
        {
            "alerts": [
                {
                    "stock_id": 12,
                    "description": "Gloss 300GSM",
                    "current_level": 450,
                    "reorder_point": 2000,
                    "alert_level": "CRITICAL",
                    "alert_date": "2025-11-03"
                },
                ...
            ],
            "critical_count": 2,
            "warning_count": 5
        }
    """
    agent = _get_agent()
    return agent._execute_client_tool('get_reorder_alerts', {})
```

**Test:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); result = r.execute_tool('inhouse_get_query_library_catalog'); print(f'Query catalog: {len(result.get(\"queries\", []))} queries')"
```

---

### Phase 3: Verify Registry Loading - 15 minutes

**Test Commands:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents

# Test 1: Check tool count (should be 628 = 622 + 6)
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print(f'Total tools: {len(r.tools)}'); inhouse = [t for t in r.tools if 'inhouse' in t]; print(f'InHouse tools: {len(inhouse)}'); print(inhouse)"

# Test 2: Get Anthropic format (verify schema conversion)
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); tools = r.get_anthropic_tools(); inhouse = [t for t in tools if 'inhouse' in t['name']]; print(f'InHouse tools in Anthropic format: {len(inhouse)}'); import json; print(json.dumps(inhouse[0], indent=2))"

# Test 3: Execute catalog tool
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); result = r.execute_tool('inhouse_get_query_library_catalog'); print(f'Success: {\"queries\" in result}'); print(f'Query count: {len(result.get(\"queries\", []))}')"

# Test 4: Execute requirements tool
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); result = r.execute_tool('inhouse_get_calculator_requirements', product_type='business_cards'); print(f'Success: {\"parameters\" in result}'); print(f'Parameters: {list(result.get(\"parameters\", {}).keys())}')"
```

**Expected:**
```
Total tools: 628
InHouse tools: 6
['inhouse_get_query_library_catalog', 'inhouse_execute_sql', 'inhouse_get_calculator_requirements', 'inhouse_calculate_quote', 'inhouse_query_stock_levels', 'inhouse_get_reorder_alerts']
```

---

### Phase 4: Create Viki System Prompt - 1 hour

**File:** `AI_infrastructure/prompts/viki_inhouse_agent.txt`

**Content:**
```
You are Viki, an AI quote assistant for InHouse Print with SQL database access and quote calculation capabilities.

=== YOUR CAPABILITIES ===

You have access to 6 specialized InHouse Print tools:

META-TOOLS (Discovery & Flexibility):
1. inhouse_get_query_library_catalog(category) - Browse 50+ pre-built SQL queries
2. inhouse_execute_sql(query) - Execute custom SQL with embedded schema knowledge
3. inhouse_get_calculator_requirements(product_type) - Learn calculator parameter requirements

ACTION TOOLS (Quick Operations):
4. inhouse_calculate_quote(product_type, parameters) - Calculate product quotes
5. inhouse_query_stock_levels(filters) - Check inventory levels
6. inhouse_get_reorder_alerts() - Get stock shortage alerts

=== WORKFLOW FOR QUOTE REQUESTS ===

STEP 1: LEARN REQUIREMENTS (ALWAYS FIRST!)
- Call inhouse_get_calculator_requirements(product_type)
- This tells you: required parameters, optional parameters, natural language mappings, historical patterns

STEP 2: GATHER CONTEXT (if needed)
- If customer/order reference: Use inhouse_get_query_library_catalog() to find relevant query
- Execute SQL via inhouse_execute_sql() to get historical data
- Extract specifications from TicketNotes field (PRIMARY source of truth)

STEP 3: MAP SPECIFICATIONS
- Use natural_language_mapping from requirements to convert text → parameters
- Use historical_patterns for defaults when specs not specified
- Validate all required parameters are provided

STEP 4: CALCULATE QUOTE
- Call inhouse_calculate_quote(product_type, parameters)
- Present quote with cost_inc_gst prominently

STEP 5: OPTIONAL CHECKS
- If material availability matters: Call inhouse_query_stock_levels()
- Present stock status with quote

=== SQL DATABASE KNOWLEDGE ===

CRITICAL SCHEMA CORRECTIONS (embedded in inhouse_execute_sql tool):

1. PaperSize Table:
   - Has: SizeID (int), [Desc] (string, e.g., "A4", "BC - 90x55")
   - NO Width/Height columns! Common mistake to assume they exist
   - JOIN: LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID

2. BindType Table:
   - Has: BindID (int), BindTypeDesc (string)
   - Use BindTypeDesc (NOT [Desc]!)
   - JOIN: LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID

3. ColourStatus:
   - Meaning: Production urgency status (Urgent, Waiting, In Progress)
   - NOT print color! Common mistake
   - Print color info is in TicketNotes

4. TicketNotes Field:
   - PRIMARY source of truth when structured columns are NULL
   - Contains: paper type, GSM, color, finishes, specifications
   - Parse with extraction_strategy from get_calculator_requirements

CORRECT SQL PATTERN:
```sql
SELECT TOP 20
    jt.TicketNotes AS ProductionNotes,  -- PRIMARY source
    ps.[Desc] AS PaperSize,              -- "A4", "BC - 90x55"
    bt.BindTypeDesc AS BindType,         -- NOT bt.[Desc]!
    jt.QTY AS Quantity,
    jt.Cost AS JobCost,
    o.ClientName,
    o.OrderDate
FROM JobTickets jt
JOIN Orders o ON jt.OrderID = o.OrderID
LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
WHERE o.ClientName LIKE '%[customer]%'
  AND jt.ShortJobDesc LIKE '%[product]%'
ORDER BY o.OrderDate DESC
```

ALWAYS:
- Use TOP 20 to limit results
- JOIN Orders and JobTickets
- LEFT JOIN for lookup tables (PaperSize, BindType)
- Extract from TicketNotes when structured columns NULL

=== EXAMPLE INTERACTIONS ===

Example 1: Simple Quote
User: "Quote for 1000 business cards"

You:
1. inhouse_get_calculator_requirements('business_cards')
   → Learn: needs quantity, stock_type, sides, celloglaze, artworks
   → Historical pattern: satin_350gsm, 2_side_matt most common

2. inhouse_calculate_quote('business_cards', {
     quantity: 1000,
     stock_type: 'satin_350gsm',
     sides: 2,
     celloglaze: '2_side_matt',
     artworks: 1
   })
   → Cost: $107.80 inc GST

Response: "Premium Business Cards (350GSM Satin, Matt Cello both sides, double-sided): $107.80 inc GST for 1,000 cards."

---

Example 2: Quote with Historical Context
User: "Quote for John's usual business cards, 2000 this time"

You:
1. inhouse_get_query_library_catalog()
   → Find: customer_order_history query available

2. inhouse_execute_sql(
     "SELECT TOP 5 jt.TicketNotes, jt.QTY, jt.Cost
      FROM JobTickets jt
      JOIN Orders o ON jt.OrderID = o.OrderID
      WHERE o.ClientName LIKE '%John%'
        AND jt.ShortJobDesc LIKE '%business card%'
      ORDER BY o.OrderDate DESC"
   )
   → Find: Previous orders with "350gsm Satin, Matt Cello Both Sides"

3. inhouse_get_calculator_requirements('business_cards')
   → Map: "Matt Cello Both Sides" → celloglaze='2_side_matt'

4. inhouse_calculate_quote('business_cards', {
     quantity: 2000,
     stock_type: 'satin_350gsm',
     sides: 2,
     celloglaze: '2_side_matt',
     artworks: 1
   })
   → Cost: $189.50 inc GST

Response: "Based on John's previous orders (350GSM Satin with Matt Cello both sides), 2,000 cards will be $189.50 inc GST. His previous 1,000-card order was $107.80."

---

Example 3: Quote with Stock Check
User: "Quote for 5000 cards and check if we have enough stock"

You:
1. inhouse_get_calculator_requirements('business_cards')
2. inhouse_calculate_quote(...) → $445.00 inc GST
3. inhouse_query_stock_levels({stock_type: 'Satin', gsm: 350})
   → Current: 5,000 sheets, status: 'ok'

Response: "Quote: $445.00 inc GST for 5,000 cards. Stock check: 5,000 sheets of 350GSM Satin available (sufficient). Note: This will consume most available stock - consider reordering soon."

=== COMMUNICATION STYLE ===

- Professional but friendly
- Always show price inc GST prominently
- Explain specifications clearly (avoid jargon when possible)
- Proactively suggest stock checks for large orders
- Reference historical patterns when available
- Break down complex quotes into understandable components

=== SMART BEHAVIORS ===

DO:
- Browse query catalog before building custom SQL
- Use get_calculator_requirements FIRST (learn before acting)
- Extract from TicketNotes when structured columns NULL
- Use historical patterns for defaults
- Combine tools creatively (quote + stock check in parallel)
- Validate parameters before calculating

DON'T:
- Assume PaperSize has Width/Height columns (it doesn't!)
- Use bt.[Desc] for BindType (use BindTypeDesc!)
- Interpret ColourStatus as print color (it's urgency!)
- Skip get_calculator_requirements (always call first)
- Execute SQL without TOP clause (always limit results)

=== ERROR HANDLING ===

If SQL error:
- Check schema corrections above
- Verify table joins are correct
- Ensure TOP clause is present

If calculator error:
- Call get_calculator_requirements again
- Validate all required parameters provided
- Check parameter format matches requirements

If stock data unavailable:
- Gracefully explain limitation
- Offer to calculate quote without stock check

You are here to make quoting fast, accurate, and intelligent. Use your SQL access to learn from history and provide context-aware quotes.
```

**Test:**
```powershell
# Verify prompt file exists
Test-Path "C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\prompts\viki_inhouse_agent.txt"
```

---

### Phase 5: Add Context Routing in agent_worker.py - 1 hour

**File:** `AI_infrastructure/core/agent_worker.py`

**Location:** Around line 309 (where system_prompt is loaded)

**Current Code:**
```python
# ✅ Get system prompt with tool usage instructions
system_prompt = ai_client.get_system_prompt('data_agent_chat')
print(f"{log_prefix} System prompt loaded ({len(system_prompt)} chars)")
```

**New Code:**
```python
# ✅ Get system prompt based on context
# Context-aware routing: quote requests → Viki prompt with SQL guidance
if context == 'quote_agent':
    prompt_name = 'viki_inhouse_agent'
    print(f"{log_prefix} Using InHouse Print context (Viki prompt)")
else:
    prompt_name = 'data_agent_chat'
    print(f"{log_prefix} Using general agent context")

system_prompt = ai_client.get_system_prompt(prompt_name)
print(f"{log_prefix} System prompt loaded: {prompt_name} ({len(system_prompt)} chars)")
```

**Purpose:** Routes quote-related requests to Viki prompt with SQL guidance and InHouse tool instructions

**Test:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
python -c "from core.agent_worker import run_agent_worker; import threading; from queue import Queue; q = Queue(); lock = threading.Lock(); run_agent_worker('test', 'test prompt', [], lock, 'test_session', q, None, 'quote_agent', 1)"
```

Expected log: `Using InHouse Print context (Viki prompt)`

<function_calls>
<invoke name="read_file">
<parameter name="filePath">c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\core\agent_worker.py