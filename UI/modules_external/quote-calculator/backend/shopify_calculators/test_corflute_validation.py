"""
Test Corflute Signs Calculator Against Validated Prices
Compares backend calculator results with validated test configurations
"""

from corflute_calculator_shopify import (
    CorflutePricingCalculatorShopify,
    CorfluteSizePreset,
    CorfiuteThickness,
    EyeletOption
)

def test_corflute_signs():
    calc = CorflutePricingCalculatorShopify()
    
    tests = [
        {
            "name": "Test 1: Standard Real Estate Sign",
            "params": {
                "size_preset": CorfluteSizePreset.SIZE_600x900,
                "thickness": CorfiuteThickness.MM_5,
                "quantity": 10,
                "double_sided": False,
                "eyelet_option": EyeletOption.FOUR_CORNERS,
                "artworks": 1
            },
            "expected": 166.34
        },
        {
            "name": "Test 2: Volume Order (100 Units)",
            "params": {
                "size_preset": CorfluteSizePreset.SIZE_600x900,
                "thickness": CorfiuteThickness.MM_5,
                "quantity": 100,
                "double_sided": False,
                "eyelet_option": EyeletOption.NONE,
                "artworks": 1
            },
            "expected": 771.04
        },
        {
            "name": "Test 3: Custom Double-Sided",
            "params": {
                "size_preset": CorfluteSizePreset.CUSTOM,
                "custom_width_mm": 800,
                "custom_height_mm": 1200,
                "thickness": CorfiuteThickness.MM_5,
                "quantity": 20,
                "double_sided": True,
                "eyelet_option": EyeletOption.TWO_TOP,
                "artworks": 3
            },
            "expected": 532.03
        },
        {
            "name": "Test 4: Bulk 3mm (500 Units)",
            "params": {
                "size_preset": CorfluteSizePreset.SIZE_450x600,
                "thickness": CorfiuteThickness.MM_3,
                "quantity": 500,
                "double_sided": False,
                "eyelet_option": EyeletOption.NONE,
                "artworks": 1
            },
            "expected": 1377.41
        },
        {
            "name": "Test 5: Minimum Order",
            "params": {
                "size_preset": CorfluteSizePreset.SIZE_450x600,
                "thickness": CorfiuteThickness.MM_3,
                "quantity": 2,
                "double_sided": False,
                "eyelet_option": EyeletOption.NONE,
                "artworks": 1
            },
            "expected": 135.00
        },
        {
            "name": "Test 6: Multiple Artworks (10)",
            "params": {
                "size_preset": CorfluteSizePreset.SIZE_600x900,
                "thickness": CorfiuteThickness.MM_5,
                "quantity": 50,
                "double_sided": False,
                "eyelet_option": EyeletOption.NONE,
                "artworks": 10
            },
            "expected": 467.50
        }
    ]
    
    print("=" * 80)
    print("CORFLUTE SIGNS CALCULATOR VALIDATION")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for test in tests:
        result = calc.calculate_quote(**test["params"])
        actual = result['total']
        expected = test["expected"]
        difference = abs(actual - expected)
        
        status = "✅ PASS" if difference < 0.01 else "❌ FAIL"
        if difference < 0.01:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} {test['name']}")
        print(f"  Expected: ${expected:.2f}")
        print(f"  Actual:   ${actual:.2f}")
        if difference >= 0.01:
            print(f"  Difference: ${difference:.2f}")
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 80)
    
    if failed == 0:
        print("✅ ALL TESTS PASSED - Calculator matches validated prices!")
    else:
        print("❌ TESTS FAILED - Backend calculator needs fixing")

if __name__ == "__main__":
    test_corflute_signs()
