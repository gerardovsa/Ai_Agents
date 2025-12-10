"""
Strut Cards A3 Shopify Calculator
Exact implementation of Shopify JavaScript formula for Strut Cards A3

Based on: Shopify_Strut_Cards_A3.json specification
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
config_dir = Path(__file__).parent.parent.parent / "config"
sys.path.insert(0, str(config_dir))
from config_manager import config_manager


@dataclass
class StrutCardsA3ShopifyCalculatorQuoteResult:
    """Result from Strut Cards A3 Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class StrutCardsA3ShopifyCalculator:
    """
    Strut Cards A3 Shopify Calculator - Exact Shopify JavaScript Implementation
    
    SHOPIFY-SPECIFIC CALCULATOR - SEPARATE FROM WOOCOMMERCE
    
    Features:
    - 4-field Shopify structure
    - Tiered padding rates (0 tiers)
    - Tiered profit margins (0 tiers)
    - Artwork setup costs
    - DOUBLE GST APPLICATION (Shopify-specific: Total * 1.1 * 1.1)
    """
    
    CONFIG_FILE = "Shopify_Strut_Cards_A3.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Strut Cards A3 Shopify calculator"""
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
    
    def calculate(self, **kwargs) -> StrutCardsA3ShopifyCalculatorQuoteResult:
        """
        Calculate Strut Cards A3 Shopify quote
        
        Args:
            **kwargs: Calculator parameters from JSON config
        
        Returns:
            StrutCardsA3ShopifyCalculatorQuoteResult with pricing details
        """
        quantity = int(kwargs.get('quantity', kwargs.get('qty', 100)))
        size = kwargs.get('size', '297x420')  # A3
        sides = kwargs.get('sides', 'Single')
        artworks = int(kwargs.get('artworks', 1))

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')

        try:
            w_str, h_str = size.lower().split('x')
            width_mm = Decimal(w_str)
            height_mm = Decimal(h_str)
            area_m2 = (width_mm * height_mm) / Decimal('1000000')
        except Exception:
            area_m2 = Decimal('0.125')

        material_rate = Decimal('3.50')  # card per m2 base
        print_cost_per_m2 = Decimal('6.00')
        sides_multiplier = Decimal('2') if 'double' in sides.lower() else Decimal('1')

        impos_setup = Decimal('20')
        extra_arts = Decimal('10')
        artwork_setup_cost = (Decimal(artworks) - Decimal(1)) * extra_arts if artworks > 1 else Decimal('0')

        material_cost = area_m2 * material_rate * Decimal(quantity)
        print_cost = area_m2 * print_cost_per_m2 * Decimal(quantity) * sides_multiplier
        cutting_and_finish = Decimal('0.80') * Decimal(quantity)

        biz_cost = impos_setup + artwork_setup_cost + material_cost + print_cost + cutting_and_finish

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
            'artwork_setup_cost': artwork_setup_cost,
            'material_cost': material_cost,
            'print_cost': print_cost,
            'cutting_and_finish': cutting_and_finish,
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
            'size_mm': f"{width_mm}x{height_mm}" if 'width_mm' in locals() else size,
            'sides': sides,
            'area_m2': float(area_m2)
        }

        return StrutCardsA3ShopifyCalculatorQuoteResult(
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
