"""
Test script to show improved tool schema with complete option listings
"""

import json

# Load the Strut Cards A4 JSON config
with open(r'C:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator\shopify\Shopify_Strut_Cards_A4.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

calc_config = config['shopify_strut_cards_a4']
fields = calc_config['options']

print("=" * 80)
print("IMPROVED TOOL SCHEMA - WITH ALL OPTIONS LISTED")
print("=" * 80)
print()
print(f"Tool Name: calculate_strut_cards_a4")
print(f"Description: Calculate quote for {calc_config['product_title']}. {calc_config['description']}")
print()
print("Parameters:")
print()

for field in fields:
    field_name = field['name'].lower().replace(' ', '_').replace(':', '')
    field_type = field['type']
    description = field.get('description', field['name'])
    required = field.get('required', False)
    
    param_type = 'integer' if field_type == 'number' else 'string'
    
    # If field has options (select type), list all valid options
    if field_type == 'select' and 'options' in field:
        options = field['options']
        if isinstance(options, list) and options:
            option_titles = [opt.get('title', opt.get('name', '')) for opt in options if opt.get('title') or opt.get('name')]
            if option_titles:
                description = f"{description}. Valid options: {', '.join(repr(t) for t in option_titles)}"
    
    # Add min/max info for number fields
    if field_type == 'number':
        min_val = field.get('min')
        max_val = field.get('max')
        if min_val is not None or max_val is not None:
            range_info = []
            if min_val is not None:
                range_info.append(f"min: {min_val}")
            if max_val is not None:
                range_info.append(f"max: {max_val}")
            if range_info:
                description = f"{description} ({', '.join(range_info)})"
    
    print(f"  {field_name}:")
    print(f"    Type: {param_type}")
    print(f"    Required: {required}")
    print(f"    Description: {description}")
    print()

print("=" * 80)
print()
print("COMPARISON - BEFORE vs AFTER:")
print("=" * 80)
print()
print("BEFORE (current):")
print("  stock:")
print("    Description: 'stock'")
print()
print("AFTER (improved):")
print("  stock:")
print("    Description: 'stock. Valid options: '2mm Screenboard''")
print()
print("BEFORE (current):")
print("  size:")
print("    Description: 'size:'")
print()
print("AFTER (improved):")
print("  size:")
print("    Description: 'size:. Valid options: 'A4 - 210mm x 297mm''")
print()
print("BEFORE (current):")
print("  quantity:")
print("    Description: 'Number of A4 strut cards to produce'")
print()
print("AFTER (improved):")
print("  quantity:")
print("    Description: 'Number of A4 strut cards to produce (min: 1, max: 10000)'")
