"""Test NotepadsA5 JSON vs hardcoded"""
import sys
from pathlib import Path
from decimal import Decimal
backend_dir = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
calculators_dir = backend_dir / 'shopify_calculators'
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent))
sys.path.insert(0, str(calculators_dir))
from NotepadsA5_Shopify_Calculator import NotepadsA5ShopifyCalculator

config_path = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'config' / 'shopify' / 'Shopify_Notepads_A5.json'
calc = NotepadsA5ShopifyCalculator(config_path=str(config_path))

tests = [
    ({'quantity': 100, 'artworks': 1, 'finish_size': 'A5 Portrait', 'leaves_per_pad': 50, 'print_type': 'Black & White 1 sided', 'stock_type': 'Uncoated Bond 80GSM'}, Decimal('294.85')),
    ({'quantity': 500, 'artworks': 1, 'finish_size': 'A5 Portrait', 'leaves_per_pad': 100, 'print_type': 'Colour 2 sided', 'stock_type': 'Uncoated Bond 90GSM'}, Decimal('4461.83')),
    ({'quantity': 1000, 'artworks': 2, 'finish_size': 'A5 Portrait', 'leaves_per_pad': 50, 'print_type': 'Colour 1 sided', 'stock_type': 'Uncoated Bond 100GSM'}, Decimal('4001.02')),
    ({'quantity': 2000, 'artworks': 3, 'finish_size': 'A5 Portrait', 'leaves_per_pad': 100, 'print_type': 'Black & White 2 sided', 'stock_type': 'Revive 100% Recycled 80GSM Bond'}, Decimal('10579.08'))
]

passed = 0
for i, (params, expected) in enumerate(tests, 1):
    result = calc.calculate(**params)
    diff = abs(result.total_price - expected)
    status = "✅ PASS" if diff < Decimal('0.01') else "❌ FAIL"
    print(f"Test {i}: ${result.total_price:.2f} vs ${expected:.2f} - {status}")
    if diff < Decimal('0.01'):
        passed += 1

print(f"\nSUMMARY: {passed}/{len(tests)} tests passed")
if passed == len(tests):
    print("🎉 ALL TESTS PASSED")
