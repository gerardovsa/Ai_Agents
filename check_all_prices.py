import json

with open('UI/modules_external/quote-calculator/config/shopify/Shopify_Spiral_Bound_Books.json') as f:
    d = json.load(f)

opts = d['shopify_spiral_bound_books']['options']

print("ALL FIELD PRICES:")
print("="*80)

for field in opts:
    if 'options' in field:
        print(f"\n{field['name']} ({field['field_id']}):")
        for option in field['options']:
            price = option.get('price', 0)
            price_type = option.get('price_type', 'unknown')
            print(f"  {option['title']:30s} ${price:8.4f} ({price_type})")
