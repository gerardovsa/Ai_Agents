"""
Custom Vinyl Stickers Shopify Calculator
Complete roll-to-roll implementation with accurate JSON specification - NO WEBSITE CALCULATOR

Based on: Shopify_Custom_Vinyl_Stickers.json
Implementation Date: January 25, 2026
Platform: Shopify (backend-only, no website validation possible)
Parameters: 10 fields (quantity, size, width, height, vinyl_family, adhesive, laminate, cutting_method, artworks, labour_rate)
Key Features: Roll-to-roll production (1370mm rolls), 51-tier SQM pricing, laminating costs, cutting labour, kiss-cut surcharge, minimum order
"""

import json
import math
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CustomVinylStickersShopifyCalculatorQuoteResult:
    """Result from Custom Vinyl Stickers Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class CustomVinylStickersShopifyCalculator:
    """
    Custom Vinyl Stickers Shopify Calculator - Accurate Roll-to-Roll Implementation
    
    NO WEBSITE CALCULATOR - Backend implementation only for AI access
    
    Features (from Shopify_Custom_Vinyl_Stickers.json):
    - Roll-to-roll production: 1370mm wide rolls, 50m default length, 10% waste factor
    - 51-tier square meter-based pricing ($950/sqm down to $14/sqm)
    - Material multipliers: Standard ×1.0, Premium ×1.25, Removable ×1.15
    - Roll setup: $15 per extra roll (first roll free)
    - Laminating costs: $15 setup + (rolls / 1 roll per hour) × labour_rate
    - Cutting labour: 5 minutes per linear meter × labour_rate
    - Kiss-cut surcharge: $15 per linear meter (only for Kiss-Cut method)
    - Artwork costs: First included, then $5 each
    - Minimum order: IF total < $45 THEN $55 ($45 + $10 handling)
    - GST: ×1.1 (10% Australian GST)
    """
    
    CONFIG_FILE = "Shopify_Custom_Vinyl_Stickers.json"
    
    # 51-tier square meter pricing (Standard Vinyl base rates)
    SQM_RATES = [
        {"sqm_max": 0.01, "rate": 950},
        {"sqm_max": 0.02, "rate": 475},
        {"sqm_max": 0.03, "rate": 317},
        {"sqm_max": 0.05, "rate": 190},
        {"sqm_max": 0.08, "rate": 119},
        {"sqm_max": 0.1, "rate": 95},
        {"sqm_max": 0.15, "rate": 73},
        {"sqm_max": 0.2, "rate": 60},
        {"sqm_max": 0.25, "rate": 52},
        {"sqm_max": 0.3, "rate": 47},
        {"sqm_max": 0.4, "rate": 42},
        {"sqm_max": 0.5, "rate": 38},
        {"sqm_max": 0.6, "rate": 35},
        {"sqm_max": 0.7, "rate": 33},
        {"sqm_max": 0.8, "rate": 31.5},
        {"sqm_max": 0.9, "rate": 30.2},
        {"sqm_max": 1, "rate": 29},
        {"sqm_max": 1.25, "rate": 27.5},
        {"sqm_max": 1.5, "rate": 26.3},
        {"sqm_max": 1.75, "rate": 25.4},
        {"sqm_max": 2, "rate": 24.5},
        {"sqm_max": 2.5, "rate": 23.2},
        {"sqm_max": 3, "rate": 22.3},
        {"sqm_max": 3.5, "rate": 21.6},
        {"sqm_max": 4, "rate": 21},
        {"sqm_max": 4.5, "rate": 20.5},
        {"sqm_max": 5, "rate": 20},
        {"sqm_max": 6, "rate": 19.3},
        {"sqm_max": 7, "rate": 18.8},
        {"sqm_max": 8, "rate": 18.4},
        {"sqm_max": 9, "rate": 18.1},
        {"sqm_max": 10, "rate": 17.8},
        {"sqm_max": 12, "rate": 17.3},
        {"sqm_max": 14, "rate": 17},
        {"sqm_max": 16, "rate": 16.8},
        {"sqm_max": 18, "rate": 16.6},
        {"sqm_max": 20, "rate": 16.5},
        {"sqm_max": 25, "rate": 16.2},
        {"sqm_max": 30, "rate": 16},
        {"sqm_max": 35, "rate": 15.8},
        {"sqm_max": 40, "rate": 15.6},
        {"sqm_max": 45, "rate": 15.5},
        {"sqm_max": 50, "rate": 15.4},
        {"sqm_max": 60, "rate": 15.2},
        {"sqm_max": 70, "rate": 15.1},
        {"sqm_max": 80, "rate": 15},
        {"sqm_max": 90, "rate": 14.9},
        {"sqm_max": 100, "rate": 14.8},
        {"sqm_max": 150, "rate": 14.5},
        {"sqm_max": 200, "rate": 14.3},
        {"sqm_max": 999999, "rate": 14}
    ]
    
    # Material multipliers (from JSON)
    MATERIAL_MULTIPLIERS = {
        "Standard Vinyl": Decimal("1.0"),
        "Standard (Monomeric)": Decimal("1.0"),
        "Premium Vinyl": Decimal("1.25"),
        "Premium (Polymeric)": Decimal("1.25")
    }
    
    # Adhesive multipliers (from JSON - Removable applies to material cost)
    ADHESIVE_MULTIPLIERS = {
        "Permanent": Decimal("1.0"),
        "Removable": Decimal("1.15")
    }
    
    # Roll constants (from JSON)
    ROLL_WIDTH_MM = 1370
    ROLL_WIDTH_M = Decimal("1.37")
    DEFAULT_ROLL_LENGTH_M = 50
    WASTE_FACTOR = Decimal("1.10")  # 10% waste
    PER_EXTRA_ROLL_SETUP_FEE = Decimal("15")
    
    # Laminating costs (from JSON)
    LAMINATING_SETUP_FEE = Decimal("15")
    ROLLS_PER_HOUR = 1
    TRADE_RATE_PER_HOUR = Decimal("70")
    NONTRADE_RATE_PER_HOUR = Decimal("90")
    
    # Cutting costs (from JSON)
    PER_LINEAR_METER_MINUTES = 5
    KISS_CUT_PER_LINEAR_M = Decimal("15")
    
    # Size presets
    SIZE_PRESETS = {
        "50mm Circle": (50, 50),
        "75mm Circle": (75, 75),
        "100mm Circle": (100, 100),
        "50mm Square": (50, 50),
        "75mm Square": (75, 75),
        "100mm Square": (100, 100),
        "100x50mm Rectangle": (100, 50),
        "150x75mm Rectangle": (150, 75),
        "200x100mm Rectangle": (200, 100)
    }
    
    GST_RATE = Decimal("1.1")  # 10% Australian GST
    
    def __init__(self):
        """Initialize Custom Vinyl Stickers Shopify calculator"""
        self.config = self._load_config()
    
    def _load_config(self) -> Optional[Dict]:
        """Load configuration from JSON file"""
        try:
            config_path = Path(__file__).parent.parent.parent / "config" / "shopify" / self.CONFIG_FILE
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("shopify_custom_vinyl_stickers", {})
        except Exception as e:
            print(f"⚠️ Warning: Could not load config {self.CONFIG_FILE}: {e}")
        return None
    
    def calculate(
        self,
        quantity: int,
        size: str = "75mm Circle",
        width: int = None,
        height: int = None,
        vinyl_family: str = "Standard (Monomeric)",
        adhesive: str = "Permanent",
        laminate: str = "No Lamination",
        cutting_method: str = "Kiss-Cut (Individual)",
        artworks: int = 1,
        labour_rate: str = "Trade ($70/hr)",
        **kwargs
    ) -> CustomVinylStickersShopifyCalculatorQuoteResult:
        """
        Calculate Custom Vinyl Stickers Shopify quote
        
        Args:
            quantity: Number of stickers (1-10000)
            size: Preset size or "Custom Size"
            width: Custom width in mm (required if size="Custom Size")
            height: Custom height in mm (required if size="Custom Size")
            vinyl_family: Material type (Standard/Premium)
            adhesive: Adhesive type (Permanent/Removable)
            laminate: Laminate type (No Lamination/Gloss/Matte)
            cutting_method: Cutting method (Kiss-Cut/Die-Cut/Contour-Cut/Sheet)
            artworks: Number of designs (1-20)
            labour_rate: Labour rate (Trade $70/hr or Non-Trade $90/hr) - currently unused
        
        Returns:
            CustomVinylStickersShopifyCalculatorQuoteResult with pricing details
        """
        # Handle legacy parameter names
        if 'width_mm' in kwargs and width is None:
            width = kwargs['width_mm']
            size = "Custom Size"
        if 'height_mm' in kwargs and height is None:
            height = kwargs['height_mm']
            size = "Custom Size"
        if 'finish' in kwargs and laminate == "No Lamination":
            finish = kwargs['finish']
            if 'gloss' in finish.lower():
                laminate = "Gloss Laminate"
            elif 'matte' in finish.lower():
                laminate = "Matte Laminate"
        
        # Step 1: Determine dimensions
        if size != "Custom Size" and size in self.SIZE_PRESETS:
            width, height = self.SIZE_PRESETS[size]
        elif size == "Custom Size":
            if width is None or height is None:
                raise ValueError("Custom Size requires width and height parameters")
        else:
            # Default to 75mm Circle if invalid size
            width, height = 75, 75
        
        # Step 2: Calculate artwork cost (first included, then $5 each)
        artwork_total = artworks * Decimal("5")
        if artwork_total <= Decimal("5"):
            artwork_cost = Decimal("0")
        else:
            artwork_cost = artwork_total - Decimal("5")
        
        # Step 3: Calculate total square meters
        sqm_per_sticker = (Decimal(width) * Decimal(height)) / Decimal("1000000")
        total_sqm = sqm_per_sticker * Decimal(quantity)
        
        # Step 4: Roll-to-roll layout calculations
        stickers_per_row = math.floor(self.ROLL_WIDTH_MM / width)
        stickers_per_linear_m = stickers_per_row * math.floor(1000 / height)
        
        if stickers_per_linear_m > 0:
            raw_linear_m = math.ceil(quantity / stickers_per_linear_m)
        else:
            raw_linear_m = quantity  # Fallback if sticker too large
        
        linear_m_with_waste = Decimal(raw_linear_m) * self.WASTE_FACTOR
        
        # Step 5: Determine base rate per SQM from 51-tier table
        base_rate_per_sqm = self._get_sqm_rate(float(total_sqm))
        
        # Step 6: Apply material multiplier
        material_mult = self.MATERIAL_MULTIPLIERS.get(vinyl_family, Decimal("1.0"))
        adjusted_rate_per_sqm = base_rate_per_sqm * material_mult
        
        # Step 7: Apply adhesive multiplier
        adhesive_mult = self.ADHESIVE_MULTIPLIERS.get(adhesive, Decimal("1.0"))
        adjusted_rate_per_sqm = adjusted_rate_per_sqm * adhesive_mult
        
        # Step 8: Calculate material cost using SQM pricing
        material_cost = total_sqm * adjusted_rate_per_sqm
        
        # Step 9: Calculate rolls needed
        rolls_needed = math.ceil(float(linear_m_with_waste) / self.DEFAULT_ROLL_LENGTH_M)
        
        # Step 10: Roll setup fees (first roll free, $15 per extra roll)
        roll_setup_cost = self.PER_EXTRA_ROLL_SETUP_FEE * Decimal(max(0, rolls_needed - 1))
        
        # Step 11: Laminating costs (only if laminate selected)
        laminating_cost = Decimal("0")
        if laminate != "No Lamination":
            labour_rate_value = self.NONTRADE_RATE_PER_HOUR if "Non-Trade" in labour_rate else self.TRADE_RATE_PER_HOUR
            laminating_hours = Decimal(rolls_needed) / Decimal(self.ROLLS_PER_HOUR)
            laminating_cost = self.LAMINATING_SETUP_FEE + (laminating_hours * labour_rate_value)
        
        # Step 12: Cutting labour costs (5 minutes per linear meter)
        labour_rate_value = self.NONTRADE_RATE_PER_HOUR if "Non-Trade" in labour_rate else self.TRADE_RATE_PER_HOUR
        cutting_labour_minutes = linear_m_with_waste * Decimal(self.PER_LINEAR_METER_MINUTES)
        cutting_labour_cost = (cutting_labour_minutes / Decimal("60")) * labour_rate_value
        
        # Step 13: Kiss-cut surcharge (only for Kiss-Cut method)
        kiss_cut_surcharge = Decimal("0")
        if "Kiss-Cut" in cutting_method:
            kiss_cut_surcharge = self.KISS_CUT_PER_LINEAR_M * linear_m_with_waste
        
        # Step 14: Calculate subtotal
        subtotal = material_cost + roll_setup_cost + laminating_cost + cutting_labour_cost + kiss_cut_surcharge + artwork_cost
        
        # Step 15: Apply minimum order rule
        minimum_threshold = Decimal("45")
        minimum_order_fee = Decimal("10")
        if subtotal < minimum_threshold:
            handling_fee = minimum_order_fee
            subtotal_before_gst = minimum_threshold + minimum_order_fee
        else:
            handling_fee = Decimal("0")
            subtotal_before_gst = subtotal
        
        # Step 16: Apply GST
        total_price = subtotal_before_gst * self.GST_RATE
        total_price = total_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Calculate per-unit pricing
        unit_price = total_price / Decimal(quantity)
        
        # Build breakdown
        breakdown = {
            "sqm_per_sticker": sqm_per_sticker,
            "total_sqm": total_sqm,
            "stickers_per_row": Decimal(stickers_per_row),
            "stickers_per_linear_m": Decimal(stickers_per_linear_m),
            "raw_linear_m": Decimal(raw_linear_m),
            "linear_m_with_waste": linear_m_with_waste,
            "rolls_needed": Decimal(rolls_needed),
            "base_rate_per_sqm": base_rate_per_sqm,
            "material_multiplier": material_mult,
            "adhesive_multiplier": adhesive_mult,
            "material_cost": material_cost,
            "roll_setup_cost": roll_setup_cost,
            "laminating_cost": laminating_cost,
            "cutting_labour_cost": cutting_labour_cost,
            "kiss_cut_surcharge": kiss_cut_surcharge,
            "artwork_cost": artwork_cost,
            "subtotal": subtotal,
            "handling_fee": handling_fee,
            "subtotal_before_gst": subtotal_before_gst,
            "gst": total_price - subtotal_before_gst,
            "total_price": total_price
        }
        
        # Build specifications
        specifications = {
            "quantity": quantity,
            "size": size,
            "width_mm": width,
            "height_mm": height,
            "vinyl_family": vinyl_family,
            "adhesive": adhesive,
            "laminate": laminate,
            "cutting_method": cutting_method,
            "artworks": artworks,
            "labour_rate": labour_rate,
            "sqm_per_sticker": float(sqm_per_sticker),
            "total_sqm": float(total_sqm)
        }
        
        return CustomVinylStickersShopifyCalculatorQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            cost_per_item=unit_price,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    def _get_sqm_rate(self, total_sqm: float) -> Decimal:
        """Lookup rate from 51-tier SQM table"""
        for tier in self.SQM_RATES:
            if total_sqm <= tier["sqm_max"]:
                return Decimal(str(tier["rate"]))
        # Fallback to highest tier rate
        return Decimal(str(self.SQM_RATES[-1]["rate"]))
