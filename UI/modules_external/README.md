# External Modules Directory

## 🎯 Purpose

This directory contains **business modules** that are dynamically loaded and provide optional functionality to the AI Agents Platform.

---

## 📁 Directory Structure

```
modules_external/
├── inhouse-kanban/           📊 InHouse Kanban board
├── quote-calculator/         💰 Print quote calculator
├── communication-hub/        💬 Communication dashboard
├── shopify/                  🛍️ Shopify integration
├── salesforce/               💼 Salesforce integration
├── xero/                     📈 Xero accounting integration
├── database-visualizer/      🗄️ Database visualization
├── github/                   🐙 GitHub management
└── [other business modules]
```

---

## 🔧 What Goes Here

**External modules are:**

- Optional business features
- Dynamically loaded on-demand
- Can be enabled/disabled per user
- Require `manifest.json` for discovery
- Have floating toggles and/or sidebars
- Integrate with external services

**Examples:**
- InHouse Kanban board
- Quote Calculator
- Communication Hub
- Shopify/Salesforce/Xero integrations
- Business-specific tools

---

## 🚫 What Does NOT Go Here

**Core platform components** should go in **`../modules_internal/`** instead:

- Authentication system
- Module loader
- Sidebar framework
- Core UI components
- Always-loaded functionality

---

## 📋 Module Requirements

Each module in this directory **MUST have**:

### 1. manifest.json (Required)

```json
{
  "id": "my-module",
  "name": "My Module",
  "version": "1.0.0",
  "description": "What this module does",
  "icon": "fas fa-cube",
  "color": "#3B82F6",
  "main_tab": true,
  "main_tab_id": "my-module",
  "floating_toggle": true,
  "floating_toggle_opens_sidebar": true,
  "sidebar": {
    "enabled": true,
    "html_file": "my-module-sidebar.html",
    "position": "right",
    "width": "500px"
  },
  "html_file": "my-module-main.html",
  "js_file": "my-module.js",
  "css_file": "my-module.css"
}
```

### 2. Required Files (Based on manifest)

- **HTML file** (if `html_file` specified)
- **JavaScript file** (if `js_file` specified)
- **CSS file** (if `css_file` specified)
- **Sidebar HTML** (if `sidebar.enabled: true`)

### 3. Module Structure Example

```
my-module/
├── manifest.json              ✅ Required
├── my-module-main.html        📄 Main tab content
├── my-module-sidebar.html     🚪 Sidebar content
├── my-module.js               📜 Module logic
├── my-module.css              🎨 Module styles
└── README.md                  📚 Module documentation
```

---

## 🔍 How Modules are Discovered

1. **Backend Registry** (AI_infrastructure/flask_app.py):
   - Scans `UI/modules_external/` directory
   - Reads all `manifest.json` files
   - Registers modules in registry

2. **Frontend Loader** (UI/modules_internal/module_loader.js):
   - Fetches module list from backend
   - Dynamically loads HTML/CSS/JS files
   - Creates floating toggles
   - Initializes sidebars

3. **AI Tool Discovery** (tools/plugins/module_plugin_loader.py):
   - Scans `UI/modules_external/` for AI tools
   - Looks for `schema/` and `implementations/` folders
   - Registers tools with AI agent

---

## 📝 Naming Convention

- **Directory:** `modules_external/` (clearly indicates optional modules)
- **Old name:** `external/modules/` (renamed for clarity Nov 29, 2025)
- **Reason:** Make it clear these are separate from core platform

---

## 🚀 Loading Process

### Step 1: Module Discovery (Backend)
```python
# AI_infrastructure/flask_app.py
registry.initialize(str(base_dir / 'UI' / 'modules_external'))
```

### Step 2: Module Loading (Frontend)
```javascript
// UI/modules_internal/module_loader.js
await window.moduleLoader.loadModule('my-module');
```

### Step 3: Assets Loading
```javascript
// Loads from modules_external/{moduleId}/{filename}
fetch('modules_external/my-module/my-module.html')
fetch('modules_external/my-module/my-module.js')
fetch('modules_external/my-module/my-module.css')
```

---

## 🎯 Creating a New Module

### Quick Start

1. **Create module directory:**
   ```powershell
   mkdir UI\modules_external\my-module
   ```

2. **Create manifest.json:**
   ```json
   {
     "id": "my-module",
     "name": "My Module",
     "version": "1.0.0",
     "main_tab": true,
     "floating_toggle": true,
     "html_file": "my-module.html",
     "js_file": "my-module.js",
     "css_file": "my-module.css"
   }
   ```

3. **Create module files:**
   - `my-module.html` - UI structure
   - `my-module.js` - Module logic
   - `my-module.css` - Styling

4. **Restart Flask:**
   ```powershell
   BISTART
   ```

5. **Module auto-discovered and loaded!** ✅

---

## 🔗 Related Directories

- **`../modules_internal/`** - Core platform components
- **`../../frontend/modules_ARCHIVED/`** - Old unused code

---

## 📚 Documentation

- See `MODULE_CLEANUP_REORGANIZATION_NOV29.md` for reorganization details
- See `MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md` for full architecture
- See `MODULE_SYSTEM_INTEGRATION_GUIDE.md` for integration guide

---

## 🧪 Example Modules

### InHouse Kanban (`inhouse-kanban/`)
- Production workflow management
- Floating toggle opens sidebar
- Full Kanban board in main tab

### Quote Calculator (`quote-calculator/`)
- Print quote calculations
- Integrates with In_House_SQL database
- Calculator tools for AI agents

### Communication Hub (`communication-hub/`)
- Unified communication dashboard
- WhatsApp, email, SMS integration
- Conversation management

---

## ⚠️ Important Notes

1. **Path Changes (Nov 29, 2025):**
   - Old: `external/modules/` 
   - New: `modules_external/`
   - All code updated automatically

2. **Backward Compatibility:**
   - Modules don't need changes (manifests use relative paths)
   - Frontend loader updated to use new paths
   - Backend registry scans new location

3. **Adding AI Tools:**
   - Create `schema/` folder with JSON tool definitions
   - Create `implementations/` folder with Python code
   - Tools auto-discovered by module_plugin_loader.py

---

**Last Updated:** November 29, 2025  
**Status:** ✅ Active Business Modules Directory
