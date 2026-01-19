"""
Calculator Alignment Tests - Folded Flyers Shopify
===================================================

Tests parameter alignment between:
- Schema (calculator_tools.json)
- Wrapper (calculator_wrapper.py)
- Backend (FoldedFlyers_Shopify_Calculator.py)

Author: AI Agent
Date: January 19, 2026
Status: Calculator 1 of 30 - Group 1 (Priority)
"""

import pytest
import sys
from pathlib import Path
from decimal import Decimal

# Add project root and calculator path to Python path
project_root = Path(__file__).resolve().parent.parent.parent
calculator_impl_path = project_root / "UI" / "modules_external" / "quote-calculator" / "implementations"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(calculator_impl_path))

# Import directly from calculator_wrapper
from calculator_wrapper import calculate_folded_flyers_shopify


class TestFoldedFlyersParameterAlignment:
    """Test correct parameter names work (no legacy parameters)"""
    
    def test_new_parameters_basic_quote(self):
        """Test 1: Basic quote with NEW parameter names (print_type, folding, celloglaze)"""
        result = calculate_folded_flyers_shopify(
            quantity=1000,
            size="A4",
            stock="Satin 300GSM",
            double_sided=True,
            print_type="Colour",           # ✅ NEW NAME
            folding="Double Fold",          # ✅ NEW NAME
            artworks=1,                     # ✅ ADDED PARAM
            celloglaze="2 Side Matt"        # ✅ NEW NAME (not cellophane)
        )
        
        assert result["success"] is True
        assert result["product_type"] == "Folded Flyers"
        assert result["quantity"] == 1000
        assert result["total_price"] > 0
        assert "deprecation_warnings" not in result  # No warnings - using new params
        assert result["specifications"]["celloglaze"] == "2 Side Matt"
        assert result["specifications"]["fold_type"] == "Double Fold"
        assert result["specifications"]["print_type"] == "Colour"
    
    def test_new_parameters_no_celloglaze(self):
        """Test 2: Quote with print_type='Black & White' and no celloglaze"""
        result = calculate_folded_flyers_shopify(
            quantity=500,
            size="A5",
            stock="Uncoated Bond 80GSM",
            double_sided=False,
            print_type="Black & White",     # ✅ NEW NAME
            folding="Single Fold",
            artworks=2,
            celloglaze="None"
        )
        
        assert result["success"] is True
        assert result["specifications"]["print_type"] == "Black & White"
        assert result["specifications"]["celloglaze"] == "None"
        assert result["specifications"]["artworks"] == 2
        assert "deprecation_warnings" not in result
    
    def test_new_parameters_all_combinations(self):
        """Test 3: Test all fold types with new parameter names"""
        for fold in ["Single Fold", "Double Fold", "Triple Fold"]:
            result = calculate_folded_flyers_shopify(
                quantity=250,
                size="A4",
                stock="Satin 150GSM",
                print_type="Colour",
                folding=fold,               # ✅ NEW NAME
                celloglaze="1 Side Gloss"
            )
            assert result["success"] is True
            assert result["specifications"]["fold_type"] == fold


class TestFoldedFlyersLegacyParameters:
    """Test legacy parameters still work with deprecation warnings"""
    
    def test_legacy_colour_parameter(self):
        """Test 4: Legacy 'colour' parameter translates to 'print_type' with warning"""
        result = calculate_folded_flyers_shopify(
            quantity=1000,
            size="A4",
            stock="Satin 300GSM",
            colour=True  # ⚠️ LEGACY PARAM (should translate to print_type="Colour")
        )
        
        assert result["success"] is True
        assert "deprecation_warnings" in result
        
        # Check warning details
        warnings = result["deprecation_warnings"]
        assert len(warnings) >= 1
        
        colour_warning = next(w for w in warnings if w["deprecated_parameter"] == "colour")
        assert colour_warning["use_instead"] == "print_type"
        assert colour_warning["value_sent"] is True
        assert colour_warning["translated_to"] == "Colour"
        
        # Verify actual result uses translated value
        assert result["specifications"]["print_type"] == "Colour"
    
    def test_legacy_fold_type_parameter(self):
        """Test 5: Legacy 'fold_type' parameter translates to 'folding' with warning"""
        result = calculate_folded_flyers_shopify(
            quantity=500,
            size="A5",
            stock="Satin 150GSM",
            fold_type="Triple Fold"  # ⚠️ LEGACY PARAM (should translate to folding)
        )
        
        assert result["success"] is True
        assert "deprecation_warnings" in result
        
        warnings = result["deprecation_warnings"]
        fold_warning = next(w for w in warnings if w["deprecated_parameter"] == "fold_type")
        assert fold_warning["use_instead"] == "folding"
        assert fold_warning["translated_to"] == "Triple Fold"
        
        assert result["specifications"]["fold_type"] == "Triple Fold"
    
    def test_legacy_cellophane_parameter(self):
        """Test 6: Legacy 'cellophane' parameter translates to 'celloglaze' with warning"""
        result = calculate_folded_flyers_shopify(
            quantity=1000,
            size="A4",
            stock="Satin 300GSM",
            cellophane="Matt"  # ⚠️ LEGACY PARAM (should translate to celloglaze="2 Side Matt")
        )
        
        assert result["success"] is True
        assert "deprecation_warnings" in result
        
        warnings = result["deprecation_warnings"]
        cello_warning = next(w for w in warnings if w["deprecated_parameter"] == "cellophane")
        assert cello_warning["use_instead"] == "celloglaze"
        assert cello_warning["value_sent"] == "Matt"
        assert cello_warning["translated_to"] == "2 Side Matt"
        
        # Verify backend received correct translated value
        assert result["specifications"]["celloglaze"] == "2 Side Matt"
    
    def test_legacy_all_parameters_together(self):
        """Test 7: All legacy parameters together (colour + fold_type + cellophane)"""
        result = calculate_folded_flyers_shopify(
            quantity=1000,
            size="A4",
            stock="Satin 300GSM",
            colour=False,              # ⚠️ LEGACY (should → print_type="Black & White")
            fold_type="Double Fold",   # ⚠️ LEGACY (should → folding="Double Fold")
            cellophane="Gloss"         # ⚠️ LEGACY (should → celloglaze="2 Side Gloss")
        )
        
        assert result["success"] is True
        assert "deprecation_warnings" in result
        assert len(result["deprecation_warnings"]) == 3  # All 3 legacy params
        
        # Verify translations worked
        assert result["specifications"]["print_type"] == "Black & White"
        assert result["specifications"]["fold_type"] == "Double Fold"
        assert result["specifications"]["celloglaze"] == "2 Side Gloss"


class TestFoldedFlyersValidation:
    """Test validation and error handling"""
    
    def test_artworks_parameter_required(self):
        """Test 8: Artworks parameter defaults to 1 if not provided"""
        result = calculate_folded_flyers_shopify(
            quantity=500,
            size="A4",
            stock="Satin 150GSM"
            # artworks not provided - should default to 1
        )
        
        assert result["success"] is True
        assert result["specifications"]["artworks"] == 1
    
    def test_artworks_multiple_designs(self):
        """Test 9: Multiple artworks increases setup cost"""
        result_1_artwork = calculate_folded_flyers_shopify(
            quantity=1000,
            size="A4",
            stock="Satin 300GSM",
            artworks=1
        )
        
        result_5_artworks = calculate_folded_flyers_shopify(
            quantity=1000,
            size="A4",
            stock="Satin 300GSM",
            artworks=5
        )
        
        # 5 artworks should cost more due to setup fees ($15 per extra artwork)
        assert result_5_artworks["total_price"] > result_1_artwork["total_price"]
        price_diff = result_5_artworks["total_price"] - result_1_artwork["total_price"]
        # Should be ~$60-$70 more (4 extra artworks × $15 setup + GST)
        assert 60 < price_diff < 80
    
    def test_celloglaze_changes_price(self):
        """Test 10: Celloglaze adds cost vs no celloglaze"""
        result_no_cello = calculate_folded_flyers_shopify(
            quantity=1000,
            size="A4",
            stock="Satin 300GSM",
            celloglaze="None"
        )
        
        result_with_cello = calculate_folded_flyers_shopify(
            quantity=1000,
            size="A4",
            stock="Satin 300GSM",
            celloglaze="2 Side Matt"
        )
        
        # Celloglaze should add setup ($16) + per-sheet cost (0.38 × sheets)
        assert result_with_cello["total_price"] > result_no_cello["total_price"]
        assert result_with_cello["specifications"]["celloglaze"] == "2 Side Matt"


class TestFoldedFlyersEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_minimum_quantity(self):
        """Test 11: Minimum quantity (100) works correctly"""
        result = calculate_folded_flyers_shopify(
            quantity=100,
            size="A5",
            stock="Satin 150GSM"
        )
        
        assert result["success"] is True
        assert result["quantity"] == 100
    
    def test_maximum_quantity(self):
        """Test 12: Maximum quantity (10000) works correctly"""
        result = calculate_folded_flyers_shopify(
            quantity=10000,
            size="A4",
            stock="Satin 300GSM"
        )
        
        assert result["success"] is True
        assert result["quantity"] == 10000
        # High quantity should have better unit price
        unit_price = result["unit_price"]
        assert unit_price > 0
    
    def test_6pp_a4_special_size(self):
        """Test 13: Special 6pp A4 size (0.5 items per sheet)"""
        result = calculate_folded_flyers_shopify(
            quantity=1000,
            size="6pp A4",
            stock="Satin 300GSM",
            folding="Double Fold"
        )
        
        assert result["success"] is True
        assert result["specifications"]["finish_size"] == "6pp A4 - 630mm x 297mm"
        # 6pp A4 requires 2 sheets per item (0.5 items per sheet)
        assert result["specifications"]["items_per_sheet"] == 0.5


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
