# Universal Sidebar System - Complete Documentation

**Created:** November 29, 2025  
**Status:** ✅ Production Ready  
**Version:** 2.0.0

---

## 📋 Table of Contents

1. [Overview & Architecture](#overview--architecture)
2. [Positioning System (60px Offset)](#positioning-system-60px-offset)
3. [Floating Toggle Buttons](#floating-toggle-buttons)
4. [Module System Integration](#module-system-integration)
5. [Sidebar Loading & Lifecycle](#sidebar-loading--lifecycle)
6. [Developer Guide](#developer-guide)
7. [Visual Reference](#visual-reference)
8. [Troubleshooting](#troubleshooting)

---

## Overview & Architecture

### System Purpose

The **Universal Sidebar Framework** provides a consistent, performant sidebar experience across the entire AI Agents Platform. All sidebars (core and module-based) use this unified system for:

- ✅ **Consistent positioning** - 60px offset from screen edges
- ✅ **Smooth animations** - Transform-based slide in/out
- ✅ **Z-index management** - Automatic layering, no conflicts
- ✅ **State persistence** - Remember open/closed state
- ✅ **Draggable toggles** - Users can reposition floating buttons
- ✅ **Module auto-registration** - Manifest-driven integration
- ✅ **Lazy loading** - Initialize only when first opened

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│         Universal Sidebar Framework                      │
│  (modules/sidebar-framework/sidebar-manager.js)          │
└──────────────────┬──────────────────────────────────────┘
                   │
      ┌────────────┼────────────┐
      │                         │
      ↓                         ↓
┌──────────────┐       ┌────────────────┐
│ Module System│       │ Manual Registry │
│ (manifest)   │       │ (sidebar-init)  │
└──────────────┘       └────────────────┘
      │                         │
      ↓                         ↓
┌─────────────────────────────────────────┐
│    Registered Sidebars (4 Active)       │
│  - Synergy (left, 480px, manual)        │
│  - Automations (right, 480px, manual)   │
│  - Account (right, 450px, manual)       │
│  - InHouse Kanban (left, 480px, module) │
└─────────────────────────────────────────┘
```

### File Structure

```
UI/
├── modules/
│   ├── sidebar-framework/
│   │   ├── sidebar-manager.js         ← Core framework
│   │   ├── sidebar-styles.css         ← Base styles
│   │   ├── sidebar-init.js            ← Manual registrations
│   │   └── SIDEBAR_FRAMEWORK_GUIDE.md
│   │
│   └── module_loader.js               ← Auto-registers module sidebars
│
└── external/modules/
    └── [module-name]/
        ├── manifest.json              ← Sidebar config here
        ├── [module]-sidebar.html      ← Sidebar template
        └── [module].js                ← Module controller
```

---

## Positioning System (60px Offset)

### Why 60px Offset?

The platform has **60px fixed UI elements** that sidebars must clear:

```
┌────────────────────────────────────────────────────┐
│         60px Header Bar (z-index: 11000)           │
├────┬──────────────────────────────────────────┬───┤
│    │                                          │   │
│ 6  │                                          │ 6 │
│ 0  │           Main Content Area             │ 0 │
│ p  │                                          │ p │
│ x  │                                          │ x │
│    │                                          │   │
│ L  │  Sidebars appear at 60px offset         │ R │
│ e  │                                          │ i │
│ f  │  Left: Synergy, Kanban                  │ g │
│ t  │  Right: Automations, Account, Debug     │ h │
│    │                                          │ t │
│ B  │                                          │   │
│ u  │                                          │ B │
│ t  │                                          │ u │
│ t  │                                          │ t │
│ o  │                                          │ t │
│ n  │                                          │ o │
│ s  │                                          │ n │
│    │                                          │ s │
└────┴──────────────────────────────────────────┴───┘
```

**Problem (before fix):**
- Sidebars at `left: 0` or `right: 0` overlapped button bars
- Users couldn't access main sidebar buttons when sidebar was open
- Inconsistent positioning across different modules

**Solution:**
- All sidebars positioned at 60px from edges
- Clear visual separation from main UI
- Consistent, professional appearance

### CSS Implementation

#### Left-Side Sidebar Pattern

```css
.my-sidebar {
    position: fixed;
    top: 60px;                    /* Below header */
    left: 60px;                   /* Right of button bar */
    height: calc(100vh - 60px);   /* Full height minus header */
    width: 480px;
    
    background: var(--bg-primary);
    border-right: 1px solid var(--border-default);
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3);
    
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 9999;
}

/* Hidden state (collapsed) */
.my-sidebar.collapsed {
    transform: translateX(calc(-100% - 60px));  /* Slide off-screen LEFT beyond the 60px offset */
}

/* Visible state (open) */
.my-sidebar:not(.collapsed) {
    transform: translateX(0);  /* Slide to visible position at 60px from left */
}
```

**Why `calc(-100% - 60px)`?**
- Sidebar is positioned at `left: 60px`
- To hide it, we need to move it `-100%` (its full width) PLUS the 60px offset
- Result: Sidebar slides completely off-screen to the left

#### Right-Side Sidebar Pattern

```css
.my-sidebar {
    position: fixed;
    top: 60px;                    /* Below header */
    right: 60px;                  /* Left of button bar */
    height: calc(100vh - 60px);   /* Full height minus header */
    width: 480px;
    
    background: var(--bg-primary);
    border-left: 1px solid var(--border-default);  /* ← Border on LEFT for right-side */
    box-shadow: -4px 0 24px rgba(0, 0, 0, 0.3);    /* ← Shadow on LEFT for right-side */
    
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 9999;
}

/* Hidden state (collapsed) */
.my-sidebar.collapsed {
    transform: translateX(calc(100% + 60px));  /* Slide off-screen RIGHT beyond the 60px offset */
}

/* Visible state (open) */
.my-sidebar:not(.collapsed) {
    transform: translateX(0);  /* Slide to visible position at 60px from right */
}
```

**Why `calc(100% + 60px)`?**
- Sidebar is positioned at `right: 60px`
- To hide it, we need to move it `+100%` (its full width) PLUS the 60px offset
- Result: Sidebar slides completely off-screen to the right

### HTML Structure

```html
<!-- LEFT-SIDE SIDEBAR -->
<div class="universal-sidebar collapsed" 
     id="my-sidebar" 
     data-side="left">
    
    <div class="universal-sidebar-header">
        <div class="universal-sidebar-title">
            <span><i class="fas fa-cube"></i> My Module</span>
            <button class="universal-sidebar-close" 
                    onclick="SidebarManager.close('my-sidebar')">
                <i class="fas fa-times"></i>
            </button>
        </div>
    </div>

    <div class="universal-sidebar-content">
        <!-- Content goes here -->
    </div>
</div>
```

**Required attributes:**
- `class="universal-sidebar collapsed"` - Framework styles + hidden by default
- `id="my-sidebar"` - Unique identifier for registration
- `data-side="left|right"` - Positioning side

### Animation Timing

```css
transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
```

**Breakdown:**
- **Property:** `transform` (GPU-accelerated, smooth)
- **Duration:** `0.3s` (300ms - feels responsive)
- **Easing:** `cubic-bezier(0.4, 0, 0.2, 1)` (ease-in-out with subtle acceleration)

**Why not animate `left/right`?**
- Transform is GPU-accelerated (smoother, better performance)
- Animating position properties triggers layout recalculations (janky)
- Transform only triggers compositing (much faster)

---

## Floating Toggle Buttons

### Purpose

Floating toggle buttons provide quick access to sidebars from anywhere on the screen. Users can:
- Click to open/close sidebar
- Drag to reposition (position saved to localStorage)
- Move between left/right sides (sidebar follows)

### Visual Design

**Style Evolution (November 2025):**

**Before:**
```
█  Rectangle (36px × 64px)
█  Solid color background
█  Flush against edge (0px)
```

**After:**
```
╔═══╗  Circle (48px × 48px)
║ ● ║  Border + secondary background
╚═══╝  80px from edge (60px sidebar + 20px spacing)
       Blue border on hover
       Blue glow when active
```

### CSS Implementation

```css
.module-floating-toggle {
    position: fixed;
    width: 48px;
    height: 48px;
    border-radius: 50%;                        /* Circular */
    
    background: var(--bg-secondary);
    border: 2px solid var(--border-default);
    color: var(--text-secondary);
    
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    
    cursor: move;                              /* Draggable indicator */
    user-select: none;
    z-index: 10000;
    
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
    transition: all 0.2s ease;
}

/* Hover state */
.module-floating-toggle:hover {
    background: var(--bg-tertiary);
    border-color: var(--accent-primary);       /* Blue border */
    color: var(--accent-primary);              /* Blue icon */
    transform: scale(1.05);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

/* Active state (sidebar open) */
.module-floating-toggle.active {
    background: var(--accent-primary);         /* Blue background */
    border-color: var(--accent-primary);
    color: white;
    box-shadow: 0 0 20px rgba(79, 108, 255, 0.4);  /* Blue glow */
}

/* Dragging state */
.module-floating-toggle.dragging {
    opacity: 0.7;
    transform: scale(1.1);
    cursor: grabbing;
}
```

### Positioning Logic

```javascript
function positionToggle(side, moduleId) {
    const toggle = document.getElementById(`${moduleId}-floating-toggle`);
    
    // Vertical position (saved per toggle)
    const savedY = localStorage.getItem(`${moduleId}-toggle-y`) || '200';
    toggle.style.top = savedY + 'px';
    
    // Horizontal position (based on side)
    if (side === 'left') {
        toggle.style.left = '80px';   // 60px sidebar + 20px spacing
        toggle.style.right = 'auto';
    } else {
        toggle.style.right = '80px';  // 60px sidebar + 20px spacing
        toggle.style.left = 'auto';
    }
    
    // Update sidebar positioning to match
    updateSidebarPosition(moduleId, side);
}
```

### Dynamic Side Detection

**Feature:** When user drags toggle across the screen, sidebar side automatically switches.

```javascript
// Mouse up handler after drag
function handleDragEnd(event, toggle, moduleId) {
    const windowWidth = window.innerWidth;
    const toggleRect = toggle.getBoundingClientRect();
    const toggleCenterX = toggleRect.left + (toggleRect.width / 2);
    
    // Detect which half of screen toggle is in
    const newSide = toggleCenterX < (windowWidth / 2) ? 'left' : 'right';
    const oldSide = localStorage.getItem(`${moduleId}-toggle-side`) || 'left';
    
    if (newSide !== oldSide) {
        console.log(`[Toggle] Switched from ${oldSide} to ${newSide}`);
        
        // Save new side
        localStorage.setItem(`${moduleId}-toggle-side`, newSide);
        
        // Reposition toggle and sidebar
        positionToggle(newSide, moduleId);
        
        // Update SidebarManager if registered
        if (window.SidebarManager && window.SidebarManager.sidebars.has(`${moduleId}-sidebar`)) {
            const sidebarConfig = window.SidebarManager.sidebars.get(`${moduleId}-sidebar`);
            sidebarConfig.side = newSide;
            window.SidebarManager.applySidebarStyles(sidebarConfig.element, sidebarConfig);
        }
    }
}
```

**User Experience:**
1. User drags Kanban toggle from left side to right side
2. Toggle crosses center line → System detects side change
3. Toggle snaps to right side (80px from right edge)
4. Kanban sidebar reconfigures to open from right
5. Preference saved → Next session remembers right-side position

### Drag and Drop Implementation

```javascript
let isDragging = false;
let dragOffsetY = 0;

toggle.addEventListener('mousedown', (e) => {
    isDragging = true;
    dragOffsetY = e.clientY - toggle.getBoundingClientRect().top;
    toggle.classList.add('dragging');
});

document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    
    // Calculate new position (constrained to viewport)
    const newY = e.clientY - dragOffsetY;
    const maxY = window.innerHeight - toggle.offsetHeight - 20;
    const clampedY = Math.max(80, Math.min(newY, maxY));  // Min 80px (below header)
    
    toggle.style.top = clampedY + 'px';
});

document.addEventListener('mouseup', (e) => {
    if (!isDragging) return;
    
    isDragging = false;
    toggle.classList.remove('dragging');
    
    // Save position
    const finalY = parseInt(toggle.style.top);
    localStorage.setItem(`${moduleId}-toggle-y`, finalY);
    
    // Check if side changed
    handleDragEnd(e, toggle, moduleId);
});
```

---

## Module System Integration

### Automatic Registration

Modules with sidebars are **automatically registered** via their `manifest.json` configuration.

### Manifest Configuration

```json
{
  "id": "my-module",
  "name": "My Module",
  "version": "1.0.0",
  "icon": "fas fa-cube",
  "color": "#6366f1",
  
  "floating_toggle": true,              // ← Enable floating toggle button
  
  "sidebar": {
    "enabled": true,                    // ← Enable sidebar
    "position": "left",                 // ← "left" or "right"
    "width": 480,                       // ← Width in pixels
    "html_file": "my-module-sidebar.html"  // ← HTML template
  },
  
  "js_file": "my-module.js",            // ← Module controller
  "css_file": "my-module.css"
}
```

### Registration Flow

```
1. PAGE LOAD
   ↓
2. ModuleLoader.initialize()
   ↓
3. Fetch all module manifests from /api/modules/list
   ↓
4. For each module with sidebar.enabled:
   ├─ Create floating toggle button (if floating_toggle: true)
   ├─ Position at 80px from saved side
   ├─ Make draggable
   └─ Call registerModuleSidebarWithFramework()
      ↓
5. SidebarManager.register({
      id: 'my-module-sidebar',
      side: 'left',
      width: '480px',
      toggleButtonId: 'my-module-floating-toggle',
      onInit: async () => { ... }
   })
   ↓
6. REGISTERED ✅
   User can now click toggle → sidebar opens
```

### ModuleLoader Integration Code

```javascript
// In module_loader.js

generateFloatingToggles() {
    for (const [moduleId, module] of this.modules) {
        if (!module.available || !module.floating_toggle) continue;
        
        // Create toggle button
        const toggle = document.createElement('button');
        toggle.id = `${moduleId}-floating-toggle`;
        toggle.className = 'module-floating-toggle';
        toggle.innerHTML = `<i class="${module.icon}"></i>`;
        toggle.title = module.name;
        
        // Position based on saved preference
        const savedSide = localStorage.getItem(`${moduleId}-toggle-side`) || 
                          module.sidebar?.position || 'left';
        this.positionFloatingToggle(toggle, savedSide, moduleId);
        
        // Make draggable
        this.makeToggleDraggable(toggle, moduleId);
        
        // Click handler
        toggle.addEventListener('click', () => {
            this.toggleModule(moduleId);
        });
        
        document.body.appendChild(toggle);
        
        // Auto-register if sidebar enabled
        if (module.sidebar && module.sidebar.enabled) {
            this.registerModuleSidebarWithFramework(moduleId, module);
        }
    }
}

registerModuleSidebarWithFramework(moduleId, module) {
    const config = {
        id: `${moduleId}-sidebar`,
        side: module.sidebar.position || 'left',
        width: `${module.sidebar.width || 450}px`,
        toggleButtonId: `${moduleId}-floating-toggle`,
        icon: module.icon,
        title: module.name,
        zIndex: 9999,
        
        onInit: async () => {
            // Initialize module controller on first open
            const controllerName = `${moduleId.replace(/-/g, '')}Controller`;
            if (window[controllerName] && typeof window[controllerName].init === 'function') {
                await window[controllerName].init();
            }
        }
    };
    
    window.SidebarManager.register(config);
    console.log(`[ModuleLoader] ✅ Registered ${moduleId} with Universal Sidebar Framework`);
}
```

---

## Sidebar Loading & Lifecycle

### Lazy Loading Strategy

Sidebars use **lazy loading** - they don't initialize until first opened. This reduces:
- Initial page load time
- Memory usage
- API calls

### Lifecycle Phases

```
Phase 1: PAGE LOAD
├─ SidebarManager initialized
├─ Manifest configurations read
├─ Sidebar elements exist in DOM (hidden)
└─ NO DATA LOADED YET ✅

Phase 2: FIRST OPEN (User clicks toggle)
├─ SidebarManager.toggle('my-sidebar') called
├─ Check if initialized: No
├─ Call onInit callback
│  ├─ Load module controller
│  ├─ Fetch initial data from API
│  ├─ Render initial UI
│  └─ Set initialized = true
├─ Slide sidebar in (transform: translateX(0))
└─ Save state: localStorage['sidebar-state-my-sidebar'] = 'open'

Phase 3: SUBSEQUENT OPENS
├─ SidebarManager.toggle('my-sidebar') called
├─ Check if initialized: Yes
├─ SKIP onInit (already initialized) ✅
├─ Slide sidebar in
└─ Save state

Phase 4: CLOSE
├─ SidebarManager.close('my-sidebar') called
├─ Slide sidebar out (transform: translateX(calc(-100% - 60px)))
└─ Save state: localStorage['sidebar-state-my-sidebar'] = 'closed'

Phase 5: REFRESH/RELOAD
├─ Check localStorage for saved state
├─ If state = 'open': Open sidebar on load
└─ If state = 'closed': Keep sidebar hidden (default)
```

### Module Controller Pattern

```javascript
// my-module.js

class MyModuleController {
    constructor() {
        this.initialized = false;
        this.data = [];
    }
    
    async init() {
        // Prevent double initialization
        if (this.initialized) {
            console.log('[MyModule] Already initialized, skipping...');
            return;
        }
        
        console.log('[MyModule] Initializing...');
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load data from API
        await this.loadData();
        
        // Render initial UI
        this.render();
        
        // Mark as initialized
        this.initialized = true;
        
        console.log('[MyModule] ✅ Initialization complete');
    }
    
    setupEventListeners() {
        // Setup once, never again
        document.getElementById('my-button').addEventListener('click', () => {
            this.handleButtonClick();
        });
    }
    
    async loadData() {
        try {
            const response = await fetch('/api/my-module/data');
            this.data = await response.json();
        } catch (error) {
            console.error('[MyModule] Failed to load data:', error);
            this.data = [];
        }
    }
    
    render() {
        const container = document.getElementById('my-module-content');
        container.innerHTML = this.data.map(item => `
            <div class="item">${item.name}</div>
        `).join('');
    }
    
    // Public method for refreshing data
    async refresh() {
        await this.loadData();
        this.render();
    }
}

// Create global instance
window.mymoduleController = new MyModuleController();
```

### SidebarManager onInit Callback

```javascript
SidebarManager.register({
    id: 'my-module-sidebar',
    side: 'left',
    toggleButtonId: 'my-module-toggle',
    
    onInit: async () => {
        console.log('[SidebarManager] First open - calling module init...');
        
        // Find controller by naming convention
        const controllerName = 'mymoduleController';
        
        if (window[controllerName]) {
            if (typeof window[controllerName].init === 'function') {
                await window[controllerName].init();
            }
        } else {
            console.warn(`[SidebarManager] Controller ${controllerName} not found`);
        }
    },
    
    onOpen: () => {
        // Called every time sidebar opens (after init)
        console.log('[SidebarManager] Sidebar opened');
    },
    
    onClose: () => {
        // Called every time sidebar closes
        console.log('[SidebarManager] Sidebar closed');
    }
});
```

---

## Developer Guide

### Adding a New Sidebar (Module System)

**Step 1: Create module folder**
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

**Step 3: Create sidebar HTML (analytics-sidebar.html)**
```html
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

    <div class="universal-sidebar-content" id="analytics-content">
        <div class="loading">Loading analytics...</div>
    </div>
</div>
```

**Step 4: Create controller (analytics.js)**
```javascript
class AnalyticsController {
    constructor() {
        this.initialized = false;
        this.charts = [];
    }
    
    async init() {
        if (this.initialized) return;
        
        console.log('[Analytics] Initializing...');
        
        await this.loadChartData();
        this.renderCharts();
        
        this.initialized = true;
        console.log('[Analytics] ✅ Ready');
    }
    
    async loadChartData() {
        const response = await fetch('/api/analytics/charts');
        this.charts = await response.json();
    }
    
    renderCharts() {
        const container = document.getElementById('analytics-content');
        // Render charts...
    }
}

window.analyticsController = new AnalyticsController();
```

**Step 5: Reload page**
- Module automatically discovered ✅
- Floating toggle created ✅
- Sidebar registered ✅
- Click toggle → sidebar opens ✅

**Total time:** 10-15 minutes

### Adding a Manual Sidebar (Core Platform)

For core platform sidebars not part of the Module System:

**Step 1: Add HTML to business-ai-platform-v2.html**
```html
<div class="universal-sidebar collapsed" 
     id="notifications-sidebar" 
     data-side="right">
    <!-- sidebar content -->
</div>
```

**Step 2: Create toggle button**
```html
<button class="sidebar-toggle-btn" 
        id="notifications-toggle" 
        data-side="right">
    <i class="fas fa-bell"></i>
</button>
```

**Step 3: Register in sidebar-init.js**
```javascript
SidebarManager.register({
    id: 'notifications-sidebar',
    side: 'right',
    toggleButtonId: 'notifications-toggle',
    width: '400px',
    icon: 'fa-bell',
    title: 'Notifications',
    zIndex: 10500,
    
    onInit: async () => {
        await window.NotificationsController.init();
    }
});
```

---

## Visual Reference

### Screen Layout

```
┌──────────────────────────────────────────────────────────────┐
│                    60px Header Bar                           │
│            (Logo, Title, User Menu, etc.)                    │
└──────────────────────────────────────────────────────────────┘
┌─────┬────────────────────────────────────────────────┬──────┐
│     │                                                │      │
│  6  │                                                │  6   │
│  0  │                                                │  0   │
│  p  │                                                │  p   │
│  x  │                                                │  x   │
│     │                                                │      │
│  L  │            Main Content Area                  │  R   │
│  e  │                                                │  i   │
│  f  │                                                │  g   │
│  t  │  ╔════════════════╗                           │  h   │
│     │  ║                ║  ← Left sidebar           │  t   │
│  B  │  ║  SYNERGY       ║     at 60px offset        │      │
│  u  │  ║  SIDEBAR       ║                           │  B   │
│  t  │  ║  (480px wide)  ║                           │  u   │
│  t  │  ║                ║                           │  t   │
│  o  │  ║                ║                           │  t   │
│  n  │  ║                ║                           │  o   │
│  s  │  ╚════════════════╝                           │  n   │
│     │                                                │  s   │
│     │                        ╔═══════════════════╗  │      │
│     │                        ║                   ║  │      │
│     │  Right sidebar →       ║  AUTOMATIONS      ║  │      │
│     │  at 60px offset        ║  SIDEBAR          ║  │      │
│     │                        ║  (480px wide)     ║  │      │
│     │                        ║                   ║  │      │
│     │                        ║                   ║  │      │
│     │                        ╚═══════════════════╝  │      │
│     │                                                │      │
└─────┴────────────────────────────────────────────────┴──────┘

Floating Toggles:
Left side:  80px from left (60px buttons + 20px spacing)
Right side: 80px from right (60px buttons + 20px spacing)
```

### Transform Animation States

**LEFT-SIDE SIDEBAR:**

```
HIDDEN:
┌─────┬────────────────────────────────────┐
│ 60px│                                    │
│     │ [Sidebar is off-screen LEFT]      │
│     │                                    │
└─────┴────────────────────────────────────┘
Position: left: 60px
Transform: translateX(calc(-100% - 60px))

OPENING:
┌─────┬────────────────────────────────────┐
│ 60px│ ╔══╗                               │
│     │ ║  ║ [Sliding in from left]        │
│     │ ╚══╝                               │
└─────┴────────────────────────────────────┘
Position: left: 60px
Transform: translateX(-50%) ← mid-animation

OPEN:
┌─────┬────────────────────────────────────┐
│ 60px│ ╔═════════╗                        │
│     │ ║ SIDEBAR ║                        │
│     │ ╚═════════╝                        │
└─────┴────────────────────────────────────┘
Position: left: 60px
Transform: translateX(0)
```

**RIGHT-SIDE SIDEBAR:**

```
HIDDEN:
┌────────────────────────────────────┬─────┐
│                                    │ 60px│
│      [Sidebar is off-screen RIGHT]│     │
│                                    │     │
└────────────────────────────────────┴─────┘
Position: right: 60px
Transform: translateX(calc(100% + 60px))

OPENING:
┌────────────────────────────────────┬─────┐
│                               ╔══╗ │ 60px│
│        [Sliding in from right]║  ║ │     │
│                               ╚══╝ │     │
└────────────────────────────────────┴─────┘
Position: right: 60px
Transform: translateX(50%) ← mid-animation

OPEN:
┌────────────────────────────────────┬─────┐
│                        ╔═════════╗ │ 60px│
│                        ║ SIDEBAR ║ │     │
│                        ╚═════════╝ │     │
└────────────────────────────────────┴─────┘
Position: right: 60px
Transform: translateX(0)
```

### Toggle Button States

```
DEFAULT STATE:
╔═══╗
║ ● ║  Gray background, gray border
╚═══╝  Icon: gray

HOVER STATE:
╔═══╗
║ ● ║  Lighter background, BLUE border
╚═══╝  Icon: BLUE, slightly larger (scale: 1.05)

ACTIVE STATE (Sidebar open):
╔═══╗
║ ● ║  BLUE background, white icon
╚═══╝  Blue glow effect around button

DRAGGING STATE:
╔═══╗
║ ● ║  70% opacity, larger (scale: 1.1)
╚═══╝  Cursor: grabbing
```

---

## Troubleshooting

### Sidebar Doesn't Appear

**Symptom:** Click toggle, sidebar doesn't slide in

**Debugging steps:**

1. **Check if sidebar is registered**
```javascript
console.log(SidebarManager.sidebars.has('my-sidebar'));
// Should return: true
```

2. **Check if element exists**
```javascript
console.log(document.getElementById('my-sidebar'));
// Should return: <div> element
```

3. **Check initial classes**
```javascript
const sidebar = document.getElementById('my-sidebar');
console.log(sidebar.classList.contains('collapsed'));
// Should return: true (initially hidden)
```

4. **Check console for errors**
- Look for JavaScript errors during registration
- Check if sidebar-manager.js loaded

5. **Verify HTML structure**
- Ensure `id` matches registration config
- Ensure `data-side` attribute present
- Ensure `collapsed` class on initial state

### Toggle Button Not Draggable

**Symptom:** Can't drag floating toggle button

**Fixes:**

1. **Check if sidebar-manager.js loaded**
```javascript
console.log(typeof SidebarManager);
// Should return: "object" or "function"
```

2. **Check cursor style**
```css
.module-floating-toggle {
    cursor: move;  /* Should be "move" not "pointer" */
}
```

3. **Check event listeners**
```javascript
const toggle = document.getElementById('my-toggle');
console.log(getEventListeners(toggle));
// Should show: mousedown, mousemove, mouseup
```

### Sidebar Overlaps Button Bar

**Symptom:** Sidebar covers 60px button sidebar

**Fix:**

Check positioning:
```css
.my-sidebar {
    left: 60px;   /* NOT left: 0 */
    /* or */
    right: 60px;  /* NOT right: 0 */
}
```

Check transform hidden state:
```css
.my-sidebar.collapsed {
    transform: translateX(calc(-100% - 60px));  /* NOT translateX(-100%) */
}
```

### Z-Index Conflicts

**Symptom:** Sidebar appears behind other elements

**Solution:**

Manually set z-index in registration:
```javascript
SidebarManager.register({
    id: 'my-sidebar',
    zIndex: 11000,  // Higher than other sidebars
    // ...
});
```

**Z-Index hierarchy (current):**
- Header: 11000
- Account sidebar: 10000
- Automations sidebar: 9999
- Synergy sidebar: 9999
- Debug sidebar: 9000

### State Not Persisting

**Symptom:** Sidebar state doesn't remember open/closed on refresh

**Check localStorage:**
```javascript
console.log(localStorage.getItem('sidebar-state-my-sidebar'));
// Should return: "open" or "closed"
```

**Clear state and reset:**
```javascript
localStorage.removeItem('sidebar-state-my-sidebar');
localStorage.removeItem('my-module-toggle-side');
localStorage.removeItem('my-module-toggle-y');
// Refresh page
```

### Module Controller Not Initializing

**Symptom:** onInit callback doesn't call controller.init()

**Debugging:**

1. **Check controller exists**
```javascript
console.log(window.mymoduleController);
// Should return: Object with init method
```

2. **Check naming convention**
```
Module ID: "my-module"
Controller name: "mymoduleController"  ← No hyphens!
```

3. **Check init method exists**
```javascript
console.log(typeof window.mymoduleController.init);
// Should return: "function"
```

4. **Manually test**
```javascript
await window.mymoduleController.init();
// Check console for initialization logs
```

---

## Current Sidebars in Platform

| Sidebar | ID | Side | Width | Z-Index | Toggle Type | Status |
|---------|-----|------|-------|---------|-------------|--------|
| **Synergy** | `synergy-sidebar` | Left | 480px | 9999 | Top-left floating | ✅ Active |
| **Automations** | `automations-sidebar` | Right | 480px | 9999 | Top-right floating | ✅ Active |
| **Account** | `account-sidebar` | Right | 450px | 10000 | User profile button | ✅ Active |
| **Debug** | `debug-sidebar` | Right | 600px | 9000 | Debug button | ✅ Active |
| **InHouse Kanban** | `inhouse-kanban-sidebar` | Left | 480px | 9999 | Module floating toggle | ✅ Active |
| **Vector Database** | `vector-db-sidebar` | Right | 450px | 9999 | Module floating toggle | ✅ Active |

---

## Real-World Example: Vector Database Sidebar

### Implementation (November 28, 2025)

The Vector Database module demonstrates the complete 60px offset pattern for right-side sidebars.

**CSS Implementation (UI/modules/vector_database/vector_database.css):**

```css
.vector-db-sidebar {
    position: fixed;
    top: 60px;                          /* ✅ 60px below header */
    right: 60px;                        /* ✅ 60px from right edge */
    height: calc(100vh - 60px);         /* ✅ Full height minus header */
    width: 450px;
    
    background: var(--bg-primary);
    border-left: 1px solid var(--border-default);
    box-shadow: -4px 0 24px rgba(0, 0, 0, 0.3);
    
    display: flex;
    flex-direction: column;
    overflow: hidden;
    z-index: 9999;
    
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease;
}

/* Hidden state (default) */
.vector-db-sidebar.collapsed {
    transform: translateX(calc(100% + 60px));  /* ✅ Hide beyond 60px offset */
    box-shadow: none;
}

/* Visible state (when open) */
.vector-db-sidebar:not(.collapsed) {
    transform: translateX(0);  /* ✅ Slide to 60px from right edge */
    box-shadow: -4px 0 24px rgba(0, 0, 0, 0.3);
}

/* Optional: Right-side variant (if module supports left-side positioning) */
.vector-db-sidebar.right-side {
    right: 60px;
    left: auto;
    border-left: 1px solid var(--border-default);
    border-right: none;
    box-shadow: -4px 0 24px rgba(0, 0, 0, 0.3);
}

.vector-db-sidebar.right-side.collapsed {
    transform: translateX(calc(100% + 60px));
}
```

**Key Features:**
- ✅ **60px offset** - Clears right-side button bar
- ✅ **Transform-based animation** - Smooth GPU-accelerated slide
- ✅ **Proper hide calculation** - `calc(100% + 60px)` accounts for positioning offset
- ✅ **Conditional shadow** - Only visible when open
- ✅ **Full height** - `calc(100vh - 60px)` fills space below header

**HTML Structure:**
```html
<div class="vector-db-sidebar collapsed" id="vector-db-sidebar" data-side="right">
    <div class="vector-db-sidebar-header">
        <!-- Header content -->
    </div>
    <div class="vector-db-sidebar-content">
        <!-- Main content -->
    </div>
</div>
```

**Benefits of This Pattern:**
- Users can access right-side buttons even when sidebar is open
- Consistent with all other platform sidebars
- Professional appearance with proper spacing
- Smooth animations without jank

---

## Related Documentation

- **[modules/sidebar-framework/SIDEBAR_FRAMEWORK_GUIDE.md](sidebar-framework/SIDEBAR_FRAMEWORK_GUIDE.md)** - Complete API reference
- **[modules/sidebar-framework/README.md](sidebar-framework/README.md)** - Framework overview
- **[external/modules/MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md](../external/modules/MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md)** - Module System docs

---

**Last Updated:** November 29, 2025  
**Version:** 2.0.0  
**Status:** ✅ Production Ready  
**Maintainer:** AI Agents Platform Team
