# Calculator Code Fixes - Implementation Guide
**Date**: January 3, 2026  
**Purpose**: Step-by-step fixes for wrapper vs direct calculator issues

---

## 🎯 Fix #1: Celloglaze Case-Sensitivity Bug (CRITICAL)

### Priority: 🔴 CRITICAL - Fix Today
### Effort: ⏱️ 5 minutes
### Impact: 💰 Prevents $8 overcharge per order

### Location
`UI/modules_external/quote-calculator/backend/shopify_calculators/PremiumBusinessCards_Shopify_Calculator.py`

### Current Code (Lines 199-213)
```python
# STEP 10: Celloglaze Cost (F7)
cello_cost = Decimal('0')

if "None" in celloglaze:  # ❌ CASE SENSITIVE - FAILS FOR "none"
    cello_per_sheet = Decimal('0')
elif "SILK FEEL" in celloglaze:
    if "2 Side" in celloglaze:
        cello_per_sheet = Decimal('0.64')
    else:
        cello_per_sheet = Decimal('0.32')
elif "2 Side" in celloglaze:
    cello_per_sheet = Decimal('0.32')
else:  # 1 Side - DEFAULT FALLBACK
    cello_per_sheet = Decimal('0.16')  # ❌ CHARGES $8 FOR "none"

cello_cost = sheets_needed * cello_per_sheet
```

### Fixed Code
```python
# STEP 10: Celloglaze Cost (F7)
cello_cost = Decimal('0')

# ✅ FIX: Case-insensitive check for "none"
if "None" in celloglaze or celloglaze.lower() == "none":
    cello_per_sheet = Decimal('0')
elif "SILK FEEL" in celloglaze:
    if "2 Side" in celloglaze:
        cello_per_sheet = Decimal('0.64')
    else:
        cello_per_sheet = Decimal('0.32')
elif "2 Side" in celloglaze:
    cello_per_sheet = Decimal('0.32')
else:  # 1 Side
    cello_per_sheet = Decimal('0.16')

cello_cost = sheets_needed * cello_per_sheet
```

### Test Case
```python
# Test 1: Uppercase "None"
result = calculator.calculate(
    quantity=1000,
    celloglaze="None"
)
assert result.breakdown['cello_cost'] == 0

# Test 2: Lowercase "none"
result = calculator.calculate(
    quantity=1000,
    celloglaze="none"
)
assert result.breakdown['cello_cost'] == 0

# Test 3: 1 Side Gloss (should still charge)
result = calculator.calculate(
    quantity=1000,
    celloglaze="1 Side Gloss"
)
assert result.breakdown['cello_cost'] > 0
```

### Rollout
1. ✅ Update `PremiumBusinessCards_Shopify_Calculator.py`
2. ✅ Run test cases
3. ✅ Check `EconomicalBusinessCards_Shopify_Calculator.py` for same issue
4. ✅ Deploy immediately

---

## 🎯 Fix #2: Parameter Translation Layer (HIGH PRIORITY)

### Priority: 🟠 HIGH - Fix This Week
### Effort: ⏱️ 2-4 hours
### Impact: 🔧 Makes wrapper work for GOD calculators

### Problem
```python
# AI calls wrapper with high-level parameters
inhouse_calculate_quote(
    product_type="flyers",
    parameters={
        "size": "A5",        # ❌ GOD calculator needs width=148, height=210
        "stock": "150gsm",   # ❌ GOD calculator needs gsm=150
        "sides": 2           # ❌ GOD calculator needs print_mode="double_sided"
    }
)

# Result: Missing positional arguments error
```

### Solution Architecture

#### Step 1: Create Translation Module
**File**: `UI/modules_external/inhouse-print/implementations/parameter_translator.py`

```python
"""
Parameter Translation Layer for InHouse Print Calculators

Translates high-level AI-friendly parameters to calculator-specific formats.

HIGH-LEVEL (AI provides):
    - size="A5", stock="150gsm", sides=2
    
LOW-LEVEL (GOD calculator needs):
    - width=148, height=210, gsm=150, print_mode="double_sided"

LAST MODIFIED: 2026-01-03 - Initial implementation
"""

from typing import Dict, Any
from decimal import Decimal

# ============================================================================
# SIZE TRANSLATION MAPS
# ============================================================================

STANDARD_SIZES = {
    "A3": {"width": 297, "height": 420},
    "A4": {"width": 210, "height": 297},
    "A5": {"width": 148, "height": 210},
    "A6": {"width": 105, "height": 148},
    "DL": {"width": 99, "height": 210},
    "business_card": {"width": 90, "height": 55},
    "90x55mm": {"width": 90, "height": 55},
    "90x50mm": {"width": 90, "height": 50},
    "85x55mm": {"width": 85, "height": 55}
}

# ============================================================================
# STOCK TRANSLATION
# ============================================================================

def parse_stock(stock_str: str) -> Dict[str, Any]:
    """
    Parse stock string to GSM and type
    
    Examples:
        "150gsm" → {"gsm": 150}
        "Satin 350GSM" → {"gsm": 350, "type": "satin"}
        "300gsm matt" → {"gsm": 300, "type": "matt"}
    """
    stock_str = stock_str.lower().strip()
    
    # Extract GSM
    import re
    gsm_match = re.search(r'(\d+)\s*gsm', stock_str)
    gsm = int(gsm_match.group(1)) if gsm_match else None
    
    # Extract type
    stock_type = None
    if "satin" in stock_str:
        stock_type = "satin"
    elif "gloss" in stock_str:
        stock_type = "gloss"
    elif "matt" in stock_str or "matte" in stock_str:
        stock_type = "matt"
    elif "uncoated" in stock_str or "bond" in stock_str:
        stock_type = "uncoated"
    
    return {"gsm": gsm, "type": stock_type}

# ============================================================================
# PRINT MODE TRANSLATION
# ============================================================================

def translate_print_mode(sides: Any, print_type: str = None) -> str:
    """
    Translate sides and print_type to print_mode
    
    Examples:
        sides=1 → "single_sided"
        sides=2 → "double_sided"
        sides=2, print_type="color" → "double_sided"
        sides=2, print_type="bw" → "black_white"
    """
    if isinstance(sides, str):
        if "double" in sides.lower():
            return "double_sided"
        elif "single" in sides.lower():
            return "single_sided"
    
    if sides == 2:
        if print_type and "bw" in print_type.lower():
            return "black_white"
        return "double_sided"
    elif sides == 1:
        return "single_sided"
    
    return "single_sided"  # default

# ============================================================================
# PRODUCT-SPECIFIC TRANSLATORS
# ============================================================================

def translate_flyers_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translate flyers parameters from high-level to GOD calculator format
    
    HIGH-LEVEL INPUT:
        {
            "quantity": 5000,
            "size": "A5",
            "stock": "150gsm",
            "sides": 2,
            "cello": "none"
        }
    
    GOD CALCULATOR OUTPUT:
        {
            "quantity": 5000,
            "width": 148,
            "height": 210,
            "stock_gsm": 150,
            "print_mode": "double_sided",
            "cello_type": "none",
            "folded": false
        }
    """
    translated = params.copy()
    
    # Translate size to width/height
    if "size" in params:
        size_str = params["size"].upper()
        if size_str in STANDARD_SIZES:
            translated["width"] = STANDARD_SIZES[size_str]["width"]
            translated["height"] = STANDARD_SIZES[size_str]["height"]
            del translated["size"]
    
    # Translate stock to gsm
    if "stock" in params:
        stock_info = parse_stock(params["stock"])
        if stock_info["gsm"]:
            translated["stock_gsm"] = stock_info["gsm"]
        del translated["stock"]
    
    # Translate sides to print_mode
    if "sides" in params:
        print_type = params.get("print_type")
        translated["print_mode"] = translate_print_mode(params["sides"], print_type)
        del translated["sides"]
    
    # Ensure cello_type exists
    if "cello" in params:
        translated["cello_type"] = params["cello"]
        del translated["cello"]
    elif "cello_type" not in translated:
        translated["cello_type"] = "none"
    
    # Ensure folded exists
    if "folded" not in translated:
        translated["folded"] = False
    
    return translated


def translate_booklets_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translate booklets parameters
    
    HIGH-LEVEL INPUT:
        {
            "quantity": 500,
            "pages": 24,
            "size": "A5",
            "cover_stock": "250gsm",
            "internal_stock": "150gsm"
        }
    
    GOD CALCULATOR OUTPUT:
        {
            "quantity": 500,
            "width": 148,
            "height": 210,
            "pages": 24,
            "cover_gsm": 250,
            "internal_gsm": 150,
            "stock_type_id": 29,
            "cover_stock_type_id": 20
        }
    """
    translated = params.copy()
    
    # Translate size
    if "size" in params:
        size_str = params["size"].upper()
        if size_str in STANDARD_SIZES:
            translated["width"] = STANDARD_SIZES[size_str]["width"]
            translated["height"] = STANDARD_SIZES[size_str]["height"]
            del translated["size"]
    
    # Translate cover_stock
    if "cover_stock" in params:
        stock_info = parse_stock(params["cover_stock"])
        if stock_info["gsm"]:
            translated["cover_gsm"] = stock_info["gsm"]
        del translated["cover_stock"]
    
    # Translate internal_stock
    if "internal_stock" in params:
        stock_info = parse_stock(params["internal_stock"])
        if stock_info["gsm"]:
            translated["internal_gsm"] = stock_info["gsm"]
        del translated["internal_stock"]
    
    # Add default stock_type_id if not present (most common)
    if "stock_type_id" not in translated:
        translated["stock_type_id"] = 29  # Uncoated (most common for booklets)
    
    if "cover_stock_type_id" not in translated:
        translated["cover_stock_type_id"] = 20  # Satin (most common for covers)
    
    return translated


def translate_perfect_bound_books_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translate perfect bound books parameters
    
    Similar to booklets but with additional binding parameters
    """
    translated = translate_booklets_parameters(params)
    
    # Add binding-specific parameters
    if "binding_type" not in translated:
        translated["binding_type"] = "Perfect Bound"
    
    if "cello_type" not in translated:
        translated["cello_type"] = 0  # No cello by default
    
    return translated


def translate_business_cards_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translate business cards parameters
    
    Business cards use Shopify calculator, minimal translation needed
    """
    translated = params.copy()
    
    # Ensure finish_size is in correct format
    if "size" in params:
        size = params["size"]
        if size == "standard":
            translated["finish_size"] = "90x55mm"
        elif size == "small":
            translated["finish_size"] = "90x45mm"
        else:
            translated["finish_size"] = size
        del translated["size"]
    
    return translated

# ============================================================================
# MAIN TRANSLATION FUNCTION
# ============================================================================

def translate_parameters(product_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main translation function - routes to product-specific translator
    
    Args:
        product_type: Calculator type (flyers, booklets, etc.)
        parameters: High-level parameters from AI
    
    Returns:
        Translated parameters ready for calculator
    """
    translators = {
        "flyers": translate_flyers_parameters,
        "booklets": translate_booklets_parameters,
        "perfect_bound_books": translate_perfect_bound_books_parameters,
        "business_cards": translate_business_cards_parameters,
        "letterheads": translate_flyers_parameters,  # Same structure as flyers
    }
    
    translator = translators.get(product_type)
    
    if translator:
        return translator(parameters)
    else:
        # No translation needed, pass through
        return parameters
```

#### Step 2: Update inhouse_wrapper.py

**File**: `UI/modules_external/inhouse-print/implementations/inhouse_wrapper.py`

**Before (Lines 258-303):**
```python
def inhouse_calculate_quote(product_type: str, parameters: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Calculate quote for InHouse Print product"""
    agent = _get_agent()
    return agent._execute_client_tool('calculate_quote', {
        'product_type': product_type,
        'parameters': parameters  # ❌ NO TRANSLATION
    })
```

**After:**
```python
def inhouse_calculate_quote(product_type: str, parameters: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Calculate quote for InHouse Print product
    
    NOW WITH PARAMETER TRANSLATION:
    - Converts high-level parameters (size="A5") to low-level (width=148, height=210)
    - Works with both GOD calculators and Shopify calculators
    """
    # ✅ NEW: Import translator
    from parameter_translator import translate_parameters
    
    # ✅ NEW: Translate parameters before passing to calculator
    try:
        translated_params = translate_parameters(product_type, parameters)
    except Exception as e:
        # If translation fails, pass through original parameters
        print(f"⚠️ Parameter translation failed: {e}")
        translated_params = parameters
    
    agent = _get_agent()
    return agent._execute_client_tool('calculate_quote', {
        'product_type': product_type,
        'parameters': translated_params  # ✅ TRANSLATED PARAMETERS
    })
```

### Test Cases

#### Test 1: Flyers with Size Translation
```python
def test_flyers_size_translation():
    result = inhouse_calculate_quote(
        product_type="flyers",
        parameters={
            "quantity": 5000,
            "size": "A5",           # ← High-level
            "stock": "150gsm",      # ← High-level
            "sides": 2              # ← High-level
        }
    )
    
    assert result["success"] == True
    assert result["cost_inc_gst"] == 397.73
```

#### Test 2: Booklets with Stock Translation
```python
def test_booklets_stock_translation():
    result = inhouse_calculate_quote(
        product_type="booklets",
        parameters={
            "quantity": 500,
            "pages": 24,
            "size": "A5",                    # ← High-level
            "cover_stock": "Satin 250gsm",   # ← High-level
            "internal_stock": "150gsm"       # ← High-level
        }
    )
    
    assert result["success"] == True
    assert "total_price" in result
```

#### Test 3: Business Cards (Should Still Work)
```python
def test_business_cards_passthrough():
    result = inhouse_calculate_quote(
        product_type="business_cards",
        parameters={
            "quantity": 1000,
            "stock_type": "premium",
            "print_type": "double_sided",
            "celloglaze": "none"
        }
    )
    
    assert result["success"] == True
```

### Rollout Plan

**Phase 1: Translation Module** (1 hour)
1. Create `parameter_translator.py`
2. Add unit tests for each translator function
3. Verify translation logic with sample inputs

**Phase 2: Integration** (1 hour)
1. Update `inhouse_wrapper.py` to use translator
2. Add error handling for translation failures
3. Ensure backward compatibility (pass through if translation fails)

**Phase 3: Testing** (1-2 hours)
1. Test flyers with various sizes
2. Test booklets with different stock combinations
3. Test business cards (ensure no regression)
4. Test edge cases (custom sizes, missing parameters)

**Phase 4: Deployment** (30 minutes)
1. Deploy to staging
2. Run integration tests
3. Deploy to production

---

## 🎯 Fix #3: Double GST Strategy Decision (BUSINESS DECISION)

### Priority: 🟡 MEDIUM - Needs Business Decision
### Effort: ⏱️ 1 hour (after decision made)
### Impact: 💰 Affects all business card pricing

### Current Situation

**Shopify Calculator**: Applies GST twice (21% total tax)
```python
# Lines 236-245
gst_rate = Decimal('1.1')

# First GST: $103.68 × 1.1 = $114.048
subtotal_after_first_gst = sub_total * gst_rate

# Second GST: $114.048 × 1.1 = $125.45
total_price = subtotal_after_first_gst * gst_rate
```

**WooCommerce Calculator**: Applies GST once (10% tax)
```python
total_price = sub_total * Decimal('1.1')
```

### Options

#### Option A: Fix Double GST (Recommended)
```python
# Change line 244 from:
total_price = subtotal_after_first_gst * gst_rate

# To:
total_price = subtotal_after_first_gst  # Already has GST applied
```

**Pros**:
- ✅ Correct tax calculation (10% GST)
- ✅ Matches WooCommerce pricing
- ✅ Lower customer prices (10% reduction)

**Cons**:
- ❌ Breaks exact Shopify parity
- ❌ May confuse if comparing to live Shopify site

**Impact**: Business cards price drops from $125.45 → $114.05 (9% reduction)

#### Option B: Keep Double GST
```python
# Keep current code (lines 236-245)
```

**Pros**:
- ✅ Maintains exact Shopify formula
- ✅ No code changes needed

**Cons**:
- ❌ Incorrect tax (21% instead of 10%)
- ❌ Higher customer prices
- ❌ May violate tax regulations

**Impact**: Customers continue to be overcharged

#### Option C: Configuration Flag
```python
def calculate(self, ..., use_shopify_double_gst: bool = False):
    """
    Args:
        use_shopify_double_gst: If True, apply GST twice (Shopify parity)
                                 If False, apply GST once (correct calculation)
    """
    gst_rate = Decimal('1.1')
    subtotal_after_first_gst = sub_total * gst_rate
    
    if use_shopify_double_gst:
        # Maintain Shopify parity (double GST)
        total_price = subtotal_after_first_gst * gst_rate
    else:
        # Correct single GST application
        total_price = subtotal_after_first_gst
    
    return total_price
```

**Pros**:
- ✅ Flexibility for testing
- ✅ Can be toggled per environment
- ✅ Maintains audit trail

**Cons**:
- ❌ More complex code
- ❌ Need to decide default value

**Impact**: Best of both worlds, but adds complexity

### Recommendation

**Implement Option A** (Fix Double GST) because:
1. Correct tax calculation is legally important
2. 10% price reduction improves competitiveness
3. Can document "we corrected the Shopify error"
4. Simpler than configuration flag

### Implementation (Option A)

**File**: `PremiumBusinessCards_Shopify_Calculator.py`

```python
# Lines 230-250 - BEFORE
gst_rate = Decimal('1.1')
subtotal_after_first_gst = sub_total * gst_rate
first_gst_amount = sub_total * (gst_rate - Decimal('1'))
total_price = subtotal_after_first_gst * gst_rate  # ❌ DOUBLE GST
second_gst_amount = subtotal_after_first_gst * (gst_rate - Decimal('1'))
total_gst_amount = first_gst_amount + second_gst_amount

# Lines 230-250 - AFTER
gst_rate = Decimal('1.1')

# ✅ FIX: Apply GST once (correct calculation)
total_price = sub_total * gst_rate
gst_amount = sub_total * (gst_rate - Decimal('1'))

# Round to nearest cent
total_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
```

### Update Breakdown Structure
```python
# Before
"breakdown": {
    "first_gst_application": 114.048,
    "first_gst_amount": 10.368,
    "second_gst_application": 125.45,  # ❌ REMOVE
    "second_gst_amount": 11.4048,      # ❌ REMOVE
    "total_gst_amount": 21.7728
}

# After
"breakdown": {
    "subtotal": 103.68,
    "gst_amount": 10.368,
    "total_price": 114.048
}
```

---

## 🧪 Integration Test Suite

### File: `test_calculator_fixes.py`

```python
"""
Integration tests for calculator fixes

Tests:
1. Celloglaze case-sensitivity fix
2. Parameter translation layer
3. GST calculation (depending on decision)
"""

import pytest
from calculator_wrapper import calculate_business_cards, calculate_flyers, calculate_booklets
from inhouse_wrapper import inhouse_calculate_quote

class TestCelloglazeFix:
    def test_uppercase_none(self):
        """Test celloglaze='None' (uppercase)"""
        result = calculate_business_cards(
            quantity=1000,
            stock_type="premium",
            print_type="double_sided",
            finish_size="90x55mm",
            celloglaze="None"
        )
        assert result["breakdown"]["cello_cost"] == 0
    
    def test_lowercase_none(self):
        """Test celloglaze='none' (lowercase) - THIS WAS BROKEN"""
        result = calculate_business_cards(
            quantity=1000,
            stock_type="premium",
            print_type="double_sided",
            finish_size="90x55mm",
            celloglaze="none"
        )
        assert result["breakdown"]["cello_cost"] == 0
        assert result["breakdown"]["has_celloglaze"] == 0
    
    def test_gloss_charges_correctly(self):
        """Test celloglaze='1 Side Gloss' still charges"""
        result = calculate_business_cards(
            quantity=1000,
            stock_type="premium",
            print_type="double_sided",
            finish_size="90x55mm",
            celloglaze="1 Side Gloss"
        )
        assert result["breakdown"]["cello_cost"] > 0


class TestParameterTranslation:
    def test_flyers_size_translation(self):
        """Test size='A5' translates to width=148, height=210"""
        result = inhouse_calculate_quote(
            product_type="flyers",
            parameters={
                "quantity": 5000,
                "size": "A5",
                "stock": "150gsm",
                "sides": 2
            }
        )
        assert result["success"] == True
        assert result["cost_inc_gst"] == 397.73
    
    def test_booklets_stock_translation(self):
        """Test stock='250gsm' translates to gsm=250"""
        result = inhouse_calculate_quote(
            product_type="booklets",
            parameters={
                "quantity": 500,
                "pages": 24,
                "size": "A5",
                "cover_stock": "250gsm",
                "internal_stock": "150gsm"
            }
        )
        assert result["success"] == True
        assert "total_price" in result
    
    def test_multiple_size_formats(self):
        """Test various size formats"""
        for size in ["A4", "A5", "A6", "DL"]:
            result = inhouse_calculate_quote(
                product_type="flyers",
                parameters={
                    "quantity": 1000,
                    "size": size,
                    "stock": "150gsm",
                    "sides": 1
                }
            )
            assert result["success"] == True


class TestGSTCalculation:
    def test_business_cards_gst_amount(self):
        """Test GST is 10% (not 21%)"""
        result = calculate_business_cards(
            quantity=1000,
            stock_type="premium",
            print_type="double_sided",
            finish_size="90x55mm",
            celloglaze="none"
        )
        
        subtotal = result["breakdown"]["subtotal"]
        gst_amount = result["breakdown"]["gst_amount"]
        
        # GST should be 10% of subtotal
        expected_gst = subtotal * 0.10
        assert abs(gst_amount - expected_gst) < 0.01
    
    def test_no_double_gst_application(self):
        """Test that GST is not applied twice"""
        result = calculate_business_cards(
            quantity=1000,
            stock_type="premium",
            print_type="double_sided",
            finish_size="90x55mm",
            celloglaze="none"
        )
        
        # Should NOT have second_gst_amount field
        assert "second_gst_amount" not in result["breakdown"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Review all code changes
- [ ] Run unit tests
- [ ] Run integration tests
- [ ] Update documentation
- [ ] Get business approval for GST decision

### Deployment Steps
1. [ ] Deploy to staging environment
2. [ ] Run smoke tests on staging
3. [ ] Verify:
   - [ ] Business cards pricing correct
   - [ ] Flyers work with size translation
   - [ ] Booklets work with stock translation
   - [ ] No regressions on other calculators
4. [ ] Deploy to production
5. [ ] Monitor error logs for 24 hours

### Post-Deployment
- [ ] Update AI tool descriptions
- [ ] Update calculator documentation
- [ ] Notify users of pricing changes (if GST fixed)
- [ ] Archive this document

---

## 🎯 Summary of Changes

| Fix | File | Lines | Change | Impact |
|-----|------|-------|--------|--------|
| Celloglaze Case | `PremiumBusinessCards_Shopify_Calculator.py` | 199 | Add `or celloglaze.lower() == "none"` | Prevents $8 overcharge |
| Parameter Translation | `parameter_translator.py` | NEW | Add translation module | Makes wrapper work for GOD |
| Wrapper Integration | `inhouse_wrapper.py` | 258-303 | Import and use translator | Enables high-level parameters |
| Double GST Fix | `PremiumBusinessCards_Shopify_Calculator.py` | 236-245 | Remove second GST application | 10% price reduction |

**Total Code Changes**: ~300 lines added, ~10 lines modified  
**Total Effort**: 4-6 hours  
**Business Impact**: Correct pricing, better user experience, no more wrapper failures
