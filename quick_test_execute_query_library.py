import sys
sys.path.insert(0, 'AI_infrastructure')

# Suppress logs
import logging
logging.basicConfig(level=logging.CRITICAL)

from tools.registry_v3 import RegistryV3

print("=" * 60)
print("TESTING: execute_query_library Tool Registration")
print("=" * 60)

registry = RegistryV3()

# Test 1: Is tool in registry?
print("\n[TEST 1] Registry Check")
in_registry = 'execute_query_library' in registry.tools
print(f"execute_query_library in registry: {in_registry}")
print(f"get_available_queries in registry: {'get_available_queries' in registry.tools}")

if in_registry:
    tool = registry.tools['execute_query_library']
    print(f"Platform: {tool.get('platform')}")
    print(f"Parameters: {list(tool.get('parameters', {}).get('properties', {}).keys())}")

# Test 2: Can we get the implementation?
print("\n[TEST 2] Implementation Check")
try:
    impl_func = registry.get_tool_function('execute_query_library')
    print(f"Implementation function: {impl_func is not None}")
    if impl_func:
        print(f"Callable: {callable(impl_func)}")
except Exception as e:
    print(f"Error getting implementation: {e}")

# Test 3: Try to execute via registry
print("\n[TEST 3] Execution Test (get_available_queries)")
try:
    result = registry.execute_tool(
        tool_name='get_available_queries',
        category='Sales & Revenue'
    )
    print(f"Success: {result.get('success')}")
    print(f"Query count: {result.get('query_count', 0)}")
    if result.get('success'):
        queries = result.get('queries', [])
        if queries:
            print(f"First query: {queries[0].get('name')}")
except Exception as e:
    print(f"Execution error: {e}")

# Test 4: Try execute_query_library if available
if in_registry:
    print("\n[TEST 4] Execution Test (execute_query_library)")
    try:
        result = registry.execute_tool(
            tool_name='execute_query_library',
            query_name='sales_trend_by_month',
            parameters={'months': 3}
        )
        print(f"Success: {result.get('success')}")
        if result.get('success'):
            data = result.get('data', [])
            print(f"Data rows: {len(data)}")
            print(f"Metadata: {result.get('metadata', {}).get('description', 'N/A')}")
        else:
            print(f"Error: {result.get('error')}")
    except Exception as e:
        print(f"Execution error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
