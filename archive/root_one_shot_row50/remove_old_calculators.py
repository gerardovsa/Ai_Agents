import json

# Load current schema
current = json.load(open(r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator\schema\calculator_tools.json', encoding='utf-8'))

# Remove the 4 old-style calculators
remove_names = ['calculate_flyers', 'calculate_letterheads', 'calculate_perfect_bound_books', 'calculate_corflute_signs']
original_count = len(current['tools'])

current['tools'] = [t for t in current['tools'] if t['name'] not in remove_names]

# Save updated schema
with open(r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator\schema\calculator_tools.json', 'w', encoding='utf-8') as f:
    json.dump(current, f, indent=2)

removed = original_count - len(current['tools'])
print(f'Removed {removed} old-style calculators')
print(f'Schema now has {len(current["tools"])} tools (was {original_count})')
print('\nRemoved:')
for name in remove_names:
    print(f'  - {name}')
