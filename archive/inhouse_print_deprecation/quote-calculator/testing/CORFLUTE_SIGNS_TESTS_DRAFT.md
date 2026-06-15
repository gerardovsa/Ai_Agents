# Corflute Signs Calculator - Test Configurations (DRAFT)
**Created:** January 27, 2026  
**Status:** Awaiting website validation  
**Calculator:** `calculate_corflute_signs_shopify`

---

## Quick Test Summary

| Test | Qty | Size | Thickness | Sides | Eyelets | Artworks | Expected (inc GST) |
|------|-----|------|-----------|-------|---------|----------|-------------------|
| 1 | 10 | 600x900 | 5mm | Single | 4 corners | 1 | **$182.97** |
| 2 | 100 | 600x900 | 5mm | Single | None | 1 | **$848.14** |
| 3 | 20 | Custom 800x1200 | 5mm | Double | 2 top | 1 | **$585.23** |
| 4 | 5 | 1200x2400 | 5mm | Single | 6 top/bottom | 1 | **$336.86** |
| 5 | 25 | 450x600 | 3mm | Single | None | 1 | **$148.76** |
| 6 | 50 | 900x1200 | 5mm | Single | 4 corners | 8 | **$978.77** |

---

## Test Overview

Based on schema examples and 43-tier pricing structure. Tests cover:
- ✅ Standard preset sizes (600x900, 900x1200, 1200x2400)
- ✅ Custom size with 10% premium
- ✅ Both thicknesses (3mm and 5mm)
- ✅ Double-sided option ($6/sqm add)
- ✅ Various eyelet options (none, 4 corners, 2 top)
- ✅ Different tier levels (10 sqm, 54 sqm, 100+ sqm)

---

## Test 1: Standard 600x900mm Sign (Small Order)
**Expected from Schema:** $166.34 (ex GST) → **$182.97 (inc GST)**  
**Configuration:**
- Quantity: 10 units
- Size: 600x900 (preset)
- Thickness: 5mm
- Double-sided: No
- Eyelets: 4 corners (4 per sign)
- Artworks: 1

**Expected Calculation:**
- SQM per unit: 0.54 sqm
- Total SQM: 5.4 sqm
- Tier price: $28.35/sqm (5-6 sqm tier)
- Base cost: 5.4 × $28.35 = $153.09
- Eyelet cost: 10 qty × 4 eyelets × $0.55 = $22.00
- Artwork: FREE (first 5 free)
- Subtotal: $175.09
- Discount (5%): -$8.75
- After discount: $166.34 (ex GST)
- **Add GST (10%): $166.34 × 1.1 = $182.97**
- Minimum $135: Applied, final = **$182.97 (inc GST)**

---

## Test 2: Large Volume 600x900mm (Medium Tier)
**Expected from Schema:** $771.04 (ex GST) → **$848.14 (inc GST)**  
**Configuration:**
- Quantity: 100 units
- Size: 600x900 (preset)
- Thickness: 5mm
- Double-sided: No
- Eyelets: None
- Artworks: 1

**Expected Calculation:**
- SQM per unit: 0.54 sqm
- Total SQM: 54 sqm
- Tier price: $15.03/sqm (50-60 sqm tier)
- Base cost: 54 × $15.03 = $811.62
- Eyelet cost: $0
- Artwork: FREE
- Subtotal: $811.62
- Discount (5%): -$40.58
- After discount: $771.04 (ex GST)
- **Add GST (10%): $771.04 × 1.1 = $848.14**
- Final: **$848.14 (inc GST)**

---

## Test 3: Custom Size Double-Sided (Premium Surcharge)
**Expected from Schema:** $532.03 (ex GST) → **$585.23 (inc GST)**  
**Configuration:**
- Quantity: 20 units
- Size: Custom
- Custom width: 800mm
- Custom height: 1200mm
- Thickness: 5mm
- Double-sided: Yes
- Eyelets: 2 top corners (2 per sign)
- Artworks: 1

**Expected Calculation:**
- SQM per unit: 0.96 sqm
- Total SQM: 19.2 sqm
- Tier price: $19.50/sqm (15-20 sqm tier)
- Base cost: 19.2 × $19.50 = $374.40
- Double-sided: 19.2 × $6 = $115.20
- Subtotal before custom: $489.60
- Custom premium (10%): $489.60 × 0.10 = $48.96
- Cost after custom: $538.56
- Eyelet cost: 20 × 2 × $0.55 = $22.00
- Artwork: FREE
- Subtotal: $560.56
- Discount (5%): -$28.03
- After discount: $532.03 (ex GST)
- **Add GST (10%): $532.03 × 1.1 = $585.23**
- Final: **$585.23 (inc GST)**

---

## Test 4: Large Format Sign (1200x2400mm)
**Configuration:**
- Quantity: 5 units
- Size: 1200x2400 (preset)
- Thickness: 5mm
- Double-sided: No
- Eyelets: 6 top/bottom (6 per sign)
- Artworks: 1

**Expected Calculation:**
- SQM per unit: 2.88 sqm
- Total SQM: 14.4 sqm
- Tier price: $21.24/sqm (10-15 sqm tier)
- Base cost: 14.4 × $21.24 = $305.86
- Eyelet cost: 5 × 6 × $0.55 = $16.50
- Artwork: FREE
- Subtotal: $322.36
- Discount (5%): -$16.12
- After discount: $306.24 (ex GST)
- **Add GST (10%): $306.24 × 1.1 = $336.86**
- Minimum $135: Applied, final = **$336.86 (inc GST)**

---

## Test 5: 3mm Economical Option
**Configuration:**
- Quantity: 25 units
- Size: 450x600 (preset)
- Thickness: 3mm
- Double-sided: No
- Eyelets: None
- Artworks: 1

**Expected Calculation:**
- SQM per unit: 0.27 sqm
- Total SQM: 6.75 sqm
- Tier price: $21.09/sqm (7 sqm tier for 3mm)
- Base cost: 6.75 × $21.09 = $142.36
- Eyelet cost: $0
- Artwork: FREE
- Subtotal: $142.36
- Discount (5%): -$7.12
- After discount: $135.24 (ex GST)
- **Add GST (10%): $135.24 × 1.1 = $148.76**
- Final: **$148.76 (inc GST)**

---

## Test 6: Multiple Artworks (Artwork Charges)
**Configuration:**
- Quantity: 50 units
- Size: 900x1200 (preset)
- Thickness: 5mm
- Double-sided: No
- Eyelets: 4 corners
- Artworks: 8

**Expected Calculation:**
- SQM per unit: 1.08 sqm
- Total SQM: 54 sqm
- Tier price: $15.03/sqm (50-60 sqm tier)
- Base cost: 54 × $15.03 = $811.62
- Eyelet cost: 50 × 4 × $0.55 = $110.00
- Artwork: (8 - 5) × $5 = $15.00 (first 5 FREE, then $5 each)
- Subtotal: $936.62
- Discount (5%): -$46.83
- After discount: $889.79 (ex GST)
- **Add GST (10%): $889.79 × 1.1 = $978.77**
- Final: **$978.77 (inc GST)**

---

## Validation Checklist

For each test:
1. ✅ Go to: https://www.inhouseprint.com.au/products/corflute-signs
2. ✅ Enter exact configuration
3. ✅ Compare website price with expected price
4. ✅ Document actual price if different
5. ✅ Note any restrictions or validation errors

---

## Notes for Testing

**Critical Formula Elements:**
- 43-tier pricing based on TOTAL SQM (all units combined)
- 5mm: $31.25/sqm (< 5sqm) → $10.97/sqm (700+ sqm)
- 3mm: $25.00/sqm (< 5sqm) → $8.91/sqm (700+ sqm)
- Double-sided: +$6/sqm (flat rate on total sqm)
- Custom size: +10% premium on (base_cost + double_sided_cost)
- Eyelets: $0.55 each × eyelet_count × quantity
- Artworks: First 5 FREE, then $5 per additional
- Discount: 5% on subtotal
- Minimum: $135 enforced

**Website Testing Tips:**
- Use "Calculate Price" or "Get Quote" button after entering all fields
- Check if preset sizes auto-fill width/height (don't need custom fields)
- Verify eyelet dropdown shows correct count (2, 4, or 6 eyelets)
- For artworks, may be labeled "Number of Designs" or "Unique Artworks"
- **CRITICAL:** Website displays prices **INCLUDING GST** (ex GST × 1.1)
- **Backend calculator returns ex GST prices** (confirmed line 361: "Note: Prices ex GST")
- All expected prices above are **inc GST** for website comparison

