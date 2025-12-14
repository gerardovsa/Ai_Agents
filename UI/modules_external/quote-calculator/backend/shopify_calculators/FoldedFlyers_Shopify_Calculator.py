#!/usr/bin/env python3
"""
Shopify Folded Flyers Calculator - Website Pricing Match
=========================================================

Extracted from: folded_printed_flyers_Shopify.json
Source: inhouseprint.com.au Shopify WooCommerce DPO plugin
Status: Shopify Hardcoded Pricing (NOT database-driven)

Key Features:
- F1-F8 field structure (Quantity, Print Sides, Print Type, Finish Size, Paper Stock, Artworks, Fold Type, Celloglaze)
- Size-based profit margins (A5, A4, A3, 6pp A4)
- Quantity threshold at 4000 (triggers different margin tiers)
- Folding costs with setup ($22) and per-thousand rates
- Celloglaze only visible for Satin stocks
- 10% GST (standard rate)

Price Components:
1. Setup Costs: $15 imposition + $12 guillotine + $22 folder + $16 cello (if applicable) + artworks
2. Stock Cost: Per 1000 sheets (39.6 to 138.6)
3. Click Cost: Sheets * Sides * Print Type (0.042 colour, 0.01 b&w)
4. Cutting Cost: (Sheets / 500) * $11
5. Folding Cost: (Qty * Fold Multiplier / 1000) * $23
6. Cello Cost: Sheets * Cello Rate (0.19 or 0.38 per sheet)
7. Profit Margin: BizCost-based tiers (21% to 160%)
8. GST: 10% on final total

Author: Extracted from Shopify JSON specification
Date: October 14, 2025
Status: Production-ready Shopify Calculator
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import sys

# Import config manager
from config_manager import config_manager


# ============================================================================
# ENUMS
# ============================================================================

class PrintSides(Enum):
    """Print sides options"""
    SINGLE_SIDE = ("Single side print", 1)
    DOUBLE_SIDE = ("Double side print", 2)
    
    def __init__(self, title, multiplier):
        self.title = title
        self.multiplier = multiplier


class PrintType(Enum):
    """Print type options"""
    COLOUR = ("Colour", Decimal('0.042'))
    BLACK_WHITE = ("Black & White", Decimal('0.01'))
    
    def __init__(self, title, cost_per_sheet):
        self.title = title
        self.cost_per_sheet = cost_per_sheet


class FinishSize(Enum):
    """Finish size options with items per sheet"""
    A5 = ("A5 - 148mm x 210mm", 148, 210, Decimal('4'), "a5_size")
    A4 = ("A4 - 210mm x 297mm", 210, 297, Decimal('2'), "a4_size")
    A3 = ("A3 - 297mm x 420mm", 297, 420, Decimal('1'), "a3_size")
    A4_6PP = ("6pp A4 - 630mm x 297mm", 630, 297, Decimal('0.5'), "6pp_a4_size")
    
    def __init__(self, title, width, height, items_per_sheet, margin_category):
        self.title = title
        self.width = width
        self.height = height
        self.items_per_sheet = items_per_sheet
        self.margin_category = margin_category


class PaperStock(Enum):
    """Paper stock options with pricing per 1000 sheets"""
    SATIN_128GSM = ("Satin 128GSM", Decimal('39.6'), 128, "Satin")
    SATIN_150GSM = ("Satin 150GSM", Decimal('64.8'), 150, "Satin")
    SATIN_250GSM = ("Satin 250GSM", Decimal('115.5'), 250, "Satin")
    SATIN_300GSM = ("Satin 300GSM", Decimal('126'), 300, "Satin")
    SATIN_350GSM = ("Satin 350GSM", Decimal('138.6'), 350, "Satin")
    UNCOATED_80GSM = ("Uncoated Bond 80GSM", Decimal('31.6'), 80, "Uncoated")
    UNCOATED_90GSM = ("Uncoated Bond 90GSM", Decimal('35.41'), 90, "Uncoated")
    UNCOATED_100GSM = ("Uncoated Bond 100GSM", Decimal('35.2'), 100, "Uncoated")
    
    def __init__(self, title, cost_per_1000, gsm, stock_type):
        self.title = title
        self.cost_per_1000 = cost_per_1000
        self.gsm = gsm
        self.stock_type = stock_type


class FoldType(Enum):
    """Fold type options"""
    SINGLE_FOLD = ("Single Fold", 1)
    DOUBLE_FOLD = ("Double Fold", 2)
    TRIPLE_FOLD = ("Triple Fold", 3)
    
    def __init__(self, title, multiplier):
        self.title = title
        self.multiplier = multiplier


class Celloglaze(Enum):
    """Celloglaze lamination options (only visible for Satin stocks)"""
    NONE = ("None", Decimal('0'), Decimal('0'))
    ONE_SIDE_GLOSS = ("1 Side Gloss", Decimal('0.19'), Decimal('16'))
    TWO_SIDE_GLOSS = ("2 Side Gloss", Decimal('0.38'), Decimal('16'))
    ONE_SIDE_MATT = ("1 Side Matt", Decimal('0.19'), Decimal('16'))
    TWO_SIDE_MATT = ("2 Side Matt", Decimal('0.38'), Decimal('16'))
    
    def __init__(self, title, cost_per_sheet, setup_cost):
        self.title = title
        self.cost_per_sheet = cost_per_sheet
        self.setup_cost = setup_cost


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class FoldedFlyerResult:
    """Quote result for folded flyers"""
    # Product details
    quantity: int
    finish_size: str
    paper_stock: str
    fold_type: str
    
    # Cost breakdown
    setup_total: Decimal
    stock_cost: Decimal
    click_cost: Decimal
    cutting_cost: Decimal
    folding_cost: Decimal
    cello_cost: Decimal
    
    # Totals
    biz_cost: Decimal
    profit_margin_rate: Decimal
    profit: Decimal
    subtotal: Decimal
    gst: Decimal
    final_price: Decimal
    
    # Specifications
    specifications: Dict[str, Any]
    
    def __str__(self):
        return f"""
Folded Flyer Quote - {self.finish_size}
{'='*60}
Quantity: {self.quantity}
Paper Stock: {self.paper_stock}
Fold Type: {self.fold_type}

Cost Breakdown:
  Setup:         ${self.setup_total:>10.2f}
  Stock:         ${self.stock_cost:>10.2f}
  Printing:      ${self.click_cost:>10.2f}
  Cutting:       ${self.cutting_cost:>10.2f}
  Folding:       ${self.folding_cost:>10.2f}
  Celloglaze:    ${self.cello_cost:>10.2f}
  
  BizCost:       ${self.biz_cost:>10.2f}
  Profit ({self.profit_margin_rate * 100:.0f}%):  ${self.profit:>10.2f}
  
  Subtotal:      ${self.subtotal:>10.2f}
  GST (10%):     ${self.gst:>10.2f}
  
TOTAL INC GST:   ${self.final_price:>10.2f}

Per Unit: ${self.final_price / self.quantity:.4f}
{'='*60}
"""


# ============================================================================
# FOLDED FLYERS CALCULATOR (SHOPIFY VERSION)
# ============================================================================

class FoldedFlyersShopifyCalculator:
    """
    Shopify Folded Flyers Calculator - Exact website pricing match
    
    Features:
    - Size-based profit margins (A5, A4, A3, 6pp A4)
    - Quantity threshold at 4000 for margin tiers
    - Folding operations with setup and per-thousand costs
    - Celloglaze only for Satin stocks
    - Hardcoded pricing (matches Shopify exactly)
    
    Usage:
        calc = FoldedFlyersShopifyCalculator()
        result = calc.calculate_quote(
            quantity=1000,
            print_sides=PrintSides.DOUBLE_SIDE,
            print_type=PrintType.COLOUR,
            finish_size=FinishSize.A4,
            paper_stock=PaperStock.SATIN_300GSM,
            artworks=1,
            fold_type=FoldType.DOUBLE_FOLD,
            celloglaze=Celloglaze.TWO_SIDE_GLOSS
        )
        print(f"Total: ${result.final_price:.2f}")
    """
    
    # Setup costs (hardcoded from JSON)
    IMPOS_SETUP = Decimal('15')
    GUILO_SETUP = Decimal('12')
    FOLDER_SETUP = Decimal('22')
    EXTRA_ARTS = Decimal('15')
    
    # Production constants
    STOCK_WASTE = Decimal('1.05')
    CUTTING_BLOCK = Decimal('500')
    CUT_COST = Decimal('11')
    FOLD_PER_THOUSAND = Decimal('23')
    
    # GST rate
    GST_RATE = Decimal('1.1')
    
    def __init__(self):
        """Initialize calculator with profit margin tiers"""
        self._load_profit_margin_tiers()
    
    def _load_profit_margin_tiers(self):
        """Load all profit margin tiers from JSON specification"""
        
        # A5 Size - Under 4000 qty
        self.a5_under_4000 = [
            (Decimal('50.999'), Decimal('1.5')),    # $1-$50.99: 150% margin
            (Decimal('100.999'), Decimal('1.25')),  # $51-$100.99: 125%
            (Decimal('150.999'), Decimal('1.1')),   # $75-$150.99: 110%
            (Decimal('200.999'), Decimal('1.0')),   # $101-$200.99: 100%
            (Decimal('300.999'), Decimal('0.7')),   # $151-$300.99: 70%
            (Decimal('400.999'), Decimal('0.53')),  # $201-$400.99: 53%
            (Decimal('500.999'), Decimal('0.4')),   # $301-$500.99: 40%
            (Decimal('1000.999'), Decimal('0.3')),  # $401-$1000.99: 30%
            (Decimal('5000.999'), Decimal('0.21'))  # $501-$5000.99: 21%
        ]
        
        # A5 Size - Over 4000 qty
        self.a5_over_4000 = [
            (Decimal('50.999'), Decimal('1.6')),    # $1-$50.99: 160%
            (Decimal('100.999'), Decimal('1.3')),   # $51-$100.99: 130%
            (Decimal('150.999'), Decimal('0.9')),   # $101-$150.99: 90%
            (Decimal('200.999'), Decimal('0.85')),  # $151-$200.99: 85%
            (Decimal('300.999'), Decimal('0.6')),   # $201-$300.99: 60%
            (Decimal('400.999'), Decimal('0.45')),  # $301-$400.99: 45%
            (Decimal('500.999'), Decimal('0.4')),   # $401-$500.99: 40%
            (Decimal('1000.999'), Decimal('0.3')),  # $501-$1000.99: 30%
            (Decimal('5000.999'), Decimal('0.21'))  # $1001-$5000.99: 21%
        ]
        
        # A4 Size - Under 4000 qty
        self.a4_under_4000 = [
            (Decimal('50.999'), Decimal('1.6')),    # $1-$50.99: 160%
            (Decimal('100.999'), Decimal('1.3')),   # $51-$100.99: 130%
            (Decimal('150.999'), Decimal('0.9')),   # $75-$150.99: 90%
            (Decimal('200.999'), Decimal('0.85')),  # $101-$200.99: 85%
            (Decimal('300.999'), Decimal('0.6')),   # $151-$300.99: 60%
            (Decimal('400.999'), Decimal('0.45')),  # $201-$400.99: 45%
            (Decimal('500.999'), Decimal('0.4')),   # $301-$500.99: 40%
            (Decimal('1000.999'), Decimal('0.3')),  # $401-$1000.99: 30%
            (Decimal('5000.999'), Decimal('0.21'))  # $501-$5000.99: 21%
        ]
        
        # A4 Size - Over 4000 qty (same as under 4000)
        self.a4_over_4000 = self.a4_under_4000.copy()
        
        # A3 Size - Under 4000 qty
        self.a3_under_4000 = [
            (Decimal('100.999'), Decimal('1.3')),   # $1-$100.99: 130%
            (Decimal('200.999'), Decimal('1.1')),   # $101-$200.99: 110%
            (Decimal('400.999'), Decimal('0.8')),   # $201-$400.99: 80%
            (Decimal('1000.999'), Decimal('0.5')),  # $401-$1000.99: 50%
            (Decimal('5000.999'), Decimal('0.3'))   # $1001-$5000.99: 30%
        ]
        
        # A3 Size - Over 4000 qty (same as A4/A5)
        self.a3_over_4000 = self.a4_over_4000.copy()
        
        # 6pp A4 Size - Under 4000 qty
        self.a4_6pp_under_4000 = [
            (Decimal('150.999'), Decimal('1.2')),   # $1-$150.99: 120%
            (Decimal('300.999'), Decimal('0.9')),   # $151-$300.99: 90%
            (Decimal('600.999'), Decimal('0.6')),   # $301-$600.99: 60%
            (Decimal('1000.999'), Decimal('0.45')), # $601-$1000.99: 45%
            (Decimal('5000.999'), Decimal('0.33'))  # $1001-$5000.99: 33%
        ]
        
        # 6pp A4 Size - Over 4000 qty (same as other high qty)
        self.a4_6pp_over_4000 = self.a4_over_4000.copy()
    
    def _get_profit_margin(self, biz_cost: Decimal, finish_size: FinishSize, quantity: int) -> Decimal:
        """
        Get profit margin based on BizCost, finish size, and quantity threshold
        
        Logic:
        1. Determine size category (A5, A4, A3, 6pp A4)
        2. Check quantity threshold (< 4000 or >= 4000)
        3. Find tier based on BizCost value
        """
        
        # Determine which tier list to use
        if quantity >= 4000:
            # High quantity tiers
            if finish_size == FinishSize.A5:
                tiers = self.a5_over_4000
            elif finish_size == FinishSize.A4:
                tiers = self.a4_over_4000
            elif finish_size == FinishSize.A3:
                tiers = self.a3_over_4000
            else:  # 6pp A4
                tiers = self.a4_6pp_over_4000
        else:
            # Standard quantity tiers
            if finish_size == FinishSize.A5:
                tiers = self.a5_under_4000
            elif finish_size == FinishSize.A4:
                tiers = self.a4_under_4000
            elif finish_size == FinishSize.A3:
                tiers = self.a3_under_4000
            else:  # 6pp A4
                tiers = self.a4_6pp_under_4000
        
        # Find matching tier
        for max_cost, margin in tiers:
            if biz_cost <= max_cost:
                return margin
        
        # Default to lowest margin if beyond all tiers
        return tiers[-1][1]
    
    def calculate_quote(
        self,
        quantity: int,
        print_sides: PrintSides,
        print_type: PrintType,
        finish_size: FinishSize,
        paper_stock: PaperStock,
        artworks: int,
        fold_type: FoldType,
        celloglaze: Celloglaze = Celloglaze.NONE
    ) -> FoldedFlyerResult:
        """
        Calculate folded flyer quote with exact Shopify pricing
        
        Args:
            quantity: Number of flyers (100-10000)
            print_sides: Single or double sided printing
            print_type: Colour or black & white
            finish_size: A5, A4, A3, or 6pp A4
            paper_stock: Paper stock type and GSM
            artworks: Number of artwork designs (1-50)
            fold_type: Single, double, or triple fold
            celloglaze: Lamination option (only for Satin stocks)
        
        Returns:
            FoldedFlyerResult with complete pricing breakdown
        """
        
        # Validate celloglaze is only for Satin stocks
        if celloglaze != Celloglaze.NONE and paper_stock.stock_type != "Satin":
            raise ValueError("Celloglaze is only available for Satin paper stocks")
        
        # Step 1: Calculate Setup Costs
        impos_setup = self.IMPOS_SETUP
        guilo_setup = self.GUILO_SETUP
        folder_setup = self.FOLDER_SETUP
        
        # Celloglaze setup (if applicable)
        cello_setup = celloglaze.setup_cost
        
        # Artwork setup (extra artworks beyond first)
        artwork_setup = Decimal('0')
        if artworks > 1:
            artwork_setup = (Decimal(str(artworks)) * self.EXTRA_ARTS) - self.EXTRA_ARTS
        
        setup_total = impos_setup + guilo_setup + folder_setup + cello_setup + artwork_setup
        
        # Step 2: Calculate Sheets Needed
        sheets_needed = (Decimal(str(quantity)) / finish_size.items_per_sheet) * self.STOCK_WASTE
        
        # Step 3: Calculate Stock Cost
        stock_cost = (sheets_needed / Decimal('1000')) * paper_stock.cost_per_1000
        
        # Step 4: Calculate Click Cost
        click_cost = sheets_needed * Decimal(str(print_sides.multiplier)) * print_type.cost_per_sheet
        
        # Step 5: Calculate Cutting Cost
        cutting_cost = (sheets_needed / self.CUTTING_BLOCK) * self.CUT_COST
        
        # Step 6: Calculate Folding Cost
        folding_cost = (Decimal(str(quantity)) * Decimal(str(fold_type.multiplier)) / Decimal('1000')) * self.FOLD_PER_THOUSAND
        
        # Step 7: Calculate Cello Cost
        cello_cost = Decimal('0')
        if celloglaze != Celloglaze.NONE:
            cello_cost = sheets_needed * celloglaze.cost_per_sheet
        
        # Step 8: Calculate BizCost
        biz_cost = setup_total + stock_cost + click_cost + cutting_cost + folding_cost + cello_cost
        
        # Step 9: Determine Profit Margin
        profit_margin_rate = self._get_profit_margin(biz_cost, finish_size, quantity)
        profit = biz_cost * profit_margin_rate
        
        # Step 10: Calculate Subtotal
        subtotal = biz_cost + profit
        
        # Step 11: Calculate GST and Final Price
        final_price = subtotal * self.GST_RATE
        gst = final_price - subtotal
        
        # Round to 2 decimal places
        final_price = final_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        gst = gst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Build specifications
        specifications = {
            'quantity': quantity,
            'print_sides': print_sides.title,
            'print_type': print_type.title,
            'finish_size': finish_size.title,
            'paper_stock': paper_stock.title,
            'artworks': artworks,
            'fold_type': fold_type.title,
            'celloglaze': celloglaze.title,
            'sheets_needed': float(sheets_needed),
            'items_per_sheet': float(finish_size.items_per_sheet)
        }
        
        return FoldedFlyerResult(
            quantity=quantity,
            finish_size=finish_size.title,
            paper_stock=paper_stock.title,
            fold_type=fold_type.title,
            setup_total=setup_total,
            stock_cost=stock_cost,
            click_cost=click_cost,
            cutting_cost=cutting_cost,
            folding_cost=folding_cost,
            cello_cost=cello_cost,
            biz_cost=biz_cost,
            profit_margin_rate=profit_margin_rate,
            profit=profit,
            subtotal=subtotal,
            gst=gst,
            final_price=final_price,
            specifications=specifications
        )


# ============================================================================
# DEMONSTRATION & TESTING
# ============================================================================

def main():
    """Demonstrate the Folded Flyers calculator"""
    calc = FoldedFlyersShopifyCalculator()
    
    print("=" * 80)
    print("SHOPIFY FOLDED FLYERS CALCULATOR - DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Test 1: Standard A4 bi-fold brochure
    print("TEST 1: Standard A4 Bi-Fold Brochure")
    print("-" * 80)
    result1 = calc.calculate_quote(
        quantity=1000,
        print_sides=PrintSides.DOUBLE_SIDE,
        print_type=PrintType.COLOUR,
        finish_size=FinishSize.A4,
        paper_stock=PaperStock.SATIN_150GSM,
        artworks=1,
        fold_type=FoldType.SINGLE_FOLD,
        celloglaze=Celloglaze.NONE
    )
    print(result1)
    
    # Test 2: Premium A5 tri-fold with lamination
    print("TEST 2: Premium A5 Tri-Fold with Lamination")
    print("-" * 80)
    result2 = calc.calculate_quote(
        quantity=500,
        print_sides=PrintSides.DOUBLE_SIDE,
        print_type=PrintType.COLOUR,
        finish_size=FinishSize.A5,
        paper_stock=PaperStock.SATIN_300GSM,
        artworks=1,
        fold_type=FoldType.DOUBLE_FOLD,
        celloglaze=Celloglaze.ONE_SIDE_GLOSS
    )
    print(result2)
    
    # Test 3: Large format A3 single fold menu
    print("TEST 3: Large Format A3 Single Fold Menu")
    print("-" * 80)
    result3 = calc.calculate_quote(
        quantity=250,
        print_sides=PrintSides.DOUBLE_SIDE,
        print_type=PrintType.COLOUR,
        finish_size=FinishSize.A3,
        paper_stock=PaperStock.SATIN_250GSM,
        artworks=1,
        fold_type=FoldType.SINGLE_FOLD,
        celloglaze=Celloglaze.TWO_SIDE_MATT
    )
    print(result3)
    
    # Test 4: High volume 6-panel brochure
    print("TEST 4: High Volume 6-Panel Brochure")
    print("-" * 80)
    result4 = calc.calculate_quote(
        quantity=5000,
        print_sides=PrintSides.DOUBLE_SIDE,
        print_type=PrintType.COLOUR,
        finish_size=FinishSize.A4_6PP,
        paper_stock=PaperStock.SATIN_128GSM,
        artworks=1,
        fold_type=FoldType.DOUBLE_FOLD,
        celloglaze=Celloglaze.NONE
    )
    print(result4)


if __name__ == "__main__":
    main()
