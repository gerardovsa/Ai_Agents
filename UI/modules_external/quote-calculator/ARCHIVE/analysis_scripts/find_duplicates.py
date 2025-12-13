import json

data = json.load(open('schema/calculator_tools.json', 'r', encoding='utf-8-sig'))
tools = data['tools']
all_names = [t['name'] for t in tools]

print('DUPLICATES (have standard + god/shopify):')
bases = {}
for name in all_names:
    base = name.replace('_god', '').replace('_shopify', '')
    if base not in bases:
        bases[base] = []
    bases[base].append(name)

for base, versions in sorted(bases.items()):
    if len(versions) > 1:
        print(f'\n{base}:')
        for v in versions:
            print(f'  - {v}')
