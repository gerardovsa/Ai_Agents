/**
 * QUICK TEST: Copy-paste this entire file content into browser console
 * This will test if the expand function works after the fix
 */

console.clear();
console.log('%c='.repeat(70), 'color: #58a6ff');
console.log('%c🧪 AGENT INPUT EXPAND TEST', 'color: #3fb950; font-size: 18px; font-weight: bold');
console.log('%c='.repeat(70), 'color: #58a6ff');
console.log('');

// Test configuration
const TEST_AGENT_ID = 3;

// Step 1: Check if AgentInput exists
console.log('%c📦 Step 1: Checking if AgentInput module exists...', 'color: #d29922; font-weight: bold');

if (typeof AgentInput === 'undefined') {
    console.error('%c❌ FAIL: AgentInput is not defined!', 'color: #f85149; font-weight: bold');
    console.error('   This means agent-input-manager.js did not load.');
    console.error('   Solution: Hard refresh browser (Ctrl+Shift+R) to reload scripts.');
    console.log('');
    console.log('%c⚠️ TEST ABORTED', 'color: #f85149; font-weight: bold');
} else {
    console.log('%c✅ PASS: AgentInput exists', 'color: #3fb950; font-weight: bold');
    console.log('   Available methods:', Object.keys(AgentInput));
    console.log('');

    // Step 2: Check if expand function exists
    console.log('%c🔧 Step 2: Checking if expand function exists...', 'color: #d29922; font-weight: bold');

    if (typeof AgentInput.expand !== 'function') {
        console.error('%c❌ FAIL: AgentInput.expand is not a function!', 'color: #f85149; font-weight: bold');
        console.error('   Type of expand:', typeof AgentInput.expand);
        console.error('   Available methods:', Object.keys(AgentInput));
        console.log('');
        console.log('%c⚠️ TEST ABORTED', 'color: #f85149; font-weight: bold');
    } else {
        console.log('%c✅ PASS: AgentInput.expand is a function', 'color: #3fb950; font-weight: bold');
        console.log('');

        // Step 3: Find the container
        console.log('%c📍 Step 3: Finding container for Agent ${TEST_AGENT_ID}...', 'color: #d29922; font-weight: bold');

        const container = document.querySelector(`#agent-column-${TEST_AGENT_ID} .agent-input-container`);

        if (!container) {
            console.error('%c❌ FAIL: Container not found!', 'color: #f85149; font-weight: bold');
            console.error(`   Selector: #agent-column-${TEST_AGENT_ID} .agent-input-container`);
            console.error('   Possible reasons:');
            console.error('   - Agent 3 column does not exist in DOM');
            console.error('   - Container element has different structure');
            console.log('');
            console.log('%c⚠️ TEST ABORTED', 'color: #f85149; font-weight: bold');
        } else {
            console.log('%c✅ PASS: Container found', 'color: #3fb950; font-weight: bold');
            console.log('   Container:', container);
            console.log('');

            // Step 4: Check container state BEFORE expand
            console.log('%c📊 Step 4: Container state BEFORE expand...', 'color: #d29922; font-weight: bold');

            const beforeHeight = container.offsetHeight;
            const beforeHasExpanded = container.classList.contains('expanded');
            const beforeDisplay = window.getComputedStyle(container).display;

            console.table({
                'offsetHeight': beforeHeight + 'px',
                'has "expanded" class': beforeHasExpanded,
                'display': beforeDisplay,
                'className': container.className
            });

            if (beforeDisplay === 'none') {
                console.warn('%c⚠️ WARNING: Container is hidden (display: none)', 'color: #d29922; font-weight: bold');
                console.warn('   This means no thread is loaded in Agent 3.');
                console.warn('   Load a thread first, then run this test again.');
                console.log('');
                console.log('%c⚠️ TEST ABORTED', 'color: #f85149; font-weight: bold');
            } else {
                console.log('');

                // Step 5: Call expand function
                console.log('%c🚀 Step 5: Calling AgentInput.expand(${TEST_AGENT_ID})...', 'color: #d29922; font-weight: bold');

                try {
                    AgentInput.expand(TEST_AGENT_ID);
                    console.log('%c✅ PASS: expand() called without errors', 'color: #3fb950; font-weight: bold');
                } catch (error) {
                    console.error('%c❌ FAIL: expand() threw an error!', 'color: #f85149; font-weight: bold');
                    console.error('   Error:', error);
                    console.log('');
                    console.log('%c❌ TEST FAILED', 'color: #f85149; font-weight: bold');
                    throw error;
                }

                console.log('');

                // Step 6: Check container state AFTER expand (with delay)
                console.log('%c⏳ Step 6: Waiting 200ms for transition...', 'color: #d29922; font-weight: bold');

                setTimeout(() => {
                    console.log('%c📊 Container state AFTER expand...', 'color: #d29922; font-weight: bold');

                    const afterHeight = container.offsetHeight;
                    const afterHasExpanded = container.classList.contains('expanded');
                    const afterDisplay = window.getComputedStyle(container).display;

                    console.table({
                        'offsetHeight': afterHeight + 'px',
                        'has "expanded" class': afterHasExpanded,
                        'display': afterDisplay,
                        'className': container.className
                    });

                    console.log('');

                    // Step 7: Verify expansion worked
                    console.log('%c🎯 Step 7: Verifying expansion...', 'color: #d29922; font-weight: bold');

                    const heightIncreased = afterHeight > beforeHeight;
                    const hasExpandedClass = afterHasExpanded === true;
                    const notCollapsed = afterHeight > 30;

                    console.log('   Height increased:', heightIncreased ? '✅ YES' : '❌ NO', `(${beforeHeight}px → ${afterHeight}px)`);
                    console.log('   Has "expanded" class:', hasExpandedClass ? '✅ YES' : '❌ NO');
                    console.log('   Height > 30px:', notCollapsed ? '✅ YES' : '❌ NO', `(${afterHeight}px)`);
                    console.log('');

                    // Final result
                    if (heightIncreased && hasExpandedClass && notCollapsed) {
                        console.log('%c='.repeat(70), 'color: #3fb950');
                        console.log('%c🎉 SUCCESS! Container expanded correctly!', 'color: #3fb950; font-size: 18px; font-weight: bold');
                        console.log('%c='.repeat(70), 'color: #3fb950');
                        console.log('');
                        console.log('%cThe expandable input container is working! ✅', 'color: #3fb950; font-weight: bold');
                        console.log('');
                        console.log('Next steps:');
                        console.log('1. Visually confirm the container expanded in the UI');
                        console.log('2. Try clicking the 30px bar to expand it manually');
                        console.log('3. Try hovering over the bar to see animation');
                        console.log('4. Test the feedback area (click feedback button)');
                        console.log('5. Test all 6 buttons in the vertical stack');
                    } else {
                        console.log('%c='.repeat(70), 'color: #f85149');
                        console.log('%c❌ TEST FAILED - Container did not expand properly', 'color: #f85149; font-size: 18px; font-weight: bold');
                        console.log('%c='.repeat(70), 'color: #f85149');
                        console.log('');
                        console.log('%cPossible issues:', 'color: #f85149; font-weight: bold');

                        if (!heightIncreased) {
                            console.log('❌ Height did not increase - CSS transition may be broken');
                        }
                        if (!hasExpandedClass) {
                            console.log('❌ "expanded" class was not added - JavaScript issue');
                        }
                        if (!notCollapsed) {
                            console.log('❌ Height still 30px or less - CSS not applying');
                        }

                        console.log('');
                        console.log('Debug info:');
                        console.log('  CSS file loaded:', Array.from(document.styleSheets).some(s => s.href && s.href.includes('agent-ui.css')));
                        console.log('  Container element:', container);
                    }
                }, 200);
            }
        }
    }
}
