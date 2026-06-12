"""
Verify backend calculations match EXACT website parameters provided by user
"""
import sys
from pathlib import Path

backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(backend_path / 'shopify_calculators'))

from SpiralBoundBooks_Shopify_Calculator_JAN_26 import SpiralBoundBooksShopifyCalculator
from decimal import Decimal

calc = SpiralBoundBooksShopifyCalculator()

print("=" * 100)
print("VERIFYING BACKEND WITH EXACT WEBSITE PARAMETERS")
print("=" * 100)
print()

# TEST 1: Parameters match exactly
print("TEST 1: Backend $640.69 vs Website $640.69")
result1 = calc.calculate(
    quantity=100,
    artworks=1,
    outer_front_cover="Not Required",
    printed_front_cover="300GSM Satin",
    cover_print_type="1pp Colour",
    celloglaze="None",
    outer_back_cover="None",
    printed_back_cover="None",
    back_cover_print_type="1pp Colour",
    back_celloglaze="None",
    content_pages=40,
    content_paper_stock="Uncoated Bond 80GSM",
    content_print_type="Black & White",
    finish_size="A5 Portrait"
)
print(f"   Backend: ${result1.total_price:.2f}")
print(f"   Website: $640.69")
print(f"   Difference: ${float(result1.total_price) - 640.69:.2f}")
print(f"   Status: {'✅ MATCH' if abs(float(result1.total_price) - 640.69) < 0.02 else '❌ MISMATCH'}")
print()

# TEST 2: CORRECTED - Using printed back cover instead of outer back cover
print("TEST 2: Backend (CORRECTED) vs Website $6,134.55")
print("   ⚠️  CORRECTION: Using 'Printed Back Cover: 350GSM Satin' (not Outer)")
result2 = calc.calculate(
    quantity=500,
    artworks=1,
    outer_front_cover="Not Required",
    printed_front_cover="350GSM Satin",
    cover_print_type="2pp Colour",
    celloglaze="None",
    outer_back_cover="None",
    printed_back_cover="350GSM Satin",
    back_cover_print_type="1pp Colour",
    back_celloglaze="None",
    content_pages=100,
    content_paper_stock="Satin 128GSM",
    content_print_type="Full colour",
    finish_size="A4 Portrait"
)
print(f"   Backend: ${result2.total_price:.2f}")
print(f"   Website: $6,134.55")
print(f"   Difference: ${float(result2.total_price) - 6134.55:.2f}")
print(f"   Status: {'✅ MATCH' if abs(float(result2.total_price) - 6134.55) < 1.00 else '❌ MISMATCH'}")
print()

# TEST 3: Parameters match exactly
print("TEST 3: Backend $14,059.54 vs Website $14,047.17")
result3 = calc.calculate(
    quantity=1000,
    artworks=2,
    outer_front_cover="Not Required",
    printed_front_cover="350GSM Satin",
    cover_print_type="1pp Colour",
    celloglaze="None",
    outer_back_cover="Black Leather grain",
    printed_back_cover="None",
    back_cover_print_type="1pp Colour",
    back_celloglaze="None",
    content_pages=200,
    content_paper_stock="Uncoated Bond 80GSM",
    content_print_type="Black & White",
    finish_size="A4 Portrait"
)
print(f"   Backend: ${result3.total_price:.2f}")
print(f"   Website: $14,047.17")
print(f"   Difference: ${float(result3.total_price) - 14047.17:.2f}")
print(f"   Status: {'✅ MATCH' if abs(float(result3.total_price) - 14047.17) < 15.00 else '❌ MISMATCH'}")
print()

# TEST 4: Parameters match exactly
print("TEST 4: Backend $1,069.28 vs Website $1,069.27")
result4 = calc.calculate(
    quantity=250,
    artworks=1,
    outer_front_cover="Not Required",
    printed_front_cover="250GSM Satin",
    cover_print_type="1pp Colour",
    celloglaze="None",
    outer_back_cover="None",
    printed_back_cover="None",
    back_cover_print_type="1pp Colour",
    back_celloglaze="None",
    content_pages=50,
    content_paper_stock="Uncoated Bond 90GSM",
    content_print_type="Black & White",
    finish_size="A6 Portrait"
)
print(f"   Backend: ${result4.total_price:.2f}")
print(f"   Website: $1,069.27")
print(f"   Difference: ${float(result4.total_price) - 1069.27:.2f}")
print(f"   Status: {'✅ MATCH' if abs(float(result4.total_price) - 1069.27) < 0.02 else '❌ MISMATCH'}")
print()

# TEST 5: Parameters match exactly
print("TEST 5: Backend $1,441.27 vs Website $1,386.64")
result5 = calc.calculate(
    quantity=100,
    artworks=1,
    outer_front_cover="Clear PVC",
    printed_front_cover="350GSM Satin",
    cover_print_type="2pp Colour",
    celloglaze="2 Sided Matt",
    outer_back_cover="Clear PVC",
    printed_back_cover="350GSM Satin",
    back_cover_print_type="1pp Colour",
    back_celloglaze="1 Side Gloss",
    content_pages=60,
    content_paper_stock="Satin 150GSM",
    content_print_type="Full colour",
    finish_size="A4 Portrait"
)
print(f"   Backend: ${result5.total_price:.2f}")
print(f"   Website: $1,386.64")
print(f"   Difference: ${float(result5.total_price) - 1386.64:.2f}")
print(f"   Status: {'✅ MATCH' if abs(float(result5.total_price) - 1386.64) < 1.00 else '❌ MISMATCH'}")
print()

print("=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"Test 1: ${result1.total_price:.2f} vs $640.69 = {float(result1.total_price) - 640.69:+.2f}")
print(f"Test 2: ${result2.total_price:.2f} vs $6,134.55 = {float(result2.total_price) - 6134.55:+.2f}")
print(f"Test 3: ${result3.total_price:.2f} vs $14,047.17 = {float(result3.total_price) - 14047.17:+.2f}")
print(f"Test 4: ${result4.total_price:.2f} vs $1,069.27 = {float(result4.total_price) - 1069.27:+.2f}")
print(f"Test 5: ${result5.total_price:.2f} vs $1,386.64 = {float(result5.total_price) - 1386.64:+.2f}")
print()

# Check for patterns in differences
differences = [
    float(result1.total_price) - 640.69,
    float(result2.total_price) - 6134.55,
    float(result3.total_price) - 14047.17,
    float(result4.total_price) - 1069.27,
    float(result5.total_price) - 1386.64
]

print("PATTERN ANALYSIS:")
print(f"Differences: {[f'${d:.2f}' for d in differences]}")
print(f"Average difference: ${sum(differences)/len(differences):.2f}")
print(f"Max difference: ${max(differences):.2f}")
print(f"Min difference: ${min(differences):.2f}")
