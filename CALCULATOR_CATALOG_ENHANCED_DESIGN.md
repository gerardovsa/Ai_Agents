# Enhanced Calculator Pricing Catalog - WITH UPDATE PROPAGATION

**NEW FEATURES:**
1. ✅ Track which calculators use each parameter (`used_by_calculators[]`)
2. ✅ Update propagation (change parameter → updates all calculators)
3. ✅ Calculator override system (custom values per calculator)
4. ✅ Version history (audit trail of changes)
5. ✅ AI-powered bulk updates via UI table

---

## ENHANCED TABLE STRUCTURE

### Table 1: `calculator_pricing_parameters` (Master Catalog)

**Core concept:** Each parameter tracks ALL calculators using it

```sql
CREATE TABLE calculator_pricing_parameters (
    id SERIAL PRIMARY KEY,
    
    -- Parameter Identity
    parameter_name VARCHAR(100) UNIQUE NOT NULL,    -- 'impos_setup', 'vinyl_gloss'
    parameter_label VARCHAR(200),                   -- "Imposition Setup Cost"
    category VARCHAR(50) NOT NULL,                  -- 'setup', 'material', 'print', 'margin'
    subcategory VARCHAR(50),                        -- 'imposition', 'vinyl', 'digital'
    
    -- Default/Base Value (used if no override)
    base_value DECIMAL(10,4),                       -- 15.00
    value_unit VARCHAR(50),                         -- 'dollars', 'per_sqm', 'percentage'
    
    -- 🎯 CALCULATOR TRACKING (NEW!)
    used_by_calculators JSONB NOT NULL DEFAULT '[]'::JSONB,
    -- Structure: [
    --   {"calculator": "PremiumBusinessCards", "value": 15.00, "override": false},
    --   {"calculator": "NotepadsA4", "value": 30.00, "override": true},
    --   {"calculator": "BollardSigns", "value": 40.00, "override": true}
    -- ]
    
    total_usage_count INTEGER GENERATED ALWAYS AS (jsonb_array_length(used_by_calculators)) STORED,
    
    -- Context
    applies_when JSONB,                             -- Conditional logic
    calculation_formula TEXT,                       -- How to use in formulas
    description TEXT,
    
    -- 📊 STATISTICS (NEW!)
    most_common_value DECIMAL(10,4),                -- Most frequently used value
    value_range JSONB,                              -- {"min": 15.00, "max": 40.00, "values": [15, 30, 40]}
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_modified_by VARCHAR(100),                  -- AI agent or user who changed it
    
    CONSTRAINT valid_usage CHECK (jsonb_typeof(used_by_calculators) = 'array')
);

CREATE INDEX idx_param_category ON calculator_pricing_parameters(category);
CREATE INDEX idx_param_usage ON calculator_pricing_parameters USING GIN(used_by_calculators);
CREATE INDEX idx_param_name_search ON calculator_pricing_parameters USING GIN(to_tsvector('english', parameter_label || ' ' || description));
```

### Table 2: `calculator_parameter_overrides` (Custom Values)

**Core concept:** Calculators can override base values with custom values

```sql
CREATE TABLE calculator_parameter_overrides (
    id SERIAL PRIMARY KEY,
    
    calculator_name VARCHAR(100) NOT NULL,          -- 'BollardSigns'
    parameter_id INTEGER REFERENCES calculator_pricing_parameters(id) ON DELETE CASCADE,
    
    -- Override Value
    override_value DECIMAL(10,4) NOT NULL,          -- 40.00 (instead of base 15.00)
    override_reason TEXT,                           -- "Signs require larger format setup"
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100),
    
    CONSTRAINT unique_calc_param UNIQUE(calculator_name, parameter_id)
);

CREATE INDEX idx_override_calc ON calculator_parameter_overrides(calculator_name);
CREATE INDEX idx_override_param ON calculator_parameter_overrides(parameter_id);
```

### Table 3: `calculator_parameter_history` (Audit Trail)

**Core concept:** Track every change to parameters and who made them

```sql
CREATE TABLE calculator_parameter_history (
    id SERIAL PRIMARY KEY,
    
    parameter_id INTEGER REFERENCES calculator_pricing_parameters(id),
    
    -- Change Details
    change_type VARCHAR(50) NOT NULL,               -- 'value_update', 'calculator_added', 'calculator_removed'
    old_value JSONB,                                -- Previous state
    new_value JSONB,                                -- New state
    affected_calculators TEXT[],                    -- Which calculators were updated
    
    -- Metadata
    changed_by VARCHAR(100),                        -- AI agent ID or user email
    change_reason TEXT,                             -- "Updated to match supplier pricing"
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_history_param ON calculator_parameter_history(parameter_id);
CREATE INDEX idx_history_date ON calculator_parameter_history(created_at DESC);
```

### Table 4: `calculators_registry` (Calculator Master List)

**Core concept:** Central registry of all calculators with their parameters

```sql
CREATE TABLE calculators_registry (
    id SERIAL PRIMARY KEY,
    
    calculator_name VARCHAR(100) UNIQUE NOT NULL,   -- 'PremiumBusinessCards'
    calculator_type VARCHAR(50),                    -- 'shopify', 'god', 'custom'
    display_name VARCHAR(200),                      -- "Premium Business Cards"
    
    -- Parameters Used (with actual values)
    parameters_used JSONB NOT NULL DEFAULT '{}'::JSONB,
    -- Structure: {
    --   "impos_setup": {"value": 15.00, "source": "base"},
    --   "guilo_setup": {"value": 10.00, "source": "base"},
    --   "vinyl_gloss": {"value": 40.00, "source": "override"}
    -- }
    
    -- Metadata
    product_category VARCHAR(50),                   -- 'cards', 'signs', 'books'
    file_path TEXT,                                 -- Path to Python file
    is_active BOOLEAN DEFAULT true,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_calc_type ON calculators_registry(calculator_type);
CREATE INDEX idx_calc_category ON calculators_registry(product_category);
CREATE INDEX idx_calc_params ON calculators_registry USING GIN(parameters_used);
```

---

## EXAMPLE DATA WITH CALCULATOR TRACKING

### Example 1: `impos_setup` - Used by 12 calculators

```sql
INSERT INTO calculator_pricing_parameters VALUES
(1, 'impos_setup', 'Imposition Setup Cost', 'setup', 'imposition',
 15.00, 'dollars',
 '[
   {"calculator": "PremiumBusinessCards", "value": 15.00, "override": false, "file": "PremiumBusinessCards_Shopify_Calculator.py"},
   {"calculator": "EconomicalBusinessCards", "value": 15.00, "override": false, "file": "EconomicalBusinessCards_Shopify_Calculator.py"},
   {"calculator": "NotepadsA4", "value": 30.00, "override": true, "file": "NotepadsA4_Shopify_Calculator.py"},
   {"calculator": "NotepadsA5", "value": 30.00, "override": true, "file": "NotepadsA5_Shopify_Calculator.py"},
   {"calculator": "BollardSigns", "value": 40.00, "override": true, "file": "BollardSigns_Shopify_Calculator.py"},
   {"calculator": "ConstructionSigns", "value": 28.00, "override": true, "file": "ConstructionSigns_Shopify_Calculator.py"},
   {"calculator": "CustomVinylStickers", "value": 35.00, "override": true, "file": "CustomVinylStickers_Shopify_Calculator.py"},
   {"calculator": "Letterheads", "value": 15.00, "override": false, "file": "PrintedLetterheads_Shopify_Calculator.py"},
   {"calculator": "WithComplimentsSlips", "value": 15.00, "override": false, "file": "WithComplimentsSlips_Shopify_Calculator.py"},
   {"calculator": "PremiumBookmarks", "value": 15.00, "override": false, "file": "PremiumBookmarks_Shopify_Calculator.py"},
   {"calculator": "FoldedFlyers", "value": 20.00, "override": true, "file": "FoldedFlyers_Shopify_Calculator.py"},
   {"calculator": "CustomPosterPrinting", "value": 25.00, "override": true, "file": "CustomPosterPrinting_Shopify_Calculator.py"}
 ]'::JSONB,
 -- total_usage_count auto-calculated = 12
 NULL,
 'Fixed setup cost for imposition (plate/digital setup)',
 'Varies by product size and complexity',
 15.00, -- most_common_value
 '{"min": 15.00, "max": 40.00, "median": 20.00, "values": [15, 20, 25, 28, 30, 35, 40]}'::JSONB,
 NOW(), NOW(), 'system_import');

-- Create overrides for calculators with custom values
INSERT INTO calculator_parameter_overrides VALUES
(1, 'NotepadsA4', 1, 30.00, 'Notepads require larger setup due to padding glue', true, NOW(), 'system_import'),
(2, 'BollardSigns', 1, 40.00, 'Large format signs require extensive imposition setup', true, NOW(), 'system_import'),
(3, 'ConstructionSigns', 1, 28.00, 'Construction signs mid-size format', true, NOW(), 'system_import');
```

### Example 2: `vinyl_gloss` - Used by 2 calculators

```sql
INSERT INTO calculator_pricing_parameters VALUES
(10, 'vinyl_gloss', 'Gloss Vinyl Material Cost', 'material', 'vinyl',
 25.00, 'per_sqm',
 '[
   {"calculator": "CustomVinylStickers", "value": 25.00, "override": false, "file": "CustomVinylStickers_Shopify_Calculator.py"},
   {"calculator": "BollardSigns", "value": 28.00, "override": true, "file": "BollardSigns_Shopify_Calculator.py"}
 ]'::JSONB,
 -- total_usage_count = 2
 '{"finish": "gloss"}'::JSONB,
 'area_m2 * vinyl_gloss * quantity',
 'Premium gloss vinyl for sticker and sign printing',
 25.00,
 '{"min": 25.00, "max": 28.00, "values": [25, 28]}'::JSONB,
 NOW(), NOW(), 'system_import');
```

---

## AI-POWERED UPDATE SYSTEM

### Use Case 1: Bulk Update Base Value

**Scenario:** Supplier increases vinyl prices by 10%

```sql
-- AI executes this through the catalog management tool
UPDATE calculator_pricing_parameters 
SET 
    base_value = base_value * 1.10,
    updated_at = NOW(),
    last_modified_by = 'ai_agent_alpha'
WHERE parameter_name = 'vinyl_gloss';

-- Log the change
INSERT INTO calculator_parameter_history VALUES
(DEFAULT, 10, 'value_update',
 '{"base_value": 25.00}'::JSONB,
 '{"base_value": 27.50}'::JSONB,
 ARRAY['CustomVinylStickers'],  -- Only affects calculators using base value
 'ai_agent_alpha',
 'Supplier price increase 10% effective Dec 2025',
 NOW());

-- Result: CustomVinylStickers now uses $27.50
-- BollardSigns still uses override $28.00 (unchanged)
```

### Use Case 2: Update All Calculators (Including Overrides)

**Scenario:** GST rate changes from 10% to 15% (government mandate)

```sql
-- Update base value
UPDATE calculator_pricing_parameters
SET base_value = 1.15
WHERE parameter_name = 'GST_RATE';

-- Update ALL overrides (force update)
UPDATE calculator_parameter_overrides
SET override_value = 1.15
WHERE parameter_id = (SELECT id FROM calculator_pricing_parameters WHERE parameter_name = 'GST_RATE');

-- Update calculator registry
UPDATE calculators_registry
SET 
    parameters_used = jsonb_set(
        parameters_used,
        '{GST_RATE,value}',
        '1.15'::jsonb
    ),
    updated_at = NOW()
WHERE parameters_used ? 'GST_RATE';

-- Log change
INSERT INTO calculator_parameter_history VALUES
(DEFAULT, (SELECT id FROM calculator_pricing_parameters WHERE parameter_name = 'GST_RATE'),
 'forced_update_all',
 '{"base_value": 1.10}'::JSONB,
 '{"base_value": 1.15}'::JSONB,
 (SELECT ARRAY_AGG(calculator_name) FROM calculators_registry WHERE parameters_used ? 'GST_RATE'),
 'ai_agent_alpha',
 'Government GST rate change - mandatory update all calculators',
 NOW());
```

### Use Case 3: Add New Parameter to Multiple Calculators

**Scenario:** Add "eco_fee" (environmental levy) to all card products

```sql
-- Create parameter
INSERT INTO calculator_pricing_parameters VALUES
(DEFAULT, 'eco_fee', 'Environmental Sustainability Fee', 'fee', 'regulatory',
 2.50, 'dollars',
 '[]'::JSONB,  -- No calculators yet
 NULL,
 'fixed_cost',
 'Government-mandated environmental fee for paper products',
 2.50,
 '{"min": 2.50, "max": 2.50, "values": [2.50]}'::JSONB,
 NOW(), NOW(), 'ai_agent_alpha');

-- Add to all card calculators
WITH card_calculators AS (
    SELECT calculator_name FROM calculators_registry
    WHERE product_category = 'cards'
)
UPDATE calculator_pricing_parameters
SET used_by_calculators = (
    SELECT jsonb_agg(
        jsonb_build_object(
            'calculator', calculator_name,
            'value', 2.50,
            'override', false
        )
    )
    FROM card_calculators
)
WHERE parameter_name = 'eco_fee';

-- Update calculator registry for all cards
UPDATE calculators_registry
SET 
    parameters_used = parameters_used || jsonb_build_object('eco_fee', jsonb_build_object('value', 2.50, 'source', 'base')),
    updated_at = NOW()
WHERE product_category = 'cards';
```

---

## AI MANAGEMENT UI - TABLE VIEW

### Interactive Table Interface

AI can present calculators and parameters in a **spreadsheet-like UI** for bulk editing:

```
📊 CALCULATOR PARAMETER MATRIX

Parameter          | Base Value | Premium BC | Economical BC | Notepads A4 | Bollard Signs | Total Usage
-------------------|------------|------------|---------------|-------------|---------------|-------------
impos_setup        | $15.00     | $15.00     | $15.00        | $30.00 ⚠️   | $40.00 ⚠️     | 12 calcs
guilo_setup        | $10.00     | $10.00     | $10.00        | $20.00 ⚠️   | N/A           | 8 calcs
vinyl_gloss        | $25.00/m²  | N/A        | N/A           | N/A         | $28.00 ⚠️     | 2 calcs
print_colour       | $0.048/sh  | $0.048     | $0.035 ⚠️     | $0.050 ⚠️   | N/A           | 15 calcs
GST_RATE           | 1.10       | 1.10       | 1.10          | 1.10        | 1.10          | 30 calcs

Legend:
✅ Uses base value
⚠️ Custom override
N/A Not used by this calculator

[Bulk Actions]
- Update all base values by %
- Apply override to selected calculators
- Remove overrides (reset to base)
- Export to CSV
- Import from CSV
```

### AI Commands for Table Operations

```python
# AI tool: update_parameter_bulk()
update_parameter_bulk(
    parameter_name="impos_setup",
    new_base_value=18.00,
    update_overrides=False,  # Keep custom overrides
    reason="Cost adjustment Q4 2025"
)

# AI tool: sync_parameter_to_calculators()
sync_parameter_to_calculators(
    parameter_name="eco_fee",
    calculator_filter={"product_category": "cards"},
    value=2.50,
    force_override=True
)

# AI tool: export_calculator_matrix()
export_calculator_matrix(
    format="csv",
    include_columns=["parameter", "base_value", "PremiumBusinessCards", "BollardSigns"],
    output_file="calculator_pricing_matrix.csv"
)
```

---

## BENEFITS OF THIS SYSTEM

### 1. TRANSPARENCY
- See exactly which calculators use each parameter
- Understand pricing variations across products
- Audit trail: who changed what and why

### 2. EFFICIENCY
- Update 12 calculators at once (change base value)
- Selective updates (keep overrides intact)
- Bulk operations via AI table interface

### 3. CONSISTENCY
- Shared parameters ensure consistency
- Override system for legitimate exceptions
- AI can flag inconsistencies

### 4. FLEXIBILITY
- Base values with calculator-specific overrides
- Easy to add new calculators (inherit base values)
- Easy to add new parameters to existing calculators

### 5. AUDITABILITY
- History table tracks every change
- Know when/why parameters changed
- Rollback capability

---

## QUERY EXAMPLES

### Find all calculators using a parameter
```sql
SELECT 
    parameter_name,
    jsonb_array_elements(used_by_calculators)->>'calculator' as calculator,
    jsonb_array_elements(used_by_calculators)->>'value' as value,
    jsonb_array_elements(used_by_calculators)->>'override' as is_override
FROM calculator_pricing_parameters
WHERE parameter_name = 'impos_setup'
ORDER BY (jsonb_array_elements(used_by_calculators)->>'value')::numeric;
```

### Find parameters with high variation (potential inconsistencies)
```sql
SELECT 
    parameter_name,
    base_value,
    (value_range->>'min')::numeric as min_value,
    (value_range->>'max')::numeric as max_value,
    ((value_range->>'max')::numeric - (value_range->>'min')::numeric) / NULLIF((value_range->>'min')::numeric, 0) * 100 as variation_pct
FROM calculator_pricing_parameters
WHERE (value_range->>'max')::numeric / NULLIF((value_range->>'min')::numeric, 1) > 1.5  -- More than 50% variation
ORDER BY variation_pct DESC;
```

### Find calculators that override a parameter
```sql
SELECT 
    parameter_name,
    base_value,
    calculator_name,
    override_value,
    override_reason
FROM calculator_parameter_overrides o
JOIN calculator_pricing_parameters p ON o.parameter_id = p.id
WHERE o.is_active = true
ORDER BY parameter_name, calculator_name;
```

---

## NEXT STEPS

**Should I:**

1. ✅ Create the enhanced SQL migration script (4 tables with tracking)
2. ✅ Build Python script to populate `used_by_calculators` from extracted data
3. ✅ Create AI management tools (`update_parameter_bulk`, `sync_calculators`, etc.)
4. ✅ Build the spreadsheet-like UI for bulk editing

**This system turns your catalog into a LIVING PRICING MANAGEMENT PLATFORM!** 🎯
