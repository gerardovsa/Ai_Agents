# Calculator Pricing Catalog - Database Table Design

**Extracted Data:** 30 calculators, 363 unique pricing values
**Goal:** Store pricing catalog for AI to query when creating new calculators

---

## OPTION A: "ATOMIC" STRUCTURE (Hundreds of Individual Rows)

### Table: `calculator_pricing_catalog_atomic`

**Structure:** Each pricing parameter gets its own row

```sql
CREATE TABLE calculator_pricing_catalog_atomic (
    id SERIAL PRIMARY KEY,
    
    -- Classification
    category VARCHAR(50) NOT NULL,              -- 'setup', 'material', 'print', 'finishing', 'labor', 'margin'
    subcategory VARCHAR(50),                    -- 'imposition', 'guillotine', 'artwork', 'stock', 'click'
    
    -- Parameter Identity
    parameter_name VARCHAR(100) NOT NULL,       -- 'impos_setup', 'vinyl_gloss_cost', 'print_colour'
    parameter_label VARCHAR(200),               -- Human-readable: "Imposition Setup Cost"
    
    -- Pricing Data
    base_value DECIMAL(10,4),                   -- 15.00, 0.048, 28.00
    value_unit VARCHAR(50),                     -- 'dollars', 'per_sqm', 'per_sheet', 'percentage'
    
    -- Applicability
    calculator_types TEXT[],                    -- ['business_cards', 'flyers', 'notepads']
    product_categories TEXT[],                  -- ['cards', 'signs', 'books', 'promotional']
    
    -- Context & Rules
    applies_when JSONB,                         -- Conditions: {"has_celloglaze": true, "quantity_min": 500}
    calculation_formula TEXT,                   -- How to use: "area_m2 * base_value * quantity"
    
    -- Metadata
    description TEXT,
    source_calculator VARCHAR(100),             -- Original calculator this came from
    usage_frequency INTEGER DEFAULT 0,          -- How many calculators use this
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_parameter UNIQUE(parameter_name, category, subcategory)
);

CREATE INDEX idx_catalog_atomic_category ON calculator_pricing_catalog_atomic(category);
CREATE INDEX idx_catalog_atomic_types ON calculator_pricing_catalog_atomic USING GIN(calculator_types);
CREATE INDEX idx_catalog_atomic_search ON calculator_pricing_catalog_atomic USING GIN(to_tsvector('english', parameter_label || ' ' || description));
```

### Example Rows (Option A):

```sql
-- Setup Costs (15 rows)
INSERT INTO calculator_pricing_catalog_atomic VALUES
(1, 'setup', 'imposition', 'impos_setup_premium', 'Imposition Setup (Premium Products)', 
 15.00, 'dollars', 
 ARRAY['business_cards', 'notepads', 'letterheads'], 
 ARRAY['cards', 'stationery'],
 '{"product_tier": "premium"}'::JSONB,
 'fixed_cost',
 'Fixed cost added to every quote for plate/digital setup',
 'PremiumBusinessCards', 5, NOW(), NOW()),

(2, 'setup', 'imposition', 'impos_setup_signs', 'Imposition Setup (Signs)', 
 40.00, 'dollars',
 ARRAY['bollard_signs', 'construction_signs', 'election_signs'],
 ARRAY['signs'],
 '{"product_category": "signs"}'::JSONB,
 'fixed_cost',
 'Higher setup cost for large format sign printing',
 'BollardSigns', 8, NOW(), NOW()),

(3, 'setup', 'guillotine', 'guilo_setup', 'Guillotine Cutting Setup',
 10.00, 'dollars',
 ARRAY['business_cards', 'flyers', 'bookmarks'],
 ARRAY['cards', 'promotional'],
 NULL,
 'fixed_cost',
 'Setup cost for guillotine cutting operation',
 'PremiumBusinessCards', 12, NOW(), NOW());

-- Material Costs (50+ rows)
INSERT INTO calculator_pricing_catalog_atomic VALUES
(10, 'material', 'vinyl', 'vinyl_gloss', 'Gloss Vinyl Material',
 25.00, 'per_sqm',
 ARRAY['vinyl_stickers', 'custom_stickers'],
 ARRAY['stickers'],
 '{"finish": "gloss"}'::JSONB,
 'area_m2 * base_value * quantity',
 'Premium gloss vinyl for sticker printing',
 'CustomVinylStickers', 2, NOW(), NOW()),

(11, 'material', 'vinyl', 'vinyl_matte', 'Matte Vinyl Material',
 22.00, 'per_sqm',
 ARRAY['vinyl_stickers', 'custom_stickers'],
 ARRAY['stickers'],
 '{"finish": "matte"}'::JSONB,
 'area_m2 * base_value * quantity',
 'Standard matte vinyl for sticker printing',
 'CustomVinylStickers', 2, NOW(), NOW()),

(12, 'material', 'metal', 'aluminium_sheet', 'Aluminium Sheet Material',
 28.00, 'per_sqm',
 ARRAY['bollard_signs', 'construction_signs'],
 ARRAY['signs'],
 '{"material_type": "aluminium"}'::JSONB,
 'area_m2 * base_value * quantity',
 'Aluminium sheet for metal sign production',
 'BollardSigns', 3, NOW(), NOW());

-- Print Costs (30+ rows)
INSERT INTO calculator_pricing_catalog_atomic VALUES
(20, 'print', 'digital', 'print_colour_premium', 'Full Colour Digital Print (Premium)',
 0.048, 'per_sheet',
 ARRAY['business_cards'],
 ARRAY['cards'],
 '{"print_mode": "colour", "stock_tier": "premium"}'::JSONB,
 'sheets_needed * sides_multiplier * base_value',
 'CMYK full colour printing on premium stock',
 'PremiumBusinessCards', 1, NOW(), NOW()),

(21, 'print', 'digital', 'print_colour_standard', 'Full Colour Digital Print (Standard)',
 0.05, 'per_sheet',
 ARRAY['notepads', 'flyers'],
 ARRAY['stationery'],
 '{"print_mode": "colour"}'::JSONB,
 'sheets_needed * sides_multiplier * base_value',
 'CMYK full colour printing on standard stock',
 'NotepadsA4', 8, NOW(), NOW());

-- Profit Margins (20+ rows for different tiers)
INSERT INTO calculator_pricing_catalog_atomic VALUES
(30, 'margin', 'profit', 'profit_notepads_tier1', 'Profit Margin: Notepads (Up to $500)',
 0.80, 'percentage',
 ARRAY['notepads_a4', 'notepads_a5', 'notepads_a6'],
 ARRAY['stationery'],
 '{"subtotal_min": 0, "subtotal_max": 500}'::JSONB,
 'biz_cost * base_value',
 '80% profit margin for small notepad orders (sub-$500)',
 'NotepadsA4', 3, NOW(), NOW()),

(31, 'margin', 'profit', 'profit_notepads_tier2', 'Profit Margin: Notepads ($500-$1000)',
 0.80, 'percentage',
 ARRAY['notepads_a4', 'notepads_a5', 'notepads_a6'],
 ARRAY['stationery'],
 '{"subtotal_min": 500, "subtotal_max": 1000}'::JSONB,
 'biz_cost * base_value',
 '80% profit margin for medium notepad orders',
 'NotepadsA4', 3, NOW(), NOW());
```

### PROS of Option A:
- ✅ Simple queries: `WHERE category = 'setup'`
- ✅ Easy to add new parameters individually
- ✅ Clear relationships (each row = one concept)
- ✅ Good for analytics: "What's average setup cost across products?"

### CONS of Option A:
- ❌ **300-500 rows** (overwhelming to browse)
- ❌ Hard to see "complete picture" for a calculator
- ❌ Context loss: Multiple rows for tiered pricing
- ❌ Redundant metadata (calculator_types repeated 300 times)

---

## OPTION B: "GROUPED" STRUCTURE (Logical Bundles with JSONB)

### Table: `calculator_pricing_catalog_grouped`

**Structure:** Related parameters grouped together logically

```sql
CREATE TABLE calculator_pricing_catalog_grouped (
    id SERIAL PRIMARY KEY,
    
    -- Group Identity
    group_name VARCHAR(100) NOT NULL,           -- 'business_cards_setup', 'sign_materials', 'notepad_margins'
    group_label VARCHAR(200),                   -- Human-readable: "Business Cards - Setup Costs"
    category VARCHAR(50) NOT NULL,              -- 'setup', 'material', 'print', 'finishing', 'margin'
    
    -- Pricing Data (JSONB for flexibility)
    pricing_data JSONB NOT NULL,                -- All related parameters in structured JSON
    
    -- Applicability
    calculator_types TEXT[],                    -- ['business_cards', 'premium_business_cards']
    product_categories TEXT[],                  -- ['cards']
    
    -- Context
    applies_when JSONB,                         -- Conditions
    calculation_notes TEXT,                     -- Formula explanations
    
    -- Metadata
    description TEXT,
    source_calculators TEXT[],                  -- All calculators using this group
    usage_count INTEGER DEFAULT 0,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_group UNIQUE(group_name, category)
);

CREATE INDEX idx_catalog_grouped_category ON calculator_pricing_catalog_grouped(category);
CREATE INDEX idx_catalog_grouped_types ON calculator_pricing_catalog_grouped USING GIN(calculator_types);
CREATE INDEX idx_catalog_grouped_pricing ON calculator_pricing_catalog_grouped USING GIN(pricing_data);
CREATE INDEX idx_catalog_grouped_search ON calculator_pricing_catalog_grouped USING GIN(to_tsvector('english', group_label || ' ' || description));
```

### Example Rows (Option B):

```sql
-- Setup Costs Group (1 row = all setup costs for business cards)
INSERT INTO calculator_pricing_catalog_grouped VALUES
(1, 'business_cards_setup_costs', 'Business Cards - Setup Costs', 'setup',
 '{
   "impos_setup": {"value": 15.00, "unit": "dollars", "description": "Imposition setup"},
   "guilo_setup": {"value": 10.00, "unit": "dollars", "description": "Guillotine setup"},
   "extra_artwork": {"value": 15.00, "unit": "dollars", "description": "Per extra artwork (first free)"},
   "cello_setup": {"value": 17.00, "unit": "dollars", "description": "Celloglaze lamination setup", "applies_when": {"celloglaze": "not None"}}
 }'::JSONB,
 ARRAY['business_cards', 'premium_business_cards', 'economical_business_cards'],
 ARRAY['cards'],
 NULL,
 'Total setup = impos + guilo + cello (if applicable) + (artworks-1)*extra_artwork',
 'Fixed costs added once per job regardless of quantity',
 ARRAY['PremiumBusinessCards', 'EconomicalBusinessCards'], 2,
 NOW(), NOW());

-- Material Costs Group (1 row = all vinyl types)
INSERT INTO calculator_pricing_catalog_grouped VALUES
(2, 'vinyl_materials', 'Vinyl Materials - Stickers', 'material',
 '{
   "gloss": {"value": 25.00, "unit": "per_sqm", "description": "Premium gloss vinyl"},
   "matte": {"value": 22.00, "unit": "per_sqm", "description": "Standard matte vinyl"},
   "calculation": "area_m2 * material_cost * quantity"
 }'::JSONB,
 ARRAY['vinyl_stickers', 'custom_stickers'],
 ARRAY['stickers'],
 NULL,
 'Cost = (width_mm * height_mm / 1,000,000) * vinyl_cost_per_m2 * quantity',
 'Vinyl material costs for sticker production',
 ARRAY['CustomVinylStickers'], 1,
 NOW(), NOW());

-- Sign Materials Group (1 row = all sign materials)
INSERT INTO calculator_pricing_catalog_grouped VALUES
(3, 'sign_materials', 'Sign Materials - Metal & Corflute', 'material',
 '{
   "aluminium": {"value": 28.00, "unit": "per_sqm", "description": "Aluminium sheet (premium)"},
   "metal": {"value": 22.00, "unit": "per_sqm", "description": "Standard metal sheet"},
   "corflute_3mm": {"value": 6.50, "unit": "per_sqm", "description": "3mm Corflute board"},
   "corflute_5mm": {"value": 8.50, "unit": "per_sqm", "description": "5mm Corflute board"}
 }'::JSONB,
 ARRAY['bollard_signs', 'construction_signs', 'election_signs'],
 ARRAY['signs'],
 NULL,
 'Cost = (width_mm * height_mm / 1,000,000) * material_rate * quantity',
 'Material costs for sign production (metal and corflute options)',
 ARRAY['BollardSigns', 'ConstructionSigns', 'ElectionSigns'], 3,
 NOW(), NOW());

-- Print Costs Group (1 row = all print modes)
INSERT INTO calculator_pricing_catalog_grouped VALUES
(4, 'digital_print_costs', 'Digital Print Costs - Standard Products', 'print',
 '{
   "colour_premium": {"value": 0.048, "unit": "per_sheet", "applies_to": ["business_cards"]},
   "colour_standard": {"value": 0.050, "unit": "per_sheet", "applies_to": ["notepads", "flyers"]},
   "bw_standard": {"value": 0.020, "unit": "per_sheet", "applies_to": ["business_cards", "notepads"]},
   "bw_economy": {"value": 0.025, "unit": "per_sheet", "applies_to": ["notepads"]},
   "calculation": "sheets_needed * sides_multiplier * print_cost"
 }'::JSONB,
 ARRAY['business_cards', 'notepads', 'flyers'],
 ARRAY['cards', 'stationery'],
 NULL,
 'Cost = (quantity / items_per_sheet) * waste_factor * sides * print_rate',
 'Digital printing costs for CMYK colour and black & white',
 ARRAY['PremiumBusinessCards', 'NotepadsA4', 'NotepadsA5'], 5,
 NOW(), NOW());

-- Profit Margins Group with Tiers (1 row = all tiers)
INSERT INTO calculator_pricing_catalog_grouped VALUES
(5, 'profit_margins_notepads', 'Profit Margins - Notepads (13 Tiers)', 'margin',
 '{
   "tiers": [
     {"subtotal_max": 500, "rate": 0.80, "label": "Up to $500: 80%"},
     {"subtotal_max": 1000, "rate": 0.80, "label": "$500-$1000: 80%"},
     {"subtotal_max": 1500, "rate": 0.80, "label": "$1000-$1500: 80%"},
     {"subtotal_max": 2000, "rate": 0.75, "label": "$1500-$2000: 75%"},
     {"subtotal_max": 2500, "rate": 0.72, "label": "$2000-$2500: 72%"},
     {"subtotal_max": 3000, "rate": 0.72, "label": "$2500-$3000: 72%"},
     {"subtotal_max": 4000, "rate": 0.65, "label": "$3000-$4000: 65%"},
     {"subtotal_max": 5000, "rate": 0.55, "label": "$4000-$5000: 55%"},
     {"subtotal_max": 7500, "rate": 0.52, "label": "$5000-$7500: 52%"},
     {"subtotal_max": 10000, "rate": 0.47, "label": "$7500-$10k: 47%"},
     {"subtotal_max": 15000, "rate": 0.42, "label": "$10k-$15k: 42%"},
     {"subtotal_max": 20000, "rate": 0.41, "label": "$15k-$20k: 41%"},
     {"subtotal_max": null, "rate": 0.41, "label": "Over $20k: 41%"}
   ],
   "calculation": "Find tier where biz_cost <= subtotal_max, return rate"
 }'::JSONB,
 ARRAY['notepads_a4', 'notepads_a5', 'notepads_a6'],
 ARRAY['stationery'],
 NULL,
 'Profit = biz_cost * margin_rate (based on subtotal tier)',
 '13-tier profit margin structure for notepad products (80% down to 41%)',
 ARRAY['NotepadsA4', 'NotepadsA5', 'NotepadsA6'], 3,
 NOW(), NOW());

-- Stock Costs Group (1 row = all stock types with per-1000-sheets pricing)
INSERT INTO calculator_pricing_catalog_grouped VALUES
(6, 'card_stock_costs', 'Card Stock Costs - Business Cards', 'material',
 '{
   "satin_350gsm": {"value": 180.00, "unit": "per_1000_sheets", "description": "Satin 350GSM (standard premium)"},
   "king_kong_420gsm": {"value": 300.00, "unit": "per_1000_sheets", "description": "King Kong High Bulk 420GSM (ultra-premium)"},
   "ecostar_350gsm": {"value": 500.00, "unit": "per_1000_sheets", "description": "EcoStar 350GSM Uncoated (eco-friendly premium)"},
   "calculation": "(sheets_needed / 1000) * stock_cost_per_1000",
   "cards_per_sheet": {"90x55mm": 21, "90x45mm": 30}
 }'::JSONB,
 ARRAY['business_cards', 'premium_business_cards'],
 ARRAY['cards'],
 NULL,
 'sheets_needed = (quantity / cards_per_sheet) * waste_factor; cost = sheets * rate/1000',
 'Premium card stock pricing for business cards (per 1000 sheets)',
 ARRAY['PremiumBusinessCards'], 1,
 NOW(), NOW());
```

### PROS of Option B:
- ✅ **50-80 rows total** (easy to browse)
- ✅ Complete context preserved (all tiers together)
- ✅ AI sees "full picture" for each pricing group
- ✅ Less redundancy (metadata stored once per group)
- ✅ Flexible JSONB structure (add fields without schema changes)

### CONS of Option B:
- ❌ More complex queries: `WHERE pricing_data->>'vinyl_gloss' IS NOT NULL`
- ❌ Harder to query individual parameters
- ❌ Requires JSON knowledge for queries
- ❌ Less normalized (violates 1NF slightly)

---

## RECOMMENDATION: **HYBRID APPROACH (Best of Both Worlds)**

### Two Tables Working Together:

```sql
-- TABLE 1: Grouped catalog (for AI context & browsing)
CREATE TABLE calculator_pricing_groups (
    id SERIAL PRIMARY KEY,
    group_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL,
    pricing_data JSONB NOT NULL,
    calculator_types TEXT[],
    description TEXT,
    -- ... (same as Option B)
);

-- TABLE 2: Atomic lookup (for fast individual queries)
CREATE TABLE calculator_pricing_lookup (
    id SERIAL PRIMARY KEY,
    parameter_name VARCHAR(100) NOT NULL,
    group_id INTEGER REFERENCES calculator_pricing_groups(id),
    base_value DECIMAL(10,4),
    value_unit VARCHAR(50),
    calculator_types TEXT[],
    -- ... (same as Option A but links to group)
);

-- VIEW: Combined access (AI uses this)
CREATE VIEW calculator_pricing_catalog AS
SELECT 
    g.group_name,
    g.category,
    g.pricing_data,
    g.calculator_types as group_calculator_types,
    ARRAY_AGG(l.parameter_name) as individual_parameters,
    g.description
FROM calculator_pricing_groups g
LEFT JOIN calculator_pricing_lookup l ON l.group_id = g.id
GROUP BY g.id;
```

### How AI Uses It:

```python
# Scenario: Create "Magnetic Business Cards" calculator

# 1. AI queries for similar calculators
result = query("""
    SELECT * FROM calculator_pricing_groups 
    WHERE 'business_cards' = ANY(calculator_types)
    ORDER BY usage_count DESC
""")

# Returns:
# - business_cards_setup_costs (impos, guilo, artwork)
# - card_stock_costs (satin, king kong, ecostar)
# - digital_print_costs (colour, b&w rates)
# - celloglaze_costs (lamination options)

# 2. AI presents to user:
"I found pricing for business cards. Use these as base?
 - Setup costs: $15 impos + $10 guilo + $15 per artwork
 - Stock: Satin 350GSM ($180/1000 sheets)
 - Print: $0.048/sheet colour, $0.02/sheet B&W
 
 What's different for MAGNETIC cards?"

# 3. User responds:
"Same setup and print, but magnetic backing costs $0.50 per card"

# 4. AI creates new group:
INSERT INTO calculator_pricing_groups VALUES
('magnetic_business_cards_materials', 'material', '{
   "magnetic_backing": {"value": 0.50, "unit": "per_card"},
   "inherits_from": "card_stock_costs"
}'::JSONB, ...)
```

---

## FINAL RECOMMENDATION

**Use HYBRID APPROACH:**

1. **`calculator_pricing_groups`** - 50-80 grouped rows (AI browses this)
2. **`calculator_pricing_lookup`** - 300-500 atomic rows (fast lookups)
3. **`calculator_pricing_catalog` VIEW** - Combined access

### Benefits:
- ✅ AI sees logical groups (context preserved)
- ✅ Fast queries on individual parameters (via lookup table)
- ✅ Easy to browse (50-80 groups, not 300-500 rows)
- ✅ Flexible JSONB for complex structures (tiers, maps)
- ✅ Best of both worlds!

### Storage Estimate:
- **Groups table:** 50-80 rows (~50 KB)
- **Lookup table:** 300-500 rows (~200 KB)
- **Total:** ~250 KB (negligible database size)

---

## NEXT STEPS

1. ✅ **Extract complete catalog** (DONE - 363 values from 30 calculators)
2. ⏳ **Create hybrid table structure** (SQL migration script)
3. ⏳ **Populate with extracted data** (seed script from JSON)
4. ⏳ **Build AI query tool** (`query_pricing_catalog()`)
5. ⏳ **Test with example** (create magnetic business cards)

**What do you think? Should I proceed with the HYBRID approach?**
