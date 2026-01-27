# ALL 3 NOTEPADS SHOPIFY CALCULATORS REWRITTEN - JANUARY 24, 2026

## Executive Summary

✅ **STATUS: COMPLETE** - All 3 Notepads Shopify calculators rewritten to match exact TXT formulas  
📅 **Completion Date:** January 24, 2026  
🎯 **Objective:** Fix completely wrong backend implementations  
📄 **Source:** SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt  

---

## Calculators Fixed

### 1. ✅ Notepads A5 (Lines 1-540)
**File:** `NotepadsA5_Shopify_Calculator.py`  
**Status:** COMPLETE  
**Changed:** 217 lines completely rewritten  

**Key Constants:**
- guiloSetup: 18 → **12** ✅
- imposSetup: 26 → **15** ✅
- boxBoardC: none → **0.07** ✅
- Padding rates: generic glue_cost → **0.2/0.2/0.15/0.15/0.1/0.1/0.1** ✅
- Finish size multiplier: none → **0.5** (A5 Portrait) ✅

**Formula Change:**
```python
# OLD (WRONG):
sheets_needed = (Decimal(quantity) / items_per_sheet) * stock_waste
binding_cost = glue_cost_per_pad * Decimal(quantity)

# NEW (CORRECT):
total_leave_sheets = ((Decimal(quantity) * leaves_per_pad_value) * stock_waste) * finish_size_multiplier
padding_cost = Decimal(quantity) * self._get_padding_rate(quantity)
total_content_cost = (total_leave_sheets * stock_type_price) + content_click_cost + (box_board_c * Decimal(quantity))
```

---

### 2. ✅ Notepads A6 (Lines 538-1100)
**File:** `NotepadsA6_Shopify_Calculator.py`  
**Status:** COMPLETE  
**Changed:** 230 lines completely rewritten  

**Key Constants:**
- guiloSetup: 14 → **12** ✅
- imposSetup: 22 → **15** ✅
- boxBoardC: none → **0.03** ✅ (LOWER than A5)
- Padding rates: 0.1 → **0.1/0.1/0.05/0.05/0.03/0.03/0.03** ✅ (LOWER than A5)
- Finish size multiplier: none → **0.25** (A6 Portrait) ✅
- Leaves options: none → **10, 15, 25, 50, 100** ✅ (more options than A5)

**Formula Change:**
```python
# OLD (WRONG):
sheets_needed = (Decimal(quantity) / items_per_sheet) * stock_waste  # items_per_sheet=4
binding_cost = glue_cost_per_pad * Decimal(quantity)  # glue_cost_per_pad=0.12

# NEW (CORRECT):
total_leave_sheets = ((Decimal(quantity) * leaves_per_pad_value) * stock_waste) * finish_size_multiplier  # finish_size_multiplier=0.25
padding_cost = Decimal(quantity) * self._get_padding_rate(quantity)  # 0.1/0.05/0.03 tiers
total_content_cost = (total_leave_sheets * stock_type_price) + content_click_cost + (box_board_c * Decimal(quantity))  # boxBoardC=0.03
```

---

### 3. ✅ Notepads A4 (Lines 1098-1650)
**File:** `NotepadsA4_Shopify_Calculator.py`  
**Status:** COMPLETE  
**Changed:** 251 lines completely rewritten  

**CRITICAL DIFFERENCE: Uses different field IDs (F7, F8, F10, F11 instead of F3, F4, F5, F6)**

**Key Constants:**
- guiloSetup: 20 → **12** ✅
- imposSetup: 30 → **15** ✅
- boxBoardC: none → **0.15** ✅ (PREMIUM - highest of all 3 sizes)
- Padding rates: 0.3 → **0.3/0.3/0.25/0.25/0.2/0.2/0.2** ✅ (PREMIUM - highest of all 3)
- Finish size multiplier: none → **1.0** (A4 Portrait - full sheet) ✅
- Leaves options: none → **25, 50, 100, 200** ✅ (larger quantities)

**Field Mapping:**
- F7 (not F4): Leaves Per Pad
- F8 (not F3): Finish Size
- F10 (not F5): Print Type
- F11 (not F6): Stock Type

**Formula Change:**
```python
# OLD (WRONG):
sheets_needed = (Decimal(quantity) / items_per_sheet) * stock_waste  # items_per_sheet=1, stock_waste=1.08
binding_cost = glue_cost_per_pad * Decimal(quantity)  # glue_cost_per_pad=0.20

# NEW (CORRECT):
total_leave_sheets = ((Decimal(quantity) * leaves_per_pad_value) * stock_waste) * finish_size_multiplier  # finish_size_multiplier=1.0, stock_waste=1.05
padding_cost = Decimal(quantity) * self._get_padding_rate(quantity)  # 0.3/0.25/0.2 PREMIUM tiers
total_content_cost = (total_leave_sheets * stock_type_price) + content_click_cost + (box_board_c * Decimal(quantity))  # boxBoardC=0.15 PREMIUM
```

---

## Size Comparison Matrix

| Property | A5 | A6 | A4 |
|----------|----|----|-----|
| **Box Board Cost** | $0.07 | $0.03 (LOWER) | $0.15 (PREMIUM) |
| **Padding Rate Tier 1** | 0.2 | 0.1 (LOWER) | 0.3 (PREMIUM) |
| **Padding Rate Tier 2** | 0.2 | 0.1 (LOWER) | 0.3 (PREMIUM) |
| **Padding Rate Tier 3** | 0.15 | 0.05 (LOWER) | 0.25 (PREMIUM) |
| **Padding Rate Tier 4** | 0.15 | 0.05 (LOWER) | 0.25 (PREMIUM) |
| **Padding Rate Tier 5** | 0.1 | 0.03 (LOWER) | 0.2 (PREMIUM) |
| **Padding Rate Tier 6** | 0.1 | 0.03 (LOWER) | 0.2 (PREMIUM) |
| **Padding Rate Tier 7** | 0.1 | 0.03 (LOWER) | 0.2 (PREMIUM) |
| **Finish Multiplier** | 0.5 | 0.25 (smaller) | 1.0 (full sheet) |
| **Leaves Options** | 25, 50, 100 | 10, 15, 25, 50, 100 | 25, 50, 100, 200 |
| **Field IDs** | F3,F4,F5,F6 | F3,F4,F5,F6 | **F7,F8,F10,F11** |
| **guiloSetup** | 12 | 12 | 12 |
| **imposSetup** | 15 | 15 | 15 |
| **Stock Waste** | 1.05 | 1.05 | 1.05 |

---

## Common Formula (All 3 Sizes)

All 3 calculators now use the same TXT formula structure:

```python
# 1. Artwork setup
_a = Decimal(artworks) * extra_arts  # extra_arts=15
_a2 = Decimal('0') if _a <= extra_arts else (_a - extra_arts)

# 2. Total setup cost
total_setup_cost = impos_setup + guilo_setup + _a2  # impos=15, guilo=12

# 3. Total leave sheets (KEY FORMULA)
total_leave_sheets = ((Decimal(quantity) * leaves_per_pad_value) * stock_waste) * finish_size_multiplier

# 4. Content click cost
content_click_cost = total_leave_sheets * print_type_price

# 5. Total content cost (includes box board)
total_content_cost = (total_leave_sheets * stock_type_price) + content_click_cost + (box_board_c * Decimal(quantity))

# 6. Cutting cost
cutting_cost = (total_leave_sheets / cutting_blk) * cut_cost  # cutting_blk=500, cut_cost=11

# 7. Padding cost (quantity-based tiers)
padding_cost = Decimal(quantity) * self._get_padding_rate(quantity)

# 8. Subtotal
sub_total = total_setup_cost + total_content_cost + cutting_cost + padding_cost

# 9. Profit margin (13 subtotal-based tiers)
profit_margin = self._get_profit_margin(float(sub_total))

# 10-12. Apply margin and double GST
total2 = (sub_total + (sub_total * profit_margin)) * Decimal('1.1')
total_price = total2 * Decimal('1.1')
```

---

## Why Old Backends Were Completely Wrong

### 1. **Generic Implementation**
❌ OLD: Used `(qty / items_per_sheet) * stock_waste`  
✅ NEW: Uses `((qty * leaves_per_pad) * stock_waste) * finish_size_multiplier`

The old formula divided quantity by items_per_sheet (4 for A6, 1 for A4), but TXT multiplies quantity by leaves_per_pad value, then applies finish size multiplier.

### 2. **Wrong Constants**
❌ OLD: A5 had impos=26/guilo=18, A6 had impos=22/guilo=14, A4 had impos=30/guilo=20  
✅ NEW: All 3 use impos=15, guilo=12 (from TXT)

### 3. **Missing Box Board Cost**
❌ OLD: No box board cost component  
✅ NEW: Adds box board per pad (0.07/0.03/0.15 depending on size)

### 4. **Wrong Padding Logic**
❌ OLD: Used fixed `glue_cost_per_pad` (0.12, 0.12, 0.20)  
✅ NEW: Uses quantity-based tiered padding rates (7 tiers)

### 5. **No Field Price Logic**
❌ OLD: Hardcoded print/stock prices in calculate() method  
✅ NEW: Reads prices from JSON field config via helper methods

---

## Field Price Extraction Methods

All 3 calculators now have these helper methods:

```python
def _get_finish_size_multiplier(self, finish_size: str) -> Decimal:
    """Get finish size multiplier from field price"""
    # A5: 0.5, A6: 0.25, A4: 1.0

def _get_leaves_per_pad_value(self, leaves_per_pad: int) -> Decimal:
    """Get leaves per pad value from field price"""
    # A5: {25:12.5, 50:25, 100:50}
    # A6: {10:5, 15:7.5, 25:12.5, 50:25, 100:50}
    # A4: {25:12.5, 50:25, 100:50, 200:100}

def _get_print_type_price(self, print_type: str) -> Decimal:
    """Get print type price per sheet from field price"""
    # Colour 2-sided: 0.096
    # Colour 1-sided: 0.048
    # B&W 2-sided: 0.02
    # B&W 1-sided: 0.01

def _get_stock_type_price(self, stock_type: str) -> Decimal:
    """Get stock type price per sheet from field price"""
    # Recycled: 0.06
    # 100GSM: 0.054
    # 90GSM: 0.033
    # 80GSM: 0.03
```

---

## Testing Strategy

### Test Cases Per Calculator

For each size (A5, A6, A4), test:

1. **Baseline Test:**
   - Quantity: 100
   - Artworks: 1
   - Leaves: 50
   - Print: Black & White 1 sided
   - Stock: 80GSM

2. **High Volume Test:**
   - Quantity: 2000
   - Artworks: 2
   - Leaves: 100 (or 200 for A4)
   - Print: Colour 2 sided
   - Stock: 100GSM

3. **Premium Test:**
   - Quantity: 500
   - Artworks: 3
   - Leaves: 25
   - Print: Colour 1 sided
   - Stock: Recycled

4. **Edge Case Test:**
   - Quantity: 50
   - Artworks: 1
   - Leaves: 10 (A6 only) or 25
   - Print: Black & White 2 sided
   - Stock: 90GSM

### Validation Required

For each test case:
1. Calculate with new backend
2. Get quote from Shopify website
3. Compare total price (should match exactly)
4. Compare breakdown values (setup, content, cutting, padding)
5. Verify double GST (1.1 * 1.1 = 21% total)

---

## Preserved Correct Logic

These components were already correct and kept unchanged:

### ✅ Profit Margin Tiers (13 tiers)
```python
def _get_profit_margin(self, subtotal: float) -> Decimal:
    if subtotal <= 500: return Decimal('0.8')
    elif subtotal <= 1000: return Decimal('0.8')
    elif subtotal <= 1500: return Decimal('0.8')
    elif subtotal <= 2000: return Decimal('0.75')
    elif subtotal <= 2500: return Decimal('0.72')
    elif subtotal <= 3000: return Decimal('0.72')
    elif subtotal <= 4000: return Decimal('0.65')
    elif subtotal <= 5000: return Decimal('0.55')
    elif subtotal <= 7500: return Decimal('0.52')
    elif subtotal <= 10000: return Decimal('0.47')
    elif subtotal <= 15000: return Decimal('0.42')
    elif subtotal <= 20000: return Decimal('0.41')
    else: return Decimal('0.41')
```

### ✅ Double GST Application
```python
total2 = (sub_total + (sub_total * profit_margin)) * Decimal('1.1')
total_price = total2 * Decimal('1.1')  # 1.1 * 1.1 = 21% total
```

This is correct and deliberate - TXT confirms double GST calculation.

---

## File Changes Summary

### NotepadsA5_Shopify_Calculator.py
- **Lines changed:** 217 (entire file rewritten)
- **Old constants:** impos=26, guilo=18, items_per_sheet=2, glue_cost=0.12
- **New constants:** impos=15, guilo=12, boxBoard=0.07, padding tiers 0.2/0.15/0.1
- **Old formula:** Generic sheets = qty / items_per_sheet
- **New formula:** Exact TXT leaves = ((qty * leaves_value) * waste) * finish_multiplier

### NotepadsA6_Shopify_Calculator.py
- **Lines changed:** 230 (entire file rewritten)
- **Old constants:** impos=22, guilo=14, items_per_sheet=4, glue_cost=0.12
- **New constants:** impos=15, guilo=12, boxBoard=0.03, padding tiers 0.1/0.05/0.03
- **Old formula:** Generic sheets = qty / items_per_sheet
- **New formula:** Exact TXT leaves = ((qty * leaves_value) * waste) * finish_multiplier

### NotepadsA4_Shopify_Calculator.py
- **Lines changed:** 251 (entire file rewritten)
- **Old constants:** impos=30, guilo=20, items_per_sheet=1, glue_cost=0.20
- **New constants:** impos=15, guilo=12, boxBoard=0.15, padding tiers 0.3/0.25/0.2
- **Old formula:** Generic sheets = qty / items_per_sheet
- **New formula:** Exact TXT leaves = ((qty * leaves_value) * waste) * finish_multiplier
- **CRITICAL:** Uses different field IDs (F7, F8, F10, F11 vs F3, F4, F5, F6)

---

## Next Steps

### Immediate (Before Production)
1. ✅ Rewrite all 3 backends - **COMPLETE**
2. ⏳ Create comprehensive test cases (4 per calculator = 12 total)
3. ⏳ Get website validation quotes for all test cases
4. ⏳ Run automated test suite comparing backend vs website
5. ⏳ Document any remaining discrepancies

### Follow-Up Analysis
- Analyze remaining 13 "NOT YET ANALYZED" calculators
- Check for similar generic implementation issues
- Prioritize fixes based on production usage

---

## Key Takeaways

1. **All 3 Notepads backends were completely wrong** - using generic formulas not matching TXT
2. **Size-specific differences critical** - box board costs, padding rates, finish multipliers, field IDs
3. **Field price logic missing** - old backends hardcoded prices, new ones read from JSON config
4. **Formula structure identical** - all 3 use same TXT pattern with size-specific constants
5. **A4 field mapping different** - uses F7/F8/F10/F11 instead of F3/F4/F5/F6

---

## Related Documentation

- `NOTEPADS_ANALYSIS_COMPLETE_JAN24_2026.md` - Initial analysis showing all discrepancies
- `SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt` - Source TXT formulas
  - Lines 1-540: Notepads A5
  - Lines 538-1100: Notepads A6
  - Lines 1098-1650: Notepads A4

---

**Status: ALL 3 CALCULATORS REWRITTEN TO EXACT TXT FORMULAS** ✅  
**Next: Create test cases and get website validation quotes** ⏳
