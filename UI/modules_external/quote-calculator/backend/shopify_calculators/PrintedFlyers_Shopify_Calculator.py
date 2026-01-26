#!/usr/bin/env python3
"""
Shopify Printed Flyers Calculator - Website Pricing Match
==========================================================

Extracted from: SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt (lines 11360+)
Source: inhouseprint.com.au Shopify WooCommerce DPO plugin
Status: Shopify Hardcoded Pricing (NOT database-driven)

Key Features:
- F1-F6 field structure (Quantity, Print Sides, Print Type, Finish Size, Paper Stock, Artworks)
- Items-per-sheet calculation (DL=6, A6=8, A5=4, A4=2, A3=1)
- 11-tier profit margin system (1.7 → 0.25 based on subtotal)
- 10% discount for quantities ≥ 1000
- 5% stock waste factor
- Setup costs: $15 imposition + $12 guillotine + artwork setup

Price Components:
1. Setup Costs: $15 + $12 + artwork extras
2. Stock Cost: (Sheets / 1000) * Price per 1000 sheets
3. Click Cost: Sheets * Sides Multiplier * Print Type Price
4. Cutting Cost: (Sheets / 500) * $11
5. Profit Margin: 11-tier lookup based on subtotal
6. GST: 10% on final total
7. Quantity Discount: If qty >= 1000, apply 10% discount

Author: Created from JSON specification
Date: January 23, 2026
Status: Production-ready Shopify Calculator
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class PrintSides(Enum):
    """Print sides options"""
    SINGLE = ("Single", 1)
    DOUBLE = ("Double", 2)
    
    def __init__(self, title, multiplier):
        self.title = title
        self.multiplier = multiplier


class PrintType(Enum):
    """Print type options"""
    COLOUR = ("Colour", Decimal('0.044'))
    BLACK_WHITE = ("Black & White", Decimal('0.02'))
    
    def __init__(self, title, cost_per_sheet):
        self.title = title
        self.cost_per_sheet = cost_per_sheet


class FinishSize(Enum):
    """Finish size options with items per sheet"""
    DL = ("DL - 99mm x 210mm", 99, 210, 6)
    A6 = ("A6 - 105mm x 148mm", 105, 148, 8)
    A5 = ("A5 - 148mm x 210mm", 148, 210, 4)
    A4 = ("A4 - 210mm x 297mm", 210, 297, 2)
    A3 = ("A3 - 297mm x 420mm", 297, 420, 1)
    
    def __init__(self, title, width, height, items_per_sheet):
        self.title = title
        self.width = width
        self.height = height
        self.items_per_sheet = items_per_sheet


class PaperStock(Enum):
    """Paper stock options with pricing per 1000 sheets"""
    SATIN_128GSM = ("Satin 128GSM", Decimal('45'), 128)
    SATIN_150GSM = ("Satin 150GSM", Decimal('54'), 150)
    SATIN_170GSM = ("Satin 170GSM", Decimal('105'), 170)
    SATIN_250GSM = ("Satin 250GSM", Decimal('105'), 250)
    SATIN_300GSM = ("Satin 300GSM", Decimal('126'), 300)
    SATIN_350GSM = ("Satin 350GSM", Decimal('150'), 350)
    UNCOATED_80GSM = ("Uncoated Bond 80GSM", Decimal('26.34'), 80)
    UNCOATED_90GSM = ("Uncoated Bond 90GSM", Decimal('29.51'), 90)
    UNCOATED_100GSM = ("Uncoated Bond 100GSM", Decimal('32.68'), 100)
    
    def __init__(self, title, cost_per_1000, gsm):
        self.title = title
        self.cost_per_1000 = cost_per_1000
        self.gsm = gsm


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class PrintedFlyerResult:
    """Quote result for printed flyers"""
    # Product details
    quantity: int
    finish_size: str
    paper_stock: str
    print_sides: str
    print_type: str
    artworks: int
    
    # Cost breakdown
    setup_cost: Decimal
    stock_cost: Decimal
    click_cost: Decimal
    cutting_cost: Decimal
    sheets_needed: Decimal
    
    # Totals
    subtotal: Decimal
    profit_margin_rate: Decimal
    profit_amount: Decimal
    total_before_gst: Decimal
    gst_amount: Decimal
    total_inc_gst: Decimal
    discount_applied: bool
    final_price: Decimal
    
    # Per unit pricing
    price_per_unit_ex_gst: Decimal
    price_per_unit_inc_gst: Decimal
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'success': True,
            'product_type': 'Printed Flyers',
            'quantity': self.quantity,
            'finish_size': self.finish_size,
            'paper_stock': self.paper_stock,
            'print_sides': self.print_sides,
            'print_type': self.print_type,
            'artworks': self.artworks,
            'breakdown': {
                'setup_cost': float(self.setup_cost),
                'stock_cost': float(self.stock_cost),
                'click_cost': float(self.click_cost),
                'cutting_cost': float(self.cutting_cost),
                'sheets_needed': float(self.sheets_needed),
                'subtotal': float(self.subtotal),
                'profit_margin_rate': f"{float(self.profit_margin_rate * 100):.1f}%",
                'profit_amount': float(self.profit_amount),
                'total_before_gst': float(self.total_before_gst),
                'gst_amount': float(self.gst_amount),
                'total_inc_gst': float(self.total_inc_gst),
                'discount_applied': self.discount_applied,
                'discount_amount': float(self.total_inc_gst - self.final_price) if self.discount_applied else 0
            },
            'total_price': float(self.final_price),
            'unit_price': float(self.price_per_unit_inc_gst),
            'price_per_unit_ex_gst': float(self.price_per_unit_ex_gst),
            'price_per_unit_inc_gst': float(self.price_per_unit_inc_gst)
        }


# ============================================================================
# PRINTED FLYERS CALCULATOR
# ============================================================================

class PrintedFlyersShopifyCalculator:
    """
    Shopify Printed Flyers Calculator
    
    Formula Steps:
    1. Artwork setup: First free, then $15 each
    2. Total setup: $15 (imposition) + $12 (guillotine) + artwork extras
    3. Sheets needed: (quantity / items_per_sheet) * 1.05 (5% waste)
    4. Stock cost: (sheets / 1000) * price_per_1000_sheets
    5. Click cost: sheets * sides_multiplier * price_per_sheet
    6. Cutting cost: (sheets / 500) * $11
    7. Subtotal: setup + stock + click + cutting
    8. Profit margin: 11-tier lookup based on subtotal
    9. Total before GST: subtotal + (subtotal * margin)
    10. GST: total * 1.1
    11. Discount: If qty >= 1000, apply 10% discount
    """
    
    # Constants
    IMPOSITION_SETUP = Decimal('15')
    GUILLOTINE_SETUP = Decimal('12')
    EXTRA_ARTWORK_COST = Decimal('15')
    STOCK_WASTE_FACTOR = Decimal('1.05')
    CUTTING_BLOCK_SIZE = Decimal('500')
    CUTTING_COST_PER_BLOCK = Decimal('11')
    GST_RATE = Decimal('1.1')
    DISCOUNT_QUANTITY_THRESHOLD = 1000
    DISCOUNT_RATE = Decimal('0.9')  # 10% discount = multiply by 0.9
    
    # 11-tier profit margin system
    PROFIT_MARGINS = [
        (Decimal('1'), Decimal('50.999'), Decimal('1.7')),      # 170%
        (Decimal('51'), Decimal('74.999'), Decimal('1.55')),    # 155%
        (Decimal('75'), Decimal('100.999'), Decimal('1.35')),   # 135%
        (Decimal('101'), Decimal('150.999'), Decimal('1.30')),  # 130%
        (Decimal('151'), Decimal('200.999'), Decimal('1.15')),  # 115%
        (Decimal('201'), Decimal('300.999'), Decimal('0.70')),  # 70%
        (Decimal('301'), Decimal('400.999'), Decimal('0.53')),  # 53%
        (Decimal('401'), Decimal('500.999'), Decimal('0.40')),  # 40%
        (Decimal('501'), Decimal('1000.999'), Decimal('0.30')), # 30%
        (Decimal('1001'), Decimal('5000.999'), Decimal('0.30')),# 30%
        (Decimal('5001'), Decimal('100000.999'), Decimal('0.25')) # 25%
    ]
    
    def __init__(self):
        """Initialize calculator"""
        pass
    
    def _get_profit_margin(self, subtotal: Decimal) -> Decimal:
        """
        Get profit margin based on subtotal using 11-tier system
        
        Args:
            subtotal: Cost subtotal before margin
            
        Returns:
            Profit margin multiplier (e.g., 1.7 for 170% markup)
        """
        for min_val, max_val, margin in self.PROFIT_MARGINS:
            if min_val <= subtotal <= max_val:
                return margin
        
        # Default to highest tier margin if beyond range
        return Decimal('0.25')
    
    def calculate(
        self,
        quantity: int,
        print_sides: str,
        print_type: str,
        finish_size: str,
        paper_stock: str,
        artworks: int = 1
    ) -> PrintedFlyerResult:
        """
        Calculate printed flyer quote
        
        Args:
            quantity: Number of flyers (100, 250, 500, 1000, 2000, 5000, 10000)
            print_sides: "Single" or "Double"
            print_type: "Colour" or "Black & White"
            finish_size: Size option (DL, A6, A5, A4, A3)
            paper_stock: Paper stock option
            artworks: Number of different artworks (1-50, default 1)
            
        Returns:
            PrintedFlyerResult with pricing breakdown
        """
        # Parse enums
        sides_enum = PrintSides.SINGLE if "Single" in print_sides else PrintSides.DOUBLE
        type_enum = PrintType.COLOUR if "Colour" in print_type else PrintType.BLACK_WHITE
        
        # Find finish size
        size_enum = None
        for size in FinishSize:
            if finish_size in size.title or finish_size == size.name:
                size_enum = size
                break
        if not size_enum:
            raise ValueError(f"Invalid finish size: {finish_size}")
        
        # Find paper stock
        stock_enum = None
        for stock in PaperStock:
            if paper_stock in stock.title or paper_stock.replace(" ", "_").upper() == stock.name:
                stock_enum = stock
                break
        if not stock_enum:
            raise ValueError(f"Invalid paper stock: {paper_stock}")
        
        # STEP 1: Artwork setup
        # First artwork is free, then $15 each
        artwork_extra = max(0, artworks - 1) * self.EXTRA_ARTWORK_COST
        
        # STEP 2: Total setup cost
        setup_cost = self.IMPOSITION_SETUP + self.GUILLOTINE_SETUP + artwork_extra
        
        # STEP 3: Sheets needed (with 5% waste)
        sheets_needed = (Decimal(quantity) / Decimal(size_enum.items_per_sheet)) * self.STOCK_WASTE_FACTOR
        
        # STEP 4: Stock cost
        stock_cost = (sheets_needed / Decimal('1000')) * stock_enum.cost_per_1000
        
        # STEP 5: Click cost (print cost)
        click_cost = sheets_needed * Decimal(sides_enum.multiplier) * type_enum.cost_per_sheet
        
        # STEP 6: Cutting cost
        cutting_cost = (sheets_needed / self.CUTTING_BLOCK_SIZE) * self.CUTTING_COST_PER_BLOCK
        
        # STEP 7: Subtotal
        subtotal = setup_cost + stock_cost + click_cost + cutting_cost
        
        # STEP 8: Profit margin
        profit_margin_rate = self._get_profit_margin(subtotal)
        profit_amount = subtotal * profit_margin_rate
        
        # STEP 9: Total before GST
        total_before_gst = subtotal + profit_amount
        
        # STEP 10: Apply GST
        total_inc_gst = total_before_gst * self.GST_RATE
        
        # STEP 11: Quantity discount OR second GST application (website bug)
        # Website formula: {F1.price} >= 1000 ? ({total}/100)*90 : {total}*1.1
        # This means: discount for >=1000, OR multiply by 1.1 AGAIN for <1000 (double GST!)
        discount_applied = quantity >= self.DISCOUNT_QUANTITY_THRESHOLD
        if discount_applied:
            final_price = total_inc_gst * self.DISCOUNT_RATE  # Apply 10% discount
        else:
            final_price = total_inc_gst * self.GST_RATE  # Apply GST AGAIN (website quirk)
        
        # Calculate GST amount
        gst_amount = final_price - (final_price / self.GST_RATE)
        
        # Per unit pricing
        price_per_unit_ex_gst = (final_price / self.GST_RATE) / Decimal(quantity)
        price_per_unit_inc_gst = final_price / Decimal(quantity)
        
        # Round all monetary values to 2 decimal places
        setup_cost = setup_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        stock_cost = stock_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        click_cost = click_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        cutting_cost = cutting_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        sheets_needed = sheets_needed.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        subtotal = subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        profit_amount = profit_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_before_gst = total_before_gst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        gst_amount = gst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_inc_gst = total_inc_gst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        final_price = final_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        price_per_unit_ex_gst = price_per_unit_ex_gst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        price_per_unit_inc_gst = price_per_unit_inc_gst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return PrintedFlyerResult(
            quantity=quantity,
            finish_size=size_enum.title,
            paper_stock=stock_enum.title,
            print_sides=sides_enum.title,
            print_type=type_enum.title,
            artworks=artworks,
            setup_cost=setup_cost,
            stock_cost=stock_cost,
            click_cost=click_cost,
            cutting_cost=cutting_cost,
            sheets_needed=sheets_needed,
            subtotal=subtotal,
            profit_margin_rate=profit_margin_rate,
            profit_amount=profit_amount,
            total_before_gst=total_before_gst,
            gst_amount=gst_amount,
            total_inc_gst=total_inc_gst,
            discount_applied=discount_applied,
            final_price=final_price,
            price_per_unit_ex_gst=price_per_unit_ex_gst,
            price_per_unit_inc_gst=price_per_unit_inc_gst
        )


# ============================================================================
# TOOL INTERFACE
# ============================================================================

def calculate_printed_flyers_shopify(
    quantity: int,
    print_sides: str = "Double",
    print_type: str = "Colour",
    finish_size: str = "A5",
    paper_stock: str = "Satin 150GSM",
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate Printed Flyers quote - Shopify pricing
    
    Args:
        quantity: Number of flyers (100, 250, 500, 1000, 2000, 5000, 10000)
        print_sides: "Single" or "Double" (default: "Double")
        print_type: "Colour" or "Black & White" (default: "Colour")
        finish_size: "DL", "A6", "A5", "A4", "A3" (default: "A5")
        paper_stock: Paper stock option (default: "Satin 150GSM")
            Options: "Satin 128GSM", "Satin 150GSM", "Satin 200GSM", "Satin 250GSM",
                     "Satin 300GSM", "Satin 350GSM", "Uncoated Bond 80GSM",
                     "Uncoated Bond 90GSM", "Uncoated Bond 100GSM"
        artworks: Number of different artworks (1-50, default: 1)
    
    Returns:
        Dict with quote details, pricing breakdown, and success status
        
    Example:
        >>> result = calculate_printed_flyers_shopify(
        ...     quantity=1000,
        ...     print_sides="Double",
        ...     print_type="Colour",
        ...     finish_size="A5",
        ...     paper_stock="Satin 150GSM",
        ...     artworks=1
        ... )
        >>> print(f"Total: ${result['total_price']:.2f}")
    """
    try:
        calculator = PrintedFlyersShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            print_sides=print_sides,
            print_type=print_type,
            finish_size=finish_size,
            paper_stock=paper_stock,
            artworks=artworks
        )
        return result.to_dict()
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'product_type': 'Printed Flyers'
        }


# ============================================================================
# CLI TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("PRINTED FLYERS CALCULATOR - TEST CASES")
    print("=" * 80)
    
    test_cases = [
        {
            'name': 'TEST 1: Small quantity (100), DL size, Colour, Double sided',
            'params': {
                'quantity': 100,
                'print_sides': 'Double',
                'print_type': 'Colour',
                'finish_size': 'DL',
                'paper_stock': 'Satin 128GSM',
                'artworks': 1
            }
        },
        {
            'name': 'TEST 2: Medium quantity (500), A5 size, Black & White, Single sided',
            'params': {
                'quantity': 500,
                'print_sides': 'Single',
                'print_type': 'Black & White',
                'finish_size': 'A5',
                'paper_stock': 'Uncoated Bond 80GSM',
                'artworks': 1
            }
        },
        {
            'name': 'TEST 3: Large quantity with discount (1000), A4 size, Colour, Double sided',
            'params': {
                'quantity': 1000,
                'print_sides': 'Double',
                'print_type': 'Colour',
                'finish_size': 'A4',
                'paper_stock': 'Satin 150GSM',
                'artworks': 2
            }
        },
        {
            'name': 'TEST 4: Bulk quantity (5000), A3 size, Colour, Double sided',
            'params': {
                'quantity': 5000,
                'print_sides': 'Double',
                'print_type': 'Colour',
                'finish_size': 'A3',
                'paper_stock': 'Satin 250GSM',
                'artworks': 1
            }
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{test['name']}")
        print("-" * 80)
        result = calculate_printed_flyers_shopify(**test['params'])
        
        if result['success']:
            print(f"Quantity: {result['quantity']}")
            print(f"Size: {result['finish_size']}")
            print(f"Stock: {result['paper_stock']}")
            print(f"Print: {result['print_sides']} sided, {result['print_type']}")
            print(f"Artworks: {result['artworks']}")
            print(f"\nBreakdown:")
            print(f"  Setup: ${result['breakdown']['setup_cost']:.2f}")
            print(f"  Stock: ${result['breakdown']['stock_cost']:.2f}")
            print(f"  Click: ${result['breakdown']['click_cost']:.2f}")
            print(f"  Cutting: ${result['breakdown']['cutting_cost']:.2f}")
            print(f"  Sheets: {result['breakdown']['sheets_needed']:.2f}")
            print(f"  Subtotal: ${result['breakdown']['subtotal']:.2f}")
            print(f"  Profit Margin: {result['breakdown']['profit_margin_rate']}")
            print(f"  Profit Amount: ${result['breakdown']['profit_amount']:.2f}")
            print(f"  Before GST: ${result['breakdown']['total_before_gst']:.2f}")
            print(f"  GST: ${result['breakdown']['gst_amount']:.2f}")
            print(f"  After GST: ${result['breakdown']['total_inc_gst']:.2f}")
            if result['breakdown']['discount_applied']:
                print(f"  Discount (10%): -${result['breakdown']['discount_amount']:.2f}")
            print(f"\nTOTAL: ${result['total_price']:.2f} inc GST")
            print(f"Per Unit: ${result['unit_price']:.2f} inc GST")
        else:
            print(f"❌ ERROR: {result['error']}")
