"""
Test SpiralBoundBooks calculator with JSON loading
"""
import sys
from pathlib import Path

# Add paths
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))
shopify_path = backend_path / 'shopify_calculators'
sys.path.insert(0, str(shopify_path))

from SpiralBoundBooks_Shopify_Calculator import SpiralBoundBooksShopifyCalculator

print("\n" + "="*80)
print("TESTING SpiralBoundBooks Calculator")
print("="*80 + "\n")

calc = SpiralBoundBooksShopifyCalculator()

test_case = {
    "quantity": 100,
    "artworks": 1,
    "outer_front_cover": "Clear PVC",
    "printed_front_cover": "300GSM Satin",
    "cover_print_type": "2pp Colour",
    "celloglaze": "2 Sided Gloss",
    "outer_back_cover": "Clear PVC",
    "printed_back_cover": "300GSM Satin",
    "back_cover_print_type": "2pp Colour",
    "back_celloglaze": "2 Sided Matt",
    "content_pages": 50,
    "content_paper_stock": "Uncoated Bond 80GSM",
    "content_print_type": "Black & White",
    "finish_size": "A4 Portrait"
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
