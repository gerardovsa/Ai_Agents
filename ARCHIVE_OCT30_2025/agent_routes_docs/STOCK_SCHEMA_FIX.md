# Stock Management Schema Fix

## Problem
SQL queries using incorrect column names causing 500 errors:
- `Orders.StockID` doesn't exist
- `Orders.Quantity` doesn't exist  
- `Quote_DigitalStocks` columns assumed wrongly

## Actual Schema

### Quote_DigitalStocks (7 columns only)
- StockID
- StockTypeID  
- GSM
- Length
- Width
- CostPerThousand
- Markup

### JobTickets (order line items)
- TicketID
- OrderID
- GSM_ID (FK to GSM table, NOT StockID)
- QTY (quantity, not "Quantity")
- ShortJobDesc
- Pages
- ... (50+ other columns)

### GSM table (lookup)
- GSM_ID
- DESC (e.g., "90GSM", "100gsm")

### Orders table
- OrderID
- ClientName  
- OrderDate
- ... (no TotalAmount, no StockID, no Quantity)

## Correct JOIN Pattern

```sql
-- Link JobTickets → GSM → Quote_DigitalStocks
SELECT 
    jt.TicketID,
    jt.OrderID,
    jt.QTY,
    gsm.[DESC] as gsm_desc,
    ds.StockID,
    dst.StockType
FROM JobTickets jt
LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
LEFT JOIN Quote_DigitalStocks ds 
    ON ds.GSM = CAST(REPLACE(REPLACE(gsm.[DESC], 'GSM', ''), 'gsm', '') AS INT)
LEFT JOIN Quote_DigitalStockType dst 
    ON ds.StockTypeID = dst.StockTypeID
```

## Fixed Queries

### Usage Analytics
```sql
-- Stock consumption over time
SELECT 
    ds.StockID,
    dst.StockType,
    ds.GSM,
    COUNT(jt.TicketID) as job_count,
    CAST(o.OrderDate AS DATE) as order_date
FROM JobTickets jt
INNER JOIN Orders o ON jt.OrderID = o.OrderID
LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
LEFT JOIN Quote_DigitalStocks ds 
    ON ds.GSM = CAST(REPLACE(REPLACE(gsm.[DESC], 'GSM', ''), 'gsm', '') AS INT)
LEFT JOIN Quote_DigitalStockType dst ON ds.StockTypeID = dst.StockTypeID
WHERE o.OrderDate >= DATEADD(day, -30, GETDATE())
GROUP BY ds.StockID, dst.StockType, ds.GSM, CAST(o.OrderDate AS DATE)
ORDER BY order_date
```

### Reorder Dashboard
```sql
SELECT 
    ds.StockID,
    dst.StockType,
    ds.GSM,
    ds.Length,
    ds.Width,
    ds.CostPerThousand,
    COUNT(jt.TicketID) as recent_jobs,
    SUM(jt.QTY) as total_quantity_used,
    MAX(o.OrderDate) as last_used_date
FROM JobTickets jt
INNER JOIN Orders o ON jt.OrderID = o.OrderID
LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
LEFT JOIN Quote_DigitalStocks ds 
    ON ds.GSM = CAST(REPLACE(REPLACE(gsm.[DESC], 'GSM', ''), 'gsm', '') AS INT)
LEFT JOIN Quote_DigitalStockType dst ON ds.StockTypeID = dst.StockTypeID
WHERE o.OrderDate >= DATEADD(day, -90, GETDATE())
GROUP BY ds.StockID, dst.StockType, ds.GSM, ds.Length, ds.Width, ds.CostPerThousand
ORDER BY recent_jobs DESC
```

### Profit Analysis
```sql
SELECT 
    ds.StockID,
    dst.StockType,
    ds.GSM,
    ds.CostPerThousand as cost_per_thousand,
    ds.Markup,
    COUNT(jt.TicketID) as job_count,
    SUM(jt.QTY) as total_quantity,
    SUM(jt.QTY * ds.CostPerThousand / 1000) as total_cost,
    SUM(jt.QTY * ds.CostPerThousand * ds.Markup / 1000) as total_revenue,
    SUM((jt.QTY * ds.CostPerThousand * ds.Markup / 1000) - (jt.QTY * ds.CostPerThousand / 1000)) as total_profit
FROM JobTickets jt
INNER JOIN Orders o ON jt.OrderID = o.OrderID
LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
LEFT JOIN Quote_DigitalStocks ds 
    ON ds.GSM = CAST(REPLACE(REPLACE(gsm.[DESC], 'GSM', ''), 'gsm', '') AS INT)
LEFT JOIN Quote_DigitalStockType dst ON ds.StockTypeID = dst.StockTypeID
WHERE o.OrderDate >= DATEADD(day, -30, GETDATE())
GROUP BY ds.StockID, dst.StockType, ds.GSM, ds.CostPerThousand, ds.Markup
ORDER BY total_profit DESC
```
