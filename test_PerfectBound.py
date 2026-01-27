"""
Test PerfectBound calculator
"""
import sys
from pathlib import Path

# Add paths
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))
shopify_path = backend_path / 'shopify_calculators'
sys.path.insert(0, str(shopify_path))

from PerfectBound_Shopify_Calculator import PerfectBoundShopifyCalculator

print("\n" + "="*80)
print("TESTING PerfectBound Calculator")
print("="*80 + "\n")

calc = PerfectBoundShopifyCalculator()

test_case = {
    "quantity": 100,
    "printed_pages": 48,
    "proof_requirements": "Digital Emailed Proof",
    "cover_stock": "Satin 300GSM",
    "cover_print_type": "2 side colour (4pp)",
    "celloglaze": "2 side Matt (outside only)",
    "finish_size": "A5 Portrait",
    "content_print_type": "Black & White",
    "content_stock_type": "Uncoated Bond 80GSM"
}

try:
    result = calc.calculate(**test_case)
    print(f"✅ Calculator working!")
    print(f"   Quantity: {test_case['quantity']}")
    print(f"   Total Price: ${result.total_price:.2f}")
    print(f"   Unit Price: ${result.unit_price:.2f}")
    print(f"\n   Breakdown:")
    for key, value in result.breakdown.items():
        print(f"     {key}: ${value:.2f}")
except Exception as e:
    import traceback
    print(f"❌ ERROR: {e}")
    print(traceback.format_exc())

print("\n" + "="*80)
