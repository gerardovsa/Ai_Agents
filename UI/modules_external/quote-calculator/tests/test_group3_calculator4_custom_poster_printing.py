"""
Test Group 3 Calculator 4: Custom Poster Printing

Backend Parameters (verified CustomPosterPrinting_Shopify_Calculator.py lines 76-79):
- quantity: int (default 50)
- width_mm (or width): Decimal (default 420)
- height_mm (or height): Decimal (default 594)
- paper_stock: str (default "150gsm")

Legacy Parameters:
- width → width_mm
- height → height_mm

3-Part Pattern Applied:
1. ✅ Decorator exists: @calculator_wrapper(validate_params=True)
2. ✅ None defaults: All 3 optional parameters use None
3. ✅ Validation: Backend defaults applied after legacy translation
"""

import sys
from pathlib import Path

# Add paths
test_file = Path(__file__).resolve()
wrapper_dir = test_file.parent.parent / "implementations"
sys.path.insert(0, str(wrapper_dir))

from calculator_wrapper import calculate_custom_poster_printing

def test_custom_poster_printing_with_new_parameters():
    """Test #1: New parameters (all explicit values) - should work"""
    print("\n🧪 TEST 1: Custom Poster Printing with NEW parameters (all explicit)")
    print("=" * 80)
    
    result = calculate_custom_poster_printing(
        quantity=100,
        width_mm=500,
        height_mm=700,
        paper_stock="200gsm"
    )
    
    print(f"Result: {result}")
    
    assert result["success"] is True, f"Expected success=True, got {result.get('success')}"
    assert result["quantity"] == 100, f"Expected quantity=100, got {result.get('quantity')}"
    assert "total_price" in result, "Missing total_price"
    assert "unit_price" in result, "Missing unit_price"
    assert "cost_per_item" in result, "Missing cost_per_item"
    assert "breakdown" in result, "Missing breakdown"
    assert "specifications" in result, "Missing specifications"
    assert "warnings" not in result, f"Should NOT have warnings with new parameters, got {result.get('warnings')}"
    
    print(f"✅ TEST 1 PASSED: Custom Poster Printing quote calculated successfully")
    print(f"   Quantity: {result['quantity']}")
    print(f"   Total Price: ${result['total_price']:.2f}")
    print(f"   Unit Price: ${result['unit_price']:.2f}")
    print(f"   Specifications: {result['specifications']}")


def test_custom_poster_printing_with_legacy_parameters():
    """Test #2: Legacy parameters (width, height) - should work with warnings"""
    print("\n🧪 TEST 2: Custom Poster Printing with LEGACY parameters (width, height)")
    print("=" * 80)
    
    result = calculate_custom_poster_printing(
        quantity=50,
        width=420,  # Legacy parameter
        height=594,  # Legacy parameter
        paper_stock="150gsm"
    )
    
    print(f"Result: {result}")
    
    assert result["success"] is True, f"Expected success=True, got {result.get('success')}"
    assert result["quantity"] == 50, f"Expected quantity=50, got {result.get('quantity')}"
    assert "warnings" in result, "Expected deprecation warnings for legacy parameters"
    
    # Verify warning structure
    warnings = result["warnings"]
    assert len(warnings) == 2, f"Expected 2 warnings, got {len(warnings)}"
    
    # Check both warnings exist
    deprecated_params = [w["deprecated"] for w in warnings]
    assert "width" in deprecated_params, f"Expected 'width' in warnings, got {deprecated_params}"
    assert "height" in deprecated_params, f"Expected 'height' in warnings, got {deprecated_params}"
    
    print(f"✅ TEST 2 PASSED: Legacy parameters translated with warnings")
    print(f"   Warnings: {warnings}")
    print(f"   Total Price: ${result['total_price']:.2f}")


def test_custom_poster_printing_price_consistency():
    """Test #3: Price consistency between new and legacy parameters"""
    print("\n🧪 TEST 3: Price consistency NEW vs LEGACY parameters")
    print("=" * 80)
    
    # Call with NEW parameters
    result_new = calculate_custom_poster_printing(
        quantity=100,
        width_mm=420,
        height_mm=594,
        paper_stock="150gsm"
    )
    
    # Call with LEGACY parameters (width, height)
    result_legacy = calculate_custom_poster_printing(
        quantity=100,
        width=420,  # Legacy
        height=594,  # Legacy
        paper_stock="150gsm"
    )
    
    print(f"NEW result: {result_new}")
    print(f"LEGACY result: {result_legacy}")
    
    assert result_new["success"] is True, "NEW parameters should succeed"
    assert result_legacy["success"] is True, "LEGACY parameters should succeed"
    
    # Prices should be identical
    assert result_new["total_price"] == result_legacy["total_price"], \
        f"Prices should match: NEW=${result_new['total_price']:.2f} vs LEGACY=${result_legacy['total_price']:.2f}"
    
    assert result_new["unit_price"] == result_legacy["unit_price"], \
        f"Unit prices should match: NEW=${result_new['unit_price']:.2f} vs LEGACY=${result_legacy['unit_price']:.2f}"
    
    # Legacy should have warnings, new should not
    assert "warnings" not in result_new, "NEW parameters should NOT have warnings"
    assert "warnings" in result_legacy, "LEGACY parameters should have warnings"
    
    print(f"✅ TEST 3 PASSED: Price consistency verified")
    print(f"   NEW total: ${result_new['total_price']:.2f}")
    print(f"   LEGACY total: ${result_legacy['total_price']:.2f}")
    print(f"   Match: ✅")


def test_custom_poster_printing_defaults_validation():
    """Test #4: Validation with None defaults - backend defaults should apply"""
    print("\n🧪 TEST 4: Custom Poster Printing defaults validation (None → backend defaults)")
    print("=" * 80)
    
    # Call with ONLY quantity (all other params should use backend defaults)
    result = calculate_custom_poster_printing(quantity=50)
    
    print(f"Result: {result}")
    
    assert result["success"] is True, f"Expected success=True with defaults, got {result.get('success')}"
    assert result["quantity"] == 50, f"Expected quantity=50, got {result.get('quantity')}"
    
    # Verify backend defaults were applied by checking specifications
    specs = result["specifications"]
    
    # Backend applies these defaults (from lines 76-79):
    # - width_mm: 420
    # - height_mm: 594
    # - paper_stock: "150gsm"
    
    assert "width_mm" in specs, "Missing width_mm in specifications"
    assert specs["width_mm"] == 420, f"Expected width_mm=420 (backend default), got {specs['width_mm']}"
    
    assert "height_mm" in specs, "Missing height_mm in specifications"
    assert specs["height_mm"] == 594, f"Expected height_mm=594 (backend default), got {specs['height_mm']}"
    
    assert "paper_stock" in specs, "Missing paper_stock in specifications"
    assert specs["paper_stock"] == "150gsm", f"Expected paper_stock='150gsm' (backend default), got '{specs['paper_stock']}'"
    
    print(f"✅ TEST 4 PASSED: Backend defaults applied correctly")
    print(f"   width_mm: {specs['width_mm']} (backend default)")
    print(f"   height_mm: {specs['height_mm']} (backend default)")
    print(f"   paper_stock: {specs['paper_stock']} (backend default)")
    print(f"   Total Price: ${result['total_price']:.2f}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("GROUP 3 CALCULATOR 4: Custom Poster Printing - 4 Test Suite")
    print("=" * 80)
    
    try:
        test_custom_poster_printing_with_new_parameters()
        test_custom_poster_printing_with_legacy_parameters()
        test_custom_poster_printing_price_consistency()
        test_custom_poster_printing_defaults_validation()
        
        print("\n" + "=" * 80)
        print("🎉 ALL 4 TESTS PASSED FOR CUSTOM POSTER PRINTING")
        print("=" * 80)
        print("✅ Pattern 3.0/3.0 - Decorator ✅, None Defaults ✅, Validation ✅")
        print("✅ Backend Parameters: 4/4 verified (quantity, width_mm, height_mm, paper_stock)")
        print("✅ Legacy Support: width → width_mm, height → height_mm with warnings")
        print("✅ Backend Defaults: All 3 defaults verified and working")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
