# 🚀 Modern Module Loading Framework - Complete Guide

**Version**: 4.0  
**Date**: November 29, 2025  
**Status**: Production Ready ✅

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Why Composition Over Inheritance](#why-composition-over-inheritance)
3. [Module Structure](#module-structure)
4. [Lifecycle Hooks](#lifecycle-hooks)
5. [Utilities System](#utilities-system)
6. [Migration Guide](#migration-guide)
7. [Best Practices](#best-practices)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### The Problem We Solved

**Before (BaseModule Pattern)**:
```
❌ Module extends BaseModule
❌ super.initialize() in every module
❌ Tight coupling to BaseModule implementation
❌ Duplicate manifest loading
❌ Container management confusion
❌ Dashboard and sidebar tightly coupled
❌ Manual instantiation required
```

**After (Modern Composition Pattern)**:
```
✅ Module is plain object (no inheritance)
✅ Utilities injected via composition
✅ Zero coupling to framework internals
✅ Single source of truth (manifest)
✅ Framework handles containers
✅ Dashboard and sidebar independent
✅ Automatic instantiation
```

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   ModuleLoaderV4                        │
│  - Fetches manifests from API                           │
│  - Detects module pattern (modern vs legacy)            │
│  - Composes utilities based on dependencies             │
│  - Calls lifecycle hooks with utilities                 │
└─────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│               UtilityComposer                           │
│  - Selects utilities based on manifest.dependencies    │
│  - Creates module-specific logger                       │
│  - Returns composed utilities object                    │
└─────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  Modern Module                          │
│  - Plain object with lifecycle hooks                    │
│  - onDashboardLoad(utilities) - Dashboard entry         │
│  - onSidebarLoad(utilities) - Sidebar entry             │
│  - onLoad(utilities) - Generic entry                    │
│  - onUnload() - Cleanup                                 │
└─────────────────────────────────────────────────────────┘
```

---

## Why Composition Over Inheritance

### 1. **Flexibility**

**Inheritance (Old)**:
- Locked into BaseModule hierarchy
- Can't change base implementation without affecting all modules
- Must call `super.initialize()` correctly

**Composition (New)**:
- Pick exactly what utilities you need
- Framework can change without breaking modules
- No super calls, just pure functions

### 2. **Testability**

**Inheritance (Old)**:
```javascript
class MyModule extends BaseModule {
    async initialize() {
        await super.initialize(); // Hard to mock
        this.doWork();
    }
}
```

**Composition (New)**:
```javascript
const MyModule = {
    async onLoad(utilities) {
        // utilities is plain object - easy to mock
        await utilities.api.get('/data');
    }
};
```

### 3. **Clarity**

**Inheritance (Old)**:
- What does `super.initialize()` do? (Hidden magic)
- Where does `this.containerElement` come from? (Inherited)
- When is `this.manifest` populated? (Unclear)

**Composition (New)**:
- Utilities explicitly passed in
- No hidden state or magic methods
- Clear data flow: `utilities → module`

### 4. **Maintenance**

**Inheritance (Old)**:
- Change BaseModule → breaks 16 modules
- Must update all modules when BaseModule changes
- Technical debt accumulates

**Composition (New)**:
- Change UtilityComposer → no module changes needed
- Utilities are versioned interfaces
- Backward compatible by design

---

## Module Structure

### File Organization

```
UI/modules_external/my-module/
├── my-module.js              ← Module logic (composition pattern)
├── my-module.manifest.json   ← V3.0 manifest
├── my-module-SIDEBAR.html    ← Sidebar HTML (optional)
├── my-module-NEW.css         ← Styles
└── README.md                 ← Module documentation
```

### Modern Module Template

```javascript
/**
 * FILE: UI/modules_external/my-module/my-module.js
 * MODULE TYPE: external
 * ARCHITECTURE: Framework-modern (Composition pattern)
 * 
 * CAPABILITIES:
 * ✅ Dashboard: YES - Main data view
 * ✅ Sidebar: YES - Quick access panel
 * 
 * DEPENDENCIES:
 * - dom (DOM manipulation)
 * - api (Backend API calls)
 * - storage (localStorage wrapper)
 * - events (Inter-module communication)
 * 
 * LAST MODIFIED: 2025-11-29
 */

export default {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // STATE (Private to this object)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    // Utilities (injected by ModuleLoader)
    dom: null,
    api: null,
    storage: null,
    events: null,
    log: null,

    // Module-specific state
    data: [],
    filters: {},
    dashboardContainer: null,
    sidebarContainer: null,
    eventCleanupFns: [],

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // LIFECYCLE HOOKS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * DASHBOARD HOOK - Called when user clicks sidebar button
     */
    async onDashboardLoad(utilities) {
        // 1. Store utilities
        Object.assign(this, utilities);
        this.log.info('Dashboard loading...');

        try {
            // 2. Get container
            this.dashboardContainer = this.dom.getContainer('tab-my-module');

            // 3. Render UI
            this.renderDashboard();

            // 4. Setup events
            this.setupDashboardEvents();

            // 5. Load data
            await this.loadDashboardData();

            this.log.success('Dashboard loaded');
        } catch (error) {
            this.log.error('Dashboard load failed', error);
            throw error;
        }
    },

    /**
     * SIDEBAR HOOK - Called when user clicks floating toggle
     */
    async onSidebarLoad(utilities) {
        // 1. Store utilities
        Object.assign(this, utilities);
        this.log.info('Sidebar loading...');

        try {
            // 2. Get container
            this.sidebarContainer = this.dom.getContainer('my-module-sidebar');

            // 3. Setup events (HTML already loaded)
            this.setupSidebarEvents();

            // 4. Load data
            await this.loadSidebarData();

            this.log.success('Sidebar loaded');
        } catch (error) {
            this.log.error('Sidebar load failed', error);
            throw error;
        }
    },

    /**
     * CLEANUP HOOK - Called when module unloads
     */
    async onUnload() {
        this.log.info('Unloading module...');

        // Cleanup event listeners
        this.eventCleanupFns.forEach(cleanup => cleanup());
        this.eventCleanupFns = [];

        // Clear references
        this.dashboardContainer = null;
        this.sidebarContainer = null;

        this.log.success('Module unloaded');
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // RENDERING
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    renderDashboard() {
        const html = `
            <div class="module-dashboard">
                <h2>My Module Dashboard</h2>
                <div id="data-grid"></div>
            </div>
        `;
        this.dom.injectHTML(this.dashboardContainer, html);
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // EVENT HANDLING
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    setupDashboardEvents() {
        const saveBtn = this.dashboardContainer.querySelector('#save-btn');
        const cleanup = this.dom.on(saveBtn, 'click', () => this.handleSave());
        this.eventCleanupFns.push(cleanup);
    },

    setupSidebarEvents() {
        const quickActions = this.sidebarContainer.querySelectorAll('.quick-action');
        const cleanup = this.dom.onAll(quickActions, 'click', (e) => this.handleQuickAction(e));
        this.eventCleanupFns.push(cleanup);
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // DATA LOADING
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async loadDashboardData() {
        const data = await this.api.get('/api/my-module/data');
        this.data = data.items || [];
        this.renderDataGrid();
    },

    async loadSidebarData() {
        const summary = await this.api.get('/api/my-module/summary');
        this.renderSummary(summary);
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // BUSINESS LOGIC
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async handleSave() {
        this.log.info('Saving data...');
        await this.api.post('/api/my-module/save', { data: this.data });
        this.events.emit('my-module:saved', { data: this.data });
        this.log.success('Data saved');
    },

    handleQuickAction(event) {
        const action = event.target.dataset.action;
        this.log.info(`Quick action: ${action}`);
        this.events.emit('my-module:action', { action });
    }
};
```

---

## Lifecycle Hooks

### Hook Execution Order

```
User Action → ModuleLoader → Module Hook → Module Logic
```

### Available Hooks

#### 1. `onLoad(utilities)` - Generic entry point

**When Called**: 
- Module has no dashboard/sidebar
- Auto-load modules
- Programmatic loading

**Use Case**:
- Component modules (no UI)
- Background services
- Data processors

**Example**:
```javascript
async onLoad(utilities) {
    this.log = utilities.log;
    this.api = utilities.api;
    
    // Initialize background service
    await this.startDataSync();
}
```

#### 2. `onDashboardLoad(utilities)` - Dashboard entry point

**When Called**:
- User clicks sidebar button
- Programmatic: `moduleLoader.loadModule('my-module', 'dashboard')`

**Use Case**:
- Main tab initialization
- Full-screen data views
- Complex UI rendering

**Example**:
```javascript
async onDashboardLoad(utilities) {
    Object.assign(this, utilities);
    this.dashboardContainer = this.dom.getContainer('tab-my-module');
    this.renderDashboard();
    await this.loadData();
}
```

#### 3. `onSidebarLoad(utilities)` - Sidebar entry point

**When Called**:
- User clicks floating toggle
- Programmatic: `moduleLoader.loadModule('my-module', 'sidebar')`

**Use Case**:
- Quick access panels
- Lightweight views
- Notification centers

**Example**:
```javascript
async onSidebarLoad(utilities) {
    Object.assign(this, utilities);
    this.sidebarContainer = this.dom.getContainer('my-module-sidebar');
    this.setupSidebarEvents();
    await this.loadSummary();
}
```

#### 4. `onUnload()` - Cleanup hook

**When Called**:
- Module being removed from memory
- Page refresh
- Manual: `moduleLoader.unloadModule('my-module')`

**Use Case**:
- Remove event listeners
- Cancel pending requests
- Clear intervals/timeouts
- Release resources

**Example**:
```javascript
async onUnload() {
    // Clean up event listeners
    this.eventCleanupFns.forEach(fn => fn());
    
    // Cancel requests
    if (this.abortController) {
        this.abortController.abort();
    }
    
    // Clear intervals
    if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
    }
    
    this.log.info('Module unloaded');
}
```

---

## Utilities System

### Available Utilities

#### 1. **dom** - DOM Manipulation

```javascript
// Get container
const container = utilities.dom.getContainer('tab-my-module');

// Create element
const button = utilities.dom.createElement('button', {
    class: 'btn btn-primary',
    'data-action': 'save'
}, ['Save']);

// Show/hide elements
utilities.dom.show(element);
utilities.dom.hide(element);
utilities.dom.toggle(element);

// Event listeners with cleanup
const cleanup = utilities.dom.on(button, 'click', handleClick);
// Later:
cleanup(); // Remove listener

// Query selector
const buttons = utilities.dom.query('.btn', container);

// Inject HTML safely
utilities.dom.injectHTML(container, '<div>Safe HTML</div>');
```

#### 2. **api** - Backend Communication

```javascript
// GET request
const data = await utilities.api.get('/api/my-module/data');
const dataWithParams = await utilities.api.get('/api/search', { q: 'test', limit: 10 });

// POST request
const result = await utilities.api.post('/api/my-module/create', {
    name: 'New Item',
    description: 'Item description'
});

// PUT request
await utilities.api.put('/api/my-module/update/123', { name: 'Updated' });

// DELETE request
await utilities.api.delete('/api/my-module/delete/123');

// Upload file
const file = document.getElementById('file-input').files[0];
await utilities.api.upload('/api/upload', file, { type: 'document' });

// Custom timeout
const data = await utilities.api.get('/api/slow', {}, { timeout: 60000 });
```

#### 3. **storage** - Local/Session Storage

```javascript
// localStorage
utilities.storage.set('my-module:settings', { theme: 'dark', lang: 'en' });
const settings = utilities.storage.get('my-module:settings', { theme: 'light' });
utilities.storage.remove('my-module:settings');
utilities.storage.clear();

// sessionStorage
utilities.storage.session.set('temp-data', { items: [] });
const temp = utilities.storage.session.get('temp-data');
utilities.storage.session.clear();
```

#### 4. **events** - Inter-Module Communication

```javascript
// Subscribe to event
const unsubscribe = utilities.events.on('kanban:job-updated', (data) => {
    console.log('Job updated:', data);
});

// Emit event
utilities.events.emit('my-module:data-changed', { 
    items: this.data,
    timestamp: Date.now()
});

// Subscribe once
utilities.events.once('init-complete', () => {
    console.log('Initialization done');
});

// Unsubscribe
unsubscribe(); // Or:
utilities.events.off('kanban:job-updated', handler);

// Clear all listeners
utilities.events.clear('my-module:*'); // Specific event
utilities.events.clear(); // All events
```

#### 5. **log** - Module-Specific Logger

```javascript
// Info
utilities.log.info('Loading data...');

// Success
utilities.log.success('Data loaded successfully');

// Warning
utilities.log.warn('Deprecated API used');

// Error
utilities.log.error('Failed to load data', error);

// Debug
utilities.log.debug('State:', { data: this.data });
```

### Requesting Utilities in Manifest

```json
{
    "id": "my-module",
    "name": "My Module",
    "version": "1.0.0",
    
    "dependencies": {
        "utilities": ["dom", "api", "storage", "events"]
    }
}
```

**Note**: `log` utility is ALWAYS included, no need to request it.

---

## Migration Guide

### Step-by-Step: BaseModule → Modern Composition

#### Step 1: Update Module Structure

**Before (BaseModule)**:
```javascript
class InhouseKanbanModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);
        this.jobs = [];
    }
    
    async initialize() {
        await super.initialize();
        this.renderBoard();
    }
}

// Manual instantiation
window.inhousekanban = new InhouseKanbanModule('inhouse-kanban');
window.inhousekanban.initialize();
```

**After (Modern)**:
```javascript
export default {
    // State
    jobs: [],
    dom: null,
    api: null,
    log: null,
    
    // Lifecycle hooks
    async onDashboardLoad(utilities) {
        Object.assign(this, utilities);
        this.log.info('Loading dashboard...');
        
        const container = this.dom.getContainer('tab-inhouse-kanban');
        this.renderBoard(container);
    }
};

// NO manual instantiation - ModuleLoader handles it
```

#### Step 2: Update Manifest

**Add dependencies**:
```json
{
    "dependencies": {
        "utilities": ["dom", "api", "storage", "events"]
    },
    
    "capabilities": {
        "dashboard": {
            "enabled": true,
            "tab_id": "inhouse-kanban"
        },
        "sidebar": {
            "enabled": true,
            "html_file": "inhouse-kanban-SIDEBAR.html"
        }
    }
}
```

#### Step 3: Replace BaseModule Patterns

**Pattern 1: Container Access**

Before:
```javascript
this.containerElement // From BaseModule
```

After:
```javascript
this.dashboardContainer = this.dom.getContainer('tab-my-module');
```

**Pattern 2: API Calls**

Before:
```javascript
const response = await fetch(`${this.API_BASE_URL}/api/data`);
const data = await response.json();
```

After:
```javascript
const data = await this.api.get('/api/data');
```

**Pattern 3: Event Listeners**

Before:
```javascript
this.containerElement.addEventListener('click', this.handleClick.bind(this));
```

After:
```javascript
const cleanup = this.dom.on(this.dashboardContainer, 'click', this.handleClick.bind(this));
this.eventCleanupFns.push(cleanup);
```

**Pattern 4: Logging**

Before:
```javascript
console.log('[InhouseKanban] Loading data...');
```

After:
```javascript
this.log.info('Loading data...');
```

#### Step 4: Remove Manual Instantiation

**Delete from module file**:
```javascript
// DELETE THESE LINES:
if (typeof window !== 'undefined') {
    window.inhousekanban = new InhouseKanbanModule('inhouse-kanban');
    window.inhousekanban.initialize();
}
```

#### Step 5: Test Module

```javascript
// In browser console:
const moduleLoader = window.ModuleLoaderV4;
await moduleLoader.loadModule('my-module', 'dashboard');
```

---

## Best Practices

### 1. **State Management**

✅ **DO**:
```javascript
export default {
    // Clear state declaration
    data: [],
    filters: { status: 'all' },
    isLoading: false,
    
    async onDashboardLoad(utilities) {
        // Initialize state
        this.data = [];
        this.isLoading = true;
    }
};
```

❌ **DON'T**:
```javascript
export default {
    async onDashboardLoad(utilities) {
        // Creating state in hook (unclear)
        this.someNewProperty = [];
    }
};
```

### 2. **Event Cleanup**

✅ **DO**:
```javascript
setupEvents() {
    const cleanup1 = this.dom.on(btn1, 'click', handler1);
    const cleanup2 = this.dom.on(btn2, 'click', handler2);
    this.eventCleanupFns.push(cleanup1, cleanup2);
},

async onUnload() {
    this.eventCleanupFns.forEach(fn => fn());
    this.eventCleanupFns = [];
}
```

❌ **DON'T**:
```javascript
setupEvents() {
    btn1.addEventListener('click', handler1);
    btn2.addEventListener('click', handler2);
    // No cleanup tracking - memory leak!
}
```

### 3. **Error Handling**

✅ **DO**:
```javascript
async loadData() {
    try {
        const data = await this.api.get('/api/data');
        this.data = data;
        this.log.success('Data loaded');
    } catch (error) {
        this.log.error('Failed to load data', error);
        this.showErrorMessage(error.message);
    }
}
```

❌ **DON'T**:
```javascript
async loadData() {
    const data = await this.api.get('/api/data'); // Unhandled rejection
    this.data = data;
}
```

### 4. **Utility Storage**

✅ **DO**:
```javascript
async onDashboardLoad(utilities) {
    // Store ALL utilities at once
    Object.assign(this, utilities);
    
    // Now use them
    this.log.info('Dashboard loading...');
}
```

❌ **DON'T**:
```javascript
async onDashboardLoad(utilities) {
    // Manually assign each one (tedious)
    this.dom = utilities.dom;
    this.api = utilities.api;
    this.storage = utilities.storage;
    this.events = utilities.events;
    this.log = utilities.log;
}
```

### 5. **Container Management**

✅ **DO**:
```javascript
async onDashboardLoad(utilities) {
    Object.assign(this, utilities);
    
    // Get container once, store it
    this.dashboardContainer = this.dom.getContainer('tab-my-module');
    
    // Use stored reference
    this.renderDashboard();
}
```

❌ **DON'T**:
```javascript
async onDashboardLoad(utilities) {
    // Getting container multiple times (inefficient)
    const container1 = document.getElementById('tab-my-module');
    // ... later ...
    const container2 = document.getElementById('tab-my-module');
}
```

---

## Examples

### Example 1: Simple Dashboard Module

```javascript
export default {
    dom: null,
    api: null,
    log: null,
    data: [],
    container: null,
    
    async onDashboardLoad(utilities) {
        Object.assign(this, utilities);
        this.log.info('Loading dashboard...');
        
        this.container = this.dom.getContainer('tab-simple-module');
        this.render();
        await this.loadData();
    },
    
    render() {
        const html = `
            <div class="simple-dashboard">
                <h2>Simple Module</h2>
                <div id="data-list"></div>
            </div>
        `;
        this.dom.injectHTML(this.container, html);
    },
    
    async loadData() {
        this.data = await this.api.get('/api/simple/data');
        this.renderList();
    },
    
    renderList() {
        const listContainer = this.container.querySelector('#data-list');
        listContainer.innerHTML = this.data.map(item => 
            `<div class="item">${item.name}</div>`
        ).join('');
    }
};
```

### Example 2: Dashboard + Sidebar Module

```javascript
export default {
    dom: null,
    api: null,
    storage: null,
    events: null,
    log: null,
    
    data: [],
    dashboardContainer: null,
    sidebarContainer: null,
    eventCleanupFns: [],
    
    // Dashboard lifecycle
    async onDashboardLoad(utilities) {
        Object.assign(this, utilities);
        this.log.info('Loading dashboard...');
        
        this.dashboardContainer = this.dom.getContainer('tab-dual-module');
        this.renderDashboard();
        this.setupDashboardEvents();
        await this.loadFullData();
    },
    
    // Sidebar lifecycle
    async onSidebarLoad(utilities) {
        Object.assign(this, utilities);
        this.log.info('Loading sidebar...');
        
        this.sidebarContainer = this.dom.getContainer('dual-module-sidebar');
        this.setupSidebarEvents();
        await this.loadSummary();
    },
    
    // Cleanup
    async onUnload() {
        this.eventCleanupFns.forEach(fn => fn());
        this.log.info('Module unloaded');
    },
    
    renderDashboard() {
        const html = `
            <div class="dashboard">
                <h2>Full Data View</h2>
                <div id="data-grid"></div>
            </div>
        `;
        this.dom.injectHTML(this.dashboardContainer, html);
    },
    
    setupDashboardEvents() {
        const saveBtn = this.dashboardContainer.querySelector('#save-btn');
        const cleanup = this.dom.on(saveBtn, 'click', () => this.handleSave());
        this.eventCleanupFns.push(cleanup);
    },
    
    setupSidebarEvents() {
        const quickBtn = this.sidebarContainer.querySelector('#quick-action');
        const cleanup = this.dom.on(quickBtn, 'click', () => this.handleQuickAction());
        this.eventCleanupFns.push(cleanup);
    },
    
    async loadFullData() {
        this.data = await this.api.get('/api/dual-module/full');
        this.renderDataGrid();
    },
    
    async loadSummary() {
        const summary = await this.api.get('/api/dual-module/summary');
        this.renderSummary(summary);
    },
    
    handleSave() {
        this.log.info('Saving...');
        this.events.emit('dual-module:saved', { data: this.data });
    },
    
    handleQuickAction() {
        this.log.info('Quick action triggered');
        this.events.emit('dual-module:action', { source: 'sidebar' });
    }
};
```

### Example 3: Component Module (No UI)

```javascript
export default {
    api: null,
    storage: null,
    events: null,
    log: null,
    
    syncInterval: null,
    
    async onLoad(utilities) {
        Object.assign(this, utilities);
        this.log.info('Starting background service...');
        
        // Start background sync
        this.syncInterval = setInterval(() => this.syncData(), 60000);
        
        // Listen for events from other modules
        this.events.on('*:data-changed', (data) => this.handleDataChange(data));
        
        this.log.success('Background service started');
    },
    
    async onUnload() {
        clearInterval(this.syncInterval);
        this.events.clear();
        this.log.info('Background service stopped');
    },
    
    async syncData() {
        this.log.debug('Syncing data...');
        await this.api.post('/api/sync', { timestamp: Date.now() });
    },
    
    handleDataChange(data) {
        this.log.debug('Data changed:', data);
        this.syncData(); // Trigger immediate sync
    }
};
```

---

## Troubleshooting

### Issue 1: "Container not found"

**Error**:
```
Error: Container not found: #tab-my-module
```

**Solution**:
- Check manifest `capabilities.dashboard.tab_id` matches container ID
- Verify ModuleLoader generated tab container
- Check browser console for tab generation errors

### Issue 2: "Module not loading"

**Symptoms**: Module doesn't appear, no errors

**Solution**:
```javascript
// Check if module registered
const moduleLoader = window.ModuleLoaderV4;
console.log(moduleLoader.modules.has('my-module')); // Should be true

// Check if module available
const module = moduleLoader.modules.get('my-module');
console.log(module.available); // Should be true

// Try loading manually
await moduleLoader.loadModule('my-module', 'dashboard');
```

### Issue 3: "Utilities undefined"

**Error**:
```
TypeError: Cannot read property 'get' of null (this.api)
```

**Solution**:
- Ensure utilities stored: `Object.assign(this, utilities);`
- Check manifest has `dependencies.utilities` array
- Verify lifecycle hook called correctly

### Issue 4: "Event listeners not cleaning up"

**Symptoms**: Memory leaks, duplicate handlers

**Solution**:
```javascript
// Track cleanup functions
this.eventCleanupFns = [];

setupEvents() {
    const cleanup = this.dom.on(btn, 'click', handler);
    this.eventCleanupFns.push(cleanup); // ← CRITICAL
}

async onUnload() {
    this.eventCleanupFns.forEach(fn => fn()); // ← CRITICAL
}
```

### Issue 5: "Module pattern not detected"

**Error**:
```
[ModuleLoaderV4] Unknown module pattern: unknown
```

**Solution**:
- Ensure module exports default object: `export default { ... };`
- Verify lifecycle hooks exist: `onLoad`, `onDashboardLoad`, or `onSidebarLoad`
- Check file uses ES6 module syntax (not script tags)

---

## Framework Advantages Summary

| Feature | BaseModule (Old) | Composition (Modern) |
|---------|------------------|----------------------|
| Inheritance | Required | None |
| Coupling | Tight | Loose |
| Testing | Hard | Easy |
| Maintenance | Difficult | Simple |
| Flexibility | Limited | High |
| Learning Curve | Medium | Low |
| Migration Cost | N/A | 2-3 hours/module |
| Framework Updates | Break modules | Backward compatible |
| Code Clarity | Hidden magic | Explicit |
| Memory Management | Manual | Automatic |

---

**Last Updated**: November 29, 2025  
**Version**: 4.0  
**Status**: ✅ Production Ready  
**Migrated Modules**: 0/16 (In Progress)
