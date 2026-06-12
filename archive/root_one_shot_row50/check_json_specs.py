#!/usr/bin/env python3
"""Quick JSON specification checker"""

import json
from pathlib import Path

json_dir = Path('UI/modules_external/quote-calculator/ARCHIVE_CONSOLIDATED/CALCULATOR_JSONS/shopify')

# Check specific calculators
files = [
    'Shopify_Bollard_Signs.json',
    'Shopify_Construction_Signs.json', 
    'Shopify_Election_Signs.json',
    'Shopify_Notepads_A4.json',
    'Shopify_Notepads_A5.json',
    'Shopify_Notepads_A6.json',
]

print('JSON SPECIFICATION CHECKER')
print('=' * 80)

for filename in files:
    filepath = json_dir / filename
    if filepath.exists():
        with open(filepath) as f:
            data = json.load(f)
            
        print(f'\n{filename}:')
        print('-' * 60)
        
        # Find the main config key
        for key in data:
            if 'options' in data[key]:
                for opt in data[key]['options']:
                    field_name = opt.get('name', 'N/A')
                    default = opt.get('default', 'N/A')
                    
                    print(f'  Field: {field_name}')
                    print(f'    Default: {default}')
                    
                    if 'options' in opt and len(opt['options']) > 0:
                        titles = [o.get('title') for o in opt['options'][:5]]
                        print(f'    Options ({len(opt["options"])} total): {titles}')
                    print()
