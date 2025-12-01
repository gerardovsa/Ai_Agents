/**
 * FILE: UI/js/tabulator-test-config-template.js
 * PURPOSE: Ready-to-use configuration templates for TabulatorTestFramework
 * VERSION: 1.0.0
 * CREATED: November 8, 2025
 * 
 * USAGE:
 * 1. Copy the template that matches your module
 * 2. Replace placeholder values with actual module data
 * 3. Run: await tester.runAllTests()
 */

// =============================================================================
// TEMPLATE 1: STOCK MANAGEMENT MODULE (Complete Example)
// =============================================================================

const stockManagementConfig = {
    moduleId: 'stock-management',
    backendUrl: 'http://localhost:5001',
    timeout: 10000,
    verbose: true,
    tables: {
        reorder: {
            containerId: 'reorder-tabulator',
            apiEndpoint: '/api/stock-management/reorder-dashboard',
            dataKey: 'data',
            expectedColumns: [
                'stock_id',
                'stock_name',
                'stock_type',
                'current_quantity',
                'reorder_point',
                'reorder_quantity',
                'alert_level',
                'days_until_stockout'
            ]
        },
        profit: {
            containerId: 'profit-tabulator',
            apiEndpoint: '/api/stock-management/profit-analysis?days=90',
            dataKey: 'data',
            expectedColumns: [
                'stock_id',
                'stock_name',
                'total_jobs',
                'total_cost',
                'total_revenue',
                'gross_profit',
                'margin_percent',
                'avg_profit_per_job'
            ]
        },
        usage: {
            containerId: 'usage-tabulator',
            apiEndpoint: '/api/stock-management/usage-analytics?days=90',
            dataKey: 'data',
            expectedColumns: [
                'stock_id',
                'stock_name',
                'stock_type',
                'usage_count',
                'total_quantity_used',
                'avg_usage_per_job',
                'trend',
                'last_used',
                'status'
            ]
        },
        aiAnalytics: {
            containerId: 'ai-analytics-tabulator',
            apiEndpoint: '/api/stock/ai-analytics',
            dataKey: 'queries',  // Note: Different data key!
            expectedColumns: [
                'query_id',
                'query_text',
                'timestamp',
                'status',
                'results_count'
            ]
        },
        sqlViewer: {
            containerId: 'sql-viewer-tabulator',
            apiEndpoint: '/api/stock-management/sql-query',
            method: 'POST',
            dataKey: 'data',
            postData: {
                query: 'SELECT * FROM unified_stocks LIMIT 5'
            }
            // Note: No expectedColumns for dynamic SQL viewer
        }
    }
};

// Usage:
// const tester = new TabulatorTestFramework(stockManagementConfig);
// await tester.runAllTests();

// =============================================================================
// TEMPLATE 2: SINGLE TABLE MODULE (Minimal Example)
// =============================================================================

const singleTableConfig = {
    moduleId: 'my-module',
    backendUrl: 'http://localhost:5001',
    tables: {
        main: {
            containerId: 'my-table',
            apiEndpoint: '/api/my-data',
            dataKey: 'results'
        }
    }
};

// =============================================================================
// TEMPLATE 3: E-COMMERCE MODULE
// =============================================================================

const ecommerceConfig = {
    moduleId: 'woocommerce',
    backendUrl: 'http://localhost:5001',
    tables: {
        orders: {
            containerId: 'orders-table',
            apiEndpoint: '/api/woocommerce/orders',
            dataKey: 'data',
            expectedColumns: [
                'order_id',
                'customer_name',
                'order_date',
                'total',
                'status'
            ]
        },
        products: {
            containerId: 'products-table',
            apiEndpoint: '/api/woocommerce/products',
            dataKey: 'data',
            expectedColumns: [
                'product_id',
                'name',
                'price',
                'stock_quantity',
                'category'
            ]
        }
    }
};

// =============================================================================
// TEMPLATE 4: CRM MODULE
// =============================================================================

const crmConfig = {
    moduleId: 'crm',
    backendUrl: 'http://localhost:5001',
    tables: {
        contacts: {
            containerId: 'contacts-table',
            apiEndpoint: '/api/crm/contacts',
            dataKey: 'contacts',
            expectedColumns: [
                'contact_id',
                'name',
                'email',
                'phone',
                'company',
                'status'
            ]
        },
        deals: {
            containerId: 'deals-table',
            apiEndpoint: '/api/crm/deals',
            dataKey: 'deals',
            expectedColumns: [
                'deal_id',
                'title',
                'value',
                'stage',
                'probability',
                'close_date'
            ]
        },
        tasks: {
            containerId: 'tasks-table',
            apiEndpoint: '/api/crm/tasks',
            dataKey: 'tasks',
            expectedColumns: [
                'task_id',
                'title',
                'due_date',
                'priority',
                'assigned_to',
                'status'
            ]
        }
    }
};

// =============================================================================
// TEMPLATE 5: ANALYTICS DASHBOARD
// =============================================================================

const analyticsConfig = {
    moduleId: 'analytics',
    backendUrl: 'http://localhost:5001',
    tables: {
        pageViews: {
            containerId: 'page-views-table',
            apiEndpoint: '/api/analytics/page-views',
            dataKey: 'data',
            expectedColumns: [
                'page_url',
                'views',
                'unique_visitors',
                'avg_time',
                'bounce_rate'
            ]
        },
        conversions: {
            containerId: 'conversions-table',
            apiEndpoint: '/api/analytics/conversions',
            dataKey: 'data',
            expectedColumns: [
                'date',
                'source',
                'conversions',
                'conversion_rate',
                'revenue'
            ]
        }
    }
};

// =============================================================================
// TEMPLATE 6: BULK OPERATIONS MODULE
// =============================================================================

const bulkOpsConfig = {
    moduleId: 'bulk-operations',
    backendUrl: 'http://localhost:5001',
    tables: {
        jobs: {
            containerId: 'bulk-jobs-table',
            apiEndpoint: '/api/bulk/jobs',
            dataKey: 'jobs',
            expectedColumns: [
                'job_id',
                'job_number',
                'client_name',
                'status',
                'created_date'
            ]
        },
        products: {
            containerId: 'bulk-products-table',
            apiEndpoint: '/api/bulk/products',
            dataKey: 'products',
            expectedColumns: [
                'product_id',
                'name',
                'quantity',
                'price',
                'job_id'
            ]
        }
    }
};

// =============================================================================
// BLANK TEMPLATE (Copy and Fill In)
// =============================================================================

const blankTemplate = {
    moduleId: 'YOUR-MODULE-ID',              // e.g., 'stock-management'
    backendUrl: 'http://localhost:5001',     // Your Flask backend URL
    timeout: 10000,                          // Test timeout in milliseconds
    verbose: true,                           // Enable debug logging
    tables: {
        tableName1: {                        // Unique key for this table
            containerId: 'TABLE-ID',         // DOM element ID (without #)
            apiEndpoint: '/api/YOUR-ENDPOINT', // API endpoint path
            method: 'GET',                   // HTTP method (GET or POST)
            dataKey: 'data',                 // Key containing data array in response
            expectedColumns: [               // Optional: Expected column names
                'column1',
                'column2',
                'column3'
            ]
            // For POST requests, add:
            // postData: { query: '...', params: {...} }
        },
        tableName2: {
            // Add more tables as needed
        }
    }
};

// =============================================================================
// USAGE EXAMPLES
// =============================================================================

// Example 1: Test Stock Management
async function testStockManagement() {
    const tester = new TabulatorTestFramework(stockManagementConfig);
    const result = await tester.runAllTests();

    if (result.success) {
        console.log('🎉 All tests passed!');
        tester.exportHTML('stock-management-report.html');
    } else {
        console.error(`❌ ${result.stats.failed} tests failed`);
        tester.exportJSON('stock-management-errors.json');
    }

    return result;
}

// Example 2: Test Single Category
async function testAPIsOnly() {
    const tester = new TabulatorTestFramework(stockManagementConfig);
    await tester.runAPITests();
}

// Example 3: Test Specific Table
async function testReorderTable() {
    const config = {
        moduleId: 'stock-management',
        backendUrl: 'http://localhost:5001',
        tables: {
            reorder: stockManagementConfig.tables.reorder
        }
    };

    const tester = new TabulatorTestFramework(config);
    await tester.runAllTests();
}

// Example 4: Quick Health Check
async function quickHealthCheck() {
    const tester = new TabulatorTestFramework({
        moduleId: 'any-module',
        backendUrl: 'http://localhost:5001',
        tables: {}
    });

    await tester.runHealthCheck();
}

// =============================================================================
// AI AGENT HELPER: AUTO-GENERATE CONFIG FROM MODULE
// =============================================================================

/**
 * Helper function for AI agents to generate config from module code
 * 
 * @param {string} moduleCode - The module's JavaScript code
 * @returns {Object} - Generated configuration object
 */
function generateConfigFromModule(moduleCode) {
    const config = {
        moduleId: '',
        backendUrl: '',
        tables: {}
    };

    // Extract module ID
    const moduleIdMatch = moduleCode.match(/class\s+(\w+)Module/);
    if (moduleIdMatch) {
        config.moduleId = moduleIdMatch[1].toLowerCase().replace(/([A-Z])/g, '-$1').slice(1);
    }

    // Extract backend URL
    const backendUrlMatch = moduleCode.match(/this\.backendUrl\s*=\s*['"]([^'"]+)['"]/);
    if (backendUrlMatch) {
        config.backendUrl = backendUrlMatch[1];
    }

    // Extract Tabulator instances
    const tabulatorMatches = moduleCode.matchAll(/new\s+Tabulator\(['"]#([^'"]+)['"],/g);
    for (const match of tabulatorMatches) {
        const containerId = match[1];
        const tableKey = containerId.replace(/-tabulator$/, '').replace(/^.*-/, '');

        config.tables[tableKey] = {
            containerId: containerId,
            apiEndpoint: '', // AI needs to find this
            dataKey: 'data'
        };
    }

    // Extract API endpoints (AI would need to match them to tables)
    const apiMatches = moduleCode.matchAll(/fetch\([`'"]([^`'"]+api[^`'"]+)[`'"]/g);
    for (const match of apiMatches) {
        console.log('Found API endpoint:', match[1]);
        // AI would need to associate this with correct table
    }

    return config;
}

// =============================================================================
// EXPORT FOR USE IN OTHER SCRIPTS
// =============================================================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        stockManagementConfig,
        singleTableConfig,
        ecommerceConfig,
        crmConfig,
        analyticsConfig,
        bulkOpsConfig,
        blankTemplate,
        generateConfigFromModule
    };
}

// =============================================================================
// GLOBAL EXPORT FOR BROWSER
// =============================================================================

if (typeof window !== 'undefined') {
    window.TabulatorTestConfigs = {
        stockManagement: stockManagementConfig,
        singleTable: singleTableConfig,
        ecommerce: ecommerceConfig,
        crm: crmConfig,
        analytics: analyticsConfig,
        bulkOps: bulkOpsConfig,
        blank: blankTemplate
    };

    console.log('✅ Tabulator Test Config Templates loaded');
    console.log('   Available: window.TabulatorTestConfigs');
}
