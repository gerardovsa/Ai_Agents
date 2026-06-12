# Calculator Testing Guide
**Date:** January 19, 2026  
**Last Updated:** January 19, 2026
**Purpose:** Comprehensive testing strategy for calculator alignment

---

## 🚨 CRITICAL: TEST ONE CALCULATOR AT A TIME

**⚠️ DO NOT BATCH TEST MULTIPLE CALCULATORS ⚠️**

**Testing Requirements:**
1. ✅ Test ONE calculator completely (4 tests minimum)
2. ✅ Verify ALL 4 tests passing before moving on
3. ✅ Fix any failures immediately
4. ✅ Commit that calculator's changes
5. ✅ THEN move to next calculator

**Why?**
- Individual testing catches calculator-specific issues
- Easier to debug when only one calculator is changed
- Prevents cascading failures
- Clear pass/fail per calculator

---

## 📊 CURRENT STATUS AWARENESS

**What's Actually Missing (January 19, 2026):**

| Component | Status | Completion |
|-----------|--------|------------|
| **kwargs removal | ✅ 96% | 26/27 done (spiral_simple pending) |
| None defaults | ⚠️ 63% | 17/27 done (10 need fixing) |
| **Validation** | ❌ **0%** | **0/27 done - ALL MISSING!** |

**The Validation Gap:**
- Groups 1-3 have None defaults but NO validation (15 calculators)
- Groups 4-6 need BOTH None defaults AND validation (12 calculators)
- This means **100% of calculators are missing the validation piece**

---

## 🎯 Testing Strategy

### **Three-Layer Testing:**
1. **Unit Tests** - Individual parameter validation
2. **Integration Tests** - Wrapper → Backend flow
3. **Regression Tests** - Legacy parameters still work

---

## 📋 Test Checklist (Per Calculator - ONE AT A TIME)

### ✅ **Test 1: New Parameters Work**
**Purpose:** Verify correct parameter names work without warnings
```python
result = calculate_product_shopify(
    quantity=1000,
    print_type='Colour',       # New correct name
    celloglaze='2 Side Matt'   # New correct name
)
assert result['success'] == True
assert 'warnings' not in result  # No warnings
assert result['total_price'] > 0
```

### ⚠️ **Test 2: Legacy Parameters Work With Warnings**
**Purpose:** Verify backwards compatibility with deprecation warnings
```python
result = calculate_product_shopify(
    quantity=1000,
    colour=True,           # Legacy name
    cellophane='Matt'      # Legacy name
)
assert result['success'] == True
assert 'warnings' in result  # Should have warnings
assert len(result['warnings']) >= 2
```

### 💰 **Test 3: Price Consistency (New = Legacy)**
**Purpose:** Ensure pricing identical regardless of parameter style
```python
result_new = calculate_product_shopify(
    quantity=1000,
    print_type='Colour',
    celloglaze='2 Side Matt'
)

result_legacy = calculate_product_shopify(
    quantity=1000,
    colour=True,
    cellophane='Matt'
)

assert result_new['total_price'] == result_legacy['total_price']
```

### ❌ **Test 4: Missing Required Parameter Validation (CRITICAL!)**
**Purpose:** Verify validation catches missing params - THIS IS WHAT'S MISSING!
```python
result = calculate_product_shopify(
    quantity=1000
    # Intentionally omit required params
)
assert result['success'] == False
assert 'error' in result
assert 'Missing required parameter' in result['error']
assert 'print_type' in result['error']  # Mentions param name
```

**⚠️ THIS TEST CURRENTLY FAILS FOR ALL 27 CALCULATORS!**

Without validation, missing params cause:
- Silent failures in backend
- Cryptic error messages
- AI agent confusion
- Incorrect quotes

---

## 🔧 Quick Test Pattern (Copy & Customize Per Calculator)

### **Pattern 1: New Parameters Test**
```python
def test_new_params():
    result = calculate_product_shopify(
        quantity=1000,
        param1="value1",  # Correct new name
        param2="value2"   # Correct new name
    )
    assert result["success"] == True
    assert "warnings" not in result  # No warnings
    assert result["total_price"] > 0
```

### **Pattern 2: Legacy Parameters Test**
```python
def test_legacy_params():
    result = calculate_product_shopify(
        quantity=1000,
        old_param1="value1",  # Deprecated name
        old_param2="value2"   # Deprecated name
    )
    assert result["success"] == True
    assert "warnings" in result  # Should have warnings
    assert len(result["warnings"]) == 2  # Both deprecated
    
    # Verify each warning
    warnings = result["warnings"]
    assert any(w["deprecated"] == "old_param1" for w in warnings)
    assert any(w["use_instead"] == "param1" for w in warnings)
```

### **Pattern 3: Missing Required Param Test**
```python
def test_missing_required():
    result = calculate_product_shopify(
        quantity=1000
        # Intentionally omit required param
    )
    assert result["success"] == False
    assert "error" in result
    assert "Missing required parameter" in result["error"]
    assert "param_name" in result["error"]  # Error mentions param
```

### **Pattern 4: Price Consistency Test**
```python
def test_price_consistency():
    # New params
    result_new = calculate_product_shopify(
        quantity=1000,
        param1="value1"
    )
    
    # Legacy params (same values)
    result_legacy = calculate_product_shopify(
        quantity=1000,
        old_param1="value1"  # Should translate to param1
    )
    
    # Prices must match exactly
    assert result_new["total_price"] == result_legacy["total_price"]
```

---

## 🚀 Running Tests (ONE CALCULATOR AT A TIME)

### **Individual Calculator Test Workflow:**
```powershell
# 1. Add validation to ONE calculator in calculator_wrapper.py
# 2. Create/update test for that ONE calculator
python test_single_calculator.py  # Test ONLY that calculator

# 3. Verify 4/4 tests pass
# Expected output:
# ✅ Test 1: New parameters - PASS
# ✅ Test 2: Legacy parameters - PASS
# ✅ Test 3: Price consistency - PASS
# ✅ Test 4: Missing param validation - PASS (was failing before!)

# 4. If all pass, commit that calculator
git add calculator_wrapper.py test_single_calculator.py
git commit -m "fix(calculator): add validation to <product_name>"

# 5. Move to NEXT calculator (repeat 1-4)
```

### **Group Testing (After Individual Completion):**
```powershell
# Only run after ALL calculators in group have validation
python test_group1.py  # All 5 calculators in Group 1
# Expected: 20/20 tests passing (4 per calculator × 5 calculators)
```

### **DO NOT Run Full Suite Until All Done:**
```powershell
# Only when ALL 27 calculators have validation:
python test_all_calculators.py
# Expected: 108/108 tests passing (4 per calculator × 27 calculators)
```

---

## 🔍 Debugging Failed Tests

### **Test 4 Fails: "Missing param not rejected" (CURRENT STATE)**
**Problem:** Validation block missing
**Solution:**
```python
# Add this AFTER legacy translation in wrapper:
if required_param is None:
    return {
        "success": False,
        "error": "Missing required parameter: 'required_param' (or legacy 'old_param')"
    }
```

### **Test 2 Fails: "No warnings present"**
**Problem:** Warnings list not being returned
**Check:**
1. Is warnings list created? `warnings = []`
2. Are warnings appended during legacy translation?
3. Is warnings added to response? `if warnings: response["warnings"] = warnings`

### **Test 3 Fails: "Prices don't match"**
**Problem:** Legacy translation incorrect
**Check:**
1. Is legacy param translating to correct new value?
2. Are enum values exact matches?
3. Is translation happening BEFORE backend call?

---

## 📊 Test Results Format

### **Expected Output:**
```
======================================================================
TESTING: Product Name
======================================================================

[Test 1: New Parameters]
✅ SUCCESS
   Price: $1,234.56
   Warnings: 0

[Test 2: Legacy Parameters]
⚠️  DEPRECATED PARAMETERS in calculate_product_shopify:
   old_param=value → new_param='value'

✅ SUCCESS
   Price: $1,234.56
   Warnings: 1
      - old_param → new_param

[Test 3: Missing Required Parameter]
✅ CORRECTLY REJECTED
   Error: Missing required parameter: 'param1' (or legacy 'old_param')
```

---

## 🎓 Understanding Validation Flow

### **The Proper Pattern:**

```
1. Function receives params
   ↓
2. Legacy translation (if legacy param provided)
   ↓
3. Validation (check required params present after translation)
   ↓
4. Backend call (with translated/validated params)
   ↓
5. Return result (with warnings if legacy used)
```

### **Why This Order Matters:**

**❌ WRONG (default values):**
```python
def calculate_product(param1: str = "default"):
    # Problem: masks whether param was actually provided
```

**✅ CORRECT (None + validation):**
```python
def calculate_product(
    param1: str = None,      # Required but optional for legacy
    old_param: str = None    # Legacy
):
    # Translate legacy first
    if old_param is not None:
        param1 = translate(old_param)
    
    # Then validate
    if param1 is None:
        return {"error": "Missing required parameter"}
    
    # Now safe to use param1
```

---

## 📈 Success Criteria

### **Per Calculator:**
- ✅ All new parameter tests pass (5/5)
- ✅ All legacy parameter tests pass (3/3)
- ✅ All error handling tests pass (4/4)
- ✅ Price consistency verified
- ✅ No `**kwargs` in wrapper
- ✅ Validation errors are helpful

### **Per Group:**
- ✅ 100% calculator pass rate (5/5 in each group)
- ✅ All tests execute in < 10 seconds
- ✅ No Python exceptions during tests

### **Overall Project:**
- ✅ All 30 calculators passing
- ✅ Backwards compatibility maintained
- ✅ Clear deprecation path documented

---

## 🔍 Debugging Failed Tests

### **Test fails with "Missing required parameter":**
**Check:**
1. Is legacy translation happening BEFORE validation?
2. Is the legacy parameter spelled correctly?
3. Does the validation message mention both new and legacy names?

### **Test fails with "Unknown parameter":**
**Check:**
1. Is `validate_params=True` in decorator?
2. Is parameter spelled correctly (case-sensitive)?
3. Is parameter in wrapper function signature?

### **Legacy test shows no warnings:**
**Check:**
1. Is warnings list being populated in translation block?
2. Is warnings list being added to response?
3. Is console logging working (`print(log_msg)`)?

### **Prices don't match (new vs legacy):**
**Check:**
1. Is translation logic correct?
2. Are enum values mapping properly?
3. Is backend receiving identical values?

---

## 📝 Test Documentation Template

```python
\"\"\"
Test Suite: Calculator <Product> Alignment
Date: <Date>
Status: <PASS/FAIL>

Test Results:
- New Parameters: 5/5 ✅
- Legacy Parameters: 3/3 ✅
- Error Handling: 4/4 ✅

Issues Found: None

Notes:
- All parameters aligned with backend
- Legacy support working correctly
- Validation messages helpful and clear
\"\"\"
```

---

## 🎯 Quick Validation Commands

```powershell
# Test that validation works
python -c "from calculator_wrapper import calculate_product_shopify; r = calculate_product_shopify(quantity=1000); print('PASS' if not r['success'] else 'FAIL: Should reject missing params')"

# Test that new params work
python -c "from calculator_wrapper import calculate_product_shopify; r = calculate_product_shopify(quantity=1000, param1='value'); print('PASS' if r['success'] else f'FAIL: {r[\"error\"]}')"

# Test that legacy params work with warnings
python -c "from calculator_wrapper import calculate_product_shopify; r = calculate_product_shopify(quantity=1000, old_param='value'); print(f'Warnings: {len(r.get(\"warnings\", []))}')"
```

---

## ✅ Validation Checklist (Per Calculator - Complete Before Moving On)

**Before starting next calculator, verify:**
- [ ] No **kwargs in wrapper signature
- [ ] Required params have None defaults (not arbitrary defaults)
- [ ] Legacy translation present (if applicable)
- [ ] **VALIDATION BLOCK AFTER TRANSLATION** (critical missing piece!)
- [ ] Test 1 passing (new params work)
- [ ] Test 2 passing (legacy params work with warnings)
- [ ] Test 3 passing (prices match)
- [ ] **Test 4 passing (missing params rejected)** ← Was failing, now passes!
- [ ] Individual git commit made
- [ ] Calculator marked complete in tracking doc

**Only when ALL checkboxes checked, move to next calculator.**

---

## 📊 Progress Tracking Template

```markdown
## Calculator Validation Progress

### Group 1: Business Cards & Flyers
- [ ] economical_business_cards (None ✅, validation ❌ → ✅)
- [ ] premium_business_cards (None ✅, validation ❌ → ✅)
- [ ] folded_flyers (None ✅, validation ❌ → ✅)
- [ ] printed_letterheads (None ✅, validation ❌ → ✅)
- [ ] with_compliments_slips (None ✅, validation ❌ → ✅)

Status: 0/5 complete → 5/5 complete
Tests: 0/20 passing → 20/20 passing
```

---

## 🎯 Expected Outcomes Per Calculator

**BEFORE Adding Validation:**
- Pattern Score: 2.0/3.0 (has None defaults, no validation)
- Test 1: ✅ PASS (new params work)
- Test 2: ✅ PASS (legacy params work)
- Test 3: ✅ PASS (prices match)
- Test 4: ❌ **FAIL** (missing params not caught!)

**AFTER Adding Validation:**
- Pattern Score: 3.0/3.0 (complete pattern!)
- Test 1: ✅ PASS (new params work)
- Test 2: ✅ PASS (legacy params work)
- Test 3: ✅ PASS (prices match)
- Test 4: ✅ **PASS** (missing params rejected properly!)

---

**Remember:** Test 4 failing → missing validation block. Test 4 passing → validation working correctly. This is THE critical piece missing from all 27 calculators right now!
