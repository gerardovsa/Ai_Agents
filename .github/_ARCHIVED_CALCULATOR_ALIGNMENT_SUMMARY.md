# Calculator Alignment Project - Summary & Instructions
**Created:** January 19, 2026  
**Last Updated:** January 19, 2026
**Status:** In Progress - Groups 1-3 Partial, Groups 4-6 In Progress

---

## 🚨 CRITICAL: WORK ONE CALCULATOR AT A TIME

**⚠️ DO NOT BULK EDIT MULTIPLE CALCULATORS ⚠️**

Each calculator MUST be:
1. ✅ Analyzed individually (backend → wrapper → schema)
2. ✅ Fixed individually (schema, then wrapper)
3. ✅ Tested individually (minimum 4 tests)
4. ✅ Validated individually (all tests passing)
5. ✅ Committed individually (separate git commit per calculator)

**Why?** Bulk changes cause:
- ❌ Copy-paste errors across calculators
- ❌ Missing unique parameter requirements
- ❌ Untested combinations
- ❌ Difficult rollback if issues found

---

## 📊 CURRENT STATUS (January 19, 2026)

**Overall Progress: 1.6/3.0 (53% Complete)**

| Component | Status | Details |
|-----------|--------|---------|
| **kwargs Removal** | 96% ✅ | 26/27 done (spiral_simple pending) |
| **None Defaults** | 63% ⚠️ | 17/27 done (10 pending in Groups 4-6) |
| **Validation** | 0% ❌ | 0/27 done (ALL MISSING) |

**Groups Status:**
- Group 1: 2.0/3.0 - Has None defaults, NO validation ⚠️
- Group 2: 1.6/3.0 - Mostly None defaults, NO validation, spiral_simple broken ❌
- Group 3: 2.0/3.0 - Has None defaults, NO validation ⚠️
- Group 4: 1.0/3.0 - NO None defaults, NO validation ❌
- Group 5: 1.4/3.0 - Partial None defaults, NO validation ❌
- Group 6: 1.5/3.0 - Partial None defaults, NO validation ❌

---

## 📚 DOCUMENTATION CREATED

### 1. **CALCULATOR_ALIGNMENT_INSTRUCTIONS.md**
Complete step-by-step guide for AI agents to:
- Analyze backend calculators (source of truth)
- Identify schema-wrapper-backend misalignments
- Fix schemas to match backend exactly
- Update wrappers with legacy parameter support
- Create validation tests
- Document all changes

### 2. **CALCULATOR_GROUPS.md**
Divides 30 calculators into 6 groups of 5:
- **Group 1:** Business Cards & Flyers (PRIORITY - where bug was found)
- **Group 2:** Bound Books (complex multi-parameter)
- **Group 3:** Notepads & Printing
- **Group 4:** Signs & Displays  
- **Group 5:** Promotional Products
- **Group 6:** Specialty & Cleanup

### 3. **TEST_TEMPLATE.py**
Ready-to-use test template with 12 test cases:
- Test 1-2: New correct parameter names
- Test 3-4: Legacy deprecated parameters with warnings
- Test 5-7: Parameter validation & enum checking
- Test 8-9: Backend integration & type verification
- Test 10-12: Edge cases & error handling

### 4. **schema_validator.py** (Already Updated)
Enhanced validation system with:
- `ParameterValidator` class - detects unknown parameters
- Helpful error messages with suggestions
- Logging of validation failures

---

## 🎯 THE PROPER 3-PART PATTERN

**ALL calculators MUST implement ALL 3 parts:**

### **Part 1: Remove `**kwargs` ✅ (96% Done)**
```python
# ❌ OLD (silently catches wrong params):
def calculate_product_shopify(quantity, **kwargs):

# ✅ NEW (explicit parameters only):
def calculate_product_shopify(quantity, param1=None, param2=None):
```

### **Part 2: Use None Defaults ⚠️ (63% Done)**
```python
# ❌ WRONG (arbitrary defaults mask missing params):
def calculate_product_shopify(
    quantity: int,
    print_type: str = "Colour",  # Bad: masks if param was provided
    paper_stock: str = "Satin"   # Bad: arbitrary default
):

# ✅ CORRECT (None allows validation):
def calculate_product_shopify(
    quantity: int,
    print_type: str = None,      # Good: can check if provided
    paper_stock: str = None,     # Good: can validate after translation
    legacy_colour: bool = None   # Legacy param for backwards compatibility
):
```

### **Part 3: Validate After Legacy Translation ❌ (0% Done - CRITICAL!)**
```python
# This is THE MISSING PIECE in all 27 calculators!

def calculate_product_shopify(
    quantity: int,
    print_type: str = None,
    legacy_colour: bool = None
):
    warnings = []
    
    # 1. LEGACY TRANSLATION FIRST
    if legacy_colour is not None:
        print_type = "Colour" if legacy_colour else "Black & White"
        warnings.append({
            "deprecated": "legacy_colour",
            "use_instead": "print_type",
            "translated_to": print_type
        })
    
    # 2. VALIDATION AFTER TRANSLATION (MISSING FROM ALL CALCULATORS!)
    if print_type is None:
        return {
            "success": False,
            "error": "Missing required parameter: 'print_type' (or legacy 'legacy_colour')"
        }
    
    # 3. Backend call (safe, params validated)
    result = calculator.calculate(print_type=print_type)
    
    response = {"success": True, "total_price": result.total_price}
    if warnings:
        response["warnings"] = warnings
    
    return response
```

---

## 🎯 THE STRATEGY

---

## 🚀 EXECUTION PLAN

**⚠️ CRITICAL: ONE CALCULATOR AT A TIME - NO EXCEPTIONS ⚠️**

### **Phase 1: Complete Group 1 (5 calculators)**
**Current Status:** 2.0/3.0 - Has None defaults, MISSING validation

**Required Actions PER CALCULATOR:**
1. ✅ Read backend signature (source of truth)
2. ✅ Add validation block after legacy translation
3. ✅ Test with 4 test cases (new params, legacy params, consistency, missing params)
4. ✅ Verify 4/4 tests passing
5. ✅ Commit individually: `fix(calculator): add validation to <product>`
6. ✅ Move to NEXT calculator (repeat 1-5)

**Calculators:**
- [ ] economical_business_cards (None ✅, validation ❌)
- [ ] premium_business_cards (None ✅, validation ❌)
- [ ] folded_flyers (None ✅, validation ❌)
- [ ] printed_letterheads (None ✅, validation ❌)
- [ ] with_compliments_slips (None ✅, validation ❌)

**Time Estimate:** 1 hour per calculator = 5 hours total

---

### **Phase 2: Fix Group 2 Issues + Add Validation (5 calculators)**
**Current Status:** 1.6/3.0 - Mostly None defaults, NO validation, spiral_simple broken

**Required Actions:**
1. Fix `spiral_books_simple_shopify` (remove **kwargs, add None defaults)
2. Add validation to ALL 5 calculators (one at a time)
3. Test each individually

**Calculators:**
- [ ] wire_bound_books (None ✅, validation ❌)
- [ ] spiral_bound_books (None ✅, validation ❌)
- [ ] perfect_bound_books (None ✅, validation ❌)
- [ ] saddle_stitch_books (None ✅, validation ❌)
- [ ] spiral_books_simple (**kwargs ❌, None ❌, validation ❌) **FIX FIRST**

**Time Estimate:** 6 hours (1.5h for spiral_simple fix, 1h each for 5 validations)

---

### **Phase 3: Complete Group 3 Validation (5 calculators)**
**Current Status:** 2.0/3.0 - Has None defaults, MISSING validation

**Required Actions:**
1. Add validation to all 5 calculators (one at a time)
2. Test each individually

**Calculators:**
- [ ] notepads_a4 (None ✅, validation ❌)
- [ ] notepads_a5 (None ✅, validation ❌)
- [ ] notepads_a6 (None ✅, validation ❌)
- [ ] custom_poster_printing (None ✅, validation ❌)
- [ ] custom_vinyl_stickers (None ✅, validation ❌)

**Time Estimate:** 5 hours (1h each)

---

### **Phase 4: Complete Groups 4-6 (Full Pattern - 12 calculators)**
**Current Status:** Groups 4-6 have partial/no None defaults, NO validation

**Required Actions PER CALCULATOR:**
1. Remove **kwargs (if present)
2. Add None defaults to required params
3. Add legacy parameter support (if applicable)
4. Add validation after legacy translation
5. Test individually (4 tests minimum)

**Group 4 - Signs (5 calculators):**
- [ ] election_signs (None ❌, validation ❌)
- [ ] construction_signs (None ❌, validation ❌)
- [ ] bollard_signs (None ❌, validation ❌)
- [ ] corflute_insert_a_frame (None ❌, validation ❌)
- [ ] metal_face_a_frame (None ❌, validation ❌)

**Group 5 - Promotional (5 calculators):**
- [ ] luxury_classic_pull_up_banners (None ✅, validation ❌)
- [ ] selfie_frames (None ✅, validation ❌)
- [ ] stackable_cubes (None ❌, validation ❌)
- [ ] strut_cards_a3 (None ❌, validation ❌)
- [ ] strut_cards_a4 (None ❌, validation ❌)

**Group 6 - Specialty (2 calculators):**
- [ ] premium_bookmarks (None ✅, validation ❌)
- [ ] corflute_signs_shopify (None ❌, validation ❌)

**Time Estimate:** 15 hours (1-1.5h each calculator)

---

## 📋 FOR EACH CALCULATOR (ONE AT A TIME!)

**⚠️ Complete these steps FULLY for ONE calculator before moving to the next ⚠️**

### **Input (What AI Receives):**
```
Calculator Name: calculate_folded_flyers_shopify
Backend File: UI/modules_external/quote-calculator/backend/shopify_calculators/FoldedFlyers_Shopify_Calculator.py
Wrapper Location: Line 1357 in calculator_wrapper.py
Schema Location: calculator_tools.json
Instructions: CALCULATOR_ALIGNMENT_INSTRUCTIONS.md
```

### **Process (Complete for ONE calculator):**
1. ✅ Analyze backend signature (STEP 1 - 10 minutes)
2. ✅ Verify/add None defaults to wrapper (STEP 2 - 5 minutes)
3. ✅ Add validation block after legacy translation (STEP 3 - 15 minutes)
4. ✅ Create 4 test cases (STEP 4 - 20 minutes):
   - Test 1: New parameters work
   - Test 2: Legacy parameters work with warnings
   - Test 3: Price consistency (new = legacy pricing)
   - Test 4: Missing required parameter rejected
5. ✅ Run tests, verify 4/4 passing (STEP 5 - 5 minutes)
6. ✅ Fix any failing tests (STEP 6 - variable)
7. ✅ Commit changes (STEP 7 - 5 minutes):
   ```
   fix(calculator): add validation to folded_flyers
   
   - Add validation after legacy translation
   - Validate size, stock, print_type params
   - Clear error messages for missing params
   - All 4 tests passing
   ```

**Total Time Per Calculator:** 60 minutes average

### **⚠️ THEN and ONLY THEN move to next calculator**

### **Output (What AI Delivers PER CALCULATOR):**
```
✅ Updated wrapper with validation block
✅ Test file with 4 tests (or add to group test file)
✅ Test results: 4/4 passing
✅ Git commit: Individual commit per calculator
✅ Brief summary: "Calculator X now has validation, 4/4 tests passing"
```

---

## ✅ SUCCESS CRITERIA

### **Per Calculator (Complete Before Moving On):**
- ✅ No **kwargs in signature
- ✅ Required params have None defaults
- ✅ Legacy translation present (if applicable)
- ✅ **VALIDATION BLOCK AFTER TRANSLATION** (critical!)
- ✅ 4/4 tests passing minimum
- ✅ Individual git commit made

### **Per Group (5 calculators completed individually):**
- ✅ All 5 calculators have validation
- ✅ 20/20 tests passing (4 per calculator)
- ✅ 5 individual commits (one per calculator)
- ✅ Group status updated in CALCULATOR_GROUPS.md
- ✅ Pattern score 3.0/3.0 for group

### **Overall Project (All 27 calculators):**
- ✅ 27 calculators with full 3-part pattern
- ✅ 108+ tests passing (4 per calculator minimum)
- ✅ Zero **kwargs in wrappers
- ✅ All validation blocks implemented
- ✅ 27 individual commits (one per calculator)
- ✅ Overall pattern score: 3.0/3.0
✅ Test results (5/5 passing)
✅ Alignment report (CALCULATOR_<PRODUCT>_ALIGNMENT.md)
```

---

## ✅ SUCCESS CRITERIA

### **Per Calculator:**
- ✅ Schema params match backend exactly
- ✅ Wrapper removes `**kwargs`
- ✅ Wrapper adds legacy param support with warnings
- ✅ Parameter validation decorator added
- ✅ 5/5 tests passing minimum
- ✅ Documentation complete

### **Per Group (5 calculators):**
- ✅ 25/25 tests passing
- ✅ Git branch created: `fix/calculator-alignment-group-<N>`
- ✅ All changes committed
- ✅ Group summary report created
- ✅ Ready for PR review

### **Overall Project:**
- ✅ ~30 calculators aligned
- ✅ ~150 tests passing (5 per calculator)
- ✅ Zero `**kwargs` in wrappers
- ✅ All schemas match backend signatures
- ✅ Legacy compatibility maintained
- ✅ Comprehensive documentation

---

## 🛠️ TOOLS PROVIDED

### **1. Validation System (Already in Code)**
```python
@calculator_wrapper(validate_params=True)
def calculate_<product>_shopify(...):
    # Automatically validates parameters
    # Rejects unknown params with suggestions
```

### **2. Test Template**
```python
# Copy TEST_TEMPLATE.py
# Customize for each calculator
# Run: pytest test_calculator_<product>_alignment.py -v
```

### **3. Instructions Document**
```markdown
# Complete step-by-step guide
# What to analyze, how to fix, what to test
# Error handling patterns
# Commit message format
```

### **4. Group Assignments**
```markdown
# Calculator groupings with:
# - File locations
# - Line numbers
# - Known issues
# - Priority levels
```

---

## 🚨 CRITICAL REMINDERS

### **DO NOT:**
- ❌ Touch backend calculator logic
- ❌ Change pricing calculations
- ❌ Modify backend method signatures
- ❌ Break existing functionality

### **DO:**
- ✅ Update schemas to match backend
- ✅ Add legacy parameter support in wrappers
- ✅ Remove all `**kwargs` from wrappers
- ✅ Add validation decorators
- ✅ Create comprehensive tests
- ✅ Document all changes

### **WHEN IN DOUBT:**
- Check backend signature (source of truth)
- Look for JSON config files
- Check docstrings
- Test manually
- Document uncertainty in report

---

## 📊 PROGRESS TRACKING

Create file: `PROGRESS.md`

```markdown
| Group | Calculator | Schema | Wrapper | Tests | Status |
|-------|-----------|--------|---------|-------|--------|
| 1 | economical_business_cards | ⚪ | ⚪ | 0/5 | Not Started |
| 1 | premium_business_cards | ⚪ | ⚪ | 0/5 | Not Started |
| 1 | folded_flyers | ⚪ | ⚪ | 0/5 | Not Started |
| 1 | printed_letterheads | ⚪ | ⚪ | 0/5 | Not Started |
| 1 | with_compliments_slips | ⚪ | ⚪ | 0/5 | Not Started |

Legend: ⚪ Not Started | 🟡 In Progress | 🟢 Complete | 🔴 Failed
```

---

## 🎓 LEARNING OUTCOMES

After completing this project, you will have:

1. **Perfect alignment** between AI schemas, wrappers, and backend
2. **Comprehensive test coverage** for all calculators
3. **Backwards compatibility** with deprecation warnings
4. **Parameter validation** preventing silent failures
5. **Clear documentation** of all calculator signatures
6. **Confidence** in calculator behavior and pricing

---

## 📞 SUPPORT

If issues arise:

1. **Check Instructions:** CALCULATOR_ALIGNMENT_INSTRUCTIONS.md
2. **Check Backend:** Look at actual calculator code
3. **Check Tests:** TEST_TEMPLATE.py for examples
4. **Document Issue:** In group report
5. **Continue:** Move to next calculator, revisit later

---

## 🏁 GET STARTED

```bash
# 1. Read instructions
cat .github/CALCULATOR_ALIGNMENT_INSTRUCTIONS.md

# 2. Check your group assignment
cat .github/CALCULATOR_GROUPS.md

# 3. Start with Group 1, Calculator 1
# Follow STEP 1-7 in instructions

# 4. Run tests
pytest tests/calculators/alignment/test_calculator_economical_business_cards_alignment.py -v

# 5. Document results
# Create CALCULATOR_ECONOMICAL_BUSINESS_CARDS_ALIGNMENT.md
```

---

**READY TO BEGIN!**

Start with **GROUP 1** - this is where the user's bug was discovered.
The alignment issue that caused `cellophane="Matt"` to be silently ignored.

Good luck! 🚀
