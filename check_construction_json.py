import json

with open(r'UI\modules_external\quote-calculator\ARCHIVE_CONSOLIDATED\CALCULATOR_JSONS\shopify\Shopify_Construction_Signs.json', encoding='utf-8') as f:
    data = json.load(f)

opts = data['shopify_construction_signs']['options']

print('Construction Signs - JSON Specification\n' + '='*60)
print('\nFields and Defaults:')
for o in opts:
    print(f"  {o['name']}: {o.get('default', 'N/A')}")

print('\nField Details:')
for o in opts:
    if 'options' in o:
        print(f"\n{o['name']} options:")
        for opt in o['options']:
            print(f"  - {opt['title']}")
