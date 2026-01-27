import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'))

from BollardSigns_Shopify_Calculator import BollardSignsShopifyCalculator

calc = BollardSignsShopifyCalculator()

print("Test 4: 3 artworks")
r = calc.calculate(quantity=10, material='5mm Corflute', size='270mm W x 1000mm H - Three Sided', artworks=3)
print(f'Material: ${r.breakdown["material_cost"]:.2f}')
print(f'Artwork: ${r.breakdown["artwork_setup_cost"]:.2f}')
print(f'Biz cost: ${r.breakdown["biz_cost"]:.2f}')
print(f'After 1.3x: ${r.breakdown["subtotal_with_multiplier"]:.2f}')
print(f'After GST 1: ${r.breakdown["after_first_gst"]:.2f}')
print(f'Total: ${r.total_price}')
print(f'Expected: $774.14')
print(f'Diff: ${r.total_price - 774.14:.2f}')

# Manual calculation
material = 468.75
artwork = 15
biz = material + artwork
after_mult = biz * 1.3
after_gst1 = after_mult * 1.1
after_gst2 = after_gst1 * 1.1
print(f'\nManual calculation:')
print(f'Material: ${material:.2f}')
print(f'Artwork: ${artwork:.2f}')
print(f'Biz: ${biz:.2f}')
print(f'×1.3: ${after_mult:.2f}')
print(f'×1.1: ${after_gst1:.2f}')
print(f'×1.1: ${after_gst2:.2f}')
