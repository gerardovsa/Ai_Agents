"""
COMPLETE WORKFLOW: Create Quote with Template + Attach to Draft Email

═══════════════════════════════════════════════════════════════════════════════
📋 WORKFLOW OVERVIEW
═══════════════════════════════════════════════════════════════════════════════

This document describes the complete 5-step workflow for:
1. Finding a customer contact
2. Getting available branding themes (quote templates)
3. Creating a quote with the selected template
4. Retrieving quote details including PDF URL
5. Creating a draft email with quote attached

═══════════════════════════════════════════════════════════════════════════════
🔄 STEP-BY-STEP WORKFLOW
═══════════════════════════════════════════════════════════════════════════════

STEP 1: Find Customer Contact
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tool: xero_get_contacts
Purpose: Search for the customer who will receive the quote

Example:
```python
from tools.implementations.xero import xero_get_contacts

result = xero_get_contacts(
    business_id=1,  # 1=InHouse Print, 2=Publishing, 3=Signs
    search='ABC Company',
    limit=10
)

# Result contains:
{
    "success": True,
    "contacts": [
        {
            "contact_id": "abc-123-guid",
            "name": "ABC Company",
            "email": "billing@abccompany.com",
            "status": "ACTIVE"
        }
    ]
}

# Extract needed values:
contact_id = result['contacts'][0]['contact_id']
contact_name = result['contacts'][0]['name']
contact_email = result['contacts'][0].get('email', 'N/A')
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 2: Get Available Branding Themes (Templates)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tool: xero_get_branding_themes
Purpose: List available quote templates with logos, colors, and styling

⚠️ IMPORTANT: Requires 'accounting.settings.read' OAuth scope
   If scope is missing, you'll get 401 Unauthorized error

Example:
```python
from tools.implementations.xero_quotes import xero_get_branding_themes

result = xero_get_branding_themes(business_id=1)

# Result contains:
{
    "success": True,
    "branding_themes": [
        {
            "branding_theme_id": "d5b89e36-8a28-4c40-b8e4-2a0d3f5d7c93",
            "name": "Standard Invoice",
            "logo_url": "https://...",
            "type": "INVOICE",
            "sort_order": 0
        },
        {
            "branding_theme_id": "xyz-789-guid",
            "name": "Premium Quote Template",
            "logo_url": "https://...",
            "type": "INVOICE",
            "sort_order": 1
        }
    ]
}

# Extract needed values:
template_name = result['branding_themes'][0]['name']
branding_theme_id = result['branding_themes'][0]['branding_theme_id']
```

Alternative: If OAuth scope is missing, use template_name parameter instead
```python
# Skip xero_get_branding_themes and use known template name
template_name = "Standard Invoice"  # Use default or known template
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 3: Create Quote with Template
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tool: xero_create_quote
Purpose: Create a new sales quote with line items and selected template

Method A: Using template_name (Easier - automatic lookup)
```python
from tools.implementations.xero_quotes import xero_create_quote

result = xero_create_quote(
    business_id=1,
    contact_id="abc-123-guid",
    line_items=[
        {
            "description": "Business Cards - 1000qty, 350GSM Premium",
            "quantity": 1,
            "unit_amount": 150.00,
            "account_code": "200"  # Sales account
        },
        {
            "description": "Letterhead - 500 sheets, Full Color",
            "quantity": 1,
            "unit_amount": 85.00,
            "account_code": "200"
        },
        {
            "description": "Envelopes - 250 DL size with logo",
            "quantity": 1,
            "unit_amount": 45.00,
            "account_code": "200"
        }
    ],
    template_name="Standard Invoice",  # Auto-lookup BrandingThemeID
    title="Professional Printing Services Quote",
    expiry_date="2025-12-31",
    summary="Thank you for your interest. This quote includes premium business cards, letterhead, and envelopes.",
    terms="Payment due within 30 days. 50% deposit required to commence production."
)

# Result contains:
{
    "success": True,
    "quote_id": "quote-guid-123",
    "quote_number": "QU-0145",
    "status": "DRAFT",
    "total": 280.00,
    "sub_total": 280.00,
    "total_tax": 0.00,
    "date": "2025-12-08",
    "expiry_date": "2025-12-31",
    "contact": {
        "contact_id": "abc-123-guid",
        "name": "ABC Company"
    }
}
```

Method B: Using branding_theme_id (If you have the GUID from Step 2)
```python
result = xero_create_quote(
    business_id=1,
    contact_id="abc-123-guid",
    line_items=[...],
    branding_theme_id="d5b89e36-8a28-4c40-b8e4-2a0d3f5d7c93",  # Direct GUID
    title="Professional Printing Services Quote",
    expiry_date="2025-12-31"
)
```

Method C: No template (Uses Xero's default styling)
```python
result = xero_create_quote(
    business_id=1,
    contact_id="abc-123-guid",
    line_items=[...],
    # No template_name or branding_theme_id - uses default
    title="Professional Printing Services Quote"
)
```

# Extract needed values:
quote_id = result['quote_id']
quote_number = result['quote_number']
quote_total = result['total']
quote_status = result['status']

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 4: Get Quote Details Including PDF URL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tool: xero_get_quote_by_id
Purpose: Retrieve complete quote details including PDF download URL

Example:
```python
from tools.implementations.xero_quotes import xero_get_quote_by_id

result = xero_get_quote_by_id(
    business_id=1,
    quote_id="quote-guid-123"
)

# Result contains:
{
    "success": True,
    "quote_id": "quote-guid-123",
    "quote_number": "QU-0145",
    "status": "DRAFT",
    "total": 280.00,
    "contact": {
        "name": "ABC Company",
        "email": "billing@abccompany.com"
    },
    "line_items": [
        {
            "description": "Business Cards - 1000qty, 350GSM Premium",
            "quantity": 1.0,
            "unit_amount": 150.00,
            "line_amount": 150.00
        },
        # ... more line items
    ],
    "pdf_url": "https://api.xero.com/api.xro/2.0/Quotes/quote-guid-123/pdf",
    "date": "2025-12-08",
    "expiry_date": "2025-12-31",
    "title": "Professional Printing Services Quote",
    "summary": "Thank you for your interest...",
    "terms": "Payment due within 30 days..."
}

# Extract PDF URL:
pdf_url = result['pdf_url']
```

💡 Note: PDF URLs from Xero API may require authentication
    Download immediately and encode to base64 for email attachment

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 5: Create Draft Email with Quote
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tool: outlook_send_email (creates DRAFT, does not send)
Purpose: Create draft email with quote information and optional PDF attachment

⚠️ IMPORTANT: outlook_send_email creates DRAFTS only - not sent automatically!
   User must manually send from Outlook Drafts folder

Option A: Email with PDF Attachment
```python
from tools.implementations.microsoft_outlook_tools import outlook_send_email
import base64
import requests

# Download PDF from Xero (requires authentication)
# Note: In practice, you'd need to handle Xero OAuth authentication
pdf_response = requests.get(pdf_url, headers={'Authorization': 'Bearer <xero_token>'})
pdf_content = base64.b64encode(pdf_response.content).decode('utf-8')

# Create draft email with attachment
result = outlook_send_email(
    to=["billing@abccompany.com"],
    subject=f"Quote {quote_number} - Professional Printing Services",
    body=f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #2c5aa0;">Your Printing Services Quote</h2>
        
        <p>Dear ABC Company,</p>
        
        <p>Thank you for your interest in our professional printing services. 
        Please find your quote attached.</p>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #2c5aa0; margin: 20px 0;">
            <p style="margin: 5px 0;"><strong>Quote Number:</strong> {quote_number}</p>
            <p style="margin: 5px 0;"><strong>Total Amount:</strong> ${quote_total:.2f}</p>
            <p style="margin: 5px 0;"><strong>Valid Until:</strong> December 31, 2025</p>
        </div>
        
        <h3>Quote Items:</h3>
        <ul>
            <li>Business Cards - 1000qty, 350GSM Premium - $150.00</li>
            <li>Letterhead - 500 sheets, Full Color - $85.00</li>
            <li>Envelopes - 250 DL size with logo - $45.00</li>
        </ul>
        
        <p>If you have any questions or would like to proceed with this order, 
        please don't hesitate to contact us.</p>
        
        <p style="margin-top: 30px;">
        Best regards,<br>
        <strong>InHouse Print Team</strong><br>
        Phone: (555) 123-4567<br>
        Email: sales@inhouseprint.com
        </p>
    </body>
    </html>
    """,
    body_type='html',
    attachments=[
        {
            'name': f'Quote-{quote_number}.pdf',
            'content_type': 'application/pdf',
            'content': pdf_content  # Base64 encoded PDF
        }
    ]
)

# Result:
{
    "success": True,
    "message": "⚠️ EMAIL SAVED AS DRAFT (not sent) - 1 recipient(s)",
    "note": "This email was saved to your Outlook Drafts folder for manual review and sending.",
    "recipients": ["billing@abccompany.com"],
    "draft_id": "draft-message-id-123",
    "action_required": "Please open Outlook and send this email manually from your Drafts folder."
}
```

Option B: Email with Quote Link (Simpler - no PDF attachment)
```python
result = outlook_send_email(
    to=["billing@abccompany.com"],
    subject=f"Quote {quote_number} - Professional Printing Services",
    body=f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>Your Printing Services Quote</h2>
        <p>Dear ABC Company,</p>
        <p>Your quote is ready to view:</p>
        <p><a href="{pdf_url}" style="background-color: #2c5aa0; color: white; padding: 10px 20px; text-decoration: none; display: inline-block;">
        View Quote {quote_number}</a></p>
        <p><strong>Total:</strong> ${quote_total:.2f}<br>
        <strong>Valid Until:</strong> December 31, 2025</p>
    </body>
    </html>
    """,
    body_type='html'
    # No attachments - just include link to quote
)
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

═══════════════════════════════════════════════════════════════════════════════
📊 COMPLETE WORKFLOW EXAMPLE
═══════════════════════════════════════════════════════════════════════════════

Here's the complete workflow in one script:

```python
from tools.implementations.xero import xero_get_contacts
from tools.implementations.xero_quotes import (
    xero_get_branding_themes,
    xero_create_quote,
    xero_get_quote_by_id
)
from tools.implementations.microsoft_outlook_tools import outlook_send_email

# Configuration
BUSINESS_ID = 1  # InHouse Print

# Step 1: Find customer
contacts = xero_get_contacts(business_id=BUSINESS_ID, search='ABC Company', limit=5)
contact_id = contacts['contacts'][0]['contact_id']
contact_name = contacts['contacts'][0]['name']
contact_email = contacts['contacts'][0].get('email', 'customer@example.com')

print(f"✅ Customer: {contact_name}")

# Step 2: Get templates (optional - can skip if OAuth scope missing)
try:
    themes = xero_get_branding_themes(business_id=BUSINESS_ID)
    template_name = themes['branding_themes'][0]['name']
    print(f"✅ Using template: {template_name}")
except:
    template_name = "Standard Invoice"  # Fallback
    print(f"⚠️  Using default template: {template_name}")

# Step 3: Create quote
quote = xero_create_quote(
    business_id=BUSINESS_ID,
    contact_id=contact_id,
    line_items=[
        {
            "description": "Business Cards - 1000qty, 350GSM",
            "quantity": 1,
            "unit_amount": 150.00,
            "account_code": "200"
        },
        {
            "description": "Letterhead - 500 sheets",
            "quantity": 1,
            "unit_amount": 85.00,
            "account_code": "200"
        }
    ],
    template_name=template_name,
    title="Professional Printing Services Quote",
    expiry_date="2025-12-31",
    summary="Thank you for your interest in our services."
)

quote_id = quote['quote_id']
quote_number = quote['quote_number']
quote_total = quote['total']

print(f"✅ Quote created: {quote_number} (${quote_total:.2f})")

# Step 4: Get quote details with PDF URL
quote_details = xero_get_quote_by_id(business_id=BUSINESS_ID, quote_id=quote_id)
pdf_url = quote_details.get('pdf_url', 'N/A')

print(f"✅ Quote details retrieved, PDF URL: {pdf_url[:50]}...")

# Step 5: Create draft email with quote info
email = outlook_send_email(
    to=[contact_email],
    subject=f"Quote {quote_number} - Professional Printing Services",
    body=f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #2c5aa0;">Your Printing Services Quote</h2>
        <p>Dear {contact_name},</p>
        <p>Please find your quote details below:</p>
        <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0;">
            <p><strong>Quote Number:</strong> {quote_number}</p>
            <p><strong>Total:</strong> ${quote_total:.2f}</p>
            <p><strong>Valid Until:</strong> December 31, 2025</p>
        </div>
        <p>Best regards,<br><strong>InHouse Print Team</strong></p>
    </body>
    </html>
    """,
    body_type='html'
)

print(f"✅ Draft email created: {email['draft_id']}")
print(f"⚠️  Email saved to Outlook Drafts - user must send manually")
```

═══════════════════════════════════════════════════════════════════════════════
⚠️ IMPORTANT NOTES
═══════════════════════════════════════════════════════════════════════════════

1. OAuth Scopes Required:
   • xero_get_branding_themes: Requires 'accounting.settings.read' scope
   • If missing, use template_name parameter instead of fetching themes
   
2. Email Behavior:
   • outlook_send_email creates DRAFTS only - does NOT send automatically
   • User must open Outlook and manually send from Drafts folder
   • This is intentional to prevent accidental sends
   
3. PDF Attachments:
   • Xero PDF URLs require authentication
   • PDFs must be downloaded and base64 encoded for email attachments
   • Alternative: Include quote link instead of PDF attachment
   
4. Line Item Account Codes:
   • "200" = Sales/Revenue account (standard for quotes)
   • Check your Xero chart of accounts for correct codes
   
5. Quote Status:
   • Created quotes start as "DRAFT" status
   • Can be converted to invoice or sent to customer via Xero UI

═══════════════════════════════════════════════════════════════════════════════
📚 TOOL REFERENCE
═══════════════════════════════════════════════════════════════════════════════

• xero_get_contacts(business_id, search, limit)
• xero_get_contact_by_id(business_id, contact_id)
• xero_get_branding_themes(business_id)
• xero_create_quote(business_id, contact_id, line_items, template_name, ...)
• xero_get_quote_by_id(business_id, quote_id)
• outlook_send_email(to, subject, body, body_type, attachments)

For complete parameter details, see:
- tools/schemas/xero_tools.json
- tools/schemas/xero_quotes_tools.json
- tools/implementations/microsoft_outlook_tools.py

═══════════════════════════════════════════════════════════════════════════════
