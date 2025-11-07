# Available Calculators in Tool Use Agent

**Last Updated:** October 10, 2025  
**Status:** 5 Active Calculators in Production

---

##  ACTIVE CALCULATORS (5 Product Types)

The `tool_use_agent.py` has access to **5 calculator types** via `ComprehensiveQuoteCalculator`:

### 1. **flyers** (VB.NET Algorithm - Database-Driven)

**Use for**: Flyers, leaflets, posters, flat printed items  
**Source**: `complete_calculator_implementation.py` lines 900-2200  
**Database**: SQL Server `Quote_DigitalStocks`, `Quote_DigitalClicks` pricing tables

**Parameters**:
- `quantity` (int): Number to print
- `paper_size` (str): Paper size (A4, A5, A6, DL, 90x55, etc.)
- `stock_gsm` (int): Paper weight in GSM (e.g., 150, 200, 300, 350)
- `stock_type` (str): Paper type (Gloss, Satin, Uncoated)
- `color_type` (str): Color type (4/4, 4/0, 1/1, 1/0)
- `sides` (int): 1 or 2

**Example:**
```python
calculate_quote("flyers", {
    "quantity": 1000,
    "paper_size": "A4",
    "stock_gsm": 150,
    "stock_type": "Gloss",
    "color_type": "4/4",
    "sides": 2
})
```

---

### 2. **business_cards** (Shopify Algorithm - Website Pricing)

**Use for**: Business cards only (90x55mm standard)  
**Source**: `complete_calculator_implementation.py` lines 2200-2800 → redirects to `ShopifyBusinessCardCalculator`  
**Database**: Uses HARDCODED Shopify tier pricing (NOT database)

**Parameters**:
- `quantity` (int): Number to print
- `stock_type` (str): Paper type (satin_350gsm, gloss_350gsm, uncoated_300gsm, etc.)
- `sides` (int): 1 or 2
- `print_type` (str): color or bw
- `finish_size` (str): standard (90x55) or small (90x45)
- `celloglaze` (str): none, matt, gloss, soft_touch (premium only)
- `artworks` (int): Number of artworks (1-10)

**Example:**
```python
calculate_quote("business_cards", {
    "quantity": 500,
    "stock_type": "satin_350gsm",
    "sides": 2,
    "print_type": "color",
    "finish_size": "standard",
    "celloglaze": "matt",
    "artworks": 1
})
```

**Important:** Business cards use Shopify pricing to match website. For database pricing, use flyers calculator with `paper_size="90x55"`.

---

### 3. **perfect_bound_books** (VB.NET Algorithm - Database-Driven)

**Use for**: Books with square spine, thick manuals, annual reports (40+ pages)  
**Also handles**: Wire Bound, Spiral Bound (same algorithm)  
**Source**: `complete_calculator_implementation.py` lines 2800-3800  
**Database**: SQL Server `Quote_PBBPerBookBindCost`, `Quote_ProfitMargins` tables

**Parameters**:
- `quantity` (int): Number of books
- `pages` (int): Total pages (must be divisible by 4)
- `cover_stock_gsm` (int): Cover paper weight (e.g., 300)
- `cover_stock_type` (str): Cover paper type
- `interior_stock_gsm` (int): Interior pages weight (e.g., 80, 100)
- `interior_stock_type` (str): Interior paper type
- `cover_sides` (int): 1 or 2
- `interior_sides` (int): 1 or 2
- `binding_type` (str): perfect, wire, spiral

**Example:**
```python
calculate_quote("perfect_bound_books", {
    "quantity": 100,
    "pages": 120,
    "cover_stock_gsm": 300,
    "cover_stock_type": "Gloss",
    "interior_stock_gsm": 80,
    "interior_stock_type": "Uncoated",
    "cover_sides": 2,
    "interior_sides": 2,
    "binding_type": "perfect"
})
```

---

### 4. **booklets** (VB.NET Algorithm - Database-Driven)

**Use for**: Saddle-stitched magazines, brochures, catalogs (4-60 pages)  
**Source**: `complete_calculator_implementation.py` lines 3800-4200  
**Database**: SQL Server `Quote_DigitalStocks`, `Quote_DigitalClicks` pricing tables

**Parameters**:
- `quantity` (int): Number of booklets
- `pages` (int): Total pages (must be divisible by 4)
- `cover_stock_gsm` (int): Cover paper weight
- `cover_stock_type` (str): Cover paper type
- `interior_stock_gsm` (int): Interior pages weight
- `interior_stock_type` (str): Interior paper type
- `cover_sides` (int): 1 or 2
- `interior_sides` (int): 1 or 2

**Example:**
```python
calculate_quote("booklets", {
    "quantity": 500,
    "pages": 16,
    "cover_stock_gsm": 200,
    "cover_stock_type": "Gloss",
    "interior_stock_gsm": 100,
    "interior_stock_type": "Uncoated",
    "cover_sides": 2,
    "interior_sides": 2
})
```

---

### 5. **letterheads** (VB.NET Algorithm - Database-Driven)

**Use for**: Letterheads, official stationery  
**Source**: `complete_calculator_implementation.py` lines 4200-4500  
**Database**: SQL Server `Quote_DigitalStocks`, `Quote_DigitalClicks` pricing tables

**Parameters**:
- `quantity` (int): Number to print
- `stock_gsm` (int): Paper weight (typically 80-120 GSM)
- `stock_type` (str): Paper type (usually Uncoated)
- `color_type` (str): Color type (4/0, 1/0)
- `sides` (int): 1 (letterheads are single-sided)

**Example:**
```python
calculate_quote("letterheads", {
    "quantity": 1000,
    "stock_gsm": 100,
    "stock_type": "Uncoated",
    "color_type": "4/0",
    "sides": 1
})
```

---

## ⚠️ NOT IMPLEMENTED (Exist but Not Connected)

These calculators **EXIST** in the codebase but are **NOT accessible** via tool_use_agent.py:

### GOD Calculators (Database-Driven - Orphaned)
-  `god_calculators/business_card_calculator.py` - NOT imported
-  `god_calculators/corflute_calculator.py` - NOT imported

### Shopify Calculators (Website Pricing - Not Connected)
- ⚠️ `shopify_calculators/business_card_calculator_shopify.py` - Used internally by business_cards
-  `shopify_calculators/PremiumBusinessCards_Shopify_Calculator.py` - NOT accessible
-  `shopify_calculators/EconomicalBusinessCards_Shopify_Calculator.py` - NOT accessible
-  `shopify_calculators/corflute_calculator_shopify.py` - NOT accessible
-  `shopify_calculators/WireBound_Shopify_Calculator.py` - NOT accessible
-  `shopify_calculators/SpiralBound_Shopify_Calculator.py` - NOT accessible
-  `shopify_calculators/PerfectBound_Shopify_Calculator.py` - NOT accessible

---

## 📊 CALCULATOR ARCHITECTURE

### VB.NET Algorithms (Database-Driven)
**Used for:** Production quoting with real database pricing
- **flyers** - Digital printing cost calculation
- **perfect_bound_books** - Book binding with per-book costs
- **booklets** - Saddle-stitch magazine calculation
- **letterheads** - Stationery printing

**Data Source:** SQL Server tables (`Quote_DigitalStocks`, `Quote_DigitalClicks`, `Quote_PBBPerBookBindCost`, etc.)

### Shopify Algorithms (Hardcoded Website Pricing)
**Used for:** Website price matching ONLY
- **business_cards** - Website DPO formula replication

**Data Source:** Hardcoded tier pricing tables (no database connection)

---

## 🔧 USAGE IN AI AGENT

### 1. Request Calculator Requirements
```python
get_calculator_requirements("business_cards")
# Returns: 4,600+ lines of detailed guidance
```

### 2. Calculate Quote
```python
calculate_quote("business_cards", {
    "quantity": 500,
    "stock_type": "satin_350gsm",
    "sides": 2,
    "celloglaze": "matt"
})
# Returns: QuoteResult with price, breakdown, metadata
```

---

## 📝 NOTES

1. **Business Cards Pricing:**
   - Use `business_cards` calculator for Shopify website price matching
   - Use `flyers` calculator with `paper_size="90x55"` for database pricing

2. **Book Binding:**
   - `perfect_bound_books` handles Perfect, Wire, and Spiral binding
   - Use `binding_type` parameter to specify

3. **Page Count Rules:**
   - Books/Booklets: Pages must be divisible by 4
   - Minimum 4 pages for booklets
   - Minimum 40 pages for perfect bound books

4. **GOD Calculators:**
   - Exist but not connected to AI agent
   - May be integrated in future for database-driven business cards/corflute pricing

---

## 🔗 RELATED DOCUMENTATION

- `CALCULATOR_ARCHITECTURE.md` - Detailed GOD vs Shopify architecture
- `CALCULATOR_INFORMATION_AUDIT.md` - What guidance AI receives
- `complete_calculator_implementation.py` - Main calculator implementation
- `shopify_calculators/` - Website pricing calculators
- `god_calculators/` - Database pricing calculators (orphaned)
