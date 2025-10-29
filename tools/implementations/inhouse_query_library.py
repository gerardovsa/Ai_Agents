"""
InHouse Print Query Library for AI_agents
==========================================
Pre-built SQL queries for common business intelligence needs

Provides fast access to frequently-used queries without AI having to write SQL
"""

from typing import Dict, List, Any, Optional

# Use absolute import instead of relative import
try:
    from tools.implementations.inhouse_db_connector import InHousePrintDB
except ImportError:
    # Fallback for direct execution
    from inhouse_db_connector import InHousePrintDB


class InHousePrintQueryLibrary:
    """Pre-built query library for InHouse Print business intelligence"""
    
    def __init__(self, **kwargs):
        """Initialize with database connection"""
        self.db = InHousePrintDB(**kwargs)
        self.credentials = None  # Injected at runtime
        self.query_catalog = self._build_query_catalog()
    
    def _build_query_catalog(self) -> Dict[str, Dict]:
        """Build catalog of available queries with metadata"""
        return {
            "recent_orders": {
                "name": "recent_orders",
                "category": "Orders",
                "description": "Get recent orders with client details",
                "parameters": {
                    "days": {
                        "type": "integer",
                        "default": 7,
                        "min": 1,
                        "max": 365
                    },
                    "limit": {
                        "type": "integer",
                        "default": 50,
                        "max": 500
                    }
                },
                "best_for": "Viewing recent order activity and client information"
            },
            "top_clients": {
                "name": "top_clients",
                "category": "Clients",
                "description": "Get top clients by revenue with order counts",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "default": 12,
                        "min": 1,
                        "max": 60
                    },
                    "top_n": {
                        "type": "integer",
                        "default": 20,
                        "min": 1,
                        "max": 100
                    }
                },
                "best_for": "Identifying most valuable customers"
            },
            "sales_by_month": {
                "name": "sales_by_month",
                "category": "Revenue",
                "description": "Monthly sales trends with revenue and order count",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "default": 12,
                        "min": 1,
                        "max": 60
                    }
                },
                "best_for": "Understanding revenue patterns and seasonality"
            },
            "pending_orders": {
                "name": "pending_orders",
                "category": "Operations",
                "description": "Get all non-invoiced (pending) orders",
                "parameters": {},
                "best_for": "Tracking work in progress"
            },
            "stock_levels": {
                "name": "stock_levels",
                "category": "Inventory",
                "description": "Get current stock levels from Quote_DigitalStocks",
                "parameters": {
                    "low_stock_only": {
                        "type": "boolean",
                        "default": False
                    }
                },
                "best_for": "Inventory management and reorder planning"
            }
        }
    
    def get_available_queries(self, category: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Get list of available queries
        
        Args:
            category: Optional filter by category (Orders, Clients, Revenue, Operations, Inventory)
        """
        queries = []
        for query_name, query_def in self.query_catalog.items():
            if category is None or query_def['category'] == category:
                queries.append({
                    'name': query_name,
                    'category': query_def['category'],
                    'description': query_def['description'],
                    'parameters': query_def['parameters'],
                    'best_for': query_def['best_for']
                })
        
        return {
            'success': True,
            'count': len(queries),
            'queries': queries,
            'categories': list(set(q['category'] for q in self.query_catalog.values()))
        }
    
    def execute_query(self, query_name: str, parameters: Dict = None, **kwargs) -> Dict[str, Any]:
        """
        Execute pre-built query with parameters
        
        Args:
            query_name: Name of query from catalog
            parameters: Query parameters (validated against schema)
        """
        if query_name not in self.query_catalog:
            return {
                'success': False,
                'error': f"Query '{query_name}' not found. Use get_available_queries() to see available queries."
            }
        
        query_def = self.query_catalog[query_name]
        params = parameters or {}
        
        # Validate and apply defaults
        validated_params = {}
        for param_name, param_def in query_def['parameters'].items():
            value = params.get(param_name, param_def.get('default'))
            
            # Type validation
            if value is not None and param_def['type'] == 'integer':
                value = int(value)
                # Range validation
                if 'min' in param_def and value < param_def['min']:
                    value = param_def['min']
                if 'max' in param_def and value > param_def['max']:
                    value = param_def['max']
            
            validated_params[param_name] = value
        
        # Generate SQL
        sql = self._generate_sql(query_name, validated_params)
        
        # Execute query
        result = self.db.execute_query(sql)
        
        if result['success']:
            return {
                'success': True,
                'query_name': query_name,
                'category': query_def['category'],
                'rows': result['rows'],
                'data': result['data'],
                'parameters_used': validated_params
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }
    
    def _generate_sql(self, query_name: str, params: Dict) -> str:
        """Generate SQL for specific query"""
        
        if query_name == "recent_orders":
            days = params.get('days', 7)
            limit = params.get('limit', 50)
            return f"""
                SELECT TOP {limit}
                    o.OrderID,
                    o.OrderDate,
                    c.Name AS ClientName,
                    o.TotalCost,
                    o.Invoiced,
                    o.OrderDescription
                FROM Orders o
                INNER JOIN Clients c ON o.ClientID = c.ClientID
                WHERE o.OrderDate >= DATEADD(DAY, -{days}, GETDATE())
                ORDER BY o.OrderDate DESC
            """
        
        elif query_name == "top_clients":
            months = params.get('months', 12)
            top_n = params.get('top_n', 20)
            return f"""
                SELECT TOP {top_n}
                    c.Name AS ClientName,
                    c.ClientID,
                    COUNT(DISTINCT o.OrderID) AS OrderCount,
                    SUM(o.TotalCost) AS TotalRevenue,
                    AVG(o.TotalCost) AS AvgOrderValue,
                    MAX(o.OrderDate) AS LastOrderDate
                FROM Clients c
                INNER JOIN Orders o ON c.ClientID = o.ClientID
                WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                    AND o.Invoiced = 1
                GROUP BY c.Name, c.ClientID
                ORDER BY TotalRevenue DESC
            """
        
        elif query_name == "sales_by_month":
            months = params.get('months', 12)
            return f"""
                SELECT 
                    FORMAT(o.OrderDate, 'yyyy-MM') AS Month,
                    SUM(o.TotalCost) AS Revenue,
                    COUNT(DISTINCT o.OrderID) AS OrderCount,
                    AVG(o.TotalCost) AS AvgOrderValue
                FROM Orders o
                WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                    AND o.Invoiced = 1
                GROUP BY FORMAT(o.OrderDate, 'yyyy-MM')
                ORDER BY Month ASC
            """
        
        elif query_name == "pending_orders":
            return """
                SELECT 
                    o.OrderID,
                    o.OrderDate,
                    c.Name AS ClientName,
                    o.TotalCost,
                    o.OrderDescription,
                    DATEDIFF(DAY, o.OrderDate, GETDATE()) AS DaysOpen
                FROM Orders o
                INNER JOIN Clients c ON o.ClientID = c.ClientID
                WHERE o.Invoiced = 0
                ORDER BY o.OrderDate ASC
            """
        
        elif query_name == "stock_levels":
            low_stock_only = params.get('low_stock_only', False)
            where_clause = ""
            # Note: Quote_DigitalStocks may not have stock level columns
            # This is a simplified version
            return f"""
                SELECT 
                    s.StockID,
                    st.StockTypeDesc AS StockType,
                    s.GSM,
                    s.Width,
                    s.Length,
                    s.CostPerThousand,
                    s.Markup
                FROM Quote_DigitalStocks s
                LEFT JOIN Quote_StockType st ON s.StockTypeID = st.StockTypeID
                ORDER BY st.StockTypeDesc, s.GSM
            """
        
        return ""
    
    def close(self, **kwargs) -> Dict[str, Any]:
        """Close database connection"""
        return self.db.close()
