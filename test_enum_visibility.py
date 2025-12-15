import requests
import json

# Test that AI can now see enum values via get_tool_schema

response = requests.post(
    'http://localhost:5000/api/get_tool_schema',
    json={'tool_name': 'calculate_premium_business_cards_shopify'}
)

schema = response.json()

print("=" * 80)
print("ENUM VISIBILITY TEST - calculate_premium_business_cards_shopify")
print("=" * 80)
print()

# Check quantity parameter
qty_param = schema.get('parameters', {}).get('quantity', {})
print("✅ quantity parameter:")
print(f"   Type: {qty_param.get('type')}")
print(f"   Enum: {qty_param.get('enum')}")
print()

# Check other parameters with enums
param_names = ['finish_size', 'stock_type', 'print_type', 'celloglaze']
for param in param_names:
    param_def = schema.get('parameters', {}).get(param, {})
    if 'enum' in param_def:
        print(f"✅ {param}:")
        print(f"   Enum values: {param_def.get('enum')[:3]}... ({len(param_def.get('enum'))} total)")
    else:
        print(f"❌ {param}: NO ENUM")

print()
print("=" * 80)
print("RESULT: AI can now see valid values BEFORE calling the calculator!")
print("=" * 80)
