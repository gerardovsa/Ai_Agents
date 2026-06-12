# Test Suite Requirements - January 23, 2026

## 🎯 **PRIMARY OBJECTIVE**

The test suite MUST test BOTH methods because **the AI agent may use EITHER approach** depending on context:

### **Method 1: WRAPPER (Tool Registry) - Production Primary Path**
```
AI Agent → inhouse_calculate_quote('flyers', {...})
  → RegistryV3.execute_tool('calculate_folded_flyers_shopify', ...)
    → calculator_wrapper.calculate_folded_flyers_shopify(...)
      → FoldedFlyersShopifyCalculator().calculate_quote(...)
```

### **Method 2: DIRECT (Backend) - Schema-Only Path**
```
AI Agent → calculate_folded_flyers_shopify(...)
  → FoldedFlyersShopifyCalculator().calculate_quote(...)
```

---

## 📚 **CRITICAL DOCUMENTATION SOURCES**

### **1. CALCULATOR_ALIGNMENT_INSTRUCTIONS.md**
**Location:** `.github/CALCULATOR_ALIGNMENT_INSTRUCTIONS.md`  
**Key Sections:**
- Lines 331-410: "⚠️ THIS IS THE MISSING PIECE IN ALL 27 CALCULATORS"
- **Part 3: Validate After Legacy Translation** (most critical section)

**What It Teaches:**

**3-Part Pattern (ALL REQUIRED):**

1. ✅ **Remove `**kwargs`** - Explicit parameters only
2. ✅ **None defaults** - Not arbitrary defaults (allows validation)
3. ✅ **Validation AFTER legacy translation** - The missing piece!

```python
def calculate_product_shopify(
    quantity: int,
    print_type: str = None,        # ✅ None allows validation
    legacy_colour: bool = None     # ✅ Legacy for compatibility
):
    warnings = []
    
    # STEP 1: TRANSLATE LEGACY PARAMS FIRST
    if legacy_colour is not None:
        print_type = "Colour" if legacy_colour else "Black & White"
        warnings.append({"deprecated": "legacy_colour", "translated_to": print_type})
    
    # STEP 2: VALIDATE AFTER TRANSLATION (CRITICAL!)
    if print_type is None:
        return {
            "success": False,
            "error": "Missing required parameter: 'print_type' (or legacy 'legacy_colour')"
        }
    
    if print_type not in ["Colour", "Black & White"]:
        return {
            "success": False,
            "error": f"Invalid print_type: '{print_type}'. Must be 'Colour' or 'Black & White'"
        }
```

---

### **2. CALCULATOR_TESTING_GUIDE.md**
**Location:** `.github/CALCULATOR_TESTING_GUIDE.md`  
**Key Sections:**
- Lines 38-42: "**100% of calculators are missing the validation piece**"
- Lines 95-130: **Test 4 - Missing Required Parameter Validation (CRITICAL!)**
- Lines 230-245: Debugging failed tests due to missing validation

**What It Teaches:**

**4 Required Tests Per Calculator:**

**✅ Test 1: New Parameters Work**
```python
result = calculate_product_shopify(
    quantity=1000,
    print_type='Colour',       # New correct name
    celloglaze='2 Side Matt'   # New correct name
)
assert result['success'] == True
assert 'warnings' not in result  # No warnings expected
assert result['total_price'] > 0
```

**⚠️ Test 2: Legacy Parameters Work With Warnings**
```python
result = calculate_product_shopify(
    quantity=1000,
    colour=True,           # Legacy name
    cellophane='Matt'      # Legacy name
)
assert result['success'] == True
assert 'warnings' in result           # Should have warnings
assert len(result['warnings']) >= 2   # Both deprecated
```

**💰 Test 3: Price Consistency (New = Legacy)**
```python
result_new = calculate_product_shopify(quantity=1000, print_type='Colour')
result_legacy = calculate_product_shopify(quantity=1000, colour=True)

assert result_new['total_price'] == result_legacy['total_price']
```

**❌ Test 4: Missing Required Parameter Validation**
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

---

### **3. VALIDATION_COMPLETE_JAN19_2026.md**
**Location:** Root directory  
**Key Sections:**
- Lines 1-85: Complete implementation of validation across all 27 calculators
- Lines 24-85: "AI Learning Workflow Example" showing how structured errors teach AI

**What It Teaches:**

**AI Learning Through Structured Errors:**

```
Initial Call:
calculate_business_cards(quantity=500, print_type="Rainbow", celloglaze="Sparkle")

Response:
{
  "success": false,
  "error": "Invalid print_type: 'Rainbow'. Must be 'Colour' or 'Black & White'"
}

AI Learns: Valid options are "Colour" or "Black & White"

Retry 1:
calculate_business_cards(quantity=500, print_type="Colour", celloglaze="Sparkle")

Response:
{
  "success": false,
  "error": "Invalid celloglaze: 'Sparkle'. Must be one of: None, Gloss 1 Sided, Matt 1 Sided, Matt 2 Sided, Gloss 2 Sided"
}

AI Learns: Valid celloglaze options

Retry 2:
calculate_business_cards(quantity=500, print_type="Colour", celloglaze="Matt 1 Sided")

Response:
{
  "success": true,
  "total_price": 450.00,
  "unit_price": 0.90
}

Success! AI learned valid parameters through iterative error feedback.
```

**Validation Types Implemented:**

1. **Valid Enum Values:**
   ```python
   {"error": "Invalid print_type: 'Rainbow'. Must be 'Colour' or 'Black & White'"}
   ```

2. **Valid Ranges:**
   ```python
   {"error": "Invalid artworks: 100. Must be between 1 and 50"}
   {"error": "Invalid width_mm: 3000. Must be between 500 and 1200 millimeters"}
   ```

3. **Business Rules:**
   ```python
   {"error": "Invalid printed_pages: 38. Must be divisible by 4 (40-800 pages)"}
   ```

4. **Required Parameters:**
   ```python
   {"error": "Missing required parameter: 'print_type' (or legacy 'colour')"}
   ```

---

## 🎯 **WHAT THE TEST SUITE MUST DO**

### **Architecture: Dual Method Testing**

The test suite must test BOTH pathways that the AI agent uses in production:

```
┌─────────────────────────────────────────────────────┐
│              AI AGENT DECISION POINT                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Context-based routing:                            │
│  - Complex workflows → WRAPPER (inhouse_*)         │
│  - Direct tool calls → WRAPPER (calculate_*)       │
│  - Schema-only mode → DIRECT (backend class)       │
│                                                     │
└──────────────┬────────────────────┬─────────────────┘
               │                    │
        ┌──────▼──────┐      ┌─────▼──────┐
        │   WRAPPER   │      │   DIRECT   │
        │   METHOD    │      │   METHOD   │
        └──────┬──────┘      └─────┬──────┘
               │                    │
               └────────┬───────────┘
                        │
                 ┌──────▼──────┐
                 │  BACKEND    │
                 │ CALCULATOR  │
                 └─────────────┘
```

### **Required Test Structure**

```python
"""
Comprehensive Calculator Test Suite
Tests BOTH wrapper and direct methods for each calculator
Validates 3-part pattern: **kwargs removal, None defaults, validation
"""

def test_calculator_complete(calculator_name):
    """Test single calculator with all 4 tests via BOTH methods"""
    
    # ===================================================================
    # METHOD 1: WRAPPER (Tool Registry - Production Primary)
    # ===================================================================
    print(f"\n{'='*70}")
    print(f"TESTING {calculator_name.upper()} - WRAPPER METHOD")
    print(f"{'='*70}")
    
    # Test 1: New Parameters (Wrapper)
    wrapper_new = test_wrapper_new_params(calculator_name)
    
    # Test 2: Legacy Parameters with Warnings (Wrapper)
    wrapper_legacy = test_wrapper_legacy_params(calculator_name)
    
    # Test 3: Price Consistency (Wrapper)
    test_wrapper_price_consistency(wrapper_new, wrapper_legacy)
    
    # Test 4: Missing Parameter Validation (Wrapper)
    test_wrapper_missing_params(calculator_name)
    
    # ===================================================================
    # METHOD 2: DIRECT (Backend Class - Alternative Path)
    # ===================================================================
    print(f"\n{'='*70}")
    print(f"TESTING {calculator_name.upper()} - DIRECT METHOD")
    print(f"{'='*70}")
    
    # Test 1: Direct Backend Call with Enums
    direct_result = test_direct_backend_call(calculator_name)
    
    # Test 2: Price Consistency (Wrapper vs Direct)
    test_wrapper_direct_consistency(wrapper_new, direct_result)
    
    # Test 3: Direct Missing Parameter Validation
    test_direct_missing_params(calculator_name)
```

### **Test 1: Wrapper New Parameters**
```python
def test_wrapper_new_params(calculator_name):
    """Test wrapper with current parameter names"""
    from UI.modules_external.quote-calculator.implementations.calculator_wrapper import (
        calculate_folded_flyers_shopify  # Import actual wrapper
    )
    
    result = calculate_folded_flyers_shopify(
        quantity=1000,
        size="DL",
        stock="Satin 128GSM",
        double_sided=True,
        print_type="Colour",
        folding="Single Fold",
        celloglaze="None",
        artworks=1
    )
    
    # Assertions
    assert result['success'] == True, "Wrapper should succeed with valid params"
    assert 'warnings' not in result, "No warnings for current parameter names"
    assert result['total_price'] > 0, "Must return valid price"
    assert result['product_type'] == "Folded Flyers", "Must return product type"
    
    print(f"✅ Test 1 (Wrapper New): PASSED")
    print(f"   Price: ${result['total_price']}")
    return result
```

### **Test 2: Wrapper Legacy Parameters**
```python
def test_wrapper_legacy_params(calculator_name):
    """Test wrapper with deprecated parameter names"""
    from UI.modules_external.quote-calculator.implementations.calculator_wrapper import (
        calculate_folded_flyers_shopify
    )
    
    result = calculate_folded_flyers_shopify(
        quantity=1000,
        size="DL",
        stock="Satin 128GSM",
        double_sided=True,
        colour=True,           # ⚠️ LEGACY parameter
        fold_type="Single Fold",  # ⚠️ LEGACY parameter
        cellophane="None",     # ⚠️ LEGACY parameter
        artworks=1
    )
    
    # Assertions
    assert result['success'] == True, "Legacy params should work"
    assert 'warnings' in result, "Must return deprecation warnings"
    assert len(result['warnings']) >= 2, "Should warn about colour, cellophane"
    
    # Verify warnings structure
    for warning in result['warnings']:
        assert 'deprecated' in warning
        assert 'use_instead' in warning
        assert 'translated_to' in warning
    
    print(f"⚠️  Test 2 (Wrapper Legacy): PASSED")
    print(f"   Warnings: {len(result['warnings'])}")
    for w in result['warnings']:
        print(f"      - {w['deprecated']} → {w['use_instead']}")
    
    return result
```

### **Test 3: Price Consistency**
```python
def test_wrapper_price_consistency(new_result, legacy_result):
    """Verify new params and legacy params produce identical pricing"""
    
    new_price = new_result['total_price']
    legacy_price = legacy_result['total_price']
    
    assert new_price == legacy_price, (
        f"Price mismatch! New: ${new_price}, Legacy: ${legacy_price}"
    )
    
    print(f"💰 Test 3 (Price Consistency): PASSED")
    print(f"   New params price: ${new_price}")
    print(f"   Legacy params price: ${legacy_price}")
```

### **Test 4: Missing Parameter Validation (CRITICAL!)**
```python
def test_wrapper_missing_params(calculator_name):
    """Test validation catches missing required parameters"""
    from UI.modules_external.quote-calculator.implementations.calculator_wrapper import (
        calculate_folded_flyers_shopify
    )
    
    # Call with ONLY quantity (missing required params)
    result = calculate_folded_flyers_shopify(
        quantity=1000
        # Intentionally omit: size, stock, print_type, etc.
    )
    
    # Assertions
    assert result['success'] == False, "Should fail with missing params"
    assert 'error' in result, "Must return error message"
    assert 'Missing required parameter' in result['error'] or 'Invalid' in result['error']
    
    print(f"❌ Test 4 (Missing Params): PASSED")
    print(f"   Correctly rejected: {result['error']}")
```

### **Test 5: Direct Backend Method**
```python
def test_direct_backend_call(calculator_name):
    """Test direct backend calculator call (bypassing wrapper)"""
    from shopify_calculators.FoldedFlyers_Shopify_Calculator import (
        FoldedFlyersShopifyCalculator,
        PrintSides, PrintType, FinishSize, PaperStock, FoldType, Celloglaze
    )
    
    calc = FoldedFlyersShopifyCalculator()
    result = calc.calculate_quote(  # ← Note: calculate_quote(), NOT calculate()!
        quantity=1000,
        print_sides=PrintSides.DOUBLE_SIDE,  # ← Must use ENUMS!
        print_type=PrintType.COLOUR,
        finish_size=FinishSize.DL,
        paper_stock=PaperStock.SATIN_128GSM,
        artworks=1,
        fold_type=FoldType.SINGLE_FOLD,
        celloglaze=Celloglaze.NONE
    )
    
    # Convert dataclass to dict
    result_dict = {
        'total_price': float(result.final_price),
        'unit_price': float(result.unit_price),
        'quantity': result.quantity
    }
    
    print(f"✅ Test 5 (Direct Backend): PASSED")
    print(f"   Price: ${result_dict['total_price']}")
    
    return result_dict
```

### **Test 6: Wrapper vs Direct Consistency**
```python
def test_wrapper_direct_consistency(wrapper_result, direct_result):
    """Verify wrapper and direct methods produce identical pricing"""
    
    wrapper_price = wrapper_result['total_price']
    direct_price = direct_result['total_price']
    
    # Allow small floating point differences
    assert abs(wrapper_price - direct_price) < 0.01, (
        f"Price mismatch! Wrapper: ${wrapper_price}, Direct: ${direct_price}"
    )
    
    print(f"🔀 Test 6 (Wrapper vs Direct): PASSED")
    print(f"   Wrapper: ${wrapper_price}")
    print(f"   Direct: ${direct_price}")
```

---

## 🚨 **CRITICAL ISSUES IN CURRENT TEST SUITE**

### **Issue 1: Wrong Method Name**
```python
# ❌ CURRENT (WRONG):
calc = FoldedFlyersShopifyCalculator()
result = calc.calculate(**params)  # Method doesn't exist!

# ✅ CORRECT:
calc = FoldedFlyersShopifyCalculator()
result = calc.calculate_quote(**params)  # Correct method name
```

### **Issue 2: Missing Wrapper Tests**
Current test suite ONLY tests direct method, missing the wrapper layer entirely.

**Production Reality:**
- 90% of AI agent calls → WRAPPER method (`inhouse_calculate_quote`)
- 10% of AI agent calls → DIRECT method (schema-only mode)

**Current Test Coverage:**
- 0% wrapper method testing ❌
- 100% direct method testing (but wrong method name) ❌

### **Issue 3: Wrong Parameter Format**
```python
# ❌ CURRENT (WRONG):
result = calc.calculate(
    size="DL",           # String (needs enum)
    stock="Satin 128GSM", # String (needs enum)
    double_sided=True    # Bool (needs enum)
)

# ✅ CORRECT (Direct method):
result = calc.calculate_quote(
    finish_size=FinishSize.DL,        # Enum
    paper_stock=PaperStock.SATIN_128GSM,  # Enum
    print_sides=PrintSides.DOUBLE_SIDE    # Enum
)
```

### **Issue 4: No Validation Testing**
Current test suite doesn't test the validation layer that:
- Catches missing parameters
- Returns structured error messages
- Teaches AI valid parameter values
- Ensures backwards compatibility

---

## ✅ **REQUIRED TEST SUITE STRUCTURE**

```
test_comprehensive_calculator_suite.py
├── Imports (BOTH wrapper and backend)
│   ├── calculator_wrapper functions (WRAPPER)
│   └── Backend calculator classes + Enums (DIRECT)
│
├── For Each Calculator:
│   ├── WRAPPER METHOD TESTS
│   │   ├── Test 1: New parameters work
│   │   ├── Test 2: Legacy parameters work with warnings
│   │   ├── Test 3: Price consistency (new = legacy)
│   │   └── Test 4: Missing params validation (CRITICAL!)
│   │
│   └── DIRECT METHOD TESTS
│       ├── Test 5: Direct backend call with enums
│       ├── Test 6: Wrapper vs direct consistency
│       └── Test 7: Direct missing params handling
│
└── Summary Report
    ├── Wrapper tests: X/Y passed
    ├── Direct tests: X/Y passed
    ├── Price consistency: X/Y matched
    └── Validation: X/Y caught errors
```

---

## 📊 **EXPECTED OUTPUT FORMAT**

```
================================================================================
COMPREHENSIVE CALCULATOR TEST SUITE - DUAL METHOD
January 23, 2026
================================================================================

Testing: FOLDED FLYERS CALCULATOR

==============================================================================
METHOD 1: WRAPPER (Tool Registry - Production Primary)
==============================================================================

[Test 1: New Parameters]
✅ SUCCESS
   Price: $235.90
   Warnings: 0

[Test 2: Legacy Parameters]
⚠️  DEPRECATED PARAMETERS DETECTED:
   colour=True → print_type='Colour'
   cellophane='None' → celloglaze='None'

✅ SUCCESS
   Price: $235.90
   Warnings: 2

[Test 3: Price Consistency]
💰 PASSED
   New params: $235.90
   Legacy params: $235.90

[Test 4: Missing Parameter Validation]
❌ CORRECTLY REJECTED
   Error: "Invalid size: 'None'. Must be one of: DL, A5, A4, A3, 6pp A4"

==============================================================================
METHOD 2: DIRECT (Backend Class - Alternative Path)
==============================================================================

[Test 5: Direct Backend Call]
✅ SUCCESS
   Price: $235.90
   Method: calculate_quote() with Enums

[Test 6: Wrapper vs Direct Consistency]
🔀 PASSED
   Wrapper: $235.90
   Direct: $235.90

[Test 7: Direct Missing Params]
❌ CORRECTLY REJECTED
   Error: TypeError (enum validation at backend)

==============================================================================
SUMMARY - FOLDED FLYERS CALCULATOR
==============================================================================

Wrapper Method: 4/4 tests passed ✅
Direct Method: 3/3 tests passed ✅
Price Consistency: 100% match ✅
Validation: Working correctly ✅

Overall: PASSING ✅
```

---

## 🎯 **FINAL CHECKLIST**

### **Before Implementation:**
- [ ] Read CALCULATOR_ALIGNMENT_INSTRUCTIONS.md (Part 3 validation)
- [ ] Read CALCULATOR_TESTING_GUIDE.md (4 required tests)
- [ ] Read VALIDATION_COMPLETE_JAN19_2026.md (AI learning examples)
- [ ] Understand why BOTH methods must be tested

### **During Implementation:**
- [ ] Import BOTH wrapper functions AND backend classes
- [ ] Test wrapper method (4 tests per calculator)
- [ ] Test direct method (3 tests per calculator)
- [ ] Verify price consistency across all methods
- [ ] Test validation catches missing/invalid params

### **After Implementation:**
- [ ] All wrapper tests passing
- [ ] All direct tests passing
- [ ] Prices match across wrapper/direct/legacy
- [ ] Validation returns structured errors
- [ ] AI can learn from error messages

---

## 💡 **KEY INSIGHTS**

1. **Wrapper ≠ Unnecessary Overhead**
   - Provides parameter translation (strings → enums)
   - Handles legacy parameter support
   - Returns structured validation errors
   - Teaches AI valid parameter values

2. **Direct Method ≠ Simpler**
   - Requires enum imports
   - Requires exact backend method names
   - No automatic validation
   - Raw backend errors (less helpful for AI)

3. **Both Methods Required**
   - AI agents use BOTH in production
   - Wrapper = primary path (90%)
   - Direct = schema-only mode (10%)
   - Testing only one = incomplete coverage

4. **Validation is Key**
   - Missing in original 27 calculators
   - Added Jan 19, 2026 (VALIDATION_COMPLETE doc)
   - Enables AI learning through structured errors
   - Critical for production reliability

---

**END OF REQUIREMENTS DOCUMENT**
