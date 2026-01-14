"""
InHouse Print Database Query & Search Tools
============================================

Two powerful tools for querying the Fred InHouse print shop database (SQL Server):

1. inhouse_execute_query() - Execute custom SQL queries on Fred database
2. inhouse_search_database() - Search across Fred database for text/keywords

Fred Database Platform: SQL Server (on-premises/hosted)
Connection: Via inhouse_execute_sql() wrapper

Created: December 8, 2025
"""

import sys
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add modules to path - note: folder is 'inhouse-print' with dash
inhouse_path = Path(__file__).parent.parent.parent / 'UI' / 'modules_external' / 'inhouse-print'
sys.path.insert(0, str(inhouse_path))

from implementations.inhouse_wrapper import inhouse_execute_sql


def inhouse_execute_query(
    query: str,
    params: Optional[List[Any]] = None,
    max_rows: int = 100,
    read_only: bool = True
) -> Dict[str, Any]:
    """
    Execute custom SQL query on Fred InHouse database (SQL Server).
    
    Fred is the production print shop database containing:
    - Orders: Customer orders and invoices
    - JobTickets: Individual print jobs with specifications
    - Clients: Customer contact information
    - Materials: PaperSize, PaperType, GSM, BindType
    - Reference: JobStages, JobTypes, ShippingTypes
    
    Args:
        query (str): SQL query to execute
            - Use SQL Server syntax (TOP N, not LIMIT)
            - Use ? placeholders for parameters
            - Schema: dbo (implicit, no need to specify)
        
        params (list, optional): Values for ? placeholders in query
            - Pass values in order they appear
            - Example: ['John Doe', '2025-01-01']
        
        max_rows (int): Maximum rows to return (default 100, max 1000)
            - Prevents token overflow
            - Use LIMIT in query for better control
        
        read_only (bool): If True, only SELECT queries allowed (default True)
            - Set to False to allow INSERT/UPDATE/DELETE
            - Write operations require explicit permission
    
    Returns:
        dict: {
            'success': bool,
            'rows': list of dicts (column_name: value),
            'row_count': int,
            'columns': list of column names,
            'query_type': str ('SELECT', 'INSERT', 'UPDATE', 'DELETE'),
            'error': str (if failed),
            'hint': str (helpful suggestion if error)
        }
    
    SQL Server Syntax Guide:
        - LIMIT: Use TOP N instead of LIMIT N
          SELECT TOP 20 * FROM Orders
        
        - Placeholders: Use ? (not %s or $1)
          WHERE ClientName = ? AND OrderDate > ?
        
        - String concat: Use + or CONCAT()
          ClientName + ' - ' + InvoiceNumber
        
        - Date functions: DATEADD, GETDATE, CONVERT
          WHERE OrderDate > DATEADD(month, -3, GETDATE())
        
        - Case-insensitive: Use LIKE (case-insensitive by default in SQL Server)
          WHERE ClientName LIKE '%Printing%'
        
        - Boolean: Use bit (1/0)
          WHERE Invoiced = 1 AND Urgent = 0
    
    Examples:
        # Find orders by client
        inhouse_execute_query(
            query="SELECT TOP 10 * FROM Orders WHERE ClientName LIKE ? ORDER BY OrderDate DESC",
            params=['%CJ King%']
        )
        
        # Get job tickets for order
        inhouse_execute_query(
            query='''
                SELECT jt.*, ps.[Desc] as PaperSize, bt.BindTypeDesc
                FROM JobTickets jt
                LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
                LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
                WHERE jt.OrderID = ?
            ''',
            params=[56230]
        )
        
        # Search clients by email
        inhouse_execute_query(
            query="SELECT ClientID, ClientName, Email FROM Clients WHERE Email LIKE ?",
            params=['%@example.com']
        )
        
        # Get urgent orders
        inhouse_execute_query(
            query='''
                SELECT TOP 50 
                    o.OrderID, o.ClientName, o.OrderDate, o.DateRequired,
                    COUNT(jt.TicketID) as JobCount,
                    SUM(jt.Cost) as TotalCost
                FROM Orders o
                LEFT JOIN JobTickets jt ON o.OrderID = jt.OrderID
                WHERE o.Urgent = 1 AND o.Invoiced = 0
                GROUP BY o.OrderID, o.ClientName, o.OrderDate, o.DateRequired
                ORDER BY o.DateRequired
            '''
        )
    """
    try:
        # Validate query type
        query_upper = query.strip().upper()
        
        if query_upper.startswith('SELECT'):
            query_type = 'SELECT'
        elif query_upper.startswith('INSERT'):
            query_type = 'INSERT'
        elif query_upper.startswith('UPDATE'):
            query_type = 'UPDATE'
        elif query_upper.startswith('DELETE'):
            query_type = 'DELETE'
        else:
            return {
                'success': False,
                'error': 'Unsupported query type',
                'hint': 'Only SELECT, INSERT, UPDATE, DELETE queries are supported. Query must start with one of these keywords.',
                'rows': [],
                'row_count': 0
            }
        
        # Check read-only enforcement
        if read_only and query_type != 'SELECT':
            return {
                'success': False,
                'error': f'{query_type} query blocked by read_only=True',
                'hint': f'To execute {query_type} queries, set read_only=False. Read-only mode only allows SELECT queries for safety.',
                'rows': [],
                'row_count': 0
            }
        
        # Build query with parameters (inhouse_execute_sql doesn't support parameterized queries)
        # We need to embed params in the query string
        if params:
            # Replace ? placeholders with quoted values
            formatted_query = query
            for param in params:
                if isinstance(param, str):
                    # Escape single quotes in strings
                    escaped = param.replace("'", "''")
                    formatted_query = formatted_query.replace('?', f"'{escaped}'", 1)
                elif param is None:
                    formatted_query = formatted_query.replace('?', 'NULL', 1)
                else:
                    formatted_query = formatted_query.replace('?', str(param), 1)
        else:
            formatted_query = query
        
        # Execute query via inhouse wrapper
        result = inhouse_execute_sql(formatted_query)
        
        if not result.get('success'):
            # Extract error message
            error_msg = result.get('error', 'Unknown error')
            
            # Provide helpful hints based on error
            hint = None
            if 'Invalid column name' in error_msg:
                hint = "Column doesn't exist. Check FRED_DATABASE_SCHEMA_ACTUAL.md for correct column names. Common issues: Orders has 'Invoiced' not 'Status', JobTickets has 'BindTypeDesc' in BindType table."
            elif 'Invalid object name' in error_msg:
                hint = "Table doesn't exist. Check FRED_DATABASE_SCHEMA_ACTUAL.md for correct table names. Main tables: Orders, JobTickets, Clients, PaperSize, BindType, JobStages, JobType."
            elif 'Incorrect syntax near' in error_msg:
                hint = "SQL syntax error. Remember: SQL Server uses TOP N (not LIMIT), ? placeholders (not %s), and DATEADD() for dates."
            
            return {
                'success': False,
                'error': error_msg,
                'hint': hint,
                'rows': [],
                'row_count': 0
            }
        
        # Get rows and limit
        rows = result.get('data', [])
        row_count = len(rows)
        
        # Apply max_rows limit
        if row_count > max_rows:
            rows = rows[:max_rows]
            truncated = True
        else:
            truncated = False
        
        # Get column names
        columns = list(rows[0].keys()) if rows else []
        
        return {
            'success': True,
            'rows': rows,
            'row_count': row_count,
            'columns': columns,
            'query_type': query_type,
            'truncated': truncated,
            'message': f"Query executed successfully. Returned {len(rows)} rows" + (f" (truncated from {row_count})" if truncated else "")
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Exception: {str(e)}',
            'hint': 'Check query syntax and parameters. See FRED_DATABASE_SCHEMA_ACTUAL.md for database structure.',
            'rows': [],
            'row_count': 0
        }


def inhouse_search_database(
    search_text: str,
    tables: Optional[List[str]] = None,
    limit_per_table: int = 10
) -> Dict[str, Any]:
    """
    Search across Fred InHouse database for text/keywords.
    
    Automatically searches common text columns in major Fred tables:
    - Orders: ClientName, ClientOrderNum, OrderNotes, InvoiceNumber
    - JobTickets: ShortJobDesc, TicketNotes
    - Clients: ClientName, Email
    
    Use when you don't know which table contains the data.
    
    Args:
        search_text (str): Text to search for
            - Supports % wildcards (e.g., '%business cards%')
            - Case-insensitive by default in SQL Server
            - Automatically adds wildcards if not present
        
        tables (list, optional): Specific tables to search
            - Default: ['Orders', 'JobTickets', 'Clients']
            - Available: Orders, JobTickets, Clients, PaperSize, BindType, JobStages, JobType
        
        limit_per_table (int): Max results per table (default 10)
    
    Returns:
        dict: {
            'success': bool,
            'results': dict of {table_name: [rows]},
            'total_matches': int,
            'searched_tables': list of table names,
            'message': str
        }
    
    Examples:
        # Find customer anywhere
        inhouse_search_database(search_text='CJ King Printing')
        
        # Search for invoice number
        inhouse_search_database(search_text='INV-2025-')
        
        # Find orders about business cards
        inhouse_search_database(
            search_text='%business cards%',
            tables=['Orders', 'JobTickets']
        )
        
        # Search by email
        inhouse_search_database(
            search_text='%@cjking.com.au',
            tables=['Clients']
        )
    """
    try:
        # Add wildcards if not present
        if '%' not in search_text:
            search_text = f'%{search_text}%'
        
        # Default tables to search
        if not tables:
            tables = ['Orders', 'JobTickets', 'Clients']
        
        # Search queries for each table
        search_queries = {
            'Orders': f"""
                SELECT TOP {limit_per_table}
                    OrderID, ClientName, OrderDate, ClientOrderNum, 
                    OrderNotes, InvoiceNumber, Invoiced, Urgent
                FROM Orders
                WHERE 
                    ClientName LIKE ?
                    OR ClientOrderNum LIKE ?
                    OR OrderNotes LIKE ?
                    OR InvoiceNumber LIKE ?
                ORDER BY OrderDate DESC
            """,
            
            'JobTickets': f"""
                SELECT TOP {limit_per_table}
                    jt.TicketID, jt.OrderID, jt.ShortJobDesc, jt.TicketNotes,
                    jt.QTY, jt.Cost, o.ClientName
                FROM JobTickets jt
                LEFT JOIN Orders o ON jt.OrderID = o.OrderID
                WHERE 
                    jt.ShortJobDesc LIKE ?
                    OR jt.TicketNotes LIKE ?
                ORDER BY jt.TicketID DESC
            """,
            
            'Clients': f"""
                SELECT TOP {limit_per_table}
                    ContactID, Name, defaultEmail, Phone, AddressCity
                FROM Clients
                WHERE 
                    Name LIKE ?
                    OR defaultEmail LIKE ?
                    OR Phone LIKE ?
            """,
            
            'PaperSize': f"""
                SELECT TOP {limit_per_table}
                    SizeID, [Desc] as PaperSize
                FROM PaperSize
                WHERE [Desc] LIKE ?
            """,
            
            'BindType': f"""
                SELECT TOP {limit_per_table}
                    BindID, BindTypeDesc
                FROM BindType
                WHERE BindTypeDesc LIKE ?
            """,
            
            'JobStages': f"""
                SELECT TOP {limit_per_table}
                    StageID, [Desc] as StageDescription
                FROM JobStages
                WHERE [Desc] LIKE ?
            """,
            
            'JobType': f"""
                SELECT TOP {limit_per_table}
                    JobTypeID, [Desc] as JobTypeDescription
                FROM JobType
                WHERE [Desc] LIKE ?
            """
        }
        
        results = {}
        total_matches = 0
        
        # Search each table
        for table in tables:
            if table not in search_queries:
                continue
            
            query = search_queries[table]
            
            # Count how many ? placeholders in query and replace with escaped search_text
            formatted_query = query
            param_count = query.count('?')
            escaped_search = search_text.replace("'", "''")
            for _ in range(param_count):
                formatted_query = formatted_query.replace('?', f"'{escaped_search}'", 1)
            
            # Execute search
            try:
                result = inhouse_execute_sql(formatted_query)
                
                # inhouse_execute_sql returns a list of dicts directly (not a dict with 'success' key)
                if isinstance(result, list) and result:
                    results[table] = result
                    total_matches += len(result)
                elif isinstance(result, dict) and result.get('error'):
                    # Handle error case
                    results[table] = {'error': result.get('error')}
            except Exception as e:
                # Include error in results for debugging
                results[table] = {'error': str(e)}
        
        # Build message
        if total_matches == 0:
            message = f"No matches found for '{search_text}' in {len(tables)} tables"
        else:
            tables_with_results = [t for t in results if isinstance(results[t], list)]
            message = f"Found {total_matches} matches across {len(tables_with_results)} tables"
        
        return {
            'success': True,
            'results': results,
            'total_matches': total_matches,
            'searched_tables': tables,
            'message': message
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Search failed: {str(e)}',
            'results': {},
            'total_matches': 0
        }


# Tool registration metadata
__tools__ = {
    'inhouse_execute_query': {
        'function': inhouse_execute_query,
        'description': 'Execute custom SQL query on Fred InHouse print shop database (SQL Server)',
        'parameters': {
            'query': 'SQL query with ? placeholders (SQL Server syntax: TOP N, DATEADD, etc.)',
            'params': 'List of values for ? placeholders (optional)',
            'max_rows': 'Maximum rows to return (default 100, max 1000)',
            'read_only': 'If True, only SELECT allowed (default True)'
        },
        'returns': 'Dict with rows, columns, row_count, query_type',
        'examples': [
            "inhouse_execute_query('SELECT TOP 10 * FROM Orders WHERE ClientName LIKE ?', ['%Printing%'])",
            "inhouse_execute_query('SELECT * FROM JobTickets WHERE OrderID = ?', [56230])"
        ]
    },
    
    'inhouse_search_database': {
        'function': inhouse_search_database,
        'description': 'Search Fred database for text/keywords across multiple tables',
        'parameters': {
            'search_text': 'Text to search (supports % wildcards)',
            'tables': 'Tables to search (default: Orders, JobTickets, Clients)',
            'limit_per_table': 'Max results per table (default 10)'
        },
        'returns': 'Dict with results grouped by table, total_matches',
        'examples': [
            "inhouse_search_database('CJ King Printing')",
            "inhouse_search_database('%business cards%', tables=['JobTickets'])"
        ]
    }
}
