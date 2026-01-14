# Universal Sidebar Framework ↔️ Module System Integration

**Date:** November 28, 2025  
**Purpose:** Document how the Universal Sidebar Framework integrates with the Module System  
**Status:** ✅ Production Ready

---

## 🎯 Overview

The **Universal Sidebar Framework** and **Module System** work together seamlessly. When you add a sidebar to your module's `manifest.json`, it's automatically registered with the framework.

```
Module System (manifest.json)
        ↓
    ModuleLoader
        ↓
Universal Sidebar Framework
        ↓
    Unified UX
```

---

## 🏗️ Architecture

### Component Interaction

```
┌─────────────────────────────────────────────────────────┐
│          MODULE MANIFEST (manifest.json)                 │
│  {                                                       │
│    "sidebar": {                                          │
│      "enabled": true,                                    │
│      "position": "left",                                 │
│      "width": 480                                        │
│    },                                                    │
│    "floating_toggle": true                               │
│  }                                                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓ (Read by ModuleLoader at startup)
┌─────────────────────────────────────────────────────────┐
│         MODULE LOADER (module_loader.js)                 │
│                                                          │
│  generateFloatingToggles() {                            │
│    for each module with sidebar.enabled:                │
│      1. Create floating toggle button                   │
│      2. Call registerModuleSidebarWithFramework()       │
│  }                                                       │
│                                                          │
│  registerModuleSidebarWithFramework(moduleId, module) { │
│    SidebarManager.register({                            │
│      id: `${moduleId}-sidebar`,                         │
│      side: module.sidebar.position,                     │
│      width: module.sidebar.width,                       │
│      toggleButtonId: `${moduleId}-floating-toggle`,     │
│      onInit: () => { /* initialize controller */ }      │
│    });                                                   │
│  }                                                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓ (Automatic registration)
┌─────────────────────────────────────────────────────────┐
│    UNIVERSAL SIDEBAR FRAMEWORK (sidebar-manager.js)      │
│                                                          │
│  register(config) {                                      │
│    - Validates config                                   │
│    - Applies transform-based positioning                │
│    - Auto-calculates z-index                            │
│    - Sets up state persistence                          │
│    - Makes toggle draggable                             │
│  }                                                       │
│                                                          │
│  toggle(sidebarId) {                                     │
│    - Smooth slide-in/out animation                      │
│    - Calls onInit (first time only)                     │
│    - Saves state to localStorage                        │
│  }                                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Registration Flow

### Step-by-Step Process

```javascript
// 1. PAGE LOAD
document.addEventListener('DOMContentLoaded', () => {
    // Universal Sidebar Framework loads first
    window.SidebarManager = new UniversalSidebarManager();
    
    // Then Module Loader initializes
    window.moduleLoader = new ModuleLoader();
    await moduleLoader.initialize(userId);
});

// 2. MODULE LOADER INITIALIZATION
async initialize(userId) {
    // Fetch module manifests from backend
    const response = await fetch('/api/modules/list');
    const data = await response.json();
    
    // Store module manifests
    for (const module of data.modules) {
        this.modules.set(module.id, module);
    }
    
    // Check user credentials for each module
    await this.checkModuleAvailability();
    
    // Generate UI elements
    this.generateSidebarButtons();      // Left/main sidebar buttons
    this.generateFloatingToggles();     // Floating toggle buttons
    this.generateMainTabs();            // Main tab containers
}

// 3. FLOATING TOGGLE GENERATION
generateFloatingToggles() {
    for (const [moduleId, module] of this.modules) {
        if (!module.available || !module.floating_toggle) continue;
        
        // Create floating button
        const toggle = document.createElement('button');
        toggle.id = `${moduleId}-floating-toggle`;
        toggle.className = 'module-floating-toggle';
        // ... setup button ...
        
        // ⭐ AUTO-REGISTER WITH FRAMEWORK
        if (module.sidebar && module.sidebar.enabled) {
            this.registerModuleSidebarWithFramework(moduleId, module);
        }
    }
}

// 4. FRAMEWORK REGISTRATION
registerModuleSidebarWithFramework(moduleId, module) {
    const config = {
        id: `${moduleId}-sidebar`,
        side: module.sidebar.position || 'left',
        width: `${module.sidebar.width || 450}px`,
        toggleButtonId: `${moduleId}-floating-toggle`,
        icon: module.icon,
        title: module.name,
        onInit: async () => {
            // Initialize module controller
            const controllerName = `${moduleId.replace(/-/g, '')}Controller`;
            if (window[controllerName]?.init) {
                await window[controllerName].init();
            }
        }
    };
    
    window.SidebarManager.register(config);
}

// 5. USER INTERACTION
// User clicks floating toggle → Framework handles everything
User clicks "InHouse Kanban" toggle
    ↓
SidebarManager.toggle('inhouse-kanban-sidebar')
    ↓
- Loads module HTML/CSS/JS (if not loaded)
- Runs onInit callback (first time)
- Slides sidebar in with animation
- Saves state to localStorage
```

---

## 📝 Manifest Configuration

### Full Sidebar Configuration Options

```json
{
  "id": "my-module",
  "name": "My Module",
  "version": "1.0.0",
  "icon": "fas fa-cube",
  "color": "#6366f1",
  
  "floating_toggle": true,
  
  "sidebar": {
    "enabled": true,
    "position": "left",
    "side": "left",
    "width": 480,
    "html_file": "my-module-sidebar.html"
  },
  
  "main_tab": false
}
```

**Property Descriptions:**

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| `floating_toggle` | boolean | Show floating toggle button | false |
| `sidebar.enabled` | boolean | Enable sidebar for this module | false |
| `sidebar.position` | string | "left" or "right" | "left" |
| `sidebar.side` | string | Alias for position | "left" |
| `sidebar.width` | number | Sidebar width in pixels | 450 |
| `sidebar.html_file` | string | HTML template filename | N/A |

---

## 🎯 Real-World Examples

### Example 1: InHouse Kanban (Sidebar + Floating Toggle)

**manifest.json:**
```json
{
  "id": "inhouse-kanban",
  "name": "Production Workflow",
  "icon": "fas fa-industry",
  "color": "#00509E",
  "floating_toggle": true,
  "sidebar": {
    "enabled": true,
    "position": "left",
    "width": 480,
    "html_file": "inhouse-kanban-SIDEBAR.html"
  }
}
```

**What happens automatically:**
1. ✅ Floating toggle button created at left side
2. ✅ Sidebar registered with framework (id: `inhouse-kanban-sidebar`)
3. ✅ Click toggle → sidebar slides in from left
4. ✅ 480px width, left positioning
5. ✅ State persisted across sessions

### Example 2: Communication Hub (Main Tab, No Sidebar)

**manifest.json:**
```json
{
  "id": "communication-hub",
  "name": "Communication Hub",
  "icon": "fas fa-comments",
  "main_tab": true,
  "main_tab_id": "communication",
  "show_in_sidebar": true,
  "sidebar": {
    "enabled": false
  }
}
```

**What happens automatically:**
1. ✅ Button added to left main sidebar
2. ✅ Click button → switches to main tab (not sidebar)
3. ❌ No sidebar registration (enabled: false)
4. ❌ No floating toggle

### Example 3: Settings (Manual Registration)

**Not using Module System - registered in sidebar-init.js:**
```javascript
SidebarManager.register({
    id: 'settings-sidebar',
    side: 'right',
    toggleButtonId: 'settings-toggle',
    width: '450px',
    zIndex: 25000,  // Higher than other sidebars
    icon: 'fa-cog',
    title: 'Settings'
});
```

**Why manual:**
- Core platform component (not an external module)
- Needs custom z-index priority
- Toggle button in main left sidebar (not floating)

---

## 🔧 Module Controller Pattern

### Auto-Initialization

When your sidebar opens for the first time, the framework looks for a module controller:

**Naming Convention:**
```
Module ID: "inhouse-kanban"
Controller Name: "inhousekanbanController"
Method: init()
```

**Your module JS file:**
```javascript
// inhouse-kanban.js

class InhouseKanbanController {
    constructor() {
        this.initialized = false;
        this.jobs = [];
    }
    
    async init() {
        if (this.initialized) return;
        
        console.log('[InHouse Kanban] Initializing...');
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load initial data
        await this.loadJobs();
        
        // Mark as initialized
        this.initialized = true;
        
        console.log('[InHouse Kanban] ✅ Ready');
    }
    
    setupEventListeners() {
        // Listen for drag-and-drop, clicks, etc.
    }
    
    async loadJobs() {
        const response = await fetch('/api/inhouse-kanban/jobs');
        this.jobs = await response.json();
        this.renderJobs();
    }
    
    renderJobs() {
        // Render Kanban board
    }
}

// Create global instance
window.inhousekanbanController = new InhouseKanbanController();
```

**Framework calls init() automatically:**
```javascript
// Inside registerModuleSidebarWithFramework()
onInit: async () => {
    const controllerName = 'inhousekanbanController';
    if (window[controllerName]) {
        if (typeof window[controllerName].init === 'function') {
            await window[controllerName].init();
            window[controllerName].initialized = true;
        }
    }
}
```

---

## 🎨 Sidebar HTML Template

### Standard Structure

All module sidebars should follow this structure:

```html
<!-- my-module-sidebar.html -->
<div class="universal-sidebar collapsed" 
     id="my-module-sidebar" 
     data-side="left">
    
    <!-- HEADER -->
    <div class="universal-sidebar-header">
        <div class="universal-sidebar-title">
            <span>
                <i class="fas fa-cube"></i> My Module
            </span>
            <button class="universal-sidebar-close" 
                    onclick="SidebarManager.close('my-module-sidebar')">
                <i class="fas fa-times"></i>
            </button>
        </div>
    </div>

    <!-- CONTENT -->
    <div class="universal-sidebar-content" id="my-module-content">
        <!-- Your module content goes here -->
        <div class="module-widget">
            <h3>Widget Title</h3>
            <div id="widget-data">Loading...</div>
        </div>
    </div>
</div>
```

**Required elements:**
1. `.universal-sidebar` - Main container
2. `.collapsed` - Initial state (hidden)
3. `id="{module-id}-sidebar"` - Unique ID
4. `data-side="left|right"` - Positioning
5. `.universal-sidebar-header` - Header section
6. `.universal-sidebar-close` - Close button
7. `.universal-sidebar-content` - Content area

---

## 📊 Benefits of Integration

### Before Integration

**Manual sidebar implementation:**
```javascript
// ❌ Every module had custom code

// Create toggle button manually
const toggle = document.createElement('button');
toggle.onclick = () => {
    const sidebar = document.getElementById('my-sidebar');
    if (sidebar.classList.contains('active')) {
        sidebar.classList.remove('active');
        sidebar.style.transform = 'translateX(-100%)';
    } else {
        sidebar.classList.add('active');
        sidebar.style.transform = 'translateX(0)';
    }
};

// Manage z-index manually (conflicts!)
sidebar.style.zIndex = '10000';

// No state persistence
// No lazy loading
// No draggable toggle
```

### After Integration

**Automatic registration:**
```json
// ✅ Just add to manifest.json
{
  "sidebar": {
    "enabled": true,
    "position": "left",
    "width": 480
  },
  "floating_toggle": true
}
```

**Everything handled automatically:**
- ✅ Toggle button creation
- ✅ Sidebar registration
- ✅ Z-index management (no conflicts)
- ✅ State persistence
- ✅ Lazy loading
- ✅ Draggable toggle
- ✅ Smooth animations
- ✅ Controller initialization

---

## 🔍 Debugging

### Check If Sidebar Is Registered

```javascript
// Open browser console
console.log(SidebarManager.sidebars.has('inhouse-kanban-sidebar'));
// Should return: true

// Get sidebar config
console.log(SidebarManager.sidebars.get('inhouse-kanban-sidebar'));
// Shows: {id, side, width, toggleButtonId, onInit, ...}
```

### Check Module Manifest

```javascript
// Check if module loaded
console.log(moduleLoader.modules.get('inhouse-kanban'));
// Shows full manifest

// Check if sidebar config exists
const module = moduleLoader.modules.get('inhouse-kanban');
console.log(module.sidebar);
// Shows: {enabled: true, position: "left", width: 480}
```

### Verify Registration Call

Check console logs during page load:
```
[ModuleLoader] Generating floating toggle buttons...
[ModuleLoader] Created floating toggle for Production Workflow
[ModuleLoader] ✅ Registered inhouse-kanban with Universal Sidebar Framework
```

---

## 🚀 Adding a New Module with Sidebar

### Complete Example

**Step 1: Create module directory**
```
UI/external/modules/analytics/
├── manifest.json
├── analytics-sidebar.html
├── analytics.js
└── analytics.css
```

**Step 2: Configure manifest.json**
```json
{
  "id": "analytics",
  "name": "Analytics Dashboard",
  "version": "1.0.0",
  "icon": "fas fa-chart-line",
  "color": "#10b981",
  "floating_toggle": true,
  "sidebar": {
    "enabled": true,
    "position": "right",
    "width": 500,
    "html_file": "analytics-sidebar.html"
  },
  "js_file": "analytics.js",
  "css_file": "analytics.css"
}
```

**Step 3: Create sidebar HTML**
```html
<!-- analytics-sidebar.html -->
<div class="universal-sidebar collapsed" 
     id="analytics-sidebar" 
     data-side="right">
    <div class="universal-sidebar-header">
        <div class="universal-sidebar-title">
            <span><i class="fas fa-chart-line"></i> Analytics</span>
            <button class="universal-sidebar-close" 
                    onclick="SidebarManager.close('analytics-sidebar')">
                <i class="fas fa-times"></i>
            </button>
        </div>
    </div>
    <div class="universal-sidebar-content">
        <div id="analytics-charts">Loading...</div>
    </div>
</div>
```

**Step 4: Create controller (analytics.js)**
```javascript
class AnalyticsController {
    constructor() {
        this.initialized = false;
    }
    
    async init() {
        if (this.initialized) return;
        console.log('[Analytics] Initializing...');
        await this.loadData();
        this.initialized = true;
    }
    
    async loadData() {
        const response = await fetch('/api/analytics/data');
        const data = await response.json();
        this.renderCharts(data);
    }
}

window.analyticsController = new AnalyticsController();
```

**Step 5: Reload page**
- Module automatically discovered
- Floating toggle button created
- Sidebar registered with framework
- Click toggle → sidebar works!

**Total time:** 5-10 minutes  
**Manual registration:** NOT NEEDED ✅

---

## 📚 Related Documentation

- **[MODULE_SIDEBAR_INTEGRATION.md](MODULE_SIDEBAR_INTEGRATION.md)** - How to add sidebars
- **[sidebar-framework/SIDEBAR_FRAMEWORK_GUIDE.md](sidebar-framework/SIDEBAR_FRAMEWORK_GUIDE.md)** - Framework API
- **[sidebar-framework/README.md](sidebar-framework/README.md)** - Framework overview
- **[../external/modules/MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md](../external/modules/MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md)** - Module System docs

---

**Last Updated:** November 28, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
