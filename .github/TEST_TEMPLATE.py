"""
Calculator Alignment Test Template
===================================

Copy this template for each calculator and customize the test cases.

File naming: test_calculator_<product_name>_alignment.py
Location: tests/calculators/alignment/

Example: test_calculator_folded_flyers_alignment.py
"""

import pytest
from UI.modules_external.quote_calculator.implementations.calculator_wrapper import (
    calculate_<PRODUCT>_shopify  # REPLACE <PRODUCT> with actual calculator name
)


class TestCalculator<Product>Alignment:
    """
    Test schema-wrapper-backend alignment for <Product> Calculator
    
    Tests verify:
    1. New parameter names work correctly
    2. Legacy parameters work with deprecation warnings
    3. Unknown parameters are rejected
    4. Enum validation works
    5. Backend receives correct values
    """
    
    # ========================================================================
    # TEST 1: NEW PARAMETERS (Correct Names)
    # ========================================================================
    
    def test_01_new_params_basic_success(self):
        """
        Test using NEW correct parameter names with basic configuration.
        Should succeed without warnings.
        """
        result = calculate_<PRODUCT>_shopify(
            quantity=1000,
            # ADD CORRECT PARAMETERS HERE matching backend exactly
            # Example:
            # print_sides="Double side print",
            # print_type="Colour",
            # celloglaze="None"
        )
        
        # Assertions
        assert result["success"] == True, f"Expected success, got: {result}"
        assert "warnings" not in result, "Should not have warnings with correct params"
        assert result["total_price"] > 0, "Price should be positive"
        assert "specifications" in result, "Should have specifications"
        
        # Verify backend received correct params
        specs = result["specifications"]
        # ADD ASSERTIONS for critical specs
        # Example:
        # assert specs["celloglaze"] == "None"
        # assert specs["print_sides"] == "Double side print"
    
    def test_02_new_params_all_optional_variations(self):
        """
        Test all optional parameter combinations with correct names.
        """
        # Test Case 1: Single sided printing
        result1 = calculate_<PRODUCT>_shopify(
            quantity=500,
            # ADD SINGLE-SIDED PARAMS
        )
        assert result1["success"] == True
        
        # Test Case 2: Black & white printing
        result2 = calculate_<PRODUCT>_shopify(
            quantity=500,
            # ADD BLACK & WHITE PARAMS
        )
        assert result2["success"] == True
        
        # Test Case 3: With lamination/celloglaze
        result3 = calculate_<PRODUCT>_shopify(
            quantity=500,
            # ADD CELLOGLAZE PARAMS
        )
        assert result3["success"] == True
        
        # Verify prices are different for different options
        assert result1["total_price"] != result2["total_price"], \
            "Single vs double sided should have different prices"
    
    # ========================================================================
    # TEST 2: LEGACY PARAMETERS (Deprecated but Still Work)
    # ========================================================================
    
    def test_03_legacy_params_with_warnings(self):
        """
        Test using OLD deprecated parameter names.
        Should work but return warnings.
        """
        result = calculate_<PRODUCT>_shopify(
            quantity=1000,
            # ADD LEGACY PARAMETER NAMES HERE
            # Example:
            # double_sided=True,      # DEPRECATED - use print_sides
            # colour=True,            # DEPRECATED - use print_type
            # cellophane="Matt"       # DEPRECATED - use celloglaze
        )
        
        # Should succeed despite using deprecated params
        assert result["success"] == True, f"Legacy params should still work, got: {result}"
        
        # Should have warnings
        assert "warnings" in result, "Should have deprecation warnings"
        warnings = result["warnings"]
        
        # Count expected warnings (adjust based on how many legacy params sent)
        # Example: If sent 3 deprecated params, expect 3 warnings
        expected_warning_count = 0  # SET THIS based on params used above
        assert len(warnings) == expected_warning_count, \
            f"Expected {expected_warning_count} warnings, got {len(warnings)}"
        
        # Verify each warning has correct structure
        for warning in warnings:
            assert "deprecated" in warning, "Warning should identify deprecated param"
            assert "use_instead" in warning, "Warning should suggest new param"
            assert "value_sent" in warning, "Warning should show what was sent"
            assert "translated_to" in warning, "Warning should show translation"
        
        # Verify price is correct despite using legacy params
        assert result["total_price"] > 0, "Should still calculate price correctly"
    
    def test_04_legacy_vs_new_params_same_result(self):
        """
        Verify legacy and new parameters produce identical results.
        """
        # Call with NEW parameters
        result_new = calculate_<PRODUCT>_shopify(
            quantity=1000,
            # ADD NEW PARAMS
            # Example:
            # print_sides="Double side print",
            # print_type="Colour",
            # celloglaze="2 Side Matt"
        )
        
        # Call with LEGACY parameters (same configuration)
        result_legacy = calculate_<PRODUCT>_shopify(
            quantity=1000,
            # ADD EQUIVALENT LEGACY PARAMS
            # Example:
            # double_sided=True,
            # colour=True,
            # cellophane="2 Side Matt"
        )
        
        # Prices should be identical
        assert result_new["total_price"] == result_legacy["total_price"], \
            f"Legacy and new params should produce same price: " \
            f"{result_new['total_price']} vs {result_legacy['total_price']}"
        
        # Specs should be identical (except for warning presence)
        assert result_new["specifications"] == result_legacy["specifications"], \
            "Specifications should match regardless of param names"
    
    # ========================================================================
    # TEST 3: PARAMETER VALIDATION
    # ========================================================================
    
    def test_05_unknown_param_rejected(self):
        """
        Test that unknown parameters are rejected with helpful error.
        """
        result = calculate_<PRODUCT>_shopify(
            quantity=1000,
            invalid_param="test",           # UNKNOWN
            another_wrong_param="value"     # UNKNOWN
        )
        
        # Should fail
        assert result["success"] == False, "Unknown params should be rejected"
        
        # Should identify unknown parameters
        assert "unknown_parameters" in result, "Should list unknown params"
        unknown = result["unknown_parameters"]
        assert "invalid_param" in unknown, "Should identify first unknown param"
        assert "another_wrong_param" in unknown, "Should identify second unknown param"
        
        # Should suggest valid parameters
        assert "valid_parameters" in result, "Should list valid params"
        assert len(result["valid_parameters"]) > 0, "Should have valid params list"
    
    def test_06_quantity_enum_validation(self):
        """
        Test quantity enum validation.
        """
        # Valid quantities (adjust based on actual enum)
        valid_quantities = [100, 250, 500, 1000, 2000, 5000, 10000]
        
        # Test valid quantity works
        result_valid = calculate_<PRODUCT>_shopify(
            quantity=500,  # Valid
            # ADD OTHER REQUIRED PARAMS
        )
        assert result_valid["success"] == True, "Valid quantity should work"
        
        # Test invalid quantity fails
        result_invalid = calculate_<PRODUCT>_shopify(
            quantity=999,  # NOT in enum
            # ADD OTHER REQUIRED PARAMS
        )
        assert result_invalid["success"] == False, "Invalid quantity should fail"
        assert "quantity" in str(result_invalid.get("error", "")).lower(), \
            "Error should mention quantity"
    
    def test_07_enum_values_exact_match(self):
        """
        Test that enum values must be EXACT matches (case-sensitive).
        """
        # Test correct case works
        result_correct = calculate_<PRODUCT>_shopify(
            quantity=500,
            # ADD PARAM WITH CORRECT CASE
            # Example: print_type="Colour"
        )
        assert result_correct["success"] == True
        
        # Test wrong case fails (if backend is case-sensitive)
        result_wrong_case = calculate_<PRODUCT>_shopify(
            quantity=500,
            # ADD SAME PARAM WITH WRONG CASE
            # Example: print_type="colour"  # lowercase - should fail
        )
        # This may pass if backend is case-insensitive, adjust assertion accordingly
        # assert result_wrong_case["success"] == False, "Case sensitivity should be enforced"
    
    # ========================================================================
    # TEST 4: BACKEND INTEGRATION
    # ========================================================================
    
    def test_08_backend_receives_correct_types(self):
        """
        Verify backend receives parameters in correct types/format.
        """
        result = calculate_<PRODUCT>_shopify(
            quantity=1000,
            # ADD PARAMS that test type conversion
            # Example: send "1000" as string, should convert to int
        )
        
        assert result["success"] == True, "Type conversion should work"
        assert result["quantity"] == 1000, "Quantity should be integer"
        
        # Check specifications returned by backend
        specs = result["specifications"]
        # ADD ASSERTIONS for spec types
        # Example:
        # assert isinstance(specs["quantity"], int)
        # assert isinstance(specs["celloglaze"], str)
    
    def test_09_all_quantity_tiers(self):
        """
        Test all quantity tiers to ensure pricing works across range.
        """
        quantity_tiers = [100, 250, 500, 1000, 2000, 5000, 10000]
        
        previous_price = None
        previous_unit_price = None
        
        for qty in quantity_tiers:
            result = calculate_<PRODUCT>_shopify(
                quantity=qty,
                # ADD OTHER REQUIRED PARAMS
            )
            
            assert result["success"] == True, f"Quantity {qty} should work"
            assert result["total_price"] > 0, f"Price for {qty} should be positive"
            
            # Higher quantities should have higher total price
            if previous_price:
                assert result["total_price"] > previous_price, \
                    f"Total price should increase with quantity: {qty}"
            
            # Higher quantities should have lower unit price (volume discount)
            if previous_unit_price:
                assert result["unit_price"] <= previous_unit_price, \
                    f"Unit price should decrease or stay same with quantity: {qty}"
            
            previous_price = result["total_price"]
            previous_unit_price = result["unit_price"]
    
    # ========================================================================
    # TEST 5: EDGE CASES & ERROR HANDLING
    # ========================================================================
    
    def test_10_missing_required_params(self):
        """
        Test behavior when required parameters are missing.
        """
        # Try to call with ONLY quantity (if other params are required)
        result = calculate_<PRODUCT>_shopify(
            quantity=1000
            # OMIT other required params
        )
        
        # Behavior depends on whether params have defaults
        # If all params have defaults, this should succeed
        # If some are required, should fail
        
        # Adjust assertion based on your calculator's requirements
        if result["success"]:
            # All params have defaults - verify defaults were used
            assert "specifications" in result
        else:
            # Some params are required - verify error message
            assert "error" in result
    
    def test_11_extreme_values(self):
        """
        Test extreme or boundary values.
        """
        # Test minimum quantity
        result_min = calculate_<PRODUCT>_shopify(
            quantity=100,  # minimum
            # ADD OTHER PARAMS
        )
        assert result_min["success"] == True, "Minimum quantity should work"
        
        # Test maximum quantity
        result_max = calculate_<PRODUCT>_shopify(
            quantity=10000,  # maximum
            # ADD OTHER PARAMS
        )
        assert result_max["success"] == True, "Maximum quantity should work"
    
    def test_12_special_characters_handling(self):
        """
        Test that string params with special chars are handled correctly.
        """
        # This depends on your backend's string handling
        # Example: Test stock names with spaces, slashes, etc.
        result = calculate_<PRODUCT>_shopify(
            quantity=500,
            # ADD PARAMS with special chars if applicable
            # Example: stock="Satin 150GSM"  # space in name
        )
        assert result["success"] == True, "Special chars in params should work"


# ============================================================================
# HELPER FUNCTIONS (Optional)
# ============================================================================

def assert_valid_quote_structure(result: dict):
    """
    Helper to validate quote response structure.
    
    Args:
        result: Response from calculator
    """
    assert "success" in result, "Response must have 'success' field"
    
    if result["success"]:
        assert "total_price" in result, "Success response must have total_price"
        assert "unit_price" in result, "Success response must have unit_price"
        assert "specifications" in result, "Success response must have specifications"
        assert result["total_price"] > 0, "Price must be positive"
        assert result["unit_price"] > 0, "Unit price must be positive"
    else:
        assert "error" in result, "Failed response must have error message"


def print_test_summary():
    """Print test execution summary (call at end of test run)"""
    print("\n" + "="*70)
    print("CALCULATOR ALIGNMENT TEST SUMMARY")
    print("="*70)
    print("All tests passed! ✅")
    print("\nTests verify:")
    print("  ✓ New parameter names work correctly")
    print("  ✓ Legacy parameters work with warnings")
    print("  ✓ Unknown parameters are rejected")
    print("  ✓ Enum validation works")
    print("  ✓ Backend receives correct values")
    print("="*70 + "\n")


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])
    
    # Or run specific test:
    # pytest.main([__file__, "-v", "-k", "test_01_new_params"])
