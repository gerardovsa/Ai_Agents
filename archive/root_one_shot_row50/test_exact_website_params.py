import sys
from pathlib import Path

# Add backend and shopify_calculators to path FIRST
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
shopify_path = backend_path / 'shopify_calculators'
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(shopify_path))

import importlib.util

# Direct import without going through __init__.py
calc_path = shopify_path / 'SaddleStitchBooks_Shopify_Calculator.py'
spec = importlib.util.spec_from_file_location("saddle_calc", calc_path)
saddle_module = importlib.util.module_from_spec(spec)
sys.modules['saddle_calc'] = saddle_module

spec.loader.exec_module(saddle_module)
SaddleStitchBooksShopifyCalculator = saddle_module.SaddleStitchBooksShopifyCalculator

calc = SaddleStitchBooksShopifyCalculator()

# EXACT parameters from website image
print("=" * 80)
print("TEST 3: EXACT Website Parameters")
print("=" * 80)
print("Quantity: 500")
print("Finish Size: A5 Portrait")
print("Artworks: 1")
print("Cover Option: Self Cover")
print("Printed Pages: 32pp")
print("Content Print Type: Black & White")
print("Content Stock Type: Uncoated Bond 80GSM")
print("=" * 80)

# Call with EXACT parameters - BUT WAIT, self cover doesn't need cover stock/print!
result = calc.calculate(
    quantity='500',
    finish_size='A5 Portrait',
    artworks=1,
    cover_option='Self Cover',
    printed_pages='32pp',
    content_print_type='Black & White',
    content_stock_type='Uncoated Bond 80GSM',
    # These are ignored for Self Cover but need defaults:
    cover_stock='Satin 250GSM',
    cover_print_type='2 side colour (4pp)',
    celloglaze='None'
)

print(f"\nBackend Total: ${result.total_price:.2f}")
print(f"Website Total: $832.84")
print(f"Difference: ${float(result.total_price) - 832.84:.2f}")
print(f"\nUnit Price: ${result.unit_price:.2f}")
print(f"\nDETAILED BREAKDOWN:")
print(f"  Setup costs: ${result.breakdown['setup_costs']:.2f}")
print(f"  Cello setup: ${result.breakdown['cello_setup']:.2f}")
print(f"  Total setup: ${result.breakdown['total_setup']:.2f}")
print(f"  Cover cost: ${result.breakdown['cover_cost']:.2f}")
print(f"  Celloglaze cost: ${result.breakdown['celloglaze_cost']:.2f}")
print(f"  Content cost: ${result.breakdown['content_cost']:.2f}")
print(f"  Cutting cost: ${result.breakdown['cutting_cost']:.2f}")
print(f"  Binding cost: ${result.breakdown['binding_cost']:.2f}")
print(f"  Subtotal before margin: ${result.breakdown['subtotal_before_margin']:.2f}")
print(f"  Profit margin %: {result.breakdown['profit_margin_pct']:.2f}%")
print(f"  Subtotal with margin: ${result.breakdown['subtotal_with_margin']:.2f}")
print(f"  First GST (10%): ${result.breakdown['first_gst_10pct']:.2f}")
print(f"  Total after first GST: ${result.breakdown['total_after_first_gst']:.2f}")
print(f"  Second GST (10%): ${result.breakdown['second_gst_10pct']:.2f}")
print(f"  TOTAL INC DOUBLE GST: ${result.breakdown['total_inc_double_gst']:.2f}")
print(f"\nSPECS:")
print(f"  Cover sheets: {result.specifications['cover_sheets']:.2f}")
print(f"  Content sheets: {result.specifications['content_sheets']:.2f}")
print(f"  Total sheets: {result.specifications['total_sheets_printed']:.2f}")
print(f"  Pages sheet count (from JSON): {result.specifications['pages_sheet_count']:.2f}")

# Manual calculation to verify
print("\n" + "=" * 80)
print("MANUAL CALCULATION VERIFICATION:")
print("=" * 80)
print("Setup: $15 (impos) + $12 (guilo) + $30 (binder) = $57")
print("Cover: $0 (self cover)")
print("Content: 500 qty × 8 sheets (32pp) × 1.05 waste × 0.5 (A5) = 2100 sheets")
print("  Content stock: 2100 × $0.03 (Bond 80GSM) = $63.00")
print("  Content print: 2100 × $0.01 (B&W) = $21.00")
print("  Total content: $84.00")
print("Cutting: 2100 sheets / 500 × $11 = $46.20")
print("Binding: ((2100 / 5000) × $60) + (500 × $0.20) = $25.20 + $100 = $125.20")
print("-" * 80)
print("SUBTOTAL: $57 + $0 + $84 + $46.20 + $125.20 = $312.40")
print("Profit margin (300-499 tier): 104%")
print("Subtotal with margin: $312.40 × 2.04 = $637.30")
print("First GST: $637.30 × 1.1 = $701.03")
print("Second GST: $701.03 × 1.1 = $771.13")
print("=" * 80)

print("\n🔍 DISCREPANCY ANALYSIS:")
print(f"Website shows: $832.84")
print(f"Backend shows: ${result.total_price:.2f}")
print(f"Difference: ${832.84 - float(result.total_price):.2f}")
print(f"\nWorking backwards from website price:")
print(f"$832.84 / 1.1 (2nd GST) = $757.13")
print(f"$757.13 / 1.1 (1st GST) = $688.30")
print(f"$688.30 / 2.04 (1+104% margin) = $337.40 <- IMPLIED SUBTOTAL")
print(f"\nOur calculated subtotal: $312.40")
print(f"Difference in subtotal: ${337.40 - 312.40:.2f}")
print(f"\n⚠️  Website has $25 EXTRA in subtotal somewhere!")
print(f"\nPossible causes:")
print(f"  1. Website using wrong content stock price")
print(f"  2. Website adding extra setup cost")
print(f"  3. Website has different A5 calculation")
print(f"  4. Website has bug with Self Cover + A5 combo")
