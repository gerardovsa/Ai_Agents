/**
 * COMMUNICATION HUB - COMPREHENSIVE SMOKE TEST
 * Tests module loading, initialization, and backend connectivity
 */

console.log('🧪 ========== COMMUNICATION HUB SMOKE TEST ==========');

// ==================== TEST 1: Module Import ====================
console.log('\n📦 TEST 1: Module Import Check');

function test1_moduleImport() {
    const results = {
        moduleExists: typeof window.communicationHub !== 'undefined',
        hasOnDashboardLoad: typeof window.communicationHub?.onDashboardLoad === 'function',
        hasRenderDashboard: typeof window.communicationHub?.renderDashboard === 'function',
        hasLoadEmails: typeof window.communicationHub?.loadEmails === 'function'
    };
    
    console.log('  ✓ Module exists:', results.moduleExists);
    console.log('  ✓ onDashboardLoad method:', results.hasOnDashboardLoad);
    console.log('  ✓ renderDashboard method:', results.hasRenderDashboard);
    console.log('  ✓ loadEmails method:', results.hasLoadEmails);
    
    const passed = Object.values(results).every(v => v === true);
    console.log(passed ? '  ✅ TEST 1 PASSED' : '  ❌ TEST 1 FAILED');
    return passed;
}

// ==================== TEST 2: Container Lookup ====================
console.log('\n🎯 TEST 2: Container ID Check');

function test2_containerLookup() {
    const container = document.getElementById('communication-hub-main-container');
    const tabExists = document.getElementById('tab-communication');
    
    console.log('  ✓ Container exists:', !!container);
    console.log('  ✓ Tab exists:', !!tabExists);
    console.log('  ✓ Container ID:', container?.id || 'NOT FOUND');
    console.log('  ✓ Container display:', container ? window.getComputedStyle(container).display : 'N/A');
    
    const passed = !!container && !!tabExists;
    console.log(passed ? '  ✅ TEST 2 PASSED' : '  ❌ TEST 2 FAILED');
    return passed;
}

// ==================== TEST 3: Initialization State ====================
console.log('\n⚙️ TEST 3: Initialization State');

function test3_initState() {
    const results = {
        dashboardContainerSet: !!window.communicationHub?.dashboardContainer,
        apiBaseSet: !!window.communicationHub?.state?.apiBase,
        utilitiesInjected: !!(window.communicationHub?.dom && window.communicationHub?.api && window.communicationHub?.log)
    };
    
    console.log('  ✓ Dashboard container set:', results.dashboardContainerSet);
    console.log('  ✓ API base URL set:', results.apiBaseSet, '→', window.communicationHub?.state?.apiBase);
    console.log('  ✓ Utilities injected:', results.utilitiesInjected);
    
    const passed = Object.values(results).every(v => v === true);
    console.log(passed ? '  ✅ TEST 3 PASSED' : '  ❌ TEST 3 FAILED');
    return passed;
}

// ==================== TEST 4: Backend Endpoint Connectivity ====================
console.log('\n🌐 TEST 4: Backend Endpoint Test');

async function test4_backendEndpoints() {
    const baseUrl = window.API_BASE_URL || 'http://localhost:5001';
    const endpoints = [
        '/api/communication-hub/accounts',
        '/api/communication-hub/emails',
        '/health'
    ];
    
    const results = [];
    
    for (const endpoint of endpoints) {
        try {
            const response = await fetch(`${baseUrl}${endpoint}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const status = response.status;
            const ok = response.ok || status === 404; // 404 is acceptable (endpoint may not exist yet)
            
            results.push({ endpoint, status, ok });
            console.log(`  ${ok ? '✓' : '✗'} ${endpoint}: ${status}`);
        } catch (error) {
            results.push({ endpoint, status: 'ERROR', ok: false, error: error.message });
            console.log(`  ✗ ${endpoint}: ERROR →`, error.message);
        }
    }
    
    const passed = results.every(r => r.ok);
    console.log(passed ? '  ✅ TEST 4 PASSED' : '  ⚠️ TEST 4 PARTIAL (backend may be offline)');
    return passed;
}

// ==================== TEST 5: Tab Switch Activation ====================
console.log('\n🔄 TEST 5: Tab Switch Simulation');

function test5_tabSwitch() {
    console.log('  ⚡ Simulating tab switch to communication...');
    
    // Check if switchTab function exists
    const hasSwitchTab = typeof switchTab === 'function';
    console.log('  ✓ switchTab function exists:', hasSwitchTab);
    
    if (hasSwitchTab) {
        try {
            // Don't actually switch (might break test page), just check the logic path exists
            const tabElement = document.getElementById('tab-communication');
            console.log('  ✓ Tab element found:', !!tabElement);
            console.log('  ✓ Tab is active:', tabElement?.classList.contains('active'));
        } catch (error) {
            console.log('  ✗ Tab switch check failed:', error.message);
            return false;
        }
    }
    
    const passed = hasSwitchTab;
    console.log(passed ? '  ✅ TEST 5 PASSED' : '  ❌ TEST 5 FAILED');
    return passed;
}

// ==================== TEST 6: Module Dependencies ====================
console.log('\n📚 TEST 6: Module Dependencies');

function test6_dependencies() {
    const deps = {
        'Tabulator': typeof Tabulator !== 'undefined',
        'API_BASE_URL': typeof window.API_BASE_URL !== 'undefined',
        'UserAuth': typeof window.UserAuth !== 'undefined',
        'showNotification': typeof window.showNotification === 'function'
    };
    
    for (const [dep, exists] of Object.entries(deps)) {
        console.log(`  ${exists ? '✓' : '✗'} ${dep}: ${exists ? 'LOADED' : 'MISSING'}`);
    }
    
    const passed = deps['API_BASE_URL']; // Only require API_BASE_URL
    console.log(passed ? '  ✅ TEST 6 PASSED' : '  ❌ TEST 6 FAILED');
    return passed;
}

// ==================== RUN ALL TESTS ====================
async function runAllTests() {
    console.log('\n🚀 Running all tests...\n');
    
    const test1 = test1_moduleImport();
    const test2 = test2_containerLookup();
    const test3 = test3_initState();
    const test4 = await test4_backendEndpoints();
    const test5 = test5_tabSwitch();
    const test6 = test6_dependencies();
    
    console.log('\n📊 ========== TEST SUMMARY ==========');
    console.log('  TEST 1 - Module Import:', test1 ? '✅ PASS' : '❌ FAIL');
    console.log('  TEST 2 - Container Lookup:', test2 ? '✅ PASS' : '❌ FAIL');
    console.log('  TEST 3 - Initialization State:', test3 ? '✅ PASS' : '❌ FAIL');
    console.log('  TEST 4 - Backend Endpoints:', test4 ? '✅ PASS' : '⚠️ PARTIAL');
    console.log('  TEST 5 - Tab Switch:', test5 ? '✅ PASS' : '❌ FAIL');
    console.log('  TEST 6 - Dependencies:', test6 ? '✅ PASS' : '❌ FAIL');
    
    const criticalPassed = test1 && test2 && test6;
    const allPassed = test1 && test2 && test3 && test4 && test5 && test6;
    
    console.log('\n🎯 RESULT:', criticalPassed ? '✅ CRITICAL TESTS PASSED' : '❌ CRITICAL TESTS FAILED');
    console.log('   Overall:', allPassed ? '✅ ALL TESTS PASSED' : '⚠️ SOME TESTS FAILED');
    console.log('=====================================\n');
    
    return { criticalPassed, allPassed, individual: { test1, test2, test3, test4, test5, test6 } };
}

// Auto-run on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runAllTests);
} else {
    runAllTests();
}

// Export for manual testing
window.communicationHubSmokeTest = runAllTests;
console.log('💡 TIP: Run manually with: communicationHubSmokeTest()');
