"""
GROUP 5 CALCULATOR ALIGNMENT TESTS - Promotional Products
Tests for all 5 Group 5 calculators following CALCULATOR_ALIGNMENT_INSTRUCTIONS.md
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
    calculate_luxury_classic_pull_up_banners,
    calculate_selfie_frames,
    calculate_stackable_cubes,
    calculate_strut_cards_a3,
    calculate_strut_cards_a4
)


def test_luxury_classic_pull_up_banners():
    """Test 1: Luxury Classic Pull Up Banners - Standard parameters"""
    print("\n🧪 TEST 1: Luxury Classic Pull Up Banners")
    result = calculate_luxury_classic_pull_up_banners(
        quantity=5,
        width_mm=850,
        height_mm=2000,
        material="Premium Vinyl"
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Luxury Classic Pull Up Banners: ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_selfie_frames():
    """Test 2: Selfie Frames - Standard parameters"""
    print("\n🧪 TEST 2: Selfie Frames")
    result = calculate_selfie_frames(
        quantity=10,
        width_mm=600,
        height_mm=600,
        material="Foam Core",
        artworks=1
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Selfie Frames: ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_stackable_cubes():
    """Test 3: Stackable Cubes - Standard parameters"""
    print("\n🧪 TEST 3: Stackable Cubes")
    result = calculate_stackable_cubes(
        quantity=10,
        size="300",
        material="Corrugated"
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Stackable Cubes: ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_strut_cards_a3():
    """Test 4: Strut Cards A3 - Standard parameters"""
    print("\n🧪 TEST 4: Strut Cards A3")
    result = calculate_strut_cards_a3(
        quantity=100,
        size="297x420",
        sides="Single",
        artworks=1
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Strut Cards A3: ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_strut_cards_a4():
    """Test 5: Strut Cards A4 - Standard parameters"""
    print("\n🧪 TEST 5: Strut Cards A4")
    result = calculate_strut_cards_a4(
        quantity=100,
        size="210x297",
        sides="Single",
        artworks=1
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Strut Cards A4: ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_pull_up_banners_legacy():
    """Test 6: Pull Up Banners - Legacy parameters (width/height)"""
    print("\n🧪 TEST 6: Pull Up Banners (Legacy Parameters)")
    result = calculate_luxury_classic_pull_up_banners(
        quantity=5,
        width=850,  # Legacy parameter
        height=2000,  # Legacy parameter
        material="Premium Vinyl"
    )
    
    if result["success"]:
        if "warnings" in result and len(result["warnings"]) > 0:
            print("⚠️  DEPRECATED PARAMETERS in calculate_luxury_classic_pull_up_banners:")
            for warning in result["warnings"]:
                print(f"   {warning['deprecated']}={warning['value']} → {warning['use_instead']}={warning['value']}")
        price = result["total_price"]
        print(f"✅ PASS - Legacy parameters work with {len(result.get('warnings', []))} warnings")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_selfie_frames_legacy():
    """Test 7: Selfie Frames - Legacy parameters"""
    print("\n🧪 TEST 7: Selfie Frames (Legacy Parameters)")
    result = calculate_selfie_frames(
        quantity=10,
        width=600,  # Legacy parameter
        height=600,  # Legacy parameter
        material="Foam Core",
        artworks=1
    )
    
    if result["success"]:
        if "warnings" in result and len(result["warnings"]) > 0:
            print("⚠️  DEPRECATED PARAMETERS in calculate_selfie_frames:")
            for warning in result["warnings"]:
                print(f"   {warning['deprecated']}={warning['value']} → {warning['use_instead']}={warning['value']}")
        price = result["total_price"]
        print(f"✅ PASS - Legacy parameters work with {len(result.get('warnings', []))} warnings")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_strut_cards_double_sided():
    """Test 8: Strut Cards - Double sided with multiple artworks"""
    print("\n🧪 TEST 8: Strut Cards A3 (Double Sided)")
    result = calculate_strut_cards_a3(
        quantity=100,
        size="297x420",
        sides="Double",
        artworks=2
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Strut Cards A3 (Double): ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_backend_integration():
    """Test 9: Backend Integration - Multiple calculators"""
    print("\n🧪 TEST 9: Backend Integration")
    
    tests = [
        ("Pull Up Banners (10qty)", calculate_luxury_classic_pull_up_banners(quantity=10, width_mm=850, height_mm=2000, material="Premium Vinyl")),
        ("Selfie Frames (Card)", calculate_selfie_frames(quantity=10, width_mm=600, height_mm=600, material="Card", artworks=1)),
        ("Stackable Cubes (Card)", calculate_stackable_cubes(quantity=20, size="300", material="Card")),
        ("Strut Cards A4 (Double)", calculate_strut_cards_a4(quantity=100, size="210x297", sides="Double", artworks=1))
    ]
    
    passed = 0
    for name, result in tests:
        if result["success"]:
            passed += 1
            print(f"  ✅ {name}: ${result['total_price']:.2f}")
        else:
            print(f"  ❌ {name}: {result.get('error')}")
    
    if passed == len(tests):
        print(f"✅ PASS - All {len(tests)} backend integrations working")
        return True
    else:
        print(f"❌ FAIL - Only {passed}/{len(tests)} passed")
        return False


def main():
    """Run all Group 5 tests"""
    print("=" * 48)
    print("GROUP 5 CALCULATOR ALIGNMENT TESTS")
    print("=" * 48)
    
    results = []
    
    # Test all calculators
    results.append(("Luxury Classic Pull Up Banners", test_luxury_classic_pull_up_banners()))
    results.append(("Selfie Frames", test_selfie_frames()))
    results.append(("Stackable Cubes", test_stackable_cubes()))
    results.append(("Strut Cards A3", test_strut_cards_a3()))
    results.append(("Strut Cards A4", test_strut_cards_a4()))
    results.append(("Pull Up Banners (Legacy)", test_pull_up_banners_legacy()))
    results.append(("Selfie Frames (Legacy)", test_selfie_frames_legacy()))
    results.append(("Strut Cards (Double)", test_strut_cards_double_sided()))
    results.append(("Backend Integration", test_backend_integration()))
    
    # Summary
    print("\n" + "=" * 48)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL GROUP 5 TESTS COMPLETE!")
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
