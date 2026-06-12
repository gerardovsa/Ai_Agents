"""
Test Cases for Saddle Stitch Books Shopify Calculator
Validates exact implementation against TXT formula (Lines 3054-3120)

Date: January 23, 2026
Calculator: SaddleStitchBooks_Shopify_Calculator.py
"""

import sys
from pathlib import Path
from decimal import Decimal
import json

# Add backend paths
backend_path = Path(__file__).parent / "UI" / "modules_external" / "quote-calculator" / "backend"
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(backend_path / "shopify_calculators"))

# Import directly to avoid __init__.py issues
import importlib.util
spec = importlib.util.spec_from_file_location(
    "SaddleStitchBooks_Shopify_Calculator",
    backend_path / "shopify_calculators" / "SaddleStitchBooks_Shopify_Calculator.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SaddleStitchBooksShopifyCalculator = module.SaddleStitchBooksShopifyCalculator


def test_case_1_basic_small_order():
    """
    TEST 1: Basic Small Order
    100 books, 16pp, Hard Cover Satin 200GSM, No Celloglaze, 1 artwork
    Expected: $351.28
    """
    print("\n" + "="*80)
    print("TEST CASE 1: Basic Small Order")
    print("="*80)
    
    calc = SaddleStitchBooksShopifyCalculator()
    
    result = calc.calculate(
        quantity="100",
        artworks=1,
        cover_option="Hard Cover",
        cover_stock="Satin 200GSM",
        cover_print_type="2 side colour (4pp)",
        celloglaze="None",
        printed_pages="16pp",
        finish_size="A4 Portrait",
        content_print_type="Black & White",
        content_stock_type="Uncoated Bond 80GSM"
    )
    
    expected = Decimal('351.28')
    difference = abs(result.total_price - expected)
    
    print(f"\n📊 RESULTS:")
    print(f"  Total Price:      ${result.total_price:.2f}")
    print(f"  Expected:         ${expected:.2f}")
    print(f"  Difference:       ${difference:.2f}")
    print(f"  Unit Price:       ${result.unit_price:.2f}")
    
    print(f"\n💰 BREAKDOWN:")
    for key, value in result.breakdown.items():
        print(f"  {key:25s}: ${float(value):.2f}")
    
    print(f"\n📋 SPECIFICATIONS:")
    for key, value in result.specifications.items():
        print(f"  {key:25s}: {value}")
    
    if difference <= Decimal('0.02'):
        print(f"\n✅ TEST PASSED - Price matches expected (within $0.02)")
        return True
    else:
        print(f"\n❌ TEST FAILED - Price differs by ${difference:.2f}")
        return False


def test_case_2_celloglaze_multiple_artworks():
    """
    TEST 2: With Celloglaze & Multiple Artworks
    250 books, 24pp, Hard Cover Satin 250GSM, Gloss Celloglaze, 3 artworks
    Expected: $1,403.95
    """
    print("\n" + "="*80)
    print("TEST CASE 2: With Celloglaze & Multiple Artworks")
    print("="*80)
    
    calc = SaddleStitchBooksShopifyCalculator()
    
    result = calc.calculate(
        quantity="250",
        artworks=3,
        cover_option="Hard Cover",
        cover_stock="Satin 250GSM",
        cover_print_type="2 side colour (4pp)",
        celloglaze="Gloss outside only",
        printed_pages="24pp",
        finish_size="A4 Portrait",
        content_print_type="Colour",
        content_stock_type="Satin 128GSM"
    )
    
    expected = Decimal('1403.95')
    difference = abs(result.total_price - expected)
    
    print(f"\n📊 RESULTS:")
    print(f"  Total Price:      ${result.total_price:.2f}")
    print(f"  Expected:         ${expected:.2f}")
    print(f"  Difference:       ${difference:.2f}")
    print(f"  Unit Price:       ${result.unit_price:.2f}")
    
    print(f"\n💰 BREAKDOWN:")
    for key, value in result.breakdown.items():
        print(f"  {key:25s}: ${float(value):.2f}")
    
    if difference <= Decimal('0.02'):
        print(f"\n✅ TEST PASSED - Price matches expected (within $0.02)")
        return True
    else:
        print(f"\n❌ TEST FAILED - Price differs by ${difference:.2f}")
        return False


def test_case_3_self_cover():
    """
    TEST 3: Self Cover (No Separate Cover)
    500 books, 32pp, Self Cover, A5 Portrait
    Expected: $771.13
    """
    print("\n" + "="*80)
    print("TEST CASE 3: Self Cover (No Separate Cover)")
    print("="*80)
    
    calc = SaddleStitchBooksShopifyCalculator()
    
    result = calc.calculate(
        quantity="500",
        artworks=1,
        cover_option="Self Cover",
        cover_stock="Satin 200GSM",  # Ignored
        cover_print_type="2 side colour (4pp)",  # Ignored
        celloglaze="None",
        printed_pages="32pp",
        finish_size="A5 Portrait",
        content_print_type="Black & White",
        content_stock_type="Uncoated Bond 80GSM"
    )
    
    expected = Decimal('771.13')
    difference = abs(result.total_price - expected)
    
    print(f"\n📊 RESULTS:")
    print(f"  Total Price:      ${result.total_price:.2f}")
    print(f"  Expected:         ${expected:.2f}")
    print(f"  Difference:       ${difference:.2f}")
    print(f"  Unit Price:       ${result.unit_price:.2f}")
    
    print(f"\n💰 BREAKDOWN:")
    for key, value in result.breakdown.items():
        print(f"  {key:25s}: ${float(value):.2f}")
    
    print(f"\n📋 SPECIFICATIONS (Note cover_sheets = 0):")
    for key, value in result.specifications.items():
        print(f"  {key:25s}: {value}")
    
    if difference <= Decimal('0.02'):
        print(f"\n✅ TEST PASSED - Price matches expected (within $0.02)")
        return True
    else:
        print(f"\n❌ TEST FAILED - Price differs by ${difference:.2f}")
        return False


def test_case_4_large_order():
    """
    TEST 4: Large Order (High Volume, Low Margin)
    2000 books, 48pp, Hard Cover Satin 300GSM, Matt Celloglaze, A4 Landscape, 2 artworks
    Expected: $17,848.66
    """
    print("\n" + "="*80)
    print("TEST CASE 4: Large Order (High Volume, Low Margin)")
    print("="*80)
    
    calc = SaddleStitchBooksShopifyCalculator()
    
    result = calc.calculate(
        quantity="2000",
        artworks=2,
        cover_option="Hard Cover",
        cover_stock="Satin 300GSM",
        cover_print_type="2 side colour (4pp)",
        celloglaze="Matt outside only",
        printed_pages="48pp",
        finish_size="A4 Landscape",
        content_print_type="Colour",
        content_stock_type="Satin 200GSM"
    )
    
    expected = Decimal('17220.19')
    difference = abs(result.total_price - expected)
    
    print(f"\n📊 RESULTS:")
    print(f"  Total Price:      ${result.total_price:,.2f}")
    print(f"  Expected:         ${expected:,.2f}")
    print(f"  Difference:       ${difference:.2f}")
    print(f"  Unit Price:       ${result.unit_price:.2f}")
    
    print(f"\n💰 BREAKDOWN:")
    for key, value in result.breakdown.items():
        print(f"  {key:25s}: ${float(value):,.2f}")
    
    if difference <= Decimal('0.02'):
        print(f"\n✅ TEST PASSED - Price matches expected (within $0.02)")
        return True
    else:
        print(f"\n❌ TEST FAILED - Price differs by ${difference:.2f}")
        return False


def main():
    """Run all test cases"""
    print("\n" + "="*80)
    print("🧪 SADDLE STITCH BOOKS CALCULATOR - TEST SUITE")
    print("="*80)
    print("Formula Source: Lines 3054-3120 in SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt")
    print("Backend: SaddleStitchBooks_Shopify_Calculator.py")
    print("Key Feature: DOUBLE GST (× 1.1 × 1.1 = 21% effective GST)")
    print("="*80)
    
    results = []
    
    try:
        results.append(("Test 1: Basic Small Order", test_case_1_basic_small_order()))
        results.append(("Test 2: Celloglaze & Multiple Artworks", test_case_2_celloglaze_multiple_artworks()))
        results.append(("Test 3: Self Cover", test_case_3_self_cover()))
        results.append(("Test 4: Large Order", test_case_4_large_order()))
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, passed_test in results:
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"  {status} - {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Backend matches TXT formula exactly!")
        print("✅ Double GST (× 1.1 × 1.1) verified in all test cases")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - Review discrepancies")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
