"""Get baseline hardcoded output for NotepadsA5"""
import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'
sys.path.insert(0, str(backend_dir))
from NotepadsA5_Shopify_Calculator import NotepadsA5ShopifyCalculator
calc = NotepadsA5ShopifyCalculator()
tests = [
    {'quantity': 100, 'artworks': 1, 'finish_size': 'A5 Portrait', 'leaves_per_pad': 50, 'print_type': 'Black & White 1 sided', 'stock_type': 'Uncoated Bond 80GSM'},
    {'quantity': 500, 'artworks': 1, 'finish_size': 'A5 Portrait', 'leaves_per_pad': 100, 'print_type': 'Colour 2 sided', 'stock_type': 'Uncoated Bond 90GSM'},
    {'quantity': 1000, 'artworks': 2, 'finish_size': 'A5 Portrait', 'leaves_per_pad': 50, 'print_type': 'Colour 1 sided', 'stock_type': 'Uncoated Bond 100GSM'},
    {'quantity': 2000, 'artworks': 3, 'finish_size': 'A5 Portrait', 'leaves_per_pad': 100, 'print_type': 'Black & White 2 sided', 'stock_type': 'Revive 100% Recycled 80GSM Bond'}
]
print("BASELINE:")
for i, p in enumerate(tests, 1):
    print(f"Test {i}: ${calc.calculate(**p).total_price:.2f}")
