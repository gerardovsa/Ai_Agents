"""
Printed Letterheads Shopify Calculator
Exact implementation of Shopify JavaScript formula from TXT lines 2115-2450

Based on: SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt lines 2115-2450
Platform: Shopify
Fields: 6 fields (F1-F6)
- F1: Quantity (50-5000) - price = quantity value
- F2: Print Sides (Single=1, Double=2 multiplier)
- F3: Print Type (Colour=0.044, B&W=0.02 per sheet)
- F4: Finish Size (A4 = 2 sheets per unit - letterheads use 2 per A4 sheet)
- F5: Paper Stock (80GSM=26.34, 90GSM=29.51, 100GSM=32.68 per 1000 sheets)
- F6: Artworks (number input)

Key Features:
- No celloglaze (unlike other Shopify calculators)
- Extra artworks: $15 each (first artwork free)
- 11 profit margin tiers (1.7 → 0.25, then fixed $200)
- Double GST: ×1.1 ×1.1 = 1.21 total
- Stock waste: 1.05
- Cutting cost: $11 per 500 sheets

Rewritten: January 24, 2026 - Exact TXT formula match
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
class PrintedLetterheadsShopifyCalculatorQuoteResult:
    """Result from Printed Letterheads Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class PrintedLetterheadsShopifyCalculator:
    """
    Printed Letterheads Shopify Calculator - Exact TXT Formula Implementation
    
    TXT Formula (lines 2115-2154):
    - imposSetup = 15
    - guiloSetup = 12
    - extraArts = 15 (per artwork, first free)
    - stockWaste = 1.05
    - cuttingBlk = 500
    - cutCost = 11
    - totalSetupCost = imposSetup + guiloSetup + extraArtsCost
    - totalCostOfSheets = (((quantity / F4.price) / 1000) * stockWaste) * F5.price
    - totalSheetsPrinted = (quantity / F4.price) * stockWaste
    - clickCost = totalSheetsPrinted * F2.price * F3.price
    - cuttingCost = (totalSheetsPrinted / 500) * 11
    - subTotal = setup + sheets + clicks + cutting
    - profitMargin = 11 tiers (1.7 → 0.25, then fixed $200)
    - total = (subTotal + (subTotal * profitMargin)) * 1.1 * 1.1 (DOUBLE GST)
    
    Fields:
    - F1: quantity (50-5000)
    - F2: print_sides (Single=1, Double=2) - multiplier
    - F3: print_type (Colour=0.044, B&W=0.02) - per sheet
    - F4: finish_size (A4 = 2 sheets per unit)
    - F5: paper_stock (80GSM=26.34, 90GSM=29.51, 100GSM=32.68) - per 1000 sheets
    - F6: artworks (number)
    """
    
    CONFIG_FILE = "Shopify_Printed_Letterheads.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Printed Letterheads Shopify calculator"""
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
    
    def calculate(self, **kwargs) -> PrintedLetterheadsShopifyCalculatorQuoteResult:
        """
        Calculate Printed Letterheads quote - EXACT TXT formula implementation
        
        TXT Formula Order:
        1. Setup costs (impos, guilo, extra artworks)
        2. Sheet calculations (quantity / sheets_per_unit × stockWaste)
        3. Stock cost ((sheets / 1000) × stock_price_per_1000 × stockWaste)
        4. Click cost (sheets × print_sides_multiplier × print_type_price)
        5. Cutting cost ((sheets / 500) × 11)
        6. Subtotal = all costs
        7. Profit margin (11 tiers based on subtotal)
        8. Total = (subtotal + profit) × 1.1 × 1.1 (double GST)
        
        Args:
            quantity (int): F1 - Quantity (50-5000)
            print_sides (str): F2 - "Single side print" or "Double side print"
            print_type (str): F3 - "Colour" or "Black & White"
            finish_size (str): F4 - "A4 - 210mm x 297mm" (only option)
            paper_stock (str): F5 - "Uncoated Bond 80GSM", "90GSM", or "100GSM"
            artworks (int): F6 - Number of artworks
        
        Returns:
            PrintedLetterheadsShopifyCalculatorQuoteResult with exact pricing
        """
        # Extract parameters with exact field names from JSON
        quantity = int(kwargs.get('quantity', kwargs.get('F1', 250)))
        print_sides = kwargs.get('print_sides', kwargs.get('F2', 'Single side print'))
        print_type = kwargs.get('print_type', kwargs.get('F3', 'Colour'))
        finish_size = kwargs.get('finish_size', kwargs.get('F4', 'A4 - 210mm x 297mm'))
        paper_stock = kwargs.get('paper_stock', kwargs.get('F5', 'Uncoated Bond 80GSM'))
        artworks = int(kwargs.get('artworks', kwargs.get('F6', 1)))

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')

        # TXT Constants
        impos_setup = Decimal('15')  # TXT: imposSetup = 15
        guilo_setup = Decimal('12')  # TXT: guiloSetup = 12
        extra_arts = Decimal('15')   # TXT: extraArts = 15
        stock_waste = Decimal('1.05')  # TXT: stockWaste = 1.05
        cutting_blk = Decimal('500')   # TXT: cuttingBlk = 500
        cut_cost = Decimal('11')       # TXT: cutCost = 11

        # TXT: var _a = {art} * {extraArts};
        # TXT: var _a2 = {_a} <= {extraArts} ? 0 : ({_a} - {extraArts});
        # This means: first artwork is free, each additional costs $15
        _a = Decimal(artworks) * extra_arts
        _a2 = Decimal('0') if _a <= extra_arts else (_a - extra_arts)

        # TXT: var totalSetupCost = {imposSetup} + {guiloSetup} + {_a2};
        total_setup_cost = impos_setup + guilo_setup + _a2

        # Get field values
        sheets_per_unit = self._get_sheets_per_unit(finish_size)  # F4.price
        stock_price_per_1000 = self._get_stock_price(paper_stock)  # F5.price
        print_sides_multiplier = self._get_print_sides_multiplier(print_sides)  # F2.price
        print_type_price = self._get_print_type_price(print_type)  # F3.price

        # TXT: var totalSheetsPrinted = {F1.Price}/{F4.price} * {stockWaste};
        # F1.price = quantity, F4.price = sheets per unit (2 for A4)
        total_sheets_printed = (Decimal(quantity) / sheets_per_unit) * stock_waste

        # TXT: var totalCostOfSheets = ((({F1.price}/{F4.price}) / 1000) * {stockWaste}) * {F5.price};
        total_cost_of_sheets = (((Decimal(quantity) / sheets_per_unit) / Decimal('1000')) * stock_waste) * stock_price_per_1000

        # TXT: var clickCost = {totalSheetsPrinted} * {F2.price} * {F3.price};
        click_cost = total_sheets_printed * print_sides_multiplier * print_type_price

        # TXT: var cuttingCost = {totalSheetsPrinted} / {cuttingBlk} * {cutCost};
        cutting_cost = (total_sheets_printed / cutting_blk) * cut_cost

        # TXT: var subTotal = {totalSetupCost} + {totalCostOfSheets} + {clickCost} + {cuttingCost};
        sub_total = total_setup_cost + total_cost_of_sheets + click_cost + cutting_cost

        # TXT: var profitMargin = [11 tiers based on subtotal]
        profit_margin_rate = self._get_profit_margin(float(sub_total))
        profit_amount = sub_total * profit_margin_rate

        # TXT: var total = ({subTotal} + ({subTotal}*{profitMargin})) * 1.1;
        # TXT: {total}*1.1
        # NOTE: Double GST (first line ×1.1, second line ×1.1 again)
        GST_RATE = Decimal('1.10')
        total_price = (sub_total + profit_amount) * GST_RATE * GST_RATE
        total_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        unit_price = total_price / Decimal(quantity)

        breakdown = {
            'impos_setup': impos_setup,
            'guilo_setup': guilo_setup,
            'extra_artworks_cost': _a2,
            'total_setup_cost': total_setup_cost,
            'sheets_per_unit': sheets_per_unit,
            'total_sheets_printed': total_sheets_printed,
            'stock_price_per_1000': stock_price_per_1000,
            'total_cost_of_sheets': total_cost_of_sheets,
            'print_sides_multiplier': print_sides_multiplier,
            'print_type_price': print_type_price,
            'click_cost': click_cost,
            'cutting_cost': cutting_cost,
            'subtotal': sub_total,
            'profit_margin_rate': profit_margin_rate,
            'profit_amount': profit_amount,
            'total_price': total_price,
        }

        specifications = {
            'quantity': quantity,
            'print_sides': print_sides,
            'print_type': print_type,
            'finish_size': finish_size,
            'paper_stock': paper_stock,
            'artworks': artworks,
            'sheets_printed': float(total_sheets_printed),
        }

        return PrintedLetterheadsShopifyCalculatorQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            cost_per_item=unit_price,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    def _get_sheets_per_unit(self, finish_size: str) -> Decimal:
        """
        Get sheets per unit from F4 field (TXT: F4.price)
        
        TXT JSON Field F4 - Finish Size:
        - "A4 - 210mm x 297mm" → 2 sheets per unit (letterheads use 2 per sheet)
        
        Note: This is unusual - most products use this field differently
        """
        # Only one option for letterheads
        if 'A4' in finish_size or 'a4' in finish_size.lower():
            return Decimal('2')
        
        # Default to 2 if not specified
        return Decimal('2')
    
    def _get_stock_price(self, paper_stock: str) -> Decimal:
        """
        Get paper stock price per 1000 sheets from F5 field (TXT: F5.price)
        
        TXT JSON Field F5 - Paper Stock Type:
        - "Uncoated Bond 80GSM" → $26.34 per 1000 sheets
        - "Uncoated Bond 90GSM" → $29.51 per 1000 sheets
        - "Uncoated Bond 100GSM" → $32.68 per 1000 sheets
        """
        stock_map = {
            'uncoated_bond_80gsm': Decimal('26.34'),
            'uncoated_bond_90gsm': Decimal('29.51'),
            'uncoated_bond_100gsm': Decimal('32.68'),
        }
        
        # Normalize key
        stock_key = paper_stock.lower().replace(' ', '_')
        if stock_key not in stock_map:
            raise ValueError(f"Invalid paper_stock: {paper_stock}. Must be one of: {list(stock_map.keys())}")
        
        return stock_map[stock_key]
    
    def _get_print_sides_multiplier(self, print_sides: str) -> Decimal:
        """
        Get print sides multiplier from F2 field (TXT: F2.price)
        
        TXT JSON Field F2 - Print Sides:
        - "Single side print" → 1 (multiplier)
        - "Double side print" → 2 (multiplier)
        """
        if 'double' in print_sides.lower():
            return Decimal('2')
        else:
            return Decimal('1')
    
    def _get_print_type_price(self, print_type: str) -> Decimal:
        """
        Get print type price per sheet from F3 field (TXT: F3.price)
        
        TXT JSON Field F3 - Print Type:
        - "Colour" → $0.044 per sheet
        - "Black & White" → $0.02 per sheet
        """
        if 'colour' in print_type.lower() or 'color' in print_type.lower():
            return Decimal('0.044')
        else:
            return Decimal('0.02')
    
    def _get_profit_margin(self, subtotal: float) -> Decimal:
        """
        Get profit margin rate based on subtotal - EXACT TXT tiers
        
        TXT JSON profit_margin_tiers (11 tiers + fixed):
        1. $1.00 - $50.99 → 1.7 (170%)
        2. $51.00 - $74.99 → 1.55 (155%)
        3. $75.00 - $100.99 → 1.35 (135%)
        4. $101.00 - $150.99 → 1.30 (130%)
        5. $151.00 - $200.99 → 1.15 (115%)
        6. $201.00 - $300.99 → 0.70 (70%)
        7. $301.00 - $400.99 → 0.53 (53%)
        8. $401.00 - $500.99 → 0.40 (40%)
        9. $501.00 - $1000.99 → 0.30 (30%)
        10. $1001.00 - $5000.99 → 0.30 (30%)
        11. $5001.00 - $100000.99 → 0.25 (25%)
        12. $100001.00+ → Fixed $200 margin
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
            # Fixed $200 margin for jobs over $100k
            return Decimal('200')
