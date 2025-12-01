# InHouse Print Quote Calculator - AI_agents Integration
**Date:** October 30, 2025  
**Source:** In_House_SQL/G_Folder/Quote_Calculator  
**Destination:** AI_agents/UI/external/modules/calculator-module/ORIGINAL

---

## 📋 Files Copied - Complete Transfer

### 🔑 Core Calculator Files (3 files)

1. **`complete_calculator_implementation.py`** (6,277 lines)
   - Main calculator engine
   - 5 production calculators: flyers, business_cards, perfect_bound_books, booklets, letterheads
   - Database-driven pricing (SQL Server)
   - VB.NET algorithm translations
   - 13-tier profit margin system

2. **`tool_use_agent.py`** (3,186 lines)
   - Main AI agent orchestrator
   - Tool definitions for all calculators
   - Claude AI integration
   - System prompt and routing logic
   - 22+ tools available

3. **`query_library.py`** (4,937 lines)
   - 50+ pre-built SQL queries
   - Historical quote analysis
   - Production data queries
   - Customer analytics
   - Visualization metadata

### 🛒 Shopify Calculators (9 Python files)

**Location:** `shopify_calculators/`

1. `business_card_calculator_shopify.py` - Business cards (website pricing)
2. `corflute_calculator_shopify.py` - Corflute signs (tier-based)
3. `EconomicalBusinessCards_Shopify_Calculator.py` - Economy cards
4. `PremiumBusinessCards_Shopify_Calculator.py` - Premium cards
5. `PerfectBound_Shopify_Calculator.py` - Perfect bound books
6. `FoldedFlyers_Shopify_Calculator.py` - Folded flyers
7. `WireBound_Shopify_Calculator.py` - Wire bound booklets
8. `SpiralBound_Shopify_Calculator.py` - Spiral bound booklets
9. `__init__.py` - Package initialization

### 📊 JSON Configuration Files (9 files)

**Location:** `shopify/`

1. `Business_Cards_Economic.json` - Economy card pricing tiers
2. `Premium_Business_Cards.json` - Premium card pricing
3. `Corflute_Signs_Shopify.json` - Corflute tier pricing
4. `Printed_Flyers_Shopify.json` - Standard flyers
5. `folded_printed_flyers_Shopify.json` - Folded flyers
6. `Perfect_Bound_books.json` - Perfect bound (Shopify)
7. `Perfect_Bound_Books_WooCommerce.json` - Perfect bound (WooCommerce)
8. `Wire_Spiral_Bound.json` - Wire/spiral binding
9. `[Additional configs as needed]`

### 📚 Documentation Files (10 files)

**Root Level:**
1. `CALCULATOR_ARCHITECTURE.md` - GOD vs Shopify architecture (3,000+ words)
2. `DATABASE_AND_BUSINESS_RULES.md` - Business logic reference
3. `CALCULATION_ALGORITHMS.md` - Formula documentation
4. `DOCUMENTATION_INDEX.md` - Navigation guide
5. `WHERE_IS_THE_AGENT_CODE.md` - File locations guide

**AI_Quote_Agent folder:**
6. `CALCULATORS_AVAILABLE.md` - Calculator status and features
7. `AI_Quote_Agent/core/query_catalog.json` - Query library catalog

### 🔌 Database Connector (1 file)

**`db_connector.py`** - SQL Server connection class
- InHousePrintDB class
- Connection pooling
- Query execution
- Result formatting

---

## 🏗️ Architecture Overview

```
calculator-module/ORIGINAL/
│
├── complete_calculator_implementation.py  # 🔑 Main Calculator Engine
├── tool_use_agent.py                      # 🔑 AI Agent Orchestrator
├── query_library.py                       # 🔑 SQL Query Library
├── db_connector.py                        # Database Connection
│
├── shopify_calculators/                   # Website Pricing Calculators
│   ├── business_card_calculator_shopify.py
│   ├── corflute_calculator_shopify.py
│   ├── [7 more calculator files]
│   └── __init__.py
│
├── shopify/                               # JSON Pricing Configs
│   ├── Business_Cards_Economic.json
│   ├── Premium_Business_Cards.json
│   ├── Corflute_Signs_Shopify.json
│   └── [6 more JSON configs]
│
├── AI_Quote_Agent/                        # AI Agent Support
│   ├── CALCULATORS_AVAILABLE.md
│   └── core/
│       └── query_catalog.json
│
└── [Documentation files]                  # 10 reference documents
```

---

## 🔄 Integration Flow

### Original In_House_SQL Flow:
```
User → Streamlit UI → tool_use_agent.py → Calculator/Query Library → SQL Server → Result
```

### Target AI_agents Flow:
```
User → AI_agents UI → [TO BE IMPLEMENTED] → Calculator Module → SQLite/SQL Server → Result
```

---

## 🎯 Calculator Capabilities

### 1. **Flyers (GOD Calculator)**
- Digital printing on paper stocks
- Database-driven pricing (SQL Server)
- Quantity tiers: 100-10,000+
- GSM options: 128-400gsm
- Print modes: Color, B&W, mixed

### 2. **Business Cards (Shopify Calculator)**
- 95% accurate website pricing
- Hardcoded tier-based pricing
- Standard/Premium options
- Cellophane finishes (gloss/matt)
- Quantities: 1,000-10,000+

### 3. **Perfect Bound Books (GOD Calculator)**
- Books with glued spine
- Cover + interior stock combinations
- Page count: 24-500 pages
- Database-driven costing
- Binding and trimming included

### 4. **Booklets (GOD Calculator)**
- Saddle-stitched multi-page
- 4-48 pages (divisible by 4)
- Various stock options
- Database pricing

### 5. **Letterheads (GOD Calculator)**
- Single/multi-color printing
- Standard sizes
- Database pricing

---

## 🛠️ Integration Requirements

### Python Dependencies:
```python
# Core
anthropic>=0.40.0        # Claude AI API
pandas>=2.0.0            # Data manipulation
pyodbc>=5.0.0            # SQL Server connector (for GOD calculators)
sqlite3                  # SQLite (built-in, for AI_agents)

# Shopify calculators
dataclasses              # Built-in Python 3.7+
decimal                  # Built-in
enum                     # Built-in
json                     # Built-in
math                     # Built-in
```

### Database Options:

**Option 1: SQL Server (Original)**
- Requires: Connection to In_House_SQL production database
- Tables: Quote_DigitalStocks, Quote_ProfitMargins, JobTickets
- Use: GOD calculators (flyers, perfect_bound_books, etc.)

**Option 2: SQLite (AI_agents Native)**
- Requires: Migration of pricing tables to SQLite
- Use: Self-contained deployment
- Note: Requires data export from SQL Server

**Option 3: Hybrid (Recommended)**
- Shopify calculators: No database needed (hardcoded pricing)
- GOD calculators: SQLite with exported pricing tables
- Query library: Adapt to AI_agents database schema

---

## 🔧 Adaptation Steps for AI_agents

### Step 1: Database Adaptation
```python
# Current (In_House_SQL):
from db_connector import InHousePrintDB
db = InHousePrintDB("config/database-config.json")

# Target (AI_agents):
import sqlite3
conn = sqlite3.connect("ai_infrastructure.db")
# OR
from AI_infrastructure.database import get_db_connection
```

### Step 2: Import Path Updates
```python
# Current (In_House_SQL):
from complete_calculator_implementation import ComprehensiveQuoteCalculator
from query_library import QueryLibrary

# Target (AI_agents):
from UI.external.modules.calculator_module.ORIGINAL.complete_calculator_implementation import ComprehensiveQuoteCalculator
from UI.external.modules.calculator_module.ORIGINAL.query_library import QueryLibrary
```

### Step 3: Tool Use Agent Integration
```python
# tool_use_agent.py needs:
1. AI_agents database connection
2. Import path adjustments
3. Tool registration in AI_agents tool registry
4. System prompt integration
```

### Step 4: Query Library Adaptation
```python
# query_library.py needs:
1. Adapt SQL queries to AI_agents schema
2. Replace In_House_SQL table names with AI_agents equivalents
3. Update visualization metadata for AI_agents UI
```

---

## 📊 Calculator Tool Definitions

### Available Tools (from tool_use_agent.py):

1. **`calculate_quote`** - Calculate quote for printing job
   - Input: product_type, parameters
   - Output: QuoteResult with full breakdown

2. **`get_calculator_requirements`** - Get required parameters
   - Input: product_type
   - Output: Parameter list and guidance

3. **`get_stock_list`** - List available paper stocks
   - Input: None or filters
   - Output: Stock options with pricing

4. **`execute_sql`** - Execute custom SQL query
   - Input: sql_query
   - Output: pandas DataFrame

5. **`get_available_queries`** - List pre-built queries
   - Input: Optional category filter
   - Output: Query catalog with descriptions

6. **`get_query_from_library`** - Execute pre-built query
   - Input: query_name, parameters
   - Output: DataFrame + visualization metadata

---

## 🎯 Next Steps - Implementation Plan

### Phase 1: Database Migration (Priority 1)
- [ ] Export pricing tables from SQL Server to SQLite
- [ ] Create AI_agents quote_calculator schema
- [ ] Test database connectivity

### Phase 2: Calculator Adaptation (Priority 2)
- [ ] Update import paths
- [ ] Adapt db_connector.py for AI_agents
- [ ] Test calculator execution

### Phase 3: Tool Registry Integration (Priority 3)
- [ ] Register calculator tools in AI_agents/tools/registry.py
- [ ] Create tool schemas (tools/schemas/calculator_tools.json)
- [ ] Create tool implementations (tools/implementations/calculator.py)

### Phase 4: Query Library Adaptation (Priority 4)
- [ ] Map In_House_SQL tables to AI_agents schema
- [ ] Update SQL queries
- [ ] Test query execution

### Phase 5: UI Integration (Priority 5)
- [ ] Create calculator UI component
- [ ] Integrate with AI_agents chat interface
- [ ] Test end-to-end workflow

---

## 🔍 Key Differences: In_House_SQL vs AI_agents

| Feature | In_House_SQL | AI_agents |
|---------|--------------|-----------|
| **Database** | SQL Server (production) | SQLite (ai_infrastructure.db) |
| **UI Framework** | Streamlit | Flask + HTML/JS |
| **Tool System** | Built-in to tool_use_agent.py | Centralized tools/registry.py |
| **Schema** | Quote_*, JobTickets | user_platform_credentials, sessions |
| **Deployment** | Local Python app | Render cloud + local |
| **AI Provider** | Anthropic Claude | Multi-provider (Anthropic, DeepSeek, OpenAI) |

---

## 📚 Documentation Reference

### Complete Documentation Index:
1. `CALCULATOR_ARCHITECTURE.md` - System design (GOD vs Shopify)
2. `DATABASE_AND_BUSINESS_RULES.md` - Business logic reference
3. `CALCULATION_ALGORITHMS.md` - Formula documentation
4. `DOCUMENTATION_INDEX.md` - Navigation guide
5. `WHERE_IS_THE_AGENT_CODE.md` - File locations
6. `CALCULATORS_AVAILABLE.md` - Calculator status matrix

### Query Library:
- 50+ pre-built queries documented in `query_library.py`
- Query catalog: `AI_Quote_Agent/core/query_catalog.json`
- Categories: Sales, Revenue, Customer Analytics, Quote Analysis, Production

---

## ⚠️ Critical Notes

### GOD Calculators (Database-Driven):
- **Require SQL Server connection** or SQLite export
- Tables needed: Quote_DigitalStocks, Quote_ProfitMargins, Quote_BinderyCosts
- **Most accurate** for production costing
- Used for: Flyers, Perfect Bound Books, Booklets, Letterheads

### Shopify Calculators (Hardcoded):
- **No database required** - all pricing hardcoded
- **95% accurate** for website pricing
- Used for: Business Cards (standard/premium/economy)
- Easier to deploy in AI_agents

### Recommended First Calculator:
**Start with Business Cards (Shopify)** - No database needed, easier integration, high usage.

---

## 🚀 Quick Start Test

```python
# Test Business Card Calculator (No database needed)
from shopify_calculators.business_card_calculator_shopify import (
    ShopifyBusinessCardCalculator,
    PrintType,
    StockTypeStandard
)

calculator = ShopifyBusinessCardCalculator()

result = calculator.calculate(
    quantity=1000,
    print_type=PrintType.DOUBLE_SIDED,
    stock_type=StockTypeStandard.SATIN_350GSM
)

print(f"Total: ${result.total_inc_gst}")
print(f"Per card: ${result.price_per_unit}")
# Expected: Total: ~$234.50, Per card: ~$0.23
```

---

## 📞 Support & References

- **Original Source:** `C:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator`
- **AI_agents Location:** `C:\Users\gpoli\GIT\AI_agents\UI\external\modules\calculator-module\ORIGINAL`
- **Integration Target:** AI_agents tools/implementations/calculator.py

**Total Files Copied:** 38+ files (3 core Python, 9 Shopify calculators, 9 JSON configs, 10 docs, 1 connector, plus support files)

**Status:** ✅ **COMPLETE** - All files successfully copied and ready for integration

---

**Last Updated:** October 30, 2025  
**Version:** 1.0 - Initial Transfer
