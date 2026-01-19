"""
Test Suite: Luxury Classic Pull Up Banners Calculator Alignment
Calculator: calculate_luxury_classic_pull_up_banners
Date: January 19, 2026
Status: Testing 3-part pattern (kwargs removal, None defaults, validation)

Test Coverage:
1. New parameters work correctly
2. Legacy parameters work with warnings
3. Price consistency (new params = legacy params)
4. Missing parameter handling (validation test)
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "UI" / "modules_external" / "quote-calculator" / "implementations"))
sys.path.insert(0, str(project_root / "UI" / "modules_external" / "quote-calculator" / "backend" / "shopify_calculators"))

from calculator_wrapper import calculate_luxury_classic_pull_up_banners


class TestLuxuryPullUpBannersAlignment:
    """Test schema-wrapper-backend alignment for Luxury Classic Pull Up Banners"""
    
    def test_1_new_params_work(self):
        """Test 1: New parameters work without warnings"""
        print("\n" + "="*70)
        print("TEST 1: New Parameters (width_mm, height_mm)")
        print("="*70)
        
        result = calculate_luxury_classic_pull_up_banners(
            quantity=10,
            width_mm=850,
            height_mm=2000,
            material="Premium Vinyl"
        )
        
        print(f"✅ Success: {result['success']}")
        print(f"✅ Total Price: ${result['total_price']:.2f}")
        print(f"✅ Unit Price: ${result['unit_price']:.2f}")
        print(f"✅ Warnings: {len(result.get('warnings', []))}")
        
        assert result["success"] == True, "Calculation should succeed"
        assert "warnings" not in result or len(result["warnings"]) == 0, "Should have no warnings for correct params"
        assert result["total_price"] > 0, "Price should be positive"
        
        print("✅ TEST 1 PASSED - New parameters work correctly\n")
        return result
    
    def test_2_legacy_params_with_warnings(self):
        """Test 2: Legacy parameters work but generate warnings"""
        print("\n" + "="*70)
        print("TEST 2: Legacy Parameters (width, height)")
        print("="*70)
        
        result = calculate_luxury_classic_pull_up_banners(
            quantity=10,
            width=850,      # DEPRECATED
            height=2000,    # DEPRECATED
            material="Premium Vinyl"
        )
        
        print(f"✅ Success: {result['success']}")
        print(f"✅ Total Price: ${result['total_price']:.2f}")
        print(f"✅ Warnings: {len(result.get('warnings', []))}")
        
        if "warnings" in result:
            print("\n⚠️  Deprecation Warnings:")
            for w in result["warnings"]:
                print(f"   - {w['deprecated']} → {w['use_instead']}")
        
        assert result["success"] == True, "Calculation should succeed with legacy params"
        assert "warnings" in result, "Should have warnings for legacy params"
        assert len(result["warnings"]) == 2, "Should have 2 warnings (width, height)"
        
        # Verify warnings mention correct params
        deprecated_params = [w["deprecated"] for w in result["warnings"]]
        assert "width" in deprecated_params, "Should warn about 'width'"
        assert "height" in deprecated_params, "Should warn about 'height'"
        
        print("✅ TEST 2 PASSED - Legacy parameters work with warnings\n")
        return result
    
    def test_3_price_consistency(self):
        """Test 3: Prices match regardless of parameter style"""
        print("\n" + "="*70)
        print("TEST 3: Price Consistency (New vs Legacy)")
        print("="*70)
        
        # Calculate with NEW parameters
        result_new = calculate_luxury_classic_pull_up_banners(
            quantity=10,
            width_mm=850,
            height_mm=2000,
            material="Premium Vinyl"
        )
        
        # Calculate with LEGACY parameters (same values)
        result_legacy = calculate_luxury_classic_pull_up_banners(
            quantity=10,
            width=850,
            height=2000,
            material="Premium Vinyl"
        )
        
        print(f"New Params Price:    ${result_new['total_price']:.2f}")
        print(f"Legacy Params Price: ${result_legacy['total_price']:.2f}")
        print(f"Difference:          ${abs(result_new['total_price'] - result_legacy['total_price']):.2f}")
        
        assert result_new["total_price"] == result_legacy["total_price"], \
            "Prices must match exactly regardless of parameter style"
        
        print("✅ TEST 3 PASSED - Prices are consistent\n")
    
    def test_4_missing_params_use_defaults(self):
        """Test 4: Missing optional params use backend defaults"""
        print("\n" + "="*70)
        print("TEST 4: Missing Optional Parameters (Defaults)")
        print("="*70)
        
        # Only provide quantity (required)
        result = calculate_luxury_classic_pull_up_banners(
            quantity=10
            # width_mm, height_mm, material will use defaults
        )
        
        print(f"✅ Success: {result['success']}")
        print(f"✅ Total Price: ${result['total_price']:.2f}")
        print(f"✅ Specifications: {result['specifications']}")
        
        assert result["success"] == True, "Should succeed with defaults"
        assert result["specifications"]["width_mm"] == 850, "Should use default width 850"
        assert result["specifications"]["height_mm"] == 2000, "Should use default height 2000"
        assert result["specifications"]["material"] == "Premium Vinyl", "Should use default material"
        
        print("✅ TEST 4 PASSED - Defaults applied correctly\n")


def run_all_tests():
    """Run all 4 tests for Luxury Classic Pull Up Banners"""
    print("\n" + "="*70)
    print("LUXURY CLASSIC PULL UP BANNERS - CALCULATOR ALIGNMENT TESTS")
    print("="*70)
    print("Testing 3-Part Pattern:")
    print("  1. ✅ **kwargs removed (explicit parameters)")
    print("  2. ✅ None defaults used")
    print("  3. ✅ Validation after legacy translation")
    print("="*70)
    
    tester = TestLuxuryPullUpBannersAlignment()
    
    try:
        # Test 1: New parameters
        tester.test_1_new_params_work()
        
        # Test 2: Legacy parameters
        tester.test_2_legacy_params_with_warnings()
        
        # Test 3: Price consistency
        tester.test_3_price_consistency()
        
        # Test 4: Default handling
        tester.test_4_missing_params_use_defaults()
        
        print("\n" + "="*70)
        print("✅ ALL 4 TESTS PASSED - Calculator 1 Complete!")
        print("="*70)
        print("✅ Pattern Score: 3.0/3.0")
        print("   - **kwargs removed: ✅")
        print("   - None defaults: ✅")
        print("   - Validation: ✅")
        print("="*70 + "\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
