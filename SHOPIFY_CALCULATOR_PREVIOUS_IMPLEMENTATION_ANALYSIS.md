# Shopify Calculator Previous Implementation Analysis

**Date:** December 10, 2025  
**Source:** Git commit `5e29923` and `66563e0`  
**Location:** `UI/modules_external/quote-calculator/schema/calculator_tools.json`

## 🎯 **DISCOVERY: Previous Implementation Found!**

### **What Previously Existed**

In older commits, there WAS a complete implementation of Shopify calculator tool schemas:

## 📋 **Previous Tool Names (With `_shopify` Suffix)**

### **1. `calculate_wire_bound_books_shopify`**

```json
{
  "name": "calculate_wire_bound_books_shopify",
  "description": "Shopify calculator for Wire Bound Books - Hardcoded Shopify pricing (wire-o binding, A4/A5, multiple page counts). Fast quotes matching website.",
  "platform": "quote_calculator",
  "parameters": {
    "type": "object",
    "properties": {
      "quantity": {
        "type": "integer",
        "description": "Number of books (Shopify quantities)"
      },
      "pages": {
        "type": "integer",
        "description": "Total page count (must be divisible by 4)"
      },
      "size": {
        "type": "string",
        "enum": ["A4", "A5"],
        "description": "Book size"
      },
      "cover_stock": {
        "type": "string",
        "description": "Cover paper stock"
      },
      "inner_stock": {
        "type": "string",
        "description": "Inner pages paper stock"
      },
      "cover_cellophane": {
        "type": "string",
        "enum": ["No Cellophane", "Gloss Cellophane", "Matt Cellophane"],
        "description": "Cover cellophane option (default: No Cellophane)"
      }
    },
    "required": ["quantity", "pages", "size", "cover_stock", "inner_stock"]
  }
}
```

### **2. `calculate_spiral_bound_books_shopify`**

```json
{
  "name": "calculate_spiral_bound_books_shopify",
  "description": "Shopify calculator for Spiral Bound Books - Hardcoded Shopify pricing (plastic coil binding, A4/A5, multiple page counts). Fast quotes matching website.",
  "platform": "quote_calculator",
  "parameters": {
    "type": "object",
    "properties": {
      "quantity": {
        "type": "integer",
        "description": "Number of books (Shopify quantities)"
      },
      "pages": {
        "type": "integer",
        "description": "Total page count (must be divisible by 4)"
      },
      "size": {
        "type": "string",
        "enum": ["A4", "A5"],
        "description": "Book size"
      },
      "cover_stock": {
        "type": "string",
        "description": "Cover paper stock"
      },
      "inner_stock": {
        "type": "string",
        "description": "Inner pages paper stock"
      },
      "cover_cellophane": {
        "type": "string",
        "enum": ["No Cellophane", "Gloss Cellophane", "Matt Cellophane"],
        "description": "Cover cellophane option"
      }
    },
    "required": ["quantity", "pages", "size", "cover_stock", "inner_stock"]
  }
}
```

### **3. `calculate_folded_flyers_shopify`**

```json
{
  "name": "calculate_folded_flyers_shopify",
  "description": "Shopify calculator for Folded Flyers - Hardcoded Shopify pricing",
  "parameters": {
    "quantity": "integer",
    "size": "enum [A4, A5, DL]",
    "paper_stock": "string (e.g., '150GSM Gloss Art', '300GSM Gloss Art')",
    "print_sides": "enum [Single side print, Double side print]",
    "folding": "enum [No Folding, Half Fold, Z Fold, Gate Fold]"
  },
  "required": ["quantity", "size", "paper_stock", "print_sides"]
}
```

## 🔍 **Key Differences: Old vs New Implementation**

| Aspect | Old Implementation (commit 5e29923) | Current v10 | F1-F14 Shopify Params |
|--------|--------------------------------------|-------------|----------------------|
| **Tool Name** | `calculate_wire_bound_books_shopify` | ❓ Unknown | Should be `shopify_wire_bound` |
| **Parameter Style** | **Simplified** (quantity, pages, size, cover_stock, inner_stock) | ❓ Unknown | **Complex** (F1-F14: artworks, finish_size, outer_front_cover, etc.) |
| **Size Format** | `"A4"` or `"A5"` (simple strings) | ❓ Unknown | `"A4 Portrait"` or `"A5 Landscape"` (orientation included) |
| **Cover Stock** | Single param: `"cover_stock"` | ❓ Unknown | Multiple: `outer_front_cover`, `printed_front_cover`, `front_cover_print` |
| **Cellophane** | Single param: `"cover_cellophane"` | ❓ Unknown | Multiple: `front_celloglaze`, `back_celloglaze` |

## 🚨 **CRITICAL DISCOVERY**

### **The Old Implementation Was SIMPLER!**

The old Shopify calculator tools used **simplified parameters**, NOT the complex F1-F14 structure!

**Old Approach:**
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

**Current WireBoundShopifyCalculator F1-F14 Approach:**
```python
WireBoundShopifyCalculator.calculate(
    quantity=3,                              # F1
    artworks=1,                              # F2
    finish_size="A4 Portrait",               # F14
    outer_front_cover="Clear PVC",           # F3
    printed_front_cover="350GSM Satin",      # F4
    front_cover_print="2pp Colour",          # F5
    front_celloglaze="None",                 # F6
    outer_back_cover="350GSM Satin Blank Card", # F7
    printed_back_cover="None",               # F8
    back_cover_print="None",                 # F9
    back_celloglaze="None",                  # F10
    internal_pages=316,                      # F11
    internal_stock="Uncoated Bond 100GSM",   # F12
    internal_print="Full Colour"             # F13
)
```

## 📊 **Comparison Table**

| Parameter | Old Shopify Tool | Current Shopify Calculator (F1-F14) |
|-----------|------------------|-------------------------------------|
| **Quantity** | `quantity` (int) | `quantity` (F1, int) ✅ Same |
| **Pages** | `pages` (int) | `internal_pages` (F11, int) ⚠️ Different name |
| **Size** | `size` ("A4", "A5") | `finish_size` (F14, "A4 Portrait", "A5 Landscape") ⚠️ More complex |
| **Cover Stock** | `cover_stock` (string) | Split into F3+F4+F5+F6 (4 params!) ⚠️ Much more complex |
| **Inner Stock** | `inner_stock` (string) | `internal_stock` (F12) + `internal_print` (F13) ⚠️ Split |
| **Cellophane** | `cover_cellophane` (single) | `front_celloglaze` (F6) + `back_celloglaze` (F10) ⚠️ Split |

## 🎯 **The Problem**

### **Two Conflicting Implementations:**

1. **Old Wrapper Tools** (commit 5e29923):
   - Simple parameters
   - Easy for AI to understand
   - Mapped to Shopify calculator internally
   - **Tool name:** `calculate_wire_bound_books_shopify`

2. **Current Shopify Calculators** (WireBoundShopifyCalculator.py):
   - Complex F1-F14 parameters
   - Exact WooCommerce DPO field structure
   - More flexible but harder to use
   - **No documented tool wrapper**

## ✅ **Solution Options**

### **Option 1: Restore Old Wrapper Style (RECOMMENDED)**

Create simple wrapper tools that match the old schema:

```python
def calculate_wire_bound_books_shopify(
    quantity: int,
    pages: int,
    size: str,  # "A4" or "A5"
    cover_stock: str,
    inner_stock: str,
    cover_cellophane: str = "No Cellophane"
) -> Dict[str, Any]:
    """
    Simplified Shopify wire bound calculator
    Maps simple parameters to F1-F14 internally
    """
    # Map simple params to F1-F14
    finish_size = f"{size} Portrait"  # A4 → A4 Portrait
    
    # Parse cover_stock
    # "350GSM Satin" → printed_front_cover="350GSM Satin"
    
    # Parse inner_stock
    # "100GSM Uncoated" → internal_stock="Uncoated Bond 100GSM"
    
    # Map cellophane
    # "Gloss Cellophane" → front_celloglaze="2 Sided Gloss"
    
    # Call actual calculator
    calc = WireBoundShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        internal_pages=pages,
        finish_size=finish_size,
        printed_front_cover=mapped_cover,
        internal_stock=mapped_inner,
        front_celloglaze=mapped_cello,
        # ... other F1-F14 params with sensible defaults
    )
    return result
```

### **Option 2: Document F1-F14 Parameters**

Add comprehensive documentation for all F1-F14 parameters (what we created in previous docs).

## 🚦 **Recommendation**

**Use Option 1 (Restore Wrapper Style)** because:

1. ✅ **Backward compatible** with old tool schema
2. ✅ **AI-friendly** - simple parameters easy to understand
3. ✅ **Pacific Partnerships spec** maps cleanly:
   - `quantity=3`
   - `pages=316`
   - `size="A4"`
   - `cover_stock="350GSM Satin"`
   - `inner_stock="100GSM Uncoated"`
   - `cover_cellophane="No Cellophane"`
4. ✅ **Wrapper handles complexity** - maps to F1-F14 internally
5. ✅ **Faster implementation** - less documentation needed

## 📝 **Implementation Plan**

### **Step 1: Create Wrapper Functions**

File: `inhouse_modules/shopify_calculator_wrappers.py`

```python
def calculate_wire_bound_books_shopify(quantity, pages, size, cover_stock, inner_stock, cover_cellophane="No Cellophane"):
    """Simple wrapper for WireBoundShopifyCalculator"""
    # Mapping logic here
    pass

def calculate_spiral_bound_books_shopify(quantity, pages, size, cover_stock, inner_stock, cover_cellophane="No Cellophane"):
    """Simple wrapper for SpiralBoundShopifyCalculator"""
    # Mapping logic here
    pass
```

### **Step 2: Add to Calculator Requirements**

```python
requirements = {
    # ... existing GOD calculators ...
    
    "calculate_wire_bound_books_shopify": {
        "description": "Wire Bound Books - Shopify pricing",
        "parameters": {
            "quantity": {"type": "int"},
            "pages": {"type": "int"},
            "size": {"enum": ["A4", "A5"]},
            "cover_stock": {"type": "string"},
            "inner_stock": {"type": "string"},
            "cover_cellophane": {"enum": ["No Cellophane", "Gloss Cellophane", "Matt Cellophane"]}
        }
    }
}
```

### **Step 3: Test Pacific Partnerships**

```python
quote = calculate_wire_bound_books_shopify(
    quantity=3,
    pages=316,
    size="A4",
    cover_stock="350GSM Satin",
    inner_stock="100GSM Uncoated",
    cover_cellophane="No Cellophane"
)
```

## 📋 **Summary**

- ✅ **Found** previous implementation with simplified parameters
- ✅ **Identified** conflict between old wrappers and new F1-F14 calculators  
- ✅ **Recommended** restoring simplified wrapper style
- ⏭️ **Next:** Implement wrapper functions and test

---

**Status:** ✅ Analysis Complete - Previous implementation discovered  
**Next Action:** Implement simplified wrappers for Shopify calculators  
**Priority:** 🔥 HIGH - Needed for Pacific Partnerships wire bound quotes
