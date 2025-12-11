#!/usr/bin/env python
"""Quick test to verify enum preservation fix"""
from tools.implementations.meta_tools import get_tool_schema

result = get_tool_schema('calculate_bollard_signs')
props = result['input_schema']['properties']

print('=== ENUM VERIFICATION AFTER FIX ===')
print(f'Quantity has enum: {"enum" in props["quantity"]}')
print(f'Material has enum: {"enum" in props["material"]}')
print(f'Size has enum: {"enum" in props["size"]}')
print(f'Artworks has enum: {"enum" in props["artworks"]}')

if 'enum' in props['quantity']:
    print(f'\nQuantity enum values: {props["quantity"]["enum"][:5]}...')
    print(f'Total enum values: {len(props["quantity"]["enum"])}')
else:
    print('\nERROR: Enum still missing!')
