# 🔷 Xero Quotes System - Comprehensive Analysis & Implementation Plan

**Generated:** January 3, 2026  
**Purpose:** Create Quote Builder in Xero Module with Job Ticket Integration

---

## 📊 **CURRENT STATE ANALYSIS**

### **✅ What Already Exists:**

#### **1. Backend Xero Quote Tools** (`tools/implementations/xero_quotes.py`)
```python
# 5 Complete Functions Available:
- xero_create_quote()       # Create new quote with branding
- xero_list_quotes()        # List/filter 70,000+ quotes
- xero_get_quote_by_id()    # Get specific quote details
- xero_update_quote()       # Update existing quote
- xero_get_branding_themes() # List templates/logos
```

#### **2. Xero API Quote Structure:**
```json
{
  "QuoteID": "guid-here",
  "QuoteNumber": "QU-0001",
  "Status": "DRAFT|SENT|DECLINED|ACCEPTED|INVOICED",
  "Contact": {
    "ContactID": "contact-guid",
    "Name": "Customer Name"
  },
  "LineItems": [
    {
      "Description": "Business Cards - 1000qty, 350GSM",
      "Quantity": 1,
      "UnitAmount": 150.00,
      "AccountCode": "200",
      "LineAmount": 150.00,
      "TaxType": "OUTPUT",
      "TaxAmount": 15.00
    }
  ],
  "Date": "2026-01-03",
  "ExpiryDate": "2026-02-03",
  "SubTotal": 150.00,
  "TotalTax": 15.00,
  "Total": 165.00,
  "BrandingThemeID": "guid-here",
  "Title": "Printing Quote",
  "Summary": "Quote for business card printing",
  "Terms": "Payment due within 30 days",
  "Reference": "Order #12345",
  "UpdatedDateUTC": "2026-01-03T10:30:00Z"
}
```

#### **3. Quote Calculator System** (`UI/modules_external/quote-calculator/`)
- 80+ quote calculation tools
- 5 domains: Digital_Printing, Large_Format, Offset_Printing, Finishing, Misc
- Calculates costs for:
  - Business cards, flyers, brochures
  - Banners, signage
  - Finishing (laminating, folding, binding)

#### **4. Existing FRED Workflow** (In_House_SQL/InHousePrint)
```vb
' Current Manual Process:
1. Create Order in FRED → Saves to SQL Server
2. Add Job Tickets → Line items with pricing
3. MANUALLY create invoice in Xero website
4. MANUALLY link invoice back to FRED order
```

---

## 🔄 **QUOTE → JOB TICKET → PRODUCTION WORKFLOW**

### **Discovered from Documentation:**

```
┌──────────────────────────────────────────────────────────────┐
│ IDEAL AUTOMATED WORKFLOW (Not Currently Implemented)        │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ 1. Create Quote in Xero Module                               │
│    ├─ Select customer                                        │
│    ├─ Add line items from Quote Calculator                  │
│    ├─ Apply branding theme                                   │
│    └─ Save as DRAFT quote in Xero                            │
│                                                               │
│ 2. Send Quote to Customer                                    │
│    ├─ Xero generates branded PDF                             │
│    ├─ Email sent via Xero                                    │
│    └─ Customer reviews quote                                 │
│                                                               │
│ 3. Customer Accepts Quote                                    │
│    ├─ Update quote status to ACCEPTED                        │
│    └─ Trigger conversion workflow                            │
│                                                               │
│ 4. Convert Quote → Invoice                                   │
│    ├─ Create invoice from quote line items                   │
│    ├─ Set status to AUTHORISED or DRAFT                      │
│    └─ Store invoice ID in database                           │
│                                                               │
│ 5. Convert Quote → Production Order (FRED)                   │
│    ├─ Create Order record in SQL Server                      │
│    ├─ Convert line items → Job Tickets                       │
│    ├─ Link invoice number to order                           │
│    ├─ Set production priority                                │
│    └─ Notify production team                                 │
│                                                               │
│ 6. Production Workflow                                       │
│    ├─ Job tickets appear in FRED dashboard                   │
│    ├─ Operators claim tickets                                │
│    ├─ Mark progress (In Progress → Complete)                 │
│    └─ Update order status                                    │
│                                                               │
│ 7. Invoice & Payment                                         │
│    ├─ Invoice already created (Step 4)                       │
│    ├─ Customer pays                                          │
│    ├─ Xero tracks payment                                    │
│    └─ Order marked as paid                                   │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 🏗️ **IMPLEMENTATION PLAN**

### **Phase 1: Xero Module - Create Quote UI** (Priority 1)

#### **A. Add "Quotes" Tab to Xero Module**

**File:** `UI/modules_external/xero/xero.js`

```javascript
// Add to sub-tabs (line ~150):
{
    id: 'quotes',
    name: '📄 Quotes',
    icon: 'fa-file-invoice-dollar',
    description: 'Create and manage sales quotes'
}
```

#### **B. Create Quote List View**

```javascript
async loadQuotes() {
    const response = await fetch(`${this.API_BASE_URL}/api/xero/quotes?business_id=${this.currentBusiness}`);
    const data = await response.json();
    
    // Render Tabulator table with columns:
    // - Quote Number
    // - Customer Name  
    // - Date
    // - Status (DRAFT/SENT/ACCEPTED/DECLINED/INVOICED)
    // - Total Amount
    // - Actions (View, Edit, Convert to Invoice)
}
```

#### **C. Create "New Quote" Modal**

**Features:**
- Customer selector (from Xero contacts)
- Line item builder:
  - Product/Service description
  - Quantity
  - Unit price
  - Tax type
  - Account code
  - **Integration with Quote Calculator** (button to calculate costs)
- Quote details:
  - Quote date
  - Expiry date
  - Title
  - Summary
  - Terms & conditions
  - Reference number
- Branding theme selector
- Preview PDF button
- Save as DRAFT/SENT

#### **D. Quote Calculator Integration**

```javascript
// Button in line item: "Calculate Price"
async calculatePrice() {
    // Open modal with Quote Calculator options:
    // - Select product type (Business Cards, Flyers, etc.)
    // - Enter specifications (size, qty, paper stock)
    // - Calculate cost
    // - Auto-fill line item with calculated price
}
```

---

### **Phase 2: Backend Quote Routes** (Priority 1)

**File:** `UI/modules_external/xero/xero_routes.py`

```python
@cross_origin()
def xero_quotes():
    """Get or create quotes"""
    if request.method == 'POST':
        return create_quote()
    else:
        return get_quotes()

def get_quotes():
    """Get quotes from Xero with filtering"""
    try:
        business_id = int(request.args.get('business_id', 1))
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        status = request.args.get('status')
        contact_id = request.args.get('contact_id')
        
        client = XeroAPIClient(business_id)
        
        # Build where clause
        where_clauses = []
        if date_from:
            where_clauses.append(f'Date >= DateTime({date_from.replace("-", ", ")})')
        if date_to:
            where_clauses.append(f'Date <= DateTime({date_to.replace("-", ", ")})')
        if status:
            where_clauses.append(f'Status == "{status}"')
        if contact_id:
            where_clauses.append(f'Contact.ContactID == Guid("{contact_id}")')
        
        params = {}
        if where_clauses:
            params['where'] = ' AND '.join(where_clauses)
        
        data = client.make_request('GET', 'Quotes', params=params)
        quotes = data.get('Quotes', [])
        
        # Format response
        formatted_quotes = []
        for quote in quotes:
            formatted_quotes.append({
                'quote_id': quote.get('QuoteID'),
                'quote_number': quote.get('QuoteNumber'),
                'contact_name': quote.get('Contact', {}).get('Name'),
                'date': quote.get('Date'),
                'expiry_date': quote.get('ExpiryDate'),
                'status': quote.get('Status'),
                'sub_total': quote.get('SubTotal'),
                'total_tax': quote.get('TotalTax'),
                'total': quote.get('Total'),
                'title': quote.get('Title')
            })
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'quote_count': len(formatted_quotes),
            'quotes': formatted_quotes
        })
    
    except Exception as e:
        print(f"Error in get_quotes: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

def create_quote():
    """Create new quote in Xero"""
    try:
        data = request.json
        business_id = int(data.get('business_id', 1))
        
        client = XeroAPIClient(business_id)
        
        # Build quote data
        quote_data = {
            'Contact': {'ContactID': data['contact_id']},
            'LineItems': []
        }
        
        # Add line items
        for item in data.get('line_items', []):
            quote_data['LineItems'].append({
                'Description': item['description'],
                'Quantity': item['quantity'],
                'UnitAmount': item['unit_amount'],
                'AccountCode': item.get('account_code', '200'),
                'TaxType': item.get('tax_type', 'OUTPUT')
            })
        
        # Optional fields
        if data.get('date'):
            quote_data['Date'] = data['date']
        if data.get('expiry_date'):
            quote_data['ExpiryDate'] = data['expiry_date']
        if data.get('title'):
            quote_data['Title'] = data['title']
        if data.get('summary'):
            quote_data['Summary'] = data['summary']
        if data.get('terms'):
            quote_data['Terms'] = data['terms']
        if data.get('reference'):
            quote_data['Reference'] = data['reference']
        if data.get('branding_theme_id'):
            quote_data['BrandingThemeID'] = data['branding_theme_id']
        
        # Create quote via Xero API
        payload = {'Quotes': [quote_data]}
        result = client.make_request('PUT', 'Quotes', json=payload)
        
        quotes = result.get('Quotes', [])
        if not quotes:
            raise Exception("Failed to create quote")
        
        quote = quotes[0]
        
        return jsonify({
            'success': True,
            'business': BUSINESS_CONFIGS[business_id]['name'],
            'quote': {
                'quote_id': quote.get('QuoteID'),
                'quote_number': quote.get('QuoteNumber'),
                'status': quote.get('Status'),
                'total': quote.get('Total')
            }
        })
    
    except Exception as e:
        print(f"Error in create_quote: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

### **Phase 3: Quote → Invoice Conversion** (Priority 2)

```python
@cross_origin()
def xero_convert_quote_to_invoice():
    """Convert accepted quote to invoice"""
    try:
        data = request.json
        business_id = int(data.get('business_id', 1))
        quote_id = data['quote_id']
        
        client = XeroAPIClient(business_id)
        
        # Get quote details
        quote_response = client.make_request('GET', f'Quotes/{quote_id}')
        quote = quote_response.get('Quotes', [{}])[0]
        
        # Create invoice from quote
        invoice_data = {
            'Type': 'ACCREC',
            'Contact': quote.get('Contact'),
            'LineItems': quote.get('LineItems'),
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'DueDate': data.get('due_date'),
            'Status': data.get('status', 'DRAFT'),  # DRAFT or AUTHORISED
            'Reference': f"Quote: {quote.get('QuoteNumber')}",
            'BrandingThemeID': quote.get('BrandingThemeID')
        }
        
        # Create invoice
        inv_payload = {'Invoices': [invoice_data]}
        inv_result = client.make_request('POST', 'Invoices', json=inv_payload)
        
        invoice = inv_result.get('Invoices', [{}])[0]
        
        # Update quote status to INVOICED
        update_payload = {
            'Quotes': [{
                'QuoteID': quote_id,
                'Status': 'INVOICED'
            }]
        }
        client.make_request('POST', 'Quotes', json=update_payload)
        
        return jsonify({
            'success': True,
            'invoice': {
                'invoice_id': invoice.get('InvoiceID'),
                'invoice_number': invoice.get('InvoiceNumber'),
                'status': invoice.get('Status'),
                'total': invoice.get('Total')
            }
        })
    
    except Exception as e:
        print(f"Error in convert_quote_to_invoice: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

### **Phase 4: Quote → Production Order (FRED Integration)** (Priority 3)

**File:** `UI/modules_external/xero/xero_routes.py`

```python
@cross_origin()
def xero_convert_quote_to_production():
    """Convert quote to production order in FRED database"""
    try:
        from AI_infrastructure.shared.database_utils import execute_query
        
        data = request.json
        business_id = int(data.get('business_id', 1))
        quote_id = data['quote_id']
        
        client = XeroAPIClient(business_id)
        
        # Get quote details
        quote_response = client.make_request('GET', f'Quotes/{quote_id}')
        quote = quote_response.get('Quotes', [{}])[0]
        
        # Get contact details
        contact = quote.get('Contact', {})
        contact_name = contact.get('Name')
        
        # Create Order in FRED database
        order_sql = """
            INSERT INTO [InHousePrint].[dbo].[Orders] (
                CustomerMYOB_ID,
                ClientName,
                OrderDate,
                DateRequired,
                InvoicingBusinessID,
                Invoiced,
                ReadToInvoice,
                InvoiceNumber,
                InvoiceDate,
                UserID,
                Urgent
            ) VALUES (
                %s, %s, GETDATE(), %s, %s, 0, 1, NULL, NULL, %s, 0
            );
            SELECT SCOPE_IDENTITY() AS OrderID;
        """
        
        order_result = execute_query(
            order_sql,
            (
                contact.get('ContactID'),
                contact_name,
                data.get('date_required'),
                business_id,
                data.get('user_id', 1)
            ),
            fetch_mode='one'
        )
        
        order_id = order_result[0]
        
        # Create Job Tickets from line items
        for idx, item in enumerate(quote.get('LineItems', [])):
            ticket_sql = """
                INSERT INTO [InHousePrint].[dbo].[JobTickets] (
                    OrderID,
                    TicketNumber,
                    Description,
                    Quantity,
                    UnitPrice,
                    TotalPrice,
                    Status,
                    Priority,
                    BusinessID
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, 'Pending', 'Normal', %s
                )
            """
            
            execute_query(
                ticket_sql,
                (
                    order_id,
                    idx + 1,
                    item.get('Description'),
                    item.get('Quantity'),
                    item.get('UnitAmount'),
                    item.get('LineAmount'),
                    business_id
                )
            )
        
        return jsonify({
            'success': True,
            'order': {
                'order_id': order_id,
                'customer': contact_name,
                'ticket_count': len(quote.get('LineItems', [])),
                'total': quote.get('Total')
            }
        })
    
    except Exception as e:
        print(f"Error in convert_quote_to_production: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

## 🎯 **UI MOCKUP - Create Quote Modal**

```html
<div class="xero-modal-overlay" id="create-quote-modal">
    <div class="xero-modal-content" style="max-width: 900px;">
        <!-- Header -->
        <div class="modal-header">
            <h2>📄 Create New Quote</h2>
            <button id="close-modal">✕</button>
        </div>
        
        <!-- Quote Form -->
        <form id="quote-form">
            <!-- Customer Selection -->
            <div class="form-section">
                <label>Customer *</label>
                <select id="contact-selector">
                    <option value="">Select customer...</option>
                    <!-- Populated from Xero contacts -->
                </select>
                <button type="button" id="add-new-customer">+ New Customer</button>
            </div>
            
            <!-- Quote Details -->
            <div class="form-row">
                <div>
                    <label>Quote Date</label>
                    <input type="date" id="quote-date" value="2026-01-03">
                </div>
                <div>
                    <label>Expiry Date</label>
                    <input type="date" id="expiry-date">
                </div>
            </div>
            
            <div class="form-row">
                <div>
                    <label>Quote Title</label>
                    <input type="text" id="quote-title" placeholder="e.g., Printing Quote">
                </div>
                <div>
                    <label>Branding Theme</label>
                    <select id="branding-theme">
                        <!-- Populated from xero_get_branding_themes -->
                    </select>
                </div>
            </div>
            
            <!-- Line Items -->
            <div class="form-section">
                <div class="section-header">
                    <h3>Line Items</h3>
                    <button type="button" id="add-line-item">+ Add Item</button>
                </div>
                
                <table id="line-items-table">
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th>Qty</th>
                            <th>Unit Price</th>
                            <th>Tax</th>
                            <th>Total</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="line-items-body">
                        <!-- Dynamic rows -->
                        <tr>
                            <td>
                                <input type="text" placeholder="Product/Service description">
                                <button type="button" class="calculate-price">🧮 Calculate</button>
                            </td>
                            <td><input type="number" value="1"></td>
                            <td><input type="number" step="0.01" placeholder="0.00"></td>
                            <td>
                                <select>
                                    <option>GST</option>
                                    <option>No Tax</option>
                                </select>
                            </td>
                            <td class="calculated-total">$0.00</td>
                            <td>
                                <button type="button" class="remove-item">🗑️</button>
                            </td>
                        </tr>
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colspan="4" class="text-right"><strong>Subtotal:</strong></td>
                            <td id="subtotal">$0.00</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td colspan="4" class="text-right"><strong>Tax:</strong></td>
                            <td id="total-tax">$0.00</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td colspan="4" class="text-right"><strong>Total:</strong></td>
                            <td id="grand-total" style="font-size: 18px; color: var(--xero-primary);">$0.00</td>
                            <td></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
            
            <!-- Additional Details -->
            <details>
                <summary>📝 Additional Details</summary>
                <div>
                    <label>Summary</label>
                    <textarea id="quote-summary" rows="3"></textarea>
                    
                    <label>Terms & Conditions</label>
                    <textarea id="quote-terms" rows="3"></textarea>
                    
                    <label>Reference Number</label>
                    <input type="text" id="quote-reference">
                </div>
            </details>
            
            <!-- Actions -->
            <div class="modal-actions">
                <button type="button" id="cancel-btn">Cancel</button>
                <button type="button" id="preview-btn">👁️ Preview PDF</button>
                <button type="submit" id="save-draft-btn">💾 Save as Draft</button>
                <button type="button" id="send-btn">📧 Save & Send</button>
            </div>
        </form>
    </div>
</div>
```

---

## 📦 **DELIVERABLES**

### **Week 1: Core Quote UI**
- ✅ Add "Quotes" tab to Xero module
- ✅ Create quote list view (Tabulator table)
- ✅ Implement "Create Quote" modal
- ✅ Backend quote routes (GET, POST)
- ✅ Integration with existing Quote Calculator

### **Week 2: Quote Management**
- ✅ View quote details modal
- ✅ Edit existing quotes
- ✅ Update quote status (DRAFT → SENT → ACCEPTED)
- ✅ Email quote via Xero
- ✅ PDF preview functionality

### **Week 3: Conversions**
- ✅ Convert quote → invoice
- ✅ Convert quote → production order (FRED)
- ✅ Auto-create job tickets from line items
- ✅ Link invoice to production order

### **Week 4: Polish & Testing**
- ✅ Error handling & validation
- ✅ Loading states & animations
- ✅ Mobile responsiveness
- ✅ User testing & bug fixes

---

## 🚀 **NEXT STEPS**

1. **Implement Phase 1** - Create Quote UI in Xero module
2. **Add Backend Routes** - `/api/xero/quotes` endpoint
3. **Test with Real Data** - Pull existing quotes from Xero API
4. **Implement Conversions** - Quote → Invoice → Production Order

Would you like me to start implementing Phase 1 now?
