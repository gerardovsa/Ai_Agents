#!/usr/bin/env python3
"""
Systematic Audit of Remaining 17 Calculators
Compares JSON specs vs Wrapper validation
"""

import json
import re
from pathlib import Path

# Calculator mapping: name -> (json_file, wrapper_line_start)
CALCULATORS = {
    'bollard_signs': ('Shopify_Bollard_Signs.json', 2750),
    'construction_signs': ('Shopify_Construction_Signs.json', 2833),
    'election_signs': ('Shopify_Election_Signs.json', 2917),
    'corflute_insert_a_frame': ('Shopify_Corflute_Insert_A_Frame.json', 3003),
    'metal_face_a_frame': ('Shopify_Metal_Face_A_Frame.json', 3075),
    'luxury_pull_up_banners': ('Shopify_Luxury_Classic_Pull_Up_Banners.json', 3148),
    'selfie_frames': ('Shopify_Selfie_Frames.json', 3268),
    'stackable_cubes': ('Shopify_Stackable_Cubes.json', 3399),
    'strut_cards_a3': ('Shopify_Strut_Cards_A3.json', 3468),
    'strut_cards_a4': ('Shopify_Strut_Cards_A4.json', 3549),
    'custom_poster_printing': ('Shopify_Custom_Poster_Printing.json', 3630),
    'custom_vinyl_stickers': ('Shopify_Custom_Vinyl_Stickers.json', 3749),
    'premium_bookmarks': ('Shopify_Premium_Bookmarks.json', 3868),
    'printed_letterheads': ('Shopify_Printed_Letterheads.json', 3998),
    'with_compliments_slips': ('Shopify_With_Compliments_Slips.json', 4120),
    'notepads_a4': ('Shopify_Notepads_A4.json', 4247),
    'notepads_a5': ('Shopify_Notepads_A5.json', 4374),
    'notepads_a6': ('Shopify_Notepads_A6.json', 4486),
}

json_dir = Path('UI/modules_external/quote-calculator/ARCHIVE_CONSOLIDATED/CALCULATOR_JSONS/shopify')
wrapper_file = Path('UI/modules_external/quote-calculator/implementations/calculator_wrapper.py')

def extract_json_enums(json_path):
    """Extract enum values from JSON file"""
    try:
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)
        
        enums = {}
        for key in data:
            if isinstance(data[key], dict) and 'options' in data[key]:
                for opt in data[key]['options']:
                    field_name = opt.get('name', '').lower().replace(' ', '_')
                    if 'options' in opt and opt['options']:
                        enums[field_name] = [o.get('title') for o in opt['options']]
                    elif opt.get('type') == 'select' and 'default' in opt:
                        enums[field_name] = [opt['default']]
        return enums
    except Exception as e:
        return {'error': str(e)}

def extract_wrapper_validation(wrapper_path, start_line, lines_to_read=150):
    """Extract validation logic from wrapper function"""
    try:
        with open(wrapper_path, encoding='utf-8') as f:
            lines = f.readlines()
        
        relevant_lines = lines[start_line-1:start_line-1+lines_to_read]
        validations = {}
        
        for i, line in enumerate(relevant_lines):
            # Look for valid_xxx = [...]
            match = re.search(r'valid_(\w+)\s*=\s*\[(.*?)\]', line)
            if match:
                field = match.group(1)
                values_str = match.group(2)
                values = [v.strip().strip('"\'') for v in values_str.split(',') if v.strip()]
                validations[field] = values
            
            # Look for if xxx not in [...]
            match = re.search(r'if\s+(\w+)\s+not\s+in\s+\[(.*?)\]', line)
            if match:
                field = match.group(1)
                values_str = match.group(2)
                values = [v.strip().strip('"\'') for v in values_str.split(',') if v.strip()]
                validations[field] = values
        
        return validations
    except Exception as e:
        return {'error': str(e)}

def compare_enums(json_enums, wrapper_validations):
    """Compare JSON enums with wrapper validations"""
    mismatches = []
    
    for field, json_values in json_enums.items():
        if field == 'error':
            continue
            
        # Try to find matching wrapper field
        wrapper_field = None
        for w_field in wrapper_validations:
            if w_field in field or field in w_field:
                wrapper_field = w_field
                break
        
        if wrapper_field:
            wrapper_values = wrapper_validations[wrapper_field]
            if set(json_values) != set(wrapper_values):
                mismatches.append({
                    'field': field,
                    'json_values': json_values,
                    'wrapper_values': wrapper_values,
                    'wrapper_field': wrapper_field
                })
        else:
            # Field in JSON but not validated in wrapper
            if len(json_values) > 1:  # Only flag if multiple options exist
                mismatches.append({
                    'field': field,
                    'json_values': json_values,
                    'wrapper_values': None,
                    'wrapper_field': None
                })
    
    return mismatches

print('=' * 80)
print('SYSTEMATIC CALCULATOR AUDIT')
print('=' * 80)
print()

results = {}

for calc_name, (json_file, line_start) in CALCULATORS.items():
    print(f'Auditing: {calc_name}')
    print('-' * 60)
    
    json_path = json_dir / json_file
    if not json_path.exists():
        print(f'  ❌ JSON not found: {json_file}')
        results[calc_name] = {'status': 'json_missing'}
        print()
        continue
    
    # Extract enums from JSON
    json_enums = extract_json_enums(json_path)
    if 'error' in json_enums:
        print(f'  ❌ Error reading JSON: {json_enums["error"]}')
        results[calc_name] = {'status': 'json_error', 'error': json_enums['error']}
        print()
        continue
    
    # Extract validations from wrapper
    wrapper_validations = extract_wrapper_validation(wrapper_file, line_start)
    if 'error' in wrapper_validations:
        print(f'  ❌ Error reading wrapper: {wrapper_validations["error"]}')
        results[calc_name] = {'status': 'wrapper_error', 'error': wrapper_validations['error']}
        print()
        continue
    
    # Compare
    mismatches = compare_enums(json_enums, wrapper_validations)
    
    if mismatches:
        print(f'  ⚠️  {len(mismatches)} MISMATCH(ES) FOUND')
        for m in mismatches:
            print(f'      Field: {m["field"]}')
            if m['wrapper_values'] is None:
                print(f'        JSON has {len(m["json_values"])} options, wrapper has NO validation')
            else:
                print(f'        JSON: {m["json_values"][:3]}{"..." if len(m["json_values"]) > 3 else ""}')
                print(f'        Wrapper: {m["wrapper_values"][:3]}{"..." if len(m["wrapper_values"]) > 3 else ""}')
        results[calc_name] = {'status': 'mismatches', 'count': len(mismatches), 'details': mismatches}
    else:
        print(f'  ✅ ALIGNED - No mismatches found')
        results[calc_name] = {'status': 'aligned'}
    
    print()

# Summary
print('=' * 80)
print('AUDIT SUMMARY')
print('=' * 80)
aligned = sum(1 for r in results.values() if r['status'] == 'aligned')
mismatched = sum(1 for r in results.values() if r['status'] == 'mismatches')
errors = sum(1 for r in results.values() if r['status'] in ['json_error', 'wrapper_error', 'json_missing'])

print(f'Total Calculators: {len(results)}')
print(f'Aligned: {aligned}')
print(f'Mismatched: {mismatched}')
print(f'Errors: {errors}')
print()

if mismatched > 0:
    print('CALCULATORS WITH MISMATCHES:')
    for name, result in results.items():
        if result['status'] == 'mismatches':
            print(f'  - {name}: {result["count"]} mismatch(es)')
