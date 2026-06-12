# Module Metadata Standard

**Purpose**: Every module MUST declare its capabilities and architecture clearly  
**Location**: Top of every `.js` file  
**Format**: JSDoc comment block with structured metadata

---

## 📋 Required Metadata Block

```javascript
/**
 * FILE: UI/modules_[internal|external]/[module-name]/[module-name].js
 * MODULE TYPE: [internal|external|component]
 * ARCHITECTURE: [BaseModule-legacy|Framework-modern|Hybrid]
 * 
 * CAPABILITIES:
 * ================
 * DASHBOARD: [ENABLED|DISABLED]
 *   - Container ID: [#tab-xxx]
 *   - Rendering: [js-controlled|html-template|hybrid]
 *   - Init Method: [initializeDashboard()]
 *   - Entry Point: [Sidebar button click]
 * 
 * SIDEBAR: [ENABLED|DISABLED]
 *   - Container ID: [#xxx-sidebar]
 *   - HTML File: [xxx-SIDEBAR.html|none]
 *   - Rendering: [js-controlled|html-template|hybrid]
 *   - Init Method: [initializeSidebar()]
 *   - Entry Point: [Floating toggle click]
 * 
 * RENDERING PATHS:
 * ================
 * Path 1 - Dashboard:
 *   User clicks sidebar button
 *     → ModuleLoader.loadModule()
 *     → Inject dashboard HTML (if html-template)
 *     → Load JS file
 *     → Call initializeDashboard()
 *     → Render UI / Load data
 * 
 * Path 2 - Sidebar:
 *   User clicks floating toggle
 *     → ModuleLoader.loadModule()
 *     → Inject sidebar HTML (from html_file)
 *     → Load JS file
 *     → Call initializeSidebar()
 *     → Wire up events / Load data
 * 
 * INITIALIZATION ORDER:
 * =====================
 * 1. Constructor() - State setup only
 * 2. initializeDashboard() OR initializeSidebar() - Depends on entry point
 * 3. Load data from API
 * 4. Wire up event listeners
 * 5. Render initial UI state
 * 
 * DEPENDENCIES:
 * =============
 * - ModuleLoader (required: module discovery & loading)
 * - SidebarManager (optional: if has sidebar)
 * - ThreadManager (optional: if thread integration)
 * - BaseModule (legacy only: if extending BaseModule)
 * 
 * LAST MODIFIED: [YYYY-MM-DD] - [Description]
 */
```

---

## 🏷️ Metadata Field Definitions

### MODULE TYPE
- **internal**: Built-in UI components (settings, threads, etc.)
- **external**: Business modules (kanban, CRM, accounting, etc.)
- **component**: Reusable building blocks (thread-cards, charts, etc.)

### ARCHITECTURE
- **BaseModule-legacy**: Extends BaseModule class (OLD)
- **Framework-modern**: Pure framework approach, no BaseModule (NEW)
- **Hybrid**: Uses both patterns (TEMPORARY during migration)

### DASHBOARD
- **ENABLED**: Module has main tab view
- **Container ID**: DOM element ID where dashboard renders
- **Rendering**:
  - `js-controlled`: JavaScript creates all DOM elements
  - `html-template`: HTML file loaded and injected
  - `hybrid`: Mix of template + JS rendering
- **Init Method**: Function called to initialize dashboard
- **Entry Point**: How user accesses dashboard

### SIDEBAR
- **ENABLED**: Module has sidebar view
- **Container ID**: DOM element ID for sidebar
- **HTML File**: Sidebar template file (if html-template)
- **Rendering**: Same as dashboard
- **Init Method**: Function called to initialize sidebar
- **Entry Point**: How user accesses sidebar

---

## 📖 Examples

### Example 1: Dashboard + Sidebar (Both)
```javascript
/**
 * FILE: UI/modules_external/inhouse-kanban/inhouse-kanban.js
 * MODULE TYPE: external
 * ARCHITECTURE: BaseModule-legacy (TO BE MIGRATED)
 * 
 * CAPABILITIES:
 * ================
 * DASHBOARD: ENABLED
 *   - Container ID: #tab-inhouse-kanban
 *   - Rendering: js-controlled (renderKanbanBoard creates DOM)
 *   - Init Method: initializeDashboard()
 *   - Entry Point: Sidebar button click
 * 
 * SIDEBAR: ENABLED
 *   - Container ID: #inhouse-kanban-sidebar
 *   - HTML File: inhouse-kanban-SIDEBAR.html
 *   - Rendering: html-template (HTML file loaded by ModuleLoader)
 *   - Init Method: initializeSidebar()
 *   - Entry Point: Floating toggle click
 * 
 * RENDERING PATHS:
 * ================
 * Path 1 - Dashboard:
 *   User clicks sidebar button
 *     → ModuleLoader checks if loaded
 *     → If not: Load inhouse-kanban.js
 *     → Module constructor creates instance
 *     → Call initialize() (BaseModule pattern)
 *     → super.initialize() loads manifest, gets container
 *     → initializeKanbanBoard() renders dashboard UI
 * 
 * Path 2 - Sidebar:
 *   User clicks floating toggle
 *     → ModuleLoader checks if loaded
 *     → If not: Fetch inhouse-kanban-SIDEBAR.html
 *     → Inject HTML into DOM
 *     → Load inhouse-kanban.js
 *     → Call initializeSidebar() (custom method)
 *     → Wire up sidebar event listeners
 * 
 * INITIALIZATION ORDER:
 * =====================
 * 1. Constructor(moduleId) - Sets up state, API URLs, workboards
 * 2. initialize() - Calls super.initialize(), then initializeKanbanBoard()
 * 3. initializeKanbanBoard() - Renders dashboard HTML structure
 * 4. setupEventListeners() - Wires up filters, buttons, drag-drop
 * 5. loadKanbanData() - Fetches jobs from API
 * 
 * DEPENDENCIES:
 * =============
 * - ModuleLoader (loads module on-demand)
 * - SidebarManager (manages sidebar open/close)
 * - BaseModule (provides initialize, loadManifest, createModuleStructure)
 * - kanban-logger.js (analytics tracking)
 * - kanban-supabase-integration.js (database integration)
 * - kanban-supabase-ui.js (Supabase UI components)
 * 
 * LAST MODIFIED: 2025-11-29 - Added metadata block
 */

class InhouseKanbanModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);
        // ...
    }
}
```

### Example 2: Dashboard Only
```javascript
/**
 * FILE: UI/modules_external/quote-calculator/quote-calculator.js
 * MODULE TYPE: external
 * ARCHITECTURE: BaseModule-legacy
 * 
 * CAPABILITIES:
 * ================
 * DASHBOARD: ENABLED
 *   - Container ID: #tab-quote-calculator
 *   - Rendering: js-controlled (calculator UI built in JS)
 *   - Init Method: initialize()
 *   - Entry Point: Sidebar button click
 * 
 * SIDEBAR: DISABLED
 *   - Container ID: N/A
 *   - HTML File: none
 *   - Rendering: N/A
 *   - Init Method: N/A
 *   - Entry Point: N/A
 * 
 * RENDERING PATHS:
 * ================
 * Path 1 - Dashboard (ONLY PATH):
 *   User clicks sidebar button
 *     → switchTab('quote-calculator')
 *     → ModuleLoader loads quote-calculator.js
 *     → Module constructor creates instance
 *     → Call initialize()
 *     → Render calculator form
 * 
 * INITIALIZATION ORDER:
 * =====================
 * 1. Constructor('quote-calculator')
 * 2. initialize() - Calls super.initialize()
 * 3. renderCalculatorForm() - Builds UI
 * 4. setupEventListeners() - Wire up form inputs
 * 
 * DEPENDENCIES:
 * =============
 * - ModuleLoader
 * - BaseModule
 * - Calculator API (/api/calculator/*)
 * 
 * LAST MODIFIED: 2025-11-29 - Added metadata block
 */
```

### Example 3: Sidebar Only
```javascript
/**
 * FILE: UI/modules_internal/quick-actions/quick-actions.js
 * MODULE TYPE: internal
 * ARCHITECTURE: Framework-modern
 * 
 * CAPABILITIES:
 * ================
 * DASHBOARD: DISABLED
 *   - Container ID: N/A
 *   - Rendering: N/A
 *   - Init Method: N/A
 *   - Entry Point: N/A
 * 
 * SIDEBAR: ENABLED
 *   - Container ID: #quick-actions-sidebar
 *   - HTML File: quick-actions.html
 *   - Rendering: html-template (HTML loaded by ModuleLoader)
 *   - Init Method: initializeSidebar()
 *   - Entry Point: Floating toggle click
 * 
 * RENDERING PATHS:
 * ================
 * Path 1 - Sidebar (ONLY PATH):
 *   User clicks floating toggle
 *     → ModuleLoader loads quick-actions.html
 *     → Inject sidebar HTML
 *     → Load quick-actions.js
 *     → Call initializeSidebar()
 *     → Populate action buttons
 * 
 * INITIALIZATION ORDER:
 * =====================
 * 1. Constructor() - State setup
 * 2. initializeSidebar() - Wire up buttons
 * 3. loadUserActions() - Fetch user's configured actions
 * 
 * DEPENDENCIES:
 * =============
 * - ModuleLoader
 * - SidebarManager
 * - ThreadManager (for thread creation shortcuts)
 * 
 * LAST MODIFIED: 2025-11-29 - Created metadata standard
 */
```

### Example 4: Component (No UI)
```javascript
/**
 * FILE: UI/modules_internal/thread-cards/thread-cards.js
 * MODULE TYPE: component
 * ARCHITECTURE: Framework-modern
 * 
 * CAPABILITIES:
 * ================
 * DASHBOARD: DISABLED (No standalone UI)
 *   - Container ID: N/A
 *   - Rendering: N/A
 *   - Init Method: N/A
 *   - Entry Point: N/A
 * 
 * SIDEBAR: DISABLED (Building block only)
 *   - Container ID: N/A
 *   - HTML File: none
 *   - Rendering: N/A
 *   - Init Method: N/A
 *   - Entry Point: N/A
 * 
 * COMPONENT USAGE:
 * ================
 * This is a BUILDING BLOCK used by other modules.
 * It provides the ThreadCard class for rendering thread cards.
 * 
 * Used by:
 * - thread-manager (thread list view)
 * - dashboard (recent threads widget)
 * - search (search results)
 * 
 * Usage Pattern:
 *   const card = new ThreadCard(threadData);
 *   container.appendChild(card.render());
 * 
 * INITIALIZATION ORDER:
 * =====================
 * N/A - No initialization, used as library
 * 
 * DEPENDENCIES:
 * =============
 * - None (pure utility component)
 * 
 * LAST MODIFIED: 2025-11-29 - Marked as component
 */
```

---

## ✅ Validation Checklist

Before committing module code, verify:

- [ ] Metadata block exists at top of file
- [ ] MODULE TYPE declared (internal/external/component)
- [ ] ARCHITECTURE declared (BaseModule-legacy/Framework-modern/Hybrid)
- [ ] DASHBOARD capability clearly stated (ENABLED/DISABLED)
- [ ] SIDEBAR capability clearly stated (ENABLED/DISABLED)
- [ ] Container IDs specified for enabled capabilities
- [ ] Rendering method specified (js-controlled/html-template/hybrid)
- [ ] Init methods specified
- [ ] Entry points documented
- [ ] Rendering paths described step-by-step
- [ ] Initialization order numbered sequentially
- [ ] Dependencies listed with purpose
- [ ] LAST MODIFIED date updated

---

## 🚀 Migration Strategy

### Phase 1: ADD METADATA (1 hour)
- Add metadata block to ALL modules
- Don't change code, just document current state
- Identifies which modules need migration

### Phase 2: CATEGORIZE (30 minutes)
- Tag modules as BaseModule-legacy or Framework-modern
- Identify hybrid cases
- Prioritize migration order

### Phase 3: MIGRATE (2-3 days per module)
- Convert BaseModule-legacy → Framework-modern
- Remove `extends BaseModule`
- Split initialize() into initializeDashboard() + initializeSidebar()
- Update metadata block

### Phase 4: VERIFY (1 hour per module)
- Test dashboard rendering
- Test sidebar rendering
- Verify no console errors
- Update metadata LAST MODIFIED

---

**Last Updated**: November 29, 2025  
**Status**: PRODUCTION STANDARD (Mandatory for all modules)
