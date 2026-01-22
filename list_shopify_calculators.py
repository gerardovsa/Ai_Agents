#!/usr/bin/env python3
import json
from pathlib import Path

# Load schema
schema_path = Path('UI/modules_external/quote-calculator/schema/calculator_tools.json')
with open(schema_path, 'r', encoding='utf-8') as f:
    schema = json.load(f)

# Find all Shopify calculators
shopify_calcs = [t for t in schema['tools'] if '_shopify' in t['name']]

print(f'Found {len(shopify_calcs)} Shopify calculators:\n')
for i, calc in enumerate(shopify_calcs, 1):
    print(f"{i}. {calc['name']}")
    params = calc.get('parameters', {})
    enum_params = {k: v.get('enum') for k, v in params.items() if isinstance(v, dict) and v.get('enum')}
    if enum_params:
        print(f"   Enum parameters:")
        for param, values in enum_params.items():
            print(f"     - {param}: {len(values)} options")
    print()
