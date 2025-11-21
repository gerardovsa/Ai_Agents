"""
Query Library Wrapper - Pre-Built SQL Queries for Business Intelligence

Provides 50+ optimized SQL queries for AI agent access.
Auto-discovered by module_plugin_loader.py

Architecture:
    AI Agent Request
        ↓
    Registry V3
        ↓
    query_library_wrapper.py (THIS FILE)
        ↓
    backend/query_library.py (QueryLibrary class)
        ↓
    InHousePrintDB database

FILE: UI/external/modules/quote-calculator/implementations/query_library_wrapper.py
PURPOSE: Wrapper functions for QueryLibrary tools
DEPENDENCIES:
- ../backend/query_library.py (QueryLibrary class)
- inhouse_modules.db_connector (InHousePrintDB)

EXPORTS:
- get_available_queries(category="all")
- execute_query_library(query_name, parameters)

USED BY:
- tools/registry_v3.py (auto-discovery)
- AI agent (via registry)

LAST MODIFIED: 2025-11-04 - Initial creation for plugin system
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add paths for imports
module_dir = Path(__file__).parent.parent
backend_path = module_dir / "backend"
root_dir = module_dir.parent.parent.parent

# Add to sys.path
for path in [backend_path, root_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Import QueryLibrary and database connector
try:
    from query_library import QueryLibrary
    from inhouse_modules.db_connector import InHousePrintDB
    
    QUERY_LIBRARY_AVAILABLE = True
    print("✅ [Query Library Wrapper] QueryLibrary imported successfully")
    
except ImportError as e:
    QUERY_LIBRARY_AVAILABLE = False
    QueryLibrary = None
    InHousePrintDB = None
    print(f"⚠️  [Query Library Wrapper] Failed to import: {e}")
    print("   Query library tools will not be available")


# ==================== HELPER FUNCTIONS ====================

def _get_query_library(**kwargs) -> Optional[QueryLibrary]:
    """
    Get QueryLibrary instance with database connection
    
    Args:
        **kwargs: May contain db_connector or config_path
    
    Returns:
        QueryLibrary instance or None if unavailable
    """
    if not QUERY_LIBRARY_AVAILABLE:
        return None
    
    try:
        # Try to get database connection from kwargs
        db_connector = kwargs.get('db_connector')
        
        if not db_connector:
            # Create database connection - works both locally and on Render.com
            if os.environ.get('RENDER') == 'true':
                # Render deployment: Use /app root
                config_path = Path('/app/config/database-config.json')
            else:
                # Local development: Use root_dir
                config_path = root_dir / "config" / "database-config.json"
            
            if not config_path.exists():
                print(f"⚠️  [Query Library] Config not found: {config_path}")
                return None
            
            db_connector = InHousePrintDB(str(config_path))
        
        # Create QueryLibrary instance
        query_lib = QueryLibrary(db_connector)
        
        return query_lib
        
    except Exception as e:
        print(f"⚠️  [Query Library] Initialization failed: {e}")
        return None


def _format_error(error_message: str, context: str = "") -> Dict[str, Any]:
    """Format error response consistently"""
    return {
        "success": False,
        "error": error_message,
        "context": context,
        "message": "Query library unavailable. Ensure database-config.json is configured."
    }


# ==================== TOOL FUNCTIONS ====================

def get_available_queries(
    category: str = "all",
    **kwargs
) -> Dict[str, Any]:
    """
    List available pre-built queries from QueryLibrary
    
    Use this tool to discover what business intelligence queries are available.
    Queries are organized by category:
    - Sales & Revenue
    - Customer Analytics
    - Production Planning
    - Stock Management
    - Historical Quote Analysis
    
    Args:
        category: Filter by category (optional, default: all)
            Options: "Sales & Revenue", "Customer Analytics", 
                    "Production Planning", "Stock Management",
                    "Historical Quote Analysis", "all"
        **kwargs: Credential injection (db_connector, etc.)
    
    Returns:
        Dict with:
        - success: boolean
        - category: filter applied
        - query_count: number of queries found
        - queries: list of query metadata
            Each query includes:
            - name: query identifier
            - description: what the query does
            - category: which category it belongs to
            - parameters: required/optional parameters
            - visualization: recommended chart type
            - best_for: use case description
    
    Example:
        result = get_available_queries(category="Sales & Revenue")
        # Returns 4 sales-related queries with full metadata
    """
    try:
        query_lib = _get_query_library(**kwargs)
        
        if not query_lib:
            return _format_error(
                "QueryLibrary not available",
                "get_available_queries"
            )
        
        # Get queries from QueryLibrary
        category_filter = None if category == "all" else category
        queries = query_lib.get_available_queries(category=category_filter)
        
        return {
            "success": True,
            "category": category,
            "query_count": len(queries),
            "queries": queries,
            "categories_available": query_lib.get_query_categories(),
            "note": "Use execute_query_library() to run a specific query"
        }
        
    except Exception as e:
        return _format_error(
            f"Failed to get available queries: {str(e)}",
            "get_available_queries"
        )


def execute_query_library(
    query_name: str,
    parameters: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute a pre-built query from QueryLibrary
    
    IMPORTANT: Always call get_available_queries() first to see available queries
    and their required parameters.
    
    Pre-built queries are:
    - Optimized for performance
    - Tested and validated
    - Include proper parameterization
    - Return visualization metadata
    
    Args:
        query_name: Name of the query to execute (from get_available_queries)
            Examples: "sales_trend_by_month", "top_customers_detailed",
                     "daily_production_plan", "stock_inventory_master"
        parameters: Query parameters (optional, varies by query)
            Examples:
            - {"months": 6} for sales_trend_by_month
            - {"months": 12, "top_n": 10} for top_customers_detailed
            - {"days_ahead": 1} for daily_production_plan
        **kwargs: Credential injection (db_connector, etc.)
    
    Returns:
        Dict with:
        - success: boolean
        - query_name: query executed
        - parameters_used: actual parameters applied (includes defaults)
        - data: query results as list of dicts (rows)
        - metadata:
            - description: what the query returned
            - visualization: recommended chart type
            - row_count: number of rows returned
        
        On error:
        - success: False
        - error: error message
        - query_name: query that failed
    
    Example:
        # Get sales trend for last 6 months
        result = execute_query_library(
            query_name="sales_trend_by_month",
            parameters={"months": 6}
        )
        
        # Result:
        # {
        #   "success": True,
        #   "query_name": "sales_trend_by_month",
        #   "data": [
        #       {"Month": "2025-05", "TotalRevenue": 45000, "OrderCount": 120},
        #       {"Month": "2025-06", "TotalRevenue": 52000, "OrderCount": 135},
        #       ...
        #   ],
        #   "metadata": {
        #       "visualization": "line_chart",
        #       "row_count": 6
        #   }
        # }
    """
    try:
        query_lib = _get_query_library(**kwargs)
        
        if not query_lib:
            return _format_error(
                "QueryLibrary not available",
                f"execute_query_library({query_name})"
            )
        
        # Validate query exists
        query_def = query_lib.get_query_definition(query_name)
        if not query_def:
            return {
                "success": False,
                "error": f"Query '{query_name}' not found",
                "query_name": query_name,
                "suggestion": "Use get_available_queries() to see available queries"
            }
        
        # Execute query via QueryLibrary
        result = query_lib.execute_query(
            query_name=query_name,
            **(parameters or {})
        )
        
        # Check if query succeeded
        if not result.get("success"):
            return {
                "success": False,
                "error": result.get("error", "Query execution failed"),
                "query_name": query_name,
                "parameters": parameters
            }
        
        # Return formatted result
        return {
            "success": True,
            "query_name": query_name,
            "parameters_used": result.get("parameters_used", parameters or {}),
            "data": result.get("data", []),
            "metadata": {
                "description": query_def.get("description", ""),
                "category": query_def.get("category", ""),
                "visualization": query_def.get("visualization", "table"),
                "row_count": len(result.get("data", [])),
                "best_for": query_def.get("best_for", "")
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Query execution failed: {str(e)}",
            "query_name": query_name,
            "parameters": parameters
        }


# ==================== UTILITY FUNCTIONS (Optional) ====================

def get_query_definition(
    query_name: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Get detailed definition for a specific query
    
    This is a utility function - usually you'd use get_available_queries() instead.
    Use this when you need detailed parameter specifications for a specific query.
    
    Args:
        query_name: Name of query to get definition for
        **kwargs: Credential injection
    
    Returns:
        Query definition with parameters, description, visualization metadata
    """
    try:
        query_lib = _get_query_library(**kwargs)
        
        if not query_lib:
            return _format_error("QueryLibrary not available", "get_query_definition")
        
        definition = query_lib.get_query_definition(query_name)
        
        if not definition:
            return {
                "success": False,
                "error": f"Query '{query_name}' not found",
                "query_name": query_name
            }
        
        return {
            "success": True,
            "query_name": query_name,
            "definition": definition
        }
        
    except Exception as e:
        return _format_error(f"Failed to get query definition: {str(e)}", "get_query_definition")
