# 🚀 Modern Module Framework - Quick Reference Card

**Version**: 4.0 | **Date**: November 29, 2025

---

## 📦 Module Structure (Copy & Paste)

```javascript
/**
 * FILE: UI/modules_external/[module-name]/[module-name].js
 * MODULE TYPE: external
 * ARCHITECTURE: Framework-modern (Composition pattern)
 * 
 * CAPABILITIES:
 * ✅ Dashboard: YES - [Description]
 * ✅ Sidebar: YES - [Description]
 * 
 * DEPENDENCIES: dom, api, storage, events
 * LAST MODIFIED: 2025-11-29
 */

export default {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // STATE
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    // Utilities (injected by ModuleLoader)
    dom: null,
    api: null,
    storage: null,
    events: null,
    log: null,

    // Module state
    data: [],
    dashboardContainer: null,
    sidebarContainer: null,
    eventCleanupFns: [],

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // LIFECYCLE HOOKS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async onDashboardLoad(utilities) {
        Object.assign(this, utilities);
        this.log.info('Loading dashboard...');

        try {
            this.dashboardContainer = this.dom.getContainer('tab-module-name');
            this.renderDashboard();
            this.setupDashboardEvents();
            await this.loadData();
            this.log.success('Dashboard loaded');
        } catch (error) {
            this.log.error('Dashboard load failed', error);
            throw error;
        }
    },

    async onSidebarLoad(utilities) {
        Object.assign(this, utilities);
        this.log.info('Loading sidebar...');

        try {
            this.sidebarContainer = this.dom.getContainer('module-name-sidebar');
            this.setupSidebarEvents();
            await this.loadSummary();
            this.log.success('Sidebar loaded');
        } catch (error) {
            this.log.error('Sidebar load failed', error);
            throw error;
        }
    },

    async onUnload() {
        this.eventCleanupFns.forEach(fn => fn());
        this.eventCleanupFns = [];
        this.log.info('Module unloaded');
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // YOUR METHODS HERE
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    renderDashboard() {
        // Your rendering logic
    },

    setupDashboardEvents() {
        // Your event setup
    },

    async loadData() {
        // Your data loading
    }
};
```

---

## 📄 Manifest Template (V3.0)

```json
{
    "id": "module-name",
    "name": "Display Name",
    "version": "1.0.0",
    "type": "external",
    "category": "Tools",
    "icon": "fas fa-icon-name",
    "color": "#4A90E2",
    
    "dependencies": {
        "utilities": ["dom", "api", "storage", "events"]
    },
    
    "capabilities": {
        "dashboard": {
            "enabled": true,
            "tab_id": "module-name",
            "tab_label": "Dashboard Title",
            "rendering": "js-controlled",
            "initialization": "lazy"
        },
        "sidebar": {
            "enabled": true,
            "side": "right",
            "width": "480px",
            "html_file": "module-name-SIDEBAR.html",
            "framework": "SidebarManager",
            "rendering": "html-template",
            "initialization": "on-open",
            "toggle_button": {
                "position": "right",
                "default_top": 280,
                "opens_sidebar": true
            }
        }
    },
    
    "files": {
        "js": "module-name.js",
        "css": "module-name.css",
        "sidebar_html": "module-name-SIDEBAR.html"
    },
    
    "loading": {
        "strategy": "lazy",
        "priority": 50
    }
}
```

---

## 🔧 Utility Cheat Sheet

### DOM Utils

```javascript
// Get container
const container = this.dom.getContainer('tab-module');

// Create element
const btn = this.dom.createElement('button', {
    class: 'btn btn-primary',
    'data-action': 'save'
}, ['Save']);

// Show/hide
this.dom.show(element);
this.dom.hide(element);
this.dom.toggle(element);

// Event listener with cleanup
const cleanup = this.dom.on(btn, 'click', handler);
this.eventCleanupFns.push(cleanup);

// Batch event listeners
const cleanup = this.dom.onAll(buttons, 'click', handler);
this.eventCleanupFns.push(cleanup);

// Inject HTML
this.dom.injectHTML(container, '<div>Content</div>');

// Query selector
const items = this.dom.query('.item', container);
```

### API Client

```javascript
// GET
const data = await this.api.get('/api/endpoint');
const filtered = await this.api.get('/api/search', { q: 'test' });

// POST
const result = await this.api.post('/api/create', { name: 'Item' });

// PUT
await this.api.put('/api/update/123', { name: 'Updated' });

// DELETE
await this.api.delete('/api/delete/123');

// Upload file
await this.api.upload('/api/upload', file, { type: 'doc' });

// Custom timeout
const data = await this.api.get('/api/slow', {}, { timeout: 60000 });
```

### Storage Utils

```javascript
// localStorage
this.storage.set('key', { data: 'value' });
const data = this.storage.get('key', defaultValue);
this.storage.remove('key');
this.storage.clear();

// sessionStorage
this.storage.session.set('temp', { items: [] });
const temp = this.storage.session.get('temp');
this.storage.session.clear();
```

### Event Bus

```javascript
// Subscribe
const unsubscribe = this.events.on('event-name', (data) => {
    console.log('Event received:', data);
});

// Emit
this.events.emit('my-module:action', { type: 'save', data: this.data });

// Subscribe once
this.events.once('init-complete', () => console.log('Done'));

// Unsubscribe
unsubscribe();
// Or:
this.events.off('event-name', handler);

// Clear
this.events.clear('event-name'); // Specific event
this.events.clear(); // All events
```

### Logger

```javascript
this.log.info('Loading data...');
this.log.success('Data loaded successfully');
this.log.warn('Deprecated API used');
this.log.error('Failed to load data', error);
this.log.debug('State:', { data: this.data });
```

---

## 🔄 Migration Patterns

### Pattern 1: Container Access

```javascript
// Before (BaseModule)
this.containerElement

// After (Modern)
this.dashboardContainer = this.dom.getContainer('tab-module-id');
```

### Pattern 2: API Calls

```javascript
// Before
const response = await fetch(`${this.API_BASE_URL}/api/data`);
const data = await response.json();

// After
const data = await this.api.get('/api/data');
```

### Pattern 3: Event Listeners

```javascript
// Before
element.addEventListener('click', handler);

// After
const cleanup = this.dom.on(element, 'click', handler);
this.eventCleanupFns.push(cleanup);
```

### Pattern 4: Logging

```javascript
// Before
console.log('[ModuleName] Loading...');
console.error('[ModuleName] Error:', error);

// After
this.log.info('Loading...');
this.log.error('Error occurred', error);
```

### Pattern 5: Class to Object

```javascript
// Before
class MyModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);
        this.data = [];
    }
    
    async initialize() {
        await super.initialize();
        this.render();
    }
}

// After
export default {
    data: [],
    dom: null,
    log: null,
    
    async onDashboardLoad(utilities) {
        Object.assign(this, utilities);
        this.render();
    }
};
```

### Pattern 6: Remove Manual Instantiation

```javascript
// DELETE THIS (at bottom of module file):
if (typeof window !== 'undefined') {
    window.mymodule = new MyModule('my-module');
    window.mymodule.initialize();
}
```

---

## 🧪 Testing Commands

### Load Module

```javascript
const moduleLoader = window.ModuleLoaderV4;

// Load dashboard
await moduleLoader.loadModule('module-name', 'dashboard');

// Load sidebar
await moduleLoader.loadModule('module-name', 'sidebar');

// Get module instance
const module = moduleLoader.getModule('module-name');
console.log(module);

// Unload module
await moduleLoader.unloadModule('module-name');
```

### Check Module Status

```javascript
// Is registered?
console.log(moduleLoader.modules.has('module-name'));

// Is available?
const module = moduleLoader.modules.get('module-name');
console.log(module.available);

// Is loaded?
console.log(moduleLoader.loadedModules.has('module-name'));

// Get loaded info
const loaded = moduleLoader.loadedModules.get('module-name');
console.log(loaded.type); // 'modern' or 'legacy'
```

---

## ⚠️ Common Mistakes

### ❌ Mistake 1: Not storing utilities

```javascript
// WRONG
async onDashboardLoad(utilities) {
    // utilities not stored
    this.log.info('Loading...'); // ← ERROR: this.log is null
}

// CORRECT
async onDashboardLoad(utilities) {
    Object.assign(this, utilities); // ← Store utilities FIRST
    this.log.info('Loading...');
}
```

### ❌ Mistake 2: Not tracking cleanup

```javascript
// WRONG
setupEvents() {
    btn.addEventListener('click', handler); // No cleanup tracking
}

// CORRECT
setupEvents() {
    const cleanup = this.dom.on(btn, 'click', handler);
    this.eventCleanupFns.push(cleanup); // ← Track for cleanup
}
```

### ❌ Mistake 3: Not implementing onUnload

```javascript
// WRONG
export default {
    // ... no onUnload method
};

// CORRECT
export default {
    async onUnload() {
        this.eventCleanupFns.forEach(fn => fn());
        this.eventCleanupFns = [];
    }
};
```

### ❌ Mistake 4: Wrong container ID

```javascript
// WRONG
this.dashboardContainer = this.dom.getContainer('wrong-id'); // Error!

// CORRECT (match manifest tab_id)
this.dashboardContainer = this.dom.getContainer('tab-module-name');
```

### ❌ Mistake 5: Keeping manual instantiation

```javascript
// WRONG - DELETE THIS:
window.mymodule = new MyModule('my-module');
window.mymodule.initialize();

// CORRECT - Let ModuleLoader handle it
export default { /* ... */ };
```

---

## 🔍 Debugging Tips

### Enable Debug Logging

```javascript
// In browser console
localStorage.setItem('module-debug', 'true');
location.reload();
```

### Check Module Loading

```javascript
// Watch ModuleLoader logs
const originalLog = console.log;
console.log = function(...args) {
    if (args[0]?.includes('ModuleLoaderV4')) {
        originalLog.apply(console, ['🔷', ...args]);
    } else {
        originalLog.apply(console, args);
    }
};
```

### Inspect Module State

```javascript
const loader = window.ModuleLoaderV4;
const module = loader.getModule('module-name');

console.log('Type:', module.type); // 'modern' or 'legacy'
console.log('Module:', module.module); // Module object
console.log('Utilities:', module.utilities); // Composed utilities
console.log('Manifest:', module.manifest); // Module manifest
```

---

## 📊 Performance Tips

### 1. Lazy Load Data

```javascript
async onDashboardLoad(utilities) {
    Object.assign(this, utilities);
    this.renderDashboard(); // ← Render UI immediately
    await this.loadData(); // ← Load data after render
}
```

### 2. Debounce Search

```javascript
setupSearch() {
    let timeout;
    const cleanup = this.dom.on(searchInput, 'input', (e) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => this.search(e.target.value), 300);
    });
    this.eventCleanupFns.push(cleanup);
}
```

### 3. Batch DOM Updates

```javascript
renderList(items) {
    const html = items.map(item => `<div>${item.name}</div>`).join('');
    this.dom.injectHTML(listContainer, html); // Single update
}
```

### 4. Use Event Delegation

```javascript
setupEvents() {
    // Instead of:
    // buttons.forEach(btn => this.dom.on(btn, 'click', handler));
    
    // Do:
    const cleanup = this.dom.on(container, 'click', (e) => {
        if (e.target.matches('.btn')) {
            this.handleClick(e);
        }
    });
    this.eventCleanupFns.push(cleanup);
}
```

---

## 🎯 Quick Checklist

Before committing module:

- [ ] `export default { ... }` structure
- [ ] Utilities stored: `Object.assign(this, utilities)`
- [ ] Lifecycle hooks: `onDashboardLoad`, `onSidebarLoad`, `onUnload`
- [ ] Event cleanup: `this.eventCleanupFns.push(cleanup)`
- [ ] Error handling: `try/catch` around async operations
- [ ] Logging: Use `this.log.*` not `console.*`
- [ ] Container access: `this.dom.getContainer()`
- [ ] API calls: `this.api.get/post/put/delete()`
- [ ] Manifest V3.0 with `dependencies.utilities`
- [ ] No manual instantiation at file bottom
- [ ] Tests passing in browser

---

**Print this card and keep it handy! 🖨️**

**Version**: 4.0 | **Last Updated**: November 29, 2025
