#!/usr/bin/env python3
"""Test Spiral Bound Books wrapper parameter fix"""

import sys
from pathlib import Path

# Add paths
wrapper_dir = Path(__file__).parent / "UI" / "modules_external" / "quote-calculator" / "implementations"
sys.path.insert(0, str(wrapper_dir))

from calculator_wrapper import calculate_spiral_bound_books_shopify

print("Testing Spiral Bound Books wrapper with NEW parameter names...")
print("=" * 70)
print("Test: User Config - 50 qty A6 Portrait with Clear PVC front + Satin Blank back")
print("=" * 70)

result = calculate_spiral_bound_books_shopify(
    quantity=50,
    artworks=1,
    internal_pages=50,
    finish_size='A6 Portrait',
    outer_front_cover='Clear PVC',
    printed_front_cover='300GSM Satin',
    front_cover_print='1pp Colour',
    front_celloglaze='None',
    outer_back_cover='350GSM Satin Blank',  # Note: "350GSM Satin Blank Card" might map to this
    printed_back_cover='None',  # NO printed back
    # back_cover_print NOT included when printed_back_cover='None'
    back_celloglaze='None',
    internal_stock='Uncoated Bond 100GSM',
    internal_print='Black & White'
)

if result['success']:
    print(f"✅ SUCCESS: ${result['total_price']:.2f}")
    print(f"   Unit Price: ${result['unit_price']:.2f}")
    print(f"   Quantity: {result['quantity']}")
else:
    print(f"❌ ERROR: {result['error']}")

print("\n" + "=" * 70)
print("Expected website price: $401.71")
print("=" * 70)
