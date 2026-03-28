"""
WooCommerce API Routes
File: AI_infrastructure/routes/woocommerce_routes.py

WooCommerce API Routes (ENHANCED VERSION)
==========================================

Direct programmatic API endpoints for WooCommerce operations.
These routes bypass the AI agent for efficient data retrieval.

✅ NO CURSOR MANAGEMENT ISSUES - All operations delegated to WooCommerce tools
✅ ENHANCEMENTS: Logging, validation, error handling, authentication

ENDPOINTS:
- GET /api/woocommerce/orders - List orders
- GET /api/woocommerce/orders/<id> - Get order details
- GET /api/woocommerce/products - List products
- GET /api/woocommerce/customers - List customers
- GET /api/woocommerce/reports/sales - Sales report
- GET /api/woocommerce/reports/top-sellers - Top selling products
- GET /api/woocommerce/system/status - System status
- GET /api/woocommerce/health - Health check

NOTE: All database/API operations are handled by tools/implementations/woocommerce.py
      This file has ZERO direct database operations.

LAST MODIFIED: 2025-12-07 - Enhanced logging and error handling
PREVIOUS: Initial implementation
"""

from flask import Blueprint, request, jsonify
import sys
import os
import logging
from AI_infrastructure.auth.user_auth import require_auth

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))

# Setup logging
logger = logging.getLogger(__name__)

# ======================================================================
# IMPORT WOOCOMMERCE TOOLS
# ======================================================================

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
    WOOCOMMERCE_AVAILABLE = True
    logger.info("✅ WooCommerce tools imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import WooCommerce tools: {e}")
    WOOCOMMERCE_AVAILABLE = False
    
    # Define dummy functions if import fails
    def woocommerce_get_orders(*args, **kwargs):
        return {'error': 'WooCommerce tools not available', 'details': str(e)}
    def woocommerce_get_order(*args, **kwargs):
        return {'error': 'WooCommerce tools not available'}
    def woocommerce_get_products(*args, **kwargs):
        return {'error': 'WooCommerce tools not available'}
    def woocommerce_get_product(*args, **kwargs):
        return {'error': 'WooCommerce tools not available'}
    def woocommerce_get_customers(*args, **kwargs):
        return {'error': 'WooCommerce tools not available'}
    def woocommerce_get_customer(*args, **kwargs):
        return {'error': 'WooCommerce tools not available'}
    def woocommerce_get_refunds(*args, **kwargs):
        return {'error': 'WooCommerce tools not available'}
    def woocommerce_get_coupons(*args, **kwargs):
        return {'error': 'WooCommerce tools not available'}
    def woocommerce_get_reports_sales(*args, **kwargs):
        return {'error': 'WooCommerce tools not available'}
    def woocommerce_get_reports_top_sellers(*args, **kwargs):
        return {'error': 'WooCommerce tools not available'}
    def woocommerce_get_system_status(*args, **kwargs):
        return {'error': 'WooCommerce tools not available'}

# Create blueprint
woocommerce_bp = Blueprint('woocommerce', __name__, url_prefix='/api/woocommerce')

# ======================================================================
# CONSTANTS
# ======================================================================

# Default pagination values
DEFAULT_LIMIT = 50
MAX_LIMIT = 100
DEFAULT_PAGE = 1

# Valid order statuses
VALID_ORDER_STATUSES = [
    'any', 'pending', 'processing', 'on-hold', 'completed', 
    'cancelled', 'refunded', 'failed', 'trash'
]

# Valid report periods
VALID_REPORT_PERIODS = ['today', 'week', 'month', 'year', 'last_month']

# ======================================================================
# HELPER FUNCTIONS
# ======================================================================

def validate_pagination_params(limit=None, page=None):
    """
    Validate and normalize pagination parameters
    
    Args:
        limit: Items per page (optional)
        page: Page number (optional)
    
    Returns:
        tuple: (validated_limit, validated_page)
    """
    try:
        validated_limit = int(limit) if limit else DEFAULT_LIMIT
        validated_page = int(page) if page else DEFAULT_PAGE
        
        # Enforce limits
        if validated_limit < 1:
            validated_limit = DEFAULT_LIMIT
        if validated_limit > MAX_LIMIT:
            validated_limit = MAX_LIMIT
        
        if validated_page < 1:
            validated_page = DEFAULT_PAGE
        
        return validated_limit, validated_page
    except (ValueError, TypeError):
        return DEFAULT_LIMIT, DEFAULT_PAGE


def format_error_response(error_message, status_code=500):
    """Format error response"""
    logger.error(f"API Error: {error_message}")
    return jsonify({
        'success': False,
        'error': error_message
    }), status_code


def format_success_response(data, status_code=200):
    """Format success response"""
    data['success'] = True
    return jsonify(data), status_code


# ======================================================================
# ENDPOINTS (NO DATABASE OPERATIONS)
# ======================================================================

@woocommerce_bp.route('/orders', methods=['GET'])
@require_auth
def get_orders():
    """
    Get WooCommerce orders with optional filtering.
    
    Query Parameters:
        status: Order status filter (any, pending, processing, completed, etc.)
        limit: Number of orders to return (default: 50, max: 100)
        page: Page number (default: 1)
    
    Returns:
        JSON array of orders with formatted data
    
    ✅ NO CURSOR ISSUES: All operations delegated to woocommerce_get_orders()
    """
    try:
        # Validate parameters
        status = request.args.get('status', 'any')
        if status not in VALID_ORDER_STATUSES:
            return format_error_response(
                f"Invalid status. Must be one of: {', '.join(VALID_ORDER_STATUSES)}", 
                400
            )
        
        limit, page = validate_pagination_params(
            request.args.get('limit'),
            request.args.get('page')
        )
        
        logger.info(f"🛒 Get orders: status={status}, limit={limit}, page={page}")
        
        # Call WooCommerce tool directly (handles all database/API operations)
        result = woocommerce_get_orders(
            status=None if status == 'any' else status,
            limit=limit,
            page=page
        )
        
        if not isinstance(result, dict):
            return format_error_response(f'WooCommerce tool returned unexpected response: {str(result)[:200]}', 500)
        if 'error' in result:
            return format_error_response(result['error'], 500)
        
        # Format orders for dashboard
        orders = result.get('orders', [])

        # Guard: WooCommerce API may return an error dict instead of a list
        # (e.g. {"code":"woocommerce_rest_...", "message":"..."})
        if not isinstance(orders, list):
            err_msg = orders.get('message', str(orders)) if isinstance(orders, dict) else str(orders)
            return format_error_response(f'WooCommerce API error: {err_msg}', 500)

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
        
        logger.info(f"✅ Retrieved {len(formatted_orders)} orders")
        
        return format_success_response({
            'count': len(formatted_orders),
            'orders': formatted_orders,
            'page': page,
            'limit': limit
        })
        
    except Exception as e:
        logger.exception(f"Error in get_orders: {e}")
        return format_error_response(str(e), 500)


@woocommerce_bp.route('/orders/<int:order_id>', methods=['GET'])
@require_auth
def get_order(order_id):
    """
    Get detailed information for a specific order.
    
    ✅ NO CURSOR ISSUES: All operations delegated to woocommerce_get_order()
    """
    try:
        logger.info(f"🛒 Get order: #{order_id}")
        
        # Call WooCommerce tool (handles all database/API operations)
        result = woocommerce_get_order(order_id)
        
        if 'error' in result:
            return format_error_response(result['error'], 500)
        
        return format_success_response({
            'order': result.get('order')
        })
        
    except Exception as e:
        logger.exception(f"Error in get_order: {e}")
        return format_error_response(str(e), 500)


@woocommerce_bp.route('/products', methods=['GET'])
@require_auth
def get_products():
    """
    Get WooCommerce products with optional filtering.
    
    Query Parameters:
        category: Product category filter
        limit: Number of products to return (default: 50, max: 100)
        page: Page number (default: 1)
    
    ✅ NO CURSOR ISSUES: All operations delegated to woocommerce_get_products()
    """
    try:
        category = request.args.get('category')
        limit, page = validate_pagination_params(
            request.args.get('limit'),
            request.args.get('page')
        )
        
        logger.info(f"📦 Get products: category={category}, limit={limit}, page={page}")
        
        # Call WooCommerce tool (handles all database/API operations)
        result = woocommerce_get_products(limit=limit, page=page)
        
        if 'error' in result:
            return format_error_response(result['error'], 500)
        
        logger.info(f"✅ Retrieved {result.get('count')} products")
        
        return format_success_response({
            'count': result.get('count'),
            'products': result.get('products', []),
            'page': page,
            'limit': limit
        })
        
    except Exception as e:
        logger.exception(f"Error in get_products: {e}")
        return format_error_response(str(e), 500)


@woocommerce_bp.route('/customers', methods=['GET'])
@require_auth
def get_customers():
    """
    Get WooCommerce customers.
    
    ✅ NO CURSOR ISSUES: All operations delegated to woocommerce_get_customers()
    """
    try:
        limit, page = validate_pagination_params(
            request.args.get('limit'),
            request.args.get('page')
        )
        
        logger.info(f"👥 Get customers: limit={limit}, page={page}")
        
        # Call WooCommerce tool (handles all database/API operations)
        result = woocommerce_get_customers(limit=limit, page=page)
        
        if 'error' in result:
            return format_error_response(result['error'], 500)
        
        logger.info(f"✅ Retrieved {result.get('count')} customers")
        
        return format_success_response({
            'count': result.get('count'),
            'customers': result.get('customers', []),
            'page': page,
            'limit': limit
        })
        
    except Exception as e:
        logger.exception(f"Error in get_customers: {e}")
        return format_error_response(str(e), 500)


@woocommerce_bp.route('/reports/sales', methods=['GET'])
@require_auth
def get_sales_report():
    """
    Get sales report data.
    
    Query Parameters:
        period: Report period (today, week, month, year, last_month)
    
    ✅ NO CURSOR ISSUES: All operations delegated to woocommerce_get_reports_sales()
    """
    try:
        period = request.args.get('period', 'week')
        
        if period not in VALID_REPORT_PERIODS:
            return format_error_response(
                f"Invalid period. Must be one of: {', '.join(VALID_REPORT_PERIODS)}", 
                400
            )
        
        logger.info(f"📊 Get sales report: period={period}")
        
        # Call WooCommerce tool (handles all database/API operations)
        result = woocommerce_get_reports_sales(period=period)
        
        if 'error' in result:
            return format_error_response(result['error'], 500)
        
        return format_success_response({
            'report': result,
            'period': period
        })
        
    except Exception as e:
        logger.exception(f"Error in get_sales_report: {e}")
        return format_error_response(str(e), 500)


@woocommerce_bp.route('/reports/top-sellers', methods=['GET'])
@require_auth
def get_top_sellers():
    """
    Get top selling products.
    
    ✅ NO CURSOR ISSUES: All operations delegated to woocommerce_get_reports_top_sellers()
    """
    try:
        period = request.args.get('period', 'week')
        limit, _ = validate_pagination_params(request.args.get('limit', 10), None)
        
        if period not in VALID_REPORT_PERIODS:
            return format_error_response(
                f"Invalid period. Must be one of: {', '.join(VALID_REPORT_PERIODS)}", 
                400
            )
        
        logger.info(f"🏆 Get top sellers: period={period}, limit={limit}")
        
        # Call WooCommerce tool (handles all database/API operations)
        result = woocommerce_get_reports_top_sellers(period=period, limit=limit)
        
        if 'error' in result:
            return format_error_response(result['error'], 500)
        
        return format_success_response({
            'products': result,
            'period': period,
            'limit': limit
        })
        
    except Exception as e:
        logger.exception(f"Error in get_top_sellers: {e}")
        return format_error_response(str(e), 500)


@woocommerce_bp.route('/system/status', methods=['GET'])
@require_auth
def get_system_status():
    """
    Get WooCommerce system status.
    
    ✅ NO CURSOR ISSUES: All operations delegated to woocommerce_get_system_status()
    """
    try:
        logger.info(f"⚙️ Get system status")
        
        # Call WooCommerce tool (handles all database/API operations)
        result = woocommerce_get_system_status()
        
        if 'error' in result:
            return format_error_response(result['error'], 500)
        
        return format_success_response({
            'status': result
        })
        
    except Exception as e:
        logger.exception(f"Error in get_system_status: {e}")
        return format_error_response(str(e), 500)


@woocommerce_bp.route('/health', methods=['GET'])
def health_check():
    """
    Check if WooCommerce API is configured and accessible.
    
    ✅ NO CURSOR ISSUES: All operations delegated to woocommerce_get_orders()
    """
    try:
        if not WOOCOMMERCE_AVAILABLE:
            return jsonify({
                'status': 'error',
                'message': 'WooCommerce tools not available',
                'configured': False
            }), 503
        
        # Try to get a single order to verify connection
        result = woocommerce_get_orders(limit=1, page=1)
        
        if 'error' in result:
            return jsonify({
                'status': 'error',
                'message': result['error'],
                'configured': True,
                'accessible': False
            }), 500
        
        return jsonify({
            'status': 'ok',
            'message': 'WooCommerce API is configured and accessible',
            'configured': True,
            'accessible': True,
            'status_code': result.get('status_code')
        }), 200
        
    except Exception as e:
        logger.exception(f"Error in health_check: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'configured': WOOCOMMERCE_AVAILABLE,
            'accessible': False
        }), 500


# ======================================================================
# STARTUP LOGGING
# ======================================================================
if WOOCOMMERCE_AVAILABLE:
    logger.info("✅ WooCommerce routes loaded")
else:
    logger.warning("⚠️ WooCommerce tools not available")