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

# TEST 1: Expected $351.28, Website shows $355.55
print("=" * 80)
print("TEST 1: Basic Order (100 books)")
print("=" * 80)
result = calc.calculate(
    quantity='100',
    artworks=1,
    cover_option='Hard Cover',
    cover_stock='Satin 250GSM',
    cover_print_type='2 side colour (4pp)',
    celloglaze='None',
    printed_pages='16pp',
    finish_size='A4 Portrait',
    content_print_type='Black & White',
    content_stock_type='Uncoated Bond 80GSM'
)

print(f"Backend Total: ${result.total_price:.2f}")
print(f"Website Total: $355.55")
print(f"Difference: ${float(result.total_price) - 355.55:.2f}")
print(f"\nUnit Price: ${result.unit_price:.2f}")
print(f"\nBREAKDOWN:")
for key, val in result.breakdown.items():
    print(f"  {key}: ${val:.2f}")
print(f"\nSPECS:")
print(f"  Cover sheets: {result.specifications['cover_sheets']:.2f}")
print(f"  Content sheets: {result.specifications['content_sheets']:.2f}")
print(f"  Total sheets: {result.specifications['total_sheets_printed']:.2f}")

# TEST 3: Expected $771.13, Website shows $832.84
print("\n" + "=" * 80)
print("TEST 3: Self Cover & A5 Size (500 books)")
print("=" * 80)
result3 = calc.calculate(
    quantity='500',
    artworks=1,
    cover_option='Self Cover',
    printed_pages='32pp',
    finish_size='A5 Portrait',
    content_print_type='Black & White',
    content_stock_type='Uncoated Bond 80GSM'
)

print(f"Backend Total: ${result3.total_price:.2f}")
print(f"Website Total: $832.84")
print(f"Difference: ${float(result3.total_price) - 832.84:.2f}")
print(f"\nUnit Price: ${result3.unit_price:.2f}")
print(f"\nBREAKDOWN:")
for key, val in result3.breakdown.items():
    print(f"  {key}: ${val:.2f}")
print(f"\nSPECS:")
print(f"  Cover sheets: {result3.specifications['cover_sheets']:.2f}")
print(f"  Content sheets: {result3.specifications['content_sheets']:.2f}")
print(f"  Total sheets: {result3.specifications['total_sheets_printed']:.2f}")
