# Calculator Pricing Catalog UI Design

## Overview

A **spreadsheet-like web interface** for managing 363 pricing parameters across 30 calculators with AI-powered bulk operations.

---

## UI Architecture

### Technology Stack

**Frontend:**
- **Streamlit** (fastest to build, Python-native)
- **AG Grid** (spreadsheet UI component)
- **Pandas** (data handling)
- **ApexCharts** (visualizations)

**Backend:**
- Flask API (existing AI_agents infrastructure)
- PostgreSQL (calculator_pricing_catalog tables)
- Python calculators (execution layer)

**Why Streamlit?**
- Rapid development (1-2 days vs 1-2 weeks)
- Python-native (reuse existing calculator code)
- Built-in data editor components
- Easy AG Grid integration
- Already in your stack

---

## Main Interface: Parameter Matrix View

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🔧 Calculator Pricing Catalog                     [Export] │
├─────────────────────────────────────────────────────────────┤
│  Filters:  [Category ▼] [Subcategory ▼] [Calculator ▼]     │
│  Search:   [_________________________] 🔍                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Parameter Matrix (Editable Grid)                            │
│  ═══════════════════════════════════════════════════════     │
│                                                               │
│  Parameter Name │ Category │ Base │ BollardSigns │ Cards ... │
│  ───────────────┼──────────┼──────┼──────────────┼───────    │
│  impos_setup    │ Setup    │ 15.00│    40.00 ⚠️  │ 15.00 ✅ │
│  guilo_setup    │ Setup    │ 30.00│    30.00 ✅  │ 30.00 ✅ │
│  GST_RATE       │ Tax      │  1.10│     1.21 ⚠️  │  1.10 ✅ │
│  print_cost_sqm │ Print    │ 12.00│    12.00 ✅  │ 10.00 ⚠️ │
│  ...            │ ...      │ ...  │     ...      │  ...     │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  Bulk Actions:  [Update All] [Reset Overrides] [Add Param]  │
└─────────────────────────────────────────────────────────────┘
```

### Color Coding

- **✅ Green cell** = Uses base value (no override)
- **⚠️ Orange cell** = Custom override value
- **➖ Gray cell** = Parameter not used by calculator
- **🔴 Red cell** = Validation error (invalid value)

### Cell Interaction

**Single Cell Edit:**
1. Click cell → Inline edit mode
2. Type new value → Press Enter
3. Backend validates → Updates database
4. Cell color changes based on base/override

**Bulk Selection:**
1. Click + drag to select cells
2. Right-click → Context menu
   - Set to base value
   - Apply value to all
   - Create override
   - Reset to default

---

## Secondary Interface: Parameter Detail View

When clicking a parameter row, slide-out panel shows:

```
┌─────────────────────────────────────────┐
│  Parameter: impos_setup               ✕ │
├─────────────────────────────────────────┤
│                                         │
│  📊 USAGE STATISTICS                    │
│  ─────────────────────────────────      │
│  Used by: 12 calculators                │
│  Base value: $15.00                     │
│  Most common: $15.00 (8 calcs)          │
│  Range: $15.00 - $40.00                 │
│                                         │
│  📈 VALUE DISTRIBUTION                  │
│  ─────────────────────────────────      │
│  [Bar chart showing value frequency]    │
│                                         │
│  🧮 CALCULATORS USING THIS              │
│  ─────────────────────────────────      │
│  ✅ PremiumBusinessCards    $15.00      │
│  ⚠️  BollardSigns           $40.00      │
│  ✅ CustomVinylStickers     $15.00      │
│  ✅ NotepadsA4              $15.00      │
│  ... (8 more)                           │
│                                         │
│  📜 CHANGE HISTORY                      │
│  ─────────────────────────────────      │
│  Dec 15, 2025 - Base: 10→15 (Admin)    │
│  Dec 10, 2025 - Override: 40 (Bollard) │
│  Dec 1, 2025 - Created (System)        │
│                                         │
│  ⚙️ ACTIONS                             │
│  ─────────────────────────────────      │
│  [Update Base Value]                    │
│  [Force Update All Calculators]         │
│  [Reset All Overrides]                  │
│  [Delete Parameter]                     │
│                                         │
└─────────────────────────────────────────┘
```

---

## Bulk Operations Interface

### Update Wizard

**Scenario: Vinyl price increased 10%**

```
┌─────────────────────────────────────────────┐
│  Bulk Update Wizard                    [✕]  │
├─────────────────────────────────────────────┤
│                                             │
│  Step 1: Select Parameters                  │
│  ──────────────────────────────             │
│  ☑ vinyl_cost_sqm                           │
│  ☑ vinyl_cost_gloss                         │
│  ☑ vinyl_cost_matte                         │
│  ☐ print_cost_sqm                           │
│                                             │
│  Step 2: Define Change                      │
│  ──────────────────────────────             │
│  Operation: [Increase by ▼] [10] [% ▼]     │
│                                             │
│  Step 3: Select Calculators                 │
│  ──────────────────────────────             │
│  Update mode:                               │
│  ○ Base only (affects 8 calculators)       │
│  ● Selective (choose below)                 │
│  ○ Force all (overrides custom values)     │
│                                             │
│  ☑ CustomVinylStickers                      │
│  ☑ CorfluteSigns                            │
│  ☐ BollardSigns (has override)              │
│                                             │
│  Step 4: Preview Changes                    │
│  ──────────────────────────────             │
│  vinyl_cost_sqm: 25.00 → 27.50              │
│  - CustomVinylStickers: 25.00 → 27.50 ✅    │
│  - CorfluteSigns: 25.00 → 27.50 ✅          │
│  - BollardSigns: 28.00 (unchanged) ➖       │
│                                             │
│  [Cancel] [Apply Changes]                   │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Calculator View

### Individual Calculator Editor

```
┌─────────────────────────────────────────────┐
│  Calculator: Premium Business Cards         │
├─────────────────────────────────────────────┤
│                                             │
│  PARAMETERS USED (15 total)                 │
│  ══════════════════════════════             │
│                                             │
│  Parameter          │ Value  │ Status       │
│  ──────────────────┼────────┼─────────     │
│  impos_setup        │ 15.00  │ ✅ Base      │
│  guilo_setup        │ 10.00  │ ⚠️ Override  │
│  artwork_cost       │ 15.00  │ ✅ Base      │
│  GST_RATE           │  1.10  │ ✅ Base      │
│  print_cost_sheet   │  0.02  │ ✅ Base      │
│  profit_margin_max  │  0.80  │ ⚠️ Override  │
│  profit_margin_min  │  0.50  │ ⚠️ Override  │
│  ...                │  ...   │  ...         │
│                                             │
│  SPECIAL FEATURES                           │
│  ══════════════════════════════             │
│  ✅ DOUBLE_GST_APPLICATION                  │
│  ✅ DUAL_PROFIT_STRUCTURE                   │
│  ✅ TIERED_PRICING (13 tiers)               │
│                                             │
│  ACTIONS                                    │
│  ══════════════════════════════             │
│  [Reset All to Base]                        │
│  [Test Calculator]                          │
│  [View History]                             │
│  [Export Config]                            │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Comparison View

### Side-by-Side Calculator Comparison

```
┌─────────────────────────────────────────────────────────┐
│  Compare: [PremiumBusinessCards ▼] vs [BollardSigns ▼] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Parameter          │ Premium Cards │ Bollard Signs     │
│  ──────────────────┼───────────────┼─────────────      │
│  impos_setup        │ 15.00 ✅      │ 40.00 ⚠️          │
│  guilo_setup        │ 10.00 ⚠️      │ 30.00 ✅          │
│  GST_RATE           │  1.10 ✅      │  1.21 ⚠️ (DOUBLE) │
│  print_cost_sqm     │ 10.00 ⚠️      │ 12.00 ✅          │
│  profit_margin      │  0.80 ⚠️      │  0.50 ✅          │
│  ...                │  ...          │  ...              │
│                                                         │
│  DIFFERENCES: 8 parameters                              │
│  SIMILARITIES: 7 parameters                             │
│                                                         │
│  [Align Values] [Export Comparison]                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Analytics Dashboard

```
┌─────────────────────────────────────────────┐
│  📊 Pricing Analytics                       │
├─────────────────────────────────────────────┤
│                                             │
│  PARAMETER USAGE                            │
│  ══════════════════════════════             │
│  [Horizontal bar chart]                     │
│  impos_setup     ████████████ 12            │
│  GST_RATE        ███████████  11            │
│  print_cost_sqm  ██████████   10            │
│  ...                                        │
│                                             │
│  OVERRIDE FREQUENCY                         │
│  ══════════════════════════════             │
│  [Pie chart]                                │
│  ✅ Base values: 70%                        │
│  ⚠️ Overrides: 25%                          │
│  ➖ Unused: 5%                               │
│                                             │
│  VALUE CONSISTENCY                          │
│  ══════════════════════════════             │
│  [Scatter plot]                             │
│  Parameters with high variation:            │
│  - impos_setup (15-40)                      │
│  - profit_margin (41-80%)                   │
│  - GST_RATE (1.10-1.21)                     │
│                                             │
│  RECENT CHANGES                             │
│  ══════════════════════════════             │
│  Dec 15: GST_RATE updated (3 calcs)         │
│  Dec 10: vinyl_cost increased 10%           │
│  Dec 5: New parameter: eco_fee              │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Basic Grid (Week 1)

**Features:**
- Streamlit + AG Grid integration
- Read-only parameter matrix
- Filter by category/calculator
- Color-coded cells (base/override/unused)
- Basic search

**Tech Stack:**
```python
import streamlit as st
import pandas as pd
from streamlit_aggrid import AgGrid, GridOptionsBuilder

# Load data from PostgreSQL
df = load_parameter_matrix()

# Configure AG Grid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, groupable=True)
gb.configure_column("parameter_name", pinned='left', width=200)

# Render grid
AgGrid(df, gridOptions=gb.build())
```

### Phase 2: Editing (Week 2)

**Features:**
- Inline cell editing
- Validation on change
- Save to database
- Undo/redo
- Cell color updates

**API Endpoints:**
```python
POST /api/calculator/parameter/update
{
  "parameter_id": 123,
  "calculator_name": "BollardSigns",
  "new_value": 40.00,
  "is_override": true
}

GET /api/calculator/parameter/{id}/history
Returns: List of all changes with timestamps
```

### Phase 3: Bulk Operations (Week 3)

**Features:**
- Multi-cell selection
- Bulk update wizard
- Preview changes before apply
- Update propagation (3 modes)
- Batch validation

**Wizard Flow:**
1. User selects cells/parameters
2. Choose operation (increase/decrease/set)
3. Choose update mode (base/selective/force)
4. Preview affected calculators
5. Confirm and apply

### Phase 4: Analytics (Week 4)

**Features:**
- Parameter usage charts
- Override frequency analysis
- Value distribution graphs
- Change history timeline
- Inconsistency detection

**ApexCharts Integration:**
```python
import streamlit.components.v1 as components

# Usage bar chart
chart_config = {
    "chart": {"type": "bar"},
    "series": [{"data": usage_data}],
    "xaxis": {"categories": parameter_names}
}

components.html(f"""
<APEXCHARTS>
{json.dumps(chart_config)}
</APEXCHARTS>
""")
```

---

## AI Integration

### Natural Language Commands

**Chat Interface (Bottom of screen):**

```
┌─────────────────────────────────────────────┐
│  💬 AI Assistant                            │
├─────────────────────────────────────────────┤
│                                             │
│  You: Increase vinyl prices by 10%         │
│                                             │
│  AI: I found 3 vinyl-related parameters:    │
│      - vinyl_cost_sqm                       │
│      - vinyl_cost_gloss                     │
│      - vinyl_cost_matte                     │
│                                             │
│      This affects 8 calculators.            │
│      Update mode:                           │
│      [Base Only] [Selective] [Force All]    │
│                                             │
│  You: Base only                             │
│                                             │
│  AI: ✅ Updated 3 parameters                │
│      📊 8 calculators affected              │
│      [View Changes]                         │
│                                             │
└─────────────────────────────────────────────┘
```

**AI Commands:**
- "Show all parameters used by BollardSigns"
- "Which calculators use impos_setup?"
- "Find parameters with high variation"
- "Reset all overrides for NotepadsA4"
- "Compare PremiumBusinessCards and BollardSigns"
- "Increase all setup costs by $5"
- "Show calculators with double GST"

---

## Mobile/Responsive View

### Stacked Layout (Mobile)

```
┌─────────────────────┐
│  Calculator Catalog │
├─────────────────────┤
│  [Search ________]  │
│  [Filters ▼]        │
├─────────────────────┤
│  📋 impos_setup     │
│  Category: Setup    │
│  Base: $15.00       │
│  Used by: 12        │
│  [View Details >]   │
├─────────────────────┤
│  📋 GST_RATE        │
│  Category: Tax      │
│  Base: 1.10         │
│  Used by: 11        │
│  [View Details >]   │
├─────────────────────┤
│  ...                │
└─────────────────────┘
```

---

## Export/Import

### Export Options

**CSV Export:**
```csv
parameter_name,category,base_value,BollardSigns,PremiumBusinessCards,...
impos_setup,Setup,15.00,40.00,15.00,...
guilo_setup,Setup,30.00,30.00,10.00,...
```

**JSON Export:**
```json
{
  "impos_setup": {
    "base_value": 15.00,
    "calculators": {
      "BollardSigns": {"value": 40.00, "override": true},
      "PremiumBusinessCards": {"value": 15.00, "override": false}
    }
  }
}
```

**Excel Export:**
- Multiple sheets (parameters, calculators, history)
- Formatted with colors (green/orange/gray)
- Formulas preserved
- Pivot tables included

### Import Options

**Bulk Upload:**
1. Upload CSV/Excel file
2. Map columns to parameters
3. Preview changes
4. Validate data
5. Apply updates

---

## Security & Permissions

### Role-Based Access

**Admin:**
- Full edit access
- Bulk operations
- Delete parameters
- Force updates

**Manager:**
- Edit base values
- Create overrides
- View history
- Export data

**Viewer:**
- Read-only access
- Search/filter
- Export data
- View history

### Audit Trail

Every action logged:
```
Dec 17, 2025 10:45 AM - admin@example.com
Action: Updated base_value
Parameter: impos_setup
Old value: 10.00 → New value: 15.00
Affected: 8 calculators
```

---

## Performance Optimization

### Lazy Loading

- Load only visible rows (virtual scrolling)
- Paginate calculator columns
- Cache frequently accessed data
- Debounce search queries

### Database Optimization

```sql
-- Index for fast filtering
CREATE INDEX idx_parameters_category ON calculator_pricing_parameters(category);

-- Index for calculator lookup
CREATE INDEX idx_used_by ON calculator_pricing_parameters USING GIN (used_by_calculators);

-- Materialized view for analytics
CREATE MATERIALIZED VIEW parameter_usage_stats AS
SELECT 
  parameter_name,
  category,
  jsonb_array_length(used_by_calculators) as usage_count,
  (used_by_calculators::jsonb -> 0 ->> 'value')::numeric as most_common_value
FROM calculator_pricing_parameters;
```

---

## Technical Architecture

```
┌──────────────────┐
│   Streamlit UI   │ ← User interacts here
└────────┬─────────┘
         │
         │ HTTP/WebSocket
         ↓
┌──────────────────┐
│   Flask API      │ ← Existing AI_agents backend
│  (/api/catalog)  │
└────────┬─────────┘
         │
         │ SQL Queries
         ↓
┌──────────────────┐
│   PostgreSQL     │ ← 4 tables (parameters, overrides, history, registry)
│  (Fred Database) │
└────────┬─────────┘
         │
         │ Calculator execution
         ↓
┌──────────────────┐
│  Python Calcs    │ ← 30 calculator files
│  (shopify_calcs) │
└──────────────────┘
```

---

## File Structure

```
UI/modules_external/quote-calculator/
├── catalog_ui/                          # NEW Streamlit app
│   ├── app.py                           # Main Streamlit entry point
│   ├── pages/
│   │   ├── 1_Parameter_Matrix.py        # Main grid view
│   │   ├── 2_Calculator_View.py         # Individual calculator editor
│   │   ├── 3_Comparison.py              # Side-by-side comparison
│   │   ├── 4_Analytics.py               # Charts and insights
│   │   └── 5_Bulk_Operations.py         # Bulk update wizard
│   ├── components/
│   │   ├── ag_grid.py                   # AG Grid wrapper
│   │   ├── charts.py                    # ApexCharts helpers
│   │   ├── filters.py                   # Filter components
│   │   └── bulk_wizard.py               # Bulk update wizard
│   ├── api/
│   │   ├── catalog_client.py            # API client for Flask
│   │   └── validators.py                # Data validation
│   └── utils/
│       ├── color_coding.py              # Cell color logic
│       └── export.py                    # CSV/Excel export
│
├── backend/
│   ├── api/
│   │   └── catalog_routes.py            # NEW Flask routes
│   ├── models/
│   │   └── catalog_models.py            # SQLAlchemy models
│   └── services/
│       └── catalog_service.py           # Business logic
│
└── database/
    ├── migrations/
    │   └── 001_create_catalog_tables.sql # DDL from design
    └── seeds/
        └── load_extracted_data.py        # Populate from JSON
```

---

## Quick Start Guide

### For Developers

```bash
# 1. Install dependencies
pip install streamlit streamlit-aggrid pandas psycopg2-binary

# 2. Run migrations
psql -U postgres -d fred -f database/migrations/001_create_catalog_tables.sql

# 3. Load extracted data
python database/seeds/load_extracted_data.py

# 4. Start Streamlit UI
cd catalog_ui
streamlit run app.py

# Opens: http://localhost:8501
```

### For Users

1. Navigate to **Calculator Pricing Catalog** in main menu
2. Use filters to find parameters
3. Click cells to edit values
4. Use bulk operations for mass updates
5. Export data for offline analysis

---

## Future Enhancements

### Phase 5+ (After MVP)

**AI-Powered Features:**
- Anomaly detection (flag unusual values)
- Smart suggestions (optimal pricing recommendations)
- Predictive analysis (forecast price changes)
- Natural language queries ("Show me all overpriced setups")

**Advanced Visualizations:**
- 3D parameter space (cluster similar calculators)
- Network graph (parameter dependencies)
- Time-series analysis (pricing trends)
- Heat maps (usage intensity)

**Integration:**
- Real-time calculator testing
- Automatic parameter extraction from code
- Version control (Git-like diffs)
- A/B testing (compare pricing strategies)

**Collaboration:**
- Multi-user editing (Google Docs-style)
- Comments on parameters
- Approval workflows
- Change notifications

---

## Summary

**What You Get:**
- ✅ Spreadsheet-like UI (familiar Excel-style interface)
- ✅ Visual parameter management (color-coded cells)
- ✅ Bulk operations (update multiple calculators at once)
- ✅ Calculator tracking (see which calcs use which params)
- ✅ Change history (full audit trail)
- ✅ AI integration (natural language commands)
- ✅ Analytics dashboard (usage insights)
- ✅ Export/import (CSV, Excel, JSON)
- ✅ Mobile responsive (works on all devices)

**Timeline:**
- Week 1: Basic grid (read-only matrix)
- Week 2: Editing (inline cell updates)
- Week 3: Bulk operations (update wizard)
- Week 4: Analytics (charts and insights)

**Total:** 4 weeks to full featured UI

**Next Steps:**
1. Approve UI design (this document)
2. Create SQL migration script
3. Build Streamlit app skeleton
4. Implement AG Grid integration
5. Add API routes to Flask
6. Test with real data

Ready to start building?
