# GOD Calculator Deprecation for Business Cards - January 28, 2026

## 🚨 CRITICAL PRODUCTION BUG FIX

**Issue Discovered:** Production AI agent on Render v11 deployment used GOD calculator (`calculate_business_cards`) instead of specialized Shopify calculators for Premium Business Cards, resulting in **30-56% under-quoted prices**.

**Financial Impact:**
- Quote 1: AI quoted $59.71 vs expected $85.80 = **$26.09 under-quoted (30% error)**
- Quote 2: AI quoted $70.42 vs expected $161.70 = **$91.28 under-quoted (56% error)**

## Root Cause Analysis

### **Production Conversation Trace Evidence**

**Round 3:** AI called wrong calculator
```
Tool Call: get_tool_schema('calculate_business_cards')  ❌ GOD calculator
```

**Round 5:** Calculator guide showed GOD calculator as valid for business cards
```json
{
  "god_calculator": {
    "products": ["flyers", "business_cards"],  ❌ WRONG
    "description": "Flexible parameter system, handles 90x55mm business cards"
  }
}
```

**Round 8:** Wrong calculator executed with wrong parameters
```
Tool Call: calculate_business_cards(
  quantity=500, 
  stock_type="satin",  ❌ Should be paper_stock="Satin 350GSM"
  print_type="double_sided"  ❌ Should be print_sides="Double side print"
)
Result: $59.71  ❌ Expected: $85.80 (30% under-quote)
```

**Round 12:** Second quote with even worse error
```
Tool Call: calculate_business_cards(
  quantity=1000,
  stock_type="uncoated",  ❌ Should be paper_stock="EcoStar 350GSM Uncoated"
  print_type="double_sided"
)
Result: $70.42  ❌ Expected: $161.70 (56% under-quote)
```

### **Why GOD Calculator Produces Wrong Prices**

**Parameter Mismatch:**
```python
# GOD Calculator Schema (calculator_tools.json line 6)
{
  "name": "calculate_business_cards",
  "parameters": {
    "stock_type": {
      "enum": ["standard", "premium", "satin", "uncoated"]  ❌ Generic types
    },
    "print_type": {
      "enum": ["single_sided", "double_sided"]  ❌ Generic types
    }
  }
}

# Premium Business Cards Schema (calculator_tools.json line 390)
{
  "name": "calculate_premium_business_cards_shopify",
  "parameters": {
    "paper_stock": {
      "enum": ["Satin 350GSM", "King Kong High Bulk", "EcoStar 350GSM Uncoated"]  ✅ Specific types
    },
    "print_sides": {
      "enum": ["Single side print", "Double side print"]  ✅ Correct format
    }
  }
}
```

**Pricing Impact:**
- GOD calculator uses generic stock types with basic pricing
- Premium calculator uses specific Shopify DPO pricing formulas
- Result: 30-56% price difference due to wrong cost calculations

## Fixes Applied

### **1. Updated Calculator Guide (inhouse_guide_wrapper.py line 180)**

**Before:**
```python
"god_calculator": {
    "products": ["flyers", "business_cards"],  ❌
    "description": "Flexible parameter system, handles 90x55mm business cards"
}
```

**After:**
```python
"god_calculator": {
    "products": ["flyers"],  ✅ Removed business_cards
    "description": "Flexible parameter system for flyer products only. WARNING: DO NOT use for business cards - use specialized calculators instead (calculate_premium_business_cards_shopify or calculate_economical_business_cards_shopify)"
}
```

### **2. Deprecated GOD Calculator Schema (calculator_tools.json line 6)**

**Before:**
```json
{
  "name": "calculate_business_cards",
  "short_description": "Calculate business card printing quotes",
  "description": "Calculate quote for business cards. Returns total price, per-card cost, stock details, and turnaround time."
}
```

**After:**
```json
{
  "name": "calculate_business_cards",
  "short_description": "DEPRECATED for business cards - Use calculate_premium_business_cards_shopify or calculate_economical_business_cards_shopify instead",
  "description": "DEPRECATED: This GOD calculator should NOT be used for business card quotes - it produces incorrect pricing (30-56% under-quoted). For business cards, ALWAYS use the specialized Shopify calculators: calculate_premium_business_cards_shopify (Satin 350GSM, King Kong, EcoStar) or calculate_economical_business_cards_shopify (Standard 350GSM). This calculator is only valid for flyer products."
}
```

### **3. Added Validation Rejection (calculator_wrapper.py line 112)**

**Added deprecation check at function start:**
```python
def calculate_business_cards(...):
    """
    DEPRECATED: This GOD calculator should NOT be used for business card quotes.
    
    ⚠️ WARNING: This calculator produces incorrect pricing (30-56% under-quoted).
    
    For business cards, ALWAYS use the specialized Shopify calculators:
    - calculate_premium_business_cards_shopify
    - calculate_economical_business_cards_shopify
    """
    try:
        # CRITICAL VALIDATION: Reject business card requests
        if finish_size in ["90x55mm", "90x50mm", "85x55mm"]:
            return {
                "success": False,
                "error": "DEPRECATED: calculate_business_cards() should NOT be used for business card quotes. "
                        "This calculator produces incorrect pricing (30-56% under-quoted). "
                        "Use calculate_premium_business_cards_shopify or calculate_economical_business_cards_shopify instead.",
                "error_type": "deprecated_calculator",
                "recommended_tools": [
                    "calculate_premium_business_cards_shopify",
                    "calculate_economical_business_cards_shopify"
                ]
            }
```

## Expected AI Behavior After Fix

### **Before Fix (Production Error):**
```
User: "Quote 500 premium business cards, satin 350GSM"

AI Round 1: Call inhouse_get_domain_guide() → "calculator" domain
AI Round 2: Call inhouse_calculator_guide() → Sees "business_cards" in GOD calculator
AI Round 3: Call get_tool_schema('calculate_business_cards') → Gets GOD schema
AI Round 4: Call calculate_business_cards(quantity=500, stock_type="satin") → Wrong price $59.71
```

### **After Fix (Correct Behavior):**
```
User: "Quote 500 premium business cards, satin 350GSM"

AI Round 1: Call inhouse_get_domain_guide() → "calculator" domain
AI Round 2: Call inhouse_calculator_guide() → Sees business_cards ONLY in specialized calculators
AI Round 3: Call get_tool_schema('calculate_premium_business_cards_shopify') → Gets correct schema
AI Round 4: Call calculate_premium_business_cards_shopify(quantity=500, paper_stock="Satin 350GSM") → Correct price $85.80
```

**OR if AI somehow calls GOD calculator:**
```
AI Round 4: Call calculate_business_cards(quantity=500, stock_type="satin", finish_size="90x55mm")
Response: {
  "success": False,
  "error": "DEPRECATED: This calculator produces incorrect pricing. Use calculate_premium_business_cards_shopify instead.",
  "recommended_tools": ["calculate_premium_business_cards_shopify", ...]
}
AI Round 5: Call calculate_premium_business_cards_shopify() → Correct price
```

## Files Modified

1. **inhouse_guide_wrapper.py**
   - Line 180: Removed "business_cards" from GOD calculator products list
   - Added explicit warning in description

2. **calculator_tools.json**
   - Line 6-8: Updated short_description and description with deprecation warning
   - Made clear this calculator should NOT be used for business cards

3. **calculator_wrapper.py**
   - Line 112-145: Added validation check to reject business card requests
   - Returns error with recommended specialized calculators
   - Updated docstring with deprecation warning

## Testing Validation

### **Test 1: Verify GOD Calculator Rejection**
```python
from calculator_wrapper import calculate_business_cards

result = calculate_business_cards(
    quantity=500,
    stock_type="satin",
    print_type="double_sided",
    finish_size="90x55mm"
)

assert result["success"] == False
assert "DEPRECATED" in result["error"]
assert "calculate_premium_business_cards_shopify" in result["recommended_tools"]
```

### **Test 2: Verify Calculator Guide Update**
```python
from inhouse_guide_wrapper import inhouse_calculator_guide

guide = inhouse_calculator_guide()
god_calc = guide["calculator_index"]["god_calculator"]

assert "business_cards" not in god_calc["products"]
assert "flyers" in god_calc["products"]
assert "DO NOT use for business cards" in god_calc["description"]
```

### **Test 3: Verify Schema Deprecation**
```python
# Check calculator_tools.json schema
import json

with open("calculator_tools.json") as f:
    schema = json.load(f)
    
god_calc = schema["tools"][0]  # First tool is calculate_business_cards
assert god_calc["name"] == "calculate_business_cards"
assert "DEPRECATED" in god_calc["description"]
assert "30-56% under-quoted" in god_calc["description"]
```

## Deployment Checklist

- [x] Fixed inhouse_guide_wrapper.py (removed business_cards from GOD calculator)
- [x] Fixed calculator_tools.json (added deprecation warning)
- [x] Fixed calculator_wrapper.py (added validation rejection)
- [ ] Commit changes with urgent bug fix message
- [ ] Push to gerardo (production deployment)
- [ ] Monitor Render deployment logs
- [ ] Test in production with same test case from trace
- [ ] Verify AI now uses correct specialized calculators

## Related Documentation

- **BUSINESS_CARDS_ALIGNMENT_COMPLETE_JAN28_2026.md** - Original three-layer alignment fixes
- **AI_TEST_CONFIGURATIONS.md** - Test cases showing correct pricing
- **PRODUCTION_TRACE_ANALYSIS_JAN28_2026.md** - Detailed trace analysis of production failure

## Key Lessons

1. **Calculator Guide is Critical:** AI agents use `inhouse_calculator_guide()` to decide which calculator to use
2. **Schema Descriptions Matter:** Short descriptions appear in tool lists - must be clear about deprecation
3. **Defense in Depth:** Multiple layers of protection (guide + schema + validation) prevent routing errors
4. **Production Monitoring:** Always verify AI behavior in production matches expected workflows
5. **Three-Layer Validation:** Schema, wrapper, and Python must all align - but also guide must route correctly

## Success Metrics

**Before Fix:**
- ❌ Production AI quoted $59.71 instead of $85.80 (30% under-quote)
- ❌ Production AI quoted $70.42 instead of $161.70 (56% under-quote)
- ❌ GOD calculator listed as valid for business cards

**After Fix:**
- ✅ GOD calculator removed from business cards routing
- ✅ Explicit deprecation warnings in schema and guide
- ✅ Validation rejection with recommended alternatives
- ✅ AI forced to use correct specialized calculators

---

**Status:** Fixes complete, ready for commit and deployment
**Priority:** URGENT - Production pricing error affecting customer quotes
**Impact:** Prevents 30-56% under-quoted prices for all business card quotes
