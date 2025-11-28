# Module Sidebar Integration Guide

**Created:** November 28, 2025  
**Purpose:** How to add consistent sidebars to new modules using the Universal Sidebar Framework

---

## 📋 Overview

All module sidebars in the platform use the **Universal Sidebar Framework** for consistent behavior. This guide shows you how to add a sidebar to your new module.

---

## 🚀 Quick Start - Adding a Sidebar to Your Module

### Integration Methods

The Universal Sidebar Framework integrates with the **Module System** automatically. You can add a sidebar in two ways:

1. **MODULE SYSTEM (Recommended)** - Add sidebar config to your module's `manifest.json`
2. **Manual Registration** - Register directly with `SidebarManager.register()`

---

## 📦 Method 1: Module System Integration (Automatic)

**Best for:** External modules loaded via the Module System

### Step 1: Configure Sidebar in manifest.json

Add sidebar configuration to your module's `manifest.json`:

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
    "width": 450,
    "html_file": "my-module-sidebar.html"
  },
  "main_tab": false
}
```

**Sidebar Configuration Options:**
- `enabled` (boolean) - Enable sidebar for this module
- `position` (string) - "left" or "right" (default: "left")
- `width` (number) - Sidebar width in pixels (default: 450)
- `html_file` (string) - HTML template file for sidebar content

### Step 2: Create Your Sidebar HTML

Create `my-module-sidebar.html` in your module folder:

```html
<!-- MY MODULE SIDEBAR -->
<div class="universal-sidebar collapsed" 
     id="my-module-sidebar" 
     data-side="left">
    
    <div class="universal-sidebar-header">
        <div class="universal-sidebar-title">
            <span><i class="fas fa-cube"></i> My Module</span>
            <button class="universal-sidebar-close" 
                    onclick="SidebarManager.close('my-module-sidebar')">
                <i class="fas fa-times"></i>
            </button>
        </div>
    </div>

    <div class="universal-sidebar-content" id="my-module-content">
        <!-- Your module content goes here -->
    </div>
</div>
```

### Step 3: Module Loader Auto-Registers Sidebar

**That's it!** The Module System automatically:
- ✅ Creates floating toggle button (if `floating_toggle: true`)
- ✅ Registers sidebar with Universal Sidebar Framework
- ✅ Handles click events and sidebar toggle
- ✅ Manages z-index and animations
- ✅ Persists open/closed state

**No manual registration needed!** The `ModuleLoader` reads your `manifest.json` and calls `SidebarManager.register()` automatically.

---

## 🔧 Method 2: Manual Registration (Legacy/Core Modules)

**Best for:** Core sidebars not part of the Module System (Settings, Synergy, etc.)

### Step 1: Create Sidebar HTML

Add your sidebar container to `business-ai-platform-v2.html`:

```html
<!-- LEGACY MODULE SIDEBAR -->
<div class="universal-sidebar collapsed" 
     id="legacy-sidebar" 
     data-side="right">
    
    <div class="universal-sidebar-header">
        <div class="universal-sidebar-title">
            <span><i class="fas fa-cog"></i> Legacy Module</span>
            <button class="universal-sidebar-close" 
                    onclick="SidebarManager.close('legacy-sidebar')">
                <i class="fas fa-times"></i>
            </button>
        </div>
    </div>

    <div class="universal-sidebar-content">
        <!-- Content -->
    </div>
</div>
```

### Step 2: Create Toggle Button

```html
<button class="sidebar-toggle-btn" 
        id="legacy-sidebar-toggle" 
        data-side="right"
        title="Legacy Module">
    <i class="fas fa-cog"></i>
</button>
```

### Step 3: Manual Registration

Add to `modules/sidebar-framework/sidebar-init.js`:

```javascript
SidebarManager.register({
    id: 'legacy-sidebar',
    side: 'right',
    toggleButtonId: 'legacy-sidebar-toggle',
    width: '450px',
    icon: 'fa-cog',
    title: 'Legacy Module',
    onInit: async () => {
        // Initialize on first open
        await initializeLegacyModule();
    }
});
```

---

## 🎯 Module System Manifest Examples

### Example 1: Simple Sidebar Module

```json
{
  "id": "analytics",
  "name": "Analytics Dashboard",
  "icon": "fas fa-chart-line",
  "color": "#10b981",
  "floating_toggle": true,
  "sidebar": {
    "enabled": true,
    "position": "right",
    "width": 500
  }
}
```

### Example 2: Sidebar + Main Tab Module

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
**Note:** When `main_tab: true`, clicking the sidebar button switches to the main tab instead of opening a sidebar.

### Example 3: Production Workflow (InHouse Kanban)

```json
{
  "id": "inhouse-kanban",
  "name": "Production Workflow",
  "icon": "fas fa-industry",
  "color": "#00509E",
  "floating_toggle": true,
  "floating_toggle_opens_sidebar": true,
  "sidebar": {
    "enabled": true,
    "position": "left",
    "width": 480,
    "html_file": "inhouse-kanban-SIDEBAR.html"
  }
}
```

---

## ✅ What You Get Automatically

Your sidebar now has:
- ✅ Consistent slide-in/out animation
- ✅ Draggable toggle button (users can reposition it)
- ✅ Automatic z-index management (no conflicts)
- ✅ State persistence (remembers if it's open/closed)
- ✅ Lazy loading (data loads only when first opened)

---

## 📖 Current Sidebars in the Platform

| Module | Type | Side | Toggle Button | Sidebar ID | Status |
|--------|------|------|---------------|------------|--------|
| **Synergy Sessions** | Manual | Left | Top-left floating | `synergy-sidebar` | ✅ Active |
| **Automations** | Manual | Right | Top-right floating | `automations-sidebar` | ✅ Active |
| **Settings** | Manual | Right | Left main sidebar | `settings-sidebar` | ✅ Active |
| **InHouse Kanban** | Module System | Left | Floating (auto) | `inhouse-kanban-sidebar` | ✅ Active |
| **Communication Hub** | Module System | N/A (Main Tab) | Left main sidebar | N/A | ✅ Active |

**Legend:**
- **Manual** - Registered in `sidebar-init.js` (core platform sidebars)
- **Module System** - Auto-registered via `manifest.json` (external modules)

---

## 🎨 Sidebar Positioning Guidelines

### Left Side (Content/Data Modules)
Use for modules that display content or data:
- ✅ Synergy Sessions
- ✅ InHouse Print Kanban
- ✅ Document Library
- ✅ Thread Manager

### Right Side (Actions/Settings Modules)
Use for modules with actions or configuration:
- ✅ Automation Workflows
- ✅ Settings
- ✅ Notifications
- ✅ Account Profile

---

## 🔧 Advanced Configuration

### Custom Width

```javascript
SidebarManager.register({
    id: 'wide-sidebar',
    width: '600px',  // Wider sidebar
    // ... other config
});
```

### Custom Z-Index

```javascript
SidebarManager.register({
    id: 'priority-sidebar',
    zIndex: 15000,  // Override auto-calculated z-index
    // ... other config
});
```

### Allow Multiple Sidebars Open

```javascript
SidebarManager.register({
    id: 'independent-sidebar',
    allowMultiple: true,  // Won't close other sidebars on same side
    // ... other config
});
```

---

## 🎯 Best Practices

### 1. Use Lazy Loading (onInit)

Load data only when the sidebar is first opened:

```javascript
onInit: async () => {
    // ✅ GOOD - Loads only on first open
    const data = await fetch('/api/my-module/data').then(r => r.json());
    renderData(data);
}
```

**Don't load data immediately in module scripts:**

```javascript
// ❌ BAD - Loads even if sidebar is never opened
const data = await fetch('/api/my-module/data').then(r => r.json());
```

### 2. Choose the Correct Side

- **Left:** Content, data, information displays
- **Right:** Actions, settings, configuration

### 3. Standard Widths

- **Compact:** 400px
- **Standard:** 450px (recommended)
- **Wide:** 500-600px

### 4. Descriptive IDs

Use clear, consistent naming:
- ✅ `kanban-sidebar`
- ✅ `communication-sidebar`
- ❌ `sidebar1`
- ❌ `my-sidebar`

### 5. Close Button

Always include a close button in the header:

```html
<button class="universal-sidebar-close" 
        onclick="SidebarManager.close('mymodule-sidebar')">
    <i class="fas fa-times"></i>
</button>
```

---

## 🐛 Troubleshooting

### Sidebar Doesn't Appear

**Check:**
1. Element IDs match registration config
2. Sidebar has `collapsed` class initially
3. Browser console for JavaScript errors
4. Framework CSS and JS files are loaded

**Debug:**
```javascript
// Check if sidebar is registered
console.log(SidebarManager.sidebars.has('mymodule-sidebar'));

// Check if elements exist
console.log(document.getElementById('mymodule-sidebar'));
console.log(document.getElementById('mymodule-sidebar-toggle'));
```

### Z-Index Conflicts

If your sidebar appears behind other elements:

```javascript
SidebarManager.register({
    id: 'mymodule-sidebar',
    zIndex: 25000,  // Set higher z-index
    // ... other config
});
```

### Toggle Button Not Draggable

The framework automatically makes buttons draggable. If it's not working:
1. Ensure `sidebar-manager.js` is loaded
2. Check browser console for errors
3. Verify button has correct class/attributes

---

## 🔗 Module System Integration Details

### How Auto-Registration Works

When you configure a sidebar in your module's `manifest.json`, this is what happens automatically:

```
1. ModuleLoader.initialize()
   ↓
2. Reads all manifest.json files
   ↓
3. Discovers modules with sidebar.enabled = true
   ↓
4. Creates floating toggle buttons (if floating_toggle = true)
   ↓
5. Calls registerModuleSidebarWithFramework()
   ↓
6. SidebarManager.register() called automatically
   ↓
7. Your sidebar is now managed by Universal Sidebar Framework!
```

### Module Manifest → Framework Config Mapping

| Manifest Property | Framework Config | Default |
|-------------------|------------------|---------|
| `sidebar.enabled` | (Required for auto-registration) | false |
| `sidebar.position` | `side` | "left" |
| `sidebar.width` | `width` | 450 |
| `icon` | `icon` | "fa-cube" |
| `name` | `title` | (module name) |
| `id` | `id` (as `{id}-sidebar`) | N/A |
| `floating_toggle` | Creates toggle button | false |

### Module Lifecycle with Sidebar Framework

```javascript
// 1. User clicks floating toggle button
User clicks "InHouse Kanban" toggle
↓
// 2. ModuleLoader.toggleModule() called
if (!loadedModules.has(moduleId)) {
    await loadModule(moduleId);  // Load HTML/CSS/JS
}
↓
// 3. Framework registration already done (at page load)
SidebarManager has module registered
↓
// 4. Framework handles toggle
SidebarManager.toggle('inhouse-kanban-sidebar')
↓
// 5. onInit callback fires (first time only)
Initialize module controller
Load initial data
↓
// 6. Sidebar slides in with animation
Transform: translateX(0)
↓
// 7. State persisted to localStorage
sidebar-state-inhouse-kanban-sidebar: "open"
```

### Module Controller Integration

Your module's JavaScript controller can be initialized automatically:

**In your module JS (e.g., `inhouse-kanban.js`):**
```javascript
class InhousekanbanController {
    constructor() {
        this.initialized = false;
    }
    
    async init() {
        if (this.initialized) return;
        
        console.log('[InHouse Kanban] Initializing...');
        
        // Load data, setup event listeners, etc.
        await this.loadJobs();
        
        this.initialized = true;
    }
    
    async loadJobs() {
        // Fetch data from backend
    }
}

// Create global instance
window.inhousekanbanController = new InhousekanbanController();
```

**Framework calls init() automatically:**
- First time sidebar opens: `onInit` callback runs
- `onInit` checks for `window.inhousekanbanController`
- Calls `init()` if method exists
- Sets `initialized = true` to prevent re-init

---

## 📚 Complete Documentation

For full API reference and advanced features, see:
- **[modules/sidebar-framework/SIDEBAR_FRAMEWORK_GUIDE.md](sidebar-framework/SIDEBAR_FRAMEWORK_GUIDE.md)** - Complete API guide
- **[modules/sidebar-framework/README.md](sidebar-framework/README.md)** - Framework overview
- **[external/modules/MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md](../external/modules/MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md)** - Module System docs
- **[external/modules/MODULE_SYSTEM_INTEGRATION_GUIDE.md](../external/modules/MODULE_SYSTEM_INTEGRATION_GUIDE.md)** - Integration guide

---

## ✅ Integration Checklist

### For Module System Modules (Recommended):

- [ ] Added `sidebar` config to `manifest.json`
- [ ] Set `sidebar.enabled: true`
- [ ] Set `sidebar.position` ("left" or "right")
- [ ] Set `sidebar.width` in pixels
- [ ] Set `floating_toggle: true` (for floating button)
- [ ] Created sidebar HTML file (e.g., `my-module-sidebar.html`)
- [ ] Added `universal-sidebar` class to sidebar container
- [ ] Set correct `id` (`{module-id}-sidebar`)
- [ ] Set `data-side` attribute matching position
- [ ] Added close button with `SidebarManager.close()`
- [ ] Created module controller with `init()` method
- [ ] Tested toggle functionality
- [ ] Verified z-index (no conflicts)
- [ ] Tested on different screen sizes
- [ ] Updated module documentation

### For Manual Registration (Core/Legacy):

- [ ] Created sidebar HTML in `business-ai-platform-v2.html`
- [ ] Created toggle button with correct `data-side`
- [ ] Added registration in `sidebar-init.js`
- [ ] Used `onInit` for lazy loading
- [ ] Added close button to header
- [ ] Tested toggle functionality
- [ ] Tested drag-and-drop for toggle button
- [ ] Verified z-index (no conflicts)
- [ ] Updated this document

---

## 🔗 Thread Card Integration (NEW - November 28, 2025)

In addition to sidebar integration, modules can now integrate with **thread info cards** to enable drag-and-drop linking and badge display.

### What is Thread Card Integration?

Thread cards are the single source of truth for thread linkages (Synergy sessions, workflows, automations, etc.). The **ThreadCardRegistry** enables any module to integrate with thread cards via manifest configuration.

### Benefits

✅ Users can drag your module items onto thread cards to link them  
✅ Thread cards automatically show badges when linked to your module  
✅ Real-time WebSocket updates refresh badges automatically  
✅ Zero changes to thread card code required (manifest-driven)  
✅ Integration takes ~5 minutes (vs 2-3 hours hardcoded)  

### Quick Integration

Add `thread_card_integration` to your `manifest.json`:

```json
{
  "id": "my-module",
  "name": "My Module",
  "sidebar": { ... },
  
  "thread_card_integration": {
    "enabled": true,
    
    "drag_and_drop": {
      "accepts": [{
        "data_type": "my-item",
        "mime_type": "application/x-my-item",
        "handler": "window.MyModule.linkToThread"
      }]
    },
    
    "badge": {
      "enabled": true,
      "condition": "thread.my_module_id !== null",
      "render_function": "window.MyModule.renderThreadBadge",
      "config": {
        "icon": "fa-my-icon",
        "color": "#10b981",
        "label": "My Module",
        "priority": 5
      }
    },
    
    "realtime_events": {
      "enabled": true,
      "events": ["thread_linked_to_my_module"],
      "handler": "window.MyModule.handleRealtimeUpdate"
    }
  }
}
```

Implement 3 handler functions:

```javascript
window.MyModule = {
    // Called when user drops your item on thread card
    async linkToThread(itemDataJson, threadId, location) {
        const itemData = JSON.parse(itemDataJson);
        await fetch('/api/my-module/link-to-thread', {
            method: 'POST',
            body: JSON.stringify({item_id: itemData.id, thread_id: threadId})
        });
        window.ThreadManager.refreshThreadCard(threadId);
    },
    
    // Generates HTML for badge on thread card
    renderThreadBadge(thread, config) {
        if (!thread.my_module_id) return '';
        return `<div class="badge" style="background: ${config.color}">
            <i class="fas ${config.icon}"></i> ${thread.my_module_title}
        </div>`;
    },
    
    // Called when WebSocket event received
    async handleRealtimeUpdate(eventData) {
        window.ThreadManager.refreshThreadCard(eventData.thread_id);
    }
};
```

**That's it!** Your module now integrates with thread cards.

### Complete Documentation

For detailed instructions, see:
- **`THREAD_CARD_INTEGRATION_GUIDE.md`** - Step-by-step developer guide (600+ lines)
- **`THREAD_CARD_MODULE_REGISTRY_ARCHITECTURE.md`** - Technical architecture
- **`MANIFEST_SCHEMA_THREAD_CARD_EXTENSION.md`** - Complete schema specification
- **`MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md`** - Section on thread card integration

### Real-World Example

**Synergy Module:**
- Files: `UI/external/modules/synergy/manifest.json`, `synergy-thread-integration.js`
- Features: Drag sessions to threads, green badge display, real-time updates
- Integration time: 5 minutes

---

**Last Updated:** November 28, 2025  
**Maintainer:** AI Agents Platform Team  
**Version:** 1.1.0 (Added Thread Card Integration)
