# Group 1 vs Group 2 Pattern Comparison
**Date:** January 19, 2026

## 🎯 Summary

**Group 2 Pattern (CORRECT):** ✅  
- Parameters use `= None` for required params
- Explicit validation after legacy translation
- Clear error messages

**Group 1 Pattern (INCONSISTENT):** ⚠️  
- Mix of required params and defaults  
- No validation for missing params
- Some calculators missing parameters entirely

---

## 📊 Detailed Comparison

### **Group 2 (Wire/Spiral/Perfect Bound) - PROPER PATTERN:**

```python
def calculate_spiral_bound_books_shopify(
    quantity: int,
    internal_pages: int = None,     # ✅ Required but optional (for legacy)
    finish_size: str = None,        # ✅ Required but optional (for legacy)
    # ... other params ...
    pages: int = None,              # Legacy
    size: str = None                # Legacy
):
    warnings = []
    
    # 1. TRANSLATE LEGACY FIRST
    if pages is not None:
        internal_pages = pages
        warnings.append({...})
    
    # 2. VALIDATE AFTER TRANSLATION
    if internal_pages is None:
        return {"success": False, "error": "Missing required parameter: 'internal_pages' (or legacy 'pages')"}
    
    # 3. BACKEND CALL
    result = calculator.calculate(internal_pages=internal_pages, ...)
```

### **Group 1 (Folded Flyers) - INCONSISTENT PATTERN:**

```python
def calculate_folded_flyers_shopify(
    quantity: int,
    size: str,                     # ❌ REQUIRED - no default, no validation
    stock: str,                    # ❌ REQUIRED - no default, no validation
    double_sided: bool = True,
    print_type: str = "Colour",
    # ... legacy params ...
    colour: bool = None,
    fold_type: str = None
):
    warnings = []
    
    # Has translation but no validation
    if colour is not None:
        print_type = "Colour" if colour else "Black & White"
        warnings.append({...})
    
    # ❌ NO VALIDATION - just calls backend directly
    result = calculator.calculate(...)
```

### **Problems with Group 1 Pattern:**

1. **Folded Flyers:** `size` and `stock` are required but have no legacy translation or validation
2. **Economical Business Cards:** Missing `celloglaze` parameter entirely
3. **Premium Business Cards:** Has `double_sided` but backend expects `print_sides` directly
4. **All Group 1:** No validation for missing required parameters

---

## ✅ What Group 2 Does RIGHT:

1. **All parameters optional with None:** Allows legacy translation to work
2. **Explicit validation after translation:** Clear error messages
3. **Consistent pattern across all 5 calculators**
4. **No arbitrary defaults:** `None` means "not provided"
5. **Helpful error messages:** Mentions both new and legacy param names

---

## ❌ What Group 1 Needs Fixed:

### **Calculator 1: Folded Flyers**
- Make `size` and `stock` optional (`= None`)
- Add validation after legacy translation
- Add missing `size` legacy parameter support

### **Calculator 2: Economical Business Cards**
- Add `celloglaze` parameter (missing entirely!)
- Add validation for `print_type`
- Make parameters follow None pattern

### **Calculator 3: Premium Business Cards**
- Change `paper_stock` enum value format (backend rejects `satin_350gsm`)
- Add `finish_size` parameter
- Add validation

### **Calculator 4 & 5: Letterheads & Compliments**
- Add validation for required parameters
- Make all parameters consistent with Group 2 pattern

---

## 🎯 Action Plan

### **Option 1: Update Group 1 to Match Group 2** (RECOMMENDED)
- Apply Group 2 pattern to all Group 1 calculators
- Add None defaults + validation
- Test comprehensively
- **Time:** ~30 minutes
- **Result:** Consistent, validated, perfect

### **Option 2: Update Group 2 to Match Group 1**
- Remove validation from Group 2
- Use required parameters
- **Not recommended:** Loses validation benefits

---

## 📝 Recommended Pattern (From Group 2)

```python
@calculator_wrapper(quantity_enum=[...], validate_params=True)
def calculate_product(
    quantity: int,
    # REQUIRED PARAMETERS - Use None to allow legacy translation
    required_param1: str = None,
    required_param2: str = None,
    # OPTIONAL PARAMETERS - Use sensible defaults
    optional_param: str = "default_value",
    # LEGACY PARAMETERS - Explicit for backwards compatibility
    old_param1: str = None,
    old_param2: str = None
) -> Dict[str, Any]:
    \"\"\"Documentation...\"\"\"
    
    warnings = []
    
    # STEP 1: LEGACY TRANSLATION
    if old_param1 is not None:
        required_param1 = translate(old_param1)
        warnings.append({...})
    
    # STEP 2: VALIDATION
    if required_param1 is None:
        return {
            "success": False,
            "error": "Missing required parameter: 'required_param1' (or legacy 'old_param1')"
        }
    
    # STEP 3: BACKEND CALL
    result = calculator.calculate(
        required_param1=required_param1,
        required_param2=required_param2,
        ...
    )
    
    # STEP 4: RETURN WITH WARNINGS
    response = {"success": True, ...}
    if warnings:
        response["warnings"] = warnings
    return response
```

---

## 🎓 Key Lessons

1. **Don't use arbitrary defaults** - Use `None` for required params
2. **Validate AFTER translation** - Legacy params need to translate first
3. **Clear error messages** - Mention both new and legacy names
4. **Consistent patterns** - All calculators should work the same way
5. **Test validation** - Ensure missing params are caught properly

---

## 📊 Test Results

### Group 2: 5/5 ✅ (100%)
- All tests pass
- Validation working
- Legacy translation working
- Price consistency verified

### Group 1: 6/20 ⚠️ (30%)
- Validation missing
- Parameters inconsistent
- Some calculators incomplete

---

## 🚀 Next Steps

1. **Fix Group 1** to match Group 2 pattern
2. **Retest Group 1** with comprehensive tests
3. **Update documentation** to reflect proper pattern
4. **Move to Group 3** with correct pattern from start

---

**Conclusion:** Group 2 pattern is CORRECT. Group 1 needs to be updated to match.
