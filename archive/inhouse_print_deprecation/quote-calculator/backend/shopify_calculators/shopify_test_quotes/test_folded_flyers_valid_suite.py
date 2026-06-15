"""
Folded Flyers Phase 1 Test Suite - VALID CONFIGURATIONS ONLY
Respects website restrictions:
1. NO DL size (removed from backend Jan 26, 2026)
2. Celloglaze ONLY on Satin 250/300/350GSM (not 128/150 or Uncoated)
3. Size-specific fold types:
   - A5: Half fold to A6 ONLY
   - A4: Half fold to A5, Tri Roll fold to DL, Tri Z fold to DL
   - A3: Half fold to A4, Crash fold to A5(Half then half), Crash fold to DL(Half then roll)
   - 6pp A4: Tri Roll fold to A4 ONLY
"""

import sys
from pathlib import Path

# Add backend path (parent directory contains calculator modules)
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from FoldedFlyers_Shopify_Calculator import (
    FoldedFlyersShopifyCalculator,
    FinishSize, PaperStock, PrintSides, PrintType, FoldType, Celloglaze
)

def run_test(test_num, config, expected_price):
    """Run a single test configuration"""
    print(f"\n{'='*80}")
    print(f"TEST {test_num}: {config.get('name', 'Unnamed Test')}")
    print(f"{'='*80}")
    
    calc = FoldedFlyersShopifyCalculator()
    result = calc.calculate_quote(**config['params'])
    
    backend_price = result.final_price
    difference = abs(backend_price - expected_price)
    percent_diff = (difference / expected_price * 100) if expected_price > 0 else 0
    
    print(f"\n📋 Configuration:")
    for key, value in config['params'].items():
        if hasattr(value, 'value'):
            print(f"  {key}: {value.value[0]}")
        else:
            print(f"  {key}: {value}")
    
    print(f"\n💰 Backend Calculator Result: ${backend_price:.2f}")
    print(f"💰 Expected Website Price: ${expected_price:.2f}")
    print(f"📊 Difference: ${difference:.2f} ({percent_diff:.1f}%)")
    
    if difference <= 0.50:
        print(f"[PASS] Within acceptable range")
        return True
    else:
        print(f"[FAIL] Exceeds $0.50 threshold")
        return False

# TEST SUITE
print("="*80)
print("FOLDED FLYERS - VALID TEST SUITE (Jan 26, 2026)")
print("="*80)

tests = []

# TEST 1: A5 Basic - Half fold only (no celloglaze on 150GSM)
test1 = {
    'name': 'A5 half fold double colour Satin 150GSM',
    'params': {
        'quantity': 500,
        'finish_size': FinishSize.A5,
        'paper_stock': PaperStock.SATIN_150GSM,  # NO celloglaze allowed
        'print_sides': PrintSides.DOUBLE_SIDE,
        'print_type': PrintType.COLOUR,
        'fold_type': FoldType.HALF_FOLD_TO_A6,  # Only valid fold for A5
        'celloglaze': Celloglaze.NONE,  # MUST be None (150GSM not eligible)
        'artworks': 1
    }
}

# TEST 2: A4 with celloglaze (premium stock 300GSM)
test2 = {
    'name': 'A4 half fold + 2-side matt cello Satin 300GSM',
    'params': {
        'quantity': 1000,
        'finish_size': FinishSize.A4,
        'paper_stock': PaperStock.SATIN_300GSM,  # Celloglaze allowed
        'print_sides': PrintSides.DOUBLE_SIDE,
        'print_type': PrintType.COLOUR,
        'fold_type': FoldType.HALF_FOLD_TO_A5,  # Valid for A4
        'celloglaze': Celloglaze.TWO_SIDE_MATT,  # OK on 300GSM
        'artworks': 1
    }
}

# TEST 3: A5 Uncoated (no celloglaze option exists)
test3 = {
    'name': 'A5 half fold single B&W Uncoated 100GSM',
    'params': {
        'quantity': 250,
        'finish_size': FinishSize.A5,
        'paper_stock': PaperStock.UNCOATED_100GSM,  # NO celloglaze on Uncoated
        'print_sides': PrintSides.SINGLE_SIDE,
        'print_type': PrintType.BLACK_WHITE,
        'fold_type': FoldType.HALF_FOLD_TO_A6,  # Only valid fold for A5
        'celloglaze': Celloglaze.NONE,  # MUST be None (Uncoated not eligible)
        'artworks': 1
    }
}

# TEST 4: A3 with celloglaze (premium stock 350GSM)
test4 = {
    'name': 'A3 crash fold + 1-side gloss cello Satin 350GSM',
    'params': {
        'quantity': 500,
        'finish_size': FinishSize.A3,
        'paper_stock': PaperStock.SATIN_350GSM,  # Celloglaze allowed
        'print_sides': PrintSides.DOUBLE_SIDE,
        'print_type': PrintType.COLOUR,
        'fold_type': FoldType.CRASH_FOLD_TO_A5_HALF,  # Valid for A3
        'celloglaze': Celloglaze.ONE_SIDE_GLOSS,  # OK on 350GSM
        'artworks': 1
    }
}

# TEST 5: A4 Tri-fold (no celloglaze on 128GSM)
test5 = {
    'name': 'A4 tri-roll fold double colour Satin 128GSM',
    'params': {
        'quantity': 1000,
        'finish_size': FinishSize.A4,
        'paper_stock': PaperStock.SATIN_128GSM,  # NO celloglaze allowed
        'print_sides': PrintSides.DOUBLE_SIDE,
        'print_type': PrintType.COLOUR,
        'fold_type': FoldType.TRI_ROLL_FOLD_TO_DL,  # Valid for A4
        'celloglaze': Celloglaze.NONE,  # MUST be None (128GSM not eligible)
        'artworks': 1
    }
}

# TEST 6: 6pp A4 large format (no celloglaze on 128GSM)
test6 = {
    'name': '6pp A4 tri-roll fold double colour Satin 128GSM',
    'params': {
        'quantity': 250,
        'finish_size': FinishSize.A4_6PP,
        'paper_stock': PaperStock.SATIN_128GSM,  # NO celloglaze allowed
        'print_sides': PrintSides.DOUBLE_SIDE,
        'print_type': PrintType.COLOUR,
        'fold_type': FoldType.TRI_ROLL_FOLD_TO_A4,  # Only valid fold for 6pp A4
        'celloglaze': Celloglaze.NONE,  # MUST be None (128GSM not eligible)
        'artworks': 1
    }
}

# Run all tests
calc = FoldedFlyersShopifyCalculator()

print("\n\n" + "="*80)
print("RUNNING ALL TESTS...")
print("="*80)

# Calculate expected prices first
test_configs = [test1, test2, test3, test4, test5, test6]
expected_prices = []

for i, test in enumerate(test_configs, 1):
    result = calc.calculate_quote(**test['params'])
    expected_prices.append(result.final_price)
    print(f"\nTest {i}: {test['name']}")
    print(f"  Expected: ${result.final_price:.2f}")

# Display all tests for user validation
print("\n\n" + "="*80)
print("TESTS TO VALIDATE ON WEBSITE")
print("="*80)

for i, (test, price) in enumerate(zip(test_configs, expected_prices), 1):
    print(f"\n{'='*80}")
    print(f"TEST {i}: {test['name']}")
    print(f"{'='*80}")
    print(f"Expected Price: ${price:.2f}\n")
    print("Configuration:")
    params = test['params']
    print(f"  Quantity: {params['quantity']}")
    print(f"  Finish Size: {params['finish_size'].value[0]}")
    print(f"  Paper Stock: {params['paper_stock'].value[0]}")
    print(f"  Print Sides: {'Double' if params['print_sides'] == PrintSides.DOUBLE_SIDE else 'Single'}")
    print(f"  Print Type: {params['print_type'].value}")
    print(f"  Fold Type: {params['fold_type'].value[0]}")
    print(f"  Celloglaze: {params['celloglaze'].value[0]}")
    print(f"  Artworks: {params['artworks']}")
    
    # Validation notes
    stock_name = params['paper_stock'].value[0]
    cello = params['celloglaze']
    
    if cello != Celloglaze.NONE:
        if '250GSM' in stock_name or '300GSM' in stock_name or '350GSM' in stock_name:
            print(f"  [OK] Celloglaze valid (premium stock)")
        else:
            print(f"  [WARNING] Celloglaze on non-premium stock (should be None)")
    else:
        print(f"  [OK] No celloglaze (correct for this stock)")

print("\n\n" + "="*80)
print("CRITICAL VALIDATION CHECKLIST")
print("="*80)
print("""
Before testing on website, verify each test follows these rules:

1. [OK] NO DL SIZE - All tests use A5, A4, A3, or 6pp A4
2. [OK] CELLOGLAZE RESTRICTIONS:
   - Tests 1,3,5,6: NO celloglaze (Satin 128/150GSM or Uncoated)
   - Tests 2,4: Celloglaze allowed (Satin 300/350GSM)
3. [OK] SIZE-SPECIFIC FOLD TYPES:
   - Test 1,3: A5 -> Half fold to A6 (ONLY option)
   - Test 2: A4 -> Half fold to A5 (valid)
   - Test 5: A4 -> Tri Roll fold to DL (valid)
   - Test 4: A3 -> Crash fold to A5 (valid)
   - Test 6: 6pp A4 -> Tri Roll fold to A4 (ONLY option)

4. NEXT STEPS:
   a) Test each configuration on website
   b) Compare website price to expected price
   c) If all within $0.50, Phase 1 complete
   d) If any differ >$1, update JSON config and re-test
""")

print("\n" + "="*80)
print("SUMMARY TABLE")
print("="*80)
print(f"{'Test':<6} {'Size':<8} {'Stock':<20} {'Cello':<15} {'Expected':<12}")
print("-"*80)
for i, (test, price) in enumerate(zip(test_configs, expected_prices), 1):
    params = test['params']
    size = params['finish_size'].value[0].split(' - ')[0]
    stock = params['paper_stock'].value[0][:18]
    cello = "Yes" if params['celloglaze'] != Celloglaze.NONE else "No"
    print(f"{i:<6} {size:<8} {stock:<20} {cello:<15} ${price:<11.2f}")
