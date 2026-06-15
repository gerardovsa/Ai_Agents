"""
Test Suite for With Compliments Slips Shopify Calculator
CREATED: Jan 24, 2026

Tests backend against TXT formula (lines 2581-2930)
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from WithComplimentsSlips_Shopify_Calculator import WithComplimentsSlipsShopifyCalculator


def test_with_compliments_slips():
    """
    Test With Compliments Slips calculator with 4 comprehensive test cases
    
    All tests use exact TXT formula implementation:
    - Setup costs: impos=15, guilo=12, extraArts=15 (first FREE)
    - DL size: 6 slips per sheet (F4.price)
    - Paper stocks: 80GSM=$26.34, 90GSM=$29.51, 100GSM=$32.68 per 1000
    - Print: Colour=$0.044, B&W=$0.02 per sheet
    - Sides: Single=1×, Double=2×
    - Stock waste: 1.05 (5%)
    - Cutting: $11 per 500 sheets
    - Profit: 11 tiers (170% → 25% → fixed $200)
    - Double GST: ×1.1 ×1.1
    """
    
    calc = WithComplimentsSlipsShopifyCalculator()
    
    print("=" * 80)
    print("WITH COMPLIMENTS SLIPS SHOPIFY CALCULATOR - TEST SUITE")
    print("=" * 80)
    print("\nBackend: WithComplimentsSlips_Shopify_Calculator.py")
    print("TXT Source: Lines 2581-2930")
    print("Date: January 24, 2026")
    print("\n" + "=" * 80)
    
    # ========================================================================
    # TEST 1: Small quantity, single side, colour, 80GSM, 1 artwork
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 1: Small Quantity - Single Side Colour")
    print("=" * 80)
    
    result1 = calc.calculate(
        quantity=250,
        print_sides="Single side print",
        print_type="Colour",
        finish_size="DL - 99mm x 210mm",
        paper_stock="Uncoated Bond 80GSM",
        artworks=1
    )
    
    print(f"\nInput Parameters:")
    print(f"  Quantity: 250")
    print(f"  Print Sides: Single side print")
    print(f"  Print Type: Colour")
    print(f"  Finish Size: DL - 99mm x 210mm (6 slips per sheet)")
    print(f"  Paper Stock: Uncoated Bond 80GSM")
    print(f"  Artworks: 1 (FREE)")
    
    print(f"\nCalculation Breakdown:")
    print(f"  Setup Costs: ${result1.breakdown['setup_costs']:.2f}")
    print(f"    - Impos: ${result1.breakdown['impos_setup']:.2f}")
    print(f"    - Guilo: ${result1.breakdown['guilo_setup']:.2f}")
    print(f"    - Artwork: ${result1.breakdown['artwork_setup_cost']:.2f}")
    print(f"  Sheets Needed: {result1.breakdown['sheets_needed']:.2f} (250 slips / 6 per sheet × 1.05)")
    print(f"  Stock Cost: ${result1.breakdown['stock_cost']:.2f}")
    print(f"  Click Cost: ${result1.breakdown['click_cost']:.2f}")
    print(f"  Cutting Cost: ${result1.breakdown['cutting_cost']:.2f}")
    print(f"  Business Cost: ${result1.breakdown['biz_cost']:.2f}")
    print(f"  Profit Margin: {result1.breakdown['profit_margin_rate']:.2f} ({result1.breakdown['profit_margin_rate']*100:.0f}%)")
    print(f"  Profit Amount: ${result1.breakdown['profit_amount']:.2f}")
    print(f"  Subtotal: ${result1.breakdown['subtotal']:.2f}")
    print(f"  After 1st GST (×1.1): ${result1.breakdown['first_gst']:.2f}")
    print(f"  After 2nd GST (×1.1): ${result1.total_price:.2f}")
    
    print(f"\n✅ TEST 1 RESULT: ${result1.total_price:.2f}")
    print(f"   Per slip: ${result1.unit_price:.2f}")
    
    # ========================================================================
    # TEST 2: Large quantity, double side, B&W, 100GSM, 2 artworks
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 2: Large Quantity - Double Side B&W with Extra Artwork")
    print("=" * 80)
    
    result2 = calc.calculate(
        quantity=5000,
        print_sides="Double side print",
        print_type="Black & White",
        finish_size="DL - 99mm x 210mm",
        paper_stock="Uncoated Bond 100GSM",
        artworks=2
    )
    
    print(f"\nInput Parameters:")
    print(f"  Quantity: 5000")
    print(f"  Print Sides: Double side print")
    print(f"  Print Type: Black & White")
    print(f"  Finish Size: DL - 99mm x 210mm (6 slips per sheet)")
    print(f"  Paper Stock: Uncoated Bond 100GSM")
    print(f"  Artworks: 2 (first FREE, +$15 for second)")
    
    print(f"\nCalculation Breakdown:")
    print(f"  Setup Costs: ${result2.breakdown['setup_costs']:.2f}")
    print(f"    - Impos: ${result2.breakdown['impos_setup']:.2f}")
    print(f"    - Guilo: ${result2.breakdown['guilo_setup']:.2f}")
    print(f"    - Artwork: ${result2.breakdown['artwork_setup_cost']:.2f}")
    print(f"  Sheets Needed: {result2.breakdown['sheets_needed']:.2f} (5000 slips / 6 per sheet × 1.05)")
    print(f"  Stock Cost: ${result2.breakdown['stock_cost']:.2f}")
    print(f"  Click Cost: ${result2.breakdown['click_cost']:.2f}")
    print(f"  Cutting Cost: ${result2.breakdown['cutting_cost']:.2f}")
    print(f"  Business Cost: ${result2.breakdown['biz_cost']:.2f}")
    print(f"  Profit Margin: {result2.breakdown['profit_margin_rate']:.2f} ({result2.breakdown['profit_margin_rate']*100:.0f}%)")
    print(f"  Profit Amount: ${result2.breakdown['profit_amount']:.2f}")
    print(f"  Subtotal: ${result2.breakdown['subtotal']:.2f}")
    print(f"  After 1st GST (×1.1): ${result2.breakdown['first_gst']:.2f}")
    print(f"  After 2nd GST (×1.1): ${result2.total_price:.2f}")
    
    print(f"\n✅ TEST 2 RESULT: ${result2.total_price:.2f}")
    print(f"   Per slip: ${result2.unit_price:.2f}")
    
    # ========================================================================
    # TEST 3: Medium quantity, double side, colour, 90GSM, 1 artwork
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 3: Medium Quantity - Double Side Colour")
    print("=" * 80)
    
    result3 = calc.calculate(
        quantity=1000,
        print_sides="Double side print",
        print_type="Colour",
        finish_size="DL - 99mm x 210mm",
        paper_stock="Uncoated Bond 90GSM",
        artworks=1
    )
    
    print(f"\nInput Parameters:")
    print(f"  Quantity: 1000")
    print(f"  Print Sides: Double side print")
    print(f"  Print Type: Colour")
    print(f"  Finish Size: DL - 99mm x 210mm (6 slips per sheet)")
    print(f"  Paper Stock: Uncoated Bond 90GSM")
    print(f"  Artworks: 1 (FREE)")
    
    print(f"\nCalculation Breakdown:")
    print(f"  Setup Costs: ${result3.breakdown['setup_costs']:.2f}")
    print(f"  Sheets Needed: {result3.breakdown['sheets_needed']:.2f}")
    print(f"  Stock Cost: ${result3.breakdown['stock_cost']:.2f}")
    print(f"  Click Cost: ${result3.breakdown['click_cost']:.2f}")
    print(f"  Cutting Cost: ${result3.breakdown['cutting_cost']:.2f}")
    print(f"  Business Cost: ${result3.breakdown['biz_cost']:.2f}")
    print(f"  Profit Margin: {result3.breakdown['profit_margin_rate']:.2f} ({result3.breakdown['profit_margin_rate']*100:.0f}%)")
    print(f"  Subtotal: ${result3.breakdown['subtotal']:.2f}")
    print(f"  Total (Double GST): ${result3.total_price:.2f}")
    
    print(f"\n✅ TEST 3 RESULT: ${result3.total_price:.2f}")
    print(f"   Per slip: ${result3.unit_price:.2f}")
    
    # ========================================================================
    # TEST 4: Minimum quantity, single side, B&W, 80GSM, 1 artwork
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 4: Minimum Quantity - Single Side B&W")
    print("=" * 80)
    
    result4 = calc.calculate(
        quantity=50,
        print_sides="Single side print",
        print_type="Black & White",
        finish_size="DL - 99mm x 210mm",
        paper_stock="Uncoated Bond 80GSM",
        artworks=1
    )
    
    print(f"\nInput Parameters:")
    print(f"  Quantity: 50")
    print(f"  Print Sides: Single side print")
    print(f"  Print Type: Black & White")
    print(f"  Finish Size: DL - 99mm x 210mm (6 slips per sheet)")
    print(f"  Paper Stock: Uncoated Bond 80GSM")
    print(f"  Artworks: 1 (FREE)")
    
    print(f"\nCalculation Breakdown:")
    print(f"  Setup Costs: ${result4.breakdown['setup_costs']:.2f}")
    print(f"  Sheets Needed: {result4.breakdown['sheets_needed']:.2f}")
    print(f"  Stock Cost: ${result4.breakdown['stock_cost']:.2f}")
    print(f"  Click Cost: ${result4.breakdown['click_cost']:.2f}")
    print(f"  Cutting Cost: ${result4.breakdown['cutting_cost']:.2f}")
    print(f"  Business Cost: ${result4.breakdown['biz_cost']:.2f}")
    print(f"  Profit Margin: {result4.breakdown['profit_margin_rate']:.2f} ({result4.breakdown['profit_margin_rate']*100:.0f}%)")
    print(f"  Subtotal: ${result4.breakdown['subtotal']:.2f}")
    print(f"  Total (Double GST): ${result4.total_price:.2f}")
    
    print(f"\n✅ TEST 4 RESULT: ${result4.total_price:.2f}")
    print(f"   Per slip: ${result4.unit_price:.2f}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("BACKEND TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"\n✅ TEST 1 (250 qty, Single, Colour, 80GSM, 1 art):  ${result1.total_price:.2f}")
    print(f"✅ TEST 2 (5000 qty, Double, B&W, 100GSM, 2 arts):  ${result2.total_price:.2f}")
    print(f"✅ TEST 3 (1000 qty, Double, Colour, 90GSM, 1 art): ${result3.total_price:.2f}")
    print(f"✅ TEST 4 (50 qty, Single, B&W, 80GSM, 1 art):      ${result4.total_price:.2f}")
    
    print("\n" + "=" * 80)
    print("WEBSITE VALIDATION INSTRUCTIONS")
    print("=" * 80)
    print("\nGo to: https://[shopify-store]/products/with-compliments-slips")
    print("\nTest each configuration and compare prices:\n")
    
    print("TEST 1:")
    print("  - Quantity: 250")
    print("  - Print Sides: Single side print")
    print("  - Print Type: Colour")
    print("  - Finish Size: DL - 99mm x 210mm")
    print("  - Paper Stock Type: Uncoated Bond 80GSM")
    print("  - Artworks: 1")
    print(f"  - Expected: ${result1.total_price:.2f}")
    print("  - Website: $______")
    print("  - Match: ☐ YES  ☐ NO\n")
    
    print("TEST 2:")
    print("  - Quantity: 5000")
    print("  - Print Sides: Double side print")
    print("  - Print Type: Black & White")
    print("  - Finish Size: DL - 99mm x 210mm")
    print("  - Paper Stock Type: Uncoated Bond 100GSM")
    print("  - Artworks: 2")
    print(f"  - Expected: ${result2.total_price:.2f}")
    print("  - Website: $______")
    print("  - Match: ☐ YES  ☐ NO\n")
    
    print("TEST 3:")
    print("  - Quantity: 1000")
    print("  - Print Sides: Double side print")
    print("  - Print Type: Colour")
    print("  - Finish Size: DL - 99mm x 210mm")
    print("  - Paper Stock Type: Uncoated Bond 90GSM")
    print("  - Artworks: 1")
    print(f"  - Expected: ${result3.total_price:.2f}")
    print("  - Website: $______")
    print("  - Match: ☐ YES  ☐ NO\n")
    
    print("TEST 4:")
    print("  - Quantity: 50")
    print("  - Print Sides: Single side print")
    print("  - Print Type: Black & White")
    print("  - Finish Size: DL - 99mm x 210mm")
    print("  - Paper Stock Type: Uncoated Bond 80GSM")
    print("  - Artworks: 1")
    print(f"  - Expected: ${result4.total_price:.2f}")
    print("  - Website: $______")
    print("  - Match: ☐ YES  ☐ NO\n")
    
    print("=" * 80)


if __name__ == "__main__":
    test_with_compliments_slips()
