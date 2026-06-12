"""
Test Election Signs Calculator (Group 4, Calculator 1)
Date: January 19, 2026
Tests the 3-part pattern implementation
"""

import sys
from pathlib import Path

# Add paths
wrapper_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'
sys.path.insert(0, str(wrapper_path))

from calculator_wrapper import calculate_election_signs

def test_election_signs():
    """Test Election Signs calculator with 4 core tests"""
    
    print("="*70)
    print("TESTING: Election Signs (Group 4, Calculator 1)")
    print("="*70)
    
    tests_passed = 0
    tests_total = 4
    
    # Test 1: New Parameters Work
    print("\n[Test 1: New Parameters Work]")
    try:
        result = calculate_election_signs(
            quantity=50,
            size="600x450",
            material="Corflute",
            sides="Single",
            artworks=1
        )
        assert result['success'] == True, f"Failed: {result.get('error')}"
        assert result['total_price'] > 0, "Price should be > 0"
        print(f"✅ PASS - Price: ${result['total_price']:.2f}")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ FAIL - {e}")
    except Exception as e:
        print(f"❌ FAIL - Unexpected error: {e}")
    
    # Test 2: Backend Defaults Work (None values)
    print("\n[Test 2: Backend Defaults Work (None values)]")
    try:
        result = calculate_election_signs(
            quantity=50
            # All other params None - should use backend defaults
        )
        assert result['success'] == True, f"Failed: {result.get('error')}"
        assert result['total_price'] > 0, "Price should be > 0"
        assert result['specifications']['size_mm'] == "600x450", "Should use default size"
        assert result['specifications']['material'] == "Corflute", "Should use default material"
        print(f"✅ PASS - Price: ${result['total_price']:.2f}, Defaults applied correctly")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ FAIL - {e}")
    except Exception as e:
        print(f"❌ FAIL - Unexpected error: {e}")
    
    # Test 3: Different Material Pricing
    print("\n[Test 3: Different Material Pricing]")
    try:
        result_corflute = calculate_election_signs(
            quantity=50,
            size="600x450",
            material="Corflute",
            sides="Single",
            artworks=1
        )
        
        result_metal = calculate_election_signs(
            quantity=50,
            size="600x450",
            material="Metal",
            sides="Single",
            artworks=1
        )
        
        assert result_corflute['success'] == True
        assert result_metal['success'] == True
        assert result_metal['total_price'] > result_corflute['total_price'], \
            "Metal should be more expensive than Corflute"
        
        print(f"✅ PASS - Corflute: ${result_corflute['total_price']:.2f}, " +
              f"Metal: ${result_metal['total_price']:.2f} (Metal more expensive)")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ FAIL - {e}")
    except Exception as e:
        print(f"❌ FAIL - Unexpected error: {e}")
    
    # Test 4: Double-sided More Expensive
    print("\n[Test 4: Double-sided More Expensive Than Single]")
    try:
        result_single = calculate_election_signs(
            quantity=50,
            size="600x450",
            material="Corflute",
            sides="Single",
            artworks=1
        )
        
        result_double = calculate_election_signs(
            quantity=50,
            size="600x450",
            material="Corflute",
            sides="Double",
            artworks=1
        )
        
        assert result_single['success'] == True
        assert result_double['success'] == True
        assert result_double['total_price'] > result_single['total_price'], \
            "Double-sided should be more expensive than single-sided"
        
        print(f"✅ PASS - Single: ${result_single['total_price']:.2f}, " +
              f"Double: ${result_double['total_price']:.2f} (Double more expensive)")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ FAIL - {e}")
    except Exception as e:
        print(f"❌ FAIL - Unexpected error: {e}")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"ELECTION SIGNS TEST SUMMARY: {tests_passed}/{tests_total} ({tests_passed/tests_total*100:.0f}%)")
    print(f"{'='*70}")
    
    if tests_passed == tests_total:
        print("🎉 ALL TESTS PASSED - Election Signs calculator validated!")
        return True
    else:
        print(f"⚠️ {tests_total - tests_passed} test(s) failed - needs fixing")
        return False

if __name__ == "__main__":
    success = test_election_signs()
    sys.exit(0 if success else 1)
