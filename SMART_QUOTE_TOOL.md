# Smart Quote Tool - AI-Optimized Workflow

**Date:** December 1, 2025  
**Status:** ✅ COMPLETE - Production Ready

---

## Overview

`xero_create_quote_smart` is an AI-optimized tool that handles the **complete quote creation workflow in one call**. Perfect for natural language requests and automating repetitive tasks.

---

## What It Does Automatically

### 🔍 **Contact Lookup**
- Search by name: "ABC Company" → finds contact
- Search by email: "john@example.com" → finds contact
- Use ContactID: "a3675fc4-..." → direct lookup
- Partial matching: "John" → finds "John Smith"

### 📝 **Line Item Parsing**
- Natural language: "Business Cards 1000qty $150"
- Simple format: "Flyers A5 $95"
- Structured data: `{"description": "...", "quantity": 1, "price": 150}`
- Mixed formats supported

### 🎨 **Template Selection**
- Auto-selects default template if not specified
- Finds by name: "Professional", "Standard", etc.
- Uses business-appropriate defaults

### 📅 **Smart Dates**
- Today's date as quote date
- Auto-calculates expiry (default: 30 days)
- Custom validity: `valid_days=14`

### 📋 **Business Defaults**
- Terms and conditions per business
- Account codes (if needed)
- Professional formatting

### 📤 **Optional Auto-Send**
- `auto_send=True` marks quote as SENT
- Default: creates DRAFT for review

---

## Usage Examples

### Example 1: Simple Natural Language
```python
xero_create_quote_smart(
    business_id=1,
    customer="ABC Company",
    items=["Business Cards 1000qty $150", "Flyers A5 500qty $95"]
)
```

**What happens:**
1. ✅ Finds "ABC Company" in contacts
2. ✅ Parses "Business Cards 1000qty" → description, qty, price
3. ✅ Parses "Flyers A5 500qty" → description, qty, price
4. ✅ Selects default template
5. ✅ Auto-generates title: "Quote: Business Cards 1000qty... (+1 items)"
6. ✅ Sets expiry: 30 days from today
7. ✅ Creates DRAFT quote
8. ✅ Returns quote #, total, contact info

### Example 2: Customer Email Lookup
```python
xero_create_quote_smart(
    business_id=1,
    customer="john@example.com",
    items=[
        {"description": "Logo Design", "quantity": 1, "price": 500},
        {"description": "Business Card Design", "quantity": 1, "price": 150}
    ],
    valid_days=7,
    notes="Rush order - 48hr turnaround"
)
```

**What happens:**
1. ✅ Finds contact by email "john@example.com"
2. ✅ Uses structured line items
3. ✅ Sets 7-day validity
4. ✅ Adds notes to quote summary
5. ✅ Returns ready-to-send quote

### Example 3: Auto-Send Quote
```python
xero_create_quote_smart(
    business_id=1,
    customer="Jane Doe",
    items=["Website Design $2500", "Hosting Setup $250"],
    template="Professional",
    title="Website Project Quote",
    valid_days=14,
    auto_send=True
)
```

**What happens:**
1. ✅ Finds "Jane Doe" contact
2. ✅ Parses items from strings
3. ✅ Uses "Professional" template
4. ✅ Sets custom title
5. ✅ 14-day validity
6. ✅ Creates quote
7. ✅ **Marks as SENT automatically**

---

## Response Format

### Success Response
```json
{
  "success": true,
  "business_id": 1,
  "business_name": "InHouse Print",
  "workflow_log": [
    "🔍 Looking up customer...",
    "✅ Found customer: ABC Company (a3675fc4-...)",
    "📝 Parsing 2 line items...",
    "✅ Items parsed - Estimated total: $245.00",
    "🎨 Selecting template...",
    "✅ Using default template",
    "✅ Auto-generated title: Quote: Business Cards 1000qty... (+1 items)",
    "✅ Quote valid until: 2025-12-31 (30 days)",
    "✅ Using default terms",
    "📤 Creating quote in Xero...",
    "✅ Quote created: QT-0001"
  ],
  "quote": {
    "quote_id": "...",
    "quote_number": "QT-0001",
    "status": "DRAFT",
    "total": 245.00,
    "sub_total": 245.00,
    "total_tax": 0,
    "date": "2025-12-01",
    "expiry_date": "2025-12-31",
    "title": "Quote: Business Cards 1000qty... (+1 items)"
  },
  "contact": {
    "contact_id": "...",
    "name": "ABC Company",
    "email": "contact@abc.com"
  },
  "items": [
    {
      "description": "Business Cards 1000qty",
      "quantity": 1,
      "unit_amount": 150.00,
      "line_amount": 150.00
    },
    {
      "description": "Flyers A5 500qty",
      "quantity": 1,
      "unit_amount": 95.00,
      "line_amount": 95.00
    }
  ],
  "summary": {
    "total_items": 2,
    "estimated_total": "$245.00",
    "valid_until": "2025-12-31",
    "status": "DRAFT",
    "ready_to_send": true
  },
  "next_steps": [
    "Quote QT-0001 created successfully",
    "Status: DRAFT",
    "Use xero_update_quote to mark as SENT when ready",
    "Share quote with customer via email or Xero portal"
  ]
}
```

### Error Response (Customer Not Found)
```json
{
  "success": false,
  "error": "Customer not found: 'Unknown Company'",
  "suggestion": "Try searching with xero_get_contacts first, or provide exact ContactID",
  "workflow_log": [
    "🔍 Looking up customer..."
  ]
}
```

---

## Line Item Formats Supported

### Format 1: Natural Language String
```python
items=["Business Cards 1000qty $150"]
# Extracts: description="Business Cards", quantity=1000, price=150
```

### Format 2: Simple String
```python
items=["Logo Design $500"]
# Extracts: description="Logo Design", quantity=1, price=500
```

### Format 3: String with Price Only
```python
items=["Consultation 250.00"]
# Extracts: description="Consultation", quantity=1, price=250
```

### Format 4: Structured Object
```python
items=[{"description": "Business Cards", "quantity": 1000, "price": 150}]
# Uses exact values
```

### Format 5: Mixed Formats
```python
items=[
    "Business Cards 1000qty $150",
    {"description": "Flyers", "quantity": 500, "price": 95},
    "Design Work $300"
]
# All formats work together!
```

---

## AI Integration Examples

### ChatGPT/Claude Request
> "Create a quote for ABC Company: 1000 business cards at $150 and 500 flyers at $95"

**AI calls:**
```python
xero_create_quote_smart(
    business_id=1,
    customer="ABC Company",
    items=["Business Cards 1000qty $150", "Flyers 500qty $95"]
)
```

### Email Request
> "Quote john@example.com for website design $2500, valid for 2 weeks"

**AI calls:**
```python
xero_create_quote_smart(
    business_id=1,
    customer="john@example.com",
    items=["Website Design $2500"],
    valid_days=14
)
```

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `business_id` | integer | ✅ Yes | - | 1=Print, 2=Publishing, 3=Signs |
| `customer` | string | ✅ Yes | - | Name, email, or ContactID |
| `items` | array | ✅ Yes | - | Strings or objects |
| `template` | string | ❌ No | Auto | Template name hint |
| `title` | string | ❌ No | Auto | Quote title |
| `valid_days` | integer | ❌ No | 30 | Validity period |
| `notes` | string | ❌ No | - | Additional notes |
| `terms` | string | ❌ No | Business default | Terms and conditions |
| `reference` | string | ❌ No | - | Internal reference |
| `auto_send` | boolean | ❌ No | false | Mark as SENT |

---

## Workflow Log

Every response includes a `workflow_log` array showing exactly what the tool did:

```json
"workflow_log": [
  "🔍 Looking up customer...",
  "✅ Found customer: ABC Company (a3675fc4-...)",
  "📝 Parsing 2 line items...",
  "✅ Items parsed - Estimated total: $245.00",
  "🎨 Selecting template...",
  "✅ Using default template",
  "✅ Auto-generated title: Quote: Business Cards 1000qty...",
  "✅ Quote valid until: 2025-12-31 (30 days)",
  "✅ Using default terms",
  "📤 Creating quote in Xero...",
  "✅ Quote created: QT-0001"
]
```

Perfect for debugging and transparency!

---

## Comparison: Regular vs Smart

### Regular Tool (Multiple Steps)
```python
# Step 1: Find contact
contacts = xero_get_contacts(business_id=1)
contact_id = [c for c in contacts if 'ABC' in c['name']][0]['contact_id']

# Step 2: Get templates
themes = xero_get_branding_themes(business_id=1)
template_id = themes['branding_themes'][0]['branding_theme_id']

# Step 3: Create quote
xero_create_quote(
    business_id=1,
    contact_id=contact_id,
    line_items=[
        {"description": "Business Cards 1000qty", "quantity": 1, "unit_amount": 150},
        {"description": "Flyers A5 500qty", "quantity": 1, "unit_amount": 95}
    ],
    branding_theme_id=template_id,
    date="2025-12-01",
    expiry_date="2025-12-31"
)
```

### Smart Tool (One Call) ✨
```python
xero_create_quote_smart(
    business_id=1,
    customer="ABC Company",
    items=["Business Cards 1000qty $150", "Flyers A5 500qty $95"]
)
```

**Savings:** 3 API calls → 1 call, ~20 lines → 5 lines

---

## Business Defaults

### InHouse Print (business_id=1)
- **Terms:** "Payment due within 7 days. All prices are in AUD and exclude GST. Rush orders available for additional fee."
- **Template:** Default printing template

### InHouse Publishing (business_id=2)
- **Terms:** "Payment due within 14 days. Publishing services include design and print. Revisions subject to additional charges."
- **Template:** Default publishing template

### InHouse Signs (business_id=3)
- **Terms:** "Payment due within 7 days. Installation not included unless specified. Weather delays may affect timeline."
- **Template:** Default signs template

---

## Files Created

| File | Type | Size |
|------|------|------|
| `tools/schemas/xero_quotes_smart_tools.json` | Schema | ~3KB |
| `tools/implementations/xero_quotes_smart.py` | Implementation | ~15KB |

---

## Status

✅ **Production Ready**
- Schema defined
- Implementation complete
- Natural language parsing
- Contact lookup
- Template selection
- Smart defaults
- Error handling
- Comprehensive logging

---

**Perfect for:** AI agents, chatbots, automation workflows, natural language interfaces

**Use when:** You want one simple call instead of multiple steps!
