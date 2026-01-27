"""
Election Signs Shopify Calculator
✅ FIXED JAN 23, 2026: Implements TXT/JSON formula exactly

TXT Formula: ((((sqm × (tier + sides_cost)) × custom_tax) + eyelets + artwork) × 0.95)
Minimum: $135, Final multiplier: ×1.1

Based on: SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt lines 5880-6100
Platform: Shopify
Fields: 9 fields
Key Features: 43-tier pricing, 5% discount, minimum $135, sides surcharge
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
class ElectionSignsShopifyCalculatorQuoteResult:
    """Result from Election Signs Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class ElectionSignsShopifyCalculator:
    """
    Election Signs Shopify Calculator
    ✅ FIXED JAN 23, 2026
    
    Implements TXT formula exactly:
    - 43-tier pricing per material (5mm: $31.25→$10.97, 3mm: $25→$8.91)
    - Sides surcharge: +$6 to tier price if double sided
    - Custom size tax: ×1.1 if custom
    - 5% discount: ×0.95
    - Minimum order: $135
    - Final multiplier: ×1.1
    """
    
    CONFIG_FILE = "Shopify_Election_Signs.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Election Signs Shopify calculator"""
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
            # 5mm - 43 tiers
            if sqm_float < 5: return Decimal('31.25')
            elif sqm_float < 6: return Decimal('28.35')
            elif sqm_float < 7: return Decimal('25.15')
            elif sqm_float < 8: return Decimal('24.71')
            elif sqm_float < 9: return Decimal('22.74')
            elif sqm_float < 10: return Decimal('22.64')
            elif sqm_float < 15: return Decimal('21.24')
            elif sqm_float < 20: return Decimal('19.5')
            elif sqm_float < 25: return Decimal('17.05')
            elif sqm_float < 30: return Decimal('17.3')
            elif sqm_float < 35: return Decimal('16.44')
            elif sqm_float < 40: return Decimal('16.16')
            elif sqm_float < 45: return Decimal('15.6')
            elif sqm_float < 50: return Decimal('15.43')
            elif sqm_float < 60: return Decimal('15.03')
            elif sqm_float < 70: return Decimal('14.6')
            elif sqm_float < 80: return Decimal('14.26')
            elif sqm_float < 90: return Decimal('13.99')
            elif sqm_float < 100: return Decimal('13.75')
            elif sqm_float < 110: return Decimal('13.56')
            elif sqm_float < 120: return Decimal('13.38')
            elif sqm_float < 130: return Decimal('13.23')
            elif sqm_float < 140: return Decimal('13.1')
            elif sqm_float < 150: return Decimal('12.97')
            elif sqm_float < 175: return Decimal('12.86')
            elif sqm_float < 200: return Decimal('12.65')
            elif sqm_float < 225: return Decimal('12.43')
            elif sqm_float < 250: return Decimal('12.29')
            elif sqm_float < 275: return Decimal('12.12')
            elif sqm_float < 300: return Decimal('12.01')
            elif sqm_float < 325: return Decimal('11.88')
            elif sqm_float < 350: return Decimal('11.8')
            elif sqm_float < 375: return Decimal('11.69')
            elif sqm_float < 400: return Decimal('11.61')
            elif sqm_float < 425: return Decimal('11.53')
            elif sqm_float < 450: return Decimal('11.47')
            elif sqm_float < 475: return Decimal('11.39')
            elif sqm_float < 500: return Decimal('11.34')
            elif sqm_float < 539: return Decimal('11.17')
            elif sqm_float < 550: return Decimal('11.17')
            elif sqm_float < 600: return Decimal('11.17')
            elif sqm_float < 650: return Decimal('11.08')
            elif sqm_float < 700: return Decimal('11')
            else: return Decimal('10.97')
        else:
            # 3mm - 43 tiers
            if sqm_float < 5: return Decimal('25')
            elif sqm_float < 6: return Decimal('25')
            elif sqm_float < 7: return Decimal('21.09')
            elif sqm_float < 8: return Decimal('20.48')
            elif sqm_float < 9: return Decimal('19.02')
            elif sqm_float < 10: return Decimal('18.75')
            elif sqm_float < 15: return Decimal('17.73')
            elif sqm_float < 20: return Decimal('16.13')
            elif sqm_float < 25: return Decimal('14.82')
            elif sqm_float < 30: return Decimal('14.28')
            elif sqm_float < 35: return Decimal('13.61')
            elif sqm_float < 40: return Decimal('13.32')
            elif sqm_float < 45: return Decimal('12.89')
            elif sqm_float < 50: return Decimal('12.7')
            elif sqm_float < 60: return Decimal('12.4')
            elif sqm_float < 70: return Decimal('12.03')
            elif sqm_float < 80: return Decimal('11.74')
            elif sqm_float < 90: return Decimal('11.5')
            elif sqm_float < 100: return Decimal('11.3')
            elif sqm_float < 110: return Decimal('11.13')
            elif sqm_float < 120: return Decimal('10.98')
            elif sqm_float < 130: return Decimal('10.85')
            elif sqm_float < 140: return Decimal('10.74')
            elif sqm_float < 150: return Decimal('10.63')
            elif sqm_float < 175: return Decimal('10.54')
            elif sqm_float < 200: return Decimal('10.35')
            elif sqm_float < 225: return Decimal('10.16')
            elif sqm_float < 250: return Decimal('10.03')
            elif sqm_float < 275: return Decimal('9.89')
            elif sqm_float < 300: return Decimal('9.8')
            elif sqm_float < 325: return Decimal('9.69')
            elif sqm_float < 350: return Decimal('9.61')
            elif sqm_float < 375: return Decimal('9.52')
            elif sqm_float < 400: return Decimal('9.46')
            elif sqm_float < 425: return Decimal('9.39')
            elif sqm_float < 450: return Decimal('9.34')
            elif sqm_float < 475: return Decimal('9.27')
            elif sqm_float < 500: return Decimal('9.22')
            elif sqm_float < 539: return Decimal('9.08')
            elif sqm_float < 550: return Decimal('9.08')
            elif sqm_float < 600: return Decimal('9.08')
            elif sqm_float < 650: return Decimal('9')
            elif sqm_float < 700: return Decimal('8.93')
            else: return Decimal('8.91')
    
    def _get_eyelet_price(self, eyelets: str) -> Decimal:
        """Get eyelet price from option title"""
        eyelet_prices = {
            "No Eyelets": Decimal('0'),
            "4 x Eyelets (1 In Each Corner)": Decimal('1.6'),
            "2 x Eyelets (top left and right corners)": Decimal('0.8'),
            "2 x Eyelets (center left and right)": Decimal('0.8'),
            "2 x Eyelets (center top and bottom)": Decimal('0.8'),
            "6 x Eyelets (3 each top and bottom)": Decimal('2.4'),
            "6 x Eyelets (3 each left and right)": Decimal('2.4')
        }
        return eyelet_prices.get(eyelets, Decimal('0'))
    
    def calculate(self, **kwargs) -> ElectionSignsShopifyCalculatorQuoteResult:
        """
        Calculate Election Signs quote using TXT/JSON formula
        
        TXT Formula:
        1. sqm = (width × height ÷ 1M) × qty
        2. tier = 43-tier lookup
        3. sides_cost = Double Sided ? 6 : 0
        4. custom_tax = Custom size ? 1.1 : 1
        5. subtotal = ((((sqm × (tier + sides_cost)) × custom_tax) + (eyelets.price × qty) + artwork) × 0.95)
        6. total = subtotal < 135 ? 135 : subtotal
        7. final = total × 1.1
        """
        # Extract parameters
        quantity = int(kwargs.get('quantity', 1))
        size_raw = kwargs.get('size', '600mm x 900mm')
        thickness_raw = kwargs.get('thickness', '5mm')
        sides_raw = kwargs.get('sides', 'Single Sided')
        eyelets_raw = kwargs.get('eyelets', 'No Eyelets')
        artworks = int(kwargs.get('artworks', 1))
        width_mm = kwargs.get('width_mm')  # For custom sizes
        height_mm = kwargs.get('height_mm')  # For custom sizes

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')

        # ✅ Size dimensions (from JSON size_dimensions)
        is_custom = size_raw == 'Custom'
        if is_custom and width_mm and height_mm:
            width = Decimal(str(width_mm))
            height = Decimal(str(height_mm))
        else:
            size_map = {
                "450mm x 600mm": (Decimal('450'), Decimal('600')),
                "600mm x 900mm": (Decimal('600'), Decimal('900')),
                "900mm x 1200mm": (Decimal('900'), Decimal('1200')),
                "1200mm x 2400mm": (Decimal('1200'), Decimal('2400'))
            }
            width, height = size_map.get(size_raw, (Decimal('600'), Decimal('900')))
        
        # ✅ SQM calculation
        area_m2 = (width * height) / Decimal('1000000')
        total_sqm = area_m2 * Decimal(quantity)
        
        # ✅ Get tiered price per sqm (43 tiers)
        price_per_sqm = self._get_price_per_sqm(total_sqm, thickness_raw)
        
        # ✅ Sides surcharge (+$6 if double sided)
        sides_cost = Decimal('6') if 'Double' in sides_raw else Decimal('0')
        
        # ✅ Custom tax multiplier (×1.1 if custom)
        custom_tax = Decimal('1.1') if is_custom else Decimal('1')
        
        # ✅ Eyelet cost per sign
        eyelet_price_per_sign = self._get_eyelet_price(eyelets_raw)
        eyelet_total_cost = eyelet_price_per_sign * Decimal(quantity)
        
        # ✅ Artwork cost (first FREE, $5 per extra)
        _a = Decimal(artworks) * Decimal('5')
        if _a <= Decimal('5'):
            artwork_setup_cost = Decimal('0')
        else:
            artwork_setup_cost = _a - Decimal('5')
        
        # ✅ TXT Formula
        material_cost = total_sqm * (price_per_sqm + sides_cost)
        material_with_tax = material_cost * custom_tax
        subtotal_before_discount = material_with_tax + eyelet_total_cost + artwork_setup_cost
        
        # ✅ 5% discount (×0.95)
        subtotal = subtotal_before_discount * Decimal('0.95')
        
        # ✅ Minimum order ($135)
        if subtotal < Decimal('135'):
            after_minimum = Decimal('135')
        else:
            after_minimum = subtotal
        
        # ✅ Final multiplier (×1.1)
        final_total = after_minimum * Decimal('1.1')
        
        # Round to 2 decimals
        total_price = final_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        unit_price = total_price / Decimal(quantity)

        breakdown = {
            'total_sqm': total_sqm,
            'price_per_sqm': price_per_sqm,
            'sides_cost': sides_cost,
            'material_cost': material_cost,
            'custom_tax': custom_tax,
            'material_with_tax': material_with_tax,
            'eyelet_cost': eyelet_total_cost,
            'artwork_setup_cost': artwork_setup_cost,
            'subtotal_before_discount': subtotal_before_discount,
            'subtotal': subtotal,
            'after_minimum': after_minimum,
            'total_price': total_price,
        }

        specifications = {
            'quantity': quantity,
            'size': size_raw,
            'thickness': thickness_raw,
            'sides': sides_raw,
            'eyelets': eyelets_raw,
            'artworks': artworks,
            'area_m2': float(area_m2)
        }

        return ElectionSignsShopifyCalculatorQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            cost_per_item=unit_price,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
