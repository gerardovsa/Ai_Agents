"""
Test cases for Strut Cards A3 Shopify calculator
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

from StrutCardsA3_Shopify_Calculator import StrutCardsA3ShopifyCalculator
from decimal import Decimal

def test_low_quantity_minimum_order():
    """Test 1-9 tier with minimum order enforcement"""
    calc = StrutCardsA3ShopifyCalculator()
    result = calc.calculate(quantity=5, artworks=1)
    
    # Expected: 5 × $16 = $80, artwork = $0 (first included)
    # Subtotal = $80 (above $79 minimum)
    # First markup: $80 × 1.1 = $88
    # Final markup: $88 × 1.1 = $96.80
    
    print(f"Test 1 - Low Quantity (5 cards, 1 artwork):")
    print(f"  Unit price: ${result.breakdown['unit_price']}")
    print(f"  Artwork cost: ${result.breakdown['artwork_cost']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Minimum applied: {result.breakdown['minimum_applied']}")
    print(f"  After first markup: ${result.breakdown['total_after_first_markup']}")
    print(f"  Total price: ${result.total_price}")
    print(f"  Per card: ${result.unit_price}")
    
    assert result.breakdown['unit_price'] == Decimal("16"), "Unit price should be $16"
    assert result.breakdown['artwork_cost'] == Decimal("0"), "First artwork included"
    assert result.breakdown['subtotal'] == Decimal("80"), "Subtotal should be $80"
    assert not result.breakdown['minimum_applied'], "Minimum should NOT apply ($80 > $79)"
    assert result.total_price == Decimal("96.80"), "Total should be $96.80"
    print("  ✅ PASS\n")

def test_minimum_order_enforcement():
    """Test minimum order $79 enforcement"""
    calc = StrutCardsA3ShopifyCalculator()
    result = calc.calculate(quantity=2, artworks=1)
    
    # Expected: 2 × $16 = $32, artwork = $0
    # Subtotal = $32 (below $79 minimum)
    # Apply minimum: $79
    # Final markup: $79 × 1.1 = $86.90
    
    print(f"Test 2 - Minimum Order (2 cards, 1 artwork):")
    print(f"  Unit price: ${result.breakdown['unit_price']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Minimum applied: {result.breakdown['minimum_applied']}")
    print(f"  After first markup: ${result.breakdown['total_after_first_markup']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['subtotal'] == Decimal("32"), "Subtotal should be $32"
    assert result.breakdown['minimum_applied'], "Minimum should apply ($32 < $79)"
    assert result.breakdown['total_after_first_markup'] == Decimal("79"), "Should use $79 minimum"
    assert result.total_price == Decimal("86.90"), "Total should be $86.90 ($79 × 1.1)"
    print("  ✅ PASS\n")

def test_tier_boundary_100():
    """Test 100-124 tier boundary"""
    calc = StrutCardsA3ShopifyCalculator()
    result = calc.calculate(quantity=100, artworks=1)
    
    # Expected: 100 × $7.70 = $770, artwork = $0
    # Subtotal = $770
    # First markup: $770 × 1.1 = $847
    # Final markup: $847 × 1.1 = $931.70
    
    print(f"Test 3 - Tier Boundary (100 cards, 1 artwork):")
    print(f"  Unit price: ${result.breakdown['unit_price']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  After first markup: ${result.breakdown['total_after_first_markup']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['unit_price'] == Decimal("7.7"), "Unit price should be $7.70"
    assert result.breakdown['subtotal'] == Decimal("770"), "Subtotal should be $770"
    assert result.total_price == Decimal("931.70"), "Total should be $931.70"
    print("  ✅ PASS\n")

def test_multiple_artworks():
    """Test multiple artworks ($5 first included, $5 each additional)"""
    calc = StrutCardsA3ShopifyCalculator()
    result = calc.calculate(quantity=50, artworks=5)
    
    # Expected: 50 × $10.6 = $530
    # Artwork: 5 × $5 = $25; IF $25 ≤ $5 THEN $0 ELSE ($25 - $5) = $20
    # Subtotal = $530 + $20 = $550
    # First markup: $550 × 1.1 = $605
    # Final markup: $605 × 1.1 = $665.50
    
    print(f"Test 4 - Multiple Artworks (50 cards, 5 artworks):")
    print(f"  Unit price: ${result.breakdown['unit_price']}")
    print(f"  Artwork cost: ${result.breakdown['artwork_cost']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  After first markup: ${result.breakdown['total_after_first_markup']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['unit_price'] == Decimal("10.6"), "Unit price should be $10.6"
    assert result.breakdown['artwork_cost'] == Decimal("20"), "4 extra artworks × $5 = $20"
    assert result.breakdown['subtotal'] == Decimal("550"), "Subtotal should be $550"
    assert result.total_price == Decimal("665.50"), "Total should be $665.50"
    print("  ✅ PASS\n")

def test_high_volume_1000_plus():
    """Test 1000+ tier (lowest price)"""
    calc = StrutCardsA3ShopifyCalculator()
    result = calc.calculate(quantity=1000, artworks=1)
    
    # Expected: 1000 × $5.42 = $5420, artwork = $0
    # Subtotal = $5420
    # First markup: $5420 × 1.1 = $5962
    # Final markup: $5962 × 1.1 = $6558.20
    
    print(f"Test 5 - High Volume (1000 cards, 1 artwork):")
    print(f"  Unit price: ${result.breakdown['unit_price']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  After first markup: ${result.breakdown['total_after_first_markup']}")
    print(f"  Total price: ${result.total_price}")
    print(f"  Per card: ${result.unit_price}")
    
    assert result.breakdown['unit_price'] == Decimal("5.42"), "Unit price should be $5.42"
    assert result.breakdown['subtotal'] == Decimal("5420"), "Subtotal should be $5420"
    assert result.total_price == Decimal("6558.20"), "Total should be $6558.20"
    print("  ✅ PASS\n")

if __name__ == "__main__":
    print("=" * 70)
    print("STRUT CARDS A3 - CALCULATOR VALIDATION")
    print("Backend: StrutCardsA3_Shopify_Calculator.py")
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
