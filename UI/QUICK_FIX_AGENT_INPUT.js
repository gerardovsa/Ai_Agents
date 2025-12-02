/**
 * QUICK FIX: Agent Input Container Expander
 * 
 * PASTE THIS ENTIRE SCRIPT INTO YOUR BROWSER CONSOLE (F12)
 * This will diagnose the issue and provide a working expand function
 */

console.log('%c🔧 AGENT INPUT QUICK FIX SCRIPT', 'color: #3fb950; font-size: 16px; font-weight: bold');
console.log('');

// Check if AgentInput exists
if (typeof AgentInput !== 'undefined') {
    console.log('%c✅ AgentInput exists', 'color: #3fb950');
    console.log('AgentInput object:', AgentInput);
    console.log('Available methods:', Object.keys(AgentInput));

    // Check if expand method exists
    if (typeof AgentInput.expand === 'function') {
        console.log('%c✅ AgentInput.expand exists', 'color: #3fb950');
    } else {
        console.log('%c❌ AgentInput.expand is missing!', 'color: #f85149; font-weight: bold');
        console.log('Available methods:', Object.keys(AgentInput));
    }
} else {
    console.log('%c❌ AgentInput is NOT defined', 'color: #f85149; font-weight: bold');
    console.log('This means agent-input-manager.js is not loaded!');
}

console.log('');
console.log('%c🔍 Checking for agent-input-manager.js...', 'color: #58a6ff');

// Check if the script is loaded
const scripts = Array.from(document.querySelectorAll('script[src]'));
const agentInputScript = scripts.find(s => s.src.includes('agent-input-manager.js'));

if (agentInputScript) {
    console.log('%c✅ agent-input-manager.js is loaded', 'color: #3fb950');
    console.log('  URL:', agentInputScript.src);
} else {
    console.log('%c❌ agent-input-manager.js is NOT loaded in the page!', 'color: #f85149; font-weight: bold');
    console.log('  Available scripts:', scripts.map(s => s.src.split('/').pop()));
}

console.log('');
console.log('%c📦 MANUAL EXPAND FUNCTION', 'color: #d29922; font-weight: bold');
console.log('Copy and paste this function to expand Agent 3 manually:');
console.log('');

// Provide a manual expand function
const manualExpandCode = `
// Manual expand function (paste this in console)
function manualExpand(agentId) {
    const container = document.querySelector(\`#agent-column-\${agentId} .agent-input-container\`);
    
    if (!container) {
        console.error('❌ Container not found for agent', agentId);
        return false;
    }
    
    console.log('📦 Container found:', container);
    console.log('📏 Current height:', container.offsetHeight + 'px');
    console.log('📝 Current classes:', container.className);
    
    // Add expanded class
    container.classList.add('expanded');
    
    // Force styles
    container.style.height = 'auto';
    container.style.padding = '20px';
    container.style.overflow = 'visible';
    
    // Show wrapper
    const wrapper = container.querySelector('.agent-input-wrapper');
    if (wrapper) {
        wrapper.style.opacity = '1';
        wrapper.style.pointerEvents = 'auto';
    }
    
    // Focus textarea
    const textarea = container.querySelector('.agent-input-textarea');
    if (textarea) {
        setTimeout(() => textarea.focus(), 100);
    }
    
    console.log('✅ Expanded!');
    console.log('📏 New height:', container.offsetHeight + 'px');
    console.log('📝 New classes:', container.className);
    
    return true;
}

// Run it for Agent 3
manualExpand(3);
`;

console.log(manualExpandCode);

console.log('');
console.log('%c🚀 AUTO-RUNNING MANUAL EXPAND...', 'color: #58a6ff; font-weight: bold');

// Auto-run the manual expand
(function manualExpand(agentId) {
    const container = document.querySelector(`#agent-column-${agentId} .agent-input-container`);

    if (!container) {
        console.error('❌ Container not found for agent', agentId);
        console.log('Trying alternative selector...');

        const alt = document.querySelector(`.agent-input-container[data-agent-id="${agentId}"]`);
        if (alt) {
            console.log('✅ Found container with alternative selector!');
            return manualExpand.call(this, agentId);
        }
        return false;
    }

    console.log('📦 Container found:', container);
    console.log('📏 Current height:', container.offsetHeight + 'px');
    console.log('📝 Current classes:', container.className);
    console.log('📊 Current computed styles:');

    const before = window.getComputedStyle(container);
    console.table({
        'height': before.height,
        'padding': before.padding,
        'overflow': before.overflow,
        'cursor': before.cursor,
        'pointer-events': before.pointerEvents
    });

    // Add expanded class
    container.classList.add('expanded');

    // Force styles (in case CSS isn't working)
    container.style.height = 'auto';
    container.style.padding = '20px';
    container.style.overflow = 'visible';
    container.style.cursor = 'default';

    // Show wrapper
    const wrapper = container.querySelector('.agent-input-wrapper');
    if (wrapper) {
        wrapper.style.opacity = '1';
        wrapper.style.pointerEvents = 'auto';
        console.log('✅ Wrapper opacity/pointer-events updated');
    } else {
        console.warn('⚠️ No .agent-input-wrapper found');
    }

    // Focus textarea
    const textarea = container.querySelector('.agent-input-textarea');
    if (textarea) {
        setTimeout(() => {
            textarea.focus();
            console.log('✅ Textarea focused');
        }, 100);
    } else {
        console.warn('⚠️ No .agent-input-textarea found');
    }

    console.log('');
    console.log('%c✅ EXPANSION COMPLETE!', 'color: #3fb950; font-weight: bold');
    console.log('📏 New height:', container.offsetHeight + 'px');
    console.log('📝 New classes:', container.className);

    console.log('📊 New computed styles:');
    const after = window.getComputedStyle(container);
    console.table({
        'height': after.height,
        'padding': after.padding,
        'overflow': after.overflow,
        'cursor': after.cursor,
        'pointer-events': after.pointerEvents
    });

    return true;
})(3);

console.log('');
console.log('%c📝 NEXT STEPS:', 'color: #d29922; font-weight: bold');
console.log('1. Check if the container expanded visually in the UI');
console.log('2. Look at the console output above to see what changed');
console.log('3. If height is still 30px, there may be CSS conflicts');
console.log('4. Share the "Current computed styles" table output with me');
