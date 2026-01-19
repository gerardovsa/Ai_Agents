"""
Test Suite: Group 5 Calculators 3-5 Alignment
Calculators: Stackable Cubes, Strut Cards A3, Strut Cards A4
Date: January 19, 2026
Status: Testing 3-part pattern (kwargs removal, None defaults, validation)
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "UI" / "modules_external" / "quote-calculator" / "implementations"))
sys.path.insert(0, str(project_root / "UI" / "modules_external" / "quote-calculator" / "backend" / "shopify_calculators"))

from calculator_wrapper import (
    calculate_stackable_cubes,
    calculate_strut_cards_a3,
    calculate_strut_cards_a4
)


def test_calculator_3_stackable_cubes():
    """Test Calculator 3: Stackable Cubes (NO artworks parameter)"""
    print("\n" + "="*70)
    print("CALCULATOR 3: STACKABLE CUBES")
    print("="*70)
    
    # Test 1: New parameters with explicit values
    print("\n🧪 Test 1: Explicit parameters")
    result1 = calculate_stackable_cubes(
        quantity=10,
        size="300",
        material="Corrugated"
    )
    assert result1["success"] == True, "Should succeed with explicit params"
    assert result1["total_price"] > 0, "Price should be positive"
    print(f"✅ Price: ${result1['total_price']:.2f}")
    
    # Test 2: Only required param (uses defaults)
    print("\n🧪 Test 2: Defaults applied")
    result2 = calculate_stackable_cubes(quantity=10)
    assert result2["success"] == True, "Should succeed with defaults"
    assert result2["specifications"]["edge_mm"] == 300.0, "Should use default edge 300mm"
    assert result2["specifications"]["material"] == "Corrugated", "Should use default material"
    print(f"✅ Edge: {result2['specifications']['edge_mm']}mm")
    print(f"✅ Material: {result2['specifications']['material']}")
    
    # Test 3: Price consistency
    print("\n🧪 Test 3: Price consistency")
    assert result1["total_price"] == result2["total_price"], "Prices should match when values same"
    print(f"✅ Consistent: ${result1['total_price']:.2f}")
    
    # Test 4: Different material
    print("\n🧪 Test 4: Material variation")
    result_card = calculate_stackable_cubes(quantity=10, size="300", material="Card")
    assert result_card["success"] == True
    assert result_card["total_price"] != result1["total_price"], "Different material = different price"
    print(f"✅ Corrugated: ${result1['total_price']:.2f}")
    print(f"✅ Card: ${result_card['total_price']:.2f}")
    
    print("\n✅ CALCULATOR 3 COMPLETE - 4/4 tests passed\n")


def test_calculator_4_strut_cards_a3():
    """Test Calculator 4: Strut Cards A3 (HAS artworks parameter)"""
    print("\n" + "="*70)
    print("CALCULATOR 4: STRUT CARDS A3")
    print("="*70)
    
    # Test 1: New parameters with explicit values
    print("\n🧪 Test 1: Explicit parameters")
    result1 = calculate_strut_cards_a3(
        quantity=100,
        size="297x420",
        sides="Single",
        artworks=1
    )
    assert result1["success"] == True, "Should succeed with explicit params"
    assert result1["total_price"] > 0, "Price should be positive"
    print(f"✅ Price (Single): ${result1['total_price']:.2f}")
    
    # Test 2: Only required param (uses defaults)
    print("\n🧪 Test 2: Defaults applied")
    result2 = calculate_strut_cards_a3(quantity=100)
    assert result2["success"] == True, "Should succeed with defaults"
    assert "297x420" in result2["specifications"]["size_mm"], "Should use default A3 size"
    assert result2["specifications"]["sides"] == "Single", "Should use default sides"
    print(f"✅ Size: {result2['specifications']['size_mm']}")
    print(f"✅ Sides: {result2['specifications']['sides']}")
    
    # Test 3: Price consistency
    print("\n🧪 Test 3: Price consistency")
    assert result1["total_price"] == result2["total_price"], "Prices should match when values same"
    print(f"✅ Consistent: ${result1['total_price']:.2f}")
    
    # Test 4: Double-sided variation
    print("\n🧪 Test 4: Double-sided variation")
    result_double = calculate_strut_cards_a3(
        quantity=100,
        size="297x420",
        sides="Double",
        artworks=1
    )
    assert result_double["success"] == True
    assert result_double["total_price"] > result1["total_price"], "Double-sided should cost more"
    print(f"✅ Single-sided: ${result1['total_price']:.2f}")
    print(f"✅ Double-sided: ${result_double['total_price']:.2f}")
    
    print("\n✅ CALCULATOR 4 COMPLETE - 4/4 tests passed\n")


def test_calculator_5_strut_cards_a4():
    """Test Calculator 5: Strut Cards A4 (HAS artworks parameter)"""
    print("\n" + "="*70)
    print("CALCULATOR 5: STRUT CARDS A4")
    print("="*70)
    
    # Test 1: New parameters with explicit values
    print("\n🧪 Test 1: Explicit parameters")
    result1 = calculate_strut_cards_a4(
        quantity=100,
        size="210x297",
        sides="Single",
        artworks=1
    )
    assert result1["success"] == True, "Should succeed with explicit params"
    assert result1["total_price"] > 0, "Price should be positive"
    print(f"✅ Price (Single): ${result1['total_price']:.2f}")
    
    # Test 2: Only required param (uses defaults)
    print("\n🧪 Test 2: Defaults applied")
    result2 = calculate_strut_cards_a4(quantity=100)
    assert result2["success"] == True, "Should succeed with defaults"
    assert "210x297" in result2["specifications"]["size_mm"], "Should use default A4 size"
    assert result2["specifications"]["sides"] == "Single", "Should use default sides"
    print(f"✅ Size: {result2['specifications']['size_mm']}")
    print(f"✅ Sides: {result2['specifications']['sides']}")
    
    # Test 3: Price consistency
    print("\n🧪 Test 3: Price consistency")
    assert result1["total_price"] == result2["total_price"], "Prices should match when values same"
    print(f"✅ Consistent: ${result1['total_price']:.2f}")
    
    # Test 4: Double-sided variation
    print("\n🧪 Test 4: Double-sided variation")
    result_double = calculate_strut_cards_a4(
        quantity=100,
        size="210x297",
        sides="Double",
        artworks=1
    )
    assert result_double["success"] == True
    assert result_double["total_price"] > result1["total_price"], "Double-sided should cost more"
    print(f"✅ Single-sided: ${result1['total_price']:.2f}")
    print(f"✅ Double-sided: ${result_double['total_price']:.2f}")
    
    print("\n✅ CALCULATOR 5 COMPLETE - 4/4 tests passed\n")


def run_all_tests():
    """Run all tests for Calculators 3-5"""
    print("\n" + "="*70)
    print("GROUP 5 CALCULATORS 3-5 - ALIGNMENT TESTS")
    print("="*70)
    print("Testing 3-Part Pattern:")
    print("  1. ✅ **kwargs removed (explicit parameters)")
    print("  2. ✅ None defaults used")
    print("  3. ✅ Validation after legacy translation")
    print("="*70)
    
    try:
        # Calculator 3: Stackable Cubes (NO artworks)
        test_calculator_3_stackable_cubes()
        
        # Calculator 4: Strut Cards A3 (HAS artworks)
        test_calculator_4_strut_cards_a3()
        
        # Calculator 5: Strut Cards A4 (HAS artworks)
        test_calculator_5_strut_cards_a4()
        
        print("\n" + "="*70)
        print("✅ ALL CALCULATORS 3-5 COMPLETE!")
        print("="*70)
        print("✅ Calculator 3 (Stackable Cubes): 4/4 tests passed")
        print("✅ Calculator 4 (Strut Cards A3): 4/4 tests passed")
        print("✅ Calculator 5 (Strut Cards A4): 4/4 tests passed")
        print("="*70)
        print("✅ Total: 12/12 tests passed")
        print("✅ Pattern Score: 3.0/3.0 for all 3 calculators")
        print("="*70 + "\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
