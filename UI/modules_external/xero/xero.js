// Import Quick Prompts module
import { XeroQuickPrompts } from './xero-quick-prompts.js';

// BaseModule polyfill (required since module-base.js is not globally loaded)
class BaseModule {
    constructor(moduleId) {
        this.moduleId = moduleId;
        this.manifest = null;
        this.backendUrl = window.API_BASE_URL || 'http://localhost:5001';
        console.log(` BaseModule constructor - moduleId: ${moduleId}`);
    }

    async initialize() {
        console.log(` BaseModule.initialize() called for ${this.moduleId}`);
        try {
            const response = await fetch(`${this.backendUrl}/api/modules/${this.moduleId}`);
            if (response.ok) {
                this.manifest = await response.json();
                console.log(` Manifest loaded for ${this.moduleId}:`, this.manifest);
            }
        } catch (error) {
            console.warn(` Failed to load manifest for ${this.moduleId}:`, error);
        }
    }
}
/**
 * Xero Accounting Module
 * Financial management for InHouse Print, Publishing, and Signs
 * 
 * @class XeroModule
 * @extends BaseModule
 * @created January 28, 2025
 * 
 * Features:
 * - Dashboard with financial metrics across 3 businesses
 * - Invoice management and tracking
 * - Contact (customer/supplier) management
 * - Payment tracking and reconciliation
 * - Chart of Accounts explorer
 * - Financial reports and analytics
 * - Multi-business support (Print, Publishing, Signs)
 */

// ============================================================================
// XERO MODULE CLASS
// ============================================================================

class XeroModule extends BaseModule {
    constructor() {
        super('xero');
        this.API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
        this.currentBusiness = 1; // Default to InHouse Print
        this.data = {
            invoices: [],
            contacts: [],
            payments: [],
            accounts: [],
            stats: {}
        };
        this.tables = {};
        this.charts = {};
        this.subTabs = new Map(); // Initialize Map for sub-tabs
        this.container = null; // Will be set when module is loaded
        // Selection tracking
        this.selectedItems = {
            invoices: new Set(),
            contacts: new Set(),
            payments: new Set(),
            accounts: new Set()
        };
        // Date range filters (default to 3 months)
        this.dateRanges = {
            invoices: 3,
            contacts: 3,
            payments: 3,
            accounts: null // No date filter for accounts
        };
    }

    /**
     * Calculate date range in months
     * @param {number|null} months - Number of months back, or null for all time
     * @returns {string|null} ISO date string (YYYY-MM-DD) or null
     */
    getDateRangeStart(months) {
        if (!months) return null;
        const date = new Date();
        date.setMonth(date.getMonth() - months);
        return date.toISOString().split('T')[0];
    }

    /**
     * Format date range for display in DD/MM/YYYY format
     * @param {number|null} months - Number of months to go back (null = all time)
     * @param {Date} endDate - End date (default: today)
     * @returns {string} Formatted date range string
     */
    formatDateRangeDisplay(months, endDate = new Date()) {
        if (!months) {
            return 'All Time';
        }

        const end = endDate;
        const start = new Date(end);
        start.setMonth(start.getMonth() - months);

        const formatDate = (date) => {
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            return `${day}/${month}/${year}`;
        };

        return `${formatDate(start)} - ${formatDate(end)}`;
    }

    /**
     * Get date range text for current period
     * @param {string} tabKey - 'invoices', 'contacts', or 'payments'
     * @returns {string} Formatted date range
     */
    getDateRangeText(tabKey = 'invoices') {
        const months = this.dateRanges[tabKey];
        return this.formatDateRangeDisplay(months);
    }

    /**
     * Parse Xero date format: /Date(1372291200000+0000)/
     * @param {string} dateStr - Xero date string
     * @returns {Date|null} JavaScript Date object or null
     */
    parseXeroDate(dateStr) {
        if (!dateStr || dateStr === 'undefined' || dateStr === 'null') return null;

        // Type validation - ensure dateStr is actually a string
        if (typeof dateStr !== 'string') {
            // If it's already a Date object, return it
            if (dateStr instanceof Date) return dateStr;
            // If it's a number (timestamp), convert it
            if (typeof dateStr === 'number') return new Date(dateStr);
            // Otherwise, try to convert to string
            dateStr = String(dateStr);
        }

        // Handle Xero format: /Date(timestamp+timezone)/
        const match = dateStr.match(/\/Date\((\d+)([\+\-]\d+)?\)\//)
        if (match) {
            const timestamp = parseInt(match[1]);
            return new Date(timestamp);
        }

        // Try standard ISO format
        try {
            const parsed = new Date(dateStr);
            if (!isNaN(parsed.getTime())) return parsed;
        } catch { }

        return null;
    }

    /**
     * Get tooltip information for dashboards
     * @returns {Object} Dashboard tooltip data
     */
    getTooltipData() {
        return {
            'aged-receivables': {
                title: 'Aged Receivables Report',
                introduction: 'Current snapshot of outstanding customer balances organized by age.',
                whatData: 'All unpaid invoices from Xero, categorized into aging buckets (Current, 1-30 days, 31-60 days, 61-90 days, 90+ days).',
                whatItShows: 'How much money customers owe and how long invoices have been outstanding. Helps identify collection priorities.',
                howToUse: 'Focus on older buckets (61-90, 90+) for follow-up. Large balances in 90+ require immediate attention.',
                visuals: 'Horizontal bar chart showing total amount in each age bucket.',
                differentiation: 'This is a current snapshot (not time-series). Shows aging of receivables, not payment trends.'
            },
            'sales-summary': {
                title: 'Sales Summary',
                introduction: 'High-level overview of total sales, average invoice value, and number of invoices.',
                whatData: 'Approved and paid invoices within selected date range, aggregated to show totals.',
                whatItShows: 'Top-line sales metrics: Total Revenue, Average Invoice Amount, Invoice Count.',
                howToUse: 'Quick health check for sales performance. Compare across time periods to identify growth or decline.',
                visuals: 'Three metric cards displaying key totals and averages.',
                differentiation: 'Summary metrics only (no drill-down). Use other dashboards for detailed breakdowns.'
            },
            'overdue-invoices': {
                title: 'Overdue Invoices',
                introduction: 'Real-time list of all past-due customer invoices requiring collection action.',
                whatData: 'Invoices with due dates before today that have outstanding amounts.',
                whatItShows: 'Customer name, invoice number, amount due, due date, and days overdue.',
                howToUse: 'Prioritize by days overdue or amount. Contact customers with oldest/largest balances first.',
                visuals: 'Sortable table with color-coded overdue indicators.',
                differentiation: 'Actionable list (not aggregate metrics). Shows specific invoices to chase.'
            },
            'revenue-trends': {
                title: 'Revenue Trends',
                introduction: 'Month-by-month sales performance over the selected time period.',
                whatData: 'Invoices grouped by month, showing total revenue for each month.',
                whatItShows: 'Sales patterns, seasonality, growth trends, and month-over-month changes.',
                howToUse: 'Identify peak months, seasonal patterns, or declining trends. Plan inventory and staffing.',
                visuals: 'Line chart showing revenue progression over months.',
                differentiation: 'Time-series analysis (not snapshot). Shows trends, not current state.'
            },
            'invoice-status': {
                title: 'Invoice Status Breakdown',
                introduction: 'Distribution of invoices across different payment statuses.',
                whatData: 'All invoices within date range, categorized by status (Draft, Submitted, Authorized, Paid).',
                whatItShows: 'How many invoices are in each processing stage. Identifies bottlenecks.',
                howToUse: 'High Draft count = need to finalize. High Authorized = need to send. High Submitted = awaiting payment.',
                visuals: 'Pie chart showing percentage breakdown by status.',
                differentiation: 'Status distribution (not payment status). Shows workflow state.'
            },
            'invoice-volume': {
                title: 'Invoice Volume Over Time',
                introduction: 'Count of invoices created each month to track activity levels.',
                whatData: 'Number of invoices grouped by month, regardless of amount or status.',
                whatItShows: 'Billing activity patterns, workload distribution, seasonal volume changes.',
                howToUse: 'Compare to revenue trends to spot average invoice size changes. Plan capacity for high-volume periods.',
                visuals: 'Bar chart showing invoice count per month.',
                differentiation: 'Count of invoices (not revenue). Shows activity volume, not financial performance.'
            },
            'contact-activity': {
                title: 'Contact Activity',
                introduction: 'List of all customers with their total invoices and combined amounts.',
                whatData: 'Each contact (customer) with sum of all invoice values and count of invoices.',
                whatItShows: 'Who your biggest customers are by total sales volume and transaction frequency.',
                howToUse: 'Identify VIP customers for relationship management. Spot one-time vs. repeat customers.',
                visuals: 'Sortable table with customer name, invoice count, and total amount.',
                differentiation: 'Customer-level aggregates (not invoice-level). Shows customer lifetime value.'
            },
            'inactive-customers': {
                title: 'Inactive Customers',
                introduction: 'Customers who have not been invoiced recently, indicating potential churn.',
                whatData: 'Contacts with last invoice date older than threshold (e.g., 90 days).',
                whatItShows: 'Which customers have gone quiet and may need re-engagement.',
                howToUse: 'Run re-engagement campaigns, check for service issues, or clean up contact list.',
                visuals: 'Table listing inactive contacts with last invoice date and days since last purchase.',
                differentiation: 'Churn indicator (not sales report). Shows absence of activity.'
            },
            'customer-ltv': {
                title: 'Customer Lifetime Value',
                introduction: 'Total historical revenue generated by each customer across all time.',
                whatData: 'Sum of all paid invoices for each contact since account creation.',
                whatItShows: 'Your most valuable customers by total lifetime spend.',
                howToUse: 'Prioritize retention efforts for high-LTV customers. Reward loyalty programs.',
                visuals: 'Horizontal bar chart ranking customers by total lifetime revenue.',
                differentiation: 'All-time totals (not time-bound). Shows historical value, not recent activity.'
            },
            'customer-segmentation': {
                title: 'Customer Segmentation',
                introduction: 'Customers grouped into tiers based on total spending (High, Medium, Low).',
                whatData: 'Contacts categorized by total invoice value into segments.',
                whatItShows: 'Distribution of customer base by value tier. Who are your whales vs. small accounts.',
                howToUse: 'Tailor marketing, support, and pricing strategies by segment. Focus on high-value retention.',
                visuals: 'Pie chart or bar chart showing count/revenue per segment.',
                differentiation: 'Categorical grouping (not ranking). Shows distribution across tiers.'
            },
            'product-customer-overlap': {
                title: 'Product-Customer Overlap Analysis',
                introduction: 'Which customers purchase which products, revealing cross-sell opportunities.',
                whatData: 'Invoice line items matched to customers, showing product purchase patterns.',
                whatItShows: 'Customer purchase diversity, product affinity, and bundling potential.',
                howToUse: 'Identify customers who buy only one product for upsell campaigns. Find product pairs often purchased together.',
                visuals: 'Matrix or network diagram showing customer-product relationships.',
                differentiation: 'Relationship analysis (not sales totals). Shows purchase patterns.'
            },
            'revenue-by-product': {
                title: 'Revenue by Product/Service',
                introduction: 'Breakdown of total revenue by individual products or services sold.',
                whatData: 'Invoice line items aggregated by product name/SKU with total revenue per item.',
                whatItShows: 'Which products are top sellers and revenue drivers.',
                howToUse: 'Focus marketing on best-sellers. Discontinue low-performers. Optimize pricing.',
                visuals: 'Horizontal bar chart ranking products by total revenue.',
                differentiation: 'Product-level analysis (not customer-level). Shows what sells, not who buys.'
            },
            'invoice-reports-manual': {
                title: 'Manual Invoice Reports',
                introduction: 'Curated collection of specialized Xero reports with custom filtering.',
                whatData: 'Multi-month invoice data with advanced filters (status, date ranges, customers).',
                whatItShows: 'Flexible views of invoice data for custom analysis needs.',
                howToUse: 'Select report type, adjust filters, and generate on-demand tables.',
                visuals: 'Dynamic tables with column sorting and CSV export.',
                differentiation: 'User-driven queries (not pre-aggregated). Flexible exploration tool.'
            },
            'invoice-reports-auto-invoices': {
                title: 'Automated Invoice Analysis',
                introduction: 'Pre-configured report showing all invoices with key details.',
                whatData: '12 months of invoice records with contact, amount, status, and dates.',
                whatItShows: 'Complete invoice history with filterable columns.',
                howToUse: 'Search for specific invoices, analyze patterns, or export for external tools.',
                visuals: 'Paginated table with search and sort capabilities.',
                differentiation: 'Raw invoice list (not aggregated). Detail-level data access.'
            },
            'invoice-reports-auto-contacts': {
                title: 'Contact Performance Report',
                introduction: 'Automated analysis of customer-level metrics and payment behavior.',
                whatData: 'Contact list with total invoices, revenue, average order value, and payment punctuality.',
                whatItShows: 'Customer health scores, reliability, and profitability.',
                howToUse: 'Identify reliable vs. problematic customers. Adjust credit terms.',
                visuals: 'Table with customer metrics and color-coded performance indicators.',
                differentiation: 'Contact-centric (not invoice-centric). Shows customer behavior patterns.'
            },
            'invoice-reports-auto-status': {
                title: 'Status Flow Analysis',
                introduction: 'Tracking invoice progression through workflow stages over time.',
                whatData: 'Status change timestamps and counts showing how long invoices stay in each stage.',
                whatItShows: 'Process efficiency, bottlenecks, and average time to payment.',
                howToUse: 'Optimize workflow by reducing time in bottleneck stages.',
                visuals: 'Flow diagram or timeline showing status transitions.',
                differentiation: 'Process analysis (not financial). Shows operational efficiency.'
            }
        };
    }

    /**
     * Initialize tooltip functionality for all dashboard info icons
     */
    initializeTooltips() {
        console.log('[Xero] Initializing dashboard tooltips...');

        // Prevent multiple initializations
        if (this._tooltipsInitialized) {
            console.log('[Xero] Tooltips already initialized, skipping...');
            return;
        }
        this._tooltipsInitialized = true;

        // Wait for DOM to be ready
        setTimeout(() => {
            const tooltipData = this.getTooltipData();
            let currentTooltip = null;
            let lastIconHovered = null;

            // Use mouseover (bubbles) instead of mouseenter (doesn't bubble)
            document.addEventListener('mouseover', (e) => {
                // Safety check for target
                if (!e.target || !e.target.classList) return;
                if (!e.target.classList.contains('xero-info-icon')) return;

                // Prevent duplicate tooltips for same icon
                if (lastIconHovered === e.target) return;
                lastIconHovered = e.target;

                const dashboardId = e.target.dataset.tooltip;
                console.log('[Xero] Info icon hovered:', dashboardId);

                const data = tooltipData[dashboardId];

                if (!data) {
                    console.warn(`[Xero] No tooltip data for dashboard: ${dashboardId}`);
                    return;
                }

                // Remove any existing tooltip
                if (currentTooltip) {
                    currentTooltip.remove();
                    currentTooltip = null;
                }

                // Create tooltip element
                currentTooltip = this.createTooltipElement(data);
                document.body.appendChild(currentTooltip);

                // Position tooltip near icon
                this.positionTooltip(currentTooltip, e.target);

                // Show tooltip with slight delay
                setTimeout(() => {
                    if (currentTooltip && currentTooltip.classList) {
                        currentTooltip.classList.add('show');
                    }
                }, 50);

            }, true); // Use capture phase

            // Use mouseout (bubbles) instead of mouseleave (doesn't bubble)
            document.addEventListener('mouseout', (e) => {
                // Safety check for target
                if (!e.target || !e.target.classList) return;
                if (!e.target.classList.contains('xero-info-icon')) return;

                lastIconHovered = null;

                if (currentTooltip) {
                    if (currentTooltip.classList) {
                        currentTooltip.classList.remove('show');
                    }
                    setTimeout(() => {
                        if (currentTooltip && currentTooltip.parentNode) {
                            currentTooltip.remove();
                            currentTooltip = null;
                        }
                    }, 200);
                }
            }, true); // Use capture phase

            console.log('[Xero] ✅ Tooltip system initialized (using event delegation with mouseover/mouseout)');
        }, 500);
    }

    /**
     * Re-attach tooltip listeners after dynamic content loads
     * Call this after rendering dashboards with info icons
     */
    refreshTooltips() {
        console.log('[Xero] Refreshing tooltip listeners for dynamic content...');
        // Tooltips already use event delegation, just log for debugging
        const icons = document.querySelectorAll('.xero-info-icon');
        console.log(`[Xero] Found ${icons.length} info icons`);

        // Test first icon if it exists
        if (icons.length > 0) {
            const testIcon = icons[0];
            console.log('[Xero] Test icon data-tooltip:', testIcon.dataset.tooltip);
        }
    }

    /**
     * Create tooltip DOM element from data
     * @param {Object} data - Tooltip content data
     * @returns {HTMLElement} Tooltip element
     */
    createTooltipElement(data) {
        const tooltip = document.createElement('div');
        tooltip.className = 'xero-info-tooltip';

        tooltip.innerHTML = `
            <h5>${data.title}</h5>
            
            <div class="tooltip-section">
                <div class="tooltip-label">Introduction</div>
                <div class="tooltip-text">${data.introduction}</div>
            </div>
            
            <div class="tooltip-section">
                <div class="tooltip-label">What Data</div>
                <div class="tooltip-text">${data.whatData}</div>
            </div>
            
            <div class="tooltip-section">
                <div class="tooltip-label">What It Shows</div>
                <div class="tooltip-text">${data.whatItShows}</div>
            </div>
            
            <div class="tooltip-section">
                <div class="tooltip-label">How To Use</div>
                <div class="tooltip-text">${data.howToUse}</div>
            </div>
            
            <div class="tooltip-section">
                <div class="tooltip-label">Visuals</div>
                <div class="tooltip-text">${data.visuals}</div>
            </div>
            
            <div class="tooltip-section">
                <div class="tooltip-label">Differentiation</div>
                <div class="tooltip-text">${data.differentiation}</div>
            </div>
        `;

        return tooltip;
    }

    /**
     * Position tooltip near icon, adjusting to stay on screen
     * @param {HTMLElement} tooltip - Tooltip element
     * @param {HTMLElement} icon - Info icon element
     */
    positionTooltip(tooltip, icon) {
        const iconRect = icon.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;

        // Default position: to the right of icon
        let left = iconRect.right + 10;
        let top = iconRect.top;

        // Adjust if tooltip goes off right edge
        if (left + tooltipRect.width > viewportWidth - 20) {
            left = iconRect.left - tooltipRect.width - 10;
        }

        // Adjust if tooltip goes off left edge
        if (left < 20) {
            left = 20;
        }

        // Adjust if tooltip goes off bottom
        if (top + tooltipRect.height > viewportHeight - 20) {
            top = viewportHeight - tooltipRect.height - 20;
        }

        // Adjust if tooltip goes off top
        if (top < 20) {
            top = 20;
        }

        tooltip.style.left = `${left}px`;
        tooltip.style.top = `${top}px`;
    }

    /**
     * Format date for display
     * @param {Date|string} date - Date object or string
     * @returns {string} Formatted date string
     */
    formatDate(date) {
        if (!date || date === 'null' || date === 'undefined') return 'N/A';
        if (typeof date === 'string') {
            date = this.parseXeroDate(date);
        }
        if (!date || isNaN(date.getTime())) return 'Invalid Date';
        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    }

    /**
     * Create universal date range picker with comparison options
     * @param {string} containerId - ID of container element
     * @param {Function} onChangeCallback - Callback when date range changes
     * @returns {Object} Date range controller
     */
    createDateRangePicker(containerId, onChangeCallback) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        const presets = [
            { label: 'This Month', value: 'this_month' },
            { label: 'Last Month', value: 'last_month' },
            { label: 'This Quarter', value: 'this_quarter' },
            { label: 'Last Quarter', value: 'last_quarter' },
            { label: 'This Year', value: 'this_year' },
            { label: 'Last Year', value: 'last_year' },
            { label: 'Last 3 Months', value: 'last_3_months' },
            { label: 'Last 6 Months', value: 'last_6_months' },
            { label: 'Last 12 Months', value: 'last_12_months' },
            { label: 'Custom', value: 'custom' }
        ];

        const compareOptions = [
            { label: 'None', value: 'none' },
            { label: 'Same Period Last Year', value: 'yoy' },
            { label: 'Previous Period', value: 'previous' }
        ];

        container.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding: 16px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 16px;">
                <div>
                    <label style="display: block; font-size: 12px; color: #8b949e; margin-bottom: 6px;">📅 Quick Select</label>
                    <div style="display: flex; flex-wrap: wrap; gap: 6px;" id="${containerId}-presets"></div>
                </div>
                <div>
                    <label style="display: block; font-size: 12px; color: #8b949e; margin-bottom: 6px;">🔄 Compare To</label>
                    <select id="${containerId}-compare" style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #c9d1d9; font-size: 14px;">
                        ${compareOptions.map(opt => `<option value="${opt.value}">${opt.label}</option>`).join('')}
                    </select>
                </div>
                <div id="${containerId}-custom-dates" style="grid-column: 1 / -1; display: none; gap: 12px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div>
                            <label style="display: block; font-size: 12px; color: #8b949e; margin-bottom: 6px;">From</label>
                            <input type="date" id="${containerId}-from" style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #c9d1d9;">
                        </div>
                        <div>
                            <label style="display: block; font-size: 12px; color: #8b949e; margin-bottom: 6px;">To</label>
                            <input type="date" id="${containerId}-to" style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #c9d1d9;">
                        </div>
                    </div>
                </div>
            </div>
        `;

        const presetsContainer = document.getElementById(`${containerId}-presets`);
        presets.forEach(preset => {
            const btn = document.createElement('button');
            btn.textContent = preset.label;
            btn.className = 'date-preset-btn';
            btn.dataset.value = preset.value;
            btn.style.cssText = 'padding: 6px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 4px; color: #c9d1d9; font-size: 13px; cursor: pointer; transition: all 0.2s;';
            btn.addEventListener('mouseenter', () => btn.style.background = 'rgba(19, 181, 234, 0.15)');
            btn.addEventListener('mouseleave', () => btn.style.background = btn.classList.contains('active') ? '#13B5EA' : '#21262d');
            btn.addEventListener('click', () => handlePresetClick(preset.value));
            presetsContainer.appendChild(btn);
        });

        const customDatesDiv = document.getElementById(`${containerId}-custom-dates`);
        const fromInput = document.getElementById(`${containerId}-from`);
        const toInput = document.getElementById(`${containerId}-to`);
        const compareSelect = document.getElementById(`${containerId}-compare`);

        function calculateDateRange(presetValue) {
            const now = new Date();
            let from, to;

            switch (presetValue) {
                case 'this_month':
                    from = new Date(now.getFullYear(), now.getMonth(), 1);
                    to = now;
                    break;
                case 'last_month':
                    from = new Date(now.getFullYear(), now.getMonth() - 1, 1);
                    to = new Date(now.getFullYear(), now.getMonth(), 0);
                    break;
                case 'this_quarter':
                    const q = Math.floor(now.getMonth() / 3);
                    from = new Date(now.getFullYear(), q * 3, 1);
                    to = now;
                    break;
                case 'last_quarter':
                    const lq = Math.floor(now.getMonth() / 3) - 1;
                    from = new Date(now.getFullYear(), lq * 3, 1);
                    to = new Date(now.getFullYear(), lq * 3 + 3, 0);
                    break;
                case 'this_year':
                    from = new Date(now.getFullYear(), 0, 1);
                    to = now;
                    break;
                case 'last_year':
                    from = new Date(now.getFullYear() - 1, 0, 1);
                    to = new Date(now.getFullYear() - 1, 11, 31);
                    break;
                case 'last_3_months':
                    from = new Date(now.getFullYear(), now.getMonth() - 3, now.getDate());
                    to = now;
                    break;
                case 'last_6_months':
                    from = new Date(now.getFullYear(), now.getMonth() - 6, now.getDate());
                    to = now;
                    break;
                case 'last_12_months':
                    from = new Date(now.getFullYear(), now.getMonth() - 12, now.getDate());
                    to = now;
                    break;
                default:
                    return null;
            }

            return {
                from: from.toISOString().split('T')[0],
                to: to.toISOString().split('T')[0]
            };
        }

        function handlePresetClick(value) {
            // Update button styles
            document.querySelectorAll('.date-preset-btn').forEach(btn => {
                btn.classList.remove('active');
                btn.style.background = '#21262d';
                btn.style.borderColor = '#30363d';
            });

            const clickedBtn = document.querySelector(`[data-value="${value}"]`);
            if (clickedBtn) {
                clickedBtn.classList.add('active');
                clickedBtn.style.background = '#13B5EA';
                clickedBtn.style.borderColor = '#13B5EA';
            }

            if (value === 'custom') {
                customDatesDiv.style.display = 'block';
            } else {
                customDatesDiv.style.display = 'none';
                const range = calculateDateRange(value);
                if (range && onChangeCallback) {
                    onChangeCallback(range, compareSelect.value);
                }
            }
        }

        // Handle custom date changes
        [fromInput, toInput].forEach(input => {
            input.addEventListener('change', () => {
                if (fromInput.value && toInput.value && onChangeCallback) {
                    const dates = {
                        from: fromInput.value,
                        to: toInput.value
                    };

                    // Auto-calculate YoY comparison dates for custom ranges
                    if (compareSelect.value === 'yoy') {
                        const fromDate = new Date(fromInput.value);
                        const toDate = new Date(toInput.value);
                        fromDate.setFullYear(fromDate.getFullYear() - 1);
                        toDate.setFullYear(toDate.getFullYear() - 1);
                        dates.compare_from = fromDate.toISOString().split('T')[0];
                        dates.compare_to = toDate.toISOString().split('T')[0];
                    } else if (compareSelect.value === 'previous') {
                        const fromDate = new Date(fromInput.value);
                        const toDate = new Date(toInput.value);
                        const daysDiff = Math.floor((toDate - fromDate) / (1000 * 60 * 60 * 24));
                        const compareToDate = new Date(fromDate);
                        compareToDate.setDate(compareToDate.getDate() - 1);
                        const compareFromDate = new Date(compareToDate);
                        compareFromDate.setDate(compareFromDate.getDate() - daysDiff);
                        dates.compare_from = compareFromDate.toISOString().split('T')[0];
                        dates.compare_to = compareToDate.toISOString().split('T')[0];
                    }

                    onChangeCallback(dates, compareSelect.value);
                }
            });
        });

        // Handle comparison change
        compareSelect.addEventListener('change', () => {
            const activeBtn = document.querySelector('.date-preset-btn.active');
            if (activeBtn) {
                const value = activeBtn.dataset.value;
                if (value === 'custom' && fromInput.value && toInput.value) {
                    const dates = {
                        from: fromInput.value,
                        to: toInput.value
                    };

                    // Auto-calculate comparison dates for custom ranges
                    if (compareSelect.value === 'yoy') {
                        const fromDate = new Date(fromInput.value);
                        const toDate = new Date(toInput.value);
                        fromDate.setFullYear(fromDate.getFullYear() - 1);
                        toDate.setFullYear(toDate.getFullYear() - 1);
                        dates.compare_from = fromDate.toISOString().split('T')[0];
                        dates.compare_to = toDate.toISOString().split('T')[0];
                    } else if (compareSelect.value === 'previous') {
                        const fromDate = new Date(fromInput.value);
                        const toDate = new Date(toInput.value);
                        const daysDiff = Math.floor((toDate - fromDate) / (1000 * 60 * 60 * 24));
                        const compareToDate = new Date(fromDate);
                        compareToDate.setDate(compareToDate.getDate() - 1);
                        const compareFromDate = new Date(compareToDate);
                        compareFromDate.setDate(compareFromDate.getDate() - daysDiff);
                        dates.compare_from = compareFromDate.toISOString().split('T')[0];
                        dates.compare_to = compareToDate.toISOString().split('T')[0];
                    }

                    onChangeCallback(dates, compareSelect.value);
                } else if (value !== 'custom') {
                    const range = calculateDateRange(value);
                    if (range && onChangeCallback) {
                        onChangeCallback(range, compareSelect.value);
                    }
                }
            }
        });

        // Set default to last 12 months
        handlePresetClick('last_12_months');

        return {
            getDateRange: () => {
                const activeBtn = document.querySelector('.date-preset-btn.active');
                if (!activeBtn) return null;
                const value = activeBtn.dataset.value;
                if (value === 'custom') {
                    return { from: fromInput.value, to: toInput.value };
                }
                return calculateDateRange(value);
            },
            getComparison: () => compareSelect.value
        };
    }

    /**
     * Create export to clipboard button for dashboards
     * @param {string} containerId - Container element ID
     * @param {Function} getDataCallback - Function that returns dashboard data to export
     * @param {string} dashboardName - Name of the dashboard for context
     * @param {string} endpoint - API endpoint used to fetch the data
     */
    createExportButton(containerId, getDataCallback, dashboardName, endpoint) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const exportBtn = document.createElement('button');
        exportBtn.innerHTML = '<i class="fas fa-clipboard"></i> Export for AI';
        exportBtn.className = 'export-to-clipboard-btn';
        exportBtn.style.cssText = `
            position: absolute;
            top: 16px;
            right: 16px;
            padding: 8px 16px;
            background: linear-gradient(135deg, #8957e5 0%, #9b6df7 100%);
            border: none;
            border-radius: 6px;
            color: white;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(137, 87, 229, 0.3);
            transition: all 0.2s;
            z-index: 100;
        `;

        exportBtn.addEventListener('mouseenter', () => {
            exportBtn.style.transform = 'translateY(-2px)';
            exportBtn.style.boxShadow = '0 4px 12px rgba(137, 87, 229, 0.4)';
        });

        exportBtn.addEventListener('mouseleave', () => {
            exportBtn.style.transform = 'translateY(0)';
            exportBtn.style.boxShadow = '0 2px 8px rgba(137, 87, 229, 0.3)';
        });

        exportBtn.addEventListener('click', async () => {
            try {
                exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Copying...';
                exportBtn.disabled = true;

                const data = await getDataCallback();
                const exportText = this.formatDataForAI(data, dashboardName, endpoint);

                await navigator.clipboard.writeText(exportText);

                exportBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                exportBtn.style.background = 'linear-gradient(135deg, #3fb950 0%, #2ea043 100%)';

                setTimeout(() => {
                    exportBtn.innerHTML = '<i class="fas fa-clipboard"></i> Export for AI';
                    exportBtn.style.background = 'linear-gradient(135deg, #8957e5 0%, #9b6df7 100%)';
                    exportBtn.disabled = false;
                }, 2000);

            } catch (error) {
                console.error('Failed to copy to clipboard:', error);
                exportBtn.innerHTML = '<i class="fas fa-times"></i> Failed';
                exportBtn.style.background = 'linear-gradient(135deg, #f85149 0%, #d73027 100%)';

                setTimeout(() => {
                    exportBtn.innerHTML = '<i class="fas fa-clipboard"></i> Export for AI';
                    exportBtn.style.background = 'linear-gradient(135deg, #8957e5 0%, #9b6df7 100%)';
                    exportBtn.disabled = false;
                }, 2000);
            }
        });

        container.style.position = 'relative';
        container.insertBefore(exportBtn, container.firstChild);
    }

    /**
     * Format dashboard data for AI interpretation
     * @param {Object} data - Dashboard data object
     * @param {string} dashboardName - Name of the dashboard
     * @param {string} endpoint - API endpoint used
     * @returns {string} Formatted text for AI
     */
    formatDataForAI(data, dashboardName, endpoint) {
        const timestamp = new Date().toISOString();

        let output = `# Xero ${dashboardName} - Export for AI Analysis\n`;
        output += `**Exported:** ${new Date().toLocaleString()}\n`;
        output += `**Dashboard:** ${dashboardName}\n`;
        output += `**API Endpoint:** ${endpoint}\n\n`;

        // Add data source queries
        output += `## 📊 Data Source Information\n\n`;
        output += `### Primary Endpoint\n`;
        output += `\`\`\`\n${endpoint}\n\`\`\`\n\n`;

        output += `### SQL Queries Used (Backend)\n`;
        output += `To retrieve raw data or verify calculations, use these SQL patterns:\n\n`;

        if (dashboardName.includes('Business Comparison')) {
            output += `\`\`\`sql\n`;
            output += `-- Business revenue and outstanding by date range\n`;
            output += `SELECT \n`;
            output += `    business_name,\n`;
            output += `    SUM(CASE WHEN status = 'PAID' THEN total ELSE 0 END) as total_revenue,\n`;
            output += `    SUM(CASE WHEN status NOT IN ('PAID', 'VOIDED') THEN total ELSE 0 END) as outstanding,\n`;
            output += `    COUNT(*) as invoice_count,\n`;
            output += `    AVG(total) as avg_invoice_value\n`;
            output += `FROM xero_invoices\n`;
            output += `WHERE date BETWEEN '${data.date_range?.from}' AND '${data.date_range?.to}'\n`;
            output += `GROUP BY business_name;\n`;
            output += `\n`;
            output += `-- Collection days calculation\n`;
            output += `SELECT \n`;
            output += `    business_name,\n`;
            output += `    AVG(JULIANDAY(fully_paid_date) - JULIANDAY(date)) as avg_collection_days\n`;
            output += `FROM xero_invoices\n`;
            output += `WHERE status = 'PAID' AND fully_paid_date IS NOT NULL\n`;
            output += `GROUP BY business_name;\n`;
            output += `\`\`\`\n\n`;
        } else if (dashboardName.includes('Consolidated Revenue')) {
            output += `\`\`\`sql\n`;
            output += `-- Consolidated revenue across all businesses\n`;
            output += `SELECT \n`;
            output += `    strftime('%Y-%m', date) as month,\n`;
            output += `    SUM(CASE WHEN status = 'PAID' THEN total ELSE 0 END) as revenue,\n`;
            output += `    SUM(CASE WHEN status NOT IN ('PAID', 'VOIDED') THEN total ELSE 0 END) as outstanding\n`;
            output += `FROM xero_invoices\n`;
            output += `WHERE date BETWEEN '${data.date_range?.from}' AND '${data.date_range?.to}'\n`;
            output += `GROUP BY month ORDER BY month;\n`;
            output += `\n`;
            output += `-- Cash flow projection by aging\n`;
            output += `SELECT \n`;
            output += `    CASE \n`;
            output += `        WHEN JULIANDAY('now') - JULIANDAY(date) <= 30 THEN '0-30 days'\n`;
            output += `        WHEN JULIANDAY('now') - JULIANDAY(date) <= 60 THEN '31-60 days'\n`;
            output += `        WHEN JULIANDAY('now') - JULIANDAY(date) <= 90 THEN '61-90 days'\n`;
            output += `        ELSE '90+ days'\n`;
            output += `    END as aging_bucket,\n`;
            output += `    SUM(total) as outstanding_amount\n`;
            output += `FROM xero_invoices\n`;
            output += `WHERE status NOT IN ('PAID', 'VOIDED')\n`;
            output += `GROUP BY aging_bucket;\n`;
            output += `\`\`\`\n\n`;
        } else if (dashboardName.includes('Seasonality')) {
            output += `\`\`\`sql\n`;
            output += `-- Monthly revenue patterns over multiple years\n`;
            output += `SELECT \n`;
            output += `    strftime('%Y', date) as year,\n`;
            output += `    strftime('%m', date) as month,\n`;
            output += `    SUM(CASE WHEN status = 'PAID' THEN total ELSE 0 END) as revenue,\n`;
            output += `    COUNT(*) as invoice_count\n`;
            output += `FROM xero_invoices\n`;
            output += `WHERE business_id = ${data.business_id || 1}\n`;
            output += `GROUP BY year, month\n`;
            output += `ORDER BY year, month;\n`;
            output += `\n`;
            output += `-- Average revenue by month across all years\n`;
            output += `SELECT \n`;
            output += `    strftime('%m', date) as month_num,\n`;
            output += `    AVG(monthly_revenue) as avg_revenue,\n`;
            output += `    MIN(monthly_revenue) as min_revenue,\n`;
            output += `    MAX(monthly_revenue) as max_revenue\n`;
            output += `FROM (\n`;
            output += `    SELECT strftime('%Y-%m', date) as month, SUM(total) as monthly_revenue\n`;
            output += `    FROM xero_invoices WHERE status = 'PAID'\n`;
            output += `    GROUP BY month\n`;
            output += `) GROUP BY month_num;\n`;
            output += `\`\`\`\n\n`;
        } else if (dashboardName.includes('Forecast')) {
            output += `\`\`\`sql\n`;
            output += `-- Historical monthly revenue for forecasting\n`;
            output += `SELECT \n`;
            output += `    strftime('%Y-%m', date) as month,\n`;
            output += `    SUM(CASE WHEN status = 'PAID' THEN total ELSE 0 END) as revenue\n`;
            output += `FROM xero_invoices\n`;
            output += `WHERE business_id = ${data.business_id || 1}\n`;
            output += `    AND date >= date('now', '-${data.historical_months || 12} months')\n`;
            output += `GROUP BY month\n`;
            output += `ORDER BY month;\n`;
            output += `\`\`\`\n\n`;
        }

        // Add date range context
        if (data.date_range) {
            output += `## 📅 Date Range\n`;
            output += `- **From:** ${data.date_range.from}\n`;
            output += `- **To:** ${data.date_range.to}\n`;
            if (data.comparison_period) {
                output += `- **Comparison Period:** ${data.comparison_period.from} to ${data.comparison_period.to}\n`;
            }
            output += `\n`;
        }

        // Add dashboard-specific data
        output += `## 📈 Dashboard Data\n\n`;
        output += `\`\`\`json\n${JSON.stringify(data, null, 2)}\n\`\`\`\n\n`;

        // Add instructions for AI
        output += `## 🤖 AI Analysis Instructions\n\n`;
        output += `This data export contains:\n`;
        output += `1. **API Endpoint:** The backend endpoint that generated this data\n`;
        output += `2. **SQL Queries:** Reference queries to retrieve raw data from the database\n`;
        output += `3. **Dashboard Data:** Complete JSON response with all metrics, charts, and tables\n\n`;
        output += `**To analyze this data, you can:**\n`;
        output += `- Interpret trends and patterns in the metrics\n`;
        output += `- Compare year-over-year growth rates\n`;
        output += `- Identify anomalies or outliers\n`;
        output += `- Generate insights and recommendations\n`;
        output += `- Run the provided SQL queries to verify calculations or get more detail\n\n`;
        output += `**To get raw data from the database:**\n`;
        output += `Use the SQL queries provided above in the "SQL Queries Used" section. These queries:\n`;
        output += `- Show exactly how the backend calculated the displayed metrics\n`;
        output += `- Can be modified to drill down into specific businesses, dates, or transactions\n`;
        output += `- Include joins and aggregations used for complex calculations\n\n`;
        output += `**Example questions to ask:**\n`;
        output += `- "What's driving the revenue growth in Q4?"\n`;
        output += `- "Which business has the best collection days and why?"\n`;
        output += `- "Are there any concerning trends in the cash flow aging?"\n`;
        output += `- "What seasonality patterns should we plan for?"\n`;
        output += `- "How confident should we be in the 6-month forecast?"\n`;

        return output;
    }

    /**
     * Create Plotly chart with standard theming
     * @param {string} containerId - Chart container ID
     * @param {Object} data - Plotly data array
     * @param {Object} layout - Plotly layout object
     * @param {Object} config - Plotly config object
     */
    createChart(containerId, data, layout = {}, config = {}) {
        const defaultLayout = {
            paper_bgcolor: '#0d1117',
            plot_bgcolor: '#161b22',
            font: { color: '#c9d1d9', family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' },
            margin: { l: 50, r: 50, t: 50, b: 50 },
            xaxis: { gridcolor: '#21262d', zeroline: false },
            yaxis: { gridcolor: '#21262d', zeroline: false },
            showlegend: true,
            legend: { bgcolor: '#0d1117', bordercolor: '#30363d', borderwidth: 1 }
        };

        const defaultConfig = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            ...config
        };

        const mergedLayout = { ...defaultLayout, ...layout };

        const container = document.getElementById(containerId);
        if (container) {
            Plotly.newPlot(containerId, data, mergedLayout, defaultConfig);
        }
    }

    /**
     * Calculate YoY comparison metrics
     * @param {number} current - Current period value
     * @param {number} previous - Previous period value
     * @returns {Object} Comparison metrics
     */
    calculateYoYMetrics(current, previous) {
        const change = current - previous;
        const percentChange = previous !== 0 ? ((change / previous) * 100) : 0;
        const arrow = percentChange > 0 ? '⬆' : percentChange < 0 ? '⬇' : '━';
        const color = percentChange > 0 ? '#3fb950' : percentChange < 0 ? '#f85149' : '#8b949e';

        return {
            change,
            percentChange: percentChange.toFixed(1),
            arrow,
            color,
            formatted: `${arrow} ${Math.abs(percentChange).toFixed(1)}%`
        };
    }

    /**
     * Initialize module
     */
    async initialize() {
        console.log('Initializing Xero module...');

        try {
            // Call parent initialization
            await super.initialize();

            // Initialize Quick Prompts module with reference to this instance
            XeroQuickPrompts.init(this);

            // CRITICAL FIX DEC 16: Inject base HTML structure first
            this.injectBaseStructure();

            // Create business selector in header
            this.createBusinessSelector();

            // Initialize sub-tabs
            this.initializeSubTabs();

            // Initialize dashboard tooltips
            this.initializeTooltips();

            // CRITICAL FIX DEC 21: Load data in background (don't block initialization)
            // This allows UI to render immediately while data loads
            this.loadDashboard().catch(error => {
                console.error('Failed to load dashboard:', error);
                this.showError('Failed to load dashboard: ' + error.message);
            });

            console.log('✅ Xero module initialized successfully (data loading in background)');
        } catch (error) {
            console.error('Failed to initialize Xero module:', error);
            this.showError('Failed to initialize Xero module: ' + error.message);
        }
    }

    /**
     * Inject base HTML structure into empty container
     */
    injectBaseStructure() {
        if (!this.container) {
            console.error('[Xero] Cannot inject structure - container not set');
            return;
        }

        // SHOW LOADING SPINNER IMMEDIATELY
        this.container.innerHTML = `
            <div class="xero-module-wrapper">
                <div class="module-header" style="display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #0d1117; border-bottom: 1px solid #30363d;">
                    <div class="module-header-left">
                        <h2 style="margin: 0; color: #ffffff; font-size: 24px;">
                            <i class="fas fa-file-invoice-dollar" style="margin-right: 10px; color: #13B5EA;"></i>
                            Xero Accounting
                        </h2>
                    </div>
                    <div class="module-header-right"></div>
                </div>
                <div class="xero-content">
                    <div class="xero-loading-initial" style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 500px; gap: 20px;">
                        <div class="xero-spinner" style="width: 64px; height: 64px; border: 5px solid #30363d; border-top-color: #13B5EA; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                        <p style="color: #8b949e; font-size: 16px; margin: 0; font-weight: 500;">Loading Xero Accounting...</p>
                        <p style="color: #6e7681; font-size: 13px; margin: 0;">Connecting to Xero API and loading data</p>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Create business selector dropdown
     */
    createBusinessSelector() {
        if (!this.container) {
            console.warn('[Xero] Container not set, skipping business selector');
            return;
        }

        const header = this.container.querySelector('.module-header-right');
        if (!header) {
            console.warn('[Xero] Module header not found');
            return;
        }

        const businesses = [
            { id: 1, name: 'InHouse Print', color: '#00509E' },
            { id: 2, name: 'InHouse Publishing', color: '#7B2D26' },
            { id: 3, name: 'InHouse Signs', color: '#F7941D' }
        ];

        const selector = document.createElement('div');
        selector.className = 'xero-business-selector';
        selector.innerHTML = `
            <label for="xero-business-select">
                <i class="fas fa-building"></i> Business:
            </label>
            <select id="xero-business-select" class="xero-select">
                ${businesses.map(b => `
                    <option value="${b.id}" ${b.id === this.currentBusiness ? 'selected' : ''}>
                        ${b.name}
                    </option>
                `).join('')}
            </select>
        `;

        // Insert before refresh button
        const refreshBtn = header.querySelector('[data-action="refresh"]');
        header.insertBefore(selector, refreshBtn);

        // Add change event listener
        const select = selector.querySelector('select');
        select.addEventListener('change', (e) => {
            this.currentBusiness = parseInt(e.target.value);
            this.onBusinessChange();
        });
    }

    /**
     * Handle business change
     */
    async onBusinessChange() {
        console.log(`Business changed to: ${this.currentBusiness}`);

        // Reload current tab data
        const activeTab = this.activeSubTab || 'dashboard';
        switch (activeTab) {
            case 'dashboard':
                await this.loadDashboard();
                break;
            case 'invoices':
                await this.loadInvoices();
                // Also reload invoice reports if visible
                const invoiceReportsContent = document.getElementById('xero-invoice-reports-content');
                if (invoiceReportsContent && invoiceReportsContent.style.display !== 'none') {
                    const lastReportType = this.lastInvoiceReportType;
                    if (lastReportType) {
                        console.log('[Xero] Refreshing invoice reports after business change');
                        // Re-trigger the last report
                        if (lastReportType === 'auto-invoices') await this.showAutoInvoices();
                        else if (lastReportType === 'auto-contacts') await this.showAutoContacts();
                        else if (lastReportType === 'auto-status') await this.showAutoStatus();
                    }
                }
                break;
            case 'contacts':
                await this.loadContacts();
                // Also reload contact reports if visible
                const contactsReportsContent = document.getElementById('xero-contacts-reports-content');
                if (contactsReportsContent && contactsReportsContent.style.display !== 'none') {
                    const lastContactReportType = this.lastContactReportType;
                    if (lastContactReportType) {
                        console.log('[Xero] Refreshing contact reports after business change');
                        // Re-trigger the last report
                        if (lastContactReportType === 'intelligence') await this.showCustomerIntelligence();
                        else if (lastContactReportType === 'activity') await this.showContactActivity();
                        else if (lastContactReportType === 'inactive') await this.showInactiveCustomers();
                        else if (lastContactReportType === 'ltv') await this.showCustomerLTV();
                        else if (lastContactReportType === 'segmentation') await this.showCustomerSegmentation();
                        else if (lastContactReportType === 'health') await this.showCustomerHealth();
                    }
                }
                break;
            case 'customer-intelligence':
                await this.loadCustomerIntelligence();
                break;
            case 'payments':
                await this.loadPayments();
                break;
            case 'accounts':
                await this.loadAccounts();
                break;
            case 'reports':
                await this.loadReports();
                break;
        }
    }

    /**
     * Initialize sub-tabs
     */
    initializeSubTabs() {
        console.log('Initializing Xero sub-tabs...');

        // REMOVE INITIAL LOADING SPINNER
        const loadingSpinner = this.container.querySelector('.xero-loading-initial');
        if (loadingSpinner) {
            loadingSpinner.remove();
        }

        // CRITICAL FIX DEC 16: Inject sub-tab navigation into content area
        const contentArea = this.container.querySelector('.xero-content');
        if (!contentArea) {
            console.error('[Xero] Content area not found - cannot inject sub-tabs');
            return;
        }

        contentArea.innerHTML = `
            <div class="xero-subtabs-nav" style="display: flex; gap: 10px; padding: 15px 20px; background: #161b22; border-bottom: 1px solid #30363d;">
                <button class="module-subtab-btn active" data-subtab="dashboard">
                    <i class="fas fa-tachometer-alt"></i> Dashboard
                </button>
                <button class="module-subtab-btn" data-subtab="invoices">
                    <i class="fas fa-file-invoice"></i> Invoices
                </button>
                <button class="module-subtab-btn" data-subtab="contacts">
                    <i class="fas fa-address-book"></i> Contacts
                </button>
                <button class="module-subtab-btn" data-subtab="customer-intelligence">
                    <i class="fas fa-brain"></i> Customer Intelligence
                </button>
                <button class="module-subtab-btn" data-subtab="payments">
                    <i class="fas fa-money-bill-wave"></i> Payments
                </button>
                <button class="module-subtab-btn" data-subtab="accounts">
                    <i class="fas fa-list"></i> Accounts
                </button>
                <button class="module-subtab-btn" data-subtab="reports">
                    <i class="fas fa-chart-bar"></i> Reports
                </button>
            </div>
            <div class="xero-tab-content-area" style="padding: 20px;">
                <!-- Tab content will be injected here -->
            </div>
        `;

        // Add click handlers to sub-tab buttons
        const buttons = contentArea.querySelectorAll('.module-subtab-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.getAttribute('data-subtab');
                this.switchSubTab(tabId);
            });
        });

        this.subTabs.set('dashboard', {
            render: () => this.renderDashboard(),
            load: () => this.loadDashboard()
        });

        this.subTabs.set('invoices', {
            render: () => this.renderInvoices(),
            load: () => this.loadInvoices()
        });

        this.subTabs.set('contacts', {
            render: () => this.renderContacts(),
            load: () => this.loadContacts()
        });

        this.subTabs.set('customer-intelligence', {
            render: () => this.renderCustomerIntelligence(),
            load: () => this.loadCustomerIntelligence()
        });

        this.subTabs.set('payments', {
            render: () => this.renderPayments(),
            load: () => this.loadPayments()
        });

        this.subTabs.set('accounts', {
            render: () => this.renderAccounts(),
            load: () => this.loadAccounts()
        });

        this.subTabs.set('reports', {
            render: () => this.renderReports(),
            load: () => this.loadReports()
        });

        // Render initial tab
        const defaultTab = this.activeSubTab || 'dashboard';
        this.switchSubTab(defaultTab);
    }

    /**
     * Switch between sub-tabs
     */
    switchSubTab(tabId) {
        console.log(`\n========================================`);
        console.log(`[Xero] 🔄 SWITCHING TO TAB: ${tabId}`);
        console.log(`========================================`);

        // Update active button
        const buttons = this.container.querySelectorAll('.module-subtab-btn');
        console.log(`[Xero] Found ${buttons.length} tab buttons`);
        buttons.forEach(btn => {
            if (btn.getAttribute('data-subtab') === tabId) {
                btn.classList.add('active');
                console.log(`[Xero] ✅ Activated button: ${tabId}`);
            } else {
                btn.classList.remove('active');
            }
        });

        // Store active tab
        this.activeSubTab = tabId;
        console.log(`[Xero] Active tab set to: ${this.activeSubTab}`);

        // Get tab definition and render
        const tab = this.subTabs.get(tabId);
        if (!tab) {
            console.error(`[Xero] ❌ Unknown tab: ${tabId}`);
            console.error(`[Xero] Available tabs:`, Array.from(this.subTabs.keys()));
            return;
        }

        console.log(`[Xero] ✅ Tab definition found for: ${tabId}`);
        console.log(`[Xero] Tab has render function:`, typeof tab.render === 'function');
        console.log(`[Xero] Tab has load function:`, typeof tab.load === 'function');

        // Render tab content
        console.log(`[Xero] 📄 Calling render() for ${tabId}...`);
        tab.render();
        console.log(`[Xero] ✅ Render complete for ${tabId}`);

        // Load tab data
        console.log(`[Xero] 📊 Calling load() for ${tabId}...`);
        tab.load();
        console.log(`[Xero] ✅ Load initiated for ${tabId}`);
        console.log(`========================================\n`);
    }

    // ========================================================================
    // DASHBOARD TAB
    // ========================================================================

    renderDashboard() {
        console.log('[Xero] 📄 renderDashboard() STARTED');
        if (!this.container) {
            console.error('[Xero] ❌ Container not set, cannot render dashboard');
            return;
        }
        console.log('[Xero] ✅ Container found:', this.container.id);

        const contentArea = this.container.querySelector('.xero-tab-content-area');
        if (!contentArea) {
            console.error('[Xero] ❌ Content area (.xero-tab-content-area) not found');
            console.log('[Xero] Container HTML:', this.container.innerHTML.substring(0, 200));
            return;
        }
        console.log('[Xero] ✅ Content area found');

        contentArea.innerHTML = `
            <div class="xero-dashboard">
                <div class="xero-stats-grid">
                    <div class="xero-stat-card" id="xero-stat-revenue">
                        <div class="xero-stat-icon" style="background: #10b981;">
                            <i class="fas fa-dollar-sign"></i>
                        </div>
                        <div class="xero-stat-content">
                            <div class="xero-stat-label">Total Revenue</div>
                            <div class="xero-stat-value">$0.00</div>
                            <div class="xero-stat-change">Loading...</div>
                        </div>
                    </div>

                    <div class="xero-stat-card" id="xero-stat-outstanding">
                        <div class="xero-stat-icon" style="background: #f59e0b;">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="xero-stat-content">
                            <div class="xero-stat-label">Outstanding</div>
                            <div class="xero-stat-value">$0.00</div>
                            <div class="xero-stat-change">Loading...</div>
                        </div>
                    </div>

                    <div class="xero-stat-card" id="xero-stat-overdue">
                        <div class="xero-stat-icon" style="background: #ef4444;">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <div class="xero-stat-content">
                            <div class="xero-stat-label">Overdue</div>
                            <div class="xero-stat-value">$0.00</div>
                            <div class="xero-stat-change">Loading...</div>
                        </div>
                    </div>

                    <div class="xero-stat-card" id="xero-stat-invoices">
                        <div class="xero-stat-icon" style="background: #3b82f6;">
                            <i class="fas fa-file-invoice"></i>
                        </div>
                        <div class="xero-stat-content">
                            <div class="xero-stat-label">Total Invoices</div>
                            <div class="xero-stat-value">0</div>
                            <div class="xero-stat-change">Loading...</div>
                        </div>
                    </div>
                </div>

                <div class="xero-charts-row">
                    <div class="xero-chart-container">
                        <h3 class="xero-chart-title">Revenue Over Time</h3>
                        <div id="xero-chart-revenue" class="xero-chart"></div>
                    </div>
                    <div class="xero-chart-container">
                        <h3 class="xero-chart-title">Invoice Status Distribution</h3>
                        <div id="xero-chart-status" class="xero-chart"></div>
                    </div>
                </div>

                <div class="xero-charts-row">
                    <div class="xero-chart-container">
                        <h3 class="xero-chart-title">Top Customers by Revenue</h3>
                        <div id="xero-chart-customers" class="xero-chart"></div>
                    </div>
                </div>

                <div class="xero-recent-section">
                    <h3 class="xero-section-title">Recent Invoices</h3>
                    <div id="xero-recent-invoices-table"></div>
                </div>
            </div>
        `;
    }

    async loadDashboard() {
        console.log('Loading Xero dashboard...');
        this.showLoading('Loading dashboard...');

        try {
            // Fetch dashboard data
            const response = await fetch(`${this.API_BASE_URL}/api/xero/dashboard?business_id=${this.currentBusiness}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to load dashboard');
            }

            this.data.stats = data;
            this.updateDashboardStats(data);
            this.createDashboardCharts(data);

            this.hideLoading();
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showError('Failed to load dashboard: ' + error.message);
        }
    }

    updateDashboardStats(data) {
        console.log('[Xero] Dashboard data received:', data);

        // Data structure: { success, business, stats: {...}, revenue_timeline, status_distribution, top_customers }
        const stats = data.stats || {};

        // If we have valid data, render the dashboard content
        if (stats.total_revenue !== undefined) {
            this.renderDashboardWithData(data);
        } else {
            console.error('[Xero] Invalid dashboard data structure:', data);
        }
    }

    renderDashboardWithData(data) {
        const contentArea = this.container.querySelector('.xero-tab-content-area');
        if (!contentArea) return;

        const stats = data.stats;

        contentArea.innerHTML = `
            <div class=\"xero-dashboard-wrapper\">
                <!-- Financial Overview Section -->
                <div class=\"xero-dashboard-section\" style=\"margin-bottom: 40px;\">
                    <h2 style=\"color: var(--text-primary); font-size: 20px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #30363d;\">
                        <i class=\"fas fa-chart-line\"></i> Financial Overview
                    </h2>
                    <div class=\"xero-metrics-grid\" style=\"display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;\">
                        <div class=\"xero-metric-card\">
                            <div class=\"metric-icon\" style=\"background: #0d419d;\"><i class=\"fas fa-dollar-sign\"></i></div>
                            <div class=\"metric-content\">
                                <div class=\"metric-label\" style=\"color: var(--text-primary);\">Total Revenue (Paid)</div>
                                <div class=\"metric-value\" style=\"color: var(--text-primary);\">${this.formatCurrency(stats.total_revenue)}</div>
                                <div class=\"metric-change\" style=\"color: var(--text-secondary);\">${stats.paid_invoices} paid invoices</div>
                            </div>
                        </div>
                        <div class=\"xero-metric-card\">
                            <div class=\"metric-icon\" style=\"background: #f7941d;\"><i class=\"fas fa-clock\"></i></div>
                            <div class=\"metric-content\">
                                <div class=\"metric-label\" style=\"color: var(--text-primary);\">Outstanding</div>
                                <div class=\"metric-value\" style=\"color: var(--text-primary);\">${this.formatCurrency(stats.outstanding_amount)}</div>
                                <div class=\"metric-change\" style=\"color: var(--text-secondary);\">${stats.outstanding_count} invoices</div>
                            </div>
                        </div>
                        <div class=\"xero-metric-card\">
                            <div class=\"metric-icon\" style=\"background: #f85149;\"><i class=\"fas fa-exclamation-triangle\"></i></div>
                            <div class=\"metric-content\">
                                <div class=\"metric-label\" style=\"color: var(--text-primary);\">Overdue</div>
                                <div class=\"metric-value\" style=\"color: var(--text-primary);\">${this.formatCurrency(stats.overdue_amount)}</div>
                                <div class=\"metric-change negative\" style=\"color: #f85149;\">${stats.overdue_count} invoices</div>
                            </div>
                        </div>
                        <div class=\"xero-metric-card\">
                            <div class=\"metric-icon\" style=\"background: #238636;\"><i class=\"fas fa-file-invoice\"></i></div>
                            <div class=\"metric-content\">
                                <div class=\"metric-label\" style=\"color: var(--text-primary);\">Total Invoices</div>
                                <div class=\"metric-value\" style=\"color: var(--text-primary);\">${stats.total_invoices}</div>
                                <div class=\"metric-change\" style=\"color: var(--text-secondary);\">${stats.paid_invoices} paid</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Revenue Trends Section -->
                <div class=\"xero-dashboard-section\" style=\"margin-bottom: 40px;\">
                    <h2 style=\"color: var(--text-primary); font-size: 20px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #30363d;\">
                        <i class=\"fas fa-chart-area\"></i> Revenue Trends
                    </h2>
                    <div class=\"xero-chart-card\">
                        <h3 style=\"color: var(--text-primary); font-size: 16px; font-weight: 500; margin-bottom: 15px;\"><i class=\"fas fa-chart-line\"></i> Revenue Trend (Last 30 Days)</h3>
                        <div id=\"xero-chart-revenue\" style=\"height: 350px;\"></div>
                    </div>
                </div>

                <!-- Invoice Analytics Section -->
                <div class=\"xero-dashboard-section\" style=\"margin-bottom: 40px;\">
                    <h2 style=\"color: var(--text-primary); font-size: 20px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #30363d;\">
                        <i class=\"fas fa-file-invoice-dollar\"></i> Invoice Analytics
                    </h2>
                    <div class=\"xero-chart-card\">
                        <h3 style=\"color: var(--text-primary); font-size: 16px; font-weight: 500; margin-bottom: 15px;\"><i class=\"fas fa-chart-pie\"></i> Invoice Status Distribution</h3>
                        <div id=\"xero-chart-status\" style=\"height: 350px;\"></div>
                    </div>
                </div>

                <!-- Customer Insights Section -->
                <div class=\"xero-dashboard-section\">
                    <h2 style=\"color: var(--text-primary); font-size: 20px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #30363d;\">
                        <i class=\"fas fa-users\"></i> Customer Insights
                    </h2>
                    <div class=\"xero-chart-card\">
                        <h3 style=\"color: var(--text-primary); font-size: 16px; font-weight: 500; margin-bottom: 15px;\"><i class=\"fas fa-trophy\"></i> Top 10 Customers by Revenue</h3>
                        <div id=\"xero-chart-customers\" style=\"height: 400px;\"></div>
                    </div>
                </div>
            </div>
        `;

        // Render charts
        this.createDashboardCharts(data);
    }

    updateStatCard(id, data) {
        const card = this.container.querySelector(`#xero-stat-${id}`);
        if (!card) return;

        const valueEl = card.querySelector('.xero-stat-value');
        const changeEl = card.querySelector('.xero-stat-change');

        if (valueEl) valueEl.textContent = data.value;
        if (changeEl) changeEl.textContent = data.change;
    }

    createDashboardCharts(data) {
        // Revenue over time chart
        if (data.revenue_timeline) {
            this.createRevenueChart(data.revenue_timeline);
        }

        // Status distribution chart
        if (data.status_distribution) {
            this.createStatusChart(data.status_distribution);
        }

        // Top customers chart
        if (data.top_customers) {
            this.createCustomersChart(data.top_customers);
        }
    }

    createRevenueChart(data) {
        const container = this.container.querySelector('#xero-chart-revenue');
        if (!container) return;

        const trace = {
            x: data.map(d => d.date),
            y: data.map(d => d.amount),
            type: 'scatter',
            mode: 'lines+markers',
            fill: 'tozeroy',
            line: { color: '#13B5EA', width: 3 },
            marker: { color: '#13B5EA', size: 8 }
        };

        const layout = {
            xaxis: {
                title: { text: 'Date', font: { color: '#ffffff' } },
                tickfont: { color: '#ffffff' },
                gridcolor: '#30363d'
            },
            yaxis: {
                title: { text: 'Revenue ($)', font: { color: '#ffffff' } },
                tickfont: { color: '#ffffff' },
                gridcolor: '#30363d'
            },
            margin: { l: 60, r: 40, t: 40, b: 60 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#ffffff' }
        };

        Plotly.newPlot(container, [trace], layout, { responsive: true });
    }

    createStatusChart(data) {
        const container = this.container.querySelector('#xero-chart-status');
        if (!container) return;

        const trace = {
            labels: data.map(d => d.status),
            values: data.map(d => d.count),
            type: 'pie',
            hole: 0.4,
            marker: {
                colors: ['#10b981', '#f59e0b', '#3b82f6', '#ef4444', '#8b5cf6']
            }
        };

        const layout = {
            margin: { l: 40, r: 40, t: 40, b: 40 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#ffffff' },
            legend: { font: { color: '#ffffff' } }
        };

        Plotly.newPlot(container, [trace], layout, { responsive: true });
    }

    createCustomersChart(data) {
        const container = this.container.querySelector('#xero-chart-customers');
        if (!container) return;

        const trace = {
            x: data.map(d => d.amount),
            y: data.map(d => d.name),
            type: 'bar',
            orientation: 'h',
            marker: { color: '#13B5EA' }
        };

        const layout = {
            xaxis: {
                title: { text: 'Revenue ($)', font: { color: '#ffffff' } },
                tickfont: { color: '#ffffff' },
                gridcolor: '#30363d'
            },
            yaxis: {
                title: '',
                tickfont: { color: '#ffffff' },
                automargin: true
            },
            margin: { l: 150, r: 40, t: 40, b: 60 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#ffffff' }
        };

        Plotly.newPlot(container, [trace], layout, { responsive: true });
    }

    // ========================================================================
    // INVOICES TAB
    // ========================================================================

    renderInvoices() {
        console.log('[Xero] 📄 renderInvoices() STARTED');
        const container = this.container.querySelector('.xero-tab-content-area');
        if (!container) {
            console.error('[Xero] ❌ Tab content area not found!');
            return;
        }
        console.log('[Xero] ✅ Container found for invoices');

        container.innerHTML = `
            <div class="xero-invoices">
                <!-- Toolbar with count and actions -->
                <div class="xero-toolbar" style="display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background: #161b22; border-radius: 6px; margin-bottom: 20px;">
                    <div class="xero-toolbar-left">
                        <span id="xero-invoice-count" style="color: #8b949e; font-size: 14px;">Loading invoices...</span>
                    </div>
                    <div class="xero-toolbar-right" style="display: flex; gap: 10px;">
                        <button class="xero-btn" id="xero-ai-export-invoices" style="padding: 8px 16px; background: #1f6feb; border: 1px solid #1f6feb; border-radius: 6px; color: white; font-weight: 500; cursor: pointer;">
                            <i class="fas fa-robot"></i> AI Export
                        </button>
                        <button class="xero-btn" id="xero-export-all-invoices" style="padding: 8px 16px; background: #238636; border: none; border-radius: 6px; color: white; font-weight: 500; cursor: pointer;">
                            <i class="fas fa-download"></i> Export CSV
                        </button>
                        <button class="xero-btn xero-btn-primary" id="xero-create-invoice" style="padding: 8px 16px; background: var(--xero-primary); border: none; border-radius: 6px; color: white; font-weight: 500; cursor: pointer;">
                            <i class="fas fa-plus"></i> Create Invoice
                        </button>
                        <button class="xero-btn" id="xero-refresh-invoices" style="padding: 8px 16px; background: #30363d; border: none; border-radius: 6px; color: white; font-weight: 500; cursor: pointer;">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                </div>

                <!-- Date Range Filter Buttons -->
                <div style="margin-bottom: 15px;">
                    <label style="color: #8b949e; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; display: block;">Date Range</label>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <button class="xero-date-filter" data-months="1" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">1 Month</button>
                        <button class="xero-date-filter" data-months="2" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">2 Months</button>
                        <button class="xero-date-filter active" data-months="3" style="padding: 6px 12px; background: var(--xero-primary); border: 1px solid var(--xero-primary); border-radius: 6px; color: white; font-size: 12px; font-weight: 500; cursor: pointer;">3 Months</button>
                        <button class="xero-date-filter" data-months="6" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">6 Months</button>
                        <button class="xero-date-filter" data-months="9" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">9 Months</button>
                        <button class="xero-date-filter" data-months="12" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">1 Year</button>
                        <button class="xero-date-filter" data-months="24" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">2 Years</button>
                        <button class="xero-date-filter" data-months="36" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">3 Years</button>
                        <button class="xero-date-filter" data-months="" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">All Time</button>
                    </div>
                </div>

                <!-- Reports Section -->
                <div class="xero-reports-section" style="margin-bottom: 15px; border: 1px solid #30363d; border-radius: 6px; overflow: hidden;">
                    <button class="xero-reports-toggle" id="xero-invoices-reports-toggle" style="width: 100%; padding: 12px 16px; background: #161b22; border: none; color: #8b949e; font-size: 13px; font-weight: 600; text-align: left; cursor: pointer; display: flex; justify-content: space-between; align-items: center;">
                        <span><i class="fas fa-chart-bar"></i> Invoice Reports</span>
                        <i class="fas fa-chevron-up"></i>
                    </button>
                    <div class="xero-reports-content" id="xero-invoices-reports-content" style="display: block; padding: 16px; background: #0d1117; border-top: 1px solid #30363d;">
                        <div style="margin-bottom: 12px;">
                            <button class="xero-btn" id="xero-show-invoice-intelligence" style="width: 100%; padding: 12px 16px; background: linear-gradient(135deg, #1f6feb 0%, #0d419d 100%); border: 1px solid #1f6feb; border-radius: 6px; color: white; font-size: 14px; font-weight: 600; cursor: pointer; box-shadow: 0 2px 8px rgba(31, 111, 235, 0.3);">
                                <i class="fas fa-chart-line"></i> Invoice Intelligence Dashboard
                            </button>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                            <button class="xero-btn xero-btn-sm" id="xero-show-aged-receivables" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-clock" style="margin-right: 6px;"></i>Aged Receivables
                            </button>
                            <button class="xero-btn xero-btn-sm" id="xero-show-sales-summary-inv" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-dollar-sign" style="margin-right: 6px;"></i>Sales Summary
                            </button>
                            <button class="xero-btn xero-btn-sm" id="xero-show-overdue-invoices" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-exclamation-triangle" style="margin-right: 6px;"></i>Overdue Invoices
                            </button>
                            <button class="xero-btn xero-btn-sm" id="xero-show-revenue-trends" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-chart-line" style="margin-right: 6px;"></i>Revenue Trends
                            </button>
                            <button class="xero-btn xero-btn-sm" id="xero-show-invoice-status" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-info-circle" style="margin-right: 6px;"></i>Status Summary
                            </button>
                            <button class="xero-btn xero-btn-sm" id="xero-show-invoice-volume" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-chart-bar" style="margin-right: 6px;"></i>Volume Analysis
                            </button>
                        </div>
                        <div id="xero-invoices-report-results" style="margin-top: 16px;"></div>
                    </div>
                </div>

                <!-- Status Filter Buttons -->
                <div style="margin-bottom: 15px;">
                    <label style="color: #8b949e; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; display: block;">Status</label>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <button class="xero-status-filter active" data-status="" style="padding: 6px 12px; background: var(--xero-primary); border: 1px solid var(--xero-primary); border-radius: 6px; color: white; font-size: 12px; font-weight: 500; cursor: pointer;">All</button>
                        <button class="xero-status-filter" data-status="DRAFT" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">Draft</button>
                        <button class="xero-status-filter" data-status="SUBMITTED" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">Submitted</button>
                        <button class="xero-status-filter" data-status="AUTHORISED" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">Authorised</button>
                        <button class="xero-status-filter" data-status="PAID" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">Paid</button>
                        <button class="xero-status-filter" data-status="VOIDED" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">Voided</button>
                    </div>
                </div>

                <!-- Search Bar -->
                <div style="margin-bottom: 20px;">
                    <input type="text" id="xero-invoice-global-search" placeholder="🔍 Search invoices by number, contact, or amount..." style="width: 100%; padding: 12px 16px; background: #161b22; border: 2px solid #30363d; border-radius: 6px; color: #ffffff; font-size: 14px;">
                </div>

                <!-- Bulk Actions Toolbar -->
                <div class="xero-bulk-actions" id="xero-invoice-bulk-actions" style="display: none; padding: 12px 20px; background: #1c2128; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="xero-selection-count" id="xero-invoice-selection-count" style="color: #ffffff; font-weight: 600;">0 selected</span>
                        <div style="display: flex; gap: 10px;">
                            <button class="xero-btn xero-btn-sm" id="xero-export-selected" style="padding: 6px 12px; background: #238636; border: none; border-radius: 4px; color: white; font-size: 12px; cursor: pointer;">
                                <i class="fas fa-download"></i> Export Selected
                            </button>
                            <button class="xero-btn xero-btn-sm xero-btn-danger" id="xero-delete-selected" style="padding: 6px 12px; background: #f85149; border: none; border-radius: 4px; color: white; font-size: 12px; cursor: pointer;">
                                <i class="fas fa-trash"></i> Delete Selected
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Tabulator Table -->
                <div id="xero-invoices-table"></div>
            </div>
        `;

        // Add event listeners
        const createBtn = container.querySelector('#xero-create-invoice');
        const refreshBtn = container.querySelector('#xero-refresh-invoices');
        const exportAllBtn = container.querySelector('#xero-export-all-invoices');
        const globalSearch = container.querySelector('#xero-invoice-global-search');
        const statusFilters = container.querySelectorAll('.xero-status-filter');
        const exportSelectedBtn = container.querySelector('#xero-export-selected');
        const deleteSelectedBtn = container.querySelector('#xero-delete-selected');

        if (createBtn) createBtn.addEventListener('click', () => this.showCreateInvoiceModal());
        if (refreshBtn) refreshBtn.addEventListener('click', () => this.loadInvoices());
        if (exportAllBtn) exportAllBtn.addEventListener('click', () => this.exportInvoices('csv'));

        // AI Export button for invoices
        const aiExportBtn = container.querySelector('#xero-ai-export-invoices');
        if (aiExportBtn) {
            aiExportBtn.addEventListener('click', (e) => {
                // Remove existing dropdown
                document.querySelectorAll('.ai-export-dropdown').forEach(d => d.remove());

                const dropdown = document.createElement('div');
                dropdown.className = 'ai-export-dropdown';
                dropdown.style.cssText = `
                    position: absolute;
                    top: ${e.target.getBoundingClientRect().bottom + 5}px;
                    right: ${window.innerWidth - e.target.getBoundingClientRect().right}px;
                    background: #161b22;
                    border: 1px solid #30363d;
                    border-radius: 6px;
                    padding: 12px;
                    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
                    z-index: 1000;
                    min-width: 320px;
                    max-width: 400px;
                `;

                dropdown.innerHTML = `
                    <div style="margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #30363d;">
                        <div style="font-weight: 600; color: #c9d1d9; margin-bottom: 8px;">Data Scope</div>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px; cursor: pointer; font-size: 13px; color: #8b949e;">
                            <input type="checkbox" id="scope-invoice-summary" checked style="cursor: pointer;">
                            Include Summary Stats
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px; cursor: pointer; font-size: 13px; color: #8b949e;">
                            <input type="checkbox" id="scope-overdue" checked style="cursor: pointer;">
                            Include Overdue Analysis
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 13px; color: #8b949e;">
                            <input type="checkbox" id="scope-full-invoices" checked style="cursor: pointer;">
                            Include Full Invoice Table (limited to 100)
                        </label>
                    </div>
                    
                    <button id="quick-prompts-invoices" style="width: 100%; padding: 10px; background: linear-gradient(135deg, #8957e5 0%, #9b6df7 100%); border: none; border-radius: 4px; color: white; font-size: 13px; font-weight: 600; cursor: pointer; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; justify-content: center;">
                        <i class="fas fa-comments"></i> Quick AI Prompts
                    </button>
                    
                    <button id="export-invoices-for-ai" style="width: 100%; padding: 10px; background: linear-gradient(135deg, #1f6feb 0%, #0d419d 100%); border: none; border-radius: 4px; color: white; font-size: 13px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; justify-content: center;">
                        <i class="fas fa-file-export"></i> Export for AI Analysis
                    </button>
                `;

                document.body.appendChild(dropdown);

                // Quick Prompts for Invoices
                document.getElementById('quick-prompts-invoices')?.addEventListener('click', () => {
                    const overdueInvoices = this.data.invoices.filter(inv => {
                        const dueDate = this.parseXeroDate(inv.due_date);
                        return dueDate && dueDate < new Date() && inv.status !== 'PAID';
                    });

                    const totalOutstanding = this.data.invoices
                        .filter(inv => inv.status !== 'PAID')
                        .reduce((sum, inv) => sum + (inv.amount_due || 0), 0);

                    const prompts = [
                        `Analyze my overdue invoices and create an action plan:\n\nTotal Overdue: ${overdueInvoices.length} invoices\nTotal Outstanding: $${totalOutstanding.toFixed(2)}\n\nTop 5 Overdue:\n${overdueInvoices.slice(0, 5).map(inv => `- Invoice #${inv.invoice_number}: ${inv.contact_name}, $${inv.amount_due.toFixed(2)} (${Math.floor((new Date() - this.parseXeroDate(inv.due_date)) / (1000 * 60 * 60 * 24))} days overdue)`).join('\n')}\n\nProvide: 1) Priority follow-up list, 2) Email templates, 3) Payment plan suggestions`,

                        `Revenue forecasting based on invoice patterns:\n\nCurrent Pipeline: ${this.data.invoices.filter(inv => inv.status === 'AUTHORISED').length} authorized invoices\nAvg Invoice Value: $${(this.data.invoices.reduce((sum, inv) => sum + inv.total, 0) / this.data.invoices.length).toFixed(2)}\n\nPredict: 1) Next 30 days revenue, 2) Cash flow forecast, 3) Collection rate improvement opportunities`,

                        `Customer payment behavior analysis:\n\nTop customers by invoice volume:\n${Object.entries(this.data.invoices.reduce((acc, inv) => { acc[inv.contact_name] = (acc[inv.contact_name] || 0) + 1; return acc; }, {})).sort((a, b) => b[1] - a[1]).slice(0, 10).map(([name, count]) => '- ' + name + ': ' + count + ' invoices').join('\\n')}\n\nAnalyze: 1) Payment patterns, 2) Credit risk, 3) Terms optimization`,

                        `Invoice efficiency audit:\n\nTotal Invoices: ${this.data.invoices.length}\nDraft: ${this.data.invoices.filter(i => i.status === 'DRAFT').length}\nAuthorized: ${this.data.invoices.filter(i => i.status === 'AUTHORISED').length}\nPaid: ${this.data.invoices.filter(i => i.status === 'PAID').length}\nOverdue: ${overdueInvoices.length}\n\nSuggest: 1) Workflow improvements, 2) Automation opportunities, 3) Collection strategies`,

                        `Create AR aging report summary and action plan based on invoice due dates. Include: 1) Current/30/60/90+ day buckets, 2) High-risk accounts, 3) Recommended collection tactics`
                    ];

                    const promptsDropdown = document.createElement('div');
                    promptsDropdown.className = 'prompts-list-dropdown';
                    promptsDropdown.style.cssText = dropdown.style.cssText;
                    promptsDropdown.style.maxHeight = '400px';
                    promptsDropdown.style.overflowY = 'auto';
                    promptsDropdown.innerHTML = `
                        <div style="margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #30363d;">
                            <div style="font-weight: 600; color: #c9d1d9;">Select Prompt to Copy</div>
                        </div>
                        ${prompts.map((p, i) => `
                            <button data-prompt-index="${i}" class="prompt-option" style="width: 100%; padding: 8px; background: #21262d; border: 1px solid #30363d; border-radius: 4px; color: #c9d1d9; font-size: 12px; text-align: left; cursor: pointer; margin-bottom: 6px; transition: 0.2s;">
                                ${p.split('\n')[0].substring(0, 60)}...
                            </button>
                        `).join('')}
                    `;

                    dropdown.replaceWith(promptsDropdown);

                    promptsDropdown.querySelectorAll('.prompt-option').forEach((btn, idx) => {
                        btn.addEventListener('click', () => {
                            navigator.clipboard.writeText(prompts[idx]);
                            btn.innerHTML = '✓ Copied to clipboard!';
                            btn.style.background = '#238636';
                            setTimeout(() => promptsDropdown.remove(), 1500);
                        });
                        btn.addEventListener('mouseenter', () => btn.style.borderColor = '#8957e5');
                        btn.addEventListener('mouseleave', () => btn.style.borderColor = '#30363d');
                    });
                });

                // Export for AI
                document.getElementById('export-invoices-for-ai')?.addEventListener('click', () => {
                    const includeSummary = document.getElementById('scope-invoice-summary')?.checked;
                    const includeOverdue = document.getElementById('scope-overdue')?.checked;
                    const includeFullTable = document.getElementById('scope-full-invoices')?.checked;

                    // Calculate summary stats
                    const stats = {
                        total_invoices: this.data.invoices.length,
                        total_revenue: this.data.invoices.reduce((sum, inv) => sum + inv.total, 0),
                        total_outstanding: this.data.invoices.filter(i => i.status !== 'PAID').reduce((sum, inv) => sum + (inv.amount_due || 0), 0),
                        overdue_count: this.data.invoices.filter(inv => {
                            const dueDate = this.parseXeroDate(inv.due_date);
                            return dueDate && dueDate < new Date() && inv.status !== 'PAID';
                        }).length,
                        status_breakdown: this.data.invoices.reduce((acc, inv) => {
                            acc[inv.status] = (acc[inv.status] || 0) + 1;
                            return acc;
                        }, {})
                    };

                    const exportData = {
                        summary: includeSummary ? stats : null,
                        overdue_analysis: includeOverdue ? this.data.invoices.filter(inv => {
                            const dueDate = this.parseXeroDate(inv.due_date);
                            return dueDate && dueDate < new Date() && inv.status !== 'PAID';
                        }).slice(0, 50) : null,
                        invoices: includeFullTable ? this.data.invoices.slice(0, 100) : this.data.invoices.slice(0, 25)
                    };

                    const formattedText = this.formatDataForAI(
                        exportData,
                        'Invoice Management Dashboard',
                        `${this.API_BASE_URL}/api/xero/invoices?business_id=${this.currentBusiness}`
                    );

                    navigator.clipboard.writeText(formattedText).then(() => {
                        dropdown.innerHTML = `
                            <div style="padding: 20px; text-align: center;">
                                <i class="fas fa-check-circle" style="font-size: 48px; color: #238636; margin-bottom: 12px;"></i>
                                <div style="font-weight: 600; color: #c9d1d9; margin-bottom: 8px;">Copied to Clipboard!</div>
                                <div style="font-size: 13px; color: #8b949e;">Paste into ChatGPT, Claude, or any AI assistant</div>
                            </div>
                        `;
                        setTimeout(() => dropdown.remove(), 2000);
                    }).catch(err => {
                        alert('Failed to copy: ' + err.message);
                    });
                });

                // Close dropdown on outside click
                setTimeout(() => {
                    document.addEventListener('click', function closeDropdown(e) {
                        if (!dropdown.contains(e.target) && e.target !== aiExportBtn) {
                            dropdown.remove();
                            document.removeEventListener('click', closeDropdown);
                        }
                    });
                }, 100);
            });
        }

        // Reports toggle
        const reportsToggle = container.querySelector('#xero-invoices-reports-toggle');
        const reportsContent = container.querySelector('#xero-invoices-reports-content');
        if (reportsToggle && reportsContent) {
            reportsToggle.addEventListener('click', () => {
                const isHidden = reportsContent.style.display === 'none';
                reportsContent.style.display = isHidden ? 'block' : 'none';
                const icon = reportsToggle.querySelector('i.fa-chevron-down');
                if (icon) {
                    icon.className = isHidden ? 'fas fa-chevron-up' : 'fas fa-chevron-down';
                }
            });
        }

        // Report buttons
        const invoiceIntelligenceBtn = container.querySelector('#xero-show-invoice-intelligence');
        const agedReceivablesBtn = container.querySelector('#xero-show-aged-receivables');
        const salesSummaryBtn = container.querySelector('#xero-show-sales-summary-inv');
        const overdueInvoicesBtn = container.querySelector('#xero-show-overdue-invoices');
        const revenueTrendsBtn = container.querySelector('#xero-show-revenue-trends');
        const invoiceStatusBtn = container.querySelector('#xero-show-invoice-status');
        const invoiceVolumeBtn = container.querySelector('#xero-show-invoice-volume');

        if (invoiceIntelligenceBtn) invoiceIntelligenceBtn.addEventListener('click', () => this.showInvoiceIntelligence());
        if (agedReceivablesBtn) agedReceivablesBtn.addEventListener('click', () => this.showAgedReceivables());
        if (salesSummaryBtn) salesSummaryBtn.addEventListener('click', () => this.showSalesSummary());
        if (overdueInvoicesBtn) overdueInvoicesBtn.addEventListener('click', () => this.showOverdueInvoices());
        if (revenueTrendsBtn) revenueTrendsBtn.addEventListener('click', () => this.showRevenueTrends());
        if (invoiceStatusBtn) invoiceStatusBtn.addEventListener('click', () => this.showInvoiceStatus());
        if (invoiceVolumeBtn) invoiceVolumeBtn.addEventListener('click', () => this.showInvoiceVolume());

        // Date range filter buttons
        const dateFilters = container.querySelectorAll('.xero-date-filter');
        dateFilters.forEach(btn => {
            btn.addEventListener('click', () => {
                // Update active state
                dateFilters.forEach(b => {
                    b.style.background = '#30363d';
                    b.style.color = '#8b949e';
                    b.style.borderColor = '#30363d';
                    b.classList.remove('active');
                });
                btn.style.background = 'var(--xero-primary)';
                btn.style.color = 'white';
                btn.style.borderColor = 'var(--xero-primary)';
                btn.classList.add('active');

                // Update date range and reload
                const months = btn.dataset.months;
                this.dateRanges.invoices = months ? parseInt(months) : null;
                this.loadInvoices();
            });
        });

        // Global search across all columns
        if (globalSearch) {
            globalSearch.addEventListener('input', (e) => {
                if (this.tables.invoices) {
                    this.tables.invoices.setFilter([
                        { field: 'invoice_number', type: 'like', value: e.target.value },
                        { field: 'contact_name', type: 'like', value: e.target.value },
                        { field: 'total', type: 'like', value: e.target.value }
                    ]);
                }
            });
        }

        // Status filter buttons
        statusFilters.forEach(btn => {
            btn.addEventListener('click', () => {
                // Update active state
                statusFilters.forEach(b => {
                    b.style.background = '#30363d';
                    b.style.color = '#8b949e';
                    b.classList.remove('active');
                });
                btn.style.background = 'var(--xero-primary)';
                btn.style.color = 'white';
                btn.classList.add('active');

                // Apply filter
                const status = btn.dataset.status;
                if (this.tables.invoices) {
                    if (status) {
                        this.tables.invoices.setFilter('status', '=', status);
                    } else {
                        this.tables.invoices.clearFilter();
                    }
                }
            });
        });

        // Bulk actions
        if (exportSelectedBtn) {
            exportSelectedBtn.addEventListener('click', () => {
                if (this.tables.invoices) {
                    this.tables.invoices.download('xlsx', 'xero_invoices_selected.xlsx', {}, 'selected');
                }
            });
        }

        if (deleteSelectedBtn) {
            deleteSelectedBtn.addEventListener('click', () => this.deleteSelectedInvoices());
        }
    }

    async loadInvoices() {
        console.log('[Xero] 📊 loadInvoices() STARTED');
        console.log('[Xero] Current business ID:', this.currentBusiness);

        // Update count to show loading state
        const countEl = this.container.querySelector('#xero-invoice-count');
        if (countEl) {
            countEl.textContent = 'Loading invoices...';
            console.log('[Xero] ✅ Updated loading text in count element');
        } else {
            console.warn('[Xero] ⚠️ Invoice count element not found');
        }

        try {
            // Build URL with date filter
            let url = `${this.API_BASE_URL}/api/xero/invoices?business_id=${this.currentBusiness}`;
            const fromDate = this.getDateRangeStart(this.dateRanges.invoices);
            if (fromDate) {
                url += `&from_date=${fromDate}`;
            }
            console.log('[Xero] 🌐 Fetching invoices from:', url, `(${this.dateRanges.invoices || 'all'} months)`);

            const response = await fetch(url);
            console.log('[Xero] Response status:', response.status, response.statusText);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('[Xero] Response data:', {
                success: data.success,
                invoiceCount: data.invoices?.length || 0,
                hasError: !!data.error
            });

            if (!data.success) {
                throw new Error(data.error || 'Failed to load invoices');
            }

            // Transform invoice data - convert date strings to Date objects for proper sorting
            this.data.invoices = (data.invoices || []).map(inv => {
                return {
                    ...inv,
                    date: inv.date ? new Date(inv.date) : null,
                    due_date: inv.due_date ? new Date(inv.due_date) : null
                };
            });
            console.log(`[Xero] ✅ Loaded ${this.data.invoices.length} invoices into memory (dates converted)`);

            // Create the table
            console.log('[Xero] 📊 Creating invoices table...');
            this.createInvoicesTable();
            console.log('[Xero] ✅ Invoices table created');
        } catch (error) {
            console.error('[Xero] ❌ Error loading invoices:', error);
            console.error('[Xero] Error stack:', error.stack);
            if (countEl) {
                countEl.textContent = 'Error loading invoices';
                countEl.style.color = '#f85149';
            }
        }
    }

    createInvoicesTable() {
        const container = this.container.querySelector('#xero-invoices-table');
        if (!container) return;

        // Update count
        const countEl = this.container.querySelector('#xero-invoice-count');
        if (countEl) {
            countEl.textContent = `Showing ${this.data.invoices.length} invoices`;
        }

        this.tables.invoices = new Tabulator(container, {
            data: this.data.invoices,
            layout: 'fitData',
            autoColumns: false,
            responsiveLayout: 'collapse',
            pagination: 'local',
            paginationSize: 25,
            paginationSizeSelector: [10, 25, 50, 100, 200],
            paginationCounter: 'rows',
            height: '600px',
            resizableRows: true,
            movableColumns: true,
            resizableColumns: true,
            selectable: true,
            selectableRangeMode: 'click',
            placeholder: 'No invoices found',
            columns: [
                {
                    formatter: 'rowSelection',
                    titleFormatter: 'rowSelection',
                    hozAlign: 'center',
                    headerSort: false,
                    width: 40,
                    minWidth: 40,
                    maxWidth: 40,
                    widthGrow: 0,
                    cellClick: function (e, cell) {
                        cell.getRow().toggleSelect();
                    }
                },
                {
                    title: 'Invoice #',
                    field: 'invoice_number',
                    minWidth: 100,
                    maxWidth: 150,
                    widthGrow: 1,
                    widthShrink: 1,
                    headerSort: true,
                    headerFilter: 'input',
                    headerFilterPlaceholder: 'Search...',
                    formatter: (cell) => {
                        const value = cell.getValue();
                        return `<span style="font-weight: 600; color: #ffffff;">#${value}</span>`;
                    }
                },
                {
                    title: 'Contact',
                    field: 'contact_name',
                    minWidth: 120,
                    maxWidth: 300,
                    widthGrow: 2,
                    widthShrink: 1,
                    headerSort: true,
                    headerFilter: 'input',
                    headerFilterPlaceholder: 'Search...',
                    formatter: (cell) => `<span style="color: #ffffff;">${cell.getValue()}</span>`
                },
                {
                    title: 'Date',
                    field: 'date',
                    minWidth: 90,
                    maxWidth: 130,
                    widthGrow: 1,
                    widthShrink: 1,
                    headerSort: true,
                    sorter: 'date',
                    sorterParams: {
                        format: 'iso',
                        alignEmptyValues: 'bottom'
                    },
                    headerFilter: 'input',
                    headerFilterPlaceholder: 'Search...',
                    formatter: (cell) => {
                        const val = cell.getValue();
                        if (!val) return '<span style="color: #8b949e;">N/A</span>';
                        const dateObj = val instanceof Date ? val : this.parseXeroDate(val);
                        return `<span style="color: #ffffff;">${this.formatDate(dateObj)}</span>`;
                    }
                },
                {
                    title: 'Due Date',
                    field: 'due_date',
                    minWidth: 90,
                    maxWidth: 130,
                    widthGrow: 1,
                    widthShrink: 1,
                    headerSort: true,
                    sorter: 'date',
                    sorterParams: {
                        format: 'iso',
                        alignEmptyValues: 'bottom'
                    },
                    headerFilter: 'input',
                    headerFilterPlaceholder: 'Search...',
                    formatter: (cell) => {
                        const val = cell.getValue();
                        if (!val) return '<span style="color: #8b949e;">N/A</span>';
                        const dateObj = val instanceof Date ? val : this.parseXeroDate(val);
                        return `<span style="color: #ffffff;">${this.formatDate(dateObj)}</span>`;
                    }
                },
                {
                    title: 'Total',
                    field: 'total',
                    minWidth: 90,
                    maxWidth: 150,
                    widthGrow: 1,
                    widthShrink: 1,
                    headerSort: true,
                    sorter: 'number',
                    hozAlign: 'right',
                    headerFilter: 'input',
                    headerFilterPlaceholder: 'Search...',
                    formatter: (cell) => `<span style="font-weight: 600; color: #ffffff;">${this.formatCurrency(cell.getValue())}</span>`
                },
                {
                    title: 'Amount Due',
                    field: 'amount_due',
                    minWidth: 110,
                    maxWidth: 150,
                    widthGrow: 1,
                    widthShrink: 1,
                    headerSort: true,
                    sorter: 'number',
                    hozAlign: 'right',
                    headerFilter: 'input',
                    headerFilterPlaceholder: 'Search...',
                    formatter: (cell) => `<span style="font-weight: 600; color: #ffffff;">${this.formatCurrency(cell.getValue())}</span>`
                },
                {
                    title: 'Status',
                    field: 'status',
                    minWidth: 90,
                    maxWidth: 130,
                    widthGrow: 1,
                    widthShrink: 1,
                    headerSort: true,
                    headerFilter: 'input',
                    headerFilterPlaceholder: 'Search...',
                    formatter: (cell) => {
                        const status = cell.getValue();
                        const badge = this.getStatusBadge(status);
                        return badge;
                    }
                },
                {
                    title: 'Actions',
                    width: 100,
                    hozAlign: 'center',
                    formatter: () => `
                        <button class="xero-action-btn" style="padding: 6px 12px; background: #1f6feb; border: 1px solid #1f6feb; border-radius: 4px; color: white; cursor: pointer; font-size: 11px;">
                            <i class="fas fa-eye"></i> View
                        </button>
                    `,
                    cellClick: (e, cell) => {
                        this.showDetailsModal('invoice', cell.getRow().getData());
                    }
                }
            ]
        });

        // Dynamic height adjustment when page size changes
        this.tables.invoices.on('pageSizeChanged', (size) => {
            if (size >= 50) {
                this.tables.invoices.setHeight('800px');
            } else {
                this.tables.invoices.setHeight('600px');
            }
        });

        // Handle row selection
        this.tables.invoices.on('rowSelectionChanged', (data, rows) => {
            this.selectedItems.invoices = new Set(rows.map(r => r.getData().invoice_id));

            // Update selection count
            const countEl = this.container.querySelector('#xero-invoice-selection-count');
            const bulkActions = this.container.querySelector('#xero-invoice-bulk-actions');

            if (countEl) {
                countEl.textContent = `${rows.length} selected`;
            }

            // Show/hide bulk actions toolbar
            if (bulkActions) {
                bulkActions.style.display = rows.length > 0 ? 'block' : 'none';
            }
        });
    }

    // ========================================================================
    // CONTACTS TAB
    // ========================================================================

    renderContacts() {
        console.log('[Xero] 📄 renderContacts() STARTED');
        const container = this.container.querySelector('.xero-tab-content-area');
        if (!container) {
            console.error('[Xero] ❌ Tab content area not found for contacts!');
            return;
        }
        console.log('[Xero] ✅ Container found for contacts');

        container.innerHTML = `
            <div class="xero-contacts">
                <div class="xero-toolbar" style="display: flex; justify-content: space-between; align-items: center; padding: 16px; background: #0d1117; border-bottom: 1px solid #30363d; margin-bottom: 16px;">
                    <div class="xero-toolbar-left" style="display: flex; gap: 8px;">
                        <button class="xero-btn xero-btn-primary" id="xero-create-contact" style="padding: 10px 16px; background: var(--xero-primary); color: white; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: all 0.2s;">
                            <i class="fas fa-plus"></i> Create Contact
                        </button>
                        <button class="xero-btn" id="xero-refresh-contacts" style="padding: 10px 16px; background: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; font-size: 14px; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: all 0.2s;">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                    <div class="xero-toolbar-right">
                        <input type="text" class="xero-search" id="xero-contact-search" 
                               placeholder="Search contacts..." style="padding: 10px 14px; background: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; font-size: 14px; width: 300px;">
                    </div>
                </div>

                <!-- Date Range Filter Buttons -->
                <div style="margin-bottom: 15px;">
                    <label style="color: #8b949e; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; display: block;">Date Range</label>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <button class="xero-date-filter" data-months="1" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">1 Month</button>
                        <button class="xero-date-filter" data-months="2" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">2 Months</button>
                        <button class="xero-date-filter active" data-months="3" style="padding: 6px 12px; background: var(--xero-primary); border: 1px solid var(--xero-primary); border-radius: 6px; color: white; font-size: 12px; font-weight: 500; cursor: pointer;">3 Months</button>
                        <button class="xero-date-filter" data-months="6" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">6 Months</button>
                        <button class="xero-date-filter" data-months="9" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">9 Months</button>
                        <button class="xero-date-filter" data-months="12" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">1 Year</button>
                        <button class="xero-date-filter" data-months="24" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">2 Years</button>
                        <button class="xero-date-filter" data-months="36" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">3 Years</button>
                        <button class="xero-date-filter" data-months="" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">All Time</button>
                    </div>
                </div>

                <!-- Reports Section -->
                <div class="xero-reports-section" style="margin-bottom: 15px; border: 1px solid #30363d; border-radius: 6px; overflow: hidden;">
                    <button class="xero-reports-toggle" id="xero-contacts-reports-toggle" style="width: 100%; padding: 12px 16px; background: #161b22; border: none; color: #8b949e; font-size: 13px; font-weight: 600; text-align: left; cursor: pointer; display: flex; justify-content: space-between; align-items: center;">
                        <span><i class="fas fa-chart-bar"></i> Contact Reports</span>
                        <i class="fas fa-chevron-up"></i>
                    </button>
                    <div class="xero-reports-content" id="xero-contacts-reports-content" style="display: block; padding: 16px; background: #0d1117; border-top: 1px solid #30363d;">
                        <!-- Unified Customer Intelligence Dashboard Button -->
                        <button class="xero-btn" id="xero-show-customer-intelligence" style="width: 100%; padding: 20px; background: linear-gradient(135deg, #1f6feb 0%, #1a56db 100%); border: 1px solid #388bfd; border-radius: 8px; color: white; font-size: 14px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 16px; box-shadow: 0 4px 12px rgba(31, 111, 235, 0.2);">
                            <i class="fas fa-brain" style="font-size: 32px; color: #fff;"></i>
                            <div style="flex: 1;">
                                <div style="font-size: 16px; font-weight: 700; margin-bottom: 4px;">🎯 Customer Intelligence Dashboard</div>
                                <div style="font-size: 12px; color: rgba(255,255,255,0.9); line-height: 1.4;">
                                    Unified view: Risk scores, RFM segments, churn prediction, LTV, payment behavior, and actionable recommendations
                                </div>
                            </div>
                            <i class="fas fa-arrow-right" style="font-size: 20px; color: rgba(255,255,255,0.8);"></i>
                        </button>
                        <div id="xero-contacts-report-results" style="margin-top: 16px;"></div>
                    </div>
                </div>

                <!-- Bulk Actions Toolbar -->
                <div class="xero-bulk-actions" id="xero-contacts-bulk-actions" style="display: none;">
                    <div class="xero-bulk-left">
                        <span class="xero-selection-count" id="xero-contacts-selection-count">0 selected</span>
                    </div>
                    <div class="xero-bulk-right">
                        <div class="xero-btn-group">
                            <button class="xero-btn xero-btn-sm" id="xero-export-contacts-dropdown">
                                <i class="fas fa-download"></i> Export
                                <i class="fas fa-chevron-down"></i>
                            </button>
                            <div class="xero-dropdown-menu" id="xero-export-contacts-menu" style="display: none;">
                                <a href="#" data-format="xlsx">Export to Excel</a>
                                <a href="#" data-format="csv">Export to CSV</a>
                                <a href="#" data-format="pdf">Export to PDF</a>
                            </div>
                        </div>
                        <button class="xero-btn xero-btn-sm xero-btn-danger" id="xero-delete-contacts">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
                <div id="xero-contacts-table"></div>
            </div>
        `;

        // Add event listeners
        const createBtn = container.querySelector('#xero-create-contact');
        const refreshBtn = container.querySelector('#xero-refresh-contacts');
        const searchInput = container.querySelector('#xero-contact-search');

        if (createBtn) createBtn.addEventListener('click', () => this.showCreateContactModal());
        if (refreshBtn) refreshBtn.addEventListener('click', () => this.loadContacts());
        if (searchInput) searchInput.addEventListener('input', (e) => this.filterContacts(e.target.value));

        // Date range filter buttons
        const dateFilters = container.querySelectorAll('.xero-date-filter');
        dateFilters.forEach(btn => {
            btn.addEventListener('click', () => {
                dateFilters.forEach(b => {
                    b.style.background = '#30363d';
                    b.style.color = '#8b949e';
                    b.style.borderColor = '#30363d';
                    b.classList.remove('active');
                });
                btn.style.background = 'var(--xero-primary)';
                btn.style.color = 'white';
                btn.style.borderColor = 'var(--xero-primary)';
                btn.classList.add('active');

                const months = btn.dataset.months;
                this.dateRanges.contacts = months ? parseInt(months) : null;
                this.loadContacts();
            });
        });

        // Bulk actions for contacts
        const exportBtn = container.querySelector('#xero-export-contacts-dropdown');
        const exportMenu = container.querySelector('#xero-export-contacts-menu');
        const deleteBtn = container.querySelector('#xero-delete-contacts');

        if (exportBtn && exportMenu) {
            exportBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                exportMenu.style.display = exportMenu.style.display === 'none' ? 'block' : 'none';
            });

            exportMenu.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const format = e.target.dataset.format;
                    this.exportContacts(format);
                    exportMenu.style.display = 'none';
                });
            });

            document.addEventListener('click', () => {
                exportMenu.style.display = 'none';
            });
        }

        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => this.deleteSelectedContacts());
        }

        // Contacts reports toggle
        const contactsReportsToggle = container.querySelector('#xero-contacts-reports-toggle');
        const contactsReportsContent = container.querySelector('#xero-contacts-reports-content');
        if (contactsReportsToggle && contactsReportsContent) {
            contactsReportsToggle.addEventListener('click', () => {
                const isHidden = contactsReportsContent.style.display === 'none';
                contactsReportsContent.style.display = isHidden ? 'block' : 'none';
                const icon = contactsReportsToggle.querySelector('i.fa-chevron-down');
                if (icon) {
                    icon.className = isHidden ? 'fas fa-chevron-up' : 'fas fa-chevron-down';
                }
            });
        }

        // Contacts report buttons
        const customerIntelligenceBtn = container.querySelector('#xero-show-customer-intelligence');

        if (customerIntelligenceBtn) customerIntelligenceBtn.addEventListener('click', async () => {
            customerIntelligenceBtn.disabled = true;
            const originalHTML = customerIntelligenceBtn.innerHTML;
            customerIntelligenceBtn.innerHTML = '<i class="fas fa-spinner fa-spin" style="font-size: 32px;"></i><div style="flex: 1;"><div style="font-size: 16px; font-weight: 700;">Loading Customer Intelligence...</div></div>';
            try {
                await this.showCustomerIntelligence();
            } finally {
                customerIntelligenceBtn.disabled = false;
                customerIntelligenceBtn.innerHTML = originalHTML;
            }
        });
    }

    async loadContacts() {
        console.log('[Xero] 📊 loadContacts() STARTED');
        console.log('[Xero] Current business ID:', this.currentBusiness);

        try {
            let url = `${this.API_BASE_URL}/api/xero/contacts?business_id=${this.currentBusiness}`;

            // Add date range filter if set
            const fromDate = this.getDateRangeStart(this.dateRanges.contacts);
            if (fromDate) {
                url += `&from_date=${fromDate}`;
            }

            console.log('[Xero] 🌐 Fetching contacts from:', url);

            const response = await fetch(url);
            console.log('[Xero] Response status:', response.status, response.statusText);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('[Xero] Response data:', {
                success: data.success,
                contactCount: data.contacts?.length || 0,
                hasError: !!data.error
            });

            if (!data.success) {
                throw new Error(data.error || 'Failed to load contacts');
            }

            this.data.contacts = data.contacts || [];
            console.log(`[Xero] ✅ Loaded ${this.data.contacts.length} contacts into memory`);

            console.log('[Xero] 📊 Creating contacts table...');
            this.createContactsTable();
            console.log('[Xero] ✅ Contacts table created');
        } catch (error) {
            console.error('[Xero] ❌ Error loading contacts:', error);
            console.error('[Xero] Error stack:', error.stack);
        }
    }

    createContactsTable() {
        const container = this.container.querySelector('#xero-contacts-table');
        if (!container) return;

        this.tables.contacts = new Tabulator(container, {
            data: this.data.contacts,
            layout: 'fitData',
            autoColumns: false,
            responsiveLayout: 'collapse',
            pagination: true,
            paginationSize: 50,
            selectable: true,
            selectableRangeMode: 'click',
            columns: [
                {
                    formatter: 'rowSelection',
                    titleFormatter: 'rowSelection',
                    hozAlign: 'center',
                    headerSort: false,
                    width: 40,
                    minWidth: 40,
                    maxWidth: 40,
                    widthGrow: 0,
                    cellClick: function (e, cell) {
                        cell.getRow().toggleSelect();
                    }
                },
                { title: 'Name', field: 'name', minWidth: 120, maxWidth: 300, widthGrow: 2, widthShrink: 1 },
                { title: 'Email', field: 'email', minWidth: 150, maxWidth: 250, widthGrow: 2, widthShrink: 1 },
                { title: 'Phone', field: 'phone', minWidth: 100, maxWidth: 150, widthGrow: 1, widthShrink: 1 },
                {
                    title: 'Type',
                    field: 'is_customer',
                    minWidth: 80,
                    maxWidth: 120,
                    widthGrow: 1,
                    widthShrink: 1,
                    formatter: (cell) => {
                        const isCustomer = cell.getValue();
                        const row = cell.getRow().getData();
                        const types = [];
                        if (isCustomer) types.push('Customer');
                        if (row.is_supplier) types.push('Supplier');
                        return types.join(', ') || 'N/A';
                    }
                },
                {
                    title: 'Actions',
                    minWidth: 90,
                    maxWidth: 100,
                    widthGrow: 0,
                    widthShrink: 0,
                    hozAlign: 'center',
                    formatter: () => `
                        <button class="xero-action-btn" style="padding: 6px 12px; background: #1f6feb; border: 1px solid #1f6feb; border-radius: 4px; color: white; cursor: pointer; font-size: 11px;">
                            <i class="fas fa-eye"></i> View
                        </button>
                    `,
                    cellClick: (e, cell) => {
                        this.showContactDetails(cell.getRow().getData());
                    }
                }
            ]
        });

        // Handle row selection
        this.tables.contacts.on('rowSelectionChanged', (data, rows) => {
            this.selectedItems.contacts = new Set(rows.map(r => r.getData().contact_id));
            this.updateSelectionCount('contacts', rows.length);
        });
    }

    // ========================================================================
    // CUSTOMER INTELLIGENCE TAB
    // ========================================================================

    renderCustomerIntelligence() {
        console.log('[Xero] 🧠 renderCustomerIntelligence() STARTED');
        const container = this.container.querySelector('.xero-tab-content-area');
        if (!container) {
            console.error('[Xero] Content area not found');
            return;
        }

        container.innerHTML = `
            <div class="xero-customer-intelligence-container">
                <!-- Sticky Toolbar -->
                <div class="xero-intelligence-toolbar" style="
                    position: sticky;
                    top: 0;
                    z-index: 100;
                    background: #0d1117;
                    border-bottom: 1px solid #30363d;
                    padding: 16px 20px;
                    display: flex;
                    gap: 12px;
                    align-items: center;
                    flex-wrap: wrap;
                ">
                    <!-- Quick Navigation Dropdown -->
                    <select id="intelligence-quick-nav" style="
                        padding: 8px 12px;
                        background: #161b22;
                        border: 1px solid #30363d;
                        border-radius: 6px;
                        color: #c9d1d9;
                        font-size: 14px;
                        cursor: pointer;
                        min-width: 200px;
                    ">
                        <option value="">📍 Jump to Section</option>
                        <option value="customer-intelligence-dashboard">Customer Intelligence Dashboard</option>
                        <option value="ltv-forecasting">LTV Forecasting</option>
                        <option value="next-best-actions">Next Best Action Engine</option>
                        <option value="cohort-analysis">Cohort Analysis</option>
                        <option value="all-contacts">All Contacts</option>
                    </select>

                    <!-- Refresh Button -->
                    <button id="refresh-intelligence" class="xero-btn xero-btn-primary" style="
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    ">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>

                    <!-- Date Range Selector -->
                    <select id="intelligence-date-range" style="
                        padding: 8px 12px;
                        background: #161b22;
                        border: 1px solid #30363d;
                        border-radius: 6px;
                        color: #c9d1d9;
                        font-size: 14px;
                        cursor: pointer;
                    ">
                        <option value="3">Last 3 Months</option>
                        <option value="6">Last 6 Months</option>
                        <option value="12" selected>Last 12 Months</option>
                        <option value="24">Last 24 Months</option>
                        <option value="36">Last 36 Months</option>
                        <option value="">All Time</option>
                    </select>

                    <!-- Comparison Period -->
                    <select id="intelligence-comparison" style="
                        padding: 8px 12px;
                        background: #161b22;
                        border: 1px solid #30363d;
                        border-radius: 6px;
                        color: #c9d1d9;
                        font-size: 14px;
                        cursor: pointer;
                    ">
                        <option value="prior-period">vs Prior Period</option>
                        <option value="prior-year" selected>vs Prior Year</option>
                        <option value="custom">Custom Range</option>
                    </select>
                </div>

                <!-- Main Content Area (Long Scrollable) -->
                <div class="xero-intelligence-content" style="padding: 20px;">
                    
                    <!-- Section 1: Customer Intelligence Dashboard -->
                    <div id="customer-intelligence-dashboard" class="intelligence-section" style="margin-bottom: 40px;">
                        <div class="section-header" style="
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                            padding: 16px 20px;
                            background: #161b22;
                            border: 1px solid #30363d;
                            border-radius: 6px 6px 0 0;
                            cursor: pointer;
                        ">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <i class="fas fa-brain" style="font-size: 24px; color: var(--xero-primary);"></i>
                                <div>
                                    <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #c9d1d9;">Customer Intelligence Dashboard</h2>
                                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #8b949e;">ML-powered risk scores, behavioral insights, and strategic recommendations</p>
                                </div>
                            </div>
                            <i class="fas fa-chevron-down section-toggle" style="font-size: 16px; color: #8b949e; transition: transform 0.3s;"></i>
                        </div>
                        <div class="section-content" style="
                            border: 1px solid #30363d;
                            border-top: none;
                            border-radius: 0 0 6px 6px;
                            padding: 20px;
                            background: #0d1117;
                        ">
                            <div id="customer-intelligence-dashboard-content">
                                <p style="color: #8b949e; text-align: center; padding: 40px;">Loading Customer Intelligence...</p>
                            </div>
                        </div>
                    </div>

                    <!-- Section 2: LTV Forecasting -->
                    <div id="ltv-forecasting" class="intelligence-section" style="margin-bottom: 40px;">
                        <div class="section-header" style="
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                            padding: 16px 20px;
                            background: #161b22;
                            border: 1px solid #30363d;
                            border-radius: 6px 6px 0 0;
                            cursor: pointer;
                        ">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <i class="fas fa-chart-line" style="font-size: 24px; color: #58a6ff;"></i>
                                <div>
                                    <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #c9d1d9;">LTV Forecasting</h2>
                                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #8b949e;">Predictive lifetime value modeling with churn-adjusted projections</p>
                                </div>
                            </div>
                            <i class="fas fa-chevron-down section-toggle" style="font-size: 16px; color: #8b949e; transition: transform 0.3s;"></i>
                        </div>
                        <div class="section-content" style="
                            border: 1px solid #30363d;
                            border-top: none;
                            border-radius: 0 0 6px 6px;
                            padding: 20px;
                            background: #0d1117;
                        ">
                            <div id="ltv-forecasting-content">
                                <p style="color: #8b949e; text-align: center; padding: 40px;">Loading LTV forecasting data...</p>
                            </div>
                        </div>
                    </div>

                    <!-- Section 3: Next Best Action Engine -->
                    <div id="next-best-actions" class="intelligence-section" style="margin-bottom: 40px;">
                        <div class="section-header" style="
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                            padding: 16px 20px;
                            background: #161b22;
                            border: 1px solid #30363d;
                            border-radius: 6px 6px 0 0;
                            cursor: pointer;
                        ">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <i class="fas fa-bullseye" style="font-size: 24px; color: #f78166;"></i>
                                <div>
                                    <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #c9d1d9;">Next Best Action Engine</h2>
                                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #8b949e;">Prioritized action queue with optimal contact timing and expected ROI</p>
                                </div>
                            </div>
                            <i class="fas fa-chevron-down section-toggle" style="font-size: 16px; color: #8b949e; transition: transform 0.3s;"></i>
                        </div>
                        <div class="section-content" style="
                            border: 1px solid #30363d;
                            border-top: none;
                            border-radius: 0 0 6px 6px;
                            padding: 20px;
                            background: #0d1117;
                        ">
                            <div id="next-best-actions-content">
                                <p style="color: #8b949e; text-align: center; padding: 40px;">Loading action recommendations...</p>
                            </div>
                        </div>
                    </div>

                    <!-- Section 4: Cohort Analysis -->
                    <div id="cohort-analysis" class="intelligence-section" style="margin-bottom: 40px;">
                        <div class="section-header" style="
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                            padding: 16px 20px;
                            background: #161b22;
                            border: 1px solid #30363d;
                            border-radius: 6px 6px 0 0;
                            cursor: pointer;
                        ">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <i class="fas fa-users" style="font-size: 24px; color: #a371f7;"></i>
                                <div>
                                    <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #c9d1d9;">Cohort Analysis</h2>
                                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #8b949e;">Customer retention patterns by acquisition cohort</p>
                                </div>
                            </div>
                            <i class="fas fa-chevron-down section-toggle" style="font-size: 16px; color: #8b949e; transition: transform 0.3s;"></i>
                        </div>
                        <div class="section-content" style="
                            border: 1px solid #30363d;
                            border-top: none;
                            border-radius: 0 0 6px 6px;
                            padding: 20px;
                            background: #0d1117;
                        ">
                            <div id="cohort-analysis-content">
                                <p style="color: #8b949e; text-align: center; padding: 40px;">Loading cohort analysis...</p>
                            </div>
                        </div>
                    </div>

                    <!-- Section 5: All Contacts -->
                    <div id="all-contacts" class="intelligence-section" style="margin-bottom: 40px;">
                        <div class="section-header" style="
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                            padding: 16px 20px;
                            background: #161b22;
                            border: 1px solid #30363d;
                            border-radius: 6px 6px 0 0;
                            cursor: pointer;
                        ">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <i class="fas fa-address-book" style="font-size: 24px; color: #56d364;"></i>
                                <div>
                                    <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #c9d1d9;">All Contacts</h2>
                                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #8b949e;">Complete contact list with inline expandable details</p>
                                </div>
                            </div>
                            <i class="fas fa-chevron-down section-toggle" style="font-size: 16px; color: #8b949e; transition: transform 0.3s;"></i>
                        </div>
                        <div class="section-content" style="
                            border: 1px solid #30363d;
                            border-top: none;
                            border-radius: 0 0 6px 6px;
                            padding: 20px;
                            background: #0d1117;
                        ">
                            <div id="all-contacts-table"></div>
                        </div>
                    </div>

                </div>
            </div>
        `;

        // Add event listeners
        this.setupIntelligenceEventListeners();
    }

    setupIntelligenceEventListeners() {
        const container = this.container.querySelector('.xero-customer-intelligence-container');
        if (!container) return;

        // Quick Navigation Dropdown
        const quickNav = container.querySelector('#intelligence-quick-nav');
        if (quickNav) {
            quickNav.addEventListener('change', (e) => {
                const sectionId = e.target.value;
                if (sectionId) {
                    const section = document.getElementById(sectionId);
                    if (section) {
                        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        // Reset dropdown after navigation
                        setTimeout(() => { e.target.value = ''; }, 300);
                    }
                }
            });
        }

        // Refresh Button
        const refreshBtn = container.querySelector('#refresh-intelligence');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadCustomerIntelligence();
            });
        }

        // Date Range Selector
        const dateRange = container.querySelector('#intelligence-date-range');
        if (dateRange) {
            dateRange.addEventListener('change', () => {
                this.loadCustomerIntelligence();
            });
        }

        // Comparison Period
        const comparison = container.querySelector('#intelligence-comparison');
        if (comparison) {
            comparison.addEventListener('change', () => {
                this.loadCustomerIntelligence();
            });
        }

        // Section Collapse/Expand Toggles
        const sectionHeaders = container.querySelectorAll('.section-header');
        sectionHeaders.forEach(header => {
            header.addEventListener('click', () => {
                const section = header.parentElement;
                const content = section.querySelector('.section-content');
                const toggle = header.querySelector('.section-toggle');

                if (content.style.display === 'none') {
                    content.style.display = 'block';
                    toggle.style.transform = 'rotate(0deg)';
                } else {
                    content.style.display = 'none';
                    toggle.style.transform = 'rotate(-90deg)';
                }
            });
        });
    }

    async loadCustomerIntelligence() {
        console.log('[Xero] 🧠 loadCustomerIntelligence() STARTED');
        console.log('[Xero] Current business ID:', this.currentBusiness);

        try {
            // Get date range from selector
            const dateRangeSelect = this.container.querySelector('#intelligence-date-range');
            const months = dateRangeSelect ? dateRangeSelect.value : '12';

            let url = `${this.API_BASE_URL}/api/xero/reports/customer-intelligence?business_id=${this.currentBusiness}`;

            if (months) {
                const fromDate = this.getDateRangeStart(parseInt(months));
                if (fromDate) {
                    url += `&from_date=${fromDate}`;
                }
            }

            console.log('[Xero] 🌐 Fetching Customer Intelligence from:', url);

            const response = await fetch(url);
            console.log('[Xero] Response status:', response.status, response.statusText);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('[Xero] Customer Intelligence data received:', {
                success: data.success,
                customerCount: data.customers?.length || 0,
                hasError: !!data.error
            });

            if (!data.success) {
                throw new Error(data.error || 'Failed to load customer intelligence');
            }

            // Render Customer Intelligence Dashboard (Section 1)
            this.renderCustomerIntelligenceDashboard(data);

            // Render LTV Forecasting (Section 2)
            this.renderLTVForecasting(data);

            // Render Next Best Actions (Section 3)
            this.renderNextBestActions(data);

            // Render Cohort Analysis (Section 4)
            this.renderCohortAnalysis(data);

            // Load contacts for Section 5 (All Contacts)
            await this.loadAllContactsForIntelligence();

        } catch (error) {
            console.error('[Xero] ❌ Error loading customer intelligence:', error);
            const contentDiv = this.container.querySelector('#customer-intelligence-dashboard-content');
            if (contentDiv) {
                contentDiv.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: #f85149;">
                        <i class="fas fa-exclamation-triangle" style="font-size: 48px; margin-bottom: 16px;"></i>
                        <p style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">Error Loading Customer Intelligence</p>
                        <p style="font-size: 13px; color: #8b949e;">${error.message}</p>
                    </div>
                `;
            }
        }
    }

    renderCustomerIntelligenceDashboard(data) {
        const contentDiv = this.container.querySelector('#customer-intelligence-dashboard-content');
        if (!contentDiv) return;

        // For now, create a simple table view of the customer intelligence data
        // This reuses the existing ML pipeline structure
        contentDiv.innerHTML = `
            <div id="customer-intelligence-table-container"></div>
        `;

        const tableContainer = contentDiv.querySelector('#customer-intelligence-table-container');
        if (tableContainer && data.customers) {
            new Tabulator(tableContainer, {
                data: data.customers,
                layout: 'fitDataFill',
                pagination: true,
                paginationSize: 50,
                columns: [
                    { title: 'Customer', field: 'contact_name', minWidth: 150, frozen: true },
                    {
                        title: 'Last Activity', field: 'last_order_date', minWidth: 110,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            if (!val) return '<span style="color: #f85149;">Never</span>';
                            const date = new Date(val);
                            const now = new Date();
                            const daysAgo = Math.floor((now - date) / (1000 * 60 * 60 * 24));

                            if (daysAgo > 180) {
                                return `<span style="color: #f85149; font-size: 11px;">${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}<br>${daysAgo}d ago</span>`;
                            } else if (daysAgo > 90) {
                                return `<span style="color: #d29922; font-size: 11px;">${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}<br>${daysAgo}d ago</span>`;
                            } else {
                                return `<span style="color: #3fb950; font-size: 11px;">${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}<br>${daysAgo}d ago</span>`;
                            }
                        }
                    },
                    {
                        title: 'Segment', field: 'rfm_segment', minWidth: 120,
                        formatter: (cell) => {
                            const segment = cell.getValue();
                            const colors = {
                                'VIP-Protect': '#56d364',
                                'VIP At-Risk': '#f85149',
                                'High-Value Declining': '#f0883e',
                                'Rising Star': '#58a6ff',
                                'Lost Cause': '#8b949e',
                                'Stable Regular': '#a371f7',
                                'Standard': '#c9d1d9'
                            };
                            const color = colors[segment] || '#8b949e';
                            return `<span style="color: ${color}; font-weight: 600;">${segment}</span>`;
                        }
                    },
                    {
                        title: 'Churn Risk', field: 'ml_churn_probability', minWidth: 100,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            if (!val) return '-';
                            const color = val > 70 ? '#f85149' : val > 40 ? '#f0883e' : '#56d364';
                            return `<span style="color: ${color}; font-weight: 600;">${val.toFixed(1)}%</span>`;
                        }
                    },
                    {
                        title: 'Payment Risk', field: 'payment_risk_score', minWidth: 100,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            if (!val) return '-';
                            const color = val > 70 ? '#f85149' : val > 40 ? '#f0883e' : '#56d364';
                            return `<span style="color: ${color}; font-weight: 600;">${val.toFixed(1)}%</span>`;
                        }
                    },
                    {
                        title: 'LTV', field: 'lifetime_revenue', minWidth: 100,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            return val ? `$${val.toLocaleString()}` : '-';
                        }
                    },
                    {
                        title: 'Avg Invoice', field: 'avg_invoice_value', minWidth: 120,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            return val ? `$${val.toLocaleString()}` : '-';
                        }
                    },
                    { title: 'Best Action', field: 'recommended_action', minWidth: 150 },
                    {
                        title: 'Behavior Trend', field: 'behavior_trend', minWidth: 120,
                        formatter: (cell) => {
                            const trend = cell.getValue();
                            const icons = {
                                'Improving': '📈',
                                'Declining': '📉',
                                'Stable': '➡️'
                            };
                            return `${icons[trend] || ''} ${trend}`;
                        }
                    },
                    {
                        title: 'Actions',
                        width: 100,
                        hozAlign: 'center',
                        headerSort: false,
                        formatter: () => `
                            <button class="xero-action-btn" style="padding: 6px 12px; background: #1f6feb; border: 1px solid #1f6feb; border-radius: 4px; color: white; cursor: pointer; font-size: 11px;">
                                <i class="fas fa-eye"></i> View
                            </button>
                        `,
                        cellClick: (e, cell) => {
                            const customerData = cell.getRow().getData();
                            this.showDetailsModal('contact', customerData);
                        }
                    }
                ]
            });
        }
    }

    renderLTVForecasting(data) {
        const contentDiv = this.container.querySelector('#ltv-forecasting-content');
        if (!contentDiv || !data.customers) return;

        // Calculate LTV metrics from customer data - use lifetime_revenue as historical LTV
        const customers = data.customers.filter(c => c.lifetime_revenue > 0);
        const totalLTV = customers.reduce((sum, c) => sum + (c.lifetime_revenue || 0), 0);
        const avgLTV = customers.length > 0 ? totalLTV / customers.length : 0;

        // Predict 12-month LTV based on order frequency and average value
        const customersWithPredictions = customers.map(c => {
            const monthlyOrders = c.order_frequency || 0;
            const avgOrderValue = c.avg_invoice_value || 0;
            const predicted12m = monthlyOrders * 12 * avgOrderValue * (1 - c.ml_churn_probability / 100);
            return { ...c, predicted_12m_ltv: predicted12m };
        });

        const totalPredicted = customersWithPredictions.reduce((sum, c) => sum + (c.predicted_12m_ltv || 0), 0);
        const avgPredicted = customers.length > 0 ? totalPredicted / customers.length : 0;

        // Top 10 customers by predicted LTV
        const topCustomers = [...customersWithPredictions]
            .sort((a, b) => (b.predicted_12m_ltv || 0) - (a.predicted_12m_ltv || 0))
            .slice(0, 10);

        contentDiv.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
                <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; border-left: 3px solid #58a6ff;">
                    <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Total Historical LTV</div>
                    <div style="font-size: 28px; color: #58a6ff; font-weight: 700;">$${totalLTV.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
                    <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">From ${customers.length} customers</div>
                </div>
                <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; border-left: 3px solid #3fb950;">
                    <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Predicted 12M LTV</div>
                    <div style="font-size: 28px; color: #3fb950; font-weight: 700;">$${totalPredicted.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
                    <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Churn-adjusted forecast</div>
                </div>
                <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; border-left: 3px solid #d29922;">
                    <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Avg Customer LTV</div>
                    <div style="font-size: 28px; color: #d29922; font-weight: 700;">$${avgLTV.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
                    <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Per customer</div>
                </div>
                <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; border-left: 3px solid #a371f7;">
                    <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Avg Predicted LTV</div>
                    <div style="font-size: 28px; color: #a371f7; font-weight: 700;">$${avgPredicted.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
                </div>
            </div>

            <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px;">
                <h4 style="margin: 0 0 16px 0; color: #c9d1d9; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-trophy" style="color: #f78166;"></i>
                    Top 10 Customers by Predicted LTV
                </h4>
                <div id="ltv-top-customers-table"></div>
            </div>
        `;

        // Create table for top customers
        const tableContainer = contentDiv.querySelector('#ltv-top-customers-table');
        if (tableContainer && topCustomers.length > 0) {
            new Tabulator(tableContainer, {
                data: topCustomers,
                layout: 'fitDataFill',
                columns: [
                    { title: 'Customer', field: 'name', minWidth: 200 },
                    {
                        title: 'Historical LTV', field: 'historical_ltv', minWidth: 120,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            return val ? `$${val.toLocaleString()}` : '-';
                        }
                    },
                    {
                        title: 'Predicted 12M LTV', field: 'predicted_12m_ltv', minWidth: 140,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            return val ? `<span style="color: #3fb950; font-weight: 600;">$${val.toLocaleString()}</span>` : '-';
                        }
                    },
                    {
                        title: 'Growth', minWidth: 100,
                        formatter: (cell) => {
                            const row = cell.getRow().getData();
                            const historical = row.historical_ltv || 0;
                            const predicted = row.predicted_12m_ltv || 0;
                            if (historical === 0) return '-';
                            const growth = ((predicted - historical) / historical * 100);
                            const color = growth > 0 ? '#3fb950' : '#f85149';
                            return `<span style="color: ${color}; font-weight: 600;">${growth > 0 ? '+' : ''}${growth.toFixed(1)}%</span>`;
                        }
                    },
                    { title: 'Segment', field: 'segment', minWidth: 140 }
                ]
            });
        }
    }

    renderNextBestActions(data) {
        const contentDiv = this.container.querySelector('#next-best-actions-content');
        if (!contentDiv || !data.recommendations) return;

        const { urgent, this_week, this_month } = data.recommendations;
        const allActions = [...(urgent || []), ...(this_week || []), ...(this_month || [])];

        contentDiv.innerHTML = `
            <div style="margin-bottom: 20px;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 20px;">
                    <div style="padding: 16px; background: rgba(248, 81, 73, 0.1); border: 1px solid #f85149; border-radius: 6px;">
                        <div style="font-size: 11px; color: #f85149; text-transform: uppercase; margin-bottom: 6px;">🚨 Urgent Actions</div>
                        <div style="font-size: 32px; color: #f85149; font-weight: 700;">${(urgent || []).length}</div>
                        <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Today</div>
                    </div>
                    <div style="padding: 16px; background: rgba(210, 153, 34, 0.1); border: 1px solid #d29922; border-radius: 6px;">
                        <div style="font-size: 11px; color: #d29922; text-transform: uppercase; margin-bottom: 6px;">📅 This Week</div>
                        <div style="font-size: 32px; color: #d29922; font-weight: 700;">${(this_week || []).length}</div>
                        <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Next 7 days</div>
                    </div>
                    <div style="padding: 16px; background: rgba(31, 111, 235, 0.1); border: 1px solid #1f6feb; border-radius: 6px;">
                        <div style="font-size: 11px; color: #1f6feb; text-transform: uppercase; margin-bottom: 6px;">📆 This Month</div>
                        <div style="font-size: 32px; color: #1f6feb; font-weight: 700;">${(this_month || []).length}</div>
                        <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Next 30 days</div>
                    </div>
                </div>
            </div>

            ${allActions.length > 0 ? `
                <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px;">
                    <h4 style="margin: 0 0 16px 0; color: #c9d1d9; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-tasks" style="color: #f78166;"></i>
                        Prioritized Action Queue
                    </h4>
                    <div id="next-best-actions-table"></div>
                </div>
            ` : `
                <div style="text-align: center; padding: 40px; color: #8b949e;">
                    <i class="fas fa-check-circle" style="font-size: 48px; margin-bottom: 16px; color: #3fb950;"></i>
                    <p style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">All Caught Up!</p>
                    <p style="font-size: 13px;">No immediate actions required at this time.</p>
                </div>
            `}
        `;

        if (allActions.length > 0) {
            const tableContainer = contentDiv.querySelector('#next-best-actions-table');
            if (tableContainer) {
                new Tabulator(tableContainer, {
                    data: allActions,
                    layout: 'fitDataFill',
                    initialSort: [{ column: 'priority', dir: 'asc' }],
                    columns: [
                        {
                            title: 'Priority', field: 'priority', width: 100,
                            formatter: (cell) => {
                                const priority = cell.getValue();
                                if (priority === 'urgent') return '<span style="color: #f85149; font-weight: 600;">🚨 URGENT</span>';
                                if (priority === 'high') return '<span style="color: #d29922; font-weight: 600;">⚠️ High</span>';
                                return '<span style="color: #1f6feb; font-weight: 600;">📌 Normal</span>';
                            }
                        },
                        { title: 'Customer', field: 'customer', minWidth: 180 },
                        { title: 'Action', field: 'action', minWidth: 300 },
                        { title: 'Reason', field: 'reason', minWidth: 200 },
                        {
                            title: 'Expected ROI', field: 'expected_roi', width: 120,
                            formatter: (cell) => {
                                const val = cell.getValue();
                                return val ? `<span style="color: #3fb950; font-weight: 600;">$${val.toLocaleString()}</span>` : '-';
                            }
                        }
                    ]
                });
            }
        }
    }

    renderCohortAnalysis(data) {
        const contentDiv = this.container.querySelector('#cohort-analysis-content');
        if (!contentDiv || !data.customers) return;

        // Group customers by acquisition year
        const cohorts = {};
        data.customers.forEach(customer => {
            if (customer.first_order_date) {
                const year = new Date(customer.first_order_date).getFullYear();
                if (!cohorts[year]) {
                    cohorts[year] = { year, count: 0, active: 0, churned: 0, total_revenue: 0 };
                }
                cohorts[year].count++;
                cohorts[year].total_revenue += customer.historical_ltv || 0;
                if (customer.segment && customer.segment.includes('Active')) cohorts[year].active++;
                else if (customer.segment && customer.segment.includes('Churned')) cohorts[year].churned++;
            }
        });

        const cohortData = Object.values(cohorts).sort((a, b) => b.year - a.year);

        contentDiv.innerHTML = `
            <div style="margin-bottom: 20px;">
                <p style="color: #8b949e; font-size: 13px; margin-bottom: 16px;">
                    <i class="fas fa-info-circle"></i> Analyzing customer retention patterns by acquisition year
                </p>
            </div>

            ${cohortData.length > 0 ? `
                <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px;">
                    <h4 style="margin: 0 0 16px 0; color: #c9d1d9; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-calendar-alt" style="color: #a371f7;"></i>
                        Cohort Retention by Acquisition Year
                    </h4>
                    <div id="cohort-analysis-table"></div>
                </div>
            ` : `
                <div style="text-align: center; padding: 40px; color: #8b949e;">
                    <i class="fas fa-database" style="font-size: 48px; margin-bottom: 16px;"></i>
                    <p style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">Insufficient Data</p>
                    <p style="font-size: 13px;">Not enough historical data for cohort analysis.</p>
                </div>
            `}
        `;

        if (cohortData.length > 0) {
            const tableContainer = contentDiv.querySelector('#cohort-analysis-table');
            if (tableContainer) {
                new Tabulator(tableContainer, {
                    data: cohortData,
                    layout: 'fitDataFill',
                    columns: [
                        { title: 'Acquisition Year', field: 'year', width: 140 },
                        { title: 'Total Customers', field: 'count', width: 140 },
                        { title: 'Active', field: 'active', width: 100 },
                        { title: 'Churned', field: 'churned', width: 100 },
                        {
                            title: 'Retention Rate', width: 140,
                            formatter: (cell) => {
                                const row = cell.getRow().getData();
                                const rate = row.count > 0 ? (row.active / row.count * 100) : 0;
                                const color = rate > 70 ? '#3fb950' : rate > 40 ? '#d29922' : '#f85149';
                                return `<span style="color: ${color}; font-weight: 600;">${rate.toFixed(1)}%</span>`;
                            }
                        },
                        {
                            title: 'Total Revenue', field: 'total_revenue', width: 140,
                            formatter: (cell) => {
                                const val = cell.getValue();
                                return `$${val.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
                            }
                        },
                        {
                            title: 'Avg per Customer', width: 140,
                            formatter: (cell) => {
                                const row = cell.getRow().getData();
                                const avg = row.count > 0 ? row.total_revenue / row.count : 0;
                                return `$${avg.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
                            }
                        }
                    ]
                });
            }
        }
    }

    renderLTVForecasting(data) {
        const contentDiv = this.container.querySelector('#ltv-forecasting-content');
        if (!contentDiv || !data.customers) return;

        // Calculate LTV metrics from customer data
        const customers = data.customers;
        const totalLTV = customers.reduce((sum, c) => sum + (c.lifetime_revenue || 0), 0);
        const avgLTV = totalLTV / customers.length;

        // Top 10 by LTV
        const topCustomers = [...customers]
            .sort((a, b) => (b.lifetime_revenue || 0) - (a.lifetime_revenue || 0))
            .slice(0, 10);

        contentDiv.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px;">
                <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                    <div style="font-size: 12px; color: #8b949e; margin-bottom: 8px;">TOTAL HISTORICAL LTV</div>
                    <div style="font-size: 32px; font-weight: 700; color: #58a6ff;">$${totalLTV.toLocaleString()}</div>
                </div>
                <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                    <div style="font-size: 12px; color: #8b949e; margin-bottom: 8px;">AVG CUSTOMER LTV</div>
                    <div style="font-size: 32px; font-weight: 700; color: #56d364;">$${Math.round(avgLTV).toLocaleString()}</div>
                </div>
                <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                    <div style="font-size: 12px; color: #8b949e; margin-bottom: 8px;">TOP CUSTOMER LTV</div>
                    <div style="font-size: 32px; font-weight: 700; color: #a371f7;">$${(topCustomers[0]?.lifetime_revenue || 0).toLocaleString()}</div>
                </div>
                <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                    <div style="font-size: 12px; color: #8b949e; margin-bottom: 8px;">ACTIVE CUSTOMERS</div>
                    <div style="font-size: 32px; font-weight: 700; color: #f0883e;">${customers.length}</div>
                </div>
            </div>
            
            <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px;">
                <h3 style="margin: 0 0 16px 0; color: #c9d1d9; font-size: 16px; font-weight: 600;">
                    🏆 Top 10 Customers by Predicted LTV
                </h3>
                <div id="ltv-top-customers-table"></div>
            </div>
        `;

        const tableContainer = contentDiv.querySelector('#ltv-top-customers-table');
        if (tableContainer) {
            new Tabulator(tableContainer, {
                data: topCustomers,
                layout: 'fitDataFill',
                columns: [
                    { title: 'Rank', formatter: 'rownum', width: 60, hozAlign: 'center' },
                    { title: 'Customer', field: 'contact_name', minWidth: 200 },
                    {
                        title: 'Historical LTV',
                        field: 'lifetime_revenue',
                        minWidth: 120,
                        formatter: (cell) => `$${(cell.getValue() || 0).toLocaleString()}`
                    },
                    {
                        title: 'Avg Invoice',
                        field: 'avg_invoice_value',
                        minWidth: 100,
                        formatter: (cell) => `$${(cell.getValue() || 0).toLocaleString()}`
                    },
                    {
                        title: 'Total Invoices',
                        field: 'total_invoices',
                        minWidth: 100,
                        hozAlign: 'center'
                    },
                    {
                        title: 'Churn Risk',
                        field: 'ml_churn_probability',
                        minWidth: 100,
                        formatter: (cell) => {
                            const val = cell.getValue() || 0;
                            const color = val > 70 ? '#f85149' : val > 40 ? '#f0883e' : '#56d364';
                            return `<span style="color: ${color}; font-weight: 600;">${val.toFixed(1)}%</span>`;
                        }
                    }
                ]
            });
        }
    }

    renderNextBestActions(data) {
        const contentDiv = this.container.querySelector('#next-best-actions-content');
        if (!contentDiv || !data.recommendations) return;

        const recs = data.recommendations;

        // Count actions by timeframe
        const urgentCount = recs.urgent?.length || 0;
        const thisWeekCount = recs.this_week?.length || 0;
        const thisMonthCount = recs.this_month?.length || 0;

        contentDiv.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px;">
                <div style="padding: 24px; background: #2d1117; border: 2px solid #f85149; border-radius: 6px;">
                    <div style="font-size: 12px; color: #f85149; font-weight: 600; margin-bottom: 8px;">🔴 URGENT ACTIONS</div>
                    <div style="font-size: 48px; font-weight: 700; color: #f85149;">${urgentCount}</div>
                    <div style="font-size: 13px; color: #8b949e; margin-top: 8px;">Today</div>
                </div>
                <div style="padding: 24px; background: #2d2412; border: 2px solid #f0883e; border-radius: 6px;">
                    <div style="font-size: 12px; color: #f0883e; font-weight: 600; margin-bottom: 8px;">🟡 THIS WEEK</div>
                    <div style="font-size: 48px; font-weight: 700; color: #f0883e;">${thisWeekCount}</div>
                    <div style="font-size: 13px; color: #8b949e; margin-top: 8px;">Next 7 days</div>
                </div>
                <div style="padding: 24px; background: #132639; border: 2px solid #58a6ff; border-radius: 6px;">
                    <div style="font-size: 12px; color: #58a6ff; font-weight: 600; margin-bottom: 8px;">🔵 THIS MONTH</div>
                    <div style="font-size: 48px; font-weight: 700; color: #58a6ff;">${thisMonthCount}</div>
                    <div style="font-size: 13px; color: #8b949e; margin-top: 8px;">Next 30 days</div>
                </div>
            </div>

            <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px;">
                <h3 style="margin: 0 0 16px 0; color: #c9d1d9; font-size: 16px; font-weight: 600; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-list"></i> Prioritized Action Queue
                </h3>
                <div id="next-best-actions-table"></div>
            </div>
        `;

        // Combine all recommendations into single prioritized list
        const allActions = [
            ...(recs.urgent || []).map(r => ({ ...r, priority: 'Urgent', icon: '🔴' })),
            ...(recs.this_week || []).map(r => ({ ...r, priority: 'This Week', icon: '🟡' })),
            ...(recs.this_month || []).map(r => ({ ...r, priority: 'This Month', icon: '🔵' }))
        ];

        const tableContainer = contentDiv.querySelector('#next-best-actions-table');
        if (tableContainer && allActions.length > 0) {
            new Tabulator(tableContainer, {
                data: allActions,
                layout: 'fitDataFill',
                columns: [
                    {
                        title: 'Priority',
                        field: 'icon',
                        width: 80,
                        hozAlign: 'center',
                        formatter: (cell) => `<span style="font-size: 20px;">${cell.getValue()}</span>`
                    },
                    {
                        title: 'Customer',
                        field: 'customer',
                        minWidth: 150
                    },
                    {
                        title: 'Action',
                        field: 'action',
                        minWidth: 300
                    },
                    {
                        title: 'Risk Score',
                        field: 'risk_score',
                        minWidth: 100,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            if (!val) return '-';
                            const color = val > 70 ? '#f85149' : val > 40 ? '#f0883e' : '#56d364';
                            return `<span style="color: ${color}; font-weight: 600;">${val}%</span>`;
                        }
                    },
                    {
                        title: 'Expected LTV',
                        field: 'ltv',
                        minWidth: 120,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            return val ? `$${val.toLocaleString()}` : '-';
                        }
                    }
                ]
            });
        }
    }

    renderCohortAnalysis(data) {
        const contentDiv = this.container.querySelector('#cohort-analysis-content');
        if (!contentDiv || !data.customers) return;

        // Group customers by first invoice month
        const cohorts = {};
        data.customers.forEach(customer => {
            if (customer.first_invoice_date) {
                const date = new Date(customer.first_invoice_date);
                const cohortKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;

                if (!cohorts[cohortKey]) {
                    cohorts[cohortKey] = {
                        month: cohortKey,
                        customers: [],
                        totalRevenue: 0,
                        activeCount: 0,
                        churnedCount: 0
                    };
                }

                cohorts[cohortKey].customers.push(customer);
                cohorts[cohortKey].totalRevenue += customer.lifetime_revenue || 0;

                if (customer.days_since_last_order < 90) {
                    cohorts[cohortKey].activeCount++;
                } else {
                    cohorts[cohortKey].churnedCount++;
                }
            }
        });

        // Convert to array and calculate retention
        const cohortArray = Object.values(cohorts)
            .map(cohort => ({
                ...cohort,
                size: cohort.customers.length,
                retention: cohort.size > 0 ? (cohort.activeCount / cohort.size * 100) : 0,
                avgRevenue: cohort.totalRevenue / cohort.size
            }))
            .sort((a, b) => b.month.localeCompare(a.month))
            .slice(0, 12); // Last 12 months

        contentDiv.innerHTML = `
            <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px;">
                <h3 style="margin: 0 0 16px 0; color: #c9d1d9; font-size: 16px; font-weight: 600;">
                    📊 Cohort Retention Analysis (Last 12 Months)
                </h3>
                <div id="cohort-analysis-table"></div>
            </div>
        `;

        const tableContainer = contentDiv.querySelector('#cohort-analysis-table');
        if (tableContainer) {
            new Tabulator(tableContainer, {
                data: cohortArray,
                layout: 'fitDataFill',
                columns: [
                    { title: 'Cohort Month', field: 'month', minWidth: 120 },
                    { title: 'Initial Size', field: 'size', minWidth: 100, hozAlign: 'center' },
                    { title: 'Still Active', field: 'activeCount', minWidth: 100, hozAlign: 'center' },
                    { title: 'Churned', field: 'churnedCount', minWidth: 100, hozAlign: 'center' },
                    {
                        title: 'Retention Rate',
                        field: 'retention',
                        minWidth: 120,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            const color = val >= 70 ? '#56d364' : val >= 50 ? '#f0883e' : '#f85149';
                            return `<span style="color: ${color}; font-weight: 600;">${val.toFixed(1)}%</span>`;
                        }
                    },
                    {
                        title: 'Total Revenue',
                        field: 'totalRevenue',
                        minWidth: 150,
                        formatter: (cell) => `$${cell.getValue().toLocaleString()}`
                    },
                    {
                        title: 'Avg per Customer',
                        field: 'avgRevenue',
                        minWidth: 150,
                        formatter: (cell) => `$${Math.round(cell.getValue()).toLocaleString()}`
                    }
                ]
            });
        }
    }

    async loadAllContactsForIntelligence() {
        console.log('[Xero] 📊 Loading contacts for All Contacts section...');

        try {
            let url = `${this.API_BASE_URL}/api/xero/contacts?business_id=${this.currentBusiness}`;

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            if (!data.success) {
                throw new Error(data.error || 'Failed to load contacts');
            }

            const contactsData = data.contacts || [];
            console.log(`[Xero] ✅ Loaded ${contactsData.length} contacts`);

            // Create contacts table in Section 5
            const tableContainer = this.container.querySelector('#all-contacts-table');
            if (tableContainer) {
                new Tabulator(tableContainer, {
                    data: contactsData,
                    layout: 'fitDataFill',
                    pagination: true,
                    paginationSize: 50,
                    columns: [
                        { title: 'Name', field: 'name', minWidth: 150 },
                        { title: 'Email', field: 'email', minWidth: 200 },
                        { title: 'Phone', field: 'phone', minWidth: 120 },
                        {
                            title: 'Type', field: 'is_customer', minWidth: 100,
                            formatter: (cell) => {
                                const isCustomer = cell.getValue();
                                const row = cell.getRow().getData();
                                if (isCustomer && row.is_supplier) return '👥 Both';
                                if (isCustomer) return '🛒 Customer';
                                if (row.is_supplier) return '📦 Supplier';
                                return '📋 Contact';
                            }
                        },
                        { title: 'Status', field: 'contact_status', minWidth: 100 },
                        {
                            title: 'Outstanding', field: 'accounts_receivable_outstanding', minWidth: 120,
                            formatter: (cell) => {
                                const val = cell.getValue();
                                return val ? `$${parseFloat(val).toLocaleString()}` : '-';
                            }
                        }
                    ]
                });
            }

        } catch (error) {
            console.error('[Xero] ❌ Error loading contacts:', error);
        }
    }

    // ========================================================================
    // PAYMENTS TAB
    // ========================================================================

    renderPayments() {
        console.log('[Xero] 📄 renderPayments() STARTED');
        const container = this.container.querySelector('.xero-tab-content-area');
        if (!container) {
            console.error('[Xero] ❌ Tab content area not found for payments!');
            return;
        }
        console.log('[Xero] ✅ Container found for payments');

        container.innerHTML = `
            <div class="xero-payments">
                <div class="xero-toolbar">
                    <div class="xero-toolbar-left">
                        <button class="xero-btn" id="xero-refresh-payments">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                    <div class="xero-toolbar-right">
                        <input type="text" class="xero-search" id="xero-payment-search" 
                               placeholder="Search payments...">
                    </div>
                </div>

                <!-- Date Range Filter Buttons -->
                <div style="margin-bottom: 15px;">
                    <label style="color: #8b949e; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; display: block;">Date Range</label>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <button class="xero-date-filter" data-months="1" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">1 Month</button>
                        <button class="xero-date-filter" data-months="2" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">2 Months</button>
                        <button class="xero-date-filter active" data-months="3" style="padding: 6px 12px; background: var(--xero-primary); border: 1px solid var(--xero-primary); border-radius: 6px; color: white; font-size: 12px; font-weight: 500; cursor: pointer;">3 Months</button>
                        <button class="xero-date-filter" data-months="6" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">6 Months</button>
                        <button class="xero-date-filter" data-months="9" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">9 Months</button>
                        <button class="xero-date-filter" data-months="12" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">1 Year</button>
                        <button class="xero-date-filter" data-months="24" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">2 Years</button>
                        <button class="xero-date-filter" data-months="36" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">3 Years</button>
                        <button class="xero-date-filter" data-months="" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">All Time</button>
                    </div>
                </div>

                <div id="xero-payments-table"></div>
            </div>
        `;

        // Add event listeners
        const refreshBtn = container.querySelector('#xero-refresh-payments');
        const searchInput = container.querySelector('#xero-payment-search');

        if (refreshBtn) refreshBtn.addEventListener('click', () => this.loadPayments());
        if (searchInput) searchInput.addEventListener('input', (e) => this.filterPayments(e.target.value));

        // Date range filter buttons
        const dateFilters = container.querySelectorAll('.xero-date-filter');
        dateFilters.forEach(btn => {
            btn.addEventListener('click', () => {
                dateFilters.forEach(b => {
                    b.style.background = '#30363d';
                    b.style.color = '#8b949e';
                    b.style.borderColor = '#30363d';
                    b.classList.remove('active');
                });
                btn.style.background = 'var(--xero-primary)';
                btn.style.color = 'white';
                btn.style.borderColor = 'var(--xero-primary)';
                btn.classList.add('active');

                const months = btn.dataset.months;
                this.dateRanges.payments = months ? parseInt(months) : null;
                this.loadPayments();
            });
        });
    }

    async loadPayments() {
        console.log('[Xero] 📊 loadPayments() STARTED');
        console.log('[Xero] Current business ID:', this.currentBusiness);

        try {
            let url = `${this.API_BASE_URL}/api/xero/payments?business_id=${this.currentBusiness}`;

            // Add date range filter if set
            const fromDate = this.getDateRangeStart(this.dateRanges.payments);
            if (fromDate) {
                url += `&from_date=${fromDate}`;
            }

            console.log('[Xero] 🌐 Fetching payments from:', url);

            const response = await fetch(url);
            console.log('[Xero] Response status:', response.status, response.statusText);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('[Xero] Response data:', {
                success: data.success,
                paymentCount: data.payments?.length || 0,
                hasError: !!data.error
            });

            if (!data.success) {
                throw new Error(data.error || 'Failed to load payments');
            }

            this.data.payments = data.payments || [];
            console.log(`[Xero] ✅ Loaded ${this.data.payments.length} payments into memory`);

            console.log('[Xero] 📊 Creating payments table...');
            this.createPaymentsTable();
            console.log('[Xero] ✅ Payments table created');
        } catch (error) {
            console.error('[Xero] ❌ Error loading payments:', error);
            console.error('[Xero] Error stack:', error.stack);
        }
    }

    createPaymentsTable() {
        const container = this.container.querySelector('#xero-payments-table');
        if (!container) return;

        this.tables.payments = new Tabulator(container, {
            data: this.data.payments,
            layout: 'fitData',
            autoColumns: false,
            responsiveLayout: 'collapse',
            pagination: 'local',
            paginationSize: 50,
            columns: [
                {
                    title: 'Date',
                    field: 'date',
                    minWidth: 90,
                    maxWidth: 130,
                    widthGrow: 1,
                    widthShrink: 1,
                    formatter: (cell) => this.formatDate(cell.getValue())
                },
                {
                    title: 'Invoice #',
                    field: 'invoice_number',
                    minWidth: 100,
                    maxWidth: 150,
                    widthGrow: 1,
                    widthShrink: 1
                },
                {
                    title: 'Amount',
                    field: 'amount',
                    minWidth: 90,
                    maxWidth: 150,
                    widthGrow: 1,
                    widthShrink: 1,
                    hozAlign: 'right',
                    formatter: (cell) => this.formatCurrency(cell.getValue())
                },
                {
                    title: 'Status',
                    field: 'status',
                    minWidth: 90,
                    maxWidth: 130,
                    widthGrow: 1,
                    widthShrink: 1,
                    formatter: (cell) => {
                        const status = cell.getValue();
                        return this.getStatusBadge(status);
                    }
                }
            ]
        });
    }

    // ========================================================================
    // ACCOUNTS TAB
    // ========================================================================

    renderAccounts() {
        console.log('[Xero] 📄 renderAccounts() STARTED');
        const contentArea = this.container.querySelector('.xero-tab-content-area');
        if (!contentArea) {
            console.error('[Xero] ❌ Content area not found for accounts!');
            return;
        }
        console.log('[Xero] ✅ Content area found for accounts');

        contentArea.innerHTML = `
            <div class="xero-accounts">
                <div class="xero-toolbar">
                    <div class="xero-toolbar-left">
                        <button class="xero-btn" id="xero-refresh-accounts">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                    <div class="xero-toolbar-right">
                        <input type="text" class="xero-search" id="xero-account-search" 
                               placeholder="Search accounts...">
                    </div>
                </div>
                <div id="xero-accounts-table"></div>
            </div>
        `;

        console.log('[Xero] ✅ Accounts HTML injected');

        // Add event listeners
        const refreshBtn = contentArea.querySelector('#xero-refresh-accounts');
        const searchInput = contentArea.querySelector('#xero-account-search');

        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadAccounts());
            console.log('[Xero] ✅ Refresh button event listener added');
        }
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.filterAccounts(e.target.value));
            console.log('[Xero] ✅ Search input event listener added');
        }
    }

    async loadAccounts() {
        console.log('[Xero] 📊 loadAccounts() STARTED');
        console.log('[Xero] Current business ID:', this.currentBusiness);

        try {
            const url = `${this.API_BASE_URL}/api/xero/accounts?business_id=${this.currentBusiness}`;
            console.log('[Xero] 🌐 Fetching accounts from:', url);

            const response = await fetch(url);
            console.log('[Xero] Response status:', response.status, response.statusText);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('[Xero] Response data:', {
                success: data.success,
                accountCount: data.accounts?.length || 0,
                hasError: !!data.error
            });

            if (!data.success) {
                throw new Error(data.error || 'Failed to load accounts');
            }

            this.data.accounts = data.accounts || [];
            console.log(`[Xero] ✅ Loaded ${this.data.accounts.length} accounts into memory`);

            console.log('[Xero] 📊 Creating accounts table...');
            this.createAccountsTable();
            console.log('[Xero] ✅ Accounts table created');
        } catch (error) {
            console.error('[Xero] ❌ Error loading accounts:', error);
            console.error('[Xero] Error stack:', error.stack);
        }
    }

    createAccountsTable() {
        const container = this.container.querySelector('#xero-accounts-table');
        if (!container) return;

        this.tables.accounts = new Tabulator(container, {
            data: this.data.accounts,
            layout: 'fitData',
            autoColumns: false,
            responsiveLayout: 'collapse',
            pagination: 'local',
            paginationSize: 50,
            columns: [
                { title: 'Code', field: 'code', minWidth: 70, maxWidth: 100, widthGrow: 1, widthShrink: 1 },
                { title: 'Name', field: 'name', minWidth: 150, maxWidth: 300, widthGrow: 3, widthShrink: 1 },
                { title: 'Type', field: 'type', minWidth: 100, maxWidth: 180, widthGrow: 1, widthShrink: 1 },
                { title: 'Tax Type', field: 'tax_type', minWidth: 100, maxWidth: 150, widthGrow: 1, widthShrink: 1 }
            ]
        });
    }

    // ========================================================================
    // REPORTS TAB
    // ========================================================================

    renderReports() {
        console.log('[Xero] 📄 renderReports() STARTED');
        const contentArea = this.container.querySelector('.xero-tab-content-area');
        if (!contentArea) {
            console.error('[Xero] ❌ Content area not found for reports!');
            return;
        }
        console.log('[Xero] ✅ Content area found for reports');

        contentArea.innerHTML = `
            <div class="xero-reports" style="padding: 20px;">
                <h2 style="margin-bottom: 24px; color: #c9d1d9;">Multi-Business Reports</h2>
                
                <div class="xero-reports-section" style="margin-bottom: 40px;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px;">
                        <button class="xero-btn" id="xero-show-business-comparison" style="padding: 16px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 14px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-building" style="font-size: 24px; color: var(--xero-primary);"></i>
                            <div>
                                <div style="font-weight: 600;">Business Comparison</div>
                                <div style="font-size: 12px; color: #8b949e;">Compare performance across all businesses</div>
                            </div>
                        </button>
                        <button class="xero-btn" id="xero-show-consolidated-revenue" style="padding: 16px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 14px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-chart-pie" style="font-size: 24px; color: var(--xero-primary);"></i>
                            <div>
                                <div style="font-weight: 600;">Consolidated Revenue</div>
                                <div style="font-size: 12px; color: #8b949e;">Total revenue across all businesses</div>
                            </div>
                        </button>
                        <button class="xero-btn" id="xero-show-customer-overlap" style="padding: 16px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 14px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-exchange-alt" style="font-size: 24px; color: var(--xero-primary);"></i>
                            <div>
                                <div style="font-weight: 600;">Customer Overlap</div>
                                <div style="font-size: 12px; color: #8b949e;">Customers using multiple businesses</div>
                            </div>
                        </button>
                    </div>
                </div>
                
                <h2 style="margin-bottom: 24px; color: #c9d1d9;">Advanced Analytics</h2>
                
                <div class="xero-reports-section">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px;">
                        <button class="xero-btn" id="xero-show-revenue-by-product" style="padding: 16px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 14px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-box" style="font-size: 24px; color: var(--xero-primary);"></i>
                            <div>
                                <div style="font-weight: 600;">Revenue by Product</div>
                                <div style="font-size: 12px; color: #8b949e;">Product/service revenue breakdown</div>
                            </div>
                        </button>
                        <button class="xero-btn" id="xero-show-seasonality" style="padding: 16px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 14px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-calendar-alt" style="font-size: 24px; color: var(--xero-primary);"></i>
                            <div>
                                <div style="font-weight: 600;">Seasonality Analysis</div>
                                <div style="font-size: 12px; color: #8b949e;">Monthly patterns and trends</div>
                            </div>
                        </button>
                        <button class="xero-btn" id="xero-show-forecast" style="padding: 16px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 14px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-chart-line" style="font-size: 24px; color: var(--xero-primary);"></i>
                            <div>
                                <div style="font-weight: 600;">Revenue Forecast</div>
                                <div style="font-size: 12px; color: #8b949e;">Predictive revenue projections</div>
                            </div>
                        </button>
                    </div>
                </div>
                
                <h2 style="margin-top: 40px; margin-bottom: 24px; color: #c9d1d9;">
                    <i class="fas fa-robot" style="margin-right: 8px; color: #13B5EA;"></i>ML-Powered Predictions
                </h2>
                
                <div class="xero-reports-section">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px;">
                        <button class="xero-btn" id="xero-show-payment-risk" style="padding: 16px; background: linear-gradient(135deg, #21262d 0%, #1a1f25 100%); border: 1px solid #f8514950; border-radius: 6px; color: #c9d1d9; font-size: 14px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-exclamation-triangle" style="font-size: 24px; color: #f85149;"></i>
                            <div>
                                <div style="font-weight: 600;"><i class="fas fa-credit-card" style="margin-right: 6px;"></i>Payment Risk Prediction</div>
                                <div style="font-size: 12px; color: #8b949e;">ML forecasts late payments (saves $50K/yr)</div>
                            </div>
                        </button>
                        <button class="xero-btn" id="xero-show-churn-risk" style="padding: 16px; background: linear-gradient(135deg, #21262d 0%, #1a1f25 100%); border: 1px solid #d2992250; border-radius: 6px; color: #c9d1d9; font-size: 14px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-user-slash" style="font-size: 24px; color: #d29922;"></i>
                            <div>
                                <div style="font-weight: 600;"><i class="fas fa-chart-line-down" style="margin-right: 6px;"></i>Customer Churn Prediction</div>
                                <div style="font-size: 12px; color: #8b949e;">ML identifies at-risk customers (saves $80K/yr)</div>
                            </div>
                        </button>
                    </div>
                </div>
                
                <div id="xero-reports-results" style="margin-top: 30px;"></div>
            </div>
        `;

        // Add event listeners
        const businessComparisonBtn = contentArea.querySelector('#xero-show-business-comparison');
        const consolidatedRevenueBtn = contentArea.querySelector('#xero-show-consolidated-revenue');
        const customerOverlapBtn = contentArea.querySelector('#xero-show-customer-overlap');
        const revenueByProductBtn = contentArea.querySelector('#xero-show-revenue-by-product');
        const seasonalityBtn = contentArea.querySelector('#xero-show-seasonality');
        const forecastBtn = contentArea.querySelector('#xero-show-forecast');

        if (businessComparisonBtn) businessComparisonBtn.addEventListener('click', async () => {
            businessComparisonBtn.disabled = true;
            businessComparisonBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            await this.showBusinessComparison();
            businessComparisonBtn.disabled = false;
            businessComparisonBtn.innerHTML = '<i class="fas fa-building"></i><div><div style="font-weight: 600;">Business Comparison</div><div style="font-size: 12px; color: #8b949e;">Compare performance across all businesses</div></div>';
        });
        if (consolidatedRevenueBtn) consolidatedRevenueBtn.addEventListener('click', async () => {
            consolidatedRevenueBtn.disabled = true;
            consolidatedRevenueBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            await this.showConsolidatedRevenue();
            consolidatedRevenueBtn.disabled = false;
            consolidatedRevenueBtn.innerHTML = '<i class="fas fa-chart-pie"></i><div><div style="font-weight: 600;">Consolidated Revenue</div><div style="font-size: 12px; color: #8b949e;">Total revenue across all businesses</div></div>';
        });
        if (customerOverlapBtn) customerOverlapBtn.addEventListener('click', async () => {
            customerOverlapBtn.disabled = true;
            customerOverlapBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            await this.showCustomerOverlap();
            customerOverlapBtn.disabled = false;
            customerOverlapBtn.innerHTML = '<i class="fas fa-users"></i><div><div style="font-weight: 600;">Customer Overlap</div><div style="font-size: 12px; color: #8b949e;">Customers using multiple businesses</div></div>';
        });
        if (revenueByProductBtn) revenueByProductBtn.addEventListener('click', async () => {
            revenueByProductBtn.disabled = true;
            revenueByProductBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            await this.showRevenueByProduct();
            revenueByProductBtn.disabled = false;
            revenueByProductBtn.innerHTML = '<i class="fas fa-box"></i><div><div style="font-weight: 600;">Revenue by Product</div><div style="font-size: 12px; color: #8b949e;">Product/service revenue breakdown</div></div>';
        });
        if (seasonalityBtn) seasonalityBtn.addEventListener('click', async () => {
            seasonalityBtn.disabled = true;
            seasonalityBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            await this.showSeasonality();
            seasonalityBtn.disabled = false;
            seasonalityBtn.innerHTML = '<i class="fas fa-calendar-alt"></i><div><div style="font-weight: 600;">Seasonality Analysis</div><div style="font-size: 12px; color: #8b949e;">Monthly patterns and trends</div></div>';
        });
        if (forecastBtn) forecastBtn.addEventListener('click', async () => {
            forecastBtn.disabled = true;
            forecastBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            await this.showForecast();
            forecastBtn.disabled = false;
            forecastBtn.innerHTML = '<i class="fas fa-chart-line"></i><div><div style="font-weight: 600;">Revenue Forecast</div><div style="font-size: 12px; color: #8b949e;">Predictive revenue projections</div></div>';
        });

        // ML feature event listeners
        const paymentRiskBtn = contentArea.querySelector('#xero-show-payment-risk');
        const churnRiskBtn = contentArea.querySelector('#xero-show-churn-risk');

        if (paymentRiskBtn) paymentRiskBtn.addEventListener('click', async () => {
            paymentRiskBtn.disabled = true;
            paymentRiskBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running ML Model...';
            await this.showPaymentRiskML();
            paymentRiskBtn.disabled = false;
            paymentRiskBtn.innerHTML = '<i class="fas fa-exclamation-triangle" style="color: #f85149;"></i><div><div style="font-weight: 600;"><i class="fas fa-credit-card" style="margin-right: 6px;"></i>Payment Risk Prediction</div><div style="font-size: 12px; color: #8b949e;">ML forecasts late payments (saves $50K/yr)</div></div>';
        });

        if (churnRiskBtn) churnRiskBtn.addEventListener('click', async () => {
            churnRiskBtn.disabled = true;
            churnRiskBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running ML Model...';
            await this.showChurnRiskML();
            churnRiskBtn.disabled = false;
            churnRiskBtn.innerHTML = '<i class="fas fa-user-slash" style="color: #d29922;"></i><div><div style="font-weight: 600;"><i class="fas fa-chart-line-down" style="margin-right: 6px;"></i>Customer Churn Prediction</div><div style="font-size: 12px; color: #8b949e;">ML identifies at-risk customers (saves $80K/yr)</div></div>';
        });

        console.log('[Xero] ✅ Reports HTML injected');
    }

    async loadReports() {
        console.log('[Xero] 📊 loadReports() STARTED');
        console.log('[Xero] Reports tab - no data to load yet');
        // TODO: Implement reports
    }

    // ========================================================================
    // UTILITY METHODS
    // ========================================================================

    formatCurrency(amount) {
        if (amount === null || amount === undefined) return '$0.00';
        return new Intl.NumberFormat('en-AU', {
            style: 'currency',
            currency: 'AUD'
        }).format(amount);
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-AU', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    getStatusBadge(status) {
        const colors = {
            'PAID': 'success',
            'AUTHORISED': 'info',
            'DRAFT': 'warning',
            'SUBMITTED': 'info',
            'VOIDED': 'danger'
        };
        const color = colors[status] || 'secondary';
        return `<span class="xero-badge xero-badge-${color}">${status}</span>`;
    }

    showLoading(message = 'Loading...') {
        const contentArea = this.container?.querySelector('.xero-tab-content-area');
        if (!contentArea) return;

        contentArea.innerHTML = `
            <div class="xero-loading-container" style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 400px; gap: 20px;">
                <div class="xero-spinner" style="width: 48px; height: 48px; border: 4px solid #30363d; border-top-color: #13B5EA; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                <p style="color: #8b949e; font-size: 14px; margin: 0;">${message}</p>
            </div>
        `;
    }

    hideLoading() {
        const loading = this.container?.querySelector('.xero-loading-container');
        if (loading) {
            loading.remove();
        }
    }

    showError(message) {
        console.error('[Xero Error]', message);
        const contentArea = this.container?.querySelector('.xero-tab-content-area');
        if (!contentArea) return;

        contentArea.innerHTML = `
            <div class="xero-error-container" style="padding: 40px; text-align: center;">
                <div style="max-width: 500px; margin: 0 auto; padding: 30px; background: #1c1f26; border: 1px solid #f85149; border-radius: 6px;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: #f85149; margin-bottom: 20px;"></i>
                    <h3 style="color: #ffffff; margin-bottom: 10px;">Error Loading Data</h3>
                    <p style="color: #8b949e; margin-bottom: 20px;">${message}</p>
                    <button class="xero-btn xero-btn-primary" onclick="location.reload()">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                </div>
            </div>
        `;
    }

    showInvoiceDetails(invoice) {
        console.log('[Xero] Showing invoice details modal:', invoice);
        this.showDetailsModal('invoice', invoice);
    }

    showContactDetails(contact) {
        console.log('[Xero] Showing contact details modal:', contact);
        this.showDetailsModal('contact', contact);
    }

    showDetailsModal(type, data) {
        // Create modal container if it doesn't exist
        let modal = document.getElementById('xero-details-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'xero-details-modal';
            modal.style.cssText = `
                position: fixed;
                top: 10%;
                left: 50%;
                transform: translateX(-50%);
                width: 900px;
                max-width: 95vw;
                max-height: 85vh;
                background: #0d1117;
                border: 1px solid #30363d;
                border-radius: 8px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
                z-index: 10000;
                display: none;
                flex-direction: column;
                overflow: hidden;
            `;
            document.body.appendChild(modal);

            // Make modal draggable
            this.makeModalDraggable(modal);
        }

        // Build unified modal content with tabs
        modal.innerHTML = this.buildUnifiedModalContent(type, data);

        // Show modal
        modal.style.display = 'flex';

        // Add close button handler
        const closeBtn = modal.querySelector('.xero-modal-close');
        if (closeBtn) {
            closeBtn.onclick = () => {
                modal.style.display = 'none';
            };
        }

        // Add tab switching handlers
        const tabButtons = modal.querySelectorAll('.modal-tab-btn');
        const tabContents = modal.querySelectorAll('.modal-tab-content');

        tabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetTab = btn.dataset.tab;

                // Update active tab button
                tabButtons.forEach(b => {
                    b.style.background = b.dataset.tab === targetTab ? '#1f6feb' : '#21262d';
                    b.style.color = b.dataset.tab === targetTab ? 'white' : '#8b949e';
                    b.style.borderColor = b.dataset.tab === targetTab ? '#1f6feb' : '#30363d';
                });

                // Show active tab content
                tabContents.forEach(content => {
                    content.style.display = content.dataset.tab === targetTab ? 'block' : 'none';
                });
            });
        });
    }

    makeModalDraggable(modal) {
        let isDragging = false;
        let currentX;
        let currentY;
        let initialX;
        let initialY;
        let xOffset = 0;
        let yOffset = 0;

        modal.addEventListener('mousedown', (e) => {
            // Only drag if clicking the header
            if (e.target.closest('.xero-modal-header')) {
                isDragging = true;
                initialX = e.clientX - xOffset;
                initialY = e.clientY - yOffset;
                modal.style.cursor = 'grabbing';
            }
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;
                xOffset = currentX;
                yOffset = currentY;
                modal.style.transform = `translate(calc(-50% + ${currentX}px), ${currentY}px)`;
            }
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                modal.style.cursor = 'default';
            }
        });
    }

    buildUnifiedModalContent(type, data) {
        // Get contact name - works for both invoice and contact types
        const contactName = data.contact_name || data.name || data.Contact?.Name || data.Name || 'Customer Details';
        const contactId = data.contact_id || data.ContactID || null;

        // Get related invoices for this contact
        const relatedInvoices = contactId
            ? (this.data.invoices || []).filter(inv =>
                inv.contact_id === contactId ||
                inv.ContactID === contactId ||
                inv.contact_name === contactName
            )
            : (type === 'invoice' ? [data] : []);

        // Determine which tabs to show based on available data
        const hasIntelligenceData = data.rfm_segment || data.unified_risk_score || data.ml_churn_probability;
        
        return `
            <div class="xero-modal-header" style="
                padding: 16px 20px;
                background: #161b22;
                border-bottom: 1px solid #30363d;
                display: flex;
                justify-content: space-between;
                align-items: center;
                cursor: grab;
            ">
                <h3 style="margin: 0; color: #c9d1d9; font-size: 18px; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-user-circle" style="color: #58a6ff;"></i>
                    ${contactName}
                </h3>
                <button class="xero-modal-close" style="
                    background: none;
                    border: none;
                    color: #8b949e;
                    font-size: 24px;
                    cursor: pointer;
                    padding: 0;
                    width: 32px;
                    height: 32px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 4px;
                    transition: all 0.2s;
                " onmouseover="this.style.background='#21262d'; this.style.color='#c9d1d9'" onmouseout="this.style.background='none'; this.style.color='#8b949e'">
                    <i class="fas fa-times"></i>
                </button>
            </div>

            <!-- Tab Navigation -->
            <div style="
                padding: 12px 20px;
                background: #161b22;
                border-bottom: 1px solid #30363d;
                display: flex;
                gap: 8px;
            ">
                ${hasIntelligenceData ? `
                    <button class="modal-tab-btn" data-tab="intelligence" style="
                        padding: 8px 16px;
                        background: #1f6feb;
                        border: 1px solid #1f6feb;
                        border-radius: 6px;
                        color: white;
                        font-size: 13px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.2s;
                    ">
                        <i class="fas fa-brain"></i> Customer Intelligence
                    </button>
                ` : ''}
                <button class="modal-tab-btn" data-tab="details" style="
                    padding: 8px 16px;
                    background: ${hasIntelligenceData ? '#21262d' : '#1f6feb'};
                    border: 1px solid ${hasIntelligenceData ? '#30363d' : '#1f6feb'};
                    border-radius: 6px;
                    color: ${hasIntelligenceData ? '#8b949e' : 'white'};
                    font-size: 13px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                ">
                    <i class="fas fa-user"></i> Customer Details
                </button>
                <button class="modal-tab-btn" data-tab="invoices" style="
                    padding: 8px 16px;
                    background: #21262d;
                    border: 1px solid #30363d;
                    border-radius: 6px;
                    color: #8b949e;
                    font-size: 13px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                ">
                    <i class="fas fa-file-invoice"></i> Invoices (${relatedInvoices.length})
                </button>
            </div>

            <div class="xero-modal-body" style="
                padding: 20px;
                overflow-y: auto;
                max-height: calc(85vh - 140px);
            ">
                ${hasIntelligenceData ? `
                    <!-- Customer Intelligence Tab -->
                    <div class="modal-tab-content" data-tab="intelligence" style="display: block;">
                        ${this.buildCustomerIntelligenceContent(data)}
                    </div>
                ` : ''}

                <!-- Customer Details Tab -->
                <div class="modal-tab-content" data-tab="details" style="display: ${hasIntelligenceData ? 'none' : 'block'};">
                    ${this.buildCustomerDetailsContent(data, type, contactId)}
                </div>

                <!-- Invoices Tab -->
                <div class="modal-tab-content" data-tab="invoices" style="display: none;">
                    ${this.buildInvoicesTabContent(relatedInvoices, contactName, data)}
                </div>
            </div>
        `;
    }

    buildCustomerIntelligenceContent(data) {
        // This shows the intelligence/analytics data: RFM, risk scores, churn, etc.
        const contact = {
            lifetime_revenue: data.lifetime_revenue || 0,
            rfm_segment: data.rfm_segment,
            unified_risk_score: data.unified_risk_score,
            ml_churn_probability: data.ml_churn_probability,
            days_since_last_order: data.days_since_last_order,
            recommended_action: data.recommended_action,
            recency_score: data.recency_score,
            frequency_score: data.frequency_score,
            monetary_score: data.monetary_score
        };

        return `
            <!-- Key Metrics Grid -->
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 24px;">
                <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; border-left: 3px solid #3fb950;">
                    <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Lifetime Revenue</div>
                    <div style="font-size: 32px; color: #3fb950; font-weight: 700;">$${contact.lifetime_revenue.toLocaleString()}</div>
                </div>
                <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; border-left: 3px solid #1f6feb;">
                    <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Customer Segment</div>
                    <div style="font-size: 24px; margin-top: 8px;">
                        <span style="
                            padding: 8px 16px;
                            border-radius: 6px;
                            font-weight: 700;
                            ${contact.rfm_segment === 'Champions' ? 'background: rgba(35, 134, 54, 0.2); color: #238636;' :
                                contact.rfm_segment === 'At Risk' ? 'background: rgba(210, 153, 34, 0.2); color: #d29922;' :
                                contact.rfm_segment === 'Lost' ? 'background: rgba(248, 81, 73, 0.2); color: #f85149;' :
                                'background: rgba(31, 111, 235, 0.2); color: #1f6feb;'}
                        ">
                            ${contact.rfm_segment || 'N/A'}
                        </span>
                    </div>
                </div>
            </div>

            <!-- RFM Scores -->
            ${contact.recency_score || contact.frequency_score || contact.monetary_score ? `
                <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 24px;">
                    <h4 style="margin: 0 0 16px 0; color: #c9d1d9; font-size: 14px; text-transform: uppercase;">
                        <i class="fas fa-chart-bar" style="color: #1f6feb;"></i> RFM Analysis
                    </h4>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
                        ${contact.recency_score ? `
                            <div>
                                <div style="font-size: 11px; color: #8b949e; margin-bottom: 8px;">Recency Score</div>
                                <div style="font-size: 36px; color: #58a6ff; font-weight: 700;">${contact.recency_score}</div>
                                <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">How recently purchased</div>
                            </div>
                        ` : ''}
                        ${contact.frequency_score ? `
                            <div>
                                <div style="font-size: 11px; color: #8b949e; margin-bottom: 8px;">Frequency Score</div>
                                <div style="font-size: 36px; color: #a371f7; font-weight: 700;">${contact.frequency_score}</div>
                                <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">How often purchases</div>
                            </div>
                        ` : ''}
                        ${contact.monetary_score ? `
                            <div>
                                <div style="font-size: 11px; color: #8b949e; margin-bottom: 8px;">Monetary Score</div>
                                <div style="font-size: 36px; color: #3fb950; font-weight: 700;">${contact.monetary_score}</div>
                                <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">How much spends</div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            ` : ''}

            <!-- Risk Analysis -->
            <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 24px;">
                <h4 style="margin: 0 0 16px 0; color: #c9d1d9; font-size: 14px; text-transform: uppercase;">
                    <i class="fas fa-exclamation-triangle" style="color: #f85149;"></i> Risk Analysis
                </h4>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
                    ${contact.unified_risk_score ? `
                        <div>
                            <div style="font-size: 11px; color: #8b949e; margin-bottom: 8px;">Risk Score</div>
                            <div style="font-size: 36px; color: ${contact.unified_risk_score > 70 ? '#f85149' : contact.unified_risk_score > 40 ? '#d29922' : '#3fb950'}; font-weight: 700;">
                                ${contact.unified_risk_score.toFixed(1)}%
                            </div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Overall risk level</div>
                        </div>
                    ` : ''}
                    ${contact.ml_churn_probability ? `
                        <div>
                            <div style="font-size: 11px; color: #8b949e; margin-bottom: 8px;">Churn Probability</div>
                            <div style="font-size: 36px; color: #f85149; font-weight: 700;">${contact.ml_churn_probability.toFixed(1)}%</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Likelihood to leave</div>
                        </div>
                    ` : ''}
                    ${contact.days_since_last_order !== undefined ? `
                        <div>
                            <div style="font-size: 11px; color: #8b949e; margin-bottom: 8px;">Days Inactive</div>
                            <div style="font-size: 36px; color: ${contact.days_since_last_order > 180 ? '#f85149' : contact.days_since_last_order > 90 ? '#d29922' : '#3fb950'}; font-weight: 700;">
                                ${contact.days_since_last_order}d
                            </div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Since last order</div>
                        </div>
                    ` : ''}
                </div>

                ${contact.recommended_action ? `
                    <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #30363d;">
                        <div style="font-size: 11px; color: #8b949e; margin-bottom: 8px;">Recommended Action</div>
                        <div style="font-size: 16px; color: #58a6ff; font-weight: 600; display: flex; align-items: center; gap: 8px;">
                            ${contact.recommended_action === 'call_now' ? '📞 Call Now - Immediate attention required' :
                                contact.recommended_action === 'email_campaign' ? '✉️ Email Campaign - Re-engagement needed' :
                                contact.recommended_action === 'monitor' ? '👀 Monitor - Keep watching' : contact.recommended_action}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    buildCustomerDetailsContent(data, type, contactId) {
        // This shows actual contact information: name, address, phone, email, etc.
        // We'll make this load via API call when the tab is clicked
        const contact = type === 'contact' ? data : {
            contact_name: data.contact_name || data.Contact?.Name,
            email_address: data.email || data.email_address || data.Contact?.EmailAddress,
            phone: data.phone || data.Contact?.Phones?.[0]?.PhoneNumber,
            contact_status: data.contact_status || 'N/A'
        };

        return `
            <div id="customer-details-loading" style="display: none; text-align: center; padding: 40px; color: #8b949e;">
                <i class="fas fa-spinner fa-spin" style="font-size: 32px; margin-bottom: 12px;"></i>
                <div>Loading customer details...</div>
            </div>
            
            <div id="customer-details-content">
                <!-- Contact Information -->
                <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 16px 0; color: #c9d1d9; font-size: 14px; text-transform: uppercase;">
                        <i class="fas fa-address-card" style="color: #58a6ff;"></i> Contact Information
                    </h4>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
                        <div>
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 4px;">Email</div>
                            <div style="font-size: 14px; color: #58a6ff; word-break: break-all;">${contact.email_address || 'N/A'}</div>
                        </div>
                        <div>
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 4px;">Phone</div>
                            <div style="font-size: 14px; color: #c9d1d9;">${contact.phone || 'N/A'}</div>
                        </div>
                        <div>
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 4px;">Status</div>
                            <div style="font-size: 14px; color: #c9d1d9; font-weight: 600;">${contact.contact_status || 'Active'}</div>
                        </div>
                    </div>
                </div>

                <!-- Placeholder for full details from API -->
                <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; text-align: center; color: #8b949e;">
                    <i class="fas fa-info-circle" style="font-size: 24px; margin-bottom: 12px; opacity: 0.5;"></i>
                    <div style="font-size: 13px;">Additional customer details will be loaded from Xero API</div>
                    <div style="font-size: 11px; margin-top: 8px;">Including addresses, tax numbers, account details, etc.</div>
                </div>
            </div>
        `;
    }

    buildInvoicesTabContent(invoices, contactName, contactData) {
        if (!invoices || invoices.length === 0) {
            return `
                <div style="text-align: center; padding: 60px 20px; color: #8b949e;">
                    <i class="fas fa-inbox" style="font-size: 48px; margin-bottom: 16px; opacity: 0.5;"></i>
                    <div style="font-size: 16px;">No invoices found for ${contactName}</div>
                </div>
            `;
        }

        // Calculate totals
        const totalRevenue = invoices.reduce((sum, inv) => sum + (inv.total || inv.Total || 0), 0);
        const totalOutstanding = invoices.filter(inv => inv.status !== 'PAID' && inv.Status !== 'PAID')
            .reduce((sum, inv) => sum + (inv.amount_due || inv.AmountDue || 0), 0);
        const paidCount = invoices.filter(inv => inv.status === 'PAID' || inv.Status === 'PAID').length;

        return `
            <!-- Invoice Summary Cards -->
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px;">
                <div style="padding: 12px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                    <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 4px;">Total Invoices</div>
                    <div style="font-size: 24px; color: #58a6ff; font-weight: 700;">${invoices.length}</div>
                </div>
                <div style="padding: 12px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                    <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 4px;">Total Revenue</div>
                    <div style="font-size: 24px; color: #3fb950; font-weight: 700;">$${totalRevenue.toLocaleString()}</div>
                </div>
                <div style="padding: 12px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                    <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 4px;">Outstanding</div>
                    <div style="font-size: 24px; color: ${totalOutstanding > 0 ? '#f0883e' : '#3fb950'}; font-weight: 700;">$${totalOutstanding.toLocaleString()}</div>
                </div>
            </div>

            <!-- Invoice List -->
            <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; overflow: hidden;">
                ${invoices.sort((a, b) => {
            const dateA = new Date(a.date || a.Date || 0);
            const dateB = new Date(b.date || b.Date || 0);
            return dateB - dateA;
        }).map(inv => {
            const status = inv.status || inv.Status || 'UNKNOWN';
            const isPaid = status === 'PAID';
            const total = inv.total || inv.Total || 0;
            const amountDue = inv.amount_due || inv.AmountDue || 0;
            const invoiceNumber = inv.invoice_number || inv.InvoiceNumber || 'N/A';
            const date = inv.date || inv.Date || 'N/A';

            return `
                        <div style="
                            padding: 16px;
                            border-bottom: 1px solid #30363d;
                            display: grid;
                            grid-template-columns: 120px 1fr 120px 100px 120px;
                            gap: 16px;
                            align-items: center;
                            transition: background 0.2s;
                        " onmouseover="this.style.background='#21262d'" onmouseout="this.style.background='transparent'">
                            <div>
                                <div style="font-size: 11px; color: #8b949e; margin-bottom: 2px;">Invoice #</div>
                                <div style="font-size: 14px; color: #58a6ff; font-weight: 600;">${invoiceNumber}</div>
                            </div>
                            <div>
                                <div style="font-size: 11px; color: #8b949e; margin-bottom: 2px;">Date</div>
                                <div style="font-size: 13px; color: #c9d1d9;">${typeof date === 'string' ? date.split('T')[0] : date}</div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 11px; color: #8b949e; margin-bottom: 2px;">Total</div>
                                <div style="font-size: 14px; color: #c9d1d9; font-weight: 600;">$${total.toLocaleString()}</div>
                            </div>
                            <div>
                                <span style="
                                    padding: 4px 8px;
                                    border-radius: 4px;
                                    font-size: 11px;
                                    font-weight: 600;
                                    white-space: nowrap;
                                    ${isPaid ?
                    'background: rgba(63, 185, 80, 0.15); color: #3fb950;' :
                    status === 'AUTHORISED' ?
                        'background: rgba(31, 111, 235, 0.15); color: #1f6feb;' :
                        status === 'DRAFT' ?
                            'background: rgba(139, 148, 158, 0.15); color: #8b949e;' :
                            'background: rgba(210, 153, 34, 0.15); color: #d29922;'}
                                ">
                                    ${status}
                                </span>
                            </div>
                            <div style="text-align: right;">
                                ${!isPaid && amountDue > 0 ? `
                                    <div style="font-size: 11px; color: #8b949e; margin-bottom: 2px;">Due</div>
                                    <div style="font-size: 14px; color: #f0883e; font-weight: 600;">$${amountDue.toLocaleString()}</div>
                                ` : `
                                    <div style="font-size: 11px; color: #3fb950;">✓ Paid</div>
                                `}
                            </div>
                        </div>
                    `;
        }).join('')}
            </div>
        `;
    }

    buildInvoiceModalContent(invoice) {
        return `
            <div class="xero-modal-header" style="
                padding: 16px 20px;
                background: #161b22;
                border-bottom: 1px solid #30363d;
                display: flex;
                justify-content: space-between;
                align-items: center;
                cursor: grab;
            ">
                <h3 style="margin: 0; color: #c9d1d9; font-size: 18px; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-file-invoice" style="color: #58a6ff;"></i>
                    Invoice ${invoice.invoice_number || invoice.InvoiceNumber || 'N/A'}
                </h3>
                <button class="xero-modal-close" style="
                    background: none;
                    border: none;
                    color: #8b949e;
                    font-size: 24px;
                    cursor: pointer;
                    padding: 0;
                    width: 32px;
                    height: 32px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 4px;
                    transition: all 0.2s;
                " onmouseover="this.style.background='#21262d'; this.style.color='#c9d1d9'" onmouseout="this.style.background='none'; this.style.color='#8b949e'">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="xero-modal-body" style="
                padding: 20px;
                overflow-y: auto;
                max-height: calc(80vh - 70px);
            ">
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 20px;">
                    <div>
                        <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 4px;">Contact</div>
                        <div style="font-size: 14px; color: #c9d1d9; font-weight: 600;">${invoice.contact_name || invoice.Contact?.Name || 'N/A'}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 4px;">Date</div>
                        <div style="font-size: 14px; color: #c9d1d9;">${invoice.date || invoice.Date || 'N/A'}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 4px;">Status</div>
                        <div style="font-size: 14px;">
                            <span style="
                                padding: 4px 8px;
                                border-radius: 4px;
                                font-weight: 600;
                                ${invoice.status === 'PAID' || invoice.Status === 'PAID' ?
                'background: rgba(63, 185, 80, 0.15); color: #3fb950;' :
                invoice.status === 'AUTHORISED' || invoice.Status === 'AUTHORISED' ?
                    'background: rgba(210, 153, 34, 0.15); color: #d29922;' :
                    'background: rgba(139, 148, 158, 0.15); color: #8b949e;'
            }
                            ">
                                ${invoice.status || invoice.Status || 'N/A'}
                            </span>
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 4px;">Total</div>
                        <div style="font-size: 20px; color: #58a6ff; font-weight: 700;">$${(invoice.total || invoice.Total || 0).toFixed(2)}</div>
                    </div>
                </div>
                
                ${invoice.line_items || invoice.LineItems ? `
                    <div style="margin-top: 24px;">
                        <h4 style="margin: 0 0 12px 0; color: #c9d1d9; font-size: 14px; text-transform: uppercase;">Line Items</h4>
                        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; overflow: hidden;">
                            ${(invoice.line_items || invoice.LineItems || []).map(item => `
                                <div style="padding: 12px; border-bottom: 1px solid #30363d; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 12px; align-items: center;">
                                    <div>
                                        <div style="font-size: 13px; color: #c9d1d9; font-weight: 600;">${item.description || item.Description || 'N/A'}</div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="font-size: 11px; color: #8b949e;">Quantity</div>
                                        <div style="font-size: 13px; color: #c9d1d9;">${item.quantity || item.Quantity || 0}</div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="font-size: 11px; color: #8b949e;">Unit Price</div>
                                        <div style="font-size: 13px; color: #c9d1d9;">$${(item.unit_amount || item.UnitAmount || 0).toFixed(2)}</div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="font-size: 11px; color: #8b949e;">Total</div>
                                        <div style="font-size: 13px; color: #58a6ff; font-weight: 600;">$${(item.line_amount || item.LineAmount || 0).toFixed(2)}</div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    buildContactModalContent(contact) {
        return `
            <div class="xero-modal-header" style="
                padding: 16px 20px;
                background: #161b22;
                border-bottom: 1px solid #30363d;
                display: flex;
                justify-content: space-between;
                align-items: center;
                cursor: grab;
            ">
                <h3 style="margin: 0; color: #c9d1d9; font-size: 18px; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-user" style="color: #58a6ff;"></i>
                    ${contact.contact_name || contact.Name || 'Contact Details'}
                </h3>
                <button class="xero-modal-close" style="
                    background: none;
                    border: none;
                    color: #8b949e;
                    font-size: 24px;
                    cursor: pointer;
                    padding: 0;
                    width: 32px;
                    height: 32px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 4px;
                    transition: all 0.2s;
                " onmouseover="this.style.background='#21262d'; this.style.color='#c9d1d9'" onmouseout="this.style.background='none'; this.style.color='#8b949e'">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="xero-modal-body" style="
                padding: 20px;
                overflow-y: auto;
                max-height: calc(80vh - 70px);
            ">
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 20px;">
                    <div>
                        <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 4px;">Email</div>
                        <div style="font-size: 14px; color: #58a6ff;">${contact.email_address || contact.EmailAddress || 'N/A'}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 4px;">Phone</div>
                        <div style="font-size: 14px; color: #c9d1d9;">${contact.phone || contact.Phones?.[0]?.PhoneNumber || 'N/A'}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 4px;">Account Number</div>
                        <div style="font-size: 14px; color: #c9d1d9;">${contact.account_number || contact.AccountNumber || 'N/A'}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 4px;">Contact Status</div>
                        <div style="font-size: 14px;">
                            <span style="
                                padding: 4px 8px;
                                border-radius: 4px;
                                font-weight: 600;
                                ${contact.contact_status === 'ACTIVE' || contact.ContactStatus === 'ACTIVE' ?
                'background: rgba(63, 185, 80, 0.15); color: #3fb950;' :
                'background: rgba(139, 148, 158, 0.15); color: #8b949e;'
            }
                            ">
                                ${contact.contact_status || contact.ContactStatus || 'N/A'}
                            </span>
                        </div>
                    </div>
                </div>

                ${contact.addresses || contact.Addresses ? `
                    <div style="margin-top: 24px;">
                        <h4 style="margin: 0 0 12px 0; color: #c9d1d9; font-size: 14px; text-transform: uppercase;">Addresses</h4>
                        <div style="display: grid; gap: 12px;">
                            ${(contact.addresses || contact.Addresses || []).map(addr => `
                                <div style="padding: 12px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                                    <div style="font-size: 11px; color: #8b949e; margin-bottom: 8px; text-transform: uppercase;">${addr.AddressType || 'Address'}</div>
                                    <div style="font-size: 13px; color: #c9d1d9; line-height: 1.6;">
                                        ${addr.AddressLine1 ? `${addr.AddressLine1}<br>` : ''}
                                        ${addr.AddressLine2 ? `${addr.AddressLine2}<br>` : ''}
                                        ${addr.City ? `${addr.City}, ` : ''}${addr.Region || ''} ${addr.PostalCode || ''}<br>
                                        ${addr.Country || ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                ${contact.bank_account_details || contact.BankAccountDetails ? `
                    <div style="margin-top: 24px;">
                        <h4 style="margin: 0 0 12px 0; color: #c9d1d9; font-size: 14px; text-transform: uppercase;">Bank Account</h4>
                        <div style="padding: 12px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                            <div style="font-size: 13px; color: #c9d1d9;">
                                Account: ${contact.bank_account_details || contact.BankAccountDetails || 'N/A'}
                            </div>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    async renderCustomerDetailView(contactId) {
        const container = this.container.querySelector('#xero-main-content');

        if (!container) {
            console.error('[Xero] Main content container not found');
            return;
        }

        // Show loading state
        container.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 400px;">
                <div style="text-align: center;">
                    <i class="fas fa-spinner fa-spin" style="font-size: 48px; color: var(--xero-primary); margin-bottom: 16px;"></i>
                    <div style="color: #8b949e; font-size: 16px;">Loading customer details...</div>
                </div>
            </div>
        `;

        try {
            // Fetch comprehensive customer data
            const response = await fetch(
                `${this.API_BASE_URL}/api/xero/customer-details?contact_id=${contactId}&business_id=${this.currentBusiness}`
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to load customer details');
            }

            const customer = data.customer;

            // Render full customer detail view
            container.innerHTML = `
                <div class="xero-customer-detail-view" style="min-height: 100vh;">
                    <!-- Breadcrumb Navigation -->
                    <div class="xero-breadcrumb" style="
                        padding: 16px 24px;
                        background: #161b22;
                        border-bottom: 1px solid #30363d;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        margin-bottom: 0;
                    ">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <button id="xero-back-to-dashboard" style="
                                padding: 8px 16px;
                                background: #30363d;
                                border: none;
                                border-radius: 6px;
                                color: #c9d1d9;
                                cursor: pointer;
                                display: flex;
                                align-items: center;
                                gap: 8px;
                                font-size: 14px;
                                transition: all 0.2s;
                            ">
                                <i class="fas fa-arrow-left"></i> Back to Dashboard
                            </button>
                            <span style="color: #8b949e; font-size: 14px;">
                                ${this.previousView?.type === 'contacts' ? 'Contacts' : 'Invoice Risk Scoring'} > 
                                <strong style="color: #c9d1d9;">${customer.profile.name}</strong>
                            </span>
                        </div>
                        <div style="display: flex; gap: 12px;">
                            <button class="xero-btn" id="xero-export-customer-report" style="
                                padding: 8px 16px;
                                background: #238636;
                                border: none;
                                border-radius: 6px;
                                color: white;
                                cursor: pointer;
                                font-size: 14px;
                            ">
                                <i class="fas fa-file-pdf"></i> Export
                            </button>
                        </div>
                    </div>

                    <!-- Sticky Header with Key Metrics -->
                    <div class="xero-detail-header" style="
                        position: sticky;
                        top: 0;
                        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
                        border-bottom: 1px solid #30363d;
                        padding: 24px 32px;
                        z-index: 100;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h2 style="margin: 0; font-size: 28px; color: #c9d1d9; font-weight: 700;">
                                    <i class="fas fa-user-circle" style="color: var(--xero-primary); margin-right: 12px;"></i>
                                    ${customer.profile.name}
                                </h2>
                                <div style="margin-top: 12px; display: flex; gap: 12px; flex-wrap: wrap;">
                                    <span style="padding: 6px 14px; background: ${this.getRiskColor(customer.ml_insights.ml_churn_probability)}; border-radius: 14px; font-size: 13px; font-weight: 600; color: white;">
                                        Churn: ${customer.ml_insights.ml_churn_probability}% ${customer.ml_insights.ml_churn_probability >= 70 ? 'HIGH' : customer.ml_insights.ml_churn_probability >= 40 ? 'MEDIUM' : 'LOW'}
                                    </span>
                                    <span style="padding: 6px 14px; background: ${this.getRiskColor(customer.ml_insights.payment_risk_score)}; border-radius: 14px; font-size: 13px; font-weight: 600; color: white;">
                                        Payment Risk: ${customer.ml_insights.payment_risk_score}%
                                    </span>
                                    <span style="padding: 6px 14px; background: #3fb950; border-radius: 14px; font-size: 13px; font-weight: 600; color: white;">
                                        LTV: ${this.formatCurrency(customer.ml_insights.lifetime_revenue)}
                                    </span>
                                    <span style="padding: 6px 14px; background: ${this.getSegmentColor(customer.ml_insights.strategic_segment)}; border-radius: 14px; font-size: 13px; font-weight: 600; color: white;">
                                        ${customer.ml_insights.strategic_segment}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Tab Navigation (Sticky below header) -->
                    <div class="xero-detail-tabs" style="
                        position: sticky;
                        top: 120px;
                        background: #161b22;
                        border-bottom: 1px solid #30363d;
                        padding: 0 32px;
                        z-index: 99;
                        display: flex;
                        gap: 32px;
                    ">
                        <button class="xero-detail-tab active" data-tab="profile" style="
                            padding: 16px 8px;
                            background: transparent;
                            border: none;
                            border-bottom: 3px solid var(--xero-primary);
                            color: var(--xero-primary);
                            cursor: pointer;
                            font-size: 14px;
                            font-weight: 600;
                            transition: all 0.2s;
                        ">
                            📋 Profile
                        </button>
                        <button class="xero-detail-tab" data-tab="ml-insights" style="
                            padding: 16px 8px;
                            background: transparent;
                            border: none;
                            border-bottom: 3px solid transparent;
                            color: #8b949e;
                            cursor: pointer;
                            font-size: 14px;
                            font-weight: 600;
                            transition: all 0.2s;
                        ">
                            📊 ML Insights
                        </button>
                        <button class="xero-detail-tab" data-tab="financial" style="
                            padding: 16px 8px;
                            background: transparent;
                            border: none;
                            border-bottom: 3px solid transparent;
                            color: #8b949e;
                            cursor: pointer;
                            font-size: 14px;
                            font-weight: 600;
                            transition: all 0.2s;
                        ">
                            💰 Financial
                        </button>
                        <button class="xero-detail-tab" data-tab="history" style="
                            padding: 16px 8px;
                            background: transparent;
                            border: none;
                            border-bottom: 3px solid transparent;
                            color: #8b949e;
                            cursor: pointer;
                            font-size: 14px;
                            font-weight: 600;
                            transition: all 0.2s;
                        ">
                            📅 History
                        </button>
                        <button class="xero-detail-tab" data-tab="actions" style="
                            padding: 16px 8px;
                            background: transparent;
                            border: none;
                            border-bottom: 3px solid transparent;
                            color: #8b949e;
                            cursor: pointer;
                            font-size: 14px;
                            font-weight: 600;
                            transition: all 0.2s;
                        ">
                            🎯 Actions
                        </button>
                    </div>

                    <!-- Scrollable Content Area -->
                    <div class="xero-detail-body" style="padding: 32px; background: #0d1117;">
                        <!-- Profile Tab -->
                        <div id="tab-profile" class="xero-tab-content" style="display: block;">
                            ${this.renderCustomerProfile(customer.profile, customer.ml_insights)}
                        </div>
                        
                        <!-- ML Insights Tab -->
                        <div id="tab-ml-insights" class="xero-tab-content" style="display: none;">
                            ${this.renderMLInsights(customer.ml_insights)}
                        </div>
                        
                        <!-- Financial Tab -->
                        <div id="tab-financial" class="xero-tab-content" style="display: none;">
                            ${this.renderFinancialSummary(customer.financial_summary)}
                        </div>
                        
                        <!-- History Tab -->
                        <div id="tab-history" class="xero-tab-content" style="display: none;">
                            ${this.renderTransactionHistory(customer.invoices)}
                        </div>
                        
                        <!-- Actions Tab -->
                        <div id="tab-actions" class="xero-tab-content" style="display: none;">
                            ${this.renderRecommendedActions(customer)}
                        </div>
                    </div>
                </div>
            `;

            // Add event listeners
            this.initCustomerDetailNavigation();

        } catch (error) {
            console.error('[Xero] Error loading customer details:', error);
            container.innerHTML = `
                <div style="padding: 40px; text-align: center;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: #f85149; margin-bottom: 16px;"></i>
                    <h3 style="color: #c9d1d9; margin-bottom: 8px;">Failed to load customer details</h3>
                    <p style="color: #8b949e; margin-bottom: 24px;">${error.message}</p>
                    <button id="xero-retry-load" class="xero-btn" style="
                        padding: 10px 20px;
                        background: var(--xero-primary);
                        border: none;
                        border-radius: 6px;
                        color: white;
                        cursor: pointer;
                    ">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                </div>
            `;

            document.getElementById('xero-retry-load')?.addEventListener('click', () => {
                this.renderCustomerDetailView(contactId);
            });
        }
    }

    initCustomerDetailNavigation() {
        // Back button
        const backBtn = this.container.querySelector('#xero-back-to-dashboard');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.returnToPreviousView());
        }

        // Export button
        const exportBtn = this.container.querySelector('#xero-export-customer-report');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportCustomerReport());
        }

        // Tab switching
        const tabs = this.container.querySelectorAll('.xero-detail-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Update active states
                tabs.forEach(t => {
                    t.style.borderBottomColor = 'transparent';
                    t.style.color = '#8b949e';
                    t.classList.remove('active');
                });
                tab.style.borderBottomColor = 'var(--xero-primary)';
                tab.style.color = 'var(--xero-primary)';
                tab.classList.add('active');

                // Show corresponding content
                const tabName = tab.dataset.tab;
                this.container.querySelectorAll('.xero-tab-content').forEach(content => {
                    content.style.display = 'none';
                });
                this.container.querySelector(`#tab-${tabName}`).style.display = 'block';
            });
        });
    }

    returnToPreviousView() {
        console.log('[Xero] Returning to previous view:', this.previousView);

        if (this.previousView?.type === 'contacts') {
            this.renderContacts();
            this.loadContacts();
            // Restore scroll position after a short delay
            setTimeout(() => {
                window.scrollTo(0, this.previousView.scrollPosition || 0);
            }, 100);
        } else {
            // Return to invoice risk scoring or other dashboard
            this.renderInvoices();
            this.loadInvoices();
        }
    }

    getRiskColor(riskScore) {
        if (riskScore >= 70) return '#f85149';  // Red
        if (riskScore >= 40) return '#d29922';  // Yellow
        return '#3fb950';  // Green
    }

    getSegmentColor(segment) {
        const colors = {
            'VIP-Protect': '#3fb950',
            'VIP At-Risk': '#f85149',
            'High-Value Declining': '#d29922',
            'Rising Star': '#58a6ff',
            'Lost Cause': '#8b949e',
            'Stable Regular': '#7ee787',
            'Standard': '#6e7681'
        };
        return colors[segment] || '#6e7681';
    }

    renderCustomerProfile(profile, mlInsights) {
        return `
            <div style="max-width: 1000px;">
                <div style="
                    background: #161b22;
                    border: 1px solid #30363d;
                    border-radius: 8px;
                    padding: 24px;
                    margin-bottom: 24px;
                ">
                    <h3 style="margin: 0 0 20px 0; font-size: 18px; color: #c9d1d9; border-bottom: 1px solid #30363d; padding-bottom: 12px;">
                        <i class="fas fa-address-card" style="color: var(--xero-primary); margin-right: 8px;"></i>
                        Contact Information
                    </h3>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                        <div>
                            <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Name</div>
                            <div style="color: #c9d1d9; font-size: 16px; font-weight: 600;">${profile.name}</div>
                        </div>
                        <div>
                            <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Email</div>
                            <div style="color: #c9d1d9; font-size: 16px;">
                                ${profile.email ? `<a href="mailto:${profile.email}" style="color: var(--xero-primary); text-decoration: none;">${profile.email}</a>` : 'N/A'}
                            </div>
                        </div>
                        <div>
                            <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Phone</div>
                            <div style="color: #c9d1d9; font-size: 16px;">
                                ${profile.phone ? `<a href="tel:${profile.phone}" style="color: var(--xero-primary); text-decoration: none;">${profile.phone}</a>` : 'N/A'}
                            </div>
                        </div>
                        <div>
                            <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Customer Since</div>
                            <div style="color: #c9d1d9; font-size: 16px;">${profile.customer_since ? this.formatDate(new Date(profile.customer_since)) : 'N/A'}</div>
                        </div>
                        <div style="grid-column: 1 / -1;">
                            <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Address</div>
                            <div style="color: #c9d1d9; font-size: 16px;">${profile.address || 'N/A'}</div>
                        </div>
                        <div>
                            <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Payment Terms</div>
                            <div style="color: #c9d1d9; font-size: 16px;">${profile.payment_terms}</div>
                        </div>
                        <div>
                            <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Contact Type</div>
                            <div style="color: #c9d1d9; font-size: 16px;">
                                ${profile.is_customer ? '<span style="padding: 4px 10px; background: #238636; border-radius: 10px; font-size: 12px; margin-right: 8px;">Customer</span>' : ''}
                                ${profile.is_supplier ? '<span style="padding: 4px 10px; background: #1f6feb; border-radius: 10px; font-size: 12px;">Supplier</span>' : ''}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderMLInsights(mlInsights) {
        return `
            <div style="max-width: 1200px;">
                <!-- 4 Key Metrics Cards -->
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 32px;">
                    <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; text-align: center;">
                        <div style="font-size: 12px; color: #8b949e; margin-bottom: 12px; font-weight: 600; text-transform: uppercase;">Churn Risk</div>
                        <div style="font-size: 36px; font-weight: 700; color: ${this.getRiskColor(mlInsights.ml_churn_probability)}; margin-bottom: 8px;">
                            ${mlInsights.ml_churn_probability}%
                        </div>
                        <div style="font-size: 13px; color: #8b949e; font-weight: 600;">
                            ${mlInsights.ml_churn_probability >= 70 ? 'HIGH' : mlInsights.ml_churn_probability >= 40 ? 'MEDIUM' : 'LOW'}
                        </div>
                    </div>
                    <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; text-align: center;">
                        <div style="font-size: 12px; color: #8b949e; margin-bottom: 12px; font-weight: 600; text-transform: uppercase;">Payment Risk</div>
                        <div style="font-size: 36px; font-weight: 700; color: ${this.getRiskColor(mlInsights.payment_risk_score)}; margin-bottom: 8px;">
                            ${mlInsights.payment_risk_score}%
                        </div>
                        <div style="font-size: 13px; color: #8b949e; font-weight: 600;">
                            ${mlInsights.payment_risk_score >= 70 ? 'HIGH' : mlInsights.payment_risk_score >= 40 ? 'MEDIUM' : 'LOW'}
                        </div>
                    </div>
                    <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; text-align: center;">
                        <div style="font-size: 12px; color: #8b949e; margin-bottom: 12px; font-weight: 600; text-transform: uppercase;">Deviation</div>
                        <div style="font-size: 36px; font-weight: 700; color: ${mlInsights.deviation_score >= 2.5 ? '#f85149' : mlInsights.deviation_score >= 1.5 ? '#d29922' : '#3fb950'}; margin-bottom: 8px;">
                            ${mlInsights.deviation_score.toFixed(1)}σ
                        </div>
                        <div style="font-size: 13px; color: #8b949e; font-weight: 600;">
                            ${mlInsights.deviation_score >= 2.5 ? 'HIGH' : mlInsights.deviation_score >= 1.5 ? 'MEDIUM' : 'NORMAL'}
                        </div>
                    </div>
                    <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; text-align: center;">
                        <div style="font-size: 12px; color: #8b949e; margin-bottom: 12px; font-weight: 600; text-transform: uppercase;">LTV Value</div>
                        <div style="font-size: 36px; font-weight: 700; color: #3fb950; margin-bottom: 8px;">
                            ${this.formatCurrency(mlInsights.lifetime_revenue)}
                        </div>
                        <div style="font-size: 13px; color: #8b949e; font-weight: 600;">
                            Lifetime Revenue
                        </div>
                    </div>
                </div>

                <!-- Additional Insights -->
                <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px;">
                    <h3 style="margin: 0 0 20px 0; font-size: 18px; color: #c9d1d9; border-bottom: 1px solid #30363d; padding-bottom: 12px;">
                        <i class="fas fa-brain" style="color: var(--xero-primary); margin-right: 8px;"></i>
                        ML Analysis
                    </h3>
                    
                    <div style="margin-bottom: 20px;">
                        <strong style="color: #c9d1d9;">Strategic Segment:</strong>
                        <span style="margin-left: 12px; padding: 6px 14px; background: ${this.getSegmentColor(mlInsights.strategic_segment)}; border-radius: 14px; font-size: 13px; font-weight: 600; color: white;">
                            ${mlInsights.strategic_segment}
                        </span>
                    </div>
                    
                    <div style="margin-bottom: 20px; color: #8b949e; font-size: 14px;">
                        <strong style="color: #c9d1d9;">Behavior Trend:</strong>
                        ${mlInsights.behavior_trend === 'declining' ? '📉' : mlInsights.behavior_trend === 'improving' ? '📈' : '➡️'}
                        <span style="text-transform: capitalize; margin-left: 8px;">${mlInsights.behavior_trend}</span>
                    </div>
                    
                    <div style="margin-bottom: 24px; color: #8b949e; font-size: 14px;">
                        <strong style="color: #c9d1d9;">ML Confidence:</strong>
                        <span style="margin-left: 8px;">${mlInsights.ml_confidence_score}% (${mlInsights.ml_confidence_score >= 80 ? 'high' : mlInsights.ml_confidence_score >= 60 ? 'moderate' : 'low'} data quality)</span>
                    </div>
                    
                    ${mlInsights.root_causes && mlInsights.root_causes.length > 0 ? `
                        <div>
                            <strong style="color: #c9d1d9; display: block; margin-bottom: 12px;">Root Causes:</strong>
                            ${mlInsights.root_causes.map((cause, i) => `
                                <div style="margin-bottom: 12px; padding-left: 20px; color: #8b949e; font-size: 14px;">
                                    ${i + 1}. <strong style="color: #c9d1d9;">${cause.name}</strong>
                                    <div style="margin-top: 4px; color: #8b949e;">${cause.description}</div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    renderFinancialSummary(financial) {
        return `
            <div style="max-width: 1000px;">
                <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px;">
                    <h3 style="margin: 0 0 20px 0; font-size: 18px; color: #c9d1d9; border-bottom: 1px solid #30363d; padding-bottom: 12px;">
                        <i class="fas fa-chart-line" style="color: var(--xero-primary); margin-right: 8px;"></i>
                        Financial Overview
                    </h3>
                    
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px;">
                        <div>
                            <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Historical LTV</div>
                            <div style="color: #c9d1d9; font-size: 24px; font-weight: 700;">${this.formatCurrency(financial.historical_ltv)}</div>
                            <div style="color: #8b949e; font-size: 12px; margin-top: 2px;">Lifetime revenue to date</div>
                        </div>
                        
                        <div>
                            <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Predicted 12M LTV</div>
                            <div style="color: #c9d1d9; font-size: 24px; font-weight: 700;">${this.formatCurrency(financial.predicted_12m_ltv)}</div>
                            <div style="color: #8b949e; font-size: 12px; margin-top: 2px;">Forecasted future value</div>
                        </div>
                        
                        <div>
                            <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Churn-Adjusted LTV</div>
                            <div style="color: #c9d1d9; font-size: 24px; font-weight: 700;">${this.formatCurrency(financial.churn_adjusted_ltv)}</div>
                            <div style="color: #8b949e; font-size: 12px; margin-top: 2px;">Risk-weighted prediction</div>
                        </div>
                        
                        <div>
                            <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Total Expected LTV</div>
                            <div style="color: #3fb950; font-size: 24px; font-weight: 700;">${this.formatCurrency(financial.total_expected_ltv)}</div>
                            <div style="color: #8b949e; font-size: 12px; margin-top: 2px;">Historical + adjusted future</div>
                        </div>
                        
                        <div>
                            <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Avg Invoice Value</div>
                            <div style="color: #c9d1d9; font-size: 20px; font-weight: 600;">${this.formatCurrency(financial.avg_invoice_value)}</div>
                        </div>
                        
                        <div>
                            <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Avg Reorder Frequency</div>
                            <div style="color: #c9d1d9; font-size: 20px; font-weight: 600;">${financial.avg_reorder_frequency.toFixed(1)} days</div>
                        </div>
                        
                        <div>
                            <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Reorder Variance</div>
                            <div style="color: #c9d1d9; font-size: 20px; font-weight: 600;">${financial.reorder_variance.toFixed(1)} days</div>
                        </div>
                        
                        <div>
                            <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Current Outstanding</div>
                            <div style="color: ${financial.current_outstanding > 0 ? '#f85149' : '#3fb950'}; font-size: 20px; font-weight: 600;">${this.formatCurrency(financial.current_outstanding)}</div>
                        </div>
                        
                        ${financial.days_overdue > 0 ? `
                            <div>
                                <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Days Overdue</div>
                                <div style="color: #f85149; font-size: 20px; font-weight: 600;">${financial.days_overdue} days</div>
                            </div>
                            
                            <div>
                                <div style="color: #8b949e; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">Collection Risk</div>
                                <div style="color: ${this.getRiskColor(financial.collection_risk)}; font-size: 20px; font-weight: 600;">${financial.collection_risk.toFixed(1)}%</div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    renderTransactionHistory(invoices) {
        if (!invoices || invoices.length === 0) {
            return `<div style="text-align: center; padding: 40px; color: #8b949e;">No invoice history available</div>`;
        }

        return `
            <div style="max-width: 1200px;">
                <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; overflow: hidden;">
                    <h3 style="margin: 0; padding: 20px 24px; font-size: 18px; color: #c9d1d9; border-bottom: 1px solid #30363d;">
                        <i class="fas fa-file-invoice" style="color: var(--xero-primary); margin-right: 8px;"></i>
                        Invoice History (Last ${invoices.length} invoices)
                    </h3>
                    
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="background: #0d1117;">
                                    <th style="padding: 12px 16px; text-align: left; font-size: 12px; color: #8b949e; font-weight: 600; text-transform: uppercase;">Date</th>
                                    <th style="padding: 12px 16px; text-align: left; font-size: 12px; color: #8b949e; font-weight: 600; text-transform: uppercase;">Invoice #</th>
                                    <th style="padding: 12px 16px; text-align: right; font-size: 12px; color: #8b949e; font-weight: 600; text-transform: uppercase;">Amount</th>
                                    <th style="padding: 12px 16px; text-align: left; font-size: 12px; color: #8b949e; font-weight: 600; text-transform: uppercase;">Paid Date</th>
                                    <th style="padding: 12px 16px; text-align: center; font-size: 12px; color: #8b949e; font-weight: 600; text-transform: uppercase;">Days to Pay</th>
                                    <th style="padding: 12px 16px; text-align: center; font-size: 12px; color: #8b949e; font-weight: 600; text-transform: uppercase;">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${invoices.map((inv, index) => `
                                    <tr style="border-top: 1px solid #30363d; ${index % 2 === 0 ? 'background: #0d1117;' : ''}">
                                        <td style="padding: 12px 16px; color: #c9d1d9; font-size: 14px;">${inv.date ? this.formatDate(new Date(inv.date)) : 'N/A'}</td>
                                        <td style="padding: 12px 16px; color: var(--xero-primary); font-size: 14px; font-weight: 600;">${inv.invoice_number}</td>
                                        <td style="padding: 12px 16px; color: #c9d1d9; font-size: 14px; text-align: right; font-weight: 600;">${this.formatCurrency(inv.amount)}</td>
                                        <td style="padding: 12px 16px; color: #c9d1d9; font-size: 14px;">${inv.paid_date ? this.formatDate(new Date(inv.paid_date)) : inv.status === 'PAID' ? 'PAID' : '-'}</td>
                                        <td style="padding: 12px 16px; color: ${inv.days_to_pay > 45 ? '#f85149' : inv.days_to_pay > 30 ? '#d29922' : '#3fb950'}; font-size: 14px; text-align: center; font-weight: 600;">
                                            ${inv.days_to_pay ? inv.days_to_pay + 'd' : '-'}
                                        </td>
                                        <td style="padding: 12px 16px; text-align: center;">
                                            ${this.getStatusBadge(inv.status)}
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    }

    renderRecommendedActions(customer) {
        const scenarios = customer.scenarios || {};

        return `
            <div style="max-width: 1200px;">
                <!-- Best Action Card -->
                <div style="background: linear-gradient(135deg, #1f6feb 0%, #1a56db 100%); border: 1px solid #388bfd; border-radius: 8px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(31, 111, 235, 0.2);">
                    <h3 style="margin: 0 0 12px 0; font-size: 20px; color: white; font-weight: 700;">
                        <i class="fas fa-star" style="margin-right: 8px;"></i>
                        Recommended Action: ${customer.best_action === 'call' ? 'Executive Call' : customer.best_action === 'email' ? 'Email Reminder' : 'Payment Plan'}
                    </h3>
                    <p style="margin: 0 0 20px 0; color: rgba(255, 255, 255, 0.9); font-size: 14px; line-height: 1.5;">
                        ${customer.best_action_reason}
                    </p>
                    
                    <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 20px; padding: 16px; background: rgba(255, 255, 255, 0.1); border-radius: 6px;">
                        <i class="fas fa-calendar-check" style="font-size: 24px; color: white;"></i>
                        <div>
                            <div style="color: rgba(255, 255, 255, 0.9); font-size: 12px; margin-bottom: 4px;">Best Contact Time</div>
                            <div style="color: white; font-size: 16px; font-weight: 600;">${customer.best_contact_time}</div>
                            <div style="color: rgba(255, 255, 255, 0.8); font-size: 12px; margin-top: 2px;">Next window: ${customer.next_optimal_window}</div>
                        </div>
                    </div>
                    
                    <!-- Quick Action Buttons -->
                    <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                        <button class="xero-btn" style="padding: 12px 20px; background: white; color: #1f6feb; border: none; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer;">
                            <i class="fas fa-phone"></i> Make Call Now
                        </button>
                        <button class="xero-btn" style="padding: 12px 20px; background: rgba(255, 255, 255, 0.2); color: white; border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer;">
                            <i class="fas fa-envelope"></i> Send Email
                        </button>
                        <button class="xero-btn" style="padding: 12px 20px; background: rgba(255, 255, 255, 0.2); color: white; border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer;">
                            <i class="fas fa-percent"></i> Apply Discount
                        </button>
                        <button class="xero-btn" style="padding: 12px 20px; background: rgba(255, 255, 255, 0.2); color: white; border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer;">
                            <i class="fas fa-calendar-alt"></i> Payment Plan
                        </button>
                    </div>
                </div>

                <!-- Scenario Analysis -->
                <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px;">
                    <h3 style="margin: 0 0 20px 0; font-size: 18px; color: #c9d1d9; border-bottom: 1px solid #30363d; padding-bottom: 12px;">
                        <i class="fas fa-chart-line" style="color: var(--xero-primary); margin-right: 8px;"></i>
                        Scenario Analysis
                    </h3>
                    
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="background: #0d1117;">
                                    <th style="padding: 12px 16px; text-align: left; font-size: 12px; color: #8b949e; font-weight: 600; text-transform: uppercase;">Action</th>
                                    <th style="padding: 12px 16px; text-align: center; font-size: 12px; color: #8b949e; font-weight: 600; text-transform: uppercase;">Churn Reduction</th>
                                    <th style="padding: 12px 16px; text-align: right; font-size: 12px; color: #8b949e; font-weight: 600; text-transform: uppercase;">Expected Impact</th>
                                    <th style="padding: 12px 16px; text-align: center; font-size: 12px; color: #8b949e; font-weight: 600; text-transform: uppercase;">ROI</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${Object.entries(scenarios).map(([key, scenario]) => `
                                    <tr style="border-top: 1px solid #30363d;">
                                        <td style="padding: 12px 16px; color: #c9d1d9; font-size: 14px; font-weight: 600;">
                                            ${key === 'executive_call' ? '📞 Executive Call' :
                key === 'offer_discount' ? '💰 Offer 5% Discount' :
                    key === 'payment_plan' ? '📋 Payment Plan' :
                        '⚠️ No Action'}
                                        </td>
                                        <td style="padding: 12px 16px; text-align: center; font-size: 14px; font-weight: 600; color: ${scenario.churn_reduction > 0 ? '#3fb950' : '#f85149'};">
                                            ${scenario.churn_reduction > 0 ? '-' : '+'}${Math.abs(scenario.churn_reduction)}%
                                        </td>
                                        <td style="padding: 12px 16px; text-align: right; font-size: 14px; font-weight: 600; color: ${scenario.expected_ltv_increase > 0 ? '#3fb950' : '#f85149'};">
                                            ${scenario.expected_ltv_increase > 0 ? '+' : ''}${this.formatCurrency(scenario.expected_ltv_increase)}
                                        </td>
                                        <td style="padding: 12px 16px; text-align: center; font-size: 14px; font-weight: 600; color: ${scenario.roi > 0 ? '#3fb950' : scenario.roi < 0 ? '#f85149' : '#8b949e'};">
                                            ${scenario.roi > 0 ? scenario.roi + '%' : scenario.roi < 0 ? scenario.roi + '%' : 'N/A'}
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    }

    exportCustomerReport() {
        console.log('[Xero] Exporting customer report...');
        alert('Export functionality will be available in the next update.');
    }

    showInvoiceDetails(invoice) {
        console.log('Showing invoice details:', invoice);
        // TODO: Implement invoice details modal
    }

    showCreateInvoiceModal() {
        console.log('Opening create invoice modal');
        // TODO: Implement create invoice modal
    }

    showCreateContactModal() {
        console.log('Opening create contact modal');

        // Create modal HTML
        const modalHTML = `
            <style>
                /* Global input styling for Xero modal */
                .xero-input:focus {
                    border-color: var(--xero-primary, #13b9fd) !important;
                    box-shadow: 0 0 0 3px rgba(19, 185, 253, 0.1) !important;
                }
                
                /* Address input focus states */
                .address-input:focus {
                    border-color: var(--xero-primary, #13b9fd) !important;
                    box-shadow: 0 0 0 3px rgba(19, 185, 253, 0.1) !important;
                }
            </style>
            <div class="xero-modal-overlay" id="xero-contact-modal" style="
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                backdrop-filter: blur(4px);
            ">
                <div class="xero-modal-content" style="
                    background: var(--xero-bg-primary, #0d1117);
                    border: 1px solid var(--xero-border, #30363d);
                    border-radius: 12px;
                    width: 90%;
                    max-width: 650px;
                    max-height: 90vh;
                    overflow-y: auto;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
                ">
                    <!-- Modal Header -->
                    <div style="
                        padding: 24px 32px;
                        border-bottom: 1px solid var(--xero-border, #30363d);
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    ">
                        <div>
                            <h2 style="margin: 0; font-size: 24px; color: var(--xero-text, #c9d1d9);">
                                <i class="fas fa-user-plus" style="color: var(--xero-primary, #13b9fd); margin-right: 12px;"></i>
                                Create New Contact
                            </h2>
                            <p style="margin: 8px 0 0 0; font-size: 14px; color: var(--xero-text-secondary, #8b949e);">
                                Add a new customer or supplier to <span id="modal-business-name" style="color: var(--xero-primary);">Xero</span>
                            </p>
                        </div>
                        <button id="xero-close-modal" style="
                            background: transparent;
                            border: none;
                            color: var(--xero-text-secondary, #8b949e);
                            font-size: 24px;
                            cursor: pointer;
                            padding: 0;
                            width: 32px;
                            height: 32px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            border-radius: 6px;
                            transition: all 0.2s;
                        " onmouseover="this.style.background='var(--xero-bg-secondary)'; this.style.color='var(--xero-text)';"
                           onmouseout="this.style.background='transparent'; this.style.color='var(--xero-text-secondary)';">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>

                    <!-- Modal Body -->
                    <form id="xero-contact-form" style="padding: 32px;">
                        <!-- Contact Type -->
                        <div style="margin-bottom: 24px;">
                            <label style="display: block; margin-bottom: 8px; font-weight: 500; color: var(--xero-text);">
                                Contact Type <span style="color: #f85149;">*</span>
                            </label>
                            <div style="display: flex; gap: 12px;">
                                <label style="
                                    flex: 1;
                                    padding: 12px 16px;
                                    border: 2px solid var(--xero-border);
                                    border-radius: 8px;
                                    cursor: pointer;
                                    display: flex;
                                    align-items: center;
                                    gap: 8px;
                                    transition: all 0.2s;
                                " class="contact-type-option">
                                    <input type="checkbox" id="is-customer" name="is_customer" checked style="width: 18px; height: 18px; cursor: pointer;">
                                    <span style="color: var(--xero-text); font-size: 14px;">
                                        <i class="fas fa-shopping-cart"></i> Customer
                                    </span>
                                </label>
                                <label style="
                                    flex: 1;
                                    padding: 12px 16px;
                                    border: 2px solid var(--xero-border);
                                    border-radius: 8px;
                                    cursor: pointer;
                                    display: flex;
                                    align-items: center;
                                    gap: 8px;
                                    transition: all 0.2s;
                                " class="contact-type-option">
                                    <input type="checkbox" id="is-supplier" name="is_supplier" style="width: 18px; height: 18px; cursor: pointer;">
                                    <span style="color: var(--xero-text); font-size: 14px;">
                                        <i class="fas fa-truck"></i> Supplier
                                    </span>
                                </label>
                            </div>
                        </div>

                        <!-- Contact Name -->
                        <div style="margin-bottom: 24px;">
                            <label for="contact-name" style="display: block; margin-bottom: 8px; font-weight: 500; color: var(--xero-text);">
                                Contact Name <span style="color: #f85149;">*</span>
                            </label>
                            <input type="text" id="contact-name" required
                                placeholder="e.g., Acme Corporation"
                                class="xero-input"
                                style="
                                    width: 100%;
                                    padding: 12px 16px;
                                    background: var(--xero-bg-secondary, #161b22);
                                    border: 1.5px solid var(--xero-border, #30363d);
                                    border-radius: 8px;
                                    color: var(--xero-text, #c9d1d9);
                                    font-size: 14px;
                                    transition: all 0.2s ease;
                                    box-sizing: border-box;
                                    outline: none;
                                ">
                        </div>

                        <!-- First & Last Name (optional, for person contacts) -->
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px;">
                            <div>
                                <label for="first-name" style="display: block; margin-bottom: 8px; font-weight: 500; color: var(--xero-text);">
                                    First Name
                                </label>
                                <input type="text" id="first-name"
                                    placeholder="e.g., John"
                                    class="xero-input"
                                    style="
                                        width: 100%;
                                        padding: 12px 16px;
                                        background: var(--xero-bg-secondary);
                                        border: 1.5px solid var(--xero-border);
                                        border-radius: 8px;
                                        color: var(--xero-text);
                                        font-size: 14px;
                                        box-sizing: border-box;
                                        transition: all 0.2s ease;
                                        outline: none;
                                    ">
                            </div>
                            <div>
                                <label for="last-name" style="display: block; margin-bottom: 8px; font-weight: 500; color: var(--xero-text);">
                                    Last Name
                                </label>
                                <input type="text" id="last-name"
                                    placeholder="e.g., Smith"
                                    class="xero-input"
                                    style="
                                        width: 100%;
                                        padding: 12px 16px;
                                        background: var(--xero-bg-secondary);
                                        border: 1.5px solid var(--xero-border);
                                        border-radius: 8px;
                                        color: var(--xero-text);
                                        font-size: 14px;
                                        box-sizing: border-box;
                                        transition: all 0.2s ease;
                                        outline: none;
                                    ">
                            </div>
                        </div>

                        <!-- Email Address -->
                        <div style="margin-bottom: 24px;">
                            <label for="contact-email" style="display: block; margin-bottom: 8px; font-weight: 500; color: var(--xero-text);">
                                Email Address
                            </label>
                            <div style="position: relative;">
                                <i class="fas fa-envelope" style="
                                    position: absolute;
                                    left: 16px;
                                    top: 50%;
                                    transform: translateY(-50%);
                                    color: var(--xero-text-secondary);
                                    pointer-events: none;
                                    z-index: 1;
                                "></i>
                                <input type="email" id="contact-email"
                                    placeholder="contact@example.com"
                                    class="xero-input"
                                    style="
                                        width: 100%;
                                        padding: 12px 16px 12px 44px;
                                        background: var(--xero-bg-secondary);
                                        border: 1.5px solid var(--xero-border);
                                        border-radius: 8px;
                                        color: var(--xero-text);
                                        font-size: 14px;
                                        box-sizing: border-box;
                                        transition: all 0.2s ease;
                                        outline: none;
                                    ">
                            </div>
                        </div>

                        <!-- Phone Numbers -->
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px;">
                            <div>
                                <label for="contact-phone" style="display: block; margin-bottom: 8px; font-weight: 500; color: var(--xero-text);">
                                    Phone
                                </label>
                                <div style="position: relative;">
                                    <i class="fas fa-phone" style="
                                        position: absolute;
                                        left: 16px;
                                        top: 50%;
                                        transform: translateY(-50%);
                                        color: var(--xero-text-secondary);
                                        pointer-events: none;
                                        z-index: 1;
                                    "></i>
                                    <input type="tel" id="contact-phone"
                                        placeholder="(555) 123-4567"
                                        class="xero-input"
                                        style="
                                            width: 100%;
                                            padding: 12px 16px 12px 44px;
                                            background: var(--xero-bg-secondary);
                                            border: 1.5px solid var(--xero-border);
                                            border-radius: 8px;
                                            color: var(--xero-text);
                                            font-size: 14px;
                                            box-sizing: border-box;
                                            transition: all 0.2s ease;
                                            outline: none;
                                        ">
                                </div>
                            </div>
                            <div>
                                <label for="contact-mobile" style="display: block; margin-bottom: 8px; font-weight: 500; color: var(--xero-text);">
                                    Mobile
                                </label>
                                <div style="position: relative;">
                                    <i class="fas fa-mobile-alt" style="
                                        position: absolute;
                                        left: 16px;
                                        top: 50%;
                                        transform: translateY(-50%);
                                        color: var(--xero-text-secondary);
                                        pointer-events: none;
                                        z-index: 1;
                                    "></i>
                                    <input type="tel" id="contact-mobile"
                                        placeholder="(555) 987-6543"
                                        class="xero-input"
                                        style="
                                            width: 100%;
                                            padding: 12px 16px 12px 44px;
                                            background: var(--xero-bg-secondary);
                                            border: 1.5px solid var(--xero-border);
                                            border-radius: 8px;
                                            color: var(--xero-text);
                                            font-size: 14px;
                                            box-sizing: border-box;
                                            transition: all 0.2s ease;
                                            outline: none;
                                        ">
                                </div>
                            </div>
                        </div>

                        <!-- Contact Persons (for businesses only) -->
                        <div id="contact-persons-section" style="margin-bottom: 24px;">
                            <details style="border: 1px solid var(--xero-border); border-radius: 8px; padding: 16px;">
                                <summary style="
                                    cursor: pointer;
                                    font-weight: 500;
                                    color: var(--xero-text);
                                    list-style: none;
                                    display: flex;
                                    align-items: center;
                                    justify-content: space-between;
                                ">
                                    <div style="display: flex; align-items: center; gap: 8px;">
                                        <i class="fas fa-chevron-right" style="transition: transform 0.2s; font-size: 12px;"></i>
                                        <i class="fas fa-users" style="color: var(--xero-primary);"></i>
                                        Contact Persons (Optional)
                                    </div>
                                    <button type="button" id="add-contact-person" style="
                                        padding: 6px 12px;
                                        background: var(--xero-primary);
                                        border: none;
                                        border-radius: 6px;
                                        color: white;
                                        font-size: 12px;
                                        cursor: pointer;
                                        display: flex;
                                        align-items: center;
                                        gap: 6px;
                                    " onclick="event.stopPropagation();">
                                        <i class="fas fa-plus"></i> Add Person
                                    </button>
                                </summary>
                                <div id="contact-persons-list" style="margin-top: 16px; padding-left: 24px;"></div>
                            </details>
                        </div>

                        <!-- Addresses Section (Postal, Street, Delivery) -->
                        <details style="margin-bottom: 24px; border: 1px solid var(--xero-border); border-radius: 8px; padding: 16px;">
                            <summary style="
                                cursor: pointer;
                                font-weight: 500;
                                color: var(--xero-text);
                                list-style: none;
                                display: flex;
                                align-items: center;
                                gap: 8px;
                            ">
                                <i class="fas fa-chevron-right" style="transition: transform 0.2s; font-size: 12px;"></i>
                                <i class="fas fa-map-marker-alt" style="color: var(--xero-primary);"></i>
                                Addresses (Optional)
                            </summary>
                            <div style="margin-top: 16px; padding-left: 24px;">
                                <!-- Postal Address Tab -->
                                <div style="margin-bottom: 24px;">
                                    <div style="
                                        background: rgba(19, 185, 253, 0.05);
                                        border-left: 3px solid var(--xero-primary);
                                        padding: 12px 16px;
                                        margin-bottom: 12px;
                                        border-radius: 6px;
                                    ">
                                        <span style="font-weight: 600; color: var(--xero-primary); font-size: 13px;">
                                            <i class="fas fa-envelope"></i> Postal Address
                                        </span>
                                    </div>
                                    <div style="padding-left: 12px;">
                                        <input type="text" id="postal-line1" placeholder="Street Address" class="address-input" style="margin-bottom: 10px;">
                                        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 10px; margin-bottom: 10px;">
                                            <input type="text" id="postal-city" placeholder="City" class="address-input">
                                            <input type="text" id="postal-postal-code" placeholder="Postal Code" class="address-input">
                                        </div>
                                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                                            <input type="text" id="postal-region" placeholder="State/Region" class="address-input">
                                            <input type="text" id="postal-country" placeholder="Country" class="address-input">
                                        </div>
                                    </div>
                                </div>

                                <!-- Street Address Tab -->
                                <div style="margin-bottom: 24px;">
                                    <div style="
                                        background: rgba(19, 185, 253, 0.05);
                                        border-left: 3px solid var(--xero-primary);
                                        padding: 12px 16px;
                                        margin-bottom: 12px;
                                        border-radius: 6px;
                                    ">
                                        <span style="font-weight: 600; color: var(--xero-primary); font-size: 13px;">
                                            <i class="fas fa-road"></i> Street/Physical Address
                                        </span>
                                    </div>
                                    <div style="padding-left: 12px;">
                                        <input type="text" id="street-line1" placeholder="Street Address" class="address-input" style="margin-bottom: 10px;">
                                        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 10px; margin-bottom: 10px;">
                                            <input type="text" id="street-city" placeholder="City" class="address-input">
                                            <input type="text" id="street-postal-code" placeholder="Postal Code" class="address-input">
                                        </div>
                                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                                            <input type="text" id="street-region" placeholder="State/Region" class="address-input">
                                            <input type="text" id="street-country" placeholder="Country" class="address-input">
                                        </div>
                                    </div>
                                </div>

                                <!-- Delivery Address Tab -->
                                <div>
                                    <div style="
                                        background: rgba(19, 185, 253, 0.05);
                                        border-left: 3px solid var(--xero-primary);
                                        padding: 12px 16px;
                                        margin-bottom: 12px;
                                        border-radius: 6px;
                                    ">
                                        <span style="font-weight: 600; color: var(--xero-primary); font-size: 13px;">
                                            <i class="fas fa-truck"></i> Delivery Address
                                        </span>
                                    </div>
                                    <div style="padding-left: 12px;">
                                        <input type="text" id="delivery-line1" placeholder="Street Address" class="address-input" style="margin-bottom: 10px;">
                                        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 10px; margin-bottom: 10px;">
                                            <input type="text" id="delivery-city" placeholder="City" class="address-input">
                                            <input type="text" id="delivery-postal-code" placeholder="Postal Code" class="address-input">
                                        </div>
                                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                                            <input type="text" id="delivery-region" placeholder="State/Region" class="address-input">
                                            <input type="text" id="delivery-country" placeholder="Country" class="address-input">
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <style>
                                .address-input {
                                    width: 100%;
                                    padding: 10px 14px;
                                    background: var(--xero-bg-secondary);
                                    border: 1.5px solid var(--xero-border);
                                    border-radius: 6px;
                                    color: var(--xero-text);
                                    font-size: 13px;
                                    box-sizing: border-box;
                                    transition: all 0.2s ease;
                                    outline: none;
                                }
                                .address-input:focus {
                                    border-color: var(--xero-primary, #13b9fd);
                                    box-shadow: 0 0 0 3px rgba(19, 185, 253, 0.1);
                                }
                            </style>
                        </details>

                        <!-- Additional Details (expandable) -->
                        <details style="margin-bottom: 24px; border: 1px solid var(--xero-border); border-radius: 8px; padding: 16px;">
                            <summary style="
                                cursor: pointer;
                                font-weight: 500;
                                color: var(--xero-text);
                                list-style: none;
                                display: flex;
                                align-items: center;
                                gap: 8px;
                            ">
                                <i class="fas fa-chevron-right" style="transition: transform 0.2s; font-size: 12px;"></i>
                                <i class="fas fa-info-circle" style="color: var(--xero-primary);"></i>
                                Additional Details (Optional)
                            </summary>
                            <div style="margin-top: 16px; padding-left: 24px;">
                                <div style="margin-bottom: 16px;">
                                    <label for="tax-number" style="display: block; margin-bottom: 8px; font-size: 13px; color: var(--xero-text-secondary);">
                                        Tax Number / ABN
                                    </label>
                                    <input type="text" id="tax-number"
                                        placeholder="e.g., 12-3456789 or 12 345 678 901"
                                        class="xero-input"
                                        style="
                                            width: 100%;
                                            padding: 10px 14px;
                                            background: var(--xero-bg-secondary);
                                            border: 1.5px solid var(--xero-border);
                                            border-radius: 6px;
                                            color: var(--xero-text);
                                            font-size: 13px;
                                            box-sizing: border-box;
                                            transition: all 0.2s ease;
                                            outline: none;
                                        ">
                                </div>
                                <div style="margin-bottom: 16px;">
                                    <label for="website" style="display: block; margin-bottom: 8px; font-size: 13px; color: var(--xero-text-secondary);">
                                        Website
                                    </label>
                                    <input type="url" id="website"
                                        placeholder="https://example.com"
                                        class="xero-input"
                                        style="
                                            width: 100%;
                                            padding: 10px 14px;
                                            background: var(--xero-bg-secondary);
                                            border: 1.5px solid var(--xero-border);
                                            border-radius: 6px;
                                            color: var(--xero-text);
                                            font-size: 13px;
                                            box-sizing: border-box;
                                            transition: all 0.2s ease;
                                            outline: none;
                                        ">
                                </div>
                                <div>
                                    <label for="account-number" style="display: block; margin-bottom: 8px; font-size: 13px; color: var(--xero-text-secondary);">
                                        Account Number
                                    </label>
                                    <input type="text" id="account-number"
                                        placeholder="Custom account reference"
                                        class="xero-input"
                                        style="
                                            width: 100%;
                                            padding: 10px 14px;
                                            background: var(--xero-bg-secondary);
                                            border: 1.5px solid var(--xero-border);
                                            border-radius: 6px;
                                            color: var(--xero-text);
                                            font-size: 13px;
                                            box-sizing: border-box;
                                            transition: all 0.2s ease;
                                            outline: none;
                                        ">
                                </div>
                            </div>
                        </details>

                        <!-- Status Message -->
                        <div id="contact-status" style="
                            margin-bottom: 24px;
                            padding: 12px 16px;
                            border-radius: 8px;
                            display: none;
                        "></div>

                        <!-- Action Buttons -->
                        <div style="display: flex; gap: 12px; justify-content: flex-end;">
                            <button type="button" id="xero-cancel-btn" style="
                                padding: 12px 24px;
                                background: transparent;
                                border: 1px solid var(--xero-border);
                                border-radius: 8px;
                                color: var(--xero-text);
                                font-size: 14px;
                                font-weight: 500;
                                cursor: pointer;
                                transition: all 0.2s;
                            " onmouseover="this.style.background='var(--xero-bg-secondary)';"
                               onmouseout="this.style.background='transparent';">
                                Cancel
                            </button>
                            <button type="submit" id="xero-submit-btn" style="
                                padding: 12px 32px;
                                background: var(--xero-primary, #13b9fd);
                                border: none;
                                border-radius: 8px;
                                color: white;
                                font-size: 14px;
                                font-weight: 500;
                                cursor: pointer;
                                transition: all 0.2s;
                                display: flex;
                                align-items: center;
                                gap: 8px;
                            " onmouseover="this.style.background='#0ea5e9';"
                               onmouseout="this.style.background='var(--xero-primary)';">
                                <i class="fas fa-plus-circle"></i>
                                Create Contact
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        // Insert modal into DOM
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Get business name - use hardcoded mapping
        const businessNames = {
            1: 'InHouse Print',
            2: 'InHouse Publishing',
            3: 'InHouse Signs'
        };
        const businessNameSpan = document.getElementById('modal-business-name');
        if (businessNameSpan) {
            businessNameSpan.textContent = businessNames[this.currentBusiness] || 'Xero';
        }

        // Setup event listeners
        const modal = document.getElementById('xero-contact-modal');
        const closeBtn = document.getElementById('xero-close-modal');
        const cancelBtn = document.getElementById('xero-cancel-btn');
        const form = document.getElementById('xero-contact-form');

        // Close modal handlers
        const closeModal = () => {
            if (modal && modal.parentNode) {
                modal.remove();
            }
        };

        if (closeBtn) {
            closeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                closeModal();
            });
        }

        if (cancelBtn) {
            cancelBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                closeModal();
            });
        }

        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    closeModal();
                }
            });
        }

        // Handle details expand/collapse animation
        document.querySelectorAll('details').forEach(details => {
            details.addEventListener('toggle', (e) => {
                const icon = e.target.querySelector('.fa-chevron-right');
                if (icon) {
                    icon.style.transform = details.open ? 'rotate(90deg)' : 'rotate(0deg)';
                }
            });
        });

        // Contact person management
        let contactPersonCounter = 0;
        const addContactPersonBtn = document.getElementById('add-contact-person');
        const contactPersonsList = document.getElementById('contact-persons-list');

        addContactPersonBtn.addEventListener('click', () => {
            contactPersonCounter++;
            const personId = `contact-person-${contactPersonCounter}`;

            const personHTML = `
                <div id="${personId}" style="
                    margin-bottom: 16px;
                    padding: 16px;
                    background: var(--xero-bg-secondary);
                    border: 1px solid var(--xero-border);
                    border-radius: 8px;
                    position: relative;
                ">
                    <button type="button" class="remove-person" data-person-id="${personId}" style="
                        position: absolute;
                        top: 12px;
                        right: 12px;
                        background: transparent;
                        border: none;
                        color: #f85149;
                        cursor: pointer;
                        font-size: 16px;
                        padding: 4px 8px;
                        border-radius: 4px;
                    " onmouseover="this.style.background='rgba(248,81,73,0.1)';"
                       onmouseout="this.style.background='transparent';">
                        <i class="fas fa-times"></i>
                    </button>
                    
                    <div style="margin-bottom: 12px; font-weight: 500; color: var(--xero-primary); font-size: 13px;">
                        <i class="fas fa-user"></i> Contact Person #${contactPersonCounter}
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
                        <input type="text" class="person-first-name" placeholder="First Name" style="
                            width: 100%;
                            padding: 8px 12px;
                            background: var(--xero-bg-primary);
                            border: 1px solid var(--xero-border);
                            border-radius: 6px;
                            color: var(--xero-text);
                            font-size: 13px;
                            box-sizing: border-box;
                        ">
                        <input type="text" class="person-last-name" placeholder="Last Name" style="
                            width: 100%;
                            padding: 8px 12px;
                            background: var(--xero-bg-primary);
                            border: 1px solid var(--xero-border);
                            border-radius: 6px;
                            color: var(--xero-text);
                            font-size: 13px;
                            box-sizing: border-box;
                        ">
                    </div>
                    
                    <div style="margin-bottom: 12px;">
                        <input type="email" class="person-email" placeholder="Email Address" style="
                            width: 100%;
                            padding: 8px 12px;
                            background: var(--xero-bg-primary);
                            border: 1px solid var(--xero-border);
                            border-radius: 6px;
                            color: var(--xero-text);
                            font-size: 13px;
                            box-sizing: border-box;
                        ">
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <input type="tel" class="person-phone" placeholder="Phone" style="
                            width: 100%;
                            padding: 8px 12px;
                            background: var(--xero-bg-primary);
                            border: 1px solid var(--xero-border);
                            border-radius: 6px;
                            color: var(--xero-text);
                            font-size: 13px;
                            box-sizing: border-box;
                        ">
                        <input type="tel" class="person-mobile" placeholder="Mobile" style="
                            width: 100%;
                            padding: 8px 12px;
                            background: var(--xero-bg-primary);
                            border: 1px solid var(--xero-border);
                            border-radius: 6px;
                            color: var(--xero-text);
                            font-size: 13px;
                            box-sizing: border-box;
                        ">
                    </div>
                    
                    <label style="
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        margin-top: 12px;
                        font-size: 13px;
                        color: var(--xero-text-secondary);
                        cursor: pointer;
                    ">
                        <input type="checkbox" class="person-include-emails" checked style="width: 16px; height: 16px;">
                        Include in emails
                    </label>
                </div>
            `;

            contactPersonsList.insertAdjacentHTML('beforeend', personHTML);
        });

        // Remove contact person handler (event delegation)
        contactPersonsList.addEventListener('click', (e) => {
            const removeBtn = e.target.closest('.remove-person');
            if (removeBtn) {
                const personId = removeBtn.dataset.personId;
                document.getElementById(personId)?.remove();
            }
        });

        // Form submission
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.submitCreateContact(form, closeModal);
        });
    }

    async submitCreateContact(form, closeModal) {
        const submitBtn = document.getElementById('xero-submit-btn');
        const statusDiv = document.getElementById('contact-status');

        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';

        // Collect contact persons
        const contactPersons = [];
        document.querySelectorAll('#contact-persons-list > div').forEach(personDiv => {
            const firstName = personDiv.querySelector('.person-first-name')?.value.trim();
            const lastName = personDiv.querySelector('.person-last-name')?.value.trim();
            const email = personDiv.querySelector('.person-email')?.value.trim();
            const phone = personDiv.querySelector('.person-phone')?.value.trim();
            const mobile = personDiv.querySelector('.person-mobile')?.value.trim();
            const includeEmails = personDiv.querySelector('.person-include-emails')?.checked;

            if (firstName || lastName || email) {
                contactPersons.push({
                    first_name: firstName,
                    last_name: lastName,
                    email: email,
                    phone: phone,
                    mobile: mobile,
                    include_in_emails: includeEmails
                });
            }
        });

        // Collect addresses
        const addresses = [];

        // Postal address
        const postalLine1 = document.getElementById('postal-line1')?.value.trim();
        if (postalLine1) {
            addresses.push({
                type: 'POBOX',
                line1: postalLine1,
                city: document.getElementById('postal-city')?.value.trim(),
                postal_code: document.getElementById('postal-postal-code')?.value.trim(),
                region: document.getElementById('postal-region')?.value.trim(),
                country: document.getElementById('postal-country')?.value.trim()
            });
        }

        // Street address
        const streetLine1 = document.getElementById('street-line1')?.value.trim();
        if (streetLine1) {
            addresses.push({
                type: 'STREET',
                line1: streetLine1,
                city: document.getElementById('street-city')?.value.trim(),
                postal_code: document.getElementById('street-postal-code')?.value.trim(),
                region: document.getElementById('street-region')?.value.trim(),
                country: document.getElementById('street-country')?.value.trim()
            });
        }

        // Delivery address
        const deliveryLine1 = document.getElementById('delivery-line1')?.value.trim();
        if (deliveryLine1) {
            addresses.push({
                type: 'DELIVERY',
                line1: deliveryLine1,
                city: document.getElementById('delivery-city')?.value.trim(),
                postal_code: document.getElementById('delivery-postal-code')?.value.trim(),
                region: document.getElementById('delivery-region')?.value.trim(),
                country: document.getElementById('delivery-country')?.value.trim()
            });
        }

        // Build contact data
        const contactData = {
            business_id: this.currentBusiness,
            name: document.getElementById('contact-name').value.trim(),
            first_name: document.getElementById('first-name')?.value.trim(),
            last_name: document.getElementById('last-name')?.value.trim(),
            email: document.getElementById('contact-email')?.value.trim(),
            phone: document.getElementById('contact-phone')?.value.trim(),
            mobile: document.getElementById('contact-mobile')?.value.trim(),
            is_customer: document.getElementById('is-customer')?.checked,
            is_supplier: document.getElementById('is-supplier')?.checked,
            contact_persons: contactPersons,
            addresses: addresses,
            tax_number: document.getElementById('tax-number')?.value.trim(),
            website: document.getElementById('website')?.value.trim(),
            account_number: document.getElementById('account-number')?.value.trim()
        };

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/contacts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(contactData)
            });

            const result = await response.json();

            if (result.success) {
                // Show success message
                statusDiv.style.display = 'block';
                statusDiv.style.background = 'rgba(46, 160, 67, 0.1)';
                statusDiv.style.border = '1px solid #2ea043';
                statusDiv.style.color = '#2ea043';
                statusDiv.innerHTML = `
                    <i class="fas fa-check-circle"></i>
                    Contact "${result.contact.name}" created successfully!
                `;

                // Refresh contacts table
                setTimeout(() => {
                    this.loadContacts();
                    closeModal();
                }, 1500);
            } else {
                throw new Error(result.error || 'Failed to create contact');
            }
        } catch (error) {
            console.error('Error creating contact:', error);

            // Show error message
            statusDiv.style.display = 'block';
            statusDiv.style.background = 'rgba(248, 81, 73, 0.1)';
            statusDiv.style.border = '1px solid #f85149';
            statusDiv.style.color = '#f85149';
            statusDiv.innerHTML = `
                <i class="fas fa-exclamation-circle"></i>
                Error: ${error.message}
            `;

            // Re-enable submit button
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-plus-circle"></i> Create Contact';
        }
    }

    filterInvoices(searchTerm) {
        if (this.tables.invoices) {
            this.tables.invoices.setFilter([
                { field: 'invoice_number', type: 'like', value: searchTerm },
                { field: 'contact_name', type: 'like', value: searchTerm }
            ]);
        }
    }

    filterInvoicesByStatus(status) {
        if (this.tables.invoices) {
            if (status) {
                this.tables.invoices.setFilter('status', '=', status);
            } else {
                this.tables.invoices.clearFilter();
            }
        }
    }

    filterContacts(searchTerm) {
        if (this.tables.contacts) {
            this.tables.contacts.setFilter([
                { field: 'name', type: 'like', value: searchTerm },
                { field: 'email', type: 'like', value: searchTerm }
            ]);
        }
    }

    filterPayments(searchTerm) {
        if (this.tables.payments) {
            this.tables.payments.setFilter('invoice_number', 'like', searchTerm);
        }
    }

    filterAccounts(searchTerm) {
        if (this.tables.accounts) {
            this.tables.accounts.setFilter([
                { field: 'code', type: 'like', value: searchTerm },
                { field: 'name', type: 'like', value: searchTerm }
            ]);
        }
    }

    // ========================================================================
    // BULK ACTIONS
    // ========================================================================

    updateSelectionCount(type, count) {
        const countElement = document.getElementById(`xero-${type}-selection-count`);
        const bulkActionsBar = document.getElementById(`xero-${type}-bulk-actions`);

        if (countElement) {
            countElement.textContent = `${count} selected`;
        }

        if (bulkActionsBar) {
            bulkActionsBar.style.display = count > 0 ? 'flex' : 'none';
        }
    }

    exportInvoices(format) {
        if (!this.tables.invoices) return;

        const filename = `xero_invoices_${Date.now()}`;

        try {
            switch (format) {
                case 'xlsx':
                    this.tables.invoices.download('xlsx', `${filename}.xlsx`, {
                        sheetName: 'Invoices'
                    });
                    break;
                case 'csv':
                    this.tables.invoices.download('csv', `${filename}.csv`);
                    break;
                case 'pdf':
                    this.tables.invoices.download('pdf', `${filename}.pdf`, {
                        orientation: 'landscape',
                        title: 'Xero Invoices'
                    });
                    break;
            }
            console.log(`Exported ${this.selectedItems.invoices.size} invoices as ${format}`);
        } catch (error) {
            console.error('Export failed:', error);
            this.showError('Export failed', error.message, 'error');
        }
    }

    exportContacts(format) {
        if (!this.tables.contacts) return;

        const filename = `xero_contacts_${Date.now()}`;

        try {
            switch (format) {
                case 'xlsx':
                    this.tables.contacts.download('xlsx', `${filename}.xlsx`, {
                        sheetName: 'Contacts'
                    });
                    break;
                case 'csv':
                    this.tables.contacts.download('csv', `${filename}.csv`);
                    break;
                case 'pdf':
                    this.tables.contacts.download('pdf', `${filename}.pdf`, {
                        orientation: 'landscape',
                        title: 'Xero Contacts'
                    });
                    break;
            }
            console.log(`Exported ${this.selectedItems.contacts.size} contacts as ${format}`);
        } catch (error) {
            console.error('Export failed:', error);
            this.showError('Export failed', error.message, 'error');
        }
    }

    deleteSelectedInvoices() {
        const count = this.selectedItems.invoices.size;
        if (count === 0) return;

        if (confirm(`Are you sure you want to delete ${count} invoice(s)?`)) {
            console.log('Deleting invoices:', Array.from(this.selectedItems.invoices));
            // TODO: Implement actual delete API call
            this.showWarning(`Delete functionality will be implemented in next update. Would delete ${count} invoices.`);
        }
    }

    deleteSelectedContacts() {
        const count = this.selectedItems.contacts.size;
        if (count === 0) return;

        if (confirm(`Are you sure you want to delete ${count} contact(s)?`)) {
            console.log('Deleting contacts:', Array.from(this.selectedItems.contacts));
            // TODO: Implement actual delete API call
            this.showWarning(`Delete functionality will be implemented in next update. Would delete ${count} contacts.`);
        }
    }

    // Base module required methods
    onRefresh() {
        const activeTab = this.activeSubTab || 'dashboard';
        const tabConfig = this.subTabs.get(activeTab);
        if (tabConfig && tabConfig.load) {
            tabConfig.load();
        }
    }

    onSettings() {
        console.log('Opening Xero settings...');
        // TODO: Implement settings modal
    }

    // ========================================================================
    // REPORTS METHODS
    // ========================================================================

    async showInvoiceIntelligence() {
        const resultsDiv = document.querySelector('#xero-invoices-report-results');
        if (!resultsDiv) return;

        resultsDiv.innerHTML = '<div style="padding: 40px; text-align: center; color: #8b949e;"><i class="fas fa-spinner fa-spin" style="font-size: 32px;"></i><br><br>Loading Invoice Intelligence Dashboard...</div>';

        try {
            // Fetch all necessary data in parallel
            const [agedReceivablesRes, salesSummaryRes, revenueTrendsRes, invoiceStatusRes] = await Promise.all([
                fetch(`${this.API_BASE_URL}/api/xero/reports/aged-receivables?business_id=${this.currentBusiness}`),
                fetch(`${this.API_BASE_URL}/api/xero/reports/sales-summary?business_id=${this.currentBusiness}&from_date=${this.getDateRangeStart(12)}`),
                fetch(`${this.API_BASE_URL}/api/xero/reports/revenue-trends?business_id=${this.currentBusiness}&from_date=${this.getDateRangeStart(12)}`),
                fetch(`${this.API_BASE_URL}/api/xero/reports/invoice-status?business_id=${this.currentBusiness}`)
            ]);

            const [agedData, salesData, trendsData, statusData] = await Promise.all([
                agedReceivablesRes.json(),
                salesSummaryRes.json(),
                revenueTrendsRes.json(),
                invoiceStatusRes.json()
            ]);

            if (!agedData.success || !salesData.success || !trendsData.success || !statusData.success) {
                throw new Error('Failed to load dashboard data');
            }

            // Calculate additional metrics
            const invoices = this.data.invoices || [];
            const paidInvoices = invoices.filter(inv => inv.status === 'PAID');
            const overdueInvoices = invoices.filter(inv => {
                const dueDate = this.parseXeroDate(inv.due_date);
                return dueDate && dueDate < new Date() && inv.status !== 'PAID';
            });

            const totalRevenue = invoices.reduce((sum, inv) => sum + (inv.total || 0), 0);
            const totalOutstanding = invoices.filter(i => i.status !== 'PAID').reduce((sum, inv) => sum + (inv.amount_due || 0), 0);
            const overdueAmount = overdueInvoices.reduce((sum, inv) => sum + (inv.amount_due || 0), 0);
            const avgInvoiceValue = invoices.length > 0 ? totalRevenue / invoices.length : 0;

            // Calculate average days to pay
            const avgDaysToPay = paidInvoices.length > 0
                ? paidInvoices.reduce((sum, inv) => {
                    const issued = this.parseXeroDate(inv.date);
                    const paid = this.parseXeroDate(inv.fully_paid_on_date || inv.date);
                    return sum + Math.floor((paid - issued) / (1000 * 60 * 60 * 24));
                }, 0) / paidInvoices.length
                : 0;

            const collectionRate = totalRevenue > 0 ? ((totalRevenue - totalOutstanding) / totalRevenue * 100) : 0;

            // Get current month invoices
            const currentMonth = new Date().getMonth();
            const currentYear = new Date().getFullYear();
            const thisMonthInvoices = invoices.filter(inv => {
                const date = this.parseXeroDate(inv.date);
                return date && date.getMonth() === currentMonth && date.getFullYear() === currentYear;
            }).length;

            // Payment velocity (avg days between invoices)
            const paymentVelocity = invoices.length > 1
                ? invoices.reduce((sum, inv, idx) => {
                    if (idx === 0) return 0;
                    const prev = this.parseXeroDate(invoices[idx - 1].date);
                    const curr = this.parseXeroDate(inv.date);
                    return sum + Math.floor((curr - prev) / (1000 * 60 * 60 * 24));
                }, 0) / (invoices.length - 1)
                : 0;

            // Build comprehensive dashboard HTML
            const html = `
                <div style="padding: 20px; background: #0d1117; border-radius: 8px;">
                    <!-- Header -->
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                        <h3 style="margin: 0; color: #c9d1d9; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-chart-line" style="color: #1f6feb;"></i>
                            Invoice Intelligence Dashboard
                        </h3>
                        <div style="display: flex; gap: 8px;">
                            <button id="ai-export-invoice-intelligence" class="xero-btn xero-btn-sm" style="padding: 8px 16px; background: #1f6feb; border: 1px solid #1f6feb;">
                                <i class="fas fa-robot"></i> AI Export
                            </button>
                            <button id="export-invoice-intelligence-csv" class="xero-btn xero-btn-sm" style="padding: 8px 16px; background: #238636; border: 1px solid #238636;">
                                <i class="fas fa-download"></i> Export CSV
                            </button>
                            <button id="refresh-invoice-intelligence" class="xero-btn xero-btn-sm" style="padding: 8px 16px;">
                                <i class="fas fa-sync"></i> Refresh
                            </button>
                        </div>
                    </div>

                    <!-- Key Metrics Grid (8 cards) -->
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;">
                        <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; border-left: 3px solid #3fb950;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Total Revenue</div>
                            <div style="font-size: 28px; color: #3fb950; font-weight: 700;">$${(totalRevenue / 1000).toFixed(1)}K</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">${invoices.length} invoices</div>
                        </div>
                        <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; border-left: 3px solid #f0883e;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Outstanding</div>
                            <div style="font-size: 28px; color: #f0883e; font-weight: 700;">$${(totalOutstanding / 1000).toFixed(1)}K</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">${invoices.filter(i => i.status !== 'PAID').length} unpaid</div>
                        </div>
                        <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; border-left: 3px solid #f85149;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Overdue Amount</div>
                            <div style="font-size: 28px; color: #f85149; font-weight: 700;">$${(overdueAmount / 1000).toFixed(1)}K</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">${overdueInvoices.length} overdue</div>
                        </div>
                        <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; border-left: 3px solid #1f6feb;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Collection Rate</div>
                            <div style="font-size: 28px; color: #1f6feb; font-weight: 700;">${collectionRate.toFixed(1)}%</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Last 12 months</div>
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px;">
                        <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Avg Invoice Value</div>
                            <div style="font-size: 28px; color: #c9d1d9; font-weight: 700;">$${(avgInvoiceValue / 1000).toFixed(1)}K</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Per invoice</div>
                        </div>
                        <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Avg Days to Pay</div>
                            <div style="font-size: 28px; color: #c9d1d9; font-weight: 700;">${Math.round(avgDaysToPay)}d</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Payment cycle</div>
                        </div>
                        <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">This Month</div>
                            <div style="font-size: 28px; color: #c9d1d9; font-weight: 700;">${thisMonthInvoices}</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Invoices issued</div>
                        </div>
                        <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Payment Velocity</div>
                            <div style="font-size: 28px; color: #c9d1d9; font-weight: 700;">${Math.round(paymentVelocity)}d</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Between invoices</div>
                        </div>
                    </div>

                    <!-- Aged Receivables Visual -->
                    <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 24px;">
                        <h4 style="margin: 0 0 16px 0; color: #c9d1d9; font-size: 14px;">Aged Receivables Breakdown</h4>
                        <div style="display: flex; height: 40px; border-radius: 4px; overflow: hidden; margin-bottom: 12px;">
                            ${Object.entries(agedData.buckets).map(([key, bucket]) => {
                const percentage = agedData.total_outstanding > 0 ? (bucket.amount / agedData.total_outstanding * 100) : 0;
                const colors = { 'Current': '#3fb950', '1-30': '#58a6ff', '31-60': '#f0c14e', '61-90': '#f0883e', '90+': '#f85149' };
                const color = colors[key] || '#8b949e';
                return percentage > 0 ? `
                                    <div style="flex: ${percentage}; background: ${color}; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 12px;">
                                        ${percentage.toFixed(0)}%
                                    </div>
                                ` : '';
            }).join('')}
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 12px; color: #8b949e; flex-wrap: wrap; gap: 8px;">
                            ${Object.entries(agedData.buckets).map(([key, bucket]) => {
                const colors = { 'Current': '#3fb950', '1-30': '#58a6ff', '31-60': '#f0c14e', '61-90': '#f0883e', '90+': '#f85149' };
                const color = colors[key] || '#8b949e';
                return `<span style="color: ${color};">● ${bucket.label}: $${(bucket.amount / 1000).toFixed(1)}K (${bucket.count})</span>`;
            }).join('')}
                        </div>
                    </div>

                    <!-- Revenue Trends -->
                    <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 24px;">
                        <h4 style="margin: 0 0 16px 0; color: #c9d1d9; font-size: 14px;">Revenue Trends (Last 12 Months)</h4>
                        <div id="revenue-trends-chart-mini"></div>
                    </div>

                    <!-- Top Overdue Invoices -->
                    <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 24px;">
                        <h4 style="margin: 0 0 16px 0; color: #c9d1d9; font-size: 14px;">
                            Critical: Top 10 Overdue Invoices
                            <span style="font-size: 12px; color: #f85149; font-weight: 400; margin-left: 8px;">Requires Immediate Action</span>
                        </h4>
                        <div id="critical-overdue-table"></div>
                    </div>

                    <!-- Customer Payment Intelligence -->
                    <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 24px;">
                        <h4 style="margin: 0 0 16px 0; color: #c9d1d9; font-size: 14px;">
                            <i class="fas fa-brain" style="color: #1f6feb;"></i>
                            Customer Payment Intelligence
                        </h4>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
                            ${this.generatePaymentIntelligence(invoices)}
                        </div>
                    </div>

                    <!-- Full Invoice Table -->
                    <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                        <h4 style="margin: 0 0 16px 0; color: #c9d1d9; font-size: 14px;">All Invoices</h4>
                        <div id="invoice-intelligence-full-table"></div>
                    </div>
                </div>
            `;

            resultsDiv.innerHTML = html;

            // Initialize critical overdue table
            const overdueTableData = overdueInvoices
                .map(inv => ({
                    invoice_number: inv.invoice_number,
                    contact_name: inv.contact_name,
                    amount_due: inv.amount_due || 0,
                    due_date: this.parseXeroDate(inv.due_date),
                    days_overdue: Math.floor((new Date() - this.parseXeroDate(inv.due_date)) / (1000 * 60 * 60 * 24)),
                    status: inv.status
                }))
                .sort((a, b) => b.days_overdue - a.days_overdue)
                .slice(0, 10);

            new Tabulator('#critical-overdue-table', {
                data: overdueTableData,
                layout: 'fitData',
                height: '400px',
                columns: [
                    { title: 'Invoice #', field: 'invoice_number', width: 120 },
                    { title: 'Contact', field: 'contact_name', widthGrow: 2 },
                    {
                        title: 'Amount Due',
                        field: 'amount_due',
                        width: 120,
                        hozAlign: 'right',
                        formatter: (cell) => `<span style="color: #f85149; font-weight: 600;">$${cell.getValue().toFixed(2)}</span>`
                    },
                    {
                        title: 'Days Overdue',
                        field: 'days_overdue',
                        width: 130,
                        hozAlign: 'right',
                        formatter: (cell) => {
                            const val = cell.getValue();
                            const color = val > 90 ? '#f85149' : val > 60 ? '#f0883e' : '#f0c14e';
                            return `<span style="color: ${color}; font-weight: 700;">${val}d</span>`;
                        }
                    },
                    {
                        title: 'Recommended Action',
                        width: 180,
                        formatter: (cell) => {
                            const days = cell.getRow().getData().days_overdue;
                            if (days > 90) return '<span style="color: #f85149; font-weight: 600;">📞 Call Now</span>';
                            if (days > 60) return '<span style="color: #f0883e; font-weight: 600;">✉️ Send Reminder</span>';
                            return '<span style="color: #f0c14e; font-weight: 600;">📧 Email Follow-up</span>';
                        }
                    },
                    {
                        title: 'Actions',
                        width: 100,
                        hozAlign: 'center',
                        headerSort: false,
                        formatter: () => `
                            <button class="xero-action-btn" style="padding: 6px 12px; background: #1f6feb; border: 1px solid #1f6feb; border-radius: 4px; color: white; cursor: pointer; font-size: 11px;">
                                <i class="fas fa-eye"></i> View
                            </button>
                        `,
                        cellClick: (e, cell) => {
                            const rowData = cell.getRow().getData();
                            // Find full invoice data
                            const invoice = invoices.find(inv => inv.invoice_number === rowData.invoice_number);
                            if (invoice) {
                                this.showDetailsModal('invoice', invoice);
                            }
                        }
                    }
                ]
            });

            // Initialize full invoice table
            new Tabulator('#invoice-intelligence-full-table', {
                data: invoices,
                layout: 'fitData',
                height: '600px',
                pagination: 'local',
                paginationSize: 25,
                paginationSizeSelector: [10, 25, 50, 100, 200],
                paginationCounter: 'rows',
                resizableRows: true,
                columns: [
                    { title: 'Invoice #', field: 'invoice_number', width: 120, headerFilter: 'input' },
                    { title: 'Contact', field: 'contact_name', widthGrow: 2, headerFilter: 'input' },
                    {
                        title: 'Date',
                        field: 'date',
                        width: 110,
                        formatter: (cell) => {
                            const date = this.parseXeroDate(cell.getValue());
                            return date ? this.formatDate(date) : 'N/A';
                        }
                    },
                    {
                        title: 'Total',
                        field: 'total',
                        width: 120,
                        hozAlign: 'right',
                        formatter: (cell) => `$${cell.getValue().toFixed(2)}`
                    },
                    {
                        title: 'Amount Due',
                        field: 'amount_due',
                        width: 120,
                        hozAlign: 'right',
                        formatter: (cell) => {
                            const val = cell.getValue() || 0;
                            return `<span style="color: ${val > 0 ? '#f0883e' : '#3fb950'}; font-weight: 600;">$${val.toFixed(2)}</span>`;
                        }
                    },
                    {
                        title: 'Status',
                        field: 'status',
                        width: 110,
                        headerFilter: 'input',
                        formatter: (cell) => this.getStatusBadge(cell.getValue())
                    },
                    {
                        title: 'Actions',
                        width: 100,
                        hozAlign: 'center',
                        headerSort: false,
                        formatter: () => `
                            <button class="xero-action-btn" style="padding: 6px 12px; background: #1f6feb; border: 1px solid #1f6feb; border-radius: 4px; color: white; cursor: pointer; font-size: 11px;">
                                <i class="fas fa-eye"></i> View
                            </button>
                        `,
                        cellClick: (e, cell) => {
                            const invoice = cell.getRow().getData();
                            this.showDetailsModal('invoice', invoice);
                        }
                    }
                ]
            });

            // Initialize revenue trends mini chart
            this.createRevenueTrendsChart(trendsData.trends || []);

            // Event listeners for action buttons
            document.getElementById('refresh-invoice-intelligence')?.addEventListener('click', () => this.showInvoiceIntelligence());

            document.getElementById('ai-export-invoice-intelligence')?.addEventListener('click', () => {
                const exportData = {
                    metrics: { totalRevenue, totalOutstanding, overdueAmount, collectionRate, avgInvoiceValue, avgDaysToPay },
                    aged_receivables: agedData.buckets,
                    overdue_invoices: overdueTableData,
                    revenue_trends: trendsData.trends,
                    invoices: invoices.slice(0, 100)
                };

                const formattedText = this.formatDataForAI(exportData, 'Invoice Intelligence Dashboard', `${this.API_BASE_URL}/api/xero/invoices?business_id=${this.currentBusiness}`);
                navigator.clipboard.writeText(formattedText).then(() => {
                    alert('Invoice intelligence data copied to clipboard! Paste into your AI assistant.');
                });
            });

            document.getElementById('export-invoice-intelligence-csv')?.addEventListener('click', () => {
                const csv = this.convertToCSV(invoices);
                this.downloadCSV(csv, 'invoice-intelligence.csv');
            });

        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;"><i class="fas fa-exclamation-circle"></i> Error loading invoice intelligence: ${error.message}</div>`;
        }
    }

    generatePaymentIntelligence(invoices) {
        // Calculate customer payment patterns
        const customerStats = {};

        invoices.forEach(inv => {
            if (!customerStats[inv.contact_name]) {
                customerStats[inv.contact_name] = {
                    total_invoices: 0,
                    total_amount: 0,
                    paid_on_time: 0,
                    late_payments: 0,
                    avg_days_to_pay: []
                };
            }

            const stats = customerStats[inv.contact_name];
            stats.total_invoices++;
            stats.total_amount += inv.total || 0;

            if (inv.status === 'PAID') {
                const issued = this.parseXeroDate(inv.date);
                const due = this.parseXeroDate(inv.due_date);
                const paid = this.parseXeroDate(inv.fully_paid_on_date || inv.date);

                if (paid && due) {
                    const daysDiff = Math.floor((paid - due) / (1000 * 60 * 60 * 24));
                    stats.avg_days_to_pay.push(daysDiff);

                    if (daysDiff <= 0) stats.paid_on_time++;
                    else stats.late_payments++;
                }
            }
        });

        // Find best and worst payers
        const customers = Object.entries(customerStats)
            .filter(([_, stats]) => stats.total_invoices >= 3)
            .map(([name, stats]) => ({
                name,
                ...stats,
                avg_payment_delay: stats.avg_days_to_pay.length > 0
                    ? stats.avg_days_to_pay.reduce((a, b) => a + b, 0) / stats.avg_days_to_pay.length
                    : 0,
                on_time_rate: stats.total_invoices > 0 ? (stats.paid_on_time / stats.total_invoices * 100) : 0
            }));

        const bestPayers = customers.sort((a, b) => b.on_time_rate - a.on_time_rate).slice(0, 5);
        const worstPayers = customers.sort((a, b) => a.on_time_rate - b.on_time_rate).slice(0, 5);
        const highValue = customers.sort((a, b) => b.total_amount - a.total_amount).slice(0, 5);

        return `
            <div style="padding: 12px; background: #0d1117; border: 1px solid #3fb950; border-radius: 4px;">
                <div style="font-size: 11px; color: #3fb950; text-transform: uppercase; margin-bottom: 8px; font-weight: 600;">
                    <i class="fas fa-star"></i> Best Payers
                </div>
                ${bestPayers.map(c => `
                    <div style="font-size: 12px; color: #c9d1d9; margin-bottom: 4px;">
                        <strong>${c.name}</strong>
                        <div style="font-size: 10px; color: #8b949e;">${c.on_time_rate.toFixed(0)}% on-time • ${c.total_invoices} invoices</div>
                    </div>
                `).join('')}
            </div>
            <div style="padding: 12px; background: #0d1117; border: 1px solid #f85149; border-radius: 4px;">
                <div style="font-size: 11px; color: #f85149; text-transform: uppercase; margin-bottom: 8px; font-weight: 600;">
                    <i class="fas fa-exclamation-triangle"></i> Needs Attention
                </div>
                ${worstPayers.map(c => `
                    <div style="font-size: 12px; color: #c9d1d9; margin-bottom: 4px;">
                        <strong>${c.name}</strong>
                        <div style="font-size: 10px; color: #8b949e;">Avg ${Math.abs(c.avg_payment_delay).toFixed(0)}d ${c.avg_payment_delay > 0 ? 'late' : 'early'} • ${c.total_invoices} invoices</div>
                    </div>
                `).join('')}
            </div>
            <div style="padding: 12px; background: #0d1117; border: 1px solid #1f6feb; border-radius: 4px;">
                <div style="font-size: 11px; color: #1f6feb; text-transform: uppercase; margin-bottom: 8px; font-weight: 600;">
                    <i class="fas fa-dollar-sign"></i> High-Value Customers
                </div>
                ${highValue.map(c => `
                    <div style="font-size: 12px; color: #c9d1d9; margin-bottom: 4px;">
                        <strong>${c.name}</strong>
                        <div style="font-size: 10px; color: #8b949e;">$${(c.total_amount / 1000).toFixed(1)}K total • ${c.total_invoices} invoices</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    createRevenueTrendsChart(trends) {
        const container = document.getElementById('revenue-trends-chart-mini');
        if (!container || !trends || trends.length === 0) return;

        const maxRevenue = Math.max(...trends.map(t => t.revenue || 0));
        const bars = trends.slice(-12).map(trend => {
            const height = maxRevenue > 0 ? (trend.revenue / maxRevenue * 100) : 0;
            return `
                <div style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; min-width: 40px;">
                    <div style="font-size: 10px; color: #8b949e; margin-bottom: 4px;">$${(trend.revenue / 1000).toFixed(0)}K</div>
                    <div style="width: 100%; height: ${height * 2}px; background: linear-gradient(180deg, #1f6feb 0%, #0d419d 100%); border-radius: 4px 4px 0 0; transition: all 0.3s;"></div>
                    <div style="font-size: 10px; color: #8b949e; margin-top: 4px; white-space: nowrap;">${trend.month || ''}</div>
                </div>
            `;
        }).join('');

        container.innerHTML = `<div style="display: flex; gap: 4px; align-items: flex-end; height: 250px;">${bars}</div>`;
    }

    async showAgedReceivables() {
        const resultsDiv = document.querySelector('#xero-invoices-report-results');
        if (!resultsDiv) return;

        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading aged receivables...</div>';

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/aged-receivables?business_id=${this.currentBusiness}`);
            const data = await response.json();

            if (!data.success) throw new Error(data.error);

            const { buckets, total_outstanding, total_count } = data;

            let html = `
                <div style="padding: 16px; background: #161b22; border-radius: 6px;">
                    <h4 style="margin: 0 0 16px 0; color: #c9d1d9;">
                        Aged Receivables Report
                        <i class="fas fa-info-circle xero-info-icon" data-tooltip="aged-receivables"></i>
                        <span style="font-size: 12px; color: #8b949e; font-weight: normal; margin-left: 8px;">
                            as of ${new Date().toLocaleDateString('en-GB')}
                        </span>
                    </h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="border-bottom: 1px solid #30363d;">
                                <th style="text-align: left; padding: 8px; color: #8b949e; font-size: 12px; font-weight: 600;">Age Bucket</th>
                                <th style="text-align: right; padding: 8px; color: #8b949e; font-size: 12px; font-weight: 600;">Count</th>
                                <th style="text-align: right; padding: 8px; color: #8b949e; font-size: 12px; font-weight: 600;">Amount</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            for (const [key, bucket] of Object.entries(buckets)) {
                const color = key === '90+' ? '#f85149' : key === '61-90' ? '#f0883e' : key === '31-60' ? '#f0c14e' : '#c9d1d9';
                html += `
                    <tr style="border-bottom: 1px solid #21262d;">
                        <td style="padding: 8px; color: ${color};">${bucket.label}</td>
                        <td style="text-align: right; padding: 8px; color: #c9d1d9;">${bucket.count}</td>
                        <td style="text-align: right; padding: 8px; color: #c9d1d9;">$${bucket.amount.toFixed(2)}</td>
                    </tr>
                `;
            }

            html += `
                        </tbody>
                        <tfoot>
                            <tr style="border-top: 2px solid #30363d; font-weight: 600;">
                                <td style="padding: 8px; color: #ffffff;">TOTAL</td>
                                <td style="text-align: right; padding: 8px; color: #ffffff;">${total_count}</td>
                                <td style="text-align: right; padding: 8px; color: #ffffff;">$${total_outstanding.toFixed(2)}</td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            `;

            resultsDiv.innerHTML = html;

            // Refresh tooltips for info icon
            this.refreshTooltips();
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 16px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showSalesSummary() {
        const resultsDiv = document.querySelector('#xero-invoices-report-results');
        if (!resultsDiv) return;

        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading sales summary...</div>';

        try {
            const months = this.dateRanges.invoices || 3;
            const fromDate = this.getDateRangeStart(months);
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/sales-summary?business_id=${this.currentBusiness}&from_date=${fromDate}`);
            const data = await response.json();

            if (!data.success) throw new Error(data.error);

            const { sales, total_revenue, total_paid, total_outstanding } = data;

            let html = `
                <div style="padding: 16px; background: #161b22; border-radius: 6px;">
                    <h4 style="margin: 0 0 16px 0; color: #c9d1d9;">
                        Sales Summary
                        <i class="fas fa-info-circle xero-info-icon" data-tooltip="sales-summary"></i>
                        <span style="font-size: 12px; color: #8b949e; font-weight: normal; margin-left: 8px;">
                            ${this.formatDateRangeDisplay(months)}
                        </span>
                    </h4>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;">
                        <div style="padding: 12px; background: #0d1117; border-radius: 4px;">
                            <div style="color: #8b949e; font-size: 11px; margin-bottom: 4px;">Total Revenue</div>
                            <div style="color: #ffffff; font-size: 18px; font-weight: 600;">$${total_revenue.toFixed(2)}</div>
                        </div>
                        <div style="padding: 12px; background: #0d1117; border-radius: 4px;">
                            <div style="color: #8b949e; font-size: 11px; margin-bottom: 4px;">Total Paid</div>
                            <div style="color: #3fb950; font-size: 18px; font-weight: 600;">$${total_paid.toFixed(2)}</div>
                        </div>
                        <div style="padding: 12px; background: #0d1117; border-radius: 4px;">
                            <div style="color: #8b949e; font-size: 11px; margin-bottom: 4px;">Outstanding</div>
                            <div style="color: #f0883e; font-size: 18px; font-weight: 600;">$${total_outstanding.toFixed(2)}</div>
                        </div>
                    </div>
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                        <thead>
                            <tr style="border-bottom: 1px solid #30363d;">
                                <th style="text-align: left; padding: 8px; color: #8b949e; font-weight: 600;">Customer</th>
                                <th style="text-align: right; padding: 8px; color: #8b949e; font-weight: 600;">Invoices</th>
                                <th style="text-align: right; padding: 8px; color: #8b949e; font-weight: 600;">Revenue</th>
                                <th style="text-align: right; padding: 8px; color: #8b949e; font-weight: 600;">Outstanding</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            for (const sale of sales.slice(0, 10)) {
                html += `
                    <tr style="border-bottom: 1px solid #21262d;">
                        <td style="padding: 8px; color: #c9d1d9;">${sale.contact_name}</td>
                        <td style="text-align: right; padding: 8px; color: #c9d1d9;">${sale.invoice_count}</td>
                        <td style="text-align: right; padding: 8px; color: #c9d1d9;">$${sale.total_invoiced.toFixed(2)}</td>
                        <td style="text-align: right; padding: 8px; color: #c9d1d9;">$${sale.outstanding.toFixed(2)}</td>
                    </tr>
                `;
            }

            html += `
                        </tbody>
                    </table>
                </div>
            `;

            resultsDiv.innerHTML = html;

            // Refresh tooltips for info icon
            this.refreshTooltips();
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 16px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showOverdueInvoices() {
        const resultsDiv = document.querySelector('#xero-invoices-report-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading overdue invoices...</div>';

        try {
            const fromDate = this.getDateRangeStart(this.dateRanges.invoices);
            let url = `${this.API_BASE_URL}/api/xero/reports/overdue-invoices?business_id=${this.currentBusiness}`;
            if (fromDate) url += `&from_date=${fromDate}`;

            const response = await fetch(url);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);

            // Transform data for Tabulator
            const tableData = (data.invoices || []).map(inv => ({
                invoice_number: inv.invoice_number || inv.InvoiceNumber || 'N/A',
                contact_name: inv.contact_name || inv.contact || inv.Contact?.Name || 'Unknown',
                due_date: this.parseXeroDate(inv.due_date || inv.DueDate),
                amount_due: parseFloat(inv.amount_due || inv.AmountDue || 0),
                days_overdue: inv.days_overdue || Math.max(0, Math.floor((new Date() - this.parseXeroDate(inv.due_date || inv.DueDate)) / (1000 * 60 * 60 * 24)))
            }));

            resultsDiv.innerHTML = `<div style="padding: 16px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Overdue Invoices (${tableData.length}) <i class="fas fa-info-circle xero-info-icon" data-tooltip="overdue-invoices"></i> <span style="font-size: 12px; color: #8b949e; font-weight: normal; margin-left: 8px;">${this.getDateRangeText('invoices')}</span></h4><div id="overdue-invoices-table"></div></div>`;

            new Tabulator('#overdue-invoices-table', {
                data: tableData,
                layout: 'fitData',
                autoColumns: false,
                height: '600px',
                pagination: 'local',
                paginationSize: 25,
                paginationSizeSelector: [10, 25, 50, 100],
                columns: [
                    { title: 'Invoice #', field: 'invoice_number', sorter: 'string', headerFilter: 'input', minWidth: 100, maxWidth: 150, widthGrow: 1, widthShrink: 1 },
                    { title: 'Contact', field: 'contact_name', sorter: 'string', headerFilter: 'input', minWidth: 120, maxWidth: 300, widthGrow: 2, widthShrink: 1 },
                    {
                        title: 'Due Date',
                        field: 'due_date',
                        sorter: 'date',
                        sorterParams: {
                            format: 'iso',
                            alignEmptyValues: 'bottom'
                        },
                        formatter: (cell) => {
                            const val = cell.getValue();
                            if (!val) return 'N/A';
                            const dateObj = val instanceof Date ? val : this.parseXeroDate(val);
                            return this.formatDate(dateObj);
                        },
                        minWidth: 90,
                        maxWidth: 130,
                        widthGrow: 1,
                        widthShrink: 1
                    },
                    {
                        title: 'Days Overdue',
                        field: 'days_overdue',
                        sorter: 'number',
                        hozAlign: 'right',
                        minWidth: 100,
                        maxWidth: 130,
                        widthGrow: 1,
                        widthShrink: 1,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            const color = val > 90 ? '#f85149' : val > 60 ? '#d29922' : '#f0883e';
                            return `<span style="color: ${color}; font-weight: bold;">${val}</span>`;
                        }
                    },
                    {
                        title: 'Amount Due',
                        field: 'amount_due',
                        sorter: 'number',
                        hozAlign: 'right',
                        formatter: 'money',
                        formatterParams: { precision: 2, symbol: '$' },
                        minWidth: 100,
                        maxWidth: 150,
                        widthGrow: 1,
                        widthShrink: 1
                    },
                    {
                        title: 'Actions',
                        width: 100,
                        hozAlign: 'center',
                        headerSort: false,
                        formatter: () => `
                            <button class="xero-action-btn" style="padding: 6px 12px; background: #1f6feb; border: 1px solid #1f6feb; border-radius: 4px; color: white; cursor: pointer; font-size: 11px;">
                                <i class="fas fa-eye"></i> View
                            </button>
                        `,
                        cellClick: (e, cell) => {
                            const rowData = cell.getRow().getData();
                            // Find full invoice from original data
                            const invoice = (data.invoices || []).find(inv =>
                                (inv.invoice_number || inv.InvoiceNumber) === rowData.invoice_number
                            );
                            if (invoice) {
                                this.showDetailsModal('invoice', invoice);
                            }
                        }
                    }
                ],
                initialSort: [{ column: 'days_overdue', dir: 'desc' }]
            });

            // Refresh tooltips for dynamically loaded icons
            this.refreshTooltips();
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showRevenueTrends() {
        const resultsDiv = document.querySelector('#xero-invoices-report-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading revenue trends...</div>';

        try {
            const fromDate = this.getDateRangeStart(this.dateRanges.invoices);
            let url = `${this.API_BASE_URL}/api/xero/reports/revenue-trends?business_id=${this.currentBusiness}`;
            if (fromDate) url += `&from_date=${fromDate}`;

            const response = await fetch(url);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);

            // Transform data for Tabulator
            const tableData = (data.trends || []).map(trend => ({
                month: trend.month || trend.period,
                revenue: parseFloat(trend.revenue || 0),
                invoice_count: trend.invoice_count || trend.count || 0,
                avg_value: trend.invoice_count ? (trend.revenue / trend.invoice_count) : 0
            }));

            // Calculate totals and averages
            const totalRevenue = tableData.reduce((sum, t) => sum + t.revenue, 0);
            const avgMonthlyRevenue = tableData.length > 0 ? totalRevenue / tableData.length : 0;

            resultsDiv.innerHTML = `
                <div style="padding: 16px;">
                    <h4 style="margin: 0 0 16px 0; color: #c9d1d9;">
                        Revenue Trends
                        <span style="font-size: 12px; color: #8b949e; font-weight: normal; margin-left: 8px;">
                            ${this.getDateRangeText('invoices')}
                        </span>
                    </h4>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 16px;">
                        <div style="padding: 12px; background: #0d1117; border-radius: 4px;">
                            <div style="color: #8b949e; font-size: 11px; margin-bottom: 4px;">Total Revenue</div>
                            <div style="color: #3fb950; font-size: 18px; font-weight: 600;">$${totalRevenue.toFixed(2)}</div>
                        </div>
                        <div style="padding: 12px; background: #0d1117; border-radius: 4px;">
                            <div style="color: #8b949e; font-size: 11px; margin-bottom: 4px;">Avg Monthly</div>
                            <div style="color: #58a6ff; font-size: 18px; font-weight: 600;">$${avgMonthlyRevenue.toFixed(2)}</div>
                        </div>
                    </div>
                    <div id="revenue-trends-table"></div>
                </div>
            `;

            new Tabulator('#revenue-trends-table', {
                data: tableData,
                layout: 'fitData',
                autoColumns: false,
                height: '500px',
                pagination: 'local',
                paginationSize: 12,
                columns: [
                    { title: 'Month', field: 'month', sorter: 'string', headerFilter: 'input', minWidth: 90, maxWidth: 150, widthGrow: 1, widthShrink: 1 },
                    { title: 'Revenue', field: 'revenue', sorter: 'number', hozAlign: 'right', formatter: 'money', formatterParams: { precision: 2, symbol: '$' }, minWidth: 100, maxWidth: 200, widthGrow: 2, widthShrink: 1 },
                    { title: 'Invoices', field: 'invoice_count', sorter: 'number', hozAlign: 'center', minWidth: 80, maxWidth: 110, widthGrow: 1, widthShrink: 1 },
                    { title: 'Avg Value', field: 'avg_value', sorter: 'number', hozAlign: 'right', formatter: 'money', formatterParams: { precision: 2, symbol: '$' }, minWidth: 90, maxWidth: 150, widthGrow: 1, widthShrink: 1 }
                ],
                initialSort: [{ column: 'month', dir: 'desc' }]
            });
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showInvoiceStatus() {
        const resultsDiv = document.querySelector('#xero-invoices-report-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading status summary...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/invoice-status?business_id=${this.currentBusiness}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Invoice Status Summary <i class="fas fa-info-circle xero-info-icon" data-tooltip="invoice-status"></i> <span style="font-size: 12px; color: #8b949e; font-weight: normal; margin-left: 8px;">as of ${new Date().toLocaleDateString('en-GB')}</span></h4><table style="width: 100%; border-collapse: collapse;"><thead><tr style="border-bottom: 1px solid #30363d;"><th style="text-align: left; padding: 8px;">Status</th><th style="text-align: right; padding: 8px;">Count</th><th style="text-align: right; padding: 8px;">Total Amount</th></tr></thead><tbody>`;
            Object.entries(data.status_summary).forEach(([status, stats]) => {
                html += `<tr style="border-bottom: 1px solid #30363d;"><td style="padding: 8px; color: #c9d1d9;">${status}</td><td style="padding: 8px; text-align: right; color: #8b949e;">${stats.count}</td><td style="padding: 8px; text-align: right; color: #c9d1d9;">$${stats.total.toFixed(2)}</td></tr>`;
            });
            html += `</tbody></table></div>`;
            resultsDiv.innerHTML = html;

            // Refresh tooltips for info icon
            this.refreshTooltips();
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showInvoiceVolume() {
        const resultsDiv = document.querySelector('#xero-invoices-report-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading volume analysis...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/invoice-volume?business_id=${this.currentBusiness}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Invoice Volume Analysis <i class="fas fa-info-circle xero-info-icon" data-tooltip="invoice-volume"></i> <span style="font-size: 12px; color: #8b949e; font-weight: normal; margin-left: 8px;">All Time</span></h4><div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;"><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e; margin-bottom: 4px;">Total Invoices</div><div style="font-size: 20px; color: #c9d1d9; font-weight: 600;">${data.total_invoices}</div></div><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e; margin-bottom: 4px;">Avg per Month</div><div style="font-size: 20px; color: #c9d1d9; font-weight: 600;">${data.avg_invoices_per_month.toFixed(1)}</div></div><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e; margin-bottom: 4px;">Avg Value</div><div style="font-size: 20px; color: #c9d1d9; font-weight: 600;">$${data.avg_invoice_value.toFixed(2)}</div></div></div></div>`;
            resultsDiv.innerHTML = html;

            // Refresh tooltips for info icon
            this.refreshTooltips();
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showContactActivity() {
        const resultsDiv = document.querySelector('#xero-contacts-report-results');
        if (!resultsDiv) return;
        this.lastContactReportType = 'activity';
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading contact activity...</div>';

        try {
            const fromDate = this.getDateRangeStart(this.dateRanges.contacts);
            let url = `${this.API_BASE_URL}/api/xero/reports/contact-activity?business_id=${this.currentBusiness}`;
            if (fromDate) url += `&from_date=${fromDate}`;

            const response = await fetch(url);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);

            const tableData = (data.contacts || []).map(c => ({
                contact_name: c.contact_name || c.contact || c.name || 'Unknown',
                invoice_count: c.invoice_count || c.total_invoices || 0,
                total_revenue: parseFloat(c.total_revenue || c.revenue || 0)
            }));

            resultsDiv.innerHTML = `<div style="padding: 16px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Contact Activity (${tableData.length}) <i class="fas fa-info-circle xero-info-icon" data-tooltip="contact-activity"></i> <span style="font-size: 12px; color: #8b949e; font-weight: normal; margin-left: 8px;">${this.getDateRangeText('contacts')}</span></h4><div id="contact-activity-table"></div></div>`;

            new Tabulator('#contact-activity-table', {
                data: tableData,
                layout: 'fitData',
                autoColumns: false,
                height: '600px',
                pagination: 'local',
                paginationSize: 25,
                paginationSizeSelector: [10, 25, 50, 100],
                columns: [
                    { title: 'Contact', field: 'contact_name', sorter: 'string', headerFilter: 'input', minWidth: 150, maxWidth: 300, widthGrow: 2, widthShrink: 1 },
                    { title: 'Invoices', field: 'invoice_count', sorter: 'number', hozAlign: 'right', minWidth: 80, maxWidth: 120, widthGrow: 1, widthShrink: 1, headerFilter: 'input' },
                    { title: 'Total Revenue', field: 'total_revenue', sorter: 'number', hozAlign: 'right', formatter: 'money', formatterParams: { precision: 2, symbol: '$' }, minWidth: 120, maxWidth: 180, widthGrow: 1, widthShrink: 1 }
                ],
                initialSort: [{ column: 'total_revenue', dir: 'desc' }]
            });

            // Refresh tooltips for dynamically loaded icons
            this.refreshTooltips();
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showInactiveCustomers() {
        const resultsDiv = document.querySelector('#xero-contacts-report-results');
        if (!resultsDiv) return;
        this.lastContactReportType = 'inactive';
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading inactive customers...</div>';

        try {
            const fromDate = this.getDateRangeStart(this.dateRanges.contacts);
            let url = `${this.API_BASE_URL}/api/xero/reports/inactive-customers?business_id=${this.currentBusiness}`;
            if (fromDate) url += `&from_date=${fromDate}`;

            const response = await fetch(url);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);

            const tableData = (data.customers || []).map(c => ({
                contact_name: c.contact_name || c.contact || c.name || 'Unknown',
                last_invoice_date: c.last_invoice_date !== 'Never' ? this.parseXeroDate(c.last_invoice_date) : null,
                days_since_last: c.days_since_last || c.days_inactive || 0,
                total_orders: c.total_orders || 0,
                total_revenue: c.total_revenue || 0,
                avg_order_value: c.avg_order_value || 0,
                avg_days_between_orders: c.avg_days_between_orders || 0
            }));

            resultsDiv.innerHTML = `<div style="padding: 16px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Inactive Customers (${tableData.length}) <i class="fas fa-info-circle xero-info-icon" data-tooltip="inactive-customers"></i> <span style="font-size: 12px; color: #8b949e; font-weight: normal; margin-left: 8px;">${this.getDateRangeText('contacts')}</span></h4><div id="inactive-customers-table"></div></div>`;

            new Tabulator('#inactive-customers-table', {
                data: tableData,
                layout: 'fitData',
                autoColumns: false,
                height: '600px',
                pagination: 'local',
                paginationSize: 25,
                paginationSizeSelector: [10, 25, 50, 100],
                columns: [
                    { title: 'Contact', field: 'contact_name', sorter: 'string', headerFilter: 'input', minWidth: 120, maxWidth: 250, widthGrow: 2, widthShrink: 1 },
                    {
                        title: 'Last Invoice',
                        field: 'last_invoice_date',
                        sorter: 'date',
                        formatter: (cell) => {
                            const val = cell.getValue();
                            return val ? this.formatDate(val) : 'Never';
                        },
                        minWidth: 90,
                        maxWidth: 130,
                        widthGrow: 1,
                        widthShrink: 1
                    },
                    {
                        title: 'Days Inactive',
                        field: 'days_since_last',
                        sorter: 'number',
                        hozAlign: 'right',
                        minWidth: 100,
                        maxWidth: 130,
                        widthGrow: 1,
                        widthShrink: 1,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            const color = val > 180 ? '#f85149' : val > 90 ? '#d29922' : '#8b949e';
                            return `<span style="color: ${color};">${val || 'N/A'}</span>`;
                        }
                    },
                    {
                        title: 'Total Orders',
                        field: 'total_orders',
                        sorter: 'number',
                        hozAlign: 'right',
                        minWidth: 80,
                        maxWidth: 120,
                        widthGrow: 1,
                        widthShrink: 1
                    },
                    {
                        title: 'Total Revenue',
                        field: 'total_revenue',
                        sorter: 'number',
                        hozAlign: 'right',
                        formatter: 'money',
                        formatterParams: { precision: 2, symbol: '$' },
                        minWidth: 100,
                        maxWidth: 150,
                        widthGrow: 1,
                        widthShrink: 1
                    },
                    {
                        title: 'Avg Order Value',
                        field: 'avg_order_value',
                        sorter: 'number',
                        hozAlign: 'right',
                        formatter: 'money',
                        formatterParams: { precision: 2, symbol: '$' },
                        minWidth: 110,
                        maxWidth: 160,
                        widthGrow: 1,
                        widthShrink: 1
                    },
                    {
                        title: 'Order Frequency',
                        field: 'avg_days_between_orders',
                        sorter: 'number',
                        hozAlign: 'right',
                        minWidth: 110,
                        maxWidth: 170,
                        widthGrow: 1,
                        widthShrink: 1,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            return val ? val.toFixed(1) + ' days' : 'N/A';
                        }
                    }
                ],
                initialSort: [{ column: 'days_since_last', dir: 'desc' }]
            });

            // Refresh tooltips for dynamically loaded icons
            this.refreshTooltips();
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showCustomerLTV() {
        const resultsDiv = document.querySelector('#xero-contacts-report-results');
        if (!resultsDiv) return;
        this.lastContactReportType = 'ltv';
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading customer lifetime value...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/customer-lifetime-value?business_id=${this.currentBusiness}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Customer Lifetime Value <i class="fas fa-info-circle xero-info-icon" data-tooltip="customer-ltv"></i> <span style="font-size: 12px; color: #8b949e; font-weight: normal; margin-left: 8px;">(Lifetime)</span></h4><table style="width: 100%; border-collapse: collapse;"><thead><tr style="border-bottom: 1px solid #30363d;"><th style="text-align: left; padding: 8px;">Customer</th><th style="text-align: right; padding: 8px;">Revenue</th><th style="text-align: right; padding: 8px;">Invoices</th><th style="text-align: right; padding: 8px;">Tenure (days)</th></tr></thead><tbody>`;
            data.customers.slice(0, 20).forEach(customer => {
                html += `<tr style="border-bottom: 1px solid #30363d;"><td style="padding: 8px; color: #c9d1d9;">${customer.contact_name}</td><td style="padding: 8px; text-align: right; color: #238636; font-weight: 600;">$${customer.total_revenue.toFixed(2)}</td><td style="padding: 8px; text-align: right; color: #8b949e;">${customer.invoice_count}</td><td style="padding: 8px; text-align: right; color: #8b949e;">${customer.tenure_days}</td></tr>`;
            });
            html += `</tbody></table></div>`;
            resultsDiv.innerHTML = html;

            // Refresh tooltips for info icon
            this.refreshTooltips();
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showCustomerSegmentation() {
        const resultsDiv = document.querySelector('#xero-contacts-report-results');
        if (!resultsDiv) return;
        this.lastContactReportType = 'segmentation';
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading customer segmentation...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/customer-segmentation?business_id=${this.currentBusiness}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Customer Segmentation (RFM) <i class="fas fa-info-circle xero-info-icon" data-tooltip="customer-segmentation"></i> <span style="font-size: 12px; color: #8b949e; font-weight: normal; margin-left: 8px;">Current</span></h4><div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px; margin-bottom: 16px;">`;
            const colors = { Champions: '#238636', 'Loyal Customers': '#1f6feb', 'Potential Loyalists': '#8957e5', 'At Risk': '#d29922', Lost: '#f85149' };
            Object.entries(data.segment_distribution).forEach(([segment, count]) => {
                html += `<div style="padding: 12px; background: #0d1117; border-radius: 4px; border-left: 3px solid ${colors[segment] || '#8b949e'};"><div style="font-size: 12px; color: #8b949e;">${segment}</div><div style="font-size: 20px; color: #c9d1d9; font-weight: 600;">${count}</div></div>`;
            });
            html += `</div></div>`;
            resultsDiv.innerHTML = html;

            // Refresh tooltips for info icon
            this.refreshTooltips();
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showCustomerHealth() {
        const resultsDiv = document.querySelector('#xero-contacts-report-results');
        if (!resultsDiv) return;
        this.lastContactReportType = 'health';
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;"><i class="fas fa-spinner fa-spin"></i> Loading customer health metrics...</div>';

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/customer-health?business_id=${this.currentBusiness}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);

            const html = `
                <div style="padding: 16px; background: #161b22; border-radius: 6px;">
                    <h4 style="margin: 0 0 16px 0; color: #c9d1d9;">
                        Customer Health Dashboard
                        <span style="font-size: 12px; color: #8b949e; font-weight: normal; margin-left: 8px;">as of ${new Date().toLocaleDateString('en-GB')}</span>
                    </h4>
                    
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;">
                        <div style="padding: 16px; background: #0d1117; border-radius: 4px; border-left: 3px solid #3fb950;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Total Customers</div>
                            <div style="font-size: 24px; color: #c9d1d9; font-weight: 700;">${data.total_customers || 0}</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Active contacts</div>
                        </div>
                        
                        <div style="padding: 16px; background: #0d1117; border-radius: 4px; border-left: 3px solid #1f6feb;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">New Customers</div>
                            <div style="font-size: 24px; color: #1f6feb; font-weight: 700;">${data.new_customers || 0}</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Last 30 days</div>
                        </div>
                        
                        <div style="padding: 16px; background: #0d1117; border-radius: 4px; border-left: 3px solid #f85149;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Churned</div>
                            <div style="font-size: 24px; color: #f85149; font-weight: 700;">${data.churned_customers || 0}</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">${((data.churn_rate || 0) * 100).toFixed(1)}% churn rate</div>
                        </div>
                        
                        <div style="padding: 16px; background: #0d1117; border-radius: 4px; border-left: 3px solid #d29922;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Retention</div>
                            <div style="font-size: 24px; color: #d29922; font-weight: 700;">${((data.retention_rate || 0) * 100).toFixed(1)}%</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">30-day retention</div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;">
                        <div style="padding: 16px; background: #0d1117; border-radius: 6px;">
                            <h5 style="margin: 0 0 12px 0; color: #c9d1d9; font-size: 14px;">Customer Growth</h5>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 20px; color: #3fb950; font-weight: 700;">+${data.net_growth || 0}</div>
                                    <div style="font-size: 11px; color: #8b949e;">Net growth (30d)</div>
                                </div>
                                <div style="font-size: 36px; color: #3fb950;"><i class="fas fa-arrow-trend-up"></i></div>
                            </div>
                        </div>
                        
                        <div style="padding: 16px; background: #0d1117; border-radius: 6px;">
                            <h5 style="margin: 0 0 12px 0; color: #c9d1d9; font-size: 14px;">At-Risk Customers</h5>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 20px; color: #f85149; font-weight: 700;">${data.at_risk_count || 0}</div>
                                    <div style="font-size: 11px; color: #8b949e;">Require attention</div>
                                </div>
                                <div style="font-size: 36px; color: #f85149;"><i class="fas fa-exclamation-triangle"></i></div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="padding: 12px; background: #0d1117; border-radius: 6px; border: 1px solid #388bfd;">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                            <i class="fas fa-lightbulb" style="color: #d29922;"></i>
                            <span style="font-size: 13px; color: #c9d1d9; font-weight: 600;">Key Insights</span>
                        </div>
                        <ul style="margin: 0; padding-left: 20px; font-size: 12px; color: #8b949e; line-height: 1.6;">
                            <li>Customer base ${(data.net_growth || 0) >= 0 ? 'growing' : 'shrinking'} at ${Math.abs((data.growth_rate || 0) * 100).toFixed(1)}% monthly rate</li>
                            <li>${data.at_risk_count || 0} customers haven't ordered in 60+ days - consider re-engagement campaign</li>
                            <li>Retention rate of ${((data.retention_rate || 0) * 100).toFixed(1)}% ${(data.retention_rate || 0) > 0.8 ? 'is strong' : 'needs improvement'}</li>
                        </ul>
                    </div>
                </div>
            `;

            resultsDiv.innerHTML = html;
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;"><i class="fas fa-exclamation-circle"></i> Error loading customer health: ${error.message}</div>`;
        }
    }

    async showBusinessComparison() {
        const resultsDiv = document.querySelector('#xero-reports-results');
        if (!resultsDiv) return;

        // Create date picker container
        resultsDiv.innerHTML = `
            <div style="padding: 20px;">
                <h2 style="margin: 0 0 16px 0; color: #c9d1d9; font-size: 24px; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-building" style="color: #13B5EA;"></i> Business Performance Dashboard
                </h2>
                <div id="business-comparison-date-picker"></div>
                <div id="business-comparison-kpis" style="margin-bottom: 20px;"></div>
                <div id="business-comparison-charts" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 20px;"></div>
                <div id="business-comparison-table" style="margin-bottom: 20px;"></div>
                <div id="business-comparison-alerts"></div>
            </div>
        `;

        const loadData = async (dateRange, comparison) => {
            // Show loading spinner
            const kpisDiv = document.getElementById('business-comparison-kpis');
            const chartsDiv = document.getElementById('business-comparison-charts');
            const tableDiv = document.getElementById('business-comparison-table');
            const alertsDiv = document.getElementById('business-comparison-alerts');

            if (kpisDiv) kpisDiv.innerHTML = '<div style="text-align: center; padding: 40px; color: #8b949e;"><i class="fas fa-spinner fa-spin" style="font-size: 24px;"></i><br><br>Loading business comparison data...</div>';
            if (chartsDiv) chartsDiv.innerHTML = '';
            if (tableDiv) tableDiv.innerHTML = '';
            if (alertsDiv) alertsDiv.innerHTML = '';

            try {
                const url = `${this.API_BASE_URL}/api/xero/reports/business-comparison-enhanced?from_date=${dateRange.from}&to_date=${dateRange.to}&compare_to=${comparison}`;
                const response = await fetch(url);
                const data = await response.json();
                if (!data.success) throw new Error(data.error);

                // KPI Cards
                const kpiHtml = `
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
                        <div style="padding: 16px; background: linear-gradient(135deg, #1f6feb 0%, #1a56db 100%); border-radius: 8px; border: 1px solid #388bfd;">
                            <div style="font-size: 11px; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Total Revenue</div>
                            <div style="font-size: 28px; color: #ffffff; font-weight: 700; margin-bottom: 4px;">$${(data.total_revenue / 1000).toFixed(1)}k</div>
                            ${data.compare_to !== 'none' && data.businesses[0].comparison ?
                        `<div style="font-size: 13px; color: rgba(255,255,255,0.9);">${this.calculateYoYMetrics(data.total_revenue, data.businesses.reduce((sum, b) => sum + b.comparison.revenue, 0)).formatted}</div>`
                        : ''}
                        </div>
                        <div style="padding: 16px; background: linear-gradient(135deg, #238636 0%, #1a7f37 100%); border-radius: 8px; border: 1px solid #2ea043;">
                            <div style="font-size: 11px; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Avg Invoice</div>
                            <div style="font-size: 28px; color: #ffffff; font-weight: 700; margin-bottom: 4px;">$${(data.businesses.reduce((sum, b) => sum + b.avg_invoice_value, 0) / 3).toFixed(0)}</div>
                            <div style="font-size: 13px; color: rgba(255,255,255,0.9);">Across 3 businesses</div>
                        </div>
                        <div style="padding: 16px; background: linear-gradient(135deg, #d29922 0%, #b08008 100%); border-radius: 8px; border: 1px solid #e2a611;">
                            <div style="font-size: 11px; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Outstanding</div>
                            <div style="font-size: 28px; color: #ffffff; font-weight: 700; margin-bottom: 4px;">$${(data.total_outstanding / 1000).toFixed(1)}k</div>
                            <div style="font-size: 13px; color: rgba(255,255,255,0.9);">${((data.total_outstanding / data.total_revenue) * 100).toFixed(1)}% of revenue</div>
                        </div>
                        <div style="padding: 16px; background: linear-gradient(135deg, #8957e5 0%, #6e40c9 100%); border-radius: 8px; border: 1px solid #a371f7;">
                            <div style="font-size: 11px; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Avg Collection</div>
                            <div style="font-size: 28px; color: #ffffff; font-weight: 700; margin-bottom: 4px;">${(data.businesses.reduce((sum, b) => sum + b.collection_days, 0) / 3).toFixed(0)} days</div>
                            <div style="font-size: 13px; color: rgba(255,255,255,0.9);">Days Sales Outstanding</div>
                        </div>
                    </div>
                `;
                document.getElementById('business-comparison-kpis').innerHTML = kpiHtml;

                // Charts Container
                const chartsContainer = document.getElementById('business-comparison-charts');
                chartsContainer.innerHTML = `
                    <div style="background: #161b22; padding: 20px; border-radius: 8px; border: 1px solid #30363d;">
                        <h3 style="margin: 0 0 16px 0; font-size: 16px; color: #c9d1d9; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-chart-pie" style="color: #13B5EA;"></i> Market Share Distribution
                        </h3>
                        <div id="market-share-pie" style="height: 350px;"></div>
                    </div>
                    <div style="background: #161b22; padding: 20px; border-radius: 8px; border: 1px solid #30363d;">
                        <h3 style="margin: 0 0 16px 0; font-size: 16px; color: #c9d1d9; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-chart-line" style="color: #13B5EA;"></i> 12-Month Revenue Trend
                        </h3>
                        <div id="revenue-trend-line" style="height: 350px;"></div>
                    </div>
                `;

                // Pie Chart - Market Share
                const pieData = [{
                    values: data.businesses.map(b => b.revenue),
                    labels: data.businesses.map(b => b.business_name),
                    type: 'pie',
                    marker: {
                        colors: ['#1f6feb', '#238636', '#d29922']
                    },
                    textinfo: 'label+percent',
                    textfont: { color: '#ffffff', size: 14 },
                    hoverinfo: 'label+value+percent',
                    hole: 0.4
                }];
                this.createChart('market-share-pie', pieData, {
                    showlegend: false,
                    height: 400,
                    autosize: true,
                    annotations: [{
                        font: { size: 20, color: '#c9d1d9' },
                        showarrow: false,
                        text: 'Market<br>Share',
                        x: 0.5,
                        y: 0.5
                    }]
                });

                // Line Chart - Revenue Trends
                const lineData = data.businesses.map((business, idx) => ({
                    x: business.monthly_trend.map(m => m.month),
                    y: business.monthly_trend.map(m => m.revenue),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: business.business_name,
                    line: { width: 3, color: ['#1f6feb', '#238636', '#d29922'][idx] },
                    marker: { size: 8 }
                }));
                this.createChart('revenue-trend-line', lineData, {
                    xaxis: { title: 'Month', gridcolor: '#21262d' },
                    yaxis: { title: 'Revenue ($)', gridcolor: '#21262d' },
                    hovermode: 'x unified',
                    height: 400,
                    autosize: true
                });

                // Metrics Table
                let tableHtml = `
                    <div style="background: #161b22; padding: 20px; border-radius: 8px; border: 1px solid #30363d;">
                        <h3 style="margin: 0 0 16px 0; font-size: 16px; color: #c9d1d9; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-table" style="color: #13B5EA;"></i> Detailed Metrics Comparison
                        </h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="border-bottom: 2px solid #30363d;">
                                    <th style="text-align: left; padding: 12px; color: #8b949e; font-weight: 600; font-size: 12px; text-transform: uppercase;">Business</th>
                                    <th style="text-align: right; padding: 12px; color: #8b949e; font-weight: 600; font-size: 12px; text-transform: uppercase;">Revenue</th>
                                    <th style="text-align: right; padding: 12px; color: #8b949e; font-weight: 600; font-size: 12px; text-transform: uppercase;">Market Share</th>
                                    <th style="text-align: right; padding: 12px; color: #8b949e; font-weight: 600; font-size: 12px; text-transform: uppercase;">Invoices</th>
                                    <th style="text-align: right; padding: 12px; color: #8b949e; font-weight: 600; font-size: 12px; text-transform: uppercase;">Avg Value</th>
                                    <th style="text-align: right; padding: 12px; color: #8b949e; font-weight: 600; font-size: 12px; text-transform: uppercase;">Outstanding</th>
                                    <th style="text-align: right; padding: 12px; color: #8b949e; font-weight: 600; font-size: 12px; text-transform: uppercase;">Collection Days</th>
                                    ${data.compare_to !== 'none' ? '<th style="text-align: right; padding: 12px; color: #8b949e; font-weight: 600; font-size: 12px; text-transform: uppercase;">YoY Growth</th>' : ''}
                                </tr>
                            </thead>
                            <tbody>
                `;

                data.businesses.forEach(biz => {
                    const yoyMetrics = biz.comparison ? this.calculateYoYMetrics(biz.revenue, biz.comparison.revenue) : null;
                    tableHtml += `
                        <tr style="border-bottom: 1px solid #21262d;">
                            <td style="padding: 12px; color: #c9d1d9; font-weight: 600;">${biz.business_name}</td>
                            <td style="padding: 12px; text-align: right; color: #3fb950; font-weight: 600; font-size: 15px;">$${biz.revenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                            <td style="padding: 12px; text-align: right; color: #8b949e;">${biz.market_share}%</td>
                            <td style="padding: 12px; text-align: right; color: #8b949e;">${biz.invoice_count}</td>
                            <td style="padding: 12px; text-align: right; color: #8b949e;">$${biz.avg_invoice_value.toFixed(2)}</td>
                            <td style="padding: 12px; text-align: right; color: #d29922;">$${biz.outstanding.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                            <td style="padding: 12px; text-align: right; color: #8b949e;">${biz.collection_days} days</td>
                            ${yoyMetrics ? `<td style="padding: 12px; text-align: right; color: ${yoyMetrics.color}; font-weight: 600;">${yoyMetrics.formatted}</td>` : ''}
                        </tr>
                    `;
                });

                tableHtml += `</tbody></table></div>`;
                document.getElementById('business-comparison-table').innerHTML = tableHtml;

                // Automated Alerts
                const alerts = [];
                data.businesses.forEach(biz => {
                    if (biz.comparison && biz.comparison.revenue_change_pct < -5) {
                        alerts.push({
                            type: 'danger',
                            icon: 'exclamation-triangle',
                            text: `${biz.business_name} revenue down ${Math.abs(biz.comparison.revenue_change_pct).toFixed(1)}% ${data.compare_to === 'yoy' ? 'YoY' : 'vs previous period'} - investigate immediately`
                        });
                    }
                    if (biz.collection_days > 60) {
                        alerts.push({
                            type: 'warning',
                            icon: 'clock',
                            text: `${biz.business_name} collection days at ${biz.collection_days} - focus on AR collection`
                        });
                    }
                });

                if (alerts.length > 0) {
                    let alertsHtml = `
                        <div style="background: #161b22; padding: 20px; border-radius: 8px; border: 1px solid #30363d;">
                            <h3 style="margin: 0 0 16px 0; font-size: 16px; color: #c9d1d9; display: flex; align-items: center; gap: 8px;">
                                <i class="fas fa-bell" style="color: #f85149;"></i> Automated Alerts
                            </h3>
                            <div style="display: flex; flex-direction: column; gap: 12px;">
                    `;
                    alerts.forEach(alert => {
                        const bgColor = alert.type === 'danger' ? 'rgba(248, 81, 73, 0.1)' : 'rgba(210, 153, 34, 0.1)';
                        const borderColor = alert.type === 'danger' ? '#f85149' : '#d29922';
                        const iconColor = alert.type === 'danger' ? '#f85149' : '#d29922';
                        alertsHtml += `
                            <div style="padding: 12px 16px; background: ${bgColor}; border-left: 3px solid ${borderColor}; border-radius: 4px; display: flex; align-items: center; gap: 12px;">
                                <i class="fas fa-${alert.icon}" style="color: ${iconColor}; font-size: 16px;"></i>
                                <span style="color: #c9d1d9; font-size: 14px;">${alert.text}</span>
                            </div>
                        `;
                    });
                    alertsHtml += `</div></div>`;
                    document.getElementById('business-comparison-alerts').innerHTML = alertsHtml;
                }

                // Store data for export
                this.lastBusinessComparisonData = data;

            } catch (error) {
                resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
            }
        };

        // Initialize date picker
        this.createDateRangePicker('business-comparison-date-picker', loadData);

        // Add export button
        this.createExportButton(
            'xero-reports-results',
            async () => this.lastBusinessComparisonData || {},
            'Business Comparison Dashboard',
            '/api/xero/reports/business-comparison-enhanced'
        );

        // Add Quick Prompts button
        XeroQuickPrompts.createQuickPromptsButton(
            'xero-reports-results',
            'Business Comparison',
            () => this.lastBusinessComparisonData || null,
            '/api/xero/reports/business-comparison-enhanced'
        );
    }

    async showConsolidatedRevenue() {
        const resultsDiv = document.querySelector('#xero-reports-results');
        if (!resultsDiv) return;

        resultsDiv.innerHTML = `
            <div style="padding: 20px;">
                <h3 style="color: #c9d1d9; margin-bottom: 20px;">
                    <i class="fas fa-layer-group" style="color: #13B5EA; margin-right: 8px;"></i>
                    Consolidated Revenue Dashboard
                </h3>
                
                <div id="consolidated-revenue-date-picker"></div>
                <div id="consolidated-revenue-kpis" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px;"></div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 24px;">
                    <div id="consolidated-revenue-waterfall-chart" style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 16px;"></div>
                    <div id="consolidated-revenue-trend-chart" style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 16px;"></div>
                </div>
                <div id="consolidated-revenue-cashflow-chart" style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 16px; margin-bottom: 24px;"></div>
                <div id="consolidated-revenue-table"></div>
            </div>
        `;

        const loadData = async (dateRange, compareType) => {
            // Show loading spinner
            const kpisDiv = document.getElementById('consolidated-revenue-kpis');
            if (kpisDiv) kpisDiv.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #8b949e;"><i class="fas fa-spinner fa-spin" style="font-size: 24px;"></i><br><br>Loading consolidated revenue data...</div>';

            try {
                const params = new URLSearchParams({
                    from_date: dateRange.from,
                    to_date: dateRange.to,
                    compare_to: compareType || 'none'
                });

                if (dateRange.compare_from && dateRange.compare_to) {
                    params.set('compare_from', dateRange.compare_from);
                    params.set('compare_to_date', dateRange.compare_to);
                }

                const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/consolidated-revenue-enhanced?${params}`);
                const data = await response.json();
                if (!data.success) throw new Error(data.error);

                // Render KPI Cards
                const kpisHtml = `
                    <div style="padding: 20px; background: linear-gradient(135deg, #238636 0%, #2ea043 100%); border-radius: 6px; box-shadow: 0 2px 8px rgba(35, 134, 54, 0.3);">
                        <div style="font-size: 12px; color: rgba(255,255,255,0.8); margin-bottom: 4px;">Total Revenue</div>
                        <div style="font-size: 28px; color: white; font-weight: 700; margin-bottom: 4px;">$${(data.consolidated.total_revenue / 1000).toFixed(1)}k</div>
                        ${data.consolidated.comparison ? `<div style="font-size: 12px; color: rgba(255,255,255,0.9);">${this.calculateYoYMetrics(data.consolidated.total_revenue, data.consolidated.comparison.total_revenue).formatted}</div>` : ''}
                    </div>
                    <div style="padding: 20px; background: linear-gradient(135deg, #d29922 0%, #e2a329 100%); border-radius: 6px; box-shadow: 0 2px 8px rgba(210, 153, 34, 0.3);">
                        <div style="font-size: 12px; color: rgba(255,255,255,0.8); margin-bottom: 4px;">Total Outstanding</div>
                        <div style="font-size: 28px; color: white; font-weight: 700; margin-bottom: 4px;">$${(data.consolidated.total_outstanding / 1000).toFixed(1)}k</div>
                        ${data.consolidated.comparison ? `<div style="font-size: 12px; color: rgba(255,255,255,0.9);">${this.calculateYoYMetrics(data.consolidated.total_outstanding, data.consolidated.comparison.total_outstanding).formatted}</div>` : ''}
                    </div>
                    <div style="padding: 20px; background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%); border-radius: 6px; box-shadow: 0 2px 8px rgba(31, 111, 235, 0.3);">
                        <div style="font-size: 12px; color: rgba(255,255,255,0.8); margin-bottom: 4px;">Avg Monthly</div>
                        <div style="font-size: 28px; color: white; font-weight: 700;">$${(data.consolidated.total_revenue / 12 / 1000).toFixed(1)}k</div>
                    </div>
                    <div style="padding: 20px; background: linear-gradient(135deg, #8957e5 0%, #9b6df7 100%); border-radius: 6px; box-shadow: 0 2px 8px rgba(137, 87, 229, 0.3);">
                        <div style="font-size: 12px; color: rgba(255,255,255,0.8); margin-bottom: 4px;">Total Invoices</div>
                        <div style="font-size: 28px; color: white; font-weight: 700;">${data.consolidated.total_invoice_count}</div>
                    </div>
                `;
                document.getElementById('consolidated-revenue-kpis').innerHTML = kpisHtml;

                // Waterfall Chart - Business Contributions
                const businesses = data.consolidated.businesses;
                this.createChart('consolidated-revenue-waterfall-chart', [{
                    x: businesses.map(b => b.business_name),
                    y: businesses.map(b => b.revenue),
                    type: 'bar',
                    marker: { color: ['#238636', '#1f6feb', '#8957e5'] },
                    text: businesses.map(b => `$${(b.revenue / 1000).toFixed(1)}k (${b.percentage_of_total}%)`),
                    textposition: 'outside'
                }], {
                    title: { text: 'Revenue by Business', font: { size: 16 } },
                    xaxis: { title: 'Business' },
                    yaxis: { title: 'Revenue ($)' },
                    showlegend: false,
                    height: 400,
                    autosize: true
                });

                // Monthly Trend Chart
                const monthlyData = data.monthly_trends;
                const traces = [{
                    x: monthlyData.map(m => m.month),
                    y: monthlyData.map(m => m.current),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Current Period',
                    line: { color: '#13B5EA', width: 3 },
                    marker: { size: 8 }
                }];

                if (compareType !== 'none' && monthlyData.some(m => m.comparison !== null)) {
                    traces.push({
                        x: monthlyData.map(m => m.month),
                        y: monthlyData.map(m => m.comparison),
                        type: 'scatter',
                        mode: 'lines+markers',
                        name: 'Comparison Period',
                        line: { color: '#8b949e', width: 2, dash: 'dash' },
                        marker: { size: 6 }
                    });
                }

                this.createChart('consolidated-revenue-trend-chart', traces, {
                    title: { text: 'Monthly Revenue Trend', font: { size: 16 } },
                    xaxis: { title: 'Month' },
                    yaxis: { title: 'Revenue ($)' },
                    height: 400,
                    autosize: true
                });

                // Cash Flow Projection Chart
                const cashFlow = data.cash_flow_projection;
                this.createChart('consolidated-revenue-cashflow-chart', [{
                    x: Object.keys(cashFlow),
                    y: Object.values(cashFlow),
                    type: 'bar',
                    marker: {
                        color: ['#238636', '#d29922', '#f85149', '#8b1000']
                    },
                    text: Object.values(cashFlow).map(v => `$${(v / 1000).toFixed(1)}k`),
                    textposition: 'outside'
                }], {
                    title: { text: 'Cash Flow Projection (Outstanding by Age)', font: { size: 16 } },
                    xaxis: { title: 'Aging Bucket (Days)' },
                    yaxis: { title: 'Outstanding Amount ($)' },
                    showlegend: false,
                    height: 400,
                    autosize: true
                });

                // Business Contribution Table
                const tableData = businesses.map(b => ({
                    business: b.business_name,
                    revenue: b.revenue,
                    outstanding: b.outstanding,
                    invoices: b.invoice_count,
                    percentage: b.percentage_of_total,
                    yoy_growth: b.comparison ? this.calculateYoYMetrics(b.revenue, b.comparison.revenue).formatted : 'N/A'
                }));

                new Tabulator('#consolidated-revenue-table', {
                    data: tableData,
                    layout: 'fitColumns',
                    columns: [
                        { title: 'Business', field: 'business', minWidth: 150 },
                        { title: 'Revenue', field: 'revenue', formatter: 'money', formatterParams: { precision: 2 }, minWidth: 120 },
                        { title: 'Outstanding', field: 'outstanding', formatter: 'money', formatterParams: { precision: 2 }, minWidth: 120 },
                        { title: 'Invoices', field: 'invoices', minWidth: 100 },
                        { title: '% of Total', field: 'percentage', formatter: cell => `${cell.getValue()}%`, minWidth: 110 },
                        { title: 'YoY Growth', field: 'yoy_growth', minWidth: 120 }
                    ]
                });

                // Store data for export
                this.lastConsolidatedRevenueData = data;

            } catch (error) {
                resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
            }
        };

        this.createDateRangePicker('consolidated-revenue-date-picker', loadData);
        loadData({ from: this.getDateRangeStart(12), to: new Date().toISOString().split('T')[0] }, 'none');

        // Add export button
        this.createExportButton(
            'xero-reports-results',
            async () => this.lastConsolidatedRevenueData || {},
            'Consolidated Revenue Dashboard',
            '/api/xero/reports/consolidated-revenue-enhanced'
        );

        // Add Quick Prompts button
        XeroQuickPrompts.createQuickPromptsButton(
            'xero-reports-results',
            'Consolidated Revenue',
            () => this.lastConsolidatedRevenueData || null,
            '/api/xero/reports/consolidated-revenue-enhanced'
        );
    }

    async showCustomerOverlap() {
        const resultsDiv = document.querySelector('#xero-reports-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading customer overlap...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/customer-overlap`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Customer Overlap Analysis <i class="fas fa-info-circle xero-info-icon" data-tooltip="product-customer-overlap"></i> <span style="font-size: 12px; color: #8b949e; font-weight: normal; margin-left: 8px;">All Time</span></h4><div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;"><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e;">Total Customers</div><div style="font-size: 20px; color: #c9d1d9; font-weight: 600;">${data.total_unique_customers}</div></div><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e;">Overlapping</div><div style="font-size: 20px; color: #1f6feb; font-weight: 600;">${data.overlapping_customer_count}</div></div><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e;">Overlap %</div><div style="font-size: 20px; color: #8957e5; font-weight: 600;">${data.overlap_percentage}%</div></div></div></div>`;
            resultsDiv.innerHTML = html;

            // Refresh tooltips for info icon
            this.refreshTooltips();
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showRevenueByProduct() {
        const resultsDiv = document.querySelector('#xero-reports-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading revenue by product...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/revenue-by-product?business_id=${this.currentBusiness}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Revenue by Product/Service <i class="fas fa-info-circle xero-info-icon" data-tooltip="revenue-by-product"></i> <span style="font-size: 12px; color: #8b949e; font-weight: normal; margin-left: 8px;">All Time</span></h4><table style="width: 100%; border-collapse: collapse;"><thead><tr style="border-bottom: 1px solid #30363d;"><th style="text-align: left; padding: 8px;">Product</th><th style="text-align: right; padding: 8px;">Quantity</th><th style="text-align: right; padding: 8px;">Revenue</th></tr></thead><tbody>`;
            data.products.slice(0, 20).forEach(product => {
                html += `<tr style="border-bottom: 1px solid #30363d;"><td style="padding: 8px; color: #c9d1d9;">${product.product}</td><td style="padding: 8px; text-align: right; color: #8b949e;">${product.quantity_sold}</td><td style="padding: 8px; text-align: right; color: #238636; font-weight: 600;">$${product.revenue.toFixed(2)}</td></tr>`;
            });
            html += `</tbody></table></div>`;
            resultsDiv.innerHTML = html;

            // Refresh tooltips for info icon
            this.refreshTooltips();
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showSeasonality() {
        const resultsDiv = document.querySelector('#xero-reports-results');
        if (!resultsDiv) return;

        resultsDiv.innerHTML = `
            <div style="padding: 20px;">
                <h3 style="color: #c9d1d9; margin-bottom: 20px;">
                    <i class="fas fa-calendar-alt" style="color: #13B5EA; margin-right: 8px;"></i>
                    Seasonality Analysis Dashboard
                </h3>
                
                <div style="margin-bottom: 16px;">
                    <label style="font-size: 12px; color: #8b949e; margin-right: 8px;">Years of History:</label>
                    <select id="seasonality-years" style="padding: 6px 12px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #c9d1d9;">
                        <option value="2">2 Years</option>
                        <option value="3" selected>3 Years</option>
                        <option value="5">5 Years</option>
                    </select>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px;">
                    <div id="seasonality-current-month" style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;"></div>
                    <div id="seasonality-peak-month" style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;"></div>
                    <div id="seasonality-slow-month" style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;"></div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px;">
                    <div id="seasonality-heatmap" style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 16px;"></div>
                    <div id="seasonality-bar-chart" style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 16px;"></div>
                </div>
                
                <div id="seasonality-insights" style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 16px; margin-bottom: 24px;"></div>
                <div id="seasonality-table"></div>
            </div>
        `;

        const loadData = async (years = 3) => {
            // Show loading spinner
            const currentMonthDiv = document.getElementById('seasonality-current-month');
            if (currentMonthDiv) currentMonthDiv.innerHTML = '<div style="text-align: center; padding: 20px; color: #8b949e;"><i class="fas fa-spinner fa-spin"></i></div>';

            try {
                const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/seasonality-enhanced?business_id=${this.currentBusiness}&years=${years}`);
                const data = await response.json();
                if (!data.success) throw new Error(data.error);

                // Current Month Stats Card
                const currentMonthHtml = `
                    <div style="font-size: 12px; color: #8b949e; margin-bottom: 8px;">
                        <i class="fas fa-calendar-check" style="margin-right: 4px;"></i> ${data.current_month_stats.month}
                    </div>
                    <div style="font-size: 24px; color: #13B5EA; font-weight: 700; margin-bottom: 8px;">
                        $${(data.current_month_stats.revenue / 1000).toFixed(1)}k
                    </div>
                    <div style="font-size: 12px; color: ${data.current_month_stats.variance_pct > 0 ? '#3fb950' : '#f85149'};">
                        ${data.current_month_stats.variance_pct > 0 ? '⬆' : '⬇'} ${Math.abs(data.current_month_stats.variance_pct).toFixed(1)}% vs Avg
                    </div>
                `;
                document.getElementById('seasonality-current-month').innerHTML = currentMonthHtml;

                // Peak Month Card
                const peakMonth = data.peak_months[0];
                const peakMonthHtml = `
                    <div style="font-size: 12px; color: #8b949e; margin-bottom: 8px;">
                        <i class="fas fa-arrow-up" style="margin-right: 4px;"></i> Peak Month
                    </div>
                    <div style="font-size: 20px; color: #3fb950; font-weight: 700; margin-bottom: 4px;">
                        ${peakMonth.month_name}
                    </div>
                    <div style="font-size: 14px; color: #c9d1d9;">
                        $${(peakMonth.avg_revenue / 1000).toFixed(1)}k avg
                    </div>
                `;
                document.getElementById('seasonality-peak-month').innerHTML = peakMonthHtml;

                // Slow Month Card
                const slowMonth = data.slow_months[0];
                const slowMonthHtml = `
                    <div style="font-size: 12px; color: #8b949e; margin-bottom: 8px;">
                        <i class="fas fa-arrow-down" style="margin-right: 4px;"></i> Slowest Month
                    </div>
                    <div style="font-size: 20px; color: #f85149; font-weight: 700; margin-bottom: 4px;">
                        ${slowMonth.month_name}
                    </div>
                    <div style="font-size: 14px; color: #c9d1d9;">
                        $${(slowMonth.avg_revenue / 1000).toFixed(1)}k avg
                    </div>
                `;
                document.getElementById('seasonality-slow-month').innerHTML = slowMonthHtml;

                // Heatmap - Years x Months
                const heatmapData = [];
                const monthlyBreakdown = data.monthly_breakdown;
                const yearsList = [...new Set(monthlyBreakdown.map(m => m.year))].sort();
                const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

                const revenueMatrix = yearsList.map(year =>
                    months.map((_, monthIdx) => {
                        const monthData = monthlyBreakdown.find(m => m.year === year && m.month === monthIdx + 1);
                        return monthData ? monthData.revenue : 0;
                    })
                );

                this.createChart('seasonality-heatmap', [{
                    z: revenueMatrix,
                    x: months,
                    y: yearsList,
                    type: 'heatmap',
                    colorscale: [
                        [0, '#0d1117'],
                        [0.25, '#1f6feb'],
                        [0.5, '#13B5EA'],
                        [0.75, '#3fb950'],
                        [1, '#238636']
                    ],
                    hovertemplate: '%{y} %{x}: $%{z:,.0f}<extra></extra>'
                }], {
                    title: { text: 'Revenue Heatmap (Years × Months)', font: { size: 14 } },
                    xaxis: { title: 'Month' },
                    yaxis: { title: 'Year' },
                    height: 400,
                    autosize: true
                });

                // Bar Chart - Average by Month with Variance
                const seasonalPattern = data.seasonal_pattern;
                this.createChart('seasonality-bar-chart', [{
                    x: seasonalPattern.map(m => m.month_name),
                    y: seasonalPattern.map(m => m.avg_revenue),
                    type: 'bar',
                    marker: {
                        color: seasonalPattern.map(m => {
                            const avg = seasonalPattern.reduce((sum, x) => sum + x.avg_revenue, 0) / seasonalPattern.length;
                            return m.avg_revenue > avg * 1.1 ? '#3fb950' : m.avg_revenue < avg * 0.9 ? '#f85149' : '#13B5EA';
                        })
                    },
                    text: seasonalPattern.map(m => `$${(m.avg_revenue / 1000).toFixed(1)}k`),
                    textposition: 'outside',
                    error_y: {
                        type: 'data',
                        array: seasonalPattern.map(m => m.variance / 2),
                        color: '#8b949e'
                    }
                }], {
                    title: { text: 'Average Revenue by Month (with Variance)', font: { size: 14 } },
                    xaxis: { title: 'Month' },
                    yaxis: { title: 'Average Revenue ($)' },
                    showlegend: false,
                    height: 400,
                    autosize: true
                });

                // Insights Section
                const insightsHtml = `
                    <h4 style="color: #c9d1d9; margin: 0 0 12px 0;">
                        <i class="fas fa-lightbulb" style="color: #d29922;"></i> Seasonal Insights
                    </h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div style="padding: 12px; background: rgba(63, 185, 80, 0.1); border-left: 3px solid #3fb950; border-radius: 4px;">
                            <div style="font-size: 12px; color: #3fb950; font-weight: 600; margin-bottom: 4px;">PEAK SEASON</div>
                            <div style="font-size: 13px; color: #c9d1d9;">
                                ${data.peak_months.map(m => m.month_name).join(', ')} perform strongest 
                                (${((data.peak_months[0].avg_revenue / (seasonalPattern.reduce((s, m) => s + m.avg_revenue, 0) / seasonalPattern.length) - 1) * 100).toFixed(0)}% above average)
                            </div>
                        </div>
                        <div style="padding: 12px; background: rgba(248, 81, 73, 0.1); border-left: 3px solid #f85149; border-radius: 4px;">
                            <div style="font-size: 12px; color: #f85149; font-weight: 600; margin-bottom: 4px;">SLOW SEASON</div>
                            <div style="font-size: 13px; color: #c9d1d9;">
                                ${data.slow_months.map(m => m.month_name).join(', ')} need marketing support
                                (${((1 - data.slow_months[0].avg_revenue / (seasonalPattern.reduce((s, m) => s + m.avg_revenue, 0) / seasonalPattern.length)) * 100).toFixed(0)}% below average)
                            </div>
                        </div>
                    </div>
                `;
                document.getElementById('seasonality-insights').innerHTML = insightsHtml;

                // Detailed Table
                const tableData = seasonalPattern.map(m => ({
                    month: m.month_name,
                    avg_revenue: m.avg_revenue,
                    min_revenue: m.min_revenue,
                    max_revenue: m.max_revenue,
                    variance: m.variance,
                    yoy_change: m.yoy_change !== undefined ? `${m.yoy_change > 0 ? '⬆' : '⬇'} ${Math.abs(m.yoy_change).toFixed(1)}%` : 'N/A'
                }));

                new Tabulator('#seasonality-table', {
                    data: tableData,
                    layout: 'fitColumns',
                    columns: [
                        { title: 'Month', field: 'month', minWidth: 100 },
                        { title: 'Avg Revenue', field: 'avg_revenue', formatter: 'money', formatterParams: { precision: 0 }, minWidth: 120 },
                        { title: 'Min', field: 'min_revenue', formatter: 'money', formatterParams: { precision: 0 }, minWidth: 100 },
                        { title: 'Max', field: 'max_revenue', formatter: 'money', formatterParams: { precision: 0 }, minWidth: 100 },
                        { title: 'Variance', field: 'variance', formatter: 'money', formatterParams: { precision: 0 }, minWidth: 100 },
                        { title: 'YoY Change', field: 'yoy_change', minWidth: 110 }
                    ]
                });

                // Store data for export
                this.lastSeasonalityData = data;

            } catch (error) {
                resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
            }
        };

        document.getElementById('seasonality-years').addEventListener('change', (e) => {
            loadData(parseInt(e.target.value));
        });

        loadData(3);

        // Add export button
        this.createExportButton(
            'xero-reports-results',
            async () => this.lastSeasonalityData || {},
            'Seasonality Analysis Dashboard',
            '/api/xero/reports/seasonality-enhanced'
        );

        // Add Quick Prompts button
        XeroQuickPrompts.createQuickPromptsButton(
            'xero-reports-results',
            'Seasonality',
            () => this.lastSeasonalityData || null,
            '/api/xero/reports/seasonality-enhanced'
        );
    }

    async showForecast() {
        const resultsDiv = document.querySelector('#xero-reports-results');
        if (!resultsDiv) return;

        resultsDiv.innerHTML = `
            <div style="padding: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h3 style="color: #c9d1d9; margin: 0;">
                        <i class="fas fa-chart-line" style="color: #13B5EA; margin-right: 8px;"></i>
                        Revenue Forecast Dashboard
                    </h3>
                    <span id="forecast-method-badge" style="padding: 6px 16px; background: rgba(31, 111, 235, 0.15); border: 1px solid #1f6feb; border-radius: 4px; color: #1f6feb; font-size: 12px; font-weight: 600;">
                        <i class="fas fa-robot"></i> Loading...
                    </span>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;">
                    <div>
                        <label style="font-size: 12px; color: #8b949e; margin-right: 8px;">Historical Months:</label>
                        <select id="forecast-historical" style="width: 100%; padding: 6px 12px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #c9d1d9;">
                            <option value="6">6 Months</option>
                            <option value="12" selected>12 Months</option>
                            <option value="24">24 Months</option>
                        </select>
                    </div>
                    <div>
                        <label style="font-size: 12px; color: #8b949e; margin-right: 8px;">Forecast Period:</label>
                        <select id="forecast-period" style="width: 100%; padding: 6px 12px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #c9d1d9;">
                            <option value="3">3 Months</option>
                            <option value="6" selected>6 Months</option>
                            <option value="12">12 Months</option>
                        </select>
                    </div>
                    <div>
                        <label style="font-size: 12px; color: #8b949e; margin-right: 8px;">Scenario View:</label>
                        <select id="forecast-scenario" style="width: 100%; padding: 6px 12px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #c9d1d9;">
                            <option value="base" selected>Base Case</option>
                            <option value="optimistic">Optimistic</option>
                            <option value="pessimistic">Pessimistic</option>
                            <option value="all">All Scenarios</option>
                        </select>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px;">
                    <div id="forecast-total-kpi" style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;"></div>
                    <div id="forecast-growth-kpi" style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;"></div>
                    <div id="forecast-confidence-kpi" style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;"></div>
                </div>
                
                <div id="forecast-chart" style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 16px; margin-bottom: 24px; min-height: 500px;"></div>
                
                <div id="forecast-risks" style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 16px; margin-bottom: 24px;"></div>
                
                <div id="forecast-table"></div>
            </div>
        `;

        const loadData = async (historicalMonths = 12, forecastMonths = 6) => {
            // Show loading spinner
            const kpiDiv = document.getElementById('forecast-total-kpi');
            if (kpiDiv) kpiDiv.innerHTML = '<div style="text-align: center; padding: 20px; color: #8b949e;"><i class="fas fa-spinner fa-spin"></i></div>';

            try {
                const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/forecast-enhanced?business_id=${this.currentBusiness}&historical_months=${historicalMonths}&forecast_months=${forecastMonths}`);
                const data = await response.json();
                if (!data.success) throw new Error(data.error);

                // Update method badge
                const methodBadge = document.getElementById('forecast-method-badge');
                if (methodBadge) {
                    const isSARIMA = data.method.includes('SARIMA');
                    const isARIMA = data.method.includes('ARIMA') && !isSARIMA;
                    const isML = isSARIMA || isARIMA;

                    methodBadge.innerHTML = isML
                        ? `<i class="fas fa-robot"></i> ${data.method}`
                        : `<i class="fas fa-calculator"></i> ${data.method}`;
                    methodBadge.style.background = isML ? 'rgba(63, 185, 80, 0.15)' : 'rgba(210, 153, 34, 0.15)';
                    methodBadge.style.borderColor = isML ? '#3fb950' : '#d29922';
                    methodBadge.style.color = isML ? '#3fb950' : '#d29922';
                }

                // KPI Cards
                document.getElementById('forecast-total-kpi').innerHTML = `
                    <div style="font-size: 12px; color: #8b949e; margin-bottom: 8px;">
                        <i class="fas fa-dollar-sign"></i> ${forecastMonths}-Month Forecast
                    </div>
                    <div style="font-size: 26px; color: #1f6feb; font-weight: 700;">
                        $${(data.total_forecast_base / 1000).toFixed(1)}k
                    </div>
                    <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">
                        Range: $${(data.total_forecast_pessimistic / 1000).toFixed(1)}k - $${(data.total_forecast_optimistic / 1000).toFixed(1)}k
                    </div>
                `;

                document.getElementById('forecast-growth-kpi').innerHTML = `
                    <div style="font-size: 12px; color: #8b949e; margin-bottom: 8px;">
                        <i class="fas fa-percentage"></i> Avg Monthly Growth
                    </div>
                    <div style="font-size: 26px; color: ${data.avg_growth_rate >= 0 ? '#3fb950' : '#f85149'}; font-weight: 700;">
                        ${data.avg_growth_rate >= 0 ? '⬆' : '⬇'} ${Math.abs(data.avg_growth_rate).toFixed(1)}%
                    </div>
                    <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">
                        Based on ${historicalMonths} months
                    </div>
                `;

                const avgConfidence = data.forecast.reduce((sum, f) => sum + f.confidence, 0) / data.forecast.length;
                document.getElementById('forecast-confidence-kpi').innerHTML = `
                    <div style="font-size: 12px; color: #8b949e; margin-bottom: 8px;">
                        <i class="fas fa-check-circle"></i> Avg Confidence
                    </div>
                    <div style="font-size: 26px; color: ${avgConfidence > 70 ? '#3fb950' : avgConfidence > 50 ? '#d29922' : '#f85149'}; font-weight: 700;">
                        ${avgConfidence.toFixed(0)}%
                    </div>
                    <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">
                        Volatility: ±${data.volatility.toFixed(1)}%
                    </div>
                `;

                // Forecast Chart with Confidence Bands
                const scenario = document.getElementById('forecast-scenario').value;
                const historicalData = data.historical_data;
                const forecastData = data.forecast;

                const traces = [];

                // Historical line (solid)
                traces.push({
                    x: historicalData.map(h => h.month),
                    y: historicalData.map(h => h.revenue),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Historical',
                    line: { color: '#c9d1d9', width: 3 },
                    marker: { size: 6 }
                });

                // Forecast scenarios
                if (scenario === 'all') {
                    // Show all three lines with distinct styling
                    traces.push({
                        x: forecastData.map(f => f.month_name),
                        y: forecastData.map(f => f.base),
                        type: 'scatter',
                        mode: 'lines+markers',
                        name: 'Base Forecast',
                        line: { color: '#1f6feb', width: 3, dash: 'solid' },
                        marker: { size: 8, symbol: 'circle' }
                    });

                    traces.push({
                        x: forecastData.map(f => f.month_name),
                        y: forecastData.map(f => f.optimistic),
                        type: 'scatter',
                        mode: 'lines+markers',
                        name: 'Optimistic',
                        line: { color: '#3fb950', width: 2, dash: 'dash' },
                        marker: { size: 6, symbol: 'triangle-up' }
                    });

                    traces.push({
                        x: forecastData.map(f => f.month_name),
                        y: forecastData.map(f => f.pessimistic),
                        type: 'scatter',
                        mode: 'lines+markers',
                        name: 'Pessimistic',
                        line: { color: '#f85149', width: 2, dash: 'dash' },
                        marker: { size: 6, symbol: 'triangle-down' }
                    });
                } else if (scenario === 'base') {
                    traces.push({
                        x: forecastData.map(f => f.month_name),
                        y: forecastData.map(f => f.base),
                        type: 'scatter',
                        mode: 'lines+markers',
                        name: 'Base Forecast',
                        line: { color: '#1f6feb', width: 3, dash: 'dash' },
                        marker: { size: 8 }
                    });
                } else if (scenario === 'optimistic') {
                    traces.push({
                        x: forecastData.map(f => f.month_name),
                        y: forecastData.map(f => f.optimistic),
                        type: 'scatter',
                        mode: 'lines+markers',
                        name: 'Optimistic',
                        line: { color: '#3fb950', width: 3, dash: 'dash' },
                        marker: { size: 8 }
                    });
                } else if (scenario === 'pessimistic') {
                    traces.push({
                        x: forecastData.map(f => f.month_name),
                        y: forecastData.map(f => f.pessimistic),
                        type: 'scatter',
                        mode: 'lines+markers',
                        name: 'Pessimistic',
                        line: { color: '#f85149', width: 3, dash: 'dash' },
                        marker: { size: 8 }
                    });
                }

                // Confidence band (fill between optimistic and pessimistic)
                if (scenario === 'all' || scenario === 'base') {
                    traces.push({
                        x: [...forecastData.map(f => f.month_name), ...forecastData.map(f => f.month_name).reverse()],
                        y: [...forecastData.map(f => f.optimistic), ...forecastData.map(f => f.pessimistic).reverse()],
                        fill: 'toself',
                        fillcolor: 'rgba(31, 111, 235, 0.1)',
                        line: { color: 'transparent' },
                        name: 'Confidence Band',
                        showlegend: true
                    });
                }

                this.createChart('forecast-chart', traces, {
                    title: { text: 'Revenue Forecast with Confidence Intervals', font: { size: 16 } },
                    xaxis: { title: 'Month' },
                    yaxis: { title: 'Revenue ($)' },
                    height: 500,
                    autosize: true
                });

                // Risk Factors
                let risksHtml = '<h4 style="color: #c9d1d9; margin: 0 0 12px 0;"><i class="fas fa-exclamation-triangle" style="color: #d29922;"></i> Risk Factors</h4>';
                if (data.risk_factors && data.risk_factors.length > 0) {
                    risksHtml += '<div style="display: flex; flex-direction: column; gap: 8px;">';
                    data.risk_factors.forEach(risk => {
                        const colors = {
                            'danger': { bg: 'rgba(248, 81, 73, 0.1)', border: '#f85149', icon: 'fa-times-circle' },
                            'warning': { bg: 'rgba(210, 153, 34, 0.1)', border: '#d29922', icon: 'fa-exclamation-circle' },
                            'info': { bg: 'rgba(19, 181, 234, 0.1)', border: '#13B5EA', icon: 'fa-info-circle' }
                        };
                        const style = colors[risk.type] || colors.info;
                        risksHtml += `
                            <div style="padding: 12px; background: ${style.bg}; border-left: 3px solid ${style.border}; border-radius: 4px;">
                                <i class="fas ${style.icon}" style="color: ${style.border}; margin-right: 8px;"></i>
                                <span style="color: #c9d1d9;">${risk.text}</span>
                            </div>
                        `;
                    });
                    risksHtml += '</div>';
                } else {
                    risksHtml += '<div style="color: #8b949e; font-size: 14px;">No significant risk factors identified.</div>';
                }
                document.getElementById('forecast-risks').innerHTML = risksHtml;

                // Forecast Table
                const tableData = forecastData.map(f => ({
                    month: f.month_name,
                    base: f.base,
                    optimistic: f.optimistic,
                    pessimistic: f.pessimistic,
                    confidence: `${f.confidence}%`,
                    range: `$${((f.optimistic - f.pessimistic) / 1000).toFixed(1)}k`
                }));

                new Tabulator('#forecast-table', {
                    data: tableData,
                    layout: 'fitColumns',
                    columns: [
                        { title: 'Month', field: 'month', minWidth: 120 },
                        { title: 'Base Forecast', field: 'base', formatter: 'money', formatterParams: { precision: 0 }, minWidth: 130 },
                        { title: 'Optimistic', field: 'optimistic', formatter: 'money', formatterParams: { precision: 0 }, minWidth: 120 },
                        { title: 'Pessimistic', field: 'pessimistic', formatter: 'money', formatterParams: { precision: 0 }, minWidth: 120 },
                        { title: 'Confidence', field: 'confidence', minWidth: 100 },
                        { title: 'Range', field: 'range', minWidth: 100 }
                    ]
                });

                // Store data for export
                this.lastForecastData = data;

            } catch (error) {
                resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
            }
        };

        document.getElementById('forecast-historical').addEventListener('change', () => {
            loadData(
                parseInt(document.getElementById('forecast-historical').value),
                parseInt(document.getElementById('forecast-period').value)
            );
        });

        document.getElementById('forecast-period').addEventListener('change', () => {
            loadData(
                parseInt(document.getElementById('forecast-historical').value),
                parseInt(document.getElementById('forecast-period').value)
            );
        });

        document.getElementById('forecast-scenario').addEventListener('change', () => {
            loadData(
                parseInt(document.getElementById('forecast-historical').value),
                parseInt(document.getElementById('forecast-period').value)
            );
        });

        loadData(12, 6);

        // Add export button
        this.createExportButton(
            'xero-reports-results',
            async () => this.lastForecastData || {},
            'Revenue Forecast Dashboard',
            '/api/xero/reports/forecast-enhanced'
        );

        // Add Quick Prompts button
        XeroQuickPrompts.createQuickPromptsButton(
            'xero-reports-results',
            'Forecast',
            () => this.lastForecastData || null,
            '/api/xero/reports/forecast-enhanced'
        );
    }

    // ========================================================================
    // ML PREDICTION FEATURES
    // ========================================================================

    async showPaymentRiskML() {
        console.log('[Xero] 🤖 showPaymentRiskML() STARTED');
        const resultsDiv = document.querySelector('#xero-reports-results');
        if (!resultsDiv) return;

        resultsDiv.innerHTML = `
            <div style="padding: 20px; text-align: center;">
                <i class="fas fa-robot fa-3x" style="color: #13B5EA; margin-bottom: 16px;"></i>
                <p style="color: #c9d1d9; font-size: 16px; margin: 0;">Running ML Model: Logistic Regression</p>
                <p style="color: #8b949e; font-size: 14px; margin: 8px 0 0 0;">Analyzing payment patterns...</p>
            </div>
        `;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/payment-risk-ml?business_id=${this.currentBusiness}`);
            const data = await response.json();

            if (!data.success) {
                resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${data.error}</div>`;
                return;
            }

            const highRisk = data.predictions.filter(p => p.risk > 70);
            const mediumRisk = data.predictions.filter(p => p.risk > 40 && p.risk <= 70);
            const lowRisk = data.predictions.filter(p => p.risk <= 40);

            resultsDiv.innerHTML = `
                <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                        <h3 style="margin: 0; color: #c9d1d9; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-robot" style="color: #13B5EA;"></i>
                            Payment Risk Prediction (ML)
                        </h3>
                        <div style="display: flex; gap: 12px; align-items: center;">
                            <span style="color: #8b949e; font-size: 14px;">Method: ${data.method}</span>
                            <span style="padding: 4px 12px; background: rgba(63, 185, 80, 0.15); border: 1px solid #3fb950; border-radius: 4px; color: #3fb950; font-size: 12px; font-weight: 600;">
                                ${data.accuracy}% Accurate
                            </span>
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
                        <div style="background: rgba(248, 81, 73, 0.1); border: 1px solid #f85149; border-radius: 6px; padding: 16px;">
                            <div style="font-size: 32px; font-weight: 700; color: #f85149;">${highRisk.length}</div>
                            <div style="color: #8b949e; font-size: 14px;">High Risk (>70%)</div>
                        </div>
                        <div style="background: rgba(210, 153, 34, 0.1); border: 1px solid #d29922; border-radius: 6px; padding: 16px;">
                            <div style="font-size: 32px; font-weight: 700; color: #d29922;">${mediumRisk.length}</div>
                            <div style="color: #8b949e; font-size: 14px;">Medium Risk (40-70%)</div>
                        </div>
                        <div style="background: rgba(63, 185, 80, 0.1); border: 1px solid #3fb950; border-radius: 6px; padding: 16px;">
                            <div style="font-size: 32px; font-weight: 700; color: #3fb950;">${lowRisk.length}</div>
                            <div style="color: #8b949e; font-size: 14px;">Low Risk (<40%)</div>
                        </div>
                        <div style="background: rgba(19, 181, 234, 0.1); border: 1px solid #13B5EA; border-radius: 6px; padding: 16px;">
                            <div style="font-size: 32px; font-weight: 700; color: #13B5EA;">${data.training_samples}</div>
                            <div style="color: #8b949e; font-size: 14px;">Training Samples</div>
                        </div>
                    </div>

                    <div id="payment-risk-chart" style="margin-bottom: 24px;"></div>
                    <div id="payment-risk-table"></div>
                </div>
            `;

            // Create bar chart
            const sortedPredictions = data.predictions.slice(0, 15);
            const traces = [{
                x: sortedPredictions.map(p => p.invoice_number),
                y: sortedPredictions.map(p => p.risk),
                type: 'bar',
                marker: {
                    color: sortedPredictions.map(p =>
                        p.risk > 70 ? '#f85149' :
                            p.risk > 40 ? '#d29922' : '#3fb950'
                    )
                },
                text: sortedPredictions.map(p => `${p.risk.toFixed(1)}%`),
                textposition: 'outside',
                name: 'Late Payment Risk'
            }];

            this.createChart('payment-risk-chart', traces, {
                title: { text: 'Top 15 At-Risk Invoices', font: { size: 16 } },
                xaxis: { title: 'Invoice Number' },
                yaxis: { title: 'Risk (%)', range: [0, 100] },
                height: 400
            });

            // Create table
            new Tabulator('#payment-risk-table', {
                data: data.predictions,
                layout: 'fitDataStretch',
                pagination: 'local',
                paginationSize: 20,
                columns: [
                    { title: 'Invoice #', field: 'invoice_number', minWidth: 120 },
                    { title: 'Customer', field: 'contact_name', minWidth: 200 },
                    { title: 'Amount', field: 'amount', formatter: 'money', formatterParams: { precision: 2 }, minWidth: 120 },
                    {
                        title: 'Risk',
                        field: 'risk',
                        formatter: (cell) => {
                            const value = cell.getValue();
                            const color = value > 70 ? '#f85149' : value > 40 ? '#d29922' : '#3fb950';
                            return `<span style="color: ${color}; font-weight: 600;">${value.toFixed(1)}%</span>`;
                        },
                        minWidth: 100
                    },
                    {
                        title: 'Category',
                        field: 'risk_category',
                        formatter: (cell) => {
                            const value = cell.getValue();
                            const colors = {
                                'High': { bg: 'rgba(248, 81, 73, 0.15)', text: '#f85149' },
                                'Medium': { bg: 'rgba(210, 153, 34, 0.15)', text: '#d29922' },
                                'Low': { bg: 'rgba(63, 185, 80, 0.15)', text: '#3fb950' }
                            };
                            const style = colors[value] || colors.Low;
                            return `<span style="padding: 4px 12px; background: ${style.bg}; color: ${style.text}; border-radius: 4px; font-size: 12px; font-weight: 600;">${value}</span>`;
                        },
                        minWidth: 120
                    }
                ]
            });

        } catch (error) {
            console.error('[Xero ML] Payment risk error:', error);
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showChurnRiskML() {
        console.log('[Xero] 🤖 showChurnRiskML() STARTED');
        const resultsDiv = document.querySelector('#xero-reports-results');
        if (!resultsDiv) return;

        resultsDiv.innerHTML = `
            <div style="padding: 20px; text-align: center;">
                <i class="fas fa-robot fa-3x" style="color: #d29922; margin-bottom: 16px;"></i>
                <p style="color: #c9d1d9; font-size: 16px; margin: 0;">Running ML Model: Random Forest</p>
                <p style="color: #8b949e; font-size: 14px; margin: 8px 0 0 0;">Analyzing customer behavior...</p>
            </div>
        `;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/churn-risk-ml?business_id=${this.currentBusiness}`);
            const data = await response.json();

            if (!data.success) {
                resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${data.error}</div>`;
                return;
            }

            const highRisk = data.predictions.filter(p => p.churn_risk > 70);
            const mediumRisk = data.predictions.filter(p => p.churn_risk > 40 && p.churn_risk <= 70);
            const lowRisk = data.predictions.filter(p => p.churn_risk <= 40);

            resultsDiv.innerHTML = `
                <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                        <h3 style="margin: 0; color: #c9d1d9; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-robot" style="color: #d29922;"></i>
                            Customer Churn Prediction (ML)
                        </h3>
                        <div style="display: flex; gap: 12px; align-items: center;">
                            <span style="color: #8b949e; font-size: 14px;">Method: ${data.method}</span>
                            <span style="padding: 4px 12px; background: rgba(63, 185, 80, 0.15); border: 1px solid #3fb950; border-radius: 4px; color: #3fb950; font-size: 12px; font-weight: 600;">
                                ${data.accuracy}% Accurate
                            </span>
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
                        <div style="background: rgba(248, 81, 73, 0.1); border: 1px solid #f85149; border-radius: 6px; padding: 16px;">
                            <div style="font-size: 32px; font-weight: 700; color: #f85149;">${highRisk.length}</div>
                            <div style="color: #8b949e; font-size: 14px;">High Churn Risk (>70%)</div>
                        </div>
                        <div style="background: rgba(210, 153, 34, 0.1); border: 1px solid #d29922; border-radius: 6px; padding: 16px;">
                            <div style="font-size: 32px; font-weight: 700; color: #d29922;">${mediumRisk.length}</div>
                            <div style="color: #8b949e; font-size: 14px;">Medium Risk (40-70%)</div>
                        </div>
                        <div style="background: rgba(63, 185, 80, 0.1); border: 1px solid #3fb950; border-radius: 6px; padding: 16px;">
                            <div style="font-size: 32px; font-weight: 700; color: #3fb950;">${lowRisk.length}</div>
                            <div style="color: #8b949e; font-size: 14px;">Low Risk (<40%)</div>
                        </div>
                        <div style="background: rgba(19, 181, 234, 0.1); border: 1px solid #13B5EA; border-radius: 6px; padding: 16px;">
                            <div style="font-size: 32px; font-weight: 700; color: #13B5EA;">${data.training_samples}</div>
                            <div style="color: #8b949e; font-size: 14px;">Customers Analyzed</div>
                        </div>
                    </div>

                    <div style="background: rgba(19, 181, 234, 0.05); border: 1px solid #13B5EA40; border-radius: 6px; padding: 16px; margin-bottom: 24px;">
                        <h4 style="margin: 0 0 12px 0; color: #13B5EA;">
                            <i class="fas fa-chart-bar" style="margin-right: 6px;"></i>Feature Importance (What Drives Churn?)
                        </h4>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: #c9d1d9;">Months Since Order</span>
                                <span style="color: #13B5EA; font-weight: 600;">${data.feature_importance.months_since_order}%</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: #c9d1d9;">Order Frequency</span>
                                <span style="color: #13B5EA; font-weight: 600;">${data.feature_importance.order_frequency}%</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: #c9d1d9;">Avg Order Value</span>
                                <span style="color: #13B5EA; font-weight: 600;">${data.feature_importance.avg_order_value}%</span>
                            </div>
                        </div>
                    </div>

                    <div id="churn-risk-chart" style="margin-bottom: 24px;"></div>
                    <div id="churn-risk-table"></div>
                </div>
            `;

            // Create scatter plot
            const topRisk = data.predictions.slice(0, 30);
            const traces = [{
                x: topRisk.map(p => p.months_since_order),
                y: topRisk.map(p => p.churn_risk),
                mode: 'markers',
                type: 'scatter',
                marker: {
                    size: topRisk.map(p => Math.sqrt(p.total_revenue) / 20),
                    color: topRisk.map(p =>
                        p.churn_risk > 70 ? '#f85149' :
                            p.churn_risk > 40 ? '#d29922' : '#3fb950'
                    ),
                    line: { color: '#c9d1d9', width: 1 }
                },
                text: topRisk.map(p => `${p.contact_name}<br>Risk: ${p.churn_risk.toFixed(1)}%<br>Revenue: $${p.total_revenue.toFixed(0)}`),
                hovertemplate: '%{text}<extra></extra>'
            }];

            this.createChart('churn-risk-chart', traces, {
                title: { text: 'Churn Risk vs Time Since Last Order', font: { size: 16 } },
                xaxis: { title: 'Months Since Last Order' },
                yaxis: { title: 'Churn Risk (%)', range: [0, 100] },
                height: 400
            });

            // Create table
            new Tabulator('#churn-risk-table', {
                data: data.predictions,
                layout: 'fitDataStretch',
                pagination: 'local',
                paginationSize: 20,
                columns: [
                    { title: 'Customer', field: 'contact_name', minWidth: 200 },
                    {
                        title: 'Churn Risk',
                        field: 'churn_risk',
                        formatter: (cell) => {
                            const value = cell.getValue();
                            const color = value > 70 ? '#f85149' : value > 40 ? '#d29922' : '#3fb950';
                            return `<span style="color: ${color}; font-weight: 600;">${value.toFixed(1)}%</span>`;
                        },
                        minWidth: 120
                    },
                    {
                        title: 'Category',
                        field: 'risk_category',
                        formatter: (cell) => {
                            const value = cell.getValue();
                            const colors = {
                                'High': { bg: 'rgba(248, 81, 73, 0.15)', text: '#f85149' },
                                'Medium': { bg: 'rgba(210, 153, 34, 0.15)', text: '#d29922' },
                                'Low': { bg: 'rgba(63, 185, 80, 0.15)', text: '#3fb950' }
                            };
                            const style = colors[value] || colors.Low;
                            return `<span style="padding: 4px 12px; background: ${style.bg}; color: ${style.text}; border-radius: 4px; font-size: 12px; font-weight: 600;">${value}</span>`;
                        },
                        minWidth: 120
                    },
                    {
                        title: 'Months Since Order',
                        field: 'months_since_order',
                        formatter: (cell) => cell.getValue().toFixed(1),
                        minWidth: 150
                    },
                    {
                        title: 'Order Frequency',
                        field: 'order_frequency',
                        formatter: (cell) => cell.getValue().toFixed(2) + '/mo',
                        minWidth: 150
                    },
                    { title: 'Lifetime Revenue', field: 'total_revenue', formatter: 'money', formatterParams: { precision: 0 }, minWidth: 150 }
                ]
            });

        } catch (error) {
            console.error('[Xero ML] Churn risk error:', error);
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    // ========================================================================
    // CUSTOMER INTELLIGENCE DASHBOARD (Unified View)
    // ========================================================================

    async showCustomerIntelligence() {
        const resultsDiv = document.querySelector('#xero-contacts-report-results');
        if (!resultsDiv) {
            console.log('[Xero] showCustomerIntelligence() called but #xero-contacts-report-results not found. This report is only available from the Contacts tab.');
            return;
        }

        this.lastContactReportType = 'intelligence';
        resultsDiv.innerHTML = '<div style="padding: 40px; text-align: center; color: #8b949e;"><i class="fas fa-spinner fa-spin" style="font-size: 32px;"></i><br><br>Loading Customer Intelligence Dashboard...</div>';

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/customer-intelligence?business_id=${this.currentBusiness}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);

            const { metrics, risk_distribution, segment_distribution, customers } = data;

            // Filter recommendations - only show customers with LTV >= $500 (focus on high-value clients)
            const MIN_LTV_THRESHOLD = 500;
            const recommendations = {
                urgent: (data.recommendations?.urgent || []).filter(r => !r.ltv || r.ltv >= MIN_LTV_THRESHOLD),
                this_week: (data.recommendations?.this_week || []).filter(r => !r.ltv || r.ltv >= MIN_LTV_THRESHOLD),
                this_month: (data.recommendations?.this_month || []).filter(r => !r.ltv || r.ltv >= MIN_LTV_THRESHOLD)
            };

            // Build dashboard HTML
            const html = `
                <div style="padding: 20px; background: #0d1117; border-radius: 8px;">
                    <!-- Header -->
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                        <h3 style="margin: 0; color: #c9d1d9; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-brain" style="color: #1f6feb;"></i>
                            Customer Intelligence Dashboard
                        </h3>
                        <div style="display: flex; gap: 8px;">
                            <button id="ai-export-btn" class="xero-btn xero-btn-sm" style="padding: 8px 16px; position: relative; background: linear-gradient(135deg, #8957e5 0%, #9b6df7 100%); border: 1px solid #8957e5; box-shadow: 0 2px 8px rgba(137, 87, 229, 0.3);">
                                <i class="fas fa-robot"></i> AI Export
                            </button>
                            <button id="export-intelligence" class="xero-btn xero-btn-sm" style="padding: 8px 16px;">
                                <i class="fas fa-download"></i> Export CSV
                            </button>
                            <button id="refresh-intelligence" class="xero-btn xero-btn-sm" style="padding: 8px 16px;">
                                <i class="fas fa-sync"></i> Refresh
                            </button>
                        </div>
                    </div>

                    <!-- Metrics Cards (8 cards in 2 rows) -->
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;">
                        <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; border-left: 3px solid #3fb950;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Total Customers</div>
                            <div style="font-size: 28px; color: #c9d1d9; font-weight: 700;">${metrics.total_customers.toLocaleString()}</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">All contacts</div>
                        </div>
                        <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; border-left: 3px solid #1f6feb;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Active</div>
                            <div style="font-size: 28px; color: #1f6feb; font-weight: 700;">${metrics.active}</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">${((metrics.active / metrics.total_customers) * 100).toFixed(1)}% of total</div>
                        </div>
                        <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; border-left: 3px solid #d29922;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">At-Risk</div>
                            <div style="font-size: 28px; color: #d29922; font-weight: 700;">${metrics.at_risk}</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Need attention</div>
                        </div>
                        <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; border-left: 3px solid #f85149;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Churned</div>
                            <div style="font-size: 28px; color: #f85149; font-weight: 700;">${metrics.churned}</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">90+ days inactive</div>
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px;">
                        <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Net Growth</div>
                            <div style="font-size: 28px; color: ${metrics.net_growth >= 0 ? '#3fb950' : '#f85149'}; font-weight: 700;">${metrics.net_growth >= 0 ? '+' : ''}${metrics.net_growth}</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">30-day change</div>
                        </div>
                        <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Avg LTV</div>
                            <div style="font-size: 28px; color: #c9d1d9; font-weight: 700;">$${(metrics.avg_ltv / 1000).toFixed(1)}K</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Per customer</div>
                        </div>
                        <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Payment Risk</div>
                            <div style="font-size: 28px; color: #f85149; font-weight: 700;">${metrics.late_invoices}</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Late invoices</div>
                        </div>
                        <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 6px;">Retention</div>
                            <div style="font-size: 28px; color: #d29922; font-weight: 700;">${metrics.retention_rate.toFixed(1)}%</div>
                            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">30-day rate</div>
                        </div>
                    </div>

                    <!-- Risk Distribution Bar -->
                    <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 24px;">
                        <h4 style="margin: 0 0 16px 0; color: #c9d1d9; font-size: 14px;">Risk Distribution</h4>
                        <div style="display: flex; height: 40px; border-radius: 4px; overflow: hidden; margin-bottom: 12px;">
                            <div style="flex: ${risk_distribution.high}; background: #f85149; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 14px;">
                                ${risk_distribution.high > 0 ? risk_distribution.high : ''}
                            </div>
                            <div style="flex: ${risk_distribution.medium}; background: #d29922; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 14px;">
                                ${risk_distribution.medium > 0 ? risk_distribution.medium : ''}
                            </div>
                            <div style="flex: ${risk_distribution.low}; background: #3fb950; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 14px;">
                                ${risk_distribution.low > 0 ? risk_distribution.low : ''}
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 12px; color: #8b949e;">
                            <span>🔴 High Risk: ${risk_distribution.high}</span>
                            <span>🟡 Medium Risk: ${risk_distribution.medium}</span>
                            <span>🟢 Low Risk: ${risk_distribution.low}</span>
                        </div>
                        <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #30363d; display: flex; gap: 12px; flex-wrap: wrap;">
                            ${Object.entries(segment_distribution).map(([segment, count]) => {
                const colors = {
                    'Champions': '#238636',
                    'Loyal Customers': '#1f6feb',
                    'Potential Loyalists': '#8957e5',
                    'At Risk': '#d29922',
                    'Lost': '#f85149'
                };
                return `<div class="segment-badge" data-segment="${segment}" style="padding: 6px 12px; background: ${colors[segment]}20; border: 1px solid ${colors[segment]}; border-radius: 4px; font-size: 12px; color: ${colors[segment]}; font-weight: 600; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='${colors[segment]}40'" onmouseout="this.style.background='${colors[segment]}20'">${segment}: ${count}</div>`;
            }).join('')}
                        </div>
                    </div>

                    <!-- ML Insights Panel -->
                    ${data.ml_insights ? `
                    <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 24px;">
                        <h4 style="margin: 0 0 16px 0; color: #c9d1d9; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-brain" style="color: #8957e5;"></i>
                            ML-Powered Insights
                            <span style="margin-left: auto; font-size: 11px; color: #8b949e; font-weight: 400;">
                                Confidence: ${data.ml_insights.avg_ml_confidence}%
                            </span>
                        </h4>
                        
                        <!-- ML Segments Grid -->
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;">
                            ${Object.entries(data.ml_insights.ml_segments || {}).map(([segment, count]) => {
                const segmentColors = {
                    'VIP - Protect': '#238636',
                    'VIP At-Risk': '#f85149',
                    'High-Value Declining': '#d29922',
                    'Rising Star': '#1f6feb',
                    'Lost Cause': '#6e7681',
                    'Stable Regular': '#8957e5',
                    'Standard': '#8b949e'
                };
                const color = segmentColors[segment] || '#8b949e';
                return `
                                    <div style="padding: 12px; background: ${color}15; border: 1px solid ${color}; border-radius: 4px;">
                                        <div style="font-size: 11px; color: ${color}; font-weight: 600; margin-bottom: 4px;">${segment}</div>
                                        <div style="font-size: 24px; color: ${color}; font-weight: 700;">${count}</div>
                                    </div>
                                `;
            }).join('')}
                        </div>
                        
                        <!-- Behavior Trends & Revenue at Risk -->
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
                            <div style="padding: 12px; background: #0d1117; border: 1px solid #30363d; border-radius: 4px;">
                                <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 8px;">Behavior Trends</div>
                                <div style="display: flex; gap: 16px;">
                                    <div>
                                        <div style="font-size: 20px; color: #f85149; font-weight: 700;">${data.ml_insights.behavior_trends.declining}</div>
                                        <div style="font-size: 11px; color: #8b949e;">Declining</div>
                                    </div>
                                    <div>
                                        <div style="font-size: 20px; color: #3fb950; font-weight: 700;">${data.ml_insights.behavior_trends.improving}</div>
                                        <div style="font-size: 11px; color: #8b949e;">Improving</div>
                                    </div>
                                    <div>
                                        <div style="font-size: 20px; color: #8b949e; font-weight: 700;">${data.ml_insights.behavior_trends.stable}</div>
                                        <div style="font-size: 11px; color: #8b949e;">Stable</div>
                                    </div>
                                </div>
                            </div>
                            
                            <div style="padding: 12px; background: #0d1117; border: 1px solid #30363d; border-radius: 4px;">
                                <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 8px;">Revenue at Risk</div>
                                <div>
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                        <span style="font-size: 11px; color: #f85149;">High Risk</span>
                                        <span style="font-size: 14px; color: #f85149; font-weight: 700;">$${(data.ml_insights.revenue_at_risk.high_risk / 1000).toFixed(0)}K</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                        <span style="font-size: 11px; color: #d29922;">Medium Risk</span>
                                        <span style="font-size: 14px; color: #d29922; font-weight: 700;">$${(data.ml_insights.revenue_at_risk.medium_risk / 1000).toFixed(0)}K</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; padding-top: 8px; border-top: 1px solid #30363d; margin-top: 4px;">
                                        <span style="font-size: 12px; color: #c9d1d9; font-weight: 600;">Total at Risk</span>
                                        <span style="font-size: 16px; color: #c9d1d9; font-weight: 700;">$${(data.ml_insights.revenue_at_risk.total / 1000).toFixed(0)}K</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Root Causes & Recommended Actions -->
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                            <div style="padding: 12px; background: #0d1117; border: 1px solid #30363d; border-radius: 4px;">
                                <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 8px;">Top Root Causes</div>
                                <div style="display: flex; flex-direction: column; gap: 6px;">
                                    ${Object.entries(data.ml_insights.root_causes || {}).sort((a, b) => b[1] - a[1]).slice(0, 4).map(([cause, count]) => {
                return `
                                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                                <span style="font-size: 12px; color: #c9d1d9;">${cause.charAt(0).toUpperCase() + cause.slice(1)}</span>
                                                <span style="font-size: 14px; color: #f85149; font-weight: 600;">${count}</span>
                                            </div>
                                        `;
            }).join('')}
                                </div>
                            </div>
                            
                            <div style="padding: 12px; background: #0d1117; border: 1px solid #30363d; border-radius: 4px;">
                                <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; margin-bottom: 8px;">Best Actions (ML)</div>
                                <div style="display: flex; flex-direction: column; gap: 6px;">
                                    ${Object.entries(data.ml_insights.recommended_actions || {}).sort((a, b) => b[1] - a[1]).map(([action, count]) => {
                return `
                                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                                <span style="font-size: 12px; color: #c9d1d9;">${action.replace('_', ' ').charAt(0).toUpperCase() + action.slice(1).replace('_', ' ')}</span>
                                                <span style="font-size: 14px; color: #3fb950; font-weight: 600;">${count}</span>
                                            </div>
                                        `;
            }).join('')}
                                </div>
                            </div>
                        </div>
                        
                        <!-- Predictive Forecast -->
                        <div style="margin-top: 16px; padding: 12px; background: linear-gradient(135deg, rgba(137, 87, 229, 0.1) 0%, rgba(31, 111, 235, 0.1) 100%); border: 1px solid #8957e5; border-radius: 4px;">
                            <div style="font-size: 11px; color: #8957e5; text-transform: uppercase; margin-bottom: 8px; font-weight: 600;">
                                <i class="fas fa-chart-line"></i> Predictive Risk Forecast
                            </div>
                            <div style="display: flex; justify-content: space-around;">
                                <div style="text-align: center;">
                                    <div style="font-size: 18px; color: #c9d1d9; font-weight: 700;">${data.ml_insights.predictive_summary.avg_30d_risk}%</div>
                                    <div style="font-size: 11px; color: #8b949e;">30 Days</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 18px; color: #c9d1d9; font-weight: 700;">${data.ml_insights.predictive_summary.avg_60d_risk}%</div>
                                    <div style="font-size: 11px; color: #8b949e;">60 Days</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 18px; color: #c9d1d9; font-weight: 700;">${data.ml_insights.predictive_summary.avg_90d_risk}%</div>
                                    <div style="font-size: 11px; color: #8b949e;">90 Days</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    ` : ''
                }

                    <!--Smart Filters-->
                    <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 16px;">
                        <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 12px;">
                            <button id="toggle-internal" data-exclude="true" style="padding: 6px 12px; background: #238636; border: 1px solid #238636; border-radius: 4px; color: white; font-size: 12px; cursor: pointer; font-weight: 600;">
                                🏢 Exclude In-House ✓
                            </button>
                            <div style="height: 20px; width: 1px; background: #30363d; margin: 0 4px;"></div>
                            <button class="filter-btn" data-filter="all" style="padding: 6px 12px; background: #1f6feb; border: 1px solid #1f6feb; border-radius: 4px; color: white; font-size: 12px; cursor: pointer;">
                                All Customers
                            </button>
                            <button class="filter-btn" data-filter="high" style="padding: 6px 12px; background: #21262d; border: 1px solid #f85149; border-radius: 4px; color: #f85149; font-size: 12px; cursor: pointer;">
                                🚨 High Risk (${risk_distribution.high})
                            </button>
                            <button class="filter-btn" data-filter="medium" style="padding: 6px 12px; background: #21262d; border: 1px solid #d29922; border-radius: 4px; color: #d29922; font-size: 12px; cursor: pointer;">
                                ⚠️ Medium Risk (${risk_distribution.medium})
                            </button>
                            <button class="filter-btn" data-filter="champions" style="padding: 6px 12px; background: #21262d; border: 1px solid #238636; border-radius: 4px; color: #238636; font-size: 12px; cursor: pointer;">
                                Champions (${segment_distribution['Champions'] || 0})
                            </button>
                            <button class="filter-btn" data-filter="at_risk" style="padding: 6px 12px; background: #21262d; border: 1px solid #d29922; border-radius: 4px; color: #d29922; font-size: 12px; cursor: pointer;">
                                At Risk Segment (${segment_distribution['At Risk'] || 0})
                            </button>
                            <input type="text" id="customer-search" placeholder="Search customers..." 
                                   style="padding: 6px 12px; background: #0d1117; border: 1px solid #30363d; border-radius: 4px; color: #c9d1d9; font-size: 12px; flex: 1; min-width: 200px;">
                        </div>
                        
                        <!-- Advanced Filters Row -->
                        <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center; padding-top: 12px; border-top: 1px solid #30363d;">
                            <div style="display: flex; align-items: center; gap: 6px;">
                                <label style="font-size: 11px; color: #8b949e; text-transform: uppercase; font-weight: 600;">Min LTV:</label>
                                <input type="number" id="filter-min-ltv" placeholder="500" value="500" min="0" step="100" 
                                       style="width: 90px; padding: 4px 8px; background: #0d1117; border: 1px solid #30363d; border-radius: 4px; color: #c9d1d9; font-size: 12px;">
                                <span style="font-size: 11px; color: #8b949e;">$</span>
                            </div>
                            
                            <div style="display: flex; align-items: center; gap: 6px;">
                                <label style="font-size: 11px; color: #8b949e; text-transform: uppercase; font-weight: 600;">Inactive Days:</label>
                                <select id="filter-inactive-days" style="padding: 4px 8px; background: #0d1117; border: 1px solid #30363d; border-radius: 4px; color: #c9d1d9; font-size: 12px; cursor: pointer;">
                                    <option value="0">All</option>
                                    <option value="30">30+ days</option>
                                    <option value="60">60+ days</option>
                                    <option value="90">90+ days</option>
                                    <option value="180" selected>180+ days</option>
                                    <option value="365">365+ days</option>
                                </select>
                            </div>
                            
                            <div style="display: flex; align-items: center; gap: 6px;">
                                <label style="font-size: 11px; color: #8b949e; text-transform: uppercase; font-weight: 600;">Churn Risk:</label>
                                <select id="filter-churn-risk" style="padding: 4px 8px; background: #0d1117; border: 1px solid #30363d; border-radius: 4px; color: #c9d1d9; font-size: 12px; cursor: pointer;">
                                    <option value="0">All</option>
                                    <option value="50">50%+</option>
                                    <option value="70">70%+</option>
                                    <option value="90">90%+</option>
                                </select>
                            </div>
                            
                            <button id="apply-advanced-filters" style="padding: 4px 12px; background: #1f6feb; border: 1px solid #1f6feb; border-radius: 4px; color: white; font-size: 11px; cursor: pointer; font-weight: 600; margin-left: auto;">
                                <i class="fas fa-filter"></i> Apply Filters
                            </button>
                            
                            <button id="clear-advanced-filters" style="padding: 4px 12px; background: #21262d; border: 1px solid #6e7681; border-radius: 4px; color: #8b949e; font-size: 11px; cursor: pointer;">
                                <i class="fas fa-times"></i> Clear
                            </button>
                        </div>
                    </div>

                    <!--Customer Intelligence Table-->
                    <div id="customer-intelligence-table"></div>

                    <!--Smart Recommendations-->
            <div style="padding: 20px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; margin-top: 24px;">
                <h4 style="margin: 0 0 8px 0; color: #c9d1d9; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-lightbulb" style="color: #d29922;"></i>
                    Smart Recommendations
                </h4>
                <p style="margin: 0 0 16px 0; font-size: 12px; color: #8b949e; line-height: 1.5;">
                    <strong>Prioritization Logic:</strong> High-value clients (LTV ≥ $500) ranked by: (1) Churn risk + days overdue, (2) Revenue at risk, (3) Historical order frequency. Focus on preventing losses from valuable customers and re-engaging frequent buyers who've gone quiet.
                </p>

                ${recommendations.urgent.length > 0 ? `
                        <div style="margin-bottom: 16px; padding: 16px; background: rgba(248, 81, 73, 0.1); border-left: 3px solid #f85149; border-radius: 4px;">
                            <div style="font-weight: 600; color: #f85149; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                                <i class="fas fa-exclamation-triangle"></i> URGENT (Today)
                            </div>
                            <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #c9d1d9; line-height: 1.8;">
                                ${recommendations.urgent.map(r => `
                                    <li>
                                        <strong>${r.action || 'Action required'}</strong>
                                        ${r.ltv || r.risk_score ? `
                                        <div style="font-size: 11px; color: #8b949e; margin-top: 4px; padding-left: 8px;">
                                            ${r.ltv ? `<i class="fas fa-chart-line"></i> LTV: $${r.ltv.toLocaleString()}` : ''}
                                            ${r.ltv && r.risk_score ? ' | ' : ''}
                                            ${r.risk_score ? `Risk: ${r.risk_score}%` : ''}
                                        </div>
                                        ` : ''}
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                        ` : ''}

                ${recommendations.this_week.length > 0 ? `
                        <div style="margin-bottom: 16px; padding: 16px; background: rgba(210, 153, 34, 0.1); border-left: 3px solid #d29922; border-radius: 4px;">
                            <div style="font-weight: 600; color: #d29922; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                                <i class="fas fa-calendar-week"></i> THIS WEEK
                            </div>
                            <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #c9d1d9; line-height: 1.8;">
                                ${recommendations.this_week.map(r => `
                                    <li>
                                        <strong>${r.action || 'Action required'}</strong>
                                        ${r.customer || r.ltv || r.risk_score ? `
                                        <div style="font-size: 11px; color: #8b949e; margin-top: 4px; padding-left: 8px;">
                                            ${r.customer ? `<i class="fas fa-users"></i> ${r.customer}` : ''}
                                            ${r.customer && r.ltv ? ' | ' : ''}
                                            ${r.ltv ? `Total LTV: $${r.ltv.toLocaleString()}` : ''}
                                            ${r.ltv && r.risk_score ? ' | ' : ''}
                                            ${r.risk_score ? `Avg Risk: ${r.risk_score.toFixed(1)}%` : ''}
                                        </div>
                                        ` : ''}
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                        ` : ''}

                ${recommendations.this_month.length > 0 ? `
                        <div style="padding: 16px; background: rgba(31, 111, 235, 0.1); border-left: 3px solid #1f6feb; border-radius: 4px;">
                            <div style="font-weight: 600; color: #1f6feb; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                                <i class="fas fa-calendar-alt"></i> THIS MONTH
                            </div>
                            <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #c9d1d9; line-height: 1.8;">
                                ${recommendations.this_month.map(r => `
                                    <li>
                                        <strong>${r.action || 'Action required'}</strong>
                                        ${r.ltv || r.risk_score ? `
                                        <div style="font-size: 11px; color: #8b949e; margin-top: 4px; padding-left: 8px;">
                                            ${r.ltv ? `<i class="fas fa-dollar-sign"></i> Combined LTV: $${r.ltv.toLocaleString()}` : ''}
                                            ${r.ltv && r.risk_score ? ' | ' : ''}
                                            ${r.risk_score ? `Avg Risk: ${r.risk_score.toFixed(1)}%` : ''}
                                        </div>
                                        ` : ''}
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                        ` : ''}
            </div>
                </div >
                `;

            resultsDiv.innerHTML = html;

            // Initialize Tabulator - check if container exists first
            const tableContainer = document.querySelector('#customer-intelligence-table');
            if (!tableContainer) {
                console.error('[Xero] Cannot initialize Tabulator - #customer-intelligence-table not found in DOM');
                return;
            }

            const table = new Tabulator('#customer-intelligence-table', {
                data: customers,
                layout: 'fitDataStretch',
                pagination: 'local',
                paginationSize: 25,
                paginationSizeSelector: [10, 25, 50, 100, 200],
                paginationCounter: 'rows',
                height: '600px',
                resizableRows: true,
                columns: [
                    {
                        title: '',
                        field: 'risk_category',
                        width: 50,
                        formatter: (cell) => {
                            const colors = { High: '🔴', Medium: '🟡', Low: '🟢' };
                            return colors[cell.getValue()] || '⚪';
                        }
                    },
                    { title: 'Customer', field: 'contact_name', minWidth: 200, widthGrow: 2 },
                    {
                        title: 'Risk Score',
                        field: 'unified_risk_score',
                        width: 100,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            const color = val >= 70 ? '#f85149' : val >= 40 ? '#d29922' : '#3fb950';
                            return `<span style="color: ${color}; font-weight: 600;">${val.toFixed(1)}%</span>`;
                        }
                    },
                    { title: 'Segment', field: 'rfm_segment', width: 150 },
                    {
                        title: 'Last Order',
                        field: 'last_order_date',
                        width: 110,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            if (!val) return '-';
                            const date = new Date(val);
                            const now = new Date();
                            const daysAgo = Math.floor((now - date) / (1000 * 60 * 60 * 24));

                            if (daysAgo > 180) {
                                return `<span style="color: #f85149; font-size: 11px;">${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' })}<br>${daysAgo}d ago</span>`;
                            } else if (daysAgo > 90) {
                                return `<span style="color: #d29922; font-size: 11px;">${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' })}<br>${daysAgo}d ago</span>`;
                            } else {
                                return `<span style="color: #8b949e; font-size: 11px;">${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' })}<br>${daysAgo}d ago</span>`;
                            }
                        }
                    },
                    {
                        title: 'Avg Reorder',
                        field: 'avg_reorder_days',
                        width: 110,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            return val > 0 ? `${Math.round(val)} d` : '-';
                        }
                    },
                    {
                        title: 'Variance',
                        field: 'reorder_variance',
                        width: 100,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            if (val === 0) return '-';
                            const color = val < 7 ? '#3fb950' : val < 14 ? '#d29922' : '#f85149';
                            return `<span style="color: ${color}; font-weight: 600;">±${Math.round(val)}d</span>`;
                        }
                    },
                    {
                        title: 'Days Overdue',
                        field: 'days_overdue',
                        width: 120,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            const row = cell.getRow().getData();
                            const variance = row.reorder_variance || 1;

                            if (val === 0) return '<span style="color: #3fb950;">On Time</span>';

                            let emoji = '🟢';
                            let color = '#3fb950';
                            if (val > variance * 2) {
                                emoji = '🔴';
                                color = '#f85149';
                            } else if (val > variance) {
                                emoji = '🟡';
                                color = '#d29922';
                            }

                            return `<span style="color: ${color}; font-weight: 600;">${emoji} ${val}d</span>`;
                        }
                    },
                    {
                        title: 'Deviation',
                        field: 'deviation_severity',
                        width: 110,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            const colors = {
                                'On Time': '#3fb950',
                                'Slightly Late': '#d29922',
                                'Very Late': '#f85149',
                                'Critical': '#f85149'
                            };
                            const color = colors[val] || '#8b949e';
                            const bg = colors[val] ? `${color}20` : '#21262d';
                            return `<span style="background: ${bg}; color: ${color}; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; border: 1px solid ${color};">${val}</span>`;
                        }
                    },
                    {
                        title: 'Churn %',
                        field: 'ml_churn_probability',
                        width: 90,
                        formatter: (cell) => `${cell.getValue().toFixed(1)}%`
                    },
                    {
                        title: 'LTV',
                        field: 'lifetime_revenue',
                        width: 120,
                        formatter: 'money',
                        formatterParams: { precision: 0 }
                    },
                    {
                        title: 'Days Inactive',
                        field: 'days_since_last_order',
                        width: 120,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            const color = val > 180 ? '#f85149' : val > 90 ? '#d29922' : '#8b949e';
                            return `<span style="color: ${color};">${val}d</span>`;
                        }
                    },
                    {
                        title: 'Payment',
                        field: 'payment_consistency',
                        width: 100,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            const color = val >= 90 ? '#3fb950' : val >= 70 ? '#d29922' : '#f85149';
                            return `<span style="color: ${color};">${val.toFixed(0)}%</span>`;
                        }
                    },
                    {
                        title: 'Action',
                        field: 'recommended_action',
                        width: 120,
                        formatter: (cell) => {
                            const actions = {
                                'call_now': '📞 Call',
                                'email_campaign': '✉️ Email',
                                'monitor': '👀 Monitor'
                            };
                            return actions[cell.getValue()] || cell.getValue();
                        }
                    },
                    {
                        title: 'Details',
                        width: 100,
                        hozAlign: 'center',
                        headerSort: false,
                        formatter: () => `
                            <button class="xero-action-btn" style="padding: 6px 12px; background: #1f6feb; border: 1px solid #1f6feb; border-radius: 4px; color: white; cursor: pointer; font-size: 11px;">
                                <i class="fas fa-eye"></i> View
                            </button>
                        `,
                        cellClick: (e, cell) => {
                            const customer = cell.getRow().getData();
                            // Show contact details modal
                            this.showDetailsModal('contact', {
                                name: customer.contact_name,
                                contact_id: customer.contact_id,
                                email: customer.email || 'N/A',
                                phone: customer.phone || 'N/A',
                                lifetime_revenue: customer.lifetime_revenue,
                                rfm_segment: customer.rfm_segment,
                                unified_risk_score: customer.unified_risk_score,
                                ml_churn_probability: customer.ml_churn_probability,
                                days_since_last_order: customer.days_since_last_order,
                                recommended_action: customer.recommended_action
                            });
                        }
                    }
                ]
            });

            // Dynamically adjust height when page size changes
            table.on('pageSizeChanged', (size) => {
                if (size >= 50) {
                    table.setHeight('800px');
                } else {
                    table.setHeight('600px');
                }
            });

            // Filter buttons
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.filter-btn').forEach(b => {
                        b.style.background = '#21262d';
                        b.style.color = b.style.borderColor;
                    });
                    btn.style.background = btn.style.borderColor;
                    btn.style.color = 'white';

                    const filter = btn.dataset.filter;
                    if (filter === 'all') {
                        table.clearFilter();
                    } else if (filter === 'high') {
                        table.setFilter('risk_category', '=', 'High');
                    } else if (filter === 'medium') {
                        table.setFilter('risk_category', '=', 'Medium');
                    } else if (filter === 'champions') {
                        table.setFilter('rfm_segment', '=', 'Champions');
                    } else if (filter === 'at_risk') {
                        table.setFilter('rfm_segment', '=', 'At Risk');
                    }
                });
            });

            // Search filter
            document.getElementById('customer-search')?.addEventListener('keyup', (e) => {
                table.setFilter('contact_name', 'like', e.target.value);
            });

            // Segment badge filters
            document.querySelectorAll('.segment-badge').forEach(badge => {
                badge.addEventListener('click', () => {
                    const segment = badge.dataset.segment;

                    // Reset filter buttons
                    document.querySelectorAll('.filter-btn').forEach(b => {
                        b.style.background = '#21262d';
                        b.style.color = b.style.borderColor;
                    });

                    // Apply filter
                    table.setFilter('rfm_segment', '=', segment);
                    console.log(`[Xero] Filtering by segment: ${segment}`);
                });
            });

            // Advanced Filters - Apply Button
            document.getElementById('apply-advanced-filters')?.addEventListener('click', () => {
                const minLTV = parseFloat(document.getElementById('filter-min-ltv').value) || 0;
                const inactiveDays = parseInt(document.getElementById('filter-inactive-days').value) || 0;
                const churnRisk = parseInt(document.getElementById('filter-churn-risk').value) || 0;

                // Build compound filter
                const filters = [];

                if (minLTV > 0) {
                    filters.push({ field: 'lifetime_revenue', type: '>=', value: minLTV });
                }

                if (inactiveDays > 0) {
                    filters.push({ field: 'days_since_last_order', type: '>=', value: inactiveDays });
                }

                if (churnRisk > 0) {
                    filters.push({ field: 'ml_churn_probability', type: '>=', value: churnRisk });
                }

                // Apply all filters
                if (filters.length > 0) {
                    table.setFilter(filters);
                    console.log(`[Xero] Applied advanced filters: LTV>=$${minLTV}, Inactive>=${inactiveDays}d, Churn>=${churnRisk}%`);
                } else {
                    table.clearFilter();
                }
            });

            // Advanced Filters - Clear Button
            document.getElementById('clear-advanced-filters')?.addEventListener('click', () => {
                document.getElementById('filter-min-ltv').value = '500';
                document.getElementById('filter-inactive-days').value = '0';
                document.getElementById('filter-churn-risk').value = '0';
                table.clearFilter();
                console.log('[Xero] Cleared all advanced filters');
            });

            // Toggle in-house entities
            let excludeInternal = true;
            document.getElementById('toggle-internal')?.addEventListener('click', async (e) => {
                const btn = e.target;
                excludeInternal = !excludeInternal;

                if (excludeInternal) {
                    btn.style.background = '#238636';
                    btn.style.borderColor = '#238636';
                    btn.innerHTML = '🏢 Exclude In-House ✓';
                } else {
                    btn.style.background = '#6e7681';
                    btn.style.borderColor = '#6e7681';
                    btn.innerHTML = '🏢 Include In-House ✗';
                }

                // Reload with new filter
                const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/customer-intelligence?business_id=${this.currentBusiness}&exclude_internal=${excludeInternal}`);
                const newData = await response.json();
                if (newData.success) {
                    table.setData(newData.customers);
                }
            });

            // Export CSV button
            document.getElementById('export-intelligence')?.addEventListener('click', () => {
                table.download('csv', 'customer-intelligence.csv');
            });

            // AI Export button with dropdown
            document.getElementById('ai-export-btn')?.addEventListener('click', (e) => {
                // Remove existing dropdown if any
                document.querySelectorAll('.ai-export-dropdown').forEach(d => d.remove());

                // Create dropdown
                const dropdown = document.createElement('div');
                dropdown.className = 'ai-export-dropdown';
                dropdown.style.cssText = `
            position: absolute;
            top: ${e.target.offsetTop + e.target.offsetHeight + 5} px;
            right: ${window.innerWidth - e.target.getBoundingClientRect().right} px;
            background: #161b22;
            border: 1px solid #30363d;
            border - radius: 6px;
            padding: 12px;
            box - shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
            z - index: 1000;
            min - width: 320px;
            max - width: 400px;
            `;

                dropdown.innerHTML = `
                < div style = "margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #30363d;" >
                        <div style="font-weight: 600; color: #c9d1d9; margin-bottom: 8px;">Data Scope</div>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px; cursor: pointer; font-size: 13px; color: #8b949e;">
                            <input type="checkbox" id="scope-metrics" checked style="cursor: pointer;">
                            Include Summary Metrics
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px; cursor: pointer; font-size: 13px; color: #8b949e;">
                            <input type="checkbox" id="scope-recommendations" checked style="cursor: pointer;">
                            Include Recommendations
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 13px; color: #8b949e;">
                            <input type="checkbox" id="scope-full-table" checked style="cursor: pointer;">
                            Include Full Customer Table
                        </label>
                    </div >
                    
                    <button id="quick-prompts-option" style="width: 100%; padding: 10px; background: linear-gradient(135deg, #8957e5 0%, #9b6df7 100%); border: none; border-radius: 4px; color: white; font-size: 13px; font-weight: 600; cursor: pointer; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; justify-content: center;">
                        <i class="fas fa-comments"></i> Quick AI Prompts
                    </button>
                    
                    <button id="export-for-ai-option" style="width: 100%; padding: 10px; background: linear-gradient(135deg, #1f6feb 0%, #0d419d 100%); border: none; border-radius: 4px; color: white; font-size: 13px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; justify-content: center;">
                        <i class="fas fa-file-export"></i> Export for AI Analysis
                    </button>
            `;

                document.body.appendChild(dropdown);

                // Quick Prompts
                document.getElementById('quick-prompts-option')?.addEventListener('click', () => {
                    const prompts = [
                        `Analyze these top 10 at - risk customers and provide: \n1.Top 3 retention strategies\n2.Prioritized call list with talking points\n3.Email campaign ideas\n\nCustomers: \n${customers.filter(c => c.risk_category === 'High').slice(0, 10).map(c => `- ${c.contact_name}: ${c.unified_risk_score}% risk, ${c.days_overdue}d overdue from ${Math.round(c.avg_reorder_days)}d cycle, $${c.lifetime_revenue.toLocaleString()} LTV`).join('\n')} `,

                        `Review my customer segmentation and suggest: \n1.Best segment to target for growth\n2.Win - back campaign for Lost customers\n3.VIP program ideas for Champions\n\nSegments: \n${Object.entries(segment_distribution).map(([seg, count]) => `- ${seg}: ${count} customers`).join('\n')} `,

                        `Analyze reorder frequency patterns: \n1.Identify customers with unusual patterns\n2.Suggest proactive outreach timing\n3.Forecast next 30 days orders\n\nTop variance customers: \n${customers.filter(c => c.reorder_variance > 14).slice(0, 10).map(c => `- ${c.contact_name}: ${Math.round(c.avg_reorder_days)}d avg ±${Math.round(c.reorder_variance)}d variance`).join('\n')} `,

                        `Create retention strategy for: \n - ${metrics.at_risk} at - risk customers\n - ${metrics.churned} churned customers\n - ${metrics.retention_rate.toFixed(1)}% current retention rate\n\nProvide: 1) Quick wins, 2) Long - term plan, 3) Success metrics`,

                        `Payment risk analysis: \n - ${metrics.late_invoices} late invoices\n - Top late payers: ${customers.filter(c => c.late_payments > 0).slice(0, 5).map(c => c.contact_name).join(', ')} \n\nSuggest: 1) Payment terms strategy, 2) Credit policy updates, 3) Follow - up process`
                    ];

                    const promptsDropdown = document.createElement('div');
                    promptsDropdown.className = 'prompts-list-dropdown';
                    promptsDropdown.style.cssText = dropdown.style.cssText;
                    promptsDropdown.style.maxHeight = '400px';
                    promptsDropdown.style.overflowY = 'auto';
                    promptsDropdown.innerHTML = `
                < div style = "margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #30363d;" >
                    <div style="font-weight: 600; color: #c9d1d9;">Select Prompt to Copy</div>
                        </div >
                ${prompts.map((p, i) => `
                            <button data-prompt-index="${i}" class="prompt-option" style="width: 100%; padding: 8px; background: #21262d; border: 1px solid #30363d; border-radius: 4px; color: #c9d1d9; font-size: 12px; text-align: left; cursor: pointer; margin-bottom: 6px; transition: 0.2s;">
                                ${p.split('\n')[0].substring(0, 60)}...
                            </button>
                        `).join('')
                        }
            `;

                    dropdown.replaceWith(promptsDropdown);

                    promptsDropdown.querySelectorAll('.prompt-option').forEach((btn, idx) => {
                        btn.addEventListener('click', () => {
                            navigator.clipboard.writeText(prompts[idx]);
                            btn.innerHTML = '✓ Copied to clipboard!';
                            btn.style.background = '#238636';
                            setTimeout(() => promptsDropdown.remove(), 1500);
                        });
                        btn.addEventListener('mouseenter', () => btn.style.borderColor = '#8957e5');
                        btn.addEventListener('mouseleave', () => btn.style.borderColor = '#30363d');
                    });
                });

                // Export for AI
                document.getElementById('export-for-ai-option')?.addEventListener('click', () => {
                    const includeMetrics = document.getElementById('scope-metrics')?.checked;
                    const includeRecommendations = document.getElementById('scope-recommendations')?.checked;
                    const includeFullTable = document.getElementById('scope-full-table')?.checked;

                    // Build export data
                    const exportData = {
                        metrics: includeMetrics ? metrics : null,
                        risk_distribution: includeMetrics ? risk_distribution : null,
                        segment_distribution: includeMetrics ? segment_distribution : null,
                        recommendations: includeRecommendations ? recommendations : null,
                        customers: includeFullTable ? customers : customers.slice(0, 50),
                        ml_insights: data.ml_insights || null
                    };

                    // Use formatDataForAI method
                    const formattedText = this.formatDataForAI(
                        exportData,
                        'Customer Intelligence Dashboard',
                        `${this.API_BASE_URL}/api/xero/reports/customer-intelligence?business_id=${this.currentBusiness}`
                    );

                    // Copy to clipboard
                    navigator.clipboard.writeText(formattedText).then(() => {
                        dropdown.innerHTML = `
                            <div style="padding: 20px; text-align: center;">
                                <i class="fas fa-check-circle" style="font-size: 48px; color: #238636; margin-bottom: 12px;"></i>
                                <div style="font-weight: 600; color: #c9d1d9; margin-bottom: 8px;">Copied to Clipboard!</div>
                                <div style="font-size: 13px; color: #8b949e;">Paste into ChatGPT, Claude, or any AI assistant</div>
                            </div>
                        `;
                        setTimeout(() => dropdown.remove(), 2000);
                    }).catch(err => {
                        alert('Failed to copy to clipboard: ' + err.message);
                    });
                });

                // Close dropdown on click outside
                setTimeout(() => {
                    document.addEventListener('click', function closeDropdown(e) {
                        if (!dropdown.contains(e.target) && e.target !== document.getElementById('ai-export-btn')) {
                            dropdown.remove();
                            document.removeEventListener('click', closeDropdown);
                        }
                    });
                }, 100);
            });

            // Refresh button
            document.getElementById('refresh-intelligence')?.addEventListener('click', () => {
                this.showCustomerIntelligence();
            });

        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;"><i class="fas fa-exclamation-circle"></i> Error loading customer intelligence: ${error.message}</div>`;
        }
    }
}

// ============================================================================
// REGISTER MODULE
// ============================================================================

// Register module with ModuleLoader (V5.0 pattern)
if (window.ModuleLoader) {
    window.ModuleLoader.registerModuleClass('xero', XeroModule);
    console.log('[Xero] Module class registered with ModuleLoader');
} else {
    console.warn('[Xero] ModuleLoader not found - module may not load correctly');
}

// ES6 Export
export default XeroModule;
