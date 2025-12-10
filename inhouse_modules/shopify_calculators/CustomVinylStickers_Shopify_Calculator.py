"""
Custom Vinyl Stickers Shopify Calculator
Exact implementation of Shopify JavaScript formula for Custom Vinyl Stickers

Based on: c:/Users/gpoli/GIT/In_House_SQL/G_Folder/Quote_Calculator/shopify/Shopify_Custom_Vinyl_Stickers.json specification
Platform: Shopify (separate from WooCommerce calculators)
Fields: 10 fields (Shopify-specific structure)
Key Features: Tiered padding rates, profit margins, double GST application
"""

import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CustomVinylStickersShopifyCalculatorQuoteResult:
    """Result from Custom Vinyl Stickers Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class CustomVinylStickersShopifyCalculator:
    """
    Custom Vinyl Stickers Shopify Calculator - Exact Shopify JavaScript Implementation
    
    SHOPIFY-SPECIFIC CALCULATOR - SEPARATE FROM WOOCOMMERCE
    
    Features:
    - 10-field Shopify structure
    - Tiered padding rates (0 tiers)
    - Tiered profit margins (0 tiers)
    - Artwork setup costs
    - DOUBLE GST APPLICATION (Shopify-specific: Total * 1.1 * 1.1)
    """
    
    CONFIG_FILE = r"c:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator\shopify\Shopify_Custom_Vinyl_Stickers.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Custom Vinyl Stickers Shopify calculator"""
        if config_path:
            self.config = self._load_config(config_path)
        else:
            default_path = Path(__file__).parent.parent.parent / "In_House_SQL" / "G_Folder" / "Quote_Calculator" / "shopify" / self.CONFIG_FILE
            if default_path.exists():
                self.config = self._load_config(str(default_path))
            else:
                self.config = None
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def calculate(self, **kwargs) -> CustomVinylStickersShopifyCalculatorQuoteResult:
        """
        Calculate Custom Vinyl Stickers Shopify quote
        
        Args:
            **kwargs: Calculator parameters from JSON config
        
        Returns:
            CustomVinylStickersShopifyCalculatorQuoteResult with pricing details
        """
        quantity = int(kwargs.get('quantity', kwargs.get('qty', 100)))
        width = Decimal(kwargs.get('width_mm', kwargs.get('width', 100)))
        height = Decimal(kwargs.get('height_mm', kwargs.get('height', 100)))
        finish = kwargs.get('finish', 'Gloss')

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')

        area_m2 = (width * height) / Decimal('1000000')

        impos_setup = Decimal('35')
        vinyl_cost_per_m2 = Decimal('25.00') if 'gloss' in finish.lower() else Decimal('22.00')
        print_cost_per_m2 = Decimal('10.00')
        cutting_cost_per_item = Decimal('0.40')

        material_cost = area_m2 * vinyl_cost_per_m2 * Decimal(quantity)
        print_cost = area_m2 * print_cost_per_m2 * Decimal(quantity)
        cutting_cost = cutting_cost_per_item * Decimal(quantity)

        biz_cost = impos_setup + material_cost + print_cost + cutting_cost

        profit_margin_rate = self._get_profit_margin(float(biz_cost))
        profit_amount = biz_cost * profit_margin_rate
        sub_total = biz_cost + profit_amount

        GST_RATE = Decimal('1.10')
        subtotal_with_increase = sub_total
        total_price = (subtotal_with_increase * GST_RATE) * GST_RATE
        total_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        unit_price = total_price / Decimal(quantity)

        breakdown = {
            'impos_setup': impos_setup,
            'material_cost': material_cost,
            'print_cost': print_cost,
            'cutting_cost': cutting_cost,
            'biz_cost': biz_cost,
            'profit_margin_rate': Decimal(profit_margin_rate),
            'profit_amount': profit_amount,
            'subtotal': sub_total,
            'total_price': total_price,
        }

        specifications = {
            'quantity': quantity,
            'width_mm': float(width),
            'height_mm': float(height),
            'finish': finish
        }

        return CustomVinylStickersShopifyCalculatorQuoteResult(
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
        """Get profit margin (no tiers defined)"""
        return Decimal('0.50')
