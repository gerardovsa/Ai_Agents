"""
Test cases for Metal Face A-Frame Shopify calculator
Backend created Jan 25, 2026 with exact TXT formula

Test Strategy:
- 10 quantity tiers (1, 2, 3, 5, 6, 8, 10, 11+)
- Artwork count (unusual: adds count directly, not cost calculation)
- Double GST (×1.1 ×1.1)
- Unusual price increase at qty 6 ($170.31 vs $165.80 at qty 5)
"""

import sys
from pathlib import Path

# Add backend path
backend_dir = Path(__file__).resolve().parent.parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'
sys.path.insert(0, str(backend_dir))

from MetalFaceAFrame_Shopify_Calculator import MetalFaceAFrameShopifyCalculator
from decimal import Decimal

def test_single_unit():
    """Test 1 A-frame - highest per-unit price"""
    calc = MetalFaceAFrameShopifyCalculator()
    result = calc.calculate(quantity=1, artworks=1)
    
    # Expected: rate $197
    # Subtotal: 1 × $197 = $197
    # Pre-markup: $197 + 1 (artworks) = $198
    # First markup: $198 × 1.1 = $217.80
    # Final: $217.80 × 1.1 = $239.58
    
    print(f"Test 1 - Single A-Frame (1 unit, 1 artwork):")
    print(f"  Rate: ${result.breakdown['rate']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Artworks added: ${result.breakdown['artworks_added']}")
    print(f"  Pre-markup total: ${result.breakdown['pre_markup_total']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['rate'] == Decimal("197"), "Rate should be $197"
    assert result.breakdown['subtotal'] == Decimal("197"), "Subtotal should be $197"
    assert result.breakdown['artworks_added'] == Decimal("1"), "Artworks count should be 1"
    assert result.breakdown['pre_markup_total'] == Decimal("198"), "Pre-markup should be $198"
    assert result.total_price == Decimal("239.58"), "Total should be $239.58"
    print("  ✅ PASS\n")

def test_tier_3():
    """Test 3 A-frames"""
    calc = MetalFaceAFrameShopifyCalculator()
    result = calc.calculate(quantity=3, artworks=1)
    
    # Expected: rate $179.55
    # Subtotal: 3 × $179.55 = $538.65
    # Pre-markup: $538.65 + 1 = $539.65
    # First markup: $539.65 × 1.1 = $593.615 → $593.62
    # Final: $593.62 × 1.1 = $652.982 → $652.98
    
    print(f"Test 2 - 3 A-Frames (3 units, 1 artwork):")
    print(f"  Rate: ${result.breakdown['rate']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Total price: ${result.total_price}")
    print(f"  Per frame: ${result.unit_price}")
    
    assert result.breakdown['rate'] == Decimal("179.55"), "Rate should be $179.55"
    assert result.breakdown['subtotal'] == Decimal("538.65"), "Subtotal should be $538.65"
    assert result.total_price == Decimal("652.98"), "Total should be $652.98"
    print("  ✅ PASS\n")

def test_tier_6_unusual_increase():
    """Test 6 A-frames - unusual price INCREASE from qty 5"""
    calc = MetalFaceAFrameShopifyCalculator()
    result = calc.calculate(quantity=6, artworks=1)
    
    # Expected: rate $170.31 (higher than $165.80 at qty 5!)
    # Subtotal: 6 × $170.31 = $1021.86
    # Pre-markup: $1021.86 + 1 = $1022.86
    # First markup: $1022.86 × 1.1 = $1125.146
    # Final: $1125.146 × 1.1 = $1237.6606 → $1237.66 (no intermediate rounding)
    
    print(f"Test 3 - 6 A-Frames - Unusual Price Increase (6 units, 1 artwork):")
    print(f"  Rate: ${result.breakdown['rate']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Total price: ${result.total_price}")
    print(f"  NOTE: Rate $170.31 is HIGHER than qty 5 rate of $165.80")
    
    assert result.breakdown['rate'] == Decimal("170.31"), "Rate should be $170.31"
    assert result.breakdown['subtotal'] == Decimal("1021.86"), "Subtotal should be $1021.86"
    assert result.total_price == Decimal("1237.66"), "Total should be $1237.66"
    print("  ✅ PASS\n")

def test_multiple_artworks():
    """Test multiple artworks (adds artwork COUNT to subtotal, not cost)"""
    calc = MetalFaceAFrameShopifyCalculator()
    result = calc.calculate(quantity=5, artworks=3)
    
    # Expected: rate $165.80
    # Subtotal: 5 × $165.80 = $829
    # Pre-markup: $829 + 3 (artworks COUNT) = $832
    # First markup: $832 × 1.1 = $915.20
    # Final: $915.20 × 1.1 = $1006.72
    
    print(f"Test 4 - Multiple Artworks (5 units, 3 artworks):")
    print(f"  Rate: ${result.breakdown['rate']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Artworks added: ${result.breakdown['artworks_added']}")
    print(f"  Pre-markup total: ${result.breakdown['pre_markup_total']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['rate'] == Decimal("165.8"), "Rate should be $165.80"
    assert result.breakdown['subtotal'] == Decimal("829"), "Subtotal should be $829"
    assert result.breakdown['artworks_added'] == Decimal("3"), "Should add 3 artworks (COUNT)"
    assert result.breakdown['pre_markup_total'] == Decimal("832"), "Pre-markup should be $832"
    assert result.total_price == Decimal("1006.72"), "Total should be $1006.72"
    print("  ✅ PASS\n")

def test_tier_10_plus():
    """Test 11+ A-frames (uses same rate as qty 10)"""
    calc = MetalFaceAFrameShopifyCalculator()
    result = calc.calculate(quantity=15, artworks=1)
    
    # Expected: rate $159.35 (same as qty 10)
    # Subtotal: 15 × $159.35 = $2390.25
    # Pre-markup: $2390.25 + 1 = $2391.25
    # First markup: $2391.25 × 1.1 = $2630.375
    # Final: $2630.375 × 1.1 = $2893.4125 → $2893.41 (no intermediate rounding)
    
    print(f"Test 5 - 11+ A-Frames (15 units, 1 artwork):")
    print(f"  Rate: ${result.breakdown['rate']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Total price: ${result.total_price}")
    print(f"  Per frame: ${result.unit_price}")
    
    assert result.breakdown['rate'] == Decimal("159.35"), "Rate should be $159.35"
    assert result.breakdown['subtotal'] == Decimal("2390.25"), "Subtotal should be $2390.25"
    assert result.total_price == Decimal("2893.41"), "Total should be $2893.41"
    print("  ✅ PASS\n")

if __name__ == "__main__":
    print("=" * 70)
    print("METAL FACE A-FRAME - CALCULATOR VALIDATION")
    print("Backend: MetalFaceAFrame_Shopify_Calculator.py")
    print("Formula: qty-based tiers (10 tiers) + artworks COUNT + ×1.1 ×1.1")
    print("NOTE: Formula adds artwork COUNT directly, not artwork cost!")
    print("=" * 70 + "\n")
    
    try:
        test_single_unit()
        test_tier_3()
        test_tier_6_unusual_increase()
        test_multiple_artworks()
        test_tier_10_plus()
        
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
