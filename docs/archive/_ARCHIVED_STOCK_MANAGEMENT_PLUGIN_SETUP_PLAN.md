# Stock-Management Module - Plugin System Setup

**Date:** November 4, 2025  
**Status:** Ready for Setup  
**Task:** Clean up and implement plugin folder structure

---

## 📊 Current State Analysis

### Files Found (17 items)
```
stock-management/
├── 🎨 Frontend Code
│   ├── stock-management.js (main)
│   ├── stock-management-enhanced.js (enhanced variant)
│   ├── stock-management.css
│   ├── TABLE_ENHANCEMENTS.js
│   └── ENHANCED_STOCK_TABLE.html
│
├── 📚 Documentation (7 files)
│   ├── manifest.json ✅
│   ├── README.md (NOT FOUND - needs check)
│   ├── IMPLEMENTATION_COMPLETE.md
│   ├── INTEGRATION_GUIDE.md
│   ├── INTEGRATION_CHECKLIST.md
│   ├── INTEGRATION_FEATURES_SUMMARY.md
│   ├── ENHANCEMENTS_COMPLETE.md
│   ├── README_TABLE_ENHANCEMENTS.md
│   └── TEST_ENHANCEMENTS.html
│
├── 🧪 Test/Demo Files
│   ├── VISUAL_DASHBOARD.html
│   ├── TEST_ENHANCEMENTS.html
│   └── USAGE_EXAMPLE.html
│
├── 🐍 Backend (Incomplete)
│   ├── stock_routes.py (EXISTS but orphaned)
│   └── database-config.json
│
└── ❌ Plugin Folders MISSING
    ├── schema/ (NOT FOUND)
    ├── implementations/ (NOT FOUND)
    └── routes/ (NOT FOUND)
```

---

## ⚙️ Current Issue: `stock_routes.py` is orphaned

**Problem:**
- `stock_routes.py` exists in root of module
- It's NOT in a `routes/` folder
- It's NOT auto-discoverable by module_blueprint_loader
- It's NOT being registered with Flask

**Result:** 
- Flask doesn't know about the routes
- Routes are not available at `/api/stock-management/*`

---

## ✅ Solution: Implement Plugin Structure

### Step 1: Organize Flask Routes

Move `stock_routes.py` into proper plugin folder:

```
Before:
stock-management/
├── stock_routes.py          ← Orphaned, not auto-discovered
├── stock-management.js
└── ...

After:
stock-management/
├── routes/                  ← NEW: Auto-discovered folder
│   ├── __init__.py         ← Export blueprint
│   └── stock_routes.py     ← Moved here
├── stock-management.js
└── ...
```

### Step 2: Read & Adapt stock_routes.py

Before moving, we need to:
1. Read current `stock_routes.py`
2. Check if it exports a Flask blueprint
3. Adapt it if needed for module_blueprint_loader discovery
4. Place in `routes/` folder

### Step 3: Create schema/ and implementations/ (Optional Phase)

For Phase 1 (quick win):
```
stock-management/
├── schema/                         ← NEW: AI tools
│   └── stock_tools.json           (3 tools: get_items, get_status, get_alerts)
├── implementations/                ← NEW: AI tool implementations
│   ├── __init__.py
│   └── stock_wrapper.py           (3 functions)
└── routes/                         ← Already done above
    ├── __init__.py
    └── stock_routes.py
```

---

## 🎯 What Needs to Happen

### IMMEDIATE (Today):
1. ✅ **Read** `stock_routes.py` to understand current Flask setup
2. ✅ **Create** `routes/` folder
3. ✅ **Move** `stock_routes.py` into `routes/`
4. ✅ **Create** `routes/__init__.py` with blueprint export
5. ✅ **Test** that Flask discovers the routes (BISTART)

### OPTIONAL (Later - Phase 1 Plugin Support):
6. Create `schema/` folder with 3 stock tools
7. Create `implementations/` folder with wrapper functions
8. Test with `python tools/plugins/module_plugin_loader.py`

---

## 🗑️ Cleanup Tasks

### Files to Keep:
- ✅ `manifest.json` - Module config
- ✅ `stock-management.js` - Main UI
- ✅ `stock-management-enhanced.js` - Enhanced variant
- ✅ `stock-management.css` - Styles
- ✅ Documentation files
- ✅ Test files
- ✅ `stock_routes.py` - MOVE TO routes/ folder

### Files to Delete or Archive:
- ❓ `__pycache__/` - Cache (auto-removed when not used)
- ❓ `database-config.json` - Check if still needed
- ❓ `ENHANCED_STOCK_TABLE.html` - Duplicate? Check

### Files to Verify:
- Check if `README.md` exists in stock-management root
- If not, create one summarizing features

---

## 📋 Step-by-Step Implementation

### Step 1: Check stock_routes.py

**File:** `UI/external/modules/stock-management/stock_routes.py`

Need to verify:
- [ ] Does it define a Flask blueprint?
- [ ] Is it named properly?
- [ ] Does it have url_prefix set?
- [ ] Can we move it unchanged?

### Step 2: Create routes/ Folder Structure

```bash
# Create the folder
mkdir C:\Users\gpoli\GIT\AI_agents\UI\external\modules\stock-management\routes

# Create __init__.py
touch C:\Users\gpoli\GIT\AI_agents\UI\external\modules\stock-management\routes\__init__.py
```

### Step 3: Update __init__.py

**File:** `routes/__init__.py`

```python
"""
Stock Management Routes

FILE: UI/external/modules/stock-management/routes/__init__.py
PURPOSE: Export blueprint for auto-discovery
"""

from .stock_routes import stock_management_bp

__all__ = ['stock_management_bp']
```

### Step 4: Move stock_routes.py

Move from:
- `UI/external/modules/stock-management/stock_routes.py`

To:
- `UI/external/modules/stock-management/routes/stock_routes.py`

### Step 5: Test Blueprint Discovery

```powershell
cd c:\Users\gpoli\GIT\AI_agents
python AI_infrastructure\core\module_blueprint_loader.py

# Should show:
# ✅ [Module Blueprints] Discovered: stock-management
# 📦 Loading: stock-management
#   📄 Loaded: stock_routes.py
#   ✅ Registered: stock_management
```

### Step 6: Restart Flask

```powershell
BISTART
```

---

## 🎯 Success Criteria

### Immediate Success (Routes):
- [ ] `routes/` folder created
- [ ] `stock_routes.py` moved to `routes/`
- [ ] `routes/__init__.py` created and exports blueprint
- [ ] Flask restarts without errors
- [ ] Routes available at `/api/stock-management/*`
- [ ] Can call endpoints with curl/Postman

### Phase 1 Success (Optional - AI Tools):
- [ ] `schema/` folder created with `stock_tools.json`
- [ ] `implementations/` folder created with `stock_wrapper.py`
- [ ] 3+ tools discoverable with `python tools/plugins/module_plugin_loader.py`
- [ ] Tools callable from AI agent

---

## 📝 Command Reference

### Check module_blueprint_loader
```powershell
cd c:\Users\gpoli\GIT\AI_agents
python AI_infrastructure\core\module_blueprint_loader.py
```

### Check module_plugin_loader (after implementing schema/)
```powershell
cd c:\Users\gpoli\GIT\AI_agents
python tools\plugins\module_plugin_loader.py
```

### Restart Flask
```powershell
BISTART
```

### Test a route
```powershell
curl -X GET http://localhost:5001/api/stock-management/items
```

### Test an AI tool (after Phase 1)
```powershell
CHAT "Get my stock items"
```

---

## 🏗️ Final Structure (After Completion)

```
stock-management/
├── manifest.json
├── stock-management.js
├── stock-management-enhanced.js
├── stock-management.css
│
├── routes/                          ← NEW: Auto-discovered
│   ├── __init__.py
│   └── stock_routes.py             ← MOVED HERE
│
├── schema/                          ← OPTIONAL: Phase 1
│   └── stock_tools.json
│
├── implementations/                 ← OPTIONAL: Phase 1
│   ├── __init__.py
│   └── stock_wrapper.py
│
├── docs/
│   ├── manifest.json
│   ├── README.md
│   └── [other docs]
│
└── test/
    ├── VISUAL_DASHBOARD.html
    └── [other tests]
```

---

## 📊 Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| **Routes discoverable** | ❌ No | ✅ Yes |
| **Routes auto-registered** | ❌ No | ✅ Yes |
| **Routes location** | Orphaned | Organized |
| **Plugin-ready** | ❌ No | ✅ Yes |
| **AI tools** | ❌ No | ✅ Possible |
| **HTTP endpoints** | ❓ Unclear | ✅ Clear |

---

## ⚠️ Important Notes

### For `stock_routes.py` Move:
- Just move the file, no code changes needed
- Only update path in `__init__.py`
- The blueprint name should match: `stock_management_bp`

### For Tests After Move:
- Test that Flask still discovers routes
- Test that endpoints still work
- Test that no functionality is broken

### For Future Phase 1:
- Can add `schema/` and `implementations/` anytime
- No blocking dependencies
- Can be added incrementally

---

## ✅ Next Steps

**Recommended Order:**
1. Review current `stock_routes.py` content
2. Create `routes/` folder structure
3. Move `stock_routes.py` to `routes/`
4. Create and populate `routes/__init__.py`
5. Test with `python AI_infrastructure\core\module_blueprint_loader.py`
6. Restart Flask with `BISTART`
7. Verify routes work with curl
8. Consider Phase 1 AI tools (optional, later)

---

**Status:** ✅ Ready to Implement  
**Estimated Time:** 15 minutes (routes only)  
**Optional Phase 1:** 1 day (add AI tools)

