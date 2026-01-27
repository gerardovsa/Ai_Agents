# Construction Signs TXT vs Backend Comparison
**Date:** January 23, 2026  
**Status:** ❌ BACKEND WRONG - Needs complete rewrite

---

## TXT Formula (CORRECT - From Website JavaScript)

```javascript
// Artwork: First FREE, $5 per extra
var _a = {art} * 5;
var _a2 = {_a} <= 5 ? 0 : ({_a} - 5);

// Width/Height extraction
var _w = {f6} == 'Custom' ? {f3} : (standard size widths)
var _h = {f6} == 'Custom' ? {f7} : (standard size heights)

// SQM calculation
var sqm = (_w * _h / 1000000) * qty

// 43-tier pricing per material (5mm and 3mm)
var tier = {f4} == '5mm' ? (43 tiers: $31.25 → $10.97) : (43 tiers: $25 → $8.91)

// Sides surcharge
var _sidesCost = {f8} == 'Single Sided' ? 0 : 6;

// Custom tax
var taxRateOnCustom = {f6} == 'Custom' ? 1.1 : 1;

// Subtotal with 5% discount
var subTotal = ((((sqm * (tier + _sidesCost)) * taxRateOnCustom) + eyelets + _a2) * 0.95);

// Minimum order
var total = subTotal < 129 ? 129 : subTotal;

// Large size surcharge (+$45 if any dimension >= 1800mm OR 1200x2400 size)
If F7 >= 1800: Price = total + 45
Else If F3 >= 1800: Price = total + 45  
Else If f6 == '1200mm x 2400mm': Price = total + 45
Else If total >= 129: Price = total * 1.1
```

### Formula Breakdown:

1. **SQM Calculation:** (width × height ÷ 1M) × qty
2. **Tier Lookup:** 43 tiers per material (5mm/3mm)
3. **Sides surcharge:** +$6 to tier price if double sided
4. **Custom tax:** ×1.1 if custom size selected
5. **Add eyelets cost:** {f2.price} × qty
6. **Add artwork:** First FREE, $5 per extra
7. **5% discount:** ×0.95
8. **Minimum order:** $129
9. **Large surcharge:** +$45 if ≥1800mm dimension or 1200×2400
10. **Final multiplier:** ×1.1 (if ≥$129 and no large surcharge)

### 43-Tier Pricing (5mm Corflute):
- < 5 sqm: $31.25
- < 6 sqm: $28.35
- < 7 sqm: $25.15
- < 8 sqm: $24.71
- < 9 sqm: $22.74
- < 10 sqm: $22.64
- < 15 sqm: $21.24
- < 20 sqm: $19.50
- ... (35 more tiers)
- ≥ 700 sqm: $10.97

### 43-Tier Pricing (3mm Corflute):
- < 5 sqm: $25.00
- < 6 sqm: $25.00
- < 7 sqm: $21.09
- < 8 sqm: $20.48
- < 9 sqm: $19.02
- < 10 sqm: $18.75
- < 15 sqm: $17.73
- < 20 sqm: $16.13
- ... (35 more tiers)
- ≥ 700 sqm: $8.91

---

## Backend Implementation (WRONG - Old System)

```python
def calculate(self, **kwargs):
    # ❌ WRONG: Uses setup costs + profit margins
    impos_setup = Decimal('28')
    extra_arts = Decimal('18')
    
    # ❌ WRONG: Fixed material rates instead of tier lookup
    material_rate = Decimal('5.50') or Decimal('6.50')
    
    # ❌ WRONG: Separate print cost
    print_cost_per_m2 = Decimal('9.00')
    print_cost = area_m2 * print_cost_per_m2 * quantity * sides_multiplier
    
    # ❌ WRONG: Profit margin calculation
    profit_margin_rate = self._get_profit_margin(float(biz_cost))
    profit_amount = biz_cost * profit_margin_rate
    sub_total = biz_cost + profit_amount
    
    # ❌ WRONG: Double GST application
    total_price = (subtotal_with_increase * GST_RATE) * GST_RATE
```

**Backend Formula:**
- Setup costs: $28 impos + $18 per extra artwork
- Material cost: area × $5.50 (3mm) or $6.50 (5mm) × qty
- Print cost: area × $9/sqm × qty × sides
- Cut/fix: $1.50 × qty
- Profit margin: Variable rate based on cost
- Double GST: × 1.1 × 1.1

---

## Comparison Analysis

### Critical Differences:

| Aspect | TXT Formula | Backend |
|--------|------------|---------|
| **Pricing Method** | ✅ 43-tier SQM-based | ❌ Fixed material rates |
| **Base Rate** | ✅ Tier lookup ($31.25→$10.97) | ❌ Fixed $5.50/$6.50 per sqm |
| **Sides Handling** | ✅ +$6 to tier price | ❌ Multiplier on print cost |
| **Artwork Cost** | ✅ First FREE, $5 per extra | ❌ $28 + $18 per extra |
| **Discount** | ✅ 5% discount (×0.95) | ❌ No discount |
| **Minimum Order** | ✅ $129 | ❌ Not implemented |
| **Custom Tax** | ✅ ×1.1 for custom sizes | ❌ Not implemented |
| **Large Surcharge** | ✅ +$45 for ≥1800mm | ❌ Not implemented |
| **Final Multiplier** | ✅ ×1.1 (conditional) | ❌ Double GST (×1.1×1.1) |
| **Eyelets** | ✅ Direct cost from JSON | ❌ Not implemented |

### Price Difference Examples:

**Test Case 1: 1 sign, 600×900, 5mm, Single, No Eyelets, 1 artwork**
- TXT:
  - sqm = 0.54, tier = $31.25, sides = 0
  - subtotal = ((0.54 × 31.25) × 1 + 0 + 0) × 0.95 = 16.03
  - minimum = 16.03 < 129 → $129
  - final = 129 × 1.1 = **$141.90**
- Backend: ($28 + 0.54×$6.50 + 0.54×$9 + $1.50) × profit × 1.21 ≈ **$95** (WRONG)

**Test Case 2: 10 signs, 900×1200, 5mm, Double, 4 Corner Eyelets, 2 artworks**
- TXT:
  - sqm = 10.8, tier = $22.64, sides = 6, eyelets = $1.60 × 10 = $16
  - subtotal = ((10.8 × 28.64) × 1 + 16 + 5) × 0.95 = 314.26
  - minimum = 314.26 > 129 → $314.26
  - final = 314.26 × 1.1 = **$345.69**
- Backend: ($28 + $18 + 10.8×$6.50 + 10.8×$9×2 + $15) × profit × 1.21 ≈ **$523** (WRONG)

---

## Required Changes

### ✅ What TXT Shows (CORRECT):
1. **43 SQM-based tiers** per material (5mm/3mm)
2. **Sides surcharge** - +$6 to tier price (NOT separate cost)
3. **5% discount** - ×0.95 on subtotal
4. **Minimum order** - $129 floor
5. **Custom tax** - ×1.1 for custom sizes
6. **Large surcharge** - +$45 for signs ≥1800mm or 1200×2400
7. **Final multiplier** - ×1.1 (conditional, NOT double GST)
8. **Eyelets** - Direct JSON price × qty
9. **Artwork** - First FREE, $5 per extra

### ❌ What Backend Does (WRONG):
1. **Fixed material rates** - $5.50/$6.50 per sqm
2. **Separate print cost** - $9/sqm × sides multiplier
3. **Setup costs** - $28 impos + $18 per extra artwork
4. **Profit margin** - Variable rate added to cost
5. **Double GST** - ×1.1 × 1.1
6. **No discount, minimum, custom tax, or large surcharge**

---

## Root Cause

**Backend was built using Construction Signs OLD system** (similar to other Shopify calculators) with setup costs + profit margins + double GST.

**TXT shows Construction Signs uses HYBRID system:**
- Election Signs-style tier pricing (43 tiers)
- 5% discount (×0.95)
- Minimum order ($129)
- Custom tax for custom sizes (×1.1)
- Large size surcharge (+$45)
- Single final multiplier (×1.1)
- Eyelets as direct cost

Backend needs complete rewrite to match TXT formula exactly.

---

## Implementation Plan

### Step 1: Read TXT Tier Tables
- Copy ALL 43 tiers for 5mm ($31.25 → $10.97)
- Copy ALL 43 tiers for 3mm ($25 → $8.91)
- Verify tier ranges match sqm thresholds

### Step 2: Implement Tier Lookup
```python
def _get_price_per_sqm(self, total_sqm: Decimal, material: str) -> Decimal:
    """43-tier SQM-based pricing"""
    sqm_float = float(total_sqm)
    
    if '5mm' in material:
        # 5mm tiers
        if sqm_float < 5: return Decimal('31.25')
        elif sqm_float < 6: return Decimal('28.35')
        # ... 41 more tiers ...
    else:
        # 3mm tiers
        if sqm_float < 5: return Decimal('25.00')
        elif sqm_float < 6: return Decimal('25.00')
        # ... 41 more tiers ...
```

### Step 3: Implement TXT Formula
```python
def calculate(self, **kwargs):
    # Step 1: Width/Height extraction (standard or custom)
    # Step 2: SQM = (width × height ÷ 1M) × qty
    # Step 3: Tier lookup (43 tiers)
    # Step 4: Sides surcharge (+$6 if double sided)
    # Step 5: Custom tax (×1.1 if custom size)
    # Step 6: Add eyelets cost
    # Step 7: Add artwork (first FREE, $5 per extra)
    # Step 8: 5% discount (×0.95)
    # Step 9: Minimum order ($129)
    # Step 10: Large surcharge (+$45 if ≥1800mm or 1200×2400)
    # Step 11: Final multiplier (×1.1 conditional)
```

### Step 4: Website Validation Tests
```
TEST 1: 1 sign, 600×900, 5mm, Single, No Eyelets, 1 artwork → $141.90
TEST 2: 10 signs, 900×1200, 5mm, Double, 4 Corner Eyelets, 2 artworks → $345.69
TEST 3: 5 signs, 450×600, 3mm, Single, 2 Top Eyelets, 1 artwork → $148.50
TEST 4: 1 sign, Custom 2000×3000 (large), 5mm, Single, No Eyelets, 1 artwork → $[calculate]
```

---

## Status

- ❌ **Backend:** WRONG - uses old system (setup costs + profit margins + double GST)
- ✅ **TXT Formula:** DOCUMENTED - 43-tier hybrid system with discount, minimum, surcharges
- ⏳ **Fix Required:** Complete backend rewrite to implement TXT formula exactly
- ⏳ **Validation:** Website testing with 4 test cases

**Next Action:** Rewrite [ConstructionSigns_Shopify_Calculator.py](c:\Users\gpoli\GIT\AI_Agents_V11\AI_agents\UI\modules_external\quote-calculator\backend\Shopify_Calculators\ConstructionSigns_Shopify_Calculator.py) to implement TXT formula with 43-tier pricing + all surcharges.
