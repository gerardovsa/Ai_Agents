"""
Calculator Alignment Test: Notepads A5
========================================
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'))
sys.path.insert(0, str(project_root / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'))

from calculator_wrapper import calculate_notepads_a5


class TestCalculatorNotepadsA5Alignment:
    """Test schema-wrapper-backend alignment for Notepads A5 Calculator"""
    
    def test_01_new_params_basic_success(self):
        result = calculate_notepads_a5(
            quantity=250,
            print_type="Colour",
            print_sides="Single side print",
            paper_stock="Uncoated Bond 80GSM",
            artworks=1
        )
        assert result["success"] == True
        assert "warnings" not in result
        assert result["total_price"] > 0
    
    def test_02_legacy_params_with_warnings(self):
        result = calculate_notepads_a5(
            quantity=250,
            stock_type="Uncoated Bond 80GSM"
        )
        assert result["success"] == True
        assert "warnings" in result
    
    def test_03_print_variations(self):
        result_single = calculate_notepads_a5(quantity=100, print_sides="Single side print")
        result_double = calculate_notepads_a5(quantity=100, print_sides="Double side print")
        assert result_double["total_price"] > result_single["total_price"]
    
    def test_04_quantity_enum(self):
        for qty in [25, 50, 100, 250, 500, 1000]:
            result = calculate_notepads_a5(quantity=qty)
            assert result["success"] == True
    
    def test_05_paper_stock_options(self):
        stocks = ["Uncoated Bond 80GSM", "Uncoated Bond 90GSM", "Standard"]
        for stock in stocks:
            result = calculate_notepads_a5(quantity=100, paper_stock=stock)
            assert result["success"] == True
    
    def test_06_artworks_pricing(self):
        result1 = calculate_notepads_a5(quantity=100, artworks=1)
        result2 = calculate_notepads_a5(quantity=100, artworks=3)
        assert result2["total_price"] > result1["total_price"]
    
    def test_07_colour_vs_bw(self):
        result_colour = calculate_notepads_a5(quantity=100, print_type="Colour")
        result_bw = calculate_notepads_a5(quantity=100, print_type="Black & White")
        assert result_bw["total_price"] < result_colour["total_price"]
    
    def test_08_full_configuration(self):
        result = calculate_notepads_a5(
            quantity=500,
            print_type="Colour",
            print_sides="Double side print",
            paper_stock="Uncoated Bond 100GSM",
            artworks=2
        )
        assert result["success"] == True
        assert result["quantity"] == 500
    
    def test_09_minimum_params(self):
        result = calculate_notepads_a5(quantity=100)
        assert result["success"] == True
    
    def test_10_price_consistency(self):
        result1 = calculate_notepads_a5(quantity=250)
        result2 = calculate_notepads_a5(quantity=250)
        assert result1["total_price"] == result2["total_price"]
    
    def test_11_legacy_vs_new(self):
        result_new = calculate_notepads_a5(quantity=100, paper_stock="Standard")
        result_legacy = calculate_notepads_a5(quantity=100, stock_type="Standard")
        assert result_new["total_price"] == result_legacy["total_price"]
    
    def test_12_response_structure(self):
        result = calculate_notepads_a5(quantity=100)
        assert "success" in result
        assert "total_price" in result
        assert "unit_price" in result
        assert "breakdown" in result
        assert "specifications" in result
