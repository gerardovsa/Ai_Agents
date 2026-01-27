"""
Wire Bound Books Calculator - Test Suite
=========================================

Tests for rewritten backend (Jan 26, 2026)
Validates against website prices (NON-TRADE version)
"""

import sys
from pathlib import Path

# Add backend path
backend_path = Path(__file__).parent.parent / 'backend' / 'shopify_calculators'
sys.path.insert(0, str(backend_path))

from WireBound_Shopify_Calculator import WireBoundShopifyCalculator


def test_wire_bound_books():
    """Test Wire Bound Books calculator against website prices"""
    
    calc = WireBoundShopifyCalculator()
    
    tests = [
        {
            "name": "Test 1: A4 Portrait Basic - 100 books, 50 pages",
            "website_price": 781.24,
            "params": {
                "quantity": 100,
                "artworks": 1,
                "internal_pages": 50,
                "finish_size": "A4 Portrait",
                "printed_front_cover": "300GSM Satin",
                "front_cover_print": "2pp Colour",
                "front_celloglaze": "None",
                "outer_front_cover": "Not Required",
                "printed_back_cover": "300GSM Satin",
                "back_cover_print": "2pp Colour",
                "back_celloglaze": "None",
                "outer_back_cover": "None",
                "internal_stock": "Uncoated Bond 100GSM",
                "internal_print": "Black & White"
            }
        },
        {
            "name": "Test 2: A5 Landscape with PVC - 250 books, 80 pages (artworks=1)",
            "website_price": 2225.96,
            "params": {
                "quantity": 250,
                "artworks": 1,
                "internal_pages": 80,
                "finish_size": "A5 Landscape",
                "printed_front_cover": "350GSM Satin",
                "front_cover_print": "2pp Colour",
                "front_celloglaze": "2 Sided Matt",
                "outer_front_cover": "Not Required",  # Website shows "Not Required"
                "printed_back_cover": "350GSM Satin",
                "back_cover_print": "2pp Colour",
                "back_celloglaze": "2 Side Matt",
                "outer_back_cover": "Clear PVC",  # Website shows "Clear PVC"
                "internal_stock": "Satin 128GSM",
                "internal_print": "Full colour"
            }
        },
        {
            "name": "Test 3: DL Portrait Small - 50 books, 20 pages",
            "website_price": 375.70,
            "params": {
                "quantity": 50,
                "artworks": 1,
                "internal_pages": 20,
                "finish_size": "DL Portrait",
                "printed_front_cover": "250GSM Satin",
                "front_cover_print": "1pp Colour",
                "front_celloglaze": "1 Side Gloss",
                "outer_front_cover": "Not Required",
                "printed_back_cover": "250GSM Satin",
                "back_cover_print": "1pp Colour",
                "back_celloglaze": "None",
                "outer_back_cover": "None",
                "internal_stock": "Uncoated Bond 80GSM",
                "internal_print": "Black & White"
            }
        },
        {
            "name": "Test 4: A6 Landscape with Leather - 500 books, 120 pages",
            "website_price": 3406.66,
            "params": {
                "quantity": 500,
                "artworks": 3,
                "internal_pages": 120,
                "finish_size": "A6 Landscape",
                "printed_front_cover": "300GSM Satin",
                "front_cover_print": "2pp Colour",
                "front_celloglaze": "None",
                "outer_front_cover": "Not Required",
                "printed_back_cover": "300GSM Satin",
                "back_cover_print": "2pp Colour",
                "back_celloglaze": "None",
                "outer_back_cover": "Black Leather",
                "internal_stock": "Satin 150GSM",
                "internal_print": "Full Colour"
            }
        },
        {
            "name": "Test 5: A4 Landscape B&W Large - 1000 books, 200 pages",
            "website_price": 10513.47,
            "params": {
                "quantity": 1000,
                "artworks": 1,
                "internal_pages": 200,
                "finish_size": "A4 Landscape",
                "printed_front_cover": "300GSM Satin",
                "front_cover_print": "1pp Black & White",
                "front_celloglaze": "None",
                "outer_front_cover": "Not Required",
                "printed_back_cover": "300GSM Satin",
                "back_cover_print": "1pp Black & White",
                "back_celloglaze": "None",
                "outer_back_cover": "None",
                "internal_stock": "Uncoated Bond 90GSM",
                "internal_print": "Black & White"
            }
        }
    ]
    
    print("=" * 80)
    print("WIRE BOUND BOOKS - TEST SUITE (Rewritten Jan 26, 2026)")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"\n{test['name']}")
        print("-" * 80)
        
        try:
            result = calc.calculate(**test['params'])
            
            backend_price = float(result.total_price)
            unit_price = float(result.unit_price)
            
            print(f"Backend Total: ${backend_price:,.2f}")
            print(f"Unit Price: ${unit_price:.2f}")
            
            if test['website_price'] is not None:
                website_price = test['website_price']
                difference = backend_price - website_price
                percent_diff = (difference / website_price) * 100
                
                print(f"Website Total: ${website_price:,.2f}")
                print(f"Difference: ${difference:+,.2f} ({percent_diff:+.2f}%)")
                
                # Allow 0.01% tolerance for rounding
                if abs(percent_diff) < 0.01:
                    print("✅ EXACT MATCH")
                    passed += 1
                else:
                    print("❌ MISMATCH")
                    failed += 1
                    
                    # Show breakdown for debugging
                    print(f"\nBreakdown:")
                    print(f"  BizCost: ${result.breakdown['biz_cost']:,.2f}")
                    print(f"  Profit: ${result.breakdown['profit_amount']:,.2f} ({result.breakdown['profit_margin_rate']*100:.0f}%)")
                    print(f"  Subtotal: ${result.breakdown['subtotal']:,.2f}")
                    print(f"  ×1.15: ${result.breakdown['total_before_surcharge']:,.2f}")
                    print(f"  +$44: ${result.breakdown['total_price']:,.2f}")
            else:
                print("⏳ NEEDS WEBSITE VALIDATION")
                
                # Show key details for website checking
                print(f"\nSpecifications:")
                print(f"  Quantity: {result.specifications['quantity']}")
                print(f"  Pages: {result.specifications['internal_pages']}")
                print(f"  Size: {result.specifications['finish_size']}")
                print(f"  Artworks: {result.specifications['artworks']}")
                print(f"  Outer Front Cover: {result.specifications['outer_front_cover']}")
                print(f"  Printed Front Cover: {result.specifications['printed_front_cover']}")
                print(f"  Front Cover Print: {result.specifications['front_cover_print']}")
                print(f"  Front Celloglaze: {result.specifications['front_celloglaze']}")
                print(f"  Outer Back Cover: {result.specifications['outer_back_cover']}")
                print(f"  Printed Back Cover: {result.specifications['printed_back_cover']}")
                print(f"  Back Cover Print: {result.specifications['back_cover_print']}")
                print(f"  Back Celloglaze: {result.specifications['back_celloglaze']}")
                print(f"  Internal Stock: {result.specifications['internal_stock']}")
                print(f"  Internal Print: {result.specifications['internal_print']}")
                print(f"  Thickness: {result.specifications['book_thickness_mm']:.2f}mm")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if passed == 5:
        print("\n🎉 ALL TESTS PASS - Wire Bound Books calculator 100% accurate!")


if __name__ == "__main__":
    test_wire_bound_books()
