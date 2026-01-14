# Calculator Pricing Catalog - Database Setup Complete ✅

**Date:** December 17, 2025  
**Database:** Supabase PostgreSQL  
**Status:** Successfully deployed and populated

---

## What Was Accomplished

### Phase 1: Database Setup (COMPLETED ✅)

**1. Created 4 Database Tables:**
- `calculator_pricing_parameters` - Master catalog of 71 pricing parameters
- `calculator_parameter_overrides` - Calculator-specific custom values
- `calculator_parameter_history` - Complete audit trail (71 initial entries)
- `calculators_registry` - Registry of 30 calculators

**2. Table Sizes:**
- calculator_pricing_parameters: 144 KB
- calculators_registry: 184 KB
- calculator_parameter_overrides: 48 KB
- calculator_parameter_history: 48 KB
- **Total:** ~424 KB

**3. Indexes Created:**
- 19 total indexes including:
  - GIN indexes for JSONB queries (fast calculator tracking)
  - Full-text search on parameter names/descriptions
  - Standard B-tree indexes for lookups
  - Conditional indexes for active records

**4. Data Loaded:**
- **71 Parameters** extracted from 30 calculators
- **30 Calculators** registered (custom, shopify, basic, god types)
- **71 History entries** for audit trail
- **0 Overrides** (none in initial data)

---

## Database Schema

### Table 1: calculator_pricing_parameters
Master catalog tracking which calculators use which parameters.

**Key Columns:**
- `parameter_name` - Unique parameter identifier (e.g., "impos_setup", "GST_RATE")
- `category` - Setup, Material, Print, Tax, Profit, Other
- `base_value` - Default/most common value
- `value_unit` - currency, percentage, multiplier, per_sqm, etc.
- `used_by_calculators` - JSONB array tracking all usages
- `total_usage_count` - How many calculators use this parameter

**JSONB Structure:**
```json
[
  {
    "calculator": "BollardSigns",
    "value": 40.00,
    "override": true,
    "file": "BollardSigns_Shopify_Calculator.py",
    "added_date": "2025-12-17T..."
  }
]
```

### Table 2: calculators_registry
Complete registry of all calculator systems.

**Key Columns:**
- `calculator_name` - Unique calculator identifier
- `calculator_type` - shopify, god, custom, basic
- `parameters_used` - JSONB object of ALL parameters this calculator uses
- `special_features` - Array: ['DOUBLE_GST', 'TIERED_PRICING', 'DUAL_PROFIT']
- `total_parameters_count` - Number of parameters used

**JSONB Structure:**
```json
{
  "impos_setup": {"value": 40.00, "unit": "currency", "override": true},
  "GST_RATE": {"value": 1.1, "unit": "multiplier", "override": false}
}
```

### Table 3: calculator_parameter_overrides
Calculator-specific custom values (currently empty, for future use).

### Table 4: calculator_parameter_history
Complete audit trail of all changes (71 initial creation entries).

---

## Top Parameters by Usage

| Rank | Parameter | Category | Base Value | Used By |
|------|-----------|----------|------------|---------|
| 1 | impos_setup | Setup | $15.00 | 27 calculators |
| 2 | GST_RATE | Tax | $1.10 | 26 calculators |
| 3 | PRICE_INCREASE_MULTIPLIER | Other | $1.00 | 19 calculators |
| 4 | extra_arts | Other | $25.00 | 18 calculators |
| 5 | sides_multiplier | Other | $2.00 | 16 calculators |
| 6 | guilo_setup | Setup | $10.00 | 14 calculators |
| 7 | cut_cost | Other | $10.00 | 11 calculators |
| 8 | stock_waste | Material | $1.05 | 11 calculators |
| 9 | print_cost_per_m2 | Print | $12.00 | 10 calculators |
| 10 | SURCHARGE | Other | $44.00 | 10 calculators |

---

## Calculator Types Breakdown

- **Custom:** 1 calculator (CustomVinylStickers)
- **Shopify:** 24 calculators (BollardSigns, PremiumBusinessCards, etc.)
- **Basic:** 3 calculators (standard calculators)
- **GOD:** 2 calculators (database-driven calculators)

**Special Features:**
- **DOUBLE_GST_APPLICATION:** 20 calculators
- **TIERED_PRICING:** 22 calculators
- **DUAL_PROFIT_STRUCTURE:** 1 calculator

---

## Database Connection Details

**Host:** aws-1-ap-southeast-2.pooler.supabase.com  
**Port:** 6543  
**Database:** postgres  
**Connection String:** `postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres`

**Access:**
- All tables are in the `public` schema
- Full JSONB query support for advanced filtering
- Connection pooler enabled for performance

---

## File Locations

### Database Files:
```
UI/modules_external/quote-calculator/database/
├── migrations/
│   ├── 001_create_catalog_tables.sql    (412 lines, 14KB)
│   └── run_migration.py                  (104 lines)
├── seeds/
│   ├── load_extracted_data.py            (411 lines)
│   └── verify_data.py                    (NEW - 60 lines)
└── README.md                             (280 lines)
```

### Source Data:
```
AI_agents/CALCULATOR_PRICING_CATALOG_EXTRACTED.json (1431 lines, 30 calculators)
```

---

## SQL Query Examples

### Find all parameters used by a specific calculator:
```sql
SELECT parameter_name, base_value, value_unit,
       used_by_calculators::jsonb
FROM calculator_pricing_parameters
WHERE used_by_calculators::text LIKE '%BollardSigns%';
```

### Get calculator details with parameter count:
```sql
SELECT calculator_name, calculator_type, 
       jsonb_object_keys(parameters_used) as param_list,
       special_features
FROM calculators_registry
WHERE calculator_name = 'BollardSigns';
```

### Find parameters with overrides:
```sql
SELECT parameter_name, base_value,
       jsonb_array_length(
         jsonb_path_query_array(
           used_by_calculators, 
           '$[*] ? (@.override == true)'
         )
       ) as override_count
FROM calculator_pricing_parameters
WHERE used_by_calculators::text LIKE '%"override":true%';
```

### Get parameter usage statistics:
```sql
SELECT 
    category,
    COUNT(*) as parameter_count,
    AVG(jsonb_array_length(used_by_calculators)) as avg_usage
FROM calculator_pricing_parameters
GROUP BY category
ORDER BY parameter_count DESC;
```

---

## Next Steps (Phase 2: Backend API)

### 1. Create Flask API Routes
**File:** `backend/api/catalog_routes.py`

**Endpoints to implement:**
- `GET /api/calculator/catalog/parameters` - List all parameters with filters
- `GET /api/calculator/catalog/parameters/:id` - Get single parameter
- `PUT /api/calculator/catalog/parameters/:id/base` - Update base value
- `POST /api/calculator/catalog/overrides` - Create override
- `PUT /api/calculator/catalog/overrides/:id` - Update override
- `DELETE /api/calculator/catalog/overrides/:id` - Delete override
- `POST /api/calculator/catalog/bulk-update` - Bulk update (3 modes)
- `GET /api/calculator/catalog/parameters/:id/history` - Change history
- `GET /api/calculator/catalog/calculators` - List calculators
- `GET /api/calculator/catalog/calculators/:name` - Calculator details

**Estimated Time:** 2-3 days

### 2. Create SQLAlchemy Models
**File:** `backend/models/catalog_models.py`

- CalculatorPricingParameter
- CalculatorParameterOverride
- CalculatorParameterHistory
- CalculatorsRegistry

**Estimated Time:** 4 hours

### 3. Create Service Layer
**File:** `backend/services/catalog_service.py`

- Update propagation logic (base/selective/forced modes)
- JSONB manipulation helpers
- History tracking functions
- Bulk operation handlers

**Estimated Time:** 1 day

---

## Next Steps (Phase 3: Frontend UI)

### 1. Create Tabulator Module
**Files:**
- `catalog/catalog.html` - Module template
- `catalog/catalog.js` - Main module class
- `catalog/catalog-tabulator.js` - Table configurations
- `catalog/catalog-api.js` - API client
- `catalog/manifest.json` - Module metadata

**Reuses 100% existing infrastructure:**
- tabulator-enhancements.js (1,239 lines) - Advanced filtering, bulk actions, history
- tabulator-functions.js (690 lines) - Row tagging, utilities
- tabulator-theme-adapter.js (397 lines) - Module theming
- tabulator-enhancements.css (1,052 lines) - Complete styling

**Table Design:**
- 71 parameters × 35 columns (30 calculators + 5 metadata)
- Color-coded cells: Green (base), Orange (override), Gray (unused)
- Inline editing with real-time API updates
- Bulk operations: Update all, reset overrides, export

**Estimated Time:** 4-5 days

---

## Documentation

✅ **Database Schema:** Complete (this document)  
✅ **Setup Guide:** Complete (README.md)  
✅ **SQL Migration:** Complete (001_create_catalog_tables.sql)  
✅ **Data Loader:** Complete (load_extracted_data.py)  
✅ **Verification Tool:** Complete (verify_data.py)  
⏳ **API Documentation:** Pending (Phase 2)  
⏳ **UI User Guide:** Pending (Phase 3)

---

## Testing Verification

Run the verification script anytime:
```bash
cd UI/modules_external/quote-calculator/database/seeds
python verify_data.py
```

**Expected Output:**
- Top 10 most used parameters
- Sample calculators with features
- Database statistics (71 params, 30 calcs, 71 history, 0 overrides)

---

## Key Benefits

✅ **Centralized Pricing:** All 71 parameters in one database  
✅ **Calculator Tracking:** Know exactly which calculators use which parameters  
✅ **JSONB Performance:** Fast queries with GIN indexes  
✅ **Full Audit Trail:** Every change tracked in history table  
✅ **Bulk Updates:** Change GST rate across 26 calculators in one operation  
✅ **Override System:** Calculator-specific custom values when needed  
✅ **Scalable:** Ready for 100+ calculators with minimal overhead  

---

## Timeline

- **Phase 1 (Database):** ✅ COMPLETE (December 17, 2025)
- **Phase 2 (API):** 3-4 days
- **Phase 3 (UI):** 5-7 days
- **Phase 4 (Testing):** 3-4 days
- **Total:** 2-3 weeks to production-ready system

---

**System Ready:** Database fully deployed and operational ✅  
**Status:** Ready for Phase 2 (Backend API development)
