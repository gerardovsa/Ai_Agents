"""Quick test of search_tools after wrapper deletion"""
from tools.registry_v3 import RegistryV3

print("Initializing Registry V3...")
r = RegistryV3()

print(f"\nTotal tools: {len(r.tools)}")
print(f"search_tools exists: {'search_tools' in r.tools}")

print("\nExecuting: search_tools(query='shopify')")
result = r.execute_tool(tool_name='search_tools', query='shopify')

print(f"Success: {result.get('success', False)}")
print(f"Found: {result.get('total_results', 0)} tools")

if result.get('success'):
    print("\n✅ META-TOOLS WORK WITHOUT WRAPPER!")
    print("   AI can discover tools through Registry V3")
else:
    print(f"\n❌ Error: {result.get('error', 'Unknown')}")
