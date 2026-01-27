"""
Compare backend calculator parameters vs JSON specifications
This checks if backends use all JSON fields or simplified APIs
"""
import json
import re
from pathlib import Path

# Calculator mapping
CALCULATORS = {
    'bollard_signs': {
        'json': r'UI\modules_external\quote-calculator\ARCHIVE_CONSOLIDATED\CALCULATOR_JSONS\shopify\Shopify_Bollard_Signs.json',
        'backend': r'UI\modules_external\quote-calculator\backend\shopify_calculators\BollardSigns_Shopify_Calculator.py',
        'json_key': 'shopify_bollard_signs'
    },
    'custom_vinyl_stickers': {
        'json': r'UI\modules_external\quote-calculator\ARCHIVE_CONSOLIDATED\CALCULATOR_JSONS\shopify\Shopify_Custom_Vinyl_Stickers.json',
        'backend': r'UI\modules_external\quote-calculator\backend\shopify_calculators\CustomVinylStickers_Shopify_Calculator.py',
        'json_key': 'shopify_custom_vinyl_stickers'
    }
}

def get_json_fields(json_path, json_key):
    """Extract field names from JSON"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    options = data[json_key]['options']
    return [opt['name'] for opt in options]

def get_backend_params(backend_path):
    """Extract parameters from backend calculate() method"""
    with open(backend_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find calculate method and extract kwargs.get() calls
    match = re.search(r'def calculate\(self,.*?\):(.*?)(?=\n    def|\Z)', content, re.DOTALL)
    if not match:
        return []
    
    method_body = match.group(1)
    
    # Find all kwargs.get('param_name') calls
    params = re.findall(r"kwargs\.get\(['\"](\w+)['\"]", method_body)
    return list(set(params))  # Unique params

print("="*80)
print("BACKEND PARAMETER ANALYSIS")
print("="*80)

for calc_name, paths in CALCULATORS.items():
    print(f"\n{calc_name.upper().replace('_', ' ')}")
    print("-" * 80)
    
    try:
        json_fields = get_json_fields(paths['json'], paths['json_key'])
        backend_params = get_backend_params(paths['backend'])
        
        print(f"\nJSON Fields ({len(json_fields)}):")
        for field in json_fields:
            print(f"  - {field}")
        
        print(f"\nBackend Parameters ({len(backend_params)}):")
        for param in backend_params:
            print(f"  - {param}")
        
        # Check coverage
        json_lower = [f.lower().replace(' ', '_').replace('(', '').replace(')', '') for f in json_fields]
        backend_lower = [p.lower() for p in backend_params]
        
        missing = [f for f, fl in zip(json_fields, json_lower) if fl not in backend_lower]
        
        if missing:
            print(f"\n⚠️ BACKEND IGNORES {len(missing)} JSON FIELDS:")
            for field in missing:
                print(f"  - {field}")
        else:
            print(f"\n✅ Backend uses all JSON fields")
        
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*80)
print("CONCLUSION: If backend ignores JSON fields, wrapper should match backend API, not JSON!")
print("="*80)
