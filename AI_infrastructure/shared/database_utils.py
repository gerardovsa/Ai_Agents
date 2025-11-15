"""
FILE: AI_infrastructure/shared/database_utils.py
PURPOSE: Database connection utility with auto-detection (SQLite vs Supabase PostgreSQL)

DEPENDENCIES:
- sqlite3 (built-in) - Local development SQLite
- psycopg2 (optional) - Supabase PostgreSQL for production
- os - Environment variable detection
- pathlib - Path handling

EXPORTS:
- get_database_connection(db_name: str) -> Connection - Get DB connection based on environment
- get_supabase_schema_name(db_name: str) -> str - Convert SQLite DB name to PostgreSQL schema
- is_using_supabase() -> bool - Check if using Supabase

ENVIRONMENT DETECTION:
- Local Dev: USE_SUPABASE not set or false → SQLite in data/ folder
- Render/Production: USE_SUPABASE=true → Supabase PostgreSQL with schemas

NOTES:
- Auto-detects environment via USE_SUPABASE env var
- Local: Uses SQLite databases in AI_agents/data/
- Render: Uses Supabase PostgreSQL with schema separation
- Each SQLite database becomes a PostgreSQL schema
- Backward compatible with existing SQLite code

LAST MODIFIED: 2025-11-15 - Initial creation with multi-environment support
"""

import os
import sqlite3
from pathlib import Path
from typing import Union, Tuple
from dotenv import load_dotenv

# Load environment variables from project root
_root_dir = Path(__file__).parent.parent.parent
_env_file = _root_dir / '.env.master'
if _env_file.exists():
    load_dotenv(_env_file)
else:
    load_dotenv()  # Try default .env

def is_using_supabase() -> bool:
    """
    Check if application should use Supabase PostgreSQL
    
    Returns:
        bool: True if USE_SUPABASE=true AND (RENDER=true OR explicit override), 
              False for local SQLite development
    
    Environment Variables:
        RENDER: Set to 'true' on Render deployment (auto-detected)
        USE_SUPABASE: Set to 'true' to enable Supabase
        USE_SQLITE: Set to 'true' to force SQLite (overrides USE_SUPABASE)
    
    Priority:
        1. USE_SQLITE=true → Force SQLite (for local dev)
        2. RENDER=true → Use Supabase (deployment)
        3. USE_SUPABASE=true AND RENDER not set → SQLite (safe default)
    """
    # Check for explicit SQLite override (highest priority)
    if os.getenv('USE_SQLITE', 'false').lower() == 'true':
        return False
    
    # Check if running on Render deployment
    is_render = os.getenv('RENDER', 'false').lower() == 'true'
    
    # Check USE_SUPABASE setting
    use_supabase = os.getenv('USE_SUPABASE', 'false').lower() == 'true'
    
    # Only use Supabase if both conditions met: USE_SUPABASE=true AND RENDER=true
    # This prevents accidental Supabase usage during local dev
    return use_supabase and is_render


def get_supabase_schema_name(db_name: str) -> str:
    """
    Convert SQLite database name to PostgreSQL schema name
    
    Args:
        db_name: SQLite database name (e.g., 'ai_infrastructure', 'sessions')
    
    Returns:
        str: PostgreSQL schema name (same as db_name, lowercased)
    
    Examples:
        'ai_infrastructure' -> 'ai_infrastructure'
        'sessions' -> 'sessions'
        'synergy_sessions' -> 'synergy_sessions'
    """
    return db_name.lower().replace('.db', '')


def get_database_connection(db_name: str = 'ai_infrastructure'):
    """
    Get database connection with auto-detection (SQLite or Supabase)
    
    Args:
        db_name: Database name without extension
                 Examples: 'ai_infrastructure', 'sessions', 'synergy_sessions'
    
    Returns:
        Connection object (sqlite3.Connection or psycopg2.Connection)
        
    Environment Detection:
        Local Dev: Returns SQLite connection to data/{db_name}.db
        Render: Returns PostgreSQL connection to Supabase
    
    Raises:
        ImportError: If USE_SUPABASE=true but psycopg2 not installed
        ConnectionError: If database connection fails
    
    Examples:
        # Local development (USE_SUPABASE not set)
        conn = get_database_connection('ai_infrastructure')
        # -> sqlite3.Connection to data/ai_infrastructure.db
        
        # Render deployment (USE_SUPABASE=true)
        conn = get_database_connection('ai_infrastructure')
        # -> psycopg2.Connection to Supabase (ai_infrastructure schema)
    """
    if is_using_supabase():
        # SUPABASE POSTGRESQL (Render deployment)
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
        except ImportError:
            raise ImportError(
                "psycopg2 not installed. Run: pip install psycopg2-binary"
            )
        
        db_url = os.getenv('SUPABASE_DB_URL')
        if not db_url:
            raise ValueError(
                "SUPABASE_DB_URL not set in environment. "
                "Add to .env.master or Render environment variables."
            )
        
        try:
            conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
            
            # Set search_path to use the correct schema
            schema_name = get_supabase_schema_name(db_name)
            with conn.cursor() as cursor:
                cursor.execute(f"SET search_path TO {schema_name}, public")
            
            print(f"🔷 [DB] Connected to Supabase PostgreSQL (schema: {schema_name})")
            return conn
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Supabase: {e}")
    
    else:
        # SQLITE (Local development)
        # Find project root (go up from AI_infrastructure/shared/)
        root_dir = Path(__file__).parent.parent.parent
        db_path = root_dir / 'data' / f'{db_name}.db'
        
        # Ensure data directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            
            print(f"🔷 [DB] Connected to SQLite: {db_path}")
            return conn
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to SQLite: {e}")


def get_database_path(db_name: str = 'ai_infrastructure') -> Path:
    """
    Get path to SQLite database file (local dev only)
    
    Args:
        db_name: Database name without extension
    
    Returns:
        Path: Absolute path to SQLite database
    
    Raises:
        ValueError: If called when USE_SUPABASE=true
    
    Note:
        Only use this for SQLite-specific operations.
        For queries, use get_database_connection() instead.
    """
    if is_using_supabase():
        raise ValueError(
            "get_database_path() only works with SQLite. "
            "Use get_database_connection() for PostgreSQL."
        )
    
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / f'{db_name}.db'
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    return db_path


def execute_query(db_name: str, query: str, params: tuple = None, fetch: str = 'all'):
    """
    Execute SQL query with auto-detection (SQLite or Supabase)
    
    Args:
        db_name: Database name (e.g., 'ai_infrastructure')
        query: SQL query (use %s for parameters, works for both)
        params: Query parameters as tuple
        fetch: 'all' | 'one' | 'none' (for SELECT queries)
    
    Returns:
        Query results (list of dicts or single dict) or None for non-SELECT
    
    Examples:
        # Fetch all users
        users = execute_query('ai_infrastructure', 
                             'SELECT * FROM users WHERE active = %s',
                             (True,), 
                             fetch='all')
        
        # Fetch one user
        user = execute_query('ai_infrastructure',
                            'SELECT * FROM users WHERE id = %s',
                            (1,),
                            fetch='one')
        
        # Insert/Update (no fetch)
        execute_query('ai_infrastructure',
                     'UPDATE users SET last_login = %s WHERE id = %s',
                     ('2025-11-15', 1),
                     fetch='none')
    """
    conn = get_database_connection(db_name)
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch == 'all':
            results = cursor.fetchall()
        elif fetch == 'one':
            results = cursor.fetchone()
        else:
            results = None
        
        conn.commit()
        return results
        
    except Exception as e:
        conn.rollback()
        raise e
        
    finally:
        cursor.close()
        conn.close()


# Convenience functions for common databases
def get_ai_infrastructure_connection():
    """Get connection to ai_infrastructure database"""
    return get_database_connection('ai_infrastructure')


def get_sessions_connection():
    """Get connection to sessions database"""
    return get_database_connection('sessions')


def get_synergy_sessions_connection():
    """Get connection to synergy_sessions database"""
    return get_database_connection('synergy_sessions')


def get_stock_data_connection():
    """Get connection to stock_data database"""
    return get_database_connection('stock_data')


def get_kanban_analytics_connection():
    """Get connection to kanban_analytics database"""
    return get_database_connection('kanban_analytics')


def get_auto_increment_sql() -> str:
    """
    Get database-specific auto-increment syntax
    
    Returns:
        'AUTOINCREMENT' for SQLite
        'GENERATED ALWAYS AS IDENTITY' for PostgreSQL
    
    Usage:
        CREATE TABLE example (
            id INTEGER PRIMARY KEY {get_auto_increment_sql()},
            ...
        )
    """
    if is_using_supabase():
        return 'GENERATED ALWAYS AS IDENTITY'
    else:
        return 'AUTOINCREMENT'


def adapt_sql_for_database(sql: str) -> str:
    """
    Adapt SQL syntax for current database (SQLite or PostgreSQL)
    
    Converts:
    - AUTOINCREMENT → GENERATED ALWAYS AS IDENTITY (PostgreSQL)
    - INTEGER PRIMARY KEY AUTOINCREMENT → SERIAL PRIMARY KEY (PostgreSQL)
    
    Args:
        sql: SQL query with SQLite syntax
    
    Returns:
        Adapted SQL for current database
    
    Example:
        sql = "CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, ...)"
        adapted = adapt_sql_for_database(sql)
        # PostgreSQL: "CREATE TABLE users (id SERIAL PRIMARY KEY, ...)"
        # SQLite: unchanged
    """
    if is_using_supabase():
        # PostgreSQL adaptations
        # Replace INTEGER PRIMARY KEY AUTOINCREMENT with SERIAL PRIMARY KEY
        sql = sql.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
        sql = sql.replace('AUTOINCREMENT', '')  # Remove any remaining AUTOINCREMENT
        
        # Replace TEXT columns that should be VARCHAR
        # (optional - PostgreSQL accepts TEXT)
    
    return sql


if __name__ == '__main__':
    """Test database connection auto-detection"""
    print("=" * 60)
    print("Database Connection Auto-Detection Test")
    print("=" * 60)
    
    print(f"\nEnvironment: {'Supabase PostgreSQL' if is_using_supabase() else 'SQLite (Local)'}")
    print(f"USE_SUPABASE: {os.getenv('USE_SUPABASE', 'not set')}")
    
    # Test connections
    databases = ['ai_infrastructure', 'sessions', 'synergy_sessions']
    
    for db_name in databases:
        print(f"\nTesting {db_name}...")
        try:
            conn = get_database_connection(db_name)
            cursor = conn.cursor()
            
            # Test query
            if is_using_supabase():
                cursor.execute("SELECT version()")
                result = cursor.fetchone()
                version_str = result['version'] if isinstance(result, dict) else result[0]
                print(f"  ✅ Connected: {version_str[:50]}...")
            else:
                cursor.execute("SELECT sqlite_version()")
                result = cursor.fetchone()
                version_str = result[0] if hasattr(result, '__getitem__') else str(result)
                print(f"  ✅ Connected: SQLite {version_str}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
    
    print("\n" + "=" * 60)
