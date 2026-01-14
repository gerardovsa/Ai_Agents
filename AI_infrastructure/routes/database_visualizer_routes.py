"""

Database Visualizer Routes
Provides API endpoints for exploring Supabase PostgreSQL databases

MIGRATION STATUS: ✅ COMPLETE - Migrated from SQLite to Supabase PostgreSQL
LAST UPDATED: 2025-12-07

ENDPOINTS:
- GET /list-databases - List all PostgreSQL schemas
- GET /schema - Get schema structure (tables, columns)
- GET /table-data - Query table data with pagination
- GET /table-info - Get detailed table metadata
- POST /execute-query - Execute read-only SELECT queries

SCHEMA ARCHITECTURE:
- ai_infrastructure - User management, tokens, preferences
- sessions - Threads, messages, OAuth tokens
- synergy_sessions - Synergy workflow data
- stock_data - Stock market data
- kanban_analytics - Kanban board analytics
"""

from flask import Blueprint, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import os
import sys

# Import Supabase database utilities
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared.database_utils import get_database_connection

database_visualizer_bp = Blueprint('database_visualizer', __name__, url_prefix='/api/database-visualizer')


def list_supabase_schemas():
    """
    List all available Supabase PostgreSQL schemas
    
    Returns:
        List of schema information dictionaries
    """
    conn = None
    try:
        # Connect to default schema to query information_schema
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query all schemas with table counts
        query = """
        SELECT 
            s.schema_name,
            COUNT(t.table_name) as table_count
        FROM information_schema.schemata s
        LEFT JOIN information_schema.tables t 
            ON s.schema_name = t.table_schema 
            AND t.table_type = 'BASE TABLE'
        WHERE s.schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        GROUP BY s.schema_name
        ORDER BY s.schema_name
        """
        
        cursor.execute(query)
        schemas = cursor.fetchall()
        
        return [
            {
                'name': f"{schema['schema_name']} schema",
                'schema': schema['schema_name'],
                'table_count': schema['table_count'],
                'type': 'postgresql'
            }
            for schema in schemas
        ]
        
    except Exception as e:
        print(f"Error listing Supabase schemas: {e}")
        return []
    finally:
        if conn:
            conn.close()


@database_visualizer_bp.route('/list-databases', methods=['GET'])
def list_databases():
    """
    List all Supabase PostgreSQL schemas
    
    Returns:
        JSON with list of schemas
    """
    try:
        schemas = list_supabase_schemas()
        
        return jsonify({
            'success': True,
            'databases': schemas,
            'count': len(schemas)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@database_visualizer_bp.route('/schema', methods=['GET'])
def get_schema():
    """
    Get schema for a Supabase PostgreSQL schema
    
    Query params:
        schema: Schema name (e.g., 'stock_data', 'sessions')
        db_path: (deprecated, use schema instead)
        
    Returns:
        JSON with schema information
    """
    conn = None
    try:
        # Support both 'schema' and legacy 'db_path' parameters
        schema_name = request.args.get('schema') or request.args.get('db_path')
        
        if not schema_name:
            return jsonify({
                'success': False,
                'error': 'schema parameter required'
            }), 400
        
        # Extract schema name from db_path if needed (backward compatibility)
        if '/' in schema_name or '\\' in schema_name:
            # Legacy db_path format: extract schema from path
            schema_name = schema_name.split('/')[-1].split('\\')[-1].replace('.db', '')
        
        # Connect to schema
        conn = get_database_connection(schema_name)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all tables in schema
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        schema = {}
        for table_row in tables:
            table_name = table_row['table_name']
            
            # Get columns for this table
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            
            columns = cursor.fetchall()
            schema[table_name] = columns
        
        return jsonify({
            'success': True,
            'schema': schema,
            'schema_name': schema_name,
            'table_count': len(schema)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()


@database_visualizer_bp.route('/table-data', methods=['GET'])
def get_table_data():
    """
    Get data from a specific table in Supabase PostgreSQL
    
    Query params:
        schema: Schema name (e.g., 'stock_data')
        table: Table name
        limit: Max rows to return (default 1000)
        db_path: (deprecated, use schema instead)
        
    Returns:
        JSON with table data
    """
    conn = None
    try:
        schema_name = request.args.get('schema') or request.args.get('db_path')
        table = request.args.get('table')
        limit = request.args.get('limit', 1000, type=int)
        
        if not schema_name or not table:
            return jsonify({
                'success': False,
                'error': 'schema and table parameters required'
            }), 400
        
        # Extract schema from legacy db_path format
        if '/' in schema_name or '\\' in schema_name:
            schema_name = schema_name.split('/')[-1].split('\\')[-1].replace('.db', '')
        
        # Connect to schema
        conn = get_database_connection(schema_name)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get data with limit (using sql.Identifier for safety)
        query = sql.SQL("SELECT * FROM {} LIMIT %s").format(sql.Identifier(table))
        cursor.execute(query, (limit,))
        data = cursor.fetchall()
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Get total count
        count_query = sql.SQL("SELECT COUNT(*) as count FROM {}").format(sql.Identifier(table))
        cursor.execute(count_query)
        total_count = cursor.fetchone()['count']
        
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
    finally:
        if conn:
            conn.close()


@database_visualizer_bp.route('/table-info', methods=['GET'])
def get_table_info():
    """
    Get detailed information about a Supabase PostgreSQL table
    
    Query params:
        schema: Schema name
        table: Table name
        db_path: (deprecated, use schema instead)
        
    Returns:
        JSON with table information
    """
    conn = None
    try:
        schema_name = request.args.get('schema') or request.args.get('db_path')
        table = request.args.get('table')
        
        if not schema_name or not table:
            return jsonify({
                'success': False,
                'error': 'schema and table parameters required'
            }), 400
        
        # Extract schema from legacy format
        if '/' in schema_name or '\\' in schema_name:
            schema_name = schema_name.split('/')[-1].split('\\')[-1].replace('.db', '')
        
        # Connect to schema
        conn = get_database_connection(schema_name)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get column information
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table,))
        columns = cursor.fetchall()
        
        # Get row count
        count_query = sql.SQL("SELECT COUNT(*) as count FROM {}").format(sql.Identifier(table))
        cursor.execute(count_query)
        row_count = cursor.fetchone()['count']
        
        # Get indexes
        cursor.execute("""
            SELECT
                indexname as name,
                indexdef as definition
            FROM pg_indexes
            WHERE schemaname = 'public' AND tablename = %s
        """, (table,))
        indexes = cursor.fetchall()
        
        # Get foreign keys
        cursor.execute("""
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public'
                AND tc.table_name = %s
        """, (table,))
        foreign_keys = cursor.fetchall()
        
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
    finally:
        if conn:
            conn.close()


@database_visualizer_bp.route('/execute-query', methods=['POST'])
def execute_query():
    """
    Execute a SELECT query (read-only) on Supabase PostgreSQL
    
    JSON body:
        schema: Schema name (e.g., 'stock_data')
        query: SQL query (SELECT only)
        db_path: (deprecated, use schema instead)
        
    Returns:
        JSON with query results
    """
    conn = None
    try:
        data = request.get_json()
        schema_name = data.get('schema') or data.get('db_path')
        query = data.get('query', '').strip()
        
        if not schema_name or not query:
            return jsonify({
                'success': False,
                'error': 'schema and query required'
            }), 400
        
        # Extract schema from legacy format
        if '/' in schema_name or '\\' in schema_name:
            schema_name = schema_name.split('/')[-1].split('\\')[-1].replace('.db', '')
        
        # Validate it's a read-only query (security)
        query_upper = query.upper()
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'TRUNCATE', 'ALTER', 'CREATE']
        if any(keyword in query_upper for keyword in dangerous_keywords):
            return jsonify({
                'success': False,
                'error': 'Only SELECT queries are allowed'
            }), 400
        
        # Connect to schema
        conn = get_database_connection(schema_name)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Execute query
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Get column names
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
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
    finally:
        if conn:
            conn.close()


# Export blueprint
__all__ = ['database_visualizer_bp']
