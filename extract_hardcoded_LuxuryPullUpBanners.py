"""
Extract Hardcoded Prices from Luxury Classic Pull Up Banners Shopify Calculator

Purpose: Document all hardcoded values from Python backend for JSON alignment
Calculator: LuxuryClassicPullUpBannersShopifyCalculator
Date: January 25, 2026
Source: backend/shopify_calculators/LuxuryClassicPullUpBanners_Shopify_Calculator.py
"""

print("=" * 80)
print("HARDCODED VALUES EXTRACTION - Luxury Classic Pull Up Banners")
print("=" * 80)
print()

print("## FORMULA CONSTANTS")
print("-" * 80)
print("Production Setup Cost: $15")
print("Artwork Cost: {F2} (artworks count)")
print("Markup: Double GST (× 1.1 × 1.1 = × 1.21)")
print()

print("## QUANTITY-BASED PRICING TIERS")
print("-" * 80)
print()

print("### SIZE: 850mm W x 2000mm H (Standard)")
print("-" * 40)
tiers_2000mm = [
    (1, 135.00),
    (2, 135.00),
    (3, 132.61),
    (4, 126.88),
    (5, 123.33),
    (6, 120.84),
    (7, 118.96),
    (8, 117.47),
    (9, 116.25),
    (10, 115.22),
    (11, 114.33),
    (12, 113.56),
    (13, 112.88),
    (14, 112.27),
    (15, 111.72),  # < 20
    (20, 109.60),  # < 25
    (25, 108.11),  # < 30
    (30, 106.99),  # < 35
    (35, 106.09),  # < 40
    (40, 105.35),  # < 45
    (45, 104.72),  # < 50
    (50, 104.18),  # < 55
    (55, 103.70),  # < 60
    (60, 103.28),  # < 65
    (65, 102.90),  # < 70
    (70, 102.60),  # >= 70
]

for qty, rate in tiers_2000mm:
    print(f"Quantity {qty:3d}: ${rate:.2f}")
print()

print("### SIZE: 850mm W x 1500mm H (Shopping Center)")
print("-" * 40)
tiers_1500mm = [
    (1, 128.00),
    (2, 128.00),
    (3, 125.74),
    (4, 120.30),
    (5, 116.94),
    (6, 114.57),
    (7, 112.80),
    (8, 111.38),
    (9, 110.23),
    (10, 109.25),
    (11, 108.40),
    (12, 107.68),
    (13, 107.03),
    (14, 107.45),  # Note: Higher than qty 13 (unique pricing)
    (15, 105.93),  # < 20
    (20, 103.91),  # < 25
    (25, 102.50),  # < 30
    (30, 101.44),  # < 35
    (35, 100.59),  # < 40
    (40, 99.89),   # < 45
    (45, 99.29),   # < 50
    (50, 98.78),   # < 55
    (55, 98.33),   # < 60
    (60, 97.92),   # < 65
    (65, 97.56),   # < 70
    (70, 97.28),   # >= 70
]

for qty, rate in tiers_1500mm:
    print(f"Quantity {qty:3d}: ${rate:.2f}")
print()

print("## CALCULATION FORMULA")
print("-" * 80)
print("var subtotal = {F1} * {rate};")
print("var total = ({subtotal} + {F2} + 15) * 1.1;")
print("{total} * 1.1")
print()
print("Where:")
print("  F1 = quantity")
print("  F2 = artworks count")
print("  rate = quantity-based tier lookup (different for 2000mm vs 1500mm)")
print("  15 = production setup cost")
print("  * 1.1 * 1.1 = double GST application")
print()

print("## PARAMETER OPTIONS")
print("-" * 80)
print("F1: Quantity (integer, > 0)")
print("F2: Artworks (integer, default 1)")
print("F3: Base Colour (options: Silver, Black)")
print("F4: Size (options: '850mm W x 2000mm H', '850mm W x 1500mm H (Shopping Center)')")
print()

print("## NOTES")
print("-" * 80)
print("- Size F4 determines which pricing tier table to use")
print("- Pattern match: '2000mm' in size → use 2000mm tiers")
print("- Pattern match: '1500mm' or 'Shopping Center' → use 1500mm tiers")
print("- Base colour F3 does NOT affect pricing (cosmetic choice)")
print("- Artwork count F2 adds directly to subtotal (not per-artwork pricing)")
print("- Setup cost $15 is flat fee per order (not per banner)")
print()

print("=" * 80)
print("EXTRACTION COMPLETE")
print("=" * 80)
