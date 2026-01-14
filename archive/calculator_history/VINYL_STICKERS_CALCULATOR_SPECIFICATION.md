# 🎨 Custom Vinyl Stickers Calculator - Complete Specification

**Document Version:** 1.0  
**Created:** November 13, 2025  
**Pricing Model:** Square Meter-Based with Material/Finish Multipliers  
**Status:** Design Specification - Ready for Implementation

---

## 📋 Executive Summary

This calculator uses a **sophisticated square meter-based pricing model** (similar to Custom Poster Printing) combined with material/finish multipliers and cutting cost structures. It provides professional vinyl sticker pricing for quantities from 1 to 10,000+ units across various sizes, materials, finishes, and cutting methods.

### Key Features:
- ✅ Square meter-based pricing (51 pricing tiers for efficiency at scale)
- ✅ Material-specific rate tables (Standard, Premium, Clear, Removable vinyl)
- ✅ Finish multipliers (Gloss, Matte, Gloss Laminated, Matte Laminated)
- ✅ Shape/cutting cost structure (Kiss-cut, Die-cut, Contour-cut)
- ✅ Predefined sizes + custom dimensions support
- ✅ Artwork setup fees (first included, additional $5 each)
- ✅ Minimum order enforcement ($45 + $10 handling)
- ✅ Conditional field visibility (custom dimensions, artwork limits)

---

## 🎯 Product Information

### Basic Details
```json
{
  "product_title": "Custom Vinyl Stickers",
  "product_type": "Vinyl Stickers",
  "vendor": "PrintShop",
  "tags": ["stickers", "vinyl", "custom", "adhesive", "waterproof", "decals", "labels"],
  "description": "Premium custom vinyl stickers with professional square meter-based pricing. Choose from standard or premium vinyl materials, multiple finishes including lamination, and various cutting options. Perfect for branding, product labels, promotional giveaways, and outdoor applications."
}
```

### Applications
- Product packaging and labels
- Brand promotion and marketing
- Vehicle decals and signage
- Laptop and water bottle stickers
- Indoor/outdoor promotional materials
- Event merchandising
- Warning and safety labels
- Decorative wall decals

---

## 🔧 Input Fields Configuration

### Field 1: Quantity
```json
{
  "name": "Quantity",
  "field_id": "F1",
  "type": "number",
  "required": true,
  "default": 100,
  "min": 1,
  "max": 10000,
  "description": "Number of vinyl stickers required",
  "visibility": "Always visible"
}
```

### Field 2: Size (Predefined + Custom)
```json
{
  "name": "Size",
  "field_id": "F2",
  "type": "select",
  "required": true,
  "default": "75mm Circle",
  "options": [
    {
      "title": "50mm Circle",
      "dimensions": {"width": 50, "height": 50},
      "description": "Small circular sticker - 50mm diameter"
    },
    {
      "title": "75mm Circle",
      "dimensions": {"width": 75, "height": 75},
      "description": "Medium circular sticker - 75mm diameter"
    },
    {
      "title": "100mm Circle",
      "dimensions": {"width": 100, "height": 100},
      "description": "Large circular sticker - 100mm diameter"
    },
    {
      "title": "50mm Square",
      "dimensions": {"width": 50, "height": 50},
      "description": "Small square sticker - 50mm × 50mm"
    },
    {
      "title": "75mm Square",
      "dimensions": {"width": 75, "height": 75},
      "description": "Medium square sticker - 75mm × 75mm"
    },
    {
      "title": "100mm Square",
      "dimensions": {"width": 100, "height": 100},
      "description": "Large square sticker - 100mm × 100mm"
    },
    {
      "title": "75mm × 50mm Rectangle",
      "dimensions": {"width": 75, "height": 50},
      "description": "Rectangular sticker - 75mm × 50mm"
    },
    {
      "title": "100mm × 75mm Rectangle",
      "dimensions": {"width": 100, "height": 75},
      "description": "Rectangular sticker - 100mm × 75mm"
    },
    {
      "title": "150mm × 100mm Rectangle",
      "dimensions": {"width": 150, "height": 100},
      "description": "Large rectangular sticker - 150mm × 100mm"
    },
    {
      "title": "Custom Size",
      "description": "Custom dimensions - specify width and height"
    }
  ]
}
```

### Field 3: Width (mm) - Conditional
```json
{
  "name": "Width (mm)",
  "field_id": "F3",
  "type": "number",
  "required": true,
  "default": 75,
  "min": 25,
  "max": 500,
  "description": "Custom width in millimeters",
  "visibility": {
    "make_it": "Visible",
    "if": "(F2 == 'Custom Size')",
    "description": "Width field only visible when Custom Size is selected"
  }
}
```

### Field 4: Height (mm) - Conditional
```json
{
  "name": "Height (mm)",
  "field_id": "F4",
  "type": "number",
  "required": true,
  "default": 75,
  "min": 25,
  "max": 500,
  "description": "Custom height in millimeters",
  "visibility": {
    "make_it": "Visible",
    "if": "(F2 == 'Custom Size')",
    "description": "Height field only visible when Custom Size is selected"
  }
}
```

### Field 5: Vinyl Material
```json
{
  "name": "Vinyl Material",
  "field_id": "F5",
  "type": "select",
  "required": true,
  "default": "Standard Vinyl",
  "options": [
    {
      "title": "Standard Vinyl",
      "rate_multiplier": 1.0,
      "description": "High-quality white vinyl - indoor/outdoor use (3-5 year durability)"
    },
    {
      "title": "Premium Vinyl",
      "rate_multiplier": 1.25,
      "description": "Enhanced durability vinyl - 5-7 year outdoor life (+25%)"
    },
    {
      "title": "Clear Vinyl",
      "rate_multiplier": 1.35,
      "description": "Transparent vinyl - see-through effect (+35%)"
    },
    {
      "title": "Removable Vinyl",
      "rate_multiplier": 1.15,
      "description": "Easy-remove adhesive - ideal for temporary applications (+15%)"
    }
  ]
}
```

### Field 6: Finish
```json
{
  "name": "Finish",
  "field_id": "F6",
  "type": "select",
  "required": true,
  "default": "Gloss",
  "options": [
    {
      "title": "Gloss",
      "finish_multiplier": 1.0,
      "description": "Standard glossy finish - vibrant colors"
    },
    {
      "title": "Matte",
      "finish_multiplier": 1.08,
      "description": "Non-reflective matte finish - sophisticated look (+8%)"
    },
    {
      "title": "Gloss Laminated",
      "finish_multiplier": 1.25,
      "description": "Gloss with protective laminate - UV resistant, scratch-proof (+25%)"
    },
    {
      "title": "Matte Laminated",
      "finish_multiplier": 1.30,
      "description": "Matte with protective laminate - premium durability (+30%)"
    }
  ]
}
```

### Field 7: Cutting Method
```json
{
  "name": "Cutting Method",
  "field_id": "F7",
  "type": "select",
  "required": true,
  "default": "Kiss-Cut (Individual Stickers)",
  "options": [
    {
      "title": "Kiss-Cut (Individual Stickers)",
      "setup_fee": 0,
      "per_sticker_cost": 0.05,
      "description": "Cut through vinyl only, leaving backing - easy peel individual stickers"
    },
    {
      "title": "Die-Cut (No Background)",
      "setup_fee": 15,
      "per_sticker_cost": 0.08,
      "description": "Precision cut to shape with no background - professional look (+$15 setup)"
    },
    {
      "title": "Contour-Cut (Custom Shapes)",
      "setup_fee": 25,
      "per_sticker_cost": 0.12,
      "description": "Complex custom shape cutting - intricate designs (+$25 setup)"
    },
    {
      "title": "Sheet (Uncut Grid)",
      "setup_fee": 0,
      "per_sticker_cost": 0,
      "description": "Stickers printed on sheet without individual cutting - lowest cost"
    }
  ]
}
```

### Field 8: Artworks - Conditional
```json
{
  "name": "Artworks",
  "field_id": "F8",
  "type": "number",
  "required": true,
  "default": 1,
  "min": 1,
  "max": 20,
  "description": "Number of different artwork designs (first artwork included, additional at $5 each)",
  "visibility": {
    "make_it": "Visible",
    "if": "(F1 < '100')",
    "description": "Artworks field only visible when quantity is less than 100"
  }
}
```

---

## 💰 Pricing Structure

### Square Meter-Based Rate Tables (51 Tiers)

#### Standard Vinyl Base Rates
```json
"standard_vinyl_rates": [
  {"sqm_max": 0.01, "rate": 950, "description": "Under 0.01 sqm (very small stickers)"},
  {"sqm_max": 0.02, "rate": 475, "description": "0.01-0.02 sqm"},
  {"sqm_max": 0.03, "rate": 317, "description": "0.02-0.03 sqm"},
  {"sqm_max": 0.05, "rate": 190, "description": "0.03-0.05 sqm"},
  {"sqm_max": 0.08, "rate": 119, "description": "0.05-0.08 sqm"},
  {"sqm_max": 0.1, "rate": 95, "description": "0.08-0.1 sqm"},
  {"sqm_max": 0.15, "rate": 73, "description": "0.1-0.15 sqm"},
  {"sqm_max": 0.2, "rate": 60, "description": "0.15-0.2 sqm"},
  {"sqm_max": 0.25, "rate": 52, "description": "0.2-0.25 sqm"},
  {"sqm_max": 0.3, "rate": 47, "description": "0.25-0.3 sqm"},
  {"sqm_max": 0.4, "rate": 42, "description": "0.3-0.4 sqm"},
  {"sqm_max": 0.5, "rate": 38, "description": "0.4-0.5 sqm"},
  {"sqm_max": 0.6, "rate": 35, "description": "0.5-0.6 sqm"},
  {"sqm_max": 0.7, "rate": 33, "description": "0.6-0.7 sqm"},
  {"sqm_max": 0.8, "rate": 31.5, "description": "0.7-0.8 sqm"},
  {"sqm_max": 0.9, "rate": 30.2, "description": "0.8-0.9 sqm"},
  {"sqm_max": 1, "rate": 29, "description": "0.9-1 sqm"},
  {"sqm_max": 1.25, "rate": 27.5, "description": "1-1.25 sqm"},
  {"sqm_max": 1.5, "rate": 26.3, "description": "1.25-1.5 sqm"},
  {"sqm_max": 1.75, "rate": 25.4, "description": "1.5-1.75 sqm"},
  {"sqm_max": 2, "rate": 24.5, "description": "1.75-2 sqm"},
  {"sqm_max": 2.5, "rate": 23.2, "description": "2-2.5 sqm"},
  {"sqm_max": 3, "rate": 22.3, "description": "2.5-3 sqm"},
  {"sqm_max": 3.5, "rate": 21.6, "description": "3-3.5 sqm"},
  {"sqm_max": 4, "rate": 21, "description": "3.5-4 sqm"},
  {"sqm_max": 4.5, "rate": 20.5, "description": "4-4.5 sqm"},
  {"sqm_max": 5, "rate": 20, "description": "4.5-5 sqm"},
  {"sqm_max": 6, "rate": 19.3, "description": "5-6 sqm"},
  {"sqm_max": 7, "rate": 18.8, "description": "6-7 sqm"},
  {"sqm_max": 8, "rate": 18.4, "description": "7-8 sqm"},
  {"sqm_max": 9, "rate": 18.1, "description": "8-9 sqm"},
  {"sqm_max": 10, "rate": 17.8, "description": "9-10 sqm"},
  {"sqm_max": 12, "rate": 17.4, "description": "10-12 sqm"},
  {"sqm_max": 14, "rate": 17.1, "description": "12-14 sqm"},
  {"sqm_max": 16, "rate": 16.9, "description": "14-16 sqm"},
  {"sqm_max": 18, "rate": 16.7, "description": "16-18 sqm"},
  {"sqm_max": 20, "rate": 16.5, "description": "18-20 sqm"},
  {"sqm_max": 25, "rate": 16.2, "description": "20-25 sqm"},
  {"sqm_max": 30, "rate": 16, "description": "25-30 sqm"},
  {"sqm_max": 35, "rate": 15.8, "description": "30-35 sqm"},
  {"sqm_max": 40, "rate": 15.6, "description": "35-40 sqm"},
  {"sqm_max": 45, "rate": 15.5, "description": "40-45 sqm"},
  {"sqm_max": 50, "rate": 15.4, "description": "45-50 sqm"},
  {"sqm_max": 60, "rate": 15.2, "description": "50-60 sqm"},
  {"sqm_max": 70, "rate": 15.1, "description": "60-70 sqm"},
  {"sqm_max": 80, "rate": 15, "description": "70-80 sqm"},
  {"sqm_max": 90, "rate": 14.9, "description": "80-90 sqm"},
  {"sqm_max": 100, "rate": 14.8, "description": "90-100 sqm"},
  {"sqm_max": 150, "rate": 14.5, "description": "100-150 sqm"},
  {"sqm_max": 200, "rate": 14.3, "description": "150-200 sqm"},
  {"sqm_max": 999999, "rate": 14, "description": "200+ sqm (bulk orders)"}
]
```

**Note:** Premium Vinyl, Clear Vinyl, and Removable Vinyl use the same sqm tier structure but with their respective material multipliers applied (1.25×, 1.35×, 1.15×).

### Material Multipliers
```json
"material_multipliers": {
  "standard_vinyl": 1.0,
  "premium_vinyl": 1.25,
  "clear_vinyl": 1.35,
  "removable_vinyl": 1.15
}
```

### Finish Multipliers
```json
"finish_multipliers": {
  "gloss": 1.0,
  "matte": 1.08,
  "gloss_laminated": 1.25,
  "matte_laminated": 1.30
}
```

### Cutting Costs
```json
"cutting_costs": {
  "kiss_cut": {
    "setup_fee": 0,
    "per_sticker_cost": 0.05,
    "description": "Individual stickers on backing"
  },
  "die_cut": {
    "setup_fee": 15,
    "per_sticker_cost": 0.08,
    "description": "Cut to shape, no background"
  },
  "contour_cut": {
    "setup_fee": 25,
    "per_sticker_cost": 0.12,
    "description": "Complex custom shapes"
  },
  "sheet_uncut": {
    "setup_fee": 0,
    "per_sticker_cost": 0,
    "description": "Uncut sheet grid"
  }
}
```

### Artwork Fees
```json
"artwork_pricing": {
  "base_cost": 5,
  "first_artwork_free": true,
  "additional_cost": 5,
  "formula": "_a = artworks * 5, IF _a <= 5 THEN 0 ELSE (_a - 5)"
}
```

### Minimum Order Rule
```json
"minimum_order": {
  "minimum_value": 45,
  "handling_fee": 10,
  "description": "Orders under $45 are charged minimum $45 + $10 handling fee",
  "formula": "IF total < 45 THEN price = 45 + 10 ELSE price = total + 10"
}
```

### GST Calculation
```json
"gst": {
  "rate": 1.1,
  "description": "10% GST (Australia)"
}
```

---

## 🧮 Calculation Formula (Step-by-Step)

### Complete Calculation Logic
```
STEP 1: Calculate Artwork Cost
─────────────────────────────────
_artwork_total = artworks × 5
IF _artwork_total <= 5 THEN
    artwork_cost = 0
ELSE
    artwork_cost = _artwork_total - 5
END IF

STEP 2: Determine Dimensions
─────────────────────────────────
IF size == "Custom Size" THEN
    width = F3 (custom width)
    height = F4 (custom height)
ELSE
    width = predefined_width (from size option)
    height = predefined_height (from size option)
END IF

STEP 3: Calculate Total Square Meters
─────────────────────────────────
sqm_per_sticker = (width × height) / 1,000,000
total_sqm = sqm_per_sticker × quantity

STEP 4: Determine Base Rate per SQM
─────────────────────────────────
Lookup rate from 51-tier "standard_vinyl_rates" table based on total_sqm
Example: If total_sqm = 0.75 sqm, rate = 33 (from 0.7-0.8 tier)

STEP 5: Apply Material Multiplier
─────────────────────────────────
material_multiplier = lookup from material selection
- Standard Vinyl: 1.0
- Premium Vinyl: 1.25
- Clear Vinyl: 1.35
- Removable Vinyl: 1.15

adjusted_rate = base_rate × material_multiplier

STEP 6: Apply Finish Multiplier
─────────────────────────────────
finish_multiplier = lookup from finish selection
- Gloss: 1.0
- Matte: 1.08
- Gloss Laminated: 1.25
- Matte Laminated: 1.30

final_rate = adjusted_rate × finish_multiplier

STEP 7: Calculate Base Printing Cost
─────────────────────────────────
printing_cost = total_sqm × final_rate

STEP 8: Add Cutting Costs
─────────────────────────────────
cutting_setup_fee = lookup from cutting method
cutting_per_unit = lookup from cutting method
cutting_cost = cutting_setup_fee + (cutting_per_unit × quantity)

STEP 9: Calculate Subtotal
─────────────────────────────────
subtotal = printing_cost + cutting_cost + artwork_cost

STEP 10: Apply GST
─────────────────────────────────
total_before_minimum = subtotal × 1.1

STEP 11: Apply Minimum Order Rule
─────────────────────────────────
IF total_before_minimum < 45 THEN
    final_price = 45 + 10
ELSE
    final_price = total_before_minimum + 10
END IF

RETURN final_price
```

---

## 📊 Calculation Examples

### Example 1: Small Promotional Stickers
**Configuration:**
- Quantity: 100 stickers
- Size: 75mm Circle
- Material: Standard Vinyl
- Finish: Gloss
- Cutting: Kiss-Cut
- Artworks: 1

**Calculation:**
```
1. Artwork cost: 1 × $5 = $5, but <= $5 so: $0

2. Dimensions: 75mm circle = 75mm × 75mm

3. Total sqm: (75 × 75 / 1,000,000) × 100 = 0.5625 sqm

4. Base rate: 0.5625 sqm falls in 0.5-0.6 tier = $35/sqm

5. Material multiplier: Standard Vinyl = 1.0
   Adjusted rate: $35 × 1.0 = $35/sqm

6. Finish multiplier: Gloss = 1.0
   Final rate: $35 × 1.0 = $35/sqm

7. Printing cost: 0.5625 × $35 = $19.69

8. Cutting costs: Kiss-Cut setup $0 + ($0.05 × 100) = $5

9. Subtotal: $19.69 + $5 + $0 = $24.69

10. Apply GST: $24.69 × 1.1 = $27.16

11. Minimum order: $27.16 < $45, so: $45 + $10 = $55

FINAL PRICE: $55.00
```

### Example 2: Medium Business Label Run
**Configuration:**
- Quantity: 500 stickers
- Size: 100mm × 75mm Rectangle
- Material: Premium Vinyl
- Finish: Gloss Laminated
- Cutting: Die-Cut
- Artworks: 2

**Calculation:**
```
1. Artwork cost: 2 × $5 = $10, $10 > $5 so: $10 - $5 = $5

2. Dimensions: 100mm × 75mm

3. Total sqm: (100 × 75 / 1,000,000) × 500 = 3.75 sqm

4. Base rate: 3.75 sqm falls in 3.5-4 tier = $21/sqm

5. Material multiplier: Premium Vinyl = 1.25
   Adjusted rate: $21 × 1.25 = $26.25/sqm

6. Finish multiplier: Gloss Laminated = 1.25
   Final rate: $26.25 × 1.25 = $32.81/sqm

7. Printing cost: 3.75 × $32.81 = $123.04

8. Cutting costs: Die-Cut setup $15 + ($0.08 × 500) = $55

9. Subtotal: $123.04 + $55 + $5 = $183.04

10. Apply GST: $183.04 × 1.1 = $201.34

11. Minimum order: $201.34 > $45, so: $201.34 + $10 = $211.34

FINAL PRICE: $211.34
```

### Example 3: Bulk Vehicle Decal Order
**Configuration:**
- Quantity: 1000 stickers
- Size: 150mm × 100mm Rectangle
- Material: Premium Vinyl
- Finish: Matte Laminated
- Cutting: Contour-Cut
- Artworks: 1 (bulk order, no artwork field)

**Calculation:**
```
1. Artwork cost: Bulk order (qty >= 100), artwork field hidden: $0

2. Dimensions: 150mm × 100mm

3. Total sqm: (150 × 100 / 1,000,000) × 1000 = 15 sqm

4. Base rate: 15 sqm falls in 14-16 tier = $16.9/sqm

5. Material multiplier: Premium Vinyl = 1.25
   Adjusted rate: $16.9 × 1.25 = $21.13/sqm

6. Finish multiplier: Matte Laminated = 1.30
   Final rate: $21.13 × 1.30 = $27.47/sqm

7. Printing cost: 15 × $27.47 = $412.05

8. Cutting costs: Contour-Cut setup $25 + ($0.12 × 1000) = $145

9. Subtotal: $412.05 + $145 + $0 = $557.05

10. Apply GST: $557.05 × 1.1 = $612.76

11. Minimum order: $612.76 > $45, so: $612.76 + $10 = $622.76

FINAL PRICE: $622.76
```

### Example 4: Custom Size Clear Vinyl Sticker
**Configuration:**
- Quantity: 50 stickers
- Size: Custom (200mm × 150mm)
- Material: Clear Vinyl
- Finish: Gloss
- Cutting: Kiss-Cut
- Artworks: 3

**Calculation:**
```
1. Artwork cost: 3 × $5 = $15, $15 > $5 so: $15 - $5 = $10

2. Dimensions: Custom 200mm × 150mm

3. Total sqm: (200 × 150 / 1,000,000) × 50 = 1.5 sqm

4. Base rate: 1.5 sqm falls in 1.25-1.5 tier = $26.3/sqm

5. Material multiplier: Clear Vinyl = 1.35
   Adjusted rate: $26.3 × 1.35 = $35.51/sqm

6. Finish multiplier: Gloss = 1.0
   Final rate: $35.51 × 1.0 = $35.51/sqm

7. Printing cost: 1.5 × $35.51 = $53.27

8. Cutting costs: Kiss-Cut setup $0 + ($0.05 × 50) = $2.50

9. Subtotal: $53.27 + $2.50 + $10 = $65.77

10. Apply GST: $65.77 × 1.1 = $72.35

11. Minimum order: $72.35 > $45, so: $72.35 + $10 = $82.35

FINAL PRICE: $82.35
```

### Example 5: Sheet Grid (Uncut) Bulk Order
**Configuration:**
- Quantity: 2000 stickers
- Size: 50mm Square
- Material: Removable Vinyl
- Finish: Matte
- Cutting: Sheet (Uncut Grid)
- Artworks: N/A (bulk order)

**Calculation:**
```
1. Artwork cost: Bulk order: $0

2. Dimensions: 50mm × 50mm

3. Total sqm: (50 × 50 / 1,000,000) × 2000 = 5 sqm

4. Base rate: 5 sqm falls in 4.5-5 tier = $20/sqm

5. Material multiplier: Removable Vinyl = 1.15
   Adjusted rate: $20 × 1.15 = $23/sqm

6. Finish multiplier: Matte = 1.08
   Final rate: $23 × 1.08 = $24.84/sqm

7. Printing cost: 5 × $24.84 = $124.20

8. Cutting costs: Sheet Uncut setup $0 + ($0 × 2000) = $0

9. Subtotal: $124.20 + $0 + $0 = $124.20

10. Apply GST: $124.20 × 1.1 = $136.62

11. Minimum order: $136.62 > $45, so: $136.62 + $10 = $146.62

FINAL PRICE: $146.62
```

---

## ✅ Validation Rules

### Field Constraints
```json
{
  "quantity": {
    "min": 1,
    "max": 10000,
    "required": true,
    "default": 100
  },
  "width_custom": {
    "min": 25,
    "max": 500,
    "required": true,
    "condition": "Only when Custom Size selected"
  },
  "height_custom": {
    "min": 25,
    "max": 500,
    "required": true,
    "condition": "Only when Custom Size selected"
  },
  "artworks": {
    "min": 1,
    "max": 20,
    "required": true,
    "default": 1,
    "condition": "Only visible when quantity < 100"
  }
}
```

### Business Rules
1. **Minimum sticker size:** 25mm × 25mm (0.000625 sqm)
2. **Maximum sticker size:** 500mm × 500mm (0.25 sqm)
3. **Artwork visibility:** Only shown for orders under 100 units
4. **Custom dimensions:** Only appear when "Custom Size" is selected
5. **Minimum order enforcement:** All orders under $45 charged $45 + $10 handling
6. **Handling fee:** $10 flat fee added to ALL orders (regardless of size)

---

## 🎨 Visibility Rules

### Conditional Field Display Logic
```json
{
  "custom_width_field": {
    "make_it": "Visible",
    "if": "(F2 == 'Custom Size')",
    "description": "Width field only visible when Custom Size is selected"
  },
  "custom_height_field": {
    "make_it": "Visible",
    "if": "(F2 == 'Custom Size')",
    "description": "Height field only visible when Custom Size is selected"
  },
  "artworks_field": {
    "make_it": "Visible",
    "if": "(F1 < '100')",
    "description": "Artworks field only visible when quantity is less than 100"
  }
}
```

**Rationale:**
- Custom dimensions only needed for non-standard sizes
- Artwork field hidden for bulk orders (100+ units assumed to be single design)
- Reduces form complexity for common use cases

---

## 📐 Key Calculation Variables Summary

```json
{
  "sqm_calculation": "(width_mm × height_mm / 1,000,000) × quantity",
  "base_rate_lookup": "51 tiers from $950/sqm (tiny stickers) to $14/sqm (bulk)",
  "material_multiplier": "1.0 (Standard) to 1.35 (Clear Vinyl)",
  "finish_multiplier": "1.0 (Gloss) to 1.30 (Matte Laminated)",
  "cutting_setup": "$0 (Kiss-cut) to $25 (Contour-cut)",
  "cutting_per_unit": "$0 (Sheet) to $0.12 (Contour-cut)",
  "artwork_formula": "IF (artworks × 5) > 5 THEN (artworks × 5 - 5) ELSE 0",
  "gst_rate": "1.1 (10% Australian GST)",
  "minimum_order": "$45 + $10 handling if subtotal < $45"
}
```

---

## 🏆 Competitive Advantages

### Pricing Benefits
1. **Square Meter Efficiency:** Bulk orders get exponentially better rates (from $950/sqm to $14/sqm)
2. **Transparent Material Costs:** Clear multipliers for premium options (no hidden fees)
3. **Flexible Cutting Options:** Budget-friendly sheet option vs premium die-cut
4. **First Artwork Free:** Encourages orders without penalizing single designs
5. **Predictable Pricing:** Formula-based calculations ensure consistency

### Technical Benefits
1. **51-Tier Precision:** Highly granular pricing captures all order sizes
2. **Material-Specific Tables:** Different vinyl types priced accurately
3. **Conditional Logic:** Only shows relevant fields (reduces user confusion)
4. **Minimum Order Protection:** Ensures profitability on small orders
5. **GST Compliant:** Australian tax regulations built-in

---

## 🚀 Implementation Checklist

- [ ] JSON configuration file created
- [ ] Square meter rate tables (51 tiers) entered
- [ ] Material multipliers configured
- [ ] Finish multipliers configured
- [ ] Cutting cost structures defined
- [ ] Artwork pricing logic implemented
- [ ] Minimum order rule implemented
- [ ] GST calculation configured
- [ ] Conditional field visibility tested
- [ ] All 5 example calculations verified
- [ ] Python calculator class generated
- [ ] Tool schema entry created
- [ ] Parameter documentation complete
- [ ] End-to-end testing passed

---

## 📝 Notes for Implementation

### Critical Considerations
1. **Micro-Sticker Handling:** Very small stickers (under 0.01 sqm) have high rates ($950/sqm) to cover setup costs
2. **Sheet Cutting Advantage:** Uncut sheets have ZERO cutting costs - significant savings for bulk
3. **Lamination Premium:** Laminated finishes add 25-30% but provide UV/scratch protection
4. **Die-Cut Setup Waiver:** Consider waiving $15-$25 setup fees at higher quantities (500+ units)
5. **Bulk Artwork Logic:** Artwork field hidden at 100+ units (assumed single design for bulk)

### Roll-to-Roll Media Rules (Machine + Roll Handling)
- **Standard roll width:** 1370 mm (1.37 m) for roll-to-roll media used by the production printers.
- **Common roll lengths:** 30 m, 50 m and 100 m; default commercial stock is 50 m.
- **Material families:**
  - *Monomeric vinyl* — short-term stock (white gloss), available with permanent or removable adhesive. Pricing generally similar across adhesive types.
  - *Polymeric vinyl* — long-term outdoor vinyl (up to ~5 years). Same width/length specs as monomerics.
- **Laminates:** Use matching laminates by material family:
  - *Monomeric laminate* matches monomeric vinyl.
  - *Polymeric laminate* matches polymeric vinyl.
  - Laminates available: Gloss laminate, Matte laminate.

### Roll Handling Charges & Labor Rules
- **Per-roll re-setup charge:** When a job spans multiple physical rolls, charge **$15 extra per additional roll** to re-set the printer (i.e. every roll beyond the first).
- **Laminating:**
  - Laminating machine **setup fee:** $15 per job.
  - Laminating throughput: **1 × 50 m roll per hour** (i.e. 50 m/hour).
  - Laminating labour rates: **Trade:** $70/hr, **Non-trade:** $90/hr.
  - Laminating labour cost per roll = labour_rate × time_per_roll (1 hour) + setup fee (split per job as appropriate).
- **Cutting / Finishing:**
  - **Straight trim to singles (Aristo cutter):** measured by linear metres of roll used. Cutter processes **2 linear metres** per cut in **10 minutes**.
    - This implies **10 minutes per 2 linear metres**, equivalent to **5 minutes per linear metre**.
    - Labour cost per linear metre = labour_rate × (5/60).
  - **Kiss-cut** for custom shapes (with waste left on roll): additional **$15 per linear metre** applied to the amount of media used.

### Linear Metre Calculation (Layout → Linear metres)
To determine how many linear metres of roll are required for a stickers job:

1. Compute sticker footprint per unit in mm: width_mm × height_mm.
2. Determine how many stickers fit across the roll width (per row):
   - stickers_per_row = floor(roll_width_mm / sticker_width_mm)
3. Determine how many stickers fit per linear metre along the roll:
   - stickers_per_linear_m = stickers_per_row × floor(1000 / sticker_height_mm)
   - (If stickers are longer than 1000mm, use 1000mm blocks or compute decimal metres accordingly.)
4. Required linear metres (raw) = ceil(quantity / stickers_per_linear_m)
5. Add **10% wastage**: linear_metres_with_waste = raw_linear_metres × 1.10

Notes:
- Use orientation and nesting heuristics to maximize stickers_per_row when width/height allow rotation; fallback to conservative packing if complex shapes.
- If stickers are irregular die-cut shapes, estimate slightly lower packing efficiency (e.g., -5% to -10%).

### Material Charge on Roll Basis
- Material/printing cost should be computed as either:
  - Square-metre pricing (base_rate × total_sqm), or
  - Per-linear-metre material charge derived from square-metre rates using roll width (e.g. per_linear_m_rate = base_rate × roll_width_m),
  - Then multiply per_linear_m_rate × linear_metres_with_waste to get material printing cost.

### Final Roll-based Cost Components
- Printing cost: total_sqm × final_rate (as defined in main logic) OR per-linear-metre equivalent
- Per-roll re-setup fees: $15 × (number_of_rolls_used - 1)
- Laminating cost: setup ($15) + labour (labour_rate × hours_for_rolls)
- Cutting cost: cutter labour (labour_rate × minutes) + kiss-cut per-linear-metre surcharge where used
- 10% waste applied to linear metres (or sqm) before material multiplication
- Apply artwork fees, GST, and minimum order rule as usual

### Business Rule Examples
- Job spanning 10 × 50 m rolls → **per-roll re-setup charges:** $15 × 9 = $135 extra
- Laminating 3 rolls (50 m each) at trade labour: setup $15 + (3 × $70) = $225


### Future Enhancements
- [ ] Add "Rush Production" option (+$20 fee, 24-hour turnaround)
- [ ] Add "White Ink Backing" for clear vinyl (+$0.10/sticker)
- [ ] Add "Specialty Shapes" (ovals, stars, hearts) to predefined sizes
- [ ] Add "Holographic Vinyl" material option (+50% multiplier)
- [ ] Add "Metallic Finish" option (+40% multiplier)
- [ ] Implement quantity break suggestions ("Order 50 more for $X savings!")

---

## 🎯 Ready for Implementation

This specification provides **complete pricing logic** for a professional vinyl stickers calculator using the square meter-based model. All formulas, multipliers, tiers, and business rules are defined and ready to be converted into JSON configuration format.

**Next Step:** Convert this specification into `Shopify_Custom_Vinyl_Stickers.json` format following the established pattern from the 26 existing calculators.

---

**Document Prepared By:** AI Agent  
**For:** InHouse Print Calculator System  
**Pricing Model Reference:** Custom Poster Printing (Square Meter-Based)  
**Status:** ✅ Complete Specification - Ready for JSON Conversion

