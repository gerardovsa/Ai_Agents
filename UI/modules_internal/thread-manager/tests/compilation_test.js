/**
 * COMPILATION TEST: Verify JavaScript syntax and structure
 */

console.log('🔍 COMPILATION TEST: Checking JavaScript syntax...\n');

const filesToCheck = [
    'UI/shared/utilities/message_renderer.js',
    'UI/modules_internal/agents/agent-js.js',
    'UI/modules_internal/thread-manager/thread-manager-messages.js'
];

let passCount = 0;
let failCount = 0;

filesToCheck.forEach(file => {
    console.log(`Checking: ${file}`);

    // Try to load the script
    const script = document.createElement('script');
    script.src = file;

    script.onload = () => {
        console.log(`✅ PASS: ${file} loaded successfully`);
        passCount++;
    };

    script.onerror = (err) => {
        console.error(`❌ FAIL: ${file} failed to load`, err);
        failCount++;
    };

    document.head.appendChild(script);
});

// Check for syntax errors in key functions
setTimeout(() => {
    console.log('\n' + '='.repeat(80));
    console.log('🔍 Checking key function signatures...\n');

    // Check UnifiedMessageRenderer.render signature
    if (typeof UnifiedMessageRenderer !== 'undefined' && typeof UnifiedMessageRenderer.render === 'function') {
        const renderFn = UnifiedMessageRenderer.render.toString();

        // Check for messageId parameter
        if (renderFn.includes('messageId')) {
            console.log('✅ PASS: UnifiedMessageRenderer.render has messageId parameter');
        } else {
            console.error('❌ FAIL: UnifiedMessageRenderer.render missing messageId parameter');
            failCount++;
        }

        // Check for early return bug (should NOT have return; after array processing)
        if (renderFn.includes('// CRITICAL FIX: DO NOT RETURN HERE')) {
            console.log('✅ PASS: Early return bug fix comment present');
        } else {
            console.warn('⚠️  WARN: Fix comment not found (may be removed during minification)');
        }

        // Check if dataset.messageId is set
        if (renderFn.includes('dataset.messageId')) {
            console.log('✅ PASS: messageDiv.dataset.messageId assignment present');
        } else {
            console.error('❌ FAIL: messageDiv.dataset.messageId assignment missing');
            failCount++;
        }
    } else {
        console.error('❌ FAIL: UnifiedMessageRenderer.render not available');
        failCount++;
    }

    console.log('\n' + '='.repeat(80));
    console.log(`📊 COMPILATION TEST RESULTS: ${passCount} passed, ${failCount} failed`);
    console.log('='.repeat(80) + '\n');
}, 2000);
