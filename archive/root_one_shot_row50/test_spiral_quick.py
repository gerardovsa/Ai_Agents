import sys
import json
from pathlib import Path
from decimal import Decimal

# Load JSON directly
json_path = Path('UI/modules_external/quote-calculator/ARCHIVE_CONSOLIDATED/CALCULATOR_JSONS/shopify/Shopify_Spiral_Bound_Books.json')
with open(json_path) as f:
    config = json.load(f)

# Get F12 prices
f12 = None
for option in config['shopify_spiral_bound_books']['options']:
    if option['field_id'] == 'F12':
        f12 = option
        break

print("F12 Content Paper Stock Prices:")
print("="*80)
for opt in f12['options']:
    price = opt['price']
    price_type = opt['price_type']
    print(f"{opt['title']:30s} {price:10.4f}  {price_type}")
    
# Manual calculation for Test 1
print("\n\nTEST 1 MANUAL CALCULATION:")
print("="*80)
quantity = 100
content_pages = 40
finish_size_sheets_per_sra3 = 4  # A5 Portrait
stock_waste = 1.05
bond_80_price = 0.075
content_print_price = 0.02

# Calculate total content sheets (SRA3)
total_content_sheets = ((quantity * content_pages) / 2) / finish_size_sheets_per_sra3 * stock_waste
print(f"Total Content Sheets (SRA3): {total_content_sheets:.2f}")

# Calculate costs
content_stock_cost = total_content_sheets * bond_80_price
content_click_cost = total_content_sheets * content_print_price
total_content_cost = content_stock_cost + content_click_cost

print(f"Content Stock Cost: ${content_stock_cost:.2f}")
print(f"Content Click Cost: ${content_click_cost:.2f}")
print(f"Total Content Cost: ${total_content_cost:.2f}")

