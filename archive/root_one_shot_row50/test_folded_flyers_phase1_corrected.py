"""
Folded Flyers - Phase 1 CORRECTED Tests (Replacing Invalid DL Tests)
Tests 1 & 5 FAILED - DL not available on website
Tests 2, 3, 4 PASSED - Exact match

New tests to replace failed DL tests
"""

import sys
import os

backend_path = os.path.join(os.path.dirname(__file__), 'UI', 'modules_external', 'quote-calculator', 'backend', 'shopify_calculators')
sys.path.insert(0, backend_path)

from FoldedFlyers_Shopify_Calculator import FoldedFlyersShopifyCalculator
from FoldedFlyers_Shopify_Calculator import PrintSides, PrintType, FinishSize, PaperStock, FoldType, Celloglaze

def run_test(test_num, desc, **params):
    """Run a single test configuration"""
    calc = FoldedFlyersShopifyCalculator()
    result = calc.calculate_quote(**params)
    
    print(f"\n{'='*80}")
    print(f"TEST {test_num}: {desc}")
    print(f"{'='*80}")
    print(f"Configuration:")
    for key, value in params.items():
        if hasattr(value, 'value'):
            print(f"  {key}: {value.value}")
        else:
            print(f"  {key}: {value}")
    print(f"\nBackend Calculator Result:")
    print(f"  Total Price (inc GST): ${result.final_price:.2f}")
    print(f"  Unit Price: ${result.final_price / params['quantity']:.4f}")
    print(f"\nExpected Website Price: ~${result.final_price:.2f} (within $0.50)")
    print(f"{'='*80}\n")
    
    return result

print("\n" + "="*80)
print("REPLACEMENT TESTS FOR FAILED DL CONFIGURATIONS")
print("="*80)
print("Original Test 1 (500 DL) - FAILED: DL not available on website")
print("Original Test 5 (1000 DL B&W) - FAILED: DL not available on website")
print("\nCreating replacement tests with valid sizes...\n")

# REPLACEMENT TEST 1A: A5 tri-fold (similar to DL but valid)
test1a = run_test(
    "1A", "A5 half fold double colour - replaces DL test",
    quantity=500,
    print_sides=PrintSides.DOUBLE_SIDE,
    print_type=PrintType.COLOUR,
    finish_size=FinishSize.A5,
    paper_stock=PaperStock.SATIN_150GSM,
    artworks=1,
    fold_type=FoldType.HALF_FOLD_TO_A6,
    celloglaze=Celloglaze.NONE
)

# REPLACEMENT TEST 5A: A5 single side B&W with celloglaze (economical like DL test)
test5a = run_test(
    "5A", "A5 single B&W with matt cello - replaces DL test",
    quantity=1000,
    print_sides=PrintSides.SINGLE_SIDE,
    print_type=PrintType.BLACK_WHITE,
    finish_size=FinishSize.A5,
    paper_stock=PaperStock.SATIN_128GSM,
    artworks=1,
    fold_type=FoldType.HALF_FOLD_TO_A6,
    celloglaze=Celloglaze.ONE_SIDE_MATT
)

# ALTERNATIVE: 6pp A4 large format test
test6 = run_test(
    6, "6pp A4 crash fold - large format test",
    quantity=250,
    print_sides=PrintSides.DOUBLE_SIDE,
    print_type=PrintType.COLOUR,
    finish_size=FinishSize.A4_6PP,
    paper_stock=PaperStock.SATIN_300GSM,
    artworks=1,
    fold_type=FoldType.CRASH_FOLD_TO_A5_HALF,
    celloglaze=Celloglaze.NONE
)

print("\n" + "="*80)
print("COMPLETE TEST SUITE SUMMARY")
print("="*80)
print("✅ Test 2 (1000 A4 + cello): $621.83 - VALIDATED")
print("✅ Test 3 (250 A5 uncoated): $158.44 - VALIDATED")
print("✅ Test 4 (5000 A4 bulk): $802.52 - VALIDATED")
print(f"🔄 Test 1A (500 A5 half fold): ${test1a.final_price:.2f} - NEW (replaces DL)")
print(f"🔄 Test 5A (1000 A5 B&W + cello): ${test5a.final_price:.2f} - NEW (replaces DL)")
print(f"➕ Test 6 (250 6pp A4): ${test6.final_price:.2f} - BONUS (large format)")
print("="*80)
print("\nNEXT STEPS:")
print("1. Test replacement configurations on website")
print("2. If all match, proceed to Phase 2 (schema enhancement)")
print("3. CRITICAL: Remove DL from calculator enum - not valid for folded flyers")
print("="*80 + "\n")
