# Plugin System Quick Reference

**Date:** November 4, 2025  
**Status:** Ready to Use ✅  
**Purpose:** Quick lookup for plugin system features

---

## 🚀 30-Second Summary

Your modules can now provide:

1. **AI Tools** - Things AI agents can discover and use
2. **Flask Routes** - HTTP endpoints for external access
3. **Both together** - Complete backend integration

**No manual registration needed!** Just drop files in the right folders.

---

## 📁 Folder Structure (Quick Copy/Paste)

```
UI/external/modules/your-module/
├── manifest.json
├── your-module.js
├── your-module.css
│
├── schema/                           ← AI TOOLS
│   └── your_tools.json
│
├── implementations/                  ← AI TOOLS  
│   ├── __init__.py
│   └── your_wrapper.py
│
└── routes/                           ← FLASK ROUTES
    ├── __init__.py
    └── your_routes.py
```

---

## 🎯 What Goes Where?

| Folder | Purpose | File Type | Example |
|--------|---------|-----------|---------|
| `schema/` | Define AI tools | JSON | `calculator_tools.json` |
| `implementations/` | Implement AI tools | Python | `calculator_wrapper.py` |
| `routes/` | Define HTTP endpoints | Python/Flask | `calculator_routes.py` |

---

## ⚡ Quick Checklist

### To Add AI Tools:
- [ ] Create `schema/{name}_tools.json` (define tools)
- [ ] Create `implementations/{name}_wrapper.py` (implement functions)
- [ ] Create `implementations/__init__.py` (empty file)
- [ ] Test: `python tools/plugins/module_plugin_loader.py`
- [ ] Restart: `BISTART`

### To Add Flask Routes:
- [ ] Create `routes/{name}_routes.py` (define endpoints)
- [ ] Create `routes/__init__.py` (export blueprint)
- [ ] Test: `python AI_infrastructure/core/module_blueprint_loader.py`
- [ ] Restart: `BISTART`
- [ ] Test endpoint: `curl http://localhost:5001/api/your-module/endpoint`

---

## 📖 Full Documentation

| Document | Read When | Topics |
|----------|-----------|--------|
| `PLUGIN_SYSTEM_GUIDE.md` | **Always first!** | Complete plugin tutorial with examples |
| `MODULE_BEST_PRACTICES.md` | Before coding | Best practices for all modules |
| `STOCK_MANAGEMENT_ASSESSMENT.md` | Evaluating features | Assessment of existing module |
| `README.md` | Getting oriented | Overview of all docs |
| `Instructions.md` | Specific questions | Technical deep dives |

---

## 🛠️ Tools & Commands

```powershell
# Discover AI tools from modules
python tools/plugins/module_plugin_loader.py

# Discover Flask routes from modules  
python AI_infrastructure/core/module_blueprint_loader.py

# Validate module structure
python scripts/maintenance/validate_modules.py

# Restart Flask (picks up new tools/routes)
BISTART

# Test AI tool
CHAT "Use my module to do something"

# Test Flask route
curl -X POST http://localhost:5001/api/my-module/endpoint
```

---

## 📋 File Templates

### JSON Schema Template

```json
{
  "platform": "my_module",
  "description": "What my module does",
  "tools": [
    {
      "name": "my_function",
      "description": "What this does",
      "platform": "my_module",
      "parameters": {
        "type": "object",
        "properties": {
          "param1": {"type": "string", "description": "..."}
        },
        "required": ["param1"]
      },
      "returns": {"type": "object", "description": "..."}
    }
  ]
}
```

### Python Implementation Template

```python
def my_function(param1: str, **kwargs) -> dict:
    """Implementation of my_function"""
    try:
        # Your code here
        return {"success": True, "result": "..."}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Flask Route Template

```python
from flask import Blueprint, request, jsonify
from my_wrapper import my_function

my_module_bp = Blueprint('my_module', __name__, url_prefix='/api/my-module')

@my_module_bp.route('/endpoint', methods=['POST'])
def api_my_endpoint():
    data = request.get_json()
    result = my_function(data.get('param1'))
    return jsonify(result), 200 if result['success'] else 400
```

---

## 🎯 Three-Phase Implementation

### Phase 1: AI Tools (1 day)
- [ ] Create schema/ folder
- [ ] Define tool schemas (JSON)
- [ ] Implement wrapper functions (Python)
- [ ] Test with module_plugin_loader.py

### Phase 2: Flask Routes (1 day)
- [ ] Create routes/ folder
- [ ] Define Flask blueprints
- [ ] Update UI to use HTTP if needed
- [ ] Test with curl

### Phase 3: Advanced Features (2+ days)
- [ ] Add analytics tools
- [ ] Add complex calculations
- [ ] Optimize database queries
- [ ] Add authentication

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Tools not appearing | Run: `python tools/plugins/module_plugin_loader.py` |
| Routes not working | Run: `python AI_infrastructure/core/module_blueprint_loader.py` |
| Import errors | Check sys.path setup in wrapper files |
| "Module not found" | Restart Flask with `BISTART` |
| JSON invalid | Use JSONLint to validate schema files |

---

## ✅ Success Checklist

Your module is ready when:

- [ ] Schema files are valid JSON
- [ ] Implementation functions have `**kwargs`
- [ ] Flask blueprints export properly in `__init__.py`
- [ ] `python module_plugin_loader.py` shows your tools
- [ ] `python module_blueprint_loader.py` shows your routes
- [ ] `BISTART` completes without errors
- [ ] `CHAT "use my tool"` works
- [ ] `curl http://localhost:5001/api/my-module/endpoint` works

---

## 🔗 Links

- **Full Guide:** `UI/module_development/PLUGIN_SYSTEM_GUIDE.md`
- **Best Practices:** `UI/module_development/MODULE_BEST_PRACTICES.md`
- **Assessment:** `UI/module_development/STOCK_MANAGEMENT_ASSESSMENT.md`
- **Example Module:** `UI/external/modules/quote-calculator/`
- **Testing Suite:** `test_module_architecture.py`

---

## 💡 Key Concepts

### Auto-Discovery
Files in the right folders are automatically loaded:
```
schema/*.json → AI tools defined
implementations/*.py → AI tools implemented  
routes/*.py → Flask routes registered
```

### Namespace
Each tool/route is namespaced:
```
Tool: my_module_my_function
Route: /api/my-module/endpoint
```

### No Breaking Changes
Existing modules continue to work unchanged. Plugin support is optional enhancement!

---

## 🎓 One-Minute Example

**Goal:** Let AI calculate something

**Step 1:** Create schema
```json
// schema/calc_tools.json
{
  "tools": [{
    "name": "my_calculate",
    "description": "Calculate total",
    "parameters": {
      "type": "object",
      "properties": {"amount": {"type": "number"}}
    }
  }]
}
```

**Step 2:** Implement function
```python
# implementations/calc_wrapper.py
def my_calculate(amount: float, **kwargs) -> dict:
    return {"success": True, "result": amount * 2}
```

**Step 3:** Test
```powershell
BISTART
CHAT "Calculate 50"
```

**Done!** 🎉

---

**Last Updated:** November 4, 2025  
**Status:** Ready for Production  
**Maintained By:** AI Agents Platform Team
