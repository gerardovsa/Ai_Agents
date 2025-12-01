"""
Quote Calculator Flask Routes

Flask API endpoints for quote calculator module.
These routes are auto-discovered and registered by module_blueprint_loader.

Endpoints:
    POST /api/quote-calculator/calculate - Calculate quote
    POST /api/quote-calculator/business-cards - Business cards quote
    POST /api/quote-calculator/flyers - Flyers quote
    POST /api/quote-calculator/booklets - Booklets quote
    POST /api/quote-calculator/perfect-bound - Perfect bound books quote
    POST /api/quote-calculator/letterheads - Letterheads quote
    POST /api/quote-calculator/corflute - Corflute signs quote
    GET  /api/quote-calculator/stocks - Get available stocks
    GET  /api/quote-calculator/stocks/:category - Get stocks by category

FILE: UI/external/modules/quote-calculator/routes/calculator_routes.py
PURPOSE: Flask routes for quote calculator module
DEPENDENCIES:
- inhouse_modules.calculators.complete_calculator_implementation
- Flask

USED BY:
- AI_infrastructure/core/module_blueprint_loader.py (auto-discovery)

LAST MODIFIED: 2025-11-04 - Initial creation
"""

import sys
from pathlib import Path
from flask import Blueprint, request, jsonify

# Add parent directories to path for imports
module_dir = Path(__file__).parent.parent
root_dir = module_dir.parent.parent.parent

if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Import calculator wrapper
sys.path.insert(0, str(module_dir / "implementations"))
from calculator_wrapper import (
    calculate_business_cards,
    calculate_flyers,
    calculate_booklets,
    calculate_perfect_bound_books,
    calculate_letterheads,
    calculate_corflute_signs,
    get_stock_list
)

# Create Blueprint
quote_calculator_bp = Blueprint(
    'quote_calculator',
    __name__,
    url_prefix='/api/quote-calculator'
)


# ==================== HELPER FUNCTIONS ====================

def validate_required_fields(data: dict, required_fields: list) -> tuple:
    """
    Validate that all required fields are present
    
    Returns:
        (is_valid, error_message)
    """
    missing = [field for field in required_fields if field not in data]
    
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    return True, None


def handle_calculator_request(calculator_func, required_fields: list):
    """
    Generic handler for calculator requests
    
    Args:
        calculator_func: Calculator function to call
        required_fields: List of required parameter names
    
    Returns:
        JSON response
    """
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided",
                "message": "Request body must be valid JSON"
            }), 400
        
        # Validate required fields
        is_valid, error_msg = validate_required_fields(data, required_fields)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": error_msg
            }), 400
        
        # Call calculator function
        result = calculator_func(**data)
        
        # Check if calculator returned an error
        if not result.get("success", True):
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": str(e)
        }), 500


# ==================== ROUTES ====================

@quote_calculator_bp.route('/calculate', methods=['POST'])
def calculate_generic():
    """
    Generic calculate endpoint - routes to specific calculator based on product_type
    
    Request body:
        {
            "product_type": "business_cards" | "flyers" | "booklets" | "perfect_bound" | "letterheads" | "corflute",
            "parameters": { ... product-specific parameters ... }
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        product_type = data.get("product_type")
        parameters = data.get("parameters", {})
        
        if not product_type:
            return jsonify({
                "success": False,
                "error": "product_type is required"
            }), 400
        
        # Route to specific calculator
        calculators = {
            "business_cards": calculate_business_cards,
            "flyers": calculate_flyers,
            "booklets": calculate_booklets,
            "perfect_bound": calculate_perfect_bound_books,
            "letterheads": calculate_letterheads,
            "corflute": calculate_corflute_signs
        }
        
        calculator_func = calculators.get(product_type)
        
        if not calculator_func:
            return jsonify({
                "success": False,
                "error": f"Unknown product_type: {product_type}",
                "available_types": list(calculators.keys())
            }), 400
        
        # Call calculator
        result = calculator_func(**parameters)
        
        if not result.get("success", True):
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": str(e)
        }), 500


@quote_calculator_bp.route('/business-cards', methods=['POST'])
def calculate_business_cards_route():
    """
    Calculate business cards quote
    
    Request body:
        {
            "quantity": 1000,
            "stock_type": "premium",
            "sides": 2
        }
    """
    return handle_calculator_request(
        calculate_business_cards,
        required_fields=["quantity", "stock_type", "sides"]
    )


@quote_calculator_bp.route('/flyers', methods=['POST'])
def calculate_flyers_route():
    """
    Calculate flyers quote
    
    Request body:
        {
            "quantity": 5000,
            "size": "A5",
            "stock": "150GSM Gloss",
            "sides": 2
        }
    """
    return handle_calculator_request(
        calculate_flyers,
        required_fields=["quantity", "size", "stock", "sides"]
    )


@quote_calculator_bp.route('/booklets', methods=['POST'])
def calculate_booklets_route():
    """
    Calculate booklets quote
    
    Request body:
        {
            "quantity": 500,
            "pages": 16,
            "cover_stock": "250GSM Gloss",
            "inner_stock": "150GSM Gloss",
            "size": "A5"
        }
    """
    return handle_calculator_request(
        calculate_booklets,
        required_fields=["quantity", "pages", "cover_stock", "inner_stock", "size"]
    )


@quote_calculator_bp.route('/perfect-bound', methods=['POST'])
def calculate_perfect_bound_route():
    """
    Calculate perfect bound books quote
    
    Request body:
        {
            "quantity": 100,
            "pages": 120,
            "cover_stock": "300GSM Gloss",
            "inner_stock": "115GSM Uncoated",
            "size": "A4"
        }
    """
    return handle_calculator_request(
        calculate_perfect_bound_books,
        required_fields=["quantity", "pages", "cover_stock", "inner_stock", "size"]
    )


@quote_calculator_bp.route('/letterheads', methods=['POST'])
def calculate_letterheads_route():
    """
    Calculate letterheads quote
    
    Request body:
        {
            "quantity": 1000,
            "stock": "100GSM Uncoated",
            "colors": 4
        }
    """
    return handle_calculator_request(
        calculate_letterheads,
        required_fields=["quantity", "stock", "colors"]
    )


@quote_calculator_bp.route('/corflute', methods=['POST'])
def calculate_corflute_route():
    """
    Calculate corflute signs quote
    
    Request body:
        {
            "quantity": 50,
            "size": "600x900",
            "thickness": "5mm",
            "sides": 2
        }
    """
    return handle_calculator_request(
        calculate_corflute_signs,
        required_fields=["quantity", "size", "thickness", "sides"]
    )


@quote_calculator_bp.route('/stocks', methods=['GET'])
@quote_calculator_bp.route('/stocks/<category>', methods=['GET'])
def get_stocks(category: str = "all"):
    """
    Get available paper stocks
    
    Query params:
        category: Filter by category (gloss, satin, uncoated, specialty)
    
    Returns:
        List of stock objects
    """
    try:
        stocks = get_stock_list(category=category)
        
        return jsonify({
            "success": True,
            "count": len(stocks),
            "category": category,
            "stocks": stocks
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to fetch stocks",
            "message": str(e)
        }), 500


# ==================== HEALTH CHECK ====================

@quote_calculator_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "module": "quote-calculator",
        "endpoints": [
            "POST /api/quote-calculator/calculate",
            "POST /api/quote-calculator/business-cards",
            "POST /api/quote-calculator/flyers",
            "POST /api/quote-calculator/booklets",
            "POST /api/quote-calculator/perfect-bound",
            "POST /api/quote-calculator/letterheads",
            "POST /api/quote-calculator/corflute",
            "GET  /api/quote-calculator/stocks",
            "GET  /api/quote-calculator/stocks/:category"
        ]
    }), 200


# ==================== ERROR HANDLERS ====================

@quote_calculator_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "message": str(error)
    }), 404


@quote_calculator_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": str(error)
    }), 500
