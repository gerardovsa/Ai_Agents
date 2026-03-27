/**
 * FILE: UI/shared/js/module-components.js
 * PURPOSE: Shared UI component factory functions for V4 modules
 * ARCHITECTURE: ES Module — pure factory functions, no classes, no framework
 *
 * USAGE:
 *   import { createKpiCard, updateKpiCard, createFilterBar,
 *            createDataTable, createChartPanel }
 *     from '../../shared/js/module-components.js';
 *
 * DESIGN SYSTEM:
 *   All components use CSS class names from ui-standardization.css.
 *   No inline styles except dynamic values (icon color, chart height).
 *   Colour tokens come from CSS custom properties defined in that file.
 *
 * XSS SAFETY:
 *   All user-supplied text is set via .textContent, never innerHTML.
 *   HTML templates only use trusted constant strings (icon classes, CSS names).
 *
 * DEPENDENCIES (loaded by the host page — not imported here):
 *   - Tabulator (global `Tabulator`) for createDataTable()
 *   - ApexCharts (global `ApexCharts`) for createChartPanel()
 *   - FontAwesome for icon classes
 *   - ui-standardization.css loaded in <head>
 *
 * LAST MODIFIED: 2026-03-27 — Initial implementation (Phase 1 module redesign)
 */

// ─────────────────────────────────────────────────────────────────────────────
// 1. KPI / Metric Card
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Creates a standardised KPI metric card matching the .metric-card pattern
 * from ui-standardization.css.
 *
 * @param {object} config
 * @param {string}  config.id         - HTML id for the value element (for updateKpiCard)
 * @param {string}  config.icon       - FontAwesome class string, e.g. 'fas fa-dollar-sign'
 * @param {string}  config.label      - Descriptive label text shown below the value
 * @param {string}  [config.value]    - Initial display value (default '—')
 * @param {string}  [config.variant]  - Left-border colour: 'success'|'error'|'warning'|'info'
 * @param {string}  [config.trend]    - Trend caption e.g. '+12% vs last month'
 * @param {string}  [config.trendDir] - 'up'|'down'|'neutral' (default 'neutral')
 * @returns {HTMLElement} .metric-card div ready to append
 */
export function createKpiCard({
    id,
    icon,
    label,
    value    = '\u2014',   // em-dash as default
    variant  = '',
    trend    = '',
    trendDir = 'neutral',
}) {
    const card = document.createElement('div');
    card.className = `metric-card${variant ? ' ' + variant : ''}`;

    // Icon column
    const iconWrap = document.createElement('div');
    iconWrap.className = 'metric-icon';
    const iconEl = document.createElement('i');
    iconEl.className = icon;
    iconWrap.appendChild(iconEl);

    // Content column
    const content = document.createElement('div');
    content.className = 'metric-content';

    const valueEl = document.createElement('div');
    valueEl.className = 'metric-value';
    valueEl.id = id;
    valueEl.textContent = value;

    const labelEl = document.createElement('div');
    labelEl.className = 'metric-label';
    labelEl.textContent = label;

    content.appendChild(valueEl);
    content.appendChild(labelEl);

    // Optional trend row
    if (trend) {
        const trendEl = document.createElement('div');
        trendEl.className = `metric-footer`;

        const changeEl = document.createElement('span');
        changeEl.className = `metric-change ${trendDir}`;

        const arrowIcon = document.createElement('i');
        arrowIcon.className = trendDir === 'up'
            ? 'fas fa-arrow-up'
            : trendDir === 'down'
                ? 'fas fa-arrow-down'
                : 'fas fa-equals';
        changeEl.appendChild(arrowIcon);

        const trendText = document.createTextNode(' ' + trend);
        changeEl.appendChild(trendText);
        trendEl.appendChild(changeEl);
        content.appendChild(trendEl);
    }

    card.appendChild(iconWrap);
    card.appendChild(content);
    return card;
}

/**
 * Update an existing KPI card's displayed value (and optional trend text).
 * Looks up the value element by `id` that was passed to createKpiCard().
 *
 * @param {string}      id       - The id passed to createKpiCard()
 * @param {string}      value    - New value to display
 * @param {string|null} [trend]  - New trend text (null = leave unchanged)
 */
export function updateKpiCard(id, value, trend = null) {
    const valueEl = document.getElementById(id);
    if (valueEl) {
        valueEl.textContent = value;
    }
    if (trend !== null && valueEl) {
        const footer = valueEl.closest('.metric-card')?.querySelector('.metric-footer');
        if (footer) {
            const changeEl = footer.querySelector('.metric-change');
            if (changeEl) {
                // Preserve the arrow icon, update only the text node
                const textNodes = [...changeEl.childNodes].filter(n => n.nodeType === Node.TEXT_NODE);
                if (textNodes.length) {
                    textNodes[textNodes.length - 1].textContent = ' ' + trend;
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// 2. KPI Card Grid wrapper
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Wraps multiple KPI cards in a responsive .metrics-grid container.
 *
 * @param {HTMLElement[]} cards - Array of elements from createKpiCard()
 * @returns {HTMLElement} .metrics-grid div
 */
export function createKpiGrid(cards) {
    const grid = document.createElement('div');
    grid.className = 'metrics-grid';
    cards.forEach(c => grid.appendChild(c));
    return grid;
}

// ─────────────────────────────────────────────────────────────────────────────
// 3. Filter Bar
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Creates a standardised filter/action bar with select dropdowns,
 * optional text search, and optional date range inputs.
 *
 * The bar uses .action-bar CSS from ui-standardization.css.
 * On any change, calls config.onChange with an object of current values.
 *
 * @param {object}   config
 * @param {Array}    [config.filters]       - Dropdown filter definitions
 * @param {string}    config.filters[].id       - <select> element id
 * @param {string}    config.filters[].label    - Visible label
 * @param {Array}     config.filters[].options  - [{value, label}] options
 * @param {string}   [config.filters[].default] - Default selected value
 * @param {boolean}  [config.showSearch]    - Include a text search input (default true)
 * @param {string}   [config.searchId]      - id for the search input
 * @param {string}   [config.searchPlaceholder] - Placeholder text
 * @param {boolean}  [config.showDateRange] - Include from/to date inputs (default false)
 * @param {function} [config.onChange]      - Callback({filterId: value, ...search, ...dates})
 * @param {Array}    [config.actions]       - Right-side action buttons [{label, icon, onClick, variant}]
 * @returns {HTMLElement} .action-bar element
 */
export function createFilterBar({
    filters          = [],
    showSearch       = true,
    searchId         = 'filter-search',
    searchPlaceholder = 'Search...',
    showDateRange    = false,
    onChange         = () => {},
    actions          = [],
} = {}) {
    const bar = document.createElement('div');
    bar.className = 'action-bar';

    // ── Left: dropdowns + search ─────────────────────────────────────────────
    const left = document.createElement('div');
    left.className = 'action-bar-left';

    // Helper to collect all current filter values and fire onChange
    function emitChange() {
        const vals = {};
        filters.forEach(f => {
            const el = bar.querySelector(`#${f.id}`);
            if (el) vals[f.id] = el.value;
        });
        if (showSearch) {
            const searchEl = bar.querySelector(`#${searchId}`);
            if (searchEl) vals.search = searchEl.value;
        }
        if (showDateRange) {
            const from = bar.querySelector('#filter-date-from');
            const to   = bar.querySelector('#filter-date-to');
            if (from) vals.dateFrom = from.value;
            if (to)   vals.dateTo   = to.value;
        }
        onChange(vals);
    }

    // Build dropdown selects
    filters.forEach(f => {
        const wrap = document.createElement('div');
        wrap.style.display = 'flex';
        wrap.style.flexDirection = 'column';
        wrap.style.gap = '2px';

        const labelEl = document.createElement('label');
        labelEl.className = 'form-label';
        labelEl.htmlFor = f.id;
        labelEl.textContent = f.label;
        labelEl.style.marginBottom = '0';
        labelEl.style.fontSize = 'var(--font-size-xs)';

        const select = document.createElement('select');
        select.className = 'form-control';
        select.id = f.id;
        select.style.width = 'auto';
        select.style.minWidth = '130px';

        (f.options || []).forEach(opt => {
            const option = document.createElement('option');
            option.value = opt.value;
            option.textContent = opt.label;
            if (opt.value === f.default) option.selected = true;
            select.appendChild(option);
        });

        select.addEventListener('change', emitChange);
        wrap.appendChild(labelEl);
        wrap.appendChild(select);
        left.appendChild(wrap);
    });

    // Date range inputs
    if (showDateRange) {
        ['filter-date-from', 'filter-date-to'].forEach((dateId, idx) => {
            const wrap = document.createElement('div');
            wrap.style.display = 'flex';
            wrap.style.flexDirection = 'column';
            wrap.style.gap = '2px';

            const labelEl = document.createElement('label');
            labelEl.className = 'form-label';
            labelEl.htmlFor = dateId;
            labelEl.textContent = idx === 0 ? 'From' : 'To';
            labelEl.style.marginBottom = '0';
            labelEl.style.fontSize = 'var(--font-size-xs)';

            const input = document.createElement('input');
            input.type = 'date';
            input.className = 'form-control';
            input.id = dateId;
            input.style.width = 'auto';
            input.addEventListener('change', emitChange);

            wrap.appendChild(labelEl);
            wrap.appendChild(input);
            left.appendChild(wrap);
        });
    }

    // Search input
    if (showSearch) {
        const searchWrap = document.createElement('div');
        searchWrap.style.position = 'relative';

        const searchIcon = document.createElement('i');
        searchIcon.className = 'fas fa-search';
        searchIcon.style.cssText = 'position:absolute;left:10px;top:50%;transform:translateY(-50%);color:var(--text-tertiary);pointer-events:none;font-size:12px;';

        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control';
        searchInput.id = searchId;
        searchInput.placeholder = searchPlaceholder;
        searchInput.style.paddingLeft = '30px';
        searchInput.style.width = '200px';
        searchInput.addEventListener('input', emitChange);

        searchWrap.appendChild(searchIcon);
        searchWrap.appendChild(searchInput);
        left.appendChild(searchWrap);
    }

    bar.appendChild(left);

    // ── Right: action buttons ────────────────────────────────────────────────
    if (actions.length > 0) {
        const right = document.createElement('div');
        right.className = 'action-bar-right';

        actions.forEach(act => {
            const btn = document.createElement('button');
            btn.className = `btn${act.variant ? ' btn-' + act.variant : ''}`;
            if (act.icon) {
                const ico = document.createElement('i');
                ico.className = act.icon;
                btn.appendChild(ico);
                btn.appendChild(document.createTextNode(' ' + act.label));
            } else {
                btn.textContent = act.label;
            }
            btn.addEventListener('click', act.onClick || (() => {}));
            right.appendChild(btn);
        });

        bar.appendChild(right);
    }

    return bar;
}

// ─────────────────────────────────────────────────────────────────────────────
// 4. Data Table (Tabulator wrapper)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Creates a Tabulator table inside a new wrapper div, with optional export buttons.
 *
 * The wrapper div is inserted into the element found by `containerId`.
 * The Tabulator instance is returned so callers can call .replaceData(), .setFilter(), etc.
 *
 * Requires global `Tabulator` to be loaded by the host page.
 *
 * @param {object}    config
 * @param {string}    config.containerId  - ID of the parent element to render into
 * @param {Array}     config.columns      - Tabulator column definitions
 * @param {Array}     [config.data]       - Initial row data
 * @param {boolean}   [config.exportable] - Show CSV export button above table (default true)
 * @param {boolean}   [config.paginate]   - Enable pagination (default true)
 * @param {number}    [config.pageSize]   - Rows per page (default 20)
 * @param {function}  [config.onRowClick] - Callback receiving (row data) on row click
 * @param {string}    [config.height]     - CSS height string e.g. '400px' (default '100%')
 * @returns {Tabulator|null} Tabulator instance, or null if Tabulator not available
 */
export function createDataTable({
    containerId,
    columns,
    data       = [],
    exportable = true,
    paginate   = true,
    pageSize   = 20,
    onRowClick = null,
    height     = '100%',
} = {}) {
    const parent = document.getElementById(containerId);
    if (!parent) {
        console.warn(`[module-components] createDataTable: container #${containerId} not found`);
        return null;
    }

    if (typeof Tabulator === 'undefined') {
        console.warn('[module-components] createDataTable: Tabulator is not loaded');
        parent.innerHTML = '<p style="color:var(--text-secondary);padding:16px;">Table library not available.</p>';
        return null;
    }

    // ── Optional export bar ──────────────────────────────────────────────────
    if (exportable) {
        const exportBar = document.createElement('div');
        exportBar.className = 'action-bar';
        exportBar.style.marginBottom = '8px';

        const right = document.createElement('div');
        right.className = 'action-bar-right';

        const csvBtn = document.createElement('button');
        csvBtn.className = 'btn btn-secondary';
        csvBtn.innerHTML = '<i class="fas fa-file-csv"></i> CSV';
        csvBtn.addEventListener('click', () => tableInstance && tableInstance.download('csv', 'export.csv'));

        right.appendChild(csvBtn);
        exportBar.appendChild(right);
        parent.appendChild(exportBar);
    }

    // ── Tabulator mount target ───────────────────────────────────────────────
    const tableDiv = document.createElement('div');
    parent.appendChild(tableDiv);

    // ── Tabulator config ─────────────────────────────────────────────────────
    const tabulatorConfig = {
        data,
        columns,
        height,
        layout:        'fitDataFill',
        responsiveLayout: 'collapse',
        pagination:    paginate ? 'local' : false,
        paginationSize: pageSize,
        paginationSizeSelector: paginate ? [10, 20, 50, 100] : false,
        movableColumns: true,
        resizableRows:  false,
        placeholder:    '<span style="color:var(--text-secondary);font-size:14px;">No data to display</span>',
        // Theme — use existing Tabulator theme already loaded by the platform
        theme: 'midnight',
    };

    if (onRowClick) {
        tabulatorConfig.rowClick = (_e, row) => onRowClick(row.getData());
    }

    const tableInstance = new Tabulator(tableDiv, tabulatorConfig);
    return tableInstance;
}

// ─────────────────────────────────────────────────────────────────────────────
// 5. Chart Panel (ApexCharts wrapper)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Creates a labelled chart panel containing an ApexCharts chart.
 * Returns an object with the ApexCharts instance and an `update()` helper.
 *
 * The chart is rendered into a new div appended to the element found by `containerId`.
 * Requires global `ApexCharts` to be loaded by the host page.
 *
 * @param {object}   config
 * @param {string}   config.containerId  - ID of the parent element to render into
 * @param {string}   config.title        - Panel heading text
 * @param {string}   [config.type]       - 'bar'|'line'|'area'|'donut'|'pie' (default 'bar')
 * @param {Array}    [config.series]     - ApexCharts series array
 * @param {Array}    [config.categories] - X-axis category labels
 * @param {string}   [config.height]     - Chart height CSS e.g. '300px' (default '300px')
 * @returns {{ chart: ApexCharts|null, update: function }}
 */
export function createChartPanel({
    containerId,
    title,
    type       = 'bar',
    series     = [],
    categories = [],
    height     = '300px',
} = {}) {
    const parent = document.getElementById(containerId);
    if (!parent) {
        console.warn(`[module-components] createChartPanel: container #${containerId} not found`);
        return { chart: null, update: () => {} };
    }

    // ── Wrapper card ─────────────────────────────────────────────────────────
    const card = document.createElement('div');
    card.className = 'dashboard-card';

    // Card header with title
    const header = document.createElement('div');
    header.className = 'card-header';

    const titleEl = document.createElement('div');
    titleEl.className = 'card-title';
    titleEl.textContent = title;
    header.appendChild(titleEl);

    card.appendChild(header);

    // Chart mount div
    const chartDiv = document.createElement('div');
    chartDiv.className = 'card-body';
    card.appendChild(chartDiv);

    parent.appendChild(card);

    // ── ApexCharts availability check ────────────────────────────────────────
    if (typeof ApexCharts === 'undefined') {
        console.warn('[module-components] createChartPanel: ApexCharts is not loaded');
        chartDiv.innerHTML = '<p style="color:var(--text-secondary);padding:16px;">Chart library not available.</p>';
        return { chart: null, update: () => {} };
    }

    // ── ApexCharts options (dark theme matching ui-standardization.css) ──────
    const chartOptions = {
        chart: {
            type,
            height,
            background: 'transparent',
            toolbar: { show: true },
            animations: { enabled: true },
            fontFamily: 'Roboto, Arial, sans-serif',
        },
        series,
        xaxis: {
            categories,
            labels: { style: { colors: '#b8bcc8' } },
            axisBorder: { color: '#444' },
        },
        yaxis: {
            labels: { style: { colors: '#b8bcc8' } },
        },
        grid: {
            borderColor: '#333',
        },
        theme: {
            mode: 'dark',
        },
        tooltip: {
            theme: 'dark',
        },
        legend: {
            labels: { colors: '#b8bcc8' },
        },
        stroke: {
            curve: 'smooth',
            width: type === 'line' || type === 'area' ? 2 : 0,
        },
        fill: {
            opacity: type === 'area' ? 0.4 : 1,
        },
        colors: [
            '#3b82f6', '#10b981', '#f59e0b',
            '#ef4444', '#8b5cf6', '#06b6d4',
        ],
    };

    const chartInstance = new ApexCharts(chartDiv, chartOptions);
    chartInstance.render();

    // ── update() helper ───────────────────────────────────────────────────────
    /**
     * Replace chart data without re-creating the chart.
     * @param {Array} newSeries     - ApexCharts series array
     * @param {Array} [newCategories] - New x-axis categories
     */
    function update(newSeries, newCategories = null) {
        if (!chartInstance) return;
        chartInstance.updateSeries(newSeries);
        if (newCategories) {
            chartInstance.updateOptions({ xaxis: { categories: newCategories } });
        }
    }

    return { chart: chartInstance, update };
}

// ─────────────────────────────────────────────────────────────────────────────
// 6. Loading / Empty state helpers
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Creates a centred loading spinner element.
 * Typically appended to a container while data is fetching,
 * then removed when data arrives.
 *
 * @param {string} [message] - Optional message text below the spinner
 * @returns {HTMLElement}
 */
export function createLoadingSpinner(message = 'Loading...') {
    const wrap = document.createElement('div');
    wrap.className = 'loading-spinner-wrap';
    wrap.style.cssText = 'display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px;gap:12px;';

    const spinner = document.createElement('i');
    spinner.className = 'fas fa-circle-notch fa-spin';
    spinner.style.cssText = 'font-size:24px;color:var(--primary-color);';

    const label = document.createElement('span');
    label.style.cssText = 'color:var(--text-secondary);font-size:var(--font-size-sm);';
    label.textContent = message;

    wrap.appendChild(spinner);
    wrap.appendChild(label);
    return wrap;
}

/**
 * Creates an empty-state illustration with icon, heading, and optional subtext.
 *
 * @param {object} config
 * @param {string} [config.icon]     - FontAwesome class (default 'fas fa-inbox')
 * @param {string} [config.heading]  - Main message (default 'No data')
 * @param {string} [config.subtext]  - Secondary message
 * @returns {HTMLElement}
 */
export function createEmptyState({ icon = 'fas fa-inbox', heading = 'No data', subtext = '' } = {}) {
    const wrap = document.createElement('div');
    wrap.style.cssText = 'display:flex;flex-direction:column;align-items:center;justify-content:center;padding:60px 20px;gap:12px;text-align:center;';

    const ico = document.createElement('i');
    ico.className = icon;
    ico.style.cssText = 'font-size:40px;color:var(--text-tertiary);';

    const h = document.createElement('div');
    h.style.cssText = 'font-size:var(--font-size-lg);color:var(--text-secondary);';
    h.textContent = heading;

    wrap.appendChild(ico);
    wrap.appendChild(h);

    if (subtext) {
        const sub = document.createElement('div');
        sub.style.cssText = 'font-size:var(--font-size-sm);color:var(--text-tertiary);max-width:360px;line-height:1.5;';
        sub.textContent = subtext;
        wrap.appendChild(sub);
    }

    return wrap;
}

/**
 * Creates an inline error message element.
 *
 * @param {string} message - Error text to display
 * @returns {HTMLElement}
 */
export function createErrorMessage(message) {
    const wrap = document.createElement('div');
    wrap.style.cssText = 'display:flex;align-items:center;gap:10px;padding:12px 16px;background:rgba(220,53,69,0.1);border:1px solid rgba(220,53,69,0.3);border-radius:var(--border-radius-md);color:var(--error-color);font-size:var(--font-size-sm);';

    const icon = document.createElement('i');
    icon.className = 'fas fa-exclamation-circle';
    icon.style.flexShrink = '0';

    const text = document.createElement('span');
    text.textContent = message;

    wrap.appendChild(icon);
    wrap.appendChild(text);
    return wrap;
}
