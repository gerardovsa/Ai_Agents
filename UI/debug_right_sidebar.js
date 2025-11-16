/**
 * RIGHT SIDEBAR BUTTONS DEBUGGING SCRIPT
 * 
 * This script tests all right sidebar buttons and provides detailed diagnostics.
 * Copy and paste this entire script into the browser console.
 * 
 * Usage:
 *   1. Open browser console (F12)
 *   2. Paste this entire script
 *   3. Run: testAllButtons()
 *   4. Or test individual buttons: testAIPrimeButton(), testUserProfileButton(), etc.
 */

console.log('%c=== RIGHT SIDEBAR BUTTON DEBUGGER ===', 'color: #58a6ff; font-size: 16px; font-weight: bold;');
console.log('Available commands:');
console.log('  testAllButtons()          - Test all buttons');
console.log('  testAIPrimeButton()       - Test AI Prime toggle');
console.log('  testUserProfileButton()   - Test User Profile');
console.log('  testQuickActionsButton()  - Test Quick Actions');
console.log('  testThreadsButton()       - Test Thread History');
console.log('  testThemeButton()         - Test Theme Toggle');
console.log('  forceAIPrime()            - Force AI Prime toggle');
console.log('  forceUserProfile()        - Force User Profile open');
console.log('  fixAllButtons()           - Apply fixes to all buttons');
console.log('');

// ============================================================
// BUTTON DIAGNOSTICS
// ============================================================

window.testAIPrimeButton = function() {
    console.log('\n%c🤖 TESTING AI PRIME TOGGLE BUTTON', 'color: #58a6ff; font-size: 14px; font-weight: bold;');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    const btn = document.getElementById('ai-prime-toggle-btn');
    const panel = document.getElementById('ai-chat-panel');
    const wrapper = document.getElementById('main-content-wrapper');
    
    console.log('1. Button Element:', btn ? '✅ Found' : '❌ Not Found', btn);
    console.log('2. Chat Panel:', panel ? '✅ Found' : '❌ Not Found', panel);
    console.log('3. Wrapper:', wrapper ? '✅ Found' : '❌ Not Found', wrapper);
    
    if (btn) {
        const listeners = getEventListeners(btn);
        console.log('4. Event Listeners:', listeners);
        console.log('   - Click listeners:', listeners.click ? listeners.click.length : 0);
        console.log('5. Button Active State:', btn.classList.contains('active'));
    }
    
    if (panel) {
        console.log('6. Panel Display:', window.getComputedStyle(panel).display);
        console.log('7. Panel Visibility:', window.getComputedStyle(panel).visibility);
    }
    
    if (wrapper) {
        console.log('8. Wrapper Classes:', wrapper.className);
        console.log('9. Chat Collapsed:', wrapper.classList.contains('chat-collapsed'));
    }
    
    console.log('10. AppState.chatOpen:', typeof AppState !== 'undefined' ? AppState.chatOpen : 'AppState not defined');
    console.log('11. Initialization Flag:', window._rightSidebarInitialized);
    
    console.log('\n📋 RECOMMENDATIONS:');
    if (!btn) console.log('   ❌ Button not found - check HTML');
    if (btn && getEventListeners(btn).click?.length === 0) console.log('   ❌ No click listeners - button not initialized');
    if (btn && getEventListeners(btn).click?.length > 1) console.log('   ⚠️  Multiple click listeners detected - possible conflict');
    if (!panel) console.log('   ❌ Chat panel not found - check HTML');
    if (!wrapper) console.log('   ❌ Wrapper not found - check HTML');
    
    return { btn, panel, wrapper, hasListeners: btn ? getEventListeners(btn).click?.length > 0 : false };
};

window.testUserProfileButton = function() {
    console.log('\n%c👤 TESTING USER PROFILE BUTTON', 'color: #58a6ff; font-size: 14px; font-weight: bold;');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    const btnSidebar = document.getElementById('userProfileBtn-sidebar');
    const btnHeader = document.getElementById('userProfileBtn');
    const menu = document.getElementById('userDropdownMenu');
    const container = document.getElementById('userProfileContainer');
    
    console.log('1. Sidebar Button:', btnSidebar ? '✅ Found' : '❌ Not Found', btnSidebar);
    console.log('2. Header Button:', btnHeader ? '✅ Found' : '❌ Not Found', btnHeader);
    console.log('3. Dropdown Menu:', menu ? '✅ Found' : '❌ Not Found', menu);
    console.log('4. Profile Container:', container ? '✅ Found' : '❌ Not Found', container);
    
    if (container) {
        console.log('5. Container Display:', window.getComputedStyle(container).display);
        console.log('6. Container Visibility:', window.getComputedStyle(container).visibility);
    }
    
    if (menu) {
        console.log('7. Menu Active State:', menu.classList.contains('active'));
        console.log('8. Menu Display:', window.getComputedStyle(menu).display);
    }
    
    if (btnSidebar) {
        console.log('9. Sidebar Button onclick:', btnSidebar.onclick ? '✅ Has onclick' : '❌ No onclick');
        console.log('10. Sidebar Button Active:', btnSidebar.classList.contains('active'));
    }
    
    if (btnHeader) {
        console.log('11. Header Button onclick:', btnHeader.onclick ? '✅ Has onclick' : '❌ No onclick');
        console.log('12. Header Button Active:', btnHeader.classList.contains('active'));
    }
    
    console.log('13. toggleUserMenu function:', typeof toggleUserMenu !== 'undefined' ? '✅ Defined' : '❌ Not defined');
    
    console.log('\n📋 RECOMMENDATIONS:');
    if (!btnSidebar) console.log('   ❌ Sidebar button not found - check HTML');
    if (!btnHeader) console.log('   ❌ Header button not found - check HTML');
    if (!menu) console.log('   ❌ Dropdown menu not found - check HTML');
    if (container && window.getComputedStyle(container).display === 'none') {
        console.log('   ⚠️  Container is hidden - this is the issue!');
    }
    if (typeof toggleUserMenu === 'undefined') console.log('   ❌ toggleUserMenu function not defined');
    
    return { btnSidebar, btnHeader, menu, container, hasFunction: typeof toggleUserMenu !== 'undefined' };
};

window.testQuickActionsButton = function() {
    console.log('\n%c⚡ TESTING QUICK ACTIONS BUTTON', 'color: #58a6ff; font-size: 14px; font-weight: bold;');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    const btn = document.getElementById('quick-actions-btn');
    const promptSidebar = document.getElementById('prompt-sidebar');
    
    console.log('1. Button Element:', btn ? '✅ Found' : '❌ Not Found', btn);
    console.log('2. Prompt Sidebar:', promptSidebar ? '✅ Found' : '❌ Not Found', promptSidebar);
    
    if (btn) {
        const listeners = getEventListeners(btn);
        console.log('3. Event Listeners:', listeners);
        console.log('   - Click listeners:', listeners.click ? listeners.click.length : 0);
        console.log('4. Button Active State:', btn.classList.contains('active'));
    }
    
    if (promptSidebar) {
        console.log('5. Sidebar Classes:', promptSidebar.className);
        console.log('6. Sidebar Show State:', promptSidebar.classList.contains('show'));
        console.log('7. Sidebar Position:', window.getComputedStyle(promptSidebar).right);
        console.log('8. Sidebar Display:', window.getComputedStyle(promptSidebar).display);
    }
    
    console.log('\n📋 RECOMMENDATIONS:');
    if (!btn) console.log('   ❌ Button not found - check HTML');
    if (!promptSidebar) console.log('   ❌ Prompt sidebar not found - check if prompt-library.js loaded');
    if (btn && getEventListeners(btn).click?.length === 0) console.log('   ❌ No click listeners - button not initialized');
    
    return { btn, promptSidebar, hasListeners: btn ? getEventListeners(btn).click?.length > 0 : false };
};

window.testThreadsButton = function() {
    console.log('\n%c💬 TESTING THREADS BUTTON', 'color: #58a6ff; font-size: 14px; font-weight: bold;');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    const btn = document.getElementById('threads-btn');
    const menu = document.getElementById('thread-menu');
    
    console.log('1. Button Element:', btn ? '✅ Found' : '❌ Not Found', btn);
    console.log('2. Thread Menu:', menu ? '✅ Found' : '❌ Not Found', menu);
    
    if (btn) {
        const listeners = getEventListeners(btn);
        console.log('3. Event Listeners:', listeners);
        console.log('   - Click listeners:', listeners.click ? listeners.click.length : 0);
        console.log('4. Button Active State:', btn.classList.contains('active'));
    }
    
    if (menu) {
        console.log('5. Menu Active State:', menu.classList.contains('active'));
        console.log('6. Menu Position:', window.getComputedStyle(menu).right);
    }
    
    console.log('7. ThreadManager:', typeof ThreadManager !== 'undefined' ? '✅ Defined' : '❌ Not defined');
    if (typeof ThreadManager !== 'undefined') {
        console.log('8. toggleThreadMenu:', typeof ThreadManager.toggleThreadMenu === 'function' ? '✅ Function exists' : '❌ Not a function');
    }
    
    console.log('\n📋 RECOMMENDATIONS:');
    if (!btn) console.log('   ❌ Button not found - check HTML');
    if (!menu) console.log('   ❌ Thread menu not found - check HTML');
    if (typeof ThreadManager === 'undefined') console.log('   ❌ ThreadManager not initialized');
    
    return { btn, menu, hasThreadManager: typeof ThreadManager !== 'undefined' };
};

window.testThemeButton = function() {
    console.log('\n%c🌓 TESTING THEME TOGGLE BUTTON', 'color: #58a6ff; font-size: 14px; font-weight: bold;');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    const btn = document.getElementById('theme-toggle-btn-sidebar');
    const currentTheme = document.documentElement.getAttribute('data-theme') || localStorage.getItem('theme') || 'dark';
    
    console.log('1. Button Element:', btn ? '✅ Found' : '❌ Not Found', btn);
    console.log('2. Current Theme:', currentTheme);
    console.log('3. HTML data-theme:', document.documentElement.getAttribute('data-theme'));
    console.log('4. LocalStorage theme:', localStorage.getItem('theme'));
    
    if (btn) {
        const listeners = getEventListeners(btn);
        console.log('5. Event Listeners:', listeners);
        console.log('   - Click listeners:', listeners.click ? listeners.click.length : 0);
    }
    
    console.log('\n📋 RECOMMENDATIONS:');
    if (!btn) console.log('   ❌ Button not found - check HTML');
    if (btn && getEventListeners(btn).click?.length === 0) console.log('   ❌ No click listeners - button not initialized');
    
    return { btn, currentTheme, hasListeners: btn ? getEventListeners(btn).click?.length > 0 : false };
};

window.testAllButtons = function() {
    console.log('\n%c╔═══════════════════════════════════════════════════════════════╗', 'color: #58a6ff; font-weight: bold;');
    console.log('%c║          RIGHT SIDEBAR COMPREHENSIVE DIAGNOSTICS              ║', 'color: #58a6ff; font-weight: bold;');
    console.log('%c╚═══════════════════════════════════════════════════════════════╝', 'color: #58a6ff; font-weight: bold;');
    
    const results = {
        aiPrime: testAIPrimeButton(),
        userProfile: testUserProfileButton(),
        quickActions: testQuickActionsButton(),
        threads: testThreadsButton(),
        theme: testThemeButton()
    };
    
    console.log('\n%c📊 SUMMARY', 'color: #58a6ff; font-size: 16px; font-weight: bold;');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🤖 AI Prime:', results.aiPrime.btn ? (results.aiPrime.hasListeners ? '✅ Working' : '⚠️  No listeners') : '❌ Not found');
    console.log('👤 User Profile:', results.userProfile.btnSidebar ? (results.userProfile.hasFunction ? '✅ Working' : '⚠️  No function') : '❌ Not found');
    console.log('⚡ Quick Actions:', results.quickActions.btn ? (results.quickActions.hasListeners ? '✅ Working' : '⚠️  No listeners') : '❌ Not found');
    console.log('💬 Threads:', results.threads.btn ? (results.threads.hasThreadManager ? '✅ Working' : '⚠️  No ThreadManager') : '❌ Not found');
    console.log('🌓 Theme:', results.theme.btn ? (results.theme.hasListeners ? '✅ Working' : '⚠️  No listeners') : '❌ Not found');
    
    console.log('\n%c🔧 NEXT STEPS:', 'color: #d29922; font-size: 14px; font-weight: bold;');
    console.log('Run fixAllButtons() to apply fixes automatically');
    
    return results;
};

// ============================================================
// FORCE FUNCTIONS - MAKE BUTTONS WORK
// ============================================================

window.forceAIPrime = function() {
    console.log('\n%c🔧 FORCING AI PRIME TOGGLE', 'color: #d29922; font-size: 14px; font-weight: bold;');
    
    const btn = document.getElementById('ai-prime-toggle-btn');
    const panel = document.getElementById('ai-chat-panel');
    const wrapper = document.getElementById('main-content-wrapper');
    
    if (!btn || !panel || !wrapper) {
        console.error('❌ Missing required elements');
        return false;
    }
    
    // Remove all existing listeners
    const newBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(newBtn, btn);
    
    // Add single clean listener
    newBtn.addEventListener('click', function() {
        const isOpen = !wrapper.classList.contains('chat-collapsed');
        
        if (isOpen) {
            // Close chat
            wrapper.classList.add('chat-collapsed');
            panel.style.display = 'none';
            newBtn.classList.remove('active');
            if (typeof AppState !== 'undefined') AppState.chatOpen = false;
            console.log('🤖 AI Prime chat CLOSED');
        } else {
            // Open chat
            wrapper.classList.remove('chat-collapsed');
            panel.style.display = 'flex';
            newBtn.classList.add('active');
            if (typeof AppState !== 'undefined') AppState.chatOpen = true;
            console.log('🤖 AI Prime chat OPENED');
        }
    });
    
    console.log('✅ AI Prime toggle fixed and working');
    return true;
};

window.forceUserProfile = function() {
    console.log('\n%c🔧 FORCING USER PROFILE OPEN', 'color: #d29922; font-size: 14px; font-weight: bold;');
    
    const menu = document.getElementById('userDropdownMenu');
    const container = document.getElementById('userProfileContainer');
    const btnSidebar = document.getElementById('userProfileBtn-sidebar');
    const btnHeader = document.getElementById('userProfileBtn');
    
    if (!menu) {
        console.error('❌ Dropdown menu not found');
        return false;
    }
    
    // Show container if hidden
    if (container) {
        container.style.display = 'flex';
        console.log('✅ Profile container shown');
    }
    
    // Toggle menu
    menu.classList.toggle('active');
    
    // Update button states
    if (btnSidebar) btnSidebar.classList.toggle('active');
    if (btnHeader) btnHeader.classList.toggle('active');
    
    console.log('✅ User profile', menu.classList.contains('active') ? 'OPENED' : 'CLOSED');
    return true;
};

window.forceQuickActions = function() {
    console.log('\n%c🔧 FORCING QUICK ACTIONS TOGGLE', 'color: #d29922; font-size: 14px; font-weight: bold;');
    
    const promptSidebar = document.getElementById('prompt-sidebar');
    
    if (!promptSidebar) {
        console.error('❌ Prompt sidebar not found');
        return false;
    }
    
    promptSidebar.classList.toggle('show');
    console.log('✅ Quick actions', promptSidebar.classList.contains('show') ? 'OPENED' : 'CLOSED');
    return true;
};

window.forceThreads = function() {
    console.log('\n%c🔧 FORCING THREAD MENU TOGGLE', 'color: #d29922; font-size: 14px; font-weight: bold;');
    
    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.toggleThreadMenu === 'function') {
        ThreadManager.toggleThreadMenu();
        console.log('✅ Thread menu toggled via ThreadManager');
        return true;
    }
    
    const menu = document.getElementById('thread-menu');
    if (menu) {
        menu.classList.toggle('active');
        console.log('✅ Thread menu toggled directly');
        return true;
    }
    
    console.error('❌ Thread menu not found');
    return false;
};

window.forceTheme = function() {
    console.log('\n%c🔧 FORCING THEME TOGGLE', 'color: #d29922; font-size: 14px; font-weight: bold;');
    
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    console.log('✅ Theme changed from', currentTheme, 'to', newTheme);
    return true;
};

// ============================================================
// FIX ALL BUTTONS
// ============================================================

window.fixAllButtons = function() {
    console.log('\n%c🔧 APPLYING FIXES TO ALL BUTTONS', 'color: #d29922; font-size: 16px; font-weight: bold;');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    let fixed = 0;
    let failed = 0;
    
    // Fix AI Prime
    console.log('\n1. Fixing AI Prime toggle...');
    if (forceAIPrime()) {
        fixed++;
    } else {
        failed++;
    }
    
    // Fix User Profile container
    console.log('\n2. Fixing User Profile...');
    const container = document.getElementById('userProfileContainer');
    if (container) {
        container.style.display = 'flex';
        console.log('✅ User Profile container shown');
        fixed++;
    } else {
        console.log('❌ User Profile container not found');
        failed++;
    }
    
    // Fix Quick Actions button
    console.log('\n3. Fixing Quick Actions...');
    const quickActionsBtn = document.getElementById('quick-actions-btn');
    if (quickActionsBtn) {
        const newBtn = quickActionsBtn.cloneNode(true);
        quickActionsBtn.parentNode.replaceChild(newBtn, quickActionsBtn);
        
        newBtn.addEventListener('click', function() {
            const promptSidebar = document.getElementById('prompt-sidebar');
            if (promptSidebar) {
                promptSidebar.classList.toggle('show');
                console.log('⚡ Quick actions toggled');
            }
        });
        console.log('✅ Quick Actions button fixed');
        fixed++;
    } else {
        console.log('❌ Quick Actions button not found');
        failed++;
    }
    
    // Fix Threads button
    console.log('\n4. Fixing Threads button...');
    const threadsBtn = document.getElementById('threads-btn');
    if (threadsBtn) {
        const newBtn = threadsBtn.cloneNode(true);
        threadsBtn.parentNode.replaceChild(newBtn, threadsBtn);
        
        newBtn.addEventListener('click', function() {
            if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.toggleThreadMenu === 'function') {
                ThreadManager.toggleThreadMenu();
            } else {
                const menu = document.getElementById('thread-menu');
                if (menu) menu.classList.toggle('active');
            }
            console.log('💬 Threads toggled');
        });
        console.log('✅ Threads button fixed');
        fixed++;
    } else {
        console.log('❌ Threads button not found');
        failed++;
    }
    
    // Fix Theme button
    console.log('\n5. Fixing Theme toggle...');
    const themeBtn = document.getElementById('theme-toggle-btn-sidebar');
    if (themeBtn) {
        const newBtn = themeBtn.cloneNode(true);
        themeBtn.parentNode.replaceChild(newBtn, themeBtn);
        
        newBtn.addEventListener('click', function() {
            forceTheme();
        });
        console.log('✅ Theme button fixed');
        fixed++;
    } else {
        console.log('❌ Theme button not found');
        failed++;
    }
    
    console.log('\n%c📊 FIX SUMMARY', 'color: #58a6ff; font-size: 14px; font-weight: bold;');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('✅ Fixed:', fixed);
    console.log('❌ Failed:', failed);
    console.log('\n%c🎉 All buttons should now work! Test them manually.', 'color: #3fb950; font-size: 14px; font-weight: bold;');
};

// ============================================================
// AUTO-RUN ON LOAD
// ============================================================

console.log('\n%c✅ Debugging script loaded successfully!', 'color: #3fb950; font-size: 14px; font-weight: bold;');
console.log('\nRun testAllButtons() to diagnose issues');
console.log('Run fixAllButtons() to apply fixes automatically\n');
