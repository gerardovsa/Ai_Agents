import sys
sys.path.insert(0, 'UI/modules_external/quote-calculator/backend')
sys.path.insert(0, 'UI/modules_external/quote-calculator/ARCHIVE_CONSOLIDATED/CALCULATOR_JSONS/shopify')

import json
from pathlib import Path
from decimal import Decimal

# Load the JSON to see what the calculator is reading
json_path = Path('UI/modules_external/quote-calculator/ARCHIVE_CONSOLIDATED/CALCULATOR_JSONS/shopify/Shopify_Spiral_Bound_Books.json')
with open(json_path) as f:
    config = json.load(f)

# Find the prices for Test 1 configuration
print("PRICES FROM JSON:")
print("="*80)

# F4 - Printed Front Cover (300GSM Satin)
for opt in config['shopify_spiral_bound_books']['options']:
    if opt['field_id'] == 'F4':
        for option in opt['options']:
            if '300GSM' in option['title']:
                print(f"F4 (300GSM Satin): {option['price']} ({option['price_type']})")
                f4_price = option['price']
                
# F5 - Cover Print Type (1pp Colour)
for opt in config['shopify_spiral_bound_books']['options']:
    if opt['field_id'] == 'F5':
        for option in opt['options']:
            if '1pp Colour' in option['title']:
                print(f"F5 (1pp Colour): {option['price']} ({option['price_type']})")
                f5_price = option['price']
                
# F12 - Content Paper Stock (Bond 80GSM)
for opt in config['shopify_spiral_bound_books']['options']:
    if opt['field_id'] == 'F12':
        for option in opt['options']:
            if 'Bond 80GSM' in option['title']:
                print(f"F12 (Bond 80GSM): {option['price']} ({option['price_type']})")
                f12_price = option['price']
                
# F13 - Content Print Type (Black & White)
for opt in config['shopify_spiral_bound_books']['options']:
    if opt['field_id'] == 'F13':
        for option in opt['options']:
            if 'Black & White' in option['title']:
                print(f"F13 (Black & White): {option['price']} ({option['price_type']})")
                f13_price = option['price']

print("\nEXPECTED CALCULATION:")
print("="*80)
quantity = 100
content_pages = 40
finish_size_out = 4  # A5 Portrait
stock_waste = Decimal('1.05')

# Front cover sheets (SRA3)
total_front_cover_sheets = (Decimal(quantity) / Decimal(finish_size_out)) * stock_waste
print(f"Front Cover Sheets (SRA3): {total_front_cover_sheets}")
front_cover_stock_cost = total_front_cover_sheets * Decimal(str(f4_price))
front_cover_click_cost = total_front_cover_sheets * Decimal(str(f5_price))
total_front_cover_cost = front_cover_stock_cost + front_cover_click_cost
print(f"Front Cover Stock: ${front_cover_stock_cost}")
print(f"Front Cover Click: ${front_cover_click_cost}")
print(f"Total Front Cover: ${total_front_cover_cost}")

# Content sheets (SRA3)
total_content_sheets = ((Decimal(quantity) * Decimal(content_pages)) / Decimal('2')) / Decimal(finish_size_out) * stock_waste
print(f"\nContent Sheets (SRA3): {total_content_sheets}")
content_stock_cost = total_content_sheets * Decimal(str(f12_price))
content_click_cost = total_content_sheets * Decimal(str(f13_price))
total_content_cost = content_stock_cost + content_click_cost
print(f"Content Stock: ${content_stock_cost}")
print(f"Content Click: ${content_click_cost}")
print(f"Total Content: ${total_content_cost}")

print(f"\nPrint Cost (Front + Content): ${total_front_cover_cost + total_content_cost}")
