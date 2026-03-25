"""
WooCommerce E-Commerce API Routes - WooCommerce Dashboard Module
========================================================================
REFACTORED: January 4, 2026

This module provides Flask API endpoints for the WooCommerce E-Commerce module.
Uses Supabase PostgreSQL for credential storage and WooCommerce REST API for data.

Architecture:
- Frontend (shopify.js) → Flask endpoints → WooCommerce REST API
- Credentials stored in ai_infrastructure.user_platform_credentials
- Platform-wide credentials (user_id=1) available to all users

Credentials Schema:
- platform: 'shopify' (legacy name, actually WooCommerce)
- credentials.consumer_key: WooCommerce API key
- credentials.consumer_secret: WooCommerce API secret  
- credentials.base_url: Store URL (https://inhouseprint.com.au)

Endpoints:
- /api/shopify/dashboard/metrics - Dashboard KPIs
- /api/shopify/dashboard/orders - Orders list with filters
- /api/shopify/dashboard/charts/* - Chart data
- /api/shopify/dashboard/customers/* - Customer analytics
- /api/shopify/dashboard/products/* - Product performance
- /api/shopify/dashboard/webhooks/* - Webhook monitoring (not implemented)

Created: November 6, 2025
Last Refactor: January 4, 2026 - Removed SQLite, added WooCommerce API
"""

import sys
import os
import traceback
from datetime import datetime, timedelta
from flask import jsonify, request, g
from flask_cors import cross_origin
from pathlib import Path

# Conditional WooCommerce import - makes module work without WooCommerce dependency
try:
    from woocommerce import API
    WOOCOMMERCE_AVAILABLE = True
except ImportError:
    WOOCOMMERCE_AVAILABLE = False
    API = None
    print("[SHOPIFY] ⚠️  WooCommerce module not installed - some features will be unavailable")
    print("[SHOPIFY] Install with: pip install WooCommerce")

# Add shared utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'AI_infrastructure' / 'shared'))
from database_utils import execute_query


def init_shopify_routes(app, config_path=None, db_available=True):
    """
    Initialize WooCommerce/Shopify routes
    
    Args:
        app: Flask app instance
        config_path: Unused (legacy parameter)
        db_available: Unused (legacy parameter)
    """
    
    if not WOOCOMMERCE_AVAILABLE:
        print(f"   ⚠️  WooCommerce/Shopify routes SKIPPED - woocommerce module not installed")
        return
    
    print(f"   Registering WooCommerce/Shopify endpoints...")
    
    # Dashboard endpoints
    app.add_url_rule('/api/shopify/dashboard/metrics', 'shopify_metrics', shopify_metrics, methods=['GET', 'OPTIONS'])
    print(f"     ✓ /api/shopify/dashboard/metrics")
    
    app.add_url_rule('/api/shopify/dashboard/orders', 'shopify_orders', shopify_orders, methods=['GET', 'OPTIONS'])
    print(f"     ✓ /api/shopify/dashboard/orders")
    
    app.add_url_rule('/api/shopify/dashboard/charts/orders-over-time', 'shopify_orders_chart', shopify_orders_chart, methods=['GET', 'OPTIONS'])
    print(f"     ✓ /api/shopify/dashboard/charts/orders-over-time")
    
    app.add_url_rule('/api/shopify/dashboard/charts/revenue-by-product', 'shopify_revenue_chart', shopify_revenue_chart, methods=['GET', 'OPTIONS'])
    print(f"     ✓ /api/shopify/dashboard/charts/revenue-by-product")
    
    app.add_url_rule('/api/shopify/dashboard/customers/top', 'shopify_top_customers', shopify_top_customers, methods=['GET', 'OPTIONS'])
    print(f"     ✓ /api/shopify/dashboard/customers/top")
    
    app.add_url_rule('/api/shopify/dashboard/customers/segments', 'shopify_customer_segments', shopify_customer_segments, methods=['GET', 'OPTIONS'])
    print(f"     ✓ /api/shopify/dashboard/customers/segments")
    
    app.add_url_rule('/api/shopify/dashboard/products/top-sellers', 'shopify_top_products', shopify_top_products, methods=['GET', 'OPTIONS'])
    print(f"     ✓ /api/shopify/dashboard/products/top-sellers")
    
    app.add_url_rule('/api/shopify/dashboard/products/catalog', 'shopify_product_catalog', shopify_product_catalog, methods=['GET', 'OPTIONS'])
    print(f"     ✓ /api/shopify/dashboard/products/catalog")
    
    app.add_url_rule('/api/shopify/dashboard/webhooks/log', 'shopify_webhook_log', shopify_webhook_log, methods=['GET', 'OPTIONS'])
    print(f"     ✓ /api/shopify/dashboard/webhooks/log")
    
    app.add_url_rule('/api/shopify/dashboard/webhooks/health', 'shopify_webhook_health', shopify_webhook_health, methods=['GET', 'OPTIONS'])
    print(f"     ✓ /api/shopify/dashboard/webhooks/health")
    
    print(f"   WooCommerce/Shopify routes initialized")
    print(f"   ✅ 10 woocommerce/shopify endpoints registered")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_woocommerce_credentials(user_id=None):
    """
    Get WooCommerce credentials from Supabase
    
    Args:
        user_id: User ID (defaults to 1 for platform-wide credentials)
        
    Returns:
        dict: credentials with consumer_key, consumer_secret, base_url
    """
    if user_id is None:
        # GAP-M4: resolve from request context so each org gets its own creds
        try:
            user_id = getattr(g, 'rls_user_id', None) or 1
        except RuntimeError:
            # Outside request context (e.g. tests / background jobs)
            user_id = 1
    
    try:
        # Fetch credentials from Supabase
        result = execute_query(
            """
            SELECT credentials 
            FROM ai_infrastructure.user_platform_credentials
            WHERE user_id = %s AND platform = 'shopify' AND is_active = TRUE
            LIMIT 1
            """,
            (user_id,),
            fetch_mode='one'
        )
        
        if not result or not result[0]:
            print(f"[WooCommerce] No credentials found for user_id={user_id}")
            return None
            
        credentials = result[0]
        
        # Validate required fields
        required_fields = ['consumer_key', 'consumer_secret', 'base_url']
        if not all(field in credentials for field in required_fields):
            print(f"[WooCommerce] Missing required credential fields: {credentials.keys()}")
            return None
            
        return credentials
        
    except Exception as e:
        print(f"[WooCommerce] Error fetching credentials: {e}")
        traceback.print_exc()
        return None


def get_woocommerce_api(user_id=None):
    """
    Get WooCommerce API client with credentials
    
    Args:
        user_id: User ID (defaults to 1 for platform-wide credentials)
        
    Returns:
        woocommerce.API: Configured API client or None
    """
    credentials = get_woocommerce_credentials(user_id)
    
    if not credentials:
        return None
    
    try:
        wcapi = API(
            url=credentials['base_url'],
            consumer_key=credentials['consumer_key'],
            consumer_secret=credentials['consumer_secret'],
            version="wc/v3",
            timeout=30
        )
        return wcapi
    except Exception as e:
        print(f"[WooCommerce] Error creating API client: {e}")
        return None


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
        wcapi = get_woocommerce_api()
        if not wcapi:
            return jsonify({
                'status': 'error',
                'message': 'WooCommerce credentials not configured'
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
        
        # Fetch orders from WooCommerce API
        params = {
            'after': f"{start_date}T00:00:00",
            'before': f"{end_date}T23:59:59",
            'per_page': 100
        }
        
        response = wcapi.get("orders", params=params)
        
        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': f'WooCommerce API error: {response.status_code}'
            }), response.status_code
        
        orders = response.json()
        
        # Calculate metrics
        total_orders = len(orders)
        total_revenue = sum(float(order.get('total', 0)) for order in orders)
        aov = total_revenue / total_orders if total_orders > 0 else 0
        
        # Orders today
        today = datetime.now().date()
        orders_today = sum(1 for order in orders 
                          if datetime.fromisoformat(order['date_created'].replace('Z', '+00:00')).date() == today)
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_orders': total_orders,
                'total_revenue': round(total_revenue, 2),
                'average_order_value': round(aov, 2),
                'orders_today': orders_today
            }
        })
        
    except Exception as e:
        print(f"[WooCommerce] Error in shopify_metrics: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================================
# ENDPOINT 2: Orders List
# ============================================================================

@cross_origin()
def shopify_orders():
    """
    Get orders list with filters
    Query params: days, status, min_value
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        wcapi = get_woocommerce_api()
        if not wcapi:
            return jsonify({
                'status': 'error',
                'message': 'WooCommerce credentials not configured'
            }), 503
        
        days = int(request.args.get('days', 30))
        status = request.args.get('status', '')
        min_value = float(request.args.get('min_value', 0))
        
        start_date, end_date = calculate_date_range(days)
        
        # Fetch orders from WooCommerce API
        params = {
            'after': f"{start_date}T00:00:00",
            'before': f"{end_date}T23:59:59",
            'per_page': 100
        }
        
        if status:
            params['status'] = status
        
        response = wcapi.get("orders", params=params)
        
        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': f'WooCommerce API error: {response.status_code}'
            }), response.status_code
        
        orders = response.json()
        
        # Filter by min_value
        if min_value > 0:
            orders = [order for order in orders if float(order.get('total', 0)) >= min_value]
        
        # Format orders for frontend
        formatted_orders = []
        for order in orders:
            formatted_orders.append({
                'order_id': order['id'],
                'order_number': order['number'],
                'date': order['date_created'],
                'customer_name': f"{order.get('billing', {}).get('first_name', '')} {order.get('billing', {}).get('last_name', '')}".strip(),
                'total': float(order.get('total', 0)),
                'status': order.get('status', ''),
                'payment_method': order.get('payment_method_title', ''),
                'items_count': len(order.get('line_items', []))
            })
        
        return jsonify({
            'status': 'success',
            'data': formatted_orders
        })
        
    except Exception as e:
        print(f"[WooCommerce] Error in shopify_orders: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================================
# ENDPOINT 3: Orders Over Time Chart
# ============================================================================

@cross_origin()
def shopify_orders_chart():
    """
    Get orders over time for charting
    Query params: days
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        wcapi = get_woocommerce_api()
        if not wcapi:
            return jsonify({
                'status': 'error',
                'message': 'WooCommerce credentials not configured'
            }), 503
        
        days = int(request.args.get('days', 30))
        start_date, end_date = calculate_date_range(days)
        
        # Fetch orders
        params = {
            'after': f"{start_date}T00:00:00",
            'before': f"{end_date}T23:59:59",
            'per_page': 100
        }
        
        response = wcapi.get("orders", params=params)
        
        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': f'WooCommerce API error: {response.status_code}'
            }), response.status_code
        
        orders = response.json()
        
        # Group by date
        orders_by_date = {}
        for order in orders:
            date = order['date_created'][:10]  # YYYY-MM-DD
            orders_by_date[date] = orders_by_date.get(date, 0) + 1
        
        # Format for chart
        chart_data = {
            'dates': sorted(orders_by_date.keys()),
            'counts': [orders_by_date[date] for date in sorted(orders_by_date.keys())]
        }
        
        return jsonify({
            'status': 'success',
            'data': chart_data
        })
        
    except Exception as e:
        print(f"[WooCommerce] Error in shopify_orders_chart: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================================
# ENDPOINT 4: Revenue by Product Chart
# ============================================================================

@cross_origin()
def shopify_revenue_chart():
    """
    Get revenue by product for charting
    Query params: days
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        wcapi = get_woocommerce_api()
        if not wcapi:
            return jsonify({
                'status': 'error',
                'message': 'WooCommerce credentials not configured'
            }), 503
        
        days = int(request.args.get('days', 30))
        start_date, end_date = calculate_date_range(days)
        
        # Fetch orders
        params = {
            'after': f"{start_date}T00:00:00",
            'before': f"{end_date}T23:59:59",
            'per_page': 100
        }
        
        response = wcapi.get("orders", params=params)
        
        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': f'WooCommerce API error: {response.status_code}'
            }), response.status_code
        
        orders = response.json()
        
        # Calculate revenue by product
        product_revenue = {}
        for order in orders:
            for item in order.get('line_items', []):
                product_name = item.get('name', 'Unknown')
                product_total = float(item.get('total', 0))
                product_revenue[product_name] = product_revenue.get(product_name, 0) + product_total
        
        # Get top 10 products
        sorted_products = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:10]
        
        chart_data = {
            'products': [p[0] for p in sorted_products],
            'revenue': [p[1] for p in sorted_products]
        }
        
        return jsonify({
            'status': 'success',
            'data': chart_data
        })
        
    except Exception as e:
        print(f"[WooCommerce] Error in shopify_revenue_chart: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================================
# ENDPOINT 5: Top Customers
# ============================================================================

@cross_origin()
def shopify_top_customers():
    """
    Get top customers by total spend
    Query params: days
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        wcapi = get_woocommerce_api()
        if not wcapi:
            return jsonify({
                'status': 'error',
                'message': 'WooCommerce credentials not configured'
            }), 503
        
        days = int(request.args.get('days', 90))
        start_date, end_date = calculate_date_range(days)
        
        # Fetch orders
        params = {
            'after': f"{start_date}T00:00:00",
            'before': f"{end_date}T23:59:59",
            'per_page': 100
        }
        
        response = wcapi.get("orders", params=params)
        
        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': f'WooCommerce API error: {response.status_code}'
            }), response.status_code
        
        orders = response.json()
        
        # Calculate customer totals
        customer_totals = {}
        for order in orders:
            customer_id = order.get('customer_id', 0)
            customer_name = f"{order.get('billing', {}).get('first_name', '')} {order.get('billing', {}).get('last_name', '')}".strip() or 'Guest'
            total = float(order.get('total', 0))
            
            key = f"{customer_id}_{customer_name}"
            if key not in customer_totals:
                customer_totals[key] = {
                    'customer_name': customer_name,
                    'total_spent': 0,
                    'order_count': 0
                }
            
            customer_totals[key]['total_spent'] += total
            customer_totals[key]['order_count'] += 1
        
        # Get top 10 customers
        sorted_customers = sorted(customer_totals.values(), key=lambda x: x['total_spent'], reverse=True)[:10]
        
        return jsonify({
            'status': 'success',
            'data': sorted_customers
        })
        
    except Exception as e:
        print(f"[WooCommerce] Error in shopify_top_customers: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================================
# ENDPOINT 6: Customer Segments
# ============================================================================

@cross_origin()
def shopify_customer_segments():
    """
    Get customer segmentation data
    Query params: days
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        wcapi = get_woocommerce_api()
        if not wcapi:
            return jsonify({
                'status': 'error',
                'message': 'WooCommerce credentials not configured'
            }), 503
        
        days = int(request.args.get('days', 90))
        start_date, end_date = calculate_date_range(days)
        
        # Fetch orders
        params = {
            'after': f"{start_date}T00:00:00",
            'before': f"{end_date}T23:59:59",
            'per_page': 100
        }
        
        response = wcapi.get("orders", params=params)
        
        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': f'WooCommerce API error: {response.status_code}'
            }), response.status_code
        
        orders = response.json()
        
        # Simple segmentation: by order frequency
        customer_orders = {}
        for order in orders:
            customer_id = order.get('customer_id', 0)
            if customer_id not in customer_orders:
                customer_orders[customer_id] = 0
            customer_orders[customer_id] += 1
        
        # Count segments
        new_customers = sum(1 for count in customer_orders.values() if count == 1)
        returning_customers = sum(1 for count in customer_orders.values() if 2 <= count <= 5)
        vip_customers = sum(1 for count in customer_orders.values() if count > 5)
        
        segments = [
            {'segment': 'New Customers', 'count': new_customers},
            {'segment': 'Returning Customers', 'count': returning_customers},
            {'segment': 'VIP Customers', 'count': vip_customers}
        ]
        
        return jsonify({
            'status': 'success',
            'data': segments
        })
        
    except Exception as e:
        print(f"[WooCommerce] Error in shopify_customer_segments: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================================
# ENDPOINT 7: Top Selling Products
# ============================================================================

@cross_origin()
def shopify_top_products():
    """
    Get top selling products
    Query params: days
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        wcapi = get_woocommerce_api()
        if not wcapi:
            return jsonify({
                'status': 'error',
                'message': 'WooCommerce credentials not configured'
            }), 503
        
        days = int(request.args.get('days', 30))
        start_date, end_date = calculate_date_range(days)
        
        # Fetch orders
        params = {
            'after': f"{start_date}T00:00:00",
            'before': f"{end_date}T23:59:59",
            'per_page': 100
        }
        
        response = wcapi.get("orders", params=params)
        
        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': f'WooCommerce API error: {response.status_code}'
            }), response.status_code
        
        orders = response.json()
        
        # Calculate product sales
        product_stats = {}
        for order in orders:
            for item in order.get('line_items', []):
                product_name = item.get('name', 'Unknown')
                quantity = int(item.get('quantity', 0))
                revenue = float(item.get('total', 0))
                
                if product_name not in product_stats:
                    product_stats[product_name] = {
                        'product_name': product_name,
                        'quantity_sold': 0,
                        'revenue': 0
                    }
                
                product_stats[product_name]['quantity_sold'] += quantity
                product_stats[product_name]['revenue'] += revenue
        
        # Get top 10 products
        sorted_products = sorted(product_stats.values(), key=lambda x: x['revenue'], reverse=True)[:10]
        
        return jsonify({
            'status': 'success',
            'data': sorted_products
        })
        
    except Exception as e:
        print(f"[WooCommerce] Error in shopify_top_products: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================================
# ENDPOINT 8: Product Catalog
# ============================================================================

@cross_origin()
def shopify_product_catalog():
    """
    Get product catalog
    Query params: limit
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        wcapi = get_woocommerce_api()
        if not wcapi:
            return jsonify({
                'status': 'error',
                'message': 'WooCommerce credentials not configured'
            }), 503
        
        limit = int(request.args.get('limit', 50))
        
        # Fetch products
        params = {
            'per_page': min(limit, 100),
            'status': 'publish'
        }
        
        response = wcapi.get("products", params=params)
        
        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': f'WooCommerce API error: {response.status_code}'
            }), response.status_code
        
        products = response.json()
        
        # Format products
        formatted_products = []
        for product in products:
            formatted_products.append({
                'product_id': product['id'],
                'product_name': product['name'],
                'sku': product.get('sku', ''),
                'price': float(product.get('price', 0)),
                'stock_quantity': product.get('stock_quantity', 0),
                'in_stock': product.get('stock_status', '') == 'instock'
            })
        
        return jsonify({
            'status': 'success',
            'data': formatted_products
        })
        
    except Exception as e:
        print(f"[WooCommerce] Error in shopify_product_catalog: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================================
# ENDPOINT 9 & 10: Webhooks (Not Implemented)
# ============================================================================

@cross_origin()
def shopify_webhook_log():
    """Webhook log - not implemented for WooCommerce"""
    if request.method == 'OPTIONS':
        return '', 204
    
    return jsonify({
        'status': 'success',
        'data': []
    })


@cross_origin()
def shopify_webhook_health():
    """Webhook health - not implemented for WooCommerce"""
    if request.method == 'OPTIONS':
        return '', 204
    
    return jsonify({
        'status': 'success',
        'data': {
            'total_events': 0,
            'success_rate': 100
        }
    })
