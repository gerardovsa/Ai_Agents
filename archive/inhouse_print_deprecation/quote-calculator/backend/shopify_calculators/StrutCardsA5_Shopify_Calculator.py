"""
Strut Cards A5 Shopify Calculator
Exact implementation from SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt

Formula:
  _a = artworks × 5
  _a2 = IF _a ≤ 5 THEN 0 ELSE (_a - 5)
  _up = quantity-based tier pricing (25 tiers)
  subTotal = (quantity × _up) + _a2
  total = IF subTotal < 79 THEN 79 ELSE (subTotal × 1.1)
  final = total × 1.2  (A5-specific: 20% final markup)

Created: January 25, 2026
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class StrutCardsA5ShopifyCalculatorQuoteResult:
    """Result from Strut Cards A5 Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class StrutCardsA5ShopifyCalculator:
    """
    Strut Cards A5 Shopify Calculator - Exact TXT Formula Implementation
    
    Formula: quantity-tier pricing + artwork costs + $79 minimum + double markup (×1.1 ×1.2)
    """
    
    # 25-tier quantity pricing (from TXT - A5 specific)
    QUANTITY_TIERS = [
        {"qty_min": 1, "qty_max": 9, "price": Decimal("5.5")},
        {"qty_min": 10, "qty_max": 14, "price": Decimal("5.5")},
        {"qty_min": 15, "qty_max": 19, "price": Decimal("4.5")},
        {"qty_min": 20, "qty_max": 24, "price": Decimal("4.45")},
        {"qty_min": 25, "qty_max": 29, "price": Decimal("4.4")},
        {"qty_min": 30, "qty_max": 34, "price": Decimal("4.4")},
        {"qty_min": 35, "qty_max": 39, "price": Decimal("4.35")},
        {"qty_min": 40, "qty_max": 44, "price": Decimal("4.3")},
        {"qty_min": 45, "qty_max": 49, "price": Decimal("4.25")},
        {"qty_min": 50, "qty_max": 59, "price": Decimal("4.15")},
        {"qty_min": 60, "qty_max": 69, "price": Decimal("4.1")},
        {"qty_min": 70, "qty_max": 79, "price": Decimal("4.08")},
        {"qty_min": 80, "qty_max": 89, "price": Decimal("4.05")},
        {"qty_min": 90, "qty_max": 99, "price": Decimal("3.7")},
        {"qty_min": 100, "qty_max": 124, "price": Decimal("3.42")},
        {"qty_min": 125, "qty_max": 149, "price": Decimal("3.2")},
        {"qty_min": 150, "qty_max": 174, "price": Decimal("3.08")},
        {"qty_min": 175, "qty_max": 199, "price": Decimal("3.03")},
        {"qty_min": 200, "qty_max": 249, "price": Decimal("2.99")},
        {"qty_min": 250, "qty_max": 299, "price": Decimal("2.93")},
        {"qty_min": 300, "qty_max": 399, "price": Decimal("2.9")},
        {"qty_min": 400, "qty_max": 499, "price": Decimal("2.89")},
        {"qty_min": 500, "qty_max": 749, "price": Decimal("2.87")},
        {"qty_min": 750, "qty_max": 999, "price": Decimal("2.86")},
        {"qty_min": 1000, "qty_max": 999999, "price": Decimal("2.85")}
    ]
    
    MINIMUM_ORDER = Decimal("79")
    INITIAL_MARKUP = Decimal("1.1")
    FINAL_MARKUP = Decimal("1.2")  # A5-specific: 20% final markup
    
    def __init__(self):
        """Initialize Strut Cards A5 Shopify calculator"""
        pass
    
    def calculate(
        self,
        quantity: int,
        artworks: int = 1,
        **kwargs
    ) -> StrutCardsA5ShopifyCalculatorQuoteResult:
        """
        Calculate Strut Cards A5 Shopify quote
        
        Args:
            quantity: Number of strut cards (1-10000)
            artworks: Number of artwork designs (1-20)
        
        Returns:
            StrutCardsA5ShopifyCalculatorQuoteResult with pricing details
        """
        # Handle legacy parameter names
        if 'qty' in kwargs and quantity is None:
            quantity = int(kwargs['qty'])
        if 'art' in kwargs and artworks == 1:
            artworks = int(kwargs['art'])
        
        # Step 1: Calculate artwork cost
        _a = Decimal(artworks) * Decimal("5")
        if _a <= Decimal("5"):
            artwork_cost = Decimal("0")
        else:
            artwork_cost = _a - Decimal("5")
        
        # Step 2: Get unit price from quantity tiers
        unit_price = self._get_unit_price(quantity)
        
        # Step 3: Calculate subtotal
        subtotal = (Decimal(quantity) * unit_price) + artwork_cost
        
        # Step 4: Apply minimum order rule + first markup
        if subtotal < self.MINIMUM_ORDER:
            total_after_first_markup = self.MINIMUM_ORDER
        else:
            total_after_first_markup = subtotal * self.INITIAL_MARKUP
        
        # Step 5: Apply final markup (A5-specific: ×1.2)
        total_price = total_after_first_markup * self.FINAL_MARKUP
        total_price = total_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Calculate per-unit pricing
        unit_price_final = total_price / Decimal(quantity)
        
        # Build breakdown (match A3/A4 format)
        breakdown = {
            "artwork_cost": artwork_cost,
            "unit_price": unit_price,
            "subtotal": subtotal,
            "minimum_applied": subtotal < self.MINIMUM_ORDER,
            "total_after_first_markup": total_after_first_markup,
            "initial_markup": self.INITIAL_MARKUP,
            "final_markup": self.FINAL_MARKUP,
            "total_price": total_price
        }
        
        # Build specifications
        specifications = {
            "quantity": quantity,
            "artworks": artworks,
            "size": "A5 - 148mm x 210mm",
            "stock": "2mm Screenboard"
        }
        
        return StrutCardsA5ShopifyCalculatorQuoteResult(
            total_price=total_price,
            unit_price=unit_price_final,
            cost_per_item=unit_price_final,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    def _get_unit_price(self, quantity: int) -> Decimal:
        """Lookup unit price from 25-tier quantity table"""
        for tier in self.QUANTITY_TIERS:
            if tier["qty_min"] <= quantity <= tier["qty_max"]:
                return tier["price"]
        # Fallback to highest tier
        return self.QUANTITY_TIERS[-1]["price"]
