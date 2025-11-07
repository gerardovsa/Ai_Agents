#!/usr/bin/env python3
"""
GOD Flyers Calculator - CLI Tool
=================================

Command-line interface for the GOD Flyers Calculator.

Usage Examples:
---------------

1. Basic A4 flyer quote:
   python flyers_cli.py --qty 1000 --width 210 --height 297 --gsm 150 --sides both

2. With folding and cellophane:
   python flyers_cli.py --qty 5000 --width 210 --height 297 --gsm 200 --sides both \
                        --folding 2 --cello gloss-both

3. A5 flyer single-sided:
   python flyers_cli.py --qty 2000 --width 148 --height 210 --gsm 130 --sides front

4. Compare multiple quantities:
   python flyers_cli.py --qty 1000 5000 10000 --width 210 --height 297 --gsm 150 --sides both

5. JSON output for API:
   python flyers_cli.py --qty 1000 --width 210 --height 297 --gsm 150 --sides both --json

Author: GOD Calculator System
Date: October 12, 2025
"""

import argparse
import sys
import json
import os
from decimal import Decimal
from typing import List, Dict, Any

from GOD_flyer_calculator import FlyerCalculatorGOD, QuoteResult

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))
from db_connector import InHousePrintDB


def format_currency(value: Decimal) -> str:
    """Format decimal as currency"""
    return f"${value:,.2f}"


def format_percentage(value: Decimal) -> str:
    """Format decimal as percentage"""
    return f"{value * 100:.1f}%"


def print_quote_result(result: QuoteResult, quantity: int):
    """Print formatted quote result"""
    print(f"\n{'='*80}")
    print(f"FLYERS QUOTE - Quantity: {quantity}")
    print(f"{'='*80}")
    
    # Pricing Summary
    print(f"\n💰 PRICING:")
    print(f"  Cost per Unit (ex GST): {format_currency(result.cost_per_unit_ex_gst)}")
    print(f"  Cost per Unit (inc GST): {format_currency(result.cost_per_unit_inc_gst)}")
    print(f"  Total (ex GST):          {format_currency(result.total_cost_ex_gst)}")
    print(f"  Total (inc GST):         {format_currency(result.total_cost_inc_gst)}")
    print(f"  GST Amount:              {format_currency(result.gst_amount)}")
    print(f"  Profit Margin:           {format_percentage(result.profit_margin)}")
    
    # Cost Breakdown
    print(f"\n📋 COST BREAKDOWN:")
    breakdown = result.breakdown
    print(f"  Paper Cost:          {format_currency(breakdown['paper_cost'])}")
    print(f"  Click Cost:          {format_currency(breakdown['click_cost'])}")
    print(f"  Setup Cost:          {format_currency(breakdown['setup_cost'])}")
    print(f"  Cutting Cost:        {format_currency(breakdown['cutting_cost'])}")
    
    if breakdown.get('cello_cost', 0) > 0:
        print(f"  Cellophane Cost:     {format_currency(breakdown['cello_cost'])}")
    
    if breakdown.get('folding_cost', 0) > 0:
        print(f"  Folding Cost:        {format_currency(breakdown['folding_cost'])}")
    
    print(f"  Business Cost:       {format_currency(result.cost_to_business)}")
    
    # Specifications
    print(f"\n📝 SPECIFICATIONS:")
    specs = result.specifications
    print(f"  Size:                {specs['size']}")
    print(f"  Stock:               {specs['stock']}")
    print(f"  Stock Size:          {specs['stock_size']}")
    print(f"  GSM:                 {specs['gsm']}")
    print(f"  Print Side 1:        {specs['print_side1']}")
    print(f"  Print Side 2:        {specs['print_side2']}")
    print(f"  UPS (per sheet):     {specs['ups_per_sheet']}")
    print(f"  Sheets Required:     {specs['sheets_needed']}")
    
    if specs.get('folding_passes'):
        print(f"  Folding:             {specs['folding_passes']} pass(es)")
    
    if specs.get('cello') == 'Yes':
        print(f"  Cello Side 1:        {specs.get('cello_side1', 'None')}")
        print(f"  Cello Side 2:        {specs.get('cello_side2', 'None')}")
    
    print(f"\n{'='*80}\n")


def print_comparison_table(results: List[tuple[int, QuoteResult]]):
    """Print comparison table for multiple quantities"""
    print(f"\n{'='*100}")
    print(f"FLYERS QUOTE COMPARISON")
    print(f"{'='*100}")
    
    # Header
    print(f"\n{'Quantity':<20}", end="")
    for qty, _ in results:
        print(f"{qty:>18}", end="")
    print()
    print(f"{'-'*100}")
    
    # Unit Price
    print(f"{'Unit Price (ex GST)':<20}", end="")
    for _, result in results:
        print(f"{format_currency(result.cost_per_unit_ex_gst):>18}", end="")
    print()
    
    print(f"{'Unit Price (inc GST)':<20}", end="")
    for _, result in results:
        print(f"{format_currency(result.cost_per_unit_inc_gst):>18}", end="")
    print()
    
    print(f"{'-'*100}")
    
    # Total ex GST
    print(f"{'Total ex GST':<20}", end="")
    for _, result in results:
        print(f"{format_currency(result.total_cost_ex_gst):>18}", end="")
    print()
    
    # Total inc GST
    print(f"{'Total inc GST':<20}", end="")
    for _, result in results:
        print(f"{format_currency(result.total_cost_inc_gst):>18}", end="")
    print()
    
    print(f"{'-'*100}")
    
    # Cost breakdown
    print(f"\n{'BREAKDOWN':<20}")
    print(f"{'-'*100}")
    
    components = [
        ('Stock Cost', 'stock_cost'),
        ('Click Cost', 'click_cost'),
        ('Imposition Setup', 'imposition_setup'),
        ('Guillotine Cost', 'guillotine_cost'),
        ('Cellophane', 'cello_cost'),
        ('Folding', 'folding_cost'),
        ('Business Cost', None)  # Special: use cost_to_business
    ]
    
    for label, key in components:
        # Skip if all results have 0 for this component
        if key and all(result.breakdown.get(key, 0) == 0 for _, result in results):
            continue
        
        print(f"{label:<20}", end="")
        for _, result in results:
            if key:
                value = result.breakdown.get(key, Decimal('0'))
            else:
                value = result.cost_to_business
            print(f"{format_currency(value):>18}", end="")
        print()
    
    print(f"\n{'='*100}\n")


def result_to_dict(result: QuoteResult, quantity: int) -> Dict[str, Any]:
    """Convert QuoteResult to dictionary for JSON output"""
    return {
        "quantity": quantity,
        "pricing": {
            "unit_price_ex_gst": float(result.cost_per_unit_ex_gst),
            "unit_price_inc_gst": float(result.cost_per_unit_inc_gst),
            "total_ex_gst": float(result.total_cost_ex_gst),
            "total_inc_gst": float(result.total_cost_inc_gst),
            "gst_amount": float(result.gst_amount),
            "profit_margin": float(result.profit_margin)
        },
        "breakdown": {
            "stock_cost": float(result.breakdown['stock_cost']),
            "click_cost": float(result.breakdown['click_cost']),
            "imposition_setup": float(result.breakdown['imposition_setup']),
            "guillotine_cost": float(result.breakdown['guillotine_cost']),
            "cello_cost": float(result.breakdown.get('cello_cost', 0)),
            "folding_cost": float(result.breakdown.get('folding_cost', 0)),
            "business_cost": float(result.cost_to_business)
        },
        "specifications": result.specifications
    }


def main():
    parser = argparse.ArgumentParser(
        description="GOD Flyers Calculator - Database-driven quote calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic A4 flyer
  python flyers_cli.py --qty 1000 --width 210 --height 297 --gsm 150 --sides both
  
  # With folding and cellophane
  python flyers_cli.py --qty 5000 --width 210 --height 297 --gsm 200 --sides both \\
                       --folding 2 --cello gloss-both
  
  # Compare multiple quantities
  python flyers_cli.py --qty 1000 5000 10000 --width 210 --height 297 --gsm 150 --sides both
  
  # JSON output
  python flyers_cli.py --qty 1000 --width 210 --height 297 --gsm 150 --sides both --json
        """
    )
    
    # Required arguments
    parser.add_argument('--qty', type=int, nargs='+', required=True,
                        help='Quantity (can specify multiple for comparison)')
    parser.add_argument('--width', type=int, required=True,
                        help='Finish width in mm')
    parser.add_argument('--height', type=int, required=True,
                        help='Finish height in mm')
    parser.add_argument('--gsm', type=int, required=True,
                        help='Paper GSM')
    parser.add_argument('--sides', choices=['front', 'back', 'both', 'none'], required=True,
                        help='Print sides')
    
    # Optional arguments
    parser.add_argument('--folding', type=int, choices=[0, 1, 2, 3], default=0,
                        help='Number of folding passes (0=none, 1-3=passes)')
    parser.add_argument('--cello', 
                        choices=['none', 'gloss-front', 'gloss-back', 'gloss-both', 
                                'matt-front', 'matt-back', 'matt-both'],
                        default='none',
                        help='Cellophane lamination')
    
    # Output format
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    parser.add_argument('--compare', action='store_true',
                        help='Show comparison table (default if multiple quantities)')
    
    args = parser.parse_args()
    
    # Map print sides to print_side1 and print_side2
    print_modes = {
        'front': (1, 0),   # Color front only
        'back': (0, 1),    # Color back only
        'both': (1, 1),    # Both sides color
        'none': (0, 0)     # No print (unusual)
    }
    print_side1, print_side2 = print_modes[args.sides]
    
    # Map cello choices
    cello_side1, cello_side2 = 0, 0
    cello_required = args.cello != 'none'
    
    if 'gloss' in args.cello:
        cello_type = 1  # Gloss
    elif 'matt' in args.cello:
        cello_type = 2  # Matt
    else:
        cello_type = 0
    
    if 'front' in args.cello or 'both' in args.cello:
        cello_side1 = cello_type
    if 'back' in args.cello or 'both' in args.cello:
        cello_side2 = cello_type
    
    # Calculate quotes
    # Initialize database connection
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'database-config.json')
    db = InHousePrintDB(config_path)
    
    try:
        calc = FlyerCalculatorGOD(db)
        
        results = []
        
        for qty in args.qty:
            result = calc.calculate(
                quantity=qty,
                width=args.width,
                height=args.height,
                gsm=args.gsm,
                print_side1=print_side1,
                print_side2=print_side2,
                folding_passes=args.folding,
                cello_required=cello_required,
                cello_side1=cello_side1,
                cello_side2=cello_side2
            )
            results.append((qty, result))
        
        # Output results
        if args.json:
            output = [result_to_dict(r, q) for q, r in results]
            print(json.dumps(output, indent=2))
        elif len(results) > 1 or args.compare:
            print_comparison_table(results)
        else:
            qty, result = results[0]
            print_quote_result(result, qty)
        
        db.close()  # Clean up database connection
        return 0
        
    except Exception as e:
        db.close()  # Ensure cleanup on error
        print(f"\n ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
