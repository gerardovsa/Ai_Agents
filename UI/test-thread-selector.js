/**
 * Diagnostic script to test thread selector clickability
 * Run this in browser console to diagnose issues
 */

console.log('=== THREAD SELECTOR DIAGNOSTIC ===');

// 1. Check if AgentColumn exists
console.log('1. AgentColumn exists:', typeof AgentColumn !== 'undefined');

// 2. Check if functions exist
if (typeof AgentColumn !== 'undefined') {
    console.log('2. showThreadSelector exists:', typeof AgentColumn.showThreadSelector === 'function');
    console.log('   refreshAllAgentThreadInfos exists:', typeof AgentColumn.refreshAllAgentThreadInfos === 'function');
}

// 3. Check thread-info containers
for (let i = 1; i <= 3; i++) {
    const container = document.getElementById(`thread-info-${i}`);
    if (container) {
        const noThreadMsg = container.querySelector('.no-thread-message');
        const computedStyle = noThreadMsg ? window.getComputedStyle(noThreadMsg) : null;

        console.log(`\n3. Agent ${i} thread-info:`);
        console.log('   - Container exists:', !!container);
        console.log('   - Has .no-thread-message:', !!noThreadMsg);
        console.log('   - Has .clickable class:', noThreadMsg ? noThreadMsg.classList.contains('clickable') : false);
        console.log('   - Has onclick:', noThreadMsg ? noThreadMsg.hasAttribute('onclick') : false);

        if (computedStyle) {
            console.log('   - cursor:', computedStyle.cursor);
            console.log('   - pointer-events:', computedStyle.pointerEvents);
            console.log('   - z-index:', computedStyle.zIndex);
            console.log('   - position:', computedStyle.position);
        }

        // Check for dropdown
        const dropdown = document.getElementById(`thread-selector-${i}`);
        console.log('   - Dropdown exists:', !!dropdown);
    }
}

// 4. Check for blocking overlays
console.log('\n4. Checking for blocking overlays:');
const overlays = document.querySelectorAll('[class*="overlay"]');
overlays.forEach(overlay => {
    const style = window.getComputedStyle(overlay);
    const isVisible = style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
    if (isVisible) {
        console.log(`   - Found visible overlay: ${overlay.className}`);
        console.log(`     z-index: ${style.zIndex}, pointer-events: ${style.pointerEvents}`);
    }
});

// 5. Test click handler
console.log('\n5. Testing click on agent-1 no-thread-message:');
const testContainer = document.getElementById('thread-info-1');
if (testContainer) {
    const testMsg = testContainer.querySelector('.no-thread-message');
    if (testMsg) {
        console.log('   - Adding test click listener...');
        testMsg.addEventListener('click', function testClick(e) {
            console.log('   ✅ CLICK DETECTED!');
            console.log('   - Target:', e.target);
            console.log('   - CurrentTarget:', e.currentTarget);
            testMsg.removeEventListener('click', testClick);
        }, { once: true });
        console.log('   - Click the "No thread assigned" message now...');
    }
}

// 6. Manual refresh suggestion
console.log('\n6. To manually refresh all agent thread infos:');
console.log('   AgentColumn.refreshAllAgentThreadInfos()');

console.log('\n=== END DIAGNOSTIC ===');
