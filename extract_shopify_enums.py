"""
Extract enum values from Shopify JSON configs and create schema updates
"""

import json
from pathlib import Path
from collections import defaultdict

# Map Shopify JSON files to schema tool names
SHOPIFY_MAPPINGS = {
    'Shopify_Bollard_Signs.json': 'calculate_bollard_signs',
    'Shopify_Construction_Signs.json': 'calculate_construction_signs',
    'Shopify_Election_Signs.json': 'calculate_election_signs',
    'Shopify_Corflute_Insert_A_Frame.json': 'calculate_corflute_insert_a_frame',
    'Shopify_Custom_Poster_Printing.json': 'calculate_custom_poster_printing',
    'Shopify_Custom_Vinyl_Stickers.json': 'calculate_custom_vinyl_stickers',
    'Shopify_Luxury_Classic_Pull_Up_Banners.json': 'calculate_luxury_classic_pull_up_banners',
    'Shopify_Metal_Face_A_Frame.json': 'calculate_metal_face_a_frame',
    'Shopify_Notepads_A4.json': 'calculate_notepads_a4',
    'Shopify_Notepads_A5.json': 'calculate_notepads_a5',
    'Shopify_Notepads_A6.json': 'calculate_notepads_a6',
    'Shopify_Premium_Bookmarks.json': 'calculate_premium_bookmarks',
    'Shopify_Printed_Letterheads.json': 'calculate_printed_letterheads',
    'Shopify_Saddle_Stitch_Books.json': 'calculate_saddle_stitch_books',
    'Shopify_Selfie_Frames.json': 'calculate_selfie_frames',
    'Shopify_Spiral_Bound_Books.json': 'calculate_spiral_bound_books_shopify',
    'Shopify_Stackable_Cubes.json': 'calculate_stackable_cubes',
    'Shopify_Strut_Cards_A3.json': 'calculate_strut_cards_a3',
    'Shopify_Strut_Cards_A4.json': 'calculate_strut_cards_a4',
    'Shopify_With_Compliments_Slips.json': 'calculate_with_compliments_slips',
}

# Additional tools needing enums (from wrappers)
ADDITIONAL_TOOLS = {
    'calculate_economical_business_cards_shopify': [250, 500, 1000, 2000, 5000, 10000],
    'calculate_premium_business_cards_shopify': [250, 500, 1000, 2000, 5000, 10000],
    'calculate_folded_flyers_shopify': [100, 250, 500, 1000, 2000, 5000, 10000],
    'calculate_wire_bound_books_shopify': [10, 25, 50, 75, 100, 150, 200, 250, 300, 400, 500],
}

config_base = Path(r'c:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator\shopify')

extracted_enums = {}

print("=" * 100)
print("EXTRACTING ENUM VALUES FROM SHOPIFY CONFIG FILES")
print("=" * 100)
print()

for json_file, tool_name in SHOPIFY_MAPPINGS.items():
    json_path = config_base / json_file
    
    if not json_path.exists():
        print(f"⚠️  File not found: {json_file}")
        continue
    
    try:
        data = json.load(open(json_path, 'r', encoding='utf-8'))
        
        # Find the config key (usually shopify_xxx)
        config_key = list(data.keys())[0]
        config = data[config_key]
        
        tool_enums = {}
        
        # Extract enums from all fields
        if 'options' in config:
            for option in config['options']:
                field_name = option.get('name', '')
                field_id = option.get('field_id', '')
                
                # Get enum values
                if 'options' in option:
                    values = []
                    for opt in option['options']:
                        title = opt.get('title', '')
                        # Try to convert to int for quantities
                        if field_name == 'Quantity':
                            try:
                                values.append(int(title))
                            except:
                                values.append(title)
                        else:
                            values.append(title)
                    
                    # Map field names to schema parameter names
                    param_name = field_name.lower().replace(' ', '_')
                    tool_enums[param_name] = values
        
        extracted_enums[tool_name] = tool_enums
        
        print(f"✅ {tool_name}:")
        for param, values in tool_enums.items():
            if len(values) <= 5:
                print(f"   {param}: {values}")
            else:
                print(f"   {param}: {values[:5]}... ({len(values)} total)")
        print()
        
    except Exception as e:
        print(f"❌ Error processing {json_file}: {e}")
        print()

# Add manually defined enums
for tool_name, quantities in ADDITIONAL_TOOLS.items():
    extracted_enums[tool_name] = {'quantity': quantities}
    print(f"✅ {tool_name}:")
    print(f"   quantity: {quantities}")
    print()

print("=" * 100)
print(f"SUMMARY: Extracted enums for {len(extracted_enums)} tools")
print("=" * 100)
print()

# Save to file for reference
output = {
    'extracted_enums': extracted_enums,
    'total_tools': len(extracted_enums),
    'note': 'Use these enums to update calculator_tools.json schema'
}

with open('shopify_enum_extraction.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("✅ Saved to: shopify_enum_extraction.json")
print()

# Generate schema update template
print("=" * 100)
print("SCHEMA UPDATE TEMPLATE")
print("=" * 100)
print()
print("Add these enum arrays to calculator_tools.json:")
print()

for tool_name, enums in list(extracted_enums.items())[:3]:
    print(f'// {tool_name}')
    print('"parameters": {')
    for param_name, values in enums.items():
        value_type = "integer" if all(isinstance(v, int) for v in values) else "string"
        print(f'  "{param_name}": {{')
        print(f'    "type": "{value_type}",')
        print(f'    "description": "...",')
        print(f'    "enum": {json.dumps(values)}')
        print(f'  }},')
    print('}')
    print()
