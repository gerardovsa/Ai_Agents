# Tool Use Agent - Key Dependencies Map
**Analysis of `tool_use_agent.py` (3,187 lines) - Complete Dependency Tree**

---

## 🎯 Core Dependencies (CRITICAL - Must Have)

### 1. **Database Connector**
```python
from db_connector import InHousePrintDB
```
**File:** `inhouse_modules/db_connector.py`  
**Purpose:** SQL Server (FredDEV) connection for Orders, JobTickets, PaperSize, BindType tables  
**Used For:** All SQL queries (`execute_sql` tool)  
**Critical:** YES - Without this, no database access

### 2. **Comprehensive Quote Calculator**
```python
from complete_calculator_implementation import ComprehensiveQuoteCalculator
```
**File:** `inhouse_modules/complete_calculator_implementation.py` (6,277 lines)  
**Purpose:** Master calculator with all product types (business cards, flyers, booklets, books)  
**Used For:** `calculate_quote` tool, `get_calculator_requirements` tool  
**Critical:** YES - Core quote calculation engine

### 3. **Query Library**
```python
from query_library import QueryLibrary
```
**File:** `UI/external/modules/quote-calculator/backend/query_library.py` (5,042 lines)  
**Purpose:** 50+ pre-built SQL queries for business intelligence  
**Used For:** `get_available_queries` and `get_query_from_library` tools  
**Critical:** YES - Provides BI query catalog

### 4. **Stock Database Tools**
```python
from stock_database_tools import StockDatabaseTools
```
**File:** `UI/external/modules/quote-calculator/backend/stock_database_tools.py`  
**Purpose:** SQLite stock_data.db management (inventory, transactions, alerts)  
**Used For:** All stock management tools (9 tools total)  
**Critical:** YES - Inventory management

---

## 📦 Shopify Calculator Dependencies (Product-Specific)

### 5. **Wire Bound Calculator (Shopify)**
```python
from WireBound_Shopify_Calculator import WireBoundShopifyCalculator
```
**File:** `UI/external/modules/quote-calculator/backend/shopify_calculators/WireBound_Shopify_Calculator.py`  
**Purpose:** Metal wire coil binding (14 thickness tiers, 15% GST + $44 surcharge)  
**Used For:** `calculate_quote` with `product_type='wire_bound_books'`  
**Critical:** For wire bound quotes only

### 6. **Spiral Bound Calculator (Shopify)**
```python
from SpiralBound_Shopify_Calculator import SpiralBoundShopifyCalculator
```
**File:** `UI/external/modules/quote-calculator/backend/shopify_calculators/SpiralBound_Shopify_Calculator.py`  
**Purpose:** Plastic spiral coil binding (17 thickness tiers, 15% GST + $44 surcharge)  
**Used For:** `calculate_quote` with `product_type='spiral_bound_books'`  
**Critical:** For spiral bound quotes only

### 7. **Perfect Bound Calculator (Shopify)**
```python
from PerfectBound_Shopify_Calculator import PerfectBoundShopifyCalculator
```
**File:** `UI/external/modules/quote-calculator/backend/shopify_calculators/PerfectBound_Shopify_Calculator.py`  
**Purpose:** Glued square spine binding (8 quantity tiers, 10% GST only)  
**Used For:** `calculate_quote` with `product_type='perfect_bound_books'`  
**Critical:** For perfect bound quotes only

### 8. **Economical Business Cards (Shopify)**
```python
from EconomicalBusinessCards_Shopify_Calculator import EconomicalBusinessCardsShopifyCalculator
```
**File:** `UI/external/modules/quote-calculator/backend/shopify_calculators/EconomicalBusinessCards_Shopify_Calculator.py`  
**Purpose:** Budget business cards (F1-F6 fields, cards-per-sheet calculation, 10% GST)  
**Used For:** `calculate_quote` with `product_type='economical_business_cards'`  
**Critical:** For economical cards quotes only

### 9. **Folded Flyers (Shopify)**
```python
from FoldedFlyers_Shopify_Calculator import FoldedFlyersShopifyCalculator
```
**File:** `UI/external/modules/quote-calculator/backend/shopify_calculators/FoldedFlyers_Shopify_Calculator.py`  
**Purpose:** Folded brochures (F1-F8 fields, MANDATORY folding, size-based profit margins)  
**Used For:** `calculate_quote` with `product_type='folded_flyers'`  
**Critical:** For folded flyers quotes only

### 10. **Premium Business Cards (Shopify)**
```python
from PremiumBusinessCards_Shopify_Calculator import PremiumBusinessCardsShopifyCalculator
```
**File:** `UI/external/modules/quote-calculator/backend/shopify_calculators/PremiumBusinessCards_Shopify_Calculator.py`  
**Purpose:** Premium cards (F1-F7 fields, DOUBLE GST, dual profit structure)  
**Used For:** `calculate_quote` with `product_type='premium_business_cards_shopify'`  
**Critical:** For premium cards quotes only

---

## 🔧 Configuration & Python Libraries

### 11. **Database Configuration File**
```python
# Loaded in __init__
with open(config_full_path, 'r') as f:
    self.config = json.load(f)
```
**File:** `config/database-config.json`  
**Purpose:** Database connection strings, API keys, model settings  
**Format:**
```json
{
  "Database": {
    "Server": "FredDEV",
    "Database": "InHousePrintDB",
    "Driver": "ODBC Driver 17 for SQL Server"
  },
  "AI": {
    "AnthropicAPIKey": "sk-ant-...",
    "Model": "claude-sonnet-4-5-20250929"
  }
}
```
**Critical:** YES - Required for initialization

### 12. **Anthropic Python SDK**
```python
from anthropic import Anthropic
self.anthropic_client = Anthropic(api_key=self.config['AI']['AnthropicAPIKey'])
```
**Package:** `anthropic` (pip install anthropic)  
**Purpose:** Claude API access for Tool Use API  
**Critical:** YES - Core AI functionality

### 13. **Standard Python Libraries**
```python
import sys, os, json
from typing import Dict, Any, Optional, List
from datetime import datetime
```
**Purpose:** System paths, JSON handling, type hints, timestamps  
**Critical:** YES - Standard library (always available)

---

## 📊 Database Files

### 14. **SQL Server Database (FredDEV)**
**Server:** FredDEV  
**Database:** InHousePrintDB  
**Tables Used:**
- `Orders` (ClientName, OrderDate, OrderID)
- `JobTickets` (TicketID, TicketNotes, QTY, Cost, Pages, etc.)
- `PaperSize` (SizeID, [Desc]) - NO Width/Height columns
- `BindType` (BindID, BindTypeDesc) - NOT [Desc]
- `ColourStatus` (ColourID, ColourDesc) - Urgency, NOT print color
- `JobType`, `PaperType`, `GSM` (Lookup tables)
- `Quote_DigitalStocks` (Production pricing)

**Critical:** YES - Production order history and specifications

### 15. **SQLite Database (stock_data.db)**
**File:** `UI/external/modules/quote-calculator/backend/stocks/stock_data.db`  
**Tables Used:**
- `unified_stocks` (Current inventory levels, reorder points)
- `transactions` (Stock movements PURCHASE/CONSUMPTION/ADJUSTMENT)
- `reorder_alerts` (CRITICAL/WARNING alerts)
- `extracted_jobs` (219 AI-extracted jobs with 31 columns)

**Critical:** YES - Inventory management and BI data

---

## 📁 File Structure Map

```
AI_agents/
├── config/
│   └── database-config.json  ◄── 11. Configuration file (CRITICAL)
│
├── inhouse_modules/
│   ├── db_connector.py  ◄── 1. SQL Server connector (CRITICAL)
│   ├── complete_calculator_implementation.py  ◄── 2. Master calculator (CRITICAL)
│   └── [other InHouse modules]
│
└── UI/external/modules/quote-calculator/
    ├── backend/
    │   ├── tool_use_agent.py  ◄── MAIN FILE (3,187 lines)
    │   ├── query_library.py  ◄── 3. Query catalog (CRITICAL)
    │   ├── stock_database_tools.py  ◄── 4. Inventory tools (CRITICAL)
    │   │
    │   ├── shopify_calculators/  ◄── Shopify pricing calculators
    │   │   ├── WireBound_Shopify_Calculator.py  ◄── 5. Wire bound
    │   │   ├── SpiralBound_Shopify_Calculator.py  ◄── 6. Spiral bound
    │   │   ├── PerfectBound_Shopify_Calculator.py  ◄── 7. Perfect bound
    │   │   ├── EconomicalBusinessCards_Shopify_Calculator.py  ◄── 8. Econ cards
    │   │   ├── FoldedFlyers_Shopify_Calculator.py  ◄── 9. Folded flyers
    │   │   └── PremiumBusinessCards_Shopify_Calculator.py  ◄── 10. Premium cards
    │   │
    │   └── stocks/
    │       └── stock_data.db  ◄── 15. SQLite inventory database
    │
    └── exports/
        └── AI_Quotes/  ◄── Log files (created at runtime)
```

---

## 🎯 Dependency Priority Levels

### **LEVEL 1 - ABSOLUTE CRITICAL (System won't start)**
1. ✅ `db_connector.py` - Database access
2. ✅ `complete_calculator_implementation.py` - Core calculations
3. ✅ `database-config.json` - Configuration
4. ✅ `anthropic` Python package - AI API

**Without these:** `ToolUseAgent.__init__()` will fail immediately

### **LEVEL 2 - FEATURE CRITICAL (Tools won't work)**
5. ✅ `query_library.py` - BI queries fail
6. ✅ `stock_database_tools.py` - Inventory tools fail
7. ✅ SQL Server FredDEV - All SQL queries fail
8. ✅ `stock_data.db` - Inventory queries fail

**Without these:** Specific tools fail, but agent starts

### **LEVEL 3 - PRODUCT-SPECIFIC (Only affects specific products)**
9. ⚠️ `WireBound_Shopify_Calculator.py` - Wire bound quotes fail
10. ⚠️ `SpiralBound_Shopify_Calculator.py` - Spiral bound quotes fail
11. ⚠️ `PerfectBound_Shopify_Calculator.py` - Perfect bound quotes fail
12. ⚠️ `EconomicalBusinessCards_Shopify_Calculator.py` - Economical cards fail
13. ⚠️ `FoldedFlyers_Shopify_Calculator.py` - Folded flyers fail
14. ⚠️ `PremiumBusinessCards_Shopify_Calculator.py` - Premium cards fail

**Without these:** Specific product quotes fail, other products work

---

## 🔍 Dependency Verification Checklist

### Pre-Integration Checklist
```bash
# 1. Check database connector exists
test -f c:\Users\gpoli\GIT\AI_agents\inhouse_modules\db_connector.py
echo $?  # Should be 0

# 2. Check master calculator exists
test -f c:\Users\gpoli\GIT\AI_agents\inhouse_modules\complete_calculator_implementation.py
echo $?  # Should be 0

# 3. Check query library exists
test -f c:\Users\gpoli\GIT\AI_agents\UI\external\modules\quote-calculator\backend\query_library.py
echo $?  # Should be 0

# 4. Check stock tools exist
test -f c:\Users\gpoli\GIT\AI_agents\UI\external\modules\quote-calculator\backend\stock_database_tools.py
echo $?  # Should be 0

# 5. Check config file exists
test -f c:\Users\gpoli\GIT\AI_agents\config\database-config.json
echo $?  # Should be 0

# 6. Check Shopify calculators exist
test -d c:\Users\gpoli\GIT\AI_agents\UI\external\modules\quote-calculator\backend\shopify_calculators
echo $?  # Should be 0

# 7. Check stock database exists
test -f c:\Users\gpoli\GIT\AI_agents\UI\external\modules\quote-calculator\backend\stocks\stock_data.db
echo $?  # Should be 0

# 8. Check anthropic package installed
python -c "import anthropic; print(anthropic.__version__)"
# Should print version (e.g., 0.58.0)
```

### Python Import Test
```python
# Test all critical imports
import sys
import os

# Add paths
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents/inhouse_modules')
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents/UI/external/modules/quote-calculator/backend')
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents/UI/external/modules/quote-calculator/backend/shopify_calculators')

# Test imports
try:
    from db_connector import InHousePrintDB
    print("✅ db_connector")
except ImportError as e:
    print(f"❌ db_connector: {e}")

try:
    from complete_calculator_implementation import ComprehensiveQuoteCalculator
    print("✅ complete_calculator_implementation")
except ImportError as e:
    print(f"❌ complete_calculator_implementation: {e}")

try:
    from query_library import QueryLibrary
    print("✅ query_library")
except ImportError as e:
    print(f"❌ query_library: {e}")

try:
    from stock_database_tools import StockDatabaseTools
    print("✅ stock_database_tools")
except ImportError as e:
    print(f"❌ stock_database_tools: {e}")

try:
    from WireBound_Shopify_Calculator import WireBoundShopifyCalculator
    print("✅ WireBound_Shopify_Calculator")
except ImportError as e:
    print(f"❌ WireBound_Shopify_Calculator: {e}")

try:
    from anthropic import Anthropic
    print("✅ anthropic")
except ImportError as e:
    print(f"❌ anthropic: {e}")
```

---

## 🚨 Common Import Issues & Solutions

### Issue 1: ModuleNotFoundError for `db_connector`
**Error:** `ModuleNotFoundError: No module named 'db_connector'`

**Solution:**
```python
# Add inhouse_modules to sys.path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'inhouse_modules'))
```

### Issue 2: ModuleNotFoundError for Shopify calculators
**Error:** `ModuleNotFoundError: No module named 'WireBound_Shopify_Calculator'`

**Solution:**
```python
# Add shopify_calculators to sys.path
shopify_path = os.path.join(os.path.dirname(__file__), 'shopify_calculators')
sys.path.insert(0, shopify_path)
```

### Issue 3: Database connection fails
**Error:** `pyodbc.Error: ('01000', "[01000] [unixODBC][Driver Manager]...")`

**Solution:**
```bash
# Install ODBC Driver 17 for SQL Server
# Windows: Download from Microsoft
# Verify: odbcinst -q -d
```

### Issue 4: SQLite database not found
**Error:** `sqlite3.OperationalError: unable to open database file`

**Solution:**
```python
# Verify path is correct
db_path = os.path.join(os.path.dirname(__file__), 'stocks', 'stock_data.db')
print(f"Looking for: {db_path}")
print(f"Exists: {os.path.exists(db_path)}")
```

---

## 📋 Integration Requirements Summary

**For G_FOLDER Integration into AI_agents, you MUST have:**

### Minimum Required (Can't start without these)
- ✅ `inhouse_modules/db_connector.py`
- ✅ `inhouse_modules/complete_calculator_implementation.py`
- ✅ `config/database-config.json`
- ✅ Python package: `anthropic`

### Highly Recommended (Core functionality)
- ✅ `backend/query_library.py`
- ✅ `backend/stock_database_tools.py`
- ✅ SQL Server access to FredDEV
- ✅ `backend/stocks/stock_data.db`

### Optional (Product-specific)
- ⚠️ All Shopify calculator files (6 calculators)
- ⚠️ Individual product calculators can be added incrementally

---

## 🔗 Integration File Changes

**When integrating into AI_agents via wrapper pattern:**

### New Files to Create
```
UI/external/modules/quote-calculator/
├── schema/
│   └── inhouse_tools.json  ◄── NEW (15 tool definitions)
└── implementations/
    └── inhouse_wrapper.py  ◄── NEW (bridges registry → tool_use_agent)
```

### Files to Reference (NOT MODIFY)
```
UI/external/modules/quote-calculator/
└── backend/
    ├── tool_use_agent.py  ◄── REUSE AS LIBRARY (unchanged)
    ├── query_library.py  ◄── Used by wrapper
    ├── stock_database_tools.py  ◄── Used by wrapper
    └── shopify_calculators/  ◄── Used by wrapper
        └── [all 6 calculator files]
```

### Files from inhouse_modules
```
inhouse_modules/
├── db_connector.py  ◄── Imported by tool_use_agent.py
└── complete_calculator_implementation.py  ◄── Imported by tool_use_agent.py
```

---

## ✅ Verification Command

**Run this to verify ALL dependencies are present:**

```python
# Comprehensive dependency check
import sys
import os

# Set up paths
base_path = r'c:\Users\gpoli\GIT\AI_agents'
sys.path.insert(0, os.path.join(base_path, 'inhouse_modules'))
sys.path.insert(0, os.path.join(base_path, 'UI', 'external', 'modules', 'quote-calculator', 'backend'))
sys.path.insert(0, os.path.join(base_path, 'UI', 'external', 'modules', 'quote-calculator', 'backend', 'shopify_calculators'))

dependencies = {
    'CRITICAL': [
        ('db_connector', 'InHousePrintDB'),
        ('complete_calculator_implementation', 'ComprehensiveQuoteCalculator'),
        ('anthropic', 'Anthropic'),
    ],
    'IMPORTANT': [
        ('query_library', 'QueryLibrary'),
        ('stock_database_tools', 'StockDatabaseTools'),
    ],
    'OPTIONAL': [
        ('WireBound_Shopify_Calculator', 'WireBoundShopifyCalculator'),
        ('SpiralBound_Shopify_Calculator', 'SpiralBoundShopifyCalculator'),
        ('PerfectBound_Shopify_Calculator', 'PerfectBoundShopifyCalculator'),
        ('EconomicalBusinessCards_Shopify_Calculator', 'EconomicalBusinessCardsShopifyCalculator'),
        ('FoldedFlyers_Shopify_Calculator', 'FoldedFlyersShopifyCalculator'),
        ('PremiumBusinessCards_Shopify_Calculator', 'PremiumBusinessCardsShopifyCalculator'),
    ]
}

for level, deps in dependencies.items():
    print(f"\n{level} Dependencies:")
    for module, cls in deps:
        try:
            mod = __import__(module)
            getattr(mod, cls)
            print(f"  ✅ {module}.{cls}")
        except ImportError as e:
            print(f"  ❌ {module}.{cls} - MISSING: {e}")
        except AttributeError as e:
            print(f"  ⚠️  {module}.{cls} - Module found but class missing: {e}")

# Check files
print("\nFile Dependencies:")
files = [
    ('config/database-config.json', 'CRITICAL'),
    ('UI/external/modules/quote-calculator/backend/stocks/stock_data.db', 'IMPORTANT'),
]
for file_path, level in files:
    full_path = os.path.join(base_path, file_path)
    exists = os.path.exists(full_path)
    status = "✅" if exists else "❌"
    print(f"  {status} {file_path} ({level})")

print("\n🎯 Ready for integration!" if all else "⚠️  Missing dependencies - resolve before integrating")
```

---

**Last Updated:** November 4, 2025  
**Status:** Complete Dependency Analysis  
**Next:** Run verification command before starting Phase 1 implementation
