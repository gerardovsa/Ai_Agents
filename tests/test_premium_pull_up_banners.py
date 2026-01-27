"""
Test cases for Premium Pull Up Banners Shopify calculator
Backend created Jan 25, 2026 with exact TXT formula

Test Strategy:
- Same formula as Luxury Classic Pull Up Banners but DIFFERENT tier pricing
- Quantity tier boundaries (1, 3, 10, 20, 50, 70+)
- Both size options (850×2000mm vs 850×1500mm)
- Artwork count (unusual: adds count directly, not cost calculation)
- Double GST (×1.1 ×1.1)
- $15 production setup fee
"""

import sys
from pathlib import Path

# Add backend path
backend_dir = Path(__file__).resolve().parent.parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'
sys.path.insert(0, str(backend_dir))

from PremiumPullUpBanners_Shopify_Calculator import PremiumPullUpBannersShopifyCalculator
from decimal import Decimal

def test_single_unit_2000mm():
    """Test 1 banner - 2000mm size with tier 1 pricing"""
    calc = PremiumPullUpBannersShopifyCalculator()
    result = calc.calculate(quantity=1, artworks=1, size='850mm W x 2000mm H')
    
    # Expected: rate $97 (DIFFERENT from Luxury Classic's $135)
    # Subtotal: 1 × $97 = $97
    # Pre-markup: $97 + 1 (artworks) + $15 (setup) = $113
    # First markup: $113 × 1.1 = $124.30
    # Final: $124.30 × 1.1 = $136.73
    
    print(f"Test 1 - Single Banner 2000mm (1 banner, 1 artwork):")
    print(f"  Rate: ${result.breakdown['rate']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Artworks added: ${result.breakdown['artworks_added']}")
    print(f"  Production setup: ${result.breakdown['production_setup']}")
    print(f"  Pre-markup total: ${result.breakdown['pre_markup_total']}")
    print(f"  After first markup: ${result.breakdown['after_first_markup']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['rate'] == Decimal("97"), "Rate should be $97"
    assert result.breakdown['subtotal'] == Decimal("97"), "Subtotal should be $97"
    assert result.breakdown['artworks_added'] == Decimal("1"), "Artworks count should be 1"
    assert result.breakdown['production_setup'] == Decimal("15"), "Setup should be $15"
    assert result.breakdown['pre_markup_total'] == Decimal("113"), "Pre-markup should be $113"
    assert result.total_price == Decimal("136.73"), "Total should be $136.73"
    print("  ✅ PASS\n")

def test_tier_boundary_10_2000mm():
    """Test 10 banners - 2000mm size tier boundary"""
    calc = PremiumPullUpBannersShopifyCalculator()
    result = calc.calculate(quantity=10, artworks=1, size='850mm W x 2000mm H')
    
    # Expected: rate $82.78 (DIFFERENT from Luxury Classic's $115.22)
    # Subtotal: 10 × $82.78 = $827.80
    # Pre-markup: $827.80 + 1 + $15 = $843.80
    # First markup: $843.80 × 1.1 = $928.18
    # Final: $928.18 × 1.1 = $1,020.998 → $1,021.00
    
    print(f"Test 2 - 10 Banners 2000mm (10 banners, 1 artwork):")
    print(f"  Rate: ${result.breakdown['rate']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Pre-markup total: ${result.breakdown['pre_markup_total']}")
    print(f"  Total price: ${result.total_price}")
    print(f"  Per banner: ${result.unit_price}")
    
    assert result.breakdown['rate'] == Decimal("82.78"), "Rate should be $82.78"
    assert result.breakdown['subtotal'] == Decimal("827.80"), "Subtotal should be $827.80"
    assert result.total_price == Decimal("1021.00"), "Total should be $1021.00"
    print("  ✅ PASS\n")

def test_single_unit_1500mm():
    """Test 1 banner - 1500mm size (different tier pricing)"""
    calc = PremiumPullUpBannersShopifyCalculator()
    result = calc.calculate(quantity=1, artworks=1, size='850mm W x 1500mm H')
    
    # Expected: rate $90 (DIFFERENT from Luxury Classic's $128)
    # Subtotal: 1 × $90 = $90
    # Pre-markup: $90 + 1 + $15 = $106
    # First markup: $106 × 1.1 = $116.60
    # Final: $116.60 × 1.1 = $128.26
    
    print(f"Test 3 - Single Banner 1500mm (1 banner, 1 artwork):")
    print(f"  Rate: ${result.breakdown['rate']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['rate'] == Decimal("90"), "Rate should be $90"
    assert result.breakdown['subtotal'] == Decimal("90"), "Subtotal should be $90"
    assert result.total_price == Decimal("128.26"), "Total should be $128.26"
    print("  ✅ PASS\n")

def test_multiple_artworks():
    """Test multiple artworks (adds artwork COUNT to subtotal, not cost)"""
    calc = PremiumPullUpBannersShopifyCalculator()
    result = calc.calculate(quantity=5, artworks=3, size='850mm W x 2000mm H')
    
    # Expected: rate $88.61
    # Subtotal: 5 × $88.61 = $443.05
    # Pre-markup: $443.05 + 3 (artworks COUNT) + $15 = $461.05
    # First markup: $461.05 × 1.1 = $507.155
    # Final: $507.155 × 1.1 = $557.8705 → $557.87 (no intermediate rounding)
    
    print(f"Test 4 - Multiple Artworks (5 banners, 3 artworks):")
    print(f"  Rate: ${result.breakdown['rate']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Artworks added: ${result.breakdown['artworks_added']}")
    print(f"  Pre-markup total: ${result.breakdown['pre_markup_total']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['rate'] == Decimal("88.61"), "Rate should be $88.61"
    assert result.breakdown['subtotal'] == Decimal("443.05"), "Subtotal should be $443.05"
    assert result.breakdown['artworks_added'] == Decimal("3"), "Should add 3 artworks (COUNT)"
    assert result.breakdown['pre_markup_total'] == Decimal("461.05"), "Pre-markup should be $461.05"
    assert result.total_price == Decimal("557.87"), "Total should be $557.87"
    print("  ✅ PASS\n")

def test_high_volume_70_plus():
    """Test 70+ banners (top tier pricing)"""
    calc = PremiumPullUpBannersShopifyCalculator()
    result = calc.calculate(quantity=70, artworks=1, size='850mm W x 2000mm H')
    
    # Expected: rate $73.72 (70+ tier) - DIFFERENT from Luxury Classic's $102.60
    # Subtotal: 70 × $73.72 = $5160.40
    # Pre-markup: $5160.40 + 1 + $15 = $5176.40
    # First markup: $5176.40 × 1.1 = $5694.04
    # Final: $5694.04 × 1.1 = $6263.444 → $6263.44
    
    print(f"Test 5 - High Volume (70 banners, 1 artwork):")
    print(f"  Rate: ${result.breakdown['rate']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Total price: ${result.total_price}")
    print(f"  Per banner: ${result.unit_price}")
    
    assert result.breakdown['rate'] == Decimal("73.72"), "Rate should be $73.72"
    assert result.breakdown['subtotal'] == Decimal("5160.40"), "Subtotal should be $5160.40"
    assert result.total_price == Decimal("6263.44"), "Total should be $6263.44"
    print("  ✅ PASS\n")

if __name__ == "__main__":
    print("=" * 70)
    print("PREMIUM PULL UP BANNERS - CALCULATOR VALIDATION")
    print("Backend: PremiumPullUpBanners_Shopify_Calculator.py")
    print("Formula: qty-based tiers + artworks COUNT + $15 setup + ×1.1 ×1.1")
    print("NOTE: Same formula as Luxury Classic but DIFFERENT tier pricing!")
    print("=" * 70 + "\n")
    
    try:
        test_single_unit_2000mm()
        test_tier_boundary_10_2000mm()
        test_single_unit_1500mm()
        test_multiple_artworks()
        test_high_volume_70_plus()
        
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
