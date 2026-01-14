# Module Deployment Configuration - Quick Start

**Created:** December 16, 2025  
**Status:** ✅ Implementation Complete

---

## 🎯 What Was Done

Implemented **environment-based module filtering** to selectively disable modules for Render deployment while keeping them active locally.

---

## 📁 Files Created/Modified

### ✅ New Files Created

1. **`AI_infrastructure/config/__init__.py`**
   - Makes config directory a Python package

2. **`AI_infrastructure/config/deployment_config.py`** (150 lines)
   - Environment detection (local/Render/production)
   - Module filtering configuration
   - Public API: `is_module_enabled()`, `get_disabled_modules()`

3. **`test_deployment_config.py`** (220 lines)
   - Comprehensive test suite
   - Environment simulation
   - Module registry verification

4. **`MODULE_DEPLOYMENT_CONFIGURATION_GUIDE.md`** (550 lines)
   - Complete documentation
   - Module inventory
   - Implementation guide
   - Testing procedures

### ✅ Files Modified

1. **`AI_infrastructure/core/module_registry.py`**
   - Added import: `from AI_infrastructure.config.deployment_config import is_module_enabled`
   - Added filter check before module registration (line ~315)
   - Modules failing `is_module_enabled()` check are skipped

---

## 🚀 How to Use

### **Local Development** (Default)
```bash
# No environment variables needed
python AI_infrastructure/flask_app.py
```
**Result:** All modules load normally

### **Render Deployment**
Set environment variables in Render dashboard:
```
RENDER = true
FLASK_ENV = production
```
**Result:** Heavy/demo modules automatically disabled

### **Custom Configuration**
Edit `AI_infrastructure/config/deployment_config.py`:
```python
RENDER_DISABLED_MODULES = [
    'parametric-cad',      # Heavy CAD
    'veterinary_alerts',   # Deprecated
    'voip-demo',           # Demo
    # Add more modules here...
]
```

---

## 📊 Default Configuration

### Disabled on Render
- ⏸️ `parametric-cad` (heavy CAD engine)
- ⏸️ `veterinary_alerts` (deprecated)
- ⏸️ `voip-demo` (demo only)

### Disabled in Production
- ⏸️ `debug-module` (development tools)

### Always Enabled
- ✅ All core internal modules (agents, synergy, thread-cards, etc.)
- ✅ Business modules (inhouse-kanban, github, etc.)

---

## 🧪 Testing

### Test Locally
```bash
# Run test suite
python test_deployment_config.py
```

Expected output:
```
💻 Local development - all modules enabled
✅ Current environment: LOCAL
   Disabled modules (0): (none - all modules enabled)
```

### Test Render Simulation
```powershell
# Simulate Render environment
$env:RENDER = "true"
$env:FLASK_ENV = "production"
python test_deployment_config.py
```

Expected output:
```
🌐 Render deployment detected - disabling 3 modules
✅ Current environment: RENDER
   Disabled modules (3):
   ⏸️  parametric-cad
   ⏸️  veterinary_alerts
   ⏸️  voip-demo
```

### Verify API
```bash
# Start Flask
python AI_infrastructure/flask_app.py

# Check loaded modules
curl http://localhost:5001/api/modules/list
```

Disabled modules should NOT appear in the response.

---

## 🔍 How It Works

### 1. Environment Detection
```python
IS_RENDER = os.environ.get('RENDER') == 'true'
IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production'
IS_LOCAL = not (IS_RENDER or IS_PRODUCTION)
```

### 2. Module Filtering
```python
def is_module_enabled(module_id):
    # Always enable core modules
    if module_id in ALWAYS_ENABLED_MODULES:
        return True
    
    # Check disabled list
    disabled = get_disabled_modules()
    return module_id not in disabled
```

### 3. Registry Integration
```python
# In module_registry.py initialize()
if not is_module_enabled(manifest.id):
    logger.info(f"⏸️  Skipping module '{manifest.id}'")
    continue  # Skip registration
```

### 4. Result
- Local: `is_module_enabled('parametric-cad')` → `True` → loads
- Render: `is_module_enabled('parametric-cad')` → `False` → skips

---

## 📋 Module Inventory

Run to see all modules:
```bash
python -c "from AI_infrastructure.core.module_registry import get_module_registry; r = get_module_registry(); r._ensure_initialized(); [print(f'{m.id} (v{m.version})') for m in r.get_all_modules()]"
```

---

## ✅ Deployment Checklist

### Before Deploying to Render

- [ ] Test locally: `python test_deployment_config.py`
- [ ] Verify disabled modules list in `deployment_config.py`
- [ ] Test Render simulation with environment variables
- [ ] Commit changes to Git
- [ ] Set Render environment variables:
  - `RENDER = true`
  - `FLASK_ENV = production`
- [ ] Deploy to Render
- [ ] Verify logs show disabled modules
- [ ] Test API `/api/modules/list` shows correct modules

---

## 🎨 Customization

### Add More Modules to Disable
Edit `deployment_config.py`:
```python
RENDER_DISABLED_MODULES = [
    'parametric-cad',
    'veterinary_alerts',
    'voip-demo',
    'your-module-here',  # Add your module
]
```

### Environment-Specific Config
```python
# Disable only on Render
if IS_RENDER:
    disabled.extend(['module-a', 'module-b'])

# Disable only on production (not Render)
if IS_PRODUCTION and not IS_RENDER:
    disabled.extend(['module-c'])
```

### Always Enable Module
```python
ALWAYS_ENABLED_MODULES = [
    'agents',
    'synergy',
    'your-critical-module',  # Add here
]
```

---

## 📞 Quick Commands

```bash
# Check environment
python -c "from AI_infrastructure.config.deployment_config import get_environment_name; print(get_environment_name())"

# List disabled modules
python -c "from AI_infrastructure.config.deployment_config import get_disabled_modules; print(get_disabled_modules())"

# Check specific module
python -c "from AI_infrastructure.config.deployment_config import is_module_enabled; print('parametric-cad enabled:', is_module_enabled('parametric-cad'))"

# Get stats
python -c "from AI_infrastructure.config.deployment_config import get_module_filter_stats; import json; print(json.dumps(get_module_filter_stats(), indent=2))"
```

---

## 🚨 Troubleshooting

### Module still loading on Render
1. Check Render environment variables set correctly
2. Verify module ID matches exactly in `RENDER_DISABLED_MODULES`
3. Check Flask startup logs for "⏸️ Skipping module..." messages

### Module not loading locally
1. Ensure no environment variables set (`RENDER`, `FLASK_ENV`)
2. Check module not in `ALWAYS_DISABLED_MODULES`
3. Verify module manifest exists and is valid

### Changes not taking effect
1. Restart Flask server
2. Clear Python bytecode: `Remove-Item -Recurse AI_infrastructure/__pycache__`
3. Check for import errors in deployment_config.py

---

## 📚 Related Documentation

- **`MODULE_DEPLOYMENT_CONFIGURATION_GUIDE.md`** - Full guide
- **`AI_infrastructure/config/deployment_config.py`** - Configuration file
- **`test_deployment_config.py`** - Test suite

---

## ✨ Summary

**Before:** All modules load everywhere (heavy, slow)  
**After:** Smart filtering based on environment (lean, fast)

**Local:** All modules enabled ✅  
**Render:** Heavy/demo modules disabled ⏸️  
**Production:** Debug modules disabled ⏸️  

**Configuration:** Single file (`deployment_config.py`)  
**Control:** Environment variables (`RENDER`, `FLASK_ENV`)  
**Testing:** Automated test suite (`test_deployment_config.py`)  

🚀 Ready to deploy!
