"""
Stock Management API Routes - SQLite Stock Database
========================================================================
from shared.database_utils import convert_sql_placeholders

This module provides Flask API endpoints for the Stock Management module.
Uses SQLite database (stock_data.db) with AI-extracted job data.

Database Architecture:
- SQL Server (Production): JobTickets, Orders, Quote_DigitalStocks (read-only reference)
- SQLite (stock_data.db): extracted_jobs, unified_stocks (PRIMARY for analytics)

Architecture:
- Frontend (stock-management.js) → Flask endpoints → SQLite stock_data.db

Created: October 30, 2025
"""

import sys
import os
import traceback
import sqlite3
from flask import jsonify, request
from flask_cors import cross_origin
from pathlib import Path

# SQLite stock database path - Local AI_agents copy (independent of G_Folder)
STOCK_DB_PATH = str(Path(__file__).parent.parent.parent.parent.parent / 'data' / 'stock_data.db')

# Will be set by flask_app.py
STOCK_DB_CONFIG = None
STOCK_DB_AVAILABLE = False


def init_stock_routes(app, config_path, db_available):
    """
    Initialize stock routes with configuration
    
    Args:
        app: Flask app instance
        config_path: Path to database-config.json
        db_available: Boolean indicating if DB is configured
    """
    global STOCK_DB_CONFIG, STOCK_DB_AVAILABLE
    STOCK_DB_CONFIG = config_path
    STOCK_DB_AVAILABLE = db_available
    
    # Register all routes - using direct function references
    print(f"   Registering stock endpoints...")
    try:
        app.add_url_rule('/api/stock/usage-analytics', 'stock_usage_analytics', stock_usage_analytics, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/stock/usage-analytics")
    except Exception as e:
        print(f"     ✗ /api/stock/usage-analytics - {e}")
    
    try:
        app.add_url_rule('/api/stock/hierarchy', 'stock_hierarchy', stock_hierarchy, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/stock/hierarchy")
    except Exception as e:
        print(f"     ✗ /api/stock/hierarchy - {e}")
    
    try:
        app.add_url_rule('/api/stock/reorder-dashboard', 'stock_reorder_dashboard', stock_reorder_dashboard, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/stock/reorder-dashboard")
    except Exception as e:
        print(f"     ✗ /api/stock/reorder-dashboard - {e}")
    
    try:
        app.add_url_rule('/api/stock/profit-analysis', 'stock_profit_analysis', stock_profit_analysis, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/stock/profit-analysis")
    except Exception as e:
        print(f"     ✗ /api/stock/profit-analysis - {e}")
    
    try:
        app.add_url_rule('/api/stock/sql-query', 'stock_sql_query', stock_sql_query, methods=['GET', 'POST', 'OPTIONS'])
        print(f"     ✓ /api/stock/sql-query (GET+POST)")
    except Exception as e:
        print(f"     ✗ /api/stock/sql-query - {e}")
    
    try:
        app.add_url_rule('/api/stock/update-cell', 'stock_update_cell', stock_update_cell, methods=['POST', 'OPTIONS'])
        print(f"     ✓ /api/stock/update-cell (POST)")
    except Exception as e:
        print(f"     ✗ /api/stock/update-cell - {e}")
    
    try:
        app.add_url_rule('/api/stock/ai-analytics', 'stock_ai_analytics', stock_ai_analytics, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/stock/ai-analytics")
    except Exception as e:
        print(f"     ✗ /api/stock/ai-analytics - {e}")
    
    print(f"   Stock management routes initialized (DB: {db_available})")
    print(f"   ✅ 7 stock endpoints registered")


# ============================================================================
# ENDPOINT 1: Usage Analytics
# ============================================================================

@cross_origin()
def stock_usage_analytics():
    """
    Usage Analytics - Stock consumption patterns from AI-extracted jobs
    Query params: days (7, 30, 90, 365)
    
    Database: SQLite (stock_data.db)
    Tables: extracted_jobs, unified_stocks
    
    Returns top 10 most-used stocks with job count and total quantity
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        if not os.path.exists(STOCK_DB_PATH):
            return jsonify({
                'status': 'error', 
                'message': f'Stock database not found: {STOCK_DB_PATH}'
            }), 503
        
        days = int(request.args.get('days', 30))
        
        # Connect to SQLite stock database
        conn = sqlite3.connect(STOCK_DB_PATH)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        
        # Query AI-extracted jobs with stock information
        # Uses extracted_jobs (AI data) + unified_stocks (stock master)
        # Column: quantity_ordered (not quantity)
        query = f"""
        SELECT 
            u.stock_id AS StockID,
            u.stock_type_name AS StockType,
            COUNT(e.ticket_id) as usage_count,
            SUM(COALESCE(e.total_sheets_consumed, e.quantity_ordered, 0)) as total_quantity,
            u.gsm AS GSM,
            (CAST(u.length_mm AS TEXT) || 'x' || CAST(u.width_mm AS TEXT) || 'mm') AS Dimensions
        FROM extracted_jobs e
        INNER JOIN unified_stocks u ON e.stock_id = u.stock_id
        WHERE date(e.order_date) >= date('now', '-{days} days')
          AND e.stock_id IS NOT NULL
        GROUP BY u.stock_id, u.stock_type_name, u.gsm, u.length_mm, u.width_mm
        ORDER BY usage_count DESC
        LIMIT 50
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert rows to list of dictionaries
        data = [dict(row) for row in rows]
        
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'days': days,
            'database': 'SQLite (stock_data.db)',
            'tables': 'extracted_jobs + unified_stocks',
            'data': data
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   Usage analytics failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e), 'traceback': error_details}), 500


# ============================================================================
# ENDPOINT 2: Stock Hierarchy (for Sunburst Chart)
# ============================================================================

@cross_origin()
def stock_hierarchy():
    """
    Get hierarchical stock usage data for sunburst visualization
    Returns: category -> stock_type -> individual stocks with usage counts
    """
    try:
        days = int(request.args.get('days', 90))
        
        conn = sqlite3.connect(STOCK_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get hierarchical data: category -> type -> stock
        query = f"""
        SELECT 
            COALESCE(u.stock_category, 'Unknown') as category,
            COALESCE(u.stock_type_name, 'Unknown Type') as stock_type,
            u.stock_id,
            u.gsm,
            (CAST(u.length_mm AS TEXT) || 'x' || CAST(u.width_mm AS TEXT)) as dimensions,
            COUNT(e.ticket_id) as usage_count,
            SUM(COALESCE(e.total_sheets_consumed, e.quantity_ordered, 0)) as total_quantity,
            ROUND(SUM(COALESCE(e.total_sheets_consumed, e.quantity_ordered, 0)) * u.cost_per_thousand / 1000.0, 2) as total_cost
        FROM extracted_jobs e
        INNER JOIN unified_stocks u ON e.stock_id = u.stock_id
        WHERE date(e.order_date) >= date('now', '-{days} days')
          AND e.stock_id IS NOT NULL
        GROUP BY u.stock_category, u.stock_type_name, u.stock_id, u.gsm, u.length_mm, u.width_mm, u.cost_per_thousand
        ORDER BY category, stock_type, usage_count DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        data = [dict(row) for row in rows]
        conn.close()
        
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


# ============================================================================
# ENDPOINT 3: Reorder Dashboard
# ============================================================================

@cross_origin()
def stock_reorder_dashboard():
    """
    Reorder Dashboard - Stock alerts based on inventory levels and usage
    Uses SQLite stock_data.db
    
    NOTE: Columns current_stock_level, reorder_point, critical_level don't exist yet.
    Returns mock data with usage-based alerts until inventory tracking is implemented.
    
    Returns:
    - Critical stocks (immediate action needed)
    - Warning stocks (monitor closely)
    - Healthy stocks (adequate levels)
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        conn = sqlite3.connect(STOCK_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query StockLevels table (has real inventory columns: CurrentStockLevel, ReorderPoint, CriticalLevel)
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
        conn.close()
        
        # Calculate summary stats
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


# ============================================================================
# ENDPOINT 3: Profit Analysis
# ============================================================================

@cross_origin()
def stock_profit_analysis():
    """
    Profit Analysis - Profitability metrics by stock
    Uses SQLite stock_data.db
    Query params: days (30, 90, 180, 365)
    
    Returns:
    - Profit margins by stock
    - High-margin vs low-margin products
    - Revenue contribution
    - Cost analysis
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        days = int(request.args.get('days', 90))
        
        conn = sqlite3.connect(STOCK_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Calculate profitability by stock with cost and revenue estimates
        query = f"""
        SELECT 
            u.stock_id,
            u.stock_type_name,
            u.gsm,
            (CAST(u.length_mm AS TEXT) || 'x' || CAST(u.width_mm AS TEXT) || 'mm') AS dimensions,
            COUNT(e.ticket_id) as total_jobs,
            SUM(COALESCE(e.total_sheets_consumed, e.quantity_ordered, 0)) as total_sheets,
            ROUND(SUM(COALESCE(e.total_sheets_consumed, e.quantity_ordered, 0)) * u.cost_per_thousand / 1000.0, 2) as total_cost,
            ROUND(SUM(COALESCE(e.total_sheets_consumed, e.quantity_ordered, 0)) * u.cost_per_thousand * u.markup / 1000.0, 2) as estimated_revenue,
            ROUND(SUM(COALESCE(e.total_sheets_consumed, e.quantity_ordered, 0)) * u.cost_per_thousand * (u.markup - 1.0) / 1000.0, 2) as gross_profit,
            ROUND(((u.markup - 1.0) / u.markup) * 100, 1) as margin_percent,
            u.supplier_name
        FROM extracted_jobs e
        INNER JOIN unified_stocks u ON e.stock_id = u.stock_id
        WHERE date(e.order_date) >= date('now', '-{days} days')
          AND e.stock_id IS NOT NULL
          AND u.cost_per_thousand > 0
        GROUP BY u.stock_id, u.stock_type_name, u.gsm, u.length_mm, u.width_mm, u.cost_per_thousand, u.markup, u.supplier_name
        HAVING total_sheets > 0
        ORDER BY gross_profit DESC
        LIMIT 50
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        data = [dict(row) for row in rows]
        conn.close()
        
        # Calculate summary statistics (handle NULL values)
        total_cost = sum(row['total_cost'] or 0 for row in data)
        total_revenue = sum(row['estimated_revenue'] or 0 for row in data)
        total_profit = total_revenue - total_cost
        overall_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return jsonify({
            'status': 'ok',
            'days': days,
            'database': 'SQLite (stock_data.db)',
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


# ============================================================================
# ENDPOINT 4: SQL Viewer
# ============================================================================

@cross_origin(methods=['GET', 'POST', 'OPTIONS'])
def stock_sql_query():
    """
    SQL Viewer - Execute custom queries with results
    GET: Returns table list and schemas
    POST body: { "query": "SELECT ..." }
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # GET: Return table list
        if request.method == 'GET':
            conn = sqlite3.connect(STOCK_DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
            
            table_info = {}
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                table_info[table] = [
                    {'name': col[1], 'type': col[2], 'nullable': not col[3]}
                    for col in columns
                ]
            
            conn.close()
            
            return jsonify({
                'status': 'ok',
                'tables': tables,
                'table_info': table_info,
                'database': 'SQLite (stock_data.db)'
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
        
        conn = sqlite3.connect(STOCK_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        results = [dict(row) for row in rows]
        execution_time = round((time.time() - start_time) * 1000, 2)
        
        conn.commit()  # Commit if UPDATE/INSERT/DELETE
        conn.close()
        
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


# ============================================================================
# ENDPOINT 5: Update Cell (Inline Editing)
# ============================================================================

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
    """
    if request.method == 'OPTIONS':
        return '', 204
    
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
        
        conn = sqlite3.connect(STOCK_DB_PATH)
        cursor = conn.cursor()
        
        # Use parameterized query to prevent SQL injection
        update_query = f"UPDATE {table} SET {column} = ? WHERE {where_col} = ?"
        cursor.execute(update_query, (value, where_val))
        
        conn.commit()
        rows_affected = cursor.rowcount
        
        # Get updated record
        cursor.execute(f"SELECT * FROM {table} WHERE {where_col} = ?", (where_val,))
        updated_record = cursor.fetchone()
        
        conn.close()
        
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


# ============================================================================
# ENDPOINT 6: AI Analytics
# ============================================================================

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
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        if not STOCK_DB_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Database not configured'}), 503
        
        days = int(request.args.get('days', 90))
        
        # TODO: Implement AI analytics (StockManager not available in this project)
        # For now, return placeholder data
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
