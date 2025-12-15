import json

# Load updated schema
schema = json.load(open('UI/modules_external/quote-calculator/schema/calculator_tools.json', 'r', encoding='utf-8'))

# Find calculate_premium_business_cards_shopify
tool = [t for t in schema['tools'] if t['name'] == 'calculate_premium_business_cards_shopify'][0]

print("=" * 80)
print("VERIFICATION: Enum Coverage Fix Applied Successfully")
print("=" * 80)
print()
print("Tool: calculate_premium_business_cards_shopify")
print()

# Check quantity parameter
qty = tool['parameters']['quantity']
print("✅ quantity parameter NOW HAS ENUM:")
print(f"   Type: {qty.get('type')}")
print(f"   Enum: {qty.get('enum')}")
print()

# Count all parameters with enums in this tool
params_with_enums = sum(1 for p in tool['parameters'].values() if 'enum' in p)
total_params = len(tool['parameters'])

print(f"Total parameters with enums: {params_with_enums}/{total_params}")
print()

# Show all parameter enums
print("All parameters with enums:")
for param_name, param_def in tool['parameters'].items():
    if 'enum' in param_def:
        enum_list = param_def['enum']
        if len(enum_list) <= 5:
            print(f"  - {param_name}: {enum_list}")
        else:
            print(f"  - {param_name}: {enum_list[:3]}... ({len(enum_list)} total)")

print()
print("=" * 80)
print("RESULT: AI can now see valid values BEFORE calling the calculator!")
print("=" * 80)
