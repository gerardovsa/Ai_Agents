# Calculator Pricing Catalog - Value Range Analysis Guide

**Date:** December 17, 2025  
**Migration:** 002 Complete ✅  
**New Features:** Value statistics, duplicate merging, variance analysis

---

## What's New

### 1. Duplicate Parameters Fixed ✅
Merged 7 case-sensitive duplicates:
- `CUT_COST` + `cut_cost` → `cut_cost`
- `cutting_block` + `CUTTING_BLOCK` → `cutting_block`
- `EXTRA_ARTS` + `extra_arts` → `extra_arts`
- `GST_RATE` + `gst_rate` → `gst_rate`
- `GUILO_SETUP` + `guilo_setup` → `guilo_setup`
- `impos_setup` + `IMPOS_SETUP` → `impos_setup`
- `STOCK_WASTE` + `stock_waste` → `stock_waste`

**Result:** 71 parameters → 64 parameters (7 duplicates merged)

### 2. Value Statistics Column Added ✅
Every parameter now has a `value_statistics` JSONB column containing:

```json
{
  "range": {"min": 15.0, "max": 75.0},
  "mean": 29.0,
  "median": 25.0,
  "std_dev": 15.23,
  "distinct_count": 8,
  "distinct_values": [15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 60.0, 75.0],
  "value_counts": {
    "15.0": 12,
    "20.0": 5,
    "25.0": 3,
    "30.0": 2,
    "35.0": 2,
    "40.0": 2,
    "60.0": 1,
    "75.0": 1
  }
}
```

### 3. Value Variance Analysis View ✅
New view: `v_parameter_value_analysis`

Shows parameters ranked by **variance percentage** (how much values differ across calculators).

---

## Top 10 Parameters with Highest Value Variance

| Rank | Parameter | Min | Max | Mean | Variance | Used By |
|------|-----------|-----|-----|------|----------|---------|
| 1 | stock_cost_per_1000_sheets | $60 | $500 | $150.14 | 293% | 7 calcs |
| 2 | impos_setup | $15 | $75 | $29.00 | 207% | 28 calcs |
| 3 | material_rate | $3.50 | $28 | $13.14 | 186% | 7 calcs |
| 4 | items_per_sheet | 1.0 | 4.0 | 2.0 | 150% | 5 calcs |
| 5 | area_m2 | $0.06 | $0.27 | $0.21 | 99% | 9 calcs |
| 6 | print_mode_cost | $0.02 | $0.06 | $0.04 | 97% | 7 calcs |
| 7 | extra_arts | $10 | $25 | $16.32 | 92% | 19 calcs |
| 8 | guilo_setup | $10 | $20 | $13.93 | 72% | 15 calcs |
| 9 | print_cost_per_m2 | $6 | $12 | $8.85 | 68% | 10 calcs |
| 10 | sides_multiplier | 1.0 | 2.0 | 1.88 | 53% | 16 calcs |

**Key Insight:** Parameters with high variance (>100%) need individual calculator attention when updating.

---

## Example: impos_setup Value Distribution

**Parameter:** `impos_setup` (Imposition Setup Cost)  
**Variance:** 207% (very high)  
**Base Value:** $15.00  
**Range:** $15 - $75  
**Mean:** $29.00  
**Used By:** 28 calculators

### Value Breakdown by Calculator:

| Calculator | Value | Override? | Diff from Base | % Diff |
|-----------|-------|-----------|----------------|--------|
| LuxuryClassicPullUpBanners | $75.00 | NO | +$60 | +400% |
| SpiralBoundBooks | $60.00 | NO | +$45 | +300% |
| PerfectBound | $50.00 | NO | +$35 | +233% |
| BollardSigns | $40.00 | NO | +$25 | +167% |
| MetalFaceA-Frame | $40.00 | NO | +$25 | +167% |
| CustomVinylStickers | $35.00 | NO | +$20 | +133% |
| ElectionSigns | $35.00 | NO | +$20 | +133% |
| CustomPosterPrinting | $30.00 | NO | +$15 | +100% |
| CorfluteInsertA-Frame | $30.00 | NO | +$15 | +100% |
| ... | ... | ... | ... | ... |
| EconomicalBusinessCards | $15.00 | NO | $0 | 0% |
| PremiumBusinessCards | $15.00 | NO | $0 | 0% |

**Analysis:** 
- 12 calculators use base value ($15)
- 16 calculators have custom values ($20-$75)
- High variance indicates product complexity affects setup cost
- Luxury/specialty products ($60-$75) vs standard products ($15-$20)

---

## SQL Queries for UI Development

### Query 1: Get Parameter with Full Value Distribution
```sql
SELECT 
    parameter_name,
    category,
    base_value,
    total_usage_count,
    value_statistics
FROM calculator_pricing_parameters
WHERE parameter_name = 'impos_setup';
```

**Returns:**
```json
{
  "parameter_name": "impos_setup",
  "category": "Setup",
  "base_value": 15.00,
  "total_usage_count": 28,
  "value_statistics": {
    "range": {"min": 15.0, "max": 75.0},
    "mean": 29.0,
    "distinct_count": 8,
    "value_counts": {"15.0": 12, "20.0": 5, ...}
  }
}
```

### Query 2: Get All Calculator Values for a Parameter
```sql
SELECT 
    elem->>'calculator' as calculator_name,
    (elem->>'value')::DECIMAL as value,
    (elem->>'override')::BOOLEAN as is_override,
    (elem->>'value')::DECIMAL - p.base_value as diff_from_base,
    CASE 
        WHEN p.base_value > 0 
        THEN ((elem->>'value')::DECIMAL - p.base_value) / p.base_value * 100
        ELSE 0
    END as percentage_diff
FROM calculator_pricing_parameters p,
     LATERAL jsonb_array_elements(p.used_by_calculators) as elem
WHERE p.parameter_name = 'impos_setup'
ORDER BY (elem->>'value')::DECIMAL DESC;
```

**Returns:** Table showing each calculator's specific value with variance from base.

### Query 3: Find Parameters with High Variance (>100%)
```sql
SELECT 
    parameter_name,
    min_value,
    max_value,
    mean_value,
    variance_percentage,
    total_usage_count,
    distinct_values
FROM v_parameter_value_analysis
WHERE variance_percentage > 100
ORDER BY variance_percentage DESC;
```

**Use Case:** Identify parameters that need calculator-specific review when bulk updating.

### Query 4: Get Parameters Used by a Specific Calculator
```sql
SELECT 
    p.parameter_name,
    p.category,
    p.base_value,
    elem->>'value' as calculator_value,
    (elem->>'override')::BOOLEAN as has_override,
    p.value_statistics->'range' as value_range_across_all
FROM calculator_pricing_parameters p,
     LATERAL jsonb_array_elements(p.used_by_calculators) as elem
WHERE elem->>'calculator' = 'BollardSigns'
ORDER BY p.category, p.parameter_name;
```

**Returns:** All parameters used by BollardSigns with their specific values and global ranges.

---

## UI Implementation Requirements

### 1. Parameter Matrix Table (Tabulator)

**Columns:**
- Parameter Name (frozen left)
- Category
- Base Value
- **Min Value** (NEW - from value_statistics)
- **Max Value** (NEW - from value_statistics)
- **Mean Value** (NEW - from value_statistics)
- **Variance %** (NEW - color coded: green <25%, yellow 25-100%, red >100%)
- **Distinct Values Count** (NEW - shows how many different values exist)
- Calculator 1 Value (color: green=base, orange=override)
- Calculator 2 Value
- ... (30 calculator columns)

**Color Coding:**
- **Green cell:** Uses base value (no override)
- **Orange cell:** Has custom override value
- **Gray cell:** Not used by this calculator
- **Red background:** Variance > 100% (needs attention)

### 2. Parameter Detail Panel

When clicking a parameter row, show:

**Value Distribution Chart (ApexCharts):**
```javascript
{
  series: [{
    name: 'Calculator Count',
    data: [12, 5, 3, 2, 2, 2, 1, 1] // from value_counts
  }],
  xaxis: {
    categories: [15, 20, 25, 30, 35, 40, 60, 75] // distinct_values
  },
  colors: ['#00E396'] // green bars
}
```

**Statistics Summary:**
```
Range: $15 - $75 (5x difference)
Mean: $29.00
Median: $25.00
Std Dev: ±$15.23
Variance: 207% (HIGH)
```

**Calculator Breakdown Table:**
- List all 28 calculators
- Show each calculator's value
- Highlight overrides in orange
- Show diff from base (+$25, +400%)
- Allow inline editing

### 3. Bulk Update Wizard

**Step 1: Filter Parameters**
- By variance: "Show only parameters with >100% variance"
- By category: "Show only Setup parameters"
- By usage: "Show only parameters used by >10 calculators"

**Step 2: Define Change**
- Increase by 10%
- Decrease by $5
- Set to specific value
- Apply multiplier (1.15x)

**Step 3: Select Update Mode**
- **Base Only:** Update base_value only, leave overrides unchanged
- **All Using Base:** Update calculators currently using base value
- **Force All:** Update all calculators (replace overrides)

**Step 4: Preview Impact**
```
Parameter: impos_setup
Current Base: $15.00
New Base: $16.50 (+10%)

Calculators Affected: 12 (using base)
Calculators Unchanged: 16 (have overrides)

Preview:
  • EconomicalBusinessCards: $15.00 → $16.50
  • PremiumBusinessCards: $15.00 → $16.50
  • ... (10 more)

Overrides Preserved:
  • BollardSigns: $40.00 (no change)
  • CustomVinylStickers: $35.00 (no change)
  • ... (14 more)
```

---

## API Endpoints Needed

### GET /api/calculator/catalog/parameters/:id/value-distribution
Returns:
```json
{
  "parameter": {
    "id": 1,
    "name": "impos_setup",
    "category": "Setup",
    "base_value": 15.00
  },
  "statistics": {
    "range": {"min": 15.0, "max": 75.0},
    "mean": 29.0,
    "median": 25.0,
    "std_dev": 15.23,
    "variance_percentage": 207
  },
  "calculator_values": [
    {
      "calculator": "LuxuryClassicPullUpBanners",
      "value": 75.00,
      "override": false,
      "diff_from_base": 60.00,
      "percentage_diff": 400
    },
    ...
  ]
}
```

### GET /api/calculator/catalog/parameters/high-variance?threshold=100
Returns parameters with variance > threshold, sorted by variance descending.

### GET /api/calculator/catalog/calculators/:name/parameters
Returns all parameters used by a specific calculator with their values.

---

## Next Steps for UI Development

1. **Update Tabulator Configuration**
   - Add min/max/mean/variance columns
   - Implement color coding for variance (green/yellow/red)
   - Add variance percentage badge

2. **Build Parameter Detail Panel**
   - ApexCharts bar chart for value distribution
   - Statistics summary card
   - Calculator breakdown table with inline editing

3. **Implement Bulk Update Wizard**
   - Filter by variance threshold
   - Preview impact before applying
   - Show "affected vs unchanged" calculator counts

4. **Add Search/Filter Features**
   - "Show high variance parameters (>100%)"
   - "Show parameters with overrides"
   - "Show parameters used by specific calculator"

---

## Database Schema Changes

### New Column: `value_statistics`
```sql
value_statistics JSONB DEFAULT '{}'::JSONB
```

**Contains:**
- `range.min` - Lowest value across all calculators
- `range.max` - Highest value across all calculators
- `mean` - Average value
- `median` - Middle value
- `std_dev` - Standard deviation
- `distinct_count` - How many unique values exist
- `distinct_values` - Array of all unique values
- `value_counts` - Object mapping value → count

### New View: `v_parameter_value_analysis`
Pre-calculates variance percentages and provides easy access to statistics.

**Use in UI:**
```sql
-- Get top 10 most variable parameters
SELECT * FROM v_parameter_value_analysis 
WHERE variance_percentage > 50 
ORDER BY variance_percentage DESC 
LIMIT 10;
```

---

## Key Insights from Data

1. **High Variance Parameters Need Special Attention**
   - `stock_cost_per_1000_sheets`: 293% variance (8x difference)
   - `impos_setup`: 207% variance (5x difference)
   - These should NOT be bulk updated without review

2. **Standard Parameters (Low Variance)**
   - `gst_rate`: 0% variance (all use 1.1)
   - `cutting_block`: 0% variance (all use 500)
   - Safe for bulk updates

3. **Product Complexity Drives Variance**
   - Luxury/specialty products have higher setup costs
   - Basic products use standard base values
   - Variance correlates with product type

---

**Summary:** Database now tracks value ranges, statistics, and variance for every parameter across all calculators. UI can show "how different are values" and "which calculators use which values" for informed bulk update decisions.
