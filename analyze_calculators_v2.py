"""
Comprehensive Calculator System Analysis - FIXED VERSION
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# Load schema
schema_path = Path('UI/modules_external/quote-calculator/schema/calculator_tools.json')
with open(schema_path, 'r', encoding='utf-8') as f:
    schema = json.load(f)

# Load wrapper
wrapper_path = Path('UI/modules_external/quote-calculator/implementations/calculator_wrapper.py')
wrapper_content = wrapper_path.read_text(encoding='utf-8')

print("=" * 100)
print("CALCULATOR SYSTEM COMPREHENSIVE ANALYSIS")
print("=" * 100)
print()

# Extract all functions
func_pattern = r'^def (calculate_\w+|get_stock_list)\('
wrapper_functions = re.findall(func_pattern, wrapper_content, re.MULTILINE)

schema_tools = [t['name'] for t in schema['tools']]

print(f"📊 OVERVIEW:")
print(f"   Schema tools: {len(schema_tools)}")
print(f"   Wrapper functions: {len(wrapper_functions)}")
print()

# Check completeness
schema_set = set(schema_tools)
wrapper_set = set(wrapper_functions)

missing_in_wrapper = schema_set - wrapper_set
missing_in_schema = wrapper_set - schema_set

if missing_in_wrapper:
    print(f"❌ {len(missing_in_wrapper)} tools in SCHEMA but NOT WRAPPER:")
    for t in sorted(missing_in_wrapper):
        print(f"   - {t}")
    print()

if missing_in_schema:
    print(f"⚠️  {len(missing_in_schema)} tools in WRAPPER but NOT SCHEMA:")
    for t in sorted(missing_in_schema):
        print(f"   - {t}")
    print()

# Deep parameter analysis
print("=" * 100)
print("PARAMETER MISMATCH ANALYSIS")
print("=" * 100)
print()

for tool in schema['tools']:
    name = tool['name']
    
    # Find function definition in wrapper
    func_def_pattern = rf'^def {name}\((.*?)\):'
    match = re.search(func_def_pattern, wrapper_content, re.MULTILINE | re.DOTALL)
    
    if not match:
        continue
    
    # Parse wrapper parameters
    params_block = match.group(1)
    wrapper_params = {}
    
    for line in params_block.split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line == '**kwargs':
            continue
        
        # Parse: param_name: type = default
        param_match = re.match(r'(\w+)\s*:\s*(\w+)', line)
        if param_match:
            param_name = param_match.group(1)
            param_type = param_match.group(2)
            wrapper_params[param_name] = param_type
    
    # Compare with schema
    schema_params = tool.get('parameters', {}).get('properties', {})
    
    issues = []
    
    # Check each schema parameter
    for schema_param, schema_def in schema_params.items():
        if schema_param not in wrapper_params:
            issues.append(f"   ⚠️  Schema has '{schema_param}' but wrapper doesn't")
            continue
        
        schema_type = schema_def.get('type', 'unknown')
        wrapper_type = wrapper_params[schema_param]
        
        # Type mapping check
        type_map = {
            'integer': 'int',
            'string': 'str',
            'boolean': 'bool',
            'number': 'float',
            'array': 'list',
            'object': 'dict'
        }
        
        expected_wrapper_type = type_map.get(schema_type)
        
        if expected_wrapper_type and wrapper_type != expected_wrapper_type:
            issues.append(
                f"   ❌ TYPE MISMATCH: '{schema_param}' - "
                f"Schema={schema_type}, Wrapper={wrapper_type} "
                f"(expected {expected_wrapper_type})"
            )
    
    # Check for wrapper-only parameters (excluding kwargs)
    for wrapper_param in wrapper_params:
        if wrapper_param not in schema_params:
            issues.append(f"   ⚠️  Wrapper has '{wrapper_param}' but schema doesn't")
    
    if issues:
        print(f"\n{name}:")
        for issue in issues:
            print(issue)

# Enum coverage analysis
print("\n" + "=" * 100)
print("ENUM COVERAGE ANALYSIS")
print("=" * 100)
print()

tools_with_enums = 0
tools_without_enums = []
total_params_with_enums = 0
tools_needing_enums = []

for tool in schema['tools']:
    name = tool['name']
    params = tool.get('parameters', {}).get('properties', {})
    
    has_enum = False
    enum_count = 0
    missing_enums = []
    
    for param_name, param_def in params.items():
        if 'enum' in param_def:
            has_enum = True
            enum_count += 1
            total_params_with_enums += 1
        else:
            # Check if parameter should have enum
            param_type = param_def.get('type')
            description = param_def.get('description', '').lower()
            
            # Heuristics for parameters that should have enums
            should_have_enum = (
                param_name == 'quantity' or
                param_name in ['size', 'stock', 'finish_size', 'print_type', 'celloglaze', 'binding_type'] or
                'select' in description or
                'choose' in description or
                'options:' in description or
                'e.g.' in description and ',' in description
            )
            
            if should_have_enum:
                missing_enums.append(param_name)
    
    if has_enum:
        tools_with_enums += 1
    else:
        tools_without_enums.append(name)
    
    if missing_enums:
        tools_needing_enums.append({
            'tool': name,
            'missing': missing_enums
        })

print(f"✅ Tools with at least one enum: {tools_with_enums}/{len(schema['tools'])}")
print(f"✅ Total parameters with enums: {total_params_with_enums}")
print()

if tools_needing_enums:
    print(f"⚠️  {len(tools_needing_enums)} tools have parameters that SHOULD have enums:")
    for item in tools_needing_enums[:15]:  # Show first 15
        print(f"\n   {item['tool']}:")
        print(f"      Missing enums on: {', '.join(item['missing'])}")
    if len(tools_needing_enums) > 15:
        print(f"\n   ... and {len(tools_needing_enums) - 15} more tools")

# Backend calculator type check
print("\n" + "=" * 100)
print("BACKEND CALCULATOR TYPE CONSISTENCY")
print("=" * 100)
print()

backend_issues = []

for tool in schema['tools']:
    name = tool['name']
    
    # Find where calculator.calculate() is called in wrapper
    calc_call_pattern = rf'calculator\.calculate\((.*?)\)'
    
    # Find function body
    func_start = wrapper_content.find(f'def {name}(')
    if func_start == -1:
        continue
    
    # Find next function or end
    next_func = wrapper_content.find('\ndef ', func_start + 10)
    if next_func == -1:
        func_body = wrapper_content[func_start:]
    else:
        func_body = wrapper_content[func_start:next_func]
    
    # Look for str(quantity) conversion
    if 'quantity' in func_body:
        if 'str(quantity)' in func_body or 'quantity=str(' in func_body:
            backend_issues.append({
                'tool': name,
                'issue': 'Converts quantity to string before backend call',
                'note': 'Backend expects string but schema defines integer'
            })

if backend_issues:
    print(f"⚠️  Found {len(backend_issues)} quantity type conversion patterns:")
    for item in backend_issues:
        print(f"\n   {item['tool']}:")
        print(f"      {item['issue']}")
        print(f"      {item['note']}")
else:
    print("✅ No string conversion issues found (all consistent)")

# Summary
print("\n" + "=" * 100)
print("🎯 SUMMARY & RECOMMENDATIONS")
print("=" * 100)
print()

total_issues = (
    len(missing_in_wrapper) + 
    len(missing_in_schema) +
    len(tools_needing_enums) +
    len(backend_issues)
)

if total_issues == 0:
    print("✅ EXCELLENT! Calculator system is fully consistent!")
    print("   - All schema tools have implementations")
    print("   - All parameters match between schema and wrapper")
    print("   - Type conversions are handled correctly")
else:
    print(f"⚠️  Found {total_issues} areas needing attention:")
    print()
    
    if missing_in_wrapper:
        print(f"   1. {len(missing_in_wrapper)} missing wrapper implementations")
    
    if missing_in_schema:
        print(f"   2. {len(missing_in_schema)} undocumented wrappers (not in schema)")
    
    if tools_needing_enums:
        print(f"   3. {len(tools_needing_enums)} tools could benefit from enum arrays")
        print("      → Recommendation: Add enum arrays to constrained parameters")
        print("      → This improves AI guidance and prevents invalid values")
    
    if backend_issues:
        print(f"   4. {len(backend_issues)} type conversion patterns found")
        print("      → Recommendation: Document why conversion is needed")
        print("      → Or make schema type match backend expectation")

print()
