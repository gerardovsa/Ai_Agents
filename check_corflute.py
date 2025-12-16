import json

with open('UI/modules_external/quote-calculator/schema/calculator_tools.json', 'r', encoding='utf-8') as f:
    schema = json.load(f)

print('='*60)
print('CORFLUTE CALCULATORS:')
print('='*60)
corflute = [t for t in schema['tools'] if 'corflute' in t['name'].lower()]
for i, tool in enumerate(corflute, 1):
    name = tool['name']
    calc_type = 'SHOPIFY' if 'shopify' in name else 'GOD' if 'god' in name else 'OTHER'
    print(f'{i}. {name} ({calc_type})')

print(f'\nTotal corflute calculators: {len(corflute)}')

print('\n' + '='*60)
print('ALL SHOPIFY/HARDCODED CALCULATORS:')
print('='*60)
shopify = [t for t in schema['tools'] if 'shopify' in t['name'].lower()]
for i, tool in enumerate(shopify, 1):
    print(f'{i}. {tool["name"]}')

print(f'\nTotal Shopify calculators: {len(shopify)}')
print(f'Total tools in schema: {len(schema["tools"])}')
