# Production Deployment Issues - Root Cause Analysis

**Date:** January 4, 2026  
**Environment:** Render Production vs Local Testing  
**Status:** Critical Issues Identified

---

## 🔴 Critical Issues Found

### Issue 1: ToolUseAgent Dependency - HARDCODED LOCAL PATHS

**Error Message:**
```
ToolUseAgent could not be imported - check backend path and dependencies
```

**Root Cause:**
The file `UI/modules_external/quote-calculator/backend/tool_use_agent.py` contains **hardcoded Windows local paths** that don't exist on Render's Linux deployment:

**Lines 48-50:**
```python
in_house_sql_root = 'C:/Users/gpoli/GIT/In_House_SQL'  # ❌ WINDOWS PATH
shopify_calc_path = os.path.join(in_house_sql_root, 'G_Folder', 'Quote_Calculator', 'shopify_calculators')
quote_calc_path = os.path.join(in_house_sql_root, 'G_Folder', 'Quote_Calculator')
```

**Line 105:**
```python
in_house_sql_root = 'C:/Users/gpoli/GIT/In_House_SQL'  # ❌ DUPLICATE HARDCODED PATH
```

**Files Affected:**
- `UI/modules_external/quote-calculator/backend/tool_use_agent.py` (3 hardcoded paths)
- `UI/modules_external/quote-calculator/backend/quote_calculator_routes.py` (1 hardcoded path)

**Impact:**
- ❌ `inhouse_execute_sql()` - Cannot import ToolUseAgent
- ❌ `inhouse_get_query_library_catalog()` - Cannot import ToolUseAgent
- ❌ All InHouse Print SQL tools fail on Render

**Why It Works Locally:**
- Local Windows machine HAS `C:/Users/gpoli/GIT/In_House_SQL` directory
- Render Linux server does NOT have this directory
- Import fails silently, tools return "ToolUseAgent could not be imported"

---

### Issue 2: DataFrame JSON Serialization - MISSING CONVERSION

**Error Message:**
```
Object of type DataFrame is not JSON serializable
```

**Root Cause:**
The `execute_query_library` tool in `query_library_wrapper.py` returns a pandas DataFrame in the `data` field, but Flask's JSON encoder cannot serialize DataFrames.

**Problem Code (Line 308 in query_library_wrapper.py):**
```python
return {
    "success": True,
    "query_name": query_name,
    "parameters_used": result.get("parameters_used", parameters or {}),
    "data": result.get("data", []),  # ❌ This is a DataFrame, not a list!
    "metadata": { ... }
}
```

**Why It Fails:**
```python
# query_library.py execute_query() returns:
{
    "success": True,
    "data": <pandas.DataFrame>,  # ❌ Not JSON serializable
    "summary": "Query returned X results",
    ...
}
```

**Flask JSON Response:**
```python
jsonify(result)  # ❌ TypeError: Object of type DataFrame is not JSON serializable
```

**Impact:**
- ⚠️ `execute_query_library()` - Query executes successfully but cannot return results
- ⚠️ All 77 pre-built queries fail at serialization stage
- Data is retrieved from database but lost during JSON encoding

---

### Issue 3: Supabase Client - MISSING DEPENDENCY

**Error Message:**
```
Supabase client not available - install dependencies
```

**Root Cause:**
Supabase Python client is listed in `requirements.txt` but may have installation issues during Render deployment.

**Requirements.txt Line:**
```txt
supabase>=2.0.0,<3.0  # Pin to avoid gotrue backtracking
```

**Possible Causes:**
1. **Dependency conflict** - gotrue version backtracking during pip install
2. **Import error** - supabase module not properly initialized
3. **Network timeout** - Render build timeout before supabase fully installs

**Impact:**
- ❌ `supabase_query()` - Cannot connect to Supabase PostgreSQL
- ❌ Stock data (ReorderAlerts, StockLevels) inaccessible
- ❌ All Supabase tools (25 tools) unavailable

**Why It Works Locally:**
- Local environment has supabase installed correctly
- No version conflicts in local environment
- Render may have pip resolver issues with gotrue dependency

---

### Issue 4: Database Tools Under Construction

**Error Message:**
```
Database tools not yet implemented
```

**Root Cause:**
The `db_*` tools in `inhouse_database` platform are placeholder implementations that always return "under construction" messages.

**Files Affected:**
- `db_get_available_queries()` - Returns `{"status": "under_construction"}`
- `db_execute_query()` - Returns `{"status": "under_construction"}`
- `db_get_business_summary()` - Returns `{"status": "under_construction"}`

**Impact:**
- ⚠️ 5 database tools return placeholder responses
- Not critical - these are duplicate tools (real tools exist in `quote_calculator` platform)

---

## 🔧 Solutions

### Solution 1: Remove Hardcoded Paths - USE RELATIVE PATHS

**Replace in `tool_use_agent.py` (Lines 46-56):**

**BEFORE (❌ BROKEN):**
```python
# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
implementations_dir = os.path.join(current_dir, '..', 'implementations')
in_house_sql_root = 'C:/Users/gpoli/GIT/In_House_SQL'  # ❌ HARDCODED
shopify_calc_path = os.path.join(in_house_sql_root, 'G_Folder', 'Quote_Calculator', 'shopify_calculators')
quote_calc_path = os.path.join(in_house_sql_root, 'G_Folder', 'Quote_Calculator')

# Path to inhouse-print module (contains db_connector.py)
# From: backend/ -> quote-calculator/ -> modules_external/ -> inhouse-print/
inhouse_print_module = os.path.abspath(os.path.join(current_dir, '..', '..', 'inhouse-print'))
```

**AFTER (✅ FIXED):**
```python
# Setup paths - ENVIRONMENT-AGNOSTIC
current_dir = os.path.dirname(os.path.abspath(__file__))
implementations_dir = os.path.join(current_dir, '..', 'implementations')

# Path to inhouse-print module (contains db_connector.py)
# From: backend/ -> quote-calculator/ -> modules_external/ -> inhouse-print/
inhouse_print_module = os.path.abspath(os.path.join(current_dir, '..', '..', 'inhouse-print'))

# ✅ All Shopify calculators are now in quote-calculator/backend/shopify_calculators/ (same repo)
# No need for external paths - everything is self-contained
shopify_calc_path = os.path.join(current_dir, 'shopify_calculators')
```

**Replace in `tool_use_agent.py` (Lines 102-108):**

**BEFORE (❌ BROKEN):**
```python
in_house_sql_root = 'C:/Users/gpoli/GIT/In_House_SQL'  # ❌ DUPLICATE HARDCODED PATH
quote_calc_path = os.path.join(in_house_sql_root, 'G_Folder', 'Quote_Calculator')
```

**AFTER (✅ FIXED):**
```python
# ✅ REMOVED - No longer needed. All calculators are in quote-calculator/backend/
```

**Remove Stock Tools Import (Lines 71-76):**

**BEFORE (❌ BROKEN):**
```python
# Import stock database tools from In_House_SQL
try:
    stock_tools_path = os.path.join(quote_calc_path, 'stocks')
    if stock_tools_path not in sys.path:
        sys.path.insert(0, stock_tools_path)
    from stock_database_tools import StockDatabaseTools
except ImportError:
    StockDatabaseTools = None
```

**AFTER (✅ FIXED):**
```python
# ✅ Stock data moved to Supabase PostgreSQL
# Stock tools should query Supabase directly (not SQLite)
# Remove legacy SQLite stock tools import
```

**Update Shopify Calculator Imports (Lines 80-86):**

**BEFORE (❌ BROKEN):**
```python
# Import Shopify calculator classes from In_House_SQL (source of truth)
from WireBound_Shopify_Calculator import WireBoundShopifyCalculator
from SpiralBound_Shopify_Calculator import SpiralBoundShopifyCalculator
from PerfectBound_Shopify_Calculator import PerfectBoundShopifyCalculator
from EconomicalBusinessCards_Shopify_Calculator import EconomicalBusinessCardsShopifyCalculator
from FoldedFlyers_Shopify_Calculator import FoldedFlyersShopifyCalculator
from PremiumBusinessCards_Shopify_Calculator import PremiumBusinessCardsShopifyCalculator
```

**AFTER (✅ FIXED):**
```python
# ✅ Import from local shopify_calculators/ folder (same repo)
# All calculators copied to quote-calculator/backend/shopify_calculators/
from shopify_calculators.WireBound_Shopify_Calculator import WireBoundShopifyCalculator
from shopify_calculators.SpiralBound_Shopify_Calculator import SpiralBoundShopifyCalculator
from shopify_calculators.PerfectBound_Shopify_Calculator import PerfectBoundShopifyCalculator
from shopify_calculators.EconomicalBusinessCards_Shopify_Calculator import EconomicalBusinessCardsShopifyCalculator
from shopify_calculators.FoldedFlyers_Shopify_Calculator import FoldedFlyersShopifyCalculator
from shopify_calculators.PremiumBusinessCards_Shopify_Calculator import PremiumBusinessCardsShopifyCalculator
```

---

### Solution 2: Convert DataFrame to JSON - ADD .to_dict()

**Replace in `query_library_wrapper.py` (Lines 285-320):**

**BEFORE (❌ BROKEN):**
```python
return {
    "success": True,
    "query_name": query_name,
    "parameters_used": result.get("parameters_used", parameters or {}),
    "data": result.get("data", []),  # ❌ DataFrame not serializable
    "metadata": {
        "description": query_def.get("description", ""),
        "category": query_def.get("category", ""),
        "visualization": query_def.get("visualization", "table"),
        "row_count": len(result.get("data", [])),
        "best_for": query_def.get("best_for", "")
    }
}
```

**AFTER (✅ FIXED):**
```python
# ✅ Convert DataFrame to JSON-serializable format
data_raw = result.get("data")
if isinstance(data_raw, pd.DataFrame):
    # Convert DataFrame to list of dicts (records orientation)
    data_json = data_raw.to_dict(orient='records')
    row_count = len(data_raw)
else:
    # Already a list or empty
    data_json = data_raw if data_raw else []
    row_count = len(data_json) if data_json else 0

return {
    "success": True,
    "query_name": query_name,
    "parameters_used": result.get("parameters_used", parameters or {}),
    "data": data_json,  # ✅ Now JSON serializable
    "metadata": {
        "description": query_def.get("description", ""),
        "category": query_def.get("category", ""),
        "visualization": query_def.get("visualization", "table"),
        "row_count": row_count,
        "best_for": query_def.get("best_for", "")
    }
}
```

**Add pandas import at top of file (Line 29):**
```python
import pandas as pd  # ✅ For DataFrame detection
```

---

### Solution 3: Fix Supabase Dependency - VERIFY INSTALLATION

**Option A: Pin gotrue explicitly in requirements.txt**
```txt
# Supabase with explicit gotrue version
gotrue==1.0.4
supabase==2.0.3
```

**Option B: Use alternative Supabase client**
```txt
# Use postgrest directly (lightweight)
postgrest-py>=0.10.0
```

**Option C: Verify import in wrapper**

Add defensive import check in `UI/modules_external/supabase/implementations/supabase_wrapper.py`:
```python
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError as e:
    print(f"[SUPABASE] Failed to import: {e}")
    print("[SUPABASE] Trying alternative import...")
    try:
        import supabase
        from supabase import create_client, Client
        SUPABASE_AVAILABLE = True
    except ImportError:
        SUPABASE_AVAILABLE = False
        print("[SUPABASE] All imports failed - tools unavailable")
```

---

## 📋 Deployment Checklist

### Pre-Deployment (Local Testing)

- [ ] **Remove all hardcoded paths** from tool_use_agent.py
- [ ] **Verify Shopify calculators** are in `quote-calculator/backend/shopify_calculators/`
- [ ] **Add DataFrame serialization** to query_library_wrapper.py
- [ ] **Test execute_query_library** locally with 3+ queries
- [ ] **Verify supabase import** in Python console
- [ ] **Check requirements.txt** for version conflicts
- [ ] **Run `pip install -r requirements.txt`** in clean venv
- [ ] **Test InHouse tools** locally (should work now)

### Deployment (Render)

- [ ] **Push fixes** to `v10` branch (auto-deploys to Render)
- [ ] **Monitor build logs** for import errors
- [ ] **Check Render environment variables** (SUPABASE_URL, SUPABASE_KEY)
- [ ] **Verify 77 queries load** in registry on startup
- [ ] **Test execute_query_library** via AI agent
- [ ] **Test calculator tools** (should still work)
- [ ] **Check InHouse SQL tools** (should now work)

### Post-Deployment (Verification)

- [ ] **Run test query** via AI: `execute_query_library("monthly_revenue_trend", {"months": 6})`
- [ ] **Verify JSON response** contains array of objects (not DataFrame)
- [ ] **Test InHouse SQL execution** via AI
- [ ] **Check Supabase connection** via AI
- [ ] **Monitor error logs** for 24 hours
- [ ] **Document any remaining issues**

---

## 🎯 Expected Outcomes

### After Fixes Applied:

**InHouse SQL Tools:**
- ✅ `inhouse_execute_sql()` - **WORKING** (no hardcoded paths)
- ✅ `inhouse_get_query_library_catalog()` - **WORKING** (ToolUseAgent imports)

**Query Library Tools:**
- ✅ `execute_query_library()` - **WORKING** (DataFrame → JSON conversion)
- ✅ All 77 queries return data successfully

**Supabase Tools:**
- ✅ `supabase_query()` - **WORKING** (dependency resolved)
- ✅ Stock data accessible

**Calculator Tools:**
- ✅ `calculate_business_cards()` - **STILL WORKING** (no changes needed)
- ✅ All 54 calculators functional

---

## 🔍 Testing Commands

### Local Testing:

```bash
# 1. Test InHouse SQL import
cd AI_infrastructure
python -c "from UI.modules_external.quote-calculator.backend.tool_use_agent import ToolUseAgent; print('✅ Import successful')"

# 2. Test query execution
cd AI_infrastructure
python -c "
from tools.registry_v3 import RegistryV3
r = RegistryV3()
result = r.execute_tool('execute_query_library', query_name='monthly_revenue_trend', parameters={'months': 6})
print('✅ Query executed')
print(f'Rows returned: {result['metadata']['row_count']}')
"

# 3. Test Supabase import
python -c "from supabase import create_client, Client; print('✅ Supabase available')"
```

### Render Testing (After Deploy):

```bash
# Check Render logs for startup messages
# Look for:
# ✅ "Registry V3 initialized with X tools"
# ✅ "QueryLibrary: 77 queries loaded"
# ✅ "InHouse Print module loaded successfully"
```

### AI Agent Testing:

Ask the AI agent:
1. "Run the monthly revenue trend query for the last 6 months"
2. "Execute SQL: SELECT TOP 10 * FROM Orders"
3. "Get stock levels from Supabase"

---

## 📊 Summary

| Issue | Status | Priority | Effort | Impact |
|-------|--------|----------|--------|--------|
| Hardcoded paths in tool_use_agent.py | 🔴 Critical | P0 | 30 min | High - Blocks all InHouse tools |
| DataFrame serialization | 🔴 Critical | P0 | 15 min | High - Blocks query results |
| Supabase dependency | 🟡 Important | P1 | 30 min | Medium - Blocks stock data |
| DB tools under construction | 🟢 Minor | P3 | 0 min | Low - Duplicate tools exist |

**Total Fix Time:** ~1-2 hours  
**Deployment Risk:** Low (fixes are isolated, no breaking changes)  
**Testing Required:** Moderate (test InHouse + Query tools)

---

## 🚀 Next Steps

1. **Apply Solution 1** - Remove hardcoded paths (30 minutes)
2. **Apply Solution 2** - Fix DataFrame serialization (15 minutes)
3. **Test locally** - Verify all tools work (30 minutes)
4. **Deploy to Render** - Push to v10 branch (auto-deploy)
5. **Verify production** - Test via AI agent (15 minutes)
6. **Monitor logs** - Watch for errors (24 hours)
7. **Apply Solution 3** - Fix Supabase if still failing (30 minutes)

**Estimated Total Time:** 2-3 hours including testing and deployment.
