# 🔄 Xero Integration Flow Analysis - VB.NET to AI Agent Tools

**Generated:** November 13, 2025  
**Purpose:** Complete analysis of Xero data flow between VB.NET application, SQL Server, and Xero API to design AI agent tools

---

## 📊 **EXECUTIVE SUMMARY**

### Current Integration Pattern:
- **VB.NET Application (FRED)** reads/writes to **SQL Server Database**
- **XeroDataAccess.vb** class provides **READ-ONLY** access to Xero
- **NO data is written TO Xero** - only retrieved FROM Xero
- Data flows: **Xero → VB.NET → SQL Server** (ONE-WAY)

### Key Discovery:
The VB.NET code **NEVER creates or updates invoices in Xero**. It only:
1. Fetches invoice lists from Xero by ContactID
2. Retrieves single invoice details by InvoiceID
3. Updates SQL Server with Xero data

---

## 🗂️ **DATABASE SCHEMA ANALYSIS**

### 1. **Client Table** (Stores Xero Contact Sync)
```sql
Client Table Fields:
- ContactID (String, GUID)          -- Xero Contact GUID
- Name (String)                      -- Client name
- AddressLine1 (String)              -- Address
- AddressCity (String)               -- City
- PostalCode (String)                -- Postal code
- Phone (String)                     -- Phone number
- BusinessID (Integer)               -- 1=Print, 2=Publishing, 3=Signs
- LastSyncTime (DateTime, Nullable)  -- Last sync with Xero
```

**Purpose:** Maps FRED clients to Xero contacts for invoice retrieval

---

### 2. **Order Table** (Stores Print/Signs Orders)
```sql
Order Table Fields (Xero-related):
- OrderID (Integer, PK)              -- Internal order ID
- InvoiceNumber (String)             -- From Xero invoice
- InvoiceDate (DateTime)             -- From Xero invoice
- Invoiced (Boolean)                 -- Marked as invoiced flag
- InvoicingBusinessID (Integer)      -- 1=Print, 2=Publishing, 3=Signs
- CustomerMYOB_ID (String)           -- DEPRECATED (was MYOB, now Xero ContactID)
```

**Purpose:** Stores which Xero invoice number/date applies to this order

---

### 3. **PublishingProject Table** (Publishing Division Orders)
```sql
PublishingProject Table Fields (Xero-related):
- ProjectID (Integer, PK)            -- Internal project ID
- InvoiceNumber (String)             -- From Xero invoice
- InvoiceDate (DateTime)             -- From Xero invoice
- Invoiced (Boolean)                 -- Marked as invoiced flag
- ReadyToInvoice (Boolean)           -- Ready to invoice flag
- Customer_XEROID (String, GUID)     -- Xero Contact GUID
- ProjDesc (String)                  -- Project description
- CreateDate (DateTime)              -- Project created date
- CreateUser (Integer)               -- User who created project
- ETADate (DateTime)                 -- Expected completion date
```

**Purpose:** Publishing projects with Xero contact linkage

---

## 🔍 **XERO DATA FLOW ANALYSIS**

### **Flow 1: Get Invoice List for Client** (Most Common)

**VB.NET Function:** `GetInvoiceNumbersForClient(ContactID As Guid, BusinessID As Integer)`

**REQUEST to Xero:**
```
API Call: GET /api.xro/2.0/Invoices
Parameters:
  - access_token: {OAuth2 token}
  - ContactIDs: [ContactID]
  - order: "Date DESC"
  
Headers:
  - Authorization: Bearer {token}
  - Xero-tenant-id: {tenant_guid}
```

**RESPONSE from Xero:**
```json
{
  "_Invoices": [
    {
      "InvoiceID": "guid-here",
      "InvoiceNumber": "INV-0001",
      "Date": "2025-01-15",
      "Total": 1250.00,
      "AmountPaid": 1250.00,
      "AmountDue": 0.00,
      "AmountCredited": 0.00,
      "Status": "PAID"
    }
  ]
}
```

**DATA EXTRACTED:**
```csharp
DataTable columns:
- InvoiceNumberDesc: "INV-0001 - 15/01/2025 - $1250.00"  // Display text
- InvoiceID: "guid-here"                                  // Xero GUID
```

**STORED in SQL:**
- **NOT stored in Client table** (no invoice data there)
- **Only used for UI dropdown** in VB.NET application
- User selects invoice → **then updates Order/Project table**

---

### **Flow 2: Get Single Invoice Details**

**VB.NET Function:** `SetExitingProjectInvNumDate(ExProject, InvoiceID, businessID)` or `SetExitingOrdertInvNumDate(ExOrder, InvoiceID, businessID)`

**REQUEST to Xero:**
```
API Call: GET /api.xro/2.0/Invoices/{InvoiceID}
Parameters:
  - access_token: {OAuth2 token}
  - invoiceID: {guid}
  
Headers:
  - Authorization: Bearer {token}
  - Xero-tenant-id: {tenant_guid}
```

**RESPONSE from Xero:**
```json
{
  "_Invoices": [
    {
      "InvoiceID": "guid-here",
      "InvoiceNumber": "INV-0001",
      "Date": "2025-01-15",
      "Total": 1250.00,
      "LineItems": [...]
    }
  ]
}
```

**DATA EXTRACTED:**
```csharp
From result._Invoices:
- InvoiceNumber (String)
- Date (DateTime)
```

**STORED in SQL:**
```sql
-- For Orders:
UPDATE Orders 
SET InvoiceNumber = 'INV-0001',
    InvoiceDate = '2025-01-15',
    Invoiced = 1
WHERE OrderID = {orderID}

-- For Publishing Projects:
UPDATE PublishingProject 
SET InvoiceNumber = 'INV-0001',
    InvoiceDate = '2025-01-15',
    Invoiced = 1
WHERE ProjectID = {projectID}
```

---

### **Flow 3: Get Publishing Client Invoice History (FREEDA)**

**VB.NET Function:** `GetInvoicesForPublishingClientFreeda(ContactID As String)`

**REQUEST to Xero:**
```
API Call: GET /api.xro/2.0/Invoices
Parameters:
  - access_token: {OAuth2 token}
  - ContactIDs: [ContactID]
  - order: "Date DESC"
```

**RESPONSE from Xero:**
```json
{
  "_Invoices": [
    {
      "InvoiceID": "guid-1",
      "InvoiceNumber": "INV-0001",
      "Date": "2025-01-15",
      "Total": 1250.00,
      "AmountPaid": 1250.00,
      "AmountDue": 0.00,
      "AmountCredited": 0.00
    },
    {
      "InvoiceID": "guid-2",
      "InvoiceNumber": "INV-0002",
      "Date": "2025-01-20",
      "Total": 850.00,
      "AmountPaid": 0.00,
      "AmountDue": 850.00,
      "AmountCredited": 0.00
    }
  ]
}
```

**DATA EXTRACTED:**
```csharp
DataTable columns:
- InvoiceNumberDesc: "INV-0001"  // Just the number
- InvoiceID: "guid-1"
- InvoiceCost: "1250.00"
- Paid: "1250.00"
- Owing: "0.00"
- Credited: "0.00"
- Date: "15/01/2025"
```

**STORED in SQL:**
- **NOT stored** - displayed in UI only
- Used for financial reporting in FREEDA dashboard

---

## 🎯 **USER WORKFLOWS**

### **Workflow 1: Mark Order as Invoiced**

**Location:** `Invoices.aspx.vb` → `btnMarkInvoicedYes_Click`

**Steps:**
1. **User Action:** Clicks "Mark as Invoiced" on Order
2. **VB.NET:**
   - Loads `XeroDataAccess` class
   - Calls `GetInvoiceNumbersForClient(ContactID, BusinessID)`
   - Displays dropdown of invoices from Xero
3. **User Action:** Selects invoice from dropdown (or leaves blank)
4. **VB.NET:**
   - If invoice selected:
     - Calls `SetExitingOrdertInvNumDate(Order, InvoiceID, BusinessID)`
     - Updates `Order.InvoiceNumber` and `Order.InvoiceDate`
   - If no invoice selected:
     - Sets `Order.InvoiceDate = DateTime.Today`
   - Sets `Order.Invoiced = True`
   - Saves to SQL Server

**SQL Operations:**
```sql
-- Read from Xero (via API):
SELECT InvoiceID, InvoiceNumber, Date, Total 
FROM Xero.Invoices 
WHERE ContactID = '{clientContactID}'

-- Write to SQL Server:
UPDATE Orders 
SET Invoiced = 1,
    InvoiceNumber = 'INV-0001',  -- From Xero
    InvoiceDate = '2025-01-15'   -- From Xero
WHERE OrderID = {orderID}
```

---

### **Workflow 2: Mark Publishing Project as Invoiced**

**Location:** `PublishingBoard.aspx.vb` / `Invoices.aspx.vb`

**Steps:**
1. **User Action:** Clicks "Mark as Invoiced" on Publishing Project
2. **VB.NET:**
   - Loads project with `Customer_XEROID` field
   - Calls `GetInvoiceNumbersForClient(Customer_XEROID, 2)` (2 = Publishing)
   - Displays dropdown of invoices
3. **User Action:** Selects invoice
4. **VB.NET:**
   - Calls `SetExitingProjectInvNumDate(Project, InvoiceID, 2)`
   - Updates project fields
   - Saves to SQL Server

**SQL Operations:**
```sql
-- Read from Xero:
SELECT InvoiceID, InvoiceNumber, Date, Total 
FROM Xero.Invoices 
WHERE ContactID = '{Customer_XEROID}'

-- Write to SQL Server:
UPDATE PublishingProject 
SET Invoiced = 1,
    InvoiceNumber = 'INV-0001',
    InvoiceDate = '2025-01-15'
WHERE ProjectID = {projectID}
```

---

### **Workflow 3: View Client Invoice History (FREEDA)**

**Location:** Publishing dashboard / FREEDA interface

**Steps:**
1. **User Action:** Opens client record in FREEDA
2. **VB.NET:**
   - Calls `GetInvoicesForPublishingClientFreeda(ContactID)`
   - Retrieves full invoice history with payment details
3. **Display:** Shows DataTable with:
   - Invoice numbers
   - Dates
   - Total amounts
   - Paid amounts
   - Outstanding amounts
   - Credited amounts

**SQL Operations:**
```sql
-- Read from Xero (detailed history):
SELECT InvoiceID, InvoiceNumber, Date, Total, 
       AmountPaid, AmountDue, AmountCredited
FROM Xero.Invoices 
WHERE ContactID = '{contactID}'
ORDER BY Date DESC
```

---

## 🔐 **AUTHENTICATION FLOW**

**OAuth 2.0 Client Credentials (Private App)**

### **VB.NET Implementation:**
```vb
' Configure OAuth
Dim XeroConfig = New XeroConfiguration
XeroConfig.ClientId = PrintClientId      ' From Web.config
XeroConfig.ClientSecret = PrintClientSecret

' Get token
Dim Client = New XeroClient(XeroConfig)
Dim xeroToken = Await Client.RequestClientCredentialsTokenAsync()

' Make API call
Dim apiInstance = New AccountingApi
Dim result = Await apiInstance.GetInvoicesAsync(
    xeroToken.AccessToken,     -- OAuth token
    "",                        -- Xero-tenant-id (empty, gets from token)
    Nothing,                   -- ifModifiedSince
    Nothing,                   -- where clause
    "Date DESC",               -- order
    Nothing,                   -- IDs
    Nothing,                   -- InvoiceNumbers
    TempContactGuidList,       -- ContactIDs (filter by contact)
    Nothing,                   -- statuses
    Nothing,                   -- page
    Nothing,                   -- includeArchived
    Nothing,                   -- createdByMyApp
    Nothing,                   -- unitdp
    Nothing                    -- summaryOnly
)
```

**Key Points:**
- ✅ **Client Credentials flow** (no user interaction)
- ✅ **NO scope parameter** (scopes pre-configured in Xero portal)
- ✅ **30-minute token lifetime** with automatic refresh
- ✅ **3 separate apps** (Print, Publishing, Signs)

---

## 📋 **DATA FIELDS MAPPING**

### **From Xero API → VB.NET → SQL Server**

| **Xero Field** | **VB.NET Variable** | **SQL Field** | **Table** |
|----------------|---------------------|---------------|-----------|
| `InvoiceID` (GUID) | `I.InvoiceID` | - | Not stored |
| `InvoiceNumber` (String) | `I.InvoiceNumber` | `InvoiceNumber` | Order / PublishingProject |
| `Date` (DateTime) | `I.Date` | `InvoiceDate` | Order / PublishingProject |
| `Total` (Decimal) | `I.Total` | - | Display only |
| `AmountPaid` (Decimal) | `I.AmountPaid` | - | Display only |
| `AmountDue` (Decimal) | `I.AmountDue` | - | Display only |
| `AmountCredited` (Decimal) | `I.AmountCredited` | - | Display only |
| `Status` (String) | `I.Status` | - | Not used |
| `Contact.ContactID` (GUID) | - | `ContactID` | Client |
| - | - | `Customer_XEROID` | PublishingProject |

### **Business Logic Fields (SQL Only)**

| **SQL Field** | **Type** | **Purpose** |
|---------------|----------|-------------|
| `Invoiced` (Boolean) | User-controlled flag | "Has this been invoiced?" |
| `InvoicingBusinessID` (Integer) | Business selector | 1=Print, 2=Publishing, 3=Signs |
| `ReadyToInvoice` (Boolean) | Workflow flag | "Ready to be invoiced?" |
| `LastSyncTime` (DateTime) | Sync tracking | Last contact sync from Xero |

---

## 🚨 **CRITICAL INSIGHTS**

### **What the VB.NET Code DOES:**
1. ✅ **Reads** invoice lists from Xero by ContactID
2. ✅ **Reads** single invoice details by InvoiceID
3. ✅ **Displays** invoice data in UI dropdowns
4. ✅ **Updates** SQL Server with selected invoice data

### **What the VB.NET Code DOES NOT DO:**
1. ❌ **Create** invoices in Xero
2. ❌ **Update** invoices in Xero
3. ❌ **Delete** invoices in Xero
4. ❌ **Create** contacts in Xero
5. ❌ **Sync** orders TO Xero
6. ❌ **Write** any data back to Xero

### **Why This Matters:**
- Invoices are **created manually in Xero** (or via other system)
- FRED system **links existing invoices** to orders/projects
- FRED **does not automate invoice creation**
- Xero is the **source of truth** for invoice data

---

## 🛠️ **AI AGENT TOOL DESIGN**

### **Tool Category 1: Invoice Lookup Tools**

#### **Tool 1: `xero_get_invoices_for_contact`**
```python
def xero_get_invoices_for_contact(
    contact_id: str,           # Xero Contact GUID
    business_id: int,          # 1=Print, 2=Publishing, 3=Signs
    include_payments: bool = False,  # Include payment details?
    date_from: str = None,     # Optional date filter
    date_to: str = None        # Optional date filter
) -> List[Dict]:
    """
    Get all invoices for a specific Xero contact
    
    Returns:
    [
        {
            "invoice_id": "guid",
            "invoice_number": "INV-0001",
            "date": "2025-01-15",
            "total": 1250.00,
            "amount_paid": 1250.00,
            "amount_due": 0.00,
            "amount_credited": 0.00,
            "status": "PAID"
        }
    ]
    
    Use Case: "Show me all invoices for client X"
    """
```

#### **Tool 2: `xero_get_invoice_details`**
```python
def xero_get_invoice_details(
    invoice_id: str,           # Xero Invoice GUID
    business_id: int           # 1=Print, 2=Publishing, 3=Signs
) -> Dict:
    """
    Get detailed information for a specific invoice
    
    Returns:
    {
        "invoice_id": "guid",
        "invoice_number": "INV-0001",
        "date": "2025-01-15",
        "due_date": "2025-02-14",
        "total": 1250.00,
        "sub_total": 1136.36,
        "total_tax": 113.64,
        "amount_paid": 1250.00,
        "amount_due": 0.00,
        "line_items": [
            {
                "description": "500 Business Cards - Full Color",
                "quantity": 1,
                "unit_amount": 125.00,
                "line_amount": 125.00,
                "account_code": "200"
            }
        ],
        "contact": {
            "contact_id": "guid",
            "name": "Client Name"
        }
    }
    
    Use Case: "What's on invoice INV-0001?"
    """
```

---

### **Tool Category 2: Order/Project Linking Tools**

#### **Tool 3: `fred_link_order_to_invoice`**
```python
def fred_link_order_to_invoice(
    order_id: int,             # FRED Order ID
    invoice_id: str,           # Xero Invoice GUID
    business_id: int           # 1=Print, 2=Publishing, 3=Signs
) -> Dict:
    """
    Link FRED order to Xero invoice
    
    Process:
    1. Fetch invoice details from Xero (InvoiceNumber, Date)
    2. Update FRED Orders table:
       - SET InvoiceNumber = {from_xero}
       - SET InvoiceDate = {from_xero}
       - SET Invoiced = 1
    3. Return confirmation
    
    Returns:
    {
        "success": True,
        "order_id": 12345,
        "invoice_number": "INV-0001",
        "invoice_date": "2025-01-15",
        "message": "Order #12345 linked to invoice INV-0001"
    }
    
    Use Case: "Link order 12345 to invoice INV-0001"
    """
```

#### **Tool 4: `fred_link_project_to_invoice`**
```python
def fred_link_project_to_invoice(
    project_id: int,           # FRED Project ID
    invoice_id: str,           # Xero Invoice GUID
    business_id: int = 2       # Publishing = 2
) -> Dict:
    """
    Link FRED publishing project to Xero invoice
    
    Process:
    1. Fetch invoice details from Xero
    2. Update FRED PublishingProject table:
       - SET InvoiceNumber = {from_xero}
       - SET InvoiceDate = {from_xero}
       - SET Invoiced = 1
    3. Return confirmation
    
    Returns:
    {
        "success": True,
        "project_id": 789,
        "invoice_number": "INV-0002",
        "invoice_date": "2025-01-20",
        "message": "Project #789 linked to invoice INV-0002"
    }
    
    Use Case: "Mark publishing project 789 as invoiced with INV-0002"
    """
```

---

### **Tool Category 3: Client Invoice Analysis Tools**

#### **Tool 5: `xero_get_client_invoice_summary`**
```python
def xero_get_client_invoice_summary(
    contact_id: str,           # Xero Contact GUID
    business_id: int,          # 1=Print, 2=Publishing, 3=Signs
    period_months: int = 12    # Last N months
) -> Dict:
    """
    Get invoice summary for client (for FREEDA dashboard)
    
    Returns:
    {
        "contact_id": "guid",
        "contact_name": "Client Name",
        "period_months": 12,
        "invoice_count": 15,
        "total_invoiced": 18750.00,
        "total_paid": 16250.00,
        "total_outstanding": 2500.00,
        "total_credited": 125.00,
        "average_invoice": 1250.00,
        "invoices": [
            {
                "invoice_number": "INV-0001",
                "date": "2025-01-15",
                "total": 1250.00,
                "paid": 1250.00,
                "owing": 0.00,
                "status": "PAID"
            }
        ]
    }
    
    Use Case: "Show me client X's invoice history"
    """
```

#### **Tool 6: `fred_get_uninvoiced_orders`**
```python
def fred_get_uninvoiced_orders(
    business_id: int = None,   # Optional: 1=Print, 2=Publishing, 3=Signs
    client_id: int = None,     # Optional: Filter by client
    date_from: str = None,     # Optional: Date range
    date_to: str = None
) -> List[Dict]:
    """
    Get all FRED orders/projects that haven't been marked as invoiced
    
    Returns:
    [
        {
            "order_id": 12345,
            "order_type": "order",  # or "project"
            "client_name": "Client Name",
            "client_xero_contact_id": "guid",
            "order_date": "2025-01-10",
            "cost": 1250.00,
            "business_id": 1,
            "business_name": "InHouse Print",
            "ready_to_invoice": True,
            "days_since_order": 5
        }
    ]
    
    Use Case: "What orders need to be invoiced?"
    """
```

---

### **Tool Category 4: Workflow Automation Tools**

#### **Tool 7: `xero_suggest_invoice_for_order`**
```python
def xero_suggest_invoice_for_order(
    order_id: int,             # FRED Order ID
    business_id: int           # 1=Print, 2=Publishing, 3=Signs
) -> List[Dict]:
    """
    Suggest matching Xero invoices for FRED order (AI-assisted)
    
    Process:
    1. Get order details from FRED (client, date, amount)
    2. Get client's ContactID from FRED
    3. Get invoices from Xero for that contact
    4. Filter by date range (±7 days of order date)
    5. Filter by amount (±10% of order cost)
    6. Return ranked suggestions
    
    Returns:
    [
        {
            "invoice_id": "guid",
            "invoice_number": "INV-0001",
            "date": "2025-01-15",
            "total": 1250.00,
            "match_score": 95,  # 0-100 confidence
            "match_reasons": [
                "Date matches order date (2025-01-15)",
                "Amount matches order cost ($1250.00)",
                "Client matches"
            ]
        }
    ]
    
    Use Case: "Help me find the right invoice for order 12345"
    """
```

#### **Tool 8: `fred_bulk_link_invoices`**
```python
def fred_bulk_link_invoices(
    links: List[Dict]          # [{order_id, invoice_id, business_id}]
) -> Dict:
    """
    Link multiple orders/projects to invoices in one operation
    
    Input:
    [
        {"order_id": 12345, "invoice_id": "guid1", "business_id": 1},
        {"project_id": 789, "invoice_id": "guid2", "business_id": 2}
    ]
    
    Returns:
    {
        "success_count": 2,
        "failed_count": 0,
        "results": [
            {
                "order_id": 12345,
                "invoice_number": "INV-0001",
                "status": "success"
            },
            {
                "project_id": 789,
                "invoice_number": "INV-0002",
                "status": "success"
            }
        ]
    }
    
    Use Case: "Link these 10 orders to their invoices at once"
    """
```

---

### **Tool Category 5: Reporting & Analytics Tools**

#### **Tool 9: `xero_get_business_invoice_stats`**
```python
def xero_get_business_invoice_stats(
    business_id: int,          # 1=Print, 2=Publishing, 3=Signs
    date_from: str,            # Start date
    date_to: str               # End date
) -> Dict:
    """
    Get invoice statistics for entire business
    
    Returns:
    {
        "business_id": 1,
        "business_name": "InHouse Print",
        "period": "2025-01-01 to 2025-01-31",
        "invoice_count": 150,
        "total_invoiced": 187500.00,
        "total_paid": 165000.00,
        "total_outstanding": 22500.00,
        "average_invoice": 1250.00,
        "largest_invoice": 5000.00,
        "smallest_invoice": 50.00,
        "status_breakdown": {
            "PAID": 120,
            "AUTHORISED": 20,
            "DRAFT": 10
        }
    }
    
    Use Case: "What's our invoicing performance this month?"
    """
```

#### **Tool 10: `fred_xero_reconciliation_report`**
```python
def fred_xero_reconciliation_report(
    business_id: int,          # 1=Print, 2=Publishing, 3=Signs
    date_from: str,
    date_to: str
) -> Dict:
    """
    Compare FRED orders marked as invoiced vs actual Xero invoices
    
    Returns:
    {
        "fred_invoiced_count": 145,
        "fred_invoiced_total": 181250.00,
        "xero_invoice_count": 150,
        "xero_invoice_total": 187500.00,
        "discrepancy_count": 5,
        "discrepancy_total": 6250.00,
        "mismatches": [
            {
                "order_id": 12345,
                "fred_invoice_number": "INV-0001",
                "fred_total": 1250.00,
                "xero_invoice_number": "INV-0001",
                "xero_total": 1250.00,
                "status": "match"
            },
            {
                "order_id": 12346,
                "fred_invoice_number": "INV-0002",
                "fred_total": 850.00,
                "xero_invoice_number": None,
                "xero_total": None,
                "status": "missing_in_xero"
            }
        ]
    }
    
    Use Case: "Are our FRED records in sync with Xero?"
    """
```

---

## 🎛️ **TOOL TRIGGER PATTERNS**

### **Natural Language → Tool Mapping**

| **User Request** | **Tool to Use** | **Parameters** |
|------------------|-----------------|----------------|
| "Show me invoices for client ABC Corp" | `xero_get_invoices_for_contact` | contact_id, business_id |
| "What's on invoice INV-0001?" | `xero_get_invoice_details` | invoice_id, business_id |
| "Link order 12345 to invoice INV-0001" | `fred_link_order_to_invoice` | order_id, invoice_id, business_id |
| "Mark project 789 as invoiced" | `fred_link_project_to_invoice` | project_id, invoice_id |
| "Show client X's invoice history" | `xero_get_client_invoice_summary` | contact_id, business_id |
| "What orders need invoicing?" | `fred_get_uninvoiced_orders` | business_id (optional) |
| "Find invoice for order 12345" | `xero_suggest_invoice_for_order` | order_id, business_id |
| "Link these 10 orders to invoices" | `fred_bulk_link_invoices` | links array |
| "Invoicing stats for January" | `xero_get_business_invoice_stats` | business_id, date_from, date_to |
| "Are FRED and Xero in sync?" | `fred_xero_reconciliation_report` | business_id, date_from, date_to |

---

## 🔄 **COMPLETE WORKFLOW EXAMPLE**

### **Scenario: User wants to mark Order #12345 as invoiced**

**User:** "Link order 12345 to the invoice for that job"

**AI Agent Steps:**

1. **Get Order Details:**
   ```python
   # Query FRED database
   order = fred_db.get_order(12345)
   # Returns: {order_id: 12345, client_id: 45, business_id: 1, cost: 1250.00, order_date: '2025-01-10'}
   ```

2. **Get Client Xero ContactID:**
   ```python
   # Query FRED database
   client = fred_db.get_client(45)
   # Returns: {client_id: 45, name: 'ABC Corp', xero_contact_id: 'guid-123'}
   ```

3. **Find Matching Invoices:**
   ```python
   # Call AI tool
   suggestions = xero_suggest_invoice_for_order(
       order_id=12345,
       business_id=1
   )
   # Returns: [
   #   {invoice_id: 'guid-456', invoice_number: 'INV-0001', 
   #    total: 1250.00, match_score: 95}
   # ]
   ```

4. **Present to User:**
   ```
   AI: "I found invoice INV-0001 ($1,250.00) from Jan 15, 2025 that matches 
        order #12345 (95% confidence). Would you like me to link them?"
   ```

5. **Execute Link:**
   ```python
   # Call AI tool
   result = fred_link_order_to_invoice(
       order_id=12345,
       invoice_id='guid-456',
       business_id=1
   )
   # Returns: {success: True, invoice_number: 'INV-0001', message: 'Linked!'}
   ```

6. **Confirm:**
   ```
   AI: "✓ Order #12345 linked to invoice INV-0001 dated 2025-01-15"
   ```

---

## 📊 **BUSINESS INTELLIGENCE USE CASES**

### **Use Case 1: Daily Invoice Reconciliation**
```python
# AI Agent scheduled task (runs daily at 6am)
report = fred_xero_reconciliation_report(
    business_id=1,  # Print
    date_from='2025-01-01',
    date_to='2025-01-31'
)

if report['discrepancy_count'] > 0:
    send_email(
        to='accounting@inhouse.com',
        subject=f"Invoice Discrepancy Alert: {report['discrepancy_count']} mismatches",
        body=format_report(report)
    )
```

### **Use Case 2: Automated Invoice Linking**
```python
# AI Agent: Find and link uninvoiced orders
uninvoiced = fred_get_uninvoiced_orders(business_id=1)

links = []
for order in uninvoiced:
    suggestions = xero_suggest_invoice_for_order(
        order_id=order['order_id'],
        business_id=1
    )
    
    if suggestions and suggestions[0]['match_score'] > 90:
        # High confidence match
        links.append({
            'order_id': order['order_id'],
            'invoice_id': suggestions[0]['invoice_id'],
            'business_id': 1
        })

if links:
    result = fred_bulk_link_invoices(links)
    notify_user(f"Auto-linked {result['success_count']} orders to invoices")
```

### **Use Case 3: Client Invoice Dashboard**
```python
# AI Agent: Generate client dashboard
def generate_client_dashboard(contact_id, business_id):
    summary = xero_get_client_invoice_summary(
        contact_id=contact_id,
        business_id=business_id,
        period_months=12
    )
    
    invoices = xero_get_invoices_for_contact(
        contact_id=contact_id,
        business_id=business_id,
        include_payments=True
    )
    
    return {
        'summary': summary,
        'recent_invoices': invoices[:5],
        'payment_health': calculate_payment_health(summary),
        'recommendations': generate_recommendations(summary)
    }
```

---

## ✅ **IMPLEMENTATION CHECKLIST**

### **Phase 1: Core Invoice Tools (10 tools)**
- [ ] `xero_get_invoices_for_contact` - Fetch invoice list
- [ ] `xero_get_invoice_details` - Fetch single invoice
- [ ] `xero_get_client_invoice_summary` - Invoice history
- [ ] `fred_link_order_to_invoice` - Link order to invoice
- [ ] `fred_link_project_to_invoice` - Link project to invoice
- [ ] `fred_get_uninvoiced_orders` - Find uninvoiced orders
- [ ] `xero_suggest_invoice_for_order` - AI matching
- [ ] `fred_bulk_link_invoices` - Batch linking
- [ ] `xero_get_business_invoice_stats` - Business stats
- [ ] `fred_xero_reconciliation_report` - Sync check

### **Phase 2: Database Integration**
- [ ] Create `fred_db` connection module
- [ ] Test SQL Server read operations
- [ ] Test SQL Server write operations (UPDATE orders)
- [ ] Add transaction rollback support
- [ ] Add audit logging for updates

### **Phase 3: Xero API Integration**
- [ ] Extend existing `xero_routes.py`
- [ ] Add new endpoints for invoice operations
- [ ] Test all 3 business connections
- [ ] Add error handling for API failures
- [ ] Add rate limiting protection

### **Phase 4: AI Matching Logic**
- [ ] Build `xero_suggest_invoice_for_order` algorithm
- [ ] Test date matching (±7 days)
- [ ] Test amount matching (±10%)
- [ ] Add confidence scoring
- [ ] Add manual override support

### **Phase 5: Testing & Validation**
- [ ] Unit tests for each tool
- [ ] Integration tests with FRED database
- [ ] Integration tests with Xero API
- [ ] End-to-end workflow tests
- [ ] Performance testing (bulk operations)

---

## 🎯 **SUCCESS METRICS**

- **Automation Rate:** % of orders auto-linked to invoices
- **Accuracy Rate:** % of AI suggestions that are correct
- **Time Savings:** Hours saved vs manual linking
- **Reconciliation Accuracy:** % match between FRED and Xero
- **User Satisfaction:** Feedback on tool usefulness

---

**END OF ANALYSIS**

This document provides complete specifications for building AI agent tools that replicate and enhance the VB.NET Xero integration workflow.
