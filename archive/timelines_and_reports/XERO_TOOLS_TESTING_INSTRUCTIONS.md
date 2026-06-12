# Xero Tools - Complete Testing Instructions for AI

Use these instructions to systematically test all Xero tools and workflows. Copy and paste each test case to an AI assistant.

---

## 🧪 TEST SUITE 1: Basic Contact Operations

### Test 1.1: Search for Contacts
```
Test xero_get_contacts with the following:
- Business ID: 1 (InHouse Print)
- Search for: "CJ King"
- Limit: 5 contacts

Verify the response includes:
- contact_id (GUID format)
- name
- email address
- customer status

Save the first contact_id for use in subsequent tests.
```

### Test 1.2: Get Contact Details
```
Using the contact_id from Test 1.1, test xero_get_contact_by_id:
- Business ID: 1
- Contact ID: [from previous test]

Verify the response includes:
- Full contact profile
- Addresses (STREET and/or POBOX types)
- Phone numbers (up to 4 types)
- Contact persons with emails
- Tax number
- Account number

Note the email address for email workflow testing.
```

---

## 🧪 TEST SUITE 2: Quote Management

### Test 2.1: List Available Templates (Branding Themes)
```
Test xero_get_branding_themes:
- Business ID: 1

Expected outcomes:
- SUCCESS: Returns list of branding themes with IDs and names
- FAILURE (401): OAuth scope 'accounting.settings.read' is missing
  - This is OK - note the error and use template_name='Standard Invoice' in later tests

Save a template name (e.g., "Standard Invoice") for Test 2.2.
```

### Test 2.2: Create a New Quote
```
Test xero_create_quote with the following:
- Business ID: 1
- Contact ID: [from Test 1.1]
- Line Items:
  [
    {
      "description": "Test Business Cards - 1000qty",
      "quantity": 1,
      "unit_amount": 150.00,
      "account_code": "200"
    },
    {
      "description": "Test Letterhead - 500 sheets",
      "quantity": 1,
      "unit_amount": 85.00,
      "account_code": "200"
    }
  ]
- Template Name: "Standard Invoice" (or from Test 2.1)
- Title: "AI Test Quote - Do Not Use"
- Expiry Date: "2025-12-31"
- Summary: "This is a test quote created by AI for testing purposes only."
- Terms: "Test terms - Not a real quote."

Verify the response includes:
- quote_id (save this for next tests)
- quote_number (e.g., QU-0123)
- status: "DRAFT"
- total: 235.00
- contact information

Save the quote_id and quote_number for subsequent tests.
```

### Test 2.3: Get Quote Details
```
Using the quote_id from Test 2.2, test xero_get_quote_by_id:
- Business ID: 1
- Quote ID: [from Test 2.2]

Verify the response includes:
- Complete quote details
- Line items with descriptions and amounts
- pdf_url field (for downloading quote PDF)
- quote_number
- total amount
- contact information

Note: PDF URL may require authentication and expires quickly.
```

### Test 2.4: List Quotes by Contact
```
Test xero_list_quotes to find quotes for specific contact:
- Business ID: 1
- Contact ID: [from Test 1.1]
- Page: 1
- Page Size: 10

Verify the response includes:
- total_count (should show 100+ quotes for CJ King Printing)
- Array of quotes with quote_number, status, total, date
- The quote created in Test 2.2 should appear if status matches

Alternative: Filter by date range
- date_from: "2025-12-01"
- date_to: "2025-12-31"
```

### Test 2.5: Update Quote Status
```
Using the quote_id from Test 2.2, test xero_update_quote:
- Business ID: 1
- Quote ID: [from Test 2.2]
- Status: "SENT"

This marks the quote as sent to the customer.

Verify the response shows updated status: "SENT"
```

---

## 🧪 TEST SUITE 3: Invoice Operations

### Test 3.1: List Unpaid Invoices
```
Test xero_get_invoices:
- Business ID: 1
- Status: "AUTHORISED" (unpaid invoices)
- Limit: 10

Verify the response includes:
- Invoice count
- Array of invoices with invoice_number, total, due_date, contact_name
- status: "AUTHORISED"

Expected result: ~204 AUTHORISED invoices
```

### Test 3.2: Get Invoice Details
```
Using an invoice_id from Test 3.1, test xero_get_invoice_by_id:
- Business ID: 1
- Invoice ID: [from previous test]

Verify the response includes:
- Complete invoice details
- Line items
- Payment status
- Due date
- Total amount
```

---

## 🧪 TEST SUITE 4: Payment Tracking

### Test 4.1: List Recent Payments
```
Test xero_get_payments:
- Business ID: 1
- Limit: 50

Verify the response includes:
- Payment count
- Array of payments with payment_id, date, amount, invoice reference
- Payment status

Expected result: ~50 payments returned
```

---

## 🧪 TEST SUITE 5: Chart of Accounts (May Fail)

### Test 5.1: Get Accounts
```
Test xero_get_accounts:
- Business ID: 1
- Limit: 10

Expected outcomes:
- SUCCESS: Returns list of accounts with codes and names
- FAILURE (401): OAuth scope 'accounting.settings.read' is missing
  - This is expected - note the error
  - Account code "200" (Sales) is commonly used and known to work

Note: This endpoint requires additional OAuth scope and may fail.
```

---

## 🧪 TEST SUITE 6: Complete Workflow Test - Quote Creation + Email

### Test 6.1: Find Customer for Quote
```
Test xero_get_contacts:
- Business ID: 1
- Search: "ABC" or any partial company name
- Limit: 5

Save the first result's:
- contact_id
- name
- email (if available, use placeholder if not)
```

### Test 6.2: Check Templates (Optional)
```
Try xero_get_branding_themes:
- Business ID: 1

If fails with 401: Use template_name='Standard Invoice' in next step
If succeeds: Note a template name to use
```

### Test 6.3: Create Quote with Template
```
Test xero_create_quote:
- Business ID: 1
- Contact ID: [from Test 6.1]
- Line Items:
  [
    {
      "description": "Professional Business Cards - 1000qty, 350GSM",
      "quantity": 1,
      "unit_amount": 150.00,
      "account_code": "200"
    },
    {
      "description": "Letterhead - 500 sheets, Full Color",
      "quantity": 1,
      "unit_amount": 85.00,
      "account_code": "200"
    },
    {
      "description": "Envelopes - 250 DL size",
      "quantity": 1,
      "unit_amount": 45.00,
      "account_code": "200"
    }
  ]
- Template Name: "Standard Invoice"
- Title: "Professional Printing Services Quote"
- Expiry Date: "2025-12-31"
- Summary: "Thank you for your interest in our printing services."
- Terms: "Payment due within 30 days. 50% deposit required."

Save:
- quote_id
- quote_number
- total amount
```

### Test 6.4: Get Quote Details with PDF URL
```
Test xero_get_quote_by_id:
- Business ID: 1
- Quote ID: [from Test 6.3]

Verify response includes:
- pdf_url (for downloading quote PDF)
- Complete line items
- Total: 280.00
- Contact information
```

### Test 6.5: Prepare Draft Email (Documentation Only)
```
Document how to call outlook_send_email (don't actually execute):
- to: [email from Test 6.1 or "customer@example.com"]
- subject: "Quote [quote_number] - Professional Printing Services"
- body: HTML formatted with:
  - Greeting with customer name
  - Quote number and total amount
  - Expiry date
  - Link to quote or "attached quote" message
  - Professional closing
- body_type: "html"
- attachments: (optional) PDF if downloaded and base64 encoded

Note: outlook_send_email creates DRAFTS only - not sent automatically
```

---

## 🧪 TEST SUITE 7: Data Volume and Performance

### Test 7.1: Check Data Metadata
```
Test xero_get_data_metadata:
- Business ID: 1

Verify the response shows:
- Total invoice count
- Invoice date ranges
- Monthly breakdown
- Recommended query approach
- Warning about data volume

Use this to understand scale before querying large datasets.
```

### Test 7.2: Safe Date-Range Query
```
Test xero_get_invoices_by_date_range:
- Business ID: 1
- From Date: "2025-11-01"
- To Date: "2025-11-30"
- Status: "PAID"

Verify the response includes:
- Invoices within date range only
- Performance is reasonable
- No token overflow
```

---

## 🧪 TEST SUITE 8: Error Handling

### Test 8.1: Invalid Contact ID
```
Test xero_get_contact_by_id with invalid ID:
- Business ID: 1
- Contact ID: "invalid-guid-12345"

Verify proper error handling:
- Returns error message
- Explains what went wrong
- Doesn't crash or hang
```

### Test 8.2: Missing OAuth Scope
```
Test xero_get_branding_themes:
- Business ID: 1

If 401 Unauthorized:
- Verify error message mentions OAuth scope requirement
- Confirms 'accounting.settings.read' scope is missing
- Provides fallback suggestion (use template_name parameter)
```

### Test 8.3: Missing Required Parameters
```
Try xero_create_quote without line_items:
- Business ID: 1
- Contact ID: [valid ID]
- (omit line_items)

Verify error about missing required parameter.
```

---

## 📊 COMPREHENSIVE TEST RESULTS TEMPLATE

After running all tests, document results in this format:

```
═══════════════════════════════════════════════════════════════
XERO TOOLS TEST RESULTS SUMMARY
═══════════════════════════════════════════════════════════════

Test Date: [Date]
Business: InHouse Print (ID: 1)
Total Tests: 18

───────────────────────────────────────────────────────────────
SUITE 1: Basic Contact Operations (2 tests)
───────────────────────────────────────────────────────────────
✅ Test 1.1: Search Contacts - PASS
   - Found: [X] contacts
   - Sample: [Contact Name]
   - Contact ID: [GUID]

✅ Test 1.2: Get Contact Details - PASS
   - Addresses: [X]
   - Phones: [X]
   - Email: [email or N/A]

───────────────────────────────────────────────────────────────
SUITE 2: Quote Management (5 tests)
───────────────────────────────────────────────────────────────
[❌/⚠️/✅] Test 2.1: List Templates - [PASS/FAIL]
   - Result: [Success or 401 OAuth scope missing]
   
✅ Test 2.2: Create Quote - PASS
   - Quote Number: [QU-XXXX]
   - Quote ID: [GUID]
   - Total: $[amount]
   - Status: DRAFT

✅ Test 2.3: Get Quote Details - PASS
   - PDF URL: [available/not available]
   - Line Items: [X]

✅ Test 2.4: List Quotes by Contact - PASS
   - Total Count: [X]
   - Returned: [X]

✅ Test 2.5: Update Quote Status - PASS
   - New Status: SENT

───────────────────────────────────────────────────────────────
SUITE 3: Invoice Operations (2 tests)
───────────────────────────────────────────────────────────────
✅ Test 3.1: List Unpaid Invoices - PASS
   - Count: [X] AUTHORISED invoices

✅ Test 3.2: Get Invoice Details - PASS
   - Invoice retrieved successfully

───────────────────────────────────────────────────────────────
SUITE 4: Payment Tracking (1 test)
───────────────────────────────────────────────────────────────
✅ Test 4.1: List Payments - PASS
   - Payments: [X]

───────────────────────────────────────────────────────────────
SUITE 5: Chart of Accounts (1 test)
───────────────────────────────────────────────────────────────
[❌/⚠️/✅] Test 5.1: Get Accounts - [PASS/FAIL]
   - Result: [Success or 401 OAuth scope missing]

───────────────────────────────────────────────────────────────
SUITE 6: Complete Workflow (5 tests)
───────────────────────────────────────────────────────────────
✅ Test 6.1-6.5: Full Quote + Email Workflow - PASS
   - Customer: [Name]
   - Quote: [QU-XXXX] ($[amount])
   - PDF URL: [available/not available]
   - Email: [prepared/not prepared]

───────────────────────────────────────────────────────────────
SUITE 7: Data Volume (2 tests)
───────────────────────────────────────────────────────────────
✅ Test 7.1: Data Metadata - PASS
✅ Test 7.2: Date-Range Query - PASS

───────────────────────────────────────────────────────────────
SUITE 8: Error Handling (3 tests)
───────────────────────────────────────────────────────────────
✅ Test 8.1: Invalid Contact ID - Proper error handling
✅ Test 8.2: Missing OAuth Scope - Proper error message
✅ Test 8.3: Missing Parameters - Proper validation

───────────────────────────────────────────────────────────────
OVERALL RESULTS
───────────────────────────────────────────────────────────────
Tests Passed: [X]/18
Tests Failed: [X]/18
Tests Skipped (OAuth): [X]/18
Pass Rate: [XX]%

Known Limitations:
- OAuth scope 'accounting.settings.read' missing (affects 2 tests)
- This is expected and documented

Core Workflow Status: ✅ FULLY FUNCTIONAL
Quote Creation + Email: ✅ WORKING
Contact Management: ✅ WORKING
Invoice/Payment Tracking: ✅ WORKING

═══════════════════════════════════════════════════════════════
```

---

## 🎯 QUICK REFERENCE: Copy-Paste Test Commands

### Fastest Way to Test Core Functionality
```
Test 1: Search contacts
xero_get_contacts(business_id=1, search="CJ King", limit=5)

Test 2: Get contact details  
xero_get_contact_by_id(business_id=1, contact_id="996dfeab-0754-4d5c-881b-00740d6d12a2")

Test 3: Create quote
xero_create_quote(
  business_id=1,
  contact_id="996dfeab-0754-4d5c-881b-00740d6d12a2",
  line_items=[{"description":"Test Item","quantity":1,"unit_amount":100.00,"account_code":"200"}],
  template_name="Standard Invoice",
  title="Test Quote"
)

Test 4: List quotes
xero_list_quotes(business_id=1, contact_id="996dfeab-0754-4d5c-881b-00740d6d12a2", page_size=10)

Test 5: Get invoices
xero_get_invoices(business_id=1, status="AUTHORISED", limit=10)

Test 6: Get payments
xero_get_payments(business_id=1, limit=50)
```

---

## ⚠️ IMPORTANT NOTES FOR AI TESTERS

1. **OAuth Scopes**: Two endpoints require 'accounting.settings.read' scope:
   - xero_get_branding_themes (templates)
   - xero_get_accounts (chart of accounts)
   - These may return 401 Unauthorized - this is EXPECTED and documented

2. **Real vs Test Data**: All operations use real Xero data for InHouse Print
   - Create test quotes with obvious "TEST" labels
   - Don't convert test quotes to invoices
   - Mark test quotes with status DRAFT or DECLINED

3. **Email Operations**: outlook_send_email creates DRAFTS only
   - Emails are NOT sent automatically
   - User must manually send from Outlook Drafts folder
   - This is intentional for safety

4. **PDF URLs**: Quote PDFs require authentication
   - URLs expire quickly
   - Download immediately if needed for attachments
   - May need Xero OAuth token to access

5. **Contact IDs**: Use GUIDs in this format:
   - Valid: "996dfeab-0754-4d5c-881b-00740d6d12a2"
   - Invalid: "123", "abc", short strings

6. **Account Codes**: Standard codes for line items:
   - "200" = Sales/Revenue (standard for quotes)
   - Check Xero chart of accounts for other codes

7. **Date Formats**: Always use YYYY-MM-DD format:
   - Valid: "2025-12-31"
   - Invalid: "12/31/2025", "31-Dec-2025"

8. **Test Cleanup**: After testing, you may want to:
   - Mark test quotes as DECLINED or DELETED
   - Note which records are test data
   - Don't delete - just mark status

---

## 🚀 AUTOMATION SCRIPT (Optional)

If testing via Python script, use this template:

```python
import json
from tools.implementations.xero import xero_get_contacts, xero_get_contact_by_id
from tools.implementations.xero_quotes import (
    xero_create_quote, 
    xero_get_quote_by_id,
    xero_list_quotes,
    xero_get_branding_themes
)

# Test configuration
BUSINESS_ID = 1
test_results = {"passed": 0, "failed": 0, "tests": []}

def run_test(name, func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        if result.get('success'):
            test_results["passed"] += 1
            test_results["tests"].append(f"✅ {name}")
            print(f"✅ {name}")
            return result
        else:
            test_results["failed"] += 1
            test_results["tests"].append(f"❌ {name}: {result.get('error')}")
            print(f"❌ {name}: {result.get('error')}")
            return None
    except Exception as e:
        test_results["failed"] += 1
        test_results["tests"].append(f"❌ {name}: {str(e)}")
        print(f"❌ {name}: {str(e)}")
        return None

# Run tests
print("Starting Xero Tools Test Suite...\n")

# Test 1: Get contacts
contacts = run_test(
    "Get Contacts", 
    xero_get_contacts,
    business_id=BUSINESS_ID,
    search="CJ King",
    limit=5
)

if contacts and contacts.get('contacts'):
    contact_id = contacts['contacts'][0]['contact_id']
    
    # Test 2: Get contact details
    run_test(
        "Get Contact Details",
        xero_get_contact_by_id,
        business_id=BUSINESS_ID,
        contact_id=contact_id
    )
    
    # Test 3: Create quote
    quote = run_test(
        "Create Quote",
        xero_create_quote,
        business_id=BUSINESS_ID,
        contact_id=contact_id,
        line_items=[
            {
                "description": "Test Item",
                "quantity": 1,
                "unit_amount": 100.00,
                "account_code": "200"
            }
        ],
        template_name="Standard Invoice",
        title="AI Test Quote"
    )
    
    if quote:
        quote_id = quote.get('quote_id')
        
        # Test 4: Get quote details
        run_test(
            "Get Quote Details",
            xero_get_quote_by_id,
            business_id=BUSINESS_ID,
            quote_id=quote_id
        )

# Print summary
print(f"\n{'='*60}")
print(f"Test Results: {test_results['passed']} passed, {test_results['failed']} failed")
print(f"{'='*60}")
for test in test_results['tests']:
    print(test)
```

---

## 📚 ADDITIONAL RESOURCES

- **Workflow Documentation**: `WORKFLOW_QUOTE_WITH_TEMPLATE_AND_EMAIL.md`
- **Tool Schemas**: `tools/schemas/xero_tools.json`, `tools/schemas/xero_quotes_tools.json`
- **Implementation**: `tools/implementations/xero.py`, `tools/implementations/xero_quotes.py`
- **Test Reports**: `UI/modules_external/xero/test_results/test_report.txt`

---

**Testing Complete!** Use these instructions to thoroughly test all Xero functionality.
