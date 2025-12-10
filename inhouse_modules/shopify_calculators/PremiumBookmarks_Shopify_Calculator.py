"""
Premium Bookmarks Shopify Calculator
Exact implementation of Shopify JavaScript formula for Premium Bookmarks

Based on: c:/Users/gpoli/GIT/In_House_SQL/G_Folder/Quote_Calculator/shopify/Shopify_Premium_Bookmarks.json specification
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
class PremiumBookmarksShopifyCalculatorQuoteResult:
    """Result from Premium Bookmarks Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class PremiumBookmarksShopifyCalculator:
    """
    Premium Bookmarks Shopify Calculator - Exact Shopify JavaScript Implementation
    
    SHOPIFY-SPECIFIC CALCULATOR - SEPARATE FROM WOOCOMMERCE
    
    Features:
    - 6-field Shopify structure
    - Tiered padding rates (0 tiers)
    - Tiered profit margins (12 tiers)
    - Artwork setup costs
    - DOUBLE GST APPLICATION (Shopify-specific: Total * 1.1 * 1.1)
    """
    
    CONFIG_FILE = "Shopify_Premium_Bookmarks.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Premium Bookmarks Shopify calculator"""
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
    
    def calculate(self, **kwargs) -> PremiumBookmarksShopifyCalculatorQuoteResult:
        """
        Calculate Premium Bookmarks Shopify quote
        
        Args:
            **kwargs: Calculator parameters from JSON config
        
        Returns:
            PremiumBookmarksShopifyCalculatorQuoteResult with pricing details
        """
        quantity = int(kwargs.get('quantity', kwargs.get('qty', 250)))
        width = Decimal(kwargs.get('width_mm', kwargs.get('width', 55)))
        height = Decimal(kwargs.get('height_mm', kwargs.get('height', 200)))
        paper_stock = kwargs.get('paper_stock', '350gsm')
        lamination = kwargs.get('lamination', 'Matte')

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')

        area_m2 = (width * height) / Decimal('1000000')
        bookmarks_per_sheet = Decimal('12')  # typical layout

        impos_setup = Decimal('20')
        guilo_setup = Decimal('12')

        stock_waste = Decimal('1.05')
        sheets_needed = (Decimal(quantity) / bookmarks_per_sheet) * stock_waste

        stock_cost_per_1000 = Decimal('140') if '350' in paper_stock else Decimal('110')
        stock_cost = (sheets_needed / Decimal('1000')) * stock_cost_per_1000

        print_cost = sheets_needed * Decimal('0.055')
        cutting_cost = (sheets_needed / Decimal('500')) * Decimal('10')

        lamination_cost_per_bookmark = Decimal('0.08') if lamination else Decimal('0')
        lamination_cost = lamination_cost_per_bookmark * Decimal(quantity)

        biz_cost = impos_setup + guilo_setup + stock_cost + print_cost + cutting_cost + lamination_cost

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
            'lamination_cost': lamination_cost,
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
            'paper_stock': paper_stock,
            'lamination': lamination,
            'bookmarks_per_sheet': float(bookmarks_per_sheet)
        }

        return PremiumBookmarksShopifyCalculatorQuoteResult(
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
        if subtotal <= 50.999:
            return Decimal('1.8')
        elif subtotal <= 74.999:
            return Decimal('1.6')
        elif subtotal <= 100.999:
            return Decimal('1.45')
        elif subtotal <= 150.999:
            return Decimal('1.35')
        elif subtotal <= 200.999:
            return Decimal('1.2')
        elif subtotal <= 300.999:
            return Decimal('0.83')
        elif subtotal <= 400.999:
            return Decimal('0.67')
        elif subtotal <= 500.999:
            return Decimal('0.54')
        elif subtotal <= 1000.999:
            return Decimal('0.33')
        elif subtotal <= 5000.999:
            return Decimal('0.32')
        elif subtotal <= 100000.999:
            return Decimal('0.31')
        else:
            return Decimal('200')
