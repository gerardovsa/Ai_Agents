# InHouse Database Guide Corrections - Dec 4, 2025

## Testing Methodology

Executed systematic testing of the `inhouse_database_guide()` schema documentation by running actual SQL queries against the InHouse Fred database to verify:
1. Column existence
2. Table existence  
3. SQL pattern validity
4. JOIN relationships

## Critical Errors Found

### ❌ ERROR 1: Orders.Status Column (DOES NOT EXIST)
**Guide Claimed:** `Status: "nvarchar(50) - Order status"`

**Reality:** Column does not exist in Orders table

**Test Result:**
```sql
SELECT o.Status FROM Orders o
-- Error: Invalid column name 'Status'
```

**Actual Orders Columns:**
- OrderID ✅
- ClientName ✅
- OrderDate ✅
- **Invoiced** (bit) - Use this for order status
- **ReadToInvoice** (bit) - Ready to invoice flag
- Urgent (bit)
- CustomerPickup (bit)
- InvoiceNumber, InvoiceDate, DateRequired

**Fix Applied:** Removed Status from schema, documented Invoiced flag as status indicator

---

### ❌ ERROR 2: Orders.TotalCost Column (DOES NOT EXIST)
**Guide Claimed:** `TotalCost: "decimal(10,2) - Order total"`

**Reality:** Column does not exist in Orders table

**Test Result:**
```sql
SELECT o.TotalCost FROM Orders o
-- Error: Invalid column name 'TotalCost'
```

**Correct Approach:**
```sql
SELECT SUM(jt.Cost) AS TotalCost 
FROM JobTickets jt 
WHERE jt.OrderID = ?
```

**Fix Applied:** Removed TotalCost from schema, documented calculation method from JobTickets

---

### ❌ ERROR 3: ReorderAlerts Table (WRONG DATABASE!)
**Guide Claimed:** Table exists in InHouse Fred database with schema

**Reality:** ReorderAlerts is in **Supabase PostgreSQL** (`stock_data.reorderalerts`), NOT InHouse Fred

**Test Result:**
```sql
SELECT * FROM ReorderAlerts
-- Error: Invalid object name 'ReorderAlerts'
```

**Database Architecture Discovery:**
```
InHouse Fred Database (SQL Server - LIVE):
├── Orders ✅
├── JobTickets ✅
├── PaperSize ✅
├── BindType ✅
└── Clients ✅

Stock Database (Supabase PostgreSQL - NEW):
├── stock_data.reorderalerts ✅
├── stock_data.stocklevels ✅
├── stock_data.consumableinventory ✅
└── stock_data.corflutematerials ✅
```

**Fix Applied:** 
- Removed ReorderAlerts from InHouse schema
- Added database architecture warning
- Documented that stock tables are in separate Supabase database
- Clarified you CANNOT JOIN between InHouse and Supabase in a single query

---

### ❌ ERROR 4: Guide's Own SQL Pattern Failed
**Guide Provided:**
```sql
SELECT TOP 20
    o.OrderID, o.ClientName, o.OrderDate, o.Status,  -- ❌ Status doesn't exist!
    jt.TicketNotes, jt.QTY, jt.Cost,
    ps.[Desc] AS PaperSize,
    bt.BindTypeDesc AS BindType
FROM Orders o
JOIN JobTickets jt ON o.OrderID = jt.OrderID
LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
WHERE o.ClientName LIKE '%customer%'
ORDER BY o.OrderDate DESC
```

**Error:** `Invalid column name 'Status'`

**Corrected Pattern:**
```sql
SELECT TOP 20
    o.OrderID, 
    o.ClientName, 
    o.OrderDate,
    o.Invoiced,      -- ✅ Use this instead of Status
    o.Urgent,
    jt.TicketNotes, 
    jt.QTY, 
    jt.Cost,
    ps.[Desc] AS PaperSize,
    bt.BindTypeDesc AS BindType
FROM Orders o
JOIN JobTickets jt ON o.OrderID = jt.OrderID
LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
WHERE o.ClientName LIKE '%customer%'
ORDER BY o.OrderDate DESC
```

**Fix Applied:** Updated SQL patterns with tested, working queries

---

## Verified Correct Information ✅

### PaperSize Table Structure
```sql
SELECT TOP 5 * FROM PaperSize
-- Returns: SizeID, Desc
```
✅ Guide correctly states: Use `ps.[Desc]`, NO Width/Height columns

### BindType Table Structure
```sql
SELECT TOP 5 * FROM BindType
-- Returns: BindID, BindTypeDesc
```
✅ Guide correctly states: Use `bt.BindTypeDesc`, NOT `bt.[Desc]`

### JobTickets Table Structure
```sql
SELECT TOP 3 * FROM JobTickets
-- Returns: TicketID, OrderID, QTY, Cost, TicketNotes, ColourStatus, etc.
-- Does NOT have: DateCreated
```
✅ Guide correctly states: NO DateCreated column, must JOIN Orders for dates

### SQL Server Syntax
```sql
SELECT * FROM Orders LIMIT 5
-- Error: Incorrect syntax near '5'
```
✅ Guide correctly states: Use TOP, not LIMIT (SQL Server syntax)

---

## Complete Changes Applied

### 1. Orders Table Schema
**Removed:**
- Status (doesn't exist)
- TotalCost (doesn't exist)

**Added:**
- CustomerMYOB_ID
- ReadToInvoice (bit)
- Invoiced (bit) - **USE THIS for order status**
- CustomerPickup (bit)
- Urgent (bit)
- DateRequired
- InvoiceNumber, InvoiceDate

### 2. ReorderAlerts Removal
**Removed entire section from InHouse schema**

**Added:**
- Clients table schema (exists in InHouse)
- Database architecture warning section
- Clarification that stock tables are in Supabase

### 3. SQL Patterns Updated
**Replaced broken pattern with tested queries:**
- basic_order_query (removed o.Status, uses o.Invoiced)
- Added recent_orders_with_client_info pattern

**Removed:**
- stock_query (uses ReorderAlerts which doesn't exist)

### 4. Common Mistakes Updated
**Updated with actual test results:**
- "Querying Status from Orders" - confirmed doesn't exist
- "Querying TotalCost from Orders" - confirmed doesn't exist
- "Querying ReorderAlerts" - confirmed wrong database

**Added frequency notes:**
- "CONFIRMED BY TESTING - Dec 2025"
- "Guide's own SQL pattern failed"

### 5. Mandatory Syntax Rules
**Updated:**
- ❌ DO NOT use o.Status - use o.Invoiced
- ❌ DO NOT use o.TotalCost - calculate from JobTickets
- ❌ DO NOT query ReorderAlerts - in Supabase, not InHouse
- ✅ Verify column existence - don't assume

---

## Impact

### Before Fixes:
- Guide's SQL pattern immediately failed ❌
- Documentation claimed 2 non-existent columns in Orders
- Documentation claimed 1 non-existent table (ReorderAlerts)
- Users would copy-paste broken SQL
- 3-4 failed query attempts before discovering errors

### After Fixes:
- SQL patterns are tested and working ✅
- All documented columns verified to exist ✅
- Database architecture clarified (InHouse vs Supabase) ✅
- Common mistakes section reflects real testing ✅
- Users get working queries on first attempt ✅

---

## Testing Proof

### Test 1: Orders Structure Verification ✅
```sql
SELECT TOP 5 * FROM Orders
-- Confirmed: No Status, No TotalCost
-- Confirmed: Has Invoiced, ReadToInvoice, Urgent, OrderDate, etc.
```

### Test 2: ReorderAlerts Non-Existence ✅
```sql
SELECT * FROM ReorderAlerts
-- Error: Invalid object name 'ReorderAlerts'
-- Confirms table not in InHouse database
```

### Test 3: Database Table List ✅
```sql
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'
-- Returns 68 tables
-- Confirmed: Orders, JobTickets, PaperSize, BindType exist
-- Confirmed: ReorderAlerts does NOT exist
```

### Test 4: SQL Syntax Validation ✅
```sql
SELECT * FROM Orders LIMIT 5
-- Error: Incorrect syntax near '5'
-- Confirms SQL Server requires TOP, not LIMIT
```

---

## Database Architecture Clarification

### InHouse Fred Database (SQL Server)
**Purpose:** Production orders, jobs, clients, paper specifications

**Tables:**
- Orders (order header data)
- JobTickets (job specifications)
- PaperSize (paper size lookup)
- BindType (binding type lookup)
- Clients (customer data)
- 68 total tables

**Access:** `inhouse_execute_sql()` tool

---

### Stock Database (Supabase PostgreSQL)
**Purpose:** Inventory management, stock levels, reorder alerts

**Schema:** `stock_data.*`

**Tables:**
- reorderalerts
- stocklevels  
- consumableinventory
- corflutematerials
- shopify_orders, shopify_products, etc.

**Access:** Separate Supabase connection (NOT through inhouse_execute_sql)

**Key Point:** You CANNOT JOIN between InHouse and Supabase in a single query - they are separate database servers!

---

## Files Modified

```
c:\Users\gpoli\GIT\AI_agents\UI\modules_external\inhouse-print\implementations\inhouse_guide_wrapper.py
```

**Function:** `inhouse_database_guide()`

**Lines Changed:** ~100+ lines (schema definitions, SQL patterns, common mistakes, syntax rules)

---

## Recommendation

✅ **Guide is now accurate** based on real database testing

✅ **SQL patterns work** without modification

✅ **Database architecture documented** (two separate databases)

✅ **Common mistakes reflect reality** (tested Dec 2025)

---

## Next Steps

1. ✅ Test guide corrections with real queries
2. ⏳ Create separate Supabase Stock Database guide
3. ⏳ Document cross-database query patterns (if needed)
4. ⏳ Update any dependent documentation referencing old schema

---

**Testing Date:** December 4, 2025  
**Tester:** GitHub Copilot (Claude Sonnet 4.5)  
**Method:** Systematic SQL execution against InHouse Fred production database  
**Result:** 3 critical errors found and fixed, guide now reflects actual database structure
