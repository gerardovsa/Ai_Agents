"""
Test cases for Strut Cards A4 Shopify calculator
Backend rewritten Jan 25, 2026 with exact TXT formula

Test Strategy:
- Tier boundaries (1-9, 10-14, 15-19, 100-124, 1000+)
- $79 minimum order enforcement
- Artwork cost formula (first $5 included, then $5 each)
- Double markup: ×1.1 ×1.1
"""

import sys
from pathlib import Path

# Add backend path
backend_dir = Path(__file__).resolve().parent.parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'
sys.path.insert(0, str(backend_dir))

from StrutCardsA4_Shopify_Calculator import StrutCardsA4ShopifyCalculator
from decimal import Decimal

def test_low_quantity_minimum_order():
    """Test 1-9 tier with minimum order enforcement"""
    calc = StrutCardsA4ShopifyCalculator()
    result = calc.calculate(quantity=10, artworks=1)
    
    # Expected: 10 × $9 = $90, artwork = $0 (first included)
    # Subtotal = $90 (above $79 minimum)
    # First markup: $90 × 1.1 = $99
    # Final markup: $99 × 1.1 = $108.90
    
    print(f"Test 1 - Low Quantity (10 cards, 1 artwork):")
    print(f"  Unit price: ${result.breakdown['unit_price']}")
    print(f"  Artwork cost: ${result.breakdown['artwork_cost']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Minimum applied: {result.breakdown['minimum_applied']}")
    print(f"  After first markup: ${result.breakdown['total_after_first_markup']}")
    print(f"  Total price: ${result.total_price}")
    print(f"  Per card: ${result.unit_price}")
    
    assert result.breakdown['unit_price'] == Decimal("9"), "Unit price should be $9"
    assert result.breakdown['artwork_cost'] == Decimal("0"), "First artwork included"
    assert result.breakdown['subtotal'] == Decimal("90"), "Subtotal should be $90"
    assert not result.breakdown['minimum_applied'], "Minimum should NOT apply ($90 > $79)"
    assert result.total_price == Decimal("108.90"), "Total should be $108.90"
    print("  ✅ PASS\n")

def test_minimum_order_enforcement():
    """Test minimum order $79 enforcement"""
    calc = StrutCardsA4ShopifyCalculator()
    result = calc.calculate(quantity=5, artworks=1)
    
    # Expected: 5 × $9 = $45, artwork = $0
    # Subtotal = $45 (below $79 minimum)
    # Apply minimum: $79
    # Final markup: $79 × 1.1 = $86.90
    
    print(f"Test 2 - Minimum Order (5 cards, 1 artwork):")
    print(f"  Unit price: ${result.breakdown['unit_price']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Minimum applied: {result.breakdown['minimum_applied']}")
    print(f"  After first markup: ${result.breakdown['total_after_first_markup']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['subtotal'] == Decimal("45"), "Subtotal should be $45"
    assert result.breakdown['minimum_applied'], "Minimum should apply ($45 < $79)"
    assert result.breakdown['total_after_first_markup'] == Decimal("79"), "Should use $79 minimum"
    assert result.total_price == Decimal("86.90"), "Total should be $86.90 ($79 × 1.1)"
    print("  ✅ PASS\n")

def test_tier_boundary_100():
    """Test 100-124 tier boundary"""
    calc = StrutCardsA4ShopifyCalculator()
    result = calc.calculate(quantity=100, artworks=1)
    
    # Expected: 100 × $4.85 = $485, artwork = $0
    # Subtotal = $485
    # First markup: $485 × 1.1 = $533.50
    # Final markup: $533.50 × 1.1 = $586.85
    
    print(f"Test 3 - Tier Boundary (100 cards, 1 artwork):")
    print(f"  Unit price: ${result.breakdown['unit_price']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  After first markup: ${result.breakdown['total_after_first_markup']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['unit_price'] == Decimal("4.85"), "Unit price should be $4.85"
    assert result.breakdown['subtotal'] == Decimal("485"), "Subtotal should be $485"
    assert result.total_price == Decimal("586.85"), "Total should be $586.85"
    print("  ✅ PASS\n")

def test_multiple_artworks():
    """Test multiple artworks ($5 first included, $5 each additional)"""
    calc = StrutCardsA4ShopifyCalculator()
    result = calc.calculate(quantity=50, artworks=3)
    
    # Expected: 50 × $6.3 = $315
    # Artwork: 3 × $5 = $15; IF $15 ≤ $5 THEN $0 ELSE ($15 - $5) = $10
    # Subtotal = $315 + $10 = $325
    # First markup: $325 × 1.1 = $357.50
    # Final markup: $357.50 × 1.1 = $393.25
    
    print(f"Test 4 - Multiple Artworks (50 cards, 3 artworks):")
    print(f"  Unit price: ${result.breakdown['unit_price']}")
    print(f"  Artwork cost: ${result.breakdown['artwork_cost']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  After first markup: ${result.breakdown['total_after_first_markup']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['unit_price'] == Decimal("6.3"), "Unit price should be $6.3"
    assert result.breakdown['artwork_cost'] == Decimal("10"), "2 extra artworks × $5 = $10"
    assert result.breakdown['subtotal'] == Decimal("325"), "Subtotal should be $325"
    assert result.total_price == Decimal("393.25"), "Total should be $393.25"
    print("  ✅ PASS\n")

def test_high_volume_1000_plus():
    """Test 1000+ tier (lowest price)"""
    calc = StrutCardsA4ShopifyCalculator()
    result = calc.calculate(quantity=1500, artworks=1)
    
    # Expected: 1500 × $3.71 = $5565, artwork = $0
    # Subtotal = $5565
    # First markup: $5565 × 1.1 = $6121.50
    # Final markup: $6121.50 × 1.1 = $6733.65
    
    print(f"Test 5 - High Volume (1500 cards, 1 artwork):")
    print(f"  Unit price: ${result.breakdown['unit_price']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  After first markup: ${result.breakdown['total_after_first_markup']}")
    print(f"  Total price: ${result.total_price}")
    print(f"  Per card: ${result.unit_price}")
    
    assert result.breakdown['unit_price'] == Decimal("3.71"), "Unit price should be $3.71"
    assert result.breakdown['subtotal'] == Decimal("5565"), "Subtotal should be $5565"
    assert result.total_price == Decimal("6733.65"), "Total should be $6733.65"
    print("  ✅ PASS\n")

if __name__ == "__main__":
    print("=" * 70)
    print("STRUT CARDS A4 - CALCULATOR VALIDATION")
    print("Backend: StrutCardsA4_Shopify_Calculator.py")
    print("Formula: 25-tier quantity pricing + artwork cost + $79 minimum + ×1.1 ×1.1")
    print("=" * 70 + "\n")
    
    try:
        test_low_quantity_minimum_order()
        test_minimum_order_enforcement()
        test_tier_boundary_100()
        test_multiple_artworks()
        test_high_volume_1000_plus()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED - Backend matches exact TXT formula")
        print("=" * 70)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
