"""
Sync enum arrays from tools/schemas/calculator_tools.json to UI/modules_external/quote-calculator/schema/calculator_tools.json

This fixes the issue where module schemas don't have enum guidance for AI parameter selection.
"""
import json

# Read both schemas
with open('tools/schemas/calculator_tools.json', 'r') as f:
    main_schema = json.load(f)

with open('UI/modules_external/quote-calculator/schema/calculator_tools.json', 'r') as f:
    module_schema = json.load(f)

# Build lookup dict
main_tools_dict = {t['name']: t for t in main_schema['tools']}

print("="*60)
print("ENUM SYNC: tools/schemas → UI/modules_external")
print("="*60)

updated_count = 0
total_enums_added = 0

# Update each tool in module schema
for i, module_tool in enumerate(module_schema['tools']):
    tool_name = module_tool['name']
    
    # Skip if not in main schema
    if tool_name not in main_tools_dict:
        continue
    
    main_tool = main_tools_dict[tool_name]
    
    # Get parameters
    module_params = module_tool.get('parameters', {})
    main_params = main_tool.get('parameters', {})
    
    enums_added = 0
    
    # Copy enum arrays from main to module
    for param_name in main_params:
        if param_name in module_params:
            # If main has enum but module doesn't, copy it
            if 'enum' in main_params[param_name] and 'enum' not in module_params[param_name]:
                module_params[param_name]['enum'] = main_params[param_name]['enum']
                enums_added += 1
                print(f"✓ {tool_name}.{param_name} - Added enum ({len(main_params[param_name]['enum'])} values)")
    
    if enums_added > 0:
        updated_count += 1
        total_enums_added += enums_added

# Write updated module schema
with open('UI/modules_external/quote-calculator/schema/calculator_tools.json', 'w') as f:
    json.dump(module_schema, f, indent=2)

print("="*60)
print(f"✅ COMPLETE:")
print(f"   - Updated {updated_count} tools")
print(f"   - Added {total_enums_added} enum arrays")
print(f"   - Module schema now has enum guidance for AI")
print("="*60)
