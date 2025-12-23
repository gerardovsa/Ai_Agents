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
     * Parse Xero date format: /Date(1372291200000+0000)/
     * @param {string} dateStr - Xero date string
     * @returns {Date|null} JavaScript Date object or null
     */
    parseXeroDate(dateStr) {
        if (!dateStr || dateStr === 'undefined' || dateStr === 'null') return null;

        // Handle Xero format: /Date(timestamp+timezone)/
        const match = dateStr.match(/\/Date\((\d+)([\+\-]\d+)?\)\//);
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
                break;
            case 'contacts':
                await this.loadContacts();
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
                        <button class="xero-btn" id="xero-export-all-invoices" style="padding: 8px 16px; background: #238636; border: none; border-radius: 6px; color: white; font-weight: 500; cursor: pointer;">
                            <i class="fas fa-download"></i> Export All
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
                        <i class="fas fa-chevron-down"></i>
                    </button>
                    <div class="xero-reports-content" id="xero-invoices-reports-content" style="display: none; padding: 16px; background: #0d1117; border-top: 1px solid #30363d;">
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
        if (exportAllBtn) exportAllBtn.addEventListener('click', () => this.exportInvoices('xlsx'));

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
        const agedReceivablesBtn = container.querySelector('#xero-show-aged-receivables');
        const salesSummaryBtn = container.querySelector('#xero-show-sales-summary-inv');
        const overdueInvoicesBtn = container.querySelector('#xero-show-overdue-invoices');
        const revenueTrendsBtn = container.querySelector('#xero-show-revenue-trends');
        const invoiceStatusBtn = container.querySelector('#xero-show-invoice-status');
        const invoiceVolumeBtn = container.querySelector('#xero-show-invoice-volume');

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
            paginationSizeSelector: [10, 25, 50, 100],
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
                        <button class="xero-action-btn" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                    `,
                    cellClick: (e, cell) => {
                        this.showInvoiceDetails(cell.getRow().getData());
                    }
                }
            ]
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
                <div class="xero-toolbar">
                    <div class="xero-toolbar-left">
                        <button class="xero-btn xero-btn-primary" id="xero-create-contact">
                            <i class="fas fa-plus"></i> Create Contact
                        </button>
                        <button class="xero-btn" id="xero-refresh-contacts">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                    <div class="xero-toolbar-right">
                        <input type="text" class="xero-search" id="xero-contact-search" 
                               placeholder="Search contacts...">
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
                        <i class="fas fa-chevron-down"></i>
                    </button>
                    <div class="xero-reports-content" id="xero-contacts-reports-content" style="display: none; padding: 16px; background: #0d1117; border-top: 1px solid #30363d;">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                            <button class="xero-btn xero-btn-sm" id="xero-show-contact-activity" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-history" style="margin-right: 6px;"></i>Contact Activity
                            </button>
                            <button class="xero-btn xero-btn-sm" id="xero-show-inactive-customers" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-user-slash" style="margin-right: 6px;"></i>Inactive Customers
                            </button>
                            <button class="xero-btn xero-btn-sm" id="xero-show-customer-ltv" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-gem" style="margin-right: 6px;"></i>Customer Lifetime Value
                            </button>
                            <button class="xero-btn xero-btn-sm" id="xero-show-customer-segmentation" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-users" style="margin-right: 6px;"></i>Customer Segmentation
                            </button>
                        </div>
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
        const contactActivityBtn = container.querySelector('#xero-show-contact-activity');
        const inactiveCustomersBtn = container.querySelector('#xero-show-inactive-customers');
        const customerLtvBtn = container.querySelector('#xero-show-customer-ltv');
        const customerSegmentationBtn = container.querySelector('#xero-show-customer-segmentation');

        if (contactActivityBtn) contactActivityBtn.addEventListener('click', () => this.showContactActivity());
        if (inactiveCustomersBtn) inactiveCustomersBtn.addEventListener('click', () => this.showInactiveCustomers());
        if (customerLtvBtn) customerLtvBtn.addEventListener('click', () => this.showCustomerLTV());
        if (customerSegmentationBtn) customerSegmentationBtn.addEventListener('click', () => this.showCustomerSegmentation());
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
                        <button class="xero-action-btn" title="View Details">
                            <i class="fas fa-eye"></i>
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

        if (businessComparisonBtn) businessComparisonBtn.addEventListener('click', () => this.showBusinessComparison());
        if (consolidatedRevenueBtn) consolidatedRevenueBtn.addEventListener('click', () => this.showConsolidatedRevenue());
        if (customerOverlapBtn) customerOverlapBtn.addEventListener('click', () => this.showCustomerOverlap());
        if (revenueByProductBtn) revenueByProductBtn.addEventListener('click', () => this.showRevenueByProduct());
        if (seasonalityBtn) seasonalityBtn.addEventListener('click', () => this.showSeasonality());
        if (forecastBtn) forecastBtn.addEventListener('click', () => this.showForecast());
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
        console.log('Showing invoice details:', invoice);
        // TODO: Implement invoice details modal
    }

    showContactDetails(contact) {
        console.log('Showing contact details:', contact);
        // TODO: Implement contact details modal
    }

    showCreateInvoiceModal() {
        console.log('Opening create invoice modal');
        // TODO: Implement create invoice modal
    }

    showCreateContactModal() {
        console.log('Opening create contact modal');
        // TODO: Implement create contact modal
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
                    <h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Aged Receivables Report</h4>
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
                    <h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Sales Summary (Last ${months} months)</h4>
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

            resultsDiv.innerHTML = `<div style="padding: 16px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Overdue Invoices (${tableData.length})</h4><div id="overdue-invoices-table"></div></div>`;

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
                    }
                ],
                initialSort: [{ column: 'days_overdue', dir: 'desc' }]
            });
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
                    <h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Revenue Trends (${tableData.length} months)</h4>
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
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Invoice Status Summary</h4><table style="width: 100%; border-collapse: collapse;"><thead><tr style="border-bottom: 1px solid #30363d;"><th style="text-align: left; padding: 8px;">Status</th><th style="text-align: right; padding: 8px;">Count</th><th style="text-align: right; padding: 8px;">Total Amount</th></tr></thead><tbody>`;
            Object.entries(data.status_summary).forEach(([status, stats]) => {
                html += `<tr style="border-bottom: 1px solid #30363d;"><td style="padding: 8px; color: #c9d1d9;">${status}</td><td style="padding: 8px; text-align: right; color: #8b949e;">${stats.count}</td><td style="padding: 8px; text-align: right; color: #c9d1d9;">$${stats.total.toFixed(2)}</td></tr>`;
            });
            html += `</tbody></table></div>`;
            resultsDiv.innerHTML = html;
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
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Invoice Volume Analysis</h4><div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;"><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e; margin-bottom: 4px;">Total Invoices</div><div style="font-size: 20px; color: #c9d1d9; font-weight: 600;">${data.total_invoices}</div></div><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e; margin-bottom: 4px;">Avg per Month</div><div style="font-size: 20px; color: #c9d1d9; font-weight: 600;">${data.avg_invoices_per_month.toFixed(1)}</div></div><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e; margin-bottom: 4px;">Avg Value</div><div style="font-size: 20px; color: #c9d1d9; font-weight: 600;">$${data.avg_invoice_value.toFixed(2)}</div></div></div></div>`;
            resultsDiv.innerHTML = html;
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showContactActivity() {
        const resultsDiv = document.querySelector('#xero-contacts-report-results');
        if (!resultsDiv) return;
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

            resultsDiv.innerHTML = `<div style="padding: 16px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Contact Activity (${tableData.length})</h4><div id="contact-activity-table"></div></div>`;

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
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showInactiveCustomers() {
        const resultsDiv = document.querySelector('#xero-contacts-report-results');
        if (!resultsDiv) return;
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

            resultsDiv.innerHTML = `<div style="padding: 16px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Inactive Customers (${tableData.length})</h4><div id="inactive-customers-table"></div></div>`;

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
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showCustomerLTV() {
        const resultsDiv = document.querySelector('#xero-contacts-report-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading customer lifetime value...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/customer-lifetime-value?business_id=${this.currentBusiness}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Customer Lifetime Value</h4><table style="width: 100%; border-collapse: collapse;"><thead><tr style="border-bottom: 1px solid #30363d;"><th style="text-align: left; padding: 8px;">Customer</th><th style="text-align: right; padding: 8px;">Revenue</th><th style="text-align: right; padding: 8px;">Invoices</th><th style="text-align: right; padding: 8px;">Tenure (days)</th></tr></thead><tbody>`;
            data.customers.slice(0, 20).forEach(customer => {
                html += `<tr style="border-bottom: 1px solid #30363d;"><td style="padding: 8px; color: #c9d1d9;">${customer.contact_name}</td><td style="padding: 8px; text-align: right; color: #238636; font-weight: 600;">$${customer.total_revenue.toFixed(2)}</td><td style="padding: 8px; text-align: right; color: #8b949e;">${customer.invoice_count}</td><td style="padding: 8px; text-align: right; color: #8b949e;">${customer.tenure_days}</td></tr>`;
            });
            html += `</tbody></table></div>`;
            resultsDiv.innerHTML = html;
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showCustomerSegmentation() {
        const resultsDiv = document.querySelector('#xero-contacts-report-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading customer segmentation...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/customer-segmentation?business_id=${this.currentBusiness}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Customer Segmentation (RFM)</h4><div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px; margin-bottom: 16px;">`;
            const colors = { Champions: '#238636', 'Loyal Customers': '#1f6feb', 'Potential Loyalists': '#8957e5', 'At Risk': '#d29922', Lost: '#f85149' };
            Object.entries(data.segment_distribution).forEach(([segment, count]) => {
                html += `<div style="padding: 12px; background: #0d1117; border-radius: 4px; border-left: 3px solid ${colors[segment] || '#8b949e'};"><div style="font-size: 12px; color: #8b949e;">${segment}</div><div style="font-size: 20px; color: #c9d1d9; font-weight: 600;">${count}</div></div>`;
            });
            html += `</div></div>`;
            resultsDiv.innerHTML = html;
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
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
                    hovermode: 'x unified'
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
                this.createChart('consolidated-revenue-waterfall-chart', {
                    x: businesses.map(b => b.name),
                    y: businesses.map(b => b.revenue),
                    type: 'bar',
                    marker: { color: ['#238636', '#1f6feb', '#8957e5'] },
                    text: businesses.map(b => `$${(b.revenue / 1000).toFixed(1)}k (${b.percentage_of_total}%)`),
                    textposition: 'outside'
                }, {
                    title: { text: 'Revenue by Business', font: { size: 16 } },
                    xaxis: { title: 'Business' },
                    yaxis: { title: 'Revenue ($)' },
                    showlegend: false
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
                    yaxis: { title: 'Revenue ($)' }
                });

                // Cash Flow Projection Chart
                const cashFlow = data.cash_flow_projection;
                this.createChart('consolidated-revenue-cashflow-chart', {
                    x: Object.keys(cashFlow),
                    y: Object.values(cashFlow),
                    type: 'bar',
                    marker: {
                        color: ['#238636', '#d29922', '#f85149', '#8b1000']
                    },
                    text: Object.values(cashFlow).map(v => `$${(v / 1000).toFixed(1)}k`),
                    textposition: 'outside'
                }, {
                    title: { text: 'Cash Flow Projection (Outstanding by Age)', font: { size: 16 } },
                    xaxis: { title: 'Aging Bucket (Days)' },
                    yaxis: { title: 'Outstanding Amount ($)' },
                    showlegend: false
                });

                // Business Contribution Table
                const tableData = businesses.map(b => ({
                    business: b.name,
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
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Customer Overlap Analysis</h4><div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;"><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e;">Total Customers</div><div style="font-size: 20px; color: #c9d1d9; font-weight: 600;">${data.total_unique_customers}</div></div><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e;">Overlapping</div><div style="font-size: 20px; color: #1f6feb; font-weight: 600;">${data.overlapping_customer_count}</div></div><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e;">Overlap %</div><div style="font-size: 20px; color: #8957e5; font-weight: 600;">${data.overlap_percentage}%</div></div></div></div>`;
            resultsDiv.innerHTML = html;
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
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Revenue by Product/Service</h4><table style="width: 100%; border-collapse: collapse;"><thead><tr style="border-bottom: 1px solid #30363d;"><th style="text-align: left; padding: 8px;">Product</th><th style="text-align: right; padding: 8px;">Quantity</th><th style="text-align: right; padding: 8px;">Revenue</th></tr></thead><tbody>`;
            data.products.slice(0, 20).forEach(product => {
                html += `<tr style="border-bottom: 1px solid #30363d;"><td style="padding: 8px; color: #c9d1d9;">${product.product}</td><td style="padding: 8px; text-align: right; color: #8b949e;">${product.quantity_sold}</td><td style="padding: 8px; text-align: right; color: #238636; font-weight: 600;">$${product.revenue.toFixed(2)}</td></tr>`;
            });
            html += `</tbody></table></div>`;
            resultsDiv.innerHTML = html;
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
                const years = [...new Set(monthlyBreakdown.map(m => m.year))].sort();
                const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

                const revenueMatrix = years.map(year =>
                    months.map((_, monthIdx) => {
                        const monthData = monthlyBreakdown.find(m => m.year === year && m.month === monthIdx + 1);
                        return monthData ? monthData.revenue : 0;
                    })
                );

                this.createChart('seasonality-heatmap', {
                    z: revenueMatrix,
                    x: months,
                    y: years,
                    type: 'heatmap',
                    colorscale: [
                        [0, '#0d1117'],
                        [0.25, '#1f6feb'],
                        [0.5, '#13B5EA'],
                        [0.75, '#3fb950'],
                        [1, '#238636']
                    ],
                    hovertemplate: '%{y} %{x}: $%{z:,.0f}<extra></extra>'
                }, {
                    title: { text: 'Revenue Heatmap (Years × Months)', font: { size: 14 } },
                    xaxis: { title: 'Month' },
                    yaxis: { title: 'Year' }
                });

                // Bar Chart - Average by Month with Variance
                const seasonalPattern = data.seasonal_pattern;
                this.createChart('seasonality-bar-chart', {
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
                }, {
                    title: { text: 'Average Revenue by Month (with Variance)', font: { size: 14 } },
                    xaxis: { title: 'Month' },
                    yaxis: { title: 'Average Revenue ($)' },
                    showlegend: false
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
                <h3 style="color: #c9d1d9; margin-bottom: 20px;">
                    <i class="fas fa-chart-line" style="color: #13B5EA; margin-right: 8px;"></i>
                    Revenue Forecast Dashboard
                </h3>
                
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
                
                <div id="forecast-chart" style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 16px; margin-bottom: 24px;"></div>
                
                <div id="forecast-risks" style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 16px; margin-bottom: 24px;"></div>
                
                <div id="forecast-table"></div>
            </div>
        `;

        const loadData = async (historicalMonths = 12, forecastMonths = 6) => {
            try {
                const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/forecast-enhanced?business_id=${this.currentBusiness}&historical_months=${historicalMonths}&forecast_months=${forecastMonths}`);
                const data = await response.json();
                if (!data.success) throw new Error(data.error);

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
                if (scenario === 'base' || scenario === 'all') {
                    traces.push({
                        x: forecastData.map(f => f.month_name),
                        y: forecastData.map(f => f.base),
                        type: 'scatter',
                        mode: 'lines+markers',
                        name: 'Base Forecast',
                        line: { color: '#1f6feb', width: 3, dash: 'dash' },
                        marker: { size: 8 }
                    });
                }

                if (scenario === 'optimistic' || scenario === 'all') {
                    traces.push({
                        x: forecastData.map(f => f.month_name),
                        y: forecastData.map(f => f.optimistic),
                        type: 'scatter',
                        mode: 'lines',
                        name: 'Optimistic',
                        line: { color: '#3fb950', width: 2, dash: 'dot' }
                    });
                }

                if (scenario === 'pessimistic' || scenario === 'all') {
                    traces.push({
                        x: forecastData.map(f => f.month_name),
                        y: forecastData.map(f => f.pessimistic),
                        type: 'scatter',
                        mode: 'lines',
                        name: 'Pessimistic',
                        line: { color: '#f85149', width: 2, dash: 'dot' }
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
                    yaxis: { title: 'Revenue ($)' }
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
