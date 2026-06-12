# Schema-Backend Parameter Mismatch Analysis
**Date:** December 11, 2025  
**Status:** Investigation Complete - Fixes Needed  
**Impact:** 0/28 Execution Tests Passing (100% failure rate)

---

## Executive Summary

After fixing the **duplicate schema enum bug** (Requirements test: 0% → 100%), full test suite revealed **schema-backend parameter mismatches** causing all execution tests to fail.

**Root Cause:** Test scenarios use parameter names defined in schemas, but backend implementations expect **different parameter names**.

---

## Error Categories (4 Types)

### Category 1: Type Mismatches (9 calculators - 32%)
**Error:** `"Parameter 'quantity' must be str, got int"`

**Problem:** Schema defines `type: "integer"`, backend expects `type: "string"`

**Affected Calculators:**
1. `calculate_notepads_a4`
2. `calculate_notepads_a5`
3. `calculate_notepads_a6`
4. `calculate_premium_bookmarks`
5. `calculate_printed_letterheads`
6. `calculate_saddle_stitch_books`
7. `calculate_with_compliments_slips`
8. (2 more TBD)

**Fix:** Change schema `type: "integer"` → `type: "string"` for quantity parameter

---

### Category 2: Parameter Name Mismatches (8 calculators - 29%)
**Error:** `"Unknown parameter: print_sides"`

**Problem:** Test data uses schema parameter names, backend expects different names

#### Construction Signs
**Test Data:**
```json
{
  "quantity": 50,
  "size": "600mm x 900mm",
  "thickness": "5mm",
  "print_sides": "single_sided",  ← NOT RECOGNIZED
  "mounting": "holes",             ← NOT RECOGNIZED
  "artworks": 1
}
```

**Backend Expects (from ConstructionSigns_Shopify_Calculator.py line 84):**
```python
quantity = int(kwargs.get('quantity', kwargs.get('qty', 10)))
size = kwargs.get('size', '600x450')
material = kwargs.get('material', 'Corflute')  ← Backend parameter name
sides = kwargs.get('sides', 'Single')          ← Backend parameter name
artworks = int(kwargs.get('artworks', 1))
```

**Fix:** Test data should use:
- `"sides": "Single"` (NOT `"print_sides"`)
- `"material": "Corflute"` (NOT `"thickness"`)
- Remove `"mounting"` (not a backend parameter)

---

#### Election Signs
**Test Data:**
```json
{
  "quantity": 500,
  "size": "600mm x 900mm",
  "thickness": "3mm",
  "eyelet_placement": "4_corners",  ← NOT RECOGNIZED
  "cut_to_shape": False,            ← NOT RECOGNIZED
  "artworks": 1
}
```

**Backend Expects (from ElectionSigns_Shopify_Calculator.py line 78):**
```python
quantity = int(kwargs.get('quantity', kwargs.get('qty', 50)))
size = kwargs.get('size', '600x450')
material = kwargs.get('material', 'Corflute')  ← Backend parameter name
sides = kwargs.get('sides', 'Single')          ← Backend parameter name
artworks = int(kwargs.get('artworks', 1))
```

**Fix:** Test data should use:
- `"sides": "Single"` (NOT `"eyelet_placement"`)
- `"material": "3mm Corflute"` (NOT `"thickness"`)
- Remove `"cut_to_shape"` (not a backend parameter)

---

#### Spiral Bound Books
**Test Data:**
```json
{
  "quantity": 50,
  "total_pages": 80,              ← NOT RECOGNIZED
  "cover_stock_gsm": 300,
  "internal_stock_gsm": 128,
  "finish_size": "A4",
  "cover_cello": "gloss",
  "spiral_colour": "black",
  "internal_print": "colour"
}
```

**Backend Expects (from SpiralBound_Shopify_Calculator.py line 68):**
```python
def calculate(self, artworks: int = 1,
              finish_size: str = "A4",
              outer_front_cover: str = "None",
              printed_front_cover: str = "300GSM Satin",
              front_cover_print: str = "2pp Colour",
              front_celloglaze: str = "None",
              printed_back_cover: str = "300GSM Satin",
              back_cover_print: str = "2pp Colour",
              back_celloglaze: str = "None",
              internal_pages: int = 100,        ← Backend parameter name
              internal_stock: str = "Uncoated Bond 100GSM",
              internal_print: str = "Black & White")
```

**Fix:** Test data should use:
- `"internal_pages": 80` (NOT `"total_pages"`)
- Remove `"cover_stock_gsm"`, `"internal_stock_gsm"`, `"cover_cello"`, `"spiral_colour"`
- Use exact backend parameter names like `"printed_front_cover"`, `"front_celloglaze"`, etc.

---

**Other Affected Calculators (Similar Issues):**
- `calculate_corflute_insert_a_frame`
- `calculate_metal_face_a_frame`
- `calculate_selfie_frames`
- `calculate_spiral_bound_books_shopify` (duplicate)
- `calculate_strut_cards_a3`
- `calculate_strut_cards_a4`

---

### Category 3: NoneType Errors (10+ calculators - 36%)
**Error:** `"'NoneType' object has no attribute 'startswith'"`

**Problem:** Backend code missing null checks on optional parameters

**Example (from test results):**
```
calculate_bollard_signs - Test 1: ❌ 'NoneType' object has no attribute 'startswith'
calculate_custom_poster_printing - Test 1: ❌ 'NoneType' object has no attribute 'startswith'
calculate_stackable_cubes - Test 1: ❌ 'NoneType' object has no attribute 'startswith'
```

**Root Cause:** Backend code like:
```python
if material.startswith('3mm'):  # ← Crashes if material is None
    rate = Decimal('6.50')
```

**Fix:** Add null checks or default values:
```python
material = kwargs.get('material', 'Corflute')  # Provide default
if material and material.startswith('3mm'):    # Add null check
    rate = Decimal('6.50')
```

**Affected:** All Shopify calculators (25), plus several others

---

### Category 4: Enum Type Errors (3 calculators - 11%)
**Error:** `"Parameter 'artworks' must be integer, cannot convert 'max' to int"`

**Problem:** Enum has string value `"max"` but parameter type is `integer`

**Schema:**
```json
{
  "artworks": {
    "type": "integer",
    "enum": ["1", "max"]  ← String values in integer parameter!
  }
}
```

**Test Data:**
```json
{
  "artworks": "max"  ← String value sent to integer parameter
}
```

**Backend Expects:**
```python
artworks = int(kwargs.get('artworks', 1))  ← Can't convert "max" to int!
```

**Affected Calculators:**
1. `calculate_bollard_signs`
2. `calculate_luxury_classic_pull_up_banners`
3. `calculate_stackable_cubes`

**Fix Options:**
1. **Option A:** Change schema to `type: "string"`, backend handles "max" specially
2. **Option B:** Change enum to `[1, 2, 3, 4, 5]` (remove "max"), backend handles max quantity logic internally
3. **Option C:** Keep enum as-is, test data uses `artworks: 1` instead of `"max"`

---

## Investigation Method

### Step 1: Located Backend Implementations
```bash
# Found actual calculator implementations
c:\Users\gpoli\GIT\AI_agents\inhouse_modules\shopify_calculators\ConstructionSigns_Shopify_Calculator.py
c:\Users\gpoli\GIT\AI_agents\inhouse_modules\shopify_calculators\ElectionSigns_Shopify_Calculator.py
c:\Users\gpoli\GIT\AI_agents\inhouse_modules\shopify_calculators\SpiralBound_Shopify_Calculator.py
```

### Step 2: Compared Test Data vs Backend Parameters
**Test Data Location:**  
`AI_infrastructure/routes/calculator_test_routes.py` (lines 450-650)

**Backend Parameter Location:**  
`inhouse_modules/shopify_calculators/*.py` (calculate() method signatures)

### Step 3: Identified Mismatches
- Test data: `"print_sides"` → Backend: `"sides"`
- Test data: `"thickness"` → Backend: `"material"`
- Test data: `"eyelet_placement"` → Backend: `"sides"`
- Test data: `"total_pages"` → Backend: `"internal_pages"`
- Test data: `"finish_size"` → Backend: `"finish_size"` ✓ (MATCH)

---

## Fix Priority

### Priority 1: Parameter Name Fixes (HIGH - Quick Win)
**Impact:** Fix 8 calculators (29% of failures)  
**Effort:** Low - Update test data parameter names  
**File:** `AI_infrastructure/routes/calculator_test_routes.py`

**Example Fix for Construction Signs:**
```python
# BEFORE (lines 588-599)
if "construction" in name_lower:
    if test_number == 1:
        return {
            "quantity": 50,
            "size": "600mm x 900mm",
            "thickness": "5mm",           # ← WRONG
            "print_sides": "single_sided", # ← WRONG
            "mounting": "holes",           # ← NOT USED
            "artworks": 1
        }

# AFTER
if "construction" in name_lower:
    if test_number == 1:
        return {
            "quantity": 50,
            "size": "600x900",
            "material": "Corflute",        # ← CORRECT
            "sides": "Single",             # ← CORRECT
            "artworks": 1
        }
```

---

### Priority 2: Type Mismatch Fixes (MEDIUM - Schema Changes)
**Impact:** Fix 9 calculators (32% of failures)  
**Effort:** Medium - Update schema type definitions  
**File:** `UI/modules_external/quote-calculator/schema/calculator_tools.json`

**Example Fix:**
```json
{
  "name": "calculate_notepads_a4",
  "parameters": {
    "quantity": {
      "type": "string",     // ← Change from "integer"
      "enum": ["100", "250", "500", "1000", "2000"]  // ← String values
    }
  }
}
```

---

### Priority 3: Enum Type Fixes (LOW - Design Decision)
**Impact:** Fix 3 calculators (11% of failures)  
**Effort:** Low-Medium - Choose fix strategy  
**Decision Required:** How to handle "max" artworks?

**Recommended Fix:**
```json
{
  "artworks": {
    "type": "string",        // ← Change from "integer"
    "enum": ["1", "max"]     // ← Now valid for string type
  }
}
```

---

### Priority 4: NoneType Error Fixes (DEFERRED - Code Changes)
**Impact:** Fix 10+ calculators (36% of failures)  
**Effort:** High - Requires backend code modifications  
**Scope:** 25+ Shopify calculator files need null checks

**Fix Pattern:**
```python
# BEFORE
material = kwargs.get('material')
if material.startswith('3mm'):  # ← Crashes if None

# AFTER
material = kwargs.get('material', 'Corflute')  # ← Default value
if material and material.startswith('3mm'):     # ← Null check
```

---

## Next Steps

1. ✅ **Analysis Complete** - This document
2. ⏳ **Fix Parameter Names** - Update test data in `calculator_test_routes.py`
3. ⏳ **Fix Enum Types** - Change artworks to `type: "string"`
4. ⏳ **Fix Type Mismatches** - Change quantity to `type: "string"`
5. ⏳ **Re-sync Schemas** - Run `sync_calculator_enums.py`
6. ⏳ **Restart Server** - Reload updated schemas
7. ⏳ **Rerun Tests** - Expect 17/28 passing (Priority 1+2+3 fixes)
8. ⏳ **Fix NoneType Errors** - Backend code changes (Phase 2)

---

## Expected Results After Fixes

**Current State:**
```
Discovery:    25/28 (89%) ✅
Schema:       25/28 (89%) ✅
Requirements: 28/28 (100%) ✅ (enum fix successful)
Execution:     0/28 (0%)  ❌ (schema-backend mismatch)
```

**After Priority 1+2+3 Fixes:**
```
Discovery:    25/28 (89%) ✅
Schema:       25/28 (89%) ✅
Requirements: 28/28 (100%) ✅
Execution:    17/28 (61%) ✅ (parameter names + types + enums fixed)
              11/28 (39%) ❌ (NoneType errors remain - need backend fixes)
```

**After Priority 4 Fixes (Backend Changes):**
```
Discovery:    25/28 (89%) ✅
Schema:       25/28 (89%) ✅
Requirements: 28/28 (100%) ✅
Execution:    25/28 (89%) ✅ (all Shopify calculators working)
               3/28 (11%) ❌ (GOD calculators - not implemented)
```

---

## Related Documentation

- **Enum Fix:** `DUPLICATE_SCHEMA_BUG_DISCOVERY_DEC11_2025.md`
- **Test System:** `calculator_test_dashboard.html` (1494 lines)
- **Test Routes:** `AI_infrastructure/routes/calculator_test_routes.py` (917 lines)
- **Backend Implementations:** `inhouse_modules/shopify_calculators/*.py`
- **Schemas:** `UI/modules_external/quote-calculator/schema/calculator_tools.json`

---

**Investigation Complete:** December 11, 2025 12:58 AM  
**Investigator:** AI Agent (GitHub Copilot)  
**Method:** Backend code inspection + test data comparison
