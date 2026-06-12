# Group 3 Calculators - Consolidated Alignment Plan

**Date:** 2026-01-19  
**Status:** SYSTEMATIC IMPLEMENTATION IN PROGRESS

---

## Overview

Group 3 consists of 5 Shopify calculators with similar structure:
1. ✅ **calculate_notepads_a4** - COMPLETED (12/12 tests passing)
2. ⚠️ **calculate_notepads_a5** - Needs cleanup (remove unused legacy params)
3. ⚠️ **calculate_notepads_a6** - Needs cleanup (remove unused legacy params)
4. ⚠️ **calculate_custom_poster_printing** - Needs analysis and fixing
5. ⚠️ **calculate_custom_vinyl_stickers** - Needs analysis and fixing

---

## Notepads A5 Analysis

### Backend Parameters (NotepadsA5_Shopify_Calculator.py):
```python
quantity = int(kwargs.get('quantity', kwargs.get('qty', 250)))
print_sides = kwargs.get('print_sides', 'Single side print')
print_type = kwargs.get('print_type', 'Colour')
paper_stock = kwargs.get('paper_stock', 'Standard')
artworks = int(kwargs.get('artworks', 1))
# NO pads_per_book parameter used
```

### Current Wrapper Status:
- ✅ Has @calculator_wrapper decorator
- ✅ Has explicit parameters
- ❌ Has unused legacy params (leaves_per_pad, finish_size)

### Required Changes:
1. Remove `leaves_per_pad` and `finish_size` legacy parameters
2. Update docstring
3. Fix test expectations

---

## Notepads A6 Analysis

### Backend Parameters (NotepadsA6_Shopify_Calculator.py):
Same structure as A5 - quantity, print_sides, print_type, paper_stock, artworks

### Current Wrapper Status:
- ✅ Has @calculator_wrapper decorator
- ✅ Has explicit parameters
- ❌ Has unused legacy params (leaves_per_pad, finish_size)

### Required Changes:
Same as A5

---

## Custom Poster Printing Analysis

**NEEDS FULL BACKEND ANALYSIS** - Different product type, likely different parameters

### Next Steps:
1. Read backend CustomPosterPrinting_Shopify_Calculator.py
2. Identify actual parameters used
3. Compare to current schema/wrapper
4. Create specific alignment plan

---

## Custom Vinyl Stickers Analysis

**NEEDS FULL BACKEND ANALYSIS** - Different product type, likely different parameters

### Next Steps:
1. Read backend CustomVinylStickers_Shopify_Calculator.py
2. Identify actual parameters used
3. Compare to current schema/wrapper
4. Create specific alignment plan

---

## Implementation Order

1. ✅ **Notepads A4** - COMPLETE
2. **Notepads A5** - Clean up wrapper (5 min)
3. **Notepads A6** - Clean up wrapper (5 min)
4. **Custom Poster** - Full analysis + implementation (15 min)
5. **Custom Vinyl** - Full analysis + implementation (15 min)

**Total Estimated Time:** 40 minutes

---

## Pattern to Follow

### For Notepads A5 & A6:
```python
@calculator_wrapper(quantity_enum=[...], validate_params=True)
def calculate_notepads_aX(
    quantity: int,
    print_type: str = "Colour",
    print_sides: str = "Single side print",
    paper_stock: str = "Standard",
    artworks: int = 1,
    stock_type: str = None  # Only legacy param
) -> Dict[str, Any]:
    """
    Calculate quote for Notepads AX (Shopify)
    
    Args:
        quantity: Number of notepads (25-2000)
        print_type: "Colour" or "Black & White"
        print_sides: "Single side print" or "Double side print"
        paper_stock: Paper type
        artworks: Number of unique designs
        stock_type: Legacy alias for paper_stock (deprecated)
    
    Returns:
        Dict with quote details
    """
    warnings = []
    if stock_type is not None:
        paper_stock = stock_type
        warnings.append({
            "deprecated": "stock_type",
            "use_instead": "paper_stock",
            "value": stock_type
        })
    # ... rest
```

### For Custom Products:
**TBD** - Based on backend analysis

---

## Success Criteria

For each calculator:
- [x] Backend parameters documented
- [x] Schema matches backend exactly
- [x] Wrapper has explicit parameters (no **kwargs)
- [x] Decorator validates types/enums
- [x] Only used legacy parameters included
- [x] Comprehensive docstring present
- [x] All 12 tests pass
- [x] No backend changes made

---

## Testing Strategy

Each calculator must pass:
1. New params basic success
2. New params all variations
3. Legacy params with warnings
4. Legacy vs new same result
5. Quantity validation
6. Enum validation for all parameters
7. Response structure verification
8. Price consistency checks

**Current Status:**
- Notepads A4: 12/12 ✅
- Notepads A5: TBD
- Notepads A6: TBD
- Custom Poster: TBD
- Custom Vinyl: TBD
