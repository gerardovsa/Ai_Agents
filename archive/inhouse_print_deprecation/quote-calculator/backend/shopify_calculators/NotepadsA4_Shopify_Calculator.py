"""
Notepads A4 Shopify Calculator
Exact implementation of Shopify JavaScript formula for Notepads A4

Based on: SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt Lines 1098-1650
Platform: Shopify (separate from WooCommerce calculators)
Fields: F1 (Quantity), F2 (Artworks), F7 (Leaves Per Pad), F8 (Finish Size), F10 (Print Type), F11 (Stock Type)
Key Features: Premium padding rates (0.3/0.25/0.2), premium box board (0.15), A4 multiplier (1.0), DIFFERENT field IDs

REWRITTEN: January 24, 2026 - Complete rewrite to match exact TXT formula with A4-specific field IDs
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
class NotepadsA4ShopifyCalculatorQuoteResult:
    """Result from Notepads A4 Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class NotepadsA4ShopifyCalculator:
    """
    Notepads A4 Shopify Calculator - Exact Shopify JavaScript Implementation
    
    EXACT TXT FORMULA IMPLEMENTATION (Lines 1100-1144)
    
    CRITICAL DIFFERENCES from A5/A6:
    - Box board cost: 0.15 (PREMIUM - highest of all 3 sizes)
    - Padding rates: 0.3/0.25/0.2 (PREMIUM - highest of all 3 sizes)
    - Finish size multiplier: 1.0 (full sheet size)
    - Field IDs: F7, F8, F10, F11 (NOT F3, F4, F5, F6 like A5/A6)
    """
    
    CONFIG_FILE = "Shopify_Notepads_A4.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Notepads A4 Shopify calculator"""
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
    
    def calculate(self, **kwargs) -> NotepadsA4ShopifyCalculatorQuoteResult:
        """
        Calculate Notepads A4 Shopify quote using EXACT TXT FORMULA
        
        Args:
            quantity: Number of notepads
            artworks: Number of artworks (first free, $15 each additional)
            finish_size: Size option (A4 Portrait = 1.0 multiplier)
            leaves_per_pad: Number of leaves (25/50/100/200)
            print_type: Print type with price per sheet
            stock_type: Stock type with price per sheet
        
        Returns:
            NotepadsA4ShopifyCalculatorQuoteResult with pricing details
        """
        quantity = int(kwargs.get('quantity', kwargs.get('F1', 100)))
        artworks = int(kwargs.get('artworks', kwargs.get('F2', 1)))
        # CRITICAL: A4 uses F8 for finish size (not F3)
        finish_size = kwargs.get('finish_size', kwargs.get('F8', 'A4 Portrait'))
        # CRITICAL: A4 uses F7 for leaves (not F4)
        leaves_per_pad = kwargs.get('leaves_per_pad', kwargs.get('F7', 50))
        # CRITICAL: A4 uses F10 for print type (not F5)
        print_type = kwargs.get('print_type', kwargs.get('F10', 'Black & White 1 sided'))
        # CRITICAL: A4 uses F11 for stock type (not F6)
        stock_type = kwargs.get('stock_type', kwargs.get('F11', 'Uncoated Bond 80GSM'))

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')

        # Constants from TXT (same as A5/A6 except boxBoardC)
        guilo_setup = Decimal('12')
        impos_setup = Decimal('15')
        stock_waste = Decimal('1.05')
        extra_arts = Decimal('15')
        cutting_blk = Decimal('500')
        cut_cost = Decimal('11')
        box_board_c = Decimal('0.15')  # A4-specific: PREMIUM (highest of all 3)
        
        # Get field prices (using A4-specific field IDs F7, F8, F10, F11)
        finish_size_multiplier = self._get_finish_size_multiplier(finish_size)
        leaves_per_pad_value = self._get_leaves_per_pad_value(leaves_per_pad)
        print_type_price = self._get_print_type_price(print_type)
        stock_type_price = self._get_stock_type_price(stock_type)

        # 1. Artwork setup
        _a = Decimal(artworks) * extra_arts
        _a2 = Decimal('0') if _a <= extra_arts else (_a - extra_arts)

        # 2. Total setup cost
        total_setup_cost = impos_setup + guilo_setup + _a2

        # 3. Total leave sheets
        total_leave_sheets = ((Decimal(quantity) * leaves_per_pad_value) * stock_waste) * finish_size_multiplier

        # 4. Content click cost
        content_click_cost = total_leave_sheets * print_type_price

        # 5. Total content cost
        total_content_cost = (total_leave_sheets * stock_type_price) + content_click_cost + (box_board_c * Decimal(quantity))

        # 6. Cutting cost
        cutting_cost = (total_leave_sheets / cutting_blk) * cut_cost

        # 7. Padding cost (A4-specific PREMIUM rates)
        padding_rate = self._get_padding_rate(quantity)
        padding_cost = Decimal(quantity) * padding_rate

        # 8. Subtotal
        sub_total = total_setup_cost + total_content_cost + cutting_cost + padding_cost

        # 9. Profit margin
        profit_margin = self._get_profit_margin(float(sub_total))

        # 10-12. Apply margin and double GST
        total2 = (sub_total + (sub_total * profit_margin)) * Decimal('1.1')
        total_price = total2 * Decimal('1.1')
        total_price = total2 * Decimal('1.1')
        total_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        cost_per_item = total_price / Decimal(quantity)
        unit_price = cost_per_item

        breakdown = {
            'guilo_setup': guilo_setup,
            'impos_setup': impos_setup,
            'artwork_setup_cost': _a2,
            'total_setup_cost': total_setup_cost,
            'total_leave_sheets': total_leave_sheets,
            'content_click_cost': content_click_cost,
            'box_board_cost': box_board_c * Decimal(quantity),
            'total_content_cost': total_content_cost,
            'cutting_cost': cutting_cost,
            'padding_rate': padding_rate,
            'padding_cost': padding_cost,
            'subtotal': sub_total,
            'profit_margin_rate': profit_margin,
            'profit_amount': sub_total * profit_margin,
            'subtotal_with_margin': sub_total + (sub_total * profit_margin),
            'after_first_gst': total2,
            'total_price': total_price,
        }

        specifications = {
            'quantity': quantity,
            'artworks': artworks,
            'finish_size': finish_size,
            'finish_size_multiplier': float(finish_size_multiplier),
            'leaves_per_pad': leaves_per_pad,
            'print_type': print_type,
            'print_type_price': float(print_type_price),
            'stock_type': stock_type,
            'stock_type_price': float(stock_type_price),
        }

        return NotepadsA4ShopifyCalculatorQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            cost_per_item=cost_per_item,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    def _get_finish_size_multiplier(self, finish_size: str) -> Decimal:
        """Get finish size multiplier (F8.price in TXT - A4 uses F8 not F3)"""
        # A4 Portrait = 1.0 multiplier (full sheet size)
        if 'A4' in finish_size:
            return Decimal('1.0')
        return Decimal('1.0')  # Default
    
    def _get_leaves_per_pad_value(self, leaves_per_pad: int) -> Decimal:
        """Get leaves per pad value (F7.price in TXT - A4 uses F7 not F4)"""
        # A4 options: 25, 50, 100 (website confirmed - no 200 option available)
        leaves_map = {
            25: Decimal('12.5'),
            50: Decimal('25'),
            100: Decimal('50'),
        }
        return leaves_map.get(leaves_per_pad, Decimal('25'))
    
    def _get_print_type_price(self, print_type: str) -> Decimal:
        """Get print type price per sheet (F10.price in TXT - A4 uses F10 not F5)"""
        if 'Colour 2 sided' in print_type:
            return Decimal('0.096')
        elif 'Colour 1 sided' in print_type or 'Colour' in print_type:
            return Decimal('0.048')
        elif 'Black & White 2 sided' in print_type:
            return Decimal('0.02')
        elif 'Black & White 1 sided' in print_type or 'Black' in print_type:
            return Decimal('0.01')
        return Decimal('0.01')
    
    def _get_stock_type_price(self, stock_type: str) -> Decimal:
        """Get stock type price per sheet (F11.price in TXT - A4 uses F11 not F6)"""
        if 'Revive' in stock_type or 'Recycled' in stock_type:
            return Decimal('0.06')
        elif '100GSM' in stock_type:
            return Decimal('0.054')
        elif '90GSM' in stock_type:
            return Decimal('0.033')
        elif '80GSM' in stock_type:
            return Decimal('0.03')
        return Decimal('0.03')
    
    def _get_padding_rate(self, quantity: int) -> Decimal:
        """
        Get padding rate based on quantity tiers (TXT Lines 1118-1124)
        
        A4-specific: PREMIUM rates (HIGHEST of all 3 sizes)
        - 1-250: 0.3
        - 251-500: 0.3
        - 501-1000: 0.25
        - 1001-1500: 0.25
        - 1501-2000: 0.2
        - 2001-3000: 0.2
        - 3001+: 0.2
        """
        if quantity <= 250:
            return Decimal('0.3')
        elif quantity <= 500:
            return Decimal('0.3')
        elif quantity <= 1000:
            return Decimal('0.25')
        elif quantity <= 1500:
            return Decimal('0.25')
        elif quantity <= 2000:
            return Decimal('0.2')
        elif quantity <= 3000:
            return Decimal('0.2')
        else:
            return Decimal('0.2')
    
    def _get_profit_margin(self, subtotal: float) -> Decimal:
        """
        Get profit margin rate based on subtotal tiers
        
        13 tiers based on subtotal amount
        """
        if subtotal <= 500:
            return Decimal('0.8')
        elif subtotal <= 1000:
            return Decimal('0.8')
        elif subtotal <= 1500:
            return Decimal('0.8')
        elif subtotal <= 2000:
            return Decimal('0.75')
        elif subtotal <= 2500:
            return Decimal('0.72')
        elif subtotal <= 3000:
            return Decimal('0.72')
        elif subtotal <= 4000:
            return Decimal('0.65')
        elif subtotal <= 5000:
            return Decimal('0.55')
        elif subtotal <= 7500:
            return Decimal('0.52')
        elif subtotal <= 10000:
            return Decimal('0.47')
        elif subtotal <= 15000:
            return Decimal('0.42')
        elif subtotal <= 20000:
            return Decimal('0.41')
        else:
            return Decimal('0.41')
