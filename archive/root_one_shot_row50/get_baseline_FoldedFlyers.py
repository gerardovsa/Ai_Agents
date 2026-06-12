"""
Get baseline prices from hardcoded FoldedFlyers calculator
"""
import sys
from pathlib import Path

backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))

shopify_path = backend_path / 'shopify_calculators'
sys.path.insert(0, str(shopify_path))

from FoldedFlyers_Shopify_Calculator import FoldedFlyersShopifyCalculator

calc = FoldedFlyersShopifyCalculator()

# Test cases
test_cases = [
    {
        "name": "Test 1: 500 DL flyers, 150gsm gloss, 2-sided, no cello",
        "params": {
            "quantity": 500,
            "size": "DL",
            "stock_type": "gloss_150gsm",
            "print_sides": 2,
            "celloglaze": "none",
            "artworks": 1
        }
    },
    {
        "name": "Test 2: 2000 A5 flyers, 170gsm silk, 2-sided, 2-side gloss",
        "params": {
            "quantity": 2000,
            "size": "A5",
            "stock_type": "silk_170gsm",
            "print_sides": 2,
            "celloglaze": "2_side_gloss",
            "artworks": 1
        }
    },
    {
        "name": "Test 3: 10000 A4 flyers, 250gsm uncoated, 1-sided, 1-side matt",
        "params": {
            "quantity": 10000,
            "size": "A4",
            "stock_type": "uncoated_250gsm",
            "print_sides": 1,
            "celloglaze": "1_side_matt",
            "artworks": 2
        }
    },
    {
        "name": "Test 4: 50000 A6 flyers, 350gsm satin, 2-sided, no cello",
        "params": {
            "quantity": 50000,
            "size": "A6",
            "stock_type": "satin_350gsm",
            "print_sides": 2,
            "celloglaze": "none",
            "artworks": 3
        }
    }
]

print("\n" + "="*80)
print("BASELINE PRICES - FoldedFlyers (Hardcoded)")
print("="*80 + "\n")

for test in test_cases:
    try:
        result = calc.calculate(**test["params"])
        price = result.get("total_price", 0)
        print(f"{test['name']}")
        print(f"  Price: ${price:.2f}")
        print()
    except Exception as e:
        print(f"{test['name']}")
        print(f"  ERROR: {e}")
        print()
