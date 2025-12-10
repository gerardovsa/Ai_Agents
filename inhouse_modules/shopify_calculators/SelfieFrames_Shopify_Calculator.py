"""
Selfie Frames Shopify Calculator
Exact implementation of Shopify JavaScript formula for Selfie Frames

Based on: Shopify_Selfie_Frames.json specification
Platform: Shopify (separate from WooCommerce calculators)
Fields: 3 fields (Shopify-specific structure)
Key Features: Tiered padding rates, profit margins, double GST application
"""

import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import sys

# Import config manager
config_dir = Path(__file__).parent.parent.parent / "config"
sys.path.insert(0, str(config_dir))
from config_manager import config_manager


@dataclass
class SelfieFramesShopifyCalculatorQuoteResult:
    """Result from Selfie Frames Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class SelfieFramesShopifyCalculator:
    """
    Selfie Frames Shopify Calculator - Exact Shopify JavaScript Implementation
    
    SHOPIFY-SPECIFIC CALCULATOR - SEPARATE FROM WOOCOMMERCE
    
    Features:
    - 3-field Shopify structure
    - Tiered padding rates (0 tiers)
    - Tiered profit margins (0 tiers)
    - Artwork setup costs
    - DOUBLE GST APPLICATION (Shopify-specific: Total * 1.1 * 1.1)
    """
    
    CONFIG_FILE = "Shopify_Selfie_Frames.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Selfie Frames Shopify calculator"""
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
    
    def calculate(self, **kwargs) -> SelfieFramesShopifyCalculatorQuoteResult:
        """
        Calculate Selfie Frames Shopify quote
        
        Args:
            **kwargs: Calculator parameters from JSON config
        
        Returns:
            SelfieFramesShopifyCalculatorQuoteResult with pricing details
        """
        quantity = int(kwargs.get('quantity', kwargs.get('qty', 10)))
        width = Decimal(kwargs.get('width_mm', kwargs.get('width', 600)))
        height = Decimal(kwargs.get('height_mm', kwargs.get('height', 600)))
        material = kwargs.get('material', 'Foam Core')
        artworks = int(kwargs.get('artworks', 1))

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')

        area_m2 = (width * height) / Decimal('1000000')
        material_map = {'foam core': Decimal('18.00'), 'card': Decimal('8.00')}
        material_rate = material_map.get(material.lower(), Decimal('18.00'))

        impos_setup = Decimal('28')
        extra_arts = Decimal('15')
        artwork_setup_cost = (Decimal(artworks) - Decimal(1)) * extra_arts if artworks > 1 else Decimal('0')

        material_cost = area_m2 * material_rate * Decimal(quantity)
        print_cost = area_m2 * Decimal('10.00') * Decimal(quantity)
        cut_and_finish = Decimal('2.50') * Decimal(quantity)

        biz_cost = impos_setup + artwork_setup_cost + material_cost + print_cost + cut_and_finish

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
            'artwork_setup_cost': artwork_setup_cost,
            'material_cost': material_cost,
            'print_cost': print_cost,
            'cut_and_finish': cut_and_finish,
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

        return SelfieFramesShopifyCalculatorQuoteResult(
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
