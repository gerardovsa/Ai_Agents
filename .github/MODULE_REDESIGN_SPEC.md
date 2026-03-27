# Module System Redesign — Complete Specification
**Version: 1.0 — March 27, 2026**
**Status: READY TO IMPLEMENT**
**Author: Architecture review + design — GitHub Copilot**
**Intended audience: AI agents, developers implementing this work**

---

## Table of Contents

1. [Why This Redesign Is Needed](#1-why-this-redesign-is-needed)
2. [Current Architecture Problems](#2-current-architecture-problems)
3. [Target Architecture](#3-target-architecture)
4. [Shared Component Library](#4-shared-component-library)
5. [Standard Module Structure](#5-standard-module-structure)
6. [DB-Driven Sidebar Wiring (initModulesFromOrg)](#6-db-driven-sidebar-wiring)
7. [Shared Auth-Aware API Client](#7-shared-auth-aware-api-client)
8. [Migrating Xero to V4 Pattern (Gold Standard)](#8-migrating-xero-to-v4-pattern)
9. [Implementation Order](#9-implementation-order)
10. [Checklist for a New Module](#10-checklist-for-a-new-module)
11. [What NOT to Change](#11-what-not-to-change)

---

## 1. Why This Redesign Is Needed

The platform supports multi-tenant organisations. Each org can enable/disable modules via a
DB catalog (`ai_infrastructure.module_catalog` + `org_module_access`). Individual users can
have per-module restrictions (`user_module_access`). This backend is fully built and
working as of Migration 039.

**However, none of this affects the sidebar or UI.** The sidebar is still driven by a static
`manifest.json` file that is identical for every user. Every module renders its UI differently.
There are four competing JS patterns and no reusable component library.

The result:
- Enabling a module in the DB does not show it in the sidebar
- Building a new module requires inventing its entire UI from scratch
- Bugs like missing auth headers recur because every module has its own `fetch()` calls
- Visual inconsistency across modules despite a design system existing and being unused

This spec defines exactly what to build to fix all of the above.

---

## 2. Current Architecture Problems

### Problem 1: Four Competing JS Patterns

| Pattern | Used By | Problem |
|---------|---------|---------|
| Class + inheritance (`XeroModule extends BaseModule`) | Xero | `BaseModule` is a polyfill defined inside `xero.js` — not actually a global base |
| Flat script (no class) | Shopify | Not reusable, no lifecycle hooks, monolithic |
| V4 Composition (lifecycle hooks, utility injection) | **Nobody** — it's a template only | Designed correctly but never adopted |
| ModuleManager + manifest.json | Sidebar icon loader | Static JSON, everyone sees same modules |

**Fix:** Adopt V4 Composition as the one mandatory pattern. All new modules use it.
Migration of Xero provides the gold-standard reference.

### Problem 2: No Shared Component Library

Every module builds its own KPI cards, filter bars, data tables, and chart panels from
scratch in HTML. The same card markup is repeated 6+ times across different modules with
slightly different classes. `ui-standardization.css` exists with design tokens but nothing
builds components from it programmatically.

**Fix:** A `shared/js/module-components.js` file exporting factory functions:
`createKpiCard()`, `createFilterBar()`, `createDataTable()`, `createChartPanel()`.

### Problem 3: Raw `fetch()` With Manual Auth Headers

Every module calls:
```javascript
fetch('/api/xero/invoices', {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
})
```

This is the source of every auth header bug. If `authToken` is renamed, every module breaks.
If the server returns 401 (token expired), nothing handles it consistently.

**Fix:** A shared `ModuleAPI` wrapper so modules call:
```javascript
this.api.get('/api/xero/invoices')
```
...and auth, error handling, and retry are centralised in one place.

### Problem 4: Sidebar Not Connected to DB

`manifest.json` is a static file listing 7 modules. The DB has 26. The sidebar renders
from the file, not the DB. Enabling a module in Org Settings has no visible effect.

**Fix:** `initModulesFromOrg()` function called on login that reads `GET /api/org/modules`
and drives sidebar visibility. `manifest.json` becomes a legacy fallback only.

### Problem 5: No Standard Module Folder Structure

Modules have inconsistent folder layouts:
- Xero has `ui/` subfolder for sub-reports; Shopify does not
- Some have `routes/blueprint.py`; others put routes in parent directory
- Tool definitions mix with implementations in some; others keep them separate

**Fix:** Enforce the standard layout defined in Section 5.

---

## 3. Target Architecture

### The Three-Layer Model

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: Shared Infrastructure                         │
│  shared/js/module-api.js      ← auth-aware fetch()     │
│  shared/js/module-components.js ← KPI, table, chart    │
│  shared/css/ui-standardization.css ← design tokens     │
└────────────────────┬────────────────────────────────────┘
                     │ used by
┌────────────────────▼────────────────────────────────────┐
│  LAYER 2: Module V4 Pattern (one pattern for all)       │
│  modules_external/<name>/<name>.js                      │
│  export default {                                       │
│      async onDashboardLoad(utilities) { ... },          │
│      async onSidebarLoad(utilities) { ... },            │
│      async onUnload() { ... }                           │
│  }                                                      │
└────────────────────┬────────────────────────────────────┘
                     │ loaded by
┌────────────────────▼────────────────────────────────────┐
│  LAYER 3: DB-Driven Sidebar Wiring                      │
│  initModulesFromOrg()  ← reads GET /api/org/modules     │
│  Shows/hides sidebar icons and tab-content divs         │
│  Replaces manifest.json static loader                   │
└─────────────────────────────────────────────────────────┘
```

### What a Complete Standard Module Looks Like

```
dashboard tab-content div       ← in business-ai-platform-v2.html
  └── module.js onDashboardLoad()
        └── KpiCards from module-components.js
        └── FilterBar from module-components.js
        └── DataTable (Tabulator wrapper) from module-components.js
        └── ChartPanel (ApexCharts wrapper) from module-components.js
        └── all API calls via this.api.get() from module-api.js
        └── CSS from ui-standardization.css tokens only
```

---

## 4. Shared Component Library

### File: `UI/shared/js/module-components.js`

Create this file. It exports factory functions that return DOM elements styled to
`ui-standardization.css` tokens. Modules call these instead of writing HTML.

#### 4a. `createKpiCard(config)` — Metric summary card

```javascript
/**
 * Creates a standardised KPI/metric card.
 * @param {object} config
 * @param {string} config.id        - HTML id for the value span
 * @param {string} config.icon      - FontAwesome class e.g. "fas fa-dollar-sign"
 * @param {string} config.label     - Card label text
 * @param {string} config.value     - Initial value (can be updated later)
 * @param {string} [config.variant] - "success"|"error"|"warning"|"info" (left border colour)
 * @param {string} [config.trend]   - Trend text e.g. "+12% vs last month"
 * @param {string} [config.trendDir]- "up"|"down"|"neutral"
 * @returns {HTMLElement}
 */
export function createKpiCard({ id, icon, label, value = '—', variant = '', trend = '', trendDir = 'neutral' }) {
    const card = document.createElement('div');
    card.className = `metric-card ${variant}`;
    card.innerHTML = `
        <div class="metric-icon">
            <i class="${icon}"></i>
        </div>
        <div class="metric-content">
            <div class="metric-value" id="${id}">${value}</div>
            <div class="metric-label">${label}</div>
            ${trend ? `<div class="metric-trend ${trendDir}"><i class="fas fa-arrow-${trendDir === 'up' ? 'up' : trendDir === 'down' ? 'down' : 'equals'}"></i> ${trend}</div>` : ''}
        </div>
    `;
    return card;
}

// Helper: Update a KPI card value after data loads
export function updateKpiCard(id, value, trend = null) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
    if (trend) {
        const trendEl = el?.closest('.metric-card')?.querySelector('.metric-trend');
        if (trendEl) trendEl.textContent = trend;
    }
}
```

#### 4b. `createFilterBar(config)` — Standardised filter row

```javascript
/**
 * Creates a filter bar with date range, status dropdowns, and search input.
 * @param {object} config
 * @param {Array}  config.filters     - Filter definitions
 * @param {string} config.filters[].id       - select element id
 * @param {string} config.filters[].label    - label text
 * @param {Array}  config.filters[].options  - [{value, label}]
 * @param {boolean} [config.showSearch]      - include search input
 * @param {function} config.onChange         - callback on any change
 * @returns {HTMLElement}
 */
export function createFilterBar({ filters = [], showSearch = true, onChange }) { ... }
```

#### 4c. `createDataTable(config)` — Tabulator wrapper

```javascript
/**
 * Creates a Tabulator table with standard theming, export buttons, and pagination.
 * @param {object} config
 * @param {string} config.containerId  - ID to render into
 * @param {Array}  config.columns      - Tabulator column definitions
 * @param {Array}  [config.data]       - Initial data
 * @param {boolean} [config.exportable] - Show CSV/Excel export buttons
 * @param {function} [config.onRowClick]
 * @returns {Tabulator} instance
 */
export function createDataTable({ containerId, columns, data = [], exportable = true, onRowClick }) { ... }
```

#### 4d. `createChartPanel(config)` — ApexCharts wrapper

```javascript
/**
 * Creates an ApexCharts chart panel with title, type selector, and export.
 * @param {object} config
 * @param {string} config.containerId
 * @param {string} config.title
 * @param {string} [config.type]      - "bar"|"line"|"donut" (default: "bar")
 * @param {object} [config.series]    - ApexCharts series data
 * @param {Array}  [config.categories]
 * @returns {{ chart: ApexCharts, update: function }}
 */
export function createChartPanel({ containerId, title, type = 'bar', series = [], categories = [] }) { ... }
```

### Implementation Notes for module-components.js

- All components use CSS classes from `ui-standardization.css` — **no inline styles except dynamic values**
- Components return DOM elements, not HTML strings — avoids XSS risks
- Each factory function is ~30–50 lines — keep them simple
- Start with `createKpiCard` and `createDataTable` as they are used most

---

## 5. Standard Module Structure

Every module in `modules_external/` MUST follow this layout:

```
UI/modules_external/<module-name>/
├── manifest.json               ← REQUIRED — module metadata
├── <module-name>.js            ← REQUIRED — V4 composition object
├── <module-name>.css           ← REQUIRED — module-specific CSS only
├── routes/
│   └── blueprint.py            ← REQUIRED if backend API needed
├── tools/
│   └── <module-name>_tools.json ← REQUIRED if AI tools used
├── implementations/
│   └── <module-name>_wrapper.py ← REQUIRED if AI tools used
└── ui/                          ← OPTIONAL — sub-reports / iframes
    └── <sub-report>.html
```

### `manifest.json` Schema (Standard)

```json
{
  "id": "module-name",
  "module_name": "module_name",
  "display_name": "Human Name",
  "description": "One-sentence description",
  "version": "1.0.0",
  "icon_class": "fas fa-star",
  "icon_color": "#F59E0B",
  "tab_id": "tab-module-name",
  "min_plan_tier": "professional",
  "required_platforms": ["shopify"],
  "capabilities": {
    "dashboard": true,
    "sidebar": false,
    "ai_tools": true
  },
  "api_prefix": "/api/module-name"
}
```

### `<module-name>.js` — V4 Composition Pattern (REQUIRED)

```javascript
/**
 * FILE: UI/modules_external/<module-name>/<module-name>.js
 * ARCHITECTURE: V4 Composition (lifecycle hooks + utility injection)
 * DB module_name: <module_name>
 * Tab ID: tab-<module-name>
 * API prefix: /api/<module-name>
 */

import { createKpiCard, updateKpiCard, createDataTable, createChartPanel, createFilterBar }
    from '../../shared/js/module-components.js';

export default {
    // ── State ──────────────────────────────────────────────────────
    api: null, dom: null, storage: null, events: null, log: null,
    data: [],
    filters: { dateRange: 90, status: 'all', search: '' },
    table: null,
    chart: null,
    eventCleanupFns: [],

    // ── Lifecycle: Dashboard ───────────────────────────────────────
    async onDashboardLoad(utilities) {
        Object.assign(this, utilities);
        this.log.info('Loading dashboard...');
        try {
            const container = this.dom.getContainer('tab-<module-name>');
            this._renderShell(container);
            this._setupEvents();
            await this._loadData();
        } catch (e) {
            this.log.error('Dashboard failed to load', e);
        }
    },

    // ── Lifecycle: Unload (cleanup) ────────────────────────────────
    async onUnload() {
        this.eventCleanupFns.forEach(fn => fn());
        this.eventCleanupFns = [];
        if (this.table) { this.table.destroy(); this.table = null; }
        if (this.chart)  { this.chart.destroy(); this.chart = null; }
    },

    // ── Private: Render ────────────────────────────────────────────
    _renderShell(container) {
        // 1. KPI grid
        const kpiGrid = document.createElement('div');
        kpiGrid.className = 'metric-grid';
        kpiGrid.appendChild(createKpiCard({ id: 'kpi-total', icon: 'fas fa-dollar-sign', label: 'Total' }));
        container.appendChild(kpiGrid);

        // 2. Filter bar
        container.appendChild(createFilterBar({
            filters: [{ id: 'filter-status', label: 'Status', options: [
                { value: 'all', label: 'All' }, { value: 'active', label: 'Active' }
            ]}],
            showSearch: true,
            onChange: () => this._applyFilters()
        }));

        // 3. Chart + Table
        createChartPanel({ containerId: 'chart-<module-name>', title: 'Overview', type: 'bar' });
        this.table = createDataTable({
            containerId: 'table-<module-name>',
            columns: [{ title: 'Name', field: 'name' }],
            exportable: true
        });
    },

    // ── Private: Data ──────────────────────────────────────────────
    async _loadData() {
        const result = await this.api.get('/api/<module-name>/data');
        this.data = result.data || [];
        this.table.replaceData(this.data);
        updateKpiCard('kpi-total', this.data.length);
    },

    _applyFilters() { /* filter this.data then this.table.replaceData(filtered) */ },
    _setupEvents() { /* add event listeners, push cleanup fn to this.eventCleanupFns */ }
};
```

---

## 6. DB-Driven Sidebar Wiring

### File to edit: `UI/business-ai-platform-v2.html`

This is the most critical piece. Without this, the DB module catalog has no effect on the UI.

### 6a. Add `module-hidden` CSS (once, in the `<style>` block)

Find the CSS block near the top of the file and add:

```css
/* DB-driven module visibility — set by initModulesFromOrg() */
.module-hidden { display: none !important; }
```

### 6b. Add `data-module` attributes to all optional Zone 1 sidebar buttons

Find each hardcoded sidebar `<li>` or `<button>` for optional modules and add `data-module="..."`:

```html
<!-- WooCommerce — currently NO data-module attribute, hardcoded visible -->
<!-- CHANGE: add data-module="woocommerce" -->
<button class="sidebar-icon-btn" data-tab="sales" data-module="woocommerce" title="Sales & E-Commerce">
    <i class="fas fa-shopping-cart"></i>
</button>
```

Full list of buttons that need `data-module` added:

| Sidebar button (search term) | Add `data-module=` |
|---|---|
| `data-tab="sales"` | `woocommerce` |
| `data-tab="analytics"` | *(core — no gate needed)* |
| `data-tab="automation"` | *(core — no gate needed)* |
| `data-tab="multi-agent"` | *(core — no gate needed)* |
| `data-tab="synergy"` | *(core — no gate needed)* |
| `data-tab="inhouse-kanban"` | `inhouse_kanban` *(already has it)* |
| `data-tab="vsa-veterinary-alerts"` | `vsa_veterinary` *(already has it, hidden)* |

### 6c. Implement `initModulesFromOrg(enabledModules)` function

Add this function in the main `<script>` block of `business-ai-platform-v2.html`.
Call it after login and after any org switch.

```javascript
/**
 * initModulesFromOrg — DB-driven sidebar visibility
 *
 * Called after: login, org switch, token refresh.
 * Reads the user's enabled module set and:
 *   1. Shows/hides Zone 1 optional sidebar buttons (data-module attribute)
 *   2. Shows/hides the corresponding tab-content panels
 *   3. Rebuilds Zone 2 #sidebarModulesSection from DB data (replaces manifest.json)
 *
 * @param {Array} enabledModules - from GET /api/org/modules, filter is_enabled=true
 *   Each entry: { module_name, display_name, icon_class, icon_color, ... }
 */
function initModulesFromOrg(enabledModules) {
    const enabledSet = new Set(enabledModules.map(m => m.module_name));

    // ── Step 1: Gate Zone 1 optional items by data-module attribute ──────────
    document.querySelectorAll('[data-module]').forEach(el => {
        const modName = el.getAttribute('data-module');
        const visible = enabledSet.has(modName);
        el.classList.toggle('module-hidden', !visible);
    });

    // ── Step 2: Gate corresponding tab-content panels ─────────────────────────
    // Maps module_name → tab-content id (for modules where tab≠module_name)
    const TAB_MAP = {
        'woocommerce':    'tab-sales',
        'inhouse_kanban': 'tab-inhouse-kanban',
        'vsa_veterinary': 'tab-vsa-veterinary-alerts',
        'stock_management': 'tab-stock',
        // modules with matching names handled by convention: tab-{module_name.replace('_','-')}
    };
    enabledModules.forEach(m => {
        const tabId = TAB_MAP[m.module_name] || `tab-${m.module_name.replace(/_/g, '-')}`;
        const tab = document.getElementById(tabId);
        if (tab) tab.classList.remove('module-hidden');
    });
    // Hide tabs for modules NOT enabled
    document.querySelectorAll('.tab-content[id^="tab-"]').forEach(tab => {
        const moduleId = tab.id.replace('tab-', '').replace(/-/g, '_');
        const reverseMap = Object.fromEntries(Object.entries(TAB_MAP).map(([k,v]) => [v.replace('tab-',''), k]));
        const modName = reverseMap[moduleId] || moduleId;
        // Only hide if this tab is an optional module tab (has a DB entry)
        if (!CORE_TABS.has(tab.id) && !enabledSet.has(modName)) {
            tab.classList.add('module-hidden');
        }
    });

    // ── Step 3: Rebuild Zone 2 sidebar from DB data ───────────────────────────
    const container = document.getElementById('sidebarModulesSection');
    if (!container) return;
    container.innerHTML = '';

    // Modules that render as Zone 2 sidebar icon buttons
    const ZONE2_MODULES = [
        'inhouse_print', 'quote_calculator', 'stock_management',
        'xero', 'shopify', 'auspost_shipping', 'customer_reactivation',
        'database_visualizer', 'github', 'render_management', 'local_filesystem'
    ];

    ZONE2_MODULES.forEach(modName => {
        if (!enabledSet.has(modName)) return;
        const catalog = enabledModules.find(m => m.module_name === modName) || {};
        const btn = document.createElement('button');
        btn.className = 'sidebar-icon-btn';
        btn.title = catalog.display_name || modName;
        btn.setAttribute('data-module', modName);
        btn.setAttribute('data-action', modName.replace(/_/g, '-'));
        btn.innerHTML = `<i class="${catalog.icon_class || 'fas fa-cube'}" style="color:${catalog.icon_color || '#6B7280'}"></i>`;
        container.appendChild(btn);
    });
}

// Tabs that are ALWAYS visible regardless of module state
const CORE_TABS = new Set([
    'tab-home', 'tab-communication', 'tab-analytics',
    'tab-universal-search', 'tab-vector-database', 'tab-automation',
    'tab-multi-agent', 'tab-synergy'
]);
```

### 6d. Wire to Login Flow

Find the existing login success callback in `business-ai-platform-v2.html` where
`AppState.user` is set, and add:

```javascript
// After successful login + org data loaded:
async function loadAndApplyOrgModules() {
    try {
        const token = localStorage.getItem('authToken');
        if (!token) return;
        const res = await fetch(`${API_BASE_URL}/api/org/modules`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (data.success && Array.isArray(data.modules)) {
            const enabled = data.modules.filter(m => m.is_enabled);
            initModulesFromOrg(enabled);
        }
    } catch (e) {
        console.warn('[ModuleGating] Could not load org modules:', e);
        // Fail gracefully — show all modules rather than hiding everything
    }
}
// Call on login:
loadAndApplyOrgModules();
// Call on org switch (wherever _orgData changes):
// loadAndApplyOrgModules();
```

---

## 7. Shared Auth-Aware API Client

### File: `UI/shared/js/module-api.js`

This centralises all API calls from modules. Modules stop using raw `fetch()`.

```javascript
/**
 * ModuleAPI — auth-aware API client for modules
 *
 * Injected into module's `utilities.api` by the module loader.
 * Automatically attaches Authorization header from localStorage.
 * Handles 401 UnauthorizedError by emitting a global event.
 */
export class ModuleAPI {
    constructor({ baseUrl = '', moduleId = '' } = {}) {
        this.baseUrl = baseUrl || window.API_BASE_URL || '';
        this.moduleId = moduleId;
    }

    _headers(extra = {}) {
        const token = localStorage.getItem('authToken') || '';
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...extra
        };
    }

    async _request(method, path, body = null) {
        const url = `${this.baseUrl}${path}`;
        const opts = { method, headers: this._headers() };
        if (body !== null) opts.body = JSON.stringify(body);

        const res = await fetch(url, opts);

        if (res.status === 401) {
            // Token expired — emit event so app can handle logout/refresh
            window.dispatchEvent(new CustomEvent('module:auth-expired', { detail: { module: this.moduleId } }));
            throw new Error('Session expired. Please log in again.');
        }
        if (!res.ok) {
            const err = await res.json().catch(() => ({ error: res.statusText }));
            throw new Error(err.error || `HTTP ${res.status}`);
        }
        return res.json();
    }

    get(path)              { return this._request('GET', path); }
    post(path, body)       { return this._request('POST', path, body); }
    put(path, body)        { return this._request('PUT', path, body); }
    delete(path)           { return this._request('DELETE', path); }
    patch(path, body)      { return this._request('PATCH', path, body); }
}
```

**Injected as `utilities.api`** by the module loader so every module that follows V4
pattern gets it automatically with no imports required.

---

## 8. Migrating Xero to V4 Pattern (Gold Standard)

Xero is the most complete module — migrating it first creates the definitive reference.

### What changes in `xero.js`

1. Remove the inline `BaseModule` polyfill class
2. Remove `class XeroModule extends BaseModule`
3. Convert to exported V4 object: `export default { ... }`
4. Move constructor state to plain object properties
5. Replace `this.API_BASE_URL + ...` with `this.api.get(...)`
6. Add `onDashboardLoad(utilities)`, `onSidebarLoad(utilities)`, `onUnload()` lifecycle hooks
7. Import `createKpiCard`, `createDataTable`, `createChartPanel` from module-components.js
8. Keep all existing business logic — only the shell pattern changes

### What does NOT change in Xero

- Sub-tab structure (Invoices, Contacts, Payments, Accounts, Quotes)
- Tabulator table configuration
- ApexCharts chart code
- xero.css (keep as-is — add module-components classes gradually)
- All backend routes (`xero_routes.py`) — untouched
- The Flask Blueprint (`routes/blueprint.py`) — untouched

### Verifying the Migration Worked

After migration:
1. Xero dashboard loads and displays data ✅
2. `createKpiCard()` renders the KPI cards ✅
3. `this.api.get('/api/xero/dashboard')` returns data correctly ✅
4. `onUnload()` cleans up tables and charts without memory leaks ✅
5. Code can be used as a template by copying `xero.js` → `new-module.js` and
   doing a find-replace on `xero` → `new-module` ✅

---

## 9. Implementation Order

Do these steps **in order**. Each step is independently testable before moving on.

### Phase 1 — Infrastructure (no visible UI changes)

| # | Task | File | Test |
|---|------|------|------|
| 1 | Create `module-api.js` with `ModuleAPI` class | `UI/shared/js/module-api.js` | Unit test: `new ModuleAPI().get('/api/org/info')` returns data |
| 2 | Create `module-components.js` with `createKpiCard` + `createDataTable` | `UI/shared/js/module-components.js` | Render a test card in browser console |
| 3 | Add `module-hidden` CSS to main HTML | `UI/business-ai-platform-v2.html` | Not visible yet |

### Phase 2 — DB-Driven Sidebar

| # | Task | File | Test |
|---|------|------|------|
| 4 | Add `data-module="woocommerce"` to sales sidebar button | `business-ai-platform-v2.html` | Attribute appears in DOM |
| 5 | Implement `initModulesFromOrg()` function | `business-ai-platform-v2.html` | Call manually in console: `initModulesFromOrg([])` — all optional tabs hidden |
| 6 | Wire `loadAndApplyOrgModules()` to login flow | `business-ai-platform-v2.html` | Log in → sidebar shows only org-enabled modules |
| 7 | Verify WooCommerce tab hidden for orgs without `woocommerce` enabled | Browser | Disable woocommerce in org → tab disappears |
| 8 | Verify Zone 2 renders from DB icons not manifest.json | Browser | Enable `xero` module → Xero icon appears via DB data |

### Phase 3 — Gold Standard Module Migration (Xero)

| # | Task | File | Test |
|---|------|------|------|
| 9  | Migrate `xero.js` to V4 composition pattern | `UI/modules_external/xero/xero.js` | Xero dashboard loads correctly |
| 10 | Replace `fetch('/api/xero/...')` in xero.js with `this.api.get(...)` | `xero.js` | All data endpoints return correctly |
| 11 | Replace KPI card HTML with `createKpiCard()` calls | `xero.js` | KPI cards render identically |
| 12 | Replace Tabulator init with `createDataTable()` | `xero.js` | Tables render correctly |
| 13 | Update `xero/manifest.json` to use new schema | `manifest.json` | Schema validates |

### Phase 4 — Migrate Shopify to match Xero

| # | Task | File |
|---|------|------|
| 14 | Create `shopify/ui/` folder and `shopify-dashboard.html` | `UI/modules_external/shopify/ui/` |
| 15 | Convert `shopify.js` to V4 pattern using Xero as reference | `shopify.js` |
| 16 | Replace raw fetch with `this.api.get()` | `shopify.js` |

### Phase 5 — Clean Up Orphaned / Missing Items

| # | Task |
|---|------|
| 17 | Either add `vsa_veterinary` to `module_catalog` + sidebar button, or remove `tab-vsa-veterinary-alerts` from HTML |
| 18 | Remove `manifest.json` fallback from `ModuleManager` after `initModulesFromOrg()` is live |
| 19 | Add sidebar entries for `auspost_shipping` and `customer_reactivation` (they exist as modules, not in sidebar) |

---

## 10. Checklist for a New Module

When building a brand-new module from scratch, complete every item:

### Backend
- [ ] `INSERT INTO ai_infrastructure.module_catalog (...)` — adds module to DB catalog
- [ ] `INSERT INTO ai_infrastructure.org_module_access (...)` — enables it for target org(s)
- [ ] `UI/modules_external/<name>/routes/blueprint.py` — Flask Blueprint registered
- [ ] `UI/modules_external/<name>/tools/<name>_tools.json` — AI tool definitions
- [ ] `UI/modules_external/<name>/implementations/<name>_wrapper.py` — tool implementations

### Frontend
- [ ] `UI/modules_external/<name>/manifest.json` — module metadata
- [ ] `UI/modules_external/<name>/<name>.js` — V4 composition pattern
- [ ] `UI/modules_external/<name>/<name>.css` — module-specific styles only
- [ ] Tab-content div added to `UI/business-ai-platform-v2.html` with `id="tab-<name>"`
- [ ] Add to `ZONE2_MODULES` array in `initModulesFromOrg()` in main HTML
- [ ] Add to `TAB_MAP` in `initModulesFromOrg()` if tab ID doesn't match module name

### Verification
- [ ] Module appears in `GET /api/org/modules/catalog`
- [ ] Toggle ON in Org Settings → Modules panel → sidebar icon appears
- [ ] Toggle OFF → sidebar icon disappears and tab is inaccessible
- [ ] Module loads without console errors
- [ ] `onUnload()` cleans up correctly (no memory leaks after switching tabs)
- [ ] All API calls use `this.api.get()` — no raw `fetch()` with manual auth headers

---

## 11. What NOT to Change

These things work correctly and should NOT be modified as part of this redesign:

| Item | Reason |
|------|--------|
| All Flask backend routes (`xero_routes.py`, `shopify_routes.py`, etc.) | Untouched — the redesign is frontend-only except for module catalog entries |
| `AI_infrastructure/routes/organisation_credentials_routes.py` | Org module API endpoints are complete and working |
| `AI_infrastructure/shared/org_credentials_loader.py` | `get_user_enabled_modules()` is correct |
| `AI_infrastructure/migrations/` | All migrations are applied. No schema changes needed for this redesign |
| `ui-standardization.css` | Already correct — components should extend it, not replace it |
| Tool definitions in `tools/` JSON files | Separate system from module UI redesign |
| Database schema | No changes needed — redesign is a frontend wiring exercise |
| The module catalog DB data (036 migration) | Correct as-is — just not yet read by the frontend |

---

## Key Files Reference

| File | Purpose | Status |
|------|---------|--------|
| `UI/business-ai-platform-v2.html` | Main SPA — add `initModulesFromOrg()`, `module-hidden` CSS, `data-module` attrs | To modify |
| `UI/shared/js/module-api.js` | Shared auth-aware fetch client | To create |
| `UI/shared/js/module-components.js` | Shared component factory functions | To create |
| `UI/shared/css/ui-standardization.css` | Design tokens CSS | Exists — use as-is |
| `UI/modules_external/xero/xero.js` | Gold standard migration target | To migrate |
| `UI/modules_external/manifest.json` | Static fallback (legacy) | Deprecate after Phase 2 |
| `AI_infrastructure/routes/organisation_credentials_routes.py` | All org API routes | Complete — do not change |
| `AI_infrastructure/shared/org_credentials_loader.py` | Module resolver | Complete — do not change |
| `AI_infrastructure/migrations/036_platform_module_catalog.sql` | DB module catalog | Applied — do not change |
| `AI_infrastructure/migrations/039_user_module_access.sql` | Per-user restrictions | Applied — do not change |

---

## Context for AI Agents Picking This Up

You are implementing a frontend wiring exercise. The backend is complete. The DB schema
is live. The API endpoints work. The only gap is that the frontend does not read the DB
to determine what to show in the sidebar.

**The single most important task is Phase 2 (Steps 4–8):** implementing
`initModulesFromOrg()` and wiring it to the login flow. This alone makes the entire
module system functional for real users. Everything in Phase 3–5 is quality/consistency
work that can be done incrementally.

**Do NOT:**
- Rewrite the existing Flask backend
- Change the database schema
- Rename or restructure existing working modules
- Remove manifest.json until Phase 2 is complete and tested

**DO:**
- Read `UI/shared/js/module-template-modern.js` and `example-modern-module.js` as
  reference implementations of the V4 pattern before writing any module JS
- Read `UI/shared/css/ui-standardization.css` before writing any module CSS
- Search for `MODULE_GATE_MAP` in `business-ai-platform-v2.html` — there is already
  partial gating logic that `initModulesFromOrg()` should replace or extend
- Search for `loadAndApplyOrgModules` in `business-ai-platform-v2.html` — there may
  already be a stub function to extend

**Start here:** Review `MODULE_GATE_MAP` in `business-ai-platform-v2.html` to understand
what gating already exists, then implement `initModulesFromOrg()` immediately below it.
