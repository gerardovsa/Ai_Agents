"""
Comprehensive test for the 4 calculators that had import errors
Tests: bollard_signs, construction_signs, custom_vinyl_stickers, notepads_a4
"""
from tools.registry_v3 import RegistryV3

r = RegistryV3()

print('\n' + '='*70)
print('TESTING 4 CALCULATORS THAT HAD IMPORT ERRORS (MODULE NOT FOUND)')
print('='*70)

passed = 0
failed = 0

# Test 1: Bollard Signs
print('\n1. Testing calculate_bollard_signs...')
try:
    result = r.execute_tool(
        tool_name='calculate_bollard_signs',
        quantity=100,
        material='3mm Corflute',
        size='270mm W x 1000mm H - Three Sided'
    )
    if result.get('success'):
        print(f'   ✅ SUCCESS: ${result.get("total_price", 0):.2f}')
        print(f'      Unit: ${result.get("unit_price", 0):.2f}')
        passed += 1
    else:
        print(f'   ❌ FAILED: {result.get("error", "Unknown error")}')
        failed += 1
except Exception as e:
    print(f'   ❌ EXCEPTION: {str(e)}')
    failed += 1

# Test 2: Construction Signs
print('\n2. Testing calculate_construction_signs...')
try:
    result = r.execute_tool(
        tool_name='calculate_construction_signs',
        quantity=10,
        size='600mm x 450mm',
        material='3mm Corflute',
        print_sides='Single Sided'
    )
    if result.get('success'):
        print(f'   ✅ SUCCESS: ${result.get("total_price", 0):.2f}')
        print(f'      Unit: ${result.get("unit_price", 0):.2f}')
        passed += 1
    else:
        print(f'   ❌ FAILED: {result.get("error", "Unknown error")}')
        failed += 1
except Exception as e:
    print(f'   ❌ EXCEPTION: {str(e)}')
    failed += 1

# Test 3: Custom Vinyl Stickers
print('\n3. Testing calculate_custom_vinyl_stickers...')
try:
    result = r.execute_tool(
        tool_name='calculate_custom_vinyl_stickers',
        quantity=100,
        size='75mm x 75mm',
        finish='Gloss',
        cut_type='Cut to Shape'
    )
    if result.get('success'):
        print(f'   ✅ SUCCESS: ${result.get("total_price", 0):.2f}')
        print(f'      Unit: ${result.get("unit_price", 0):.2f}')
        passed += 1
    else:
        print(f'   ❌ FAILED: {result.get("error", "Unknown error")}')
        failed += 1
except Exception as e:
    print(f'   ❌ EXCEPTION: {str(e)}')
    failed += 1

# Test 4: Notepads A4
print('\n4. Testing calculate_notepads_a4...')
try:
    result = r.execute_tool(
        tool_name='calculate_notepads_a4',
        quantity=50,
        sheets=50,
        print_type='Black Only',
        backing='Grey Board Backing'
    )
    if result.get('success'):
        print(f'   ✅ SUCCESS: ${result.get("total_price", 0):.2f}')
        print(f'      Unit: ${result.get("unit_price", 0):.2f}')
        passed += 1
    else:
        print(f'   ❌ FAILED: {result.get("error", "Unknown error")}')
        failed += 1
except Exception as e:
    print(f'   ❌ EXCEPTION: {str(e)}')
    failed += 1

# Summary
print('\n' + '='*70)
print('TEST SUMMARY')
print('='*70)
print(f'Passed: {passed}/4')
print(f'Failed: {failed}/4')
print(f'Success Rate: {(passed/4)*100:.1f}%')

if passed == 4:
    print('\n✅ ALL 4 CALCULATORS NOW WORKING - Import fixes successful!')
    exit(0)
else:
    print(f'\n❌ {failed} CALCULATOR(S) STILL BROKEN - Import fixes incomplete')
    exit(1)
