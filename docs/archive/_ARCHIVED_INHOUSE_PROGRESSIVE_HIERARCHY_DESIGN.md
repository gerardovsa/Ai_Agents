# InHouse Print - Progressive Tool Discovery Hierarchy

**Date:** November 5, 2025  
**Status:** DESIGN DOCUMENT  
**Approach:** Tiered discovery system for intelligent tool navigation

---

## 🎯 Design Philosophy

Instead of overwhelming AI with all 6+ tools upfront, create a **hierarchical discovery system** where:
1. **Tier 1** (Entry Point) - Single tool that maps user intent to specialized domains
2. **Tier 2** (Domain Guides) - Specialized tools that provide deep knowledge for specific areas
3. **Tier 3** (Action Tools) - Execution tools that perform actual work

**Benefits:**
- ✅ Progressive disclosure - AI gets info when needed
- ✅ Intent-driven - AI chooses relevant path
- ✅ Scalable - Easy to add new domains
- ✅ Token efficient - Only loads necessary context
- ✅ Self-documenting - Each tier explains next steps

---

## 📊 Current Tool Analysis

### Existing 6 Tools (Flat Structure):

| Tool | Type | Purpose | Problem |
|------|------|---------|---------|
| `inhouse_get_query_library_catalog` | Meta | Browse 50+ queries | Too specific upfront |
| `inhouse_execute_sql` | Action | Run custom SQL | No schema guidance |
| `inhouse_get_calculator_requirements` | Meta | Get calc params | Too specific upfront |
| `inhouse_calculate_quote` | Action | Calculate quote | Requires prior knowledge |
| `inhouse_query_stock_levels` | Action | Check inventory | Quick but limited |
| `inhouse_get_reorder_alerts` | Action | Stock alerts | Quick but specific |

**Current Problems:**
- AI doesn't know WHERE to start
- No guidance on WHICH tool for WHICH task
- Schema/calculator knowledge not provided progressively
- AI guesses and fails (e.g., DateCreated column error)

---

## 🏗️ Proposed Hierarchical Structure

### **TIER 1: Entry Point (Single Tool)**

```
inhouse_get_domain_guide()
│
├── Returns overview of ALL InHouse capabilities
├── Maps user intent → Tier 2 tool
└── Provides next steps based on request type
```

**Purpose:** Universal entry point that directs AI to right domain

**CRITICAL USAGE GUIDANCE:**
- ⚠️ **ALWAYS call this tool FIRST** when user mentions InHouse, quotes, printing, or SQL queries
- ⚠️ **DO NOT skip to action tools** - progressive discovery prevents errors
- ⚠️ **READ the suggested domain guide** before executing any actions
- ⚠️ **For calculators:** MUST call `inhouse_calculator_guide()` → `inhouse_get_calculator_requirements()` → THEN calculate
- ⚠️ **For SQL queries:** MUST call `inhouse_database_guide()` to get schema BEFORE writing SQL

**Input:** User request (optional description of what they need)

**Output:**
```json
{
  "domains": [
    {
      "domain": "quotes_and_calculations",
      "description": "Calculate quotes for print products (business cards, flyers, booklets, etc.)",
      "when_to_use": "User asks for pricing, quotes, or cost calculations",
      "next_tool": "inhouse_calculator_guide",
      "example_requests": [
        "Quote for 1000 business cards",
        "How much for 500 flyers?",
        "Calculate price for perfect bound book"
      ]
    },
    {
      "domain": "business_intelligence",
      "description": "Query sales data, customer analytics, production metrics from SQL database",
      "when_to_use": "User asks for reports, analytics, historical data, or business metrics",
      "next_tool": "inhouse_query_guide",
      "example_requests": [
        "Show top customers this year",
        "What products are selling best?",
        "Production bottlenecks analysis"
      ]
    },
    {
      "domain": "inventory_management",
      "description": "Check stock levels, reorder alerts, material availability",
      "when_to_use": "User asks about stock, inventory, or material availability",
      "next_tool": "inhouse_stock_guide",
      "example_requests": [
        "Check 350GSM Satin stock",
        "What stocks are low?",
        "Do we have enough paper for this order?"
      ]
    },
    {
      "domain": "custom_sql",
      "description": "Write custom SQL queries for specific data needs",
      "when_to_use": "Complex queries not covered by pre-built queries",
      "next_tool": "inhouse_database_guide",
      "example_requests": [
        "Custom analysis across multiple tables",
        "Complex JOIN operations",
        "Data exploration"
      ]
    }
  ],
  "suggested_domain": "quotes_and_calculations",
  "reasoning": "User request contains 'quote' keyword - likely needs pricing calculation",
  "next_step": "Call inhouse_calculator_guide() to learn about calculator types and workflow",
  
  "critical_reminders": [
    "⚠️ NEVER skip directly to action tools - always read the domain guide first",
    "⚠️ For quotes: MUST call inhouse_calculator_guide() → inhouse_get_calculator_requirements() → THEN calculate_quote",
    "⚠️ For SQL: MUST call inhouse_database_guide() to get schema BEFORE execute_sql",
    "⚠️ For queries: Check inhouse_query_guide() first - pre-built queries are faster and tested",
    "⚠️ Progressive discovery prevents errors - follow the tier hierarchy"
  ],
  
  "workflow_enforcement": {
    "quotes": "Tier 1 (domain_guide) → Tier 2 (calculator_guide) → Tier 3 (get_requirements) → Tier 3 (calculate_quote)",
    "sql_queries": "Tier 1 (domain_guide) → Tier 2 (query_guide OR database_guide) → Tier 3 (execute)",
    "inventory": "Tier 1 (domain_guide) → Tier 2 (stock_guide) → Tier 3 (query_stock OR get_alerts)"
  }
}
```

---

### **TIER 2: Domain Guides (4 Specialized Tools)**

Each Tier 2 tool provides **deep knowledge** for its domain and points to **execution tools**.

---

#### **2A. inhouse_calculator_guide()**

**Purpose:** Complete guide to quote calculator system

**When to call:** User needs pricing/quote for print products

**CRITICAL USAGE GUIDANCE:**
- ⚠️ **ALWAYS call this BEFORE using any calculator** - it tells you which calculator to use
- ⚠️ **MANDATORY NEXT STEP:** After reading this guide, MUST call `inhouse_get_calculator_requirements(product_type)`
- ⚠️ **DO NOT call calculate_quote without requirements** - you'll get parameter errors
- ⚠️ **WORKFLOW ENFORCEMENT:** calculator_guide → get_calculator_requirements → calculate_quote
- ⚠️ **No shortcuts:** Requirements tool returns natural language mappings and defaults you need

**Follow-up tool chain:**
```
1. inhouse_calculator_guide() ← YOU ARE HERE
2. inhouse_get_calculator_requirements(product_type) ← MANDATORY NEXT
3. inhouse_calculate_quote(product_type, parameters) ← ONLY AFTER STEP 2
```

**Returns:**
```json
{
  "domain": "quotes_and_calculations",
  "overview": {
    "total_calculators": 10,
    "calculator_types": {
      "god_calculators": ["business_cards", "flyers"],
      "shopify_calculators": ["perfect_bound_books", "booklets", "corflute_signs", "wire_bound", "spiral_bound", "premium_business_cards", "economical_business_cards", "folded_flyers"]
    },
    "workflow_summary": "1. Get requirements → 2. Extract parameters → 3. Calculate quote"
  },
  
  "calculator_index": [
    {
      "calculator_type": "business_cards",
      "description": "Standard business cards (90x55mm) with Shopify pricing tiers",
      "typical_use": "Most common product - 80% of customers order 1000 cards, double-sided",
      "required_parameters": ["quantity", "stock_type", "sides"],
      "optional_parameters": ["finish", "turnaround"],
      "complexity": "simple",
      "next_tool": "inhouse_get_calculator_requirements",
      "next_params": {"product_type": "business_cards"}
    },
    {
      "calculator_type": "flyers",
      "description": "Flyers and leaflets (various sizes: DL, A5, A4, A3)",
      "typical_use": "Marketing materials - flexible sizing and finishing options",
      "required_parameters": ["quantity", "size", "stock_type", "sides"],
      "optional_parameters": ["folding", "finish", "turnaround"],
      "complexity": "moderate",
      "next_tool": "inhouse_get_calculator_requirements",
      "next_params": {"product_type": "flyers"}
    },
    {
      "calculator_type": "perfect_bound_books",
      "description": "Books with glued spine (professional finish)",
      "typical_use": "Manuals, catalogs, magazines with 20+ pages",
      "required_parameters": ["page_count", "cover_stock", "inner_stock", "quantity"],
      "optional_parameters": ["cover_finish", "binding_style"],
      "complexity": "complex",
      "next_tool": "inhouse_get_calculator_requirements",
      "next_params": {"product_type": "perfect_bound_books"}
    }
    // ... 7 more calculators
  ],
  
  "workflow_guidance": {
    "step_1": {
      "action": "Call inhouse_get_calculator_requirements(product_type)",
      "why": "Get complete parameter list, natural language mappings, historical patterns",
      "example": "inhouse_get_calculator_requirements('business_cards')",
      "mandatory": "YES - DO NOT skip this step or you will get parameter errors"
    },
    "step_2": {
      "action": "Extract parameters from user input OR query historical data",
      "why": "Parameters must match calculator requirements exactly",
      "options": [
        "Parse user text using natural_language_mapping from requirements",
        "Query database for customer preferences (if customer_id known)",
        "Use historical_patterns from requirements for defaults"
      ],
      "reminder": "Requirements tool tells you HOW to extract - follow its guidance"
    },
    "step_3": {
      "action": "Call inhouse_calculate_quote(product_type, parameters)",
      "why": "Generate accurate quote with pricing breakdown",
      "example": "inhouse_calculate_quote('business_cards', {quantity: 1000, stock_type: 'standard', sides: 2})",
      "prerequisite": "MUST have called get_calculator_requirements first"
    },
    "step_4_optional": {
      "action": "Check stock availability if material-specific quote",
      "why": "Verify materials are in stock before promising delivery",
      "tool": "inhouse_stock_guide() then inhouse_query_stock_levels()"
    }
  },
  
  "error_prevention": [
    "⚠️ Calling calculate_quote WITHOUT get_calculator_requirements = PARAMETER ERRORS",
    "⚠️ Skipping calculator_guide = Don't know which calculator to use",
    "⚠️ Not reading natural_language_mapping = Wrong parameter extraction",
    "⚠️ Ignoring historical_patterns = Missing sensible defaults"
  ],
  
  "common_scenarios": [
    {
      "scenario": "User says: 'Quote for 1000 business cards'",
      "path": "business_cards calculator → get_requirements → extract (quantity=1000) → use defaults → calculate",
      "expected_result": "Quote: $156.20 total ($0.156 per card), 3-5 days turnaround"
    },
    {
      "scenario": "User says: 'Price for 500 flyers, A5, double-sided, gloss finish'",
      "path": "flyers calculator → get_requirements → extract all params → calculate",
      "expected_result": "Quote with breakdown by size, finish, quantity tier"
    },
    {
      "scenario": "User says: 'Customer #456 wants their usual business cards'",
      "path": "business_cards → get_requirements → query customer_stock_preference → calculate with history",
      "expected_result": "Quote using customer's preferred stock (e.g., 350GSM Satin)"
    }
  ],
  
  "next_steps": [
    {
      "step": "Choose calculator type based on user request",
      "tool": "See calculator_index above"
    },
    {
      "step": "Get detailed requirements for chosen calculator",
      "tool": "inhouse_get_calculator_requirements(product_type)"
    },
    {
      "step": "If need historical data for parameters",
      "tool": "inhouse_query_guide() for pre-built queries"
    }
  ],
  
  "related_tools": {
    "inhouse_get_calculator_requirements": "TIER 3 - Get parameter requirements for specific calculator",
    "inhouse_calculate_quote": "TIER 3 - Execute quote calculation",
    "inhouse_query_guide": "TIER 2 - If need customer history for parameters"
  }
}
```

---

#### **2B. inhouse_query_guide()**

**Purpose:** Complete guide to business intelligence queries

**When to call:** User needs reports, analytics, or historical data

**CRITICAL USAGE GUIDANCE:**
- ⚠️ **Check pre-built queries FIRST** - they are optimized and tested
- ⚠️ **WORKFLOW:** query_guide → get_query_library_catalog → execute query
- ⚠️ **For custom SQL:** If no pre-built query fits, call `inhouse_database_guide()` to get schema BEFORE writing SQL
- ⚠️ **DO NOT write SQL without schema** - you'll get column name errors (e.g., DateCreated doesn't exist)
- ⚠️ **Pre-built queries >> Custom SQL** - use pre-built when available

**Follow-up tool chain (Option 1 - Pre-built Query):**
```
1. inhouse_query_guide() ← YOU ARE HERE
2. inhouse_get_query_library_catalog(category) ← BROWSE QUERIES
3. Execute query from catalog ← ACTION
```

**Follow-up tool chain (Option 2 - Custom SQL):**
```
1. inhouse_query_guide() ← YOU ARE HERE
2. inhouse_database_guide() ← GET SCHEMA FIRST (MANDATORY)
3. inhouse_execute_sql(query) ← WRITE SQL WITH SCHEMA KNOWLEDGE
```

**Returns:**
```json
{
  "domain": "business_intelligence",
  "overview": {
    "total_queries": 50,
    "pre_built_queries": true,
    "custom_sql_supported": true,
    "query_categories": [
      "Sales & Revenue",
      "Customer Analytics", 
      "Product Analysis",
      "Operational Metrics",
      "Operational Flow",
      "Production Planning"
    ]
  },
  
  "query_categories": [
    {
      "category": "Sales & Revenue",
      "description": "Revenue analysis, sales trends, profitability metrics",
      "query_count": 4,
      "common_questions": [
        "Who are our top customers?",
        "What's our revenue this month/year?",
        "Which products are most profitable?",
        "How do sales compare year-over-year?"
      ],
      "featured_queries": [
        {
          "query_name": "top_customers_by_revenue",
          "description": "Top N customers ranked by total revenue",
          "parameters": {"limit": 10, "date_range": "optional"},
          "typical_result": "List of customers with revenue, order count, avg order value",
          "visualization": "bar_chart"
        },
        {
          "query_name": "monthly_revenue_trend",
          "description": "Revenue by month for trend analysis",
          "parameters": {"months_back": 12},
          "typical_result": "Time series of monthly revenue totals",
          "visualization": "line_chart"
        }
      ],
      "next_tool": "inhouse_get_query_library_catalog",
      "next_params": {"category": "Sales & Revenue"}
    },
    {
      "category": "Customer Analytics",
      "description": "Customer behavior, preferences, order patterns",
      "query_count": 5,
      "common_questions": [
        "What does this customer usually order?",
        "Who are our repeat customers?",
        "What's the average customer lifetime value?",
        "Customer stock preferences?"
      ],
      "featured_queries": [
        {
          "query_name": "customer_stock_preference",
          "description": "Get customer's preferred paper stock from past orders",
          "parameters": {"customer_id": "required"},
          "typical_result": "Most frequently ordered stock with usage percentage",
          "use_case": "Quoting - pre-fill stock parameter for repeat customer"
        },
        {
          "query_name": "customer_order_history",
          "description": "Complete order history for specific customer",
          "parameters": {"customer_id": "required", "months": 12},
          "typical_result": "List of orders with products, quantities, dates, values",
          "use_case": "Understanding customer needs and patterns"
        }
      ],
      "next_tool": "inhouse_get_query_library_catalog",
      "next_params": {"category": "Customer Analytics"}
    },
    {
      "category": "Product Analysis",
      "description": "Product performance, popularity, profitability",
      "query_count": 6,
      "common_questions": [
        "What's our best-selling product?",
        "Which products have highest margins?",
        "Product mix analysis?",
        "Slow-moving products?"
      ],
      "next_tool": "inhouse_get_query_library_catalog",
      "next_params": {"category": "Product Analysis"}
    },
    {
      "category": "Operational Metrics",
      "description": "Production efficiency, turnaround times, capacity",
      "query_count": 8,
      "common_questions": [
        "What's our average turnaround time?",
        "Production bottlenecks?",
        "Orders by stage?",
        "Capacity utilization?"
      ],
      "next_tool": "inhouse_get_query_library_catalog",
      "next_params": {"category": "Operational Metrics"}
    },
    {
      "category": "Operational Flow",
      "description": "Order flow, stage transitions, job tracking",
      "query_count": 15,
      "common_questions": [
        "Jobs stuck in production?",
        "Orders by current stage?",
        "Average time per stage?",
        "Workflow efficiency?"
      ],
      "next_tool": "inhouse_get_query_library_catalog",
      "next_params": {"category": "Operational Flow"}
    },
    {
      "category": "Production Planning",
      "description": "Scheduling, resource allocation, workload planning",
      "query_count": 12,
      "common_questions": [
        "What jobs are due this week?",
        "Production schedule?",
        "Workload by staff member?",
        "Upcoming deadlines?"
      ],
      "next_tool": "inhouse_get_query_library_catalog",
      "next_params": {"category": "Production Planning"}
    }
  ],
  
  "workflow_guidance": {
    "option_1_prebuilt": {
      "step_1": "Browse queries in relevant category",
      "tool": "inhouse_get_query_library_catalog(category)",
      "step_2": "Execute chosen query",
      "tool": "Execute via catalog (returns query_name to use)",
      "when_to_use": "ALWAYS try this first - pre-built queries are faster and tested"
    },
    "option_2_custom": {
      "step_1": "Get database schema knowledge",
      "tool": "inhouse_database_guide()",
      "mandatory": "YES - DO NOT write SQL without schema",
      "step_2": "Write custom SQL query using schema",
      "tool": "inhouse_execute_sql(query)",
      "warning": "Use custom SQL only when pre-built queries don't fit - they are optimized and tested"
    }
  },
  
  "error_prevention": [
    "⚠️ Writing SQL WITHOUT database_guide = Column name errors (DateCreated, Width, Height, etc.)",
    "⚠️ Skipping query_guide = Missing pre-built query that already does what you need",
    "⚠️ Not checking get_query_library_catalog = Reinventing the wheel with custom SQL",
    "⚠️ Using custom SQL when pre-built exists = Slower, untested, error-prone"
  ],
  
  "next_steps": [
    {
      "step": "Choose query category based on user question",
      "tool": "See query_categories above"
    },
    {
      "step": "Browse specific category queries",
      "tool": "inhouse_get_query_library_catalog(category)"
    },
    {
      "step": "If no pre-built query fits, get schema for custom SQL",
      "tool": "inhouse_database_guide()"
    }
  ],
  
  "related_tools": {
    "inhouse_get_query_library_catalog": "TIER 3 - Browse queries in specific category",
    "inhouse_execute_sql": "TIER 3 - Execute custom SQL (after getting schema from database_guide)",
    "inhouse_database_guide": "TIER 2 - If need custom SQL, get schema first"
  }
}
```

---

#### **2C. inhouse_stock_guide()**

**Purpose:** Complete guide to inventory management

**When to call:** User needs stock levels, reorder alerts, or material availability

**CRITICAL USAGE GUIDANCE:**
- ⚠️ **Quick checks:** Use `inhouse_query_stock_levels()` or `inhouse_get_reorder_alerts()` for simple stock queries
- ⚠️ **Complex analysis:** Call `inhouse_database_guide()` to get ReorderAlerts table schema BEFORE custom SQL
- ⚠️ **DO NOT write stock SQL without schema** - get database_guide first
- ⚠️ **Most common use:** Quote verification (check if stock available for order)

**Follow-up tool chain (Quick checks):**
```
1. inhouse_stock_guide() ← YOU ARE HERE
2. inhouse_query_stock_levels(filters) ← FOR SPECIFIC STOCK CHECKS
   OR
   inhouse_get_reorder_alerts() ← FOR SHORTAGE DASHBOARD
```

**Follow-up tool chain (Complex analysis):**
```
1. inhouse_stock_guide() ← YOU ARE HERE
2. inhouse_database_guide() ← GET REORDERALERTS TABLE SCHEMA
3. inhouse_execute_sql(query) ← CUSTOM STOCK ANALYSIS
```

**Returns:**
```json
{
  "domain": "inventory_management",
  "overview": {
    "stock_database": "SQLite (stock_data.db)",
    "total_stocks": 50,
    "alert_system": "Reorder alerts when stock below threshold",
    "integrations": ["Calculators check stock for quotes", "Production planning uses stock data"]
  },
  
  "stock_types": [
    {
      "category": "Digital Stocks",
      "description": "Papers for digital printing (most common)",
      "examples": ["350GSM Satin", "300GSM Gloss", "400GSM Uncoated"],
      "typical_use": "Business cards, flyers, leaflets",
      "stock_count": 25
    },
    {
      "category": "Offset Stocks",
      "description": "Papers for offset printing (bulk orders)",
      "examples": ["100GSM Bond", "150GSM Gloss", "200GSM Matt"],
      "typical_use": "Large run booklets, catalogs",
      "stock_count": 15
    },
    {
      "category": "Specialty Stocks",
      "description": "Special materials (signage, packaging)",
      "examples": ["Corflute 5mm", "Foamboard 10mm", "Banner vinyl"],
      "typical_use": "Signs, displays, outdoor materials",
      "stock_count": 10
    }
  ],
  
  "common_tasks": [
    {
      "task": "Check specific stock level",
      "example": "Do we have 350GSM Satin?",
      "tool": "inhouse_query_stock_levels",
      "params": {"filters": {"stock_type": "Satin", "gsm": 350}},
      "result": "Current level, reorder point, status (ok/low/critical)"
    },
    {
      "task": "Find all low stocks",
      "example": "What stocks are running low?",
      "tool": "inhouse_get_reorder_alerts",
      "params": {},
      "result": "List of stocks below reorder point with alert levels"
    },
    {
      "task": "Check stock for quote",
      "example": "Can we fulfill order for 10,000 cards on 350GSM Satin?",
      "workflow": "1. Check current level → 2. Calculate sheets needed → 3. Compare availability",
      "tools": ["inhouse_query_stock_levels", "Calculate sheets from quote params"],
      "result": "Yes/No + current level + sheets needed"
    },
    {
      "task": "Stock availability report",
      "example": "Show me all stock levels",
      "tool": "inhouse_query_stock_levels",
      "params": {"filters": {}},
      "result": "Complete stock list with levels and statuses"
    }
  ],
  
  "workflow_guidance": {
    "quick_checks": {
      "description": "Fast stock status checks (most common)",
      "step_1": "Use inhouse_query_stock_levels(filters) for specific stocks",
      "step_2": "Use inhouse_get_reorder_alerts() for shortage dashboard",
      "when": "Quick checks, quote verification, daily monitoring",
      "no_schema_needed": "These tools are ready to use immediately"
    },
    "detailed_analysis": {
      "description": "Complex stock analysis across time or categories",
      "step_1": "Get database schema from inhouse_database_guide()",
      "mandatory": "YES - DO NOT write stock SQL without ReorderAlerts table schema",
      "step_2": "Write custom SQL query against ReorderAlerts table",
      "when": "Historical trends, forecasting, complex reporting"
    }
  },
  
  "error_prevention": [
    "⚠️ Writing stock SQL WITHOUT database_guide = Table/column errors",
    "⚠️ Using custom SQL for simple checks = Unnecessary complexity",
    "⚠️ Not calling stock_guide first = Don't know which tool to use"
  ],
  
  "alert_system": {
    "alert_levels": {
      "CRITICAL": "Stock below critical_level (< 20% of reorder point)",
      "WARNING": "Stock below reorder_point but above critical",
      "OK": "Stock above reorder_point"
    },
    "checking_alerts": {
      "tool": "inhouse_get_reorder_alerts()",
      "returns": "All stocks with status != OK",
      "use_case": "Daily monitoring, production planning, procurement"
    }
  },
  
  "next_steps": [
    {
      "step": "For quick stock checks",
      "tool": "inhouse_query_stock_levels(filters)"
    },
    {
      "step": "For shortage dashboard",
      "tool": "inhouse_get_reorder_alerts()"
    },
    {
      "step": "For complex stock analysis",
      "tool": "inhouse_database_guide() then inhouse_execute_sql()"
    }
  ],
  
  "related_tools": {
    "inhouse_query_stock_levels": "TIER 3 - Check specific stock levels",
    "inhouse_get_reorder_alerts": "TIER 3 - Get shortage alerts",
    "inhouse_database_guide": "TIER 2 - For custom stock analysis SQL"
  }
}
```

---

#### **2D. inhouse_database_guide()**

**Purpose:** Complete SQL schema documentation for custom queries

**When to call:** User needs custom SQL query not covered by pre-built queries

**CRITICAL USAGE GUIDANCE:**
- ⚠️ **ALWAYS call this BEFORE execute_sql** - provides complete schema with column names, types, relationships
- ⚠️ **Prevents common errors:** DateCreated (doesn't exist), Width/Height (doesn't exist), bt.[Desc] (doesn't exist)
- ⚠️ **MANDATORY for custom SQL** - DO NOT guess column names
- ⚠️ **Check query_guide first** - pre-built queries are better than custom SQL when available
- ⚠️ **Schema includes:** Tables, columns, types, relationships, JOIN patterns, common mistakes

**Follow-up tool chain:**
```
1. inhouse_database_guide() ← YOU ARE HERE (GET SCHEMA FIRST)
2. Write SQL using schema knowledge ← USE EXACT COLUMN NAMES
3. inhouse_execute_sql(query) ← EXECUTE WITH CONFIDENCE
```

**What you get:**
- Complete table schemas (Orders, JobTickets, PaperSize, BindType, etc.)
- Column names and types (prevents "Invalid column name" errors)
- Critical notes (what columns DON'T exist)
- Common JOIN patterns (tested and working)
- SQL templates (copy and modify)
- Common mistakes to avoid (DateCreated, Width, Height, etc.)

**Returns:**
```json
{
  "domain": "custom_sql",
  "overview": {
    "database": "InHousePrintDB (SQL Server FredDEV)",
    "total_tables": 12,
    "primary_tables": ["Orders", "JobTickets", "PaperSize", "BindType", "Clients"],
    "warning": "Use pre-built queries when possible - they are optimized and tested",
    "when_to_use_custom": "Complex analysis, data exploration, queries not in library"
  },
  
  "schema": {
    "Orders": {
      "description": "Master table for all customer orders",
      "primary_key": "OrderID",
      "columns": [
        {"name": "OrderID", "type": "int", "description": "Unique order identifier"},
        {"name": "ClientName", "type": "varchar(200)", "description": "Customer/company name"},
        {"name": "OrderDate", "type": "datetime", "description": "When order was placed"},
        {"name": "DueDate", "type": "datetime", "description": "Expected completion date"},
        {"name": "OrderStatus", "type": "varchar(50)", "description": "Current status (e.g., 'Complete', 'In Progress')"}
      ],
      "relationships": [
        {"table": "JobTickets", "via": "OrderID", "type": "1:many", "description": "Orders have multiple job tickets"}
      ],
      "common_joins": [
        "INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID"
      ],
      "indexing": "OrderID (PK), ClientName (indexed), OrderDate (indexed)"
    },
    
    "JobTickets": {
      "description": "Individual jobs within orders (one order can have multiple job tickets)",
      "primary_key": "TicketID",
      "columns": [
        {"name": "TicketID", "type": "int", "description": "Unique job ticket identifier"},
        {"name": "OrderID", "type": "int", "description": "Links to Orders.OrderID (FK)"},
        {"name": "StageID", "type": "int", "description": "Production stage (1=Quote, 2=Design, 3=Approved, 4=Production, 5=Complete)"},
        {"name": "Cost", "type": "decimal(18,2)", "description": "Job cost/price"},
        {"name": "Qty", "type": "int", "description": "Quantity ordered"},
        {"name": "PaperSizeID", "type": "int", "description": "Links to PaperSize.SizeID (FK)"},
        {"name": "BindTypeID", "type": "int", "description": "Links to BindType.BindTypeID (FK)"},
        {"name": "PrintType", "type": "varchar(50)", "description": "Print color type (e.g., 'CMYK', 'Mono')"},
        {"name": "ColourStatus", "type": "varchar(50)", "description": "Production urgency (e.g., 'Red', 'Green', 'Yellow') - NOT print color!"},
        {"name": "TicketNotes", "type": "text", "description": "PRIMARY source of specifications when structured fields are NULL"},
        {"name": "InternalInvoiceComplete", "type": "bit", "description": "0=Not invoiced, 1=Invoiced"}
      ],
      "critical_notes": [
        "⚠️ NO DateCreated column! Use Orders.OrderDate for date filtering",
        "⚠️ ColourStatus is production urgency (Red/Yellow/Green), NOT print color",
        "⚠️ PrintType is actual print color (CMYK/Mono), NOT ColourStatus",
        "⚠️ TicketNotes is PRIMARY source when structured columns are NULL"
      ],
      "relationships": [
        {"table": "Orders", "via": "OrderID", "type": "many:1"},
        {"table": "PaperSize", "via": "PaperSizeID", "type": "many:1"},
        {"table": "BindType", "via": "BindTypeID", "type": "many:1"}
      ],
      "common_joins": [
        "INNER JOIN Orders o ON jt.OrderID = o.OrderID",
        "LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID",
        "LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindTypeID"
      ]
    },
    
    "PaperSize": {
      "description": "Paper size definitions (A4, DL, business card, etc.)",
      "primary_key": "SizeID",
      "columns": [
        {"name": "SizeID", "type": "int", "description": "Unique size identifier"},
        {"name": "[Desc]", "type": "varchar(100)", "description": "Size description (e.g., 'A4', 'DL', 'BC - 90x55')"}
      ],
      "critical_notes": [
        "⚠️ NO Width/Height columns exist! Size info is in [Desc] field only",
        "⚠️ Use square brackets: ps.[Desc] (reserved keyword)"
      ],
      "common_patterns": [
        "Business cards: 'BC - 90x55'",
        "DL flyer: 'DL'",
        "A4: 'A4'"
      ]
    },
    
    "BindType": {
      "description": "Binding type definitions (saddle stitch, perfect bound, etc.)",
      "primary_key": "BindTypeID",
      "columns": [
        {"name": "BindTypeID", "type": "int", "description": "Unique binding type identifier"},
        {"name": "BindTypeDesc", "type": "varchar(100)", "description": "Binding description (e.g., 'Saddle Stitch', 'Perfect Bound', 'Wire-O')"}
      ],
      "critical_notes": [
        "⚠️ Use BindTypeDesc, NOT [Desc] column (doesn't exist)!"
      ],
      "common_patterns": [
        "Booklets: 'Saddle Stitch'",
        "Books: 'Perfect Bound'",
        "Notebooks: 'Wire-O' or 'Spiral Bound'"
      ]
    }
  },
  
  "sql_patterns": {
    "basic_order_query": {
      "description": "Get orders with job details",
      "template": "SELECT o.ClientName, jt.Cost, ps.[Desc] as PaperSize, bt.BindTypeDesc\\nFROM Orders o\\nINNER JOIN JobTickets jt ON o.OrderID = jt.OrderID\\nLEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID\\nLEFT JOIN BindType bt ON jt.BindTypeID = bt.BindTypeID\\nWHERE o.OrderDate >= DATEADD(month, -12, GETDATE())",
      "use_case": "Most common query pattern"
    },
    "date_filtering": {
      "description": "Filter by date range",
      "correct": "WHERE o.OrderDate >= DATEADD(day, -30, GETDATE())",
      "wrong": "WHERE jt.DateCreated >= ... -- NO DateCreated column!",
      "note": "Always use Orders.OrderDate for date filtering"
    },
    "stage_filtering": {
      "description": "Filter by production stage",
      "template": "WHERE jt.StageID = 4  -- 4 = Production stage",
      "stages": {
        "1": "Quote",
        "2": "Design",
        "3": "Approved",
        "4": "Production",
        "5": "Complete"
      }
    },
    "incomplete_jobs": {
      "description": "Get not-yet-invoiced jobs",
      "template": "WHERE jt.InternalInvoiceComplete = 0"
    }
  },
  
  "best_practices": [
    "✅ ALWAYS call database_guide BEFORE execute_sql",
    "✅ Always use TOP N to limit results (e.g., SELECT TOP 20)",
    "✅ JOIN Orders → JobTickets → PaperSize → BindType for complete info",
    "✅ Use Orders.OrderDate for date filtering (NOT jt.DateCreated - doesn't exist)",
    "✅ Use ps.[Desc] for paper size (square brackets - reserved word)",
    "✅ Use bt.BindTypeDesc for binding (NOT bt.[Desc] - doesn't exist)",
    "✅ Check TicketNotes for specs when structured columns are NULL",
    "⚠️ Avoid SELECT * - be explicit about columns",
    "⚠️ Test complex queries on small datasets first (TOP 10)"
  ],
  
  "common_mistakes": [
    {
      "mistake": "Using jt.DateCreated",
      "error": "Invalid column name 'DateCreated'",
      "fix": "Use o.OrderDate instead (must JOIN Orders table)",
      "why_it_happens": "DateCreated is a common column name, but JobTickets doesn't have it"
    },
    {
      "mistake": "Using ps.Width or ps.Height",
      "error": "Invalid column name",
      "fix": "PaperSize has NO Width/Height - only ps.[Desc] field",
      "why_it_happens": "Seems logical that size table would have dimensions, but it doesn't"
    },
    {
      "mistake": "Using bt.[Desc]",
      "error": "Invalid column name",
      "fix": "Use bt.BindTypeDesc instead",
      "why_it_happens": "Other tables use [Desc], but BindType uses BindTypeDesc"
    },
    {
      "mistake": "Assuming ColourStatus is print color",
      "error": "Logic error - returns urgency not color",
      "fix": "Use jt.PrintType for print color (CMYK/Mono)",
      "why_it_happens": "Name is misleading - ColourStatus is production urgency (Red/Yellow/Green)"
    },
    {
      "mistake": "Writing SQL without calling database_guide first",
      "error": "Multiple column name errors, failed queries",
      "fix": "ALWAYS call inhouse_database_guide() before execute_sql",
      "why_it_happens": "Guessing column names instead of reading schema"
    }
  ],
  
  "error_prevention": [
    "⚠️ Calling execute_sql WITHOUT database_guide = Multiple column name errors",
    "⚠️ Guessing column names = Trial-and-error, wasted time, user frustration",
    "⚠️ Not reading common_mistakes = Repeating same errors others made",
    "⚠️ Skipping database_guide = No knowledge of table relationships, JOIN patterns fail"
  ],
  
  "next_steps": [
    {
      "step": "Write SQL query using schema above",
      "tool": "Reference tables, columns, relationships"
    },
    {
      "step": "Execute custom SQL query",
      "tool": "inhouse_execute_sql(query)"
    },
    {
      "step": "If query fails, check common_mistakes section",
      "tool": "Review error and apply fixes"
    }
  ],
  
  "related_tools": {
    "inhouse_execute_sql": "TIER 3 - Execute your custom SQL query",
    "inhouse_query_guide": "TIER 2 - Check if pre-built query exists first"
  }
}
```

---

### **TIER 3: Action Tools (Execution)**

These are the **existing 6 tools** (unchanged):

| Tool | Type | Purpose | When Used |
|------|------|---------|-----------|
| `inhouse_get_calculator_requirements` | Meta | Get calc params | After calculator_guide |
| `inhouse_calculate_quote` | Action | Calculate quote | After getting requirements |
| `inhouse_get_query_library_catalog` | Meta | Browse queries | After query_guide |
| `inhouse_execute_sql` | Action | Run SQL | After database_guide |
| `inhouse_query_stock_levels` | Action | Check stock | After stock_guide |
| `inhouse_get_reorder_alerts` | Action | Get alerts | After stock_guide |

---

## 🔄 Complete User Journey Examples

### Example 1: Quote Request

```
User: "Quote for 1000 business cards"

AI Turn 1:
  - Calls: inhouse_get_domain_guide()
  - Receives: "quotes_and_calculations" domain suggested
  - Next: Call inhouse_calculator_guide()

AI Turn 2:
  - Calls: inhouse_calculator_guide()
  - Receives: Calculator index with business_cards info
  - Learns: Workflow is requirements → extract → calculate
  - Next: Call inhouse_get_calculator_requirements('business_cards')

AI Turn 3:
  - Calls: inhouse_get_calculator_requirements('business_cards')
  - Receives: required_parameters (quantity, stock_type, sides)
  - Receives: defaults (sides=2, stock='standard')
  - Receives: extraction_hints
  - Extracts: quantity=1000 from user input
  - Uses defaults: stock='standard', sides=2
  - Next: Call inhouse_calculate_quote()

AI Turn 4:
  - Calls: inhouse_calculate_quote('business_cards', {quantity: 1000, stock_type: 'standard', sides: 2})
  - Receives: Quote with $156.20 total, $0.156 per card
  - Presents: Complete quote to user

Total: 4 turns, progressive discovery, no errors
```

### Example 2: Business Intelligence Query

```
User: "Show me top customers this year"

AI Turn 1:
  - Calls: inhouse_get_domain_guide()
  - Receives: "business_intelligence" domain suggested
  - Next: Call inhouse_query_guide()

AI Turn 2:
  - Calls: inhouse_query_guide()
  - Receives: Query category index
  - Identifies: "Sales & Revenue" category matches request
  - Sees: top_customers_by_revenue query exists
  - Next: Call inhouse_get_query_library_catalog('Sales & Revenue')

AI Turn 3:
  - Calls: inhouse_get_query_library_catalog('Sales & Revenue')
  - Receives: 4 queries in category
  - Finds: top_customers_by_revenue with parameters
  - Executes: Query with default parameters
  - Presents: Top 10 customers with revenue data

Total: 3 turns, used pre-built query, no SQL writing needed
```

### Example 3: Custom SQL Query

```
User: "Show me jobs in production stage from last 30 days"

AI Turn 1:
  - Calls: inhouse_get_domain_guide()
  - Receives: "business_intelligence" domain suggested
  - Next: Call inhouse_query_guide()

AI Turn 2:
  - Calls: inhouse_query_guide()
  - Receives: Query categories
  - Notes: "Operational Flow" might have this query
  - Next: Check query library first

AI Turn 3:
  - Calls: inhouse_get_query_library_catalog('Operational Flow')
  - Receives: 15 queries
  - Finds: No exact match for this specific request
  - Decides: Need custom SQL
  - Next: Get schema

AI Turn 4:
  - Calls: inhouse_database_guide()
  - Receives: Complete schema
  - Learns: JobTickets has StageID column
  - Learns: NO DateCreated - must use Orders.OrderDate
  - Learns: Must JOIN Orders table
  - Writes SQL:
    SELECT jt.TicketID, o.ClientName, jt.Cost
    FROM JobTickets jt
    INNER JOIN Orders o ON jt.OrderID = o.OrderID
    WHERE jt.StageID = 4
      AND o.OrderDate >= DATEADD(day, -30, GETDATE())
  - Next: Execute query

AI Turn 5:
  - Calls: inhouse_execute_sql(query)
  - Receives: Results (10 rows)
  - Presents: Jobs in production stage

Total: 5 turns, wrote correct SQL on first try, no errors
```

---

## 📈 Benefits vs Current System

### Current System (Flat):
- ❌ AI doesn't know where to start
- ❌ Guesses column names → fails → retries
- ❌ No schema knowledge upfront
- ❌ 6+ tools presented upfront (overwhelming)
- ❌ Trial-and-error approach

### Hierarchical System:
- ✅ Clear entry point (domain_guide)
- ✅ Progressive disclosure (get info when needed)
- ✅ Schema provided BEFORE writing SQL
- ✅ Intent-driven navigation (AI chooses path)
- ✅ Self-documenting (each tier explains next)
- ✅ Error prevention (schema/requirements first)
- ✅ Scalable (easy to add new domains)

---

## 🛠️ Implementation Steps

### Phase 1: Create Tier 1 Entry Point (30 min)
- [ ] Create `inhouse_get_domain_guide()` function
- [ ] Add to schema: `inhouse_tools.json`
- [ ] Test: AI calls it first for any InHouse request

### Phase 2: Create Tier 2 Domain Guides (2 hours)
- [ ] Create `inhouse_calculator_guide()` function
- [ ] Create `inhouse_query_guide()` function
- [ ] Create `inhouse_stock_guide()` function
- [ ] Create `inhouse_database_guide()` function
- [ ] Add all 4 to schema
- [ ] Test: AI calls appropriate guide based on domain

### Phase 3: Update System Prompt (15 min)
- [ ] Remove detailed schema from system prompt
- [ ] Add brief hint: "Use inhouse_get_domain_guide() first"
- [ ] Add workflow: Tier 1 → Tier 2 → Tier 3

### Phase 4: Test End-to-End (1 hour)
- [ ] Test: Quote calculation flow (3-4 turns)
- [ ] Test: Pre-built query flow (2-3 turns)
- [ ] Test: Custom SQL flow (4-5 turns)
- [ ] Test: Stock check flow (2-3 turns)
- [ ] Verify: No schema errors (DateCreated, Width/Height, etc.)

---

## ✅ Success Criteria

- **Progressive Discovery:** AI gets info in stages (not all upfront)
- **Intent Detection:** AI chooses correct domain based on user request
- **Error Prevention:** AI gets schema BEFORE writing SQL (no column errors)
- **Efficiency:** Quote calculations in 3-4 turns (vs 6-8 with trial-and-error)
- **Scalability:** Easy to add new domains/tools without overwhelming AI
- **Self-Documenting:** Each tool explains next steps clearly

---

**Ready to implement this hierarchical system?**

**Estimated Time:** 4 hours total  
**Impact:** Eliminates trial-and-error, reduces token usage, prevents schema errors, provides better UX

---

**END OF DESIGN DOCUMENT**
