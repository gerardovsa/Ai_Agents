"""
Database Schema Helper
Provides consistent schema name resolution for Supabase PostgreSQL

CRITICAL: 
- Uses Supabase PostgreSQL exclusively (both local and production)
- Each "database" is a PostgreSQL schema in Supabase
- No file paths needed - connection handled by database_utils.py
"""

import os
from pathlib import Path


def get_ai_infrastructure_schema() -> str:
    """
    Get schema name for ai_infrastructure
    
    Returns:
        'ai_infrastructure' - PostgreSQL schema in Supabase
    """
    return 'ai_infrastructure'


def get_sessions_schema() -> str:
    """
    Get schema name for sessions
    
    Returns:
        'sessions' - PostgreSQL schema in Supabase
    """
    return 'sessions'


def get_stock_data_schema() -> str:
    """
    Get schema name for stock_data
    
    Returns:
        'stock_data' - PostgreSQL schema in Supabase
    """
    return 'stock_data'


def get_synergy_sessions_schema() -> str:
    """
    Get schema name for synergy_sessions
    
    Returns:
        'synergy_sessions' - PostgreSQL schema in Supabase
    """
    return 'synergy_sessions'


def get_kanban_analytics_schema() -> str:
    """
    Get schema name for kanban_analytics
    
    Returns:
        'kanban_analytics' - PostgreSQL schema in Supabase
    """
    return 'kanban_analytics'


# Legacy function names for backward compatibility
def get_ai_infrastructure_db_path() -> str:
    """
    Get schema name for ai_infrastructure (legacy function)
    
    Note: This function exists for backward compatibility.
          Returns schema name instead of file path.
          Use get_ai_infrastructure_schema() for new code.
    
    Returns:
        'ai_infrastructure' - PostgreSQL schema in Supabase
    """
    return 'ai_infrastructure'


def get_sessions_db_path() -> str:
    """
    Get schema name for sessions (legacy function)
    
    Note: This function exists for backward compatibility.
          Returns schema name instead of file path.
          Use get_sessions_schema() for new code.
    
    Returns:
        'sessions' - PostgreSQL schema in Supabase
    """
    return 'sessions'


def get_stock_db_path() -> str:
    """
    Get schema name for stock_data (legacy function)
    
    Note: This function exists for backward compatibility.
          Returns schema name instead of file path.
          Use get_stock_data_schema() for new code.
    
    Returns:
        'stock_data' - PostgreSQL schema in Supabase
    """
    return 'stock_data'


def get_synergy_sessions_db_path() -> str:
    """
    Get schema name for synergy_sessions (legacy function)
    
    Note: This function exists for backward compatibility.
          Returns schema name instead of file path.
          Use get_synergy_sessions_schema() for new code.
    
    Returns:
        'synergy_sessions' - PostgreSQL schema in Supabase
    """
    return 'synergy_sessions'


def ensure_data_directory():
    """
    Ensure database schemas exist in Supabase
    
    Note: Schemas are automatically created by database_utils.py
          when get_database_connection() is called.
          This function exists for backward compatibility.
    """
    # No-op - schemas created automatically by database_utils.py
    # Connection pooling handles schema creation on first access
    pass


def verify_supabase_connection():
    """
    Verify Supabase connection is available
    
    Raises:
        ConnectionError: If SUPABASE_DB_URL not set or connection fails
    
    Returns:
        True if connection successful
    """
    if not os.getenv('SUPABASE_DB_URL'):
        raise ConnectionError(
            "SUPABASE_DB_URL not set in environment. "
            "This is required for database connections."
        )
    
    try:
        from shared.database_utils import get_database_connection
        
        # Test connection to ai_infrastructure schema
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        print("✓ Supabase connection verified")
        return True
        
    except Exception as e:
        raise ConnectionError(f"Supabase connection failed: {e}")


if __name__ == '__main__':
    """Test database schema helper"""
    print("=" * 60)
    print("Database Schema Helper Test")
    print("=" * 60)
    
    # Show schema names
    print("\n1. Schema Names:")
    print(f"   AI Infrastructure: {get_ai_infrastructure_schema()}")
    print(f"   Sessions: {get_sessions_schema()}")
    print(f"   Stock Data: {get_stock_data_schema()}")
    print(f"   Synergy Sessions: {get_synergy_sessions_schema()}")
    print(f"   Kanban Analytics: {get_kanban_analytics_schema()}")
    
    # Test legacy functions
    print("\n2. Legacy Functions (backward compatibility):")
    print(f"   get_ai_infrastructure_db_path(): {get_ai_infrastructure_db_path()}")
    print(f"   get_sessions_db_path(): {get_sessions_db_path()}")
    print(f"   get_stock_db_path(): {get_stock_db_path()}")
    print(f"   get_synergy_sessions_db_path(): {get_synergy_sessions_db_path()}")
    
    # Verify connection
    print("\n3. Verifying Supabase Connection:")
    try:
        verify_supabase_connection()
        print("   ✓ Connection test passed")
    except Exception as e:
        print(f"   ✗ Connection test failed: {e}")
    
    print("\n" + "=" * 60)