"""
Database Helpers
Connection helpers for Supabase PostgreSQL and SQL Server databases

SUPABASE POSTGRESQL:
This module uses Supabase PostgreSQL for all database operations.
Connection pooling is handled by database_utils.py for optimal performance.
"""

import threading
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

# Make pyodbc optional - only needed for SQL Server connections
try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False
    pyodbc = None


class DatabaseConnectionError(Exception):
    """Database connection error"""
    pass


def get_sql_server_connection(server: str, database: str, timeout: int = 30):
    """
    Get SQL Server connection
    
    Args:
        server: Server address (e.g., "3.25.76.138\\INHPSQLSERVER")
        database: Database name (e.g., "In HousePrint")
        timeout: Connection timeout in seconds
    
    Returns:
        pyodbc.Connection
    
    Raises:
        DatabaseConnectionError: If pyodbc not available or connection fails
    """
    if not PYODBC_AVAILABLE:
        raise DatabaseConnectionError(
            "pyodbc not available - SQL Server connections disabled. "
            "Install pyodbc and unixodbc to enable SQL Server support."
        )
    
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Trusted_Connection=yes;"
            f"Connection Timeout={timeout};"
        )
        
        conn = pyodbc.connect(conn_str)
        return conn
    
    except Exception as e:
        raise DatabaseConnectionError(f"SQL Server connection failed: {e}")


def get_stock_database_connection():
    """
    Get connection to stock_data schema in Supabase
    
    Returns:
        DatabaseConnection: Supabase connection to stock_data schema
    """
    from shared.database_utils import get_database_connection, convert_sql_placeholders
    return get_database_connection('stock_data')


def get_sessions_database_connection():
    """
    Get connection to sessions schema in Supabase
    
    This is the CORRECT database for threads, user data, credentials, OAuth tokens
    
    Returns:
        DatabaseConnection: Supabase connection to sessions schema
    """
    from shared.database_utils import get_database_connection, convert_sql_placeholders
    return get_database_connection('sessions')


def get_ai_infrastructure_connection():
    """
    Get connection to ai_infrastructure schema in Supabase
    
    Returns:
        DatabaseConnection: Supabase connection to ai_infrastructure schema
    """
    from shared.database_utils import get_database_connection, convert_sql_placeholders
    return get_database_connection('ai_infrastructure')


def execute_sql_server_query(server: str, database: str, query: str, params: Optional[tuple] = None) -> List[Dict]:
    """
    Execute SQL Server query and return results as list of dicts
    
    Args:
        server: Server address
        database: Database name
        query: SQL query
        params: Query parameters
    
    Returns:
        List of dictionaries (rows)
    
    Raises:
        DatabaseConnectionError: If query execution fails
    """
    conn = None
    try:
        conn = get_sql_server_connection(server, database)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Get column names
        columns = [column[0] for column in cursor.description] if cursor.description else []
        
        # Fetch rows
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        
        return results
    
    finally:
        if conn:
            conn.close()


def execute_query(schema: str, query: str, params: Optional[tuple] = None) -> List[Dict]:
    """
    Execute Supabase PostgreSQL query and return results as list of dicts
    
    Args:
        schema: Schema name ('sessions', 'ai_infrastructure', 'stock_data', etc.)
        query: SQL query (use %s or ? placeholders - auto-converted)
        params: Query parameters
    
    Returns:
        List of dictionaries (rows)
    
    Raises:
        DatabaseConnectionError: If query execution fails
    
    Examples:
        # Query sessions schema
        rows = execute_query('sessions', 
                           'SELECT * FROM threads WHERE user_id = %s', 
                           (user_id,))
        
        # Query ai_infrastructure schema
        users = execute_query('ai_infrastructure',
                            'SELECT * FROM users WHERE email = %s',
                            (email,))
    """
    try:
        from shared.database_utils import get_database_connection, convert_sql_placeholders
        
        conn = get_database_connection(schema)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Fetch rows
        rows = cursor.fetchall()
        
        # Convert to list of dicts (RealDictCursor already returns dict-like rows)
        results = [dict(row) for row in rows] if rows else []
        
        cursor.close()
        conn.close()
        
        return results
    
    except Exception as e:
        raise DatabaseConnectionError(f"Database query failed: {e}")


def execute_update(schema: str, query: str, params: Optional[tuple] = None) -> int:
    """
    Execute Supabase PostgreSQL UPDATE/INSERT/DELETE and return affected rows
    
    Args:
        schema: Schema name ('sessions', 'ai_infrastructure', 'stock_data', etc.)
        query: SQL query (use %s or ? placeholders - auto-converted)
        params: Query parameters
    
    Returns:
        Number of affected rows
    
    Raises:
        DatabaseConnectionError: If query execution fails
    
    Examples:
        # Update sessions schema
        rows = execute_update('sessions',
                            'UPDATE threads SET name = %s WHERE id = %s',
                            ('New Name', thread_id))
        
        # Insert into ai_infrastructure schema
        rows = execute_update('ai_infrastructure',
                            'INSERT INTO users (username, email) VALUES (%s, %s)',
                            ('john', 'john@example.com'))
    """
    try:
        from shared.database_utils import get_database_connection, convert_sql_placeholders
        
        conn = get_database_connection(schema)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Commit and get rowcount
        conn.commit()
        rowcount = cursor.rowcount
        
        cursor.close()
        conn.close()
        
        return rowcount
    
    except Exception as e:
        raise DatabaseConnectionError(f"Database update failed: {e}")


# Legacy function names for backward compatibility
def execute_sqlite_query(db_path: str, query: str, params: Optional[tuple] = None) -> List[Dict]:
    """
    Execute database query (legacy function - maps to execute_query)
    
    MIGRATION NOTE: This function now uses Supabase PostgreSQL.
    The db_path parameter is used to determine the schema:
      - Contains 'sessions': uses 'sessions' schema
      - Contains 'synergy': uses 'synergy_sessions' schema
      - Contains 'stock': uses 'stock_data' schema
      - Otherwise: uses 'ai_infrastructure' schema
    
    Args:
        db_path: Path-like string (used to infer schema name)
        query: SQL query (use %s or ? placeholders)
        params: Query parameters
    
    Returns:
        List of dictionaries (rows)
    
    Note:
        This function exists for backward compatibility.
        New code should use execute_query(schema, query, params) instead.
    """
    # Determine schema from db_path
    db_path_lower = str(db_path).lower()
    
    if 'sessions' in db_path_lower and 'synergy' not in db_path_lower:
        schema = 'sessions'
    elif 'synergy' in db_path_lower:
        schema = 'synergy_sessions'
    elif 'stock' in db_path_lower:
        schema = 'stock_data'
    elif 'kanban' in db_path_lower:
        schema = 'kanban_analytics'
    else:
        schema = 'ai_infrastructure'
    
    return execute_query(schema, query, params)


def execute_sqlite_update(db_path: str, query: str, params: Optional[tuple] = None) -> int:
    """
    Execute database UPDATE/INSERT/DELETE (legacy function - maps to execute_update)
    
    MIGRATION NOTE: This function now uses Supabase PostgreSQL.
    The db_path parameter is used to determine the schema:
      - Contains 'sessions': uses 'sessions' schema
      - Contains 'synergy': uses 'synergy_sessions' schema
      - Contains 'stock': uses 'stock_data' schema
      - Otherwise: uses 'ai_infrastructure' schema
    
    Args:
        db_path: Path-like string (used to infer schema name)
        query: SQL query (use %s or ? placeholders)
        params: Query parameters
    
    Returns:
        Number of affected rows
    
    Note:
        This function exists for backward compatibility.
        New code should use execute_update(schema, query, params) instead.
    """
    # Determine schema from db_path
    db_path_lower = str(db_path).lower()
    
    if 'sessions' in db_path_lower and 'synergy' not in db_path_lower:
        schema = 'sessions'
    elif 'synergy' in db_path_lower:
        schema = 'synergy_sessions'
    elif 'stock' in db_path_lower:
        schema = 'stock_data'
    elif 'kanban' in db_path_lower:
        schema = 'kanban_analytics'
    else:
        schema = 'ai_infrastructure'
    
    return execute_update(schema, query, params)


def get_database_schema(schema: str) -> Dict[str, List[Dict]]:
    """
    Get PostgreSQL database schema information
    
    Args:
        schema: Schema name ('sessions', 'ai_infrastructure', etc.)
    
    Returns:
        Dictionary with table names as keys, column info as values
    
    Example:
        schema_info = get_database_schema('sessions')
        # Returns: {
        #   'threads': [
        #     {'name': 'id', 'type': 'integer', 'notnull': True, 'pk': True},
        #     {'name': 'name', 'type': 'text', 'notnull': False, 'pk': False},
        #     ...
        #   ],
        #   'messages': [...],
        #   ...
        # }
    """
    try:
        from shared.database_utils import get_database_connection, convert_sql_placeholders
        
        conn = get_database_connection(schema)
        cursor = conn.cursor()
        
        # Get table names from information_schema
        sql, params = convert_sql_placeholders("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            ORDER BY table_name
        """, (schema,))

        cursor.execute(sql, params)
        
        tables = [row['table_name'] for row in cursor.fetchall()]
        
        # Get columns for each table
        schema_info = {}
        for table in tables:
            sql, params = convert_sql_placeholders("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
            """, (schema, table))

            cursor.execute(sql, params)
            
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'name': row['column_name'],
                    'type': row['data_type'],
                    'notnull': row['is_nullable'] == 'NO',
                    'pk': 'nextval' in str(row['column_default']) if row['column_default'] else False
                })
            
            schema_info[table] = columns
        
        cursor.close()
        conn.close()
        
        return schema_info
    
    except Exception as e:
        raise DatabaseConnectionError(f"Failed to get schema info: {e}")


# Legacy function name for backward compatibility
def get_sqlite_schema(db_path: str) -> Dict[str, List[Dict]]:
    """
    Get database schema (legacy function - maps to get_database_schema)
    
    Args:
        db_path: Path-like string (used to infer schema name)
    
    Returns:
        Dictionary with table names as keys, column info as values
    
    Note:
        This function exists for backward compatibility.
        New code should use get_database_schema(schema) instead.
    """
    # Determine schema from db_path
    db_path_lower = str(db_path).lower()
    
    if 'sessions' in db_path_lower and 'synergy' not in db_path_lower:
        schema = 'sessions'
    elif 'synergy' in db_path_lower:
        schema = 'synergy_sessions'
    elif 'stock' in db_path_lower:
        schema = 'stock_data'
    elif 'kanban' in db_path_lower:
        schema = 'kanban_analytics'
    else:
        schema = 'ai_infrastructure'
    
    return get_database_schema(schema)


if __name__ == '__main__':
    """Test database helpers"""
    print("=" * 60)
    print("Database Helpers Test")
    print("=" * 60)
    
    # Test Supabase connection
    print("\n1. Testing Supabase connections:")
    try:
        conn = get_sessions_database_connection()
        print("   ✓ Connected to sessions schema")
        conn.close()
        
        conn = get_ai_infrastructure_connection()
        print("   ✓ Connected to ai_infrastructure schema")
        conn.close()
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test query execution
    print("\n2. Testing query execution:")
    try:
        rows = execute_query('sessions', 'SELECT COUNT(*) as count FROM threads')
        print(f"   ✓ Query executed: {rows[0]['count']} threads found")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test schema introspection
    print("\n3. Testing schema introspection:")
    try:
        schema_info = get_database_schema('sessions')
        print(f"   ✓ Schema loaded: {len(schema_info)} tables found")
        print(f"   Tables: {', '.join(schema_info.keys())}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    print("\n" + "=" * 60)