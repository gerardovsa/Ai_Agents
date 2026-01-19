"""Test Spiral Books Simple Calculator Alignment - Group 2 Calculator 5"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from UI.modules_external.quote_calculator.implementations.calculator_wrapper import (
    calculate_spiral_books_simple_shopify,
    calculate_spiral_bound_books_shopify
)


class TestSpiralBooksSimpleAlignment:
    """Test schema-wrapper-backend alignment for Spiral Books Simple (Alias)"""
    
    def test_01_alias_works(self):
        """Test that Simple alias calls Spiral Bound correctly"""
        result = calculate_spiral_books_simple_shopify(
            quantity=100,
            internal_pages=100,
            finish_size="A5 Portrait"
        )
        
        assert result["success"] == True
        assert result["total_price"] > 0
        print(f"✅ Test 1 passed: Alias works ${result['total_price']:.2f}")
    
    def test_02_identical_to_spiral_bound(self):
        """Test that Simple produces same results as Spiral Bound"""
        simple_result = calculate_spiral_books_simple_shopify(
            quantity=100,
            internal_pages=100,
            finish_size="A5 Portrait",
            artworks=1
        )
        
        spiral_result = calculate_spiral_bound_books_shopify(
            quantity=100,
            internal_pages=100,
            finish_size="A5 Portrait",
            artworks=1
        )
        
        assert simple_result["success"] == True
        assert spiral_result["success"] == True
        assert simple_result["total_price"] == spiral_result["total_price"]
        print(f"✅ Test 2 passed: Simple = Spiral Bound pricing")
    
    def test_03_simplified_parameters(self):
        """Test that simplified interface works"""
        result = calculate_spiral_books_simple_shopify(
            quantity=200,
            internal_pages=150,
            finish_size="A4 Portrait",
            printed_front_cover="300GSM Satin",
            internal_stock="Satin 128GSM",
            artworks=2
        )
        
        assert result["success"] == True
        assert "specifications" in result
        print(f"✅ Test 3 passed: Simplified interface works")
    
    def test_04_backend_integration(self):
        """Verify backend calculator works through alias"""
        result = calculate_spiral_books_simple_shopify(
            quantity=250,
            internal_pages=200,
            finish_size="A4 Landscape"
        )
        
        assert result["success"] == True
        assert "breakdown" in result
        assert result["specifications"]["quantity"] == 250
        print(f"✅ Test 4 passed: Backend integration through alias works")


if __name__ == "__main__":
    print("🧪 Running Spiral Books Simple Alignment Tests...\n")
    tester = TestSpiralBooksSimpleAlignment()
    
    try:
        tester.test_01_alias_works()
        tester.test_02_identical_to_spiral_bound()
        tester.test_03_simplified_parameters()
        tester.test_04_backend_integration()
        print("\n✅ ALL TESTS PASSED for Spiral Books Simple!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
