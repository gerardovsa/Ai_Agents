# Module Visibility Architecture
**Document Version: 1.3 — May 28, 2026**
**Status: IMPLEMENTATION COMPLETE. `initModulesFromOrg()` built and live (May 2026). Personal org subtab gating implemented (May 28, 2026). Tab-vsa-veterinary-alerts removed (Apr 8). Vector DB sidebar gating done (Apr 29). Account identity panel done (Apr 30).**

> **Cross-reference:** Credentials/vault/role hierarchy → `ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
1b. [The 4-Layer Visibility Model](#1b-the-4-layer-visibility-model)
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

**✅ IMPLEMENTED (May 2026):** `initModulesFromOrg()` reads `/api/org/modules` on login and org switch, then drives:
1. Which Zone 1 sidebar buttons appear (`data-module` attribute gating)
2. Which Zone 2 module icons appear (rebuilt from DB catalog data)
3. Whether team-management subtabs (Members, Invitations) are visible for personal orgs

---

## 1b. The 4-Layer Visibility Model

Modules are **conditionally displayed and functional** based on four independent layers of gating. All must permit access for a module to be fully functional.

### Layer 1: Organisation Level

- **Table**: `ai_infrastructure.org_module_access`
- **Control**: Admin toggles module on/off per organisation
- **Example**: Customer A enables Xero module, Customer B disables it
- **What shows**: If disabled, module tab is hidden in sidebar
- **Gating Code**: `if (!enabledModules.includes('xero')) { hideTab('tab-xero'); }`

### Layer 2: User Role Level

- **Column**: `ai_infrastructure.users.org_role`
- **Hierarchy**: `viewer (1) < member (2) < manager (3) < admin (4) < owner (5)`
- **Pattern**: `data-org-min-role="admin"` attributes on sidebar buttons gate by role
- **Example**: Viewers can't see Credentials vault or Settings tabs; only managers+ can manage them
- **Gating Code**: `if (roleLevel < requiredRoleLevel) { hideTab(); }`

### Layer 3: Team / Sub-User System

- **Columns**: `parent_user_id`, `is_sub_user` on `ai_infrastructure.users` table
- **Rule**: Sub-users inherit parent's enabled modules but operate within their own role level
- **Example**: Parent (owner) creates sub-user (viewer):
  - Sub-user CAN see enabled module tabs (parent has them enabled in org)
  - Sub-user CAN'T edit credentials (viewer role prevents writing)
  - Sub-user CAN'T create automations (viewer role prevents advanced features)
- **Gating Code**: `if (profile.is_sub_user && org_role === 'viewer') { restrictAccessToReadOnly(); }`

### Layer 4: Module-Specific Requirements

- **Column**: `ai_infrastructure.module_catalog.required_platforms`
- **Rule**: Module requires specific platform credentials to function
- **Example**: Xero module requires `xero` platform credential in organisation vault
- **What shows**:
  - If credential exists: tab fully functional
  - If credential missing: tab shows "Configuration Required" message with setup instructions
- **Gating Code**: `if (!vaultHasCredential('xero')) { showConfigurationRequired(); return; }`

### How Layers Combine — The Decision Tree

A module is **fully accessible** only if ALL four layers permit it:

```
Evaluation Order:

1. Is module in org_module_access AND is_enabled = TRUE?
   ├─ NO  → HIDE TAB
   └─ YES ↓

2. Is user's org_role high enough to see this tab?
   ├─ NO  → HIDE TAB
   └─ YES ↓

3. Is user a sub-user with role-based restrictions?
   ├─ YES & role='viewer' → RESTRICT TO READ-ONLY ACCESS
   └─ NO or higher role ↓

4. Does module require credentials? Are they in org vault?
   ├─ REQUIRED & MISSING → SHOW "CONFIGURATION REQUIRED"
   ├─ REQUIRED & EXISTS  → FULLY ACCESSIBLE ✓
   └─ NOT REQUIRED       → FULLY ACCESSIBLE ✓
```

### Related Documentation

- **Section 5**: How `org_module_access` (Layer 1) is managed via Org Settings
- **`ORG_DOCUMENTATION_AND_UI_ALIGNMENT_SUMMARY_MAR28_2026.md`**: Complete role hierarchy details (Layer 2) and user table schema
- **`ORG_CREDENTIALS_MASTER_ANALYSIS.md`**: Sub-user system and credential vault architecture (Layer 3 + 4)
- **Section 7** (Module Status Table): Module-specific requirements and plan tier constraints (Layer 4)

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
| 10 | Vector Database | `fas fa-database` | `data-action="vectordb"` | ⚠️ **Hardcoded always-visible — should be Professional plan gated** |

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
| `tab-vector-database` | Vector Database | `fas fa-database` | ⚠️ **Hardcoded** | Should require `vector_database` module (Professional tier) + Pinecone credential |
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

### 3d. VSA Veterinary Alerts — ✅ REMOVED

**`tab-vsa-veterinary-alerts`** was a client-specific tab that had no sidebar button and was inaccessible to users. It was **removed from `business-ai-platform-v2.html` on April 8, 2026**. The `vsa_veterinary` entry was also removed from the `OPTIONAL_TAB_MAP` in `initModulesFromOrg()`. No further action needed.

> **Note:** `VSA_API_BASE_URL` references that remain in the HTML (pointing to `vsa-agent-service.onrender.com`) are for a separate VSA automation agent service — unrelated to the veterinary tab.

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
3. **✅ CONNECTED (May 2026):** On next login / page load, `initModulesFromOrg()` calls `GET /api/org/modules` and reflects the updated state in the sidebar

### 4d. Current Visibility Control Map

```
┌────────────────────────────────────────────────────────────────┐
│  SIDEBAR CONTROL (May 2026 — IMPLEMENTED)                      │
│  Zone 1 (core): data-module gated by initModulesFromOrg()     │
│  Zone 2 (modules): DB-driven, rebuilt from org_module_access  │
│  Zone 3 (bottom): HARDCODED HTML — no control possible        │
├────────────────────────────────────────────────────────────────┤
│  TAB CONTENT CONTROL                                           │
│  switchTab(id): shows tabId by adding .active class           │
│  Zone 1 buttons hidden means tabs unreachable (no direct URL) │
├────────────────────────────────────────────────────────────────┤
│  ORG SETTINGS SUBTAB GATING                                    │
│  _gateOrgSubTabs(): role-based (vault/modules/audit)          │
│  + personal org: hides Members + Invitations subtabs          │
├────────────────────────────────────────────────────────────────┤
│  ORG MODULE TOGGLES (DB) — ✅ CONNECTED (May 2026)             │
│  org_module_access → GET /api/org/modules → initModulesFromOrg│
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
| Automation Workflows | `fas fa-project-diagram` | `tab-automation` | Core operational tool |

### 5b. Optional Modules (Org/Plan/Role Gated)

These should only appear in the sidebar when enabled for the org, not hardcoded:

| Module | Icon | Tab ID | Plan Tier | DB module_name | Currently |
|--------|------|--------|-----------|---------------|-----------|
| **Vector Database** | `fas fa-database` | `tab-vector-database` | Professional | `vector_database` | ✅ **Gated** — `data-module="vector_database"` on sidebar button; hidden by `initModulesFromOrg()` if not enabled |
| **WooCommerce Management** | `fas fa-shopping-cart` | `tab-sales` / `tab-sales-v4` | Enterprise | `woocommerce` | ✅ **Gated** — both WooCommerce buttons have `data-module="woocommerce"`; hidden by `initModulesFromOrg()` |
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

## 6. Implementation — DB-Driven Sidebar Visibility

> **Status: IMPLEMENTED (May 2026).** The design below was executed. Actual implementation differs slightly from the spec — see notes at end of section.

### 6a. The Implemented Architecture

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

### 6d. Login Flow (As Implemented)

In `business-ai-platform-v2.html` `loadUserInfo()` (around line 30688):

```javascript
// After /api/org/modules fetch:
if (data.success && window.initModulesFromOrg) {
    const _effectiveRole = /* org_role or 'platform_developer' */;
    window.initModulesFromOrg(data.modules || [], _effectiveRole, window._orgInfo || null);
}
```

**Actual signature:** `initModulesFromOrg(modules, userRole, orgInfo)` — 3 parameters, not 2.
- `userRole` enables `platform_developer` super-role (sees all modules regardless of org settings)
- `orgInfo` carries `is_personal_org` flag for team-management subtab gating

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
| **Vector Database** | Zone 1 Core | `tab-vector-database` | ❌ Built-in | `vector_database` | Professional | Optional | ✅ Done (Apr 29) — `data-module="vector_database"` gated by `initModulesFromOrg()` |
| **WooCommerce (Legacy + V4)** | Zone 1 Core | `tab-sales`, `tab-sales-v4` | ❌ Built-in | `woocommerce` | Enterprise | Optional | ✅ Done (May 2026) — both buttons have `data-module="woocommerce"` |
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
| **VSA Veterinary Alerts** | ❌ Removed | ❌ Removed | N/A | ❌ Not in DB | — | N/A | ✅ Done (Apr 8) — Tab div + sidebar entry removed from HTML |
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
| May 28, 2026 | **Personal org subtab gating:** `_gateOrgSubTabs()` extended to hide Members + Invitations subtab buttons when `window._orgIsPersonal=TRUE`. `initModulesFromOrg()` Step 3 added: hides Members + Invitations buttons for personal orgs using `isPersonalOrg` flag. The `isPersonalOrg` variable was computed but not acted on until this fix. | AI Agents dev session |
| May 2026 | **`initModulesFromOrg()` IMPLEMENTED:** Zone 1 module gating via `data-module` attributes; Zone 2 rebuilt from DB catalog data (replaces `manifest.json`). Called from `loadUserInfo()` after `GET /api/org/modules`. Accepts `(modules, userRole, orgInfo)`. `platform_developer` super-role sees all modules. `is_personal_org` flag passed via `orgInfo`. Both WooCommerce sidebar buttons (`tab-sales` + `tab-sales-v4`) have `data-module="woocommerce"`. | AI Agents dev session |
| April 30, 2026 | Added `#account-identity-panel` to account sidebar header: colour-coded org role badge + live org name + team sub-account amber notice + platform developer blue notice. `_updateIdentityPanel()` method in `AccountSidebar`. `sidebarTeamBadge` replaced by this panel. | AI Agents dev session |
| April 29, 2026 | Vector DB sidebar button gated: `data-module="vector_database"` + `id` added to `business-ai-platform-v2.html`. pgvector as default provider. Migrations 044 (pgvector table) + 045 (catalog updates) confirmed running. | AI Agents dev session |
| April 8, 2026 | `tab-vsa-veterinary-alerts` div removed from `business-ai-platform-v2.html`. `vsa_veterinary` removed from JS module map. | AI Agents dev session |
| April 8, 2026 | Accept-invite frontend fully implemented; `execute_query()` DML bugs fixed; recursive trigger fixed (migration 041); `POST /api/org/invite` rewritten with provider field | AI Agents dev session |
| March 28, 2026 | Added Section 1b: The 4-Layer Visibility Model + cross-references to org system docs | AI Agents dev session |
| March 26, 2026 | Document created — full audit of current architecture, gap analysis, design spec for DB-driven visibility | AI Agents dev session |

---

## Cross-Document References

For complete information on the Organisation system that governs module visibility, see:

- **[ORG_DOCUMENTATION_AND_UI_ALIGNMENT_SUMMARY_MAR28_2026.md](../ORG_DOCUMENTATION_AND_UI_ALIGNMENT_SUMMARY_MAR28_2026.md)** — Complete organisation table schema (20 columns), all 4 migrations, UI form mappings, API endpoints
- **[ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md](./ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md)** — Multi-tenancy architecture, credential vault, role hierarchy, RLS policies, sub-user system, personal org, 4-tier credential resolution, bug audit
- **[../copilot-instructions.md](../copilot-instructions.md)** — Org/Platform/Module system reference (Section: Org, Team, Roles, Platform Catalog & Module System)

---

*Next step: Implement `initModulesFromOrg()` in `business-ai-platform-v2.html` and gate `tab-sales` (WooCommerce) behind `woocommerce` module flag.*

---

## Changelog & TODO

### Last Updated: April 30, 2026

#### Recent Changes
- ✅ **April 30** — `#account-identity-panel` added to account sidebar header: surfaces `org_role` as a colour-coded pill (viewer=grey, member=green, manager=blue, admin=amber, owner=purple) + live org display name fetched async from `/api/org/info`. Team sub-accounts get amber border + scope notice. Platform developers get blue border. `_updateIdentityPanel(profile)` method added to `AccountSidebar`; called from `loadUserInfo()` after profile fetch. `sidebarTeamBadge` (always-hidden) retired in favour of this panel.
- ✅ **April 29** — Vector DB sidebar button gated with `data-module="vector_database"` and `id="sidebar-vector-db"` in `business-ai-platform-v2.html` (GAP-V7/V8).
- ✅ **April 29** — pgvector dual-provider: `_get_vector_provider()` auto-routes to pgvector when no Pinecone credential in org vault. Migration 044 (pgvector table + RLS + HNSW cosine index), Migration 045 (catalog update). `pgvector_tools.py` with 6 tool functions.
- ✅ **April 29** — All Vector DB security gaps resolved (GAP-V1 through GAP-V8): `@require_auth` on all routes, `g.rls_user_id` throughout, `resolve_credentials()` for Pinecone + embeddings, org-scoped namespaces, Settings-tab form returns 410.
- ✅ **April 8** — Accept-invite frontend fully implemented: `checkPendingInvite()`, `handleAcceptInvite()`, `_showInviteAcceptDialog()`, `_showInviteNotice()` added to `account_profile.js`; `?accept_invite=<token>` URL param detection + `sessionStorage` stash wired into all three `initializeApp()` login paths (email/password, OAuth callback, stored token)
- ✅ **April 8** — Core `execute_query()` framework fix in `database_utils.py`: DML without RETURNING no longer raises `ProgrammingError`; INSERT+RETURNING now correctly auto-commits (eliminates phantom INSERTs silently rolled back by `PooledConnection.close()`)
- ✅ **April 8** — Recursive DB trigger `trg_expire_invitations` fixed: added `WHEN (pg_trigger_depth() = 0)` guard; prevents "stack depth limit exceeded" on any `org_invitations` INSERT/UPDATE; applied to production Supabase; migration `041_fix_invite_trigger_recursion.sql` created
- ✅ **April 8** — `POST /api/org/invite` rewritten with `provider` field (`gmail`/`outlook`/none): sends invite email inline via user's stored OAuth token; returns `email_sent`/`email_error`; HTML invite form updated with "Send via" `<select id="inviteProvider">` dropdown; `inviteOrgMember()` JS updated for provider/email UX
- ✅ **March 26** — BUG-5: Added missing InHouse Kanban sidebar button with `data-module="inhouse_kanban"` attribute so org module toggle can actually hide it
- ✅ **March 26** — BUG-6: Added `_gateOrgSubTabs(role)` function — hides Vault/Modules/Audit org panel buttons based on `org_role` (Vault: manager+, Modules: member+, Audit: admin+)
- ✅ **March 26** — BUG-1–4: Missing auth headers on all `/api/org/*` calls, user role always showing "—" (`your_role` at wrong response nesting), `auth_token` key typos in `account_profile.js` and `business-ai-platform-v2.html` — all fixed
- ✅ **March 26** — Per-user module access (Migration 039): `user_module_access` table, `get_user_enabled_modules()` resolver (applies user restrictions on top of org-level set), member puzzle-piece toggle UI in Members panel; `GET /api/org/modules` now returns user-personalised filtered set
- ✅ **March 28** — Added Section 1b: "The 4-Layer Visibility Model" with full evaluation decision tree
- ✅ **March 28** — Consolidated to 3 core documents; removed duplicate analysis files; cross-references added

#### TODO

- [ ] **HIGH** — Implement `initModulesFromOrg()` function in `business-ai-platform-v2.html`
  - Full implementation spec in Section 6 of this document (function body provided, CSS class defined)
  - Calls `GET /api/org/modules` on login — response is already user-personalised (per-user restrictions applied backend-side)
  - Zone 1: shows/hides WooCommerce + other optional hardcoded sidebar items
  - Zone 2: rebuilds `#sidebarModulesSection` from live DB catalog data (replaces `manifest.json`)

- [ ] **HIGH** — Gate WooCommerce `tab-sales` sidebar button + tab content
  - Add `data-module="woocommerce"` to the sidebar `<li>` button
  - Add `module-hidden` CSS class logic for `#tab-sales` content div
  - Should be invisible unless org has `woocommerce` enabled in `org_module_access`

- [ ] **MEDIUM** — Replace `manifest.json` Zone 2 rendering with DB-driven module loading
  - InHouse Kanban sidebar button was added (BUG-5 ✅) but still rendered via static `manifest.json`
  - Target: `initModulesFromOrg()` rebuilds `#sidebarModulesSection` from live DB data

- [ ] **MEDIUM** — Add role-based `data-org-min-role` gating to sidebar nav items
  - Org panel subtab gating done (BUG-6 ✅)
  - Sidebar navigation items (Settings, Credentials, etc.) still have no per-role visibility gate

- [ ] **LOW** — Resolve orphaned `tab-vsa-veterinary-alerts`
  - Either: add `module_catalog` entry + sidebar button + `data-module` attribute
  - Or: delete the HTML tab entirely (it is currently inaccessible to all users)

#### Related Files (Keep These 3 as Source of Truth)
- `../ORG_CREDENTIALS_MASTER_ANALYSIS.md` — Credentials, vault, role hierarchy, sub-user system
- `../ORG_DOCUMENTATION_AND_UI_ALIGNMENT_SUMMARY_MAR28_2026.md` — Organisation table schema, UI forms
- This file — Module visibility model, implementation design, sidebar gating logic
