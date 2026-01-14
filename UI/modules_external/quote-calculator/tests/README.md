# Quote Calculator Tests

## Overview

This folder contains comprehensive tests for all 35+ quote calculators. Tests use **Registry V3** - the exact same interface that AI agents use.

---

## Running Tests

### Run All Calculator Tests

```bash
# From AI_agents root directory
python UI/modules_external/quote-calculator/tests/test_all_calculators.py
```

**Expected Output:**
```
============================================================
CALCULATOR TEST SUITE - Registry V3 Integration
============================================================

Testing: calculate_business_cards
✅ PASSED - $125.45

Testing: calculate_flyers
✅ PASSED - $109.46

...

============================================================
TEST SUMMARY
============================================================
✅ Passed: 35/35
❌ Failed: 0/35
Success Rate: 100.0%
============================================================
```

---

## Test Structure

### What It Tests

Each test validates:
- ✅ Calculator executes successfully through Registry V3
- ✅ Returns expected data structure
- ✅ Price calculation is within expected range
- ✅ All required fields are present

### Test Categories

1. **Core Calculators (6)**
   - business_cards, flyers, booklets, perfect_bound_books, letterheads, corflute_signs

2. **Shopify Calculators (5)**
   - economical_business_cards_shopify, premium_business_cards_shopify, folded_flyers_shopify
   - wire_bound_books_shopify, spiral_bound_books_shopify

3. **GOD Variant Calculators (4)**
   - flyers_god, letterheads_god, perfect_bound_books_god, corflute_signs_god

4. **Specialized Shopify Calculators (20)**
   - saddle_stitch_books, bollard_signs, construction_signs, election_signs, selfie_frames
   - stackable_cubes, strut_cards_a3, strut_cards_a4, custom_poster_printing, custom_vinyl_stickers
   - premium_bookmarks, printed_letterheads, with_compliments_slips, notepads_a4/a5/a6
   - luxury_classic_pull_up_banners, metal_face_a_frame, corflute_insert_a_frame, spiral_bound_books

---

## Using Calculators in Your Code

### Python - Registry V3 (Recommended for AI Agents)

```python
from tools.registry_v3 import RegistryV3

# Initialize registry
registry = RegistryV3()

# Execute calculator (exact AI usage pattern)
result = registry.execute_tool(
    tool_name='calculate_business_cards',
    quantity=1000,
    stock_type='premium',
    sides=2
)

# Check result
if result.get('success'):
    print(f"Total Price: ${result['total_price']:.2f}")
    print(f"Unit Price: ${result['unit_price']:.2f}")
    print(f"Breakdown: {result['breakdown']}")
else:
    print(f"Error: {result.get('error')}")
```

### HTTP API - Flask Endpoint

```bash
# Start Flask server first
python AI_infrastructure/flask_app.py
```

```javascript
// Test calculator via API
fetch('http://localhost:5001/api/calculator/test', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        tool_name: 'calculate_business_cards',
        params: {
            quantity: 1000,
            stock_type: 'premium',
            sides: 2
        }
    })
})
.then(r => r.json())
.then(data => {
    console.log('Result:', data.result);
    console.log('Execution Time:', data.execution_time_ms + 'ms');
});
```

### List All Calculators

```javascript
// Get list of all available calculators
fetch('http://localhost:5001/api/calculator/list')
    .then(r => r.json())
    .then(data => {
        console.log(`Found ${data.total} calculators`);
        data.calculators.forEach(calc => {
            console.log(`- ${calc.name}: ${calc.short_description}`);
        });
    });
```

---

## Testing Dashboard (HTML)

Open in browser: `file:///C:/Users/gpoli/GIT/AI_agents/calculator_test_dashboard.html`

**Requirements:**
1. Flask server must be running: `python AI_infrastructure/flask_app.py`
2. Dashboard will call API at `http://localhost:5001/api/calculator/test`
3. Tests execute using exact Registry V3 pattern

---

## Adding New Calculator Tests

To add a new calculator to the test suite:

```python
# In test_all_calculators.py, add to the tests list:

{
    'tool_name': 'calculate_my_new_product',
    'params': {
        'quantity': 100,
        'size': 'A4',
        'finish': 'Gloss'
        # ... all required params
    },
    'expected_min': 150  # Minimum expected price
}
```

---

## Troubleshooting

### ImportError: No module named 'tools.registry_v3'

**Solution:** Run from AI_agents root directory:
```bash
cd C:\Users\gpoli\GIT\AI_agents
python UI/modules_external/quote-calculator/tests/test_all_calculators.py
```

### Calculator Test Fails

1. Check parameter names match schema: `UI/modules_external/quote-calculator/schema/calculator_tools.json`
2. Verify backend calculator exists: `UI/modules_external/quote-calculator/backend/`
3. Check wrapper function: `UI/modules_external/quote-calculator/implementations/calculator_wrapper.py`

### API Returns 500 Error

1. Ensure Flask server is running
2. Check server logs for errors
3. Verify calculator name is correct (use `/api/calculator/list`)

---

## Files in This Directory

- **test_all_calculators.py** - Main test suite (35 tests)
- **README.md** - This file (usage guide)

---

## Success Metrics

**Current Status: 35/35 Working (100%)**

All calculators tested and working through Registry V3 interface, ready for AI agent usage.

**Last Updated:** December 11, 2025
