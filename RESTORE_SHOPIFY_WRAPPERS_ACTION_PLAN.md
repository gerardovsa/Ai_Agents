# Action Plan: Restore Shopify Calculator Wrappers

**Date:** December 10, 2025  
**Priority:** 🔥 **CRITICAL** - Needed for Pacific Partnerships quotes  
**Complexity:** ⭐⭐ **Medium** - Create wrappers + documentation

## 🎯 **Goal**

Restore the simplified Shopify calculator wrapper interface that previously existed in commit `5e29923`.

## 📊 **What We're Restoring**

### **Simple Tool Interface (What AI Needs)**

```python
calculate_wire_bound_books_shopify(
    quantity=3,
    pages=316,
    size="A4",
    cover_stock="350GSM Satin",
    inner_stock="100GSM Uncoated",
    cover_cellophane="No Cellophane"
)
```

### **Complex Internal Calculator (What Exists)**

```python
WireBoundShopifyCalculator.calculate(
    quantity=3,                      # F1
    artworks=1,                      # F2  
    finish_size="A4 Portrait",       # F14
    outer_front_cover="Clear PVC",   # F3
    printed_front_cover="350GSM Satin", # F4
    # ... 9 more F-parameters ...
)
```

## 🛠️ **Implementation Steps**

### **Step 1: Create Wrapper Module**

**File:** `inhouse_modules/shopify_calculator_wrappers.py`

```python
"""
Shopify Calculator Wrappers
===========================

Simplified interface for Shopify WooCommerce calculators.
Maps user-friendly parameters to complex F1-F14 WooCommerce fields.
"""

from typing import Dict, Any
from decimal import Decimal
from shopify_calculators.WireBound_Shopify_Calculator import WireBoundShopifyCalculator
from shopify_calculators.SpiralBound_Shopify_Calculator import SpiralBoundShopifyCalculator


def calculate_wire_bound_books_shopify(
    quantity: int,
    pages: int,
    size: str,  # "A4" or "A5"
    cover_stock: str,  # e.g., "350GSM Satin"
    inner_stock: str,  # e.g., "100GSM Uncoated"
    cover_cellophane: str = "No Cellophane"  # "No Cellophane", "Gloss Cellophane", "Matt Cellophane"
) -> Dict[str, Any]:
    """
    Calculate quote for Wire Bound Books using simplified parameters.
    
    This wrapper maps simple parameters to the complex F1-F14 WooCommerce structure.
    
    Args:
        quantity: Number of books to produce
        pages: Total page count (must be divisible by 4)
        size: Book size ("A4" or "A5")
        cover_stock: Cover paper specification (e.g., "350GSM Satin")
        inner_stock: Internal pages paper (e.g., "100GSM Uncoated")
        cover_cellophane: Cellophane/lamination option
        
    Returns:
        Dict with cost_ex_gst, cost_inc_gst, breakdown, specifications
        
    Example:
        >>> calculate_wire_bound_books_shopify(
        ...     quantity=3,
        ...     pages=316,
        ...     size="A4",
        ...     cover_stock="350GSM Satin",
        ...     inner_stock="100GSM Uncoated"
        ... )
    """
    
    # Map size to finish_size with orientation (default Portrait)
    finish_size = f"{size} Portrait"
    
    # Parse cover_stock to extract GSM and type
    # "350GSM Satin" → "350GSM Satin"
    printed_front_cover = cover_stock
    
    # Parse inner_stock and map to Shopify format
    # "100GSM Uncoated" → "Uncoated Bond 100GSM"
    if "Uncoated" in inner_stock or "Bond" in inner_stock:
        # Extract GSM
        gsm = inner_stock.replace("GSM", "").replace("Uncoated", "").replace("Bond", "").strip()
        internal_stock = f"Uncoated Bond {gsm}GSM"
        internal_print = "Black & White"  # Uncoated typically B&W
    elif "Satin" in inner_stock:
        gsm = inner_stock.replace("GSM", "").replace("Satin", "").strip()
        internal_stock = f"Satin {gsm}GSM"
        internal_print = "Full Colour"  # Satin typically color
    else:
        internal_stock = inner_stock
        internal_print = "Full Colour"  # Default to color
    
    # Map cellophane to front_celloglaze
    if "Gloss" in cover_cellophane:
        front_celloglaze = "2 Sided Gloss"
    elif "Matt" in cover_cellophane or "Matte" in cover_cellophane:
        front_celloglaze = "2 Sided Matt"
    else:
        front_celloglaze = "None"
    
    # Detect if clear front cover mentioned
    # (Pacific Partnerships: "Clear Acetate (250mic)")
    outer_front_cover = "Not Required"  # Default
    
    # Detect back cover type
    # (Pacific Partnerships: "350gsm Black Satin Card")
    outer_back_cover = "None"  # Default
    if "Black" in cover_stock.lower() or "black" in str(cover_cellophane).lower():
        outer_back_cover = "350GSM Satin Blank Card"
    
    # Initialize calculator
    calc = WireBoundShopifyCalculator()
    
    # Call with F1-F14 parameters
    result = calc.calculate(
        quantity=quantity,                          # F1
        artworks=1,                                 # F2 (default to 1)
        finish_size=finish_size,                    # F14
        outer_front_cover=outer_front_cover,        # F3
        printed_front_cover=printed_front_cover,    # F4
        front_cover_print="2pp Colour",             # F5 (default color both sides)
        front_celloglaze=front_celloglaze,          # F6
        outer_back_cover=outer_back_cover,          # F7
        printed_back_cover="None",                  # F8
        back_cover_print="None",                    # F9
        back_celloglaze="None",                     # F10
        internal_pages=pages,                       # F11
        internal_stock=internal_stock,              # F12
        internal_print=internal_print               # F13
    )
    
    # Convert result to standard format
    return {
        "success": True,
        "cost_ex_gst": float(result.total_price / Decimal('1.10')),  # Remove GST
        "cost_inc_gst": float(result.total_price),
        "unit_price": float(result.unit_price),
        "product_type": "Wire Bound Books",
        "quantity": result.quantity,
        "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
        "specifications": result.specifications
    }


def calculate_spiral_bound_books_shopify(
    quantity: int,
    pages: int,
    size: str,
    cover_stock: str,
    inner_stock: str,
    cover_cellophane: str = "No Cellophane"
) -> Dict[str, Any]:
    """
    Calculate quote for Spiral Bound Books using simplified parameters.
    
    Same interface as calculate_wire_bound_books_shopify but uses
    SpiralBoundShopifyCalculator internally.
    """
    
    # Same mapping logic as wire_bound (DRY could be improved)
    finish_size = f"{size} Portrait"
    printed_front_cover = cover_stock
    
    if "Uncoated" in inner_stock or "Bond" in inner_stock:
        gsm = inner_stock.replace("GSM", "").replace("Uncoated", "").replace("Bond", "").strip()
        internal_stock = f"Uncoated Bond {gsm}GSM"
        internal_print = "Black & White"
    elif "Satin" in inner_stock:
        gsm = inner_stock.replace("GSM", "").replace("Satin", "").strip()
        internal_stock = f"Satin {gsm}GSM"
        internal_print = "Full Colour"
    else:
        internal_stock = inner_stock
        internal_print = "Full Colour"
    
    if "Gloss" in cover_cellophane:
        front_celloglaze = "2 Sided Gloss"
    elif "Matt" in cover_cellophane or "Matte" in cover_cellophane:
        front_celloglaze = "2 Sided Matt"
    else:
        front_celloglaze = "None"
    
    outer_front_cover = "Not Required"
    outer_back_cover = "None"
    
    calc = SpiralBoundShopifyCalculator()
    
    result = calc.calculate(
        quantity=quantity,
        artworks=1,
        finish_size=finish_size,
        outer_front_cover=outer_front_cover,
        printed_front_cover=printed_front_cover,
        front_cover_print="2pp Colour",
        front_celloglaze=front_celloglaze,
        outer_back_cover=outer_back_cover,
        printed_back_cover="None",
        back_cover_print="None",
        back_celloglaze="None",
        internal_pages=pages,
        internal_stock=internal_stock,
        internal_print=internal_print
    )
    
    return {
        "success": True,
        "cost_ex_gst": float(result.total_price / Decimal('1.10')),
        "cost_inc_gst": float(result.total_price),
        "unit_price": float(result.unit_price),
        "product_type": "Spiral Bound Books",
        "quantity": result.quantity,
        "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
        "specifications": result.specifications
    }
```

### **Step 2: Add to Calculator Requirements**

**File:** `inhouse_modules/complete_calculator_implementation.py`

Add to `get_calculator_requirements()`:

```python
requirements = {
    # ... existing calculators ...
    
    "calculate_wire_bound_books_shopify": {
        "description": "Wire Bound Books - Shopify hardcoded pricing (simplified interface)",
        "note": "Metal wire coil binding. Wrapper for WireBoundShopifyCalculator F1-F14 complexity",
        
        "required_parameters": {
            "quantity": {
                "type": "int",
                "description": "Number of books",
                "example": 3
            },
            "pages": {
                "type": "int",
                "description": "Total page count (must be divisible by 4)",
                "example": 316
            },
            "size": {
                "type": "str",
                "description": "Book size",
                "options": ["A4", "A5"],
                "example": "A4"
            },
            "cover_stock": {
                "type": "str",
                "description": "Cover paper specification",
                "example": "350GSM Satin"
            },
            "inner_stock": {
                "type": "str",
                "description": "Internal pages paper",
                "example": "100GSM Uncoated"
            }
        },
        
        "optional_parameters": {
            "cover_cellophane": {
                "type": "str",
                "description": "Cover lamination",
                "options": ["No Cellophane", "Gloss Cellophane", "Matt Cellophane"],
                "default": "No Cellophane"
            }
        },
        
        "example_pacific_partnerships": {
            "quantity": 3,
            "pages": 316,
            "size": "A4",
            "cover_stock": "350GSM Satin",
            "inner_stock": "100GSM Uncoated",
            "cover_cellophane": "No Cellophane"
        }
    },
    
    "calculate_spiral_bound_books_shopify": {
        "description": "Spiral Bound Books - Shopify hardcoded pricing (simplified interface)",
        "note": "Same parameters as wire_bound_books_shopify but uses plastic spiral coil",
        "parameters": "Same as calculate_wire_bound_books_shopify"
    }
}
```

### **Step 3: Add Routing**

```python
def calculate_quote(self, product_type: str, parameters: Dict[str, Any]):
    """Route to appropriate calculator"""
    
    if product_type == "calculate_wire_bound_books_shopify":
        from shopify_calculator_wrappers import calculate_wire_bound_books_shopify
        return calculate_wire_bound_books_shopify(**parameters)
    
    elif product_type == "calculate_spiral_bound_books_shopify":
        from shopify_calculator_wrappers import calculate_spiral_bound_books_shopify
        return calculate_spiral_bound_books_shopify(**parameters)
    
    # ... existing GOD calculator routing ...
```

## ✅ **Testing**

### **Test 1: Pacific Partnerships Job 1**

```python
quote = calculate_wire_bound_books_shopify(
    quantity=3,
    pages=316,
    size="A4",
    cover_stock="350GSM Satin",
    inner_stock="100GSM Uncoated"
)

assert quote["success"] == True
assert quote["quantity"] == 3
assert "cost_inc_gst" in quote
print(f"Total: ${quote['cost_inc_gst']:.2f}")
```

### **Test 2: All 5 Pacific Jobs**

```python
jobs = [
    {"name": "Job 1 - Main Report", "pages": 316},
    {"name": "Job 2 - Appendix A-H", "pages": 372},
    {"name": "Job 3 - Appendix I", "pages": 392},
    {"name": "Job 4 - Appendix J-L", "pages": 372},
    {"name": "Job 5 - Appendix M-Q", "pages": 360}
]

for job in jobs:
    quote = calculate_wire_bound_books_shopify(
        quantity=3,
        pages=job["pages"],
        size="A4",
        cover_stock="350GSM Satin",
        inner_stock="100GSM Uncoated"
    )
    print(f"{job['name']}: ${quote['cost_inc_gst']:.2f}")
```

## 📋 **Checklist**

- [ ] Create `shopify_calculator_wrappers.py`
- [ ] Implement `calculate_wire_bound_books_shopify()`
- [ ] Implement `calculate_spiral_bound_books_shopify()`
- [ ] Add to `get_calculator_requirements()`
- [ ] Add routing in `calculate_quote()`
- [ ] Test Pacific Partnerships specs
- [ ] Verify all 5 jobs calculate correctly
- [ ] Document wrapper approach

## 🎯 **Benefits**

1. ✅ **Simple for AI** - Only 5-6 parameters vs 13 F-parameters
2. ✅ **Backward compatible** - Matches old tool schema from commit 5e29923
3. ✅ **Easy natural language mapping** - "350GSM Satin" → understood directly
4. ✅ **Hides complexity** - F1-F14 mapping done internally
5. ✅ **Fast implementation** - ~200 lines of wrapper code

## 🚀 **Next Steps**

1. Create the wrapper module
2. Test with Pacific Partnerships
3. Complete all 5 wire bound quotes
4. Reply to customer with pricing

---

**Status:** 📋 **Plan Complete** - Ready to implement  
**Estimated Time:** 30-45 minutes  
**Priority:** 🔥 **CRITICAL** - Customer waiting
