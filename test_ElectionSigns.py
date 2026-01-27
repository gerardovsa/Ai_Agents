"""
Test ElectionSigns calculator
"""
import sys
from pathlib import Path

backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))
shopify_path = backend_path / 'shopify_calculators'
sys.path.insert(0, str(shopify_path))

from ElectionSigns_Shopify_Calculator import ElectionSignsShopifyCalculator

print("\n" + "="*80)
print("TESTING ElectionSigns Calculator")
print("="*80 + "\n")

calc = ElectionSignsShopifyCalculator()

# Test Case 1: Small batch single-sided
test1 = {
    "quantity": 10,
    "eyelets": "4 Eyelets",
    "width_mm": 600,
    "thickness": "5mm Corflute",
    "size": "Custom Size",
    "length_mm": 900,
    "sides": "Single Sided",
    "artworks": 1
}

# Test Case 2: Medium batch double-sided
test2 = {
    "quantity": 50,
    "eyelets": "No Eyelets",
    "width_mm": 900,
    "thickness": "5mm Corflute",
    "size": "Custom Size",
    "length_mm": 600,
    "sides": "Double Sided",
    "artworks": 2
}

# Test Case 3: Large batch 3mm
test3 = {
    "quantity": 200,
    "eyelets": "4 Eyelets",
    "width_mm": 450,
    "thickness": "3mm Corflute",
    "size": "Custom Size",
    "length_mm": 600,
    "sides": "Single Sided",
    "artworks": 1
}

# Test Case 4: Small quantity (minimum order test)
test4 = {
    "quantity": 5,
    "eyelets": "4 Eyelets",
    "width_mm": 300,
    "thickness": "5mm Corflute",
    "size": "Custom Size",
    "length_mm": 450,
    "sides": "Single Sided",
    "artworks": 1
}

test_cases = [
    ("Test 1: 10× 600×900mm single-sided", test1),
    ("Test 2: 50× 900×600mm double-sided", test2),
    ("Test 3: 200× 450×600mm 3mm", test3),
    ("Test 4: 5× small 300×450mm (minimum order)", test4)
]

passed = 0
failed = 0

for name, test_case in test_cases:
    try:
        result = calc.calculate(**test_case)
        print(f"✅ {name}")
        print(f"   Total: ${result.total_price:.2f}")
        print(f"   Unit: ${result.unit_price:.2f}")
        print()
        passed += 1
    except Exception as e:
        import traceback
        print(f"❌ {name}")
        print(f"   ERROR: {e}")
        print(f"   Details: {traceback.format_exc()[:500]}")
        print()
        failed += 1

print("="*80)
print(f"SUMMARY: {passed}/{len(test_cases)} tests passed")
if failed == 0:
    print("🎉 ALL TESTS PASSED - Calculator working correctly")
else:
    print(f"⚠️  {failed} tests failed")
print("="*80)
