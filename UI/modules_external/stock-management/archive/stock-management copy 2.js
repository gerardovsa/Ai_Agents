/**
 * Stock Management Module
 * Complete inventory management, analytics, and AI-powered invoice processing
 * 
 * @class StockManagementModule
 * @extends BaseModule
 * @created October 30, 2025
 * @updated November 6, 2025 - Combined with enhanced features
 * 
 * Features:
 * - Invoice Processing with AI extraction
 * - Usage Analytics with Plotly.js charts
 * - Reorder Dashboard with alerts and pie charts
 * - Profit Analysis with dual-axis charts
 * - SQL Viewer with inline editing
 * - AI Usage Analytics
 */

// ============================================================================
// PLOTLY CHART HELPERS
// ============================================================================

class PlotlyChartHelper {
    /**
     * Create usage analytics bar chart
     */
    static createUsageChart(data, containerId) {
        const trace = {
            x: data.map(row => `Stock #${row.StockID} (${row.StockType})`),
            y: data.map(row => row.usage_count || 0),
            type: 'bar',
            marker: {
                color: '#3b82f6',
                line: { color: '#1e40af', width: 1 }
            },
            text: data.map(row => row.usage_count),
            textposition: 'outside'
        };

        const layout = {
            title: 'Top Stock Usage (90 Days)',
            xaxis: { title: 'Stock Type', tickangle: -45 },
            yaxis: { title: 'Number of Jobs' },
            margin: { l: 60, r: 30, t: 60, b: 120 },
            height: 400
        };

        Plotly.newPlot(containerId, [trace], layout, { responsive: true });
    }

    /**
     * Create profit analysis charts
     */
    static createProfitCharts(data, containerId) {
        // Profit by stock - Bar chart
        const trace1 = {
            x: data.map(row => `#${row.stock_id}`),
            y: data.map(row => row.gross_profit || 0),
            type: 'bar',
            name: 'Gross Profit',
            marker: { color: '#10b981' }
        };

        // Margin percentage - Line chart
        const trace2 = {
            x: data.map(row => `#${row.stock_id}`),
            y: data.map(row => row.margin_percent || 0),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Margin %',
            yaxis: 'y2',
            marker: { color: '#f59e0b', size: 8 }
        };

        const layout = {
            title: 'Profit Analysis by Stock',
            xaxis: { title: 'Stock ID' },
            yaxis: { title: 'Gross Profit ($)' },
            yaxis2: {
                title: 'Margin (%)',
                overlaying: 'y',
                side: 'right'
            },
            height: 450,
            showlegend: true
        };

        Plotly.newPlot(containerId, [trace1, trace2], layout, { responsive: true });
    }

    /**
     * Create reorder alerts pie chart
     */
    static createReorderAlertsChart(summary, containerId) {
        const data = [{
            values: [summary.critical, summary.moderate, summary.upcoming],
            labels: ['Critical', 'Moderate', 'Upcoming'],
            type: 'pie',
            marker: {
                colors: ['#ef4444', '#f59e0b', '#3b82f6']
            },
            textinfo: 'label+value+percent',
            hoverinfo: 'label+value+percent'
        }];

        const layout = {
            title: 'Stock Reorder Alerts',
            height: 350,
            showlegend: true
        };

        Plotly.newPlot(containerId, data, layout, { responsive: true });
    }
}

// ============================================================================
// SQL VIEWER HELPER
// ============================================================================

class SQLViewerHelper {
    constructor(module) {
        this.module = module;
        this.queryHistory = [];
    }

    /**
     * Render SQL viewer interface
     */
    renderInterface(containerId) {
        const container = document.getElementById(containerId);

        container.innerHTML = `
            <div class="sql-viewer-container">
                <div class="sql-editor-section">
                    <div class="editor-header">
                        <h3>SQL Query Editor</h3>
                        <div class="editor-actions">
                            <button class="btn btn-primary" onclick="stockModule.executeSQLQuery()">
                                ▶ Execute Query
                            </button>
                            <button class="btn btn-secondary" onclick="stockModule.clearSQLQuery()">
                                Clear
                            </button>
                            <button class="btn btn-secondary" onclick="stockModule.loadTableList()">
                                📋 Show Tables
                            </button>
                        </div>
                    </div>
                    <textarea 
                        id="sql-query-editor" 
                        class="sql-editor" 
                        placeholder="Enter SQL query...&#10;Example: SELECT * FROM unified_stocks LIMIT 10"
                        rows="8"
                    >SELECT * FROM unified_stocks LIMIT 10</textarea>
                    <div class="query-hints">
                        <strong>Available Tables:</strong> 
                        <code>unified_stocks</code>, 
                        <code>extracted_jobs</code>, 
                        <code>job_stocks</code>
                    </div>
                </div>

                <div class="sql-results-section">
                    <div id="sql-execution-info" class="execution-info"></div>
                    <div id="sql-results-grid" class="results-grid"></div>
                </div>

                <div class="query-history-section">
                    <h4>Query History</h4>
                    <div id="query-history-list" class="history-list"></div>
                </div>
            </div>
        `;
    }

    /**
     * Execute SQL query
     */
    async executeQuery() {
        const editor = document.getElementById('sql-query-editor');
        const query = editor.value.trim();

        if (!query) {
            this.showError('Please enter a SQL query');
            return;
        }

        try {
            const response = await fetch(`${this.module.backendUrl}/api/stock-management/sql-query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            const result = await response.json();

            if (result.status === 'ok') {
                this.displayResults(result);
                this.addToHistory(query, result);
            } else {
                this.showError(result.message || 'Query failed');
            }

        } catch (error) {
            this.showError(error.message);
        }
    }

    /**
     * Display query results in table
     */
    displayResults(result) {
        const infoDiv = document.getElementById('sql-execution-info');
        const gridDiv = document.getElementById('sql-results-grid');

        // Show execution info
        infoDiv.innerHTML = `
            <div class="success-banner">
                ✓ Query executed successfully
                <span class="execution-stats">
                    ${result.row_count} rows | ${result.execution_time_ms}ms
                </span>
            </div>
        `;

        // Build results table
        if (result.data && result.data.length > 0) {
            const columns = result.columns || Object.keys(result.data[0]);

            let html = `
                <table class="results-table editable-table">
                    <thead>
                        <tr>
                            ${columns.map(col => `<th>${col}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
            `;

            result.data.forEach((row, rowIndex) => {
                html += '<tr>';
                columns.forEach(col => {
                    const value = row[col] !== null ? row[col] : 'NULL';
                    html += `
                        <td 
                            contenteditable="true"
                            data-row="${rowIndex}"
                            data-column="${col}"
                            data-original="${value}"
                            onblur="stockModule.handleCellEdit(this, '${col}', ${rowIndex})"
                        >
                            ${value}
                        </td>
                    `;
                });
                html += '</tr>';
            });

            html += '</tbody></table>';
            gridDiv.innerHTML = html;
        } else {
            gridDiv.innerHTML = '<div class="info-message">No results returned</div>';
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        const infoDiv = document.getElementById('sql-execution-info');
        infoDiv.innerHTML = `
            <div class="error-banner">
                ✗ Error: ${message}
            </div>
        `;
    }

    /**
     * Add query to history
     */
    addToHistory(query, result) {
        this.queryHistory.unshift({
            query,
            timestamp: new Date().toLocaleTimeString(),
            rows: result.row_count
        });

        if (this.queryHistory.length > 10) {
            this.queryHistory.pop();
        }

        this.updateHistoryDisplay();
    }

    /**
     * Update history display
     */
    updateHistoryDisplay() {
        const historyDiv = document.getElementById('query-history-list');

        historyDiv.innerHTML = this.queryHistory.map((item, index) => `
            <div class="history-item" onclick="stockModule.loadHistoryQuery(${index})">
                <div class="history-time">${item.timestamp}</div>
                <div class="history-query">${item.query.substring(0, 60)}...</div>
                <div class="history-rows">${item.rows} rows</div>
            </div>
        `).join('');
    }
}

// ============================================================================
// CELL EDITING HELPER
// ============================================================================

class CellEditingHelper {
    constructor(module) {
        this.module = module;
    }

    /**
     * Handle cell edit
     */
    async handleEdit(cell, column, rowIndex) {
        const newValue = cell.textContent.trim();
        const originalValue = cell.dataset.original;

        if (newValue === originalValue) {
            return; // No change
        }

        // Determine table and where clause from query context
        const query = document.getElementById('sql-query-editor').value;
        const table = this.extractTableFromQuery(query);

        if (!table) {
            alert('Cannot determine table for update. Query must start with SELECT ... FROM table_name');
            cell.textContent = originalValue;
            return;
        }

        // Get primary key column and value
        const pkColumn = table === 'unified_stocks' ? 'stock_id' : 'id';
        const resultsTable = cell.closest('table');
        const row = cell.closest('tr');
        const pkCell = row.cells[0]; // Assume first column is PK
        const pkValue = pkCell.textContent;

        try {
            const response = await fetch(`${this.module.backendUrl}/api/stock-management/update-cell`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    table,
                    column,
                    value: newValue,
                    where_column: pkColumn,
                    where_value: pkValue
                })
            });

            const result = await response.json();

            if (result.status === 'ok') {
                cell.dataset.original = newValue;
                cell.style.backgroundColor = '#d1fae5'; // Green highlight
                setTimeout(() => {
                    cell.style.backgroundColor = '';
                }, 2000);

                this.showSuccess(`Updated ${table}.${column}`);
            } else {
                throw new Error(result.message);
            }

        } catch (error) {
            alert(`Failed to update: ${error.message}`);
            cell.textContent = originalValue;
        }
    }

    /**
     * Extract table name from SELECT query
     */
    extractTableFromQuery(query) {
        const match = query.match(/FROM\s+(\w+)/i);
        return match ? match[1] : null;
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        const infoDiv = document.getElementById('sql-execution-info');
        const tempDiv = document.createElement('div');
        tempDiv.className = 'success-banner';
        tempDiv.textContent = `✓ ${message}`;
        tempDiv.style.position = 'fixed';
        tempDiv.style.top = '20px';
        tempDiv.style.right = '20px';
        tempDiv.style.zIndex = '9999';
        document.body.appendChild(tempDiv);

        setTimeout(() => tempDiv.remove(), 3000);
    }
}

// ============================================================================
// STOCK MANAGEMENT MODULE (Main Class)
// ============================================================================

class StockManagementModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);

        // Configuration
        this.apiEndpoint = '/api/stock-management';
        this.backendUrl = 'http://localhost:5001';

        // State management
        this.currentPeriod = 90; // Default 90 days
        this.charts = {}; // Store Chart.js instances
        this.editingCell = null; // Track inline editing

        // Data cache
        this.stockData = [];
        this.usageData = null;
        this.reorderData = null;
        this.profitData = null;

        // Helper instances (initialized after module loads)
        this.sqlViewer = null;
        this.cellEditor = null;

        console.log('[INIT] StockManagementModule created');
    }

    async initialize() {
        await super.initialize();

        console.log('[INIT] Initializing Stock Management Module...');

        // Load manifest settings
        if (this.manifest && this.manifest.settings) {
            this.apiEndpoint = this.manifest.settings.api_endpoint || this.apiEndpoint;
            this.backendUrl = this.manifest.settings.backend_url || this.backendUrl;
        }

        // Initialize helper classes
        this.sqlViewer = new SQLViewerHelper(this);
        this.cellEditor = new CellEditingHelper(this);
        console.log('[INIT] Helper classes initialized (SQL Viewer, Cell Editor)');

        // Check backend connectivity
        await this.checkBackendConnection();

        console.log('Stock Management Module initialized');
    }

    async checkBackendConnection() {
        try {
            const response = await fetch(`${this.backendUrl}/health`, {
                method: 'GET',
                timeout: 3000
            });

            if (response.ok) {
                console.log('Backend connection established');
                return true;
            } else {
                console.warn('[WARN] Backend health check failed');
                return false;
            }
        } catch (error) {
            console.warn('[WARN] Backend not reachable:', error.message);
            return false;
        }
    }

    initializeSubTabs() {
        console.log('� [INIT] Scheduling Stock Management sub-tabs initialization...');

        // Use requestAnimationFrame to ensure DOM is fully rendered
        requestAnimationFrame(() => {
            // Verify all required containers exist (BaseModule should have created them)
            const requiredTabs = [
                'invoice-processing',
                'usage-analytics',
                'reorder-dashboard',
                'profit-analysis',
                'sql-viewer',
                'ai-analytics'
            ];

            // Check each container individually with detailed logging
            console.log('🔍 [CHECK] Checking for required containers...');
            const containerStatus = requiredTabs.map(tabId => {
                const container = this.getSubTabContainer(tabId);
                const found = !!container;
                console.log(`   ${found ? '✅' : '❌'} ${this.moduleId}-subtab-${tabId}`);
                return { tabId, found, container };
            });

            const missingTabs = containerStatus.filter(s => !s.found).map(s => s.tabId);

            if (missingTabs.length > 0) {
                console.error('❌ [INIT] Missing sub-tab containers:', missingTabs);
                console.error('❌ [DEBUG] Module ID:', this.moduleId);
                console.error('❌ [DEBUG] Expected ID format:', `${this.moduleId}-subtab-{tabId}`);

                // List what we actually found
                const allContainers = document.querySelectorAll(`[id^="${this.moduleId}-subtab-"]`);
                console.error('❌ [DEBUG] Found containers:', Array.from(allContainers).map(el => el.id));
                console.error('❌ [DEBUG] DOM state - module container exists:', !!this.container);
                console.error('❌ [DEBUG] DOM state - module container id:', this.container?.id);
                return;
            }

            console.log('✅ [INIT] All sub-tab containers found. Initializing content...');

            // Initialize all 6 tabs
            this.initializeInvoiceProcessingTab();
            this.initializeUsageAnalyticsTab();
            this.initializeReorderDashboardTab();
            this.initializeProfitAnalysisTab();
            this.initializeSQLViewerTab();
            this.initializeAIAnalyticsTab();

            console.log('✅ [INIT] All sub-tabs initialized successfully');
        });
    }

    // ========================================================================
    // MODULE LIFECYCLE METHODS (Override BaseModule behavior)
    // ========================================================================

    onRefresh() {
        console.log('[REFRESH] Refreshing Stock Management Module...');

        // Refresh the currently active sub-tab
        if (!this.activeSubTab) {
            console.warn('[WARN] No active sub-tab to refresh');
            return;
        }

        switch (this.activeSubTab) {
            case 'invoice-processing':
                this.refreshInvoiceTab();
                break;
            case 'usage-analytics':
                this.refreshUsageAnalyticsTab();
                break;
            case 'reorder-dashboard':
                this.refreshReorderDashboardTab();
                break;
            case 'profit-analysis':
                this.refreshProfitAnalysisTab();
                break;
            case 'sql-viewer':
                this.refreshSQLViewerTab();
                break;
            case 'ai-analytics':
                this.refreshAIAnalyticsTab();
                break;
            default:
                console.log('[REFRESH] No specific refresh handler for:', this.activeSubTab);
        }
    }

    onSubTabActivate(subTabId) {
        console.log('[TAB] Stock Management sub-tab activated:', subTabId);
        this.activeSubTab = subTabId;

        // FIXED: Disabled auto-loading of data on tab activation
        // User must click the refresh button to load data for each tab
        // This prevents unnecessary API calls and gives user control
        console.log(`   → Tab content ready. Click 'Refresh' button to load data.`);
    }

    onRefresh() {
        console.log('[REFRESH] Refreshing Stock Management data (NOT reloading page)...');

        // Refresh data for currently active tab
        switch (this.activeSubTab) {
            case 'invoice-processing':
                console.log('Refreshing invoice processing tab...');
                // Clear upload state if needed
                break;
            case 'usage-analytics':
                console.log('Refreshing usage analytics...');
                // Re-fetch analytics data
                this.loadUsageAnalytics(this.currentPeriod);
                break;
            case 'reorder-dashboard':
                console.log('Refreshing reorder dashboard...');
                // Re-fetch reorder data
                break;
            case 'profit-analysis':
                console.log('Refreshing profit analysis...');
                // Re-fetch profit data
                break;
            case 'sql-viewer':
                console.log('Refreshing SQL viewer...');
                // Re-execute last query if any
                break;
            case 'ai-analytics':
                console.log('Refreshing AI analytics...');
                // Re-fetch AI usage data
                break;
            default:
                console.log('Unknown tab, no refresh action');
        }
    }

    onSettings() {
        console.log('⚙️ Stock Management settings requested');
        alert('Stock Management settings coming soon!\n\n' +
            'Will include:\n' +
            '- API endpoint configuration\n' +
            '- Default time periods\n' +
            '- Alert thresholds\n' +
            '- Export options');
    }

    onSubTabActivate(subTabId) {
        console.log(`[TAB] Stock Management sub-tab activated: ${subTabId}`);

        // Load data when switching to certain tabs
        switch (subTabId) {
            case 'usage-analytics':
                // Auto-load analytics if not already loaded
                if (!this.usageData) {
                    this.loadUsageAnalytics(this.currentPeriod);
                }
                break;
            case 'reorder-dashboard':
                // Auto-load reorder data
                if (!this.reorderData) {
                    this.loadReorderDashboard();
                }
                break;
            case 'profit-analysis':
                // Auto-load profit data
                if (!this.profitData) {
                    this.loadProfitAnalysis(this.currentPeriod);
                }
                break;
        }
    }

    // ========================================================================
    // TAB 1: INVOICE PROCESSING
    // ========================================================================

    initializeInvoiceProcessingTab() {
        const tab = this.getSubTabContainer('invoice-processing');
        if (!tab) {
            console.error('❌ [INIT] Could not find invoice-processing container');
            return;
        }

        console.log('✅ [INIT] Initializing Invoice Processing tab...');

        tab.innerHTML = `
            <div class="module-dashboard">
                <div class="dashboard-card">
                    <div class="card-header">
                        <div class="header-left">
                            <h3 class="card-title">
                                <i class="fas fa-file-invoice"></i> AI Invoice Processing
                            </h3>
                            <div class="card-subtitle">
                                Upload supplier invoices for automatic extraction and stock matching
                            </div>
                        </div>
                        <div class="header-right">
                            <button class="btn btn-secondary" id="invoice-refresh-btn" onclick="stockModule.refreshInvoiceTab()">
                                <i class="fas fa-sync-alt"></i> Clear
                            </button>
                        </div>
                    </div>
                    <div class="card-content">
                        <!-- Upload Area -->
                        <div class="upload-zone" id="invoice-upload-zone">
                            <div class="upload-icon">
                                <i class="fas fa-cloud-upload-alt"></i>
                            </div>
                            <div class="upload-text">
                                <h4>Drag & Drop Invoice Here</h4>
                                <p>or click to browse (PDF, JPG, PNG)</p>
                            </div>
                            <input type="file" 
                                   id="invoice-file-input" 
                                   accept=".pdf,.jpg,.jpeg,.png"
                                   style="display: none;">
                        </div>
                        
                        <!-- Processing Status -->
                        <div id="invoice-processing-status" style="display: none;">
                            <div class="processing-indicator">
                                <i class="fas fa-spinner fa-spin"></i>
                                <span id="processing-message">Processing invoice...</span>
                            </div>
                        </div>
                        
                        <!-- Results Area -->
                        <div id="invoice-results" style="display: none;">
                            <!-- Will be populated with extraction results -->
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Setup event handlers
        this.setupInvoiceUploadHandlers();
    }

    setupInvoiceUploadHandlers() {
        const uploadZone = document.getElementById('invoice-upload-zone');
        const fileInput = document.getElementById('invoice-file-input');

        if (!uploadZone || !fileInput) return;

        // Click to upload
        uploadZone.addEventListener('click', () => {
            fileInput.click();
        });

        // File selected
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleInvoiceUpload(e.target.files[0]);
            }
        });

        // Drag and drop
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');

            if (e.dataTransfer.files.length > 0) {
                this.handleInvoiceUpload(e.dataTransfer.files[0]);
            }
        });
    }

    async handleInvoiceUpload(file) {
        console.log('📄 Processing invoice:', file.name);

        // Show processing indicator
        document.getElementById('invoice-upload-zone').style.display = 'none';
        document.getElementById('invoice-processing-status').style.display = 'block';
        document.getElementById('processing-message').textContent = 'Reading file...';

        try {
            // Read file as base64
            const base64 = await this.readFileAsBase64(file);

            document.getElementById('processing-message').textContent = 'Sending to AI for extraction...';

            // Send to backend for AI processing
            const response = await fetch(`${this.backendUrl}${this.apiEndpoint}/invoice-process`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    file_base64: base64,
                    file_type: file.type,
                    file_name: file.name
                })
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const result = await response.json();

            // Display results
            this.displayInvoiceResults(result);

        } catch (error) {
            console.error(' Invoice processing failed:', error);
            this.showError('invoice-processing-status', 'Failed to process invoice: ' + error.message);
        }
    }

    readFileAsBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    displayInvoiceResults(result) {
        // Hide processing, show results
        document.getElementById('invoice-processing-status').style.display = 'none';
        const resultsDiv = document.getElementById('invoice-results');
        resultsDiv.style.display = 'block';

        // Placeholder for full implementation
        resultsDiv.innerHTML = `
            <div class="results-header">
                <h4>Extraction Results</h4>
                <button class="btn btn-secondary" onclick="location.reload()">
                    <i class="fas fa-redo"></i> Process Another
                </button>
            </div>
            <div class="extraction-summary">
                <p><strong>Supplier:</strong> ${result.supplier || 'Not detected'}</p>
                <p><strong>Invoice #:</strong> ${result.invoice_number || 'Not detected'}</p>
                <p><strong>Items Extracted:</strong> ${result.items?.length || 0}</p>
            </div>
            <div class="info-message">
                <i class="fas fa-info-circle"></i>
                Full implementation coming in Phase 7
            </div>
        `;
    }

    // ========================================================================
    // TAB 2: USAGE ANALYTICS
    // ========================================================================

    initializeUsageAnalyticsTab() {
        const tab = this.getSubTabContainer('usage-analytics');
        if (!tab) {
            console.error('❌ [INIT] Could not find usage-analytics container');
            return;
        }

        console.log('✅ [INIT] Initializing Usage Analytics tab...');

        tab.innerHTML = `
            <div class="module-dashboard">
                <!-- Card Header with Title and Subtitle -->
                <div class="dashboard-card">
                    <div class="card-header">
                        <div class="header-left" style="width: 100%; display: flex; flex-direction: column; gap: 8px; text-align: center;">
                            <h3 class="card-title" style="font-size: 24px; margin: 0;">
                                <i class="fas fa-chart-line"></i> Usage Analytics
                            </h3>
                            <div class="card-subtitle" style="margin: 0;">
                                Stock consumption trends and patterns
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Summary Metrics -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon primary">
                            <i class="fas fa-boxes"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Total Stocks Used</div>
                            <div class="stat-value" id="total-stocks-used">-</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon success">
                            <i class="fas fa-layer-group"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Total Sheets</div>
                            <div class="stat-value" id="total-sheets-used">-</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon warning">
                            <i class="fas fa-fire"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Fast Movers</div>
                            <div class="stat-value" id="fast-movers-count">-</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon info">
                            <i class="fas fa-turtle"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Slow Movers</div>
                            <div class="stat-value" id="slow-movers-count">-</div>
                        </div>
                    </div>
                </div>
                
                <!-- Toolbar -->
                <div class="bulk-operations-toolbar" style="display: flex; align-items: center; gap: 12px; padding: 16px 20px; background: #1a1f2e; border-bottom: 1px solid #2a3142; margin-bottom: 20px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <select id="usage-period-selector" class="form-control" style="margin: 0; width: auto; padding: 6px 10px; background: #0B0E13; border: 1px solid #2A3142; border-radius: 6px; color: #E5E7EB; font-size: 12px;">
                            <option value="30">Last 30 Days</option>
                            <option value="90" selected>Last 90 Days</option>
                            <option value="180">Last 180 Days</option>
                            <option value="365">Last Year</option>
                        </select>
                        <button class="btn btn-primary" id="usage-refresh-btn" onclick="stockModule.refreshUsageAnalyticsTab()" style="padding: 6px 12px; font-size: 12px;">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                </div>
                
                <!-- Charts -->
                <div class="dashboard-card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <i class="fas fa-chart-bar"></i> Usage Analytics Data
                        </h3>
                    </div>
                    <div class="card-content">
                        <div id="analytics-loading" class="loading-state" style="display: none;">
                            <i class="fas fa-spinner fa-spin"></i> Loading analytics...
                        </div>
                        <div id="analytics-ready" class="ready-state" style="text-align: center; padding: 40px; color: #9ca3af;">
                            <i class="fas fa-info-circle" style="font-size: 32px; color: #4ec9b0; margin-bottom: 10px; display: block;"></i>
                            <p style="margin: 0; font-size: 16px;">Click the <strong>Refresh</strong> button to load usage analytics data</p>
                            <p style="margin: 5px 0 0 0; font-size: 12px; color: #6b7280;">Select timeframe from dropdown and click Refresh</p>
                        </div>
                        <div id="analytics-table-container" style="display: none; min-height: 400px;"></div>
                    </div>
                </div>
            </div>
        `;

        // Setup event handlers
        document.getElementById('usage-period-selector')?.addEventListener('change', (e) => {
            this.currentPeriod = parseInt(e.target.value);
            this.loadUsageAnalytics();
        });

        // FIXED: Removed auto-loading. User must click Refresh button.
    }

    async loadUsageAnalytics() {
        console.log(`[LOAD] Loading usage analytics for ${this.currentPeriod} days...`);

        const loadingDiv = document.getElementById('analytics-loading');
        const readyDiv = document.getElementById('analytics-ready');
        const tableContainer = document.getElementById('analytics-table-container');

        if (loadingDiv) loadingDiv.style.display = 'block';
        if (readyDiv) readyDiv.style.display = 'none';
        if (tableContainer) tableContainer.style.display = 'none';

        try {
            // Call the REAL backend API
            const response = await fetch(
                `${this.backendUrl}/api/stock-management/usage-analytics?days=${this.currentPeriod}&group_by=month`
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.status !== 'ok') {
                throw new Error(result.message || 'Failed to load usage analytics');
            }

            console.log('[OK] Usage analytics loaded:', result.data.length, 'records');

            // Update summary stats
            const data = result.data || [];
            const totalStocks = data.length;
            const totalUsage = data.reduce((sum, item) => sum + (item.usage_count || 0), 0);
            const totalSheets = data.reduce((sum, item) => sum + (item.total_quantity || 0), 0);

            // Fast movers = usage > average
            const avgUsage = totalUsage / (totalStocks || 1);
            const fastMovers = data.filter(item => item.usage_count > avgUsage).length;
            const slowMovers = data.filter(item => item.usage_count < avgUsage).length;

            document.getElementById('total-stocks-used').textContent = totalStocks;
            document.getElementById('total-sheets-used').textContent = totalSheets.toLocaleString();
            document.getElementById('fast-movers-count').textContent = fastMovers;
            document.getElementById('slow-movers-count').textContent = slowMovers;

            // Render Tabulator table
            this.renderUsageTable(data);

            if (loadingDiv) loadingDiv.style.display = 'none';
            if (tableContainer) tableContainer.style.display = 'block';

        } catch (error) {
            console.error('[ERROR] Failed to load usage analytics:', error);

            if (loadingDiv) {
                loadingDiv.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-circle"></i>
                        <p>Failed to load usage analytics</p>
                        <p class="error-details">${error.message}</p>
                        <button class="btn btn-secondary" onclick="stockModule.loadUsageAnalytics()">
                            <i class="fas fa-redo"></i> Retry
                        </button>
                    </div>
                `;
                loadingDiv.style.display = 'block';
            }
        }
    }

    renderUsageTable(data) {
        const container = document.getElementById('analytics-table-container');
        if (!container) {
            console.warn('[WARN] Cannot find container: analytics-table-container');
            return;
        }

        // Destroy existing table
        if (this.usageTable) {
            this.usageTable.destroy();
        }

        // Create Tabulator
        this.usageTable = new Tabulator(container, {
            data: data,
            layout: "fitDataStretch",
            pagination: "local",
            paginationSize: 25,
            paginationSizeSelector: [10, 25, 50, 100],
            movableColumns: true,
            resizableColumns: true,
            height: "500px",
            placeholder: "No usage data available",
            columns: [
                {
                    title: "Stock ID",
                    field: "StockID",
                    width: 120,
                    headerSort: true,
                    headerFilter: "input",
                    formatter: function (cell) {
                        return `<span style="font-weight: 600; color: #0078d4;">${cell.getValue()}</span>`;
                    }
                },
                {
                    title: "Stock Type",
                    field: "StockType",
                    width: 200,
                    headerSort: true,
                    headerFilter: "input"
                },
                {
                    title: "GSM",
                    field: "GSM",
                    width: 100,
                    headerSort: true,
                    hozAlign: "center"
                },
                {
                    title: "Dimensions",
                    field: "Dimensions",
                    width: 150,
                    headerSort: true,
                    hozAlign: "center"
                },
                {
                    title: "Usage Count",
                    field: "usage_count",
                    width: 130,
                    headerSort: true,
                    hozAlign: "right",
                    formatter: function (cell) {
                        const value = cell.getValue() || 0;
                        return `<span style="font-weight: 700; color: #10b981;">${value.toLocaleString()}</span>`;
                    }
                },
                {
                    title: "Total Sheets",
                    field: "total_quantity",
                    width: 140,
                    headerSort: true,
                    hozAlign: "right",
                    formatter: function (cell) {
                        const value = cell.getValue() || 0;
                        return `<span style="font-weight: 700;">${value.toLocaleString()}</span>`;
                    }
                }
            ]
        });

        console.log('[TABULATOR] Usage analytics table rendered with', data.length, 'rows');
    }

    async loadUsageAnalyticsData() {
        // Alias for compatibility
        return this.loadUsageAnalytics();
    }

    refreshUsageAnalyticsTab() {
        console.log('[REFRESH] Refreshing usage analytics tab...');
        this.loadUsageAnalytics();
    }

    // ========================================================================
    // TAB 3: REORDER DASHBOARD
    // ========================================================================

    initializeReorderDashboardTab() {
        const tab = this.getSubTabContainer('reorder-dashboard');
        if (!tab) {
            console.error('❌ [INIT] Could not find reorder-dashboard container');
            return;
        }

        console.log('✅ [INIT] Initializing Reorder Dashboard tab with Tabulator...');

        tab.innerHTML = `
            <div class="sm-module-dashboard">
                <!-- Card Header with Title and Subtitle -->
                <div class="dashboard-card">
                    <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="sm-header-left">
                            <h3 class="card-title" style="font-size: 20px; margin: 0;">
                                <i class="fas fa-bell"></i> Reorder Dashboard
                            </h3>
                            <div class="sm-card-subtitle">
                                Stock alerts and reorder recommendations
                            </div>
                        </div>
                        <div class="sm-header-right" style="display: flex; gap: 12px; align-items: center;">
                            <span id="reorder-count-badge" class="badge" style="background: #0078d4; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 700;">
                                0 stocks
                            </span>
                            <select id="reorder-limit-selector" class="form-control" style="width: auto; padding: 6px 10px;">
                                <option value="10">Show 10</option>
                                <option value="25" selected>Show 25</option>
                                <option value="50">Show 50</option>
                                <option value="100">Show 100</option>
                                <option value="all">Show All</option>
                            </select>
                            <div class="sm-font-controls" style="display: flex; gap: 4px;">
                                <button class="btn btn-sm" onclick="stockModule.adjustFontSize('reorder', -1)" title="Decrease font size">
                                    <i class="fas fa-minus"></i>
                                </button>
                                <button class="btn btn-sm" onclick="stockModule.adjustFontSize('reorder', 1)" title="Increase font size">
                                    <i class="fas fa-plus"></i>
                                </button>
                            </div>
                            <button class="btn btn-primary" onclick="stockModule.exportReorderToExcel()" title="Export to Excel">
                                <i class="fas fa-file-excel"></i> Export
                            </button>
                            <button class="btn btn-primary" onclick="stockModule.refreshReorderDashboardTab()">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Summary Cards -->
                <div class="sm-stats-grid">
                    <div class="sm-stat-card sm-critical">
                        <div class="sm-stat-icon"><i class="fas fa-exclamation-triangle"></i></div>
                        <div class="sm-stat-content">
                            <div class="sm-stat-label">Critical Stock</div>
                            <div class="sm-stat-value" id="reorder-critical-count">--</div>
                        </div>
                    </div>
                    <div class="sm-stat-card sm-warning">
                        <div class="sm-stat-icon"><i class="fas fa-bell"></i></div>
                        <div class="sm-stat-content">
                            <div class="sm-stat-label">Low Stock</div>
                            <div class="sm-stat-value" id="reorder-low-count">--</div>
                        </div>
                    </div>
                    <div class="sm-stat-card sm-info">
                        <div class="sm-stat-icon"><i class="fas fa-check-circle"></i></div>
                        <div class="sm-stat-content">
                            <div class="sm-stat-label">Adequate Stock</div>
                            <div class="sm-stat-value" id="reorder-adequate-count">--</div>
                        </div>
                    </div>
                    <div class="sm-stat-card">
                        <div class="sm-stat-icon"><i class="fas fa-boxes"></i></div>
                        <div class="sm-stat-content">
                            <div class="sm-stat-label">Total Stocks</div>
                            <div class="sm-stat-value" id="reorder-total-count">--</div>
                        </div>
                    </div>
                </div>

                <!-- Filter Buttons -->
                <div style="display: flex; gap: 8px; margin: 20px 0; flex-wrap: wrap;">
                    <button class="btn btn-sm active" data-filter="all" onclick="stockModule.filterReorderTable('all')" style="padding: 6px 16px;">
                        <i class="fas fa-list"></i> All
                    </button>
                    <button class="btn btn-sm" data-filter="critical" onclick="stockModule.filterReorderTable('critical')" style="padding: 6px 16px; border-color: #ef4444;">
                        <i class="fas fa-exclamation-triangle"></i> Critical
                    </button>
                    <button class="btn btn-sm" data-filter="low" onclick="stockModule.filterReorderTable('low')" style="padding: 6px 16px; border-color: #f97316;">
                        <i class="fas fa-bell"></i> Low Stock
                    </button>
                    <button class="btn btn-sm" data-filter="adequate" onclick="stockModule.filterReorderTable('adequate')" style="padding: 6px 16px; border-color: #22c55e;">
                        <i class="fas fa-check-circle"></i> Adequate
                    </button>
                </div>

                <!-- Search Bar -->
                <div style="margin-bottom: 20px;">
                    <input type="text" id="reorder-search-input" class="form-control" placeholder="🔍 Search by Stock ID, Stock Type, or Supplier..." 
                           style="width: 100%; padding: 10px 16px; background: #0B0E13; border: 1px solid #2A3142; border-radius: 6px; color: #E5E7EB; font-size: 14px;">
                </div>

                <!-- Tabulator Container -->
                <div id="reorder-table-container" style="min-height: 400px; background: #0B0E13; border: 1px solid #2A3142; border-radius: 6px;"></div>
            </div>
        `;

        // Initialize Tabulator after DOM is ready
        setTimeout(() => {
            this.initializeReorderTabulator();
            this.loadReorderDashboard();
        }, 100);
    }

    initializeReorderTabulator() {
        const container = document.getElementById('reorder-table-container');
        if (!container) {
            console.error('❌ Reorder table container not found');
            return;
        }

        console.log('✅ Initializing Reorder Tabulator...');

        // Destroy existing table if any
        if (this.reorderTable) {
            this.reorderTable.destroy();
        }

        // Create Tabulator
        this.reorderTable = new Tabulator(container, {
            data: [],
            layout: "fitDataStretch",
            pagination: "local",
            paginationSize: 25,
            paginationSizeSelector: [10, 25, 50, 100],
            movableColumns: true,
            resizableColumns: true,
            height: "600px",
            placeholder: "No reorder data available. Click Refresh to load.",
            columns: [
                {
                    title: "Stock ID",
                    field: "stock_id",
                    width: 150,
                    headerSort: true,
                    headerFilter: "input",
                    formatter: function (cell) {
                        return `<span style="font-weight: 600; color: #0078d4;">${cell.getValue() || 'N/A'}</span>`;
                    }
                },
                {
                    title: "Stock Type",
                    field: "stock_type",
                    width: 200,
                    headerSort: true,
                    headerFilter: "input"
                },
                {
                    title: "Current Level",
                    field: "current_level",
                    width: 120,
                    headerSort: true,
                    hozAlign: "center",
                    formatter: function (cell) {
                        const value = cell.getValue() || 0;
                        return `<span style="font-weight: 700;">${value}</span>`;
                    }
                },
                {
                    title: "Reorder Point",
                    field: "reorder_point",
                    width: 120,
                    headerSort: true,
                    hozAlign: "center",
                    formatter: function (cell) {
                        return `<span style="color: #f97316;">${cell.getValue() || 100}</span>`;
                    }
                },
                {
                    title: "Status",
                    field: "status",
                    width: 150,
                    headerSort: true,
                    headerFilter: "select",
                    headerFilterParams: { values: { "": "All", "critical": "Critical", "low": "Low", "adequate": "Adequate" } },
                    formatter: function (cell) {
                        const row = cell.getRow().getData();
                        const level = parseInt(row.current_level || 0);
                        const reorderPoint = parseInt(row.reorder_point || 100);

                        let status, color, icon;
                        if (level === 0 || level < (reorderPoint * 0.5)) {
                            status = 'CRITICAL';
                            color = '#ef4444';
                            icon = 'fa-exclamation-triangle';
                        } else if (level < reorderPoint) {
                            status = 'LOW';
                            color = '#f97316';
                            icon = 'fa-bell';
                        } else {
                            status = 'ADEQUATE';
                            color = '#22c55e';
                            icon = 'fa-check-circle';
                        }

                        return `<span style="background: ${color}33; color: ${color}; padding: 4px 12px; border-radius: 4px; font-size: 11px; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;">
                        <i class="fas ${icon}"></i> ${status}
                    </span>`;
                    }
                },
                {
                    title: "Last Order Date",
                    field: "last_order_date",
                    width: 150,
                    headerSort: true,
                    formatter: function (cell) {
                        const value = cell.getValue();
                        if (!value || value === 'N/A') return '<span style="color: #6b7280;">Never</span>';
                        return `<span style="color: #9ca3af;">${value}</span>`;
                    }
                },
                {
                    title: "Supplier",
                    field: "supplier",
                    width: 180,
                    headerSort: true,
                    headerFilter: "input",
                    formatter: function (cell) {
                        return `<span style="color: #e5e7eb;">${cell.getValue() || 'Unknown'}</span>`;
                    }
                },
                {
                    title: "Actions",
                    width: 140,
                    hozAlign: "center",
                    headerSort: false,
                    formatter: function (cell) {
                        return `<button class="btn btn-sm" onclick="stockModule.viewStockDetails('${cell.getRow().getData().stock_id}')" style="padding: 4px 12px; font-size: 11px;">
                        <i class="fas fa-eye"></i> View
                    </button>`;
                    }
                }
            ]
        });

        // Attach search listener
        const searchInput = document.getElementById('reorder-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.reorderTable.setFilter([
                    { field: "stock_id", type: "like", value: e.target.value },
                    { field: "stock_type", type: "like", value: e.target.value },
                    { field: "supplier", type: "like", value: e.target.value }
                ], "or");
            });
        }

        // Attach limit selector listener
        const limitSelector = document.getElementById('reorder-limit-selector');
        if (limitSelector) {
            limitSelector.addEventListener('change', (e) => {
                const value = e.target.value;
                if (value === 'all') {
                    this.reorderTable.setPageSize(this.reorderTable.getDataCount());
                } else {
                    this.reorderTable.setPageSize(parseInt(value));
                }
            });
        }

        console.log('✅ Reorder Tabulator initialized');
    }

    async loadReorderDashboard() {
        console.log('[LOAD] Loading reorder dashboard...');

        const tbody = document.getElementById('reorder-table-body');

        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="10" class="loading-cell">
                        <i class="fas fa-spinner fa-spin"></i> Loading reorder data...
                    </td>
                </tr>
            `;
        }

        try {
            // Call the REAL backend API - reorder dashboard endpoint
            const response = await fetch(
                `${this.backendUrl}/api/stock-management/reorder-dashboard`
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.status !== 'ok') {
                throw new Error(result.message || 'Failed to load reorder data');
            }

            console.log('[OK] Reorder data loaded:', result.data.length, 'stocks');

            const stocks = result.data || [];
            this.reorderData = stocks;

            // Calculate summary statistics
            let critical = 0, low = 0, adequate = 0;

            stocks.forEach(stock => {
                const level = parseInt(stock.current_level || 0);
                const reorderPoint = parseInt(stock.reorder_point || 100);

                if (level === 0 || level < (reorderPoint * 0.5)) {
                    critical++;
                } else if (level < reorderPoint) {
                    low++;
                } else {
                    adequate++;
                }
            });

            // Update summary cards
            document.getElementById('reorder-critical-count').textContent = critical;
            document.getElementById('reorder-low-count').textContent = low;
            document.getElementById('reorder-adequate-count').textContent = adequate;
            document.getElementById('reorder-total-count').textContent = stocks.length;

            // Populate table
            this.populateReorderTable(stocks);

        } catch (error) {
            console.error('[ERROR] Failed to load reorder data:', error);

            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="10" class="error-cell">
                            <div class="error-message">
                                <i class="fas fa-exclamation-circle"></i>
                                <p>Failed to load reorder data</p>
                                <p class="error-details">${error.message}</p>
                                <button class="btn btn-secondary" onclick="stockModule.loadReorderDashboard()">
                                    <i class="fas fa-redo"></i> Retry
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            }
        }
    }

    populateReorderTable(stocks) {
        const tbody = document.getElementById('reorder-table-body');
        if (!tbody) return;

        if (stocks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="10" class="empty-cell">No stocks need reordering</td></tr>';
            return;
        }

        tbody.innerHTML = stocks.map((stock, index) => {
            // Calculate status based on current vs reorder level
            const currentLevel = parseInt(stock.current_level || 0);
            const reorderPoint = parseInt(stock.reorder_point || 100);

            let status, statusClass;
            if (currentLevel === 0 || currentLevel < (reorderPoint * 0.5)) {
                status = 'CRITICAL';
                statusClass = 'status-critical';
            } else if (currentLevel < reorderPoint) {
                status = 'LOW';
                statusClass = 'status-warning';
            } else {
                status = 'OK';
                statusClass = 'status-ok';
            }

            const tag = this.getRowTag ? this.getRowTag(stock.stock_id) : null;

            return `
                <tr class="${tag ? 'tagged-row-' + tag : ''}" data-stock-id="${stock.stock_id}">
                    <td><input type="checkbox" class="stock-checkbox" data-stock-id="${stock.stock_id}"></td>
                    <td class="row-number">${index + 1}</td>
                    <td>
                        <button class="tag-btn ${tag ? 'tag-' + tag : ''}" 
                                onclick="stockModule.toggleRowTag(event, '${stock.stock_id}')" 
                                title="Tag Row">
                            <i class="fas fa-tag"></i>
                        </button>
                    </td>
                    <td data-field="Stock ID"><strong>#${stock.stock_id}</strong></td>
                    <td data-field="Stock Type">${stock.stock_type_name || 'N/A'}</td>
                    <td data-field="Current Level" style="text-align: right;">${currentLevel.toLocaleString()}</td>
                    <td data-field="Reorder Point" style="text-align: right;">${reorderPoint.toLocaleString()}</td>
                    <td><span class="status-badge ${statusClass}">${status}</span></td>
                    <td data-field="Last Order Date">${stock.last_used || 'Never'}</td>
                    <td data-field="Supplier">${stock.supplier_name || 'N/A'}</td>
                </tr>
            `;
        }).join('');

        // Apply table enhancements
        const table = document.getElementById('reorder-table');
        if (this.attachTableEnhancements) {
            this.attachTableEnhancements(table);
        }

        // Setup select-all
        document.getElementById('reorder-select-all')?.addEventListener('change', (e) => {
            document.querySelectorAll('#reorder-table .stock-checkbox').forEach(cb => {
                cb.checked = e.target.checked;
            });
            if (this.updateSelectionCount) this.updateSelectionCount();
        });
    }

    refreshReorderDashboardTab() {
        console.log('[REFRESH] Refreshing reorder dashboard...');
        this.loadReorderDashboard();
    }

    // ========================================================================
    // TAB 4: PROFIT ANALYSIS
    // ========================================================================

    initializeProfitAnalysisTab() {
        const tab = this.getSubTabContainer('profit-analysis');
        if (!tab) {
            console.error('❌ [INIT] Could not find profit-analysis container');
            return;
        }

        console.log('✅ [INIT] Initializing Profit Analysis tab...');

        tab.innerHTML = `
            <div class="module-dashboard">
                <!-- Card Header with Title and Subtitle -->
                <div class="dashboard-card">
                    <div class="card-header">
                        <div class="header-left" style="width: 100%; display: flex; flex-direction: column; gap: 8px; text-align: center;">
                            <h3 class="card-title" style="font-size: 24px; margin: 0;">
                                <i class="fas fa-dollar-sign"></i> Profit Analysis
                            </h3>
                            <div class="card-subtitle" style="margin: 0;">
                                Profitability analysis by stock and job type
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Summary Cards -->
                <div class="stats-grid">
                    <div class="stat-card success">
                        <div class="stat-icon"><i class="fas fa-dollar-sign"></i></div>
                        <div class="stat-content">
                            <div class="stat-label">Total Revenue</div>
                            <div class="stat-value" id="profit-total-revenue">$0</div>
                        </div>
                    </div>
                    <div class="stat-card info">
                        <div class="stat-icon"><i class="fas fa-chart-line"></i></div>
                        <div class="stat-content">
                            <div class="stat-label">Total Cost</div>
                            <div class="stat-value" id="profit-total-cost">$0</div>
                        </div>
                    </div>
                    <div class="stat-card warning">
                        <div class="stat-icon"><i class="fas fa-percentage"></i></div>
                        <div class="stat-content">
                            <div class="stat-label">Profit Margin</div>
                            <div class="stat-value" id="profit-margin-avg">0%</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon"><i class="fas fa-boxes"></i></div>
                        <div class="stat-content">
                            <div class="stat-label">Total Jobs</div>
                            <div class="stat-value" id="profit-total-jobs">0</div>
                        </div>
                    </div>
                </div>

                <!-- Bulk Operations Toolbar -->
                <div class="bulk-operations-toolbar" style="display: flex; align-items: center; gap: 12px; padding: 16px 20px; background: #1a1f2e; border-bottom: 1px solid #2a3142; margin-bottom: 20px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <select id="profit-period-selector" class="form-control" style="margin: 0; width: auto; padding: 6px 10px; background: #0B0E13; border: 1px solid #2A3142; border-radius: 6px; color: #E5E7EB; font-size: 12px;">
                            <option value="30">Last 30 Days</option>
                            <option value="90" selected>Last 90 Days</option>
                            <option value="180">Last 6 Months</option>
                            <option value="365">Last Year</option>
                        </select>
                        <button class="btn btn-primary" id="profit-refresh-btn" onclick="stockModule.refreshProfitAnalysisTab()" style="padding: 6px 12px; font-size: 12px;">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                    <div class="selected-count" style="margin-left: 16px; font-size: 12px;">
                        <span id="profit-selected-count">0 selected</span>
                    </div>
                    <div class="bulk-actions" style="display: flex; align-items: center; gap: 8px; margin-left: auto;">
                        <button onclick="stockModule.bulkTagRows(null)" class="btn btn-sm" style="padding: 6px 12px; font-size: 12px;">
                            <i class="fas fa-eraser"></i> Clear
                        </button>
                        <button onclick="stockModule.bulkTagRows('green')" class="btn btn-sm" style="background: #28a745; padding: 6px 12px; font-size: 12px;" title="High Profit">
                            <i class="fas fa-arrow-up"></i> High
                        </button>
                        <button onclick="stockModule.bulkTagRows('orange')" class="btn btn-sm" style="background: #fd7e14; padding: 6px 12px; font-size: 12px;" title="Medium Profit">
                            <i class="fas fa-minus"></i> Medium
                        </button>
                        <button onclick="stockModule.bulkTagRows('red')" class="btn btn-sm" style="background: #dc3545; padding: 6px 12px; font-size: 12px;" title="Low Profit">
                            <i class="fas fa-arrow-down"></i> Low
                        </button>
                        <div style="border-left: 1px solid #2A3142; height: 24px; margin: 0 4px;"></div>
                        <div class="dropdown" style="position: relative;">
                            <button class="btn btn-sm" style="padding: 6px 12px; font-size: 12px; background: #0078d4;" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'block' ? 'none' : 'block';">
                                <i class="fas fa-download"></i> Export
                            </button>
                            <div class="dropdown-menu" style="display: none; position: absolute; right: 0; top: 100%; margin-top: 4px; background: #1A1F2E; border: 1px solid #2A3142; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1000; min-width: 120px;">
                                <button onclick="stockModule.exportProfit('xlsx')" style="display: block; width: 100%; padding: 8px 12px; background: none; border: none; color: #E5E7EB; text-align: left; font-size: 12px; cursor: pointer;" onmouseover="this.style.background='#2A3142'" onmouseout="this.style.background='none'">
                                    <i class="fas fa-file-excel" style="color: #10b981; width: 16px;"></i> Excel
                                </button>
                                <button onclick="stockModule.exportProfit('csv')" style="display: block; width: 100%; padding: 8px 12px; background: none; border: none; color: #E5E7EB; text-align: left; font-size: 12px; cursor: pointer;" onmouseover="this.style.background='#2A3142'" onmouseout="this.style.background='none'">
                                    <i class="fas fa-file-csv" style="color: #60a5fa; width: 16px;"></i> CSV
                                </button>
                                <button onclick="stockModule.exportProfit('pdf')" style="display: block; width: 100%; padding: 8px 12px; background: none; border: none; color: #E5E7EB; text-align: left; font-size: 12px; cursor: pointer;" onmouseover="this.style.background='#2A3142'" onmouseout="this.style.background='none'">
                                    <i class="fas fa-file-pdf" style="color: #ef4444; width: 16px;"></i> PDF
                                </button>
                                <button onclick="stockModule.exportProfit('json')" style="display: block; width: 100%; padding: 8px 12px; background: none; border: none; color: #E5E7EB; text-align: left; font-size: 12px; cursor: pointer;" onmouseover="this.style.background='#2A3142'" onmouseout="this.style.background='none'">
                                    <i class="fas fa-file-code" style="color: #f59e0b; width: 16px;"></i> JSON
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Profit Analysis Table (Tabulator) -->
                <div id="profit-table-container" style="min-height: 400px; background: #0B0E13; border: 1px solid #2A3142; border-radius: 6px;">
                    <div style="text-align: center; padding: 40px; color: #9ca3af;">
                        <i class="fas fa-info-circle" style="font-size: 32px; color: #4ec9b0; margin-bottom: 10px; display: block;"></i>
                        <p style="margin: 0; font-size: 16px;">Click the <strong>Refresh</strong> button to load profit analysis</p>
                        <p style="margin: 5px 0 0 0; font-size: 12px; color: #6b7280;">Select timeframe from dropdown and click Refresh</p>
                    </div>
                </div>
            </div>
        `;

        // Setup event handlers
        document.getElementById('profit-period-selector')?.addEventListener('change', (e) => {
            const days = parseInt(e.target.value);
            this.loadProfitAnalysis(days);
        });

        // Initialize Tabulator after DOM is ready
        setTimeout(() => {
            this.initializeProfitTabulator();
        }, 100);
    }

    initializeProfitTabulator() {
        const container = document.getElementById('profit-table-container');
        if (!container) {
            console.error('Profit table container not found');
            return;
        }

        console.log('Initializing Profit Tabulator...');

        // Destroy existing table if any
        if (this.profitTable) {
            this.profitTable.destroy();
        }

        // Create Tabulator with advanced features
        this.profitTable = new Tabulator(container, {
            data: [],
            layout: "fitDataStretch",
            pagination: "local",
            paginationSize: 25,
            paginationSizeSelector: [10, 25, 50, 100],
            movableColumns: true,
            resizableColumns: true,
            height: "600px",
            placeholder: "No profit data available. Click Refresh to load.",
            selectable: true,
            selectableRangeMode: "click",
            columns: [
                {
                    title: "Tag",
                    field: "stock_id",
                    width: 60,
                    frozen: true,
                    headerSort: false,
                    hozAlign: "center",
                    formatter: function (cell) {
                        const rowId = cell.getValue();
                        const tag = window.TabulatorFunctions?.getRowTag(rowId, 'profit_tags');
                        const color = tag || 'untagged';
                        return `<button class="tag-btn tag-${color}" onclick="window.TabulatorFunctions.toggleRowTag(event, '${rowId}', stockModule.profitTable, 'profit_tags')" title="Tag row">
                            <i class="fas fa-tag"></i>
                        </button>`;
                    }
                },
                {
                    title: "Stock ID",
                    field: "stock_id",
                    width: 120,
                    headerSort: true,
                    headerFilter: "input",
                    formatter: function (cell) {
                        return `<span style="font-weight: 600; color: #0078d4;">${cell.getValue()}</span>`;
                    }
                },
                {
                    title: "Stock Type",
                    field: "stock_type",
                    width: 200,
                    headerSort: true,
                    headerFilter: "input"
                },
                {
                    title: "Jobs Count",
                    field: "job_count",
                    width: 120,
                    headerSort: true,
                    hozAlign: "center",
                    formatter: function (cell) {
                        return `<span style="font-weight: 600;">${cell.getValue() || 0}</span>`;
                    }
                },
                {
                    title: "Total Revenue",
                    field: "total_revenue",
                    width: 140,
                    headerSort: true,
                    hozAlign: "right",
                    formatter: function (cell) {
                        const value = cell.getValue() || 0;
                        return `<span style="font-weight: 700; color: #10b981;">$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>`;
                    }
                },
                {
                    title: "Total Cost",
                    field: "total_cost",
                    width: 140,
                    headerSort: true,
                    hozAlign: "right",
                    formatter: function (cell) {
                        const value = cell.getValue() || 0;
                        return `<span style="font-weight: 700; color: #ef4444;">$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>`;
                    }
                },
                {
                    title: "Gross Profit",
                    field: "gross_profit",
                    width: 140,
                    headerSort: true,
                    hozAlign: "right",
                    formatter: function (cell) {
                        const value = cell.getValue() || 0;
                        const color = value >= 0 ? '#10b981' : '#ef4444';
                        return `<span style="font-weight: 700; color: ${color};">$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>`;
                    }
                },
                {
                    title: "Margin %",
                    field: "margin_percent",
                    width: 120,
                    headerSort: true,
                    hozAlign: "right",
                    formatter: function (cell) {
                        const value = cell.getValue() || 0;
                        let color = '#9ca3af';
                        if (value >= 40) color = '#10b981'; // Green for high margin
                        else if (value >= 20) color = '#f59e0b'; // Orange for medium
                        else if (value > 0) color = '#ef4444'; // Red for low
                        return `<span style="font-weight: 700; color: ${color};">${value.toFixed(1)}%</span>`;
                    }
                }
            ],
            rowFormatter: function (row) {
                if (window.TabulatorFunctions) {
                    window.TabulatorFunctions.applyRowTagFormatter(row, 'stock_id', 'profit_tags');
                }
            }
        });

        console.log('Profit Tabulator initialized');
    }

    async loadProfitAnalysis(days) {
        console.log(`[LOAD] Loading profit analysis for ${days} days...`);

        // Show loading in Tabulator
        if (this.profitTable) {
            this.profitTable.setData([]);
            this.profitTable.setPlaceholder("Loading profit analysis...");
        }

        try {
            const response = await fetch(
                `${this.backendUrl}/api/stock-management/profit-analysis?days=${days}`
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.message || 'Failed to load profit data');
            }

            console.log('[OK] Profit analysis loaded:', result.data);

            const analysisData = result.data || {};
            const stocks = analysisData.stocks || [];
            this.profitData = stocks;

            // Calculate summary stats from the data
            let totalRevenue = 0, totalCost = 0, totalJobs = 0;

            stocks.forEach(stock => {
                const revenue = parseFloat(stock.total_revenue || 0);
                const cost = parseFloat(stock.total_cost || 0);
                const jobs = parseInt(stock.job_count || 0);

                totalRevenue += revenue;
                totalCost += cost;
                totalJobs += jobs;
            });

            const totalProfit = totalRevenue - totalCost;
            const avgMargin = totalRevenue > 0 ? ((totalProfit / totalRevenue) * 100) : 0;

            // Update summary cards
            document.getElementById('profit-total-revenue').textContent = `$${totalRevenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            document.getElementById('profit-total-cost').textContent = `$${totalCost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            document.getElementById('profit-margin-avg').textContent = `${avgMargin.toFixed(1)}%`;
            document.getElementById('profit-total-jobs').textContent = totalJobs.toLocaleString();

            // Load data into Tabulator
            if (this.profitTable) {
                this.profitTable.setData(stocks);
                console.log(`[OK] Loaded ${stocks.length} profit records into Tabulator`);
            }

        } catch (error) {
            console.error('[ERROR] Failed to load profit data:', error);

            if (this.profitTable) {
                this.profitTable.setData([]);
                this.profitTable.setPlaceholder(`Failed to load profit analysis: ${error.message}`);
            }

            if (window.TabulatorToast) {
                window.TabulatorToast.showToast('Error loading profit data', 'error');
            }
        }
    }

    refreshProfitAnalysisTab() {
        console.log('[REFRESH] Refreshing profit analysis tab...');
        const days = document.getElementById('profit-period-selector')?.value || 90;
        this.loadProfitAnalysis(parseInt(days));
    }

    // ========================================================================
    // TAB 5: SQL VIEWER
    // ========================================================================

    initializeSQLViewerTab() {
        const tab = this.getSubTabContainer('sql-viewer');
        if (!tab) {
            console.error('❌ [INIT] Could not find sql-viewer container');
            return;
        }

        console.log('✅ [INIT] Initializing SQL Viewer tab...');

        tab.innerHTML = `
            <div class="module-dashboard">
                <!-- Card Header with Title and Subtitle -->
                <div class="dashboard-card">
                    <div class="card-header">
                        <div class="header-left" style="width: 100%; display: flex; flex-direction: column; gap: 8px; text-align: center;">
                            <h3 class="card-title" style="font-size: 24px; margin: 0;">
                                <i class="fas fa-database"></i> SQL Viewer
                            </h3>
                            <div class="card-subtitle" style="margin: 0;">
                                Direct database queries with inline editing
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Query Input Section -->
                <div class="stats-grid" style="grid-template-columns: 1fr; gap: 20px; margin-bottom: 20px;">
                    <div style="background: #1A1F2E; border: 1px solid #2A3142; border-radius: 8px; padding: 16px;">
                        <label style="display: block; font-size: 13px; font-weight: 700; color: #00D9FF; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.8px;">
                            <i class="fas fa-keyboard"></i> SQL Query Input
                        </label>
                        <textarea id="sql-query-input" 
                                  class="sql-editor" 
                                  placeholder="Enter SQL query...&#10;&#10;Example:&#10;SELECT * FROM unified_stocks&#10;WHERE is_active = 1&#10;ORDER BY stock_type_name&#10;LIMIT 50"
                                  rows="6"
                                  style="width: 100%; background: #0B0E13; border: 1px solid #2A3142; border-radius: 6px; color: #E5E7EB; padding: 12px; font-family: 'Courier New', monospace; font-size: 13px; resize: vertical;"></textarea>
                        <div style="margin-top: 8px; font-size: 12px; color: #9CA3AF;">
                            <i class="fas fa-info-circle"></i> Enter any SQL query to retrieve data from the database
                        </div>
                    </div>
                </div>

                <!-- Toolbar -->
                <div class="bulk-operations-toolbar" style="display: flex; align-items: center; gap: 12px; padding: 16px 20px; background: #1a1f2e; border-bottom: 1px solid #2a3142; margin-bottom: 20px;">
                    <div class="bulk-actions" style="display: flex; align-items: center; gap: 8px;">
                        <button onclick="stockModule.executeSQLQuery()" class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;">
                            <i class="fas fa-play"></i> Execute
                        </button>
                        <button onclick="stockModule.clearSQLQuery()" class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;">
                            <i class="fas fa-eraser"></i> Clear
                        </button>
                    </div>
                    <div class="selected-count" style="margin-left: 16px; font-size: 12px;">
                        <span id="sql-selected-count">0 selected</span>
                    </div>
                    <div class="bulk-actions" style="display: flex; align-items: center; gap: 8px; margin-left: auto;">
                        <button onclick="stockModule.bulkTagRows(null)" class="btn btn-sm" style="padding: 6px 12px; font-size: 12px;">
                            <i class="fas fa-eraser"></i> Clear Tag
                        </button>
                        <button onclick="stockModule.bulkTagRows('green')" class="btn btn-sm" style="background: #28a745; padding: 6px 12px; font-size: 12px;">
                            <i class="fas fa-tag"></i> Green
                        </button>
                        <button onclick="stockModule.bulkTagRows('orange')" class="btn btn-sm" style="background: #fd7e14; padding: 6px 12px; font-size: 12px;">
                            <i class="fas fa-tag"></i> Orange
                        </button>
                        <button onclick="stockModule.bulkTagRows('red')" class="btn btn-sm" style="background: #dc3545; padding: 6px 12px; font-size: 12px;">
                            <i class="fas fa-tag"></i> Red
                        </button>
                        <div style="border-left: 1px solid #2A3142; height: 24px; margin: 0 4px;"></div>
                        <div class="dropdown" style="position: relative;">
                            <button class="btn btn-sm" style="padding: 6px 12px; font-size: 12px; background: #0078d4;" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'block' ? 'none' : 'block';">
                                <i class="fas fa-download"></i> Export
                            </button>
                            <div class="dropdown-menu" style="display: none; position: absolute; right: 0; top: 100%; margin-top: 4px; background: #1A1F2E; border: 1px solid #2A3142; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1000; min-width: 120px;">
                                <button onclick="stockModule.exportSQLResults('xlsx')" style="display: block; width: 100%; padding: 8px 12px; background: none; border: none; color: #E5E7EB; text-align: left; font-size: 12px; cursor: pointer;" onmouseover="this.style.background='#2A3142'" onmouseout="this.style.background='none'">
                                    <i class="fas fa-file-excel" style="color: #10b981; width: 16px;"></i> Excel
                                </button>
                                <button onclick="stockModule.exportSQLResults('csv')" style="display: block; width: 100%; padding: 8px 12px; background: none; border: none; color: #E5E7EB; text-align: left; font-size: 12px; cursor: pointer;" onmouseover="this.style.background='#2A3142'" onmouseout="this.style.background='none'">
                                    <i class="fas fa-file-csv" style="color: #60a5fa; width: 16px;"></i> CSV
                                </button>
                                <button onclick="stockModule.exportSQLResults('pdf')" style="display: block; width: 100%; padding: 8px 12px; background: none; border: none; color: #E5E7EB; text-align: left; font-size: 12px; cursor: pointer;" onmouseover="this.style.background='#2A3142'" onmouseout="this.style.background='none'">
                                    <i class="fas fa-file-pdf" style="color: #ef4444; width: 16px;"></i> PDF
                                </button>
                                <button onclick="stockModule.exportSQLResults('json')" style="display: block; width: 100%; padding: 8px 12px; background: none; border: none; color: #E5E7EB; text-align: left; font-size: 12px; cursor: pointer;" onmouseover="this.style.background='#2A3142'" onmouseout="this.style.background='none'">
                                    <i class="fas fa-file-code" style="color: #f59e0b; width: 16px;"></i> JSON
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Query Results (Tabulator) -->
                <div id="sql-results-tabulator-container" style="min-height: 400px; background: #0B0E13; border: 1px solid #2A3142; border-radius: 6px;">
                    <div style="text-align: center; padding: 40px; color: #9ca3af;">
                        <i class="fas fa-info-circle" style="font-size: 32px; color: #4ec9b0; margin-bottom: 10px; display: block;"></i>
                        <p style="margin: 0; font-size: 16px;">Enter a SQL query above and click <strong>Execute</strong></p>
                        <p style="margin: 5px 0 0 0; font-size: 12px; color: #6b7280;">Results will display in a formatted table below</p>
                    </div>
                </div>
            </div>
        `;

        // Initialize empty Tabulator
        setTimeout(() => {
            this.initializeSQLViewerTabulator();
        }, 100);
    }

    initializeSQLViewerTabulator() {
        const container = document.getElementById('sql-results-tabulator-container');
        if (!container) {
            console.error('SQL results container not found');
            return;
        }

        console.log('Initializing SQL Viewer Tabulator...');

        // Destroy existing table if any
        if (this.sqlViewerTable) {
            this.sqlViewerTable.destroy();
        }

        // Create empty Tabulator (will be populated dynamically)
        this.sqlViewerTable = new Tabulator(container, {
            data: [],
            layout: "fitDataStretch",
            pagination: "local",
            paginationSize: 25,
            paginationSizeSelector: [10, 25, 50, 100, 500],
            movableColumns: true,
            resizableColumns: true,
            height: "600px",
            placeholder: "Enter a SQL query above and click Execute to load data",
            selectable: true,
            selectableRangeMode: "click",
            columns: [] // Will be set dynamically based on query results
        });

        console.log('SQL Viewer Tabulator initialized (empty)');
    }

    clearSQLQuery() {
        document.getElementById('sql-query-input').value = '';
        document.getElementById('sql-results-container').style.display = 'none';
        document.getElementById('sql-toolbar').style.display = 'none';
        document.getElementById('sql-no-results').style.display = 'none';
    }

    async executeSQLQuery() {
        const query = document.getElementById('sql-query-input').value.trim();

        if (!query) {
            alert('Please enter a SQL query');
            return;
        }

        console.log('Executing SQL query:', query);

        try {
            const response = await fetch(`${this.backendUrl}${this.apiEndpoint}/sql-query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            if (!response.ok) throw new Error('Query execution failed');

            const data = await response.json();
            this.displaySQLResults(data);

        } catch (error) {
            console.error(' SQL query failed:', error);
            alert('Query failed: ' + error.message);
        }
    }

    displaySQLResults(data) {
        if (!data.results || data.results.length === 0) {
            if (this.sqlViewerTable) {
                this.sqlViewerTable.setData([]);
                this.sqlViewerTable.setPlaceholder('Query returned no results');
            }
            return;
        }

        console.log(`[SQL] Displaying ${data.results.length} rows`);

        // Get columns from first row
        const dataColumns = data.columns || Object.keys(data.results[0]);

        // Build dynamic Tabulator columns
        const tabulatorColumns = [
            {
                title: "Tag",
                field: "_rowId",
                width: 60,
                frozen: true,
                headerSort: false,
                hozAlign: "center",
                formatter: function (cell) {
                    const row = cell.getRow().getData();
                    const rowId = row.stock_id || row.id || row._rowId;
                    const tag = window.TabulatorFunctions?.getRowTag(rowId, 'sql_viewer_tags');
                    const color = tag || 'untagged';
                    return `<button class="tag-btn tag-${color}" onclick="window.TabulatorFunctions.toggleRowTag(event, '${rowId}', stockModule.sqlViewerTable, 'sql_viewer_tags')" title="Tag row">
                        <i class="fas fa-tag"></i>
                    </button>`;
                }
            }
        ];

        // Add data columns dynamically
        dataColumns.forEach(col => {
            const column = {
                title: col,
                field: col,
                headerSort: true,
                headerFilter: "input",
                formatter: function (cell) {
                    const value = cell.getValue();
                    if (value === null || value === undefined) {
                        return '<em style="color: #6b7280;">NULL</em>';
                    }
                    if (typeof value === 'object') {
                        return `<span style="font-family: monospace; font-size: 11px;">${JSON.stringify(value)}</span>`;
                    }
                    // Detect numeric values
                    if (typeof value === 'number') {
                        if (Number.isInteger(value)) {
                            return `<span style="font-weight: 600; color: #60a5fa;">${value.toLocaleString()}</span>`;
                        } else {
                            return `<span style="font-weight: 600; color: #60a5fa;">${value.toFixed(2)}</span>`;
                        }
                    }
                    // Detect currency
                    if (typeof value === 'string' && value.match(/^\$?\d+\.?\d*$/)) {
                        const num = parseFloat(value.replace('$', ''));
                        return `<span style="font-weight: 600; color: #10b981;">$${num.toFixed(2)}</span>`;
                    }
                    // Detect dates
                    if (typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}/)) {
                        return `<span style="color: #f59e0b;">${new Date(value).toLocaleString()}</span>`;
                    }
                    return String(value);
                }
            };

            // Auto-size column based on column name
            if (col.toLowerCase().includes('id')) column.width = 100;
            else if (col.toLowerCase().includes('name') || col.toLowerCase().includes('type')) column.width = 200;
            else if (col.toLowerCase().includes('date') || col.toLowerCase().includes('time')) column.width = 180;
            else column.width = 150;

            tabulatorColumns.push(column);
        });

        // Add _rowId to each row for tagging
        const processedData = data.results.map((row, index) => ({
            ...row,
            _rowId: row.stock_id || row.id || `row_${index}`
        }));

        // Update Tabulator with new columns and data
        if (this.sqlViewerTable) {
            this.sqlViewerTable.setColumns(tabulatorColumns);
            this.sqlViewerTable.setData(processedData);
            console.log(`[OK] SQL Viewer loaded ${processedData.length} rows with ${tabulatorColumns.length} columns`);
        }
    }

    // ========================================================================
    // TAB 6: AI ANALYTICS
    // ========================================================================

    initializeAIAnalyticsTab() {
        const tab = this.getSubTabContainer('ai-analytics');
        if (!tab) {
            console.error('❌ [INIT] Could not find ai-analytics container');
            return;
        }

        console.log('✅ [INIT] Initializing AI Analytics tab...');

        tab.innerHTML = `
            <div class="module-dashboard">
                <!-- Card Header with Title and Subtitle -->
                <div class="dashboard-card">
                    <div class="card-header">
                        <div class="header-left" style="width: 100%; display: flex; flex-direction: column; gap: 8px;">
                            <h3 class="card-title" style="font-size: 24px; margin: 0;">
                                <i class="fas fa-brain"></i> AI Analytics
                            </h3>
                            <div class="card-subtitle" style="margin: 0;">
                                AI usage metrics and invoice processing analytics
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Summary Cards -->
                <div class="stats-grid">
                    <div class="stat-card info">
                        <div class="stat-icon"><i class="fas fa-robot"></i></div>
                        <div class="stat-content">
                            <div class="stat-label">Total AI Queries</div>
                            <div class="stat-value" id="ai-total-queries">0</div>
                        </div>
                    </div>
                    <div class="stat-card success">
                        <div class="stat-icon"><i class="fas fa-dollar-sign"></i></div>
                        <div class="stat-content">
                            <div class="stat-label">Total Cost</div>
                            <div class="stat-value" id="ai-total-cost">$0</div>
                        </div>
                    </div>
                    <div class="stat-card warning">
                        <div class="stat-icon"><i class="fas fa-clock"></i></div>
                        <div class="stat-content">
                            <div class="stat-label">Avg Response Time</div>
                            <div class="stat-value" id="ai-avg-time">0s</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon"><i class="fas fa-file-invoice"></i></div>
                        <div class="stat-content">
                            <div class="stat-label">Invoices Processed</div>
                            <div class="stat-value" id="ai-invoice-count">0</div>
                        </div>
                    </div>
                </div>

                <!-- Bulk Operations Toolbar -->
                <div class="bulk-operations-toolbar" style="display: flex; align-items: center; gap: 12px; padding: 16px 20px; background: #1a1f2e; border-bottom: 1px solid #2a3142; margin-bottom: 20px;">
                    <div class="selected-count" style="font-size: 12px;">
                        <span id="ai-selected-count">0 selected</span>
                    </div>
                    <div class="bulk-actions" style="display: flex; align-items: center; gap: 8px; margin-left: auto;">
                        <button onclick="stockModule.bulkTagRows(null)" class="btn btn-sm" style="padding: 6px 12px; font-size: 12px;">
                            <i class="fas fa-eraser"></i> Clear
                        </button>
                        <button onclick="stockModule.bulkTagRows('green')" class="btn btn-sm" style="background: #28a745; padding: 6px 12px; font-size: 12px;" title="Success">
                            <i class="fas fa-check"></i> Success
                        </button>
                        <button onclick="stockModule.bulkTagRows('orange')" class="btn btn-sm" style="background: #fd7e14; padding: 6px 12px; font-size: 12px;" title="Needs Review">
                            <i class="fas fa-eye"></i> Review
                        </button>
                        <button onclick="stockModule.bulkTagRows('red')" class="btn btn-sm" style="background: #dc3545; padding: 6px 12px; font-size: 12px;" title="Failed">
                            <i class="fas fa-times"></i> Failed
                        </button>
                        <div style="border-left: 1px solid #2A3142; height: 24px; margin: 0 4px;"></div>
                        <button class="btn btn-primary" id="ai-refresh-btn" onclick="stockModule.refreshAIAnalyticsTab()" style="padding: 6px 12px; font-size: 12px;">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                        <div class="dropdown" style="position: relative;">
                            <button class="btn btn-sm" style="padding: 6px 12px; font-size: 12px; background: #0078d4;" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'block' ? 'none' : 'block';">
                                <i class="fas fa-download"></i> Export
                            </button>
                            <div class="dropdown-menu" style="display: none; position: absolute; right: 0; top: 100%; margin-top: 4px; background: #1A1F2E; border: 1px solid #2A3142; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1000; min-width: 120px;">
                                <button onclick="stockModule.exportAIAnalytics('xlsx')" style="display: block; width: 100%; padding: 8px 12px; background: none; border: none; color: #E5E7EB; text-align: left; font-size: 12px; cursor: pointer;" onmouseover="this.style.background='#2A3142'" onmouseout="this.style.background='none'">
                                    <i class="fas fa-file-excel" style="color: #10b981; width: 16px;"></i> Excel
                                </button>
                                <button onclick="stockModule.exportAIAnalytics('csv')" style="display: block; width: 100%; padding: 8px 12px; background: none; border: none; color: #E5E7EB; text-align: left; font-size: 12px; cursor: pointer;" onmouseover="this.style.background='#2A3142'" onmouseout="this.style.background='none'">
                                    <i class="fas fa-file-csv" style="color: #60a5fa; width: 16px;"></i> CSV
                                </button>
                                <button onclick="stockModule.exportAIAnalytics('pdf')" style="display: block; width: 100%; padding: 8px 12px; background: none; border: none; color: #E5E7EB; text-align: left; font-size: 12px; cursor: pointer;" onmouseover="this.style.background='#2A3142'" onmouseout="this.style.background='none'">
                                    <i class="fas fa-file-pdf" style="color: #ef4444; width: 16px;"></i> PDF
                                </button>
                                <button onclick="stockModule.exportAIAnalytics('json')" style="display: block; width: 100%; padding: 8px 12px; background: none; border: none; color: #E5E7EB; text-align: left; font-size: 12px; cursor: pointer;" onmouseover="this.style.background='#2A3142'" onmouseout="this.style.background='none'">
                                    <i class="fas fa-file-code" style="color: #f59e0b; width: 16px;"></i> JSON
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- AI Analytics Table (Tabulator) -->
                <div id="ai-analytics-table-container" style="min-height: 400px; background: #0B0E13; border: 1px solid #2A3142; border-radius: 6px;">
                    <div style="text-align: center; padding: 40px; color: #9ca3af;">
                        <i class="fas fa-info-circle" style="font-size: 32px; color: #4ec9b0; margin-bottom: 10px; display: block;"></i>
                        <p style="margin: 0; font-size: 16px;">Click the <strong>Refresh</strong> button to load AI analytics</p>
                        <p style="margin: 5px 0 0 0; font-size: 12px; color: #6b7280;">View AI usage metrics and processing analytics</p>
                    </div>
                </div>
            </div>
        `;

        // Initialize Tabulator after DOM is ready
        setTimeout(() => {
            this.initializeAIAnalyticsTabulator();
        }, 100);
    }

    initializeAIAnalyticsTabulator() {
        const container = document.getElementById('ai-analytics-table-container');
        if (!container) {
            console.error('AI Analytics table container not found');
            return;
        }

        console.log('Initializing AI Analytics Tabulator...');

        // Destroy existing table if any
        if (this.aiAnalyticsTable) {
            this.aiAnalyticsTable.destroy();
        }

        // Create Tabulator with advanced features
        this.aiAnalyticsTable = new Tabulator(container, {
            data: [],
            layout: "fitDataStretch",
            pagination: "local",
            paginationSize: 25,
            paginationSizeSelector: [10, 25, 50, 100],
            movableColumns: true,
            resizableColumns: true,
            height: "600px",
            placeholder: "No AI analytics data available. Click Refresh to load.",
            selectable: true,
            selectableRangeMode: "click",
            columns: [
                {
                    title: "Tag",
                    field: "id",
                    width: 60,
                    frozen: true,
                    headerSort: false,
                    hozAlign: "center",
                    formatter: function (cell) {
                        const rowId = cell.getValue();
                        const tag = window.TabulatorFunctions?.getRowTag(rowId, 'ai_analytics_tags');
                        const color = tag || 'untagged';
                        return `<button class="tag-btn tag-${color}" onclick="window.TabulatorFunctions.toggleRowTag(event, '${rowId}', stockModule.aiAnalyticsTable, 'ai_analytics_tags')" title="Tag row">
                            <i class="fas fa-tag"></i>
                        </button>`;
                    }
                },
                {
                    title: "Timestamp",
                    field: "timestamp",
                    width: 180,
                    headerSort: true,
                    headerFilter: "input",
                    formatter: function (cell) {
                        const value = cell.getValue();
                        if (!value) return 'N/A';
                        const date = new Date(value);
                        return date.toLocaleString();
                    }
                },
                {
                    title: "Query Type",
                    field: "query_type",
                    width: 150,
                    headerSort: true,
                    headerFilter: "input"
                },
                {
                    title: "Model",
                    field: "model",
                    width: 120,
                    headerSort: true,
                    headerFilter: "input"
                },
                {
                    title: "Input Tokens",
                    field: "input_tokens",
                    width: 130,
                    headerSort: true,
                    hozAlign: "right",
                    formatter: function (cell) {
                        return (cell.getValue() || 0).toLocaleString();
                    }
                },
                {
                    title: "Output Tokens",
                    field: "output_tokens",
                    width: 130,
                    headerSort: true,
                    hozAlign: "right",
                    formatter: function (cell) {
                        return (cell.getValue() || 0).toLocaleString();
                    }
                },
                {
                    title: "Cost",
                    field: "cost",
                    width: 100,
                    headerSort: true,
                    hozAlign: "right",
                    formatter: function (cell) {
                        const value = cell.getValue() || 0;
                        return `<span style="font-weight: 600; color: #f59e0b;">$${value.toFixed(4)}</span>`;
                    }
                },
                {
                    title: "Response Time",
                    field: "response_time",
                    width: 130,
                    headerSort: true,
                    hozAlign: "right",
                    formatter: function (cell) {
                        const value = cell.getValue() || 0;
                        let color = '#10b981';
                        if (value > 5) color = '#ef4444';
                        else if (value > 2) color = '#f59e0b';
                        return `<span style="font-weight: 600; color: ${color};">${value.toFixed(2)}s</span>`;
                    }
                },
                {
                    title: "Status",
                    field: "status",
                    width: 100,
                    headerSort: true,
                    hozAlign: "center",
                    formatter: function (cell) {
                        const status = cell.getValue() || 'unknown';
                        let color = '#9ca3af';
                        let icon = 'question';
                        if (status === 'success') { color = '#10b981'; icon = 'check'; }
                        else if (status === 'failed') { color = '#ef4444'; icon = 'times'; }
                        else if (status === 'pending') { color = '#f59e0b'; icon = 'clock'; }
                        return `<span style="color: ${color}; font-weight: 600;"><i class="fas fa-${icon}"></i> ${status.charAt(0).toUpperCase() + status.slice(1)}</span>`;
                    }
                }
            ],
            rowFormatter: function (row) {
                if (window.TabulatorFunctions) {
                    window.TabulatorFunctions.applyRowTagFormatter(row, 'id', 'ai_analytics_tags');
                }
            }
        });

        console.log('AI Analytics Tabulator initialized');
    }

    async loadAIAnalytics() {
        console.log('[LOAD] Loading AI analytics...');

        // Show loading in Tabulator
        if (this.aiAnalyticsTable) {
            this.aiAnalyticsTable.setData([]);
            this.aiAnalyticsTable.setPlaceholder("Loading AI analytics...");
        }

        try {
            // CORRECT API endpoint: /api/stock/ai-analytics (not /api/stock-management/ai-analytics)
            const response = await fetch(`${this.backendUrl}/api/stock/ai-analytics`);
            if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);

            const data = await response.json();

            // Update summary cards
            document.getElementById('ai-total-queries').textContent = (data.total_queries || 0).toLocaleString();
            document.getElementById('ai-total-cost').textContent = `$${(data.total_cost || 0).toFixed(2)}`;
            document.getElementById('ai-avg-time').textContent = `${(data.avg_response_time || 0).toFixed(2)}s`;
            document.getElementById('ai-invoice-count').textContent = (data.invoice_count || 0).toLocaleString();

            // Load data into Tabulator
            const queries = data.queries || [];
            if (this.aiAnalyticsTable) {
                this.aiAnalyticsTable.setData(queries);
                console.log(`[OK] Loaded ${queries.length} AI analytics records into Tabulator`);
            }

        } catch (error) {
            console.error('[ERROR] Failed to load AI analytics:', error);

            if (this.aiAnalyticsTable) {
                this.aiAnalyticsTable.setData([]);
                this.aiAnalyticsTable.setPlaceholder(`Failed to load AI analytics: ${error.message}`);
            }

            if (window.TabulatorToast) {
                window.TabulatorToast.showToast('Error loading AI analytics', 'error');
            }
        }
    }

    // ========================================================================
    // UTILITY METHODS
    // ========================================================================

    showPlaceholderMessage(containerId, message) {
        const container = document.getElementById(containerId);
        if (container) {
            const placeholder = document.createElement('div');
            placeholder.className = 'info-message';
            placeholder.innerHTML = `
                <i class="fas fa-info-circle"></i>
                ${message}
            `;
            container.appendChild(placeholder);
        }
    }

    showError(containerId, message) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    ${message}
                </div>
            `;
        }
    }

    showLoading(container, message = 'Loading...') {
        if (container) {
            container.innerHTML = `
                <div class="loading-state">
                    <i class="fas fa-spinner fa-spin"></i>
                    ${message}
                </div>
            `;
        }
    }

    // ========================================================================
    // DATA LOADING METHODS (Placeholders for Phase 2-6)
    // ========================================================================

    async loadUsageAnalytics(days = 90) {
        console.log(`[LOAD] Loading usage analytics for ${days} days...`);

        try {
            const response = await fetch(`${this.backendUrl}/api/stock-management/usage-analytics?days=${days}`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('[OK] Usage analytics loaded:', result);

            // Display the data in the UI
            const container = document.querySelector('#usage-analytics-content');
            if (container && result.data) {
                const data = result.data;
                container.innerHTML = `
                    <div class="analytics-summary">
                        <h3>Stock Usage Summary (${days} days)</h3>
                        <div class="data-table-container">
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Stock ID</th>
                                        <th>Stock Type</th>
                                        <th>Usage Count</th>
                                        <th>Total Quantity</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.map(row => `
                                        <tr>
                                            <td>${row.StockID || 'N/A'}</td>
                                            <td>${row.StockType || 'Unknown'}</td>
                                            <td>${row.usage_count || 0}</td>
                                            <td>${(row.total_quantity || 0).toLocaleString()}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
            }

        } catch (error) {
            console.error('[ERROR] Failed to load usage analytics:', error);
            const container = document.querySelector('#usage-analytics-content');
            if (container) {
                container.innerHTML = `
                    <div class="error-message">
                        <p><strong>Error loading usage analytics:</strong></p>
                        <p>${error.message}</p>
                        <p>Make sure Flask backend is running on ${this.backendUrl}</p>
                    </div>
                `;
            }
        }
    }

    async loadReorderDashboard() {
        console.log('[LOAD] Loading reorder dashboard...');

        try {
            const response = await fetch(`${this.backendUrl}/api/stock-management/reorder-dashboard`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('[OK] Reorder dashboard loaded:', result);
            console.log('[DEBUG] Reorder data count:', result.data?.length);

            // Update the existing table with data
            const tbody = document.getElementById('reorder-table-body');
            if (!tbody) {
                console.error('[ERROR] Could not find reorder-table-body element');
                return;
            }

            // Update summary cards
            const summary = result.summary || {};
            document.getElementById('reorder-critical-count').textContent = summary.critical || 0;
            document.getElementById('reorder-low-count').textContent = summary.moderate || 0;
            document.getElementById('reorder-adequate-count').textContent = summary.upcoming || 0;
            document.getElementById('reorder-total-count').textContent = summary.total_alerts || 0;

            // Populate table rows
            if (result.data && result.data.length > 0) {
                console.log('[DEBUG] Rendering', result.data.length, 'rows');
                tbody.innerHTML = result.data.map((item, index) => `
                    <tr data-row-id="${index}">
                        <td><input type="checkbox" class="row-checkbox"></td>
                        <td>${index + 1}</td>
                        <td><div class="tag-indicator" data-tag=""></div></td>
                        <td>${item.stock_id || item.sku || 'N/A'}</td>
                        <td>${item.stock_type_name || item.product_name || 'Unknown'}</td>
                        <td style="text-align: right;">${item.current_level || item.current_stock || 0}</td>
                        <td style="text-align: right;">${item.reorder_point || 0}</td>
                        <td>
                            <span class="status-badge ${item.alert_level || 'ok'}">
                                ${(item.alert_level || 'ok').toUpperCase()}
                            </span>
                        </td>
                        <td>${item.last_order_date || 'N/A'}</td>
                        <td>${item.supplier_name || 'TBD'}</td>
                    </tr>
                `).join('');
                console.log('[SUCCESS] Reorder dashboard rendered with', result.data.length, 'items');
            } else {
                tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; padding: 20px;">No reorder alerts found</td></tr>';
            }

        } catch (error) {
            console.error('[ERROR] Failed to load reorder dashboard:', error);
            const container = this.getSubTabContainer('reorder-dashboard');
            if (container) {
                container.innerHTML = `
                    <div class="error-message">
                        <p><strong>Error loading reorder dashboard:</strong></p>
                        <p>${error.message}</p>
                    </div>
                `;
            }
        }
    }

    async loadProfitAnalysis(days) {
        console.log(`[LOAD] Loading profit analysis for ${days} days...`);

        try {
            const response = await fetch(`${this.backendUrl}/api/stock-management/profit-analysis?days=${days}`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('[OK] Profit analysis loaded:', result);
            console.log('[DEBUG] Profit data count:', result.data?.length);

            // Update the existing table with data
            const tbody = document.getElementById('profit-table-body');
            if (!tbody) {
                console.error('[ERROR] Could not find profit-table-body element');
                return;
            }

            // Update summary cards
            const summary = result.summary || {};
            document.getElementById('profit-total-revenue').textContent = `$${(summary.total_revenue || 0).toLocaleString()}`;
            document.getElementById('profit-total-cost').textContent = `$${(summary.total_cost || 0).toLocaleString()}`;
            document.getElementById('profit-margin-avg').textContent = `${(summary.overall_margin || 0).toFixed(1)}%`;
            document.getElementById('profit-total-jobs').textContent = summary.stocks_analyzed || 0;

            // Populate table rows
            if (result.data && result.data.length > 0) {
                console.log('[DEBUG] Rendering', result.data.length, 'profit rows');
                tbody.innerHTML = result.data.map((item, index) => {
                    const profit = parseFloat(item.gross_profit || item.profit || 0);
                    const margin = parseFloat(item.margin_percent || item.margin || 0);
                    const revenue = parseFloat(item.estimated_revenue || item.revenue || 0);
                    const cost = parseFloat(item.total_cost || item.cost || 0);

                    return `
                        <tr data-row-id="${index}">
                            <td><input type="checkbox" class="row-checkbox"></td>
                            <td>${index + 1}</td>
                            <td><div class="tag-indicator" data-tag=""></div></td>
                            <td>#${item.stock_id || item.sku || 'N/A'}</td>
                            <td>${item.stock_type_name || item.product_name || 'Unknown'}</td>
                            <td style="text-align: right;">${item.total_jobs || item.units_sold || 0}</td>
                            <td style="text-align: right;">$${revenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                            <td style="text-align: right;">$${cost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                            <td style="text-align: right; color: ${profit >= 0 ? '#10b981' : '#ef4444'};">
                                $${profit.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </td>
                            <td style="text-align: right;">${margin.toFixed(1)}%</td>
                        </tr>
                    `;
                }).join('');
                console.log('[SUCCESS] Profit analysis rendered with', result.data.length, 'items');
            } else {
                tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; padding: 20px;">No profit data found</td></tr>';
            }

        } catch (error) {
            console.error('[ERROR] Failed to load profit analysis:', error);
            const container = this.getSubTabContainer('profit-analysis');
            if (container) {
                container.innerHTML = `
                    <div class="error-message">
                        <p><strong>Error loading profit analysis:</strong></p>
                        <p>${error.message}</p>
                    </div>
                `;
            }
        }
    }

    // ========================================================================
    // REFRESH FUNCTIONS FOR ALL TABS
    // ========================================================================

    refreshInvoiceTab() {
        console.log('[REFRESH] Clearing invoice processor...');
        const container = this.getSubTabContainer('invoice-processing');

        const uploadZone = container.querySelector('#invoice-upload-zone');
        const processingDiv = container.querySelector('#invoice-processing-status');
        const resultsDiv = container.querySelector('#invoice-results');
        const fileInput = container.querySelector('#invoice-file-input');

        if (uploadZone) uploadZone.style.display = 'block';
        if (processingDiv) processingDiv.style.display = 'none';
        if (resultsDiv) resultsDiv.style.display = 'none';
        if (fileInput) fileInput.value = '';
    }

    refreshSQLViewerTab() {
        console.log('[REFRESH] Refreshing SQL viewer...');
        // SQL Viewer refresh - placeholder for future implementation
    }

    refreshAIAnalyticsTab() {
        console.log('[REFRESH] Refreshing AI analytics...');
        this.loadAIAnalytics();
    }

    // ========================================================================
    // PLOTLY ENHANCED CHART METHODS
    // ========================================================================

    /**
     * Load usage analytics with Plotly chart
     */
    async loadUsageAnalyticsWithChart(days = 90) {
        console.log(`[LOAD] Loading usage analytics with Plotly chart for ${days} days...`);

        try {
            const response = await fetch(`${this.backendUrl}/api/stock-management/usage-analytics?days=${days}`);
            const result = await response.json();

            if (result.status === 'ok') {
                const container = document.querySelector('#usage-analytics-content');
                container.innerHTML = `
                <div class="chart-container">
                    <div id="usage-chart" style="width:100%;height:400px;"></div>
                </div>
                <div class="data-table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Stock ID</th>
                                <th>Stock Type</th>
                                <th>GSM</th>
                                <th>Dimensions</th>
                                <th>Usage Count</th>
                                <th>Total Quantity</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${result.data.map(row => `
                                    <tr>
                                        <td>${row.StockID}</td>
                                        <td>${row.StockType}</td>
                                        <td>${row.GSM || 'N/A'}</td>
                                        <td>${row.Dimensions || 'N/A'}</td>
                                        <td>${row.usage_count}</td>
                                        <td>${row.total_quantity.toLocaleString()}</td>
                                    </tr>
                                `).join('')}
                        </tbody>
                    </table>
                </div>
            `;

                // Create Plotly chart
                PlotlyChartHelper.createUsageChart(result.data, 'usage-chart');
            }

        } catch (error) {
            console.error('[ERROR]', error);
        }
    }

    /**
     * Load profit analysis with Plotly chart
     */
    async loadProfitAnalysisWithChart(days = 90) {
        console.log(`[LOAD] Loading profit analysis with Plotly chart for ${days} days...`);

        try {
            const response = await fetch(`${this.backendUrl}/api/stock-management/profit-analysis?days=${days}`);
            const result = await response.json();

            if (result.status === 'ok') {
                const container = document.querySelector('#profit-analysis-content');
                container.innerHTML = `
                <div class="summary-cards">
                    <div class="card">
                        <h4>Total Revenue</h4>
                        <div class="value">$${result.summary.total_revenue.toLocaleString()}</div>
                    </div>
                    <div class="card">
                        <h4>Total Cost</h4>
                        <div class="value">$${result.summary.total_cost.toLocaleString()}</div>
                    </div>
                    <div class="card">
                        <h4>Gross Profit</h4>
                        <div class="value">$${result.summary.total_profit.toLocaleString()}</div>
                    </div>
                    <div class="card">
                        <h4>Margin</h4>
                        <div class="value">${result.summary.overall_margin}%</div>
                    </div>
                </div>
                <div class="chart-container">
                    <div id="profit-chart" style="width:100%;height:450px;"></div>
                </div>
            `;

                // Create Plotly chart
                PlotlyChartHelper.createProfitCharts(result.data, 'profit-chart');
            }

        } catch (error) {
            console.error('[ERROR]', error);
        }
    }

    /**
     * Load reorder dashboard with Plotly pie chart
     */
    async loadReorderDashboardWithChart() {
        console.log('[LOAD] Loading reorder dashboard with Plotly chart...');

        try {
            const response = await fetch(`${this.backendUrl}/api/stock-management/reorder-dashboard`);
            const result = await response.json();

            if (result.status === 'ok') {
                const container = document.querySelector('#reorder-dashboard-content');
                container.innerHTML = `
                <div class="chart-container">
                    <div id="reorder-alerts-chart" style="width:100%;height:350px;"></div>
                </div>
                <div class="alerts-grid">
                    ${result.data.map(stock => `
                            <div class="alert-card alert-${stock.alert_level}">
                                <div class="alert-header">
                                    <span class="stock-name">Stock #${stock.stock_id} - ${stock.stock_type_name}</span>
                                    <span class="badge badge-${stock.alert_level}">${stock.alert_level.toUpperCase()}</span>
                                </div>
                                <div class="alert-details">
                                    <div>Current: ${stock.current_level}</div>
                                    <div>Reorder Point: ${stock.reorder_point}</div>
                                    <div>Days Until Empty: ${stock.days_until_empty}</div>
                                    <div>Recommended Order: ${stock.recommended_order_qty}</div>
                                </div>
                            </div>
                        `).join('')}
                </div>
            `;

                // Create Plotly pie chart
                PlotlyChartHelper.createReorderAlertsChart(result.summary, 'reorder-alerts-chart');
            }

        } catch (error) {
            console.error('[ERROR]', error);
        }
    }

    // ========================================================================
    // SQL VIEWER METHODS (Delegate to SQLViewerHelper)
    // ========================================================================

    /**
     * Load SQL viewer interface
     */
    async loadSQLViewer() {
        console.log('[LOAD] Loading SQL Viewer...');

        const container = this.getSubTabContainer('sql-viewer');
        if (container && this.sqlViewer) {
            this.sqlViewer.renderInterface(container.id);
        }
    }

    /**
     * Execute SQL query (called from onclick handlers)
     */
    executeSQLQuery() {
        if (this.sqlViewer) {
            this.sqlViewer.executeQuery();
        }
    }

    /**
     * Clear SQL query editor
     */
    clearSQLQuery() {
        const editor = document.getElementById('sql-query-editor');
        if (editor) {
            editor.value = '';
        }
    }

    /**
     * Load query from history
     */
    loadHistoryQuery(index) {
        if (this.sqlViewer && this.sqlViewer.queryHistory[index]) {
            const query = this.sqlViewer.queryHistory[index].query;
            const editor = document.getElementById('sql-query-editor');
            if (editor) {
                editor.value = query;
            }
        }
    }

    /**
     * Load and display table list
     */
    async loadTableList() {
        try {
            const response = await fetch(`${this.backendUrl}/api/stock-management/sql-query`);
            const result = await response.json();

            if (result.status === 'ok') {
                let info = 'Available Tables:\n\n';
                result.tables.forEach(table => {
                    const cols = result.table_info[table];
                    info += `${table}: \n`;
                    cols.forEach(col => {
                        info += `  - ${col.name} (${col.type}) \n`;
                    });
                    info += '\n';
                });
                alert(info);
            }
        } catch (error) {
            console.error('Failed to load tables:', error);
        }
    }

    // ========================================================================
    // CELL EDITING METHODS (Delegate to CellEditingHelper)
    // ========================================================================

    /**
     * Handle cell edit (called from onblur handlers)
     */
    handleCellEdit(cell, column, rowIndex) {
        if (this.cellEditor) {
            this.cellEditor.handleEdit(cell, column, rowIndex);
        }
    }

    // ========================================================================
    // BULK OPERATIONS
    // ========================================================================

    bulkTagRows(color, tableName = null) {
        console.log(`[BULK TAG] Tagging selected rows as: ${color || 'cleared'}`);

        // Determine which table to operate on
        let table = null;
        let storageKey = '';

        // Try to determine from current active tab
        const activeTab = document.querySelector('.sub-tab-btn.active');
        if (activeTab) {
            const tabId = activeTab.getAttribute('data-tab');
            if (tabId === 'profit-analysis') {
                table = this.profitTable;
                storageKey = 'profit_tags';
            } else if (tabId === 'ai-analytics') {
                table = this.aiAnalyticsTable;
                storageKey = 'ai_analytics_tags';
            } else if (tabId === 'sql-viewer') {
                table = this.sqlViewerTable;
                storageKey = 'sql_viewer_tags';
            } else if (tabId === 'usage-analytics') {
                table = this.usageTable;
                storageKey = 'usage_tags';
            } else if (tabId === 'reorder-dashboard') {
                table = this.reorderTable;
                storageKey = 'reorder_tags';
            }
        }

        if (!table) {
            console.warn('[BULK TAG] No active table found');
            return;
        }

        const selectedRows = table.getSelectedRows();

        if (selectedRows.length === 0) {
            if (window.TabulatorToast) {
                window.TabulatorToast.showToast('No rows selected', 'warning', 3000);
            } else {
                alert('Please select rows first');
            }
            return;
        }

        let taggedCount = 0;
        selectedRows.forEach(row => {
            const rowData = row.getData();
            const rowId = rowData.stock_id || rowData.id || rowData._rowId;

            if (rowId) {
                if (color) {
                    window.TabulatorFunctions?.setRowTag(rowId, color, storageKey);
                } else {
                    window.TabulatorFunctions?.clearRowTag(rowId, storageKey);
                }
                row.reformat(); // Refresh row styling
                taggedCount++;
            }
        });

        // Deselect all rows after tagging
        table.deselectRow();

        // Show success message
        const message = color ?
            `Tagged ${taggedCount} rows as ${color}` :
            `Cleared tags from ${taggedCount} rows`;

        if (window.TabulatorToast) {
            window.TabulatorToast.showToast(message, 'success', 3000);
        } else {
            console.log(`[BULK TAG] ${message}`);
        }

        this.updateSelectionCount();
    }

    updateSelectionCount() {
        // Find all selection count displays and update them
        const countDisplays = ['profit-selected-count', 'ai-selected-count', 'sql-selected-count'];

        countDisplays.forEach(displayId => {
            const display = document.getElementById(displayId);
            if (display) {
                // Get the corresponding table
                let table = null;
                if (displayId.includes('profit')) table = this.profitTable;
                else if (displayId.includes('ai')) table = this.aiAnalyticsTable;
                else if (displayId.includes('sql')) table = this.sqlViewerTable;

                if (table) {
                    const selectedRows = table.getSelectedRows();
                    display.textContent = `${selectedRows.length} selected`;
                }
            }
        });
    }

    // ========================================================================
    // EXPORT FUNCTIONALITY
    // ========================================================================

    exportProfit(format = 'xlsx') {
        if (!this.profitTable) {
            alert('No data to export');
            return;
        }

        const fileName = `profit_analysis_${new Date().toISOString().split('T')[0]}`;
        console.log(`[EXPORT] Exporting Profit Analysis as ${format}`);

        if (format === 'xlsx') {
            this.profitTable.download("xlsx", `${fileName}.xlsx`, { sheetName: "Profit Analysis" });
        } else if (format === 'csv') {
            this.profitTable.download("csv", `${fileName}.csv`);
        } else if (format === 'pdf') {
            this.profitTable.download("pdf", `${fileName}.pdf`, {
                orientation: "landscape",
                title: "Profit Analysis Report",
                autoTable: {
                    styles: { fontSize: 8 },
                    margin: { top: 40 }
                }
            });
        } else if (format === 'json') {
            this.profitTable.download("json", `${fileName}.json`);
        }

        if (window.TabulatorToast) {
            window.TabulatorToast.showToast(`Exported as ${format.toUpperCase()}`, 'success', 3000);
        }
    }

    exportAIAnalytics(format = 'xlsx') {
        if (!this.aiAnalyticsTable) {
            alert('No data to export');
            return;
        }

        const fileName = `ai_analytics_${new Date().toISOString().split('T')[0]}`;
        console.log(`[EXPORT] Exporting AI Analytics as ${format}`);

        if (format === 'xlsx') {
            this.aiAnalyticsTable.download("xlsx", `${fileName}.xlsx`, { sheetName: "AI Analytics" });
        } else if (format === 'csv') {
            this.aiAnalyticsTable.download("csv", `${fileName}.csv`);
        } else if (format === 'pdf') {
            this.aiAnalyticsTable.download("pdf", `${fileName}.pdf`, {
                orientation: "landscape",
                title: "AI Analytics Report"
            });
        } else if (format === 'json') {
            this.aiAnalyticsTable.download("json", `${fileName}.json`);
        }

        if (window.TabulatorToast) {
            window.TabulatorToast.showToast(`Exported as ${format.toUpperCase()}`, 'success', 3000);
        }
    }

    exportSQLResults(format = 'xlsx') {
        if (!this.sqlViewerTable) {
            alert('No data to export');
            return;
        }

        const fileName = `sql_results_${new Date().toISOString().split('T')[0]}`;
        console.log(`[EXPORT] Exporting SQL Results as ${format}`);

        if (format === 'xlsx') {
            this.sqlViewerTable.download("xlsx", `${fileName}.xlsx`, { sheetName: "SQL Results" });
        } else if (format === 'csv') {
            this.sqlViewerTable.download("csv", `${fileName}.csv`);
        } else if (format === 'pdf') {
            this.sqlViewerTable.download("pdf", `${fileName}.pdf`, {
                orientation: "landscape",
                title: "SQL Query Results"
            });
        } else if (format === 'json') {
            this.sqlViewerTable.download("json", `${fileName}.json`);
        }

        if (window.TabulatorToast) {
            window.TabulatorToast.showToast(`Exported as ${format.toUpperCase()}`, 'success', 3000);
        }
    }

    // ========================================================================
    // API CONNECTION TESTING (Development Tool)
    // ========================================================================

    /**
     * Test all Tabulator API endpoints to verify data flow
     * This is a development/debugging tool to verify that:
     * 1. Backend APIs are responding correctly
     * 2. Data structure matches Tabulator expectations
     * 3. All endpoints return valid data
     * 
     * Usage: stockModule.runAPIConnectionTest()
     */
    async runAPIConnectionTest() {
        console.log('\n' + '='.repeat(70));
        console.log('TABULATOR API CONNECTION TEST');
        console.log('Time: ' + new Date().toLocaleString());
        console.log('='.repeat(70) + '\n');

        const tests = [
            {
                name: 'Health Check',
                endpoint: '/health',
                method: 'GET',
                validateData: (data) => data.app && data.providers
            },
            {
                name: 'Usage Analytics',
                endpoint: '/api/stock-management/usage-analytics?days=90',
                method: 'GET',
                dataKey: 'data',
                validateData: (data) => Array.isArray(data.data)
            },
            {
                name: 'Reorder Dashboard',
                endpoint: '/api/stock-management/reorder-dashboard',
                method: 'GET',
                dataKey: 'data',
                validateData: (data) => Array.isArray(data.data)
            },
            {
                name: 'Profit Analysis',
                endpoint: '/api/stock-management/profit-analysis?days=90',
                method: 'GET',
                dataKey: 'data',
                validateData: (data) => Array.isArray(data.data)
            },
            {
                name: 'AI Analytics',
                endpoint: '/api/stock/ai-analytics',
                method: 'GET',
                dataKey: 'queries',
                validateData: (data) => Array.isArray(data.queries)
            },
            {
                name: 'SQL Query',
                endpoint: '/api/stock-management/sql-query',
                method: 'POST',
                dataKey: 'data',
                body: { query: 'SELECT * FROM unified_stocks LIMIT 5' },
                validateData: (data) => Array.isArray(data.data) && Array.isArray(data.columns)
            }
        ];

        let passed = 0;
        let failed = 0;
        const results = [];

        for (const test of tests) {
            try {
                const startTime = performance.now();

                const options = {
                    method: test.method,
                    headers: { 'Content-Type': 'application/json' }
                };

                if (test.body) {
                    options.body = JSON.stringify(test.body);
                }

                const response = await fetch(`${this.backendUrl}${test.endpoint}`, options);
                const responseTime = ((performance.now() - startTime) / 1000).toFixed(2);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();

                // Validate data structure
                if (!test.validateData(data)) {
                    throw new Error('Invalid data structure');
                }

                // Count records
                const dataArray = test.dataKey ? data[test.dataKey] : [];
                const recordCount = Array.isArray(dataArray) ? dataArray.length : 0;

                // Success
                passed++;
                results.push({
                    name: test.name,
                    passed: true,
                    recordCount,
                    responseTime,
                    status: response.status
                });

                console.log(`✅ ${test.name}: ${recordCount} records in ${responseTime}s`);

            } catch (error) {
                failed++;
                results.push({
                    name: test.name,
                    passed: false,
                    error: error.message
                });

                console.error(`❌ ${test.name}: ${error.message}`);
            }
        }

        // Print summary
        console.log('\n' + '='.repeat(70));
        console.log('TEST SUMMARY');
        console.log('='.repeat(70));
        console.log(`Total Tests: ${tests.length}`);
        console.log(`Passed: ${passed}`);
        console.log(`Failed: ${failed}`);
        console.log(`Pass Rate: ${((passed / tests.length) * 100).toFixed(1)}%\n`);

        // Tabulator compatibility check
        console.log('='.repeat(70));
        console.log('TABULATOR COMPATIBILITY CHECK');
        console.log('='.repeat(70) + '\n');

        for (const result of results) {
            if (result.passed) {
                if (result.recordCount === 0) {
                    console.log(`⚠️  ${result.name}: No data (may be expected)`);
                } else {
                    console.log(`✅ ${result.name}: Compatible (${result.recordCount} records)`);
                }
            } else {
                console.log(`❌ ${result.name}: FAILED`);
            }
        }

        console.log('\n' + '='.repeat(70));

        if (failed === 0) {
            console.log('\n🎉 All tests passed! APIs are ready for Tabulator.\n');
        } else {
            console.log(`\n⚠️  ${failed} test(s) failed. Check backend and database.\n`);
        }

        return { passed, failed, results };
    }

    /**
     * Quick test of a single endpoint
     * Usage: stockModule.testEndpoint('reorder-dashboard')
     */
    async testEndpoint(name) {
        const endpoints = {
            'usage': '/api/stock-management/usage-analytics?days=90',
            'reorder': '/api/stock-management/reorder-dashboard',
            'profit': '/api/stock-management/profit-analysis?days=90',
            'ai': '/api/stock/ai-analytics',
            'sql': '/api/stock-management/sql-query'
        };

        const endpoint = endpoints[name];
        if (!endpoint) {
            console.error(`Unknown endpoint: ${name}`);
            console.log(`Available: ${Object.keys(endpoints).join(', ')}`);
            return;
        }

        console.log(`Testing ${name} endpoint: ${endpoint}`);

        try {
            const options = {
                method: name === 'sql' ? 'POST' : 'GET',
                headers: { 'Content-Type': 'application/json' }
            };

            if (name === 'sql') {
                options.body = JSON.stringify({ query: 'SELECT * FROM unified_stocks LIMIT 5' });
            }

            const response = await fetch(`${this.backendUrl}${endpoint}`, options);
            const data = await response.json();

            console.log('Response:', data);

            const dataKey = name === 'ai' ? 'queries' : 'data';
            const records = data[dataKey] || [];
            console.log(`✅ Success: ${records.length} records`);

            return data;
        } catch (error) {
            console.error(`❌ Failed: ${error.message}`);
            return null;
        }
    }

    // ========================================================================
    // UTILITY METHODS
    // ========================================================================

    getSubTabContainer(tabName) {
        // Return the tab container created by BaseModule
        // BaseModule creates containers with IDs like: stock-management-subtab-usage-analytics
        return document.getElementById(`${this.moduleId}-subtab-${tabName}`);
    }

    showError(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>${message}</p>
                </div>
            `;
        }
    }
}

// Register the module in ModuleRegistry (required for auto-discovery)
if (typeof window !== 'undefined') {
    // Ensure ModuleRegistry exists
    if (!window.ModuleRegistry) {
        window.ModuleRegistry = {};
    }

    // Register the module class
    window.ModuleRegistry['stock-management'] = StockManagementModule;
    console.log('✅ StockManagementModule class registered in ModuleRegistry (Combined Edition)');
    console.log('   Includes: Base Module + Plotly Charts + SQL Viewer + Cell Editing');
    console.log('   (Instance reference will be created by ModuleManager after initialization)');
}

console.log('✅ Stock Management Module Loaded - Combined Edition v1.1.0');
console.log('   Features: Invoice Processing, Usage Analytics, Reorder Dashboard, Profit Analysis, SQL Viewer, AI Analytics');
console.log('   Enhancements: Plotly.js charts, SQL query interface, inline cell editing');
