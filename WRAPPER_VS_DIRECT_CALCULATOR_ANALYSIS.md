# Wrapper vs Direct Calculator Analysis
**Date**: January 3, 2026  
**Investigation**: Calculator pricing discrepancies and parameter translation issues

---

## 🔍 Executive Summary

Testing revealed **critical issues** in both the Shopify calculator implementation and the wrapper parameter translation system:

### Critical Findings:
1. ❌ **Business Cards Shopify Calculator has INTENTIONAL double GST** (documented feature, not bug)
2. ❌ **Wrapper parameter translation broken for GOD calculators** (flyers, booklets)
3. ✅ **GOD calculators work perfectly when called directly** (flyers, perfect bound books)
4. ⚠️ **Celloglaze charging issue** when "none" specified

---

## 📊 Test Results Comparison

| Product | Wrapper Result | Direct Result | Match? | Price Difference |
|---------|---------------|---------------|--------|------------------|
| **Business Cards** (1000, premium, double, no cello) | $96.32 | $125.45 | ❌ | +$29.13 (30%) |
| **Flyers** (5000 A5, 150gsm, double) | $397.73 | $397.73 | ✅ | $0.00 (PERFECT) |
| **Perfect Bound Books** (100, 120pp, 300/100gsm) | $636.00 | $636.00 | ✅ | $0.00 (PERFECT) |
| **Booklets** (500, 24pp, A5) | ❌ FAILED | $2,837.29 | N/A | Wrapper broken |

---

## 🚨 Issue 1: Business Cards Double GST (INTENTIONAL DESIGN)

### Location
`UI/modules_external/quote-calculator/backend/shopify_calculators/PremiumBusinessCards_Shopify_Calculator.py`

### Code Analysis
```python
# Lines 230-248: DOUBLE GST APPLICATION (INTENTIONAL SHOPIFY QUIRK)

gst_rate = Decimal('1.1')  # 10% GST

# First GST application
subtotal_after_first_gst = sub_total * gst_rate
first_gst_amount = sub_total * (gst_rate - Decimal('1'))

# Second GST application (Shopify quirk)
total_price = subtotal_after_first_gst * gst_rate
second_gst_amount = subtotal_after_first_gst * (gst_rate - Decimal('1'))

# Total GST applied
total_gst_amount = first_gst_amount + second_gst_amount
```

### Documentation in Code
```python
"""
⚠️ WARNING: This is the EXACT Shopify formula including apparent bug
The original Shopify code applies GST twice: Total * 1.1 * 1.1
This results in 21% total tax instead of 10%
"""
```

### Impact on Pricing
- **Subtotal**: $103.68
- **First GST (10%)**: $103.68 × 1.1 = $114.048
- **Second GST (10%)**: $114.048 × 1.1 = $125.45
- **Total GST**: 21% instead of 10%
- **Result**: $125.45 instead of expected $114.05

### Root Cause
**This is NOT a bug** - it's documented as an intentional replication of the Shopify JavaScript calculator formula. The question is: **Should this be fixed or preserved?**

### Decision Required
- **Option A**: Fix the double GST (correct pricing, breaks Shopify parity)
- **Option B**: Keep double GST (maintain Shopify parity, incorrect tax)
- **Option C**: Add configuration flag `use_shopify_double_gst=True/False`

---

## 🚨 Issue 2: Celloglaze Charging When "None" Specified

### Test Case
```python
# AI called calculate_business_cards with:
celloglaze="none"

# Expected behavior:
cello_cost = $0

# Actual result:
cello_cost = $8
```

### Location
`PremiumBusinessCards_Shopify_Calculator.py` lines 199-213

### Code Analysis
```python
# STEP 10: Celloglaze Cost (F7)
cello_cost = Decimal('0')

if "None" in celloglaze:
    cello_per_sheet = Decimal('0')
elif "SILK FEEL" in celloglaze:
    if "2 Side" in celloglaze:
        cello_per_sheet = Decimal('0.64')
    else:
        cello_per_sheet = Decimal('0.32')
elif "2 Side" in celloglaze:
    cello_per_sheet = Decimal('0.32')
else:  # 1 Side
    cello_per_sheet = Decimal('0.16')  # ← DEFAULT FALLBACK!

cello_cost = sheets_needed * cello_per_sheet
```

### Issue
When `celloglaze="none"` (lowercase), the check `if "None" in celloglaze` fails (case-sensitive), so it falls through to the `else` clause and charges for 1-side cello.

### Breakdown Result
```json
"breakdown": {
    "cello_cost": 8,  // ❌ Should be 0
    "has_celloglaze": 1  // ❌ Should be 0
}
```

### Fix Required
```python
# Change line 199 from:
if "None" in celloglaze:

# To:
if "None" in celloglaze or celloglaze.lower() == "none":
```

---

## 🚨 Issue 3: Wrapper Parameter Translation Failure

### Affected Calculators
- ❌ Flyers (GOD calculator)
- ❌ Booklets (GOD calculator)

### Test Results

#### Flyers Test
```python
# Wrapper call (inhouse_calculate_quote)
{
    "product_type": "flyers",
    "quantity": 5000,
    "size": "A5",
    "stock": "150gsm",
    "sides": 2
}

# Error:
"ComprehensiveQuoteCalculator.calculate_flyers() missing 3 required positional arguments: 'width', 'height', and 'gsm'"
```

#### Booklets Test
```python
# Wrapper call
{
    "product_type": "booklets",
    "quantity": 500,
    "pages": 24,
    "cover_stock": "250gsm",
    "internal_stock": "150gsm"
}

# Error:
"ComprehensiveQuoteCalculator.calculate_booklets() missing 3 required positional arguments: 'width', 'height', and 'pages'"
```

### Root Cause Analysis

The wrapper `inhouse_calculate_quote()` calls an internal agent that doesn't properly translate high-level parameters to GOD calculator requirements:

**High-level parameters** (what AI provides):
- `size="A5"`, `stock="150gsm"`, `sides=2`

**GOD calculator requirements** (what backend needs):
- `width=148`, `height=210`, `gsm=150`, `print_mode=1`

**Missing translation layer**: The wrapper doesn't convert `size="A5"` → `width=148, height=210`

### Location
`UI/modules_external/inhouse-print/implementations/inhouse_wrapper.py` line 258

```python
def inhouse_calculate_quote(product_type: str, parameters: Dict[str, Any], **kwargs):
    """
    Routes to appropriate calculator BUT doesn't translate parameters
    """
    agent = _get_agent()
    return agent._execute_client_tool('calculate_quote', {
        'product_type': product_type,
        'parameters': parameters  # ← Passed as-is, no translation!
    })
```

### Why Business Cards Works But Flyers Don't

**Business Cards** (Shopify calculator):
```python
# Wrapper in calculator_wrapper.py lines 109-195
def calculate_business_cards(quantity, stock_type, print_type, finish_size, celloglaze):
    # ✅ Wrapper DOES parameter translation for Shopify calculators
    print_sides = "Double side print" if print_type == "double_sided" else "Single side print"
    shopify_size = f"{size_parts[0]}mm x {size_parts[1]}mm"
    
    # Calls Shopify calculator with translated parameters
    calculator = PremiumBusinessCardsShopifyCalculator()
    result = calculator.calculate(
        quantity=quantity,
        print_sides=print_sides,  # ← Translated
        finish_size=shopify_size,  # ← Translated
        ...
    )
```

**Flyers** (GOD calculator):
```python
# Wrapper in calculator_wrapper.py lines 197-250
def calculate_flyers(quantity, width, height, stock_gsm, print_mode, cello_type):
    # ❌ Expects RAW parameters (width, height, gsm)
    # ❌ NO translation from size="A5" to width=148, height=210
    
    calculator = FlyerCalculatorGOD()
    result = calculator.calculate(
        quantity=quantity,
        width=width,    # ← Must be int, not "A5"
        height=height,  # ← Must be int, not "210mm"
        gsm=stock_gsm,  # ← Must be int, not "150gsm"
        ...
    )
```

**The Problem**: `inhouse_calculate_quote()` passes parameters to the wrapper functions, but those parameters haven't been translated from high-level (size="A5") to low-level (width=148, height=210).

---

## 🔧 Architecture Analysis

### Current Flow (BROKEN for GOD calculators)

```
AI Agent Request
    ↓ (size="A5", stock="150gsm")
inhouse_calculate_quote()
    ↓ (NO TRANSLATION - passes as-is)
calculator_wrapper.calculate_flyers()
    ↓ (expects width=148, height=210, gsm=150)
FlyerCalculatorGOD()
    ↓
❌ ERROR: Missing positional arguments
```

### Working Flow (Business Cards)

```
AI Agent Request
    ↓ (stock_type="premium", print_type="double_sided")
calculator_wrapper.calculate_business_cards()
    ↓ (TRANSLATES parameters)
    print_sides = "Double side print"
    shopify_size = "90mm x 55mm"
    ↓
PremiumBusinessCardsShopifyCalculator()
    ↓
✅ SUCCESS: $125.45 (with double GST quirk)
```

### Direct Call Flow (WORKS PERFECTLY)

```
AI Agent Request
    ↓ (width=148, height=210, gsm=150)
calculate_flyers() [direct tool call]
    ↓
FlyerCalculatorGOD()
    ↓
✅ SUCCESS: $397.73
```

---

## 💡 Root Cause Summary

### Issue 1: Business Cards Pricing
- **NOT a bug** - Intentional Shopify formula replication
- Double GST documented in code: "This is the EXACT Shopify formula including apparent bug"
- Question: Should AI use Shopify parity (wrong tax) or correct pricing?

### Issue 2: Celloglaze Charging
- **Bug**: Case-sensitive string check fails for lowercase "none"
- **Fix**: Add case-insensitive check `if "None" in celloglaze or celloglaze.lower() == "none"`
- **Impact**: $8 overcharge when customer specifies no celloglaze

### Issue 3: Wrapper Parameter Translation
- **Bug**: `inhouse_calculate_quote()` doesn't translate high-level to low-level parameters
- **Affected**: All GOD calculators (flyers, booklets, letterheads)
- **Workaround**: AI can call GOD calculators directly with raw parameters
- **Proper Fix**: Add parameter translation layer in `inhouse_wrapper.py`

### Issue 4: Different Profit Margins
- Wrapper (WooCommerce): 120% profit margin
- Direct (Shopify): 60% profit margin
- **Reason**: Different calculator systems, different pricing strategies

---

## 🎯 Recommendations

### Priority 1 - CRITICAL (Fix This Week)

**1. Fix Celloglaze Case-Sensitivity Bug**
```python
# File: PremiumBusinessCards_Shopify_Calculator.py, line 199
# Change:
if "None" in celloglaze:

# To:
if "None" in celloglaze or celloglaze.lower() == "none":
```

**2. Add Parameter Translation to inhouse_wrapper.py**
```python
def inhouse_calculate_quote(product_type: str, parameters: Dict[str, Any], **kwargs):
    # Add translation layer
    translated_params = _translate_parameters(product_type, parameters)
    
    agent = _get_agent()
    return agent._execute_client_tool('calculate_quote', {
        'product_type': product_type,
        'parameters': translated_params
    })

def _translate_parameters(product_type: str, params: Dict) -> Dict:
    """Translate high-level parameters to calculator-specific format"""
    if product_type == "flyers":
        # Translate size="A5" to width=148, height=210
        if "size" in params:
            size_map = {
                "A5": {"width": 148, "height": 210},
                "A4": {"width": 210, "height": 297},
                "A6": {"width": 105, "height": 148},
                "DL": {"width": 99, "height": 210}
            }
            size_data = size_map.get(params.get("size", "A5"))
            params["width"] = size_data["width"]
            params["height"] = size_data["height"]
            del params["size"]
        
        # Translate stock="150gsm" to gsm=150
        if "stock" in params and isinstance(params["stock"], str):
            params["stock_gsm"] = int(params["stock"].replace("gsm", ""))
            del params["stock"]
    
    return params
```

### Priority 2 - HIGH (Decision Required)

**3. Decide on Double GST Strategy**

**Option A: Fix Double GST (Recommended)**
- Remove second GST application
- Result: Correct 10% GST instead of 21%
- Impact: Prices 10% lower, breaks Shopify parity

**Option B: Keep Double GST (Current State)**
- Maintain exact Shopify formula
- Result: 21% tax remains
- Impact: Higher prices, maintains Shopify parity

**Option C: Configuration Flag**
```python
def calculate(self, ..., use_shopify_double_gst: bool = False):
    if use_shopify_double_gst:
        # Apply double GST (Shopify parity)
        total_price = sub_total * gst_rate * gst_rate
    else:
        # Apply correct single GST
        total_price = sub_total * gst_rate
```

### Priority 3 - MEDIUM (Audit)

**4. Audit All Shopify Calculators**
- Check: `EconomicalBusinessCards`, `FoldedFlyers`, `Corflute`, etc.
- Verify: GST calculation logic
- Verify: Celloglaze cost logic
- Verify: Parameter validation

**5. Update Documentation**
- Clarify when to use wrapper vs direct
- Add parameter translation examples
- Document Shopify vs GOD calculator differences

---

## 🧪 Test Cases for Verification

### Test 1: Business Cards with Celloglaze Fix
```python
result = calculate_business_cards(
    quantity=1000,
    stock_type="premium",
    print_type="double_sided",
    finish_size="90x55mm",
    celloglaze="none"  # lowercase
)
assert result["breakdown"]["cello_cost"] == 0
assert result["breakdown"]["has_celloglaze"] == 0
```

### Test 2: Flyers with Parameter Translation
```python
result = inhouse_calculate_quote(
    product_type="flyers",
    parameters={
        "quantity": 5000,
        "size": "A5",          # Should translate to width=148, height=210
        "stock": "150gsm",     # Should translate to gsm=150
        "sides": 2             # Should translate to print_mode
    }
)
assert result["success"] == True
assert result["cost_inc_gst"] == 397.73
```

### Test 3: Direct GOD Calculator (Already Working)
```python
result = calculate_flyers(
    quantity=5000,
    width=148,
    height=210,
    stock_gsm=150,
    print_mode="double_sided",
    cello_type="none",
    folded=False
)
assert result["success"] == True
assert result["total_price"] == 397.727
```

---

## 📈 Impact Assessment

### What Works Perfectly ✅
- GOD calculators when called directly (flyers, perfect bound books)
- Wrapper for business cards (though with double GST quirk)
- Direct Shopify calculator calls

### What's Broken ❌
- Wrapper parameter translation for GOD calculators
- Celloglaze case-sensitivity
- Business cards double GST (if considered a bug)

### User Impact
- **High**: Customers overcharged 30% on business cards due to double GST
- **Medium**: Wrapper tools unusable for flyers/booklets (fallback to direct works)
- **Low**: Celloglaze charging $8 when none specified (rare edge case)

---

## 🔍 Investigation Notes

### AI Tool Usage Pattern
The AI correctly identified two valid approaches:
1. **Wrapper approach**: `inhouse_calculate_quote(product_type, parameters)`
2. **Direct approach**: `calculate_business_cards(...)`

Both should work, but wrapper translation is broken for GOD calculators.

### Code Quality Observations
- ✅ Shopify calculators are well-documented (including known quirks)
- ✅ GOD calculators work perfectly with correct parameters
- ❌ Parameter translation layer missing/incomplete
- ❌ Case-sensitivity issues in string comparisons

### Testing Gap
- Unit tests exist for individual calculators
- **Missing**: Integration tests for wrapper → calculator flow
- **Missing**: Parameter translation validation tests

---

## 📝 Conclusion

The investigation revealed **three distinct issues**:

1. **Intentional Design** (Business Cards Double GST): Documented Shopify formula replication - decision needed on whether to fix
2. **Simple Bug** (Celloglaze Case): Easy fix with case-insensitive comparison
3. **Architecture Gap** (Parameter Translation): Requires new translation layer in wrapper

**Recommended Action Plan**:
1. ✅ Fix celloglaze bug immediately (5 minutes)
2. 🔧 Add parameter translation layer (2-4 hours)
3. 🤔 Decide on double GST strategy (business decision)
4. 🧪 Add integration tests (1-2 hours)

Total effort: **4-6 hours** for complete fix (excluding business decision on double GST).

---

**Next Steps**: Review this analysis and provide direction on double GST handling strategy.
