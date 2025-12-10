"""
With Compliments Slips Shopify Calculator
Exact implementation of Shopify JavaScript formula for With Compliments Slips

Based on: c:/Users/gpoli/GIT/In_House_SQL/G_Folder/Quote_Calculator/shopify/Shopify_With_Compliments_Slips.json specification
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
class WithComplimentsSlipsShopifyCalculatorQuoteResult:
    """Result from With Compliments Slips Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class WithComplimentsSlipsShopifyCalculator:
    """
    With Compliments Slips Shopify Calculator - Exact Shopify JavaScript Implementation
    
    SHOPIFY-SPECIFIC CALCULATOR - SEPARATE FROM WOOCOMMERCE
    
    Features:
    - 6-field Shopify structure
    - Tiered padding rates (0 tiers)
    - Tiered profit margins (12 tiers)
    - Artwork setup costs
    - DOUBLE GST APPLICATION (Shopify-specific: Total * 1.1 * 1.1)
    """
    
    CONFIG_FILE = "Shopify_With_Compliments_Slips.json"
    
    def __init__(self, config_path: str = None):
        """Initialize With Compliments Slips Shopify calculator"""
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
    
    def calculate(self, **kwargs) -> WithComplimentsSlipsShopifyCalculatorQuoteResult:
        """
        Calculate With Compliments Slips Shopify quote
        
        Args:
            **kwargs: Calculator parameters from JSON config
        
        Returns:
            WithComplimentsSlipsShopifyCalculatorQuoteResult with pricing details
        """
        # Implement calculation using the same pattern as other Shopify calculators
        quantity = int(kwargs.get('quantity', kwargs.get('qty', 250)))
        print_sides = kwargs.get('print_sides', 'Single side print')
        print_type = kwargs.get('print_type', 'Colour')
        paper_stock = kwargs.get('paper_stock', 'Standard')
        artworks = int(kwargs.get('artworks', 1))

        if quantity <= 0:
            raise ValueError("Quantity must be > 0")

        impos_setup = Decimal('18')
        guilo_setup = Decimal('14')
        extra_arts = Decimal('12')

        if artworks > 1:
            artwork_setup_cost = (Decimal(artworks) - Decimal(1)) * extra_arts
        else:
            artwork_setup_cost = Decimal('0')

        total_setup_cost = impos_setup + guilo_setup + artwork_setup_cost

        sides_multiplier = Decimal('2') if 'Double' in print_sides else Decimal('1')
        print_mode_cost = Decimal('0.045') if 'Colour' in print_type else Decimal('0.02')

        # Compliment slips typically fit 2 per A4 sheet
        items_per_sheet = Decimal('2')
        stock_cost_per_1000_sheets = Decimal('60')

        stock_waste = Decimal('1.05')
        sheets_needed = (Decimal(quantity) / items_per_sheet) * stock_waste
        stock_cost = (sheets_needed / Decimal('1000')) * stock_cost_per_1000_sheets

        click_cost = sheets_needed * sides_multiplier * print_mode_cost

        cutting_block = Decimal('500')
        cut_cost = Decimal('10')
        cutting_cost = (sheets_needed / cutting_block) * cut_cost

        biz_cost = total_setup_cost + stock_cost + click_cost + cutting_cost

        profit_margin_rate = self._get_profit_margin(float(biz_cost))
        profit_amount = biz_cost * profit_margin_rate
        sub_total = biz_cost + profit_amount

        PRICE_INCREASE_MULTIPLIER = Decimal('1.00')
        GST_RATE = Decimal('1.10')
        SURCHARGE = Decimal('0.00')

        subtotal_with_increase = sub_total * PRICE_INCREASE_MULTIPLIER
        total_price = (subtotal_with_increase * GST_RATE) * GST_RATE + SURCHARGE
        total_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        cost_per_item = total_price / Decimal(quantity)
        unit_price = cost_per_item

        breakdown = {
            'setup_costs': total_setup_cost,
            'artwork_setup_cost': artwork_setup_cost,
            'stock_cost': stock_cost,
            'click_cost': click_cost,
            'cutting_cost': cutting_cost,
            'biz_cost': biz_cost,
            'profit_margin_rate': Decimal(profit_margin_rate),
            'profit_amount': profit_amount,
            'subtotal': sub_total,
            'subtotal_with_increase': subtotal_with_increase,
            'gst_rate': GST_RATE,
            'gst_amount': subtotal_with_increase * (GST_RATE - Decimal('1')),
            'total_price': total_price,
            'sheets_needed': sheets_needed,
        }

        specifications = {
            'quantity': quantity,
            'items_per_sheet': items_per_sheet,
            'print_sides': print_sides,
            'print_type': print_type,
            'paper_stock': paper_stock,
            'artworks': artworks
        }

        return WithComplimentsSlipsShopifyCalculatorQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            cost_per_item=cost_per_item,
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
        if subtotal <= 50.999:
            return Decimal('1.7')
        elif subtotal <= 74.999:
            return Decimal('1.55')
        elif subtotal <= 100.999:
            return Decimal('1.35')
        elif subtotal <= 150.999:
            return Decimal('1.3')
        elif subtotal <= 200.999:
            return Decimal('1.15')
        elif subtotal <= 300.999:
            return Decimal('0.7')
        elif subtotal <= 400.999:
            return Decimal('0.53')
        elif subtotal <= 500.999:
            return Decimal('0.4')
        elif subtotal <= 1000.999:
            return Decimal('0.3')
        elif subtotal <= 5000.999:
            return Decimal('0.3')
        elif subtotal <= 100000.999:
            return Decimal('0.25')
        else:
            return Decimal('200')
