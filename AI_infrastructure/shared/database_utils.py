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
        bool: True if SUPABASE_URL is set OR USE_SUPABASE=true
              False only if USE_SQLITE=true (explicit override)
    
    Environment Variables:
        USE_SQLITE: Set to 'true' to force SQLite (overrides everything)
        SUPABASE_URL: If set, automatically use Supabase
        USE_SUPABASE: Set to 'true' to enable Supabase
    
    Priority:
        1. USE_SQLITE=true → Force SQLite (explicit override)
        2. SUPABASE_URL exists → Use Supabase (auto-detect)
        3. USE_SUPABASE=true → Use Supabase (explicit enable)
        4. Otherwise → SQLite (safe default)
    """
    # Check for explicit SQLite override (highest priority)
    if os.getenv('USE_SQLITE', 'false').lower() == 'true':
        return False
    
    # Check if Supabase credentials exist (auto-detect)
    supabase_url = os.getenv('SUPABASE_URL')
    if supabase_url:
        return True
    
    # Check USE_SUPABASE setting (explicit enable)
    use_supabase = os.getenv('USE_SUPABASE', 'false').lower() == 'true'
    
    return use_supabase


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
        
        # Get connection string from environment
        db_url = os.getenv('SUPABASE_DB_URL')
        if not db_url:
            raise ValueError(
                "SUPABASE_DB_URL not set in environment. "
                "Use Session Pooler URL: postgresql://postgres.PROJECT:[PASSWORD]@aws-X-region.pooler.supabase.com:5432/postgres"
            )
        
        try:
            # Connect to Supabase Session Pooler (IPv4 compatible)
            # Use connection pooler for Render compatibility
            print(f"🔷 [DB] Attempting Supabase connection for '{db_name}'...")
            print(f"🔷 [DB] Connection timeout: 30s, Statement timeout: 60s")
            
            conn = psycopg2.connect(
                db_url,
                cursor_factory=RealDictCursor,
                connect_timeout=30,
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5,
                options='-c statement_timeout=60000'  # 60 seconds statement timeout (in milliseconds)
            )
            
            # Set search_path to use the correct schema
            schema_name = get_supabase_schema_name(db_name)
            with conn.cursor() as cursor:
                # Create schema if it doesn't exist
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
                cursor.execute(f"SET search_path TO {schema_name}, public")
                # Set statement timeout for all queries on this connection
                cursor.execute("SET statement_timeout = '60s'")
            
            conn.commit()
            print(f"✅ [DB] Connected to Supabase PostgreSQL (schema: {schema_name})")
            
            # Wrap connection to provide automatic placeholder conversion
            return DatabaseConnection(conn)
            
        except psycopg2.OperationalError as e:
            # Connection failed - detailed error logging
            error_msg = str(e)
            print(f"\n{'='*70}")
            print(f"❌ [DB] SUPABASE CONNECTION FAILED - OPERATIONAL ERROR")
            print(f"{'='*70}")
            print(f"Database: {db_name}")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {error_msg}")
            
            # Detailed diagnostics
            if "timeout" in error_msg.lower():
                print(f"\n🔍 DIAGNOSIS: Connection timeout")
                print(f"   - Supabase server may be slow or unreachable")
                print(f"   - Network latency too high (>30 seconds)")
                print(f"   - Check internet connection")
                print(f"   - Try increasing connect_timeout value")
            elif "could not connect" in error_msg.lower():
                print(f"\n🔍 DIAGNOSIS: Cannot reach Supabase server")
                print(f"   - Check SUPABASE_DB_URL is correct")
                print(f"   - Verify Supabase project is active")
                print(f"   - Check firewall/network settings")
            elif "password" in error_msg.lower() or "authentication" in error_msg.lower():
                print(f"\n🔍 DIAGNOSIS: Authentication failed")
                print(f"   - Check database password in SUPABASE_DB_URL")
                print(f"   - Verify credentials haven't expired")
            else:
                print(f"\n🔍 DIAGNOSIS: Unknown operational error")
                print(f"   - Review full error message above")
            
            print(f"\n🔄 RECOVERY ATTEMPT: Retrying connection once...")
            print(f"{'='*70}\n")
            
            # Single retry attempt
            try:
                import time
                time.sleep(2)  # Wait 2 seconds before retry
                
                print(f"🔷 [DB] Retry attempt for '{db_name}'...")
                conn = psycopg2.connect(
                    db_url,
                    cursor_factory=RealDictCursor,
                    connect_timeout=30,
                    keepalives=1,
                    keepalives_idle=30,
                    keepalives_interval=10,
                    keepalives_count=5
                )
                
                schema_name = get_supabase_schema_name(db_name)
                with conn.cursor() as cursor:
                    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
                    cursor.execute(f"SET search_path TO {schema_name}, public")
                
                conn.commit()
                print(f"✅ [DB] RETRY SUCCESSFUL! Connected to Supabase")
                return DatabaseConnection(conn)
                
            except Exception as retry_error:
                print(f"❌ [DB] RETRY FAILED: {retry_error}")
                print(f"❌ [DB] CANNOT PROCEED - Supabase connection required")
                raise ConnectionError(
                    f"Supabase connection failed after retry. "
                    f"Original error: {error_msg}. "
                    f"Retry error: {str(retry_error)}"
                )
        
        except Exception as e:
            # Catch-all for other exceptions
            print(f"\n{'='*70}")
            print(f"❌ [DB] SUPABASE CONNECTION FAILED - UNEXPECTED ERROR")
            print(f"{'='*70}")
            print(f"Database: {db_name}")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print(f"{'='*70}\n")
            raise ConnectionError(f"Supabase connection failed: {e}")
    
    # SQLITE (Local development ONLY - Supabase must succeed first)
    # Find project root (go up from AI_infrastructure/shared/)
    root_dir = Path(__file__).parent.parent.parent
    
    # This code only runs if USE_SUPABASE is not set
    db_path = root_dir / 'data' / f'{db_name}.db'
    
    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        
        print(f"🔷 [DB] Connected to SQLite (LOCAL DEV): {db_path}")
        
        # Wrap connection to provide automatic placeholder conversion
        return DatabaseConnection(conn)
        
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
    Execute SQL query with auto-detection (SQLite or Supabase REST API)
    
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
    
    if is_using_supabase():
        # Supabase REST API - use RPC for raw SQL
        try:
            # Format query for Supabase (replace %s with $1, $2, etc.)
            formatted_query = query
            if params:
                for i, param in enumerate(params, 1):
                    formatted_query = formatted_query.replace('%s', f'${i}', 1)
            
            # Execute via Supabase RPC (requires function in database)
            # For now, we'll use table-based operations
            # NOTE: Full SQL support requires creating an RPC function in Supabase
            raise NotImplementedError(
                "Direct SQL queries not yet implemented for Supabase REST API. "
                "Use table-based operations: conn.table('users').select('*').execute()"
            )
            
        except Exception as e:
            raise e
    else:
        # SQLite
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


def convert_sql_placeholders(sql: str, params: tuple = None) -> Tuple[str, tuple]:
    """
    Convert SQL placeholders from SQLite (?) to PostgreSQL (%s) style
    
    Args:
        sql: SQL query with ? placeholders (SQLite style)
        params: Query parameters tuple
    
    Returns:
        Tuple of (converted_sql, params)
        - SQLite: returns unchanged (?, params)
        - PostgreSQL: converts ? to %s, returns (%s, params)
    
    Example:
        sql = "SELECT * FROM users WHERE id = ?"
        params = (123,)
        
        # SQLite: returns ("SELECT * FROM users WHERE id = ?", (123,))
        # PostgreSQL: returns ("SELECT * FROM users WHERE id = %s", (123,))
    """
    if is_using_supabase():
        # Convert ? to %s for PostgreSQL
        converted_sql = sql.replace('?', '%s')
        return (converted_sql, params)
    else:
        # Keep as-is for SQLite
        return (sql, params)


class DatabaseCursor:
    """
    Cursor wrapper that automatically converts SQL placeholders
    
    Usage:
        conn = get_database_connection('ai_infrastructure')
        cursor = DatabaseCursor(conn)
        cursor.execute("SELECT * FROM users WHERE id = ?", (123,))
        # Automatically converts ? to %s for PostgreSQL
    """
    def __init__(self, connection):
        self.connection = connection
        if is_using_supabase():
            # PostgreSQL cursor - but check if connection is actually PostgreSQL
            import sqlite3
            if isinstance(connection._wrapped_conn, sqlite3.Connection):
                # Supabase failed, fell back to SQLite - don't use cursor_factory
                self._cursor = connection._wrapped_conn.cursor()
            else:
                # Actual PostgreSQL connection
                import psycopg2.extras
                self._cursor = connection._wrapped_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            # SQLite cursor
            self._cursor = connection._wrapped_conn.cursor()
    
    def execute(self, sql, params=None):
        """Execute with automatic placeholder conversion"""
        if params:
            sql, params = convert_sql_placeholders(sql, params)
        return self._cursor.execute(sql, params)
    
    def fetchone(self):
        """Fetch one row"""
        return self._cursor.fetchone()
    
    def fetchall(self):
        """Fetch all rows"""
        return self._cursor.fetchall()
    
    def fetchmany(self, size=None):
        """Fetch many rows"""
        return self._cursor.fetchmany(size)
    
    def close(self):
        """Close cursor"""
        return self._cursor.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # Delegate other attributes to wrapped cursor
    def __getattr__(self, name):
        return getattr(self._cursor, name)


class DatabaseConnection:
    """
    Connection wrapper that provides automatic SQL placeholder conversion
    
    Wraps sqlite3.Connection or psycopg2.Connection and returns DatabaseCursor
    when cursor() is called, which automatically converts ? to %s for PostgreSQL.
    """
    def __init__(self, connection):
        self._wrapped_conn = connection
    
    def cursor(self, *args, **kwargs):
        """Return DatabaseCursor that auto-converts placeholders"""
        if args or kwargs:
            # If specific cursor factory requested, check if it's supported
            # SQLite doesn't support cursor_factory parameter
            import sqlite3
            if isinstance(self._wrapped_conn, sqlite3.Connection):
                # SQLite: Remove unsupported parameters, return DatabaseCursor
                # (row_factory is set at connection level, not cursor level)
                return DatabaseCursor(self)
            else:
                # PostgreSQL: Pass through cursor factory
                return self._wrapped_conn.cursor(*args, **kwargs)
        return DatabaseCursor(self)
    
    def commit(self):
        return self._wrapped_conn.commit()
    
    def rollback(self):
        return self._wrapped_conn.rollback()
    
    def close(self):
        return self._wrapped_conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._wrapped_conn.__exit__(exc_type, exc_val, exc_tb)
    
    # Delegate other attributes to wrapped connection
    def __getattr__(self, name):
        return getattr(self._wrapped_conn, name)


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
            
            # Test connection
            if is_using_supabase():
                # Supabase REST API client - test with health check
                print(f"  ✅ Connected: Supabase REST API client")
                print(f"  Schema: {conn._schema}")
            else:
                # SQLite
                cursor = conn.cursor()
                cursor.execute("SELECT sqlite_version()")
                result = cursor.fetchone()
                version_str = result[0] if hasattr(result, '__getitem__') else str(result)
                print(f"  ✅ Connected: SQLite {version_str}")
                cursor.close()
                conn.close()
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
    
    print("\n" + "=" * 60)
