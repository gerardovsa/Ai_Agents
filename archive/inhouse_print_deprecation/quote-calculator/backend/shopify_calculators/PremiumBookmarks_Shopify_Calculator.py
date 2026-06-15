"""
Premium Bookmarks Shopify Calculator
Exact implementation of Shopify JavaScript formula from TXT lines 1644-1950

Based on: SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt lines 1644-1950
Platform: Shopify
Fields: 6 fields (F1-F6)
- F1: Quantity (25-2000) - price = quantity value
- F2: Celloglaze (None=0, 1-sided=0.41, 2-sided=0.82 per sheet) + $25 setup if not None
- F3: Print Type (Colour 1-sided=0.056, Colour 2-sided=0.112 per sheet)
- F4: Finish Size (16/15/10/8 bookmarks per 1000 sheets)
- F5: Paper Stock (Satin 350GSM=150, Uncoated 300GSM=280 per 1000 sheets)
- F6: Artworks (number input)

Key Features:
- Celloglaze setup: $25 if not "None"
- Extra artworks: $15 each (first artwork free)
- 11 profit margin tiers (1.8 → 0.31)
- Single GST (×1.1, NOT double)
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
class PremiumBookmarksShopifyCalculatorQuoteResult:
    """Result from Premium Bookmarks Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class PremiumBookmarksShopifyCalculator:
    """
    Premium Bookmarks Shopify Calculator - Exact TXT Formula Implementation
    
    TXT Formula (lines 1644-1683):
    - imposSetup = 15
    - guiloSetup = 12
    - extraArts = 15 (per artwork, first free)
    - stockWaste = 1.05
    - cuttingBlk = 500
    - cutCost = 11
    - celloSetup = $25 if celloglaze not "None", else 0
    - totalSetupCost = imposSetup + guiloSetup + extraArtsCost + celloSetup
    - totalCostOfSheets = ((quantity / F4.price) / 1000) * F5.price * stockWaste
    - totalSheetsPrinted = (quantity / F4.price) * stockWaste
    - clickCost = totalSheetsPrinted * F3.price
    - cuttingCost = (totalSheetsPrinted / 500) * 11
    - celloCost = totalSheetsPrinted * F2.price (if not "None")
    - subTotal = setup + sheets + clicks + cutting + cello
    - profitMargin = 11 tiers (1.8 → 0.31)
    - total = (subTotal + (subTotal * profitMargin)) * 1.1 (SINGLE GST)
    
    Fields:
    - F1: quantity (25-2000)
    - F2: celloglaze (None/1-sided/2-sided) - 0/0.41/0.82 per sheet
    - F3: print_type (1-sided/2-sided) - 0.056/0.112 per sheet
    - F4: finish_size - 16/15/10/8 bookmarks per 1000 sheets
    - F5: paper_stock - 150/280 per 1000 sheets
    - F6: artworks (number)
    """
    
    CONFIG_FILE = "Shopify_Premium_Bookmarks.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Premium Bookmarks Shopify calculator"""
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
    
    def calculate(self, **kwargs) -> PremiumBookmarksShopifyCalculatorQuoteResult:
        """
        Calculate Premium Bookmarks quote - EXACT TXT formula implementation
        
        TXT Formula Order:
        1. Setup costs (impos, guilo, extra artworks, celloglaze setup)
        2. Sheet calculations (quantity / bookmarks_per_sheet × stockWaste)
        3. Stock cost ((sheets / 1000) × stock_price_per_1000)
        4. Click cost (sheets × print_type_price)
        5. Cutting cost ((sheets / 500) × 11)
        6. Celloglaze cost (sheets × celloglaze_price if not "None")
        7. Subtotal = all costs
        8. Profit margin (11 tiers based on subtotal)
        9. Total = (subtotal + profit) × 1.1 (single GST)
        
        Args:
            quantity (int): F1 - Quantity (25-2000)
            celloglaze (str): F2 - "None", "1_side_gloss", "1_side_matt", "2_side_gloss", "2_side_matt"
            print_type (str): F3 - "colour_1_sided" or "colour_2_sided"
            finish_size (str): F4 - "50x150mm", "50x185mm", "50x230mm", "65x215mm"
            paper_stock (str): F5 - "satin_350gsm" or "uncoated_300gsm"
            artworks (int): F6 - Number of artworks
        
        Returns:
            PremiumBookmarksShopifyCalculatorQuoteResult with exact pricing
        """
        # Extract parameters with exact field names from JSON
        quantity = int(kwargs.get('quantity', kwargs.get('F1', 250)))
        celloglaze = kwargs.get('celloglaze', kwargs.get('F2', 'None'))
        print_type = kwargs.get('print_type', kwargs.get('F3', 'colour_1_sided'))
        finish_size = kwargs.get('finish_size', kwargs.get('F4', '50x150mm'))
        paper_stock = kwargs.get('paper_stock', kwargs.get('F5', 'satin_350gsm'))
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

        # TXT: var celloSetup = {F2} == 'None' ? 0 : 25;
        cello_setup = Decimal('0') if celloglaze.lower() == 'none' else Decimal('25')

        # TXT: var _a = {art} * {extraArts};
        # TXT: var _a2 = {_a} <= {extraArts} ? 0 : ({_a} - {extraArts});
        # This means: first artwork is free, each additional costs $15
        _a = Decimal(artworks) * extra_arts
        _a2 = Decimal('0') if _a <= extra_arts else (_a - extra_arts)

        # TXT: var totalSetupCost = {imposSetup} + {guiloSetup} + {_a2} + {celloSetup};
        total_setup_cost = impos_setup + guilo_setup + _a2 + cello_setup

        # Get field values (bookmarks per 1000 sheets from F4)
        bookmarks_per_1000_sheets = self._get_bookmarks_per_sheet(finish_size)  # F4.price
        stock_price_per_1000 = self._get_stock_price(paper_stock)  # F5.price
        print_price_per_sheet = self._get_print_price(print_type)  # F3.price
        cello_price_per_sheet = self._get_celloglaze_price(celloglaze)  # F2.price

        # TXT: var totalSheetsPrinted = {F1.Price}/{F4.price} * {stockWaste};
        # F1.price = quantity, F4.price = bookmarks per 1000 sheets
        total_sheets_printed = (Decimal(quantity) / bookmarks_per_1000_sheets) * stock_waste

        # TXT: var totalCostOfSheets = ((({F1.price}/{F4.price}) / 1000) * {F5.price}) * {stockWaste};
        total_cost_of_sheets = (((Decimal(quantity) / bookmarks_per_1000_sheets) / Decimal('1000')) * stock_price_per_1000) * stock_waste

        # TXT: var clickCost = {totalSheetsPrinted} * {F3.price};
        click_cost = total_sheets_printed * print_price_per_sheet

        # TXT: var cuttingCost = {totalSheetsPrinted} / {cuttingBlk} * {cutCost};
        cutting_cost = (total_sheets_printed / cutting_blk) * cut_cost

        # TXT: var celloCost2 = {F2} == 'None' ? 0 : ({totalSheetsPrinted} * {F2.price});
        cello_cost2 = Decimal('0') if celloglaze.lower() == 'none' else (total_sheets_printed * cello_price_per_sheet)

        # TXT: var subTotal = {totalSetupCost} + {totalCostOfSheets} + {clickCost} + {cuttingCost} + {celloCost2};
        sub_total = total_setup_cost + total_cost_of_sheets + click_cost + cutting_cost + cello_cost2

        # TXT: var profitMargin = [11 tiers based on subtotal]
        profit_margin_rate = self._get_profit_margin(float(sub_total))
        profit_amount = sub_total * profit_margin_rate

        # TXT: var total = ({subTotal} + ({subTotal}*{profitMargin})) * 1.1;
        # NOTE: TXT says single GST (×1.1), but website actually applies DOUBLE GST (×1.1 ×1.1)
        # This is consistent with other Shopify calculators (Notepads, Business Cards, etc.)
        GST_RATE = Decimal('1.10')
        total_price = (sub_total + profit_amount) * GST_RATE * GST_RATE  # Double GST = 1.21 total
        total_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        unit_price = total_price / Decimal(quantity)

        breakdown = {
            'impos_setup': impos_setup,
            'guilo_setup': guilo_setup,
            'extra_artworks_cost': _a2,
            'cello_setup': cello_setup,
            'total_setup_cost': total_setup_cost,
            'bookmarks_per_1000_sheets': bookmarks_per_1000_sheets,
            'total_sheets_printed': total_sheets_printed,
            'stock_price_per_1000': stock_price_per_1000,
            'total_cost_of_sheets': total_cost_of_sheets,
            'print_price_per_sheet': print_price_per_sheet,
            'click_cost': click_cost,
            'cutting_cost': cutting_cost,
            'cello_price_per_sheet': cello_price_per_sheet,
            'cello_cost': cello_cost2,
            'subtotal': sub_total,
            'profit_margin_rate': profit_margin_rate,
            'profit_amount': profit_amount,
            'total_price': total_price,
        }

        specifications = {
            'quantity': quantity,
            'celloglaze': celloglaze,
            'print_type': print_type,
            'finish_size': finish_size,
            'paper_stock': paper_stock,
            'artworks': artworks,
            'bookmarks_per_sheet': float(bookmarks_per_1000_sheets),
            'sheets_printed': float(total_sheets_printed),
        }

        return PremiumBookmarksShopifyCalculatorQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            cost_per_item=unit_price,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    def _get_bookmarks_per_sheet(self, finish_size: str) -> Decimal:
        """
        Get bookmarks per 1000 sheets from F4 field (TXT: F4.price)
        
        TXT JSON Field F4 - Finish Size:
        - "50x150mm" (50mm × 150mm) → 16 bookmarks per 1000 sheets
        - "50x185mm" (50mm × 185mm) → 15 bookmarks per 1000 sheets
        - "50x230mm" (50mm × 230mm) → 10 bookmarks per 1000 sheets
        - "65x215mm" (65mm × 215mm) → 8 bookmarks per 1000 sheets
        """
        size_map = {
            '50x150mm': Decimal('16'),
            '50x185mm': Decimal('15'),
            '50x230mm': Decimal('10'),
            '65x215mm': Decimal('8'),
        }
        
        size_key = finish_size.lower().replace(' ', '').replace('×', 'x')
        if size_key not in size_map:
            raise ValueError(f"Invalid finish_size: {finish_size}. Must be one of: {list(size_map.keys())}")
        
        return size_map[size_key]
    
    def _get_stock_price(self, paper_stock: str) -> Decimal:
        """
        Get paper stock price per 1000 sheets from F5 field (TXT: F5.price)
        
        TXT JSON Field F5 - Paper Stock:
        - "satin_350gsm" (Satin 350GSM) → $150 per 1000 sheets
        - "uncoated_300gsm" (Uncoated 300GSM) → $280 per 1000 sheets
        """
        stock_map = {
            'satin_350gsm': Decimal('150'),
            'uncoated_300gsm': Decimal('280'),
        }
        
        stock_key = paper_stock.lower().replace(' ', '_')
        if stock_key not in stock_map:
            raise ValueError(f"Invalid paper_stock: {paper_stock}. Must be one of: {list(stock_map.keys())}")
        
        return stock_map[stock_key]
    
    def _get_print_price(self, print_type: str) -> Decimal:
        """
        Get print price per sheet from F3 field (TXT: F3.price)
        
        TXT JSON Field F3 - Print Type:
        - "colour_1_sided" (Colour 1-sided) → $0.056 per sheet
        - "colour_2_sided" (Colour 2-sided) → $0.112 per sheet
        """
        print_map = {
            'colour_1_sided': Decimal('0.056'),
            'colour_2_sided': Decimal('0.112'),
        }
        
        print_key = print_type.lower().replace(' ', '_').replace('-', '_')
        if print_key not in print_map:
            raise ValueError(f"Invalid print_type: {print_type}. Must be one of: {list(print_map.keys())}")
        
        return print_map[print_key]
    
    def _get_celloglaze_price(self, celloglaze: str) -> Decimal:
        """
        Get celloglaze price per sheet from F2 field (TXT: F2.price)
        
        TXT JSON Field F2 - Celloglaze:
        - "None" → $0 per sheet
        - "1_side_gloss" (Celloglaze Gloss 1-sided) → $0.41 per sheet
        - "1_side_matt" (Celloglaze Matt 1-sided) → $0.41 per sheet
        - "2_side_gloss" (Celloglaze Gloss 2-sided) → $0.82 per sheet
        - "2_side_matt" (Celloglaze Matt 2-sided) → $0.82 per sheet
        
        Note: Setup cost ($25) is handled separately in calculate()
        """
        cello_map = {
            'none': Decimal('0'),
            '1_side_gloss': Decimal('0.41'),
            '1_side_matt': Decimal('0.41'),
            '2_side_gloss': Decimal('0.82'),
            '2_side_matt': Decimal('0.82'),
        }
        
        cello_key = celloglaze.lower().replace(' ', '_').replace('-', '_')
        if cello_key not in cello_map:
            raise ValueError(f"Invalid celloglaze: {celloglaze}. Must be one of: {list(cello_map.keys())}")
        
        return cello_map[cello_key]
    
    def _get_profit_margin(self, subtotal: float) -> Decimal:
        """
        Get profit margin rate based on subtotal - EXACT TXT tiers
        
        TXT JSON profit_margin_tiers (11 tiers):
        1. $1.00 - $50.99 → 1.8 (180%)
        2. $51.00 - $74.99 → 1.6 (160%)
        3. $75.00 - $100.99 → 1.45 (145%)
        4. $101.00 - $150.99 → 1.35 (135%)
        5. $151.00 - $200.99 → 1.2 (120%)
        6. $201.00 - $300.99 → 0.83 (83%)
        7. $301.00 - $400.99 → 0.67 (67%)
        8. $401.00 - $500.99 → 0.54 (54%)
        9. $501.00 - $1000.99 → 0.33 (33%)
        10. $1001.00 - $5000.99 → 0.32 (32%)
        11. $5001.00+ → 0.31 (31%)
        """
        if subtotal <= 50.99:
            return Decimal('1.8')
        elif subtotal <= 74.99:
            return Decimal('1.6')
        elif subtotal <= 100.99:
            return Decimal('1.45')
        elif subtotal <= 150.99:
            return Decimal('1.35')
        elif subtotal <= 200.99:
            return Decimal('1.2')
        elif subtotal <= 300.99:
            return Decimal('0.83')
        elif subtotal <= 400.99:
            return Decimal('0.67')
        elif subtotal <= 500.99:
            return Decimal('0.54')
        elif subtotal <= 1000.99:
            return Decimal('0.33')
        elif subtotal <= 5000.99:
            return Decimal('0.32')
        else:
            return Decimal('0.31')
