"""
Test SelfieFrames calculator
"""
import sys
from pathlib import Path

backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))
shopify_path = backend_path / 'shopify_calculators'
sys.path.insert(0, str(shopify_path))

from SelfieFrames_Shopify_Calculator import SelfieFramesShopifyCalculator

print("\n" + "="*80)
print("TESTING SelfieFrames Calculator")
print("="*80 + "\n")

calc = SelfieFramesShopifyCalculator()

# Test Case 1: Single small frame
test1 = {
    "quantity": 1,
    "size": "Small 600mm x 900mm",
    "artworks": 1
}

# Test Case 2: Small batch small size
test2 = {
    "quantity": 10,
    "size": "Small 600mm x 900mm",
    "artworks": 1
}

# Test Case 3: Medium batch large size
test3 = {
    "quantity": 50,
    "size": "Large 900mm x 1200mm",
    "artworks": 3
}

# Test Case 4: Large batch small size
test4 = {
    "quantity": 200,
    "size": "Small 600mm x 900mm",
    "artworks": 5
}

test_cases = [
    ("Test 1: 1× small frame (highest tier $117)", test1),
    ("Test 2: 10× small frames", test2),
    ("Test 3: 50× large frames with 3 artworks", test3),
    ("Test 4: 200× small frames (bulk pricing)", test4)
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
