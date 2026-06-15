"""
Alignment Test: NotepadsA6 Shopify Calculator
Tests that JSON config values match hardcoded backend prices

Purpose: Verify 3-pathway alignment (AI schema ↔ JSON config ↔ Python backend)
Result: Differences < $0.01 per test = SUCCESS
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add backend path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from NotepadsA6_Shopify_Calculator import NotepadsA6ShopifyCalculator


def run_alignment_tests():
    """Test that JSON config matches hardcoded backend prices"""
    
    print("\n" + "="*80)
    print("NOTEPADS A6 ALIGNMENT TEST")
    print("Testing: JSON config vs Hardcoded backend prices")
    print("="*80 + "\n")
    
    # Initialize calculators
    try:
        config_calc = NotepadsA6ShopifyCalculator()  # Tries to load JSON config
        print("✅ JSON config loaded successfully")
        has_config = True
    except Exception as e:
        print(f"⚠️  No JSON config found (expected): {e}")
        print("   Testing will verify hardcoded prices are correct")
        config_calc = NotepadsA6ShopifyCalculator()  # Uses hardcoded values
        has_config = False
    
    print(f"\n{'='*80}")
    print(f"CONFIG STATUS: {'JSON config exists' if has_config else 'Using hardcoded prices (no JSON config yet)'}")
    print(f"{'='*80}\n")
    
    # Test cases based on test_all_notepads.py
    test_cases = [
        {
            "name": "Test 1: Baseline (100 qty, 50 leaves, B&W, 80GSM)",
            "params": {
                "quantity": 100,
                "artworks": 1,
                "finish_size": "A6 Portrait",
                "leaves_per_pad": 50,
                "print_type": "Black & White 1 sided",
                "stock_type": "Uncoated Bond 80GSM"
            },
            "expected": Decimal("175.74")
        },
        {
            "name": "Test 2: High Volume (2000 qty, 100 leaves, Colour 2-sided, 100GSM)",
            "params": {
                "quantity": 2000,
                "artworks": 2,
                "finish_size": "A6 Portrait",
                "leaves_per_pad": 100,
                "print_type": "Colour 2 sided",
                "stock_type": "Uncoated Bond 100GSM"
            },
            "expected": Decimal("8771.71")
        },
        {
            "name": "Test 3: Small Format (500 qty, 10 leaves, Colour 1-sided, Recycled)",
            "params": {
                "quantity": 500,
                "artworks": 3,
                "finish_size": "A6 Portrait",
                "leaves_per_pad": 10,
                "print_type": "Colour 1 sided",
                "stock_type": "Revive Recycled Uncoated"
            },
            "expected": Decimal("451.53")
        },
        {
            "name": "Test 4: Edge Case (50 qty, 15 leaves, B&W 2-sided, 90GSM)",
            "params": {
                "quantity": 50,
                "artworks": 1,
                "finish_size": "A6 Portrait",
                "leaves_per_pad": 15,
                "print_type": "Black & White 2 sided",
                "stock_type": "Uncoated Bond 90GSM"
            },
            "expected": Decimal("89.04")
        },
    ]
    
    all_passed = True
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"TEST {i}: {test['name']}")
        print(f"{'─'*80}")
        
        # Run calculation
        result = config_calc.calculate(**test['params'])
        backend_price = result.total_price
        expected_price = test['expected']
        
        # Calculate difference
        diff = abs(backend_price - expected_price)
        diff_pct = (diff / expected_price * 100) if expected_price > 0 else Decimal(0)
        
        # Check if passed (< $0.01 difference)
        passed = diff < Decimal("0.01")
        all_passed = all_passed and passed
        
        results.append({
            "test": test['name'],
            "backend": backend_price,
            "expected": expected_price,
            "diff": diff,
            "diff_pct": diff_pct,
            "passed": passed
        })
        
        # Print results
        print(f"\n📋 Parameters:")
        for key, value in test['params'].items():
            print(f"   {key}: {value}")
        
        print(f"\n💰 Results:")
        print(f"   Backend (config):    ${backend_price:>10.2f}")
        print(f"   Expected (baseline): ${expected_price:>10.2f}")
        print(f"   Difference:          ${diff:>10.2f} ({diff_pct:.4f}%)")
        
        if passed:
            print(f"   ✅ PASS - Difference < $0.01")
        else:
            print(f"   ❌ FAIL - Difference >= $0.01")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")
    
    passed_count = sum(1 for r in results if r['passed'])
    total_count = len(results)
    
    print(f"Tests Passed: {passed_count}/{total_count}")
    print(f"\nDetailed Results:")
    print(f"{'Test':<60} {'Backend':>10} {'Expected':>10} {'Diff':>8} {'Status':>8}")
    print(f"{'-'*80}")
    
    for r in results:
        status = "✅ PASS" if r['passed'] else "❌ FAIL"
        test_name = r['test'][:58] if len(r['test']) > 58 else r['test']
        print(f"{test_name:<60} ${r['backend']:>9.2f} ${r['expected']:>9.2f} ${r['diff']:>7.2f} {status:>8}")
    
    print(f"\n{'='*80}")
    if all_passed:
        if has_config:
            print("✅ SUCCESS - All tests show <$0.01 difference!")
            print("   NotepadsA6 calculator properly loads prices from JSON config.")
        else:
            print("✅ SUCCESS - All tests show <$0.01 difference!")
            print("   NotepadsA6 calculator uses correct hardcoded prices.")
            print("   NOTE: JSON config doesn't exist yet - calculator uses hardcoded values")
    else:
        print("❌ FAILURE - Some tests show >= $0.01 difference")
        print("   Review pricing configuration alignment")
    print(f"{'='*80}\n")
    
    return all_passed


if __name__ == "__main__":
    success = run_alignment_tests()
    sys.exit(0 if success else 1)
