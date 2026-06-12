# Construction Signs - JSON-First Re-Audit
**Date:** January 23, 2026
**Status:** CRITICAL DISCREPANCIES FOUND - Backend completely wrong
**Methodology:** JSON-FIRST (per SHOPIFY_CALCULATOR_JSON_FIRST_METHODOLOGY.md)

---

## Step 1: JSON Specification Summary

**File:** `Shopify_Construction_Signs.json` (882 lines)

### Fields (10 total):
1. **F1 - Quantity:** 1-10000 (integer, required)
2. **F2 - Eyelets:** 7 options (select, required, fixed prices: $0-$2.40)
   - "No Eyelets" ($0)
   - "4 x Eyelets (1 In Each Corner)" ($1.60)
   - "2 x Eyelets (top left & right corners)" ($0.80)
   - "2 x Eyelets (center left & right)" ($0.80)
   - "2 x Eyelets (center top & bottom)" ($0.80)
   - "6 x Eyelets (3 each top & bottom)" ($2.40)
   - "6 x Eyelets (3 each left & right)" ($2.40)
3. **F3 - Width (mm):** 100-5000 (custom width, hidden unless F6=="Custom")
4. **F4 - Thickness:** "3mm" or "5mm" (select, required, default "5mm")
5. **F6 - Size:** 5 options (select, required, default "600mm x 900mm")
   - "450mm x 600mm" (0.27 sqm)
   - "600mm x 900mm" (0.54 sqm)
   - "900mm x 1200mm" (1.08 sqm)
   - "1200mm x 2400mm" (2.88 sqm)
   - "Custom" (use F3/F7 for dimensions)
6. **F7 - Length (mm):** 100-5000 (custom height, hidden unless F6=="Custom")
7. **F8 - Sides?:** "Single Sided" or "Double Sided" (select, required, default "Single Sided")
8. **F9 - Cutting:** "Standard square edge" or "Custom Shape" (select, required)
9. **F10 - Artworks:** 1-20 (integer, required, default 1, visible when F1 > 2)

### Pricing Structure (JSON specification):

**Artwork Costs:**
```
IF artworks > 1 THEN (artworks * 5) - 5 ELSE 0
```
- First artwork FREE
- Additional artworks: $5 each

**Material Pricing - 42-Tier System:**

**5mm Corflute:**
- 0-5 sqm: $31.25/sqm
- 5-6 sqm: $28.35/sqm
- ... (42 tiers total)
- 700+ sqm: $10.97/sqm

**3mm Corflute:**
- 0-5 sqm: $25.00/sqm
- 5-6 sqm: $25.00/sqm
- ... (42 tiers total)
- 700+ sqm: $8.91/sqm

**Double-Sided Surcharge:**
```json
"double_sided_surcharge": 6
```
- Add $6.00 per sqm if double-sided

**Custom Size Tax Rate:**
```json
"custom_tax_rate": 1.1
```
- Multiply by 1.1 if F6=="Custom"

**Minimum Order:**
```json
"minimum_order": {"value": 129}
```

**Large Size Surcharge:**
```json
"large_size_surcharge": {
    "amount": 45,
    "description": "Additional charge for large signs (>=1800mm dimension or 1200x2400mm size)"
}
```
- Add $45 if: F7 >= 1800 OR F3 >= 1800 OR F6 == "1200mm x 2400mm"

**Final Multiplier:**
```json
"final_multiplier": {
    "rate": 1.1,
    "description": "10% final markup applied when no large size surcharge"
}
```
- Multiply by 1.1 if NO large size surcharge AND total >= $129

**Discount Factor:**
```json
"discount_factor": 0.95
```
- Multiply subtotal by 0.95 (5% discount)

### Complete Formula (from JSON):

```
1. Calculate artwork setup:
   IF artworks > 1 THEN (artworks * 5) - 5 ELSE 0

2. Determine dimensions:
   - Use predefined sizes OR custom width/height from F3/F7

3. Calculate square meters:
   sqm = (width * height / 1,000,000) * quantity

4. Determine base price per sqm:
   - Lookup tier price from material_pricing_tiers based on total sqm
   - Use 5mm_corflute or 3mm_corflute array

5. Calculate sides cost:
   IF double sided THEN add $6 per sqm ELSE $0

6. Apply custom tax rate:
   IF custom size (F6=="Custom") THEN multiply by 1.1 ELSE 1.0

7. Calculate subtotal:
   ((sqm * (tier_price + sides_cost)) * tax_rate) + (eyelet_cost * quantity) + artwork_setup

8. Apply discount:
   subtotal * 0.95

9. Apply minimum order value:
   IF result < 129 THEN 129 ELSE result

10. Check for large size surcharge:
    IF F7 >= 1800 OR F3 >= 1800 OR F6 == "1200mm x 2400mm" THEN add $45

11. ELSE IF total >= 129 THEN multiply by 1.1 (final markup)
```

**CRITICAL: NO GST IN FORMULA**
- JSON formula does NOT include GST multiplication
- Final price from formula = display price
- Shopify may show "Inc GST" but it's a label only

---

## Step 2: Backend Implementation Summary

**File:** `ConstructionSigns_Shopify_Calculator.py` (300 lines)

### What Backend Does:

**Artwork Cost:**
```python
artwork_setup_cost = (Decimal(artworks) - Decimal(1)) * extra_arts if artworks > 1 else Decimal('0')
# extra_arts = Decimal('18')
```
- ❌ WRONG: Uses $18 per extra artwork (JSON says $5)
- ✅ CORRECT: First artwork FREE logic

**Material Rates:**
```python
if '3mm' in thickness_raw:
    material_rate = Decimal('5.50')  # 3mm Corflute rate
elif '5mm' in thickness_raw:
    material_rate = Decimal('6.50')  # 5mm Corflute rate
```
- ❌ WRONG: Fixed rates ($5.50/$6.50)
- ❌ WRONG: No 42-tier pricing system

**Calculation:**
```python
material_cost = area_m2 * material_rate * Decimal(quantity)
print_cost = area_m2 * print_cost_per_m2 * Decimal(quantity) * sides_multiplier
cutting_and_fix = Decimal('1.50') * Decimal(quantity)

biz_cost = impos_setup + artwork_setup_cost + material_cost + print_cost + cutting_and_fix

profit_margin_rate = self._get_profit_margin(float(biz_cost))
profit_amount = biz_cost * profit_margin_rate
sub_total = biz_cost + profit_amount

total_price = (subtotal_with_increase * GST_RATE) * GST_RATE
```
- ❌ WRONG: Uses impos_setup ($28), print_cost, cutting_and_fix - not in JSON
- ❌ WRONG: Profit margin system - not in JSON
- ❌ WRONG: **DOUBLE GST** (× 1.1 × 1.1) - JSON has NO GST

**Missing from Backend:**
- ❌ 42-tier pricing lookup
- ❌ Eyelet costs ($0-$2.40 per sign)
- ❌ Double-sided surcharge ($6/sqm)
- ❌ Custom size tax rate (× 1.1)
- ❌ Discount factor (× 0.95)
- ❌ Minimum order ($129)
- ❌ Large size surcharge ($45)
- ❌ Final multiplier (× 1.1)

---

## Step 3: Wrapper Validation Summary

**File:** `calculator_wrapper.py` (lines 2846-2976)

### Wrapper Validations:

**Field Validations:**
- ✅ Quantity: 1-10000 (implicit, no explicit check)
- ✅ Size: 5 valid options (enum check present)
- ✅ Thickness: "3mm"/"5mm" (enum check present)
- ✅ Sides: "Single Sided"/"Double Sided" (enum check present)
- ✅ Eyelets: 7 valid options (enum check present)
- ✅ Cutting: 2 valid options (enum check present)
- ✅ Artworks: 1-20 (range check present)

**Format Transformations:**
- ✅ Passes JSON formats directly to backend (no transformation)

**Missing Validations:**
- ❌ Custom width/height validation (F3/F7) when F6=="Custom"
- ❌ Artworks visibility rule (should only show when quantity > 2)

---

## Step 4: Discrepancies Found

### CRITICAL Issues:

#### 1. ❌ **Material Pricing - Completely Wrong**
- **JSON Specification:** 42-tier pricing system per material type
  - 5mm: $31.25/sqm (0-5 sqm) → $10.97/sqm (700+ sqm)
  - 3mm: $25.00/sqm (0-5 sqm) → $8.91/sqm (700+ sqm)
- **Backend Implementation:** Fixed rates ($5.50 for 3mm, $6.50 for 5mm)
- **Impact:** Prices completely incorrect - no volume discounts, wrong base rates
- **Fix Required:** Implement 42-tier lookup system from JSON

#### 2. ❌ **Artwork Costs - Wrong Amount**
- **JSON Specification:** First artwork FREE, then $5 per additional
  - Formula: `(artworks * 5) - 5` if artworks > 1
- **Backend Implementation:** First artwork FREE, then $18 per additional
  - Formula: `(artworks - 1) * 18`
- **Impact:** Artwork costs 3.6x too high
- **Fix Required:** Change `extra_arts` from $18 to $5

#### 3. ❌ **Eyelet Costs - Completely Missing**
- **JSON Specification:** 7 eyelet options with fixed prices
  - "No Eyelets" ($0)
  - "4 x Eyelets (1 In Each Corner)" ($1.60 per sign)
  - "2 x Eyelets (top left & right corners)" ($0.80 per sign)
  - "2 x Eyelets (center left & right)" ($0.80 per sign)
  - "2 x Eyelets (center top & bottom)" ($0.80 per sign)
  - "6 x Eyelets (3 each top & bottom)" ($2.40 per sign)
  - "6 x Eyelets (3 each left & right)" ($2.40 per sign)
- **Backend Implementation:** Not implemented at all
- **Impact:** Missing $0-$2.40 per sign cost
- **Fix Required:** Add eyelet cost lookup and multiply by quantity

#### 4. ❌ **Double-Sided Surcharge - Wrong Implementation**
- **JSON Specification:** Add $6.00 per sqm if double-sided
  - Applied to sqm, not quantity
- **Backend Implementation:** Uses sides_multiplier (×2) on print_cost
  - Doubles entire print cost instead of adding $6/sqm
- **Impact:** Wrong calculation method
- **Fix Required:** Add $6/sqm when double-sided, not multiply by 2

#### 5. ❌ **Custom Size Tax Rate - Missing**
- **JSON Specification:** Multiply by 1.1 if F6=="Custom"
- **Backend Implementation:** Not implemented
- **Impact:** Custom sizes underpriced by 10%
- **Fix Required:** Add custom size check and apply 1.1x multiplier

#### 6. ❌ **Discount Factor - Missing**
- **JSON Specification:** Multiply subtotal by 0.95 (5% discount)
- **Backend Implementation:** Not implemented
- **Impact:** All prices 5% too high (but offset by other errors)
- **Fix Required:** Apply 0.95x discount after subtotal

#### 7. ❌ **Minimum Order - Missing**
- **JSON Specification:** If result < $129, set to $129
- **Backend Implementation:** Not implemented
- **Impact:** Small orders underpriced
- **Fix Required:** Add minimum order check

#### 8. ❌ **Large Size Surcharge - Missing**
- **JSON Specification:** Add $45 if F7>=1800 OR F3>=1800 OR F6=="1200mm x 2400mm"
- **Backend Implementation:** Not implemented
- **Impact:** Large signs underpriced by $45
- **Fix Required:** Add large size check and apply $45 surcharge

#### 9. ❌ **Final Multiplier - Missing**
- **JSON Specification:** Multiply by 1.1 if NO large size surcharge AND total >= $129
- **Backend Implementation:** Not implemented (but has wrong double GST instead)
- **Impact:** Wrong final markup calculation
- **Fix Required:** Add final multiplier logic (mutually exclusive with large size surcharge)

#### 10. ❌ **GST Handling - Completely Wrong**
- **JSON Specification:** NO GST in formula (formula output = final price)
- **Backend Implementation:** **DOUBLE GST** (× 1.1 × 1.1 = ×1.21 total)
- **Impact:** All prices 21% too high
- **Fix Required:** Remove ALL GST multiplication

#### 11. ❌ **Wrong Cost Components**
- **Backend Uses:** impos_setup ($28), print_cost ($9/sqm), cutting_and_fix ($1.50/unit), profit_margin
- **JSON Uses:** None of these - uses tier pricing + surcharges + discounts only
- **Impact:** Completely different calculation method
- **Fix Required:** Remove all non-JSON cost components

### Minor Issues:

#### 12. ⚠️ **Custom Width/Height Validation Missing**
- **Wrapper:** No validation for F3/F7 when F6=="Custom"
- **JSON Specification:** F3 and F7 required when F6=="Custom", range 100-5000
- **Fix Required:** Add conditional validation

#### 13. ⚠️ **Artworks Visibility Rule Not Enforced**
- **Wrapper:** Always accepts artworks parameter
- **JSON Specification:** F10 visible only when F1 > 2
- **Fix Required:** Add visibility condition (or document as UI-only rule)

---

## Step 5: Required Changes

### Backend Changes (ConstructionSigns_Shopify_Calculator.py):

**COMPLETE REWRITE REQUIRED - Current backend is 100% wrong**

```python
def calculate(self, **kwargs) -> ConstructionSignsShopifyCalculatorQuoteResult:
    """Calculate Construction Signs following JSON specification exactly"""
    
    # 1. Extract parameters
    quantity = int(kwargs.get('quantity', 1))
    size = kwargs.get('size', '600mm x 900mm')
    thickness = kwargs.get('thickness', '5mm')
    sides = kwargs.get('sides', 'Single Sided')
    eyelets = kwargs.get('eyelets', 'No Eyelets')
    cutting = kwargs.get('cutting', 'Standard square edge')
    artworks = int(kwargs.get('artworks', 1))
    custom_width = kwargs.get('custom_width')
    custom_height = kwargs.get('custom_height')
    
    # 2. Calculate artwork setup (JSON formula)
    if artworks > 1:
        artwork_setup_cost = Decimal((artworks * 5) - 5)
    else:
        artwork_setup_cost = Decimal('0')
    
    # 3. Get dimensions
    if size == "Custom":
        if not custom_width or not custom_height:
            raise ValueError("Custom size requires width and height")
        width_mm = Decimal(custom_width)
        height_mm = Decimal(custom_height)
        is_custom = True
    else:
        # Lookup from size_dimensions in JSON
        width_mm, height_mm = self._get_dimensions_from_size(size)
        is_custom = False
    
    # 4. Calculate square meters
    total_sqm = (width_mm * height_mm / Decimal('1000000')) * Decimal(quantity)
    
    # 5. Get base price per sqm from 42-tier system
    material_key = '5mm_corflute' if '5mm' in thickness else '3mm_corflute'
    price_per_sqm = self._get_tier_price(material_key, float(total_sqm))
    
    # 6. Calculate sides cost (add $6/sqm if double-sided)
    sides_cost_per_sqm = Decimal('6') if 'Double' in sides else Decimal('0')
    
    # 7. Apply custom tax rate if custom size
    custom_tax = Decimal('1.1') if is_custom else Decimal('1.0')
    
    # 8. Get eyelet cost per sign
    eyelet_cost_per_sign = self._get_eyelet_cost(eyelets)
    total_eyelet_cost = eyelet_cost_per_sign * Decimal(quantity)
    
    # 9. Calculate subtotal
    material_cost = total_sqm * (price_per_sqm + sides_cost_per_sqm) * custom_tax
    subtotal = material_cost + total_eyelet_cost + artwork_setup_cost
    
    # 10. Apply discount (5%)
    subtotal_after_discount = subtotal * Decimal('0.95')
    
    # 11. Apply minimum order
    if subtotal_after_discount < Decimal('129'):
        subtotal_after_discount = Decimal('129')
    
    # 12. Check for large size surcharge
    is_large_size = (
        (custom_height and custom_height >= 1800) or
        (custom_width and custom_width >= 1800) or
        size == "1200mm x 2400mm"
    )
    
    if is_large_size:
        total_price = subtotal_after_discount + Decimal('45')
    else:
        # Apply final multiplier (10%)
        if subtotal_after_discount >= Decimal('129'):
            total_price = subtotal_after_discount * Decimal('1.1')
        else:
            total_price = subtotal_after_discount
    
    # NO GST - formula output is final price
    
    total_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    unit_price = total_price / Decimal(quantity)
    
    return ConstructionSignsShopifyCalculatorQuoteResult(...)
```

**Helper Methods to Add:**

```python
def _get_dimensions_from_size(self, size: str) -> Tuple[Decimal, Decimal]:
    """Get width/height from predefined size"""
    dimensions = {
        "450mm x 600mm": (450, 600),
        "600mm x 900mm": (600, 900),
        "900mm x 1200mm": (900, 1200),
        "1200mm x 2400mm": (1200, 2400)
    }
    if size not in dimensions:
        raise ValueError(f"Unknown size: {size}")
    return Decimal(dimensions[size][0]), Decimal(dimensions[size][1])

def _get_tier_price(self, material_key: str, total_sqm: float) -> Decimal:
    """Lookup price from 42-tier system"""
    # Load from JSON config material_pricing_tiers
    tiers = self.config['shopify_construction_signs']['material_pricing_tiers'][material_key]
    for tier in tiers:
        if total_sqm <= tier['sqm_max']:
            return Decimal(str(tier['price_per_sqm']))
    # Fallback to last tier
    return Decimal(str(tiers[-1]['price_per_sqm']))

def _get_eyelet_cost(self, eyelets: str) -> Decimal:
    """Get eyelet cost per sign"""
    eyelet_costs = {
        "No Eyelets": Decimal('0'),
        "4 x Eyelets (1 In Each Corner)": Decimal('1.60'),
        "2 x Eyelets (top left & right corners)": Decimal('0.80'),
        "2 x Eyelets (center left & right)": Decimal('0.80'),
        "2 x Eyelets (center top & bottom)": Decimal('0.80'),
        "6 x Eyelets (3 each top & bottom)": Decimal('2.40'),
        "6 x Eyelets (3 each left & right)": Decimal('2.40')
    }
    return eyelet_costs.get(eyelets, Decimal('0'))
```

### Wrapper Changes (calculator_wrapper.py):

**Add custom width/height validation:**

```python
def calculate_construction_signs(quantity, size, thickness, sides, eyelets, cutting, artworks, custom_width=None, custom_height=None):
    # ... existing validations ...
    
    # Add custom size validation
    if size == "Custom":
        if custom_width is None or custom_height is None:
            return {
                "success": False,
                "error": "Custom size requires both width and height parameters"
            }
        if custom_width < 100 or custom_width > 5000:
            return {
                "success": False,
                "error": f"Custom width must be between 100-5000mm, got {custom_width}"
            }
        if custom_height < 100 or custom_height > 5000:
            return {
                "success": False,
                "error": f"Custom height must be between 100-5000mm, got {custom_height}"
            }
    
    # Pass custom dimensions to backend
    result = calculator.calculate(
        quantity=quantity,
        size=size,
        thickness=thickness,
        sides=sides,
        eyelets=eyelets,
        cutting=cutting,
        artworks=artworks,
        custom_width=custom_width,
        custom_height=custom_height
    )
```

---

## Step 6: Test Plan

**Create:** `test_construction_signs_fixed.py`

### Tests:

1. **Small Order with Minimum Price:**
   - 1 sign, 450x600, 5mm, single sided, no eyelets, 1 artwork
   - Expected: $129 (minimum order)

2. **Standard Construction Sign:**
   - 10 signs, 600x900, 5mm, single sided, 4 corner eyelets, 1 artwork
   - Verify: tier pricing, eyelet costs, discount, final multiplier

3. **Double-Sided with Multiple Artworks:**
   - 25 signs, 900x1200, 5mm, double sided, 6 eyelets, 2 artworks
   - Verify: $6/sqm surcharge, artwork costs ($5), tier pricing

4. **Large Size with Surcharge:**
   - 5 signs, 1200x2400, 5mm, single sided, 4 corner eyelets, 1 artwork
   - Expected: $45 surcharge (NO final multiplier)

5. **Custom Size with Tax:**
   - 15 signs, custom 800x1500, 5mm, double sided, 6 eyelets, 1 artwork
   - Verify: custom tax (×1.1), double-sided surcharge, tier pricing

6. **3mm vs 5mm Material Comparison:**
   - Same config, test both materials
   - Verify: different tier prices (3mm cheaper)

7. **Volume Tier Test:**
   - Test quantities showing tier price changes
   - Verify: price per sqm decreases with volume

8. **Edge Cases:**
   - Quantity 10000 (max)
   - Artworks 20 (max)
   - Custom size 5000x5000 (max dimensions, triggers large surcharge)

---

## Summary

**Status:** ❌ **CRITICAL - Backend 100% Wrong**

**Key Findings:**
1. Backend uses completely different formula (profit margins, setup costs, double GST)
2. Missing 42-tier pricing system (most important feature)
3. Missing eyelet costs ($0-$2.40 per sign)
4. Missing all JSON pricing constants (discount, minimum, surcharges, multipliers)
5. Artwork costs 3.6x too high ($18 vs $5)
6. GST handling completely wrong (double GST vs none)

**Next Steps:**
1. ✅ JSON read (complete)
2. ✅ Backend read (complete)
3. ✅ Wrapper read (complete)
4. ✅ Discrepancies documented (complete)
5. ⏳ Fix backend (COMPLETE REWRITE REQUIRED)
6. ⏳ Create tests
7. ⏳ Validate against JSON formula
8. ⏳ Production validation (if Shopify available)

**Estimated Impact:** All prices completely wrong - backend needs full replacement to match JSON specification.
