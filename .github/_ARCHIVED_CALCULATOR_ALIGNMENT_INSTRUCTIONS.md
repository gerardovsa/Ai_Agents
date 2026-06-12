# Calculator Schema-Wrapper-Backend Alignment Instructions
**Date:** January 19, 2026  
**Last Updated:** January 19, 2026
**Objective:** Align tool schemas with backend calculators while maintaining backwards compatibility

---

## 🚨 CRITICAL: WORK ONE CALCULATOR AT A TIME

**⚠️ DO NOT EDIT MULTIPLE CALCULATORS IN BULK ⚠️**

**Why Individual Processing is Required:**
1. Each calculator has unique parameter requirements
2. Backend signatures vary significantly
3. Legacy parameter translations are calculator-specific
4. Testing must validate specific calculator behavior
5. Rollback easier with individual commits
6. Prevents copy-paste errors across calculators

**Process:**
- ✅ Pick ONE calculator
- ✅ Complete ALL 7 steps for that calculator
- ✅ Verify ALL tests passing
- ✅ Make ONE git commit
- ✅ THEN move to next calculator

---

## 📊 THE 3-PART PATTERN (ALL PARTS REQUIRED)

### **Part 1: Remove **kwargs ✅**
```python
# ❌ BAD (catches errors silently):
def calculate_product_shopify(quantity, **kwargs):

# ✅ GOOD (explicit parameters only):
def calculate_product_shopify(quantity, param1=None, param2=None):
```

### **Part 2: Use None Defaults (Not Arbitrary Defaults) ✅**
```python
# ❌ BAD (arbitrary defaults mask missing params):
def calculate_product_shopify(
    print_type: str = "Colour",      # Bad: can't tell if provided
    paper_stock: str = "Satin 350GSM"  # Bad: arbitrary default
):

# ✅ GOOD (None allows validation):
def calculate_product_shopify(
    print_type: str = None,          # Good: can validate
    paper_stock: str = None,         # Good: can check if provided
    legacy_colour: bool = None       # Legacy for compatibility
):
```

### **Part 3: Validate After Legacy Translation ✅ (MOST IMPORTANT)**
```python
def calculate_product_shopify(
    quantity: int,
    print_type: str = None,
    legacy_colour: bool = None
):
    warnings = []
    
    # Step 1: TRANSLATE LEGACY PARAMS FIRST
    if legacy_colour is not None:
        print_type = "Colour" if legacy_colour else "Black & White"
        warnings.append({
            "deprecated": "legacy_colour",
            "use_instead": "print_type",
            "translated_to": print_type
        })
    
    # Step 2: VALIDATE AFTER TRANSLATION (CRITICAL!)
    # This is what's missing from all 27 calculators!
    if print_type is None:
        return {
            "success": False,
            "error": "Missing required parameter: 'print_type' (or legacy 'legacy_colour')"
        }
    
    # Step 3: Safe to call backend now
    result = calculator.calculate(print_type=print_type)
    
    response = {"success": True, "total_price": result.total_price}
    if warnings:
        response["warnings"] = warnings
    
    return response
```

---

## 🎯 MISSION

Fix parameter misalignment between:
1. **Tool Schema** (JSON) - What AI agents see
2. **Wrapper Function** (Python) - Translation layer
3. **Backend Calculator** (Python) - Source of truth (IMMUTABLE)

---

## 🔒 CRITICAL RULES

### **DO NOT TOUCH:**
- ❌ Backend calculator logic (`UI/modules_external/quote-calculator/backend/shopify_calculators/*.py`)
- ❌ Pricing calculations
- ❌ Enum definitions in backend
- ❌ Backend `calculate()` or `calculate_quote()` method signatures

### **DO NOT ADD:**
- ❌ Parameters that don't exist in backend code
- ❌ Parameters from other calculators
- ❌ Parameters you think should be there but aren't
- ❌ **ONLY wrapper parameters that backend actually uses!**

### **SAFE TO MODIFY:**
- ✅ Tool schemas (`tools/schemas/ARCHIVE/calculator_tools.json`)
- ✅ Wrapper functions (`UI/modules_external/quote-calculator/implementations/calculator_wrapper.py`)
- ✅ Parameter names and types in wrappers (ONLY if backend uses them)
- ✅ Add legacy parameter support (ONLY for params backend actually uses)

---

## 📋 PROCESS FOR EACH CALCULATOR

### **STEP 1: ANALYZE BACKEND (Source of Truth)**

**🚨 ABSOLUTE RULE: ONLY USE PARAMETERS THAT EXIST IN BACKEND CODE 🚨**

**File:** `UI/modules_external/quote-calculator/backend/shopify_calculators/<Calculator>_Shopify_Calculator.py`

**Find the main calculation method:**
```python
def calculate(self, **kwargs) -> ResultType:
    quantity = int(kwargs.get('quantity', 50))
    param1 = kwargs.get('param1', 'default')
    param2 = kwargs.get('param2', 100)
```

**HOW TO VERIFY PARAMETERS (MANDATORY PROCESS):**

1. **Open the backend calculator file**
2. **Find ALL `kwargs.get()` calls in the calculate() method**
3. **List EVERY parameter name from kwargs.get('parameter_name', default)**
4. **STOP - Do NOT add any other parameters!**

**Example Verification:**
```python
# Backend code (lines 65-85):
quantity = int(kwargs.get('quantity', kwargs.get('qty', 50)))   # ✅ quantity
size = kwargs.get('size', '600x450')                            # ✅ size  
material = kwargs.get('material', 'Corflute')                   # ✅ material
sides = kwargs.get('sides', 'Single')                           # ✅ sides
artworks = int(kwargs.get('artworks', 1))                       # ✅ artworks

# ONLY these 5 parameters should be in wrapper!
# If you don't see kwargs.get('parameter'), DON'T add it!
```

**Extract ONLY parameters that backend actually uses:**
1. **Required parameters** (no default value in kwargs.get)
2. **Optional parameters** (has default value in kwargs.get)
3. **Parameter types** (int, str, bool, Enum)
4. **Parameter names** (exact spelling from backend)
5. **Enum values** (if applicable)
6. **Default values** (what backend uses if not provided)

**❌ NEVER DO THESE THINGS:**
- ❌ Add `artworks` if backend doesn't have `kwargs.get('artworks')`
- ❌ Add `material` if backend doesn't have `kwargs.get('material')`
- ❌ Add `sides` if backend doesn't have `kwargs.get('sides')`
- ❌ Copy parameters from other calculators
- ❌ Assume parameters exist - VERIFY in backend code!
- ❌ Add parameters that "make sense" but aren't in backend

**✅ VERIFICATION CHECKLIST:**
- [ ] Found calculate() method in backend file
- [ ] Listed ALL kwargs.get() calls (line by line)
- [ ] Counted total parameters from backend (e.g., 5 parameters)
- [ ] Documented exact line numbers where parameters found
- [ ] CONFIRMED no extra parameters being added

**Document in format:**
```
BACKEND SIGNATURE (from actual code lines 65-85):
✅ quantity: int (line 65: kwargs.get('quantity', kwargs.get('qty', 50)))
✅ size: str (line 70: kwargs.get('size', '600x450'))
✅ material: str (line 71: kwargs.get('material', 'Corflute'))
✅ sides: str (line 72: kwargs.get('sides', 'Single'))
✅ artworks: int (line 75: kwargs.get('artworks', 1))

TOTAL: 5 parameters found in backend
VERIFIED: All parameters exist in backend code
```

---

### **STEP 2: ANALYZE CURRENT WRAPPER**

**File:** `UI/modules_external/quote-calculator/implementations/calculator_wrapper.py`

**Find wrapper function:**
```python
def calculate_<product>_shopify(param1, param2, **kwargs):
```

**Extract:**
1. Current parameter names
2. Current parameter types
3. Default values
4. Presence of `**kwargs` (PROBLEM!)
5. Translation logic (e.g., `bool` → `str`)

**Document misalignments:**
```
WRAPPER VS BACKEND MISMATCHES:
❌ Wrapper has: double_sided (bool)
   Backend expects: print_sides (str)
   
❌ Wrapper has: cellophane (str)
   Backend expects: celloglaze (str)
   
⚠️ Wrapper has: **kwargs (silently catches wrong params)
```

---

### **STEP 3: ANALYZE CURRENT SCHEMA**

**File:** `tools/schemas/ARCHIVE/calculator_tools.json`

**Find schema definition:**
```json
{
  "name": "calculate_<product>_shopify",
  "parameters": {
    "param1": {"type": "...", "enum": [...]}
  }
}
```

**Extract:**
1. Parameter names in schema
2. Parameter types
3. Enum values
4. Descriptions

**Document misalignments:**
```
SCHEMA VS BACKEND MISMATCHES:
❌ Schema has: colour (boolean)
   Backend expects: print_type (string)
   
❌ Schema has: fold_type (string)
   Backend expects: folding (string)
   
❌ Schema missing: artworks (integer)
```

---

### **STEP 4: CREATE ALIGNMENT PLAN**

**Document the complete alignment:**

```markdown
## Calculator: <Product Name>

### Current Misalignments:
1. Schema param `X` (type) → Wrapper param `Y` (type) → Backend param `Z` (type)
2. Schema missing param `A` that backend requires
3. Wrapper has `**kwargs` catching errors silently

### Fix Strategy:

#### Schema Changes (tools/schemas/ARCHIVE/calculator_tools.json):
- Rename: `cellophane` → `celloglaze`
- Change type: `colour` (bool) → `print_type` (string with enum)
- Add missing: `artworks` (integer, default: 1)
- Update enums: ["Colour", "Black & White"]

#### Wrapper Changes (calculator_wrapper.py):
- Remove: `**kwargs`
- Add: Legacy parameter support (deprecated warnings)
- Keep: Translation logic for backwards compatibility
- Add: `@calculator_wrapper(validate_params=True)` decorator
```

---

### **STEP 5: IMPLEMENT SCHEMA FIX**

**Update `tools/schemas/ARCHIVE/calculator_tools.json`:**

```json
{
  "name": "calculate_<product>_shopify",
  "parameters": {
    "quantity": {
      "type": "integer",
      "description": "Number of items (REQUIRED)",
      "enum": [100, 250, 500, 1000, 2000, 5000, 10000]
    },
    "print_sides": {
      "type": "string",
      "description": "EXACT string required: 'Single side print' or 'Double side print'",
      "enum": ["Single side print", "Double side print"],
      "required": false
    },
    "print_type": {
      "type": "string",
      "description": "Print color mode (use EXACT strings)",
      "enum": ["Colour", "Black & White"],
      "required": false
    }
  }
}
```

**Rules:**
- Use EXACT backend parameter names
- Use EXACT backend enum values (including capitalization)
- Mark required params correctly
- Document EXACT string formats needed

---

### **STEP 6: IMPLEMENT WRAPPER FIX + VALIDATION (CRITICAL!)**

**⚠️ THIS IS THE MISSING PIECE IN ALL 27 CALCULATORS ⚠️**

**Update `calculator_wrapper.py`:**

```python
@calculator_wrapper(quantity_enum=[100, 250, 500, 1000, 2000, 5000, 10000], validate_params=True)
def calculate_<product>_shopify(
    # ✅ PRIMARY PARAMETERS (match backend exactly)
    quantity: int,
    print_sides: str = "Double side print",  # ✅ BACKEND NAME
    print_type: str = "Colour",              # ✅ BACKEND NAME
    celloglaze: str = "None",                # ✅ BACKEND NAME
    artworks: int = 1,                       # ✅ BACKEND NAME
    
    # ⚠️ DEPRECATED LEGACY PARAMETERS (backwards compatibility)
    double_sided: bool = None,               # OLD NAME - will warn
    colour: bool = None,                     # OLD NAME - will warn
    cellophane: str = None                   # OLD NAME - will warn
    
    # ❌ REMOVE **kwargs COMPLETELY!
) -> Dict[str, Any]:
    """
    Calculator for <Product>
    
    ✅ CURRENT PARAMETERS (matches backend):
        print_sides: "Single side print" or "Double side print"
        print_type: "Colour" or "Black & White"
        celloglaze: "None", "1 Side Gloss", "2 Side Gloss", "1 Side Matt", "2 Side Matt"
        artworks: Number of artwork designs (1-50)
    
    ⚠️ DEPRECATED PARAMETERS (legacy support with warnings):
        double_sided (bool) → use print_sides instead
        colour (bool) → use print_type instead
        cellophane (str) → use celloglaze instead
    """
    
    # 🔄 LEGACY TRANSLATION WITH WARNINGS
    warnings = []
    
    if double_sided is not None:
        print_sides = "Double side print" if double_sided else "Single side print"
        warnings.append({
            "deprecated": "double_sided",
            "use_instead": "print_sides",
            "value_sent": double_sided,
            "translated_to": print_sides
        })
    
    if colour is not None:
        print_type = "Colour" if colour else "Black & White"
        warnings.append({
            "deprecated": "colour",
            "use_instead": "print_type",
            "value_sent": colour,
            "translated_to": print_type
        })
    
    if cellophane is not None:
        celloglaze = cellophane
        warnings.append({
            "deprecated": "cellophane",
            "use_instead": "celloglaze",
            "value_sent": cellophane,
            "translated_to": celloglaze
        })
    
    # 📢 LOG WARNINGS
    if warnings:
        log_msg = f"\n⚠️  DEPRECATED PARAMETERS in calculate_<product>_shopify:\n"
        for w in warnings:
            log_msg += f"   {w['deprecated']}={w['value_sent']} → {w['use_instead']}='{w['translated_to']}'\n"
        print(log_msg)
    
    # ✅ VALIDATION (AFTER LEGACY TRANSLATION - CRITICAL!)
    # This validation block is MISSING from all 27 calculators!
    if print_type is None:
        return {
            "success": False,
            "error": "Missing required parameter: 'print_type' (or legacy 'colour')"
        }
    
    if celloglaze is None:
        return {
            "success": False,
            "error": "Missing required parameter: 'celloglaze' (or legacy 'cellophane')"
        }
    
    # Add validation for ALL required parameters
    # Check AFTER legacy translation so both paths are validated
    
    # ✅ CALL BACKEND (now with correct params AND validated)
    try:
        calculator = <Product>ShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            print_sides=print_sides,     # ✅ EXACT BACKEND NAME
            print_type=print_type,       # ✅ EXACT BACKEND NAME
            celloglaze=celloglaze,       # ✅ EXACT BACKEND NAME
            artworks=artworks            # ✅ EXACT BACKEND NAME
        )
        
        response = {
            "success": True,
            "total_price": float(result.total_price),
            "specifications": result.specifications
        }
        
        if warnings:
            response["warnings"] = warnings
            
        return response
        
    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

### **STEP 7: CREATE VALIDATION TESTS**

**Create test file:** `tests/calculator_<product>_alignment_tests.py`

```python
import pytest
from UI.modules_external.quote_calculator.implementations.calculator_wrapper import calculate_<product>_shopify

class TestCalculator<Product>Alignment:
    """Test schema-wrapper-backend alignment for <Product>"""
    
    def test_1_new_params_correct_names(self):
        """Test using NEW correct parameter names"""
        result = calculate_<product>_shopify(
            quantity=1000,
            print_sides="Double side print",  # ✅ CORRECT NAME
            print_type="Colour",              # ✅ CORRECT NAME
            celloglaze="2 Side Matt"          # ✅ CORRECT NAME
        )
        assert result["success"] == True
        assert "warnings" not in result  # No warnings for correct params
        assert result["total_price"] > 0
    
    def test_2_legacy_params_with_warnings(self):
        """Test using OLD deprecated parameter names"""
        result = calculate_<product>_shopify(
            quantity=1000,
            double_sided=True,    # ⚠️ DEPRECATED
            colour=True,          # ⚠️ DEPRECATED
            cellophane="Matt"     # ⚠️ DEPRECATED
        )
        assert result["success"] == True
        assert "warnings" in result  # Should have warnings
        assert len(result["warnings"]) == 3  # All 3 deprecated params
        assert result["total_price"] > 0
    
    def test_3_unknown_param_rejected(self):
        """Test that unknown parameters are rejected"""
        result = calculate_<product>_shopify(
            quantity=1000,
            invalid_param="test"  # ❌ UNKNOWN
        )
        assert result["success"] == False
        assert "unknown_parameters" in result
        assert "invalid_param" in result["unknown_parameters"]
    
    def test_4_quantity_enum_validation(self):
        """Test quantity enum validation"""
        result = calculate_<product>_shopify(
            quantity=999  # ❌ NOT IN ENUM
        )
        assert result["success"] == False
        assert "quantity" in result["error"].lower()
    
    def test_5_enum_values_match_backend(self):
        """Test that enum values work exactly as backend expects"""
        # Test all print_type enum values
        for print_type in ["Colour", "Black & White"]:
            result = calculate_<product>_shopify(
                quantity=500,
                print_type=print_type
            )
            assert result["success"] == True
        
        # Test all print_sides enum values
        for print_sides in ["Single side print", "Double side print"]:
            result = calculate_<product>_shopify(
                quantity=500,
                print_sides=print_sides
            )
            assert result["success"] == True
```

**Run tests:**
```bash
pytest tests/calculator_<product>_alignment_tests.py -v
```

**Expected output:**
```
test_1_new_params_correct_names PASSED
test_2_legacy_params_with_warnings PASSED
test_3_unknown_param_rejected PASSED
test_4_quantity_enum_validation PASSED
test_5_enum_values_match_backend PASSED
```

---

## 📊 DOCUMENTATION TEMPLATE

**For each calculator, create:**

### `CALCULATOR_<PRODUCT>_ALIGNMENT.md`

```markdown
# <Product> Calculator Alignment Report
Date: January 19, 2026

## Backend Analysis
**File:** `backend/shopify_calculators/<Product>_Shopify_Calculator.py`

**Method Signature:**
```python
def calculate(
    quantity: int,
    print_sides: str = "Double side print",
    print_type: str = "Colour",
    celloglaze: str = "None",
    artworks: int = 1
) -> <Product>QuoteResult:
```

**Required Parameters:** quantity  
**Optional Parameters:** print_sides, print_type, celloglaze, artworks

## Schema Changes Made
**File:** `tools/schemas/ARCHIVE/calculator_tools.json`

| Old Parameter | New Parameter | Type Change | Reason |
|---------------|---------------|-------------|--------|
| `cellophane` | `celloglaze` | No change | Backend uses `celloglaze` |
| `colour` (bool) | `print_type` (str) | Yes | Backend expects string enum |
| `fold_type` | `folding` | No change | Backend uses `folding` |
| N/A | `artworks` | Added | Missing from schema |

## Wrapper Changes Made
**File:** `UI/modules_external/quote-calculator/implementations/calculator_wrapper.py`

1. ✅ Removed `**kwargs`
2. ✅ Added `@calculator_wrapper(validate_params=True)` decorator
3. ✅ Renamed parameters to match backend exactly
4. ✅ Added legacy parameter support (double_sided, colour, cellophane)
5. ✅ Added deprecation warnings for legacy params

## Test Results
```
✅ test_1_new_params_correct_names - PASSED
✅ test_2_legacy_params_with_warnings - PASSED
✅ test_3_unknown_param_rejected - PASSED
✅ test_4_quantity_enum_validation - PASSED
✅ test_5_enum_values_match_backend - PASSED

5/5 tests passed (100%)
```

## Example Usage

### ✅ CORRECT (New parameters):
```python
calculate_<product>_shopify(
    quantity=1000,
    print_sides="Double side print",
    print_type="Colour",
    celloglaze="2 Side Matt",
    artworks=1
)
```

### ⚠️ DEPRECATED (Still works with warnings):
```python
calculate_<product>_shopify(
    quantity=1000,
    double_sided=True,
    colour=True,
    cellophane="Matt"
)
```
```

---

## 🎯 CALCULATOR GROUPS

### **GROUP 1: Business Cards & Simple Products**
1. `calculate_economical_business_cards_shopify`
2. `calculate_premium_business_cards_shopify`
3. `calculate_folded_flyers_shopify`
4. `calculate_printed_letterheads_shopify`
5. `calculate_with_compliments_slips_shopify`

### **GROUP 2: Bound Books**
1. `calculate_wire_bound_books_shopify`
2. `calculate_spiral_bound_books_shopify`
3. `calculate_perfect_bound_books_shopify`
4. `calculate_saddle_stitch_books_shopify`
5. `calculate_spiral_books_simple_shopify`

### **GROUP 3: Notepads & Stationery**
1. `calculate_notepads_a4_shopify`
2. `calculate_notepads_a5_shopify`
3. `calculate_notepads_a6_shopify`
4. `calculate_custom_poster_printing_shopify`
5. `calculate_custom_vinyl_stickers_shopify`

### **GROUP 4: Signs & Displays**
1. `calculate_election_signs_shopify`
2. `calculate_construction_signs_shopify`
3. `calculate_bollard_signs_shopify`
4. `calculate_corflute_insert_a_frame_shopify`
5. `calculate_metal_face_a_frame_shopify`

### **GROUP 5: Promotional Products**
1. `calculate_luxury_classic_pull_up_banners_shopify`
2. `calculate_selfie_frames_shopify`
3. `calculate_stackable_cubes_shopify`
4. `calculate_strut_cards_a3_shopify`
5. `calculate_strut_cards_a4_shopify`

### **GROUP 6: Specialty Items**
1. `calculate_premium_bookmarks_shopify`
2. `calculate_corflute_signs_shopify` (original corflute)
3. Any remaining calculators...

---

## ✅ COMPLETION CHECKLIST (Per Calculator)

- [ ] Backend signature documented
- [ ] Current wrapper analyzed
- [ ] Current schema analyzed
- [ ] Misalignments documented
- [ ] Schema updated to match backend
- [ ] Wrapper updated with new params
- [ ] Legacy params added with warnings
- [ ] `**kwargs` removed
- [ ] Validation decorator added
- [ ] 5 test cases created
- [ ] All tests passing
- [ ] Alignment report created
- [ ] Changes committed to git

---

## 📝 DELIVERABLE FORMAT

For each calculator group, provide:

1. **Analysis Document:** `CALCULATOR_GROUP_<N>_ANALYSIS.md`
2. **Test File:** `tests/calculator_group_<N>_tests.py`
3. **Test Results:** All tests passing (25/25 for 5 calculators)
4. **Git Branch:** `fix/calculator-alignment-group-<N>`
5. **Summary Report:** Changes made, issues found, tests results

---

## 🚨 ERROR HANDLING

If you encounter:

**Backend uses `**kwargs`:**
- Document all parameters from backend docstring
- Check JSON config files for enum values
- Use parameter names from docstring as source of truth

**No clear backend signature:**
- Check parent class methods
- Look for JSON schema files in `backend/configs/` or `backend/schema/`
- Examine test files if they exist

**Enum values unclear:**
- Check backend code for string literals
- Look for validation logic in backend
- Test with common values and document what works

**Complex parameter translations:**
- Document the translation logic clearly
- Keep translation in wrapper, not schema
- Test both direct and translated paths

---

## 💾 COMMIT MESSAGE FORMAT

```
fix(calculators): align <product> schema/wrapper with backend

- Remove **kwargs from wrapper
- Add parameter validation decorator
- Rename cellophane → celloglaze to match backend
- Change colour (bool) → print_type (str) to match backend
- Add artworks parameter (was missing from schema)
- Add legacy parameter support with deprecation warnings
- Add 5 validation tests (all passing)

Fixes parameter misalignment that caused silent failures.
Backend signature now matches schema exactly.
Legacy params still work with warnings for backwards compatibility.

Tests: 5/5 passing
```

---

**END OF INSTRUCTIONS**
