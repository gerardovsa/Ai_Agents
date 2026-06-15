# Perfect Bound Books Calculator - Test Configurations

## Calculator Name
**Perfect Bound Books**

## AI Instructions for Testing

To get a quote for Perfect Bound Books:

```
Please calculate a quote for Perfect Bound Books with these specifications:
[paste specifications from tests below]
```

All prices listed below include GST and are actual website results.

---

# Perfect Bound Books - Actual Website Test Configurations

## TEST 1: Standard Catalogue A5

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 100
- Printed Pages: 100
- Proof Requirements: Digital Emailed Proof
- Finish Size: A5 Portrait

**Cover**
- Cover Stock: Satin 300GSM
- Cover Print Type: 2 side colour (4pp)
- Celloglaze: None

**Contents**
- Content Print Type: Black & White
- Content Stock Type: Uncoated Bond 100GSM

**Regular price: $603.97**

---

## TEST 2: Product Manual A4 with Celloglaze

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 200
- Printed Pages: 200
- Proof Requirements: Digital Emailed Proof
- Finish Size: A4 Portrait

**Cover**
- Cover Stock: Satin 300GSM
- Cover Print Type: 2 side colour (4pp)
- Celloglaze: Gloss outside only

**Contents**
- Content Print Type: Full Colour
- Content Stock Type: Satin 128GSM

**Regular price: $4,478.63**

---

## TEST 3: Large Format Catalogue A4 Landscape

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 500
- Printed Pages: 300
- Proof Requirements: Physical Proof
- Finish Size: A4 Landscape

**Cover**
- Cover Stock: Satin 300GSM
- Cover Print Type: 2 side colour (4pp)
- Celloglaze: Matt outside only

**Contents**
- Content Print Type: Full Colour
- Content Stock Type: Satin 150GSM

**Regular price: $13,060.10**

---

## TEST 4: Trade Paperback US Trade Size

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 50
- Printed Pages: 80
- Proof Requirements: Digital Emailed Proof
- Finish Size: US Trade (152mm x 229mm)

**Cover**
- Cover Stock: Satin 300GSM
- Cover Print Type: 1 side colour (2pp)
- Celloglaze: None

**Contents**
- Content Print Type: Black & White
- Content Stock Type: Uncoated Bond 80GSM

**Regular price: $426.09**

---

## TEST 5: Bulk Booklet Best Value

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 1000
- Printed Pages: 40 (minimum)
- Proof Requirements: Digital Emailed Proof
- Finish Size: A5 Portrait

**Cover**
- Cover Stock: Satin 300GSM
- Cover Print Type: 2 side colour (4pp)
- Celloglaze: Gloss outside only

**Contents**
- Content Print Type: Black & White
- Content Stock Type: Uncoated Bond 90GSM

**Regular price: $4,244.11**

---

## Technical Notes (Internal Reference)

### Validation Status:
- **Total Tests:** 5 (all website validated)
- **Accuracy:** 100% validated
- **Date Validated:** January 23-24, 2026
- **Status:** All tests validated ✅

### Test Coverage:
- **Test 1:** Standard catalogue (100 qty, 100 pages, A5 Portrait, B&W internals)
- **Test 2:** Product manual (200 qty, 200 pages, A4 Portrait, colour internals, celloglaze)
- **Test 3:** Large format (500 qty, 300 pages, A4 Landscape, colour, physical proof)
- **Test 4:** Trade paperback (50 qty, 80 pages, US Trade size, B&W, 1-side colour cover)
- **Test 5:** Bulk budget (1000 qty, 40 pages minimum, A5, B&W, best value)

### Business Rules:
- **Page Counts:** Must be divisible by 4 (40-800 pages range)
- **Sizes:** A5 Portrait, A4 Portrait, A4 Landscape, US Trade (152mm x 229mm)
- **Proof Options:** Digital Emailed Proof ($0), Physical Proof Required (+$40)
- **Cover Stock:** Satin 300GSM (standard) - no other options
- **Cover Print:** 1 side colour (2pp), 2 side colour (4pp), 1/2 side B&W
- **Celloglaze:** None, Gloss outside only, Matt outside only
- **Content Print:** Full Colour (expensive), Black & White (economical)
- **Content Stock:** Satin (128-150GSM), Uncoated Bond (80-100GSM)
- **NO Artworks Parameter:** Uses proof system instead (unique to Perfect Bound)
- **Binding:** Quantity-based tiered rates (8 tiers)
- **Profit Margins:** BizCost-based tiers (12 tiers)
- **GST:** 10% standard (no double GST like other book calculators)
- **NO Surcharge:** Unlike Wire Bound ($44 surcharge), Perfect Bound has $0 surcharge

### Key Differences from Other Book Calculators:
- **NO Double GST:** Only ×1.1 (10% standard GST) - NOT ×1.1 ×1.1
- **NO Artworks:** Uses proof system instead (Digital $0 / Physical $40)
- **NO Surcharge:** $0 surcharge (Wire/Spiral have $44)
- **Cover Simplicity:** Single cover stock option (Satin 300GSM only)
- **Page Range:** 40-800 pages (wider than Saddle Stitch's 4-48pp limit)

### Formula Components:
```
Setup Costs:
  - Base: $57 (imposition $15 + guillotine $12 + binder $30)
  - Celloglaze setup: +$25 (if Gloss or Matt selected)
  - Proof: $0 (digital) or $40 (physical)
  - NO artwork costs (proof system used instead)

Cover Cost: Sheets × (Stock + Print + Celloglaze)

Content Cost: Sheets × (Stock + Print)

Cutting Cost: (Total Sheets / 500) × $11

Binding Cost: Quantity-based tier (8 tiers)

Subtotal = Setup + Cover + Content + Cutting + Binding
With Margin = Subtotal × (1 + Tier%)
Final Price = With Margin × 1.10  ← SINGLE GST (standard 10%)
```

### Size Characteristics:
- **A5 Portrait:** Most economical (fits 2 per A4 parent sheet)
- **A4 Portrait:** Standard catalog size
- **A4 Landscape:** Wide format, no surcharge (unlike Saddle Stitch)
- **US Trade:** 152mm × 229mm (popular paperback book format)

---

## CONSOLIDATED TEST BLOCK

```
Calculate quotes for Perfect Bound Books with these specifications:

**Test 1 - Standard Catalogue ($603.97):** ✅ VALIDATED
Quantity: 100 books
Printed Pages: 100
Proof: Digital Emailed Proof
Finish Size: A5 Portrait
Cover Stock: Satin 300GSM
Cover Print: 2 side colour (4pp)
Celloglaze: None
Content Print: Black & White
Content Stock: Uncoated Bond 100GSM

**Test 2 - Product Manual ($4,478.63):** ✅ VALIDATED
Quantity: 200 books
Printed Pages: 200
Proof: Digital Emailed Proof
Finish Size: A4 Portrait
Cover Stock: Satin 300GSM
Cover Print: 2 side colour (4pp)
Celloglaze: Gloss outside only
Content Print: Full Colour
Content Stock: Satin 128GSM

**Test 3 - Large Catalogue ($13,060.10):** ✅ VALIDATED
Quantity: 500 books
Printed Pages: 300
Proof: Physical Proof
Finish Size: A4 Landscape
Cover Stock: Satin 300GSM
Cover Print: 2 side colour (4pp)
Celloglaze: Matt outside only
Content Print: Full Colour
Content Stock: Satin 150GSM

**Test 4 - Trade Paperback ($426.09):** ✅ VALIDATED
Quantity: 50 books
Printed Pages: 80
Proof: Digital Emailed Proof
Finish Size: US Trade
Cover Stock: Satin 300GSM
Cover Print: 1 side colour (2pp)
Celloglaze: None
Content Print: Black & White
Content Stock: Uncoated Bond 80GSM

**Test 5 - Bulk Budget ($4,244.11):** ✅ VALIDATED
Quantity: 1000 books
Printed Pages: 40 (minimum)
Proof: Digital Emailed Proof
Finish Size: A5 Portrait
Cover Stock: Satin 300GSM
Cover Print: 2 side colour (4pp)
Celloglaze: Gloss outside only
Content Print: Black & White
Content Stock: Uncoated Bond 90GSM

✅ **All tests validated** - Backend matches website prices
```

---

## VALIDATION RESULTS

| Test | Configuration | Backend | Website | Per Unit | Status |
|------|--------------|---------|---------|----------|--------|
| 1 | 100 A5 100pp B&W | $603.97 | $603.97 | $6.04 | ✅ VALIDATED |
| 2 | 200 A4 200pp Colour Celloglaze | $4,478.63 | $4,478.63 | $22.39 | ✅ VALIDATED |
| 3 | 500 A4L 300pp Colour Physical Proof | $13,060.10 | $13,060.10 | $26.12 | ✅ VALIDATED |
| 4 | 50 US Trade 80pp B&W | $426.09 | $426.09 | $8.52 | ✅ VALIDATED |
| 5 | 1000 A5 40pp B&W | $4,244.11 | $4,244.11 | $4.24 | ✅ VALIDATED |

**Overall Accuracy:** 5/5 tests validated = 100% ✅  
**Best Value:** Test 5 @ $4.24/unit (1000 qty, minimum pages)  
**Status:** ALL TESTS VALIDATED - Calculator is production ready!

---

## USAGE RECOMMENDATIONS

### ✅ USE WITH CONFIDENCE
- All test configurations validated
- All sizes tested (A5, A4, A4 Landscape, US Trade)
- Page range tested (40-300 pages, full spectrum)
- Celloglaze options validated (None, Gloss, Matt)
- Proof options validated (Digital $0, Physical $40)
- Both print types validated (Colour, B&W)
- Quantity range validated (50-1000 books)

### 💡 INTELLIGENT QUOTING TIPS
1. **Best value: Minimum pages + high quantity** - Test 5 shows $4.24/unit with 40pp × 1000 qty
2. **Colour internals expensive** - Test 2 @ $22.39/unit vs Test 1 @ $6.04/unit (3.7× cost)
3. **A5 Portrait most economical** - Double sheets per parent sheet reduces material cost
4. **Physical proof adds $40** - Only 8¢/unit at 500 qty (Test 3), but 80¢/unit at 50 qty
5. **Page count impact** - 300pp @ $26.12/unit (Test 3) vs 40pp @ $4.24/unit (Test 5) = 6× cost
6. **US Trade size popular** - Standard paperback format (152×229mm) between A5 and A4
7. **NO double GST** - Perfect Bound uses standard 10% GST (cheaper than Saddle Stitch)

### 📊 TYPICAL USE CASES
- **Product catalogues** - Test 1 (100 qty, 100pp, A5, B&W, economical)
- **Corporate reports** - Test 2 (200 qty, colour internals, celloglaze, professional)
- **Trade books** - Test 4 (US Trade size, standard paperback format)
- **Marketing materials** - Test 5 (bulk 1000 qty, short 40pp, best per-unit price)
- **Large catalogs** - Test 3 (300pp, A4 Landscape, wide format)

---

## TECHNICAL DETAILS

### Calculation Formula
```
1. Setup = $57 + [Celloglaze $25] + [Physical Proof $40]
2. Cover = Sheets × (Stock + Print + [Celloglaze rate])
3. Content = Sheets × (Stock + Print)
4. Cutting = (Sheets / 500) × $11
5. Binding = Quantity-based tier rate (8 tiers)
6. Subtotal = Setup + Cover + Content + Cutting + Binding
7. With Margin = Subtotal × (1 + Tier%)
8. Final = With Margin × 1.10  ← SINGLE GST (standard 10%)
```

### Parameter Formats
- `quantity`: Integer (1-20,000 range)
- `printed_pages`: Integer divisible by 4 (40-800 range)
- `proof_requirements`: "Digital Emailed Proof" | "Physical Proof Required"
- `cover_stock`: "Satin 300GSM" (only option)
- `cover_print_type`: "1 side colour (2pp)" | "2 side colour (4pp)" | "1 side B&W (2pp)" | "2 side B&W (4pp)"
- `celloglaze`: "None" | "Gloss outside only" | "Matt outside only"
- `finish_size`: "A5 Portrait" | "A4 Portrait" | "A4 Landscape" | "US Trade"
- `content_print_type`: "Full Colour" | "Black & White"
- `content_stock_type`: "Satin 128GSM" | "Satin 150GSM" | "Uncoated Bond 80GSM" | "Uncoated Bond 90GSM" | "Uncoated Bond 100GSM"

---

**Document Version:** 1.0  
**Last Updated:** January 27, 2026  
**Validation Status:** 5/5 tests validated ✅ 100% COMPLETE  
**Calculator File:** `PerfectBound_Shopify_Calculator.py`  
**Website:** https://inhouseprint.com.au/product/perfect-bound-books/
**Calculator Status:** PRODUCTION READY  
**Key Difference:** Standard 10% GST (NOT double GST like other book calculators)
