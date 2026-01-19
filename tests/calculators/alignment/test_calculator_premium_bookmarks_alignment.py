"""
Premium Bookmarks Calculator Alignment Tests

Tests the alignment between:
- Schema (calculator_tools.json)
- Wrapper (calculator_wrapper.py)
- Backend (PremiumBookmarks_Shopify_Calculator.py)

12 comprehensive tests covering new parameters, legacy parameters, and validation.
"""

import pytest
import sys
from pathlib import Path
from decimal import Decimal

# Add paths
implementations_path = Path(__file__).parent.parent.parent.parent / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'
sys.path.insert(0, str(implementations_path))

from calculator_wrapper import calculate_premium_bookmarks


class TestPremiumBookmarksAlignment:
    """Test suite for Premium Bookmarks calculator alignment"""
    
    def test_01_new_params_basic_success(self):
        """NEW PARAMS: Basic calculation with all new parameters works"""
        result = calculate_premium_bookmarks(
            quantity=500,
            width_mm=55,
            height_mm=200,
            paper_stock="350gsm",
            lamination="Matte"
        )
        
        assert result["success"] is True
        assert result["product_type"] == "Premium Bookmarks"
        assert result["quantity"] == 500
        assert "total_price" in result
        assert "unit_price" in result
        assert "cost_per_item" in result
        assert "breakdown" in result
        assert "specifications" in result
        print(f"✅ NEW PARAMS: Basic calculation successful - ${result['total_price']:.2f}")
    
    def test_02_legacy_celloglaze_translation(self):
        """LEGACY: celloglaze parameter translates to lamination"""
        result = calculate_premium_bookmarks(
            quantity=500,
            width_mm=55,
            height_mm=200,
            paper_stock="350gsm",
            celloglaze="Matt 1 Sided"  # Old parameter
        )
        
        assert result["success"] is True
        assert "warnings" in result
        assert any(w["deprecated"] == "celloglaze" for w in result["warnings"])
        assert any(w["translated_to"] == "Matte" for w in result["warnings"])
        print("✅ LEGACY: celloglaze → lamination translation works")
    
    def test_03_legacy_width_height(self):
        """LEGACY: width/height parameters translate to width_mm/height_mm"""
        result = calculate_premium_bookmarks(
            quantity=500,
            width=55,  # Old parameter
            height=200,  # Old parameter
            paper_stock="350gsm",
            lamination="Matte"
        )
        
        assert result["success"] is True
        assert "warnings" in result
        assert any(w["deprecated"] == "width" for w in result["warnings"])
        assert any(w["deprecated"] == "height" for w in result["warnings"])
        print("✅ LEGACY: width/height → width_mm/height_mm translation works")
    
    def test_04_legacy_vs_new_same_result(self):
        """LEGACY: Old and new parameters produce identical results"""
        result_new = calculate_premium_bookmarks(
            quantity=500,
            width_mm=55,
            height_mm=200,
            paper_stock="350gsm",
            lamination="Matte"
        )
        
        result_legacy = calculate_premium_bookmarks(
            quantity=500,
            width=55,
            height=200,
            paper_stock="350gsm",
            celloglaze="Matt 1 Sided"
        )
        
        assert result_new["success"] is True
        assert result_legacy["success"] is True
        assert result_new["total_price"] == result_legacy["total_price"]
        assert result_new["unit_price"] == result_legacy["unit_price"]
        print(f"✅ LEGACY: Price consistency verified - ${result_new['total_price']:.2f}")
    
    def test_05_quantity_enum_validation(self):
        """VALIDATION: Quantity enum values work correctly"""
        valid_quantities = [25, 50, 100, 250, 500, 750, 1000, 1250, 1500, 2000]
        
        for qty in [250, 1000, 2000]:  # Sample test
            result = calculate_premium_bookmarks(
                quantity=qty,
                width_mm=55,
                height_mm=200,
                paper_stock="350gsm",
                lamination="Matte"
            )
            assert result["success"] is True
            assert result["quantity"] == qty
        
        print(f"✅ VALIDATION: Quantity enum values work correctly")
    
    def test_06_lamination_options(self):
        """VALIDATION: All lamination options work"""
        laminations = ["None", "Matte", "Gloss"]
        
        for lam in laminations:
            result = calculate_premium_bookmarks(
                quantity=500,
                width_mm=55,
                height_mm=200,
                paper_stock="350gsm",
                lamination=lam
            )
            assert result["success"] is True
            print(f"  ✓ Lamination '{lam}' works - ${result['total_price']:.2f}")
        
        print("✅ VALIDATION: All lamination options work")
    
    def test_07_paper_stock_options(self):
        """VALIDATION: All paper stock options work"""
        stocks = ["350gsm", "300gsm", "250gsm"]
        
        for stock in stocks:
            result = calculate_premium_bookmarks(
                quantity=500,
                width_mm=55,
                height_mm=200,
                paper_stock=stock,
                lamination="Matte"
            )
            assert result["success"] is True
            print(f"  ✓ Paper stock '{stock}' works - ${result['total_price']:.2f}")
        
        print("✅ VALIDATION: All paper stock options work")
    
    def test_08_custom_dimensions(self):
        """VALIDATION: Custom width/height dimensions work"""
        test_cases = [
            {"width_mm": 50, "height_mm": 150},
            {"width_mm": 65, "height_mm": 215},
            {"width_mm": 70, "height_mm": 250}
        ]
        
        for dims in test_cases:
            result = calculate_premium_bookmarks(
                quantity=500,
                width_mm=dims["width_mm"],
                height_mm=dims["height_mm"],
                paper_stock="350gsm",
                lamination="Matte"
            )
            assert result["success"] is True
            print(f"  ✓ Size {dims['width_mm']}x{dims['height_mm']}mm - ${result['total_price']:.2f}")
        
        print("✅ VALIDATION: Custom dimensions work")
    
    def test_09_minimum_parameters(self):
        """VALIDATION: Minimum parameters with defaults work"""
        result = calculate_premium_bookmarks(
            quantity=500  # Only required parameter
        )
        
        assert result["success"] is True
        assert result["quantity"] == 500
        assert result["specifications"]["width_mm"] == 55  # Default
        assert result["specifications"]["height_mm"] == 200  # Default
        assert result["specifications"]["paper_stock"] == "350gsm"  # Default
        assert result["specifications"]["lamination"] == "Matte"  # Default
        print("✅ VALIDATION: Minimum parameters work with defaults")
    
    def test_10_price_consistency(self):
        """VALIDATION: Same parameters produce consistent pricing"""
        result1 = calculate_premium_bookmarks(
            quantity=1000,
            width_mm=55,
            height_mm=200,
            paper_stock="350gsm",
            lamination="Matte"
        )
        
        result2 = calculate_premium_bookmarks(
            quantity=1000,
            width_mm=55,
            height_mm=200,
            paper_stock="350gsm",
            lamination="Matte"
        )
        
        assert result1["success"] is True
        assert result2["success"] is True
        assert result1["total_price"] == result2["total_price"]
        assert result1["unit_price"] == result2["unit_price"]
        print(f"✅ VALIDATION: Price consistency verified - ${result1['total_price']:.2f}")
    
    def test_11_response_structure(self):
        """VALIDATION: Response has all required fields"""
        result = calculate_premium_bookmarks(
            quantity=500,
            width_mm=55,
            height_mm=200,
            paper_stock="350gsm",
            lamination="Matte"
        )
        
        assert result["success"] is True
        
        # Required fields
        required_fields = [
            "success", "product_type", "quantity", 
            "total_price", "unit_price", "cost_per_item",
            "breakdown", "specifications"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Breakdown structure
        assert isinstance(result["breakdown"], dict)
        assert len(result["breakdown"]) > 0
        
        # Specifications structure
        assert isinstance(result["specifications"], dict)
        assert "width_mm" in result["specifications"]
        assert "height_mm" in result["specifications"]
        
        print("✅ VALIDATION: Response structure correct")
    
    def test_12_size_based_pricing(self):
        """VALIDATION: Larger bookmarks cost more than smaller ones"""
        small = calculate_premium_bookmarks(
            quantity=500,
            width_mm=50,
            height_mm=150,
            paper_stock="350gsm",
            lamination="None"
        )
        
        large = calculate_premium_bookmarks(
            quantity=500,
            width_mm=70,
            height_mm=250,
            paper_stock="350gsm",
            lamination="None"
        )
        
        assert small["success"] is True
        assert large["success"] is True
        assert large["total_price"] > small["total_price"], \
            f"Large (${large['total_price']:.2f}) should cost more than small (${small['total_price']:.2f})"
        
        print(f"✅ VALIDATION: Size-based pricing works")
        print(f"   Small (50x150mm): ${small['total_price']:.2f}")
        print(f"   Large (70x250mm): ${large['total_price']:.2f}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
