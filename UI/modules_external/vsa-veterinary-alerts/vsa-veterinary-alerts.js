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
 * SUB-TABS (this iteration — stubs only, data wiring deferred):
 *   dashboard      → KPI cards (open alerts, follow-ups, calls today, avg risk)
 *   calls          → Tabulator table of phone calls (placeholder, awaiting
 *                    a /api/vsa-alerts/calls backend route)
 *   cloud-folders  → Connect Google Drive / OneDrive folder sync (placeholder,
 *                    wired up in a later iteration — platform already has
 *                    /api/cloud-folder-sync)
 *   analysis       → Manual + auto analysis triggers (placeholder — the 21-stage
 *                    call analysis pipeline lives in the external Supabase project
 *                    and is not ported yet)
 *
 * SECURITY / SECRETS:
 *   - NO direct Supabase calls from the browser in this iteration.
 *   - NO hardcoded API keys. All data fetches go through this.api (ModuleAPI),
 *     which auto-injects the JWT from localStorage and surfaces 401s via the
 *     'module:auth-expired' window event.
 *   - The external Supabase URL + anon key live in manifest.settings (per user's
 *     explicit decision for this iteration). They are *declared but not yet
 *     consumed* by this module. Migrate to organisation_platform_credentials
 *     via the existing supabase_vsa catalog row (migration 036) in a later round.
 *
 * MIGRATION NOTES:
 *   - Supabase URL+key: move from manifest.settings into the org vault.
 *   - The 21-stage analysis pipeline: port from the external Supabase project
 *     into a backend service under AI_infrastructure/services/vsa/.
 *   - Real data for the Calls tab: add a new GET /api/vsa-alerts/calls endpoint
 *     in AI_infrastructure/routes/vsa_alerts_routes.py that proxies the external
 *     Supabase query (server-side, so the anon key never reaches the browser).
 *
 * LAST MODIFIED: 2026-07-14 — Initial V4 external module creation
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

const GREEN = '#2E7D32';

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

        // Guard: only render once. Re-clicking the active tab is a no-op.
        if (panel.dataset.rendered === 'true') return;
        panel.dataset.rendered = 'true';

        panel.innerHTML = '';
        panel.appendChild(createLoadingSpinner('Loading dashboard...'));

        try {
            // TODO: replace placeholder data with a real /api/vsa-alerts/dashboard-summary
            // endpoint that aggregates counts from the external Supabase project.
            // For now, render zeroed KPI cards so the layout is verifiable.
            const kpis = createKpiGrid([
                createKpiCard({
                    id: 'vsav4-kpi-open-alerts',
                    icon: 'fas fa-exclamation-triangle',
                    label: 'Open alerts',
                    value: '—',
                    variant: 'warning',
                    trend: 'awaiting backend',
                    trendDir: 'neutral',
                }),
                createKpiCard({
                    id: 'vsav4-kpi-follow-ups',
                    icon: 'fas fa-phone-volume',
                    label: 'Follow-ups due',
                    value: '—',
                    variant: 'info',
                    trend: 'awaiting backend',
                    trendDir: 'neutral',
                }),
                createKpiCard({
                    id: 'vsav4-kpi-calls-today',
                    icon: 'fas fa-headset',
                    label: 'Calls today',
                    value: '—',
                    variant: 'success',
                    trend: 'awaiting backend',
                    trendDir: 'neutral',
                }),
                createKpiCard({
                    id: 'vsav4-kpi-avg-risk',
                    icon: 'fas fa-heartbeat',
                    label: 'Avg risk score',
                    value: '—',
                    variant: 'error',
                    trend: 'awaiting backend',
                    trendDir: 'neutral',
                }),
            ]);

            panel.innerHTML = '';
            panel.appendChild(kpis);

            // Defer the placeholder update so users see the cards populate.
            // Real values will arrive via /api/vsa-alerts/dashboard-summary.
            this.notify('Dashboard loaded (placeholder data)', 'info');
        } catch (err) {
            this.log.error('Dashboard load failed:', err);
            panel.innerHTML = '';
            panel.appendChild(createErrorMessage(`Failed to load dashboard: ${err.message}`));
        }
    },

    // ─────────────────────────────────────────────────────────────────────────
    // Calls sub-tab — Tabulator table of phone calls
    // ─────────────────────────────────────────────────────────────────────────

    async _loadCalls() {
        const panel = this.container.querySelector('#vsav4-content-calls');
        if (!panel) return;

        panel.innerHTML = '';
        panel.appendChild(createLoadingSpinner('Loading calls...'));

        try {
            // TODO: wire up to a real /api/vsa-alerts/calls endpoint that
            // proxies the external Supabase query server-side.
            // For this iteration, render an empty Tabulator so the layout
            // is verifiable end-to-end.
            const data = [];

            panel.innerHTML = '';
            if (data.length === 0) {
                panel.appendChild(createEmptyState({
                    icon: 'fas fa-phone-slash',
                    heading: 'No calls yet',
                    subtext: 'Calls will appear here once cloud-folder ingestion is connected.',
                }));
            } else {
                this._renderCallsTable(data, panel);
            }
            this.notify('Calls panel loaded', 'success');
        } catch (err) {
            this.log.error('Calls load failed:', err);
            panel.innerHTML = '';
            panel.appendChild(createErrorMessage(`Failed to load calls: ${err.message}`));
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