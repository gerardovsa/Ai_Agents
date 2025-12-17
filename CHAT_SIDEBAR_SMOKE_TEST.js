/**
 * CHAT SIDEBAR SMOKE TEST
 * Validates all dependencies, imports, and API availability
 */

console.log('=== CHAT SIDEBAR SMOKE TEST ===\n');

// ==================== DEPENDENCY CHECKS ====================

console.log('1. Checking Global Dependencies...');

const dependencies = {
    'Socket.IO': typeof io !== 'undefined',
    'SynergyRealtime': typeof SynergyRealtime !== 'undefined',
    'ChatSidebar': typeof ChatSidebar !== 'undefined',
    'EnhancedToast': typeof EnhancedToast !== 'undefined' // Optional
};

Object.entries(dependencies).forEach(([name, available]) => {
    const status = available ? '✓' : '✗';
    const required = name === 'EnhancedToast' ? '(optional)' : '(required)';
    console.log(`  ${status} ${name} ${required}: ${available ? 'Available' : 'MISSING'}`);
});

// ==================== WEBRTC SUPPORT ====================

console.log('\n2. Checking WebRTC Support...');

const webrtcChecks = {
    'getUserMedia': !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
    'RTCPeerConnection': typeof RTCPeerConnection !== 'undefined',
    'WebSocket': typeof WebSocket !== 'undefined'
};

Object.entries(webrtcChecks).forEach(([name, available]) => {
    const status = available ? '✓' : '✗';
    console.log(`  ${status} ${name}: ${available ? 'Supported' : 'NOT SUPPORTED'}`);
});

// ==================== CHAT SIDEBAR API ====================

console.log('\n3. Checking ChatSidebar API...');

if (typeof ChatSidebar !== 'undefined') {
    const methods = [
        'init',
        'toggle',
        'open',
        'close',
        'showChatList',
        'openConversation',
        'sendMessage',
        'startVoiceCall',
        'endCall',
        'copyMessage',
        'replyToMessage',
        'deleteMessage',
        'loadConversationHistory',
        'refreshChatList'
    ];
    
    methods.forEach(method => {
        const exists = typeof ChatSidebar[method] === 'function';
        const status = exists ? '✓' : '✗';
        console.log(`  ${status} ChatSidebar.${method}(): ${exists ? 'Defined' : 'MISSING'}`);
    });
} else {
    console.log('  ✗ ChatSidebar not loaded - cannot check methods');
}

// ==================== SYNERGY REALTIME API ====================

console.log('\n4. Checking SynergyRealtime API...');

if (typeof SynergyRealtime !== 'undefined') {
    const methods = [
        'connect',
        'disconnect',
        'isConnected',
        'sendDirectMessage',
        'broadcastMessage',
        '_getUserId',
        '_getUserName',
        '_getDeviceInfo',
        '_generateSessionToken'
    ];
    
    methods.forEach(method => {
        const exists = typeof SynergyRealtime[method] === 'function';
        const status = exists ? '✓' : '✗';
        console.log(`  ${status} SynergyRealtime.${method}(): ${exists ? 'Defined' : 'MISSING'}`);
    });
    
    // Check session token
    if (SynergyRealtime.sessionToken) {
        console.log(`  ✓ Session Token: ${SynergyRealtime.sessionToken}`);
    } else {
        console.log('  ⚠ Session Token: Not generated yet');
    }
    
    // Check connection status
    const connected = SynergyRealtime.isConnected();
    console.log(`  ${connected ? '✓' : '⚠'} Connection Status: ${connected ? 'Connected' : 'Not Connected'}`);
    
} else {
    console.log('  ✗ SynergyRealtime not loaded - cannot check methods');
}

// ==================== DOM ELEMENTS ====================

console.log('\n5. Checking Required DOM Elements...');

const requiredElements = [
    'chat-sidebar',
    'chat-list-view',
    'chat-conversation-view',
    'chat-call-view',
    'chat-messages-container',
    'chat-message-input',
    'chat-list-container',
    'chat-unread-badge'
];

requiredElements.forEach(id => {
    const exists = document.getElementById(id) !== null;
    const status = exists ? '✓' : '✗';
    console.log(`  ${status} #${id}: ${exists ? 'Found' : 'MISSING'}`);
});

// ==================== CSS CLASSES ====================

console.log('\n6. Checking CSS Classes...');

const requiredClasses = [
    'chat-sidebar',
    'chat-message-bubble',
    'chat-list-item',
    'chat-send-btn',
    'chat-call-btn'
];

// Check if CSS is loaded by looking for computed styles
const testDiv = document.createElement('div');
testDiv.className = 'chat-sidebar';
testDiv.style.display = 'none';
document.body.appendChild(testDiv);

requiredClasses.forEach(className => {
    testDiv.className = className;
    const styles = window.getComputedStyle(testDiv);
    const hasStyles = styles.position !== 'static' || 
                      styles.display !== 'inline' || 
                      styles.padding !== '0px';
    const status = hasStyles ? '✓' : '⚠';
    console.log(`  ${status} .${className}: ${hasStyles ? 'Styled' : 'No specific styles (may be OK)'}`);
});

document.body.removeChild(testDiv);

// ==================== API ENDPOINTS ====================

console.log('\n7. Testing API Endpoints (async)...');

const apiEndpoints = [
    '/api/messages/conversations',
    '/api/messages/history?user_id=1&limit=10',
    '/api/user/avatar/1'
];

// Function to test endpoint
async function testEndpoint(endpoint) {
    try {
        const response = await fetch(endpoint);
        const status = response.ok ? '✓' : '⚠';
        console.log(`  ${status} ${endpoint}: ${response.status} ${response.statusText}`);
        return response.ok;
    } catch (error) {
        console.log(`  ✗ ${endpoint}: ERROR - ${error.message}`);
        return false;
    }
}

// Run async tests
(async () => {
    for (const endpoint of apiEndpoints) {
        await testEndpoint(endpoint);
    }
    
    // ==================== MULTI-SESSION TEST ====================
    
    console.log('\n8. Multi-Session Support Test...');
    
    if (typeof SynergyRealtime !== 'undefined') {
        const deviceInfo = SynergyRealtime._getDeviceInfo();
        console.log(`  ✓ Device Detection: ${deviceInfo}`);
        
        // Check for emojis (should be text only)
        const hasEmojis = /[\u{1F300}-\u{1F9FF}]/u.test(deviceInfo);
        console.log(`  ${hasEmojis ? '✗' : '✓'} Emoji Check: ${hasEmojis ? 'CONTAINS EMOJIS (should be text)' : 'Text only (correct)'}`);
        
        // Check session token format
        if (SynergyRealtime.sessionToken) {
            const validFormat = /^session_[a-z0-9]+_\d+$/.test(SynergyRealtime.sessionToken);
            console.log(`  ${validFormat ? '✓' : '✗'} Session Token Format: ${validFormat ? 'Valid' : 'Invalid format'}`);
        }
        
        // Check multi-session tracking
        const hasTracking = typeof SynergyRealtime.otherSessionsViewingAgents === 'object';
        console.log(`  ${hasTracking ? '✓' : '✗'} Multi-Session Tracking: ${hasTracking ? 'Enabled' : 'MISSING'}`);
    }
    
    // ==================== WEBSOCKET EVENTS ====================
    
    console.log('\n9. Checking WebSocket Event Handlers...');
    
    if (typeof SynergyRealtime !== 'undefined' && SynergyRealtime.socket) {
        const eventHandlers = [
            'voice_call_offer',
            'voice_call_answer',
            'voice_call_ice_candidate',
            'voice_call_ended',
            'direct_message_received',
            'broadcast_message_received'
        ];
        
        eventHandlers.forEach(event => {
            const hasHandler = SynergyRealtime.socket._callbacks && 
                              SynergyRealtime.socket._callbacks[`$${event}`];
            const status = hasHandler ? '✓' : '⚠';
            console.log(`  ${status} ${event}: ${hasHandler ? 'Handler registered' : 'No handler (may be added later)'}`);
        });
    } else {
        console.log('  ⚠ Socket not connected - cannot check event handlers');
    }
    
    // ==================== SECURITY CHECKS ====================
    
    console.log('\n10. Security Checks...');
    
    const isSecure = window.location.protocol === 'https:' || 
                     window.location.hostname === 'localhost' || 
                     window.location.hostname === '127.0.0.1';
    
    console.log(`  ${isSecure ? '✓' : '⚠'} HTTPS/Localhost: ${window.location.protocol} ${isSecure ? '(WebRTC will work)' : '(WebRTC requires HTTPS)'}`);
    
    // ==================== FINAL SUMMARY ====================
    
    console.log('\n=== SMOKE TEST SUMMARY ===\n');
    
    const allDepsAvailable = dependencies['Socket.IO'] && 
                            dependencies['SynergyRealtime'] && 
                            dependencies['ChatSidebar'];
    
    const webrtcSupported = webrtcChecks['getUserMedia'] && 
                           webrtcChecks['RTCPeerConnection'];
    
    console.log(`Dependencies: ${allDepsAvailable ? '✓ ALL REQUIRED AVAILABLE' : '✗ SOME MISSING'}`);
    console.log(`WebRTC Support: ${webrtcSupported ? '✓ FULLY SUPPORTED' : '✗ NOT SUPPORTED'}`);
    console.log(`Security: ${isSecure ? '✓ SECURE CONTEXT' : '⚠ INSECURE (WebRTC may fail)'}`);
    
    if (allDepsAvailable && webrtcSupported && isSecure) {
        console.log('\n✓✓✓ CHAT SIDEBAR IS READY TO USE ✓✓✓');
    } else {
        console.log('\n⚠⚠⚠ SOME ISSUES FOUND - REVIEW ABOVE ⚠⚠⚠');
    }
    
    // ==================== INTEGRATION TEST ====================
    
    console.log('\n11. Quick Integration Test...');
    
    if (typeof ChatSidebar !== 'undefined' && typeof ChatSidebar.init === 'function') {
        try {
            // Don't actually init (may cause issues), just check it's callable
            console.log('  ✓ ChatSidebar.init is callable');
            console.log('  ℹ To initialize: ChatSidebar.init()');
            console.log('  ℹ To toggle sidebar: ChatSidebar.toggle()');
            console.log('  ℹ To open conversation: ChatSidebar.openConversation(userId, userName, device)');
        } catch (error) {
            console.log(`  ✗ Error checking init: ${error.message}`);
        }
    }
    
    console.log('\n=== END OF SMOKE TEST ===');
})();

// Export for use in browser console
if (typeof window !== 'undefined') {
    window.ChatSidebarSmokeTest = {
        run: () => {
            console.log('Re-running smoke test...');
            // Reload the script to re-run
            location.reload();
        }
    };
}
