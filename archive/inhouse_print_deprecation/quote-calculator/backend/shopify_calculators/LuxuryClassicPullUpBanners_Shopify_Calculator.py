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
        
        EXACT IMPLEMENTATION OF JSON FORMULA:
        var _a = {F2} * 6;
        var _a2 = {_a} <= 6 ? 0 : ({_a} - 6);
        var rate = [quantity-based lookup from pricing tiers];
        var subtotal = {F1}*{rate};
        var total = ({subtotal} + {F2} + 15) * 1.1;
        {total}*1.1
        
        Args:
            **kwargs: Calculator parameters from JSON config
        
        Returns:
            LuxuryClassicPullUpBannersShopifyCalculatorQuoteResult with pricing details
        """
        import re
        
        # ==========================================
        # PARSE JSON FORMAT PARAMETERS
        # ==========================================
        quantity = int(kwargs.get('quantity', kwargs.get('qty', 1)))  # F1
        artworks = int(kwargs.get('artworks', 1))  # F2
        base_colour = kwargs.get('base_colour', 'Silver')  # F3
        size_raw = kwargs.get('size', '850mm W x 2000mm H')  # F4
        
        if quantity <= 0:
            raise ValueError('Quantity must be > 0')
        
        # Parse size for display only (doesn't affect calculations in formula)
        match = re.search(r'(\d+)mm.*?x\s*(\d+)mm', size_raw, re.IGNORECASE)
        if match:
            width = Decimal(match.group(1))
            height = Decimal(match.group(2))
        else:
            width = Decimal('850')
            height = Decimal('2000')
        
        # ==========================================
        # EXACT JSON FORMULA IMPLEMENTATION
        # ==========================================
        
        # Get rate from quantity-based pricing tiers
        rate = self._get_rate_for_quantity(quantity, size_raw)
        
        # var subtotal = {F1}*{rate};
        subtotal = Decimal(quantity) * rate
        
        # var total = ({subtotal} + {F2} + 15) * 1.1;
        # NOTE: {F2} is the artworks COUNT (not artwork cost calculation)
        total = (subtotal + Decimal(artworks) + Decimal('15')) * Decimal('1.1')
        
        # Final price: {total}*1.1
        total_price = total * Decimal('1.1')
        total_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        unit_price = total_price / Decimal(quantity)
        
        breakdown = {
            'rate': rate,
            'subtotal': subtotal,
            'artworks_added': Decimal(artworks),
            'production_setup': Decimal('15'),
            'pre_markup_total': subtotal + Decimal(artworks) + Decimal('15'),
            'after_first_markup': total,
            'total_price': total_price,
        }
        
        specifications = {
            'quantity': quantity,
            'size': size_raw,
            'base_colour': base_colour,
            'artworks': artworks,
            'width_mm': float(width),
            'height_mm': float(height),
        }
        
        return LuxuryClassicPullUpBannersShopifyCalculatorQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            cost_per_item=unit_price,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    def _get_rate_for_quantity(self, quantity: int, size: str) -> Decimal:
        """
        Get unit rate from quantity-based pricing tiers (exact JSON formula logic)
        
        Implements the nested ternary from JSON:
        var rate = {f4} == '850mm W x 2000mm H' ? (
            {F1} == 1 ? 135 : (
            {F1} == 2 ? 135 : (
            {F1} == 3 ? 132.61 : (...)
        
        Args:
            quantity: Number of units
            size: Size string (e.g., "850mm W x 2000mm H")
        
        Returns:
            Unit rate for the quantity tier
        """
        # Determine which pricing tier to use based on size
        if '2000mm' in size or '2000' in size:
            # 850mm W x 2000mm H pricing
            if quantity == 1: return Decimal('135')
            elif quantity == 2: return Decimal('135')
            elif quantity == 3: return Decimal('132.61')
            elif quantity == 4: return Decimal('126.88')
            elif quantity == 5: return Decimal('123.33')
            elif quantity == 6: return Decimal('120.84')
            elif quantity == 7: return Decimal('118.96')
            elif quantity == 8: return Decimal('117.47')
            elif quantity == 9: return Decimal('116.25')
            elif quantity == 10: return Decimal('115.22')
            elif quantity == 11: return Decimal('114.33')
            elif quantity == 12: return Decimal('113.56')
            elif quantity == 13: return Decimal('112.88')
            elif quantity == 14: return Decimal('112.27')
            elif quantity < 20: return Decimal('111.72')
            elif quantity < 25: return Decimal('109.6')
            elif quantity < 30: return Decimal('108.11')
            elif quantity < 35: return Decimal('106.99')
            elif quantity < 40: return Decimal('106.09')
            elif quantity < 45: return Decimal('105.35')
            elif quantity < 50: return Decimal('104.72')
            elif quantity < 55: return Decimal('104.18')
            elif quantity < 60: return Decimal('103.7')
            elif quantity < 65: return Decimal('103.28')
            elif quantity < 70: return Decimal('102.9')
            else: return Decimal('102.6')
        else:
            # Other sizes (1500mm or Shopping Center)
            if quantity == 1: return Decimal('128')
            elif quantity == 2: return Decimal('128')
            elif quantity == 3: return Decimal('125.74')
            elif quantity == 4: return Decimal('120.3')
            elif quantity == 5: return Decimal('116.94')
            elif quantity == 6: return Decimal('114.57')
            elif quantity == 7: return Decimal('112.8')
            elif quantity == 8: return Decimal('111.38')
            elif quantity == 9: return Decimal('110.23')
            elif quantity == 10: return Decimal('109.25')
            elif quantity == 11: return Decimal('108.4')
            elif quantity == 12: return Decimal('107.68')
            elif quantity == 13: return Decimal('107.03')
            elif quantity == 14: return Decimal('107.45')
            elif quantity < 20: return Decimal('105.93')
            elif quantity < 25: return Decimal('103.91')
            elif quantity < 30: return Decimal('102.5')
            elif quantity < 35: return Decimal('101.44')
            elif quantity < 40: return Decimal('100.59')
            elif quantity < 45: return Decimal('99.89')
            elif quantity < 50: return Decimal('99.29')
            elif quantity < 55: return Decimal('98.78')
            elif quantity < 60: return Decimal('98.33')
            elif quantity < 65: return Decimal('97.92')
            elif quantity < 70: return Decimal('97.56')
            else: return Decimal('97.28')
