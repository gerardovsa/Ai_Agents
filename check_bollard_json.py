import json

with open(r'UI\modules_external\quote-calculator\ARCHIVE_CONSOLIDATED\CALCULATOR_JSONS\shopify\Shopify_Bollard_Signs.json', encoding='utf-8') as f:
    data = json.load(f)

opts = data['shopify_bollard_signs']['options']

print('JSON Defaults:')
for o in opts:
    print(f"  {o['name']}: {o.get('default', 'N/A')}")

print('\nMaterial Options:')
mat = [o for o in opts if o['name'] == 'Material'][0]
for opt in mat['options']:
    print(f"  - {opt['title']}")

print('\nSize Options:')
sz = [o for o in opts if o['name'] == 'Size'][0]
for opt in sz['options']:
    print(f"  - {opt['title']}")
