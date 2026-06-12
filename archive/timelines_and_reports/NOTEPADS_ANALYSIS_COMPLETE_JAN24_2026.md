# NOTEPADS CALCULATOR ANALYSIS - ALL 3 SIZES
**Analysis Date:** January 24, 2026
**Methodology:** SHOPIFY_CALCULATOR_JSON_FIRST_METHODOLOGY.md

---

## 🚨 CRITICAL FINDINGS

**ALL 3 NOTEPAD BACKENDS ARE COMPLETELY WRONG**

The backends use a generic implementation that does NOT match the TXT formulas at all.
They need to be completely rewritten from scratch using the exact TXT formulas.

---

## DETAILED COMPARISON: TXT vs BACKEND

### **NOTEPADS A5**

| Component | TXT Formula (Lines 1-540) | Backend Implementation | Match? |
|-----------|---------------------------|------------------------|--------|
| **Setup Costs** | | | |
| - guiloSetup | `12` | `18` | ❌ WRONG |
| - imposSetup | `15` | `26` | ❌ WRONG |
| - extraArts | `15` | `15` | ✅ |
| **Formula Structure** | | | |
| - Total Leave Sheets | `((qty * leaves_per_pad) * 1.05) * finish_size_multiplier` | `(qty / items_per_sheet) * 1.07` | ❌ COMPLETELY DIFFERENT |
| - Content Click Cost | `totalLeaveSheets * print_type_price` | `sheets_needed * sides_multiplier * 0.05` | ❌ WRONG LOGIC |
| - Stock Cost | `totalLeaveSheets * stock_price` | `(sheets_needed / 1000) * 95` | ❌ WRONG LOGIC |
| - Box Board Cost | `0.07 * quantity` | NOT IN BACKEND | ❌ MISSING |
| - Cutting Cost | `totalLeaveSheets / 500 * 11` | `sheets_needed / 500 * 13` | ❌ WRONG CUT COST |
| - Padding Cost | `quantity * padding_rate` (7 tiers) | `glue_cost_per_pad (0.18) * quantity` | ❌ WRONG LOGIC |
| **Padding Rate Tiers** | | | |
| - 1-250 | `0.2` | Backend has `_get_padding_rate()` | ⚠️ DEFINED BUT NOT USED |
| - 251-500 | `0.2` | but uses glue_cost instead | ❌ WRONG |
| - 501-1000 | `0.15` | | ❌ |
| - 1001-1500 | `0.15` | | ❌ |
| - 1501-2000 | `0.1` | | ❌ |
| - 2001-3000 | `0.1` | | ❌ |
| - 3001+ | `0.1` | | ❌ |
| **Profit Margins** | | | |
| - 13 tiers | ✅ CORRECT TIERS | ✅ CORRECT | ✅ |
| **GST Application** | `(subtotal * (1 + margin)) * 1.1 * 1.1` | `(subtotal * 1.1) * 1.1` | ✅ CORRECT |

**FIELDS USED:**
- TXT: F1 (qty), F2 (artworks), F3 (finish_size), F4 (leaves_per_pad), F5 (print_type), F6 (stock_type)
- Backend: qty, artworks, print_sides, print_type, paper_stock (GENERIC FIELDS - NOT FROM JSON)

---

### **NOTEPADS A6**

| Component | TXT Formula (Lines 538-1100) | Backend Implementation | Match? |
|-----------|------------------------------|------------------------|--------|
| **Setup Costs** | | | |
| - guiloSetup | `12` | `18` | ❌ WRONG |
| - imposSetup | `15` | `26` | ❌ WRONG |
| - extraArts | `15` | `15` | ✅ |
| **Box Board Cost** | `0.03 * quantity` | NOT IN BACKEND | ❌ MISSING |
| **Padding Rate Tiers** | | | |
| - 1-250 | `0.1` | NOT USED | ❌ |
| - 251-500 | `0.1` | NOT USED | ❌ |
| - 501-1000 | `0.05` | NOT USED | ❌ |
| - 1001-1500 | `0.05` | NOT USED | ❌ |
| - 1501-2000 | `0.03` | NOT USED | ❌ |
| - 2001-3000 | `0.03` | NOT USED | ❌ |
| - 3001+ | `0.03` | NOT USED | ❌ |
| **Finish Size** | A6 Portrait (0.25 multiplier) | NOT IN FORMULA | ❌ MISSING |
| **Leaves Per Pad** | 10, 15, 25, 50, 100 | NOT IN FORMULA | ❌ MISSING |

**KEY DIFFERENCES FROM A5:**
- Lower box board cost: $0.03 vs $0.07
- Lower padding rates: 0.1/0.05/0.03 vs 0.2/0.15/0.1
- Smaller finish size multiplier: 0.25 vs 0.5
- More leaves options: 5 options vs 3 options

---

### **NOTEPADS A4**

| Component | TXT Formula (Lines 1098-1650) | Backend Implementation | Match? |
|-----------|-------------------------------|------------------------|--------|
| **Setup Costs** | | | |
| - guiloSetup | `12` | `18` | ❌ WRONG |
| - imposSetup | `15` | `26` | ❌ WRONG |
| - extraArts | `15` | `15` | ✅ |
| **Box Board Cost** | `0.15 * quantity` | NOT IN BACKEND | ❌ MISSING |
| **Padding Rate Tiers** | | | |
| - 1-250 | `0.3` | NOT USED | ❌ |
| - 251-500 | `0.3` | NOT USED | ❌ |
| - 501-1000 | `0.25` | NOT USED | ❌ |
| - 1001-1500 | `0.25` | NOT USED | ❌ |
| - 1501-2000 | `0.20` | NOT USED | ❌ |
| - 2001-3000 | `0.20` | NOT USED | ❌ |
| - 3001+ | `0.20` | NOT USED | ❌ |
| **Finish Size** | A4 Portrait (1.0 multiplier) | NOT IN FORMULA | ❌ MISSING |
| **Field IDs** | F7 (leaves), F8 (size), F10 (print), F11 (stock) | GENERIC FIELDS | ❌ WRONG |

**KEY DIFFERENCES FROM A5/A6:**
- Higher box board cost: $0.15 (premium backing)
- Higher padding rates: 0.3/0.25/0.2 (premium service)
- Larger finish size: A4 Portrait (1.0 multiplier)
- Different field numbering: F7, F8, F10, F11 (not F3-F6)

---

## EXACT TXT FORMULAS

### **NOTEPADS A5 (Lines 6-48)**

```javascript
// Constants
var guiloSetup = 12;
var imposSetup = 15;
var stockWaste = 1.05;
var extraArts = 15;
var cuttingBlk = 500;
var cutCost = 11;
var q = {F1.price};  // quantity
var boxBoardC = 0.07;

// Artwork setup
var _a = {art} * {extraArts};
var _a2 = {_a} <= {extraArts} ? 0 : ({_a} - {extraArts});

// Setup cost
var totalSetupCost = {imposSetup} + {guiloSetup} + {_a2};

// Total leave sheets: ((qty * leaves_per_pad) * waste) * finish_size_multiplier
var totalLeaveSheets = (({F1.price} * {F4.price}) * {stockWaste}) * {F3.price};

// Content costs
var contentClickCost = {totalLeaveSheets} * {F5.price};  // print type per sheet
var totalContentCost = ({totalLeaveSheets} * {F6.price}) + {contentClickCost} + ({boxBoardC} * {q});

// Cutting cost
var cuttingCost = {totalLeaveSheets} / {cuttingBlk} * {cutCost};

// Padding cost (7 tiers)
var paddingRate = ({q} >= 1 && {q} <= 250) ? .2 : (
    ({q} >= 251 && {q} <= 500) ? 0.2 : (
    ({q} >= 501 && {q} <= 1000) ? 0.15 : (
    ({q} >= 1001 && {q} <= 1500) ? 0.15 : (
    ({q} >= 1501 && {q} <= 2000) ? 0.10 : (
    ({q} >= 2001 && {q} <= 3000) ? 0.10 : 0.10)))));
var paddingCost = {q} * {paddingRate};

// Subtotal
var subTotal = {totalSetupCost} + {totalContentCost} + {cuttingCost} + {paddingCost};

// Profit margin (13 tiers)
var profitMargin = ({subTotal} >= 1 && {subTotal} <= 500) ? 0.8 : (
    ({subTotal} >= 501 && {subTotal} <= 1000) ? 0.8 : (
    ({subTotal} >= 1001 && {subTotal} <= 1500) ? 0.8 : (
    ({subTotal} >= 1501 && {subTotal} <= 2000) ? 0.75 : (
    ({subTotal} >= 2001 && {subTotal} <= 2500) ? 0.72 : (
    ({subTotal} >= 2501 && {subTotal} <= 3000) ? 0.72 : (
    ({subTotal} >= 3001 && {subTotal} <= 4000) ? 0.65 : (
    ({subTotal} >= 4001 && {subTotal} <= 5000) ? 0.55 : (
    ({subTotal} >= 5001 && {subTotal} <= 7500) ? 0.52 : (
    ({subTotal} >= 7501 && {subTotal} <= 10000) ? 0.47 : (
    ({subTotal} >= 10001 && {subTotal} <= 15000) ? 0.42 : (
    ({subTotal} >= 15001 && {subTotal} <= 20000) ? 0.41 : 0)))))))))));

// Final calculation with double GST
var total2 = ({subTotal} + ({subTotal} * {profitMargin})) * 1.1;
{total2}*1.1  // Second 1.1 multiplier (DOUBLE GST)
```

---

### **NOTEPADS A6 (Lines 540-584)**

**Same structure as A5 but with these differences:**

```javascript
var boxBoardC = 0.03;  // Lower cost for smaller size

// Different padding rates (lower)
var paddingRate = ({q} >= 1 && {q} <= 250) ? .1 : (
    ({q} >= 251 && {q} <= 500) ? 0.1 : (
    ({q} >= 501 && {q} <= 1000) ? 0.05 : (
    ({q} >= 1001 && {q} <= 1500) ? 0.05 : (
    ({q} >= 1501 && {q} <= 2000) ? 0.03 : (
    ({q} >= 2001 && {q} <= 3000) ? 0.03 : 0.03)))));

// F3 (Finish Size): A6 Portrait = 0.25 multiplier
// F4 (Leaves Per Pad): 10, 15, 25, 50, 100 options
```

---

### **NOTEPADS A4 (Lines 1100-1144)**

**Same structure as A5 but with these differences:**

```javascript
var boxBoardC = 0.15;  // Higher cost for premium backing

// Higher padding rates (premium)
var paddingRate = ({q} >= 1 && {q} <= 250) ? .3 : (
    ({q} >= 251 && {q} <= 500) ? 0.3 : (
    ({q} >= 501 && {q} <= 1000) ? 0.25 : (
    ({q} >= 1001 && {q} <= 1500) ? 0.25 : (
    ({q} >= 1501 && {q} <= 2000) ? 0.20 : (
    ({q} >= 2001 && {q} <= 3000) ? 0.20 : 0.20)))));

// Different field IDs:
// F7 = Leaves Per Pad (instead of F4)
// F8 = Finish Size: A4 Portrait = 1.0 multiplier (instead of F3)
// F10 = Print Type (instead of F5)
// F11 = Stock Type (instead of F6)

// Formula uses F7, F8, F10, F11 instead of F4, F3, F5, F6:
var totalLeaveSheets = (({F1.price} * {F7.price}) * {stockWaste}) * {F8.price};
var contentClickCost = {totalLeaveSheets} * {F10.price};
var totalContentCost = ({totalLeaveSheets} * {F11.price}) + {contentClickCost} + ({boxBoardC} * {q});
```

---

## REQUIRED FIXES

### **ALL 3 BACKENDS NEED:**

1. ✅ **Correct setup costs:**
   - guiloSetup: 12 (not 18)
   - imposSetup: 15 (not 26)

2. ✅ **Implement exact TXT formula structure:**
   - Total leave sheets = ((qty * leaves_per_pad) * 1.05) * finish_size_multiplier
   - Use field prices from JSON config (F3.price, F4.price, F5.price, F6.price)

3. ✅ **Add box board cost:**
   - A5: $0.07 per pad
   - A6: $0.03 per pad
   - A4: $0.15 per pad

4. ✅ **Implement padding rate tiers:**
   - Use quantity-based lookup (NOT fixed glue cost)
   - Different rates for each size

5. ✅ **Use correct field IDs:**
   - A5/A6: F1, F2, F3, F4, F5, F6
   - A4: F1, F2, F7, F8, F10, F11

6. ✅ **Double GST:**
   - Already correct in backends

---

## BACKEND STATUS

| Calculator | Lines | Status | Required Action |
|-----------|-------|--------|-----------------|
| NotepadsA5_Shopify_Calculator.py | 217 | ❌ WRONG FORMULA | REWRITE FROM SCRATCH |
| NotepadsA6_Shopify_Calculator.py | 217 | ❌ WRONG FORMULA | REWRITE FROM SCRATCH |
| NotepadsA4_Shopify_Calculator.py | 251 | ❌ WRONG FORMULA | REWRITE FROM SCRATCH |

**All 3 backends are using a generic "items per sheet" logic that does NOT match the TXT formulas.**

---

## NEXT STEPS

1. **Rewrite NotepadsA5_Shopify_Calculator.py** - Use exact TXT formula lines 6-48
2. **Rewrite NotepadsA6_Shopify_Calculator.py** - Use A5 formula with A6 adjustments
3. **Rewrite NotepadsA4_Shopify_Calculator.py** - Use A5 formula with A4 adjustments (field IDs F7, F8, F10, F11)
4. **Create test cases** - 4+ per calculator with website validation
5. **Validate all 3** - Get website quotes and compare

---

**PRIORITY: HIGH - These are production calculators with completely wrong logic**
