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
import threading
import time
from dotenv import load_dotenv

# Load environment variables from project root
_root_dir = Path(__file__).parent.parent.parent
_env_file = _root_dir / '.env.master'
if _env_file.exists():
    load_dotenv(_env_file)
else:
    load_dotenv()  # Try default .env

# CONNECTION POOLING - Thread-safe connection pools
_connection_pools = {}
_pool_lock = threading.Lock()
_pool_stats = {
    'pools_created': 0,
    'connections_acquired': 0,
    'connections_returned': 0,
    'pool_hits': 0,
    'pool_misses': 0,
    'total_wait_time': 0.0,
    'avg_wait_time': 0.0
}

def is_using_supabase() -> bool:
    """
    Check if application should use Supabase PostgreSQL
    
    Returns:
        bool: True if USE_SUPABASE=true AND SUPABASE_DB_URL is set, False otherwise
    
    Environment Variables:
        USE_SUPABASE: Set to 'true' to enable Supabase (default: false)
        SUPABASE_DB_URL: Required when USE_SUPABASE=true
    
    Local Development:
        - Set USE_SUPABASE=false (or unset) to use SQLite
        - SQLite databases in data/ folder
    
    Production (Render):
        - Set USE_SUPABASE=true to use Supabase PostgreSQL
        - Requires SUPABASE_DB_URL environment variable
    """
    # Check if Supabase is explicitly enabled
    use_supabase = os.getenv('USE_SUPABASE', 'false').lower() == 'true'
    
    # If Supabase enabled, verify connection URL is set
    if use_supabase:
        has_url = bool(os.getenv('SUPABASE_DB_URL'))
        if not has_url:
            print("⚠️  [DB] USE_SUPABASE=true but SUPABASE_DB_URL not set, falling back to SQLite")
            return False
        return True
    
    return False


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


def get_connection_pool(schema_name: str):
    """
    Get or create thread-safe connection pool for schema
    
    CONNECTION POOLING BENEFITS:
    - 10-100x faster connections (reuse instead of create)
    - Thread-safe for concurrent requests
    - Resource efficient (maintains 2-20 connections)
    - Automatic cleanup (connections returned to pool)
    
    Args:
        schema_name: PostgreSQL schema name
    
    Returns:
        psycopg2.pool.ThreadedConnectionPool
    
    Pool Configuration:
        - Min connections: 2 (always ready)
        - Max connections: 20 (scales with traffic)
        - Connection timeout: 30s
        - Statement timeout: 60s
    """
    global _connection_pools, _pool_stats
    
    with _pool_lock:
        if schema_name not in _connection_pools:
            try:
                import psycopg2
                from psycopg2 import pool
            except ImportError:
                raise ImportError("psycopg2 not installed. Run: pip install psycopg2-binary")
            
            db_url = os.getenv('SUPABASE_DB_URL')
            if not db_url:
                raise ValueError("SUPABASE_DB_URL not set in environment")
            
            # Create thread-safe connection pool
            # Min=2 (always ready), Max=20 (scales with traffic)
            _connection_pools[schema_name] = pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=20,
                dsn=db_url,
                sslmode='require',
                connect_timeout=30,
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5
            )
            
            _pool_stats['pools_created'] += 1
            _pool_stats['pool_misses'] += 1
            
            print(f"🔷 [POOL] Created connection pool for '{schema_name}' (2-20 connections)")
            print(f"🔷 [POOL] Total pools: {_pool_stats['pools_created']}")
        else:
            _pool_stats['pool_hits'] += 1
        
        return _connection_pools[schema_name]


def get_pool_stats():
    """
    Get connection pool statistics
    
    Returns:
        dict: Pool stats including hits, misses, avg wait time
    """
    global _pool_stats
    
    if _pool_stats['connections_acquired'] > 0:
        _pool_stats['avg_wait_time'] = (
            _pool_stats['total_wait_time'] / _pool_stats['connections_acquired']
        )
    
    return dict(_pool_stats)


def close_all_pools():
    """
    Close all connection pools (for graceful shutdown)
    """
    global _connection_pools
    
    with _pool_lock:
        for schema_name, pool_instance in _connection_pools.items():
            try:
                pool_instance.closeall()
                print(f"🔷 [POOL] Closed pool for '{schema_name}'")
            except Exception as e:
                print(f"❌ [POOL] Error closing pool '{schema_name}': {e}")
        
        _connection_pools.clear()
        print(f"🔷 [POOL] All pools closed")


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
        # SUPABASE POSTGRESQL WITH CONNECTION POOLING (Render deployment)
        global _pool_stats
        
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
        except ImportError:
            raise ImportError(
                "psycopg2 not installed. Run: pip install psycopg2-binary"
            )
        
        schema_name = get_supabase_schema_name(db_name)
        
        try:
            # GET CONNECTION FROM POOL (FAST - reuses existing connections)
            start_time = time.time()
            pool_instance = get_connection_pool(schema_name)
            conn = pool_instance.getconn()
            wait_time = time.time() - start_time
            
            # Track pool stats
            _pool_stats['connections_acquired'] += 1
            _pool_stats['total_wait_time'] += wait_time
            
            # Set search_path and configure connection
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
            cursor.execute(f"SET search_path TO {schema_name}, public")
            cursor.execute("SET statement_timeout = '60s'")
            cursor.close()
            conn.commit()
            
            print(f"🔷 [POOL] Got connection from pool for '{schema_name}' (wait: {wait_time*1000:.1f}ms)")
            
            # Wrap connection to return to pool on close
            # Can't override conn.close directly on psycopg2 (read-only), so use wrapper
            class PooledConnection:
                def __init__(self, conn, pool, schema):
                    self._conn = conn
                    self._pool = pool
                    self._schema = schema
                    self._closed = False
                
                def close(self):
                    """Return to pool instead of closing"""
                    if not self._closed:
                        try:
                            if not self._conn.closed:
                                self._conn.rollback()
                                self._pool.putconn(self._conn)
                                _pool_stats['connections_returned'] += 1
                            self._closed = True
                        except Exception as e:
                            print(f"⚠️ [POOL] Error returning connection: {e}")
                
                def __getattr__(self, name):
                    return getattr(self._conn, name)
                
                def __enter__(self):
                    return self
                
                def __exit__(self, exc_type, exc_val, exc_tb):
                    self.close()
                    return False
            
            pooled_conn = PooledConnection(conn, pool_instance, schema_name)
            
            # Wrap with DatabaseConnection for placeholder conversion
            return DatabaseConnection(pooled_conn)
            
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
                time.sleep(2)  # Wait 2 seconds before retry
                
                print(f"🔷 [DB] Retry attempt for '{db_name}'...")
                conn = psycopg2.connect(
                    db_url,
                    cursor_factory=RealDictCursor,
                    connect_timeout=30,
                    keepalives=1,
                    keepalives_idle=30,
                    keepalives_interval=10,
                    keepalives_count=5,
                    options='-c client_min_messages=ERROR'  # Suppress server warnings
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
    
    # SQLITE (Local development ONLY - requires USE_SQLITE=true)
    # Find project root (go up from AI_infrastructure/shared/)
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / f'{db_name}.db'
    
    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        
        print(f"🔷 [DB] Connected to SQLite (LOCAL DEV): {db_path}")
        print(f"⚠️ [DB] USE_SQLITE=true - Production should use Supabase!")
        
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


def convert_sql_placeholders(sql: str, params: tuple = None):
    """
    Convert SQL placeholders from SQLite ( %s) to PostgreSQL (%s) style
    
    Args:
        sql: SQL query with ? placeholders (SQLite style)
        params: Query parameters tuple (optional)
    
    Returns:
        - If params is None: returns converted SQL string only
        - If params provided: returns tuple of (converted_sql, params)
    
    Example:
        # Simple usage (string only):
        sql = convert_sql_placeholders("SELECT * FROM users WHERE id = %s")
        # Returns: "SELECT * FROM users WHERE id = %s"
        
        # With params (tuple):
        sql, params = convert_sql_placeholders("SELECT * FROM users WHERE id = %s", (123,))
        # Returns: ("SELECT * FROM users WHERE id = %s", (123,))
    """
    if is_using_supabase():
        # Convert ? to %s for PostgreSQL
        converted_sql = sql.replace('?', '%s')
        if params is None:
            return converted_sql
        else:
            return (converted_sql, params)
    else:
        # Keep as-is for SQLite
        if params is None:
            return sql
        else:
            return (sql, params)


class DatabaseCursor:
    """
    Cursor wrapper that automatically converts SQL placeholders
    
    Usage:
        conn = get_database_connection('ai_infrastructure')
        cursor = DatabaseCursor(conn)
        cursor.execute("SELECT * FROM users WHERE id = %s", (123,))
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
        if is_using_supabase():
            # Convert PostgreSQL numbered positional parameters ($1, $2, ...) to psycopg2 format (%s, %s, ...)
            import re
            # Replace $1, $2, $3, etc. with %s in sequential order
            sql = re.sub(r'\$\d+', '%s', sql)
        
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
