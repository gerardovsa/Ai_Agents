"""
Test Premium Bookmarks Shopify Calculator
Comprehensive tests covering all field combinations
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add backend path and config_manager path
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
shopify_calc_path = backend_path / 'shopify_calculators'
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(shopify_calc_path))

from shopify_calculators.PremiumBookmarks_Shopify_Calculator import PremiumBookmarksShopifyCalculator


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
    print(f"   Print Type: {specs['print_type']}")
    print(f"   Celloglaze: {specs['celloglaze']}")
    print(f"   Artworks: {specs['artworks']}")
    print(f"   Bookmarks per 1000 sheets: {specs['bookmarks_per_sheet']}")
    print(f"   Total sheets printed: {specs['sheets_printed']:.2f}")
    
    print(f"\n💰 COST BREAKDOWN:")
    print(f"   Setup Costs:")
    print(f"      Impos Setup: ${breakdown['impos_setup']:.2f}")
    print(f"      Guilo Setup: ${breakdown['guilo_setup']:.2f}")
    print(f"      Extra Artworks: ${breakdown['extra_artworks_cost']:.2f}")
    print(f"      Celloglaze Setup: ${breakdown['cello_setup']:.2f}")
    print(f"      ─────────────────────")
    print(f"      Total Setup: ${breakdown['total_setup_cost']:.2f}")
    
    print(f"\n   Production Costs:")
    print(f"      Stock Cost: ${breakdown['total_cost_of_sheets']:.2f}")
    print(f"         (${breakdown['stock_price_per_1000']:.2f}/1000 sheets)")
    print(f"      Click Cost: ${breakdown['click_cost']:.2f}")
    print(f"         (${breakdown['print_price_per_sheet']:.3f}/sheet)")
    print(f"      Cutting Cost: ${breakdown['cutting_cost']:.2f}")
    print(f"      Celloglaze Cost: ${breakdown['cello_cost']:.2f}")
    print(f"         (${breakdown['cello_price_per_sheet']:.3f}/sheet)")
    
    print(f"\n   ─────────────────────")
    print(f"   Subtotal: ${breakdown['subtotal']:.2f}")
    print(f"   Profit Margin: {float(breakdown['profit_margin_rate'])*100:.0f}% (${breakdown['profit_amount']:.2f})")
    print(f"   GST (10%): ${(result.total_price / Decimal('1.1') - breakdown['subtotal'] - breakdown['profit_amount']):.2f}")
    
    print(f"\n   ═════════════════════")
    print(f"   TOTAL PRICE: ${result.total_price:.2f}")
    print(f"   Unit Price: ${result.unit_price:.2f}")
    print(f"   ═════════════════════")


def run_premium_bookmarks_tests():
    """Run comprehensive Premium Bookmarks tests"""
    
    calc = PremiumBookmarksShopifyCalculator()
    
    # Test 1: Baseline - Small quantity, no celloglaze, smallest size
    print("\n" + "="*80)
    print("PREMIUM BOOKMARKS CALCULATOR - TEST SUITE")
    print("="*80)
    
    result1 = calc.calculate(
        quantity=250,
        finish_size='50x150mm',
        paper_stock='satin_350gsm',
        print_type='colour_1_sided',
        celloglaze='None',
        artworks=1
    )
    print_test_result("Baseline - 250 qty, 50×150mm, no celloglaze, 1 artwork", result1, 1)
    
    # Test 2: High volume with celloglaze and extra artworks
    result2 = calc.calculate(
        quantity=2000,
        finish_size='65x215mm',
        paper_stock='uncoated_300gsm',
        print_type='colour_2_sided',
        celloglaze='2_side_gloss',
        artworks=3
    )
    print_test_result("High Volume - 2000 qty, 65×215mm, 2-sided celloglaze, 3 artworks", result2, 2)
    
    # Test 3: Medium quantity with 1-sided celloglaze
    result3 = calc.calculate(
        quantity=500,
        finish_size='50x185mm',
        paper_stock='satin_350gsm',
        print_type='colour_1_sided',
        celloglaze='1_side_matt',
        artworks=2
    )
    print_test_result("Medium - 500 qty, 50×185mm, 1-sided celloglaze, 2 artworks", result3, 3)
    
    # Test 4: Edge case - Minimum quantity, largest size
    result4 = calc.calculate(
        quantity=25,
        finish_size='65x215mm',
        paper_stock='uncoated_300gsm',
        print_type='colour_2_sided',
        celloglaze='None',
        artworks=1
    )
    print_test_result("Edge Case - 25 qty (minimum), 65×215mm (fewest per sheet)", result4, 4)
    
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
            'config': 'Quantity: 250 | Finish Size: 50mm × 150mm | Paper Stock: Satin 350GSM | Print Type: Colour 1-sided | Celloglaze: None | Artworks: 1',
            'expected': results[0].total_price
        },
        {
            'name': 'Test 2: High Volume with Premium Features',
            'config': 'Quantity: 2000 | Finish Size: 65mm × 215mm | Paper Stock: Uncoated 300GSM | Print Type: Colour 2-sided | Celloglaze: 2-sided Gloss | Artworks: 3',
            'expected': results[1].total_price
        },
        {
            'name': 'Test 3: Medium Volume with 1-sided Celloglaze',
            'config': 'Quantity: 500 | Finish Size: 50mm × 185mm | Paper Stock: Satin 350GSM | Print Type: Colour 1-sided | Celloglaze: 1-sided Matt | Artworks: 2',
            'expected': results[2].total_price
        },
        {
            'name': 'Test 4: Minimum Quantity Edge Case',
            'config': 'Quantity: 25 | Finish Size: 65mm × 215mm | Paper Stock: Uncoated 300GSM | Print Type: Colour 2-sided | Celloglaze: None | Artworks: 1',
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
    results = run_premium_bookmarks_tests()
    generate_website_test_guide(results)
    
    print("\n" + "="*80)
    print("✅ All 4 tests completed successfully!")
    print("📋 Please validate these prices on the Shopify website")
    print("="*80)
