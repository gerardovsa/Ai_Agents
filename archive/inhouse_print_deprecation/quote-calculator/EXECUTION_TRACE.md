# Quote Calculator Module - Complete Execution Trace

**Document Type:** Architecture & Data Flow Analysis  
**Date:** December 17, 2024  
**Purpose:** Trace complete execution path from AI agent → database → response

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI AGENT LAYER                               │
│  (Claude, GPT-4, Anthropic Claude via tool_use_agent.py)           │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           │ Tool Call Request
                           ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    REGISTRY V3 LAYER                                 │
│  tools/registry_v3.py                                                │
│  - Tool Discovery                                                    │
│  - Implementation Routing                                            │
│  - Parameter Validation                                              │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           │ Route to Implementation
                           ↓
┌─────────────────────────────────────────────────────────────────────┐
│              MODULE PLUGIN LOADER                                    │
│  tools/plugins/module_plugin_loader.py                               │
│  - Discovers modules in UI/modules_external/                         │
│  - Loads schema/*.json files                                         │
│  - Loads implementations/*_wrapper.py files                          │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           │ Load Module
                           ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    WRAPPER LAYER                                     │
│  UI/modules_external/quote-calculator/implementations/               │
│                                                                       │
│  ┌──────────────────────┐  ┌──────────────────────┐                │
│  │ calculator_wrapper.py│  │calculator_pricing_   │                │
│  │                       │  │wrapper.py            │                │
│  │ • 31 calculators      │  │ • 4 database tools   │                │
│  │ • GOD calculators     │  │ • CalculatorPricingDB│                │
│  │ • Shopify calculators │  │ • QueryLibrary       │                │
│  └──────────────────────┘  └──────────────────────┘                │
│                                                                       │
│  ┌──────────────────────┐  ┌──────────────────────┐                │
│  │query_library_wrapper.│  │calculator_builder_   │                │
│  │py                     │  │wrapper.py            │                │
│  │ • 2 query tools       │  │ • 6 builder tools    │                │
│  │ • QueryLibrary access │  │ • 7 query tools      │                │
│  └──────────────────────┘  └──────────────────────┘                │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           │ Delegate to Backend
                           ↓
┌─────────────────────────────────────────────────────────────────────┐
│                       BACKEND LAYER                                  │
│  UI/modules_external/quote-calculator/backend/                       │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │ query_library.py (5,958 lines)                            │       │
│  │ • 77 pre-built queries                                    │       │
│  │ • 6 custom calculator queries                             │       │
│  │ • SQL generation with parameters                          │       │
│  │ • Routing: _generate_sql() → _sql_xxx() methods          │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │ calculator_builder_tools.py (632 lines)                   │       │
│  │ • CalculatorBuilderTools class                            │       │
│  │ • 6 interactive builder methods                           │       │
│  │ • Database CRUD operations                                │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │ universal_calculator_executor.py (400 lines)              │       │
│  │ • UniversalCalculatorExecutor class                       │       │
│  │ • Execute JSON calculator definitions                     │       │
│  │ • asteval for safe formula execution                      │       │
│  │ • Parameter resolution (2-tier)                           │       │
│  │ • Component library integration                           │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │ common_components.py (250 lines)                          │       │
│  │ • 11 reusable calculation components                      │       │
│  │ • tiered_pricing_lookup()                                 │       │
│  │ • quantity_break_discount()                               │       │
│  │ • calculate_profit_margin()                               │       │
│  │ • calculate_gst()                                         │       │
│  │ • ... 7 more components                                   │       │
│  └──────────────────────────────────────────────────────────┘       │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           │ Execute SQL / Database Operations
                           ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    DATABASE CONNECTION LAYER                         │
│  AI_infrastructure/shared/database_utils.py                          │
│  - get_database_connection()                                         │
│  - Connection pooling                                                │
│  - Error handling                                                    │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           │ psycopg2 Connection
                           ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      SUPABASE POSTGRESQL                             │
│                                                                       │
│  TIER 1: Calculator Pricing Database (8 tables)                     │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │ calculator_pricing_parameters (363 params)                │       │
│  │ calculator_parameter_overrides                            │       │
│  │ calculator_parameter_history                              │       │
│  │ calculators_registry (30 calculators)                     │       │
│  │ product_options (14 options)                              │       │
│  │ product_option_choices (288 choices)                      │       │
│  │ product_option_overrides                                  │       │
│  │ product_option_history                                    │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                                                       │
│  TIER 2E: Custom Calculator Builder (6 tables)                      │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │ custom_calculators (JSON definitions)                     │       │
│  │ custom_calculator_parameters (dependency tracking)        │       │
│  │ custom_calculator_components (component usage)            │       │
│  │ pricing_scenario_models (what-if analysis)                │       │
│  │ quote_history_archive (execution records)                 │       │
│  │ pricing_impact_projections (impact forecasting)           │       │
│  └──────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Complete Execution Traces

### Trace 1: Query Tool Execution (Read Operation)

**Example:** `custom_calculator_list()` - List all custom calculators

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: AI Agent Tool Call                                          │
└─────────────────────────────────────────────────────────────────────┘
AI Agent: "List all custom calculators"
↓
Tool Call: custom_calculator_list(is_active=true, category="rush_job")

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: Registry V3 Lookup                                          │
└─────────────────────────────────────────────────────────────────────┘
File: tools/registry_v3.py
↓
registry.execute_tool(
    tool_name="custom_calculator_list",
    is_active=true,
    category="rush_job"
)
↓
Lookup: registry.tools["custom_calculator_list"]
         → Found in quote-calculator module schema
↓
Lookup: registry.implementations["custom_calculator_list"]
         → Found in calculator_builder_wrapper.py
↓
Route to: calculator_builder_wrapper.custom_calculator_list()

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: Wrapper Execution                                           │
└─────────────────────────────────────────────────────────────────────┘
File: UI/modules_external/quote-calculator/implementations/
      calculator_builder_wrapper.py
↓
def custom_calculator_list(**kwargs):
    try:
        # Delegate to QueryLibrary
        sql = ql._generate_sql('list_custom_calculators', kwargs)
        return {
            "success": True,
            "query_name": "list_custom_calculators",
            "sql": sql,
            "parameters": kwargs
        }

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: QueryLibrary SQL Generation                                 │
└─────────────────────────────────────────────────────────────────────┘
File: UI/modules_external/quote-calculator/backend/query_library.py
↓
QueryLibrary._generate_sql("list_custom_calculators", {...})
↓
Routes to: _sql_list_custom_calculators(params)
↓
Generates SQL:
    SELECT
        calculator_id,
        name,
        short_description,
        category,
        usage_count,
        last_used_at,
        is_active,
        is_template,
        (SELECT COUNT(*) FROM custom_calculator_parameters 
         WHERE calculator_id = c.calculator_id) as parameter_count,
        avg_calculation_time_ms
    FROM custom_calculators c
    WHERE is_active = true
      AND category = 'rush_job'
    ORDER BY 
        is_active DESC,
        usage_count DESC,
        name ASC;
↓
Returns: 590-character SQL string

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: Response to AI Agent                                        │
└─────────────────────────────────────────────────────────────────────┘
Wrapper returns:
{
    "success": true,
    "query_name": "list_custom_calculators",
    "sql": "SELECT calculator_id, name, ...",
    "parameters": {"is_active": true, "category": "rush_job"},
    "note": "Execute this SQL via calculator_database_query tool"
}
↓
AI Agent receives response
↓
AI Agent calls: calculator_database_query(sql=...)
↓
(Continues to Trace 2 for database execution)
```

---

### Trace 2: Database Tool Execution (Write Operation)

**Example:** `calculator_database_query()` - Execute SQL query

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: AI Agent Tool Call (from Trace 1 or direct)                │
└─────────────────────────────────────────────────────────────────────┘
AI Agent calls: calculator_database_query(
    sql="SELECT calculator_id, name, ... FROM custom_calculators ..."
)

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: Registry V3 Lookup                                          │
└─────────────────────────────────────────────────────────────────────┘
registry.execute_tool(
    tool_name="calculator_database_query",
    sql="SELECT ..."
)
↓
Route to: calculator_pricing_wrapper.calculator_database_query()

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: Wrapper Execution                                           │
└─────────────────────────────────────────────────────────────────────┘
File: UI/modules_external/quote-calculator/implementations/
      calculator_pricing_wrapper.py
↓
def calculator_database_query(**kwargs):
    return db.query(**kwargs)
↓
Delegates to: CalculatorPricingDB.query()

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: Database Query Execution                                    │
└─────────────────────────────────────────────────────────────────────┘
File: UI/modules_external/quote-calculator/backend/
      calculator_pricing_tools.py
↓
Class: CalculatorPricingDB
Method: query(sql, params=None)
↓
1. Validate SQL (must start with SELECT or WITH)
2. Get database connection
   conn = get_database_connection()
3. Create cursor
4. Execute query
   cursor.execute(sql, params)
5. Fetch results
   rows = cursor.fetchall()
6. Convert to list of dicts
   results = [dict(row) for row in rows]
7. Return formatted response

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: Database Connection Layer                                   │
└─────────────────────────────────────────────────────────────────────┘
File: AI_infrastructure/shared/database_utils.py
↓
def get_database_connection():
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    # Get Supabase credentials from environment
    conn = psycopg2.connect(
        host=os.getenv('SUPABASE_HOST'),
        database=os.getenv('SUPABASE_DB'),
        user=os.getenv('SUPABASE_USER'),
        password=os.getenv('SUPABASE_PASSWORD'),
        cursor_factory=RealDictCursor
    )
    return conn

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 6: Supabase PostgreSQL Execution                               │
└─────────────────────────────────────────────────────────────────────┘
Database: Supabase PostgreSQL
↓
Execute query:
    SELECT calculator_id, name, short_description, ...
    FROM custom_calculators
    WHERE is_active = true AND category = 'rush_job'
    ORDER BY usage_count DESC
↓
Returns: ResultSet with matching rows

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 7: Response Chain Back to AI Agent                             │
└─────────────────────────────────────────────────────────────────────┘
Database → Connection Layer:
    ResultSet converted to list of RealDictRow

Connection Layer → Backend:
    [
        {"calculator_id": "uuid1", "name": "Rush24HourVinyl", ...},
        {"calculator_id": "uuid2", "name": "SameDayBanner", ...}
    ]

Backend → Wrapper:
    {
        "success": true,
        "data": [...],
        "row_count": 2,
        "executed": "SELECT calculator_id, ...",
        "execution_time_ms": 45
    }

Wrapper → Registry V3:
    (passes through unchanged)

Registry V3 → AI Agent:
    Tool execution result with data

AI Agent:
    Processes result, formats response for user
```

---

### Trace 3: Builder Tool Execution (Create Operation)

**Example:** `calculator_builder_start()` - Create new custom calculator

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: AI Agent Tool Call                                          │
└─────────────────────────────────────────────────────────────────────┘
AI Agent: "Create new custom calculator for rush vinyl stickers"
↓
Tool Call: calculator_builder_start(
    name="Rush24HourVinylStickers",
    description="Custom pricing for vinyl stickers with 24-hour turnaround",
    short_description="Rush vinyl stickers - 24hr turnaround",
    category="rush_job",
    tags=["vinyl", "rush", "24-hour", "outdoor"]
)

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: Registry V3 Lookup                                          │
└─────────────────────────────────────────────────────────────────────┘
registry.execute_tool(
    tool_name="calculator_builder_start",
    name="Rush24HourVinylStickers",
    ...
)
↓
Route to: calculator_builder_wrapper.calculator_builder_start()

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: Wrapper Execution                                           │
└─────────────────────────────────────────────────────────────────────┘
File: calculator_builder_wrapper.py
↓
def calculator_builder_start(**kwargs):
    # Delegates to backend implementation
    from calculator_builder_tools import calculator_builder_start
    return calculator_builder_start(**kwargs)

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: Backend Builder Tool Execution                              │
└─────────────────────────────────────────────────────────────────────┘
File: calculator_builder_tools.py
↓
Class: CalculatorBuilderTools
Method: calculator_builder_start(name, description, ...)
↓
1. Generate UUID for calculator_id
   calculator_id = str(uuid.uuid4())

2. Create JSON definition structure
   json_definition = {
       "inputs": [],
       "calculation_steps": []
   }

3. Build SQL INSERT statement
   INSERT INTO custom_calculators (
       calculator_id, name, description, short_description,
       category, tags, json_definition, is_active, created_at
   ) VALUES (%s, %s, %s, %s, %s, %s, %s, false, NOW())

4. Get database connection
   conn = get_database_connection()

5. Execute INSERT
   cursor.execute(sql, params)
   conn.commit()

6. Fetch top 10 most-used parameters for suggestions
   SELECT parameter_name, usage_count
   FROM calculator_pricing_parameters
   ORDER BY usage_count DESC LIMIT 10

7. Return response

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: Database Execution                                          │
└─────────────────────────────────────────────────────────────────────┘
INSERT INTO custom_calculators ... (executed)
↓
SELECT parameter_name ... (executed)
↓
Database changes committed

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 6: Response to AI Agent                                        │
└─────────────────────────────────────────────────────────────────────┘
{
    "success": true,
    "calculator_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Rush24HourVinylStickers",
    "category": "rush_job",
    "is_active": false,
    "created_at": "2024-12-17T10:30:00Z",
    "suggested_parameters": [
        "labor_rate_trade",
        "gst_rate",
        "profit_margin_standard",
        ...
    ]
}
↓
AI Agent: "Calculator created. Next, add parameters with calculator_builder_add_parameter()"
```

---

### Trace 4: Calculator Execution (Custom Calculator)

**Example:** Execute custom calculator via UniversalCalculatorExecutor

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: Retrieve Calculator Definition                              │
└─────────────────────────────────────────────────────────────────────┘
SQL: SELECT json_definition FROM custom_calculators 
     WHERE calculator_id = '...'
↓
Retrieved JSON:
{
    "inputs": [
        {"name": "width", "type": "number", "label": "Width (mm)"},
        {"name": "height", "type": "number", "label": "Height (mm)"},
        {"name": "quantity", "type": "integer", "label": "Quantity"}
    ],
    "calculation_steps": [
        {
            "step": 1,
            "output_variable": "area_m2",
            "type": "component",
            "component_name": "calculate_area_m2",
            "parameters": {"width": "width", "height": "height"}
        },
        {
            "step": 2,
            "output_variable": "base_price",
            "type": "component",
            "component_name": "tiered_pricing_lookup",
            "parameters": {
                "quantity": "quantity",
                "tier_parameter": "vinyl_sticker_tiers"
            }
        },
        {
            "step": 3,
            "output_variable": "material_cost",
            "type": "formula",
            "formula": "area_m2 * base_price * quantity"
        },
        {
            "step": 4,
            "output_variable": "rush_premium",
            "type": "formula",
            "formula": "material_cost * rush_multiplier_24hr"
        },
        {
            "step": 5,
            "output_variable": "subtotal",
            "type": "formula",
            "formula": "material_cost + rush_premium"
        },
        {
            "step": 6,
            "output_variable": "total_with_margin",
            "type": "component",
            "component_name": "calculate_profit_margin",
            "parameters": {
                "cost": "subtotal",
                "margin_parameter": "profit_margin_rush"
            }
        },
        {
            "step": 7,
            "output_variable": "final_price",
            "type": "component",
            "component_name": "calculate_gst",
            "parameters": {"base_amount": "total_with_margin"}
        }
    ]
}

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: Universal Calculator Executor Initialization                │
└─────────────────────────────────────────────────────────────────────┘
File: universal_calculator_executor.py
↓
executor = UniversalCalculatorExecutor()
↓
1. Load pricing parameters from database
   pricing_constants = executor._resolve_pricing_constants()
   
   Result:
   {
       "labor_rate_trade": Decimal("65.00"),
       "gst_rate": Decimal("0.10"),
       "profit_margin_standard": Decimal("0.40"),
       "profit_margin_rush": Decimal("0.50"),
       "rush_multiplier_24hr": Decimal("1.5"),
       "vinyl_sticker_tiers": {...}
   }

2. Import component library
   from common_components import *

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: Execute Calculation Steps                                   │
└─────────────────────────────────────────────────────────────────────┘
Input values:
    {"width": 100, "height": 150, "quantity": 500}

Context (execution state):
    {
        "width": 100,
        "height": 150,
        "quantity": 500
    }

─── STEP 1: Calculate area ───
Type: component
Component: calculate_area_m2(width=100, height=150)
↓
area_m2 = (100 * 150) / 1000000 = 0.015 m²
↓
Context updated: {"area_m2": Decimal("0.015"), ...}

─── STEP 2: Tiered pricing lookup ───
Type: component
Component: tiered_pricing_lookup(quantity=500, tier_parameter="vinyl_sticker_tiers")
↓
Retrieve vinyl_sticker_tiers from pricing_constants
Lookup quantity in tiers:
    0-99: $2.50
    100-499: $2.00
    500-999: $1.50  ← MATCH
↓
base_price = Decimal("1.50")
↓
Context updated: {"base_price": Decimal("1.50"), ...}

─── STEP 3: Material cost formula ───
Type: formula
Formula: "area_m2 * base_price * quantity"
↓
Using asteval (safe evaluator):
    aeval = Interpreter()
    aeval.symtable.update(context)  # Load all variables
    result = aeval("area_m2 * base_price * quantity")
↓
Calculation:
    0.015 * 1.50 * 500 = 11.25
↓
material_cost = Decimal("11.25")
↓
Context updated: {"material_cost": Decimal("11.25"), ...}

─── STEP 4: Rush premium formula ───
Type: formula
Formula: "material_cost * rush_multiplier_24hr"
↓
rush_multiplier_24hr retrieved from pricing_constants = 1.5
↓
Calculation:
    11.25 * 1.5 = 16.875
↓
rush_premium = Decimal("16.875")
↓
Context updated: {"rush_premium": Decimal("16.875"), ...}

─── STEP 5: Subtotal formula ───
Type: formula
Formula: "material_cost + rush_premium"
↓
Calculation:
    11.25 + 16.875 = 28.125
↓
subtotal = Decimal("28.125")
↓
Context updated: {"subtotal": Decimal("28.125"), ...}

─── STEP 6: Apply profit margin ───
Type: component
Component: calculate_profit_margin(cost=28.125, margin_parameter="profit_margin_rush")
↓
profit_margin_rush retrieved from pricing_constants = 0.50 (50%)
↓
Calculation:
    28.125 / (1 - 0.50) = 56.25
↓
total_with_margin = Decimal("56.25")
↓
Context updated: {"total_with_margin": Decimal("56.25"), ...}

─── STEP 7: Add GST ───
Type: component
Component: calculate_gst(base_amount=56.25)
↓
gst_rate retrieved from pricing_constants = 0.10 (10%)
↓
Calculation:
    56.25 * 1.10 = 61.875
↓
final_price = Decimal("61.88")  # Rounded to 2 decimal places
↓
Context updated: {"final_price": Decimal("61.88"), ...}

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: Return Result                                               │
└─────────────────────────────────────────────────────────────────────┘
{
    "success": true,
    "final_price": "61.88",
    "breakdown": {
        "area_m2": "0.015",
        "base_price": "1.50",
        "material_cost": "11.25",
        "rush_premium": "16.875",
        "subtotal": "28.125",
        "total_with_margin": "56.25",
        "final_price": "61.88"
    },
    "calculator_name": "Rush24HourVinylStickers",
    "execution_time_ms": 12
}

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: Update Usage Statistics                                     │
└─────────────────────────────────────────────────────────────────────┘
SQL:
UPDATE custom_calculators 
SET usage_count = usage_count + 1,
    last_used_at = NOW(),
    avg_calculation_time_ms = (avg_calculation_time_ms * usage_count + 12) / (usage_count + 1)
WHERE calculator_id = '...'
↓
INSERT INTO quote_history_archive (
    calculator_id, inputs, outputs, execution_time_ms, created_at
) VALUES (...)
↓
Database updated
```

---

## Error Handling Flows

### Error Type 1: Invalid Tool Name

```
AI Agent → "calculator_builder_strat" (typo)
↓
Registry V3: tool not found in registry.tools
↓
Response: {
    "success": false,
    "error": "Tool 'calculator_builder_strat' not found",
    "available_tools": ["calculator_builder_start", ...]
}
```

### Error Type 2: Missing Required Parameter

```
AI Agent → calculator_builder_start(name="Test")  # Missing description
↓
Wrapper → Backend
↓
Backend validation:
    if not description:
        return {"success": false, "error": "description is required"}
```

### Error Type 3: Database Connection Failure

```
Backend → get_database_connection()
↓
Connection error: psycopg2.OperationalError
↓
Wrapper catches exception:
    try:
        conn = get_database_connection()
    except Exception as e:
        return {
            "success": false,
            "error": f"Database connection failed: {str(e)}",
            "error_type": "CONNECTION_ERROR"
        }
```

### Error Type 4: Invalid Calculator JSON

```
Custom calculator JSON missing required field
↓
UniversalCalculatorExecutor.execute()
↓
Validation fails:
    if "calculation_steps" not in json_definition:
        raise ValueError("calculation_steps required")
↓
Wrapper catches:
    return {
        "success": false,
        "error": "Invalid calculator definition: calculation_steps required",
        "error_type": "VALIDATION_ERROR"
    }
```

---

## Performance Characteristics

### Query Tool Performance
- **Registry Lookup:** <1ms
- **SQL Generation:** 1-5ms
- **Total (before DB):** <10ms

### Database Query Performance
- **Simple SELECT:** 10-50ms
- **Complex JOIN:** 50-200ms
- **Aggregation:** 100-500ms

### Calculator Execution Performance
- **Simple (3-5 steps):** 5-15ms
- **Medium (10-15 steps):** 15-30ms
- **Complex (20+ steps):** 30-60ms

### End-to-End Performance
- **Query Tool:** 50-250ms (with DB)
- **Builder Tool:** 100-500ms (with DB writes)
- **Calculator Execution:** 50-200ms (with DB lookups + computation)

---

## Conclusion

This trace document provides complete visibility into:
- ✅ Tool discovery and registration flow
- ✅ Request routing through Registry V3
- ✅ Wrapper delegation patterns
- ✅ Backend processing logic
- ✅ Database interaction
- ✅ Response formatting and error handling
- ✅ Custom calculator execution with formula evaluation
- ✅ Performance characteristics

All execution paths are documented from AI agent → database → response.
