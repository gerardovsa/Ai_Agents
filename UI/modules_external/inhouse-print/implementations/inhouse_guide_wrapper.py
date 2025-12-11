"""
InHouse Print Progressive Discovery Guide Tools
Hierarchical tool discovery system (3 tiers) for InHouse Print operations

PURPOSE:
- Prevent trial-and-error by guiding AI through progressive discovery
- Enforce workflows: get_requirements → calculate, get_schema → execute_sql
- Provide domain-specific guidance before action tool execution

ARCHITECTURE:
Tier 1 (Entry Point):
  - inhouse_get_domain_guide() → Maps user intent to domain

Tier 2 (Domain Guides):
  - inhouse_calculator_guide() → Quote calculation system
  - inhouse_query_guide() → Business intelligence queries
  - inhouse_stock_guide() → Inventory management
  - inhouse_database_guide() → SQL schema for custom queries

Tier 3 (Action Tools - in inhouse_wrapper.py):
  - inhouse_get_calculator_requirements()
  - inhouse_calculate_quote()
  - inhouse_get_query_library_catalog()
  - inhouse_execute_sql()
  - inhouse_query_stock_levels()
  - inhouse_get_reorder_alerts()

WORKFLOW ENFORCEMENT:
- Calculator: domain_guide → calculator_guide → get_requirements → calculate
- Pre-built Query: domain_guide → query_guide → get_catalog → execute
- Custom SQL: domain_guide → query_guide → database_guide → execute_sql
- Stock Check: domain_guide → stock_guide → query_stock_levels

NO COMPETING PATHWAYS:
- These guide tools are SEPARATE from action tools
- Guide tools return JSON guidance (not database results)
- Action tools execute operations (SQL, calculations, stock queries)
- Clear separation: Guides provide knowledge, Actions execute operations
"""

from typing import Dict, Any, Optional


def inhouse_get_domain_guide(**kwargs) -> Dict[str, Any]:
    """
    TIER 1 ENTRY POINT - Map user intent to InHouse Print domain
    
    ALWAYS call this tool FIRST when user mentions:
    - InHouse Print, quotes, printing, orders
    - SQL queries, database, customers, orders
    - Stock, inventory, paper, materials
    
    This tool is the ONLY entry point to InHouse Print system.
    DO NOT skip to action tools - progressive discovery prevents errors.
    
    Returns domain map and guides user to appropriate Tier 2 tool.
    """
    return {
        "system": "InHouse Print Management System",
        "entry_point": "inhouse_get_domain_guide",
        "tier": "TIER 1 - Universal Entry Point",
        
        "domains": [
            {
                "domain": "calculator",
                "description": "Quote calculation for printing products",
                "keywords": ["quote", "price", "cost", "calculate", "business cards", "flyers", "books", "booklets", "signs"],
                "next_tool": "inhouse_calculator_guide",
                "when_to_use": "User wants to calculate quote/price for printing products"
            },
            {
                "domain": "query",
                "description": "Business intelligence queries (pre-built and custom SQL)",
                "keywords": ["customer", "orders", "sales", "revenue", "report", "history", "analytics", "query"],
                "next_tool": "inhouse_query_guide",
                "when_to_use": "User wants to analyze data, get reports, or execute SQL queries"
            },
            {
                "domain": "stock",
                "description": "Inventory management and stock alerts",
                "keywords": ["stock", "inventory", "paper", "materials", "reorder", "shortage", "supply"],
                "next_tool": "inhouse_stock_guide",
                "when_to_use": "User wants to check inventory, reorder alerts, or stock levels"
            },
            {
                "domain": "database",
                "description": "SQL schema knowledge for custom queries",
                "keywords": ["schema", "columns", "tables", "SQL", "database structure", "custom query"],
                "next_tool": "inhouse_database_guide",
                "when_to_use": "User wants to write custom SQL or needs schema knowledge"
            }
        ],
        
        "suggested_domain": None,  # AI should analyze user intent and pick domain
        
        "next_step": "Call inhouse_calculator_guide() to learn about calculator types and workflow",
        
        "critical_reminders": [
            "ALWAYS call this tool FIRST when user mentions InHouse, quotes, printing, or SQL queries",
            "DO NOT skip to action tools - progressive discovery prevents errors",
            "For calculators: MUST call calculator_guide → get_calculator_requirements → THEN calculate",
            "For SQL queries: MUST call database_guide to get schema BEFORE writing SQL",
            "For stock checks: stock_guide recommends quick tools (no schema needed) vs complex analysis",
            "Read the guide tools - they prevent common errors (DateCreated, Width/Height, etc.)"
        ],
        
        "workflow_enforcement": {
            "calculator_workflow": {
                "steps": [
                    "inhouse_get_domain_guide() → Identify 'calculator' domain",
                    "inhouse_calculator_guide() → Learn calculator types and workflow",
                    "inhouse_get_calculator_requirements(product_type) → Get parameter requirements",
                    "inhouse_calculate_quote(product_type, parameters) → Execute calculation"
                ],
                "mandatory": "YES - Skipping get_calculator_requirements causes parameter errors"
            },
            "query_workflow": {
                "pre_built": [
                    "inhouse_get_domain_guide() → Identify 'query' domain",
                    "inhouse_query_guide() → Learn about pre-built queries",
                    "inhouse_get_query_library_catalog(category) → Browse available queries",
                    "inhouse_execute_sql(query) → Execute selected query"
                ],
                "custom_sql": [
                    "inhouse_get_domain_guide() → Identify 'query' domain",
                    "inhouse_query_guide() → Learn that custom SQL requires schema",
                    "inhouse_database_guide() → GET SCHEMA FIRST (prevents column name errors)",
                    "inhouse_execute_sql(query) → Execute custom SQL"
                ],
                "mandatory": "YES - Skipping database_guide causes 'Invalid column name' errors"
            },
            "stock_workflow": {
                "quick_check": [
                    "inhouse_get_domain_guide() → Identify 'stock' domain",
                    "inhouse_stock_guide() → Learn about quick stock tools",
                    "inhouse_query_stock_levels() or inhouse_get_reorder_alerts() → Execute"
                ],
                "complex_analysis": [
                    "inhouse_get_domain_guide() → Identify 'stock' domain",
                    "inhouse_stock_guide() → Learn that complex analysis requires schema",
                    "inhouse_database_guide() → GET SCHEMA FIRST",
                    "inhouse_execute_sql(query) → Execute custom stock SQL"
                ],
                "mandatory": "CONDITIONAL - Quick tools don't need schema, complex analysis does"
            }
        },
        
        "anti_patterns": [
            "Calling inhouse_calculate_quote WITHOUT inhouse_get_calculator_requirements",
            "Calling inhouse_execute_sql WITHOUT inhouse_database_guide (for custom SQL)",
            "Skipping domain_guide and going directly to action tools",
            "Assuming schema knowledge without reading database_guide"
        ]
    }


def inhouse_calculator_guide(**kwargs) -> Dict[str, Any]:
    """
    TIER 2A - Calculator System Guide
    
    ALWAYS call this BEFORE using any calculator.
    Explains calculator types, workflow, and parameter requirements system.
    
    MANDATORY NEXT STEP: After reading this guide, MUST call:
    - inhouse_get_calculator_requirements(product_type)
    
    DO NOT call calculate_quote without requirements - you'll get parameter errors.
    """
    return {
        "tier": "TIER 2 - Domain Guide",
        "domain": "calculator",
        "tool": "inhouse_calculator_guide",
        
        "calculator_index": {
            "god_calculator": {
                "name": "Universal GOD Calculator",
                "products": ["flyers", "business_cards"],
                "description": "Flexible parameter system, handles 90x55mm business cards when product_type='flyers'",
                "parameters": "Dynamic - call get_calculator_requirements to see all options"
            },
            "shopify_calculators": {
                "name": "Specialized Calculators",
                "products": [
                    "perfect_bound_books",
                    "corflute_signs",
                    "booklets",
                    "wire_bound",
                    "spiral_bound",
                    "premium_business_cards",
                    "economical_business_cards",
                    "folded_flyers"
                ],
                "description": "Product-specific calculators with optimized pricing",
                "parameters": "Product-specific - MUST call get_calculator_requirements for each type"
            }
        },
        
        "workflow_guidance": {
            "step_1": {
                "tool": "inhouse_get_calculator_requirements(product_type)",
                "description": "Get complete parameter requirements, natural language mappings, historical patterns",
                "mandatory": "YES - DO NOT skip this step or you will get parameter errors",
                "returns": "parameters dict (types, required flags, options, defaults), natural_language_mapping (text → params), historical_patterns (common values)"
            },
            "step_2": {
                "tool": "Parse user input or TicketNotes",
                "description": "Extract parameters from user request or JobTickets.TicketNotes using natural_language_mapping from step 1",
                "techniques": [
                    "Use natural_language_mapping: '350gsm satin' → 'satin_350gsm'",
                    "Use historical_patterns for defaults: Most common is satin_350gsm with 2_side_matt",
                    "Check extraction_strategy for TicketNotes parsing patterns"
                ]
            },
            "step_3": {
                "tool": "inhouse_calculate_quote(product_type, parameters)",
                "description": "Calculate quote with validated parameters",
                "prerequisite": "MUST have called get_calculator_requirements first",
                "returns": "cost_ex_gst, cost_inc_gst, cost_to_business, profit_margin, specifications, breakdown"
            }
        },
        
        "natural_language_handling": {
            "description": "get_calculator_requirements returns mapping of natural language phrases to parameter values",
            "examples": [
                {
                    "user_says": "350gsm satin with matt cello both sides",
                    "mapping": {
                        "350gsm satin": "stock_type='satin_350gsm'",
                        "matt cello both sides": "celloglaze='2_side_matt'"
                    }
                },
                {
                    "user_says": "standard business cards, 1000 quantity",
                    "mapping": {
                        "standard business cards": "product_type='business_cards', stock_type='satin_350gsm'",
                        "1000 quantity": "quantity=1000"
                    }
                }
            ]
        },
        
        "historical_patterns": {
            "description": "get_calculator_requirements returns most common parameter combinations from database",
            "usage": "Use these as sensible defaults when user doesn't specify",
            "example": {
                "most_common": {
                    "stock_type": "satin_350gsm",
                    "celloglaze": "2_side_matt",
                    "perforation": "none"
                }
            }
        },
        
        "error_prevention": [
            "Calling calculator WITHOUT get_tool_schema = PARAMETER ERRORS",
            "Skipping calculator_guide = Don't know which calculator to use",
            "Not checking enum values in schema = Invalid parameter values",
            "Guessing parameters instead of reading schema = Wrong types or missing required fields"
        ],
        
        "next_steps": [
            "1. Call get_tool_schema('calculate_business_cards') to get parameter requirements from schema",
            "2. Parse user input using enum values and descriptions from schema",
            "3. Call calculate_business_cards(quantity=1000, ...) with validated parameters"
        ],
        
        "available_calculators": {
            "business_cards": "calculate_business_cards",
            "flyers": "calculate_flyers",
            "booklets": "calculate_booklets",
            "perfect_bound_books": "calculate_perfect_bound_books",
            "spiral_bound_books": "calculate_spiral_bound_books_shopify",
            "wire_bound_books": "calculate_wire_bound_books_shopify",
            "letterheads": "calculate_letterheads",
            "corflute_signs": "calculate_corflute_signs",
            "note": "Total of 37 calculators available - use list_platform_tools('quote_calculator') to see all"
        },
        
        "follow_up_tool_chain": {
            "description": "MANDATORY workflow after reading this guide",
            "steps": [
                {
                    "step": 1,
                    "tool": "inhouse_calculator_guide()",
                    "status": "YOU ARE HERE",
                    "action": "Read this guide to understand calculator system"
                },
                {
                    "step": 2,
                    "tool": "get_tool_schema('calculate_business_cards')",
                    "status": "NEXT (MANDATORY)",
                    "action": "Get parameter requirements, enums, examples from calculator schema"
                },
                {
                    "step": 3,
                    "tool": "calculate_business_cards(quantity, finish_size, stock_type, print_sides, celloglaze)",
                    "status": "FINAL",
                    "action": "Execute calculator with validated parameters from schema"
                }
            ],
            "ascii_diagram": """
            1. inhouse_calculator_guide() ← YOU ARE HERE
                    ↓
            2. get_tool_schema('calculate_business_cards') ← MANDATORY NEXT
                    ↓
            3. calculate_business_cards(...) ← FINAL EXECUTION
            """
        }
    }


def inhouse_query_guide(**kwargs) -> Dict[str, Any]:
    """
    TIER 2B - Query System Guide
    
    Explains pre-built queries (50+ optimized queries) vs custom SQL.
    CRITICAL: For custom SQL, MUST call inhouse_database_guide() to get schema BEFORE writing SQL.
    
    NEXT STEPS:
    - Option 1 (Pre-built): Call inhouse_get_query_library_catalog(category)
    - Option 2 (Custom SQL): Call inhouse_database_guide() FIRST (MANDATORY)
    """
    return {
        "tier": "TIER 2 - Domain Guide",
        "domain": "query",
        "tool": "inhouse_query_guide",
        
        "query_categories": {
            "sales_revenue": {
                "category": "Sales & Revenue",
                "query_count": 4,
                "examples": ["Top customers by revenue", "Revenue by product type", "Monthly sales trends"],
                "use_case": "Financial reporting, sales analysis"
            },
            "customer_analytics": {
                "category": "Customer Analytics",
                "query_count": 5,
                "examples": ["Customer order history", "Customer lifetime value", "Repeat customer analysis"],
                "use_case": "Customer relationship management, retention analysis"
            },
            "product_performance": {
                "category": "Product Performance",
                "query_count": 6,
                "examples": ["Best-selling products", "Product profitability", "Product demand trends"],
                "use_case": "Product strategy, inventory planning"
            },
            "operations_efficiency": {
                "category": "Operations & Efficiency",
                "query_count": 8,
                "examples": ["Average production time", "Job completion rates", "Bottleneck analysis"],
                "use_case": "Process optimization, capacity planning"
            },
            "operational_flow": {
                "category": "Operational Flow",
                "query_count": 15,
                "examples": ["Orders by status", "Production queue", "Urgent jobs"],
                "use_case": "Daily operations, workflow management"
            },
            "production_planning": {
                "category": "Production Planning",
                "query_count": 12,
                "examples": ["Production schedule", "Resource allocation", "Material requirements"],
                "use_case": "Production scheduling, resource planning"
            }
        },
        
        "workflow_guidance": {
            "option_1_pre_built_queries": {
                "when": "User request matches common reports (sales, customers, products, operations)",
                "advantage": "Optimized, tested, fast - 50+ queries available",
                "steps": [
                    {
                        "step": 1,
                        "tool": "inhouse_get_query_library_catalog(category)",
                        "description": "Browse available queries by category (optional filter)"
                    },
                    {
                        "step": 2,
                        "tool": "Select appropriate query from catalog",
                        "description": "Read query descriptions and parameter requirements"
                    },
                    {
                        "step": 3,
                        "tool": "inhouse_execute_sql(query)",
                        "description": "Execute selected query with parameters"
                    }
                ],
                "no_schema_needed": "Pre-built queries are already validated and tested"
            },
            "option_2_custom_sql": {
                "when": "User request is unique, no pre-built query fits",
                "warning": "MUST call inhouse_database_guide() to get schema BEFORE writing SQL",
                "steps": [
                    {
                        "step": 1,
                        "tool": "inhouse_database_guide()",
                        "description": "GET SCHEMA FIRST - prevents 'Invalid column name' errors",
                        "mandatory": "YES - DO NOT write SQL without schema knowledge"
                    },
                    {
                        "step": 2,
                        "tool": "Write custom SQL using schema knowledge",
                        "description": "Use table schemas, JOIN patterns, and common_mistakes list from database_guide"
                    },
                    {
                        "step": 3,
                        "tool": "inhouse_execute_sql(query)",
                        "description": "Execute custom SQL with schema-validated column names"
                    }
                ],
                "schema_mandatory": "YES - Prevents DateCreated, Width/Height, bt.[Desc] errors"
            }
        },
        
        "error_prevention": [
            "Calling execute_sql for custom query WITHOUT database_guide = 'Invalid column name' errors",
            "Skipping query_library_catalog = Missing optimized pre-built queries",
            "Writing SQL without reading common_mistakes in database_guide = Repeating known errors",
            "Not checking pre-built queries first = Reinventing the wheel"
        ],
        
        "next_steps": [
            "Decision point: Pre-built query or custom SQL?",
            "Pre-built: Call inhouse_get_query_library_catalog(category) to browse queries",
            "Custom SQL: Call inhouse_database_guide() FIRST to get schema knowledge"
        ],
        
        "follow_up_tool_chain": {
            "description": "Two possible workflows after reading this guide",
            "option_1_pre_built": {
                "steps": [
                    {
                        "step": 1,
                        "tool": "inhouse_query_guide()",
                        "status": "YOU ARE HERE",
                        "action": "Read this guide to understand query options"
                    },
                    {
                        "step": 2,
                        "tool": "inhouse_get_query_library_catalog(category)",
                        "status": "NEXT (Check pre-built queries FIRST)",
                        "action": "Browse 50+ optimized queries"
                    },
                    {
                        "step": 3,
                        "tool": "inhouse_execute_sql(query)",
                        "status": "FINAL",
                        "action": "Execute selected pre-built query"
                    }
                ],
                "ascii_diagram": """
                1. inhouse_query_guide() ← YOU ARE HERE
                        ↓
                2. inhouse_get_query_library_catalog(category) ← Check pre-built FIRST
                        ↓
                3. inhouse_execute_sql(query) ← Execute
                """
            },
            "option_2_custom_sql": {
                "steps": [
                    {
                        "step": 1,
                        "tool": "inhouse_query_guide()",
                        "status": "YOU ARE HERE",
                        "action": "Read this guide to understand need for schema"
                    },
                    {
                        "step": 2,
                        "tool": "inhouse_database_guide()",
                        "status": "NEXT (MANDATORY for custom SQL)",
                        "action": "GET SCHEMA FIRST - prevents column name errors"
                    },
                    {
                        "step": 3,
                        "tool": "Write custom SQL using schema",
                        "status": "INTERMEDIATE",
                        "action": "Use table schemas, JOIN patterns, common_mistakes from database_guide"
                    },
                    {
                        "step": 4,
                        "tool": "inhouse_execute_sql(query)",
                        "status": "FINAL",
                        "action": "Execute schema-validated SQL"
                    }
                ],
                "ascii_diagram": """
                1. inhouse_query_guide() ← YOU ARE HERE
                        ↓
                2. inhouse_database_guide() ← GET SCHEMA FIRST (MANDATORY)
                        ↓
                3. Write SQL using schema
                        ↓
                4. inhouse_execute_sql(query) ← Execute
                """
            }
        }
    }


def inhouse_stock_guide(**kwargs) -> Dict[str, Any]:
    """
    TIER 2C - Stock Management Guide
    
    Explains quick stock tools (ready to use) vs complex stock analysis (needs schema).
    
    NEXT STEPS:
    - Quick checks: Call inhouse_query_stock_levels() or inhouse_get_reorder_alerts()
    - Complex analysis: Call inhouse_database_guide() to get ReorderAlerts table schema
    """
    return {
        "tier": "TIER 2 - Domain Guide",
        "domain": "stock",
        "tool": "inhouse_stock_guide",
        
        "stock_types": {
            "paper_stock": {
                "description": "Paper/cardstock inventory (Satin, Gloss, etc.)",
                "gsm_options": [300, 350, 400],
                "tracking": "Current level, reorder point, critical level"
            },
            "materials": {
                "description": "Binding materials, coatings, finishing supplies",
                "tracking": "Stock ID, description, current level, status"
            }
        },
        
        "common_tasks": {
            "quick_stock_check": {
                "description": "Check current stock levels for specific materials",
                "tool": "inhouse_query_stock_levels(filters)",
                "filters": ["stock_type (e.g., 'Satin')", "gsm (e.g., 350)", "status ('critical'|'low'|'ok')"],
                "no_schema_needed": "This tool is ready to use immediately"
            },
            "reorder_alerts": {
                "description": "Get list of stocks below reorder point",
                "tool": "inhouse_get_reorder_alerts()",
                "returns": "Stocks with CRITICAL/WARNING alerts, counts",
                "no_schema_needed": "This tool is ready to use immediately"
            },
            "complex_stock_analysis": {
                "description": "Custom SQL for stock trends, usage patterns, forecasting",
                "requires_schema": "YES - MUST call inhouse_database_guide() to get ReorderAlerts table schema",
                "tool": "inhouse_execute_sql(query) after getting schema",
                "examples": ["Stock usage over time", "Reorder frequency analysis", "Stock turnover rates"]
            }
        },
        
        "workflow_guidance": {
            "quick_checks": {
                "when": "User wants current stock levels or reorder alerts",
                "tools": ["inhouse_query_stock_levels(filters)", "inhouse_get_reorder_alerts()"],
                "no_schema_needed": "These tools are ready to use immediately - no database_guide call required",
                "advantage": "Fast, simple, no SQL knowledge needed"
            },
            "complex_analysis": {
                "when": "User wants stock trends, forecasting, custom reports",
                "requires_schema": "YES - MUST call inhouse_database_guide() first",
                "mandatory": "YES - DO NOT write stock SQL without ReorderAlerts table schema",
                "workflow": [
                    "1. Call inhouse_database_guide() to get ReorderAlerts table schema",
                    "2. Write custom SQL using schema knowledge",
                    "3. Call inhouse_execute_sql(query)"
                ]
            }
        },
        
        "error_prevention": [
            "Using execute_sql for stock WITHOUT database_guide = Column name errors",
            "Writing complex stock SQL without schema = Trial-and-error queries",
            "Not using quick tools first = Overcomplicating simple tasks"
        ],
        
        "next_steps": [
            "Decision point: Quick check or complex analysis?",
            "Quick: Call inhouse_query_stock_levels() or inhouse_get_reorder_alerts() directly",
            "Complex: Call inhouse_database_guide() FIRST to get schema"
        ],
        
        "follow_up_tool_chain": {
            "description": "Two possible workflows after reading this guide",
            "option_1_quick_checks": {
                "steps": [
                    {
                        "step": 1,
                        "tool": "inhouse_stock_guide()",
                        "status": "YOU ARE HERE",
                        "action": "Read this guide to understand stock tools"
                    },
                    {
                        "step": 2,
                        "tool": "inhouse_query_stock_levels() or inhouse_get_reorder_alerts()",
                        "status": "NEXT (No schema needed)",
                        "action": "Execute quick stock check"
                    }
                ],
                "ascii_diagram": """
                1. inhouse_stock_guide() ← YOU ARE HERE
                        ↓
                2. inhouse_query_stock_levels() or inhouse_get_reorder_alerts() ← READY TO USE
                """
            },
            "option_2_complex_analysis": {
                "steps": [
                    {
                        "step": 1,
                        "tool": "inhouse_stock_guide()",
                        "status": "YOU ARE HERE",
                        "action": "Read this guide to understand need for schema"
                    },
                    {
                        "step": 2,
                        "tool": "inhouse_database_guide()",
                        "status": "NEXT (MANDATORY for complex analysis)",
                        "action": "GET SCHEMA FIRST - get ReorderAlerts table structure"
                    },
                    {
                        "step": 3,
                        "tool": "inhouse_execute_sql(query)",
                        "status": "FINAL",
                        "action": "Execute custom stock SQL"
                    }
                ],
                "ascii_diagram": """
                1. inhouse_stock_guide() ← YOU ARE HERE
                        ↓
                2. inhouse_database_guide() ← GET SCHEMA FIRST (for complex analysis)
                        ↓
                3. inhouse_execute_sql(query) ← Execute custom stock SQL
                """
            }
        }
    }


def inhouse_database_guide(**kwargs) -> Dict[str, Any]:
    """
    TIER 2D - Database Schema Guide
    
    ALWAYS call this BEFORE inhouse_execute_sql when writing custom SQL.
    Provides complete schema with column names, types, relationships, and common mistakes.
    
    Prevents common errors:
    - DateCreated (doesn't exist in JobTickets)
    - Width/Height (don't exist in PaperSize)
    - bt.[Desc] (doesn't exist - use bt.BindTypeDesc)
    
    MANDATORY for custom SQL - DO NOT guess column names.
    """
    return {
        "tier": "TIER 2 - Domain Guide",
        "domain": "database",
        "tool": "inhouse_database_guide",
        
        "what_you_get": [
            "Complete table schemas (Orders, JobTickets, PaperSize, BindType, Clients) for InHouse Fred database",
            "Column names and types (prevents 'Invalid column name' errors)",
            "Critical notes (what columns DON'T exist: Status, TotalCost, DateCreated, Width/Height, bt.[Desc])",
            "Database architecture (InHouse Fred vs Supabase Stock - two separate databases)",
            "Common JOIN patterns (Orders → JobTickets → PaperSize → BindType)",
            "SQL templates (TESTED and VERIFIED query patterns)",
            "Common mistakes to avoid (with real testing results from Dec 2025)"
        ],
        
        "schema": {
            "Orders": {
                "table": "Orders",
                "alias": "o",
                "primary_key": "OrderID",
                "key_columns": {
                    "OrderID": "int (Primary Key)",
                    "CustomerMYOB_ID": "uniqueidentifier - MYOB customer reference",
                    "ClientName": "nvarchar(255) - Customer name",
                    "OrderDate": "date - Order creation date (USE THIS for date filtering)",
                    "ReadToInvoice": "bit - Ready for invoicing flag",
                    "Invoiced": "bit - Invoice status",
                    "CustomerPickup": "bit - Pickup vs delivery",
                    "Urgent": "bit - Rush order flag",
                    "DateRequired": "date - Customer requested date",
                    "InvoiceNumber": "nvarchar(50) - Invoice reference",
                    "InvoiceDate": "date - When invoiced"
                },
                "critical_note": "❌ NO Status column! ❌ NO TotalCost column! Use Invoiced flag (bit) for order status. Use o.OrderDate for date filtering - JobTickets does NOT have DateCreated column"
            },
            "JobTickets": {
                "table": "JobTickets",
                "alias": "jt",
                "primary_key": "TicketID",
                "foreign_keys": {
                    "OrderID": "References Orders.OrderID",
                    "PaperSizeID": "References PaperSize.SizeID",
                    "BindTypeID": "References BindType.BindID"
                },
                "key_columns": {
                    "TicketID": "int (Primary Key)",
                    "OrderID": "int (Foreign Key to Orders)",
                    "TicketNotes": "nvarchar(MAX) - PRIMARY source of truth for specs",
                    "QTY": "int - Quantity ordered",
                    "Cost": "decimal(10,2) - Job cost",
                    "PrintType": "nvarchar(50) - CMYK or Mono (print color)",
                    "ColourStatus": "nvarchar(50) - Red/Yellow/Green (PRODUCTION URGENCY, not print color!)",
                    "PaperSizeID": "int (Foreign Key to PaperSize)",
                    "BindTypeID": "int (Foreign Key to BindType)"
                },
                "critical_note": "NO DateCreated column! Use o.OrderDate instead (must JOIN Orders). TicketNotes is PRIMARY source when structured columns are NULL. ColourStatus is urgency, NOT print color (use PrintType for color)."
            },
            "PaperSize": {
                "table": "PaperSize",
                "alias": "ps",
                "primary_key": "SizeID",
                "key_columns": {
                    "SizeID": "int (Primary Key)",
                    "[Desc]": "nvarchar(100) - Paper size description (use square brackets - reserved word)"
                },
                "critical_note": "NO Width or Height columns! Only has SizeID and [Desc]. Use ps.[Desc] for size info."
            },
            "BindType": {
                "table": "BindType",
                "alias": "bt",
                "primary_key": "BindID",
                "key_columns": {
                    "BindID": "int (Primary Key)",
                    "BindTypeDesc": "nvarchar(100) - Binding type description"
                },
                "critical_note": "NO [Desc] column! Use bt.BindTypeDesc instead (not bt.[Desc])."
            },
            "Clients": {
                "table": "Clients",
                "alias": "c",
                "primary_key": "ClientID",
                "key_columns": {
                    "ClientID": "int (Primary Key)",
                    "ClientName": "nvarchar(255) - Client/company name",
                    "ContactName": "nvarchar(255) - Primary contact",
                    "Email": "nvarchar(255) - Contact email",
                    "Phone": "nvarchar(50) - Contact phone",
                    "Address": "nvarchar(500) - Physical address",
                    "MYOB_ID": "uniqueidentifier - MYOB customer reference"
                },
                "use_case": "Customer data, contact info lookups"
            }
        },
        
        "important_database_note": {
            "title": "🚨 STOCK DATABASE IS SEPARATE 🚨",
            "message": "ReorderAlerts, StockLevels, ConsumableInventory are in SUPABASE (stock_data schema), NOT in InHouse Fred database",
            "what_this_means": [
                "InHouse Fred Database = Orders, JobTickets, Clients, PaperSize, BindType (production data)",
                "Stock Database (Supabase) = StockLevels, ReorderAlerts, ConsumableInventory, CorfluteMaterials (inventory data)",
                "You CANNOT JOIN between these databases in a single query",
                "Use inhouse_execute_sql() for InHouse Fred queries ONLY",
                "Stock queries require separate Supabase/PostgreSQL connection"
            ],
            "examples": {
                "correct_inhouse_query": "SELECT o.OrderID, jt.QTY FROM Orders o JOIN JobTickets jt ON o.OrderID = jt.OrderID",
                "incorrect_inhouse_query": "SELECT * FROM ReorderAlerts -- ❌ This table is in Supabase, not InHouse!",
                "correct_stock_query": "Use Supabase connection to query stock_data.reorderalerts"
            }
        },
        
        "sql_patterns": {
            "basic_order_query": """
            SELECT TOP 20
                o.OrderID, 
                o.ClientName, 
                o.OrderDate,
                o.Invoiced,
                o.Urgent,
                jt.TicketNotes, 
                jt.QTY, 
                jt.Cost,
                ps.[Desc] AS PaperSize,
                bt.BindTypeDesc AS BindType
            FROM Orders o
            JOIN JobTickets jt ON o.OrderID = jt.OrderID
            LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
            LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
            WHERE o.ClientName LIKE '%customer%'
            ORDER BY o.OrderDate DESC
            """,
            "recent_orders_with_client_info": """
            SELECT TOP 20
                o.OrderID,
                o.ClientName,
                o.OrderDate,
                o.Invoiced,
                o.InvoiceNumber,
                o.DateRequired,
                o.Urgent,
                COUNT(jt.TicketID) AS TotalJobs
            FROM Orders o
            LEFT JOIN JobTickets jt ON o.OrderID = jt.OrderID
            WHERE o.OrderDate > DATEADD(month, -3, GETDATE())
            GROUP BY o.OrderID, o.ClientName, o.OrderDate, o.Invoiced, o.InvoiceNumber, o.DateRequired, o.Urgent
            ORDER BY o.OrderDate DESC
            """
        },
        
        "removed_tables": {
            "ReorderAlerts": "❌ NOT in InHouse Fred - moved to Supabase stock_data.reorderalerts",
            "StockLevels": "❌ NOT in InHouse Fred - moved to Supabase stock_data.stocklevels",
            "ConsumableInventory": "❌ NOT in InHouse Fred - moved to Supabase stock_data.consumableinventory",
            "note": "Stock/inventory data migrated from SQLite to Supabase PostgreSQL. Use separate connection for stock queries."
        },
        
        "best_practices": [
            "ALWAYS call database_guide BEFORE execute_sql",
            "Always use TOP N to limit results (e.g., SELECT TOP 20)",
            "JOIN Orders → JobTickets → PaperSize → BindType for complete info",
            "Use Orders.OrderDate for date filtering (NOT jt.DateCreated - doesn't exist)",
            "Use ps.[Desc] for paper size (square brackets - reserved word)",
            "Use bt.BindTypeDesc for binding (NOT bt.[Desc] - doesn't exist)",
            "Check TicketNotes for specs when structured columns are NULL",
            "Avoid SELECT * - be explicit about columns",
            "Test complex queries on small datasets first (TOP 10)"
        ],
        
        "common_mistakes": [
            {
                "mistake": "Using jt.DateCreated",
                "error": "Invalid column name 'DateCreated'",
                "fix": "Use o.OrderDate instead (must JOIN Orders table)",
                "why_it_happens": "DateCreated is a common column name, but JobTickets doesn't have it",
                "real_world_example": "AI tried: SELECT DateCreated FROM JobTickets WHERE... → FAILED",
                "frequency": "VERY COMMON - happened in real AI conversation"
            },
            {
                "mistake": "Using ps.Width or ps.Height",
                "error": "Invalid column name",
                "fix": "PaperSize has NO Width/Height - only ps.[Desc] field",
                "why_it_happens": "Seems logical that size table would have dimensions, but it doesn't",
                "real_world_example": "AI tried: SELECT ps.Width, ps.Height FROM... → FAILED",
                "frequency": "COMMON - logical assumption"
            },
            {
                "mistake": "Using bt.[Desc]",
                "error": "Invalid column name",
                "fix": "Use bt.BindTypeDesc instead",
                "why_it_happens": "Other tables use [Desc], but BindType uses BindTypeDesc",
                "real_world_example": "AI tried: SELECT bt.[Desc] FROM BindType → FAILED (use bt.BindTypeDesc)",
                "frequency": "COMMON - inconsistent naming"
            },
            {
                "mistake": "Querying Status from Orders",
                "error": "Invalid column name 'Status'",
                "fix": "❌ Status column does NOT exist! Use o.Invoiced (bit flag) instead",
                "why_it_happens": "Assumed Orders would have Status column - it doesn't",
                "real_world_example": "AI tried: SELECT o.Status FROM Orders o → FAILED. Use: SELECT o.Invoiced, o.ReadToInvoice FROM Orders o",
                "frequency": "VERY COMMON - tested and confirmed Dec 2025"
            },
            {
                "mistake": "Querying TotalCost from Orders",
                "error": "Invalid column name 'TotalCost'",
                "fix": "❌ TotalCost column does NOT exist! Calculate from JobTickets.Cost instead",
                "why_it_happens": "Assumed Orders would have TotalCost - must calculate from tickets",
                "real_world_example": "AI tried: SELECT o.TotalCost FROM Orders o → FAILED. Use: SELECT SUM(jt.Cost) AS TotalCost FROM JobTickets jt WHERE jt.OrderID = ?",
                "frequency": "VERY COMMON - tested and confirmed Dec 2025"
            },
            {
                "mistake": "Querying ReorderAlerts from InHouse database",
                "error": "Invalid object name 'ReorderAlerts'",
                "fix": "❌ ReorderAlerts table NOT in InHouse! It's in Supabase stock_data.reorderalerts",
                "why_it_happens": "Stock data was migrated from InHouse to Supabase (separate database)",
                "real_world_example": "AI tried: SELECT * FROM ReorderAlerts → FAILED. This table is in Supabase PostgreSQL, not InHouse SQL Server",
                "frequency": "CRITICAL - tested and confirmed Dec 2025"
            },
            {
                "mistake": "Assuming ColourStatus is print color",
                "error": "Logic error - returns urgency not color",
                "fix": "Use jt.PrintType for print color (CMYK/Mono)",
                "why_it_happens": "Name is misleading - ColourStatus is production urgency (Red/Yellow/Green)",
                "frequency": "COMMON - misleading name"
            },
            {
                "mistake": "Using LIMIT syntax (MySQL/PostgreSQL)",
                "error": "Incorrect syntax near 'LIMIT'",
                "fix": "Use TOP instead: SELECT TOP 10 * FROM... (SQL Server syntax)",
                "why_it_happens": "InHouse uses SQL Server (not MySQL/PostgreSQL) - different syntax",
                "real_world_example": "AI tried: SELECT * FROM Orders LIMIT 10 → FAILED. Correct: SELECT TOP 10 * FROM Orders",
                "frequency": "VERY COMMON - happened in real AI conversation (Nov 2025)"
            },
            {
                "mistake": "Querying PrintTickets table columns without proper JOINs",
                "error": "Invalid column name 'Status', 'TotalCost', 'PrintType' in wrong context",
                "fix": "Status/TotalCost are in Orders table, PrintType is in JobTickets - JOIN properly",
                "why_it_happens": "Assumed columns exist in PrintTickets table without verifying schema",
                "real_world_example": "AI tried: SELECT ps.SizeID, Status, TotalCost FROM PrintTickets ps → FAILED (Status/TotalCost are in Orders, not PrintTickets)",
                "frequency": "VERY COMMON - happened in real AI conversation (Nov 2025)"
            },
            {
                "mistake": "Not JOINing PaperSize table when using ps.SizeID",
                "error": "Multi-part identifier 'ps.SizeID' could not be bound",
                "fix": "Must JOIN: LEFT JOIN PaperSize ps ON t.SizeID = ps.SizeID",
                "why_it_happens": "Used alias 'ps' without actually JOINing PaperSize table",
                "real_world_example": "AI tried: SELECT ps.SizeID FROM PrintTickets → FAILED (forgot LEFT JOIN PaperSize ps)",
                "frequency": "COMMON - forgot JOIN"
            },
            {
                "mistake": "Using backticks for column names (MySQL syntax)",
                "error": "Incorrect syntax near '`'",
                "fix": "Use square brackets [column] for reserved words (SQL Server syntax)",
                "why_it_happens": "MySQL uses backticks, SQL Server uses square brackets",
                "real_world_example": "AI tried: SELECT `Desc` FROM PaperSize → FAILED. Correct: SELECT [Desc] FROM PaperSize",
                "frequency": "COMMON - MySQL habits"
            },
            {
                "mistake": "Using double quotes for string values",
                "error": "Invalid syntax or incorrect results",
                "fix": "Use single quotes for strings: WHERE Name = 'John' (not \"John\")",
                "why_it_happens": "Some databases allow double quotes for strings, SQL Server doesn't",
                "real_world_example": "AI tried: WHERE ClientName = \"ABC Corp\" → May fail. Correct: WHERE ClientName = 'ABC Corp'",
                "frequency": "OCCASIONAL - syntax confusion"
            },
            {
                "mistake": "Writing SQL without calling database_guide first",
                "error": "Multiple column name errors, failed queries, wasted 2-3 attempts",
                "fix": "ALWAYS call inhouse_database_guide() before execute_sql",
                "why_it_happens": "Guessing column names instead of reading schema",
                "real_world_impact": "In real usage (Nov 2025), AI wasted 2-3 query rounds before calling database_guide. This could have been avoided entirely.",
                "frequency": "CRITICAL ISSUE - Most impactful mistake. Causes 40% of initial query failures."
            }
        ],
        
        "critical_sql_syntax": {
            "database_type": "SQL Server (NOT MySQL, NOT PostgreSQL, NOT SQLite)",
            "no_fallback": "🚨 NO SQLITE FALLBACK EXISTS - SQL Server only! Query errors cannot be recovered by switching databases. You must get the query right the first time.",
            "why_this_matters": "In real AI conversation (Nov 2025), wrong syntax caused immediate failure with no recovery path. SQL Server is strict - no second chances.",
            "syntax_differences": [
                {
                    "feature": "Limit Results",
                    "wrong_mysql": "SELECT * FROM Orders LIMIT 10",
                    "correct_sqlserver": "SELECT TOP 10 * FROM Orders",
                    "error_if_wrong": "Incorrect syntax near 'LIMIT'",
                    "real_occurrence": "HAPPENED IN PRODUCTION - AI used LIMIT, query failed, had to retry with TOP",
                    "auto_fix_available": "YES - system can auto-convert LIMIT to TOP (see INHOUSE_TOOLS_IMPROVEMENTS_NOV28.md)"
                },
                {
                    "feature": "String Quoting",
                    "wrong_mysql": 'SELECT * FROM Orders WHERE Name = "John"',
                    "correct_sqlserver": "SELECT * FROM Orders WHERE Name = 'John'",
                    "note": "Use single quotes for strings (double quotes are for identifiers)",
                    "severity": "MEDIUM - May work but unreliable"
                },
                {
                    "feature": "Column Name Escaping",
                    "wrong_mysql": "SELECT `Desc` FROM PaperSize",
                    "correct_sqlserver": "SELECT [Desc] FROM PaperSize",
                    "note": "Use square brackets [column] for reserved words, not backticks",
                    "error_if_wrong": "Incorrect syntax near '`'",
                    "auto_fix_available": "YES - system can auto-convert backticks to square brackets"
                },
                {
                    "feature": "TOP vs LIMIT Placement",
                    "wrong": "SELECT * FROM Orders TOP 10",
                    "correct": "SELECT TOP 10 * FROM Orders",
                    "note": "TOP goes after SELECT, not at end of query",
                    "error_if_wrong": "Incorrect syntax near 'TOP'"
                },
                {
                    "feature": "Column Existence Verification",
                    "wrong": "SELECT o.Status, o.TotalCost FROM Orders o",
                    "correct": "SELECT o.Invoiced, o.ReadToInvoice, SUM(jt.Cost) AS TotalCost FROM Orders o LEFT JOIN JobTickets jt ON o.OrderID = jt.OrderID",
                    "note": "❌ Status and TotalCost columns do NOT exist in Orders table!",
                    "error_if_wrong": "Invalid column name 'Status' or 'TotalCost'",
                    "real_occurrence": "CONFIRMED BY TESTING - Dec 2025. Guide's own SQL pattern failed.",
                    "prevention": "ALWAYS call inhouse_database_guide() first AND verify actual table structure"
                },
                {
                    "feature": "Stock Database Separation",
                    "wrong": "SELECT * FROM ReorderAlerts",
                    "correct": "Use Supabase connection: SELECT * FROM stock_data.reorderalerts",
                    "note": "Stock tables (ReorderAlerts, StockLevels, etc.) are in Supabase PostgreSQL, NOT InHouse SQL Server",
                    "error_if_wrong": "Invalid object name 'ReorderAlerts'",
                    "real_occurrence": "CONFIRMED BY TESTING - Dec 2025. ReorderAlerts does not exist in InHouse.",
                    "prevention": "Understand database architecture: InHouse = Orders/Jobs, Supabase = Stock/Inventory"
                },
                {
                    "feature": "Date Filtering",
                    "wrong": "SELECT * FROM JobTickets WHERE DateCreated > '2025-01-01'",
                    "correct": "SELECT * FROM Orders o JOIN JobTickets jt ON o.OrderID = jt.OrderID WHERE o.OrderDate > '2025-01-01'",
                    "note": "JobTickets has NO DateCreated column - use Orders.OrderDate",
                    "error_if_wrong": "Invalid column name 'DateCreated'",
                    "real_occurrence": "HAPPENED IN PRODUCTION - Common assumption that job tables have dates",
                    "prevention": "Check schema - dates are stored at order level, not ticket level"
                }
            ],
            "mandatory_syntax_rules": [
                "✅ USE TOP N (not LIMIT N) - SQL Server syntax",
                "✅ USE [brackets] (not `backticks`) - SQL Server escaping",
                "✅ USE 'single quotes' (not \"double quotes\") for strings",
                "✅ JOIN Orders first if you need: OrderDate, Invoiced, ClientName",
                "✅ LEFT JOIN PaperSize if you use ps.anything",
                "✅ LEFT JOIN BindType if you use bt.anything",
                "✅ Use o.OrderDate (NOT jt.DateCreated - doesn't exist)",
                "❌ DO NOT use o.Status - column doesn't exist! Use o.Invoiced instead",
                "❌ DO NOT use o.TotalCost - column doesn't exist! Calculate SUM(jt.Cost)",
                "❌ DO NOT query ReorderAlerts - table is in Supabase, not InHouse!",
                "✅ Use bt.BindTypeDesc (NOT bt.[Desc] - doesn't exist)",
                "✅ Call inhouse_database_guide() BEFORE writing SQL (prevents 2-3 wasted queries)",
                "✅ Verify column existence - don't assume common columns exist"
            ]
        },
        
        "error_prevention": [
            "Calling execute_sql WITHOUT database_guide = Multiple column name errors (2-3 wasted queries)",
            "Guessing column names = Trial-and-error, wasted time, user frustration",
            "Not reading common_mistakes = Repeating same errors others made",
            "Skipping database_guide = No knowledge of table relationships, JOIN patterns fail",
            "Using MySQL/PostgreSQL syntax = LIMIT, backticks, double quotes → Query fails",
            "No SQLite fallback = Get it right first time, no second chance with different database"
        ],
        
        "next_steps": [
            "1. Read schema above to understand table structure",
            "2. Review common_mistakes to avoid known errors",
            "3. Use sql_patterns as templates for your custom query",
            "4. Call inhouse_execute_sql(query) with schema-validated SQL"
        ],
        
        "follow_up_tool_chain": {
            "description": "MANDATORY workflow after reading this guide",
            "steps": [
                {
                    "step": 1,
                    "tool": "inhouse_database_guide()",
                    "status": "YOU ARE HERE",
                    "action": "Read schema, common_mistakes, sql_patterns"
                },
                {
                    "step": 2,
                    "tool": "Write custom SQL using schema knowledge",
                    "status": "NEXT",
                    "action": "Use table schemas, JOIN patterns, avoid common mistakes"
                },
                {
                    "step": 3,
                    "tool": "inhouse_execute_sql(query)",
                    "status": "FINAL",
                    "action": "Execute schema-validated SQL"
                }
            ],
            "ascii_diagram": """
            1. inhouse_database_guide() ← YOU ARE HERE (GET SCHEMA FIRST)
                    ↓
            2. Write SQL using schema
                    ↓
            3. inhouse_execute_sql(query) ← Execute with correct column names
            """
        }
    }
