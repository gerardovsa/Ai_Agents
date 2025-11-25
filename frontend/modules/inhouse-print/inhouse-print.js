/**
 * InHouse Print Tools Module Controller
 * Manages SQL queries, quote calculations, and inventory
 */

class InHousePrintController {
    constructor() {
        this.userId = null;
        this.initialized = false;
        this.queryLibrary = [];
        this.stockLevels = [];
    }

    async init() {
        console.log('[InHousePrint] Initializing...');
        this.initialized = true;

        // Setup tab switching
        this.setupTabs();

        // Load initial data
        await this.loadQueryLibrary();
        await this.loadStockLevels();
        await this.loadReorderAlerts();

        // Setup event listeners
        this.setupEventListeners();

        console.log('[InHousePrint] Initialization complete');
    }

    setupTabs() {
        const tabs = document.querySelectorAll('#inhouse-print-sidebar .tab-btn');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active from all tabs
                tabs.forEach(t => t.classList.remove('active'));
                document.querySelectorAll('#inhouse-print-sidebar .tab-content')
                    .forEach(c => c.classList.remove('active'));

                // Add active to clicked tab
                tab.classList.add('active');
                const tabId = tab.dataset.tab;
                document.getElementById(`tab-${tabId}`).classList.add('active');
            });
        });
    }

    setupEventListeners() {
        // Execute query button
        document.getElementById('execute-query-btn')?.addEventListener('click', () => {
            this.executeCustomQuery();
        });

        // Calculate quote button
        document.getElementById('calculate-quote-btn')?.addEventListener('click', () => {
            this.calculateQuote();
        });

        // Query search
        document.getElementById('query-search')?.addEventListener('input', (e) => {
            this.filterQueries(e.target.value);
        });

        // Stock search
        document.getElementById('stock-search')?.addEventListener('input', (e) => {
            this.filterStock(e.target.value);
        });

        // Product type change
        document.getElementById('product-type')?.addEventListener('change', (e) => {
            this.loadCalculatorParams(e.target.value);
        });
    }

    async loadQueryLibrary() {
        console.log('[InHousePrint] Loading query library...');

        try {
            const response = await fetch('/api/inhouse/query-library');
            const data = await response.json();

            this.queryLibrary = data.queries || [];
            this.renderQueryLibrary();

        } catch (error) {
            console.error('[InHousePrint] Failed to load query library:', error);
            this.showError('query-library-list', 'Failed to load query library');
        }
    }

    renderQueryLibrary() {
        const container = document.getElementById('query-library-list');

        if (this.queryLibrary.length === 0) {
            container.innerHTML = '<p class="no-data">No queries found</p>';
            return;
        }

        container.innerHTML = this.queryLibrary.map(query => `
            <div class="query-item" data-query-id="${query.id}">
                <div class="query-name">${query.name}</div>
                <div class="query-description">${query.description}</div>
                <button class="btn btn-sm" onclick="window.inhousePrintController.loadQuery('${query.id}')">
                    <i class="fas fa-edit"></i>
                    Use Query
                </button>
            </div>
        `).join('');
    }

    loadQuery(queryId) {
        const query = this.queryLibrary.find(q => q.id === queryId);
        if (query) {
            document.getElementById('custom-sql-query').value = query.sql;
        }
    }

    async executeCustomQuery() {
        const query = document.getElementById('custom-sql-query').value.trim();

        if (!query) {
            alert('Please enter a SQL query');
            return;
        }

        console.log('[InHousePrint] Executing query...');

        try {
            const response = await fetch('/api/inhouse/execute-sql', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, user_id: this.userId || 1 })
            });

            const data = await response.json();

            if (data.success) {
                this.renderQueryResults(data.results);
            } else {
                alert(`Query failed: ${data.error}`);
            }

        } catch (error) {
            console.error('[InHousePrint] Query execution failed:', error);
            alert('Failed to execute query');
        }
    }

    renderQueryResults(results) {
        const container = document.getElementById('query-results');
        const tableContainer = document.getElementById('query-results-table');

        if (!results || results.length === 0) {
            tableContainer.innerHTML = '<p class="no-data">No results</p>';
            container.style.display = 'block';
            return;
        }

        // Build table HTML
        const columns = Object.keys(results[0]);
        const html = `
            <table class="results-table">
                <thead>
                    <tr>
                        ${columns.map(col => `<th>${col}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${results.map(row => `
                        <tr>
                            ${columns.map(col => `<td>${row[col] || ''}</td>`).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        tableContainer.innerHTML = html;
        container.style.display = 'block';
    }

    async loadCalculatorParams(productType) {
        console.log('[InHousePrint] Loading calculator params for:', productType);

        try {
            const response = await fetch(`/api/calculator-requirements?product=${productType}`);
            const data = await response.json();

            // Render dynamic parameter form
            const container = document.getElementById('calculator-params');
            // TODO: Implement dynamic form generation

        } catch (error) {
            console.error('[InHousePrint] Failed to load calculator params:', error);
        }
    }

    async calculateQuote() {
        const productType = document.getElementById('product-type').value;

        console.log('[InHousePrint] Calculating quote for:', productType);

        // Collect parameters based on product type
        // TODO: Implement quote calculation

        try {
            const response = await fetch(`/api/calculator/${productType}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({/* params */ })
            });

            const data = await response.json();

            if (data.success) {
                this.renderQuoteResult(data.quote);
            } else {
                alert(`Calculation failed: ${data.error}`);
            }

        } catch (error) {
            console.error('[InHousePrint] Quote calculation failed:', error);
        }
    }

    renderQuoteResult(quote) {
        const container = document.getElementById('quote-result');
        const detailsContainer = document.getElementById('quote-details');

        detailsContainer.innerHTML = `
            <div class="quote-summary">
                <div class="quote-price">
                    <strong>Total Price:</strong>
                    $${quote.total_price?.toFixed(2)}
                </div>
                <div class="quote-breakdown">
                    ${quote.breakdown ? this.renderBreakdown(quote.breakdown) : ''}
                </div>
            </div>
        `;

        container.style.display = 'block';
    }

    renderBreakdown(breakdown) {
        return Object.entries(breakdown).map(([key, value]) => `
            <div class="breakdown-item">
                <span>${key}:</span>
                <span>${value}</span>
            </div>
        `).join('');
    }

    async loadStockLevels() {
        console.log('[InHousePrint] Loading stock levels...');

        try {
            const response = await fetch('/api/inhouse/stock-levels');
            const data = await response.json();

            this.stockLevels = data.stock || [];
            this.renderStockLevels();

        } catch (error) {
            console.error('[InHousePrint] Failed to load stock levels:', error);
            this.showError('stock-levels-list', 'Failed to load stock levels');
        }
    }

    renderStockLevels() {
        const container = document.getElementById('stock-levels-list');

        if (this.stockLevels.length === 0) {
            container.innerHTML = '<p class="no-data">No stock data</p>';
            return;
        }

        container.innerHTML = this.stockLevels.map(stock => `
            <div class="stock-item ${stock.quantity < stock.reorder_level ? 'low-stock' : ''}">
                <div class="stock-name">${stock.name}</div>
                <div class="stock-quantity">
                    <strong>${stock.quantity}</strong> ${stock.unit}
                    ${stock.quantity < stock.reorder_level ? '<span class="badge badge-warning">Low</span>' : ''}
                </div>
            </div>
        `).join('');
    }

    async loadReorderAlerts() {
        console.log('[InHousePrint] Loading reorder alerts...');

        try {
            const response = await fetch('/api/inhouse/reorder-alerts');
            const data = await response.json();

            this.renderReorderAlerts(data.alerts || []);

        } catch (error) {
            console.error('[InHousePrint] Failed to load reorder alerts:', error);
            this.showError('reorder-alerts-list', 'Failed to load alerts');
        }
    }

    renderReorderAlerts(alerts) {
        const container = document.getElementById('reorder-alerts-list');

        if (alerts.length === 0) {
            container.innerHTML = '<p class="no-data">No alerts</p>';
            return;
        }

        container.innerHTML = alerts.map(alert => `
            <div class="alert-item alert-${alert.severity}">
                <i class="fas fa-exclamation-triangle"></i>
                <div class="alert-content">
                    <div class="alert-title">${alert.item_name}</div>
                    <div class="alert-message">${alert.message}</div>
                </div>
            </div>
        `).join('');
    }

    filterQueries(searchTerm) {
        const items = document.querySelectorAll('.query-item');
        const term = searchTerm.toLowerCase();

        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(term) ? 'block' : 'none';
        });
    }

    filterStock(searchTerm) {
        const items = document.querySelectorAll('.stock-item');
        const term = searchTerm.toLowerCase();

        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(term) ? 'block' : 'none';
        });
    }

    showError(containerId, message) {
        const container = document.getElementById(containerId);
        container.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                ${message}
            </div>
        `;
    }
}

// Create global instance
window.inhousePrintController = new InHousePrintController();
