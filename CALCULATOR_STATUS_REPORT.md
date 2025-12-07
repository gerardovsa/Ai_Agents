# Calculator Status Report - December 8, 2025

## Executive Summary

Analysis of all calculator implementations in the InHouse Print system to identify parameter parsing bugs similar to the one found in `inhouse_calculate_quote`.

---

## Calculators Identified

### 1. **InHouse Wrapper Calculators** (`UI/modules_external/inhouse-print/`)

**File**: `implementations/inhouse_wrapper.py`

✅ **FIXED**: `inhouse_calculate_quote()`
- **Status**: Parameter parsing bug FIXED (Dec 8, 2025)
- **Fix Applied**: JSON deserialization added in `tool_use_agent.py:1023`
- **Test Result**: JSON string parameters now work correctly
- **Location**: Calls `agent._execute_client_tool('calculate_quote', {...})`

---

### 2. **Quote Calculator Wrappers** (`UI/modules_external/quote-calculator/`)

**File**: `implementations/calculator_wrapper.py`

#### Direct Calculator Functions (16 total):

1. **`calculate_business_cards()`**
   - **Type**: Direct wrapper
   - **Backend**: `ComprehensiveQuoteCalculator`
   - **Risk**: ⚠️ MEDIUM - May have same bug if parameters passed as JSON string
   - **Status**: NOT TESTED

2. **`calculate_flyers()`**
   - **Type**: Direct wrapper
   - **Backend**: `ComprehensiveQuoteCalculator`
   - **Risk**: ⚠️ MEDIUM
   - **Status**: NOT TESTED

3. **`calculate_booklets()`**
   - **Type**: Direct wrapper
   - **Backend**: `ComprehensiveQuoteCalculator`
   - **Risk**: ⚠️ MEDIUM
   - **Status**: NOT TESTED

4. **`calculate_perfect_bound_books()`**
   - **Type**: Direct wrapper
   - **Backend**: `ComprehensiveQuoteCalculator`
   - **Risk**: ⚠️ MEDIUM
   - **Status**: NOT TESTED

5. **`calculate_letterheads()`**
   - **Type**: Direct wrapper
   - **Backend**: `ComprehensiveQuoteCalculator`
   - **Risk**: ⚠️ MEDIUM
   - **Status**: NOT TESTED

6. **`calculate_corflute_signs()`**
   - **Type**: Direct wrapper
   - **Backend**: `ComprehensiveQuoteCalculator`
   - **Risk**: ⚠️ MEDIUM
   - **Status**: NOT TESTED

#### GOD Calculator Functions (4 total):

7. **`calculate_flyers_god()`**
   - **Type**: GOD calculator
   - **Backend**: `FlyerCalculatorGOD`
   - **Risk**: ⚠️ MEDIUM
   - **Status**: NOT TESTED

8. **`calculate_letterheads_god()`**
   - **Type**: GOD calculator
   - **Backend**: `LetterheadCalculatorGOD`
   - **Risk**: ⚠️ MEDIUM
   - **Status**: NOT TESTED

9. **`calculate_perfect_bound_books_god()`**
   - **Type**: GOD calculator
   - **Backend**: `PerfectBoundBooksCalculator`
   - **Risk**: ⚠️ MEDIUM
   - **Status**: NOT TESTED

10. **`calculate_corflute_signs_god()`**
    - **Type**: GOD calculator
    - **Backend**: `CorflutePricingCalculator`
    - **Risk**: ⚠️ MEDIUM
    - **Status**: NOT TESTED

#### Shopify Calculator Functions (6 total):

11. **`calculate_economical_business_cards_shopify()`**
    - **Type**: Shopify calculator
    - **Backend**: `EconomicalBusinessCardsShopifyCalculator`
    - **Risk**: ⚠️ MEDIUM
    - **Status**: NOT TESTED

12. **`calculate_premium_business_cards_shopify()`**
    - **Type**: Shopify calculator
    - **Backend**: `PremiumBusinessCardsShopifyCalculator`
    - **Risk**: ⚠️ MEDIUM
    - **Status**: NOT TESTED

13. **`calculate_folded_flyers_shopify()`**
    - **Type**: Shopify calculator
    - **Backend**: `FoldedFlyersShopifyCalculator`
    - **Risk**: ⚠️ MEDIUM
    - **Status**: NOT TESTED

14. **`calculate_wire_bound_books_shopify()`**
    - **Type**: Shopify calculator
    - **Backend**: `WireBoundShopifyCalculator`
    - **Risk**: ⚠️ MEDIUM
    - **Status**: NOT TESTED

15. **`calculate_spiral_bound_books_shopify()`**
    - **Type**: Shopify calculator
    - **Backend**: `SpiralBoundShopifyCalculator`
    - **Risk**: ⚠️ MEDIUM
    - **Status**: NOT TESTED

16. **`get_stock_list()`**
    - **Type**: Utility function
    - **Backend**: `ComprehensiveQuoteCalculator`
    - **Risk**: ✅ LOW - No parameter parsing
    - **Status**: NOT APPLICABLE

---

## Bug Analysis

### Where the Bug Was Found

**File**: `UI/modules_external/quote-calculator/backend/tool_use_agent.py`  
**Line**: 1068  
**Function**: `_execute_client_tool()` when `tool_name == "calculate_quote"`

### The Bug Pattern

```python
# BEFORE FIX (BROKEN):
params = tool_input["parameters"]  # Receives JSON string: '{"quantity": 100, ...}'

filtered_params = {
    k: v for k, v in params.items()  # ❌ CRASH: 'str' object has no attribute 'items'
    if k in supported_params[product_type]
}

# AFTER FIX (WORKING):
params = tool_input["parameters"]

# Add JSON deserialization
if isinstance(params, str):
    params = json.loads(params)  # ✅ Convert string to dict

filtered_params = {
    k: v for k, v in params.items()  # ✅ Now works!
    if k in supported_params[product_type]
}
```

### Risk Assessment

**HIGH RISK** calculators (same backend as fixed one):
- ❌ None - The fixed calculator routes through `tool_use_agent._execute_client_tool()`

**MEDIUM RISK** calculators (different entry points):
- ⚠️ All 16 calculator wrapper functions in `calculator_wrapper.py`
- These call the backend calculators directly, bypassing `tool_use_agent`
- Unknown if they handle JSON string parameters

**LOW RISK** calculators:
- ✅ `get_stock_list()` - No complex parameter parsing

---

## Testing Required

### Test Scenarios

For each calculator, test with:

1. **Dict parameters** (expected format):
   ```python
   registry.execute_tool("calculate_business_cards", 
       quantity=500,
       stock_type="satin_350gsm",
       sides=2
   )
   ```

2. **JSON string parameters** (bug scenario):
   ```python
   registry.execute_tool("calculate_business_cards",
       parameters='{"quantity": 500, "stock_type": "satin_350gsm", "sides": 2}'
   )
   ```

3. **Invalid JSON** (error handling):
   ```python
   registry.execute_tool("calculate_business_cards",
       parameters='{invalid json'
   )
   ```

### Expected Outcomes

✅ **PASS**: Calculator handles both dict and JSON string parameters  
⚠️ **WARN**: Calculator works with dict but fails with JSON string (needs fix)  
❌ **FAIL**: Calculator fails with both formats (different issue)  

---

## Recommendations

### Immediate Actions (Priority 1 - CRITICAL)

1. **Test Business Cards Calculator**
   - Most commonly used
   - Test with JSON string parameters
   - Apply fix if needed

2. **Test All Wrapper Functions**
   - Run test suite on all 16 calculator functions
   - Identify which have the bug
   - Document findings

### Short Term Actions (Priority 2 - HIGH)

1. **Apply Universal Fix**
   - Add parameter deserialization to ALL calculator wrappers
   - Use defensive programming approach
   - Handle both dict and JSON string inputs

2. **Add Parameter Validation**
   - Type checking for all parameters
   - Clear error messages
   - Graceful failure handling

### Long Term Actions (Priority 3 - MEDIUM)

1. **Centralized Parameter Handling**
   - Create `_parse_parameters()` utility function
   - Use across all calculators
   - Single point of maintenance

2. **Comprehensive Test Suite**
   - Automated tests for all calculators
   - Test both parameter formats
   - Prevent future regressions

3. **Schema Validation**
   - JSON Schema validation for parameters
   - Pre-validate before calling calculators
   - Better error messages

---

## Implementation Strategy

### Step 1: Create Universal Parameter Parser

```python
# File: UI/modules_external/quote-calculator/implementations/parameter_utils.py

import json
from typing import Dict, Any, Union

def parse_calculator_parameters(
    parameters: Union[str, Dict[str, Any]],
    calculator_name: str
) -> Dict[str, Any]:
    """
    Universal parameter parser for all calculators
    
    Handles both dict and JSON string parameters
    with comprehensive error handling.
    
    Args:
        parameters: Dict object or JSON string
        calculator_name: Name for error messages
        
    Returns:
        Dict of parameters
        
    Raises:
        ValueError: If invalid JSON or wrong type
    """
    # Handle JSON string
    if isinstance(parameters, str):
        try:
            parameters = json.loads(parameters)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"{calculator_name}: Invalid JSON in parameters: {str(e)}"
            )
    
    # Validate it's now a dict
    if not isinstance(parameters, dict):
        raise ValueError(
            f"{calculator_name}: Parameters must be dict or JSON string, "
            f"got {type(parameters).__name__}"
        )
    
    return parameters
```

### Step 2: Apply to All Calculators

```python
# File: UI/modules_external/quote-calculator/implementations/calculator_wrapper.py

from .parameter_utils import parse_calculator_parameters

def calculate_business_cards(
    quantity: int,
    stock_type: str,
    sides: int,
    **kwargs
) -> Dict[str, Any]:
    """Calculate business card quote"""
    
    # If parameters passed as single dict/JSON string
    if 'parameters' in kwargs:
        try:
            params = parse_calculator_parameters(
                kwargs['parameters'],
                'calculate_business_cards'
            )
            # Extract individual parameters
            quantity = params.get('quantity', quantity)
            stock_type = params.get('stock_type', stock_type)
            sides = params.get('sides', sides)
        except ValueError as e:
            return {"success": False, "error": str(e)}
    
    # Continue with existing logic...
```

### Step 3: Test All Calculators

Run comprehensive test suite to verify:
- ✅ Dict parameters work
- ✅ JSON string parameters work
- ✅ Invalid JSON fails gracefully
- ✅ Missing parameters caught
- ✅ Error messages are clear

---

## Success Criteria

### Phase 1: Verification (Week 1)
- [ ] Test all 16 calculator wrappers
- [ ] Document which have the bug
- [ ] Prioritize fixes

### Phase 2: Implementation (Week 2)
- [ ] Create universal parameter parser
- [ ] Apply fix to all affected calculators
- [ ] Run comprehensive test suite
- [ ] Verify 100% success rate

### Phase 3: Deployment (Week 3)
- [ ] Deploy fixes to production
- [ ] Monitor error rates
- [ ] Validate with real user requests
- [ ] Document lessons learned

---

## Conclusion

The parameter parsing bug in `inhouse_calculate_quote` has been successfully fixed. However, there are 16 additional calculator functions that may have the same vulnerability.

**Next Steps**:
1. Run comprehensive test suite (when Unicode issues resolved)
2. Apply universal fix to all affected calculators
3. Deploy with confidence

**Risk Level**: ⚠️ MEDIUM  
**Impact**: Medium (calculators may fail with certain parameter formats)  
**Effort**: Low (fix is known and tested)  
**Timeline**: 1-2 weeks for complete implementation

---

**Document Version**: 1.0  
**Last Updated**: December 8, 2025  
**Author**: Platform Tool Suite Construction Agent  
**Status**: Investigation Complete - Testing Pending
