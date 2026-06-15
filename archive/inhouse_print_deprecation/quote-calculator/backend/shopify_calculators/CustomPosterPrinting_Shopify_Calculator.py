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
    
"""
Custom Poster Printing Shopify Calculator
Exact implementation of Shopify JavaScript formula for Custom Poster Printing

Based on: SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt Lines 10700-10890
Platform: Shopify
Formula: ((sqm × tier × taxOnCustom) + artworkSurcharge) × 1.1
Minimum: $117 + $15 = $132
Key Features: 50 SQM-based tiers for Satin, 50 tiers for Yuppo, custom size 10% tax

REWRITTEN: January 26, 2026 - Complete rewrite with exact TXT formula
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
    
    EXACT TXT FORMULA (Lines 10700-10890):
    sqm = (width × height / 1,000,000) × quantity
    tier = based on sqm (50 tiers for Satin, 50 for Yuppo)
    taxRateOnCustom = 1.1 if custom size else 1.0
    artworkSurcharge = (artworks × 5) - 5 (first free)
    subtotal = ((sqm × tier × taxRateOnCustom) + artworkSurcharge)
    total = subtotal × 1.1
    minimum = $117 + $15 = $132
    """
    
    CONFIG_FILE = "Shopify_Custom_Poster_Printing.json"
    
    # 250GSM Satin Poster Paper - 50 tiers
    SATIN_TIERS = [
        (1, 90.00), (2, 45.00), (3, 30.00), (4, 22.50), (5, 18.00),
        (6, 15.00), (7, 12.86), (8, 12.22), (9, 12.03), (10, 11.88),
        (12, 11.63), (14, 11.43), (16, 11.27), (18, 11.14), (20, 11.03),
        (25, 10.81), (30, 10.65), (35, 10.52), (40, 10.41), (45, 10.32),
        (50, 10.24), (55, 10.17), (60, 10.11), (65, 10.05), (70, 10.00),
        (75, 9.96), (80, 9.92), (85, 9.88), (90, 9.84), (95, 9.81),
        (100, 9.78), (105, 9.75), (110, 9.73), (115, 9.70), (120, 9.68),
        (125, 9.65), (130, 9.63), (135, 9.61), (140, 9.59), (145, 9.57),
        (150, 9.55), (155, 9.54), (160, 9.52), (165, 9.50), (170, 9.49),
        (175, 9.47), (180, 9.46), (185, 9.44), (190, 9.43), (195, 9.42),
        (200, 9.40), (205, 9.39), (210, 9.38), (215, 9.37), (220, 9.36),
        (225, 9.35), (230, 9.34), (235, 9.33), (240, 9.32), (245, 9.31)
    ]
    
    # 200GSM Yuppo Synthetic Paper - 50 tiers
    YUPPO_TIERS = [
        (1, 90.00), (2, 45.00), (3, 30.00), (4, 22.50), (5, 19.26),
        (6, 18.69), (7, 18.26), (8, 17.92), (9, 17.65), (10, 17.42),
        (12, 17.05), (14, 16.77), (16, 16.54), (18, 16.34), (20, 16.18),
        (25, 15.86), (30, 15.62), (35, 15.42), (40, 15.26), (45, 15.13),
        (50, 15.02), (55, 14.91), (60, 14.83), (65, 14.75), (70, 14.67),
        (75, 14.61), (80, 14.55), (85, 14.49), (90, 14.44), (95, 14.39),
        (100, 14.35), (105, 14.30), (110, 14.26), (115, 14.23), (120, 14.19),
        (125, 14.16), (130, 14.12), (135, 14.09), (140, 14.06), (145, 14.04),
        (150, 14.01), (155, 13.98), (160, 13.96), (165, 13.94), (170, 13.91),
        (175, 13.89), (180, 13.87), (185, 13.85), (190, 13.83), (195, 13.81),
        (200, 13.79), (205, 13.78), (210, 13.76), (215, 13.74), (220, 13.72),
        (225, 13.71), (230, 13.69), (235, 13.68), (240, 13.66), (245, 13.65)
    ]
    
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
        Calculate Custom Poster Printing Shopify quote using EXACT TXT FORMULA
        
        Args:
            quantity: Number of posters
            width_mm: Width in millimeters
            height_mm: Height in millimeters  
            paper_stock: '250GSM Satin Poster Paper' or '200GSM Yuppo Synthetic Paper'
            artworks: Number of artworks (default 1)
            size: Optional size string (determines if custom)
        
        Returns:
            CustomPosterPrintingShopifyCalculatorQuoteResult with pricing details
        """
        quantity = int(kwargs.get('quantity', kwargs.get('F1', 10)))
        width_mm = Decimal(str(kwargs.get('width_mm', kwargs.get('F3', 420))))
        height_mm = Decimal(str(kwargs.get('height_mm', kwargs.get('F7', 594))))
        paper_stock = kwargs.get('paper_stock', kwargs.get('F4', '250GSM Satin Poster Paper'))
        artworks = int(kwargs.get('artworks', kwargs.get('F10', 1)))
        size = kwargs.get('size', kwargs.get('F6', 'Custom'))

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')

        # Calculate total square meters
        sqm = (width_mm * height_mm / Decimal('1000000')) * Decimal(quantity)
        
        # Get price per SQM based on material
        tier_price = self._get_tier_price(float(sqm), paper_stock)
        
        # Tax rate for custom sizes (10% surcharge)
        tax_rate_on_custom = Decimal('1.1') if size == 'Custom' else Decimal('1.0')
        
        # Artwork surcharge: (artworks × 5) - 5, but only if result > 0
        # Formula: _a = artworks × 5, then _a2 = _a <= 5 ? 0 : (_a - 5)
        artwork_temp = artworks * 5
        artwork_surcharge = Decimal(max(0, artwork_temp - 5))
        
        # Subtotal = (sqm × tier × taxOnCustom) + artworkSurcharge
        material_cost = sqm * tier_price * tax_rate_on_custom
        subtotal = material_cost + artwork_surcharge
        
        # Apply final 10% GST
        total_before_min = subtotal * Decimal('1.1')
        
        # Minimum price: $117 + $15 = $132
        MINIMUM_PRICE = Decimal('132.00')
        total_price = max(total_before_min, MINIMUM_PRICE)
        
        # Round to 2 decimal places
        total_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        unit_price = (total_price / Decimal(quantity)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        breakdown = {
            'sqm': sqm,
            'tier_price_per_sqm': tier_price,
            'material_cost': material_cost,
            'tax_rate_on_custom': tax_rate_on_custom,
            'artwork_surcharge': artwork_surcharge,
            'subtotal': subtotal,
            'total_before_min': total_before_min,
            'minimum_applied': total_price > total_before_min,
            'total_price': total_price
        }

        specifications = {
            'quantity': quantity,
            'width_mm': float(width_mm),
            'height_mm': float(height_mm),
            'paper_stock': paper_stock,
            'artworks': artworks,
            'size': size
        }

        return CustomPosterPrintingShopifyCalculatorQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            cost_per_item=unit_price,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    def _get_tier_price(self, sqm: float, paper_stock: str) -> Decimal:
        """Get price per SQM based on total SQM and paper stock"""
        # Choose tier table
        tiers = self.SATIN_TIERS if '250GSM Satin' in paper_stock else self.YUPPO_TIERS
        
        # Find tier (tiers are sorted by sqm threshold)
        for threshold, price in tiers:
            if sqm < threshold:
                return Decimal(str(price))
        
        # If >= 245 sqm, use lowest tier (9.30 for Satin, 13.63 for Yuppo)
        return Decimal('9.30') if '250GSM Satin' in paper_stock else Decimal('13.63')
