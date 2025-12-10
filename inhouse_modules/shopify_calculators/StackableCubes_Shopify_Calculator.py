"""
Stackable Cubes Shopify Calculator
Exact implementation of Shopify JavaScript formula for Stackable Cubes

Based on: Shopify_Stackable_Cubes.json specification
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
class StackableCubesShopifyCalculatorQuoteResult:
    """Result from Stackable Cubes Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class StackableCubesShopifyCalculator:
    """
    Stackable Cubes Shopify Calculator - Exact Shopify JavaScript Implementation
    
    SHOPIFY-SPECIFIC CALCULATOR - SEPARATE FROM WOOCOMMERCE
    
    Features:
    - 4-field Shopify structure
    - Tiered padding rates (0 tiers)
    - Tiered profit margins (0 tiers)
    - Artwork setup costs
    - DOUBLE GST APPLICATION (Shopify-specific: Total * 1.1 * 1.1)
    """
    
    CONFIG_FILE = "Shopify_Stackable_Cubes.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Stackable Cubes Shopify calculator"""
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
    
    def calculate(self, **kwargs) -> StackableCubesShopifyCalculatorQuoteResult:
        """
        Calculate Stackable Cubes Shopify quote
        
        Args:
            **kwargs: Calculator parameters from JSON config
        
        Returns:
            StackableCubesShopifyCalculatorQuoteResult with pricing details
        """
        quantity = int(kwargs.get('quantity', kwargs.get('qty', 10)))
        size = kwargs.get('size', '300')  # mm (edge)
        material = kwargs.get('material', 'Corrugated')

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')

        edge_mm = Decimal(size)
        face_area_m2 = (edge_mm * edge_mm) / Decimal('1000000')

        # material rate per m2
        material_map = {'corrugated': Decimal('12.00'), 'card': Decimal('8.00')}
        material_rate = material_map.get(material.lower(), Decimal('12.00'))

        material_cost = face_area_m2 * material_rate * Decimal(quantity) * Decimal('6')  # 6 faces
        assembly_cost = Decimal('2.50') * Decimal(quantity)
        packaging = Decimal('1.00') * Decimal(quantity)

        impos_setup = Decimal('25')

        biz_cost = impos_setup + material_cost + assembly_cost + packaging

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
            'assembly_cost': assembly_cost,
            'packaging': packaging,
            'biz_cost': biz_cost,
            'profit_margin_rate': Decimal(profit_margin_rate),
            'profit_amount': profit_amount,
            'subtotal': sub_total,
            'total_price': total_price,
        }

        specifications = {
            'quantity': quantity,
            'edge_mm': float(edge_mm),
            'material': material
        }

        return StackableCubesShopifyCalculatorQuoteResult(
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
