import sys
import os
sys.path.insert(0, 'AI_infrastructure')
os.environ['SUPABASE_URL'] = 'https://placeholder.supabase.co'
os.environ['SUPABASE_KEY'] = 'placeholder'

# Test what's actually registered
print("Testing InHouse Tools Registration...")

try:
    from tools.registry_v3 import RegistryV3
    registry = RegistryV3()
    
    # Find all inhouse and query library tools
    inhouse_tools = [t for t in registry.tools.keys() if t.startswith('inhouse_')]
    query_lib_tools = [t for t in registry.tools.keys() if 'query_library' in t.lower()]
    
    print(f"\nInHouse tools found: {len(inhouse_tools)}")
    for tool in sorted(inhouse_tools):
        print(f"  - {tool}")
    
    print(f"\nQuery library tools found: {len(query_lib_tools)}")
    for tool in sorted(query_lib_tools):
        print(f"  - {tool}")
    
    # Check specific tools
    print("\n--- Specific Tool Check ---")
    print(f"inhouse_get_query_library_catalog: {'inhouse_get_query_library_catalog' in registry.tools}")
    print(f"execute_query_library: {'execute_query_library' in registry.tools}")
    print(f"get_available_queries: {'get_available_queries' in registry.tools}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\nDone.")
