"""
Get CURRENT hardcoded calculator output (baseline for tests)
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add paths
backend_dir = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
calculators_dir = backend_dir / 'shopify_calculators'
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(calculators_dir))

from NotepadsA4_Shopify_Calculator import NotepadsA4ShopifyCalculator

# Initialize without JSON (uses hardcoded)
calculator = NotepadsA4ShopifyCalculator()

test_cases = [
    {'quantity': 100, 'artworks': 1, 'finish_size': 'A4 Portrait', 'leaves_per_pad': 50,
     'print_type': 'Black & White 1 sided', 'stock_type': 'Uncoated Bond 80GSM'},
    {'quantity': 500, 'artworks': 1, 'finish_size': 'A4 Portrait', 'leaves_per_pad': 100,
     'print_type': 'Colour 2 sided', 'stock_type': 'Uncoated Bond 90GSM'},
    {'quantity': 1000, 'artworks': 2, 'finish_size': 'A4 Portrait', 'leaves_per_pad': 50,
     'print_type': 'Colour 1 sided', 'stock_type': 'Uncoated Bond 100GSM'},
    {'quantity': 2000, 'artworks': 3, 'finish_size': 'A4 Portrait', 'leaves_per_pad': 100,
     'print_type': 'Black & White 2 sided', 'stock_type': 'Revive 100% Recycled 80GSM Bond'}
]

print("CURRENT HARDCODED OUTPUT:")
for i, params in enumerate(test_cases, 1):
    result = calculator.calculate(**params)
    print(f"Test {i}: ${result.total_price:.2f}")
