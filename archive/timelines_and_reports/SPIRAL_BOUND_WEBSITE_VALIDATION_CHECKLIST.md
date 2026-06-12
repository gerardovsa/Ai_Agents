# Spiral Bound Books - Website Validation Checklist
**Date:** January 24, 2026  
**Calculator:** Spiral Bound Books (Shopify)  
**Website:** https://gerardovsa.myshopify.com/  

---

## 🎯 Expected Results Summary

| Test | Configuration | Backend Price | Website Price | Status |
|------|--------------|---------------|---------------|--------|
| 1 | 100 books, A5, 40pp, B&W | **$507.30** | _________ | ⏳ |
| 2 | 500 books, A4, 100pp, Color | **$3,425.73** | _________ | ⏳ |
| 3 | 1000 books, A4, 200pp, B&W | **$8,125.50** | _________ | ⏳ |
| 4 | 250 books, A6, 50pp, B&W | **$978.21** | _________ | ⏳ |
| 5 | 100 books, A4, 60pp, Premium | **$1,021.85** | _________ | ⏳ |

---

## ⚠️ Critical Validation Points

**Formula Pattern: 15% GST + $44 Fixed Surcharge**
- ✅ **GST Rate:** 15% (not 10% like other calculators)
- ✅ **Surcharge:** Fixed $44 added AFTER GST
- ✅ **Wire Pricing:** 18 tiers based on book thickness
- ✅ **Small Formats:** A6/DL/A5 Landscape use HALF wire price
- ✅ **Celloglaze Setup:** $25 when EITHER front OR back celloglaze selected
- ✅ **Profit Margins:** 12 tiers (90% at low cost, down to 41% at high cost)

---

## 📋 TEST 1: Basic Spiral Bound - Small Quantity

### Configuration:
```
Quantity: 100
Content Pages: 40
Content Paper Stock: Uncoated Bond 80GSM
Content Print Type: Black & White
Finish Size: A5 Portrait

Outer Front Cover: Not Required
Printed Front Cover: 300GSM Satin
Cover Print Type: 1pp Colour
Celloglaze: None

Outer Back Cover: None
Printed Back Cover: None
Back Cover Print Type: (default)
Back Celloglaze: None

Artworks: 1
```

### Expected Breakdown:
- **BizCost:** $212.04
- **Profit Margin:** 90.0% (low cost tier)
- **Subtotal with Margin:** $402.87
- **15% GST:** $60.43
- **Total after GST:** $463.30
- **Fixed Surcharge:** +$44.00
- **📊 TOTAL PRICE: $507.30**
- **Unit Price:** $5.07/book

### Technical Details:
- Book Thickness: 2.00mm
- Wire Price Per Ring: $0.13065
- Wire Cost Total: $13.06
- Sheets to Punch: 2,205

### Website Testing Steps:
1. Navigate to Spiral Bound Books product page
2. Set **Quantity** = 100
3. Set **Artworks** = 1
4. Set **Outer Front Cover** = "Not Required"
5. Set **Printed Front Cover** = "300GSM Satin"
6. Set **Cover Print Type** = "1pp Colour"
7. Set **Celloglaze** = "None"
8. Set **Outer Back Cover** = "None"
9. Set **Printed Back Cover** = "None"
10. Set **Content Pages** = 40
11. Set **Content Paper Stock** = "Uncoated Bond 80GSM"
12. Set **Content Print Type** = "Black & White"
13. Set **Finish Size** = "A5 Portrait"
14. ✅ **Verify price shows $507.30**

---

## 📋 TEST 2: Medium Quantity with Color Content

### Configuration:
```
Quantity: 500
Content Pages: 100
Content Paper Stock: Satin 128GSM
Content Print Type: Full colour
Finish Size: A4 Portrait

Outer Front Cover: Not Required
Printed Front Cover: 350GSM Satin
Cover Print Type: 2pp Colour
Celloglaze: None

Outer Back Cover: 350GSM Satin Blank
Printed Back Cover: None
Back Cover Print Type: (default)
Back Celloglaze: None

Artworks: 1
```

### Expected Breakdown:
- **BizCost:** $1,680.36
- **Profit Margin:** 75.0%
- **Subtotal with Margin:** $2,940.63
- **15% GST:** $441.10
- **Total after GST:** $3,381.73
- **Fixed Surcharge:** +$44.00
- **📊 TOTAL PRICE: $3,425.73**
- **Unit Price:** $6.85/book

### Technical Details:
- Book Thickness: 6.00mm
- Wire Price Per Ring: $0.13065
- Content Cost: $505.31
- Total Print Cost: $573.56

### Website Testing Steps:
1. Set **Quantity** = 500
2. Set **Artworks** = 1
3. Set **Outer Front Cover** = "Not Required"
4. Set **Printed Front Cover** = "350GSM Satin"
5. Set **Cover Print Type** = "2pp Colour"
6. Set **Celloglaze** = "None"
7. Set **Outer Back Cover** = "350GSM Satin Blank"
8. Set **Printed Back Cover** = "None"
9. Set **Content Pages** = 100
10. Set **Content Paper Stock** = "Satin 128GSM"
11. Set **Content Print Type** = "Full colour"
12. Set **Finish Size** = "A4 Portrait"
13. ✅ **Verify price shows $3,425.73**

---

## 📋 TEST 3: Large Quantity Thick Book

### Configuration:
```
Quantity: 1000
Content Pages: 200
Content Paper Stock: Uncoated Bond 80GSM
Content Print Type: Black & White
Finish Size: A4 Portrait

Outer Front Cover: Not Required
Printed Front Cover: 350GSM Satin
Cover Print Type: 1pp Colour
Celloglaze: None

Outer Back Cover: Black Leather grain
Printed Back Cover: None
Back Cover Print Type: (default)
Back Celloglaze: None

Artworks: 2
```

### Expected Breakdown:
- **BizCost:** $4,533.80
- **Profit Margin:** 55.0%
- **Subtotal with Margin:** $7,027.39
- **15% GST:** $1,054.11
- **Total after GST:** $8,081.50
- **Fixed Surcharge:** +$44.00
- **📊 TOTAL PRICE: $8,125.50**
- **Unit Price:** $8.13/book

### Technical Details:
- Book Thickness: 10.00mm
- Wire Price Per Ring: $0.157 (tier 2)
- Wire Cost Total: $157.00
- Setup Costs (2 artworks): $57.00
- Extra artwork charge: $15.00

### Website Testing Steps:
1. Set **Quantity** = 1000
2. Set **Artworks** = 2  ⚠️ **Extra artwork charge applies**
3. Set **Outer Front Cover** = "Not Required"
4. Set **Printed Front Cover** = "350GSM Satin"
5. Set **Cover Print Type** = "1pp Colour"
6. Set **Celloglaze** = "None"
7. Set **Outer Back Cover** = "Black Leather grain"
8. Set **Printed Back Cover** = "None"
9. Set **Content Pages** = 200
10. Set **Content Paper Stock** = "Uncoated Bond 80GSM"
11. Set **Content Print Type** = "Black & White"
12. Set **Finish Size** = "A4 Portrait"
13. ✅ **Verify price shows $8,125.50**

---

## 📋 TEST 4: Small Format (A6) - Wire Price Halved

### Configuration:
```
Quantity: 250
Content Pages: 50
Content Paper Stock: Uncoated Bond 90GSM
Content Print Type: Black & White
Finish Size: A6 Portrait  ⚠️ WIRE PRICE HALVED

Outer Front Cover: Not Required
Printed Front Cover: 250GSM Satin
Cover Print Type: 1pp Colour
Celloglaze: None

Outer Back Cover: None
Printed Back Cover: None
Back Cover Print Type: (default)
Back Celloglaze: None

Artworks: 1
```

### Expected Breakdown:
- **BizCost:** $427.55
- **Profit Margin:** 90.0%
- **Subtotal with Margin:** $812.35
- **15% GST:** $121.85
- **Total after GST:** $934.21
- **Fixed Surcharge:** +$44.00
- **📊 TOTAL PRICE: $978.21**
- **Unit Price:** $3.91/book

### Technical Details:
- Book Thickness: 2.75mm
- Wire Price Per Ring: $0.13065
- **Wire Cost Total: $16.33 (HALVED for A6)**
- ⚠️ **Small formats (A6/DL/A5 Landscape) use 50% wire cost**

### Website Testing Steps:
1. Set **Quantity** = 250
2. Set **Artworks** = 1
3. Set **Outer Front Cover** = "Not Required"
4. Set **Printed Front Cover** = "250GSM Satin"
5. Set **Cover Print Type** = "1pp Colour"
6. Set **Celloglaze** = "None"
7. Set **Outer Back Cover** = "None"
8. Set **Printed Back Cover** = "None"
9. Set **Content Pages** = 50
10. Set **Content Paper Stock** = "Uncoated Bond 90GSM"
11. Set **Content Print Type** = "Black & White"
12. Set **Finish Size** = "A6 Portrait"  ⚠️ **Check wire cost is halved**
13. ✅ **Verify price shows $978.21**

---

## 📋 TEST 5: Premium Covers with Celloglaze

### Configuration:
```
Quantity: 100
Content Pages: 60
Content Paper Stock: Satin 150GSM
Content Print Type: Full colour
Finish Size: A4 Portrait

Outer Front Cover: Clear PVC
Printed Front Cover: 350GSM Satin
Cover Print Type: 2pp Colour
Celloglaze: 2 Sided Matt  ⚠️ CELLO SETUP $25

Outer Back Cover: Clear PVC
Printed Back Cover: 350GSM Satin
Back Cover Print Type: 1pp Colour
Back Celloglaze: 1 Side Gloss  ⚠️ CELLO SETUP ALREADY ADDED

Artworks: 1
```

### Expected Breakdown:
- **BizCost:** $447.53
- **Profit Margin:** 90.0%
- **Subtotal with Margin:** $850.31
- **15% GST:** $127.55
- **Total after GST:** $977.85
- **Fixed Surcharge:** +$44.00
- **📊 TOTAL PRICE: $1,021.85**
- **Unit Price:** $10.22/book

### Technical Details:
- Front Cello Cost: $43.05
- Back Cello Cost: $21.52
- **Cello Setup: $25.00** (added once when EITHER front OR back has celloglaze)
- Total Setup: $67.00

### Website Testing Steps:
1. Set **Quantity** = 100
2. Set **Artworks** = 1
3. Set **Outer Front Cover** = "Clear PVC"
4. Set **Printed Front Cover** = "350GSM Satin"
5. Set **Cover Print Type** = "2pp Colour"
6. Set **Celloglaze** = "2 Sided Matt"  ⚠️ **$25 setup added**
7. Set **Outer Back Cover** = "Clear PVC"
8. Set **Printed Back Cover** = "350GSM Satin"
9. Set **Back Cover Print Type** = "1pp Colour"
10. Set **Back Celloglaze** = "1 Side Gloss"  ⚠️ **No additional setup (already $25)**
11. Set **Content Pages** = 60
12. Set **Content Paper Stock** = "Satin 150GSM"
13. Set **Content Print Type** = "Full colour"
14. Set **Finish Size** = "A4 Portrait"
15. ✅ **Verify price shows $1,021.85**

---

## 📊 Results Summary

### Fill in after website testing:

| Test | Backend | Website | Difference | Match? |
|------|---------|---------|------------|--------|
| 1 | $507.30 | $_______ | $_______ | ☐ |
| 2 | $3,425.73 | $_______ | $_______ | ☐ |
| 3 | $8,125.50 | $_______ | $_______ | ☐ |
| 4 | $978.21 | $_______ | $_______ | ☐ |
| 5 | $1,021.85 | $_______ | $_______ | ☐ |

**Success Rate:** ___/5 tests passed

---

## 🔍 Pattern Analysis

### Expected Patterns to Verify:

**1. GST Calculation:**
- All tests should show **15% GST** (not 10%)
- GST applied to subtotal with profit margin
- Formula: `subtotal * 1.15`

**2. Fixed Surcharge:**
- All tests should show **+$44** added AFTER GST
- Formula: `(subtotal * 1.15) + 44`

**3. Wire Pricing Tiers (18 tiers):**
- ≤8mm: $0.13065/ring
- ≤10mm: $0.157/ring
- ≤12mm: $0.2242/ring
- (continues to 53mm+)

**4. Small Format Wire Discount:**
- A6 Portrait/Landscape
- DL Landscape
- A5 Landscape
- **Wire cost = (price_per_ring × qty) / 2**

**5. Celloglaze Setup:**
- $25 setup added when EITHER front OR back celloglaze selected
- NOT $25 + $25 for both
- Only ONE $25 charge regardless of how many celloglaze options

**6. Profit Margin Tiers (12 tiers):**
- $1-$500: 90%
- $500-$1000: 90%
- $1000-$1500: 80%
- $1500-$2000: 75%
- $2000-$2500: 70%
- $2500-$3000: 67%
- $3000-$4000: 65%
- $4000-$5000: 55%
- $5000-$7500: 52%
- $7500-$10000: 47%
- $10000-$15000: 42%
- $15000+: 41%

---

## 📝 Notes Section

**Discrepancies Found:**

Test #: _____
Backend: $_____
Website: $_____
Difference: $_____
Possible Cause: _______________________________________________

---

**Additional Observations:**

- ☐ 15% GST correctly applied
- ☐ $44 surcharge present on all tests
- ☐ A6 wire price correctly halved (Test 4)
- ☐ Celloglaze setup $25 (not $50) on Test 5
- ☐ Profit margins match cost tiers
- ☐ Wire pricing matches thickness tiers

---

## ✅ Validation Checklist

- [ ] All 5 test configurations entered correctly
- [ ] All prices recorded from website
- [ ] Discrepancies documented with root cause analysis
- [ ] Pattern validation complete (GST, surcharge, wire pricing)
- [ ] Update methodology document with results
- [ ] Mark calculator as validated if all tests pass

---

**Next Steps:**
1. Complete website testing (fill in prices above)
2. Document any discrepancies
3. Update `SHOPIFY_CALCULATOR_JSON_FIRST_METHODOLOGY.md`
4. If validated, move to next calculator (Wire Bound Books)
