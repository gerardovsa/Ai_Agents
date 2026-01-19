"""
Calculator Alignment Test: Notepads A4
========================================

Tests schema-wrapper-backend alignment for Notepads A4 Calculator.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'))
sys.path.insert(0, str(project_root / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'))

from calculator_wrapper import calculate_notepads_a4


class TestCalculatorNotepadsA4Alignment:
    """Test schema-wrapper-backend alignment for Notepads A4 Calculator"""
    
    def test_01_new_params_basic_success(self):
        """Test using NEW correct parameter names"""
        result = calculate_notepads_a4(
            quantity=250,
            print_type="Colour",
            print_sides="Single side print",
            paper_stock="Uncoated Bond 80GSM",
            artworks=1
        )
        
        assert result["success"] == True, f"Expected success, got: {result}"
        assert "warnings" not in result, "Should not have warnings with correct params"
        assert result["total_price"] > 0, "Price should be positive"
        assert result["quantity"] == 250
    
    def test_02_new_params_variations(self):
        """Test parameter variations with correct names"""
        # Test single sided
        result1 = calculate_notepads_a4(
            quantity=100,
            print_type="Colour",
            print_sides="Single side print",
            paper_stock="Standard"
        )
        assert result1["success"] == True
        
        # Test double sided
        result2 = calculate_notepads_a4(
            quantity=100,
            print_type="Colour",
            print_sides="Double side print",
            paper_stock="Standard"
        )
        assert result2["success"] == True
        assert result2["total_price"] > result1["total_price"], "Double sided should cost more"
    
    def test_03_legacy_params_with_warnings(self):
        """Test using OLD deprecated parameter names"""
        result = calculate_notepads_a4(
            quantity=250,
            stock_type="Uncoated Bond 80GSM"  # DEPRECATED - use paper_stock
        )
        
        assert result["success"] == True, "Legacy params should still work"
        assert "warnings" in result, "Should have deprecation warnings"
        assert len(result["warnings"]) == 1, "Should have 1 warning for stock_type"
        assert result["warnings"][0]["deprecated"] == "stock_type"
        assert result["warnings"][0]["use_instead"] == "paper_stock"
    
    def test_04_legacy_vs_new_same_result(self):
        """Verify legacy and new parameters produce identical results"""
        result_new = calculate_notepads_a4(
            quantity=500,
            paper_stock="Uncoated Bond 90GSM"
        )
        
        result_legacy = calculate_notepads_a4(
            quantity=500,
            stock_type="Uncoated Bond 90GSM"  # DEPRECATED
        )
        
        assert result_new["total_price"] == result_legacy["total_price"]
    
    def test_05_quantity_validation(self):
        """Test quantity enum validation"""
        valid_quantities = [25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 750, 1000, 2000]
        
        for qty in valid_quantities:
            result = calculate_notepads_a4(quantity=qty)
            assert result["success"] == True, f"Quantity {qty} should be valid"
    
    def test_06_print_type_enum(self):
        """Test print_type enum validation"""
        result_colour = calculate_notepads_a4(quantity=100, print_type="Colour")
        assert result_colour["success"] == True
        
        result_bw = calculate_notepads_a4(quantity=100, print_type="Black & White")
        assert result_bw["success"] == True
        assert result_bw["total_price"] < result_colour["total_price"], "B&W should be cheaper"
    
    def test_07_print_sides_enum(self):
        """Test print_sides enum validation"""
        result_single = calculate_notepads_a4(quantity=100, print_sides="Single side print")
        assert result_single["success"] == True
        
        result_double = calculate_notepads_a4(quantity=100, print_sides="Double side print")
        assert result_double["success"] == True
    
    def test_08_paper_stock_options(self):
        """Test paper_stock enum values"""
        stocks = ["Uncoated Bond 80GSM", "Uncoated Bond 90GSM", "Uncoated Bond 100GSM", "Standard"]
        
        for stock in stocks:
            result = calculate_notepads_a4(quantity=100, paper_stock=stock)
            assert result["success"] == True, f"Stock '{stock}' should be valid"
    
    def test_09_artworks_parameter(self):
        """Test artworks parameter"""
        result1 = calculate_notepads_a4(quantity=100, artworks=1)
        assert result1["success"] == True
        
        result2 = calculate_notepads_a4(quantity=100, artworks=3)
        assert result2["success"] == True
        assert result2["total_price"] > result1["total_price"], "More artworks should cost more"
    
    def test_10_full_configuration(self):
        """Test full configuration with all parameters"""
        result = calculate_notepads_a4(
            quantity=500,
            print_type="Colour",
            print_sides="Double side print",
            paper_stock="Uncoated Bond 100GSM",
            artworks=2
        )
        
        assert result["success"] == True
        assert result["quantity"] == 500
        assert result["total_price"] > 0
        assert "breakdown" in result
        assert "specifications" in result
    
    def test_11_minimum_parameters(self):
        """Test with only required parameters"""
        result = calculate_notepads_a4(quantity=100)
        assert result["success"] == True
        assert result["quantity"] == 100
    
    def test_12_price_consistency(self):
        """Test that same parameters produce consistent prices"""
        result1 = calculate_notepads_a4(quantity=250, print_type="Colour", artworks=1)
        result2 = calculate_notepads_a4(quantity=250, print_type="Colour", artworks=1)
        
        assert result1["total_price"] == result2["total_price"], "Same params should give same price"
