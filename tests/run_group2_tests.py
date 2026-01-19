"""Run all Group 2 Calculator Tests"""
import sys
import os

# Add implementation directory to path
impl_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                        'UI', 'modules_external', 'quote-calculator', 'implementations')
sys.path.insert(0, impl_dir)

from calculator_wrapper import (
    calculate_wire_bound_books_shopify,
    calculate_spiral_bound_books_shopify,
    calculate_perfect_bound_books_shopify,
    calculate_saddle_stitch_books_shopify,
    calculate_spiral_books_simple_shopify
)

print("=" * 80)
print("GROUP 2 CALCULATOR ALIGNMENT TESTS")
print("=" * 80)

# Test 1: Wire Bound Books
print("\n🧪 TEST 1: Wire Bound Books")
try:
    result = calculate_wire_bound_books_shopify(
        quantity=100,
        internal_pages=100,
        finish_size="A5 Portrait"
    )
    if result["success"]:
        print(f"✅ PASS - Wire Bound Books: ${result['total_price']:.2f}")
    else:
        print(f"❌ FAIL - Wire Bound Books: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"❌ EXCEPTION - Wire Bound Books: {e}")

# Test 2: Spiral Bound Books
print("\n🧪 TEST 2: Spiral Bound Books")
try:
    result = calculate_spiral_bound_books_shopify(
        quantity=100,
        internal_pages=100,
        finish_size="A5 Portrait"
    )
    if result["success"]:
        print(f"✅ PASS - Spiral Bound Books: ${result['total_price']:.2f}")
    else:
        print(f"❌ FAIL - Spiral Bound Books: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"❌ EXCEPTION - Spiral Bound Books: {e}")

# Test 3: Perfect Bound Books
print("\n🧪 TEST 3: Perfect Bound Books")
try:
    result = calculate_perfect_bound_books_shopify(
        quantity=100,
        printed_pages=200,
        finish_size="A5 Portrait"
    )
    if result["success"]:
        print(f"✅ PASS - Perfect Bound Books: ${result['total_price']:.2f}")
    else:
        print(f"❌ FAIL - Perfect Bound Books: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"❌ EXCEPTION - Perfect Bound Books: {e}")

# Test 4: Saddle Stitch Books
print("\n🧪 TEST 4: Saddle Stitch Books")
try:
    result = calculate_saddle_stitch_books_shopify(
        quantity=100,
        printed_pages="16pp",
        finish_size="A4 Portrait"
    )
    if result["success"]:
        print(f"✅ PASS - Saddle Stitch Books: ${result['total_price']:.2f}")
    else:
        print(f"❌ FAIL - Saddle Stitch Books: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"❌ EXCEPTION - Saddle Stitch Books: {e}")

# Test 5: Spiral Books Simple (Alias)
print("\n🧪 TEST 5: Spiral Books Simple (Alias)")
try:
    result = calculate_spiral_books_simple_shopify(
        quantity=100,
        internal_pages=100,
        finish_size="A5 Portrait"
    )
    if result["success"]:
        print(f"✅ PASS - Spiral Books Simple: ${result['total_price']:.2f}")
    else:
        print(f"❌ FAIL - Spiral Books Simple: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"❌ EXCEPTION - Spiral Books Simple: {e}")

# Test 6: Legacy Parameter Support
print("\n🧪 TEST 6: Legacy Parameters (Wire Bound)")
try:
    result = calculate_wire_bound_books_shopify(
        quantity=100,
        pages=100,  # DEPRECATED
        size="A5"   # DEPRECATED
    )
    if result["success"]:
        warnings_count = len(result.get("warnings", []))
        print(f"✅ PASS - Legacy parameters work with {warnings_count} warnings")
    else:
        print(f"❌ FAIL - Legacy parameters: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"❌ EXCEPTION - Legacy parameters: {e}")

print("\n" + "=" * 80)
print("✅ ALL GROUP 2 TESTS COMPLETE!")
print("=" * 80)
