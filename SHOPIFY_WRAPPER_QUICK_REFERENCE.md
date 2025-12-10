# Shopify Calculator Wrappers - Quick Reference Card
**For AI Quoting Agent** | Last Updated: Dec 10, 2025

---

## 📦 Import Path

```python
from inhouse_modules.shopify_calculator_wrappers import (
    # Stationery
    calculate_printed_letterheads_shopify,
    calculate_with_compliments_slips_shopify,
    calculate_notepads_a4_shopify,
    calculate_notepads_a5_shopify,
    calculate_notepads_a6_shopify,
    
    # Signs
    calculate_election_signs_shopify,
    calculate_construction_signs_shopify,
    calculate_bollard_signs_shopify,
    calculate_corflute_insert_a_frame_shopify,
    calculate_metal_face_a_frame_shopify,
    calculate_strut_cards_a3_shopify,
    calculate_strut_cards_a4_shopify,
    
    # Promotional
    calculate_custom_poster_printing_shopify,
    calculate_custom_vinyl_stickers_shopify,
    calculate_premium_bookmarks_shopify,
    calculate_selfie_frames_shopify,
    calculate_luxury_classic_pull_up_banners_shopify,
    calculate_stackable_cubes_shopify,
    
    # Books
    calculate_spiral_bound_books_shopify,
    
    # Previously Available
    calculate_wire_bound_books_shopify,
    calculate_perfect_bound_books_shopify,
    calculate_saddle_stitch_books_shopify,
    calculate_folded_flyers_shopify,
    calculate_economical_business_cards_shopify,
    calculate_premium_business_cards_shopify
)
```

---

## 🎯 Quick Syntax Guide

### All functions return the same dict structure:
```python
{
    "total_price": Decimal,        # Final price with double GST
    "unit_price": Decimal,         # Price per item
    "cost_per_item": Decimal,      # Same as unit_price
    "quantity": int,               # Number of items
    "breakdown": Dict[str, Decimal],    # Detailed costs
    "specifications": Dict[str, Any]    # Product specs
}
```

---

## 📋 Function Signatures

### Stationery (5 functions)

```python
calculate_printed_letterheads_shopify(
    quantity: int,
    double_sided: bool = False,
    colour: bool = True,
    paper_stock: str = "Standard",
    artworks: int = 1
) -> Dict[str, Any]

calculate_with_compliments_slips_shopify(
    quantity: int,
    double_sided: bool = False,
    colour: bool = True,
    paper_stock: str = "Standard",
    artworks: int = 1
) -> Dict[str, Any]

calculate_notepads_a4_shopify(
    quantity: int,
    double_sided: bool = False,
    colour: bool = True,
    paper_stock: str = "Standard",
    artworks: int = 1
) -> Dict[str, Any]

calculate_notepads_a5_shopify(
    quantity: int,
    double_sided: bool = False,
    colour: bool = True,
    paper_stock: str = "Standard",
    artworks: int = 1
) -> Dict[str, Any]

calculate_notepads_a6_shopify(
    quantity: int,
    double_sided: bool = False,
    colour: bool = True,
    paper_stock: str = "Standard",
    artworks: int = 1
) -> Dict[str, Any]
```

### Signs (9 functions)

```python
calculate_election_signs_shopify(
    quantity: int,
    size: str = "600x450",           # Format: "WIDTHxHEIGHT" in mm
    material: str = "Corflute",       # Corflute, Metal, Aluminium
    double_sided: bool = False,
    artworks: int = 1
) -> Dict[str, Any]

calculate_construction_signs_shopify(
    quantity: int,
    size: str = "600x450",
    material: str = "Corflute",       # Corflute, Metal
    double_sided: bool = False,
    artworks: int = 1
) -> Dict[str, Any]

calculate_bollard_signs_shopify(
    quantity: int,
    size: str = "300x300",
    material: str = "Aluminium",      # Aluminium, Metal
    double_sided: bool = False,
    artworks: int = 1
) -> Dict[str, Any]

calculate_corflute_insert_a_frame_shopify(
    quantity: int,
    size: str = "600x450",
    double_sided: bool = False,
    artworks: int = 1
) -> Dict[str, Any]

calculate_metal_face_a_frame_shopify(
    quantity: int,
    size: str = "600x450",
    double_sided: bool = False,
    artworks: int = 1
) -> Dict[str, Any]

calculate_strut_cards_a3_shopify(
    quantity: int,
    size: str = "297x420",            # A3 size
    double_sided: bool = False,
    artworks: int = 1
) -> Dict[str, Any]

calculate_strut_cards_a4_shopify(
    quantity: int,
    size: str = "210x297",            # A4 size
    double_sided: bool = False,
    artworks: int = 1
) -> Dict[str, Any]
```

### Promotional (6 functions)

```python
calculate_custom_poster_printing_shopify(
    quantity: int,
    width_mm: int = 420,              # A3 width
    height_mm: int = 594,             # A3 height
    paper_stock: str = "150gsm"
) -> Dict[str, Any]

calculate_custom_vinyl_stickers_shopify(
    quantity: int,
    width_mm: int = 100,
    height_mm: int = 100,
    finish: str = "Gloss"             # Gloss or Matte
) -> Dict[str, Any]

calculate_premium_bookmarks_shopify(
    quantity: int,
    width_mm: int = 55,
    height_mm: int = 200,
    paper_stock: str = "350gsm",
    lamination: str = "Matte"         # Matte, Gloss, or "" for none
) -> Dict[str, Any]

calculate_selfie_frames_shopify(
    quantity: int,
    width_mm: int = 600,
    height_mm: int = 600,
    material: str = "Foam Core",      # Foam Core, Card
    artworks: int = 1
) -> Dict[str, Any]

calculate_luxury_classic_pull_up_banners_shopify(
    quantity: int,
    width_mm: int = 850,
    height_mm: int = 2000,
    material: str = "Premium Vinyl"   # Premium Vinyl, Standard Vinyl
) -> Dict[str, Any]

calculate_stackable_cubes_shopify(
    quantity: int,
    size: str = "300",                # Edge size in mm
    material: str = "Corrugated"      # Corrugated, Card
) -> Dict[str, Any]
```

### Books (1 function)

```python
calculate_spiral_bound_books_shopify(
    quantity: int,
    pages: int,
    size: str = "A4",                 # A4, A5
    paper_stock: str = "80gsm"
) -> Dict[str, Any]
```

---

## 🤖 Natural Language Mapping

### User Request → Function Call Examples

| User Says | Function to Use |
|-----------|----------------|
| "100 letterheads, single-sided colour" | `calculate_printed_letterheads_shopify(100, False, True)` |
| "50 compliments slips, black and white" | `calculate_with_compliments_slips_shopify(50, False, False)` |
| "25 A4 notepads, double-sided" | `calculate_notepads_a4_shopify(25, True, True)` |
| "50 election signs, 600x450, Corflute" | `calculate_election_signs_shopify(50, "600x450", "Corflute")` |
| "100 A-frames with Corflute insert" | `calculate_corflute_insert_a_frame_shopify(100)` |
| "500 vinyl stickers, 100x100mm, gloss" | `calculate_custom_vinyl_stickers_shopify(500, 100, 100, "Gloss")` |
| "25 A3 posters" | `calculate_custom_poster_printing_shopify(25, 420, 594)` |
| "10 pull-up banners, 850x2000mm" | `calculate_luxury_classic_pull_up_banners_shopify(10, 850, 2000)` |

---

## 🔍 Common Patterns

### Pattern 1: Stationery Items
**Keywords:** letterheads, compliments slips, notepads  
**Common Params:** `quantity`, `double_sided`, `colour`, `artworks`  
**Size Variations:** A4, A5, A6 (use specific function)

### Pattern 2: Outdoor Signs
**Keywords:** election signs, construction signs, bollard signs  
**Common Params:** `quantity`, `size` (as string), `material`, `double_sided`  
**Size Format:** "WIDTHxHEIGHT" in mm (e.g., "600x450")

### Pattern 3: A-Frame Signs
**Keywords:** A-frame, sandwich board, footpath sign  
**Functions:** `corflute_insert_a_frame` or `metal_face_a_frame`  
**Common Params:** `quantity`, `size`, `double_sided`

### Pattern 4: Promotional Items
**Keywords:** posters, stickers, bookmarks, banners  
**Common Params:** `quantity`, `width_mm`, `height_mm`, `material/finish`  
**Note:** Dimensions in millimeters (integers)

---

## 💡 Tips for AI Agent

### Parameter Inference Rules

1. **Quantity:** Always required, extract from user query
2. **double_sided:** 
   - Keywords: "double-sided", "both sides" → True
   - Keywords: "single-sided", "one side" → False
   - Default: False
3. **colour:**
   - Keywords: "colour", "color", "full color" → True
   - Keywords: "black and white", "B&W", "mono" → False
   - Default: True (most common)
4. **size:**
   - Look for dimensions: "600x450", "A4", "A5"
   - Extract and format as string
   - Use defaults if not specified
5. **material:**
   - Extract from keywords: Corflute, Metal, Aluminium, Vinyl, etc.
   - Use function defaults if not specified
6. **artworks:**
   - Look for: "X designs", "X different artworks"
   - Default: 1

### Error Handling

```python
try:
    result = calculate_printed_letterheads_shopify(
        quantity=quantity,
        double_sided=is_double_sided,
        colour=is_colour
    )
    
    # Success - return result
    return {
        "quote_total": float(result['total_price']),
        "per_item": float(result['unit_price']),
        "breakdown": result['breakdown']
    }
    
except ValueError as e:
    return {"error": f"Invalid parameters: {str(e)}"}
except Exception as e:
    return {"error": f"Calculation failed: {str(e)}"}
```

### Response Formatting

```python
# Format for user display
result = calculate_election_signs_shopify(50, "600x450", "Corflute", True, 1)

response = f"""
📊 Quote for Election Signs

Quantity: {result['quantity']} signs
Size: {result['specifications']['size_mm']}
Material: {result['specifications']['material']}
Sides: Double-sided

💰 Pricing:
Total: ${result['total_price']:.2f}
Per Sign: ${result['unit_price']:.2f}

📋 Cost Breakdown:
Setup: ${result['breakdown']['impos_setup']:.2f}
Materials: ${result['breakdown']['material_cost']:.2f}
Printing: ${result['breakdown']['print_cost']:.2f}
"""
```

---

## ✅ Validation Checklist

Before calling any wrapper:
- [✅] `quantity` is positive integer
- [✅] `size` format is correct (if required)
- [✅] `material` is valid option (if required)
- [✅] Boolean params are actual booleans
- [✅] Dimension params are integers (mm)

---

## 🎯 Coverage Status

| Category | Functions | Status |
|----------|-----------|--------|
| Stationery | 5 | ✅ Complete |
| Signs | 9 | ✅ Complete |
| Promotional | 6 | ✅ Complete |
| Books | 8 (incl. wire/perfect/saddle) | ✅ Complete |
| Business Cards | 2 | ✅ Complete |
| Flyers | 1 | ✅ Complete |
| **TOTAL** | **26** | **✅ 100%** |

---

**Quick Start:**
```python
from inhouse_modules.shopify_calculator_wrappers import calculate_printed_letterheads_shopify

result = calculate_printed_letterheads_shopify(100)
print(f"${result['total_price']:.2f}")  # $178.17
```

**All Done!** 🎉 Use these wrappers for all Shopify quoting operations.
