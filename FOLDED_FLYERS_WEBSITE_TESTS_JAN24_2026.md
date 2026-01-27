# Folded Flyers - Website Validation Tests
**Date:** January 24, 2026  
**Calculator:** FoldedFlyers_Shopify_Calculator.py  
**Website:** https://inhouseprint.com.au/product/folded-flyers/

---

## Test Configuration

### Backend Test Command
```powershell
python UI\modules_external\quote-calculator\backend\shopify_calculators\FoldedFlyers_Shopify_Calculator.py
```

---

## TEST 1: Standard A4 Bi-Fold Brochure

**Purpose:** Verify standard A4 single fold pricing

**Configuration:**
- **Quantity:** 1000
- **Finish Size:** A4 - 210mm x 297mm
- **Paper Stock:** Satin 150GSM
- **Print Type:** Colour
- **Print Sides:** Double side print
- **Fold Type:** Single Fold
- **Celloglaze:** None
- **Artworks:** 1

**Backend Calculation:**
```
Setup: $49.00 ($15 imposition + $12 guillotine + $22 folder)
Stock: $34.02 (525 sheets / 1000 × $64.8)
Click: $44.10 (525 sheets × 2 sides × $0.042)
Cutting: $11.55 (525 / 500 × $11)
Folding: $23.00 (1000 × 1 fold / 1000 × $23)
Celloglaze: $0.00
BizCost: $161.67
Profit (85%): $137.42
Subtotal: $299.09
GST (10%): $29.91
TOTAL: $329.00 inc GST
Unit Price: $0.329
```

**Website Steps:**
1. Navigate to: https://inhouseprint.com.au/product/folded-flyers/
2. Select: Quantity = 1000
3. Select: Size = A4 - 210mm x 297mm
4. Select: Stock = Satin 150GSM
5. Select: Double sided = Yes
6. Select: Print type = Colour
7. Select: Folding = Single Fold
8. Select: Celloglaze = None
9. Set: Artworks = 1
10. Note website total price

**Expected Result:** Website price should be **~$329.00** (within $0.50)

**Actual Website Price:** _____________

**Difference:** _____________

**Status:** ⬜ PASS ⬜ FAIL

---

## TEST 2: Premium A5 Tri-Fold with Lamination

**Purpose:** Verify A5 double fold with celloglaze lamination

**Configuration:**
- **Quantity:** 500
- **Finish Size:** A5 - 148mm x 210mm
- **Paper Stock:** Satin 300GSM
- **Print Type:** Colour
- **Print Sides:** Double side print
- **Fold Type:** Double Fold (Tri-fold)
- **Celloglaze:** 2 Side Gloss
- **Artworks:** 1

**Backend Calculation:**
```
Setup: $65.00 ($15 + $12 + $22 + $16 celloglaze)
Stock: $16.54 (131.25 sheets / 1000 × $126)
Click: $11.02 (131.25 sheets × 2 sides × $0.042)
Cutting: $2.89 (131.25 / 500 × $11)
Folding: $23.00 (500 × 2 folds / 1000 × $23)
Celloglaze: $24.94 (131.25 sheets × $0.19 per sheet)
BizCost: $143.39
Profit (110%): $157.73
Subtotal: $301.11
GST (10%): $30.11
TOTAL: $331.23 inc GST
Unit Price: $0.663
```

**Website Steps:**
1. Navigate to: https://inhouseprint.com.au/product/folded-flyers/
2. Select: Quantity = 500
3. Select: Size = A5 - 148mm x 210mm
4. Select: Stock = Satin 300GSM
5. Select: Double sided = Yes
6. Select: Print type = Colour
7. Select: Folding = Double Fold
8. Select: Celloglaze = 2 Side Gloss
9. Set: Artworks = 1
10. Note website total price

**Expected Result:** Website price should be **~$331.23** (within $0.50)

**Actual Website Price:** _____________

**Difference:** _____________

**Status:** ⬜ PASS ⬜ FAIL

---

## TEST 3: Large Format A3 Single Fold Menu

**Purpose:** Verify A3 size with premium stock and matt lamination

**Configuration:**
- **Quantity:** 250
- **Finish Size:** A3 - 297mm x 420mm
- **Paper Stock:** Satin 250GSM
- **Print Type:** Colour
- **Print Sides:** Double side print
- **Fold Type:** Single Fold
- **Celloglaze:** 2 Side Matt
- **Artworks:** 1

**Backend Calculation:**
```
Setup: $65.00 ($15 + $12 + $22 + $16 celloglaze)
Stock: $30.32 (262.5 sheets / 1000 × $115.5)
Click: $22.05 (262.5 sheets × 2 sides × $0.042)
Cutting: $5.78 (262.5 / 500 × $11)
Folding: $5.75 (250 × 1 fold / 1000 × $23)
Celloglaze: $99.75 (262.5 sheets × $0.38 per sheet)
BizCost: $228.64
Profit (80%): $182.92
Subtotal: $411.56
GST (10%): $41.16
TOTAL: $452.71 inc GST
Unit Price: $1.811
```

**Website Steps:**
1. Navigate to: https://inhouseprint.com.au/product/folded-flyers/
2. Select: Quantity = 250
3. Select: Size = A3 - 297mm x 420mm
4. Select: Stock = Satin 250GSM
5. Select: Double sided = Yes
6. Select: Print type = Colour
7. Select: Folding = Single Fold
8. Select: Celloglaze = 2 Side Matt
9. Set: Artworks = 1
10. Note website total price

**Expected Result:** Website price should be **~$452.71** (within $0.50)

**Actual Website Price:** _____________

**Difference:** _____________

**Status:** ⬜ PASS ⬜ FAIL

---

## TEST 4: High Volume 6-Panel Brochure

**Purpose:** Verify 6pp A4 size with high quantity (tests lower profit margin tier)

**Configuration:**
- **Quantity:** 5000
- **Finish Size:** 6pp A4 - 630mm x 297mm
- **Paper Stock:** Satin 128GSM
- **Print Type:** Colour
- **Print Sides:** Double side print
- **Fold Type:** Double Fold (Z-fold)
- **Celloglaze:** None
- **Artworks:** 1

**Backend Calculation:**
```
Setup: $49.00 ($15 + $12 + $22)
Stock: $415.80 (10500 sheets / 1000 × $39.6)
Click: $882.00 (10500 sheets × 2 sides × $0.042)
Cutting: $231.00 (10500 / 500 × $11)
Folding: $230.00 (5000 × 2 folds / 1000 × $23)
Celloglaze: $0.00
BizCost: $1807.80
Profit (21%): $379.64 (qty >= 4000 triggers low margin tier)
Subtotal: $2187.44
GST (10%): $218.74
TOTAL: $2406.18 inc GST
Unit Price: $0.481
```

**Website Steps:**
1. Navigate to: https://inhouseprint.com.au/product/folded-flyers/
2. Select: Quantity = 5000
3. Select: Size = 6pp A4 - 630mm x 297mm
4. Select: Stock = Satin 128GSM
5. Select: Double sided = Yes
6. Select: Print type = Colour
7. Select: Folding = Double Fold
8. Select: Celloglaze = None
9. Set: Artworks = 1
10. Note website total price

**Expected Result:** Website price should be **~$2406.18** (within $1.00)

**Actual Website Price:** _____________

**Difference:** _____________

**Status:** ⬜ PASS ⬜ FAIL

---

## TEST 5: Economy Single-Sided B&W

**Purpose:** Verify budget option with uncoated stock and B&W printing

**Configuration:**
- **Quantity:** 1000
- **Finish Size:** DL - 99mm x 210mm
- **Paper Stock:** Uncoated Bond 80GSM
- **Print Type:** Black & White
- **Print Sides:** Single side print
- **Fold Type:** Single Fold
- **Celloglaze:** None (not available for Uncoated)
- **Artworks:** 1

**Backend Calculation:**
```
Setup: $49.00 ($15 + $12 + $22)
Stock: $33.18 (1050 sheets / 1000 × $31.6)
Click: $10.50 (1050 sheets × 1 side × $0.01)
Cutting: $23.10 (1050 / 500 × $11)
Folding: $23.00 (1000 × 1 fold / 1000 × $23)
Celloglaze: $0.00
BizCost: $138.78
Profit (110%): $152.66
Subtotal: $291.44
GST (10%): $29.14
TOTAL: $320.58 inc GST
Unit Price: $0.321
```

**Website Steps:**
1. Navigate to: https://inhouseprint.com.au/product/folded-flyers/
2. Select: Quantity = 1000
3. Select: Size = DL - 99mm x 210mm
4. Select: Stock = Uncoated Bond 80GSM
5. Select: Double sided = No
6. Select: Print type = Black & White
7. Select: Folding = Single Fold
8. Verify: Celloglaze options NOT visible (Uncoated stock)
9. Set: Artworks = 1
10. Note website total price

**Expected Result:** Website price should be **~$320.58** (within $0.50)

**Actual Website Price:** _____________

**Difference:** _____________

**Celloglaze Hidden:** ⬜ YES (PASS) ⬜ NO (FAIL)

**Status:** ⬜ PASS ⬜ FAIL

---

## TEST 6: Triple Fold Gate-Fold Brochure

**Purpose:** Verify triple fold calculation

**Configuration:**
- **Quantity:** 2000
- **Finish Size:** A4 - 210mm x 297mm
- **Paper Stock:** Satin 200GSM (if available, else use 250GSM)
- **Print Type:** Colour
- **Print Sides:** Double side print
- **Fold Type:** Triple Fold
- **Celloglaze:** 1 Side Gloss
- **Artworks:** 2 (extra artwork)

**Backend Calculation:**
```
Setup: $80.00 ($15 + $12 + $22 + $16 cello + $15 extra artwork)
Stock: (calculate based on available stock)
Click: (calculate)
Cutting: (calculate)
Folding: $138.00 (2000 × 3 folds / 1000 × $23)
Celloglaze: (calculate at $0.19/sheet)
BizCost: (calculate)
Profit: (calculate based on margin tier)
Subtotal: (calculate)
GST (10%): (calculate)
TOTAL: (calculate) inc GST
```

**Website Steps:**
1. Navigate to: https://inhouseprint.com.au/product/folded-flyers/
2. Select: Quantity = 2000
3. Select: Size = A4 - 210mm x 297mm
4. Select: Stock = Satin 250GSM (or available option)
5. Select: Double sided = Yes
6. Select: Print type = Colour
7. Select: Folding = Triple Fold
8. Select: Celloglaze = 1 Side Gloss
9. Set: Artworks = 2
10. Note website total price

**Expected Result:** Calculate backend price and compare (within $1.00)

**Actual Website Price:** _____________

**Backend Calculated:** _____________

**Difference:** _____________

**Status:** ⬜ PASS ⬜ FAIL

---

## Summary Results

| Test | Description | Backend Price | Website Price | Difference | Status |
|------|-------------|---------------|---------------|------------|--------|
| 1 | A4 Single Fold Standard | $329.00 | __________ | __________ | ⬜ |
| 2 | A5 Double Fold + Lamination | $331.23 | __________ | __________ | ⬜ |
| 3 | A3 Single Fold Menu | $452.71 | __________ | __________ | ⬜ |
| 4 | 6pp A4 Bulk Order | $2406.18 | __________ | __________ | ⬜ |
| 5 | DL B&W Economy | $320.58 | __________ | __________ | ⬜ |
| 6 | A4 Triple Fold | __________ | __________ | __________ | ⬜ |

---

## Key Features to Verify

### Profit Margin Tiers
**Size-based margins (Quantity < 4000):**
- A5/DL: 110%
- A4: 85%
- A3: 80%
- 6pp A4: 50%

**Bulk orders (Quantity ≥ 4000):**
- A5/DL: 40%
- A4: 30%
- A3: 30%
- 6pp A4: 21%

### Folding Costs
- Setup: $22 (one-time)
- Per 1000 units per fold: $23
- Single Fold: 1× multiplier
- Double Fold: 2× multiplier
- Triple Fold: 3× multiplier

### Celloglaze Rules
- Only visible for Satin stocks
- Hidden for Uncoated stocks
- 1 Side: $0.19/sheet + $16 setup
- 2 Side: $0.38/sheet + $16 setup

### Stock Waste
5% waste factor (×1.05) applied to all sheet calculations

---

## Acceptance Criteria

✅ **PASS:** Backend price matches website within $0.50 (or $1.00 for large orders)  
✅ **PASS:** Celloglaze hidden for Uncoated stocks  
✅ **PASS:** Profit margins adjust correctly at 4000 qty threshold  
✅ **PASS:** Folding costs calculate correctly for single/double/triple folds  
❌ **FAIL:** Price difference > tolerance → Extract website formula for debugging

---

## Next Steps

### If All Tests Pass:
1. ✅ Mark Folded Flyers calculator as **VALIDATED**
2. Move to next calculator:
   - **Option A:** GOD Flyers (database-driven)
   - **Option B:** Books (Wire Bound, Spiral, Perfect, Saddle Stitch)
   - **Option C:** Business Cards (Economical, Premium)

### If Tests Fail:
1. Extract actual JavaScript formula from website (browser DevTools)
2. Compare line-by-line with backend implementation
3. Identify calculation differences (profit margins, folding costs, stock prices)
4. Fix backend to match website precisely
5. Re-run all tests until 100% alignment

---

**Ready for Website Testing!** 🚀
