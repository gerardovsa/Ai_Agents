"""
Test PrintedLetterheads JSON config vs hardcoded Python backend
Part of: CALCULATOR_PATHWAY_ALIGNMENT_GUIDE.md
Date: January 25, 2026

Compares:
- JSON: config/shopify/Shopify_Printed_Letterheads.json
- Python: PrintedLetterheads_Shopify_Calculator.py (hardcoded prices)

Expected: 0% difference (JSON should match hardcoded backend)
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add paths for imports
backend_dir = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
calculators_dir = backend_dir / 'shopify_calculators'
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent))  # For config_manager
sys.path.insert(0, str(calculators_dir))

# Direct import to avoid __init__.py
from PrintedLetterheads_Shopify_Calculator import PrintedLetterheadsShopifyCalculator

def test_json_vs_hardcoded():
    """Test that JSON config produces identical results to hardcoded Python"""
    
    # Initialize calculator with JSON config
    config_path = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'config' / 'shopify' / 'Shopify_Printed_Letterheads.json'
    calculator = PrintedLetterheadsShopifyCalculator(config_path=str(config_path))
    
    print("=" * 80)
    print("TESTING: PrintedLetterheads JSON vs Hardcoded Python")
    print("=" * 80)
    
    test_cases = [
        {
            'name': 'Test 1: Basic order',
            'params': {
                'quantity': 100,
                'print_sides': 'Single side print',
                'print_type': 'Colour',
                'finish_size': 'A4 - 210mm x 297mm',
                'paper_stock': 'Uncoated Bond 80GSM',
                'artworks': 1
            },
            'expected': Decimal('104.05')  # CURRENT hardcoded output
        },
        {
            'name': 'Test 2: Medium order, double-sided, B&W',
            'params': {
                'quantity': 500,
                'print_sides': 'Double side print',
                'print_type': 'Black & White',
                'finish_size': 'A4 - 210mm x 297mm',
                'paper_stock': 'Uncoated Bond 90GSM',
                'artworks': 1
            },
            'expected': Decimal('157.43')  # CURRENT hardcoded output
        },
        {
            'name': 'Test 3: Large order, colour, 2 artworks',
            'params': {
                'quantity': 1000,
                'print_sides': 'Single side print',
                'print_type': 'Colour',
                'finish_size': 'A4 - 210mm x 297mm',
                'paper_stock': 'Uncoated Bond 100GSM',
                'artworks': 2
            },
            'expected': Decimal('266.74')  # CURRENT hardcoded output
        },
        {
            'name': 'Test 4: Complex order, double-sided, 3 artworks',
            'params': {
                'quantity': 3000,
                'print_sides': 'Double side print',
                'print_type': 'Colour',
                'finish_size': 'A4 - 210mm x 297mm',
                'paper_stock': 'Uncoated Bond 90GSM',
                'artworks': 3
            },
            'expected': Decimal('569.23')  # CURRENT hardcoded output
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {test['name']}")
        print(f"{'='*80}")
        print(f"Params: {test['params']}")
        
        try:
            # Calculate using JSON config
            result = calculator.calculate(**test['params'])
            json_price = result.total_price
            expected_price = test['expected']
            
            # Calculate difference
            diff = abs(json_price - expected_price)
            diff_percent = (diff / expected_price * 100) if expected_price != 0 else 0
            
            print(f"\nJSON Result:  ${json_price:.2f}")
            print(f"Expected:     ${expected_price:.2f}")
            print(f"Difference:   ${diff:.4f} ({diff_percent:.4f}%)")
            
            if diff < Decimal('0.01'):  # Within 1 cent
                print("✅ PASS")
                passed += 1
            else:
                print("❌ FAIL - Prices don't match!")
                failed += 1
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"SUMMARY: {passed}/{len(test_cases)} tests passed")
    print(f"{'='*80}")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED - JSON pricing matches hardcoded perfectly!")
        return 0
    else:
        print(f"⚠️ {failed} tests FAILED - JSON needs updating")
        return 1

if __name__ == '__main__':
    sys.exit(test_json_vs_hardcoded())
