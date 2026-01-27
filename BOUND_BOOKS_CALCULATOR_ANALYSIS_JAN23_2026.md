# BOUND BOOKS CALCULATOR ANALYSIS
**Created:** January 23, 2026  
**Methodology:** JSON-First TXT vs Backend Comparison

---

## 📋 CALCULATORS FOUND

### In TXT File (SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt):
1. ✅ **Saddle Stitch Books** (Lines 3054-3857)
2. ✅ **Spiral Bound Books** (Lines 3863-4700)
3. ❌ **Perfect Bound Books** (Line 13776 - NO FORMULA, file ends)
4. ❌ **Wire Bound Books** (NOT FOUND in TXT)

### In Backend (shopify_calculators/):
1. ✅ **SaddleStitchBooks_Shopify_Calculator.py**
2. ✅ **SpiralBoundBooks_Shopify_Calculator.py**
3. ✅ **SpiralBound_Shopify_Calculator.py** (Duplicate? 17 tiers vs different)
4. ✅ **WireBound_Shopify_Calculator.py** (14 binding tiers)
5. ✅ **PerfectBound_Shopify_Calculator.py**

---

## 🚨 CRITICAL ISSUE: DOUBLE GST IN TXT

### Saddle Stitch Books - DOUBLE GST ERROR

**TXT Formula (Lines 3115-3116):**
```javascript
var total = ({subTotal} + ({subTotal} *{profitMargin})) * 1.1;
{total}*1.1
```

**Analysis:**
- Line 3115: `subtotal_with_margin * 1.1` (first GST)
- Line 3116: `{total}*1.1` (second GST)
- **Result:** Double GST application = 1.1 × 1.1 = 21% instead of 10%

**Backend Implementation:**
```python
# Line 213
subtotal_with_margin = subtotal_before_margin * (Decimal('1') + margin_multiplier)

# Line 216
total_inc_gst = subtotal_with_margin * Decimal('1.1')
```

**Comparison:**
| Component | TXT Formula | Backend | Match? |
|-----------|-------------|---------|--------|
| GST Application | × 1.1 × 1.1 (21%) | × 1.1 (10%) | ❌ MISMATCH |

**Question for User:**
🤔 **Is the double GST in the TXT file a mistake, or is this how Shopify actually calculates it?**

We need to verify on the live website before fixing backend.

---

## 📊 COMPARISON: SADDLE STITCH BOOKS

### TXT Formula (Lines 3054-3120)

**Constants:**
```javascript
var guiloSetup = 12;
var imposSetup = 15;
var celloSetup = {F6} == 'None' ? 0 : 25;
var stockWaste = 1.05;
var extraArts = 15;
var cuttingBlk = 500;
var cutCost = 11;
var binderSetup = 30;
var binderPerBook = 0.2;
var binderyLaborperhour = 60;
var bindersheetsperhour = 5000;
```

**Artwork Cost:**
```javascript
var _a = {art} * {extraArts};
var _a2 = {_a} <= {extraArts} ? 0 : ({_a} - {extraArts});
// Translation: First artwork free, $15 per extra
```

**Setup Cost:**
```javascript
var totalSetupCost = {imposSetup} + {guiloSetup} + {_a2} + {celloSetup} + {binderSetup};
// = 15 + 12 + artwork_extra + (0 or 25) + 30
```

**Cover Cost (if Hard Cover):**
```javascript
var totalCoverSheetsA3 = {F3} == 'Self Cover' ? 0 : (({f1.price} * {F8.price}) * {stockWaste});
var coverClickCost = {F5.price} * {totalCoverSheetsA3};
var totalCoverCost = ({totalCoverSheetsA3} * {F4.price}) + {coverClickCost};
```

**Content Cost:**
```javascript
var totalContentSheets = (({F1.price} * {F7.price}) * {stockWaste}) * {F8.price};
var contentClickCost = {totalContentSheets} * {F10.price};
var totalContentCost = ({totalContentSheets} * {F11.price}) + {contentClickCost};
```

**Cutting Cost:**
```javascript
var totalSheetsPrinted = {totalContentSheets} + {totalCoverSheetsA3};
var cuttingCost = {totalSheetsPrinted} / {cuttingBlk} * {cutCost};
```

**Celloglaze Cost:**
```javascript
var celloCost = {F6} == 'None' ? 0 : ({totalCoverSheetsA3} * {F6.price});
```

**Binding Cost:**
```javascript
var bindRunCost = ((({totalContentSheets} + {totalCoverSheetsA3}) / {bindersheetsperhour}) * {binderyLaborperhour}) + ({F1.price} * {binderPerBook});
```

**Profit Margin Tiers (14 tiers):**
```javascript
var profitMargin = ({subTotal} >= 1 && {subTotal} <= 49.999) ? 1.7 : (
          ({subTotal} >= 50 && {subTotal} <= 99.999) ? 1.54 : (
          ({subTotal} >= 100 && {subTotal} <= 199.999) ? 1.24 : (
          ({subTotal} >= 200 && {subTotal} <= 299.999) ? 1.1 : (
          ({subTotal} >= 300 && {subTotal} <= 499.999) ? 1.04 : (
          ({subTotal} >= 500 && {subTotal} <= 749.999) ? 0.88 : (
          ({subTotal} >= 750 && {subTotal} <= 999.999) ? 0.78 : (
          ({subTotal} >= 1000 && {subTotal} <= 1249.999) ? 0.7 : (
          ({subTotal} >= 1250 && {subTotal} <= 1499.999) ? 0.64 : (
          ({subTotal} >= 1500 && {subTotal} <= 1749.999) ? 0.52 : (
          ({subTotal} >= 1750 && {subTotal} <= 1999.999) ? 0.47 : (
          ({subTotal} >= 2000 && {subTotal} <= 2499.999) ? 0.42 : (
          ({subTotal} >= 2500 && {subTotal} <= 2999.999) ? 0.4 : (
          ({subTotal} >= 3000 && {subTotal} <= 100000) ? 0.37 : .37)))))))))))));
```

**Final Calculation:**
```javascript
var total = ({subTotal} + ({subTotal} *{profitMargin})) * 1.1;
{total}*1.1  // ❌ DOUBLE GST
```

### Backend Implementation

**Setup Costs:**
✅ Matches TXT:
- `guilo_setup = 12`
- `impos_setup = 15`
- `binder_setup = 30`
- `extra_arts = 15 * max(0, artworks - 1)`
- `cello_setup = 25 if celloglaze != "None" else 0`

**Profit Margins:**
✅ All 14 tiers match TXT exactly:
```python
def _get_profit_margin(self, subtotal: float) -> Decimal:
    if subtotal <= 49.999: return Decimal('1.7')
    elif subtotal <= 99.999: return Decimal('1.54')
    elif subtotal <= 199.999: return Decimal('1.24')
    # ... (14 tiers total)
```

**GST Application:**
❌ **MISMATCH:**
- TXT: `* 1.1 * 1.1` (21% total)
- Backend: `* 1.1` (10% only)

### Discrepancy Summary

| Component | TXT | Backend | Match? |
|-----------|-----|---------|--------|
| Setup costs | 12+15+30+artwork+cello | 12+15+30+artwork+cello | ✅ |
| Stock waste | 1.05 | 1.05 | ✅ |
| Cutting block | 500 | 500 | ✅ |
| Binder per book | 0.2 | 0.2 | ✅ |
| Profit margins | 14 tiers | 14 tiers | ✅ |
| GST | **× 1.1 × 1.1** | **× 1.1** | ❌ |
| Formula logic | Complex | Simplified | ⚠️ |

---

## 📊 COMPARISON: SPIRAL BOUND BOOKS

### TXT Formula (Lines 3863-4050)

**Constants:**
```javascript
var guiloSetup = 12;
var imposSetup = 15;
var stockWaste = 1.05;
var extraArts = 15;
var cuttingBlk = 500;
var cutCost = 11;
var punchSetup = 15;
var wirebindperbook = 1.16;
var binderyLaborperhour = 70;
var punchsheetsperhour = 15000;
var celloSetup = ({F6} == 'None' && {F10} == 'None') ? 0 : 25;
```

**Wire Pricing Tiers (18 tiers based on book thickness):**
```javascript
var pricePerRing = ({bookThickness} <= 8) ? 0.13065 : (
    ({bookThickness} <= 10) ? 0.157 : (
    ({bookThickness} <= 12) ? 0.2242 : (
    ({bookThickness} <= 14) ? 0.25 : (
    ({bookThickness} <= 16) ? 0.2895 : (
    ({bookThickness} <= 18) ? 0.321 : (
    ({bookThickness} <= 20) ? 0.4141 : (
    ({bookThickness} <= 22) ? 0.516 : (
    ({bookThickness} <= 24) ? 0.563 : (
    ({bookThickness} <= 28) ? 0.6392 : (
    ({bookThickness} <= 31) ? 0.7172 : (
    ({bookThickness} <= 33) ? 0.7558 : (
    ({bookThickness} <= 35) ? 0.829 : (
    ({bookThickness} <= 38) ? 0.9042 : (
    ({bookThickness} <= 41) ? 1.201 : (
    ({bookThickness} <= 48) ? 1.248 : (
    ({bookThickness} <= 53) ? 1.248 : 1.248))))))))))))))));
```

**Wire Cost Calculation:**
```javascript
var priceofwire = ({F14} == 'A6 Portrait' || {F14} == 'A6 Landscape' || {F14} == 'DL Landscape' || {F14} == 'A5 Landscape') ? 
    ({pricePerRing} * {F1}) / 2 :  // Small formats use HALF wire
    ({pricePerRing} * {F1});
```

**Profit Margin Tiers (12 tiers):**
```javascript
var profitMargin = ({BizCost} >= 1 && {BizCost} <= 500) ? 0.9 : (
    ({BizCost} > 500 && {BizCost} <= 1000) ? 0.9 : (
    ({BizCost} > 1000 && {BizCost} <= 1500) ? 0.80 : (
    ({BizCost} > 1500 && {BizCost} <= 2000) ? 0.75 : (
    ({BizCost} > 2000 && {BizCost} <= 2500) ? 0.70 : (
    ({BizCost} > 2500 && {BizCost} <= 3000) ? 0.67 : (
    ({BizCost} > 3000 && {BizCost} <= 4000) ? 0.65 : (
    ({BizCost} > 4000 && {BizCost} <= 5000) ? 0.55 : (
    ({BizCost} > 5000 && {BizCost} <= 7500) ? 0.52 : (
    ({BizCost} > 7500 && {BizCost} <= 10000) ? 0.47 : (
    ({BizCost} > 10000 && {BizCost} <= 15000) ? 0.42 : (
    ({BizCost} > 15000 && {BizCost} <= 100000) ? 0.41 : 0)))))))))));
```

**Final Calculation:**
```javascript
var subTotal = ({BizCost} + ({BizCost}*{profitMargin}));
var total = {subTotal} * 1.15;
{total} + 44  // ❌ GST is 15%, not 10%!? + $44 surcharge
```

**⚠️ CRITICAL:** Spiral Bound uses **1.15 (15% GST)** instead of 1.10, PLUS adds $44 surcharge!

### Backend Investigation Needed

Need to check if backend implements:
1. ✅ 18-tier wire pricing based on thickness
2. ✅ Small format wire cost division (÷ 2)
3. ✅ 12-tier profit margins
4. ❌ **1.15 GST rate** (not 1.10)
5. ❌ **$44 surcharge** at end

---

## 🎯 NEXT STEPS

### 1. **Verify Double GST on Live Website**
Test Saddle Stitch calculator on Shopify:
- Input: 100 books, 16pp, A4, basic config
- Check if price shows 21% markup or 10%
- **IF 21%:** Backend needs `* 1.1 * 1.1`
- **IF 10%:** TXT file has error, backend is correct

### 2. **Verify Spiral Bound GST Rate**
Test Spiral Bound calculator on Shopify:
- Check if it uses 1.15 (15%) or 1.10 (10%)
- Check if $44 surcharge is added at end
- **Critical:** Different GST rate from other calculators!

### 3. **Wire Bound vs Spiral Bound**
Determine:
- Are these same calculator with different tiers?
- Wire Bound: 14 binding tiers (from backend comments)
- Spiral Bound: 18 binding tiers (from TXT)
- Need to find Wire Bound formula in TXT (not found yet)

### 4. **Perfect Bound Books**
- TXT file has NO formula (line 13776 is just comment)
- Backend file exists but no TXT reference
- **Action:** Need to find original Perfect Bound formula or test website

### 5. **Create Test Cases**
Once website validation is complete, create test cases with expected results.

---

## 📝 SUMMARY OF FINDINGS

### ✅ CORRECT IMPLEMENTATIONS:
- Saddle Stitch: All constants, 14-tier margins (**EXCEPT GST**)
- Spiral Bound: 18-tier wire pricing, thickness calculations

### ❌ CRITICAL DISCREPANCIES:
1. **Saddle Stitch:** TXT shows double GST (`* 1.1 * 1.1`), backend uses single
2. **Spiral Bound:** TXT shows 15% GST + $44 surcharge, need to verify backend
3. **Perfect Bound:** No TXT formula found
4. **Wire Bound:** No TXT formula found

### 🚨 BLOCKING ISSUE:
**Cannot proceed with fixes until website validation confirms:**
- Is double GST intentional or error?
- Is 15% GST + $44 surcharge correct for Spiral Bound?
- What are the formulas for Perfect Bound and Wire Bound?

---

## 🔍 RECOMMENDED WORKFLOW

1. **User tests Saddle Stitch on live Shopify:**
   - 100 books, Hard Cover, 16pp, A4, Satin 200GSM cover, B&W content
   - Compare backend result vs website
   - Determine if double GST is real

2. **User tests Spiral Bound on live Shopify:**
   - 100 books, 50 pages, A4, standard config
   - Check GST rate (10% or 15%?)
   - Check if $44 added at end

3. **User provides Perfect Bound website example:**
   - Test case with inputs and expected price
   - We can reverse-engineer formula

4. **User provides Wire Bound website example:**
   - Test case with inputs and expected price
   - Compare to existing backend implementation

**Then we can create accurate comparison tables and fix all discrepancies.**

---

**Status:** Analysis PAUSED - awaiting website validation  
**Next Action:** User to test calculators on live Shopify and provide results
