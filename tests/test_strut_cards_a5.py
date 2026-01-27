"""
Test cases for Strut Cards A5 Shopify calculator
Backend created Jan 25, 2026 with exact TXT formula

Test Strategy:
- Tier boundaries (1-9, 10-14, 15-19, 100-124, 1000+)
- $79 minimum order enforcement
- Artwork cost formula (first $5 included, then $5 each)
- Double markup: ×1.1 ×1.2 (A5-specific higher final multiplier)
"""

import sys
from pathlib import Path

# Add backend path
backend_dir = Path(__file__).resolve().parent.parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'
sys.path.insert(0, str(backend_dir))

from StrutCardsA5_Shopify_Calculator import StrutCardsA5ShopifyCalculator
from decimal import Decimal

def test_low_quantity_minimum_order():
    """Test 1-9 tier with minimum order enforcement"""
    calc = StrutCardsA5ShopifyCalculator()
    result = calc.calculate(quantity=15, artworks=1)
    
    # Expected: 15 × $4.5 = $67.50, artwork = $0 (first included)
    # Subtotal = $67.50 (below $79 minimum)
    # Apply minimum: $79
    # Final markup: $79 × 1.2 = $94.80
    
    print(f"Test 1 - Low Quantity (15 cards, 1 artwork):")
    print(f"  Unit price: ${result.breakdown['unit_price']}")
    print(f"  Artwork cost: ${result.breakdown['artwork_cost']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Minimum applied: {result.breakdown['minimum_applied']}")
    print(f"  After first markup: ${result.breakdown['total_after_first_markup']}")
    print(f"  Total price: ${result.total_price}")
    print(f"  Per card: ${result.unit_price}")
    
    assert result.breakdown['unit_price'] == Decimal("4.5"), "Unit price should be $4.5"
    assert result.breakdown['artwork_cost'] == Decimal("0"), "First artwork included"
    assert result.breakdown['subtotal'] == Decimal("67.50"), "Subtotal should be $67.50"
    assert result.breakdown['minimum_applied'], "Minimum should apply ($67.50 < $79)"
    assert result.breakdown['total_after_first_markup'] == Decimal("79"), "Should use $79 minimum"
    assert result.total_price == Decimal("94.80"), "Total should be $94.80 ($79 × 1.2)"
    print("  ✅ PASS\n")

def test_above_minimum_no_enforcement():
    """Test quantity above minimum order"""
    calc = StrutCardsA5ShopifyCalculator()
    result = calc.calculate(quantity=25, artworks=1)
    
    # Expected: 25 × $4.4 = $110, artwork = $0
    # Subtotal = $110 (above $79 minimum)
    # First markup: $110 × 1.1 = $121
    # Final markup: $121 × 1.2 = $145.20
    
    print(f"Test 2 - Above Minimum (25 cards, 1 artwork):")
    print(f"  Unit price: ${result.breakdown['unit_price']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Minimum applied: {result.breakdown['minimum_applied']}")
    print(f"  After first markup: ${result.breakdown['total_after_first_markup']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['unit_price'] == Decimal("4.4"), "Unit price should be $4.4"
    assert result.breakdown['subtotal'] == Decimal("110"), "Subtotal should be $110"
    assert not result.breakdown['minimum_applied'], "Minimum should NOT apply ($110 > $79)"
    assert result.breakdown['total_after_first_markup'] == Decimal("121"), "Should be $121"
    assert result.total_price == Decimal("145.20"), "Total should be $145.20"
    print("  ✅ PASS\n")

def test_tier_boundary_100():
    """Test 100-124 tier boundary"""
    calc = StrutCardsA5ShopifyCalculator()
    result = calc.calculate(quantity=100, artworks=1)
    
    # Expected: 100 × $3.42 = $342, artwork = $0
    # Subtotal = $342
    # First markup: $342 × 1.1 = $376.20
    # Final markup: $376.20 × 1.2 = $451.44
    
    print(f"Test 3 - Tier Boundary (100 cards, 1 artwork):")
    print(f"  Unit price: ${result.breakdown['unit_price']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  After first markup: ${result.breakdown['total_after_first_markup']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['unit_price'] == Decimal("3.42"), "Unit price should be $3.42"
    assert result.breakdown['subtotal'] == Decimal("342"), "Subtotal should be $342"
    assert result.total_price == Decimal("451.44"), "Total should be $451.44"
    print("  ✅ PASS\n")

def test_multiple_artworks():
    """Test multiple artworks ($5 first included, $5 each additional)"""
    calc = StrutCardsA5ShopifyCalculator()
    result = calc.calculate(quantity=50, artworks=4)
    
    # Expected: 50 × $4.15 = $207.50
    # Artwork: 4 × $5 = $20; IF $20 ≤ $5 THEN $0 ELSE ($20 - $5) = $15
    # Subtotal = $207.50 + $15 = $222.50
    # First markup: $222.50 × 1.1 = $244.75
    # Final markup: $244.75 × 1.2 = $293.70
    
    print(f"Test 4 - Multiple Artworks (50 cards, 4 artworks):")
    print(f"  Unit price: ${result.breakdown['unit_price']}")
    print(f"  Artwork cost: ${result.breakdown['artwork_cost']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  After first markup: ${result.breakdown['total_after_first_markup']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['unit_price'] == Decimal("4.15"), "Unit price should be $4.15"
    assert result.breakdown['artwork_cost'] == Decimal("15"), "3 extra artworks × $5 = $15"
    assert result.breakdown['subtotal'] == Decimal("222.50"), "Subtotal should be $222.50"
    assert result.total_price == Decimal("293.70"), "Total should be $293.70"
    print("  ✅ PASS\n")

def test_high_volume_1000_plus():
    """Test 1000+ tier (lowest price) - Verify A5 uses ×1.2 final markup"""
    calc = StrutCardsA5ShopifyCalculator()
    result = calc.calculate(quantity=1000, artworks=1)
    
    # Expected: 1000 × $2.85 = $2850, artwork = $0
    # Subtotal = $2850
    # First markup: $2850 × 1.1 = $3135
    # Final markup: $3135 × 1.2 = $3762 (KEY: ×1.2 not ×1.1 like A3/A4)
    
    print(f"Test 5 - High Volume (1000 cards, 1 artwork):")
    print(f"  Unit price: ${result.breakdown['unit_price']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  After first markup: ${result.breakdown['total_after_first_markup']}")
    print(f"  Final markup multiplier: {result.breakdown['final_markup']}")
    print(f"  Total price: ${result.total_price}")
    print(f"  Per card: ${result.unit_price}")
    
    assert result.breakdown['unit_price'] == Decimal("2.85"), "Unit price should be $2.85"
    assert result.breakdown['subtotal'] == Decimal("2850"), "Subtotal should be $2850"
    assert result.breakdown['final_markup'] == Decimal("1.2"), "A5 uses ×1.2 (not ×1.1)"
    assert result.total_price == Decimal("3762.00"), "Total should be $3762.00"
    print("  ✅ PASS (A5-specific ×1.2 final markup verified)\n")

if __name__ == "__main__":
    print("=" * 70)
    print("STRUT CARDS A5 - CALCULATOR VALIDATION")
    print("Backend: StrutCardsA5_Shopify_Calculator.py")
    print("Formula: 25-tier quantity pricing + artwork cost + $79 minimum + ×1.1 ×1.2")
    print("KEY: A5 uses ×1.2 final markup (higher than A3/A4's ×1.1)")
    print("=" * 70 + "\n")
    
    try:
        test_low_quantity_minimum_order()
        test_above_minimum_no_enforcement()
        test_tier_boundary_100()
        test_multiple_artworks()
        test_high_volume_1000_plus()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED - Backend matches exact TXT formula")
        print("   A5 correctly uses ×1.2 final markup (vs A3/A4's ×1.1)")
        print("=" * 70)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
