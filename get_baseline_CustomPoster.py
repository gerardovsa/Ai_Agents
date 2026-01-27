"""Baseline for CustomPosterPrinting"""
import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'
sys.path.insert(0, str(backend_dir))
from CustomPosterPrinting_Shopify_Calculator import CustomPosterPrintingShopifyCalculator
calc = CustomPosterPrintingShopifyCalculator()
tests = [
    {'quantity': 50, 'width_mm': 420, 'height_mm': 594, 'paper_stock': '150gsm'},
    {'quantity': 100, 'width_mm': 594, 'height_mm': 841, 'paper_stock': '200gsm'},
]
print("BASELINE:")
for i, p in enumerate(tests, 1):
    try:
        print(f"Test {i}: ${calc.calculate(**p).total_price:.2f}")
    except Exception as e:
        print(f"Test {i}: ERROR - {e}")
