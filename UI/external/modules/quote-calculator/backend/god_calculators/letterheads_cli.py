#!/usr/bin/env python3
"""
Letterheads Calculator CLI Tool
================================

Command-line interface for GOD_letterhead_calculator.py

Usage:
    python letterheads_cli.py --qty 500 --width 210 --height 297 --gsm 100 --sides front
    python letterheads_cli.py --qty 500 1000 2500 --width 210 --height 297 --gsm 100 --sides both --compare
    python letterheads_cli.py --qty 1000 --width 210 --height 297 --gsm 100 --sides front --json

Author: Extracted from GOD Calculator Suite
Date: October 12, 2025
"""

import argparse
import sys
import json
import os
from decimal import Decimal
from typing import List, Dict, Any

from GOD_letterhead_calculator import LetterheadCalculatorGOD, QuoteResult

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))
from db_connector import InHousePrintDB


# ============================================================================
# OUTPUT FORMATTING
# ============================================================================

def format_currency(value: float) -> str:
    """Format value as currency"""
    return f"${value:,.2f}"


def format_percentage(value: Decimal) -> str:
    """Format decimal as percentage"""
    return f"{value * 100:.1f}%"


def print_quote_result(result: QuoteResult, quantity: int):
    """Print formatted quote result"""
    print(f"\n{'='*80}")
    print(f"LETTERHEADS QUOTE - Quantity: {quantity}")
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
    print(f"    - Side 1:          {format_currency(breakdown['side1_cost'])}")
    print(f"    - Side 2:          {format_currency(breakdown['side2_cost'])}")
    print(f"  Setup Cost:          {format_currency(breakdown['setup_cost'])}")
    print(f"  Cutting Cost:        {format_currency(breakdown['cutting_cost'])}")
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
    print(f"  A4 Multiplier:       {specs['a4_multiplier']:.2f}")
    
    print(f"\n{'='*80}\n")


def print_comparison_table(results: List[tuple]):
    """Print comparison table for multiple quantities"""
    print(f"\n{'='*97}")
    print(f"LETTERHEADS QUOTE COMPARISON")
    print(f"{'='*97}\n")
    
    # Header
    quantities = [qty for qty, _ in results]
    header = f"{'Quantity':<35}"
    for qty in quantities:
        header += f"{qty:>15,}"
    print(header)
    print('-' * 97)
    
    # Prices
    print(f"{'Unit Price (ex GST)':<35}", end='')
    for _, result in results:
        print(f"{result.cost_per_unit_ex_gst:>14.2f} ", end='')
    print()
    
    print(f"{'Unit Price (inc GST)':<35}", end='')
    for _, result in results:
        print(f"{result.cost_per_unit_inc_gst:>14.2f} ", end='')
    print()
    
    print('-' * 97)
    
    print(f"{'Total ex GST':<35}", end='')
    for _, result in results:
        print(f"{result.total_cost_ex_gst:>14.2f} ", end='')
    print()
    
    print(f"{'Total inc GST':<35}", end='')
    for _, result in results:
        print(f"{result.total_cost_inc_gst:>14.2f} ", end='')
    print()
    
    print('-' * 97)
    print("\nBREAKDOWN")
    print('-' * 97)
    
    # Breakdown
    print(f"{'Click Cost':<35}", end='')
    for _, result in results:
        print(f"{result.breakdown['click_cost']:>14.2f} ", end='')
    print()
    
    print(f"{'Business Cost':<35}", end='')
    for _, result in results:
        print(f"{result.cost_to_business:>14.2f} ", end='')
    print()
    
    print(f"\n{'='*97}\n")


def result_to_dict(result: QuoteResult, quantity: int) -> Dict[str, Any]:
    """Convert QuoteResult to dictionary for JSON output"""
    return {
        'quantity': quantity,
        'total_ex_gst': float(result.total_cost_ex_gst),
        'total_inc_gst': float(result.total_cost_inc_gst),
        'cost_per_unit_ex_gst': float(result.cost_per_unit_ex_gst),
        'cost_per_unit_inc_gst': float(result.cost_per_unit_inc_gst),
        'breakdown': result.breakdown,
        'specifications': result.specifications
    }


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='GOD Letterheads Calculator - Database-driven pricing calculator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single A4 letterhead quote (one-sided)
  python letterheads_cli.py --qty 500 --width 210 --height 297 --gsm 100 --sides front

  # Comparison across multiple quantities
  python letterheads_cli.py --qty 250 500 1000 2500 --width 210 --height 297 --gsm 100 --sides front --compare

  # Double-sided letterheads
  python letterheads_cli.py --qty 1000 --width 210 --height 297 --gsm 100 --sides both

  # JSON output for API integration
  python letterheads_cli.py --qty 500 --width 210 --height 297 --gsm 100 --sides front --json
        """
    )
    
    # Required arguments
    parser.add_argument('--qty', type=int, nargs='+', required=True,
                        help='Quantity (can specify multiple for comparison)')
    parser.add_argument('--width', type=float, required=True,
                        help='Width in mm')
    parser.add_argument('--height', type=float, required=True,
                        help='Height in mm')
    parser.add_argument('--gsm', type=int, required=True,
                        help='Paper GSM')
    parser.add_argument('--sides', choices=['front', 'back', 'both', 'none'], required=True,
                        help='Print sides')
    
    # Optional arguments
    parser.add_argument('--discount', type=float, default=0.0,
                        help='Discount percentage (e.g., 10 for 10%%)')
    
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
    
    # Convert discount to decimal
    discount = Decimal(str(args.discount / 100.0)) if args.discount > 0 else Decimal('0')
    
    # Calculate quotes
    # Initialize database connection
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'database-config.json')
    db = InHousePrintDB(config_path)
    
    try:
        calc = LetterheadCalculatorGOD(db)
        
        results = []
        
        for qty in args.qty:
            result = calc.calculate(
                quantity=qty,
                width=args.width,
                height=args.height,
                gsm=args.gsm,
                print_side1=print_side1,
                print_side2=print_side2,
                discount=discount
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
