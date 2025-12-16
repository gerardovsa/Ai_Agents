"""
Extract pricing catalog from all Shopify calculators
This script analyzes Python files to extract pricing constants and parameters
"""

import os
import re
import json
from pathlib import Path
from decimal import Decimal

# Path to Shopify calculators
CALC_DIR = Path("UI/modules_external/quote-calculator/backend/shopify_calculators")

def extract_decimal_assignments(content):
    """Extract all Decimal() assignments from Python code"""
    pattern = r"(\w+)\s*=\s*Decimal\('([\d.]+)'\)"
    matches = re.findall(pattern, content)
    return {name: float(value) for name, value in matches}

def extract_dict_definitions(content):
    """Extract dictionary definitions with pricing data"""
    # Pattern for dict assignments like: material_map = {'aluminium': Decimal('28.00'), ...}
    dict_pattern = r"(\w+)\s*=\s*\{([^}]+)\}"
    dicts = {}
    
    for match in re.finditer(dict_pattern, content):
        dict_name = match.group(1)
        dict_content = match.group(2)
        
        # Extract key-value pairs
        kv_pattern = r"'([^']+)':\s*Decimal\('([\d.]+)'\)"
        pairs = re.findall(kv_pattern, dict_content)
        
        if pairs:
            dicts[dict_name] = {k: float(v) for k, v in pairs}
    
    return dicts

def extract_function_signatures(content):
    """Extract calculate() function parameters"""
    pattern = r"def calculate\(self,([^)]+)\)"
    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
    
    if not matches:
        return []
    
    params_str = matches[0]
    params = []
    
    # Parse each parameter
    for line in params_str.split(','):
        line = line.strip()
        if not line or line == 'self':
            continue
        
        # Extract parameter name and default value
        if '=' in line:
            parts = line.split('=')
            param_name = parts[0].strip().rstrip(':').strip()
            default_value = parts[1].strip().strip('"').strip("'")
            param_type = 'str' if '"' in parts[1] or "'" in parts[1] else 'int'
        else:
            param_name = line.strip().rstrip(':').strip()
            default_value = None
            param_type = 'unknown'
        
        params.append({
            'name': param_name,
            'default': default_value,
            'type': param_type
        })
    
    return params

def extract_tiered_pricing(content):
    """Extract tiered pricing structures (profit margins, padding rates)"""
    tiers = {}
    
    # Look for if/elif chains with numeric comparisons
    tier_pattern = r"if\s+(\w+)\s*<=\s*(\d+):\s*return\s+Decimal\('([\d.]+)'\)"
    matches = re.findall(tier_pattern, content)
    
    if matches:
        tier_list = []
        for var, threshold, rate in matches:
            tier_list.append({
                'threshold': int(threshold),
                'rate': float(rate)
            })
        if tier_list:
            tiers['profit_margin_tiers'] = tier_list
    
    return tiers

def extract_comments_and_docs(content):
    """Extract key comments explaining pricing logic"""
    # Extract docstring
    docstring_pattern = r'"""([^"]+)"""'
    docstrings = re.findall(docstring_pattern, content, re.DOTALL)
    
    # Extract key features from comments
    features = []
    if 'DOUBLE GST' in content:
        features.append('DOUBLE_GST_APPLICATION')
    if 'DUAL profit' in content or 'dual profit' in content:
        features.append('DUAL_PROFIT_STRUCTURE')
    if 'tiered' in content.lower():
        features.append('TIERED_PRICING')
    
    return {
        'docstring': docstrings[0][:200] if docstrings else '',
        'features': features
    }

def analyze_calculator(filepath):
    """Analyze a single calculator file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    calculator_name = filepath.stem.replace('_Shopify_Calculator', '').replace('_calculator_shopify', '')
    
    data = {
        'name': calculator_name,
        'file': filepath.name,
        'pricing_constants': extract_decimal_assignments(content),
        'pricing_dicts': extract_dict_definitions(content),
        'parameters': extract_function_signatures(content),
        'tiered_pricing': extract_tiered_pricing(content),
        'metadata': extract_comments_and_docs(content)
    }
    
    return data

def main():
    """Extract all calculator data"""
    all_calculators = []
    
    calc_files = list(CALC_DIR.glob('*Calculator*.py'))
    calc_files = [f for f in calc_files if f.name != '__init__.py']
    
    print(f"Found {len(calc_files)} calculator files\n")
    print("=" * 80)
    
    for calc_file in sorted(calc_files):
        print(f"\nProcessing: {calc_file.name}")
        try:
            data = analyze_calculator(calc_file)
            all_calculators.append(data)
            
            # Print summary
            print(f"  Parameters: {len(data['parameters'])}")
            print(f"  Pricing Constants: {len(data['pricing_constants'])}")
            print(f"  Pricing Dicts: {len(data['pricing_dicts'])}")
            print(f"  Features: {', '.join(data['metadata']['features']) if data['metadata']['features'] else 'None'}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Save to JSON
    output_file = 'CALCULATOR_PRICING_CATALOG_EXTRACTED.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_calculators, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 80)
    print(f"\n✅ Extracted {len(all_calculators)} calculators")
    print(f"📄 Saved to: {output_file}")
    
    # Summary statistics
    total_params = sum(len(c['parameters']) for c in all_calculators)
    total_constants = sum(len(c['pricing_constants']) for c in all_calculators)
    total_dicts = sum(len(c['pricing_dicts']) for c in all_calculators)
    
    print(f"\n📊 CATALOG STATISTICS:")
    print(f"   Total Parameters: {total_params}")
    print(f"   Total Pricing Constants: {total_constants}")
    print(f"   Total Pricing Dictionaries: {total_dicts}")
    print(f"   Total Unique Values: {total_params + total_constants + total_dicts}")

if __name__ == '__main__':
    main()
