import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'))

from BollardSigns_Shopify_Calculator import BollardSignsShopifyCalculator

calc = BollardSignsShopifyCalculator()
result = calc.calculate(quantity=1, material='5mm Corflute', size='270mm W x 1000mm H - Three Sided', artworks=1)

print(f'Total: ${result.total_price}')
print(f'Unit: ${result.unit_price}')
print(f'\nBreakdown:')
for key, value in result.breakdown.items():
    print(f'  {key}: {value}')
