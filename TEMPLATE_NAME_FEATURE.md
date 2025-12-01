# Template Name Feature - Enhanced Quote Creation

**Date:** December 1, 2025  
**Status:** ✅ COMPLETE

---

## Enhancement Summary

Added `template_name` parameter to `xero_create_quote` for easier template assignment. Now you can use template names instead of requiring the BrandingThemeID GUID.

---

## Before (Required GUID)

```python
# Had to look up the GUID first
themes = xero_get_branding_themes(business_id=1)
branding_theme_id = themes['branding_themes'][0]['branding_theme_id']

# Then create quote with GUID
xero_create_quote(
    business_id=1,
    contact_id="...",
    line_items=[...],
    branding_theme_id="d5b89e36-8a28-4c40-b8e4-2a0d3f5d7c93"  # Hard to remember!
)
```

---

## After (Use Template Name) ✨

```python
# Just use the template name!
xero_create_quote(
    business_id=1,
    contact_id="...",
    line_items=[...],
    template_name="Standard Invoice"  # Easy!
)
```

---

## How It Works

1. **Automatic Lookup:** Function queries `GET /BrandingThemes` API
2. **Exact Match:** Searches for exact template name (case-insensitive)
3. **Partial Match:** Falls back to partial name match if no exact match
4. **Graceful Fallback:** If lookup fails, continues without template

### Matching Logic

```python
# Exact match (case-insensitive)
template_name="Standard Invoice" → Matches "Standard Invoice", "standard invoice", "STANDARD INVOICE"

# Partial match
template_name="Standard" → Matches "Standard Invoice", "Standard Quote", etc.
```

---

## Usage Examples

### Example 1: Using Template Name
```python
xero_create_quote(
    business_id=1,
    contact_id="a3675fc4-f8dd-4f03-ba5b-f1870566bcd7",
    line_items=[
        {
            "description": "Business Cards - 1000qty, 350GSM",
            "quantity": 1,
            "unit_amount": 150.00
        }
    ],
    template_name="Standard Invoice",  # ← Easy to use!
    title="Printing Quote"
)
```

### Example 2: Using BrandingThemeID (Still Works)
```python
xero_create_quote(
    business_id=1,
    contact_id="a3675fc4-f8dd-4f03-ba5b-f1870566bcd7",
    line_items=[...],
    branding_theme_id="d5b89e36-8a28-4c40-b8e4-2a0d3f5d7c93"  # ← Direct GUID
)
```

### Example 3: No Template (Uses Default)
```python
xero_create_quote(
    business_id=1,
    contact_id="a3675fc4-f8dd-4f03-ba5b-f1870566bcd7",
    line_items=[...]
    # No template_name or branding_theme_id → Uses Xero default
)
```

---

## Parameter Details

### New Parameter: `template_name`
- **Type:** `string`
- **Optional:** Yes
- **Description:** Template name (e.g., "Default Theme", "Standard Invoice")
- **Behavior:** Automatically looks up the BrandingThemeID by name
- **Priority:** If both `template_name` and `branding_theme_id` provided, `branding_theme_id` takes precedence

### Existing Parameter: `branding_theme_id`
- **Type:** `string`
- **Optional:** Yes
- **Description:** BrandingThemeID GUID from `xero_get_branding_themes`
- **Use When:** You already have the GUID or need precise control

---

## Common Template Names

**InHouse Print (business_id=1):**
- "Default Theme"
- "Standard Invoice"
- "Professional Quote"
- (Check with `xero_get_branding_themes(business_id=1)`)

**InHouse Publishing (business_id=2):**
- "Default Theme"
- "Publishing Template"
- (Check with `xero_get_branding_themes(business_id=2)`)

**InHouse Signs (business_id=3):**
- "Default Theme"
- "Signs Template"
- (Check with `xero_get_branding_themes(business_id=3)`)

---

## Error Handling

### Template Not Found
```python
xero_create_quote(
    business_id=1,
    contact_id="...",
    line_items=[...],
    template_name="NonExistentTemplate"  # Template doesn't exist
)

# Result: Warning logged, quote created with default template
# Function continues without error
```

### API Lookup Failure
```python
# If BrandingThemes API call fails
# Warning: "Could not lookup template 'Standard Invoice': [error]"
# Function continues without template
```

---

## Implementation Details

### Code Changes

**1. Schema (`xero_quotes_tools.json`):**
```json
{
  "template_name": {
    "type": "string",
    "description": "Template name (e.g., 'Default Theme', 'Standard Invoice'). Automatically looks up the BrandingThemeID."
  }
}
```

**2. Implementation (`xero_quotes.py`):**
```python
# Added template_name parameter
def xero_create_quote(
    business_id: int,
    contact_id: str,
    line_items: List[Dict[str, Any]],
    branding_theme_id: Optional[str] = None,
    template_name: Optional[str] = None,  # ← New parameter
    ...
)

# Auto-lookup logic
if template_name and not branding_theme_id:
    themes_response = client.make_request('GET', 'BrandingThemes')
    themes = themes_response.get('BrandingThemes', [])
    
    # Exact match
    for theme in themes:
        if theme.get('Name', '').lower() == template_name.lower():
            resolved_branding_theme_id = theme.get('BrandingThemeID')
            break
    
    # Partial match fallback
    if not resolved_branding_theme_id:
        for theme in themes:
            if template_name.lower() in theme.get('Name', '').lower():
                resolved_branding_theme_id = theme.get('BrandingThemeID')
                break
```

---

## Testing

### Validation Tests: 8/8 PASSING ✅

All existing tests still pass:
```
✅ Schema File Validation
✅ Implementation File Validation
✅ Credential Injection Prefix
✅ Function Signatures
✅ Schema-Implementation Name Match
✅ Pagination Parameters
✅ Branding Theme Support
✅ Filter Parameters for Large Dataset
```

### Manual Testing

```python
# Test 1: Template name lookup
result = xero_create_quote(
    business_id=1,
    contact_id="test-contact-id",
    line_items=[{"description": "Test", "quantity": 1, "unit_amount": 100}],
    template_name="Standard Invoice"
)

# Test 2: Both parameters (branding_theme_id takes precedence)
result = xero_create_quote(
    business_id=1,
    contact_id="test-contact-id",
    line_items=[...],
    branding_theme_id="exact-guid-123",
    template_name="Standard Invoice"  # Ignored
)

# Test 3: Invalid template name (graceful fallback)
result = xero_create_quote(
    business_id=1,
    contact_id="test-contact-id",
    line_items=[...],
    template_name="NonExistentTemplate"  # Uses default
)
```

---

## Benefits

✅ **Easier to Use:** No need to remember GUIDs  
✅ **More Intuitive:** Human-readable template names  
✅ **Backward Compatible:** Existing code still works  
✅ **Flexible:** Supports exact and partial matching  
✅ **Resilient:** Graceful fallback if lookup fails  

---

## Files Modified

| File | Change |
|------|--------|
| `tools/schemas/xero_quotes_tools.json` | Added `template_name` parameter |
| `tools/implementations/xero_quotes.py` | Added auto-lookup logic |

---

**Status:** ✅ COMPLETE - All tests passing  
**Backward Compatible:** ✅ Yes - existing code unaffected  
**Production Ready:** ✅ Yes
