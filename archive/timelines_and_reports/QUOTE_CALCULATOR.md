# QUOTE_CALCULATOR - InHouse Print Quote Calculation System

**Version:** 2.0 (Consolidated & Self-Contained)  
**Status:** ✅ Production Ready - 97.5% Test Success (39/40 Tests Passing)  
**Last Updated:** January 18, 2026  
**Module Type:** External Module - Print Product Pricing

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Calculator Types](#calculator-types)
4. [Implementation Details](#implementation-details)
5. [API Reference](#api-reference)
6. [Database Schema](#database-schema)
7. [Query Library](#query-library)
8. [Testing & Validation](#testing--validation)
9. [Configuration](#configuration)
10. [Troubleshooting](#troubleshooting)
11. [Known Issues](#known-issues)
12. [Appendix](#appendix)

---

## Overview

### Purpose

The **Quote Calculator Module** is a comprehensive printing quote calculation system for InHouse Print, providing AI-accessible pricing tools for 31 different print products. The system connects to the G_Folder SQL Server database for real-time pricing data and product configurations.

### Key Capabilities

✅ **31 Shopify Calculators** - Hardcoded pricing matching website quotes  
✅ **77 QueryLibrary Queries** - Pre-built SQL queries for business intelligence  
✅ **4 Database Tools** - Direct database access for custom queries  
✅ **Type-Safe Wrappers** - Automatic parameter type conversion and validation  
✅ **AI Tool Integration** - Full Registry V3 schema definitions  
✅ **Comprehensive Testing** - 97.5% test success rate (39/40 tests)  
✅ **Dual Architecture** - Shopify (primary) + GOD (legacy, deactivated)

### Statistics

- **Total Calculator Tools:** 31 active (35 total, 4 deactivated)
- **QueryLibrary Queries:** 77 pre-built queries
- **Database Tools:** 4 (query, modify, schema guide, list queries)
- **Code Size:** 10,164 lines total
  - calculator_wrapper.py: 2,103 lines
  - query_library.py: 5,958 lines
  - Backend calculators: 2,103+ lines (31 files)
- **Test Coverage:** 40 comprehensive tests
- **Success Rate:** 97.5% (39/40 passing, Dec 14 2025)
- **Module Location:** `UI/modules_external/quote-calculator/`

### Product Categories

1. **Business Cards** (3 calculators) - Standard, economical, premium variants
2. **Flyers** (2 calculators) - Standard and folded flyers
3. **Books & Booklets** (5 calculators) - Perfect bound, wire bound, spiral, saddle stitch
4. **Letterheads** (2 calculators) - Standard and printed letterheads
5. **Signs & Displays** (10 calculators) - Corflute, election, construction, A-frames, pull-up banners
6. **Stationery** (6 calculators) - Notepads, with compliments slips, bookmarks
7. **Large Format** (3 calculators) - Posters, vinyl stickers, selfie frames

---

## Architecture

### System Overview

The quote calculator system follows a **three-layer architecture**: AI Tools → Wrapper Layer → Backend Calculators → Database.

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI AGENT REQUEST                            │
│  "Calculate quote for 500 business cards, double-sided, satin"  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    REGISTRY V3 (Tool Discovery)                  │
│  Location: tools/registry_v3.py                                 │
│  Schema: UI/modules_external/quote-calculator/schema/*.json     │
│  Total Tools: 31 calculators + 77 queries + 4 database tools    │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  WRAPPER LAYER (Type Safety)                     │
│  Location: implementations/calculator_wrapper.py (2,103 lines)  │
│  Purpose: Type conversion, parameter validation, error handling │
│  Features:                                                       │
│  - @calculator_wrapper decorator (automatic type conversion)    │
│  - Parameter enum validation (quantity: [100, 250, 500...])     │
│  - String→Integer conversion ("500" → 500)                      │
│  - Default value injection                                       │
│  - Comprehensive error messages                                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  BACKEND CALCULATORS (Pricing Logic)             │
│  Location: backend/shopify_calculators/ (31 files)              │
│  Architecture: Hardcoded pricing tables (Shopify source)        │
│  Example: EconomicalBusinessCards_Shopify_Calculator.py         │
│  Logic:                                                          │
│  1. Validate parameters (quantity, stock, sides, etc.)          │
│  2. Lookup base price in pricing table                          │
│  3. Apply finish multipliers (celloglaze, lamination)           │
│  4. Calculate setup fees                                         │
│  5. Apply quantity discounts                                     │
│  6. Return total price + breakdown                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    G_FOLDER SQL SERVER DATABASE                  │
│  Server: DESKTOP-Q2C1H93\SQL2022EXPRESS                         │
│  Database: G_Folder                                             │
│  Tables:                                                         │
│  - calculator_pricing_constants (500+ pricing rules)            │
│  - calculator_pricing_parameters (100+ variables)               │
│  - calculator_product_options (200+ product configs)            │
│  - calculator_pricing_formulas (50+ calculation formulas)       │
│  - calculator_parameter_overrides (custom pricing)              │
│  - calculator_audit_log (change tracking)                       │
│  - calculator_pricing_catalog (product catalog)                 │
│  - calculator_custom_calculators (custom calculator builder)    │
└─────────────────────────────────────────────────────────────────┘
```

### Component Relationships

```
quote-calculator/
│
├── schema/                          # AI Tool Definitions (Registry V3)
│   ├── calculator_tools.json        # 31 calculator tool schemas
│   ├── calculator_pricing_tools.json # 4 database tool schemas
│   ├── query_library_tools.json     # 2 QueryLibrary tool schemas
│   └── custom_calculator_*.json     # Custom calculator builder (separate doc)
│
├── implementations/                 # Wrapper Layer (Type Safety)
│   ├── calculator_wrapper.py        # 2,103 lines - Main wrapper
│   ├── calculator_pricing_wrapper.py # Database tool wrappers
│   ├── query_library_wrapper.py     # QueryLibrary wrappers
│   └── schema_validator.py          # @calculator_wrapper decorator
│
├── backend/                         # Core Calculators & Logic
│   ├── shopify_calculators/         # 31 Shopify calculators (PRIMARY)
│   │   ├── EconomicalBusinessCards_Shopify_Calculator.py
│   │   ├── PremiumBusinessCards_Shopify_Calculator.py
│   │   ├── FoldedFlyers_Shopify_Calculator.py
│   │   ├── PerfectBound_Shopify_Calculator.py
│   │   ├── WireBound_Shopify_Calculator.py
│   │   ├── SpiralBound_Shopify_Calculator.py
│   │   └── [25+ more calculators]
│   │
│   ├── god_calculators/             # 4 GOD calculators (DEACTIVATED Jan 13)
│   │   ├── GOD_flyer_calculator.py
│   │   ├── GOD_letterhead_calculator.py
│   │   ├── GOD_perfect_bound_books_calculator.py
│   │   └── GOD_corflute_signs_calculator.py
│   │
│   ├── query_library.py             # 5,958 lines - 77 pre-built SQL queries
│   ├── calculator_pricing_db.py     # Database connector for Supabase
│   └── parameter_translator.py      # Legacy parameter translation
│
├── config/                          # Configuration Files
│   ├── database-config.json         # Database connection settings
│   └── pricing-config.json          # Pricing rule configurations
│
├── tests/                           # Test Suite (40 tests)
│   ├── test_comprehensive.py        # Main test suite
│   ├── test_all_calculators.py      # All 31 calculator tests
│   ├── test_calculator_queries.py   # QueryLibrary tests (14/14 passing)
│   ├── test_wrapper_integration.py  # Wrapper integration tests
│   └── test_registry_tools.py       # Registry V3 discovery tests
│
├── DOCUMENTATION/                   # Reference Documentation
│   ├── QUERY_LIBRARY_COMPLETE_INVENTORY.md
│   ├── SQL_PATTERNS_ANALYSIS.md
│   └── README.md
│
└── README.md                        # Module overview (703 lines)
```

### External Dependencies

**Database Connector (Sibling Module):**
```
AI_agents/UI/modules_external/
├── quote-calculator/                # This module
└── inhouse-print/                   # Database connector module
    └── db_connector.py              # Shared SQL Server connector
                                     # Used by GOD calculators (deactivated)
```

**Python Dependencies:**
- `pandas` - Data manipulation for QueryLibrary results
- `numpy` - Numerical operations
- `decimal.Decimal` - Precise financial calculations
- `asteval` - Safe formula evaluation (custom calculator builder)
- `AI_infrastructure.shared.database_utils` - Supabase PostgreSQL connector

### Data Flow Example

**Example Request:** "Calculate quote for 500 business cards, double-sided, satin finish"

```python
# 1. AI Agent calls tool via Registry V3
result = calculate_business_cards(
    quantity="500",              # Note: String input (AI provides strings)
    stock_type="satin",
    print_type="double_sided",
    celloglaze="none"
)

# 2. Wrapper Layer (calculator_wrapper.py)
@calculator_wrapper(quantity_enum=[100, 250, 500, 1000, 2000, 5000, 10000])
def calculate_business_cards(quantity: int, stock_type: str, print_type: str, ...):
    # Decorator automatically converts:
    # "500" (string) → 500 (integer)
    # Validates: 500 is in enum [100, 250, 500, ...]
    
    # Route to appropriate calculator
    if stock_type == "satin":
        calculator = EconomicalBusinessCardsShopifyCalculator()
    
    # Convert parameters to Shopify format
    print_sides = "Double side print" if print_type == "double_sided" else "Single side print"
    
    # Call backend calculator
    price = calculator.calculate(
        quantity=500,
        print_sides="Double side print",
        celloglaze="No Celloglaze"
    )
    
    return {
        "success": True,
        "total_price": 125.45,
        "per_unit_price": 0.25,
        "quantity": 500,
        "stock": "350GSM Satin",
        "turnaround_days": 3
    }

# 3. Backend Calculator (EconomicalBusinessCards_Shopify_Calculator.py)
def calculate(self, quantity, print_sides, celloglaze):
    # Step 1: Lookup base price from hardcoded pricing table
    base_price = self.pricing_table[quantity][print_sides]  # e.g., 95.00
    
    # Step 2: Apply celloglaze multiplier (if applicable)
    if celloglaze != "No Celloglaze":
        base_price *= self.celloglaze_multipliers[celloglaze]  # e.g., 1.15
    
    # Step 3: Add setup fee
    setup_fee = 15.00
    total = base_price + setup_fee
    
    # Step 4: Calculate per-unit price
    per_unit = total / quantity
    
    return {
        "total_price": total,
        "per_unit_price": per_unit,
        "breakdown": {
            "base_price": base_price,
            "setup_fee": setup_fee,
            "celloglaze": celloglaze
        }
    }

# 4. Return to AI Agent
# {
#     "success": True,
#     "total_price": 125.45,
#     "per_unit_price": 0.25,
#     "quantity": 500,
#     "stock": "350GSM Satin",
#     "turnaround_days": 3
# }
```

---

## Calculator Types

### Category 1: Business Cards (3 Calculators)

#### 1. `calculate_business_cards` - Standard Business Cards

**Status:** ✅ Active  
**Backend:** Routes to Economical or Premium based on `stock_type`  
**Parameters:**
- `quantity` (int, required) - Number of cards: [100, 250, 500, 1000, 2000, 5000, 10000]
- `stock_type` (string, required) - Stock material: `"standard"`, `"premium"`, `"satin"`, `"uncoated"`
- `print_type` (string, required) - Sides: `"single_sided"` or `"double_sided"`
- `finish_size` (string, optional) - Card size: `"90x55mm"` (default), `"90x50mm"`, `"85x55mm"`
- `celloglaze` (string, optional) - Finish: `"none"` (default), `"gloss"`, `"matt"`, `"1_side_gloss"`, `"2_side_gloss"`, `"1_side_matt"`, `"2_side_matt"`

**Returns:**
```json
{
    "success": true,
    "total_price": 125.45,
    "per_unit_price": 0.25,
    "quantity": 500,
    "stock": "350GSM Satin",
    "sides": "Double Sided",
    "celloglaze": "None",
    "finish_size": "90x55mm",
    "turnaround_days": 3,
    "breakdown": {
        "base_price": 110.45,
        "setup_fee": 15.00,
        "celloglaze_cost": 0.00
    }
}
```

**Example Usage:**
```python
# AI agent call
result = calculate_business_cards(
    quantity=500,
    stock_type="satin",
    print_type="double_sided",
    celloglaze="2_side_matt"
)

# Response: $125.45 total, $0.25 per card
```

---

#### 2. `calculate_economical_business_cards_shopify` - Budget Business Cards

**Status:** ✅ Active  
**Backend:** `EconomicalBusinessCards_Shopify_Calculator.py`  
**Stock:** 300GSM Satin (hardcoded, cannot be changed)  
**Size:** 90x55mm (hardcoded)  
**Parameters:**
- `quantity` (int, required) - Number of cards: [250, 500, 1000, 2000, 5000, 10000]
- `print_sides` (string, required) - `"Single side print"` or `"Double side print"`
- `celloglaze` (string, optional) - `"No Celloglaze"` (default), `"1 Side Gloss"`, `"1 Side Matt"`, `"2 Side Gloss"`, `"2 Side Matt"`

**Pricing Table (Hardcoded):**
```python
# Single Side Print
250:  $82.00
500:  $95.00
1000: $115.00
2000: $145.00
5000: $345.00
10000: $665.00

# Double Side Print
250:  $90.00
500:  $110.00
1000: $145.00
2000: $195.00
5000: $445.00
10000: $865.00

# Celloglaze Multipliers
1 Side Gloss/Matt: 1.15x base price
2 Side Gloss/Matt: 1.25x base price
```

---

#### 3. `calculate_premium_business_cards_shopify` - Premium Business Cards

**Status:** ✅ Active  
**Backend:** `PremiumBusinessCards_Shopify_Calculator.py`  
**Stock:** 400GSM Uncoated (hardcoded)  
**Size:** 90x55mm (hardcoded)  
**Parameters:**
- `quantity` (int, required) - Number of cards: [250, 500, 1000, 2000, 5000, 10000]
- `print_sides` (string, required) - `"Single side print"` or `"Double side print"`
- `celloglaze` (string, optional) - `"No Celloglaze"` (default), `"1 Side Gloss"`, `"1 Side Matt"`, `"2 Side Gloss"`, `"2 Side Matt"`

**Pricing Table (Hardcoded):**
```python
# Single Side Print
250:  $95.00
500:  $115.00
1000: $145.00
2000: $195.00
5000: $445.00
10000: $865.00

# Double Side Print
250:  $110.00
500:  $145.00
1000: $195.00
2000: $275.00
5000: $645.00
10000: $1265.00

# Celloglaze Multipliers (same as Economical)
1 Side Gloss/Matt: 1.15x base price
2 Side Gloss/Matt: 1.25x base price
```

---

### Category 2: Flyers (2 Calculators)

#### 4. `calculate_flyers` - Standard Flyers

**Status:** ✅ Active  
**Backend:** Routes to `FoldedFlyers_Shopify_Calculator.py` (if folded) or hardcoded pricing  
**Parameters:**
- `quantity` (int, required) - Number of flyers: [100, 250, 500, 1000, 2000, 5000, 10000]
- `size` (string, required) - Paper size: `"A4"`, `"A5"`, `"A6"`, `"DL"`
- `stock` (string, required) - Paper stock: `"150gsm_gloss"`, `"150gsm_silk"`, `"170gsm_silk"`, `"250gsm_silk"`
- `sides` (string, required) - Print sides: `"single_sided"` or `"double_sided"`
- `folding` (string, optional) - Fold type: `"none"` (default), `"half_fold"`, `"tri_fold"`, `"gate_fold"`, `"z_fold"`

**Returns:**
```json
{
    "success": true,
    "total_price": 85.50,
    "per_unit_price": 0.17,
    "quantity": 500,
    "size": "A5",
    "stock": "150gsm Gloss",
    "sides": "Double Sided",
    "folding": "None",
    "turnaround_days": 2
}
```

---

#### 5. `calculate_folded_flyers_shopify` - Folded Flyers (Shopify)

**Status:** ✅ Active  
**Backend:** `FoldedFlyers_Shopify_Calculator.py`  
**Parameters:**
- `quantity` (int, required) - Number of flyers: [100, 250, 500, 1000, 2000, 5000, 10000]
- `size` (string, required) - `"A4"`, `"A5"`, `"A6"`, `"DL"`
- `fold_type` (string, required) - `"Half Fold"`, `"Tri Fold"`, `"Gate Fold"`, `"Z Fold"`
- `print_sides` (string, optional) - `"Single sided"` (default) or `"Double sided"`

**Pricing Logic:**
1. Lookup base price from `pricing_table[quantity][size][fold_type]`
2. Apply double-sided multiplier if needed (1.5x base price)
3. Add setup fee ($15-25 depending on fold complexity)
4. Return total

---

### Category 3: Books & Booklets (5 Calculators)

#### 6. `calculate_booklets` - Saddle Stitch Booklets

**Status:** ✅ Active  
**Backend:** `SaddleStitchBooks_Shopify_Calculator.py`  
**Binding:** Saddle stitch (stapled spine)  
**Parameters:**
- `quantity` (int, required) - Number of booklets: [25, 50, 100, 250, 500, 1000]
- `pages` (int, required) - Total pages (must be multiple of 4): [8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64]
- `size` (string, required) - Finished size: `"A4"`, `"A5"`, `"A6"`
- `cover_stock` (string, optional) - Cover paper: `"200gsm_silk"` (default), `"250gsm_silk"`, `"300gsm_silk"`
- `inner_stock` (string, optional) - Inner pages: `"100gsm_silk"` (default), `"120gsm_silk"`, `"150gsm_silk"`

**Returns:**
```json
{
    "success": true,
    "total_price": 245.00,
    "per_unit_price": 4.90,
    "quantity": 50,
    "pages": 24,
    "size": "A5",
    "cover_stock": "250gsm Silk",
    "inner_stock": "120gsm Silk",
    "binding": "Saddle Stitch",
    "turnaround_days": 5
}
```

---

#### 7. `calculate_perfect_bound_books` - Perfect Bound Books

**Status:** ✅ Active  
**Backend:** `PerfectBound_Shopify_Calculator.py`  
**Binding:** Perfect bound (glued spine, square back)  
**Parameters:**
- `quantity` (int, required) - Number of books: [25, 50, 100, 250, 500, 1000]
- `pages` (int, required) - Total pages (minimum 40): [40, 44, 48, ..., 300, 350, 400]
- `size` (string, required) - Finished size: `"A4"`, `"A5"`
- `cover_stock` (string, optional) - Cover: `"300gsm_silk"` (default), `"350gsm_silk"`
- `inner_stock` (string, optional) - Inner: `"100gsm_silk"` (default), `"120gsm_silk"`, `"150gsm_silk"`

**Pricing Formula:**
```python
base_price = (pages / 4) * page_rate[quantity]
cover_surcharge = cover_stock_surcharge[cover_stock]
binding_fee = perfect_bound_setup_fee[quantity]

total = base_price + cover_surcharge + binding_fee
```

---

#### 8. `calculate_wire_bound_books_shopify` - Wire Bound Books

**Status:** ✅ Active  
**Backend:** `WireBound_Shopify_Calculator.py`  
**Binding:** Wire-o binding (double loop wire spine)  
**Parameters:**
- `quantity` (int, required) - Number of books: [25, 50, 100, 250, 500, 1000]
- `pages` (int, required) - Total pages: [20, 24, 28, ..., 200]
- `size` (string, required) - `"A4"`, `"A5"`, `"A6"`
- `cover` (string, optional) - `"Clear PVC Front Cover"` (default), `"Full Color Cover"`
- `inner_stock` (string, optional) - `"100gsm_silk"` (default), `"120gsm_silk"`

---

#### 9. `calculate_spiral_bound_books_shopify` - Spiral Bound Books

**Status:** ✅ Active  
**Backend:** `SpiralBound_Shopify_Calculator.py`  
**Binding:** Spiral coil binding  
**Parameters:** Same as wire bound (quantity, pages, size, cover, inner_stock)

---

#### 10. `calculate_saddle_stitch_books` - Saddle Stitch Books

**Status:** ✅ Active (Alias for `calculate_booklets`)  
**Backend:** Same as booklets calculator  
**Note:** Provided for clarity in tool names

---

### Category 4: Letterheads (2 Calculators)

#### 11. `calculate_letterheads` - Standard Letterheads

**Status:** ✅ Active  
**Backend:** `PrintedLetterheads_Shopify_Calculator.py`  
**Parameters:**
- `quantity` (int, required) - Number of letterheads: [100, 250, 500, 1000, 2500, 5000]
- `stock` (string, required) - Paper stock: `"100gsm_laser"`, `"120gsm_laser"`, `"150gsm_laser"`
- `colors` (string, required) - Color printing: `"full_color"`, `"black_only"`

**Pricing Table:**
```python
# 100gsm Laser, Full Color
100:  $65.00
250:  $85.00
500:  $125.00
1000: $215.00
2500: $495.00
5000: $945.00

# Black only: -20% discount
```

---

#### 12. `calculate_printed_letterheads` - Printed Letterheads (Shopify)

**Status:** ✅ Active (Alias for standard letterheads)  
**Backend:** Same as `calculate_letterheads`

---

### Category 5: Signs & Displays (10 Calculators)

#### 13. `calculate_corflute_signs` - Corflute Signs

**Status:** ✅ Active  
**Backend:** `corflute_calculator_shopify.py`  
**Material:** Corflute (corrugated plastic)  
**Parameters:**
- `quantity` (int, required) - Number of signs: [1, 5, 10, 25, 50, 100]
- `width` (float, required) - Width in mm: [300, 600, 900, 1200, 1800, 2400]
- `height` (float, required) - Height in mm: [300, 600, 900, 1200, 1800]
- `thickness` (string, required) - Material thickness: `"3mm"`, `"5mm"`
- `sides` (string, required) - Print sides: `"single_sided"` or `"double_sided"`

**Pricing Formula:**
```python
area_sqm = (width / 1000) * (height / 1000)
base_price = area_sqm * rate_per_sqm[thickness]

if sides == "double_sided":
    base_price *= 1.6  # 60% surcharge

setup_fee = 25.00
total = (base_price * quantity) + setup_fee
```

---

#### 14. `calculate_corflute_signs_shopify` - Corflute Signs (Shopify)

**Status:** ✅ Active  
**Backend:** `CorfluteInsertA_Frame_Shopify_Calculator.py`  
**Note:** Alias for standard corflute calculator

---

#### 15. `calculate_bollard_signs` - Bollard Signs

**Status:** ✅ Active (Stub Implementation)  
**Backend:** Hardcoded return value  
**Material:** Corflute for bollard wraps  
**Returns:** Fixed quote ($45.00 per sign, minimum 5 signs)

---

#### 16. `calculate_construction_signs` - Construction Signs

**Status:** ✅ Active (Stub Implementation)  
**Backend:** Hardcoded return value  
**Material:** Heavy-duty corflute  
**Returns:** Fixed quote ($125.00 per sign, minimum 2 signs)

---

#### 17. `calculate_election_signs` - Election Campaign Signs

**Status:** ✅ Active  
**Backend:** `ElectionSigns_Shopify_Calculator.py`  
**Material:** 5mm corflute  
**Parameters:**
- `quantity` (int, required) - Number of signs: [10, 25, 50, 100, 250, 500]
- `size` (string, required) - Standard sizes: `"600x900mm"`, `"900x1200mm"`, `"1200x1800mm"`

**Pricing:**
```python
# 600x900mm
10:  $295.00
25:  $545.00
50:  $895.00
100: $1595.00

# Larger sizes: +30% (900x1200mm), +60% (1200x1800mm)
```

---

#### 18. `calculate_corflute_insert_a_frame` - A-Frame Insert Signs

**Status:** ✅ Active  
**Backend:** `CorfluteInsertA_Frame_Shopify_Calculator.py`  
**Purpose:** Corflute inserts for A-frame stands

---

#### 19. `calculate_metal_face_a_frame` - Metal Face A-Frame

**Status:** ✅ Active (Stub Implementation)  
**Backend:** Hardcoded return value  
**Returns:** Fixed quote ($245.00 per frame)

---

#### 20. `calculate_luxury_classic_pull_up_banners` - Pull-Up Banners

**Status:** ✅ Active  
**Backend:** `LuxuryClassicPullUpBanners_Shopify_Calculator.py`  
**Parameters:**
- `quantity` (int, required) - Number of banners: [1, 2, 3, 5, 10]
- `size` (string, required) - Banner size: `"850x2000mm"`, `"1000x2000mm"`, `"1200x2000mm"`

**Pricing:**
```python
# 850x2000mm
1:  $145.00
2:  $275.00
3:  $395.00
5:  $645.00
10: $1245.00

# Larger sizes: +15% (1000mm), +30% (1200mm)
```

---

#### 21. `calculate_selfie_frames` - Large Selfie Frames

**Status:** ✅ Active  
**Backend:** `SelfieFrames_Shopify_Calculator.py`  
**Material:** 5mm corflute with custom cutout

---

#### 22. `calculate_stackable_cubes` - Display Cubes

**Status:** ✅ Active  
**Backend:** `StackableCubes_Shopify_Calculator.py`  
**Material:** Printed corflute cubes

---

### Category 6: Stationery (6 Calculators)

#### 23. `calculate_premium_bookmarks` - Premium Bookmarks

**Status:** ✅ Active  
**Backend:** `PremiumBookmarks_Shopify_Calculator.py`  
**Parameters:**
- `quantity` (int, required) - Number of bookmarks: [100, 250, 500, 1000, 2500, 5000]
- `size` (string, optional) - `"50x200mm"` (default) or `"60x200mm"`
- `stock` (string, optional) - `"350gsm_silk"` (default)
- `lamination` (string, optional) - `"Gloss Lamination"`, `"Matt Lamination"`, `"None"`

---

#### 24. `calculate_with_compliments_slips` - With Compliments Slips

**Status:** ✅ Active  
**Backend:** `WithComplimentsSlips_Shopify_Calculator.py`  
**Parameters:**
- `quantity` (int, required) - Number of slips: [100, 250, 500, 1000, 2500]
- `size` (string, optional) - `"99x210mm"` (DL, default)
- `stock` (string, optional) - `"150gsm_silk"` (default)

---

#### 25-27. `calculate_notepads_a4/a5/a6` - Notepads

**Status:** ✅ Active  
**Backend:** `NotepadsA4_Shopify_Calculator.py` (+ A5, A6 variants)  
**Parameters:**
- `quantity` (int, required) - Number of pads: [5, 10, 25, 50, 100]
- `sheets_per_pad` (int, required) - Sheets per pad: [25, 50, 100]
- `backing` (string, optional) - `"Chipboard Backing"` (default) or `"None"`

**Pricing:**
```python
# A4, 50 sheets per pad
5:   $45.00
10:  $75.00
25:  $165.00
50:  $295.00
100: $545.00

# A5: -25%, A6: -40% from A4 prices
```

---

### Category 7: Large Format (3 Calculators)

#### 28. `calculate_custom_poster_printing` - Custom Posters

**Status:** ✅ Active  
**Backend:** `CustomPosterPrinting_Shopify_Calculator.py`  
**Parameters:**
- `quantity` (int, required) - Number of posters: [1, 5, 10, 25, 50, 100]
- `size` (string, required) - Poster size: `"A3"`, `"A2"`, `"A1"`, `"A0"`
- `stock` (string, optional) - `"200gsm_silk"` (default), `"250gsm_silk"`

---

#### 29. `calculate_custom_vinyl_stickers` - Vinyl Stickers

**Status:** ✅ Active  
**Backend:** `CustomVinylStickers_Shopify_Calculator.py`  
**Parameters:**
- `quantity` (int, required) - Number of stickers: [50, 100, 250, 500, 1000]
- `size` (string, required) - Sticker size: `"50x50mm"`, `"75x75mm"`, `"100x100mm"`, `"Custom"`
- `finish` (string, optional) - `"Gloss"` (default), `"Matt"`
- `cut_type` (string, optional) - `"Square Cut"` (default), `"Die Cut"`

---

#### 30-31. `calculate_strut_cards_a3/a4` - Strut Cards

**Status:** ✅ Active  
**Backend:** `StrutCardsA3_Shopify_Calculator.py` (+ A4 variant)  
**Parameters:**
- `quantity` (int, required) - Number of cards: [10, 25, 50, 100, 250]
- `stock` (string, optional) - `"400gsm_silk"` (default)

---

### Deactivated Calculators (4 - GOD Variants)

**Status:** ❌ Deactivated (January 13, 2026)  
**Reason:** Database-driven GOD calculators bypassed in favor of Shopify hardcoded calculators

#### 32. `calculate_flyers_god` - GOD Flyers Calculator
**Backend:** `GOD_flyer_calculator.py`  
**Deactivation:** Line 50-59 in calculator_wrapper.py commented out

#### 33. `calculate_letterheads_god` - GOD Letterheads Calculator
**Backend:** `GOD_letterhead_calculator.py`

#### 34. `calculate_perfect_bound_books_god` - GOD Perfect Bound Calculator
**Backend:** `GOD_perfect_bound_books_calculator.py`

#### 35. `calculate_corflute_signs_god` - GOD Corflute Calculator
**Backend:** `GOD_corflute_signs_calculator.py`

**Note:** GOD calculators are still present in codebase but imports are commented out. Can be re-enabled if needed for future database-driven pricing.

---

## Implementation Details

### File Structure

```
UI/modules_external/quote-calculator/
├── manifest.json                    # Module manifest (244 lines)
├── quote-calculator.js              # Frontend JavaScript
├── quote-calculator.css             # Frontend styles
├── quote-calculator.html            # Frontend HTML
├── README.md                        # Module documentation (703 lines)
│
├── schema/                          # AI Tool Definitions (Registry V3)
│   ├── calculator_tools.json        # 31 calculator schemas
│   ├── calculator_pricing_tools.json # 4 database tool schemas
│   ├── query_library_tools.json     # 2 QueryLibrary tool schemas
│   ├── calculator_pricing_guide.json # Schema guide tool
│   └── custom_calculator_*.json     # Custom calculator builder (separate doc)
│
├── implementations/                 # Wrapper Layer (2,103 lines total)
│   ├── calculator_wrapper.py        # Main wrapper (2,103 lines)
│   ├── calculator_pricing_wrapper.py # Database wrappers
│   ├── query_library_wrapper.py     # QueryLibrary wrappers
│   ├── schema_validator.py          # @calculator_wrapper decorator
│   └── test_wrapper_integration.py  # Wrapper tests
│
├── backend/                         # Core Calculators & Logic
│   ├── shopify_calculators/         # 31 files (PRIMARY SYSTEM)
│   │   ├── EconomicalBusinessCards_Shopify_Calculator.py
│   │   ├── PremiumBusinessCards_Shopify_Calculator.py
│   │   ├── FoldedFlyers_Shopify_Calculator.py
│   │   └── [28+ more calculator files]
│   │
│   ├── god_calculators/             # 4 files (DEACTIVATED)
│   │   ├── GOD_flyer_calculator.py
│   │   └── [3 more GOD calculators]
│   │
│   ├── query_library.py             # 5,958 lines - 77 SQL queries
│   ├── calculator_pricing_db.py     # Supabase connector
│   ├── parameter_translator.py      # Legacy translator
│   └── universal_calculator_executor.py # Universal executor
│
├── config/                          # Configuration
│   ├── database-config.json         # DB connection settings
│   └── pricing-config.json          # Pricing rules
│
├── tests/                           # Test Suite (40 tests)
│   ├── test_comprehensive.py        # Main test suite
│   ├── test_all_calculators.py      # All calculator tests
│   ├── test_calculator_queries.py   # QueryLibrary tests (14/14 ✅)
│   ├── test_wrapper_integration.py  # Wrapper integration (all ✅)
│   └── test_registry_tools.py       # Registry V3 discovery (4/4 ✅)
│
├── DOCUMENTATION/                   # Reference Docs
│   ├── README.md                    # CLI tools guide
│   ├── QUERY_LIBRARY_COMPLETE_INVENTORY.md
│   └── SQL_PATTERNS_ANALYSIS.md
│
└── ARCHIVE_CONSOLIDATED/            # Archived files
```

---

### Key Components

#### Component 1: Type-Safe Wrapper Decorator

**File:** `implementations/schema_validator.py`  
**Purpose:** Automatic parameter type conversion and validation

**Code Example:**
```python
def calculator_wrapper(quantity_enum=None, **decorator_kwargs):
    """
    Decorator that enforces type safety for calculator parameters.
    Automatically converts string inputs to correct types (int, float, etc.)
    
    Args:
        quantity_enum: List of valid quantity values (e.g., [100, 250, 500, 1000])
        **decorator_kwargs: Additional validation rules
    
    Features:
        - Converts "500" (string) → 500 (integer)
        - Validates quantity is in enum list
        - Injects default values for optional parameters
        - Provides clear error messages on validation failure
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract parameter types from function signature
            sig = inspect.signature(func)
            
            # Convert kwargs to correct types
            for param_name, param in sig.parameters.items():
                if param_name in kwargs:
                    value = kwargs[param_name]
                    expected_type = param.annotation
                    
                    # Type conversion
                    if expected_type == int and isinstance(value, str):
                        try:
                            kwargs[param_name] = int(value)
                        except ValueError:
                            raise TypeError(f"Parameter '{param_name}' must be integer, got '{value}'")
                    
                    elif expected_type == float and isinstance(value, (str, int)):
                        kwargs[param_name] = float(value)
            
            # Validate quantity enum
            if quantity_enum and 'quantity' in kwargs:
                quantity = kwargs['quantity']
                if quantity not in quantity_enum:
                    raise ValueError(
                        f"Invalid quantity: {quantity}. "
                        f"Must be one of {quantity_enum}"
                    )
            
            # Call wrapped function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Usage Example
@calculator_wrapper(quantity_enum=[100, 250, 500, 1000, 2000, 5000, 10000])
def calculate_business_cards(
    quantity: int,
    stock_type: str,
    print_type: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate business card quote.
    
    TYPE SAFE: @calculator_wrapper ensures:
    - "500" (string) → 500 (integer) automatic conversion
    - quantity validated against enum [100, 250, 500, ...]
    - Clear error if quantity=375 (not in enum)
    """
    # At this point, quantity is guaranteed to be int and in enum
    # No need for manual validation or conversion
    
    if stock_type == "satin":
        calculator = EconomicalBusinessCardsShopifyCalculator()
    
    return calculator.calculate(quantity=quantity, ...)
```

---

#### Component 2: Shopify Calculator Pattern

**File:** `backend/shopify_calculators/EconomicalBusinessCards_Shopify_Calculator.py`  
**Purpose:** Hardcoded pricing tables matching Shopify website

**Architecture:**
```python
class EconomicalBusinessCardsShopifyCalculator:
    """
    Economical Business Cards (300GSM Satin, 90x55mm)
    
    Pricing matches Shopify product:
    https://example.com/products/economical-business-cards
    
    Last updated: December 14, 2025
    """
    
    def __init__(self):
        """Initialize pricing tables"""
        
        # Hardcoded pricing table (source: Shopify product page)
        self.pricing_table = {
            # quantity: {"Single side print": price, "Double side print": price}
            250: {
                "Single side print": 82.00,
                "Double side print": 90.00
            },
            500: {
                "Single side print": 95.00,
                "Double side print": 110.00
            },
            1000: {
                "Single side print": 115.00,
                "Double side print": 145.00
            },
            2000: {
                "Single side print": 145.00,
                "Double side print": 195.00
            },
            5000: {
                "Single side print": 345.00,
                "Double side print": 445.00
            },
            10000: {
                "Single side print": 665.00,
                "Double side print": 865.00
            }
        }
        
        # Celloglaze finish multipliers
        self.celloglaze_multipliers = {
            "No Celloglaze": 1.0,
            "1 Side Gloss": 1.15,
            "1 Side Matt": 1.15,
            "2 Side Gloss": 1.25,
            "2 Side Matt": 1.25
        }
        
        # Product specifications
        self.stock = "300GSM Satin"
        self.size = "90mm x 55mm"
        self.turnaround_days = 3
    
    def calculate(self, quantity, print_sides, celloglaze="No Celloglaze"):
        """
        Calculate quote for economical business cards.
        
        Args:
            quantity (int): Number of cards (must be in pricing_table keys)
            print_sides (str): "Single side print" or "Double side print"
            celloglaze (str): Finish option (default: "No Celloglaze")
        
        Returns:
            dict: {
                "total_price": float,
                "per_unit_price": float,
                "quantity": int,
                "stock": str,
                "sides": str,
                "celloglaze": str,
                "size": str,
                "turnaround_days": int,
                "breakdown": dict
            }
        
        Raises:
            ValueError: If quantity not in pricing table
            ValueError: If print_sides not valid
        """
        
        # Validate quantity
        if quantity not in self.pricing_table:
            raise ValueError(
                f"Invalid quantity: {quantity}. "
                f"Available: {list(self.pricing_table.keys())}"
            )
        
        # Validate print sides
        if print_sides not in ["Single side print", "Double side print"]:
            raise ValueError(
                f"Invalid print_sides: {print_sides}. "
                f"Must be 'Single side print' or 'Double side print'"
            )
        
        # Step 1: Lookup base price
        base_price = self.pricing_table[quantity][print_sides]
        
        # Step 2: Apply celloglaze multiplier
        celloglaze_multiplier = self.celloglaze_multipliers.get(celloglaze, 1.0)
        final_price = base_price * celloglaze_multiplier
        
        # Step 3: Calculate per-unit price
        per_unit_price = final_price / quantity
        
        # Step 4: Build result
        return {
            "total_price": round(final_price, 2),
            "per_unit_price": round(per_unit_price, 4),
            "quantity": quantity,
            "stock": self.stock,
            "sides": print_sides,
            "celloglaze": celloglaze,
            "size": self.size,
            "turnaround_days": self.turnaround_days,
            "breakdown": {
                "base_price": base_price,
                "celloglaze_multiplier": celloglaze_multiplier,
                "celloglaze_cost": final_price - base_price
            }
        }
```

---

#### Component 3: Registry V3 Tool Schema

**File:** `schema/calculator_tools.json`  
**Purpose:** AI tool definitions for Registry V3 auto-discovery

**Schema Example:**
```json
{
    "name": "calculate_business_cards",
    "description": "Calculate quote for business cards with flexible stock and finish options. Automatically routes to economical (300GSM Satin) or premium (400GSM Uncoated) calculator based on stock_type parameter. Supports single or double-sided printing with optional celloglaze finishes.",
    "module": "quote-calculator",
    "platform": "quote_calculator",
    "parameters": {
        "type": "object",
        "properties": {
            "quantity": {
                "type": "integer",
                "description": "Number of business cards to print",
                "enum": [100, 250, 500, 1000, 2000, 5000, 10000],
                "required": true
            },
            "stock_type": {
                "type": "string",
                "description": "Stock material type",
                "enum": ["standard", "premium", "satin", "uncoated"],
                "default": "satin",
                "required": true
            },
            "print_type": {
                "type": "string",
                "description": "Single or double-sided printing",
                "enum": ["single_sided", "double_sided"],
                "required": true
            },
            "finish_size": {
                "type": "string",
                "description": "Finished card size",
                "enum": ["90x55mm", "90x50mm", "85x55mm"],
                "default": "90x55mm"
            },
            "celloglaze": {
                "type": "string",
                "description": "Celloglaze finish option",
                "enum": [
                    "none",
                    "gloss",
                    "matt",
                    "1_side_gloss",
                    "2_side_gloss",
                    "1_side_matt",
                    "2_side_matt"
                ],
                "default": "none"
            }
        },
        "required": ["quantity", "stock_type", "print_type"]
    },
    "returns": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "total_price": {"type": "number"},
            "per_unit_price": {"type": "number"},
            "quantity": {"type": "integer"},
            "stock": {"type": "string"},
            "sides": {"type": "string"},
            "celloglaze": {"type": "string"},
            "finish_size": {"type": "string"},
            "turnaround_days": {"type": "integer"},
            "breakdown": {
                "type": "object",
                "properties": {
                    "base_price": {"type": "number"},
                    "setup_fee": {"type": "number"},
                    "celloglaze_cost": {"type": "number"}
                }
            }
        }
    },
    "examples": [
        {
            "description": "500 business cards, double-sided, satin stock with matt celloglaze",
            "input": {
                "quantity": 500,
                "stock_type": "satin",
                "print_type": "double_sided",
                "celloglaze": "2_side_matt"
            },
            "output": {
                "success": true,
                "total_price": 137.50,
                "per_unit_price": 0.275,
                "quantity": 500,
                "stock": "350GSM Satin",
                "turnaround_days": 3
            }
        }
    ],
    "implementation": {
        "module_path": "UI.modules_external.quote-calculator.implementations.calculator_wrapper",
        "function_name": "calculate_business_cards",
        "type": "direct_import"
    }
}
```

---

## API Reference

### Calculator Tool APIs

**Base URL:** N/A (Direct Python function calls via Registry V3)  
**Authentication:** Not required (internal system)

---

### Tool 1: calculate_business_cards

**Purpose:** Calculate quote for business cards with flexible stock and finish options

**Function Signature:**
```python
def calculate_business_cards(
    quantity: int,
    stock_type: str,
    print_type: str,
    finish_size: str = "90x55mm",
    celloglaze: str = "none",
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
| Parameter | Type | Required | Valid Values | Default | Description |
|-----------|------|----------|--------------|---------|-------------|
| `quantity` | int | ✅ Yes | [100, 250, 500, 1000, 2000, 5000, 10000] | - | Number of cards |
| `stock_type` | string | ✅ Yes | `"standard"`, `"premium"`, `"satin"`, `"uncoated"` | - | Stock material |
| `print_type` | string | ✅ Yes | `"single_sided"`, `"double_sided"` | - | Printing sides |
| `finish_size` | string | ❌ No | `"90x55mm"`, `"90x50mm"`, `"85x55mm"` | `"90x55mm"` | Card dimensions |
| `celloglaze` | string | ❌ No | `"none"`, `"gloss"`, `"matt"`, `"1_side_gloss"`, `"2_side_gloss"`, `"1_side_matt"`, `"2_side_matt"` | `"none"` | Finish |

**Returns:**
```python
{
    "success": True,
    "total_price": 125.45,
    "per_unit_price": 0.25,
    "quantity": 500,
    "stock": "350GSM Satin",
    "sides": "Double Sided",
    "celloglaze": "None",
    "finish_size": "90x55mm",
    "turnaround_days": 3,
    "breakdown": {
        "base_price": 110.45,
        "setup_fee": 15.00,
        "celloglaze_cost": 0.00
    }
}
```

**Error Response:**
```python
{
    "success": False,
    "error": "Failed to calculate business_cards quote",
    "message": "Invalid quantity: 375. Must be one of [100, 250, 500, 1000, 2000, 5000, 10000]",
    "details": "Check parameters and database connection"
}
```

**Example Usage:**
```python
# Python call
result = calculate_business_cards(
    quantity=500,
    stock_type="satin",
    print_type="double_sided",
    celloglaze="2_side_matt"
)

# AI agent call (natural language → Registry V3)
"Calculate a quote for 500 business cards, double-sided, satin finish with matte celloglaze"

# Registry V3 translates to:
calculate_business_cards(
    quantity=500,  # Note: AI provides string "500", wrapper converts to int
    stock_type="satin",
    print_type="double_sided",
    celloglaze="2_side_matt"
)
```

---

### Tool 2-31: All Calculator Tools

**Complete Tool List:**

| # | Tool Name | Product Type | Status | Stock Options | Quantity Range |
|---|-----------|--------------|--------|---------------|----------------|
| 1 | calculate_business_cards | Business Cards (Standard) | ✅ Active | 4 options | 100-10000 |
| 2 | calculate_economical_business_cards_shopify | Business Cards (Economy) | ✅ Active | 300GSM Satin (fixed) | 250-10000 |
| 3 | calculate_premium_business_cards_shopify | Business Cards (Premium) | ✅ Active | 400GSM Uncoated (fixed) | 250-10000 |
| 4 | calculate_flyers | Flyers (Standard) | ✅ Active | 4 stock options | 100-10000 |
| 5 | calculate_folded_flyers_shopify | Folded Flyers | ✅ Active | 4 sizes, 4 fold types | 100-10000 |
| 6 | calculate_booklets | Saddle Stitch Booklets | ✅ Active | Multiple stocks | 25-1000 |
| 7 | calculate_perfect_bound_books | Perfect Bound Books | ✅ Active | Multiple stocks | 25-1000 |
| 8 | calculate_wire_bound_books_shopify | Wire Bound Books | ✅ Active | Multiple stocks | 25-1000 |
| 9 | calculate_spiral_bound_books_shopify | Spiral Bound Books | ✅ Active | Multiple stocks | 25-1000 |
| 10 | calculate_saddle_stitch_books | Saddle Stitch Books | ✅ Active | Multiple stocks | 25-1000 |
| 11 | calculate_letterheads | Letterheads (Standard) | ✅ Active | 3 stock options | 100-5000 |
| 12 | calculate_printed_letterheads | Printed Letterheads | ✅ Active | 3 stock options | 100-5000 |
| 13 | calculate_corflute_signs | Corflute Signs | ✅ Active | 3mm/5mm | 1-100 |
| 14 | calculate_corflute_signs_shopify | Corflute Signs (Shopify) | ✅ Active | 3mm/5mm | 1-100 |
| 15 | calculate_bollard_signs | Bollard Signs | ✅ Active (Stub) | Fixed | 5-50 |
| 16 | calculate_construction_signs | Construction Signs | ✅ Active (Stub) | Fixed | 2-25 |
| 17 | calculate_election_signs | Election Signs | ✅ Active | 5mm corflute | 10-500 |
| 18 | calculate_corflute_insert_a_frame | A-Frame Inserts | ✅ Active | 5mm corflute | 1-50 |
| 19 | calculate_metal_face_a_frame | Metal A-Frames | ✅ Active (Stub) | Fixed | 1-10 |
| 20 | calculate_luxury_classic_pull_up_banners | Pull-Up Banners | ✅ Active | 3 sizes | 1-10 |
| 21 | calculate_selfie_frames | Selfie Frames | ✅ Active | 5mm corflute | 1-20 |
| 22 | calculate_stackable_cubes | Display Cubes | ✅ Active | Custom | 5-100 |
| 23 | calculate_premium_bookmarks | Premium Bookmarks | ✅ Active | 350gsm Silk | 100-5000 |
| 24 | calculate_with_compliments_slips | With Compliments Slips | ✅ Active | 150gsm Silk | 100-2500 |
| 25 | calculate_notepads_a4 | Notepads A4 | ✅ Active | 80gsm | 5-100 |
| 26 | calculate_notepads_a5 | Notepads A5 | ✅ Active | 80gsm | 5-100 |
| 27 | calculate_notepads_a6 | Notepads A6 | ✅ Active | 80gsm | 5-100 |
| 28 | calculate_custom_poster_printing | Custom Posters | ✅ Active | 200/250gsm Silk | 1-100 |
| 29 | calculate_custom_vinyl_stickers | Vinyl Stickers | ✅ Active | Vinyl | 50-1000 |
| 30 | calculate_strut_cards_a3 | Strut Cards A3 | ✅ Active | 400gsm Silk | 10-250 |
| 31 | calculate_strut_cards_a4 | Strut Cards A4 | ✅ Active | 400gsm Silk | 10-250 |

**Deactivated:**
| # | Tool Name | Product Type | Status | Reason |
|---|-----------|--------------|--------|--------|
| 32 | calculate_flyers_god | Flyers (GOD) | ❌ Deactivated | Database-driven, replaced by Shopify |
| 33 | calculate_letterheads_god | Letterheads (GOD) | ❌ Deactivated | Database-driven, replaced by Shopify |
| 34 | calculate_perfect_bound_books_god | Perfect Bound (GOD) | ❌ Deactivated | Database-driven, replaced by Shopify |
| 35 | calculate_corflute_signs_god | Corflute (GOD) | ❌ Deactivated | Database-driven, replaced by Shopify |

---

### Database Tool APIs

#### Tool 32 (Active): calculator_database_query

**Purpose:** Execute SELECT queries against calculator pricing database (read-only)

**Function Signature:**
```python
def calculator_database_query(
    sql: str,
    params: tuple = None,
    **kwargs
) -> List[Dict[str, Any]]
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sql` | string | ✅ Yes | SQL SELECT query (read-only) |
| `params` | tuple | ❌ No | Query parameters for prepared statements |

**Returns:**
```python
[
    {"parameter_name": "impos_setup", "base_value": 15.0, "data_type": "decimal"},
    {"parameter_name": "stock_350gsm_satin_rate", "base_value": 0.12, "data_type": "decimal"},
    ...
]
```

**Example Usage:**
```python
# Query pricing constants
result = calculator_database_query(
    sql="SELECT * FROM calculator_pricing_constants WHERE category = %s",
    params=("setup_fees",)
)

# Query product options
result = calculator_database_query(
    sql="""
        SELECT calculator_name, option_name, option_value, base_price
        FROM calculator_product_options
        WHERE calculator_name = %s
        ORDER BY base_price
    """,
    params=("business_cards",)
)
```

---

#### Tool 33 (Active): calculator_database_modify

**Purpose:** Execute INSERT/UPDATE/DELETE with safety validations

**Function Signature:**
```python
def calculator_database_modify(
    sql: str,
    params: tuple,
    reason: str,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sql` | string | ✅ Yes | SQL INSERT/UPDATE/DELETE statement |
| `params` | tuple | ✅ Yes | Query parameters |
| `reason` | string | ✅ Yes | Audit log reason for change |

**Returns:**
```python
{
    "success": True,
    "rows_affected": 1,
    "operation": "UPDATE",
    "audit_log_id": 12345
}
```

**Example Usage:**
```python
# Update pricing constant
result = calculator_database_modify(
    sql="UPDATE calculator_pricing_constants SET base_value = %s WHERE parameter_name = %s",
    params=(18.0, "impos_setup"),
    reason="Increased setup fee to cover new equipment costs"
)
```

---

#### Tool 34 (Active): calculator_database_get_schema_guide

**Purpose:** Get comprehensive schema guide for all 8 tables

**Function Signature:**
```python
def calculator_database_get_schema_guide(**kwargs) -> Dict[str, Any]
```

**Parameters:** None

**Returns:**
```python
{
    "success": True,
    "guide": "..." (500+ line markdown guide),
    "sections": 10,
    "total_tables": 8,
    "available_queries": 77
}
```

---

#### Tool 35 (Active): calculator_database_list_queries

**Purpose:** List pre-built QueryLibrary queries with metadata

**Function Signature:**
```python
def calculator_database_list_queries(
    category: str = "all",
    **kwargs
) -> List[Dict[str, Any]]
```

**Parameters:**
| Parameter | Type | Required | Valid Values | Default |
|-----------|------|----------|--------------|---------|
| `category` | string | ❌ No | `"all"`, `"Sales & Revenue"`, `"Customer Analytics"`, `"Product Performance"`, etc. | `"all"` |

**Returns:**
```python
[
    {
        "name": "sales_trend_by_month",
        "category": "Sales & Revenue",
        "description": "Monthly sales trends showing revenue, order count...",
        "parameters": {"months": {"type": "integer", "default": 6}},
        "validated": True
    },
    ...
]
```

---

## Database Schema

### Overview

The calculator system uses **8 tables** in the G_Folder SQL Server database for managing pricing data, product configurations, and custom calculators.

**Database:** G_Folder  
**Server:** DESKTOP-Q2C1H93\SQL2022EXPRESS  
**Connector:** `inhouse-print/db_connector.py` (shared with other modules)

### Table List

1. **calculator_pricing_constants** - Global pricing constants (500+ rows)
2. **calculator_pricing_parameters** - Calculation parameters (100+ rows)
3. **calculator_product_options** - Product configuration options (200+ rows)
4. **calculator_pricing_formulas** - Calculation formulas (50+ rows)
5. **calculator_parameter_overrides** - Custom pricing overrides
6. **calculator_audit_log** - Change tracking and audit trail
7. **calculator_pricing_catalog** - Product catalog and descriptions
8. **calculator_custom_calculators** - Custom calculator builder (separate doc)

---

### Table 1: calculator_pricing_constants

**Purpose:** Store global pricing constants used across all calculators

**Schema:**
```sql
CREATE TABLE calculator_pricing_constants (
    constant_id INT IDENTITY(1,1) PRIMARY KEY,
    parameter_name VARCHAR(100) NOT NULL UNIQUE,
    base_value DECIMAL(18,6) NOT NULL,
    description VARCHAR(500),
    category VARCHAR(50),
    data_type VARCHAR(20) DEFAULT 'decimal',
    unit VARCHAR(50),
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    created_by VARCHAR(100),
    updated_by VARCHAR(100)
);

CREATE INDEX idx_pricing_constants_category ON calculator_pricing_constants(category);
CREATE INDEX idx_pricing_constants_active ON calculator_pricing_constants(is_active);
```

**Example Data:**
| constant_id | parameter_name | base_value | description | category | unit |
|-------------|----------------|------------|-------------|----------|------|
| 1 | impos_setup | 15.000000 | Imposition setup fee | setup_fees | AUD |
| 2 | stock_350gsm_satin_rate | 0.120000 | 350GSM Satin per-sheet cost | stock_rates | AUD/sheet |
| 3 | celloglaze_1side_mult | 1.150000 | 1-side celloglaze multiplier | finish_multipliers | multiplier |
| 4 | celloglaze_2side_mult | 1.250000 | 2-side celloglaze multiplier | finish_multipliers | multiplier |
| 5 | quantity_discount_1000 | 0.950000 | 5% discount for 1000+ quantity | quantity_discounts | multiplier |

**Categories:**
- `setup_fees` - Setup and imposition fees
- `stock_rates` - Paper stock per-unit costs
- `finish_multipliers` - Celloglaze, lamination multipliers
- `quantity_discounts` - Volume discount multipliers
- `labor_rates` - Labor cost per hour/operation
- `overhead_rates` - Overhead percentage rates

---

### Table 2: calculator_pricing_parameters

**Purpose:** Store calculation parameters with value ranges and statistics

**Schema:**
```sql
CREATE TABLE calculator_pricing_parameters (
    parameter_id INT IDENTITY(1,1) PRIMARY KEY,
    parameter_name VARCHAR(100) NOT NULL UNIQUE,
    base_value DECIMAL(18,6) NOT NULL,
    min_value DECIMAL(18,6),
    max_value DECIMAL(18,6),
    data_type VARCHAR(20) DEFAULT 'decimal',
    value_range VARCHAR(200),
    value_statistics NVARCHAR(MAX),  -- JSON: {"min": 0.1, "max": 5.0, "mean": 1.2, "median": 1.0, "variance_pct": 15.5}
    description VARCHAR(500),
    category VARCHAR(50),
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

CREATE INDEX idx_pricing_parameters_category ON calculator_pricing_parameters(category);
```

**Example Data:**
| parameter_id | parameter_name | base_value | min_value | max_value | value_statistics (JSON) |
|--------------|----------------|------------|-----------|-----------|------------------------|
| 1 | stock_multiplier | 1.000000 | 0.800000 | 1.500000 | `{"mean": 1.12, "variance_pct": 12.5}` |
| 2 | labor_rate_per_hour | 45.000000 | 35.000000 | 60.000000 | `{"mean": 47.5, "median": 45.0}` |
| 3 | setup_time_minutes | 15.000000 | 10.000000 | 30.000000 | `{"variance_pct": 25.0}` |

---

### Table 3: calculator_product_options

**Purpose:** Store product configuration options and their pricing

**Schema:**
```sql
CREATE TABLE calculator_product_options (
    option_id INT IDENTITY(1,1) PRIMARY KEY,
    calculator_name VARCHAR(100) NOT NULL,
    option_name VARCHAR(100) NOT NULL,
    option_value VARCHAR(100) NOT NULL,
    base_price DECIMAL(18,6),
    multiplier DECIMAL(18,6),
    description VARCHAR(500),
    category VARCHAR(50),
    is_active BIT DEFAULT 1,
    display_order INT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    
    CONSTRAINT uq_calculator_option UNIQUE (calculator_name, option_name, option_value)
);

CREATE INDEX idx_product_options_calculator ON calculator_product_options(calculator_name);
CREATE INDEX idx_product_options_category ON calculator_product_options(category);
```

**Example Data:**
| option_id | calculator_name | option_name | option_value | base_price | multiplier |
|-----------|-----------------|-------------|--------------|------------|------------|
| 1 | business_cards | stock | 300GSM Satin | NULL | 1.0 |
| 2 | business_cards | stock | 400GSM Uncoated | NULL | 1.15 |
| 3 | business_cards | celloglaze | No Celloglaze | 0.00 | 1.0 |
| 4 | business_cards | celloglaze | 2 Side Matt | NULL | 1.25 |
| 5 | flyers | size | A4 | NULL | 1.0 |
| 6 | flyers | size | A5 | NULL | 0.75 |

---

### Table 4: calculator_pricing_formulas

**Purpose:** Store calculation formulas for dynamic pricing

**Schema:**
```sql
CREATE TABLE calculator_pricing_formulas (
    formula_id INT IDENTITY(1,1) PRIMARY KEY,
    calculator_name VARCHAR(100) NOT NULL,
    formula_name VARCHAR(100) NOT NULL,
    formula_expression NVARCHAR(MAX) NOT NULL,  -- e.g., "base_price * quantity * stock_multiplier + setup_fee"
    description VARCHAR(500),
    variables_required NVARCHAR(MAX),  -- JSON array: ["quantity", "base_price", "stock_multiplier"]
    example_calculation NVARCHAR(MAX),  -- JSON: {"quantity": 500, "result": 125.45}
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    
    CONSTRAINT uq_calculator_formula UNIQUE (calculator_name, formula_name)
);
```

**Example Data:**
| formula_id | calculator_name | formula_name | formula_expression | variables_required (JSON) |
|------------|-----------------|--------------|-------------------|---------------------------|
| 1 | business_cards | base_price_calc | `(quantity / 1000) * base_rate_per_1000 + setup_fee` | `["quantity", "base_rate_per_1000", "setup_fee"]` |
| 2 | business_cards | celloglaze_price | `base_price * celloglaze_multiplier` | `["base_price", "celloglaze_multiplier"]` |
| 3 | flyers | area_based_price | `(width * height / 1000000) * rate_per_sqm * quantity` | `["width", "height", "rate_per_sqm", "quantity"]` |

---

### Table 5: calculator_parameter_overrides

**Purpose:** Store custom pricing overrides for specific calculators

**Schema:**
```sql
CREATE TABLE calculator_parameter_overrides (
    override_id INT IDENTITY(1,1) PRIMARY KEY,
    calculator_name VARCHAR(100) NOT NULL,
    parameter_name VARCHAR(100) NOT NULL,
    override_value DECIMAL(18,6) NOT NULL,
    reason VARCHAR(500),
    valid_from DATETIME DEFAULT GETDATE(),
    valid_to DATETIME,
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    created_by VARCHAR(100),
    
    CONSTRAINT uq_calculator_parameter_override UNIQUE (calculator_name, parameter_name, valid_from)
);

CREATE INDEX idx_parameter_overrides_calculator ON calculator_parameter_overrides(calculator_name);
CREATE INDEX idx_parameter_overrides_active ON calculator_parameter_overrides(is_active);
```

**Example Data:**
| override_id | calculator_name | parameter_name | override_value | reason | valid_from | valid_to |
|-------------|-----------------|----------------|----------------|--------|------------|----------|
| 1 | business_cards | impos_setup | 18.000000 | Increased for new equipment costs | 2025-12-01 | NULL |
| 2 | flyers | stock_350gsm_rate | 0.135000 | Supplier price increase | 2026-01-01 | 2026-06-30 |

---

### Table 6: calculator_audit_log

**Purpose:** Track all changes to calculator pricing data

**Schema:**
```sql
CREATE TABLE calculator_audit_log (
    audit_id INT IDENTITY(1,1) PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(20) NOT NULL,  -- INSERT, UPDATE, DELETE
    record_id INT NOT NULL,
    old_values NVARCHAR(MAX),  -- JSON
    new_values NVARCHAR(MAX),  -- JSON
    changed_by VARCHAR(100),
    reason VARCHAR(500),
    changed_at DATETIME DEFAULT GETDATE()
);

CREATE INDEX idx_audit_log_table ON calculator_audit_log(table_name);
CREATE INDEX idx_audit_log_date ON calculator_audit_log(changed_at);
```

---

### Table 7: calculator_pricing_catalog

**Purpose:** Product catalog with descriptions and metadata

**Schema:**
```sql
CREATE TABLE calculator_pricing_catalog (
    catalog_id INT IDENTITY(1,1) PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL UNIQUE,
    calculator_name VARCHAR(100) NOT NULL,
    description NVARCHAR(MAX),
    thumbnail_url VARCHAR(500),
    shopify_product_id VARCHAR(50),
    category VARCHAR(50),
    tags NVARCHAR(500),  -- Comma-separated tags
    is_active BIT DEFAULT 1,
    display_order INT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);
```

---

### Table 8: calculator_custom_calculators

**Purpose:** Custom calculator builder (see CUSTOM_CALCULATOR_BUILDER.md for details)

**Note:** This table is part of the custom calculator builder system, which is documented separately as it involves formula evaluation, parameter validation, and complex business logic.

---

## Query Library

### Overview

The **QueryLibrary** system provides 77 pre-built, optimized SQL queries for business intelligence and analytics. These queries are designed for AI agents to request common reports without writing custom SQL.

**File:** `backend/query_library.py` (5,958 lines)  
**Total Queries:** 77 queries across 8 categories  
**Test Status:** 14/14 query generation tests passing (Dec 17, 2025)

### Query Categories

1. **Sales & Revenue** (12 queries) - Revenue trends, product sales, customer sales
2. **Customer Analytics** (8 queries) - Retention cohorts, lifetime value, segmentation
3. **Product Performance** (10 queries) - Best sellers, profit margins, inventory turnover
4. **Operational Metrics** (9 queries) - Turnaround times, capacity utilization, job efficiency
5. **Financial Analysis** (7 queries) - Cost breakdowns, margin analysis, profitability
6. **Calculator Pricing** (7 queries) - Pricing constants, parameter analysis, variance tracking
7. **Quality & Returns** (6 queries) - Defect rates, return reasons, quality trends
8. **Forecasting & Planning** (18 queries) - Demand forecasting, capacity planning, seasonal trends

---

### Example Queries

#### Query 1: sales_trend_by_month

**Category:** Sales & Revenue  
**Purpose:** Monthly sales trends showing revenue, order count, and average order value

**Parameters:**
- `months` (integer, default=6) - Number of months to analyze

**SQL Generated:**
```sql
SELECT 
    FORMAT(OrderDate, 'yyyy-MM') AS YearMonth,
    SUM(TotalAmount) AS TotalRevenue,
    COUNT(DISTINCT OrderID) AS OrderCount,
    AVG(TotalAmount) AS AvgOrderValue,
    SUM(CASE WHEN OrderStatus = 'completed' THEN 1 ELSE 0 END) AS CompletedOrders,
    SUM(CASE WHEN OrderStatus = 'cancelled' THEN 1 ELSE 0 END) AS CancelledOrders
FROM Orders
WHERE OrderDate >= DATEADD(MONTH, -6, GETDATE())
GROUP BY FORMAT(OrderDate, 'yyyy-MM')
ORDER BY YearMonth DESC;
```

**Returns:**
| YearMonth | TotalRevenue | OrderCount | AvgOrderValue | CompletedOrders | CancelledOrders |
|-----------|--------------|------------|---------------|-----------------|-----------------|
| 2026-01 | $45,234.50 | 87 | $520.05 | 82 | 5 |
| 2025-12 | $52,445.00 | 102 | $514.16 | 98 | 4 |
| 2025-11 | $48,990.25 | 95 | $515.69 | 91 | 4 |

**Usage Example:**
```python
# Via calculator_database_list_queries tool
queries = calculator_database_list_queries(category="Sales & Revenue")

# Find sales_trend_by_month query
query_meta = next(q for q in queries if q['name'] == 'sales_trend_by_month')

# Execute query with QueryLibrary
from backend.query_library import QueryLibrary
query_lib = QueryLibrary(db_connection)

result = query_lib.get_query("sales_trend_by_month", months=12)
# Returns: {"sql": "SELECT ...", "parameters": {...}, "visualization": "line_chart"}

# Execute via database tool
df = calculator_database_query(sql=result['sql'])
```

---

#### Query 2: get_pricing_constant

**Category:** Calculator Pricing  
**Purpose:** Get pricing constant value with override tracking

**Parameters:**
- `parameter_name` (string, required) - Name of pricing constant (e.g., "impos_setup")

**SQL Generated:**
```sql
SELECT 
    p.parameter_name,
    p.base_value,
    p.description,
    p.category,
    p.unit,
    p.data_type,
    p.updated_at AS base_updated_at,
    o.calculator_name AS override_calculator,
    o.override_value,
    o.reason AS override_reason,
    o.valid_from AS override_valid_from,
    o.valid_to AS override_valid_to,
    CASE 
        WHEN o.override_id IS NOT NULL AND o.is_active = 1 
            AND GETDATE() BETWEEN o.valid_from AND ISNULL(o.valid_to, '9999-12-31')
        THEN o.override_value
        ELSE p.base_value
    END AS effective_value
FROM calculator_pricing_constants p
LEFT JOIN calculator_parameter_overrides o 
    ON p.parameter_name = o.parameter_name
    AND o.is_active = 1
WHERE p.parameter_name = 'impos_setup'
    AND p.is_active = 1
ORDER BY o.valid_from DESC;
```

**Returns:**
| parameter_name | base_value | effective_value | override_calculator | override_reason |
|---------------|------------|-----------------|---------------------|-----------------|
| impos_setup | 15.00 | 18.00 | business_cards | Increased for new equipment costs |

---

#### Query 3: find_high_variance_parameters

**Category:** Calculator Pricing  
**Purpose:** Find parameters with high variance (potential optimization targets)

**Parameters:**
- `min_variance_pct` (integer, default=10) - Minimum variance percentage to include

**SQL Generated:**
```sql
SELECT 
    p.parameter_name,
    p.base_value,
    p.data_type,
    (p.value_statistics->>'variance_pct')::numeric AS variance_pct,
    (p.value_statistics->>'min')::numeric AS min_value,
    (p.value_statistics->>'max')::numeric AS max_value,
    (p.value_statistics->>'mean')::numeric AS mean_value,
    (p.value_statistics->>'median')::numeric AS median_value,
    COALESCE(
        (SELECT COUNT(*) 
         FROM calculator_parameter_overrides o 
         WHERE o.parameter_name = p.parameter_name AND o.is_active = 1), 
        0
    ) AS override_count
FROM calculator_pricing_parameters p
WHERE (p.value_statistics->>'variance_pct')::numeric >= 10
    AND p.is_active = 1
ORDER BY (p.value_statistics->>'variance_pct')::numeric DESC;
```

**Returns:**
| parameter_name | base_value | variance_pct | min_value | max_value | override_count |
|---------------|------------|--------------|-----------|-----------|----------------|
| stock_multiplier | 1.00 | 25.5 | 0.80 | 1.50 | 12 |
| setup_time_minutes | 15.00 | 22.3 | 10.00 | 30.00 | 5 |

**Use Case:** Identify parameters with high variation across calculators, indicating potential for standardization or optimization.

---

### Complete Query List

**Sales & Revenue (12 queries):**
1. sales_trend_by_month
2. monthly_revenue_trend
3. revenue_by_product_type
4. revenue_by_customer
5. daily_sales_summary
6. sales_by_salesperson
7. sales_by_region
8. year_over_year_comparison
9. quarter_over_quarter_growth
10. sales_forecast_linear
11. sales_by_payment_method
12. refund_analysis

**Customer Analytics (8 queries):**
13. customer_retention_cohort
14. customer_lifetime_value
15. customer_segmentation_rfm
16. churn_risk_analysis
17. customer_acquisition_cost
18. repeat_customer_rate
19. customer_feedback_sentiment
20. top_customers_by_volume

**Product Performance (10 queries):**
21. best_selling_products
22. product_profit_margins
23. inventory_turnover
24. slow_moving_inventory
25. product_bundling_analysis
26. cross_sell_opportunities
27. product_category_performance
28. stock_out_frequency
29. product_price_elasticity
30. seasonal_product_trends

**Operational Metrics (9 queries):**
31. average_turnaround_time
32. production_capacity_utilization
33. job_efficiency_by_type
34. equipment_utilization
35. labor_productivity
36. setup_time_analysis
37. bottleneck_identification
38. on_time_delivery_rate
39. order_fulfillment_speed

**Financial Analysis (7 queries):**
40. cost_breakdown_by_product
41. margin_analysis_by_customer
42. profitability_by_job_type
43. overhead_allocation
44. cost_variance_analysis
45. break_even_analysis
46. cash_flow_projection

**Calculator Pricing (7 queries):**
47. get_pricing_constant
48. get_calculator_config
49. get_product_options_for_calculator
50. find_high_variance_parameters
51. get_parameter_usage_map
52. search_product_options
53. get_option_price_variance

**Quality & Returns (6 queries):**
54. defect_rate_by_product
55. return_reasons_analysis
56. quality_trend_over_time
57. customer_complaints_by_type
58. rework_cost_analysis
59. first_pass_yield

**Forecasting & Planning (18 queries):**
60. demand_forecast_moving_average
61. capacity_planning_requirements
62. seasonal_demand_patterns
63. lead_time_analysis
64. safety_stock_recommendations
65. reorder_point_calculation
66. supplier_performance_trends
67. price_change_impact_forecast
68. new_product_launch_projection
69. market_share_analysis
70. competitive_pricing_comparison
71. customer_growth_projection
72. resource_allocation_optimization
73. budget_vs_actual_variance
74. roi_by_marketing_channel
75. sales_pipeline_conversion
76. quote_to_order_conversion_rate
77. average_deal_size_trend

---

## Testing & Validation

### Test Suite Overview

**Total Tests:** 40 comprehensive tests  
**Success Rate:** 97.5% (39/40 tests passing)  
**Last Tested:** December 14, 2025  
**Test Location:** `tests/`

### Test Files

1. **test_comprehensive.py** - Main test suite (40 tests)
2. **test_all_calculators.py** - Individual calculator validation (31 tests)
3. **test_calculator_queries.py** - QueryLibrary generation tests (14/14 passing)
4. **test_wrapper_integration.py** - Wrapper integration tests (all passing)
5. **test_registry_tools.py** - Registry V3 discovery tests (4/4 passing)

---

### Test Results Summary

**Test Suite 1: Comprehensive Calculator Tests**  
**File:** `tests/test_comprehensive.py`  
**Status:** 39/40 tests passing (97.5%)

**Passing Tests (39):**
```
✅ Business Cards
   ├─ calculate_business_cards (standard)
   ├─ calculate_economical_business_cards_shopify
   └─ calculate_premium_business_cards_shopify

✅ Flyers
   ├─ calculate_flyers
   └─ calculate_folded_flyers_shopify

✅ Books & Booklets
   ├─ calculate_booklets (saddle stitch)
   ├─ calculate_perfect_bound_books
   ├─ calculate_wire_bound_books_shopify
   ├─ calculate_spiral_bound_books_shopify
   └─ calculate_saddle_stitch_books

✅ Letterheads
   ├─ calculate_letterheads
   └─ calculate_printed_letterheads

✅ Signs & Displays
   ├─ calculate_corflute_signs
   ├─ calculate_corflute_signs_shopify
   ├─ calculate_bollard_signs
   ├─ calculate_construction_signs
   ├─ calculate_election_signs
   ├─ calculate_corflute_insert_a_frame
   ├─ calculate_metal_face_a_frame
   ├─ calculate_luxury_classic_pull_up_banners
   ├─ calculate_selfie_frames
   └─ calculate_stackable_cubes

✅ Stationery
   ├─ calculate_premium_bookmarks
   ├─ calculate_with_compliments_slips
   ├─ calculate_notepads_a4
   ├─ calculate_notepads_a5
   └─ calculate_notepads_a6

✅ Large Format
   ├─ calculate_custom_poster_printing
   ├─ calculate_custom_vinyl_stickers
   ├─ calculate_strut_cards_a3
   └─ calculate_strut_cards_a4
```

**Failing Test (1):**
```
❌ calculate_corflute_signs (specific parameter combination)
   Error: "Invalid thickness: 7mm. Must be one of ['3mm', '5mm']"
   Status: Known issue - test uses invalid parameter
   Fix: Update test to use valid thickness values
```

---

**Test Suite 2: QueryLibrary Generation Tests**  
**File:** `tests/test_calculator_queries.py`  
**Status:** 14/14 tests passing (100%)

**Tested Queries:**
```
✅ get_pricing_constant (2 parameter variations)
✅ get_calculator_config (2 parameter variations)
✅ get_product_options_for_calculator (2 parameter variations)
✅ find_high_variance_parameters (2 parameter variations)
✅ get_parameter_usage_map (2 parameter variations)
✅ search_product_options (2 parameter variations)
✅ get_option_price_variance (2 parameter variations)
```

**Validation Checks:**
- ✅ All queries build SQL correctly
- ✅ All queries have complete metadata
- ✅ All queries marked as validated=True
- ✅ SQL lengths range from 602 to 3,489 characters
- ✅ All queries include SELECT, FROM, and calculator tables

---

**Test Suite 3: Wrapper Integration Tests**  
**File:** `tests/test_wrapper_integration.py`  
**Status:** All integration checks passed

**Tests:**
```
✅ calculator_database_get_schema_guide() - Returns 500+ line guide
✅ calculator_database_list_queries() - Returns 7 queries with metadata
✅ calculator_database_query() - Function exists and validates input
✅ calculator_database_modify() - Function exists (needs DB for full test)
✅ Dynamic query injection - 7 queries discovered
```

---

**Test Suite 4: Registry V3 Auto-Discovery**  
**File:** `tests/test_registry_tools.py`  
**Status:** 4/4 tools discovered and verified (100%)

**Registry V3 Statistics:**
- Total tools in registry: 1,050 tools
- Calculator database tools found: 4/4 (100%)
- Module: quote-calculator
- Platform: quote_calculator

**Tool Verification:**
```
✅ calculator_database_get_schema_guide
   ├─ Platform: quote_calculator
   ├─ Description: Complete schema guide for 8-table database
   ├─ Parameters: None (no args required)
   ├─ Has implementation: True
   ├─ Implementation callable: True
   └─ Usage guide sections: 5 sections

✅ calculator_database_query
   ├─ Platform: quote_calculator
   ├─ Description: Execute SELECT queries (read-only)
   ├─ Parameters: sql (required), params (optional)
   ├─ Has implementation: True
   └─ Implementation callable: True

✅ calculator_database_modify
   ├─ Platform: quote_calculator
   ├─ Description: Execute INSERT/UPDATE/DELETE with safety
   ├─ Parameters: sql, params, reason (required)
   ├─ Has implementation: True
   └─ Implementation callable: True

✅ calculator_database_list_queries
   ├─ Platform: quote_calculator
   ├─ Description: List pre-built queries from QueryLibrary
   ├─ Parameters: category (default: "all")
   ├─ Has implementation: True
   └─ Implementation callable: True
```

---

### Manual Testing Checklist

```bash
# Test 1: Business Cards Calculator
# =================================
# Run calculator wrapper directly
python
>>> from implementations.calculator_wrapper import calculate_business_cards
>>> result = calculate_business_cards(quantity=500, stock_type="satin", print_type="double_sided")
>>> print(result)

# Expected output:
# {
#     "success": True,
#     "total_price": 110.00,
#     "per_unit_price": 0.22,
#     "quantity": 500,
#     "stock": "350GSM Satin",
#     "turnaround_days": 3
# }


# Test 2: Registry V3 Tool Discovery
# ==================================
# Check if tools are auto-discovered
python
>>> from tools.registry_v3 import RegistryV3
>>> registry = RegistryV3()
>>> calc_tools = [t for t in registry.tools.values() if t.get('platform') == 'quote_calculator']
>>> print(f"Found {len(calc_tools)} calculator tools")

# Expected: "Found 35 calculator tools" (31 active + 4 database tools)


# Test 3: Type Safety Validation
# ==============================
# Test type conversion (string → int)
python
>>> result = calculate_business_cards(quantity="500", stock_type="satin", print_type="double_sided")
>>> print(result['quantity'], type(result['quantity']))

# Expected: 500 <class 'int'>  (string "500" converted to integer 500)


# Test 4: Parameter Enum Validation
# =================================
# Test invalid quantity
python
>>> result = calculate_business_cards(quantity=375, stock_type="satin", print_type="double_sided")

# Expected error:
# ValueError: Invalid quantity: 375. Must be one of [100, 250, 500, 1000, 2000, 5000, 10000]


# Test 5: QueryLibrary Query Generation
# =====================================
python
>>> from backend.query_library import QueryLibrary
>>> query_lib = QueryLibrary()
>>> result = query_lib.get_query("sales_trend_by_month", months=6)
>>> print(result['sql'][:100])  # First 100 chars

# Expected: "SELECT FORMAT(OrderDate, 'yyyy-MM') AS YearMonth, SUM(TotalAmount) AS TotalRevenue..."


# Test 6: Database Tool - Schema Guide
# ====================================
python
>>> from implementations.calculator_pricing_wrapper import calculator_database_get_schema_guide
>>> result = calculator_database_get_schema_guide()
>>> print(result['sections'], result['total_tables'])

# Expected: 10 8  (10 guide sections, 8 database tables)


# Test 7: All Calculators Quick Test
# ==================================
# Run comprehensive test suite
cd tests
python test_all_calculators.py

# Expected output:
# Testing 31 calculators...
# ✅ calculate_business_cards
# ✅ calculate_economical_business_cards_shopify
# ...
# ✅ calculate_strut_cards_a4
# 
# Summary: 31/31 tests passed (100%)
```

---

## Configuration

### Environment Variables

```bash
# G_Folder Database Connection (SQL Server)
G_FOLDER_SERVER=DESKTOP-Q2C1H93\\SQL2022EXPRESS
G_FOLDER_DATABASE=G_Folder
G_FOLDER_USER=<username>
G_FOLDER_PASSWORD=<password>

# Supabase Connection (Calculator Pricing Database)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_DB_PASSWORD=your-db-password

# Quote Calculator Configuration
QUOTE_CALCULATOR_ENABLED=True
QUOTE_CALCULATOR_DEFAULT_TURNAROUND_DAYS=3
QUOTE_CALCULATOR_SETUP_FEE_BUSINESS_CARDS=15.00
QUOTE_CALCULATOR_SETUP_FEE_FLYERS=12.00

# Testing Configuration
TEST_MODE=False
TEST_DATABASE_ENABLED=False
```

### Configuration Files

**File 1: database-config.json**  
**Location:** `config/database-config.json`  
**Purpose:** Database connection settings

```json
{
    "g_folder": {
        "server": "DESKTOP-Q2C1H93\\SQL2022EXPRESS",
        "database": "G_Folder",
        "driver": "ODBC Driver 17 for SQL Server",
        "trusted_connection": true,
        "connection_timeout": 30,
        "command_timeout": 60
    },
    "supabase": {
        "url": "https://your-project.supabase.co",
        "service_role_key": "${SUPABASE_KEY}",
        "connection_string": "postgresql://postgres:${SUPABASE_DB_PASSWORD}@db.your-project.supabase.co:5432/postgres",
        "pool_size": 10,
        "max_overflow": 5
    },
    "fallback": {
        "retry_attempts": 3,
        "retry_delay_seconds": 5,
        "use_cache": true,
        "cache_ttl_seconds": 300
    }
}
```

---

**File 2: manifest.json**  
**Location:** `manifest.json`  
**Purpose:** Module manifest for Registry V3

```json
{
    "id": "quote-calculator",
    "name": "Quote Calculator",
    "version": "1.0.0",
    "description": "InHouse Print quote generation and pricing tools with AI integration",
    "author": "InHouse Print",
    "license": "Proprietary",
    "html_file": "quote-calculator.html",
    "js_file": "quote-calculator.js",
    "css_file": "quote-calculator.css",
    "main_tab": true,
    "main_tab_id": "quote-calculator",
    "module": {
        "main": "quote-calculator.js",
        "class": "QuoteCalculatorModule",
        "styles": "quote-calculator.css",
        "html": "quote-calculator.html"
    },
    "ui": {
        "icon": "fas fa-calculator",
        "colors": {
            "primary": "#ffb347",
            "secondary": "#ffd699",
            "hover": "#ffaa33",
            "gradient": "linear-gradient(135deg, #ffb347 0%, #ffd699 100%)"
        },
        "position": 4
    },
    "tabs": [
        {
            "id": "business-cards",
            "name": "Business Cards",
            "icon": "fas fa-id-card",
            "default": true
        },
        {
            "id": "flyers",
            "name": "Flyers",
            "icon": "fas fa-file-alt"
        },
        {
            "id": "books",
            "name": "Books & Booklets",
            "icon": "fas fa-book"
        }
    ]
}
```

---

### Deployment Configuration

**Production Settings:**
```bash
# Enable production mode
FLASK_ENV=production
DEBUG=False

# Database pooling
POOL_ENABLED=True
POOL_SIZE=10
POOL_MAX_OVERFLOW=5

# Caching
ENABLE_CALCULATOR_CACHE=True
CACHE_TTL_SECONDS=300

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/quote_calculator.log
```

---

## Troubleshooting

### Issue 1: Calculator Returns "Database connection failed"

**Symptoms:**
- Calculator tools return error: "Failed to calculate {product_type} quote"
- Error message: "Database connection failed"

**Diagnosis:**
```python
# Test database connection
from inhouse-print.db_connector import InHousePrintDB

db = InHousePrintDB()
try:
    result = db.execute_query("SELECT 1")
    print("✅ Database connected")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

**Solutions:**
1. **Check G_Folder database is running:**
```powershell
# Check SQL Server service
Get-Service -Name "MSSQL$SQL2022EXPRESS"

# Expected: Status "Running"
```

2. **Verify connection string in config/database-config.json**
3. **Test credentials:**
```bash
sqlcmd -S DESKTOP-Q2C1H93\SQL2022EXPRESS -d G_Folder -U <user> -P <password> -Q "SELECT 1"
```

---

### Issue 2: "Invalid quantity" Error with Valid Quantity

**Symptoms:**
- Error: "Invalid quantity: 500. Must be one of [100, 250, 500, 1000, ...]"
- Quantity IS in the enum list

**Root Cause:**
String type mismatch - AI agent passes `"500"` (string) but enum checks for `500` (integer)

**Solution:**
The `@calculator_wrapper` decorator should handle this automatically. If error persists:

```python
# Check if wrapper is applied
from implementations.calculator_wrapper import calculate_business_cards
import inspect

sig = inspect.signature(calculate_business_cards)
print(sig)  # Should show wrapper metadata

# Manual fix (if wrapper not working):
quantity = int(quantity)  # Convert string to integer
```

---

### Issue 3: QueryLibrary Query Returns Empty Results

**Symptoms:**
- Query executes successfully but returns `[]` (empty list)
- Expected results but got nothing

**Diagnosis:**
```python
# Check if data exists in G_Folder database
from inhouse-print.db_connector import InHousePrintDB

db = InHousePrintDB()
result = db.execute_query("SELECT COUNT(*) FROM Orders")
print(f"Total orders: {result[0][0]}")
```

**Solutions:**
1. **Verify date range parameters:**
```python
# Query uses relative dates (e.g., last 6 months)
# If no orders in last 6 months, result is empty

# Test with larger date range
result = query_lib.get_query("sales_trend_by_month", months=24)
```

2. **Check table names match:**
```sql
-- G_Folder uses specific table names
-- Query might reference wrong table

-- Verify table exists:
SELECT * FROM sys.tables WHERE name LIKE '%Order%'
```

---

### Issue 4: Type Enforcement Not Working

**Symptoms:**
- Calculator receives string `"500"` but doesn't convert to integer
- TypeError: "unsupported operand type(s) for /: 'str' and 'int'"

**Root Cause:**
`@calculator_wrapper` decorator not applied or schema_validator.py import failed

**Diagnosis:**
```python
# Check if decorator is loaded
from implementations.schema_validator import calculator_wrapper
print(calculator_wrapper)

# Check if wrapper applied to function
from implementations.calculator_wrapper import calculate_business_cards
print(hasattr(calculate_business_cards, '__wrapped__'))  # Should be True
```

**Solution:**
```python
# File: implementations/calculator_wrapper.py
# Line 110: Ensure decorator is applied

@calculator_wrapper(quantity_enum=[100, 250, 500, 1000, 2000, 5000, 10000])
def calculate_business_cards(quantity: int, ...):
    # Function body
```

---

### Issue 5: GOD Calculators Not Available

**Symptoms:**
- Error: "GOD calculators not available"
- Functions `calculate_flyers_god`, `calculate_letterheads_god` not working

**Expected Behavior:**
GOD calculators were **intentionally deactivated** on January 13, 2026.

**Reason:**
Shopify hardcoded calculators are now the primary system. GOD database-driven calculators had import issues and were bypassed.

**Solution:**
Use Shopify equivalents:
- `calculate_flyers_god` → `calculate_flyers`
- `calculate_letterheads_god` → `calculate_letterheads`
- `calculate_perfect_bound_books_god` → `calculate_perfect_bound_books`
- `calculate_corflute_signs_god` → `calculate_corflute_signs`

**To Re-enable GOD Calculators (if needed):**
```python
# File: implementations/calculator_wrapper.py
# Lines 50-59: Uncomment GOD imports

try:
    from GOD_flyer_calculator import FlyerCalculatorGOD
    from GOD_letterhead_calculator import LetterheadCalculatorGOD
    from GOD_perfect_bound_books_calculator import PerfectBoundBooksCalculator
    from corflute_calculator import CorflutePricingCalculator
    
    GOD_CALCULATORS_AVAILABLE = True
    print("✅ [GOD Calculators] Loaded successfully")
except ImportError as e:
    print(f"⚠️  [GOD Calculators] Failed to import: {e}")
```

---

## Known Issues

### Issue 1: ⚠️ ONE TEST FAILING (1/40) - Corflute Signs Invalid Parameter

**Status:** Known Issue (Not Critical)  
**Severity:** Low  
**Test:** `test_comprehensive.py` - `calculate_corflute_signs` with 7mm thickness

**Details:**
```python
# Test uses invalid thickness parameter
result = calculate_corflute_signs(
    quantity=10,
    width=600,
    height=900,
    thickness="7mm",  # ❌ Invalid - only 3mm and 5mm supported
    sides="single_sided"
)

# Error: "Invalid thickness: 7mm. Must be one of ['3mm', '5mm']"
```

**Impact:**
- Does not affect production functionality
- All valid parameter combinations work correctly
- Only test suite uses invalid parameter

**Workaround:**
Update test to use valid thickness:
```python
# Fixed test
result = calculate_corflute_signs(
    quantity=10,
    width=600,
    height=900,
    thickness="5mm",  # ✅ Valid
    sides="single_sided"
)
```

---

### Issue 2: ⚠️ Custom Calculator Builder Not Included

**Status:** Separate Documentation  
**Severity:** N/A  
**Details:**
Per user request, custom calculator builder is documented separately in `CUSTOM_CALCULATOR_BUILDER.md`.

**Reason:**
Custom calculator builder involves:
- Formula evaluation engine (asteval)
- Complex parameter validation
- Schema builder UI
- Separate workflow from standard calculators

**Impact:**
- 6 custom calculator tools not documented here
- Database table `calculator_custom_calculators` mentioned but not detailed

**Reference:**
See `CUSTOM_CALCULATOR_BUILDER.md` for complete documentation of custom calculator system.

---

### Issue 3: 🔵 Stub Implementation Calculators (4 Calculators)

**Status:** Design Decision  
**Severity:** Low  
**Affected Calculators:**
1. `calculate_bollard_signs`
2. `calculate_construction_signs`
3. `calculate_metal_face_a_frame`
4. `calculate_stackable_cubes` (partial stub)

**Details:**
These calculators return hardcoded fixed prices instead of dynamic calculations:

```python
def calculate_bollard_signs(**kwargs) -> Dict[str, Any]:
    """
    Calculate quote for bollard signs (STUB IMPLEMENTATION)
    
    Returns fixed quote: $45.00 per sign, minimum 5 signs
    """
    return {
        "success": True,
        "total_price": 225.00,  # Hardcoded: 5 signs × $45
        "per_unit_price": 45.00,
        "quantity": 5,
        "product": "Bollard Signs",
        "note": "Stub implementation - fixed pricing"
    }
```

**Reason:**
- Low-volume products with infrequent orders
- Pricing too variable to hardcode tables
- Custom quotes typically required

**Workaround:**
For accurate quotes, use manual quoting process or contact sales team.

---

### Issue 4: 🔵 Shopify Calculators Have Hardcoded Stock Options

**Status:** Design Limitation  
**Severity:** Low  
**Impact:** Cannot change stock/size for some calculators

**Details:**
Economical and Premium business card calculators have fixed stock:

```python
# Economical Business Cards
stock = "300GSM Satin"  # Hardcoded, cannot change

# Premium Business Cards
stock = "400GSM Uncoated"  # Hardcoded, cannot change
```

**Reason:**
Shopify product pages have fixed configurations. Calculators match website pricing exactly.

**Workaround:**
Use `calculate_business_cards` (standard) which supports flexible stock options:
```python
result = calculate_business_cards(
    quantity=500,
    stock_type="satin",  # Can choose: standard, premium, satin, uncoated
    print_type="double_sided"
)
```

---

### Issue 5: ⚠️ QueryLibrary Queries Require G_Folder Database Access

**Status:** Expected Behavior  
**Severity:** Medium (if database unavailable)

**Details:**
All 77 QueryLibrary queries execute against G_Folder SQL Server database. If database is offline or inaccessible, queries will fail.

**Error:**
```python
# If G_Folder database offline:
result = calculator_database_query(sql="SELECT * FROM Orders")

# Returns:
{
    "success": False,
    "error": "Database connection failed",
    "details": "Cannot connect to server DESKTOP-Q2C1H93\\SQL2022EXPRESS"
}
```

**Solutions:**
1. **Check database status:**
```powershell
Get-Service -Name "MSSQL$SQL2022EXPRESS"
# Should be "Running"
```

2. **Fallback to cached results** (if enabled):
```python
# config/database-config.json
{
    "fallback": {
        "use_cache": true,
        "cache_ttl_seconds": 300  # 5 minutes
    }
}
```

3. **Use alternative data sources:**
- Supabase PostgreSQL (calculator pricing tables only)
- Export historical query results to CSV

---

## Appendix

### Glossary

- **GOD Calculator** - Graphic on Demand calculator (database-driven, deactivated)
- **Shopify Calculator** - Hardcoded pricing matching Shopify website (primary system)
- **QueryLibrary** - 77 pre-built SQL queries for business intelligence
- **Calculator Wrapper** - Type-safe wrapper layer with `@calculator_wrapper` decorator
- **Registry V3** - Tool discovery and registration system
- **Celloglaze** - Laminated finish (gloss or matte)
- **Setup Fee** - One-time imposition/plate setup cost
- **Per-Unit Price** - Total price ÷ quantity
- **Turnaround Days** - Production time estimate
- **G_Folder Database** - SQL Server database with pricing data
- **Supabase** - PostgreSQL database for calculator pricing tables

### Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Overall system architecture
- [MODULES.md](MODULES.md) - Module plugin system
- [AI_AGENTS.md](AI_AGENTS.md) - AI agent integration
- [SUPABASE_DATABASE.md](SUPABASE_DATABASE.md) - Database schemas
- [INHOUSE_PRINT.md](INHOUSE_PRINT.md) - InHouse Print integration
- [CUSTOM_CALCULATOR_BUILDER.md](CUSTOM_CALCULATOR_BUILDER.md) - Custom calculator builder (separate doc)

### External Resources

- [InHouse Print Website](https://example.com) - Product catalog and pricing
- [Shopify Product Pages](https://example.com/collections/business-cards) - Pricing source of truth
- [G_Folder Database Documentation](internal) - Database schema reference
- [Supabase Documentation](https://supabase.com/docs) - PostgreSQL hosting

### Development Team Contact

- **Primary Developer:** Greg Polimeni
- **Project Repository:** https://github.com/your-username/AI_agents
- **Issue Tracker:** GitHub Issues
- **Documentation:** This file + 40+ consolidated source files

---

## Document Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-01-18 | 2.0.0 | Created master documentation consolidating 40+ files | AI Documentation Assistant |
| 2025-12-17 | 1.5.0 | Added QueryLibrary tests (14/14 passing) | Backend Team |
| 2025-12-14 | 1.4.0 | Test suite complete (39/40 passing, 97.5%) | Testing Team |
| 2025-12-12 | 1.3.0 | Type enforcement system complete | Backend Team |
| 2025-12-11 | 1.2.0 | All 31 Shopify calculators operational | Backend Team |
| 2025-12-10 | 1.1.0 | Registry V3 integration complete | Integration Team |
| 2025-12-01 | 1.0.0 | Initial production release | Full Team |

---

**End of Documentation**  
**Last Updated:** January 18, 2026  
**Document Version:** 2.0.0  
**Total Lines:** ~3,400 lines  
**File Size:** ~220 KB

---

## Quick Reference Commands

```bash
# Test All Calculators
cd tests
python test_all_calculators.py

# Test QueryLibrary
python test_calculator_queries.py

# Test Registry V3 Discovery
python test_registry_tools.py

# Check Database Connection
python -c "from inhouse-print.db_connector import InHousePrintDB; db = InHousePrintDB(); print(db.execute_query('SELECT 1'))"

# Run Single Calculator Test
python
>>> from implementations.calculator_wrapper import calculate_business_cards
>>> result = calculate_business_cards(quantity=500, stock_type="satin", print_type="double_sided")
>>> print(result)

# Check Tool Registration
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); calc_tools = [t for t in r.tools.values() if t.get('platform') == 'quote_calculator']; print(f'Found {len(calc_tools)} calculator tools')"
```
