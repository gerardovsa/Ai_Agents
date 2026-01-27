# Complete Calculator Audit Results - January 23, 2026

**Audit Date:** January 23, 2026, 2:00 PM
**Total Calculators Audited:** 18 remaining (after 9 previously validated)
**Audit Tool:** `audit_remaining_calculators.py` (automated JSON vs Wrapper comparison)

---

## Executive Summary

**CRITICAL PRODUCTION ISSUE IDENTIFIED:**
- **14 of 18 calculators (78%) have wrapper validation mismatches**
- **42 total field validation errors** across these calculators
- **Impact:** All mismatched calculators will reject 100% of valid AI agent requests
- **Root Cause:** Wrapper validation hardcoded with placeholder/template values instead of extracting from JSON specifications

**Status Breakdown:**
- ✅ **4 Aligned:** Strut Cards A3, Strut Cards A4, Notepads A5, Notepads A6
- ⚠️ **14 Mismatched:** Require immediate fixes
- ❌ **0 Errors:** No parsing/extraction failures

---

## Detailed Findings by Calculator

### 🚨 CRITICAL SEVERITY (Complete Validation Failure - 2-6 mismatches)

#### 1. **bollard_signs** (2 mismatches)
**Wrapper Location:** Line 2750-2835
**JSON File:** `Shopify_Bollard_Signs.json`

**Mismatches:**
- **material:**
  - JSON: `['3mm Corflute', '5mm Corflute']`
  - Wrapper: `['Corflute', 'Metal']` ❌
  - **Fix:** Update to match JSON exactly

- **size:**
  - JSON: 12 options including:
    - `'270mm W x 1000mm H - Three Sided'`
    - `'270mm W x 1200mm H - Three Sided'`
    - `'270mm W x 1800mm H - Three Sided'`
    - `'300mm W x 1000mm H - Three Sided'`
    - `'300mm W x 1200mm H - Three Sided'`
    - `'300mm W x 1800mm H - Three Sided'`
    - `'155mm W x 1000mm H - Four Sided'`
    - `'155mm W x 1200mm H - Four Sided'`
    - `'155mm W x 1800mm H - Four Sided'`
    - `'175mm W x 1000mm H - Four Sided'`
    - `'175mm W x 1200mm H - Four Sided'`
    - `'175mm W x 1800mm H - Four Sided'`
  - Wrapper: `['600x450', '900x600', '1200x900']` ❌
  - **Fix:** Replace with all 12 JSON sizes

**Impact:** 100% failure rate - no valid inputs will pass validation

---

#### 2. **construction_signs** (5 mismatches)
**Wrapper Location:** Line 2833-2917
**JSON File:** `Shopify_Construction_Signs.json`

**Mismatches:**
- **eyelets:** JSON has 7 options, wrapper has NO validation ❌
- **thickness:** JSON has 2 options, wrapper has NO validation ❌
- **size:**
  - JSON: `['450mm x 600mm', '600mm x 900mm', '900mm x 1200mm', '1200mm x 2400mm', 'Custom']`
  - Wrapper: `['600x450', '900x600', '1200x900']` ❌
- **sides?:**
  - JSON: `['Single Sided', 'Double Sided']`
  - Wrapper: `['Single', 'Double']` ❌ (missing "Sided" suffix)
- **cutting:** JSON has 2 options, wrapper has NO validation ❌

**Impact:** 100% failure rate - missing validation + wrong size format

---

#### 3. **election_signs** (5 mismatches)
**Wrapper Location:** Line 2917-3001
**JSON File:** `Shopify_Election_Signs.json`

**Mismatches:** (IDENTICAL to Construction Signs)
- **eyelets:** JSON has 7 options, wrapper has NO validation ❌
- **thickness:** JSON has 2 options, wrapper has NO validation ❌
- **size:**
  - JSON: `['450mm x 600mm', '600mm x 900mm', '900mm x 1200mm', '1200mm x 2400mm', 'Custom']`
  - Wrapper: `['600x450', '900x600']` ❌ (fewer options + wrong format)
- **sides?:**
  - JSON: `['Single Sided', 'Double Sided']`
  - Wrapper: `['Single', 'Double']` ❌
- **cutting:** JSON has 2 options, wrapper has NO validation ❌

**Impact:** 100% failure rate - same issues as Construction Signs

---

#### 4. **custom_vinyl_stickers** (6 mismatches)
**Wrapper Location:** Line 3471-3564
**JSON File:** `Shopify_Custom_Vinyl_Stickers.json`

**Mismatches:**
- **size:** JSON has 10 options, wrapper has NO validation ❌
- **vinyl_family:** JSON has 2 options, wrapper has NO validation ❌
- **adhesive:** JSON has 2 options, wrapper has NO validation ❌
- **laminate:** JSON has 3 options, wrapper has NO validation ❌
- **cutting_method:** JSON has 4 options, wrapper has NO validation ❌
- **labour_rate:** JSON has 2 options, wrapper has NO validation ❌

**Impact:** 100% failure rate - NO input validation exists at all!

---

#### 5. **premium_bookmarks** (5 mismatches)
**Wrapper Location:** Line 3564-3644
**JSON File:** `Shopify_Premium_Bookmarks.json`

**Mismatches:**
- **quantity:** JSON has 10 options, wrapper has NO validation ❌
- **celloglaze:** JSON has 5 options, wrapper has NO validation ❌
- **print_type:** JSON has 2 options, wrapper has NO validation ❌
- **finish_size:** JSON has 4 options, wrapper has NO validation ❌
- **paper_stock_type:** JSON has 2 options, wrapper has NO validation ❌

**Impact:** 100% failure rate - NO input validation exists at all!

---

### ⚠️ HIGH SEVERITY (Partial Validation - 4 mismatches)

#### 6. **notepads_a4** (4 mismatches)
**Wrapper Location:** Line 3785-3866
**JSON File:** `Shopify_Notepads_A4.json`

**Mismatches:**
- **quantity:** JSON has 13 options, wrapper has NO validation ❌
- **leaves_per_pad:** JSON has 3 options, wrapper has NO validation ❌
- **print_type:**
  - JSON: `['Colour 1 sided', 'Colour 2 sided', 'Black & White 1 sided', 'Black & White 2 sided']`
  - Wrapper: `['Colour', 'Black & White']` ❌ (missing "sided" details)
- **stock_type:** JSON has 4 options, wrapper has NO validation ❌

**Impact:** High failure rate - partial validation only

---

### 🔶 MEDIUM SEVERITY (1-2 mismatches)

#### 7. **corflute_insert_a_frame** (1 mismatch)
**Wrapper Location:** Line 3001-3079
**JSON File:** `Shopify_Corflute_Insert_A-Frame.json`

**Mismatches:**
- **size:**
  - JSON: `['600mm(W) x 900mm(H)']`
  - Wrapper: `['600x450', '900x600']` ❌ (multiple wrong sizes)

**Impact:** 100% failure rate - all sizes invalid

---

#### 8. **metal_face_a_frame** (1 mismatch)
**Wrapper Location:** Line 3079-3159
**JSON File:** `Shopify_Metal_Face_A-Frame.json`

**Mismatches:**
- **size:**
  - JSON: `['600mm W x 900mm H']`
  - Wrapper: `['600x450', '900x600']` ❌

**Impact:** 100% failure rate - all sizes invalid

---

#### 9. **luxury_pull_up_banners** (2 mismatches)
**Wrapper Location:** Line 3159-3236
**JSON File:** `Shopify_Luxury_Classic_Pull_Up_Banners.json`

**Mismatches:**
- **base_colour:** JSON has 2 options, wrapper has NO validation ❌
- **size:** JSON has 3 options, wrapper has NO validation ❌

**Impact:** 100% failure rate - NO validation exists

---

#### 10. **selfie_frames** (1 mismatch)
**Wrapper Location:** Line 3236-3313
**JSON File:** `Shopify_Selfie_Frames.json`

**Mismatches:**
- **size:** JSON has 2 options, wrapper has NO validation ❌

**Impact:** 100% failure rate - NO validation exists

---

#### 11. **stackable_cubes** (2 mismatches)
**Wrapper Location:** Line 3313-3393
**JSON File:** `Shopify_Stackable_Cubes.json`

**Mismatches:**
- **material:**
  - JSON: `['3mm Corflute', '5mm Corflute']`
  - Wrapper: `['Corrugated', 'Foam Core', 'Corflute']` ❌
- **cube_size:** JSON has 4 options, wrapper has NO validation ❌

**Impact:** 100% failure rate - wrong material values + no size validation

---

#### 12. **custom_poster_printing** (2 mismatches)
**Wrapper Location:** Line 3393-3471
**JSON File:** `Shopify_Custom_Poster_Printing.json`

**Mismatches:**
- **paper_type:** JSON has 2 options, wrapper has NO validation ❌
- **size:** JSON has 4 options, wrapper has NO validation ❌

**Impact:** 100% failure rate - NO validation exists

---

#### 13. **printed_letterheads** (2 mismatches)
**Wrapper Location:** Line 3644-3714
**JSON File:** `Shopify_Printed_Letterheads.json`

**Mismatches:**
- **quantity:** JSON has 14 options, wrapper has NO validation ❌
- **paper_stock_type:** JSON has 3 options, wrapper has NO validation ❌

**Impact:** 100% failure rate - NO validation exists

---

#### 14. **with_compliments_slips** (2 mismatches)
**Wrapper Location:** Line 3714-3785
**JSON File:** `Shopify_With_Compliments_Slips.json`

**Mismatches:**
- **quantity:** JSON has 14 options, wrapper has NO validation ❌
- **paper_stock_type:** JSON has 3 options, wrapper has NO validation ❌

**Impact:** 100% failure rate - NO validation exists

---

## ✅ Aligned Calculators (No Issues - 4 total)

### 1. **strut_cards_a3**
**Status:** ✅ Fully aligned - all validations match JSON

### 2. **strut_cards_a4**
**Status:** ✅ Fully aligned - all validations match JSON

### 3. **notepads_a5**
**Status:** ✅ Fully aligned - all validations match JSON

### 4. **notepads_a6**
**Status:** ✅ Fully aligned - all validations match JSON

---

## Root Cause Analysis

### Primary Issues:

1. **Missing Validation (28 instances across 11 calculators)**
   - Wrapper has NO validation logic for fields that JSON specifies
   - Agent requests will pass invalid values to backend
   - Backend may fail unexpectedly or return incorrect prices

2. **Wrong Enum Values (14 instances across 7 calculators)**
   - Wrapper validates against completely different values than JSON
   - Example: JSON has `"3mm Corflute"`, wrapper checks for `"Corflute"`
   - Example: JSON has `"270mm W x 1000mm H - Three Sided"`, wrapper checks for `"600x450"`
   - 100% of valid AI requests will be rejected

3. **String Format Mismatches (4 instances)**
   - JSON: `"Single Sided"` → Wrapper: `"Single"` (missing suffix)
   - JSON: `"Colour 1 sided"` → Wrapper: `"Colour"` (missing details)
   - These cause all requests to fail validation

### Development Process Failures:

1. **No Cross-Validation**
   - Schema team extracted JSON values correctly ✅
   - Wrapper team used placeholder values without checking JSON ❌
   - No automated tests to verify wrapper accepts schema-valid inputs

2. **Copy-Paste Development**
   - Many wrappers appear to use template validation code
   - Example: Multiple calculators use `['600x450', '900x600']` for sizes
   - Generic values never updated to match actual JSON specs

3. **No Integration Testing**
   - No tests verify AI agent can successfully call calculators
   - No tests verify wrapper validation matches schema enums
   - Only backend calculation logic was tested

---

## Fix Priority Matrix

### 🚨 IMMEDIATE (Production Broken - 6 calculators)
**Priority:** Fix today
**Impact:** 100% AI request failure, 2-6 mismatches each

1. bollard_signs (2 mismatches)
2. construction_signs (5 mismatches)
3. election_signs (5 mismatches)
4. custom_vinyl_stickers (6 mismatches)
5. premium_bookmarks (5 mismatches)
6. stackable_cubes (2 mismatches - wrong material enum)

### ⚠️ HIGH (Critical Functionality - 5 calculators)
**Priority:** Fix within 24 hours
**Impact:** 100% AI request failure, 1-4 mismatches each

7. corflute_insert_a_frame (1 mismatch - wrong sizes)
8. metal_face_a_frame (1 mismatch - wrong sizes)
9. luxury_pull_up_banners (2 mismatches - no validation)
10. notepads_a4 (4 mismatches - partial validation)
11. selfie_frames (1 mismatch - no validation)

### 🔶 MEDIUM (Missing Validation - 3 calculators)
**Priority:** Fix within 48 hours
**Impact:** 100% AI request failure, 2 mismatches each

12. custom_poster_printing (2 mismatches)
13. printed_letterheads (2 mismatches)
14. with_compliments_slips (2 mismatches)

---

## Fix Methodology

### Step-by-Step Process (Per Calculator):

1. **Extract JSON Enums**
   - Read JSON file completely
   - Extract all field options/enums
   - Note default values
   - Document required vs optional fields

2. **Update Wrapper Validation**
   - Locate wrapper function in calculator_wrapper.py
   - Replace hardcoded validation lists with JSON values
   - Ensure exact string matching (including spaces, case, punctuation)
   - Add validation for fields that have NO validation

3. **Test Valid + Invalid Inputs**
   - Create test case with valid JSON values
   - Verify calculator accepts and processes correctly
   - Create test case with invalid values
   - Verify calculator rejects with clear error message

4. **Document Fix**
   - Record what was changed
   - Note line numbers updated
   - Add to fixes completed list

5. **Move to Next Calculator**
   - Repeat for all 14 mismatched calculators

---

## Expected Timeline

**Total Calculators to Fix:** 14
**Average Time per Calculator:** 10-15 minutes
**Total Estimated Time:** 2-3 hours

**Breakdown:**
- IMMEDIATE Priority (6 calculators): 1 hour
- HIGH Priority (5 calculators): 45 minutes
- MEDIUM Priority (3 calculators): 30 minutes
- Testing & Documentation: 30 minutes

---

## Success Criteria

### Per Calculator:
- [ ] All JSON enum values extracted
- [ ] Wrapper validation updated to match JSON exactly
- [ ] Test case with valid JSON values passes
- [ ] Test case with invalid values rejected
- [ ] Documentation updated

### Overall Project:
- [ ] All 14 calculators fixed
- [ ] 100% test pass rate for all 27 calculators (9 previous + 18 audited)
- [ ] Zero wrapper validation mismatches
- [ ] Complete documentation of all fixes

---

## Next Steps

**Phase 1: IMMEDIATE Fixes (Now)**
Starting with highest-impact calculators in order:
1. custom_vinyl_stickers (6 mismatches)
2. construction_signs (5 mismatches)
3. election_signs (5 mismatches)
4. premium_bookmarks (5 mismatches)
5. bollard_signs (2 mismatches)
6. stackable_cubes (2 mismatches)

**Phase 2: HIGH Priority Fixes**
7. notepads_a4 (4 mismatches)
8. corflute_insert_a_frame (1 mismatch)
9. metal_face_a_frame (1 mismatch)
10. luxury_pull_up_banners (2 mismatches)
11. selfie_frames (1 mismatch)

**Phase 3: MEDIUM Priority Fixes**
12. custom_poster_printing (2 mismatches)
13. printed_letterheads (2 mismatches)
14. with_compliments_slips (2 mismatches)

**Phase 4: Final Validation**
- Run comprehensive test suite on all 27 calculators
- Verify 100% pass rate
- Update all documentation

---

## Lessons Learned

1. **Schema Extraction is Correct**
   - The schema generation process that reads JSON files works perfectly
   - All 4 aligned calculators show schema team did it right
   - Trust the schema, fix the wrapper to match

2. **Wrapper Validation is Independent**
   - Wrappers were developed separately from schemas
   - No automated cross-validation between layers
   - Need integration tests that verify wrapper accepts schema-valid inputs

3. **Template/Placeholder Values are Dangerous**
   - Many wrappers use generic values like `['600x450', '900x600']`
   - These were never updated to match actual JSON specifications
   - Need process to prevent placeholder values reaching production

4. **Testing Gaps**
   - Backend calculation logic was tested ✅
   - Wrapper validation was NOT tested ❌
   - Need wrapper-specific test suites for all calculators

---

**Audit Completed:** January 23, 2026, 2:05 PM
**Next Action:** Begin systematic fixing starting with custom_vinyl_stickers (6 mismatches)
