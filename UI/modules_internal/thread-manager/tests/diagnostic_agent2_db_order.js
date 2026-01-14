/**
 * DIAGNOSTIC: Show exact message order from Supabase database for Agent 2
 * This shows what the CORRECT order SHOULD be
 */

async function showAgent2DatabaseOrder() {
    // Find thread ID for Agent 2
    const agent2ThreadId = window.MultiAgent?.sessions[2];

    if (!agent2ThreadId) {
        console.error('❌ No thread loaded in Agent 2');
        console.log('Current MultiAgent sessions:', window.MultiAgent?.sessions);
        return;
    }

    console.log(`\n🔍 FETCHING DATABASE ORDER FOR AGENT 2`);
    console.log(`Thread ID: ${agent2ThreadId}\n`);
    console.log('='.repeat(100));

    // Fetch from Supabase via API
    const response = await fetch(`http://localhost:5001/api/threads/messages/get?thread_id=${agent2ThreadId}`);
    const data = await response.json();
    const messages = data?.data?.messages || [];

    console.log(`\n📊 TOTAL MESSAGES IN DATABASE: ${messages.length}\n`);
    console.log('='.repeat(100));
    console.log('| # | ID   | ROLE      | CONTENT PREVIEW (first 80 chars)');
    console.log('='.repeat(100));

    messages.forEach((msg, index) => {
        // Extract preview
        let preview = '';

        if (typeof msg.content === 'string') {
            preview = msg.content.substring(0, 80).replace(/\n/g, ' ');
        } else if (Array.isArray(msg.content)) {
            // Show block types
            const blockTypes = msg.content.map(b => b.type || 'unknown').join(', ');

            // Try to find text content
            const textBlocks = msg.content.filter(b => b.type === 'text' && b.text);
            if (textBlocks.length > 0) {
                preview = textBlocks[0].text.substring(0, 80).replace(/\n/g, ' ');
            } else {
                preview = `[${msg.content.length} blocks: ${blockTypes}]`;
            }
        } else {
            preview = '[complex object]';
        }

        // Format output
        const num = (index + 1).toString().padStart(3);
        const id = msg.id.toString().padEnd(5);
        const role = msg.role.toUpperCase().padEnd(9);

        console.log(`| ${num} | ${id} | ${role} | ${preview}`);
    });

    console.log('='.repeat(100));

    // Count by role
    const userCount = messages.filter(m => m.role === 'user').length;
    const assistantCount = messages.filter(m => m.role === 'assistant').length;

    console.log(`\n📈 SUMMARY:`);
    console.log(`   USER messages: ${userCount}`);
    console.log(`   ASSISTANT messages: ${assistantCount}`);
    console.log(`   TOTAL: ${messages.length}\n`);

    // Show expected pattern
    console.log('🎯 EXPECTED PATTERN (first 20 messages):');
    messages.slice(0, 20).forEach((msg, i) => {
        console.log(`   ${(i + 1).toString().padStart(2)}. ${msg.role.toUpperCase()}`);
    });

    console.log('\n✅ This is the CORRECT order from database!\n');

    return messages;
}

// Auto-run
showAgent2DatabaseOrder();
