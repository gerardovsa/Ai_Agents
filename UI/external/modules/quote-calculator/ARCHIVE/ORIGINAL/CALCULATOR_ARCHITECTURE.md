# Quote Calculator Architecture
## GOD vs Shopify Calculator Systems

**Last Updated:** October 9, 2025  
**Status:** Production-ready, fully organized

---

## 🎯 Overview

The InHousePrint quote system uses **TWO distinct calculator architectures**:

1. **GOD Calculators** - Database-driven, VB.NET integrated production system
2. **Shopify Calculators** - Hardcoded website pricing for quote matching

---

## 🔷 GOD Calculators (Database-Driven)

### Location
```
G_Folder/Quote_Calculator/god_calculators/
```

### Purpose
- **Production quotes** for actual customer orders
- **Live database integration** with SQL Server
- **Real-time pricing** from stock tables
- **VB.NET logic conversion** from production system

### Database Sources
- `Quote_DigitalStocks` - Paper stock pricing
- `Quote_DigitalClicks` - Click/print costs
- `Quote_GenericSetting` - System settings (GST, setup costs, waste %)
- `Quote_ProfitMargins` - Dynamic profit margin tiers
- `Quote_RidgedProfitMargin` - Specialty product margins
- `Quote_PBBPerBookBindCost` - Perfect bound binding costs

### Calculators
1. **`corflute_calculator.py`** - Corflute signs
   - Based on 100+ real order analysis
   - Median cost: $9.37/sqm for 5mm corflute
   - Dynamic profit margins (32%-105%)

2. **`business_card_calculator.py`** - Business cards
   - 48 cards per sheet imposition
   - Setup costs: $15 imposition, $12 guillotine
   - Database-driven stock selection

3. **Flyers** - In `complete_calculator_implementation.py`
   - Method: `calculate_flyers()`
   - Converts `Flyers.vb` from VB.NET
   - Sheet optimization, click costs, folding, cello

4. **Perfect Bound Books** - In `complete_calculator_implementation.py`
   - Method: `calculate_perfect_bound_book()`
   - Converts `PerfectBBQuote.vb` from VB.NET
   - Per-book binding cost tiers
   - Cover + internal page calculations

5. **Letterheads, Booklets, Ridged Boards** - In `complete_calculator_implementation.py`
   - Full VB.NET production logic
   - Database-driven pricing

### Usage Example (GOD)
```python
from god_calculators.corflute_calculator import CorflutePricingCalculator

calc = CorflutePricingCalculator()
quote = calc.calculate_base_quote(
    quantity=50,
    width_mm=600,
    height_mm=900,
    thickness_mm=5
)
# Returns: Live database pricing with current stock costs
```

---

## 🔶 Shopify Calculators (Website Hardcoded)

### Location
```
G_Folder/Quote_Calculator/shopify_calculators/
```

### Purpose
- **Website quote matching** ONLY
- **Exact JavaScript replication** from Shopify DPO plugin
- **Hardcoded pricing tables** - no database connection
- **Pricing dashboard** verification

### Characteristics
- Fixed pricing tiers
- No database queries
- Match website behavior exactly
- Based on JSON config files

### Calculators
1. **`business_card_calculator_shopify.py`** - Standard business cards
   - Exact WooCommerce DPO logic
   - PrintType, FinishSize, StockType enums
   - Matches website quotes precisely

2. **`PremiumBusinessCards_Shopify_Calculator.py`** - Premium cards
   - F1-F7 field structure
   - DOUBLE GST calculation (quirk match)
   - SILK FEEL Matt stock

3. **`EconomicalBusinessCards_Shopify_Calculator.py`** - Budget cards
   - Lower-cost stock options
   - Simplified finish options

4. **`corflute_calculator_shopify.py`** - Corflute (website version)
   - 43-tier volume pricing for 5mm
   - 43-tier volume pricing for 3mm
   - Double-sided add $6/sqm
   - Custom size 10% premium

5. **`PerfectBound_Shopify_Calculator.py`** - Perfect bound (website)
   - F1-F11 WooCommerce fields
   - Quantity-based binding tiers
   - BizCost-based profit margins

6. **`WireBound_Shopify_Calculator.py`** - Wire bound books
   - F1-F14 WooCommerce fields
   - 14 thickness-based binding tiers
   - 15% GST + $44 surcharge

7. **`SpiralBound_Shopify_Calculator.py`** - Spiral bound books
   - Similar to wire bound
   - Different binding material costs

### Usage Example (Shopify)
```python
from shopify_calculators.corflute_calculator_shopify import CorflutePricingCalculatorShopify

calc = CorflutePricingCalculatorShopify()
quote = calc.calculate_quote(
    size_preset=CorfluteSizePreset.SIZE_600x900,
    quantity=50,
    thickness=CorfiuteThickness.MM_5
)
# Returns: Hardcoded website pricing (matches Shopify exactly)
```

---

## 📋 Complete File Organization

```
G_Folder/Quote_Calculator/
│
├── complete_calculator_implementation.py  # Unified calculator with GOD logic
│
├── god_calculators/                       # Database-driven production
│   ├── __init__.py
│   ├── corflute_calculator.py             #  Live database pricing
│   └── business_card_calculator.py        #  Database stock selection
│
├── shopify_calculators/                   # Hardcoded website pricing
│   ├── __init__.py
│   ├── business_card_calculator_shopify.py
│   ├── PremiumBusinessCards_Shopify_Calculator.py
│   ├── EconomicalBusinessCards_Shopify_Calculator.py
│   ├── corflute_calculator_shopify.py
│   ├── PerfectBound_Shopify_Calculator.py
│   ├── WireBound_Shopify_Calculator.py
│   └── SpiralBound_Shopify_Calculator.py
│
├── AI_Quote_Agent/                        # AI integration
│   └── core/
│       └── tool_use_agent.py              # Routes to appropriate calculator
│
└── comprehensive_quote_system.py          # Streamlit UI integration
```

---

## 🤖 AI Agent Decision Tree

The AI agent chooses between GOD and Shopify calculators based on context:

### Use GOD Calculator When:
- Customer needs a **production quote** for ordering
- Need **current stock pricing** (prices change)
- Calculating **custom specifications** not on website
- Creating **internal quotes** or job tickets
- Need **profit margin optimization**

### Use Shopify Calculator When:
- Customer mentions **website quote** or "online price"
- Verifying **website calculator accuracy**
- Creating **pricing dashboards** or comparisons
- Matching **exact Shopify behavior** (including quirks)
- Testing **website quote scenarios**

---

## 🔧 Import Patterns

### GOD Calculator Imports
```python
from god_calculators.corflute_calculator import CorflutePricingCalculator
from god_calculators.business_card_calculator import BusinessCardCalculator

# Or unified calculator
from complete_calculator_implementation import ComprehensiveQuoteCalculator
calc = ComprehensiveQuoteCalculator(db_connector)
quote = calc.calculate_flyers(...)  # GOD method
```

### Shopify Calculator Imports
```python
from shopify_calculators.corflute_calculator_shopify import CorflutePricingCalculatorShopify
from shopify_calculators.business_card_calculator_shopify import ShopifyBusinessCardCalculator

# Or via unified calculator
from complete_calculator_implementation import ComprehensiveQuoteCalculator
calc = ComprehensiveQuoteCalculator(db_connector)
quote = calc.calculate_business_card_shopify_standard(...)  # Shopify method
```

---

## 📊 Product Coverage

| Product | GOD Calculator | Shopify Calculator |
|---------|---------------|-------------------|
| Business Cards (Standard) |  `business_card_calculator.py` |  `business_card_calculator_shopify.py` |
| Business Cards (Premium) |  (GOD uses same) |  `PremiumBusinessCards_Shopify_Calculator.py` |
| Business Cards (Economical) |  (GOD uses same) |  `EconomicalBusinessCards_Shopify_Calculator.py` |
| Flyers |  `calculate_flyers()` |  Not on website |
| Corflute Signs |  `corflute_calculator.py` |  `corflute_calculator_shopify.py` |
| Perfect Bound Books |  `calculate_perfect_bound_book()` |  `PerfectBound_Shopify_Calculator.py` |
| Wire Bound Books |  `calculate_perfect_bound_book()` |  `WireBound_Shopify_Calculator.py` |
| Spiral Bound Books |  `calculate_perfect_bound_book()` |  `SpiralBound_Shopify_Calculator.py` |
| Letterheads |  `calculate_letterheads()` |  Not on website |
| Booklets |  `calculate_booklets()` |  Not on website |
| Ridged Boards |  `calculate_ridged_boards()` |  Not on website |

---

## 🚨 Key Differences

### Pricing Philosophy
- **GOD:** "What does this ACTUALLY cost us?" (live stock prices, real margins)
- **Shopify:** "What does the website say?" (hardcoded, match JavaScript exactly)

### Profit Margins
- **GOD:** Dynamic tiers from database (32%-105% based on cost)
- **Shopify:** Hardcoded BizCost-based tiers from JSON

### Stock Selection
- **GOD:** Optimizes sheet size for best price/waste ratio
- **Shopify:** Fixed stock types with hardcoded pricing

### Setup Costs
- **GOD:** From `Quote_GenericSetting` table (can change)
- **Shopify:** Hardcoded constants ($15 imposition, $12 guillotine, etc.)

---

## 📝 Development Guidelines

### When Adding New GOD Calculator:
1. Convert VB.NET logic from `InHousePrint\InHouseProductAPI\CalcClasses\`
2. Use `Quote_*` database tables for pricing
3. Implement dynamic profit margin lookup
4. Add to `god_calculators/` directory
5. Update `__init__.py` imports

### When Adding New Shopify Calculator:
1. Extract logic from website JavaScript (DPO plugin)
2. Create hardcoded pricing tables
3. Match website behavior EXACTLY (including quirks)
4. Add to `shopify_calculators/` directory
5. Update `__init__.py` imports
6. Create corresponding JSON config file

### Testing Both Systems:
```python
# Test GOD vs Shopify pricing difference
god_calc = CorflutePricingCalculator()
shopify_calc = CorflutePricingCalculatorShopify()

god_quote = god_calc.calculate_base_quote(50, 600, 900, 5)
shopify_quote = shopify_calc.calculate_quote(...)

print(f"GOD Price: ${god_quote['total_inc_gst']:.2f}")
print(f"Shopify Price: ${shopify_quote.total_price:.2f}")
print(f"Difference: ${abs(god_quote['total_inc_gst'] - shopify_quote.total_price):.2f}")
```

---

##  System Status

- **Last Major Cleanup:** October 9, 2025
- **Files Renamed:** 5 calculator files (WooCommerce → Shopify)
- **Folders Created:** `god_calculators/` and `shopify_calculators/`
- **Imports Updated:** All major files use new paths
- **Status:** Production-ready, fully organized

---

## 🔗 Related Documentation

- `COPILOT_INSTRUCTIONS.md` - Main development guide
- `G_Folder/tools/docs/business/DATABASE_BUSINESS_ATLAS.md` - Database schema
- `G_Folder/tools/docs/business/QUOTE_CALCULATOR_UPDATES.md` - Change log
- VB.NET Source: `InHousePrint\InHouseProductAPI\CalcClasses\` - Original GOD logic

---

**Remember:** GOD = Database Truth, Shopify = Website Match 🎯
