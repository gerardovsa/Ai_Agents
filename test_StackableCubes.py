"""
Test StackableCubes calculator
"""
import sys
from pathlib import Path

backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))
shopify_path = backend_path / 'shopify_calculators'
sys.path.insert(0, str(shopify_path))

from StackableCubes_Shopify_Calculator import StackableCubesShopifyCalculator

print("\n" + "="*80)
print("TESTING StackableCubes Calculator")
print("="*80 + "\n")

calc = StackableCubesShopifyCalculator()

# Test Case 1: Small cubes
test1 = {
    "quantity": 10,
    "material": "5mm Corflute",
    "cube_size": "Small (300x300x300mm)",
    "artworks": 1
}

# Test Case 2: Medium cubes with multiple artworks
test2 = {
    "quantity": 25,
    "material": "5mm Corflute",
    "cube_size": "Medium (400x400x400mm)",
    "artworks": 3
}

# Test Case 3: Large cubes 3mm
test3 = {
    "quantity": 50,
    "material": "3mm Corflute",
    "cube_size": "Large (500x500x500mm)",
    "artworks": 1
}

# Test Case 4: X-Large bulk order
test4 = {
    "quantity": 100,
    "material": "5mm Corflute",
    "cube_size": "X-Large (550x550x550mm)",
    "artworks": 2
}

test_cases = [
    ("Test 1: 10× small cubes (300mm)", test1),
    ("Test 2: 25× medium cubes with 3 artworks", test2),
    ("Test 3: 50× large 3mm cubes", test3),
    ("Test 4: 100× X-large cubes (bulk)", test4)
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
