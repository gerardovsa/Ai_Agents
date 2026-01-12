"""Test if SMART bundled tools are registered"""
from tools.registry_v3 import RegistryV3

print("\n=== TOOL REGISTRY CHECK ===")
r = RegistryV3()
print(f"Total tools: {len(r.tools)}")

# Find SMART tools
smart_tools = [name for name in r.tools.keys() if 'email_attachment_complete' in name or 'local_file_universal' in name]

print(f"\nSMART tools found: {len(smart_tools)}")
for tool_name in smart_tools:
    print(f"  ✓ {tool_name}")
    tool_def = r.tools.get(tool_name)
    if tool_def:
        print(f"    Category: {tool_def.get('category', 'N/A')}")
        print(f"    Platform: {tool_def.get('platform', 'N/A')}")

# Check if implementations exist
print("\n=== IMPLEMENTATION CHECK ===")

# Check if universal_file_tools module was loaded
if 'universal_file_tools' in r.implementations:
    print("✓ universal_file_tools module loaded")
    module = r.implementations['universal_file_tools']
    
    # List all functions in the module
    functions = [name for name in dir(module) if not name.startswith('_') and callable(getattr(module, name))]
    print(f"  Available functions: {len(functions)}")
    
    # Check if SMART tools are in the module
    for tool_name in smart_tools:
        if hasattr(module, tool_name):
            print(f"  ✓ {tool_name} - Function exists in module")
        else:
            print(f"  ✗ {tool_name} - Function NOT FOUND in module")
else:
    print("✗ universal_file_tools module NOT loaded")

# Also check if individual function implementations exist
print("\n=== INDIVIDUAL FUNCTION CHECK ===")
for tool_name in smart_tools:
    if tool_name in r.implementations:
        print(f"  ✓ {tool_name} - Direct implementation found")
    else:
        print(f"  ✗ {tool_name} - Direct implementation not found")

print("\n=== TEST COMPLETE ===")
