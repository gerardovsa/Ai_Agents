// Test file to verify auto separator logic for thinking blocks
// This simulates what happens in the browser when streaming thinking events

/**
 * Scenario: Agent thinks → uses tool → thinks again
 * Expected: Separator appears between the two thinking blocks
 */

function testThinkingSeparator() {
    console.log('\n=== TESTING AUTO SEPARATOR FOR THINKING BLOCKS ===\n');
    
    // Simulate a thinking bubble object
    const thinkingBubble = {
        _fullThinkingText: ''
    };
    
    // Simulate streaming events
    const events = [
        { type: 'thinking', delta_type: 'start', content: 'Let me analyze the problem...' },
        { type: 'thinking', delta_type: 'delta', content: ' I need to check the data.' },
        { type: 'thinking', delta_type: 'delta', content: ' Now I understand.' },
        // Tool use happens here (different event type)
        { type: 'tool_use', tool_name: 'calculator' },
        // New thinking block
        { type: 'thinking', delta_type: 'start', content: 'Now let me verify the result...' },
        { type: 'thinking', delta_type: 'delta', content: ' Yes, that looks correct.' },
    ];
    
    let lastEventType = null;
    
    // Process events
    for (const data of events) {
        if (data.type === 'thinking') {
            const thinkingText = data.content || '';
            
            // SIMULATE THE FIX
            if (data.delta_type === 'start' && thinkingBubble._fullThinkingText.trim()) {
                thinkingBubble._fullThinkingText += '\n\n---\n\n';
                console.log('🔄 [THINKING] New thinking block detected, added visual separator');
            }
            
            thinkingBubble._fullThinkingText += thinkingText;
            lastEventType = 'thinking';
            
            console.log(`[${data.delta_type}] "${thinkingText}"`);
        } else if (data.type === 'tool_use') {
            lastEventType = 'tool_use';
            console.log(`⚙️  [${data.type}] ${data.tool_name}`);
        }
    }
    
    console.log('\n=== FINAL THINKING CONTENT ===\n');
    console.log(thinkingBubble._fullThinkingText);
    
    console.log('\n=== VERIFICATION ===\n');
    
    // Check if separator is present
    const hasSeparator = thinkingBubble._fullThinkingText.includes('\n\n---\n\n');
    console.log(`✓ Separator present: ${hasSeparator ? 'YES ✅' : 'NO ❌'}`);
    
    // Check parts
    const parts = thinkingBubble._fullThinkingText.split('\n\n---\n\n');
    console.log(`✓ Number of thinking sections: ${parts.length}`);
    console.log(`✓ First section: "${parts[0].substring(0, 50)}..."`);
    if (parts.length > 1) {
        console.log(`✓ Second section: "${parts[1].substring(0, 50)}..."`);
    }
    
    console.log('\n' + '='.repeat(50) + '\n');
    
    return hasSeparator && parts.length === 2;
}

// Run test
const result = testThinkingSeparator();
console.log(`TEST RESULT: ${result ? '✅ PASSED' : '❌ FAILED'}\n`);
