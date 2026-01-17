"""
InHouse Print Hybrid Tools Wrapper
Bridges AI_agents registry to quote-calculator backend via singleton pattern

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

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
# From: inhouse-print/implementations/ -> inhouse-print/ -> modules_external/ -> quote-calculator/backend/
quote_calc_backend = os.path.abspath(os.path.join(current_dir, '..', '..', 'quote-calculator', 'backend'))

# Add quote-calculator backend to Python path (contains tool_use_agent.py)
if quote_calc_backend not in sys.path:
    sys.path.insert(0, quote_calc_backend)

# ⚠️ DISABLED: ToolUseAgent import causes circular dependencies on Render
# InHouse Print tools use direct database access via db_connector.py instead
# See INHOUSE_TOOLS_COMPLETE_FIX_JAN13_2026.md for architecture details
ToolUseAgent = None
print("[InHouse Wrapper] ℹ️ Using direct database access (ToolUseAgent disabled)")

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
    
    if ToolUseAgent is None:
        raise ImportError("ToolUseAgent could not be imported - check backend path and dependencies")
    
    if _agent_instance is None:
        # Load database configuration from Supabase (Render) or database-config.json (Local)
        # Uses AI_infrastructure/auth/supabase_credentials.py for environment-aware loading
        
        try:
            # Import credentials manager
            import sys
            import os
            import json
            
            # Path calculation: From UI/modules_external/inhouse-print/implementations/
            # To: AI_infrastructure/auth/ (need to go up 5 levels to project root)
            # Levels: implementations -> inhouse-print -> modules_external -> UI -> AI_agents (root)
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent.parent
            credentials_path = project_root / 'AI_infrastructure' / 'auth'
            
            # Debug: Print paths for troubleshooting
            print(f"[InHouse Wrapper] Current file: {current_file}")
            print(f"[InHouse Wrapper] Project root: {project_root}")
            print(f"[InHouse Wrapper] Credentials path: {credentials_path}")
            print(f"[InHouse Wrapper] Path exists: {credentials_path.exists()}")
            
            # Add to Python path if not already there
            credentials_path_str = str(credentials_path)
            if credentials_path_str not in sys.path:
                sys.path.insert(0, credentials_path_str)
                print(f"[InHouse Wrapper] Added to sys.path: {credentials_path_str}")
            
            from supabase_credentials import get_database_config
            
            # Get config (auto-detects Render vs Local)
            print("[InHouse Wrapper] Loading database configuration...")
            config = get_database_config()
            
            # Write config to a fixed location in project root
            # This is needed because ToolUseAgent constructs paths relative to backend folder
            config_dir = project_root / 'config'
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / 'database-config-runtime.json'
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"[InHouse Wrapper] Config written to: {config_file}")
            print(f"[InHouse Wrapper] Initializing ToolUseAgent...")
            
            # Pass relative path from backend folder to config
            _agent_instance = ToolUseAgent(str(config_file))
            print("[InHouse Wrapper] Singleton ToolUseAgent initialized successfully")
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            raise RuntimeError(
                f"Failed to initialize InHouse Print tools: {e}\n"
                f"Details: {error_details}\n"
                f"Ensure Supabase credentials are configured correctly"
            )
    
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
    # ✅ FIX: Bypass ToolUseAgent - return hardcoded catalog for now
    # TODO: Load from query_library.json file in backend/
    queries = [
        {
            "name": "customer_order_history",
            "category": "Customer Analytics",
            "description": "Get all orders for a specific customer",
            "parameters": ["customer_name"],
            "example": "Find orders for 'Neilson Design'"
        },
        {
            "name": "recent_orders",
            "category": "Operational Flow",
            "description": "Get most recent orders",
            "parameters": ["days_back"],
            "example": "Orders from last 7 days"
        },
        {
            "name": "urgent_orders",
            "category": "Operational Flow",
            "description": "Get all urgent orders not yet invoiced",
            "parameters": [],
            "example": "Find all rush orders"
        },
        {
            "name": "customer_lifetime_value",
            "category": "Customer Analytics",
            "description": "Calculate total revenue from customer",
            "parameters": ["customer_name"],
            "example": "Total spent by CJ King Printing"
        },
        {
            "name": "top_customers_by_revenue",
            "category": "Sales & Revenue",
            "description": "Top N customers by total revenue",
            "parameters": ["limit"],
            "example": "Top 20 customers"
        }
    ]
    
    # Filter by category if specified
    if category:
        queries = [q for q in queries if q['category'] == category]
    
    return {
        "success": True,
        "queries": queries,
        "total_count": len(queries),
        "note": "Full query library loading requires ToolUseAgent - this is a minimal catalog"
    }


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
    # ✅ FIX: Bypass ToolUseAgent and use InHousePrintDB directly
    try:
        # Import with proper path resolution
        import sys
        from pathlib import Path
        
        # Calculate path to db_connector.py (one level up from implementations/)
        db_connector_dir = Path(__file__).resolve().parent.parent
        if str(db_connector_dir) not in sys.path:
            sys.path.insert(0, str(db_connector_dir))
        
        from db_connector import InHousePrintDB
        
        # Initialize DB connection (auto-detects Supabase vs local config)
        db = InHousePrintDB()
        
        # Execute query and return results as list of dicts
        results = db.execute_query(query)
        
        if results is None:
            return []
        
        # Convert DataFrame to list of dicts if needed
        if hasattr(results, 'to_dict'):
            return results.to_dict('records')
        
        return results
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        raise RuntimeError(
            f"SQL execution failed: {e}\n"
            f"Query: {query}\n"
            f"Details: {error_details}"
        )


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
    # ✅ FIX (Jan 13, 2026): Use registry to get tool schema instead of importing non-existent calculator
    try:
        import sys
        from pathlib import Path
        
        # Add AI_infrastructure to path to access registry
        ai_infra_dir = Path(__file__).resolve().parent.parent.parent.parent / 'AI_infrastructure'
        if str(ai_infra_dir) not in sys.path:
            sys.path.insert(0, str(ai_infra_dir))
        
        # Add tools directory to path
        tools_dir = Path(__file__).resolve().parent.parent.parent.parent / 'tools'
        if str(tools_dir) not in sys.path:
            sys.path.insert(0, str(tools_dir))
        
        from registry_v3 import RegistryV3
        
        # Initialize registry
        registry = RegistryV3()
        
        # Map product_type to calculator tool name
        calculator_map = {
            "business_cards": "calculate_business_cards",
            "flyers": "calculate_folded_flyers_shopify",
            "folded_flyers": "calculate_folded_flyers_shopify",
            "perfect_bound_books": "calculate_perfect_bound_books_shopify",
            "wire_bound": "calculate_wire_bound_books_shopify",
            "spiral_bound": "calculate_spiral_bound_books_shopify"
        }
        
        tool_name = calculator_map.get(product_type.lower())
        if not tool_name:
            return {
                "success": False,
                "error": f"Unknown product type: {product_type}",
                "available_types": list(calculator_map.keys())
            }
        
        # Get tool schema from registry
        tool_schema = registry.get_tool(tool_name)
        
        if not tool_schema:
            return {
                "success": False,
                "error": f"Calculator tool not found: {tool_name}"
            }
        
        # Extract parameters from schema
        parameters = tool_schema.get("input_schema", {}).get("properties", {})
        required = tool_schema.get("input_schema", {}).get("required", [])
        
        # Build requirements response
        requirements = {
            "product_type": product_type,
            "calculator_tool": tool_name,
            "parameters": {},
            "natural_language_mapping": {
                "300gsm satin": "stock_type='satin_300gsm'",
                "350gsm satin": "stock_type='satin_350gsm'",
                "matt cello both sides": "celloglaze='2_side_matt'",
                "gloss cello both sides": "celloglaze='2_side_gloss'"
            },
            "historical_patterns": {
                "most_common": {
                    "stock_type": "satin_350gsm",
                    "celloglaze": "2_side_matt"
                }
            }
        }
        
        # Process each parameter
        for param_name, param_schema in parameters.items():
            requirements["parameters"][param_name] = {
                "type": param_schema.get("type"),
                "description": param_schema.get("description"),
                "required": param_name in required,
                "enum": param_schema.get("enum", [])
            }
        
        return {
            "success": True,
            "requirements": requirements
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": f"Failed to get calculator requirements: {e}",
            "details": traceback.format_exc()
        }


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
    # ✅ FIX (Jan 13, 2026): Use registry to execute calculator tool directly
    try:
        import sys
        import json
        from pathlib import Path
        
        # Add AI_infrastructure and tools to path
        ai_infra_dir = Path(__file__).resolve().parent.parent.parent.parent / 'AI_infrastructure'
        tools_dir = Path(__file__).resolve().parent.parent.parent.parent / 'tools'
        
        for path_to_add in [ai_infra_dir, tools_dir]:
            if str(path_to_add) not in sys.path:
                sys.path.insert(0, str(path_to_add))
        
        from registry_v3 import RegistryV3
        
        # Initialize registry
        registry = RegistryV3()
        
        # Handle both JSON string and dict parameters (from registry)
        if isinstance(parameters, str):
            parameters = json.loads(parameters)
        
        # Map product_type to calculator tool name
        calculator_map = {
            "business_cards": "calculate_business_cards",
            "flyers": "calculate_folded_flyers_shopify",
            "folded_flyers": "calculate_folded_flyers_shopify",
            "perfect_bound_books": "calculate_perfect_bound_books_shopify",
            "wire_bound": "calculate_wire_bound_books_shopify",
            "spiral_bound": "calculate_spiral_bound_books_shopify"
        }
        
        tool_name = calculator_map.get(product_type.lower())
        if not tool_name:
            return {
                "success": False,
                "error": f"Unknown product type: {product_type}",
                "available_types": list(calculator_map.keys())
            }
        
        # Execute calculator tool via registry
        # Note: execute_tool expects tool_name in kwargs
        result = registry.execute_tool(tool_name=tool_name, **parameters)
        
        return {
            "success": True,
            "product_type": product_type,
            "quote": result
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return {
            "success": False,
            "error": f"Failed to calculate quote: {e}",
            "details": error_details
        }


def inhouse_query_stock_levels(filters: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
    """
    Quick inventory check
    
    Queries Supabase stock_data.stocklevels table (not InHouse Fred database).
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
    try:
        # Import Supabase query utility
        from AI_infrastructure.shared.database_utils import execute_query
        
        # ⚠️ FIRST: Check if stock_data.stocklevels table exists
        # If it doesn't, fall back to unified_stocks table
        check_query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'stock_data' 
                AND table_name = 'stocklevels'
            )
        """
        table_exists = execute_query(check_query, (), fetch_mode='value')
        
        if not table_exists:
            # Fallback: Use unified_stocks table instead
            return {
                "success": False,
                "error": "stock_data.stocklevels table does not exist",
                "suggestion": "Use supabase_execute_query tool to query stock_data.unified_stocks instead",
                "available_tables": ["stock_data.unified_stocks", "stock_data.extracted_jobs"]
            }
        
        # Build WHERE clause from filters
        where_clauses = []
        params = []
        
        filters = filters or {}
        if filters.get('stock_type'):
            where_clauses.append("stock_description ILIKE %s")
            params.append(f"%{filters['stock_type']}%")
        if filters.get('gsm'):
            where_clauses.append("stock_description ILIKE %s")
            params.append(f"%{filters['gsm']}%")
        if filters.get('status'):
            status = filters['status'].lower()
            if status == 'critical':
                where_clauses.append("current_level <= critical_level")
            elif status == 'low':
                where_clauses.append("current_level <= reorder_point AND current_level > critical_level")
            elif status == 'ok':
                where_clauses.append("current_level > reorder_point")
        
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        
        # Query Supabase stock_data schema (MixedCase columns)
        query = f"""
            SELECT 
                "StockID" as stock_id,
                ("StockTypeDesc" || ' ' || "GSM" || 'GSM') AS description,
                "CurrentStockLevel" as current_level,
                "ReorderPoint" as reorder_point,
                "CriticalLevel" as critical_level,
                CASE 
                    WHEN "CurrentStockLevel" <= "CriticalLevel" THEN 'critical'
                    WHEN "CurrentStockLevel" <= "ReorderPoint" THEN 'low'
                    ELSE 'ok'
                END AS status
            FROM stock_data.stocklevels
            WHERE "IsActive" = 1
            {('AND ' + ' AND '.join(where_clauses)) if where_clauses else ''}
            ORDER BY "CurrentStockLevel" ASC
            LIMIT 50
        """
        
        results = execute_query(query, tuple(params), fetch_mode='all')
        
        return {
            "success": True,
            "stocks": results or []
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": f"Stock query failed: {e}",
            "details": traceback.format_exc(),
            "note": "Stock tables may not exist yet - use supabase_execute_query to check stock_data schema"
        }


def inhouse_get_reorder_alerts(**kwargs) -> Dict[str, Any]:
    """
    Quick stock shortage alerts
    
    Queries Supabase stock_data.reorderalerts table (not InHouse Fred database).
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
    try:
        # Import Supabase query utility
        from AI_infrastructure.shared.database_utils import execute_query
        
        # ⚠️ FIRST: Check if stock_data.stocklevels table exists
        check_query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'stock_data' 
                AND table_name = 'stocklevels'
            )
        """
        table_exists = execute_query(check_query, (), fetch_mode='value')
        
        if not table_exists:
            # Fallback: Provide helpful error
            return {
                "success": False,
                "error": "stock_data.stocklevels table does not exist",
                "suggestion": "Stock inventory tracking not set up yet",
                "available_tables": ["stock_data.unified_stocks (stock master data)", "stock_data.extracted_jobs (job history)"],
                "note": "Reorder alerts require stocklevels table with current_level, reorder_point, critical_level columns"
            }
        
        # Query Supabase stock_data schema for reorder alerts (MixedCase columns)
        query = """
            SELECT 
                "StockID" as stock_id,
                ("StockTypeDesc" || ' ' || "GSM" || 'GSM') AS description,
                "CurrentStockLevel" as current_level,
                "ReorderPoint" as reorder_point,
                "CriticalLevel" as critical_level,
                CASE 
                    WHEN "CurrentStockLevel" <= "CriticalLevel" THEN 'CRITICAL'
                    WHEN "CurrentStockLevel" <= "ReorderPoint" THEN 'WARNING'
                    ELSE 'OK'
                END AS alert_level,
                CURRENT_DATE AS alert_date
            FROM stock_data.stocklevels
            WHERE "IsActive" = 1 
              AND "CurrentStockLevel" IS NOT NULL
              AND "ReorderPoint" IS NOT NULL
              AND "CurrentStockLevel" <= "ReorderPoint"
            ORDER BY 
                CASE 
                    WHEN "CurrentStockLevel" <= "CriticalLevel" THEN 1
                    ELSE 2
                END,
                "CurrentStockLevel" ASC
            LIMIT 50
        """
        
        results = execute_query(query, (), fetch_mode='all')
        
        # Count alerts by level
        critical_count = len([r for r in results if r.get('alert_level') == 'CRITICAL'])
        warning_count = len([r for r in results if r.get('alert_level') == 'WARNING'])
        
        return {
            "success": True,
            "alerts": results or [],
            "critical_count": critical_count,
            "warning_count": warning_count
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": f"Reorder alerts query failed: {e}",
            "details": traceback.format_exc(),
            "note": "Stock tables may not exist yet - use supabase_execute_query to inspect stock_data schema"
        }
