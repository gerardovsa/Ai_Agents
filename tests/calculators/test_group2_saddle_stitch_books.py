"""Test Saddle Stitch Books Calculator Alignment - Group 2 Calculator 4"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from UI.modules_external.quote_calculator.implementations.calculator_wrapper import calculate_saddle_stitch_books_shopify


class TestSaddleStitchBooksAlignment:
    """Test schema-wrapper-backend alignment for Saddle Stitch Books"""
    
    def test_01_new_params_basic(self):
        """Test NEW correct parameter names"""
        result = calculate_saddle_stitch_books_shopify(
            quantity=100,
            printed_pages="16pp",
            finish_size="A4 Portrait"
        )
        
        assert result["success"] == True
        assert "warnings" not in result
        assert result["total_price"] > 0
        print(f"✅ Test 1 passed: ${result['total_price']:.2f}")
    
    def test_02_legacy_params_with_warnings(self):
        """Test LEGACY deprecated parameters"""
        result = calculate_saddle_stitch_books_shopify(
            quantity=100,
            pages=16,  # DEPRECATED - converted to "16pp"
            size="A4",  # DEPRECATED - converted to "A4 Portrait"
            hard_cover=True  # DEPRECATED - converted to "Hard Cover"
        )
        
        assert result["success"] == True
        assert "warnings" in result
        assert len(result["warnings"]) >= 3
        print(f"✅ Test 2 passed with {len(result['warnings'])} warnings")
    
    def test_03_quantity_enum_validation(self):
        """Test quantity enum (25, 50, 75, 100, etc.)"""
        # Valid quantities
        for qty in [25, 50, 100, 250, 500, 1000]:
            result = calculate_saddle_stitch_books_shopify(
                quantity=qty,
                printed_pages="20pp"
            )
            assert result["success"] == True
        
        print(f"✅ Test 3 passed: Quantity enum validation works")
    
    def test_04_page_count_options(self):
        """Test all page count options (8pp to 48pp)"""
        for pages in ["8pp", "16pp", "24pp", "32pp", "48pp"]:
            result = calculate_saddle_stitch_books_shopify(
                quantity=100,
                printed_pages=pages
            )
            assert result["success"] == True
        
        print(f"✅ Test 4 passed: All page counts work")
    
    def test_05_cover_option_comparison(self):
        """Test Hard Cover vs Self Cover pricing"""
        result_hard = calculate_saddle_stitch_books_shopify(
            quantity=100,
            printed_pages="20pp",
            cover_option="Hard Cover"
        )
        
        result_self = calculate_saddle_stitch_books_shopify(
            quantity=100,
            printed_pages="20pp",
            cover_option="Self Cover"
        )
        
        assert result_hard["success"] == True
        assert result_self["success"] == True
        # Hard cover should cost more
        assert result_hard["total_price"] > result_self["total_price"]
        print(f"✅ Test 5 passed: Hard ${result_hard['total_price']:.2f} > Self ${result_self['total_price']:.2f}")


if __name__ == "__main__":
    print("🧪 Running Saddle Stitch Books Alignment Tests...\n")
    tester = TestSaddleStitchBooksAlignment()
    
    try:
        tester.test_01_new_params_basic()
        tester.test_02_legacy_params_with_warnings()
        tester.test_03_quantity_enum_validation()
        tester.test_04_page_count_options()
        tester.test_05_cover_option_comparison()
        print("\n✅ ALL TESTS PASSED for Saddle Stitch Books!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
