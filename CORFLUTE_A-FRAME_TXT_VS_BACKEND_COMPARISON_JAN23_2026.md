# Corflute Insert A-Frame TXT vs Backend Comparison
**Date:** January 23, 2026  
**Status:** ❌ BACKEND WRONG - Needs complete rewrite

---

## TXT Formula (CORRECT - From Website JavaScript)

```javascript
// Artwork: First FREE, $5 per extra
var _a = {art} * 5;
var _a2 = {_a} <= 5 ? 0 : ({_a} - 5);

// 26-tier quantity-based pricing
var _up = (qty-based 26 tiers: $159 → $99)

// Formula: ((qty × rate) + artwork) × 1.1
var total = (qty * _up) + _a2;
{total} * 1.10
```

### 26-Tier Quantity Pricing:
- 1: $159.00
- 2: $146.94
- 3: $138.33 (138.3333333)
- 4: $130.00
- 5: $125.00
- 6: $130.83 (130.8333333)
- 7: $127.14 (127.1428571)
- 8: $124.38 (124.375)
- 9: $122.11 (122.1111111)
- 10: $120.00
- 11-12: $117.08 (117.0833333)
- 13-14: $115.00
- 15: $114.00
- 16-20: $110.75
- 21-25: $108.40
- 26-30: $107.00
- 31-35: $105.71 (105.7142857)
- 36-40: $104.75
- 41-45: $103.89 (103.8888889)
- 46-50: $103.40
- 51-60: $102.83 (102.8333333)
- 61-70: $102.29 (102.2857143)
- 71-80: $101.96 (101.9625)
- 81-90: $101.61 (101.6111111)
- 91-100: $101.35
- 101+: $99.00

### Formula Steps:
1. **Quantity tier lookup** - Find rate based on quantity
2. **Base cost** = qty × rate
3. **Artwork setup** = IF artworks > 1 THEN (artworks × 5) - 5 ELSE 0
4. **Subtotal** = base_cost + artwork
5. **Final total** = subtotal × 1.1

---

## Backend Implementation (WRONG - Old System)

```python
def calculate(self, **kwargs):
    # ❌ WRONG: Uses setup costs + profit margins
    impos_setup = Decimal('30')
    extra_arts = Decimal('18')
    
    material_cost = area_m2 * Decimal('6.50') * quantity
    print_cost = area_m2 * Decimal('8.50') * quantity * sides_multiplier
    a_frame_hardware = Decimal('4.50') * quantity
    
    biz_cost = impos_setup + artwork_setup_cost + material_cost + print_cost + a_frame_hardware
    
    profit_margin_rate = self._get_profit_margin(float(biz_cost))
    profit_amount = biz_cost * profit_margin_rate
    sub_total = biz_cost + profit_amount
    
    # ❌ WRONG: Double GST application
    total_price = (sub_total * 1.1) * 1.1
```

**Backend Formula:**
- Setup costs: $30 impos + $18 per extra artwork
- Material cost: area × $6.50/sqm × qty
- Print cost: area × $8.50/sqm × qty × sides
- Hardware: $4.50 × qty
- Profit margin: Variable rate
- Double GST: × 1.1 × 1.1

---

## Comparison Analysis

### Critical Differences:

| Aspect | TXT Formula | Backend |
|--------|------------|---------|
| **Pricing Method** | ✅ 26-tier quantity-based | ❌ Cost-based calculation |
| **Base Rate** | ✅ Tier lookup ($159→$99) | ❌ Area × $6.50 + $8.50/sqm |
| **Artwork Cost** | ✅ First FREE, $5 per extra | ❌ $30 setup + $18 per extra |
| **Profit/Markup** | ✅ Already in tier rates, then × 1.1 | ❌ Variable profit margin added |
| **GST Application** | ✅ Single 10% markup | ❌ Double GST (× 1.1 × 1.1) |
| **Hardware Cost** | ✅ Included in tier rates | ❌ Separate $4.50 × qty |
| **Formula** | ✅ ((qty × rate) + artwork) × 1.1 | ❌ (setup + materials + hardware + profit) × 1.1 × 1.1 |

### Price Difference Examples:

**Test Case 1: 1 A-frame, 1 artwork**
- TXT: 1 × $159 + $0 artwork = $159 × 1.1 = **$174.90**
- Backend: ($30 + 0.54×$6.50 + 0.54×$8.50 + $4.50) × profit × 1.21 ≈ **$108** (WRONG)

**Test Case 2: 10 A-frames, 2 artworks**
- TXT: 10 × $120 + $5 artwork = $1,205 × 1.1 = **$1,325.50**
- Backend: ($30 + $18 + 10×0.54×$6.50 + 10×0.54×$8.50 + 10×$4.50) × profit × 1.21 ≈ **$312** (WRONG)

**Test Case 3: 50 A-frames, 3 artworks**
- TXT: 50 × $103.40 + $10 artwork = $5,180 × 1.1 = **$5,698.00**
- Backend: ($30 + $36 + 50×0.54×$6.50 + 50×0.54×$8.50 + 50×$4.50) × profit × 1.21 ≈ **$1,343** (WRONG)

---

## Required Changes

### ✅ What TXT Shows (CORRECT):
1. **26 quantity-based tiers** - direct unit pricing
2. **Simple artwork formula** - first FREE, $5 per extra
3. **Single markup** - × 1.1 only
4. **No setup costs, no profit margins, no hardware costs** - all in tier rates

### ❌ What Backend Does (WRONG):
1. **Cost-based calculation** - setup + material + print + hardware
2. **Area-based pricing** - uses sqm calculations
3. **Complex artwork** - $30 setup + $18 per extra
4. **Profit margin** - adds variable profit
5. **Double GST** - × 1.1 × 1.1 (should be single × 1.1)
6. **Separate hardware cost** - $4.50 per unit (should be in tier rates)

---

## Root Cause

**Backend was built using the OLD system** (setup costs + profit margins + double GST) which was common for early Shopify calculators.

**TXT shows SIMPLE system** (quantity-based tier pricing) like Selfie Frames - just lookup rate, add artwork, multiply by 1.1.

Backend needs complete rewrite to match TXT formula exactly.

---

## Implementation Plan

### Step 1: Read TXT Tier Table
- Copy ALL 26 tiers ($159 → $99)
- Note the precise decimal values (e.g., 138.3333333, 127.1428571)
- Handle quantity ranges (11-12, 13-14, 16-20, etc.)

### Step 2: Implement Tier Lookup
```python
def _get_price_per_unit(self, quantity: int) -> Decimal:
    """26-tier quantity-based pricing"""
    if quantity == 1: return Decimal('159.00')
    elif quantity == 2: return Decimal('146.94')
    elif quantity == 3: return Decimal('138.3333333')
    # ... 23 more tiers ...
    elif quantity >= 101: return Decimal('99.00')
```

### Step 3: Implement TXT Formula
```python
def calculate(self, **kwargs):
    # Step 1: Tier lookup
    price_per_unit = self._get_price_per_unit(quantity)
    base_cost = price_per_unit * Decimal(quantity)
    
    # Step 2: Artwork (first FREE, $5 per extra)
    _a = Decimal(artworks) * Decimal('5')
    artwork_cost = Decimal('0') if _a <= Decimal('5') else _a - Decimal('5')
    
    # Step 3: Subtotal
    subtotal = base_cost + artwork_cost
    
    # Step 4: Final multiplier (10%)
    final_total = subtotal * Decimal('1.1')
```

### Step 4: Website Validation Tests
```
TEST 1: 1 A-frame, 1 artwork → $174.90
TEST 2: 10 A-frames, 2 artworks → $1,325.50
TEST 3: 50 A-frames, 3 artworks → $5,698.00
TEST 4: 100 A-frames, 2 artworks → $11,143.50
```

---

## Status

- ❌ **Backend:** WRONG - uses old system (setup costs + profit margins + double GST)
- ✅ **TXT Formula:** DOCUMENTED - 26-tier quantity-based pricing with simple × 1.1 markup
- ⏳ **Fix Required:** Complete backend rewrite to implement TXT formula exactly
- ⏳ **Validation:** Website testing with 4 test cases

**Next Action:** Rewrite [CorfluteInsertA_Frame_Shopify_Calculator.py](c:\Users\gpoli\GIT\AI_Agents_V11\AI_agents\UI\modules_external\quote-calculator\backend\shopify_calculators\CorfluteInsertA_Frame_Shopify_Calculator.py) to implement TXT formula with 26-tier pricing.
