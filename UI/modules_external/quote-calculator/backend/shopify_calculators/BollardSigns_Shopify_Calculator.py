"""
Bollard Signs Shopify Calculator
Exact implementation of Shopify JavaScript formula for Bollard Signs

Based on: Shopify_Bollard_Signs.json specification
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
class BollardSignsShopifyCalculatorQuoteResult:
    """Result from Bollard Signs Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class BollardSignsShopifyCalculator:
    """
    Bollard Signs Shopify Calculator - Exact Shopify JavaScript Implementation
    
    SHOPIFY-SPECIFIC CALCULATOR - SEPARATE FROM WOOCOMMERCE
    
    Features:
    - 4-field Shopify structure
    - Tiered padding rates (0 tiers)
    - Tiered profit margins (0 tiers)
    - Artwork setup costs
    - DOUBLE GST APPLICATION (Shopify-specific: Total * 1.1 * 1.1)
    """
    
    CONFIG_FILE = "Shopify_Bollard_Signs.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Bollard Signs Shopify calculator"""
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
    
    def calculate(self, **kwargs) -> BollardSignsShopifyCalculatorQuoteResult:
        """
        Calculate Bollard Signs Shopify quote
        
        ✅ FIXED JAN 23, 2026 (RE-AUDIT): Now implements JSON specification correctly
        - 42-tier pricing per material (not fixed rates)
        - Correct setup costs ($5 base + $5 per extra artwork)
        - Final multiplier (1.3x before GST)
        - Minimum order check ($129)
        - JSON dimensions mapping
        
        Args:
            **kwargs: Calculator parameters from JSON config
                quantity: Number of signs (1-1000)
                material: "3mm Corflute" or "5mm Corflute" (JSON format)
                size: "270mm W x 1000mm H - Three Sided" format (JSON format)
                artworks: Number of artwork designs (1-20)
        
        Returns:
            BollardSignsShopifyCalculatorQuoteResult with pricing details
        """
        import re
        
        quantity = int(kwargs.get('quantity', kwargs.get('qty', 1)))
        size_raw = kwargs.get('size', '270mm W x 1000mm H - Three Sided')  # JSON default
        material_raw = kwargs.get('material', '5mm Corflute')  # JSON default
        artworks = int(kwargs.get('artworks', 1))

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')

        # ✅ Get dimensions from JSON mapping first
        if self.config and 'shopify_bollard_signs' in self.config:
            dimensions_map = self.config['shopify_bollard_signs'].get('size_dimensions', {})
            if size_raw in dimensions_map:
                dims = dimensions_map[size_raw]
                width_mm = Decimal(str(dims['width']))
                height_mm = Decimal(str(dims['height']))
                area_m2 = (width_mm * height_mm) / Decimal('1000000')
            else:
                # Fallback to regex parsing
                match = re.search(r'(\d+)mm\s*W\s*x\s*(\d+)mm\s*H', size_raw, re.IGNORECASE)
                if match:
                    width_mm = Decimal(match.group(1))
                    height_mm = Decimal(match.group(2))
                    area_m2 = (width_mm * height_mm) / Decimal('1000000')
                else:
                    raise ValueError(f"Cannot parse size: {size_raw}")
        else:
            # No config - use regex parsing
            match = re.search(r'(\d+)mm\s*W\s*x\s*(\d+)mm\s*H', size_raw, re.IGNORECASE)
            if match:
                width_mm = Decimal(match.group(1))
                height_mm = Decimal(match.group(2))
                area_m2 = (width_mm * height_mm) / Decimal('1000000')
            else:
                raise ValueError(f"Cannot parse size: {size_raw}")
        
        # Extract sides from size description
        if 'Four Sided' in size_raw or 'four sided' in size_raw.lower():
            sides = 'Four'
            sides_multiplier = Decimal('4')
        else:
            sides = 'Three'
            sides_multiplier = Decimal('3')

        # ✅ RE-FIXED JAN 26, 2026: RESTORED sides multiplier (was incorrectly removed Jan 23)
        # Validation specs confirm: total_sqm = area × quantity × sides
        # Example: 0.91 m² × 1 qty × 3 sides = 2.73 sqm (matches Shopify formula)
        total_sqm = area_m2 * Decimal(quantity) * sides_multiplier
        
        # ✅ Get tiered price per sqm from JSON
        price_per_sqm = self._get_price_per_sqm(total_sqm, material_raw)
        
        # ✅ Calculate material cost using tiered pricing
        material_cost = total_sqm * price_per_sqm

        # ✅ Get setup costs from JSON constants
        if self.config and 'shopify_bollard_signs' in self.config:
            constants = self.config['shopify_bollard_signs']['pricing_constants']
            artwork_base = Decimal(str(constants['setup_costs']['artwork_base_cost']))  # $5
            extra_artwork = Decimal(str(constants['setup_costs']['extra_artwork_cost']))  # $5
            minimum_order = Decimal(str(constants['minimum_order']['value']))  # $129
            final_multiplier = Decimal(str(constants['final_multiplier']['rate']))  # 1.3
        else:
            # Fallback if no config
            artwork_base = Decimal('5')
            extra_artwork = Decimal('5')
            minimum_order = Decimal('129')
            final_multiplier = Decimal('1.3')
        
        # ✅ FIXED JAN 26, 2026: Corrected artwork cost formula
        # Validation specs: "$5 base + $5 per extra" = $5 + (art-1) × $5
        # Example: 1 artwork = $5, 3 artworks = $5 + (3-1)×$5 = $15
        # OLD (incorrect): "First FREE, then $5 each" = (art × 5) - 5
        artwork_setup_cost = artwork_base + (Decimal(artworks) - Decimal('1')) * extra_artwork

        # Calculate costs
        impos_setup = Decimal('0')  # No imposition setup in JSON formula
        print_cost = Decimal('0')  # Included in material_cost via sqm pricing
        installation_preparation = Decimal('0')  # Not in JSON formula

        # Business cost = material + setup
        biz_cost = material_cost + artwork_setup_cost

        # ✅ Apply minimum order
        if biz_cost < minimum_order:
            biz_cost = minimum_order

        # ✅ RE-FIXED JAN 26, 2026: RESTORED double GST (was incorrectly removed Jan 23)
        # Validation specs confirm: After multiplier × 1.1 × 1.1
        # Example: $129 × 1.3 × 1.1 × 1.1 = $202.92 (matches Shopify formula)
        subtotal_with_multiplier = biz_cost * final_multiplier
        after_first_gst = subtotal_with_multiplier * Decimal('1.1')
        total_price = (after_first_gst * Decimal('1.1')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        unit_price = total_price / Decimal(quantity)

        breakdown = {
            'area_per_sign_m2': area_m2,
            'sides_multiplier': sides_multiplier,  # Used in calculation
            'total_sqm': total_sqm,  # WITH sides multiplier (0.91 × qty × 3)
            'price_per_sqm': price_per_sqm,
            'material_cost': material_cost,
            'artwork_setup_cost': artwork_setup_cost,  # $5 base + $5 per extra
            'biz_cost': biz_cost,
            'minimum_order_applied': biz_cost == minimum_order,
            'final_multiplier': final_multiplier,
            'subtotal_with_multiplier': subtotal_with_multiplier,
            'after_first_gst': after_first_gst,
            'total_price': total_price,  # After double GST (×1.1 ×1.1)
        }

        specifications = {
            'quantity': quantity,
            'size': size_raw,
            'material': material_raw,
            'sides': sides,
            'area_m2': float(area_m2),
            'total_sqm': float(total_sqm),
            'artworks': artworks
        }

        return BollardSignsShopifyCalculatorQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            cost_per_item=unit_price,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    def _get_price_per_sqm(self, total_sqm: Decimal, material: str) -> Decimal:
        """
        Get tiered price per square meter from Shopify formula
        
        Args:
            total_sqm: Total square meters (area × quantity) - NO sides multiplier!
            material: "3mm Corflute" or "5mm Corflute"
        
        Returns:
            Price per sqm based on tier (42 tiers per material)
        """
        # Determine tier key
        if '3mm' in material:
            tier_key = '3mm_corflute'
        elif '5mm' in material:
            tier_key = '5mm_corflute'
        else:
            raise ValueError(f"Unknown material: {material}")
        
        # Get tiers from config
        if not self.config or 'shopify_bollard_signs' not in self.config:
            # Fallback to fixed rates if no config
            return Decimal('28.00') if '5mm' in material else Decimal('24.00')
        
        tiers = self.config['shopify_bollard_signs']['material_pricing_tiers'][tier_key]
        
        # Find matching tier
        total_sqm_float = float(total_sqm)
        for tier in tiers:
            if total_sqm_float <= tier['sqm_max']:
                return Decimal(str(tier['price_per_sqm']))
        
        # Fallback to last tier if beyond max
        return Decimal(str(tiers[-1]['price_per_sqm']))
    
    def _get_padding_rate(self, quantity: int) -> Decimal:
        """Get padding rate (no tiers defined)"""
        return Decimal('0.10')
    
    def _get_profit_margin(self, subtotal: float) -> Decimal:
        """Get profit margin (no tiers defined)"""
        return Decimal('0.50')
