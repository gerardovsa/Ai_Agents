"""Test the 3 fixed calculators: Saddle Stitch, Notepads A5, Notepads A6"""
from tools.registry_v3 import RegistryV3

r = RegistryV3()

print('\n' + '='*70)
print('TESTING 3 FIXED CALCULATORS')
print('='*70)

passed = 0
failed = 0

# Test 1: Saddle Stitch Books (syntax error fix)
print('\n1. Testing calculate_saddle_stitch_books (SYNTAX ERROR FIX)...')
try:
    result = r.execute_tool(
        tool_name='calculate_saddle_stitch_books',
        quantity=200,
        artworks=1,
        celloglaze='None',
        cover_stock='Satin 300GSM',
        finish_size='A5 Portrait',
        cover_option='Hard Cover',
        printed_pages='16pp',
        content_print_type='Black & White',
        cover_print_type='2 side colour (4pp)',
        content_stock_type='Uncoated Bond 80GSM'
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
    import traceback
    traceback.print_exc()
    failed += 1

# Test 2: Notepads A5 (Decimal serialization fix)
print('\n2. Testing calculate_notepads_a5 (JSON DECIMAL FIX)...')
try:
    result = r.execute_tool(
        tool_name='calculate_notepads_a5',
        quantity=50,
        sheets=50,
        print_type='Black Only',
        backing='Grey Board Backing'
    )
    if result.get('success'):
        print(f'   ✅ SUCCESS: ${result.get("total_price", 0):.2f}')
        print(f'      Unit: ${result.get("unit_price", 0):.2f}')
        # Check breakdown serialization
        breakdown = result.get('breakdown', {})
        print(f'      Breakdown serializable: {type(breakdown.get("profit_margin_rate")).__name__}')
        passed += 1
    else:
        print(f'   ❌ FAILED: {result.get("error", "Unknown error")}')
        failed += 1
except Exception as e:
    print(f'   ❌ EXCEPTION: {str(e)}')
    import traceback
    traceback.print_exc()
    failed += 1

# Test 3: Notepads A6 (Decimal serialization fix)
print('\n3. Testing calculate_notepads_a6 (JSON DECIMAL FIX)...')
try:
    result = r.execute_tool(
        tool_name='calculate_notepads_a6',
        quantity=50,
        sheets=50,
        print_type='Black Only',
        backing='Grey Board Backing'
    )
    if result.get('success'):
        print(f'   ✅ SUCCESS: ${result.get("total_price", 0):.2f}')
        print(f'      Unit: ${result.get("unit_price", 0):.2f}')
        # Check breakdown serialization
        breakdown = result.get('breakdown', {})
        print(f'      Breakdown serializable: {type(breakdown.get("profit_margin_rate")).__name__}')
        passed += 1
    else:
        print(f'   ❌ FAILED: {result.get("error", "Unknown error")}')
        failed += 1
except Exception as e:
    print(f'   ❌ EXCEPTION: {str(e)}')
    import traceback
    traceback.print_exc()
    failed += 1

# Summary
print('\n' + '='*70)
print('TEST SUMMARY')
print('='*70)
print(f'Passed: {passed}/3')
print(f'Failed: {failed}/3')
print(f'Success Rate: {(passed/3)*100:.1f}%')

if passed == 3:
    print('\n✅ ALL 3 FIXES SUCCESSFUL!')
    exit(0)
else:
    print(f'\n❌ {failed} CALCULATOR(S) STILL BROKEN')
    exit(1)
