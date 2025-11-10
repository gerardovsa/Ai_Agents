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

# Add backend to path (reuse quote-calculator backend)
current_dir = Path(__file__).parent
backend_path = current_dir.parent.parent / 'quote-calculator' / 'backend'

# Also add paths that tool_use_agent needs
shopify_calculators_path = backend_path / 'shopify_calculators'
complete_calculator_path = backend_path

# Add all paths in correct order
for path in [backend_path, shopify_calculators_path, complete_calculator_path]:
    path_str = str(path.resolve())
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

try:
    from tool_use_agent import ToolUseAgent
except ImportError as e:
    print(f"[InHouse Wrapper] WARNING: Could not import ToolUseAgent: {e}")
    print(f"[InHouse Wrapper] Backend path: {backend_path}")
    print(f"[InHouse Wrapper] Shopify path: {shopify_calculators_path}")
    # Don't raise - let module load without implementations
    ToolUseAgent = None

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
        # Path to database-config.json (go up to AI_agents root)
        # From: UI/external/modules/inhouse-print/implementations/inhouse_wrapper.py
        # To: config/database-config.json (6 levels up: implementations → inhouse-print → modules → external → UI → AI_agents)
        config_path = Path(__file__).parent.parent.parent.parent.parent.parent / 'config' / 'database-config.json'
        
        if not config_path.exists():
            raise FileNotFoundError(f"Database config not found: {config_path}")
        
        print(f"[InHouse Wrapper] Initializing ToolUseAgent with config: {config_path}")
        _agent_instance = ToolUseAgent(str(config_path))
        print("[InHouse Wrapper] Singleton ToolUseAgent initialized successfully")
    
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
