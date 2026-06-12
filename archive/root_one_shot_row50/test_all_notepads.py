"""
Test All 3 Notepads Shopify Calculators
Tests A5, A6, and A4 with multiple scenarios
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add backend path
backend_path = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(backend_path / 'shopify_calculators'))

from NotepadsA5_Shopify_Calculator import NotepadsA5ShopifyCalculator
from NotepadsA6_Shopify_Calculator import NotepadsA6ShopifyCalculator
from NotepadsA4_Shopify_Calculator import NotepadsA4ShopifyCalculator


def format_currency(value):
    """Format Decimal as currency"""
    if isinstance(value, Decimal):
        return f"${value:.2f}"
    return f"${float(value):.2f}"


def print_test_result(calc_name, test_name, result):
    """Print formatted test result"""
    print(f"\n{'='*80}")
    print(f"CALCULATOR: {calc_name}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")
    
    specs = result.specifications
    breakdown = result.breakdown
    
    print(f"\n📋 INPUT PARAMETERS:")
    print(f"   Quantity: {specs['quantity']}")
    print(f"   Artworks: {specs['artworks']}")
    print(f"   Finish Size: {specs['finish_size']} (multiplier: {specs['finish_size_multiplier']})")
    print(f"   Leaves Per Pad: {specs['leaves_per_pad']}")
    print(f"   Print Type: {specs['print_type']} (${specs['print_type_price']}/sheet)")
    print(f"   Stock Type: {specs['stock_type']} (${specs['stock_type_price']}/sheet)")
    
    print(f"\n💰 COST BREAKDOWN:")
    print(f"   Setup Costs:")
    print(f"      Guillotine Setup: {format_currency(breakdown['guilo_setup'])}")
    print(f"      Imposition Setup: {format_currency(breakdown['impos_setup'])}")
    print(f"      Artwork Setup: {format_currency(breakdown['artwork_setup_cost'])}")
    print(f"      Total Setup: {format_currency(breakdown['total_setup_cost'])}")
    
    print(f"\n   Content Costs:")
    print(f"      Total Leave Sheets: {float(breakdown['total_leave_sheets']):.2f}")
    print(f"      Click Cost: {format_currency(breakdown['content_click_cost'])}")
    print(f"      Box Board Cost: {format_currency(breakdown['box_board_cost'])}")
    print(f"      Total Content: {format_currency(breakdown['total_content_cost'])}")
    
    print(f"\n   Other Costs:")
    print(f"      Cutting Cost: {format_currency(breakdown['cutting_cost'])}")
    print(f"      Padding Rate: ${float(breakdown['padding_rate']):.2f}/pad")
    print(f"      Padding Cost: {format_currency(breakdown['padding_cost'])}")
    
    print(f"\n   Subtotal & Margin:")
    print(f"      Subtotal: {format_currency(breakdown['subtotal'])}")
    print(f"      Profit Margin: {float(breakdown['profit_margin_rate'])*100:.1f}%")
    print(f"      Profit Amount: {format_currency(breakdown['profit_amount'])}")
    print(f"      With Margin: {format_currency(breakdown['subtotal_with_margin'])}")
    
    print(f"\n   Final Pricing:")
    print(f"      After 1st GST (10%): {format_currency(breakdown['after_first_gst'])}")
    print(f"      After 2nd GST (10%): {format_currency(breakdown['total_price'])}")
    print(f"      Cost Per Pad: {format_currency(result.cost_per_item)}")
    
    print(f"\n🎯 FINAL TOTAL: {format_currency(result.total_price)}")
    print(f"{'='*80}\n")


def run_notepads_a5_tests():
    """Test Notepads A5 calculator"""
    calc = NotepadsA5ShopifyCalculator()
    
    # Test 1: Baseline
    result1 = calc.calculate(
        quantity=100,
        artworks=1,
        finish_size='A5 Portrait',
        leaves_per_pad=50,
        print_type='Black & White 1 sided',
        stock_type='Uncoated Bond 80GSM'
    )
    print_test_result('NOTEPADS A5', 'Test 1: Baseline (100 qty, 50 leaves, B&W, 80GSM)', result1)
    
    # Test 2: High Volume
    result2 = calc.calculate(
        quantity=2000,
        artworks=2,
        finish_size='A5 Portrait',
        leaves_per_pad=100,
        print_type='Colour 2 sided',
        stock_type='Uncoated Bond 100GSM'
    )
    print_test_result('NOTEPADS A5', 'Test 2: High Volume (2000 qty, 100 leaves, Colour 2-sided, 100GSM)', result2)
    
    # Test 3: Premium
    result3 = calc.calculate(
        quantity=500,
        artworks=3,
        finish_size='A5 Portrait',
        leaves_per_pad=25,
        print_type='Colour 1 sided',
        stock_type='Revive Recycled Uncoated'
    )
    print_test_result('NOTEPADS A5', 'Test 3: Premium (500 qty, 25 leaves, Colour 1-sided, Recycled)', result3)
    
    # Test 4: Edge Case
    result4 = calc.calculate(
        quantity=50,
        artworks=1,
        finish_size='A5 Portrait',
        leaves_per_pad=25,
        print_type='Black & White 2 sided',
        stock_type='Uncoated Bond 90GSM'
    )
    print_test_result('NOTEPADS A5', 'Test 4: Edge Case (50 qty, 25 leaves, B&W 2-sided, 90GSM)', result4)
    
    return [result1, result2, result3, result4]


def run_notepads_a6_tests():
    """Test Notepads A6 calculator"""
    calc = NotepadsA6ShopifyCalculator()
    
    # Test 1: Baseline
    result1 = calc.calculate(
        quantity=100,
        artworks=1,
        finish_size='A6 Portrait',
        leaves_per_pad=50,
        print_type='Black & White 1 sided',
        stock_type='Uncoated Bond 80GSM'
    )
    print_test_result('NOTEPADS A6', 'Test 1: Baseline (100 qty, 50 leaves, B&W, 80GSM)', result1)
    
    # Test 2: High Volume
    result2 = calc.calculate(
        quantity=2000,
        artworks=2,
        finish_size='A6 Portrait',
        leaves_per_pad=100,
        print_type='Colour 2 sided',
        stock_type='Uncoated Bond 100GSM'
    )
    print_test_result('NOTEPADS A6', 'Test 2: High Volume (2000 qty, 100 leaves, Colour 2-sided, 100GSM)', result2)
    
    # Test 3: Small Format (A6-specific: 10 leaves option)
    result3 = calc.calculate(
        quantity=500,
        artworks=3,
        finish_size='A6 Portrait',
        leaves_per_pad=10,
        print_type='Colour 1 sided',
        stock_type='Revive Recycled Uncoated'
    )
    print_test_result('NOTEPADS A6', 'Test 3: Small Format (500 qty, 10 leaves, Colour 1-sided, Recycled)', result3)
    
    # Test 4: Edge Case (15 leaves - A6 only option)
    result4 = calc.calculate(
        quantity=50,
        artworks=1,
        finish_size='A6 Portrait',
        leaves_per_pad=15,
        print_type='Black & White 2 sided',
        stock_type='Uncoated Bond 90GSM'
    )
    print_test_result('NOTEPADS A6', 'Test 4: Edge Case (50 qty, 15 leaves, B&W 2-sided, 90GSM)', result4)
    
    return [result1, result2, result3, result4]


def run_notepads_a4_tests():
    """Test Notepads A4 calculator"""
    calc = NotepadsA4ShopifyCalculator()
    
    # Test 1: Baseline
    result1 = calc.calculate(
        quantity=100,
        artworks=1,
        finish_size='A4 Portrait',
        leaves_per_pad=50,
        print_type='Black & White 1 sided',
        stock_type='Uncoated Bond 80GSM'
    )
    print_test_result('NOTEPADS A4', 'Test 1: Baseline (100 qty, 50 leaves, B&W, 80GSM)', result1)
    
    # Test 2: High Volume with 100 leaves (A4 max option)
    result2 = calc.calculate(
        quantity=2000,
        artworks=2,
        finish_size='A4 Portrait',
        leaves_per_pad=100,
        print_type='Colour 2 sided',
        stock_type='Uncoated Bond 100GSM'
    )
    print_test_result('NOTEPADS A4', 'Test 2: High Volume (2000 qty, 100 leaves, Colour 2-sided, 100GSM)', result2)
    
    # Test 3: Premium
    result3 = calc.calculate(
        quantity=500,
        artworks=3,
        finish_size='A4 Portrait',
        leaves_per_pad=25,
        print_type='Colour 1 sided',
        stock_type='Revive Recycled Uncoated'
    )
    print_test_result('NOTEPADS A4', 'Test 3: Premium (500 qty, 25 leaves, Colour 1-sided, Recycled)', result3)
    
    # Test 4: Edge Case
    result4 = calc.calculate(
        quantity=50,
        artworks=1,
        finish_size='A4 Portrait',
        leaves_per_pad=25,
        print_type='Black & White 2 sided',
        stock_type='Uncoated Bond 90GSM'
    )
    print_test_result('NOTEPADS A4', 'Test 4: Edge Case (50 qty, 25 leaves, B&W 2-sided, 90GSM)', result4)
    
    return [result1, result2, result3, result4]


def generate_website_test_guide(a5_results, a6_results, a4_results):
    """Generate guide for website validation"""
    print("\n" + "="*80)
    print("WEBSITE VALIDATION TEST GUIDE")
    print("="*80)
    print("\nGo to the Shopify website and test each configuration below.")
    print("Compare the website's total price with the backend result.\n")
    
    # A5 Tests
    print("\n" + "─"*80)
    print("📄 NOTEPADS A5 WEBSITE TESTS")
    print("─"*80)
    
    tests_a5 = [
        ("Test 1: Baseline", a5_results[0], {
            'quantity': 100, 'artworks': 1, 'finish': 'A5 Portrait',
            'leaves': 50, 'print': 'Black & White 1 sided', 'stock': 'Uncoated Bond 80GSM'
        }),
        ("Test 2: High Volume", a5_results[1], {
            'quantity': 2000, 'artworks': 2, 'finish': 'A5 Portrait',
            'leaves': 100, 'print': 'Colour 2 sided', 'stock': 'Uncoated Bond 100GSM'
        }),
        ("Test 3: Premium", a5_results[2], {
            'quantity': 500, 'artworks': 3, 'finish': 'A5 Portrait',
            'leaves': 25, 'print': 'Colour 1 sided', 'stock': 'Revive Recycled Uncoated'
        }),
        ("Test 4: Edge Case", a5_results[3], {
            'quantity': 50, 'artworks': 1, 'finish': 'A5 Portrait',
            'leaves': 25, 'print': 'Black & White 2 sided', 'stock': 'Uncoated Bond 90GSM'
        })
    ]
    
    for test_name, result, params in tests_a5:
        print(f"\n{test_name}:")
        print(f"  Quantity: {params['quantity']}")
        print(f"  Artworks: {params['artworks']}")
        print(f"  Finish Size: {params['finish']}")
        print(f"  Leaves Per Pad: {params['leaves']}")
        print(f"  Print Type: {params['print']}")
        print(f"  Stock Type: {params['stock']}")
        print(f"  ➜ EXPECTED TOTAL: {format_currency(result.total_price)}")
        print(f"  ➜ Website Result: ___________ (fill in after testing)")
        print(f"  ➜ Match? ☐ YES  ☐ NO  (Difference: $________)")
    
    # A6 Tests
    print("\n" + "─"*80)
    print("📄 NOTEPADS A6 WEBSITE TESTS")
    print("─"*80)
    
    tests_a6 = [
        ("Test 1: Baseline", a6_results[0], {
            'quantity': 100, 'artworks': 1, 'finish': 'A6 Portrait',
            'leaves': 50, 'print': 'Black & White 1 sided', 'stock': 'Uncoated Bond 80GSM'
        }),
        ("Test 2: High Volume", a6_results[1], {
            'quantity': 2000, 'artworks': 2, 'finish': 'A6 Portrait',
            'leaves': 100, 'print': 'Colour 2 sided', 'stock': 'Uncoated Bond 100GSM'
        }),
        ("Test 3: Small Format (10 leaves)", a6_results[2], {
            'quantity': 500, 'artworks': 3, 'finish': 'A6 Portrait',
            'leaves': 10, 'print': 'Colour 1 sided', 'stock': 'Revive Recycled Uncoated'
        }),
        ("Test 4: Edge Case (15 leaves)", a6_results[3], {
            'quantity': 50, 'artworks': 1, 'finish': 'A6 Portrait',
            'leaves': 15, 'print': 'Black & White 2 sided', 'stock': 'Uncoated Bond 90GSM'
        })
    ]
    
    for test_name, result, params in tests_a6:
        print(f"\n{test_name}:")
        print(f"  Quantity: {params['quantity']}")
        print(f"  Artworks: {params['artworks']}")
        print(f"  Finish Size: {params['finish']}")
        print(f"  Leaves Per Pad: {params['leaves']}")
        print(f"  Print Type: {params['print']}")
        print(f"  Stock Type: {params['stock']}")
        print(f"  ➜ EXPECTED TOTAL: {format_currency(result.total_price)}")
        print(f"  ➜ Website Result: ___________ (fill in after testing)")
        print(f"  ➜ Match? ☐ YES  ☐ NO  (Difference: $________)")
    
    # A4 Tests
    print("\n" + "─"*80)
    print("📄 NOTEPADS A4 WEBSITE TESTS")
    print("─"*80)
    
    tests_a4 = [
        ("Test 1: Baseline", a4_results[0], {
            'quantity': 100, 'artworks': 1, 'finish': 'A4 Portrait',
            'leaves': 50, 'print': 'Black & White 1 sided', 'stock': 'Uncoated Bond 80GSM'
        }),
        ("Test 2: High Volume", a4_results[1], {
            'quantity': 2000, 'artworks': 2, 'finish': 'A4 Portrait',
            'leaves': 100, 'print': 'Colour 2 sided', 'stock': 'Uncoated Bond 100GSM'
        }),
        ("Test 3: Premium", a4_results[2], {
            'quantity': 500, 'artworks': 3, 'finish': 'A4 Portrait',
            'leaves': 25, 'print': 'Colour 1 sided', 'stock': 'Revive Recycled Uncoated'
        }),
        ("Test 4: Edge Case", a4_results[3], {
            'quantity': 50, 'artworks': 1, 'finish': 'A4 Portrait',
            'leaves': 25, 'print': 'Black & White 2 sided', 'stock': 'Uncoated Bond 90GSM'
        })
    ]
    
    for test_name, result, params in tests_a4:
        print(f"\n{test_name}:")
        print(f"  Quantity: {params['quantity']}")
        print(f"  Artworks: {params['artworks']}")
        print(f"  Finish Size: {params['finish']}")
        print(f"  Leaves Per Pad: {params['leaves']}")
        print(f"  Print Type: {params['print']}")
        print(f"  Stock Type: {params['stock']}")
        print(f"  ➜ EXPECTED TOTAL: {format_currency(result.total_price)}")
        print(f"  ➜ Website Result: ___________ (fill in after testing)")
        print(f"  ➜ Match? ☐ YES  ☐ NO  (Difference: $________)")
    
    print("\n" + "="*80)
    print("TOTAL TESTS: 12 (4 per calculator)")
    print("="*80 + "\n")


if __name__ == '__main__':
    print("\n🧪 TESTING ALL 3 NOTEPADS SHOPIFY CALCULATORS\n")
    
    try:
        # Run all tests
        print("Testing Notepads A5...")
        a5_results = run_notepads_a5_tests()
        
        print("\nTesting Notepads A6...")
        a6_results = run_notepads_a6_tests()
        
        print("\nTesting Notepads A4...")
        a4_results = run_notepads_a4_tests()
        
        # Generate website validation guide
        generate_website_test_guide(a5_results, a6_results, a4_results)
        
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
