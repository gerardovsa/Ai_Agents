/**
 * AGENT INPUT CONTAINER - DEBUG CONSOLE COMMANDS
 * 
 * Copy and paste these commands into your browser console (F12)
 * to diagnose and test the expandable input container
 */

// ============================================================
// COMMAND 1: Full Diagnostic Report
// ============================================================
(function () {
    const agentId = 3; // Change this to test different agents

    console.log('%c='.repeat(60), 'color: #58a6ff');
    console.log('%c🔍 AGENT INPUT CONTAINER DIAGNOSTIC', 'color: #58a6ff; font-size: 16px; font-weight: bold');
    console.log('%c='.repeat(60), 'color: #58a6ff');
    console.log('');

    // Find container
    const container = document.querySelector(`#agent-column-${agentId} .agent-input-container`);

    if (!container) {
        console.error(`❌ Container not found: #agent-column-${agentId} .agent-input-container`);

        // Try alternatives
        const alt1 = document.querySelector(`.agent-input-container[data-agent-id="${agentId}"]`);
        const alt2 = document.querySelector(`[data-agent-id="${agentId}"]`);

        console.log('\n🔍 Alternative selectors:');
        console.log(`  .agent-input-container[data-agent-id="${agentId}"]:`, alt1 || 'NOT FOUND');
        console.log(`  [data-agent-id="${agentId}"]:`, alt2 || 'NOT FOUND');
        return;
    }

    console.log('%c✅ Container found!', 'color: #3fb950; font-weight: bold');
    console.log('Container element:', container);
    console.log('');

    // Computed styles
    const style = window.getComputedStyle(container);
    console.log('%c📊 COMPUTED STYLES:', 'color: #d29922; font-weight: bold');
    console.table({
        'display': style.display,
        'height': style.height,
        'overflow': style.overflow,
        'cursor': style.cursor,
        'position': style.position,
        'padding': style.padding,
        'background': style.background,
        'pointer-events': style.pointerEvents,
        'z-index': style.zIndex,
        'opacity': style.opacity,
        'transition': style.transition
    });
    console.log('');

    // Classes
    console.log('%c📝 CLASSES:', 'color: #d29922; font-weight: bold');
    console.log('  classList:', container.className);
    console.log('  Has "expanded":', container.classList.contains('expanded'));
    console.log('');

    // Dimensions
    console.log('%c📏 DIMENSIONS:', 'color: #d29922; font-weight: bold');
    const rect = container.getBoundingClientRect();
    console.table({
        'offsetHeight': container.offsetHeight + 'px',
        'offsetWidth': container.offsetWidth + 'px',
        'scrollHeight': container.scrollHeight + 'px',
        'clientHeight': container.clientHeight + 'px',
        'rect.height': rect.height + 'px',
        'rect.width': rect.width + 'px',
        'rect.top': rect.top + 'px',
        'rect.left': rect.left + 'px',
        'visible': (rect.width > 0 && rect.height > 0) ? '✅ YES' : '❌ NO'
    });
    console.log('');

    // Child elements
    console.log('%c👶 CHILD ELEMENTS:', 'color: #d29922; font-weight: bold');
    const feedback = container.querySelector('.agent-feedback-container');
    const wrapper = container.querySelector('.agent-input-wrapper');
    const textarea = container.querySelector('.agent-input-textarea');

    console.log('  .agent-feedback-container:', feedback || '❌ NOT FOUND');
    if (feedback) {
        const fbStyle = window.getComputedStyle(feedback);
        console.log('    → display:', fbStyle.display, '| opacity:', fbStyle.opacity);
    }

    console.log('  .agent-input-wrapper:', wrapper || '❌ NOT FOUND');
    if (wrapper) {
        const wStyle = window.getComputedStyle(wrapper);
        console.log('    → display:', wStyle.display, '| opacity:', wStyle.opacity, '| pointer-events:', wStyle.pointerEvents);
    }

    console.log('  .agent-input-textarea:', textarea || '❌ NOT FOUND');
    console.log('');

    // AgentInput state
    console.log('%c🔧 AGENT INPUT STATE:', 'color: #d29922; font-weight: bold');
    if (typeof AgentInput !== 'undefined') {
        console.log('  ✅ window.AgentInput exists');
        console.log('  AgentInput object:', AgentInput);
    } else {
        console.error('  ❌ window.AgentInput NOT FOUND');
    }
    console.log('');

    // CSS loaded
    console.log('%c📄 CSS FILES:', 'color: #d29922; font-weight: bold');
    const stylesheets = Array.from(document.styleSheets);
    const agentCss = stylesheets.find(sheet => {
        try {
            return sheet.href && sheet.href.includes('agent-ui.css');
        } catch (e) {
            return false;
        }
    });
    console.log('  agent-ui.css loaded:', agentCss ? '✅ YES' : '❌ NO');
    if (agentCss) {
        console.log('  → href:', agentCss.href);
    }
    console.log('');

    console.log('%c='.repeat(60), 'color: #58a6ff');
    console.log('%c🏁 DIAGNOSTIC COMPLETE', 'color: #3fb950; font-size: 16px; font-weight: bold');
    console.log('%c='.repeat(60), 'color: #58a6ff');
})();

// ============================================================
// COMMAND 2: Test Expand Function
// ============================================================
// Uncomment and run this separately:
/*
(function() {
    const agentId = 3;
    
    console.log('%c🔄 TESTING EXPAND...', 'color: #58a6ff; font-weight: bold');
    
    if (typeof AgentInput === 'undefined') {
        console.error('❌ AgentInput not found');
        return;
    }
    
    console.log('Calling AgentInput.expand(' + agentId + ')...');
    AgentInput.expand(agentId);
    
    setTimeout(() => {
        const container = document.querySelector(`#agent-column-${agentId} .agent-input-container`);
        if (container) {
            console.log('Result:', container.classList.contains('expanded') ? '✅ EXPANDED' : '❌ NOT EXPANDED');
            console.log('Height:', container.offsetHeight + 'px');
            console.log('Classes:', container.className);
        }
    }, 200);
})();
*/

// ============================================================
// COMMAND 3: Simulate Click Event
// ============================================================
// Uncomment and run this separately:
/*
(function() {
    const agentId = 3;
    
    console.log('%c👆 SIMULATING CLICK...', 'color: #58a6ff; font-weight: bold');
    
    const container = document.querySelector(`#agent-column-${agentId} .agent-input-container`);
    
    if (!container) {
        console.error('❌ Container not found');
        return;
    }
    
    console.log('Container before click:', {
        height: container.offsetHeight + 'px',
        hasExpandedClass: container.classList.contains('expanded')
    });
    
    // Dispatch click event
    const clickEvent = new MouseEvent('click', {
        bubbles: true,
        cancelable: true,
        view: window
    });
    
    console.log('Dispatching click event...');
    container.dispatchEvent(clickEvent);
    
    setTimeout(() => {
        console.log('Container after click:', {
            height: container.offsetHeight + 'px',
            hasExpandedClass: container.classList.contains('expanded')
        });
    }, 200);
})();
*/

// ============================================================
// COMMAND 4: Force Expand with CSS Override
// ============================================================
// Uncomment and run this separately:
/*
(function() {
    const agentId = 3;
    
    console.log('%c🔨 FORCING EXPAND WITH CSS...', 'color: #d29922; font-weight: bold');
    
    const container = document.querySelector(`#agent-column-${agentId} .agent-input-container`);
    
    if (!container) {
        console.error('❌ Container not found');
        return;
    }
    
    // Force expand with inline styles
    container.style.height = 'auto';
    container.style.padding = '20px';
    container.style.overflow = 'visible';
    container.classList.add('expanded');
    
    const wrapper = container.querySelector('.agent-input-wrapper');
    if (wrapper) {
        wrapper.style.opacity = '1';
        wrapper.style.pointerEvents = 'auto';
    }
    
    console.log('✅ Forced expand applied');
    console.log('Height:', container.offsetHeight + 'px');
    console.log('Classes:', container.className);
})();
*/

// ============================================================
// COMMAND 5: Get All Applied CSS Rules
// ============================================================
// Uncomment and run this separately:
/*
(function() {
    const agentId = 3;
    
    console.log('%c📋 ALL CSS RULES APPLIED TO CONTAINER', 'color: #58a6ff; font-weight: bold');
    
    const container = document.querySelector(`#agent-column-${agentId} .agent-input-container`);
    
    if (!container) {
        console.error('❌ Container not found');
        return;
    }
    
    // Get all matching CSS rules
    const allRules = [];
    
    for (let sheet of document.styleSheets) {
        try {
            for (let rule of sheet.cssRules || sheet.rules) {
                if (rule.selectorText && container.matches(rule.selectorText)) {
                    allRules.push({
                        selector: rule.selectorText,
                        cssText: rule.style.cssText,
                        sheet: sheet.href || 'inline'
                    });
                }
            }
        } catch (e) {
            console.warn('Cannot read stylesheet:', sheet.href, e.message);
        }
    }
    
    console.log('Found', allRules.length, 'matching CSS rules:');
    console.table(allRules);
    
    // Show computed final values
    const computed = window.getComputedStyle(container);
    console.log('\n📊 Final computed values:');
    console.table({
        height: computed.height,
        padding: computed.padding,
        overflow: computed.overflow,
        cursor: computed.cursor,
        pointerEvents: computed.pointerEvents,
        background: computed.background,
        transition: computed.transition
    });
})();
*/

// ============================================================
// COMMAND 6: Check Event Listeners (Modern browsers)
// ============================================================
// Uncomment and run this separately:
/*
(function() {
    const agentId = 3;
    
    console.log('%c👂 CHECKING EVENT LISTENERS', 'color: #58a6ff; font-weight: bold');
    
    const container = document.querySelector(`#agent-column-${agentId} .agent-input-container`);
    
    if (!container) {
        console.error('❌ Container not found');
        return;
    }
    
    // Try to get event listeners (Chrome DevTools specific)
    if (typeof getEventListeners === 'function') {
        const listeners = getEventListeners(container);
        console.log('Event listeners:', listeners);
        
        if (listeners.click) {
            console.log('Click listeners:', listeners.click);
        } else {
            console.warn('⚠️ No click listeners found!');
        }
    } else {
        console.warn('⚠️ getEventListeners() not available (only in Chrome DevTools)');
        console.log('Manual check: Look for AgentInput.setupHandlers() calls in console');
    }
})();
*/

console.log('%c📖 AGENT INPUT DEBUG COMMANDS LOADED', 'color: #3fb950; font-size: 14px; font-weight: bold');
console.log('%cℹ️ The diagnostic has auto-run above. To run other commands:', 'color: #8b949e');
console.log('%c  - Uncomment the command you want in this file', 'color: #8b949e');
console.log('%c  - Or copy-paste individual commands into console', 'color: #8b949e');
console.log('%c  - Change agentId variable to test different agents', 'color: #8b949e');
