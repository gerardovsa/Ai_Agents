"""
Corflute Signs Shopify Calculator Alignment Tests

Tests the alignment between:
- Schema (calculator_tools.json)
- Wrapper (calculator_wrapper.py)
- Backend (corflute_calculator_shopify.py)

12 comprehensive tests covering preset sizes, custom sizes, tiers, and options.
"""

import pytest
import sys
from pathlib import Path

# Add paths
implementations_path = Path(__file__).parent.parent.parent.parent / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'
sys.path.insert(0, str(implementations_path))

from calculator_wrapper import calculate_corflute_signs_shopify


class TestCorfluteSignsShopifyAlignment:
    """Test suite for Corflute Signs Shopify calculator alignment"""
    
    def test_01_preset_size_basic(self):
        """NEW PARAMS: Preset size calculation works"""
        result = calculate_corflute_signs_shopify(
            quantity=10,
            size_preset="600x900",
            thickness="5mm",
            double_sided=False
        )
        
        assert result["success"] is True
        assert result["product_type"] == "Corflute Signs (Shopify)"
        assert result["quantity"] == 10
        assert "total_price" in result
        assert "per_unit_price" in result
        assert "breakdown" in result
        assert result["breakdown"]["dimensions"] == "600mm x 900mm"
        print(f"✅ PRESET SIZE: 600x900mm, 10 units - ${result['total_price']:.2f}")
    
    def test_02_custom_size(self):
        """NEW PARAMS: Custom dimensions work"""
        result = calculate_corflute_signs_shopify(
            quantity=10,
            size_preset="custom",
            custom_width_mm=500,
            custom_height_mm=700,
            thickness="5mm"
        )
        
        assert result["success"] is True
        assert result["breakdown"]["dimensions"] == "500mm x 700mm"
        assert result["specifications"]["is_custom_size"] is True
        assert result["breakdown"]["custom_premium"] > 0  # 10% premium applied
        print(f"✅ CUSTOM SIZE: 500x700mm - ${result['total_price']:.2f} (with 10% premium)")
    
    def test_03_double_sided(self):
        """NEW PARAMS: Double-sided printing adds $6/sqm"""
        single = calculate_corflute_signs_shopify(
            quantity=10,
            size_preset="600x900",
            double_sided=False
        )
        
        double = calculate_corflute_signs_shopify(
            quantity=10,
            size_preset="600x900",
            double_sided=True
        )
        
        assert single["success"] is True
        assert double["success"] is True
        
        sqm_per_unit = double["breakdown"]["sqm_per_unit"]
        total_sqm = sqm_per_unit * 10
        expected_double_cost = total_sqm * 6  # $6/sqm
        
        assert abs(double["breakdown"]["double_sided_cost"] - expected_double_cost) < 0.01
        assert double["total_price"] > single["total_price"]
        print(f"✅ DOUBLE-SIDED: Single ${single['total_price']:.2f} → Double ${double['total_price']:.2f}")
    
    def test_04_eyelets(self):
        """NEW PARAMS: Eyelet options work"""
        no_eyelets = calculate_corflute_signs_shopify(
            quantity=10,
            size_preset="600x900",
            eyelet_option="none"
        )
        
        four_corners = calculate_corflute_signs_shopify(
            quantity=10,
            size_preset="600x900",
            eyelet_option="four_corners"
        )
        
        assert no_eyelets["success"] is True
        assert four_corners["success"] is True
        assert no_eyelets["breakdown"]["eyelet_cost"] == 0
        assert four_corners["breakdown"]["eyelet_cost"] > 0
        assert four_corners["specifications"]["eyelets"] == 4
        print(f"✅ EYELETS: None ${no_eyelets['total_price']:.2f} → 4 corners ${four_corners['total_price']:.2f}")
    
    def test_05_artworks(self):
        """NEW PARAMS: Multiple artworks (first 5 free)"""
        one_art = calculate_corflute_signs_shopify(
            quantity=10,
            size_preset="600x900",
            artworks=1
        )
        
        five_art = calculate_corflute_signs_shopify(
            quantity=10,
            size_preset="600x900",
            artworks=5
        )
        
        ten_art = calculate_corflute_signs_shopify(
            quantity=10,
            size_preset="600x900",
            artworks=10
        )
        
        assert one_art["success"] is True
        assert five_art["success"] is True
        assert ten_art["success"] is True
        
        # First 5 free
        assert one_art["breakdown"]["artwork_cost"] == 0
        assert five_art["breakdown"]["artwork_cost"] == 0
        
        # 6+ artworks cost $5 each
        assert ten_art["breakdown"]["artwork_cost"] > 0
        assert ten_art["total_price"] > five_art["total_price"]
        print(f"✅ ARTWORKS: 1 art ${one_art['total_price']:.2f}, 5 art ${five_art['total_price']:.2f}, 10 art ${ten_art['total_price']:.2f}")
    
    def test_06_thickness_3mm(self):
        """VALIDATION: 3mm thickness pricing"""
        result = calculate_corflute_signs_shopify(
            quantity=10,
            size_preset="600x900",
            thickness="3mm"
        )
        
        assert result["success"] is True
        assert result["breakdown"]["thickness"] == "3mm"
        assert result["total_price"] > 0
        print(f"✅ THICKNESS: 3mm - ${result['total_price']:.2f}")
    
    def test_07_thickness_5mm(self):
        """VALIDATION: 5mm thickness pricing (default)"""
        result = calculate_corflute_signs_shopify(
            quantity=10,
            size_preset="600x900",
            thickness="5mm"
        )
        
        assert result["success"] is True
        assert result["breakdown"]["thickness"] == "5mm"
        assert result["total_price"] > 0
        print(f"✅ THICKNESS: 5mm - ${result['total_price']:.2f}")
    
    def test_08_volume_tiers(self):
        """VALIDATION: 43-tier volume pricing discounts"""
        qty_10 = calculate_corflute_signs_shopify(
            quantity=10,
            size_preset="600x900",
            thickness="5mm"
        )
        
        qty_100 = calculate_corflute_signs_shopify(
            quantity=100,
            size_preset="600x900",
            thickness="5mm"
        )
        
        qty_1000 = calculate_corflute_signs_shopify(
            quantity=1000,
            size_preset="600x900",
            thickness="5mm"
        )
        
        assert qty_10["success"] is True
        assert qty_100["success"] is True
        assert qty_1000["success"] is True
        
        # Unit price should decrease as quantity increases
        unit_10 = qty_10["per_unit_price"]
        unit_100 = qty_100["per_unit_price"]
        unit_1000 = qty_1000["per_unit_price"]
        
        assert unit_100 < unit_10, f"100 units (${unit_100:.2f}) should be cheaper per unit than 10 (${unit_10:.2f})"
        assert unit_1000 < unit_100, f"1000 units (${unit_1000:.2f}) should be cheaper per unit than 100 (${unit_100:.2f})"
        
        print(f"✅ VOLUME TIERS:")
        print(f"   10 units: ${unit_10:.2f}/unit (total ${qty_10['total_price']:.2f})")
        print(f"   100 units: ${unit_100:.2f}/unit (total ${qty_100['total_price']:.2f})")
        print(f"   1000 units: ${unit_1000:.2f}/unit (total ${qty_1000['total_price']:.2f})")
    
    def test_09_minimum_order(self):
        """VALIDATION: $135 minimum order enforced"""
        result = calculate_corflute_signs_shopify(
            quantity=1,
            size_preset="450x600",  # Small size
            thickness="3mm"
        )
        
        assert result["success"] is True
        
        # Should apply minimum order if subtotal < $135
        if result["breakdown"]["subtotal_after_discount"] < 135:
            assert result["total_price"] == 135, "Minimum order of $135 should be applied"
            assert result["breakdown"]["minimum_order_applied"] is True
        
        print(f"✅ MINIMUM ORDER: ${result['total_price']:.2f} (minimum $135 enforced)")
    
    def test_10_discount_5_percent(self):
        """VALIDATION: 5% discount applied"""
        result = calculate_corflute_signs_shopify(
            quantity=100,
            size_preset="600x900",
            thickness="5mm"
        )
        
        assert result["success"] is True
        
        before_discount = result["breakdown"]["subtotal_before_discount"]
        after_discount = result["breakdown"]["subtotal_after_discount"]
        discount_amount = result["breakdown"]["discount_5_percent"]
        
        expected_discount = before_discount * 0.05
        expected_after = before_discount * 0.95
        
        assert abs(discount_amount - expected_discount) < 0.01, "5% discount not calculated correctly"
        assert abs(after_discount - expected_after) < 0.01, "Subtotal after discount incorrect"
        
        print(f"✅ DISCOUNT: Before ${before_discount:.2f} → Discount ${discount_amount:.2f} (5%) → After ${after_discount:.2f}")
    
    def test_11_response_structure(self):
        """VALIDATION: Response has all required fields"""
        result = calculate_corflute_signs_shopify(
            quantity=10,
            size_preset="600x900",
            thickness="5mm"
        )
        
        assert result["success"] is True
        
        # Required fields
        required_fields = [
            "success", "product_type", "quantity",
            "total_price", "per_unit_price",
            "breakdown", "specifications"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Breakdown fields
        breakdown_fields = [
            "dimensions", "thickness", "sqm_per_unit", "total_sqm",
            "tier_price_per_sqm", "base_cost", "double_sided_cost",
            "custom_premium", "eyelet_cost", "artwork_cost",
            "subtotal_before_discount", "discount_5_percent", "subtotal_after_discount"
        ]
        
        for field in breakdown_fields:
            assert field in result["breakdown"], f"Missing breakdown field: {field}"
        
        print("✅ VALIDATION: Response structure correct")
    
    def test_12_tier_pricing_consistency(self):
        """VALIDATION: Same tier = same price per sqm"""
        # Both orders should be in same tier (same total sqm)
        result1 = calculate_corflute_signs_shopify(
            quantity=10,
            size_preset="600x900",  # 0.54 sqm each = 5.4 total sqm
            thickness="5mm"
        )
        
        result2 = calculate_corflute_signs_shopify(
            quantity=20,
            size_preset="450x600",  # 0.27 sqm each = 5.4 total sqm
            thickness="5mm"
        )
        
        assert result1["success"] is True
        assert result2["success"] is True
        
        tier_price1 = result1["breakdown"]["tier_price_per_sqm"]
        tier_price2 = result2["breakdown"]["tier_price_per_sqm"]
        
        # Same total sqm should get same tier price per sqm
        assert abs(tier_price1 - tier_price2) < 0.01, \
            f"Same total sqm should get same tier price: ${tier_price1:.2f} vs ${tier_price2:.2f}"
        
        print(f"✅ TIER CONSISTENCY: Both orders ~5.4 sqm → ${tier_price1:.2f}/sqm")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
