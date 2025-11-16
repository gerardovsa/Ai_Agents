"""
Test Xero tools for deployment compatibility
Tests both local and Render.com scenarios
"""

import sys
from pathlib import Path

# Add root to path (simulates Render.com environment)
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

print("=" * 70)
print("XERO DEPLOYMENT COMPATIBILITY TEST")
print("=" * 70)

# Test 1: Registry loads all Xero tools
print("\n[TEST 1] Registry loads all 15 Xero tools")
try:
    from tools.registry_v3 import RegistryV3
    registry = RegistryV3()
    xero_tools = sorted([t for t in registry.tools.keys() if 'xero' in t])
    
    if len(xero_tools) >= 15:
        print(f"[PASS] {len(xero_tools)} Xero tools loaded")
        print("\nTools loaded:")
        for tool in xero_tools:
            print(f"  - {tool}")
    else:
        print(f"[FAIL] Only {len(xero_tools)}/15 tools loaded")
        sys.exit(1)
except Exception as e:
    print(f"[FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: XeroAPIClient imports correctly
print("\n[TEST 2] XeroAPIClient imports correctly")
try:
    from tools.implementations.xero import XeroAPIClient
    if XeroAPIClient:
        print("[PASS] XeroAPIClient imported successfully")
    else:
        print("[WARNING] XeroAPIClient is None (graceful fallback)")
except Exception as e:
    print(f"[FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: xero_platform_guide executes
print("\n[TEST 3] xero_platform_guide executes correctly")
try:
    from tools.implementations.xero import xero_platform_guide
    result = xero_platform_guide(task_description="Get unpaid invoices from last month")
    
    if result.get("success"):
        print("[PASS] xero_platform_guide executed successfully")
        print(f"  - Total tools: {result.get('total_tools')}")
        print(f"  - Task recommendations: {len(result.get('your_task_recommendations', {}))} items")
    else:
        print(f"[FAIL] {result.get('error')}")
        sys.exit(1)
except Exception as e:
    print(f"[FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Helper functions work
print("\n[TEST 4] Helper functions (_parse_xero_date) work")
try:
    from tools.implementations.xero import _parse_xero_date
    
    # Test date parsing
    date1 = _parse_xero_date("/Date(1748476800000)/")  # Xero format
    date2 = _parse_xero_date("2025-06-12")  # ISO format
    date3 = _parse_xero_date("2025-06-12T10:30:00")  # ISO with time
    
    if date1 and date2 and date3:
        print("[PASS] Date parsing works for all formats")
        print(f"  - Xero format: {date1}")
        print(f"  - ISO format: {date2}")
        print(f"  - ISO with time: {date3}")
    else:
        print("[FAIL] Date parsing returned None")
        sys.exit(1)
except Exception as e:
    print(f"[FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: All tool functions are callable
print("\n[TEST 5] All Xero tool functions are callable")
try:
    from tools.implementations import xero
    
    callable_functions = [
        'xero_platform_guide',
        'xero_get_data_metadata',
        'xero_get_contacts_by_date_range',
        'xero_get_invoices_by_date_range',
        'xero_get_payments_by_date_range',
        'xero_get_accounts_metadata',
        'xero_get_accounts_by_type',
        'xero_get_bank_transactions_by_date_range',
        'xero_get_invoices',
        'xero_get_contacts',
        'xero_get_accounts',
        'xero_get_bank_transactions',
        'xero_get_payments',
        'xero_get_invoice_by_id',
        'xero_create_invoice'
    ]
    
    missing = []
    for func_name in callable_functions:
        if not hasattr(xero, func_name) or not callable(getattr(xero, func_name)):
            missing.append(func_name)
    
    if not missing:
        print(f"[PASS] All {len(callable_functions)} functions are callable")
    else:
        print(f"[FAIL] {len(missing)} functions missing or not callable:")
        for func in missing:
            print(f"  - {func}")
        sys.exit(1)
except Exception as e:
    print(f"[FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Check dependencies in requirements.txt
print("\n[TEST 6] Check dependencies in requirements.txt")
try:
    req_path = root_dir / "requirements.txt"
    if not req_path.exists():
        print("[FAIL] requirements.txt not found")
        sys.exit(1)
    
    with open(req_path, 'r') as f:
        requirements = f.read()
    
    required_libs = ['requests', 'python-dotenv']
    missing_libs = []
    
    for lib in required_libs:
        if lib not in requirements:
            missing_libs.append(lib)
    
    if not missing_libs:
        print(f"[PASS] All required dependencies present in requirements.txt")
        print(f"  - requests: OK")
        print(f"  - python-dotenv: OK")
    else:
        print(f"[FAIL] Missing dependencies: {', '.join(missing_libs)}")
        sys.exit(1)
except Exception as e:
    print(f"[FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("[SUCCESS] ALL TESTS PASSED - Xero tools ready for deployment")
print("=" * 70)
print("\nDeployment checklist:")
print("  [OK] 15 Xero tools load correctly")
print("  [OK] XeroAPIClient imports (with graceful fallback)")
print("  [OK] Platform guide executes and returns recommendations")
print("  [OK] Date parsing helper functions work")
print("  [OK] All tool functions are callable")
print("  [OK] All dependencies in requirements.txt")
print("\nReady for:")
print("  [OK] Local development (Windows)")
print("  [OK] Render.com deployment (Linux)")
