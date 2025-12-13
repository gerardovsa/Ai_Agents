/**
 * ============================================================
 * ACCOUNT SIDEBAR REALTIME - TESTING SCRIPT
 * ============================================================
 * Run these tests in browser console after deployment
 * Tests real-time connection monitoring and notifications
 * ============================================================
 */

// ============================================================
// TEST SETUP
// ============================================================

console.log('🧪 Starting Account Sidebar Realtime Tests...\n');

// Helper: Wait for a condition
const waitFor = (condition, timeout = 5000) => {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();
        const interval = setInterval(() => {
            if (condition()) {
                clearInterval(interval);
                resolve(true);
            } else if (Date.now() - startTime > timeout) {
                clearInterval(interval);
                reject(new Error('Timeout waiting for condition'));
            }
        }, 100);
    });
};

// Helper: Format test result
const testResult = (testName, passed, details = '') => {
    const icon = passed ? '✅' : '❌';
    console.log(`${icon} ${testName}`);
    if (details) console.log(`   ${details}`);
    return passed;
};

// ============================================================
// TEST 1: Verify Supabase Client Initialized
// ============================================================

async function test1_SupabaseClientInitialized() {
    console.log('\n📋 TEST 1: Supabase Client Initialization');
    console.log('─'.repeat(50));
    
    try {
        // Check if SupabaseConnectionManager exists
        const hasManager = typeof window.SupabaseConnectionManager !== 'undefined';
        testResult('SupabaseConnectionManager exists', hasManager);
        
        if (!hasManager) {
            console.error('❌ CRITICAL: SupabaseConnectionManager not loaded');
            return false;
        }
        
        // Get or create client
        const client = await window.SupabaseConnectionManager.getClient();
        const hasClient = !!client;
        testResult('Supabase client created', hasClient);
        
        if (hasClient) {
            console.log(`   Client URL: ${client.supabaseUrl}`);
        }
        
        // Check config loaded
        const configLoaded = window.SUPABASE_CONFIG_LOADED;
        testResult('Supabase config loaded', configLoaded);
        
        if (configLoaded) {
            console.log(`   URL: ${window.SUPABASE_URL}`);
            console.log(`   Key: ${window.SUPABASE_ANON_KEY?.substring(0, 20)}...`);
        }
        
        return hasManager && hasClient && configLoaded;
        
    } catch (error) {
        console.error('❌ TEST 1 FAILED:', error);
        return false;
    }
}

// ============================================================
// TEST 2: Verify User Authentication
// ============================================================

function test2_UserAuthentication() {
    console.log('\n📋 TEST 2: User Authentication');
    console.log('─'.repeat(50));
    
    const hasUserAuth = typeof window.UserAuth !== 'undefined';
    testResult('UserAuth object exists', hasUserAuth);
    
    if (!hasUserAuth) {
        console.error('❌ CRITICAL: User not authenticated');
        return false;
    }
    
    const hasUser = !!window.UserAuth.user;
    testResult('User object exists', hasUser);
    
    if (hasUser) {
        const userId = window.UserAuth.user.user_id;
        const username = window.UserAuth.user.username;
        testResult('User ID exists', !!userId, `User ID: ${userId}`);
        testResult('Username exists', !!username, `Username: ${username}`);
        
        console.log(`   User: ${username} (ID: ${userId})`);
        return !!userId;
    }
    
    return false;
}

// ============================================================
// TEST 3: Verify AccountSidebar Exists
// ============================================================

function test3_AccountSidebarExists() {
    console.log('\n📋 TEST 3: AccountSidebar Object');
    console.log('─'.repeat(50));
    
    const hasSidebar = typeof window.AccountSidebar !== 'undefined';
    testResult('AccountSidebar object exists', hasSidebar);
    
    if (!hasSidebar) {
        console.error('❌ CRITICAL: AccountSidebar not loaded');
        return false;
    }
    
    // Check for new methods
    const hasSubscribe = typeof AccountSidebar.subscribeToConnectionChanges === 'function';
    testResult('subscribeToConnectionChanges() exists', hasSubscribe);
    
    const hasUnsubscribe = typeof AccountSidebar.unsubscribeFromConnectionChanges === 'function';
    testResult('unsubscribeFromConnectionChanges() exists', hasUnsubscribe);
    
    const hasHandleChange = typeof AccountSidebar.handleConnectionChange === 'function';
    testResult('handleConnectionChange() exists', hasHandleChange);
    
    const hasUpdateDot = typeof AccountSidebar.updateStatusDot === 'function';
    testResult('updateStatusDot() exists', hasUpdateDot);
    
    const hasNotification = typeof AccountSidebar.showNotification === 'function';
    testResult('showNotification() exists', hasNotification);
    
    return hasSubscribe && hasUnsubscribe && hasHandleChange && hasUpdateDot && hasNotification;
}

// ============================================================
// TEST 4: Open Sidebar and Subscribe to Realtime
// ============================================================

async function test4_OpenSidebarAndSubscribe() {
    console.log('\n📋 TEST 4: Open Sidebar & Subscribe to Realtime');
    console.log('─'.repeat(50));
    
    try {
        // Open sidebar
        console.log('   Opening sidebar...');
        await AccountSidebar.toggleSidebar();
        
        // Wait for sidebar to open
        await waitFor(() => {
            const sidebar = document.getElementById('account-sidebar');
            return sidebar && !sidebar.classList.contains('collapsed');
        }, 3000);
        
        const sidebarOpen = !document.getElementById('account-sidebar')?.classList.contains('collapsed');
        testResult('Sidebar opened', sidebarOpen);
        
        // Wait for subscription to initialize
        await waitFor(() => !!AccountSidebar.realtimeChannel, 5000);
        
        const hasChannel = !!AccountSidebar.realtimeChannel;
        testResult('Realtime channel created', hasChannel);
        
        if (hasChannel) {
            console.log(`   Channel: ${AccountSidebar.realtimeChannel.topic}`);
            console.log(`   State: ${AccountSidebar.realtimeChannel.state}`);
        }
        
        // Check channel state
        const isSubscribed = AccountSidebar.realtimeChannel?.state === 'joined';
        testResult('Channel subscribed', isSubscribed);
        
        return sidebarOpen && hasChannel && isSubscribed;
        
    } catch (error) {
        console.error('❌ TEST 4 FAILED:', error);
        return false;
    }
}

// ============================================================
// TEST 5: Verify Connection Handlers
// ============================================================

function test5_ConnectionHandlers() {
    console.log('\n📋 TEST 5: Connection Event Handlers');
    console.log('─'.repeat(50));
    
    // Test INSERT handler
    const hasInsert = typeof AccountSidebar.handleConnectionInsert === 'function';
    testResult('handleConnectionInsert() exists', hasInsert);
    
    // Test UPDATE handler
    const hasUpdate = typeof AccountSidebar.handleConnectionUpdate === 'function';
    testResult('handleConnectionUpdate() exists', hasUpdate);
    
    // Test DELETE handler
    const hasDelete = typeof AccountSidebar.handleConnectionDelete === 'function';
    testResult('handleConnectionDelete() exists', hasDelete);
    
    // Test platform name formatter
    const hasFormatter = typeof AccountSidebar.formatPlatformName === 'function';
    testResult('formatPlatformName() exists', hasFormatter);
    
    if (hasFormatter) {
        const googleName = AccountSidebar.formatPlatformName('google');
        testResult('Format "google" → "Google Workspace"', googleName === 'Google Workspace');
        
        const msName = AccountSidebar.formatPlatformName('microsoft');
        testResult('Format "microsoft" → "Microsoft 365"', msName === 'Microsoft 365');
    }
    
    return hasInsert && hasUpdate && hasDelete && hasFormatter;
}

// ============================================================
// TEST 6: Simulate Realtime Event (INSERT)
// ============================================================

function test6_SimulateInsertEvent() {
    console.log('\n📋 TEST 6: Simulate Connection INSERT Event');
    console.log('─'.repeat(50));
    
    try {
        const mockPayload = {
            eventType: 'INSERT',
            new: {
                id: 999,
                user_id: window.UserAuth.user.user_id,
                platform: 'github',
                credential_type: 'oauth',
                is_active: true,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            },
            old: null
        };
        
        console.log('   Triggering INSERT event for GitHub...');
        AccountSidebar.handleConnectionChange(mockPayload);
        
        testResult('INSERT event handled', true, 'Check console for notification');
        
        return true;
        
    } catch (error) {
        console.error('❌ TEST 6 FAILED:', error);
        return false;
    }
}

// ============================================================
// TEST 7: Simulate Realtime Event (UPDATE - Expiry)
// ============================================================

function test7_SimulateExpiryEvent() {
    console.log('\n📋 TEST 7: Simulate Connection EXPIRY Event');
    console.log('─'.repeat(50));
    
    try {
        const mockPayload = {
            eventType: 'UPDATE',
            old: {
                id: 1,
                user_id: window.UserAuth.user.user_id,
                platform: 'google',
                credential_type: 'oauth',
                is_active: true, // WAS active
                updated_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() // 2 hours ago
            },
            new: {
                id: 1,
                user_id: window.UserAuth.user.user_id,
                platform: 'google',
                credential_type: 'oauth',
                is_active: false, // NOW inactive
                updated_at: new Date().toISOString()
            }
        };
        
        console.log('   Triggering EXPIRY event for Google...');
        AccountSidebar.handleConnectionChange(mockPayload);
        
        testResult('EXPIRY event handled', true, 'Check console for warning notification');
        
        return true;
        
    } catch (error) {
        console.error('❌ TEST 7 FAILED:', error);
        return false;
    }
}

// ============================================================
// TEST 8: Simulate Realtime Event (UPDATE - Re-activation)
// ============================================================

function test8_SimulateReactivationEvent() {
    console.log('\n📋 TEST 8: Simulate Connection RE-ACTIVATION Event');
    console.log('─'.repeat(50));
    
    try {
        const mockPayload = {
            eventType: 'UPDATE',
            old: {
                id: 1,
                user_id: window.UserAuth.user.user_id,
                platform: 'google',
                credential_type: 'oauth',
                is_active: false, // WAS inactive
                updated_at: new Date(Date.now() - 10 * 1000).toISOString() // 10 seconds ago
            },
            new: {
                id: 1,
                user_id: window.UserAuth.user.user_id,
                platform: 'google',
                credential_type: 'oauth',
                is_active: true, // NOW active
                updated_at: new Date().toISOString()
            }
        };
        
        console.log('   Triggering RE-ACTIVATION event for Google...');
        AccountSidebar.handleConnectionChange(mockPayload);
        
        testResult('RE-ACTIVATION event handled', true, 'Check console for success notification');
        
        return true;
        
    } catch (error) {
        console.error('❌ TEST 8 FAILED:', error);
        return false;
    }
}

// ============================================================
// TEST 9: Simulate Realtime Event (DELETE)
// ============================================================

function test9_SimulateDeleteEvent() {
    console.log('\n📋 TEST 9: Simulate Connection DELETE Event');
    console.log('─'.repeat(50));
    
    try {
        const mockPayload = {
            eventType: 'DELETE',
            old: {
                id: 999,
                user_id: window.UserAuth.user.user_id,
                platform: 'github',
                credential_type: 'oauth',
                is_active: true,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            },
            new: null
        };
        
        console.log('   Triggering DELETE event for GitHub...');
        AccountSidebar.handleConnectionChange(mockPayload);
        
        testResult('DELETE event handled', true, 'Check console for info notification');
        
        return true;
        
    } catch (error) {
        console.error('❌ TEST 9 FAILED:', error);
        return false;
    }
}

// ============================================================
// TEST 10: Close Sidebar and Unsubscribe
// ============================================================

async function test10_CloseSidebarAndUnsubscribe() {
    console.log('\n📋 TEST 10: Close Sidebar & Unsubscribe');
    console.log('─'.repeat(50));
    
    try {
        console.log('   Closing sidebar...');
        await AccountSidebar.toggleSidebar();
        
        // Wait for sidebar to close
        await waitFor(() => {
            const sidebar = document.getElementById('account-sidebar');
            return sidebar && sidebar.classList.contains('collapsed');
        }, 3000);
        
        const sidebarClosed = document.getElementById('account-sidebar')?.classList.contains('collapsed');
        testResult('Sidebar closed', sidebarClosed);
        
        // Check channel removed
        const channelRemoved = !AccountSidebar.realtimeChannel;
        testResult('Realtime channel removed', channelRemoved);
        
        return sidebarClosed && channelRemoved;
        
    } catch (error) {
        console.error('❌ TEST 10 FAILED:', error);
        return false;
    }
}

// ============================================================
// RUN ALL TESTS
// ============================================================

async function runAllTests() {
    console.log('\n');
    console.log('═'.repeat(60));
    console.log('🧪 ACCOUNT SIDEBAR REALTIME - COMPREHENSIVE TEST SUITE');
    console.log('═'.repeat(60));
    
    const results = {
        passed: 0,
        failed: 0,
        tests: []
    };
    
    // Test 1: Supabase Client
    const test1 = await test1_SupabaseClientInitialized();
    results.tests.push({ name: 'Test 1: Supabase Client', passed: test1 });
    test1 ? results.passed++ : results.failed++;
    
    // Test 2: User Authentication
    const test2 = test2_UserAuthentication();
    results.tests.push({ name: 'Test 2: User Authentication', passed: test2 });
    test2 ? results.passed++ : results.failed++;
    
    // Test 3: AccountSidebar Object
    const test3 = test3_AccountSidebarExists();
    results.tests.push({ name: 'Test 3: AccountSidebar Object', passed: test3 });
    test3 ? results.passed++ : results.failed++;
    
    // Test 4: Open Sidebar & Subscribe
    const test4 = await test4_OpenSidebarAndSubscribe();
    results.tests.push({ name: 'Test 4: Open & Subscribe', passed: test4 });
    test4 ? results.passed++ : results.failed++;
    
    // Test 5: Connection Handlers
    const test5 = test5_ConnectionHandlers();
    results.tests.push({ name: 'Test 5: Event Handlers', passed: test5 });
    test5 ? results.passed++ : results.failed++;
    
    // Test 6: Simulate INSERT
    const test6 = test6_SimulateInsertEvent();
    results.tests.push({ name: 'Test 6: INSERT Event', passed: test6 });
    test6 ? results.passed++ : results.failed++;
    
    // Test 7: Simulate EXPIRY
    const test7 = test7_SimulateExpiryEvent();
    results.tests.push({ name: 'Test 7: EXPIRY Event', passed: test7 });
    test7 ? results.passed++ : results.failed++;
    
    // Test 8: Simulate RE-ACTIVATION
    const test8 = test8_SimulateReactivationEvent();
    results.tests.push({ name: 'Test 8: RE-ACTIVATION Event', passed: test8 });
    test8 ? results.passed++ : results.failed++;
    
    // Test 9: Simulate DELETE
    const test9 = test9_SimulateDeleteEvent();
    results.tests.push({ name: 'Test 9: DELETE Event', passed: test9 });
    test9 ? results.passed++ : results.failed++;
    
    // Test 10: Close & Unsubscribe
    const test10 = await test10_CloseSidebarAndUnsubscribe();
    results.tests.push({ name: 'Test 10: Close & Unsubscribe', passed: test10 });
    test10 ? results.passed++ : results.failed++;
    
    // Print summary
    console.log('\n');
    console.log('═'.repeat(60));
    console.log('📊 TEST SUMMARY');
    console.log('═'.repeat(60));
    console.log(`Total Tests: ${results.tests.length}`);
    console.log(`✅ Passed: ${results.passed}`);
    console.log(`❌ Failed: ${results.failed}`);
    console.log(`Success Rate: ${((results.passed / results.tests.length) * 100).toFixed(1)}%`);
    console.log('');
    
    results.tests.forEach((test, index) => {
        const icon = test.passed ? '✅' : '❌';
        console.log(`${icon} ${test.name}`);
    });
    
    console.log('═'.repeat(60));
    
    if (results.failed === 0) {
        console.log('🎉 ALL TESTS PASSED! Realtime monitoring is working perfectly.');
    } else {
        console.log('⚠️ Some tests failed. Check the detailed output above.');
    }
    
    return results;
}

// ============================================================
// QUICK START
// ============================================================

console.log('\n📖 QUICK START GUIDE:');
console.log('─'.repeat(60));
console.log('1. Make sure you are logged in to the platform');
console.log('2. Run: await runAllTests()');
console.log('3. Watch the console for detailed test results');
console.log('4. All tests should pass if deployment was successful');
console.log('');
console.log('💡 TIP: You can also run individual tests:');
console.log('   - await test1_SupabaseClientInitialized()');
console.log('   - await test4_OpenSidebarAndSubscribe()');
console.log('   - test6_SimulateInsertEvent()');
console.log('');
console.log('🚀 Ready? Run: await runAllTests()');
console.log('═'.repeat(60));
console.log('');

// Export functions for manual testing
window.AccountSidebarTests = {
    runAllTests,
    test1_SupabaseClientInitialized,
    test2_UserAuthentication,
    test3_AccountSidebarExists,
    test4_OpenSidebarAndSubscribe,
    test5_ConnectionHandlers,
    test6_SimulateInsertEvent,
    test7_SimulateExpiryEvent,
    test8_SimulateReactivationEvent,
    test9_SimulateDeleteEvent,
    test10_CloseSidebarAndUnsubscribe
};
