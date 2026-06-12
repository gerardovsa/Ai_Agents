#!/usr/bin/env python3
"""
Test DL Size Folded Flyers Calculator
======================================

Tests the newly added DL size (99mm x 210mm) support for folded flyers.

Test Case: User's original request
- Quantity: 1000
- Size: DL (99mm x 210mm)
- Stock: Satin 128GSM  
- Double-sided: Yes
- Print Type: Colour
- Folding: Single Fold

Author: GitHub Copilot
Date: January 22, 2026
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add backend to path
backend_path = Path(__file__).parent / "UI" / "modules_external" / "quote-calculator" / "backend" / "shopify_calculators"
sys.path.insert(0, str(backend_path))

from FoldedFlyers_Shopify_Calculator import (
    FoldedFlyersShopifyCalculator,
    FinishSize,
    PrintSides,
    PrintType,
    PaperStock,
    FoldType,
    Celloglaze
)

def test_dl_flyer():
    """Test DL size flyer calculation"""
    print("=" * 80)
    print("TESTING DL SIZE FOLDED FLYERS CALCULATOR")
    print("=" * 80)
    print()
    
    # User's original request
    print("📋 Test Case: User's Original Request")
    print("   Quantity: 1000")
    print("   Size: DL (99mm x 210mm)")
    print("   Stock: Satin 128GSM")
    print("   Sides: Double-sided")
    print("   Print: Colour")
    print("   Folding: Single Fold")
    print()
    
    try:
        # Initialize calculator
        calc = FoldedFlyersShopifyCalculator()
        
        # Calculate quote
        result = calc.calculate_quote(
            quantity=1000,
            print_sides=PrintSides.DOUBLE_SIDE,
            print_type=PrintType.COLOUR,
            finish_size=FinishSize.DL,
            paper_stock=PaperStock.SATIN_128GSM,
            artworks=1,
            fold_type=FoldType.SINGLE_FOLD,
            celloglaze=Celloglaze.NONE
        )
        
        print("✅ CALCULATION SUCCESSFUL!")
        print()
        print(f"💰 Total Price: ${result.final_price:.2f}")
        unit_price = result.final_price / result.quantity
        print(f"📊 Unit Price: ${unit_price:.4f}")
        print(f"📦 Quantity: {result.quantity}")
        print()
        print("📈 Cost Breakdown:")
        print(f"   Setup Total: ${result.setup_total:.2f}")
        print(f"   Stock Cost: ${result.stock_cost:.2f}")
        print(f"   Click Cost: ${result.click_cost:.2f}")
        print(f"   Cutting Cost: ${result.cutting_cost:.2f}")
        print(f"   Folding Cost: ${result.folding_cost:.2f}")
        print(f"   Cello Cost: ${result.cello_cost:.2f}")
        print(f"   Business Cost: ${result.biz_cost:.2f}")
        print(f"   Profit ({result.profit_margin_rate * 100:.0f}%): ${result.profit:.2f}")
        print(f"   Subtotal: ${result.subtotal:.2f}")
        print(f"   GST (10%): ${result.gst:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ CALCULATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dl_vs_a5_comparison():
    """Compare DL vs A5 pricing (DL should be cheaper due to more items per sheet)"""
    print()
    print("=" * 80)
    print("DL vs A5 PRICING COMPARISON")
    print("=" * 80)
    print()
    
    calc = FoldedFlyersShopifyCalculator()
    
    # Test DL
    dl_result = calc.calculate_quote(
        quantity=1000,
        print_sides=PrintSides.DOUBLE_SIDE,
        print_type=PrintType.COLOUR,
        finish_size=FinishSize.DL,
        paper_stock=PaperStock.SATIN_128GSM,
        artworks=1,
        fold_type=FoldType.SINGLE_FOLD,
        celloglaze=Celloglaze.NONE
    )
    
    # Test A5
    a5_result = calc.calculate_quote(
        quantity=1000,
        print_sides=PrintSides.DOUBLE_SIDE,
        print_type=PrintType.COLOUR,
        finish_size=FinishSize.A5,
        paper_stock=PaperStock.SATIN_128GSM,
        artworks=1,
        fold_type=FoldType.SINGLE_FOLD,
        celloglaze=Celloglaze.NONE
    )
    
    dl_unit = dl_result.final_price / dl_result.quantity
    a5_unit = a5_result.final_price / a5_result.quantity
    
    print(f"DL (99x210mm):  ${dl_result.final_price:.2f} (${dl_unit:.4f} each)")
    print(f"A5 (148x210mm): ${a5_result.final_price:.2f} (${a5_unit:.4f} each)")
    print()
    print(f"💡 DL should be cheaper (6 items/sheet vs A5's 4 items/sheet)")
    
    if dl_result.final_price < a5_result.final_price:
        print(f"✅ CORRECT: DL is ${a5_result.final_price - dl_result.final_price:.2f} cheaper")
    else:
        print(f"⚠️  WARNING: DL is more expensive (unexpected)")

if __name__ == "__main__":
    success = test_dl_flyer()
    if success:
        test_dl_vs_a5_comparison()
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
