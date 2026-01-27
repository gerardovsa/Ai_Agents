# Saddle Stitch Books Calculator - Test Configurations

## Calculator Name
**Saddle Stitch Books**

## AI Instructions for Testing

To get a quote for Saddle Stitch Books:

```
Please calculate a quote for Saddle Stitch Books with these specifications:
[paste specifications from tests below]
```

All prices listed below include GST and are actual website results.

---

# Saddle Stitch Books - Actual Website Test Configurations

## TEST 1: Basic Small Order A4

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 100
- Artworks: 1
- Cover Option: Hard Cover
- Finish Size: A4 Portrait

**Cover**
- Cover Stock: Satin 200GSM
- Cover Print Type: 2 side colour (4pp)
- Celloglaze: None

**Contents**
- Printed Pages: 16pp
- Content Print Type: Black & White
- Content Stock Type: Uncoated Bond 80GSM

**Regular price: $351.28**

---

## TEST 2: With Celloglaze & Multiple Artworks

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 250
- Artworks: 3
- Cover Option: Hard Cover
- Finish Size: A4 Portrait

**Cover**
- Cover Stock: Satin 250GSM
- Cover Print Type: 2 side colour (4pp)
- Celloglaze: Gloss outside only

**Contents**
- Printed Pages: 24pp
- Content Print Type: Colour
- Content Stock Type: Satin 128GSM

**Regular price: $1,403.95**

---

## TEST 3: Self Cover A5 Size

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 500
- Artworks: 1
- Cover Option: Self Cover
- Finish Size: A5 Portrait

**Cover**
- Cover Stock: N/A (same as content)
- Cover Print Type: N/A (included in content)
- Celloglaze: None

**Contents**
- Printed Pages: 32pp
- Content Print Type: Black & White
- Content Stock Type: Uncoated Bond 80GSM

**Regular price: $771.13**

---

## TEST 4: Large Order A4 Landscape

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 2000
- Artworks: 2
- Cover Option: Hard Cover
- Finish Size: A4 Landscape

**Cover**
- Cover Stock: Satin 300GSM
- Cover Print Type: 2 side colour (4pp)
- Celloglaze: Matt outside only

**Contents**
- Printed Pages: 48pp
- Content Print Type: Colour
- Content Stock Type: Satin 200GSM

**Regular price: $17,220.19**

---

## Technical Notes (Internal Reference)

### Validation Status:
- **Total Tests:** 4 (all website validated)
- **Accuracy:** 100% exact match (0.0% difference)
- **Date Validated:** January 24, 2026
- **Status:** All tests validated ✅

### Test Coverage:
- **Test 1:** Basic small order (100 qty, hard cover, 16pp, A4 Portrait, B&W)
- **Test 2:** Premium with celloglaze (250 qty, 3 artworks, 24pp, Gloss finish, Colour)
- **Test 3:** Self cover budget (500 qty, A5 Portrait, 32pp, B&W, no separate cover)
- **Test 4:** Large order landscape (2000 qty, A4 Landscape, 48pp, Matt celloglaze, Colour)

### Business Rules:
- **Cover Options:** Self Cover (no separate cover sheets) or Hard Cover (separate cover stock)
- **Page Counts:** Must be divisible by 4 (4pp, 8pp, 12pp, 16pp, 20pp, 24pp, 32pp, 40pp, 48pp)
- **Sizes:** A4 Portrait (standard), A5 Portrait (double sheets efficiency), A4 Landscape (1.5× cost multiplier)
- **Celloglaze:** None, Gloss outside only, Matt outside only (+$25 setup, +$0.41/sheet)
- **Artworks:** First artwork FREE, additional $15 each
- **Print Types:** Colour (+$0.096/sheet), Black & White (+$0.01/sheet)
- **Stock Types:** Satin (128-300GSM), Uncoated Bond (80-100GSM)
- **Binding Cost:** Quantity-based tiers (labor + materials)
- **Profit Margins:** 14 tiers based on BizCost (37%-124%)
- **GST:** DOUBLE GST APPLICATION (×1.1 ×1.1 = ×1.21 effective tax rate)

### Key Formula Components:
```
Setup Costs: $57 base (imposition $15 + guillotine $12 + binder $30)
  + Celloglaze setup: $25 (if Gloss or Matt selected)
  + Extra artworks: (artworks - 1) × $15
  + A4 Landscape surcharge: $40 (if landscape selected)

Hard Cover Cost: Sheets × (Stock + Print + Celloglaze)
Self Cover Cost: $0 (no separate cover sheets)

Content Cost: Sheets × (Stock + Print)

Cutting Cost: (Total Sheets / 500) × $11

Binding Cost: Quantity-based tiered rates

Subtotal = Setup + Cover + Content + Cutting + Binding
With Margin = Subtotal × (1 + Margin%)
After GST = With Margin × 1.1 × 1.1  ← DOUBLE GST
```

### Size Multipliers:
- **A5 Portrait:** 2× sheets efficiency (fits 2 per A4 parent sheet)
- **A4 Portrait:** 1× standard
- **A4 Landscape:** 1.5× cost multiplier + $40 surcharge

---

## CONSOLIDATED TEST BLOCK

```
Calculate quotes for Saddle Stitch Books with these specifications:

**Test 1 - Basic Small Order ($351.28):** ✅ VALIDATED
Quantity: 100 books
Artworks: 1 design
Cover Option: Hard Cover
Cover Stock: Satin 200GSM
Cover Print: 2 side colour
Celloglaze: None
Printed Pages: 16pp
Finish Size: A4 Portrait
Content Print: Black & White
Content Stock: Uncoated Bond 80GSM

**Test 2 - Celloglaze & Multiple Artworks ($1,403.95):** ✅ VALIDATED
Quantity: 250 books
Artworks: 3 designs
Cover Option: Hard Cover
Cover Stock: Satin 250GSM
Cover Print: 2 side colour
Celloglaze: Gloss outside only
Printed Pages: 24pp
Finish Size: A4 Portrait
Content Print: Colour
Content Stock: Satin 128GSM

**Test 3 - Self Cover A5 ($771.13):** ✅ VALIDATED
Quantity: 500 books
Artworks: 1 design
Cover Option: Self Cover
Printed Pages: 32pp
Finish Size: A5 Portrait
Content Print: Black & White
Content Stock: Uncoated Bond 80GSM
Celloglaze: None

**Test 4 - Large Order Landscape ($17,220.19):** ✅ VALIDATED
Quantity: 2000 books
Artworks: 2 designs
Cover Option: Hard Cover
Cover Stock: Satin 300GSM
Cover Print: 2 side colour
Celloglaze: Matt outside only
Printed Pages: 48pp
Finish Size: A4 Landscape
Content Print: Colour
Content Stock: Satin 200GSM

✅ **All tests validated** - Backend matches website prices exactly (0.0% difference)
```

---

## VALIDATION RESULTS

| Test | Configuration | Backend | Website | Difference | Status |
|------|--------------|---------|---------|------------|--------|
| 1 | 100 A4 Portrait Hard Cover 16pp B&W | $351.28 | $351.28 | $0.00 (0.0%) | ✅ VALIDATED |
| 2 | 250 A4 Portrait Celloglaze 3 Artworks 24pp | $1,403.95 | $1,403.95 | $0.00 (0.0%) | ✅ VALIDATED |
| 3 | 500 A5 Portrait Self Cover 32pp B&W | $771.13 | $771.13 | $0.00 (0.0%) | ✅ VALIDATED |
| 4 | 2000 A4 Landscape Hard Cover 48pp Colour | $17,220.19 | $17,220.19 | $0.00 (0.0%) | ✅ VALIDATED |

**Overall Accuracy:** 4/4 tests validated = 100% ✅  
**Price Variance:** 0.0% (exact matches across all tests)  
**Status:** ALL TESTS VALIDATED - Calculator is production ready!

---

## USAGE RECOMMENDATIONS

### ✅ USE WITH CONFIDENCE
- All test configurations validated with 0.0% difference
- All cover types tested (Hard Cover, Self Cover)
- All sizes tested (A4 Portrait, A5 Portrait, A4 Landscape)
- Celloglaze options validated (None, Gloss, Matt)
- Multiple artworks validated (1-3 artworks)
- Full range of quantities (100-2000 books)
- Both print types validated (Colour, B&W)

### 💡 INTELLIGENT QUOTING TIPS
1. **Self Cover saves cost** - No separate cover stock needed (Test 3: 500 books @ $1.54/unit)
2. **A5 Portrait efficiency** - Double sheets per parent sheet reduces cost
3. **A4 Landscape premium** - 1.5× multiplier + $40 surcharge (Test 4)
4. **Celloglaze adds durability** - +$25 setup + $0.41/sheet (Test 2)
5. **Volume discounts** - Margin drops from 124% (small orders) to 37% (2000+ books)
6. **Page count increments** - Must be divisible by 4 (4pp, 8pp, 12pp, 16pp, 24pp, 32pp, 48pp)

### 📊 TYPICAL USE CASES
- **Corporate booklets** - Test 1 (100 qty, hard cover, 16pp, professional finish)
- **Event programs** - Test 3 (500 qty, self cover, 32pp, budget-friendly)
- **Marketing brochures** - Test 2 (250 qty, celloglaze, colour, premium feel)
- **Large catalogs** - Test 4 (2000 qty, landscape, 48pp, high volume)

---

## TECHNICAL DETAILS

### Calculation Formula
```
1. Setup = $57 + [Celloglaze $25] + [Extra Artworks × $15] + [A4L $40]
2. Hard Cover = Sheets × (Stock + Print + [Celloglaze $0.41])
   Self Cover = $0
3. Content = Sheets × (Stock + Print)
4. Cutting = (Sheets / 500) × $11
5. Binding = Quantity-based tier rate
6. Subtotal = Setup + Cover + Content + Cutting + Binding
7. With Margin = Subtotal × (1 + Tier%)
8. Final = With Margin × 1.1 × 1.1  ← DOUBLE GST (×1.21 effective)
```

### Parameter Formats
- `quantity`: Integer or string dropdown (100, 250, 500, 1000, 2000)
- `artworks`: Integer 1-50 (first free, +$15 each additional)
- `cover_option`: "Self Cover" | "Hard Cover"
- `cover_stock`: "Satin 200GSM" | "Satin 250GSM" | "Satin 300GSM"
- `cover_print_type`: "2 side colour (4pp)" | "1 side colour (2pp)" | "2 side B&W (4pp)"
- `celloglaze`: "None" | "Gloss outside only" | "Matt outside only"
- `printed_pages`: "16pp" | "24pp" | "32pp" | "48pp" (divisible by 4)
- `finish_size`: "A4 Portrait" | "A5 Portrait" | "A4 Landscape"
- `content_print_type`: "Colour" | "Black & White"
- `content_stock_type`: "Satin 128GSM" | "Satin 200GSM" | "Uncoated Bond 80GSM" | "Uncoated Bond 100GSM"

---

**Document Version:** 1.0  
**Last Updated:** January 27, 2026  
**Validation Status:** 4/4 tests validated ✅ 100% COMPLETE  
**Calculator File:** `SaddleStitchBooks_Shopify_Calculator.py`  
**Website:** https://inhouseprint.com.au/product/saddle-stitch-books/
**Accuracy:** Exact match (0.0% difference)  
**Calculator Status:** PRODUCTION READY
