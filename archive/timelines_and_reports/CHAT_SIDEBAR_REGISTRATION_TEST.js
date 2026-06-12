/**
 * CHAT SIDEBAR REGISTRATION - VERIFICATION TEST
 * 
 * Run this script in the browser console after the page loads
 * to verify the chat sidebar is correctly registered with SidebarManager.
 */

console.log('🧪 [CHAT SIDEBAR TEST] Starting registration verification...\n');

// Test 1: Check SidebarManager exists
console.log('✓ Test 1: SidebarManager exists');
if (!window.SidebarManager) {
    console.error('❌ FAILED: SidebarManager not found');
} else {
    console.log('✅ PASSED: SidebarManager found');
}

// Test 2: Check chat sidebar is registered
console.log('\n✓ Test 2: Chat sidebar registered');
const allSidebars = window.SidebarManager.getAll().map(s => s.id);
console.log('Registered sidebars:', allSidebars);

if (!allSidebars.includes('chat-sidebar')) {
    console.error('❌ FAILED: chat-sidebar not registered');
} else {
    console.log('✅ PASSED: chat-sidebar is registered');
}

// Test 3: Check button exists
console.log('\n✓ Test 3: Toggle button exists');
const button = document.getElementById('chat-sidebar-toggle');
if (!button) {
    console.error('❌ FAILED: Toggle button not found');
} else {
    console.log('✅ PASSED: Toggle button found');
    console.log('Button onclick:', button.getAttribute('onclick')); // Should be null
    if (button.getAttribute('onclick')) {
        console.warn('⚠️ WARNING: Button still has onclick handler (should be removed)');
    } else {
        console.log('✅ PASSED: onclick handler removed correctly');
    }
}

// Test 4: Check ChatSidebar object exists
console.log('\n✓ Test 4: ChatSidebar object exists');
if (!window.ChatSidebar) {
    console.error('❌ FAILED: ChatSidebar not found');
} else {
    console.log('✅ PASSED: ChatSidebar found');
    console.log('Methods:', Object.keys(window.ChatSidebar).filter(k => typeof window.ChatSidebar[k] === 'function'));
}

// Test 5: Check sidebar element exists
console.log('\n✓ Test 5: Sidebar DOM element exists');
const sidebar = document.getElementById('chat-sidebar');
if (!sidebar) {
    console.error('❌ FAILED: Sidebar element not found');
} else {
    console.log('✅ PASSED: Sidebar element found');
}

// Test 6: Programmatic open test
console.log('\n✓ Test 6: Programmatic open/close');
console.log('Opening sidebar programmatically...');
window.SidebarManager.open('chat-sidebar');
setTimeout(() => {
    const isOpen = window.SidebarManager.isOpen('chat-sidebar');
    if (isOpen) {
        console.log('✅ PASSED: Sidebar opened successfully');

        // Close after 2 seconds
        setTimeout(() => {
            console.log('Closing sidebar programmatically...');
            window.SidebarManager.close('chat-sidebar');
            setTimeout(() => {
                const isClosed = !window.SidebarManager.isOpen('chat-sidebar');
                if (isClosed) {
                    console.log('✅ PASSED: Sidebar closed successfully');
                } else {
                    console.error('❌ FAILED: Sidebar did not close');
                }
            }, 500);
        }, 2000);
    } else {
        console.error('❌ FAILED: Sidebar did not open');
    }
}, 500);

// Test 7: Button click test
console.log('\n✓ Test 7: Button click test');
console.log('You can manually test by clicking the chat button (💬 icon)');
console.log('Expected behavior:');
console.log('  1. Sidebar should slide in from the right');
console.log('  2. Console should show "[CHAT SIDEBAR] Opening..." messages');
console.log('  3. Chat list should load');
console.log('  4. Second click should close sidebar');

// Test 8: Legacy compatibility test
console.log('\n✓ Test 8: Legacy compatibility');
if (window.ChatSidebar && typeof window.ChatSidebar.toggleSidebar === 'function') {
    console.log('✅ PASSED: ChatSidebar.toggleSidebar() exists (legacy compatibility)');
    console.log('Try: ChatSidebar.toggleSidebar() in console');
} else {
    console.error('❌ FAILED: ChatSidebar.toggleSidebar() not found');
}

// Summary
console.log('\n' + '='.repeat(60));
console.log('🎯 VERIFICATION COMPLETE');
console.log('='.repeat(60));
console.log('\n📋 Manual Testing Checklist:');
console.log('□ Click chat button - sidebar opens');
console.log('□ Click again - sidebar closes');
console.log('□ Click other sidebar buttons - chat closes automatically');
console.log('□ Drag chat button - repositions correctly');
console.log('□ Check console logs - no errors');
console.log('□ Test ChatSidebar.toggleSidebar() in console');
console.log('□ Test SidebarManager.toggle("chat-sidebar") in console');

console.log('\n💡 Quick Commands:');
console.log('  SidebarManager.open("chat-sidebar")    - Open chat');
console.log('  SidebarManager.close("chat-sidebar")   - Close chat');
console.log('  SidebarManager.toggle("chat-sidebar")  - Toggle chat');
console.log('  ChatSidebar.toggleSidebar()            - Legacy toggle');
console.log('  SidebarManager.getAll()                - List all sidebars');
