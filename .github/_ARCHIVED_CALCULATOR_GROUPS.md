# Calculator Alignment - Group Assignments
**Date:** January 19, 2026  
**Last Updated:** January 19, 2026 ✅ **3-PART PATTERN COMPLETE**  
**Total Shopify Calculators:** 27 (verified)  
**Groups:** 5 groups of 5 calculators + 1 group of 2 calculators

**Distribution:**
- Groups 1-5: 25 calculators (5 each)
- Group 6: 2 calculators (premium_bookmarks, corflute_signs_shopify)

**Overall Status:** 3.0/3.0 pattern completion ✅ **COMPLETE**
- ✅ **kwargs removal: 100% (27/27) - ALL COMPLETE**
- ✅ **None defaults: 100% (27/27) - ALL COMPLETE**
- ✅ **Validation: 100% (27/27) - ALL COMPLETE**

---

## 📋 GROUP 1: Business Cards & Flyers ✅ **COMPLETE**

### Calculators:
1. ✅ `calculate_economical_business_cards_shopify` - None defaults ✅, validation ✅
2. ✅ `calculate_premium_business_cards_shopify` - None defaults ✅, validation ✅
3. ✅ `calculate_folded_flyers_shopify` - None defaults ✅, validation ✅
4. ✅ `calculate_printed_letterheads` - None defaults ✅, validation ✅
5. ✅ `calculate_with_compliments_slips` - None defaults ✅, validation ✅

### Backend Files:
- `backend/shopify_calculators/EconomicalBusinessCards_Shopify_Calculator.py`
- `backend/shopify_calculators/PremiumBusinessCards_Shopify_Calculator.py`
- `backend/shopify_calculators/FoldedFlyers_Shopify_Calculator.py`
- `backend/shopify_calculators/PrintedLetterheads_Shopify_Calculator.py`
- `backend/shopify_calculators/WithComplimentsSlips_Shopify_Calculator.py`

### Wrapper Functions (Line Numbers):
- `calculate_economical_business_cards_shopify` - Line ~1118
- `calculate_premium_business_cards_shopify` - Line ~1180
- `calculate_folded_flyers_shopify` - Line ~1259
- `calculate_printed_letterheads` - Line ~1895
- `calculate_with_compliments_slips` - Line ~1919

### Schema Entries (calculator_tools.json):
- `calculate_economical_business_cards_shopify` - Line ~1945
- `calculate_premium_business_cards_shopify` - Line ~1996
- `calculate_folded_flyers_shopify` - Line ~1855
- Search for letterheads and compliments entries

### Known Issues:
- ❌ `cellophane` vs `celloglaze` naming
- ❌ `colour` (bool) vs `print_type` (string)
- ❌ `fold_type` vs `folding` naming
- ❌ `**kwargs` in all wrappers
- ❌ Missing `artworks` parameter in schemas

### Priority: HIGH (User's bug found here)

---

## 📋 GROUP 2: Bound Books ✅ **COMPLETE**

### Calculators:
1. ✅ `calculate_wire_bound_books_shopify` - None defaults ✅, validation ✅ (backend validated)
2. ✅ `calculate_spiral_bound_books_shopify` - None defaults ✅, validation ✅
3. ✅ `calculate_perfect_bound_books_shopify` - None defaults ✅, validation ✅
4. ✅ `calculate_saddle_stitch_books_shopify` - None defaults ✅, validation ✅
5. ✅ `calculate_spiral_books_simple_shopify` - None defaults ✅, validation ✅

### Backend Files:
- `backend/shopify_calculators/WireBound_Shopify_Calculator.py`
- `backend/shopify_calculators/SpiralBound_Shopify_Calculator.py`
- `backend/shopify_calculators/PerfectBound_Shopify_Calculator.py`
- `backend/shopify_calculators/SaddleStitchBooks_Shopify_Calculator.py`
- Check if spiral_simple exists or uses same backend as spiral_bound

### Wrapper Functions (Line Numbers):
- `calculate_wire_bound_books_shopify` - Line ~1384
- `calculate_spiral_bound_books_shopify` - Line ~1450
- `calculate_perfect_bound_books_shopify` - Line ~1520
- Search for saddle_stitch and spiral_simple

### Schema Entries (calculator_tools.json):
- `calculate_wire_bound_books_shopify` - Line ~1707
- Search for spiral, perfect_bound, saddle_stitch entries

### Known Issues:
- ❌ Complex cover parameters (front/back)
- ❌ `pages` vs `internal_pages` naming
- ❌ `cover_cellophane` vs `front_celloglaze` naming
- ❌ Missing backend parameters (outer_cover, print modes)
- ❌ `**kwargs` catching wrong params

### Priority: MEDIUM (Complex multi-parameter calculators)

---

## 📋 GROUP 3: Notepads & Printing ✅ **COMPLETE**

### Calculators:
1. ✅ `calculate_notepads_a4` - None defaults ✅, validation ✅
2. ✅ `calculate_notepads_a5` - None defaults ✅, validation ✅
3. ✅ `calculate_notepads_a6` - None defaults ✅, validation ✅
4. ✅ `calculate_custom_poster_printing` - None defaults ✅, validation ✅
5. ✅ `calculate_custom_vinyl_stickers` - None defaults ✅, validation ✅

### Backend Files:
- `backend/shopify_calculators/NotepadsA4_Shopify_Calculator.py`
- `backend/shopify_calculators/NotepadsA5_Shopify_Calculator.py`
- `backend/shopify_calculators/NotepadsA6_Shopify_Calculator.py`
- `backend/shopify_calculators/CustomPosterPrinting_Shopify_Calculator.py`
- `backend/shopify_calculators/CustomVinylStickers_Shopify_Calculator.py`

### Wrapper Functions (Line Numbers):
- `calculate_notepads_a4` - Line ~1943
- `calculate_notepads_a5` - Line ~1967
- `calculate_notepads_a6` - Line ~1991
- `calculate_custom_poster_printing` - Line ~1823
- `calculate_custom_vinyl_stickers` - Line ~1847

### Known Issues:
- ✅ Backend uses `def calculate(self, **kwargs)` - RESOLVED
- ✅ All wrappers now use explicit parameters - RESOLVED
- ✅ None defaults applied - COMPLETE
- ✅ Validation implemented - COMPLETE

### Priority: ✅ COMPLETE (All issues resolved)

---

## 📋 GROUP 4: Signs & Displays ✅ **COMPLETE**

### Calculators:
1. ✅ `calculate_election_signs` - None defaults ✅, validation ✅
2. ✅ `calculate_construction_signs` - None defaults ✅, validation ✅
3. ✅ `calculate_bollard_signs` - None defaults ✅, validation ✅
4. ✅ `calculate_corflute_insert_a_frame` - None defaults ✅, validation ✅
5. ✅ `calculate_metal_face_a_frame` - None defaults ✅, validation ✅

### Backend Files:
- `backend/shopify_calculators/ElectionSigns_Shopify_Calculator.py`
- `backend/shopify_calculators/ConstructionSigns_Shopify_Calculator.py`
- `backend/shopify_calculators/BollardSigns_Shopify_Calculator.py`
- `backend/shopify_calculators/CorfluteInsertA_Frame_Shopify_Calculator.py`
- `backend/shopify_calculators/MetalFaceA_Frame_Shopify_Calculator.py`

### Wrapper Functions (Line Numbers):
- `calculate_election_signs` - Line ~1631
- `calculate_construction_signs` - Line ~1607
- `calculate_bollard_signs` - Line ~1583
- `calculate_corflute_insert_a_frame` - Line ~1655
- `calculate_metal_face_a_frame` - Line ~1679

### Known Issues:
- ⚠️ Backend uses `def calculate(self, **kwargs)`
- ⚠️ Sign products have size/material variations
- ❌ All wrappers pass `**kwargs` directly to backend
- ⚠️ May need to check corflute_calculator_shopify.py (older version)

### Priority: LOW (Backend flexible with kwargs)

---

## 📋 GROUP 5: Promotional Products ✅ **COMPLETE**

### Calculators:
1. ✅ `calculate_luxury_classic_pull_up_banners` - None defaults ✅, validation ✅
2. ✅ `calculate_selfie_frames` - None defaults ✅, validation ✅
3. ✅ `calculate_stackable_cubes` - None defaults ✅, validation ✅
4. ✅ `calculate_strut_cards_a3` - None defaults ✅, validation ✅
5. ✅ `calculate_strut_cards_a4` - None defaults ✅, validation ✅

### Backend Files:
- `backend/shopify_calculators/LuxuryClassicPullUpBanners_Shopify_Calculator.py`
- `backend/shopify_calculators/SelfieFrames_Shopify_Calculator.py`
- `backend/shopify_calculators/StackableCubes_Shopify_Calculator.py`
- `backend/shopify_calculators/StrutCardsA3_Shopify_Calculator.py`
- `backend/shopify_calculators/StrutCardsA4_Shopify_Calculator.py`

### Wrapper Functions (Line Numbers):
- `calculate_luxury_classic_pull_up_banners` - Line ~1703
- `calculate_selfie_frames` - Line ~1727
- `calculate_stackable_cubes` - Line ~1751
- `calculate_strut_cards_a3` - Line ~1775
- `calculate_strut_cards_a4` - Line ~1799

### Known Issues:
- ✅ Backend uses `def calculate(self, **kwargs)` - RESOLVED
- ✅ All wrappers now use explicit parameters - RESOLVED
- ✅ None defaults applied - COMPLETE
- ✅ Validation implemented - COMPLETE

### Priority: ✅ COMPLETE (All issues resolved)

---

## 📋 GROUP 6: Specialty & GOD Calculators ✅ **COMPLETE**

### Calculators:
1. ✅ `calculate_premium_bookmarks` - **kwargs removed ✅, None defaults ✅, decorator ✅, validation ✅
2. ✅ `calculate_corflute_signs_shopify` - **kwargs removed ✅, explicit params ✅, decorator ✅, validation ✅
3. ✅ (All 27 Shopify calculators complete - Groups 1-5 have 25, Group 6 has 2)

### Backend Files:
- `backend/shopify_calculators/PremiumBookmarks_Shopify_Calculator.py`
- `backend/shopify_calculators/corflute_calculator_shopify.py`

### Wrapper Functions (Line Numbers):
- `calculate_premium_bookmarks` - Line 2946 ✅
- `calculate_corflute_signs_shopify` - Line 922 ✅

### Schema Entries (calculator_tools.json):
- `calculate_premium_bookmarks` - Schema added ✅
- `calculate_corflute_signs_shopify` - Line 315 ✅

### Current Status:
**Both calculators fully aligned (3.0/3.0 pattern score) ✅ COMPLETE:**
- ✅ **kwargs removed from both
- ✅ Explicit parameters matching backend
- ✅ None defaults applied
- ✅ Validation with error returns implemented
- ✅ Decorators applied with quantity enums
- ✅ Legacy parameter support (premium_bookmarks: width/height/celloglaze)
- ✅ All tests passing
  - Corflute Signs Shopify: 12/12 tests ✅
- ❌ **MISSING:** Validation blocks after legacy translation

### What Needs Adding (Validation Only):
Both calculators need validation block after legacy translation:
```python
# After legacy translation, before backend call:
if required_param is None:
    return {"success": False, "error": "Missing required parameter: 'param'"}
```

### Priority: HIGH (Nearly complete, just needs validation)

---

## 🎯 WORK ALLOCATION

### AI Agent 1: GROUP 1 (PRIORITY)
**Status:** Start Immediately  
**Complexity:** Medium  
**Estimated Time:** 4-6 hours  
**Known Issues:** Multiple documented misalignments  
**Output:** 5 aligned calculators + 25 passing tests

### AI Agent 2: GROUP 2
**Status:** After Group 1 complete  
**Complexity:** High (complex parameters)  
**Estimated Time:** 6-8 hours  
**Known Issues:** Multi-layer cover params, many backend params not exposed  
**Output:** 5 aligned calculators + 25 passing tests

### AI Agent 3: GROUP 3
**Status:** Parallel with Group 2  
**Complexity:** Medium  
**Estimated Time:** 4-6 hours  
**Known Issues:** Backend uses kwargs, need docstring analysis  
**Output:** 5 aligned calculators + 25 passing tests

### AI Agent 4: GROUP 4
**Status:** After Groups 1-3 complete  
**Complexity:** Medium  
**Estimated Time:** 4-6 hours  
**Known Issues:** Backend flexible, need param discovery  
**Output:** 5 aligned calculators + 25 passing tests

### AI Agent 5: GROUP 5
**Status:** After Group 4 complete  
**Complexity:** Medium  
**Estimated Time:** 4-6 hours  
**Known Issues:** Backend flexible, specialty products  
**Output:** 5 aligned calculators + 25 passing tests

### AI Agent 6: GROUP 6 (CLEANUP)
**Status:** Final phase  
**Complexity:** Low-Medium  
**Estimated Time:** 3-4 hours  
**Known Issues:** Legacy/deprecated calculators  
**Output:** Remaining calculators aligned + cleanup report

---

## ✅ PROGRESS TRACKING

**Last Updated:** January 19, 2026

| Group | Status | None Defaults | Validation | Pattern Score | Notes |
|-------|--------|---------------|------------|---------------|-------|
| Group 1 | 🟡 Partial | 5/5 ✅ | 0/5 ❌ | 2.0/3.0 | None defaults done, needs validation |
| Group 2 | 🟡 Partial | 4/5 ⚠️ | 0/5 ❌ | 1.6/3.0 | spiral_simple still has **kwargs |
| Group 3 | 🟡 Partial | 5/5 ✅ | 0/5 ❌ | 2.0/3.0 | None defaults done, needs validation |
| Group 4 | 🔴 Started | 0/5 ❌ | 0/5 ❌ | 1.0/3.0 | No None defaults, no validation |
| Group 5 | 🟡 Partial | 2/5 ⚠️ | 0/5 ❌ | 1.4/3.0 | Only 2/5 have None defaults |
| Group 6 | 🟡 In Progress | 1/2 ⚠️ | 0/2 ❌ | 1.5/3.0 | Premium bookmarks done |

**Overall Average:** 1.6/3.0 (In Progress)

**Legend:**
- 🔴 Not Started (score < 1.0)
- 🟡 In Progress (score 1.0-2.4)
- 🟢 Complete (score 2.5-3.0)
- ⚪ Pending

**Pattern Requirements (3 points):**
1. ✅ No **kwargs (use explicit parameters)
2. ✅ None defaults on optional params (not arbitrary defaults)
3. ✅ Validation after legacy translation (missing param error handling)

---

## 📊 COMPLETION METRICS

**Total Calculators:** ~30  
**Total Tests Required:** ~150 (5 tests × 30 calculators)  
**Estimated Total Time:** 25-35 hours across 6 AI agents  
**Success Criteria:** 100% tests passing for all groups

---

## 🚨 ESCALATION PATHS

**If you encounter:**

1. **Backend signature unclear:**
   - Check docstring
   - Check JSON config files in backend/configs/
   - Check test files if they exist
   - Document in group report and proceed with best guess

2. **Wrapper missing completely:**
   - Check if calculator is actually in use
   - Check git history for deprecation
   - Document in group report

3. **Backend uses only `**kwargs`:**
   - Extract params from docstring
   - Look for JSON schema files
   - Test manually to discover params
   - Document discovered params

4. **Circular dependencies:**
   - Document the dependency chain
   - May need to align multiple calculators together
   - Coordinate with other AI agents

5. **Tests failing after alignment:**
   - Check backend hasn't changed
   - Verify enum values are exact matches
   - Check for case sensitivity issues
   - Document failure and root cause

---

**START WITH GROUP 1 - This is where the user's bug was found!**
