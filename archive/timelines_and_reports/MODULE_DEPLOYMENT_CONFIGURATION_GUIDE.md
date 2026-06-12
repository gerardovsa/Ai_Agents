# Module Deployment Configuration Guide

**Created:** December 16, 2025  
**Purpose:** Selectively disable modules for Render deployment while keeping them active locally

---

## 📋 Overview

Your AI_agents application has a **modular architecture** where modules can be dynamically loaded and managed. You want to:

1. ✅ **Local Development:** All modules enabled
2. ✅ **Render Production:** Specific modules disabled (to reduce deployment size, improve performance, or exclude features)

---

## 🗂️ Available Modules Inventory

### **Internal Modules** (`UI/modules_internal/`)
Core system modules (always loaded in HTML, not managed by ModuleRegistry):

| Module ID | Name | Purpose | Status |
|-----------|------|---------|--------|
| `agents` | AI Agents | Agent management system | Core (Always Active) |
| `automation` | Automation | Workflow automation | Core |
| `automation-workflows` | Automation Workflows | Workflow builder | Core |
| `communication-hub` | Communication Hub | Message center | Core |
| `debug-module` | Debug Module | Development debugging | **Development Only** |
| `internal-docs` | Internal Docs | Documentation viewer | Core |
| `messages` | Messages | Messaging system | Core |
| `notifications` | Notifications | Notification center | Core |
| `prompt-library` | Prompt Library | Prompt management | Core |
| `settings-sidebar` | Settings | User settings | Core |
| `synergy` | Synergy Sidebar | Left sidebar navigation | Core |
| `thread-cards` | Thread Cards | Thread management | Core |
| `thread-manager` | Thread Manager | Thread operations | Core |
| `transcription` | Transcription | Audio transcription | Core |
| `universal-search` | Universal Search | Global search | Core |
| `vector_database` | Vector Database | Vector DB management | Core |
| `woocommerce` | WooCommerce | E-commerce integration | Optional |
| `workflow` | Workflow | Workflow engine | Core |

### **External Modules** (`UI/modules_external/`)
Plug-and-play business modules (managed by ModuleRegistry):

| Module ID | Name | Purpose | Platforms Required | Disable for Render? |
|-----------|------|---------|-------------------|---------------------|
| `database-visualizer` | Database Visualizer | Schema visualization | None | ❌ Keep |
| `design_engineering` | Design Engineering | CAD/Engineering | None | ⚠️ Consider |
| `github` | GitHub Integration | GitHub API | GitHub | ❌ Keep |
| `inhouse-kanban` | InHouse Kanban | Project management | None | ❌ Keep |
| `inhouse-print` | InHouse Print | Print management | None | ❌ Keep |
| `parametric-cad` | Parametric CAD | CAD modeling | None | ✅ **Disable** (Heavy) |
| `quote-calculator` | Quote Calculator | Quote generation | None | ❌ Keep |
| `render-management` | Render Management | Render.com API | Render | ❌ Keep |
| `salesforce` | Salesforce | CRM integration | Salesforce | ⚠️ Consider |
| `shopify` | Shopify | E-commerce | Shopify | ⚠️ Consider |
| `stock-management` | Stock Management | Inventory | None | ❌ Keep |
| `veterinary_alerts` | Veterinary Alerts | VSA alerts (old) | None | ✅ **Disable** (Deprecated) |
| `vsa-veterinary-alerts` | VSA Alerts | Veterinary alerts (new) | None | ❌ Keep |
| `voip-demo` | VoIP Demo | Voice demo | None | ✅ **Disable** (Demo) |
| `xero` | Xero Accounting | Accounting integration | Xero | ⚠️ Consider |

**Recommendation:** Disable these for Render:
- ✅ `parametric-cad` - Heavy CAD engine (large files)
- ✅ `veterinary_alerts` - Deprecated (replaced by vsa-veterinary-alerts)
- ✅ `voip-demo` - Demo module (not production)
- ⚠️ `salesforce` - Only if not using Salesforce
- ⚠️ `shopify` - Only if not using Shopify
- ⚠️ `xero` - Only if not using Xero

---

## 🔧 Implementation Methods

### **Method 1: Environment-Based Module Filtering (RECOMMENDED)**

Add environment detection to module loading logic.

#### Step 1: Create Environment Config File

```python
# File: AI_infrastructure/config/deployment_config.py
"""
Deployment-specific configuration for module loading
"""
import os

# Detect deployment environment
IS_RENDER = os.environ.get('RENDER') == 'true'
IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production'
IS_LOCAL = not (IS_RENDER or IS_PRODUCTION)

# Modules to DISABLE on Render deployment
RENDER_DISABLED_MODULES = [
    'parametric-cad',      # Heavy CAD engine
    'veterinary_alerts',   # Deprecated module
    'voip-demo',           # Demo only
    # Uncomment to disable platform-specific modules:
    # 'salesforce',        # If not using Salesforce
    # 'shopify',           # If not using Shopify
    # 'xero',              # If not using Xero
]

# Modules to DISABLE in all production environments
PRODUCTION_DISABLED_MODULES = [
    'debug-module',        # Development debugging only
]

def get_disabled_modules():
    """Get list of modules to disable based on environment"""
    disabled = []
    
    if IS_RENDER:
        disabled.extend(RENDER_DISABLED_MODULES)
        print(f"🌐 Render deployment detected - disabling {len(RENDER_DISABLED_MODULES)} modules")
    
    if IS_PRODUCTION or IS_RENDER:
        disabled.extend(PRODUCTION_DISABLED_MODULES)
        print(f"🏭 Production environment - disabling debug modules")
    
    if IS_LOCAL:
        print("💻 Local development - all modules enabled")
    
    return list(set(disabled))  # Remove duplicates

def is_module_enabled(module_id):
    """Check if module should be enabled in current environment"""
    disabled = get_disabled_modules()
    enabled = module_id not in disabled
    
    if not enabled:
        print(f"⏸️  Module '{module_id}' disabled in this environment")
    
    return enabled
```

#### Step 2: Update Module Registry to Respect Environment Config

```python
# File: AI_infrastructure/core/module_registry.py

# Add import at top:
from AI_infrastructure.config.deployment_config import is_module_enabled

# Modify the initialize() method around line 200:

# In the module processing loop, add filter after loading manifest:
try:
    # ... existing manifest loading code ...
    
    # Create ModuleManifest object
    manifest = ModuleManifest(
        # ... existing fields ...
    )
    
    # ✅ NEW: Check if module should be enabled in this environment
    if not is_module_enabled(manifest.id):
        logger.info(f"⏸️  Skipping module {manifest.id} (disabled for this environment)")
        continue  # Skip registration
    
    # Register module (existing code)
    self.modules[manifest.id] = manifest
    # ... rest of registration ...
```

#### Step 3: Set Render Environment Variable

Add to your Render dashboard or `render.yaml`:

```yaml
# render.yaml
services:
  - type: web
    name: ai-agents
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python AI_infrastructure/flask_app.py"
    envVars:
      - key: RENDER
        value: "true"
      - key: FLASK_ENV
        value: "production"
```

Or in Render dashboard:
```
Environment Variables:
RENDER = true
FLASK_ENV = production
```

---

### **Method 2: Manifest-Based Disabling**

Add `enabled` field to each module's `manifest.json`.

#### Step 1: Update Module Manifests

```json
// File: UI/modules_external/parametric-cad/manifest.json
{
  "id": "parametric-cad",
  "name": "Parametric CAD",
  "version": "1.0.0",
  "enabled": false,  // ← Add this field
  // ... rest of manifest ...
}
```

#### Step 2: Module Registry Already Respects This

The module registry already filters disabled modules (line 91 in `module-loader-v4.js`):

```javascript
data.modules.forEach(module => {
    if (module.enabled !== false) {  // ✅ Already implemented
        this.modules.set(module.id, module);
    }
});
```

**Drawback:** Changes manifest files (must remember to re-enable for local dev).

---

### **Method 3: Deployment-Specific Manifest Override**

Create a deployment configuration that overrides module settings.

#### Step 1: Create Deployment Config JSON

```json
// File: AI_infrastructure/config/render_modules.json
{
  "disabled_modules": [
    "parametric-cad",
    "veterinary_alerts",
    "voip-demo"
  ],
  "module_overrides": {
    "parametric-cad": {
      "enabled": false
    },
    "veterinary_alerts": {
      "enabled": false
    },
    "voip-demo": {
      "enabled": false
    }
  }
}
```

#### Step 2: Load Config in Module Registry

```python
# File: AI_infrastructure/core/module_registry.py

def _load_deployment_overrides(self):
    """Load deployment-specific module overrides"""
    config_path = Path(__file__).parent.parent / "config" / "render_modules.json"
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get('disabled_modules', [])
    except Exception as e:
        logger.error(f"Failed to load deployment config: {e}")
        return []

# In initialize() method:
deployment_disabled = self._load_deployment_overrides()

# In module processing loop:
if manifest.id in deployment_disabled:
    logger.info(f"⏸️  Module {manifest.id} disabled by deployment config")
    continue
```

---

## 🚀 Recommended Approach

**Use Method 1 (Environment-Based)** because:

✅ **Clean separation** - Config separate from code  
✅ **No manifest changes** - Original manifests unchanged  
✅ **Easy to maintain** - Single file to edit  
✅ **Environment-aware** - Automatically detects Render  
✅ **Git-friendly** - No local vs production file conflicts  

---

## 📝 Step-by-Step Implementation (Method 1)

### 1. Create Config File

```bash
# Create config directory
mkdir -p c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\config

# Create __init__.py to make it a package
New-Item "c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\config\__init__.py" -ItemType File

# Create deployment config
# (Content from Method 1 above)
```

### 2. Update Module Registry

Edit `c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\core\module_registry.py`

Add import and filter check as shown in Method 1.

### 3. Set Render Environment

In Render dashboard → Environment → Add:
```
RENDER = true
FLASK_ENV = production
```

### 4. Test Locally

```bash
# Should load ALL modules
python AI_infrastructure/flask_app.py
```

Check console output:
```
💻 Local development - all modules enabled
```

### 5. Test Production Simulation

```bash
# Simulate Render environment
$env:RENDER = "true"
$env:FLASK_ENV = "production"
python AI_infrastructure/flask_app.py
```

Check console output:
```
🌐 Render deployment detected - disabling 3 modules
⏸️  Module 'parametric-cad' disabled in this environment
⏸️  Module 'veterinary_alerts' disabled in this environment
⏸️  Module 'voip-demo' disabled in this environment
```

### 6. Deploy to Render

```bash
git add .
git commit -m "Add environment-based module filtering for Render deployment"
git push origin main
```

Render will automatically:
1. Detect `RENDER=true` environment variable
2. Load deployment config
3. Skip disabled modules
4. Deploy leaner application

---

## 🧪 Testing & Verification

### Local Development Test
```python
# Run in Python console
from AI_infrastructure.config.deployment_config import get_disabled_modules, is_module_enabled

print("Disabled modules:", get_disabled_modules())
print("Is parametric-cad enabled?", is_module_enabled('parametric-cad'))
```

Expected output (local):
```
💻 Local development - all modules enabled
Disabled modules: []
Is parametric-cad enabled? True
```

### Production Simulation Test
```bash
$env:RENDER = "true"
python -c "from AI_infrastructure.config.deployment_config import get_disabled_modules; print(get_disabled_modules())"
```

Expected output:
```
🌐 Render deployment detected - disabling 3 modules
['parametric-cad', 'veterinary_alerts', 'voip-demo']
```

### API Test
```bash
# Start Flask
python AI_infrastructure/flask_app.py

# Call API
curl http://localhost:5001/api/modules/list
```

Check response - disabled modules should NOT appear in `modules` array.

---

## 📊 Impact Analysis

### Before (All Modules)
- **Modules Loaded:** ~20 external modules
- **Deployment Size:** Larger (includes CAD libraries, demo files)
- **Startup Time:** Slower (more modules to initialize)
- **Memory Usage:** Higher (unused modules loaded)

### After (Filtered Modules)
- **Modules Loaded:** ~17 external modules (3 disabled)
- **Deployment Size:** Smaller (excludes heavy modules)
- **Startup Time:** Faster (fewer modules)
- **Memory Usage:** Lower (only needed modules)

**Estimated Savings:**
- 🗜️ **Deployment size:** -15-20% (CAD libraries are heavy)
- ⚡ **Startup time:** -10-15% (fewer initializations)
- 💾 **Memory usage:** -5-10% (fewer loaded modules)

---

## 🔄 Future Enhancements

### 1. Per-Environment Configs
```python
# config/environments/local.py
DISABLED_MODULES = []

# config/environments/staging.py
DISABLED_MODULES = ['voip-demo']

# config/environments/production.py
DISABLED_MODULES = ['parametric-cad', 'veterinary_alerts', 'voip-demo']
```

### 2. Feature Flags (Database-Driven)
```python
# Load module config from database
def get_disabled_modules():
    # Query settings table for disabled modules
    conn = get_db_connection()
    result = conn.execute("SELECT module_id FROM module_settings WHERE enabled = false")
    return [row['module_id'] for row in result]
```

### 3. User-Specific Module Access
```python
# In module_routes.py
def get_available_modules(user_id):
    # Filter by user permissions
    user_modules = get_user_module_permissions(user_id)
    return [m for m in all_modules if m.id in user_modules]
```

---

## 📞 Quick Commands

```bash
# List all modules
python -c "from AI_infrastructure.core.module_registry import get_module_registry; r = get_module_registry(); r._ensure_initialized(); print([m.id for m in r.get_all_modules()])"

# Check disabled modules (local)
python -c "from AI_infrastructure.config.deployment_config import get_disabled_modules; print(get_disabled_modules())"

# Check disabled modules (Render simulation)
$env:RENDER = "true"; python -c "from AI_infrastructure.config.deployment_config import get_disabled_modules; print(get_disabled_modules())"

# Test module API
curl http://localhost:5001/api/modules/list | python -m json.tool
```

---

## ✅ Summary

**To disable modules for Render deployment:**

1. ✅ Create `AI_infrastructure/config/deployment_config.py` (see Method 1)
2. ✅ Update `AI_infrastructure/core/module_registry.py` to import and use `is_module_enabled()`
3. ✅ Set `RENDER=true` environment variable in Render dashboard
4. ✅ Deploy to Render

**Modules recommended to disable:**
- `parametric-cad` (heavy)
- `veterinary_alerts` (deprecated)
- `voip-demo` (demo only)

**Modules kept active:**
- All core internal modules
- All business modules you actively use

This approach gives you **full control** over which modules load in each environment while keeping your codebase clean and maintainable! 🚀
