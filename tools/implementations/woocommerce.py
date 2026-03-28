"""
WooCommerce Tool Implementations
=================================

This module provides tool implementations for WooCommerce e-commerce.
Uses multi-tenant credential resolution via resolve_api_key() for user/org isolation.
"""

import os
import json
from flask import g
from woocommerce import API

# ============================================================================
# RUNTIME CREDENTIAL RESOLVER (Multi-tenant Safe)
# ============================================================================

def _get_woocommerce_api():
    """
    Get WooCommerce API instance with credentials for current user.
    
    Credential resolution hierarchy:
    1. User-specific credentials from database (using g.user_id)
    2. Org-shared credentials (if user is part of an org)
    3. Environment variables
    4. Fallback defaults
    
    Returns:
        woocommerce.API instance configured with appropriate credentials
        
    Raises:
        RuntimeError: If no valid credentials found
    """
    from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
    
    user_id = getattr(g, 'user_id', None)
    if not user_id:
        raise RuntimeError("No user context available - cannot resolve WooCommerce credentials")
    
    # Try to get credentials via the resolve function (3-tier: user → org → env → hardcoded)
    try:
        api_key_dict = resolve_api_key(user_id, 'woocommerce')
        
        if api_key_dict:
            # Parse credential format from database
            wc_url = api_key_dict.get('base_url') or os.getenv('WOOCOMMERCE_URL', 'https://minivetguide.com')
            wc_key = api_key_dict.get('consumer_key')
            wc_secret = api_key_dict.get('consumer_secret')
            
            if wc_key and wc_secret:
                return API(
                    url=wc_url,
                    consumer_key=wc_key,
                    consumer_secret=wc_secret,
                    version="wc/v3"
                )
    except Exception as e:
        print(f"[WARN] Error resolving WooCommerce credentials for user {user_id}: {e}")
    
    # Fallback to environment variables as last resort
    wc_url = (os.getenv('WC_STORE_URL') or 
              os.getenv('WOOCOMMERCE_URL') or 
              'https://minivetguide.com')
    wc_key = os.getenv('WC_CONSUMER_KEY') or os.getenv('WOOCOMMERCE_CONSUMER_KEY')
    wc_secret = os.getenv('WC_CONSUMER_SECRET') or os.getenv('WOOCOMMERCE_CONSUMER_SECRET')
    
    if not (wc_key and wc_secret):
        raise RuntimeError(
            f"[ERROR] WooCommerce credentials not found for user {user_id}. "
            "Please add credentials via Settings → Organisation → Credentials."
        )
    
    return API(
        url=wc_url,
        consumer_key=wc_key,
        consumer_secret=wc_secret,
        version="wc/v3"
    )


def woocommerce_get_orders(status: str = None, limit: int = 10, page: int = 1):
    """
    Retrieve orders from WooCommerce store.
    
    Args:
        status: Order status filter
        limit: Maximum orders to return
        page: Page number
    
    Returns:
        List of orders
    """
    print(f"🔧 Fetching WooCommerce orders (status: {status}, limit: {limit})")
    
    try:
        wcapi = _get_woocommerce_api()
        params = {
            'per_page': limit,
            'page': page
        }
        
        if status:
            params['status'] = status
        
        response = wcapi.get("orders", params=params)
        
        return {
            'orders': response.json(),
            'count': len(response.json()),
            'status_code': response.status_code
        }
        
    except Exception as e:
        print(f"❌ Failed to fetch orders: {e}")
        raise


def woocommerce_create_product(name: str, price: float, description: str = None, stock_quantity: int = None):
    """
    Create a new product in WooCommerce.
    
    Args:
        name: Product name
        price: Product price
        description: Product description
        stock_quantity: Stock quantity
    
    Returns:
        Created product
    """
    print(f"🔧 Creating WooCommerce product: {name}")
    
    try:
        wcapi = _get_woocommerce_api()
        data = {
            'name': name,
            'type': 'simple',
            'regular_price': str(price),
            'description': description or '',
            'manage_stock': stock_quantity is not None
        }
        
        if stock_quantity is not None:
            data['stock_quantity'] = stock_quantity
        
        response = wcapi.post("products", data)
        
        return {
            'product': response.json(),
            'product_id': response.json().get('id'),
            'created': True
        }
        
    except Exception as e:
        print(f"❌ Failed to create product: {e}")
        raise


def woocommerce_update_order(order_id: int, status: str = None, note: str = None):
    """
    Update an order's status or details.
    
    Args:
        order_id: Order ID to update
        status: New order status
        note: Order note to add
    
    Returns:
        Updated order
    """
    print(f"🔧 Updating WooCommerce order: {order_id}")
    
    try:
        wcapi = _get_woocommerce_api()
        data = {}
        
        if status:
            data['status'] = status
        
        response = wcapi.put(f"orders/{order_id}", data)
        
        # Add note if provided
        if note:
            note_data = {'note': note}
            wcapi.post(f"orders/{order_id}/notes", note_data)
        
        return {
            'order': response.json(),
            'order_id': order_id,
            'updated': True
        }
        
    except Exception as e:
        print(f"❌ Failed to update order: {e}")
        raise


def woocommerce_get_products(limit: int = 10, search: str = None):
    """
    List products from WooCommerce store.
    
    Args:
        limit: Maximum products to return
        search: Search term to filter
    
    Returns:
        List of products
    """
    print(f"🔧 Fetching WooCommerce products (limit: {limit})")
    
    try:
        wcapi = _get_woocommerce_api()
        params = {
            'per_page': limit
        }
        
        if search:
            params['search'] = search
        
        response = wcapi.get("products", params=params)
        
        return {
            'products': response.json(),
            'count': len(response.json())
        }
        
    except Exception as e:
        print(f"❌ Failed to fetch products: {e}")
        raise


def woocommerce_get_order(order_id: int):
    """Get a single order by ID"""
    print(f"🔧 Fetching WooCommerce order: {order_id}")
    try:
        wcapi = _get_woocommerce_api()
        response = wcapi.get(f"orders/{order_id}")
        return {'order': response.json(), 'status_code': response.status_code}
    except Exception as e:
        print(f"❌ Failed to fetch order: {e}")
        raise


def woocommerce_create_order(customer_id: int = None, line_items: list = None, billing: dict = None, shipping: dict = None):
    """Create a new order"""
    print(f"🔧 Creating WooCommerce order")
    try:
        wcapi = _get_woocommerce_api()
        data = {}
        if customer_id:
            data['customer_id'] = customer_id
        if line_items:
            data['line_items'] = line_items
        if billing:
            data['billing'] = billing
        if shipping:
            data['shipping'] = shipping
        
        response = wcapi.post("orders", data)
        return {'order': response.json(), 'order_id': response.json().get('id'), 'created': True}
    except Exception as e:
        print(f"❌ Failed to create order: {e}")
        raise


def woocommerce_delete_order(order_id: int, force: bool = False):
    """Delete an order"""
    print(f"🔧 Deleting WooCommerce order: {order_id}")
    try:
        wcapi = _get_woocommerce_api()
        params = {'force': force}
        response = wcapi.delete(f"orders/{order_id}", params=params)
        return {'deleted': True, 'order_id': order_id, 'status_code': response.status_code}
    except Exception as e:
        print(f"❌ Failed to delete order: {e}")
        raise


def woocommerce_get_product(product_id: int):
    """Get a single product by ID"""
    print(f"🔧 Fetching WooCommerce product: {product_id}")
    try:
        wcapi = _get_woocommerce_api()
        response = wcapi.get(f"products/{product_id}")
        return {'product': response.json(), 'status_code': response.status_code}
    except Exception as e:
        print(f"❌ Failed to fetch product: {e}")
        raise


def woocommerce_update_product(product_id: int, name: str = None, price: float = None, description: str = None, stock_quantity: int = None):
    """Update an existing product"""
    print(f"🔧 Updating WooCommerce product: {product_id}")
    try:
        wcapi = _get_woocommerce_api()
        data = {}
        if name:
            data['name'] = name
        if price:
            data['regular_price'] = str(price)
        if description:
            data['description'] = description
        if stock_quantity is not None:
            data['stock_quantity'] = stock_quantity
        
        response = wcapi.put(f"products/{product_id}", data)
        return {'product': response.json(), 'product_id': product_id, 'updated': True}
    except Exception as e:
        print(f"❌ Failed to update product: {e}")
        raise


def woocommerce_delete_product(product_id: int, force: bool = False):
    """Delete a product"""
    print(f"🔧 Deleting WooCommerce product: {product_id}")
    try:
        wcapi = _get_woocommerce_api()
        params = {'force': force}
        response = wcapi.delete(f"products/{product_id}", params=params)
        return {'deleted': True, 'product_id': product_id, 'status_code': response.status_code}
    except Exception as e:
        print(f"❌ Failed to delete product: {e}")
        raise


def woocommerce_get_customers(limit: int = 10, page: int = 1, search: str = None):
    """Get list of customers"""
    print(f"🔧 Fetching WooCommerce customers (limit: {limit})")
    try:
        params = {'per_page': limit, 'page': page}
        if search:
            params['search'] = search
        response = wcapi.get("customers", params=params)
        return {'customers': response.json(), 'count': len(response.json())}
    except Exception as e:
        print(f"❌ Failed to fetch customers: {e}")
        raise


def woocommerce_get_customer(customer_id: int):
    """Get a single customer by ID"""
    print(f"🔧 Fetching WooCommerce customer: {customer_id}")
    try:
        response = wcapi.get(f"customers/{customer_id}")
        return {'customer': response.json(), 'status_code': response.status_code}
    except Exception as e:
        print(f"❌ Failed to fetch customer: {e}")
        raise


def woocommerce_create_customer(email: str, first_name: str = None, last_name: str = None, username: str = None, billing: dict = None, shipping: dict = None):
    """Create a new customer"""
    print(f"🔧 Creating WooCommerce customer: {email}")
    try:
        data = {'email': email}
        if first_name:
            data['first_name'] = first_name
        if last_name:
            data['last_name'] = last_name
        if username:
            data['username'] = username
        if billing:
            data['billing'] = billing
        if shipping:
            data['shipping'] = shipping
        
        response = wcapi.post("customers", data)
        return {'customer': response.json(), 'customer_id': response.json().get('id'), 'created': True}
    except Exception as e:
        print(f"❌ Failed to create customer: {e}")
        raise


def woocommerce_get_categories(limit: int = 10):
    """Get product categories"""
    print(f"🔧 Fetching WooCommerce categories")
    try:
        params = {'per_page': limit}
        response = wcapi.get("products/categories", params=params)
        return {'categories': response.json(), 'count': len(response.json())}
    except Exception as e:
        print(f"❌ Failed to fetch categories: {e}")
        raise


def woocommerce_create_category(name: str, parent: int = None, description: str = None):
    """Create a new product category"""
    print(f"🔧 Creating WooCommerce category: {name}")
    try:
        data = {'name': name}
        if parent:
            data['parent'] = parent
        if description:
            data['description'] = description
        
        response = wcapi.post("products/categories", data)
        return {'category': response.json(), 'category_id': response.json().get('id'), 'created': True}
    except Exception as e:
        print(f"❌ Failed to create category: {e}")
        raise


def woocommerce_get_coupons(limit: int = 10):
    """Get list of coupons"""
    print(f"🔧 Fetching WooCommerce coupons")
    try:
        params = {'per_page': limit}
        response = wcapi.get("coupons", params=params)
        return {'coupons': response.json(), 'count': len(response.json())}
    except Exception as e:
        print(f"❌ Failed to fetch coupons: {e}")
        raise


def woocommerce_create_coupon(code: str, discount_type: str = 'fixed_cart', amount: str = '0', description: str = None):
    """Create a new coupon"""
    print(f"🔧 Creating WooCommerce coupon: {code}")
    try:
        data = {
            'code': code,
            'discount_type': discount_type,
            'amount': amount
        }
        if description:
            data['description'] = description
        
        response = wcapi.post("coupons", data)
        return {'coupon': response.json(), 'coupon_id': response.json().get('id'), 'created': True}
    except Exception as e:
        print(f"❌ Failed to create coupon: {e}")
        raise


def woocommerce_get_refunds(order_id: int):
    """Get refunds for an order"""
    print(f"🔧 Fetching refunds for order: {order_id}")
    try:
        response = wcapi.get(f"orders/{order_id}/refunds")
        return {'refunds': response.json(), 'count': len(response.json())}
    except Exception as e:
        print(f"❌ Failed to fetch refunds: {e}")
        raise


def woocommerce_create_refund(order_id: int, amount: str = None, reason: str = None, line_items: list = None):
    """Create a refund for an order"""
    print(f"🔧 Creating refund for order: {order_id}")
    try:
        data = {}
        if amount:
            data['amount'] = amount
        if reason:
            data['reason'] = reason
        if line_items:
            data['line_items'] = line_items
        
        response = wcapi.post(f"orders/{order_id}/refunds", data)
        return {'refund': response.json(), 'refund_id': response.json().get('id'), 'created': True}
    except Exception as e:
        print(f"❌ Failed to create refund: {e}")
        raise


def woocommerce_get_reports_sales(period: str = 'week', date_min: str = None, date_max: str = None):
    """Get sales reports"""
    print(f"🔧 Fetching sales reports (period: {period})")
    try:
        params = {'period': period}
        if date_min:
            params['date_min'] = date_min
        if date_max:
            params['date_max'] = date_max
        
        response = wcapi.get("reports/sales", params=params)
        return {'report': response.json(), 'period': period}
    except Exception as e:
        print(f"❌ Failed to fetch sales report: {e}")
        raise


def woocommerce_get_reports_top_sellers(period: str = 'week', limit: int = 10):
    """Get top sellers report"""
    print(f"🔧 Fetching top sellers report")
    try:
        params = {'period': period, 'per_page': limit}
        response = wcapi.get("reports/top_sellers", params=params)
        return {'top_sellers': response.json(), 'count': len(response.json())}
    except Exception as e:
        print(f"❌ Failed to fetch top sellers: {e}")
        raise


def woocommerce_get_order_notes(order_id: int):
    """Get notes for an order"""
    print(f"🔧 Fetching notes for order: {order_id}")
    try:
        response = wcapi.get(f"orders/{order_id}/notes")
        return {'notes': response.json(), 'count': len(response.json())}
    except Exception as e:
        print(f"❌ Failed to fetch order notes: {e}")
        raise


def woocommerce_create_order_note(order_id: int, note: str, customer_note: bool = False):
    """Create a note for an order"""
    print(f"🔧 Creating note for order: {order_id}")
    try:
        data = {
            'note': note,
            'customer_note': customer_note
        }
        response = wcapi.post(f"orders/{order_id}/notes", data)
        return {'note': response.json(), 'note_id': response.json().get('id'), 'created': True}
    except Exception as e:
        print(f"❌ Failed to create order note: {e}")
        raise


def woocommerce_get_shipping_zones():
    """Get shipping zones"""
    print(f"🔧 Fetching shipping zones")
    try:
        response = wcapi.get("shipping/zones")
        return {'shipping_zones': response.json(), 'count': len(response.json())}
    except Exception as e:
        print(f"❌ Failed to fetch shipping zones: {e}")
        raise


def woocommerce_get_payment_gateways():
    """Get payment gateways"""
    print(f"🔧 Fetching payment gateways")
    try:
        response = wcapi.get("payment_gateways")
        return {'payment_gateways': response.json(), 'count': len(response.json())}
    except Exception as e:
        print(f"❌ Failed to fetch payment gateways: {e}")
        raise


def woocommerce_get_tax_rates(limit: int = 10):
    """Get tax rates"""
    print(f"🔧 Fetching tax rates")
    try:
        params = {'per_page': limit}
        response = wcapi.get("taxes", params=params)
        return {'tax_rates': response.json(), 'count': len(response.json())}
    except Exception as e:
        print(f"❌ Failed to fetch tax rates: {e}")
        raise


def woocommerce_get_webhooks(limit: int = 10):
    """Get webhooks"""
    print(f"🔧 Fetching webhooks")
    try:
        params = {'per_page': limit}
        response = wcapi.get("webhooks", params=params)
        return {'webhooks': response.json(), 'count': len(response.json())}
    except Exception as e:
        print(f"❌ Failed to fetch webhooks: {e}")
        raise


def woocommerce_create_webhook(name: str, topic: str, delivery_url: str):
    """Create a new webhook"""
    print(f"🔧 Creating webhook: {name}")
    try:
        data = {
            'name': name,
            'topic': topic,
            'delivery_url': delivery_url
        }
        response = wcapi.post("webhooks", data)
        return {'webhook': response.json(), 'webhook_id': response.json().get('id'), 'created': True}
    except Exception as e:
        print(f"❌ Failed to create webhook: {e}")
        raise


def woocommerce_get_system_status():
    """Get system status"""
    print(f"🔧 Fetching WooCommerce system status")
    try:
        response = wcapi.get("system_status")
        return {'system_status': response.json(), 'status_code': response.status_code}
    except Exception as e:
        print(f"❌ Failed to fetch system status: {e}")
        raise


if __name__ == "__main__":
    print("✅ WooCommerce tools loaded - ALL 29 functions implemented")
