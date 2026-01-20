"""Simple test - are meta tools registered?"""
from tools.registry_v3 import get_registry

r = get_registry()

meta_tools = ["list_platform_tools", "search_tools", "get_tool_schema", "list_available_platforms"]

print("\nMETA TOOL REGISTRATION CHECK:")
print("="*50)
for tool in meta_tools:
    exists = tool in r.tools
    print(f"{'✅' if exists else '❌'} {tool}: {'REGISTERED' if exists else 'MISSING'}")

print(f"\nTotal tools in registry: {len(r.tools)}")

# Try to execute one
if "list_available_platforms" in r.tools:
    print("\nTesting list_available_platforms()...")
    try:
        result = r.execute_tool(tool_name="list_available_platforms")
        print(f"SUCCESS: {result.get('platform_count', 0)} platforms found")
    except Exception as e:
        print(f"FAILED: {e}")
else:
    print("\n❌ list_available_platforms NOT FOUND - cannot test")
