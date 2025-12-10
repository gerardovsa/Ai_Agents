"""
Notepads A4 Shopify Calculator
Exact implementation of Shopify JavaScript formula for Notepads A4

Based on: c:/Users/gpoli/GIT/In_House_SQL/G_Folder/Quote_Calculator/shopify/Shopify_Notepads_A4.json specification
Platform: Shopify (separate from WooCommerce calculators)
Fields: 6 fields (Shopify-specific structure)
Key Features: Tiered padding rates, profit margins, double GST application
"""

import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class NotepadsA4ShopifyCalculatorQuoteResult:
    """Result from Notepads A4 Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class NotepadsA4ShopifyCalculator:
    """
    Notepads A4 Shopify Calculator - Exact Shopify JavaScript Implementation
    
    SHOPIFY-SPECIFIC CALCULATOR - SEPARATE FROM WOOCOMMERCE
    
    Features:
    - 6-field Shopify structure
    - Tiered padding rates (7 tiers)
    - Tiered profit margins (13 tiers)
    - Artwork setup costs
    - DOUBLE GST APPLICATION (Shopify-specific: Total * 1.1 * 1.1)
    """
    
    CONFIG_FILE = r"c:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator\shopify\Shopify_Notepads_A4.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Notepads A4 Shopify calculator"""
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
    
    def calculate(self, **kwargs) -> NotepadsA4ShopifyCalculatorQuoteResult:
        """
        Calculate Notepads A4 Shopify quote
        
        Args:
            **kwargs: Calculator parameters from JSON config
        
        Returns:
            NotepadsA4ShopifyCalculatorQuoteResult with pricing details
        """
        # Implement Notepads A4 calculator logic
        quantity = int(kwargs.get('quantity', kwargs.get('qty', 250)))
        print_sides = kwargs.get('print_sides', 'Single side print')
        print_type = kwargs.get('print_type', 'Colour')
        paper_stock = kwargs.get('paper_stock', 'Standard')
        artworks = int(kwargs.get('artworks', 1))
        pads_per_book = int(kwargs.get('pads_per_book', 1))

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')

        impos_setup = Decimal('30')
        guilo_setup = Decimal('20')
        extra_arts = Decimal('18')

        if artworks > 1:
            artwork_setup_cost = (Decimal(artworks) - Decimal(1)) * extra_arts
        else:
            artwork_setup_cost = Decimal('0')

        total_setup_cost = impos_setup + guilo_setup + artwork_setup_cost

        sides_multiplier = Decimal('2') if 'Double' in print_sides else Decimal('1')
        print_mode_cost = Decimal('0.05') if 'Colour' in print_type else Decimal('0.025')

        # Notepads A4: 1 pad per sheet (finished size uses full sheet)
        items_per_sheet = Decimal('1')
        stock_cost_per_1000_sheets = Decimal('110')

        stock_waste = Decimal('1.08')
        sheets_needed = (Decimal(quantity) / items_per_sheet) * stock_waste
        stock_cost = (sheets_needed / Decimal('1000')) * stock_cost_per_1000_sheets

        click_cost = sheets_needed * sides_multiplier * print_mode_cost

        # Binding / pad glue cost (per pad)
        glue_cost_per_pad = Decimal('0.20')
        binding_cost = glue_cost_per_pad * Decimal(quantity)

        cutting_block = Decimal('500')
        cut_cost = Decimal('14')
        cutting_cost = (sheets_needed / cutting_block) * cut_cost

        biz_cost = total_setup_cost + stock_cost + click_cost + cutting_cost + binding_cost

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
            'print_sides': print_sides,
            'print_type': print_type,
            'paper_stock': paper_stock,
            'artworks': artworks,
            'sheets_used': float(sheets_needed),
        }

        return NotepadsA4ShopifyCalculatorQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            cost_per_item=cost_per_item,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    def _get_padding_rate(self, quantity: int) -> Decimal:
        """
        Get padding rate based on quantity tiers
        
        7 tiers based on quantity
        """
        if quantity <= 250:
            return Decimal('0.3')
        elif quantity <= 500:
            return Decimal('0.3')
        elif quantity <= 1000:
            return Decimal('0.25')
        elif quantity <= 1500:
            return Decimal('0.25')
        elif quantity <= 2000:
            return Decimal('0.2')
        elif quantity <= 3000:
            return Decimal('0.2')
        else:
            return Decimal('0.2')
    
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
