"""
Test Luxury Classic Pull Up Banners JSON Format Alignment
Tests that backend and wrapper accept JSON format parameters
"""
import sys
from pathlib import Path

# Add paths
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'
sys.path.insert(0, str(backend_path))

wrapper_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'
sys.path.insert(0, str(wrapper_path))

from calculator_wrapper import calculate_luxury_classic_pull_up_banners

def test_json_format():
    """Test 1: JSON format with all correct values"""
    print("\n" + "="*70)
    print("✅ Test 1: JSON format - 5 qty, 850mm W x 2000mm H, Silver, 2 artworks")
    print("="*70)
    
    result = calculate_luxury_classic_pull_up_banners(
        quantity=5,
        size="850mm W x 2000mm H",  # JSON format
        base_colour="Silver",  # JSON field name
        artworks=2  # Multiple artworks (affects setup costs)
    )
    
    print(f"Success: {result.get('success')}")
    if result.get('success'):
        print(f"Total: ${result['total_price']:.2f}")
        print(f"Unit: ${result['unit_price']:.2f}")
        print(f"Quantity: {result['quantity']}")
    else:
        print(f"Error: {result.get('error')}")
    
    return result.get('success')

def test_shopping_center_size():
    """Test 2: Shopping center size option"""
    print("\n" + "="*70)
    print("✅ Test 2: JSON format - 1 qty, Shopping Center size, Black base")
    print("="*70)
    
    result = calculate_luxury_classic_pull_up_banners(
        quantity=1,
        size="850mm W x 1400mm H Shopping Center",  # Special size format
        base_colour="Black",
        artworks=1
    )
    
    print(f"Success: {result.get('success')}")
    if result.get('success'):
        print(f"Total: ${result['total_price']:.2f}")
        print(f"Unit: ${result['unit_price']:.2f}")
    else:
        print(f"Error: {result.get('error')}")
    
    return result.get('success')

def test_invalid_size():
    """Test 3: Invalid size should be rejected"""
    print("\n" + "="*70)
    print("❌ Test 3: Invalid size '850x2000' (old format) should be rejected")
    print("="*70)
    
    result = calculate_luxury_classic_pull_up_banners(
        quantity=5,
        size="850x2000",  # Old format without spaces
        base_colour="Silver",
        artworks=1
    )
    
    print(f"Success: {result.get('success')}")
    if not result.get('success'):
        print(f"✅ Correctly rejected: {result.get('error')}")
    else:
        print(f"❌ Should have rejected invalid size")
    
    return not result.get('success')

def test_invalid_base_colour():
    """Test 4: Invalid base colour should be rejected"""
    print("\n" + "="*70)
    print("❌ Test 4: Invalid base_colour 'Gold' should be rejected")
    print("="*70)
    
    result = calculate_luxury_classic_pull_up_banners(
        quantity=5,
        size="850mm W x 2000mm H",
        base_colour="Gold",  # Invalid color
        artworks=1
    )
    
    print(f"Success: {result.get('success')}")
    if not result.get('success'):
        print(f"✅ Correctly rejected: {result.get('error')}")
    else:
        print(f"❌ Should have rejected invalid base colour")
    
    return not result.get('success')

if __name__ == '__main__':
    print("\n" + "="*70)
    print("LUXURY CLASSIC PULL UP BANNERS JSON FORMAT ALIGNMENT TEST")
    print("="*70)
    
    test1 = test_json_format()
    test2 = test_shopping_center_size()
    test3 = test_invalid_size()
    test4 = test_invalid_base_colour()
    
    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    passed = sum([test1, test2, test3, test4])
    total = 4
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Luxury Classic Pull Up Banners aligned to JSON format")
    else:
        print(f"❌ {total - passed} tests failed")
    
    sys.exit(0 if passed == total else 1)
