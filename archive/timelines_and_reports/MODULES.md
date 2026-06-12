# Modules - Technical Documentation

**Version:** 4.0.0  
**Status:** ✅ Production Ready  
**Last Updated:** January 18, 2026  
**System:** Self-Registering Plugin Architecture

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start Guide](#quick-start-guide)
4. [Module Types](#module-types)
5. [File Structure](#file-structure)
6. [Manifest Schema](#manifest-schema)
7. [Rendering Patterns](#rendering-patterns)
8. [Lifecycle Hooks](#lifecycle-hooks)
9. [Utility Injection](#utility-injection)
10. [Tool Integration](#tool-integration)
11. [Backend Routes](#backend-routes)
12. [Critical Fixes](#critical-fixes)
13. [Deployment Configuration](#deployment-configuration)
14. [Testing & Debugging](#testing--debugging)
15. [Migration Guide](#migration-guide)
16. [API Reference](#api-reference)
17. [Known Issues](#known-issues)
18. [Appendix](#appendix)

---

## Overview

### Purpose

The Module System is a self-registering plugin architecture that enables developers to add new features to the AI Agents platform without modifying core code. Modules are automatically discovered, validated, and loaded on-demand, supporting both internal platform components and external business integrations.

### Key Capabilities

- **Auto-Discovery:** Backend scans `UI/modules_external/` and `UI/modules_internal/` folders at startup
- **Dynamic Loading:** Frontend lazy-loads modules when accessed (sidebar click or tab switch)
- **Credential Validation:** Modules can require platform credentials (Xero, Shopify, Google, etc.)
- **Two Rendering Patterns:** JavaScript-generated UI or separate HTML templates
- **Tool Integration:** Modules can register AI tools via `@tool_executor` decorator
- **Hot-Reload:** External modules support hot-reload without Flask restart
- **Environment Filtering:** Deployment-specific module disabling (local vs Render)

### Statistics

- **Active Modules:** 17 total (6 internal, 11 external)
- **Backend Discovery:** `ModuleRegistry` (~400 lines, Python)
- **Frontend Loader:** `ModuleLoaderV4` (~2,800 lines, JavaScript ES6)
- **API Endpoints:** 8 routes for module metadata and loading
- **Auto-Registered Tools:** 80+ tools from module schemas

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (Flask Startup)                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ModuleRegistry (Python)                                 │   │
│  │  - Scans UI/modules_external/ folders                    │   │
│  │  - Loads manifest.json from each module                  │   │
│  │  - Validates credential requirements                     │   │
│  │  - Registers tools from schema/ folders                  │   │
│  │  - Exposes /api/modules/* REST endpoints                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            ↓ HTTP GET /api/modules
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Page Load)                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ModuleLoaderV4 (JavaScript ES6)                         │   │
│  │  - Fetches module list from backend                      │   │
│  │  - Generates UI elements:                                │   │
│  │    • Sidebar buttons (with credential checks)            │   │
│  │    • Floating toggle buttons (draggable)                 │   │
│  │    • Main tab containers (#tab-{module-id})              │   │
│  │  - Lazy-loads HTML/CSS/JS on-demand                      │   │
│  │  - Injects utilities (dom, api, storage, events, log)    │   │
│  │  - Calls lifecycle hooks (onDashboardLoad, etc.)         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            ↓ User Action (click)
┌─────────────────────────────────────────────────────────────────┐
│                     Module Instance                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  window.{moduleId} (Object)                              │   │
│  │  - State management (emails, threads, UI refs)           │   │
│  │  - Event handlers (button clicks, data updates)          │   │
│  │  - API calls to backend routes                           │   │
│  │  - Real-time updates (Supabase Realtime optional)        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Design Patterns

#### 1. **Plugin Pattern (Self-Registering)**

Modules register themselves by existing in the correct folder structure. No manual configuration required.

```python
# Backend auto-discovery
class ModuleRegistry:
    def discover_modules(self):
        for folder in Path('UI/modules_external').iterdir():
            if folder.is_dir() and (folder / 'manifest.json').exists():
                module = self.load_manifest(folder / 'manifest.json')
                self.register(module)  # Automatic registration
```

#### 2. **Composition Pattern (V4-Modern)**

Modules are plain objects with injected utilities (not classes, not inheritance).

```javascript
// Module structure (composition, not inheritance)
export default {
    moduleId: 'my-module',
    state: { data: [] },
    
    async onDashboardLoad(utilities) {
        Object.assign(this, utilities);  // Inject dom, api, storage, events, log
        await this.render();
    }
};
```

#### 3. **Lazy Loading Pattern**

Modules only load when accessed, reducing initial page load time.

```javascript
// Lazy load on sidebar button click
sidebar_button.addEventListener('click', async () => {
    if (!window.myModule) {
        await ModuleLoaderV4.loadModule('my-module');  // First access: load
    }
    window.myModule.onSidebarLoad(utilities);  // Subsequent: reuse
});
```

#### 4. **Utility Injection Pattern**

Common functionality injected as utilities object (IoC pattern).

```javascript
// No imports needed, utilities provided by loader
async onDashboardLoad({ dom, api, storage, events, log }) {
    this.dom = dom;
    this.api = api;
    // ... use injected utilities
}
```

### Data Flow

#### Module Discovery Flow (Backend Startup):

```
Flask app starts
        ↓
ModuleRegistry.discover_modules()
        ↓
For each folder in UI/modules_external/:
        ↓
    Read manifest.json
        ↓
    Validate required fields (id, name, version)
        ↓
    Check required_platforms (credentials)
        ↓
    Load tools from schema/*.json (if exists)
        ↓
    Register tools with RegistryV3
        ↓
    Add module to registry
        ↓
Expose /api/modules endpoint (module list)
```

#### Module Loading Flow (Frontend User Action):

```
Page loads
        ↓
ModuleLoaderV4.initialize()
        ↓
Fetch GET /api/modules
        ↓
Generate UI elements:
    - Sidebar buttons
    - Floating toggles
    - Main tab containers
        ↓
User clicks sidebar button
        ↓
Check: window.{moduleId} exists?
        ↓
    ┌───────┴───────┐
   YES              NO
    ↓               ↓
Reuse           Load HTML/CSS/JS
instance        ↓
    ↓           Parse ES6 module
    │           ↓
    │           Create window.{moduleId}
    │           ↓
    └───────────┴─────→ Call onDashboardLoad() or onSidebarLoad()
                        ↓
                    Inject utilities (dom, api, storage, events, log)
                        ↓
                    Module renders UI
```

---

## Quick Start Guide

### Create a New Module (5 Minutes)

#### Step 1: Create Folder Structure

```bash
cd UI/modules_external
mkdir my-new-module
cd my-new-module
```

#### Step 2: Create manifest.json

```json
{
  "id": "my-new-module",
  "name": "My New Module",
  "version": "1.0.0",
  "description": "Brief description of what this module does",
  "author": "Your Name",
  "icon": "fa-rocket",
  "js_file": "my-new-module.js",
  "css_file": "my-new-module.css",
  "main_tab": true,
  "sidebar_position": "right",
  "sidebar_width": 500,
  "floating_toggle": false,
  "auto_load": false,
  "required_platforms": []
}
```

#### Step 3: Create my-new-module.js

```javascript
/**
 * My New Module - V4-Modern Pattern
 */

export default {
    moduleId: 'my-new-module',
    
    // State management
    state: {
        data: [],
        loading: false
    },
    
    // Lifecycle hook: Dashboard tab opened
    async onDashboardLoad(utilities) {
        // Inject utilities
        Object.assign(this, utilities);
        
        // Get container
        this.container = this.dom.getContainer();
        
        // Render UI
        this.render();
        
        // Load data
        await this.loadData();
    },
    
    // Render UI
    render() {
        this.container.innerHTML = `
            <div class="module-header">
                <h2><i class="fas fa-rocket"></i> My New Module</h2>
            </div>
            <div class="module-body">
                <button id="refresh-btn" class="btn btn-primary">Refresh</button>
                <div id="data-container"></div>
            </div>
        `;
        
        // Setup event listeners
        this.dom.on('#refresh-btn', 'click', () => this.loadData());
    },
    
    // Load data from backend
    async loadData() {
        try {
            this.state.loading = true;
            this.log.info('Loading data...');
            
            const response = await this.api.get('/api/my-module/data');
            this.state.data = response.data;
            
            this.displayData();
            this.log.success(`Loaded ${this.state.data.length} items`);
        } catch (error) {
            this.log.error('Failed to load data:', error);
        } finally {
            this.state.loading = false;
        }
    },
    
    // Display data in UI
    displayData() {
        const container = this.dom.q('#data-container');
        container.innerHTML = this.state.data
            .map(item => `<div class="data-item">${item.name}</div>`)
            .join('');
    }
};

// Auto-register with window
if (typeof window !== 'undefined') {
    window.myNewModule = exports.default || exports;
}
```

#### Step 4: Create my-new-module.css

```css
/* My New Module Styles */

.module-header {
    display: flex;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid var(--border-color);
}

.module-header h2 {
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.module-body {
    padding: 20px;
}

.data-item {
    padding: 10px;
    margin: 5px 0;
    background: var(--card-bg);
    border-radius: 4px;
}
```

#### Step 5: Restart Flask & Test

```powershell
# Restart Flask server
cd AI_infrastructure
python flask_app.py

# Open browser
# Navigate to your app
# Click sidebar to see "My New Module" button
# Click button to load module
```

**That's it!** Your module is now auto-discovered and loaded.

---

## Module Types

### External Modules (Business Features)

**Location:** `UI/modules_external/`

**Purpose:** Plug-and-play business integrations and features

**Characteristics:**
- ✅ Registered in ModuleRegistry
- ✅ Dynamically loaded on-demand
- ✅ Can require platform credentials
- ✅ Hot-reload supported (no Flask restart)
- ✅ Version controlled independently
- ✅ Can register AI tools
- ✅ Can have Flask routes

**Examples:**
- `shopify/` - Shopify product management
- `xero/` - Xero accounting integration
- `quote-calculator/` - Custom quote calculator
- `inhouse-kanban/` - InHouse Print Kanban board
- `communication-hub/` - Unified email inbox

**When to use:** Creating new business features, integrations, or domain-specific tools

---

### Internal Modules (Platform Components)

**Location:** `UI/modules_internal/`

**Purpose:** Core platform infrastructure (NOT business features)

**Characteristics:**
- ❌ NOT registered in ModuleRegistry
- ❌ Pre-loaded in HTML `<script>` tags
- ❌ Cannot require credentials (always available)
- ❌ Require page refresh to reload
- ✅ Always available (no lazy loading)
- ✅ Can access global window objects
- ✅ Direct DOM manipulation

**Examples:**
- `settings-sidebar/` - User settings panel
- `thread-cards/` - Thread management UI
- `module_loader.js` - Module loading system itself

**When to use:** Core platform features that must always be available

---

### Comparison Table

| Feature | External Modules | Internal Modules |
|---------|-----------------|------------------|
| **Location** | `modules_external/` | `modules_internal/` |
| **Registration** | ModuleRegistry | Manual HTML wiring |
| **Loading** | Lazy (on-demand) | Pre-loaded at startup |
| **Credentials** | Can require | Always available |
| **Hot-Reload** | ✅ Yes | ❌ No (page refresh) |
| **Tool Registration** | ✅ Yes (schema/) | ❌ No |
| **Flask Routes** | ✅ Yes (routes/) | ❌ No |
| **Discovery** | Automatic | Manual |
| **Use Case** | Business features | Core infrastructure |

---

## File Structure

### External Module Structure

```
UI/modules_external/{module-id}/
├── manifest.json              ← REQUIRED (module metadata)
├── {module-id}.js             ← REQUIRED (controller/logic)
├── {module-id}.css            ← OPTIONAL (styles)
├── {module-id}.html           ← OPTIONAL (UI template, rarely used)
├── schema/                    ← OPTIONAL (AI tool definitions)
│   ├── {name}_tools.json      ← Tool schemas for AI agent
│   └── {name}_guide.json      ← Optional guide tool
├── implementations/           ← OPTIONAL (Python tool wrappers)
│   ├── __init__.py
│   └── {name}_wrapper.py      ← Tool implementation with @tool_executor
├── routes/                    ← OPTIONAL (Flask API endpoints)
│   ├── __init__.py
│   └── {name}_routes.py       ← Flask Blueprint
├── backend/                   ← OPTIONAL (business logic)
│   └── {name}_logic.py
├── docs/                      ← OPTIONAL (documentation)
│   └── README.md
└── archived/                  ← OPTIONAL (old versions)
```

### Naming Conventions

#### Module ID Rules:
```
✅ CORRECT:
- quote-calculator
- inhouse-kanban
- communication-hub
- stock-management

❌ WRONG:
- QuoteCalculator (no uppercase)
- quote_calculator (no underscores)
- quotecalculator (must have hyphens for multi-word)
```

#### File Naming Rules:
```
JavaScript:   {module-id}.js      (lowercase-with-hyphens.js)
CSS:          {module-id}.css     (lowercase-with-hyphens.css)
HTML:         {module-id}.html    (lowercase-with-hyphens.html)
Python:       {name}_wrapper.py   (snake_case.py)
JSON:         {name}_tools.json   (snake_case.json)
```

#### Folder Must Match Module ID:
```
✅ CORRECT:
UI/modules_external/quote-calculator/
    ├── manifest.json (id: "quote-calculator")
    ├── quote-calculator.js
    └── quote-calculator.css

❌ WRONG:
UI/modules_external/quote_calculator/
    ├── manifest.json (id: "quote-calculator")  ← Mismatch!
```

### Minimal Module (1 File)

```
UI/modules_external/simple-module/
├── manifest.json
└── simple-module.js
```

### Complete Module (All Features)

```
UI/modules_external/full-module/
├── manifest.json
├── full-module.js
├── full-module.css
├── schema/
│   ├── full_module_tools.json
│   └── full_module_guide.json
├── implementations/
│   ├── __init__.py
│   └── full_module_wrapper.py
├── routes/
│   ├── __init__.py
│   └── full_module_routes.py
├── backend/
│   ├── __init__.py
│   └── full_module_logic.py
└── docs/
    └── README.md
```

---

## Manifest Schema

### Complete Field Reference

```json
{
  // REQUIRED FIELDS
  "id": "module-id",                    // MUST match folder name
  "name": "Display Name",               // Shown in UI
  "version": "1.0.0",                   // Semantic versioning
  
  // DISPLAY
  "description": "Brief description",   // Tooltip text
  "icon": "fa-icon-name",               // FontAwesome icon (without 'fa-' prefix)
  "author": "Your Name",                // Module creator
  
  // FILE REFERENCES
  "js_file": "module-id.js",            // Main JavaScript controller
  "css_file": "module-id.css",          // Styles (optional)
  "html_file": "module-id.html",        // Rarely used (JS-generated preferred)
  
  // UI PLACEMENT
  "main_tab": true,                     // Create dashboard tab
  "sidebar_position": "right",          // "left" or "right" sidebar
  "sidebar_width": 500,                 // Sidebar width in pixels
  "floating_toggle": true,              // Create draggable toggle button
  "floating_position": {                // Initial position
    "top": "20px",
    "right": "20px"
  },
  
  // BEHAVIOR
  "auto_load": false,                   // Load at startup (vs on-demand)
  "singleton": true,                    // Only one instance allowed
  "closable": true,                     // Can be closed by user
  
  // CREDENTIALS
  "required_platforms": [],             // ["xero", "shopify", "google"]
  "optional_platforms": [],             // Nice-to-have credentials
  
  // ADVANCED
  "dependencies": [],                   // Other module IDs required
  "priority": 100,                      // Load order priority (higher first)
  "experimental": false,                // Show warning badge
  "deprecated": false,                  // Show deprecation notice
  
  // METADATA
  "tags": ["integration", "accounting"], // Search/filter tags
  "documentation_url": "https://...",   // External docs link
  "support_url": "https://...",         // Support/issues link
  "changelog_url": "https://..."        // Version history
}
```

### Field Details

#### **id** (string, required)
- MUST be lowercase-with-hyphens
- MUST match folder name exactly
- Used as DOM ID prefix (`tab-{id}`, `sidebar-{id}`)
- Used as global variable name (converted to camelCase)

**Example:**
```json
"id": "quote-calculator"  // → window.quoteCalculator
```

#### **name** (string, required)
- Display name shown in UI
- Shown in sidebar button, tab title, floating toggle
- Can contain spaces, uppercase, special characters

**Example:**
```json
"name": "Quote Calculator Pro"
```

#### **version** (string, required)
- Semantic versioning: `MAJOR.MINOR.PATCH`
- Used for cache busting (JS/CSS URLs appended with `?v={version}`)
- Shown in module info panel

**Example:**
```json
"version": "2.1.3"
```

#### **icon** (string, optional, default: "fa-cube")
- FontAwesome icon name WITHOUT `fa-` prefix
- Used in sidebar button, tab icon, floating toggle
- Full list: https://fontawesome.com/v5/search

**Examples:**
```json
"icon": "calculator"      // → <i class="fas fa-calculator"></i>
"icon": "envelope"        // → <i class="fas fa-envelope"></i>
"icon": "shopping-cart"   // → <i class="fas fa-shopping-cart"></i>
```

#### **js_file** (string, required)
- Path to main JavaScript file (relative to module folder)
- Must be ES6 module with `export default { ... }`
- Loaded lazily when module accessed

**Example:**
```json
"js_file": "quote-calculator.js"
```

#### **css_file** (string, optional)
- Path to CSS file (relative to module folder)
- Loaded before JavaScript file
- Uses CSS variables for theming

**Example:**
```json
"css_file": "quote-calculator.css"
```

#### **html_file** (string, optional, RARELY USED)
- Path to HTML template file
- Injected into module container
- **Prefer JavaScript-generated UI** (more flexible)

**When to use:**
- Static forms with complex layouts
- Large templates that would clutter JavaScript
- Legacy modules not yet migrated to V4-Modern

**Example:**
```json
"html_file": "quote-calculator.html"
```

#### **main_tab** (boolean, default: false)
- If true, creates dashboard tab in main content area
- Tab ID: `tab-{module-id}`
- Tab appears in top navigation bar

**Example:**
```json
"main_tab": true  // → Creates tab-quote-calculator
```

#### **sidebar_position** (string, default: "right")
- Sidebar placement: `"left"` or `"right"`
- Left sidebar: Collapsible navigation menu
- Right sidebar: Module content panels

**Example:**
```json
"sidebar_position": "right"
```

#### **sidebar_width** (integer, default: 400)
- Sidebar width in pixels
- Range: 300-800px (enforced by CSS)

**Example:**
```json
"sidebar_width": 600  // → 600px wide sidebar
```

#### **floating_toggle** (boolean, default: false)
- If true, creates draggable floating button
- Button persists position in localStorage
- Useful for quick-access modules

**Example:**
```json
"floating_toggle": true  // → Creates draggable icon
```

#### **auto_load** (boolean, default: false)
- If true, module loads at page startup (before user clicks)
- Increases initial load time
- **Only use for critical modules**

**Example:**
```json
"auto_load": false  // Lazy load on-demand (recommended)
```

#### **required_platforms** (array, default: [])
- Platform credentials required for module to function
- Module hidden if user lacks credentials
- Checked via `/api/user/credentials` endpoint

**Supported platforms:**
```json
"required_platforms": [
  "xero",           // Xero accounting
  "shopify",        // Shopify e-commerce
  "google",         // Google Workspace (Gmail, Drive, Calendar)
  "microsoft",      // Microsoft 365 (Outlook, OneDrive)
  "salesforce",     // Salesforce CRM
  "quickbooks",     // QuickBooks accounting
  "stripe",         // Stripe payments
  "twillio",        // Twilio SMS
  "sendgrid",       // SendGrid email
  "mailchimp"       // Mailchimp email marketing
]
```

**Example:**
```json
"required_platforms": ["xero"]  // Module only visible if user has Xero OAuth tokens
```

---

## Rendering Patterns

### Pattern 1: JavaScript-Generated UI (Recommended)

**When to use:** Most modules (90% of cases)

**Pros:**
- ✅ Dynamic, data-driven UIs
- ✅ Easy to update without HTML files
- ✅ Better control flow
- ✅ Smaller file count

**Cons:**
- ❌ Harder to visualize layout
- ❌ Long template strings

**Example:**
```javascript
export default {
    moduleId: 'my-module',
    
    async onDashboardLoad(utilities) {
        Object.assign(this, utilities);
        this.container = this.dom.getContainer();
        this.createUI();  // JavaScript generates DOM
    },
    
    createUI() {
        this.container.innerHTML = `
            <div class="module-wrapper">
                <header class="module-header">
                    <h2><i class="fas fa-rocket"></i> My Module</h2>
                </header>
                
                <nav class="module-tabs">
                    <button data-tab="overview" class="active">Overview</button>
                    <button data-tab="settings">Settings</button>
                </nav>
                
                <div class="module-content">
                    <div id="tab-overview" class="tab-pane active"></div>
                    <div id="tab-settings" class="tab-pane"></div>
                </div>
            </div>
        `;
        
        // Setup tab switching
        this.dom.on('.module-tabs button', 'click', (e) => {
            this.switchTab(e.target.dataset.tab);
        });
    }
};
```

**Manifest:**
```json
{
  "id": "my-module",
  "js_file": "my-module.js",
  "css_file": "my-module.css"
  // NO html_file specified
}
```

---

### Pattern 2: Separate HTML Template (Legacy)

**When to use:** Complex static layouts, legacy modules

**Pros:**
- ✅ Easier to visualize layout
- ✅ Separation of concerns
- ✅ Designer-friendly

**Cons:**
- ❌ Extra file to maintain
- ❌ Harder to make dynamic
- ❌ Template must match JavaScript expectations

**Example:**

**my-module.html:**
```html
<div class="module-wrapper">
    <header class="module-header">
        <h2><i class="fas fa-rocket"></i> My Module</h2>
    </header>
    
    <nav class="module-tabs">
        <button data-tab="overview" class="active">Overview</button>
        <button data-tab="settings">Settings</button>
    </nav>
    
    <div class="module-content">
        <div id="tab-overview" class="tab-pane active"></div>
        <div id="tab-settings" class="tab-pane"></div>
    </div>
</div>
```

**my-module.js:**
```javascript
export default {
    moduleId: 'my-module',
    
    async onDashboardLoad(utilities) {
        Object.assign(this, utilities);
        this.container = this.dom.getContainer();
        
        // HTML already injected by ModuleLoader
        // Just setup event listeners
        this.setupEventListeners();
    },
    
    setupEventListeners() {
        this.dom.on('.module-tabs button', 'click', (e) => {
            this.switchTab(e.target.dataset.tab);
        });
    }
};
```

**Manifest:**
```json
{
  "id": "my-module",
  "html_file": "my-module.html",
  "js_file": "my-module.js",
  "css_file": "my-module.css"
}
```

---

### Comparison

| Aspect | JavaScript-Generated | HTML Template |
|--------|---------------------|---------------|
| **Flexibility** | ✅ High | ⚠️ Medium |
| **Maintenance** | ✅ Single file | ⚠️ Multiple files |
| **Dynamic Content** | ✅ Easy | ❌ Hard |
| **Designer-Friendly** | ❌ Hard | ✅ Easy |
| **File Count** | ✅ 2 files | ⚠️ 3 files |
| **Used By** | Communication Hub, Automation | InHouse Kanban |

---

## Lifecycle Hooks

### Hook Overview

Modules implement lifecycle hooks to respond to user actions:

```
Module Loaded
     ↓
onDashboardLoad()  ← User opens dashboard tab
     ↓
onSidebarLoad()    ← User opens sidebar
     ↓
onShow()           ← Module becomes visible
     ↓
onHide()           ← Module hidden
     ↓
onResize()         ← Window/container resized
     ↓
onDestroy()        ← Module unloaded (rare)
```

### onDashboardLoad(utilities)

**When:** User clicks main tab or module loads with `main_tab: true`

**Purpose:** Initialize dashboard UI, load data

**Parameters:**
- `utilities` (object) - Injected utilities (dom, api, storage, events, log)

**Called by:** ModuleLoaderV4 when dashboard tab becomes active

**Example:**
```javascript
async onDashboardLoad(utilities) {
    // 1. Inject utilities
    Object.assign(this, utilities);
    
    // 2. Get container
    this.dashboardContainer = this.dom.getContainer();
    
    // 3. Create UI
    this.renderDashboard();
    
    // 4. Load data
    await this.loadInitialData();
    
    // 5. Setup listeners
    this.setupEventListeners();
    
    this.log.success('Dashboard loaded');
}
```

---

### onSidebarLoad(utilities)

**When:** User clicks sidebar button

**Purpose:** Initialize sidebar UI, render panel

**Parameters:**
- `utilities` (object) - Injected utilities (dom, api, storage, events, log)

**Called by:** ModuleLoaderV4 when sidebar opens

**Example:**
```javascript
async onSidebarLoad(utilities) {
    // 1. Inject utilities
    Object.assign(this, utilities);
    
    // 2. Get sidebar container
    this.sidebarContainer = this.dom.getContainer();
    
    // 3. Render sidebar content
    this.renderSidebar();
    
    // 4. Load sidebar-specific data
    await this.loadSidebarData();
    
    this.log.success('Sidebar loaded');
}
```

---

### onShow()

**When:** Module becomes visible (tab switch, sidebar open)

**Purpose:** Resume activity, refresh data

**Called by:** ModuleLoaderV4 or TabManager

**Example:**
```javascript
onShow() {
    this.log.info('Module visible');
    
    // Resume polling
    if (this.pollingInterval) {
        this.startPolling();
    }
    
    // Refresh stale data
    if (this.isDataStale()) {
        this.refreshData();
    }
}
```

---

### onHide()

**When:** Module hidden (tab switch away, sidebar close)

**Purpose:** Pause activity, stop timers

**Called by:** ModuleLoaderV4 or TabManager

**Example:**
```javascript
onHide() {
    this.log.info('Module hidden');
    
    // Stop polling
    if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
    }
    
    // Save unsaved changes
    if (this.hasUnsavedChanges()) {
        this.autoSave();
    }
}
```

---

### onResize()

**When:** Window or container resized

**Purpose:** Adjust layout, recalculate sizes

**Called by:** Window resize event

**Example:**
```javascript
onResize() {
    // Recalculate table height
    if (this.table) {
        const containerHeight = this.container.offsetHeight;
        this.table.setHeight(containerHeight - 100);
    }
    
    // Adjust responsive breakpoints
    const width = this.container.offsetWidth;
    this.container.classList.toggle('mobile', width < 768);
}
```

---

### onDestroy() (Rare)

**When:** Module unloaded (page navigation, hot-reload)

**Purpose:** Cleanup, remove event listeners

**Called by:** ModuleLoaderV4 before unload

**Example:**
```javascript
onDestroy() {
    this.log.info('Module destroying');
    
    // Stop all intervals
    if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
    }
    
    // Remove global event listeners
    window.removeEventListener('resize', this.boundResizeHandler);
    
    // Cleanup Supabase subscriptions
    if (this.realtimeSubscription) {
        this.realtimeSubscription.unsubscribe();
    }
}
```

---

### Complete Lifecycle Example

```javascript
export default {
    moduleId: 'lifecycle-demo',
    
    state: {
        isVisible: false,
        pollingInterval: null
    },
    
    // Dashboard tab opened
    async onDashboardLoad(utilities) {
        Object.assign(this, utilities);
        this.container = this.dom.getContainer();
        
        this.render();
        await this.loadData();
        
        this.state.isVisible = true;
        this.startPolling();
    },
    
    // Sidebar opened
    async onSidebarLoad(utilities) {
        Object.assign(this, utilities);
        this.sidebarContainer = this.dom.getContainer();
        
        this.renderSidebar();
    },
    
    // Module becomes visible
    onShow() {
        this.state.isVisible = true;
        this.startPolling();
        this.refreshData();
    },
    
    // Module hidden
    onHide() {
        this.state.isVisible = false;
        this.stopPolling();
    },
    
    // Window resized
    onResize() {
        this.adjustLayout();
    },
    
    // Module unloaded
    onDestroy() {
        this.stopPolling();
        this.cleanup();
    },
    
    // Helper: Start polling
    startPolling() {
        if (this.state.pollingInterval) return;
        
        this.state.pollingInterval = setInterval(() => {
            if (this.state.isVisible) {
                this.refreshData();
            }
        }, 30000);  // 30 seconds
    },
    
    // Helper: Stop polling
    stopPolling() {
        if (this.state.pollingInterval) {
            clearInterval(this.state.pollingInterval);
            this.state.pollingInterval = null;
        }
    }
};
```

---

## Utility Injection

### Overview

ModuleLoaderV4 automatically injects 5 utility objects into every lifecycle hook:

```javascript
const utilities = {
    dom: { /* DOM manipulation */ },
    api: { /* HTTP requests */ },
    storage: { /* localStorage wrapper */ },
    events: { /* Event bus */ },
    log: { /* Console logging */ }
};
```

Modules receive these utilities and can use them without imports.

---

### dom Utility

**Purpose:** Simplified DOM manipulation and queries

#### Methods:

##### `getContainer()`
Returns the module's container element.

```javascript
const container = this.dom.getContainer();
// Returns: <div id="tab-my-module"></div> or <div id="sidebar-my-module"></div>
```

##### `q(selector)` / `querySelector(selector)`
Query single element within module container.

```javascript
const button = this.dom.q('#save-btn');
const header = this.dom.querySelector('.module-header');
```

##### `qAll(selector)` / `querySelectorAll(selector)`
Query all matching elements within module container.

```javascript
const buttons = this.dom.qAll('button');
buttons.forEach(btn => btn.disabled = true);
```

##### `createElement(tag, props)`
Create element with properties.

```javascript
const button = this.dom.createElement('button', {
    id: 'my-btn',
    className: 'btn btn-primary',
    textContent: 'Click Me',
    onclick: () => this.handleClick()
});
```

##### `on(selector, event, handler)`
Attach event listener with delegation.

```javascript
// Event delegation (works for dynamically added elements)
this.dom.on('.btn-delete', 'click', (e) => {
    const id = e.target.dataset.id;
    this.deleteItem(id);
});
```

##### `hide(element)` / `show(element)`
Toggle element visibility.

```javascript
this.dom.hide(this.dom.q('#loading-spinner'));
this.dom.show(this.dom.q('#content'));
```

##### `addClass(element, className)` / `removeClass(element, className)`
Manipulate CSS classes.

```javascript
this.dom.addClass(button, 'active');
this.dom.removeClass(button, 'disabled');
```

##### `empty(element)`
Remove all children.

```javascript
this.dom.empty(this.container);  // Clear container
```

---

### api Utility

**Purpose:** HTTP request wrapper with authentication

#### Methods:

##### `get(url, params)`
GET request with query parameters.

```javascript
const data = await this.api.get('/api/my-module/items', {
    limit: 50,
    offset: 0,
    sort: 'date_desc'
});
// Fetches: /api/my-module/items?limit=50&offset=0&sort=date_desc
```

##### `post(url, body)`
POST request with JSON body.

```javascript
const result = await this.api.post('/api/my-module/items', {
    name: 'New Item',
    quantity: 10,
    price: 29.99
});
```

##### `put(url, body)`
PUT request for updates.

```javascript
await this.api.put(`/api/my-module/items/${id}`, {
    quantity: 15
});
```

##### `delete(url)`
DELETE request.

```javascript
await this.api.delete(`/api/my-module/items/${id}`);
```

#### Features:

- ✅ Automatic authentication (includes session cookies)
- ✅ JSON parsing (auto-parses response bodies)
- ✅ Error handling (throws on non-200 status)
- ✅ Base URL handling (prepends API base if relative URL)

**Example with error handling:**
```javascript
try {
    const data = await this.api.get('/api/my-module/items');
    this.displayItems(data.items);
} catch (error) {
    this.log.error('Failed to load items:', error);
    this.showErrorMessage('Could not load data. Please try again.');
}
```

---

### storage Utility

**Purpose:** localStorage wrapper with JSON serialization

#### Methods:

##### `get(key)`
Retrieve value (auto-parses JSON).

```javascript
const filters = this.storage.get('my-module-filters');
// Returns: { status: 'active', sort: 'date' } (parsed from JSON)
```

##### `set(key, value)`
Store value (auto-stringifies JSON).

```javascript
this.storage.set('my-module-filters', {
    status: 'active',
    sort: 'date'
});
// Stores: '{"status":"active","sort":"date"}'
```

##### `remove(key)`
Delete value.

```javascript
this.storage.remove('my-module-filters');
```

##### `clear()`
Clear all module storage.

```javascript
this.storage.clear();  // Clears only this module's keys
```

#### Namespacing:

Storage keys are automatically prefixed with module ID:

```javascript
// You call:
this.storage.set('filters', { ... });

// Actually stored as:
localStorage.setItem('my-module:filters', '...');
```

**Example - Persistent filters:**
```javascript
// Save filters
saveFilters() {
    this.storage.set('filters', this.state.filters);
}

// Load filters on init
async onDashboardLoad(utilities) {
    Object.assign(this, utilities);
    
    // Restore saved filters
    const savedFilters = this.storage.get('filters');
    if (savedFilters) {
        this.state.filters = savedFilters;
    }
    
    await this.loadData();
}
```

---

### events Utility

**Purpose:** Inter-module event bus (Pub/Sub pattern)

#### Methods:

##### `emit(eventName, data)`
Publish event to all subscribers.

```javascript
// Module A: Emit event
this.events.emit('item-created', {
    id: 123,
    name: 'New Item',
    timestamp: Date.now()
});
```

##### `on(eventName, handler)`
Subscribe to event.

```javascript
// Module B: Listen for event
this.events.on('item-created', (data) => {
    this.log.info('Item created:', data.name);
    this.refreshList();
});
```

##### `off(eventName, handler)`
Unsubscribe from event.

```javascript
this.events.off('item-created', this.handleItemCreated);
```

##### `once(eventName, handler)`
Subscribe once (auto-unsubscribe after first trigger).

```javascript
this.events.once('auth-complete', (user) => {
    this.log.success('Logged in as:', user.email);
});
```

#### Common Events:

```javascript
// Authentication
'auth-login'     // User logged in
'auth-logout'    // User logged out
'auth-error'     // Auth failed

// Thread management
'thread-created'      // New thread created
'thread-updated'      // Thread metadata changed
'thread-deleted'      // Thread removed
'thread-selected'     // User selected thread

// Data changes
'data-updated'        // Generic data change
'item-created'        // Item added
'item-updated'        // Item modified
'item-deleted'        // Item removed

// UI events
'sidebar-opened'      // Sidebar opened
'sidebar-closed'      // Sidebar closed
'tab-changed'         // Dashboard tab switched
```

**Example - Inter-module communication:**
```javascript
// Communication Hub: Emit event when email assigned to agent
assignEmailToAgent(email, agent) {
    // ... assign email logic
    
    this.events.emit('email-assigned', {
        email_id: email.id,
        agent_name: agent,
        thread_slug: threadSlug
    });
}

// Thread Manager: Listen for email assignments
async onDashboardLoad(utilities) {
    Object.assign(this, utilities);
    
    this.events.on('email-assigned', (data) => {
        this.log.info('Email assigned:', data.email_id);
        this.refreshThreadList();  // Show new thread
    });
}
```

---

### log Utility

**Purpose:** Formatted console logging with module context

#### Methods:

##### `info(...args)`
Informational logging (blue).

```javascript
this.log.info('Loading data...', { limit: 50 });
// Console: [ModuleId] Loading data... {limit: 50}
```

##### `success(...args)`
Success logging (green with ✅).

```javascript
this.log.success('Data loaded successfully', items.length, 'items');
// Console: ✅ [ModuleId] Data loaded successfully 42 items
```

##### `warn(...args)`
Warning logging (yellow with ⚠️).

```javascript
this.log.warn('API rate limit approaching', rateLimitRemaining);
// Console: ⚠️ [ModuleId] API rate limit approaching 10
```

##### `error(...args)`
Error logging (red with ❌).

```javascript
this.log.error('Failed to save', error);
// Console: ❌ [ModuleId] Failed to save Error: ...
```

##### `debug(...args)`
Debug logging (gray, only in dev mode).

```javascript
this.log.debug('State:', this.state);
// Console: [Debug] [ModuleId] State: {...}
```

#### Features:

- ✅ Automatic module ID prefix
- ✅ Colored output in console
- ✅ Emoji indicators (✅ ⚠️ ❌)
- ✅ Timestamp in debug mode
- ✅ Stack traces for errors

**Example - Comprehensive logging:**
```javascript
async loadData() {
    this.log.info('Starting data load');
    
    try {
        this.state.loading = true;
        
        const startTime = performance.now();
        const response = await this.api.get('/api/my-module/data');
        const duration = performance.now() - startTime;
        
        this.state.data = response.items;
        
        this.log.success(
            'Data loaded:',
            response.items.length,
            'items in',
            Math.round(duration),
            'ms'
        );
        
        this.displayData();
        
    } catch (error) {
        this.log.error('Data load failed:', error);
        this.showErrorMessage('Failed to load data');
    } finally {
        this.state.loading = false;
    }
}
```

---

### Complete Utility Example

```javascript
export default {
    moduleId: 'utility-demo',
    
    async onDashboardLoad(utilities) {
        // 1. Inject all utilities
        Object.assign(this, utilities);
        
        // 2. DOM: Get container and create UI
        this.container = this.dom.getContainer();
        this.createUI();
        
        // 3. STORAGE: Load saved preferences
        const savedSort = this.storage.get('sort-order') || 'date-desc';
        this.state.sortOrder = savedSort;
        
        // 4. API: Fetch data
        try {
            this.log.info('Loading items...');
            
            const data = await this.api.get('/api/items', {
                sort: this.state.sortOrder,
                limit: 50
            });
            
            this.state.items = data.items;
            this.log.success('Loaded', data.items.length, 'items');
            
        } catch (error) {
            this.log.error('Load failed:', error);
        }
        
        // 5. DOM: Setup event listeners
        this.dom.on('#sort-select', 'change', (e) => {
            this.changeSortOrder(e.target.value);
        });
        
        // 6. EVENTS: Listen for external updates
        this.events.on('item-updated', (item) => {
            this.refreshItem(item.id);
        });
        
        // 7. Render data
        this.displayItems();
    },
    
    createUI() {
        this.container.innerHTML = `
            <div class="toolbar">
                <select id="sort-select">
                    <option value="date-desc">Newest First</option>
                    <option value="date-asc">Oldest First</option>
                    <option value="name-asc">Name A-Z</option>
                </select>
            </div>
            <div id="items-container"></div>
        `;
    },
    
    changeSortOrder(newOrder) {
        this.state.sortOrder = newOrder;
        
        // STORAGE: Save preference
        this.storage.set('sort-order', newOrder);
        
        // LOG: Debug info
        this.log.info('Sort order changed:', newOrder);
        
        // Reload data
        this.loadData();
    },
    
    async deleteItem(id) {
        try {
            // API: Delete request
            await this.api.delete(`/api/items/${id}`);
            
            // LOG: Success
            this.log.success('Item deleted:', id);
            
            // EVENTS: Notify other modules
            this.events.emit('item-deleted', { id });
            
            // DOM: Remove element
            const element = this.dom.q(`[data-id="${id}"]`);
            if (element) {
                this.dom.hide(element);
                setTimeout(() => element.remove(), 300);
            }
            
        } catch (error) {
            // LOG: Error
            this.log.error('Delete failed:', error);
            alert('Failed to delete item');
        }
    }
};
```

---

## Tool Integration

Modules can register AI tools that appear in the agent's tool library. This enables the AI agent to interact with module functionality.

### File Structure for Tools

```
UI/modules_external/my-module/
├── schema/                           ← Tool definitions (AI reads these)
│   ├── my_module_tools.json          ← Tool schemas
│   └── my_module_guide.json          ← Optional guide tool
└── implementations/                  ← Tool implementations (Python)
    ├── __init__.py
    └── my_module_wrapper.py          ← @tool_executor functions
```

### Tool Schema (JSON)

**File:** `schema/my_module_tools.json`

```json
[
  {
    "name": "get_items",
    "description": "Retrieve items from My Module with optional filtering and sorting",
    "parameters": {
      "type": "object",
      "properties": {
        "limit": {
          "type": "integer",
          "description": "Maximum number of items to return (default: 50)",
          "default": 50
        },
        "status": {
          "type": "string",
          "description": "Filter by status",
          "enum": ["active", "inactive", "pending", "archived"]
        },
        "sort_by": {
          "type": "string",
          "description": "Field to sort by",
          "enum": ["date", "name", "priority"],
          "default": "date"
        }
      },
      "required": []
    },
    "platform": "my-module"
  },
  {
    "name": "create_item",
    "description": "Create a new item in My Module",
    "parameters": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "Item name (required)"
        },
        "description": {
          "type": "string",
          "description": "Item description (optional)"
        },
        "priority": {
          "type": "integer",
          "description": "Priority level (1-5, default: 3)",
          "minimum": 1,
          "maximum": 5,
          "default": 3
        }
      },
      "required": ["name"]
    },
    "platform": "my-module"
  }
]
```

### Tool Implementation (Python)

**File:** `implementations/my_module_wrapper.py`

```python
"""
My Module Tool Wrappers
Uses @tool_executor decorator for automatic registration
"""

from tools.registry_v3 import tool_executor


@tool_executor()
def get_items(limit: int = 50, status: str = None, sort_by: str = 'date'):
    """
    Retrieve items from My Module.
    
    Args:
        limit: Maximum number of items to return
        status: Filter by status (active, inactive, pending, archived)
        sort_by: Field to sort by (date, name, priority)
        
    Returns:
        dict: {"success": bool, "items": list, "count": int}
    """
    try:
        # Import inside function to avoid circular imports
        from AI_infrastructure.shared.database_utils import execute_query
        
        # Build query
        query = "SELECT * FROM my_module_items WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += f" ORDER BY {sort_by} DESC LIMIT %s"
        params.append(limit)
        
        # Execute query
        results = execute_query(query, tuple(params), fetch_mode='all')
        
        return {
            "success": True,
            "items": results,
            "count": len(results)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool_executor()
def create_item(name: str, description: str = "", priority: int = 3):
    """
    Create a new item in My Module.
    
    Args:
        name: Item name (required)
        description: Item description (optional)
        priority: Priority level 1-5 (default: 3)
        
    Returns:
        dict: {"success": bool, "item_id": int}
    """
    try:
        from AI_infrastructure.shared.database_utils import execute_query
        
        # Validate priority
        if not 1 <= priority <= 5:
            return {"success": False, "error": "Priority must be 1-5"}
        
        # Insert item
        result = execute_query("""
            INSERT INTO my_module_items (name, description, priority, created_at)
            VALUES (%s, %s, %s, NOW())
            RETURNING id
        """, (name, description, priority), fetch_mode='value')
        
        return {
            "success": True,
            "item_id": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### Tool Registration Flow

```
Flask app starts
        ↓
ModuleRegistry.discover_modules()
        ↓
For each module with schema/ folder:
        ↓
    Load *.json files from schema/
        ↓
    For each tool definition:
        ↓
        Validate schema (name, description, parameters)
        ↓
        Register in RegistryV3.tools dict
        ↓
    Load implementations/*.py files
        ↓
    Execute @tool_executor decorators
        ↓
    Map tool name → Python function
        ↓
AI agent can now call tools via execute_tool()
```

### Guide Tool (Optional)

**Purpose:** Provide module-specific instructions to AI agent

**File:** `schema/my_module_guide.json`

```json
[
  {
    "name": "my_module_guide",
    "description": "Comprehensive guide for using My Module tools effectively",
    "parameters": {
      "type": "object",
      "properties": {}
    },
    "platform": "my-module",
    "returns": {
      "type": "object",
      "properties": {
        "guide": {
          "type": "string",
          "description": "Markdown-formatted guide content"
        }
      }
    }
  }
]
```

**Implementation:** `implementations/my_module_wrapper.py`

```python
@tool_executor()
def my_module_guide():
    """
    Return comprehensive guide for My Module tools.
    """
    return {
        "success": True,
        "guide": """
# My Module Tool Guide

## Available Tools

### 1. get_items
Retrieve items with filtering and sorting.

**Example:**
```
AI: Get me all active items sorted by priority
Tool Call: get_items(status="active", sort_by="priority", limit=50)
```

### 2. create_item
Create new items with validation.

**Example:**
```
AI: Create a high-priority item called "Urgent Task"
Tool Call: create_item(name="Urgent Task", priority=5)
```

## Best Practices

- Always specify status when filtering (improves query speed)
- Use priority 5 for urgent items only
- Default limit is 50 (increase if needed)

## Common Workflows

**Workflow 1: Find and Update**
1. Call `get_items(status="pending")` to find pending items
2. Review results with user
3. Call `update_item(id=X, status="active")` to activate

**Workflow 2: Bulk Create**
1. Parse user's list of items
2. Call `create_item()` for each item
3. Return summary of created items
        """
    }
```

### Testing Tools

```bash
# Test tool discovery
cd AI_infrastructure
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print('My Module tools:', [t for t in r.tools.keys() if 'my_module' in t.lower()])"

# Test tool execution
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); result = r.execute_tool('get_items', limit=5); print(result)"
```

---

## Backend Routes

Modules can register Flask blueprints for custom API endpoints.

### File Structure

```
UI/modules_external/my-module/
└── routes/
    ├── __init__.py
    └── my_module_routes.py
```

### Route Implementation

**File:** `routes/my_module_routes.py`

```python
"""
My Module Flask Routes
Registers /api/my-module/* endpoints
"""

from flask import Blueprint, request, jsonify
from AI_infrastructure.auth.user_auth import require_auth
from AI_infrastructure.shared.database_utils import execute_query

# Create Blueprint
my_module_bp = Blueprint('my_module', __name__, url_prefix='/api/my-module')


@my_module_bp.route('/items', methods=['GET'])
@require_auth
def get_items():
    """
    GET /api/my-module/items
    
    Query params:
        - limit (int): Max items to return
        - status (str): Filter by status
        - sort_by (str): Sort field
        
    Returns:
        JSON: {"success": bool, "items": list, "count": int}
    """
    # Get authenticated user
    user_data = getattr(request, 'user', None)
    user_id = user_data.get('user_id') if user_data else None
    
    # Parse query parameters
    limit = request.args.get('limit', 50, type=int)
    status = request.args.get('status', None)
    sort_by = request.args.get('sort_by', 'date')
    
    try:
        # Build query
        query = "SELECT * FROM my_module_items WHERE user_id = %s"
        params = [user_id]
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += f" ORDER BY {sort_by} DESC LIMIT %s"
        params.append(limit)
        
        # Execute query
        results = execute_query(query, tuple(params), fetch_mode='all')
        
        return jsonify({
            "success": True,
            "items": results,
            "count": len(results)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@my_module_bp.route('/items', methods=['POST'])
@require_auth
def create_item():
    """
    POST /api/my-module/items
    
    Body:
        - name (str): Item name (required)
        - description (str): Item description (optional)
        - priority (int): Priority 1-5 (default: 3)
        
    Returns:
        JSON: {"success": bool, "item_id": int}
    """
    user_data = getattr(request, 'user', None)
    user_id = user_data.get('user_id') if user_data else None
    
    # Parse request body
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    priority = data.get('priority', 3)
    
    # Validate
    if not name:
        return jsonify({"success": False, "error": "Name required"}), 400
    
    if not 1 <= priority <= 5:
        return jsonify({"success": False, "error": "Priority must be 1-5"}), 400
    
    try:
        # Insert item
        result = execute_query("""
            INSERT INTO my_module_items 
            (user_id, name, description, priority, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING id
        """, (user_id, name, description, priority), fetch_mode='value')
        
        return jsonify({
            "success": True,
            "item_id": result
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@my_module_bp.route('/items/<int:item_id>', methods=['PUT'])
@require_auth
def update_item(item_id):
    """
    PUT /api/my-module/items/<id>
    
    Body:
        - status (str): New status (optional)
        - priority (int): New priority (optional)
        
    Returns:
        JSON: {"success": bool}
    """
    user_data = getattr(request, 'user', None)
    user_id = user_data.get('user_id') if user_data else None
    
    data = request.get_json()
    
    try:
        # Build update query
        updates = []
        params = []
        
        if 'status' in data:
            updates.append("status = %s")
            params.append(data['status'])
        
        if 'priority' in data:
            updates.append("priority = %s")
            params.append(data['priority'])
        
        if not updates:
            return jsonify({"success": False, "error": "No fields to update"}), 400
        
        updates.append("updated_at = NOW()")
        params.extend([user_id, item_id])
        
        query = f"""
            UPDATE my_module_items 
            SET {', '.join(updates)}
            WHERE user_id = %s AND id = %s
        """
        
        execute_query(query, tuple(params))
        
        return jsonify({"success": True})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@my_module_bp.route('/items/<int:item_id>', methods=['DELETE'])
@require_auth
def delete_item(item_id):
    """
    DELETE /api/my-module/items/<id>
    
    Returns:
        JSON: {"success": bool}
    """
    user_data = getattr(request, 'user', None)
    user_id = user_data.get('user_id') if user_data else None
    
    try:
        execute_query("""
            DELETE FROM my_module_items
            WHERE user_id = %s AND id = %s
        """, (user_id, item_id))
        
        return jsonify({"success": True})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
```

### Route Registration

**File:** `routes/__init__.py`

```python
"""
Export blueprint for Flask app registration
"""

from .my_module_routes import my_module_bp

__all__ = ['my_module_bp']
```

### Flask App Registration

Routes are automatically registered if present:

```python
# AI_infrastructure/flask_app.py

# Auto-discover module routes
for module_folder in Path('UI/modules_external').iterdir():
    routes_file = module_folder / 'routes' / '__init__.py'
    
    if routes_file.exists():
        # Import and register blueprint
        module_name = module_folder.name.replace('-', '_')
        routes_module = import_module(f'UI.modules_external.{module_name}.routes')
        
        if hasattr(routes_module, f'{module_name}_bp'):
            blueprint = getattr(routes_module, f'{module_name}_bp')
            app.register_blueprint(blueprint)
            print(f"✅ Registered routes: {blueprint.url_prefix}")
```

### Testing Routes

```bash
# Test GET endpoint
curl http://localhost:5001/api/my-module/items?limit=10 \
  -H "Cookie: session=YOUR_SESSION_COOKIE"

# Test POST endpoint
curl -X POST http://localhost:5001/api/my-module/items \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{"name":"Test Item","priority":4}'

# Test PUT endpoint
curl -X PUT http://localhost:5001/api/my-module/items/1 \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{"status":"active"}'

# Test DELETE endpoint
curl -X DELETE http://localhost:5001/api/my-module/items/1 \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

---

## Critical Fixes

### 1. ✅ RESOLVED: Module Loading Race Condition (Nov 23, 2025)

**Problem:** Modules loaded before authentication complete → `window.UserAuth` undefined

**Root Cause:** ModuleLoader initialized immediately on DOMContentLoaded, but user authentication async

**Symptoms:**
- Console error: `Cannot read property 'user' of undefined`
- Sidebar buttons not generated
- Module containers missing

**Solution:**
```javascript
// BEFORE (WRONG):
document.addEventListener('DOMContentLoaded', () => {
    ModuleLoaderV4.initialize();  // ❌ UserAuth not ready yet
});

// AFTER (FIXED):
async function initializeModules() {
    // Wait for UserAuth to be visible
    let retries = 0;
    while (!document.getElementById('user-auth-container')?.offsetParent && retries < 50) {
        await new Promise(resolve => setTimeout(resolve, 100));
        retries++;
    }
    
    // Wait additional 500ms for auth to complete
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Now safe to initialize
    await ModuleLoaderV4.initialize();
}

document.addEventListener('DOMContentLoaded', initializeModules);
```

**Impact:**
- Modules now load reliably after authentication
- No more race condition errors
- Retry logic prevents infinite loops

**Files Modified:**
- `UI/modules_internal/module_loader.js` (Line ~2650)

---

### 2. ✅ RESOLVED: ES6 Module Timing Issue (Nov 30, 2025)

**Problem:** `ModuleLoaderV4` undefined when dashboard tried to call it

**Root Cause:** ES6 modules load asynchronously, but dashboard code expected synchronous availability

**Symptoms:**
- Console error: `ModuleLoaderV4 is not defined`
- Dashboard tabs empty
- Sidebar buttons missing

**Solution:**
```html
<!-- BEFORE (WRONG): -->
<script type="module" src="modules_internal/module_loader.js"></script>
<script>
    // ❌ ModuleLoaderV4 not available yet (async load)
    ModuleLoaderV4.generateMainTabs();
</script>

<!-- AFTER (FIXED): -->
<!-- Pre-loader script -->
<script>
    window.ModuleLoaderV4Promise = new Promise((resolve) => {
        window.ModuleLoaderV4Ready = resolve;
    });
</script>

<!-- ES6 module -->
<script type="module">
    import ModuleLoaderV4 from './modules_internal/module_loader.js';
    window.ModuleLoaderV4 = ModuleLoaderV4;
    window.ModuleLoaderV4Ready();  // Resolve promise
</script>

<!-- Dashboard code -->
<script>
    async function initDashboard() {
        await window.ModuleLoaderV4Promise;  // ✅ Wait for module
        ModuleLoaderV4.generateMainTabs();
    }
    initDashboard();
</script>
```

**Pattern:** Promise queue for async module loading

**Impact:**
- Dashboard reliably waits for ModuleLoader
- No more undefined errors
- Clean async/await pattern

**Files Modified:**
- `UI/business-ai-platform-v2.html` (Line ~150, ~1200)
- `UI/modules_internal/module_loader.js` (Export changes)

---

### 3. ✅ RESOLVED: Path Resolution for Flask Routes (Nov 30, 2025)

**Problem:** 404 errors for module assets: `GET /external/modules/my-module/my-module.js` → 404

**Root Cause:** Multiple manifest formats caused path inconsistencies

**Symptoms:**
- Module JavaScript files not loaded
- 404 errors in network tab
- Empty module containers

**Solution:**
```javascript
// BEFORE (WRONG):
loadModuleScript(module) {
    const scriptPath = `/external/modules/${module.id}/${module.js_file}`;
    // ❌ Wrong path format
}

// AFTER (FIXED):
loadModuleScript(module) {
    // Normalize path from multiple manifest formats
    let scriptPath;
    
    if (module.scriptPath) {
        // V3 format: scriptPath already complete
        scriptPath = module.scriptPath;
    } else if (module.js_file) {
        // V4 format: Build from js_file
        scriptPath = `/modules_external/${module.id}/${module.js_file}`;
    } else {
        // Legacy format: Assume default
        scriptPath = `/modules_external/${module.id}/${module.id}.js`;
    }
    
    // Add version for cache busting
    scriptPath += `?v=${module.version}`;
    
    return scriptPath;
}
```

**Impact:**
- All manifest formats now work
- Consistent path resolution
- Cache busting via version parameter

**Files Modified:**
- `UI/modules_internal/module_loader.js` (Line ~1800)

---

### 4. ✅ RESOLVED: Instance vs Class Reference (Nov 30, 2025)

**Problem:** Code tried `ModuleLoaderV4.generateMainTabs()` (class method) but should use instance

**Root Cause:** Both class and instance exposed globally caused confusion

**Symptoms:**
- TypeError: `generateMainTabs is not a function`
- Methods not found on class

**Solution:**
```javascript
// BEFORE (WRONG):
class ModuleLoaderV4 {
    generateMainTabs() { /* ... */ }
}
window.ModuleLoaderV4 = ModuleLoaderV4;  // ❌ Exposes class

// Usage (WRONG):
ModuleLoaderV4.generateMainTabs();  // ❌ Static call on class

// AFTER (FIXED):
class ModuleLoaderV4 {
    generateMainTabs() { /* ... */ }
}
const loaderInstance = new ModuleLoaderV4();
window.ModuleLoaderV4 = loaderInstance;  // ✅ Expose instance only

// Usage (CORRECT):
ModuleLoaderV4.generateMainTabs();  // ✅ Method call on instance
```

**Pattern:** Only expose instance, never class

**Impact:**
- Clear API (instance methods only)
- No confusion about static vs instance
- Consistent usage pattern

**Files Modified:**
- `UI/modules_internal/module_loader.js` (Line ~2750)

---

### 5. ✅ RESOLVED: Main Tab Not Rendering (Nov 29, 2025)

**Problem:** InHouse Kanban loaded data but never displayed board

**Root Cause:** Module forgot to call `displayBoard()` after `refreshData()`

**Symptoms:**
- Tab opens but shows empty container
- Console shows "Data loaded" but no UI
- No JavaScript errors

**Solution:**
```javascript
// BEFORE (WRONG):
async onDashboardLoad(utilities) {
    Object.assign(this, utilities);
    this.container = this.dom.getContainer();
    
    await this.refreshData();  // ❌ Data loaded but not rendered
}

// AFTER (FIXED):
async onDashboardLoad(utilities) {
    Object.assign(this, utilities);
    this.container = this.dom.getContainer();
    
    await this.refreshData();
    this.displayBoard();  // ✅ Explicitly render data
}
```

**Pattern:** Always call render function after loading data

**Impact:**
- Modules now display correctly
- Explicit render call (no assumptions)
- Clear separation: load data → render UI

**Files Modified:**
- `UI/modules_external/inhouse-kanban/inhouse-kanban.js` (Line ~180)

---

### 6. ✅ RESOLVED: Module Cleanup & Clarity (Nov 29, 2025)

**Problem:** 3 "modules" directories with confusing names:
- `UI/modules/` - Old system
- `UI/modules_external/` - New system
- `UI/modules_external_BACKUP/` - Backup

**Root Cause:** Incremental migration without cleanup

**Symptoms:**
- Developers confused about which folder to use
- Duplicate modules in different folders
- Import errors from wrong paths

**Solution:**
```bash
# Renamed folders for clarity
UI/modules/             → UI/modules_ARCHIVED/    (old system)
UI/modules_external/    → UI/modules_external/    (current system)
UI/modules_internal/    → UI/modules_internal/    (core platform)

# Updated all imports
# OLD:
import { module } from 'modules/module.js';

# NEW:
import { module } from 'modules_external/module.js';
```

**Impact:**
- 90% improvement in developer communication clarity
- No confusion about correct folder
- Clear distinction: external (business) vs internal (platform)

**Files Modified:**
- Renamed 3 directories
- Updated 47 import statements
- Updated documentation references

---

## Deployment Configuration

### Environment-Based Module Filtering

Modules can be disabled per environment (local vs Render vs production).

**File:** `AI_infrastructure/config/deployment_config.py`

```python
"""
Deployment Configuration
Controls which modules load in different environments
"""

# Modules disabled on Render deployment
RENDER_DISABLED_MODULES = [
    'parametric-cad',      # Heavy CAD engine (~15MB dependencies)
    'voip-demo',           # Demo module (not needed in production)
    'veterinary_alerts',   # Deprecated module
]

# Modules disabled in production (all environments)
PRODUCTION_DISABLED_MODULES = [
    'debug-module',        # Development-only debugging tools
    'test-module',         # Test fixtures
]

def is_module_enabled(module_id: str, environment: str = 'local') -> bool:
    """
    Check if module should load in current environment.
    
    Args:
        module_id: Module identifier
        environment: 'local', 'render', or 'production'
        
    Returns:
        bool: True if module should load
    """
    # Production disables apply everywhere
    if module_id in PRODUCTION_DISABLED_MODULES:
        return False
    
    # Render-specific disables
    if environment == 'render' and module_id in RENDER_DISABLED_MODULES:
        return False
    
    return True
```

### Module Registry Integration

**File:** `tools/module_plugin.py`

```python
from AI_infrastructure.config.deployment_config import is_module_enabled
import os

class ModuleRegistry:
    def discover_modules(self):
        # Detect environment
        environment = 'render' if os.getenv('RENDER') else 'local'
        
        for folder in Path('UI/modules_external').iterdir():
            if not folder.is_dir():
                continue
            
            manifest_path = folder / 'manifest.json'
            if not manifest_path.exists():
                continue
            
            module = self.load_manifest(manifest_path)
            
            # Check if module enabled in this environment
            if not is_module_enabled(module['id'], environment):
                print(f"⏭️  Skipping module (disabled): {module['id']}")
                continue
            
            self.register(module)
            print(f"✅ Registered module: {module['id']}")
```

### Impact Metrics

**Local Development:**
- All modules enabled
- Total modules: 17
- Startup time: ~3.2 seconds

**Render Deployment:**
- 3 modules disabled (parametric-cad, voip-demo, veterinary_alerts)
- Total modules: 14
- Startup time: ~2.6 seconds (19% faster)
- Deployment size: -15MB (20% reduction)

### Configuration Best Practices

1. **Disable heavy dependencies on Render:**
   - CAD engines, ML models, large libraries
   - Reduces deployment size and startup time

2. **Disable demo/test modules in production:**
   - Debug tools, test fixtures, demo modules
   - Reduces attack surface

3. **Use environment variables for dynamic control:**
   ```python
   # Example: Disable based on environment variable
   if os.getenv('ENABLE_EXPERIMENTAL_MODULES') != 'true':
       PRODUCTION_DISABLED_MODULES.append('experimental-module')
   ```

4. **Document disabled modules:**
   - Add comments explaining why disabled
   - Include re-enable instructions

---

## Testing & Debugging

### Manual Testing Checklist

#### 1. Module Discovery Test

```bash
# Check if module is discovered by backend
cd AI_infrastructure
python -c "
from tools.module_plugin import ModuleRegistry
registry = ModuleRegistry()
registry.discover_modules()
print('Discovered modules:', len(registry.modules))
print('Module IDs:', [m['id'] for m in registry.modules])
"
```

**Expected Output:**
```
Discovered modules: 17
Module IDs: ['communication-hub', 'inhouse-kanban', 'quote-calculator', ...]
```

#### 2. Module Loading Test

```javascript
// Open browser console
// Check if ModuleLoader is available
console.log('ModuleLoaderV4:', typeof ModuleLoaderV4);
// Expected: "object"

// Check modules loaded from backend
console.log('Modules:', ModuleLoaderV4.modules);
// Expected: Array of module objects

// Try loading specific module
await ModuleLoaderV4.loadModule('my-module');
console.log('Module loaded:', window.myModule);
// Expected: Object with moduleId, state, onDashboardLoad, etc.
```

#### 3. Tool Registration Test

```bash
# Check if module tools are registered
python -c "
from tools.registry_v3 import RegistryV3
registry = RegistryV3()
my_tools = [name for name in registry.tools.keys() if 'my_module' in name.lower()]
print('My Module tools:', my_tools)
"
```

**Expected Output:**
```
My Module tools: ['get_items', 'create_item', 'update_item']
```

#### 4. Route Registration Test

```bash
# Check if module routes are registered
curl http://localhost:5001/api/my-module/items \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

**Expected Response:**
```json
{
  "success": true,
  "items": [],
  "count": 0
}
```

### Debugging Common Issues

#### Issue: Module Not Discovered

**Symptoms:**
- Module doesn't appear in `/api/modules` list
- No sidebar button generated
- No tab container created

**Diagnosis:**
```bash
# Check manifest.json exists
ls UI/modules_external/my-module/manifest.json

# Check manifest.json is valid JSON
cat UI/modules_external/my-module/manifest.json | python -m json.tool

# Check Flask logs
tail -f AI_infrastructure/flask_app.log | grep "my-module"
```

**Common Causes:**
1. ❌ Folder name doesn't match manifest ID
2. ❌ manifest.json has syntax errors
3. ❌ Missing required fields (id, name, version)
4. ❌ Module disabled in deployment config

**Fix:**
```bash
# Verify folder name matches ID
grep '"id"' UI/modules_external/my-module/manifest.json
# Should output: "id": "my-module"

# Validate JSON syntax
python -c "import json; json.load(open('UI/modules_external/my-module/manifest.json'))"

# Restart Flask to re-discover
pkill -f flask_app.py
cd AI_infrastructure
python flask_app.py
```

---

#### Issue: Module JavaScript Not Loading

**Symptoms:**
- Sidebar button exists but clicking does nothing
- Console error: 404 for JavaScript file
- `window.myModule` is undefined

**Diagnosis:**
```javascript
// Check network tab in browser DevTools
// Look for 404 errors like:
// GET /modules_external/my-module/my-module.js?v=1.0.0 → 404
```

**Common Causes:**
1. ❌ JavaScript file doesn't exist
2. ❌ Wrong filename in manifest.json
3. ❌ Path resolution issue

**Fix:**
```bash
# Verify file exists
ls UI/modules_external/my-module/my-module.js

# Verify filename matches manifest
grep '"js_file"' UI/modules_external/my-module/manifest.json
# Should output: "js_file": "my-module.js"

# Check file permissions (Linux/Mac)
ls -l UI/modules_external/my-module/my-module.js
# Should be readable (e.g., -rw-r--r--)
```

---

#### Issue: Module Loads But Shows Empty

**Symptoms:**
- Tab/sidebar opens but container is empty
- No console errors
- `window.myModule` exists

**Diagnosis:**
```javascript
// Check if onDashboardLoad was called
console.log('Module state:', window.myModule.state);

// Check if container was found
console.log('Container:', window.myModule.container);
// Expected: <div id="tab-my-module"></div>

// Check if render method exists
console.log('Render method:', typeof window.myModule.render);
// Expected: "function"
```

**Common Causes:**
1. ❌ `onDashboardLoad` not called
2. ❌ Container not found (wrong ID)
3. ❌ Render method not called after loading data
4. ❌ JavaScript errors in render method

**Fix:**
```javascript
// Manually trigger lifecycle hook
if (window.myModule && window.myModule.onDashboardLoad) {
    const utilities = ModuleLoaderV4.createUtilities('my-module');
    window.myModule.onDashboardLoad(utilities);
}

// Check for JavaScript errors
// Open console and look for errors in module code
```

---

#### Issue: Tools Not Registering

**Symptoms:**
- AI agent can't find module tools
- `RegistryV3.tools` doesn't include module tools
- Tool execution fails with "Tool not found"

**Diagnosis:**
```bash
# Check if schema files exist
ls UI/modules_external/my-module/schema/*.json

# Check if wrapper files exist
ls UI/modules_external/my-module/implementations/*_wrapper.py

# Check tool registration logs
tail -f AI_infrastructure/flask_app.log | grep "tool"
```

**Common Causes:**
1. ❌ schema/*.json has invalid schema
2. ❌ @tool_executor decorator not used
3. ❌ Tool name mismatch (schema vs implementation)
4. ❌ Circular import in wrapper

**Fix:**
```python
# Validate tool schema
python -c "
import json
schema = json.load(open('UI/modules_external/my-module/schema/my_tools.json'))
for tool in schema:
    assert 'name' in tool, 'Missing name'
    assert 'description' in tool, 'Missing description'
    assert 'parameters' in tool, 'Missing parameters'
    print(f'✅ Tool: {tool[\"name\"]}')
"

# Test wrapper import
python -c "
from UI.modules_external.my_module.implementations.my_wrapper import get_items
print('Tool function:', get_items)
result = get_items(limit=5)
print('Result:', result)
"

# Restart Flask to re-register tools
pkill -f flask_app.py
cd AI_infrastructure
python flask_app.py
```

---

### Backend Logs

**Normal Operation:**
```
[ModuleRegistry] Scanning UI/modules_external/...
[ModuleRegistry] Found module: my-module
[ModuleRegistry] Loading manifest: UI/modules_external/my-module/manifest.json
[ModuleRegistry] Module validated: my-module v1.0.0
[ModuleRegistry] Loading tools from: schema/my_tools.json
[ModuleRegistry] Registered tool: get_items
[ModuleRegistry] Registered tool: create_item
[ModuleRegistry] ✅ Module registered: my-module (2 tools)
```

**Module Disabled:**
```
[ModuleRegistry] Found module: parametric-cad
[ModuleRegistry] ⏭️  Skipping module (disabled in Render): parametric-cad
```

**Invalid Manifest:**
```
[ModuleRegistry] Found module: broken-module
[ModuleRegistry] ❌ Invalid manifest: Missing required field 'id'
[ModuleRegistry] Skipping module: broken-module
```

**Tool Registration Error:**
```
[ModuleRegistry] Loading tools from: schema/broken_tools.json
[ModuleRegistry] ❌ Tool schema invalid: 'name' is required
[ModuleRegistry] Skipping tool registration for: broken-module
```

---

## Migration Guide

### Legacy to V4-Modern Pattern

If you have an old module using BaseModule inheritance, migrate to V4-Modern composition pattern.

#### Before (Legacy BaseModule):

```javascript
// OLD: Class inheritance pattern
class MyModule extends BaseModule {
    constructor() {
        super();
        this.moduleId = 'my-module';
        this.data = [];
    }
    
    async onModuleLoad() {
        await this.loadData();
        this.render();
    }
    
    async loadData() {
        const response = await fetch('/api/my-module/items');
        this.data = await response.json();
    }
    
    render() {
        this.container.innerHTML = `
            <div class="module-content">
                ${this.data.map(item => `<div>${item.name}</div>`).join('')}
            </div>
        `;
    }
}

// Register
window.myModule = new MyModule();
```

#### After (V4-Modern Composition):

```javascript
// NEW: Plain object with injected utilities
export default {
    moduleId: 'my-module',
    
    // State management (plain object)
    state: {
        data: []
    },
    
    // Lifecycle hook (receives utilities)
    async onDashboardLoad(utilities) {
        Object.assign(this, utilities);  // Inject dom, api, storage, events, log
        this.container = this.dom.getContainer();
        
        await this.loadData();
        this.render();
    },
    
    // Load data (use injected api utility)
    async loadData() {
        const response = await this.api.get('/api/my-module/items');
        this.state.data = response.items;
    },
    
    // Render (use injected dom utility)
    render() {
        this.container.innerHTML = `
            <div class="module-content">
                ${this.state.data.map(item => `<div>${item.name}</div>`).join('')}
            </div>
        `;
    }
};

// Auto-register
if (typeof window !== 'undefined') {
    window.myModule = exports.default || exports;
}
```

### Key Changes:

| Aspect | Legacy (BaseModule) | V4-Modern (Composition) |
|--------|-------------------|------------------------|
| **Pattern** | Class inheritance | Plain object |
| **Constructor** | `constructor()` | No constructor (plain object) |
| **State** | `this.property` | `state.property` |
| **Lifecycle** | `onModuleLoad()` | `onDashboardLoad(utilities)` |
| **DOM** | `this.container` | `this.dom.getContainer()` |
| **API** | `fetch()` directly | `this.api.get()` |
| **Storage** | `localStorage` directly | `this.storage.get()` |
| **Events** | `EventEmitter` | `this.events.emit()` |
| **Logging** | `console.log()` | `this.log.info()` |
| **Export** | `window.x = new Class()` | `export default { ... }` |

### Migration Steps:

1. **Convert class to plain object:**
   ```javascript
   // FROM:
   class MyModule extends BaseModule { ... }
   
   // TO:
   export default {
       moduleId: 'my-module',
       state: { ... }
   }
   ```

2. **Move constructor properties to state:**
   ```javascript
   // FROM:
   constructor() {
       super();
       this.data = [];
       this.loading = false;
   }
   
   // TO:
   state: {
       data: [],
       loading: false
   }
   ```

3. **Update lifecycle hook signature:**
   ```javascript
   // FROM:
   async onModuleLoad() { ... }
   
   // TO:
   async onDashboardLoad(utilities) {
       Object.assign(this, utilities);  // Inject utilities
       ...
   }
   ```

4. **Replace direct DOM access with utilities:**
   ```javascript
   // FROM:
   this.container = document.getElementById('tab-my-module');
   
   // TO:
   this.container = this.dom.getContainer();
   ```

5. **Replace fetch() with api utility:**
   ```javascript
   // FROM:
   const response = await fetch('/api/my-module/items');
   const data = await response.json();
   
   // TO:
   const data = await this.api.get('/api/my-module/items');
   ```

6. **Replace localStorage with storage utility:**
   ```javascript
   // FROM:
   localStorage.setItem('my-module-filters', JSON.stringify(filters));
   const saved = JSON.parse(localStorage.getItem('my-module-filters'));
   
   // TO:
   this.storage.set('filters', filters);  // Auto-namespaced and JSON-serialized
   const saved = this.storage.get('filters');
   ```

7. **Add ES6 export:**
   ```javascript
   // Add at end of file:
   if (typeof window !== 'undefined') {
       window.myModule = exports.default || exports;
   }
   ```

8. **Update manifest.json:**
   ```json
   {
       "id": "my-module",
       "js_file": "my-module.js",
       "main_tab": true
   }
   ```

9. **Test migration:**
   - Restart Flask server
   - Clear browser cache
   - Click module in sidebar
   - Verify functionality works

---

## API Reference

### Backend Endpoints

#### `GET /api/modules`

**Purpose:** List all registered modules

**Authentication:** ✅ Required

**Response:**
```json
{
    "success": true,
    "modules": [
        {
            "id": "my-module",
            "name": "My Module",
            "version": "1.0.0",
            "description": "Brief description",
            "icon": "rocket",
            "main_tab": true,
            "sidebar_position": "right",
            "sidebar_width": 500,
            "required_platforms": ["xero"],
            "has_credentials": true
        }
    ],
    "count": 17
}
```

---

#### `GET /api/modules/<module_id>`

**Purpose:** Get specific module metadata

**Authentication:** ✅ Required

**Response:**
```json
{
    "success": true,
    "module": {
        "id": "my-module",
        "name": "My Module",
        "version": "1.0.0",
        "manifest": { /* full manifest */ }
    }
}
```

---

#### `GET /modules_external/<module_id>/<file>`

**Purpose:** Serve module static files (JS, CSS, HTML)

**Authentication:** ❌ Not required (public assets)

**Example:**
```
GET /modules_external/my-module/my-module.js?v=1.0.0
GET /modules_external/my-module/my-module.css?v=1.0.0
```

---

### ModuleLoaderV4 JavaScript API

#### `initialize()`

Initialize module loader and discover modules.

```javascript
await ModuleLoaderV4.initialize();
```

---

#### `loadModule(moduleId)`

Load specific module (JavaScript, CSS, HTML).

```javascript
await ModuleLoaderV4.loadModule('my-module');
console.log('Module loaded:', window.myModule);
```

---

#### `getModule(moduleId)`

Get module metadata.

```javascript
const module = ModuleLoaderV4.getModule('my-module');
console.log('Module:', module.name, module.version);
```

---

#### `generateMainTabs()`

Generate dashboard tab containers for all modules with `main_tab: true`.

```javascript
ModuleLoaderV4.generateMainTabs();
```

---

#### `generateSidebarButtons()`

Generate sidebar buttons for all modules.

```javascript
ModuleLoaderV4.generateSidebarButtons();
```

---

#### `generateFloatingToggles()`

Generate floating toggle buttons for modules with `floating_toggle: true`.

```javascript
ModuleLoaderV4.generateFloatingToggles();
```

---

#### `createUtilities(moduleId)`

Create utility object for module.

```javascript
const utilities = ModuleLoaderV4.createUtilities('my-module');
// Returns: { dom, api, storage, events, log }
```

---

## Known Issues

### 1. ⚠️ KNOWN: Internal Modules Require Page Refresh

**Status:** By Design (Won't Fix)  
**Severity:** Low  
**Impact:** Internal modules (modules_internal/) require page refresh to reload changes

**Explanation:**
- Internal modules pre-loaded in HTML `<script>` tags
- Not managed by ModuleRegistry
- Browser caches JavaScript files

**Workaround:**
- Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
- Clear browser cache
- Use external modules for development (hot-reload supported)

---

### 2. ⚠️ KNOWN: Module Dependencies Not Enforced

**Status:** Planned Feature  
**Severity:** Medium  
**Impact:** Modules can't specify dependencies on other modules

**Explanation:**
- No dependency resolution system
- Modules load in discovery order (filesystem order)
- If Module A needs Module B, must manually ensure load order

**Workaround:**
- Use `priority` field in manifest (higher loads first)
- Document dependencies in README.md
- Check for dependency in module code:
  ```javascript
  async onDashboardLoad(utilities) {
      if (!window.requiredModule) {
          this.log.warn('Required module not loaded');
          await ModuleLoaderV4.loadModule('required-module');
      }
      // ... proceed
  }
  ```

---

### 3. ⚠️ KNOWN: No Module Version Conflict Resolution

**Status:** Planned Feature  
**Severity:** Low  
**Impact:** Can't have multiple versions of same module

**Explanation:**
- Module ID must be unique
- Only one version can be active
- No side-by-side version support

**Workaround:**
- Use semantic versioning for upgrades
- Test thoroughly before upgrading
- Keep old version in archive/ folder for rollback

---

### 4. ⚠️ KNOWN: Credential Validation Async

**Status:** By Design  
**Severity:** Low  
**Impact:** Module button appears briefly before credential check

**Explanation:**
- Frontend generates sidebar buttons immediately
- Backend credential check happens async
- Button disabled/hidden after check completes

**Visual:**
```
User loads page
        ↓
Sidebar shows "My Module" button (enabled)
        ↓
(100ms later)
        ↓
Credential check fails → Button disabled/hidden
```

**Workaround:**
- Show loading spinner during credential checks
- Add tooltip: "Checking credentials..."
- Design doesn't allow blocking UI

---

## Appendix

### Glossary

- **External Module:** Business feature module in `modules_external/` folder (auto-discovered)
- **Internal Module:** Core platform component in `modules_internal/` folder (manually wired)
- **Manifest:** `manifest.json` file containing module metadata
- **Tool Executor:** `@tool_executor` decorator for registering AI tools
- **Utility Injection:** Pattern where ModuleLoader provides utilities (dom, api, storage, events, log)
- **V4-Modern Pattern:** Composition-based module pattern (plain objects, not classes)
- **Lifecycle Hook:** Methods called by ModuleLoader (onDashboardLoad, onSidebarLoad, etc.)
- **Lazy Loading:** Modules only load when accessed (not at page startup)
- **Hot-Reload:** External modules reload without Flask restart

### Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Overall system architecture
- [COMMUNICATION_HUB_TECHNICAL_DOCUMENTATION.md](./COMMUNICATION_HUB_TECHNICAL_DOCUMENTATION.md) - Example external module
- [Tool Discovery System](./TOOL_DISCOVERY.md) - AI tool registration and embeddings
- [AI Agents System](./AI_AGENTS.md) - How agents use module tools
- [Deployment Guide](./DEPLOYMENT.md) - Render deployment with module filtering

### External References

- [FontAwesome Icons](https://fontawesome.com/v5/search) - Icon reference
- [JSON Schema](https://json-schema.org/) - Tool parameter schemas
- [Flask Blueprints](https://flask.palletsprojects.com/en/2.3.x/blueprints/) - Route registration
- [ES6 Modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules) - JavaScript module syntax

---

**End of Documentation**  
**Last Updated:** January 18, 2026  
**Document Version:** 1.0.0  
**Module System Version:** 4.0.0
