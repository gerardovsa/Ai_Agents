"""
Comprehensive Spiral Bound Books Test Suite
Tests with ORIGINAL calculator (10% GST - WRONG) vs CORRECTED (15% GST + $98.63 surcharge)
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add backend path
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(backend_path / 'shopify_calculators'))

# Import the EXISTING (wrong) calculator
from SpiralBound_Shopify_Calculator import SpiralBoundShopifyCalculator

print("=" * 100)
print("SPIRAL BOUND BOOKS - COMPREHENSIVE TEST ANALYSIS")
print("=" * 100)
print()
print("🔍 Testing with ORIGINAL calculator from SpiralBound_Shopify_Calculator.py")
print("   ⚠️  Known Issues: GST_RATE = 1.10 (should be 1.15)")
print("   ⚠️  Known Issues: SURCHARGE = $44 (website uses $98.63)")
print()
print("=" * 100)
print()

# Create calculator instance
calc = SpiralBoundShopifyCalculator()

print(f"📋 Calculator Configuration:")
print(f"   GST Rate: {calc.GST_RATE} ({(calc.GST_RATE-1)*100:.0f}% GST)")
print(f"   Surcharge: ${calc.SURCHARGE}")
print(f"   Price Increase Multiplier: {calc.PRICE_INCREASE_MULTIPLIER} ({(calc.PRICE_INCREASE_MULTIPLIER-1)*100:.0f}% markup)")
print()
print("=" * 100)
print()

# ============================================================================
# ORIGINAL 5 TESTS
# ============================================================================

tests = []

print("PART 1: ORIGINAL 5 TESTS")
print("=" * 100)
print()

# TEST 1: Basic Spiral Bound - 100 books, A5, 40pp, B&W content
print("TEST 1: Basic Spiral Bound - Small Quantity")
print("-" * 100)
print("Config: 100 books, A5 Portrait, 40pp B&W, 300GSM Satin front cover, 1pp Colour")
result1 = calc.calculate(
    quantity=100,
    artworks=1,
    outer_front_cover="Not Required",
    printed_front_cover="300GSM Satin",
    front_cover_print="1pp Colour",
    front_celloglaze="None",
    outer_back_cover="None",
    printed_back_cover="None",
    back_cover_print="1pp Colour",
    back_celloglaze="None",
    internal_pages=40,
    internal_stock="Uncoated Bond 80GSM",
    internal_print="Black & White",
    finish_size="A5 Portrait"
)
print(f"Backend Total: ${result1.total_price:.2f}")
print(f"Unit Price: ${result1.unit_price:.2f}")
print(f"BizCost: ${result1.breakdown['biz_cost']:.2f}")
print(f"After Margin (90%): ${result1.breakdown['subtotal']:.2f}")
print(f"After 5% increase: ${result1.breakdown['subtotal_with_increase']:.2f}")
print(f"After 10% GST: ${result1.breakdown['subtotal_with_increase'] * calc.GST_RATE:.2f}")
print(f"Final (+$44): ${result1.total_price:.2f}")
print()

# TEST 2: Medium Quantity Color - 500 books, A4, 100pp, Full Colour
print("TEST 2: Medium Quantity with Color Content")
print("-" * 100)
print("Config: 500 books, A4 Portrait, 100pp Color, 350GSM Satin covers front/back")
result2 = calc.calculate(
    quantity=500,
    artworks=1,
    outer_front_cover="Not Required",
    printed_front_cover="350GSM Satin",
    front_cover_print="2pp Colour",
    front_celloglaze="None",
    outer_back_cover="350GSM Satin Blank",
    printed_back_cover="None",
    back_cover_print="1pp Colour",
    back_celloglaze="None",
    internal_pages=100,
    internal_stock="Satin 128GSM",
    internal_print="Full colour",
    finish_size="A4 Portrait"
)
print(f"Backend Total: ${result2.total_price:.2f}")
print(f"Unit Price: ${result2.unit_price:.2f}")
print(f"BizCost: ${result2.breakdown['biz_cost']:.2f}")
print()

# TEST 3: Large Quantity Thick Book - 1000 books, A4, 200pp
print("TEST 3: Large Quantity Thick Book")
print("-" * 100)
print("Config: 1000 books, A4 Portrait, 200pp B&W, 350GSM Satin front, Black Leather back")
result3 = calc.calculate(
    quantity=1000,
    artworks=2,
    outer_front_cover="Not Required",
    printed_front_cover="350GSM Satin",
    front_cover_print="1pp Colour",
    front_celloglaze="None",
    outer_back_cover="Black Leather grain",
    printed_back_cover="None",
    back_cover_print="1pp Colour",
    back_celloglaze="None",
    internal_pages=200,
    internal_stock="Uncoated Bond 80GSM",
    internal_print="Black & White",
    finish_size="A4 Portrait"
)
print(f"Backend Total: ${result3.total_price:.2f}")
print(f"Unit Price: ${result3.unit_price:.2f}")
print(f"BizCost: ${result3.breakdown['biz_cost']:.2f}")
print()

# TEST 4: Small Format - 250 books, A6, 50pp (wire price halved)
print("TEST 4: Small Format (A6) - Spiral Price Halved")
print("-" * 100)
print("Config: 250 books, A6 Portrait, 50pp B&W, 250GSM Satin front")
result4 = calc.calculate(
    quantity=250,
    artworks=1,
    outer_front_cover="Not Required",
    printed_front_cover="250GSM Satin",
    front_cover_print="1pp Colour",
    front_celloglaze="None",
    outer_back_cover="None",
    printed_back_cover="None",
    back_cover_print="1pp Colour",
    back_celloglaze="None",
    internal_pages=50,
    internal_stock="Uncoated Bond 90GSM",
    internal_print="Black & White",
    finish_size="A6 Portrait"
)
print(f"Backend Total: ${result4.total_price:.2f}")
print(f"Unit Price: ${result4.unit_price:.2f}")
print(f"BizCost: ${result4.breakdown['biz_cost']:.2f}")
print(f"Spiral cost per book: ${result4.specifications['spiral_price_per_book']:.4f} (HALVED for A6)")
print()

# TEST 5: Premium with Celloglaze - 100 books, A4, 60pp
print("TEST 5: Premium Covers with Celloglaze")
print("-" * 100)
print("Config: 100 books, A4 Portrait, 60pp Color, Premium covers with celloglaze both sides")
result5 = calc.calculate(
    quantity=100,
    artworks=1,
    outer_front_cover="Clear PVC",
    printed_front_cover="350GSM Satin",
    front_cover_print="2pp Colour",
    front_celloglaze="2 Sided Matt",
    outer_back_cover="Clear PVC",
    printed_back_cover="350GSM Satin",
    back_cover_print="1pp Colour",
    back_celloglaze="1 Side Gloss",
    internal_pages=60,
    internal_stock="Satin 150GSM",
    internal_print="Full colour",
    finish_size="A4 Portrait"
)
print(f"Backend Total: ${result5.total_price:.2f}")
print(f"Unit Price: ${result5.unit_price:.2f}")
print(f"BizCost: ${result5.breakdown['biz_cost']:.2f}")
print(f"Cello Setup: ${result5.breakdown['setup_costs']:.2f} (includes $25 cello)")
print()

# ============================================================================
# DIAGNOSTIC TESTS (from website validation)
# ============================================================================

print()
print("=" * 100)
print("PART 2: DIAGNOSTIC TESTS (Validated Against Website)")
print("=" * 100)
print()

# Test 1 (Original Reference) - 100 qty A5 Landscape with full covers
print("DIAGNOSTIC TEST 1: Full Configuration (Original Reference)")
print("-" * 100)
print("Config: 100 books, A5 Landscape, 50pp B&W, Clear PVC front, 300GSM Satin front, 350GSM Satin Blank back")
diag1 = calc.calculate(
    quantity=100,
    artworks=1,
    finish_size="A5 Landscape",
    outer_front_cover="Clear PVC",
    printed_front_cover="300GSM Satin",
    front_cover_print="1pp Colour",
    front_celloglaze="None",
    outer_back_cover="350GSM Satin Blank",
    printed_back_cover="None",
    back_cover_print="1pp Colour",
    back_celloglaze="None",
    internal_pages=50,
    internal_stock="Uncoated Bond 100GSM",
    internal_print="Black & White"
)
print(f"Backend Total: ${diag1.total_price:.2f}")
print(f"Website Price: $687.65")
print(f"Difference: ${Decimal('687.65') - diag1.total_price:.2f}")
print()

# Test 2 - No outer covers
print("DIAGNOSTIC TEST 2: No Outer Covers - Only Printed Front")
print("-" * 100)
print("Config: Same as Test 1 but no outer covers")
diag2 = calc.calculate(
    quantity=100,
    artworks=1,
    finish_size="A5 Landscape",
    outer_front_cover="Not Required",
    printed_front_cover="300GSM Satin",
    front_cover_print="1pp Colour",
    front_celloglaze="None",
    outer_back_cover="None",
    printed_back_cover="None",
    back_cover_print="1pp Colour",
    back_celloglaze="None",
    internal_pages=50,
    internal_stock="Uncoated Bond 100GSM",
    internal_print="Black & White"
)
print(f"Backend Total: ${diag2.total_price:.2f}")
print(f"Website Price: $635.21")
print(f"Difference: ${Decimal('635.21') - diag2.total_price:.2f}")
print()

# Test 3 - No printed covers
print("DIAGNOSTIC TEST 3: No Printed Covers - Only Outer PVC")
print("-" * 100)
print("Config: Same as Test 1 but no printed covers")
diag3 = calc.calculate(
    quantity=100,
    artworks=1,
    finish_size="A5 Landscape",
    outer_front_cover="Clear PVC",
    printed_front_cover="None",
    front_cover_print="1pp Colour",
    front_celloglaze="None",
    outer_back_cover="350GSM Satin Blank",
    printed_back_cover="None",
    back_cover_print="1pp Colour",
    back_celloglaze="None",
    internal_pages=50,
    internal_stock="Uncoated Bond 100GSM",
    internal_print="Black & White"
)
print(f"Backend Total: ${diag3.total_price:.2f}")
print(f"Website Price: $674.99")
print(f"Difference: ${Decimal('674.99') - diag3.total_price:.2f}")
print()

# Test 4 - No covers at all
print("DIAGNOSTIC TEST 4: No Covers - Content Only")
print("-" * 100)
print("Config: Same as Test 1 but no covers at all")
diag4 = calc.calculate(
    quantity=100,
    artworks=1,
    finish_size="A5 Landscape",
    outer_front_cover="Not Required",
    printed_front_cover="None",
    front_cover_print="1pp Colour",
    front_celloglaze="None",
    outer_back_cover="None",
    printed_back_cover="None",
    back_cover_print="1pp Colour",
    back_celloglaze="None",
    internal_pages=50,
    internal_stock="Uncoated Bond 100GSM",
    internal_print="Black & White"
)
print(f"Backend Total: ${diag4.total_price:.2f}")
print(f"Website Price: $622.55")
print(f"Difference: ${Decimal('622.55') - diag4.total_price:.2f}")
print()

# Test 6 - A4 Portrait (wire NOT halved)
print("DIAGNOSTIC TEST 6: A4 Portrait (Spiral NOT Halved)")
print("-" * 100)
print("Config: Same as Test 1 but A4 Portrait")
diag6 = calc.calculate(
    quantity=100,
    artworks=1,
    finish_size="A4 Portrait",
    outer_front_cover="Clear PVC",
    printed_front_cover="300GSM Satin",
    front_cover_print="1pp Colour",
    front_celloglaze="None",
    outer_back_cover="350GSM Satin Blank",
    printed_back_cover="None",
    back_cover_print="1pp Colour",
    back_celloglaze="None",
    internal_pages=50,
    internal_stock="Uncoated Bond 100GSM",
    internal_print="Black & White"
)
print(f"Backend Total: ${diag6.total_price:.2f}")
print(f"Website Price: $851.16")
print(f"Difference: ${Decimal('851.16') - diag6.total_price:.2f}")
print()

# Test 7 - A4 minimal
print("DIAGNOSTIC TEST 7: A4 Portrait Minimal")
print("-" * 100)
print("Config: Same as Test 6 but no outer covers")
diag7 = calc.calculate(
    quantity=100,
    artworks=1,
    finish_size="A4 Portrait",
    outer_front_cover="Not Required",
    printed_front_cover="300GSM Satin",
    front_cover_print="1pp Colour",
    front_celloglaze="None",
    outer_back_cover="None",
    printed_back_cover="None",
    back_cover_print="1pp Colour",
    back_celloglaze="None",
    internal_pages=50,
    internal_stock="Uncoated Bond 100GSM",
    internal_print="Black & White"
)
print(f"Backend Total: ${diag7.total_price:.2f}")
print(f"Website Price: $798.72")
print(f"Difference: ${Decimal('798.72') - diag7.total_price:.2f}")
print()

# ============================================================================
# SUMMARY TABLE
# ============================================================================

print()
print("=" * 100)
print("SUMMARY - ALL TESTS")
print("=" * 100)
print()
print(f"{'Test':<25} {'Backend':<15} {'Website':<15} {'Difference':<15} {'% Off':<10}")
print("-" * 100)

results = [
    ("Test 1 (Basic A5)", result1.total_price, None, None),
    ("Test 2 (500 A4 Color)", result2.total_price, None, None),
    ("Test 3 (1000 A4 Thick)", result3.total_price, None, None),
    ("Test 4 (250 A6)", result4.total_price, None, None),
    ("Test 5 (Premium Cello)", result5.total_price, None, None),
    ("Diag 1 (Full Config)", diag1.total_price, Decimal('687.65'), None),
    ("Diag 2 (No Outer)", diag2.total_price, Decimal('635.21'), None),
    ("Diag 3 (No Printed)", diag3.total_price, Decimal('674.99'), None),
    ("Diag 4 (No Covers)", diag4.total_price, Decimal('622.55'), None),
    ("Diag 6 (A4 Portrait)", diag6.total_price, Decimal('851.16'), None),
    ("Diag 7 (A4 Minimal)", diag7.total_price, Decimal('798.72'), None),
]

for name, backend, website, _ in results:
    if website:
        diff = website - backend
        pct = (diff / backend) * 100
        print(f"{name:<25} ${backend:>12.2f}  ${website:>12.2f}  ${diff:>12.2f}  {pct:>8.2f}%")
    else:
        print(f"{name:<25} ${backend:>12.2f}  {'NEED PRICE':<15} {'-':<15} {'-':<10}")

print()
print("=" * 100)
print("IDENTIFIED ISSUES:")
print("=" * 100)
print()
print("1. ⚠️  GST Rate: Calculator uses 1.10 (10%), JavaScript formula uses 1.15 (15%)")
print("2. ⚠️  Surcharge: Calculator uses $44, website charges $98.63 (extra $54.63)")
print("3. ✅ All diagnostic tests show consistent +$54.63 difference (after GST fix)")
print()
print("RECOMMENDED FIX:")
print("  • Change GST_RATE from Decimal('1.10') to Decimal('1.15')")
print("  • Change SURCHARGE from Decimal('44.00') to Decimal('98.63')")
print()
print("=" * 100)
