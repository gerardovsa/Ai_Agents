/**
 * 🔍 DIAGNOSTIC PATCH FOR AGENT COLUMN MESSAGE LOADING
 * 
 * Add this to browser console to debug why assistant messages aren't rendering
 * in agent column for thread 2112
 */

// Intercept UnifiedMessageRenderer.render
if (typeof window.UnifiedMessageRenderer !== 'undefined') {
    const originalRender = window.UnifiedMessageRenderer.render;

    window.UnifiedMessageRenderer.render = async function (container, role, content, options = {}) {
        const threadId = options.threadId;

        console.log(`%c[DIAGNOSTIC] UnifiedMessageRenderer.render called`, 'color: #4ec9b0; font-weight: bold;');
        console.log(`  Container:`, container);
        console.log(`  Role:`, role);
        console.log(`  Thread ID:`, threadId);
        console.log(`  Content type:`, Array.isArray(content) ? 'Array' : typeof content);

        if (Array.isArray(content)) {
            console.log(`  Content blocks (${content.length}):`, content.map(b => b?.type || 'unknown'));

            // Check if it has text blocks
            const hasText = content.some(b => b?.type === 'text');
            const hasThinking = content.some(b => b?.type === 'thinking');
            const hasToolUse = content.some(b => b?.type === 'tool_use');

            console.log(`  Has TEXT blocks: %c${hasText}`, hasText ? 'color: green' : 'color: red');
            console.log(`  Has THINKING blocks: %c${hasThinking}`, hasThinking ? 'color: cyan' : 'color: gray');
            console.log(`  Has TOOL_USE blocks: %c${hasToolUse}`, hasToolUse ? 'color: yellow' : 'color: gray');
        }

        // Call original
        const result = await originalRender.call(this, container, role, content, options);

        if (result) {
            console.log(`%c[DIAGNOSTIC] ✅ Message rendered successfully`, 'color: green; font-weight: bold;');
        } else {
            console.log(`%c[DIAGNOSTIC] ❌ Rendering returned NULL - message SKIPPED`, 'color: red; font-weight: bold;');
            console.log(`  This means message was filtered out (duplicate or tool_result-only)`);
        }

        return result;
    };

    console.log('%c✅ Diagnostic patch applied to UnifiedMessageRenderer.render', 'color: lime; font-weight: bold; font-size: 14px;');
} else {
    console.error('❌ UnifiedMessageRenderer not found!');
}

// Also intercept MessageStore.addMessage to check duplicates
if (typeof window.MessageStore !== 'undefined') {
    const originalAddMessage = window.MessageStore.addMessage;

    window.MessageStore.addMessage = function (threadId, message, options = {}) {
        const checkDuplicates = options.checkDuplicates !== false;

        console.log(`%c[DIAGNOSTIC] MessageStore.addMessage called`, 'color: #ce9178; font-weight: bold;');
        console.log(`  Thread ID:`, threadId);
        console.log(`  Message role:`, message.role);
        console.log(`  Check duplicates:`, checkDuplicates);

        const result = originalAddMessage.call(this, threadId, message, options);

        if (result._isDuplicate) {
            console.log(`%c[DIAGNOSTIC] 🔴 DUPLICATE DETECTED - Message will be SKIPPED`, 'color: orange; font-weight: bold;');
        } else {
            console.log(`%c[DIAGNOSTIC] ✅ Message added to store (ID: ${result.id})`, 'color: green;');
        }

        return result;
    };

    console.log('%c✅ Diagnostic patch applied to MessageStore.addMessage', 'color: lime; font-weight: bold; font-size: 14px;');
} else {
    console.error('❌ MessageStore not found!');
}

console.log('%c\n🔍 DIAGNOSTIC MODE ACTIVE - Now load thread 2112 in agent column\n', 'color: cyan; font-size: 16px; font-weight: bold;');
