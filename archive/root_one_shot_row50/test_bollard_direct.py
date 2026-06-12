"""
Direct test of Bollard Signs Shopify formula (no imports from backend)
"""

import sys
from pathlib import Path
from decimal import Decimal

# Direct import path
sys.path.insert(0, str(Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'))
sys.path.insert(0, str(Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'))

# Now import
import BollardSigns_Shopify_Calculator

calc = BollardSigns_Shopify_Calculator.BollardSignsShopifyCalculator()

print("=" * 80)
print("SHOPIFY FORMULA VALIDATION - Direct Test")
print("=" * 80)
print()

# TEST: 10 signs (should match $267.83 Inc GST)
print("TEST: 10 signs, 5mm, 270×1000, 3-sided, 1 artwork")
print("-" * 40)
result = calc.calculate(
    quantity=10,
    material='5mm Corflute',
    size='270mm W x 1000mm H - Three Sided',
    artworks=1
)

print(f"SQM: {result.breakdown['total_sqm']:.2f} (NO sides multiplier!)")
print(f"Price/sqm: ${result.breakdown['price_per_sqm']:.2f}")
print(f"Material: ${result.breakdown['material_cost']:.2f}")
print(f"Artwork: ${result.breakdown['artwork_setup_cost']:.2f} (first FREE)")
print(f"After 1.3x: ${result.breakdown['subtotal_with_multiplier']:.2f}")
print()
print(f"OUR PRICE (ex GST): ${result.total_price:.2f}")
our_with_gst = result.total_price * Decimal('1.1')
print(f"OUR PRICE (inc GST): ${our_with_gst:.2f}")
print(f"SHOPIFY ACTUAL: $267.83")
print(f"DIFFERENCE: ${abs(our_with_gst - Decimal('267.83')):.2f}")
print()

# TEST: 100 signs (should match $1,762.80 Inc GST)
print("TEST: 100 signs, 5mm, 300×1000, 3-sided, 1 artwork")
print("-" * 40)
result = calc.calculate(
    quantity=100,
    material='5mm Corflute',
    size='300mm W x 1000mm H - Three Sided',
    artworks=1
)

print(f"SQM: {result.breakdown['total_sqm']:.2f} (NO sides multiplier!)")
print(f"Price/sqm: ${result.breakdown['price_per_sqm']:.2f}")
print(f"After 1.3x: ${result.breakdown['subtotal_with_multiplier']:.2f}")
print()
print(f"OUR PRICE (ex GST): ${result.total_price:.2f}")
our_with_gst = result.total_price * Decimal('1.1')
print(f"OUR PRICE (inc GST): ${our_with_gst:.2f}")
print(f"SHOPIFY ACTUAL: $1,762.80")
print(f"DIFFERENCE: ${abs(our_with_gst - Decimal('1762.80')):.2f}")
print()
print("=" * 80)
