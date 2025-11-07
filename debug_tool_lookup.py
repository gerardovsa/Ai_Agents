"""
Debug tool lookup and function discovery
"""

from tools.registry_v3 import RegistryV3

r = RegistryV3()

# Check if outlook_send_email is in tools dict
tool_name = 'outlook_send_email'
print(f"Looking for tool: {tool_name}")
print(f"Tool in registry.tools: {tool_name in r.tools}")

if tool_name in r.tools:
    tool = r.tools[tool_name]
    print(f"  Platform: {tool.get('platform')}")
    print(f"  Description: {tool.get('description', 'N/A')[:60]}")

# Check function lookup
print(f"\nLooking for function: {tool_name}")
func = r.get_tool_function(tool_name)
print(f"Function found: {func is not None}")
if func:
    print(f"  Function name: {func.__name__}")
    print(f"  Function module: {func.__module__}")
else:
    print("  Function NOT found - debugging...")
    
    # Try to find the module
    print(f"  Checking implementations for module...")
    
    # Check exact matches
    for impl_name in r.implementations.keys():
        if 'outlook' in impl_name.lower():
            print(f"    Found implementation: {impl_name}")
            impl = r.implementations[impl_name]
            if hasattr(impl, tool_name):
                print(f"      Has function: {tool_name}")
            # List first 5 functions in this module
            funcs = [x for x in dir(impl) if not x.startswith('_')][:5]
            print(f"      Sample functions: {funcs}")

# Check if we can get the implementation directly
print(f"\nDirect implementation lookup:")
print(f"  microsoft_outlook_tools in implementations: {'microsoft_outlook_tools' in r.implementations}")

if 'microsoft_outlook_tools' in r.implementations:
    impl = r.implementations['microsoft_outlook_tools']
    print(f"  Implementation type: {type(impl)}")
    print(f"  Has outlook_send_email: {hasattr(impl, 'outlook_send_email')}")
    if hasattr(impl, 'outlook_send_email'):
        func = getattr(impl, 'outlook_send_email')
        print(f"  Function: {func}")
