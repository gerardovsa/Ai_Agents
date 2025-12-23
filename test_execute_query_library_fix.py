"""
Test execute_query_library handler fix
Verifies that execute_query_library now works through ToolUseAgent
"""
import sys
sys.path.insert(0, 'AI_infrastructure')

print("=" * 80)
print("TESTING: execute_query_library Handler Fix")
print("=" * 80)

try:
    # Import with module path (hyphen in folder name requires sys.path manipulation)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "inhouse_wrapper",
        "UI/modules_external/inhouse-print/implementations/inhouse_wrapper.py"
    )
    inhouse_wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inhouse_wrapper)
    _get_agent = inhouse_wrapper._get_agent
    
    print("\n[1/3] Getting ToolUseAgent instance...")
    agent = _get_agent()
    print("✅ Agent initialized")
    
    print("\n[2/3] Testing execute_query_library (should work now)...")
    result = agent._execute_client_tool('execute_query_library', {
        'query_name': 'sales_trend_by_month',
        'parameters': {'months': 3}
    })
    
    print("\n[3/3] Checking result...")
    if result.get('success'):
        print(f"✅ SUCCESS!")
        print(f"   Query: {result.get('query_name')}")
        print(f"   Rows returned: {len(result.get('data', []))}")
        print(f"   Category: {result.get('metadata', {}).get('category')}")
        print(f"\n🎉 FIX CONFIRMED: execute_query_library handler now works!")
    else:
        print(f"❌ FAILED: {result.get('error')}")
        print("\nIf error is 'Unknown tool', handler wasn't added correctly.")
        
except Exception as e:
    print(f"\n❌ TEST ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
