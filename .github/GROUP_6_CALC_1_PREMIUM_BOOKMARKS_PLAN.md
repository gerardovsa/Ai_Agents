# Premium Bookmarks Calculator Alignment Plan

**Calculator:** `calculate_premium_bookmarks`  
**Date:** 2026-01-19  
**Status:** READY FOR IMPLEMENTATION

---

## STEP 1: BACKEND ANALYSIS

**File:** `PremiumBookmarks_Shopify_Calculator.py`

### Backend `calculate()` Method (Lines 68-116):

```python
def calculate(self, **kwargs) -> PremiumBookmarksShopifyCalculatorQuoteResult:
    quantity = int(kwargs.get('quantity', kwargs.get('qty', 250)))
    width = Decimal(kwargs.get('width_mm', kwargs.get('width', 55)))
    height = Decimal(kwargs.get('height_mm', kwargs.get('height', 200)))
    paper_stock = kwargs.get('paper_stock', '350gsm')
    lamination = kwargs.get('lamination', 'Matte')
```

**✅ BACKEND PARAMETERS:**
- `quantity` (int) - Number of bookmarks, default 250
- `width_mm` (fallback: `width`) - Width in mm, default 55
- `height_mm` (fallback: `height`) - Height in mm, default 200
- `paper_stock` (str) - Paper type, default '350gsm'
- `lamination` (str) - Lamination finish, default 'Matte'

---

## STEP 2: CURRENT WRAPPER ANALYSIS

**File:** `calculator_wrapper.py` (Line 3010)

### Current Wrapper:

```python
def calculate_premium_bookmarks(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Premium Bookmarks"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from PremiumBookmarks_Shopify_Calculator import PremiumBookmarksShopifyCalculator
        calculator = PremiumBookmarksShopifyCalculator()
        result = calculator.calculate(**kwargs)  # ❌ PASSES ALL KWARGS
```

**❌ WRAPPER ISSUES:**
1. Uses `**kwargs` only (no explicit parameters)
2. No type validation
3. No decorator
4. Passes all kwargs directly to backend
5. No parameter documentation
6. No legacy parameter support

---

## STEP 3: CURRENT SCHEMA ANALYSIS

**File:** `calculator_tools.json` (Line 1638)

### Current Schema Parameters:

```json
{
  "quantity": {"type": "string", "enum": ["25", "50", "100", ...]},  // ❌ WRONG TYPE
  "celloglaze": {"enum": ["None", "Gloss 1 Sided", ...]},            // ❌ WRONG NAME
  "print_type": {"enum": ["Colour 1 sided", "Colour 2 sided"]},      // ❌ NOT USED
  "finish_size": {"enum": ["50mm x 150mm", "50mm x 185mm", ...]}     // ❌ NOT USED
}
```

**❌ SCHEMA ISSUES:**
1. `quantity` is string - should be integer
2. Uses `celloglaze` - backend uses `lamination`
3. Has `print_type` - backend doesn't use this
4. Has `finish_size` enum - backend uses `width_mm` + `height_mm`
5. Missing `width_mm` parameter
6. Missing `height_mm` parameter
7. Missing `paper_stock` parameter

---

## STEP 4: ALIGNMENT PLAN

### Misalignment Summary:

| Parameter | Schema | Wrapper | Backend | Status |
|-----------|--------|---------|---------|--------|
| `quantity` | ❌ string | ✅ int | ✅ int | SCHEMA WRONG TYPE |
| `lamination` | ❌ MISSING | ❌ MISSING | ✅ str | SCHEMA/WRAPPER MISSING |
| `width_mm` | ❌ MISSING | ❌ MISSING | ✅ Decimal | SCHEMA/WRAPPER MISSING |
| `height_mm` | ❌ MISSING | ❌ MISSING | ✅ Decimal | SCHEMA/WRAPPER MISSING |
| `paper_stock` | ❌ MISSING | ❌ MISSING | ✅ str | SCHEMA/WRAPPER MISSING |
| `celloglaze` | ❌ EXISTS | ❌ N/A | ❌ NOT USED | SCHEMA WRONG NAME |
| `print_type` | ❌ EXISTS | ❌ N/A | ❌ NOT USED | SCHEMA WRONG |
| `finish_size` | ❌ EXISTS | ❌ N/A | ❌ NOT USED | SCHEMA WRONG |

---

## STEP 5: SCHEMA FIX IMPLEMENTATION

**Replace schema (lines 1638-1685):**

```json
{
  "name": "calculate_premium_bookmarks",
  "short_description": "Calculate premium bookmark quotes with custom sizing and lamination",
  "description": "Calculate quote for Premium Bookmarks. High-quality bookmarks with custom dimensions and optional lamination.",
  "parameters": {
    "quantity": {
      "type": "integer",
      "description": "Number of bookmarks to print",
      "enum": [25, 50, 100, 250, 500, 750, 1000, 1250, 1500, 2000]
    },
    "width_mm": {
      "type": "integer",
      "description": "Width in millimeters (default 55mm)",
      "minimum": 40,
      "maximum": 100
    },
    "height_mm": {
      "type": "integer",
      "description": "Height in millimeters (default 200mm)",
      "minimum": 100,
      "maximum": 300
    },
    "paper_stock": {
      "type": "string",
      "description": "Paper weight",
      "enum": ["350gsm", "300gsm", "250gsm"]
    },
    "lamination": {
      "type": "string",
      "description": "Lamination finish",
      "enum": ["None", "Matte", "Gloss"]
    }
  }
}
```

---

## STEP 6: WRAPPER FIX IMPLEMENTATION

**Replace wrapper (starting line 3010):**

```python
@calculator_wrapper(
    quantity_enum=[25, 50, 100, 250, 500, 750, 1000, 1250, 1500, 2000],
    validate_params=True
)
def calculate_premium_bookmarks(
    quantity: int,
    width_mm: int = 55,
    height_mm: int = 200,
    paper_stock: str = "350gsm",
    lamination: str = "Matte",
    # Legacy parameters for backwards compatibility
    width: int = None,
    height: int = None,
    celloglaze: str = None
) -> Dict[str, Any]:
    """
    Calculate quote for Premium Bookmarks (Shopify)
    
    Args:
        quantity: Number of bookmarks (25-2000)
        width_mm: Width in millimeters (40-100mm, default 55)
        height_mm: Height in millimeters (100-300mm, default 200)
        paper_stock: Paper weight - "350gsm", "300gsm", "250gsm"
        lamination: Lamination finish - "None", "Matte", "Gloss"
        width: Legacy alias for width_mm (deprecated)
        height: Legacy alias for height_mm (deprecated)
        celloglaze: Legacy alias for lamination (deprecated)
    
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
    
    if celloglaze is not None:
        # Translate celloglaze enum to lamination
        lamination_map = {
            "None": "None",
            "Gloss 1 Sided": "Gloss",
            "Gloss 2 Sided": "Gloss",
            "Matt 1 Sided": "Matte",
            "Matt 2 Sided": "Matte"
        }
        lamination = lamination_map.get(celloglaze, "Matte")
        warnings.append({
            "deprecated": "celloglaze",
            "use_instead": "lamination",
            "value": celloglaze,
            "translated_to": lamination
        })
    
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        from PremiumBookmarks_Shopify_Calculator import PremiumBookmarksShopifyCalculator
        calculator = PremiumBookmarksShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            width_mm=width_mm,
            height_mm=height_mm,
            paper_stock=paper_stock,
            lamination=lamination
        )
        
        response = {
            "success": True,
            "product_type": "Premium Bookmarks",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        
        if warnings:
            response["warnings"] = warnings
        
        return response
        
    except Exception as e:
        print(f"❌ [Shopify Premium Bookmarks] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}
```

---

## STEP 7: TESTING PLAN

### Test Coverage (12 tests):

1. ✅ `test_01_new_params_basic_success` - New parameters work
2. ✅ `test_02_legacy_celloglaze_translation` - celloglaze → lamination
3. ✅ `test_03_legacy_width_height` - width/height → width_mm/height_mm
4. ✅ `test_04_legacy_vs_new_same_result` - Price consistency
5. ✅ `test_05_quantity_enum_validation` - Enum validation
6. ✅ `test_06_lamination_options` - All lamination values
7. ✅ `test_07_paper_stock_options` - All paper stocks
8. ✅ `test_08_custom_dimensions` - Custom width/height
9. ✅ `test_09_minimum_parameters` - Defaults work
10. ✅ `test_10_price_consistency` - Same params = same price
11. ✅ `test_11_response_structure` - All required fields
12. ✅ `test_12_size_based_pricing` - Larger = more expensive

---

## SUMMARY

**Alignment Status:** ❌ CRITICAL MISALIGNMENT (40%)

**Required Changes:**
1. Complete schema rewrite (wrong param names and types)
2. Add explicit parameters to wrapper (remove `**kwargs`)
3. Add decorator with validation
4. Add legacy parameter translation (celloglaze, width, height)
5. Create comprehensive test suite

**Timeline:** 15 minutes

**Risk Level:** MEDIUM - Schema completely wrong, needs full rewrite
