# Quote Calculator Module - Parts 3, 4, 5 (Complete Reference Continuation)

**Date:** December 18, 2025  
**This file contains:** Parts 3-5 of complete module documentation  
**See also:** README.md (Parts 1-2 overview and calculator inventory)

---

# PART 3: IMPLEMENTATION LAYER

## 8. Tool Schemas & Definitions

### Schema File Structure
- `calculator_tools.json` - 36 calculator tools (2,469 lines)
- `calculator_pricing_tools.json` - 4 database query tools  
- `custom_calculator_tools.json` - 6 builder tools
- `custom_calculator_query_tools.json` - 7 query tools
- `query_library_tools.json` - 2 pre-built query access tools

### Schema Pattern
```json
{
  "name": "calculate_business_cards",
  "description": "Calculate business card quotes",
  "parameters": {
    "quantity": {"type": "integer", "enum": [100, 250, 500, 1000, 2000, 5000, 10000]},
    "stock_type": {"type": "string", "enum": ["standard", "premium"]}
  },
  "returns": {"type": "object"},
  "platform": "quote_calculator"
}
```

---

## 9. Wrapper Layer Architecture

### Type Enforcement System
```python
# schema_validator.py
@enforce_schema_types
def calculate_business_cards(quantity: int, stock_type: str):
    # Decorator auto-converts "500" string → 500 integer
    calculator = EconomicalBusinessCardsShopifyCalculator()
    return calculator.calculate(quantity=quantity, ...)
```

### Wrapper Patterns

**Pattern 1: Direct Shopify**
```python
@enforce_schema_types
def calculate_folded_flyers_shopify(...):
    calculator = FoldedFlyersShopifyCalculator()
    result = calculator.calculate(...)
    return {"success": True, "quote": result}
```

**Pattern 2: GOD with Database**
```python
@enforce_schema_types
def calculate_flyers_god(...):
    db = InHousePrintDB()
    calculator = FlyerCalculatorGOD(db)
    result = calculator.calculate(...)
    return {"success": True, "quote": result}
```

**Pattern 3: Conditional Routing**
```python
@enforce_schema_types
def calculate_business_cards(stock_type, ...):
    if stock_type == "premium":
        calculator = PremiumBusinessCardsShopifyCalculator()
    else:
        calculator = EconomicalBusinessCardsShopifyCalculator()
    return calculator.calculate(...)
```

---

## 10. Backend Implementations

### Shopify Calculator Structure
```python
class ProductNameShopifyCalculator:
    PRICE_TABLE = {
        (quantity, size, stock, options): price,
        # Hundreds of entries...
    }
    
    def calculate(self, **params):
        key = (params['quantity'], params['size'], ...)
        base_price = self.PRICE_TABLE[key]
        gst = base_price * 0.10
        return CalculationResult(total=base_price + gst, ...)
```

### GOD Calculator Structure
```python
class GOD_ProductCalculator:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def calculate(self, **params):
        # Query database for pricing
        setup = self.db.query("SELECT SetupCost FROM ProductPricing...")
        stock = self.db.query("SELECT UnitCost FROM StockPricing...")
        
        # Calculate
        base_cost = setup + (quantity * stock)
        gst = base_cost * 0.10
        return CalculationResult(total=base_cost + gst, ...)
```

### Common Components
```python
# common_components.py
def calculate_gst(base_price, rate=0.10):
    return base_price * rate

def calculate_area_sqm(width_mm, height_mm):
    return (width_mm * height_mm) / 1_000_000

def apply_quantity_discount(base, quantity, tiers):
    for min_qty, discount in sorted(tiers.items(), reverse=True):
        if quantity >= min_qty:
            return base * (1 - discount)
    return base
```

---

# PART 4: ADVANCED FEATURES

## 11. Query Library System (77 Queries)

### Query Categories
1. **Sales & Revenue** (15 queries) - Trends, product performance, customer analysis
2. **Customer Analytics** (8 queries) - Retention, cohorts, lifetime value
3. **Product Analysis** (12 queries) - Performance, pricing, profitability
4. **Operational Metrics** (10 queries) - Efficiency, turnaround, capacity
5. **Quote Analysis** (6 queries) - Conversion rates, patterns
6. **Stock & Materials** (7 queries) - Inventory, usage, costs
7. **Pricing Intelligence** (5 queries) - Optimization, competitive analysis
8. **Time Series** (4 queries) - Trends, forecasting
9. **Geographic** (3 queries) - Regional performance
10. **Staff Performance** (3 queries) - Productivity metrics
11. **Financial** (2 queries) - Cash flow, profitability
12. **Custom Reports** (2 queries) - Ad-hoc analysis

### Query Library Class
```python
class QueryLibrary:
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.query_catalog = self._build_query_catalog()  # 77 queries
    
    def execute_query(self, query_name: str, **parameters):
        meta = self.query_catalog[query_name]
        params = self._apply_defaults(meta['parameters'], parameters)
        sql = getattr(self, f"_sql_{query_name}")(params)
        results = self.db.execute(sql)
        return {"success": True, "results": results, "metadata": meta}
```

### Sample Queries

**Monthly Revenue Trend:**
```sql
SELECT 
    FORMAT(OrderDate, 'yyyy-MM') AS YearMonth,
    SUM(TotalAmount) AS TotalRevenue,
    COUNT(DISTINCT OrderID) AS OrderCount,
    AVG(OrderAmount) AS AvgOrderValue
FROM Orders
WHERE OrderDate >= DATEADD(MONTH, -12, GETDATE())
GROUP BY FORMAT(OrderDate, 'yyyy-MM')
ORDER BY YearMonth
```

**Top Products by Revenue:**
```sql
SELECT 
    p.ProductType,
    SUM(ol.LineTotal) AS TotalRevenue,
    COUNT(DISTINCT ol.OrderID) AS OrderCount,
    AVG(ol.LineTotal) AS AvgPrice
FROM OrderLines ol
JOIN Products p ON ol.ProductID = p.ProductID
WHERE ol.OrderDate >= DATEADD(MONTH, -12, GETDATE())
GROUP BY p.ProductType
ORDER BY TotalRevenue DESC
```

**Customer Retention Cohort:**
```sql
WITH CustomerCohorts AS (
    SELECT 
        CustomerID,
        FORMAT(MIN(OrderDate), 'yyyy-MM') AS CohortMonth
    FROM Orders
    GROUP BY CustomerID
)
SELECT 
    CohortMonth,
    COUNT(DISTINCT CustomerID) AS CustomersCount,
    DATEDIFF(MONTH, CohortMonth, GETDATE()) AS MonthsActive,
    CAST(COUNT(DISTINCT o.OrderID) * 100.0 / COUNT(DISTINCT cc.CustomerID) AS DECIMAL(5,2)) AS RetentionRate
FROM CustomerCohorts cc
LEFT JOIN Orders o ON cc.CustomerID = o.CustomerID
GROUP BY CohortMonth
ORDER BY CohortMonth
```

---

## 12. Calculator Pricing Database (8 Tables)

### Schema Overview
```sql
-- pricing_constants: Base costs and rates
CREATE TABLE pricing_constants (
    id SERIAL PRIMARY KEY,
    constant_name VARCHAR(100) UNIQUE,
    constant_value DECIMAL(10, 4),
    unit VARCHAR(50),
    category VARCHAR(100)
);

-- product_options: Product configuration
CREATE TABLE product_options (
    id SERIAL PRIMARY KEY,
    product_type VARCHAR(100),
    option_name VARCHAR(100),
    option_values JSONB,  -- Array of valid values
    default_value TEXT,
    is_required BOOLEAN
);

-- stock_pricing: Paper stock costs
CREATE TABLE stock_pricing (
    id SERIAL PRIMARY KEY,
    stock_name VARCHAR(200),
    gsm INTEGER,
    finish VARCHAR(50),  -- gloss, matt, satin
    cost_per_sheet DECIMAL(10, 4),
    supplier VARCHAR(100)
);

-- finishing_costs: Celloglaze, lamination
CREATE TABLE finishing_costs (
    id SERIAL PRIMARY KEY,
    finishing_type VARCHAR(100),
    cost_per_unit DECIMAL(10, 4),
    minimum_cost DECIMAL(10, 2),
    applies_to JSONB
);

-- binding_costs: Saddle, perfect, spiral, wire
CREATE TABLE binding_costs (
    id SERIAL PRIMARY KEY,
    binding_type VARCHAR(100),
    min_pages INTEGER,
    max_pages INTEGER,
    cost_per_unit DECIMAL(10, 4),
    setup_cost DECIMAL(10, 2)
);

-- quantity_tiers: Volume discounts
CREATE TABLE quantity_tiers (
    id SERIAL PRIMARY KEY,
    product_type VARCHAR(100),
    min_quantity INTEGER,
    max_quantity INTEGER,
    discount_rate DECIMAL(5, 4)
);

-- historical_quotes: Past quotes for analysis
CREATE TABLE historical_quotes (
    id SERIAL PRIMARY KEY,
    quote_date TIMESTAMP DEFAULT NOW(),
    product_type VARCHAR(100),
    parameters JSONB,
    calculated_price DECIMAL(10, 2),
    actual_price DECIMAL(10, 2),
    variance_percent DECIMAL(5, 2)
);

-- price_variance_analysis: Accuracy tracking
CREATE TABLE price_variance_analysis (
    id SERIAL PRIMARY KEY,
    analysis_date DATE,
    product_type VARCHAR(100),
    avg_variance_percent DECIMAL(5, 2),
    quotes_analyzed INTEGER,
    recommendations TEXT
);
```

### Database Access Tools

**Query Tool:**
```python
def calculator_database_query(sql: str, params: Dict = None):
    """Execute SELECT query (read-only)"""
    if not sql.strip().upper().startswith('SELECT'):
        return {"success": False, "error": "Only SELECT allowed"}
    
    db = CalculatorPricingDB()
    results = db.execute_query(sql, params)
    return {"success": True, "results": results, "row_count": len(results)}
```

**Modify Tool:**
```python
def calculator_database_modify(sql: str, params: Dict, reason: str):
    """Execute INSERT/UPDATE/DELETE with audit trail"""
    if not reason:
        return {"success": False, "error": "Reason required"}
    
    db = CalculatorPricingDB()
    db.log_modification(sql, params, reason)
    result = db.execute_modify(sql, params)
    return {"success": True, "rows_affected": result.rowcount}
```

---

## 13. Custom Calculator Builder

### Builder Workflow

**Step 1: Start Calculator**
```python
result = calculator_builder_start(
    name="Canvas Prints Calculator",
    description="Custom canvas pricing",
    category="signage",
    customer_id=1,
    user_id=5
)
calculator_id = result['calculator_id']
```

**Step 2: Add Parameters**
```python
calculator_builder_add_parameter(
    calculator_id=calculator_id,
    parameter_name="width_cm",
    parameter_type="integer",
    min_value=20,
    max_value=200,
    description="Canvas width"
)

calculator_builder_add_parameter(
    calculator_id=calculator_id,
    parameter_name="frame_type",
    parameter_type="string",
    enum_values=["none", "black", "white", "floating"],
    description="Frame type"
)
```

**Step 3: Set Formulas**
```python
calculator_builder_set_formula(
    calculator_id=calculator_id,
    step_number=1,
    step_name="area_sqm",
    formula="(width_cm * height_cm) / 10000"
)

calculator_builder_set_formula(
    calculator_id=calculator_id,
    step_number=2,
    step_name="base_cost",
    formula="area_sqm * 45.00"
)

calculator_builder_set_formula(
    calculator_id=calculator_id,
    step_number=3,
    step_name="frame_cost",
    formula="0 if frame_type == 'none' else 25"
)

calculator_builder_set_formula(
    calculator_id=calculator_id,
    step_number=4,
    step_name="total",
    formula="(base_cost + frame_cost) * 1.10"
)
```

**Step 4: Test**
```python
test_result = calculator_builder_test(
    calculator_id=calculator_id,
    test_inputs={"width_cm": 60, "height_cm": 80, "frame_type": "black"}
)
# Returns: {"success": True, "results": {...}, "final_result": 51.26}
```

**Step 5: Save**
```python
calculator_builder_save(
    calculator_id=calculator_id,
    as_template=False,
    publish=True
)
```

### Universal Calculator Executor

```python
from asteval import Interpreter

class UniversalCalculatorExecutor:
    def __init__(self):
        self.interpreter = Interpreter()
        # Add safe math functions
        self.interpreter.symtable.update({
            'sqrt': math.sqrt,
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'ceil': math.ceil,
            'floor': math.floor
        })
        # Block dangerous operations
        self.interpreter.no_import = True
        self.interpreter.no_print = True
    
    def safe_eval(self, formula: str, variables: Dict):
        for name, value in variables.items():
            self.interpreter.symtable[name] = value
        
        result = self.interpreter(formula)
        
        if self.interpreter.error:
            raise ValueError(f"Evaluation error: {self.interpreter.error[0]}")
        
        return result
```

**Supported Formula Syntax:**
- Operators: `+`, `-`, `*`, `/`, `**`, `%`
- Functions: `sqrt()`, `abs()`, `round()`, `min()`, `max()`, `ceil()`, `floor()`
- Conditionals: `value if condition else other`
- Comparisons: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `and`, `or`, `not`

**Example Formulas:**
```python
"quantity * base_price"
"base_cost * (1 + gst_rate)"
"setup_cost if quantity < 100 else 0"
"round(price * 1.10, 2)"
"min(quantity * rate, max_price)"
```

---

# PART 5: USAGE & REFERENCE

## 14. Usage Examples

### Example 1: Business Cards (Shopify)
```python
result = calculate_economical_business_cards_shopify(
    quantity=1000,
    finish_size="90x55mm",
    stock_type="standard",
    print_type="double_sided",
    celloglaze="gloss"
)
# Result: {"success": True, "total_price": 95.00, "per_unit_price": 0.095, ...}
```

### Example 2: Flyers (GOD)
```python
result = calculate_flyers_god(
    quantity=5000,
    size="A5",
    stock="150gsm Gloss Art",
    sides=2,
    celloglaze="gloss"
)
# Result: {"success": True, "total_price": 485.50, "breakdown": {...}, ...}
```

### Example 3: Query Historical Data
```python
result = query_library_execute(
    query_name="monthly_revenue_trend",
    parameters={"months": 12}
)
# Result: {"success": True, "results": [{...}, {...}], "row_count": 12}
```

### Example 4: Database Query
```python
result = calculator_database_query(
    sql="SELECT stock_name, gsm, cost_per_sheet FROM stock_pricing WHERE gsm >= 150"
)
# Result: {"success": True, "results": [{...}], "row_count": 25}
```

### Example 5: Build Custom Calculator
```python
# Complete workflow shown in Section 13
calculator_id = calculator_builder_start(...)
calculator_builder_add_parameter(calculator_id, ...)
calculator_builder_set_formula(calculator_id, ...)
test_result = calculator_builder_test(calculator_id, test_inputs)
calculator_builder_save(calculator_id, publish=True)
```

---

## 15. Testing & Validation

### Test Suite
- Location: `tests/test_comprehensive.py`
- Coverage: 40 tests across 5 categories
- Status: ✅ 39/40 passing (97.5%)

**Test Categories:**
1. Shopify Calculator Tests (32)
2. GOD Calculator Tests (4)
3. Type Enforcement Tests (5)
4. Query Library Tests (10)
5. Custom Calculator Tests (8)

**Run Tests:**
```powershell
cd c:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator
python tests/test_comprehensive.py
```

### Smoke Test Report
- Location: `DOCUMENTATION/SMOKE_TEST_REPORT.md`
- Size: ~6,000 lines
- Coverage: All 36 calculator tools + database + query library

---

## 16. Troubleshooting Guide

### Issue 1: Tool Not Found
**Symptom:** `{"error": "Tool not found in registry"}`  
**Fix:** Restart Flask server to reload registry
```powershell
cd AI_infrastructure
python flask_app.py
```

### Issue 2: Type Mismatch
**Symptom:** `TypeError: unsupported operand type(s) for *: 'str' and 'int'`  
**Fix:** Ensure wrapper uses `@enforce_schema_types` decorator

### Issue 3: Database Unavailable (GOD)
**Symptom:** `{"error": "Database unavailable: Connection timeout"}`  
**Fix:** Use Shopify calculators instead (no database required)

### Issue 4: asteval Missing
**Symptom:** `ModuleNotFoundError: No module named 'asteval'`  
**Fix:** `pip install asteval==1.0.7`

### Issue 5: Empty Query Results
**Symptom:** `{"results": [], "row_count": 0}`  
**Fix:** Increase date range parameter (e.g., months=36 instead of 12)

### Issue 6: Circular Import
**Symptom:** `ImportError: cannot import from partially initialized module`  
**Fix:** Import inside functions, not at module level
```python
# WRONG:
from AI_infrastructure.shared.database_utils import execute_query
def my_tool(): ...

# RIGHT:
def my_tool():
    from AI_infrastructure.shared.database_utils import execute_query
    ...
```

### Issue 7: Price Mismatch
**Symptom:** Calculator returns different price than website  
**Fix:** 
1. Verify parameters match exactly
2. Update calculator PRICE_TABLE if website changed
3. Check for recent Shopify pricing updates

---

## Summary Statistics

### Module Totals
- **Total Tools:** 57 (36 calculators + 21 support tools)
- **Total Lines:** ~48,291
- **Shopify Calculators:** 32 (primary system)
- **GOD Calculators:** 4 (legacy system)
- **Pre-Built Queries:** 77
- **Database Tables:** 12 (8 pricing + 4 custom calculator)
- **Test Coverage:** 97.5% (39/40 tests passing)

### File Breakdown
- Schema files: 8
- Wrapper files: 4
- Backend files: 42
- Documentation files: 11
- Test files: 3

---

## Quick Reference

### Essential Commands
```powershell
# Start server
cd AI_infrastructure; python flask_app.py

# Run tests
cd UI/modules_external/quote-calculator; python tests/test_comprehensive.py

# Check registry
python -c "from tools.registry_v3 import RegistryV3; print(len(RegistryV3().tools))"

# View logs
Get-Content AI_infrastructure/flask_app.log -Tail 50
```

### Key Files
| File | Purpose |
|------|---------|
| `schema/calculator_tools.json` | All 36 tool definitions (2,469 lines) |
| `implementations/calculator_wrapper.py` | Main routing (2,014 lines) |
| `backend/query_library.py` | 77 SQL queries (5,958 lines) |
| `backend/calculator_builder_tools.py` | Custom calculator builder (632 lines) |
| `README.md` | Module overview (703 lines) |
| `CUSTOM_CALCULATOR_MODULE_MASTER.md` | Custom calculator docs (1,583 lines) |
| `QUOTE_CALCULATOR_MODULE_MASTER_PARTS_3_4_5.md` | **This file** |

### Common Patterns

**Calculate Quote:**
```python
result = calculate_[product]_shopify(quantity=..., size=..., stock=...)
```

**Query Data:**
```python
result = query_library_execute(query_name="...", parameters={...})
```

**Database Access:**
```python
result = calculator_database_query(sql="SELECT ...")
```

**Build Calculator:**
```python
id = calculator_builder_start(name="...")
calculator_builder_add_parameter(id, ...)
calculator_builder_set_formula(id, ...)
calculator_builder_test(id, test_inputs)
calculator_builder_save(id, publish=True)
```

---

**END OF PARTS 3, 4, 5**

**Last Updated:** December 18, 2025  
**Total Documentation:** Parts 1-2 (README.md) + Parts 3-5 (this file) = Complete coverage  
**Module Status:** Production Ready ✅

**Related Documentation:**
- Parts 1-2: See `README.md` (overview, architecture, calculator inventory)
- Custom Calculators: See `CUSTOM_CALCULATOR_MODULE_MASTER.md`
- Project-Wide: See `.github/copilot-instructions.md`
