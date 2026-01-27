"""
Analyze Folded Flyers pricing discrepancy between backend calculator and validated website prices
"""

import sys
from pathlib import Path

# Add implementations path
sys.path.insert(0, str(Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'))

from calculator_wrapper import calculate_folded_flyers_shopify

# Validated website prices from FOLDED_FLYERS_AI_TEST_CONFIGURATIONS.md (Jan 26, 2026)
tests = [
    {
        "name": "Test 1: A5 Half Fold Double Colour Satin 150GSM",
        "params": {
            "quantity": 500,
            "finish_size": "A5 - 148mm x 210mm",
            "paper_stock": "Satin 150GSM",
            "print_sides": "Double",
            "print_type": "Colour",
            "fold_type": "Half fold to A6",
            "celloglaze": "None",
            "artworks": 1
        },
        "website_price": 205.22
    },
    {
        "name": "Test 2: A4 Half Fold with Celloglaze Satin 300GSM",
        "params": {
            "quantity": 1000,
            "finish_size": "A4 - 210mm x 297mm",
            "paper_stock": "Satin 300GSM",
            "print_sides": "Double",
            "print_type": "Colour",
            "fold_type": "Half fold to A5",
            "celloglaze": "2 Side Matt",
            "artworks": 1
        },
        "website_price": 630.32
    },
    {
        "name": "Test 3: A5 Budget Single B&W Uncoated",
        "params": {
            "quantity": 250,
            "finish_size": "A5 - 148mm x 210mm",
            "paper_stock": "Uncoated Bond 100GSM",
            "print_sides": "Single",
            "print_type": "Black & White",
            "fold_type": "Half fold to A6",
            "celloglaze": "None",
            "artworks": 1
        },
        "website_price": 146.42
    },
    {
        "name": "Test 4: A3 Crash Fold with Celloglaze Satin 350GSM",
        "params": {
            "quantity": 500,
            "finish_size": "A3 - 297mm x 420mm",
            "paper_stock": "Satin 350GSM",
            "print_sides": "Double",
            "print_type": "Colour",
            "fold_type": "Crash fold to A5(Half then half)",
            "celloglaze": "1 Side Gloss",
            "artworks": 1
        },
        "website_price": 626.01
    },
    {
        "name": "Test 5: A4 Tri-Roll Fold Satin 128GSM",
        "params": {
            "quantity": 1000,
            "finish_size": "A4 - 210mm x 297mm",
            "paper_stock": "Satin 128GSM",
            "print_sides": "Double",
            "print_type": "Colour",
            "fold_type": "Tri Roll fold to DL",
            "celloglaze": "None",
            "artworks": 1
        },
        "website_price": 310.24
    },
    {
        "name": "Test 6: 6pp A4 Tri-Roll Fold Satin 128GSM",
        "params": {
            "quantity": 250,
            "finish_size": "6pp A4 - 630mm x 297mm",
            "paper_stock": "Satin 128GSM",
            "print_sides": "Double",
            "print_type": "Colour",
            "fold_type": "Tri Roll fold to A4",
            "celloglaze": "None",
            "artworks": 1
        },
        "website_price": 317.48
    }
]

print("=" * 100)
print("FOLDED FLYERS: BACKEND CALCULATOR vs VALIDATED WEBSITE PRICES")
print("=" * 100)
print()

total_diff = 0
total_pct = 0

for i, test in enumerate(tests, 1):
    result = calculate_folded_flyers_shopify(**test["params"])
    
    if not result.get("success"):
        print(f"❌ Test {i}: {test['name']}")
        print(f"   ERROR: {result.get('error')}")
        print()
        continue
    
    backend_price = result["total_price"]
    website_price = test["website_price"]
    diff = backend_price - website_price
    pct = (diff / website_price) * 100
    
    total_diff += abs(diff)
    total_pct += abs(pct)
    
    status = "✅" if abs(diff) < 0.50 else "❌"
    
    print(f"{status} Test {i}: {test['name']}")
    print(f"   Website:  ${website_price:.2f}")
    print(f"   Backend:  ${backend_price:.2f}")
    print(f"   Diff:     ${diff:+.2f} ({pct:+.2f}%)")
    print()

print("=" * 100)
print(f"AVERAGE ABSOLUTE DIFFERENCE: ${total_diff/6:.2f}")
print(f"AVERAGE ABSOLUTE PERCENTAGE: {total_pct/6:.2f}%")
print("=" * 100)
print()
print("CONCLUSION:")
print("Backend calculator pricing formulas DO NOT match actual Shopify website prices.")
print("The calculator needs pricing table updates to match validated website behavior.")
