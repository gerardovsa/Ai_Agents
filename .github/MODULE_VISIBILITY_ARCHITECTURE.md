# Module Visibility Architecture
**Document Version: 1.0 — March 26, 2026**
**Status: Current architecture documented + design spec for proper implementation**

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current Sidebar — What Is Hardcoded](#2-current-sidebar--what-is-hardcoded)
3. [All Dashboards & Modules — Complete Inventory](#3-all-dashboards--modules--complete-inventory)
4. [How the Current Show/Hide System Works (and Gaps)](#4-how-the-current-showhide-system-works-and-gaps)
5. [Desired Architecture — Always-On vs Optional Modules](#5-desired-architecture--always-on-vs-optional-modules)
6. [Implementation Design — DB-Driven Sidebar Visibility](#6-implementation-design--db-driven-sidebar-visibility)
7. [Module Status Reference Table](#7-module-status-reference-table)
8. [How to Add a New Module to the Sidebar](#8-how-to-add-a-new-module-to-the-sidebar)

---

## 1. Executive Summary

The platform currently has **two separate, disconnected module systems**:

| System | Where | What It Does | Connected to Sidebar? |
|--------|-------|--------------|----------------------|
| `manifest.json` | `UI/modules_external/manifest.json` | Static JSON file — lists enabled modules | ✅ YES — drives `ModuleManager` + sidebar icons |
| DB Module Catalog | `ai_infrastructure.module_catalog` + `org_module_access` | DB-driven per-org toggles | ❌ NO — renders only in Org Settings panel, not the sidebar |

**The core problem:** The Org Settings > Modules panel lets admins toggle modules on/off per org — but that toggle data is never read to actually show or hide anything in the sidebar or main UI. The sidebar is driven by a static `manifest.json` file that is identical for every user.

**What needs to be built:** A `initModulesFromOrg()` function that reads `/api/org/modules` on login/org switch, then drives:
1. Which sidebar icons appear
2. Which `tab-content` divs are allowed to be accessed
3. Which hardcoded tabs (WooCommerce, Stock, etc.) are shown or hidden

---

## 2. Current Sidebar — What Is Hardcoded

### File: `UI/business-ai-platform-v2.html` — Lines ~18571–18640

The sidebar has **three zones**:

```
┌─────────────────────────────┐
│  ZONE 1: Fixed Core Items   │  ← Always visible, hardcoded HTML
│  (Lines 18574–18629)        │
├─────────────────────────────┤
│  ZONE 2: Dynamic Module     │  ← #sidebarModulesSection
│  Icons (Line 18632)         │  ← Populated by ModuleManager from manifest.json
├─────────────────────────────┤
│  ZONE 3: Fixed Bottom Items │  ← Calculator Tests + Settings (hardcoded)
│  (Lines 18636–18660)        │
└─────────────────────────────┘
```

### Zone 1 — Hardcoded Core Sidebar Items

| # | Label | Icon Class | Activation | Notes |
|---|-------|-----------|------------|-------|
| 1 | Home | `fas fa-home` | `data-action="home"` | Default active state |
| 2 | Communication Hub | `fas fa-comments` | `data-action="communication-hub"` | Always visible |
| 3 | **Sales & E-Commerce** | `fas fa-shopping-cart` | `data-tab="sales"` | ⚠️ **Opens WooCommerce — ALWAYS VISIBLE** |
| 4 | Analytics & Reports | `fas fa-chart-line` | `data-tab="analytics"` | Always visible |
| 5 | Universal Search | `fas fa-search` | `data-action="universal-search"` | Always visible |
| 6 | Transcription | `fas fa-microphone` | `data-action="transcription-sidebar"` | Always visible |
| 7 | Automation Workflows | `fas fa-project-diagram` | `data-tab="automation"` | Always visible |
| 8 | Command Centre | `fas fa-users` | `data-tab="multi-agent"` | Always visible |
| 9 | Synergy Suite | `fa-solid fa-hexagon-nodes-bolt` | `data-tab="synergy"` | Always visible; Socket.IO |
| 10 | Vector Database | `fas fa-database` | `data-action="vectordb"` | Always visible |

### Zone 2 — Dynamic Module Icons (`#sidebarModulesSection`)

Populated at runtime by `window.ModuleManager.initialize()` reading `modules_external/manifest.json`.

**Currently rendered icons (from manifest.json):**
- Production Workflow (InHouse Kanban) — `fas fa-industry` → opens `tab-inhouse-kanban`
- InHouse Print Tools — `fas fa-print`
- Quote Calculator — `fas fa-calculator`
- Stock Management — `fas fa-boxes` → opens `tab-stock`
- Xero Accounting — `fas fa-file-invoice-dollar`
- Shopify E-Commerce — `fab fa-shopify`
- Local Filesystem — `fas fa-folder-open`

### Zone 3 — Fixed Bottom Items

| Label | Icon | Notes |
|-------|------|-------|
| Calculator Tests | `fas fa-calculator` | `openCalculatorDashboard()` — no role gate in HTML |
| Settings | `fas fa-cog` | `window.openSettingsSidebar()` |

---

## 3. All Dashboards & Modules — Complete Inventory

### 3a. Tab-Content Panels in HTML (`tab-*` divs)

These are the actual rendered dashboard panels inside `UI/business-ai-platform-v2.html`:

| HTML Tab ID | Module Name | Sidebar Icon | Always Visible? | Notes |
|-------------|-------------|-------------|----------------|-------|
| `tab-home` | Home Dashboard | `fas fa-home` | ✅ Yes | Default active |
| `tab-communication` | Communication Hub | `fas fa-comments` | ✅ Yes | Core feature |
| `tab-inhouse-kanban` | Production Workflow (Kanban) | `fas fa-industry` (dynamic) | Via manifest.json | No org-gate |
| `tab-vsa-veterinary-alerts` | VSA Veterinary Alerts | None in sidebar | ❌ Inaccessible | Tab exists in HTML, **no sidebar button**, no route to open it |
| `tab-universal-search` | Universal Search | `fas fa-search` | ✅ Yes | Core feature |
| `tab-vector-database` | Vector Database | `fas fa-database` | ✅ Yes | Core feature |
| `tab-sales` | **WooCommerce Management** | `fas fa-shopping-cart` | ⚠️ **HARDCODED** | No visibility gate at all |
| `tab-analytics` | Analytics & Reports | `fas fa-chart-line` | ✅ Yes | Core feature |
| `tab-automation` | Automation Workflows | `fas fa-project-diagram` | ✅ Yes | Core feature |
| `tab-multi-agent` | Command Centre | `fas fa-users` | ✅ Yes | Socket.IO realtime |
| `tab-synergy` | Synergy Suite | `fa-hexagon-nodes-bolt` | ✅ Yes | Socket.IO realtime |
| `tab-stock` | Stock Management | `fas fa-boxes` (dynamic) | Via manifest.json | In HTML at line 19782 |

### 3b. Modules in `UI/modules_external/`

These folders exist on disk. Their code is loaded at Flask startup when discovered by `tools/module_plugin.py`.

| Folder | Module Name | Plan Tier (DB) | Implementation | Status |
|--------|-------------|---------------|----------------|--------|
| `inhouse-kanban/` | `inhouse_kanban` | Enterprise | Frontend JS only | ✅ Active |
| `inhouse-print/` | `inhouse_print` | Enterprise | Python backend + DB | ✅ Active, fixed Jan 2026 |
| `quote-calculator/` | `quote_calculator` | Enterprise | 80+ tools, full backend | ✅ Active |
| `stock-management/` | `stock_management` | Professional | Flask routes + Tabulator.js | ✅ Active |
| `xero/` | `xero` | Professional | OAuth2, Flask routes | ✅ Active |
| `shopify/` | `shopify` | Professional | Flask routes | ✅ Active |
| `auspost-shipping/` | `auspost_shipping` | Professional | Python tools | ✅ Active |
| `customer-reactivation/` | `customer_reactivation` | Professional | Python tools | ✅ Active |
| `database-visualizer/` | `database_visualizer` | Enterprise | Frontend stub only | ⚠️ Stub |
| `github/` | `github` | Enterprise | Frontend stub only | ⚠️ Stub |
| `render-management/` | `render_management` | Enterprise | Frontend stub only | ⚠️ Stub |
| `local-filesystem/` | `local_filesystem` | Enterprise | Nothing implemented | ❌ Planned |
| `dev-diagnostics/` | — | — | Empty tools file | ❌ Dev only |

### 3c. Modules Defined in DB Catalog Only (no folder)

These exist in `ai_infrastructure.module_catalog` (Migration 036) but have no `modules_external/` folder. They are built into the main HTML or not yet implemented.

| module_name | display_name | Plan Tier | Location in UI |
|-------------|-------------|-----------|----------------|
| `core_chat` | AI Chat | Free | Built into main HTML |
| `documents` | Documents | Free | Built into main HTML |
| `prompt_library` | Prompt Library | Free | Built into main HTML |
| `notifications` | Notifications | Free | Built into main HTML |
| `universal_search` | Universal Search | Starter | `tab-universal-search` in HTML |
| `synergy` | Synergy Suite | Starter | `tab-synergy` in HTML |
| `automation` | Automation | Starter | `tab-automation` in HTML |
| `thread_cards` | Thread Cards | Starter | Partially in main HTML |
| `transcription` | Voice Transcription | Professional | Action-based sidebar (no tab-content) |
| `vector_database` | Vector Search | Professional | `tab-vector-database` in HTML |
| `woocommerce` | WooCommerce | Enterprise | `tab-sales` in HTML — **HARDCODED** |

### 3d. VSA Veterinary Alerts — Orphaned Tab

**`tab-vsa-veterinary-alerts`** (HTML line 19202) is a fully rendered tab in the HTML that was built for a specific client (veterinary practice). It:
- Has no sidebar icon/button to navigate to it
- Has no entry in `manifest.json`
- Has no entry in `module_catalog`
- Is inaccessible to end users
- Should be gated behind a module flag and sidebar icon, or removed

---

## 4. How the Current Show/Hide System Works (and Gaps)

### 4a. `manifest.json` → `ModuleManager` → Sidebar Icons

**Flow:**
```
Page load
  → window.ModuleManager.initialize()
  → fetch('modules_external/manifest.json')
  → For each module where "enabled": true:
      → ModuleManager.addSidebarIcon(id, name, icon, color)
      → Creates <button data-moduleId="${id}"> in #sidebarModulesSection
  → User clicks icon
  → switchTab(moduleId) → shows tab-${moduleId}
```

**Problems with this system:**
1. `manifest.json` is a **static file** — it is the same for every user, every org, every role
2. Changing which modules are visible requires editing a file and redeploying
3. There is **no connection** between `manifest.json` and `ai_infrastructure.org_module_access`
4. A developer enabling a module in the DB Modules panel has **no effect** on what appears in the sidebar

### 4b. `data-org-min-role` Attribute Gating

**How it works:**
```javascript
// Runs on user profile load
document.querySelectorAll('[data-org-min-role]').forEach(el => {
    const required = el.getAttribute('data-org-min-role');
    if (roleLevel(user.org_role) < roleLevel(required)) {
        el.style.display = 'none';
    }
});
```

**What it covers:**
- AI Settings tab (manager+)
- Connections button (manager+)
- Security settings tab (admin+)
- Biometric settings (admin+)

**What it does NOT cover:**
- Any sidebar navigation items
- Any main tab-content panels
- Any module dashboard visibility

### 4c. Org Module Catalog in Settings Panel

The Org Settings > Modules subtab (`#org-subtab-modules`) shows module cards with enable/disable toggles. When toggled:
1. `OrgManager.toggleModule(name, enabled)` calls `PUT /api/org/modules/<name>`
2. Row is upserted in `ai_infrastructure.org_module_access`
3. **That's where it stops** — nothing reads this data to update the sidebar or hide tabs

### 4d. Current Visibility Control Map

```
┌────────────────────────────────────────────────────────────────┐
│  SIDEBAR CONTROL                                               │
│  Zone 1 (core): HARDCODED HTML — no control possible          │
│  Zone 2 (modules): manifest.json — static, same for everyone  │
│  Zone 3 (bottom): HARDCODED HTML — no control possible        │
├────────────────────────────────────────────────────────────────┤
│  TAB CONTENT CONTROL                                           │
│  switchTab(id): shows tabId by adding .active class           │
│  No visibility pre-check against org/role/module state        │
├────────────────────────────────────────────────────────────────┤
│  ORG MODULE TOGGLES (DB)                                       │
│  org_module_access: data stored but NEVER READ for UI         │
│  Only rendered in /org/modules settings panel                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 5. Desired Architecture — Always-On vs Optional Modules

### 5a. Always-On Modules (Core — Never Hidden)

These appear in the sidebar for ALL users regardless of org, role, or plan tier:

| Module | Sidebar Icon | Tab ID | Rationale |
|--------|-------------|--------|-----------|
| Communication Hub | `fas fa-comments` | `tab-communication` | Core AI chat interface |
| Command Centre | `fas fa-users` | `tab-multi-agent` | Core multi-agent coordination |
| Universal Search | `fas fa-search` | `tab-universal-search` | Core platform utility |
| Analytics & Reports | `fas fa-chart-line` | `tab-analytics` | Core operational visibility |
| Transcription | `fas fa-microphone` | (action panel) | Core AI utility |
| Synergy Suite | `fa-hexagon-nodes-bolt` | `tab-synergy` | Core real-time collaboration |
| Vector Database | `fas fa-database` | `tab-vector-database` | Core AI memory/search |
| Automation Workflows | `fas fa-project-diagram` | `tab-automation` | Core operational tool |

### 5b. Optional Modules (Org/Plan/Role Gated)

These should only appear in the sidebar when enabled for the org, not hardcoded:

| Module | Icon | Tab ID | Plan Tier | DB module_name | Currently |
|--------|------|--------|-----------|---------------|-----------|
| **WooCommerce Management** | `fas fa-shopping-cart` | `tab-sales` | Enterprise | `woocommerce` | ⚠️ **HARDCODED — always visible** |
| Production Workflow (Kanban) | `fas fa-industry` | `tab-inhouse-kanban` | Enterprise | `inhouse_kanban` | Via manifest.json |
| InHouse Print Tools | `fas fa-print` | (action) | Enterprise | `inhouse_print` | Via manifest.json |
| Quote Calculator | `fas fa-calculator` | (action/tab) | Enterprise | `quote_calculator` | Via manifest.json |
| Stock Management | `fas fa-boxes` | `tab-stock` | Professional | `stock_management` | Via manifest.json |
| Xero Accounting | `fas fa-file-invoice-dollar` | (action/tab) | Professional | `xero` | Via manifest.json |
| Shopify E-Commerce | `fab fa-shopify` | (action/tab) | Professional | `shopify` | Via manifest.json |
| AusPost Shipping | `fas fa-truck` | (TBD) | Professional | `auspost_shipping` | Not in sidebar |
| Customer Reactivation | `fas fa-user-plus` | (TBD) | Professional | `customer_reactivation` | Not in sidebar |
| Database Visualizer | `fas fa-project-diagram` | (TBD) | Enterprise | `database_visualizer` | Not in sidebar |
| GitHub | `fab fa-github` | (TBD) | Enterprise | `github` | Not in sidebar |
| Render Management | `fas fa-server` | (TBD) | Enterprise | `render_management` | Not in sidebar |
| VSA Veterinary Alerts | `fas fa-stethoscope` | `tab-vsa-veterinary-alerts` | Enterprise | (missing from DB) | **Orphaned tab** |

---

## 6. Implementation Design — DB-Driven Sidebar Visibility

### 6a. The Target Architecture

```
Login / Org Switch
  → GET /api/org/modules           (enabled module set for this org)
  → initModulesFromOrg(modules)
      → renderCoreSidebar()        (always-on items — hardcoded)
      → renderModuleSidebar()      (optional items from DB)
      → applyRoleGates()           (hide elements per org_role)
  → User clicks sidebar item
      → switchTab(id)              (no change needed)
```

### 6b. New Function: `initModulesFromOrg(enabledModules)`

```javascript
// Called on login and on org switch
// enabledModules: array of { module_name, display_name, icon_class, icon_color }
//   from GET /api/org/modules (filtered to is_enabled=true)

function initModulesFromOrg(enabledModules) {
    const enabledSet = new Set(enabledModules.map(m => m.module_name));

    // 1. Show/hide the WooCommerce tab (currently hardcoded)
    const salesNavBtn = document.querySelector('[data-tab="sales"]');
    const salesTab    = document.getElementById('tab-sales');
    const wcVisible   = enabledSet.has('woocommerce');
    if (salesNavBtn) salesNavBtn.style.display = wcVisible ? '' : 'none';
    if (salesTab)    salesTab.classList.toggle('module-hidden', !wcVisible);

    // 2. Show/hide other hardcoded optional tabs
    const OPTIONAL_TAB_MAP = {
        // module_name        : { tabId, sidebarSelector }
        'stock_management'    : { tabId: 'tab-stock',               selector: '[data-action="stock"]' },
        'inhouse_kanban'      : { tabId: 'tab-inhouse-kanban',      selector: '[data-action="inhouse-kanban"]' },
        'vsa_veterinary'      : { tabId: 'tab-vsa-veterinary-alerts', selector: '[data-action="vsa"]' },
    };
    for (const [moduleName, spec] of Object.entries(OPTIONAL_TAB_MAP)) {
        const visible = enabledSet.has(moduleName);
        const tab = document.getElementById(spec.tabId);
        const btn = document.querySelector(spec.selector);
        if (tab) tab.classList.toggle('module-hidden', !visible);
        if (btn) btn.style.display = visible ? '' : 'none';
    }

    // 3. Rebuild #sidebarModulesSection from live DB data instead of manifest.json
    const DYNAMIC_MODULES = [
        // modules rendered from DB, not manifest.json
        { module_name: 'inhouse_print',        tabId: null, action: 'inhouse-print' },
        { module_name: 'quote_calculator',     tabId: null, action: 'calculator-tests' },
        { module_name: 'xero',                 tabId: null, action: 'xero-dashboard' },
        { module_name: 'shopify',              tabId: null, action: 'shopify-dashboard' },
        { module_name: 'auspost_shipping',     tabId: null, action: 'auspost' },
        { module_name: 'customer_reactivation',tabId: null, action: 'customer-reactivation' },
        { module_name: 'database_visualizer',  tabId: null, action: 'database-visualizer' },
        { module_name: 'github',               tabId: null, action: 'github' },
        { module_name: 'render_management',    tabId: null, action: 'render-management' },
    ];
    
    const container = document.getElementById('sidebarModulesSection');
    if (!container) return;
    container.innerHTML = '';

    for (const def of DYNAMIC_MODULES) {
        if (!enabledSet.has(def.module_name)) continue;
        // Find catalog entry for icon/color/label
        const catalog = enabledModules.find(m => m.module_name === def.module_name) || {};
        const btn = document.createElement('button');
        btn.className = 'sidebar-icon-btn';
        btn.title = catalog.display_name || def.module_name;
        btn.dataset.action = def.action;
        btn.innerHTML = `<i class="${catalog.icon_class || 'fas fa-cube'}" style="color:${catalog.icon_color || '#6B7280'}"></i>`;
        container.appendChild(btn);
    }
}
```

### 6c. CSS — `module-hidden` Class

Add to the CSS section of `business-ai-platform-v2.html`:

```css
/* Module visibility — set by initModulesFromOrg() */
.tab-content.module-hidden {
    display: none !important;
}
```

### 6d. Wiring to Login Flow

Find the existing login success handler (where `AppState.user` is set) and add:

```javascript
// After successful login / org load:
const modulesResponse = await fetch(`${API_BASE_URL}/api/org/modules`, {
    headers: { 'Authorization': `Bearer ${token}` }
});
const modulesData = await modulesResponse.json();
if (modulesData.success) {
    initModulesFromOrg(modulesData.modules || []);
}
```

### 6e. `GET /api/org/modules` Response Schema

The existing endpoint returns:
```json
{
  "success": true,
  "modules": [
    {
      "module_name": "shopify",
      "display_name": "Shopify",
      "icon_class": "fab fa-shopify",
      "icon_color": "#96bf48",
      "category": "ecommerce",
      "min_plan_tier": "professional",
      "required_platforms": ["shopify"],
      "is_enabled": true
    }
  ]
}
```
Filter client-side to `is_enabled === true` before passing to `initModulesFromOrg()`.

---

## 7. Module Status Reference Table

Complete reference combining sidebar visibility, HTML presence, code status, and DB catalog status.

| Module | Sidebar Zone | HTML Tab | modules_external/ | DB module_name | Plan Tier | Hide/Show | Action Needed |
|--------|-------------|----------|-------------------|---------------|-----------|-----------|---------------|
| **Communication Hub** | Zone 1 Core | `tab-communication` | ❌ Built-in | `core_chat` | Free | Always On | None |
| **Command Centre** | Zone 1 Core | `tab-multi-agent` | ❌ Built-in | none | Free | Always On | None |
| **Analytics & Reports** | Zone 1 Core | `tab-analytics` | ❌ Built-in | none | Free | Always On | None |
| **Universal Search** | Zone 1 Core | `tab-universal-search` | ❌ Built-in | `universal_search` | Starter | Always On | None |
| **Transcription** | Zone 1 Core | action panel | ❌ Built-in | `transcription` | Professional | Always On | None |
| **Automation Workflows** | Zone 1 Core | `tab-automation` | ❌ Built-in | `automation` | Starter | Always On | None |
| **Synergy Suite** | Zone 1 Core | `tab-synergy` | ❌ Built-in | `synergy` | Starter | Always On | None |
| **Vector Database** | Zone 1 Core | `tab-vector-database` | ❌ Built-in | `vector_database` | Professional | Always On | None |
| **WooCommerce** | Zone 1 Core ⚠️ | `tab-sales` | ❌ Built-in | `woocommerce` | Enterprise | **MUST BE OPTIONAL** | Gate behind `org_module_access` |
| **Production Workflow** | Zone 2 Dynamic | `tab-inhouse-kanban` | `inhouse-kanban/` | `inhouse_kanban` | Enterprise | Optional | Replace manifest.json with DB |
| **InHouse Print** | Zone 2 Dynamic | (action) | `inhouse-print/` | `inhouse_print` | Enterprise | Optional | Replace manifest.json with DB |
| **Quote Calculator** | Zone 3 Bottom | (action) | `quote-calculator/` | `quote_calculator` | Enterprise | Optional | Replace manifest.json with DB |
| **Stock Management** | Zone 2 Dynamic | `tab-stock` | `stock-management/` | `stock_management` | Professional | Optional | Replace manifest.json with DB |
| **Xero Accounting** | Zone 2 Dynamic | (action/tab) | `xero/` | `xero` | Professional | Optional | Replace manifest.json with DB |
| **Shopify E-Commerce** | Zone 2 Dynamic | (action/tab) | `shopify/` | `shopify` | Professional | Optional | Replace manifest.json with DB |
| **AusPost Shipping** | ❌ Not in sidebar | ❌ No tab | `auspost-shipping/` | `auspost_shipping` | Professional | Optional | Add sidebar icon + tab |
| **Customer Reactivation** | ❌ Not in sidebar | ❌ No tab | `customer-reactivation/` | `customer_reactivation` | Professional | Optional | Add sidebar icon + tab |
| **Database Visualizer** | ❌ Not in sidebar | ❌ No tab | `database-visualizer/` | `database_visualizer` | Enterprise | Optional | Stub — add when ready |
| **GitHub** | ❌ Not in sidebar | ❌ No tab | `github/` | `github` | Enterprise | Optional | Stub — add when ready |
| **Render Management** | ❌ Not in sidebar | ❌ No tab | `render-management/` | `render_management` | Enterprise | Optional | Stub — add when ready |
| **VSA Veterinary Alerts** | ❌ No sidebar btn | `tab-vsa-veterinary-alerts` | (built-in) | ❌ Not in DB | — | Optional | Add to DB + sidebar OR remove tab |
| **Local Filesystem** | Zone 2 Dynamic | ❌ No tab | `local-filesystem/` | `local_filesystem` | Enterprise | Optional | Not implemented |

---

## 8. How to Add a New Module to the Sidebar

### Step 1: Create the HTML Tab Panel

In `UI/business-ai-platform-v2.html`, add a new `tab-content` div in the main content area:

```html
<!-- Add after the last tab-content div, before closing .main-content -->
<div class="tab-content" id="tab-my-module">
    <div style="padding: 24px;">
        <h2><i class="fas fa-my-icon" style="color: #HEX;"></i> My Module</h2>
        <!-- Module content here -->
    </div>
</div>
```

### Step 2: Add to `ai_infrastructure.module_catalog` (DB)

```sql
INSERT INTO ai_infrastructure.module_catalog (
    module_name, display_name, description, icon_class, icon_color,
    category, min_plan_tier, required_platforms, sort_order
) VALUES (
    'my_module', 'My Module', 'Description of what it does',
    'fas fa-my-icon', '#HEX',
    'operations', 'professional', '{}', 45
);
```

### Step 3: Enable for the Org (Admin Action)

Via Org Settings > Modules panel (toggle ON), or via SQL:
```sql
INSERT INTO ai_infrastructure.org_module_access (organisation_id, module_name, is_enabled, enabled_at)
VALUES (1, 'my_module', TRUE, NOW())
ON CONFLICT (organisation_id, module_name) DO UPDATE SET is_enabled = TRUE;
```

### Step 4: Add to `DYNAMIC_MODULES` in `initModulesFromOrg()`

```javascript
{ module_name: 'my_module', tabId: 'tab-my-module', action: 'my-module' },
```

### Step 5: Wire the sidebar button click to `switchTab`

The `initModulesFromOrg()` function creates buttons with `data-action="my-module"`. The existing sidebar click handler calls:
```javascript
switchTab('my-module'); // which shows tab-my-module
```

### Step 6: Create the `modules_external/my-module/` folder (if backend tools needed)

Follow the Module Plugin System pattern documented in `copilot-instructions.md`.

---

## Key Files Reference

| File | Location | Purpose |
|------|----------|---------|
| Main HTML | `UI/business-ai-platform-v2.html` | Sidebar HTML zones, all tab-content panels |
| Module manifest | `UI/modules_external/manifest.json` | **Current** (static) module loader — to be replaced |
| Module catalog | `AI_infrastructure/migrations/036_platform_module_catalog.sql` | DB-driven module definitions |
| Module routes | `AI_infrastructure/routes/organisation_credentials_routes.py` | `/api/org/modules` endpoint |
| Module access table | `AI_infrastructure/migrations/032_org_module_access.sql` | Per-org enable/disable storage |

---

## Change History

| Date | Change | Author |
|------|--------|--------|
| March 26, 2026 | Document created — full audit of current architecture, gap analysis, design spec for DB-driven visibility | AI Agents dev session |

---

*Next step: Implement `initModulesFromOrg()` in `business-ai-platform-v2.html` and gate `tab-sales` (WooCommerce) behind `woocommerce` module flag.*
