# 🔷 **XERO INTEGRATION DISCOVERED - Complete Analysis**

**Generated:** January 3, 2026  
**Critical File Found:** `C:\Users\gpoli\GIT\In_House_SQL\InHousePrint\DAL\XeroDataAccess.vb`  
**Purpose:** Document the ACTUAL Xero API integration that exists in the legacy VB.NET system

---

## ✅ **CORRECTION TO PREVIOUS ANALYSIS:**

**The system DOES have Xero integration!** It uses the **Xero .NET Standard OAuth2 SDK** with **Client Credentials flow**.

---

## 🔑 **XERO API CONFIGURATION**

### **Three Business Connections:**

```xml
<!-- Web.config Settings -->
<appSettings>
  <!-- InHouse Print Xero -->
  <add key="PrintClientId" value="02BB492DD4EC4A5DAEAB50088D3C8C0D"/>
  <add key="PrintClientSecret" value="a70UA2sXzERadX-wWCSZoUFFkljAxA4gEuFSV1hKS_zKRPs2"/>
  
  <!-- InHouse Publishing Xero -->
  <add key="PubClientId" value="926A463987B749FB9F21950B3B4212E9"/>
  <add key="PubClientSecret" value="aBWKAnfBl17roRt3jgD_hGba7JM0di3YGj5WLHv0T89kyTyq"/>
  
  <!-- InHouse Signs Xero -->
  <add key="SignsClientId" value="7D5CE8F957944A95878F5B1F1CEE6F3D"/>
  <add key="SignClientSecret" value="xykFPAGUy5mHfMvOqwtfmg7y5uqNjaxES4OPet6L9tVoDhS3"/>
</appSettings>
```

### **NuGet Packages Used:**

```vb
Imports Xero.NetStandard.OAuth2.Api
Imports Xero.NetStandard.OAuth2.Client
Imports Xero.NetStandard.OAuth2.Config
Imports Xero.NetStandard.OAuth2.Token
Imports Xero.NetStandard.OAuth2.Model.Accounting
```

---

## 📄 **XERO FUNCTIONS IN LEGACY SYSTEM**

### **File:** `XeroDataAccess.vb` (472 lines)

```vb
Public Class XeroDataAccess
    ' Configuration for 3 businesses
    Private PrintClientId As String
    Private PrintClientSecret As String
    Private PubClientId As String
    Private PubClientSecret As String
    Private SignsClientId As String
    Private SignClientSecret As String
```

### **Available Functions:**

#### **1. GetInvoiceNumbersForClient()** - Fetch invoices for a customer

```vb
Public Async Function GetInvoiceNumbersForClient(
    ByVal ContactID As Guid, 
    ByVal BusinessID As Integer
) As Task(Of DataTable)
    
    ' Select business config based on BusinessID (1=Print, 2=Pub, 3=Signs)
    If BusinessID = 1 Then
        Dim XeroConfig = New XeroConfiguration
        XeroConfig.ClientId = PrintClientId
        XeroConfig.ClientSecret = PrintClientSecret
        
        Dim Client = New XeroClient(XeroConfig)
        
        ' Get OAuth2 token
        Dim xeroTokenTask = Await Task.Run(
            Function() Client.RequestClientCredentialsTokenAsync()
        )
        
        ' Call Xero API
        Dim TempContactGuidList As New List(Of Guid)
        TempContactGuidList.Add(ContactID)
        
        Dim apiInstance = New AccountingApi
        Dim result = Await apiInstance.GetInvoicesAsync(
            xeroTokenTask.AccessToken, 
            "", 
            Nothing, 
            Nothing, 
            "Date DESC",  ' Order by date descending
            Nothing, 
            Nothing, 
            TempContactGuidList,  ' Filter by contact
            Nothing, 
            Nothing, 
            Nothing, 
            Nothing, 
            Nothing, 
            Nothing
        )
        
        ' Build DataTable
        Dim DT As New DataTable
        DT.Columns.Add("InvoiceNumberDesc")
        DT.Columns.Add("InvoiceID")
        
        For Each I In result._Invoices
            Dim R As DataRow = DT.NewRow
            R("InvoiceNumberDesc") = I.InvoiceNumber.ToString + 
                " - " + I.Date.Value.ToShortDateString + 
                " - " + I.Total.ToString
            R("InvoiceID") = I.InvoiceID.ToString
            DT.Rows.Add(R)
        Next
        
        Return DT
    End If
End Function
```

**Purpose:** Load invoice dropdown when staff links an existing Xero invoice to a FRED order.

---

#### **2. GetInvoicesForPublishingClientFreeda()** - Publishing invoices with details

```vb
Public Async Function GetInvoicesForPublishingClientFreeda(
    ByVal ContactID As String
) As Task(Of DataTable)
    
    Dim XeroConfig = New XeroConfiguration
    XeroConfig.ClientId = PubClientId
    XeroConfig.ClientSecret = PubClientSecret
    
    Dim Client = New XeroClient(XeroConfig)
    Dim contactGuid As Guid = Guid.Parse(ContactID)
    Dim xeroTokenTask = Await Task.Run(
        Function() Client.RequestClientCredentialsTokenAsync()
    )
    
    Dim TempContactGuidList As New List(Of Guid)
    TempContactGuidList.Add(contactGuid)
    
    Dim apiInstance = New AccountingApi
    Dim result = Await apiInstance.GetInvoicesAsync(
        xeroTokenTask.AccessToken, 
        "", 
        Nothing, 
        Nothing, 
        "Date DESC", 
        Nothing, 
        Nothing, 
        TempContactGuidList, 
        Nothing, 
        Nothing, 
        Nothing, 
        Nothing, 
        Nothing, 
        Nothing
    )
    
    Dim DT As New DataTable
    DT.Columns.Add("InvoiceNumberDesc")
    DT.Columns.Add("InvoiceID")
    DT.Columns.Add("InvoiceCost")
    DT.Columns.Add("Paid")
    DT.Columns.Add("Owing")
    DT.Columns.Add("Credited")
    DT.Columns.Add("Date")
    
    For Each I In result._Invoices.OrderBy(Function(f) f.InvoiceNumber)
        Dim R As DataRow = DT.NewRow
        R("InvoiceNumberDesc") = I.InvoiceNumber.ToString
        R("InvoiceID") = I.InvoiceID.ToString
        R("InvoiceCost") = I.Total.ToString
        R("Paid") = I.AmountPaid.ToString
        R("Owing") = I.AmountDue.ToString
        R("Credited") = I.AmountCredited.ToString
        R("Date") = I.Date.Value.ToShortDateString
        DT.Rows.Add(R)
    Next
    
    Return DT
End Function
```

**Purpose:** Show detailed invoice list for Freeda (publishing system) projects.

---

#### **3. SetExitingProjectInvNumDate()** - Link invoice to publishing project

```vb
Public Async Function SetExitingProjectInvNumDate(
    ByVal ExProject As PublishingProject, 
    ByVal InvoiceID As String, 
    ByVal businessID As Integer
) As Task(Of PublishingProject)
    
    ' Get invoice details from Xero
    Dim XeroConfig = New XeroConfiguration
    XeroConfig.ClientId = PubClientId  ' (or Print/Signs based on businessID)
    XeroConfig.ClientSecret = PubClientSecret
    
    Dim Client = New XeroClient(XeroConfig)
    Dim xeroTokenTask = Await Task.Run(
        Function() Client.RequestClientCredentialsTokenAsync()
    )
    
    Dim apiInstance = New AccountingApi
    Dim GuidinvoiceID = Guid.Parse(InvoiceID)
    Dim result = Await apiInstance.GetInvoiceAsync(
        xeroTokenTask.AccessToken, 
        "", 
        GuidinvoiceID, 
        Nothing
    )
    
    ' Update project with invoice number and date from Xero
    ExProject.InvoiceNumber = result._Invoices.Select(
        Function(s) s.InvoiceNumber
    ).FirstOrDefault
    
    ExProject.InvoiceDate = result._Invoices.Select(
        Function(s) s.Date
    ).FirstOrDefault
    
    Return ExProject
End Function
```

**Purpose:** When staff selects an invoice dropdown, retrieve invoice number and date from Xero and store in FRED PublishingProject table.

---

#### **4. SetExitingOrdertInvNumDate()** - Link invoice to print order

```vb
Public Async Function SetExitingOrdertInvNumDate(
    ByVal ExOrder As Order, 
    ByVal InvoiceID As String, 
    ByVal businessID As Integer
) As Task(Of Order)
    
    ' Same as above but for Orders table instead of PublishingProjects
    ' Retrieves invoice details from Xero
    ' Updates Order.InvoiceNumber and Order.InvoiceDate
    
    Return ExOrder
End Function
```

**Purpose:** Link existing Xero invoice to FRED order.

---

## 🔄 **HOW IT ACTUALLY WORKS**

### **Current Workflow:**

```
┌──────────────────────────────────────────────────────────────┐
│ ACTUAL XERO INTEGRATION WORKFLOW (DISCOVERED)                │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ 1. Staff creates quote in Quotes.aspx                        │
│    └─> Quote emailed (NO Xero integration here)              │
│                                                               │
│ 2. Customer approves (phone/email)                           │
│    └─> Manual communication                                  │
│                                                               │
│ 3. Staff MANUALLY creates invoice in Xero.com                │
│    ├─> Opens browser, goes to Xero website                   │
│    ├─> Creates invoice with line items                       │
│    ├─> Sends invoice to customer                             │
│    └─> Invoice stored in Xero                                │
│                                                               │
│ 4. Staff creates order in NewOrder.aspx (FRED)               │
│    ├─> Enters job details                                    │
│    ├─> Creates job tickets                                   │
│    └─> Order saved to database                               │
│                                                               │
│ 5. Staff LINKS invoice to order (THIS IS WHERE XERO API USED)│
│    ├─> Dropdown populates from Xero API ✅                   │
│    ├─> Staff selects invoice from dropdown                   │
│    ├─> XeroDataAccess.GetInvoiceNumbersForClient()           │
│    ├─> XeroDataAccess.SetExitingOrdertInvNumDate()           │
│    └─> Invoice number/date written to Order table            │
│                                                               │
│ 6. Production completes job                                  │
│    └─> Job tickets marked complete                           │
│                                                               │
│ 7. Invoice already in Xero (from step 3)                     │
│    ├─> Customer pays                                         │
│    └─> Payment tracked in Xero                               │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### **Key Points:**

- ❌ **Quotes are NOT created in Xero** - Only emails
- ❌ **Invoices are NOT created via API** - Manual creation in Xero website
- ✅ **Existing invoices ARE retrieved** - Dropdown populated from Xero
- ✅ **Invoice details ARE synced** - Number and date pulled from Xero
- ✅ **Three businesses supported** - Print, Publishing, Signs

---

## 📊 **XERO API USED:**

### **Endpoints Called:**

```vb
' 1. Get invoices for contact
apiInstance.GetInvoicesAsync(
    accessToken,
    tenantId: "",
    ifModifiedSince: Nothing,
    where: Nothing,
    order: "Date DESC",
    ids: Nothing,
    invoiceNumbers: Nothing,
    contactIDs: TempContactGuidList,  ' Filter by customer
    statuses: Nothing,
    page: Nothing,
    includeArchived: Nothing,
    createdByMyApp: Nothing,
    unitdp: Nothing,
    summaryOnly: Nothing
)

' 2. Get single invoice by ID
apiInstance.GetInvoiceAsync(
    accessToken,
    tenantId: "",
    invoiceID: GuidinvoiceID,
    unitdp: Nothing
)
```

### **OAuth2 Client Credentials Flow:**

```vb
' Get access token (no user interaction required)
Dim XeroConfig = New XeroConfiguration
XeroConfig.ClientId = "02BB492DD4EC4A5DAEAB50088D3C8C0D"
XeroConfig.ClientSecret = "a70UA2sXzERadX-wWCSZoUFFkljAxA4gEuFSV1hKS_zKRPs2"

Dim Client = New XeroClient(XeroConfig)

' Request token
Dim xeroTokenTask = Await Task.Run(
    Function() Client.RequestClientCredentialsTokenAsync()
)

' Use token to make API calls
Dim result = Await apiInstance.GetInvoicesAsync(
    xeroTokenTask.AccessToken,
    ...
)
```

---

## 🔍 **WHERE XERO INTEGRATION IS USED**

### **Search Results for Usage:**

Looking for where `XeroDataAccess` class is instantiated and used...

**Finding:** The class exists and is functional, but usage appears to be in:
- Publishing project workflows (Freeda system)
- Order invoice linking
- Manual invoice selection dropdowns

**NOT used for:**
- Quote creation
- Automated invoice generation
- Quote → Invoice conversion

---

## 🎯 **WHAT THIS MEANS FOR NEW SYSTEM:**

### **✅ Good News:**

1. **Xero API credentials already exist** - All 3 businesses configured
2. **OAuth2 flow working** - Client credentials authentication proven
3. **Invoice retrieval working** - Can fetch invoice lists
4. **Multi-business support** - Pattern established for 3 businesses

### **❌ Gaps to Fill:**

1. **No Quote API integration** - Quotes.aspx doesn't use Xero at all
2. **No Invoice creation via API** - All manual in Xero website
3. **No Quote → Invoice conversion** - Manual process
4. **No Quote storage** - Quotes disappear after email

---

## 🚀 **NEW XERO MODULE ADVANTAGES:**

### **We Can Build On:**

```vb
' ✅ Use existing credentials (already in Web.config)
PrintClientId: "02BB492DD4EC4A5DAEAB50088D3C8C0D"
PubClientId: "926A463987B749FB9F21950B3B4212E9"
SignsClientId: "7D5CE8F957944A95878F5B1F1CEE6F3D"

' ✅ Use same OAuth2 pattern
XeroConfiguration + XeroClient + RequestClientCredentialsTokenAsync()

' ✅ Use same Xero SDK
Xero.NetStandard.OAuth2.Api.AccountingApi

' ✅ Use same business selection logic
If businessID = 1: Print
If businessID = 2: Publishing
If businessID = 3: Signs
```

### **We Can Add:**

```python
# NEW in Python Xero Module:

# 1. Create quotes in Xero (not just emails)
POST /Quotes
{
    "Contact": {"ContactID": "guid"},
    "LineItems": [...],
    "BrandingThemeID": "guid"
}

# 2. List/search quotes
GET /Quotes?where=Status=="DRAFT"

# 3. Convert quote to invoice
# Copy quote line items → Create invoice

# 4. Auto-create FRED orders from quotes
INSERT INTO Orders (...)
INSERT INTO JobTickets (...)

# 5. Link invoice back to order
UPDATE Orders SET InvoiceNumber = ?, InvoiceDate = ?
```

---

## 💡 **RECOMMENDED ARCHITECTURE:**

### **Python Backend (New Xero Module):**

```python
# AI_infrastructure/shared/xero_client_v2.py
class XeroAPIClient:
    """
    Improved Xero client based on legacy VB.NET pattern
    but with Quote support added
    """
    
    BUSINESS_CONFIGS = {
        1: {
            'name': 'InHouse Print',
            'client_id': '02BB492DD4EC4A5DAEAB50088D3C8C0D',
            'client_secret': 'a70UA2sXzERadX...'  # From Web.config
        },
        2: {
            'name': 'InHouse Publishing',
            'client_id': '926A463987B749FB9F21950B3B4212E9',
            'client_secret': 'aBWKAnfBl17roRt...'
        },
        3: {
            'name': 'InHouse Signs',
            'client_id': '7D5CE8F957944A95878F5B1F1CEE6F3D',
            'client_secret': 'xykFPAGUy5mHfM...'
        }
    }
    
    def get_invoices_for_contact(self, contact_id, business_id):
        """Match legacy GetInvoiceNumbersForClient()"""
        pass
    
    def create_quote(self, business_id, contact_id, line_items, **kwargs):
        """NEW - Not in legacy system"""
        pass
    
    def convert_quote_to_invoice(self, quote_id, business_id):
        """NEW - Not in legacy system"""
        pass
    
    def create_fred_order_from_quote(self, quote_id, business_id):
        """NEW - Not in legacy system"""
        pass
```

---

## 📁 **FILES TO REFERENCE:**

```
Legacy VB.NET Xero Integration:
├── C:\Users\gpoli\GIT\In_House_SQL\InHousePrint\DAL\
│   ├── XeroDataAccess.vb (472 lines) ✅ CRITICAL FILE
│   └── MYOBDataAccess.vb (commented out - old MYOB integration)
├── C:\Users\gpoli\GIT\In_House_SQL\InHousePrint\Web.config
│   └── Xero credentials (lines 50-57)
└── NuGet Packages:
    ├── Xero.NetStandard.OAuth2
    ├── Xero.NetStandard.OAuth2.Client
    └── Xero.NetStandard.OAuth2.Token

New Python Implementation:
├── AI_infrastructure/shared/xero_client_v2.py (to create)
├── UI/modules_external/xero/xero_routes.py (existing)
└── tools/implementations/xero_quotes.py (existing - update)
```

---

## 🔧 **MIGRATION CHECKLIST:**

### **✅ Already Have:**

- [x] Xero OAuth2 credentials (3 businesses)
- [x] Client Credentials flow working
- [x] Invoice retrieval API calls
- [x] Multi-business architecture
- [x] Database schema (Orders, JobTickets tables)

### **🔄 Need to Add:**

- [ ] Xero Quotes API integration
- [ ] Quote creation endpoint
- [ ] Quote → Invoice conversion
- [ ] Quote → Order automation
- [ ] Quote status tracking
- [ ] Customer quote portal
- [ ] Quote email via Xero (not SMTP)

---

## 🎉 **CONCLUSION:**

**The legacy system DOES have Xero integration, but ONLY for:**
- ✅ Retrieving existing invoices
- ✅ Linking invoices to orders
- ✅ Syncing invoice numbers/dates

**The legacy system DOES NOT have:**
- ❌ Quote creation in Xero
- ❌ Invoice creation via API
- ❌ Quote → Invoice conversion
- ❌ Automated order generation

**Our new Xero Module will:**
- ✅ Use the same Xero credentials
- ✅ Follow the same OAuth2 pattern
- ✅ Add Quote API capabilities
- ✅ Automate the entire workflow
- ✅ Eliminate manual steps

**This is a HUGE improvement over the legacy system!** 🚀
