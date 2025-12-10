"""
Test Shopify Calculator Wrapper Integration
============================================

Tests the newly added wrapper functions to verify they work correctly.
"""

import sys
from pathlib import Path

# Ensure inhouse_modules is in the path
sys.path.insert(0, str(Path(__file__).parent / "inhouse_modules"))

# Now import wrappers
from shopify_calculator_wrappers import (
    calculate_printed_letterheads_shopify,
    calculate_election_signs_shopify,
    calculate_custom_poster_printing_shopify,
    calculate_strut_cards_a4_shopify,
    calculate_custom_vinyl_stickers_shopify
)

def test_stationery():
    """Test stationery calculator wrapper."""
    print("\n" + "="*70)
    print("TEST 1: Printed Letterheads")
    print("="*70)
    result = calculate_printed_letterheads_shopify(
        quantity=100,
        double_sided=False,
        colour=True,
        paper_stock="Standard",
        artworks=1
    )
    print(f"✓ Quantity: {result['quantity']}")
    print(f"✓ Total Price: ${result['total_price']:.2f}")
    print(f"✓ Unit Price: ${result['unit_price']:.4f}")
    print(f"✓ Cost Per Item: ${result['cost_per_item']:.4f}")
    print(f"✓ Breakdown keys: {', '.join(result['breakdown'].keys())}")
    assert result['total_price'] > 0, "Total price should be positive"
    print("✓ PASSED")

def test_signs():
    """Test signs calculator wrapper."""
    print("\n" + "="*70)
    print("TEST 2: Election Signs")
    print("="*70)
    result = calculate_election_signs_shopify(
        quantity=50,
        size="600x450",
        material="Corflute",
        double_sided=True,
        artworks=1
    )
    print(f"✓ Quantity: {result['quantity']}")
    print(f"✓ Total Price: ${result['total_price']:.2f}")
    print(f"✓ Unit Price: ${result['unit_price']:.4f}")
    print(f"✓ Material: {result['specifications'].get('material', 'N/A')}")
    assert result['total_price'] > 0, "Total price should be positive"
    print("✓ PASSED")

def test_promotional_posters():
    """Test promotional calculator wrapper."""
    print("\n" + "="*70)
    print("TEST 3: Custom Poster Printing")
    print("="*70)
    result = calculate_custom_poster_printing_shopify(
        quantity=25,
        width_mm=420,
        height_mm=594,
        paper_stock="150gsm"
    )
    print(f"✓ Quantity: {result['quantity']}")
    print(f"✓ Total Price: ${result['total_price']:.2f}")
    print(f"✓ Unit Price: ${result['unit_price']:.4f}")
    assert result['total_price'] > 0, "Total price should be positive"
    print("✓ PASSED")

def test_strut_cards():
    """Test strut cards wrapper."""
    print("\n" + "="*70)
    print("TEST 4: Strut Cards A4")
    print("="*70)
    result = calculate_strut_cards_a4_shopify(
        quantity=100,
        size="210x297",
        double_sided=False,
        artworks=1
    )
    print(f"✓ Quantity: {result['quantity']}")
    print(f"✓ Total Price: ${result['total_price']:.2f}")
    print(f"✓ Unit Price: ${result['unit_price']:.4f}")
    assert result['total_price'] > 0, "Total price should be positive"
    print("✓ PASSED")

def test_vinyl_stickers():
    """Test vinyl stickers wrapper."""
    print("\n" + "="*70)
    print("TEST 5: Custom Vinyl Stickers")
    print("="*70)
    result = calculate_custom_vinyl_stickers_shopify(
        quantity=500,
        width_mm=100,
        height_mm=100,
        finish="Gloss"
    )
    print(f"✓ Quantity: {result['quantity']}")
    print(f"✓ Total Price: ${result['total_price']:.2f}")
    print(f"✓ Unit Price: ${result['unit_price']:.4f}")
    assert result['total_price'] > 0, "Total price should be positive"
    print("✓ PASSED")

def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("SHOPIFY CALCULATOR WRAPPER INTEGRATION TESTS")
    print("="*70)
    
    tests = [
        ("Stationery", test_stationery),
        ("Signs", test_signs),
        ("Promotional (Posters)", test_promotional_posters),
        ("Strut Cards", test_strut_cards),
        ("Vinyl Stickers", test_vinyl_stickers),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n✗ FAILED: {name}")
            print(f"  Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✓ Passed: {passed}/{len(tests)}")
    print(f"✗ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Wrapper integration successful.")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed. Review errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
