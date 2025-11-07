import sys
sys.path.insert(0, 'AI_infrastructure')
from tools.registry_v3 import RegistryV3

registry = RegistryV3()
tools = registry.get_anthropic_tools()

print(f'\nTotal tools: {len(tools)}\n')

# Validate
invalid = []
for idx, tool in enumerate(tools):
    schema = tool.get('input_schema', {})
    if not isinstance(schema, dict) or schema.get('type') != 'object' or 'properties' not in schema:
        invalid.append((idx, tool.get('name', 'unknown')))

if invalid:
    print(f'Found {len(invalid)} invalid tools:')
    for idx, name in invalid[:10]:
        print(f'  Tool #{idx}: {name}')
else:
    print('ALL 584 TOOLS HAVE VALID SCHEMAS!')

print(f'\nTool at index 4: {tools[4]["name"]}')
print(f'Has input_schema: {"input_schema" in tools[4]}')
print(f'Schema type: {tools[4].get("input_schema", {}).get("type")}')
print(f'Has properties: {"properties" in tools[4].get("input_schema", {})}')
