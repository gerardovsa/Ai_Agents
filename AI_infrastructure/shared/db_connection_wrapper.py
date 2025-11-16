"""
Universal Database Connection Wrapper
Automatically uses Supabase on Render, SQLite locally

USAGE:
    from shared.db_connection_wrapper import get_connection
    
    conn = get_connection('ai_infrastructure')  # Uses Supabase on Render, SQLite locally
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
"""

import os
from pathlib import Path
from typing import Union

def get_connection(db_name: str = 'ai_infrastructure'):
    """
    Get database connection - ALWAYS uses Supabase PostgreSQL (local AND Render)
    
    Args:
        db_name: Database name (for future multi-schema support)
    
    Returns:
        Connection object (psycopg2.Connection to Supabase PostgreSQL)
    
    Examples:
        >>> conn = get_connection('ai_infrastructure')
        >>> cursor = conn.cursor()
        >>> cursor.execute("SELECT * FROM ai_infrastructure.users WHERE id = %s", (1,))
    """
    # ALWAYS use Supabase PostgreSQL - NO SQLite fallback
    from shared.database_utils import get_database_connection
    return get_database_connection(db_name)


def get_connection_with_path(db_path: Union[str, Path]):
    """
    Get connection from explicit path (SQLite only, for legacy compatibility)
    
    Args:
        db_path: Path to SQLite database file
    
    Returns:
        sqlite3.Connection
    
    Note: This function is for backward compatibility only.
          New code should use get_connection() instead.
    """
    # On Render: Ignore path, use Supabase
    if os.getenv('USE_SUPABASE') == 'true' or os.getenv('RENDER') == 'true':
        # Extract database name from path
        path_str = str(db_path)
        if 'sessions' in path_str:
            db_name = 'sessions'
        elif 'synergy' in path_str:
            db_name = 'synergy_sessions'
        else:
            db_name = 'ai_infrastructure'
        
        from shared.database_utils import get_database_connection
        return get_database_connection(db_name)
    
    # Local: Use provided path
    else:
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn


# Convenience aliases
get_ai_infrastructure_connection = lambda: get_connection('ai_infrastructure')
get_sessions_connection = lambda: get_connection('sessions')
get_synergy_connection = lambda: get_connection('synergy_sessions')
