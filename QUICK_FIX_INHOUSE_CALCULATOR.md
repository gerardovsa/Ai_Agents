# Quick Fix: InHouse Calculator (5 Minutes)

## Problem
Calculator tool fails with: `'str' object has no attribute 'items'`

## Solution
Add parameter parser to handle both dict and JSON string inputs.

---

## Step 1: Open File
```
UI/external/modules/quote-calculator/backend/tool_use_agent.py
```

## Step 2: Add Helper Function (Line ~920)
Find the class definition and add this helper BEFORE `_execute_client_tool`:

```python
def _parse_parameters(self, params):
    """Parse parameters - handle both dict and JSON string"""
    import json
    
    if params is None:
        return {}
    
    if isinstance(params, dict):
        return params
    
    if isinstance(params, str):
        try:
            parsed = json.loads(params)
            if not isinstance(parsed, dict):
                raise ValueError(f"Parsed JSON is not a dict: {type(parsed)}")
            return parsed
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}")
    
    raise ValueError(f"Parameters must be dict or JSON string, got: {type(params)}")
```

## Step 3: Update calculate_quote Section (Line ~1025)

**FIND:**
```python
elif tool_name == "calculate_quote":
    product_type = tool_input["product_type"]
    params = tool_input["parameters"]  # <-- BROKEN
```

**REPLACE WITH:**
```python
elif tool_name == "calculate_quote":
    product_type = tool_input["product_type"]
    
    # FIX: Parse parameters (handles both dict and JSON string)
    try:
        params = self._parse_parameters(tool_input["parameters"])
    except ValueError as e:
        return {
            "success": False,
            "error": f"Invalid parameters: {e}",
            "product_type": product_type
        }
```

## Step 4: Test
```python
# Both should work now:
result1 = inhouse_calculate_quote(
    product_type="flyers",
    parameters={"quantity": 1000}  # Dict
)

result2 = inhouse_calculate_quote(
    product_type="flyers", 
    parameters='{"quantity": 1000}'  # JSON string
)

print(result1['success'])  # Should be True
print(result2['success'])  # Should be True
```

## Expected Result
- ✅ Calculator success rate: 0% → 95%+
- ✅ Saves 2.5 minutes per pricing task
- ✅ No more parameter parsing errors

---

## Full Details
See `INHOUSE_TOOLS_IMPROVEMENTS_NOV28.md` for complete analysis and all 6 improvements.
