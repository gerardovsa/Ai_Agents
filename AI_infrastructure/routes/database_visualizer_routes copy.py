"""

Database Visualizer Routes
Provides API endpoints for exploring SQLite databases
"""

from flask import Blueprint, request, jsonify
import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Import database helpers
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database_helpers import get_sqlite_connection, get_sqlite_schema

database_visualizer_bp = Blueprint('database_visualizer', __name__, url_prefix='/api/database-visualizer')


def find_database_files(root_path: str = None) -> List[Dict]:
    """
    Find all .db files in the project
    
    Args:
        root_path: Root directory to search (defaults to project root)
        
    Returns:
        List of database file info dictionaries
    """
    if root_path is None:
        # Start from project root (3 levels up from this file)
        root_path = Path(__file__).parent.parent.parent
    else:
        root_path = Path(root_path)
    
    databases = []
    
    # Search for .db files
    for db_file in root_path.rglob('*.db'):
        try:
            # Skip if in venv or node_modules
            if 'venv' in str(db_file) or 'node_modules' in str(db_file):
                continue
            
            # Get file info
            stat = db_file.stat()
            
            # Get table count
            table_count = 0
            try:
                conn = sqlite3.connect(str(db_file))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                conn.close()
            except Exception as e:
                print(f"Warning: Could not read {db_file}: {e}")
            
            # Relative path from project root
            try:
                relative_path = db_file.relative_to(root_path)
            except ValueError:
                relative_path = db_file
            
            databases.append({
                'name': db_file.name,
                'path': str(db_file),
                'relative_path': str(relative_path),
                'size_bytes': stat.st_size,
                'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'table_count': table_count
            })
            
        except Exception as e:
            print(f"Error processing {db_file}: {e}")
            continue
    
    # Sort by name
    databases.sort(key=lambda x: x['name'])
    
    return databases


@database_visualizer_bp.route('/list-databases', methods=['GET'])
def list_databases():
    """
    List all .db files in the project
    
    Returns:
        JSON with list of databases
    """
    try:
        databases = find_database_files()
        
        return jsonify({
            'success': True,
            'databases': databases,
            'count': len(databases)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@database_visualizer_bp.route('/schema', methods=['GET'])
def get_schema():
    """
    Get schema for a specific database
    
    Query params:
        db_path: Path to database file
        
    Returns:
        JSON with schema information
    """
    try:
        db_path = request.args.get('db_path')
        
        if not db_path:
            return jsonify({
                'success': False,
                'error': 'db_path parameter required'
            }), 400
        
        # Validate file exists
        if not os.path.exists(db_path):
            return jsonify({
                'success': False,
                'error': f'Database file not found: {db_path}'
            }), 404
        
        # Get schema using helper function
        schema = get_sqlite_schema(db_path)
        
        return jsonify({
            'success': True,
            'schema': schema,
            'db_path': db_path,
            'table_count': len(schema)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@database_visualizer_bp.route('/table-data', methods=['GET'])
def get_table_data():
    """
    Get data from a specific table
    
    Query params:
        db_path: Path to database file
        table: Table name
        limit: Max rows to return (default 1000)
        
    Returns:
        JSON with table data
    """
    try:
        db_path = request.args.get('db_path')
        table = request.args.get('table')
        limit = request.args.get('limit', 1000, type=int)
        
        if not db_path or not table:
            return jsonify({
                'success': False,
                'error': 'db_path and table parameters required'
            }), 400
        
        # Validate file exists
        if not os.path.exists(db_path):
            return jsonify({
                'success': False,
                'error': f'Database file not found: {db_path}'
            }), 404
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get data (with limit)
        cursor.execute(f"SELECT * FROM {table} LIMIT %s", (limit,))
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        data = [dict(row) for row in rows]
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': data,
            'columns': columns,
            'row_count': len(data),
            'total_count': total_count,
            'limited': total_count > limit
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@database_visualizer_bp.route('/table-info', methods=['GET'])
def get_table_info():
    """
    Get detailed information about a table
    
    Query params:
        db_path: Path to database file
        table: Table name
        
    Returns:
        JSON with table information
    """
    try:
        db_path = request.args.get('db_path')
        table = request.args.get('table')
        
        if not db_path or not table:
            return jsonify({
                'success': False,
                'error': 'db_path and table parameters required'
            }), 400
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [dict(row) for row in cursor.fetchall()]
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        row_count = cursor.fetchone()[0]
        
        # Get indexes
        cursor.execute(f"PRAGMA index_list({table})")
        indexes = [dict(row) for row in cursor.fetchall()]
        
        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        foreign_keys = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'table': table,
            'columns': columns,
            'row_count': row_count,
            'indexes': indexes,
            'foreign_keys': foreign_keys
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@database_visualizer_bp.route('/execute-query', methods=['POST'])
def execute_query():
    """
    Execute a SELECT query (read-only)
    
    JSON body:
        db_path: Path to database file
        query: SQL query (SELECT only)
        
    Returns:
        JSON with query results
    """
    try:
        data = request.get_json()
        db_path = data.get('db_path')
        query = data.get('query', '').strip()
        
        if not db_path or not query:
            return jsonify({
                'success': False,
                'error': 'db_path and query required'
            }), 400
        
        # Validate it's a SELECT query (security)
        if not query.upper().startswith('SELECT'):
            return jsonify({
                'success': False,
                'error': 'Only SELECT queries are allowed'
            }), 400
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Execute query
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        results = [dict(row) for row in rows]
        
        # Get column names
        columns = [description[0] for description in cursor.description] if cursor.description else []
        
        conn.close()
        
        return jsonify({
            'success': True,
            'results': results,
            'columns': columns,
            'row_count': len(results)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Export blueprint
__all__ = ['database_visualizer_bp']
