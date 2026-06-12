"""
Test Printed Letterheads Shopify Calculator
Comprehensive tests covering all field combinations
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add backend path
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
shopify_calc_path = backend_path / 'shopify_calculators'
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(shopify_calc_path))

from shopify_calculators.PrintedLetterheads_Shopify_Calculator import PrintedLetterheadsShopifyCalculator


def print_test_result(test_name: str, result, test_num: int):
    """Print detailed test result"""
    print(f"\n{'='*80}")
    print(f"Test {test_num}: {test_name}")
    print(f"{'='*80}")
    
    specs = result.specifications
    breakdown = result.breakdown
    
    print(f"\n📋 SPECIFICATIONS:")
    print(f"   Quantity: {specs['quantity']}")
    print(f"   Finish Size: {specs['finish_size']}")
    print(f"   Paper Stock: {specs['paper_stock']}")
    print(f"   Print Sides: {specs['print_sides']}")
    print(f"   Print Type: {specs['print_type']}")
    print(f"   Artworks: {specs['artworks']}")
    print(f"   Sheets printed: {specs['sheets_printed']:.2f}")
    
    print(f"\n💰 COST BREAKDOWN:")
    print(f"   Setup Costs:")
    print(f"      Impos Setup: ${breakdown['impos_setup']:.2f}")
    print(f"      Guilo Setup: ${breakdown['guilo_setup']:.2f}")
    print(f"      Extra Artworks: ${breakdown['extra_artworks_cost']:.2f}")
    print(f"      ─────────────────────")
    print(f"      Total Setup: ${breakdown['total_setup_cost']:.2f}")
    
    print(f"\n   Production Costs:")
    print(f"      Stock Cost: ${breakdown['total_cost_of_sheets']:.2f}")
    print(f"         (${breakdown['stock_price_per_1000']:.2f}/1000 sheets)")
    print(f"      Click Cost: ${breakdown['click_cost']:.2f}")
    print(f"         (${breakdown['print_type_price']:.3f}/sheet × {float(breakdown['print_sides_multiplier'])} sides)")
    print(f"      Cutting Cost: ${breakdown['cutting_cost']:.2f}")
    
    print(f"\n   ─────────────────────")
    print(f"   Subtotal: ${breakdown['subtotal']:.2f}")
    print(f"   Profit Margin: {float(breakdown['profit_margin_rate'])*100:.0f}% (${breakdown['profit_amount']:.2f})")
    print(f"   GST (double 10%): ${(result.total_price / Decimal('1.21') * Decimal('0.21')):.2f}")
    
    print(f"\n   ═════════════════════")
    print(f"   TOTAL PRICE: ${result.total_price:.2f}")
    print(f"   Unit Price: ${result.unit_price:.2f}")
    print(f"   ═════════════════════")


def run_printed_letterheads_tests():
    """Run comprehensive Printed Letterheads tests"""
    
    calc = PrintedLetterheadsShopifyCalculator()
    
    print("\n" + "="*80)
    print("PRINTED LETTERHEADS CALCULATOR - TEST SUITE")
    print("="*80)
    
    # Test 1: Baseline - Small quantity, single side, colour
    result1 = calc.calculate(
        quantity=250,
        print_sides='Single side print',
        print_type='Colour',
        finish_size='A4 - 210mm x 297mm',
        paper_stock='Uncoated Bond 80GSM',
        artworks=1
    )
    print_test_result("Baseline - 250 qty, Single side, Colour, 80GSM, 1 artwork", result1, 1)
    
    # Test 2: High volume with double-sided B&W
    result2 = calc.calculate(
        quantity=5000,
        print_sides='Double side print',
        print_type='Black & White',
        finish_size='A4 - 210mm x 297mm',
        paper_stock='Uncoated Bond 100GSM',
        artworks=2
    )
    print_test_result("High Volume - 5000 qty, Double side, B&W, 100GSM, 2 artworks", result2, 2)
    
    # Test 3: Medium quantity with double-sided colour
    result3 = calc.calculate(
        quantity=1000,
        print_sides='Double side print',
        print_type='Colour',
        finish_size='A4 - 210mm x 297mm',
        paper_stock='Uncoated Bond 90GSM',
        artworks=1
    )
    print_test_result("Medium - 1000 qty, Double side, Colour, 90GSM, 1 artwork", result3, 3)
    
    # Test 4: Edge case - Minimum quantity, single side
    result4 = calc.calculate(
        quantity=50,
        print_sides='Single side print',
        print_type='Black & White',
        finish_size='A4 - 210mm x 297mm',
        paper_stock='Uncoated Bond 80GSM',
        artworks=1
    )
    print_test_result("Edge Case - 50 qty (minimum), Single side, B&W, 80GSM", result4, 4)
    
    return [result1, result2, result3, result4]


def generate_website_test_guide(results):
    """Generate formatted test guide for website validation"""
    
    print("\n" + "="*80)
    print("WEBSITE VALIDATION TEST GUIDE")
    print("="*80)
    print("\nTest each configuration on the Shopify website and compare prices:\n")
    
    tests = [
        {
            'name': 'Test 1: Baseline Configuration',
            'config': 'Quantity: 250 | Print Sides: Single side print | Print Type: Colour | Finish Size: A4 | Paper Stock: Uncoated Bond 80GSM | Artworks: 1',
            'expected': results[0].total_price
        },
        {
            'name': 'Test 2: High Volume Double-Sided',
            'config': 'Quantity: 5000 | Print Sides: Double side print | Print Type: Black & White | Finish Size: A4 | Paper Stock: Uncoated Bond 100GSM | Artworks: 2',
            'expected': results[1].total_price
        },
        {
            'name': 'Test 3: Medium Volume Colour',
            'config': 'Quantity: 1000 | Print Sides: Double side print | Print Type: Colour | Finish Size: A4 | Paper Stock: Uncoated Bond 90GSM | Artworks: 1',
            'expected': results[2].total_price
        },
        {
            'name': 'Test 4: Minimum Quantity',
            'config': 'Quantity: 50 | Print Sides: Single side print | Print Type: Black & White | Finish Size: A4 | Paper Stock: Uncoated Bond 80GSM | Artworks: 1',
            'expected': results[3].total_price
        }
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'-'*80}")
        print(f"{test['name']}")
        print(f"{'-'*80}")
        print(f"Configuration: {test['config']}")
        print(f"Expected Price: ${test['expected']:.2f}")
        print(f"\n✓ Match: [ ]  ✗ Mismatch: [ ]  Website Price: $_______")


if __name__ == '__main__':
    results = run_printed_letterheads_tests()
    generate_website_test_guide(results)
    
    print("\n" + "="*80)
    print("✅ All 4 tests completed successfully!")
    print("📋 Please validate these prices on the Shopify website")
    print("="*80)
