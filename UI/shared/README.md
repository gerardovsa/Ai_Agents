# UI/shared/ - Shared Global Resources

**Created:** November 29, 2025  
**Purpose:** Centralized location for all globally loaded, reusable code

## 📁 Directory Structure

```
shared/
├── css/                          # Global stylesheets
│   ├── status-indicator.css
│   ├── ui-standardization.css
│   ├── tabulator-enhancements.css
│   ├── tabulator-toast.css
│   └── ui-standards.css
│
├── js/                           # Global utilities & infrastructure
│   ├── status-indicator.js
│   ├── supabase-connection-manager.js
│   ├── supabase-heartbeat-listener.js
│   ├── data-loader.js
│   ├── synergy-realtime.js
│   └── tabulator-*.js (9 Tabulator utilities)
│
├── sidebar-framework/            # Universal sidebar system
│   ├── sidebar-manager.js
│   ├── sidebar-manager.css
│   └── sidebar-init.js
│
└── utilities/                    # Helper functions
    └── message_renderer.js
```

## 🎯 What Belongs Here

### ✅ **INCLUDE in shared/:**
- **Global utilities** loaded before module system
- **Shared frameworks** used by multiple modules
- **Infrastructure code** (Supabase, data loading, WebSocket)
- **UI standards** (global CSS, theme, components)
- **Reusable libraries** (Tabulator enhancements)

### ❌ **DO NOT include in shared/:**
- **Module-specific code** (goes in modules_internal/ or modules_external/)
- **Internal platform features** (prompt-library, automation-workflows, etc.)
- **Business logic** (belongs in modules)

## 📋 Usage Patterns

### Loading Order in HTML
```html
<!-- 1. External CDN libraries -->
<script src="https://cdn.../library.js"></script>

<!-- 2. Shared infrastructure (this directory) -->
<link rel="stylesheet" href="shared/css/status-indicator.css">
<script src="shared/js/supabase-connection-manager.js"></script>
<script src="shared/js/data-loader.js"></script>

<!-- 3. Shared frameworks -->
<link rel="stylesheet" href="shared/sidebar-framework/sidebar-manager.css">
<script src="shared/sidebar-framework/sidebar-manager.js"></script>

<!-- 4. Core module loader -->
<script src="modules_internal/module_loader.js"></script>

<!-- 5. Modules load dynamically -->
```

### Importing in JavaScript
```javascript
// External modules can use globally available objects
if (window.moduleLoader) {
    // Use module loader
}

if (window.SidebarManager) {
    // Use sidebar framework
}

if (window.supabaseClient) {
    // Use Supabase connection
}
```

## 🔧 Key Components

### CSS (Global Styles)
- **status-indicator.css** - Bottom-left connection status indicator
- **ui-standardization.css** - Standardized UI components (metrics, badges, buttons)
- **tabulator-*.css** - Tabulator table enhancements

### JS (Global Utilities)
- **status-indicator.js** - Loading/connection status display
- **supabase-connection-manager.js** - Centralized Supabase connection with health monitoring
- **supabase-heartbeat-listener.js** - Server heartbeat detection system
- **data-loader.js** - Centralized data loading with caching
- **synergy-realtime.js** - Synergy WebSocket manager
- **tabulator-*.js** - Tabulator utilities (functions, enhancements, i18n, validation, toast)

### Sidebar Framework
Universal sidebar system providing:
- **SidebarManager class** - Manages all module sidebars
- **Consistent behavior** - Open/close, z-index management, backdrop
- **Module integration** - Used by inhouse-kanban, communication-hub, etc.

### Utilities
- **message_renderer.js** - Message rendering helper functions

## 🔄 Migration Notes

### Previous Locations (Before Nov 29, 2025)
- `UI/css/` → `UI/shared/css/`
- `UI/js/` → `UI/shared/js/`
- `UI/modules_internal/sidebar-framework/` → `UI/shared/sidebar-framework/`
- `UI/modules_internal/shared/` → `UI/shared/utilities/`

### Why the Reorganization?
1. **Clarity** - Separate shared resources from internal modules
2. **Discoverability** - All global code in one place
3. **Maintainability** - Clear distinction between shared vs internal
4. **Modularity** - External modules can use shared frameworks without depending on internal code

## 🧪 Testing Checklist

After modifying shared/ code:
- [ ] Test Flask server startup (no 404 errors)
- [ ] Check browser console for loading errors
- [ ] Verify all 17 modules load successfully
- [ ] Test sidebar functionality (if framework changed)
- [ ] Test Supabase connection (if manager changed)
- [ ] Test Tabulator tables (if enhancements changed)

## 📚 Related Documentation
- `UI/modules_internal/README.md` - Core platform modules
- `UI/modules_external/README.md` - Business feature modules
- `MODULE_CLEANUP_COMPLETE_NOV29.md` - Complete reorganization history

---

**Last Updated:** November 29, 2025  
**Maintainer:** Platform Team  
**Status:** ✅ Production Ready
