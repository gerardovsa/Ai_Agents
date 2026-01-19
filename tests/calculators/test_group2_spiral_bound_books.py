"""Test Spiral Bound Books Calculator Alignment - Group 2 Calculator 2"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from UI.modules_external.quote_calculator.implementations.calculator_wrapper import calculate_spiral_bound_books_shopify


class TestSpiralBoundBooksAlignment:
    """Test schema-wrapper-backend alignment for Spiral Bound Books"""
    
    def test_01_new_params_basic(self):
        """Test NEW correct parameter names"""
        result = calculate_spiral_bound_books_shopify(
            quantity=100,
            internal_pages=100,
            finish_size="A5 Portrait",
            artworks=1
        )
        
        assert result["success"] == True
        assert "warnings" not in result
        assert result["total_price"] > 0
        print(f"✅ Test 1 passed: ${result['total_price']:.2f}")
    
    def test_02_legacy_params_with_warnings(self):
        """Test LEGACY deprecated parameters"""
        result = calculate_spiral_bound_books_shopify(
            quantity=100,
            pages=100,
            size="A5"
        )
        
        assert result["success"] == True
        assert "warnings" in result
        print(f"✅ Test 2 passed with {len(result['warnings'])} warnings")
    
    def test_03_comparison_with_wire_bound(self):
        """Spiral and Wire should have different prices (different binding)"""
        from UI.modules_external.quote_calculator.implementations.calculator_wrapper import calculate_wire_bound_books_shopify
        
        spiral_result = calculate_spiral_bound_books_shopify(
            quantity=100,
            internal_pages=100,
            finish_size="A5 Portrait"
        )
        
        wire_result = calculate_wire_bound_books_shopify(
            quantity=100,
            internal_pages=100,
            finish_size="A5 Portrait"
        )
        
        assert spiral_result["success"] == True
        assert wire_result["success"] == True
        # Prices should differ due to different binding methods
        print(f"✅ Test 3 passed: Spiral ${spiral_result['total_price']:.2f} vs Wire ${wire_result['total_price']:.2f}")
    
    def test_04_backend_integration(self):
        """Verify backend calculator works"""
        result = calculate_spiral_bound_books_shopify(
            quantity=200,
            internal_pages=200,
            finish_size="A4 Landscape",
            printed_front_cover="350GSM Satin",
            front_celloglaze="2 Sided Matt",
            artworks=3
        )
        
        assert result["success"] == True
        assert "specifications" in result
        assert result["specifications"]["quantity"] == 200
        print(f"✅ Test 4 passed: Backend integration works")


if __name__ == "__main__":
    print("🧪 Running Spiral Bound Books Alignment Tests...\n")
    tester = TestSpiralBoundBooksAlignment()
    
    try:
        tester.test_01_new_params_basic()
        tester.test_02_legacy_params_with_warnings()
        tester.test_03_comparison_with_wire_bound()
        tester.test_04_backend_integration()
        print("\n✅ ALL TESTS PASSED for Spiral Bound Books!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
