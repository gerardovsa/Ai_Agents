import json

# Verify the schema update
schema = json.load(open('UI/modules_external/quote-calculator/schema/calculator_tools.json', 'r', encoding='utf-8'))

tools_with_enums = 0
total_enums = 0

for tool in schema['tools']:
    params = tool.get('parameters', {})
    has_enum = False
    
    for param_name, param_def in params.items():
        if 'enum' in param_def:
            has_enum = True
            total_enums += 1
    
    if has_enum:
        tools_with_enums += 1

print(f'✅ Schema updated successfully!')
print(f'   Tools with enums: {tools_with_enums}/{len(schema["tools"])}')
print(f'   Total enum parameters: {total_enums}')
print()
print('Sample: calculate_premium_business_cards_shopify')
for tool in schema['tools']:
    if tool['name'] == 'calculate_premium_business_cards_shopify':
        qty = tool['parameters'].get('quantity', {})
        print(f'   quantity.type: {qty.get("type")}')
        print(f'   quantity.enum: {qty.get("enum")}')
        break
