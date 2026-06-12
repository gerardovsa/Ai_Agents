"""
Test All Group 4 Calculators (Signs & Displays)
Date: January 19, 2026
Tests the 3-part pattern implementation for all 5 calculators
"""

import sys
from pathlib import Path

# Add paths
wrapper_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'
sys.path.insert(0, str(wrapper_path))

from calculator_wrapper import (
    calculate_election_signs,
    calculate_construction_signs,
    calculate_bollard_signs,
    calculate_corflute_insert_a_frame,
    calculate_metal_face_a_frame
)

def test_calculator_comprehensive(calc_name, calc_func, test_params, default_test_params):
    """
    Test a calculator with 4 core tests
    
    Returns: (passed, total) tuple
    """
    print(f"\n{'='*70}")
    print(f"TESTING: {calc_name}")
    print(f"{'='*70}")
    
    passed = 0
    total = 4
    
    # Test 1: New Parameters Work
    print(f"\n[Test 1: New Parameters Work]")
    try:
        result = calc_func(**test_params)
        assert result['success'] == True, f"Failed: {result.get('error')}"
        assert result['total_price'] > 0, "Price should be > 0"
        price1 = result['total_price']
        print(f"✅ PASS - Price: ${price1:.2f}")
        passed += 1
    except AssertionError as e:
        print(f"❌ FAIL - {e}")
    except Exception as e:
        print(f"❌ FAIL - Unexpected error: {e}")
    
    # Test 2: Backend Defaults Work (None values)
    print(f"\n[Test 2: Backend Defaults Work (None values)]")
    try:
        result = calc_func(quantity=test_params['quantity'])
        assert result['success'] == True, f"Failed: {result.get('error')}"
        assert result['total_price'] > 0, "Price should be > 0"
        print(f"✅ PASS - Price: ${result['total_price']:.2f}, Defaults applied")
        passed += 1
    except AssertionError as e:
        print(f"❌ FAIL - {e}")
    except Exception as e:
        print(f"❌ FAIL - Unexpected error: {e}")
    
    # Test 3: Explicit vs Default Pricing Consistency
    print(f"\n[Test 3: Explicit vs Default Pricing Consistency]")
    try:
        result_explicit = calc_func(**default_test_params)
        result_default = calc_func(quantity=default_test_params['quantity'])
        
        assert result_explicit['success'] == True
        assert result_default['success'] == True
        assert abs(result_explicit['total_price'] - result_default['total_price']) < 0.01, \
            f"Prices should match: explicit=${result_explicit['total_price']:.2f}, default=${result_default['total_price']:.2f}"
        
        print(f"✅ PASS - Explicit: ${result_explicit['total_price']:.2f}, " +
              f"Default: ${result_default['total_price']:.2f} (Match!)")
        passed += 1
    except AssertionError as e:
        print(f"❌ FAIL - {e}")
    except Exception as e:
        print(f"❌ FAIL - Unexpected error: {e}")
    
    # Test 4: Quantity Affects Pricing
    print(f"\n[Test 4: Quantity Affects Pricing]")
    try:
        test_small = test_params.copy()
        test_small['quantity'] = 10
        
        test_large = test_params.copy()
        test_large['quantity'] = 100
        
        result_small = calc_func(**test_small)
        result_large = calc_func(**test_large)
        
        assert result_small['success'] == True
        assert result_large['success'] == True
        assert result_large['total_price'] > result_small['total_price'], \
            "Larger quantity should have higher total price"
        
        # But unit price should be lower (economies of scale)
        unit_small = result_small['total_price'] / test_small['quantity']
        unit_large = result_large['total_price'] / test_large['quantity']
        
        print(f"✅ PASS - Small (10): ${result_small['total_price']:.2f} (${unit_small:.2f}/unit), " +
              f"Large (100): ${result_large['total_price']:.2f} (${unit_large:.2f}/unit)")
        passed += 1
    except AssertionError as e:
        print(f"❌ FAIL - {e}")
    except Exception as e:
        print(f"❌ FAIL - Unexpected error: {e}")
    
    return passed, total

# Run all Group 4 calculator tests
results = {}

print("="*70)
print("GROUP 4 COMPREHENSIVE TEST - Signs & Displays")
print("="*70)

# Calculator 1: Election Signs
passed, total = test_calculator_comprehensive(
    "Election Signs",
    calculate_election_signs,
    {
        'quantity': 50,
        'size': '600x450',
        'material': 'Corflute',
        'sides': 'Single',
        'artworks': 1
    },
    {
        'quantity': 50,
        'size': '600x450',
        'material': 'Corflute',
        'sides': 'Single',
        'artworks': 1
    }
)
results['election_signs'] = (passed, total)

# Calculator 2: Construction Signs
passed, total = test_calculator_comprehensive(
    "Construction Signs",
    calculate_construction_signs,
    {
        'quantity': 20,
        'size': '600x450',
        'material': 'Corflute',
        'sides': 'Single',
        'artworks': 1
    },
    {
        'quantity': 20,
        'size': '600x450',
        'material': 'Corflute',
        'sides': 'Single',
        'artworks': 1
    }
)
results['construction_signs'] = (passed, total)

# Calculator 3: Bollard Signs
passed, total = test_calculator_comprehensive(
    "Bollard Signs",
    calculate_bollard_signs,
    {
        'quantity': 10,
        'size': '300x300',
        'material': 'Aluminium',
        'sides': 'Single',
        'artworks': 1
    },
    {
        'quantity': 10,
        'size': '300x300',
        'material': 'Aluminium',
        'sides': 'Single',
        'artworks': 1
    }
)
results['bollard_signs'] = (passed, total)

# Calculator 4: Corflute Insert A-Frame
passed, total = test_calculator_comprehensive(
    "Corflute Insert A-Frame",
    calculate_corflute_insert_a_frame,
    {
        'quantity': 10,
        'size': '600x450',
        'sides': 'Single',
        'artworks': 1
    },
    {
        'quantity': 10,
        'size': '600x450',
        'sides': 'Single',
        'artworks': 1
    }
)
results['corflute_insert_a_frame'] = (passed, total)

# Calculator 5: Metal Face A-Frame
passed, total = test_calculator_comprehensive(
    "Metal Face A-Frame",
    calculate_metal_face_a_frame,
    {
        'quantity': 10,
        'size': '600x450',
        'sides': 'Single',
        'artworks': 1
    },
    {
        'quantity': 10,
        'size': '600x450',
        'sides': 'Single',
        'artworks': 1
    }
)
results['metal_face_a_frame'] = (passed, total)

# Summary
print(f"\n{'='*70}")
print("GROUP 4 COMPREHENSIVE TEST SUMMARY")
print(f"{'='*70}")

total_passed = 0
total_tests = 0

for calc_name, (passed, total) in results.items():
    total_passed += passed
    total_tests += total
    percentage = (passed / total * 100) if total > 0 else 0
    status = "✅ EXCELLENT" if passed == total else "⚠️ NEEDS WORK" if passed >= total/2 else "❌ FAILED"
    print(f"  {status} - {calc_name.replace('_', ' ').title()}: {passed}/{total} ({percentage:.0f}%)")

overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
print(f"\nOverall Score: {total_passed}/{total_tests} ({overall_percentage:.1f}%)")

if total_passed == total_tests:
    print("\n🎉 GROUP 4 PERFECT! All 20 tests passed!")
    sys.exit(0)
else:
    print(f"\n⚠️ {total_tests - total_passed} test(s) failed - needs review")
    sys.exit(1)
