# Universal Sidebar Framework - Complete Guide

**Created:** November 28, 2025  
**Purpose:** Centralized system for managing all module sidebars with consistent behavior

---

## 📋 Overview

The Universal Sidebar Framework provides a consistent, reusable system for creating module sidebars with:

- ✅ **Automatic positioning** (left or right based on toggle button location)
- ✅ **Consistent animations** (slide in/out with transform)
- ✅ **Draggable toggle buttons** (users can reposition them)
- ✅ **Z-index management** (no conflicts between multiple sidebars)
- ✅ **State persistence** (remembers which sidebars are open)
- ✅ **Lazy initialization** (sidebars load data only when first opened)
- ✅ **Standard styling** (all sidebars look consistent)

---

## 🚀 Quick Start

### 1. Load the Framework

Add to your HTML (in `<head>` or before `</body>`):

```html
<!-- Sidebar Framework -->
<link rel="stylesheet" href="modules/sidebar-framework/sidebar-manager.css">
<script src="modules/sidebar-framework/sidebar-manager.js"></script>
```

### 2. Create Your Sidebar HTML

```html
<!-- Toggle Button (floating, draggable) -->
<button class="sidebar-toggle-btn" 
        id="mymodule-sidebar-toggle" 
        data-side="left"
        title="My Module">
    <i class="fas fa-cube"></i>
</button>

<!-- Sidebar Container -->
<div class="universal-sidebar collapsed" 
     id="mymodule-sidebar" 
     data-side="left">
    
    <div class="universal-sidebar-header">
        <div class="universal-sidebar-title">
            <span><i class="fas fa-cube"></i> My Module</span>
            <button class="universal-sidebar-close" 
                    onclick="SidebarManager.close('mymodule-sidebar')">
                <i class="fas fa-times"></i>
            </button>
        </div>
    </div>

    <div class="universal-sidebar-content" id="mymodule-content">
        <!-- Your module content goes here -->
    </div>

    <div class="universal-sidebar-footer">
        <!-- Optional footer actions -->
    </div>
</div>
```

### 3. Register Your Sidebar (JavaScript)

```javascript
// Register when page loads
document.addEventListener('DOMContentLoaded', () => {
    SidebarManager.register({
        id: 'mymodule-sidebar',
        side: 'left',
        toggleButtonId: 'mymodule-sidebar-toggle',
        width: '450px',
        icon: 'fa-cube',
        title: 'My Module',
        
        // Optional: Load data when first opened
        onInit: async () => {
            console.log('Loading module data...');
            const data = await fetch('/api/mymodule/data').then(r => r.json());
            renderModuleData(data);
        },
        
        // Optional: Callbacks
        onOpen: () => {
            console.log('Sidebar opened');
        },
        
        onClose: () => {
            console.log('Sidebar closed');
        }
    });
});
```

### 4. Done! Your sidebar now has:
- ✅ Consistent slide-in/out animation
- ✅ Draggable toggle button (users can move it)
- ✅ Proper z-index management
- ✅ State persistence (reopens on page refresh)
- ✅ Lazy loading (onInit runs only once)

---

## 📖 Complete API Reference

### SidebarManager.register(config)

Register a new sidebar with the framework.

**Parameters:**

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `id` | string | ✅ Yes | - | Sidebar element ID |
| `side` | string | ✅ Yes | - | `'left'` or `'right'` |
| `toggleButtonId` | string | ✅ Yes | - | Toggle button element ID |
| `width` | string | No | `'450px'` | Sidebar width (CSS value) |
| `icon` | string | No | `'fa-bars'` | Font Awesome icon class |
| `title` | string | No | `'Sidebar'` | Sidebar title |
| `onOpen` | Function | No | `null` | Callback when sidebar opens |
| `onClose` | Function | No | `null` | Callback when sidebar closes |
| `onInit` | Function | No | `null` | Callback when sidebar first opens (lazy load) |
| `zIndex` | number | No | Auto | Custom z-index (auto-calculated if not provided) |
| `allowMultiple` | boolean | No | `false` | Allow multiple sidebars open on same side |

**Example:**

```javascript
SidebarManager.register({
    id: 'kanban-sidebar',
    side: 'left',
    toggleButtonId: 'kanban-toggle',
    width: '500px',
    title: 'InHouse Print Kanban',
    onInit: async () => {
        // Load kanban data once
        await loadKanbanBoards();
    }
});
```

---

### SidebarManager.toggle(sidebarId)

Toggle a sidebar open/closed.

```javascript
SidebarManager.toggle('synergy-sidebar');
```

---

### SidebarManager.open(sidebarId)

Open a sidebar.

```javascript
await SidebarManager.open('automations-sidebar');
```

---

### SidebarManager.close(sidebarId)

Close a sidebar.

```javascript
SidebarManager.close('settings-sidebar');
```

---

### SidebarManager.isOpen(sidebarId)

Check if a sidebar is currently open.

```javascript
if (SidebarManager.isOpen('synergy-sidebar')) {
    console.log('Synergy sidebar is open');
}
```

---

### SidebarManager.getAll()

Get all registered sidebars.

```javascript
const allSidebars = SidebarManager.getAll();
console.log(`${allSidebars.length} sidebars registered`);
```

---

### SidebarManager.getBySide(side)

Get all sidebars on a specific side.

```javascript
const leftSidebars = SidebarManager.getBySide('left');
const rightSidebars = SidebarManager.getBySide('right');
```

---

### SidebarManager.closeAll()

Close all open sidebars.

```javascript
SidebarManager.closeAll();
```

---

### SidebarManager.unregister(sidebarId)

Unregister a sidebar (cleanup).

```javascript
SidebarManager.unregister('old-sidebar');
```

---

## 🎨 Styling Your Sidebar

### Using Standard Classes

The framework provides standard classes you can use:

```html
<div class="universal-sidebar collapsed" id="my-sidebar">
    <!-- Header with standard styling -->
    <div class="universal-sidebar-header">
        <div class="universal-sidebar-title">
            <span><i class="fas fa-icon"></i> Title</span>
            <button class="universal-sidebar-close">
                <i class="fas fa-times"></i>
            </button>
        </div>
    </div>
    
    <!-- Scrollable content area -->
    <div class="universal-sidebar-content">
        <!-- Your content -->
    </div>
    
    <!-- Optional footer -->
    <div class="universal-sidebar-footer">
        <!-- Footer actions -->
    </div>
</div>
```

### Custom Styling

You can add your own CSS while keeping the framework's behavior:

```css
/* Custom styles for your module */
#mymodule-sidebar {
    background: linear-gradient(to bottom, #1a1f2e, #0f1419);
}

#mymodule-sidebar .universal-sidebar-header {
    background: rgba(99, 102, 241, 0.1);
    border-bottom: 2px solid #6366f1;
}

/* Custom content styling */
#mymodule-content .my-card {
    background: var(--bg-tertiary);
    border-radius: 8px;
    padding: 16px;
}
```

---

## 📦 Migration Examples

### Migrating Synergy Sidebar

**Before (Custom Implementation):**

```javascript
// synergy-sidebar-controller.js
async toggleSidebar() {
    const sidebar = document.getElementById('synergy-sidebar');
    sidebar.classList.toggle('expanded');
    sidebar.classList.toggle('collapsed');
}
```

**After (Using Framework):**

```javascript
// During app initialization
SidebarManager.register({
    id: 'synergy-sidebar',
    side: 'left',
    toggleButtonId: 'synergy-sidebar-toggle',
    width: '450px',
    title: 'Synergy Sessions',
    onInit: async () => {
        await SynergySidebar.loadSessions();
    }
});

// In your module code, just use:
// SidebarManager.toggle('synergy-sidebar')
// Instead of: SynergySidebar.toggleSidebar()
```

---

### Migrating Automations Sidebar

**Before (Custom Implementation):**

```javascript
function toggleAutomationsSidebar() {
    const sidebar = document.getElementById('automations-sidebar');
    sidebar.classList.toggle('expanded');
}
```

**After (Using Framework):**

```javascript
SidebarManager.register({
    id: 'automations-sidebar',
    side: 'right',
    toggleButtonId: 'automations-sidebar-toggle',
    width: '450px',
    title: 'Automation Workflows',
    onInit: async () => {
        await loadAutomations();
    }
});
```

---

### Adding New InHouse Print Kanban Sidebar

```javascript
// Just register it!
SidebarManager.register({
    id: 'kanban-sidebar',
    side: 'left',
    toggleButtonId: 'kanban-sidebar-toggle',
    width: '500px',
    icon: 'fa-tasks',
    title: 'InHouse Print Kanban',
    onInit: async () => {
        // Load kanban boards
        const boards = await fetch('/api/kanban/boards').then(r => r.json());
        renderKanbanBoards(boards);
    },
    onOpen: () => {
        // Refresh data when opened
        refreshKanbanView();
    }
});
```

---

## 🔧 Advanced Features

### Lazy Loading (Performance Optimization)

Use `onInit` to load data only when the sidebar is first opened:

```javascript
SidebarManager.register({
    id: 'heavy-sidebar',
    side: 'left',
    toggleButtonId: 'heavy-toggle',
    onInit: async () => {
        // This runs ONLY on first open
        console.log('Loading heavy data...');
        const data = await fetchLargeDataset();
        renderData(data);
        console.log('Data loaded and cached');
    },
    onOpen: () => {
        // This runs EVERY time sidebar opens
        console.log('Sidebar opened');
    }
});
```

### Multiple Sidebars on Same Side

By default, opening a sidebar closes others on the same side. To allow multiple:

```javascript
SidebarManager.register({
    id: 'sidebar-1',
    side: 'left',
    toggleButtonId: 'btn-1',
    allowMultiple: true  // ← Allow multiple sidebars open
});

SidebarManager.register({
    id: 'sidebar-2',
    side: 'left',
    toggleButtonId: 'btn-2',
    allowMultiple: true
});

// Now both can be open at the same time
SidebarManager.open('sidebar-1');
SidebarManager.open('sidebar-2');
```

### Custom Z-Index

Override auto-calculated z-index:

```javascript
SidebarManager.register({
    id: 'priority-sidebar',
    side: 'right',
    toggleButtonId: 'priority-btn',
    zIndex: 15000  // Always appear above others
});
```

### Programmatic Control

```javascript
// Open sidebar after user action
document.getElementById('my-button').addEventListener('click', () => {
    SidebarManager.open('synergy-sidebar');
});

// Close all sidebars before navigation
function navigateToPage(url) {
    SidebarManager.closeAll();
    window.location.href = url;
}

// Check state before action
if (!SidebarManager.isOpen('settings-sidebar')) {
    SidebarManager.open('settings-sidebar');
}
```

---

## 🎯 Best Practices

### 1. Use Consistent Widths

Stick to standard widths for visual consistency:

- **Compact sidebars:** 400px
- **Standard sidebars:** 450px
- **Wide sidebars:** 500-600px

### 2. Group Related Modules

Place related modules on the same side:

- **Left side:** Content/data modules (Synergy, Kanban, Documents)
- **Right side:** Settings/actions (Automations, Settings, User Profile)

### 3. Use Lazy Loading

Always use `onInit` for data fetching to improve performance:

```javascript
// ✅ GOOD - Lazy load data
onInit: async () => {
    const data = await fetch('/api/data').then(r => r.json());
    renderData(data);
}

// ❌ BAD - Load data immediately
// This loads data even if sidebar is never opened
fetch('/api/data').then(renderData);
```

### 4. Position Toggle Buttons Logically

- **Left modules:** Toggle buttons on left side of screen
- **Right modules:** Toggle buttons on right side of screen
- **Top-to-bottom:** Order buttons by frequency of use

### 5. Provide Visual Feedback

Use the `active` class on toggle buttons:

```javascript
onOpen: () => {
    document.getElementById('my-toggle').classList.add('active');
},
onClose: () => {
    document.getElementById('my-toggle').classList.remove('active');
}
```

---

## 🧪 Testing Your Sidebar

### Checklist:

- [ ] Sidebar slides in smoothly from correct side
- [ ] Toggle button shows active state when sidebar is open
- [ ] Toggle button is draggable and saves position
- [ ] Sidebar state persists across page refreshes
- [ ] onInit callback runs only once (check with console.log)
- [ ] onOpen/onClose callbacks run every time
- [ ] Sidebar closes when clicking close button
- [ ] Sidebar content is scrollable if it overflows
- [ ] No z-index conflicts with other UI elements
- [ ] Mobile responsive (sidebar fits on smaller screens)

### Debug Commands:

```javascript
// Check registered sidebars
console.log('Registered:', SidebarManager.getAll());

// Check if sidebar is open
console.log('Is open:', SidebarManager.isOpen('my-sidebar'));

// Check active sidebars
console.log('Active:', Array.from(SidebarManager.activeSidebars));

// Force open for testing
SidebarManager.open('my-sidebar');

// Force close all
SidebarManager.closeAll();
```

---

## 🐛 Troubleshooting

### Sidebar Doesn't Appear

**Problem:** Sidebar doesn't slide in when toggle button is clicked

**Solutions:**
1. Check element IDs match registration config
2. Verify sidebar HTML has `collapsed` class initially
3. Check browser console for JavaScript errors
4. Ensure `sidebar-manager.js` and `.css` are loaded

```javascript
// Debug: Check if sidebar is registered
console.log(SidebarManager.sidebars.has('my-sidebar'));

// Debug: Check if elements exist
console.log(document.getElementById('my-sidebar'));
console.log(document.getElementById('my-toggle'));
```

### Z-Index Conflicts

**Problem:** Sidebar appears behind other elements

**Solutions:**
1. Check if other elements have higher z-index
2. Set custom z-index in registration:

```javascript
SidebarManager.register({
    id: 'my-sidebar',
    zIndex: 25000  // Higher than default 9000
});
```

### Toggle Button Not Draggable

**Problem:** Can't reposition toggle button

**Solutions:**
1. Ensure button has `draggable="true"` attribute (framework adds this)
2. Check if button has `cursor: move` style
3. Verify no other drag handlers are interfering

### State Not Persisting

**Problem:** Sidebar state resets on page refresh

**Solutions:**
1. Check localStorage is enabled in browser
2. Verify no errors in console when saving state
3. Clear localStorage and try again:

```javascript
localStorage.removeItem('sidebarManagerState');
location.reload();
```

---

## 📚 Examples

### Complete Working Example

See `UI/modules/sidebar-framework/example-sidebar-integration.html` for a complete working example with:
- Multiple sidebars (left and right)
- Lazy loading
- Custom styling
- Event callbacks
- State persistence

---

**Last Updated:** November 28, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
