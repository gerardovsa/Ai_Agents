# Calculator Wrapper **kwargs Fix - January 28, 2026

## Problem

Registry V3 injects internal parameters (`_user_id`, `_injected_credentials`, `_session_id`, etc.) into every tool call, but calculator wrapper functions don't have `**kwargs` to absorb them, causing:

```
TypeError: got an unexpected keyword argument '_user_id'
```

## Root Cause

**registry_v3.py line 720:**
```python
result = func(**kwargs)  # Passes ALL kwargs including internal parameters
```

**calculator_wrapper.py functions:**
```python
def calculate_premium_business_cards_shopify(
    quantity: int,
    print_type: str = None,
    # ... other params
):  # ❌ NO **kwargs - rejects _user_id
```

## Solution

Add `**kwargs` to ALL calculator wrapper functions to absorb internal parameters:

```python
def calculate_premium_business_cards_shopify(
    quantity: int,
    print_type: str = None,
    # ... other params
    **kwargs  # ✅ Absorbs _user_id, _injected_credentials, etc.
):
    # No need to explicitly remove them - just don't use them
    # They're automatically excluded when calling the calculator backend
```

## Files to Fix

**calculator_wrapper.py** - Add `**kwargs` to these functions:

###Shopify Calculators (Need **kwargs):
1. `calculate_economical_business_cards_shopify` (line 1117)
2. `calculate_premium_business_cards_shopify` (line 1225)
3. `calculate_folded_flyers_shopify` (line 1352) - Already has deprecated params, needs `**kwargs`
4. `calculate_printed_flyers_shopify` (line 1665)
5. `calculate_wire_bound_books_shopify` (line 1729)
6. `calculate_spiral_bound_books_shopify` (line 2033)
7. `calculate_perfect_bound_books_shopify` (line 2330)
8. `calculate_saddle_stitch_books_shopify` (line 2597)
9. `calculate_spiral_books_simple_shopify` (line 2863)
10. `calculate_corflute_signs_shopify` (line 949)

### Other Calculators (Need **kwargs):
11. `calculate_business_cards` (line 112) - GOD calculator
12. `calculate_flyers` (line 223) - GOD calculator
13. `calculate_booklets` (line 325)
14. `calculate_perfect_bound_books` (line 412)
15. `calculate_letterheads` (line 508)
16. `calculate_flyers_god` (line 667)
17. `calculate_letterheads_god` (line 779)
18. `calculate_perfect_bound_books_god` (line 851)
19. `calculate_saddle_stitch_books` (line 2963)
20. `calculate_bollard_signs` (line 3040)
21. `calculate_construction_signs` (line 3136)
22. `calculate_election_signs` (line 3263)
23. `calculate_corflute_insert_a_frame` (line 3389)
24. `calculate_metal_face_a_frame` (line 3455 & 3674)
25. `calculate_luxury_classic_pull_up_banners` (line 3522)
26. `calculate_premium_pull_up_banners` (line 3598)
27. `calculate_selfie_frames` (line 3734)
28. `calculate_stackable_cubes` (line 3801)
29. `calculate_strut_cards_a3` (line 3882)
30. `calculate_strut_cards_a4` (line 3942)
31. `calculate_strut_cards_a5` (line 4002)
32. `calculate_counter_strut_cards_a3` (line 4061)
33. `calculate_counter_strut_cards_a4` (line 4107)
34. `calculate_counter_strut_cards_a5` (line 4153)
35. `calculate_custom_poster_printing` (line 4200)
36. `calculate_custom_vinyl_stickers` (line 4319)
37. `calculate_premium_bookmarks` (line 4502)
38. `calculate_printed_letterheads` (line 4637)
39. `calculate_with_compliments_slips` (line 4742)
40. `calculate_notepads_a4` (line 4857)
41. `calculate_notepads_a5` (line 4954)
42. `calculate_notepads_a6` (line 5066)

### Already Has **kwargs ✅:
43. `calculate_spiral_bound_books` (line 5177) - Already correct!

## Fix Pattern

**Before:**
```python
def calculate_premium_business_cards_shopify(
    quantity: int,
    print_type: str = None,
    paper_stock: str = None,
    print_sides: str = None,
    finish_size: str = None,
    celloglaze: str = None,
    artworks: int = None
) -> Dict[str, Any]:
```

**After:**
```python
def calculate_premium_business_cards_shopify(
    quantity: int,
    print_type: str = None,
    paper_stock: str = None,
    print_sides: str = None,
    finish_size: str = None,
    celloglaze: str = None,
    artworks: int = None,
    **kwargs  # ← Add this to absorb internal parameters
) -> Dict[str, Any]:
```

## Why This Works

1. **Registry injects parameters:** `_user_id`, `_injected_credentials`, `_session_id`, `_thread_id`, `_user_request`, `_workflow_context`
2. **`**kwargs` absorbs them:** Function accepts all parameters without error
3. **Calculator doesn't see them:** When wrapper calls calculator backend, only explicit parameters are passed
4. **No code changes needed:** Just add `**kwargs` to function signature

## Testing

After fix, all calculators should work:

```python
# This should succeed (was failing before)
registry.execute_tool(
    tool_name="calculate_premium_business_cards_shopify",
    quantity=1000,
    paper_stock="King Kong High Bulk",
    print_sides="Double side print",
    print_type="Colour",
    celloglaze="2 Side Gloss",
    artworks=1,
    _user_id=1,  # ← No longer causes error
    _session_id="abc123"
)
```

## Impact

- **42 calculator functions need fixing**
- **1 already correct** (calculate_spiral_bound_books)
- **Zero breaking changes** - only adds parameter acceptance
- **Fixes ALL "unexpected keyword argument '_user_id'" errors**

## Priority

**URGENT** - This blocks ALL calculator usage in production when called through the AI agent system.

---

**Status:** Analysis complete, ready to implement fixes
**Date:** January 28, 2026
