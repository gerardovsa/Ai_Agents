# 🏗️ Calculator Pricing & Options - Unified Architecture Plan

**Created:** December 17, 2025  
**Purpose:** Complete system design for managing both pricing constants AND product options  
**Scope:** Database schema, AI tool layer, API, UI, data management strategy

---

## 🎯 **Executive Summary**

**Problem:** Need TWO separate but integrated systems:
1. **Pricing Constants Manager** - Backend calculation variables (64 parameters)
2. **Product Options Manager** - Customer-facing product configurations (150+ options)

**Current State:**
- ✅ Pricing Constants: Database exists, 64 parameters loaded, duplicates cleaned
- ❌ Product Options: Not extracted, no database schema, no UI

**Goal:** Unified management system for AI agents and users to maintain calculator pricing

---

## 📐 **DATABASE ARCHITECTURE**

### **Design Principles**
1. **Separation of Concerns:** Two distinct table groups (constants vs options)
2. **Normalization:** Minimize redundancy, enforce referential integrity
3. **Auditability:** Complete history tracking for both systems
4. **Flexibility:** Support calculator-specific overrides without breaking base values
5. **AI-Friendly:** Queryable structure for tool layer, clear relationships

### **Schema Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    PRICING CONSTANTS                        │
│  (Backend calculation variables - single values)            │
├─────────────────────────────────────────────────────────────┤
│  calculator_pricing_parameters (64 params)                  │
│  calculator_parameter_overrides (0 rows - needs population) │
│  calculator_parameter_history (64 entries)                  │
│  calculators_registry (30 calculators)                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     PRODUCT OPTIONS                         │
│  (Customer-facing choices - multiple values with prices)    │
├─────────────────────────────────────────────────────────────┤
│  product_options (NEW - ~150 options)                       │
│  product_option_choices (NEW - ~500 choices)                │
│  product_option_overrides (NEW - for custom pricing)        │
│  product_option_history (NEW - audit trail)                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ **DETAILED SCHEMA DESIGN**

### **GROUP 1: Pricing Constants (Existing - Enhancement Needed)**

#### **Table: calculator_pricing_parameters** (Current: 64 rows)
```sql
CREATE TABLE calculator_pricing_parameters (
    id SERIAL PRIMARY KEY,
    parameter_name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,  -- Setup/Material/Labor/Markup/Tax
    base_value NUMERIC(10,4) NOT NULL,
    unit TEXT,
    value_statistics JSONB,  -- ✅ Added in Migration 002
    used_by_calculators JSONB NOT NULL DEFAULT '[]',  -- ✅ Existing
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Enhancement Needed:**
- Add `allows_calculator_override BOOLEAN DEFAULT TRUE`
- Add `update_mode TEXT DEFAULT 'base'` -- base/selective/force
- Add `validation_rules JSONB` -- {min: 0, max: 1000, required: true}

#### **Table: calculator_parameter_overrides** (Current: 0 rows ❌)
```sql
CREATE TABLE calculator_parameter_overrides (
    id SERIAL PRIMARY KEY,
    parameter_id INTEGER REFERENCES calculator_pricing_parameters(id) ON DELETE CASCADE,
    calculator_id INTEGER REFERENCES calculators_registry(id) ON DELETE CASCADE,
    override_value NUMERIC(10,4) NOT NULL,
    reason TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(parameter_id, calculator_id, is_active)
);
```

**Status:** Table exists but EMPTY - Migration 003 needed

#### **Table: calculator_parameter_history** (Current: 64 entries)
```sql
-- ✅ Already tracking parameter_created events
-- Need to enhance for override tracking
```

### **GROUP 2: Product Options (NEW - Not Built)**

#### **Table: product_options** (Target: ~150 options)
```sql
CREATE TABLE product_options (
    id SERIAL PRIMARY KEY,
    calculator_id INTEGER REFERENCES calculators_registry(id) ON DELETE CASCADE,
    option_name TEXT NOT NULL,  -- "Stock Type", "Quantity", "Celloglaze"
    field_id TEXT,  -- "F1", "F11" (from Shopify JSON)
    option_type TEXT NOT NULL,  -- select/radio/checkbox/number
    is_required BOOLEAN DEFAULT FALSE,
    default_choice_id INTEGER,  -- FK to product_option_choices
    display_order INTEGER,
    description TEXT,
    metadata JSONB,  -- {shopify_field_id: "F1", ui_hint: "dropdown"}
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(calculator_id, option_name)
);
```

**Relationships:**
- One calculator → many options (1:N)
- NotepadsA4 → [Quantity, Stock Type, Print Type, Artworks, Leaves Per Pad, Finish Size]

#### **Table: product_option_choices** (Target: ~500 choices)
```sql
CREATE TABLE product_option_choices (
    id SERIAL PRIMARY KEY,
    option_id INTEGER REFERENCES product_options(id) ON DELETE CASCADE,
    choice_title TEXT NOT NULL,  -- "Bond 80GSM", "Bond 90GSM"
    price NUMERIC(10,4) NOT NULL,
    price_type TEXT NOT NULL,  -- fixed/multiplier/per_sheet/per_unit
    sku TEXT,
    display_order INTEGER,
    description TEXT,
    metadata JSONB,  -- {color: "#fff", icon: "paper.svg"}
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(option_id, choice_title)
);
```

**Relationships:**
- One option → many choices (1:N)
- "Stock Type" option → [Bond 80GSM, Bond 90GSM, Bond 100GSM, Recycled 80GSM]

**Example Data:**
```json
{
  "option": {
    "id": 1,
    "calculator_id": 5,  -- NotepadsA4
    "option_name": "Stock Type",
    "field_id": "F11",
    "option_type": "select",
    "is_required": true,
    "default_choice_id": 10
  },
  "choices": [
    {
      "id": 10,
      "option_id": 1,
      "choice_title": "Uncoated Bond 80GSM",
      "price": 0.03,
      "price_type": "per_sheet",
      "sku": "stock_bond_80",
      "display_order": 1
    },
    {
      "id": 11,
      "option_id": 1,
      "choice_title": "Uncoated Bond 90GSM",
      "price": 0.033,
      "price_type": "per_sheet",
      "display_order": 2
    }
  ]
}
```

#### **Table: product_option_overrides** (Custom Pricing)
```sql
CREATE TABLE product_option_overrides (
    id SERIAL PRIMARY KEY,
    choice_id INTEGER REFERENCES product_option_choices(id) ON DELETE CASCADE,
    override_price NUMERIC(10,4) NOT NULL,
    override_reason TEXT,  -- "Holiday discount", "Bulk customer pricing"
    customer_segment TEXT,  -- "retail", "wholesale", "enterprise"
    valid_from TIMESTAMPTZ,
    valid_until TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    created_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Use Case:** Customer-specific pricing or seasonal discounts
- Bond 80GSM normally $0.03/sheet
- Override for enterprise customers: $0.025/sheet

#### **Table: product_option_history** (Audit Trail)
```sql
CREATE TABLE product_option_history (
    id SERIAL PRIMARY KEY,
    change_type TEXT NOT NULL,  -- option_created/choice_created/choice_price_updated/override_created
    option_id INTEGER,
    choice_id INTEGER,
    override_id INTEGER,
    old_value JSONB,
    new_value JSONB,
    changed_by TEXT,
    changed_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🔄 **DATA RELATIONSHIPS**

### **Cross-System Integration**

```
calculators_registry (30 calculators)
    ├─── Uses ───> calculator_pricing_parameters (64 params)
    │               └─── Overridden By ───> calculator_parameter_overrides
    │
    └─── Has ───> product_options (150 options)
                    └─── Contains ───> product_option_choices (500 choices)
                                        └─── Overridden By ───> product_option_overrides
```

### **Example: NotepadsA4 Calculator**

**Pricing Constants (6 parameters):**
- impos_setup: $15 (base) → $15 (no override)
- guilo_setup: $12 (base) → $12 (no override)
- extra_arts: $15 (base) → $15 (no override)
- stock_waste: 0.05 (base) → 0.05 (no override)
- gst_rate: 0.10 (base) → 0.10 (no override)
- cutting_block: $10 (base) → $10 (no override)

**Product Options (6 options, 30 choices total):**
1. **Quantity** (F1) - 13 choices
   - 25 @ $25 fixed
   - 50 @ $50 fixed
   - 100 @ $100 fixed
   - ... (10 more)

2. **Artworks** (F2) - 5 choices
   - 1 artwork @ $0 fixed
   - 2 artworks @ $15 fixed
   - 3 artworks @ $30 fixed
   - ... (2 more)

3. **Leaves Per Pad** (F3) - 3 choices
   - 25 leaves @ $0 fixed
   - 50 leaves @ $0 fixed
   - 100 leaves @ $0 fixed

4. **Finish Size** (F4) - 3 choices
   - A4 @ $0 fixed
   - A5 @ $0 fixed
   - A6 @ $0 fixed

5. **Print Type** (F10) - 4 choices
   - Colour 1 sided @ $0.048 per_sheet
   - Colour 2 sided @ $0.096 per_sheet
   - B&W 1 sided @ $0.01 per_sheet
   - B&W 2 sided @ $0.02 per_sheet

6. **Stock Type** (F11) - 4 choices
   - Bond 80GSM @ $0.03 per_sheet
   - Bond 90GSM @ $0.033 per_sheet
   - Bond 100GSM @ $0.045 per_sheet
   - Recycled 80GSM @ $0.06 per_sheet

---

## 🤖 **AI TOOL LAYER DESIGN**

### **Tool Categories**

#### **1. Query Tools (Read-Only)**
```python
@tool
def get_pricing_constant(parameter_name: str, calculator_name: str = None):
    """
    Get current value of a pricing constant.
    
    Args:
        parameter_name: Name of parameter (e.g., "impos_setup")
        calculator_name: Optional - get calculator-specific override
    
    Returns:
        {
            "parameter": "impos_setup",
            "base_value": 40.0,
            "calculator_override": 40.0,  # or null if no override
            "used_by": ["BollardSigns", "BusinessCards", ...],
            "unit": "currency",
            "last_updated": "2025-12-17T10:30:00Z"
        }
    """
    pass

@tool
def get_product_option_choices(calculator_name: str, option_name: str):
    """
    Get all available choices for a product option.
    
    Args:
        calculator_name: "NotepadsA4", "BusinessCards", etc.
        option_name: "Stock Type", "Quantity", etc.
    
    Returns:
        {
            "calculator": "NotepadsA4",
            "option": "Stock Type",
            "field_id": "F11",
            "required": true,
            "default_choice": "Bond 80GSM",
            "choices": [
                {"title": "Bond 80GSM", "price": 0.03, "price_type": "per_sheet"},
                {"title": "Bond 90GSM", "price": 0.033, "price_type": "per_sheet"},
                ...
            ]
        }
    """
    pass

@tool
def search_calculators_by_feature(feature: str):
    """
    Find calculators with specific features or options.
    
    Args:
        feature: "DOUBLE_GST", "TIERED_PRICING", "has_celloglaze_option"
    
    Returns:
        ["CustomVinylStickers", "BollardSigns", ...]
    """
    pass
```

#### **2. Update Tools (Write Operations)**
```python
@tool
def update_pricing_constant(
    parameter_name: str,
    new_value: float,
    update_mode: str = "base",
    target_calculators: list = None,
    reason: str = None
):
    """
    Update a pricing constant value.
    
    Args:
        parameter_name: Parameter to update
        new_value: New value to set
        update_mode: 
            - "base": Update base value only (affects all without overrides)
            - "selective": Update specific calculators (create/update overrides)
            - "force": Update base + remove all overrides
        target_calculators: List of calculator names (for selective mode)
        reason: Audit trail reason
    
    Returns:
        {
            "success": true,
            "updated": {
                "base_value": 45.0,
                "previous_value": 40.0,
                "affected_calculators": 28,
                "overrides_created": 0
            },
            "history_id": 142
        }
    
    Raises:
        ValidationError: If new_value violates validation rules
        ConflictError: If simultaneous update detected
    """
    pass

@tool
def update_product_option_price(
    calculator_name: str,
    option_name: str,
    choice_title: str,
    new_price: float,
    reason: str = None
):
    """
    Update the price of a specific product option choice.
    
    Args:
        calculator_name: "NotepadsA4"
        option_name: "Stock Type"
        choice_title: "Bond 80GSM"
        new_price: 0.035
        reason: "Supplier price increase"
    
    Returns:
        {
            "success": true,
            "updated": {
                "option": "Stock Type",
                "choice": "Bond 80GSM",
                "previous_price": 0.03,
                "new_price": 0.035,
                "price_type": "per_sheet"
            },
            "history_id": 256
        }
    """
    pass
```

#### **3. Validation Tools**
```python
@tool
def validate_calculator_config(calculator_name: str):
    """
    Check if calculator has all required parameters and options.
    
    Returns:
        {
            "valid": false,
            "missing_constants": ["stock_waste"],
            "missing_options": [],
            "invalid_prices": [
                {"option": "Stock Type", "choice": "Bond 90GSM", "error": "Price cannot be negative"}
            ]
        }
    """
    pass
```

#### **4. Batch Operations**
```python
@tool
def bulk_update_prices(updates: list):
    """
    Update multiple prices in a single transaction.
    
    Args:
        updates: [
            {"type": "constant", "parameter": "impos_setup", "value": 45.0},
            {"type": "option_choice", "calculator": "NotepadsA4", "option": "Stock Type", 
             "choice": "Bond 80GSM", "price": 0.035}
        ]
    
    Returns:
        {
            "success": true,
            "updated": 2,
            "failed": 0,
            "rollback": false
        }
    """
    pass
```

---

## 🌐 **API ENDPOINTS**

### **Pricing Constants API**

```
GET    /api/v1/pricing-constants
GET    /api/v1/pricing-constants/:id
GET    /api/v1/pricing-constants/:id/history
GET    /api/v1/pricing-constants/:id/calculators
POST   /api/v1/pricing-constants
PUT    /api/v1/pricing-constants/:id
DELETE /api/v1/pricing-constants/:id

GET    /api/v1/pricing-constants/:id/overrides
POST   /api/v1/pricing-constants/:id/overrides
PUT    /api/v1/pricing-constants/:id/overrides/:override_id
DELETE /api/v1/pricing-constants/:id/overrides/:override_id
```

### **Product Options API**

```
GET    /api/v1/calculators/:calculator_id/options
GET    /api/v1/calculators/:calculator_id/options/:option_id
GET    /api/v1/calculators/:calculator_id/options/:option_id/choices
POST   /api/v1/calculators/:calculator_id/options
PUT    /api/v1/calculators/:calculator_id/options/:option_id
DELETE /api/v1/calculators/:calculator_id/options/:option_id

GET    /api/v1/options/:option_id/choices/:choice_id
PUT    /api/v1/options/:option_id/choices/:choice_id
DELETE /api/v1/options/:option_id/choices/:choice_id

GET    /api/v1/choices/:choice_id/overrides
POST   /api/v1/choices/:choice_id/overrides
```

### **Unified API**

```
GET    /api/v1/calculators/:calculator_id/config
       Returns: {
           "calculator": {...},
           "pricing_constants": [...],
           "product_options": [...]
       }

POST   /api/v1/bulk-update
       Body: {updates: [...]}
```

---

## 🎨 **UI ARCHITECTURE**

### **Module 1: Pricing Constants Manager**

**Location:** `UI/modules_external/quote-calculator/pricing-constants/`

**Components:**
1. **ParametersTable.js** (Tabulator)
   - Columns: Parameter Name, Category, Base Value, Unit, Used By (count), Variance %
   - Row expansion: Show all calculators using this parameter
   - Inline editing: Base value with validation
   - Actions: Edit, View History, Manage Overrides

2. **ParameterEditor.js** (Modal)
   - Form fields: name, category, base_value, unit, description
   - Validation rules editor (min/max/required)
   - Update mode selector: base/selective/force
   - Target calculators multi-select (for selective mode)

3. **OverridesManager.js** (Nested Tabulator)
   - Shows calculator-specific overrides for a parameter
   - Columns: Calculator, Override Value, Reason, Created By, Date
   - Inline editing with active/inactive toggle
   - Bulk activate/deactivate

4. **HistoryViewer.js** (Timeline)
   - Shows all changes to a parameter
   - Filters: change_type, date range, changed_by
   - Rollback feature (create new override with old value)

### **Module 2: Product Options Manager**

**Location:** `UI/modules_external/quote-calculator/product-options/`

**Components:**
1. **CalculatorSelector.js**
   - Dropdown or card grid to select calculator
   - Shows: calculator name, total options, total choices, last updated

2. **OptionsTable.js** (Tabulator)
   - Columns: Option Name, Field ID, Type, Required, Choices Count, Default
   - Row expansion: Show all choices for this option
   - Actions: Add Choice, Edit Option, Delete Option

3. **ChoicesEditor.js** (Nested Tabulator)
   - Columns: Choice Title, Price, Price Type, SKU, Active
   - Inline editing with drag-to-reorder (display_order)
   - Bulk price update (e.g., increase all by 10%)

4. **OptionFormModal.js**
   - Create/Edit option: name, field_id, type, required, description
   - Choices sub-form with add/remove rows
   - Validation: unique choice titles, positive prices

### **Module 3: Calculator Config Dashboard**

**Location:** `UI/modules_external/quote-calculator/dashboard/`

**Features:**
1. **Calculator Overview**
   - Card showing: name, total constants used, total options, total choices
   - Health check: missing parameters, invalid prices, incomplete configs

2. **Quick Actions**
   - Clone calculator config to new calculator
   - Export config as JSON
   - Import config from JSON
   - Compare two calculators

3. **Analytics**
   - Most variable parameters (highest variance)
   - Most expensive options
   - Least used parameters (candidates for removal)
   - Price trends over time

---

## 🔐 **DATA MANAGEMENT STRATEGY**

### **1. Data Integrity**

**Foreign Key Constraints:**
```sql
-- Prevent orphaned overrides
ALTER TABLE calculator_parameter_overrides
    ADD CONSTRAINT fk_parameter
    FOREIGN KEY (parameter_id) 
    REFERENCES calculator_pricing_parameters(id) 
    ON DELETE CASCADE;

-- Prevent orphaned choices
ALTER TABLE product_option_choices
    ADD CONSTRAINT fk_option
    FOREIGN KEY (option_id) 
    REFERENCES product_options(id) 
    ON DELETE CASCADE;
```

**Check Constraints:**
```sql
-- Ensure positive prices
ALTER TABLE product_option_choices
    ADD CONSTRAINT positive_price
    CHECK (price >= 0);

-- Valid price types
ALTER TABLE product_option_choices
    ADD CONSTRAINT valid_price_type
    CHECK (price_type IN ('fixed', 'multiplier', 'per_sheet', 'per_unit'));
```

**Triggers:**
```sql
-- Auto-update updated_at timestamp
CREATE TRIGGER update_timestamp
    BEFORE UPDATE ON calculator_pricing_parameters
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Log all changes to history
CREATE TRIGGER log_parameter_change
    AFTER UPDATE ON calculator_pricing_parameters
    FOR EACH ROW
    EXECUTE FUNCTION log_to_history();
```

### **2. Update Propagation**

**Scenario 1: Update Base Value (affects all without overrides)**
```python
# User updates impos_setup from $40 to $45
UPDATE calculator_pricing_parameters 
SET base_value = 45.0 
WHERE parameter_name = 'impos_setup';

# Result:
# - Calculators WITHOUT overrides: now use $45 ✅
# - Calculators WITH overrides: still use override value ✅
# - History logged: old_value=$40, new_value=$45
```

**Scenario 2: Create Calculator-Specific Override**
```python
# User wants BollardSigns to use $50 instead of $45 base
INSERT INTO calculator_parameter_overrides 
    (parameter_id, calculator_id, override_value, reason) 
VALUES (1, 3, 50.0, 'Higher setup cost for bollard materials');

# Result:
# - BollardSigns: now uses $50 ✅
# - Other calculators: continue using $45 base ✅
# - History logged: change_type=override_created
```

**Scenario 3: Force Update (remove all overrides)**
```python
# User wants to reset all calculators to new base value $60
BEGIN;
    UPDATE calculator_pricing_parameters 
    SET base_value = 60.0 
    WHERE parameter_name = 'impos_setup';
    
    DELETE FROM calculator_parameter_overrides 
    WHERE parameter_id = 1;
COMMIT;

# Result:
# - ALL calculators now use $60 ✅
# - Previous overrides logged in history before deletion
```

### **3. Conflict Detection**

**Optimistic Locking:**
```sql
-- Add version column
ALTER TABLE calculator_pricing_parameters 
    ADD COLUMN version INTEGER DEFAULT 1;

-- Update with version check
UPDATE calculator_pricing_parameters 
SET base_value = 45.0, version = version + 1 
WHERE parameter_name = 'impos_setup' 
AND version = 3;  -- Fails if someone else updated (version now 4)
```

**Real-Time Notifications:**
```javascript
// WebSocket message when someone else edits same parameter
{
    "type": "parameter_locked",
    "parameter_id": 1,
    "parameter_name": "impos_setup",
    "locked_by": "john.doe@example.com",
    "locked_at": "2025-12-17T10:45:00Z"
}
```

### **4. Validation Rules**

**Parameter-Level Rules:**
```json
{
    "impos_setup": {
        "min": 0,
        "max": 1000,
        "required": true,
        "data_type": "currency",
        "warning_threshold": {
            "below": 10,
            "above": 100,
            "message": "Unusual imposition setup cost"
        }
    },
    "gst_rate": {
        "min": 0,
        "max": 1,
        "required": true,
        "data_type": "percentage",
        "fixed": true  // Cannot be changed without admin approval
    }
}
```

**Option-Level Rules:**
```json
{
    "Stock Type": {
        "min_choices": 2,
        "max_choices": 10,
        "required": true,
        "price_constraints": {
            "min": 0,
            "max": 1,
            "allow_zero": true
        }
    }
}
```

---

## 🚀 **ROBUSTNESS & RELIABILITY**

### **1. Database Backups**
- **Daily:** Full database backup at 2 AM UTC
- **Hourly:** Incremental backup of changed tables
- **Before Migration:** Manual backup triggered automatically
- **Retention:** 30 days rolling window

### **2. Error Handling**

**API Layer:**
```python
@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({
        "error": "validation_failed",
        "message": str(e),
        "field": e.field_name,
        "value": e.invalid_value,
        "constraints": e.validation_rules
    }), 400

@app.errorhandler(ConflictError)
def handle_conflict(e):
    return jsonify({
        "error": "conflict_detected",
        "message": "Resource was modified by another user",
        "current_version": e.current_version,
        "your_version": e.attempted_version,
        "suggestion": "Refresh and try again"
    }), 409
```

**UI Layer:**
```javascript
// Retry logic with exponential backoff
async function updateParameter(data, retries = 3) {
    for (let i = 0; i < retries; i++) {
        try {
            return await api.put(`/parameters/${data.id}`, data);
        } catch (err) {
            if (err.status === 409 && i < retries - 1) {
                await sleep(Math.pow(2, i) * 1000);  // 1s, 2s, 4s
                continue;
            }
            throw err;
        }
    }
}
```

### **3. Data Consistency**

**Transaction Boundaries:**
```python
@transaction.atomic
def bulk_update_prices(updates):
    """All updates succeed or all fail - no partial updates"""
    for update in updates:
        if update['type'] == 'constant':
            update_pricing_constant(**update)
        elif update['type'] == 'option_choice':
            update_option_choice(**update)
    
    # If any update fails, entire transaction rolls back
```

**Referential Integrity:**
```sql
-- Cannot delete calculator if it has active overrides
CREATE OR REPLACE FUNCTION prevent_calculator_delete()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM calculator_parameter_overrides 
        WHERE calculator_id = OLD.id AND is_active = TRUE
    ) THEN
        RAISE EXCEPTION 'Cannot delete calculator with active overrides';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;
```

### **4. Performance Optimization**

**Indexes:**
```sql
-- Fast parameter lookup by name
CREATE INDEX idx_param_name ON calculator_pricing_parameters(parameter_name);

-- Fast override lookup by calculator
CREATE INDEX idx_override_calculator ON calculator_parameter_overrides(calculator_id, is_active);

-- Fast option lookup by calculator
CREATE INDEX idx_option_calculator ON product_options(calculator_id, is_active);

-- Fast choice lookup by option
CREATE INDEX idx_choice_option ON product_option_choices(option_id, is_active);

-- Full-text search on parameter descriptions
CREATE INDEX idx_param_description_fts ON calculator_pricing_parameters 
USING GIN (to_tsvector('english', description));
```

**Query Optimization:**
```sql
-- Materialized view for frequently accessed data
CREATE MATERIALIZED VIEW mv_calculator_config AS
SELECT 
    c.id,
    c.calculator_name,
    COUNT(DISTINCT cpp.id) as total_constants,
    COUNT(DISTINCT po.id) as total_options,
    COUNT(DISTINCT poc.id) as total_choices,
    MAX(GREATEST(cpp.updated_at, po.updated_at)) as last_updated
FROM calculators_registry c
LEFT JOIN calculator_pricing_parameters cpp ON cpp.used_by_calculators @> jsonb_build_array(jsonb_build_object('calculator', c.calculator_name))
LEFT JOIN product_options po ON po.calculator_id = c.id
LEFT JOIN product_option_choices poc ON poc.option_id = po.id
GROUP BY c.id, c.calculator_name;

-- Refresh every hour
CREATE INDEX idx_mv_calculator_config ON mv_calculator_config(calculator_name);
```

---

## 🔄 **MIGRATION PLAN**

### **Phase 1: Complete Pricing Constants System (Week 1)**

**Migration 003: Populate Overrides**
```sql
-- Transform JSONB arrays into override rows
INSERT INTO calculator_parameter_overrides (parameter_id, calculator_id, override_value, reason, is_active)
SELECT 
    cpp.id,
    cr.id,
    (calc->>'value')::numeric,
    'Migrated from extraction',
    TRUE
FROM calculator_pricing_parameters cpp,
     jsonb_array_elements(cpp.used_by_calculators) calc,
     calculators_registry cr
WHERE calc->>'calculator' = cr.calculator_name
AND (calc->>'value')::numeric != cpp.base_value;  -- Only create override if different from base

-- Expected: ~284 override rows
```

### **Phase 2: Build Product Options System (Week 1-2)**

**Migration 004: Create Tables**
```sql
-- Run SQL from "DETAILED SCHEMA DESIGN" section
-- Creates: product_options, product_option_choices, product_option_overrides, product_option_history
```

**Extraction Script: extract_product_options.py**
```python
def extract_options_from_json(json_path):
    """Parse Shopify JSON files and extract OPTIONS arrays"""
    with open(json_path) as f:
        data = json.load(f)
    
    calculator_key = list(data.keys())[0]
    calculator_data = data[calculator_key]
    
    options = []
    for option in calculator_data.get('options', []):
        options.append({
            'option_name': option['name'],
            'field_id': option.get('field_id'),
            'option_type': option.get('type', 'select'),
            'is_required': option.get('required', False),
            'default_choice': option.get('default'),
            'choices': [
                {
                    'choice_title': choice['title'],
                    'price': choice['price'],
                    'price_type': choice.get('price_type', 'fixed'),
                    'sku': choice.get('sku'),
                    'display_order': idx
                }
                for idx, choice in enumerate(option['options'])
            ]
        })
    
    return options

# Expected output: ~150 options, ~500 choices across 30 calculators
```

### **Phase 3: Backend API (Week 2-3)**

**Endpoints to Build:**
- Pricing Constants CRUD (8 endpoints)
- Product Options CRUD (12 endpoints)
- Unified Calculator Config (2 endpoints)
- Bulk Operations (2 endpoints)
- **Total:** 24 endpoints

**Technology Stack:**
- Flask (existing infrastructure)
- SQLAlchemy ORM
- Marshmallow validation
- Flask-CORS
- WebSocket support (flask-socketio)

### **Phase 4: UI Implementation (Week 3-5)**

**Components to Build:**
1. Pricing Constants Manager (4 components)
2. Product Options Manager (4 components)
3. Calculator Config Dashboard (3 components)
4. Shared utilities (Tabulator config, API client, WebSocket handler)

**Total:** ~11 components + utilities

### **Phase 5: AI Tool Layer (Week 5)**

**Tools to Implement:**
- Query tools (3)
- Update tools (2)
- Validation tools (1)
- Batch operations (1)
- **Total:** 7 tools

---

## 📊 **SUCCESS METRICS**

### **Data Quality**
- ✅ Zero duplicate parameters (case-insensitive)
- ✅ 100% of parameters have statistics calculated
- ✅ All foreign keys enforced
- ✅ All prices positive (CHECK constraint)
- ✅ All required fields populated

### **Performance**
- API response time < 200ms (95th percentile)
- UI table load time < 1s for 500 rows
- Bulk update (100 items) < 5s
- WebSocket latency < 100ms

### **Reliability**
- 99.9% uptime
- Zero data loss
- Complete audit trail (all changes logged)
- Rollback capability for last 30 days

### **User Experience**
- Inline editing in tables (no modal for simple edits)
- Real-time validation feedback
- Conflict detection with user-friendly messaging
- One-click export/import

---

## 🎯 **NEXT IMMEDIATE ACTIONS**

### **Decision Required from User:**

**Option A: Complete Pricing Constants First** (Recommended)
1. Run Migration 003 (populate overrides) - 30 minutes
2. Test override system with sample queries
3. Build pricing constants API endpoints
4. Build pricing constants UI
5. **THEN** tackle product options

**Option B: Build Product Options System**
1. Extract options from 30 Shopify JSON files - 2-3 hours
2. Run Migration 004 (create tables) - 30 minutes
3. Load extracted options data
4. Build product options API endpoints
5. Build product options UI

**Option C: Parallel Development** (Fastest but more complex)
1. Migration 003 + Migration 004 simultaneously
2. Extraction script runs in parallel
3. Two developers: one on constants, one on options
4. Integration testing at end

---

## 📝 **OPEN QUESTIONS**

1. **User Permissions:** Do we need role-based access? (Admin, Editor, Viewer)
2. **Customer Segments:** Should product option overrides support customer tiers?
3. **Currency Support:** Multi-currency pricing or single currency (AUD)?
4. **Bulk Import:** Excel/CSV import for non-technical users?
5. **API Rate Limiting:** Should we throttle AI tool layer requests?
6. **Notifications:** Email alerts when prices change above threshold?
7. **Approval Workflow:** Require manager approval for price changes over $X?

---

**End of Architecture Plan**
