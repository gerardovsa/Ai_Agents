"""
Metal Face A-Frame - Shopify Calculator
Created: January 25, 2026
Source: SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt lines 10408-10600

Formula from TXT:
    var rate = {F1} == 1 ? 197 : ({F1} == 2 ? 186 : ... 10 tiers)
    var subtotal = {F1} * {rate}
    var total = ({subtotal} + {F2}) * 1.1
    {total} * 1.1

NOTE: Formula adds artworks COUNT directly (same pattern as Pull Up Banners)
NOT artwork cost calculation like Strut Cards

Tier Structure (10 tiers):
- 1 unit: $197
- 2 units: $186
- 3 units: $179.55
- 4 units: $171.05
- 5 units: $165.80
- 6 units: $170.31 (unusual increase)
- 7 units: $166.41
- 8 units: $163.39
- 9 units: $160.96
- 10+ units: $159.35
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any

@dataclass
class CalculatorResult:
    """Result from Metal Face A-Frame calculator"""
    quantity: int
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    breakdown: Dict[str, Any]
    specifications: Dict[str, str]

class MetalFaceAFrameShopifyCalculator:
    """
    Metal Face A-Frame Calculator
    
    Formula: qty-based tier pricing (10 tiers) + artworks COUNT + ×1.1 ×1.1
    Note: Adds artwork count directly, not cost calculation
    """
    
    def __init__(self):
        """Initialize calculator with tier pricing data"""
        self.tiers = {
            1: Decimal("197"),
            2: Decimal("186"),
            3: Decimal("179.55"),
            4: Decimal("171.05"),
            5: Decimal("165.8"),
            6: Decimal("170.31"),  # Unusual: price increases at 6 units
            7: Decimal("166.41"),
            8: Decimal("163.39"),
            9: Decimal("160.96"),
            10: Decimal("159.35")
        }
    
    def _get_rate_for_quantity(self, quantity: int) -> Decimal:
        """
        Get tier rate based on quantity
        
        Args:
            quantity: Number of A-frames
            
        Returns:
            Rate per unit as Decimal
        """
        # Check exact quantity tiers (1-10)
        if quantity in self.tiers:
            return self.tiers[quantity]
        
        # 11+ uses same rate as 10
        if quantity >= 11:
            return self.tiers[10]
        
        # Fallback (shouldn't reach here)
        return self.tiers[10]
    
    def calculate(
        self,
        quantity: int,
        artworks: int = 1,
        size: str = "600mm W x 900mm H"
    ) -> CalculatorResult:
        """
        Calculate quote for Metal Face A-Frame
        
        Args:
            quantity: Number of A-frames (1-100)
            artworks: Number of artwork designs (1-20) - NOTE: Adds COUNT directly, not cost
            size: A-frame size (fixed: "600mm W x 900mm H")
            
        Returns:
            CalculatorResult with pricing breakdown
        """
        # Get tier rate for this quantity
        rate = self._get_rate_for_quantity(quantity)
        
        # Calculate subtotal (quantity × tier rate)
        subtotal = Decimal(quantity) * rate
        
        # UNUSUAL FORMULA: Add artworks COUNT directly (not artwork cost)
        # This matches TXT formula: var total = ({subtotal} + {F2}) * 1.1
        pre_markup_total = subtotal + Decimal(artworks)
        
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
            'pre_markup_total': pre_markup_total,
            'after_first_markup': after_first_markup,
            'first_markup': Decimal('1.1'),
            'final_markup': Decimal('1.1'),
            'total_price': total_price
        }
        
        specifications = {
            'size': size,
            'artworks': str(artworks),
            'quantity': str(quantity)
        }
        
        return CalculatorResult(
            quantity=quantity,
            total_price=total_price,
            unit_price=unit_price,
            cost_per_item=rate,  # Base tier rate per A-frame
            breakdown=breakdown,
            specifications=specifications
        )
