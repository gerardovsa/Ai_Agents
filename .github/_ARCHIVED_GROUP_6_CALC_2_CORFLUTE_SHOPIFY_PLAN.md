# Corflute Signs Shopify Calculator Alignment Plan

**Calculator:** `calculate_corflute_signs_shopify`  
**Date:** 2026-01-19  
**Status:** ✅ ALREADY ALIGNED - Only needs decorator + testing

---

## STEP 1: BACKEND ANALYSIS

**File:** `corflute_calculator_shopify.py`

### Backend `calculate()` Method (Lines 196-305):

```python
def calculate(
    self,
    size_preset: CorfluteSizePreset = CorfluteSizePreset.SIZE_600x900,
    custom_width_mm: int = 0,
    custom_height_mm: int = 0,
    thickness: CorfiuteThickness = CorfiuteThickness.MM_5,
    quantity: int = 10,
    double_sided: bool = False,
    eyelet_option: EyeletOption = EyeletOption.NONE,
    cutting_type: CuttingType = CuttingType.STANDARD,
    artworks: int = 1,
) -> Dict:
```

**✅ BACKEND PARAMETERS:**
- `size_preset` (CorfluteSizePreset enum) - "450x600", "600x900", "900x1200", "1200x2400", "custom"
- `custom_width_mm` (int) - Width for custom size, default 0
- `custom_height_mm` (int) - Height for custom size, default 0
- `thickness` (CorfiuteThickness enum) - "3mm" or "5mm", default "5mm"
- `quantity` (int) - Number of signs, default 10
- `double_sided` (bool) - Print both sides, default False
- `eyelet_option` (EyeletOption enum) - "none", "four_corners", "two_top", etc.
- `artworks` (int) - Number of designs, default 1
- `cutting_type` (CuttingType enum) - Not used in schema (backend-only)

---

## STEP 2: CURRENT WRAPPER ANALYSIS

**File:** `calculator_wrapper.py` (Line 990)

### Current Wrapper:

```python
def calculate_corflute_signs_shopify(
    quantity: int,
    size_preset: str = "600x900",
    custom_width_mm: int = 0,
    custom_height_mm: int = 0,
    thickness: str = "5mm",
    double_sided: bool = False,
    eyelet_option: str = "none",
    artworks: int = 1,
    **kwargs
) -> Dict[str, Any]:
```

**✅ WRAPPER STATUS:**
1. ✅ Has explicit parameters (matches backend)
2. ✅ Correct types
3. ✅ Has type conversion for JSON inputs
4. ✅ Has enum mapping logic
5. ❌ Missing decorator
6. ❌ No legacy parameter support (but none needed)
7. ✅ Good error handling

---

## STEP 3: CURRENT SCHEMA ANALYSIS

**File:** `calculator_tools.json` (Line 315)

### Current Schema Parameters:

```json
{
  "quantity": {"type": "integer"},
  "size_preset": {"type": "string", "enum": ["450x600", "600x900", ...]},
  "custom_width_mm": {"type": "integer"},
  "custom_height_mm": {"type": "integer"},
  "thickness": {"type": "string", "enum": ["3mm", "5mm"]},
  "double_sided": {"type": "boolean"},
  "eyelet_option": {"type": "string", "enum": ["none", "four_corners", ...]},
  "artworks": {"type": "integer"}
}
```

**✅ SCHEMA STATUS:**
- ✅ All parameters match backend
- ✅ Correct types
- ✅ Correct enums
- ✅ Good descriptions

---

## STEP 4: ALIGNMENT PLAN

### Misalignment Summary:

| Parameter | Schema | Wrapper | Backend | Status |
|-----------|--------|---------|---------|--------|
| `quantity` | ✅ integer | ✅ int | ✅ int | ALIGNED |
| `size_preset` | ✅ string | ✅ str | ✅ enum | ALIGNED |
| `custom_width_mm` | ✅ integer | ✅ int | ✅ int | ALIGNED |
| `custom_height_mm` | ✅ integer | ✅ int | ✅ int | ALIGNED |
| `thickness` | ✅ string | ✅ str | ✅ enum | ALIGNED |
| `double_sided` | ✅ boolean | ✅ bool | ✅ bool | ALIGNED |
| `eyelet_option` | ✅ string | ✅ str | ✅ enum | ALIGNED |
| `artworks` | ✅ integer | ✅ int | ✅ int | ALIGNED |

**Overall Alignment: 100% ✅**

**Only Required Changes:**
1. Add @calculator_wrapper decorator with quantity enum
2. Create comprehensive test suite (12 tests)

---

## STEP 5: SCHEMA FIX IMPLEMENTATION

**No changes needed** - Schema is perfect!

---

## STEP 6: WRAPPER FIX IMPLEMENTATION

**Only need to add decorator:**

```python
@calculator_wrapper(
    quantity_enum=[1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 250, 300, 400, 500, 750, 1000, 1500, 2000, 3000, 5000, 10000],
    validate_params=True
)
def calculate_corflute_signs_shopify(
    quantity: int,
    size_preset: str = "600x900",
    custom_width_mm: int = 0,
    custom_height_mm: int = 0,
    thickness: str = "5mm",
    double_sided: bool = False,
    eyelet_option: str = "none",
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate quote for Corflute Signs (Shopify)
    
    ✅ CURRENT PARAMETERS:
        quantity: Number of signs (1-10000)
        size_preset: "450x600", "600x900", "900x1200", "1200x2400", "custom"
        custom_width_mm: Custom width in mm (only if size_preset='custom')
        custom_height_mm: Custom height in mm (only if size_preset='custom')
        thickness: "3mm" or "5mm" (default: "5mm")
        double_sided: Print both sides (default: False)
        eyelet_option: "none", "four_corners", "two_top", etc.
        artworks: Number of artworks (first 5 free, default: 1)
    
    Returns:
        Dict with success, tier pricing breakdown, costs, discounts, final total
    """
    # ... existing implementation (no changes needed)
```

**Changes:**
- ✅ Remove `**kwargs` (not needed)
- ✅ Add decorator with comprehensive quantity enum (43-tier pricing)
- ✅ Update docstring format

---

## STEP 7: TESTING PLAN

### Test Coverage (12 tests):

1. ✅ `test_01_preset_size_basic` - Preset sizes work
2. ✅ `test_02_custom_size` - Custom dimensions work
3. ✅ `test_03_double_sided` - Double-sided pricing adds $6/sqm
4. ✅ `test_04_eyelets` - Eyelet options work
5. ✅ `test_05_artworks` - Multiple artworks (first 5 free)
6. ✅ `test_06_thickness_3mm` - 3mm thickness pricing
7. ✅ `test_07_thickness_5mm` - 5mm thickness pricing
8. ✅ `test_08_volume_tiers` - 43-tier pricing discounts
9. ✅ `test_09_minimum_order` - $135 minimum applied
10. ✅ `test_10_discount_5_percent` - 5% discount applied
11. ✅ `test_11_response_structure` - All required fields
12. ✅ `test_12_tier_pricing_consistency` - Same tier = same price/sqm

---

## SUMMARY

**Alignment Status:** ✅ ALREADY ALIGNED (100%)

**Required Changes:**
1. Add @calculator_wrapper decorator
2. Remove **kwargs
3. Create comprehensive test suite

**Timeline:** 5 minutes

**Risk Level:** VERY LOW - Only adding decorator, all logic perfect
