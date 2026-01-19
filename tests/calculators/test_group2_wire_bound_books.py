"""Test Wire Bound Books Calculator Alignment - Group 2 Calculator 1"""
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from UI.modules_external.quote_calculator.implementations.calculator_wrapper import calculate_wire_bound_books_shopify


class TestWireBoundBooksAlignment:
    """Test schema-wrapper-backend alignment for Wire Bound Books"""
    
    def test_01_new_params_basic(self):
        """Test NEW correct parameter names"""
        result = calculate_wire_bound_books_shopify(
            quantity=100,
            internal_pages=100,
            finish_size="A5 Portrait",
            printed_front_cover="300GSM Satin",
            front_celloglaze="None",
            internal_stock="Uncoated Bond 100GSM",
            artworks=1
        )
        
        assert result["success"] == True
        assert "warnings" not in result
        assert result["total_price"] > 0
        print(f"✅ Test 1 passed: ${result['total_price']:.2f}")
    
    def test_02_legacy_params_with_warnings(self):
        """Test LEGACY deprecated parameters"""
        result = calculate_wire_bound_books_shopify(
            quantity=100,
            pages=100,  # DEPRECATED - use internal_pages
            size="A5",  # DEPRECATED - use finish_size
            cover_stock="300GSM Satin",  # DEPRECATED - use printed_front_cover
            inner_stock="100GSM Uncoated"  # DEPRECATED - use internal_stock
        )
        
        assert result["success"] == True
        assert "warnings" in result
        assert len(result["warnings"]) >= 3
        print(f"✅ Test 2 passed with {len(result['warnings'])} warnings")
    
    def test_03_quantity_validation(self):
        """Test quantity works (no enum restriction for books)"""
        result = calculate_wire_bound_books_shopify(
            quantity=50,  # Any quantity should work
            internal_pages=50,
            finish_size="A4 Portrait"
        )
        
        assert result["success"] == True
        print(f"✅ Test 3 passed: Quantity 50 works")
    
    def test_04_all_cover_options(self):
        """Test all cover configuration options"""
        result = calculate_wire_bound_books_shopify(
            quantity=100,
            internal_pages=100,
            finish_size="A5 Portrait",
            printed_front_cover="350GSM Satin",
            front_cover_print="2pp Colour",
            front_celloglaze="2 Sided Gloss",
            outer_front_cover="Clear PVC",
            printed_back_cover="350GSM Satin",
            back_cover_print="2pp Colour",
            back_celloglaze="2 Sided Gloss",
            outer_back_cover="Clear PVC",
            internal_stock="Satin 150GSM",
            internal_print="Full Colour",
            artworks=2
        )
        
        assert result["success"] == True
        assert result["total_price"] > 0
        print(f"✅ Test 4 passed: Full cover config works")
    
    def test_05_backend_integration(self):
        """Verify backend calculator actually calculates"""
        result = calculate_wire_bound_books_shopify(
            quantity=250,
            internal_pages=150,
            finish_size="A4 Portrait",
            artworks=1
        )
        
        assert result["success"] == True
        assert "breakdown" in result
        assert "specifications" in result
        assert result["specifications"]["quantity"] == 250
        assert result["specifications"]["internal_pages"] == 150
        print(f"✅ Test 5 passed: Backend integration works")


if __name__ == "__main__":
    print("🧪 Running Wire Bound Books Alignment Tests...\n")
    tester = TestWireBoundBooksAlignment()
    
    try:
        tester.test_01_new_params_basic()
        tester.test_02_legacy_params_with_warnings()
        tester.test_03_quantity_validation()
        tester.test_04_all_cover_options()
        tester.test_05_backend_integration()
        print("\n✅ ALL TESTS PASSED for Wire Bound Books!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
