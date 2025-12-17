# Calculator Pricing Catalog - Database Setup

## Quick Start

### Step 1: Create Tables (Run SQL Migration)

```powershell
# Connect to PostgreSQL and run migration
psql -U postgres -d in_house_print -f migrations/001_create_catalog_tables.sql
```

**What this creates:**
- ✅ 4 tables (parameters, overrides, history, registry)
- ✅ Indexes (GIN for JSONB, standard for queries)
- ✅ Views (v_parameters_complete, v_calculators_summary)
- ✅ Triggers (auto-update timestamps)
- ✅ Sample data (1 parameter, 1 calculator for testing)

### Step 2: Load Extracted Data

```powershell
# First, update database credentials in load_extracted_data.py
# Then run:

# Dry run (test without committing)
python seeds/load_extracted_data.py --dry-run

# Actual load
python seeds/load_extracted_data.py
```

**What this loads:**
- 📊 363 pricing parameters
- 🧮 30 calculators
- 📜 363 history entries (initial creation)

### Step 3: Verify Data

```sql
-- Check tables
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS size
FROM pg_tables
WHERE tablename LIKE 'calculator%'
ORDER BY tablename;

-- Check row counts
SELECT 'parameters' as table_name, COUNT(*) as row_count FROM calculator_pricing_parameters
UNION ALL
SELECT 'calculators', COUNT(*) FROM calculators_registry
UNION ALL
SELECT 'overrides', COUNT(*) FROM calculator_parameter_overrides
UNION ALL
SELECT 'history', COUNT(*) FROM calculator_parameter_history;

-- Sample parameter with calculator usage
SELECT 
    parameter_name,
    category,
    base_value,
    total_usage_count,
    jsonb_pretty(used_by_calculators) as calculators
FROM calculator_pricing_parameters
WHERE parameter_name = 'impos_setup';

-- Sample calculator with parameters
SELECT 
    calculator_name,
    calculator_type,
    total_parameters_count,
    special_features,
    jsonb_pretty(parameters_used) as parameters
FROM calculators_registry
WHERE calculator_name = 'PremiumBusinessCards';
```

---

## Database Schema

### Table 1: calculator_pricing_parameters
**Purpose:** Master catalog of all pricing parameters with calculator tracking

**Key Columns:**
- `parameter_name` (unique) - e.g., "impos_setup", "GST_RATE"
- `category` - Setup, Material, Print, Profit, Tax, etc.
- `base_value` - Default value
- `used_by_calculators` - **JSONB array** of calculator usage
- `total_usage_count` - Auto-calculated from JSONB array

**Example Row:**
```json
{
  "parameter_name": "impos_setup",
  "category": "Setup",
  "base_value": 15.00,
  "used_by_calculators": [
    {
      "calculator": "PremiumBusinessCards",
      "value": 15.00,
      "override": false,
      "file": "PremiumBusinessCards_Shopify_Calculator.py",
      "added_date": "2025-12-17"
    },
    {
      "calculator": "BollardSigns",
      "value": 40.00,
      "override": true,
      "file": "BollardSigns_Shopify_Calculator.py",
      "added_date": "2025-12-17"
    }
  ],
  "total_usage_count": 2
}
```

### Table 2: calculator_parameter_overrides
**Purpose:** Calculator-specific override values

**Key Columns:**
- `calculator_name` - e.g., "BollardSigns"
- `parameter_id` - FK to parameters table
- `override_value` - Custom value for this calculator
- `override_reason` - Why it's different
- `is_active` - Enable/disable override

### Table 3: calculator_parameter_history
**Purpose:** Complete audit trail

**Key Columns:**
- `parameter_id` - FK to parameters table
- `change_type` - value_update, calculator_added, override_created, etc.
- `old_value` - JSONB before change
- `new_value` - JSONB after change
- `affected_calculators` - Array of calculator names
- `changed_by` - User who made change

### Table 4: calculators_registry
**Purpose:** Master list of all calculators

**Key Columns:**
- `calculator_name` (unique) - e.g., "PremiumBusinessCards"
- `calculator_type` - shopify, god, custom, basic
- `parameters_used` - **JSONB object** of all parameters
- `special_features` - Array: ['DOUBLE_GST', 'TIERED_PRICING']
- `total_parameters_count` - Auto-calculated

---

## Common Queries

### Find all parameters used by a calculator
```sql
SELECT 
    p.parameter_name,
    p.category,
    p.base_value,
    calc_usage.value as calculator_value,
    calc_usage.override as is_override
FROM calculator_pricing_parameters p,
    jsonb_to_recordset(p.used_by_calculators) AS calc_usage(
        calculator TEXT,
        value NUMERIC,
        override BOOLEAN,
        file TEXT,
        added_date TEXT
    )
WHERE calc_usage.calculator = 'BollardSigns'
ORDER BY p.category, p.parameter_name;
```

### Find parameters with overrides
```sql
SELECT 
    p.parameter_name,
    p.base_value,
    calc_usage.calculator,
    calc_usage.value as override_value,
    (calc_usage.value - p.base_value) as difference
FROM calculator_pricing_parameters p,
    jsonb_to_recordset(p.used_by_calculators) AS calc_usage(
        calculator TEXT,
        value NUMERIC,
        override BOOLEAN
    )
WHERE calc_usage.override = true
ORDER BY ABS(calc_usage.value - p.base_value) DESC;
```

### Get parameter usage statistics
```sql
SELECT 
    category,
    COUNT(*) as total_parameters,
    AVG(total_usage_count) as avg_usage_per_param,
    SUM(total_usage_count) as total_usages
FROM calculator_pricing_parameters
GROUP BY category
ORDER BY total_parameters DESC;
```

### Find calculators with most overrides
```sql
SELECT 
    calculator_name,
    calculator_type,
    COUNT(*) as override_count
FROM calculator_parameter_overrides
WHERE is_active = TRUE
GROUP BY calculator_name, calculator_type
ORDER BY override_count DESC;
```

---

## Troubleshooting

### Error: "relation already exists"
Tables already created. Either:
- Drop tables: `DROP TABLE IF EXISTS calculator_pricing_parameters CASCADE;`
- Or skip to Step 2 (load data)

### Error: "permission denied"
Need PostgreSQL superuser or table owner permissions:
```sql
GRANT ALL ON ALL TABLES IN SCHEMA public TO your_username;
```

### Error: "database connection failed"
Update `DB_CONFIG` in `load_extracted_data.py`:
```python
DB_CONFIG = {
    'dbname': 'in_house_print',  # Your database name
    'user': 'postgres',          # Your username
    'password': 'your_password', # Your password
    'host': 'localhost',
    'port': 5432
}
```

### JSON file not found
Ensure `CALCULATOR_PRICING_CATALOG_EXTRACTED.json` is in:
```
AI_agents/CALCULATOR_PRICING_CATALOG_EXTRACTED.json
```

---

## Next Steps

After database is set up:

1. **✅ Database ready** (you are here)
2. **Create Flask API** - CRUD routes for catalog
3. **Build Tabulator UI** - Frontend module
4. **Test end-to-end** - Full workflow validation

See: `CALCULATOR_PRICING_UI_TABULATOR.md` for UI implementation guide
