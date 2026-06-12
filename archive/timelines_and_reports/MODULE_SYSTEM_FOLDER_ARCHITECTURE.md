# Module System Folder Architecture - Technical Specification

**Created:** November 26, 2025  
**Status:** Active Migration Plan  
**Purpose:** Complete technical documentation of module system folder structure for AI agents and developers

---

## 🎯 Executive Summary

The AI Agents platform has **THREE separate "modules" folders** serving different purposes, causing confusion. This document provides:

1. **Current state analysis** - Where modules exist today
2. **Technical architecture** - How the system works
3. **Migration strategy** - How to rebuild legacy modules without disruption
4. **Best practices** - Folder structure and naming conventions

**Key Decision:** Legacy modules in `UI/external/modules/` will remain in place during gradual migration to `frontend/modules/` production system.

---

## 📂 Current Folder Structure (As of Nov 26, 2025)

```
AI_agents/
│
├── frontend/modules/                      ← 🎯 PRODUCTION (Flask backend reads here)
│   ├── inhouse-kanban/                    ← ✅ Active production module
│   │   ├── manifest.json
│   │   ├── inhouse-kanban.html
│   │   ├── inhouse-kanban.js
│   │   └── inhouse-kanban-NEW.css
│   ├── inhouse-print/                     ← ✅ Active production module
│   ├── quote-calculator/                  ← ✅ Active production module
│   ├── vector_database/                   ← ✅ Active production module
│   └── module_loader.js                   ← Frontend loader (synchronized)
│
├── UI/external/modules/                   ← ⚠️ LEGACY (20+ modules, keep for rebuild)
│   ├── automation-workflows/              ← 🔄 To be rebuilt
│   ├── communication-hub/                 ← 🔄 To be rebuilt
│   ├── database-visualizer/               ← 🔄 To be rebuilt
│   ├── debug-module/                      ← 🔄 To be rebuilt
│   ├── inhouse-kanban/                    ← ⚠️ DUPLICATE (can archive after validation)
│   ├── inhouse-print/                     ← 🔄 To be rebuilt/validated
│   ├── production-analytics/              ← 🔄 To be rebuilt
│   ├── quote-calculator/                  ← 🔄 To be rebuilt/validated
│   ├── render-management/                 ← 🔄 To be rebuilt
│   ├── salesforce/                        ← 🔄 To be rebuilt
│   ├── settings-sidebar/                  ← 🔄 To be rebuilt
│   ├── shopify/                           ← 🔄 To be rebuilt
│   ├── stock-management/                  ← 🔄 To be rebuilt
│   ├── synergy/                           ← 🔄 To be rebuilt
│   ├── thread-cards/                      ← 🔄 To be rebuilt
│   ├── xero/                              ← 🔄 To be rebuilt
│   ├── manifest.json                      ← OLD registry system (deprecated)
│   ├── MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md
│   └── MODULE_SYSTEM_INTEGRATION_GUIDE.md
│
└── UI/modules/                            ← ⚠️ JAVASCRIPT UTILITIES (NOT plugin modules)
    ├── module_loader.js                   ← Frontend loader (synchronized with frontend/)
    ├── agents/                            ← JS utility code (agent UI components)
    ├── components/                        ← JS utility code (shared UI components)
    ├── prompt-library/                    ← JS utility code (prompt management)
    ├── settings-sidebar/                  ← JS utility code (settings UI)
    ├── shared/                            ← JS utility code (shared functions)
    ├── thread-manager/                    ← JS utility code (thread UI management)
    ├── transcription/                     ← JS utility code (transcription handling)
    ├── vector_database/                   ← ❓ Ambiguous (may be JS utility or module)
    └── woocommerce/                       ← ❓ Ambiguous (may be JS utility or module)
```

---

## 🔍 Technical Architecture - How It Works

### Backend Module Discovery (Flask)

**File:** `AI_infrastructure/core/module_registry.py`

```python
# Line 144-147
if modules_directory is None:
    base_dir = Path(__file__).parent.parent.parent  # AI_agents root
    modules_directory = os.path.join(base_dir, "frontend", "modules")

modules_directory = Path(modules_directory)
```

**Behavior:**
- Flask backend **ONLY** scans `frontend/modules/` directory
- Loads `manifest.json` from each subdirectory
- Registers modules in `ModuleRegistry` singleton
- Provides API endpoints: `/api/modules/list`, `/api/modules/available`, etc.

**Current Production Modules (4 total):**
1. `inhouse-kanban` - Production workflow Kanban (v3.0.1)
2. `inhouse-print` - Print production management
3. `quote-calculator` - Quote calculation tool
4. `vector_database` - Pinecone vector database manager (requires credentials)

---

### Frontend Module Loading (JavaScript)

**File:** `UI/business-ai-platform-v2.html`

```html
<!-- Line 264 -->
<script src="modules/module_loader.js"></script>
```

**File:** `UI/modules/module_loader.js` (788 lines)

```javascript
// Line 68 - Fetches from Flask backend
const response = await fetch('/api/modules/list');

// ModuleLoader.initialize(userId) flow:
// 1. Fetch /api/modules/list → get all registered modules
// 2. Fetch /api/modules/available?user_id=X → filter by credentials
// 3. generateSidebarButtons() → create icon buttons
// 4. generateFloatingToggles() → create draggable toggle buttons
// 5. generateMainTabs() → create main tab containers
// 6. loadAutoLoadModules() → load startup modules
```

**Key Point:** Frontend loads `module_loader.js` from `UI/modules/`, but this file is **synchronized** with `frontend/modules/module_loader.js`.

---

### Tool Plugin Discovery (Python)

**File:** `tools/plugins/module_plugin_loader.py`

```python
# Line 45 - Currently reads from LEGACY location
self.modules_dir = self.root_dir / "UI" / "external" / "modules"
```

**⚠️ ISSUE:** Tool discovery reads from legacy `UI/external/modules/`, but Flask backend reads from `frontend/modules/`. This creates **disconnection** between AI tools and production modules.

**Fix Required:** Change to `self.modules_dir = self.root_dir / "frontend" / "modules"`

---

### Module Manifest Schema

**Production modules MUST have this structure:**

```
frontend/modules/{module-id}/
├── manifest.json              ← REQUIRED (module configuration)
├── {module-id}.html           ← REQUIRED (UI template for sidebar/main tab)
├── {module-id}.js             ← REQUIRED (controller logic)
├── {module-id}.css            ← OPTIONAL (styling)
│
├── schema/                    ← OPTIONAL (AI tool definitions)
│   └── {name}_tools.json      ← Tool schema in Anthropic format
│
├── implementations/           ← OPTIONAL (AI tool implementations)
│   ├── __init__.py            ← Required for Python module
│   └── {name}_wrapper.py      ← Tool function implementations
│
└── routes/                    ← OPTIONAL (Flask API endpoints)
    ├── __init__.py            ← Exports blueprint
    └── {name}_routes.py       ← Flask route definitions
```

**Example `manifest.json`:**

```json
{
  "id": "inhouse-kanban",
  "name": "Production Workflow",
  "version": "3.0.1",
  "description": "InHousePrint production workflow Kanban board",
  "icon": "fa-industry",
  "color": "#00509E",
  
  "html_file": "inhouse-kanban.html",
  "js_file": "inhouse-kanban.js",
  "css_file": "inhouse-kanban-NEW.css",
  
  "required_platforms": [],
  "optional_platforms": [],
  
  "sidebar_position": "right",
  "sidebar_width": 1200,
  "auto_load": false,
  "requires_auth": true,
  
  "floating_toggle": true,
  "floating_toggle_position": "right",
  "floating_toggle_default_top": 280,
  "main_tab": true,
  "main_tab_id": "inhouse-kanban",
  
  "dependencies": [],
  "api_routes": ["/api/inhouse-kanban/*"],
  "features": {...}
}
```

---

## 🚧 Migration Strategy - Gradual Rebuild

### Phase 1: Keep Legacy Modules In Place ✅

**Decision:** Do NOT archive `UI/external/modules/` yet. Keep as reference during rebuild.

**Reasoning:**
- 20+ modules contain valuable implementation patterns
- Some modules may have tools/ and routes/ folders with working code
- Gradual migration allows validation before archiving
- Developers need access to legacy code during rebuild

**Action:** No action required - legacy modules stay where they are.

---

### Phase 2: Rebuild Module Workflow

When rebuilding a module from `UI/external/modules/` → `frontend/modules/`:

#### **Step 1: Review Legacy Module**

```powershell
# Examine legacy module structure
Get-ChildItem "C:\Users\gpoli\GIT\AI_agents\UI\external\modules\shopify\" -Recurse
```

**Check for:**
- ✅ Does `manifest.json` exist?
- ✅ Does it have tools/ folder? (AI tools to migrate)
- ✅ Does it have routes/ folder? (Flask endpoints to migrate)
- ✅ Does it have implementations/ folder? (Python code to migrate)
- ✅ What credentials does it require? (`required_platforms`)

#### **Step 2: Create Production Module Folder**

```powershell
# Create new production module
New-Item -ItemType Directory -Path "C:\Users\gpoli\GIT\AI_agents\frontend\modules\shopify"
```

#### **Step 3: Copy and Adapt Files**

```powershell
# Copy manifest (will need editing)
Copy-Item "UI\external\modules\shopify\manifest.json" `
          "frontend\modules\shopify\manifest.json"

# Copy HTML/JS/CSS
Copy-Item "UI\external\modules\shopify\shopify.html" `
          "frontend\modules\shopify\shopify.html"
Copy-Item "UI\external\modules\shopify\shopify.js" `
          "frontend\modules\shopify\shopify.js"
Copy-Item "UI\external\modules\shopify\shopify.css" `
          "frontend\modules\shopify\shopify.css"

# Copy optional folders (if exist)
Copy-Item "UI\external\modules\shopify\schema\" `
          "frontend\modules\shopify\schema\" -Recurse -ErrorAction SilentlyContinue
Copy-Item "UI\external\modules\shopify\implementations\" `
          "frontend\modules\shopify\implementations\" -Recurse -ErrorAction SilentlyContinue
Copy-Item "UI\external\modules\shopify\routes\" `
          "frontend\modules\shopify\routes\" -Recurse -ErrorAction SilentlyContinue
```

#### **Step 4: Update Manifest.json**

Edit `frontend/modules/shopify/manifest.json`:

```json
{
  "id": "shopify",
  "name": "Shopify Integration",
  "version": "1.0.0",
  
  // ✅ ADD NEW FIELDS (if not present):
  "floating_toggle": true,
  "floating_toggle_position": "right",
  "floating_toggle_default_top": 340,
  "main_tab": true,
  "main_tab_id": "shopify",
  
  // ✅ UPDATE PATHS (ensure correct):
  "html_file": "shopify.html",
  "js_file": "shopify.js",
  "css_file": "shopify.css",
  
  // ✅ VERIFY CREDENTIALS:
  "required_platforms": ["shopify"],  // User must have Shopify credentials
  "optional_platforms": []
}
```

#### **Step 5: Update JavaScript (if needed)**

Legacy modules may use old patterns. Update to modern pattern:

```javascript
// OLD PATTERN (deprecated):
class ShopifyModule extends BaseModule {
    constructor() {
        super('shopify');
    }
}

// NEW PATTERN (production):
class ShopifyModule {
    constructor(moduleId) {
        this.moduleId = moduleId;
        this.container = null;
    }
    
    async initialize() {
        console.log('🔧 Initializing Shopify module...');
        this.container = document.getElementById(`tab-${this.moduleId}`);
        if (!this.container) {
            console.error(`Container not found for module: ${this.moduleId}`);
            return;
        }
        
        // Your module initialization code here
        await this.loadShopifyData();
        console.log('✅ Shopify module initialized');
    }
}

// REQUIRED: Register module in global registry
window.ModuleRegistry = window.ModuleRegistry || {};
window.ModuleRegistry['shopify'] = {
    init: async () => {
        const module = new ShopifyModule('shopify');
        await module.initialize();
        return module;
    }
};
```

#### **Step 6: Test Module**

```powershell
# Restart Flask to discover new module
cd C:\Users\gpoli\GIT\AI_agents
BISTOP
Start-Sleep -Seconds 3
BISTART

# Wait for Flask to start
Start-Sleep -Seconds 12

# Open browser and test
# - Does icon appear in sidebar?
# - Does floating toggle appear?
# - Does module load when clicked?
# - Do credentials check work?
```

#### **Step 7: Validate and Archive Legacy**

```powershell
# Once validated, move legacy module to archive
Move-Item "UI\external\modules\shopify" `
          "UI\_ARCHIVED_NOV25\external_modules_LEGACY\shopify"

# Document in migration log
Add-Content "MODULE_MIGRATION_LOG.md" @"
- [x] shopify - Migrated on $(Get-Date -Format 'yyyy-MM-dd')
"@
```

---

### Phase 3: Migration Tracking

**File:** `MODULE_MIGRATION_LOG.md` (create this)

```markdown
# Module Migration Tracking Log

## Migration Progress (4/24 complete - 17% done)

### ✅ Completed Migrations (4)
- [x] inhouse-kanban - Migrated (Nov 25, 2025) - Validated ✅
- [x] inhouse-print - Migrated (Nov 2025) - Needs validation
- [x] quote-calculator - Migrated (Nov 2025) - Needs validation
- [x] vector_database - Migrated (Nov 2025) - Validated ✅

### 🔄 In Progress (0)
(None currently)

### 📋 Pending Migration (20)
- [ ] automation-workflows
- [ ] communication-hub
- [ ] database-visualizer
- [ ] debug-module
- [ ] production-analytics
- [ ] render-management
- [ ] salesforce
- [ ] settings-sidebar
- [ ] shopify
- [ ] stock-management
- [ ] synergy
- [ ] thread-cards
- [ ] xero
- [ ] [7 more modules...]

### 📦 Archived (0)
(None yet - archive after validation)

---

## Migration Template (Copy for each module)

### Module: {module-name}
**Started:** YYYY-MM-DD  
**Completed:** YYYY-MM-DD  
**Migrated By:** [Developer/AI name]  

**Legacy Location:** `UI/external/modules/{module-name}/`  
**Production Location:** `frontend/modules/{module-name}/`  

**Files Migrated:**
- [x] manifest.json (updated with new fields)
- [x] {module-name}.html
- [x] {module-name}.js (updated to modern pattern)
- [x] {module-name}.css
- [x] schema/ folder (if applicable)
- [x] implementations/ folder (if applicable)
- [x] routes/ folder (if applicable)

**Credentials Required:**
- Platform: {platform-name}
- Setup: [Link to setup guide]

**Testing Checklist:**
- [x] Module appears in sidebar
- [x] Floating toggle works
- [x] Main tab loads correctly
- [x] Credentials check works
- [x] AI tools functional (if applicable)
- [x] Flask routes work (if applicable)

**Issues Encountered:**
(Document any problems and solutions)

**Archived On:** YYYY-MM-DD (after validation)
```

---

## 🎯 Technical Specifications

### Module Naming Conventions

**Module ID Rules:**
- ✅ Format: `lowercase-with-hyphens`
- ✅ Examples: `shopify`, `salesforce`, `google-drive`, `microsoft-teams`
- ❌ NO uppercase: `Shopify`, `Salesforce`
- ❌ NO underscores: `shopify_integration`
- ❌ NO spaces: `Shopify Integration`
- ❌ NO periods: `shopify.integration`

**Folder Name = Module ID:**
```
frontend/modules/shopify/          ← ✅ Matches ID: "shopify"
frontend/modules/google-drive/     ← ✅ Matches ID: "google-drive"
frontend/modules/Shopify/          ← ❌ Uppercase not allowed
frontend/modules/shopify_store/    ← ❌ Underscore not allowed
```

**File Naming Pattern:**
```
{module-id}/
├── manifest.json         ← Always "manifest.json"
├── {module-id}.html      ← Module ID + .html
├── {module-id}.js        ← Module ID + .js
└── {module-id}.css       ← Module ID + .css (optional)
```

**Class Naming (JavaScript):**
```javascript
// Module ID: "shopify"
class ShopifyModule { }  // PascalCase, remove hyphens

// Module ID: "google-drive"
class GoogleDriveModule { }  // PascalCase, remove hyphens

// Module ID: "microsoft-teams"
class MicrosoftTeamsModule { }  // PascalCase, remove hyphens
```

---

### UI Generation (Dynamic)

**Manifest fields control UI generation:**

```json
{
  // Sidebar icon button (always generated if module available)
  "icon": "fa-shopify",
  "color": "#96d8a2",
  "sidebar_position": "right",
  "sidebar_width": 450,
  
  // Floating toggle button (optional)
  "floating_toggle": true,              // Creates draggable floating button
  "floating_toggle_position": "right",  // "left" or "right"
  "floating_toggle_default_top": 340,   // Y position in pixels
  
  // Main tab container (optional)
  "main_tab": true,                     // Creates tab in main content area
  "main_tab_id": "shopify",             // Tab container ID
  
  // Loading behavior
  "auto_load": false                    // Load at startup (default: false)
}
```

**Generated Elements:**

1. **Sidebar Icon Button:**
   ```html
   <button class="sidebar-module-btn" data-module-id="shopify">
       <i class="fa-shopify" style="color: #96d8a2"></i>
       <span>Shopify Integration</span>
   </button>
   ```

2. **Floating Toggle Button:**
   ```html
   <button class="module-floating-toggle" 
           data-module-id="shopify"
           style="background: #96d8a2; top: 340px; right: 20px;">
       <i class="fa-shopify"></i>
   </button>
   ```

3. **Main Tab Container:**
   ```html
   <div class="tab-content" id="tab-shopify" style="display: none;">
       <!-- Module HTML injected here -->
   </div>
   ```

**⚠️ CRITICAL:** Do NOT add these elements to `business-ai-platform-v2.html` manually! They are generated dynamically by `module_loader.js`.

---

### Credential Management

**How credential checking works:**

1. **User connects platform in settings** → Stored in Supabase `ai_infrastructure.user_platform_credentials` table
2. **Module declares requirements** in `manifest.json`:
   ```json
   {
     "required_platforms": ["shopify"],    // User MUST have these
     "optional_platforms": ["stripe"]      // Enhances functionality if available
   }
   ```
3. **Backend checks credentials** via `ModuleRegistry.check_user_credentials(user_id, module_id)`
4. **Frontend filters modules** via `/api/modules/available?user_id=X`
5. **Setup notifications shown** if required credentials missing

**Available Platforms:**
- `google` - Google Workspace (Gmail, Drive, Docs, Sheets, Calendar)
- `microsoft` - Microsoft 365 (Outlook, OneDrive, Excel, Teams)
- `shopify` - Shopify e-commerce
- `stripe` - Stripe payments
- `xero` - Xero accounting
- `salesforce` - Salesforce CRM
- `pinecone` - Pinecone vector database
- `openai` - OpenAI API
- [More platforms in `platform_credential_schemas.py`]

---

## 🛠️ Developer Commands

### Module Development Workflow

```powershell
# 1. Create new module folder
New-Item -ItemType Directory -Path "frontend\modules\my-module"

# 2. Create manifest.json (use template from this doc)
# 3. Create HTML/JS/CSS files
# 4. Restart Flask
cd C:\Users\gpoli\GIT\AI_agents
BISTOP
Start-Sleep -Seconds 3
BISTART

# 5. Test in browser (wait 12 seconds for Flask startup)
Start-Sleep -Seconds 12
# Open: http://localhost:5001/business-ai-platform-v2.html

# 6. Validate module loading
python -c "from AI_infrastructure.core.module_registry import get_module_registry; registry = get_module_registry(); print(f'Loaded {len(registry.modules)} modules'); print([m for m in registry.modules.keys() if 'my-module' in m])"
```

### Testing Tools

```powershell
# Check if Flask is running
Get-NetTCPConnection -LocalPort 5001 -State Listen -ErrorAction SilentlyContinue

# Check module registration
python -c "from AI_infrastructure.core.module_registry import get_module_registry; registry = get_module_registry(); print('\n'.join(registry.modules.keys()))"

# Check tool discovery (AI tools)
python tools/plugins/module_plugin_loader.py

# Check route discovery (Flask endpoints)
python AI_infrastructure/core/module_blueprint_loader.py
```

---

## 🚨 Common Issues and Solutions

### Issue 1: Module Not Appearing in UI

**Symptoms:** Module registered in backend but not showing in sidebar

**Debug Steps:**
```javascript
// Open browser console (F12)
console.log('Modules fetched:', window.moduleLoader?.modules);
console.log('Available modules:', window.moduleLoader?.availableModules);
```

**Common Causes:**
1. ❌ User missing required credentials → Check `required_platforms` in manifest
2. ❌ Manifest syntax error → Validate JSON with JSONLint
3. ❌ Module ID mismatch → Folder name must match manifest `id`
4. ❌ Flask not restarted → Run `BISTOP; BISTART`

---

### Issue 2: Module Icon Not Showing

**Symptoms:** Button appears but icon is blank/default

**Debug Steps:**
```javascript
// Check icon format in manifest
// Both formats work:
"icon": "fa-shopify"        // ✅ Short format
"icon": "fas fa-shopify"    // ✅ Long format
```

**Fix:** Update `manifest.json` to use FontAwesome icon name

---

### Issue 3: Module Loads but Breaks

**Symptoms:** Module container appears but JavaScript errors

**Debug Steps:**
```javascript
// Check module registration
console.log('Module registry:', window.ModuleRegistry);
console.log('Module init function:', window.ModuleRegistry['my-module']?.init);
```

**Common Causes:**
1. ❌ Missing `window.ModuleRegistry[id].init()` function
2. ❌ Class constructor expects parameters
3. ❌ Container ID mismatch (check `main_tab_id` in manifest)

---

### Issue 4: Duplicate Modules

**Symptoms:** Same module in multiple locations, unclear which is active

**Solution:** Only modules in `frontend/modules/` are loaded by production Flask backend. Legacy modules in `UI/external/modules/` are ignored.

**Verification:**
```powershell
# Check what Flask sees
python -c "from AI_infrastructure.core.module_registry import get_module_registry; registry = get_module_registry(); print(f'Modules directory: {registry.modules_directory}'); print('Registered modules:', list(registry.modules.keys()))"
```

---

## 📚 Reference Documentation

### Related Documentation Files

**Module Development:**
- `UI/module_development/UNDERSTANDING_AUTO_DISCOVERY.md` - Auto-discovery system explanation
- `UI/module_development/PLUGIN_SYSTEM_QUICK_REFERENCE.md` - Quick reference guide
- `UI/module_development/PLUGIN_SYSTEM_GUIDE.md` - Complete plugin tutorial
- `UI/module_development/MODULE_ARCHITECTURE_V2.md` - Architecture design (AI-integrated modules)
- `UI/module_development/MODULE_BEST_PRACTICES.md` - Best practices for all modules

**System Documentation:**
- `UI/external/modules/MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md` - Legacy system architecture
- `UI/external/modules/MODULE_SYSTEM_INTEGRATION_GUIDE.md` - Legacy integration guide
- `.github/copilot-instructions.md` - Complete platform documentation (AI agents)

**Backend Code:**
- `AI_infrastructure/core/module_registry.py` - Module discovery and registration
- `AI_infrastructure/routes/module_routes.py` - Module API endpoints
- `tools/plugins/module_plugin_loader.py` - AI tool discovery

**Frontend Code:**
- `UI/modules/module_loader.js` - Frontend module loader (788 lines)
- `frontend/modules/module_loader.js` - Synchronized copy
- `UI/business-ai-platform-v2.html` - Main UI entry point

---

## 🎯 Success Metrics

### Module Migration is Complete When:

- ✅ Module folder exists in `frontend/modules/{module-id}/`
- ✅ Manifest.json has all required fields
- ✅ Module appears in sidebar when user has credentials
- ✅ Floating toggle works (if `floating_toggle: true`)
- ✅ Main tab loads correctly (if `main_tab: true`)
- ✅ Module JavaScript initializes without errors
- ✅ AI tools work (if `schema/` and `implementations/` exist)
- ✅ Flask routes work (if `routes/` folder exists)
- ✅ Legacy module archived to `UI/_ARCHIVED_NOV25/external_modules_LEGACY/`
- ✅ Migration logged in `MODULE_MIGRATION_LOG.md`

---

## 🚀 Migration Priority Recommendations

### High Priority (Rebuild First) 🔥

These modules are likely actively used or have complete implementations:

1. **synergy** - Synergy collaboration features
2. **stock-management** - Stock/inventory management
3. **production-analytics** - Production metrics and analytics
4. **automation-workflows** - Workflow automation
5. **communication-hub** - Team communication

### Medium Priority (Rebuild Second) 📊

These modules provide valuable integrations:

6. **shopify** - E-commerce integration
7. **salesforce** - CRM integration
8. **xero** - Accounting integration
9. **render-management** - Render.com deployment management
10. **database-visualizer** - Database visualization tools

### Low Priority (Rebuild Last) 📝

These modules may be less critical or still in development:

11. **thread-cards** - Thread UI components (may be JS utility, not module)
12. **settings-sidebar** - Settings UI (may be JS utility, not module)
13. **debug-module** - Debugging tools (development only)
14. **communication-hub** - Communication features
15. [Remaining modules...]

---

## 📋 Quick Reference Checklist

### Before Starting Migration:

- [ ] Read this document completely
- [ ] Understand difference between production modules (`frontend/modules/`) and legacy modules (`UI/external/modules/`)
- [ ] Understand difference between plugin modules and JavaScript utilities (`UI/modules/`)
- [ ] Check if module has AI tools (schema/ folder) - these need special attention
- [ ] Check if module has Flask routes (routes/ folder) - these need special attention
- [ ] Verify you have access to module's required platform credentials for testing

### During Migration:

- [ ] Copy files from legacy location to production location
- [ ] Update manifest.json with new fields (`floating_toggle`, `main_tab`, etc.)
- [ ] Update JavaScript to modern pattern (remove BaseModule if present)
- [ ] Add `window.ModuleRegistry[id].init()` registration
- [ ] Test credentials checking works correctly
- [ ] Restart Flask and verify module loads
- [ ] Test all module features (clicks, forms, API calls)

### After Migration:

- [ ] Document migration in `MODULE_MIGRATION_LOG.md`
- [ ] Archive legacy module to `UI/_ARCHIVED_NOV25/external_modules_LEGACY/`
- [ ] Update this document if you discover patterns/issues
- [ ] Notify team of completed migration

---

## 🤖 For AI Coding Agents

When assisting with module migration, follow this prompt template:

```
I need to migrate the [module-name] module from legacy to production.

Context:
- Legacy location: UI/external/modules/[module-name]/
- Production location: frontend/modules/[module-name]/
- Reference: MODULE_SYSTEM_FOLDER_ARCHITECTURE.md

Tasks:
1. Review legacy module structure (check for tools/, routes/, implementations/ folders)
2. Create production folder: frontend/modules/[module-name]/
3. Copy and adapt files following migration workflow in Phase 2
4. Update manifest.json with new fields (floating_toggle, main_tab, etc.)
5. Update JavaScript to modern pattern (remove BaseModule, add ModuleRegistry registration)
6. Test module loads correctly
7. Document migration in MODULE_MIGRATION_LOG.md

Constraints:
- Do NOT delete legacy module until migration validated
- Do NOT modify UI/business-ai-platform-v2.html (UI generated dynamically)
- Do NOT confuse plugin modules with JavaScript utilities in UI/modules/
- Follow naming conventions strictly (lowercase-with-hyphens)
```

---

## 📞 Support and Questions

### For Developers:

If you encounter issues during migration:
1. Check "Common Issues and Solutions" section above
2. Review related documentation files
3. Check Flask logs: `AI_infrastructure/logs/flask_app.log`
4. Test with browser console (F12) for JavaScript errors
5. Validate manifest.json syntax with JSONLint
6. Document new issues/patterns in this file for future developers

### For AI Agents:

When uncertain about module system behavior:
1. Re-read this document completely
2. Trace code execution paths (backend → frontend → module)
3. Check existing production modules for working patterns
4. Test changes incrementally (don't change multiple files simultaneously)
5. Always restart Flask after backend changes: `BISTOP; BISTART`

---

**Document Version:** 1.0.0  
**Last Updated:** November 26, 2025  
**Status:** ✅ Active Reference Document  
**Maintained By:** Development Team + AI Coding Agents

---

## Appendix A: Complete File Tree

```
AI_agents/
├── frontend/
│   └── modules/                           ← 🎯 PRODUCTION MODULES ONLY
│       ├── inhouse-kanban/
│       │   ├── manifest.json
│       │   ├── inhouse-kanban.html
│       │   ├── inhouse-kanban.js
│       │   └── inhouse-kanban-NEW.css
│       ├── inhouse-print/
│       ├── quote-calculator/
│       ├── vector_database/
│       └── module_loader.js               ← Synchronized with UI/modules/
│
├── UI/
│   ├── business-ai-platform-v2.html       ← Main UI entry point
│   │
│   ├── modules/                           ← ⚠️ JAVASCRIPT UTILITIES (NOT plugins)
│   │   ├── module_loader.js               ← Synchronized with frontend/modules/
│   │   ├── agents/                        ← JS utility: agent UI components
│   │   ├── components/                    ← JS utility: shared UI components
│   │   ├── prompt-library/                ← JS utility: prompt management
│   │   ├── settings-sidebar/              ← JS utility: settings UI
│   │   ├── shared/                        ← JS utility: shared functions
│   │   ├── thread-manager/                ← JS utility: thread management
│   │   ├── transcription/                 ← JS utility: transcription handling
│   │   └── [other JS utilities...]
│   │
│   ├── external/
│   │   └── modules/                       ← ⚠️ LEGACY MODULES (keep for rebuild)
│   │       ├── automation-workflows/
│   │       ├── communication-hub/
│   │       ├── database-visualizer/
│   │       ├── debug-module/
│   │       ├── inhouse-kanban/            ← Can archive after validation
│   │       ├── inhouse-print/
│   │       ├── production-analytics/
│   │       ├── quote-calculator/
│   │       ├── render-management/
│   │       ├── salesforce/
│   │       ├── settings-sidebar/
│   │       ├── shopify/
│   │       ├── stock-management/
│   │       ├── synergy/
│   │       ├── thread-cards/
│   │       ├── xero/
│   │       └── manifest.json              ← OLD registry (deprecated)
│   │
│   ├── module_development/                ← Documentation for module developers
│   └── _ARCHIVED_NOV25/                   ← Archived legacy code
│
├── AI_infrastructure/
│   ├── core/
│   │   ├── module_registry.py             ← Backend module discovery
│   │   └── module_blueprint_loader.py     ← Flask route discovery
│   └── routes/
│       └── module_routes.py               ← Module API endpoints
│
├── tools/
│   └── plugins/
│       └── module_plugin_loader.py        ← AI tool discovery (needs path fix)
│
├── MODULE_SYSTEM_FOLDER_ARCHITECTURE.md   ← 📄 THIS DOCUMENT
└── MODULE_MIGRATION_LOG.md                ← 📄 TO BE CREATED
```

---

**END OF DOCUMENT**
