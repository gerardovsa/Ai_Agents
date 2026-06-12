import json

with open('UI/modules_external/quote-calculator/schema/calculator_tools.json', 'r', encoding='utf-8') as f:
    schema = json.load(f)

# Get all calculators
all_calcs = [t for t in schema['tools'] if t['name'].startswith('calculate_')]

# Categorize them
shopify_calcs = [t for t in all_calcs if 'shopify' in t['name'].lower()]
god_calcs = [t for t in all_calcs if 'god' in t['name'].lower()]
other_calcs = [t for t in all_calcs if 'shopify' not in t['name'].lower() and 'god' not in t['name'].lower()]

print('='*70)
print(f'SHOPIFY CALCULATORS ({len(shopify_calcs)}):')
print('='*70)
for i, t in enumerate(shopify_calcs, 1):
    print(f'{i}. {t["name"]}')

print('\n' + '='*70)
print(f'GOD CALCULATORS ({len(god_calcs)}):')
print('='*70)
for i, t in enumerate(god_calcs, 1):
    print(f'{i}. {t["name"]}')

print('\n' + '='*70)
print(f'OTHER HARDCODED CALCULATORS ({len(other_calcs)}):')
print('='*70)
for i, t in enumerate(other_calcs, 1):
    name = t["name"]
    short = t.get("short_description", "NO SHORT DESC")
    print(f'{i}. {name}')
    print(f'   {short[:65]}...')

print('\n' + '='*70)
print(f'SUMMARY:')
print('='*70)
print(f'Shopify:  {len(shopify_calcs)}')
print(f'GOD:      {len(god_calcs)}')
print(f'Other:    {len(other_calcs)}')
print(f'TOTAL:    {len(all_calcs)}')
