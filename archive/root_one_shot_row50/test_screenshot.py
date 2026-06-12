import sys
from pathlib import Path
backend_path = Path('UI/modules_external/quote-calculator/backend/shopify_calculators')
sys.path.insert(0, str(backend_path))
from NotepadsA4_Shopify_Calculator import NotepadsA4ShopifyCalculator

calc = NotepadsA4ShopifyCalculator()
result = calc.calculate(
    quantity=2000,
    artworks=2,
    finish_size='A4 Portrait',
    leaves_per_pad=100,
    print_type='Colour 1 sided',
    stock_type='Revive Recycled Uncoated'
)
print(f'Backend Total: ${result.total_price:,.2f}')
print(f'Website Total: $24,728.33')
diff = abs(float(result.total_price) - 24728.33)
print(f'Difference: ${diff:.2f}')
print(f'Match: {"YES" if diff < 0.01 else "NO"}')
