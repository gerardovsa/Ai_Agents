"""
Database Helpers
Connection helpers for SQL Server and SQLite databases

CONNECTION POOLING:
This module implements thread-local connection pooling to prevent database corruption
from concurrent access. Each worker thread maintains persistent connections that are
reused across requests, preventing the "database disk image is malformed" errors.
"""

import sqlite3
import threading
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

# Thread-local storage for connection pool
_local_storage = threading.local()

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


def get_sqlite_connection(db_path: str):
    """
    Get SQLite connection (legacy function - use get_pooled_sqlite_connection instead)
    
    Args:
        db_path: Path to SQLite database file
    
    Returns:
        sqlite3.Connection
    """
    try:
        db_file = Path(db_path)
        if not db_file.exists():
            raise DatabaseConnectionError(f"SQLite database not found: {db_path}")
        
        conn = sqlite3.connect(str(db_file))
        conn.row_factory = sqlite3.Row  # Return rows as dicts
        return conn
    
    except Exception as e:
        raise DatabaseConnectionError(f"SQLite connection failed: {e}")


@contextmanager
def get_pooled_sqlite_connection(db_path: str, timeout: float = 30.0):
    """
    Get pooled SQLite connection with thread-local storage
    
    This function maintains a pool of connections per thread, preventing database
    corruption from concurrent access. Each worker thread gets its own persistent
    connections that are reused across thousands of requests.
    
    Features:
    - Thread-local connection pool (each thread gets own connections)
    - WAL mode enabled (Write-Ahead Logging for 10x better concurrency)
    - Optimized PRAGMAs (64MB cache, 256MB mmap, NORMAL sync)
    - Auto-commit/rollback on context exit
    - Connection reuse prevents "database disk image is malformed" errors
    
    Args:
        db_path: Path to SQLite database file
        timeout: Lock timeout in seconds (default: 30s)
    
    Yields:
        sqlite3.Connection: Pooled database connection
    
    Example:
        with get_pooled_sqlite_connection('data/db.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
        # Connection automatically committed and kept in pool
    """
    # Initialize thread-local connection dict if needed
    if not hasattr(_local_storage, 'connections'):
        _local_storage.connections = {}
    
    # Use absolute path as cache key
    cache_key = str(Path(db_path).resolve())
    
    # Reuse existing connection for this thread if available
    if cache_key in _local_storage.connections:
        conn = _local_storage.connections[cache_key]
        try:
            # Verify connection is still valid
            conn.execute("SELECT 1")
            try:
                yield conn
                conn.commit()  # Commit on successful exit
            except Exception as e:
                conn.rollback()  # Rollback on error
                raise
            return  # Exit context manager properly
        except sqlite3.Error:
            # Connection broken, remove from pool
            try:
                conn.close()
            except:
                pass
            del _local_storage.connections[cache_key]
    
    # Create new connection with optimizations
    db_file = Path(db_path)
    if not db_file.exists():
        # Create parent directories if needed
        db_file.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(
        str(db_path),
        timeout=timeout,
        check_same_thread=False,  # Allow connection across threads (safe with thread-local storage)
        isolation_level=None  # Autocommit mode
    )
    conn.row_factory = sqlite3.Row
    
    # Enable WAL mode for 10x better concurrency
    # Skip on Render - ephemeral filesystem doesn't support WAL
    is_render = os.getenv('RENDER') == 'true' or 'onrender.com' in os.getenv('RENDER_EXTERNAL_URL', '')
    
    if not is_render:
        try:
            conn.execute('PRAGMA journal_mode=WAL')
        except sqlite3.OperationalError:
            # Fallback to DELETE mode if WAL fails
            conn.execute('PRAGMA journal_mode=DELETE')
    else:
        conn.execute('PRAGMA journal_mode=DELETE')
    
    # Optimize for performance and concurrency
    conn.execute('PRAGMA synchronous=NORMAL')  # Faster than FULL, still safe
    conn.execute('PRAGMA cache_size=-64000')  # 64MB cache (negative = KB)
    
    # Skip mmap on Render - can cause issues with ephemeral filesystem
    if not is_render:
        conn.execute('PRAGMA mmap_size=268435456')  # 256MB memory-mapped I/O
    
    conn.execute('PRAGMA temp_store=MEMORY')  # Store temp tables in memory
    
    # Store in thread-local pool
    _local_storage.connections[cache_key] = conn
    
    try:
        yield conn
        conn.commit()  # Commit on successful exit
    except Exception as e:
        conn.rollback()  # Rollback on error
        raise
    # Note: Connection is NOT closed - kept in pool for reuse


def get_stock_database_path() -> str:
    """
    Get path to stock database (stock_data.db)
    
    Returns:
        Absolute path to stock database
    """
    # Stock database location
    stock_db = Path(__file__).parent.parent.parent / 'Quote_Calculator' / 'stocks' / 'stock_data.db'
    return str(stock_db)


def get_sessions_database_path() -> str:
    """
    Get path to sessions database (sessions.db)
    
    CORRECT DATABASE for threads, user data, credentials, OAuth tokens
    
    Returns:
        Absolute path to sessions.db
    """
    # Sessions database location (CORRECT for threads)
    sessions_db = Path(__file__).parent.parent.parent / 'data' / 'sessions.db'
    return str(sessions_db)


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


def execute_sqlite_query(db_path: str, query: str, params: Optional[tuple] = None) -> List[Dict]:
    """
    Execute database query and return results as list of dicts (Supabase or SQLite)
    
    MIGRATION NOTE: This function now uses Supabase PostgreSQL instead of SQLite.
    The db_path parameter is used to determine the schema:
      - Contains 'sessions': uses 'sessions' schema
      - Contains 'synergy': uses 'synergy_sessions' schema
      - Otherwise: uses 'ai_infrastructure' schema
    
    Args:
        db_path: Path to SQLite database (legacy) or schema name identifier
        query: SQL query (use %s placeholders, not ?)
        params: Query parameters
    
    Returns:
        List of dictionaries (rows)
    """
    try:
        # Import here to avoid circular dependencies
        from shared.database_utils import get_database_connection
        
        # Determine schema from db_path
        if 'sessions' in str(db_path).lower():
            schema = 'sessions'
        elif 'synergy' in str(db_path).lower():
            schema = 'synergy_sessions'
        else:
            schema = 'ai_infrastructure'
        
        # Use Supabase-compatible connection
        conn = get_database_connection(schema)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Fetch rows
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        results = [dict(row) for row in rows] if rows else []
        
        cursor.close()
        conn.close()
        
        return results
    
    except Exception as e:
        raise DatabaseConnectionError(f"Database query failed: {e}")


def execute_sqlite_update(db_path: str, query: str, params: Optional[tuple] = None) -> int:
    """
    Execute database UPDATE/INSERT/DELETE and return affected rows (Supabase or SQLite)
    
    MIGRATION NOTE: This function now uses Supabase PostgreSQL instead of SQLite.
    The db_path parameter is used to determine the schema:
      - Contains 'sessions': uses 'sessions' schema
      - Contains 'synergy': uses 'synergy_sessions' schema
      - Otherwise: uses 'ai_infrastructure' schema
    
    Args:
        db_path: Path to SQLite database (legacy) or schema name identifier
        query: SQL query (use %s placeholders, not ?)
        params: Query parameters
    
    Returns:
        Number of affected rows
    """
    try:
        # Import here to avoid circular dependencies
        from shared.database_utils import get_database_connection
        
        # Determine schema from db_path
        if 'sessions' in str(db_path).lower():
            schema = 'sessions'
        elif 'synergy' in str(db_path).lower():
            schema = 'synergy_sessions'
        else:
            schema = 'ai_infrastructure'
        
        # Use Supabase-compatible connection
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


def get_sqlite_schema(db_path: str) -> Dict[str, List[Dict]]:
    """
    Get SQLite database schema
    
    Args:
        db_path: Path to SQLite database
    
    Returns:
        Dictionary with table names as keys, column info as values
    """
    conn = None
    try:
        conn = get_sqlite_connection(db_path)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row['name'] for row in cursor.fetchall()]
        
        # Get columns for each table
        schema = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'name': row['name'],
                    'type': row['type'],
                    'notnull': bool(row['notnull']),
                    'pk': bool(row['pk'])
                })
            schema[table] = columns
        
        return schema
    
    finally:
        if conn:
            conn.close()
