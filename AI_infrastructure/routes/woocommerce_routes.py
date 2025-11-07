"""
WooCommerce API Routes
======================

Direct programmatic API endpoints for WooCommerce operations.
These routes bypass the AI agent for efficient data retrieval.
"""

from flask import Blueprint, request, jsonify
import sys
import os

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))

try:
    from tools.implementations.woocommerce import (
        woocommerce_get_orders,
        woocommerce_get_order,
        woocommerce_get_products,
        woocommerce_get_product,
        woocommerce_get_customers,
        woocommerce_get_customer,
        woocommerce_get_refunds,
        woocommerce_get_coupons,
        woocommerce_get_reports_sales,
        woocommerce_get_reports_top_sellers,
        woocommerce_get_system_status
    )
except ImportError as e:
    print(f"⚠️ Warning: Could not import WooCommerce tools: {e}")
    # Define dummy functions if import fails
    def woocommerce_get_orders(*args, **kwargs):
        return {'error': 'WooCommerce tools not available'}
    def woocommerce_get_products(*args, **kwargs):
        return {'error': 'WooCommerce tools not available'}
    def woocommerce_get_customers(*args, **kwargs):
        return {'error': 'WooCommerce tools not available'}

# Create blueprint
woocommerce_bp = Blueprint('woocommerce', __name__, url_prefix='/api/woocommerce')


@woocommerce_bp.route('/orders', methods=['GET'])
def get_orders():
    """
    Get WooCommerce orders with optional filtering.
    
    Query Parameters:
        status: Order status filter (any, pending, processing, completed, etc.)
        limit: Number of orders to return (default: 50)
        page: Page number (default: 1)
    
    Returns:
        JSON array of orders with formatted data
    """
    try:
        status = request.args.get('status', 'any')
        limit = int(request.args.get('limit', 50))
        page = int(request.args.get('page', 1))
        
        print(f"🛒 Direct API call: Get orders (status={status}, limit={limit}, page={page})")
        
        # Call WooCommerce tool directly
        result = woocommerce_get_orders(
            status=None if status == 'any' else status,
            limit=limit,
            page=page
        )
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        # Format orders for dashboard
        orders = result.get('orders', [])
        formatted_orders = []
        
        for order in orders:
            # Extract billing info
            billing = order.get('billing', {})
            shipping = order.get('shipping', {})
            
            # Format shipping address
            shipping_parts = []
            if shipping.get('first_name') or shipping.get('last_name'):
                shipping_parts.append(f"{shipping.get('first_name', '')} {shipping.get('last_name', '')}".strip())
            if shipping.get('company'):
                shipping_parts.append(shipping.get('company'))
            if shipping.get('address_1'):
                shipping_parts.append(shipping.get('address_1'))
            if shipping.get('address_2'):
                shipping_parts.append(shipping.get('address_2'))
            if shipping.get('city'):
                city_postal = f"{shipping.get('city', '')} {shipping.get('postcode', '')}".strip()
                shipping_parts.append(city_postal)
            if shipping.get('state') or shipping.get('country'):
                state_country = f"{shipping.get('state', '')} {shipping.get('country', '')}".strip()
                shipping_parts.append(state_country)
            
            formatted_order = {
                'id': order.get('id'),
                'date_created': order.get('date_created'),
                'status': order.get('status'),
                'total': order.get('total'),
                'currency': order.get('currency'),
                'customer_name': f"{billing.get('first_name', '')} {billing.get('last_name', '')}".strip(),
                'customer_email': billing.get('email', ''),
                'customer_phone': billing.get('phone', ''),
                'shipping_address': '\n'.join(shipping_parts),
                'line_items': [
                    {
                        'name': item.get('name'),
                        'sku': item.get('sku', ''),
                        'quantity': item.get('quantity')
                    }
                    for item in order.get('line_items', [])
                ]
            }
            formatted_orders.append(formatted_order)
        
        return jsonify({
            'success': True,
            'count': len(formatted_orders),
            'orders': formatted_orders
        })
        
    except Exception as e:
        print(f" Error in get_orders: {e}")
        return jsonify({'error': str(e)}), 500


@woocommerce_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get detailed information for a specific order."""
    try:
        print(f"🛒 Direct API call: Get order #{order_id}")
        result = woocommerce_get_order(order_id)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'order': result.get('order')
        })
        
    except Exception as e:
        print(f" Error in get_order: {e}")
        return jsonify({'error': str(e)}), 500


@woocommerce_bp.route('/products', methods=['GET'])
def get_products():
    """
    Get WooCommerce products with optional filtering.
    
    Query Parameters:
        category: Product category filter
        limit: Number of products to return (default: 50)
        page: Page number (default: 1)
    """
    try:
        category = request.args.get('category')
        limit = int(request.args.get('limit', 50))
        page = int(request.args.get('page', 1))
        
        print(f"📦 Direct API call: Get products (limit={limit}, page={page})")
        
        result = woocommerce_get_products(limit=limit, page=page)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'count': result.get('count'),
            'products': result.get('products', [])
        })
        
    except Exception as e:
        print(f" Error in get_products: {e}")
        return jsonify({'error': str(e)}), 500


@woocommerce_bp.route('/customers', methods=['GET'])
def get_customers():
    """Get WooCommerce customers."""
    try:
        limit = int(request.args.get('limit', 50))
        page = int(request.args.get('page', 1))
        
        print(f"👥 Direct API call: Get customers (limit={limit}, page={page})")
        
        result = woocommerce_get_customers(limit=limit, page=page)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'count': result.get('count'),
            'customers': result.get('customers', [])
        })
        
    except Exception as e:
        print(f" Error in get_customers: {e}")
        return jsonify({'error': str(e)}), 500


@woocommerce_bp.route('/reports/sales', methods=['GET'])
def get_sales_report():
    """Get sales report data."""
    try:
        period = request.args.get('period', 'week')
        
        print(f"📊 Direct API call: Get sales report (period={period})")
        
        result = woocommerce_get_reports_sales(period=period)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'report': result
        })
        
    except Exception as e:
        print(f" Error in get_sales_report: {e}")
        return jsonify({'error': str(e)}), 500


@woocommerce_bp.route('/reports/top-sellers', methods=['GET'])
def get_top_sellers():
    """Get top selling products."""
    try:
        period = request.args.get('period', 'week')
        limit = int(request.args.get('limit', 10))
        
        print(f"🏆 Direct API call: Get top sellers (period={period}, limit={limit})")
        
        result = woocommerce_get_reports_top_sellers(period=period, limit=limit)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'products': result
        })
        
    except Exception as e:
        print(f" Error in get_top_sellers: {e}")
        return jsonify({'error': str(e)}), 500


@woocommerce_bp.route('/system/status', methods=['GET'])
def get_system_status():
    """Get WooCommerce system status."""
    try:
        print(f"⚙️ Direct API call: Get system status")
        
        result = woocommerce_get_system_status()
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'status': result
        })
        
    except Exception as e:
        print(f" Error in get_system_status: {e}")
        return jsonify({'error': str(e)}), 500


@woocommerce_bp.route('/health', methods=['GET'])
def health_check():
    """Check if WooCommerce API is configured and accessible."""
    try:
        # Try to get a single order to verify connection
        result = woocommerce_get_orders(limit=1, page=1)
        
        if 'error' in result:
            return jsonify({
                'status': 'error',
                'message': result['error']
            }), 500
        
        return jsonify({
            'status': 'ok',
            'message': 'WooCommerce API is configured and accessible',
            'status_code': result.get('status_code')
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
