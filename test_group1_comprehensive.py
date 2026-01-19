"""Comprehensive test for Group 1 calculators with validation checks"""
import sys
sys.path.insert(0, r'c:\Users\gpoli\GIT\AI_Agents_V11\AI_agents\UI\modules_external\quote-calculator\implementations')
sys.path.insert(0, r'c:\Users\gpoli\GIT\AI_Agents_V11\AI_agents\UI\modules_external\quote-calculator\backend\shopify_calculators')

from calculator_wrapper import (
    calculate_folded_flyers_shopify,
    calculate_economical_business_cards_shopify,
    calculate_premium_business_cards_shopify,
    calculate_printed_letterheads,
    calculate_with_compliments_slips
)

def test_calculator_comprehensive(name, func, new_params, legacy_params, required_params):
    """Comprehensive test including validation checks"""
    print(f"\n{'='*70}")
    print(f"TESTING: {name}")
    print(f"{'='*70}")
    
    passed = 0
    total = 4
    
    # Test 1: New parameters
    print(f"\n[Test 1: New Parameters]")
    try:
        result = func(**new_params)
        if result['success']:
            print(f"✅ PASS - Price: ${result['total_price']:.2f}, Warnings: {len(result.get('warnings', []))}")
            passed += 1
        else:
            print(f"❌ FAIL: {result['error']}")
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
    
    # Test 2: Legacy parameters
    print(f"\n[Test 2: Legacy Parameters]")
    try:
        result = func(**legacy_params)
        if result['success']:
            warnings = result.get('warnings', [])
            print(f"✅ PASS - Price: ${result['total_price']:.2f}, Warnings: {len(warnings)}")
            if warnings:
                for w in warnings[:2]:  # Show first 2 warnings
                    print(f"   - {w.get('deprecated')} → {w.get('use_instead')}")
            passed += 1
        else:
            print(f"❌ FAIL: {result['error']}")
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
    
    # Test 3: Price consistency
    print(f"\n[Test 3: Price Consistency]")
    try:
        result_new = func(**new_params)
        result_legacy = func(**legacy_params)
        if result_new['success'] and result_legacy['success']:
            if abs(result_new['total_price'] - result_legacy['total_price']) < 0.01:
                print(f"✅ PASS - Prices match: ${result_new['total_price']:.2f}")
                passed += 1
            else:
                print(f"❌ FAIL - Price mismatch: ${result_new['total_price']:.2f} vs ${result_legacy['total_price']:.2f}")
        else:
            print(f"❌ FAIL - One or both calls failed")
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
    
    # Test 4: Missing required parameter validation
    print(f"\n[Test 4: Missing Required Parameter]")
    try:
        # Call with only quantity, omit required param
        test_params = {'quantity': new_params['quantity']}
        result = func(**test_params)
        if not result['success'] and 'Missing required parameter' in result.get('error', ''):
            print(f"✅ PASS - Correctly rejected: {result['error']}")
            passed += 1
        elif not result['success']:
            print(f"⚠️  PARTIAL - Rejected but error unclear: {result['error']}")
            passed += 0.5
        else:
            print(f"❌ FAIL - Should have rejected missing param but succeeded")
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
    
    return passed, total

# ============================================================================
# GROUP 1 COMPREHENSIVE TESTS
# ============================================================================

print("\n" + "="*70)
print("GROUP 1 COMPREHENSIVE TEST - With Validation Checks")
print("="*70)

results = {}

# Calculator 1: Folded Flyers
passed, total = test_calculator_comprehensive(
    "Folded Flyers",
    calculate_folded_flyers_shopify,
    {
        'quantity': 1000,
        'size': 'A4',
        'stock': 'Satin 150GSM',
        'print_type': 'Colour',
        'celloglaze': '2 Side Matt',
        'folding': '4pp A4 to DL',
        'artworks': 1
    },
    {
        'quantity': 1000,
        'colour': True,  # Legacy
        'cellophane': 'Matt',  # Legacy
        'fold_type': '4pp A4 to DL',  # Legacy
        'artworks': 1,
        # Still need size and stock as they don't have legacy aliases
        'size': 'A4',
        'stock': 'Satin 150GSM'
    },
    ['size', 'stock', 'print_type']
)
results['folded_flyers'] = (passed, total)

# Calculator 2: Economical Business Cards
passed, total = test_calculator_comprehensive(
    "Economical Business Cards",
    calculate_economical_business_cards_shopify,
    {
        'quantity': 1000,
        'print_type': 'Colour',
        'celloglaze': 'None',
        'artworks': 1
    },
    {
        'quantity': 1000,
        'colour': True,  # Legacy
        'celloglaze': 'None',
        'artworks': 1
    },
    ['print_type']
)
results['economical_business_cards'] = (passed, total)

# Calculator 3: Premium Business Cards
passed, total = test_calculator_comprehensive(
    "Premium Business Cards",
    calculate_premium_business_cards_shopify,
    {
        'quantity': 1000,
        'print_type': 'Colour',
        'paper_stock': 'Satin 350GSM',  # Correct format without underscore
        'celloglaze': 'None',
        'artworks': 1
    },
    {
        'quantity': 1000,
        'colour': True,  # Legacy
        'stock': 'Satin 350GSM',  # Legacy (correct format)
        'celloglaze': 'None',
        'artworks': 1
    },
    ['print_type', 'paper_stock']
)
results['premium_business_cards'] = (passed, total)

# Calculator 4: Printed Letterheads
passed, total = test_calculator_comprehensive(
    "Printed Letterheads",
    calculate_printed_letterheads,
    {
        'quantity': 500,
        'print_type': 'Colour',
        'paper_stock': 'Uncoated Bond 100GSM',
        'artworks': 1
    },
    {
        'quantity': 500,
        'paper_stock_type': 'Uncoated Bond 100GSM',  # Legacy
        'artworks': 1
    },
    ['paper_stock']
)
results['printed_letterheads'] = (passed, total)

# Calculator 5: With Compliments Slips
passed, total = test_calculator_comprehensive(
    "With Compliments Slips",
    calculate_with_compliments_slips,
    {
        'quantity': 500,
        'print_type': 'Colour',
        'paper_stock': 'Uncoated Bond 100GSM',
        'artworks': 1
    },
    {
        'quantity': 500,
        'paper_stock_type': 'Uncoated Bond 100GSM',  # Legacy
        'artworks': 1
    },
    ['paper_stock']
)
results['with_compliments_slips'] = (passed, total)

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("GROUP 1 COMPREHENSIVE TEST SUMMARY")
print("="*70)

total_passed = sum(p for p, t in results.values())
total_tests = sum(t for p, t in results.values())

print(f"\nOverall Score: {total_passed}/{total_tests} ({total_passed/total_tests*100:.1f}%)")
print(f"\nDetailed Results:")
for calc, (passed, total) in results.items():
    percentage = (passed/total*100) if total > 0 else 0
    status = "✅ EXCELLENT" if passed == total else "⚠️  NEEDS WORK" if passed >= total * 0.75 else "❌ FAILING"
    print(f"  {status} - {calc}: {passed}/{total} ({percentage:.0f}%)")

if total_passed == total_tests:
    print(f"\n🎉 GROUP 1 PERFECT! All {total_tests} tests passed!")
else:
    print(f"\n⚠️  {total_tests - total_passed} tests need attention")
