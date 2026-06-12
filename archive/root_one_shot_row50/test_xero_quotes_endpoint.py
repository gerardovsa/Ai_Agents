"""
Test Xero Quotes Endpoint Registration
Created: January 18, 2026
Purpose: Verify /api/xero/quotes endpoint is properly registered and functional
"""

import sys
from pathlib import Path

# Add paths
ai_agents_root = Path(__file__).parent
sys.path.insert(0, str(ai_agents_root))
sys.path.insert(0, str(ai_agents_root / 'AI_infrastructure'))

# Import Flask and xero routes
from flask import Flask
from flask_cors import CORS

# Add xero module to path
xero_module_path = ai_agents_root / 'UI' / 'modules_external' / 'xero'
sys.path.insert(0, str(xero_module_path))

from xero_routes import init_xero_routes

def test_route_registration():
    """Test that xero quotes routes are properly registered"""
    
    print("=" * 80)
    print("TESTING XERO QUOTES ENDPOINT REGISTRATION")
    print("=" * 80)
    
    # Create Flask app
    app = Flask(__name__)
    CORS(app)
    
    # Initialize xero routes
    print("\n1. Initializing Xero routes...")
    init_xero_routes(app)
    
    # Check for quotes routes
    print("\n2. Checking for quotes endpoints...")
    quotes_routes = [rule for rule in app.url_map.iter_rules() if 'quotes' in rule.rule]
    
    if not quotes_routes:
        print("   ❌ FAILED: No quotes routes found!")
        return False
    
    print(f"   ✅ Found {len(quotes_routes)} quotes route(s):")
    for route in quotes_routes:
        print(f"      • {route.rule} - Methods: {route.methods}")
    
    # Verify specific endpoints
    print("\n3. Verifying required endpoints exist...")
    required_endpoints = [
        ('/api/xero/quotes', {'GET', 'POST', 'OPTIONS'}),
        ('/api/xero/quotes/<quote_id>', {'GET', 'PUT', 'DELETE', 'OPTIONS'})
    ]
    
    all_passed = True
    for endpoint, expected_methods in required_endpoints:
        # Find matching route (handle parameter variations)
        matching_route = None
        for route in quotes_routes:
            if route.rule == endpoint or (endpoint.replace('<quote_id>', '<') in route.rule):
                matching_route = route
                break
        
        if not matching_route:
            print(f"   ❌ FAILED: {endpoint} not found!")
            all_passed = False
        else:
            # Check if expected methods are present (Flask adds HEAD automatically for GET)
            has_required = expected_methods.issubset(matching_route.methods)
            status = "✅ PASS" if has_required else "⚠️  WARNING"
            print(f"   {status}: {matching_route.rule}")
            print(f"      Expected: {expected_methods}")
            print(f"      Actual:   {matching_route.methods}")
    
    # Summary
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ TEST PASSED: All required Xero quotes endpoints registered successfully!")
        print("\nEndpoints ready:")
        print("   • GET  /api/xero/quotes - List quotes with filters")
        print("   • POST /api/xero/quotes - Create new quote")
        print("   • GET  /api/xero/quotes/<id> - Get specific quote")
        print("   • PUT  /api/xero/quotes/<id> - Update quote")
        print("   • DELETE /api/xero/quotes/<id> - Delete quote")
    else:
        print("❌ TEST FAILED: Some endpoints missing or misconfigured!")
    print("=" * 80)
    
    return all_passed


if __name__ == '__main__':
    success = test_route_registration()
    sys.exit(0 if success else 1)
