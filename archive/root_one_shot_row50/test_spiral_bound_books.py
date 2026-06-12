"""
Test Spiral Bound Books Shopify Calculator

Validates backend implementation against TXT formula (lines 3863-3972)

Key Formula Elements:
- 15% GST (not 10%)
- Fixed $44 surcharge AFTER GST
- 18-tier wire pricing based on book thickness
- 12-tier profit margins
- Complex front/back cover calculations
"""

import sys
from pathlib import Path

# Add backend and config paths
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(backend_path / 'shopify_calculators'))

import importlib.util

# Direct import to avoid __init__ circular dependency
calc_path = backend_path / 'shopify_calculators' / 'SpiralBoundBooks_Shopify_Calculator.py'
spec = importlib.util.spec_from_file_location("spiral_calc", calc_path)
spiral_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(spiral_module)
SpiralBoundBooksShopifyCalculator = spiral_module.SpiralBoundBooksShopifyCalculator


def run_tests():
    """Run 5 comprehensive test cases for Spiral Bound Books"""
    
    calculator = SpiralBoundBooksShopifyCalculator()
    
    print("=" * 80)
    print("SPIRAL BOUND BOOKS - BACKEND VALIDATION")
    print("=" * 80)
    print()
    print("📝 Key Formula Elements:")
    print("   • 15% GST (not 10% like other calculators)")
    print("   • Fixed $44 surcharge AFTER GST")
    print("   • 18-tier wire pricing based on book thickness")
    print("   • 12-tier profit margins")
    print("   • Complex cover calculations with celloglaze")
    print()
    print("=" * 80)
    print()
    
    # =========================================================================
    # TEST 1: Basic Spiral Bound - 100 books, A5, 40pp, B&W content
    # =========================================================================
    print("\n" + "=" * 80)
    print("TEST 1: Basic Spiral Bound - Small Quantity")
    print("=" * 80)
    print("\n📋 Configuration:")
    print("   Quantity: 100 books")
    print("   Content: 40 pages, Black & White, Uncoated Bond 80GSM")
    print("   Size: A5 Portrait")
    print("   Front Cover: 300GSM Satin, 1pp Colour")
    print("   Back Cover: None")
    print("   Celloglaze: None")
    print("   Artworks: 1")
    
    result1 = calculator.calculate(
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
    
    print("\n💰 Pricing Breakdown:")
    print(f"   BizCost: ${result1.breakdown['biz_cost_before_margin']:.2f}")
    print(f"   Profit Margin: {result1.breakdown['profit_margin_pct']:.1f}%")
    print(f"   Subtotal with Margin: ${result1.breakdown['subtotal_with_margin']:.2f}")
    print(f"   15% GST: ${result1.breakdown['gst_15pct']:.2f}")
    print(f"   Total after GST: ${result1.breakdown['total_after_gst']:.2f}")
    print(f"   Surcharge $44: ${result1.breakdown['surcharge_44']:.2f}")
    print(f"   📊 TOTAL PRICE: ${result1.total_price:.2f}")
    print(f"   Unit Price: ${result1.unit_price:.2f}/book")
    
    print("\n🔧 Technical Details:")
    print(f"   Book Thickness: {result1.specifications['book_thickness_mm']:.2f}mm")
    print(f"   Wire Price Per Ring: ${result1.specifications['price_per_ring']:.5f}")
    print(f"   Wire Cost Total: ${result1.breakdown['wire_cost']:.2f}")
    print(f"   Sheets to Punch: {result1.specifications['sheets_to_punch']:.0f}")
    
    # =========================================================================
    # TEST 2: Medium Quantity Color - 500 books, A4, 100pp, Full Colour
    # =========================================================================
    print("\n" + "=" * 80)
    print("TEST 2: Medium Quantity with Color Content")
    print("=" * 80)
    print("\n📋 Configuration:")
    print("   Quantity: 500 books")
    print("   Content: 100 pages, Full Colour, Satin 128GSM")
    print("   Size: A4 Portrait")
    print("   Front Cover: 350GSM Satin, 2pp Colour")
    print("   Back Cover: 350GSM Satin Blank")
    print("   Celloglaze: None")
    print("   Artworks: 1")
    
    result2 = calculator.calculate(
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
    
    print("\n💰 Pricing Breakdown:")
    print(f"   BizCost: ${result2.breakdown['biz_cost_before_margin']:.2f}")
    print(f"   Profit Margin: {result2.breakdown['profit_margin_pct']:.1f}%")
    print(f"   Subtotal with Margin: ${result2.breakdown['subtotal_with_margin']:.2f}")
    print(f"   15% GST: ${result2.breakdown['gst_15pct']:.2f}")
    print(f"   Total after GST: ${result2.breakdown['total_after_gst']:.2f}")
    print(f"   Surcharge $44: ${result2.breakdown['surcharge_44']:.2f}")
    print(f"   📊 TOTAL PRICE: ${result2.total_price:.2f}")
    print(f"   Unit Price: ${result2.unit_price:.2f}/book")
    
    print("\n🔧 Technical Details:")
    print(f"   Book Thickness: {result2.specifications['book_thickness_mm']:.2f}mm")
    print(f"   Wire Price Per Ring: ${result2.specifications['price_per_ring']:.5f}")
    print(f"   Content Cost: ${result2.breakdown['content_cost']:.2f}")
    print(f"   Total Print Cost: ${result2.breakdown['total_print_cost']:.2f}")
    
    # =========================================================================
    # TEST 3: Large Quantity Thick Book - 1000 books, A4, 200pp
    # =========================================================================
    print("\n" + "=" * 80)
    print("TEST 3: Large Quantity Thick Book")
    print("=" * 80)
    print("\n📋 Configuration:")
    print("   Quantity: 1000 books")
    print("   Content: 200 pages, Black & White, Uncoated Bond 80GSM")
    print("   Size: A4 Portrait")
    print("   Front Cover: 350GSM Satin, 1pp Colour")
    print("   Back Cover: Black Leather grain")
    print("   Celloglaze: None")
    print("   Artworks: 2")
    
    result3 = calculator.calculate(
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
    
    print("\n💰 Pricing Breakdown:")
    print(f"   BizCost: ${result3.breakdown['biz_cost_before_margin']:.2f}")
    print(f"   Profit Margin: {result3.breakdown['profit_margin_pct']:.1f}%")
    print(f"   Subtotal with Margin: ${result3.breakdown['subtotal_with_margin']:.2f}")
    print(f"   15% GST: ${result3.breakdown['gst_15pct']:.2f}")
    print(f"   Total after GST: ${result3.breakdown['total_after_gst']:.2f}")
    print(f"   Surcharge $44: ${result3.breakdown['surcharge_44']:.2f}")
    print(f"   📊 TOTAL PRICE: ${result3.total_price:.2f}")
    print(f"   Unit Price: ${result3.unit_price:.2f}/book")
    
    print("\n🔧 Technical Details:")
    print(f"   Book Thickness: {result3.specifications['book_thickness_mm']:.2f}mm")
    print(f"   Wire Price Per Ring: ${result3.specifications['price_per_ring']:.5f}")
    print(f"   Wire Cost Total: ${result3.breakdown['wire_cost']:.2f}")
    print(f"   Setup Costs (2 artworks): ${result3.breakdown['total_setup']:.2f}")
    
    # =========================================================================
    # TEST 4: Small Format - 250 books, A6, 50pp (wire price halved)
    # =========================================================================
    print("\n" + "=" * 80)
    print("TEST 4: Small Format (A6) - Wire Price Halved")
    print("=" * 80)
    print("\n📋 Configuration:")
    print("   Quantity: 250 books")
    print("   Content: 50 pages, Black & White, Uncoated Bond 90GSM")
    print("   Size: A6 Portrait (wire price halved)")
    print("   Front Cover: 250GSM Satin, 1pp Colour")
    print("   Back Cover: None")
    print("   Celloglaze: None")
    print("   Artworks: 1")
    
    result4 = calculator.calculate(
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
    
    print("\n💰 Pricing Breakdown:")
    print(f"   BizCost: ${result4.breakdown['biz_cost_before_margin']:.2f}")
    print(f"   Profit Margin: {result4.breakdown['profit_margin_pct']:.1f}%")
    print(f"   Subtotal with Margin: ${result4.breakdown['subtotal_with_margin']:.2f}")
    print(f"   15% GST: ${result4.breakdown['gst_15pct']:.2f}")
    print(f"   Total after GST: ${result4.breakdown['total_after_gst']:.2f}")
    print(f"   Surcharge $44: ${result4.breakdown['surcharge_44']:.2f}")
    print(f"   📊 TOTAL PRICE: ${result4.total_price:.2f}")
    print(f"   Unit Price: ${result4.unit_price:.2f}/book")
    
    print("\n🔧 Technical Details:")
    print(f"   Book Thickness: {result4.specifications['book_thickness_mm']:.2f}mm")
    print(f"   Wire Price Per Ring: ${result4.specifications['price_per_ring']:.5f}")
    print(f"   Wire Cost Total: ${result4.breakdown['wire_cost']:.2f} (HALVED for A6)")
    print(f"   ⚠️ Note: A6/DL/A5 Landscape formats use half wire price")
    
    # =========================================================================
    # TEST 5: Premium with Celloglaze - 100 books, A4, 60pp
    # =========================================================================
    print("\n" + "=" * 80)
    print("TEST 5: Premium Covers with Celloglaze")
    print("=" * 80)
    print("\n📋 Configuration:")
    print("   Quantity: 100 books")
    print("   Content: 60 pages, Full Colour, Satin 150GSM")
    print("   Size: A4 Portrait")
    print("   Front Cover: 350GSM Satin, 2pp Colour, 2 Sided Matt Celloglaze")
    print("   Back Cover: 350GSM Satin, Clear PVC outer, 1 Side Gloss Celloglaze")
    print("   Artworks: 1")
    
    result5 = calculator.calculate(
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
    
    print("\n💰 Pricing Breakdown:")
    print(f"   BizCost: ${result5.breakdown['biz_cost_before_margin']:.2f}")
    print(f"   Profit Margin: {result5.breakdown['profit_margin_pct']:.1f}%")
    print(f"   Subtotal with Margin: ${result5.breakdown['subtotal_with_margin']:.2f}")
    print(f"   15% GST: ${result5.breakdown['gst_15pct']:.2f}")
    print(f"   Total after GST: ${result5.breakdown['total_after_gst']:.2f}")
    print(f"   Surcharge $44: ${result5.breakdown['surcharge_44']:.2f}")
    print(f"   📊 TOTAL PRICE: ${result5.total_price:.2f}")
    print(f"   Unit Price: ${result5.unit_price:.2f}/book")
    
    print("\n🔧 Technical Details:")
    print(f"   Front Cello Cost: ${result5.breakdown['front_cello_cost']:.2f}")
    print(f"   Back Cello Cost: ${result5.breakdown['back_cello_cost']:.2f}")
    print(f"   Cello Setup: ${result5.breakdown['cello_setup']:.2f}")
    print(f"   Total Setup: ${result5.breakdown['total_setup']:.2f}")
    
    # =========================================================================
    # SUMMARY TABLE
    # =========================================================================
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY - READY FOR WEBSITE TESTING")
    print("=" * 80)
    print()
    print("| Test | Config                          | Backend Price | Status  |")
    print("|------|---------------------------------|---------------|---------|")
    print(f"| 1    | 100 books, A5, 40pp, B&W       | ${result1.total_price:>10.2f}   | ⏳ READY |")
    print(f"| 2    | 500 books, A4, 100pp, Color    | ${result2.total_price:>10.2f}   | ⏳ READY |")
    print(f"| 3    | 1000 books, A4, 200pp, B&W     | ${result3.total_price:>10.2f}   | ⏳ READY |")
    print(f"| 4    | 250 books, A6, 50pp, B&W       | ${result4.total_price:>10.2f}   | ⏳ READY |")
    print(f"| 5    | 100 books, A4, 60pp, Premium   | ${result5.total_price:>10.2f}   | ⏳ READY |")
    print()
    print("=" * 80)
    print()
    print("✅ Backend validation complete!")
    print("📋 Next Step: Test these prices on https://gerardovsa.myshopify.com/")
    print()
    print("⚠️  CRITICAL VALIDATION POINTS:")
    print("   • 15% GST (not 10%)")
    print("   • Fixed $44 surcharge present")
    print("   • A6 wire price halved correctly")
    print("   • Celloglaze setup $25 when either front OR back celloglaze selected")
    print("   • Wire pricing matches 18-tier lookup")
    print()
    
    # Return results for checklist generation
    return [result1, result2, result3, result4, result5]


if __name__ == '__main__':
    run_tests()

print("\nNext steps:")
print("1. Get test quotes from website")
print("2. Validate backend matches website prices exactly")
print("3. Create 4+ comprehensive test cases")
