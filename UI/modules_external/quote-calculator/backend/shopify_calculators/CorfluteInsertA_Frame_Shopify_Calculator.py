"""
Corflute Insert A-Frame Shopify Calculator
Exact implementation of Shopify JavaScript formula for Corflute Insert A-Frame

✅ FIXED JAN 23, 2026: Implements TXT formula with 26-tier quantity-based pricing
Formula: ((qty × rate) + artwork) × 1.1

Based on: SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt (lines 10000-10200)
Platform: Shopify
Fields: 3 fields (quantity, size, artworks)
Key Features: 26-tier quantity-based pricing, simple artwork formula, single 10% markup
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
class CorfluteInsertA_FrameShopifyCalculatorQuoteResult:
    """Result from Corflute Insert A-Frame Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class CorfluteInsertA_FrameShopifyCalculator:
    """
    Corflute Insert A-Frame Shopify Calculator - Exact TXT JavaScript Implementation
    
    ✅ FIXED JAN 23, 2026
    
    Formula from TXT:
    - 26-tier quantity-based pricing ($159 → $99)
    - Artwork: First FREE, $5 per extra
    - Formula: ((qty × rate) + artwork) × 1.1
    
    Features:
    - Simple tier pricing (like Selfie Frames)
    - NOT cost-based with setup/profit margins
    - Single 10% markup (NOT double GST)
    """
    
    CONFIG_FILE = "Shopify_Corflute_Insert_A_Frame.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Corflute Insert A-Frame Shopify calculator"""
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
    
    
    def _get_price_per_unit(self, quantity: int) -> Decimal:
        """
        26-tier quantity-based pricing
        
        ⚠️ CRITICAL: Tier values copied EXACTLY from TXT file (lines 10030-10056)
        Character-by-character verification completed Jan 23, 2026
        
        $159 → $99 (26 tiers)
        """
        if quantity == 1: return Decimal('159')
        elif quantity == 2: return Decimal('146.94')
        elif quantity == 3: return Decimal('138.3333333')
        elif quantity == 4: return Decimal('130')
        elif quantity == 5: return Decimal('125')
        elif quantity == 6: return Decimal('130.8333333')
        elif quantity == 7: return Decimal('127.1428571')
        elif quantity == 8: return Decimal('124.375')
        elif quantity == 9: return Decimal('122.1111111')
        elif quantity == 10: return Decimal('120')
        elif 11 <= quantity <= 12: return Decimal('117.0833333')
        elif 13 <= quantity <= 14: return Decimal('115')
        elif quantity == 15: return Decimal('114')
        elif 16 <= quantity <= 20: return Decimal('110.75')
        elif 21 <= quantity <= 25: return Decimal('108.4')
        elif 26 <= quantity <= 30: return Decimal('107')
        elif 31 <= quantity <= 35: return Decimal('105.7142857')
        elif 36 <= quantity <= 40: return Decimal('104.75')
        elif 41 <= quantity <= 45: return Decimal('103.8888889')
        elif 46 <= quantity <= 50: return Decimal('103.4')
        elif 51 <= quantity <= 60: return Decimal('102.8333333')
        elif 61 <= quantity <= 70: return Decimal('102.2857143')
        elif 71 <= quantity <= 80: return Decimal('101.9625')
        elif 81 <= quantity <= 90: return Decimal('101.6111111')
        elif 91 <= quantity <= 100: return Decimal('101.35')
        elif quantity >= 101: return Decimal('99')
        else: return Decimal('159')  # Fallback
    
    def calculate(self, **kwargs) -> CorfluteInsertA_FrameShopifyCalculatorQuoteResult:
        """
        Calculate quote for Corflute Insert A-Frame
        
        ✅ FIXED JAN 23, 2026: Now implements TXT formula exactly
        
        Formula from TXT (lines 10000-10200):
        1. Tier lookup: Get rate per unit based on quantity
        2. Base cost: qty × rate
        3. Artwork: IF artworks > 1 THEN (artworks × 5) - 5 ELSE 0
        4. Subtotal: base_cost + artwork
        5. Final: subtotal × 1.1
        
        Args:
            **kwargs: Calculator parameters from JSON config
                quantity: Number of A-frames (1-10000)
                size: "600mm(W) x 900mm(H)" (only one size option)
                artworks: Number of artwork designs (1-20)
        
        Returns:
            CorfluteInsertA_FrameShopifyCalculatorQuoteResult with pricing details
        """
        # ==========================================
        # STEP 1: PARSE JSON FORMAT PARAMETERS
        # ==========================================
        quantity = int(kwargs.get('quantity', kwargs.get('qty', 1)))
        size_raw = kwargs.get('size', '600mm(W) x 900mm(H)')
        artworks = int(kwargs.get('artworks', 1))

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')
        
        # ==========================================
        # STEP 2: TIER LOOKUP (26 tiers)
        # ==========================================
        price_per_unit = self._get_price_per_unit(quantity)
        base_cost = price_per_unit * Decimal(quantity)
        
        # ==========================================
        # STEP 3: ARTWORK SETUP (First FREE, $5 per extra)
        # ==========================================
        # var _a = {art} * 5;
        # var _a2 = {_a} <= 5 ? 0 : ({_a} - 5);
        _a = Decimal(artworks) * Decimal('5')
        artwork_cost = Decimal('0') if _a <= Decimal('5') else _a - Decimal('5')
        
        # ==========================================
        # STEP 4: SUBTOTAL (Base + Artwork)
        # ==========================================
        # var total = (qty * _up) + _a2;
        subtotal = base_cost + artwork_cost
        
        # ==========================================
        # STEP 5: FINAL MULTIPLIER (10% markup)
        # ==========================================
        # {total} * 1.10
        final_total = subtotal * Decimal('1.1')
        final_total = final_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        unit_price = final_total / Decimal(quantity)

        breakdown = {
            'quantity': Decimal(quantity),
            'price_per_unit': price_per_unit,
            'base_cost': base_cost,
            'artwork_cost': artwork_cost,
            'subtotal': subtotal,
            'final_multiplier': Decimal('1.1'),
            'total_price': final_total,
        }

        specifications = {
            'quantity': quantity,
            'size': size_raw,
            'artworks': artworks,
        }

        return CorfluteInsertA_FrameShopifyCalculatorQuoteResult(
            total_price=final_total,
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
