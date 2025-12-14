"""Test the 4 calculator fixes"""
from tools.registry_v3 import RegistryV3

r = RegistryV3()

print('\n' + '='*70)
print('TESTING 4 CALCULATOR FIXES')
print('='*70)

passed = 0
failed = 0

# Test 1: Notepads A5 (Decimal serialization)
print('\n1. Testing calculate_notepads_a5...')
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
        # Verify serialization
        import json
        json.dumps(result)
        print(f'      Serialization: OK')
        passed += 1
    else:
        print(f'   ❌ FAILED: {result.get("error", "Unknown")}')
        failed += 1
except Exception as e:
    print(f'   ❌ EXCEPTION: {str(e)}')
    failed += 1

# Test 2: With Compliments Slips (Decimal serialization)
print('\n2. Testing calculate_with_compliments_slips...')
try:
    result = r.execute_tool(
        tool_name='calculate_with_compliments_slips',
        quantity=500,
        print_type='Black Only',
        paper_stock='Standard',
        artworks=1
    )
    if result.get('success'):
        print(f'   ✅ SUCCESS: ${result.get("total_price", 0):.2f}')
        # Verify serialization
        import json
        json.dumps(result)
        print(f'      Serialization: OK')
        passed += 1
    else:
        print(f'   ❌ FAILED: {result.get("error", "Unknown")}')
        failed += 1
except Exception as e:
    print(f'   ❌ EXCEPTION: {str(e)}')
    failed += 1

# Test 3: Corflute Signs GOD (missing args fix)
print('\n3. Testing calculate_corflute_signs_god...')
try:
    result = r.execute_tool(
        tool_name='calculate_corflute_signs_god',
        quantity=10,
        width=600,
        height=900,
        thickness=5,
        print_sides='double'
    )
    if result.get('success'):
        print(f'   ✅ SUCCESS: ${result.get("total_cost_inc_gst", 0):.2f}')
        passed += 1
    else:
        print(f'   ❌ FAILED: {result.get("error", "Unknown")}')
        failed += 1
except Exception as e:
    print(f'   ❌ EXCEPTION: {str(e)}')
    failed += 1

# Test 4: Perfect Bound Books GOD (missing args fix)
print('\n4. Testing calculate_perfect_bound_books_god...')
try:
    result = r.execute_tool(
        tool_name='calculate_perfect_bound_books_god',
        quantity=100,
        pages=100,
        book_width=210,
        book_height=297,
        cover_gsm=300,
        inner_gsm=80
    )
    if result.get('success'):
        print(f'   ✅ SUCCESS: ${result.get("total_cost_inc_gst", 0):.2f}')
        passed += 1
    else:
        print(f'   ❌ FAILED: {result.get("error", "Unknown")}')
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

if passed == 4:
    print('\n✅ ALL 4 FIXES SUCCESSFUL!')
    exit(0)
else:
    print(f'\n❌ {failed} STILL BROKEN')
    exit(1)
