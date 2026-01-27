"""
Strut Cards A3 Shopify Calculator
Exact implementation from SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt

Formula:
- Artwork cost: _a = artworks × 5; _a2 = IF _a ≤ 5 THEN 0 ELSE (_a - 5)
- Unit price: 25 quantity-based tiers (A3: $16 → $5.42)
- Subtotal: (quantity × unit_price) + _a2
- Minimum order: IF subtotal < $79 THEN $79
- First markup: IF above minimum THEN subtotal × 1.1
- Final markup: × 1.1 (A3-specific)

Size: A3 - 297mm × 420mm
Stock: 2mm Screenboard
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class StrutCardsA3ShopifyCalculatorQuoteResult:
    """Result from Strut Cards A3 Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class StrutCardsA3ShopifyCalculator:
    """
    Strut Cards A3 Shopify Calculator - Exact TXT Formula Implementation
    
    25-tier quantity pricing (A3 rates: $16 → $5.42)
    Artwork cost: First $5 included, then $5 each additional
    Minimum order: $79
    Double markup: ×1.1 (initial) then ×1.1 (A3 final)
    """
    
    # A3-specific 25-tier quantity pricing (CORRECTED from TXT)
    QUANTITY_TIERS = [
        (1, 9, Decimal("16")),       # 1-9
        (10, 14, Decimal("16")),     # 10-14
        (15, 19, Decimal("12")),     # 15-19
        (20, 24, Decimal("11.8")),   # 20-24
        (25, 29, Decimal("11.6")),   # 25-29
        (30, 34, Decimal("11.6")),   # 30-34
        (35, 39, Decimal("11.4")),   # 35-39
        (40, 44, Decimal("11.2")),   # 40-44
        (45, 49, Decimal("11")),     # 45-49
        (50, 59, Decimal("10.6")),   # 50-59
        (60, 69, Decimal("10.4")),   # 60-69
        (70, 79, Decimal("10.32")),  # 70-79
        (80, 89, Decimal("10.2")),   # 80-89
        (90, 99, Decimal("8.8")),    # 90-99
        (100, 124, Decimal("7.7")),  # 100-124 (CORRECTED: was 9.50)
        (125, 149, Decimal("6.8")),  # 125-149 (CORRECTED: was 9.00)
        (150, 174, Decimal("6.32")), # 150-174 (CORRECTED: was 9.00)
        (175, 199, Decimal("6.14")), # 175-199 (CORRECTED: was 8.50)
        (200, 249, Decimal("5.98")), # 200-249 (CORRECTED: was 8.00)
        (250, 299, Decimal("5.72")), # 250-299 (CORRECTED: was 7.50)
        (300, 399, Decimal("5.6")),  # 300-399 (CORRECTED: was 7.00)
        (400, 499, Decimal("5.56")), # 400-499 (CORRECTED: was 6.60)
        (500, 749, Decimal("5.5")),  # 500-749 (CORRECTED: was 6.30)
        (750, 999, Decimal("5.46")), # 750-999 (CORRECTED: was 5.80)
        (1000, float('inf'), Decimal("5.42"))  # 1000+
    ]
    
    MINIMUM_ORDER = Decimal("79")
    INITIAL_MARKUP = Decimal("1.1")   # First markup
    FINAL_MARKUP = Decimal("1.1")     # A3-specific final markup
    
    def __init__(self):
        """Initialize Strut Cards A3 Shopify calculator"""
        pass
    
    def calculate(self, **kwargs) -> StrutCardsA3ShopifyCalculatorQuoteResult:
        """
        Calculate Strut Cards A3 quote using exact TXT formula
        
        Args:
            quantity (int): Number of strut cards (1-10000)
            artworks (int): Number of artworks (1-20), default 1
        
        Returns:
            StrutCardsA3ShopifyCalculatorQuoteResult with pricing details
        """
        # Get parameters (with legacy support)
        quantity = int(kwargs.get('quantity', kwargs.get('qty', 100)))
        artworks = int(kwargs.get('artworks', kwargs.get('art', 1)))

        if quantity <= 0:
            raise ValueError('Quantity must be > 0')
        if artworks < 1:
            raise ValueError('Artworks must be >= 1')

        # Step 1: Calculate artwork cost
        # Formula: _a = artworks × 5; _a2 = IF _a ≤ 5 THEN 0 ELSE (_a - 5)
        _a = Decimal(artworks) * Decimal("5")
        if _a <= Decimal("5"):
            artwork_cost = Decimal("0")
        else:
            artwork_cost = _a - Decimal("5")

        # Step 2: Get unit price from quantity tiers
        unit_price = self._get_unit_price(quantity)

        # Step 3: Calculate subtotal
        # Formula: (quantity × unit_price) + artwork_cost
        subtotal = (Decimal(quantity) * unit_price) + artwork_cost

        # Step 4: Apply minimum order rule + first markup
        # Formula: IF subtotal < $79 THEN $79 ELSE (subtotal × 1.1)
        if subtotal < self.MINIMUM_ORDER:
            total_after_first_markup = self.MINIMUM_ORDER
        else:
            total_after_first_markup = subtotal * self.INITIAL_MARKUP

        # Step 5: Apply final markup (A3-specific: ×1.1)
        total_price = total_after_first_markup * self.FINAL_MARKUP
        total_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        unit_price_final = total_price / Decimal(quantity)

        breakdown = {
            'artwork_cost': artwork_cost,
            'unit_price': unit_price,
            'subtotal': subtotal,
            'minimum_applied': subtotal < self.MINIMUM_ORDER,
            'total_after_first_markup': total_after_first_markup,
            'initial_markup': self.INITIAL_MARKUP,
            'final_markup': self.FINAL_MARKUP,
            'total_price': total_price,
        }

        specifications = {
            'quantity': quantity,
            'artworks': artworks,
            'size': 'A3 - 297mm x 420mm',
            'stock': '2mm Screenboard'
        }

        return StrutCardsA3ShopifyCalculatorQuoteResult(
            total_price=total_price,
            unit_price=unit_price_final,
            cost_per_item=unit_price_final,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    def _get_unit_price(self, quantity: int) -> Decimal:
        """Get unit price from A3 quantity tiers"""
        for min_qty, max_qty, price in self.QUANTITY_TIERS:
            if min_qty <= quantity <= max_qty:
                return price
        return self.QUANTITY_TIERS[-1][2]  # Return highest tier if not found
