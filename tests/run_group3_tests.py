"""
GROUP 3 CALCULATOR ALIGNMENT TESTS - Notepads & Printing
Tests for all 5 Group 3 calculators following CALCULATOR_ALIGNMENT_INSTRUCTIONS.md
"""

import sys
from pathlib import Path

# Add backend path to sys.path
backend_dir = Path(__file__).resolve().parent.parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_dir))

# Import wrapper
wrapper_dir = Path(__file__).resolve().parent.parent / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'
sys.path.insert(0, str(wrapper_dir))

from calculator_wrapper import (
    calculate_notepads_a4,
    calculate_notepads_a5,
    calculate_notepads_a6,
    calculate_custom_poster_printing,
    calculate_custom_vinyl_stickers
)


def test_notepads_a4():
    """Test 1: Notepads A4 - Standard parameters"""
    print("\n🧪 TEST 1: Notepads A4")
    result = calculate_notepads_a4(
        quantity=250,
        print_type="Colour",
        print_sides="Single side print",
        paper_stock="Standard",
        artworks=1,
        pads_per_book=1
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Notepads A4: ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_notepads_a5():
    """Test 2: Notepads A5 - Standard parameters"""
    print("\n🧪 TEST 2: Notepads A5")
    result = calculate_notepads_a5(
        quantity=250,
        print_type="Colour",
        print_sides="Single side print",
        paper_stock="Standard",
        artworks=1
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Notepads A5: ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_notepads_a6():
    """Test 3: Notepads A6 - Standard parameters"""
    print("\n🧪 TEST 3: Notepads A6")
    result = calculate_notepads_a6(
        quantity=250,
        print_type="Colour",
        print_sides="Single side print",
        paper_stock="Standard",
        artworks=1
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Notepads A6: ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_custom_poster_printing():
    """Test 4: Custom Poster Printing - Standard A2 size"""
    print("\n🧪 TEST 4: Custom Poster Printing")
    result = calculate_custom_poster_printing(
        quantity=50,
        width_mm=420,
        height_mm=594,
        paper_stock="150gsm"
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Custom Poster Printing: ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_custom_vinyl_stickers():
    """Test 5: Custom Vinyl Stickers - Standard 100mm square"""
    print("\n🧪 TEST 5: Custom Vinyl Stickers")
    result = calculate_custom_vinyl_stickers(
        quantity=100,
        width_mm=100,
        height_mm=100,
        finish="Gloss"
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Custom Vinyl Stickers: ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_notepads_legacy_parameters():
    """Test 6: Legacy Parameters (Notepads A4)"""
    print("\n🧪 TEST 6: Legacy Parameters (Notepads A4)")
    result = calculate_notepads_a4(
        quantity=250,
        print_type="Colour",
        print_sides="Single side print",
        stock_type="Uncoated Bond 80GSM",  # Legacy parameter
        artworks=1
    )
    
    if result["success"]:
        if "warnings" in result and len(result["warnings"]) > 0:
            print("⚠️  DEPRECATED PARAMETERS in calculate_notepads_a4:")
            for warning in result["warnings"]:
                print(f"   {warning['deprecated']}={warning['value']} → {warning['use_instead']}='{warning['value']}'")
        price = result["total_price"]
        print(f"✅ PASS - Legacy parameters work with {len(result.get('warnings', []))} warnings")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_poster_legacy_parameters():
    """Test 7: Legacy Parameters (Custom Poster Printing)"""
    print("\n🧪 TEST 7: Legacy Parameters (Custom Poster Printing)")
    result = calculate_custom_poster_printing(
        quantity=50,
        width=420,  # Legacy parameter
        height=594,  # Legacy parameter
        paper_stock="150gsm"
    )
    
    if result["success"]:
        if "warnings" in result and len(result["warnings"]) > 0:
            print("⚠️  DEPRECATED PARAMETERS in calculate_custom_poster_printing:")
            for warning in result["warnings"]:
                print(f"   {warning['deprecated']}={warning['value']} → {warning['use_instead']}={warning['value']}")
        price = result["total_price"]
        print(f"✅ PASS - Legacy parameters work with {len(result.get('warnings', []))} warnings")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_vinyl_legacy_parameters():
    """Test 8: Legacy Parameters (Custom Vinyl Stickers)"""
    print("\n🧪 TEST 8: Legacy Parameters (Custom Vinyl Stickers)")
    result = calculate_custom_vinyl_stickers(
        quantity=100,
        width=100,  # Legacy parameter
        height=100,  # Legacy parameter
        finish="Gloss"
    )
    
    if result["success"]:
        if "warnings" in result and len(result["warnings"]) > 0:
            print("⚠️  DEPRECATED PARAMETERS in calculate_custom_vinyl_stickers:")
            for warning in result["warnings"]:
                print(f"   {warning['deprecated']}={warning['value']} → {warning['use_instead']}={warning['value']}")
        price = result["total_price"]
        print(f"✅ PASS - Legacy parameters work with {len(result.get('warnings', []))} warnings")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def main():
    """Run all Group 3 tests"""
    print("=" * 48)
    print("GROUP 3 CALCULATOR ALIGNMENT TESTS")
    print("=" * 48)
    
    results = []
    
    # Test all calculators
    results.append(("Notepads A4", test_notepads_a4()))
    results.append(("Notepads A5", test_notepads_a5()))
    results.append(("Notepads A6", test_notepads_a6()))
    results.append(("Custom Poster Printing", test_custom_poster_printing()))
    results.append(("Custom Vinyl Stickers", test_custom_vinyl_stickers()))
    results.append(("Legacy Parameters (Notepads)", test_notepads_legacy_parameters()))
    results.append(("Legacy Parameters (Poster)", test_poster_legacy_parameters()))
    results.append(("Legacy Parameters (Vinyl)", test_vinyl_legacy_parameters()))
    
    # Summary
    print("\n" + "=" * 48)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL GROUP 3 TESTS COMPLETE!")
    else:
        print(f"⚠️  {passed}/{total} TESTS PASSED")
        print("\nFailed tests:")
        for name, result in results:
            if not result:
                print(f"  ❌ {name}")
    
    print("=" * 48)
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
