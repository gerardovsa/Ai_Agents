"""
Calculator Test Routes
======================

Flask blueprint for calculator testing dashboard - integrated into BISTART server.
Tests both Shopify (25) and GOD (3) calculators.

Author: AI Agent Testing Framework
Date: December 10, 2025
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from flask import Blueprint, jsonify, request
from typing import Dict, Any, List
from collections import deque

# Add paths for tool imports
root_dir = Path(__file__).parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from tools.implementations.meta_tools import search_tools, get_tool_schema

# Create blueprint
calculator_test_bp = Blueprint('calculator_test', __name__)

# Server logs storage (keep last 100 logs)
server_logs = deque(maxlen=100)

def log_server_message(message: str, level: str = 'INFO'):
    """Log a server message with timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}"
    server_logs.append(log_entry)
    print(log_entry)  # Also print to console

# Calculator search keywords configuration
CALCULATOR_KEYWORDS = {
    # Shopify calculators
    "calculate_bollard_signs": ["bollard", "signs", "quote", "calculator"],
    "calculate_construction_signs": ["construction", "signs", "quote", "calculator"],
    "calculate_corflute_insert_a_frame": ["corflute", "frame", "insert", "signs"],
    "calculate_custom_poster_printing": ["poster", "printing", "custom", "quote"],
    "calculate_custom_vinyl_stickers": ["vinyl", "stickers", "custom", "quote"],
    "calculate_economical_business_cards_shopify": ["business cards", "economical", "cheap", "quote"],
    "calculate_election_signs": ["election", "signs", "corflute", "quote"],
    "calculate_folded_flyers_shopify": ["flyer", "folded", "brochure", "quote"],
    "calculate_luxury_classic_pull_up_banners": ["banner", "pull up", "luxury", "stand"],
    "calculate_metal_face_a_frame": ["metal", "frame", "face", "signs"],
    "calculate_notepads_a4": ["notepad", "a4", "pad", "quote"],
    "calculate_notepads_a5": ["notepad", "a5", "pad", "quote"],
    "calculate_notepads_a6": ["notepad", "a6", "pad", "quote"],
    "calculate_premium_bookmarks": ["bookmark", "premium", "quote"],
    "calculate_premium_business_cards_shopify": ["business cards", "premium", "luxury", "quote"],
    "calculate_printed_letterheads": ["letterhead", "stationery", "printed", "quote"],
    "calculate_saddle_stitch_books": ["booklet", "saddle stitch", "stapled", "book"],
    "calculate_selfie_frames": ["selfie", "frame", "photo", "instagram"],
    "calculate_spiral_bound_books": ["spiral", "book", "bound", "quote"],
    "calculate_spiral_bound_books_shopify": ["spiral", "book", "bound", "shopify"],
    "calculate_stackable_cubes": ["cube", "stackable", "display", "quote"],
    "calculate_strut_cards_a3": ["strut", "card", "a3", "easel"],
    "calculate_strut_cards_a4": ["strut", "card", "a4", "easel"],
    "calculate_wire_bound_books_shopify": ["wire", "book", "bound", "quote"],
    "calculate_with_compliments_slips": ["compliment slip", "with compliments", "stationery"],
    
    # GOD calculators
    "calculate_god_flyers": ["flyer", "god", "database", "digital", "quote"],
    "calculate_god_letterheads": ["letterhead", "god", "database", "stationery", "quote"],
    "calculate_god_perfect_bound_books": ["perfect bound", "book", "god", "database", "quote"]
}


@calculator_test_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    log_server_message('Calculator test health check')
    return jsonify({"status": "healthy", "message": "Calculator Test Dashboard Ready"})


@calculator_test_bp.route('/logs', methods=['GET'])
def get_logs():
    """Get recent server logs"""
    return jsonify({"logs": list(server_logs)})


@calculator_test_bp.route('/test/discovery', methods=['POST'])
def test_discovery():
    """
    Test if calculator can be discovered via search_tools()
    
    Tests multiple keywords to simulate AI agent behavior
    """
    data = request.json
    calculator_name = data.get('calculator')
    keywords = data.get('keywords', CALCULATOR_KEYWORDS.get(calculator_name, []))
    
    log_server_message(f'Discovery test started for: {calculator_name}')
    
    if not calculator_name:
        log_server_message('Discovery test failed: No calculator specified', 'ERROR')
        return jsonify({"success": False, "error": "No calculator specified"}), 400
    
    try:
        found_count = 0
        search_results = []
        
        # Test each keyword
        for keyword in keywords:
            search_response = search_tools(keyword)
            tools = search_response.get("tools", []) if isinstance(search_response, dict) else []
            
            # Check if calculator found
            for tool in tools:
                if tool.get("name") == calculator_name:
                    found_count += 1
                    search_results.append({
                        "keyword": keyword,
                        "found": True
                    })
                    break
            else:
                search_results.append({
                    "keyword": keyword,
                    "found": False
                })
        
        success = found_count > 0
        
        log_server_message(f'Discovery test completed for {calculator_name}: {"PASS" if success else "FAIL"} ({found_count}/{len(keywords)} keywords)')
        
        return jsonify({
            "success": success,
            "calculator": calculator_name,
            "search_count": found_count,
            "total_keywords": len(keywords),
            "details": search_results
        })
        
    except Exception as e:
        log_server_message(f'Discovery test error for {calculator_name}: {str(e)}', 'ERROR')
        return jsonify({
            "success": False,
            "calculator": calculator_name,
            "error": str(e)
        }), 500


@calculator_test_bp.route('/test/schema', methods=['POST'])
def test_schema():
    """
    Test if calculator has valid schema with parameters
    """
    data = request.json
    calculator_name = data.get('calculator')
    
    log_server_message(f'Schema test started for: {calculator_name}')
    
    if not calculator_name:
        log_server_message('Schema test failed: No calculator specified', 'ERROR')
        return jsonify({"success": False, "error": "No calculator specified"}), 400
    
    try:
        # Get tool schema
        schema_response = get_tool_schema(calculator_name)
        
        # Check if schema exists and has parameters
        if not schema_response:
            return jsonify({
                "success": False,
                "calculator": calculator_name,
                "error": "No schema returned"
            })
        
        # Extract parameters (handle different schema formats)
        parameters = schema_response.get("parameters", schema_response.get("input_schema", {}))
        
        # Handle two formats:
        # 1. Anthropic format: {"properties": {...}, "required": [...]}
        # 2. Simple format: {"param_name": {...}, ...}
        if "properties" in parameters:
            properties = parameters.get("properties", {})
            required = parameters.get("required", [])
        else:
            # Simple format - parameters ARE the properties
            properties = {k: v for k, v in parameters.items() if isinstance(v, dict) and "type" in v}
            required = [k for k, v in properties.items() if v.get("required", False)]
        
        param_count = len(properties)
        required_count = len(required)
        
        success = param_count > 0
        
        log_server_message(f'Schema test completed for {calculator_name}: {"PASS" if success else "FAIL"} ({param_count} params)')
        
        return jsonify({
            "success": success,
            "calculator": calculator_name,
            "param_count": param_count,
            "required_count": required_count,
            "parameters": list(properties.keys()),
            "required": required,
            "schema": schema_response
        })
        
    except Exception as e:
        log_server_message(f'Schema test error for {calculator_name}: {str(e)}', 'ERROR')
        return jsonify({
            "success": False,
            "calculator": calculator_name,
            "error": str(e)
        }), 500


@calculator_test_bp.route('/test/requirements', methods=['POST'])
def test_requirements():
    """
    Test if calculator has enum guidance for AI
    """
    data = request.json
    calculator_name = data.get('calculator')
    
    log_server_message(f'Requirements test started for: {calculator_name}')
    
    if not calculator_name:
        log_server_message('Requirements test failed: No calculator specified', 'ERROR')
        return jsonify({"success": False, "error": "No calculator specified"}), 400
    
    try:
        # Get tool schema
        schema_response = get_tool_schema(calculator_name)
        
        if not schema_response:
            return jsonify({
                "success": False,
                "calculator": calculator_name,
                "error": "No schema returned"
            })
        
        # Extract parameters
        parameters = schema_response.get("parameters", schema_response.get("input_schema", {}))
        
        # Handle two formats:
        # 1. Anthropic format: {"properties": {...}}
        # 2. Simple format: {"param_name": {...}}
        if "properties" in parameters:
            properties = parameters.get("properties", {})
        else:
            # Simple format - parameters ARE the properties
            properties = {k: v for k, v in parameters.items() if isinstance(v, dict) and "type" in v}
        
        # Check for enum guidance
        params_with_enums = 0
        params_without_enums = []
        
        for param_name, param_def in properties.items():
            if "enum" in param_def:
                params_with_enums += 1
            else:
                params_without_enums.append(param_name)
        
        total_params = len(properties)
        success = total_params > 0 and params_with_enums > 0
        
        log_server_message(f'Requirements test completed for {calculator_name}: {"PASS" if success else "FAIL"} ({params_with_enums}/{total_params} params with enums)')
        
        return jsonify({
            "success": success,
            "calculator": calculator_name,
            "params_with_enums": params_with_enums,
            "total_params": total_params,
            "params_without_enums": params_without_enums
        })
        
    except Exception as e:
        log_server_message(f'Requirements test error for {calculator_name}: {str(e)}', 'ERROR')
        return jsonify({
            "success": False,
            "calculator": calculator_name,
            "error": str(e)
        }), 500


@calculator_test_bp.route('/test/execution', methods=['POST'])
def test_execution():
    """
    Test if calculator is registered and callable
    """
    data = request.json
    calculator_name = data.get('calculator')
    
    log_server_message(f'Execution test started for: {calculator_name}')
    
    if not calculator_name:
        log_server_message('Execution test failed: No calculator specified', 'ERROR')
        return jsonify({"success": False, "error": "No calculator specified"}), 400
    
    try:
        # Import tool registry and meta tools
        from tools.registry import ToolRegistry
        from tools.implementations.meta_tools import get_tool_schema
        
        registry = ToolRegistry()
        
        # Check if tool is registered
        if calculator_name not in registry.tools:
            log_server_message(f'Execution test FAIL for {calculator_name}: Not in registry', 'ERROR')
            return jsonify({
                "success": False,
                "calculator": calculator_name,
                "error": "Tool not registered in ToolRegistry"
            })
        
        # Get tool schema (SAME AS SCHEMA TEST - this works correctly!)
        schema_response = get_tool_schema(calculator_name)
        
        if not schema_response or not schema_response.get("success"):
            log_server_message(f'Execution test FAIL for {calculator_name}: Schema retrieval failed', 'ERROR')
            return jsonify({
                "success": False,
                "calculator": calculator_name,
                "error": "Failed to retrieve schema"
            })
        
        # Extract parameters (handle different schema formats)
        parameters = schema_response.get("parameters", schema_response.get("input_schema", {}))
        
        # Handle two formats:
        # 1. Anthropic format: {"properties": {...}, "required": [...]}
        # 2. Simple format: {"param_name": {...}, ...}
        if "properties" in parameters:
            properties = parameters.get("properties", {})
        else:
            # Simple format - parameters ARE the properties
            properties = {k: v for k, v in parameters.items() if isinstance(v, dict) and "type" in v}
        
        param_count = len(properties)
        
        if param_count == 0:
            log_server_message(f'Execution test FAIL for {calculator_name}: No parameters found', 'ERROR')
            return jsonify({
                "success": False,
                "calculator": calculator_name,
                "error": "Schema has no parameter definitions"
            })
        
        # ACTUAL EXECUTION - Execute calculator with sample parameters (SAME AS AI USES)
        def get_sample_params(calc_name: str, test_number: int = 1) -> dict:
            """Get comprehensive, realistic sample parameters based on calculator type
            
            Args:
                calc_name: Name of the calculator
                test_number: 1 or 2 for different test scenarios
            
            Returns 2 COMPREHENSIVE test scenarios per calculator with ALL parameters
            """
            name_lower = calc_name.lower()
            
            # FLYERS - 2 comprehensive tests
            if calc_name == "calculate_flyers":
                if test_number == 1:
                    return {
                        "quantity": 1000,
                        "width": 210,
                        "height": 297,
                        "stock_gsm": 170,
                        "print_mode": "double_sided",
                        "cello_type": "gloss_both_sides",
                        "folded": False
                    }
                else:
                    return {
                        "quantity": 5000,
                        "width": 99,
                        "height": 210,
                        "stock_gsm": 250,
                        "print_mode": "single_sided",
                        "cello_type": "matt_front_only",
                        "folded": True
                    }
            
            # BUSINESS CARDS - 2 comprehensive tests
            if calc_name == "calculate_business_cards":
                if test_number == 1:
                    return {
                        "quantity": 500,
                        "finish_size": "90x55mm",
                        "stock_type": "standard",
                        "print_type": "double_sided",
                        "cello_type": "gloss_both_sides"
                    }
                else:
                    return {
                        "quantity": 2000,
                        "finish_size": "85x55mm",
                        "stock_type": "premium",
                        "print_type": "single_sided",
                        "cello_type": "matt_both_sides"
                    }
            
            # PERFECT BOUND BOOKS - 2 comprehensive tests
            if "perfect_bound" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 100,
                        "total_pages": 120,
                        "cover_stock_gsm": 300,
                        "internal_stock_gsm": 128,
                        "finish_size": "A4",
                        "cover_cello": "gloss",
                        "internal_print": "colour"
                    }
                else:
                    return {
                        "quantity": 500,
                        "total_pages": 200,
                        "cover_stock_gsm": 350,
                        "internal_stock_gsm": 150,
                        "finish_size": "A5",
                        "cover_cello": "matt",
                        "internal_print": "black_and_white"
                    }
            
            # CORFLUTE SIGNS - 2 comprehensive tests
            if "corflute_sign" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 50,
                        "width": 600,
                        "height": 900,
                        "thickness": "5mm",
                        "print_sides": "single_sided",
                        "corner_type": "rounded",
                        "holes": True
                    }
                else:
                    return {
                        "quantity": 200,
                        "width": 900,
                        "height": 1200,
                        "thickness": "3mm",
                        "print_sides": "double_sided",
                        "corner_type": "square",
                        "holes": False
                    }
            
            # BOOKLETS - 2 comprehensive tests
            if calc_name == "calculate_booklets":
                if test_number == 1:
                    return {
                        "quantity": 250,
                        "total_pages": 16,
                        "cover_stock_gsm": 250,
                        "internal_stock_gsm": 128,
                        "finish_size": "A4",
                        "binding": "saddle_stitch",
                        "cover_cello": "gloss"
                    }
                else:
                    return {
                        "quantity": 1000,
                        "total_pages": 32,
                        "cover_stock_gsm": 300,
                        "internal_stock_gsm": 150,
                        "finish_size": "A5",
                        "binding": "saddle_stitch",
                        "cover_cello": "matt"
                    }
            
            # SADDLE STITCH BOOKS - 2 comprehensive tests
            if "saddle_stitch" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 100,
                        "total_pages": 24,
                        "cover_stock_gsm": 300,
                        "internal_stock_gsm": 128,
                        "finish_size": "A4",
                        "cover_cello": "gloss",
                        "internal_print": "colour"
                    }
                else:
                    return {
                        "quantity": 500,
                        "total_pages": 48,
                        "cover_stock_gsm": 350,
                        "internal_stock_gsm": 150,
                        "finish_size": "A5",
                        "cover_cello": "none",
                        "internal_print": "black_and_white"
                    }
            
            # SPIRAL BOUND BOOKS - 2 comprehensive tests
            if "spiral_bound" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 50,
                        "total_pages": 80,
                        "cover_stock_gsm": 300,
                        "internal_stock_gsm": 128,
                        "finish_size": "A4",
                        "cover_cello": "gloss",
                        "spiral_colour": "black",
                        "internal_print": "colour"
                    }
                else:
                    return {
                        "quantity": 250,
                        "total_pages": 150,
                        "cover_stock_gsm": 350,
                        "internal_stock_gsm": 150,
                        "finish_size": "A5",
                        "cover_cello": "matt",
                        "spiral_colour": "white",
                        "internal_print": "black_and_white"
                    }
            
            # BOLLARD SIGNS - 2 comprehensive tests
            if "bollard" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 100,
                        "material": "3mm Corflute",
                        "size": "270mm W x 1000mm H - Three Sided",
                        "artworks": "1"
                    }
                else:
                    return {
                        "quantity": 500,
                        "material": "5mm Corflute",
                        "size": "155mm W x 1800mm H - Four Sided",
                        "artworks": "max"
                    }
            
            # STACKABLE CUBES - 2 comprehensive tests
            if "stackable_cube" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 250,
                        "artworks": "1",
                        "material": "3mm Corflute",
                        "cube_size": "Medium 400mm x 400mm"
                    }
                else:
                    return {
                        "quantity": 1000,
                        "artworks": "max",
                        "material": "5mm Corflute",
                        "cube_size": "X-Large 580mm x 580mm"
                    }
            
            # ELECTION SIGNS - 2 comprehensive tests
            if "election" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 500,
                        "size": "600mm x 900mm",
                        "thickness": "3mm",
                        "eyelet_placement": "4_corners",
                        "cut_to_shape": False,
                        "artworks": 1
                    }
                else:
                    return {
                        "quantity": 2000,
                        "size": "900mm x 1200mm",
                        "thickness": "5mm",
                        "eyelet_placement": "all_sides",
                        "cut_to_shape": True,
                        "artworks": "max"
                    }
            
            # SELFIE FRAMES - 2 comprehensive tests
            if "selfie_frame" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 100,
                        "size": "600mm x 900mm",
                        "material": "3mm Corflute",
                        "cut_out_size": "custom",
                        "artworks": 1
                    }
                else:
                    return {
                        "quantity": 500,
                        "size": "900mm x 1200mm",
                        "material": "5mm Corflute",
                        "cut_out_size": "standard",
                        "artworks": "max"
                    }
            
            # CONSTRUCTION SIGNS - 2 comprehensive tests
            if "construction" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 50,
                        "size": "600mm x 900mm",
                        "thickness": "5mm",
                        "print_sides": "single_sided",
                        "mounting": "holes",
                        "artworks": 1
                    }
                else:
                    return {
                        "quantity": 200,
                        "size": "1200mm x 1800mm",
                        "thickness": "3mm",
                        "print_sides": "double_sided",
                        "mounting": "stakes",
                        "artworks": "max"
                    }
            
            # STRUT CARDS A3 - 2 comprehensive tests
            if "strut_cards_a3" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 250,
                        "finish_size": "A3",
                        "stock_gsm": 350,
                        "cello_type": "gloss_both_sides",
                        "artworks": 1
                    }
                else:
                    return {
                        "quantity": 1000,
                        "finish_size": "A3",
                        "stock_gsm": 400,
                        "cello_type": "matt_both_sides",
                        "artworks": "max"
                    }
            
            # STRUT CARDS A4 - 2 comprehensive tests
            if "strut_cards_a4" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 500,
                        "finish_size": "A4",
                        "stock_gsm": 350,
                        "cello_type": "gloss_front_only",
                        "artworks": 1
                    }
                else:
                    return {
                        "quantity": 2000,
                        "finish_size": "A4",
                        "stock_gsm": 400,
                        "cello_type": "matt_front_only",
                        "artworks": "max"
                    }
            
            # PREMIUM BOOKMARKS - 2 comprehensive tests
            if "bookmark" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 1000,
                        "finish_size": "50mm x 200mm",
                        "stock_gsm": 350,
                        "cello_type": "gloss_both_sides",
                        "print_type": "double_sided",
                        "artworks": 1
                    }
                else:
                    return {
                        "quantity": 5000,
                        "finish_size": "60mm x 210mm",
                        "stock_gsm": 400,
                        "cello_type": "matt_both_sides",
                        "print_type": "single_sided",
                        "artworks": "max"
                    }
            
            # NOTEPADS A4 - 2 comprehensive tests
            if "notepads_a4" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 100,
                        "finish_size": "A4",
                        "leaves_per_pad": "50",
                        "print_type": "Colour 1 sided",
                        "stock_type": "Uncoated Bond 80GSM",
                        "artworks": 1
                    }
                else:
                    return {
                        "quantity": 500,
                        "finish_size": "A4",
                        "leaves_per_pad": "100",
                        "print_type": "Black & White 2 sided",
                        "stock_type": "Revive 100% Recycled 80GSM Bond",
                        "artworks": "max"
                    }
            
            # PRINTED LETTERHEADS - 2 comprehensive tests
            if "letterhead" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 500,
                        "finish_size": "A4",
                        "stock_gsm": 100,
                        "print_type": "single_sided",
                        "stock_type": "uncoated",
                        "artworks": 1
                    }
                else:
                    return {
                        "quantity": 2000,
                        "finish_size": "A4",
                        "stock_gsm": 120,
                        "print_type": "double_sided",
                        "stock_type": "satin",
                        "artworks": "max"
                    }
            
            # WITH COMPLIMENTS SLIPS - 2 comprehensive tests
            if "compliments" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 250,
                        "finish_size": "DL",
                        "stock_gsm": 170,
                        "print_type": "single_sided",
                        "stock_type": "standard",
                        "artworks": 1
                    }
                else:
                    return {
                        "quantity": 1000,
                        "finish_size": "DL",
                        "stock_gsm": 200,
                        "print_type": "double_sided",
                        "stock_type": "premium",
                        "artworks": "max"
                    }
            
            # NOTEPADS A5 - 2 comprehensive tests
            if "notepads_a5" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 150,
                        "finish_size": "A5",
                        "leaves_per_pad": "25",
                        "print_type": "Colour 2 sided",
                        "stock_type": "Uncoated Bond 90GSM",
                        "artworks": 1
                    }
                else:
                    return {
                        "quantity": 750,
                        "finish_size": "A5",
                        "leaves_per_pad": "100",
                        "print_type": "Black & White 1 sided",
                        "stock_type": "Uncoated Bond 100GSM",
                        "artworks": "max"
                    }
            
            # NOTEPADS A6 - 2 comprehensive tests
            if "notepads_a6" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 200,
                        "finish_size": "A6",
                        "leaves_per_pad": "15",
                        "print_type": "Colour 1 sided",
                        "stock_type": "Uncoated Bond 80GSM",
                        "artworks": 1
                    }
                else:
                    return {
                        "quantity": 1000,
                        "finish_size": "A6",
                        "leaves_per_pad": "50",
                        "print_type": "Black & White 2 sided",
                        "stock_type": "Revive 100% Recycled 80GSM Bond",
                        "artworks": "max"
                    }
            
            # LUXURY PULL UP BANNERS - 2 comprehensive tests
            if "luxury" in name_lower and "pull_up" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 100,
                        "artworks": "1",
                        "base_colour": "Silver",
                        "size": "850mm W x 2000mm H"
                    }
                else:
                    return {
                        "quantity": 500,
                        "artworks": "max",
                        "base_colour": "Black",
                        "size": "850mm W x 1400mm H Shopping Center"
                    }
            
            # CORFLUTE INSERT A-FRAME - 2 comprehensive tests
            if "a_frame" in name_lower or "aframe" in name_lower:
                if test_number == 1:
                    return {
                        "quantity": 100,
                        "size": "600mm(W) x 900mm(H)",
                        "material": "3mm Corflute",
                        "inserts": 2,
                        "artworks": 1
                    }
                else:
                    return {
                        "quantity": 500,
                        "size": "600mm(W) x 900mm(H)",
                        "material": "5mm Corflute",
                        "inserts": 4,
                        "artworks": "max"
                    }
            
            # Default fallback with quantity
            return {"quantity": 100 if test_number == 1 else 500}
        
        # RUN 2 COMPREHENSIVE TESTS for each calculator
        test_results = []
        
        for test_num in [1, 2]:
            # Get sample parameters for this test scenario
            sample_params = get_sample_params(calculator_name, test_num)
            log_server_message(f'Executing {calculator_name} TEST {test_num} with params: {sample_params}')
            
            try:
                # Execute tool through registry (SAME AS AI USES)
                execution_result = registry.execute_tool(
                    tool_name=calculator_name,
                    **sample_params
                )
                
                # Verify execution was successful
                if not execution_result.get("success"):
                    error_msg = execution_result.get('error', 'Unknown error')
                    log_server_message(f'Execution test {test_num} FAIL for {calculator_name}: {error_msg}', 'ERROR')
                    test_results.append({
                        "test_number": test_num,
                        "success": False,
                        "error": f"Execution failed: {error_msg}",
                        "sample_params": sample_params
                    })
                    continue
                
                # Verify quote result structure
                result_data = execution_result.get("result", {})
                has_valid_quote = (
                    "total_price" in result_data and
                    "unit_price" in result_data and
                    isinstance(result_data["total_price"], (int, float)) and
                    isinstance(result_data["unit_price"], (int, float))
                )
                
                if not has_valid_quote:
                    log_server_message(f'Execution test {test_num} FAIL for {calculator_name}: Invalid quote structure', 'ERROR')
                    test_results.append({
                        "test_number": test_num,
                        "success": False,
                        "error": "Invalid quote structure (missing total_price or unit_price)",
                        "sample_params": sample_params,
                        "result": result_data
                    })
                    continue
                
                # SUCCESS - Calculator executed and returned valid quote
                log_server_message(f'Execution test {test_num} PASS for {calculator_name}: Quote=${result_data["total_price"]:.2f}')
                
                test_results.append({
                    "test_number": test_num,
                    "success": True,
                    "executed": True,
                    "sample_params": sample_params,
                    "quote": {
                        "total_price": result_data["total_price"],
                        "unit_price": result_data["unit_price"],
                        "quantity": result_data.get("quantity", sample_params.get("quantity")),
                        "breakdown": result_data.get("breakdown", {})
                    }
                })
                
            except Exception as exec_error:
                log_server_message(f'Execution test {test_num} EXCEPTION for {calculator_name}: {str(exec_error)}', 'ERROR')
                test_results.append({
                    "test_number": test_num,
                    "success": False,
                    "error": f"Execution exception: {str(exec_error)}",
                    "sample_params": sample_params
                })
        
        # Determine overall success (both tests must pass)
        all_tests_passed = all(t["success"] for t in test_results)
        
        # Get platform from schema response
        platform = schema_response.get("platform", "calculator")
        
        return jsonify({
            "success": all_tests_passed,
            "calculator": calculator_name,
            "platform": platform,
            "tests_run": 2,
            "tests_passed": sum(1 for t in test_results if t["success"]),
            "test_results": test_results,
            "test_count": len(test_results)  # Added for UI display
        })
        
    except Exception as e:
        log_server_message(f'Execution test error for {calculator_name}: {str(e)}', 'ERROR')
        return jsonify({
            "success": False,
            "calculator": calculator_name,
            "error": str(e)
        }), 500


# Export for registration in main Flask app
__all__ = ['calculator_test_bp']
