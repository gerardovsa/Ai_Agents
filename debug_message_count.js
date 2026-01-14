/**
 * Debug script to analyze message counting in live thread
 * 
 * USAGE:
 * 1. Open browser console (F12)
 * 2. Copy/paste this entire script
 * 3. Run: debugMessageCount()
 * 
 * This will show you:
 * - Total messages in thread
 * - Breakdown by role
 * - Which messages are being counted
 * - Which are being excluded (thinking blocks)
 */

function debugMessageCount() {
    const thread = ThreadManager.threads.find(t => t.id === ThreadManager.currentThreadId);

    if (!thread) {
        console.error('No current thread found');
        return;
    }

    console.log('=== MESSAGE COUNT DEBUG ===');
    console.log('Thread ID:', thread.id);
    console.log('Thread Title:', thread.title);
    console.log('Total messages in array:', thread.messages.length);
    console.log('');

    // Analyze each message
    let userCount = 0;
    let assistantWithTextCount = 0;
    let assistantThinkingOnlyCount = 0;
    let toolCount = 0;
    let otherCount = 0;

    thread.messages.forEach((msg, index) => {
        const role = msg.role;
        const contentType = Array.isArray(msg.content) ? 'array' : typeof msg.content;

        console.log(`\nMessage ${index + 1}:`);
        console.log('  Role:', role);
        console.log('  Content type:', contentType);

        if (role === 'user') {
            userCount++;
            console.log('  ✅ COUNTED (user message)');
        } else if (role === 'assistant') {
            if (Array.isArray(msg.content)) {
                const blocks = msg.content.map(b => b.type).join(', ');
                console.log('  Content blocks:', blocks);

                const hasRealContent = msg.content.some(block =>
                    block.type === 'text' ||
                    (block.type !== 'thinking' && block.type !== 'redacted_thinking')
                );

                if (hasRealContent) {
                    assistantWithTextCount++;
                    console.log('  ✅ COUNTED (has text/tool content)');
                } else {
                    assistantThinkingOnlyCount++;
                    console.log('  ❌ EXCLUDED (thinking only)');
                }
            } else if (typeof msg.content === 'string') {
                const hasContent = msg.content.trim().length > 0;
                if (hasContent) {
                    assistantWithTextCount++;
                    console.log('  ✅ COUNTED (string content)');
                } else {
                    console.log('  ❌ EXCLUDED (empty string)');
                }
            }
        } else if (role === 'tool') {
            toolCount++;
            console.log('  ❌ EXCLUDED (tool message)');
        } else {
            otherCount++;
            console.log('  ❌ EXCLUDED (other role)');
        }
    });

    const expectedCount = userCount + assistantWithTextCount;

    console.log('\n=== SUMMARY ===');
    console.log('User messages:', userCount);
    console.log('Assistant (with text):', assistantWithTextCount);
    console.log('Assistant (thinking only):', assistantThinkingOnlyCount);
    console.log('Tool messages:', toolCount);
    console.log('Other:', otherCount);
    console.log('');
    console.log('EXPECTED COUNT:', expectedCount);
    console.log('ACTUAL DISPLAYED:', document.querySelector(`[data-thread-id="${thread.id}"] .thread-meta-item[title="Message count"]`)?.textContent?.match(/\d+/)?.[0] || 'Not found');
    console.log('');

    // Show if there's a mismatch
    const displayedCount = parseInt(document.querySelector(`[data-thread-id="${thread.id}"] .thread-meta-item[title="Message count"]`)?.textContent?.match(/\d+/)?.[0] || '0');
    if (displayedCount !== expectedCount) {
        console.error('⚠️ MISMATCH! Expected', expectedCount, 'but displayed', displayedCount);
    } else {
        console.log('✅ Count matches expectations');
    }
}

// Auto-run
console.log('Debug script loaded. Run: debugMessageCount()');
