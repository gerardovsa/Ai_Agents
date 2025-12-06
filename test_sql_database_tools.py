"""
Test SQL Database Tools Implementation
Quick validation that stub implementations load correctly
"""

from tools.registry_v3 import RegistryV3

print("\n" + "="*80)
print("SQL DATABASE TOOLS - IMPLEMENTATION TEST")
print("="*80 + "\n")

# Load registry
registry = RegistryV3()

print(f"✅ Registry loaded: {len(registry.tools)} total tools")

# Check if sql_database implementations loaded
print(f"\n📊 SQL Database Implementation Status:")
print(f"   sql_database module loaded: {'sql_database' in registry.implementations}")

# Check individual functions
expected_functions = [
    'db_execute_query',
    'db_get_available_queries',
    'db_calculate_quote',
    'db_get_business_summary',
    'db_get_stock_levels'
]

print(f"\n🔍 Individual Function Registration:")
for func_name in expected_functions:
    is_registered = func_name in registry.implementations
    status = "✅" if is_registered else "❌"
    print(f"   {status} {func_name}: {is_registered}")

# Try to get tool function
print(f"\n🧪 Function Retrieval Test:")
for func_name in expected_functions:
    func = registry.get_tool_function(func_name)
    if func:
        print(f"   ✅ {func_name}: {type(func).__name__}")
    else:
        print(f"   ❌ {func_name}: NOT FOUND")

# Try to execute one tool
print(f"\n🚀 Execution Test (db_execute_query):")
try:
    result = registry.execute_tool(
        tool_name="db_execute_query",
        query_name="test_query",
        params={"client_name": "Simply Signs"},
        _user_id=1
    )
    print(f"   ✅ Tool executed successfully")
    print(f"   Result success: {result.get('success')}")
    print(f"   Status: {result.get('status')}")
    print(f"   Message: {result.get('message', '')[:80]}...")
except ValueError as e:
    print(f"   ❌ Execution failed: {e}")
except Exception as e:
    print(f"   ⚠️  Unexpected error: {e}")

# List platform tools
print(f"\n📋 Platform Tools List:")
tools = registry.list_tools_by_platform("inhouse_database")
print(f"   Found {len(tools)} tools for 'inhouse_database' platform")
for tool in tools:
    print(f"   - {tool}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80 + "\n")

if all(f in registry.implementations for f in expected_functions):
    print("✅ SUCCESS: All 5 functions are registered and callable")
    print("   (Note: Functions return stub messages, not real data)")
else:
    print("❌ FAILURE: Some functions are missing")
    missing = [f for f in expected_functions if f not in registry.implementations]
    print(f"   Missing: {missing}")
