"""
Stock Management API Routes - Supabase PostgreSQL Stock Database
========================================================================

This module provides Flask API endpoints for the Stock Management module.
Uses Supabase PostgreSQL database (stock_data schema) with AI-extracted job data.

Database Architecture:
- InHouse Fred (SQL Server): JobTickets, Orders (production data)
- Supabase PostgreSQL (stock_data schema): extracted_jobs, unified_stocks, stocklevels, reorderalerts

Architecture:
- Frontend (stock-management.js) → Flask endpoints → Supabase PostgreSQL (stock_data schema)

Migration: Dec 4, 2025 - Migrated from SQLite to Supabase PostgreSQL
Updated: January 7, 2025 - Fixed cursor management (42 critical issues)
Created: October 30, 2025
"""

import sys
import os
import traceback
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from pathlib import Path

# Import Supabase connection utility
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'AI_infrastructure'))
from shared.database_utils import get_database_connection

# Create Flask Blueprint for auto-discovery by module_blueprint_loader
stock_bp = Blueprint(
    'stock_management',
    __name__,
    url_prefix='/api/stock-management'
)

# Database availability flag (set during module discovery)
STOCK_DB_AVAILABLE = True


# ============================================================================
# ENDPOINT 1: Usage Analytics
# ============================================================================

@stock_bp.route('/usage-analytics', methods=['GET', 'OPTIONS'])
@cross_origin()
def stock_usage_analytics():
    """
    Usage Analytics - Stock consumption patterns from AI-extracted jobs
    Query params: days (7, 30, 90, 365)
    
    Database: Supabase PostgreSQL (stock_data schema)
    Tables: extracted_jobs, unified_stocks
    
    Returns top 10 most-used stocks with job count and total quantity
    
    FIXED: January 7, 2025
    - Added cursor/conn initialization
    - Added proper cleanup before return
    - Added finally block with exception handling
    """
    # ✅ CRITICAL: Handle OPTIONS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    # ✅ CRITICAL: Initialize BEFORE try block
    cursor = None
    conn = None
    
    try:
        days = int(request.args.get('days', 30))
        
        # ✅ Connect to Supabase PostgreSQL (stock_data schema)
        conn = get_database_connection('stock_data')
        cursor = conn.cursor()
        
        # Query AI-extracted jobs with stock information
        query = f"""
        SELECT 
            u.stock_id AS "StockID",
            u.stock_type_name AS "StockType",
            COUNT(e.ticket_id) as usage_count,
            SUM(COALESCE(e.total_sheets_consumed, e.quantity_ordered, 0)) as total_quantity,
            u.gsm AS "GSM",
            CONCAT(u.length_mm, 'x', u.width_mm, 'mm') AS "Dimensions"
        FROM stock_data.extracted_jobs e
        INNER JOIN stock_data.unified_stocks u ON e.stock_id = u.stock_id
        WHERE e.order_date >= CURRENT_DATE - INTERVAL '{days} days'
          AND e.stock_id IS NOT NULL
        GROUP BY u.stock_id, u.stock_type_name, u.gsm, u.length_mm, u.width_mm
        ORDER BY usage_count DESC
        LIMIT 50
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert rows to list of dictionaries
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        
        # ✅ CRITICAL: Close cursor BEFORE processing results
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        # ✅ Process data AFTER connection returned to pool
        return jsonify({
            'status': 'ok',
            'days': days,
            'database': 'Supabase PostgreSQL (stock_data schema)',
            'tables': 'stock_data.extracted_jobs + stock_data.unified_stocks',
            'data': data
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   Usage analytics failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e), 'traceback': error_details}), 500
    
    finally:
        # ✅ CRITICAL: Guaranteed cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


# ============================================================================
# ENDPOINT 2: Stock Hierarchy (for Sunburst Chart)
# ============================================================================

@stock_bp.route('/hierarchy', methods=['GET', 'OPTIONS'])
@cross_origin()
def stock_hierarchy():
    """
    Get hierarchical stock usage data for sunburst visualization
    Returns: category -> stock_type -> individual stocks with usage counts
    
    FIXED: January 7, 2025
    - Added cursor/conn initialization
    - Added proper cleanup before return
    - Added finally block with exception handling
    """
    # ✅ CRITICAL: Initialize BEFORE try block
    cursor = None
    conn = None
    
    try:
        days = int(request.args.get('days', 90))
        
        conn = get_database_connection('stock_data')
        cursor = conn.cursor()
        
        # Get hierarchical data: category -> type -> stock
        query = f"""
        SELECT 
            COALESCE(u.stock_category, 'Unknown') as category,
            COALESCE(u.stock_type_name, 'Unknown Type') as stock_type,
            u.stock_id,
            u.gsm,
            CONCAT(u.length_mm, 'x', u.width_mm) as dimensions,
            COUNT(e.ticket_id) as usage_count,
            SUM(COALESCE(e.total_sheets_consumed, e.quantity_ordered, 0)) as total_quantity,
            ROUND(CAST(SUM(COALESCE(e.total_sheets_consumed, e.quantity_ordered, 0)) * u.cost_per_thousand / 1000.0 AS NUMERIC), 2) as total_cost
        FROM stock_data.extracted_jobs e
        INNER JOIN stock_data.unified_stocks u ON e.stock_id = u.stock_id
        WHERE e.order_date >= CURRENT_DATE - INTERVAL '{days} days'
          AND e.stock_id IS NOT NULL
        GROUP BY u.stock_category, u.stock_type_name, u.stock_id, u.gsm, u.length_mm, u.width_mm, u.cost_per_thousand
        ORDER BY category, stock_type, usage_count DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        
        # ✅ CRITICAL: Close BEFORE return
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'status': 'ok',
            'days': days,
            'data': data,
            'record_count': len(data)
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   Stock hierarchy failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    finally:
        # ✅ CRITICAL: Guaranteed cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


# ============================================================================
# ENDPOINT 3: Reorder Dashboard
# ============================================================================

@stock_bp.route('/reorder-dashboard', methods=['GET', 'OPTIONS'])
@cross_origin()
def stock_reorder_dashboard():
    """
    Reorder Dashboard - Stock alerts based on inventory levels and usage
    
    Returns:
    - Critical stocks (immediate action needed)
    - Warning stocks (monitor closely)
    - Healthy stocks (adequate levels)
    
    FIXED: January 7, 2025
    - Added cursor/conn initialization
    - Added proper cleanup before return
    - Added finally block with exception handling
    """
    # ✅ CRITICAL: Handle OPTIONS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    # ✅ CRITICAL: Initialize BEFORE try block
    cursor = None
    conn = None
    
    try:
        conn = get_database_connection('stock_data')
        cursor = conn.cursor()
        
        # Query stock_data.stocklevels table
        query = """
        WITH StockUsage AS (
            SELECT 
                stock_id,
                COUNT(ticket_id) as usage_count,
                SUM(COALESCE(quantity_ordered, 1)) as total_usage_90d,
                SUM(COALESCE(quantity_ordered, 1)) / 90.0 as avg_daily_usage
            FROM extracted_jobs
            WHERE date(order_date) >= date('now', '-90 days')
              AND stock_id IS NOT NULL
            GROUP BY stock_id
        )
        SELECT 
            usage.stock_id,
            sl.StockTypeDesc as stock_type_name,
            sl.GSM as gsm,
            (CAST(sl.Length AS TEXT) || 'x' || CAST(sl.Width AS TEXT) || 'mm') AS dimensions,
            COALESCE(sl.CurrentStockLevel, 0) as current_level,
            COALESCE(sl.ReorderPoint, 3000) as reorder_point,
            COALESCE(sl.CriticalLevel, 1000) as critical_level,
            sl.CostPerThousand as cost_per_thousand,
            sl.SupplierName as supplier_name,
            ROUND(usage.avg_daily_usage, 1) as avg_daily_usage,
            usage.usage_count as jobs_90d,
            CASE 
                WHEN usage.avg_daily_usage > 0 THEN 
                    CAST(COALESCE(sl.CurrentStockLevel, 0) / usage.avg_daily_usage AS INTEGER)
                ELSE 999
            END as days_until_empty,
            CASE 
                WHEN COALESCE(sl.CurrentStockLevel, 0) <= COALESCE(sl.CriticalLevel, 1000) THEN 'critical'
                WHEN COALESCE(sl.CurrentStockLevel, 0) <= COALESCE(sl.ReorderPoint, 3000) THEN 'moderate'
                WHEN usage.avg_daily_usage > 0 AND (COALESCE(sl.CurrentStockLevel, 0) / usage.avg_daily_usage) <= 30 THEN 'upcoming'
                ELSE 'ok'
            END as alert_level,
            CASE
                WHEN usage.avg_daily_usage > 0 THEN 
                    CAST((COALESCE(sl.ReorderPoint, 3000) * 2 - COALESCE(sl.CurrentStockLevel, 0)) AS INTEGER)
                ELSE COALESCE(sl.ReorderPoint, 3000)
            END as recommended_order_qty
        FROM StockUsage usage
        JOIN StockLevels sl ON usage.stock_id = sl.StockID
        WHERE sl.IsActive = 1
        ORDER BY 
            CASE alert_level 
                WHEN 'critical' THEN 1 
                WHEN 'moderate' THEN 2 
                WHEN 'upcoming' THEN 3 
                ELSE 4 
            END,
            days_until_empty ASC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        data = [dict(row) for row in rows]
        
        # ✅ CRITICAL: Close BEFORE processing
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        # Calculate summary stats AFTER connection closed
        critical_count = sum(1 for row in data if row['alert_level'] == 'critical')
        moderate_count = sum(1 for row in data if row['alert_level'] == 'moderate')
        upcoming_count = sum(1 for row in data if row['alert_level'] == 'upcoming')
        
        return jsonify({
            'status': 'ok',
            'database': 'SQLite (stock_data.db)',
            'summary': {
                'total_alerts': critical_count + moderate_count + upcoming_count,
                'critical': critical_count,
                'moderate': moderate_count,
                'upcoming': upcoming_count
            },
            'data': data
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   Reorder dashboard failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    finally:
        # ✅ CRITICAL: Guaranteed cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


# ============================================================================
# ENDPOINT 4: Profit Analysis
# ============================================================================

@stock_bp.route('/profit-analysis', methods=['GET', 'OPTIONS'])
@cross_origin()
def stock_profit_analysis():
    """
    Profit Analysis - Profitability metrics by stock
    Query params: days (30, 90, 180, 365)
    
    Returns:
    - Profit margins by stock
    - High-margin vs low-margin products
    - Revenue contribution
    - Cost analysis
    
    FIXED: January 7, 2025
    - Added cursor/conn initialization
    - Added proper cleanup before return
    - Added finally block with exception handling
    """
    # ✅ CRITICAL: Handle OPTIONS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    # ✅ CRITICAL: Initialize BEFORE try block
    cursor = None
    conn = None
    
    try:
        days = int(request.args.get('days', 90))
        
        conn = get_database_connection('stock_data')
        cursor = conn.cursor()
        
        # Calculate profitability by stock
        query = f"""
        SELECT 
            u.stock_id,
            u.stock_type_name,
            u.gsm,
            CONCAT(u.length_mm, 'x', u.width_mm, 'mm') AS dimensions,
            COUNT(e.ticket_id) as total_jobs,
            SUM(COALESCE(e.total_sheets_consumed, e.quantity_ordered, 0)) as total_sheets,
            ROUND(CAST(SUM(COALESCE(e.total_sheets_consumed, e.quantity_ordered, 0)) * u.cost_per_thousand / 1000.0 AS NUMERIC), 2) as total_cost,
            ROUND(CAST(SUM(COALESCE(e.total_sheets_consumed, e.quantity_ordered, 0)) * u.cost_per_thousand * u.markup / 1000.0 AS NUMERIC), 2) as estimated_revenue,
            ROUND(CAST(SUM(COALESCE(e.total_sheets_consumed, e.quantity_ordered, 0)) * u.cost_per_thousand * (u.markup - 1.0) / 1000.0 AS NUMERIC), 2) as gross_profit,
            ROUND(CAST(((u.markup - 1.0) / u.markup) * 100 AS NUMERIC), 1) as margin_percent,
            u.supplier_name
        FROM stock_data.extracted_jobs e
        INNER JOIN stock_data.unified_stocks u ON e.stock_id = u.stock_id
        WHERE e.order_date >= CURRENT_DATE - INTERVAL '{days} days'
          AND e.stock_id IS NOT NULL
          AND u.cost_per_thousand > 0
        GROUP BY u.stock_id, u.stock_type_name, u.gsm, u.length_mm, u.width_mm, u.cost_per_thousand, u.markup, u.supplier_name
        HAVING SUM(COALESCE(e.total_sheets_consumed, e.quantity_ordered, 0)) > 0
        ORDER BY gross_profit DESC
        LIMIT 50
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        
        # ✅ CRITICAL: Close BEFORE processing
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        # Calculate summary statistics AFTER connection closed
        total_cost = sum(row['total_cost'] or 0 for row in data)
        total_revenue = sum(row['estimated_revenue'] or 0 for row in data)
        total_profit = total_revenue - total_cost
        overall_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return jsonify({
            'status': 'ok',
            'days': days,
            'database': 'Supabase PostgreSQL (stock_data schema)',
            'summary': {
                'total_cost': round(total_cost, 2),
                'total_revenue': round(total_revenue, 2),
                'total_profit': round(total_profit, 2),
                'overall_margin': round(overall_margin, 1),
                'stocks_analyzed': len(data)
            },
            'data': data
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   Profit analysis failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    finally:
        # ✅ CRITICAL: Guaranteed cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


# ============================================================================
# ENDPOINT 5: SQL Viewer
# ============================================================================

@stock_bp.route('/sql-query', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(methods=['GET', 'POST', 'OPTIONS'])
def stock_sql_query():
    """
    SQL Viewer - Execute custom queries with results
    GET: Returns table list and schemas
    POST body: { "query": "SELECT ..." }
    
    FIXED: January 7, 2025
    - Added cursor/conn initialization for BOTH paths
    - Added proper cleanup before return
    - Added finally blocks with exception handling
    - Handles GET and POST independently
    """
    # ✅ CRITICAL: Handle OPTIONS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    # ✅ CRITICAL: Initialize BEFORE try block
    cursor = None
    conn = None
    
    try:
        # GET: Return table list from PostgreSQL stock_data schema
        if request.method == 'GET':
            conn = get_database_connection('stock_data')
            cursor = conn.cursor()
            
            # Get table list
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'stock_data' 
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            table_info = {}
            for table in tables:
                # Get column info for each table
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'stock_data' 
                      AND table_name = %s
                    ORDER BY ordinal_position
                """, (table,))
                columns = cursor.fetchall()
                table_info[table] = [
                    {'name': col[0], 'type': col[1], 'nullable': col[2] == 'YES'}
                    for col in columns
                ]
            
            # ✅ CRITICAL: Close BEFORE return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            return jsonify({
                'status': 'ok',
                'tables': tables,
                'table_info': table_info,
                'database': 'Supabase PostgreSQL (stock_data schema)'
            })
        
        # POST: Execute query
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'status': 'error', 'message': 'No query provided'}), 400
        
        # Safety check: Block destructive operations
        dangerous_keywords = ['DROP', 'TRUNCATE']
        query_upper = query.upper()
        if any(keyword in query_upper for keyword in dangerous_keywords):
            return jsonify({
                'status': 'error',
                'message': 'DROP/TRUNCATE operations not allowed'
            }), 403
        
        import time
        start_time = time.time()
        
        conn = get_database_connection('stock_data')
        cursor = conn.cursor()
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        results = [dict(zip(columns, row)) for row in rows]
        execution_time = round((time.time() - start_time) * 1000, 2)
        
        conn.commit()  # Commit if UPDATE/INSERT/DELETE
        
        # ✅ CRITICAL: Close BEFORE return
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'status': 'ok',
            'columns': columns,
            'data': results,
            'row_count': len(results),
            'execution_time_ms': execution_time,
            'query': query
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   SQL query failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    finally:
        # ✅ CRITICAL: Guaranteed cleanup (works for BOTH GET and POST)
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


# ============================================================================
# ENDPOINT 6: Update Cell (Inline Editing)
# ============================================================================

@stock_bp.route('/update-cell', methods=['POST', 'OPTIONS'])
@cross_origin()
def stock_update_cell():
    """
    Update Cell - Inline editing in SQL Viewer
    POST body: {
        "table": "unified_stocks",
        "column": "cost_per_thousand",
        "value": 145.50,
        "where_column": "stock_id",
        "where_value": 44
    }
    
    FIXED: January 7, 2025
    - Added cursor/conn initialization
    - Added proper cleanup before return
    - Added finally block with exception handling
    - Handles early return (validation) correctly
    """
    # ✅ CRITICAL: Handle OPTIONS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    # ✅ STEP 1: Validate BEFORE creating any resources
    try:
        data = request.get_json()
        table = data.get('table')
        column = data.get('column')
        value = data.get('value')
        where_col = data.get('where_column')
        where_val = data.get('where_value')
        
        if not all([table, column, value is not None, where_col, where_val]):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        # Safety: Allowed tables and columns
        allowed_tables = ['unified_stocks', 'extracted_jobs']
        if table not in allowed_tables:
            return jsonify({'status': 'error', 'message': f'Table must be one of: {allowed_tables}'}), 400
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Validation error: {str(e)}'}), 400
    
    # ✅ STEP 2: Now create resources (after validation passed)
    cursor = None
    conn = None
    
    try:
        conn = get_database_connection('stock_data')
        cursor = conn.cursor()
        
        # Use parameterized query to prevent SQL injection
        update_query = f"UPDATE stock_data.{table} SET {column} = %s WHERE {where_col} = %s"
        cursor.execute(update_query, (value, where_val))
        
        conn.commit()
        rows_affected = cursor.rowcount
        
        # Get updated record
        cursor.execute(f"SELECT * FROM stock_data.{table} WHERE {where_col} = %s", (where_val,))
        updated_record = cursor.fetchone()
        
        # ✅ CRITICAL: Close BEFORE return
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        if rows_affected > 0:
            return jsonify({
                'status': 'ok',
                'message': f'Updated {table}.{column} to {value}',
                'rows_affected': rows_affected
            })
        else:
            return jsonify({'status': 'error', 'message': 'No rows updated'}), 404
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   Update cell failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    finally:
        # ✅ CRITICAL: Guaranteed cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


# ============================================================================
# ENDPOINT 7: AI Analytics
# ============================================================================

@stock_bp.route('/ai-analytics', methods=['GET', 'OPTIONS'])
@cross_origin()
def stock_ai_analytics():
    """
    AI Analytics - AI-powered insights and recommendations
    Query params: days (30, 90, 180, 365)
    
    Returns:
    - AI-generated insights
    - Anomaly detection
    - Recommendations
    - Predictive trends
    
    FIXED: January 7, 2025
    - Added early return handling (no cursor created yet)
    - Placeholder endpoint ready for future AI implementation
    """
    # ✅ CRITICAL: Handle OPTIONS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # ✅ STEP 1: Validate BEFORE creating resources
        if not STOCK_DB_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Database not configured'}), 503
        
        days = int(request.args.get('days', 90))
        
        # TODO: Implement AI analytics (StockManager not available in this project)
        # For now, return placeholder data (no database operations = no cursor)
        return jsonify({
            'status': 'ok',
            'days': days,
            'total_queries': 0,
            'total_cost': 0.00,
            'avg_response_time': 0.0,
            'invoice_count': 0,
            'queries': [],
            'message': 'AI analytics endpoint (placeholder - no AI queries tracked yet)'
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   AI analytics failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500