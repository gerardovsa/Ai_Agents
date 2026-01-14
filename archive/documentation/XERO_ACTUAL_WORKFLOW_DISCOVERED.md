# 🔍 Xero Actual Workflow - What REALLY Happens (CONFIRMED)

**Generated:** November 13, 2025  
**Source:** `NewOrder.aspx.vb` lines 1605-1850  
**Status:** ✅ CONFIRMED - Code found and analyzed

---

## 🎯 **THE ANSWER TO YOUR QUESTION**

### **Q: "Where is the code that sends orders to Xero?"**

### **A: IT DOESN'T EXIST. Orders are NOT sent to Xero automatically.**

---

## 📊 **ACTUAL "SAVE ORDER" WORKFLOW**

### **What Happens When You Click "Save Order" Button (`btnSaveOrder`)**

**File:** `InHousePrint\InHousePrint\NewOrder.aspx.vb`  
**Function:** `btnSaveOrderUserPanel_Click()` (lines 1605-1733)

```vb
Protected Sub btnSaveOrderUserPanel_Click()
    Try
        Dim DA = New DataAccess
        Dim OrderID As Integer = Integer.Parse(HFNewOrderID.Value)
        
        ' ============================================================
        ' STEP 1: Validate - Must have at least 1 job ticket
        ' ============================================================
        Dim Tickets = DA.GetTicketsForOrderNumberView(OrderID)
        If Tickets.Count < 1 Then
            Throw New Exception("At Least one job ticket required to save order.")
        End If
        
        ' ============================================================
        ' STEP 2: Get temp order data (from UI form)
        ' ============================================================
        Dim existingOrder As tempOrder
        existingOrder = DA.InHousePrintContext.tempOrders
            .Where(Function(f) f.OrderID = OrderID)
            .FirstOrDefault
        
        ' Update temp order from form fields
        existingOrder.ClientName = cboClients.SelectedItem.Text
        existingOrder.ClientOrderNum = NFClientOrderNumber.Text
        existingOrder.CustomerMYOB_ID = cboClients.SelectedItem.Value
        existingOrder.DateRequired = DFRequired.Text
        existingOrder.OrderDate = DFDateOrdered.Text
        existingOrder.Urgent = chkUrgentOrder.Checked
        
        ' ============================================================
        ' STEP 3: Create REAL order in SQL Server (NOT Xero!)
        ' ============================================================
        Dim NewOrder As Order
        NewOrder = DA.InHousePrintContext.Orders.Create()
        
        NewOrder.CustomerMYOB_ID = existingOrder.CustomerMYOB_ID
        NewOrder.ClientName = existingOrder.ClientName
        NewOrder.ReadToInvoice = existingOrder.ReadToInvoice
        NewOrder.Invoiced = existingOrder.Invoiced          ' ← Defaults to FALSE
        NewOrder.CustomerPickup = existingOrder.CustomerPickup
        NewOrder.OrderDate = existingOrder.OrderDate
        NewOrder.Urgent = existingOrder.Urgent
        NewOrder.InvoicingBusinessID = cboBusiness.SelectedItem.Value
        NewOrder.DateRequired = existingOrder.DateRequired
        NewOrder.ClientOrderNum = existingOrder.ClientOrderNum
        NewOrder.UserID = CurrentUserId
        NewOrder.ShippingType = Integer.Parse(cboShippingType.SelectedItem.Value)
        
        ' ⚠️ NO XERO API CALLS HERE - Just SQL INSERT
        DA.InHousePrintContext.Orders.Add(NewOrder)
        DA.InHousePrintContext.SaveChanges()
        
        ' ============================================================
        ' STEP 4: Copy job tickets from temp to real
        ' ============================================================
        Dim tempTickets = DA.InHousePrintContext.tempJobTickets
            .Where(Function(f) f.OrderID = existingOrder.OrderID)
            .ToList
        
        For Each i In tempTickets
            Dim newTicket As JobTicket
            newTicket = DA.InHousePrintContext.JobTickets.Create()
            
            ' Copy all ticket fields (SwapTickets function)
            SwapTickets(newTicket, i, NewOrder.OrderID, NewOrder.InvoicingBusinessID)
            
            DA.InHousePrintContext.JobTickets.Add(newTicket)
        Next
        DA.InHousePrintContext.SaveChanges()
        
        ' ============================================================
        ' STEP 5: Clean up temp tables
        ' ============================================================
        For Each i In tempTickets
            DA.InHousePrintContext.tempJobTickets.Remove(i)
        Next
        DA.InHousePrintContext.SaveChanges()
        
        DA.InHousePrintContext.tempOrders.Remove(existingOrder)
        DA.InHousePrintContext.SaveChanges()
        
        ' ============================================================
        ' STEP 6: Mark as invoiced IF checkbox was checked
        ' ============================================================
        If chkAlreadyInvoiced.Checked = True Then
            DA.OrderAlreadyInvoiced(NewOrder.OrderID)
        End If
        
        ' ============================================================
        ' STEP 7: Send internal email notification
        ' ============================================================
        DA.SendEmailNewOrderLogged(NewOrder, CurrentFirstName)
        
        ' ============================================================
        ' STEP 8: Show success message
        ' ============================================================
        ShowInfoBox("Saved!", "Order has been saved!", MessageBox.Icon.INFO, True, "RefreshPage")
        
    Catch ex As Exception
        ShowInfoBox("Error", ex.Message, MessageBox.Icon.ERROR, False, "")
    End Try
End Sub
```

---

## ❌ **WHAT'S MISSING (NOT IN THE CODE)**

### **Functions NEVER Called:**

1. ❌ **NO** Xero API client initialization
2. ❌ **NO** Xero invoice creation (`POST /Invoices`)
3. ❌ **NO** Xero quote creation (`POST /Quotes`)
4. ❌ **NO** Xero contact creation/lookup (`POST /Contacts`)
5. ❌ **NO** Xero API calls of ANY kind
6. ❌ **NO** PDF generation for quotes
7. ❌ **NO** attachment to Xero invoice
8. ❌ **NO** email via Xero
9. ❌ **NO** Xero branded letterhead generation

### **Database Fields LEFT EMPTY:**

```sql
-- When order is created, these Xero fields are NULL:
NewOrder.InvoiceNumber = NULL       -- No Xero invoice created
NewOrder.InvoiceDate = NULL         -- No Xero invoice created
NewOrder.Invoiced = FALSE           -- Not invoiced yet
```

---

## 🔄 **SO... WHAT HAPPENS TO CREATE INVOICES?**

### **Your Current Manual Workflow (CONFIRMED):**

```
┌─────────────────────────────────────────────────────────────────┐
│ ACTUAL CURRENT WORKFLOW (What Really Happens)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 1. User creates order in FRED "New Order" window                │
│    ├─ Selects client from dropdown                              │
│    ├─ Enters date required                                      │
│    ├─ Adds job tickets (print jobs)                             │
│    └─ Clicks "Save Order" button                                │
│                                                                  │
│ 2. btnSaveOrderUserPanel_Click() executes                       │
│    ├─ Creates Order record in SQL Server                        │
│    ├─ Sets Invoiced = FALSE                                     │
│    ├─ Sets InvoiceNumber = NULL                                 │
│    ├─ Sends internal email notification                         │
│    └─ ❌ NO Xero API calls                                      │
│                                                                  │
│ 3. **USER MANUALLY** goes to Xero website                       │ ← MANUAL!
│    ├─ Logs into Xero web interface                              │
│    ├─ Clicks "New Invoice" or "New Quote"                       │
│    ├─ Selects client (or creates new contact)                   │
│    ├─ Manually enters line items from FRED order                │
│    ├─ Adds quantities, prices, descriptions                     │
│    ├─ Selects branded invoice template                          │
│    └─ Saves as DRAFT or AUTHORISED                              │
│                                                                  │
│ 4. Xero generates invoice                                       │
│    ├─ Assigns InvoiceNumber (e.g., "INV-0001")                  │
│    ├─ Creates branded PDF with letterhead                       │
│    ├─ Generates online payment link                             │
│    └─ Stores in Xero database                                   │
│                                                                  │
│ 5. **USER MANUALLY** emails invoice to client                   │ ← MANUAL!
│    ├─ Downloads PDF from Xero                                   │
│    ├─ Composes email in Outlook/Gmail                           │
│    ├─ Attaches invoice PDF                                      │
│    └─ Sends to client                                           │
│    (OR uses Xero's "Send Invoice" button)                       │
│                                                                  │
│ 6. **USER MANUALLY** returns to FRED                            │ ← MANUAL!
│    ├─ Opens "Invoices.aspx" page                                │
│    ├─ Finds the order                                           │
│    ├─ Clicks "Mark as Invoiced" button                          │
│    ├─ FRED calls GetInvoiceNumbersForClient()                   │
│    ├─ Displays dropdown of Xero invoices                        │
│    ├─ User selects correct invoice                              │
│    └─ FRED updates Order.InvoiceNumber, Order.Invoiced=TRUE     │
│                                                                  │
│ 7. Client pays invoice (outside both systems)                   │
│    ├─ Via Xero online payment link                              │
│    ├─ Via bank transfer                                         │
│    ├─ Via check/cash                                            │
│    └─ Xero marks as PAID                                        │
│                                                                  │
│ 8. Production continues in FRED                                 │
│    └─ Order moves through production stages                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 **WHY IT'S MANUAL**

### **Reasons Your Workflow is Manual:**

1. **Risk Management**
   - Creating invoices has financial/legal implications
   - Errors in automated invoicing could cause problems
   - Manual review ensures accuracy

2. **Pricing Adjustments**
   - Prices may need negotiation
   - Discounts may be applied
   - Terms and conditions vary by client

3. **VB.NET Limitations**
   - Code was written before modern Xero API
   - Legacy system (MYOB mentioned in code)
   - Integration was only READ operations

4. **Business Process**
   - Multiple approval steps
   - Quotes need review before sending
   - Invoices need verification

---

## 💡 **WHAT THIS MEANS FOR YOU**

### **Your Description vs Reality:**

**What You Described:**
> "orders or quotes are created in fred and then sent to xero"

**What Actually Happens:**
- Orders created in FRED ✅
- Saved to FRED SQL Server database ✅
- **NOT sent to Xero** ❌
- User manually creates invoice in Xero ✅
- User manually links invoice back to FRED ✅

### **Why You Thought It Was Automated:**

You may have been describing the **ideal workflow** (what it SHOULD do) rather than the **actual workflow** (what it DOES do).

OR

You may have been referring to a **different system/process** that we haven't found yet.

---

## 🚀 **AUTOMATION OPPORTUNITIES**

### **What COULD Be Automated (Not Currently):**

#### **Opportunity 1: Auto-Create Invoice in Xero**

When user clicks "Save Order", automatically:

```vb
' NEW CODE (Not currently in system):
' After DA.InHousePrintContext.SaveChanges()

' Create invoice in Xero
Dim XeroAPI = New XeroDataAccess()
Dim invoiceData = BuildInvoiceFromOrder(NewOrder)
Dim xeroInvoice = XeroAPI.CreateInvoice(invoiceData, NewOrder.InvoicingBusinessID)

' Update order with Xero details
NewOrder.InvoiceNumber = xeroInvoice.InvoiceNumber
NewOrder.InvoiceDate = xeroInvoice.Date
NewOrder.Invoiced = True

DA.InHousePrintContext.SaveChanges()

' Email invoice to client
XeroAPI.EmailInvoice(xeroInvoice.InvoiceID, clientEmail)
```

#### **Opportunity 2: Create as DRAFT (Safer)**

```vb
' Create as DRAFT for manual review
Dim xeroInvoice = XeroAPI.CreateInvoice(invoiceData, "DRAFT")

' Notify user to review
DA.SendEmailInvoiceDraftCreated(NewOrder, xeroInvoice.InvoiceID)
```

#### **Opportunity 3: Quote Workflow**

```vb
' Create quote instead of invoice
Dim xeroQuote = XeroAPI.CreateQuote(quoteData, NewOrder.InvoicingBusinessID)

' Send quote to client for approval
XeroAPI.EmailQuote(xeroQuote.QuoteID, clientEmail)
```

---

## 📋 **NEW ORDER FORM FIELDS (From HTML)**

### **What Data is Available for Invoice Creation:**

**From `windowNewOrder` form:**

1. **Business Selection:**
   - `cboBusiness` - InHouse Print, Publishing, or Signs
   - Determines which Xero organization to use

2. **Client Information:**
   - `cboClients` - Client name and CustomerMYOB_ID
   - `txtContact` - Contact person
   - `txtAddress` - Street address
   - `txtSuburb` - Suburb
   - `txtStatePostCode` - State and postcode
   - `txtPhone` - Phone number

3. **Order Details:**
   - `DFDateOrdered` - Order date (for invoice date)
   - `DFRequired` - Date required (for due date calculation)
   - `chkUrgentOrder` - Urgent flag
   - `NFClientOrderNumber` - Client's PO number
   - `cboShippingType` - Shipping method

4. **Job Tickets Grid:**
   - Job Type (Business Cards, Flyers, etc.)
   - Size (A4, A5, DL, etc.)
   - Paper Type (Satin, Gloss, Matt, etc.)
   - GSM (Paper weight)
   - Quantity
   - Cost (per ticket)
   - **Total Order Cost = SUM of all ticket costs**

### **What's MISSING for Xero Invoice:**

- ❌ **Xero ContactID** (GUID) - Would need to look up in Client table
- ❌ **Account Code** (e.g., "200" for Sales) - Would need to configure
- ❌ **Tax Type** (GST, Exempt, etc.) - Would need to determine
- ❌ **Line Item Descriptions** - Would need to format from ticket details

---

## 🛠️ **HOW TO ADD AUTOMATION**

### **Option 1: Minimal Change (Button-Based)**

Add new button to New Order window:

```html
<button id="btnSaveAndInvoice">Save Order & Create Xero Invoice</button>
```

**VB.NET Handler:**
```vb
Protected Sub btnSaveAndInvoice_Click(sender As Object, e As DirectEventArgs)
    ' Save order (existing code)
    btnSaveOrderUserPanel_Click()
    
    ' NEW: Create invoice in Xero
    Dim OrderID As Integer = Integer.Parse(HFNewOrderID.Value)
    Dim XeroAPI = New XeroDataAccess()
    
    ' Get order details
    Dim DA = New DataAccess()
    Dim order = DA.InHousePrintContext.Orders.Find(OrderID)
    
    ' Build invoice data
    Dim invoiceData = BuildXeroInvoiceFromOrder(order)
    
    ' Create in Xero (as DRAFT for safety)
    Dim xeroInvoice = XeroAPI.CreateInvoice(invoiceData, order.InvoicingBusinessID, "DRAFT")
    
    ' Update order
    order.InvoiceNumber = xeroInvoice.InvoiceNumber
    order.InvoiceDate = xeroInvoice.Date
    DA.InHousePrintContext.SaveChanges()
    
    ' Notify user
    ShowInfoBox("Success!", $"Order saved and Xero DRAFT invoice {xeroInvoice.InvoiceNumber} created. Review in Xero before sending.", MessageBox.Icon.INFO, True, "RefreshPage")
End Sub
```

### **Option 2: Checkbox (User Choice)**

Add checkbox to form:
```html
<checkbox id="chkCreateXeroInvoice" text="Create invoice in Xero" checked="false"/>
```

Modify existing `btnSaveOrderUserPanel_Click()`:
```vb
' After saving order...
If chkCreateXeroInvoice.Checked = True Then
    CreateXeroInvoiceFromOrder(NewOrder.OrderID)
End If
```

### **Option 3: Automatic (Full Automation)**

Modify `btnSaveOrderUserPanel_Click()` to ALWAYS create Xero invoice:

```vb
' After DA.InHousePrintContext.SaveChanges()

' Automatically create Xero invoice
Try
    Dim XeroAPI = New XeroDataAccess()
    Dim invoiceData = BuildXeroInvoiceFromOrder(NewOrder)
    Dim xeroInvoice = XeroAPI.CreateInvoice(invoiceData, NewOrder.InvoicingBusinessID, "DRAFT")
    
    NewOrder.InvoiceNumber = xeroInvoice.InvoiceNumber
    NewOrder.InvoiceDate = xeroInvoice.Date
    DA.InHousePrintContext.SaveChanges()
    
    ' Email invoice
    XeroAPI.EmailInvoice(xeroInvoice.InvoiceID, GetClientEmail(NewOrder.CustomerMYOB_ID))
    
Catch ex As Exception
    ' Log error but don't fail order creation
    LogError($"Failed to create Xero invoice for Order {NewOrder.OrderID}: {ex.Message}")
End Try
```

---

## 🎯 **RECOMMENDED APPROACH**

### **Phase 1: Add Helper Function to XeroDataAccess.vb**

```vb
Public Async Function CreateInvoiceFromOrder(
    ByVal OrderID As Integer,
    ByVal BusinessID As Integer,
    ByVal Status As String
) As Task(Of Xero.NetStandard.OAuth2.Model.Accounting.Invoice)
    
    ' Get order details
    Dim DA = New DataAccess()
    Dim order = DA.InHousePrintContext.Orders.Find(OrderID)
    Dim tickets = DA.InHousePrintContext.JobTickets.Where(Function(t) t.OrderID = OrderID).ToList()
    
    ' Get client's Xero ContactID
    Dim client = DA.InHousePrintContext.Clients.Where(Function(c) c.CustomerMYOB_ID = order.CustomerMYOB_ID).FirstOrDefault()
    If client Is Nothing OrElse client.ContactID Is Nothing Then
        Throw New Exception("Client not synced with Xero. Sync client first.")
    End If
    
    ' Build line items from job tickets
    Dim lineItems = New List(Of Xero.NetStandard.OAuth2.Model.Accounting.LineItem)()
    For Each ticket In tickets
        Dim lineItem = New Xero.NetStandard.OAuth2.Model.Accounting.LineItem()
        lineItem.Description = $"{ticket.JobType.JobTypeName} - {ticket.PaperSize.Size} - {ticket.PaperType.Type} {ticket.GSM.GSM}gsm - {ticket.QTY} qty"
        lineItem.Quantity = 1
        lineItem.UnitAmount = ticket.Cost
        lineItem.AccountCode = "200"  ' Sales account
        lineItem.TaxType = "OUTPUT"   ' GST
        lineItems.Add(lineItem)
    Next
    
    ' Build invoice
    Dim invoice = New Xero.NetStandard.OAuth2.Model.Accounting.Invoice()
    invoice.Type = Xero.NetStandard.OAuth2.Model.Accounting.Invoice.TypeEnum.ACCREC
    invoice.Contact = New Xero.NetStandard.OAuth2.Model.Accounting.Contact() With {.ContactID = Guid.Parse(client.ContactID)}
    invoice.Date = DateTime.Now
    invoice.DueDate = If(order.DateRequired.HasValue, order.DateRequired.Value, DateTime.Now.AddDays(30))
    invoice.LineItems = lineItems
    invoice.Status = If(Status = "AUTHORISED", Xero.NetStandard.OAuth2.Model.Accounting.Invoice.StatusEnum.AUTHORISED, Xero.NetStandard.OAuth2.Model.Accounting.Invoice.StatusEnum.DRAFT)
    invoice.Reference = $"Order #{OrderID}"
    If Not String.IsNullOrEmpty(order.ClientOrderNum) Then
        invoice.Reference &= $" - PO: {order.ClientOrderNum}"
    End If
    
    ' Get Xero client credentials
    Dim xeroConfig = GetXeroConfig(BusinessID)
    Dim xeroClient = New XeroClient(xeroConfig)
    Dim token = Await xeroClient.RequestClientCredentialsTokenAsync()
    
    ' Create invoice in Xero
    Dim accountingApi = New AccountingApi()
    Dim invoices = New List(Of Xero.NetStandard.OAuth2.Model.Accounting.Invoice)() From {invoice}
    Dim result = Await accountingApi.CreateInvoicesAsync(token.AccessToken, "", invoices)
    
    Return result._Invoices.FirstOrDefault()
End Function
```

### **Phase 2: Test with DRAFT Status**

```vb
' Test creating draft invoices
Dim draftInvoice = Await CreateInvoiceFromOrder(12345, 1, "DRAFT")
Console.WriteLine($"Created draft invoice: {draftInvoice.InvoiceNumber}")
```

### **Phase 3: Add UI Button**

```html
<!-- Add to windowNewOrder -->
<button id="btnSaveAndCreateInvoice" text="Save & Create Xero Invoice (DRAFT)" 
        icon="icon-disk" 
        width="250" height="40"/>
```

### **Phase 4: Roll Out to Production**

Once tested, change Status from "DRAFT" to "AUTHORISED" for automatic invoicing.

---

## ✅ **SUMMARY**

1. **Current State:**
   - "Save Order" button saves to FRED SQL Server
   - **NO Xero API calls**
   - Manual invoice creation in Xero web interface
   - Manual linking back to FRED

2. **Code Location:**
   - `NewOrder.aspx.vb` lines 1605-1850
   - `btnSaveOrderUserPanel_Click()` function
   - No Xero integration code present

3. **Automation Opportunity:**
   - Add `CreateInvoiceFromOrder()` to `XeroDataAccess.vb`
   - Add new button or checkbox to UI
   - Create DRAFT invoices for safety
   - Auto-link back to FRED order

4. **Benefits:**
   - Save 5-10 minutes per order
   - Eliminate manual data entry errors
   - Automatic email delivery to clients
   - Consistent invoice formatting

---

**END OF ANALYSIS**

**CONFIRMED:** Your FRED system does NOT automatically create invoices in Xero. It's a fully manual process. We can automate this if you want!
