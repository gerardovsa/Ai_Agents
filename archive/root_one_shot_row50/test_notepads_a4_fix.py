"""
Test Notepads A4 JSON Format Alignment
Tests that backend and wrapper accept JSON format parameters
"""
import sys
from pathlib import Path

# Add paths
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'
sys.path.insert(0, str(backend_path))

wrapper_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'
sys.path.insert(0, str(wrapper_path))

from calculator_wrapper import calculate_notepads_a4

def test_json_format():
    """Test 1: JSON format with all correct values"""
    print("\n" + "="*70)
    print("✅ Test 1: JSON format - 100 qty, Colour 2 sided, 80GSM, 50 leaves")
    print("="*70)
    
    result = calculate_notepads_a4(
        quantity="100",  # String as in JSON
        print_type="Colour 2 sided",  # Combined format from JSON
        stock_type="Uncoated Bond 80GSM",  # JSON field name
        leaves_per_pad="50",  # String as in JSON
        finish_size="A4 Portrait",
        artworks=1
    )
    
    print(f"Success: {result.get('success')}")
    if result.get('success'):
        print(f"Total: ${result['total_price']:.2f}")
        print(f"Unit: ${result['unit_price']:.2f}")
        print(f"Quantity: {result['quantity']}")
    else:
        print(f"Error: {result.get('error')}")
    
    return result.get('success')

def test_invalid_quantity():
    """Test 2: Invalid quantity should be rejected"""
    print("\n" + "="*70)
    print("❌ Test 2: Invalid quantity '999' should be rejected")
    print("="*70)
    
    result = calculate_notepads_a4(
        quantity="999",  # Invalid quantity not in enum
        print_type="Black & White 1 sided",
        stock_type="Uncoated Bond 80GSM",
        leaves_per_pad="50",
        finish_size="A4 Portrait",
        artworks=1
    )
    
    print(f"Success: {result.get('success')}")
    if not result.get('success'):
        print(f"✅ Correctly rejected: {result.get('error')}")
    else:
        print(f"❌ Should have rejected invalid quantity")
    
    return not result.get('success')

def test_invalid_print_type():
    """Test 3: Invalid print type should be rejected"""
    print("\n" + "="*70)
    print("❌ Test 3: Invalid print_type 'Colour' (old format) should be rejected")
    print("="*70)
    
    result = calculate_notepads_a4(
        quantity="100",
        print_type="Colour",  # Old format without "sided"
        stock_type="Uncoated Bond 80GSM",
        leaves_per_pad="50",
        finish_size="A4 Portrait",
        artworks=1
    )
    
    print(f"Success: {result.get('success')}")
    if not result.get('success'):
        print(f"✅ Correctly rejected: {result.get('error')}")
    else:
        print(f"❌ Should have rejected old format")
    
    return not result.get('success')

def test_invalid_stock_type():
    """Test 4: Invalid stock type should be rejected"""
    print("\n" + "="*70)
    print("❌ Test 4: Invalid stock_type 'Standard' should be rejected")
    print("="*70)
    
    result = calculate_notepads_a4(
        quantity="100",
        print_type="Black & White 1 sided",
        stock_type="Standard",  # Invalid stock type
        leaves_per_pad="50",
        finish_size="A4 Portrait",
        artworks=1
    )
    
    print(f"Success: {result.get('success')}")
    if not result.get('success'):
        print(f"✅ Correctly rejected: {result.get('error')}")
    else:
        print(f"❌ Should have rejected invalid stock type")
    
    return not result.get('success')

if __name__ == '__main__':
    print("\n" + "="*70)
    print("NOTEPADS A4 JSON FORMAT ALIGNMENT TEST")
    print("="*70)
    
    test1 = test_json_format()
    test2 = test_invalid_quantity()
    test3 = test_invalid_print_type()
    test4 = test_invalid_stock_type()
    
    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    passed = sum([test1, test2, test3, test4])
    total = 4
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Notepads A4 aligned to JSON format")
    else:
        print(f"❌ {total - passed} tests failed")
    
    sys.exit(0 if passed == total else 1)
