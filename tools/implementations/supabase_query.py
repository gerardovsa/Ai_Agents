"""
Supabase Custom Query Tool
Allows AI to execute custom SQL queries on Supabase PostgreSQL

SECURITY: Read-only queries recommended. Write operations require user confirmation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from AI_infrastructure.shared.database_utils import get_database_connection
from psycopg2.extras import RealDictCursor


def supabase_execute_query(
    schema_name: str,
    query: str,
    params: list = None,
    max_rows: int = 100,
    read_only: bool = True
) -> dict:
    """
    Execute custom SQL query on Supabase PostgreSQL
    
    Args:
        schema_name: Schema to query ('ai_infrastructure', 'sessions', 'synergy_sessions', 'stock_data')
        query: SQL query to execute (SELECT, INSERT, UPDATE, DELETE, etc.)
        params: Optional parameters for parameterized queries (use %s placeholders)
        max_rows: Maximum rows to return (default 100, prevents token overflow)
        read_only: If True, only SELECT queries allowed (default True for safety)
    
    Returns:
        {
            'success': bool,
            'rows': list,           # Query results
            'row_count': int,       # Number of rows returned
            'columns': list,        # Column names
            'query_type': str,      # 'SELECT', 'INSERT', 'UPDATE', 'DELETE', etc.
            'schema': str,          # Schema queried
            'message': str
        }
    
    Examples:
        # Find user by email
        supabase_execute_query(
            schema_name='ai_infrastructure',
            query='SELECT id, username, email FROM users WHERE email = %s',
            params=['user@example.com']
        )
        
        # Get recent chat messages
        supabase_execute_query(
            schema_name='sessions',
            query='''
                SELECT thread_id, created_at, content 
                FROM messages 
                WHERE thread_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            ''',
            params=['thread-123', 10]
        )
        
        # Search stock by description
        supabase_execute_query(
            schema_name='stock_data',
            query='''
                SELECT stock_id, stock_type_name, gsm, cost_per_thousand 
                FROM unified_stocks 
                WHERE stock_description ILIKE %s 
                LIMIT %s
            ''',
            params=['%business cards%', 20]
        )
        
        # Get user's kanban tasks
        supabase_execute_query(
            schema_name='synergy_sessions',
            query='''
                SELECT session_id, title, status, priority 
                FROM sessions 
                WHERE user_id = %s AND status != %s
                ORDER BY created_at DESC
            ''',
            params=[1, 'completed']
        )
    """
    
    conn = None
    cursor = None
    
    try:
        # Validate schema name
        valid_schemas = ['ai_infrastructure', 'sessions', 'synergy_sessions', 'stock_data']
        if schema_name not in valid_schemas:
            return {
                'success': False,
                'error': f'Invalid schema. Must be one of: {", ".join(valid_schemas)}',
                'valid_schemas': valid_schemas
            }
        
        # Normalize query
        query_upper = query.strip().upper()
        query_type = query_upper.split()[0] if query_upper else 'UNKNOWN'
        
        # Read-only enforcement
        if read_only and query_type not in ['SELECT', 'EXPLAIN', 'SHOW', 'DESCRIBE']:
            return {
                'success': False,
                'error': f'Read-only mode: {query_type} queries not allowed. Set read_only=False for write operations.',
                'query_type': query_type,
                'hint': 'For safety, write operations require read_only=False parameter'
            }
        
        # Warn on write operations
        if query_type in ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE']:
            print(f"⚠️  WARNING: Executing {query_type} query on {schema_name} schema")
        
        # Connect to Supabase PostgreSQL
        conn = get_database_connection(schema_name)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Execute query
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Handle SELECT queries
        if query_type == 'SELECT':
            # Fetch results with limit
            rows = cursor.fetchmany(max_rows)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # RealDictCursor already returns dicts, just convert to list
            results = [dict(row) for row in rows]
            
            # Check if there are more rows
            has_more = len(rows) == max_rows
            remaining_warning = ""
            if has_more:
                try:
                    cursor.fetchone()
                    remaining_warning = f" (Limited to {max_rows} rows. Use max_rows parameter for more.)"
                except:
                    pass
            
            return {
                'success': True,
                'rows': results,
                'row_count': len(results),
                'columns': columns,
                'query_type': query_type,
                'schema': schema_name,
                'message': f'Query executed successfully. Returned {len(results)} rows{remaining_warning}.',
                'has_more': has_more
            }
        
        # Handle write operations (INSERT, UPDATE, DELETE)
        else:
            conn.commit()
            rows_affected = cursor.rowcount
            
            return {
                'success': True,
                'rows_affected': rows_affected,
                'query_type': query_type,
                'schema': schema_name,
                'message': f'{query_type} executed successfully. {rows_affected} rows affected.'
            }
    
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful error messages
        if 'permission denied' in error_msg.lower():
            hint = 'User may not have permission to access this table/schema.'
        elif 'does not exist' in error_msg.lower():
            hint = 'Table, column, or schema does not exist. Check schema name and table names.'
        elif 'syntax error' in error_msg.lower():
            hint = 'SQL syntax error. Check query syntax and parameter placeholders (%s).'
        else:
            hint = 'Check query syntax, schema name, and parameter values.'
        
        return {
            'success': False,
            'error': error_msg,
            'hint': hint,
            'query_type': query_type,
            'schema': schema_name
        }
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def supabase_search_database(
    search_text: str,
    schemas: list = None,
    tables: list = None,
    limit_per_table: int = 10
) -> dict:
    """
    Search across Supabase database for text/keywords
    
    Searches common text columns across multiple schemas and tables.
    Useful for finding data when you don't know exact location.
    
    Args:
        search_text: Text to search for (supports wildcards with %)
        schemas: List of schemas to search (default: all)
        tables: Specific tables to search (default: common tables)
        limit_per_table: Max results per table (default 10)
    
    Returns:
        {
            'success': bool,
            'results': {
                'schema.table': [matching_rows],
                ...
            },
            'total_matches': int,
            'searched_locations': list,
            'search_text': str
        }
    
    Examples:
        # Search for user email
        supabase_search_database(
            search_text='user@example.com',
            schemas=['ai_infrastructure']
        )
        
        # Search for quote/order number
        supabase_search_database(
            search_text='QU-0123',
            schemas=['stock_data']
        )
        
        # Search for conversation content
        supabase_search_database(
            search_text='%printing quote%',
            schemas=['sessions']
        )
    """
    
    try:
        # Default to all schemas if not specified
        if not schemas:
            schemas = ['ai_infrastructure', 'sessions', 'synergy_sessions', 'stock_data']
        
        # Define searchable tables and columns for each schema
        search_config = {
            'ai_infrastructure': {
                'users': ['username', 'email'],
                'oauth_tokens': ['email', 'account_name', 'profile_name'],
                'workspaces': ['name', 'description', 'slug'],
                'saved_threads': ['thread_name', 'conversation', 'summary'],
                'user_preferences': ['nickname', 'ai_memories']
            },
            'sessions': {
                'messages': ['role', 'content', 'prompt', 'response_data'],
                'threads': ['thread_slug', 'name', 'workflow_title', 'email_subject'],
                'saved_threads': ['thread_name', 'conversation', 'tags'],
                'messages': ['content', 'role']
            },
            'synergy_sessions': {
                'sessions': ['session_id', 'title', 'content', 'tags'],
                'kanban_cards': ['title', 'description', 'tags']
            },
            'stock_data': {
                'unified_stocks': ['stock_id', 'stock_type_name', 'stock_description', 'supplier_name'],
                'extracted_jobs': ['client_name', 'job_description', 'product_type'],
                'shopify_orders': ['order_number', 'email', 'customer_name'],
                'shopify_products': ['title', 'body_html', 'vendor']
            }
        }
        
        results = {}
        total_matches = 0
        searched_locations = []
        
        # Add wildcards if not present
        search_pattern = search_text if '%' in search_text else f'%{search_text}%'
        
        # Search each schema
        for schema in schemas:
            if schema not in search_config:
                continue
            
            # Filter tables if specified
            tables_to_search = tables if tables else search_config[schema].keys()
            
            for table, columns in search_config[schema].items():
                if table not in tables_to_search:
                    continue
                
                # Build search query for this table
                where_clauses = [f"{col}::text ILIKE %s" for col in columns]
                where_sql = " OR ".join(where_clauses)
                
                query = f"""
                    SELECT * FROM {table}
                    WHERE {where_sql}
                    LIMIT %s
                """
                
                # Execute search
                params = [search_pattern] * len(columns) + [limit_per_table]
                
                result = supabase_execute_query(
                    schema_name=schema,
                    query=query,
                    params=params,
                    max_rows=limit_per_table
                )
                
                location = f"{schema}.{table}"
                searched_locations.append(location)
                
                if result.get('success') and result.get('rows'):
                    results[location] = result['rows']
                    total_matches += len(result['rows'])
        
        return {
            'success': True,
            'results': results,
            'total_matches': total_matches,
            'searched_locations': searched_locations,
            'search_text': search_text,
            'message': f'Found {total_matches} matches across {len(results)} tables.'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'hint': 'Check search_text format and schema names.'
        }


# Tool metadata for registration
__tools__ = {
    'supabase_execute_query': {
        'function': supabase_execute_query,
        'description': 'Execute custom SQL queries on Supabase PostgreSQL (ai_infrastructure, sessions, synergy_sessions, stock_data schemas)',
        'parameters': {
            'schema_name': 'Schema to query',
            'query': 'SQL query with %s placeholders for parameters',
            'params': 'List of parameter values',
            'max_rows': 'Maximum rows to return (default 100)',
            'read_only': 'If True, only SELECT queries allowed (default True)'
        },
        'examples': [
            "Find user: supabase_execute_query('ai_infrastructure', 'SELECT * FROM users WHERE email = %s', ['user@example.com'])",
            "Get chat messages: supabase_execute_query('sessions', 'SELECT * FROM messages WHERE thread_id = %s ORDER BY created_at DESC LIMIT 10', ['thread-123'])",
            "Search stock: supabase_execute_query('stock_data', 'SELECT * FROM unified_stocks WHERE stock_description ILIKE %s LIMIT 20', ['%cards%'])"
        ]
    },
    'supabase_search_database': {
        'function': supabase_search_database,
        'description': 'Search across Supabase database for text/keywords. Useful when you don\'t know exact table location.',
        'parameters': {
            'search_text': 'Text to search for (supports % wildcards)',
            'schemas': 'List of schemas to search (default: all)',
            'tables': 'Specific tables to search (default: common tables)',
            'limit_per_table': 'Max results per table (default 10)'
        },
        'examples': [
            "Find user: supabase_search_database('user@example.com', schemas=['ai_infrastructure'])",
            "Find order: supabase_search_database('QU-0123', schemas=['stock_data'])",
            "Search content: supabase_search_database('%printing%', schemas=['sessions', 'synergy_sessions'])"
        ]
    }
}
