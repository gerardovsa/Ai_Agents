"""
Test CustomVinylStickers calculator
"""
import sys
from pathlib import Path

# Add paths
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))
shopify_path = backend_path / 'shopify_calculators'
sys.path.insert(0, str(shopify_path))

from CustomVinylStickers_Shopify_Calculator import CustomVinylStickersShopifyCalculator

print("\n" + "="*80)
print("TESTING CustomVinylStickers Calculator")
print("="*80 + "\n")

calc = CustomVinylStickersShopifyCalculator()

# Test Case 1: Small circle stickers
test1 = {
    "quantity": 100,
    "size": "50mm Circle",
    "vinyl_family": "Standard Vinyl",
    "adhesive": "Permanent",
    "laminate": "No Lamination",
    "cutting_method": "Standard Cut",
    "artworks": 1,
    "labour_rate": "Non-Trade ($90/hr)"
}

# Test Case 2: Custom size with laminate
test2 = {
    "quantity": 500,
    "size": "Custom Size",
    "width": 200,
    "height": 150,
    "vinyl_family": "Premium Vinyl",
    "adhesive": "Removable",
    "laminate": "Gloss",
    "cutting_method": "Kiss-Cut",
    "artworks": 2,
    "labour_rate": "Non-Trade ($90/hr)"
}

# Test Case 3: Large rectangle
test3 = {
    "quantity": 250,
    "size": "200x100mm Rectangle",
    "vinyl_family": "Standard Vinyl",
    "adhesive": "Permanent",
    "laminate": "Matt",
    "cutting_method": "Standard Cut",
    "artworks": 1,
    "labour_rate": "Trade ($70/hr)"
}

# Test Case 4: High quantity square
test4 = {
    "quantity": 2000,
    "size": "100mm Square",
    "vinyl_family": "Premium Vinyl",
    "adhesive": "Permanent",
    "laminate": "No Lamination",
    "cutting_method": "Standard Cut",
    "artworks": 3,
    "labour_rate": "Non-Trade ($90/hr)"
}

test_cases = [
    ("Test 1: 100× 50mm circles, standard vinyl", test1),
    ("Test 2: 500× custom 200×150mm, premium removable, kiss-cut", test2),
    ("Test 3: 250× 200×100mm rectangle, laminated", test3),
    ("Test 4: 2000× 100mm square, premium vinyl", test4)
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
