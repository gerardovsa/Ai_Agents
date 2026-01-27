"""
Notepads A6 Shopify Calculator
Exact implementation of Shopify JavaScript formula for Notepads A6

Based on: SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt Lines 538-1100
Platform: Shopify (separate from WooCommerce calculators)
Fields: F1 (Quantity), F2 (Artworks), F3 (Finish Size), F4 (Leaves Per Pad), F5 (Print Type), F6 (Stock Type)
Key Features: Lower padding rates (0.1/0.05/0.03), lower box board cost (0.03), A6 size multiplier (0.25)

REWRITTEN: January 24, 2026 - Complete rewrite to match exact TXT formula
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
class NotepadsA6ShopifyCalculatorQuoteResult:
    """Result from Notepads A6 Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class NotepadsA6ShopifyCalculator:
    """
    Notepads A6 Shopify Calculator - Exact Shopify JavaScript Implementation
    
    EXACT TXT FORMULA IMPLEMENTATION (Lines 540-584)
    
    Differences from A5:
    - Box board cost: 0.03 (vs 0.07)
    - Padding rates: 0.1/0.05/0.03 (vs 0.2/0.15/0.1)
    - Finish size multiplier: 0.25 (vs 0.5)
    - Leaves options: 10, 15, 25, 50, 100 (vs 25, 50, 100)
    """
    
    CONFIG_FILE = "Shopify_Notepads_A6.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Notepads A6 Shopify calculator"""
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
    
    def calculate(self, **kwargs) -> NotepadsA6ShopifyCalculatorQuoteResult:
        """
        Calculate Notepads A6 Shopify quote using EXACT TXT FORMULA
        
        Args:
            quantity: Number of notepads
            artworks: Number of artworks (first free, $15 each additional)
            finish_size: Size option (A6 Portrait = 0.25 multiplier)
            leaves_per_pad: Number of leaves (10/15/25/50/100)
            print_type: Print type with price per sheet
            stock_type: Stock type with price per sheet
        
        Returns:
            NotepadsA6ShopifyCalculatorQuoteResult with pricing details
        """
        quantity = int(kwargs.get('quantity', kwargs.get('F1', 100)))
        artworks = int(kwargs.get('artworks', kwargs.get('F2', 1)))
        finish_size = kwargs.get('finish_size', 'A6 Portrait')
        leaves_per_pad = kwargs.get('leaves_per_pad', 50)
        print_type = kwargs.get('print_type', 'Black & White 1 sided')
        stock_type = kwargs.get('stock_type', 'Uncoated Bond 80GSM')

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')

        # Constants from TXT (same as A5 except boxBoardC)
        guilo_setup = Decimal('12')
        impos_setup = Decimal('15')
        stock_waste = Decimal('1.05')
        extra_arts = Decimal('15')
        cutting_blk = Decimal('500')
        cut_cost = Decimal('11')
        box_board_c = Decimal('0.03')  # A6-specific: Lower than A5
        
        # Get field prices
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

        # 7. Padding cost (A6-specific lower rates)
        padding_rate = self._get_padding_rate(quantity)
        padding_cost = Decimal(quantity) * padding_rate

        # 8. Subtotal
        sub_total = total_setup_cost + total_content_cost + cutting_cost + padding_cost

        # 9. Profit margin
        profit_margin = self._get_profit_margin(float(sub_total))

        # 10-12. Apply margin and double GST
        total2 = (sub_total + (sub_total * profit_margin)) * Decimal('1.1')
        total_price = total2 * Decimal('1.1')
        total_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        cost_per_item = total_price / Decimal(quantity)
        unit_price = cost_per_item

        # 10-12. Apply margin and double GST
        total2 = (sub_total + (sub_total * profit_margin)) * Decimal('1.1')
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

        return NotepadsA6ShopifyCalculatorQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            cost_per_item=cost_per_item,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    def _get_finish_size_multiplier(self, finish_size: str) -> Decimal:
        """Get finish size multiplier (F3.price in TXT)"""
        # A6 Portrait = 0.25 multiplier (smaller than A5)
        if 'A6' in finish_size:
            return Decimal('0.25')
        return Decimal('0.25')  # Default
    
    def _get_leaves_per_pad_value(self, leaves_per_pad: int) -> Decimal:
        """Get leaves per pad value (F4.price in TXT)"""
        # A6 has more options: 10, 15, 25, 50, 100
        leaves_map = {
            10: Decimal('5'),
            15: Decimal('7.5'),
            25: Decimal('12.5'),
            50: Decimal('25'),
            100: Decimal('50'),
        }
        return leaves_map.get(leaves_per_pad, Decimal('25'))
    
    def _get_print_type_price(self, print_type: str) -> Decimal:
        """Get print type price per sheet (F5.price in TXT)"""
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
        """Get stock type price per sheet (F6.price in TXT)"""
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
        Get padding rate based on quantity tiers (TXT Lines 558-564)
        
        A6-specific: LOWER rates than A5
        - 1-250: 0.1
        - 251-500: 0.1
        - 501-1000: 0.05
        - 1001-1500: 0.05
        - 1501-2000: 0.03
        - 2001-3000: 0.03
        - 3001+: 0.03
        """
        if quantity <= 250:
            return Decimal('0.1')
        elif quantity <= 500:
            return Decimal('0.1')
        elif quantity <= 1000:
            return Decimal('0.05')
        elif quantity <= 1500:
            return Decimal('0.05')
        elif quantity <= 2000:
            return Decimal('0.03')
        elif quantity <= 3000:
            return Decimal('0.03')
        else:
            return Decimal('0.03')
    
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
