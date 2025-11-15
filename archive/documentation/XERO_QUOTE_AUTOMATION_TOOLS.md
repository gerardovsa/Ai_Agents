# 🚀 Xero Quote Automation - New Tools Required

**Purpose:** Enable AI agents to create quotes, download PDFs, and convert to invoices  
**Status:** Design Phase - Ready to Implement  
**Integration:** Works with existing calculator tools and Xero API

---

## 📋 **NEW TOOLS TO CREATE**

### **Category 1: Quote Management**

#### **Tool 1: `xero_create_quote`**

```python
def xero_create_quote(
    contact_id: str,
    line_items: List[Dict],
    business_id: int = 1,
    reference: str = None,
    expiry_days: int = 30,
    status: str = "DRAFT"
) -> Dict:
    """
    Create a quote in Xero from calculated pricing
    
    Args:
        contact_id: Xero Contact GUID
        line_items: List of quote line items with descriptions, quantities, prices
        business_id: 1=Print, 2=Publishing, 3=Signs
        reference: Client PO number or internal reference
        expiry_days: Days until quote expires (default 30)
        status: "DRAFT" or "SENT" (default DRAFT for safety)
    
    Returns:
        {
            "success": True,
            "quote_id": "guid",
            "quote_number": "QU-0001",
            "total": 487.50,
            "expiry_date": "2025-12-15",
            "online_quote_url": "https://go.xero.com/...",
            "pdf_url": "https://api.xero.com/api.xro/2.0/Quotes/{quoteID}/pdf"
        }
    
    Xero API:
        POST https://api.xero.com/api.xro/2.0/Quotes
        Body: {
            "Contact": {"ContactID": "..."},
            "Date": "2025-11-13",
            "ExpiryDate": "2025-12-13",
            "LineItems": [...],
            "Status": "DRAFT",
            "Reference": "Quote for 5,000 business cards"
        }
    
    Use Case:
        User: "Create quote for ACME Corp - 5,000 business cards"
        AI: 
            1. calculate_business_cards(5000, ...)
            2. xero_get_contacts(name="ACME Corp")
            3. xero_create_quote(contact_id, line_items from calc)
            4. Returns QuoteID for next steps
    """
```

#### **Tool 2: `xero_get_quote_pdf`**

```python
def xero_get_quote_pdf(
    quote_id: str,
    business_id: int = 1,
    save_path: str = None
) -> bytes:
    """
    Download branded quote PDF from Xero
    
    Xero automatically generates professional PDFs with:
    - Business letterhead
    - Company logo
    - Quote details table
    - Terms and conditions
    - Payment instructions
    
    Args:
        quote_id: Xero Quote GUID
        business_id: 1=Print, 2=Publishing, 3=Signs
        save_path: Optional local path to save PDF
    
    Returns:
        PDF file bytes
    
    Xero API:
        GET https://api.xero.com/api.xro/2.0/Quotes/{quoteID}/pdf
        Accept: application/pdf
    
    Use Case:
        AI: 
            1. xero_create_quote() → Returns quote_id
            2. xero_get_quote_pdf(quote_id) → Returns PDF bytes
            3. onedrive_upload_file(pdf_bytes) → Upload to cloud
            4. Show link to user
    """
```

#### **Tool 3: `xero_convert_quote_to_invoice`**

```python
def xero_convert_quote_to_invoice(
    quote_id: str,
    business_id: int = 1,
    status: str = "DRAFT"
) -> Dict:
    """
    Convert approved Xero quote to invoice
    
    When client approves quote, convert it to an invoice.
    Preserves all line items, pricing, and terms.
    
    Args:
        quote_id: Xero Quote GUID
        business_id: 1=Print, 2=Publishing, 3=Signs
        status: "DRAFT" or "AUTHORISED" (default DRAFT)
    
    Returns:
        {
            "success": True,
            "invoice_id": "guid",
            "invoice_number": "INV-0001",
            "quote_number": "QU-0001",
            "total": 487.50,
            "status": "DRAFT",
            "online_invoice_url": "https://go.xero.com/..."
        }
    
    Xero API:
        1. GET /Quotes/{quoteID} to fetch quote details
        2. POST /Invoices with quote data
        3. UPDATE /Quotes/{quoteID} to mark as "ACCEPTED"
    
    Use Case:
        User: "Quote QU-0001 was approved"
        AI:
            1. xero_convert_quote_to_invoice(quote_id) → Invoice created
            2. fred_create_order(invoice_data) → Order created in FRED
            3. fred_link_xero_invoice(order_id, invoice_id) → Link them
    """
```

#### **Tool 4: `xero_email_quote`**

```python
def xero_email_quote(
    quote_id: str,
    business_id: int = 1,
    to_email: str = None,
    cc_emails: List[str] = None,
    message: str = None
) -> Dict:
    """
    Send quote email via Xero (uses branded template)
    
    Xero will:
    - Use business email template
    - Attach quote PDF
    - Include "Accept Quote" button (online acceptance)
    - Track when email opened
    
    Args:
        quote_id: Xero Quote GUID
        business_id: 1=Print, 2=Publishing, 3=Signs
        to_email: Recipient (if None, uses contact's email)
        cc_emails: CC recipients
        message: Custom message to include
    
    Returns:
        {
            "success": True,
            "sent_to": "client@acmecorp.com",
            "sent_at": "2025-11-13T15:00:00Z",
            "quote_url": "https://go.xero.com/..."
        }
    
    Xero API:
        POST https://api.xero.com/api.xro/2.0/Quotes/{quoteID}/Email
    
    Use Case:
        AI:
            1. xero_create_quote() → QU-0001
            2. xero_email_quote(quote_id, "client@acme.com")
            3. Client receives branded email with quote
    """
```

---

### **Category 2: FRED Integration**

#### **Tool 5: `fred_create_order`**

```python
def fred_create_order(
    client_name: str,
    client_myob_id: str,
    job_tickets: List[Dict],
    business_id: int = 1,
    date_required: str = None,
    urgent: bool = False,
    xero_quote_id: str = None,
    client_order_number: str = None
) -> Dict:
    """
    Create order in FRED database
    
    Mimics VB.NET NewOrder.aspx.vb btnSaveOrderUserPanel_Click()
    
    Args:
        client_name: Client name from Xero
        client_myob_id: FRED client ID (lookup from Client table)
        job_tickets: List of print jobs with specifications
        business_id: 1=Print, 2=Publishing, 3=Signs
        date_required: Due date (ISO format)
        urgent: Rush order flag
        xero_quote_id: Link to Xero quote
        client_order_number: Client's PO number
    
    Returns:
        {
            "success": True,
            "order_id": 12345,
            "order_number": "ORD-12345",
            "total_cost": 487.50,
            "job_ticket_ids": [67890, 67891],
            "message": "Order created successfully"
        }
    
    Database Operations:
        1. INSERT INTO Orders (ClientName, CustomerMYOB_ID, OrderDate, ...)
        2. INSERT INTO JobTickets (OrderID, JobTypeID, QTY, Cost, ...)
        3. Send email notification to production team
    
    Use Case:
        User: "Create order in FRED for quote QU-0001"
        AI:
            1. xero_get_quote_by_id("QU-0001") → Get quote details
            2. fred_lookup_client("ACME Corp") → Get client_myob_id
            3. fred_create_order(client_name, client_myob_id, job_tickets)
            4. Returns OrderID for linking
    """
```

#### **Tool 6: `fred_link_xero_invoice`**

```python
def fred_link_xero_invoice(
    order_id: int,
    invoice_number: str,
    invoice_id: str,
    business_id: int = 1
) -> Dict:
    """
    Link Xero invoice to FRED order
    
    Mimics VB.NET Invoices.aspx.vb "Mark as Invoiced" function
    
    Args:
        order_id: FRED Order ID
        invoice_number: Xero invoice number (e.g., "INV-0001")
        invoice_id: Xero invoice GUID
        business_id: 1=Print, 2=Publishing, 3=Signs
    
    Returns:
        {
            "success": True,
            "order_id": 12345,
            "invoice_number": "INV-0001",
            "invoice_date": "2025-11-13",
            "message": "Order marked as invoiced"
        }
    
    Database Operations:
        UPDATE Orders
        SET InvoiceNumber = 'INV-0001',
            InvoiceDate = '2025-11-13',
            Invoiced = 1,
            InvoicingBusinessID = 1
        WHERE OrderID = 12345
    
    Use Case:
        AI:
            1. fred_create_order() → Returns order_id
            2. xero_convert_quote_to_invoice() → Returns invoice details
            3. fred_link_xero_invoice(order_id, invoice_number, invoice_id)
            4. Order now shows as invoiced in FRED
    """
```

#### **Tool 7: `fred_lookup_client`**

```python
def fred_lookup_client(
    client_name: str = None,
    contact_id: str = None
) -> Dict:
    """
    Find FRED client by name or Xero ContactID
    
    Args:
        client_name: Client name to search
        contact_id: Xero Contact GUID
    
    Returns:
        {
            "success": True,
            "client_id": 123,
            "client_myob_id": "C000123",
            "client_name": "ACME Corp",
            "contact_id": "xero-guid-here",
            "email": "client@acmecorp.com",
            "phone": "555-1234"
        }
    
    Database:
        SELECT * FROM Client
        WHERE Name LIKE '%ACME%'
        OR ContactID = 'xero-guid'
    
    Use Case:
        AI needs to create order but only has client name from quote
        fred_lookup_client("ACME Corp") → Get client_myob_id for order
    """
```

---

### **Category 3: OneDrive Integration**

#### **Tool 8: `onedrive_upload_quote_pdf`**

```python
def onedrive_upload_quote_pdf(
    pdf_bytes: bytes,
    quote_number: str,
    client_name: str,
    folder_path: str = "/Quotes"
) -> Dict:
    """
    Upload quote PDF to OneDrive with organized naming
    
    Args:
        pdf_bytes: PDF file content
        quote_number: Xero quote number (e.g., "QU-0001")
        client_name: Client name for filename
        folder_path: OneDrive folder (default: /Quotes)
    
    Returns:
        {
            "success": True,
            "file_id": "onedrive-file-id",
            "file_name": "ACME_Corp_Quote_QU-0001_2025-11-13.pdf",
            "web_url": "https://1drv.ms/b/s!Abc123...",
            "download_url": "https://...",
            "folder_path": "/Quotes"
        }
    
    OneDrive API:
        PUT /drive/root:/Quotes/ACME_Corp_Quote_QU-0001.pdf:/content
    
    Use Case:
        AI:
            1. xero_get_quote_pdf(quote_id) → PDF bytes
            2. onedrive_upload_quote_pdf(pdf_bytes, "QU-0001", "ACME Corp")
            3. Returns shareable link
            4. outlook_create_draft(attachments=[onedrive_link])
    """
```

---

## 🔄 **COMPLETE AI AGENT WORKFLOW**

### **Smart Tool: `smart_create_and_send_quote`**

```python
def smart_create_and_send_quote(
    client_name: str,
    product_type: str,
    quantity: int,
    specifications: Dict,
    send_method: str = "draft"  # "draft", "send", or "both"
) -> Dict:
    """
    SMART TOOL: Complete quote workflow from calculation to delivery
    
    This is a "smart tool" that orchestrates multiple sub-tools sequentially.
    AI creates step-wise instructions, backend executes them.
    
    Workflow:
        1. Check if client exists in Xero
        2. If not, create client
        3. Calculate quote using calculator tools
        4. Create quote in Xero
        5. Download quote PDF
        6. Upload to OneDrive
        7. Create email draft OR send directly
        8. Return results with links
    
    Args:
        client_name: "ACME Corp"
        product_type: "business_cards", "flyers", "booklets", etc.
        quantity: 5000
        specifications: {
            "stock": "350GSM Satin",
            "sides": "double_sided",
            "size": "90x55mm"
        }
        send_method: 
            - "draft": Create Outlook draft for review
            - "send": Send quote immediately via Xero
            - "both": Create draft AND send via Xero
    
    Returns:
        {
            "success": True,
            "steps_completed": 8,
            "quote": {
                "quote_number": "QU-0001",
                "quote_id": "guid",
                "total": 487.50,
                "client": "ACME Corp",
                "client_created": False  # True if new client
            },
            "files": {
                "onedrive_url": "https://1drv.ms/...",
                "xero_pdf_url": "https://api.xero.com/..."
            },
            "email": {
                "draft_id": "outlook-draft-id" or null,
                "sent": True or False,
                "recipient": "client@acmecorp.com"
            },
            "next_actions": [
                "Review email draft in Outlook",
                "Wait for client approval",
                "Convert to invoice when approved"
            ]
        }
    
    Example Usage:
        User: "Create quote for ACME Corp - 5,000 business cards, 350GSM gloss, double-sided"
        
        AI interprets:
        - client_name: "ACME Corp"
        - product_type: "business_cards"
        - quantity: 5000
        - specifications: {"stock": "350GSM Satin", "sides": "double_sided"}
        - send_method: "draft" (default - let user review)
        
        AI calls: create_and_send_quote(...)
        
        Backend executes:
        ✅ Step 1: Check client → Found existing
        ✅ Step 2: Calculate quote → $487.50
        ✅ Step 3: Create Xero quote → QU-0001
        ✅ Step 4: Download PDF → 245KB
        ✅ Step 5: Upload to OneDrive → Success
        ✅ Step 6: Create Outlook draft → Ready to review
        
        AI returns: "Quote QU-0001 created for $487.50. Email draft ready: [Open Draft]"
    """
```

---

## 📊 **IMPLEMENTATION PRIORITY**

### **Phase 1: Core Quote Tools (Week 1)**
1. ✅ `xero_create_quote` - Create quotes
2. ✅ `xero_get_quote_pdf` - Download PDFs
3. ✅ `onedrive_upload_quote_pdf` - Store in cloud
4. ✅ `outlook_create_draft` - Email preparation (already exists!)

**Result:** AI can create quotes and prepare emails

### **Phase 2: Quote Management (Week 2)**
5. ✅ `xero_email_quote` - Send via Xero
6. ✅ `xero_convert_quote_to_invoice` - Convert approved quotes
7. ✅ `fred_lookup_client` - Find FRED clients

**Result:** Complete quote lifecycle

### **Phase 3: FRED Integration (Week 3)**
8. ✅ `fred_create_order` - Create orders from quotes
9. ✅ `fred_link_xero_invoice` - Link invoices to orders

**Result:** Full automation FRED ↔ Xero

### **Phase 4: Smart Tool (Week 4)**
10. ✅ `create_and_send_quote` - Orchestrated workflow

**Result:** One-command quote creation

---

## 🎯 **USE CASES**

### **Use Case 1: New Client Quote**
```
User: "Create quote for new client XYZ Ltd - 10,000 flyers A5"

AI Flow:
1. xero_get_contacts("XYZ Ltd") → Not found
2. xero_create_contact("XYZ Ltd", email, phone) → Created
3. calculate_flyers(10000, "A5", ...) → $1,245.00
4. xero_create_quote(contact_id, line_items) → QU-0002
5. xero_get_quote_pdf(quote_id) → PDF bytes
6. onedrive_upload_quote_pdf(...) → OneDrive link
7. outlook_create_draft(...) → Email ready

Result: "Quote QU-0002 created for $1,245. [View PDF] [Send Email]"
```

### **Use Case 2: Existing Client Quote**
```
User: "Quote for ACME Corp - 2,500 perfect bound books, 200 pages, full color"

AI Flow:
1. xero_get_contacts("ACME Corp") → Found existing
2. calculate_perfect_bound_books(2500, 200, "full_color") → $8,750.00
3. xero_create_quote(contact_id, line_items) → QU-0003
4. xero_email_quote(quote_id, "client@acme.com") → Sent via Xero
5. onedrive_upload_quote_pdf(...) → Backup stored

Result: "Quote QU-0003 for $8,750 sent to client@acme.com. [View in Xero]"
```

### **Use Case 3: Quote Approval → Order**
```
User: "Client approved quote QU-0003, create order"

AI Flow:
1. xero_get_quote_by_id("QU-0003") → Get quote details
2. xero_convert_quote_to_invoice(quote_id, "DRAFT") → INV-0003
3. fred_lookup_client("ACME Corp") → Get client_myob_id
4. fred_create_order(client_myob_id, job_tickets from quote) → Order #12346
5. fred_link_xero_invoice(12346, "INV-0003", invoice_id) → Linked
6. fred_send_order_notification(12346) → Production team notified

Result: "Order #12346 created and sent to production. Invoice INV-0003 linked."
```

---

## 🔐 **SECURITY & VALIDATION**

### **Required Checks:**

1. **Client Validation:**
   - Email format validation
   - Duplicate client detection
   - Required fields present

2. **Quote Validation:**
   - Line items not empty
   - Prices > 0
   - Valid contact ID

3. **Authorization:**
   - User has permission to create quotes
   - Business ID matches user's business
   - Rate limiting on quote creation

4. **Error Handling:**
   - Xero API failures (network, auth)
   - OneDrive upload failures
   - FRED database errors
   - Rollback on partial failures

---

## 📁 **FILES TO CREATE**

### **Backend:**
1. `tools/schemas/xero_quote_tools.json` - Tool definitions
2. `tools/implementations/xero_quotes.py` - Quote management
3. `tools/implementations/fred_orders.py` - FRED order creation
4. `tools/implementations/smart_workflows.py` - Orchestrated tools

### **Database:**
1. Migration: Add `xero_quote_id` to FRED Orders table
2. Add quote tracking table (optional)

### **Testing:**
1. `test_xero_quotes.py` - Unit tests for quote tools
2. `test_fred_integration.py` - FRED order creation tests
3. `test_smart_workflow.py` - End-to-end workflow tests

---

## ✅ **BENEFITS**

1. **Time Savings:**
   - Manual process: 10-15 minutes per quote
   - Automated: 30 seconds
   - **Savings: 93% reduction in time**

2. **Error Reduction:**
   - No manual data entry errors
   - Consistent formatting
   - Auto-calculation eliminates pricing mistakes

3. **Better Customer Experience:**
   - Faster quote turnaround
   - Professional branded PDFs
   - Consistent communication

4. **Audit Trail:**
   - All quotes logged
   - Version control
   - Easy to track quote → order → invoice

---

**STATUS:** Ready to implement - All tools designed and mapped

**NEXT STEP:** Implement Phase 1 (Core Quote Tools) - Estimated 1 week
