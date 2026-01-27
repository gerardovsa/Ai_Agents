# Selfie Frames TXT vs Backend Comparison
**Date:** January 23, 2026  
**Status:** ❌ BACKEND WRONG - Needs complete rewrite

---

## TXT Formula (CORRECT - From Website JavaScript)

```javascript
// Artwork setup: First FREE, $5 per extra
var _a = {art} * 5;
var _a2 = {_a} <= 5 ? 0 : ({_a} - 5);

// Formula: ((qty × rate) + artwork) × 1.1
```

### Quantity-Based Tier Pricing (34 Tiers per Size)

**Small 600mm x 900mm:**
- 1 unit: $117.00
- 2 units: $108.00
- 3 units: $98.67
- 4 units: $83.00
- 5 units: $74.60
- 6 units: $68.67
- 7 units: $64.57
- 8 units: $61.50
- 9 units: $59.00
- 10 units: $57.00
- 11 units: $55.27
- 12 units: $53.83
- 13 units: $50.23
- 14 units: $51.43
- 15 units: $50.53
- 16-20: $46.80
- 21-25: $44.40
- 26-30: $42.60
- 31-35: $41.23
- 36-40: $40.15
- 41-45: $40.00
- 46-50: $39.96
- 51-60: $39.90
- 61-70: $39.86
- 71-80: $39.84
- 81-90: $39.80
- 91-100: $39.79
- 101-110: $39.76
- 111-120: $39.75
- 121-130: $39.74
- 131-140: $39.74
- 141-150: $39.73
- 151-175: $39.70
- 176-200: $39.69

**Large 900mm x 1200mm:**
- 1 unit: $172.00
- 2 units: $163.00
- 3 units: $150.00
- 4 units: $127.00
- 5 units: $114.00
- 6 units: $105.17
- 7 units: $99.14
- 8 units: $94.50
- 9 units: $90.67
- 10 units: $87.70
- 11 units: $85.09
- 12 units: $82.83
- 13 units: $81.00
- 14 units: $79.36
- 15 units: $77.87
- 16-20: $72.30
- 21-25: $68.64
- 26-30: $66.00
- 31-35: $63.86
- 36-40: $62.20
- 41-45: $62.00
- 46-50: $61.96
- 51-60: $61.92
- 61-70: $61.86
- 71-80: $61.83
- 81-90: $61.80
- 91-100: $61.78
- 101-110: $61.76
- 111-120: $61.75
- 121-130: $61.74
- 131-140: $61.73
- 141-150: $61.72
- 151-175: $61.70
- 176-200: $61.69

### Formula Steps:
1. **Quantity tier lookup** - Find rate based on quantity and size
2. **Base cost** = qty × rate
3. **Artwork setup** = IF artworks > 1 THEN (artworks × 5) - 5 ELSE 0
4. **Subtotal** = base_cost + artwork_setup
5. **Final total** = subtotal × 1.1

---

## Backend Implementation (WRONG - Old System)

```python
def calculate(self, **kwargs):
    # ❌ WRONG: Uses setup costs + profit margins
    impos_setup = Decimal('28')
    extra_arts = Decimal('15')
    
    material_cost = area_m2 * material_rate * quantity
    print_cost = area_m2 * Decimal('10.00') * quantity
    cut_and_finish = Decimal('2.50') * quantity
    
    biz_cost = impos_setup + artwork_setup_cost + material_cost + print_cost + cut_and_finish
    
    profit_margin_rate = self._get_profit_margin(float(biz_cost))
    profit_amount = biz_cost * profit_margin_rate
    sub_total = biz_cost + profit_amount
    
    # ❌ WRONG: Double GST application
    total_price = (sub_total * 1.1) * 1.1
```

**Backend Formula:**
- Setup costs: $28 impos + $15 per extra artwork
- Material cost: area × $18/sqm (foam core) × qty
- Print cost: area × $10/sqm × qty
- Cut/finish: $2.50 × qty
- Profit margin: 50%
- Double GST: × 1.1 × 1.1

---

## Comparison Analysis

### Critical Differences:

| Aspect | TXT Formula | Backend |
|--------|------------|---------|
| **Pricing Method** | ✅ Quantity-based tiers (34 tiers per size) | ❌ Cost-based calculation |
| **Base Rate** | ✅ Tier lookup (e.g., 1 Small = $117) | ❌ Material + print + cut ($18+$10+$2.50/sqm) |
| **Artwork Cost** | ✅ First FREE, $5 per extra | ❌ $28 setup + $15 per extra |
| **Profit/Markup** | ✅ Already in tier rates, then × 1.1 | ❌ 50% profit margin added |
| **GST Application** | ✅ Single 10% markup | ❌ Double GST (× 1.1 × 1.1) |
| **Formula** | ✅ ((qty × rate) + artwork) × 1.1 | ❌ (setup + materials + profit) × 1.1 × 1.1 |

### Price Difference Examples:

**Test Case 1: 1 Small Frame, 1 Artwork**
- TXT: 1 × $117 + $0 artwork = $117 × 1.1 = **$128.70**
- Backend: ($28 + 0.54×$18 + 0.54×$10 + $2.50) × 1.5 × 1.21 ≈ **$91** (WRONG)

**Test Case 2: 10 Small Frames, 2 Artworks**
- TXT: 10 × $57 + $5 artwork = $575 × 1.1 = **$632.50**
- Backend: ($28 + $5 + 10×0.54×$18 + 10×0.54×$10 + 10×$2.50) × 1.5 × 1.21 ≈ **$421** (WRONG)

**Test Case 3: 25 Large Frames, 3 Artworks**
- TXT: 25 × $68.64 + $10 artwork = $1,726 × 1.1 = **$1,898.60**
- Backend: ($28 + $30 + 25×1.08×$18 + 25×1.08×$10 + 25×$2.50) × 1.5 × 1.21 ≈ **$1,523** (WRONG)

---

## Required Changes

### ✅ What TXT Shows (CORRECT):
1. **34 quantity-based tiers** for each size (Small and Large)
2. **Direct tier lookup** - no material/print cost calculations
3. **Simple artwork formula** - first FREE, $5 per extra
4. **Single markup** - × 1.1 only
5. **No setup costs, no profit margins** - all pricing in tiers

### ❌ What Backend Does (WRONG):
1. **Cost-based calculation** - setup + material + print + cut
2. **Area-based pricing** - uses sqm calculations
3. **Complex artwork** - $28 setup + $15 per extra
4. **Profit margin** - adds 50% profit
5. **Double GST** - × 1.1 × 1.1 (should be single × 1.1)

---

## Root Cause

**Backend was built using the OLD system** (setup costs + profit margins + double GST) which was common for other Shopify calculators like Construction Signs.

**TXT shows NEW system** (quantity-based tier pricing) which is simpler and matches Stackable Cubes pattern.

Backend needs complete rewrite to match TXT formula exactly.

---

## Implementation Plan

### Step 1: Read TXT Tier Tables
- Copy ALL 34 tiers for Small size ($117 → $39.69)
- Copy ALL 34 tiers for Large size ($172 → $61.69)
- Verify tier ranges (e.g., 16-20, 21-25, etc.)

### Step 2: Implement Tier Lookup
```python
def _get_price_per_unit(self, quantity: int, size: str) -> Decimal:
    """34-tier quantity-based pricing"""
    if 'Small' in size or '600' in size:
        # Small 600x900 tiers
        if quantity == 1: return Decimal('117.00')
        elif quantity == 2: return Decimal('108.00')
        # ... 32 more tiers ...
    else:
        # Large 900x1200 tiers
        if quantity == 1: return Decimal('172.00')
        elif quantity == 2: return Decimal('163.00')
        # ... 32 more tiers ...
```

### Step 3: Implement TXT Formula
```python
def calculate(self, **kwargs):
    # Step 1: Tier lookup
    price_per_unit = self._get_price_per_unit(quantity, size)
    base_cost = price_per_unit * Decimal(quantity)
    
    # Step 2: Artwork (first FREE, $5 per extra)
    _a = Decimal(artworks) * Decimal('5')
    artwork_setup_cost = Decimal('0') if _a <= Decimal('5') else _a - Decimal('5')
    
    # Step 3: Add artwork
    subtotal = base_cost + artwork_setup_cost
    
    # Step 4: Final multiplier (10%)
    final_total = subtotal * Decimal('1.1')
```

### Step 4: Website Validation Tests
```
TEST 1: 1 Small, 1 artwork → $128.70
TEST 2: 10 Small, 2 artworks → $632.50
TEST 3: 25 Large, 3 artworks → $1,898.60
TEST 4: 100 Large, 2 artworks → $6,801.30
```

---

## Status

- ❌ **Backend:** WRONG - uses old system (setup costs + profit margins + double GST)
- ✅ **TXT Formula:** DOCUMENTED - quantity-based tiers with simple × 1.1 markup
- ⏳ **Fix Required:** Complete backend rewrite to implement TXT formula exactly
- ⏳ **Validation:** Website testing with 4 test cases

**Next Action:** Rewrite [SelfieFrames_Shopify_Calculator.py](c:\Users\gpoli\GIT\AI_Agents_V11\AI_agents\UI\modules_external\quote-calculator\backend\shopify_calculators\SelfieFrames_Shopify_Calculator.py) to implement TXT formula with 34-tier pricing.
