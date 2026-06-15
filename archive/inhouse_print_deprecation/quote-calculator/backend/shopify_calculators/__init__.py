"""
Shopify Calculators - Hardcoded Website Pricing
===============================================

These calculators replicate EXACT pricing from the Shopify website's
Dynamic Product Options (DPO) JavaScript. They use hardcoded pricing
tables and do NOT connect to the database.

Used ONLY for:
- Verifying website quote accuracy
- Pricing dashboard comparisons
- Website quote matching

DO NOT use for production orders - use GOD calculators instead.

Calculators:
- business_card_calculator_shopify.py: Standard business cards
- PremiumBusinessCards_Shopify_Calculator.py: Premium business cards with dual GST
- EconomicalBusinessCards_Shopify_Calculator.py: Budget business cards
- FoldedFlyers_Shopify_Calculator.py: Folded flyers and brochures (NEW - October 14, 2025)
- corflute_calculator_shopify.py: Corflute signs (website version)
- PerfectBound_Shopify_Calculator.py: Perfect bound books (website version)
- WireBound_Shopify_Calculator.py: Wire bound books
- SpiralBound_Shopify_Calculator.py: Spiral bound books
"""

from .business_card_calculator_shopify import ShopifyBusinessCardCalculator
from .corflute_calculator_shopify import CorflutePricingCalculatorShopify
from .PremiumBusinessCards_Shopify_Calculator import PremiumBusinessCardsShopifyCalculator
from .EconomicalBusinessCards_Shopify_Calculator import EconomicalBusinessCardsShopifyCalculator
from .FoldedFlyers_Shopify_Calculator import FoldedFlyersShopifyCalculator
from .PerfectBound_Shopify_Calculator import PerfectBoundShopifyCalculator
from .WireBound_Shopify_Calculator import WireBoundShopifyCalculator
from .SpiralBound_Shopify_Calculator import SpiralBoundBooksShopifyCalculator
from .NotepadsA5_Shopify_Calculator import NotepadsA5ShopifyCalculator

__all__ = [
    'ShopifyBusinessCardCalculator',
    'CorflutePricingCalculatorShopify',
    'PremiumBusinessCardsShopifyCalculator',
    'EconomicalBusinessCardsShopifyCalculator',
    'FoldedFlyersShopifyCalculator',
    'PerfectBoundShopifyCalculator',
    'WireBoundShopifyCalculator',
    'SpiralBoundBooksShopifyCalculator',
    'NotepadsA5ShopifyCalculator',
]
