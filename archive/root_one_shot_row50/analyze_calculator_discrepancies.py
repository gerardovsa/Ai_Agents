"""
Comprehensive Calculator System Analysis
Checks for discrepancies between:
1. Schema definitions (calculator_tools.json)
2. Wrapper implementations (calculator_wrapper.py)
3. Backend calculators (Shopify_Calculator.py files)
"""

import json
import re
import sys
from pathlib import Path

# Load schema
schema_path = Path('UI/modules_external/quote-calculator/schema/calculator_tools.json')
with open(schema_path, 'r', encoding='utf-8') as f:
    schema = json.load(f)

# Load wrapper
wrapper_path = Path('UI/modules_external/quote-calculator/implementations/calculator_wrapper.py')
wrapper_content = wrapper_path.read_text(encoding='utf-8')

print("=" * 80)
print("CALCULATOR SYSTEM ANALYSIS - DISCREPANCY DETECTION")
print("=" * 80)
print()

# Extract all calculator functions from wrapper
wrapper_pattern = r'def (calculate_\w+)\((.*?)\):'
wrapper_functions = {}
for match in re.finditer(wrapper_pattern, wrapper_content, re.MULTILINE):
    func_name = match.group(1)
    params_str = match.group(2)
    # Parse parameters
    params = []
    for line in params_str.split('\n'):
        line = line.strip()
        if ':' in line and not line.startswith('#'):
            param_name = line.split(':')[0].strip()
            if param_name and param_name != '**kwargs':
                params.append(param_name)
    wrapper_functions[func_name] = params

print(f"Schema Tools: {len(schema['tools'])}")
print(f"Wrapper Functions: {len(wrapper_functions)}")
print()

# Analysis 1: Missing tools
print("=" * 80)
print("ANALYSIS 1: SCHEMA vs WRAPPER COMPLETENESS")
print("=" * 80)
schema_tools = {t['name'] for t in schema['tools']}
wrapper_tools = set(wrapper_functions.keys())

missing_in_wrapper = schema_tools - wrapper_tools
missing_in_schema = wrapper_tools - schema_tools

if missing_in_wrapper:
    print(f"\n❌ {len(missing_in_wrapper)} tools in SCHEMA but NOT in WRAPPER:")
    for tool in sorted(missing_in_wrapper):
        print(f"   - {tool}")
else:
    print("\n✅ All schema tools have wrapper implementations")

if missing_in_schema:
    print(f"\n⚠️  {len(missing_in_schema)} tools in WRAPPER but NOT in SCHEMA:")
    for tool in sorted(missing_in_schema):
        print(f"   - {tool}")
else:
    print("✅ All wrapper functions are in schema")

# Analysis 2: Parameter mismatches
print("\n" + "=" * 80)
print("ANALYSIS 2: PARAMETER NAME MISMATCHES")
print("=" * 80)

mismatches = []
for tool in schema['tools']:
    name = tool['name']
    if name not in wrapper_functions:
        continue
    
    schema_params = set(tool.get('parameters', {}).get('properties', {}).keys())
    wrapper_params = set(wrapper_functions[name])
    
    # Remove common system params
    wrapper_params.discard('kwargs')
    
    schema_only = schema_params - wrapper_params
    wrapper_only = wrapper_params - schema_params
    
    if schema_only or wrapper_only:
        mismatches.append({
            'tool': name,
            'schema_only': schema_only,
            'wrapper_only': wrapper_only
        })

if mismatches:
    print(f"\n❌ Found {len(mismatches)} tools with parameter mismatches:")
    for m in mismatches:
        print(f"\n   {m['tool']}:")
        if m['schema_only']:
            print(f"      Schema has: {', '.join(sorted(m['schema_only']))}")
        if m['wrapper_only']:
            print(f"      Wrapper has: {', '.join(sorted(m['wrapper_only']))}")
else:
    print("\n✅ All parameters match between schema and wrapper")

# Analysis 3: Quantity type consistency
print("\n" + "=" * 80)
print("ANALYSIS 3: QUANTITY PARAMETER TYPE CONSISTENCY")
print("=" * 80)

type_issues = []
for tool in schema['tools']:
    name = tool['name']
    params = tool.get('parameters', {}).get('properties', {})
    
    if 'quantity' in params:
        qty_type = params['quantity'].get('type')
        has_enum = 'enum' in params['quantity']
        
        # Check if wrapper converts to string
        wrapper_section_start = wrapper_content.find(f'def {name}(')
        if wrapper_section_start > 0:
            wrapper_section = wrapper_content[wrapper_section_start:wrapper_section_start + 2000]
            converts_to_str = 'str(quantity)' in wrapper_section or 'quantity=str(' in wrapper_section
            
            if qty_type == 'integer' and converts_to_str:
                type_issues.append({
                    'tool': name,
                    'issue': 'Schema says integer but wrapper converts to string',
                    'schema_type': qty_type,
                    'has_enum': has_enum
                })

if type_issues:
    print(f"\n⚠️  Found {len(type_issues)} quantity type conversion issues:")
    for issue in type_issues:
        print(f"\n   {issue['tool']}:")
        print(f"      Schema: {issue['schema_type']}")
        print(f"      Wrapper: Converts to string")
        print(f"      Has enum: {issue['has_enum']}")
else:
    print("\n✅ All quantity types are consistent")

# Analysis 4: Enum preservation
print("\n" + "=" * 80)
print("ANALYSIS 4: ENUM ARRAYS IN SCHEMA")
print("=" * 80)

enum_stats = {
    'tools_with_enums': 0,
    'total_enum_params': 0,
    'tools_without_enums': []
}

for tool in schema['tools']:
    name = tool['name']
    params = tool.get('parameters', {}).get('properties', {})
    
    has_any_enum = False
    enum_count = 0
    for param_name, param_def in params.items():
        if 'enum' in param_def:
            has_any_enum = True
            enum_count += 1
    
    if has_any_enum:
        enum_stats['tools_with_enums'] += 1
        enum_stats['total_enum_params'] += enum_count
    else:
        enum_stats['tools_without_enums'].append(name)

print(f"\n✅ Tools with enums: {enum_stats['tools_with_enums']}/{len(schema['tools'])}")
print(f"✅ Total enum parameters: {enum_stats['total_enum_params']}")

if enum_stats['tools_without_enums']:
    print(f"\n⚠️  {len(enum_stats['tools_without_enums'])} tools have NO enum arrays:")
    for tool in enum_stats['tools_without_enums'][:10]:
        print(f"   - {tool}")
    if len(enum_stats['tools_without_enums']) > 10:
        print(f"   ... and {len(enum_stats['tools_without_enums']) - 10} more")

# Analysis 5: Decorator consistency
print("\n" + "=" * 80)
print("ANALYSIS 5: @calculator_wrapper DECORATOR USAGE")
print("=" * 80)

decorator_pattern = r'@calculator_wrapper\(quantity_enum=\[(.*?)\]\)'
decorators = {}
for match in re.finditer(decorator_pattern, wrapper_content):
    enum_values = match.group(1)
    # Find next function
    pos = match.end()
    next_func = re.search(r'def (calculate_\w+)\(', wrapper_content[pos:pos+500])
    if next_func:
        func_name = next_func.group(1)
        enum_list = [int(x.strip()) for x in enum_values.split(',')]
        decorators[func_name] = enum_list

print(f"\nFound {len(decorators)} functions with @calculator_wrapper decorator")

decorator_mismatches = []
for tool in schema['tools']:
    name = tool['name']
    params = tool.get('parameters', {}).get('properties', {})
    
    if 'quantity' in params and 'enum' in params['quantity']:
        schema_enum = params['quantity']['enum']
        decorator_enum = decorators.get(name)
        
        if decorator_enum and schema_enum != decorator_enum:
            decorator_mismatches.append({
                'tool': name,
                'schema': schema_enum,
                'decorator': decorator_enum
            })

if decorator_mismatches:
    print(f"\n❌ Found {len(decorator_mismatches)} decorator/schema enum mismatches:")
    for m in decorator_mismatches:
        print(f"\n   {m['tool']}:")
        print(f"      Schema enum: {m['schema']}")
        print(f"      Decorator enum: {m['decorator']}")
else:
    print("\n✅ All decorators match schema enums")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

issues_found = (
    len(missing_in_wrapper) +
    len(missing_in_schema) +
    len(mismatches) +
    len(type_issues) +
    len(decorator_mismatches)
)

print(f"\n Total Issues Found: {issues_found}")
print(f"   - Missing in wrapper: {len(missing_in_wrapper)}")
print(f"   - Missing in schema: {len(missing_in_schema)}")
print(f"   - Parameter mismatches: {len(mismatches)}")
print(f"   - Type conversion issues: {len(type_issues)}")
print(f"   - Decorator mismatches: {len(decorator_mismatches)}")

if issues_found == 0:
    print("\n✅ Calculator system is consistent!")
else:
    print(f"\n⚠️  Found {issues_found} issues that need attention")

print()
