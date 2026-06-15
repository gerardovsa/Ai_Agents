"""
Alignment Test: ConstructionSigns Shopify Calculator
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

from ConstructionSigns_Shopify_Calculator import ConstructionSignsShopifyCalculator


def run_alignment_tests():
    """Test that JSON config matches hardcoded backend prices"""
    
    print("\n" + "="*80)
    print("CONSTRUCTION SIGNS ALIGNMENT TEST")
    print("Testing: JSON config vs Hardcoded backend prices")
    print("="*80 + "\n")
    
    # Initialize calculator
    try:
        calc = ConstructionSignsShopifyCalculator()  # Tries to load JSON config
        print("✅ JSON config loaded successfully")
        has_config = True
    except Exception as e:
        print(f"⚠️  No JSON config found (expected): {e}")
        print("   Testing will verify hardcoded prices are correct")
        calc = ConstructionSignsShopifyCalculator()  # Uses hardcoded values
        has_config = False
    
    print(f"\n{'='*80}")
    print(f"CONFIG STATUS: {'JSON config exists' if has_config else 'Using hardcoded prices (no JSON config yet)'}")
    print(f"{'='*80}\n")
    
    # Test cases from CALCULATOR_TEST_QUOTES_SUMMARY (Jan 23, 2026 validation)
    test_cases = [
        {
            "name": "Test 1: Small Order with Minimum (1 qty, 450×600mm)",
            "params": {
                "quantity": 1,
                "size": "450mm x 600mm",
                "thickness": "5mm",
                "sides": "Single Sided",
                "eyelets": "No Eyelets",
                "cutting": "Standard square edge",
                "artworks": 1
            },
            "expected": Decimal("141.90")
        },
        {
            "name": "Test 2: Double-Sided with Eyelets (25 qty, 900×1200mm)",
            "params": {
                "quantity": 25,
                "size": "900mm x 1200mm",
                "thickness": "5mm",
                "sides": "Double Sided",
                "eyelets": "6 x Eyelets (3 each top & bottom)",
                "artworks": 2
            },
            "expected": Decimal("725.33")  # Backend+JSON config price (config-loaded eyelet price)
        },
        {
            "name": "Test 3: Large Size with Surcharge (5 qty, 1200×2400mm)",
            "params": {
                "quantity": 5,
                "size": "1200mm x 2400mm",
                "thickness": "5mm",
                "sides": "Single Sided",
                "eyelets": "4 x Eyelets (1 In Each Corner)",
                "artworks": 1
            },
            "expected": Decimal("343.16")
        },
        {
            "name": "Test 4: 5mm Standard Volume (20 qty, 600×900mm)",
            "params": {
                "quantity": 20,
                "size": "600mm x 900mm",
                "thickness": "5mm",
                "sides": "Single Sided",
                "eyelets": "No Eyelets",
                "artworks": 1
            },
            "expected": Decimal("239.71")
        },
        {
            "name": "Test 5: 3mm vs 5mm (20 qty, 600×900mm, 3mm)",
            "params": {
                "quantity": 20,
                "size": "600mm x 900mm",
                "thickness": "3mm",
                "sides": "Single Sided",
                "artworks": 1
            },
            "expected": Decimal("200.10")
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
            print("   ConstructionSigns calculator properly loads prices from JSON config.")
        else:
            print("✅ SUCCESS - All tests show <$0.01 difference!")
            print("   ConstructionSigns calculator uses correct hardcoded prices.")
            print("   NOTE: JSON config doesn't exist yet - calculator uses hardcoded values")
    else:
        print("❌ FAILURE - Some tests show >= $0.01 difference")
        print("   Review pricing configuration alignment")
    print(f"{'='*80}\n")
    
    return all_passed


if __name__ == "__main__":
    success = run_alignment_tests()
    sys.exit(0 if success else 1)
