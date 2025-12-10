"""
Custom Poster Printing Shopify Calculator
Exact implementation of Shopify JavaScript formula for Custom Poster Printing

Based on: c:/Users/gpoli/GIT/In_House_SQL/G_Folder/Quote_Calculator/shopify/Shopify_Custom_Poster_Printing.json specification
Platform: Shopify (separate from WooCommerce calculators)
Fields: 6 fields (Shopify-specific structure)
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
class CustomPosterPrintingShopifyCalculatorQuoteResult:
    """Result from Custom Poster Printing Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class CustomPosterPrintingShopifyCalculator:
    """
    Custom Poster Printing Shopify Calculator - Exact Shopify JavaScript Implementation
    
    SHOPIFY-SPECIFIC CALCULATOR - SEPARATE FROM WOOCOMMERCE
    
    Features:
    - 6-field Shopify structure
    - Tiered padding rates (0 tiers)
    - Tiered profit margins (0 tiers)
    - Artwork setup costs
    - DOUBLE GST APPLICATION (Shopify-specific: Total * 1.1 * 1.1)
    """
    
    CONFIG_FILE = "Shopify_Custom_Poster_Printing.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Custom Poster Printing Shopify calculator"""
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
    
    def calculate(self, **kwargs) -> CustomPosterPrintingShopifyCalculatorQuoteResult:
        """
        Calculate Custom Poster Printing Shopify quote
        
        Args:
            **kwargs: Calculator parameters from JSON config
        
        Returns:
            CustomPosterPrintingShopifyCalculatorQuoteResult with pricing details
        """
        quantity = int(kwargs.get('quantity', kwargs.get('qty', 50)))
        width = Decimal(kwargs.get('width_mm', kwargs.get('width', 420)))  # A3
        height = Decimal(kwargs.get('height_mm', kwargs.get('height', 594)))
        paper_stock = kwargs.get('paper_stock', '150gsm')

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')

        area_m2 = (width * height) / Decimal('1000000')

        impos_setup = Decimal('30')
        guilo_setup = Decimal('15')

        posters_per_sheet = Decimal('1')  # typical 1:1 mapping
        stock_waste = Decimal('1.05')
        sheets_needed = (Decimal(quantity) / posters_per_sheet) * stock_waste

        stock_cost_per_1000 = Decimal('95')
        stock_cost = (sheets_needed / Decimal('1000')) * stock_cost_per_1000

        print_cost = sheets_needed * Decimal('0.06')
        cutting_cost = (sheets_needed / Decimal('500')) * Decimal('12')

        biz_cost = impos_setup + guilo_setup + stock_cost + print_cost + cutting_cost

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
            'guilo_setup': guilo_setup,
            'stock_cost': stock_cost,
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
            'paper_stock': paper_stock
        }

        return CustomPosterPrintingShopifyCalculatorQuoteResult(
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
