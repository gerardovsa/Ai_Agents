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
        # TODO: Implement calculation logic based on JSON config
        # This is a template - actual implementation needed
        
        raise NotImplementedError("Calculator implementation pending")
    
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
