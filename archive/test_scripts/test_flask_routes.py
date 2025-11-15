"""
Test Flask Routes - Verify all routes load correctly
Checks that Flask app initializes with all Synergy-related endpoints
"""

import sys
import os
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

print("=" * 80)
print("FLASK ROUTES VERIFICATION TEST")
print("=" * 80)

try:
    # Import Flask app
    print("\n1. Importing Flask app...")
    from flask_app import app
    print("   Flask app import: PASS")
    
    # Get all registered routes
    print("\n2. Checking registered routes...")
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
            'path': str(rule)
        })
    
    print(f"   Total routes registered: {len(routes)}")
    
    # Check for Synergy-related routes
    print("\n3. Verifying Synergy-related routes...")
    
    synergy_routes = {
        'synergy_sessions': '/api/synergy/sessions',
        'synergy_create': '/api/synergy/create',
        'synergy_update': '/api/synergy/<session_id>',
        'synergy_delete': '/api/synergy/<session_id>',
        'threads_details': '/api/threads/details',  # New endpoint
        'kanban': '/api/kanban',
    }
    
    found_routes = {}
    for route in routes:
        path = route['path']
        for key, expected_path in synergy_routes.items():
            if expected_path in path or key in route['endpoint']:
                found_routes[key] = {
                    'path': path,
                    'methods': route['methods'],
                    'endpoint': route['endpoint']
                }
    
    print(f"\n   Synergy-related routes found:")
    for key, route_info in found_routes.items():
        print(f"      {key:25} {route_info['methods']:12} {route_info['path']}")
    
    # Check specifically for the new threads/details endpoint
    threads_details_found = any('/api/threads/details' in r['path'] for r in routes)
    print(f"\n   /api/threads/details endpoint: {'FOUND' if threads_details_found else 'NOT FOUND'}")
    
    # Check for thread-related routes
    print("\n4. Verifying thread-related routes...")
    thread_routes = [r for r in routes if 'thread' in r['endpoint'].lower()]
    print(f"   Thread routes found: {len(thread_routes)}")
    for route in thread_routes[:10]:  # Show first 10
        print(f"      {route['methods']:12} {route['path']}")
    
    # Check for synergy routes
    print("\n5. Verifying synergy routes...")
    synergy_routes_list = [r for r in routes if 'synergy' in r['endpoint'].lower()]
    print(f"   Synergy routes found: {len(synergy_routes_list)}")
    for route in synergy_routes_list:
        print(f"      {route['methods']:12} {route['path']}")
    
    # Check for kanban routes
    print("\n6. Verifying kanban routes...")
    kanban_routes_list = [r for r in routes if 'kanban' in r['endpoint'].lower()]
    print(f"   Kanban routes found: {len(kanban_routes_list)}")
    for route in kanban_routes_list:
        print(f"      {route['methods']:12} {route['path']}")
    
    print("\n7. SUMMARY")
    print("=" * 80)
    
    checks = {
        'Flask app loads': True,
        'Routes registered': len(routes) > 0,
        'Thread routes present': len(thread_routes) > 0,
        'Synergy routes present': len(synergy_routes_list) > 0,
        'Kanban routes present': len(kanban_routes_list) > 0,
        '/api/threads/details found': threads_details_found,
    }
    
    for check_name, result in checks.items():
        status = "PASS" if result else "FAIL"
        icon = "" if result else ""
        print(f"   {check_name:35} {status} {icon}")
    
    all_passed = all(checks.values())
    print(f"\n   Flask route verification: {'PASS - ALL ROUTES LOADED' if all_passed else 'FAIL - ISSUES FOUND'}")
    
except Exception as e:
    print(f"\n   ERROR: {e}")
    import traceback
    traceback.print_exc()
    print(f"\n   Flask route verification: FAIL")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
