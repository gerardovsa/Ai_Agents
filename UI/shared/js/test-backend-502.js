/**
 * Manual Test Script for 502 Error Handling
 * 
 * HOW TO USE:
 * 1. Open browser DevTools console
 * 2. Copy-paste this entire file into console
 * 3. Run: testBackendAvailability()
 * 4. Observe: Retry logic and error handling
 */

async function testBackendAvailability() {
    const baseUrl = window.location.origin; // Use current domain
    const token = localStorage.getItem('authToken');

    console.log('🧪 [TEST] Starting backend availability test...');
    console.log(`   Base URL: ${baseUrl}`);
    console.log(`   Auth Token: ${token ? 'Present' : 'MISSING'}`);

    const endpoints = [
        '/api/auth/team-ids',
        '/api/auth/profile',
        '/api/modules/list',
        '/api/health'
    ];

    const results = await Promise.allSettled(
        endpoints.map(async (endpoint) => {
            const url = `${baseUrl}${endpoint}`;
            console.log(`🔍 Testing: ${endpoint}`);

            try {
                const response = await fetch(url, {
                    headers: token ? { 'Authorization': `Bearer ${token}` } : {}
                });

                const contentType = response.headers.get('content-type');
                const isJson = contentType?.includes('application/json');

                let body = null;
                if (isJson) {
                    body = await response.json();
                } else {
                    const text = await response.text();
                    body = text.substring(0, 200); // First 200 chars
                }

                return {
                    endpoint,
                    status: response.status,
                    ok: response.ok,
                    contentType,
                    isJson,
                    body
                };
            } catch (error) {
                return {
                    endpoint,
                    status: 'ERROR',
                    ok: false,
                    error: error.message
                };
            }
        })
    );

    console.log('\n📊 [TEST RESULTS]');
    console.log('='.repeat(80));

    results.forEach((result, index) => {
        const endpoint = endpoints[index];

        if (result.status === 'fulfilled') {
            const data = result.value;
            const icon = data.ok ? '✅' : '❌';
            const status = data.status === 'ERROR' ? 'FETCH_FAILED' : data.status;

            console.log(`\n${icon} ${endpoint}`);
            console.log(`   Status: ${status}`);
            console.log(`   Content-Type: ${data.contentType || 'N/A'}`);

            if (data.error) {
                console.log(`   Error: ${data.error}`);
            }

            if (data.body) {
                if (typeof data.body === 'object') {
                    console.log('   Response:', data.body);
                } else {
                    console.log(`   Body Preview: ${data.body}...`);
                }
            }
        } else {
            console.log(`\n❌ ${endpoint}`);
            console.log(`   Promise Rejected: ${result.reason}`);
        }
    });

    console.log('\n' + '='.repeat(80));

    // Summary
    const successful = results.filter(r =>
        r.status === 'fulfilled' && r.value.ok
    ).length;
    const failed = endpoints.length - successful;

    console.log(`\n📈 Summary: ${successful}/${endpoints.length} endpoints healthy`);

    if (failed > 0) {
        console.warn(`⚠️  ${failed} endpoint(s) failing - backend may be unavailable`);
    } else {
        console.log('✅ All endpoints responding correctly');
    }

    return results;
}

// Test with retry logic
async function testRetryLogic() {
    console.log('🧪 [TEST] Testing retry logic...');

    if (!window.BackendHealthCheck) {
        console.error('❌ BackendHealthCheck not loaded!');
        console.log('   Load it first: <script src="/shared/js/backend-health-check.js"></script>');
        return;
    }

    console.log('✅ BackendHealthCheck available');

    // Test 1: Health check with retries
    console.log('\n🔄 Test 1: Waiting for backend (max 10 retries)...');
    const isHealthy = await window.BackendHealthCheck.waitForBackend((attempt, max) => {
        console.log(`   Attempt ${attempt}/${max}...`);
    });

    if (isHealthy) {
        console.log('✅ Backend is healthy');
    } else {
        console.error('❌ Backend unavailable after max retries');
    }

    // Test 2: Fetch with retry on 502
    console.log('\n🔄 Test 2: Fetch with automatic retry...');
    try {
        const response = await window.BackendHealthCheck.fetchWithRetry('/api/health', {}, 3);
        console.log('✅ Fetch successful:', response);
    } catch (error) {
        console.error('❌ Fetch failed:', error.message);
    }
}

// Test defensive API wrappers
async function testDefensiveAPI() {
    console.log('🧪 [TEST] Testing DefensiveAPI wrappers...');

    if (!window.DefensiveAPI) {
        console.error('❌ DefensiveAPI not loaded!');
        console.log('   Load it first: <script src="/shared/js/defensive-api.js"></script>');
        return;
    }

    console.log('✅ DefensiveAPI available');

    // Test 1: Load team IDs
    console.log('\n📋 Test 1: Loading Team IDs...');
    const teamResult = await window.DefensiveAPI.loadTeamIds({ retries: 3 });
    if (teamResult.success) {
        console.log('✅ Team IDs loaded:', teamResult.data);
    } else {
        console.warn('⚠️  Team IDs fallback used:', teamResult.error);
    }

    // Test 2: Load profile
    console.log('\n👤 Test 2: Loading Profile...');
    const profileResult = await window.DefensiveAPI.loadProfile({ retries: 3 });
    if (profileResult.success) {
        console.log('✅ Profile loaded:', profileResult.data);
    } else {
        console.warn('⚠️  Profile fallback used:', profileResult.error);
    }

    // Test 3: Load modules
    console.log('\n📦 Test 3: Loading Modules...');
    const moduleResult = await window.DefensiveAPI.loadModules({ retries: 3 });
    if (moduleResult.success) {
        console.log('✅ Modules loaded:', moduleResult.data.count, 'modules');
    } else {
        console.warn('⚠️  Modules fallback used:', moduleResult.error);
    }
}

// Run all tests
async function runAllTests() {
    console.log('🚀 RUNNING ALL 502 ERROR HANDLING TESTS\n');

    await testBackendAvailability();
    console.log('\n' + '='.repeat(80) + '\n');

    await testRetryLogic();
    console.log('\n' + '='.repeat(80) + '\n');

    await testDefensiveAPI();

    console.log('\n✅ All tests complete!');
}

// Export for console use
window.testBackend502 = {
    testBackendAvailability,
    testRetryLogic,
    testDefensiveAPI,
    runAllTests
};

console.log('✅ Test suite loaded. Run: testBackend502.runAllTests()');
