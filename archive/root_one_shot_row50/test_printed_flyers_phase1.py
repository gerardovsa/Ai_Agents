"""
Printed Flyers - Phase 1 Website Validation Tests
Test Python calculator results against website pricing
"""

import sys
import os

# Add backend shopify_calculators directory to path
backend_path = os.path.join(os.path.dirname(__file__), 'UI', 'modules_external', 'quote-calculator', 'backend', 'shopify_calculators')
sys.path.insert(0, backend_path)

from PrintedFlyers_Shopify_Calculator import PrintedFlyersShopifyCalculator

def run_test(test_num, desc, **params):
    """Run a single test configuration"""
    calc = PrintedFlyersShopifyCalculator()
    result = calc.calculate(**params)
    
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
    print(f"Go to: https://inhouseprint.com.au/product/printed-flyers/")
    print(f"Configure:")
    print(f"  Quantity: {params['quantity']}")
    print(f"  Print Sides: {params['print_sides']}")
    print(f"  Print Type: {params['print_type']}")
    print(f"  Finish Size: {params['finish_size']}")
    print(f"  Paper Stock: {params['paper_stock']}")
    print(f"  Artworks: {params['artworks']}")
    print(f"\nExpected Website Price: ~${result.final_price:.2f} (within $0.50)")
    print(f"{'='*80}\n")
    
    return result

# TEST 1: Small quantity, standard config (tests 170% margin tier)
test1 = run_test(
    1, "Small quantity - 170% profit margin tier",
    quantity=100,
    print_sides='Double',
    print_type='Colour',
    finish_size='A5 - 148mm x 210mm',
    paper_stock='Satin 150GSM',
    artworks=1
)

# TEST 2: Medium quantity, economical config (tests B&W, single side, uncoated)
test2 = run_test(
    2, "Medium quantity - Economical B&W single sided",
    quantity=500,
    print_sides='Single',
    print_type='Black & White',
    finish_size='DL - 99mm x 210mm',
    paper_stock='Uncoated Bond 80GSM',
    artworks=1
)

# TEST 3: Bulk quantity with discount (tests ≥1000 qty 10% discount)
test3 = run_test(
    3, "Bulk quantity - 10% discount test (≥1000)",
    quantity=1000,
    print_sides='Double',
    print_type='Colour',
    finish_size='A4 - 210mm x 297mm',
    paper_stock='Satin 350GSM',
    artworks=2
)

# TEST 4: Small DL size (tests items-per-sheet=6)
test4 = run_test(
    4, "Small A6 size - items-per-sheet=8 efficiency",
    quantity=250,
    print_sides='Single',
    print_type='Colour',
    finish_size='A6 - 105mm x 148mm',
    paper_stock='Satin 128GSM',
    artworks=1
)

# TEST 5: Large format, high volume (tests A3, 1/sheet, bulk discount)
test5 = run_test(
    5, "Large format A3 - bulk volume discount",
    quantity=2000,
    print_sides='Double',
    print_type='Colour',
    finish_size='A3 - 297mm x 420mm',
    paper_stock='Satin 250GSM',
    artworks=3
)

print("\n" + "="*80)
print("PHASE 1 SUMMARY - CALCULATOR RESULTS")
print("="*80)
print(f"Test 1 (100 A5): ${test1.final_price:.2f}")
print(f"Test 2 (500 DL B&W): ${test2.final_price:.2f}")
print(f"Test 3 (1000 A4 bulk): ${test3.final_price:.2f}")
print(f"Test 4 (250 A6): ${test4.final_price:.2f}")
print(f"Test 5 (2000 A3 bulk): ${test5.final_price:.2f}")
print("="*80)
print("\nNEXT STEPS:")
print("1. Test each configuration on inhouseprint.com.au/product/printed-flyers/")
print("2. Record actual website prices")
print("3. Compare: If difference > $1, update JSON config prices")
print("4. If all match (within $1), proceed to Phase 2 (schema enhancement)")
print("="*80 + "\n")
