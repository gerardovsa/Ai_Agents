"""
Test Bollard Signs Calculator - Shopify Formula Match
Created: January 23, 2026
Purpose: Validate calculator matches Shopify JavaScript formula EXACTLY

CRITICAL FIXES APPLIED:
1. SQM calculation: NO sides multiplier (was causing 3-4x inflation)
2. Artwork cost: First artwork FREE, then $5 per additional
3. NO GST in formula (Shopify displays Inc GST but formula doesn't include it)

Expected Shopify Prices (from user testing):
- TEST 2: 10 qty = $267.83 (should now match!)
- TEST 5: 100 qty = $1,762.80 (should now match!)
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))

from shopify_calculators.BollardSigns_Shopify_Calculator import BollardSignsShopifyCalculator
from decimal import Decimal


def format_price(price):
    """Format price to match Shopify display ($XXX.XX)"""
    return f"${price:.2f}"


print("=" * 80)
print("BOLLARD SIGNS - SHOPIFY FORMULA VALIDATION")
print("=" * 80)
print()

# Initialize calculator
calc = BollardSignsShopifyCalculator()

print("🔍 TESTING AGAINST SHOPIFY JAVASCRIPT FORMULA")
print("-" * 80)
print()

# TEST 1: Single sign - minimum order check
print("TEST 1: Minimum Order (1 sign)")
print("-" * 40)
result = calc.calculate(
    quantity=1,
    material='5mm Corflute',
    size='270mm W x 1000mm H - Three Sided',
    artworks=1
)
print(f"Quantity: 1")
print(f"Material: 5mm Corflute")
print(f"Size: 270mm W x 1000mm H - Three Sided")
print(f"Artworks: 1")
print()
print(f"SQM Calculation: {result.breakdown['area_per_sign_m2']:.4f} m² × 1 qty = {result.breakdown['total_sqm']:.2f} sqm")
print(f"  (NO sides multiplier! Fixed Jan 23, 2026)")
print(f"Price/sqm tier: ${result.breakdown['price_per_sqm']:.2f}")
print(f"Material cost: ${result.breakdown['material_cost']:.2f}")
print(f"Artwork cost: ${result.breakdown['artwork_setup_cost']:.2f} (first artwork FREE!)")
print(f"Business cost: ${result.breakdown['biz_cost']:.2f}")
print(f"Minimum applied: {result.breakdown['minimum_order_applied']} ($129 minimum)")
print(f"After 1.3x multiplier: ${result.breakdown['subtotal_with_multiplier']:.2f}")
print(f"TOTAL: {format_price(result.total_price)}")
print(f"  → Shopify shows Inc GST, but formula has NO GST")
print()

# TEST 2: Standard order - compare to Shopify actual price
print("TEST 2: Standard Order (10 signs) - SHOPIFY COMPARISON")
print("-" * 40)
result = calc.calculate(
    quantity=10,
    material='5mm Corflute',
    size='270mm W x 1000mm H - Three Sided',
    artworks=1
)
print(f"Quantity: 10")
print(f"Material: 5mm Corflute")
print(f"Size: 270mm W x 1000mm H - Three Sided")
print(f"Artworks: 1")
print()
print(f"SQM Calculation: 0.91 m² × 10 qty = {result.breakdown['total_sqm']:.2f} sqm")
print(f"  (Old calculation with sides: 0.91 × 10 × 3 = 27.30 sqm ❌ WRONG)")
print(f"Price/sqm tier: ${result.breakdown['price_per_sqm']:.2f}")
print(f"Material cost: ${result.breakdown['material_cost']:.2f}")
print(f"Artwork cost: ${result.breakdown['artwork_setup_cost']:.2f}")
print(f"Business cost: ${result.breakdown['biz_cost']:.2f}")
print(f"After 1.3x: ${result.breakdown['subtotal_with_multiplier']:.2f}")
print(f"OUR PRICE: {format_price(result.total_price)}")
print(f"SHOPIFY ACTUAL: $267.83 Inc GST")
print()
# Calculate with Shopify GST to compare
our_with_gst = result.total_price * Decimal('1.1')
print(f"If we add GST (×1.1): ${our_with_gst:.2f}")
print(f"Match? {abs(our_with_gst - Decimal('267.83')) < 1}")
print()

# TEST 3: Large order
print("TEST 3: Large Order (100 signs) - SHOPIFY COMPARISON")
print("-" * 40)
result = calc.calculate(
    quantity=100,
    material='5mm Corflute',
    size='300mm W x 1000mm H - Three Sided',
    artworks=1
)
print(f"Quantity: 100")
print(f"Material: 5mm Corflute")
print(f"Size: 300mm W x 1000mm H - Three Sided")
print(f"Artworks: 1")
print()
print(f"SQM Calculation: 1.00 m² × 100 qty = {result.breakdown['total_sqm']:.2f} sqm")
print(f"  (Old calculation with sides: 1.00 × 100 × 3 = 300.00 sqm ❌ WRONG)")
print(f"Price/sqm tier: ${result.breakdown['price_per_sqm']:.2f}")
print(f"Material cost: ${result.breakdown['material_cost']:.2f}")
print(f"Artwork cost: ${result.breakdown['artwork_setup_cost']:.2f}")
print(f"After 1.3x: ${result.breakdown['subtotal_with_multiplier']:.2f}")
print(f"OUR PRICE: {format_price(result.total_price)} (ex GST)")
print(f"SHOPIFY ACTUAL: $1,762.80 Inc GST")
print()
our_with_gst = result.total_price * Decimal('1.1')
print(f"If we add GST (×1.1): ${our_with_gst:.2f}")
print(f"Match? {abs(our_with_gst - Decimal('1762.80')) < 1}")
print()

# TEST 4: Artwork cost validation
print("TEST 4: Artwork Cost Formula")
print("-" * 40)
print("Testing first artwork FREE, then $5 per additional")
print()

for art_count in [1, 2, 3, 5, 10]:
    result = calc.calculate(
        quantity=10,
        material='5mm Corflute',
        size='270mm W x 1000mm H - Three Sided',
        artworks=art_count
    )
    _a = art_count * 5
    expected = 0 if _a <= 5 else (_a - 5)
    match = "✅" if result.breakdown['artwork_setup_cost'] == expected else "❌"
    print(f"{art_count} artworks: ${result.breakdown['artwork_setup_cost']:.2f} (expected ${expected:.2f}) {match}")

print()

# TEST 5: Material pricing difference
print("TEST 5: 3mm vs 5mm Material Pricing")
print("-" * 40)

result_3mm = calc.calculate(
    quantity=10,
    material='3mm Corflute',
    size='270mm W x 1000mm H - Three Sided',
    artworks=1
)

result_5mm = calc.calculate(
    quantity=10,
    material='5mm Corflute',
    size='270mm W x 1000mm H - Three Sided',
    artworks=1
)

print(f"3mm Corflute: {format_price(result_3mm.total_price)} @ ${result_3mm.breakdown['price_per_sqm']:.2f}/sqm")
print(f"5mm Corflute: {format_price(result_5mm.total_price)} @ ${result_5mm.breakdown['price_per_sqm']:.2f}/sqm")
difference_pct = ((result_5mm.total_price - result_3mm.total_price) / result_3mm.total_price) * 100
print(f"5mm is {difference_pct:.1f}% more expensive")
print()

# TEST 6: Tier pricing progression
print("TEST 6: Tier Pricing Progression")
print("-" * 40)
print("Verifying price/sqm decreases with volume (NO sides multiplier)")
print()

test_quantities = [1, 5, 10, 25, 50, 100]
for qty in test_quantities:
    result = calc.calculate(
        quantity=qty,
        material='5mm Corflute',
        size='270mm W x 1000mm H - Three Sided',
        artworks=1
    )
    print(f"{qty:3d} signs: {result.breakdown['total_sqm']:6.2f} sqm → ${result.breakdown['price_per_sqm']:5.2f}/sqm → {format_price(result.total_price):>9s} total")

print()
print("=" * 80)
print("✅ FORMULA CORRECTIONS APPLIED:")
print("   1. SQM = area × quantity (NO sides multiplier)")
print("   2. First artwork FREE (was $5)")
print("   3. NO GST in formula (Shopify displays Inc GST separately)")
print()
print("🎯 NEXT STEP: Compare to Shopify prices")
print("   - If prices still don't match, check Shopify's actual tier values")
print("   - Shopify may have updated pricing since JSON was created")
print("=" * 80)
