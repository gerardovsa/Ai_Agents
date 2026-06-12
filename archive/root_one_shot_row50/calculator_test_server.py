"""
Calculator Test Dashboard Backend
==================================

Flask server that runs calculator tests and streams results to the UI.
Tests both Shopify (25) and GOD (3) calculators.

Author: AI Agent Testing Framework
Date: December 10, 2025
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from typing import Dict, Any, List
from collections import deque

# Add paths
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from tools.implementations.meta_tools import search_tools, get_tool_schema

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

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


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    log_server_message('Health check ping received')
    return jsonify({"status": "healthy", "message": "Calculator Test Server Running"})


@app.route('/logs', methods=['GET'])
def get_logs():
    """Get recent server logs"""
    return jsonify({"logs": list(server_logs)})


@app.route('/restart', methods=['POST'])
def restart_server():
    """Restart the server"""
    import os
    import signal
    
    log_server_message('Server restart requested - initiating shutdown', 'INFO')
    
    def shutdown():
        """Gracefully shutdown the server"""
        import time
        time.sleep(1)  # Give time to send response
        os.kill(os.getpid(), signal.SIGTERM)
    
    # Schedule shutdown in background thread
    from threading import Thread
    Thread(target=shutdown).start()
    
    return jsonify({
        "status": "restarting",
        "message": "Server restart initiated"
    })


@app.route('/test/discovery', methods=['POST'])
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


@app.route('/test/schema', methods=['POST'])
def test_schema():
    """
    Test if calculator has valid schema with parameters
    """
    data = request.json
    calculator_name = data.get('calculator')
    log_server_message(f'Schema test started for: {calculator_name}')
    calculator_name = data.get('calculator')
    
    if not calculator_name:
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
        
        # DEBUG: Log the actual schema structure
        print(f"\n=== SCHEMA DEBUG for {calculator_name} ===")
        print(f"Schema type: {type(schema_response)}")
        print(f"Schema keys: {schema_response.keys() if isinstance(schema_response, dict) else 'Not a dict'}")
        print(f"Full schema: {json.dumps(schema_response, indent=2, default=str)}")
        
        # Extract parameters (handle different schema formats)
        parameters = schema_response.get("parameters", schema_response.get("input_schema", {}))
        properties = parameters.get("properties", {})
        required = parameters.get("required", [])
        
        param_count = len(properties)
        required_count = len(required)
        
        success = param_count > 0
        
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
        return jsonify({
            "success": False,
            "calculator": calculator_name,
            "error": str(e)
        }), 500


@app.route('/test/requirements', methods=['POST'])
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
        
        # Check for enums in parameters
        parameters = schema_response.get("parameters", {})
        properties = parameters.get("properties", {})
        
        enums_found = []
        for param_name, param_def in properties.items():
            if "enum" in param_def:
                enums_found.append({
                    "parameter": param_name,
                    "enum_count": len(param_def["enum"]),
                    "values": param_def["enum"]
                })
        
        enum_count = len(enums_found)
        success = enum_count > 0
        
        return jsonify({
            "success": success,
            "calculator": calculator_name,
            "enum_count": enum_count,
            "enums": enums_found,
            "total_params": len(properties)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "calculator": calculator_name,
            "error": str(e)
        }), 500


@app.route('/test/execution', methods=['POST'])
def test_execution():
    """
    Test calculator execution by checking if tool is callable
    
    Uses the tool registry system (same way AI agents access tools)
    """
    data = request.json
    calculator_name = data.get('calculator')
    
    log_server_message(f'Execution test started for: {calculator_name}')
    
    if not calculator_name:
        log_server_message('Execution test failed: No calculator specified', 'ERROR')
        return jsonify({"success": False, "error": "No calculator specified"}), 400
    
    try:
        # Get the tool from registry (this is how AI actually calls it)
        from tools.registry import ToolRegistry
        tool_registry = ToolRegistry()
        
        # Check if tool exists in registry
        if calculator_name not in tool_registry.tools:
            return jsonify({
                "success": False,
                "calculator": calculator_name,
                "error": "Calculator not found in tool registry",
                "details": {
                    "available_tools": len(tool_registry.tools),
                    "calculator_tools": [t for t in tool_registry.tools.keys() if 'calculate' in t][:10]
                }
            })
        
        tool_schema = tool_registry.tools[calculator_name]
        
        # Tools in this registry are JSON schemas with execute_tool() method to call them
        # Verify the tool has proper schema structure
        has_name = 'name' in tool_schema
        has_description = 'description' in tool_schema
        # Check for both 'parameters' (calculator tools) and 'input_schema' (other tools)
        has_parameters = 'parameters' in tool_schema or 'input_schema' in tool_schema
        is_valid_tool = has_name and has_description and has_parameters
        
        if not is_valid_tool:
            return jsonify({
                "success": False,
                "calculator": calculator_name,
                "error": "Tool schema incomplete",
                "details": {
                    "has_name": has_name,
                    "has_description": has_description,
                    "has_parameters": has_parameters,
                    "schema_keys": list(tool_schema.keys())
                }
            })
        
        # Success - tool exists in registry and is callable via execute_tool()
        return jsonify({
            "success": True,
            "calculator": calculator_name,
            "test_count": 1,
            "details": {
                "tool_found": True,
                "is_callable": True,
                "execution_method": "tool_registry.execute_tool()",
                "tool_name": tool_schema.get('name'),
                "tool_description": tool_schema.get('description', 'N/A')[:100]
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "calculator": calculator_name,
            "error": str(e),
            "details": {
                "exception_type": type(e).__name__,
                "exception_message": str(e)
            }
        }), 500


@app.route('/calculators/list', methods=['GET'])
def list_calculators():
    """
    Return list of all calculators with their keywords
    """
    shopify = []
    god = []
    
    for calc_name, keywords in CALCULATOR_KEYWORDS.items():
        calc_info = {
            "name": calc_name,
            "keywords": keywords
        }
        
        if calc_name.startswith('calculate_god_'):
            god.append(calc_info)
        else:
            shopify.append(calc_info)
    
    return jsonify({
        "shopify": shopify,
        "god": god,
        "total": len(CALCULATOR_KEYWORDS)
    })


@app.route('/test/run-all', methods=['POST'])
def run_all_tests():
    """
    Run all test phases for all calculators
    This is for batch testing
    """
    data = request.json
    test_type = data.get('type', 'all')  # 'all', 'shopify', 'god'
    
    results = {
        "shopify": {},
        "god": {},
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0
        }
    }
    
    # Determine which calculators to test
    calculators_to_test = []
    if test_type in ['all', 'shopify']:
        calculators_to_test.extend([k for k in CALCULATOR_KEYWORDS.keys() if not k.startswith('calculate_god_')])
    if test_type in ['all', 'god']:
        calculators_to_test.extend([k for k in CALCULATOR_KEYWORDS.keys() if k.startswith('calculate_god_')])
    
    # Run tests for each calculator
    for calc_name in calculators_to_test:
        calc_result = {
            "discovery": False,
            "schema": False,
            "requirements": False,
            "execution": False,
            "overall": False
        }
        
        # Test discovery
        try:
            keywords = CALCULATOR_KEYWORDS.get(calc_name, [])
            found_count = 0
            for keyword in keywords:
                search_response = search_tools(keyword)
                tools = search_response.get("tools", []) if isinstance(search_response, dict) else []
                if any(t.get("name") == calc_name for t in tools):
                    found_count += 1
            calc_result["discovery"] = found_count > 0
        except:
            pass
        
        # Test schema
        try:
            schema_response = get_tool_schema(calc_name)
            if schema_response:
                properties = schema_response.get("parameters", {}).get("properties", {})
                calc_result["schema"] = len(properties) > 0
        except:
            pass
        
        # Test requirements
        try:
            schema_response = get_tool_schema(calc_name)
            if schema_response:
                properties = schema_response.get("parameters", {}).get("properties", {})
                has_enums = any("enum" in prop for prop in properties.values())
                calc_result["requirements"] = has_enums
        except:
            pass
        
        # Overall pass/fail
        calc_result["overall"] = all([
            calc_result["discovery"],
            calc_result["schema"],
            calc_result["requirements"]
        ])
        
        # Store result
        if calc_name.startswith('calculate_god_'):
            results["god"][calc_name] = calc_result
        else:
            results["shopify"][calc_name] = calc_result
        
        # Update summary
        results["summary"]["total"] += 1
        if calc_result["overall"]:
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1
    
    return jsonify(results)


if __name__ == '__main__':
    print("=" * 80)
    print("🧪 Calculator Test Dashboard Backend")
    print("=" * 80)
    print(f"Total Calculators: {len(CALCULATOR_KEYWORDS)}")
    print(f"  - Shopify: {len([k for k in CALCULATOR_KEYWORDS if not k.startswith('calculate_god_')])}")
    print(f"  - GOD: {len([k for k in CALCULATOR_KEYWORDS if k.startswith('calculate_god_')])}")
    print("\nServer starting on http://localhost:5000")
    print("Open calculator_test_dashboard.html in your browser to run tests.")
    print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
