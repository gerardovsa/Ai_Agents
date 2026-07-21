/**
 * FILE: UI/modules_external/vsa-veterinary-alerts/vsa-veterinary-alerts.js
 * MODULE TYPE: external
 * ARCHITECTURE: Framework-modern V4 (Composition pattern) — mirrors WooCommerce V4
 *
 * PURPOSE:
 *   External V4 rewrite of the VSA Veterinary Alerts module.
 *   Previously lived at UI/modules_external/vsa-veterinary-alerts/ in an older
 *   checkout, as a global-scope script that hardcoded Supabase credentials in the
 *   browser and bypassed RLS. This version is an ES Module with proper lifecycle
 *   hooks, uses the shared ModuleAPI client for all fetch calls, and uses
 *   module-components for UI building blocks.
 *
 * TAB: #tab-vsa-veterinary-alerts
 *
 * SUB-TABS (this iteration):
 *   dashboard      → KPI cards (open alerts, follow-ups, calls today, avg risk)
 *                    LIVE: sourced from GET /api/vsa-supabase-proxy/dashboard,
 *                    which queries the external Supabase project's
 *                    call_manager_alerts + veterinary_calls tables server-side.
 *   calls          → Tabulator table of phone calls (LIVE)
 *                    sourced from GET /api/vsa-supabase-proxy/calls with
 *                    limit/offset pagination, joined with alert severity.
 *   cloud-folders  → Connect Google Drive / OneDrive folder sync (placeholder,
 *                    wired up in a later iteration — platform already has
 *                    /api/cloud-folder-sync)
 *   analysis       → Manual + auto analysis triggers (placeholder — the 21-stage
 *                    call analysis pipeline lives in the external Supabase project
 *                    and is not ported yet)
 *
 * SECURITY / SECRETS:
 *   - NO direct Supabase calls from the browser. ALL data fetches go through
 *     this.api (ModuleAPI), which auto-injects the JWT from localStorage and
 *     surfaces 401s via the 'module:auth-expired' window event.
 *   - NO hardcoded API keys. The external Supabase URL + service-role key now
 *     live in ai_infrastructure.organisation_platform_credentials (the
 *     'supabase_vsa' row), resolved server-side per request by the new
 *     vsa_supabase_proxy_routes blueprint.
 *   - manifest.settings no longer carries the Supabase URL/key (removed on
 *     migration to the vault).
 *   - If the vault has no row for the user's org, the proxy returns a
 *     503 with a "Configuration Required" message. The module renders a
 *     guided empty-state instead of failing silently.
 *
 * MIGRATION NOTES:
 *   - All credentials now sourced via resolve_credentials('supabase_vsa', user_id=g.rls_user_id)
 *     in vsa_supabase_proxy_routes._get_vsa_supabase_creds(). First-hits are
 *     user / sub-user / org vault (org-vault is where they belong);
 *     env-var fallback is intentionally NOT wired (CLAUDE.md §13 risk #13
 *     forbids new os.getenv() callers for platform keys).
 *   - The 21-stage analysis pipeline: port from the external Supabase project
 *     into a backend service under AI_infrastructure/services/vsa/ (separate ticket).
 *
 * LAST MODIFIED: 2026-07-22 — Wired Dashboard + Calls tabs to /api/vsa-supabase-proxy/* (vault-resolved, server-side)
 *
 * VISIBILITY (per .github/MODULE_VISIBILITY_ARCHITECTURE.md, 4-Layer Model):
 *   Layer 1 — Org toggle:           ai_infrastructure.org_module_access
 *                                    Admin toggles in Org Settings > Modules.
 *                                    Wired by initModulesFromOrg() at SPA line ~31435
 *                                    which calls enabledSet.has('vsa_veterinary') to
 *                                    gate the Zone 2 sidebar button (built from
 *                                    ZONE2_MODULES at line ~31463, my entry added at ~31477).
 *   Layer 2 — Role gate:            NOT set on VSA (consistent with other Zone 2 modules).
 *                                    Add data-org-min-role="manager" to the VSA button
 *                                    creation if a stricter gate is needed.
 *   Layer 3 — Sub-user inheritance: Parent org's enabled modules are inherited.
 *                                    Sub-users with viewer role get read-only access.
 *   Layer 4 — Required platforms:   Catalog row (migration 037) declares
 *                                    required_platforms = ARRAY['supabase_vsa'].
 *                                    No UI gate yet — module loads but data fetches
 *                                    will 401/404 until org vault has the credential.
 *                                    Future: add a "Configuration Required" gate here.
 *
 *   PLAN TIER:  min_plan_tier = 'enterprise' (migration 037).
 *               Server-side /api/org/modules filters by plan tier.
 *
 *   SIDEBAR COLOR: #10B981 — sourced from ai_infrastructure.module_catalog.icon_color.
 *                  Must match the GREEN constant below for visual consistency.
 */

import { ModuleAPI } from '/shared/js/module-api.js';
import {
    createKpiCard,
    updateKpiCard,
    createKpiGrid,
    createLoadingSpinner,
    createEmptyState,
    createErrorMessage,
} from '/shared/js/module-components.js';

// ─────────────────────────────────────────────────────────────────────────────
// Constants
// ─────────────────────────────────────────────────────────────────────────────

// Must match ai_infrastructure.module_catalog.icon_color for 'vsa_veterinary'
// (migration 037). The sidebar button color is sourced from the DB catalog row
// at runtime — keeping this constant aligned ensures in-module accents match.
const GREEN = '#10B981';

const SUB_TABS = [
    { id: 'dashboard',     label: 'Dashboard' },
    { id: 'calls',         label: 'Calls' },
    { id: 'cloud-folders', label: 'Cloud Folders' },
    { id: 'analysis',      label: 'Analysis' },
];

// ─────────────────────────────────────────────────────────────────────────────
// Module definition
// ─────────────────────────────────────────────────────────────────────────────

export default {

    // ── Injected utilities ──────────────────────────────────────────────────
    api: null,      // ModuleAPI instance
    log: null,      // console-prefixed logger (or console)
    notify: null,   // showNotification(msg, type) from host page

    // ── State ────────────────────────────────────────────────────────────────
    container: null,        // #tab-vsa-veterinary-alerts
    activeSubTab: 'dashboard',
    callsTable: null,       // Tabulator instance for the Calls sub-tab

    // ── Lifecycle ────────────────────────────────────────────────────────────

    /**
     * Called by the module loader when the user activates this tab.
     * @param {object} utilities  - { api, storage, events, dom, log }
     */
    async onDashboardLoad(utilities) {
        // 1. Wire up utilities
        this.api    = new ModuleAPI({ moduleId: 'vsa_veterinary' });
        this.log    = utilities?.log ?? { info: console.log, warn: console.warn, error: console.error };
        this.notify = window.showNotification ?? ((m, t) => console.log(`[notify:${t}] ${m}`));

        this.log.info('VSA Veterinary Alerts V4 loading...');

        // 2. Locate container
        this.container = document.getElementById('tab-vsa-veterinary-alerts');
        if (!this.container) {
            this.log.error('Container #tab-vsa-veterinary-alerts not found');
            return;
        }

        // 3. Render shell
        this._renderShell();

        // 4. Wire sub-tab buttons
        this._bindSubTabs();

        // 5. Auto-load the active sub-tab
        this._switchSubTab('dashboard');
    },

    /**
     * Called when the user navigates away from this tab (if loader supports it).
     * Mandatory cleanup to avoid Tabulator memory leaks on repeat visits.
     */
    onUnload() {
        this._destroyCallsTable();
        this.log?.info('VSA Veterinary Alerts V4 unloaded');
    },

    // ─────────────────────────────────────────────────────────────────────────
    // Shell rendering
    // ─────────────────────────────────────────────────────────────────────────

    _renderShell() {
        const subTabsHtml = SUB_TABS.map(t => `
          <button data-vsav4-subtab="${t.id}"
            style="padding:8px 18px; border:none; border-radius:6px 6px 0 0; cursor:pointer; font-size:13px; font-weight:600;
                   background:var(--bg-tertiary,#161b22); color:var(--text-secondary); transition:all 0.2s;"
            onmouseover="if(!this.classList.contains('active')){this.style.background='${GREEN}22'; this.style.color='${GREEN}';}"
            onmouseout="if(!this.classList.contains('active')){this.style.background='var(--bg-tertiary,#161b22)'; this.style.color='var(--text-secondary)';}"
          >${t.label}</button>
        `).join('');

        const panelsHtml = SUB_TABS.map(t => `
          <div id="vsav4-content-${t.id}" class="vsav4-subtab-content" style="display:none;"></div>
        `).join('');

        this.container.innerHTML = `
<div class="vsa-veterinary-dashboard" style="padding: var(--space-4, 16px);">

  <!-- Header -->
  <div style="display:flex; align-items:center; gap:12px; margin-bottom:var(--space-4,16px);">
    <i class="fas fa-stethoscope" style="font-size:32px; color:${GREEN};"></i>
    <div>
      <h2 style="margin:0; font-size:22px; font-weight:700; color:var(--text-primary);">VSA Veterinary Alerts</h2>
      <span style="font-size:12px; color:var(--text-secondary);">V4 External Module &mdash; Clinical Phone-Call Analysis</span>
    </div>
    <span style="margin-left:auto; font-size:11px; background:${GREEN}22; color:${GREEN}; padding:4px 10px; border-radius:12px; font-weight:600;">V4 BETA</span>
  </div>

  <!-- Sub-tab bar -->
  <div id="vsav4-subtab-bar" style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:var(--space-4,16px); border-bottom:2px solid var(--border-color,#30363d); padding-bottom:8px;">
    ${subTabsHtml}
  </div>

  <!-- Sub-tab content areas -->
  ${panelsHtml}

</div>`;
    },

    _bindSubTabs() {
        const bar = this.container.querySelector('#vsav4-subtab-bar');
        if (!bar) return;
        bar.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-vsav4-subtab]');
            if (btn) this._switchSubTab(btn.dataset.vsav4Subtab);
        });
    },

    _switchSubTab(tabId) {
        this.activeSubTab = tabId;

        // Update button styles
        this.container.querySelectorAll('[data-vsav4-subtab]').forEach(btn => {
            const active = btn.dataset.vsav4Subtab === tabId;
            btn.classList.toggle('active', active);
            btn.style.background = active ? GREEN : 'var(--bg-tertiary,#161b22)';
            btn.style.color      = active ? '#fff' : 'var(--text-secondary)';
        });

        // Show/hide panels
        this.container.querySelectorAll('.vsav4-subtab-content').forEach(panel => {
            panel.style.display = 'none';
        });
        const panel = this.container.querySelector(`#vsav4-content-${tabId}`);
        if (panel) panel.style.display = 'block';

        // Dispatch to per-tab loader
        const loaders = {
            'dashboard':     () => this._loadDashboard(),
            'calls':         () => this._loadCalls(),
            'cloud-folders': () => this._loadCloudFolders(),
            'analysis':      () => this._loadAnalysis(),
        };
        loaders[tabId]?.();
    },

    // ─────────────────────────────────────────────────────────────────────────
    // Dashboard sub-tab — KPI overview
    // ─────────────────────────────────────────────────────────────────────────

    async _loadDashboard() {
        const panel = this.container.querySelector('#vsav4-content-dashboard');
        if (!panel) return;

        // Guard: only render the skeleton once. Re-clicking the active tab is a no-op.
        if (panel.dataset.rendered !== 'true') {
            panel.dataset.rendered = 'true';
            panel.innerHTML = '';

            const kpiGrid = createKpiGrid([
                createKpiCard({
                    id: 'vsav4-kpi-open-alerts',
                    icon: 'fas fa-exclamation-triangle',
                    label: 'Open alerts',
                    value: '—',
                    variant: 'warning',
                    trend: '—',
                    trendDir: 'neutral',
                }),
                createKpiCard({
                    id: 'vsav4-kpi-follow-ups',
                    icon: 'fas fa-phone-volume',
                    label: 'Follow-ups due',
                    value: '—',
                    variant: 'info',
                    trend: '—',
                    trendDir: 'neutral',
                }),
                createKpiCard({
                    id: 'vsav4-kpi-calls-today',
                    icon: 'fas fa-headset',
                    label: 'Calls today',
                    value: '—',
                    variant: 'success',
                    trend: '—',
                    trendDir: 'neutral',
                }),
                createKpiCard({
                    id: 'vsav4-kpi-avg-risk',
                    icon: 'fas fa-heartbeat',
                    label: 'Avg risk score',
                    value: '—',
                    variant: 'error',
                    trend: '—',
                    trendDir: 'neutral',
                }),
            ]);

            panel.appendChild(kpiGrid);
        }

        // Always re-fetch on tab activation (data can change between visits)
        panel.querySelectorAll('.vsav4-kpi-card, [id^="vsav4-kpi-"]').forEach(() => {/* preserve skeleton */});

        try {
            // Server-side fetch via the org-vault-resolved proxy. /api/vsa-supabase-proxy/dashboard
            // reads the user's external-Supabase URL+service-role-key out of
            // ai_infrastructure.organisation_platform_credentials (via
            // resolve_credentials('supabase_vsa', user_id=g.rls_user_id)) and
            // aggregates counts from call_manager_alerts and veterinary_calls.
            const resp = await this.api.get('/api/vsa-supabase-proxy/dashboard');

            if (!resp || resp.success === false) {
                // 503 path: vault has no row for this org, or proxy errored.
                const message = (resp && (resp.error || resp.message)) || 'Dashboard unavailable';
                this._showConfigState(panel, message);
                return;
            }

            const k = (resp.kpis) || {};
            if (typeof k.open_alerts !== 'undefined') {
                updateKpiCard('vsav4-kpi-open-alerts', {
                    value: String(k.open_alerts),
                    trend: k.open_alerts_trend || `${k.open_alerts_total ?? ''} total`,
                });
            }
            if (typeof k.follow_ups_due !== 'undefined') {
                updateKpiCard('vsav4-kpi-follow-ups', {
                    value: String(k.follow_ups_due),
                    trend: k.follow_ups_trend || '',
                });
            }
            if (typeof k.calls_today !== 'undefined') {
                updateKpiCard('vsav4-kpi-calls-today', {
                    value: String(k.calls_today),
                    trend: k.calls_today_trend || `${k.calls_week ?? ''} this week`,
                });
            }
            if (typeof k.avg_risk !== 'undefined') {
                updateKpiCard('vsav4-kpi-avg-risk', {
                    value: (k.avg_risk === null || k.avg_risk === undefined)
                        ? '—'
                        : (typeof k.avg_risk === 'number' ? k.avg_risk.toFixed(1) : String(k.avg_risk)),
                    trend: k.avg_risk_trend || '',
                });
            }

            this.notify('Dashboard loaded', 'success');
        } catch (err) {
            this.log.error('Dashboard load failed:', err);
            const msg = (err && err.message) || String(err);
            // 503 from the proxy = "vault has no supabase_vsa row for this org".
            // Surface as a configuration-state message, not a hard error.
            if (msg.includes('503') || msg.toLowerCase().includes('configuration')) {
                this._showConfigState(panel, msg);
            } else {
                panel.innerHTML = '';
                panel.appendChild(createErrorMessage(`Failed to load dashboard: ${msg}`));
            }
        }
    },

    /**
     * Render a uniform "Configuration Required" empty-state.
     * Triggered when the server-side proxy reports the org vault has no
     * supabase_vsa row (HTTP 503). The admin needs to seed the credential
     * via POST /api/vsa-supabase-proxy/seed-vault (admin-only).
     */
    _showConfigState(panel, message) {
        panel.innerHTML = '';
        const node = createEmptyState({
            icon: 'fas fa-key',
            heading: 'VSA Supabase credentials not configured',
            subtext: message || 'Ask an org admin to POST the URL + service-role key to /api/vsa-supabase-proxy/seed-vault. Once the vault row exists, refresh this tab.',
            action: {
                label: 'Reload',
                onClick: () => { panel.dataset.rendered = ''; this._loadDashboard(); },
            },
        });
        panel.appendChild(node);
    },

    // ─────────────────────────────────────────────────────────────────────────
    // Calls sub-tab — Tabulator table of phone calls
    // ─────────────────────────────────────────────────────────────────────────

    async _loadCalls() {
        const panel = this.container.querySelector('#vsav4-content-calls');
        if (!panel) return;

        // Always re-fetch — Destroy the old Tabulator first so we don't leak listeners.
        this._destroyCallsTable();
        panel.innerHTML = '';
        panel.appendChild(createLoadingSpinner('Loading calls...'));

        try {
            // Server-side fetch via the org-vault-resolved proxy.
            // /api/vsa-supabase-proxy/calls proxies the external Supabase query,
            // enriches each row with alert severity via a secondary
            // call_manager_alerts fetch, and returns up to 50 rows by default.
            const resp = await this.api.get('/api/vsa-supabase-proxy/calls', {
                limit: 50,
                offset: 0,
            });

            if (!resp || resp.success === false) {
                const message = (resp && (resp.error || resp.message)) || 'Calls unavailable';
                panel.innerHTML = '';
                // 503 from the proxy = no vault row yet.
                if (resp && resp.status === 503 || (message && /configuration/i.test(message))) {
                    this._showConfigState(panel, message);
                } else {
                    panel.appendChild(createErrorMessage(`Failed to load calls: ${message}`));
                }
                return;
            }

            const calls = Array.isArray(resp.calls) ? resp.calls : [];
            const total = typeof resp.total === 'number' ? resp.total : calls.length;

            panel.innerHTML = '';
            if (calls.length === 0) {
                panel.appendChild(createEmptyState({
                    icon: 'fas fa-phone-slash',
                    heading: 'No calls yet',
                    subtext: `External Supabase returned 0 calls${total ? ` (${total} total)` : ''}. Transcripts will appear here once ingestion is connected.`,
                }));
            } else {
                this._renderCallsTable(calls, panel);
                this.notify(`${calls.length} calls loaded${total > calls.length ? ` of ${total}` : ''}`, 'success');
            }
        } catch (err) {
            this.log.error('Calls load failed:', err);
            const msg = (err && err.message) || String(err);
            panel.innerHTML = '';
            // 503 from the proxy = "vault has no supabase_vsa row for this org".
            if (msg.includes('503') || msg.toLowerCase().includes('configuration')) {
                this._showConfigState(panel, msg);
            } else {
                panel.appendChild(createErrorMessage(`Failed to load calls: ${msg}`));
            }
        }
    },

    _renderCallsTable(calls, container) {
        this._destroyCallsTable();
        container.innerHTML = '';

        const tableEl = document.createElement('div');
        tableEl.style.minHeight = '400px';
        container.appendChild(tableEl);

        this.callsTable = new Tabulator(tableEl, {
            data: calls,
            layout: 'fitDataStretch',
            pagination: 'local',
            paginationSize: 25,
            paginationSizeSelector: [10, 25, 50, 100],
            movableColumns: true,
            resizableColumns: true,
            placeholder: 'No calls found',
            columns: [
                { title: 'Call ID',     field: 'call_id',     headerSort: true, headerFilter: 'input' },
                { title: 'Date',        field: 'call_date',   headerSort: true },
                { title: 'Caller',      field: 'caller_name', headerSort: true, headerFilter: 'input' },
                { title: 'Pet',         field: 'pet_name',    headerSort: true, headerFilter: 'input' },
                { title: 'Severity',    field: 'severity',    headerSort: true },
                { title: 'Disposition', field: 'disposition', headerSort: true, headerFilter: 'input' },
            ],
        });
    },

    _destroyCallsTable() {
        if (this.callsTable) {
            try { this.callsTable.destroy(); } catch (_) {}
            this.callsTable = null;
        }
    },

    // ─────────────────────────────────────────────────────────────────────────
    // Cloud Folders sub-tab — connect Drive / OneDrive
    // ─────────────────────────────────────────────────────────────────────────

    async _loadCloudFolders() {
        const panel = this.container.querySelector('#vsav4-content-cloud-folders');
        if (!panel) return;

        if (panel.dataset.rendered === 'true') return;
        panel.dataset.rendered = 'true';

        // Placeholder: defer real Google Drive / OneDrive connect flow until
        // /api/cloud-folder-sync is wired into a per-org vault credential.
        // The platform already exposes /api/cloud-folder-sync — see
        // AI_infrastructure/routes/cloud_folder_sync_routes.py.
        panel.innerHTML = `
<div style="display:flex; flex-direction:column; gap:16px;">

  <div class="dashboard-card" style="padding:20px;">
    <h3 style="margin:0 0 6px; color:var(--text-primary); font-size:16px;">
      <i class="fab fa-google-drive" style="color:#4285f4;"></i> Google Drive
    </h3>
    <p style="margin:0 0 12px; color:var(--text-secondary); font-size:13px;">
      Connect a Google Drive folder containing MP3 call recordings.
      The platform will transcribe new files and run the 21-stage analysis automatically.
    </p>
    <button disabled
      style="padding:8px 18px; background:var(--bg-tertiary); color:var(--text-secondary); border:1px solid var(--border-color); border-radius:6px; font-size:13px; font-weight:600; cursor:not-allowed;">
      <i class="fas fa-plug"></i> Connect (coming soon)
    </button>
  </div>

  <div class="dashboard-card" style="padding:20px;">
    <h3 style="margin:0 0 6px; color:var(--text-primary); font-size:16px;">
      <i class="fab fa-microsoft" style="color:#00a4ef;"></i> Microsoft OneDrive
    </h3>
    <p style="margin:0 0 12px; color:var(--text-secondary); font-size:13px;">
      Connect a OneDrive folder for veterinary call recording ingestion.
    </p>
    <button disabled
      style="padding:8px 18px; background:var(--bg-tertiary); color:var(--text-secondary); border:1px solid var(--border-color); border-radius:6px; font-size:13px; font-weight:600; cursor:not-allowed;">
      <i class="fas fa-plug"></i> Connect (coming soon)
    </button>
  </div>

  <div style="font-size:11px; color:var(--text-tertiary); padding:8px 12px; background:var(--bg-tertiary); border-radius:6px;">
    <i class="fas fa-info-circle"></i>
    Cloud folder sync will be enabled in a later iteration. The backend route
    <code>/api/cloud-folder-sync</code> and the OAuth flows for Google Drive and
    OneDrive are already in place at the platform level.
  </div>

</div>`;
    },

    // ─────────────────────────────────────────────────────────────────────────
    // Analysis sub-tab — manual + auto triggers
    // ─────────────────────────────────────────────────────────────────────────

    async _loadAnalysis() {
        const panel = this.container.querySelector('#vsav4-content-analysis');
        if (!panel) return;

        if (panel.dataset.rendered === 'true') return;
        panel.dataset.rendered = 'true';

        // Placeholder: defer real triggers until the 21-stage analysis pipeline
        // is ported from the external Supabase project into a backend service.
        panel.innerHTML = `
<div style="display:flex; flex-direction:column; gap:16px;">

  <div class="dashboard-card" style="padding:20px;">
    <h3 style="margin:0 0 6px; color:var(--text-primary); font-size:16px;">
      <i class="fas fa-robot"></i> Automatic analysis
    </h3>
    <p style="margin:0 0 12px; color:var(--text-secondary); font-size:13px;">
      When enabled, new calls are automatically pushed through the 21-stage analysis
      pipeline as soon as transcription completes.
    </p>
    <label style="display:flex; align-items:center; gap:10px; cursor:pointer;">
      <input type="checkbox" disabled style="width:18px; height:18px; accent-color:${GREEN};">
      <span style="font-size:13px; color:var(--text-secondary);">
        Enable auto-analysis on new calls (disabled until the pipeline is ported)
      </span>
    </label>
  </div>

  <div class="dashboard-card" style="padding:20px;">
    <h3 style="margin:0 0 6px; color:var(--text-primary); font-size:16px;">
      <i class="fas fa-play-circle"></i> Manual analysis
    </h3>
    <p style="margin:0 0 12px; color:var(--text-secondary); font-size:13px;">
      Pick a single call from the Calls tab and trigger the 21-stage analysis on demand.
    </p>
    <button disabled
      style="padding:8px 18px; background:var(--bg-tertiary); color:var(--text-secondary); border:1px solid var(--border-color); border-radius:6px; font-size:13px; font-weight:600; cursor:not-allowed;">
      <i class="fas fa-search"></i> Analyze selected call (coming soon)
    </button>
  </div>

  <div style="font-size:11px; color:var(--text-tertiary); padding:8px 12px; background:var(--bg-tertiary); border-radius:6px;">
    <i class="fas fa-info-circle"></i>
    The 21-stage phone-call analysis pipeline currently lives in the external
    Supabase project (not on this platform). Porting it is a separate iteration.
  </div>

</div>`;
    },
};