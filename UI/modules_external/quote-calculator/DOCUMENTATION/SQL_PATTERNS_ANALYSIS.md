# Query Library SQL Patterns Analysis

**Generated**: December 2, 2025  
**Source**: `backend/query_library.py` (60 queries analyzed)  
**Database**: FRED (SQL Server) @ 3.25.76.138\INHPSQLSERVER

---

## 📊 SQL Pattern Summary

### Core Patterns Identified:

1. **Time-Based Filtering** (45 queries use this)
2. **Aggregation with GROUP BY** (52 queries)
3. **Common Table Expressions (CTEs)** (23 queries)
4. **Window Functions** (12 queries)
5. **Dynamic TOP N** (18 queries)
6. **JOIN Patterns** (all queries use INNER/LEFT JOINs)
7. **Date Calculations** (DATEADD, DATEDIFF in 40 queries)
8. **CASE Statements for Segmentation** (15 queries)

---

## 🔍 Pattern Analysis by Category

### 1. Time-Based Filtering Pattern

**Used in**: 75% of all queries (45/60)

**Standard Pattern**:
```sql
WHERE o.OrderDate >= DATEADD(MONTH, -@months, GETDATE())
```

**Variations**:
```sql
-- Days lookback
WHERE o.OrderDate >= DATEADD(DAY, -@days, GETDATE())

-- Year lookback
WHERE o.OrderDate >= DATEADD(YEAR, -@years, GETDATE())

-- Weeks lookback
WHERE o.OrderDate >= DATEADD(WEEK, -@weeks, GETDATE())

-- Performance optimized (using TicketID instead of dates)
WHERE jt.TicketID >= @min_ticket_id
```

**Why This Matters**:
- ✅ Consistent parameter naming (`months`, `days`, `weeks`)
- ✅ Always uses DATEADD() function
- ✅ Performance optimization available via `min_ticket_id`
- ✅ Server-side date calculation (GETDATE())

---

### 2. Aggregation with GROUP BY Pattern

**Used in**: 87% of all queries (52/60)

**Standard Aggregations**:
```sql
SELECT 
    o.ClientName,
    COUNT(DISTINCT o.OrderID) AS OrderCount,
    SUM(jt.Cost) AS TotalRevenue,
    AVG(jt.Cost) AS AvgOrderValue,
    MAX(o.OrderDate) AS LastOrderDate,
    MIN(o.OrderDate) AS FirstOrderDate
FROM Orders o
INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
GROUP BY o.ClientName
```

**Common Aggregation Functions**:
- `COUNT(DISTINCT ...)` - Unique counts (orders, customers)
- `SUM(...)` - Total revenue, quantities, costs
- `AVG(...)` - Average prices, values, times
- `MAX(...)` / `MIN(...)` - Date ranges, extremes
- `CAST(...* 100.0 / ... AS DECIMAL(5,2))` - Percentage calculations

**Key Principle**: Always use explicit column types in GROUP BY (avoid SELECT *)

---

### 3. Common Table Expressions (CTEs)

**Used in**: 38% of queries (23/60)

**Pattern 1: Single CTE for Base Data**:
```sql
WITH CustomerData AS (
    SELECT 
        o.ClientName,
        COUNT(*) AS OrderCount,
        SUM(jt.Cost) AS TotalRevenue
    FROM Orders o
    INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
    WHERE o.OrderDate >= DATEADD(MONTH, -12, GETDATE())
    GROUP BY o.ClientName
)
SELECT 
    ClientName,
    OrderCount,
    TotalRevenue,
    OrderCount * 100.0 / SUM(OrderCount) OVER() AS Percentage
FROM CustomerData
ORDER BY TotalRevenue DESC
```

**Pattern 2: Multiple CTEs for Complex Analysis**:
```sql
WITH FirstOrders AS (
    -- Get customer first order dates
    SELECT ClientName, MIN(OrderDate) AS FirstOrderDate
    FROM Orders
    GROUP BY ClientName
),
CustomerOrders AS (
    -- Join with all orders to calculate tenure
    SELECT 
        fo.ClientName,
        o.OrderDate,
        DATEDIFF(MONTH, fo.FirstOrderDate, o.OrderDate) AS MonthsSinceFirst
    FROM FirstOrders fo
    INNER JOIN Orders o ON fo.ClientName = o.ClientName
)
SELECT ClientName, MAX(MonthsSinceFirst) AS CustomerTenureMonths
FROM CustomerOrders
GROUP BY ClientName
```

**Benefits of CTEs**:
- ✅ Improved readability vs nested subqueries
- ✅ Can be referenced multiple times in main query
- ✅ Better for complex multi-step calculations
- ✅ Easier to debug and validate intermediate results

---

### 4. Window Functions Pattern

**Used in**: 20% of queries (12/60)

**Pattern 1: Percentage of Total with OVER()**:
```sql
SELECT 
    ProductType,
    OrderCount,
    OrderCount * 100.0 / SUM(OrderCount) OVER() AS PercentageOfTotal
FROM ProductSummary
```

**Pattern 2: Row Numbering with ROW_NUMBER()**:
```sql
SELECT 
    ClientName,
    TotalRevenue,
    ROW_NUMBER() OVER (ORDER BY TotalRevenue DESC) AS Rank
FROM CustomerRevenue
```

**Pattern 3: Running Totals with SUM() OVER()**:
```sql
SELECT 
    OrderDate,
    DailyRevenue,
    SUM(DailyRevenue) OVER (ORDER BY OrderDate) AS RunningTotal
FROM DailySales
```

**Pattern 4: Partitioned Calculations**:
```sql
SELECT 
    ProductType,
    ClientName,
    OrderCount,
    AVG(OrderCount) OVER (PARTITION BY ProductType) AS AvgOrdersForProduct
FROM CustomerProductOrders
```

**Why Window Functions**:
- ✅ Eliminate self-joins for ranking/percentage calculations
- ✅ More efficient than subqueries for running totals
- ✅ Required for cohort retention analysis
- ✅ Clean syntax for partition-based aggregations

---

### 5. Dynamic TOP N Pattern

**Used in**: 30% of queries (18/60)

**Standard Implementation**:
```sql
SELECT TOP @top_n
    o.ClientName,
    SUM(jt.Cost) AS TotalRevenue
FROM Orders o
INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
GROUP BY o.ClientName
ORDER BY TotalRevenue DESC
```

**Parameter Definition**:
```python
"top_n": {
    "type": "integer",
    "description": "Number of top customers to return (default: 20)",
    "default": 20,
    "min": 5,
    "max": 100
}
```

**Key Points**:
- Always paired with ORDER BY clause
- Default values typically 10-50
- Min/max constraints prevent runaway queries
- Used for: Top customers, products, specifications

---

### 6. JOIN Patterns

**Used in**: 100% of queries (60/60)

**Pattern 1: Core Orders → JobTickets Join**:
```sql
FROM Orders o
INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
WHERE jt.Cost IS NOT NULL  -- Exclude zero-cost or NULL
```

**Pattern 2: Reference Table Lookups (LEFT JOIN)**:
```sql
FROM JobTickets jt
LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindTypeID
```

**Why LEFT JOIN for Reference Tables**:
- ✅ Prevents data loss if reference data missing
- ✅ Shows NULL when lookup fails (easier to debug)
- ✅ Required for JobTickets with no PaperSize, GSM, etc.

**Pattern 3: Stage/Workflow Join**:
```sql
FROM JobTickets jt
INNER JOIN WorkflowStages ws ON jt.CurrentWorkflowStageID = ws.StageID
WHERE ws.StageID IN (4, 5, 6, 7, 8, 11)  -- Active production stages
```

**CRITICAL**: Always filter out completed stages (not stage 1-3, 9-10 unless specifically requested)

---

### 7. Date Calculation Patterns

**Used in**: 67% of queries (40/60)

**Pattern 1: Days Since Event**:
```sql
DATEDIFF(DAY, o.OrderDate, GETDATE()) AS DaysSinceOrder
DATEDIFF(DAY, MAX(o.OrderDate), GETDATE()) AS DaysSinceLastOrder
```

**Pattern 2: Date Formatting**:
```sql
FORMAT(o.OrderDate, 'yyyy-MM') AS YearMonth
FORMAT(o.OrderDate, 'yyyy-MM-dd') AS OrderDate
```

**Pattern 3: Day of Week Analysis**:
```sql
DATENAME(WEEKDAY, o.OrderDate) AS DayOfWeek
DATEPART(WEEKDAY, o.OrderDate) AS DayNumber
```

**Pattern 4: Date Range Calculations**:
```sql
-- Last 6 months
WHERE o.OrderDate >= DATEADD(MONTH, -6, GETDATE())

-- Next 7 days
WHERE jt.DateRequired BETWEEN GETDATE() AND DATEADD(DAY, 7, GETDATE())

-- Overdue jobs
WHERE jt.DateRequired < GETDATE()
  AND ws.StageID NOT IN (1, 2, 3)  -- Not completed
```

**Best Practices**:
- Always use GETDATE() for server-side date (not client-side)
- Use DATEDIFF() for day calculations (not arithmetic)
- Use FORMAT() for display, not WHERE clauses (performance)
- Always consider timezone implications (all dates in server time)

---

### 8. CASE Statement Segmentation

**Used in**: 25% of queries (15/60)

**Pattern 1: Customer Segmentation**:
```sql
CASE 
    WHEN OrderCount = 1 THEN 'One-time'
    WHEN OrderCount BETWEEN 2 AND 3 THEN 'Occasional'
    WHEN OrderCount BETWEEN 4 AND 10 THEN 'Regular'
    ELSE 'Frequent'
END AS Segment
```

**Pattern 2: Urgency Color Coding**:
```sql
CASE 
    WHEN cs.UrgencyLevel <= 2 THEN 'red'      -- Critical
    WHEN cs.UrgencyLevel = 3 THEN 'orange'    -- Urgent
    WHEN cs.UrgencyLevel = 4 THEN 'yellow'    -- Rush
    ELSE 'green'                              -- Standard
END AS UrgencyColor
```

**Pattern 3: Quantity Ranges**:
```sql
CASE 
    WHEN jt.QTY BETWEEN 1 AND 100 THEN '1-100'
    WHEN jt.QTY BETWEEN 101 AND 500 THEN '101-500'
    WHEN jt.QTY BETWEEN 501 AND 1000 THEN '501-1000'
    ELSE '1000+'
END AS QuantityRange
```

**Pattern 4: Boolean Flag Translation**:
```sql
CASE WHEN jt.FrontCelloGloss = 1 THEN 'Yes' ELSE 'No' END AS HasCelloGloss
```

**Benefits**:
- ✅ Creates human-readable segments
- ✅ Enables grouping by categories
- ✅ Simplifies dashboard filtering
- ✅ Consistent across all queries

---

## 🎯 Advanced SQL Patterns

### 1. Cohort Retention Analysis

**Query**: `customer_retention_cohort`

```sql
WITH FirstOrders AS (
    SELECT 
        o.ClientName,
        MIN(o.OrderDate) AS FirstOrderDate,
        FORMAT(MIN(o.OrderDate), 'yyyy-MM') AS CohortMonth
    FROM Orders o
    GROUP BY o.ClientName
),
CustomerOrders AS (
    SELECT 
        fo.ClientName,
        fo.CohortMonth,
        o.OrderDate,
        DATEDIFF(MONTH, fo.FirstOrderDate, o.OrderDate) AS MonthsSinceFirst
    FROM FirstOrders fo
    INNER JOIN Orders o ON fo.ClientName = o.ClientName
)
SELECT 
    CohortMonth,
    COUNT(DISTINCT ClientName) AS CustomersCount,
    COUNT(DISTINCT CASE WHEN MonthsSinceFirst > 0 THEN ClientName END) AS ReturningCustomers,
    CAST(COUNT(DISTINCT CASE WHEN MonthsSinceFirst > 0 THEN ClientName END) * 100.0 / 
         COUNT(DISTINCT ClientName) AS DECIMAL(5,2)) AS RetentionRate
FROM CustomerOrders
WHERE CohortMonth >= FORMAT(DATEADD(MONTH, -12, GETDATE()), 'yyyy-MM')
GROUP BY CohortMonth
ORDER BY CohortMonth DESC
```

**Why This Pattern**:
- Step 1: Identify each customer's first order (cohort assignment)
- Step 2: Calculate months since first order for all orders
- Step 3: Aggregate to show retention rate per cohort
- Uses COUNT(DISTINCT CASE WHEN) for conditional counting

---

### 2. Priority Scoring Algorithm

**Query**: `priority_work_queue`

```sql
-- Priority Score = (Urgency * 40) + (DaysOverdue * 30) + (JobValue/1000 * 20) + (CustomerTier * 10)
SELECT 
    jt.TicketID,
    o.ClientName,
    jt.TicketNotes AS JobDescription,
    CASE 
        WHEN jt.DateRequired < GETDATE() THEN 
            (cs.Priority * 40) + 
            (DATEDIFF(DAY, jt.DateRequired, GETDATE()) * 30) +
            ((jt.Cost / 1000.0) * 20) + 
            (CASE 
                WHEN SUM(jt_hist.Cost) OVER (PARTITION BY o.ClientName) > 50000 THEN 10
                WHEN SUM(jt_hist.Cost) OVER (PARTITION BY o.ClientName) > 20000 THEN 7
                ELSE 5
            END)
        ELSE 
            (cs.Priority * 40) + 
            ((jt.Cost / 1000.0) * 20)
    END AS PriorityScore
FROM JobTickets jt
INNER JOIN Orders o ON jt.OrderID = o.OrderID
LEFT JOIN ColourStatus cs ON jt.ColourStatusID = cs.ColourStatusID
LEFT JOIN JobTickets jt_hist ON o.ClientName = jt_hist.ClientName  -- For customer tier calc
ORDER BY PriorityScore DESC
```

**Why This Pattern**:
- Multi-factor weighting (urgency, lateness, value, customer)
- Window function for customer tier calculation
- Handles overdue vs upcoming differently
- Returns actionable priority queue

---

### 3. Bottleneck Detection with Capacity Analysis

**Query**: `bottleneck_detection_advanced`

```sql
WITH StageWorkload AS (
    SELECT 
        ws.StageID,
        ws.StageDescription,
        COUNT(*) AS JobCount,
        SUM(CASE 
            WHEN jt.QTY <= 500 THEN 0.5
            WHEN jt.QTY BETWEEN 501 AND 2000 THEN 2.0
            ELSE 4.0
        END) AS TotalHoursNeeded,
        AVG(DATEDIFF(DAY, jt.DateReceived, GETDATE())) AS AvgDaysInStage,
        SUM(CASE WHEN jt.DateRequired < GETDATE() THEN 1 ELSE 0 END) AS OverdueJobs
    FROM JobTickets jt
    INNER JOIN WorkflowStages ws ON jt.CurrentWorkflowStageID = ws.StageID
    WHERE jt.TicketID >= 72680  -- Recent tickets only
      AND ws.StageID IN (4,5,6,7,8,11)
    GROUP BY ws.StageID, ws.StageDescription
),
CapacityAnalysis AS (
    SELECT 
        *,
        8.0 AS HoursAvailable,  -- 8 hours per day per stage
        TotalHoursNeeded / 8.0 AS Utilization,
        CASE 
            WHEN TotalHoursNeeded / 8.0 > 0.85 THEN 1  -- Bottleneck flag
            ELSE 0
        END AS IsBottleneck,
        (TotalHoursNeeded / 8.0) * 100 AS BottleneckScore
    FROM StageWorkload
)
SELECT 
    StageID,
    StageDescription,
    IsBottleneck,
    BottleneckScore,
    JobCount,
    TotalHoursNeeded,
    HoursAvailable,
    Utilization,
    AvgDaysInStage,
    OverdueJobs,
    CASE 
        WHEN Utilization > 0.85 AND OverdueJobs > 0 THEN 'HIGH'
        WHEN Utilization > 0.85 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS DelayRisk,
    CASE 
        WHEN Utilization > 0.85 THEN 'Add capacity or prioritize jobs'
        WHEN AvgDaysInStage > 5 THEN 'Review workflow efficiency'
        ELSE 'No action needed'
    END AS RecommendedAction
FROM CapacityAnalysis
ORDER BY BottleneckScore DESC
```

**Why This Pattern**:
- Step 1: Calculate workload per stage (jobs + hours needed)
- Step 2: Compare to available capacity (8 hours/day)
- Step 3: Flag bottlenecks and recommend actions
- Uses job quantity to estimate production hours
- Considers both capacity utilization AND overdue jobs

---

### 4. Reorder Prediction with Historical Patterns

**Query**: `customer_reorder_prediction_business`

```sql
WITH CustomerHistory AS (
    SELECT 
        o.ClientName,
        MAX(o.OrderDate) AS LastOrderDate,
        AVG(DATEDIFF(DAY, 
            LAG(o.OrderDate) OVER (PARTITION BY o.ClientName ORDER BY o.OrderDate), 
            o.OrderDate
        )) AS AvgOrderCycle,
        COUNT(DISTINCT o.OrderID) AS TotalOrders,
        MAX(jt.TicketNotes) AS LastProduct,
        MAX(jt.Cost) AS LastOrderValue
    FROM Orders o
    INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
    WHERE o.OrderDate >= DATEADD(YEAR, -2, GETDATE())
      AND jtype.[Desc] NOT LIKE '%Perfect Bound%'  -- Exclude publishing
    GROUP BY o.ClientName
    HAVING COUNT(DISTINCT o.OrderID) >= 2  -- Repeat customers only
)
SELECT TOP 50
    ClientName,
    LastOrderDate,
    DATEDIFF(DAY, LastOrderDate, GETDATE()) AS DaysSinceLastOrder,
    AvgOrderCycle,
    DATEDIFF(DAY, LastOrderDate, GETDATE()) - AvgOrderCycle AS DaysOverdue,
    LastProduct,
    LastOrderValue,
    TotalOrders,
    CASE 
        WHEN DATEDIFF(DAY, LastOrderDate, GETDATE()) > AvgOrderCycle * 1.5 THEN 'High Risk'
        WHEN DATEDIFF(DAY, LastOrderDate, GETDATE()) > AvgOrderCycle THEN 'Overdue'
        ELSE 'On Track'
    END AS ReorderStatus
FROM CustomerHistory
WHERE DATEDIFF(DAY, LastOrderDate, GETDATE()) > 90  -- At least 90 days
  AND AvgOrderCycle IS NOT NULL
ORDER BY DaysOverdue DESC
```

**Why This Pattern**:
- Uses LAG() window function to calculate time between orders
- Calculates customer-specific reorder cycle
- Flags customers overdue based on their own pattern (not global average)
- Excludes book publishing (different cycle)
- Returns actionable list sorted by urgency

---

## 🚨 Critical SQL Patterns to Avoid

### ❌ **DON'T**: Use SELECT *
```sql
-- BAD
SELECT * FROM Orders o
INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID

-- GOOD
SELECT 
    o.OrderID,
    o.ClientName,
    jt.TicketID,
    jt.Cost
FROM Orders o
INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
```

**Why**: 
- SELECT * is slow (fetches unnecessary columns)
- Breaks if table schema changes
- Makes query results unpredictable
- Harder to debug and validate

---

### ❌ **DON'T**: Use Non-Existent Columns
```sql
-- BAD (Orders.Status doesn't exist!)
SELECT OrderID, Status, TotalCost
FROM Orders

-- GOOD
SELECT 
    o.OrderID,
    CASE WHEN o.Invoiced = 1 THEN 'Invoiced' ELSE 'Pending' END AS Status,
    SUM(jt.Cost) AS TotalCost
FROM Orders o
INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
GROUP BY o.OrderID, o.Invoiced
```

**Why**:
- `Orders.Status` doesn't exist (use `Orders.Invoiced` boolean)
- `Orders.TotalCost` doesn't exist (must SUM from JobTickets)
- See `INHOUSE_DATABASE_SCHEMA_V2.md` for correct column names

---

### ❌ **DON'T**: Use BindType.[Desc] Without Exception
```sql
-- BAD (BindType.[Desc] is keywords, needs brackets)
SELECT BindType.Desc AS BindingType
FROM JobTickets jt
LEFT JOIN BindType ON jt.BindTypeID = BindType.BindTypeID

-- GOOD (Use exception column BindTypeDesc)
SELECT BindType.BindTypeDesc AS BindingType
FROM JobTickets jt
LEFT JOIN BindType ON jt.BindTypeID = BindType.BindTypeID
```

**Why**:
- `[Desc]` is SQL keyword, requires brackets
- `BindType` table has exception: `BindTypeDesc` column (NOT `[Desc]`)
- All other reference tables use `[Desc]` with brackets

---

### ❌ **DON'T**: Filter on ColourStatus for Print Color
```sql
-- BAD (ColourStatus is deadline urgency, NOT print color!)
SELECT * FROM JobTickets
WHERE ColourStatusID = 1  -- This is NOT color printing!

-- GOOD
-- ColourStatus.Priority (1-5):
-- 1 = Urgent (before lunch)
-- 2 = Rush (same day)
-- 3 = Standard (2-3 days)
-- etc.
SELECT 
    jt.TicketID,
    cs.ColourStatus AS UrgencyLevel,
    cs.Priority AS UrgencyPriority
FROM JobTickets jt
LEFT JOIN ColourStatus cs ON jt.ColourStatusID = cs.ColourStatusID
```

**Why**:
- `ColourStatus` = deadline urgency (1-5 priority)
- NOT print color (CMYK vs single color)
- See schema v2.0 for clarification

---

## 📈 Performance Optimization Patterns

### 1. Use TicketID Filter Instead of Date Filter
```sql
-- SLOW (scans all dates)
WHERE o.OrderDate >= DATEADD(MONTH, -6, GETDATE())

-- FAST (indexed TicketID lookup)
WHERE jt.TicketID >= 72680  -- Approx last 6 months
```

**Why**: TicketID is auto-incrementing primary key (indexed), dates are not always indexed

---

### 2. Filter Early in CTEs
```sql
-- SLOW (filters after aggregation)
WITH AllData AS (
    SELECT * FROM JobTickets  -- Fetches everything
)
SELECT * FROM AllData WHERE TicketID >= 72680

-- FAST (filters before aggregation)
WITH RecentData AS (
    SELECT * FROM JobTickets 
    WHERE TicketID >= 72680  -- Filter early
)
SELECT * FROM RecentData
```

---

### 3. Use EXISTS Instead of IN for Subqueries
```sql
-- SLOW (IN with large subquery)
WHERE o.OrderID IN (
    SELECT OrderID FROM JobTickets WHERE Cost > 1000
)

-- FAST (EXISTS stops at first match)
WHERE EXISTS (
    SELECT 1 FROM JobTickets jt 
    WHERE jt.OrderID = o.OrderID AND jt.Cost > 1000
)
```

---

## 🎓 Query Library Best Practices

### 1. Parameter Naming Conventions
- `months` - Time range in months (default: 6-12)
- `days` - Time range in days (default: 7-30)
- `days_back` - Lookback period (default: 30)
- `days_ahead` - Forecast period (default: 3-7)
- `top_n` - Result limit (default: 20-50)
- `min_value` - Minimum threshold filter
- `min_orders` - Minimum order count filter

### 2. SQL Formatting Standards
```sql
-- ✅ GOOD: Indented, readable, explicit JOINs
SELECT 
    o.OrderID,
    o.ClientName,
    jt.Cost,
    jtype.[Desc] AS ProductType
FROM Orders o
INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
WHERE o.OrderDate >= DATEADD(MONTH, -6, GETDATE())
  AND jt.Cost IS NOT NULL
ORDER BY o.OrderDate DESC

-- ❌ BAD: Single line, hard to read
SELECT o.OrderID,o.ClientName,jt.Cost FROM Orders o JOIN JobTickets jt ON o.OrderID=jt.OrderID WHERE o.OrderDate>=DATEADD(MONTH,-6,GETDATE())
```

### 3. Always Include NULL Filters
```sql
-- Revenue queries ALWAYS filter out NULL costs
WHERE jt.Cost IS NOT NULL

-- Reference table lookups use LEFT JOIN (allow NULL)
LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
```

### 4. Use Descriptive Column Aliases
```sql
-- ✅ GOOD
SELECT 
    o.ClientName AS CustomerName,
    COUNT(*) AS OrderCount,
    AVG(jt.Cost) AS AvgOrderValue

-- ❌ BAD
SELECT 
    o.ClientName AS CN,
    COUNT(*) AS Cnt,
    AVG(jt.Cost) AS AOV
```

---

## 📊 Query Complexity Tiers

### Tier 1: Simple Aggregation (< 10 lines)
- Single table or 2-table join
- Basic GROUP BY aggregation
- No CTEs or window functions
- Examples: `sales_trend_by_month`, `daily_order_volume`

### Tier 2: Moderate Complexity (10-30 lines)
- 3-5 table joins
- Single CTE for base data
- Basic CASE statements
- Examples: `top_customers_detailed`, `product_turnaround_benchmarks`

### Tier 3: Advanced Analytics (30-60 lines)
- 5+ table joins
- Multiple CTEs chained
- Window functions for calculations
- Complex CASE logic
- Examples: `customer_reorder_prediction_business`, `daily_production_plan`

### Tier 4: Expert Level (60+ lines)
- Multi-step CTEs (3+)
- Advanced window functions (LAG, LEAD, ROW_NUMBER)
- Dynamic scoring algorithms
- Performance optimizations
- Examples: `bottleneck_detection_advanced`, `weekly_production_forecast`

---

## 🔍 Query Validation Checklist

Before marking a query as "validated":

✅ **Schema Validation**:
- [ ] All table names exist in FRED database
- [ ] All column names exist and spelled correctly
- [ ] Reference table joins use correct key columns
- [ ] `[Desc]` brackets used where needed (except BindType.BindTypeDesc)

✅ **Logic Validation**:
- [ ] Time filters use correct parameters (months/days/weeks)
- [ ] JOIN types appropriate (INNER vs LEFT)
- [ ] NULL handling correct (IS NOT NULL where needed)
- [ ] CASE statements cover all scenarios

✅ **Performance Validation**:
- [ ] Uses TicketID filter when possible
- [ ] Filters applied early in CTEs
- [ ] Appropriate indexes leveraged
- [ ] Result set limited (TOP N) when needed

✅ **Output Validation**:
- [ ] Column aliases descriptive and clear
- [ ] Returns match metadata description
- [ ] Visualization type appropriate for data
- [ ] Handles empty result sets gracefully

---

## 📚 Additional Resources

- **Database Schema**: `docs/platforms/inhouse_print_database_schema_v2.md`
- **Query Catalog**: `QUERY_LIBRARY_COMPLETE_INVENTORY.md`
- **Tool Schemas**: `schema/inhouse_tools.json`
- **Implementation**: `backend/query_library.py`

---

**Analysis Complete**: 60 queries, 8 core patterns, 40 validated queries  
**Status**: ✅ Production Ready  
**Last Updated**: December 2, 2025
