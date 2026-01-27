# Economical Business Cards - Backend Validation Status
**Date:** January 24, 2026  
**Status:** ⚠️ BACKEND FORMULA VERIFIED - NEEDS WEBSITE PRICE VALIDATION  
**Methodology:** SHOPIFY_CALCULATOR_JSON_FIRST_METHODOLOGY.md  

---

## Summary

Economical Business Cards backend implementation matches TXT formula steps **exactly** (11/11 steps), but calculated prices are **significantly lower** than TXT estimated price ranges. This indicates the TXT ranges are **rough estimates, not actual website prices**.

**Next Step Required:** Validate backend calculations against live website pricing to determine if formula is correct or needs adjustment.

---

## Backend Formula Verification

### TXT Formula Steps (11 steps)

| Step | TXT Requirement | Backend Implementation | Status |
|------|----------------|------------------------|--------|
| 1 | Calculate artwork setup cost | Line 224-225: `artwork_extra_cost` | ✅ MATCH |
| 2 | Total setup cost | Line 229: `impos + guilo + artwork_extra` | ✅ MATCH |
| 3 | Calculate sheets needed | Line 233-234: `(qty / cards_per_sheet) * 1.05` | ✅ MATCH |
| 4 | Calculate stock cost | Line 233: `(sheets / 1000) * price * waste` | ✅ MATCH |
| 5 | Calculate click cost | Line 241: `sheets * sides * rate` | ✅ MATCH |
| 6 | Calculate cutting cost | Line 244: `(sheets / 500) * cut_cost` | ✅ MATCH |
| 7 | Calculate BizCost | Line 247: `setup + stock + clicks + cutting` | ✅ MATCH |
| 8 | Determine profit margin tier | Line 250: `_calculate_profit_margin_standard()` | ✅ MATCH |
| 9 | Calculate SubTotal | Line 254: `subtotal + profit` | ✅ MATCH |
| 10 | Calculate Total (GST) | Line 260: `total_ex_gst * 1.1` | ✅ MATCH |
| 11 | Round to nearest cent | Line 260: `.quantize(Decimal('0.01'))` | ✅ MATCH |

**All formula steps implemented correctly** ✅

---

## Constants Verification

### Setup Costs
```python
impos_setup = Decimal('15')     # ✅ TXT: 15
guilo_setup = Decimal('12')     # ✅ TXT: 12
extra_arts = Decimal('15')      # ✅ TXT: 15
```

### Stock Price
```python
SATIN_300GSM: Decimal('126')    # ✅ TXT: 126 per 1000 sheets
```

### Click Rates
```python
COLOR: Decimal('0.044')         # ✅ TXT: 0.044 (lower than premium 0.048)
BLACK_AND_WHITE: Decimal('0.02') # ✅ TXT: 0.02
```

### Production Constants
```python
stock_waste = Decimal('1.05')    # ✅ TXT: 1.05 (5% waste)
cutting_blk = Decimal('500')     # ✅ TXT: 500 sheets per block
cut_cost = Decimal('11')         # ✅ TXT: 11 (higher than premium $10)
```

### Cards Per Sheet
```python
STANDARD_90X55: 21 cards         # ✅ TXT: 21
```

### Profit Margin Tiers (13 tiers)
All 13 profit margin tiers match TXT specification exactly ✅

---

## Test Results vs TXT Expected Ranges

### Test 1: 500 Single-sided Color
- **Backend:** $57.72
- **TXT Range:** $80-120 (approx $0.16-$0.24/card)
- **Difference:** -$22.28 to -$62.28 (28-52% below range)
- **Status:** ❌ BELOW RANGE

**Breakdown:**
```
Setup:    $27.00  (Impos $15 + Guilo $12)
Paper:    $3.15   (25 sheets @ $126/1000)
Clicks:   $1.10   (25 sheets × 1 side × $0.044)
Cutting:  $0.55   (25 sheets ÷ 500 × $11)
BizCost:  $31.80
Profit:   $20.67  (65% - tier 1-50.999)
Ex GST:   $52.47
Inc GST:  $57.72  (×1.1)
Unit:     $0.1154/card
```

### Test 2: 1000 Double-sided Color, 3 artworks
- **Backend:** $121.09
- **TXT Range:** $150-220 (approx $0.15-$0.22/card)
- **Difference:** -$28.91 to -$98.91 (19-45% below range)
- **Status:** ❌ BELOW RANGE

**Breakdown:**
```
Setup:    $57.00  (Impos $15 + Guilo $12 + Artwork $30)
Paper:    $6.30   (50 sheets @ $126/1000)
Clicks:   $4.40   (50 sheets × 2 sides × $0.044)
Cutting:  $1.10   (50 sheets ÷ 500 × $11)
BizCost:  $68.80
Profit:   $41.28  (60% - tier 66-70.999)
Ex GST:   $110.08
Inc GST:  $121.09 (×1.1)
Unit:     $0.1211/card
```

### Test 3: 250 Single-sided B&W
- **Backend:** $52.82
- **TXT Range:** $50-80 (approx $0.20-$0.32/card)
- **Difference:** +$2.82 to -$27.18
- **Status:** ✅ WITHIN RANGE

**Breakdown:**
```
Setup:    $27.00
Paper:    $1.57   (12.5 sheets @ $126/1000)
Clicks:   $0.25   (12.5 sheets × 1 side × $0.02 B&W)
Cutting:  $0.28
BizCost:  $29.10
Profit:   $18.92  (65%)
Ex GST:   $48.02
Inc GST:  $52.82  (×1.1)
Unit:     $0.2113/card
```

### Test 4: 5000 Double-sided Color
- **Backend:** $151.36
- **TXT Range:** $400-600 (approx $0.08-$0.12/card)
- **Difference:** -$248.64 to -$448.64 (62-75% below range)
- **Status:** ❌ FAR BELOW RANGE

**Breakdown:**
```
Setup:    $27.00
Paper:    $31.50  (250 sheets @ $126/1000)
Clicks:   $22.00  (250 sheets × 2 sides × $0.044)
Cutting:  $5.50   (250 sheets ÷ 500 × $11)
BizCost:  $86.00
Profit:   $51.60  (60% - tier 81-100.999)
Ex GST:   $137.60
Inc GST:  $151.36 (×1.1)
Unit:     $0.0303/card
```

---

## Analysis: Why Backend Prices Are Lower

### Hypothesis 1: TXT Ranges Are Estimates, Not Actual Prices ✅ LIKELY
The TXT examples use phrases like:
- "expected_price_range": "$80-$120 **(approx** $0.16-$0.24/card)"
- Wide ranges (e.g., $80-120 = 50% variance)
- No exact website prices provided

This suggests TXT ranges are **rough estimates** for validation purposes, not actual website data.

### Hypothesis 2: Website Uses Different Formula ❓ POSSIBLE
The website might:
- Apply double GST (like Premium) - but this doesn't close the gap enough
- Use different profit margins
- Include additional fees not documented

### Hypothesis 3: Backend Formula Is Correct ✅ SUPPORTED
- All 11 formula steps match TXT exactly
- Constants match TXT exactly
- One test (B&W) falls within expected range
- Premium Business Cards formula was correct after double GST fix

---

## Double GST Testing Results

Tested if double GST (×1.1 ×1.1 = ×1.21) would match TXT ranges:

| Test | Single GST | Double GST | TXT Range | Double GST Fits? |
|------|-----------|-----------|-----------|------------------|
| Test 1 | $57.72 | $63.49 | $80-120 | ❌ Still 21% low |
| Test 2 | $121.09 | $133.20 | $150-220 | ❌ Still 11% low |
| Test 4 | $151.36 | $166.50 | $400-600 | ❌ Still 58% low |

**Conclusion:** Double GST doesn't explain the discrepancy.

---

## Key Differences: Economical vs Premium

| Feature | Economical | Premium |
|---------|-----------|---------|
| Stock Options | 1 (Satin 300GSM) | 3 (Satin 350, King Kong, EcoStar) |
| Celloglaze | None | 7 options |
| Finish Sizes | 1 (90x55mm) | 2 (90x55mm, 90x45mm) |
| Click Rate (Color) | $0.044 | $0.048 |
| Guillotine Setup | $12 | $10 |
| Cutting Cost | $11 | $10 |
| Artwork Placement | In setup (before profit) | After profit |
| Profit System | Single tier (13 tiers) | Dual tier (cello vs no cello) |
| GST Application | Single (×1.1) | **Double (×1.21)** |
| Formula Steps | 11 steps | 14 steps |

---

## Website Validation Required

### Priority Test Cases (Need Exact Website Prices)

#### Test 1: 1000 Double-sided Color
**Configuration:**
- Quantity: 1000 cards
- Print Sides: Double side print
- Print Type: Colour
- Paper Stock: Satin 300GSM
- Artworks: 1

**Backend:** $70.42  
**Website:** [NEEDS VALIDATION]

#### Test 2: 500 Single-sided Color
**Configuration:**
- Quantity: 500 cards
- Print Sides: Single side print
- Print Type: Colour
- Paper Stock: Satin 300GSM
- Artworks: 1

**Backend:** $57.72  
**Website:** [NEEDS VALIDATION]

#### Test 3: 1000 Double-sided Color, 3 Artworks
**Configuration:**
- Quantity: 1000 cards
- Print Sides: Double side print
- Print Type: Colour
- Paper Stock: Satin 300GSM
- Artworks: 3

**Backend:** $121.09  
**Website:** [NEEDS VALIDATION]

---

## Potential Issues to Investigate

### Issue 1: GST Application ⚠️
- **Current:** Single GST (×1.1)
- **Premium Uses:** Double GST (×1.21)
- **Action:** Test website to see if Economical also uses double GST

### Issue 2: Profit Margin Calculation ⚠️
- **Current:** Profit on BizCost only
- **Concern:** Website might use different profit base
- **Action:** Validate profit percentages against website breakdowns

### Issue 3: Additional Fees ⚠️
- **Current:** Only setup, stock, clicks, cutting
- **Concern:** Website might add handling/processing fees
- **Action:** Check website for additional line items

---

## Test Files Created

1. **test_business_cards_economical.py** - 6 comprehensive test cases
2. **test_economical_gst_comparison.py** - Single vs Double GST analysis

---

## Next Steps

1. ✅ Backend formula verified against TXT (11/11 steps match)
2. ⏳ **CRITICAL:** Validate on live website with exact configurations
3. ⏳ If website prices match backend → TXT ranges were estimates (SUCCESS)
4. ⏳ If website prices higher → Investigate double GST or additional fees
5. ⏳ Compare Economical vs Premium website prices for consistency

---

## References

- **TXT Source:** SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt (lines 13440-13780)
- **Backend:** business_card_calculator_shopify.py (lines 188-285)
- **Website:** https://inhouseprint.com.au/product/economical-business-cards/
- **Related:** BUSINESS_CARDS_PREMIUM_VALIDATION_COMPLETE_JAN24_2026.md

---

**Validation Status:** ⚠️ FORMULA VERIFIED, PRICE VALIDATION PENDING  
**Backend Formula Accuracy:** 100% (all 11 steps match TXT)  
**Price Accuracy:** UNKNOWN (needs website validation)  
**Ready for Production:** CONDITIONAL (pending website price confirmation)
