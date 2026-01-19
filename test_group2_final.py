"""Test Group 2 calculators after fixes"""
import sys
sys.path.insert(0, 'UI/modules_external/quote-calculator/implementations')

from calculator_wrapper import (
    calculate_wire_bound_books_shopify,
    calculate_spiral_bound_books_shopify,
    calculate_perfect_bound_books_shopify,
    calculate_saddle_stitch_books_shopify,
    calculate_spiral_books_simple_shopify
)

print("\n" + "="*60)
print("GROUP 2: BOUND BOOKS CALCULATORS - FINAL TEST")
print("="*60)

tests = [
    ("Wire Bound Books", calculate_wire_bound_books_shopify, {}),
    ("Spiral Bound Books", calculate_spiral_bound_books_shopify, {}),
    ("Perfect Bound Books", calculate_perfect_bound_books_shopify, {}),
    ("Saddle Stitch Books", calculate_saddle_stitch_books_shopify, {}),
    ("Spiral Books Simple", calculate_spiral_books_simple_shopify, {})
]

passed = 0
failed = 0

for name, func, params in tests:
    print(f"\n{name}:")
    print(f"  Test 1 (defaults): ", end="")
    try:
        result = func(quantity=500, **params)
        if result.get("success"):
            price = result.get("total_price", 0)
            print(f"✅ ${price:.2f}")
            passed += 1
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            failed += 1
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        failed += 1
    
    print(f"  Test 2 (with params): ", end="")
    try:
        # Perfect Bound doesn't support artworks parameter (backend limitation)
        if "Perfect Bound" in name:
            result = func(quantity=1000, printed_pages=200)
        else:
            result = func(quantity=1000, artworks=2)
        if result.get("success"):
            price = result.get("total_price", 0)
            print(f"✅ ${price:.2f}")
            passed += 1
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            failed += 1
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        failed += 1

print("\n" + "="*60)
print(f"RESULTS: {passed}/10 tests passing ({passed*10}%)")
print("="*60)

if passed == 10:
    print("🎉 ALL GROUP 2 TESTS PASSING!")
else:
    print(f"⚠️  {failed} tests still failing")
