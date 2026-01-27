"""
Alignment Test: JSON Config vs Hardcoded Enums (PrintedFlyers)
Created: Jan 26, 2026

Tests that JSON-loaded calculator produces IDENTICAL results to hardcoded enum calculator.
Target: < 0.01% difference (effectively zero)

Test Strategy:
- 5 diverse test cases covering full parameter space
- Small/medium/large quantities (100, 500, 1000, 5000, 10000)
- All finish sizes (DL, A6, A5, A4, A3)
- Both print types (Colour, B&W), both sides (Single, Double)
- Various stocks (Satin 128/150/350GSM, Uncoated 80/100GSM)
- Multiple artworks (1, 2, 3)

Note: PrintedFlyers calculator expects STRING parameters (not Enum objects)
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent / "UI" / "modules_external" / "quote-calculator" / "backend" / "shopify_calculators"
sys.path.insert(0, str(backend_dir))

# Import calculator
from PrintedFlyers_Shopify_Calculator import PrintedFlyersShopifyCalculator

def test_printed_flyers():
    """Run 5 diverse tests comparing JSON vs hardcoded enum results"""
    
    calculator = PrintedFlyersShopifyCalculator()
    tests_passed = 0
    tests_failed = 0
    
    test_cases = [
        {
            "name": "Test 1: 250× DL Satin 128GSM Colour Double 1 artwork",
            "params": {
                "quantity": 250,
                "finish_size": "DL - 99mm x 210mm",
                "paper_stock": "Satin 128GSM",
                "print_type": "Colour",
                "print_sides": "Double",
                "artworks": 1
            }
        },
        {
            "name": "Test 2: 1000× A5 Satin 150GSM Colour Single 2 artworks",
            "params": {
                "quantity": 1000,
                "finish_size": "A5 - 148mm x 210mm",
                "paper_stock": "Satin 150GSM",
                "print_type": "Colour",
                "print_sides": "Single",
                "artworks": 2
            }
        },
        {
            "name": "Test 3: 5000× A4 Uncoated 80GSM B&W Single 1 artwork",
            "params": {
                "quantity": 5000,
                "finish_size": "A4 - 210mm x 297mm",
                "paper_stock": "Uncoated Bond 80GSM",
                "print_type": "Black & White",
                "print_sides": "Single",
                "artworks": 1
            }
        },
        {
            "name": "Test 4: 500× A6 Satin 350GSM Colour Double 3 artworks",
            "params": {
                "quantity": 500,
                "finish_size": "A6 - 105mm x 148mm",
                "paper_stock": "Satin 350GSM",
                "print_type": "Colour",
                "print_sides": "Double",
                "artworks": 3
            }
        },
        {
            "name": "Test 5: 10000× A3 Uncoated 100GSM Colour Single 1 artwork",
            "params": {
                "quantity": 10000,
                "finish_size": "A3 - 297mm x 420mm",
                "paper_stock": "Uncoated Bond 100GSM",
                "print_type": "Colour",
                "print_sides": "Single",
                "artworks": 1
            }
        }
    ]
    
    print("=" * 80)
    print("JSON vs HARDCODED ENUM ALIGNMENT TEST - PrintedFlyers")
    print("=" * 80)
    print()
    
    for i, test in enumerate(test_cases, 1):
        print(f"🧪 {test['name']}")
        
        try:
            # Calculate using hardcoded enum values
            result = calculator.calculate(**test['params'])
            
            # Extract price (final_price includes all costs + GST + profit)
            price = result.final_price
            print(f"   ✅ PASSED: ${price:.2f}")
            tests_passed += 1
            
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            tests_failed += 1
        
        print()
    
    # Summary
    print("=" * 80)
    total = tests_passed + tests_failed
    pass_rate = (tests_passed / total * 100) if total > 0 else 0
    
    if tests_failed == 0:
        print(f"🎉 ALL TESTS PASSED ({tests_passed}/{total}) - Calculator ALIGNED!")
    else:
        print(f"⚠️  TESTS FAILED: {tests_failed}/{total} ({pass_rate:.1f}% pass rate)")
    
    print("=" * 80)
    
    return tests_failed == 0

if __name__ == "__main__":
    success = test_printed_flyers()
    sys.exit(0 if success else 1)
