# Custom Calculator Module - Master Documentation
**Last Updated: December 14, 2025**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [Builder Tools](#builder-tools)
5. [Query Library](#query-library)
6. [Execution Engine](#execution-engine)
7. [Use Cases](#use-cases)
8. [API Reference](#api-reference)
9. [Examples](#examples)

---

## 🎯 Overview

The **Custom Calculator Module** enables dynamic creation of formula-based calculators without code deployment. It's designed for:

- **What-If Scenarios** - Test pricing changes before implementation
- **Rush Job Pricing** - Special calculators for expedited orders
- **Custom Products** - One-off calculations for specialty substrates
- **A/B Testing** - Compare pricing strategies side-by-side
- **Customer-Specific Pricing** - Negotiated rate structures

### Key Features

✅ **No-Code Builder** - AI-assisted calculator creation  
✅ **Parameter References** - Dynamic pricing from parameter library  
✅ **Formula Engine** - Safe Python expression evaluation via asteval  
✅ **Version Control** - Track calculator changes over time  
✅ **AI Searchable** - Vector embeddings for semantic discovery  
✅ **Execution Trace** - Full audit trail of calculations  

---

## 🏗️ Architecture

### System Components

```
Custom Calculator System
│
├── Database Tables (4)
│   ├── custom_calculators              # Calculator definitions
│   ├── custom_calculator_parameters    # Parameter references
│   ├── custom_calculator_components    # Reusable calculation blocks
│   └── what_if_scenarios               # Scenario testing
│
├── Builder Tools (6)
│   ├── calculator_builder_start        # Initialize new calculator
│   ├── calculator_builder_add_parameter    # Add input parameters
│   ├── calculator_builder_set_formula      # Define calculation steps
│   ├── calculator_builder_add_component    # Add reusable components
│   ├── calculator_builder_test             # Test with sample inputs
│   └── calculator_builder_save             # Activate calculator
│
├── Query Tools (7)
│   ├── custom_calculator_get_schema_guide  # Get builder guide
│   ├── custom_calculator_list              # List all calculators
│   ├── custom_calculator_get_detail        # Get calculator detail
│   ├── custom_calculator_search            # Semantic search
│   ├── custom_calculator_get_parameters    # Get parameter references
│   ├── custom_calculator_get_usage_stats   # Usage statistics
│   └── custom_calculator_get_components    # List components
│
├── Execution Engine
│   ├── UniversalCalculatorExecutor         # Formula evaluation
│   ├── ParameterResolver                   # Resolve parameter references
│   └── ComponentRegistry                   # Load reusable components
│
└── Integration Layer
    ├── calculator_builder_wrapper.py       # Tool implementations
    └── query_library.py                    # SQL query library
```

### Data Flow

```
1. AI Agent invokes builder tool
   ↓
2. calculator_builder_wrapper.py validates input
   ↓
3. Draft JSON stored in custom_calculators table
   ↓
4. Parameter references linked in custom_calculator_parameters
   ↓
5. Test execution via UniversalCalculatorExecutor
   ↓
6. Formula evaluation with asteval (safe Python expressions)
   ↓
7. Result returned with execution trace
```

---

## 💾 Database Schema

### Table 1: `custom_calculators`

**Purpose:** Store calculator definitions with formulas and parameter references

| Column | Type | Description |
|--------|------|-------------|
| `calculator_id` | UUID | Primary key |
| `name` | VARCHAR(255) | Calculator name (e.g., "Rush24HourVinyl") |
| `short_description` | VARCHAR(500) | Brief description for AI search |
| `description` | TEXT | Detailed description |
| `category` | VARCHAR(100) | Category: custom_quote, specialty_substrate, rush_job, bulk_order, prototype |
| `json_definition` | JSONB | **Calculator schema with formulas** |
| `usage_instructions` | TEXT | AI tool usage instructions |
| `tags` | TEXT[] | Search tags |
| `embedding_text` | TEXT | Text for vector embedding |
| `search_keywords` | TEXT[] | Keywords for full-text search |
| `embedding` | VECTOR(1536) | OpenAI embedding for semantic search |
| `version` | VARCHAR(20) | Calculator version (e.g., "1.0", "2.1") |
| `parent_version_id` | UUID | Link to previous version |
| `parent_calculator_id` | UUID | Link to base calculator if cloned |
| `created_by` | VARCHAR(100) | Creator username |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |
| `last_used_at` | TIMESTAMP | Last execution timestamp |
| `usage_count` | INTEGER | Total executions |
| `is_active` | BOOLEAN | Active status |
| `is_template` | BOOLEAN | Template flag |
| `avg_calculation_time_ms` | INTEGER | Performance metric |

**JSON Definition Structure:**

```json
{
  "parameters": [
    {
      "name": "quantity",
      "type": "integer",
      "required": true,
      "min": 1,
      "max": 10000,
      "description": "Number of units"
    },
    {
      "name": "substrate_type",
      "type": "select",
      "options": ["vinyl", "corflute", "acrylic"],
      "default": "vinyl"
    }
  ],
  "pricing_constants": {
    "markup_percentage": 1.35,
    "setup_fee": 25.0
  },
  "calculation_steps": [
    {
      "step": 1,
      "variable": "material_cost",
      "formula": "pricing.vinyl_cost_per_sqm * width_mm / 1000 * height_mm / 1000 * quantity",
      "description": "Calculate total material cost"
    },
    {
      "step": 2,
      "variable": "total_price",
      "formula": "(material_cost + pricing.setup_fee) * pricing.markup_percentage",
      "description": "Apply markup and setup fee"
    }
  ],
  "result_structure": {
    "total_price": "total_price",
    "unit_price": "total_price / quantity",
    "quantity": "quantity",
    "breakdown": {
      "material_cost": "material_cost",
      "setup_fee": "pricing.setup_fee",
      "markup": "(total_price - material_cost - pricing.setup_fee)"
    }
  }
}
```

**Indexes:**

- `idx_custom_calculators_name` - Name lookup
- `idx_custom_calculators_category` - Category filtering
- `idx_custom_calculators_created_at` - Recent calculators (DESC)
- `idx_custom_calculators_active` - Active calculators only
- `idx_custom_calculators_tags` - GIN index for tag search
- `idx_custom_calculators_search_keywords` - GIN index for full-text
- `idx_custom_calculators_embedding` - IVFFlat index for semantic search

---

### Table 2: `custom_calculator_parameters`

**Purpose:** Track parameter references for global update impact analysis

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `calculator_id` | UUID | References `custom_calculators` (CASCADE DELETE) |
| `parameter_name` | VARCHAR(100) | Parameter name (e.g., "vinyl_cost") |
| `source_table` | VARCHAR(100) | Source table (e.g., "calculator_pricing_parameters") |
| `source_parameter_id` | VARCHAR(100) | Source ID (e.g., "vinyl_white_outdoor_cost") |
| `display_name` | VARCHAR(255) | Display name for UI |
| `parameter_type` | VARCHAR(50) | Type: pricing, material, labor, margin, multiplier |
| `formula_variable_name` | VARCHAR(100) | Variable in formula (e.g., "pricing.vinyl_cost") |
| `used_in_steps` | INTEGER[] | Which calculation steps use this parameter |
| `is_critical` | BOOLEAN | Critical parameter flag |
| `created_at` | TIMESTAMP | Creation timestamp |

**Example Usage:**

When `calculator_pricing_parameters` table is updated:
```sql
-- Find all calculators affected by parameter change
SELECT DISTINCT c.calculator_id, c.name, cp.parameter_name
FROM custom_calculators c
JOIN custom_calculator_parameters cp ON c.calculator_id = cp.calculator_id
WHERE cp.source_parameter_id = 'vinyl_white_outdoor_cost';
```

**Indexes:**

- `idx_custom_calc_params_calculator` - Calculator lookup
- `idx_custom_calc_params_source` - Source parameter lookup
- `idx_custom_calc_params_type` - Parameter type filtering

---

### Table 3: `custom_calculator_components`

**Purpose:** Reusable calculation blocks (like functions)

| Column | Type | Description |
|--------|------|-------------|
| `component_id` | UUID | Primary key |
| `calculator_id` | UUID | References `custom_calculators` (CASCADE DELETE) |
| `component_name` | VARCHAR(100) | Component name (e.g., "calculate_area") |
| `component_type` | VARCHAR(50) | Type: calculation, lookup, validation, formatting |
| `formula` | TEXT | Formula expression |
| `input_parameters` | JSONB | Required inputs |
| `output_variable` | VARCHAR(100) | Variable name for output |
| `description` | TEXT | Component description |
| `execution_order` | INTEGER | Order in calculation sequence |
| `is_conditional` | BOOLEAN | Conditional execution flag |
| `condition_expression` | TEXT | Condition for execution |
| `error_handling` | JSONB | Error handling rules |
| `created_at` | TIMESTAMP | Creation timestamp |

**Example Component:**

```json
{
  "component_name": "calculate_area_sqm",
  "component_type": "calculation",
  "formula": "width_mm / 1000 * height_mm / 1000",
  "input_parameters": {
    "width_mm": "number",
    "height_mm": "number"
  },
  "output_variable": "area_sqm",
  "description": "Convert mm dimensions to square meters",
  "execution_order": 1,
  "is_conditional": false,
  "error_handling": {
    "on_divide_by_zero": "return 0",
    "on_negative_value": "raise error"
  }
}
```

**Indexes:**

- `idx_custom_calc_components_calculator` - Calculator lookup
- `idx_custom_calc_components_name` - Component name lookup
- `idx_custom_calc_components_order` - Execution order

---

### Table 4: `what_if_scenarios`

**Purpose:** Test pricing changes before implementation

| Column | Type | Description |
|--------|------|-------------|
| `scenario_id` | UUID | Primary key |
| `calculator_id` | UUID | References `custom_calculators` |
| `scenario_name` | VARCHAR(255) | Scenario name (e.g., "10% Vinyl Increase") |
| `description` | TEXT | Scenario description |
| `parameter_overrides` | JSONB | Parameter value overrides |
| `input_samples` | JSONB | Test input samples |
| `results` | JSONB | Calculated results |
| `comparison_baseline` | UUID | Baseline calculator for comparison |
| `created_by` | VARCHAR(100) | Creator username |
| `created_at` | TIMESTAMP | Creation timestamp |
| `executed_at` | TIMESTAMP | Last execution timestamp |
| `status` | VARCHAR(50) | Status: draft, executed, approved, rejected |

**Example Scenario:**

```json
{
  "scenario_name": "10% Material Cost Increase",
  "parameter_overrides": {
    "pricing.vinyl_cost_per_sqm": 12.50,  // Was 11.36
    "pricing.corflute_cost_per_sheet": 16.50  // Was 15.00
  },
  "input_samples": [
    {"quantity": 100, "width_mm": 600, "height_mm": 900},
    {"quantity": 500, "width_mm": 600, "height_mm": 900},
    {"quantity": 1000, "width_mm": 600, "height_mm": 900}
  ],
  "results": {
    "baseline": [120.50, 450.20, 850.00],
    "scenario": [132.55, 495.22, 935.00],
    "delta_percentage": [10.0, 10.0, 10.0]
  }
}
```

**Indexes:**

- `idx_what_if_scenarios_calculator` - Calculator lookup
- `idx_what_if_scenarios_created_at` - Recent scenarios
- `idx_what_if_scenarios_status` - Status filtering

---

## 🛠️ Builder Tools

### Tool 1: `calculator_builder_start`

**Purpose:** Initialize new custom calculator

**Parameters:**
```python
{
  "name": str,                    # Required: Calculator name
  "description": str,             # Required: Detailed description
  "short_description": str,       # Optional: Brief description (auto-generated if omitted)
  "based_on_calculator": str,     # Optional: Parent calculator to clone
  "category": str,                # Optional: Category (default: "custom_quote")
  "tags": List[str]               # Optional: Search tags
}
```

**Returns:**
```json
{
  "success": true,
  "calculator_id": "uuid",
  "name": "Rush24HourVinyl",
  "status": "draft",
  "draft_json": {
    "parameters": [],
    "pricing_constants": {},
    "calculation_steps": [],
    "result_structure": {}
  },
  "suggested_parameters": [
    {
      "parameter_name": "vinyl_cost",
      "category": "Material",
      "current_value": 11.36,
      "unit": "$ per sqm"
    }
  ],
  "next_steps": "Add parameters using calculator_builder_add_parameter"
}
```

**Example Usage:**
```python
calculator_builder_start(
    name="Rush24HourVinyl",
    description="Vinyl stickers with 24-hour turnaround pricing",
    short_description="Rush vinyl - 24hr",
    category="rush_job",
    tags=["vinyl", "rush", "stickers"]
)
```

---

### Tool 2: `calculator_builder_add_parameter`

**Purpose:** Add input parameter to calculator

**Parameters:**
```python
{
  "calculator_id": str,           # Required: Calculator UUID
  "parameter_name": str,          # Required: Parameter name
  "parameter_type": str,          # Optional: integer, number, select, boolean (default: "number")
  "required": bool,               # Optional: Required flag (default: True)
  "source": str,                  # Optional: Source from parameter library
  "options": List[Any],           # Optional: For 'select' type
  "default": Any,                 # Optional: Default value
  "description": str              # Optional: Parameter description
}
```

**Returns:**
```json
{
  "success": true,
  "parameter_added": {
    "name": "quantity",
    "type": "integer",
    "required": true,
    "min": 1,
    "max": 10000
  },
  "total_parameters": 3
}
```

**Example Usage:**
```python
# Add numeric parameter
calculator_builder_add_parameter(
    calculator_id="abc123...",
    parameter_name="quantity",
    parameter_type="integer",
    required=True,
    description="Number of vinyl stickers"
)

# Add select parameter with options
calculator_builder_add_parameter(
    calculator_id="abc123...",
    parameter_name="substrate_type",
    parameter_type="select",
    options=["vinyl", "corflute", "acrylic"],
    default="vinyl",
    description="Substrate material type"
)

# Add parameter from pricing library
calculator_builder_add_parameter(
    calculator_id="abc123...",
    parameter_name="vinyl_cost",
    source="calculator_pricing_parameters:vinyl_white_outdoor_cost",
    description="Cost per square meter for white vinyl"
)
```

---

### Tool 3: `calculator_builder_set_formula`

**Purpose:** Define calculation step with formula

**Parameters:**
```python
{
  "calculator_id": str,           # Required: Calculator UUID
  "step_number": int,             # Required: Step order (1, 2, 3...)
  "variable_name": str,           # Required: Output variable name
  "formula": str,                 # Required: Python expression
  "description": str              # Optional: Step description
}
```

**Returns:**
```json
{
  "success": true,
  "step_added": {
    "step": 1,
    "variable": "area_sqm",
    "formula": "width_mm / 1000 * height_mm / 1000"
  },
  "total_steps": 3
}
```

**Example Usage:**
```python
# Step 1: Calculate area
calculator_builder_set_formula(
    calculator_id="abc123...",
    step_number=1,
    variable_name="area_sqm",
    formula="width_mm / 1000 * height_mm / 1000",
    description="Convert mm dimensions to square meters"
)

# Step 2: Calculate material cost
calculator_builder_set_formula(
    calculator_id="abc123...",
    step_number=2,
    variable_name="material_cost",
    formula="area_sqm * quantity * pricing.vinyl_cost",
    description="Total material cost = area × quantity × cost per sqm"
)

# Step 3: Apply rush fee and markup
calculator_builder_set_formula(
    calculator_id="abc123...",
    step_number=3,
    variable_name="total_price",
    formula="(material_cost + pricing.rush_fee_24hr) * pricing.markup_rush",
    description="Add rush fee and apply rush markup"
)
```

**Formula Syntax Rules:**

- Use Python expressions (asteval safe subset)
- Reference parameters: `quantity`, `width_mm`, `substrate_type`
- Reference pricing constants: `pricing.vinyl_cost`, `pricing.markup_percentage`
- Use math operators: `+`, `-`, `*`, `/`, `**` (power)
- Supported functions: `min()`, `max()`, `abs()`, `round()`
- Conditional: `value if condition else other_value`

---

### Tool 4: `calculator_builder_add_component`

**Purpose:** Add reusable calculation component

**Parameters:**
```python
{
  "calculator_id": str,           # Required: Calculator UUID
  "component_name": str,          # Required: Component name
  "component_type": str,          # Required: calculation, lookup, validation, formatting
  "formula": str,                 # Required: Formula expression
  "input_parameters": Dict,       # Required: Input parameter types
  "output_variable": str,         # Required: Output variable name
  "description": str,             # Optional: Component description
  "execution_order": int,         # Optional: Execution order
  "is_conditional": bool,         # Optional: Conditional execution
  "condition_expression": str     # Optional: Condition for execution
}
```

**Returns:**
```json
{
  "success": true,
  "component_added": {
    "component_name": "calculate_area_sqm",
    "output_variable": "area_sqm"
  },
  "total_components": 2
}
```

**Example Usage:**
```python
calculator_builder_add_component(
    calculator_id="abc123...",
    component_name="calculate_area_sqm",
    component_type="calculation",
    formula="width_mm / 1000 * height_mm / 1000",
    input_parameters={"width_mm": "number", "height_mm": "number"},
    output_variable="area_sqm",
    description="Convert mm dimensions to square meters"
)
```

---

### Tool 5: `calculator_builder_test`

**Purpose:** Test calculator with sample inputs

**Parameters:**
```python
{
  "calculator_id": str,           # Required: Calculator UUID
  "test_inputs": Dict,            # Required: Sample input values
  "parameter_overrides": Dict     # Optional: Override pricing parameters
}
```

**Returns:**
```json
{
  "success": true,
  "result": {
    "total_price": 156.75,
    "unit_price": 1.5675,
    "quantity": 100,
    "breakdown": {
      "material_cost": 68.16,
      "rush_fee": 50.00,
      "markup": 38.59
    }
  },
  "execution_trace": [
    {
      "step": 1,
      "variable": "area_sqm",
      "formula": "600 / 1000 * 900 / 1000",
      "result": 0.54
    },
    {
      "step": 2,
      "variable": "material_cost",
      "formula": "0.54 * 100 * 11.36",
      "result": 61.34
    }
  ],
  "execution_time_ms": 12
}
```

**Example Usage:**
```python
calculator_builder_test(
    calculator_id="abc123...",
    test_inputs={
        "quantity": 100,
        "width_mm": 600,
        "height_mm": 900,
        "substrate_type": "vinyl"
    }
)

# Test with parameter overrides (what-if scenario)
calculator_builder_test(
    calculator_id="abc123...",
    test_inputs={"quantity": 100, "width_mm": 600, "height_mm": 900},
    parameter_overrides={
        "pricing.vinyl_cost": 12.50,  # Test 10% increase
        "pricing.rush_fee_24hr": 75.00  # Test higher rush fee
    }
)
```

---

### Tool 6: `calculator_builder_save`

**Purpose:** Save and activate calculator

**Parameters:**
```python
{
  "calculator_id": str,           # Required: Calculator UUID
  "activate": bool,               # Optional: Activate immediately (default: False)
  "version": str                  # Optional: Version string (default: auto-increment)
}
```

**Returns:**
```json
{
  "success": true,
  "calculator_id": "abc123...",
  "version": "1.0",
  "status": "active",
  "tool_name": "calculate_rush_24hr_vinyl",
  "message": "Calculator saved and activated successfully"
}
```

**Example Usage:**
```python
calculator_builder_save(
    calculator_id="abc123...",
    activate=True,
    version="1.0"
)
```

---

## 🔍 Query Tools

### Tool 1: `custom_calculator_get_schema_guide`

**Purpose:** Get comprehensive builder guide

**Parameters:**
```python
{}  # No parameters
```

**Returns:**
```json
{
  "success": true,
  "schema_version": "2.0",
  "guide": {
    "overview": "...",
    "json_structure": {...},
    "parameter_types": [...],
    "formula_syntax": {...},
    "examples": [...]
  }
}
```

---

### Tool 2: `custom_calculator_list`

**Purpose:** List all custom calculators

**Parameters:**
```python
{
  "category": str,                # Optional: Filter by category
  "is_active": bool,              # Optional: Filter by active status
  "created_by": str,              # Optional: Filter by creator
  "limit": int                    # Optional: Result limit (default: 50)
}
```

**Returns:**
```json
{
  "success": true,
  "calculators": [
    {
      "calculator_id": "abc123...",
      "name": "Rush24HourVinyl",
      "short_description": "Vinyl stickers - 24hr turnaround",
      "category": "rush_job",
      "version": "1.0",
      "created_at": "2025-12-14T10:30:00",
      "usage_count": 42,
      "is_active": true,
      "parameter_count": 5,
      "avg_calculation_time_ms": 15
    }
  ],
  "total_count": 12
}
```

---

### Tool 3: `custom_calculator_get_detail`

**Purpose:** Get full calculator details

**Parameters:**
```python
{
  "calculator_id": str            # Required: Calculator UUID or name
}
```

**Returns:**
```json
{
  "success": true,
  "calculator": {
    "calculator_id": "abc123...",
    "name": "Rush24HourVinyl",
    "description": "...",
    "json_definition": {...},
    "parameters_used": [
      {
        "parameter_name": "vinyl_cost",
        "source_table": "calculator_pricing_parameters",
        "current_value": 11.36,
        "unit": "$ per sqm"
      }
    ],
    "components_used": [
      {
        "component_name": "calculate_area_sqm",
        "formula": "width_mm / 1000 * height_mm / 1000"
      }
    ],
    "usage_stats": {
      "total_executions": 42,
      "avg_time_ms": 15,
      "last_used": "2025-12-14T15:20:00"
    }
  }
}
```

---

### Tool 4: `custom_calculator_search`

**Purpose:** Semantic search for calculators

**Parameters:**
```python
{
  "query": str,                   # Required: Search query
  "limit": int                    # Optional: Result limit (default: 10)
}
```

**Returns:**
```json
{
  "success": true,
  "results": [
    {
      "calculator_id": "abc123...",
      "name": "Rush24HourVinyl",
      "short_description": "...",
      "similarity_score": 0.92,
      "category": "rush_job"
    }
  ]
}
```

**Example Usage:**
```python
custom_calculator_search(
    query="vinyl stickers with fast turnaround",
    limit=5
)
```

---

### Tool 5: `custom_calculator_get_parameters`

**Purpose:** Get parameter references for calculator

**Parameters:**
```python
{
  "calculator_id": str            # Required: Calculator UUID
}
```

**Returns:**
```json
{
  "success": true,
  "parameters": [
    {
      "parameter_name": "vinyl_cost",
      "source_table": "calculator_pricing_parameters",
      "source_parameter_id": "vinyl_white_outdoor_cost",
      "current_value": 11.36,
      "unit": "$ per sqm",
      "used_in_steps": [2],
      "is_critical": true
    }
  ]
}
```

---

### Tool 6: `custom_calculator_get_usage_stats`

**Purpose:** Get calculator usage statistics

**Parameters:**
```python
{
  "calculator_id": str,           # Required: Calculator UUID
  "start_date": str,              # Optional: Start date (ISO format)
  "end_date": str                 # Optional: End date (ISO format)
}
```

**Returns:**
```json
{
  "success": true,
  "stats": {
    "total_executions": 156,
    "avg_calculation_time_ms": 18,
    "last_used_at": "2025-12-14T16:45:00",
    "executions_by_date": [
      {"date": "2025-12-14", "count": 12}
    ]
  }
}
```

---

### Tool 7: `custom_calculator_get_components`

**Purpose:** List all components for calculator

**Parameters:**
```python
{
  "calculator_id": str            # Required: Calculator UUID
}
```

**Returns:**
```json
{
  "success": true,
  "components": [
    {
      "component_name": "calculate_area_sqm",
      "component_type": "calculation",
      "formula": "width_mm / 1000 * height_mm / 1000",
      "output_variable": "area_sqm",
      "execution_order": 1
    }
  ]
}
```

---

## ⚙️ Execution Engine

### UniversalCalculatorExecutor

**Purpose:** Execute custom calculator formulas with safe evaluation

**Key Features:**
- **Safe Evaluation:** Uses `asteval` (restricted Python subset)
- **Parameter Resolution:** Resolves references from pricing library
- **Component Registry:** Loads reusable calculation blocks
- **Execution Trace:** Full audit trail of calculations
- **Error Handling:** Graceful failure with detailed error messages

**Execution Flow:**

```
1. Load calculator JSON from database
   ↓
2. Resolve parameter references
   - pricing.vinyl_cost → 11.36 from calculator_pricing_parameters
   - pricing.markup_percentage → 1.35 from calculator_pricing_parameters
   ↓
3. Build evaluation context
   - Input parameters: {quantity: 100, width_mm: 600, height_mm: 900}
   - Pricing constants: {vinyl_cost: 11.36, markup_percentage: 1.35}
   ↓
4. Execute calculation steps in order
   - Step 1: area_sqm = 600 / 1000 * 900 / 1000 → 0.54
   - Step 2: material_cost = 0.54 * 100 * 11.36 → 61.34
   - Step 3: total_price = (61.34 + 25.00) * 1.35 → 116.56
   ↓
5. Format result structure
   - total_price: 116.56
   - unit_price: 1.1656
   - breakdown: {material_cost: 61.34, setup_fee: 25.00, markup: 30.22}
   ↓
6. Return result with execution trace
```

**Supported Formula Functions:**

- **Math:** `abs()`, `min()`, `max()`, `round()`, `ceil()`, `floor()`
- **Operators:** `+`, `-`, `*`, `/`, `**`, `%`, `//`
- **Conditionals:** `value if condition else other_value`
- **Comparisons:** `>`, `<`, `>=`, `<=`, `==`, `!=`
- **Logical:** `and`, `or`, `not`

**Example Formula:**
```python
# Simple calculation
"width_mm * height_mm / 1000000"

# With conditional
"material_cost * 1.35 if quantity < 100 else material_cost * 1.25"

# With parameter reference
"area_sqm * pricing.vinyl_cost + pricing.setup_fee"

# With functions
"max(50.00, area_sqm * pricing.vinyl_cost)"
```

---

## 📖 Use Cases

### Use Case 1: Rush Job Pricing

**Scenario:** Create calculator for 24-hour rush vinyl stickers with 50% markup

**Steps:**

```python
# Step 1: Start calculator
result = calculator_builder_start(
    name="Rush24HourVinyl",
    description="Vinyl stickers with 24-hour turnaround and 50% rush markup",
    category="rush_job",
    tags=["vinyl", "rush", "stickers", "24hr"]
)
calculator_id = result['calculator_id']

# Step 2: Add input parameters
calculator_builder_add_parameter(
    calculator_id=calculator_id,
    parameter_name="quantity",
    parameter_type="integer",
    required=True,
    description="Number of vinyl stickers"
)

calculator_builder_add_parameter(
    calculator_id=calculator_id,
    parameter_name="width_mm",
    parameter_type="number",
    required=True,
    description="Width in millimeters"
)

calculator_builder_add_parameter(
    calculator_id=calculator_id,
    parameter_name="height_mm",
    parameter_type="number",
    required=True,
    description="Height in millimeters"
)

# Step 3: Add pricing parameters from library
calculator_builder_add_parameter(
    calculator_id=calculator_id,
    parameter_name="vinyl_cost",
    source="calculator_pricing_parameters:vinyl_white_outdoor_cost"
)

calculator_builder_add_parameter(
    calculator_id=calculator_id,
    parameter_name="rush_fee",
    source="calculator_pricing_parameters:rush_fee_24hr"
)

# Step 4: Define calculation steps
calculator_builder_set_formula(
    calculator_id=calculator_id,
    step_number=1,
    variable_name="area_sqm",
    formula="width_mm / 1000 * height_mm / 1000",
    description="Calculate area in square meters"
)

calculator_builder_set_formula(
    calculator_id=calculator_id,
    step_number=2,
    variable_name="material_cost",
    formula="area_sqm * quantity * pricing.vinyl_cost",
    description="Total material cost"
)

calculator_builder_set_formula(
    calculator_id=calculator_id,
    step_number=3,
    variable_name="total_price",
    formula="(material_cost + pricing.rush_fee) * 1.50",
    description="Apply 50% rush markup"
)

# Step 5: Test with sample inputs
test_result = calculator_builder_test(
    calculator_id=calculator_id,
    test_inputs={
        "quantity": 100,
        "width_mm": 600,
        "height_mm": 900
    }
)

print(f"Test result: ${test_result['result']['total_price']:.2f}")
print(f"Execution time: {test_result['execution_time_ms']}ms")

# Step 6: Save and activate
calculator_builder_save(
    calculator_id=calculator_id,
    activate=True,
    version="1.0"
)
```

---

### Use Case 2: What-If Scenario Testing

**Scenario:** Test impact of 10% material cost increase

**Steps:**

```python
# Test existing calculator with parameter overrides
result = calculator_builder_test(
    calculator_id="abc123...",  # Existing calculator
    test_inputs={
        "quantity": 500,
        "width_mm": 600,
        "height_mm": 900
    },
    parameter_overrides={
        "pricing.vinyl_cost": 12.50,  # 10% increase from 11.36
        "pricing.corflute_cost": 16.50  # 10% increase from 15.00
    }
)

print("Baseline price:", result['baseline_price'])
print("Scenario price:", result['result']['total_price'])
print("Delta:", result['delta_percentage'], "%")
```

---

### Use Case 3: Customer-Specific Pricing

**Scenario:** Create calculator with negotiated rates for specific customer

**Steps:**

```python
# Clone existing calculator
result = calculator_builder_start(
    name="Customer_ABC_VinylStickers",
    description="Vinyl stickers with negotiated rates for ABC Corp",
    based_on_calculator="StandardVinylCalculator",
    category="customer_specific",
    tags=["vinyl", "customer_abc", "negotiated"]
)

calculator_id = result['calculator_id']

# Override specific pricing parameters
calculator_builder_set_formula(
    calculator_id=calculator_id,
    step_number=1,
    variable_name="negotiated_markup",
    formula="1.20",  # 20% instead of standard 35%
    description="Negotiated markup for ABC Corp"
)

calculator_builder_set_formula(
    calculator_id=calculator_id,
    step_number=5,
    variable_name="total_price",
    formula="(material_cost + labor_cost) * negotiated_markup",
    description="Apply negotiated markup"
)

# Test and activate
calculator_builder_test(calculator_id=calculator_id, test_inputs={...})
calculator_builder_save(calculator_id=calculator_id, activate=True)
```

---

## 🔧 API Reference

### Wrapper Layer

**File:** `UI/modules_external/quote-calculator/implementations/calculator_builder_wrapper.py`

**Imports:**
```python
from tools.registry_v3 import tool_executor
from AI_infrastructure.shared.database_utils import execute_query
```

**Tool Registration:**
All tools use `@tool_executor()` decorator for Registry V3 integration.

**Import Pattern:**
Import database utilities inside functions to avoid circular imports:
```python
@tool_executor()
def my_tool(param1: str):
    from AI_infrastructure.shared.database_utils import execute_query
    # Function implementation
```

---

### Backend Layer

**File:** `UI/modules_external/quote-calculator/backend/calculator_builder_tools.py`

**Class:** `CalculatorBuilderTools`

**Methods:**
- `calculator_builder_start()`
- `calculator_builder_add_parameter()`
- `calculator_builder_set_formula()`
- `calculator_builder_add_component()`
- `calculator_builder_test()`
- `calculator_builder_save()`

---

### Query Library

**File:** `UI/modules_external/quote-calculator/backend/query_library.py`

**Custom Calculator Queries:**

- `_sql_list_custom_calculators()` - List all calculators
- `_sql_get_custom_calculator_detail()` - Get calculator detail
- `_sql_search_custom_calculators()` - Semantic search
- `_sql_get_custom_calculator_parameters()` - Get parameter references
- `_sql_get_custom_calculator_usage_stats()` - Get usage statistics
- `_sql_get_custom_calculator_components()` - Get components

**Query Execution Pattern:**
```python
from AI_infrastructure.shared.database_utils import execute_query

result = execute_query(
    query_library._sql_list_custom_calculators({"category": "rush_job"}),
    fetch_mode='all'
)
```

---

## 📝 Examples

### Example 1: Simple Area-Based Calculator

**Goal:** Calculate price based on area with flat markup

```python
# Create calculator
result = calculator_builder_start(
    name="SimpleAreaPricing",
    description="Basic area-based pricing",
    category="custom_quote"
)
calc_id = result['calculator_id']

# Add parameters
calculator_builder_add_parameter(calc_id, "width_mm", "number", True)
calculator_builder_add_parameter(calc_id, "height_mm", "number", True)
calculator_builder_add_parameter(calc_id, "quantity", "integer", True)

# Add pricing constant
calculator_builder_set_formula(
    calc_id, 1, "price_per_sqm", "15.00", "Price per square meter"
)

# Calculate area
calculator_builder_set_formula(
    calc_id, 2, "area_sqm", "width_mm / 1000 * height_mm / 1000", "Area in sqm"
)

# Calculate total
calculator_builder_set_formula(
    calc_id, 3, "total_price", "area_sqm * quantity * price_per_sqm", "Total price"
)

# Test
test_result = calculator_builder_test(
    calc_id,
    {"width_mm": 1000, "height_mm": 1000, "quantity": 10}
)
# Expected: 1.0 sqm × 10 × $15.00 = $150.00

# Activate
calculator_builder_save(calc_id, activate=True)
```

---

### Example 2: Tiered Quantity Pricing

**Goal:** Apply different markups based on quantity tiers

```python
# Create calculator
result = calculator_builder_start(
    name="TieredQuantityPricing",
    description="Different markups for quantity tiers",
    category="custom_quote"
)
calc_id = result['calculator_id']

# Add parameters
calculator_builder_add_parameter(calc_id, "quantity", "integer", True)
calculator_builder_add_parameter(calc_id, "base_cost", "number", True)

# Define tier thresholds
calculator_builder_set_formula(
    calc_id, 1, "tier1_threshold", "50", "Tier 1: 1-50 units"
)
calculator_builder_set_formula(
    calc_id, 2, "tier2_threshold", "100", "Tier 2: 51-100 units"
)

# Calculate markup based on quantity
calculator_builder_set_formula(
    calc_id, 3, "markup",
    "1.50 if quantity <= tier1_threshold else (1.35 if quantity <= tier2_threshold else 1.20)",
    "Tiered markup: 50% / 35% / 20%"
)

# Calculate total
calculator_builder_set_formula(
    calc_id, 4, "total_price", "base_cost * quantity * markup", "Total with tiered markup"
)

# Test different quantities
for qty in [25, 75, 150]:
    result = calculator_builder_test(calc_id, {"quantity": qty, "base_cost": 10.0})
    print(f"Qty {qty}: ${result['result']['total_price']:.2f}")
# Expected: 25 → $375.00 (50%), 75 → $1012.50 (35%), 150 → $1800.00 (20%)
```

---

### Example 3: Conditional Setup Fee

**Goal:** Apply setup fee only for orders below threshold

```python
# Create calculator
result = calculator_builder_start(
    name="ConditionalSetupFee",
    description="Setup fee waived for large orders",
    category="custom_quote"
)
calc_id = result['calculator_id']

# Add parameters
calculator_builder_add_parameter(calc_id, "quantity", "integer", True)
calculator_builder_add_parameter(calc_id, "unit_cost", "number", True)

# Define constants
calculator_builder_set_formula(
    calc_id, 1, "setup_fee", "50.00", "Standard setup fee"
)
calculator_builder_set_formula(
    calc_id, 2, "waiver_threshold", "100", "No setup fee above this quantity"
)

# Calculate material cost
calculator_builder_set_formula(
    calc_id, 3, "material_cost", "quantity * unit_cost", "Total material cost"
)

# Conditional setup fee
calculator_builder_set_formula(
    calc_id, 4, "applicable_setup_fee",
    "0.00 if quantity >= waiver_threshold else setup_fee",
    "Setup fee waived for qty >= 100"
)

# Calculate total
calculator_builder_set_formula(
    calc_id, 5, "total_price", "material_cost + applicable_setup_fee", "Total price"
)

# Test
for qty in [50, 100, 200]:
    result = calculator_builder_test(calc_id, {"quantity": qty, "unit_cost": 2.0})
    print(f"Qty {qty}: ${result['result']['total_price']:.2f}")
# Expected: 50 → $150.00 (includes $50 fee), 100 → $200.00 (no fee), 200 → $400.00 (no fee)
```

---

### Example 4: Multi-Component Calculator

**Goal:** Combine multiple reusable components

```python
# Create calculator
result = calculator_builder_start(
    name="MultiComponentCalculator",
    description="Uses multiple reusable components",
    category="custom_quote"
)
calc_id = result['calculator_id']

# Add parameters
calculator_builder_add_parameter(calc_id, "width_mm", "number", True)
calculator_builder_add_parameter(calc_id, "height_mm", "number", True)
calculator_builder_add_parameter(calc_id, "quantity", "integer", True)

# Component 1: Calculate area
calculator_builder_add_component(
    calc_id,
    component_name="calculate_area",
    component_type="calculation",
    formula="width_mm / 1000 * height_mm / 1000",
    input_parameters={"width_mm": "number", "height_mm": "number"},
    output_variable="area_sqm",
    execution_order=1
)

# Component 2: Calculate perimeter
calculator_builder_add_component(
    calc_id,
    component_name="calculate_perimeter",
    component_type="calculation",
    formula="2 * (width_mm + height_mm) / 1000",
    input_parameters={"width_mm": "number", "height_mm": "number"},
    output_variable="perimeter_m",
    execution_order=2
)

# Use component outputs in main calculation
calculator_builder_set_formula(
    calc_id, 1, "material_cost",
    "area_sqm * quantity * 15.00",
    "Material cost based on area"
)

calculator_builder_set_formula(
    calc_id, 2, "trimming_cost",
    "perimeter_m * quantity * 2.50",
    "Trimming cost based on perimeter"
)

calculator_builder_set_formula(
    calc_id, 3, "total_price",
    "material_cost + trimming_cost",
    "Total price"
)

# Test
result = calculator_builder_test(
    calc_id,
    {"width_mm": 1000, "height_mm": 500, "quantity": 10}
)
print(f"Total: ${result['result']['total_price']:.2f}")
# Expected: (1.0×0.5) × 10 × $15.00 + (2×(1.0+0.5)) × 10 × $2.50 = $75.00 + $75.00 = $150.00
```

---

## 🎓 Best Practices

### 1. Parameter Naming
- Use descriptive names: `vinyl_cost_per_sqm` not `vc`
- Use consistent units in names: `width_mm`, `area_sqm`, `cost_per_unit`
- Prefix pricing parameters: `pricing.vinyl_cost`, `pricing.markup_percentage`

### 2. Formula Documentation
- Always include description for each calculation step
- Document assumptions: "Assumes 3mm corflute standard"
- Document units: "Returns price in AUD including GST"

### 3. Testing Strategy
- Test edge cases: minimum quantity, maximum size
- Test boundary conditions: exactly at tier threshold
- Test parameter overrides for what-if scenarios
- Validate result structure matches expectations

### 4. Version Control
- Increment version for significant changes: 1.0 → 2.0
- Use minor versions for formula tweaks: 1.0 → 1.1
- Keep parent_version_id chain intact

### 5. Performance
- Minimize calculation steps where possible
- Use components for repeated calculations
- Avoid complex nested conditionals
- Profile execution time with `calculator_builder_test`

### 6. Error Handling
- Provide clear error messages
- Validate parameter ranges in formulas: `max(0, value)`
- Handle division by zero: `value / max(1, divisor)`
- Use conditional expressions for safety: `value if value > 0 else default`

---

## 🔒 Security Considerations

### Formula Evaluation
- **asteval** restricts Python expressions to safe subset
- No file system access
- No network access
- No module imports
- No dangerous builtins (`eval`, `exec`, `__import__`)

### Database Access
- All queries use parameterized statements
- CASCADE DELETE protects referential integrity
- Connection pooling prevents resource exhaustion

### Input Validation
- Parameter types enforced: integer, number, select, boolean
- Required parameters validated before execution
- Range checks in formulas: `min()`, `max()`

---

## 📊 Monitoring & Analytics

### Usage Tracking

Every calculator execution updates:
- `usage_count` - Total number of executions
- `last_used_at` - Timestamp of last execution
- `avg_calculation_time_ms` - Rolling average execution time

### Performance Metrics

Query execution time tracking:
```sql
SELECT
    calculator_id,
    name,
    usage_count,
    avg_calculation_time_ms,
    last_used_at
FROM custom_calculators
ORDER BY usage_count DESC
LIMIT 10;
```

### Impact Analysis

Find calculators affected by parameter changes:
```sql
SELECT
    c.calculator_id,
    c.name,
    cp.parameter_name,
    cp.source_parameter_id
FROM custom_calculators c
JOIN custom_calculator_parameters cp ON c.calculator_id = cp.calculator_id
WHERE cp.source_parameter_id = 'vinyl_white_outdoor_cost'
ORDER BY c.usage_count DESC;
```

---

## 🚀 Future Enhancements

### Planned Features

1. **Visual Formula Builder** - Drag-and-drop interface for formulas
2. **A/B Testing Framework** - Compare calculator performance
3. **Automated Testing** - Regression tests for calculators
4. **Calculator Templates** - Pre-built templates for common scenarios
5. **Excel Import** - Import formulas from spreadsheets
6. **Formula Debugger** - Step-by-step execution with breakpoints
7. **Multi-Currency Support** - Automatic currency conversion
8. **Historical Snapshots** - Track parameter changes over time

---

## 📞 Support

### Common Issues

**Issue:** "Calculator not found"
- Check `calculator_id` is correct UUID
- Verify calculator is active: `is_active = TRUE`

**Issue:** "Formula execution failed"
- Check formula syntax (asteval safe subset)
- Verify all referenced variables exist
- Check for division by zero

**Issue:** "Parameter not resolved"
- Verify parameter exists in `calculator_pricing_parameters`
- Check `source_parameter_id` matches exactly
- Confirm parameter is active

**Issue:** "Execution timeout"
- Simplify calculation steps
- Move complex logic to components
- Check for infinite loops in conditionals

---

## 📚 Additional Resources

- **Migration File:** `UI/modules_external/quote-calculator/database/migrations/005_custom_calculators_tables.sql`
- **Builder Tools:** `UI/modules_external/quote-calculator/backend/calculator_builder_tools.py`
- **Execution Engine:** `UI/modules_external/quote-calculator/backend/universal_calculator_executor.py`
- **Query Library:** `UI/modules_external/quote-calculator/backend/query_library.py`
- **Wrapper Layer:** `UI/modules_external/quote-calculator/implementations/calculator_builder_wrapper.py`

---

**End of Custom Calculator Module Master Documentation**
