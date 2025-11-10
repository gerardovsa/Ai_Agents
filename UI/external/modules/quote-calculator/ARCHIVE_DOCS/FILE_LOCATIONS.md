# Quote Calculator Module - File Locations

**Complete file organization after reorganization - October 30, 2025**

---

## ✅ SELF-CONTAINED MODULE

All calculator module files are now properly organized in one location:

```
C:\Users\gpoli\GIT\AI_agents\UI\external\modules\calculator-module\
```

---

## 📂 Module Files (Frontend)

### Core Module Files
```
calculator-module/
├── manifest.json               ← Module configuration (colors, tools, sub-tabs)
├── quote-calculator.js         ← JavaScript module class (512 lines)
├── quote-calculator.css        ← Pastel orange styles (500+ lines)
└── MODULE_REORGANIZATION_COMPLETE.md ← This reorganization summary
```

### AI Tool Schemas
```
calculator-module/tools/
├── manifest.json               ← Tool registry metadata
└── calculator-tools.json       ← 7 calculator tool definitions
```

### Documentation (Reference)
```
calculator-module/
├── ARCHITECTURE_DIAGRAM.md     ← Visual system architecture
├── CONVERSION_PLAN.md          ← Implementation roadmap
├── INTEGRATION_GUIDE.md        ← Integration instructions
├── FILE_MAPPING.md             ← Complete file inventory
└── COPY_COMPLETE_SUMMARY.md    ← Original copy summary
```

### Original Source Code (Reference Only - DO NOT MODIFY)
```
calculator-module/ORIGINAL/
├── complete_calculator_implementation.py  ← GOD calculator (331 KB)
├── tool_use_agent.py                      ← AI agent (164 KB)
├── query_library.py                       ← Database queries (228 KB)
├── db_connector.py                        ← Database connection (13 KB)
└── shopify_calculators/                   ← 9 Shopify calculators
    ├── business_card_calculator_shopify.py
    ├── corflute_calculator_shopify.py
    ├── EconomicalBusinessCards_Shopify_Calculator.py
    ├── FoldedFlyers_Shopify_Calculator.py
    ├── PerfectBound_Shopify_Calculator.py
    ├── PremiumBusinessCards_Shopify_Calculator.py
    ├── SpiralBound_Shopify_Calculator.py
    └── WireBound_Shopify_Calculator.py
```

---

## 🔌 Flask API (Backend)

### Flask Route File
```
C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\
└── quote_calculator_routes.py  ← 7 API endpoints (219 lines)
```

**Endpoints:**
- `GET /api/quote-calculator/health`
- `POST /api/quote-calculator/business-cards`
- `GET /api/quote-calculator/stock-list`
- `GET /api/quote-calculator/finish-options`
- `POST /api/quote-calculator/flyers` (not implemented)
- `POST /api/quote-calculator/perfect-bound-books` (not implemented)
- `POST /api/quote-calculator/booklets` (not implemented)

### Flask App Registration
```
C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\
└── flask_app.py  ← Line 98: from routes.quote_calculator_routes import quote_calc_bp
                     Line 113: app.register_blueprint(quote_calc_bp)
```

---

## 🎯 SOURCE OF TRUTH (In_House_SQL)

### Working Calculator Code (DO NOT COPY - IMPORT DIRECTLY)
```
C:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator\
└── shopify_calculators\
    └── business_card_calculator_shopify.py  ← ACTUAL WORKING CODE (18.9 KB)
```

**This is the source code that Flask imports from.**  
**All modifications should be made here in the In_House_SQL project.**

### Import Path in Flask Route
```python
# quote_calculator_routes.py lines 14-21
in_house_sql_root = 'C:/Users/gpoli/GIT/In_House_SQL'
quote_calc_path = os.path.join(in_house_sql_root, 'G_Folder', 'Quote_Calculator')
shopify_calc_path = os.path.join(quote_calc_path, 'shopify_calculators')

sys.path.insert(0, shopify_calc_path)

from business_card_calculator_shopify import (
    ShopifyBusinessCardCalculator,
    PrintType,
    FinishSize,
    StockTypeStandard,
    StockTypePremium,
    CelloglazePremium
)
```

---

## 🔄 Module Registration

### Main Modules Manifest
```
C:\Users\gpoli\GIT\AI_agents\UI\external\modules\
└── manifest.json  ← Lines 40-48: quote-calculator module entry
```

```json
{
  "id": "quote-calculator",
  "name": "Quote Calculator",
  "icon": "fas fa-calculator",
  "color": "#ffb347",
  "manifestPath": "external/modules/calculator-module/manifest.json",
  "scriptPath": "external/modules/calculator-module/quote-calculator.js",
  "enabled": true
}
```

---

## 🎨 CSS Loading

### Automatic CSS Injection
```javascript
// quote-calculator.js lines 63-72
loadStylesheet() {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'external/modules/calculator-module/quote-calculator.css';
    link.id = 'quote-calculator-styles';
    document.head.appendChild(link);
    console.log('[OK] Quote Calculator stylesheet loaded');
}
```

**CSS File Path:**
```
external/modules/calculator-module/quote-calculator.css
```

---

## 📊 File Size Summary

### Module Files
| File | Size | Lines | Purpose |
|------|------|-------|---------|
| manifest.json | 6.7 KB | 177 | Module config |
| quote-calculator.js | 22.9 KB | 512 | Frontend logic |
| quote-calculator.css | 9.5 KB | 500+ | Styles |
| quote_calculator_routes.py | 8.3 KB | 219 | Flask API |
| calculator-tools.json | 15.8 KB | 398 | Tool schemas |
| **TOTAL (Active)** | **63.2 KB** | **1,806** | Working code |

### Reference Files (ORIGINAL/)
| Category | Size | Purpose |
|----------|------|---------|
| Python calculators | 1.2 MB | Reference implementations |
| JSON configs | 180 KB | Shopify DPO configs |
| Documentation | 150 KB | Technical docs |
| **TOTAL (Reference)** | **1.5 MB** | Read-only reference |

---

## 🚫 DELETED Files (Cleanup Complete)

### Removed During Reorganization
```
❌ C:\Users\gpoli\GIT\AI_agents\UI\external\modules\quote-calculator\
   (Entire folder deleted - was duplicate location)
```

### No Longer Needed
- Old quote_calculator_routes.py in wrong location (moved to AI_infrastructure/routes)
- Duplicate manifest.json files (consolidated)
- Scattered CSS files (consolidated into one)

---

## ✅ CORRECT File Flow

### 1. User Opens UI
```
Browser → http://localhost:5001
       → UI/business-ai-platform-v2.html
       → Loads: UI/external/modules/manifest.json
       → Registers: calculator-module
       → Loads: calculator-module/quote-calculator.js
       → Injects: calculator-module/quote-calculator.css
```

### 2. User Calculates Quote
```
Browser → quote-calculator.js (calculateBusinessCards)
       → Fetch: POST /api/quote-calculator/business-cards
       → Flask: AI_infrastructure/routes/quote_calculator_routes.py
       → Import: In_House_SQL/.../business_card_calculator_shopify.py
       → Return: JSON with quote
       → Display: quote-calculator.js (renderQuoteResult)
```

### 3. CSS Applied
```
Browser → calculator-module/quote-calculator.js (loadStylesheet)
       → Injects: <link href="calculator-module/quote-calculator.css">
       → Applies: Pastel orange theme (#ffb347)
```

---

## 🔍 How to Find Files

### Need to modify UI?
→ `calculator-module/quote-calculator.js`

### Need to modify styles?
→ `calculator-module/quote-calculator.css`

### Need to add API endpoint?
→ `AI_infrastructure/routes/quote_calculator_routes.py`

### Need to modify calculator logic?
→ `In_House_SQL/G_Folder/Quote_Calculator/shopify_calculators/business_card_calculator_shopify.py`

### Need to add AI tool?
→ `calculator-module/tools/calculator-tools.json`

### Need to change module config?
→ `calculator-module/manifest.json`

---

## 📝 Quick Commands

### View Module Files
```powershell
Get-ChildItem C:\Users\gpoli\GIT\AI_agents\UI\external\modules\calculator-module
```

### Check Flask Route
```powershell
Get-Content C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\quote_calculator_routes.py | Select-Object -First 30
```

### Verify Source Code
```powershell
Test-Path C:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator\shopify_calculators\business_card_calculator_shopify.py
```

### Start Flask Server
```powershell
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
python flask_app.py
```

---

## ✅ VERIFICATION CHECKLIST

- [x] All module files in `calculator-module/` folder
- [x] Flask route in `AI_infrastructure/routes/`
- [x] Source code in `In_House_SQL/` (not copied)
- [x] Module registered in main manifest
- [x] CSS loading implemented in JavaScript
- [x] Old `quote-calculator/` folder deleted
- [x] Import paths point to In_House_SQL
- [x] No code duplication
- [x] Clean architecture maintained

---

**Last Updated:** October 30, 2025, 11:50 PM  
**Status:** ✅ COMPLETE - All files properly organized  
**Ready for:** End-to-end testing (Task 6)
