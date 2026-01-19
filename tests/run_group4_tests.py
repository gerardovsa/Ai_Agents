"""
GROUP 4 CALCULATOR ALIGNMENT TESTS - Signs & Displays
Tests for all 5 Group 4 calculators following CALCULATOR_ALIGNMENT_INSTRUCTIONS.md
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
    calculate_election_signs,
    calculate_construction_signs,
    calculate_bollard_signs,
    calculate_corflute_insert_a_frame,
    calculate_metal_face_a_frame
)


def test_election_signs():
    """Test 1: Election Signs - Standard parameters"""
    print("\n🧪 TEST 1: Election Signs")
    result = calculate_election_signs(
        quantity=50,
        size="600x450",
        material="Corflute",
        sides="Single",
        artworks=1
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Election Signs: ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_construction_signs():
    """Test 2: Construction Signs - Standard parameters"""
    print("\n🧪 TEST 2: Construction Signs")
    result = calculate_construction_signs(
        quantity=10,
        size="600x450",
        material="Corflute",
        sides="Single",
        artworks=1
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Construction Signs: ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_bollard_signs():
    """Test 3: Bollard Signs - Standard parameters"""
    print("\n🧪 TEST 3: Bollard Signs")
    result = calculate_bollard_signs(
        quantity=10,
        size="300x300",
        material="Aluminium",
        sides="Single",
        artworks=1
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Bollard Signs: ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_corflute_insert_a_frame():
    """Test 4: Corflute Insert A-Frame - Standard parameters"""
    print("\n🧪 TEST 4: Corflute Insert A-Frame")
    result = calculate_corflute_insert_a_frame(
        quantity=10,
        size="600x450",
        sides="Single",
        artworks=1
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Corflute Insert A-Frame: ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_metal_face_a_frame():
    """Test 5: Metal Face A-Frame - Standard parameters"""
    print("\n🧪 TEST 5: Metal Face A-Frame")
    result = calculate_metal_face_a_frame(
        quantity=10,
        size="600x450",
        sides="Single",
        artworks=1
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Metal Face A-Frame: ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_election_signs_double_sided():
    """Test 6: Election Signs - Double sided with multiple artworks"""
    print("\n🧪 TEST 6: Election Signs (Double Sided)")
    result = calculate_election_signs(
        quantity=100,
        size="600x450",
        material="Corflute",
        sides="Double",
        artworks=2
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Election Signs (Double): ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_construction_signs_metal():
    """Test 7: Construction Signs - Metal material"""
    print("\n🧪 TEST 7: Construction Signs (Metal)")
    result = calculate_construction_signs(
        quantity=25,
        size="600x450",
        material="metal",  # lowercase test
        sides="Double",
        artworks=1
    )
    
    if result["success"]:
        price = result["total_price"]
        print(f"✅ PASS - Construction Signs (Metal): ${price:.2f}")
        return True
    else:
        print(f"❌ FAIL - Error: {result.get('error')}")
        return False


def test_backend_integration():
    """Test 8: Backend Integration - Multiple calculators"""
    print("\n🧪 TEST 8: Backend Integration")
    
    tests = [
        ("Bollard", calculate_bollard_signs(quantity=5, size="300x300", material="Aluminium", sides="Single", artworks=1)),
        ("Corflute A-Frame", calculate_corflute_insert_a_frame(quantity=5, size="600x450", sides="Double", artworks=1)),
        ("Metal A-Frame", calculate_metal_face_a_frame(quantity=5, size="600x450", sides="Double", artworks=1))
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
    """Run all Group 4 tests"""
    print("=" * 48)
    print("GROUP 4 CALCULATOR ALIGNMENT TESTS")
    print("=" * 48)
    
    results = []
    
    # Test all calculators
    results.append(("Election Signs", test_election_signs()))
    results.append(("Construction Signs", test_construction_signs()))
    results.append(("Bollard Signs", test_bollard_signs()))
    results.append(("Corflute Insert A-Frame", test_corflute_insert_a_frame()))
    results.append(("Metal Face A-Frame", test_metal_face_a_frame()))
    results.append(("Election Signs (Double)", test_election_signs_double_sided()))
    results.append(("Construction Signs (Metal)", test_construction_signs_metal()))
    results.append(("Backend Integration", test_backend_integration()))
    
    # Summary
    print("\n" + "=" * 48)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL GROUP 4 TESTS COMPLETE!")
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
