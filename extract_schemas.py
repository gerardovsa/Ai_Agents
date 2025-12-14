import json

# Load archived schema
archive = json.load(open(r'c:\Users\gpoli\GIT\AI_agents\tools\schemas\ARCHIVE\calculator_tools.json', encoding='utf-8'))
archive_tools = archive['tools']

# Extract the 4 missing tools
extract_names = ['calculate_flyers', 'calculate_perfect_bound_books', 'calculate_corflute_signs', 'calculate_printed_letterheads']
extracted = []

for tool in archive_tools:
    if tool['name'] in extract_names:
        # Rename calculate_printed_letterheads to calculate_letterheads
        if tool['name'] == 'calculate_printed_letterheads':
            tool['name'] = 'calculate_letterheads'
        extracted.append(tool)
        print(f'Extracted: {tool["name"]}')

# Load current schema
current = json.load(open(r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator\schema\calculator_tools.json', encoding='utf-8'))

print(f'\nCurrent tools: {len(current["tools"])}')

# Insert after calculate_booklets (index 1) and before get_stock_list (index 2)
insert_position = 2

# Insert the 4 tools
for i, tool in enumerate(extracted):
    current['tools'].insert(insert_position + i, tool)
    print(f'Inserted {tool["name"]} at position {insert_position + i}')

# Save updated schema
with open(r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator\schema\calculator_tools.json', 'w', encoding='utf-8') as f:
    json.dump(current, f, indent=2)

print(f'\n✅ Added {len(extracted)} tools to calculator_tools.json')
print(f'Total tools now: {len(current["tools"])}')
