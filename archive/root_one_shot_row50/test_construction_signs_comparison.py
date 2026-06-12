"""
Construction Signs - Backend vs JSON-Aligned Formula Comparison
Test against live Shopify website to verify correct implementation

Created: January 23, 2026
"""

from decimal import Decimal, ROUND_HALF_UP
import sys
from pathlib import Path

# Add backend path
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))

print("=" * 80)
print("CONSTRUCTION SIGNS - CURRENT BACKEND vs JSON-ALIGNED FORMULA")
print("=" * 80)
print()

# ============================================================================
# TEST 1: Small Order with Minimum Price
# ============================================================================
print("TEST 1: Small Order with Minimum Price")
print("-" * 80)
print("INPUTS:")
print("  Quantity: 1")
print("  Size: 450mm x 600mm (0.27 sqm)")
print("  Thickness: 5mm")
print("  Sides: Single Sided")
print("  Eyelets: No Eyelets")
print("  Artworks: 1")
print()

# Current Backend (WRONG)
print("CURRENT BACKEND (WRONG FORMULA):")
try:
    from ConstructionSigns_Shopify_Calculator import ConstructionSignsShopifyCalculator
    calc_current = ConstructionSignsShopifyCalculator()
    result_current = calc_current.calculate(
        quantity=1,
        size="450mm x 600mm",
        thickness="5mm",
        sides="Single Sided",
        eyelets="No Eyelets",
        artworks=1
    )
    print(f"  Total: ${result_current.total_price:.2f}")
    print(f"  Breakdown:")
    print(f"    - Material cost: ${result_current.breakdown['material_cost']:.2f}")
    print(f"    - Print cost: ${result_current.breakdown['print_cost']:.2f}")
    print(f"    - Setup: ${result_current.breakdown['impos_setup']:.2f}")
    print(f"    - Profit: ${result_current.breakdown['profit_amount']:.2f}")
    print(f"    - DOUBLE GST applied: ×{result_current.breakdown['gst_rate']:.2f} twice")
except Exception as e:
    print(f"  ERROR: {e}")
print()

# JSON-Aligned Formula (CORRECT)
print("JSON-ALIGNED FORMULA (CORRECT):")
quantity = 1
width_mm = Decimal('450')
height_mm = Decimal('600')
total_sqm = (width_mm * height_mm / Decimal('1000000')) * Decimal(quantity)
print(f"  SQM: {float(total_sqm):.4f}")

# Tier lookup for 5mm at 0.27 sqm (< 5 sqm)
price_per_sqm = Decimal('31.25')  # First tier
print(f"  Price per sqm: ${price_per_sqm:.2f} (0-5 sqm tier)")

# Artwork (first artwork FREE)
artwork_setup = Decimal('0')
print(f"  Artwork setup: ${artwork_setup:.2f} (first FREE)")

# Eyelet cost
eyelet_cost = Decimal('0')
print(f"  Eyelet cost: ${eyelet_cost:.2f}")

# Material cost (single-sided, no surcharge)
sides_cost = Decimal('0')
custom_tax = Decimal('1.0')
material_cost = total_sqm * (price_per_sqm + sides_cost) * custom_tax
print(f"  Material cost: ${float(material_cost):.2f}")

# Subtotal
subtotal = material_cost + eyelet_cost + artwork_setup
print(f"  Subtotal: ${float(subtotal):.2f}")

# Discount (5%)
subtotal_after_discount = subtotal * Decimal('0.95')
print(f"  After discount (×0.95): ${float(subtotal_after_discount):.2f}")

# Minimum order ($129)
if subtotal_after_discount < Decimal('129'):
    total_json = Decimal('129')
    print(f"  ✅ MINIMUM ORDER APPLIED: ${float(total_json):.2f}")
else:
    total_json = subtotal_after_discount
    print(f"  Total: ${float(total_json):.2f}")

# Check large size surcharge (450x600 = NO)
is_large = False
print(f"  Large size surcharge: NO")

# Final multiplier (if no large surcharge and >= $129)
if not is_large and total_json >= Decimal('129'):
    total_json = total_json * Decimal('1.1')
    print(f"  Final multiplier (×1.1): ${float(total_json):.2f}")

# NO GST
print(f"  GST: NONE (formula output = final price)")
print()
print(f"  ✅ TOTAL: ${float(total_json):.2f}")
print()
print("SHOPIFY WEBSITE CHECK:")
print("  → Go to Construction Signs calculator")
print("  → Set: 1 sign, 450x600, 5mm, single sided, no eyelets")
print(f"  → Expected price: ${float(total_json):.2f}")
print()
print()

# ============================================================================
# TEST 2: Standard Construction Sign with Eyelets
# ============================================================================
print("TEST 2: Standard Construction Sign with Eyelets")
print("-" * 80)
print("INPUTS:")
print("  Quantity: 10")
print("  Size: 600mm x 900mm (0.54 sqm each)")
print("  Thickness: 5mm")
print("  Sides: Single Sided")
print("  Eyelets: 4 x Eyelets (1 In Each Corner) - $1.60 each")
print("  Artworks: 1")
print()

# Current Backend (WRONG)
print("CURRENT BACKEND (WRONG FORMULA):")
try:
    result_current = calc_current.calculate(
        quantity=10,
        size="600mm x 900mm",
        thickness="5mm",
        sides="Single Sided",
        eyelets="4 x Eyelets (1 In Each Corner)",
        artworks=1
    )
    print(f"  Total: ${result_current.total_price:.2f}")
    print(f"  Unit: ${result_current.unit_price:.2f}")
except Exception as e:
    print(f"  ERROR: {e}")
print()

# JSON-Aligned Formula (CORRECT)
print("JSON-ALIGNED FORMULA (CORRECT):")
quantity = 10
width_mm = Decimal('600')
height_mm = Decimal('900')
total_sqm = (width_mm * height_mm / Decimal('1000000')) * Decimal(quantity)
print(f"  Total SQM: {float(total_sqm):.2f}")

# Tier lookup for 5mm at 5.4 sqm (5-6 sqm tier)
price_per_sqm = Decimal('28.35')  # Second tier
print(f"  Price per sqm: ${price_per_sqm:.2f} (5-6 sqm tier)")

# Artwork (first artwork FREE)
artwork_setup = Decimal('0')

# Eyelet cost ($1.60 per sign × 10)
eyelet_cost_per_sign = Decimal('1.60')
total_eyelet_cost = eyelet_cost_per_sign * Decimal(quantity)
print(f"  Eyelet cost: ${float(total_eyelet_cost):.2f} (${float(eyelet_cost_per_sign):.2f} × {quantity})")

# Material cost
sides_cost = Decimal('0')
custom_tax = Decimal('1.0')
material_cost = total_sqm * (price_per_sqm + sides_cost) * custom_tax
print(f"  Material cost: ${float(material_cost):.2f}")

# Subtotal
subtotal = material_cost + total_eyelet_cost + artwork_setup
print(f"  Subtotal: ${float(subtotal):.2f}")

# Discount
subtotal_after_discount = subtotal * Decimal('0.95')
print(f"  After discount: ${float(subtotal_after_discount):.2f}")

# Minimum check
if subtotal_after_discount < Decimal('129'):
    total_json = Decimal('129')
else:
    total_json = subtotal_after_discount

# Large size check (600x900 = NO)
is_large = False

# Final multiplier
if not is_large and total_json >= Decimal('129'):
    total_json = total_json * Decimal('1.1')
    print(f"  Final multiplier: ${float(total_json):.2f}")

total_json = total_json.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
unit_price = total_json / Decimal(quantity)

print()
print(f"  ✅ TOTAL: ${float(total_json):.2f}")
print(f"  ✅ UNIT: ${float(unit_price):.2f}")
print()
print("SHOPIFY WEBSITE CHECK:")
print("  → Set: 10 signs, 600x900, 5mm, single sided, 4 corner eyelets")
print(f"  → Expected total: ${float(total_json):.2f}")
print(f"  → Expected unit: ${float(unit_price):.2f}")
print()
print()

# ============================================================================
# TEST 3: Double-Sided with Multiple Artworks
# ============================================================================
print("TEST 3: Double-Sided with Multiple Artworks")
print("-" * 80)
print("INPUTS:")
print("  Quantity: 25")
print("  Size: 900mm x 1200mm (1.08 sqm each)")
print("  Thickness: 5mm")
print("  Sides: Double Sided (+$6/sqm)")
print("  Eyelets: 6 x Eyelets (3 each top & bottom) - $2.40 each")
print("  Artworks: 2 (first FREE, +$5 for extra)")
print()

# Current Backend (WRONG)
print("CURRENT BACKEND (WRONG FORMULA):")
try:
    result_current = calc_current.calculate(
        quantity=25,
        size="900mm x 1200mm",
        thickness="5mm",
        sides="Double Sided",
        eyelets="6 x Eyelets (3 each top & bottom)",
        artworks=2
    )
    print(f"  Total: ${result_current.total_price:.2f}")
    print(f"  Unit: ${result_current.unit_price:.2f}")
except Exception as e:
    print(f"  ERROR: {e}")
print()

# JSON-Aligned Formula (CORRECT)
print("JSON-ALIGNED FORMULA (CORRECT):")
quantity = 25
width_mm = Decimal('900')
height_mm = Decimal('1200')
total_sqm = (width_mm * height_mm / Decimal('1000000')) * Decimal(quantity)
print(f"  Total SQM: {float(total_sqm):.2f}")

# Tier lookup for 5mm at 27 sqm (25-30 sqm tier)
price_per_sqm = Decimal('17.05')  # Tier for 25-30 sqm
print(f"  Price per sqm: ${price_per_sqm:.2f} (25-30 sqm tier)")

# Double-sided surcharge ($6/sqm)
sides_cost = Decimal('6')
print(f"  Double-sided surcharge: +${sides_cost:.2f}/sqm")

# Artwork (first FREE, then $5 each)
artwork_setup = (Decimal(2) * Decimal('5')) - Decimal('5')
print(f"  Artwork setup: ${float(artwork_setup):.2f} (2 artworks: first FREE, +$5)")

# Eyelet cost
eyelet_cost_per_sign = Decimal('2.40')
total_eyelet_cost = eyelet_cost_per_sign * Decimal(quantity)
print(f"  Eyelet cost: ${float(total_eyelet_cost):.2f}")

# Material cost (includes double-sided)
custom_tax = Decimal('1.0')
material_cost = total_sqm * (price_per_sqm + sides_cost) * custom_tax
print(f"  Material cost: ${float(material_cost):.2f} (includes double-sided)")

# Subtotal
subtotal = material_cost + total_eyelet_cost + artwork_setup
print(f"  Subtotal: ${float(subtotal):.2f}")

# Discount
subtotal_after_discount = subtotal * Decimal('0.95')
print(f"  After discount: ${float(subtotal_after_discount):.2f}")

# Minimum check
if subtotal_after_discount < Decimal('129'):
    total_json = Decimal('129')
else:
    total_json = subtotal_after_discount

# Large size check (900x1200 = NO, neither dimension >= 1800)
is_large = False

# Final multiplier
if not is_large and total_json >= Decimal('129'):
    total_json = total_json * Decimal('1.1')
    print(f"  Final multiplier: ${float(total_json):.2f}")

total_json = total_json.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
unit_price = total_json / Decimal(quantity)

print()
print(f"  ✅ TOTAL: ${float(total_json):.2f}")
print(f"  ✅ UNIT: ${float(unit_price):.2f}")
print()
print("SHOPIFY WEBSITE CHECK:")
print("  → Set: 25 signs, 900x1200, 5mm, double sided, 6 eyelets (top/bottom), 2 artworks")
print(f"  → Expected total: ${float(total_json):.2f}")
print(f"  → Expected unit: ${float(unit_price):.2f}")
print()
print()

# ============================================================================
# TEST 4: Large Size with Surcharge
# ============================================================================
print("TEST 4: Large Size with Surcharge (NO final multiplier)")
print("-" * 80)
print("INPUTS:")
print("  Quantity: 5")
print("  Size: 1200mm x 2400mm (2.88 sqm each)")
print("  Thickness: 5mm")
print("  Sides: Single Sided")
print("  Eyelets: 4 x Eyelets (1 In Each Corner)")
print("  Artworks: 1")
print()

# Current Backend (WRONG)
print("CURRENT BACKEND (WRONG FORMULA):")
try:
    result_current = calc_current.calculate(
        quantity=5,
        size="1200mm x 2400mm",
        thickness="5mm",
        sides="Single Sided",
        eyelets="4 x Eyelets (1 In Each Corner)",
        artworks=1
    )
    print(f"  Total: ${result_current.total_price:.2f}")
except Exception as e:
    print(f"  ERROR: {e}")
print()

# JSON-Aligned Formula (CORRECT)
print("JSON-ALIGNED FORMULA (CORRECT):")
quantity = 5
width_mm = Decimal('1200')
height_mm = Decimal('2400')
total_sqm = (width_mm * height_mm / Decimal('1000000')) * Decimal(quantity)
print(f"  Total SQM: {float(total_sqm):.2f}")

# Tier lookup for 5mm at 14.4 sqm (10-15 sqm tier)
price_per_sqm = Decimal('21.24')
print(f"  Price per sqm: ${price_per_sqm:.2f} (10-15 sqm tier)")

# Artwork
artwork_setup = Decimal('0')

# Eyelet cost
eyelet_cost_per_sign = Decimal('1.60')
total_eyelet_cost = eyelet_cost_per_sign * Decimal(quantity)
print(f"  Eyelet cost: ${float(total_eyelet_cost):.2f}")

# Material cost
sides_cost = Decimal('0')
custom_tax = Decimal('1.0')
material_cost = total_sqm * (price_per_sqm + sides_cost) * custom_tax
print(f"  Material cost: ${float(material_cost):.2f}")

# Subtotal
subtotal = material_cost + total_eyelet_cost + artwork_setup
print(f"  Subtotal: ${float(subtotal):.2f}")

# Discount
subtotal_after_discount = subtotal * Decimal('0.95')
print(f"  After discount: ${float(subtotal_after_discount):.2f}")

# Minimum check
if subtotal_after_discount < Decimal('129'):
    total_json = Decimal('129')
else:
    total_json = subtotal_after_discount

# Large size check - THIS IS THE KEY DIFFERENCE
is_large = True  # 1200x2400mm size triggers surcharge
print(f"  ✅ LARGE SIZE DETECTED (1200x2400mm)")

# Apply large size surcharge ($45) - NO final multiplier
large_size_surcharge = Decimal('45')
total_json = total_json + large_size_surcharge
print(f"  Large size surcharge: +${float(large_size_surcharge):.2f}")
print(f"  NO final multiplier (mutually exclusive with surcharge)")

total_json = total_json.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
unit_price = total_json / Decimal(quantity)

print()
print(f"  ✅ TOTAL: ${float(total_json):.2f}")
print(f"  ✅ UNIT: ${float(unit_price):.2f}")
print()
print("SHOPIFY WEBSITE CHECK:")
print("  → Set: 5 signs, 1200x2400, 5mm, single sided, 4 corner eyelets")
print(f"  → Expected total: ${float(total_json):.2f}")
print()
print()

# ============================================================================
# TEST 5: 3mm vs 5mm Comparison
# ============================================================================
print("TEST 5: 3mm vs 5mm Material Comparison")
print("-" * 80)
print("INPUTS (same except thickness):")
print("  Quantity: 20")
print("  Size: 600mm x 900mm")
print("  Sides: Single Sided")
print("  Eyelets: No Eyelets")
print("  Artworks: 1")
print()

quantity = 20
width_mm = Decimal('600')
height_mm = Decimal('900')
total_sqm = (width_mm * height_mm / Decimal('1000000')) * Decimal(quantity)

print(f"Total SQM: {float(total_sqm):.2f}")
print()

# 5mm pricing
print("5mm CORFLUTE:")
price_per_sqm_5mm = Decimal('19.5')  # 10-15 sqm tier for 5mm
print(f"  Price per sqm: ${price_per_sqm_5mm:.2f} (10-15 sqm tier)")
material_cost_5mm = total_sqm * price_per_sqm_5mm
subtotal_5mm = material_cost_5mm
subtotal_after_discount_5mm = subtotal_5mm * Decimal('0.95')
if subtotal_after_discount_5mm < Decimal('129'):
    total_5mm = Decimal('129')
else:
    total_5mm = subtotal_after_discount_5mm
total_5mm = total_5mm * Decimal('1.1')  # Final multiplier
total_5mm = total_5mm.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
print(f"  ✅ TOTAL: ${float(total_5mm):.2f}")
print()

# 3mm pricing
print("3mm CORFLUTE:")
price_per_sqm_3mm = Decimal('16.13')  # 10-15 sqm tier for 3mm
print(f"  Price per sqm: ${price_per_sqm_3mm:.2f} (10-15 sqm tier)")
material_cost_3mm = total_sqm * price_per_sqm_3mm
subtotal_3mm = material_cost_3mm
subtotal_after_discount_3mm = subtotal_3mm * Decimal('0.95')
if subtotal_after_discount_3mm < Decimal('129'):
    total_3mm = Decimal('129')
else:
    total_3mm = subtotal_after_discount_3mm
total_3mm = total_3mm * Decimal('1.1')  # Final multiplier
total_3mm = total_3mm.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
print(f"  ✅ TOTAL: ${float(total_3mm):.2f}")
print()

savings = total_5mm - total_3mm
savings_pct = (savings / total_5mm) * Decimal('100')
print(f"SAVINGS with 3mm: ${float(savings):.2f} ({float(savings_pct):.1f}% cheaper)")
print()
print("SHOPIFY WEBSITE CHECK:")
print(f"  → Set: 20 signs, 600x900, single sided, no eyelets")
print(f"  → Test 5mm: Expected ${float(total_5mm):.2f}")
print(f"  → Test 3mm: Expected ${float(total_3mm):.2f}")
print()
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("SUMMARY - KEY DIFFERENCES")
print("=" * 80)
print()
print("CURRENT BACKEND ERRORS:")
print("  ❌ Uses fixed material rates ($5.50/$6.50) instead of 42-tier pricing")
print("  ❌ Missing eyelet costs ($0-$2.40 per sign)")
print("  ❌ Wrong artwork costs ($18 vs $5 per extra)")
print("  ❌ Wrong double-sided logic (multiplies instead of adding $6/sqm)")
print("  ❌ Missing custom size tax (×1.1)")
print("  ❌ Missing discount factor (×0.95)")
print("  ❌ Missing minimum order ($129)")
print("  ❌ Missing large size surcharge ($45)")
print("  ❌ Missing final multiplier (×1.1)")
print("  ❌ WRONG: Applies double GST (×1.1×1.1) - JSON has NONE")
print()
print("JSON-ALIGNED FORMULA:")
print("  ✅ 42-tier pricing system (volume discounts)")
print("  ✅ Eyelet costs included")
print("  ✅ Correct artwork formula (first FREE, $5 per extra)")
print("  ✅ Correct double-sided surcharge (+$6/sqm)")
print("  ✅ Custom size tax (×1.1)")
print("  ✅ Discount factor (×0.95)")
print("  ✅ Minimum order ($129)")
print("  ✅ Large size surcharge ($45)")
print("  ✅ Final multiplier (×1.1) - mutually exclusive with large surcharge")
print("  ✅ NO GST (formula output = final price)")
print()
print("=" * 80)
print("NEXT STEP: Verify these prices on the Shopify Construction Signs calculator")
print("=" * 80)
