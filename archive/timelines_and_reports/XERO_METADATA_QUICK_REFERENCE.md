# Xero Metadata Tools - Quick Reference

## Quick Decision Guide

```
Need Xero data? → Check this flowchart:

1. Do you know the specific ID?
   └─ YES → Use xero_get_invoice_by_id(invoice_id="...")
   
2. Do you need ALL historical data?
   └─ YES → Use standard tools (xero_get_invoices, etc.)
   
3. Do you need data from a specific time period?
   └─ YES → Follow metadata workflow below ↓

METADATA WORKFLOW:
┌─────────────────────────────────────────────────────┐
│ Step 1: Call xero_get_data_metadata(business_id=1) │
│ → Understand data scale and date ranges            │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ Step 2: Check period counts from metadata          │
│ Example: "1_month": 234 invoices                   │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ Step 3: Use appropriate range tool                 │
│ - xero_get_contacts_by_date_range()                │
│ - xero_get_invoices_by_date_range()                │
│ - xero_get_payments_by_date_range()                │
└─────────────────────────────────────────────────────┘
```

---

## Tool Reference

### 1. xero_get_data_metadata

**When:** First step before any date-based query  
**Returns:** Totals, date ranges, period breakdowns  
**Cost:** ~500 tokens, 2 seconds

```python
xero_get_data_metadata(business_id=1)

# Returns:
{
  "contacts": {
    "total": 7058,
    "by_period": {
      "1_month": 45,
      "3_months": 156,
      "6_months": 342
    }
  },
  "invoices": { ... },
  "recommendations": {
    "contacts": "Use xero_get_contacts_by_date_range..."
  }
}
```

### 2. xero_get_contacts_by_date_range

**When:** Need contacts from specific period  
**Parameters:** from_date, to_date, limit (default: 1000)  
**Returns:** Filtered contacts with parsed dates

```python
xero_get_contacts_by_date_range(
    business_id=1,
    from_date="2025-10-01",
    to_date="2025-11-16",
    limit=500
)

# Returns:
{
  "contact_count": 45,
  "truncated": false,
  "contacts": [...]
}
```

### 3. xero_get_invoices_by_date_range

**When:** Need invoices from specific period  
**Parameters:** from_date, to_date, status, limit  
**Returns:** Filtered invoices with parsed dates

```python
xero_get_invoices_by_date_range(
    business_id=1,
    from_date="2025-10-01",
    to_date="2025-11-16",
    status="AUTHORISED",  # Optional: DRAFT, SUBMITTED, AUTHORISED, PAID
    limit=1000
)

# Returns:
{
  "invoice_count": 234,
  "truncated": false,
  "invoices": [...]
}
```

### 4. xero_get_payments_by_date_range

**When:** Need payments from specific period  
**Parameters:** from_date, to_date, limit  
**Returns:** Filtered payments with parsed dates

```python
xero_get_payments_by_date_range(
    business_id=1,
    from_date="2025-11-01",
    to_date="2025-11-16",
    limit=500
)

# Returns:
{
  "payment_count": 127,
  "truncated": false,
  "payments": [...]
}
```

---

## Common Use Cases

### "Show me recent customers"
```python
# 1. Get metadata
meta = xero_get_data_metadata(business_id=1)
# → See: 45 contacts in last month

# 2. Get recent contacts
contacts = xero_get_contacts_by_date_range(
    business_id=1,
    from_date="2025-10-16",
    to_date="2025-11-16",
    limit=100
)
# → Returns: 45 contacts (22.5 KB)
```

### "Unpaid invoices from last month"
```python
# 1. Get metadata
meta = xero_get_data_metadata(business_id=1)
# → See: ~500 invoices per month

# 2. Get October unpaid invoices
invoices = xero_get_invoices_by_date_range(
    business_id=1,
    from_date="2025-10-01",
    to_date="2025-10-31",
    status="AUTHORISED",
    limit=1000
)
# → Returns: 234 invoices (468 KB)
```

### "This week's payments"
```python
# 1. Get metadata
meta = xero_get_data_metadata(business_id=1)
# → See: ~127 payments per week

# 2. Get this week's payments
payments = xero_get_payments_by_date_range(
    business_id=1,
    from_date="2025-11-10",
    to_date="2025-11-16",
    limit=200
)
# → Returns: 127 payments (38 KB)
```

---

## Time Periods Available in Metadata

```
1_week      → Last 7 days
2_weeks     → Last 14 days
3_weeks     → Last 21 days
4_weeks     → Last 28 days
1_month     → Last 30 days
2_months    → Last 60 days
3_months    → Last 90 days
4_months    → Last 120 days
5_months    → Last 150 days
6_months    → Last 180 days
7_months    → Last 210 days
8_months    → Last 240 days
9_months    → Last 270 days
10_months   → Last 300 days
11_months   → Last 330 days
12_months   → Last 365 days (1 year)
15_months   → Last 450 days
18_months   → Last 540 days
21_months   → Last 630 days
24_months   → Last 730 days (2 years)
```

---

## Performance Benefits

| Scenario | Old Way | New Way | Improvement |
|----------|---------|---------|-------------|
| "Recent customers" | 3.5 MB | 27 KB | 99.2% reduction |
| "Last month invoices" | 107 MB | 468 KB | 99.6% reduction |
| "This week payments" | 16 MB | 38 KB | 99.8% reduction |
| Response time | 10-30s | 1-3s | 3-10x faster |
| Token usage | 15,000 | 700 | 95% reduction |

---

## Best Practices

✅ **DO:**
- Call `xero_get_data_metadata` first when working with date ranges
- Use `limit` parameter to prevent memory issues
- Check `truncated` flag in response
- Use specific date ranges instead of "get all"
- Check `recommendations` in metadata response

❌ **DON'T:**
- Retrieve ALL data when you only need recent records
- Ignore the `limit` parameter (default: 1000 is safe)
- Skip metadata check for time-based queries
- Use range tools for single-record lookups

---

## Error Handling

All tools return consistent format:

**Success:**
```json
{
  "success": true,
  "business_name": "InHouse Print",
  "contact_count": 45,
  "contacts": [...]
}
```

**Failure:**
```json
{
  "success": false,
  "error": "from_date and to_date are required (YYYY-MM-DD format)",
  "traceback": "..."
}
```

---

## Date Format

**ALWAYS use:** `YYYY-MM-DD` format

Examples:
- ✅ `"2025-11-16"`
- ✅ `"2025-01-01"`
- ❌ `"11/16/2025"`
- ❌ `"16-11-2025"`
- ❌ `"Nov 16, 2025"`

---

## Tool Availability

**Total Xero Tools:** 11

**Read-Only (10):**
1. xero_get_invoices
2. xero_get_invoice_by_id
3. xero_get_contacts
4. xero_get_accounts
5. xero_get_bank_transactions
6. xero_get_payments
7. **xero_get_data_metadata** ← NEW
8. **xero_get_contacts_by_date_range** ← NEW
9. **xero_get_invoices_by_date_range** ← NEW
10. **xero_get_payments_by_date_range** ← NEW

**Write (1):**
11. xero_create_invoice

---

## Business IDs

```
business_id=1  → InHouse Print
business_id=2  → Publishing
business_id=3  → Signs
```

---

## Quick Tips

💡 **Tip 1:** Check metadata period counts before choosing date range
💡 **Tip 2:** Start with narrower date ranges, expand if needed
💡 **Tip 3:** Use `limit` parameter conservatively (100-500 for testing)
💡 **Tip 4:** Check `truncated` flag - if true, narrow your date range
💡 **Tip 5:** Metadata calls are cheap (~500 tokens), use liberally

---

**Last Updated:** November 16, 2025  
**Status:** Production Ready
