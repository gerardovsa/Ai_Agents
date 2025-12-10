"""
Test Business Card Calculators (Phase 3)
Tests both Economical and Premium business card calculators
"""

import sys
sys.path.insert(0, r'c:\Users\gpoli\GIT\AI_agents\inhouse_modules')

from shopify_calculator_wrappers import (
    calculate_economical_business_cards_shopify,
    calculate_premium_business_cards_shopify
)

def test_economical_business_cards():
    """Test economical business cards - standard order"""
    print("\n" + "="*60)
    print("TEST: Economical Business Cards (1000 cards)")
    print("="*60)
    
    result = calculate_economical_business_cards_shopify(
        quantity=1000,
        double_sided=True,
        colour=True,
        artworks=1
    )
    
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
        return False
    
    print(f"✅ SUCCESS: Quote generated")
    print(f"   Total Price: ${result['total_price']:.2f}")
    print(f"   Unit Price: ${result['unit_price']:.4f} per card")
    print(f"   Cost Per Card: ${result['cost_per_card']:.4f}")
    
    if "breakdown" in result and isinstance(result["breakdown"], dict):
        print(f"\n   Cost Breakdown:")
        for key, value in result["breakdown"].items():
            if isinstance(value, (int, float)):
                print(f"     {key}: ${value:.2f}")
            else:
                print(f"     {key}: {value}")
    
    print(f"\n   Specifications:")
    specs = result.get("specifications", {})
    for key, value in specs.items():
        print(f"     {key}: {value}")
    
    return True


def test_economical_multi_artwork():
    """Test economical business cards with multiple artworks"""
    print("\n" + "="*60)
    print("TEST: Economical Business Cards (5 employees)")
    print("="*60)
    
    result = calculate_economical_business_cards_shopify(
        quantity=2000,
        double_sided=True,
        colour=True,
        artworks=5  # 5 different employee names
    )
    
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
        return False
    
    print(f"✅ SUCCESS: Quote generated")
    print(f"   Total Price: ${result['total_price']:.2f}")
    print(f"   Artwork Charge: 4 additional artworks × $15 = $60")
    
    return True


def test_premium_business_cards():
    """Test premium business cards with silk feel"""
    print("\n" + "="*60)
    print("TEST: Premium Business Cards (Luxury Finish)")
    print("="*60)
    
    result = calculate_premium_business_cards_shopify(
        quantity=500,
        double_sided=True,
        colour=True,
        stock="King Kong High Bulk",
        celloglaze="2 Side SILK FEEL Matt",
        artworks=1
    )
    
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
        return False
    
    print(f"✅ SUCCESS: Quote generated")
    print(f"   Total Price: ${result['total_price']:.2f}")
    print(f"   Unit Price: ${result['unit_price']:.4f} per card")
    print(f"   Cost Per Card: ${result['cost_per_card']:.4f}")
    
    if "breakdown" in result and isinstance(result["breakdown"], dict):
        print(f"\n   Cost Breakdown:")
        for key, value in result["breakdown"].items():
            if isinstance(value, (int, float)):
                print(f"     {key}: ${value:.2f}")
            else:
                print(f"     {key}: {value}")
    
    print(f"\n   Specifications:")
    specs = result.get("specifications", {})
    for key, value in specs.items():
        print(f"     {key}: {value}")
    
    return True


def test_premium_eco_friendly():
    """Test premium business cards with eco-friendly stock"""
    print("\n" + "="*60)
    print("TEST: Premium Business Cards (Eco-Friendly)")
    print("="*60)
    
    result = calculate_premium_business_cards_shopify(
        quantity=1000,
        double_sided=True,
        colour=True,
        stock="EcoStar 350GSM Uncoated",
        celloglaze="1 Side Matt",
        artworks=1
    )
    
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
        return False
    
    print(f"✅ SUCCESS: Quote generated")
    print(f"   Total Price: ${result['total_price']:.2f}")
    print(f"   Stock: EcoStar (eco-friendly)")
    
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("BUSINESS CARD CALCULATOR TESTS (Phase 3)")
    print("="*60)
    
    tests = [
        ("Economical Standard Order", test_economical_business_cards),
        ("Economical Multi-Artwork", test_economical_multi_artwork),
        ("Premium Luxury Finish", test_premium_business_cards),
        ("Premium Eco-Friendly", test_premium_eco_friendly)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("="*60)
