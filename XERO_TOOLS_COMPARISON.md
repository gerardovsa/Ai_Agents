# Xero Quote Tools - Complete Comparison

**Which tool should I use?**

---

## Tool Overview

| Tool | Purpose | Best For | AI-Friendly |
|------|---------|----------|-------------|
| `xero_create_quote_smart` | **ONE-CALL WORKFLOW** | Natural language, AI automation | ⭐⭐⭐⭐⭐ |
| `xero_create_quote` | Direct quote creation | Precise control, structured data | ⭐⭐⭐ |
| `xero_list_quotes` | List/search quotes | Finding existing quotes | ⭐⭐⭐⭐ |
| `xero_get_quote_by_id` | Get specific quote | Retrieving quote details | ⭐⭐⭐ |
| `xero_update_quote` | Update existing quote | Modifying quotes | ⭐⭐⭐ |
| `xero_get_branding_themes` | List templates | Template management | ⭐⭐ |

---

## Quick Decision Guide

### Use `xero_create_quote_smart` when:
✅ Working with natural language requests  
✅ AI agent needs to create quotes automatically  
✅ Don't want to handle contact lookup separately  
✅ Want automatic template selection  
✅ Need smart defaults (dates, terms, etc.)  
✅ Want comprehensive workflow logging  

**Example:** "Create a quote for ABC Company: 1000 business cards at $150"

### Use `xero_create_quote` when:
✅ Have exact ContactID already  
✅ Need precise control over every field  
✅ Working with structured input data  
✅ Integrating with existing system that provides all data  

**Example:** Already have contact_id, line_items array, and all details

---

## Feature Comparison

| Feature | Smart Tool | Regular Tool |
|---------|------------|--------------|
| **Contact Lookup** | ✅ Automatic (name/email/ID) | ❌ Requires ContactID |
| **Line Item Parsing** | ✅ Natural language + structured | ⚠️ Structured only |
| **Template Selection** | ✅ Auto + by name | ⚠️ Requires BrandingThemeID |
| **Date Defaults** | ✅ Auto (today + validity days) | ❌ Must provide dates |
| **Title Generation** | ✅ Auto from items | ❌ Manual |
| **Terms/Conditions** | ✅ Business defaults | ❌ Manual |
| **Workflow Logging** | ✅ Detailed log | ❌ No log |
| **Error Guidance** | ✅ Helpful suggestions | ⚠️ Basic errors |
| **Auto-Send Option** | ✅ Yes | ❌ No |
| **Summary/Next Steps** | ✅ Yes | ❌ No |

---

## Code Comparison

### Scenario: Create quote for "ABC Company" with 2 items

#### Using Smart Tool (Recommended for AI) ⭐
```python
result = xero_create_quote_smart(
    business_id=1,
    customer="ABC Company",
    items=["Business Cards 1000qty $150", "Flyers 500qty $95"]
)

# Done! Returns:
# - Quote number, total, status
# - Contact info
# - Workflow log
# - Next steps
```

**Lines of code:** 5  
**API calls:** 3-4 (contact lookup + template lookup + create)  
**Error handling:** Built-in with suggestions

#### Using Regular Tool (Precise Control)
```python
# Step 1: Find contact
contacts_response = xero_list_quotes(business_id=1)
contacts = contacts_response['quotes']
contact = [c for c in contacts if 'ABC Company' in c['contact']['name']][0]
contact_id = contact['contact']['id']

# Step 2: Get template
themes = xero_get_branding_themes(business_id=1)
template_id = themes['branding_themes'][0]['branding_theme_id']

# Step 3: Create quote
result = xero_create_quote(
    business_id=1,
    contact_id=contact_id,
    line_items=[
        {"description": "Business Cards 1000qty", "quantity": 1, "unit_amount": 150},
        {"description": "Flyers 500qty", "quantity": 1, "unit_amount": 95}
    ],
    branding_theme_id=template_id,
    date="2025-12-01",
    expiry_date="2025-12-31",
    title="Quote: Business Cards 1000qty... (+1 items)",
    terms="Payment due within 7 days. All prices are in AUD and exclude GST."
)
```

**Lines of code:** ~25  
**API calls:** 3 separate calls (list contacts + get templates + create)  
**Error handling:** Manual

---

## AI Agent Recommendations

### For ChatGPT/Claude/AI Assistants:
**Use `xero_create_quote_smart`** 99% of the time

**Why:**
- Handles natural language perfectly
- Single function call = simpler prompt
- Auto-handles common errors
- Provides clear workflow log for explanation
- Returns next steps for user

### For Structured Data Systems:
**Use `xero_create_quote`** when you have all data ready

**Why:**
- No extra lookups needed
- Direct control over fields
- Faster if you already have ContactID

---

## Real-World Examples

### Example 1: Customer Request via Chat
**User says:** "Quote John Smith for 1000 business cards at $150, valid for 2 weeks"

**Smart Tool:**
```python
xero_create_quote_smart(
    business_id=1,
    customer="John Smith",
    items=["Business Cards 1000qty $150"],
    valid_days=14
)
```
✅ One call, done!

**Regular Tool:**
```python
# Need to: find John Smith, get template, format items, calculate dates, etc.
# 4-5 separate calls and data processing
```
❌ Complex workflow

### Example 2: Email-Based Request
**User says:** "Send quote to jane@example.com for logo design $500 and business cards $150"

**Smart Tool:**
```python
xero_create_quote_smart(
    business_id=1,
    customer="jane@example.com",
    items=["Logo Design $500", "Business Cards $150"],
    auto_send=True
)
```
✅ Finds contact by email, creates and sends quote

**Regular Tool:**
```python
# Need to: query contacts by email, handle not found, format items, create, then update status
# 5+ separate calls
```
❌ Multi-step process

### Example 3: Repeat Customer with Template
**User says:** "Create quote for ABC Company using Professional template: website design $2500"

**Smart Tool:**
```python
xero_create_quote_smart(
    business_id=1,
    customer="ABC Company",
    items=["Website Design $2500"],
    template="Professional"
)
```
✅ Finds customer, finds template by name, creates quote

**Regular Tool:**
```python
# Need to: get contacts, find ABC Company, get templates, match "Professional", create quote
# 4+ separate calls
```
❌ Manual matching required

---

## When NOT to Use Smart Tool

### Use Regular Tools Instead When:
❌ You need to create 100+ quotes in bulk (smart tool has lookup overhead)  
❌ You're integrating with system that already has all IDs  
❌ You need to bypass validation/parsing for speed  
❌ You're building a quote preview that doesn't save  

---

## Migration Guide

### Already Using Regular Tools?

**You can keep using them!** Smart tool is additive, not replacement.

**Gradually migrate:**
1. Start with new AI-driven features → use smart tool
2. Keep existing integrations → use regular tools
3. Refactor over time → migrate to smart tool when convenient

---

## Summary

| Use Case | Recommended Tool | Why |
|----------|------------------|-----|
| AI agent creating quotes | `xero_create_quote_smart` | Natural language, auto-workflow |
| Chatbot quote requests | `xero_create_quote_smart` | One call, comprehensive response |
| User says "quote [customer]" | `xero_create_quote_smart` | Contact lookup included |
| Email-based requests | `xero_create_quote_smart` | Email search built-in |
| Bulk quote generation | `xero_create_quote` | Faster with pre-fetched data |
| System integration | `xero_create_quote` | Direct control, no lookups |
| Quote updates | `xero_update_quote` | Modify existing quotes |
| Search quotes | `xero_list_quotes` | Filter and pagination |

---

**Bottom Line:**  
- 🤖 **AI Agent?** → Use `xero_create_quote_smart`  
- 🔧 **System Integration?** → Use `xero_create_quote`  
- 🔍 **Finding Quotes?** → Use `xero_list_quotes`  
- ✏️ **Updating Quote?** → Use `xero_update_quote`

**Both tools are production-ready and fully supported!**
