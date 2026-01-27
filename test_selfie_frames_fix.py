"""
Test Selfie Frames JSON Format Alignment
Tests that backend and wrapper accept JSON format parameters
"""
import sys
from pathlib import Path

# Add paths
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'
sys.path.insert(0, str(backend_path))

wrapper_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'
sys.path.insert(0, str(wrapper_path))

from calculator_wrapper import calculate_selfie_frames

def test_json_format_small():
    """Test 1: JSON format with small size"""
    print("\n" + "="*70)
    print("✅ Test 1: JSON format - 10 qty, Small 600mm x 900mm, 1 artwork")
    print("="*70)
    
    result = calculate_selfie_frames(
        quantity=10,
        size="Small 600mm x 900mm",  # JSON format
        number_of_artworks=1  # JSON field name
    )
    
    print(f"Success: {result.get('success')}")
    if result.get('success'):
        print(f"Total: ${result['total_price']:.2f}")
        print(f"Unit: ${result['unit_price']:.2f}")
        print(f"Quantity: {result['quantity']}")
    else:
        print(f"Error: {result.get('error')}")
    
    return result.get('success')

def test_json_format_large():
    """Test 2: JSON format with large size and multiple artworks"""
    print("\n" + "="*70)
    print("✅ Test 2: JSON format - 5 qty, Large 900mm x 1200mm, 3 artworks")
    print("="*70)
    
    result = calculate_selfie_frames(
        quantity=5,
        size="Large 900mm x 1200mm",  # JSON format
        number_of_artworks=3  # Multiple artworks
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
    print("❌ Test 3: Invalid size '600x900' (old format) should be rejected")
    print("="*70)
    
    result = calculate_selfie_frames(
        quantity=10,
        size="600x900",  # Old format without "Small" prefix
        number_of_artworks=1
    )
    
    print(f"Success: {result.get('success')}")
    if not result.get('success'):
        print(f"✅ Correctly rejected: {result.get('error')}")
    else:
        print(f"❌ Should have rejected invalid size")
    
    return not result.get('success')

def test_invalid_artworks():
    """Test 4: Invalid number of artworks should be rejected"""
    print("\n" + "="*70)
    print("❌ Test 4: Invalid number_of_artworks 25 (exceeds max 20) should be rejected")
    print("="*70)
    
    result = calculate_selfie_frames(
        quantity=10,
        size="Small 600mm x 900mm",
        number_of_artworks=25  # Exceeds max
    )
    
    print(f"Success: {result.get('success')}")
    if not result.get('success'):
        print(f"✅ Correctly rejected: {result.get('error')}")
    else:
        print(f"❌ Should have rejected invalid artworks")
    
    return not result.get('success')

if __name__ == '__main__':
    print("\n" + "="*70)
    print("SELFIE FRAMES JSON FORMAT ALIGNMENT TEST")
    print("="*70)
    
    test1 = test_json_format_small()
    test2 = test_json_format_large()
    test3 = test_invalid_size()
    test4 = test_invalid_artworks()
    
    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    passed = sum([test1, test2, test3, test4])
    total = 4
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Selfie Frames aligned to JSON format")
    else:
        print(f"❌ {total - passed} tests failed")
    
    sys.exit(0 if passed == total else 1)
