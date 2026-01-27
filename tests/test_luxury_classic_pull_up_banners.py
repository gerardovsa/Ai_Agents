"""
Test cases for Luxury Classic Pull Up Banners Shopify calculator
Backend implementation verified Jan 25, 2026 with exact TXT formula

Test Strategy:
- Quantity tier boundaries (1, 3, 10, 20, 50, 70+)
- Both size options (850x2000mm vs 850x1500mm)
- Artwork count (unusual: adds count directly, not cost calculation)
- Double GST (×1.1 ×1.1)
- $15 production setup fee
"""

import sys
from pathlib import Path

# Add backend path
backend_dir = Path(__file__).resolve().parent.parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'
sys.path.insert(0, str(backend_dir))

from LuxuryClassicPullUpBanners_Shopify_Calculator import LuxuryClassicPullUpBannersShopifyCalculator
from decimal import Decimal

def test_single_unit_2000mm():
    """Test 1 banner - 2000mm size with tier 1 pricing"""
    calc = LuxuryClassicPullUpBannersShopifyCalculator()
    result = calc.calculate(quantity=1, artworks=1, size='850mm W x 2000mm H')
    
    # Expected: rate $135
    # Subtotal: 1 × $135 = $135
    # Pre-markup: $135 + 1 (artworks) + $15 (setup) = $151
    # First markup: $151 × 1.1 = $166.10
    # Final: $166.10 × 1.1 = $182.71
    
    print(f"Test 1 - Single Banner 2000mm (1 banner, 1 artwork):")
    print(f"  Rate: ${result.breakdown['rate']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Artworks added: ${result.breakdown['artworks_added']}")
    print(f"  Production setup: ${result.breakdown['production_setup']}")
    print(f"  Pre-markup total: ${result.breakdown['pre_markup_total']}")
    print(f"  After first markup: ${result.breakdown['after_first_markup']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['rate'] == Decimal("135"), "Rate should be $135"
    assert result.breakdown['subtotal'] == Decimal("135"), "Subtotal should be $135"
    assert result.breakdown['artworks_added'] == Decimal("1"), "Artworks count should be 1"
    assert result.breakdown['production_setup'] == Decimal("15"), "Setup should be $15"
    assert result.breakdown['pre_markup_total'] == Decimal("151"), "Pre-markup should be $151"
    assert result.total_price == Decimal("182.71"), "Total should be $182.71"
    print("  ✅ PASS\n")

def test_tier_boundary_10_2000mm():
    """Test 10 banners - 2000mm size tier boundary"""
    calc = LuxuryClassicPullUpBannersShopifyCalculator()
    result = calc.calculate(quantity=10, artworks=1, size='850mm W x 2000mm H')
    
    # Expected: rate $115.22
    # Subtotal: 10 × $115.22 = $1152.20
    # Pre-markup: $1152.20 + 1 + $15 = $1168.20
    # First markup: $1168.20 × 1.1 = $1285.02
    # Final: $1285.02 × 1.1 = $1413.52
    
    print(f"Test 2 - 10 Banners 2000mm (10 banners, 1 artwork):")
    print(f"  Rate: ${result.breakdown['rate']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Pre-markup total: ${result.breakdown['pre_markup_total']}")
    print(f"  Total price: ${result.total_price}")
    print(f"  Per banner: ${result.unit_price}")
    
    assert result.breakdown['rate'] == Decimal("115.22"), "Rate should be $115.22"
    assert result.breakdown['subtotal'] == Decimal("1152.20"), "Subtotal should be $1152.20"
    assert result.total_price == Decimal("1413.52"), "Total should be $1413.52"
    print("  ✅ PASS\n")

def test_single_unit_1500mm():
    """Test 1 banner - 1500mm size (different tier pricing)"""
    calc = LuxuryClassicPullUpBannersShopifyCalculator()
    result = calc.calculate(quantity=1, artworks=1, size='850mm W x 1500mm H')
    
    # Expected: rate $128 (different from 2000mm)
    # Subtotal: 1 × $128 = $128
    # Pre-markup: $128 + 1 + $15 = $144
    # First markup: $144 × 1.1 = $158.40
    # Final: $158.40 × 1.1 = $174.24
    
    print(f"Test 3 - Single Banner 1500mm (1 banner, 1 artwork):")
    print(f"  Rate: ${result.breakdown['rate']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['rate'] == Decimal("128"), "Rate should be $128"
    assert result.breakdown['subtotal'] == Decimal("128"), "Subtotal should be $128"
    assert result.total_price == Decimal("174.24"), "Total should be $174.24"
    print("  ✅ PASS\n")

def test_multiple_artworks():
    """Test multiple artworks (adds artwork COUNT to subtotal, not cost)"""
    calc = LuxuryClassicPullUpBannersShopifyCalculator()
    result = calc.calculate(quantity=5, artworks=3, size='850mm W x 2000mm H')
    
    # Expected: rate $123.33
    # Subtotal: 5 × $123.33 = $616.65
    # Pre-markup: $616.65 + 3 (artworks COUNT) + $15 = $634.65
    # First markup: $634.65 × 1.1 = $698.12
    # Final: $698.12 × 1.1 = $767.93
    
    print(f"Test 4 - Multiple Artworks (5 banners, 3 artworks):")
    print(f"  Rate: ${result.breakdown['rate']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Artworks added: ${result.breakdown['artworks_added']}")
    print(f"  Pre-markup total: ${result.breakdown['pre_markup_total']}")
    print(f"  Total price: ${result.total_price}")
    
    assert result.breakdown['rate'] == Decimal("123.33"), "Rate should be $123.33"
    assert result.breakdown['subtotal'] == Decimal("616.65"), "Subtotal should be $616.65"
    assert result.breakdown['artworks_added'] == Decimal("3"), "Should add 3 artworks (COUNT)"
    assert result.breakdown['pre_markup_total'] == Decimal("634.65"), "Pre-markup should be $634.65"
    assert result.total_price == Decimal("767.93"), "Total should be $767.93"
    print("  ✅ PASS\n")

def test_high_volume_70_plus():
    """Test 70+ banners (top tier pricing)"""
    calc = LuxuryClassicPullUpBannersShopifyCalculator()
    result = calc.calculate(quantity=70, artworks=1, size='850mm W x 2000mm H')
    
    # Expected: rate $102.60 (70+ tier)
    # Subtotal: 70 × $102.60 = $7182
    # Pre-markup: $7182 + 1 + $15 = $7198
    # First markup: $7198 × 1.1 = $7917.80
    # Final: $7917.80 × 1.1 = $8709.58
    
    print(f"Test 5 - High Volume (70 banners, 1 artwork):")
    print(f"  Rate: ${result.breakdown['rate']}")
    print(f"  Subtotal: ${result.breakdown['subtotal']}")
    print(f"  Total price: ${result.total_price}")
    print(f"  Per banner: ${result.unit_price}")
    
    assert result.breakdown['rate'] == Decimal("102.6"), "Rate should be $102.60"
    assert result.breakdown['subtotal'] == Decimal("7182"), "Subtotal should be $7182"
    assert result.total_price == Decimal("8709.58"), "Total should be $8709.58"
    print("  ✅ PASS\n")

if __name__ == "__main__":
    print("=" * 70)
    print("LUXURY CLASSIC PULL UP BANNERS - CALCULATOR VALIDATION")
    print("Backend: LuxuryClassicPullUpBanners_Shopify_Calculator.py")
    print("Formula: qty-based tiers + artworks COUNT + $15 setup + ×1.1 ×1.1")
    print("NOTE: Formula adds artwork COUNT directly, not artwork cost!")
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
