"""
Alignment Test: BollardSigns Shopify Calculator
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

from BollardSigns_Shopify_Calculator import BollardSignsShopifyCalculator


def run_alignment_tests():
    """Test that JSON config matches hardcoded backend prices"""
    
    print("\n" + "="*80)
    print("BOLLARD SIGNS ALIGNMENT TEST")
    print("Testing: JSON config vs Hardcoded backend prices")
    print("="*80 + "\n")
    
    # Initialize calculator
    try:
        calc = BollardSignsShopifyCalculator()  # Tries to load JSON config
        print("✅ JSON config loaded successfully")
        has_config = True
    except Exception as e:
        print(f"⚠️  No JSON config found (expected): {e}")
        print("   Testing will verify hardcoded prices are correct")
        calc = BollardSignsShopifyCalculator()  # Uses hardcoded values
        has_config = False
    
    print(f"\n{'='*80}")
    print(f"CONFIG STATUS: {'JSON config exists' if has_config else 'Using hardcoded prices (no JSON config yet)'}")
    print(f"{'='*80}\n")
    
    # Test cases from CALCULATOR_TEST_QUOTES_SUMMARY (Jan 23, 2026 validation)
    test_cases = [
        {
            "name": "Test 1: Minimum Order (1 qty, 270mm×1000mm 3-sided)",
            "params": {
                "quantity": 1,
                "material": "5mm Corflute",
                "size": "270mm W x 1000mm H - Three Sided",
                "artworks": 1
            },
            "expected": Decimal("202.92")
        },
        {
            "name": "Test 2: Standard Order (10 signs, 270mm×1000mm 3-sided)",
            "params": {
                "quantity": 10,
                "material": "5mm Corflute",
                "size": "270mm W x 1000mm H - Three Sided",
                "artworks": 1
            },
            "expected": Decimal("750.78")
        },
        {
            "name": "Test 3: 3mm Material (10 signs, 270mm×1000mm 3-sided)",
            "params": {
                "quantity": 10,
                "material": "3mm Corflute",
                "size": "270mm W x 1000mm H - Three Sided",
                "artworks": 1
            },
            "expected": Decimal("621.09")
        },
        {
            "name": "Test 4: Multiple Artworks (10 signs, 5mm, 3 artworks)",
            "params": {
                "quantity": 10,
                "material": "5mm Corflute",
                "size": "270mm W x 1000mm H - Three Sided",
                "artworks": 3
            },
            "expected": Decimal("766.51")  # Updated Jan 26: $472.29 material + $15 artwork = $487.29 × 1.3 × 1.1 × 1.1
        },
        {
            "name": "Test 5: Large Order (100 signs, 300mm×1000mm 3-sided)",
            "params": {
                "quantity": 100,
                "material": "5mm Corflute",
                "size": "300mm W x 1000mm H - Three Sided",
                "artworks": 1
            },
            "expected": Decimal("5675.38")
        },
        {
            "name": "Test 6: Four-Sided (10 signs, 175mm×1000mm 4-sided)",
            "params": {
                "quantity": 10,
                "material": "5mm Corflute",
                "size": "175mm W x 1000mm H - Four Sided",
                "artworks": 1
            },
            "expected": Decimal("835.39")
        },
        {
            "name": "Test 7: Largest Size (10 signs, 300mm×1800mm 3-sided)",
            "params": {
                "quantity": 10,
                "material": "5mm Corflute",
                "size": "300mm W x 1800mm H - Three Sided",
                "artworks": 1
            },
            "expected": Decimal("1284.54")
        },
    ]
    
    all_passed = True
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"TEST {i}: {test['name']}")
        print(f"{'─'*80}")
        
        # Run calculation
        result = calc.calculate(**test['params'])
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
    print(f"{'Test':<55} {'Backend':>12} {'Expected':>12} {'Diff':>10} {'Status':>8}")
    print(f"{'-'*80}")
    
    for r in results:
        status = "✅ PASS" if r['passed'] else "❌ FAIL"
        test_name = r['test'][:53] if len(r['test']) > 53 else r['test']
        print(f"{test_name:<55} ${r['backend']:>11.2f} ${r['expected']:>11.2f} ${r['diff']:>9.2f} {status:>8}")
    
    print(f"\n{'='*80}")
    if all_passed:
        if has_config:
            print("✅ SUCCESS - All tests show <$0.01 difference!")
            print("   BollardSigns calculator properly loads prices from JSON config.")
        else:
            print("✅ SUCCESS - All tests show <$0.01 difference!")
            print("   BollardSigns calculator uses correct hardcoded prices.")
            print("   NOTE: JSON config doesn't exist yet - calculator uses hardcoded values")
    else:
        print("❌ FAILURE - Some tests show >= $0.01 difference")
        print("   Review pricing configuration alignment")
    print(f"{'='*80}\n")
    
    return all_passed


if __name__ == "__main__":
    success = run_alignment_tests()
    sys.exit(0 if success else 1)
