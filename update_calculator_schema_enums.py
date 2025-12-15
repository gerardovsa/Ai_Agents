"""
Auto-update calculator_tools.json schema with extracted enums
"""

import json
from pathlib import Path
from collections import defaultdict

# Load extracted enums
with open('shopify_enum_extraction.json', 'r', encoding='utf-8') as f:
    enum_data = json.load(f)

extracted_enums = enum_data['extracted_enums']

# Load current schema
schema_path = Path('UI/modules_external/quote-calculator/schema/calculator_tools.json')
with open(schema_path, 'r', encoding='utf-8') as f:
    schema = json.load(f)

print("=" * 100)
print("UPDATING CALCULATOR SCHEMA WITH ENUM ARRAYS")
print("=" * 100)
print()

tools_updated = 0
params_updated = 0

for tool in schema['tools']:
    tool_name = tool['name']
    
    if tool_name not in extracted_enums:
        continue
    
    tool_enums = extracted_enums[tool_name]
    params = tool.get('parameters', {})
    
    updated_params = []
    
    for param_name, enum_values in tool_enums.items():
        # Skip if parameter doesn't exist in schema
        if param_name not in params:
            print(f"⚠️  {tool_name}: Parameter '{param_name}' not in schema (skipping)")
            continue
        
        param_def = params[param_name]
        
        # Check if already has enum
        had_enum = 'enum' in param_def
        
        # Add enum
        param_def['enum'] = enum_values
        
        # Update type if needed
        if enum_values:
            first_value = enum_values[0]
            if isinstance(first_value, int):
                param_def['type'] = 'integer'
            elif isinstance(first_value, str):
                param_def['type'] = 'string'
            elif isinstance(first_value, bool):
                param_def['type'] = 'boolean'
        
        updated_params.append(param_name)
        params_updated += 1
        
        status = "✏️  Updated" if had_enum else "✅ Added"
        print(f"{status} enum for {tool_name}.{param_name} ({len(enum_values)} values)")
    
    if updated_params:
        tools_updated += 1

print()
print("=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"✅ Updated {tools_updated} tools")
print(f"✅ Added/updated {params_updated} parameter enums")
print()

# Save updated schema
output_path = Path('UI/modules_external/quote-calculator/schema/calculator_tools_UPDATED.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(schema, f, indent=2, ensure_ascii=False)

print(f"✅ Saved updated schema to: {output_path}")
print()
print("⚠️  NEXT STEPS:")
print("   1. Review the updated schema file")
print("   2. Backup the original: calculator_tools.json → calculator_tools_BACKUP.json")
print("   3. Rename: calculator_tools_UPDATED.json → calculator_tools.json")
print("   4. Restart server to reload schema")
print("   5. Test with: get_tool_schema('calculate_premium_business_cards_shopify')")
print()
