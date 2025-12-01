# 📊 CONSOLIDATED FRED DATABASE SCHEMA - COMPLETE GUIDE v2.0

**Version:** 2.0 (Corrected & Validated)  
**Date:** December 1, 2025  
**Verified Against:** Fred production database (FredDEV)  
**Status:** ✅ Production Ready

---

## 🚨 CRITICAL WARNINGS - READ FIRST

### ❌ **Columns That DON'T EXIST (Despite Documentation)**

These columns are **NEVER referenced** in tool implementations or queries:

```sql
-- ORDERS TABLE - Non-existent columns:
Orders.Status          → Use Orders.Invoiced (bit) instead
Orders.TotalCost       → Calculate SUM(JobTickets.Cost) instead

-- JOBTICKETS TABLE - Non-existent columns:
JobTickets.PrintType   → Check JobTickets.TicketNotes instead
JobTickets.DateCreated → Use Orders.OrderDate (must JOIN Orders) instead
```

### ⚠️ **Critical Misunderstandings**

```sql
-- ColourStatus is DEADLINE URGENCY (not print color!)
ColourStatus → NOT print color! It's a DEADLINE SYSTEM (int FK to ColourStatus table)
              → Values: "Before Lunch Today", "Timely Manner", "Hold", etc.
              → MUST JOIN ColourStatus table to get description
              → OrderPriority: 1 (highest urgency) to 7 (lowest urgency)

-- [Desc] is a RESERVED KEYWORD
[Desc]       → Reserved SQL keyword - MUST use [square brackets]
              → Applies to: PaperSize.[Desc], JobType.[Desc], PaperType.[Desc], 
                           JobStage.[Desc], GSM.[DESC]

-- Dates are ONLY in Orders table
Dates        → JobTickets has NO date columns
              → ALWAYS use Orders.OrderDate (requires JOIN)
              → ALWAYS use Orders.DateRequired for deadlines
```

---

## 📋 CORE TABLES SCHEMA

### **1. Orders Table** (16 columns)

**Primary business transaction container - ONE order may have MULTIPLE job tickets**

```sql
CREATE TABLE Orders (
    -- ============================================================================
    -- PRIMARY KEY
    -- ============================================================================
    OrderID              int PRIMARY KEY,      -- Unique order identifier
    
    -- ============================================================================
    -- CUSTOMER INFORMATION
    -- ============================================================================
    CustomerMYOB_ID      varchar(100),         -- MYOB customer GUID (accounting sync)
    ClientName           varchar(250),         -- Customer name (searchable, may differ from MYOB)
    ClientOrderNum       varchar(50),          -- Customer PO/reference number
    
    -- ============================================================================
    -- ORDER DATES & URGENCY
    -- ============================================================================
    OrderDate            date,                 -- ✅ Order creation date (ONLY date field in system!)
    DateRequired         date,                 -- ✅ Customer deadline (for production prioritization)
    Urgent               bit,                  -- Urgent flag (used with ColourStatus for prioritization)
    
    -- ============================================================================
    -- INVOICE INFORMATION (Financial Status)
    -- ============================================================================
    Invoiced             bit,                  -- ✅ USE THIS (not "Status" which doesn't exist!)
                                               -- 1 = Invoiced (complete), 0 = Pending/In Progress
    InvoiceNumber        varchar(50),          -- Invoice reference (when Invoiced = 1)
    InvoiceDate          date,                 -- Date invoiced
    ReadToInvoice        bit,                  -- Ready for invoicing (production complete)
    InvoicingBusinessID  int,                  -- FK to Business (which division invoices this)
    
    -- ============================================================================
    -- DELIVERY
    -- ============================================================================
    CustomerPickup       bit,                  -- Pickup vs delivery (1 = pickup, 0 = delivery)
    ShippingType         int,                  -- FK to ShippingType (Courier/Freight/Post/etc.)
    
    -- ============================================================================
    -- OTHER
    -- ============================================================================
    OrderNotes           varchar(250),         -- Order-level notes (general comments)
    UserID               int                   -- FK to Users (who created the order)
)
```

**❌ DOES NOT HAVE:**
- `Status` (nvarchar) - **NEVER EXISTED** - Use `Invoiced` (bit) instead
- `TotalCost` (decimal) - **NEVER EXISTED** - Calculate via `SUM(JobTickets.Cost)`

---

### **2. JobTickets Table** (70 columns)

**Individual job specifications within an order - PRIMARY source of truth for production**

#### **A. Core Fields** (9 essential columns)

```sql
-- ============================================================================
-- PRIMARY/FOREIGN KEYS
-- ============================================================================
TicketID              int PRIMARY KEY,        -- Unique job ticket ID
OrderID               int FK → Orders.OrderID, -- Parent order

-- ============================================================================
-- JOB CLASSIFICATION
-- ============================================================================
StageID               int FK → JobStage.StageID,  -- Production stage
                                                   -- (ArtOnly/ArtAndPrint/Digital/Complete/etc.)
JobTypeID             int FK → JobType.JobTypeID, -- Job category
                                                   -- (Business Cards/Flyers/Books/etc.)
ColourStatus          int FK → ColourStatus.ColourID,  -- ⚠️ DEADLINE URGENCY, not print color!
                                                        -- 1 = Before Lunch Today (highest priority)
                                                        -- 7 = Hold (lowest priority)

-- ============================================================================
-- QUANTITY & COST
-- ============================================================================
QTY                   int,                    -- Quantity ordered
Cost                  money,                  -- Individual job cost (per ticket)
                                              -- ⚠️ Order total = SUM(Cost) GROUP BY OrderID

-- ============================================================================
-- MATERIALS
-- ============================================================================
PaperSizeID           int FK → PaperSize.SizeID,     -- Paper size (A4/BC-90x55/etc.)
PaperTypeID           int FK → PaperType.PaperTypeID, -- Paper type (Satin/Bond/Vinyl/etc.)
GSM_ID                int FK → GSM.GSM_ID,            -- Paper weight (350/100/80/etc.)
BindTypeID            int FK → BindType.BindID,       -- Nullable (None/Spiral/etc.)

-- ============================================================================
-- JOB DETAILS
-- ============================================================================
ShortJobDesc          varchar(100),           -- Brief description (summary)
TicketNotes           varchar(500),           -- ⭐ PRIMARY source of truth
                                              -- Contains full specifications when structured columns NULL
                                              -- Check this first for product details
```

#### **B. Celloglaze Options** (7 columns)

```sql
-- ============================================================================
-- CELLOGLAZE/LAMINATION OPTIONS
-- ============================================================================
CelloYes              bit,                    -- Has any celloglaze
FrontCelloNone        bit,                    -- Front: No lamination
FrontCelloMatt        bit,                    -- Front: Matt lamination
FrontCelloGloss       bit,                    -- Front: Gloss lamination
BackCelloNone         bit,                    -- Back: No lamination
BackCelloMatt         bit,                    -- Back: Matt lamination
BackCelloGloss        bit,                    -- Back: Gloss lamination
```

#### **C. Finishing Options** (14 columns)

```sql
-- ============================================================================
-- FINISHING PROCESSES
-- ============================================================================
FoldYes               bit,                    -- Folding required
FoldDesc              nvarchar,               -- Fold specifications
StitchYes             bit,                    -- Stitching required
StitchDesc            nvarchar,               -- Stitch specifications
DieCutYes             bit,                    -- Die cutting required
DieCutDesc            nvarchar,               -- Die cut specifications
DrillYes              bit,                    -- Drilling required
DrillDesc             nvarchar,               -- Drill specifications
ScoreYes              bit,                    -- Scoring required
PerfYes               bit,                    -- Perforation required
ScorePerfDesc         nvarchar,               -- Score/perf specifications
RingBind              bit,                    -- Ring binding
PerfectBind           bit,                    -- Perfect binding
PadGlue               bit,                    -- Pad gluing
Books                 bit,                    -- Book format
Pads                  bit,                    -- Pad format
```

#### **D. Numbering/Book Details** (7 columns)

```sql
-- ============================================================================
-- NUMBERING & BOOK STRUCTURE
-- ============================================================================
Sets                  int,                    -- Number of sets
Pages                 int,                    -- Pages per unit
NumberStart           int,                    -- Starting number for numbering
NumberEnd             int,                    -- Ending number for numbering
Cover                 bit,                    -- Has cover
```

#### **E. Carbonless Forms** (25 columns)

**Pattern repeats for: Original, Duplicate, Triplicate, Quad, Other**

```sql
-- ============================================================================
-- CARBONLESS FORM SPECIFICATIONS (5 layers × 5 properties = 25 columns)
-- ============================================================================
-- Original (first copy):
OriginalColourPrint   bit,                    -- Color printing on original
OriginalTC            bit,                    -- Top coated
OriginalNum           bit,                    -- Numbered
OriginalPerf          bit,                    -- Perforated
OriginalPaperColourID int FK → PadPaperColour, -- Paper color

-- Duplicate (second copy):
DuplicateColourPrint  bit,
DuplicateTC           bit,
DuplicateNum          bit,
DuplicatePerf         bit,
DuplicatePaperColourID int FK → PadPaperColour,

-- Triplicate (third copy):
TriplicateColourPrint bit,
TriplicateTC          bit,
TriplicateNum         bit,
TriplicatePerf        bit,
TriplicatePaperColourID int FK → PadPaperColour,

-- Quad (fourth copy):
QuadColourPrint       bit,
QuadTC                bit,
QuadNum               bit,
QuadPerf              bit,
QuadPaperColourID     int FK → PadPaperColour,

-- Other (fifth copy):
OtherColourPrint      bit,
OtherTC               bit,
OtherNum              bit,
OtherPerf             bit,
OtherPaperColourID    int FK → PadPaperColour
```

#### **F. Internal Invoicing** (3 columns)

```sql
-- ============================================================================
-- INTERNAL BUSINESS INVOICING
-- ============================================================================
InvoicingBusiness         int,               -- Which business division invoices this
InternalInvoiceRequired   bit,               -- Requires internal invoice
InternalInvoiceNumber     varchar(50),       -- Internal invoice reference
InternalInvoiceComplete   bit,               -- Internal invoicing complete
```

**❌ DOES NOT HAVE:**
- `PrintType` (nvarchar) - **NEVER EXISTED** - Check `TicketNotes` for print type info
- `DateCreated` - **NEVER EXISTED** - Use `Orders.OrderDate` (must JOIN)

---

## 🔗 REFERENCE TABLES

### **3. ColourStatus** (Production Deadline System)

**⚠️ This is NOT print color - it's production urgency/deadline priority!**

```sql
CREATE TABLE ColourStatus (
    ColourID         int PRIMARY KEY,
    ColourDesc       varchar(50),          -- Human-readable deadline description
    ColourValue      varchar(20),          -- Hex color for UI display
    OrderPriority    int                   -- 1 (highest urgency) to 7 (lowest)
)

-- ACTUAL DATA:
ColourID  ColourDesc                  ColourValue    OrderPriority
--------  ------------------------    -----------    -------------
1         Hold                        White          7 (lowest urgency)
2         Before Lunch Today          #ff0000        1 (highest urgency)
3         Before COB Today            #ff6600        2
4         Before Lunch Tomorrow       #ffff00        3
5         Before COB Tomorrow         #33cc33        4
6         Urgent This Week            Blue           5
7         Timely Manner               Purple         6 (normal priority)
```

**Usage Pattern:**
```sql
-- ✅ CORRECT - Get deadline description
SELECT cs.ColourDesc, cs.OrderPriority
FROM JobTickets jt
LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID

-- ❌ WRONG - Treating as print color
WHERE jt.ColourStatus = 'Red'  -- Error: int column, not text!
```

---

### **4. JobType** (Job Category)

```sql
CREATE TABLE JobType (
    JobTypeID   int PRIMARY KEY,
    [Desc]      nvarchar(100),           -- ⚠️ [Desc] requires square brackets!
    Cello       bit,                     -- Celloglaze available
    Fold        bit,                     -- Folding available
    Stitch      bit,                     -- Stitching available
    DieCut      bit,                     -- Die cutting available
    Bind        bit,                     -- Binding available
    IsActive    bit                      -- Active/archived
)

-- SAMPLE DATA (13 of 47 active types):
JobTypeID   [Desc]                          Cello  Fold  Stitch  DieCut  Bind
---------   -----------------------------   -----  ----  ------  ------  ----
6           Business Cards - Double Sided   ✓      -     -       ✓       -
7           Flyers - Single Side            -      ✓     -       -       -
8           Flyers - Double Sided           -      ✓     -       -       -
15          Flyers - Folded                 -      ✓     -       -       -
23          Stickers - Digital Print        -      -     -       -       -
25          Books/Booklets                  -      -     -       -       ✓
35          Posters                         -      -     -       -       -
47          Invoice Books                   -      -     -       -       ✓
88          other                           -      -     -       -       -
```

**Usage Pattern:**
```sql
-- ✅ CORRECT - Use [Desc] with square brackets
SELECT jtype.[Desc]
FROM JobType jtype

-- ❌ WRONG - Desc without brackets
SELECT jtype.Desc  -- Error: Reserved keyword!
```

---

### **5. JobStage** (Production Stage)

```sql
CREATE TABLE JobStage (
    StageID    int PRIMARY KEY,
    [Desc]     nvarchar(50)              -- ⚠️ [Desc] requires square brackets!
)

-- ACTUAL DATA (6 of 10 stages):
StageID    [Desc]
-------    -----------------
1          ArtOnly
2          ArtAndPrint
3          OnHold
4          Digital - 9110
5          Digital - Other
6          Digital - Complete
10         JobComplete
```

**Usage Pattern:**
```sql
-- ✅ CORRECT - Filter by production stage
LEFT JOIN JobStage js ON jt.StageID = js.StageID
WHERE js.[Desc] IN ('ArtOnly', 'ArtAndPrint')

-- ❌ WRONG - Desc without brackets
WHERE js.Desc = 'ArtOnly'  -- Error: Reserved keyword!
```

---

### **6. PaperType**

```sql
CREATE TABLE PaperType (
    PaperTypeID    int PRIMARY KEY,
    [Desc]         nvarchar(100)         -- ⚠️ [Desc] requires square brackets!
)

-- SAMPLE DATA (8 of 75 types):
PaperTypeID    [Desc]
-----------    ------------------------
2              Satin
3              Green Bond
4              Jac Split Back Label
5              White Bond
6              White Vinyl Sticker
7              None
44             Uncoated
54             Jac Back Label
```

---

### **7. GSM** (Paper Weight)

```sql
CREATE TABLE GSM (
    GSM_ID    int PRIMARY KEY,
    [DESC]    nvarchar(50)              -- ⚠️ [DESC] requires square brackets (uppercase!)
)

-- SAMPLE DATA (7 of 14 weights):
GSM_ID    [DESC]
------    --------
3         350
4         80
5         Standard
7         300
8         None
12        100
23        100GSM
```

**⚠️ Note:** This table uses `[DESC]` (uppercase) while others use `[Desc]` (mixed case)

---

### **8. PaperSize**

```sql
CREATE TABLE PaperSize (
    SizeID    int PRIMARY KEY,
    [Desc]    nvarchar(100)             -- ⚠️ [Desc] requires square brackets!
)

-- SAMPLE DATA (4 of 78 sizes):
SizeID    [Desc]
------    -----------
3         BC - 90x55      -- Business card standard
12        100x70
30        A6
74        Various
```

**❌ CRITICAL:** PaperSize has **ONLY** `SizeID` and `[Desc]` - NO Width/Height columns!

---

### **9. BindType**

```sql
CREATE TABLE BindType (
    BindID          int PRIMARY KEY,
    BindTypeDesc    nvarchar(50)          -- ⚠️ Uses "BindTypeDesc" NOT [Desc]!
)

-- SAMPLE DATA (2 of 8 types):
BindID    BindTypeDesc
------    --------------
1         None
7         Spiral Bound
```

**⚠️ CRITICAL:** Unlike other reference tables, BindType uses `BindTypeDesc` NOT `[Desc]`!

---

### **10. ShippingType**

```sql
CREATE TABLE ShippingType (
    ShippingID      int PRIMARY KEY,
    ShippingDesc    nvarchar(50)
)

-- ACTUAL DATA:
ShippingID    ShippingDesc
----------    ------------------
1             Customer Pickup
2             Courier
3             Freight
4             Post
5             N/A
6             InHouse Delivery
```

---

### **11. Users**

```sql
CREATE TABLE Users (
    UserID          int PRIMARY KEY,
    UserName        varchar(50),
    FirstName       varchar(50),
    LastName        varchar(50),
    IsActive        bit,
    AccountType     int                   -- User role/permissions
)

-- SAMPLE DATA:
UserID    UserName    FirstName    LastName    IsActive    AccountType
------    --------    ---------    --------    --------    -----------
1         Deb         Debbie       Davidson    ✓           3
5         Guy         Guy          Kirk        ✓           1
58        Karen       Karen        Karen       ✓           ?
```

---

### **12. Business**

```sql
CREATE TABLE Business (
    BusinessID      int PRIMARY KEY,
    BusinessName    varchar(100)
)

-- ACTUAL DATA:
BusinessID    BusinessName
----------    --------------------------
1             InHouse Print & Design
2             InHouse Publishing
3             InHouse Signs
```

---

### **13. Clients**

```sql
CREATE TABLE Clients (
    ContactID       uniqueidentifier PRIMARY KEY,  -- GUID format
    Name            varchar(250),
    AddressLine1    varchar(250),
    Phone           varchar(50),
    BusinessID      int FK → Business.BusinessID
)

-- SAMPLE DATA:
ContactID (GUID)                      Name           BusinessID
------------------------------------  ------------   ----------
{uuid-format}                         Gerardo Poli   1
{uuid-format}                         The Iconic     1
```

---

## 🔧 ESSENTIAL SQL PATTERNS

### **Pattern 1: Basic Order Query with All References**

**Complete order details with proper JOINs and [Desc] brackets**

```sql
SELECT TOP 20
    -- ============================================================================
    -- ORDER INFORMATION
    -- ============================================================================
    o.OrderID,
    o.ClientName,
    o.OrderDate,                                     -- ✅ ONLY date field in system
    o.DateRequired,
    o.Urgent,
    o.Invoiced,                                      -- ✅ Not "Status" (doesn't exist)
    o.InvoiceNumber,
    o.ClientOrderNum,
    
    -- ============================================================================
    -- JOB TICKET CORE
    -- ============================================================================
    jt.TicketID,
    jt.QTY,
    jt.Cost,
    jt.ShortJobDesc,
    jt.TicketNotes,                                  -- ⭐ PRIMARY source of truth
    
    -- ============================================================================
    -- REFERENCE DATA (note [Desc] brackets!)
    -- ============================================================================
    jtype.[Desc] AS JobType,                         -- ⚠️ [Desc] with brackets!
    pt.[Desc] AS PaperType,                          -- ⚠️ [Desc] with brackets!
    ps.[Desc] AS PaperSize,                          -- ⚠️ [Desc] with brackets!
    gsm.[DESC] AS PaperWeight,                       -- ⚠️ [DESC] uppercase!
    bt.BindTypeDesc AS BindType,                     -- ⚠️ Uses "BindTypeDesc" not [Desc]!
    js.[Desc] AS ProductionStage,                    -- ⚠️ [Desc] with brackets!
    cs.ColourDesc AS ProductionDeadline,             -- ⚠️ Deadline, not print color!
    cs.OrderPriority AS DeadlinePriority,            -- 1 (highest) to 7 (lowest)
    st.ShippingDesc AS ShippingMethod,
    u.FirstName + ' ' + u.LastName AS CreatedBy,
    b.BusinessName
    
FROM Orders o
JOIN JobTickets jt ON o.OrderID = jt.OrderID
LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
LEFT JOIN JobStage js ON jt.StageID = js.StageID
LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
LEFT JOIN ShippingType st ON o.ShippingType = st.ShippingID
LEFT JOIN Users u ON o.UserID = u.UserID
LEFT JOIN Business b ON o.InvoicingBusinessID = b.BusinessID

WHERE o.ClientName LIKE '%customer%'
ORDER BY o.OrderDate DESC
```

---

### **Pattern 2: Find Orders by Customer**

```sql
SELECT TOP 10
    o.OrderID,
    o.ClientName,
    o.OrderDate,
    o.Invoiced,                                      -- ✅ Not o.Status (doesn't exist)
    jt.ShortJobDesc,
    jt.Cost,
    cs.ColourDesc AS Deadline,
    cs.OrderPriority
FROM Orders o
JOIN JobTickets jt ON o.OrderID = jt.OrderID
LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
WHERE o.ClientName LIKE '%Gerardo%'
ORDER BY o.OrderDate DESC
```

---

### **Pattern 3: Urgent Orders This Week**

```sql
SELECT TOP 20
    o.OrderID,
    o.ClientName,
    o.DateRequired,
    jt.ShortJobDesc,
    cs.ColourDesc AS Deadline,
    cs.OrderPriority
FROM Orders o
JOIN JobTickets jt ON o.OrderID = jt.OrderID
LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
WHERE o.Urgent = 1
  AND o.OrderDate >= DATEADD(day, -7, GETDATE())
ORDER BY cs.OrderPriority ASC, o.DateRequired ASC    -- Priority 1 first
```

---

### **Pattern 4: Calculate Order Totals**

**Order total is SUM of JobTickets.Cost (not o.TotalCost which doesn't exist)**

```sql
SELECT TOP 20
    o.OrderID,
    o.ClientName,
    o.OrderDate,
    o.Invoiced,
    COUNT(jt.TicketID) AS TotalTickets,
    SUM(jt.Cost) AS OrderTotal                       -- ✅ Calculate total, no o.TotalCost!
FROM Orders o
JOIN JobTickets jt ON o.OrderID = jt.OrderID
WHERE o.OrderDate >= '2025-01-01'
GROUP BY o.OrderID, o.ClientName, o.OrderDate, o.Invoiced
ORDER BY OrderTotal DESC
```

---

### **Pattern 5: Production Status Report**

```sql
SELECT TOP 20
    o.OrderID,
    o.ClientName,
    jt.ShortJobDesc,
    js.[Desc] AS Stage,                              -- ⚠️ [Desc] with brackets!
    cs.ColourDesc AS Deadline,
    cs.OrderPriority,
    jtype.[Desc] AS JobType,                         -- ⚠️ [Desc] with brackets!
    u.FirstName + ' ' + u.LastName AS AssignedTo
FROM Orders o
JOIN JobTickets jt ON o.OrderID = jt.OrderID
LEFT JOIN JobStage js ON jt.StageID = js.StageID
LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
LEFT JOIN Users u ON o.UserID = u.UserID
WHERE o.Invoiced = 0                                 -- Not invoiced yet
  AND js.[Desc] NOT IN ('JobComplete', 'OnHold')
ORDER BY cs.OrderPriority ASC, o.OrderDate ASC       -- Urgent first
```

---

## ❌ COMMON MISTAKES & FIXES

### **Mistake 1: Using Non-Existent Columns**

```sql
-- ❌ WRONG - Status column doesn't exist
WHERE o.Status = 'Completed'
-- ✅ CORRECT - Use Invoiced bit field
WHERE o.Invoiced = 1

-- ❌ WRONG - TotalCost column doesn't exist
SELECT o.TotalCost
-- ✅ CORRECT - Calculate from JobTickets
SELECT SUM(jt.Cost) AS OrderTotal
FROM Orders o
JOIN JobTickets jt ON o.OrderID = jt.OrderID
GROUP BY o.OrderID

-- ❌ WRONG - DateCreated doesn't exist in JobTickets
WHERE jt.DateCreated > '2025-01-01'
-- ✅ CORRECT - Use Orders.OrderDate (must JOIN)
WHERE o.OrderDate > '2025-01-01'

-- ❌ WRONG - PrintType doesn't exist in JobTickets
WHERE jt.PrintType = 'CMYK'
-- ✅ CORRECT - Check TicketNotes
WHERE jt.TicketNotes LIKE '%CMYK%'
```

---

### **Mistake 2: Forgetting [Desc] Brackets**

```sql
-- ❌ WRONG - Desc without brackets
SELECT Desc FROM PaperSize
-- Error: Incorrect syntax near the keyword 'Desc'

-- ✅ CORRECT - Use [Desc] with brackets
SELECT [Desc] FROM PaperSize

-- ❌ WRONG - Alias without brackets
SELECT jtype.Desc FROM JobType jtype
-- ✅ CORRECT - Brackets required
SELECT jtype.[Desc] FROM JobType jtype

-- ❌ WRONG - WHERE clause without brackets
WHERE pt.Desc = 'Satin'
-- ✅ CORRECT - Brackets required
WHERE pt.[Desc] = 'Satin'
```

**Applies to:** PaperSize, JobType, PaperType, JobStage, GSM
**Exception:** BindType uses `BindTypeDesc` (no brackets needed)

---

### **Mistake 3: Misunderstanding ColourStatus**

```sql
-- ❌ WRONG - Treating as text color
WHERE jt.ColourStatus = 'Red'
-- Error: Conversion failed when converting the varchar value 'Red' to data type int

-- ✅ CORRECT - JOIN to get description
SELECT cs.ColourDesc
FROM JobTickets jt
LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
WHERE cs.ColourDesc = 'Before Lunch Today'

-- ❌ WRONG - Assuming it's print color (CMYK/PMS)
WHERE jt.ColourStatus = 'CMYK'
-- ✅ CORRECT - Understanding: It's production deadline urgency
SELECT cs.ColourDesc, cs.OrderPriority
FROM JobTickets jt
LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
WHERE cs.OrderPriority <= 2  -- Highest urgency (Before Lunch Today, Before COB Today)
```

**Remember:**
- 1 = Hold (lowest priority)
- 2 = Before Lunch Today (highest priority)
- 7 = Timely Manner (normal priority)

---

### **Mistake 4: Not Joining Orders for Dates**

```sql
-- ❌ WRONG - DateCreated doesn't exist in JobTickets
SELECT jt.TicketID
FROM JobTickets jt
WHERE jt.DateCreated > '2025-01-01'
-- Error: Invalid column name 'DateCreated'

-- ✅ CORRECT - JOIN Orders for dates
SELECT jt.TicketID
FROM JobTickets jt
JOIN Orders o ON jt.OrderID = o.OrderID
WHERE o.OrderDate > '2025-01-01'
```

---

### **Mistake 5: Using o.Status for Urgency**

```sql
-- ❌ WRONG - Status column doesn't exist
WHERE o.Status = 'Urgent'
-- Error: Invalid column name 'Status'

-- ✅ CORRECT - Use Urgent bit field
WHERE o.Urgent = 1

-- ✅ CORRECT - Combine Urgent flag with ColourStatus priority
SELECT o.OrderID, cs.ColourDesc, cs.OrderPriority
FROM Orders o
JOIN JobTickets jt ON o.OrderID = jt.OrderID
LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
WHERE o.Urgent = 1 OR cs.OrderPriority <= 2
ORDER BY cs.OrderPriority ASC
```

---

## ✅ BEST PRACTICES

### **1. Always Use [Desc] Brackets**

```sql
-- ✅ CORRECT - Brackets for all [Desc] columns
SELECT ps.[Desc], pt.[Desc], jtype.[Desc], gsm.[DESC]

-- ❌ WRONG - No brackets
SELECT ps.Desc, pt.Desc, jtype.Desc
```

**Exception:** BindType uses `BindTypeDesc` (no brackets needed)

---

### **2. Always JOIN Orders for Dates**

```sql
-- ✅ CORRECT - Orders.OrderDate is ONLY date field
FROM JobTickets jt
JOIN Orders o ON jt.OrderID = o.OrderID
WHERE o.OrderDate > '2025-01-01'

-- ❌ WRONG - JobTickets has NO date columns
FROM JobTickets jt
WHERE jt.DateCreated > '2025-01-01'  -- Doesn't exist!
```

---

### **3. Always JOIN ColourStatus for Deadlines**

```sql
-- ✅ CORRECT - JOIN to get human-readable description
LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
SELECT cs.ColourDesc, cs.OrderPriority

-- ❌ WRONG - Treating as text value
WHERE jt.ColourStatus = 'Red'  -- It's an int FK!
```

---

### **4. Use Invoiced (bit) for Status**

```sql
-- ✅ CORRECT - Use Invoiced bit field
WHERE o.Invoiced = 1    -- Invoiced orders
WHERE o.Invoiced = 0    -- Pending orders

-- ❌ WRONG - Status column doesn't exist
WHERE o.Status = 'Complete'
```

---

### **5. Calculate Order Totals**

```sql
-- ✅ CORRECT - Sum JobTickets.Cost
SELECT SUM(jt.Cost) AS OrderTotal
FROM JobTickets jt
WHERE jt.OrderID = 12345
GROUP BY jt.OrderID

-- ❌ WRONG - TotalCost doesn't exist
SELECT o.TotalCost
```

---

### **6. TicketNotes is Primary Source**

```sql
-- ✅ CORRECT - Check TicketNotes for full specifications
SELECT jt.TicketNotes  -- Contains complete job details
WHERE jt.TicketNotes LIKE '%sticker%'

-- ✅ CORRECT - ShortJobDesc is just a summary
SELECT jt.ShortJobDesc  -- Quick overview only
```

---

### **7. Use LEFT JOIN for Nullable FKs**

```sql
-- ✅ CORRECT - NULL-safe joins
LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
LEFT JOIN JobStage js ON jt.StageID = js.StageID
```

---

### **8. Concatenate User Names**

```sql
-- ✅ CORRECT - Full name from Users table
u.FirstName + ' ' + u.LastName AS CreatedBy

-- ❌ WRONG - UserName is system username, not display name
u.UserName
```

---

### **9. Filter by Production Stage**

```sql
-- ✅ CORRECT - Filter by stage description
LEFT JOIN JobStage js ON jt.StageID = js.StageID
WHERE js.[Desc] IN ('ArtOnly', 'ArtAndPrint')

-- ✅ CORRECT - Exclude completed/on-hold
WHERE js.[Desc] NOT IN ('JobComplete', 'OnHold')
```

---

### **10. Order by Urgency**

```sql
-- ✅ CORRECT - Sort by deadline priority
ORDER BY cs.OrderPriority ASC, o.DateRequired ASC
-- Priority 1 (Before Lunch Today) first
-- Priority 7 (Hold) last
```

---

## 📊 QUICK REFERENCE CHEAT SHEET

| **Need** | **Don't Use** | **Use Instead** |
|----------|---------------|-----------------|
| Order status | `o.Status` | `o.Invoiced` (bit: 0 or 1) |
| Order total | `o.TotalCost` | `SUM(jt.Cost)` |
| Job date | `jt.DateCreated` | `o.OrderDate` (JOIN Orders) |
| Print type | `jt.PrintType` | `jt.TicketNotes` (search text) |
| Deadline | `jt.ColourStatus` value | `JOIN ColourStatus cs` → `cs.ColourDesc` |
| Column named "Desc" | `Desc` | `[Desc]` (square brackets) |
| BindType description | `bt.[Desc]` | `bt.BindTypeDesc` (no brackets) |
| Full job details | `jt.ShortJobDesc` only | `jt.TicketNotes` (primary source) |
| Paper dimensions | `ps.Width`, `ps.Height` | `ps.[Desc]` (e.g., "BC - 90x55") |

---

## 🎯 ALL 68 TABLES IN FRED

```
Core Job Management (5):
- Orders               -- Main order records (16 columns)
- JobTickets          -- Individual job specifications (70 columns)
- JobType             -- Job categories (Business Cards/Flyers/etc.)
- JobStage            -- Production workflow stages (ArtOnly/Complete/etc.)
- ColourStatus        -- Production deadline urgency system

Materials (5):
- PaperSize           -- Paper sizes (A4/BC-90x55/etc.)
- PaperType           -- Paper types (Satin/Bond/Vinyl/etc.)
- GSM                 -- Paper weights (350/100/80/etc.)
- BindType            -- Binding types (None/Spiral/etc.)
- PadPaperColour      -- Carbonless form colors

Customers (2):
- Clients             -- Customer information and history
- Business            -- Business divisions (Print/Publishing/Signs)

User Management (3):
- Users               -- System users and creators
- UserTypes           -- User role definitions
- ShippingType        -- Delivery methods (Courier/Freight/Post/etc.)

Publishing System (10):
- PublishingProject
- PublishingTask
- PublishingTaskType
- PublishingCase
- PublishingCaseType
- PublishingMiscTask
- NiagraPublication
- NiagraPublicationState
- NiagraJobTickets
- NiagraTicketStage

Quoting System (18):
- Quote_DigitalClicks
- Quote_DigitalFinishSizes
- Quote_DigitalStocks
- Quote_DigitalStockType
- Quote_GenericSetting
- Quote_MarginsProduct
- Quote_PBBExtraBookScale
- Quote_PBBPerBookBindCost
- Quote_PBBPPMarkup
- Quote_ProfitMargins
- Quote_RidgedProfitMargin
- Quote_RidgedStocks
- Quote_RidgedStockType
- Quote_RollStocks
- Quote_RollStockType

Website Integration (10):
- WebsiteOrderInfo
- WebSiteProduct
- WebSiteProductType
- WebSiteProdOptions
- WebSiteProdOptionSelection
- Website_PerItemPricingScale
- Website_PerSQMPricingScale
- WebSiteCorpDiscount
- WebSiteCorpRoles
- WebsiteSetQTYPricing

Legacy/Other (15):
- ai_extracted_jobs
- APGClientList
- APGJobStage
- APGJobTicket
- APIOptionType
- AuditBusiness
- AuditItemType
- AuditLog
- ClientCommisions
- Notes
- NoteType
- PerfectBB_JobType
- PerfectBBOrders
- PerfectBBStage
- PerItemProductOption
- sysdiagrams
- tempJobTickets
- tempOrders
```

---

## 🔄 MIGRATION NOTES

### **From Old Schema to New:**

```diff
# Column Changes:
- o.Status (nvarchar)        → + o.Invoiced (bit: 0 or 1)
- o.TotalCost (decimal)      → + SUM(jt.Cost) GROUP BY OrderID
- jt.DateCreated (date)      → + o.OrderDate (must JOIN Orders)
- jt.PrintType (nvarchar)    → + jt.TicketNotes (text search)
- jt.ColourStatus = 'text'   → + jt.ColourStatus (int FK to ColourStatus)

# Syntax Changes:
- Desc                       → + [Desc] (brackets required)
- bt.[Desc]                  → + bt.BindTypeDesc (exception: no brackets)

# Conceptual Changes:
- ColourStatus = print color → + ColourStatus = deadline urgency (1-7)
- Dates in JobTickets        → + Dates ONLY in Orders table
- Width/Height in PaperSize  → + Only SizeID and [Desc] exist
```

---

## ✅ VALIDATION TEST

**This query works and demonstrates all corrections:**

```sql
SELECT TOP 3
    -- Order info
    o.OrderID,
    o.ClientName,
    o.OrderDate,                                     -- ✅ Not jt.DateCreated
    o.Invoiced,                                      -- ✅ Not o.Status
    
    -- Job ticket info
    jt.ShortJobDesc,
    jt.Cost,                                         -- ✅ Not o.TotalCost
    
    -- Reference data
    jtype.[Desc] AS JobType,                         -- ✅ [Desc] with brackets
    cs.ColourDesc AS Deadline,                       -- ✅ Deadline not print color
    bt.BindTypeDesc AS BindType,                     -- ✅ BindTypeDesc not [Desc]
    u.FirstName + ' ' + u.LastName AS CreatedBy      -- ✅ Concatenated name
    
FROM Orders o
JOIN JobTickets jt ON o.OrderID = jt.OrderID        -- ✅ JOIN for dates
LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
LEFT JOIN Users u ON o.UserID = u.UserID
WHERE o.ClientName LIKE '%Gerardo%'
ORDER BY o.OrderDate DESC                            -- ✅ o.OrderDate (only date field)
```

**✅ Result:** 3 rows returned successfully with all correct columns

---

## 📝 DOCUMENT VERSION

**Version:** 2.0 (Corrected & Validated)  
**Date:** December 1, 2025  
**Verified Against:** Fred production database (FredDEV @ 3.25.76.138\INHPSQLSERVER)  
**Status:** ✅ Validated with real queries  
**Purpose:** AI Agent tool implementation guidance for InHouse Print system

---

## 🔗 INTEGRATION WITH AI AGENT TOOLS

### **Tool Implementation Guidelines**

**When building tools that query FRED database:**

1. **ALWAYS JOIN Orders for dates** - JobTickets has NO date columns
2. **ALWAYS use [Desc] brackets** - Except BindType which uses BindTypeDesc
3. **NEVER reference Status/TotalCost/DateCreated/PrintType** - These columns don't exist
4. **ALWAYS understand ColourStatus** - It's deadline urgency (1-7), not print color
5. **ALWAYS check TicketNotes** - Primary source when structured columns are NULL
6. **ALWAYS use TOP N** - Prevent massive result sets (TOP 20 recommended)
7. **ALWAYS use LEFT JOIN** - Many foreign keys are nullable

### **Tool Schema Integration**

Reference this schema in tool descriptions:
- `inhouse_database_guide()` - Embed schema excerpts in tool guidance
- `inhouse_execute_sql()` - Validate SQL against this schema before execution
- `inhouse_get_query_library_catalog()` - Pre-built queries follow these patterns

---

**END OF CONSOLIDATED GUIDE v2.0**
