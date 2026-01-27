# SHOPIFY CALCULATOR WEBSITE VALIDATION CHECKLIST
**Created:** January 24, 2026  
**Status:** Ready for validation

---

## 🎯 CALCULATORS TO VALIDATE (3)

### 1. BUSINESS CARDS - ECONOMICAL ⚠️

**Website URL:** https://inhouseprint.com.au/product/business-cards/ (Economical version)

**Test Configurations:**

#### TEST 1: 500 Single-sided Color
```
Quantity: 500
Sides: Single side print
Print Type: Colour
Finish Size: 90mm x 55mm
Paper Stock: Satin 300GSM
Artworks: 1

Backend Price: $57.72
Website Price: _____________
Status: ⬜ PASS / ⬜ FAIL
```

#### TEST 2: 1000 Double-sided Color, 3 artworks
```
Quantity: 1000
Sides: Double side print
Print Type: Colour
Finish Size: 90mm x 55mm
Paper Stock: Satin 300GSM
Artworks: 3

Backend Price: $121.09
Website Price: _____________
Status: ⬜ PASS / ⬜ FAIL
```

#### TEST 3: 250 Single-sided B&W
```
Quantity: 250
Sides: Single side print
Print Type: Black & White
Finish Size: 90mm x 55mm
Paper Stock: Satin 300GSM
Artworks: 1

Backend Price: $52.82
Website Price: _____________
Status: ⬜ PASS / ⬜ FAIL
Notes: TXT range $50-80 (backend IN RANGE ✅)
```

#### TEST 4: 5000 Double-sided Color
```
Quantity: 5000
Sides: Double side print
Print Type: Colour
Finish Size: 90mm x 55mm
Paper Stock: Satin 300GSM
Artworks: 1

Backend Price: $151.36
Website Price: _____________
Status: ⬜ PASS / ⬜ FAIL
```

---

### 2. PERFECT BOUND BOOKS ⚠️

**Website URL:** https://inhouseprint.com.au/product/perfect-bound-books/

**Test Configurations:**

#### TEST 1: Standard B&W Novel (500 books, 200 pages)
```
Quantity: 500
Printed Pages: 200
Finish Size: A5 Portrait
Cover Stock: Satin 300GSM
Cover Print Type: 2 side colour (4pp)
Celloglaze: Matt outside only
Content Print Type: Black & White
Content Stock Type: Uncoated Bond 100GSM
Proof Requirements: Digital Emailed Proof

Backend Price: $4,254.47
Website Price: _____________
Status: ⬜ PASS / ⬜ FAIL

Backend Breakdown:
  Setup: $111.00
  Cover: $123.90
  Content: $711.38
  Celloglaze: $99.75
  Cutting: $300.30
  Binding: $650.00 ($1.30/book)
  BizCost: $1,996.32
  Profit (72%): $1,437.35
  Overs (12 books): $82.41
  GST (double): $738.38
```

#### TEST 2: Full Color Magazine (250 books, 48 pages)
```
Quantity: 250
Printed Pages: 48
Finish Size: A4 Portrait
Cover Stock: Satin 300GSM
Cover Print Type: 2 side colour (4pp)
Celloglaze: Gloss outside only
Content Print Type: Full Colour
Content Stock Type: Satin 128GSM
Proof Requirements: Physical Unbound Proof

Backend Price: $2,343.00
Website Price: _____________
Status: ⬜ PASS / ⬜ FAIL

Backend Breakdown:
  Includes: Physical Proof ($40) + 8 extra books
  Profit Margin: 60%
```

#### TEST 3: Small A5 Book (100 books, 40 pages)
```
Quantity: 100
Printed Pages: 40
Finish Size: A5 Portrait
Cover Stock: Satin 300GSM
Cover Print Type: 2 side colour (4pp)
Celloglaze: None
Content Print Type: Black & White
Content Stock Type: Uncoated Bond 80GSM (cheapest)
Proof Requirements: Digital Emailed Proof

Backend Price: $552.17
Website Price: _____________
Status: ⬜ PASS / ⬜ FAIL

Backend Breakdown:
  Profit Margin: 40% (lowest tier)
  Bind cost: $1.25/book (lowest quantity tier)
```

#### TEST 4: Large Volume Order (5000 books)
```
Quantity: 5000
Printed Pages: 100
Finish Size: A4 Portrait
Cover Stock: Satin 300GSM
Cover Print Type: 2 side colour (4pp)
Celloglaze: None
Content Print Type: Black & White
Content Stock Type: Uncoated Bond 100GSM
Proof Requirements: Digital Emailed Proof

Backend Price: $28,627.96
Website Price: _____________
Status: ⬜ PASS / ⬜ FAIL

Backend Breakdown:
  Profit Margin: 41% (high volume tier)
  Bind cost: $0.70/book (volume discount)
  Unit price: $5.73/book
```

#### TEST 5: US Trade Size (1000 books)
```
Quantity: 1000
Printed Pages: 200
Finish Size: US Trade - 152mm x 229mm
Cover Stock: Satin 300GSM
Cover Print Type: 1 side colour (2pp) (front only)
Celloglaze: None
Content Print Type: Black & White
Content Stock Type: Uncoated Bond 90GSM
Proof Requirements: Digital Emailed Proof

Backend Price: $9,973.67
Website Price: _____________
Status: ⬜ PASS / ⬜ FAIL
```

---

### 3. SPIRAL BOUND BOOKS ⚠️

**Website URL:** https://inhouseprint.com.au/product/spiral-bound-books/

**Backend Status:** Rewritten with exact TXT formula (15% GST + $44 surcharge)

**Test Configurations:** *(Create 4 test cases covering different sizes, page counts, cover options)*

#### TEST 1: Standard Configuration (NEEDS CONFIGURATION)
```
Quantity: ___________
Printed Pages: ___________
Finish Size: ___________
Front Cover: ___________
Back Cover: ___________
Wire Color: ___________
Content Print Type: ___________
Content Stock Type: ___________

Backend Price: $___________ (run test first)
Website Price: _____________
Status: ⬜ PASS / ⬜ FAIL
```

#### TEST 2: Different Configuration (NEEDS CONFIGURATION)
```
[Copy configuration from website]

Backend Price: $___________ (run test first)
Website Price: _____________
Status: ⬜ PASS / ⬜ FAIL
```

---

## 📋 VALIDATION CRITERIA

**Success Criteria:**
- ✅ **PASS:** Website price matches backend within **$1.00 OR 1%** (whichever is larger)
- ❌ **FAIL:** Difference exceeds tolerance

**Common Issues to Watch For:**
1. **Double GST:** Perfect Bound uses double GST (×1.1 ×1.1 = ×1.21)
2. **Artwork placement:** Check if website adds artwork before or after profit
3. **Setup costs:** Verify all setup costs match (imposition, guillotine, etc.)
4. **Tier boundaries:** Test near tier breakpoints (e.g., 499 vs 501 quantity)
5. **Options interaction:** Check mutually exclusive vs combined options

---

## 🔧 HOW TO USE THIS CHECKLIST

### For Business Cards - Economical:
1. Open: https://inhouseprint.com.au/product/business-cards/
2. Select "Economical" or standard version (not Premium)
3. Configure each test exactly as shown
4. Record website price in checklist
5. Calculate difference: `|Website - Backend|`
6. Mark PASS if within $1.00 or 1%

### For Perfect Bound Books:
1. Open: https://inhouseprint.com.au/product/perfect-bound-books/
2. Configure each test exactly as shown
3. **Pay attention to:** Celloglaze options, proof type, stock types
4. Record website price
5. Compare to backend breakdown to identify discrepancies

### For Spiral Bound Books:
1. Open: https://inhouseprint.com.au/product/spiral-bound-books/
2. Create 4 diverse test configurations
3. Run backend test script first to get expected prices
4. Compare website results

---

## 📊 VALIDATION RESULTS SUMMARY

| Calculator | Total Tests | Passed | Failed | Notes |
|------------|-------------|--------|--------|-------|
| Business Cards - Economical | 4 | ___ | ___ | TXT ranges appear to be estimates |
| Perfect Bound Books | 5 | ___ | ___ | Double GST (×1.21 total) |
| Spiral Bound Books | 4 | ___ | ___ | 15% GST + $44 surcharge |
| **TOTAL** | **13** | **___** | **___** | |

---

## 🚀 NEXT STEPS AFTER VALIDATION

### If All Tests PASS:
1. Update methodology file status from ⚠️ to ✅
2. Add validation results with dates
3. Document any minor differences (within tolerance)
4. Move to next calculator batch

### If Tests FAIL:
1. Document exact discrepancy (which component differs)
2. Re-read TXT formula for that calculator
3. Compare backend implementation to TXT step-by-step
4. Check for:
   - Missing multipliers
   - Tier value errors
   - Order of operations issues
   - Conditional logic errors
5. Fix backend, re-test, re-validate

---

## 📝 NOTES FROM DEVELOPER

**Expected Outcome - Business Cards Economical:**
- Backend prices are 20-60% lower than TXT estimated ranges
- This is likely CORRECT - TXT ranges appear to be rough estimates for guidance
- Website validation will confirm if backend formula is accurate
- Test 3 ($52.82) falls within TXT range $50-80, suggesting formula is correct

**Expected Outcome - Perfect Bound Books:**
- Backend implements double GST as per JSON specification
- This matches Premium Business Cards validated pattern ($162.09 vs $161.70 website)
- Should see exact or very close matches on all 5 tests

**Expected Outcome - Spiral Bound Books:**
- Backend completely rewritten with exact TXT formula
- Uses 15% GST (not 10%) + $44 surcharge (not double GST)
- Different pattern from other book calculators
- 18-tier wire pricing based on book thickness

---

**Last Updated:** January 24, 2026  
**Ready for Website Testing:** ✅ YES
