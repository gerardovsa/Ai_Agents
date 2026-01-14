"""
Test Flexible Quantity Handling for Shopify Calculators
Tests the new _round_to_pricing_tier() method and flexible validation
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from EconomicalBusinessCards_Shopify_Calculator import EconomicalBusinessCardsShopifyCalculator
from PremiumBusinessCards_Shopify_Calculator import PremiumBusinessCardsShopifyCalculator


def test_tier_rounding():
    """Test the tier rounding logic"""
    print("=" * 80)
    print("TEST 1: Tier Rounding Logic")
    print("=" * 80)
    
    calc = EconomicalBusinessCardsShopifyCalculator()
    
    test_cases = [
        (100, 250, "Below minimum"),
        (176, 250, "Between minimum and next tier"),
        (250, 250, "Exact tier match"),
        (375, 250, "Between 250-500 tiers"),
        (500, 500, "Exact tier match"),
        (847, 500, "Between 500-1000 tiers"),
        (1000, 1000, "Exact tier match"),
        (1500, 1000, "Between 1000-2000 tiers"),
        (2000, 2000, "Exact tier match"),
        (3500, 2000, "Between 2000-5000 tiers"),
        (5000, 5000, "Exact tier match"),
        (7500, 5000, "Between 5000-10000 tiers"),
        (10000, 10000, "Exact tier match"),
        (15000, 10000, "Above maximum"),
    ]
    
    passed = 0
    failed = 0
    
    for input_qty, expected_tier, description in test_cases:
        result_tier = calc._round_to_pricing_tier(input_qty)
        status = "✓ PASS" if result_tier == expected_tier else "✗ FAIL"
        
        if result_tier == expected_tier:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | Input: {input_qty:>5} → Expected: {expected_tier:>5} | Got: {result_tier:>5} | {description}")
    
    print(f"\nResults: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    return failed == 0


def test_economical_business_cards():
    """Test Economical Business Cards calculator with flexible quantities"""
    print("\n" + "=" * 80)
    print("TEST 2: Economical Business Cards - Flexible Quantities")
    print("=" * 80)
    
    calc = EconomicalBusinessCardsShopifyCalculator()
    
    test_cases = [
        (176, "Single side print", "Colour"),
        (375, "Double side print", "Colour"),
        (847, "Single side print", "Black & White"),
        (15000, "Single side print", "Colour"),
    ]
    
    for quantity, print_sides, print_type in test_cases:
        try:
            result = calc.calculate(
                quantity=quantity,
                print_sides=print_sides,
                print_type=print_type,
                finish_size="90mm x 55mm",
                paper_stock="Satin 300GSM",
                artworks=1
            )
            
            print(f"\n✓ SUCCESS: Quantity {quantity}")
            print(f"  - Pricing tier used: {result.quantity}")
            print(f"  - Original quantity: {result.specifications.get('original_quantity')}")
            print(f"  - Quantity adjusted: {result.specifications.get('quantity_adjusted')}")
            print(f"  - Total price: ${result.total_price:.2f}")
            print(f"  - Unit price: ${result.unit_price:.4f}")
            print(f"  - Per card: ${result.cost_per_card:.4f}")
            print(f"  - Specifications: {result.specifications.get('print_sides')}, {result.specifications.get('print_type')}")
            
        except Exception as e:
            print(f"\n✗ FAILED: Quantity {quantity}")
            print(f"  Error: {str(e)}")
            return False
    
    return True


def test_premium_business_cards():
    """Test Premium Business Cards calculator with flexible quantities"""
    print("\n" + "=" * 80)
    print("TEST 3: Premium Business Cards - Flexible Quantities")
    print("=" * 80)
    
    calc = PremiumBusinessCardsShopifyCalculator()
    
    test_cases = [
        (176, "Single side print", "Colour", "1 Side Gloss"),
        (375, "Double side print", "Colour", "2 Side Matt"),
        (847, "Single side print", "Black & White", "None"),
        (15000, "Single side print", "Colour", "1 Side SILK FEEL Matt"),
    ]
    
    for quantity, print_sides, print_type, celloglaze in test_cases:
        try:
            result = calc.calculate(
                quantity=quantity,
                print_sides=print_sides,
                print_type=print_type,
                finish_size="90mm x 55mm",
                paper_stock="Satin 350GSM",
                artworks=1,
                celloglaze=celloglaze
            )
            
            print(f"\n✓ SUCCESS: Quantity {quantity}")
            print(f"  - Pricing tier used: {result.quantity}")
            print(f"  - Original quantity: {result.specifications.get('original_quantity')}")
            print(f"  - Quantity adjusted: {result.specifications.get('quantity_adjusted')}")
            print(f"  - Total price: ${result.total_price:.2f}")
            print(f"  - Unit price: ${result.unit_price:.4f}")
            print(f"  - Per card: ${result.cost_per_card:.4f}")
            print(f"  - Celloglaze: {result.specifications.get('celloglaze')}")
            
        except Exception as e:
            print(f"\n✗ FAILED: Quantity {quantity}")
            print(f"  Error: {str(e)}")
            return False
    
    return True


def test_error_handling():
    """Test error handling for invalid inputs"""
    print("\n" + "=" * 80)
    print("TEST 4: Error Handling")
    print("=" * 80)
    
    calc = EconomicalBusinessCardsShopifyCalculator()
    
    # Test negative quantity
    try:
        calc._round_to_pricing_tier(-100)
        print("✗ FAIL: Should reject negative quantity")
        return False
    except ValueError as e:
        print(f"✓ PASS: Correctly rejected negative quantity: {str(e)}")
    
    # Test zero quantity
    try:
        calc._round_to_pricing_tier(0)
        print("✗ FAIL: Should reject zero quantity")
        return False
    except ValueError as e:
        print(f"✓ PASS: Correctly rejected zero quantity: {str(e)}")
    
    return True


def test_customer_friendly_pricing():
    """Verify that rounding DOWN gives better pricing for customers"""
    print("\n" + "=" * 80)
    print("TEST 5: Customer-Friendly Pricing (Round Down)")
    print("=" * 80)
    
    calc = EconomicalBusinessCardsShopifyCalculator()
    
    # Test: 375 cards should use 250-tier pricing (cheaper than 500-tier)
    result_375 = calc.calculate(
        quantity=375,
        print_sides="Single side print",
        print_type="Colour",
        finish_size="90mm x 55mm",
        paper_stock="Satin 300GSM",
        artworks=1
    )
    
    result_250 = calc.calculate(
        quantity=250,
        print_sides="Single side print",
        print_type="Colour",
        finish_size="90mm x 55mm",
        paper_stock="Satin 300GSM",
        artworks=1
    )
    
    result_500 = calc.calculate(
        quantity=500,
        print_sides="Single side print",
        print_type="Colour",
        finish_size="90mm x 55mm",
        paper_stock="Satin 300GSM",
        artworks=1
    )
    
    print(f"\nPricing Comparison:")
    print(f"  250 cards:  ${result_250.total_price:.2f} (${result_250.unit_price:.4f}/unit)")
    print(f"  375 cards:  ${result_375.total_price:.2f} (${result_375.unit_price:.4f}/unit) ← Uses 250-tier")
    print(f"  500 cards:  ${result_500.total_price:.2f} (${result_500.unit_price:.4f}/unit)")
    
    if result_375.unit_price == result_250.unit_price:
        print(f"\n✓ PASS: 375 cards correctly uses 250-tier pricing (customer saves money)")
        return True
    else:
        print(f"\n✗ FAIL: 375 cards should use 250-tier pricing")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("SHOPIFY CALCULATOR - FLEXIBLE QUANTITY TESTING")
    print("=" * 80)
    
    all_passed = True
    
    all_passed &= test_tier_rounding()
    all_passed &= test_economical_business_cards()
    all_passed &= test_premium_business_cards()
    all_passed &= test_error_handling()
    all_passed &= test_customer_friendly_pricing()
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 80 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
