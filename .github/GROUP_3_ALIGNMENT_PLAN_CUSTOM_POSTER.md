# Custom Poster Printing Calculator Alignment Plan

**Calculator:** `calculate_custom_poster_printing`  
**Date:** 2026-01-19  
**Status:** CRITICAL MISALIGNMENT DETECTED

---

## STEP 1: Backend Analysis

**File:** `CustomPosterPrinting_Shopify_Calculator.py`

### Backend Parameters (from `calculate()` method - lines 70-73):

```python
quantity = int(kwargs.get('quantity', kwargs.get('qty', 50)))
width = Decimal(kwargs.get('width_mm', kwargs.get('width', 420)))  # A3
height = Decimal(kwargs.get('height_mm', kwargs.get('height', 594)))
paper_stock = kwargs.get('paper_stock', '150gsm')
```

**✅ BACKEND ACCEPTS:**
- `quantity` (int) - Number of posters, default 50
- `width_mm` (fallback: `width`) - Width in mm, default 420
- `height_mm` (fallback: `height`) - Height in mm, default 594
- `paper_stock` (str) - Paper type, default '150gsm'

**❌ BACKEND DOES NOT USE:**
- `size` - Not referenced anywhere in backend
- `paper_type` - Backend uses `paper_stock` not `paper_type`
- `length_mm` - Backend uses `height_mm`
- `artworks` - Not used in calculation logic

---

## STEP 2: Current Wrapper Analysis

**File:** `calculator_wrapper.py` (Lines 2656-2699)

### Current Wrapper Implementation:

```python
def calculate_custom_poster_printing(
    quantity: int,
    width_mm: int = 420,
    height_mm: int = 594,
    paper_stock: str = "150gsm",
    # Legacy aliases
    width: int = None,
    height: int = None
) -> Dict[str, Any]:
```

**✅ WRAPPER STATUS:**
- Already has explicit parameters matching backend
- Has legacy aliases (width → width_mm, height → height_mm)
- **MISSING:** @calculator_wrapper decorator with validation
- **MISSING:** Comprehensive docstring

**Issues:**
- No decorator for type validation
- Legacy translation present but not documented

---

## STEP 3: Current Schema Analysis

**File:** `calculator_tools.json` (Lines 1309-1350)

### Current Schema:

```json
{
  "name": "calculate_custom_poster_printing",
  "parameters": {
    "quantity": {"type": "integer", "minimum": 1, "maximum": 10000},
    "width_mm": {"type": "integer"},
    "paper_type": {
      "enum": ["250GSM Satin Poster Paper", "200GSM Yuppo Synthetic Paper"]
    },
    "size": {
      "enum": ["A2 - 420mm x 594mm", "A1 - 594mm x 841mm", "A0 - 841mm x 1189mm", "Custom"]
    },
    "length_mm": {"type": "integer"},
    "artworks": {"type": "integer"}
  }
}
```

**❌ CRITICAL SCHEMA ISSUES:**
1. Uses `paper_type` but backend expects `paper_stock`
2. Includes `size` enum but backend doesn't use it
3. Uses `length_mm` but backend expects `height_mm`
4. Includes `artworks` but backend doesn't use it
5. Missing `paper_stock` parameter that backend actually uses

---

## STEP 4: Alignment Plan

### Misalignment Summary:

| Parameter | Schema | Wrapper | Backend | Status |
|-----------|--------|---------|---------|--------|
| `quantity` | ✅ integer | ✅ int | ✅ int | ALIGNED |
| `width_mm` | ✅ integer | ✅ int | ✅ Decimal | ALIGNED |
| `height_mm` | ❌ MISSING | ✅ int | ✅ Decimal | SCHEMA MISSING |
| `paper_stock` | ❌ MISSING | ✅ str | ✅ str | SCHEMA MISSING |
| `paper_type` | ❌ EXISTS | ❌ MISSING | ❌ NOT USED | SCHEMA WRONG |
| `size` | ❌ EXISTS | ❌ MISSING | ❌ NOT USED | SCHEMA WRONG |
| `length_mm` | ❌ EXISTS | ❌ MISSING | ❌ NOT USED | SCHEMA WRONG |
| `artworks` | ❌ EXISTS | ❌ MISSING | ❌ NOT USED | SCHEMA WRONG |
| `width` | N/A | ✅ legacy | ✅ fallback | LEGACY SUPPORT |
| `height` | N/A | ✅ legacy | ✅ fallback | LEGACY SUPPORT |

### Target State:

**Schema must match backend exactly:**
- `quantity` (integer, 1-10000)
- `width_mm` (integer, default 420)
- `height_mm` (integer, default 594) ← **ADD THIS**
- `paper_stock` (string, default "150gsm") ← **ADD THIS**

**Remove from schema:**
- `paper_type` ← **WRONG NAME**
- `size` ← **NOT USED**
- `length_mm` ← **WRONG NAME**
- `artworks` ← **NOT USED**

**Wrapper:**
- Add `@calculator_wrapper` decorator with validation
- Keep current explicit parameters
- Keep legacy aliases (width, height)
- Add comprehensive docstring

---

## STEP 5: Implementation - Schema Fix

**REPLACE schema in calculator_tools.json (lines 1309-1350):**

```json
{
  "name": "calculate_custom_poster_printing",
  "short_description": "Calculate custom poster printing quotes with custom dimensions",
  "description": "Calculate quote for Custom Poster Printing. High-quality custom poster printing in any size from 100mm to 2000mm width and height. Professional poster printing with fast turnaround.",
  "parameters": {
    "quantity": {
      "type": "integer",
      "description": "Number of posters to print",
      "minimum": 1,
      "maximum": 10000
    },
    "width_mm": {
      "type": "integer",
      "description": "Width in millimeters (100-2000mm)",
      "minimum": 100,
      "maximum": 2000
    },
    "height_mm": {
      "type": "integer",
      "description": "Height in millimeters (100-3000mm)",
      "minimum": 100,
      "maximum": 3000
    },
    "paper_stock": {
      "type": "string",
      "description": "Paper stock type",
      "enum": ["150gsm", "200gsm", "250gsm"]
    }
  }
}
```

---

## STEP 6: Implementation - Wrapper Fix

**REPLACE wrapper in calculator_wrapper.py (starting line 2656):**

```python
@calculator_wrapper(validate_params=True)
def calculate_custom_poster_printing(
    quantity: int,
    width_mm: int = 420,
    height_mm: int = 594,
    paper_stock: str = "150gsm",
    # Legacy aliases for backwards compatibility
    width: int = None,
    height: int = None
) -> Dict[str, Any]:
    """
    Calculate quote for Custom Poster Printing (Shopify)
    
    Args:
        quantity: Number of posters (1-10000)
        width_mm: Width in millimeters (100-2000mm, default 420 for A2)
        height_mm: Height in millimeters (100-3000mm, default 594 for A2)
        paper_stock: Paper type - "150gsm", "200gsm", "250gsm"
        width: Legacy alias for width_mm (deprecated)
        height: Legacy alias for height_mm (deprecated)
    
    Returns:
        Dict with success, total_price, unit_price, cost_per_item, breakdown, specifications
    """
    warnings = []
    
    # Legacy translation
    if width is not None:
        width_mm = width
        warnings.append({
            "deprecated": "width",
            "use_instead": "width_mm",
            "value": width
        })
    if height is not None:
        height_mm = height
        warnings.append({
            "deprecated": "height",
            "use_instead": "height_mm",
            "value": height
        })
    
    # ... rest of implementation stays same
```

---

## STEP 7: Testing Plan

### Test Coverage (12 tests):

1. `test_01_new_params_basic_success` - New param structure works
2. `test_02_new_params_variations` - Different sizes
3. `test_03_legacy_params_with_warnings` - width/height → width_mm/height_mm
4. `test_04_legacy_vs_new_same_result` - Legacy and new match
5. `test_05_quantity_validation` - Range validation
6. `test_06_size_variations` - A2, A1, A0, custom sizes
7. `test_07_paper_stock_options` - All stock types
8. `test_08_minimum_parameters` - Defaults work
9. `test_09_large_format` - Large posters
10. `test_10_area_based_pricing` - Larger area = higher cost
11. `test_11_response_structure` - All required fields
12. `test_12_price_consistency` - Same params = same price

---

## Summary

**Alignment Status:** ❌ CRITICAL MISALIGNMENT (50%)

**Critical Issues:**
1. Schema uses wrong parameter names (`paper_type`, `length_mm`)
2. Schema includes unused parameters (`size`, `artworks`)
3. Schema missing required parameter (`height_mm`)
4. Schema missing required parameter (`paper_stock`)

**Required Changes:**
1. Complete schema rewrite to match backend
2. Add decorator to wrapper
3. Update wrapper docstring
4. Create comprehensive test suite

**Timeline:** 20 minutes

**Risk Level:** MEDIUM - Schema completely wrong, may break existing AI agents using old parameter names
