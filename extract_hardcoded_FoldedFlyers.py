"""
Extract hardcoded prices from FoldedFlyers calculator
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))

# Add shopify_calculators to path
shopify_path = backend_path / 'shopify_calculators'
sys.path.insert(0, str(shopify_path))

from FoldedFlyers_Shopify_Calculator import FoldedFlyersShopifyCalculator

print("\n" + "="*80)
print("HARDCODED PRICES - FoldedFlyers Calculator")
print("="*80)

calc = FoldedFlyersShopifyCalculator()

# Check if methods exist
if hasattr(calc, '_get_stock_price'):
    print("\n✅ Has _get_stock_price() method")
else:
    print("\n❌ No _get_stock_price() method")

if hasattr(calc, '_get_print_cost'):
    print("✅ Has _get_print_cost() method")
else:
    print("❌ No _get_print_cost() method")

if hasattr(calc, '_get_folding_cost'):
    print("✅ Has _get_folding_cost() method")
else:
    print("❌ No _get_folding_cost() method")

if hasattr(calc, '_get_celloglaze_cost'):
    print("✅ Has _get_celloglaze_cost() method")
else:
    print("❌ No _get_celloglaze_cost() method")

# Check config loading
print(f"\n📁 Config loaded: {calc.config is not None}")
if calc.config:
    print(f"   Config keys: {list(calc.config.keys())}")

print("\n" + "="*80)
