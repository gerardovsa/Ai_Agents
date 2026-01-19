"""
Calculator Alignment Test: Custom Poster Printing
==================================================
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'))
sys.path.insert(0, str(project_root / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'))

from calculator_wrapper import calculate_custom_poster_printing


class TestCalculatorCustomPosterAlignment:
    """Test schema-wrapper-backend alignment for Custom Poster Printing Calculator"""
    
    def test_01_new_params_basic_success(self):
        result = calculate_custom_poster_printing(
            quantity=50,
            width_mm=420,
            height_mm=594,
            paper_stock="150gsm"
        )
        assert result["success"] == True
        assert "warnings" not in result
        assert result["total_price"] > 0
    
    def test_02_legacy_params_with_warnings(self):
        result = calculate_custom_poster_printing(
            quantity=50,
            width=420,     # DEPRECATED - use width_mm
            height=594     # DEPRECATED - use height_mm
        )
        assert result["success"] == True
        assert "warnings" in result
        assert len(result["warnings"]) == 2
    
    def test_03_legacy_vs_new_same_result(self):
        result_new = calculate_custom_poster_printing(
            quantity=100,
            width_mm=420,
            height_mm=594
        )
        result_legacy = calculate_custom_poster_printing(
            quantity=100,
            width=420,
            height=594
        )
        assert result_new["total_price"] == result_legacy["total_price"]
    
    def test_04_size_variations(self):
        # A3 size
        result_a3 = calculate_custom_poster_printing(quantity=50, width_mm=420, height_mm=594)
        # A2 size (larger)
        result_a2 = calculate_custom_poster_printing(quantity=50, width_mm=594, height_mm=841)
        assert result_a2["total_price"] > result_a3["total_price"], "Larger size should cost more"
    
    def test_05_quantity_scaling(self):
        result_50 = calculate_custom_poster_printing(quantity=50)
        result_100 = calculate_custom_poster_printing(quantity=100)
        assert result_100["total_price"] > result_50["total_price"]
    
    def test_06_paper_stock_options(self):
        result = calculate_custom_poster_printing(quantity=50, paper_stock="150gsm")
        assert result["success"] == True
    
    def test_07_custom_dimensions(self):
        result = calculate_custom_poster_printing(
            quantity=50,
            width_mm=300,
            height_mm=400
        )
        assert result["success"] == True
    
    def test_08_large_format(self):
        result = calculate_custom_poster_printing(
            quantity=25,
            width_mm=841,   # A1
            height_mm=1189
        )
        assert result["success"] == True
    
    def test_09_minimum_params(self):
        result = calculate_custom_poster_printing(quantity=50)
        assert result["success"] == True
    
    def test_10_price_consistency(self):
        result1 = calculate_custom_poster_printing(quantity=50, width_mm=420, height_mm=594)
        result2 = calculate_custom_poster_printing(quantity=50, width_mm=420, height_mm=594)
        assert result1["total_price"] == result2["total_price"]
    
    def test_11_response_structure(self):
        result = calculate_custom_poster_printing(quantity=50)
        assert "success" in result
        assert "total_price" in result
        assert "unit_price" in result
        assert "breakdown" in result
        assert "specifications" in result
    
    def test_12_area_based_pricing(self):
        # Small poster
        result_small = calculate_custom_poster_printing(quantity=100, width_mm=200, height_mm=300)
        # Large poster
        result_large = calculate_custom_poster_printing(quantity=100, width_mm=600, height_mm=900)
        assert result_large["total_price"] > result_small["total_price"]
