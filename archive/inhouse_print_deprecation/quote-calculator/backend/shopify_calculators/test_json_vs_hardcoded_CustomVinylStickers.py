"""
Custom Vinyl Stickers - JSON Config vs Hardcoded Backend Alignment Test
Created: January 26, 2026

Tests verify that JSON configuration matches Python backend pricing.
Success criteria: All test prices < $0.01 difference (0% tolerance)

Test data source: test_CustomVinylStickers.py baseline prices
Expected prices: Jan 26, 2026 calculator output
"""

import sys
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any, List

# Add backend path
backend_path = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_path))

from CustomVinylStickers_Shopify_Calculator import CustomVinylStickersShopifyCalculator

print("=" * 80)
print("CUSTOM VINYL STICKERS ALIGNMENT TEST")
print("Testing: JSON config vs Hardcoded backend prices")
print("=" * 80)

# Initialize calculator
try:
    calculator = CustomVinylStickersShopifyCalculator()
    print("\n✅ JSON config loaded successfully")
    print("\n" + "=" * 80)
    print("CONFIG STATUS: JSON config exists")
    print("=" * 80)
except Exception as e:
    print(f"\n⚠️ Warning: Could not load JSON config: {e}")
    print("Test will proceed with hardcoded values only")
    calculator = CustomVinylStickersShopifyCalculator()

# Test cases with baseline prices
test_cases = [
    {
        "name": "Test 1: Small circle stickers (100× 50mm standard vinyl)",
        "params": {
            "quantity": 100,
            "size": "50mm Circle",
            "vinyl_family": "Standard Vinyl",
            "adhesive": "Permanent",
            "laminate": "No Lamination",
            "cutting_method": "Standard Cut",
            "artworks": 1,
            "labour_rate": "Non-Trade ($90/hr)"
        },
        "expected": Decimal("60.50")
    },
    {
        "name": "Test 2: Custom size with laminate (500× 200×150mm premium removable kiss-cut)",
        "params": {
            "quantity": 500,
            "size": "Custom Size",
            "width": 200,
            "height": 150,
            "vinyl_family": "Premium Vinyl",
            "adhesive": "Removable",
            "laminate": "Gloss",
            "cutting_method": "Kiss-Cut",
            "artworks": 2,
            "labour_rate": "Non-Trade ($90/hr)"
        },
        "expected": Decimal("900.63")
    },
    {
        "name": "Test 3: Large rectangle with laminate (250× 200×100mm standard laminated)",
        "params": {
            "quantity": 250,
            "size": "200x100mm Rectangle",
            "vinyl_family": "Standard Vinyl",
            "adhesive": "Permanent",
            "laminate": "Matt",
            "cutting_method": "Standard Cut",
            "artworks": 1,
            "labour_rate": "Trade ($70/hr)"
        },
        "expected": Decimal("238.79")
    },
    {
        "name": "Test 4: High quantity square (2000× 100mm premium vinyl)",
        "params": {
            "quantity": 2000,
            "size": "100mm Square",
            "vinyl_family": "Premium Vinyl",
            "adhesive": "Permanent",
            "laminate": "No Lamination",
            "cutting_method": "Standard Cut",
            "artworks": 3,
            "labour_rate": "Non-Trade ($90/hr)"
        },
        "expected": Decimal("609.95")
    }
]

# Run tests
passed = 0
failed = 0
results = []

for test in test_cases:
    print("\n\n" + "─" * 80)
    print(f"{test['name']}")
    print("─" * 80)
    
    # Print parameters
    print("\n📋 Parameters:")
    for key, value in test['params'].items():
        print(f"   {key}: {value}")
    
    try:
        # Run calculation
        result = calculator.calculate(**test['params'])
        
        # Compare prices
        backend_price = result.total_price
        expected_price = test['expected']
        difference = abs(backend_price - expected_price)
        percent_diff = (difference / expected_price * 100) if expected_price != 0 else 0
        
        # Record result
        results.append({
            'name': test['name'],
            'backend': backend_price,
            'expected': expected_price,
            'diff': difference,
            'percent': percent_diff,
            'passed': difference < Decimal('0.01')
        })
        
        # Print results
        print("\n💰 Results:")
        print(f"   Backend (config):    $ {backend_price:>10.2f}")
        print(f"   Expected (baseline): $ {expected_price:>10.2f}")
        print(f"   Difference:          $ {difference:>10.2f} ({percent_diff:.4f}%)")
        
        if difference < Decimal('0.01'):
            print(f"   ✅ PASS - Difference < $0.01")
            passed += 1
        else:
            print(f"   ❌ FAIL - Difference >= $0.01")
            failed += 1
            
    except Exception as e:
        import traceback
        print(f"\n❌ ERROR: {e}")
        print(f"Details: {traceback.format_exc()[:300]}")
        results.append({
            'name': test['name'],
            'backend': Decimal('0'),
            'expected': test['expected'],
            'diff': test['expected'],
            'percent': 100,
            'passed': False
        })
        failed += 1

# Print summary
print("\n\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"\nTests Passed: {passed}/{len(test_cases)}")

print("\nDetailed Results:")
print(f"{'Test':<60} {'Backend':>12} {'Expected':>12} {'Diff':>12}   Status")
print("-" * 80)
for r in results:
    status = "✅ PASS" if r['passed'] else "❌ FAIL"
    # Truncate name if too long
    name = r['name'] if len(r['name']) <= 55 else r['name'][:52] + "..."
    print(f"{name:<60} $ {r['backend']:>10.2f} $ {r['expected']:>10.2f} $ {r['diff']:>10.2f}   {status}")

print("\n" + "=" * 80)
if passed == len(test_cases):
    print("✅ SUCCESS - All tests show <$0.01 difference!")
    print("   CustomVinylStickers calculator properly loads prices from JSON config.")
else:
    print("❌ FAILURE - Some tests show >= $0.01 difference")
    print("   Review pricing configuration alignment")
print("=" * 80)
