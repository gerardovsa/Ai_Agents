# 🗄️ Fred's InHousePrint Database - ACTUAL Schema

**Date:** December 1, 2025  
**Source:** Direct database query results  
**Status:** ✅ VERIFIED - This is the REAL schema

---

## 📋 **JobTickets Table - Complete Column List**

### **Core Job Information:**
| Column | Type | Description |
|--------|------|-------------|
| `TicketID` | int | Unique job ticket ID (PRIMARY KEY) |
| `OrderID` | int | Links to Orders table (FOREIGN KEY) |
| `QTY` | int | Quantity to produce |
| `Cost` | decimal(10,2) | Job cost (per ticket, not order total) |
| `ShortJobDesc` | nvarchar(255) | Brief description |
| `TicketNotes` | nvarchar(MAX) | Detailed specifications, customer delivery info |
| `ColourStatus` | float | Status code (numeric: 1.0, 2.0, 3.0, etc.) |

### **Job Classification:**
| Column | Type | Description |
|--------|------|-------------|
| `StageID` | int | Production stage (1-10+) |
| `JobTypeID` | int | Type of job (links to JobType table) |

### **Materials:**
| Column | Type | Description |
|--------|------|-------------|
| `PaperSizeID` | int | Links to PaperSize table |
| `PaperTypeID` | int | Paper type ID |
| `GSM_ID` | int | Paper weight/thickness ID |
| `BindTypeID` | int | Links to BindType table (nullable) |

### **Finishing Options (Boolean flags - 1/0):**
| Column | Type | Description |
|--------|------|-------------|
| `CelloYes` | bit | Has cellophane lamination |
| `FrontCelloMatt` | bit | Front matte lamination |
| `FrontCelloGloss` | bit | Front gloss lamination |
| `FrontCelloNone` | bit | No front lamination |
| `BackCelloMatt` | bit | Back matte lamination |
| `BackCelloGloss` | bit | Back gloss lamination |
| `BackCelloNone` | bit | No back lamination |
| `FoldYes` | bit | Has folding |
| `FoldDesc` | nvarchar(100) | Folding description |
| `StitchYes` | bit | Has stitching |
| `StitchDesc` | nvarchar(100) | Stitching description |
| `DieCutYes` | bit | Has die cutting |
| `DieCutDesc` | nvarchar(100) | Die cutting description |
| `DrillYes` | bit | Has drilling |
| `DrillDesc` | nvarchar(100) | Drilling description |
| `ScoreYes` | bit | Has scoring |
| `PerfYes` | bit | Has perforation |
| `ScorePerfDesc` | nvarchar(100) | Score/perf description |
| `RingBind` | bit | Ring binding |
| `PerfectBind` | bit | Perfect binding |
| `PadGlue` | bit | Pad glue |
| `Books` | int | Number of books |
| `Pads` | int | Number of pads |
| `Sets` | int | Number of sets |
| `Pages` | int | Number of pages |

### **Multi-part Forms (NCR) - Each part has these fields:**
| Column Pattern | Description |
|----------------|-------------|
| `OriginalColourPrint` | Print type for original |
| `originalTC` | Original T/C flag |
| `originalNum` | Original number |
| `originalPerf` | Original perforation |
| `originalPaperColourID` | Original paper color |
| `Duplicate...` | Same 5 fields for duplicate |
| `Triplicate...` | Same 5 fields for triplicate |
| `Quad...` | Same 5 fields for quad |
| `Other...` | Same 5 fields for other |

### **Invoicing:**
| Column | Type | Description |
|--------|------|-------------|
| `InvoicingBusiness` | int | Business ID |
| `InternalInvoiceRequired` | bit | Needs internal invoice |
| `InternalInvoiceNumber` | nvarchar(50) | Internal invoice # |
| `InternalInvoiceComplete` | bit | Internal invoice done |

---

## 📊 **Orders Table - Complete Column List**

| Column | Type | Description |
|--------|------|-------------|
| `OrderID` | int | Primary key |
| `CustomerMYOB_ID` | uniqueidentifier | MYOB customer UUID |
| `ClientName` | nvarchar(255) | Customer name |
| `ReadToInvoice` | bit | Ready to invoice flag |
| `Invoiced` | bit | Has been invoiced |
| `CustomerPickup` | bit | Customer pickup flag |
| `ClientOrderNum` | nvarchar(100) | Client's order number |
| `OrderDate` | datetime | Order creation date |
| `Urgent` | bit | **Urgent flag (boolean)** |
| `DateRequired` | datetime | Due date |
| `OrderNotes` | nvarchar(MAX) | Order notes |
| `UserID` | int | User who created order |
| `ShippingType` | int | Shipping type ID |
| `InvoiceNumber` | nvarchar(50) | Invoice number |
| `InvoiceDate` | datetime | Date invoiced |
| `InvoicingBusinessID` | int | Business that invoiced |

### **❌ COLUMNS THAT DON'T EXIST IN ORDERS:**
- ❌ `Status` - Does NOT exist!
- ❌ `TotalCost` - Does NOT exist! (Cost is per-ticket in JobTickets)
- ❌ `PrintType` - Does NOT exist! (Use finishing flags in JobTickets)

---

## 👥 **Clients Table - Complete Column List**

**Purpose:** Customer/contact data synced from Xero accounting system

| Column | Type | Description |
|--------|------|-------------|
| `ContactID` | varchar(100) | **Primary key** - Xero contact UUID |
| `Name` | varchar(150) | Customer/company name |
| `AddressLine1` | varchar(250) | Street address |
| `AddressCity` | varchar(50) | City |
| `PostalCode` | varchar(10) | ZIP/postal code |
| `Phone` | varchar(50) | Contact phone |
| `BusinessID` | int | Business division ID |
| `LastSyncTime` | datetime | Last sync timestamp from Xero |
| `defaultEmail` | varchar(250) | Primary email address |

### **❌ COLUMNS THAT DON'T EXIST IN CLIENTS:**
- ❌ `ClientID` - Use `ContactID` instead!
- ❌ `ClientName` - Use `Name` instead!
- ❌ `Email` - Use `defaultEmail` instead!
- ❌ `ContactName` - Does NOT exist separately (use `Name`)
- ❌ `MYOB_ID` - Deprecated (system now uses Xero, not MYOB)

### **Relationship to Orders:**
```sql
-- Join pattern: Orders to Clients
SELECT o.OrderID, o.ClientName, c.Name, c.defaultEmail, c.Phone
FROM Orders o
LEFT JOIN Clients c ON o.CustomerMYOB_ID = c.ContactID
WHERE c.Name LIKE '%customer%'
```

**Note:** `Orders.ClientName` duplicates `Clients.Name` (denormalized for performance). Both contain the same customer name, but Clients table has additional contact details (email, phone, address).

---

## 🎯 **Example Real Record - Gerardo Poli Job**

```sql
=== ORDER DETAILS ===
OrderID: 56230
ClientName: Gerardo Poli
OrderDate: 2025-08-28
DateRequired: 2025-08-28
Urgent: 1 (YES - urgent job!)
Invoiced: 1
InvoiceDate: 2025-08-29

=== JOB TICKET DETAILS ===
TicketID: 72090
QTY: 500
Cost: $189.00
ShortJobDesc: "EVG Cover Stickers"

TicketNotes: 
"Jack gloss stickers
500 Individual Stickers to go on covers of 500 EVG guides 
going to the Philippines.

P:\Gerarado Stickers 28 08 2025"

ColourStatus: 2.0
StageID: 10
JobTypeID: 23

=== MATERIALS ===
PaperSizeID: 12
PaperSize: "Custom"
BindTypeID: null
BindType: null
```

---

## 🔍 **Correct SQL Query for Kanban Board**

```sql
SELECT TOP 100
    -- Order Information
    o.OrderID,
    o.ClientName,
    o.OrderDate,
    o.DateRequired,
    o.Urgent,  -- Boolean flag
    o.Invoiced,
    o.InvoiceDate,
    o.ClientOrderNum,
    
    -- Job Ticket Core
    jt.TicketID,
    jt.QTY,
    CAST(jt.Cost as DECIMAL(10,2)) as Cost,
    jt.ShortJobDesc,
    jt.TicketNotes as ProductionNotes,
    jt.ColourStatus,  -- Numeric code
    
    -- Job Classification
    jt.StageID,
    js.[Desc] as StageDescription,
    jt.JobTypeID,
    
    -- Materials (IDs + Joined Names)
    jt.PaperSizeID,
    ps.[Desc] AS PaperSize,
    jt.PaperTypeID,
    pt.[Desc] AS PaperType,
    jt.GSM_ID,
    gsm.[DESC] AS GSM,
    jt.BindTypeID,
    bt.BindTypeDesc AS BindType,
    
    -- Joined Details
    ISNULL(jtype.[Desc], '') as JobType,
    ISNULL(st.ShippingDesc, 'N/A') as ShippingDesc,
    ISNULL(b.[BusinessName], '') as InvoicingBusiness,
    
    -- Finishing Options
    jt.CelloYes,
    jt.FrontCelloMatt,
    jt.FrontCelloGloss,
    jt.BackCelloMatt,
    jt.BackCelloGloss,
    jt.FoldYes,
    jt.FoldDesc,
    jt.StitchYes,
    jt.RingBind,
    jt.PerfectBind,
    jt.Books,
    jt.Pages,
    
    -- Calculated Fields
    DATEDIFF(day, GETDATE(), o.DateRequired) as DaysUntilDue,
    DATEDIFF(day, o.OrderDate, GETDATE()) as DaysInSystem,
    
    -- Urgency Level (from DateRequired)
    CASE
        WHEN o.DateRequired < GETDATE() THEN 'OVERDUE'
        WHEN o.DateRequired <= DATEADD(day, 1, GETDATE()) THEN 'CRITICAL'
        WHEN o.DateRequired <= DATEADD(day, 3, GETDATE()) THEN 'HIGH'
        WHEN o.DateRequired <= DATEADD(day, 7, GETDATE()) THEN 'MEDIUM'
        ELSE 'LOW'
    END as UrgencyLevel,
    
    -- Customer Metrics (last 12 months)
    (
        SELECT COUNT(*) 
        FROM Orders o2 
        WHERE o2.ClientName = o.ClientName 
        AND o2.OrderDate >= DATEADD(month, -12, GETDATE())
    ) as CustomerOrderCount,
    
    (
        SELECT SUM(CAST(jt2.Cost as DECIMAL(10,2))) 
        FROM JobTickets jt2 
        INNER JOIN Orders o2 ON jt2.OrderID = o2.OrderID
        WHERE o2.ClientName = o.ClientName 
        AND o2.OrderDate >= DATEADD(month, -12, GETDATE())
    ) as CustomerLifetimeValue
    
FROM JobTickets jt
INNER JOIN Orders o ON jt.OrderID = o.OrderID
INNER JOIN JobStage js ON jt.StageID = js.StageID
LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
LEFT JOIN ShippingType st ON o.ShippingType = st.ShippingID
LEFT JOIN Business b ON o.InvoicingBusinessID = b.BusinessID

WHERE jt.InternalInvoiceComplete = 0  -- Active jobs only
    AND jt.StageID != 10  -- Exclude completed stage
    AND o.OrderDate >= DATEADD(month, -6, GETDATE())  -- Last 6 months

ORDER BY o.DateRequired ASC, o.Urgent DESC
```

---

## 🎨 **Frontend Field Mapping**

| Frontend Display | Database Source | Notes |
|-----------------|----------------|-------|
| Job ID | `jt.TicketID` | Primary identifier |
| Order ID | `jt.OrderID` | Links to order |
| Client | `o.ClientName` | Customer name |
| Description | `jt.TicketNotes` → `jt.ShortJobDesc` | TicketNotes is PRIMARY |
| Quantity | `jt.QTY` | Number to produce |
| Product Type | `JobType.[Desc]` | From JOIN |
| Quality/GSM | `gsm.[DESC]` | From JOIN |
| Paper Size | `PaperSize.[Desc]` | From JOIN |
| Binding | `BindType.BindTypeDesc` | From JOIN (nullable) |
| Cost | `jt.Cost` | Per-ticket cost |
| Due Date | `o.DateRequired` | Deadline |
| Urgent Flag | `o.Urgent` | Boolean (1/0) |
| Days in System | `DATEDIFF(day, o.OrderDate, GETDATE())` | Calculated |
| Stage | `js.[Desc]` | Current production stage |

---

## ⚠️ **Common Mistakes to Avoid**

### **DON'T Do This:**
```sql
❌ SELECT Status FROM Orders  -- Column doesn't exist!
❌ SELECT TotalCost FROM Orders  -- Column doesn't exist!
❌ SELECT PrintType FROM JobTickets  -- Column doesn't exist!
❌ WHERE ColourStatus = 'Red'  -- It's numeric, not text!
```

### **DO Do This:**
```sql
✅ SELECT Urgent FROM Orders  -- Boolean flag
✅ SELECT Cost FROM JobTickets  -- Per-ticket cost
✅ SELECT FrontCelloGloss, FrontCelloMatt FROM JobTickets  -- Individual flags
✅ WHERE ColourStatus = 2.0  -- Numeric comparison
```

---

## 📝 **Key Insights:**

1. ✅ **Cost is per-ticket** in JobTickets, not order total in Orders
2. ✅ **ColourStatus is numeric** (1.0, 2.0, 3.0), not Red/Yellow/Green text
3. ✅ **No PrintType column** - use finishing options (FrontCelloGloss, etc.)
4. ✅ **ShortJobDesc** is brief summary
5. ✅ **TicketNotes** contains full specs and customer delivery instructions
6. ✅ **Urgent flag** is at Order level (boolean), not JobTicket level
7. ✅ **Lookup tables** use `[Desc]` or `BindTypeDesc` columns for display names
8. ✅ **Square brackets** required for reserved words like `[Desc]`

---

**Last Updated:** December 1, 2025  
**Verified By:** Direct database queries against Fred (SQL Server)
