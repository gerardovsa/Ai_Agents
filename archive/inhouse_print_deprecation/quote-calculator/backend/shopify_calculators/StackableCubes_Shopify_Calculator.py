"""
Stackable Cubes Shopify Calculator
✅ FIXED JAN 23, 2026: Implements TXT/JSON formula exactly

TXT Formula: (((sqm × tier) × 1.1) + artwork) × 1.1 × 1.1

Based on: SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt lines 5338-5457
Platform: Shopify
Fields: 4 fields (quantity, material, cube_size, artworks)
Key Features: 43-tier pricing, triple multiplier (×1.1 × 1.1 × 1.1), minimum $129
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
    Stackable Cubes Shopify Calculator
    ✅ FIXED JAN 23, 2026
    
    Implements TXT formula exactly:
    - 43-tier pricing per material (5mm: $37.50→$17.80, 3mm: $25→$12.42)
    - sqm_per_cube lookup (Small 0.36, Medium 0.64, Large 1.0, X-Large 1.35)
    - Artwork: First FREE, $5 per extra
    - Triple multiplier: ×1.1 × 1.1 × 1.1
    - Minimum order: $129
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
    
    def _get_price_per_sqm(self, total_sqm: Decimal, material: str) -> Decimal:
        """
        Get tiered price per sqm based on total sqm and material
        TXT Formula: 43 tiers per material
        """
        sqm_float = float(total_sqm)
        
        if '5mm' in material:
            # 5mm Corflute - 43 tiers (CORRECTED from user's JS)
            if sqm_float < 5: return Decimal('37.50')
            elif sqm_float < 6: return Decimal('34.02')
            elif sqm_float < 7: return Decimal('30.18')
            elif sqm_float < 8: return Decimal('29.65')
            elif sqm_float < 9: return Decimal('27.29')
            elif sqm_float < 10: return Decimal('27.17')
            elif sqm_float < 15: return Decimal('26.49')
            elif sqm_float < 20: return Decimal('25.40')
            elif sqm_float < 25: return Decimal('24.46')
            elif sqm_float < 30: return Decimal('24.76')
            elif sqm_float < 35: return Decimal('23.73')
            elif sqm_float < 40: return Decimal('23.39')
            elif sqm_float < 45: return Decimal('22.72')
            elif sqm_float < 50: return Decimal('22.52')
            elif sqm_float < 60: return Decimal('22.04')
            elif sqm_float < 70: return Decimal('21.52')
            elif sqm_float < 80: return Decimal('21.11')
            elif sqm_float < 90: return Decimal('20.79')
            elif sqm_float < 100: return Decimal('20.50')
            elif sqm_float < 110: return Decimal('20.27')
            elif sqm_float < 120: return Decimal('20.06')
            elif sqm_float < 130: return Decimal('19.88')
            elif sqm_float < 140: return Decimal('19.72')
            elif sqm_float < 150: return Decimal('19.56')
            elif sqm_float < 175: return Decimal('19.43')
            elif sqm_float < 200: return Decimal('19.18')
            elif sqm_float < 225: return Decimal('18.92')
            elif sqm_float < 250: return Decimal('18.75')
            elif sqm_float < 275: return Decimal('18.54')
            elif sqm_float < 300: return Decimal('18.41')
            elif sqm_float < 325: return Decimal('18.26')
            elif sqm_float < 350: return Decimal('18.16')
            elif sqm_float < 375: return Decimal('18.03')
            elif sqm_float < 400: return Decimal('17.93')
            elif sqm_float < 425: return Decimal('17.83')
            elif sqm_float < 450: return Decimal('17.76')
            elif sqm_float < 475: return Decimal('17.67')
            elif sqm_float < 500: return Decimal('17.61')
            elif sqm_float < 539: return Decimal('17.40')
            elif sqm_float < 550: return Decimal('17.40')
            elif sqm_float < 600: return Decimal('17.40')
            elif sqm_float < 650: return Decimal('17.30')
            elif sqm_float < 700: return Decimal('17.20')
            else: return Decimal('17.80')
        else:
            # 3mm Corflute - 43 tiers (CORRECTED from user's JS)
            if sqm_float < 5: return Decimal('25')
            elif sqm_float < 6: return Decimal('25')
            elif sqm_float < 7: return Decimal('22.09')
            elif sqm_float < 8: return Decimal('21.48')
            elif sqm_float < 9: return Decimal('21.02')
            elif sqm_float < 10: return Decimal('20.75')
            elif sqm_float < 15: return Decimal('20.73')
            elif sqm_float < 20: return Decimal('19.13')
            elif sqm_float < 25: return Decimal('18.82')
            elif sqm_float < 30: return Decimal('18.28')
            elif sqm_float < 35: return Decimal('17.61')
            elif sqm_float < 40: return Decimal('17.32')
            elif sqm_float < 45: return Decimal('16.89')
            elif sqm_float < 50: return Decimal('16.7')
            elif sqm_float < 60: return Decimal('16.4')
            elif sqm_float < 70: return Decimal('16.03')
            elif sqm_float < 80: return Decimal('15.74')
            elif sqm_float < 90: return Decimal('15.5')
            elif sqm_float < 100: return Decimal('15.3')
            elif sqm_float < 110: return Decimal('15.13')
            elif sqm_float < 120: return Decimal('14.98')
            elif sqm_float < 130: return Decimal('14.85')
            elif sqm_float < 140: return Decimal('14.74')
            elif sqm_float < 150: return Decimal('14.63')
            elif sqm_float < 175: return Decimal('14.54')
            elif sqm_float < 200: return Decimal('14.35')
            elif sqm_float < 225: return Decimal('14.16')
            elif sqm_float < 250: return Decimal('14.03')
            elif sqm_float < 275: return Decimal('13.89')
            elif sqm_float < 300: return Decimal('13.8')
            elif sqm_float < 325: return Decimal('13.69')
            elif sqm_float < 350: return Decimal('13.61')
            elif sqm_float < 375: return Decimal('13.52')
            elif sqm_float < 400: return Decimal('13.46')
            elif sqm_float < 425: return Decimal('13.39')
            elif sqm_float < 450: return Decimal('13.34')
            elif sqm_float < 475: return Decimal('13.27')
            elif sqm_float < 500: return Decimal('13.22')
            elif sqm_float < 539: return Decimal('13.08')
            elif sqm_float < 550: return Decimal('13.08')
            elif sqm_float < 600: return Decimal('13.08')
            elif sqm_float < 650: return Decimal('13')
            elif sqm_float < 700: return Decimal('12.42')
            else: return Decimal('12.42')
    
    def calculate(self, **kwargs) -> StackableCubesShopifyCalculatorQuoteResult:
        """
        Calculate Stackable Cubes quote using TXT/JSON formula
        
        TXT Formula:
        1. sqm = sqm_per_cube × quantity
        2. tier = 43-tier lookup
        3. material_cost = sqm × tier
        4. first_markup = material_cost × 1.1
        5. artwork = (art × 5) <= 5 ? 0 : (art × 5 - 5)
        6. with_artwork = first_markup + artwork
        7. second_markup = with_artwork × 1.1
        8. minimum = second_markup < 129 ? 129 : second_markup
        9. final = minimum × 1.1
        """
        # Extract parameters (JSON format)
        quantity = int(kwargs.get('quantity', 1))
        material_raw = kwargs.get('material', '5mm Corflute')
        cube_size_raw = kwargs.get('cube_size', 'Medium 400mm x 400mm')
        artworks = int(kwargs.get('artworks', 1))

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')

        # ✅ SQM per cube lookup (from JSON cube_specifications)
        sqm_map = {
            "Small 300mm x 300mm": Decimal('0.36'),
            "Medium 400mm x 400mm": Decimal('0.64'),
            "Large 500mm x 500mm": Decimal('1.0'),
            "X-Large 580mm x 580mm": Decimal('1.35')
        }
        sqm_per_cube = sqm_map.get(cube_size_raw, Decimal('0.64'))  # Default medium
        
        # ✅ Total SQM calculation
        total_sqm = sqm_per_cube * Decimal(quantity)
        
        # ✅ Get tiered price per sqm (43 tiers)
        price_per_sqm = self._get_price_per_sqm(total_sqm, material_raw)
        
        # ✅ Material cost
        material_cost = total_sqm * price_per_sqm
        
        # ✅ FIRST MULTIPLIER (10%)
        after_first_markup = material_cost * Decimal('1.1')
        
        # ✅ Artwork setup (first FREE, $5 per extra)
        _a = Decimal(artworks) * Decimal('5')
        if _a <= Decimal('5'):
            artwork_setup_cost = Decimal('0')
        else:
            artwork_setup_cost = _a - Decimal('5')
        
        # ✅ Add artwork
        with_artwork = after_first_markup + artwork_setup_cost
        
        # ✅ SECOND MULTIPLIER (10%)
        after_second_markup = with_artwork * Decimal('1.1')
        
        # ✅ Apply minimum order ($129)
        if after_second_markup < Decimal('129'):
            after_minimum = Decimal('129')
        else:
            after_minimum = after_second_markup
        
        # ✅ THIRD MULTIPLIER (10% - ALWAYS RUN)
        final_total = after_minimum * Decimal('1.1')
        
        # Round to 2 decimals
        total_price = final_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        unit_price = total_price / Decimal(quantity)

        breakdown = {
            'total_sqm': total_sqm,
            'price_per_sqm': price_per_sqm,
            'material_cost': material_cost,
            'after_first_markup': after_first_markup,
            'artwork_setup_cost': artwork_setup_cost,
            'with_artwork': with_artwork,
            'after_second_markup': after_second_markup,
            'after_minimum': after_minimum,
            'total_price': total_price,
        }

        specifications = {
            'quantity': quantity,
            'cube_size': cube_size_raw,
            'material': material_raw,
            'artworks': artworks,
            'sqm_per_cube': float(sqm_per_cube)
        }

        return StackableCubesShopifyCalculatorQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            cost_per_item=unit_price,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
