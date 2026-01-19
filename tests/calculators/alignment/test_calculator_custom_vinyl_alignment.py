"""
Calculator Alignment Test: Custom Vinyl Stickers
=================================================
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'))
sys.path.insert(0, str(project_root / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'))

from calculator_wrapper import calculate_custom_vinyl_stickers


class TestCalculatorCustomVinylAlignment:
    """Test schema-wrapper-backend alignment for Custom Vinyl Stickers Calculator"""
    
    def test_01_new_params_basic_success(self):
        result = calculate_custom_vinyl_stickers(
            quantity=100,
            width_mm=100,
            height_mm=100,
            finish="Gloss"
        )
        assert result["success"] == True
        assert "warnings" not in result
        assert result["total_price"] > 0
    
    def test_02_legacy_params_with_warnings(self):
        result = calculate_custom_vinyl_stickers(
            quantity=100,
            width=100,     # DEPRECATED - use width_mm
            height=100     # DEPRECATED - use height_mm
        )
        assert result["success"] == True
        assert "warnings" in result
        assert len(result["warnings"]) == 2
    
    def test_03_legacy_vs_new_same_result(self):
        result_new = calculate_custom_vinyl_stickers(
            quantity=100,
            width_mm=150,
            height_mm=150
        )
        result_legacy = calculate_custom_vinyl_stickers(
            quantity=100,
            width=150,
            height=150
        )
        assert result_new["total_price"] == result_legacy["total_price"]
    
    def test_04_finish_options(self):
        result_gloss = calculate_custom_vinyl_stickers(quantity=100, finish="Gloss")
        result_matt = calculate_custom_vinyl_stickers(quantity=100, finish="Matt")
        assert result_gloss["success"] == True
        assert result_matt["success"] == True
        # Gloss is $25/m², Matt is $22/m²
        assert result_gloss["total_price"] > result_matt["total_price"]
    
    def test_05_size_variations(self):
        # Small sticker
        result_small = calculate_custom_vinyl_stickers(quantity=100, width_mm=50, height_mm=50)
        # Large sticker
        result_large = calculate_custom_vinyl_stickers(quantity=100, width_mm=200, height_mm=200)
        assert result_large["total_price"] > result_small["total_price"]
    
    def test_06_quantity_scaling(self):
        result_100 = calculate_custom_vinyl_stickers(quantity=100)
        result_500 = calculate_custom_vinyl_stickers(quantity=500)
        assert result_500["total_price"] > result_100["total_price"]
    
    def test_07_rectangular_stickers(self):
        result = calculate_custom_vinyl_stickers(
            quantity=100,
            width_mm=150,
            height_mm=75
        )
        assert result["success"] == True
    
    def test_08_circle_size_100mm(self):
        result = calculate_custom_vinyl_stickers(quantity=100, width_mm=100, height_mm=100)
        assert result["success"] == True
    
    def test_09_minimum_params(self):
        result = calculate_custom_vinyl_stickers(quantity=100)
        assert result["success"] == True
    
    def test_10_price_consistency(self):
        result1 = calculate_custom_vinyl_stickers(quantity=100, finish="Gloss")
        result2 = calculate_custom_vinyl_stickers(quantity=100, finish="Gloss")
        assert result1["total_price"] == result2["total_price"]
    
    def test_11_response_structure(self):
        result = calculate_custom_vinyl_stickers(quantity=100)
        assert "success" in result
        assert "total_price" in result
        assert "unit_price" in result
        assert "breakdown" in result
        assert "specifications" in result
    
    def test_12_area_based_pricing(self):
        # 50x50mm
        result_small = calculate_custom_vinyl_stickers(quantity=100, width_mm=50, height_mm=50)
        # 100x100mm (4x area)
        result_large = calculate_custom_vinyl_stickers(quantity=100, width_mm=100, height_mm=100)
        # Should cost significantly more (4x material)
        assert result_large["total_price"] > result_small["total_price"] * 2
