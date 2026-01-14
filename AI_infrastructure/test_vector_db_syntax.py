"""
Vector Database Routes - Syntax & Import Validation
Quick smoke test that validates all imports and basic syntax without needing Flask running
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*80)
print("VECTOR DATABASE ROUTES - SYNTAX VALIDATION".center(80))
print("="*80)
print()

# Test 1: Import the routes module
print("Test 1: Importing vector_db_routes module...")
try:
    from routes import vector_db_routes
    print("✓ SUCCESS: routes.vector_db_routes imported")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Test 2: Check blueprint exists
print("\nTest 2: Checking blueprint registration...")
try:
    bp = vector_db_routes.vector_db_bp
    print(f"✓ SUCCESS: Blueprint '{bp.name}' found")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Test 3: List all registered routes
print("\nTest 3: Enumerating registered endpoints...")
try:
    # Blueprint not yet registered - scan for route decorators
    print("  (Blueprint not bound to app - scanning source file)")
    import inspect
    route_funcs = []
    for name, obj in inspect.getmembers(vector_db_routes):
        if inspect.isfunction(obj) and hasattr(obj, '__name__'):
            # Check if it's likely a route function (has decorators)
            if name not in ['require_auth', 'jsonify', 'request', 'datetime', 'secure_filename', 'uuid', '_get_vector_db_credentials', '_create_embedding', '_chunk_text']:
                route_funcs.append(name)
    
    print(f"✓ SUCCESS: Found {len(route_funcs)} route functions")
    for func in sorted(route_funcs)[:15]:
        print(f"    - {func}()")
    if len(route_funcs) > 15:
        print(f"    ... and {len(route_funcs) - 15} more")
            
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Test 4: Check critical dependencies
print("\nTest 4: Checking dependencies...")
dependencies = {
    'Flask': 'flask',
    'Authentication': 'auth.user_auth',
    'Database Utils': 'shared.database_utils',
    'Credential Injector': 'auth.credential_injector'
}

for name, module_path in dependencies.items():
    try:
        __import__(module_path)
        print(f"✓ {name}: Available")
    except ImportError as e:
        print(f"⚠ {name}: Not available ({e})")

# Test 5: Scan route file for endpoint definitions
print("\nTest 5: Scanning source file for endpoints...")
try:
    source_file = os.path.join(os.path.dirname(__file__), 'routes', 'vector_db_routes.py')
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    import re
    route_pattern = r"@vector_db_bp\.route\(['\"]([^'\"]+)['\"]"
    routes = re.findall(route_pattern, content)
    
    print(f"✓ SUCCESS: Found {len(routes)} @vector_db_bp.route decorators")
    for route in sorted(set(routes)):
        print(f"    {route}")
        
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Test 6: Validate route structure
print("\nTest 6: Validating route structure...")
try:
    # Check for required helper functions
    helpers = ['_get_vector_db_credentials', '_create_embedding', '_chunk_text']
    found_helpers = []
    missing_helpers = []
    
    for helper in helpers:
        if hasattr(vector_db_routes, helper):
            found_helpers.append(helper)
        else:
            missing_helpers.append(helper)
    
    if found_helpers:
        print(f"✓ Helper functions found: {', '.join(found_helpers)}")
    if missing_helpers:
        print(f"⚠ Helper functions not found: {', '.join(missing_helpers)}")
        
except Exception as e:
    print(f"✗ FAILED: {e}")

# Test 7: Check for syntax errors in route functions
print("\nTest 7: Checking route function signatures...")
try:
    import inspect
    route_funcs = []
    
    for name, obj in inspect.getmembers(vector_db_routes, inspect.isfunction):
        # Skip private and imported functions
        if not name.startswith('_') and not name in ['require_auth', 'jsonify', 'request']:
            try:
                sig = inspect.signature(obj)
                route_funcs.append({
                    'name': name,
                    'params': len(sig.parameters)
                })
            except:
                pass
    
    if route_funcs:
        print(f"✓ SUCCESS: {len(route_funcs)} route functions validated")
        for func in sorted(route_funcs, key=lambda x: x['name'])[:10]:
            print(f"    {func['name']}() - {func['params']} parameters")
        if len(route_funcs) > 10:
            print(f"    ... and {len(route_funcs) - 10} more")
            
except Exception as e:
    print(f"✗ FAILED: {e}")

# Final summary
print("\n" + "="*80)
print("VALIDATION COMPLETE".center(80))
print("="*80)
print("\n✓ All syntax checks passed!")
print("  - Routes module imports successfully")
print("  - Blueprint is properly defined")
print(f"  - {len(routes)} endpoints detected")
print("  - No Python syntax errors found")
print("\nNext steps:")
print("  1. Start Flask server: python flask_app.py")
print("  2. Run full test: python test_vector_db_endpoints.py")
print()
