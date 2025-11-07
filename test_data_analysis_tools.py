"""
Test data analysis tools loading in registry
"""

from tools.registry_v3 import RegistryV3

# Load registry
print("Loading registry...")
registry = RegistryV3()

# Find all data_ tools
data_tools = [name for name in registry.tools.keys() if name.startswith('data_')]

print(f"\nFound {len(data_tools)} data analysis tools:")
for tool in sorted(data_tools):
    print(f"  - {tool}")

# Test each tool
print("\nTesting tool schemas:")
for tool_name in sorted(data_tools):
    tool = registry.get_tool(tool_name)
    has_description = 'description' in tool
    has_platform = 'platform' in tool
    has_parameters = 'parameters' in tool
    
    status = "OK" if (has_description and has_platform and has_parameters) else "MISSING FIELDS"
    print(f"  {tool_name}: {status}")

# Test Anthropic format conversion
print("\nTesting Anthropic format conversion:")
anthropic_tools = registry.get_anthropic_tools()
data_anthropic = [t for t in anthropic_tools if t['name'].startswith('data_')]

print(f"Found {len(data_anthropic)} data tools in Anthropic format")

for tool in data_anthropic:
    has_input_schema = 'input_schema' in tool
    has_type = tool.get('input_schema', {}).get('type') == 'object'
    has_props = 'properties' in tool.get('input_schema', {})
    
    status = "OK" if (has_input_schema and has_type and has_props) else "INVALID SCHEMA"
    print(f"  {tool['name']}: {status}")

print("\nAll tests completed!")
print(f"Total tools in registry: {len(registry.tools)}")
print(f"Data analysis tools: {len(data_tools)}")
