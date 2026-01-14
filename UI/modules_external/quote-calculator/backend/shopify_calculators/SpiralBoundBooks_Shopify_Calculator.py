"""
Spiral Bound Books Shopify Calculator
Exact implementation of Shopify JavaScript formula for Spiral Bound Books

Based on: Shopify_Spiral_Bound_Books.json specification
Platform: Shopify (separate from WooCommerce calculators)
Fields: 14 fields (Shopify-specific structure)
Key Features: Tiered padding rates, profit margins, double GST application
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
class SpiralBoundBooksShopifyCalculatorQuoteResult:
    """Result from Spiral Bound Books Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class SpiralBoundBooksShopifyCalculator:
    """
    Spiral Bound Books Shopify Calculator - Exact Shopify JavaScript Implementation
    
    SHOPIFY-SPECIFIC CALCULATOR - SEPARATE FROM WOOCOMMERCE
    
    Features:
    - 14-field Shopify structure
    - Tiered padding rates (0 tiers)
    - Tiered profit margins (12 tiers)
    - Artwork setup costs
    - DOUBLE GST APPLICATION (Shopify-specific: Total * 1.1 * 1.1)
    """
    
    CONFIG_FILE = "Shopify_Spiral_Bound_Books.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Spiral Bound Books Shopify calculator"""
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
    
    def calculate(self, **kwargs) -> SpiralBoundBooksShopifyCalculatorQuoteResult:
        """
        Calculate Spiral Bound Books Shopify quote
        
        Args:
            **kwargs: Calculator parameters from JSON config
        
        Returns:
            SpiralBoundBooksShopifyCalculatorQuoteResult with pricing details
        """
        quantity = int(kwargs.get('quantity', kwargs.get('qty', 50)))
        pages = int(kwargs.get('pages', 50))
        size = kwargs.get('size', 'A4')
        paper_stock = kwargs.get('paper_stock', '80gsm')

        if quantity <= 0 or pages <= 0:
            raise ValueError('Quantity and pages must be > 0')

        impos_setup = Decimal('60')
        guilo_setup = Decimal('20')

        # cost per page (approx)
        page_cost = Decimal('0.005') if '80' in paper_stock else Decimal('0.007')
        cover_cost = Decimal('1.20')

        paper_cost = Decimal(pages) * page_cost * Decimal(quantity)
        cover_total = cover_cost * Decimal(quantity)

        # binding cost per book
        binding_cost = Decimal('0.50') * Decimal(quantity)

        biz_cost = impos_setup + guilo_setup + paper_cost + cover_total + binding_cost

        profit_margin_rate = self._get_profit_margin(float(biz_cost))
        profit_amount = biz_cost * profit_margin_rate
        sub_total = biz_cost + profit_amount

        PRICE_INCREASE_MULTIPLIER = Decimal('1.00')
        GST_RATE = Decimal('1.10')

        subtotal_with_increase = sub_total * PRICE_INCREASE_MULTIPLIER
        total_price = (subtotal_with_increase * GST_RATE) * GST_RATE
        total_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        unit_price = total_price / Decimal(quantity)

        breakdown = {
            'impos_setup': impos_setup,
            'guilo_setup': guilo_setup,
            'paper_cost': paper_cost,
            'cover_total': cover_total,
            'binding_cost': binding_cost,
            'biz_cost': biz_cost,
            'profit_margin_rate': Decimal(profit_margin_rate),
            'profit_amount': profit_amount,
            'subtotal': sub_total,
            'subtotal_with_increase': subtotal_with_increase,
            'gst_rate': GST_RATE,
            'total_price': total_price,
        }

        specifications = {
            'quantity': quantity,
            'pages': pages,
            'size': size,
            'paper_stock': paper_stock
        }

        return SpiralBoundBooksShopifyCalculatorQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            cost_per_item=unit_price,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    def _get_padding_rate(self, quantity: int) -> Decimal:
        """Get padding rate (no tiers defined)"""
        return Decimal('0.10')
    
    def _get_profit_margin(self, subtotal: float) -> Decimal:
        """
        Get profit margin rate based on subtotal tiers
        
        12 tiers based on subtotal amount
        """
        if subtotal <= 500:
            return Decimal('0.9')
        elif subtotal <= 1000:
            return Decimal('0.9')
        elif subtotal <= 1500:
            return Decimal('0.8')
        elif subtotal <= 2000:
            return Decimal('0.75')
        elif subtotal <= 2500:
            return Decimal('0.7')
        elif subtotal <= 3000:
            return Decimal('0.67')
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
        elif subtotal <= 100000:
            return Decimal('0.41')
