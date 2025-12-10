# Complete Shopify Calculator Implementation Plan
## December 10, 2025

## Overview
Systematically document all 26 Shopify calculators to make them discoverable and usable by AI agents.

## Implementation Strategy

### Phase 1: High-Priority Calculators (COMPLETED)
**Status: ✅ DONE**
1. Wire Bound Books ✅
2. Spiral Bound Books ✅

### Phase 2: Book & Binding Calculators (NEXT - 30 mins)
**Common customer requests for books/booklets**
3. Perfect Bound Books
4. Saddle Stitch Books  
5. Folded Flyers

### Phase 3: Business Stationery (20 mins)
**Frequent small business orders**
6. Economical Business Cards
7. Premium Business Cards
8. Printed Letterheads
9. With Compliments Slips
10. Notepads A4
11. Notepads A5 (already documented!)
12. Notepads A6

### Phase 4: Signs & Displays (30 mins)
**Commercial signage orders**
13. Election Signs
14. Construction Signs
15. Bollard Signs
16. Corflute Insert A-Frame
17. Metal Face A-Frame
18. Strut Cards A3
19. Strut Cards A4

### Phase 5: Promotional Items (20 mins)
**Marketing materials**
20. Custom Poster Printing
21. Custom Vinyl Stickers
22. Premium Bookmarks
23. Selfie Frames
24. Stackable Cubes
25. Luxury Classic Pull Up Banners

## For Each Calculator - Required Components

### 1. Wrapper Function (`shopify_calculator_wrappers.py`)
```python
def calculate_[product_name]_shopify(
    # Simple, AI-friendly parameters
    quantity: int,
    # ... other intuitive parameters
) -> Dict[str, Any]:
    """
    Clear docstring with examples
    """
    # Map simple → complex F1-F14
    # Call underlying calculator
    # Return standardized result
```

### 2. Requirements Documentation (`complete_calculator_implementation.py`)
```python
"product_name": {
    "description": "Clear product description",
    "calculator_type": "Shopify (CalculatorClass via wrapper)",
    "wrapper_function": "calculate_[product_name]_shopify",
    
    "required_parameters": {
        "param1": {
            "type": "int/string/enum",
            "description": "What it means",
            "validation": "Rules",
            "example": "Real example",
            "extraction_hints": [
                "How AI should parse from customer requests"
            ]
        }
    },
    
    "optional_parameters": { ... },
    "natural_language_mapping": { ... },
    "business_rules": { ... },
    "validation_rules": { ... }
}
```

### 3. Import Statement
```python
from shopify_calculators.ProductName_Shopify_Calculator import (
    ProductNameShopifyCalculator
)
```

## Current Status by Calculator

| # | Calculator | Wrapper | Documentation | Import | Status |
|---|------------|---------|---------------|--------|--------|
| 1 | WireBound | ✅ | ✅ | ✅ | **COMPLETE** |
| 2 | SpiralBound | ✅ | ✅ | ✅ | **COMPLETE** |
| 3 | PerfectBound | ❌ | ❌ | ❌ | TODO |
| 4 | SaddleStitch | ❌ | ❌ | ❌ | TODO |
| 5 | FoldedFlyers | ❌ | ❌ | ❌ | TODO |
| 6 | EconomicalBusinessCards | ❌ | ❌ | ❌ | TODO |
| 7 | PremiumBusinessCards | ❌ | ❌ | ❌ | TODO |
| 8 | PrintedLetterheads | ❌ | ❌ | ❌ | TODO |
| 9 | WithComplimentsSlips | ❌ | ❌ | ❌ | TODO |
| 10 | NotepadsA4 | ❌ | ❌ | ❌ | TODO |
| 11 | NotepadsA5 | ❌ | ✅ | ❌ | 33% |
| 12 | NotepadsA6 | ❌ | ❌ | ❌ | TODO |
| 13 | ElectionSigns | ❌ | ❌ | ❌ | TODO |
| 14 | ConstructionSigns | ❌ | ❌ | ❌ | TODO |
| 15 | BollardSigns | ❌ | ❌ | ❌ | TODO |
| 16 | CorfluteInsertAFrame | ❌ | ❌ | ❌ | TODO |
| 17 | MetalFaceAFrame | ❌ | ❌ | ❌ | TODO |
| 18 | StrutCardsA3 | ❌ | ❌ | ❌ | TODO |
| 19 | StrutCardsA4 | ❌ | ❌ | ❌ | TODO |
| 20 | CustomPosterPrinting | ❌ | ❌ | ❌ | TODO |
| 21 | CustomVinylStickers | ❌ | ❌ | ❌ | TODO |
| 22 | PremiumBookmarks | ❌ | ❌ | ❌ | TODO |
| 23 | SelfieFrames | ❌ | ❌ | ❌ | TODO |
| 24 | StackableCubes | ❌ | ❌ | ❌ | TODO |
| 25 | LuxuryPullUpBanners | ❌ | ❌ | ❌ | TODO |

**Progress: 2/25 (8%) Complete**

## Time Estimates

- **Per Calculator:** 12-15 minutes
  - Analyze parameters: 3 min
  - Create wrapper: 4 min
  - Write documentation: 5 min
  - Add import: 1 min

- **Phase 2 (3 calculators):** 45 minutes
- **Phase 3 (7 calculators):** 1.5 hours  
- **Phase 4 (7 calculators):** 1.5 hours
- **Phase 5 (6 calculators):** 1.5 hours

**Total Remaining: ~5 hours for all 23 calculators**

## Next Steps

### Immediate (Phase 2 - Books)
1. Read PerfectBound_Shopify_Calculator.py → understand parameters
2. Create `calculate_perfect_bound_books_shopify()` wrapper
3. Add "perfect_bound_books" to `get_calculator_requirements()`
4. Add import for PerfectBoundShopifyCalculator
5. Test with sample quote

Repeat for SaddleStitch and FoldedFlyers.

### Quality Checklist (Per Calculator)
- [ ] Wrapper has clear docstring with examples
- [ ] Parameters are intuitive (no F1-F14 exposure)
- [ ] Requirements include extraction hints
- [ ] Natural language mapping provided
- [ ] Real-world example included
- [ ] Validation rules documented
- [ ] Import statement added
- [ ] Calculator is searchable via `get_calculator_requirements()`

## Benefits When Complete

✅ **26 calculators** discoverable by AI
✅ **All products** quotable automatically  
✅ **Consistent interface** across all calculators
✅ **Natural language** parameter mapping
✅ **Example-driven** documentation
✅ **Validation** built-in

## Files to Modify

1. `inhouse_modules/shopify_calculator_wrappers.py` - Add 23 wrapper functions
2. `inhouse_modules/complete_calculator_implementation.py` - Add 23 requirement blocks + imports
3. Test file to verify all calculators work

## Implementation Order Rationale

**Phase 2 First (Books):**
- High customer demand
- Similar parameter structures (pages, covers, binding)
- Can reuse documentation patterns from Wire/Spiral

**Phase 3 Next (Stationery):**
- Frequent small business orders
- Simpler parameters than books
- High volume, quick quotes needed

**Phase 4 (Signs):**
- Commercial clients
- Larger order values
- Seasonal demand (elections)

**Phase 5 Last (Promotional):**
- Specialized items
- Lower frequency
- Can handle on-demand if needed

## Completion Target

**Goal:** All 23 remaining calculators documented by end of day
**Deliverable:** AI can quote ANY Shopify product automatically
**Success Metric:** `inhouse_get_calculator_requirements()` returns docs for all 26 products
