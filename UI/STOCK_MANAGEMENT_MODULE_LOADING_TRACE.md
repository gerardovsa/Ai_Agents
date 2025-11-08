# Stock Management Module Loading - Complete Code Trace

**Date:** November 8, 2025  
**Purpose:** Complete trace of how the Stock Management module loads in the UI

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [File Structure](#file-structure)
3. [Loading Sequence](#loading-sequence)
4. [Key Files Analyzed](#key-files-analyzed)
5. [Function Call Flow](#function-call-flow)
6. [Manifest Structure](#manifest-structure)
7. [Class Hierarchy](#class-hierarchy)
8. [Initialization Process](#initialization-process)
9. [Visual Flow Diagram](#visual-flow-diagram)

---

## 📊 Overview

The Stock Management module uses a **plugin-based architecture** with:
- **Main manifest** (`external/modules/manifest.json`) - Lists all available modules
- **Module-specific manifest** (`external/modules/stock-management/manifest.json`) - Module configuration
- **Module Loader** (`UI/js/module-loader.js`) - Loads modules from manifest
- **Module Manager** (`UI/js/module-manager.js`) - Registers and manages module lifecycle
- **Base Module** (`UI/js/module-base.js`) - Parent class for all modules
- **Stock Management Module** (`external/modules/stock-management/stock-management.js`) - Module implementation

---

## 📁 File Structure

```
UI/
├── js/
│   ├── module-loader.js          # Reads manifest, loads modules
│   ├── module-manager.js         # Manages module lifecycle
│   └── module-base.js            # Base class for modules
│
└── external/
    └── modules/
        ├── manifest.json          # Main manifest (lists all modules)
        │
        └── stock-management/
            ├── manifest.json      # Stock Management manifest
            ├── stock-management.js # Module implementation
            ├── stock-management.css # Module styles
            ├── tabulator-init.js  # Tabulator initialization
            └── routes/
                └── stock_routes.py # Backend API routes
```

---

## 🔄 Loading Sequence (Step-by-Step)

### **Phase 1: DOM Ready Event**
```
Browser → DOMContentLoaded event fires
          ↓
     UI/js/module-loader.js (lines 169-191)
          ↓
     Event listener: document.addEventListener('DOMContentLoaded', ...)
          ↓
     Check: Is window.ModuleManager available?
          ↓
     Call: window.ModuleManager.initialize()
          ↓
     Create: window.ModuleLoader = new ModuleLoader()
          ↓
     Call: window.ModuleLoader.loadModules()
```

### **Phase 2: Load Main Manifest**
```
ModuleLoader.loadModules() (lines 22-57)
          ↓
     Check: Is window.location.protocol === 'file:'?
          ↓ (NO - running from HTTP server)
     Fetch: external/modules/manifest.json
          ↓
     Parse: JSON response
          ↓
     Store: this.modules = manifest.modules
          ↓
     Loop: For each module in manifest.modules
          ↓
     Check: Is moduleConfig.enabled !== false?
          ↓ (YES for stock-management)
     Call: this.loadModule(moduleConfig)
```

### **Phase 3: Load Individual Module**
```
ModuleLoader.loadModule(moduleConfig) (lines 62-109)
          ↓
     Check: Does moduleConfig.manifestPath exist?
          ↓ (YES: "external/modules/stock-management/manifest.json")
     Fetch: moduleConfig.manifestPath
          ↓
     Parse: Module-specific manifest JSON
          ↓
     Merge: fullManifest = { ...moduleManifest, ...moduleConfig }
          ↓
     Check: Is window.ModuleManager available?
          ↓ (YES)
     Call: window.ModuleManager.registerModule(fullManifest)
```

### **Phase 4: Register Module**
```
ModuleManager.registerModule(moduleConfig) (lines 42-74)
          ↓
     Validate: this.validateModule(moduleConfig)
          ↓ (Check: id, name, icon, scriptPath exist)
     Check: Is module already registered?
          ↓ (NO)
     Store: this.modules.set(moduleConfig.id, {...})
          ↓
     Call: this.addSidebarIcon(moduleConfig)
          ↓
     Call: this.createTabContainer(moduleConfig)
          ↓
     Call: this.loadModuleDependencies(moduleConfig) ✅ NEW!
          ↓
     Call: this.loadModuleScript(moduleConfig)
```

### **Phase 4.5: Load Module Dependencies** ✅ NEW!
```
ModuleManager.loadModuleDependencies(config) (lines ~156-185)
          ↓
     Check: Does config.dependencies exist?
          ↓ (YES - 8 dependencies)
     Loop: For each dependency
          ↓
     Check: Is dependency already loaded? (DOM selector)
          ↓ (NO for first load)
     Detect: CSS or JS file? (by extension)
          ↓
     Load: Call loadCSS() or loadJS()
          ↓
     Create: <link> or <script> element
          ↓
     Append: To document.head
          ↓
     Wait: Promise.all() for all dependencies
          ↓
     Console: "✅ All dependencies loaded"
          ↓
     Dependencies loaded in parallel:
          - tabulator-functions.js ✅
          - tabulator-theme-adapter.js ✅
          - tabulator-enhancements.js ✅
          - tabulator-enhancements.css ✅
          - tabulator-init.js ✅
```

### **Phase 5: Load Module Script**
```
ModuleManager.loadModuleScript(config) (lines ~220-255)
          ↓
     (Dependencies already loaded from Phase 4.5)
          ↓
     Create: <script> element
          ↓
     Build URL: config.scriptPath + cacheBuster
          ↓ (e.g., "external/modules/stock-management/stock-management.js?v=4.0.0&t=1699468800&r=abc123")
     Set: script.type = 'module'
          ↓
     Append: document.head.appendChild(script)
          ↓
     Event: script.onload fires
          ↓
     Call: this.initializeModule(config.id, lazy=true)
          ↓
     Set: module.lazyLoadReady = true
          ↓ (Module ready but NOT initialized yet - waits for tab click)
     Console: "📦 Module ready for lazy loading"
```

### **Phase 6: User Clicks Tab (Lazy Load)**
```
User clicks Stock Management icon in sidebar
          ↓
     Event: button.addEventListener('click', ...)
          ↓
     Call: ModuleManager.switchToModule('stock-management')
          ↓
     Check: Is module.loaded?
          ↓ (NO - first time)
     Check: Is module.lazyLoadReady?
          ↓ (YES)
     Call: this.initializeModule('stock-management', lazy=false)
```

### **Phase 7: Initialize Module Instance**
```
ModuleManager.initializeModule(moduleId, lazy=false) (lines 190-251)
          ↓
     Check: window.ModuleRegistry['stock-management'] exists?
          ↓ (YES - module registered itself)
     Get: ModuleClass = window.ModuleRegistry['stock-management']
          ↓
     Create: module.instance = new ModuleClass('stock-management')
          ↓
     Call: module.instance.initialize()
          ↓ (Calls BaseModule.initialize() first)
     Set: module.loaded = true
          ↓
     Store: window.ModuleRegistry['stock-management'] = module.instance
          ↓
     Create: window.stockModule = module.instance
          ↓
     Console: "✅ Module initialized: Stock Management"
```

### **Phase 8: BaseModule.initialize()**
```
BaseModule.initialize() (lines 23-42)
          ↓
     Get: this.container = document.getElementById('tab-stock-management')
          ↓
     Call: await this.loadManifest()
          ↓
     Call: this.createModuleStructure()
          ↓
     Return to child class (StockManagementModule.initialize())
```

### **Phase 9: StockManagementModule.initialize()**
```
StockManagementModule.initialize() (lines ~3200-3300 in stock-management.js)
          ↓
     Call: await super.initialize()
          ↓ (BaseModule.initialize() completes)
     Set: this.backendUrl = 'http://localhost:5001'
          ↓
     Create: Sub-tab handlers for each tab
          ↓
     Call: this.initializeSubTabs()
          ↓
     Load: Default sub-tab ('invoice-processing')
          ↓
     Module ready for user interaction
```

---

## 📄 Key Files Analyzed

### **1. external/modules/manifest.json**
```json
{
  "modules": [
    {
      "id": "stock-management",
      "name": "Stock Management",
      "icon": "fas fa-boxes",
      "color": "#0078d4",
      "description": "Comprehensive stock management system...",
      "manifestPath": "external/modules/stock-management/manifest.json",
      "scriptPath": "external/modules/stock-management/stock-management.js",
      "enabled": true
    },
    // ... other modules
  ],
  "version": "1.0.6",
  "lastUpdated": "2025-11-06"
}
```

**Purpose:** Lists all available modules for the system  
**Used by:** `ModuleLoader.loadModules()` (line 35)  
**Location:** `UI/external/modules/manifest.json`

---

### **2. external/modules/stock-management/manifest.json**
```json
{
  "id": "stock-management",
  "name": "Stock Management",
  "version": "4.0.0",
  "description": "Complete stock inventory management...",
  "icon": "fas fa-boxes",
  "scriptPath": "external/modules/stock-management/stock-management.js",
  "stylePath": "external/modules/stock-management/stock-management.css",
  "dependencies": [
    "https://cdn.plot.ly/plotly-2.27.0.min.js",
    "https://unpkg.com/tabulator-tables@5.5.2/dist/css/tabulator.min.css",
    "https://unpkg.com/tabulator-tables@5.5.2/dist/js/tabulator.min.js",
    "UI/js/tabulator-functions.js",
    "UI/js/tabulator-theme-adapter.js",
    "UI/js/tabulator-enhancements.js",
    "UI/css/tabulator-enhancements.css",
    "external/modules/stock-management/tabulator-init.js"
  ],
  "colors": {
    "primary": "#0078d4",
    "secondary": "#00b294",
    "hover": "#006cbe"
  },
  "settings": {
    "api_endpoint": "/api/stock-management",
    "backend_url": "http://localhost:5001"
  },
  "tabs": [
    {
      "id": "invoice-processing",
      "name": "Invoice Processing",
      "icon": "fas fa-file-invoice",
      "description": "AI-powered invoice extraction...",
      "default": true
    },
    {
      "id": "usage-analytics",
      "name": "Usage Analytics",
      "icon": "fas fa-chart-line",
      "description": "Stock consumption trends..."
    },
    // ... 4 more tabs
  ]
}
```

**Purpose:** Module-specific configuration  
**Used by:** `ModuleLoader.loadModule()` (line 72-81)  
**Location:** `UI/external/modules/stock-management/manifest.json`

---

### **3. UI/js/module-loader.js (191 lines)**

**Class:** `ModuleLoader`

**Key Methods:**

#### `constructor()` (lines 9-17)
```javascript
constructor() {
    this.manifestPath = 'external/modules/manifest.json';
    this.modules = [];
    this.loadedCount = 0;
    this.failedCount = 0;
}
```
- **Purpose:** Initialize loader with manifest path
- **Called by:** DOMContentLoaded event (line 177)

#### `loadModules()` (lines 22-57)
```javascript
async loadModules() {
    // Check file:// protocol
    if (window.location.protocol === 'file:') {
        console.log('⚠️ Running from file:// protocol - module loading disabled');
        return;
    }

    // Fetch main manifest
    const response = await fetch(this.manifestPath);
    const manifest = await response.json();
    this.modules = manifest.modules || [];

    // Load each enabled module
    for (const moduleConfig of this.modules) {
        if (moduleConfig.enabled !== false) {
            await this.loadModule(moduleConfig);
        }
    }
}
```
- **Purpose:** Fetch main manifest, load all enabled modules
- **Called by:** DOMContentLoaded event (line 179)
- **Calls:** `this.loadModule()` for each enabled module

#### `loadModule(moduleConfig)` (lines 62-109)
```javascript
async loadModule(moduleConfig) {
    // Fetch module-specific manifest if path provided
    let fullManifest = moduleConfig;
    
    if (moduleConfig.manifestPath) {
        const manifestResponse = await fetch(moduleConfig.manifestPath);
        const moduleManifest = await manifestResponse.json();
        fullManifest = { ...moduleManifest, ...moduleConfig };
    }

    // Register with ModuleManager
    if (window.ModuleManager) {
        window.ModuleManager.registerModule(fullManifest);
        this.loadedCount++;
    }
}
```
- **Purpose:** Load individual module's manifest and register it
- **Called by:** `loadModules()` (line 51)
- **Calls:** `ModuleManager.registerModule()`

---

### **4. UI/js/module-manager.js (404 lines)**

**Class:** `ModuleManager`

**Key Methods:**

#### `constructor()` (lines 9-16)
```javascript
constructor() {
    this.modules = new Map();
    this.activeModule = null;
    this.sidebar = null;
    this.mainContent = null;
}
```
- **Purpose:** Initialize manager with empty module map
- **Called by:** Global script execution (line 399)

#### `initialize()` (lines 21-34)
```javascript
initialize() {
    this.sidebar = document.querySelector('.sidebar');
    this.mainContent = document.querySelector('.main-content');
    
    if (!this.sidebar || !this.mainContent) {
        console.error('❌ Required DOM elements not found');
        return false;
    }
    
    return true;
}
```
- **Purpose:** Get references to DOM elements
- **Called by:** DOMContentLoaded event (line 171 in module-loader.js)

#### `registerModule(moduleConfig)` (lines 42-74)
```javascript
registerModule(moduleConfig) {
    // Validate config
    if (!this.validateModule(moduleConfig)) {
        throw new Error(`Invalid module config for ${moduleConfig.id}`);
    }

    // Store module
    this.modules.set(moduleConfig.id, {
        ...moduleConfig,
        loaded: false,
        instance: null
    });

    // Add to sidebar
    this.addSidebarIcon(moduleConfig);

    // Create tab container
    this.createTabContainer(moduleConfig);

    // Load module script
    this.loadModuleScript(moduleConfig);
}
```
- **Purpose:** Register module in system
- **Called by:** `ModuleLoader.loadModule()` (line 99)
- **Calls:** 
  - `validateModule()`
  - `addSidebarIcon()`
  - `createTabContainer()`
  - `loadModuleScript()`

#### `addSidebarIcon(config)` (lines 91-125)
```javascript
addSidebarIcon(config) {
    // Create button
    const button = document.createElement('button');
    button.className = 'sidebar-icon-btn';
    button.setAttribute('data-tab', config.id);
    
    // Add icon
    const icon = document.createElement('i');
    icon.className = config.icon;
    icon.style.color = config.color;
    button.appendChild(icon);
    
    // Add click handler
    button.addEventListener('click', () => {
        this.switchToModule(config.id);
    });
    
    // Add to sidebar
    this.sidebar.appendChild(button);
}
```
- **Purpose:** Add clickable icon to sidebar
- **Called by:** `registerModule()` (line 62)

#### `createTabContainer(config)` (lines 130-150)
```javascript
createTabContainer(config) {
    const tabContent = document.createElement('div');
    tabContent.className = 'tab-content';
    tabContent.id = `tab-${config.id}`;
    
    // Add loading state
    tabContent.innerHTML = `
        <div class="module-loading">
            <i class="${config.icon}"></i>
            <h3>Loading ${config.name}...</h3>
            <div class="loading-spinner"></div>
        </div>
    `;
    
    // Append to main content
    this.mainContent.appendChild(tabContent);
}
```
- **Purpose:** Create container for module content
- **Called by:** `registerModule()` (line 67)

#### `loadModuleScript(config)` (lines 156-188)
```javascript
async loadModuleScript(config) {
    const script = document.createElement('script');
    
    // Add cache-busting
    const version = config.version || '1.0.0';
    const random = Math.random().toString(36).substring(7);
    const cacheBuster = `?v=${version}&t=${Date.now()}&r=${random}`;
    script.src = config.scriptPath + cacheBuster;
    script.type = 'module';
    
    script.onload = () => {
        // Lazy load: Don't initialize yet
        this.initializeModule(config.id, true);
    };
    
    document.head.appendChild(script);
}
```
- **Purpose:** Dynamically load module's JavaScript file
- **Called by:** `registerModule()` (line 71)
- **Calls:** `initializeModule()` when script loads

#### `initializeModule(moduleId, lazy=false)` (lines 190-251)
```javascript
async initializeModule(moduleId, lazy = false) {
    const module = this.modules.get(moduleId);
    
    // LAZY LOADING: If lazy=true, mark ready but don't initialize
    if (lazy) {
        module.lazyLoadReady = true;
        console.log(`📦 Module ready for lazy loading`);
        return;
    }
    
    // Get module class from registry
    if (window.ModuleRegistry && window.ModuleRegistry[moduleId]) {
        const ModuleClass = window.ModuleRegistry[moduleId];
        
        // Create instance
        module.instance = new ModuleClass(moduleId);
        
        // Initialize
        await module.instance.initialize();
        module.loaded = true;
        
        // Store globally
        window.ModuleRegistry[moduleId] = module.instance;
        window.stockModule = module.instance; // Shorthand
        
        console.log(`✅ Module initialized: ${module.name}`);
    }
}
```
- **Purpose:** Create and initialize module instance
- **Called by:** 
  - `loadModuleScript()` with lazy=true (line 177)
  - `lazyInitModule()` with lazy=false (line 274)
- **Calls:** `module.instance.initialize()`

#### `switchToModule(moduleId)` (lines 280-320)
```javascript
switchToModule(moduleId) {
    const module = this.modules.get(moduleId);
    
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show module tab
    const tabContent = document.getElementById(`tab-${moduleId}`);
    tabContent.classList.add('active');
    
    // Activate sidebar button
    const button = this.sidebar.querySelector(`[data-tab="${moduleId}"]`);
    button.classList.add('active');
    
    // Notify module it's active
    if (module.loaded && module.instance && module.instance.onActivate) {
        module.instance.onActivate();
    }
    
    this.activeModule = moduleId;
}
```
- **Purpose:** Switch to module tab
- **Called by:** Sidebar icon click event (line 118)

---

### **5. UI/js/module-base.js (357 lines)**

**Class:** `BaseModule`

**Key Methods:**

#### `constructor(moduleId, modulePath)` (lines 8-18)
```javascript
constructor(moduleId, modulePath = null) {
    this.moduleId = moduleId;
    this.modulePath = modulePath || moduleId;
    this.container = null;
    this.subTabs = new Map();
    this.activeSubTab = null;
    this.manifest = null;
}
```
- **Purpose:** Initialize base module properties
- **Called by:** Child class constructor (e.g., `StockManagementModule`)

#### `initialize()` (lines 23-42)
```javascript
async initialize() {
    // Get container
    this.container = document.getElementById(`tab-${this.moduleId}`);
    
    // Load manifest
    await this.loadManifest();
    
    // Create UI structure
    this.createModuleStructure();
    
    console.log(`✅ ${this.moduleId} initialized`);
}
```
- **Purpose:** Base initialization for all modules
- **Called by:** `ModuleManager.initializeModule()` (line 213)
- **Calls:**
  - `loadManifest()`
  - `createModuleStructure()`

#### `loadManifest()` (lines 47-69)
```javascript
async loadManifest() {
    const manifestUrl = `external/modules/${this.modulePath}/manifest.json`;
    const response = await fetch(manifestUrl);
    this.manifest = await response.json();
}
```
- **Purpose:** Load module-specific manifest
- **Called by:** `initialize()` (line 31)

#### `createModuleStructure()` (lines 74-150)
```javascript
createModuleStructure() {
    // Clear loading state
    this.container.innerHTML = '';
    
    // Create header
    const header = document.createElement('div');
    header.className = 'module-header';
    header.innerHTML = `
        <h2>${this.manifest.name}</h2>
        <button data-action="refresh">Refresh</button>
        <button data-action="settings">Settings</button>
    `;
    this.container.appendChild(header);
    
    // Create sub-tabs nav
    const subTabsNav = document.createElement('div');
    subTabsNav.className = 'module-subtabs-nav';
    
    this.manifest.tabs.forEach((tab, index) => {
        const button = document.createElement('button');
        button.className = 'module-subtab-btn';
        button.setAttribute('data-subtab', tab.id);
        button.innerHTML = `<i class="${tab.icon}"></i> ${tab.name}`;
        button.addEventListener('click', () => this.switchSubTab(tab.id));
        subTabsNav.appendChild(button);
    });
    
    this.container.appendChild(subTabsNav);
    
    // Create sub-tabs content container
    const subTabsContent = document.createElement('div');
    subTabsContent.className = 'module-subtabs-content';
    this.container.appendChild(subTabsContent);
}
```
- **Purpose:** Create module UI structure (header, sub-tabs, content area)
- **Called by:** `initialize()` (line 34)

#### `switchSubTab(subTabId)` (lines 195-230)
```javascript
async switchSubTab(subTabId) {
    // Update active button
    this.container.querySelectorAll('.module-subtab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const button = this.container.querySelector(`[data-subtab="${subTabId}"]`);
    button.classList.add('active');
    
    // Hide all sub-tab contents
    this.container.querySelectorAll('.subtab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // Show selected sub-tab
    const content = this.container.querySelector(`#${this.moduleId}-${subTabId}`);
    content.style.display = 'block';
    
    // Lazy initialize if needed
    const subTab = this.subTabs.get(subTabId);
    if (subTab && !subTab.initialized) {
        await this.initializeSubTab(subTabId);
        subTab.initialized = true;
    }
    
    this.activeSubTab = subTabId;
}
```
- **Purpose:** Switch between sub-tabs within module
- **Called by:** Sub-tab button click event

---

### **6. external/modules/stock-management/stock-management.js (3,418 lines)**

**Class:** `StockManagementModule extends BaseModule`

**Key Sections:**

#### Helper Classes (lines 1-400)
```javascript
class PlotlyChartHelper { ... }      // Chart rendering
class SQLViewerHelper { ... }        // SQL interface
class CellEditingHelper { ... }      // Inline editing
```

#### Main Class: StockManagementModule (lines ~3200-3418)
```javascript
class StockManagementModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);
        this.backendUrl = 'http://localhost:5001';
        this.tabulators = {};
        this.sqlViewer = null;
        this.cellEditor = null;
    }
    
    async initialize() {
        // Call parent initialization
        await super.initialize();
        
        // Module-specific setup
        this.setupSubTabs();
        
        // Initialize helpers
        this.sqlViewer = new SQLViewerHelper(this);
        this.cellEditor = new CellEditingHelper(this);
        
        // Load default tab
        await this.initializeSubTabs();
    }
    
    setupSubTabs() {
        // Register sub-tab handlers
        this.registerSubTab('invoice-processing', () => this.loadInvoiceProcessing());
        this.registerSubTab('usage-analytics', () => this.loadUsageAnalytics());
        this.registerSubTab('reorder-dashboard', () => this.loadReorderDashboard());
        this.registerSubTab('profit-analysis', () => this.loadProfitAnalysis());
        this.registerSubTab('sql-viewer', () => this.loadSQLViewer());
        this.registerSubTab('ai-analytics', () => this.loadAIAnalytics());
    }
    
    // Tab-specific loading methods
    async loadInvoiceProcessing() { ... }
    async loadUsageAnalytics() { ... }
    async loadReorderDashboard() { ... }
    async loadProfitAnalysis() { ... }
    async loadSQLViewer() { ... }
    async loadAIAnalytics() { ... }
    
    // Tabulator initialization
    async initializeTabulator(containerId, endpoint, options) { ... }
    
    // API methods
    async fetchData(endpoint) { ... }
    async postData(endpoint, data) { ... }
}

// Register in global registry
window.ModuleRegistry = window.ModuleRegistry || {};
window.ModuleRegistry['stock-management'] = StockManagementModule;
```

**Self-Registration** (last 3 lines):
```javascript
window.ModuleRegistry = window.ModuleRegistry || {};
window.ModuleRegistry['stock-management'] = StockManagementModule;
console.log('✅ Stock Management module registered');
```
- **Purpose:** Make module class available to `ModuleManager`
- **When:** Immediately when script loads
- **Used by:** `ModuleManager.initializeModule()` (line 205)

---

## 🔗 Function Call Flow

### Complete Call Chain (From Browser Load to Module Ready)

```
1. Browser loads HTML page
   └─> DOMContentLoaded event fires
       └─> module-loader.js event listener (line 169)
           └─> ModuleManager.initialize() ✅
               └─> Get .sidebar and .main-content DOM elements
           └─> new ModuleLoader() ✅
               └─> Set manifestPath = 'external/modules/manifest.json'
           └─> ModuleLoader.loadModules() ✅
               └─> fetch('external/modules/manifest.json') ✅
                   └─> Parse JSON
                   └─> Loop each module where enabled=true
                       └─> ModuleLoader.loadModule(config) ✅
                           └─> fetch('external/modules/stock-management/manifest.json') ✅
                               └─> Parse module manifest
                               └─> Merge with main manifest config
                           └─> ModuleManager.registerModule(fullManifest) ✅
                               ├─> validateModule() ✅
                               ├─> modules.set(id, config) ✅
                               ├─> addSidebarIcon(config) ✅
                               │   └─> Create <button> with icon
                               │   └─> Add click event → switchToModule()
                               │   └─> Append to sidebar
                               ├─> createTabContainer(config) ✅
                               │   └─> Create <div id="tab-stock-management">
                               │   └─> Add loading spinner HTML
                               │   └─> Append to main content
                               └─> loadModuleScript(config) ✅
                                   └─> Create <script> element
                                   └─> Set src with cache-busting
                                   └─> script.onload event
                                       └─> initializeModule(id, lazy=true) ✅
                                           └─> Set module.lazyLoadReady = true
                                           └─> DON'T initialize yet ⏸️

2. User clicks Stock Management icon in sidebar
   └─> Click event fires on sidebar button
       └─> ModuleManager.switchToModule('stock-management') ✅
           ├─> Hide all .tab-content divs
           ├─> Show #tab-stock-management div
           ├─> Activate sidebar button
           └─> Check: Is module.loaded?
               └─> NO (first time)
               └─> Check: Is module.lazyLoadReady?
                   └─> YES
                   └─> lazyInitModule('stock-management') ✅
                       └─> initializeModule('stock-management', lazy=false) ✅
                           ├─> Get ModuleClass from window.ModuleRegistry ✅
                           ├─> Create instance = new StockManagementModule() ✅
                           │   └─> Calls super() → BaseModule.constructor()
                           │       ├─> Set moduleId = 'stock-management'
                           │       ├─> Set modulePath = 'stock-management'
                           │       ├─> Initialize containers
                           ├─> Call instance.initialize() ✅
                           │   └─> BaseModule.initialize() ✅
                           │       ├─> Get container = #tab-stock-management
                           │       ├─> loadManifest() ✅
                           │       │   └─> fetch('external/modules/stock-management/manifest.json')
                           │       │   └─> Store in this.manifest
                           │       └─> createModuleStructure() ✅
                           │           ├─> Clear container.innerHTML
                           │           ├─> Create module header with title & buttons
                           │           ├─> Create sub-tabs nav with 6 buttons
                           │           └─> Create sub-tabs content container
                           │   └─> StockManagementModule.initialize() ✅
                           │       ├─> Set backendUrl
                           │       ├─> setupSubTabs() ✅
                           │       │   └─> Register 6 sub-tab handlers
                           │       ├─> Create helpers (sqlViewer, cellEditor)
                           │       └─> initializeSubTabs() ✅
                           │           └─> Load default tab (invoice-processing)
                           │               └─> loadInvoiceProcessing() ✅
                           │                   └─> Create UI for invoice processing
                           │                   └─> Initialize Tabulator if needed
                           ├─> Set module.loaded = true ✅
                           ├─> Store globally:
                           │   ├─> window.ModuleRegistry['stock-management'] = instance
                           │   └─> window.stockModule = instance
                           └─> Console: "✅ Module initialized: Stock Management"

3. Module ready for user interaction 🎉
   └─> User can click sub-tabs
       └─> BaseModule.switchSubTab(subTabId) ✅
           ├─> Update active button styling
           ├─> Hide all sub-tab contents
           ├─> Show selected sub-tab content
           └─> Lazy initialize sub-tab if needed
               └─> StockManagementModule.loadXxxTab() ✅
                   └─> Create tab-specific UI
                   └─> Fetch data from backend
                   └─> Initialize Tabulator tables
                   └─> Render charts with Plotly
```

---

## 🎯 Manifest Structure

### Main Manifest (external/modules/manifest.json)
```json
{
  "modules": [
    {
      "id": "stock-management",           // ✅ Required - Unique identifier
      "name": "Stock Management",         // ✅ Required - Display name
      "icon": "fas fa-boxes",            // ✅ Required - FontAwesome icon
      "color": "#0078d4",                // ⚠️  Optional - Icon color
      "description": "...",              // ⚠️  Optional - Description
      "manifestPath": "...",             // ⚠️  Optional - Path to module manifest
      "scriptPath": "...",               // ✅ Required - Path to module JS
      "enabled": true                    // ⚠️  Optional - Default true
    }
  ],
  "version": "1.0.6",
  "lastUpdated": "2025-11-06"
}
```

### Module Manifest (external/modules/stock-management/manifest.json)
```json
{
  "id": "stock-management",              // ✅ Required - Must match main manifest
  "name": "Stock Management",            // ✅ Required
  "version": "4.0.0",                    // ⚠️  Optional - Used for cache-busting
  "description": "...",                  // ⚠️  Optional
  "icon": "fas fa-boxes",               // ✅ Required
  "scriptPath": "...",                   // ✅ Required
  "stylePath": "...",                    // ⚠️  Optional - CSS file path
  "dependencies": [                      // ⚠️  Optional - External libraries
    "https://cdn.plot.ly/plotly-2.27.0.min.js",
    "UI/js/tabulator-functions.js"
  ],
  "colors": {                           // ⚠️  Optional - Theme colors
    "primary": "#0078d4",
    "secondary": "#00b294"
  },
  "settings": {                         // ⚠️  Optional - Module settings
    "api_endpoint": "/api/stock-management",
    "backend_url": "http://localhost:5001"
  },
  "tabs": [                            // ⚠️  Optional - Sub-tabs
    {
      "id": "invoice-processing",      // ✅ Required if tabs exist
      "name": "Invoice Processing",    // ✅ Required
      "icon": "fas fa-file-invoice",  // ✅ Required
      "description": "...",            // ⚠️  Optional
      "default": true                  // ⚠️  Optional - Default active tab
    }
  ]
}
```

---

## 🏗️ Class Hierarchy

```
BaseModule (UI/js/module-base.js)
    ├─ Properties:
    │   ├─ moduleId: string
    │   ├─ modulePath: string
    │   ├─ container: HTMLElement
    │   ├─ subTabs: Map
    │   ├─ activeSubTab: string
    │   └─ manifest: Object
    │
    ├─ Methods:
    │   ├─ initialize() - Base initialization
    │   ├─ loadManifest() - Load module manifest
    │   ├─ createModuleStructure() - Create UI
    │   ├─ registerSubTab() - Register sub-tab handler
    │   ├─ switchSubTab() - Switch to sub-tab
    │   ├─ initializeSubTab() - Initialize specific sub-tab
    │   ├─ onRefresh() - Handle refresh button
    │   ├─ onSettings() - Handle settings button
    │   └─ onActivate() - Called when module becomes active
    │
    └─ StockManagementModule (external/modules/stock-management/stock-management.js)
        ├─ Extends BaseModule
        │
        ├─ Additional Properties:
        │   ├─ backendUrl: string
        │   ├─ tabulators: Object (stores Tabulator instances)
        │   ├─ sqlViewer: SQLViewerHelper
        │   └─ cellEditor: CellEditingHelper
        │
        ├─ Overridden Methods:
        │   └─ initialize() - Calls super.initialize() + module setup
        │
        ├─ Module-Specific Methods:
        │   ├─ setupSubTabs() - Register 6 sub-tab handlers
        │   ├─ loadInvoiceProcessing() - Load invoice tab
        │   ├─ loadUsageAnalytics() - Load usage tab
        │   ├─ loadReorderDashboard() - Load reorder tab
        │   ├─ loadProfitAnalysis() - Load profit tab
        │   ├─ loadSQLViewer() - Load SQL tab
        │   ├─ loadAIAnalytics() - Load AI tab
        │   ├─ initializeTabulator() - Create Tabulator instance
        │   ├─ fetchData() - Fetch from backend API
        │   └─ postData() - POST to backend API
        │
        └─ Helper Classes:
            ├─ PlotlyChartHelper - Chart rendering
            ├─ SQLViewerHelper - SQL interface
            └─ CellEditingHelper - Inline editing
```

---

## ⚙️ Initialization Process

### Lazy Loading Strategy

The system uses **lazy loading** to improve initial page load performance:

**Phase 1: Script Loading (Immediate)**
```
- Module script is loaded immediately
- Module class is registered in window.ModuleRegistry
- Module is marked as "lazyLoadReady"
- NO instance created yet
- NO DOM initialization yet
```

**Phase 2: Instance Creation (On First Tab Click)**
```
- User clicks module icon
- Module instance is created
- BaseModule.initialize() runs
- Module-specific initialize() runs
- Default sub-tab is loaded
- Module is marked as "loaded"
```

**Phase 3: Sub-Tab Loading (On Sub-Tab Click)**
```
- User clicks sub-tab
- Check if sub-tab already initialized
- If not, call tab-specific load method
- Create UI for that tab only
- Fetch data for that tab only
- Initialize Tabulator for that tab only
```

### Benefits:
1. **Faster Initial Load** - Only load what's visible
2. **Memory Efficiency** - Don't create unnecessary instances
3. **Better Performance** - Spread out expensive operations
4. **Progressive Enhancement** - Module becomes functional gradually

---

## 📊 Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER LOADS HTML                       │
│                    DOMContentLoaded Event Fires                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     MODULE LOADER STARTS                         │
│  File: UI/js/module-loader.js                                   │
│  ├─ Initialize ModuleManager                                    │
│  ├─ Create ModuleLoader instance                                │
│  └─ Call loadModules()                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FETCH MAIN MANIFEST                            │
│  File: external/modules/manifest.json                           │
│  ├─ Get list of all modules                                     │
│  ├─ Filter enabled modules                                      │
│  └─ Loop each enabled module                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              FETCH MODULE-SPECIFIC MANIFEST                      │
│  File: external/modules/stock-management/manifest.json          │
│  ├─ Get module configuration                                    │
│  ├─ Get dependencies list                                       │
│  ├─ Get sub-tabs definition                                     │
│  └─ Merge with main manifest                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  REGISTER MODULE IN MANAGER                      │
│  File: UI/js/module-manager.js                                  │
│  ├─ Validate module config                                      │
│  ├─ Store in modules Map                                        │
│  ├─ Add sidebar icon                                            │
│  ├─ Create tab container                                        │
│  └─ Load module script                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LOAD MODULE JAVASCRIPT                          │
│  File: external/modules/stock-management/stock-management.js    │
│  ├─ Create <script> element                                     │
│  ├─ Add cache-busting query params                              │
│  ├─ Append to document.head                                     │
│  └─ Wait for script.onload                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│               MODULE SCRIPT SELF-REGISTERS                       │
│  window.ModuleRegistry['stock-management'] = StockManagementModule│
│  ├─ Module class available globally                             │
│  ├─ Set module.lazyLoadReady = true                            │
│  └─ Module ready but NOT initialized                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │  ⏸️ WAIT FOR USER INTERACTION
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│             USER CLICKS STOCK MANAGEMENT ICON                    │
│  └─ switchToModule('stock-management') called                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              CHECK IF MODULE ALREADY LOADED                      │
│  ├─ module.loaded === false (first time)                       │
│  ├─ module.lazyLoadReady === true                              │
│  └─ Call initializeModule(lazy=false)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 CREATE MODULE INSTANCE                           │
│  const instance = new StockManagementModule('stock-management') │
│  ├─ Calls super() → BaseModule.constructor()                   │
│  ├─ Set moduleId, modulePath, containers                       │
│  └─ Ready to initialize                                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              CALL instance.initialize()                          │
│  ├─ BaseModule.initialize() runs first                         │
│  │   ├─ Get container element                                   │
│  │   ├─ Load manifest                                          │
│  │   └─ Create module structure                                │
│  │       ├─ Header with title & buttons                        │
│  │       ├─ Sub-tabs navigation (6 tabs)                       │
│  │       └─ Sub-tabs content area                              │
│  │                                                              │
│  └─ StockManagementModule.initialize() runs                    │
│      ├─ Set backendUrl                                         │
│      ├─ Setup sub-tabs handlers                                │
│      ├─ Create helper instances                                │
│      └─ Load default sub-tab                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  STORE GLOBALLY & MARK LOADED                    │
│  ├─ window.ModuleRegistry['stock-management'] = instance        │
│  ├─ window.stockModule = instance                               │
│  ├─ module.loaded = true                                        │
│  └─ Console: "✅ Module initialized"                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MODULE READY FOR USE                          │
│  ├─ User can click sub-tabs                                     │
│  ├─ User can interact with tables                               │
│  ├─ User can execute SQL queries                                │
│  └─ User can upload invoices                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Key Files and Their Roles

| File | Role | Size | Key Functions |
|------|------|------|---------------|
| `external/modules/manifest.json` | Lists all modules | ~100 lines | Module registry |
| `external/modules/stock-management/manifest.json` | Module config | ~80 lines | Module settings |
| `UI/js/module-loader.js` | Loads modules | 191 lines | `loadModules()`, `loadModule()` |
| `UI/js/module-manager.js` | Manages lifecycle | 404 lines | `registerModule()`, `initializeModule()`, `switchToModule()` |
| `UI/js/module-base.js` | Base class | 357 lines | `initialize()`, `createModuleStructure()`, `switchSubTab()` |
| `external/modules/stock-management/stock-management.js` | Module implementation | 3,418 lines | 6 tab loaders, Tabulator init, API calls |

---

## 🎯 Summary

### Loading Phases:
1. **DOM Ready** → Module system starts
2. **Manifest Load** → Get list of modules
3. **Registration** → Add to sidebar, create containers
4. **Script Load** → Load module JavaScript
5. **Lazy Ready** → Mark module as ready (don't initialize)
6. **User Click** → Initialize on first tab view
7. **Instance Creation** → Create module instance
8. **Initialization** → Set up UI, load default tab
9. **Ready** → Module fully functional

### Key Concepts:
- **Plugin Architecture** - Modules are independent, self-contained
- **Lazy Loading** - Only initialize when user clicks tab
- **Manifest-Driven** - Configuration via JSON files
- **Inheritance** - All modules extend BaseModule
- **Self-Registration** - Modules register themselves in global registry
- **Sub-Tabs** - Each module can have multiple tabs
- **Helper Classes** - Utility classes for specific functionality

---

**End of Code Trace**  
**Last Updated:** November 8, 2025  
**Total Lines Analyzed:** 5,300+ lines across 6 files
