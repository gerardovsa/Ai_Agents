"""
Australia Post Shipping Wrapper - AI Tool Layer
================================================

Exposes Australia Post shipping calculation to AI agents.
Auto-discovered by Registry V3 from tools/auspost_tools.json

Architecture:
    AI Agent Request
        ↓
    Registry V3
        ↓
    auspost_wrapper.py (THIS FILE)
        ↓
    backend/ (order_parser, box_calculator, auspost_client)
        ↓
    Australia Post PAC API

FILE: UI/modules_external/auspost-shipping/implementations/auspost_wrapper.py
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add backend path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.abspath(os.path.join(current_dir, '..', 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import backend modules
try:
    from order_parser import OrderParser
    from box_calculator import BoxCalculator
    from auspost_client import AusPostClient
    AUSPOST_AVAILABLE = True
except ImportError as e:
    AUSPOST_AVAILABLE = False
    print(f"⚠️  [AusPost Wrapper] Failed to import backend modules: {e}")

# Import Registry V3 decorator
try:
    from tools.registry_v3 import tool_executor
except ImportError:
    print("⚠️  [AusPost Wrapper] Failed to import tool_executor - tools will not register")
    def tool_executor():
        def decorator(func):
            return func
        return decorator


# ==================== TOOL 1: PARSE ORDER LABELS ====================

@tool_executor()
def auspost_parse_order_labels(label_data: str, **kwargs) -> Dict[str, Any]:
    """
    Parse shipping label data to extract order details and calculate dimensions.
    
    Args:
        label_data: Raw label text with customer details and product codes
        
    Returns:
        Dict with parsed orders, products, weights, and dimensions
    """
    if not AUSPOST_AVAILABLE:
        return {
            'success': False,
            'error': 'AusPost backend modules not available',
            'orders': []
        }
    
    try:
        # Parse orders
        orders = OrderParser.parse_labels(label_data)
        
        # Calculate box requirements
        orders = BoxCalculator.calculate_multiple_orders(orders)
        
        # Calculate totals
        total_orders = len(orders)
        successful_orders = len([o for o in orders if 'error' not in o])
        total_weight_kg = sum(o.get('box_details', {}).get('total_weight_kg', 0) for o in orders if 'error' not in o)
        
        return {
            'success': True,
            'total_orders': total_orders,
            'successful_orders': successful_orders,
            'failed_orders': total_orders - successful_orders,
            'total_weight_kg': round(total_weight_kg, 3),
            'orders': orders,
            'product_specs': OrderParser.get_product_specs(),
            'box_specs': BoxCalculator.get_box_specs()
        }
    
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': str(e),
            'details': traceback.format_exc()
        }


# ==================== TOOL 2: CALCULATE SINGLE POSTAGE ====================

@tool_executor()
def auspost_calculate_single_postage(
    from_postcode: str,
    to_address: Dict[str, str],
    weight_kg: float,
    length_cm: float,
    width_cm: float,
    height_cm: float,
    service_code: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate postage cost for a single order using Australia Post API.
    
    Args:
        from_postcode: Origin postcode (Australian)
        to_address: Destination address with postcode, country, etc.
        weight_kg: Package weight in kg
        length_cm: Package length in cm
        width_cm: Package width in cm
        height_cm: Package height in cm
        service_code: Optional specific service code
        
    Returns:
        Dict with postage cost, service options, and delivery time
    """
    if not AUSPOST_AVAILABLE:
        return {
            'success': False,
            'error': 'AusPost backend modules not available'
        }
    
    try:
        # Initialize API client (uses env var AUSPOST_API_KEY or test environment)
        client = AusPostClient()
        
        # Determine if domestic or international
        country = to_address.get('country', 'Australia').lower()
        is_domestic = 'australia' in country
        
        if is_domestic:
            # Domestic shipping
            to_postcode = to_address.get('postcode', '')
            
            if service_code:
                # Calculate specific service
                result = client.calculate_domestic_postage(
                    from_postcode=from_postcode,
                    to_postcode=to_postcode,
                    length_cm=length_cm,
                    width_cm=width_cm,
                    height_cm=height_cm,
                    weight_kg=weight_kg,
                    service_code=service_code
                )
                
                if 'error' in result:
                    return {
                        'success': False,
                        'error': result.get('message', result['error']),
                        'is_domestic': True
                    }
                
                return {
                    'success': True,
                    'is_domestic': True,
                    'service': result.get('postage_result', {}),
                    'from_postcode': from_postcode,
                    'to_postcode': to_postcode
                }
            else:
                # Get all available services
                result = client.get_domestic_services(
                    from_postcode=from_postcode,
                    to_postcode=to_postcode,
                    length_cm=length_cm,
                    width_cm=width_cm,
                    height_cm=height_cm,
                    weight_kg=weight_kg
                )
                
                if 'error' in result:
                    return {
                        'success': False,
                        'error': result.get('message', result['error']),
                        'is_domestic': True
                    }
                
                services = result.get('services', {}).get('service', [])
                
                # Find cheapest and fastest options
                cheapest = min(services, key=lambda x: float(x.get('price', 999)), default=None)
                fastest = next((s for s in services if 'EXPRESS' in s.get('code', '')), None)
                
                return {
                    'success': True,
                    'is_domestic': True,
                    'services': services,
                    'cheapest_service': cheapest,
                    'fastest_service': fastest or cheapest,
                    'total_services': len(services),
                    'from_postcode': from_postcode,
                    'to_postcode': to_postcode
                }
        else:
            # International shipping
            country_code = AusPostClient.country_name_to_code(country)
            
            if not country_code:
                return {
                    'success': False,
                    'error': f'Could not determine country code for: {country}',
                    'is_domestic': False
                }
            
            if service_code:
                # Calculate specific service
                result = client.calculate_international_postage(
                    country_code=country_code,
                    weight_kg=weight_kg,
                    service_code=service_code
                )
                
                if 'error' in result:
                    return {
                        'success': False,
                        'error': result.get('message', result['error']),
                        'is_domestic': False,
                        'country_code': country_code
                    }
                
                return {
                    'success': True,
                    'is_domestic': False,
                    'service': result.get('postage_result', {}),
                    'country': country,
                    'country_code': country_code
                }
            else:
                # Get all available services
                result = client.get_international_services(
                    country_code=country_code,
                    weight_kg=weight_kg
                )
                
                if 'error' in result:
                    return {
                        'success': False,
                        'error': result.get('message', result['error']),
                        'is_domestic': False,
                        'country_code': country_code
                    }
                
                services = result.get('services', {}).get('service', [])
                
                # Find cheapest option
                cheapest = min(services, key=lambda x: float(x.get('price', 999)), default=None)
                
                return {
                    'success': True,
                    'is_domestic': False,
                    'services': services,
                    'cheapest_service': cheapest,
                    'total_services': len(services),
                    'country': country,
                    'country_code': country_code
                }
    
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': str(e),
            'details': traceback.format_exc()
        }


# ==================== TOOL 3: BATCH CALCULATE POSTAGE ====================

@tool_executor()
def auspost_batch_calculate_postage(
    label_data: str,
    from_postcode: str,
    service_preference: str = 'cheapest',
    **kwargs
) -> Dict[str, Any]:
    """
    Process multiple orders and calculate postage costs for each.
    
    Args:
        label_data: Raw label text with multiple orders
        from_postcode: Origin postcode (Australian)
        service_preference: 'cheapest', 'fastest', 'regular', or 'express'
        
    Returns:
        Dict with all orders and their postage costs
    """
    if not AUSPOST_AVAILABLE:
        return {
            'success': False,
            'error': 'AusPost backend modules not available',
            'orders': []
        }
    
    try:
        # Parse orders
        parse_result = auspost_parse_order_labels(label_data)
        
        if not parse_result.get('success'):
            return parse_result
        
        orders = parse_result.get('orders', [])
        
        # Initialize API client
        client = AusPostClient()
        
        # Calculate postage for each order
        for order in orders:
            if 'error' in order:
                continue
            
            box_details = order.get('box_details', {})
            customer = order.get('customer', {})
            
            # Build destination address
            to_address = {
                'postcode': customer.get('postcode', ''),
                'suburb': customer.get('address_line2', ''),
                'state': customer.get('state', ''),
                'country': customer.get('country', 'Australia')
            }
            
            # Calculate postage
            postage_result = auspost_calculate_single_postage(
                from_postcode=from_postcode,
                to_address=to_address,
                weight_kg=box_details.get('total_weight_kg', 0),
                length_cm=box_details.get('length_cm', 0),
                width_cm=box_details.get('width_cm', 0),
                height_cm=box_details.get('height_cm', 0)
            )
            
            # Add postage details to order
            order['postage'] = postage_result
            
            # Select service based on preference
            if postage_result.get('success'):
                services = postage_result.get('services', [])
                
                if service_preference == 'cheapest':
                    selected = postage_result.get('cheapest_service')
                elif service_preference == 'fastest':
                    selected = postage_result.get('fastest_service')
                elif service_preference == 'express':
                    selected = next((s for s in services if 'EXPRESS' in s.get('code', '')), None)
                else:  # 'regular'
                    selected = next((s for s in services if 'REGULAR' in s.get('code', '')), None)
                
                order['selected_service'] = selected
                order['postage_cost'] = float(selected.get('price', 0)) if selected else 0.0
            else:
                order['postage_cost'] = 0.0
                order['selected_service'] = None
        
        # Calculate totals
        total_postage = sum(o.get('postage_cost', 0) for o in orders if 'error' not in o)
        successful_calculations = len([o for o in orders if o.get('postage', {}).get('success')])
        
        return {
            'success': True,
            'total_orders': len(orders),
            'successful_calculations': successful_calculations,
            'total_postage_cost': round(total_postage, 2),
            'service_preference': service_preference,
            'from_postcode': from_postcode,
            'orders': orders,
            'summary': {
                'domestic_orders': len([o for o in orders if o.get('postage', {}).get('is_domestic')]),
                'international_orders': len([o for o in orders if not o.get('postage', {}).get('is_domestic', True)]),
                'total_weight_kg': sum(o.get('box_details', {}).get('total_weight_kg', 0) for o in orders if 'error' not in o)
            }
        }
    
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': str(e),
            'details': traceback.format_exc()
        }


# ==================== TOOL 4: GET SERVICE OPTIONS ====================

@tool_executor()
def auspost_get_service_options(service_type: str = 'all', **kwargs) -> Dict[str, Any]:
    """
    Get list of available Australia Post service options.
    
    Args:
        service_type: 'domestic', 'international', or 'all'
        
    Returns:
        Dict with service codes and descriptions
    """
    if not AUSPOST_AVAILABLE:
        return {
            'success': False,
            'error': 'AusPost backend modules not available'
        }
    
    try:
        domestic_services = AusPostClient.get_service_descriptions()
        
        # International service codes (common ones)
        international_services = {
            'INT_PARCEL_STD_OWN_PACKAGING': 'International Standard Parcel',
            'INT_PARCEL_EXP_OWN_PACKAGING': 'International Express Parcel',
            'INT_PARCEL_COR_OWN_PACKAGING': 'International Courier Parcel',
            'INT_PARCEL_AIR_OWN_PACKAGING': 'International Air Mail Parcel',
            'INT_PARCEL_SEA_OWN_PACKAGING': 'International Sea Mail Parcel'
        }
        
        result = {
            'success': True,
            'service_type': service_type
        }
        
        if service_type in ['domestic', 'all']:
            result['domestic_services'] = [
                {'code': code, 'name': name, 'type': 'domestic'}
                for code, name in domestic_services.items()
            ]
        
        if service_type in ['international', 'all']:
            result['international_services'] = [
                {'code': code, 'name': name, 'type': 'international'}
                for code, name in international_services.items()
            ]
        
        if service_type == 'all':
            result['total_services'] = len(result.get('domestic_services', [])) + len(result.get('international_services', []))
        
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# ==================== MODULE INITIALIZATION ====================

if __name__ == "__main__":
    print("="*70)
    print("AUSTRALIA POST SHIPPING WRAPPER - TEST")
    print("="*70)
    
    # Test with sample label data
    sample_labels = '''
    "TO: Test Customer
    123 Main Street
    Melbourne 3000
    VIC, Australia
    Ph: 0400123456
    Email: test@example.com
    
    1 x MVG
    1 x CFS"
    '''
    
    print("\n📋 Test 1: Parse Labels")
    result = auspost_parse_order_labels(sample_labels)
    print(f"Success: {result.get('success')}")
    print(f"Total Orders: {result.get('total_orders')}")
    print(f"Total Weight: {result.get('total_weight_kg')} kg")
    
    if result.get('success') and result.get('orders'):
        order = result['orders'][0]
        print(f"\n📦 Test 2: Calculate Postage")
        
        postage_result = auspost_calculate_single_postage(
            from_postcode='3020',
            to_address={
                'postcode': '3000',
                'country': 'Australia'
            },
            weight_kg=order['box_details']['total_weight_kg'],
            length_cm=order['box_details']['length_cm'],
            width_cm=order['box_details']['width_cm'],
            height_cm=order['box_details']['height_cm']
        )
        
        print(f"Success: {postage_result.get('success')}")
        if postage_result.get('success'):
            cheapest = postage_result.get('cheapest_service', {})
            print(f"Cheapest Service: {cheapest.get('name')} - ${cheapest.get('price')}")
