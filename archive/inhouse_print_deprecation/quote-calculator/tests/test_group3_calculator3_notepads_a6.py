"""
Test Group 3 Calculator 3: Notepads A6

Backend Parameters (verified NotepadsA6_Shopify_Calculator.py lines 76-80):
- quantity: int (default 250)
- print_type: str (default "Colour")
- print_sides: str (default "Single side print")
- paper_stock: str (default "Standard")
- artworks: int (default 1)

Legacy Parameter:
- stock_type → paper_stock

3-Part Pattern Applied:
1. ✅ Decorator exists: @calculator_wrapper(quantity_enum=[...], validate_params=True)
2. ✅ None defaults: All 4 optional parameters use None
3. ✅ Validation: Backend defaults applied after legacy translation
"""

import sys
from pathlib import Path

# Add paths
test_file = Path(__file__).resolve()
wrapper_dir = test_file.parent.parent / "implementations"
sys.path.insert(0, str(wrapper_dir))

from calculator_wrapper import calculate_notepads_a6

def test_notepads_a6_with_new_parameters():
    """Test #1: New parameters (all explicit values) - should work"""
    print("\n🧪 TEST 1: Notepads A6 with NEW parameters (all explicit)")
    print("=" * 80)
    
    result = calculate_notepads_a6(
        quantity=500,
        print_type="Colour",
        print_sides="Double side print",
        paper_stock="Uncoated Bond 80GSM",
        artworks=2
    )
    
    print(f"Result: {result}")
    
    assert result["success"] is True, f"Expected success=True, got {result.get('success')}"
    assert result["quantity"] == 500, f"Expected quantity=500, got {result.get('quantity')}"
    assert "total_price" in result, "Missing total_price"
    assert "unit_price" in result, "Missing unit_price"
    assert "cost_per_item" in result, "Missing cost_per_item"
    assert "breakdown" in result, "Missing breakdown"
    assert "specifications" in result, "Missing specifications"
    assert "warnings" not in result, f"Should NOT have warnings with new parameters, got {result.get('warnings')}"
    
    print(f"✅ TEST 1 PASSED: Notepads A6 quote calculated successfully")
    print(f"   Quantity: {result['quantity']}")
    print(f"   Total Price: ${result['total_price']:.2f}")
    print(f"   Unit Price: ${result['unit_price']:.2f}")
    print(f"   Specifications: {result['specifications']}")


def test_notepads_a6_with_legacy_parameters():
    """Test #2: Legacy parameters (stock_type) - should work with warning"""
    print("\n🧪 TEST 2: Notepads A6 with LEGACY parameters (stock_type)")
    print("=" * 80)
    
    result = calculate_notepads_a6(
        quantity=250,
        print_type="Black & White",
        print_sides="Single side print",
        stock_type="Standard",  # Legacy parameter
        artworks=1
    )
    
    print(f"Result: {result}")
    
    assert result["success"] is True, f"Expected success=True, got {result.get('success')}"
    assert result["quantity"] == 250, f"Expected quantity=250, got {result.get('quantity')}"
    assert "warnings" in result, "Expected deprecation warnings for legacy parameter"
    
    # Verify warning structure
    warnings = result["warnings"]
    assert len(warnings) == 1, f"Expected 1 warning, got {len(warnings)}"
    assert warnings[0]["deprecated"] == "stock_type", f"Expected deprecated='stock_type', got {warnings[0]['deprecated']}"
    assert warnings[0]["use_instead"] == "paper_stock", f"Expected use_instead='paper_stock', got {warnings[0]['use_instead']}"
    
    print(f"✅ TEST 2 PASSED: Legacy parameter translated with warning")
    print(f"   Warning: {warnings[0]}")
    print(f"   Total Price: ${result['total_price']:.2f}")


def test_notepads_a6_price_consistency():
    """Test #3: Price consistency between new and legacy parameters"""
    print("\n🧪 TEST 3: Price consistency NEW vs LEGACY parameters")
    print("=" * 80)
    
    # Call with NEW parameters
    result_new = calculate_notepads_a6(
        quantity=500,
        print_type="Colour",
        print_sides="Single side print",
        paper_stock="Standard",
        artworks=1
    )
    
    # Call with LEGACY parameters (stock_type)
    result_legacy = calculate_notepads_a6(
        quantity=500,
        print_type="Colour",
        print_sides="Single side print",
        stock_type="Standard",  # Legacy
        artworks=1
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
    
    # Legacy should have warning, new should not
    assert "warnings" not in result_new, "NEW parameters should NOT have warnings"
    assert "warnings" in result_legacy, "LEGACY parameters should have warnings"
    
    print(f"✅ TEST 3 PASSED: Price consistency verified")
    print(f"   NEW total: ${result_new['total_price']:.2f}")
    print(f"   LEGACY total: ${result_legacy['total_price']:.2f}")
    print(f"   Match: ✅")


def test_notepads_a6_defaults_validation():
    """Test #4: Validation with None defaults - backend defaults should apply"""
    print("\n🧪 TEST 4: Notepads A6 defaults validation (None → backend defaults)")
    print("=" * 80)
    
    # Call with ONLY quantity (all other params should use backend defaults)
    result = calculate_notepads_a6(quantity=250)
    
    print(f"Result: {result}")
    
    assert result["success"] is True, f"Expected success=True with defaults, got {result.get('success')}"
    assert result["quantity"] == 250, f"Expected quantity=250, got {result.get('quantity')}"
    
    # Verify backend defaults were applied by checking specifications
    specs = result["specifications"]
    
    # Backend applies these defaults (from lines 76-80):
    # - print_type: "Colour"
    # - print_sides: "Single side print"
    # - paper_stock: "Standard"
    # - artworks: 1
    
    assert "print_type" in specs, "Missing print_type in specifications"
    assert specs["print_type"] == "Colour", f"Expected print_type='Colour' (backend default), got '{specs['print_type']}'"
    
    assert "print_sides" in specs, "Missing print_sides in specifications"
    assert specs["print_sides"] == "Single side print", f"Expected print_sides='Single side print' (backend default), got '{specs['print_sides']}'"
    
    assert "paper_stock" in specs, "Missing paper_stock in specifications"
    assert specs["paper_stock"] == "Standard", f"Expected paper_stock='Standard' (backend default), got '{specs['paper_stock']}'"
    
    assert "artworks" in specs, "Missing artworks in specifications"
    assert specs["artworks"] == 1, f"Expected artworks=1 (backend default), got {specs['artworks']}"
    
    print(f"✅ TEST 4 PASSED: Backend defaults applied correctly")
    print(f"   print_type: {specs['print_type']} (backend default)")
    print(f"   print_sides: {specs['print_sides']} (backend default)")
    print(f"   paper_stock: {specs['paper_stock']} (backend default)")
    print(f"   artworks: {specs['artworks']} (backend default)")
    print(f"   Total Price: ${result['total_price']:.2f}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("GROUP 3 CALCULATOR 3: Notepads A6 - 4 Test Suite")
    print("=" * 80)
    
    try:
        test_notepads_a6_with_new_parameters()
        test_notepads_a6_with_legacy_parameters()
        test_notepads_a6_price_consistency()
        test_notepads_a6_defaults_validation()
        
        print("\n" + "=" * 80)
        print("🎉 ALL 4 TESTS PASSED FOR NOTEPADS A6")
        print("=" * 80)
        print("✅ Pattern 3.0/3.0 - Decorator ✅, None Defaults ✅, Validation ✅")
        print("✅ Backend Parameters: 5/5 verified (quantity, print_type, print_sides, paper_stock, artworks)")
        print("✅ Legacy Support: stock_type → paper_stock with warning")
        print("✅ Backend Defaults: All 4 defaults verified and working")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
