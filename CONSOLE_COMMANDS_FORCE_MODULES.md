# 🎮 Console Commands - Force Show Modules

## 🚀 **Quick Force-Show Commands**

### **Universal Search Module**

```javascript
// FORCE LOAD Universal Search
(async () => {
    console.log('🔍 FORCE LOADING Universal Search...');
    
    // 1. Get/Create container
    let container = document.getElementById('tab-universal-search');
    if (!container) {
        const mainContent = document.querySelector('.main-content');
        container = document.createElement('div');
        container.id = 'tab-universal-search';
        container.className = 'tab-content';
        mainContent.appendChild(container);
        console.log('✅ Created tab-universal-search container');
    }
    
    // 2. Load HTML
    if (!container.querySelector('#universal-search-container')) {
        const response = await fetch('/modules_internal/universal-search/universal-search.html');
        const html = await response.text();
        container.innerHTML = html;
        console.log('✅ Loaded HTML');
    }
    
    // 3. Load CSS
    if (!document.getElementById('universal-search-styles')) {
        const link = document.createElement('link');
        link.id = 'universal-search-styles';
        link.rel = 'stylesheet';
        link.href = '/modules_internal/universal-search/universal-search.css';
        document.head.appendChild(link);
        console.log('✅ Loaded CSS');
    }
    
    // 4. Load JavaScript
    if (!window.UniversalSearchModule) {
        const script = document.createElement('script');
        script.src = '/modules_internal/universal-search/universal-search.js';
        document.body.appendChild(script);
        await new Promise(resolve => script.onload = resolve);
        console.log('✅ Loaded JavaScript');
    }
    
    // 5. Switch to tab
    switchTab('universal-search');
    console.log('✅ Switched to tab');
    
    // 6. Initialize module
    if (window.UniversalSearchModule && typeof window.UniversalSearchModule.onDashboardLoad === 'function') {
        const utilities = {
            dom: {
                on: (el, event, handler) => el.addEventListener(event, handler),
                getContainer: () => document.getElementById('universal-search-container')
            },
            api: {
                get: async (url, opts) => {
                    const params = new URLSearchParams(opts?.params || {});
                    const response = await fetch(`${url}?${params}`);
                    return response.json();
                }
            },
            storage: window.localStorage,
            events: { emit: () => {} },
            log: console
        };
        await window.UniversalSearchModule.onDashboardLoad(utilities);
        console.log('✅ Module initialized');
    }
    
    console.log('🎉 Universal Search LOADED!');
})();
```

### **Vector Database Module (Sidebar)**

```javascript
// FORCE OPEN Vector Database Sidebar
if (window.SidebarManager) {
    window.SidebarManager.open('vector-database');
    console.log('✅ Vector Database sidebar opened');
} else {
    console.error('❌ SidebarManager not available');
}
```

---

## 🔧 **Diagnostic Commands**

### **Check if modules are registered**

```javascript
// Check module registration
if (window.moduleLoader) {
    console.log('📦 Registered modules:', Array.from(window.moduleLoader.modules.keys()));
    
    // Check specific modules
    console.log('Universal Search:', window.moduleLoader.modules.get('universal-search'));
    console.log('Vector Database:', window.moduleLoader.modules.get('vector-database'));
} else {
    console.error('❌ ModuleLoader not available');
}
```

### **Check if tabs exist in DOM**

```javascript
// Check all tabs
const allTabs = document.querySelectorAll('.tab-content');
console.log('📋 All tabs:', Array.from(allTabs).map(t => t.id));
console.log('✅ Universal Search tab exists:', !!document.getElementById('tab-universal-search'));
console.log('✅ Vector Database tab exists:', !!document.getElementById('tab-vector-database'));
```

### **Check if modules are loaded**

```javascript
// Check module objects
console.log('UniversalSearchModule:', window.UniversalSearchModule);
console.log('VectorDatabaseModule:', window.VectorDatabaseModule);
```

---

## 🎯 **How to Make Them Appear Always**

### **Option 1: Add Sidebar Buttons (RECOMMENDED)**

The modules need sidebar buttons to be clickable. Add these to `business-ai-platform-v2.html`:

**Location:** Around line 15750-15800 (in the sidebar section)

```html
<!-- Universal Search Button -->
<button class="sidebar-icon-btn" data-action="universal-search" title="Universal Search">
    <i class="fas fa-magnifying-glass"></i>
</button>

<!-- Vector Database Button (already exists as 'vectordb') -->
<button class="sidebar-icon-btn" data-action="vectordb" title="Vector Database">
    <i class="fas fa-database"></i>
</button>
```

**Status:**
- ✅ Vector Database button exists (data-action="vectordb")
- ❌ Universal Search button needs to be added

### **Option 2: Register in ModuleLoader**

Ensure modules are properly registered by the backend:

**Check backend registration:**

```python
# In AI_infrastructure/core/module_registry.py
# Ensure UI/modules_internal is scanned

SCAN_PATHS = [
    'frontend/modules',      # External modules
    'UI/modules_internal'    # Internal modules (ADD THIS)
]
```

**Verify manifest.json files exist:**
- ✅ `UI/modules_internal/universal-search/manifest.json`
- ✅ `UI/modules_internal/vector_database/manifest.json`

### **Option 3: Auto-Load on Page Load**

Add to the page initialization (around line 21700):

```javascript
// Auto-load internal modules on page ready
document.addEventListener('DOMContentLoaded', async () => {
    // Wait for ModuleLoader to initialize
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Auto-register internal modules
    if (window.moduleLoader) {
        console.log('[AUTO-LOAD] Registering internal modules...');
        
        // Register Universal Search
        window.moduleLoader.modules.set('universal-search', {
            id: 'universal-search',
            name: 'Universal Search',
            available: true,
            main_tab: true,
            main_tab_id: 'universal-search',
            capabilities: {
                dashboard: { enabled: true, tab_id: 'universal-search' }
            },
            paths: {
                html: '/modules_internal/universal-search/universal-search.html',
                script: '/modules_internal/universal-search/universal-search.js',
                style: '/modules_internal/universal-search/universal-search.css'
            }
        });
        
        // Register Vector Database
        window.moduleLoader.modules.set('vector-database', {
            id: 'vector-database',
            name: 'Vector Database',
            available: true,
            main_tab: true,
            main_tab_id: 'vector-database',
            capabilities: {
                dashboard: { enabled: true, tab_id: 'vector-database' },
                sidebar: { enabled: true }
            },
            paths: {
                html: '/modules_internal/vector_database/vector_database.html',
                script: '/modules_internal/vector_database/vector_database.js',
                style: '/modules_internal/vector_database/vector_database.css'
            }
        });
        
        // Regenerate tabs
        window.moduleLoader.generateMainTabs();
        console.log('[AUTO-LOAD] Internal modules registered');
    }
});
```

---

## 📊 **Verification Steps**

1. **Open browser console** (F12)
2. **Run diagnostic commands** to check module status
3. **Run force-load commands** to test manual loading
4. **Implement permanent fix** (Option 1, 2, or 3 above)
5. **Refresh page** (Ctrl+F5) and verify modules appear

---

## 🐛 **Troubleshooting**

### **Module won't load**
```javascript
// Check for errors
console.log('Tab exists:', !!document.getElementById('tab-universal-search'));
console.log('Module loaded:', !!window.UniversalSearchModule);
console.log('Manifest:', window.moduleLoader?.modules.get('universal-search'));
```

### **Tab exists but won't show**
```javascript
// Force show tab
const tab = document.getElementById('tab-universal-search');
if (tab) {
    tab.classList.add('active');
    console.log('✅ Tab force-shown');
}
```

### **Utilities not passed**
```javascript
// Check if module has utilities
if (window.UniversalSearchModule) {
    console.log('Has dom?', !!window.UniversalSearchModule.dom);
    console.log('Has api?', !!window.UniversalSearchModule.api);
}
```

---

## 🎉 **Success Indicators**

✅ Console shows: `[UNIVERSAL SEARCH] Module loaded successfully`
✅ Tab appears in available tabs list
✅ Module responds to user interactions
✅ No console errors about missing utilities
✅ Sidebar button (if added) shows active state when clicked

