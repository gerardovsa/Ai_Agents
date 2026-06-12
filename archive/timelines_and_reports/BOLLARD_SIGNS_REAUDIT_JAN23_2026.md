# BOLLARD SIGNS - JSON-First Re-Audit (January 23, 2026)

**Calculator:** Bollard Signs  
**JSON File:** `Shopify_Bollard_Signs.json` (640 lines)  
**Backend File:** `BollardSigns_Shopify_Calculator.py` (201 lines)  
**Wrapper Location:** `calculator_wrapper.py` line 2750-2837  
**Audit Date:** January 23, 2026, 7:45 PM  
**Previous Fix Date:** January 23, 2026 (Reactive approach)  
**Re-audit Methodology:** ✅ JSON-FIRST (Proactive)

---

## ✅ STEP 1: JSON SPECIFICATION ANALYSIS

### **Fields:**
- **F1 (Quantity):**
  - Type: number
  - Range: 1-1000
  - Default: 1
  - Required: true
  - Description: "Number of bollard signs to produce"

- **F4 (Material):**
  - Type: select
  - Options: `["3mm Corflute", "5mm Corflute"]`
  - Default: "5mm Corflute"
  - Required: true
  - Description: "3mm or 5mm corrugated plastic"

- **F6 (Size):**
  - Type: select
  - Options: **12 options** (see list below)
  - Default: "270mm W x 1000mm H - Three Sided"
  - Required: true
  - Description: "Size with sides configuration"
  
  **All 12 Size Options:**
  1. "270mm W x 1000mm H - Three Sided"
  2. "270mm W x 1200mm H - Three Sided"
  3. "270mm W x 1800mm H - Three Sided"
  4. "300mm W x 1000mm H - Three Sided"
  5. "300mm W x 1200mm H - Three Sided"
  6. "300mm W x 1800mm H - Three Sided"
  7. "155mm W x 1000mm H - Four Sided"
  8. "155mm W x 1200mm H - Four Sided"
  9. "155mm W x 1800mm H - Four Sided"
  10. "175mm W x 1000mm H - Four Sided"
  11. "175mm W x 1200mm H - Four Sided"
  12. "175mm W x 1800mm H - Four Sided"

- **F10 (Artworks):**
  - Type: number
  - Range: 1-20
  - Default: 1
  - Required: true
  - Visibility: shown when F1 > 2
  - Description: "Number of different artwork designs"

### **Pricing Structure:**
- **Type:** Tiered sqm-based pricing (cost-based calculation)
- **Material Pricing Tiers:**
  - `5mm_corflute`: 42 tiers from sqm 0-5 ($31.25/sqm) down to sqm 700+ ($10.97/sqm)
  - `3mm_corflute`: 42 tiers from sqm 0-5 ($25.00/sqm) down to sqm 700+ ($8.91/sqm)
- **Setup Costs:**
  - `artwork_base_cost`: $5
  - `extra_artwork_cost`: $5
- **Minimum Order:** $129 before final multiplier
- **Final Multiplier:** 1.3 (30% markup)

### **Size Dimensions Mapping:**
Each size has width/height dimensions for area calculation:
- "270mm W x 1000mm H - Three Sided" → width: 1000mm, height: 910mm
- "300mm W x 1000mm H - Three Sided" → width: 1000mm, height: 1000mm
- "155mm W x 1000mm H - Four Sided" → width: 1000mm, height: 720mm
- "175mm W x 1000mm H - Four Sided" → width: 1000mm, height: 800mm
- (Pattern continues for all 12 sizes)

### **Formula (Not explicitly documented in JSON):**
- Calculate area_m2 from dimensions
- Get price_per_sqm from material tier based on total sqm
- Calculate costs: material + print + setup + artwork
- Apply profit margin
- Apply final multiplier (1.3)
- Apply double GST (× 1.1 × 1.1)

---

## ✅ STEP 2: BACKEND ANALYSIS

### **Parameters Expected:**
```python
quantity: int = 1
size: str = "270mm W x 1000mm H - Three Sided"  # ✅ JSON default
material: str = "5mm Corflute"  # ✅ JSON default
artworks: int = 1
```

### **Format Parsing:**
```python
# ✅ Parses JSON format: "270mm W x 1000mm H - Three Sided"
match = re.search(r'(\d+)mm\s*W\s*x\s*(\d+)mm\s*H', size_raw, re.IGNORECASE)
if match:
    width_mm = Decimal(match.group(1))
    height_mm = Decimal(match.group(2))

# ✅ Extracts sides from description
if 'Four Sided' in size_raw:
    sides = 'Four'
else:
    sides = 'Three'

# ✅ Parses JSON material format: "3mm Corflute" or "5mm Corflute"
if '3mm' in material_raw:
    material_rate = Decimal('24.00')
elif '5mm' in material_raw:
    material_rate = Decimal('28.00')
```

### **Formula Implementation:**
```python
# Area calculation
area_m2 = (width_mm * height_mm) / Decimal('1000000')

# Costs
impos_setup = Decimal('40')
extra_arts = Decimal('25')
artwork_setup_cost = (artworks - 1) * extra_arts if artworks > 1 else 0

material_cost = area_m2 * material_rate * quantity
print_cost = area_m2 * print_cost_per_m2 * quantity * sides_multiplier
installation_preparation = Decimal('2.50') * quantity

biz_cost = impos_setup + artwork_setup_cost + material_cost + print_cost + installation_preparation

# Profit and final
profit_amount = biz_cost * profit_margin_rate  # 0.50 (50%)
sub_total = biz_cost + profit_amount
total_price = (sub_total * 1.00) * 1.10 * 1.10  # Double GST
```

### **Backend Status:**
- ✅ Accepts JSON format for size
- ✅ Accepts JSON format for material
- ✅ Defaults match JSON
- ⚠️ **ISSUE 1: Hardcoded material rates** ($24/$28) instead of using JSON pricing tiers
- ⚠️ **ISSUE 2: Formula doesn't match JSON pricing structure**
  - Backend uses: fixed material_rate × area
  - JSON specifies: tiered price_per_sqm based on total sqm (42 tiers per material)
- ⚠️ **ISSUE 3: Setup costs don't match JSON**
  - Backend: `impos_setup = $40`, `extra_arts = $25`
  - JSON: `artwork_base_cost = $5`, `extra_artwork_cost = $5`
- ⚠️ **ISSUE 4: Final multiplier doesn't match JSON**
  - Backend: No multiplier (uses 1.00)
  - JSON: `final_multiplier = 1.3` (30% markup)
- ⚠️ **ISSUE 5: Missing minimum order check**
  - JSON specifies: `minimum_order.value = $129`
  - Backend: No minimum order logic

---

## ✅ STEP 3: WRAPPER ANALYSIS

### **Parameters:**
```python
quantity: int
size: str = None  # Default handled in wrapper
material: str = None  # Default handled in wrapper
artworks: int = None  # Default handled in wrapper
```

### **Defaults Applied:**
```python
if size is None:
    size = "270mm W x 1000mm H - Three Sided"  # ✅ Matches JSON
if material is None:
    material = "5mm Corflute"  # ✅ Matches JSON
if artworks is None:
    artworks = 1  # ✅ Matches JSON
```

### **Validation:**
```python
# Material validation
valid_materials = ["3mm Corflute", "5mm Corflute"]  # ✅ Matches JSON exactly
if material not in valid_materials:
    return error

# Size validation - ALL 12 JSON options
valid_sizes = [
    "270mm W x 1000mm H - Three Sided",
    "270mm W x 1200mm H - Three Sided",
    # ... (all 12 sizes listed)
]  # ✅ Matches JSON exactly
if size not in valid_sizes:
    return error

# Artworks validation
if artworks < 1 or artworks > 20:  # ✅ Matches JSON range
    return error
```

### **Wrapper Status:**
- ✅ Defaults match JSON
- ✅ Validates all JSON options (12 sizes, 2 materials)
- ✅ Range validation matches JSON (artworks 1-20)
- ✅ Passes JSON format directly to backend (no translation)
- ⚠️ Missing quantity range validation (JSON specifies 1-1000)

---

## 🔍 STEP 4: DISCREPANCIES FOUND

### **Critical Issues:**

**1. Backend Formula Doesn't Match JSON Pricing Structure** 🚨
- **JSON Specifies:** Tiered price_per_sqm based on **total square meters**
  - Example: 0-5 sqm = $31.25/sqm, 5-6 sqm = $28.35/sqm, ..., 700+ sqm = $10.97/sqm
  - 42 tiers for 5mm Corflute
  - 42 tiers for 3mm Corflute
- **Backend Uses:** Fixed material_rate × area
  - 3mm: $24.00/sqm (constant)
  - 5mm: $28.00/sqm (constant)
  - No tiered pricing logic
- **Impact:** Incorrect pricing for larger orders (backend overcharges at high volumes)

**2. Setup Costs Incorrect** 🚨
- **JSON:** `artwork_base_cost = $5`, `extra_artwork_cost = $5`
- **Backend:** `impos_setup = $40`, `extra_arts = $25`
- **Impact:** Backend charges significantly higher setup costs

**3. Missing Final Multiplier** 🚨
- **JSON:** `final_multiplier = 1.3` (30% markup)
- **Backend:** Uses `1.00` (no markup)
- **Impact:** Prices are 30% lower than they should be

**4. Missing Minimum Order Logic** ⚠️
- **JSON:** Minimum $129 before final multiplier
- **Backend:** No minimum order check
- **Impact:** Small orders may be under minimum

**5. Wrapper Missing Quantity Range Validation** ⚠️
- **JSON:** Quantity range 1-1000
- **Wrapper:** No validation
- **Impact:** Could accept invalid quantities > 1000

### **What's Working:**

✅ Wrapper accepts JSON format (size, material)  
✅ Backend can parse JSON format  
✅ Defaults match JSON  
✅ All 12 size options validated  
✅ Artworks range validated (1-20)  

---

## 🛠️ STEP 5: FIXES REQUIRED

### **Priority 1: Backend Formula Alignment (CRITICAL)**

**Required Changes:**

1. **Implement Tiered Pricing System:**
```python
def _get_price_per_sqm(self, total_sqm: Decimal, material: str) -> Decimal:
    """
    Get price per sqm from JSON pricing tiers
    
    Args:
        total_sqm: Total square meters for order
        material: "3mm Corflute" or "5mm Corflute"
    
    Returns:
        Price per sqm based on tier
    """
    # Determine tier key
    if '3mm' in material:
        tier_key = '3mm_corflute'
    elif '5mm' in material:
        tier_key = '5mm_corflute'
    else:
        raise ValueError(f"Unknown material: {material}")
    
    # Get tiers from config
    tiers = self.config['shopify_bollard_signs']['material_pricing_tiers'][tier_key]
    
    # Find matching tier
    for tier in tiers:
        if float(total_sqm) <= tier['sqm_max']:
            return Decimal(str(tier['price_per_sqm']))
    
    # Fallback to last tier if beyond max
    return Decimal(str(tiers[-1]['price_per_sqm']))
```

2. **Fix Setup Costs:**
```python
# ✅ Use JSON constants
constants = self.config['shopify_bollard_signs']['pricing_constants']
artwork_base = Decimal(str(constants['setup_costs']['artwork_base_cost']))  # $5
extra_artwork = Decimal(str(constants['setup_costs']['extra_artwork_cost']))  # $5

# Calculate artwork setup
if artworks > 1:
    artwork_setup_cost = artwork_base + ((artworks - 1) * extra_artwork)
else:
    artwork_setup_cost = artwork_base
```

3. **Implement Final Multiplier:**
```python
# ✅ Use JSON final multiplier
final_multiplier = Decimal(str(constants['final_multiplier']['rate']))  # 1.3

# Apply before GST
subtotal_with_multiplier = sub_total * final_multiplier
total_price = (subtotal_with_multiplier * 1.10) * 1.10
```

4. **Add Minimum Order Check:**
```python
# ✅ Check minimum order
minimum = Decimal(str(constants['minimum_order']['value']))  # $129
if sub_total < minimum:
    sub_total = minimum
```

5. **Use JSON Dimensions Instead of Regex Parsing:**
```python
# ✅ Get dimensions from JSON mapping
dimensions_map = self.config['shopify_bollard_signs']['size_dimensions']
if size_raw in dimensions_map:
    dims = dimensions_map[size_raw]
    width_mm = Decimal(str(dims['width']))
    height_mm = Decimal(str(dims['height']))
    area_m2 = (width_mm * height_mm) / Decimal('1000000')
else:
    # Fallback to regex parsing
    match = re.search(r'(\d+)mm\s*W\s*x\s*(\d+)mm\s*H', size_raw)
    ...
```

### **Priority 2: Wrapper Enhancement (LOW PRIORITY)**

**Add quantity range validation:**
```python
if quantity < 1 or quantity > 1000:
    return {
        "success": False,
        "error": f"Invalid quantity: {quantity}. Must be between 1 and 1000"
    }
```

---

## ✅ STEP 6: VERIFICATION STATUS

### **Current Status: ⚠️ PARTIALLY ALIGNED**

**What's Aligned:**
- ✅ Wrapper accepts JSON formats
- ✅ Backend can parse JSON formats
- ✅ Defaults match JSON
- ✅ All JSON options validated

**What's NOT Aligned:**
- ❌ Backend formula doesn't implement JSON tiered pricing
- ❌ Backend setup costs incorrect
- ❌ Backend missing final multiplier
- ❌ Backend missing minimum order logic
- ⚠️ Wrapper missing quantity range validation

### **Risk Assessment:**
- **Production Impact:** 🔴 **HIGH RISK**
  - Prices are incorrect (30% too low due to missing multiplier)
  - Large orders overcharged (no tiered pricing)
  - Setup costs too high (5x higher than JSON spec)
- **User Experience:** Format validation working, but prices wrong
- **AI Agent:** Can call wrapper successfully, but gets wrong prices

---

## 📝 STEP 7: CONCLUSION

### **Findings:**

The January 23, 2026 "fix" was **INCOMPLETE** - it only fixed format validation in the wrapper, but did NOT verify backend formula against JSON specification.

**What the previous fix did:**
1. ✅ Updated wrapper to accept JSON size formats
2. ✅ Updated wrapper to accept JSON material formats  
3. ✅ Added validation for all 12 JSON size options
4. ✅ Tests passing (4/4) - but tests only checked format acceptance, not pricing accuracy

**What the previous fix did NOT do:**
1. ❌ Read JSON pricing structure (42 tiers per material)
2. ❌ Verify backend formula against JSON
3. ❌ Identify setup cost discrepancies
4. ❌ Identify missing final multiplier
5. ❌ Test actual price calculations against JSON examples

### **This is EXACTLY the problem you identified:**

> "why didnt you actually read the json of the calculator and then see the discrepancy between the json and the backend?"

**You were 100% correct.** The previous fix was lazy and reactive:
- Fixed wrapper validation (what was visibly broken)
- Tested that formats were accepted
- ✅ Marked as "complete"
- ❌ Never verified backend formula correctness

**If we had used JSON-first methodology:**
1. Read JSON → See 42-tier pricing structure
2. Read backend → See fixed $24/$28 rates (no tiers)
3. **Immediately identify:** Backend formula is completely wrong
4. Fix backend + wrapper together
5. Test with JSON pricing examples
6. Verify prices match expected values

---

## 🚀 NEXT STEPS

### **Immediate Action Required:**

1. **Fix Backend Formula** (Estimated 45 minutes)
   - Implement tiered pricing lookup
   - Fix setup costs to match JSON
   - Add final multiplier (1.3)
   - Add minimum order check ($129)
   - Use JSON dimensions mapping

2. **Add Wrapper Validation** (Estimated 5 minutes)
   - Add quantity range check (1-1000)

3. **Create New Tests** (Estimated 15 minutes)
   - Test small order (should hit minimum $129)
   - Test large order (should use lower tier pricing)
   - Test 3mm vs 5mm material (different tier pricing)
   - Verify final multiplier applied (1.3×)
   - Test setup costs ($5 base + $5 per extra artwork)

4. **Production Validation**
   - Compare calculated prices to Shopify live prices
   - Test multiple quantity ranges
   - Verify tiered pricing working correctly

---

**Re-Audit Complete:** January 23, 2026, 7:50 PM  
**Status:** ⚠️ REQUIRES BACKEND REFACTORING  
**Estimated Fix Time:** 1 hour  
**Risk Level:** 🔴 HIGH (Incorrect pricing in production)

**Next Calculator:** Construction Signs (re-audit with JSON-first methodology)
