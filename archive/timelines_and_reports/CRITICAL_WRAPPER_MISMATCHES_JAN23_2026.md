# CRITICAL: Calculator Wrapper Mismatches Found
## Date: January 23, 2026

**Status:** 🚨 **CRITICAL MISALIGNMENTS DISCOVERED**

During systematic audit of remaining calculators, **critical mismatches** found between JSON specifications and wrapper validation logic.

---

## 🚨 CRITICAL ISSUE: Bollard Signs

### JSON Specification (`Shopify_Bollard_Signs.json`):

**Material Field:**
- Options: `["3mm Corflute", "5mm Corflute"]`
- Default: `"5mm Corflute"`

**Size Field:**
- 12 Options including:
  - "270mm W x 1000mm H - Three Sided"
  - "270mm W x 1200mm H - Three Sided"
  - "270mm W x 1800mm H - Three Sided"
  - "300mm W x 1000mm H - Three Sided"
  - "300mm W x 1200mm H - Three Sided"
  - "300mm W x 1800mm H - Three Sided"
  - "155mm W x 1000mm H - Four Sided"
  - "155mm W x 1200mm H - Four Sided"
  - "155mm W x 1800mm H - Four Sided"
  - "175mm W x 1000mm H - Four Sided"
  - "175mm W x 1200mm H - Four Sided"
  - "175mm W x 1800mm H - Four Sided"

### Wrapper Validation (`calculator_wrapper.py` line 2782-2795):

```python
# WRONG VALUES - DO NOT MATCH JSON!
valid_sizes = ["300x300", "450x450", "600x600"]  # ❌ WRONG
if material not in ["Aluminium", "Metal"]:       # ❌ WRONG
```

### Schema (`calculator_tools.json` line 1171-1188):

```json
"material": {
  "enum": ["3mm Corflute", "5mm Corflute"]  // ✅ CORRECT (matches JSON)
},
"size": {
  "enum": [
    "270mm W x 1000mm H - Three Sided",
    "270mm W x 1200mm H - Three Sided",
    ... (12 sizes total)
  ]  // ✅ CORRECT (matches JSON)
}
```

### Impact:

**CRITICAL** - This calculator **WILL FAIL 100% of the time** when called by AI agents because:
1. Wrapper validates for "Aluminium"/"Metal" but JSON/Schema use "3mm Corflute"/"5mm Corflute"
2. Wrapper validates for "300x300"/"450x450"/"600x600" but JSON has completely different size format
3. **Every single valid input will be rejected as invalid**

### Fix Required:

```python
# Line 2782-2795 in calculator_wrapper.py
valid_sizes = [
    "270mm W x 1000mm H - Three Sided",
    "270mm W x 1200mm H - Three Sided",
    "270mm W x 1800mm H - Three Sided",
    "300mm W x 1000mm H - Three Sided",
    "300mm W x 1200mm H - Three Sided",
    "300mm W x 1800mm H - Three Sided",
    "155mm W x 1000mm H - Four Sided",
    "155mm W x 1200mm H - Four Sided",
    "155mm W x 1800mm H - Four Sided",
    "175mm W x 1000mm H - Four Sided",
    "175mm W x 1200mm H - Four Sided",
    "175mm W x 1800mm H - Four Sided"
]

if material not in ["3mm Corflute", "5mm Corflute"]:
    return {"success": False, "error": f"Invalid material: '{material}'..."}
```

---

## ⚠️ Potential Issues Found (Need Verification):

### 1. Construction Signs
- Wrapper may have similar issues (needs verification against JSON)
- JSON shows: "3mm", "5mm" thickness, sizes like "450mm x 600mm", "600mm x 900mm"

### 2. Election Signs
- Wrapper may have similar issues (needs verification against JSON)
- JSON shows: "3mm", "5mm" thickness, sizes like "450mm x 600mm", "600mm x 900mm"

### 3. Notepads (A4/A5/A6)
- Need to verify stock types match between JSON and wrapper
- JSON shows: "Uncoated Bond 80GSM", "Uncoated Bond 90GSM", "Uncoated Bond 100GSM", "Revive 100% Recycled 80GSM Bond"

---

## Root Cause Analysis

**Why This Happened:**

1. **Copy-Paste Development:** Wrapper functions likely copied from template/other calculator
2. **No Validation Against JSON:** Wrapper values not cross-referenced with source JSON
3. **No Integration Testing:** No tests verify wrapper accepts JSON-specified values
4. **Schema Correct, Wrapper Wrong:** Schema team correctly extracted from JSON, wrapper team used placeholder values

**Evidence:**
- Schema enums match JSON perfectly (✅)
- Backend likely uses JSON config directly (✅)
- Only wrapper has wrong hardcoded validation (❌)

---

## Testing Recommendation

**BEFORE fixing:**
1. Test current Bollard Signs wrapper - confirm it rejects all valid inputs ✅
2. Document exact failure messages

**AFTER fixing:**
1. Test with all 12 size options + both material options = 24 combinations
2. Verify prices match expected values
3. Add to automated test suite

---

## Systematic Audit Required

**Remaining Calculators to Verify:**
1. ✅ Bollard Signs - **CRITICAL MISMATCH FOUND**
2. ⚠️ Construction Signs - Needs verification
3. ⚠️ Election Signs - Needs verification
4. ⚠️ Corflute Insert A-Frame - Needs verification
5. ⚠️ Metal Face A-Frame - Needs verification
6. ⚠️ Luxury Classic Pull Up Banners - Needs verification
7. ⚠️ Selfie Frames - Needs verification
8. ⚠️ Stackable Cubes - Needs verification
9. ⚠️ Strut Cards A3 - Needs verification
10. ⚠️ Strut Cards A4 - Needs verification
11. ⚠️ Custom Poster Printing - Needs verification
12. ⚠️ Custom Vinyl Stickers - Needs verification
13. ⚠️ Premium Bookmarks - Needs verification
14. ⚠️ Printed Letterheads - Needs verification
15. ⚠️ With Compliments Slips - Needs verification
16. ⚠️ Notepads A4 - Needs verification
17. ⚠️ Notepads A5 - Needs verification
18. ⚠️ Notepads A6 - Needs verification

**Total:** 18 calculators require JSON → Wrapper verification

---

## Priority Actions

### IMMEDIATE (Critical):
1. **FIX Bollard Signs wrapper** - Currently 100% broken
2. **Verify Construction/Election Signs** - Likely have same copy-paste issue
3. **Create test cases** for Bollard Signs to prevent regression

### HIGH (Important):
4. **Systematic audit** of all 18 remaining calculators
5. **Document all mismatches** found
6. **Create automated validation** script: JSON → Schema → Wrapper consistency check

### MEDIUM (Preventive):
7. **Implement pre-deployment check:** Wrapper validation enums must match schema enums
8. **Add integration tests** that load JSON values and test against wrapper
9. **Update development guidelines:** Always reference JSON when writing wrappers

---

## Lessons Learned

1. **Schema team did it right** - Extracted values directly from JSON
2. **Wrapper team made assumptions** - Hardcoded values without referencing JSON
3. **No cross-validation** - Schema and wrapper developed independently
4. **Testing gap** - No tests verify wrapper accepts schema-valid inputs

---

## Status

**9 Shopify Calculators (Tested):** ✅ ALL PASSING
- Wire Bound Books ✅
- Spiral Bound Books ✅ (Fixed)
- Perfect Bound Books ✅ (Fixed)
- Saddle Stitch Books ✅ (Fixed)
- Folded Flyers ✅
- Corflute Signs ✅
- Economical Business Cards ✅
- Premium Business Cards ✅
- Spiral Books Simple ✅

**18 Additional Calculators (Untested):**
- ❌ Bollard Signs - **CRITICAL FAILURE CONFIRMED**
- ⚠️ 17 Others - **UNKNOWN STATUS**

---

## Next Steps

User should decide:
1. **Fix Bollard Signs immediately?** (High priority - currently broken)
2. **Continue systematic audit of remaining 17?** (Discover scope of issue)
3. **Both?** (Parallel: Fix critical issue + audit remaining)

---

**Report Generated:** January 23, 2026  
**Auditor:** AI Agent  
**Severity:** 🚨 CRITICAL
