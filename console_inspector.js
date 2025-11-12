// PASTE THIS INTO BROWSER CONSOLE - It will intercept the next chat message
// and show you exactly what's being sent to the API

console.log('%c🔍 CONVERSATION HISTORY INSPECTOR ACTIVATED', 'background: #0ea5e9; color: white; padding: 10px; font-weight: bold;');
console.log('Send a message now to see the conversation history structure...\n');

// Store original sendChatMessage
const originalSendChat = window.sendChatMessage;

// Override sendChatMessage
window.sendChatMessage = async function (...args) {
    console.log('\n' + '='.repeat(80));
    console.log('%c📤 INTERCEPTED CHAT MESSAGE', 'background: #10b981; color: white; padding: 5px; font-weight: bold;');
    console.log('='.repeat(80));

    // Get current conversation
    const conv = window.conversationHistory || [];

    console.log(`\n📊 Conversation History Length: ${conv.length} messages\n`);

    conv.forEach((msg, i) => {
        console.log(`%c--- MESSAGE ${i + 1} ---`, 'color: #f59e0b; font-weight: bold;');
        console.log(`Role: ${msg.role}`);
        console.log(`Content Type: ${typeof msg.content}`);

        if (typeof msg.content === 'string') {
            console.log(`Content: "${msg.content.substring(0, 100)}..."`);
        } else if (Array.isArray(msg.content)) {
            console.log(`Content is ARRAY with ${msg.content.length} blocks:`);
            msg.content.forEach((block, j) => {
                console.log(`  Block ${j + 1}:`, block);
                if (block.type === 'thinking') {
                    console.log(`    ✅ Type: thinking`);
                    console.log(`    ${block.hasOwnProperty('thinking') ? '✅' : '❌'} Has 'thinking' field`);
                    console.log(`    ${block.hasOwnProperty('signature') ? '✅' : '❌'} Has 'signature' field`);

                    if (!block.hasOwnProperty('signature')) {
                        console.error('%c⚠️ PROBLEM FOUND: Missing signature field!', 'background: #ef4444; color: white; padding: 5px; font-weight: bold;');
                    }
                }
            });
        } else {
            console.log(`Content:`, msg.content);
        }
        console.log('');
    });

    console.log('='.repeat(80) + '\n');

    // Call original function
    return originalSendChat.apply(this, args);
};

console.log('%c✅ Inspector ready! Send a message to see the data.', 'color: #10b981; font-weight: bold;');
