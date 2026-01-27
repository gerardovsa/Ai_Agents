"""
Test Folded Flyers Calculator Against Validated Prices
"""

import sys
from pathlib import Path

# Add implementations path to import wrapper function
implementations_path = Path(__file__).parent.parent.parent / 'implementations'
sys.path.insert(0, str(implementations_path))

from calculator_wrapper import calculate_folded_flyers_shopify

def test_folded_flyers():
    
    tests = [
        {
            "name": "Test 1: A5 Half Fold Double Colour Satin 150GSM",
            "params": {
                "quantity": 500,
                "finish_size": "A5 - 148mm x 210mm",
                "paper_stock": "Satin 150GSM",
                "print_sides": "Double",
                "print_type": "Colour",
                "fold_type": "Half fold to A6",
                "celloglaze": "None",
                "artworks": 1
            },
            "expected": 205.22
        },
        {
            "name": "Test 2: A4 Half Fold with Celloglaze Satin 300GSM",
            "params": {
                "quantity": 1000,
                "finish_size": "A4 - 210mm x 297mm",
                "paper_stock": "Satin 300GSM",
                "print_sides": "Double",
                "print_type": "Colour",
                "fold_type": "Half fold to A5",
                "celloglaze": "2 Side Matt",
                "artworks": 1
            },
            "expected": 630.32
        },
        {
            "name": "Test 3: A5 Budget Single B&W Uncoated",
            "params": {
                "quantity": 250,
                "finish_size": "A5 - 148mm x 210mm",
                "paper_stock": "Uncoated Bond 100GSM",
                "print_sides": "Single",
                "print_type": "Black & White",
                "fold_type": "Half fold to A6",
                "celloglaze": "None",
                "artworks": 1
            },
            "expected": 146.42
        },
        {
            "name": "Test 4: A3 Crash Fold with Celloglaze Satin 350GSM",
            "params": {
                "quantity": 500,
                "finish_size": "A3 - 297mm x 420mm",
                "paper_stock": "Satin 350GSM",
                "print_sides": "Double",
                "print_type": "Colour",
                "fold_type": "Crash fold to A5(Half then half)",
                "celloglaze": "1 Side Gloss",
                "artworks": 1
            },
            "expected": 626.01
        },
        {
            "name": "Test 5: A4 Tri-Roll Fold Satin 128GSM",
            "params": {
                "quantity": 1000,
                "finish_size": "A4 - 210mm x 297mm",
                "paper_stock": "Satin 128GSM",
                "print_sides": "Double",
                "print_type": "Colour",
                "fold_type": "Tri Roll fold to DL",
                "celloglaze": "None",
                "artworks": 1
            },
            "expected": 310.24
        },
        {
            "name": "Test 6: 6pp A4 Tri-Roll Fold Satin 128GSM",
            "params": {
                "quantity": 250,
                "finish_size": "6pp A4 - 630mm x 297mm",
                "paper_stock": "Satin 128GSM",
                "print_sides": "Double",
                "print_type": "Colour",
                "fold_type": "Tri Roll fold to A4",
                "celloglaze": "None",
                "artworks": 1
            },
            "expected": 317.48
        }
    ]
    
    print("=" * 80)
    print("FOLDED FLYERS CALCULATOR VALIDATION")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for test in tests:
        result = calculate_folded_flyers_shopify(**test["params"])
        
        if not result.get("success"):
            print(f"❌ FAIL {test['name']}")
            print(f"  Error: {result.get('error')}")
            print()
            failed += 1
            continue
        
        actual = result["total_price"]
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
        print("❌ TESTS FAILED - Schema/wrapper/backend misalignment")

if __name__ == "__main__":
    test_folded_flyers()
