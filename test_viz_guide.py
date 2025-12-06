"""Test visualization_guide tool for all 7 types"""
import sys
sys.path.insert(0, 'tools/implementations')
from visualization_guide import visualization_guide

# Test all 7 visualization types
types_to_test = ['molecule', 'latex', 'svg', 'blueprint', 'cad', 'schematic', 'execute_html']

print("\n" + "="*80)
print("VISUALIZATION GUIDE TOOL - COMPREHENSIVE TEST")
print("="*80 + "\n")

for viz_type in types_to_test:
    result = visualization_guide(viz_type)
    
    if result.get('success'):
        data = result['data']
        
        # Check required fields
        has_delimiter = 'delimiter' in data
        has_description = 'description' in data
        has_rules = 'rules' in data and len(data['rules']) >= 5
        has_examples = 'examples' in data and len(data['examples']) >= 1
        has_best_practices = 'best_practices' in data
        has_when_to_use = 'when_to_use' in data
        has_common_errors = 'common_errors' in data
        
        # Check example has code
        example_has_code = False
        if has_examples:
            example_has_code = 'code' in data['examples'][0] and len(data['examples'][0]['code']) > 50
        
        all_checks = all([has_delimiter, has_description, has_rules, has_examples, 
                         has_best_practices, has_when_to_use, has_common_errors, example_has_code])
        
        status = "✓ PASS" if all_checks else "✗ FAIL"
        
        print(f"{viz_type.upper():15} {status}")
        print(f"  Delimiter:       {'✓' if has_delimiter else '✗'}")
        print(f"  Description:     {'✓' if has_description else '✗'}")
        print(f"  Rules (≥5):      {'✓' if has_rules else '✗'} ({len(data.get('rules', []))} rules)")
        print(f"  Examples (≥1):   {'✓' if has_examples else '✗'} ({len(data.get('examples', []))} examples)")
        print(f"  Example Code:    {'✓' if example_has_code else '✗'}")
        print(f"  Best Practices:  {'✓' if has_best_practices else '✗'}")
        print(f"  When to Use:     {'✓' if has_when_to_use else '✗'}")
        print(f"  Common Errors:   {'✓' if has_common_errors else '✗'}")
        
        # Show delimiter
        if has_delimiter:
            print(f"  Delimiter: {data['delimiter']}")
        
        # Show first rule
        if has_rules:
            print(f"  First Rule: {data['rules'][0]}")
        
        print()
    else:
        print(f"{viz_type.upper():15} ✗ FAIL - {result.get('error')}\n")

print("="*80)
print("TEST COMPLETE")
print("="*80 + "\n")
