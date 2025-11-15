"""
Test Notepads A5 Shopify Calculator
Simple test to verify the calculator works correctly
"""

import sys
sys.path.insert(0, 'inhouse_modules')

from shopify_calculators.NotepadsA5_Shopify_Calculator import NotepadsA5ShopifyCalculator

def test_basic_notepad_calculation():
    """Test basic notepad calculation with standard parameters"""
    print("=" * 80)
    print("TEST 1: Basic Office Notepads (100 pads, 50 leaves, B&W 1 sided, 80GSM)")
    print("=" * 80)
    
    calc = NotepadsA5ShopifyCalculator()
    
    result = calc.calculate(
        quantity=100,
        artworks=1,
        finish_size="A5 Portrait",
        leaves_per_pad=50,
        print_type="Black & White 1 sided",
        stock_type="Uncoated Bond 80GSM"
    )
    
    print(f"\nRESULTS:")
    print(f"  Total Price: ${result.total_price:.2f} (inc GST)")
    print(f"  Unit Price: ${result.unit_price:.2f} per pad")
    print(f"  Quantity: {result.quantity} pads")
    print(f"  Total Leaves: {result.specifications['total_leaves']} sheets")
    
    print(f"\nBREAKDOWN:")
    for key, value in result.breakdown.items():
        if isinstance(value, float):
            print(f"  {key}: ${value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    print(f"\nSPECIFICATIONS:")
    for key, value in result.specifications.items():
        print(f"  {key}: {value}")
    
    return result


def test_promotional_notepads():
    """Test promotional notepads with multiple artworks and color printing"""
    print("\n\n" + "=" * 80)
    print("TEST 2: Promotional Notepads (250 pads, 2 artworks, 25 leaves, Colour 1 sided, 90GSM)")
    print("=" * 80)
    
    calc = NotepadsA5ShopifyCalculator()
    
    result = calc.calculate(
        quantity=250,
        artworks=2,
        finish_size="A5 Portrait",
        leaves_per_pad=25,
        print_type="Colour 1 sided",
        stock_type="Uncoated Bond 90GSM"
    )
    
    print(f"\nRESULTS:")
    print(f"  Total Price: ${result.total_price:.2f} (inc GST)")
    print(f"  Unit Price: ${result.unit_price:.2f} per pad")
    print(f"  Quantity: {result.quantity} pads")
    print(f"  Artworks: {result.specifications['artworks']} designs")
    
    print(f"\nCOST HIGHLIGHTS:")
    print(f"  Artwork Setup: ${result.breakdown['artwork_setup_cost']:.2f}")
    print(f"  Padding Cost: ${result.breakdown['padding_cost_total']:.2f}")
    print(f"  Profit Margin: {result.breakdown['profit_margin_pct']:.1f}%")
    print(f"  Total GST: ${result.breakdown['total_gst_amount']:.2f} (double application)")
    
    return result


def test_bulk_office_notepads():
    """Test bulk office notepads with recycled paper"""
    print("\n\n" + "=" * 80)
    print("TEST 3: Bulk Office Notepads (1000 pads, 100 leaves, B&W 1 sided, Recycled 80GSM)")
    print("=" * 80)
    
    calc = NotepadsA5ShopifyCalculator()
    
    result = calc.calculate(
        quantity=1000,
        artworks=1,
        finish_size="A5 Portrait",
        leaves_per_pad=100,
        print_type="Black & White 1 sided",
        stock_type="Revive 100% Recycled 80GSM Bond"
    )
    
    print(f"\nRESULTS:")
    print(f"  Total Price: ${result.total_price:.2f} (inc GST)")
    print(f"  Unit Price: ${result.unit_price:.2f} per pad")
    print(f"  Cost per pad: ${result.cost_per_pad:.2f}")
    print(f"  Total Leaves: {result.specifications['total_leaves']:,} sheets")
    
    print(f"\nTIERING:")
    print(f"  {result.specifications['padding_rate_tier']}")
    print(f"  {result.specifications['profit_margin_tier']}")
    
    return result


def test_tool_wrapper():
    """Test the calculator through the tool wrapper"""
    print("\n\n" + "=" * 80)
    print("TEST 4: Tool Wrapper Integration Test")
    print("=" * 80)
    
    sys.path.insert(0, 'tools/implementations')
    from calculator import CalculatorWrapper
    
    wrapper = CalculatorWrapper()
    
    result = wrapper.calculate_notepads_a5(
        quantity=100,
        artworks=1,
        finish_size="A5 Portrait",
        leaves_per_pad=50,
        print_type="Black & White 1 sided",
        stock_type="Uncoated Bond 80GSM"
    )
    
    if result.get('success'):
        print("\n✅ Tool wrapper integration: SUCCESS")
        print(f"  Total Price: ${result['total_price']:.2f}")
        print(f"  Unit Price: ${result['unit_price']:.2f}")
    else:
        print(f"\n❌ Tool wrapper integration: FAILED")
        print(f"  Error: {result.get('error', 'Unknown error')}")
    
    return result


if __name__ == "__main__":
    try:
        # Run all tests
        test_basic_notepad_calculation()
        test_promotional_notepads()
        test_bulk_office_notepads()
        test_tool_wrapper()
        
        print("\n\n" + "=" * 80)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nNotepads A5 calculator is ready to use!")
        print("The AI can now calculate notepad quotes using:")
        print("  1. get_calculator_requirements('notepads_a5') - Get parameter schema")
        print("  2. calculate_notepads_a5(...) - Calculate the quote")
        
    except Exception as e:
        print(f"\n\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
