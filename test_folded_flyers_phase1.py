"""
Folded Flyers - Phase 1 Website Validation Tests
Test Python calculator results against website pricing
"""

import sys
import os

# Add backend shopify_calculators directory to path
backend_path = os.path.join(os.path.dirname(__file__), 'UI', 'modules_external', 'quote-calculator', 'backend', 'shopify_calculators')
sys.path.insert(0, backend_path)

from FoldedFlyers_Shopify_Calculator import FoldedFlyersShopifyCalculator

def run_test(test_num, desc, **params):
    """Run a single test configuration"""
    calc = FoldedFlyersShopifyCalculator()
    result = calc.calculate_quote(**params)
    
    print(f"\n{'='*80}")
    print(f"TEST {test_num}: {desc}")
    print(f"{'='*80}")
    print(f"Configuration:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    print(f"\nBackend Calculator Result:")
    print(f"  Total Price (inc GST): ${result.final_price:.2f}")
    print(f"  Unit Price: ${result.final_price / params['quantity']:.4f}")
    print(f"\n>>> WEBSITE TEST REQUIRED <<<")
    print(f"Go to: https://inhouseprint.com.au/product/folded-flyers/")
    print(f"Configure:")
    for key, value in params.items():
        # Convert enum values to readable strings
        if hasattr(value, 'value'):
            print(f"  {key}: {value.value}")
        else:
            print(f"  {key}: {value}")
    print(f"\nExpected Website Price: ~${result.final_price:.2f} (within $0.50)")
    print(f"{'='*80}\n")
    
    return result

# Import enums
from FoldedFlyers_Shopify_Calculator import PrintSides, PrintType, FinishSize, PaperStock, FoldType, Celloglaze

# TEST 1: Standard DL folded, tri-fold (most common)
test1 = run_test(
    1, "Standard DL tri-fold - most common config",
    quantity=500,
    print_sides=PrintSides.DOUBLE_SIDE,
    print_type=PrintType.COLOUR,
    finish_size=FinishSize.DL,
    paper_stock=PaperStock.SATIN_150GSM,
    artworks=1,
    fold_type=FoldType.TRI_Z_FOLD_TO_DL,
    celloglaze=Celloglaze.NONE
)

# TEST 2: A4 half fold with celloglaze (premium marketing piece)
test2 = run_test(
    2, "A4 half fold with 2-side gloss - premium",
    quantity=1000,
    print_sides=PrintSides.DOUBLE_SIDE,
    print_type=PrintType.COLOUR,
    finish_size=FinishSize.A4,
    paper_stock=PaperStock.SATIN_250GSM,
    artworks=1,
    fold_type=FoldType.HALF_FOLD_TO_A5,
    celloglaze=Celloglaze.TWO_SIDE_GLOSS
)

# TEST 3: A5 crash fold, economical stock (budget brochure)
test3 = run_test(
    3, "A5 crash fold uncoated - budget brochure",
    quantity=250,
    print_sides=PrintSides.DOUBLE_SIDE,
    print_type=PrintType.COLOUR,
    finish_size=FinishSize.A5,
    paper_stock=PaperStock.UNCOATED_100GSM,
    artworks=1,
    fold_type=FoldType.HALF_FOLD_TO_A6,
    celloglaze=Celloglaze.NONE
)

# TEST 4: High volume A4, half fold (bulk order test)
test4 = run_test(
    4, "High volume A4 half fold - bulk test",
    quantity=5000,
    print_sides=PrintSides.DOUBLE_SIDE,
    print_type=PrintType.COLOUR,
    finish_size=FinishSize.A4,
    paper_stock=PaperStock.SATIN_128GSM,
    artworks=2,
    fold_type=FoldType.HALF_FOLD_TO_A5,
    celloglaze=Celloglaze.NONE
)

# TEST 5: DL single side B&W with matt celloglaze (economical test)
test5 = run_test(
    5, "DL single side B&W with matt - economical",
    quantity=1000,
    print_sides=PrintSides.SINGLE_SIDE,
    print_type=PrintType.BLACK_WHITE,
    finish_size=FinishSize.DL,
    paper_stock=PaperStock.SATIN_128GSM,
    artworks=1,
    fold_type=FoldType.TRI_ROLL_FOLD_TO_DL,
    celloglaze=Celloglaze.ONE_SIDE_MATT
)

print("\n" + "="*80)
print("PHASE 1 SUMMARY - CALCULATOR RESULTS")
print("="*80)
print(f"Test 1 (500 DL tri-fold): ${test1.final_price:.2f}")
print(f"Test 2 (1000 A4 half fold + cello): ${test2.final_price:.2f}")
print(f"Test 3 (250 A5 half fold uncoated): ${test3.final_price:.2f}")
print(f"Test 4 (5000 A4 bulk 2 artworks): ${test4.final_price:.2f}")
print(f"Test 5 (1000 DL B&W + matt cello): ${test5.final_price:.2f}")
print("="*80)
print("\nNEXT STEPS:")
print("1. Test each configuration on inhouseprint.com.au/product/folded-flyers/")
print("2. Record actual website prices")
print("3. Compare: If difference > $1, update JSON config prices")
print("4. If all match (within $1), proceed to Phase 2 (schema enhancement)")
print("="*80 + "\n")
