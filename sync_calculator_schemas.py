"""Sync calculator schemas from main to module"""
import json

# Read both schemas
with open('tools/schemas/calculator_tools.json', 'r') as f:
    main_schema = json.load(f)

with open('UI/modules_external/quote-calculator/schema/calculator_tools.json', 'r') as f:
    module_schema = json.load(f)

# Get tool names
module_tools = {t['name'] for t in module_schema['tools']}
main_tools_dict = {t['name']: t for t in main_schema['tools']}

# Find missing tools
missing = [name for name in main_tools_dict.keys() if name not in module_tools]

print(f"Module schema has {len(module_tools)} tools")
print(f"Main schema has {len(main_tools_dict)} tools")
print(f"Missing from module: {len(missing)}")
print("\nAdding missing tools:")

# Add missing tools to module schema
for tool_name in sorted(missing):
    tool = main_tools_dict[tool_name]
    module_schema['tools'].append(tool)
    print(f"  + {tool_name}")

# Write updated module schema
with open('UI/modules_external/quote-calculator/schema/calculator_tools.json', 'w') as f:
    json.dump(module_schema, f, indent=2)

print(f"\n✅ Updated module schema: {len(module_schema['tools'])} tools total")
