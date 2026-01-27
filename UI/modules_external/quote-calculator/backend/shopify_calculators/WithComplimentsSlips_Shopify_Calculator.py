"""
With Compliments Slips Shopify Calculator
REWRITTEN Jan 24, 2026 - Exact TXT formula implementation (lines 2581-2930)

Based on: SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt (lines 2581-2930)
Platform: Shopify
Fields: F1-F6 (Quantity, Print Sides, Print Type, Finish Size, Paper Stock, Artworks)

Key Features:
- DL size only (99mm × 210mm) - 6 slips per sheet (F4.price)
- Setup costs: impos=15, guilo=12, extraArts=15 (first artwork FREE)
- Paper stocks: Uncoated Bond 80GSM ($26.34), 90GSM ($29.51), 100GSM ($32.68) per 1000 sheets
- Print types: Colour ($0.044/sheet), Black & White ($0.02/sheet)
- Print sides: Single (1× multiplier), Double (2× multiplier)
- Stock waste: 1.05 (5% wastage)
- Cutting cost: $11 per 500 sheets
- Profit margins: 11 tiers (170% for $1-50.99 down to 25% for $5001-100k, then fixed $200)
- Double GST: ×1.1 ×1.1 = 1.21 total

IDENTICAL to Printed Letterheads except F4.price = 6 slips per sheet (vs 2 sheets per letterhead)
"""

import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import sys

# Import config manager
from config_manager import config_manager


@dataclass
class WithComplimentsSlipsShopifyCalculatorQuoteResult:
    """Result from With Compliments Slips Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class WithComplimentsSlipsShopifyCalculator:
    """
    With Compliments Slips Shopify Calculator - REWRITTEN Jan 24, 2026
    
    Exact TXT formula implementation from lines 2581-2930
    
    Formula steps:
    1. Setup costs: impos (15) + guilo (12) + extra artworks (first FREE, $15 each after)
    2. Calculate sheets needed: (quantity / slips_per_sheet) × stockWaste
    3. Stock cost: ((sheets / 1000) × stock_price_per_1000) × stockWaste
    4. Click cost: sheets × print_sides_multiplier × print_type_price
    5. Cutting cost: (sheets / 500) × 11
    6. Subtotal = all costs
    7. Profit margin: 11 tiers based on subtotal
    8. Total = (subtotal + profit) × 1.1 × 1.1 (double GST)
    """
    
    CONFIG_FILE = "Shopify_With_Compliments_Slips.json"
    
    def __init__(self, config_path: str = None):
        """Initialize With Compliments Slips Shopify calculator"""
        if config_path:
            self.config = self._load_config(config_path)
        else:
            try:
                self.config = config_manager.load_shopify_config(self.CONFIG_FILE)
            except FileNotFoundError as e:
                print(f"⚠️ Warning: {e}")
                self.config = None
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def calculate(self, **kwargs) -> WithComplimentsSlipsShopifyCalculatorQuoteResult:
        """
        Calculate With Compliments Slips quote - EXACT TXT formula implementation
        
        TXT Formula Order (lines 2581-2930):
        1. Setup costs (impos, guilo, extra artworks - first FREE)
        2. Sheet calculations (quantity / slips_per_sheet × stockWaste)
        3. Stock cost ((sheets / 1000) × stock_price_per_1000 × stockWaste)
        4. Click cost (sheets × print_sides_multiplier × print_type_price)
        5. Cutting cost ((sheets / 500) × 11)
        6. Subtotal = all costs
        7. Profit margin (11 tiers based on subtotal)
        8. Total = (subtotal + profit) × 1.1 × 1.1 (double GST)
        
        Args:
            quantity (int): F1 - Quantity (50-5000)
            print_sides (str): F2 - "Single side print" (1×) or "Double side print" (2×)
            print_type (str): F3 - "Colour" ($0.044/sheet) or "Black & White" ($0.02/sheet)
            finish_size (str): F4 - "DL - 99mm x 210mm" (6 slips per sheet)
            paper_stock (str): F5 - "Uncoated Bond 80GSM" ($26.34), "90GSM" ($29.51), "100GSM" ($32.68) per 1000
            artworks (int): F6 - Number of artwork designs (first FREE, $15 per additional)
        
        Returns:
            WithComplimentsSlipsShopifyCalculatorQuoteResult with pricing details
        """
        # Extract parameters with defaults
        quantity = int(kwargs.get('quantity', 250))
        print_sides = kwargs.get('print_sides', 'Single side print')
        print_type = kwargs.get('print_type', 'Colour')
        finish_size = kwargs.get('finish_size', 'DL - 99mm x 210mm')
        paper_stock = kwargs.get('paper_stock', kwargs.get('paper_stock_type', 'Uncoated Bond 80GSM'))
        artworks = int(kwargs.get('artworks', 1))

        if quantity <= 0:
            raise ValueError("Quantity must be > 0")

        # TXT Formula Constants
        impos_setup = Decimal('15')      # TXT: var imposSetup = 15
        guilo_setup = Decimal('12')      # TXT: var guiloSetup = 12
        extra_arts = Decimal('15')       # TXT: var extraArts = 15
        stock_waste = Decimal('1.05')    # TXT: var stockWaste = 1.05
        cutting_blk = Decimal('500')     # TXT: var cuttingBlk = 500
        cut_cost = Decimal('11')         # TXT: var cutCost = 11

        # TXT: var _a = {art} * {extraArts}
        # TXT: var _a2 = {_a} <= {extraArts} ? 0 : ({_a} - {extraArts})
        # First artwork is FREE, then $15 per additional
        if artworks <= 1:
            artwork_setup_cost = Decimal('0')
        else:
            artwork_setup_cost = (Decimal(artworks) - Decimal('1')) * extra_arts

        # TXT: var totalSetupCost = {imposSetup} + {guiloSetup} + {_a2}
        total_setup_cost = impos_setup + guilo_setup + artwork_setup_cost

        # Get field values using extraction methods
        slips_per_sheet = self._get_slips_per_sheet(finish_size)            # F4.price
        stock_price = self._get_stock_price(paper_stock)                    # F5.price
        print_sides_multiplier = self._get_print_sides_multiplier(print_sides)  # F2.price
        print_type_price = self._get_print_type_price(print_type)          # F3.price

        # TXT: var totalSheetsPrinted = {F1.Price}/{F4.price} * {stockWaste}
        sheets_needed = (Decimal(quantity) / slips_per_sheet) * stock_waste

        # TXT: var totalCostOfSheets = ((({F1.price}/{F4.price}) / 1000) * {F5.price}) * {stockWaste}
        stock_cost = ((Decimal(quantity) / slips_per_sheet) / Decimal('1000')) * stock_price * stock_waste

        # TXT: var clickCost = {totalSheetsPrinted} * {F2.price} * {F3.price}
        click_cost = sheets_needed * print_sides_multiplier * print_type_price

        # TXT: var cuttingCost = {totalSheetsPrinted} / {cuttingBlk} * {cutCost}
        cutting_cost = (sheets_needed / cutting_blk) * cut_cost

        # TXT: var subTotal = {totalSetupCost} + {totalCostOfSheets} + {clickCost} + {cuttingCost}
        biz_cost = total_setup_cost + stock_cost + click_cost + cutting_cost

        # TXT: var profitMargin = ... (11 tiers)
        profit_margin_rate = self._get_profit_margin(float(biz_cost))
        
        # TXT: profit calculation (note: TXT uses subtotal * margin, not subtotal + margin)
        profit_amount = biz_cost * profit_margin_rate
        sub_total = biz_cost + profit_amount

        # TXT: var total = ({subTotal} + ({subTotal}*{profitMargin})) * 1.1
        # TXT: {total}*1.1
        # DOUBLE GST: ×1.1 ×1.1 = ×1.21
        GST_RATE = Decimal('1.1')
        total_after_first_gst = sub_total * GST_RATE
        total_price = total_after_first_gst * GST_RATE
        total_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        cost_per_item = total_price / Decimal(quantity)
        unit_price = cost_per_item

        breakdown = {
            'setup_costs': total_setup_cost,
            'impos_setup': impos_setup,
            'guilo_setup': guilo_setup,
            'artwork_setup_cost': artwork_setup_cost,
            'stock_cost': stock_cost,
            'click_cost': click_cost,
            'cutting_cost': cutting_cost,
            'biz_cost': biz_cost,
            'profit_margin_rate': profit_margin_rate,
            'profit_amount': profit_amount,
            'subtotal': sub_total,
            'first_gst': total_after_first_gst,
            'second_gst': total_price,
            'total_price': total_price,
            'sheets_needed': sheets_needed,
        }

        specifications = {
            'quantity': quantity,
            'slips_per_sheet': int(slips_per_sheet),
            'finish_size': finish_size,
            'print_sides': print_sides,
            'print_type': print_type,
            'paper_stock': paper_stock,
            'artworks': artworks,
            'stock_waste': float(stock_waste)
        }

        return WithComplimentsSlipsShopifyCalculatorQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            cost_per_item=cost_per_item,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    def _get_slips_per_sheet(self, finish_size: str) -> Decimal:
        """
        Get slips per sheet (F4.price)
        
        TXT shows F4 options:
        - "DL - 99mm x 210mm": price = 6
        
        Returns 6 for DL size (only option)
        """
        # DL size yields 6 slips per A3 sheet
        return Decimal('6')
    
    def _get_stock_price(self, paper_stock: str) -> Decimal:
        """
        Get stock price per 1000 sheets (F5.price)
        
        TXT shows F5 options:
        - "Uncoated Bond 80GSM": price = 26.34 per 1000 sheets
        - "Uncoated Bond 90GSM": price = 29.51 per 1000 sheets
        - "Uncoated Bond 100GSM": price = 32.68 per 1000 sheets
        """
        stock_prices = {
            'Uncoated Bond 80GSM': Decimal('26.34'),
            'Uncoated Bond 90GSM': Decimal('29.51'),
            'Uncoated Bond 100GSM': Decimal('32.68')
        }
        
        # Match against keys
        for key, price in stock_prices.items():
            if key in paper_stock or paper_stock in key:
                return price
        
        # Default to 80GSM
        return Decimal('26.34')
    
    def _get_print_sides_multiplier(self, print_sides: str) -> Decimal:
        """
        Get print sides multiplier (F2.price)
        
        TXT shows F2 options:
        - "Single side print": price = 1 (multiplier)
        - "Double side print": price = 2 (multiplier)
        """
        if 'Double' in print_sides:
            return Decimal('2')
        return Decimal('1')
    
    def _get_print_type_price(self, print_type: str) -> Decimal:
        """
        Get print type price per sheet (F3.price)
        
        TXT shows F3 options:
        - "Colour": price = 0.044 per sheet
        - "Black & White": price = 0.02 per sheet
        """
        if 'Colour' in print_type:
            return Decimal('0.044')
        return Decimal('0.02')
    
    def _get_profit_margin(self, subtotal: float) -> Decimal:
        """
        Get profit margin rate based on subtotal tiers
        
        TXT shows 11 tiers (same as Printed Letterheads):
        - $1-$50.99: 170% (1.7)
        - $51-$74.99: 155% (1.55)
        - $75-$100.99: 135% (1.35)
        - $101-$150.99: 130% (1.30)
        - $151-$200.99: 115% (1.15)
        - $201-$300.99: 70% (0.70)
        - $301-$400.99: 53% (0.53)
        - $401-$500.99: 40% (0.40)
        - $501-$1000.99: 30% (0.30)
        - $1001-$5000.99: 30% (0.30)
        - $5001-$100000.99: 25% (0.25)
        - $100001+: Fixed $200
        """
        if subtotal <= 50.999:
            return Decimal('1.7')
        elif subtotal <= 74.999:
            return Decimal('1.55')
        elif subtotal <= 100.999:
            return Decimal('1.35')
        elif subtotal <= 150.999:
            return Decimal('1.30')
        elif subtotal <= 200.999:
            return Decimal('1.15')
        elif subtotal <= 300.999:
            return Decimal('0.70')
        elif subtotal <= 400.999:
            return Decimal('0.53')
        elif subtotal <= 500.999:
            return Decimal('0.40')
        elif subtotal <= 1000.999:
            return Decimal('0.30')
        elif subtotal <= 5000.999:
            return Decimal('0.30')
        elif subtotal <= 100000.999:
            return Decimal('0.25')
        else:
            # For jobs over $100k, fixed $200 profit
            return Decimal('200')
    
    def _get_padding_rate(self, quantity: int) -> Decimal:
        """Get padding rate (no tiers defined)"""
        return Decimal('0.10')
