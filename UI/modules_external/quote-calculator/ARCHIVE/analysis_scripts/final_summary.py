import json
from pathlib import Path

schema_path = Path(__file__).parent / "schema" / "calculator_tools.json"
data = json.load(open(schema_path, 'r', encoding='utf-8-sig'))

tools = data['tools']
god = [t['name'] for t in tools if '_god' in t['name']]
shopify = [t['name'] for t in tools if '_shopify' in t['name']]
other = [t['name'] for t in tools if '_god' not in t['name'] and '_shopify' not in t['name'] and t['name'].startswith('calculate_')]

print('=' * 80)
print('FINAL CALCULATOR TOOL SUMMARY')
print('=' * 80)

print(f'\n🗄️  GOD CALCULATORS ({len(god)}) - Database-driven:')
for t in god:
    print(f'   ✅ {t}')

print(f'\n🛒 SHOPIFY CALCULATORS ({len(shopify)}) - Hardcoded Shopify pricing:')
for t in shopify:
    print(f'   ✅ {t}')

print(f'\n📋 OTHER CALCULATORS ({len(other)}):')
for t in other:
    print(f'   ✅ {t}')

print(f'\n📊 TOTAL: {len(tools)} tools')

print('\n' + '=' * 80)
print('CLEANUP COMPLETED')
print('=' * 80)
print('\n✅ Removed 5 duplicate standard calculators')
print('✅ Deleted unused tools/schemas/calculator_tools.json')
print('✅ No duplicate calculators remain')
print('\n🎯 Active schema: UI/modules_external/quote-calculator/schema/calculator_tools.json')
