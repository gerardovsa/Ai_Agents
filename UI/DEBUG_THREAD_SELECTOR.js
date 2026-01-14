/**
 * THREAD SELECTOR DROPDOWN DEBUG SCRIPT
 * Copy and paste this into the browser console to diagnose the issue
 */

console.clear();
console.log('🔷 THREAD SELECTOR DROPDOWN DEBUGGER');
console.log('=====================================\n');

// Test 1: Check if AgentColumn exists
console.log('1. AgentColumn exists:', typeof AgentColumn !== 'undefined');
console.log('   - showThreadSelector:', typeof AgentColumn?.showThreadSelector === 'function');
console.log('   - hideThreadSelector:', typeof AgentColumn?.hideThreadSelector === 'function');

// Test 2: Check dropdown HTML structure
console.log('\n2. Dropdown Structure Check:');
for (let i = 1; i <= 9; i++) {
    const container = document.getElementById(`thread-info-${i}`);
    if (container) {
        const dropdown = document.getElementById(`thread-selector-${i}`);
        const noThreadMsg = container.querySelector('.no-thread-message');
        const wrapper = container.querySelector('.thread-info-wrapper');

        console.log(`   Agent-${i}:`);
        console.log(`      - Container exists: ${!!container}`);
        console.log(`      - Wrapper exists: ${!!wrapper}`);
        console.log(`      - No-thread message: ${!!noThreadMsg}`);
        console.log(`      - Dropdown exists: ${!!dropdown}`);
        console.log(`      - Dropdown parent: ${dropdown?.parentElement?.className || 'N/A'}`);
        console.log(`      - Dropdown display: ${dropdown?.style.display || 'N/A'}`);
    }
}

// Test 3: Check for event listeners
console.log('\n3. Event Listener Check:');
console.log('   Checking document click listeners...');
const listeners = getEventListeners?.(document) || { click: [] };
console.log('   Document has', listeners.click?.length || 0, 'click listeners');

// Test 4: Monitor clicks in real-time
console.log('\n4. Real-time Click Monitor:');
console.log('   Setting up click monitor (will log all clicks for 30 seconds)...\n');

let clickCount = 0;
const clickMonitor = (e) => {
    clickCount++;
    console.log(`   Click #${clickCount}:`);
    console.log('      Target:', e.target.className || e.target.tagName);
    console.log('      Closest .no-thread-message:', !!e.target.closest('.no-thread-message'));
    console.log('      Closest .thread-selector-dropdown:', !!e.target.closest('.thread-selector-dropdown'));
    console.log('      Current phase:', e.eventPhase === 1 ? 'CAPTURING' : e.eventPhase === 2 ? 'AT_TARGET' : 'BUBBLING');
    console.log('');
};

document.addEventListener('click', clickMonitor, true); // Capture phase

setTimeout(() => {
    document.removeEventListener('click', clickMonitor, true);
    console.log('✅ Click monitoring stopped after 30 seconds');
}, 30000);

// Test 5: Manual trigger test
console.log('\n5. Manual Trigger Test:');
console.log('   To manually test agent-1 dropdown:');
console.log('   Run: testDropdown(1)\n');

window.testDropdown = async function (agentId) {
    console.log(`\n🔷 Testing dropdown for agent-${agentId}...`);

    const dropdown = document.getElementById(`thread-selector-${agentId}`);
    const noThreadMsg = document.querySelector(`#thread-info-${agentId} .no-thread-message`);

    console.log('   Before click:');
    console.log('      - Dropdown display:', dropdown?.style.display);
    console.log('      - Dropdown innerHTML length:', dropdown?.innerHTML?.length || 0);

    if (noThreadMsg) {
        console.log('   Clicking no-thread-message...');
        noThreadMsg.click();

        setTimeout(() => {
            console.log('   After click (100ms delay):');
            console.log('      - Dropdown display:', dropdown?.style.display);
            console.log('      - Dropdown innerHTML length:', dropdown?.innerHTML?.length || 0);
        }, 100);

        setTimeout(() => {
            console.log('   After click (500ms delay):');
            console.log('      - Dropdown display:', dropdown?.style.display);
            console.log('      - Is visible?:', dropdown?.style.display === 'block');
        }, 500);
    } else {
        console.log('   ❌ No-thread-message not found!');
    }
};

// Test 6: Fix function
console.log('\n6. PROPOSED FIX:');
console.log('   The issue: Click event bubbles up and triggers the "click outside" listener');
console.log('   Solution: Stop propagation on the no-thread-message click');
console.log('   To apply fix, run: applyFix()\n');

window.applyFix = function () {
    console.log('🔧 Applying fix...');

    // Remove inline onclick handlers and add proper event listeners
    document.querySelectorAll('.no-thread-message.clickable').forEach(msg => {
        const agentMatch = msg.getAttribute('onclick')?.match(/showThreadSelector\((\d+)\)/);
        if (agentMatch) {
            const agentId = parseInt(agentMatch[1]);
            msg.removeAttribute('onclick');

            msg.addEventListener('click', (e) => {
                e.stopPropagation(); // CRITICAL: Stop event bubbling
                e.preventDefault();
                console.log(`✅ Click intercepted for agent-${agentId} (propagation stopped)`);
                if (typeof AgentColumn !== 'undefined') {
                    AgentColumn.showThreadSelector(agentId);
                }
            });

            console.log(`   ✅ Fixed agent-${agentId} no-thread-message`);
        }

        const primeMatch = msg.getAttribute('onclick')?.match(/showPrimeThreadSelector/);
        if (primeMatch) {
            msg.removeAttribute('onclick');

            msg.addEventListener('click', (e) => {
                e.stopPropagation(); // CRITICAL: Stop event bubbling
                e.preventDefault();
                console.log(`✅ Click intercepted for Prime (propagation stopped)`);
                if (typeof AgentColumn !== 'undefined') {
                    AgentColumn.showPrimeThreadSelector();
                }
            });

            console.log(`   ✅ Fixed Prime no-thread-message`);
        }
    });

    console.log('✅ Fix applied! Try clicking a dropdown now.');
};

console.log('\n=====================================');
console.log('🔷 DEBUG SCRIPT LOADED');
console.log('   - Run testDropdown(1) to test agent-1');
console.log('   - Run applyFix() to apply the fix');
console.log('   - Click monitoring active for 30 seconds');
console.log('=====================================\n');
