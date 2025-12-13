import json
from pathlib import Path

# Load the active schema
schema_path = Path(__file__).parent / "schema" / "calculator_tools.json"
data = json.load(open(schema_path, 'r', encoding='utf-8-sig'))

# Calculators to remove (duplicates that have _god or _shopify versions)
remove_list = [
    'calculate_flyers',                    # Has calculate_flyers_god
    'calculate_letterheads',               # Has calculate_letterheads_god
    'calculate_perfect_bound_books',       # Has calculate_perfect_bound_books_god
    'calculate_corflute_signs',            # Has calculate_corflute_signs_god
    'calculate_spiral_bound_books',        # Has calculate_spiral_bound_books_shopify
]

original_count = len(data['tools'])
print(f'Original tool count: {original_count}')
print(f'\nRemoving {len(remove_list)} duplicate standard calculators:')

# Filter out the duplicates
filtered_tools = []
removed = []
for tool in data['tools']:
    if tool['name'] in remove_list:
        print(f'  ❌ {tool["name"]}')
        removed.append(tool['name'])
    else:
        filtered_tools.append(tool)

data['tools'] = filtered_tools

# Save the updated schema
with open(schema_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'\n✅ Updated schema saved')
print(f'   Tools before: {original_count}')
print(f'   Tools after: {len(filtered_tools)}')
print(f'   Removed: {len(removed)}')
