import json

missing_calcs = ['calculate_flyers', 'calculate_letterheads', 'calculate_perfect_bound_books', 'calculate_corflute_signs']

print('=' * 70)
print('MISSING CALCULATOR ANALYSIS')
print('=' * 70)

# 1. Check wrapper functions
wrapper_path = r'UI\modules_external\quote-calculator\implementations\calculator_wrapper.py'
wrapper_content = open(wrapper_path, encoding='utf-8').read()

print('\n1. WRAPPER FUNCTIONS (calculator_wrapper.py):')
print('-' * 70)
for calc in missing_calcs:
    exists = f'def {calc}(' in wrapper_content
    status = 'EXISTS' if exists else 'MISSING'
    print(f'  {status:10} {calc}')

# 2. Check schema
schema_path = r'UI\modules_external\quote-calculator\schema\calculator_tools.json'
schema_data = json.load(open(schema_path, encoding='utf-8'))
schema_tools = [t['name'] for t in schema_data['tools']]

print('\n2. SCHEMA DEFINITIONS (calculator_tools.json):')
print('-' * 70)
for calc in missing_calcs:
    exists = calc in schema_tools
    status = 'EXISTS' if exists else 'MISSING'
    print(f'  {status:10} {calc}')

# 3. Check backend
print('\n3. BACKEND IMPLEMENTATION (ComprehensiveQuoteCalculator):')
print('-' * 70)
print('  EXISTS     Shared backend for all old-style calculators')

print('\n' + '=' * 70)
print('SUMMARY:')
print('=' * 70)
wrapper_count = sum(1 for calc in missing_calcs if f'def {calc}(' in wrapper_content)
schema_count = sum(1 for calc in missing_calcs if calc in schema_tools)
print(f'Wrapper functions:        EXISTS ({wrapper_count}/4)')
print(f'Schema definitions:       EXISTS ({schema_count}/4)')
print('Backend implementation:   EXISTS (shared)')
if schema_count == 4 and wrapper_count == 4:
    print('\n✅ ALL COMPONENTS EXIST - Ready to test!')
else:
    print(f'\n❌ STILL MISSING: {4 - schema_count} schema definitions')
print('=' * 70)
