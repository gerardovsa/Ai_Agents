"""
Test Printed Flyers Calculator Against Validated Prices
"""

import sys
from pathlib import Path

# Add backend path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from PrintedFlyers_Shopify_Calculator import PrintedFlyersShopifyCalculator

def test_printed_flyers():
    calc = PrintedFlyersShopifyCalculator()
    
    tests = [
        {
            "name": "Test 1: Small Order A5 Double Colour",
            "params": {
                "quantity": 100,
                "print_sides": "Double",
                "print_type": "Colour",
                "finish_size": "A5 - 148mm x 210mm",
                "paper_stock": "Satin 150GSM",
                "artworks": 1
            },
            "expected": 102.27
        },
        {
            "name": "Test 2: Budget DL Single B&W",
            "params": {
                "quantity": 500,
                "print_sides": "Single",
                "print_type": "Black & White",
                "finish_size": "DL - 99mm x 210mm",
                "paper_stock": "Uncoated Bond 80GSM",
                "artworks": 1
            },
            "expected": 107.74
        },
        {
            "name": "Test 3: Bulk A4 Double Colour (10% discount)",
            "params": {
                "quantity": 1000,
                "print_sides": "Double",
                "print_type": "Colour",
                "finish_size": "A4 - 210mm x 297mm",
                "paper_stock": "Satin 350GSM",
                "artworks": 2  # FIXED: Test 3 has 2 artworks in validated file
            },
            "expected": 379.94
        },
        {
            "name": "Test 4: Minimum Quantity A6",
            "params": {
                "quantity": 250,  # FIXED: Test 4 is 250 not 100
                "print_sides": "Single",
                "print_type": "Colour",
                "finish_size": "A6 - 105mm x 148mm",
                "paper_stock": "Satin 128GSM",
                "artworks": 1
            },
            "expected": 100.11
        },
        {
            "name": "Test 5: Large Format A3 Bulk",
            "params": {
                "quantity": 2000,
                "print_sides": "Double",
                "print_type": "Colour",
                "finish_size": "A3 - 297mm x 420mm",
                "paper_stock": "Satin 250GSM",  # FIXED: Test 5 uses 250GSM not 350GSM
                "artworks": 3  # FIXED: Test 5 has 3 artworks
            },
            "expected": 654.44
        }
    ]
    
    print("=" * 80)
    print("PRINTED FLYERS CALCULATOR VALIDATION")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for test in tests:
        result = calc.calculate(**test["params"])
        actual = float(result.final_price)
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
    test_printed_flyers()
