# With Compliments Slips Calculator - Test Configurations

## Calculator Name
**with_compliments_slips**

## AI Instructions for Testing

To get a quote for With Compliments Slips:

```
Please calculate a quote for With Compliments Slips with these specifications:
[paste specifications from tests below]
```

All prices listed below include GST and are actual website results.

---

# With Compliments Slips - Actual Website Test Configurations

## TEST 1: Medium Quantity Single Sided Colour

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 250
- Artworks: 1
- Sides: Single
- Print Type: Colour
- Stock Type: Uncoated Bond 80GSM

**Regular price: $101.41**

---

## TEST 2: Large Quantity Double Sided B&W

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 5000
- Artworks: 2
- Sides: Double
- Print Type: Black & White
- Stock Type: Uncoated Bond 100GSM

**Regular price: $347.44**

---

## TEST 3: Medium-Large Quantity Double Sided Colour

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 1000
- Artworks: 1
- Sides: Double
- Print Type: Colour
- Stock Type: Uncoated Bond 90GSM

**Regular price: $158.64**

---

## TEST 4: Small Quantity Single Sided B&W

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 50
- Artworks: 1
- Sides: Single
- Print Type: Black & White
- Stock Type: Uncoated Bond 80GSM

**Regular price: $90.16**

---

## Technical Notes (Internal Reference)

### Backend Rewrite Complete - January 26, 2026

**Key Formula Corrections:**
- **Setup Costs:**
  - Imposition: 18 → 15
  - Guillotine: 14 → 12
  - Extra Artworks: 12 → 15 per artwork
- **Slips Per Sheet:** 2 → 6 (uses F4.price for DL size)
- **Stock Prices:** Hardcoded 60 → Field-based (80GSM: 26.34, 90GSM: 29.51, 100GSM: 32.68)
- **Print Costs:**
  - Colour: 0.045 → 0.044 per slip
  - B&W: 0.02 ✓ (unchanged)
- **Cut Cost:** 10 → 11
- **Profit Margins:** 12 tiers → 11 tiers (exact TXT match)

### Validation Status:
- **Total Tests:** 4 (all validated)
- **Accuracy:** 100% perfect match
- **Date Validated:** January 26, 2026
- **Status:** Backend rewrite complete ✅

### Business Rules:
- **Size:** DL format (210mm × 99mm) - fixed
- **Sides:** Single or Double sided printing
- **Print Types:** Colour or Black & White
- **Stock Options:** 80GSM, 90GSM, or 100GSM Uncoated Bond
- **Artwork Pricing:** First artwork included, $15 per additional
- **Imposition:** 6 slips per sheet (F4.price sheet size)
- **GST:** 10% applied to final price
