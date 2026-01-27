"""
Premium Business Cards Test Validation Script
Tests all 6 configurations against website prices
"""

from PremiumBusinessCards_Shopify_Calculator import PremiumBusinessCardsShopifyCalculator

# Initialize calculator
calculator = PremiumBusinessCardsShopifyCalculator()

print("="*80)
print("PREMIUM BUSINESS CARDS - BACKEND VALIDATION")
print("="*80)
print()

# Test 2: 500 Satin double colour no celloglaze - Website: $85.80
print("TEST 2: 500 Satin Double Colour No Celloglaze")
print("-" * 60)
result2 = calculator.calculate(
    quantity=500,
    paper_stock="Satin 350GSM",
    finish_size="90mm x 55mm",
    print_type="Colour",
    print_sides="Double side print",
    celloglaze="None",
    artworks=1
)
backend2 = float(result2.total_price)
website2 = 85.80
diff2 = abs(backend2 - website2)
pct2 = (diff2 / website2) * 100
status2 = "✅ PASS" if pct2 < 1.0 else "❌ FAIL"
print(f"Backend: ${backend2:.2f}")
print(f"Website: ${website2:.2f}")
print(f"Difference: ${diff2:.2f} ({pct2:.2f}%) {status2}")
print()

# Test 3: 1000 EcoStar single colour no celloglaze - Website: $135.30
print("TEST 3: 1000 EcoStar Single Colour No Celloglaze")
print("-" * 60)
result3 = calculator.calculate(
    quantity=1000,
    paper_stock="EcoStar 350GSM Uncoated 100% Recycled",
    finish_size="90mm x 55mm",
    print_type="Colour",
    print_sides="Single side print",
    celloglaze="None",
    artworks=1
)
backend3 = float(result3.total_price)
website3 = 135.30
diff3 = abs(backend3 - website3)
pct3 = (diff3 / website3) * 100
status3 = "✅ PASS" if pct3 < 1.0 else "❌ FAIL"
print(f"Backend: ${backend3:.2f}")
print(f"Website: ${website3:.2f}")
print(f"Difference: ${diff3:.2f} ({pct3:.2f}%) {status3}")
print()

# Test 4: 250 Satin single colour 1-side matt - Website: $85.80
print("TEST 4: 250 Satin Single Colour 1-Side Matt")
print("-" * 60)
result4 = calculator.calculate(
    quantity=250,
    paper_stock="Satin 350GSM",
    finish_size="90mm x 55mm",
    print_type="Colour",
    print_sides="Single side print",
    celloglaze="1 Side Matt",
    artworks=1
)
backend4 = float(result4.total_price)
website4 = 85.80
diff4 = abs(backend4 - website4)
pct4 = (diff4 / website4) * 100
status4 = "✅ PASS" if pct4 < 1.0 else "❌ FAIL"
print(f"Backend: ${backend4:.2f}")
print(f"Website: ${website4:.2f}")
print(f"Difference: ${diff4:.2f} ({pct4:.2f}%) {status4}")
print()

# Test 5: 5000 King Kong double colour 2-side SILK FEEL - Website: $518.10
print("TEST 5: 5000 King Kong Double Colour 2-Side SILK FEEL")
print("-" * 60)
result5 = calculator.calculate(
    quantity=5000,
    paper_stock="King Kong High Bulk 420GSM",
    finish_size="90mm x 55mm",
    print_type="Colour",
    print_sides="Double side print",
    celloglaze="2 Side SILK FEEL Matt",
    artworks=1
)
backend5 = float(result5.total_price)
website5 = 518.10
diff5 = abs(backend5 - website5)
pct5 = (diff5 / website5) * 100
status5 = "✅ PASS" if pct5 < 1.0 else "❌ FAIL"
print(f"Backend: ${backend5:.2f}")
print(f"Website: ${website5:.2f}")
print(f"Difference: ${diff5:.2f} ({pct5:.2f}%) {status5}")
print()

# Test 6: 1000 Satin single B&W no celloglaze - Website: $95.70
print("TEST 6: 1000 Satin Single B&W No Celloglaze")
print("-" * 60)
result6 = calculator.calculate(
    quantity=1000,
    paper_stock="Satin 350GSM",
    finish_size="90mm x 55mm",
    print_type="Black & White",
    print_sides="Single side print",
    celloglaze="None",
    artworks=1
)
backend6 = float(result6.total_price)
website6 = 95.70
diff6 = abs(backend6 - website6)
pct6 = (diff6 / website6) * 100
status6 = "✅ PASS" if pct6 < 1.0 else "❌ FAIL"
print(f"Backend: ${backend6:.2f}")
print(f"Website: ${website6:.2f}")
print(f"Difference: ${diff6:.2f} ({pct6:.2f}%) {status6}")
print()

# Summary
print("="*80)
print("SUMMARY")
print("="*80)
passed = sum([pct2 < 1.0, pct3 < 1.0, pct4 < 1.0, pct5 < 1.0, pct6 < 1.0])
total = 5
print(f"Tests Passed: {passed}/{total}")
print(f"Tests Failed: {total - passed}/{total}")
print()
if passed == total:
    print("✅ ALL TESTS PASSED - Calculator is accurate!")
else:
    print("❌ SOME TESTS FAILED - Investigation needed")
    print()
    print("Failed tests:")
    if pct2 >= 1.0:
        print(f"  - Test 2: {pct2:.2f}% difference")
    if pct3 >= 1.0:
        print(f"  - Test 3: {pct3:.2f}% difference")
    if pct4 >= 1.0:
        print(f"  - Test 4: {pct4:.2f}% difference")
    if pct5 >= 1.0:
        print(f"  - Test 5: {pct5:.2f}% difference")
    if pct6 >= 1.0:
        print(f"  - Test 6: {pct6:.2f}% difference")
