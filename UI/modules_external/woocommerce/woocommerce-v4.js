/**
 * FILE: UI/modules_external/woocommerce/woocommerce-v4.js
 * MODULE TYPE: external
 * ARCHITECTURE: Framework-modern V4 (Composition pattern)
 *
 * PURPOSE:
 *   External V4 rewrite of the WooCommerce module.
 *   Previously this was a 1,300-line global-scope script loaded via
 *   <script src="modules_internal/woocommerce/woocommerce.js">.
 *   This version is an ES Module with proper lifecycle hooks, uses the
 *   shared ModuleAPI client for all fetch calls, and uses module-components
 *   for UI building blocks.
 *
 * TAB: #tab-sales-v4  (runs alongside the old #tab-sales for A/B testing)
 *
 * SUB-TABS:
 *   orders    → direct API /api/woocommerce/orders  → Tabulator
 *   products  → AI agent dispatch
 *   customers → AI agent dispatch
 *   finance   → AI agent dispatch
 *   reports   → direct API /api/woocommerce/orders  → Plotly charts
 *   settings  → AI agent dispatch
 *
 * MIGRATION NOTES (delete when legacy removed):
 *   - Remove <script src="modules_internal/woocommerce/woocommerce.js"> from HTML
 *   - Remove #tab-sales hardcoded HTML block (~500 lines)
 *   - Remove initWooCommerceSubtabs() call from HTML
 *   - Remove the sidebar button that points to data-tab="sales"
 *   - Keep the sidebar button pointing to data-tab="sales-v4"
 *
 * LAST MODIFIED: 2026-03-27 — Initial V4 external module creation
 */

import { ModuleAPI } from '../../shared/js/module-api.js';
import {
    createKpiCard,
    updateKpiCard,
    createKpiGrid,
    createLoadingSpinner,
    createEmptyState,
    createErrorMessage,
} from '../../shared/js/module-components.js';

// ─────────────────────────────────────────────────────────────────────────────
// Constants
// ─────────────────────────────────────────────────────────────────────────────

const PURPLE = '#7f54b3';

const STATUS_COLORS = {
    'pending':    { bg: '#f59e0b', text: '#fffbeb' },
    'processing': { bg: '#3b82f6', text: '#eff6ff' },
    'completed':  { bg: '#10b981', text: '#ecfdf5' },
    'on-hold':    { bg: '#6b7280', text: '#f9fafb' },
    'cancelled':  { bg: '#ef4444', text: '#fef2f2' },
    'refunded':   { bg: '#8b5cf6', text: '#f5f3ff' },
    'failed':     { bg: '#dc2626', text: '#fef2f2' },
};

const CURRENCY_SYMBOLS = {
    'USD': '$', 'CAD': 'C$', 'AUD': 'A$', 'EUR': '€', 'GBP': '£',
    'NZD': 'NZ$', 'SGD': 'S$', 'JPY': '¥', 'CHF': 'CHF',
};

// ─────────────────────────────────────────────────────────────────────────────
// Module definition
// ─────────────────────────────────────────────────────────────────────────────

export default {

    // ── Injected utilities ──────────────────────────────────────────────────
    api: null,      // ModuleAPI instance
    log: null,      // console-prefixed logger (or console)
    notify: null,   // showNotification(msg, type) from host page

    // ── State ────────────────────────────────────────────────────────────────
    container: null,        // #tab-sales-v4
    activeSubTab: 'orders',
    orders: [],             // cached from last fetch
    ordersTable: null,      // Tabulator instance
    reportCharts: [],       // Plotly chart ids for cleanup

    // ── Lifecycle ────────────────────────────────────────────────────────────

    /**
     * Called by the module loader when the user activates this tab.
     * @param {object} utilities  - { api, storage, events, dom, log }
     */
    async onDashboardLoad(utilities) {
        // 1. Wire up utilities
        this.api    = new ModuleAPI({ moduleId: 'woocommerce' });
        this.log    = utilities?.log ?? { info: console.log, warn: console.warn, error: console.error };
        this.notify = window.showNotification ?? ((m, t) => console.log(`[notify:${t}] ${m}`));

        this.log.info('WooCommerce V4 loading...');

        // 2. Locate container
        this.container = document.getElementById('tab-sales-v4');
        if (!this.container) {
            this.log.error('Container #tab-sales-v4 not found');
            return;
        }

        // 3. Render shell
        this._renderShell();

        // 4. Wire sub-tab buttons
        this._bindSubTabs();

        // 5. Auto-load the active sub-tab
        this._switchSubTab('orders');
    },

    /**
     * Called when the user navigates away from this tab (if loader supports it).
     */
    onUnload() {
        this._destroyOrdersTable();
        this._destroyCharts();
        this.log?.info('WooCommerce V4 unloaded');
    },

    // ─────────────────────────────────────────────────────────────────────────
    // Shell rendering
    // ─────────────────────────────────────────────────────────────────────────

    _renderShell() {
        this.container.innerHTML = `
<div class="woocommerce-dashboard" style="padding: var(--space-4, 16px);">

  <!-- Header -->
  <div style="display:flex; align-items:center; gap:12px; margin-bottom:var(--space-4,16px);">
    <i class="fab fa-wordpress" style="font-size:32px; color:${PURPLE};"></i>
    <div>
      <h2 style="margin:0; font-size:22px; font-weight:700; color:var(--text-primary);">WooCommerce Management</h2>
      <span style="font-size:12px; color:var(--text-secondary);">V4 External Module &mdash; Store Online</span>
    </div>
    <span style="margin-left:auto; font-size:11px; background:${PURPLE}22; color:${PURPLE}; padding:4px 10px; border-radius:12px; font-weight:600;">V4 BETA</span>
  </div>

  <!-- Sub-tab bar -->
  <div id="wcv4-subtab-bar" style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:var(--space-4,16px); border-bottom:2px solid var(--border-color,#30363d); padding-bottom:8px;">
    ${['orders','products','customers','finance','reports','settings'].map(id => `
      <button data-wcv4-subtab="${id}"
        style="padding:8px 18px; border:none; border-radius:6px 6px 0 0; cursor:pointer; font-size:13px; font-weight:600;
               background:var(--bg-tertiary,#161b22); color:var(--text-secondary); transition:all 0.2s;"
        onmouseover="this.style.background='${PURPLE}22'; this.style.color='${PURPLE}'"
        onmouseout="if(!this.classList.contains('active')){this.style.background='var(--bg-tertiary,#161b22)'; this.style.color='var(--text-secondary)';}"
      >${id.charAt(0).toUpperCase()+id.slice(1)}</button>
    `).join('')}
  </div>

  <!-- Sub-tab content areas -->
  <div id="wcv4-content-orders"  class="wcv4-subtab-content"></div>
  <div id="wcv4-content-products"  class="wcv4-subtab-content" style="display:none;"></div>
  <div id="wcv4-content-customers" class="wcv4-subtab-content" style="display:none;"></div>
  <div id="wcv4-content-finance"   class="wcv4-subtab-content" style="display:none;"></div>
  <div id="wcv4-content-reports"   class="wcv4-subtab-content" style="display:none;"></div>
  <div id="wcv4-content-settings"  class="wcv4-subtab-content" style="display:none;"></div>

</div>`;
    },

    _bindSubTabs() {
        const bar = this.container.querySelector('#wcv4-subtab-bar');
        if (!bar) return;
        bar.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-wcv4-subtab]');
            if (btn) this._switchSubTab(btn.dataset.wcv4Subtab);
        });
    },

    _switchSubTab(tabId) {
        this.activeSubTab = tabId;

        // Update button styles
        this.container.querySelectorAll('[data-wcv4-subtab]').forEach(btn => {
            const active = btn.dataset.wcv4Subtab === tabId;
            btn.classList.toggle('active', active);
            btn.style.background = active ? PURPLE : 'var(--bg-tertiary,#161b22)';
            btn.style.color      = active ? '#fff'  : 'var(--text-secondary)';
        });

        // Show/hide panels
        this.container.querySelectorAll('.wcv4-subtab-content').forEach(panel => {
            panel.style.display = 'none';
        });
        const panel = this.container.querySelector(`#wcv4-content-${tabId}`);
        if (panel) panel.style.display = 'block';

        // Load content
        const loaders = {
            orders:    () => this._loadOrders(),
            products:  () => this._loadAiTab('products',  'Get all WooCommerce products with stock levels, prices, and categories. Format as a clear list grouped by category.'),
            customers: () => this._loadAiTab('customers', 'Get all WooCommerce customers showing their name, email, total orders, and total spent. Sort by total spent descending.'),
            finance:   () => this._loadAiTab('finance',   'Get WooCommerce financial summary: recent refunds, active coupons, and tax rate configuration.'),
            reports:   () => this._loadReports(),
            settings:  () => this._loadAiTab('settings',  'Get my WooCommerce store settings including shipping zones, payment gateways, and system status. Display in an organized format.'),
        };
        loaders[tabId]?.();
    },

    // ─────────────────────────────────────────────────────────────────────────
    // Orders sub-tab
    // ─────────────────────────────────────────────────────────────────────────

    async _loadOrders(statusFilter = null) {
        const panel = this.container.querySelector('#wcv4-content-orders');
        if (!panel) return;

        // Render toolbar on first load
        if (!panel.querySelector('#wcv4-orders-toolbar')) {
            panel.innerHTML = this._ordersToolbarHTML() + '<div id="wcv4-orders-table-wrap"></div>';
            this._bindOrdersToolbar(panel);
        }

        const toolbar  = panel.querySelector('#wcv4-orders-toolbar');
        const tableWrap = panel.querySelector('#wcv4-orders-table-wrap');

        // Read current filter values
        const status = statusFilter ?? panel.querySelector('[data-wcv4-status-filter].active')?.dataset.wcv4StatusFilter ?? 'any';
        const limit  = panel.querySelector('#wcv4-orders-limit')?.value ?? 50;

        tableWrap.innerHTML = '';
        tableWrap.appendChild(createLoadingSpinner('Loading orders...'));

        try {
            const data = await this.api.get(`/api/woocommerce/orders?status=${status}&limit=${limit}`);

            if (!data.success || !data.orders) throw new Error(data.error || 'No orders returned');

            this.orders = data.orders;

            // Count badge
            const badge = panel.querySelector('#wcv4-orders-count');
            if (badge) badge.textContent = `${data.orders.length} orders`;

            tableWrap.innerHTML = '';
            if (data.orders.length === 0) {
                tableWrap.appendChild(createEmptyState({ icon: 'fas fa-shopping-cart', heading: 'No orders found', subtext: 'Try changing the status filter.' }));
            } else {
                this._renderOrdersTable(data.orders, tableWrap);
            }

            this.notify(`Loaded ${data.orders.length} orders`, 'success');
        } catch (err) {
            this.log.error('Failed to load orders:', err);
            tableWrap.innerHTML = '';
            tableWrap.appendChild(createErrorMessage(`Failed to load orders: ${err.message}`));
            this.notify('Failed to load orders', 'error');
        }
    },

    _ordersToolbarHTML() {
        const filters = ['any','pending','processing','completed','on-hold','cancelled'];
        return `
<div id="wcv4-orders-toolbar" style="display:flex; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:12px;">

  <!-- Status filter pills -->
  <div style="display:flex; gap:6px; flex-wrap:wrap;">
    ${filters.map((f, i) => `
      <button data-wcv4-status-filter="${f}"
        class="${i === 0 ? 'active' : ''}"
        style="padding:5px 14px; border:none; border-radius:20px; font-size:12px; font-weight:600; cursor:pointer;
               background:${i === 0 ? PURPLE : 'var(--bg-tertiary,#161b22)'}; color:${i === 0 ? '#fff' : 'var(--text-secondary)'}; transition:all 0.2s;">
        ${f.charAt(0).toUpperCase()+f.slice(1)}
      </button>`).join('')}
  </div>

  <div style="display:flex; align-items:center; gap:8px; margin-left:auto;">
    <span id="wcv4-orders-count" style="font-size:12px; color:var(--text-secondary);"></span>
    <label style="font-size:12px; color:var(--text-secondary);">Limit:
      <select id="wcv4-orders-limit" style="margin-left:4px; background:var(--bg-tertiary); color:var(--text-primary); border:1px solid var(--border-color); border-radius:4px; padding:3px 6px; font-size:12px;">
        <option value="25">25</option>
        <option value="50" selected>50</option>
        <option value="100">100</option>
        <option value="200">200</option>
      </select>
    </label>
    <button id="wcv4-orders-refresh"
      style="padding:6px 14px; background:${PURPLE}; color:#fff; border:none; border-radius:6px; font-size:12px; font-weight:600; cursor:pointer;">
      <i class="fas fa-sync-alt"></i> Refresh
    </button>
    <button id="wcv4-orders-export"
      style="padding:6px 14px; background:var(--bg-tertiary); color:var(--text-primary); border:1px solid var(--border-color); border-radius:6px; font-size:12px; font-weight:600; cursor:pointer;">
      <i class="fas fa-file-excel"></i> Export
    </button>
  </div>
</div>`;
    },

    _bindOrdersToolbar(panel) {
        panel.addEventListener('click', (e) => {
            // Status filter pills
            const filterBtn = e.target.closest('[data-wcv4-status-filter]');
            if (filterBtn) {
                panel.querySelectorAll('[data-wcv4-status-filter]').forEach(b => {
                    const isTarget = b === filterBtn;
                    b.classList.toggle('active', isTarget);
                    b.style.background = isTarget ? PURPLE : 'var(--bg-tertiary,#161b22)';
                    b.style.color      = isTarget ? '#fff'  : 'var(--text-secondary)';
                });
                this._loadOrders(filterBtn.dataset.wcv4StatusFilter);
                return;
            }

            // Refresh
            if (e.target.closest('#wcv4-orders-refresh')) {
                this._loadOrders();
                return;
            }

            // Export CSV
            if (e.target.closest('#wcv4-orders-export')) {
                this._exportOrdersCsv();
                return;
            }
        });
    },

    _renderOrdersTable(orders, container) {
        this._destroyOrdersTable();
        container.innerHTML = '';

        // Thin wrapper div for Tabulator
        const tableEl = document.createElement('div');
        tableEl.style.minHeight = '400px';
        container.appendChild(tableEl);

        this.ordersTable = new Tabulator(tableEl, {
            data: orders,
            layout: 'fitDataStretch',
            pagination: 'local',
            paginationSize: 25,
            paginationSizeSelector: [10, 25, 50, 100],
            movableColumns: true,
            resizableColumns: true,
            placeholder: 'No orders found',
            selectable: true,
            columns: [
                { formatter: 'rowSelection', titleFormatter: 'rowSelection', hozAlign: 'center', headerSort: false, width: 40 },
                { title: '#', formatter: 'rownum', hozAlign: 'center', width: 50 },
                {
                    title: 'Order ID', field: 'id', width: 110, headerSort: true, headerFilter: 'input',
                    formatter: c => `<span style="font-weight:600; color:#fff;">#${c.getValue()}</span>`,
                },
                {
                    title: 'Date', field: 'date_created', width: 110, headerSort: true,
                    formatter: c => {
                        const d = new Date(c.getValue());
                        return `<span style="color:#fff;">${d.toLocaleDateString('en-GB').replace(/\//g,'-')}</span>`;
                    },
                },
                {
                    title: 'Status', field: 'status', width: 130, headerSort: true, headerFilter: 'input',
                    formatter: c => {
                        const s = c.getValue();
                        const col = STATUS_COLORS[s?.toLowerCase()] ?? { bg: '#6b7280', text: '#f9fafb' };
                        return `<span style="display:inline-block;padding:5px 12px;border-radius:12px;font-size:12px;font-weight:700;background:${col.bg};color:${col.text};text-transform:capitalize;">${s?.replace('-',' ')}</span>`;
                    },
                },
                {
                    title: 'Customer', field: 'customer_name', width: 170, headerSort: true, headerFilter: 'input',
                    formatter: c => `<div style="font-weight:600;color:#fff;">${c.getValue() || 'N/A'}</div>`,
                },
                {
                    title: 'Email', field: 'customer_email', width: 200, headerFilter: 'input',
                    formatter: c => `<span style="color:#fff;">${c.getValue() || 'N/A'}</span>`,
                },
                {
                    title: 'Phone', field: 'customer_phone', width: 140, headerFilter: 'input',
                    formatter: c => `<span style="color:#fff;">${c.getValue() || 'N/A'}</span>`,
                },
                {
                    title: 'Shipping Address', field: 'shipping_address', width: 240, headerFilter: 'input',
                    formatter: c => {
                        const addr = c.getValue();
                        if (!addr) return '<span style="color:#fff;">No address</span>';
                        return `<div style="line-height:1.5;color:#fff;">${addr.split('\n').filter(l => l.trim()).join('<br>')}</div>`;
                    },
                },
                {
                    title: 'Items', field: 'line_items', width: 220,
                    formatter: c => {
                        const items = c.getValue();
                        if (!items?.length) return '<span style="color:#fff;">No items</span>';
                        const list = items.slice(0, 3).map(i => `${i.quantity}× ${i.name}`).join('<br>');
                        const more = items.length > 3 ? `<br><em style="color:var(--text-secondary);">+${items.length-3} more</em>` : '';
                        return `<div style="color:#fff;">${list}${more}</div>`;
                    },
                },
                {
                    title: 'Total', field: 'total', width: 110, headerSort: true,
                    formatter: c => {
                        const row  = c.getRow().getData();
                        const sym  = CURRENCY_SYMBOLS[row.currency] ?? row.currency ?? '$';
                        return `<span style="font-weight:700;color:#10b981;">${sym}${parseFloat(c.getValue()||0).toFixed(2)}</span>`;
                    },
                },
            ],
        });
    },

    _destroyOrdersTable() {
        if (this.ordersTable) {
            try { this.ordersTable.destroy(); } catch (_) {}
            this.ordersTable = null;
        }
    },

    _exportOrdersCsv() {
        if (!this.ordersTable) { this.notify('No table to export', 'info'); return; }
        this.ordersTable.download('csv', 'woocommerce-orders.csv');
    },

    // ─────────────────────────────────────────────────────────────────────────
    // AI-driven sub-tabs (products / customers / finance / settings)
    // ─────────────────────────────────────────────────────────────────────────

    async _loadAiTab(tabId, message) {
        const panel = this.container.querySelector(`#wcv4-content-${tabId}`);
        if (!panel) return;

        panel.innerHTML = '';
        panel.appendChild(createLoadingSpinner(`Loading ${tabId}...`));

        try {
            const data = await this.api.post('/api/agent/agent/1/start', {
                message,
                context: { tab: 'woocommerce', action: `load_${tabId}`, tools_enabled: true },
            });

            const html = data.response
                ? this._basicMarkdown(data.response)
                : '<p style="color:var(--text-secondary);">No response from agent.</p>';

            panel.innerHTML = `<div style="padding:var(--space-4,16px); background:var(--bg-secondary); border-radius:8px; line-height:1.6;">${html}</div>`;
            this.notify(`${tabId.charAt(0).toUpperCase()+tabId.slice(1)} loaded`, 'success');
        } catch (err) {
            this.log.error(`Failed to load ${tabId}:`, err);
            panel.innerHTML = '';
            panel.appendChild(createErrorMessage(`Failed to load ${tabId}: ${err.message}`));
            this.notify(`Failed to load ${tabId}`, 'error');
        }
    },

    // ─────────────────────────────────────────────────────────────────────────
    // Reports sub-tab
    // ─────────────────────────────────────────────────────────────────────────

    async _loadReports() {
        const panel = this.container.querySelector('#wcv4-content-reports');
        if (!panel) return;

        panel.innerHTML = '';
        panel.appendChild(createLoadingSpinner('Generating analytics...'));

        try {
            const data = await this.api.get('/api/woocommerce/orders?status=any&limit=200');
            if (!data.success || !data.orders) throw new Error('Failed to fetch orders for reports');

            const orders  = data.orders;
            const period  = 30; // default 30 days
            const stats   = this._calcStats(orders, period);

            panel.innerHTML = `
<div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; margin-bottom:20px;" id="wcv4-stats-grid"></div>

<div style="display:flex; align-items:center; gap:10px; margin-bottom:16px;">
  <label style="font-size:13px; color:var(--text-secondary);">Period:
    <select id="wcv4-report-period" style="margin-left:6px; background:var(--bg-tertiary); color:var(--text-primary); border:1px solid var(--border-color); border-radius:4px; padding:4px 8px; font-size:12px;">
      <option value="7">Last 7 days</option>
      <option value="30" selected>Last 30 days</option>
      <option value="90">Last 90 days</option>
      <option value="365">Last 12 months</option>
    </select>
  </label>
  <button onclick="this.closest('[id]')" id="wcv4-refresh-reports"
    style="padding:6px 14px; background:${PURPLE}; color:#fff; border:none; border-radius:6px; font-size:12px; font-weight:600; cursor:pointer;">
    <i class="fas fa-sync-alt"></i> Refresh
  </button>
</div>

<div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:16px;">
  <div class="dashboard-card" style="padding:16px;">
    <h4 style="margin:0 0 12px; color:var(--text-primary); font-size:14px;">Sales Trend</h4>
    <div id="wcv4-chart-sales-trend" style="height:260px;"></div>
  </div>
  <div class="dashboard-card" style="padding:16px;">
    <h4 style="margin:0 0 12px; color:var(--text-primary); font-size:14px;">Order Status Distribution</h4>
    <div id="wcv4-chart-status-pie" style="height:260px;"></div>
  </div>
</div>
<div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
  <div class="dashboard-card" style="padding:16px;">
    <h4 style="margin:0 0 12px; color:var(--text-primary); font-size:14px;">Top Products</h4>
    <div id="wcv4-chart-top-products" style="height:260px;"></div>
  </div>
  <div class="dashboard-card" style="padding:16px;">
    <h4 style="margin:0 0 12px; color:var(--text-primary); font-size:14px;">Revenue by Day of Week</h4>
    <div id="wcv4-chart-day-revenue" style="height:260px;"></div>
  </div>
</div>`;

            // KPI cards
            const statsGrid = panel.querySelector('#wcv4-stats-grid');
            [
                { id: 'wcv4-stat-sales',     icon: 'fas fa-dollar-sign', label: 'Total Sales',   value: `$${stats.totalSales.toFixed(2)}`,          variant: 'success' },
                { id: 'wcv4-stat-orders',    icon: 'fas fa-shopping-cart', label: 'Total Orders', value: String(stats.totalOrders),                   variant: 'info' },
                { id: 'wcv4-stat-avg',       icon: 'fas fa-chart-line',  label: 'Avg Order',    value: `$${stats.avgOrderValue.toFixed(2)}`,          variant: '' },
                { id: 'wcv4-stat-customers', icon: 'fas fa-users',       label: 'Unique Customers', value: String(stats.uniqueCustomers),             variant: '' },
            ].forEach(cfg => statsGrid.appendChild(createKpiCard(cfg)));

            // Period selector re-renders
            panel.querySelector('#wcv4-report-period')?.addEventListener('change', (e) => {
                const p = parseInt(e.target.value);
                const s = this._calcStats(orders, p);
                updateKpiCard('wcv4-stat-sales',     `$${s.totalSales.toFixed(2)}`);
                updateKpiCard('wcv4-stat-orders',    String(s.totalOrders));
                updateKpiCard('wcv4-stat-avg',       `$${s.avgOrderValue.toFixed(2)}`);
                updateKpiCard('wcv4-stat-customers', String(s.uniqueCustomers));
                this._renderAllCharts(orders, p);
            });

            this._renderAllCharts(orders, period);
            this.notify('Analytics loaded', 'success');

        } catch (err) {
            this.log.error('Reports failed:', err);
            panel.innerHTML = '';
            panel.appendChild(createErrorMessage(`Failed to load analytics: ${err.message}`));
            this.notify('Failed to load analytics', 'error');
        }
    },

    _calcStats(orders, period) {
        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - period);
        const filtered = orders.filter(o => new Date(o.date_created) >= cutoff);
        const totalSales     = filtered.reduce((s, o) => s + parseFloat(o.total || 0), 0);
        const totalOrders    = filtered.length;
        const avgOrderValue  = totalOrders > 0 ? totalSales / totalOrders : 0;
        const uniqueCustomers = new Set(filtered.map(o => o.customer_email)).size;
        return { totalSales, totalOrders, avgOrderValue, uniqueCustomers };
    },

    _renderAllCharts(orders, period) {
        this._destroyCharts();
        this.reportCharts = [];
        this._chartSalesTrend(orders, period);
        this._chartStatusPie(orders);
        this._chartTopProducts(orders, period);
        this._chartDayRevenue(orders, period);
    },

    _destroyCharts() {
        this.reportCharts.forEach(id => {
            try { Plotly.purge(id); } catch (_) {}
        });
        this.reportCharts = [];
    },

    _chartSalesTrend(orders, period) {
        const id = 'wcv4-chart-sales-trend';
        if (!document.getElementById(id)) return;
        this.reportCharts.push(id);

        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - period);
        const byDate = {};
        orders.filter(o => new Date(o.date_created) >= cutoff).forEach(o => {
            const d = new Date(o.date_created).toISOString().split('T')[0];
            if (!byDate[d]) byDate[d] = { sales: 0, count: 0 };
            byDate[d].sales += parseFloat(o.total || 0);
            byDate[d].count += 1;
        });
        const dates  = Object.keys(byDate).sort();
        const sales  = dates.map(d => byDate[d].sales);
        const counts = dates.map(d => byDate[d].count);

        Plotly.newPlot(id, [
            { x: dates, y: sales,  name: 'Sales ($)', type: 'scatter', mode: 'lines+markers', marker: { color: PURPLE, size: 7 }, line: { width: 3, color: PURPLE } },
            { x: dates, y: counts, name: 'Orders',    type: 'scatter', mode: 'lines+markers', marker: { color: '#10b981', size: 7 }, line: { width: 3, color: '#10b981' }, yaxis: 'y2' },
        ], {
            paper_bgcolor: '#161b22', plot_bgcolor: '#0d1117', font: { color: '#c9d1d9', size: 11 },
            xaxis: { title: 'Date', gridcolor: '#30363d' },
            yaxis:  { title: 'Sales ($)', gridcolor: '#30363d' },
            yaxis2: { title: 'Orders', overlaying: 'y', side: 'right', showgrid: false },
            margin: { t: 20, b: 50, l: 55, r: 55 }, hovermode: 'x unified', showlegend: true,
        }, { responsive: true });
    },

    _chartStatusPie(orders) {
        const id = 'wcv4-chart-status-pie';
        if (!document.getElementById(id)) return;
        this.reportCharts.push(id);

        const counts = {};
        orders.forEach(o => { const s = o.status || 'unknown'; counts[s] = (counts[s]||0)+1; });
        const colorMap = { pending:'#f59e0b', processing:'#3b82f6', completed:'#10b981', 'on-hold':'#6b7280', cancelled:'#ef4444', refunded:'#8b5cf6', failed:'#dc2626' };

        Plotly.newPlot(id, [{
            labels:  Object.keys(counts).map(s => s.replace('-',' ').toUpperCase()),
            values:  Object.values(counts),
            type:    'pie',
            marker:  { colors: Object.keys(counts).map(s => colorMap[s] || '#6b7280') },
            textinfo: 'label+percent', hoverinfo: 'label+value+percent',
        }], {
            paper_bgcolor: '#161b22', plot_bgcolor: '#0d1117', font: { color: '#c9d1d9', size: 11 },
            margin: { t: 20, b: 20, l: 20, r: 20 }, showlegend: true,
        }, { responsive: true });
    },

    _chartTopProducts(orders, period) {
        const id = 'wcv4-chart-top-products';
        if (!document.getElementById(id)) return;
        this.reportCharts.push(id);

        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - period);
        const productCounts = {};
        orders.filter(o => new Date(o.date_created) >= cutoff).forEach(o => {
            (o.line_items || []).forEach(item => {
                productCounts[item.name] = (productCounts[item.name]||0) + item.quantity;
            });
        });
        const sorted = Object.entries(productCounts).sort((a,b) => b[1]-a[1]).slice(0, 10);
        const names  = sorted.map(([n]) => n.length > 30 ? n.slice(0,28)+'...' : n);
        const qtys   = sorted.map(([,q]) => q);

        Plotly.newPlot(id, [{
            x: qtys, y: names, type: 'bar', orientation: 'h',
            marker: { color: PURPLE, opacity: 0.85 },
        }], {
            paper_bgcolor: '#161b22', plot_bgcolor: '#0d1117', font: { color: '#c9d1d9', size: 11 },
            xaxis: { title: 'Units Sold', gridcolor: '#30363d' },
            yaxis: { autorange: 'reversed' },
            margin: { t: 20, b: 40, l: 180, r: 20 },
        }, { responsive: true });
    },

    _chartDayRevenue(orders, period) {
        const id = 'wcv4-chart-day-revenue';
        if (!document.getElementById(id)) return;
        this.reportCharts.push(id);

        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - period);
        const days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
        const rev  = new Array(7).fill(0);
        orders.filter(o => new Date(o.date_created) >= cutoff).forEach(o => {
            rev[new Date(o.date_created).getDay()] += parseFloat(o.total || 0);
        });

        Plotly.newPlot(id, [{
            x: days, y: rev, type: 'bar',
            marker: { color: rev.map(v => v === Math.max(...rev) ? '#10b981' : `${PURPLE}99`) },
        }], {
            paper_bgcolor: '#161b22', plot_bgcolor: '#0d1117', font: { color: '#c9d1d9', size: 11 },
            xaxis: { title: 'Day of Week', gridcolor: '#30363d' },
            yaxis: { title: 'Revenue ($)', gridcolor: '#30363d' },
            margin: { t: 20, b: 50, l: 65, r: 20 },
        }, { responsive: true });
    },

    // ─────────────────────────────────────────────────────────────────────────
    // Helpers
    // ─────────────────────────────────────────────────────────────────────────

    /** Minimal Markdown → HTML for AI responses (same rules as host page renderBasicMarkdown) */
    _basicMarkdown(text) {
        return text
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/`(.+?)`/g, '<code>$1</code>')
            .replace(/^#{3} (.+)$/gm, '<h3 style="color:var(--text-primary);margin:12px 0 6px;">$1</h3>')
            .replace(/^#{2} (.+)$/gm, '<h2 style="color:var(--text-primary);margin:16px 0 8px;">$1</h2>')
            .replace(/^# (.+)$/gm,   '<h1 style="color:var(--text-primary);margin:20px 0 10px;">$1</h1>')
            .replace(/^- (.+)$/gm,   '<li style="margin:4px 0;">$1</li>')
            .replace(/\n/g, '<br>');
    },
};
