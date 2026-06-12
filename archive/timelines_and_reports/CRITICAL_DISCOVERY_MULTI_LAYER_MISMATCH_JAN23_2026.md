# CRITICAL DISCOVERY: Multi-Layer Format Mismatch - January 23, 2026

**Date:** January 23, 2026, 2:30 PM
**Severity:** 🚨 CRITICAL PRODUCTION ISSUE
**Scope:** 14+ Shopify calculators affected

---

## Executive Summary

**The audit revealed a MORE COMPLEX issue than wrapper validation mismatches:**

The system has **THREE LAYERS** with **DIFFERENT DATA FORMATS**:

1. **Shopify JSON Specifications** → Human-readable formats (`"3mm Corflute"`, `"270mm W x 1000mm H - Three Sided"`)
2. **Backend Calculators** → Simplified formats (`"Corflute"`, `"300x300"`)
3. **Wrapper Validators** → Match backend format (simplified)
4. **Tool Schemas** → Extract JSON format (human-readable)

**Result:** Schema provides JSON formats to AI → Backend expects simplified formats → **100% FAILURE RATE**

---

## The Real Problem

### Example: Bollard Signs

**Layer 1: JSON Specification (Shopify)**
```json
"Material": {
  "default": "5mm Corflute",
  "options": ["3mm Corflute", "5mm Corflute"]
},
"Size": {
  "default": "270mm W x 1000mm H - Three Sided",
  "options": [
    "270mm W x 1000mm H - Three Sided",
    "270mm W x 1200mm H - Three Sided",
    "270mm W x 1800mm H - Three Sided",
    "300mm W x 1000mm H - Three Sided",
    ... (12 total)
  ]
}
```

**Layer 2: Backend Calculator**
```python
def calculate(self, **kwargs):
    material = kwargs.get('material', 'Aluminium')  # ❌ Different default!
    size = kwargs.get('size', '300x300')            # ❌ Different format!
    
    # Parses size expecting "300x300" format:
    w_str, h_str = size.lower().split('x')
    width_mm = Decimal(w_str)
    height_mm = Decimal(h_str)
```

**Layer 3: Wrapper Validator**
```python
# Validates backend-compatible format
valid_sizes = ["300x300", "450x450", "600x600"]  # ❌ Matches backend, not JSON!
if material not in ["Aluminium", "Metal"]:        # ❌ Matches backend, not JSON!
    return {"success": False, "error": "..."}
```

**Layer 4: Tool Schema (AI Interface)**
```json
{
  "material": {
    "type": "string",
    "enum": ["3mm Corflute", "5mm Corflute"]  // ✅ Correct JSON extraction
  },
  "size": {
    "type": "string",
    "enum": [
      "270mm W x 1000mm H - Three Sided",
      "270mm W x 1200mm H - Three Sided",
      ... (all 12 JSON sizes)
    ]
  }
}
```

### What Happens:
1. AI agent reads schema → sees `["3mm Corflute", "5mm Corflute"]`
2. AI calls wrapper with `material="3mm Corflute"`
3. Wrapper validates against `["Aluminium", "Metal"]` → ❌ **REJECTED**
4. If wrapper passed through: Backend parses `size="270mm W x 1000mm H - Three Sided"` with `.split('x')` → ❌ **CRASH**

---

## Extent of the Problem

### Calculators with Multi-Layer Mismatches:

**🚨 CRITICAL (Complete Format Incompatibility):**
1. **bollard_signs** - Material + Size format mismatch
2. **construction_signs** - Size format + multiple missing fields
3. **election_signs** - Size format + multiple missing fields
4. **stackable_cubes** - Material format mismatch

**⚠️ HIGH (Missing Field Translation):**
5. **custom_vinyl_stickers** - Backend uses simplified API (4 params vs 10 JSON fields)
6. **premium_bookmarks** - Backend uses simplified API
7. **luxury_pull_up_banners** - Missing field validation
8. **corflute_insert_a_frame** - Size format mismatch
9. **metal_face_a_frame** - Size format mismatch
10. **selfie_frames** - Missing field validation
11. **custom_poster_printing** - Missing field validation
12. **notepads_a4** - Print type format mismatch

**🔶 MEDIUM (Partial Field Coverage):**
13. **printed_letterheads** - Quantity + stock missing validation
14. **with_compliments_slips** - Quantity + stock missing validation

### Even "Aligned" Calculators Have Format Issues:

**Strut Cards A3/A4 (previously marked "aligned"):**
- JSON: `"A3 - 297mm x 420mm"`
- Backend: `"297x420"`
- Wrapper: `["297x420", "420x297"]`
- **Works by accident** because backend has flexible parsing, but schema still gives wrong format to AI!

---

## Root Cause Analysis

### Why This Happened:

1. **Shopify JSON files** were created with human-readable product specifications
   - Example: `"3mm Corflute"` (clear for customers)
   - Example: `"270mm W x 1000mm H - Three Sided"` (descriptive)

2. **Backend calculators** were developed independently with simplified parsing
   - Used machine-friendly formats: `"Corflute"`, `"300x300"`
   - Hardcoded cost models instead of using JSON field details
   - No format translation layer

3. **Wrappers** were created to match backend expectations
   - Validated simplified formats backend could parse
   - Acted as "protection layer" preventing backend crashes
   - But incompatible with JSON/Schema formats

4. **Schemas** were auto-generated from JSON files
   - Correctly extracted human-readable JSON values
   - No awareness of backend format requirements
   - Gave AI wrong format expectations

5. **No Integration Testing**
   - No tests verifying schema values work with backend
   - No tests verifying JSON → Backend translation
   - Each layer tested independently

---

## Impact Assessment

### Current State:
- **AI Agents:** See schema with JSON formats
- **AI Calls:** Use JSON format values (e.g., `"3mm Corflute"`)
- **Wrapper:** Rejects JSON formats (expects backend formats)
- **Result:** ❌ **100% FAILURE RATE** for affected calculators

### Production Consequences:
1. **14 calculators completely non-functional** for AI agents
2. **Customers cannot get quotes** for these products via AI
3. **No error visibility** - silent failures in production
4. **Manual intervention required** for every quote request

---

## Solution Architecture

### Three Possible Approaches:

### Option A: Add Format Translation Layer (RECOMMENDED)
**Location:** Between wrapper validation and backend call
**Complexity:** Medium
**Impact:** Least disruptive

```python
def translate_shopify_to_backend(field_name, shopify_value):
    """Translate Shopify JSON format to backend-compatible format"""
    
    # Material translations
    if field_name == 'material':
        mapping = {
            '3mm Corflute': 'Corflute',
            '5mm Corflute': 'Corflute',
            'Aluminium': 'Aluminium',
            'Metal': 'Metal'
        }
        return mapping.get(shopify_value, shopify_value)
    
    # Size translations
    if field_name == 'size':
        # Extract dimensions from descriptive format
        # "270mm W x 1000mm H - Three Sided" → "270x1000"
        match = re.search(r'(\d+)mm W x (\d+)mm H', shopify_value)
        if match:
            return f"{match.group(1)}x{match.group(2)}"
        return shopify_value
    
    return shopify_value

# In wrapper:
translated_material = translate_shopify_to_backend('material', material)
translated_size = translate_shopify_to_backend('size', size)

result = calculator.calculate(
    material=translated_material,
    size=translated_size,
    ...
)
```

**Pros:**
- ✅ Minimal changes to existing code
- ✅ Preserves working calculators
- ✅ Clear separation of concerns
- ✅ Easy to test

**Cons:**
- ⚠️ Adds complexity
- ⚠️ Need to maintain translation mappings

---

### Option B: Fix Backend Calculators
**Location:** Backend calculate() methods
**Complexity:** High
**Impact:** Most disruptive

```python
def calculate(self, **kwargs):
    material_raw = kwargs.get('material', '5mm Corflute')
    
    # Parse Shopify format
    if 'Corflute' in material_raw:
        thickness = '3mm' if '3mm' in material_raw else '5mm'
        material = 'Corflute'
    elif material_raw in ['Aluminium', 'Metal']:
        material = material_raw
    
    size_raw = kwargs.get('size', '270mm W x 1000mm H - Three Sided')
    
    # Parse Shopify descriptive format
    match = re.search(r'(\d+)mm W x (\d+)mm H', size_raw)
    if match:
        width_mm = Decimal(match.group(1))
        height_mm = Decimal(match.group(2))
    else:
        # Fallback: try simple "300x300" format
        w_str, h_str = size_raw.split('x')
        width_mm = Decimal(w_str)
        height_mm = Decimal(h_str)
```

**Pros:**
- ✅ Single source of truth (JSON)
- ✅ Backend handles both formats
- ✅ No translation layer needed

**Cons:**
- ❌ High risk of breaking working calculators
- ❌ Need to update 20+ backend files
- ❌ Complex regex parsing in every calculator
- ❌ Extensive regression testing required

---

### Option C: Fix Schemas to Match Backend
**Location:** Schema generation / Tool definitions
**Complexity:** Low
**Impact:** Wrong approach - loses JSON accuracy

```json
{
  "material": {
    "type": "string",
    "enum": ["Corflute", "Aluminium", "Metal"]  // ❌ Not accurate to JSON
  },
  "size": {
    "type": "string",
    "enum": ["300x300", "450x450", "600x600"]   // ❌ Not accurate to JSON
  }
}
```

**Pros:**
- ✅ Quick fix
- ✅ Minimal code changes

**Cons:**
- ❌ Loses JSON specification accuracy
- ❌ AI gets wrong information about product options
- ❌ Customers see different options in Shopify vs AI
- ❌ Future JSON changes won't propagate
- ❌ Not solving root problem, just hiding it

---

## Recommended Solution: Option A (Translation Layer)

### Implementation Plan:

**Phase 1: Create Translation Module (30 minutes)**
```python
# File: UI/modules_external/quote-calculator/implementations/format_translator.py

MATERIAL_TRANSLATIONS = {
    # Shopify JSON → Backend format
    '3mm Corflute': 'Corflute',
    '5mm Corflute': 'Corflute',
    '3mm': 'Corflute',
    '5mm': 'Corflute',
    'Aluminium': 'Aluminium',
    'Metal': 'Metal',
    'Standard (Monomeric)': 'mono',
    'Premium (Polymeric)': 'poly',
    ... (all material mappings)
}

def translate_size_format(shopify_size: str) -> str:
    """
    Translate Shopify descriptive size to backend WxH format
    
    Examples:
        "270mm W x 1000mm H - Three Sided" → "270x1000"
        "A3 - 297mm x 420mm" → "297x420"
        "300x300" → "300x300" (already correct)
    """
    # Try descriptive format with units
    match = re.search(r'(\d+)mm\s*W?\s*x\s*(\d+)mm\s*H?', shopify_size, re.IGNORECASE)
    if match:
        return f"{match.group(1)}x{match.group(2)}"
    
    # Try simple WxH format (already compatible)
    if re.match(r'\d+x\d+$', shopify_size):
        return shopify_size
    
    # Try format with labels "A3 - 297mm x 420mm"
    match = re.search(r'(\d+)mm\s*x\s*(\d+)mm', shopify_size)
    if match:
        return f"{match.group(1)}x{match.group(2)}"
    
    raise ValueError(f"Cannot parse size format: {shopify_size}")

def translate_field(field_name: str, shopify_value: Any) -> Any:
    """Main translation dispatcher"""
    if field_name == 'material' and shopify_value in MATERIAL_TRANSLATIONS:
        return MATERIAL_TRANSLATIONS[shopify_value]
    
    if field_name == 'size' and isinstance(shopify_value, str):
        try:
            return translate_size_format(shopify_value)
        except ValueError:
            return shopify_value  # Return original if can't parse
    
    # Add more field translations as needed
    return shopify_value
```

**Phase 2: Update Wrappers with Translation (2 hours)**

For each affected calculator:
```python
@calculator_wrapper(validate_params=True)
def calculate_bollard_signs(
    quantity: int,
    size: str = None,
    material: str = None,
    sides: str = None,
    artworks: int = None
) -> Dict[str, Any]:
    """Shopify calculator for Bollard Signs"""
    
    # Apply defaults
    if size is None:
        size = "270mm W x 1000mm H - Three Sided"  # ✅ JSON default
    if material is None:
        material = "5mm Corflute"                   # ✅ JSON default
    
    # ✅ NEW: Validate against JSON format (what AI receives from schema)
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
    if size not in valid_sizes:
        return {"success": False, "error": f"Invalid size: '{size}'. Must be one of: {valid_sizes[:3]}..."}
    
    valid_materials = ["3mm Corflute", "5mm Corflute"]
    if material not in valid_materials:
        return {"success": False, "error": f"Invalid material: '{material}'. Must be one of: {valid_materials}"}
    
    # ✅ NEW: Translate to backend format
    from format_translator import translate_field
    backend_size = translate_field('size', size)        # "270mm W x 1000mm H..." → "270x1000"
    backend_material = translate_field('material', material)  # "3mm Corflute" → "Corflute"
    
    # Call backend with translated values
    calculator = BollardSignsShopifyCalculator()
    result = calculator.calculate(
        quantity=quantity,
        size=backend_size,      # ✅ Backend-compatible format
        material=backend_material,  # ✅ Backend-compatible format
        sides=sides,
        artworks=artworks
    )
    ...
```

**Phase 3: Update Schemas with Accurate JSON Values (30 minutes)**

Schemas are already correct! They extracted JSON values properly.
Just need to verify they're being used.

**Phase 4: Testing (1 hour)**

For each fixed calculator:
```python
def test_bollard_signs_json_format():
    """Test with JSON format values (what AI receives)"""
    result = calculate_bollard_signs(
        quantity=10,
        material="3mm Corflute",  # ✅ JSON format
        size="270mm W x 1000mm H - Three Sided",  # ✅ JSON format
        sides="Single",
        artworks=1
    )
    assert result['success'] == True
    assert result['total_price'] > 0
```

---

## Timeline & Priority

### IMMEDIATE (Today - 3 hours):
1. Create format_translator.py module
2. Fix critical calculators:
   - bollard_signs
   - construction_signs
   - election_signs
   - stackable_cubes
3. Test fixes

### HIGH (Tomorrow - 3 hours):
4. Fix remaining 10 calculators
5. Comprehensive testing
6. Update documentation

### MEDIUM (This Week):
7. Add integration tests for all calculators
8. Create JSON→Backend format validation tool
9. Update development guidelines

---

## Testing Strategy

### Unit Tests (Per Calculator):
```python
# Test 1: JSON format values work (AI agent scenario)
def test_json_format():
    result = calculate_X(param="JSON_VALUE")
    assert result['success'] == True

# Test 2: Backend format still works (backwards compatibility)
def test_backend_format():
    result = calculate_X(param="BACKEND_VALUE")
    assert result['success'] == True

# Test 3: Invalid values rejected
def test_invalid():
    result = calculate_X(param="INVALID")
    assert result['success'] == False
```

### Integration Tests:
```python
# Test 4: Schema → Wrapper → Backend flow
def test_end_to_end():
    # Get schema
    schema = get_calculator_schema("bollard_signs")
    
    # Use first enum value from schema (what AI would use)
    material = schema['properties']['material']['enum'][0]
    size = schema['properties']['size']['enum'][0]
    
    # Call wrapper
    result = calculate_bollard_signs(quantity=10, material=material, size=size)
    
    # Should succeed!
    assert result['success'] == True
```

---

## Prevention Measures

### 1. Automated Format Compatibility Tests
Create CI test that verifies schema enums work with wrappers:
```python
for calculator in ALL_CALCULATORS:
    schema = get_schema(calculator)
    for field, spec in schema['properties'].items():
        if 'enum' in spec:
            for value in spec['enum']:
                # Test that schema value works with wrapper
                result = call_calculator(calculator, {field: value})
                assert result['success'] == True, f"Schema value '{value}' failed for {calculator}.{field}"
```

### 2. Documentation Requirements
Every calculator must document:
- JSON field names and formats
- Backend parameter names and formats
- Translation mappings (if any)
- Example valid values

### 3. Code Generation
Auto-generate wrappers from JSON specs:
```python
# Reads JSON → Generates wrapper with:
# - Correct defaults from JSON
# - Correct validation from JSON enums
# - Auto translation to backend format
```

---

## Key Learnings

1. **Multi-Layer Systems Need Format Agreements**
   - JSON, Backend, Wrapper, Schema must use compatible formats
   - Or explicit translation layer required

2. **Schema Extraction Was Correct**
   - The schema team did the right thing (extract JSON values)
   - The backend team created incompatible formats
   - Need translation bridge, not schema changes

3. **Testing Must Be End-to-End**
   - Unit testing each layer independently missed the integration failures
   - Need tests that verify Schema → Wrapper → Backend flow

4. **Documentation Must Include All Layers**
   - JSON specs alone are insufficient
   - Must document backend format expectations
   - Must document any translation requirements

---

## Next Steps

**Immediate Action Required:**
1. Implement format_translator.py module
2. Fix 4 critical calculators (bollard_signs, construction_signs, election_signs, stackable_cubes)
3. Test fixes thoroughly
4. Deploy to production

**After Critical Fixes:**
5. Fix remaining 10 calculators systematically
6. Add comprehensive integration tests
7. Update development documentation
8. Create format compatibility validation tool

---

**Analysis Complete:** January 23, 2026, 2:45 PM
**Recommended Approach:** Option A (Translation Layer)
**Estimated Total Time:** 6 hours
**Priority:** 🚨 CRITICAL - Blocking 14 production calculators
