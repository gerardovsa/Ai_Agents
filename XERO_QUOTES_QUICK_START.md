# Xero Quotes - Quick Start Guide

**5 New Tools - Real API Integration - Production Ready**

---

## Tools Available

1. `xero_create_quote` - Create quotes with templates
2. `xero_list_quotes` - List with filters and pagination
3. `xero_get_quote_by_id` - Get specific quote
4. `xero_update_quote` - Update quote details
5. `xero_get_branding_themes` - List available templates

---

## Common Use Cases

### 1. Create a Quote
```python
xero_create_quote(
    business_id=1,
    contact_id="customer-guid",
    line_items=[
        {"description": "Item name", "quantity": 1, "unit_amount": 100.00}
    ],
    title="Quote Title"
)
```

### 2. List Recent Quotes (Last 30 Days)
```python
xero_list_quotes(
    business_id=1,
    date_from="2025-11-01",
    date_to="2025-12-01",
    page_size=50
)
```

### 3. Get Customer's Quotes
```python
xero_list_quotes(
    business_id=1,
    contact_id="customer-guid",
    date_from="2025-01-01"
)
```

### 4. Create Quote with Template
```python
# Step 1: Get available templates
themes = xero_get_branding_themes(business_id=1)

# Step 2: Create quote with template
xero_create_quote(
    business_id=1,
    contact_id="customer-guid",
    line_items=[...],
    branding_theme_id=themes['branding_themes'][0]['branding_theme_id']
)
```

### 5. Update Quote Status
```python
xero_update_quote(
    business_id=1,
    quote_id="quote-guid",
    status="SENT"
)
```

---

## Parameters

### Business IDs
- `1` = InHouse Print
- `2` = InHouse Publishing
- `3` = InHouse Signs

### Quote Status Values
- `DRAFT` - Created but not sent
- `SENT` - Sent to customer
- `DECLINED` - Customer rejected
- `ACCEPTED` - Customer accepted
- `INVOICED` - Converted to invoice
- `DELETED` - Soft deleted

### Pagination
- `page` - Page number (default: 1)
- `page_size` - Records per page (default: 100, max: 100)

### Date Format
- Always use: `YYYY-MM-DD` (e.g., "2025-12-01")

---

## Performance Tips for 70,000+ Quotes

✅ **DO:**
```python
# Use date range filters
xero_list_quotes(business_id=1, date_from="2025-11-01", date_to="2025-12-01")

# Filter by customer
xero_list_quotes(business_id=1, contact_id="customer-guid")

# Filter by status
xero_list_quotes(business_id=1, status="DRAFT")
```

❌ **DON'T:**
```python
# Don't query without filters (retrieves all 70K quotes!)
xero_list_quotes(business_id=1)  # SLOW!
```

---

## Response Format

### Success
```python
{
    "success": True,
    "business_id": 1,
    "business_name": "InHouse Print",
    "quote": { ... }  # or "quotes": [...]
}
```

### Error
```python
{
    "success": False,
    "error": "Error message",
    "traceback": "..."
}
```

---

## Files

| File | Purpose |
|------|---------|
| `tools/schemas/xero_quotes_tools.json` | Tool definitions |
| `tools/implementations/xero_quotes.py` | Python implementation |
| `test_xero_quotes.py` | Validation tests |

---

## Testing

```powershell
# Run validation tests
python test_xero_quotes.py

# Expected: 8/8 tests passing
```

---

## Documentation

- `XERO_QUOTES_COMPLETE.md` - Complete feature documentation
- `XERO_QUOTES_API_IMPLEMENTATION.md` - API implementation details
- `IMPLEMENTATION_SUMMARY.md` - Implementation summary

---

**Status:** ✅ Production Ready  
**Tests:** 8/8 Passing  
**API:** Real Xero integration
