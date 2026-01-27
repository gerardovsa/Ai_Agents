# Printed Letterheads Calculator - Test Configurations

## Calculator Name
**printed_letterheads**

## AI Instructions for Testing

To get a quote for Printed Letterheads:

```
Please calculate a quote for Printed Letterheads with these specifications:
[paste specifications from tests below]
```

All prices listed below include GST and are actual website results.

---

# Printed Letterheads - Actual Website Test Configurations

## TEST 1: Baseline Medium Quantity Single Sided Colour

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 250
- Artworks: 1
- Sides: Single side
- Print Type: Colour
- Stock Type: Uncoated Bond 80GSM

**Regular price: $127.80**

---

## TEST 2: High Volume Double Sided B&W Multiple Artworks

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 5000
- Artworks: 2
- Sides: Double side
- Print Type: Black & White
- Stock Type: Uncoated Bond 100GSM

**Regular price: $597.63**

---

## TEST 3: Medium Quantity Double Sided Colour

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 1000
- Artworks: 1
- Sides: Double side
- Print Type: Colour
- Stock Type: Uncoated Bond 90GSM

**Regular price: $285.04**

---

## TEST 4: Edge Case Minimum Quantity Single Sided B&W

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 50
- Artworks: 1
- Sides: Single side
- Print Type: Black & White
- Stock Type: Uncoated Bond 80GSM

**Regular price: $94.07**

---

## Technical Notes (Internal Reference)

### Backend Rewrite Complete - January 26, 2026

**Key Formula Components:**
- **Setup Costs:**
  - Base Setup: $27 (Imposition $15 + Guillotine $12)
  - Extra Artworks: $15 per additional artwork
- **Sheets Per Letterhead:** 2 letterheads per sheet (A4 size, uses F4.price)
- **Stock Prices (per 1000 sheets):**
  - 80GSM Uncoated Bond: $26.34
  - 90GSM Uncoated Bond: $29.51
  - 100GSM Uncoated Bond: $32.68
- **Print Costs (per sheet):**
  - Colour: $0.044 per side
  - Black & White: $0.02 per side
- **Cut Cost:** $11
- **Profit Margins:** 11-tier system based on subtotal

### Validation Status:
- **Total Tests:** 4 (all validated)
- **Accuracy:** 100% perfect match
- **Date Validated:** January 26, 2026
- **Status:** Backend rewrite complete ✅

### Business Rules:
- **Size:** A4 format (210mm × 297mm) - fixed
- **Sides:** Single or Double sided printing
- **Print Types:** Colour or Black & White
- **Stock Options:** 80GSM, 90GSM, or 100GSM Uncoated Bond
- **Artwork Pricing:** First artwork included, $15 per additional
- **Imposition:** 2 letterheads per sheet (F4.price sheet size)
- **Sheet Calculation:** quantity ÷ 2 sheets needed
- **GST:** 10% applied to final price

### Test Coverage:
- **Test 1:** Baseline configuration (250 qty, single, colour, 80GSM, 1 art) - 170% margin
- **Test 2:** High volume with extras (5000 qty, double, B&W, 100GSM, 2 arts) - 70% margin
- **Test 3:** Medium double-sided colour (1000 qty, double, colour, 90GSM, 1 art) - 135% margin
- **Test 4:** Minimum quantity edge case (50 qty, single, B&W, 80GSM, 1 art) - 170% margin
