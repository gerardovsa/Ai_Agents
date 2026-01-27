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

from PrintedLetterheads_Shopify_Calculator import PrintedLetterheadsShopifyCalculator

# Initialize without JSON (uses hardcoded)
calculator = PrintedLetterheadsShopifyCalculator()

test_cases = [
    {'quantity': 100, 'print_sides': 'Single side print', 'print_type': 'Colour', 
     'finish_size': 'A4 - 210mm x 297mm', 'paper_stock': 'Uncoated Bond 80GSM', 'artworks': 1},
    {'quantity': 500, 'print_sides': 'Double side print', 'print_type': 'Black & White',
     'finish_size': 'A4 - 210mm x 297mm', 'paper_stock': 'Uncoated Bond 90GSM', 'artworks': 1},
    {'quantity': 1000, 'print_sides': 'Single side print', 'print_type': 'Colour',
     'finish_size': 'A4 - 210mm x 297mm', 'paper_stock': 'Uncoated Bond 100GSM', 'artworks': 2},
    {'quantity': 3000, 'print_sides': 'Double side print', 'print_type': 'Colour',
     'finish_size': 'A4 - 210mm x 297mm', 'paper_stock': 'Uncoated Bond 90GSM', 'artworks': 3}
]

print("CURRENT HARDCODED OUTPUT:")
for i, params in enumerate(test_cases, 1):
    result = calculator.calculate(**params)
    print(f"Test {i}: ${result.total_price:.2f}")
