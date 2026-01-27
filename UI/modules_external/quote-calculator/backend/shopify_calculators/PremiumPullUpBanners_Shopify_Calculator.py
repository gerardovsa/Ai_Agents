"""
Premium Pull Up Banners - Shopify Calculator
Created: January 25, 2026
Source: SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt lines 9430-9870

Formula from TXT:
    var rate = {f4} == '850mm W x 2000mm H' ? (25 tiers for 2000mm) : (25 tiers for other sizes)
    var subtotal = {F1} * {rate}
    var total = ({subtotal} + {F2} + 15) * 1.1
    {total} * 1.1

NOTE: Formula adds artworks COUNT directly (not artwork cost calculation)
This is the same unusual pattern as Luxury Classic Pull Up Banners

Tier Structure:
- 850×2000mm: $97 (qty 1-2) down to $73.72 (qty 70+)
- Other sizes (1500mm, 1400mm): $90 (qty 1-2) down to $68.40 (qty 70+)
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any

@dataclass
class CalculatorResult:
    """Result from Premium Pull Up Banners calculator"""
    quantity: int
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    breakdown: Dict[str, Any]
    specifications: Dict[str, str]

class PremiumPullUpBannersShopifyCalculator:
    """
    Premium Pull Up Banners Calculator
    
    Formula: qty-based tier pricing + artworks COUNT + $15 setup + ×1.1 ×1.1
    Note: Adds artwork count directly, not cost calculation
    """
    
    def __init__(self):
        """Initialize calculator with tier pricing data"""
        # Tier pricing for 850×2000mm size
        self.tiers_2000mm = {
            1: Decimal("97"), 2: Decimal("97"), 3: Decimal("95.28"),
            4: Decimal("91.16"), 5: Decimal("88.61"), 6: Decimal("86.83"),
            7: Decimal("85.47"), 8: Decimal("84.4"), 9: Decimal("83.52"),
            10: Decimal("82.78"), 11: Decimal("82.15"), 12: Decimal("81.59"),
            13: Decimal("81.1"), 14: Decimal("80.67")
        }
        
        # Range-based tiers for 2000mm (15-70+)
        self.range_tiers_2000mm = [
            (15, 19, Decimal("80.27")), (20, 24, Decimal("78.75")),
            (25, 29, Decimal("77.68")), (30, 34, Decimal("76.87")),
            (35, 39, Decimal("76.23")), (40, 44, Decimal("75.69")),
            (45, 49, Decimal("75.24")), (50, 54, Decimal("74.85")),
            (55, 59, Decimal("74.51")), (60, 64, Decimal("74.21")),
            (65, 69, Decimal("73.94")), (70, 999, Decimal("73.72"))
        ]
        
        # Tier pricing for other sizes (1500mm, 1400mm)
        self.tiers_other = {
            1: Decimal("90"), 2: Decimal("90"), 3: Decimal("88.41"),
            4: Decimal("84.58"), 5: Decimal("82.22"), 6: Decimal("80.56"),
            7: Decimal("79.31"), 8: Decimal("78.31"), 9: Decimal("77.5"),
            10: Decimal("76.81"), 11: Decimal("76.22"), 12: Decimal("75.71"),
            13: Decimal("75.25"), 14: Decimal("75.85")
        }
        
        # Range-based tiers for other sizes (15-70+)
        self.range_tiers_other = [
            (15, 19, Decimal("74.48")), (20, 24, Decimal("73.06")),
            (25, 29, Decimal("72.07")), (30, 34, Decimal("71.32")),
            (35, 39, Decimal("70.73")), (40, 44, Decimal("70.23")),
            (45, 49, Decimal("69.81")), (50, 54, Decimal("69.45")),
            (55, 59, Decimal("69.14")), (60, 64, Decimal("68.85")),
            (65, 69, Decimal("68.6")), (70, 999, Decimal("68.4"))
        ]
    
    def _get_rate_for_quantity(self, quantity: int, size: str) -> Decimal:
        """
        Get tier rate based on quantity and size
        
        Args:
            quantity: Number of banners
            size: Banner size (determines tier group)
            
        Returns:
            Rate per unit as Decimal
        """
        # Determine which tier set to use
        is_2000mm = size == "850mm W x 2000mm H"
        tiers = self.tiers_2000mm if is_2000mm else self.tiers_other
        range_tiers = self.range_tiers_2000mm if is_2000mm else self.range_tiers_other
        
        # Check exact quantity tiers first (1-14)
        if quantity in tiers:
            return tiers[quantity]
        
        # Check range-based tiers (15-70+)
        for min_qty, max_qty, rate in range_tiers:
            if min_qty <= quantity <= max_qty:
                return rate
        
        # Fallback to highest tier rate (shouldn't reach here)
        return range_tiers[-1][2]
    
    def calculate(
        self,
        quantity: int,
        size: str = "850mm W x 2000mm H",
        base_colour: str = "Silver",
        artworks: int = 1
    ) -> CalculatorResult:
        """
        Calculate quote for Premium Pull Up Banners
        
        Args:
            quantity: Number of banners (1-100)
            size: Banner size - "850mm W x 2000mm H", "850mm W x 1500mm H", or "850mm W x 1400mm H Shopping Center"
            base_colour: Base finish - "Silver" or "Black" (cosmetic only, no price difference)
            artworks: Number of artwork designs (1-20) - NOTE: Adds COUNT directly, not cost
            
        Returns:
            CalculatorResult with pricing breakdown
        """
        # Get tier rate for this quantity and size
        rate = self._get_rate_for_quantity(quantity, size)
        
        # Calculate subtotal (quantity × tier rate)
        subtotal = Decimal(quantity) * rate
        
        # UNUSUAL FORMULA: Add artworks COUNT directly (not artwork cost)
        # This matches TXT formula: var total = ({subtotal} + {F2} + 15) * 1.1
        pre_markup_total = subtotal + Decimal(artworks) + Decimal('15')
        
        # Apply double markup (×1.1 ×1.1)
        after_first_markup = pre_markup_total * Decimal('1.1')
        total_price = after_first_markup * Decimal('1.1')
        
        # Round to 2 decimal places
        total_price = total_price.quantize(Decimal('0.01'))
        unit_price = (total_price / Decimal(quantity)).quantize(Decimal('0.01'))
        
        breakdown = {
            'rate': rate,
            'subtotal': subtotal,
            'artworks_added': Decimal(artworks),  # COUNT added directly
            'production_setup': Decimal('15'),
            'pre_markup_total': pre_markup_total,
            'after_first_markup': after_first_markup,
            'first_markup': Decimal('1.1'),
            'final_markup': Decimal('1.1'),
            'total_price': total_price
        }
        
        specifications = {
            'size': size,
            'base_colour': base_colour,
            'artworks': str(artworks),
            'quantity': str(quantity)
        }
        
        return CalculatorResult(
            quantity=quantity,
            total_price=total_price,
            unit_price=unit_price,
            cost_per_item=rate,  # Base tier rate per banner
            breakdown=breakdown,
            specifications=specifications
        )
