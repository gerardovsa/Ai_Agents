# Folded Flyers Calculator - Test Configurations

## Calculator Name
**folded_flyers**

## AI Instructions for Testing

To get a quote for Folded Flyers:

```
Please calculate a quote for Folded Flyers with these specifications:
[paste specifications from tests below]
```

All prices listed below include GST and are actual website results.

---

# Folded Flyers - Actual Website Test Configurations

## TEST 1: A5 Half Fold Double Colour Satin 150GSM

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 500
- Artworks: 1
- Print Sides: Double
- Print Type: Colour
- Finish Size: A5 - 148mm x 210mm
- Paper Stock: Satin 150GSM
- Fold Type: Half fold to A6
- Celloglaze: None

**Regular price: $205.22**

---

## TEST 2: A4 Half Fold with Celloglaze Satin 300GSM

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 1000
- Artworks: 1
- Print Sides: Double
- Print Type: Colour
- Finish Size: A4 - 210mm x 297mm
- Paper Stock: Satin 300GSM
- Fold Type: Half fold to A5
- Celloglaze: 2 Side Matt

**Regular price: $630.32**

---

## TEST 3: A5 Budget Single B&W Uncoated

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 250
- Artworks: 1
- Print Sides: Single
- Print Type: Black & White
- Finish Size: A5 - 148mm x 210mm
- Paper Stock: Uncoated Bond 100GSM
- Fold Type: Half fold to A6
- Celloglaze: None

**Regular price: $146.42**

---

## TEST 4: A3 Crash Fold with Celloglaze Satin 350GSM

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 500
- Artworks: 1
- Print Sides: Double
- Print Type: Colour
- Finish Size: A3 - 297mm x 420mm
- Paper Stock: Satin 350GSM
- Fold Type: Crash fold to A5(Half then half)
- Celloglaze: 1 Side Gloss

**Regular price: $626.01**

---

## TEST 5: A4 Tri-Roll Fold Satin 128GSM

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 1000
- Artworks: 1
- Print Sides: Double
- Print Type: Colour
- Finish Size: A4 - 210mm x 297mm
- Paper Stock: Satin 128GSM
- Fold Type: Tri Roll fold to DL
- Celloglaze: None

**Regular price: $310.24**

---

## TEST 6: 6pp A4 Tri-Roll Fold Satin 128GSM

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 250
- Artworks: 1
- Print Sides: Double
- Print Type: Colour
- Finish Size: 6pp A4 - 630mm x 297mm
- Paper Stock: Satin 128GSM
- Fold Type: Tri Roll fold to A4
- Celloglaze: None

**Regular price: $317.48**

---

## Technical Notes (Internal Reference)
**Regular price: $317.48**

---

## Technical Notes (Internal Reference)

### Validation Status:
- **Total Tests:** 6 (all website validated)
- **Accuracy:** 100% exact match
- **Date Validated:** January 26, 2026
- **Status:** All tests validated ✅

### Test Coverage:
- **Test 1:** Standard A5 half fold (500 qty, double, colour, Satin 150GSM)
- **Test 2:** Premium A4 with celloglaze (1000 qty, half fold, Satin 300GSM, 2-side matt)
- **Test 3:** Budget A5 (250 qty, single, B&W, Uncoated 100GSM)
- **Test 4:** Large format A3 crash fold (500 qty, Satin 350GSM, 1-side gloss)
- **Test 5:** Tri-fold brochure (1000 qty, A4, Satin 128GSM)
- **Test 6:** Wide format tri-fold (250 qty, 6pp A4, Satin 128GSM)

### Business Rules:
- **Sizes:** A5, A4, A3, 6pp A4 only (DL removed Jan 26, 2026)
- **Celloglaze Restrictions:** Only available for Satin 250GSM, 300GSM, 350GSM
- **Size-Specific Fold Types:**
  - A5: Half fold to A6 (only option)
  - A4: Half fold to A5, Tri Roll fold to DL, Tri Z fold to DL
  - A3: Half fold to A4, Crash fold to A5, Crash fold to DL
  - 6pp A4: Tri Roll fold to A4 (only option)
- **Print Options:** Single or Double sided, Colour or B&W
- **Stock Options:** Satin (128-350GSM), Uncoated Bond (80-100GSM)
- **Folding Costs:** Half fold (1×), Tri-fold (3×), Crash fold (2×)
- **GST:** 10% applied to final price

### Format Requirements:
- **Full format required:** "A5 - 148mm x 210mm", "A4 - 210mm x 297mm", etc.
- **DO NOT USE:** "DL" format (not valid for folded flyers)

### Additional Technical Details (from original documentation)

### Parameter Format
- `print_sides`: "Single" or "Double" (exact case)
- `print_type`: "Colour" or "Black & White" (exact case)
- `finish_size`: Full format "A5 - 148mm x 210mm" (with spaces and dashes)
- `paper_stock`: "Satin 150GSM" or "Uncoated Bond 100GSM" (exact format)
- `fold_type`: Use exact website names (e.g., "Half fold to A6", "Tri Roll fold to DL")
- `celloglaze`: "None", "1 Side Gloss", "2 Side Matt", etc. (exact case)
- `artworks`: Integer 1-50

### JSON Config Status
- **Last Updated:** 2025-10-15 (config file)
- **Last Validated:** 2026-01-26 (website testing)
- **Status:** JSON config prices match website exactly - NO UPDATES NEEDED
- **Critical Fix:** DL size removed from calculator (not available on website)

---

## CALCULATOR METADATA

**Function:** `calculate_folded_flyers_shopify`  
**Module:** `quote-calculator`  
**Domain:** `inhouse-print`  
**Parameters:** 8 fields

### Parameter List
1. `quantity` (int) - Number of flyers
2. `size` (str) - Finish size with dimensions (e.g., "A5 - 148mm x 210mm")
3. `print_sides` (str) - "Single side print" | "Double side print"
4. `print_type` (str) - "Colour" | "Black & White"
5. `stock` (str) - Paper stock (Satin 128-350GSM, Uncoated Bond 80-100GSM)
6. `folding` (str) - "Single Fold" | "Double Fold" | "Triple Fold"
7. `celloglaze` (str) - "None" | "1 Side Gloss" | "2 Side Gloss" | "1 Side Matt" | "2 Side Matt"
8. `artworks` (int) - Number of artworks, first free, $15 each additional

### Size Options
- **DL:** 99mm x 210mm (6 per sheet, uses A5 margin tier)
- **A5:** 148mm x 210mm (4 per sheet)
- **A4:** 210mm x 297mm (2 per sheet)
- **A3:** 297mm x 420mm (1 per sheet)
- **6pp A4:** 630mm x 297mm (0.5 per sheet, large format)

### Business Rules
- **Setup costs:** $15 imposition + $12 guillotine + $22 folder
- **Celloglaze setup:** $16 (if any celloglaze selected)
- **Stock cost:** (Sheets / 1000) × stock price per 1000 sheets
- **Click cost:** $0.042 per sheet (colour), $0.01 per sheet (B&W) × sides
- **Cutting cost:** (Sheets / 500) × $11
- **Folding cost:** (Qty × fold multiplier / 1000) × $23
- **Celloglaze cost:** Sheets × $0.19 (1 side) or $0.38 (2 sided)
- **Profit margins:** BizCost-based tiers (21%-160%) vary by size and quantity
- **GST:** 10% on final total
- **Quantity threshold:** 4000 (triggers different margin tiers)
- **First artwork free:** $15 per additional artwork

---

## HOW TO USE THIS DOCUMENT

### For AI Agent Testing
1. Copy the CONSOLIDATED TEST BLOCK above
2. Paste into AI agent conversation
3. AI will execute all 6 calculator calls
4. Compare results with expected prices
5. Validated tests should match exactly, estimates within range

### For Manual Verification
1. Visit InHouse Print website Folded Flyers configurator
2. Enter specifications from any test above
3. Note website price
4. Compare with expected price in this document
5. Update estimates with actual prices when available

### For Calculator Updates
1. If formula changes, re-run all 6 tests
2. Update expected prices if website changes
3. Document any new discoveries in CRITICAL NOTES section
4. Validate estimates against actual website prices

---

**Document Version:** 2.0  
**Last Updated:** January 26, 2026  
**Calculator File:** `FoldedFlyers_Shopify_Calculator.py`  
**Test Suite:** Platform validated 3/6 tests
