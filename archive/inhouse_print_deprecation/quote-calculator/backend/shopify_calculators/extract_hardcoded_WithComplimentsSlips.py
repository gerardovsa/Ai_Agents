#!/usr/bin/env python3
"""
Extract hardcoded values from WithComplimentsSlips calculator

Date: January 25, 2026
Purpose: Document hardcoded values for JSON alignment verification
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from WithComplimentsSlips_Shopify_Calculator import WithComplimentsSlipsShopifyCalculator

def extract_hardcoded_values():
    """Extract all hardcoded values from Python backend"""
    
    calc = WithComplimentsSlipsShopifyCalculator()
    
    print("=" * 80)
    print("HARDCODED VALUES IN PYTHON BACKEND")
    print("=" * 80)
    print()
    
    # Paper stock prices
    print("PAPER STOCK (per 1000 sheets):")
    stocks = ['Uncoated Bond 80GSM', 'Uncoated Bond 90GSM', 'Uncoated Bond 100GSM']
    for stock in stocks:
        price = calc._get_stock_price(stock)
        print(f"  {stock}: ${price}")
    print()
    
    # Print type prices
    print("PRINT TYPE (per sheet):")
    prints = ['Colour', 'Black & White']
    for print_type in prints:
        price = calc._get_print_type_price(print_type)
        print(f"  {print_type}: ${price}")
    print()
    
    # Print sides multiplier
    print("PRINT SIDES (multiplier):")
    sides = ['Single side print', 'Double side print']
    for side in sides:
        mult = calc._get_print_sides_multiplier(side)
        print(f"  {side}: {mult}×")
    print()
    
    # Finish size
    print("FINISH SIZE (slips per sheet):")
    size = 'DL - 99mm x 210mm'
    qty = calc._get_slips_per_sheet(size)
    print(f"  {size}: {qty} slips per sheet")
    print()
    
    print("CONSTANTS:")
    print("  impos_setup: $15")
    print("  guilo_setup: $12")
    print("  extra_arts: $15 (first FREE)")
    print("  stock_waste: 1.05")
    print("  cutting_blk: 500 sheets")
    print("  cut_cost: $11")
    print()
    
    print("=" * 80)
    print()
    
    return {
        'paper_stock': {s: float(calc._get_stock_price(s)) for s in stocks},
        'print_type': {p: float(calc._get_print_type_price(p)) for p in prints},
        'print_sides': {s: float(calc._get_print_sides_multiplier(s)) for s in sides},
        'slips_per_sheet': float(calc._get_slips_per_sheet(size))
    }

if __name__ == '__main__':
    import json
    hardcoded = extract_hardcoded_values()
    print(f"\nHardcoded values dictionary:")
    print(json.dumps(hardcoded, indent=2))
