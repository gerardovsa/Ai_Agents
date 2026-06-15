"""
Selfie Frames Shopify Calculator
Exact implementation of Shopify JavaScript formula for Selfie Frames

✅ FIXED JAN 23, 2026: Implements TXT formula with 34-tier quantity-based pricing
Formula: ((qty × rate) + artwork) × 1.1

Based on: Shopify_Selfie_Frames.json specification + SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt
Platform: Shopify
Fields: 3 fields (quantity, size, artworks)
Key Features: 34-tier quantity-based pricing per size, simple artwork formula, single 10% markup
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
class SelfieFramesShopifyCalculatorQuoteResult:
    """Result from Selfie Frames Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class SelfieFramesShopifyCalculator:
    """
    Selfie Frames Shopify Calculator - Exact TXT JavaScript Implementation
    
    ✅ FIXED JAN 23, 2026
    
    Formula from TXT:
    - Artwork: First FREE, $5 per extra
    - var _a = {art} * 5;
    - var _a2 = {_a} <= 5 ? 0 : ({_a} - 5);
    - Formula: ((qty × rate) + artwork) × 1.1
    
    Features:
    - 34-tier quantity-based pricing per size
    - Small 600x900: $117 → $39.69
    - Large 900x1200: $172 → $61.69
    - Simple artwork formula (first FREE, $5 per extra)
    - Single 10% markup (NOT double GST)
    """
    
    CONFIG_FILE = "Shopify_Selfie_Frames.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Selfie Frames Shopify calculator"""
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
    
    
    def _get_price_per_unit(self, quantity: int, size: str) -> Decimal:
        """
        34-tier quantity-based pricing per size
        
        ⚠️ CRITICAL: Tier values copied EXACTLY from TXT file (line 6736-6769)
        Character-by-character verification completed Jan 23, 2026
        
        Small 600x900: $117 → $39.69 (34 tiers)
        Large 900x1200: $172 → $61.69 (34 tiers)
        """
        if 'Small' in size or '600' in size:
            # Small 600mm x 900mm - 34 tiers
            if quantity == 1: return Decimal('117.00')
            elif quantity == 2: return Decimal('108.00')
            elif quantity == 3: return Decimal('98.67')
            elif quantity == 4: return Decimal('83.00')
            elif quantity == 5: return Decimal('74.60')
            elif quantity == 6: return Decimal('68.67')
            elif quantity == 7: return Decimal('64.57')
            elif quantity == 8: return Decimal('61.50')
            elif quantity == 9: return Decimal('59.00')
            elif quantity == 10: return Decimal('57.00')
            elif quantity == 11: return Decimal('55.27')
            elif quantity == 12: return Decimal('53.83')
            elif quantity == 13: return Decimal('50.23')
            elif quantity == 14: return Decimal('51.43')
            elif quantity == 15: return Decimal('50.53')
            elif 16 <= quantity <= 20: return Decimal('46.80')
            elif 21 <= quantity <= 25: return Decimal('44.40')
            elif 26 <= quantity <= 30: return Decimal('42.60')
            elif 31 <= quantity <= 35: return Decimal('41.23')
            elif 36 <= quantity <= 40: return Decimal('40.15')
            elif 41 <= quantity <= 45: return Decimal('40.00')
            elif 46 <= quantity <= 50: return Decimal('39.96')
            elif 51 <= quantity <= 60: return Decimal('39.90')
            elif 61 <= quantity <= 70: return Decimal('39.86')
            elif 71 <= quantity <= 80: return Decimal('39.84')
            elif 81 <= quantity <= 90: return Decimal('39.80')
            elif 91 <= quantity <= 100: return Decimal('39.79')
            elif 101 <= quantity <= 110: return Decimal('39.76')
            elif 111 <= quantity <= 120: return Decimal('39.75')
            elif 121 <= quantity <= 130: return Decimal('39.74')
            elif 131 <= quantity <= 140: return Decimal('39.74')
            elif 141 <= quantity <= 150: return Decimal('39.73')
            elif 151 <= quantity <= 175: return Decimal('39.70')
            elif quantity >= 176: return Decimal('39.69')
            else: return Decimal('117.00')  # Fallback
        else:
            # Large 900mm x 1200mm - 34 tiers
            if quantity == 1: return Decimal('172.00')
            elif quantity == 2: return Decimal('163.00')
            elif quantity == 3: return Decimal('150.00')
            elif quantity == 4: return Decimal('127.00')
            elif quantity == 5: return Decimal('114.00')
            elif quantity == 6: return Decimal('105.17')
            elif quantity == 7: return Decimal('99.14')
            elif quantity == 8: return Decimal('94.50')
            elif quantity == 9: return Decimal('90.67')
            elif quantity == 10: return Decimal('87.70')
            elif quantity == 11: return Decimal('85.09')
            elif quantity == 12: return Decimal('82.83')
            elif quantity == 13: return Decimal('81.00')
            elif quantity == 14: return Decimal('79.36')
            elif quantity == 15: return Decimal('77.87')
            elif 16 <= quantity <= 20: return Decimal('72.30')
            elif 21 <= quantity <= 25: return Decimal('68.64')
            elif 26 <= quantity <= 30: return Decimal('66.00')
            elif 31 <= quantity <= 35: return Decimal('63.86')
            elif 36 <= quantity <= 40: return Decimal('62.20')
            elif 41 <= quantity <= 45: return Decimal('62.00')
            elif 46 <= quantity <= 50: return Decimal('61.96')
            elif 51 <= quantity <= 60: return Decimal('61.92')
            elif 61 <= quantity <= 70: return Decimal('61.86')
            elif 71 <= quantity <= 80: return Decimal('61.83')
            elif 81 <= quantity <= 90: return Decimal('61.80')
            elif 91 <= quantity <= 100: return Decimal('61.78')
            elif 101 <= quantity <= 110: return Decimal('61.76')
            elif 111 <= quantity <= 120: return Decimal('61.75')
            elif 121 <= quantity <= 130: return Decimal('61.74')
            elif 131 <= quantity <= 140: return Decimal('61.73')
            elif 141 <= quantity <= 150: return Decimal('61.72')
            elif 151 <= quantity <= 175: return Decimal('61.70')
            elif quantity >= 176: return Decimal('61.69')
            else: return Decimal('172.00')  # Fallback
    
    def calculate(self, **kwargs) -> SelfieFramesShopifyCalculatorQuoteResult:
        """
        Calculate Selfie Frames Shopify quote
        
        ✅ FIXED JAN 23, 2026: Now implements TXT formula exactly
        
        Formula from TXT:
        1. Tier lookup: Get rate per unit based on quantity and size
        2. Base cost: qty × rate
        3. Artwork: IF artworks > 1 THEN (artworks × 5) - 5 ELSE 0
        4. Subtotal: base_cost + artwork
        5. Final: subtotal × 1.1
        
        Args:
            **kwargs: Calculator parameters from JSON config
                quantity: Number of frames (1-200)
                size: "Small 600mm x 900mm" or "Large 900mm x 1200mm"
                artworks: Number of artwork designs (1-20)
        
        Returns:
            SelfieFramesShopifyCalculatorQuoteResult with pricing details
        """
        import re
        
        # ==========================================
        # STEP 1: PARSE JSON FORMAT PARAMETERS
        # ==========================================
        quantity = int(kwargs.get('quantity', kwargs.get('qty', 1)))
        
        # Size: Parse "Small 600mm x 900mm" or "Large 900mm x 1200mm"
        size_raw = kwargs.get('size', 'Small 600mm x 900mm')
        
        # Artworks: JSON field name variations
        artworks = int(kwargs.get('artworks', kwargs.get('number_of_artworks', 1)))

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')
        
        # ==========================================
        # STEP 2: TIER LOOKUP (34 tiers per size)
        # ==========================================
        price_per_unit = self._get_price_per_unit(quantity, size_raw)
        base_cost = price_per_unit * Decimal(quantity)
        
        # ==========================================
        # STEP 3: ARTWORK SETUP (First FREE, $5 per extra)
        # ==========================================
        # var _a = {art} * 5;
        # var _a2 = {_a} <= 5 ? 0 : ({_a} - 5);
        _a = Decimal(artworks) * Decimal('5')
        artwork_setup_cost = Decimal('0') if _a <= Decimal('5') else _a - Decimal('5')
        
        # ==========================================
        # STEP 4: SUBTOTAL (Base + Artwork)
        # ==========================================
        subtotal = base_cost + artwork_setup_cost
        
        # ==========================================
        # STEP 5: FINAL MULTIPLIER (10% markup)
        # ==========================================
        final_total = subtotal * Decimal('1.1')
        final_total = final_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        unit_price = final_total / Decimal(quantity)

        breakdown = {
            'quantity': Decimal(quantity),
            'price_per_unit': price_per_unit,
            'base_cost': base_cost,
            'artwork_setup_cost': artwork_setup_cost,
            'subtotal': subtotal,
            'final_multiplier': Decimal('1.1'),
            'total_price': final_total,
        }

        specifications = {
            'quantity': quantity,
            'size': size_raw,
            'artworks': artworks,
        }

        return SelfieFramesShopifyCalculatorQuoteResult(
            total_price=final_total,
            unit_price=unit_price,
            cost_per_item=unit_price,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
