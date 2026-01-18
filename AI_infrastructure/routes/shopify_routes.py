"""
Shopify E-Commerce API Routes - Shopify Dashboard Module
========================================================================
REFACTORED: January 18, 2026

This module provides Flask API endpoints for the Shopify E-Commerce module.
Uses Supabase PostgreSQL for credential storage and Shopify Admin API for data.

Architecture:
- Frontend (shopify.js) → Flask endpoints → Shopify Admin API
- Credentials stored in ai_infrastructure.user_platform_credentials
- Platform-wide credentials (user_id=1) available to all users

Credentials Schema:
- platform: 'shopify'
- credentials.shop_name: Shopify shop name (e.g., 'inhouseprint')
- credentials.access_token: Shopify Admin API access token
- credentials.api_version: API version (e.g., '2024-01')

Endpoints:
- /api/shopify/dashboard/metrics - Dashboard KPIs
- /api/shopify/dashboard/orders - Orders list with filters
- /api/shopify/dashboard/charts/* - Chart data
- /api/shopify/dashboard/customers/* - Customer analytics
- /api/shopify/dashboard/products/* - Product performance
- /api/shopify/dashboard/webhooks/* - Webhook monitoring

Created: November 6, 2025
Last Refactor: January 18, 2026 - Replaced WooCommerce with Shopify Admin API
Previous: January 4, 2026 - Removed SQLite, added WooCommerce API (WRONG PLATFORM)
"""

import sys
import os
import json
import traceback
from datetime import datetime, timedelta
from collections import defaultdict
from flask import jsonify, request
from flask_cors import cross_origin
from pathlib import Path

# Conditional Shopify import
try:
    import shopify
    SHOPIFY_AVAILABLE = True
except ImportError:
    SHOPIFY_AVAILABLE = False
    shopify = None
    print("[SHOPIFY] ⚠️  ShopifyAPI module not installed - some features will be unavailable")
    print("[SHOPIFY] Install with: pip install ShopifyAPI pyactiveresource")

# Add shared utilities to path (AI_infrastructure/routes -> AI_infrastructure/shared)
sys.path.insert(0, str(Path(__file__).parent.parent / 'shared'))
from database_utils import execute_query


def init_shopify_routes(app, config_path=None, db_available=True):
    """
    Initialize Shopify routes
    
    Args:
        app: Flask app instance
        config_path: Unused (legacy parameter)
        db_available: Unused (legacy parameter)
    """
    
    if not SHOPIFY_AVAILABLE:
        print(f"   ⚠️  Shopify routes SKIPPED - ShopifyAPI module not installed")
        return
    
    print(f"   Registering Shopify endpoints...")
    
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

def get_shopify_credentials(user_id=None):
    """
    Get Shopify credentials from Supabase
    
    Args:
        user_id: User ID (defaults to 1 for platform-wide credentials)
        
    Returns:
        dict: Credentials with shop_name, access_token, api_version
        None: If credentials not found or invalid
    """
    if user_id is None:
        user_id = 1
    
    try:
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
        
        if not result:
            print(f"[Shopify] No credentials found for user_id={user_id}")
            return None
        
        # Handle both dict and tuple results
        credentials = result['credentials'] if isinstance(result, dict) else result[0]
        
        # Handle JSON string vs dict (database_utils may return either)
        if isinstance(credentials, str):
            credentials = json.loads(credentials)
        
        # Check if credentials have new format (shop_name + access_token)
        if 'shop_name' in credentials and 'access_token' in credentials:
            return credentials
        
        # Legacy format compatibility (consumer_key/secret from WooCommerce)
        # Try to extract shop name from base_url
        if 'base_url' in credentials:
            base_url = credentials['base_url']
            # Extract shop name from URL (https://inhouseprint.com.au → inhouseprint)
            shop_name = base_url.replace('https://', '').replace('http://', '').split('.')[0]
            
            # Check if access_token exists (might be stored as consumer_secret)
            access_token = credentials.get('access_token') or credentials.get('consumer_secret')
            
            if shop_name and access_token:
                return {
                    'shop_name': shop_name,
                    'access_token': access_token,
                    'api_version': credentials.get('api_version', '2024-01')
                }
        
        print(f"[Shopify] Invalid credential format: {credentials.keys()}")
        return None
        
    except Exception as e:
        print(f"[Shopify] Error fetching credentials: {e}")
        traceback.print_exc()
        return None


def get_shopify_session(user_id=None):
    """
    Create Shopify session with credentials
    
    Args:
        user_id: User ID (defaults to 1)
        
    Returns:
        shopify.Session: Active Shopify session
        None: If credentials invalid or session creation fails
    """
    credentials = get_shopify_credentials(user_id)
    
    if not credentials:
        return None
    
    try:
        # Use shop_domain if available, otherwise construct from shop_name
        shop_url = credentials.get('shop_domain')
        if not shop_url:
            shop_url = f"{credentials['shop_name']}.myshopify.com"
        
        api_version = credentials.get('api_version', '2024-01')
        access_token = credentials['access_token']
        
        # Create session
        session = shopify.Session(shop_url, api_version, access_token)
        shopify.ShopifyResource.activate_session(session)
        
        return session
        
    except Exception as e:
        print(f"[Shopify] Error creating session: {e}")
        traceback.print_exc()
        return None


def calculate_date_range(days):
    """Helper to calculate date range for queries"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=int(days))
    return start_date, end_date


# ============================================================================
# ENDPOINT IMPLEMENTATIONS
# ============================================================================

@cross_origin()
def shopify_metrics():
    """
    Dashboard metrics - total orders, revenue, AOV, orders today
    GET /api/shopify/dashboard/metrics?period=month
    """
    try:
        session = get_shopify_session()
        if not session:
            return jsonify({
                'status': 'error',
                'message': 'Shopify credentials not configured. Please contact administrator.'
            }), 503
        
        period = request.args.get('period', 'month')
        days_map = {'today': 1, 'week': 7, 'month': 30, 'all': 9999}
        days = days_map.get(period, 30)
        
        start_date, end_date = calculate_date_range(days)
        
        # Fetch orders from Shopify
        orders = shopify.Order.find(
            created_at_min=start_date.isoformat(),
            created_at_max=end_date.isoformat(),
            status='any',
            limit=250
        )
        
        # Calculate metrics
        total_orders = len(orders)
        total_revenue = sum(float(order.total_price) for order in orders)
        aov = total_revenue / total_orders if total_orders > 0 else 0
        
        # Orders today
        today = datetime.now().date()
        orders_today = sum(
            1 for order in orders 
            if datetime.fromisoformat(str(order.created_at).replace('Z', '+00:00')).date() == today
        )
        
        shopify.ShopifyResource.clear_session()
        
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
        print(f"[Shopify] Error in shopify_metrics: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch metrics: {str(e)}'
        }), 500


@cross_origin()
def shopify_orders():
    """
    Get orders list with filters
    GET /api/shopify/dashboard/orders?days=30&status=&min_value=0
    """
    try:
        session = get_shopify_session()
        if not session:
            return jsonify({'status': 'error', 'message': 'Credentials not configured'}), 503
        
        days = int(request.args.get('days', 30))
        status_filter = request.args.get('status', '')
        min_value = float(request.args.get('min_value', 0))
        
        start_date, end_date = calculate_date_range(days)
        
        # Fetch orders
        orders = shopify.Order.find(
            created_at_min=start_date.isoformat(),
            created_at_max=end_date.isoformat(),
            status='any',
            limit=250
        )
        
        # Format for frontend
        formatted = []
        for order in orders:
            # Apply filters
            if status_filter and order.financial_status != status_filter:
                continue
            if float(order.total_price) < min_value:
                continue
            
            formatted.append({
                'order_id': order.id,
                'order_number': order.order_number,
                'date': str(order.created_at),
                'customer_name': f"{order.customer.first_name} {order.customer.last_name}" if order.customer else "Guest",
                'total': float(order.total_price),
                'status': order.financial_status,
                'fulfillment_status': order.fulfillment_status or 'unfulfilled',
                'payment_method': order.payment_gateway_names[0] if order.payment_gateway_names else 'N/A',
                'items_count': len(order.line_items)
            })
        
        shopify.ShopifyResource.clear_session()
        
        return jsonify({'status': 'success', 'data': formatted})
        
    except Exception as e:
        print(f"[Shopify] Error in shopify_orders: {e}")
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@cross_origin()
def shopify_orders_chart():
    """
    Get orders over time for charting
    GET /api/shopify/dashboard/charts/orders-over-time?days=30
    """
    try:
        session = get_shopify_session()
        if not session:
            return jsonify({'status': 'error'}), 503
        
        days = int(request.args.get('days', 30))
        start_date, end_date = calculate_date_range(days)
        
        orders = shopify.Order.find(
            created_at_min=start_date.isoformat(),
            created_at_max=end_date.isoformat(),
            status='any',
            limit=250
        )
        
        # Group by date
        orders_by_date = defaultdict(int)
        for order in orders:
            date = datetime.fromisoformat(str(order.created_at).replace('Z', '+00:00')).date()
            orders_by_date[str(date)] += 1
        
        # Sort by date
        sorted_dates = sorted(orders_by_date.items())
        
        shopify.ShopifyResource.clear_session()
        
        return jsonify({
            'status': 'success',
            'data': {
                'labels': [d[0] for d in sorted_dates],
                'data': [d[1] for d in sorted_dates]
            }
        })
        
    except Exception as e:
        print(f"[Shopify] Error in shopify_orders_chart: {e}")
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@cross_origin()
def shopify_revenue_chart():
    """
    Get revenue by product for charting
    GET /api/shopify/dashboard/charts/revenue-by-product?days=30
    """
    try:
        session = get_shopify_session()
        if not session:
            return jsonify({'status': 'error'}), 503
        
        days = int(request.args.get('days', 30))
        start_date, end_date = calculate_date_range(days)
        
        orders = shopify.Order.find(
            created_at_min=start_date.isoformat(),
            created_at_max=end_date.isoformat(),
            status='any',
            limit=250
        )
        
        # Calculate revenue by product
        product_revenue = defaultdict(float)
        for order in orders:
            for item in order.line_items:
                product_name = item.name
                product_total = float(item.price) * item.quantity
                product_revenue[product_name] += product_total
        
        # Top 10 products
        sorted_products = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:10]
        
        shopify.ShopifyResource.clear_session()
        
        return jsonify({
            'status': 'success',
            'data': {
                'products': [p[0] for p in sorted_products],
                'revenue': [round(p[1], 2) for p in sorted_products]
            }
        })
        
    except Exception as e:
        print(f"[Shopify] Error in shopify_revenue_chart: {e}")
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@cross_origin()
def shopify_top_customers():
    """
    Get top customers by spend
    GET /api/shopify/dashboard/customers/top?days=90
    """
    try:
        session = get_shopify_session()
        if not session:
            return jsonify({'status': 'error'}), 503
        
        days = int(request.args.get('days', 90))
        start_date, end_date = calculate_date_range(days)
        
        orders = shopify.Order.find(
            created_at_min=start_date.isoformat(),
            created_at_max=end_date.isoformat(),
            status='any',
            limit=250
        )
        
        # Aggregate by customer
        customer_data = defaultdict(lambda: {'orders': 0, 'total': 0.0, 'email': '', 'name': ''})
        
        for order in orders:
            if not order.customer:
                continue
            
            customer_id = order.customer.id
            customer_data[customer_id]['orders'] += 1
            customer_data[customer_id]['total'] += float(order.total_price)
            customer_data[customer_id]['email'] = order.customer.email or 'N/A'
            customer_data[customer_id]['name'] = f"{order.customer.first_name} {order.customer.last_name}".strip() or 'Unknown'
        
        # Top 10 customers
        top_customers = sorted(
            customer_data.items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )[:10]
        
        formatted = [{
            'customer_id': cid,
            'name': data['name'],
            'email': data['email'],
            'orders': data['orders'],
            'total_spent': round(data['total'], 2),
            'avg_order_value': round(data['total'] / data['orders'], 2)
        } for cid, data in top_customers]
        
        shopify.ShopifyResource.clear_session()
        
        return jsonify({'status': 'success', 'data': formatted})
        
    except Exception as e:
        print(f"[Shopify] Error in shopify_top_customers: {e}")
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@cross_origin()
def shopify_customer_segments():
    """
    Get customer segmentation (VIP, Regular, Repeat, New)
    GET /api/shopify/dashboard/customers/segments?days=90
    """
    try:
        session = get_shopify_session()
        if not session:
            return jsonify({'status': 'error'}), 503
        
        days = int(request.args.get('days', 90))
        start_date, end_date = calculate_date_range(days)
        
        orders = shopify.Order.find(
            created_at_min=start_date.isoformat(),
            created_at_max=end_date.isoformat(),
            status='any',
            limit=250
        )
        
        # Count orders per customer
        customer_orders = defaultdict(int)
        for order in orders:
            if order.customer:
                customer_orders[order.customer.id] += 1
        
        # Segment customers
        segments = {'VIP': 0, 'Regular': 0, 'Repeat': 0, 'New': 0}
        for customer_id, order_count in customer_orders.items():
            if order_count >= 5:
                segments['VIP'] += 1
            elif order_count >= 3:
                segments['Regular'] += 1
            elif order_count >= 2:
                segments['Repeat'] += 1
            else:
                segments['New'] += 1
        
        shopify.ShopifyResource.clear_session()
        
        return jsonify({
            'status': 'success',
            'data': {
                'labels': list(segments.keys()),
                'values': list(segments.values())
            }
        })
        
    except Exception as e:
        print(f"[Shopify] Error in shopify_customer_segments: {e}")
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@cross_origin()
def shopify_top_products():
    """
    Get best-selling products
    GET /api/shopify/dashboard/products/top-sellers?days=30
    """
    try:
        session = get_shopify_session()
        if not session:
            return jsonify({'status': 'error'}), 503
        
        days = int(request.args.get('days', 30))
        start_date, end_date = calculate_date_range(days)
        
        orders = shopify.Order.find(
            created_at_min=start_date.isoformat(),
            created_at_max=end_date.isoformat(),
            status='any',
            limit=250
        )
        
        # Count product sales
        product_sales = defaultdict(lambda: {'quantity': 0, 'revenue': 0.0})
        
        for order in orders:
            for item in order.line_items:
                product_sales[item.name]['quantity'] += item.quantity
                product_sales[item.name]['revenue'] += float(item.price) * item.quantity
        
        # Top 10 products
        top_products = sorted(
            product_sales.items(),
            key=lambda x: x[1]['quantity'],
            reverse=True
        )[:10]
        
        formatted = [{
            'product_name': name,
            'quantity_sold': data['quantity'],
            'revenue': round(data['revenue'], 2)
        } for name, data in top_products]
        
        shopify.ShopifyResource.clear_session()
        
        return jsonify({'status': 'success', 'data': formatted})
        
    except Exception as e:
        print(f"[Shopify] Error in shopify_top_products: {e}")
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@cross_origin()
def shopify_product_catalog():
    """
    Get product catalog
    GET /api/shopify/dashboard/products/catalog?limit=50
    """
    try:
        session = get_shopify_session()
        if not session:
            return jsonify({'status': 'error'}), 503
        
        limit = int(request.args.get('limit', 50))
        
        # Fetch products
        products = shopify.Product.find(limit=limit)
        
        formatted = [{
            'product_id': product.id,
            'title': product.title,
            'vendor': product.vendor or 'N/A',
            'product_type': product.product_type or 'N/A',
            'price': float(product.variants[0].price) if product.variants else 0,
            'inventory': sum(v.inventory_quantity or 0 for v in product.variants),
            'published': product.published_at is not None
        } for product in products]
        
        shopify.ShopifyResource.clear_session()
        
        return jsonify({'status': 'success', 'data': formatted})
        
    except Exception as e:
        print(f"[Shopify] Error in shopify_product_catalog: {e}")
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@cross_origin()
def shopify_webhook_log():
    """
    Get webhook events (uses Shopify Webhooks API)
    GET /api/shopify/dashboard/webhooks/log?limit=50
    """
    try:
        session = get_shopify_session()
        if not session:
            return jsonify({'status': 'error'}), 503
        
        limit = int(request.args.get('limit', 50))
        
        # Fetch registered webhooks
        webhooks = shopify.Webhook.find(limit=limit)
        
        formatted = [{
            'webhook_id': webhook.id,
            'topic': webhook.topic,
            'address': webhook.address,
            'format': webhook.format,
            'created_at': str(webhook.created_at)
        } for webhook in webhooks]
        
        shopify.ShopifyResource.clear_session()
        
        return jsonify({'status': 'success', 'data': formatted})
        
    except Exception as e:
        print(f"[Shopify] Error in shopify_webhook_log: {e}")
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@cross_origin()
def shopify_webhook_health():
    """
    Get webhook health metrics
    GET /api/shopify/dashboard/webhooks/health
    """
    try:
        session = get_shopify_session()
        if not session:
            return jsonify({'status': 'error'}), 503
        
        # Get webhook count
        webhooks = shopify.Webhook.find()
        
        shopify.ShopifyResource.clear_session()
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_webhooks': len(webhooks),
                'active_webhooks': len(webhooks)
            }
        })
        
    except Exception as e:
        print(f"[Shopify] Error in shopify_webhook_health: {e}")
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500
