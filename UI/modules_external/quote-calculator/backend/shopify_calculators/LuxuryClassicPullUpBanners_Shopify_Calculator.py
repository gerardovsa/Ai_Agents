"""
Luxury Classic Pull Up Banners Shopify Calculator
Exact implementation of Shopify JavaScript formula for Luxury Classic Pull Up Banners

Based on: c:/Users/gpoli/GIT/In_House_SQL/G_Folder/Quote_Calculator/shopify/Shopify_Luxury_Classic_Pull_Up_Banners.json specification
Platform: Shopify (separate from WooCommerce calculators)
Fields: 4 fields (Shopify-specific structure)
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
class LuxuryClassicPullUpBannersShopifyCalculatorQuoteResult:
    """Result from Luxury Classic Pull Up Banners Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class LuxuryClassicPullUpBannersShopifyCalculator:
    """
    Luxury Classic Pull Up Banners Shopify Calculator - Exact Shopify JavaScript Implementation
    
    SHOPIFY-SPECIFIC CALCULATOR - SEPARATE FROM WOOCOMMERCE
    
    Features:
    - 4-field Shopify structure
    - Tiered padding rates (0 tiers)
    - Tiered profit margins (0 tiers)
    - Artwork setup costs
    - DOUBLE GST APPLICATION (Shopify-specific: Total * 1.1 * 1.1)
    """
    
    CONFIG_FILE = "Shopify_Luxury_Classic_Pull_Up_Banners.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Luxury Classic Pull Up Banners Shopify calculator"""
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
    
    def calculate(self, **kwargs) -> LuxuryClassicPullUpBannersShopifyCalculatorQuoteResult:
        """
        Calculate Luxury Classic Pull Up Banners Shopify quote
        
        Args:
            **kwargs: Calculator parameters from JSON config
        
        Returns:
            LuxuryClassicPullUpBannersShopifyCalculatorQuoteResult with pricing details
        """
        quantity = int(kwargs.get('quantity', kwargs.get('qty', 5)))
        width = Decimal(kwargs.get('width_mm', kwargs.get('width', 850)))
        height = Decimal(kwargs.get('height_mm', kwargs.get('height', 2000)))
        material = kwargs.get('material', 'Premium Vinyl')

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')

        area_m2 = (width * height) / Decimal('1000000')
        material_rate = Decimal('28.00') if 'premium' in material.lower() else Decimal('18.00')

        impos_setup = Decimal('75')
        print_cost = area_m2 * Decimal('18.00') * Decimal(quantity)
        hardware_cost = Decimal('75.00') * Decimal(quantity)

        biz_cost = impos_setup + print_cost + hardware_cost

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
            'print_cost': print_cost,
            'hardware_cost': hardware_cost,
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
            'material': material
        }

        return LuxuryClassicPullUpBannersShopifyCalculatorQuoteResult(
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
