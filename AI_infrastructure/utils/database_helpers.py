"""
Database Helpers
Connection helpers for SQL Server and SQLite databases
"""

import sqlite3
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
    Get SQLite connection
    
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
    Execute SQLite query and return results as list of dicts
    
    Args:
        db_path: Path to SQLite database
        query: SQL query
        params: Query parameters
    
    Returns:
        List of dictionaries (rows)
    """
    conn = None
    try:
        conn = get_sqlite_connection(db_path)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Fetch rows (already as dicts due to row_factory)
        rows = cursor.fetchall()
        
        # Convert sqlite3.Row to dict
        results = [dict(row) for row in rows]
        
        return results
    
    finally:
        if conn:
            conn.close()


def execute_sqlite_update(db_path: str, query: str, params: Optional[tuple] = None) -> int:
    """
    Execute SQLite UPDATE/INSERT/DELETE and return affected rows
    
    Args:
        db_path: Path to SQLite database
        query: SQL query
        params: Query parameters
    
    Returns:
        Number of affected rows
    """
    conn = None
    try:
        conn = get_sqlite_connection(db_path)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        return cursor.rowcount
    
    finally:
        if conn:
            conn.close()


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
