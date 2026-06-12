"""
Test Suite for Spiral Bound Books Calculator - January 26, 2026
Tests both original 5 tests and diagnostic tests validated against website
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add backend path
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(backend_path / 'shopify_calculators'))

from SpiralBoundBooks_Shopify_Calculator_JAN_26 import SpiralBoundBooksShopifyCalculator

def test_all():
    """Run all tests for Spiral Bound Books calculator"""
    
    calc = SpiralBoundBooksShopifyCalculator()
    
    print("=" * 100)
    print("SPIRAL BOUND BOOKS - COMPLETE TEST SUITE (January 26, 2026)")
    print("=" * 100)
    print()
    print("✅ Calculator: SpiralBoundBooks_Shopify_Calculator_JAN_26.py")
    print("✅ Formula: Exact JavaScript implementation with $98.63 surcharge ($44 + $54.63)")
    print()
    print("=" * 100)
    print()
    
    all_results = []
    
    # ========================================================================
    # DIAGNOSTIC TESTS (Website Validated)
    # ========================================================================
    
    print("PART 1: DIAGNOSTIC TESTS (Website Validated)")
    print("=" * 100)
    print()
    
    # Diagnostic Test 1 - Full Configuration
    print("DIAGNOSTIC TEST 1: Full Configuration (Original Reference)")
    print("-" * 100)
    diag1 = calc.calculate(
        quantity=100,
        artworks=1,
        finish_size="A5 Landscape",
        outer_front_cover="Clear PVC",
        printed_front_cover="300GSM Satin",
        cover_print_type="1pp Colour",
        celloglaze="None",
        outer_back_cover="350GSM Satin Blank",
        printed_back_cover="None",
        back_cover_print_type="1pp Colour",
        back_celloglaze="None",
        content_pages=50,
        content_paper_stock="Uncoated Bond 100GSM",
        content_print_type="Black & White"
    )
    expected1 = Decimal('687.65')
    diff1 = diag1.total_price - expected1
    pct1 = (diff1 / expected1) * 100
    match1 = "✅ MATCH" if abs(diff1) < Decimal('1.00') else "❌ OFF"
    print(f"Backend: ${diag1.total_price:.2f}")
    print(f"Website: ${expected1:.2f}")
    print(f"Difference: ${diff1:.2f} ({pct1:.2f}%) {match1}")
    print()
    all_results.append(("Diag 1 (Full Config)", diag1.total_price, expected1, diff1, pct1, match1))
    
    # Diagnostic Test 2 - No Outer Covers
    print("DIAGNOSTIC TEST 2: No Outer Covers - Only Printed Front")
    print("-" * 100)
    diag2 = calc.calculate(
        quantity=100,
        artworks=1,
        finish_size="A5 Landscape",
        outer_front_cover="Not Required",
        printed_front_cover="300GSM Satin",
        cover_print_type="1pp Colour",
        celloglaze="None",
        outer_back_cover="None",
        printed_back_cover="None",
        back_cover_print_type="1pp Colour",
        back_celloglaze="None",
        content_pages=50,
        content_paper_stock="Uncoated Bond 100GSM",
        content_print_type="Black & White"
    )
    expected2 = Decimal('635.21')
    diff2 = diag2.total_price - expected2
    pct2 = (diff2 / expected2) * 100
    match2 = "✅ MATCH" if abs(diff2) < Decimal('1.00') else "❌ OFF"
    print(f"Backend: ${diag2.total_price:.2f}")
    print(f"Website: ${expected2:.2f}")
    print(f"Difference: ${diff2:.2f} ({pct2:.2f}%) {match2}")
    print()
    all_results.append(("Diag 2 (No Outer)", diag2.total_price, expected2, diff2, pct2, match2))
    
    # Diagnostic Test 3 - No Printed Covers
    print("DIAGNOSTIC TEST 3: No Printed Covers - Only Outer PVC")
    print("-" * 100)
    diag3 = calc.calculate(
        quantity=100,
        artworks=1,
        finish_size="A5 Landscape",
        outer_front_cover="Clear PVC",
        printed_front_cover="None",
        cover_print_type="1pp Colour",
        celloglaze="None",
        outer_back_cover="350GSM Satin Blank",
        printed_back_cover="None",
        back_cover_print_type="1pp Colour",
        back_celloglaze="None",
        content_pages=50,
        content_paper_stock="Uncoated Bond 100GSM",
        content_print_type="Black & White"
    )
    expected3 = Decimal('674.99')
    diff3 = diag3.total_price - expected3
    pct3 = (diff3 / expected3) * 100
    match3 = "✅ MATCH" if abs(diff3) < Decimal('1.00') else "❌ OFF"
    print(f"Backend: ${diag3.total_price:.2f}")
    print(f"Website: ${expected3:.2f}")
    print(f"Difference: ${diff3:.2f} ({pct3:.2f}%) {match3}")
    print()
    all_results.append(("Diag 3 (No Printed)", diag3.total_price, expected3, diff3, pct3, match3))
    
    # Diagnostic Test 4 - No Covers
    print("DIAGNOSTIC TEST 4: No Covers - Content Only")
    print("-" * 100)
    diag4 = calc.calculate(
        quantity=100,
        artworks=1,
        finish_size="A5 Landscape",
        outer_front_cover="Not Required",
        printed_front_cover="None",
        cover_print_type="1pp Colour",
        celloglaze="None",
        outer_back_cover="None",
        printed_back_cover="None",
        back_cover_print_type="1pp Colour",
        back_celloglaze="None",
        content_pages=50,
        content_paper_stock="Uncoated Bond 100GSM",
        content_print_type="Black & White"
    )
    expected4 = Decimal('622.55')
    diff4 = diag4.total_price - expected4
    pct4 = (diff4 / expected4) * 100
    match4 = "✅ MATCH" if abs(diff4) < Decimal('1.00') else "❌ OFF"
    print(f"Backend: ${diag4.total_price:.2f}")
    print(f"Website: ${expected4:.2f}")
    print(f"Difference: ${diff4:.2f} ({pct4:.2f}%) {match4}")
    print()
    all_results.append(("Diag 4 (No Covers)", diag4.total_price, expected4, diff4, pct4, match4))
    
    # Diagnostic Test 6 - A4 Portrait (wire NOT halved)
    print("DIAGNOSTIC TEST 6: A4 Portrait (Wire NOT Halved)")
    print("-" * 100)
    diag6 = calc.calculate(
        quantity=100,
        artworks=1,
        finish_size="A4 Portrait",
        outer_front_cover="Clear PVC",
        printed_front_cover="300GSM Satin",
        cover_print_type="1pp Colour",
        celloglaze="None",
        outer_back_cover="350GSM Satin Blank",
        printed_back_cover="None",
        back_cover_print_type="1pp Colour",
        back_celloglaze="None",
        content_pages=50,
        content_paper_stock="Uncoated Bond 100GSM",
        content_print_type="Black & White"
    )
    expected6 = Decimal('851.16')
    diff6 = diag6.total_price - expected6
    pct6 = (diff6 / expected6) * 100
    match6 = "✅ MATCH" if abs(diff6) < Decimal('1.00') else "❌ OFF"
    print(f"Backend: ${diag6.total_price:.2f}")
    print(f"Website: ${expected6:.2f}")
    print(f"Difference: ${diff6:.2f} ({pct6:.2f}%) {match6}")
    print()
    all_results.append(("Diag 6 (A4 Portrait)", diag6.total_price, expected6, diff6, pct6, match6))
    
    # Diagnostic Test 7 - A4 Minimal
    print("DIAGNOSTIC TEST 7: A4 Portrait Minimal")
    print("-" * 100)
    diag7 = calc.calculate(
        quantity=100,
        artworks=1,
        finish_size="A4 Portrait",
        outer_front_cover="Not Required",
        printed_front_cover="300GSM Satin",
        cover_print_type="1pp Colour",
        celloglaze="None",
        outer_back_cover="None",
        printed_back_cover="None",
        back_cover_print_type="1pp Colour",
        back_celloglaze="None",
        content_pages=50,
        content_paper_stock="Uncoated Bond 100GSM",
        content_print_type="Black & White"
    )
    expected7 = Decimal('798.72')
    diff7 = diag7.total_price - expected7
    pct7 = (diff7 / expected7) * 100
    match7 = "✅ MATCH" if abs(diff7) < Decimal('1.00') else "❌ OFF"
    print(f"Backend: ${diag7.total_price:.2f}")
    print(f"Website: ${expected7:.2f}")
    print(f"Difference: ${diff7:.2f} ({pct7:.2f}%) {match7}")
    print()
    all_results.append(("Diag 7 (A4 Minimal)", diag7.total_price, expected7, diff7, pct7, match7))
    
    # ========================================================================
    # ORIGINAL 5 TESTS (Need website validation)
    # ========================================================================
    
    print()
    print("=" * 100)
    print("PART 2: ORIGINAL 5 TESTS (Need Website Validation)")
    print("=" * 100)
    print()
    
    # Test 1 - Basic Spiral Bound
    print("TEST 1: Basic Spiral Bound - Small Quantity")
    print("-" * 100)
    test1 = calc.calculate(
        quantity=100,
        artworks=1,
        outer_front_cover="Not Required",
        printed_front_cover="300GSM Satin",
        cover_print_type="1pp Colour",
        celloglaze="None",
        outer_back_cover="None",
        printed_back_cover="None",
        back_cover_print_type="1pp Colour",
        back_celloglaze="None",
        content_pages=40,
        content_paper_stock="Uncoated Bond 80GSM",
        content_print_type="Black & White",
        finish_size="A5 Portrait"
    )
    print(f"Backend: ${test1.total_price:.2f}")
    print(f"Website: NEED PRICE")
    print()
    all_results.append(("Test 1 (Basic A5)", test1.total_price, None, None, None, "⏳ PENDING"))
    
    # Test 2 - Medium Quantity Color
    print("TEST 2: Medium Quantity with Color Content")
    print("-" * 100)
    test2 = calc.calculate(
        quantity=500,
        artworks=1,
        outer_front_cover="Not Required",
        printed_front_cover="350GSM Satin",
        cover_print_type="2pp Colour",
        celloglaze="None",
        outer_back_cover="350GSM Satin Blank",
        printed_back_cover="None",
        back_cover_print_type="1pp Colour",
        back_celloglaze="None",
        content_pages=100,
        content_paper_stock="Satin 128GSM",
        content_print_type="Full colour",
        finish_size="A4 Portrait"
    )
    print(f"Backend: ${test2.total_price:.2f}")
    print(f"Website: NEED PRICE")
    print()
    all_results.append(("Test 2 (500 A4 Color)", test2.total_price, None, None, None, "⏳ PENDING"))
    
    # Test 3 - Large Quantity Thick Book
    print("TEST 3: Large Quantity Thick Book")
    print("-" * 100)
    test3 = calc.calculate(
        quantity=1000,
        artworks=2,
        outer_front_cover="Not Required",
        printed_front_cover="350GSM Satin",
        cover_print_type="1pp Colour",
        celloglaze="None",
        outer_back_cover="Black Leather grain",
        printed_back_cover="None",
        back_cover_print_type="1pp Colour",
        back_celloglaze="None",
        content_pages=200,
        content_paper_stock="Uncoated Bond 80GSM",
        content_print_type="Black & White",
        finish_size="A4 Portrait"
    )
    print(f"Backend: ${test3.total_price:.2f}")
    print(f"Website: NEED PRICE")
    print()
    all_results.append(("Test 3 (1000 A4 Thick)", test3.total_price, None, None, None, "⏳ PENDING"))
    
    # Test 4 - Small Format (A6)
    print("TEST 4: Small Format (A6) - Wire Price Halved")
    print("-" * 100)
    test4 = calc.calculate(
        quantity=250,
        artworks=1,
        outer_front_cover="Not Required",
        printed_front_cover="250GSM Satin",
        cover_print_type="1pp Colour",
        celloglaze="None",
        outer_back_cover="None",
        printed_back_cover="None",
        back_cover_print_type="1pp Colour",
        back_celloglaze="None",
        content_pages=50,
        content_paper_stock="Uncoated Bond 90GSM",
        content_print_type="Black & White",
        finish_size="A6 Portrait"
    )
    print(f"Backend: ${test4.total_price:.2f}")
    print(f"Website: NEED PRICE")
    print()
    all_results.append(("Test 4 (250 A6)", test4.total_price, None, None, None, "⏳ PENDING"))
    
    # Test 5 - Premium with Celloglaze
    print("TEST 5: Premium Covers with Celloglaze")
    print("-" * 100)
    test5 = calc.calculate(
        quantity=100,
        artworks=1,
        outer_front_cover="Clear PVC",
        printed_front_cover="350GSM Satin",
        cover_print_type="2pp Colour",
        celloglaze="2 Sided Matt",
        outer_back_cover="Clear PVC",
        printed_back_cover="350GSM Satin",
        back_cover_print_type="1pp Colour",
        back_celloglaze="1 Side Gloss",
        content_pages=60,
        content_paper_stock="Satin 150GSM",
        content_print_type="Full colour",
        finish_size="A4 Portrait"
    )
    print(f"Backend: ${test5.total_price:.2f}")
    print(f"Website: NEED PRICE")
    print()
    all_results.append(("Test 5 (Premium Cello)", test5.total_price, None, None, None, "⏳ PENDING"))
    
    # ========================================================================
    # SUMMARY TABLE
    # ========================================================================
    
    print()
    print("=" * 100)
    print("SUMMARY - ALL TESTS")
    print("=" * 100)
    print()
    print(f"{'Test':<30} {'Backend':<15} {'Website':<15} {'Diff $':<12} {'Diff %':<10} {'Status':<12}")
    print("-" * 100)
    
    matches = 0
    total_validated = 0
    
    for name, backend, website, diff, pct, status in all_results:
        if website is not None:
            total_validated += 1
            print(f"{name:<30} ${backend:>12.2f}  ${website:>12.2f}  ${diff:>9.2f}  {pct:>7.2f}%  {status}")
            if "MATCH" in status:
                matches += 1
        else:
            print(f"{name:<30} ${backend:>12.2f}  {'NEED PRICE':<15} {'-':<12} {'-':<10} {status}")
    
    print()
    print("=" * 100)
    print("RESULTS SUMMARY")
    print("=" * 100)
    print()
    print(f"✅ Validated Tests: {matches}/{total_validated} match within $1.00")
    print(f"⏳ Pending Tests: {len(all_results) - total_validated} need website validation")
    print()
    
    if matches == total_validated and total_validated > 0:
        print("🎉 ALL VALIDATED TESTS PASS!")
        print()
        print("Next Steps:")
        print("1. Test remaining 5 configurations on website")
        print("2. Update test file with expected prices")
        print("3. Run final validation")
    else:
        print("⚠️  Some tests need adjustment")
        print()
        print("Review differences and verify:")
        print("- Field prices match JSON")
        print("- Formula matches JavaScript exactly")
        print("- Wire pricing tiers correct")
        print("- Profit margin tiers correct")
    
    print()
    print("=" * 100)


if __name__ == "__main__":
    test_all()
