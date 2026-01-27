"""
Test ConstructionSigns calculator
"""
import sys
from pathlib import Path

backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))
shopify_path = backend_path / 'shopify_calculators'
sys.path.insert(0, str(shopify_path))

from ConstructionSigns_Shopify_Calculator import ConstructionSignsShopifyCalculator

print("\n" + "="*80)
print("TESTING ConstructionSigns Calculator")
print("="*80 + "\n")

calc = ConstructionSignsShopifyCalculator()

# Test Case 1: Standard sign
test1 = {
    "quantity": 10,
    "eyelets": "4 Eyelets",
    "width_mm": 900,
    "thickness": "5mm Corflute",
    "size": "Custom Size",
    "length_mm": 600,
    "sides": "Single Sided",
    "cutting": "Square Cut",
    "artworks": 1
}

# Test Case 2: Large double-sided
test2 = {
    "quantity": 50,
    "eyelets": "No Eyelets",
    "width_mm": 1200,
    "thickness": "5mm Corflute",
    "size": "Custom Size",
    "length_mm": 2400,
    "sides": "Double Sided",
    "cutting": "Contour Cut",
    "artworks": 2
}

# Test Case 3: 3mm material
test3 = {
    "quantity": 100,
    "eyelets": "4 Eyelets",
    "width_mm": 600,
    "thickness": "3mm Corflute",
    "size": "Custom Size",
    "length_mm": 900,
    "sides": "Single Sided",
    "cutting": "Square Cut",
    "artworks": 1
}

# Test Case 4: Small quantity
test4 = {
    "quantity": 5,
    "eyelets": "4 Eyelets",
    "width_mm": 450,
    "thickness": "5mm Corflute",
    "size": "Custom Size",
    "length_mm": 600,
    "sides": "Single Sided",
    "cutting": "Square Cut",
    "artworks": 1
}

test_cases = [
    ("Test 1: 10× 900×600mm, 5mm, single-sided", test1),
    ("Test 2: 50× 1200×2400mm (large), double-sided", test2),
    ("Test 3: 100× 600×900mm, 3mm", test3),
    ("Test 4: 5× small 450×600mm (minimum order test)", test4)
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
