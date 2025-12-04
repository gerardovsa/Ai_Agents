# Database Architecture - Complete Overview (Dec 4, 2025)

## System Overview

Your AI Agents application now uses **3 separate databases** across **2 different platforms**:

```
┌─────────────────────────────────────────────────────────┐
│  AI AGENTS APPLICATION ARCHITECTURE                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐    ┌──────────────────────────┐  │
│  │  InHouse Fred    │    │  Supabase PostgreSQL     │  │
│  │  (SQL Server)    │    │  (Cloud Database)        │  │
│  └──────────────────┘    └──────────────────────────┘  │
│          │                          │                   │
│          │                          │                   │
│    ┌─────┴─────┐          ┌────────┴────────┐         │
│    │  Orders   │          │  ai_infrastructure │         │
│    │  Jobs     │          │  sessions          │         │
│    │  Clients  │          │  synergy_sessions  │         │
│    └───────────┘          │  stock_data        │         │
│                           │  kanban_analytics  │         │
│                           └────────────────────┘         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Database 1: InHouse Fred (SQL Server)

### Purpose
Production print shop management system - orders, jobs, customers

### Platform
**SQL Server** (on-premises or hosted)

### Connection
- **Tool**: `inhouse_execute_sql()`
- **Module**: `UI/modules_external/inhouse-print/`
- **Guide**: `inhouse_database_guide()`

### Tables
```
Orders
├── OrderID (PK)
├── ClientName
├── OrderDate
├── Invoiced (bit) - ⚠️ NOT "Status"
├── Urgent
└── InvoiceNumber

JobTickets
├── TicketID (PK)
├── OrderID (FK → Orders)
├── QTY
├── Cost
├── TicketNotes
├── PaperSizeID (FK → PaperSize)
├── BindTypeID (FK → BindType)
└── ColourStatus (urgency, NOT print color)

PaperSize
├── SizeID (PK)
└── [Desc] - ⚠️ NO Width/Height columns!

BindType
├── BindID (PK)
└── BindTypeDesc - ⚠️ NOT [Desc]!

Clients
├── ClientID (PK)
├── ClientName
├── Email
└── MYOB_ID
```

### ⚠️ Common Mistakes
```sql
-- ❌ WRONG - These columns don't exist!
SELECT o.Status, o.TotalCost FROM Orders o

-- ✅ CORRECT
SELECT o.Invoiced, SUM(jt.Cost) AS TotalCost 
FROM Orders o 
LEFT JOIN JobTickets jt ON o.OrderID = jt.OrderID
```

### SQL Syntax
```sql
-- InHouse uses SQL Server syntax
SELECT TOP 20 * FROM Orders  -- NOT LIMIT 20
WHERE OrderDate > DATEADD(month, -3, GETDATE())
```

---

## Database 2: Supabase PostgreSQL (stock_data schema)

### Purpose
Stock management, inventory, AI-extracted job data

### Platform
**Supabase PostgreSQL** (cloud-hosted)

### Connection
- **Function**: `get_database_connection('stock_data')`
- **Module**: `UI/modules_external/stock-management/`
- **URL**: `SUPABASE_DB_URL_POOLER` from `.env.master`

### Schema: `stock_data.*`

```
stock_data.extracted_jobs
├── id (PK)
├── ticket_id
├── order_date
├── client_name
├── stock_id (FK → unified_stocks)
├── quantity_ordered
├── total_sheets_consumed
├── stock_cost_estimate
└── [100+ columns from AI extraction]

stock_data.unified_stocks
├── stock_id (PK)
├── stock_category
├── stock_type_name
├── gsm
├── length_mm
├── width_mm
├── cost_per_thousand
├── markup
└── supplier_name

stock_data.stocklevels
├── StockID (PK)
├── CurrentStockLevel
├── ReorderPoint
├── CriticalLevel
└── LastUpdated

stock_data.reorderalerts
├── AlertID (PK)
├── StockID (FK)
├── AlertLevel
├── CurrentLevel
└── ReorderPoint

stock_data.consumableinventory
├── ConsumableID (PK)
├── Description
├── CurrentStock
├── ReorderPoint
└── CostPerUnit

stock_data.corflutematerials
├── MaterialID (PK)
├── Thickness
├── SheetsInStock
├── TotalSqmInStock
└── CostPerSheet

stock_data.shopify_orders
stock_data.shopify_products
stock_data.shopify_customers
[... other Shopify integration tables]
```

### SQL Syntax (PostgreSQL)
```sql
-- PostgreSQL syntax
SELECT * FROM stock_data.extracted_jobs 
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
LIMIT 20

-- String concatenation
SELECT CONCAT(length_mm, 'x', width_mm, 'mm') AS dimensions

-- Rounding
SELECT ROUND(CAST(cost * 1.35 AS NUMERIC), 2) AS price
```

---

## Database 3: Supabase PostgreSQL (other schemas)

### Purpose
AI agent infrastructure, sessions, Synergy Kanban

### Platform
**Supabase PostgreSQL** (same cloud instance as stock_data)

### Schemas

#### `ai_infrastructure` schema
- Agent configurations
- Tool definitions
- System settings

#### `sessions` schema
- User sessions
- Thread management
- Agent execution logs

#### `synergy_sessions` schema
- Synergy Kanban board data
- Milestones, tasks, subtasks
- Project management

#### `kanban_analytics` schema
- Analytics data
- Performance metrics

---

## Connection Methods

### 1. InHouse Fred (SQL Server)
```python
# Via inhouse tools
from UI.modules_external.inhouse_print.implementations.inhouse_wrapper import inhouse_execute_sql

result = inhouse_execute_sql("SELECT TOP 10 * FROM Orders")
```

### 2. Supabase stock_data
```python
# Direct connection
from AI_infrastructure.shared.database_utils import get_database_connection

conn = get_database_connection('stock_data')
cursor = conn.cursor()
cursor.execute("SELECT * FROM stock_data.extracted_jobs LIMIT 10")
rows = cursor.fetchall()
conn.close()
```

### 3. Supabase other schemas
```python
# Same function, different schema name
conn = get_database_connection('sessions')  # or 'ai_infrastructure', etc.
```

---

## Key Differences

| Feature | InHouse Fred (SQL Server) | Supabase (PostgreSQL) |
|---------|---------------------------|------------------------|
| **Platform** | SQL Server | PostgreSQL |
| **LIMIT** | `TOP N` | `LIMIT N` |
| **Placeholders** | `?` | `%s` |
| **Concat** | `+` or `||` | `CONCAT()` or `||` |
| **Date** | `DATEADD()`, `GETDATE()` | `INTERVAL`, `CURRENT_DATE` |
| **Schema** | `dbo` (implicit) | Explicit (`stock_data.*`) |
| **Row Factory** | ODBC (dict-like) | psycopg2 (tuple, needs zip) |

---

## Module Mapping

| Module | Database | Schema/Tables |
|--------|----------|---------------|
| InHouse Print | InHouse Fred (SQL Server) | Orders, JobTickets, PaperSize, BindType |
| Stock Management | Supabase PostgreSQL | stock_data.* |
| Agent Core | Supabase PostgreSQL | ai_infrastructure, sessions |
| Synergy Kanban | Supabase PostgreSQL | synergy_sessions |
| Quote Calculator | InHouse Fred (read-only) | Quote_DigitalStocks, etc. |

---

## Environment Configuration

### `.env.master` Variables

```bash
# InHouse Fred (SQL Server)
SUPABASE_INHOUSE_DB_URL=<SQL Server connection string>

# Supabase PostgreSQL
SUPABASE_DB_URL_POOLER=postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres
USE_SUPABASE=true

# Credentials
SUPABASE_URL=https://ryoicrdifiqhqpsnjmdo.supabase.co
SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_KEY=<service_key>
```

---

## Migration History

### October 2025
- Created SQLite `stock_data.db` for temporary stock management
- SQLite used due to inability to modify InHouse Fred production database

### November 2025
- Migrated SQLite → Supabase PostgreSQL
- Created `stock_data` schema in Supabase
- Preserved all table structures and data

### December 4, 2025
- ✅ **Updated Stock Management module** to use Supabase
- ✅ **Corrected InHouse Database Guide** with actual schema
- ✅ **Documented complete database architecture**

---

## Quick Reference

### "Where is my data?"

**Orders, Jobs, Clients?**  
→ InHouse Fred (SQL Server)

**Stock, Inventory, Reorder Alerts?**  
→ Supabase `stock_data` schema

**Agent Sessions, Threads?**  
→ Supabase `sessions` schema

**Synergy Kanban?**  
→ Supabase `synergy_sessions` schema

### "How do I query?"

**InHouse Fred:**
```python
inhouse_database_guide()  # Get schema
inhouse_execute_sql("SELECT TOP 10 * FROM Orders")
```

**Supabase stock_data:**
```python
conn = get_database_connection('stock_data')
cursor.execute("SELECT * FROM stock_data.extracted_jobs LIMIT 10")
```

### "Can I JOIN between databases?"

❌ **NO!** They are on different servers.

You must:
1. Query Database 1
2. Process results
3. Query Database 2 with results from Database 1

---

## Related Documentation

- `INHOUSE_DATABASE_GUIDE_CORRECTIONS_DEC4_2025.md` - InHouse Fred schema corrections
- `STOCK_MANAGEMENT_SUPABASE_MIGRATION_DEC4_2025.md` - Stock module migration details
- `AI_infrastructure/shared/database_utils.py` - Connection utility source code
- `UI/modules_external/inhouse-print/implementations/inhouse_guide_wrapper.py` - InHouse guide tool

---

**Last Updated:** December 4, 2025  
**Verified By:** GitHub Copilot (Claude Sonnet 4.5)  
**Status:** ✅ All modules connected to correct databases
