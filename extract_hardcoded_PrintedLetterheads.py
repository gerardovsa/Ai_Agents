"""
Extract hardcoded prices from PrintedLetterheads_Shopify_Calculator.py
Part of: CALCULATOR_PATHWAY_ALIGNMENT_GUIDE.md
Date: January 25, 2026
"""

print("=" * 80)
print("HARDCODED PRICES - PrintedLetterheads_Shopify_Calculator.py")
print("=" * 80)

print("\n1. PAPER STOCK (per 1000 sheets):")
print("   Uncoated Bond 80GSM: $26.34")
print("   Uncoated Bond 90GSM: $29.51")
print("   Uncoated Bond 100GSM: $32.68")

print("\n2. PRINT TYPE (per sheet):")
print("   Colour: $0.044")
print("   Black & White: $0.02")

print("\n3. PRINT SIDES (multiplier):")
print("   Single side print: 1×")
print("   Double side print: 2×")

print("\n4. FINISH SIZE (sheets per unit):")
print("   A4 - 210mm x 297mm: 2 letterheads per sheet")

print("\n5. CONSTANTS:")
print("   Imposition setup: $15")
print("   Guillotine setup: $12")
print("   Extra artwork charge: $15 (first FREE)")
print("   Stock waste multiplier: 1.05")
print("   Cutting block size: 500 sheets")
print("   Cutting cost: $11 per 500 sheets")

print("\n6. PROFIT MARGIN TIERS (11 tiers + fixed):")
print("   $1.00 - $50.99: 170% margin (1.7×)")
print("   $51.00 - $74.99: 155% margin (1.55×)")
print("   $75.00 - $100.99: 135% margin (1.35×)")
print("   $101.00 - $150.99: 130% margin (1.30×)")
print("   $151.00 - $200.99: 115% margin (1.15×)")
print("   $201.00 - $300.99: 70% margin (0.70×)")
print("   $301.00 - $400.99: 53% margin (0.53×)")
print("   $401.00 - $500.99: 40% margin (0.40×)")
print("   $501.00 - $1000.99: 30% margin (0.30×)")
print("   $1001.00 - $5000.99: 30% margin (0.30×)")
print("   $5001.00 - $100000.99: 25% margin (0.25×)")
print("   $100001.00+: Fixed $200 margin")

print("\n7. GST CALCULATION:")
print("   DOUBLE GST: ×1.1 ×1.1 = 1.21 total (21% effective)")

print("\n" + "=" * 80)
print("Total Price Points: 6 core prices + 7 constants + 12 margin tiers = 25 values")
print("=" * 80)
