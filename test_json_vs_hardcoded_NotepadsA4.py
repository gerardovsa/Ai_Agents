"""
Test NotepadsA4 JSON config vs hardcoded Python backend
Part of: CALCULATOR_PATHWAY_ALIGNMENT_GUIDE.md
Date: January 25, 2026

NOTE: JSON has 100GSM=0.045 but Python has 100GSM=0.054 (discrepancy)
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add paths
backend_dir = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
calculators_dir = backend_dir / 'shopify_calculators'
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent))  # For config_manager
sys.path.insert(0, str(calculators_dir))

from NotepadsA4_Shopify_Calculator import NotepadsA4ShopifyCalculator

def test_json_vs_hardcoded():
    """Test that JSON config produces identical results to hardcoded Python"""
    
    # Initialize calculator with JSON config
    config_path = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'config' / 'shopify' / 'Shopify_Notepads_A4.json'
    calculator = NotepadsA4ShopifyCalculator(config_path=str(config_path))
    
    print("=" * 80)
    print("TESTING: NotepadsA4 JSON vs Hardcoded Python")
    print("=" * 80)
    
    test_cases = [
        {
            'name': 'Test 1: Basic order - 80GSM',
            'params': {
                'quantity': 100,
                'artworks': 1,
                'finish_size': 'A4 Portrait',
                'leaves_per_pad': 50,
                'print_type': 'Black & White 1 sided',
                'stock_type': 'Uncoated Bond 80GSM'
            },
            'expected': Decimal('511.29')
        },
        {
            'name': 'Test 2: Large order - 90GSM',
            'params': {
                'quantity': 500,
                'artworks': 1,
                'finish_size': 'A4 Portrait',
                'leaves_per_pad': 100,
                'print_type': 'Colour 2 sided',
                'stock_type': 'Uncoated Bond 90GSM'
            },
            'expected': Decimal('7906.64')
        },
        {
            'name': 'Test 3: 100GSM order (DISCREPANCY TEST)',
            'params': {
                'quantity': 1000,
                'artworks': 2,
                'finish_size': 'A4 Portrait',
                'leaves_per_pad': 50,
                'print_type': 'Colour 1 sided',
                'stock_type': 'Uncoated Bond 100GSM'
            },
            'expected': Decimal('7381.06')
        },
        {
            'name': 'Test 4: Recycled stock',
            'params': {
                'quantity': 2000,
                'artworks': 3,
                'finish_size': 'A4 Portrait',
                'leaves_per_pad': 100,
                'print_type': 'Black & White 2 sided',
                'stock_type': 'Revive 100% Recycled 80GSM Bond'
            },
            'expected': Decimal('19702.60')
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
        print("\nKNOWN DISCREPANCY: JSON has 100GSM=0.045, Python has 100GSM=0.054")
        return 1

if __name__ == '__main__':
    sys.exit(test_json_vs_hardcoded())
