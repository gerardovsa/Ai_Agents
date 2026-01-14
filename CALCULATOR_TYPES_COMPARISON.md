# Calculator Type Comparison

## Overview
There are **3 types** of calculators in the system:

---

## 1️⃣ **OLD-STYLE CALCULATORS** (Deprecated)
**Functions:** `calculate_flyers`, `calculate_letterheads`, `calculate_perfect_bound_books`, `calculate_corflute_signs`

### Backend
- **File:** `implementations/complete_calculator_implementation.py` (6,277 lines)
- **Class:** `ComprehensiveQuoteCalculator`
- **Data Source:** SQL Server FredDEV database

### Method
- Complex business logic with database queries
- Wraps database calls in Python calculator logic
- Originally built as monolithic calculator

### Features
- ✅ Full quote breakdowns
- ✅ Stock database lookups  
- ✅ Pricing calculations
- ✅ Turnaround time estimates

### Interface
Simple, generic parameters:
```python
calculate_flyers(
    quantity=1000,
    width=210,
    height=297,
    stock_gsm=150,
    print_mode="double_sided",
    cello_type="gloss_both_sides"
)
```

### Status
⚠️ **DEPRECATED** - Kept for backwards compatibility only  
⚠️ Use GOD calculators instead for new implementations

---

## 2️⃣ **GOD CALCULATORS** (Primary System)
**Functions:** `calculate_flyers_god`, `calculate_letterheads_god`, `calculate_perfect_bound_books_god`, `calculate_corflute_signs_god`

### Backend
- **Files:** `backend/god_calculators/GOD_*.py`
- **Classes:** `FlyerCalculatorGOD`, `LetterheadCalculatorGOD`, etc.
- **Data Source:** SQL Server FredDEV database (real-time pricing)

### Method
- Direct database queries for live pricing data
- Reads actual price tables from database
- Most accurate and up-to-date pricing

### Features
- ✅ **Most accurate pricing** (reads from actual price tables)
- ✅ Comprehensive options (folding, lamination, special finishes)
- ✅ Detailed cost breakdowns with itemized pricing
- ✅ Production time calculations
- ✅ Stock validation and availability checks
- ✅ Supports all print modes and finishing options

### Interface
Detailed, database-driven parameters:
```python
calculate_flyers_god(
    quantity=1000,
    width=210,
    height=297,
    gsm=150,
    print_side1=1,        # 0=none, 1=colour, 2=b&w, 3=b&w on colour
    print_side2=0,
    folding_required=False,
    folding_passes=1,
    cello_required=False,
    cello_side1=0,        # 0=none, 1=gloss, 2=matt
    cello_side2=0,
    discount=0.0
)
```

### Status
✅ **ACTIVE** - Primary calculator system  
✅ Recommended for all internal quoting  
✅ Most accurate and maintained

---

## 3️⃣ **SHOPIFY CALCULATORS** (Website Integration)
**Functions:** `calculate_economical_business_cards_shopify`, `calculate_premium_business_cards_shopify`, `calculate_folded_flyers_shopify`, `calculate_wire_bound_books_shopify`, `calculate_spiral_bound_books_shopify`

### Backend
- **Location:** `In_House_SQL/G_Folder/Quote_Calculator/shopify_calculators/`
- **Files:** Standalone Python files (one per product)
- **Data Source:** **HARDCODED** pricing tables (copied from Shopify website)

### Method
- JavaScript-to-Python port of website product configurators
- Pricing tables embedded directly in code
- Exact match to inhouseprint.com.au Shopify DPO pricing

### Features
- ✅ **Exact match to website pricing** (100% accurate to customer quotes)
- ✅ No database required (standalone)
- ✅ Fast calculations (no DB queries)
- ✅ Standard Shopify product options
- ❌ Limited to products on Shopify website
- ❌ Requires manual updates when website prices change

### Interface
Shopify-specific parameters (matches website configurator):
```python
calculate_premium_business_cards_shopify(
    quantity=1000,
    print_sides="Double side print",     # Exact Shopify option text
    print_type="Colour",
    finish_size="90mm x 55mm",
    paper_stock="Satin 350GSM",           # Exact Shopify stock names
    celloglaze="1 Side Gloss",            # Exact Shopify finish names
    artworks=1
)
```

### Status
✅ **ACTIVE** - Used for website integration  
✅ Recommended for customer-facing quotes  
✅ Ensures pricing matches website exactly

---

## 📊 Comparison Table

| Feature | Old-Style | GOD | Shopify |
|---------|-----------|-----|---------|
| **Data Source** | SQL Server | SQL Server | Hardcoded |
| **Pricing Accuracy** | Good | **Excellent** | **Exact to website** |
| **Database Required** | Yes | Yes | No |
| **Calculation Speed** | Medium | Medium | **Fast** |
| **Options Coverage** | Limited | **Comprehensive** | Standard products |
| **Maintenance** | Deprecated | Active | Active |
| **Best For** | Legacy support | Internal quoting | Customer quotes |

---

## 🎯 Use Case Recommendations

### Use **GOD Calculators** when:
- ✅ Need most accurate pricing
- ✅ Custom specifications (non-standard sizes, special finishes)
- ✅ Internal quoting and estimating
- ✅ Database access is available
- ✅ Comprehensive options needed (folding types, special lamination, etc.)

**Example:** Sales team generating custom quotes for unique projects

---

### Use **Shopify Calculators** when:
- ✅ Matching website prices exactly
- ✅ Customer-facing quotes (must match what they see online)
- ✅ No database access
- ✅ Standard Shopify products only
- ✅ Website integration/automation

**Example:** Customer service confirming prices that match the website

---

### **Old-Style Calculators**
- ⚠️ **DEPRECATED** - Use GOD calculators instead
- ⚠️ Kept for backwards compatibility only
- ⚠️ May be removed in future versions

**Recommendation:** Migrate any code using old-style calculators to GOD equivalents

---

## 🔄 Migration Guide: Old → GOD

If you're using old-style calculators, here's how to migrate:

### Old-Style Flyers
```python
calculate_flyers(
    quantity=1000,
    width=210,
    height=297,
    stock_gsm=150,
    print_mode="double_sided"
)
```

### GOD Flyers (Recommended)
```python
calculate_flyers_god(
    quantity=1000,
    width=210,
    height=297,
    gsm=150,
    print_side1=1,  # colour
    print_side2=1   # colour (double-sided)
)
```

**Parameter Mapping:**
- `stock_gsm` → `gsm`
- `print_mode="double_sided"` → `print_side1=1, print_side2=1`
- `print_mode="single_sided"` → `print_side1=1, print_side2=0`
- `cello_type="gloss_both_sides"` → `cello_required=True, cello_side1=1, cello_side2=1`

---

## 📝 Summary

**Current Status (December 2024):**
- **35 calculator tools** in schema
- **Old-style:** 4 tools (deprecated, backwards compatibility)
- **GOD:** 4 tools (primary system, most accurate)
- **Shopify:** 5 tools (website integration, exact website pricing)
- **Other:** 22 specialized product calculators (signs, banners, etc.)

**Recommendation:**
- New code → Use **GOD calculators** for accuracy
- Customer quotes → Use **Shopify calculators** for website match
- Legacy code → Migrate from old-style to GOD when possible
