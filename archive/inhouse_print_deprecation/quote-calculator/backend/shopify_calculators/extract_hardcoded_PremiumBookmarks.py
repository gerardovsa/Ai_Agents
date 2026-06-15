#!/usr/bin/env python3
"""
Extract hardcoded values from Premium Bookmarks calculator and compare to JSON

Date: January 25, 2026
Purpose: Document what needs updating in JSON
"""

import sys
from pathlib import Path
import json

# Add paths
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from PremiumBookmarks_Shopify_Calculator import PremiumBookmarksShopifyCalculator

def extract_hardcoded_values():
    """Extract all hardcoded values from Python backend"""
    
    calc = PremiumBookmarksShopifyCalculator()
    
    print("=" * 80)
    print("HARDCODED VALUES IN PYTHON BACKEND")
    print("=" * 80)
    print()
    
    # Stock prices
    print("PAPER STOCK (per 1000 sheets):")
    stocks = ['satin_350gsm', 'uncoated_300gsm']
    for stock in stocks:
        price = calc._get_stock_price(stock)
        print(f"  {stock}: ${price}")
    print()
    
    # Print prices
    print("PRINT TYPE (per sheet):")
    prints = ['colour_1_sided', 'colour_2_sided']
    for print_type in prints:
        price = calc._get_print_price(print_type)
        print(f"  {print_type}: ${price}")
    print()
    
    # Celloglaze prices
    print("CELLOGLAZE (per sheet):")
    cellos = ['none', '1_side_gloss', '1_side_matt', '2_side_gloss', '2_side_matt']
    for cello in cellos:
        price = calc._get_celloglaze_price(cello)
        print(f"  {cello}: ${price}")
    print()
    
    # Finish size (bookmarks per 1000 sheets)
    print("FINISH SIZE (bookmarks per 1000 sheets):")
    sizes = ['50x150mm', '50x185mm', '50x230mm', '65x215mm']
    for size in sizes:
        qty = calc._get_bookmarks_per_sheet(size)
        print(f"  {size}: {qty} bookmarks per 1000 sheets")
    print()
    
    print("=" * 80)
    print()
    
    return {
        'paper_stock': {stock: float(calc._get_stock_price(stock)) for stock in stocks},
        'print_type': {pt: float(calc._get_print_price(pt)) for pt in prints},
        'celloglaze': {c: float(calc._get_celloglaze_price(c)) for c in cellos},
        'finish_size': {s: float(calc._get_bookmarks_per_sheet(s)) for s in sizes}
    }

def read_json_values():
    """Read current JSON values"""
    
    json_path = Path(__file__).parent.parent.parent / 'config' / 'shopify' / 'Shopify_Premium_Bookmarks.json'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("=" * 80)
    print("CURRENT JSON VALUES")
    print("=" * 80)
    print()
    
    options = config['shopify_premium_bookmarks']['options']
    
    # Find each field
    for opt in options:
        field_name = opt['name']
        field_id = opt['field_id']
        print(f"{field_name} ({field_id}):")
        
        if 'options' in opt:
            for item in opt['options']:
                title = item['title']
                price = item['price']
                price_type = item.get('price_type', 'fixed')
                print(f"  {title}: ${price} ({price_type})")
        print()
    
    print("=" * 80)
    print()

if __name__ == '__main__':
    hardcoded = extract_hardcoded_values()
    read_json_values()
    
    print("EXTRACTION COMPLETE - Review values above")
    print(f"\nHardcoded values dictionary:")
    print(json.dumps(hardcoded, indent=2))
