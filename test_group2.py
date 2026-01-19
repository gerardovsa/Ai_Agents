"""Test Group 2 calculators to assess the other AI's work"""
import sys
sys.path.insert(0, r'c:\Users\gpoli\GIT\AI_Agents_V11\AI_agents\UI\modules_external\quote-calculator\implementations')
sys.path.insert(0, r'c:\Users\gpoli\GIT\AI_Agents_V11\AI_agents\UI\modules_external\quote-calculator\backend\shopify_calculators')

from calculator_wrapper import (
    calculate_wire_bound_books_shopify,
    calculate_spiral_bound_books_shopify,
    calculate_perfect_bound_books_shopify,
    calculate_notepads_a4,
    calculate_notepads_a5
)

def test_calculator(name, func, params, legacy_params=None):
    """Test a calculator with new and legacy parameters"""
    print(f"\n{'='*70}")
    print(f"TESTING: {name}")
    print(f"{'='*70}")
    
    # Test 1: New parameters
    print(f"\n[Test 1: New Parameters]")
    try:
        result = func(**params)
        if result['success']:
            print(f"✅ SUCCESS")
            print(f"   Price: ${result['total_price']:.2f}")
            print(f"   Warnings: {len(result.get('warnings', []))}")
        else:
            print(f"❌ FAILED: {result['error']}")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Legacy parameters (if provided)
    if legacy_params:
        print(f"\n[Test 2: Legacy Parameters]")
        try:
            result = func(**legacy_params)
            if result['success']:
                print(f"✅ SUCCESS")
                print(f"   Price: ${result['total_price']:.2f}")
                warnings = result.get('warnings', [])
                print(f"   Warnings: {len(warnings)}")
                if warnings:
                    for w in warnings:
                        print(f"      - {w.get('deprecated')} → {w.get('use_instead')}")
            else:
                print(f"❌ FAILED: {result['error']}")
                return False
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

# ============================================================================
# GROUP 2 TESTS
# ============================================================================

print("\n" + "="*70)
print("GROUP 2 ASSESSMENT - Testing Calculators Fixed by Other AI")
print("="*70)

results = {}

# Calculator 1: Wire Bound Books
results['wire_bound'] = test_calculator(
    "Wire Bound Books",
    calculate_wire_bound_books_shopify,
    {
        'quantity': 500,
        'internal_pages': 100,
        'finish_size': 'A5 Portrait',
        'printed_front_cover': '300GSM Satin',
        'front_cover_print': '2pp Colour'
    },
    {
        'quantity': 500,
        'pages': 100,  # Legacy
        'size': 'A5',  # Legacy (will add Portrait)
        'cover_stock': '300GSM Satin'  # Legacy
    }
)

# Calculator 2: Spiral Bound Books
results['spiral_bound'] = test_calculator(
    "Spiral Bound Books",
    calculate_spiral_bound_books_shopify,
    {
        'quantity': 500,
        'internal_pages': 100,
        'finish_size': 'A5 Portrait',
        'printed_front_cover': '300GSM Satin',
        'front_cover_print': '2pp Colour'
    },
    {
        'quantity': 500,
        'pages': 100,  # Legacy
        'size': 'A5',  # Legacy
        'cover_stock': '300GSM Satin'  # Legacy
    }
)

# Calculator 3: Perfect Bound Books
results['perfect_bound'] = test_calculator(
    "Perfect Bound Books",
    calculate_perfect_bound_books_shopify,
    {
        'quantity': 500,
        'printed_pages': 200,
        'finish_size': 'A5 Portrait',
        'cover_stock': 'Satin 300GSM',
        'cover_print_type': '2 side colour (4pp)'
    },
    {
        'quantity': 500,
        'pages': 200,  # Legacy
        'size': 'A5',  # Legacy
        'inner_stock': 'Uncoated Bond 100GSM',  # Legacy
        'inner_print': 'Black & White'  # Legacy
    }
)

# Calculator 4: Notepads A4
results['notepads_a4'] = test_calculator(
    "Notepads A4",
    calculate_notepads_a4,
    {
        'quantity': 250,
        'print_type': 'Colour',
        'print_sides': 'Single side print',
        'paper_stock': 'Standard'
    },
    {
        'quantity': 250,
        'stock_type': 'Standard'  # Legacy
    }
)

# Calculator 5: Notepads A5
results['notepads_a5'] = test_calculator(
    "Notepads A5",
    calculate_notepads_a5,
    {
        'quantity': 250,
        'print_type': 'Colour',
        'print_sides': 'Single side print',
        'paper_stock': 'Standard'
    },
    {
        'quantity': 250,
        'stock_type': 'Standard'  # Legacy
    }
)

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("GROUP 2 ASSESSMENT SUMMARY")
print("="*70)

passed = sum(1 for v in results.values() if v)
total = len(results)

print(f"\nResults: {passed}/{total} calculators passed")
print(f"\nDetailed Results:")
for calc, passed in results.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status} - {calc}")

if passed == total:
    print(f"\n🎉 ALL {total} CALCULATORS WORKING!")
    print("Group 2 assessment: COMPLETE ✅")
else:
    print(f"\n⚠️  {total - passed} calculators need fixes")
