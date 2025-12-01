# Module System Architecture V3.0
## Complete Specification for Robust, Flexible Module Framework

**Created:** November 29, 2025  
**Status:** Design Specification  
**Purpose:** Define a clear, robust module system that handles all use cases consistently

---

## 🎯 Design Principles

1. **Clarity Over Flexibility** - Clear rules, not special cases
2. **Self-Documenting** - Module type obvious from manifest
3. **Consistent Behavior** - Same rules for all modules
4. **Zero Ambiguity** - One way to do things
5. **Easy Migration** - Clear path to upgrade existing modules

---

## 📋 Module Types & Capabilities

### Type 1: **Internal Core Modules** (`modules_internal/`)
**Purpose:** Platform infrastructure, always available, no credentials needed

**Characteristics:**
- ✅ Always loaded at startup
- ✅ No credential requirements
- ✅ Appear ABOVE module separator in sidebar
- ✅ Cannot be disabled by users
- ✅ Part of core platform experience

**Examples:**
- Settings
- Thread Cards
- Prompt Library
- Automation Workflows
- Vector Database

---

### Type 2: **External Business Modules** (`modules_external/`)
**Purpose:** Business-specific features, optional, may require credentials

**Characteristics:**
- ⚠️ Loaded on-demand or at startup (configurable)
- ⚠️ May require platform credentials (Shopify, Salesforce, etc.)
- ✅ Appear BELOW module separator in sidebar
- ✅ Can be disabled by administrators
- ✅ Business/client-specific functionality

**Examples:**
- InHouse Kanban
- Communication Hub
- Shopify Integration
- Salesforce CRM

---

## 🏗️ Module Capabilities (What Modules Can Have)

### Capability 1: **Dashboard** (Main Content Area)
- Full-width content replacing main chat area
- Opened by clicking sidebar icon OR main tab button
- Uses `#main-content` container
- Can coexist with sidebar

**Use Cases:**
- Kanban boards (InHouse Kanban)
- Project dashboards (Synergy)
- Data tables (Communication Hub)
- Analytics views

---

### Capability 2: **Sidebar** (Side Panel)
- Left or right side panel
- Slides in/out over content
- Uses `SidebarManager` framework
- Can coexist with dashboard

**Use Cases:**
- Settings panels (Settings module)
- Document browsers (Vector DB)
- Debugging tools (Debug Console)
- Quick access panels

---

### Capability 3: **Both Dashboard + Sidebar**
- Module has BOTH capabilities
- Sidebar for quick access, Dashboard for full view
- User can switch between modes

**Use Cases:**
- InHouse Kanban (sidebar for quick view, dashboard for full board)
- Synergy (sidebar for session list, dashboard for project board)
- Communication Hub (sidebar for quick chat, dashboard for full interface)

---

### Capability 4: **Thread Card Integration**
- Module extends thread cards with badges/actions
- Uses drag-and-drop for linking
- Realtime updates on thread cards

**Use Cases:**
- Synergy (link threads to projects)
- InHouse Kanban (link threads to jobs)
- Any module that tracks work items

---

## 📄 Module Manifest Schema V3.0

### Complete Manifest Structure

```json
{
  "// ==================== CORE IDENTIFICATION ====================": "",
  "id": "string (required, unique, kebab-case)",
  "name": "string (required, display name)",
  "version": "string (required, semver: X.Y.Z)",
  "description": "string (required, 1-2 sentences)",
  "author": "string (optional, author/organization)",
  
  "// ==================== MODULE TYPE ====================": "",
  "type": "internal | external (required)",
  "category": "core | business | integration | tool (required)",
  
  "// ==================== VISUAL IDENTITY ====================": "",
  "icon": "string (required, Font Awesome class: fa-icon-name)",
  "color": "string (required, hex color: #RRGGBB)",
  
  "// ==================== CAPABILITIES ====================": "",
  "capabilities": {
    "dashboard": {
      "enabled": "boolean (required)",
      "container": "string (default: #main-content)",
      "replaces_chat": "boolean (default: true)",
      "html_file": "string (path to dashboard HTML)",
      "default_view": "boolean (show on startup?)"
    },
    "sidebar": {
      "enabled": "boolean (required)",
      "position": "left | right (required if enabled)",
      "default_width": "string (CSS width: 400px, 50%, etc.)",
      "html_file": "string (path to sidebar HTML)",
      "resizable": "boolean (default: true)",
      "collapsible": "boolean (default: true)"
    },
    "modal": {
      "enabled": "boolean (default: false)",
      "size": "small | medium | large | xlarge",
      "dismissible": "boolean (default: true)"
    },
    "embedded": {
      "enabled": "boolean (default: false)",
      "target_selectors": "array of CSS selectors",
      "inline": "boolean (renders inline vs float)"
    },
    "fullscreen": {
      "enabled": "boolean (default: false)",
      "escape_key": "boolean (ESC to exit, default: true)"
    },
    "thread_integration": {
      "enabled": "boolean (default: false)",
      "badge": "object (thread card badge config)",
      "drag_drop": "object (drag/drop handlers)",
      "realtime": "object (realtime event handlers)"
    },
    "main_tab": {
      "enabled": "boolean (default: false)",
      "tab_id": "string (HTML element ID for tab button)",
      "tab_label": "string (button text)",
      "icon": "string (Font Awesome icon)"
    }
  },
  
  "// ==================== LOADING STRATEGY ====================": "",
  "loading": {
    "strategy": "startup | lazy | on-demand (required)",
    "priority": "number (1-100, lower = earlier)",
    "dependencies": ["array of module IDs this depends on"],
    "timeout": "number (milliseconds before timeout)"
  },
  
  "// ==================== ASSETS ====================": "",
  "assets": {
    "scripts": [
      {
        "path": "string (relative to module folder)",
        "type": "module | classic (default: classic)",
        "defer": "boolean (default: false)",
        "async": "boolean (default: false)"
      }
    ],
    "styles": [
      {
        "path": "string (relative to module folder)",
        "media": "string (default: all)"
      }
    ],
    "html": {
      "dashboard": "string (path to dashboard HTML)",
      "sidebar": "string (path to sidebar HTML)"
    }
  },
  
  "// ==================== CREDENTIALS & PERMISSIONS ====================": "",
  "credentials": {
    "required": "boolean (default: false)",
    "platforms": ["array of platform names: shopify, salesforce, etc."],
    "oauth_scopes": ["array of required OAuth scopes"],
    "fallback_behavior": "disable | readonly | prompt (required if credentials.required)"
  },
  
  "permissions": [
    "array of permissions: api:*, storage:*, network:*"
  ],
  
  "// ==================== SIDEBAR APPEARANCE ====================": "",
  "sidebar_button": {
    "enabled": "boolean (show in sidebar?)",
    "position": "number (sort order, lower = higher)",
    "label": "string (button label)",
    "icon": "string (Font Awesome icon)",
    "color": "string (hex color)",
    "badge": {
      "enabled": "boolean (show badge?)",
      "source": "string (data source for badge count)",
      "color": "string (badge background color)"
    }
  },
  
  "// ==================== BEHAVIOR CONFIG ====================": "",
  "behavior": {
    "singleton": "boolean (only one instance?)",
    "persistent": "boolean (keep in memory?)",
    "auto_open": "boolean (open on startup?)",
    "hotkey": "string (keyboard shortcut: Ctrl+Shift+K)"
  },
  
  "// ==================== SETTINGS & CONFIG ====================": "",
  "settings": {
    "key": "value (module-specific configuration)"
  },
  
  "// ==================== METADATA ====================": "",
  "metadata": {
    "documentation_url": "string (link to docs)",
    "support_url": "string (support/help link)",
    "repository": "string (GitHub repo URL)",
    "license": "string (license: MIT, Apache-2.0, etc.)",
    "tags": ["array of tags for search/filter"]
  }
}
```

---

## 🔧 Minimal Module Examples

### Example 1: Sidebar-Only Module (Settings)

```json
{
  "id": "settings",
  "name": "Settings",
  "version": "1.0.0",
  "description": "Platform configuration and user preferences",
  "type": "internal",
  "category": "core",
  "icon": "fa-cog",
  "color": "#6B7280",
  
  "capabilities": {
    "dashboard": { "enabled": false },
    "sidebar": {
      "enabled": true,
      "position": "left",
      "default_width": "400px",
      "html_file": "settings-sidebar.html"
    }
  },
  
  "loading": {
    "strategy": "startup",
    "priority": 10
  },
  
  "assets": {
    "scripts": [
      { "path": "settings.js" }
    ],
    "styles": [
      { "path": "settings.css" }
    ]
  },
  
  "sidebar_button": {
    "enabled": true,
    "position": 1,
    "label": "Settings",
    "icon": "fa-cog"
  }
}
```

---

### Example 2: Dashboard + Sidebar Module (InHouse Kanban)

```json
{
  "id": "inhouse-kanban",
  "name": "Production Workflow",
  "version": "3.0.0",
  "description": "InHousePrint production workflow Kanban board",
  "type": "external",
  "category": "business",
  "icon": "fa-industry",
  "color": "#00509E",
  
  "capabilities": {
    "dashboard": {
      "enabled": true,
      "html_file": "kanban-dashboard.html",
      "replaces_chat": true,
      "default_view": false
    },
    "sidebar": {
      "enabled": true,
      "position": "left",
      "default_width": "480px",
      "html_file": "kanban-sidebar.html"
    },
    "thread_integration": {
      "enabled": true,
      "badge": {
        "icon": "fa-industry",
        "color": "#00509E"
      }
    },
    "main_tab": {
      "enabled": true,
      "tab_id": "kanban-tab",
      "tab_label": "Production",
      "icon": "fa-industry"
    }
  },
  
  "loading": {
    "strategy": "startup",
    "priority": 50
  },
  
  "credentials": {
    "required": true,
    "platforms": ["inhouse-print"],
    "fallback_behavior": "disable"
  },
  
  "assets": {
    "scripts": [
      { "path": "inhouse-kanban.js" },
      { "path": "kanban-supabase-integration.js" }
    ],
    "styles": [
      { "path": "inhouse-kanban.css" }
    ]
  },
  
  "sidebar_button": {
    "enabled": true,
    "position": 100,
    "label": "Production",
    "icon": "fa-industry",
    "badge": {
      "enabled": true,
      "source": "active_jobs_count"
    }
  }
}
```

---

### Example 3: Dashboard-Only Module (Communication Hub)

```json
{
  "id": "communication-hub",
  "name": "Communication Hub",
  "version": "2.0.0",
  "description": "Unified inbox for SMS, email, and chat messages",
  "type": "external",
  "category": "business",
  "icon": "fa-comments",
  "color": "#8B5CF6",
  
  "capabilities": {
    "dashboard": {
      "enabled": true,
      "html_file": "comms-hub-dashboard.html"
    },
    "sidebar": { "enabled": false }
  },
  
  "loading": {
    "strategy": "lazy",
    "priority": 70
  },
  
  "credentials": {
    "required": true,
    "platforms": ["twilio", "sendgrid"],
    "fallback_behavior": "readonly"
  },
  
  "assets": {
    "scripts": [
      { "path": "communication-hub.js" }
    ],
    "styles": [
      { "path": "communication-hub.css" }
    ]
  },
  
  "sidebar_button": {
    "enabled": true,
    "position": 110,
    "label": "Communications",
    "icon": "fa-comments"
  }
}
```

---

## 📊 Module Loading Flow

### Startup Sequence

```
1. Load module_loader.js (Core System)
   ↓
2. Fetch module list from /api/modules/list
   ↓
3. Separate modules by type:
   - internal_modules = modules where type="internal"
   - external_modules = modules where type="external"
   ↓
4. Sort each group by loading.priority (ascending)
   ↓
5. Load INTERNAL modules first:
   - Filter: loading.strategy = "startup"
   - Check credentials (if required)
   - Load assets (CSS, JS)
   - Initialize module
   - Add to sidebar (above separator)
   ↓
6. Add MODULE SEPARATOR to sidebar
   ↓
7. Load EXTERNAL modules:
   - Filter: loading.strategy = "startup"
   - Check credentials (if required)
   - Load assets (CSS, JS)
   - Initialize module
   - Add to sidebar (below separator)
   ↓
8. Register lazy-load modules (loading.strategy = "lazy")
   ↓
9. Fire 'modules:ready' event
```

---

## 🎨 Sidebar Visual Structure

```
┌─────────────────────────────┐
│  LEFT SIDEBAR               │
├─────────────────────────────┤
│  👤 User Profile            │ ← Always at top
├─────────────────────────────┤
│                             │
│  INTERNAL MODULES           │
│  (Core Platform)            │
│                             │
│  ⚙️  Settings               │
│  📋  Thread Cards           │
│  💬  Prompt Library         │
│  🤖  Automation Workflows   │
│  🗄️  Vector Database        │
│  🐛  Debug Console          │
│                             │
├─────────────────────────────┤ ← MODULE SEPARATOR
│  ─────────────────────────  │    (visual line/divider)
├─────────────────────────────┤
│                             │
│  EXTERNAL MODULES           │
│  (Business Features)        │
│                             │
│  🏭  Production Workflow    │ [5] ← badge
│  💬  Communication Hub      │
│  🛒  Shopify Integration    │
│  📊  Salesforce CRM         │
│  ☁️  Render Cloud           │
│                             │
└─────────────────────────────┘
```

---

## 🔄 Module Lifecycle States

```javascript
Module States:
- 'unloaded'    → Module discovered but not loaded
- 'loading'     → Assets being fetched
- 'loaded'      → Assets loaded, not initialized
- 'initializing'→ Running init functions
- 'ready'       → Fully functional
- 'error'       → Failed to load/init
- 'disabled'    → User/admin disabled
- 'unauthorized'→ Missing credentials

State Transitions:
unloaded → loading → loaded → initializing → ready
unloaded → disabled (admin action)
unloaded → unauthorized (no credentials)
loading → error (network/parse error)
initializing → error (init function failed)
ready → disabled (user action)
```

---

## 🛠️ Module Loader API

### Core Methods

```javascript
class ModuleLoader {
  // Initialization
  async initialize()
  
  // Module Management
  async loadModule(moduleId)
  async unloadModule(moduleId)
  async reloadModule(moduleId)
  async enableModule(moduleId)
  async disableModule(moduleId)
  
  // State Queries
  getModule(moduleId) → Module | null
  getModuleState(moduleId) → State | null
  getModulesByType(type) → Module[]
  getModulesByCategory(category) → Module[]
  getActiveModule() → Module | null
  
  // UI Actions
  openModuleDashboard(moduleId)
  openModuleSidebar(moduleId)
  closeModuleSidebar(moduleId)
  toggleModuleSidebar(moduleId)
  
  // Events
  on(event, callback)
  off(event, callback)
  emit(event, data)
}

// Events:
- 'module:loaded' → { moduleId, module }
- 'module:unloaded' → { moduleId }
- 'module:error' → { moduleId, error }
- 'module:state-changed' → { moduleId, oldState, newState }
- 'modules:ready' → { internal, external }
- 'dashboard:opened' → { moduleId }
- 'sidebar:opened' → { moduleId }
- 'sidebar:closed' → { moduleId }
```

---

## 📁 Directory Structure

```
UI/
├── modules_internal/           ← Internal core modules
│   ├── module_loader.js       ← Core loader (always loaded first)
│   ├── settings/
│   │   ├── manifest.json
│   │   ├── settings.js
│   │   ├── settings.css
│   │   └── settings-sidebar.html
│   ├── thread-cards/
│   │   ├── manifest.json
│   │   ├── thread-cards.js
│   │   └── thread-cards.css
│   └── prompt-library/
│       ├── manifest.json
│       ├── prompt-library.js
│       └── prompt-library.css
│
├── modules_external/           ← External business modules
│   ├── inhouse-kanban/
│   │   ├── manifest.json
│   │   ├── inhouse-kanban.js
│   │   ├── inhouse-kanban.css
│   │   ├── kanban-dashboard.html
│   │   └── kanban-sidebar.html
│   ├── communication-hub/
│   │   ├── manifest.json
│   │   ├── communication-hub.js
│   │   └── comms-hub-dashboard.html
│   └── shopify-integration/
│       ├── manifest.json
│       ├── shopify.js
│       └── shopify-dashboard.html
│
└── shared/                     ← Shared frameworks & utilities
    ├── sidebar-framework/
    ├── css/
    └── js/
```

---

## ✅ Migration Checklist (Existing Modules)

### Step 1: Add Required Fields to manifest.json
- [ ] Add `"type": "internal"` or `"external"`
- [ ] Add `"category"` field
- [ ] Add `"capabilities"` section
- [ ] Add `"loading"` section
- [ ] Add `"sidebar_button"` section

### Step 2: Restructure Assets
- [ ] Move all CSS to module folder
- [ ] Move all JS to module folder
- [ ] Move HTML files to module folder
- [ ] Update paths in manifest

### Step 3: Update Initialization Code
- [ ] Remove manual DOM creation (use HTML files)
- [ ] Use `SidebarManager` for sidebars
- [ ] Emit lifecycle events
- [ ] Handle state transitions

### Step 4: Test
- [ ] Module loads without errors
- [ ] Appears in correct sidebar section
- [ ] Dashboard opens correctly (if applicable)
- [ ] Sidebar works correctly (if applicable)
- [ ] No duplicate icons
- [ ] Credentials checked correctly (if required)

---

## 🎯 Next Steps

### Phase 1: Update Module Loader (Core System)
1. Add support for `type` field (internal vs external)
2. Implement module separator in sidebar
3. Add capability-based loading (dashboard vs sidebar)
4. Add state management system
5. Update sidebar button generation

### Phase 2: Create Module Migration Tool
1. Script to analyze existing modules
2. Generate updated manifest.json files
3. Validate against schema
4. Report missing fields

### Phase 3: Migrate Modules One-by-One
**Internal Modules:**
1. Settings
2. Thread Cards
3. Prompt Library
4. Automation Workflows
5. Vector Database
6. Debug Console
7. Synergy (has both dashboard + sidebar)

**External Modules:**
8. InHouse Kanban
9. Communication Hub
10. Shopify Integration
11. Salesforce CRM
12. [Others...]

### Phase 4: Documentation & Testing
1. Create module developer guide
2. Write migration guide
3. Test all modules
4. Update copilot-instructions.md

---

## 📚 Developer Guidelines

### Creating a New Module

1. **Choose module type:**
   - Internal = Core platform feature
   - External = Business-specific feature

2. **Choose capabilities:**
   - Dashboard only (main content)
   - Sidebar only (side panel)
   - Both dashboard + sidebar

3. **Create manifest.json** (use examples above)

4. **Create assets:**
   - JavaScript file(s)
   - CSS file(s)
   - HTML file(s) for UI

5. **Test in isolation:**
   - Load module manually
   - Verify all capabilities work
   - Check credentials (if required)

6. **Register with system:**
   - Place in correct folder (internal vs external)
   - Restart module loader
   - Verify appears in sidebar

---

## 🔧 Sidebar Implementation Guide

> **📖 Complete Reference:** See `UI/shared/sidebar-framework/SIDEBAR_FRAMEWORK_GUIDE.md` for full API documentation

### Quick Start: Adding a Sidebar to Your Module

#### Step 1: Update Manifest.json

```json
{
  "id": "my-module",
  "name": "My Module",
  "capabilities": {
    "sidebar": {
      "enabled": true,
      "position": "left",
      "default_width": "450px",
      "html_file": "sidebar.html",
      "resizable": true,
      "collapsible": true
    }
  },
  "sidebar_button": {
    "enabled": true,
    "position": 10,
    "label": "My Module",
    "icon": "fa-boxes",
    "color": "#3b82f6"
  }
}
```

#### Step 2: Load Sidebar Framework

```html
<!-- In your module's main HTML or initialization script -->
<link rel="stylesheet" href="../shared/sidebar-framework/sidebar-manager.css">
<script src="../shared/sidebar-framework/sidebar-manager.js"></script>
```

#### Step 3: Create Sidebar HTML

Create `my-module/sidebar.html`:

```html
<div id="my-module-sidebar" class="module-sidebar">
  <!-- Sidebar Header -->
  <div class="sidebar-header">
    <h3><i class="fas fa-boxes"></i> My Module</h3>
  </div>
  
  <!-- Sidebar Content -->
  <div class="sidebar-content">
    <div id="my-module-data-container">
      <!-- Data loaded here -->
    </div>
  </div>
  
  <!-- Sidebar Footer (optional) -->
  <div class="sidebar-footer">
    <button id="my-module-action-btn" class="btn btn-primary">
      <i class="fas fa-plus"></i> New Item
    </button>
  </div>
</div>
```

#### Step 4: Register with SidebarManager

```javascript
// In your module's main JavaScript file
class MyModule {
  constructor() {
    this.initialized = false;
  }
  
  init() {
    // Register sidebar with framework
    SidebarManager.register({
      id: 'my-module-sidebar',
      side: 'left',  // or 'right'
      toggleButtonId: 'my-module-toggle-btn',
      width: '450px',
      title: 'My Module',
      
      // Called when sidebar first opens (lazy loading)
      onInit: async () => {
        console.log('🔧 My Module sidebar initializing...');
        await this.loadSidebarData();
        this.initialized = true;
        console.log('✅ My Module sidebar ready');
      },
      
      // Called every time sidebar opens
      onOpen: () => {
        console.log('📂 My Module sidebar opened');
        if (this.initialized) {
          this.refreshData();
        }
      },
      
      // Called when sidebar closes
      onClose: () => {
        console.log('📁 My Module sidebar closed');
      }
    });
    
    console.log('✅ My Module sidebar registered');
  }
  
  async loadSidebarData() {
    // Fetch data from API
    const response = await fetch('/api/my-module/data');
    const data = await response.json();
    
    // Render data in sidebar
    const container = document.getElementById('my-module-data-container');
    container.innerHTML = this.renderData(data);
    
    // Attach event listeners
    this.attachEventListeners();
  }
  
  refreshData() {
    // Refresh data if sidebar already initialized
    if (this.initialized) {
      this.loadSidebarData();
    }
  }
  
  renderData(data) {
    return data.items.map(item => `
      <div class="sidebar-item">
        <h4>${item.title}</h4>
        <p>${item.description}</p>
      </div>
    `).join('');
  }
  
  attachEventListeners() {
    document.getElementById('my-module-action-btn')?.addEventListener('click', () => {
      this.handleNewItem();
    });
  }
  
  handleNewItem() {
    console.log('Creating new item...');
    // Your logic here
  }
}

// Initialize module
const myModule = new MyModule();
myModule.init();
```

#### Step 5: Create Toggle Button (if not auto-generated)

```html
<!-- Toggle button in main UI -->
<button id="my-module-toggle-btn" 
        class="sidebar-toggle-btn" 
        data-sidebar-id="my-module-sidebar"
        style="position: fixed; top: 100px; left: 10px;">
  <i class="fas fa-boxes"></i>
  <span>My Module</span>
</button>
```

### Sidebar Framework Features

**✅ Automatic Positioning**
- Sidebar automatically positions left or right based on toggle button location
- No manual coordinate calculations needed

**✅ Consistent Animations**
- Smooth slide-in/out with CSS transforms
- Hardware-accelerated for 60fps performance

**✅ Draggable Toggle Buttons**
- Users can reposition toggle buttons anywhere
- Position persists in localStorage

**✅ State Persistence**
- Remembers which sidebars are open across sessions
- Stores user preferences (width, position)

**✅ Lazy Loading**
- `onInit()` called only when sidebar first opens
- Improves initial page load performance

**✅ Z-Index Management**
- No conflicts between multiple open sidebars
- Automatic stacking order

**✅ Standard Styling**
- Consistent look and feel across all modules
- CSS variables for easy theming

### Advanced Sidebar Patterns

#### Pattern 1: Sidebar with Real-time Updates

```javascript
onInit: async () => {
  await this.loadSidebarData();
  
  // Subscribe to real-time updates
  this.websocket = new WebSocket('wss://api.example.com/updates');
  this.websocket.onmessage = (event) => {
    const update = JSON.parse(event.data);
    this.updateSidebarItem(update);
  };
},

onClose: () => {
  // Clean up WebSocket when sidebar closes
  if (this.websocket) {
    this.websocket.close();
    this.websocket = null;
  }
}
```

#### Pattern 2: Sidebar with Search/Filter

```javascript
onInit: async () => {
  await this.loadSidebarData();
  
  // Add search functionality
  const searchInput = document.getElementById('my-module-search');
  searchInput.addEventListener('input', (e) => {
    this.filterItems(e.target.value);
  });
},

filterItems(query) {
  const items = document.querySelectorAll('.sidebar-item');
  items.forEach(item => {
    const text = item.textContent.toLowerCase();
    item.style.display = text.includes(query.toLowerCase()) ? 'block' : 'none';
  });
}
```

#### Pattern 3: Sidebar with Loading State

```javascript
onInit: async () => {
  const container = document.getElementById('my-module-data-container');
  
  // Show loading spinner
  container.innerHTML = '<div class="spinner">Loading...</div>';
  
  try {
    await this.loadSidebarData();
  } catch (error) {
    // Show error state
    container.innerHTML = `
      <div class="error-state">
        <i class="fas fa-exclamation-triangle"></i>
        <p>Failed to load data</p>
        <button onclick="myModule.loadSidebarData()">Retry</button>
      </div>
    `;
  }
}
```

### Sidebar CSS Classes (Standard)

```css
/* Use these classes in your sidebar HTML */

.module-sidebar {
  /* Container for entire sidebar */
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--sidebar-bg, #1e293b);
  color: var(--sidebar-text, #e2e8f0);
}

.sidebar-header {
  /* Top section with title */
  padding: 16px;
  border-bottom: 1px solid var(--border-color, #334155);
}

.sidebar-content {
  /* Scrollable content area */
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.sidebar-footer {
  /* Bottom section with actions */
  padding: 16px;
  border-top: 1px solid var(--border-color, #334155);
}

.sidebar-item {
  /* Individual items in list */
  padding: 12px;
  margin-bottom: 8px;
  background: var(--item-bg, #2d3748);
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.sidebar-item:hover {
  background: var(--item-bg-hover, #3d4758);
}
```

### Sidebar Best Practices

1. **Lazy Load Data**: Use `onInit()` to load data only when sidebar first opens
2. **Clean Up Resources**: Use `onClose()` to close WebSockets, clear intervals, etc.
3. **Show Loading States**: Display spinner while fetching data
4. **Handle Errors**: Show error messages with retry buttons
5. **Keep It Responsive**: Sidebar should work on different screen sizes
6. **Use Standard Styles**: Follow the CSS class conventions above
7. **Persist User Actions**: Save user preferences to localStorage
8. **Test Performance**: Ensure smooth animations (60fps)

### Complete Sidebar Examples

See these modules for reference implementations:

- **Settings Sidebar** (`UI/modules_internal/settings/`) - Configuration panel
- **Vector DB Sidebar** (`UI/modules_internal/vector-db/`) - Document browser
- **InHouse Kanban Sidebar** (`UI/modules_external/inhouse-kanban/`) - Quick task view
- **Synergy Sidebar** (`UI/modules_internal/synergy/`) - Session list

### Troubleshooting Sidebars

**Issue: Sidebar not appearing**
- ✅ Check `SidebarManager.register()` was called
- ✅ Verify sidebar HTML is loaded
- ✅ Ensure toggle button has correct `data-sidebar-id`

**Issue: Sidebar appears on wrong side**
- ✅ Check `side` parameter in register() call
- ✅ Verify toggle button position (left side of screen = left sidebar)

**Issue: onInit() not being called**
- ✅ Ensure sidebar has been opened at least once
- ✅ Check browser console for errors

**Issue: Multiple sidebars conflict**
- ✅ Use unique IDs for each sidebar
- ✅ SidebarManager handles z-index automatically

---

**Status:** ✅ DESIGN COMPLETE - Ready for Implementation  
**Next Action:** Implement Phase 1 (Update Module Loader)  
**Version:** 3.0.0 (Complete Rewrite)
