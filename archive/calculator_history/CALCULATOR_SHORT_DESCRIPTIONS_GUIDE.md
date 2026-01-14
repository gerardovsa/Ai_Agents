# Calculator Short Descriptions Guide

## Overview
Short descriptions are used for **vectorized semantic search** to help AI agents quickly find the right calculator tool based on natural language queries.

## Location of Short Descriptions

### 1. Main Calculator Tools Schema
**Path:** `UI/modules_external/quote-calculator/schema/calculator_tools.json`

This file contains **ALL calculator schemas** including:
- 6 Core calculators (business_cards, booklets, perfect_bound_books, flyers, letterheads, corflute_signs)
- 5 Shopify calculators (economical_business_cards, premium_business_cards, folded_flyers, wire_bound_books, spiral_bound_books)
- 4 GOD variant calculators (*_god suffixed versions)
- 22+ Specialized calculators (bollard_signs, construction_signs, notepads, etc.)

**Total:** 37 calculator tool definitions

### 2. Shopify Product Configuration Files
**Path:** `UI/modules_external/quote-calculator/schema/shopify/`

These files define the Shopify product options/pricing but **do NOT have short_description fields** (yet):
```
Business_Cards_Economic.json
Premium_Business_Cards.json
folded_printed_flyers_Shopify.json
Wire_Spiral_Bound.json
Perfect_Bound_books.json
Corflute_Signs_Shopify.json
Printed_Flyers_Shopify.json
Perfect_Bound_Books_WooCommerce.json
```

These files have:
- `description` (long form product description)
- `product_title`
- `tags` (for categorization)

But they **currently lack** `short_description` fields.

## Schema Structure

### Current Format (calculator_tools.json)
```json
{
  "name": "calculate_economical_business_cards_shopify",
  "short_description": "Calculate economical business card quotes with budget-friendly stock and finishing options",
  "description": "Shopify calculator for Economical Business Cards - Hardcoded Shopify pricing (90x55mm, 300GSM Satin, single/double sided). Fast quotes matching website.",
  "platform": "quote_calculator",
  "parameters": { ... },
  "returns": { ... }
}
```

### What to Add to Shopify Files (Recommended)
```json
{
  "shopify_economical_business_cards": {
    "product_title": "Economical Business Cards",
    "product_type": "Business Cards",
    "short_description": "Budget-friendly business cards for small businesses - 300GSM satin stock, single or double-sided printing",
    "description": "Budget-friendly business cards with professional quality. Perfect for small businesses and startups looking for cost-effective branding solutions.",
    "vendor": "PrintShop",
    "tags": ["business-cards", "economical", "custom-printing", "single-double-sided"],
    ...
  }
}
```

## Files That Need Short Descriptions Added

### ✅ Already Have Short Descriptions (calculator_tools.json)
All 37 calculators in `calculator_tools.json` already have `short_description` fields.

### ⚠️ Need Short Descriptions Added (Shopify product files)
These 8 Shopify product configuration files need `short_description` added:

1. **Business_Cards_Economic.json**
   - Current: Only has long `description`
   - Add: `"short_description": "Budget-friendly business cards - 300GSM satin, single/double sided"`

2. **Premium_Business_Cards.json**
   - Add: `"short_description": "High-quality business cards - 400GSM satin, optional cellophane finish"`

3. **folded_printed_flyers_Shopify.json**
   - Add: `"short_description": "Folded promotional flyers - DL, A5, A4 sizes with various fold options"`

4. **Wire_Spiral_Bound.json**
   - Add: `"short_description": "Wire-o and spiral bound books - durable binding for manuals and notebooks"`

5. **Perfect_Bound_books.json**
   - Add: `"short_description": "Perfect bound books - glued spine for professional catalogs and magazines"`

6. **Corflute_Signs_Shopify.json**
   - Add: `"short_description": "Rigid corflute signs - lightweight plastic signage, indoor/outdoor use"`

7. **Printed_Flyers_Shopify.json**
   - Add: `"short_description": "Flat printed flyers - A6, DL, A5, A4 sizes for promotional materials"`

8. **Perfect_Bound_Books_WooCommerce.json**
   - Add: `"short_description": "WooCommerce perfect bound books - professional publications with glued binding"`

## Best Practices for Short Descriptions

### Format Guidelines
1. **Length:** 60-120 characters optimal (for embedding/search)
2. **Structure:** `[Product Type] - [Key Features] - [Use Case]`
3. **Keywords:** Include searchable terms users might say
4. **No Marketing Fluff:** Focus on technical specs that help search

### Good Examples
✅ `"Budget business cards - 300GSM satin stock, single or double-sided printing"`
✅ `"Rigid corflute signs - 3mm/5mm plastic, weatherproof, single/double sided"`
✅ `"Perfect bound books - glued spine, 40+ pages, professional catalogs"`

### Bad Examples
❌ `"The best business cards you'll ever see!"` (too marketing-focused)
❌ `"Cards"` (too short, no context)
❌ `"We offer premium quality business cards with exceptional service and fast turnaround"` (too long)

## Where AI Will Add Them

**Primary File:** `UI/modules_external/quote-calculator/schema/calculator_tools.json`
- This is the **single source of truth** for calculator schemas
- All 37 calculator definitions are here
- Short descriptions are already present

**Secondary Files:** Individual Shopify product JSONs in `schema/shopify/`
- These define product options/pricing
- Should have short_description added for consistency
- Insert after `product_type` and before `description`

## Vectorized Search Usage

When added, short descriptions enable:
1. **Semantic search** - AI can find calculators by intent ("I need cheap business cards")
2. **Tool selection** - Vector similarity helps choose right calculator
3. **Context relevance** - Better matching for complex queries

## Registry V3 Loading

The calculator schemas are loaded in this order:
1. `tools/registry_v3.py` loads from `UI/modules_external/quote-calculator/schema/`
2. `calculator_tools.json` is parsed first (has all tool definitions)
3. Shopify JSONs are reference files for product config (not directly loaded by registry)

**Result:** Short descriptions in `calculator_tools.json` are what matter most for AI tool discovery!

## Summary

**✅ Done:** All 37 calculators have short_description in `calculator_tools.json`

**📝 To Do:** Add short_description to 8 Shopify product config files for consistency

**📁 Primary File:** `UI/modules_external/quote-calculator/schema/calculator_tools.json` (2458 lines, all calculators)

**📁 Secondary Files:** Individual JSONs in `UI/modules_external/quote-calculator/schema/shopify/`

---

## For AI Assistant Adding Descriptions

When you add short descriptions to the Shopify files, use this format:

```json
{
  "shopify_product_name": {
    "product_title": "Product Title",
    "product_type": "Product Category",
    "short_description": "Concise 60-120 char description with key features and use case",
    "description": "Longer existing description...",
    ...
  }
}
```

Insert `short_description` after `product_type` and before the existing `description` field.

Focus on technical specs, materials, sizes, and typical use cases rather than marketing language.
