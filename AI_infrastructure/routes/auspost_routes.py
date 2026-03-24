"""
Australia Post Shipping Routes
Provides API endpoints for shipping calculations integrated into WooCommerce UI
"""

from flask import Blueprint, request, jsonify
import logging
import sys
from pathlib import Path

# Setup logger
logger = logging.getLogger(__name__)

# Create blueprint
auspost_bp = Blueprint('auspost', __name__, url_prefix='/api/auspost')

# Add auspost module to path
auspost_module_path = Path(__file__).resolve().parent.parent.parent / 'UI' / 'modules_external' / 'auspost-shipping'
if str(auspost_module_path) not in sys.path:
    sys.path.insert(0, str(auspost_module_path))

try:
    from backend.order_parser import OrderParser
    from backend.box_calculator import BoxCalculator
    from backend.auspost_client import AusPostClient
    logger.info("[AUSPOST_ROUTES] Successfully imported auspost backend modules")
except Exception as e:
    logger.error(f"[AUSPOST_ROUTES] Failed to import auspost modules: {e}")
    OrderParser = None
    BoxCalculator = None
    AusPostClient = None


@auspost_bp.route('/calculate-order-shipping', methods=['POST'])
def calculate_order_shipping():
    """
    Calculate shipping cost for a WooCommerce order
    
    Request body:
    {
        "line_items": [{"sku": "CFS", "quantity": 10, "name": "Product"}],
        "shipping_address": {
            "postcode": "2000",
            "state": "NSW",
            "country": "AU"
        }
    }
    
    Returns:
    {
        "success": true,
        "box_type": "small",
        "weight_grams": 595,
        "postage_cost": 10.50,
        "service": "Parcel Post"
    }
    """
    try:
        if not all([OrderParser, BoxCalculator, AusPostClient]):
            return jsonify({
                "success": False,
                "error": "Shipping module not available"
            }), 500
        
        data = request.get_json()
        line_items = data.get('line_items', [])
        shipping_address = data.get('shipping_address', {})
        
        if not line_items:
            return jsonify({
                "success": False,
                "error": "No line items provided"
            }), 400
        
        # Parse line items to extract product data
        parser = OrderParser()
        products = []
        
        for item in line_items:
            sku = item.get('sku', '')
            quantity = int(item.get('quantity', 0))
            
            # Map SKU to product code (CFS, MVG, MVGEQ, MVGEM)
            product_code = None
            sku_upper = sku.upper()
            
            if 'CFS' in sku_upper:
                product_code = 'CFS'
            elif 'MVGEM' in sku_upper:
                product_code = 'MVGEM'
            elif 'MVGEQ' in sku_upper:
                product_code = 'MVGEQ'
            elif 'MVG' in sku_upper:
                product_code = 'MVG'
            
            if product_code and quantity > 0:
                products.append({
                    'product_code': product_code,
                    'quantity': quantity
                })
        
        if not products:
            return jsonify({
                "success": False,
                "error": "No recognized products in order"
            }), 400
        
        # Calculate box requirements
        calculator = BoxCalculator()
        box_info = calculator.calculate_box_requirements(products)
        
        if not box_info['success']:
            return jsonify({
                "success": False,
                "error": box_info.get('error', 'Box calculation failed')
            }), 400
        
        # Get postcode and country
        postcode = shipping_address.get('postcode', '')
        country = shipping_address.get('country', 'AU')
        
        if not postcode:
            return jsonify({
                "success": False,
                "error": "No postcode provided"
            }), 400
        
        # Calculate postage cost
        client = AusPostClient()
        weight_grams = box_info['total_weight_grams']
        
        if country.upper() == 'AU':
            # Domestic shipping
            result = client.calculate_domestic_postage(
                from_postcode='3977',  # Default from postcode (can be configured)
                to_postcode=postcode,
                weight_grams=weight_grams,
                service_code='AUS_PARCEL_REGULAR'  # Parcel Post
            )
        else:
            # International shipping
            result = client.calculate_international_postage(
                country_code=country,
                weight_grams=weight_grams
            )
        
        if not result['success']:
            return jsonify({
                "success": False,
                "error": result.get('error', 'Postage calculation failed')
            }), 400
        
        # Return combined results
        return jsonify({
            "success": True,
            "box_type": box_info['box_type'],
            "box_count": box_info.get('box_count', 1),
            "weight_grams": weight_grams,
            "postage_cost": result.get('cost', 0),
            "service": result.get('service', 'Standard')
        })
        
    except Exception as e:
        logger.error(f"[AUSPOST_ROUTES] Error calculating shipping: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@auspost_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "success": True,
        "module": "auspost-shipping",
        "status": "available" if all([OrderParser, BoxCalculator, AusPostClient]) else "unavailable"
    })
