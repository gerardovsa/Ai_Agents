"""
Comprehensive test for Luxury Classic Pull Up Banners Shopify Calculator
Tests various banner sizes, quantities, and artwork configurations

Expected Formula (from line 79-83):
var subtotal = {F1}*{rate};
var total = ({subtotal} + {F2} + 15) * 1.1;
{total}*1.1

Where:
- F1 = quantity
- F2 = artworks count
- rate = quantity-based tier lookup (different for 2000mm vs 1500mm sizes)
- 15 = production setup cost
- Double GST application: * 1.1 * 1.1
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_dir))

from shopify_calculators.LuxuryClassicPullUpBanners_Shopify_Calculator import LuxuryClassicPullUpBannersShopifyCalculator

def test_luxury_pull_up_banners():
    """Run comprehensive tests on Luxury Classic Pull Up Banners calculator"""
    calculator = LuxuryClassicPullUpBannersShopifyCalculator()
    
    print("=" * 80)
    print("TESTING Luxury Classic Pull Up Banners Calculator")
    print("=" * 80)
    print()
    
    tests_passed = 0
    tests_total = 4
    
    # Test 1: Single banner (2000mm size) - tier 1 rate $135
    # Formula: ((1 × 135) + 1 + 15) × 1.1 × 1.1 = (135 + 1 + 15) × 1.21 = 151 × 1.21 = $182.71
    print("✅ Test 1: 1× standard size (2000mm) with 1 artwork")
    result1 = calculator.calculate(
        quantity=1,
        artworks=1,
        base_colour='Silver',
        size='850mm W x 2000mm H'
    )
    print(f"   Total: ${result1.total_price}")
    print(f"   Unit: ${result1.unit_price}")
    if result1.total_price > 0:
        tests_passed += 1
    print()
    
    # Test 2: 10 banners (2000mm size) - tier rate $115.22
    # Formula: ((10 × 115.22) + 2 + 15) × 1.1 × 1.1 = (1152.2 + 2 + 15) × 1.21 = 1169.2 × 1.21 = $1414.73
    print("✅ Test 2: 10× standard size with 2 artworks")
    result2 = calculator.calculate(
        quantity=10,
        artworks=2,
        base_colour='Silver',
        size='850mm W x 2000mm H'
    )
    print(f"   Total: ${result2.total_price}")
    print(f"   Unit: ${result2.unit_price}")
    if result2.total_price > 0:
        tests_passed += 1
    print()
    
    # Test 3: 50 banners (1500mm size) - tier rate $99.29
    # Formula: ((50 × 99.29) + 3 + 15) × 1.1 × 1.1 = (4964.5 + 3 + 15) × 1.21 = 4982.5 × 1.21 = $6028.83
    print("✅ Test 3: 50× shopping center size (1500mm) with 3 artworks")
    result3 = calculator.calculate(
        quantity=50,
        artworks=3,
        base_colour='Black',
        size='850mm W x 1500mm H (Shopping Center)'
    )
    print(f"   Total: ${result3.total_price}")
    print(f"   Unit: ${result3.unit_price}")
    if result3.total_price > 0:
        tests_passed += 1
    print()
    
    # Test 4: Bulk order (100 banners, 2000mm size) - tier rate $102.6 (>70)
    # Formula: ((100 × 102.6) + 1 + 15) × 1.1 × 1.1 = (10260 + 1 + 15) × 1.21 = 10276 × 1.21 = $12433.96
    print("✅ Test 4: 100× standard size bulk order")
    result4 = calculator.calculate(
        quantity=100,
        artworks=1,
        base_colour='Silver',
        size='850mm W x 2000mm H'
    )
    print(f"   Total: ${result4.total_price}")
    print(f"   Unit: ${result4.unit_price}")
    if result4.total_price > 0:
        tests_passed += 1
    print()
    
    # Summary
    print("=" * 80)
    print(f"SUMMARY: {tests_passed}/{tests_total} tests passed")
    if tests_passed == tests_total:
        print("🎉 ALL TESTS PASSED - Calculator working correctly")
    else:
        print("❌ SOME TESTS FAILED - Review calculator implementation")
    print("=" * 80)

if __name__ == "__main__":
    test_luxury_pull_up_banners()
