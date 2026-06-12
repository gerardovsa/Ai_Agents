"""
Quick verification test for remaining calculators
"""
import sys
from pathlib import Path

backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))
shopify_path = backend_path / 'shopify_calculators'
sys.path.insert(0, str(shopify_path))

print("\n" + "="*80)
print("QUICK VERIFICATION TEST - Remaining Calculators")
print("="*80 + "\n")

calculators = []

# SaddleStitch
try:
    from SaddleStitch_Shopify_Calculator import SaddleStitchShopifyCalculator
    calc = SaddleStitchShopifyCalculator()
    result = calc.calculate(
        quantity=100,
        printed_pages=16,
        proof_requirements="Digital Emailed Proof",
        cover_stock="Satin 250GSM",
        cover_print_type="4pp colour",
        celloglaze="None",
        finish_size="A5 Portrait",
        content_print_type="Black & White",
        content_stock_type="Uncoated Bond 80GSM"
    )
    print(f"✅ SaddleStitch: ${result.total_price:.2f}")
    calculators.append(("SaddleStitch", True, None))
except Exception as e:
    print(f"❌ SaddleStitch: {e}")
    calculators.append(("SaddleStitch", False, str(e)))

print("\n" + "="*80)
print("SUMMARY:")
for name, success, error in calculators:
    if success:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}: {error}")
print("="*80)
