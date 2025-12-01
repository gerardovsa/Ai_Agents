"""
Shopify E-Commerce API Routes - Shopify Dashboard Module
========================================================================
from shared.database_utils import convert_sql_placeholders

This module provides Flask API endpoints for the Shopify E-Commerce module.
Uses SQLite database (stock_data.db) with Shopify webhook data.

Database Tables:
- shopify_orders: Order header information
- shopify_line_items: Line items for each order
- shopify_line_properties: DPO calculator property mappings
- shopify_webhook_events: Webhook event log
- shopify_product_mapping: Storefront to unified_stocks mapping

Architecture:
- Frontend (shopify.js) → Flask endpoints → SQLite stock_data.db

Endpoints:
- /api/shopify/dashboard/metrics - Dashboard KPIs
- /api/shopify/dashboard/orders - Orders list with filters
- /api/shopify/dashboard/charts/* - Chart data
- /api/shopify/dashboard/customers/* - Customer analytics
- /api/shopify/dashboard/products/* - Product performance
- /api/shopify/dashboard/webhooks/* - Webhook monitoring
- /api/shopify/sql-query - SQL viewer interface

Created: November 6, 2025
"""

import sys
import os
import traceback
import sqlite3
import time
from datetime import datetime, timedelta
from flask import jsonify, request
from flask_cors import cross_origin
from pathlib import Path

# SQLite database path - Same database as Stock Management
STOCK_DB_PATH = str(Path(__file__).parent.parent.parent.parent.parent / 'data' / 'stock_data.db')

# Will be set by flask_app.py
SHOPIFY_DB_CONFIG = None
SHOPIFY_DB_AVAILABLE = False


def init_shopify_routes(app, config_path, db_available):
    """
    Initialize Shopify routes with configuration
    
    Args:
        app: Flask app instance
        config_path: Path to database-config.json
        db_available: Boolean indicating if DB is configured
    """
    global SHOPIFY_DB_CONFIG, SHOPIFY_DB_AVAILABLE
    SHOPIFY_DB_CONFIG = config_path
    SHOPIFY_DB_AVAILABLE = db_available
    
    print(f"   Registering shopify endpoints...")
    
    # Dashboard endpoints
    try:
        app.add_url_rule('/api/shopify/dashboard/metrics', 'shopify_metrics', shopify_metrics, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/shopify/dashboard/metrics")
    except Exception as e:
        print(f"     ✗ /api/shopify/dashboard/metrics - {e}")
    
    try:
        app.add_url_rule('/api/shopify/dashboard/orders', 'shopify_orders', shopify_orders, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/shopify/dashboard/orders")
    except Exception as e:
        print(f"     ✗ /api/shopify/dashboard/orders - {e}")
    
    try:
        app.add_url_rule('/api/shopify/dashboard/charts/orders-over-time', 'shopify_orders_chart', shopify_orders_chart, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/shopify/dashboard/charts/orders-over-time")
    except Exception as e:
        print(f"     ✗ /api/shopify/dashboard/charts/orders-over-time - {e}")
    
    try:
        app.add_url_rule('/api/shopify/dashboard/charts/revenue-by-product', 'shopify_revenue_chart', shopify_revenue_chart, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/shopify/dashboard/charts/revenue-by-product")
    except Exception as e:
        print(f"     ✗ /api/shopify/dashboard/charts/revenue-by-product - {e}")
    
    try:
        app.add_url_rule('/api/shopify/dashboard/customers/segments', 'shopify_customer_segments', shopify_customer_segments, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/shopify/dashboard/customers/segments")
    except Exception as e:
        print(f"     ✗ /api/shopify/dashboard/customers/segments - {e}")
    
    try:
        app.add_url_rule('/api/shopify/dashboard/customers/top', 'shopify_top_customers', shopify_top_customers, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/shopify/dashboard/customers/top")
    except Exception as e:
        print(f"     ✗ /api/shopify/dashboard/customers/top - {e}")
    
    try:
        app.add_url_rule('/api/shopify/dashboard/products/top-sellers', 'shopify_top_products', shopify_top_products, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/shopify/dashboard/products/top-sellers")
    except Exception as e:
        print(f"     ✗ /api/shopify/dashboard/products/top-sellers - {e}")
    
    try:
        app.add_url_rule('/api/shopify/dashboard/products/catalog', 'shopify_product_catalog', shopify_product_catalog, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/shopify/dashboard/products/catalog")
    except Exception as e:
        print(f"     ✗ /api/shopify/dashboard/products/catalog - {e}")
    
    try:
        app.add_url_rule('/api/shopify/dashboard/webhooks/log', 'shopify_webhook_log', shopify_webhook_log, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/shopify/dashboard/webhooks/log")
    except Exception as e:
        print(f"     ✗ /api/shopify/dashboard/webhooks/log - {e}")
    
    try:
        app.add_url_rule('/api/shopify/dashboard/webhooks/health', 'shopify_webhook_health', shopify_webhook_health, methods=['GET', 'OPTIONS'])
        print(f"     ✓ /api/shopify/dashboard/webhooks/health")
    except Exception as e:
        print(f"     ✗ /api/shopify/dashboard/webhooks/health - {e}")
    
    try:
        app.add_url_rule('/api/shopify/sql-query', 'shopify_sql_query', shopify_sql_query, methods=['GET', 'POST', 'OPTIONS'])
        print(f"     ✓ /api/shopify/sql-query (GET+POST)")
    except Exception as e:
        print(f"     ✗ /api/shopify/sql-query - {e}")
    
    print(f"   Shopify E-Commerce routes initialized (DB: {db_available})")
    print(f"   ✅ 11 shopify endpoints registered")


def calculate_date_range(days):
    """Calculate date range for queries"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=int(days))
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')


# ============================================================================
# ENDPOINT 1: Dashboard Metrics
# ============================================================================

@cross_origin()
def shopify_metrics():
    """
    Dashboard KPIs - total orders, revenue, AOV, orders today
    Query params: period (today|week|month|all)
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        if not os.path.exists(STOCK_DB_PATH):
            return jsonify({
                'status': 'error',
                'message': f'Database not found: {STOCK_DB_PATH}'
            }), 503
        
        period = request.args.get('period', 'month')
        period_days = {
            'today': 1,
            'week': 7,
            'month': 30,
            'all': 9999
        }
        days = period_days.get(period, 30)
        start_date, end_date = calculate_date_range(days)
        
        conn = sqlite3.connect(STOCK_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if shopify_orders table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shopify_orders'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'total_orders': 0,
                'total_revenue': 0,
                'avg_order_value': 0,
                'orders_today': 0,
                'period': period,
                'message': 'No Shopify data yet (table does not exist)'
            })
        
        # Get metrics
        sql, params = convert_sql_placeholders("""
            SELECT 
                COUNT(*) as total_orders,
                SUM(COALESCE(total_price, 0)) as total_revenue,
                AVG(COALESCE(total_price, 0)) as avg_order_value
            FROM shopify_orders
            WHERE DATE(created_at) BETWEEN ? AND ?
        """, (start_date, end_date))

        cursor.execute(sql, params)
        
        metrics = cursor.fetchone()
        
        # Orders today
        today = datetime.now().strftime('%Y-%m-%d')
        sql, params = convert_sql_placeholders("""
            SELECT COUNT(*) as orders_today
            FROM shopify_orders
            WHERE DATE(created_at) = ?
        """, (today,))

        cursor.execute(sql, params)
        
        today_data = cursor.fetchone()
        conn.close()
        
        return jsonify({
            'total_orders': metrics['total_orders'] or 0,
            'total_revenue': round(metrics['total_revenue'] or 0, 2),
            'avg_order_value': round(metrics['avg_order_value'] or 0, 2),
            'orders_today': today_data['orders_today'] or 0,
            'period': period
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   Shopify metrics failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# ENDPOINT 2: Orders List
# ============================================================================

@cross_origin()
def shopify_orders():
    """
    Orders list with filters
    Query params: days, status, min_value
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        days = int(request.args.get('days', 30))
        status_filter = request.args.get('status', '')
        min_value = float(request.args.get('min_value', 0))
        
        start_date, end_date = calculate_date_range(days)
        
        conn = sqlite3.connect(STOCK_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shopify_orders'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'orders': [],
                'count': 0,
                'message': 'No Shopify orders yet'
            })
        
        query = """
            SELECT 
                shopify_order_id as order_id,
                order_number,
                created_at,
                customer_name,
                email as customer_email,
                total_price,
                financial_status,
                fulfillment_status
            FROM shopify_orders
            WHERE DATE(created_at) BETWEEN ? AND ?
              AND COALESCE(total_price, 0) >= ?
        """
        
        params = [start_date, end_date, min_value]
        
        if status_filter:
            query += " AND financial_status = ?"
            params.append(status_filter)
        
        query += " ORDER BY created_at DESC LIMIT 200"
        
        cursor.execute(query, params)
        orders = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'orders': orders,
            'count': len(orders),
            'filters': {
                'days': days,
                'status': status_filter,
                'min_value': min_value
            }
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   Shopify orders failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# ENDPOINT 3: Orders Over Time Chart
# ============================================================================

@cross_origin()
def shopify_orders_chart():
    """Daily order counts for line chart"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        days = int(request.args.get('days', 30))
        start_date, end_date = calculate_date_range(days)
        
        conn = sqlite3.connect(STOCK_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shopify_orders'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'labels': [],
                'data': []
            })
        
        sql, params = convert_sql_placeholders("""
            SELECT 
                DATE(created_at) as order_date,
                COUNT(*) as order_count
            FROM shopify_orders
            WHERE DATE(created_at) BETWEEN ? AND ?
            GROUP BY DATE(created_at)
            ORDER BY order_date ASC
        """, (start_date, end_date))

        
        cursor.execute(sql, params)
        
        results = cursor.fetchall()
        conn.close()
        
        labels = [row['order_date'] for row in results]
        data = [row['order_count'] for row in results]
        
        return jsonify({
            'labels': labels,
            'data': data
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   Orders chart failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# ENDPOINT 4: Revenue by Product Chart
# ============================================================================

@cross_origin()
def shopify_revenue_chart():
    """Revenue breakdown by product"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        days = int(request.args.get('days', 30))
        start_date, end_date = calculate_date_range(days)
        
        conn = sqlite3.connect(STOCK_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shopify_line_items'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'labels': [],
                'data': []
            })
        
        sql, params = convert_sql_placeholders("""
            SELECT 
                li.title,
                SUM(li.price * li.quantity) as total_revenue
            FROM shopify_line_items li
            INNER JOIN shopify_orders o ON li.shopify_order_id = o.shopify_order_id
            WHERE DATE(o.created_at) BETWEEN ? AND ?
            GROUP BY li.title
            ORDER BY total_revenue DESC
            LIMIT 10
        """, (start_date, end_date))

        
        cursor.execute(sql, params)
        
        results = cursor.fetchall()
        conn.close()
        
        labels = [row['title'] for row in results]
        data = [row['total_revenue'] or 0 for row in results]
        
        return jsonify({
            'labels': labels,
            'data': data
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   Revenue chart failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# ENDPOINT 5: Customer Segments
# ============================================================================

@cross_origin()
def shopify_customer_segments():
    """Customer segmentation by order count"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        days = int(request.args.get('days', 90))
        start_date, end_date = calculate_date_range(days)
        
        conn = sqlite3.connect(STOCK_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shopify_orders'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'segments': []
            })
        
        sql, params = convert_sql_placeholders("""
            WITH CustomerOrders AS (
                SELECT 
                    email,
                    COUNT(*) as order_count
                FROM shopify_orders
                WHERE DATE(created_at) BETWEEN ? AND ?
                  AND email IS NOT NULL
                GROUP BY email
            )
            SELECT 
                CASE 
                    WHEN order_count >= 5 THEN 'VIP (5+ orders)'
                    WHEN order_count >= 3 THEN 'Regular (3-4 orders)'
                    WHEN order_count = 2 THEN 'Repeat (2 orders)'
                    ELSE 'New (1 order)'
                END as segment,
                COUNT(*) as count
            FROM CustomerOrders
            GROUP BY segment
        """, (start_date, end_date))

        
        cursor.execute(sql, params)
        
        segments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'segments': segments
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   Customer segments failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# ENDPOINT 6: Top Customers
# ============================================================================

@cross_origin()
def shopify_top_customers():
    """Top customers by total spent"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        days = int(request.args.get('days', 90))
        start_date, end_date = calculate_date_range(days)
        
        conn = sqlite3.connect(STOCK_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shopify_orders'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'customers': []
            })
        
        sql, params = convert_sql_placeholders("""
            SELECT 
                customer_name,
                email,
                COUNT(*) as order_count,
                SUM(COALESCE(total_price, 0)) as total_spent,
                AVG(COALESCE(total_price, 0)) as avg_order_value
            FROM shopify_orders
            WHERE DATE(created_at) BETWEEN ? AND ?
              AND email IS NOT NULL
            GROUP BY customer_name, email
            ORDER BY total_spent DESC
            LIMIT 20
        """, (start_date, end_date))

        
        cursor.execute(sql, params)
        
        customers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'customers': customers
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   Top customers failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# ENDPOINT 7: Top Selling Products
# ============================================================================

@cross_origin()
def shopify_top_products():
    """Top selling products by quantity"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        days = int(request.args.get('days', 30))
        start_date, end_date = calculate_date_range(days)
        
        conn = sqlite3.connect(STOCK_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shopify_line_items'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'products': []
            })
        
        sql, params = convert_sql_placeholders("""
            SELECT 
                li.title,
                li.variant_title,
                SUM(li.quantity) as total_quantity,
                SUM(li.price * li.quantity) as total_revenue
            FROM shopify_line_items li
            INNER JOIN shopify_orders o ON li.shopify_order_id = o.shopify_order_id
            WHERE DATE(o.created_at) BETWEEN ? AND ?
            GROUP BY li.title, li.variant_title
            ORDER BY total_quantity DESC
            LIMIT 15
        """, (start_date, end_date))

        
        cursor.execute(sql, params)
        
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'products': products
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   Top products failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# ENDPOINT 8: Product Catalog
# ============================================================================

@cross_origin()
def shopify_product_catalog():
    """Product catalog with sales data"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        limit = int(request.args.get('limit', 50))
        
        conn = sqlite3.connect(STOCK_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shopify_line_items'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'products': []
            })
        
        sql, params = convert_sql_placeholders("""
            SELECT 
                product_id,
                variant_id,
                title,
                variant_title,
                sku,
                SUM(quantity) as total_quantity
            FROM shopify_line_items
            WHERE product_id IS NOT NULL
            GROUP BY product_id, variant_id, title, variant_title, sku
            ORDER BY total_quantity DESC
            LIMIT ?
        """, (limit,))

        
        cursor.execute(sql, params)
        
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'products': products
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   Product catalog failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# ENDPOINT 9: Webhook Event Log
# ============================================================================

@cross_origin()
def shopify_webhook_log():
    """Recent webhook events"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        limit = int(request.args.get('limit', 50))
        
        conn = sqlite3.connect(STOCK_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shopify_webhook_events'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'events': []
            })
        
        sql, params = convert_sql_placeholders("""
            SELECT 
                id,
                topic,
                shopify_id,
                received_at,
                processed,
                processed_at,
                error
            FROM shopify_webhook_events
            ORDER BY received_at DESC
            LIMIT ?
        """, (limit,))

        
        cursor.execute(sql, params)
        
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'events': events
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   Webhook log failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# ENDPOINT 10: Webhook Health Stats
# ============================================================================

@cross_origin()
def shopify_webhook_health():
    """Webhook health statistics"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        conn = sqlite3.connect(STOCK_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shopify_webhook_events'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'stats': {
                    'total': 0,
                    'processed': 0,
                    'pending': 0,
                    'errors': 0
                }
            })
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN processed = 1 THEN 1 ELSE 0 END) as processed,
                SUM(CASE WHEN processed = 0 AND error IS NULL THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END) as errors
            FROM shopify_webhook_events
        """)
        
        stats = dict(cursor.fetchone())
        conn.close()
        
        return jsonify({
            'stats': stats
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   Webhook health failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# ENDPOINT 11: SQL Query Interface
# ============================================================================

@cross_origin(methods=['GET', 'POST', 'OPTIONS'])
def shopify_sql_query():
    """
    SQL Viewer - Execute custom queries
    GET: Returns Shopify table list
    POST: Executes query
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # GET: Return Shopify table list
        if request.method == 'GET':
            conn = sqlite3.connect(STOCK_DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                  AND name LIKE 'shopify_%'
                ORDER BY name
            """)
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
        
        # Safety check
        dangerous_keywords = ['DROP', 'TRUNCATE']
        query_upper = query.upper()
        if any(keyword in query_upper for keyword in dangerous_keywords):
            return jsonify({
                'status': 'error',
                'message': 'DROP/TRUNCATE operations not allowed'
            }), 403
        
        start_time = time.time()
        
        conn = sqlite3.connect(STOCK_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        results = [dict(row) for row in rows]
        execution_time = f"{round((time.time() - start_time) * 1000, 2)}ms"
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'columns': columns,
            'results': results,
            'row_count': len(results),
            'execution_time': execution_time,
            'query': query
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"   SQL query failed: {error_details}")
        return jsonify({'status': 'error', 'error': str(e)}), 500
