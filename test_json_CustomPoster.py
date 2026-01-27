"""Test CustomPosterPrinting JSON vs hardcoded"""
import sys
from pathlib import Path
from decimal import Decimal
backend_dir = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
calculators_dir = backend_dir / 'shopify_calculators'
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent))
sys.path.insert(0, str(calculators_dir))
from CustomPosterPrinting_Shopify_Calculator import CustomPosterPrintingShopifyCalculator

config_path = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'config' / 'shopify' / 'Shopify_Custom_Poster_Printing.json'
calc = CustomPosterPrintingShopifyCalculator(config_path=str(config_path))

tests = [
    ({'quantity': 50, 'width_mm': 420, 'height_mm': 594, 'paper_stock': '150gsm'}, Decimal('98.73')),
    ({'quantity': 100, 'width_mm': 594, 'height_mm': 841, 'paper_stock': '200gsm'}, Decimal('115.79')),
]

passed = 0
for i, (params, expected) in enumerate(tests, 1):
    try:
        result = calc.calculate(**params)
        diff = abs(result.total_price - expected)
        status = "✅" if diff < Decimal('0.01') else "❌"
        print(f"Test {i}: ${result.total_price:.2f} vs ${expected:.2f} - {status}")
        if diff < Decimal('0.01'):
            passed += 1
    except Exception as e:
        print(f"Test {i}: ERROR - {e}")

print(f"\nSUMMARY: {passed}/{len(tests)} passed")
if passed == len(tests):
    print("🎉 ALL TESTS PASSED")
