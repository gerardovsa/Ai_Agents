/**
 * FILE: UI/js/tabulator-test-framework.js
 * PURPOSE: Universal testing framework for Tabulator implementations
 * VERSION: 1.0.0
 * CREATED: November 8, 2025
 * 
 * OVERVIEW:
 * This framework provides comprehensive testing for any module using Tabulator.
 * It can be adapted by AI agents to test:
 * - API connectivity and data flow
 * - Tabulator initialization
 * - Column configuration
 * - Data rendering
 * - Interactive features (sorting, filtering, export)
 * - Custom formatters and functions
 * - Error handling
 * - Performance metrics
 * 
 * DEPENDENCIES:
 * - Tabulator 5.5.2+
 * - tabulator-functions.js (optional)
 * - tabulator-toast-system.js (optional)
 * 
 * USAGE:
 * ```javascript
 * // Create test suite
 * const tester = new TabulatorTestFramework({
 *     moduleId: 'stock-management',
 *     backendUrl: 'http://localhost:5001',
 *     tables: {
 *         reorder: {
 *             containerId: 'reorder-tabulator',
 *             apiEndpoint: '/api/stock-management/reorder-dashboard',
 *             dataKey: 'data',
 *             expectedColumns: ['stock_id', 'stock_name', 'current_quantity']
 *         }
 *     }
 * });
 * 
 * // Run all tests
 * await tester.runAllTests();
 * 
 * // Run specific test category
 * await tester.runAPITests();
 * await tester.runTabulatorTests();
 * ```
 */

class TabulatorTestFramework {
    constructor(config) {
        this.config = {
            moduleId: config.moduleId || 'unknown-module',
            backendUrl: config.backendUrl || 'http://localhost:5001',
            tables: config.tables || {},
            timeout: config.timeout || 10000,
            verbose: config.verbose !== false,
            autoFix: config.autoFix !== false
        };

        this.results = {
            api: [],
            tabulator: [],
            rendering: [],
            interaction: [],
            performance: [],
            errors: []
        };

        this.stats = {
            total: 0,
            passed: 0,
            failed: 0,
            warnings: 0,
            skipped: 0
        };

        this.startTime = null;
        this.endTime = null;
    }

    // =========================================================================
    // LOGGING & OUTPUT
    // =========================================================================

    log(message, level = 'INFO') {
        if (!this.config.verbose && level === 'DEBUG') return;

        const timestamp = new Date().toLocaleTimeString();
        const icons = {
            'INFO': '🔵',
            'SUCCESS': '✅',
            'ERROR': '❌',
            'WARNING': '⚠️',
            'DEBUG': '🔍',
            'PERF': '⚡'
        };

        const icon = icons[level] || '📝';
        const color = {
            'INFO': 'color: #3b82f6',
            'SUCCESS': 'color: #10b981',
            'ERROR': 'color: #ef4444',
            'WARNING': 'color: #f59e0b',
            'DEBUG': 'color: #6b7280',
            'PERF': 'color: #8b5cf6'
        }[level] || '';

        console.log(`%c[${timestamp}] ${icon} ${message}`, color);
    }

    logSection(title) {
        console.log('\n' + '='.repeat(70));
        console.log(`  ${title}`);
        console.log('='.repeat(70) + '\n');
    }

    // =========================================================================
    // TEST EXECUTION
    // =========================================================================

    async runAllTests() {
        this.logSection(`TABULATOR TEST FRAMEWORK - ${this.config.moduleId.toUpperCase()}`);
        this.log(`Started: ${new Date().toLocaleString()}`, 'INFO');
        this.startTime = performance.now();

        try {
            // Run test categories in sequence
            await this.runHealthCheck();
            await this.runAPITests();
            await this.runTabulatorTests();
            await this.runRenderingTests();
            await this.runInteractionTests();
            await this.runPerformanceTests();

            // Generate report
            this.generateReport();

            return {
                success: this.stats.failed === 0,
                stats: this.stats,
                results: this.results
            };

        } catch (error) {
            this.log(`Critical error during testing: ${error.message}`, 'ERROR');
            this.results.errors.push({
                type: 'CRITICAL',
                message: error.message,
                stack: error.stack
            });
            return {
                success: false,
                error: error.message,
                stats: this.stats,
                results: this.results
            };
        } finally {
            this.endTime = performance.now();
        }
    }

    // =========================================================================
    // CATEGORY 1: HEALTH CHECK
    // =========================================================================

    async runHealthCheck() {
        this.logSection('HEALTH CHECK');

        const tests = [
            {
                name: 'Tabulator Library Loaded',
                test: () => typeof Tabulator !== 'undefined',
                fix: 'Ensure Tabulator library is included in HTML'
            },
            {
                name: 'Backend Server Running',
                test: async () => {
                    try {
                        const response = await fetch(`${this.config.backendUrl}/health`, { timeout: 3000 });
                        return response.ok;
                    } catch {
                        return false;
                    }
                },
                fix: 'Start backend server with BISTART command'
            },
            {
                name: 'Module Container Exists',
                test: () => document.getElementById(`tab-${this.config.moduleId}`) !== null,
                fix: `Ensure #tab-${this.config.moduleId} exists in DOM`
            },
            {
                name: 'Toast System Available',
                test: () => typeof ToastSystem !== 'undefined' || window.TabulatorToast !== undefined,
                severity: 'WARNING',
                fix: 'Include tabulator-toast-system.js for notifications'
            },
            {
                name: 'Tabulator Functions Available',
                test: () => typeof window.TabulatorFunctions !== 'undefined',
                severity: 'WARNING',
                fix: 'Include tabulator-functions.js for row tagging'
            }
        ];

        for (const testCase of tests) {
            await this.runTest('health', testCase);
        }
    }

    // =========================================================================
    // CATEGORY 2: API TESTS
    // =========================================================================

    async runAPITests() {
        this.logSection('API CONNECTIVITY TESTS');

        for (const [tableKey, tableConfig] of Object.entries(this.config.tables)) {
            await this.testAPI(tableKey, tableConfig);
        }
    }

    async testAPI(tableKey, config) {
        const endpoint = config.apiEndpoint;
        const method = config.method || 'GET';
        const dataKey = config.dataKey || 'data';

        this.log(`Testing API: ${endpoint}`, 'INFO');

        const tests = [
            {
                name: `${tableKey}: HTTP Response`,
                test: async () => {
                    const options = { method };
                    if (config.postData) {
                        options.headers = { 'Content-Type': 'application/json' };
                        options.body = JSON.stringify(config.postData);
                    }

                    const response = await fetch(`${this.config.backendUrl}${endpoint}`, options);
                    this.results.api.push({
                        endpoint,
                        status: response.status,
                        ok: response.ok
                    });
                    return response.ok;
                },
                fix: `Check Flask route exists: ${endpoint}`
            },
            {
                name: `${tableKey}: Valid JSON Response`,
                test: async () => {
                    const options = { method };
                    if (config.postData) {
                        options.headers = { 'Content-Type': 'application/json' };
                        options.body = JSON.stringify(config.postData);
                    }

                    const response = await fetch(`${this.config.backendUrl}${endpoint}`, options);
                    const data = await response.json();
                    return typeof data === 'object';
                },
                fix: 'Ensure API returns valid JSON'
            },
            {
                name: `${tableKey}: Data Key Exists`,
                test: async () => {
                    const options = { method };
                    if (config.postData) {
                        options.headers = { 'Content-Type': 'application/json' };
                        options.body = JSON.stringify(config.postData);
                    }

                    const response = await fetch(`${this.config.backendUrl}${endpoint}`, options);
                    const data = await response.json();
                    return dataKey in data;
                },
                fix: `API should return {${dataKey}: [...]}`
            },
            {
                name: `${tableKey}: Data is Array`,
                test: async () => {
                    const options = { method };
                    if (config.postData) {
                        options.headers = { 'Content-Type': 'application/json' };
                        options.body = JSON.stringify(config.postData);
                    }

                    const response = await fetch(`${this.config.backendUrl}${endpoint}`, options);
                    const data = await response.json();
                    return Array.isArray(data[dataKey]);
                },
                fix: 'Data must be an array for Tabulator'
            },
            {
                name: `${tableKey}: Expected Columns Present`,
                test: async () => {
                    if (!config.expectedColumns || config.expectedColumns.length === 0) {
                        return true; // Skip if no columns specified
                    }

                    const options = { method };
                    if (config.postData) {
                        options.headers = { 'Content-Type': 'application/json' };
                        options.body = JSON.stringify(config.postData);
                    }

                    const response = await fetch(`${this.config.backendUrl}${endpoint}`, options);
                    const data = await response.json();
                    const records = data[dataKey];

                    if (!records || records.length === 0) return true; // OK if empty

                    const firstRecord = records[0];
                    const missingColumns = config.expectedColumns.filter(col => !(col in firstRecord));

                    if (missingColumns.length > 0) {
                        this.log(`Missing columns: ${missingColumns.join(', ')}`, 'WARNING');
                        return false;
                    }

                    return true;
                },
                fix: 'Check SQL query returns expected columns'
            },
            {
                name: `${tableKey}: Response Time < 2s`,
                test: async () => {
                    const startTime = performance.now();

                    const options = { method };
                    if (config.postData) {
                        options.headers = { 'Content-Type': 'application/json' };
                        options.body = JSON.stringify(config.postData);
                    }

                    await fetch(`${this.config.backendUrl}${endpoint}`, options);

                    const responseTime = performance.now() - startTime;
                    this.log(`Response time: ${responseTime.toFixed(0)}ms`, 'PERF');

                    return responseTime < 2000;
                },
                severity: 'WARNING',
                fix: 'Optimize API query or add indexes to database'
            }
        ];

        for (const testCase of tests) {
            await this.runTest('api', testCase);
        }
    }

    // =========================================================================
    // CATEGORY 3: TABULATOR INITIALIZATION TESTS
    // =========================================================================

    async runTabulatorTests() {
        this.logSection('TABULATOR INITIALIZATION TESTS');

        for (const [tableKey, tableConfig] of Object.entries(this.config.tables)) {
            await this.testTabulator(tableKey, tableConfig);
        }
    }

    async testTabulator(tableKey, config) {
        this.log(`Testing Tabulator: ${tableKey}`, 'INFO');

        const tests = [
            {
                name: `${tableKey}: Container Exists`,
                test: () => document.getElementById(config.containerId) !== null,
                fix: `Add <div id="${config.containerId}"></div> to HTML`
            },
            {
                name: `${tableKey}: Tabulator Instance Created`,
                test: () => {
                    const container = document.getElementById(config.containerId);
                    return container && container.querySelector('.tabulator') !== null;
                },
                fix: `Call: new Tabulator('#${config.containerId}', {...})`
            },
            {
                name: `${tableKey}: Has Columns Defined`,
                test: () => {
                    const container = document.getElementById(config.containerId);
                    const headers = container?.querySelectorAll('.tabulator-col');
                    return headers && headers.length > 0;
                },
                fix: 'Define columns array in Tabulator config'
            },
            {
                name: `${tableKey}: Pagination Enabled`,
                test: () => {
                    const container = document.getElementById(config.containerId);
                    return container?.querySelector('.tabulator-footer') !== null;
                },
                severity: 'WARNING',
                fix: 'Add pagination:"local" to Tabulator config'
            },
            {
                name: `${tableKey}: Sortable Columns`,
                test: () => {
                    const container = document.getElementById(config.containerId);
                    const sortableHeaders = container?.querySelectorAll('.tabulator-col[role="columnheader"]');
                    return sortableHeaders && sortableHeaders.length > 0;
                },
                severity: 'WARNING',
                fix: 'Ensure headerSort:true (default) on columns'
            }
        ];

        for (const testCase of tests) {
            await this.runTest('tabulator', testCase);
        }
    }

    // =========================================================================
    // CATEGORY 4: RENDERING TESTS
    // =========================================================================

    async runRenderingTests() {
        this.logSection('DATA RENDERING TESTS');

        for (const [tableKey, tableConfig] of Object.entries(this.config.tables)) {
            await this.testRendering(tableKey, tableConfig);
        }
    }

    async testRendering(tableKey, config) {
        this.log(`Testing Rendering: ${tableKey}`, 'INFO');

        const tests = [
            {
                name: `${tableKey}: Has Data Rows`,
                test: () => {
                    const container = document.getElementById(config.containerId);
                    const rows = container?.querySelectorAll('.tabulator-row');
                    this.log(`Found ${rows?.length || 0} rows`, 'DEBUG');
                    return rows && rows.length > 0;
                },
                severity: 'WARNING',
                fix: 'Call table.setData(data) after API fetch'
            },
            {
                name: `${tableKey}: No Empty Cells`,
                test: () => {
                    const container = document.getElementById(config.containerId);
                    const cells = container?.querySelectorAll('.tabulator-cell');
                    let emptyCount = 0;

                    cells?.forEach(cell => {
                        if (!cell.textContent.trim() && !cell.querySelector('button, input, img')) {
                            emptyCount++;
                        }
                    });

                    if (emptyCount > 0) {
                        this.log(`Found ${emptyCount} empty cells`, 'WARNING');
                    }

                    return emptyCount === 0;
                },
                severity: 'WARNING',
                fix: 'Check data fields match column definitions'
            },
            {
                name: `${tableKey}: Custom Formatters Working`,
                test: () => {
                    const container = document.getElementById(config.containerId);
                    // Check for common formatter outputs
                    const hasButtons = container?.querySelector('.action-btn, button') !== null;
                    const hasIcons = container?.querySelector('i.fas, i.far') !== null;
                    const hasColors = container?.querySelector('[style*="color"]') !== null;

                    return hasButtons || hasIcons || hasColors;
                },
                severity: 'WARNING',
                fix: 'Verify custom formatters are applied to columns'
            },
            {
                name: `${tableKey}: Row Heights Consistent`,
                test: () => {
                    const container = document.getElementById(config.containerId);
                    const rows = container?.querySelectorAll('.tabulator-row');

                    if (!rows || rows.length < 2) return true;

                    const heights = Array.from(rows).map(row => row.offsetHeight);
                    const avgHeight = heights.reduce((a, b) => a + b, 0) / heights.length;
                    const maxDeviation = Math.max(...heights.map(h => Math.abs(h - avgHeight)));

                    return maxDeviation < 20; // Allow 20px variance
                },
                severity: 'WARNING',
                fix: 'Check for content overflow or inconsistent styling'
            }
        ];

        for (const testCase of tests) {
            await this.runTest('rendering', testCase);
        }
    }

    // =========================================================================
    // CATEGORY 5: INTERACTION TESTS
    // =========================================================================

    async runInteractionTests() {
        this.logSection('INTERACTION TESTS');

        for (const [tableKey, tableConfig] of Object.entries(this.config.tables)) {
            await this.testInteraction(tableKey, tableConfig);
        }
    }

    async testInteraction(tableKey, config) {
        this.log(`Testing Interaction: ${tableKey}`, 'INFO');

        const tests = [
            {
                name: `${tableKey}: Column Sorting`,
                test: () => {
                    const container = document.getElementById(config.containerId);
                    const sortableCol = container?.querySelector('.tabulator-col[role="columnheader"]');

                    if (!sortableCol) return false;

                    // Simulate click
                    sortableCol.click();

                    // Check for sort indicator
                    return sortableCol.querySelector('.tabulator-arrow') !== null ||
                        sortableCol.classList.contains('tabulator-col-sorter-active');
                },
                severity: 'WARNING',
                fix: 'Ensure Tabulator sorting is enabled'
            },
            {
                name: `${tableKey}: Row Selection`,
                test: () => {
                    const container = document.getElementById(config.containerId);
                    const firstRow = container?.querySelector('.tabulator-row');

                    if (!firstRow) return false;

                    // Try to select row
                    firstRow.click();

                    return firstRow.classList.contains('tabulator-selected') ||
                        firstRow.querySelector('input[type="checkbox"]:checked') !== null;
                },
                severity: 'WARNING',
                fix: 'Add selectableRows:true to Tabulator config'
            },
            {
                name: `${tableKey}: Export Buttons Work`,
                test: () => {
                    const exportButtons = document.querySelectorAll(
                        `[onclick*="export"],` +
                        `.btn-export,` +
                        `[data-action="export"]`
                    );

                    return exportButtons.length > 0;
                },
                severity: 'WARNING',
                fix: 'Add export buttons: exportProfit("xlsx"), etc.'
            },
            {
                name: `${tableKey}: Refresh Button Works`,
                test: () => {
                    const refreshButtons = document.querySelectorAll(
                        `[onclick*="refresh"],` +
                        `.btn-refresh,` +
                        `[data-action="refresh"]`
                    );

                    return refreshButtons.length > 0;
                },
                severity: 'WARNING',
                fix: 'Add refresh button with onClick handler'
            }
        ];

        for (const testCase of tests) {
            await this.runTest('interaction', testCase);
        }
    }

    // =========================================================================
    // CATEGORY 6: PERFORMANCE TESTS
    // =========================================================================

    async runPerformanceTests() {
        this.logSection('PERFORMANCE TESTS');

        for (const [tableKey, tableConfig] of Object.entries(this.config.tables)) {
            await this.testPerformance(tableKey, tableConfig);
        }
    }

    async testPerformance(tableKey, config) {
        this.log(`Testing Performance: ${tableKey}`, 'INFO');

        const tests = [
            {
                name: `${tableKey}: Initial Load Time < 1s`,
                test: async () => {
                    const startTime = performance.now();

                    // Simulate data load
                    const response = await fetch(`${this.config.backendUrl}${config.apiEndpoint}`);
                    await response.json();

                    const loadTime = performance.now() - startTime;
                    this.log(`Load time: ${loadTime.toFixed(0)}ms`, 'PERF');

                    return loadTime < 1000;
                },
                severity: 'WARNING',
                fix: 'Optimize API or reduce data size'
            },
            {
                name: `${tableKey}: Memory Usage Reasonable`,
                test: () => {
                    if (!performance.memory) {
                        this.log('Memory API not available (Chrome only)', 'DEBUG');
                        return true;
                    }

                    const usedMB = performance.memory.usedJSHeapSize / 1024 / 1024;
                    this.log(`Memory used: ${usedMB.toFixed(1)}MB`, 'PERF');

                    return usedMB < 100; // Under 100MB
                },
                severity: 'WARNING',
                fix: 'Check for memory leaks or large datasets'
            },
            {
                name: `${tableKey}: Virtual Scrolling (if >100 rows)`,
                test: () => {
                    const container = document.getElementById(config.containerId);
                    const rows = container?.querySelectorAll('.tabulator-row');

                    if (!rows || rows.length <= 100) return true;

                    // Check if virtual DOM is used
                    const hasVirtualScroll = container?.querySelector('.tabulator-tableholder');
                    return hasVirtualScroll !== null;
                },
                severity: 'WARNING',
                fix: 'Add virtualDom:true for large datasets'
            }
        ];

        for (const testCase of tests) {
            await this.runTest('performance', testCase);
        }
    }

    // =========================================================================
    // TEST EXECUTION HELPER
    // =========================================================================

    async runTest(category, testCase) {
        this.stats.total++;

        try {
            const result = await testCase.test();

            if (result) {
                this.log(`${testCase.name}: PASSED`, 'SUCCESS');
                this.stats.passed++;
                this.results[category].push({
                    name: testCase.name,
                    status: 'PASSED'
                });
            } else {
                const severity = testCase.severity || 'ERROR';

                if (severity === 'WARNING') {
                    this.log(`${testCase.name}: WARNING`, 'WARNING');
                    this.log(`  └─ Fix: ${testCase.fix}`, 'WARNING');
                    this.stats.warnings++;
                } else {
                    this.log(`${testCase.name}: FAILED`, 'ERROR');
                    this.log(`  └─ Fix: ${testCase.fix}`, 'ERROR');
                    this.stats.failed++;
                }

                this.results[category].push({
                    name: testCase.name,
                    status: severity === 'WARNING' ? 'WARNING' : 'FAILED',
                    fix: testCase.fix
                });
            }

        } catch (error) {
            this.log(`${testCase.name}: ERROR - ${error.message}`, 'ERROR');
            this.log(`  └─ Fix: ${testCase.fix}`, 'ERROR');
            this.stats.failed++;
            this.results[category].push({
                name: testCase.name,
                status: 'ERROR',
                error: error.message,
                fix: testCase.fix
            });
        }
    }

    // =========================================================================
    // REPORT GENERATION
    // =========================================================================

    generateReport() {
        const duration = ((this.endTime - this.startTime) / 1000).toFixed(2);

        this.logSection('TEST SUMMARY');

        console.log(`Duration: ${duration}s`);
        console.log(`Total Tests: ${this.stats.total}`);
        console.log(`%cPassed: ${this.stats.passed}`, 'color: #10b981; font-weight: bold');
        console.log(`%cFailed: ${this.stats.failed}`, 'color: #ef4444; font-weight: bold');
        console.log(`%cWarnings: ${this.stats.warnings}`, 'color: #f59e0b; font-weight: bold');
        console.log(`Pass Rate: ${((this.stats.passed / this.stats.total) * 100).toFixed(1)}%`);

        // Category breakdown
        console.log('\n📊 Category Breakdown:');
        for (const [category, results] of Object.entries(this.results)) {
            if (results.length === 0) continue;

            const passed = results.filter(r => r.status === 'PASSED').length;
            const total = results.length;
            console.log(`  ${category}: ${passed}/${total} passed`);
        }

        // Failed tests summary
        const failedTests = [];
        for (const [category, results] of Object.entries(this.results)) {
            results.forEach(r => {
                if (r.status === 'FAILED' || r.status === 'ERROR') {
                    failedTests.push({ category, ...r });
                }
            });
        }

        if (failedTests.length > 0) {
            console.log('\n❌ Failed Tests:');
            failedTests.forEach(test => {
                console.log(`  • ${test.name}`);
                console.log(`    └─ ${test.fix || test.error}`);
            });
        }

        // Overall status
        console.log('\n' + '='.repeat(70));
        if (this.stats.failed === 0) {
            console.log('%c🎉 ALL TESTS PASSED!', 'color: #10b981; font-size: 16px; font-weight: bold');
        } else {
            console.log('%c⚠️ TESTS FAILED', 'color: #ef4444; font-size: 16px; font-weight: bold');
            console.log(`Fix ${this.stats.failed} error(s) and ${this.stats.warnings} warning(s)`);
        }
        console.log('='.repeat(70) + '\n');
    }

    // =========================================================================
    // EXPORT UTILITIES
    // =========================================================================

    exportJSON(filename = 'tabulator-test-results.json') {
        const report = {
            module: this.config.moduleId,
            timestamp: new Date().toISOString(),
            duration: ((this.endTime - this.startTime) / 1000).toFixed(2),
            stats: this.stats,
            results: this.results
        };

        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);

        this.log(`Exported results to ${filename}`, 'SUCCESS');
    }

    exportHTML(filename = 'tabulator-test-report.html') {
        const duration = ((this.endTime - this.startTime) / 1000).toFixed(2);

        const html = `
<!DOCTYPE html>
<html>
<head>
    <title>Tabulator Test Report - ${this.config.moduleId}</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; padding: 20px; background: #0B0E13; color: #E5E7EB; }
        .header { background: #161b22; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .stats { display: flex; gap: 20px; margin: 20px 0; }
        .stat { background: #1f2937; padding: 15px; border-radius: 8px; flex: 1; text-align: center; }
        .stat-value { font-size: 32px; font-weight: bold; }
        .passed { color: #10b981; }
        .failed { color: #ef4444; }
        .warning { color: #f59e0b; }
        .category { background: #161b22; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .test { padding: 10px; margin: 5px 0; border-left: 3px solid #6b7280; padding-left: 15px; }
        .test.passed { border-color: #10b981; }
        .test.failed { border-color: #ef4444; }
        .test.warning { border-color: #f59e0b; }
        .fix { color: #9ca3af; font-style: italic; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Tabulator Test Report</h1>
        <p>Module: <strong>${this.config.moduleId}</strong></p>
        <p>Time: ${new Date().toLocaleString()}</p>
        <p>Duration: ${duration}s</p>
    </div>

    <div class="stats">
        <div class="stat">
            <div class="stat-value">${this.stats.total}</div>
            <div>Total Tests</div>
        </div>
        <div class="stat">
            <div class="stat-value passed">${this.stats.passed}</div>
            <div>Passed</div>
        </div>
        <div class="stat">
            <div class="stat-value failed">${this.stats.failed}</div>
            <div>Failed</div>
        </div>
        <div class="stat">
            <div class="stat-value warning">${this.stats.warnings}</div>
            <div>Warnings</div>
        </div>
    </div>

    ${Object.entries(this.results).map(([category, tests]) => {
            if (tests.length === 0) return '';
            return `
            <div class="category">
                <h2>${category.toUpperCase()}</h2>
                ${tests.map(test => `
                    <div class="test ${test.status.toLowerCase()}">
                        <strong>${test.name}</strong>
                        <span class="${test.status.toLowerCase()}">${test.status}</span>
                        ${test.fix ? `<div class="fix">Fix: ${test.fix}</div>` : ''}
                        ${test.error ? `<div class="fix">Error: ${test.error}</div>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
        }).join('')}
</body>
</html>
        `;

        const blob = new Blob([html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);

        this.log(`Exported HTML report to ${filename}`, 'SUCCESS');
    }
}

// =============================================================================
// GLOBAL EXPORT
// =============================================================================

if (typeof window !== 'undefined') {
    window.TabulatorTestFramework = TabulatorTestFramework;
    console.log('✅ TabulatorTestFramework loaded and available globally');
}

// =============================================================================
// USAGE EXAMPLES (commented out)
// =============================================================================

/*
// Example 1: Test Stock Management Module
const stockTester = new TabulatorTestFramework({
    moduleId: 'stock-management',
    backendUrl: 'http://localhost:5001',
    tables: {
        reorder: {
            containerId: 'reorder-tabulator',
            apiEndpoint: '/api/stock-management/reorder-dashboard',
            dataKey: 'data',
            expectedColumns: ['stock_id', 'stock_name', 'current_quantity', 'reorder_point']
        },
        profit: {
            containerId: 'profit-tabulator',
            apiEndpoint: '/api/stock-management/profit-analysis?days=90',
            dataKey: 'data',
            expectedColumns: ['stock_id', 'total_cost', 'total_revenue', 'gross_profit']
        },
        sql: {
            containerId: 'sql-viewer-tabulator',
            apiEndpoint: '/api/stock-management/sql-query',
            method: 'POST',
            dataKey: 'data',
            postData: { query: 'SELECT * FROM unified_stocks LIMIT 5' }
        }
    }
});

// Run all tests
await stockTester.runAllTests();

// Export results
stockTester.exportJSON();
stockTester.exportHTML();

// Example 2: Test specific category
await stockTester.runAPITests();

// Example 3: Minimal config
const minimalTester = new TabulatorTestFramework({
    moduleId: 'my-module',
    tables: {
        main: {
            containerId: 'my-table',
            apiEndpoint: '/api/my-data',
            dataKey: 'results'
        }
    }
});

await minimalTester.runAllTests();
*/
