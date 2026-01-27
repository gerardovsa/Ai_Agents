"""
Test SaddleStitchBooks calculator
"""
import sys
from pathlib import Path

# Add paths
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))
shopify_path = backend_path / 'shopify_calculators'
sys.path.insert(0, str(shopify_path))

from SaddleStitchBooks_Shopify_Calculator import SaddleStitchBooksShopifyCalculator

print("\n" + "="*80)
print("TESTING SaddleStitchBooks Calculator")
print("="*80 + "\n")

calc = SaddleStitchBooksShopifyCalculator()

# Test Case 1: Basic configuration
test1 = {
    "quantity": "100",
    "artworks": 1,
    "cover_option": "Hard Cover",
    "cover_stock": "Satin 250GSM",
    "cover_print_type": "2 side colour (4pp)",
    "celloglaze": "None",
    "printed_pages": "16pp",
    "finish_size": "A4 Portrait",
    "content_print_type": "Black & White",
    "content_stock_type": "Uncoated Bond 80GSM"
}

# Test Case 2: With celloglaze
test2 = {
    "quantity": "250",
    "artworks": 1,
    "cover_option": "Hard Cover",
    "cover_stock": "Satin 300GSM",
    "cover_print_type": "2 side colour (4pp)",
    "celloglaze": "Gloss outside only",
    "printed_pages": "24pp",
    "finish_size": "A5 Portrait",
    "content_print_type": "Colour",
    "content_stock_type": "Uncoated Bond 100GSM"
}

# Test Case 3: Self cover
test3 = {
    "quantity": "500",
    "artworks": 2,
    "cover_option": "Self Cover",
    "cover_stock": "Satin 200GSM",
    "cover_print_type": "1 side colour (2pp)",
    "celloglaze": "Matt outside only",
    "printed_pages": "32pp",
    "finish_size": "A5 Portrait",
    "content_print_type": "Black & White",
    "content_stock_type": "Uncoated Bond 90GSM"
}

# Test Case 4: Large quantity
test4 = {
    "quantity": "2000",
    "artworks": 3,
    "cover_option": "Hard Cover",
    "cover_stock": "Satin 350GSM",
    "cover_print_type": "2 side colour (4pp)",
    "celloglaze": "Gloss outside only",
    "printed_pages": "48pp",
    "finish_size": "A4 Landscape",
    "content_print_type": "Colour",
    "content_stock_type": "Satin 150GSM"
}

test_cases = [
    ("Test 1: Basic 100 books, A4, 16pp, B&W content", test1),
    ("Test 2: 250 books with celloglaze, A5, 24pp, Colour", test2),
    ("Test 3: 500 books, Self Cover, A5, 32pp", test3),
    ("Test 4: 2000 books, large format, 48pp", test4)
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
        print(f"   Traceback: {traceback.format_exc()}")
        print()
        failed += 1

print("="*80)
print(f"SUMMARY: {passed}/{len(test_cases)} tests passed")
if failed == 0:
    print("🎉 ALL TESTS PASSED - Calculator working correctly")
else:
    print(f"⚠️  {failed} tests failed")
print("="*80)
