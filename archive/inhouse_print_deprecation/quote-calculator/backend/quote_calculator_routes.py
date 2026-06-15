"""
Quote Calculator Routes - Working Implementation
Flask blueprint for Quote Calculator module API endpoints

Successfully implements Business Cards calculator with Shopify algorithm

@version 1.0.1 - WORKING
@author InHouse Print
"""

from flask import Blueprint, request, jsonify
import sys
import os

# Add In_House_SQL Quote Calculator paths (source of truth)
in_house_sql_root = 'C:/Users/gpoli/GIT/In_House_SQL'
quote_calc_path = os.path.join(in_house_sql_root, 'G_Folder', 'Quote_Calculator')
shopify_calc_path = os.path.join(quote_calc_path, 'shopify_calculators')

# Add paths to sys.path
for path in [shopify_calc_path, quote_calc_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import Shopify calculators (standalone, no DB required)
try:
    from business_card_calculator_shopify import (
        ShopifyBusinessCardCalculator,
        PrintType,
        FinishSize,
        StockTypeStandard,
        StockTypePremium,
        CelloglazePremium
    )
    BUSINESS_CARDS_AVAILABLE = True
    print("[OK] Business Cards calculator loaded successfully")
except ImportError as e:
    print(f"[WARN] Business Cards calculator not available: {e}")
    BUSINESS_CARDS_AVAILABLE = False

# Create blueprint
quote_calc_bp = Blueprint('quote_calculator', __name__, url_prefix='/api/quote-calculator')

# ==================== Health Check ====================

@quote_calc_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint - verify calculator availability"""
    return jsonify({
        'status': 'ok',
        'calculators': {
            'business_cards': BUSINESS_CARDS_AVAILABLE
        }
    }), 200

# ==================== Business Cards Calculator ====================

@quote_calc_bp.route('/business-cards', methods=['POST'])
def calculate_business_cards():
    """
    Calculate business cards quote using Shopify calculator
    
    POST /api/quote-calculator/business-cards
    Body: {
        "quantity": 1000,
        "card_type": "standard",
        "stock_type": "satin_300gsm",
        "finish": "None",
        "print_sides": 2
    }
    """
    if not BUSINESS_CARDS_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Business Cards calculator not available'
        }), 503
    
    try:
        data = request.get_json()
        
        # Validate required parameters
        required = ['quantity', 'card_type', 'print_sides']
        missing = [p for p in required if p not in data]
        if missing:
            return jsonify({
                'success': False,
                'error': f'Missing required parameters: {", ".join(missing)}'
            }), 400
        
        # Extract parameters
        quantity = int(data['quantity'])
        card_type = data['card_type']
        sides = int(data['print_sides'])
        artworks = data.get('artworks', 1)
        
        # Initialize calculator
        calculator = ShopifyBusinessCardCalculator()
        
        # Calculate based on card type
        if card_type == 'standard':
            stock_type = StockTypeStandard.SATIN_300GSM
            print_type = PrintType.COLOR
            finish_size = FinishSize.STANDARD_90X55
            
            result = calculator.calculate_standard_business_cards(
                quantity=quantity,
                sides=sides,
                print_type=print_type,
                finish_size=finish_size,
                stock_type=stock_type,
                artworks=artworks
            )
            
        elif card_type == 'premium':
            stock_param = data.get('stock_type', 'satin_350gsm')
            finish_param = data.get('finish', 'None')
            
            stock_map = {
                'satin_350gsm': StockTypePremium.SATIN_350GSM,
                'kingkong_420gsm': StockTypePremium.KINGKONG_420GSM,
                'ecostar_350gsm': StockTypePremium.ECOSTAR_350GSM
            }
            
            finish_map = {
                'None': CelloglazePremium.NONE,
                '1_side_gloss': CelloglazePremium.ONE_SIDE_GLOSS,
                '2_side_gloss': CelloglazePremium.TWO_SIDE_GLOSS,
                '1_side_matt': CelloglazePremium.ONE_SIDE_MATT,
                '2_side_matt': CelloglazePremium.TWO_SIDE_MATT,
                '1_side_silk': CelloglazePremium.ONE_SIDE_SILK,
                '2_side_silk': CelloglazePremium.TWO_SIDE_SILK
            }
            
            stock_type = stock_map.get(stock_param, StockTypePremium.SATIN_350GSM)
            celloglaze = finish_map.get(finish_param, CelloglazePremium.NONE)
            print_type = PrintType.COLOR
            finish_size = FinishSize.STANDARD_90X55
            
            result = calculator.calculate_premium_business_cards(
                quantity=quantity,
                sides=sides,
                print_type=print_type,
                finish_size=finish_size,
                stock_type=stock_type,
                celloglaze=celloglaze,
                artworks=artworks
            )
        else:
            return jsonify({
                'success': False,
                'error': f'Invalid card_type: {card_type}'
            }), 400
        
        # Format response
        return jsonify({
            'success': True,
            'total_price': float(result.total_inc_gst),
            'total_ex_gst': float(result.total_ex_gst),
            'gst_amount': float(result.gst_amount),
            'per_card_price': float(result.total_inc_gst) / quantity,
            'turnaround_days': '3-5 business days',
            'breakdown': {
                'subtotal_before_margin': float(result.subtotal_before_margin),
                'profit_margin_pct': float(result.profit_margin_pct * 100),
                'total_ex_gst': float(result.total_ex_gst),
                'gst_amount': float(result.gst_amount),
                'total_inc_gst': float(result.total_inc_gst)
            },
            'specifications': {
                'quantity': quantity,
                'card_type': card_type,
                'print_sides': sides,
                'artworks': artworks
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Calculation error: {str(e)}'
        }), 500

# ==================== Stock List ====================

@quote_calc_bp.route('/stock-list', methods=['GET'])
def get_stock_list():
    """Get list of available paper stocks"""
    card_type = request.args.get('card_type', 'standard')
    
    if card_type == 'standard':
        stocks = [{'value': 'satin_300gsm', 'label': 'Satin 300GSM', 'price': '$126/1000'}]
    elif card_type == 'premium':
        stocks = [
            {'value': 'satin_350gsm', 'label': 'Satin 350GSM', 'price': '$180/1000'},
            {'value': 'kingkong_420gsm', 'label': 'King Kong 420GSM', 'price': '$250/1000'},
            {'value': 'ecostar_350gsm', 'label': 'Ecostar 350GSM', 'price': '$500/1000'}
        ]
    else:
        return jsonify({'success': False, 'error': 'Invalid card_type'}), 400
    
    return jsonify({'success': True, 'stocks': stocks}), 200

# ==================== Finish Options ====================

@quote_calc_bp.route('/finish-options', methods=['GET'])
def get_finish_options():
    """Get available finish options for premium cards"""
    finishes = [
        {'value': 'None', 'label': 'No Celloglaze', 'price': '$0'},
        {'value': '1_side_gloss', 'label': '1 Side Gloss', 'price': '$0.16/card'},
        {'value': '2_side_gloss', 'label': '2 Side Gloss', 'price': '$0.32/card'},
        {'value': '1_side_matt', 'label': '1 Side Matt', 'price': '$0.16/card'},
        {'value': '2_side_matt', 'label': '2 Side Matt', 'price': '$0.32/card'},
        {'value': '1_side_silk', 'label': '1 Side Silk', 'price': '$0.32/card'},
        {'value': '2_side_silk', 'label': '2 Side Silk', 'price': '$0.64/card'}
    ]
    
    return jsonify({'success': True, 'finishes': finishes}), 200
