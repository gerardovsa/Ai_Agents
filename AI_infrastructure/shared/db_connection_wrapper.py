"""
Universal Database Connection Wrapper
Exclusively uses Supabase PostgreSQL

USAGE:
    from shared.db_connection_wrapper import get_connection
    
    conn = get_connection('ai_infrastructure')  # Uses Supabase PostgreSQL
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
"""

import os
from pathlib import Path
from typing import Union

def get_connection(db_name: str = 'ai_infrastructure'):
    """
    Get Supabase PostgreSQL database connection
    
    Args:
        db_name: Database name / schema name
                 Options: 'ai_infrastructure', 'sessions', 'synergy_sessions', 
                         'stock_data', 'kanban_analytics'
    
    Returns:
        DatabaseConnection: Wrapped psycopg2.Connection to Supabase PostgreSQL
    
    Raises:
        ValueError: If SUPABASE_DB_URL not set
        ConnectionError: If connection fails
    
    Examples:
        >>> conn = get_connection('ai_infrastructure')
        >>> cursor = conn.cursor()
        >>> cursor.execute("SELECT * FROM users WHERE id = %s", (1,))
        
        >>> # With context manager (auto-close)
        >>> with get_connection('sessions') as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT * FROM threads")
    """
    from shared.database_utils import get_database_connection
    return get_database_connection(db_name)


def get_connection_with_path(db_path: Union[str, Path]):
    """
    Get connection from path hint (maps to Supabase schema)
    
    This function provides backward compatibility for code that used
    SQLite file paths. It extracts the database name from the path
    and connects to the corresponding Supabase schema.
    
    Args:
        db_path: Path string (used to infer schema name)
                 Examples:
                 - 'data/sessions.db' -> 'sessions' schema
                 - 'data/ai_infrastructure.db' -> 'ai_infrastructure' schema
    
    Returns:
        DatabaseConnection: Connection to inferred Supabase schema
    
    Schema Mapping:
        - Path contains 'sessions' -> 'sessions' schema
        - Path contains 'synergy' -> 'synergy_sessions' schema
        - Default -> 'ai_infrastructure' schema
    
    Note:
        This function exists for backward compatibility only.
        New code should use get_connection(db_name) instead.
    
    Examples:
        >>> # Legacy code with path
        >>> conn = get_connection_with_path('data/sessions.db')
        >>> # Maps to: get_connection('sessions')
        
        >>> # Better: Use direct schema name
        >>> conn = get_connection('sessions')
    """
    # Extract database name from path
    path_str = str(db_path).lower()
    
    if 'sessions' in path_str and 'synergy' not in path_str:
        db_name = 'sessions'
    elif 'synergy' in path_str:
        db_name = 'synergy_sessions'
    elif 'stock_data' in path_str:
        db_name = 'stock_data'
    elif 'kanban' in path_str:
        db_name = 'kanban_analytics'
    else:
        db_name = 'ai_infrastructure'
    
    from shared.database_utils import get_database_connection
    return get_database_connection(db_name)


# Convenience aliases for common databases
def get_ai_infrastructure_connection():
    """Get connection to ai_infrastructure schema"""
    return get_connection('ai_infrastructure')


def get_sessions_connection():
    """Get connection to sessions schema"""
    return get_connection('sessions')


def get_synergy_connection():
    """Get connection to synergy_sessions schema"""
    return get_connection('synergy_sessions')


def get_stock_data_connection():
    """Get connection to stock_data schema"""
    return get_connection('stock_data')


def get_kanban_analytics_connection():
    """Get connection to kanban_analytics schema"""
    return get_connection('kanban_analytics')


if __name__ == '__main__':
    """Test database connection wrapper"""
    print("=" * 60)
    print("Database Connection Wrapper Test")
    print("=" * 60)
    
    # Test direct connection
    print("\n1. Testing direct connection:")
    try:
        conn = get_connection('ai_infrastructure')
        print("   ✓ Connected to ai_infrastructure schema")
        conn.close()
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test path-based connection (legacy)
    print("\n2. Testing path-based connection (legacy):")
    try:
        conn = get_connection_with_path('data/sessions.db')
        print("   ✓ Connected to sessions schema (from path)")
        conn.close()
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test convenience functions
    print("\n3. Testing convenience functions:")
    try:
        conn = get_ai_infrastructure_connection()
        print("   ✓ get_ai_infrastructure_connection() works")
        conn.close()
        
        conn = get_sessions_connection()
        print("   ✓ get_sessions_connection() works")
        conn.close()
        
        conn = get_synergy_connection()
        print("   ✓ get_synergy_connection() works")
        conn.close()
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    print("\n" + "=" * 60)