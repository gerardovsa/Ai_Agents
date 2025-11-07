#!/usr/bin/env python3
"""
GOD Perfect Bound Books Calculator - CLI Tool
==============================================

Command-line interface for the GOD Perfect Bound Books Calculator.

Usage Examples:
---------------

1. Basic quote:
   python pbb_cli.py --qty 100 --width 210 --height 297 --pages 100 --gsm 80 --cover-gsm 300

2. With all options:
   python pbb_cli.py --qty 565 --width 210 --height 297 --pages 100 --gsm 80 --cover-gsm 300 \
                     --cello gloss --internal-print bw --cover-print both --scored

3. JSON output:
   python pbb_cli.py --qty 100 --width 210 --height 297 --pages 100 --gsm 80 --cover-gsm 300 --json

4. Compare multiple quantities:
   python pbb_cli.py --qty 100 565 1110 --width 210 --height 297 --pages 100 --gsm 80 --cover-gsm 300

Author: GOD Calculator System
Date: October 2025
"""

import argparse
import sys
import json
from decimal import Decimal
from typing import List, Dict, Any

from GOD_perfect_bound_books_calculator import (
    PerfectBoundBooksCalculator,
    QuoteResult
)


def format_currency(value: Decimal) -> str:
    """Format decimal as currency"""
    return f"${value:,.2f}"


def format_percentage(value: Decimal) -> str:
    """Format decimal as percentage"""
    return f"{value * 100:.1f}%"


def print_quote_result(result: QuoteResult, quantity: int):
    """Print formatted quote result"""
    print(f"\n{'='*80}")
    print(f"PERFECT BOUND BOOKS QUOTE - Quantity: {quantity}")
    print(f"{'='*80}")
    
    # Pricing Summary
    print(f"\n💰 PRICING:")
    print(f"  Unit Price:          {format_currency(result.unit_price)}")
    print(f"  Total (ex GST):      {format_currency(result.total_price)}")
    print(f"  Total (inc GST):     {format_currency(result.total_inc_gst)}")
    print(f"  GST Amount:          {format_currency(result.total_inc_gst - result.total_price)}")
    
    # Cost Breakdown
    print(f"\n📋 COST BREAKDOWN:")
    print(f"  Cover:               {format_currency(result.cover_cost)}")
    print(f"  Internals:           {format_currency(result.internal_cost)}")
    print(f"  Celloglaze:          {format_currency(result.cello_cost)}")
    print(f"  Binding:             {format_currency(result.binding_cost)}")
    print(f"  Trimming:            {format_currency(result.trimming_cost)}")
    print(f"  Cutting:             {format_currency(result.cutting_cost)}")
    print(f"  Scoring:             {format_currency(result.scoring_cost)}")
    print(f"  Imposition Setup:    {format_currency(result.imposition_setup)}")
    print(f"  Proof Cost:          {format_currency(result.proof_cost)}")
    print(f"  Extra Books:         {format_currency(result.extra_books)}")
    
    # Specifications
    print(f"\n📝 SPECIFICATIONS:")
    for key, value in result.specifications.items():
        key_display = key.replace('_', ' ').title()
        print(f"  {key_display:<20} {value}")
    
    print(f"\n{'='*80}\n")


def print_comparison_table(results: List[tuple[int, QuoteResult]]):
    """Print comparison table for multiple quantities"""
    print(f"\n{'='*100}")
    print(f"PERFECT BOUND BOOKS QUOTE COMPARISON")
    print(f"{'='*100}")
    
    # Header
    print(f"\n{'Quantity':<12}", end="")
    for qty, _ in results:
        print(f"{qty:>15}", end="")
    print()
    print(f"{'-'*100}")
    
    # Unit Price
    print(f"{'Unit Price':<12}", end="")
    for _, result in results:
        print(f"{format_currency(result.unit_price):>15}", end="")
    print()
    
    # Total ex GST
    print(f"{'Total ex GST':<12}", end="")
    for _, result in results:
        print(f"{format_currency(result.total_price):>15}", end="")
    print()
    
    # Total inc GST
    print(f"{'Total inc GST':<12}", end="")
    for _, result in results:
        print(f"{format_currency(result.total_inc_gst):>15}", end="")
    print()
    
    print(f"{'-'*100}")
    
    # Cost breakdown
    print(f"\n{'BREAKDOWN':<12}")
    print(f"{'-'*100}")
    
    components = [
        ('Cover', 'cover_cost'),
        ('Internals', 'internal_cost'),
        ('Cello', 'cello_cost'),
        ('Binding', 'binding_cost'),
        ('Trimming', 'trimming_cost'),
        ('Cutting', 'cutting_cost'),
        ('Scoring', 'scoring_cost'),
        ('Setup', 'imposition_setup'),
        ('Proof', 'proof_cost'),
        ('Extra Books', 'extra_books')
    ]
    
    for label, attr in components:
        print(f"{label:<12}", end="")
        for _, result in results:
            value = getattr(result, attr)
            print(f"{format_currency(value):>15}", end="")
        print()
    
    print(f"\n{'='*100}\n")


def result_to_dict(result: QuoteResult, quantity: int) -> Dict[str, Any]:
    """Convert QuoteResult to dictionary for JSON output"""
    return {
        "quantity": quantity,
        "pricing": {
            "unit_price": float(result.unit_price),
            "total_ex_gst": float(result.total_price),
            "total_inc_gst": float(result.total_inc_gst),
            "gst_amount": float(result.total_inc_gst - result.total_price)
        },
        "breakdown": {
            "cover": float(result.cover_cost),
            "internals": float(result.internal_cost),
            "celloglaze": float(result.cello_cost),
            "binding": float(result.binding_cost),
            "trimming": float(result.trimming_cost),
            "cutting": float(result.cutting_cost),
            "scoring": float(result.scoring_cost),
            "imposition_setup": float(result.imposition_setup),
            "proof_cost": float(result.proof_cost),
            "extra_books": float(result.extra_books)
        },
        "specifications": result.specifications
    }


def main():
    parser = argparse.ArgumentParser(
        description="GOD Perfect Bound Books Calculator - Database-driven quote calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic A4 book quote
  python pbb_cli.py --qty 100 --width 210 --height 297 --pages 100 --gsm 80 --cover-gsm 300
  
  # With celloglaze and scoring
  python pbb_cli.py --qty 565 --width 210 --height 297 --pages 100 --gsm 80 --cover-gsm 300 \\
                    --cello gloss --scored
  
  # Compare multiple quantities
  python pbb_cli.py --qty 100 565 1110 --width 210 --height 297 --pages 100 --gsm 80 --cover-gsm 300
  
  # JSON output
  python pbb_cli.py --qty 100 --width 210 --height 297 --pages 100 --gsm 80 --cover-gsm 300 --json
        """
    )
    
    # Required arguments
    parser.add_argument('--qty', type=int, nargs='+', required=True,
                        help='Quantity (can specify multiple for comparison)')
    parser.add_argument('--width', type=int, required=True,
                        help='Book width in mm')
    parser.add_argument('--height', type=int, required=True,
                        help='Book height in mm')
    parser.add_argument('--pages', type=int, required=True,
                        help='Number of internal pages')
    parser.add_argument('--gsm', type=int, required=True,
                        help='Internal paper GSM')
    parser.add_argument('--cover-gsm', type=int, required=True,
                        help='Cover paper GSM')
    
    # Optional arguments
    parser.add_argument('--cello', choices=['none', 'gloss', 'matt'], default='none',
                        help='Celloglaze type (default: none)')
    parser.add_argument('--internal-print', choices=['bw', 'color', 'mixed'], default='bw',
                        help='Internal print mode (default: bw)')
    parser.add_argument('--cover-print', choices=['front', 'both'], default='both',
                        help='Cover print mode (default: both)')
    parser.add_argument('--scored', action='store_true',
                        help='Add scoring')
    parser.add_argument('--stock-type', type=int, default=29,
                        help='Stock type ID for internals (default: 29 - Bond/Uncoated)')
    parser.add_argument('--cover-stock-type', type=int, default=20,
                        help='Cover stock type ID (default: 20 - Silk/Satin)')
    
    # Output format
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    parser.add_argument('--compare', action='store_true',
                        help='Show comparison table (default if multiple quantities)')
    
    args = parser.parse_args()
    
    # Map cello choices
    cello_map = {'none': 0, 'gloss': 1, 'matt': 2}
    cello_type = cello_map[args.cello]
    
    # Map print mode choices
    print_mode_map = {'bw': 1, 'color': 0, 'mixed': 2}
    internal_print_mode = print_mode_map[args.internal_print]
    cover_print_mode = 1  # Always both sides for cover
    
    # Calculate quotes
    try:
        with PerfectBoundBooksCalculator() as calc:
            results = []
            
            for qty in args.qty:
                result = calc.calculate(
                    quantity=qty,
                    book_width=args.width,
                    book_height=args.height,
                    pages=args.pages,
                    stock_type_id=args.stock_type,
                    internal_stock_gsm=args.gsm,
                    cover_stock_type_id=args.cover_stock_type,
                    cover_stock_gsm=args.cover_gsm,
                    cello_type=cello_type,
                    internal_print_mode=internal_print_mode,
                    cover_print_mode=cover_print_mode,
                    is_scored=args.scored
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
            
            return 0
            
    except Exception as e:
        print(f"\n ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
