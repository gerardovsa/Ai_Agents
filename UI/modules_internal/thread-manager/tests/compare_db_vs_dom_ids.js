/**
 * CONSOLE DIAGNOSTIC: Compare Database vs DOM - Message IDs and Roles
 * Paste this in browser console while viewing Agent 2
 */

(async function compareDatabaseVsDOM() {
    // Get thread ID from Agent 2
    const agent2ThreadId = window.MultiAgent?.sessions[2];

    if (!agent2ThreadId) {
        console.error('❌ No thread loaded in Agent 2');
        return;
    }

    console.log(`\n${'='.repeat(120)}`);
    console.log(`THREAD ${agent2ThreadId} - DATABASE vs DOM COMPARISON`);
    console.log(`${'='.repeat(120)}\n`);

    // Fetch from database
    const response = await fetch(`http://localhost:5001/api/threads/messages/get?thread_id=${agent2ThreadId}`);
    const data = await response.json();
    const dbMessages = data?.data?.messages || [];

    console.log(`📊 DATABASE: ${dbMessages.length} messages\n`);
    console.log('DATABASE MESSAGE LIST:');
    console.log('─'.repeat(120));
    console.log('| # | MESSAGE ID | ROLE      |');
    console.log('─'.repeat(120));

    dbMessages.forEach((msg, i) => {
        const num = (i + 1).toString().padStart(3);
        const id = msg.id.toString().padEnd(10);
        const role = msg.role.toUpperCase().padEnd(9);
        console.log(`| ${num} | ${id} | ${role} |`);
    });

    console.log('─'.repeat(120));
    console.log('\n');

    // Check DOM
    const container = document.getElementById('agent-messages-3');
    if (!container) {
        console.error('❌ Container #agent-messages-3 not found!');
        return;
    }

    const domMessages = container.querySelectorAll('.ai-message');
    console.log(`🖥️ DOM: ${domMessages.length} .ai-message elements found\n`);

    console.log('DOM MESSAGE LIST:');
    console.log('─'.repeat(120));
    console.log('| # | MESSAGE ID | ROLE      | HEIGHT | DISPLAY   |');
    console.log('─'.repeat(120));

    const domMessageData = [];
    domMessages.forEach((msg, i) => {
        const msgId = msg.dataset.messageId || 'NO-ID';
        const role = msg.classList.contains('user') ? 'USER' :
            msg.classList.contains('assistant') ? 'ASSISTANT' : 'UNKNOWN';
        const height = msg.offsetHeight;
        const display = window.getComputedStyle(msg).display;

        const num = (i + 1).toString().padStart(3);
        const id = msgId.padEnd(10);
        const roleStr = role.padEnd(9);
        const heightStr = (height + 'px').padEnd(6);
        const displayStr = display.padEnd(9);

        console.log(`| ${num} | ${id} | ${roleStr} | ${heightStr} | ${displayStr} |`);
        domMessageData.push({ id: msgId, role, height, display });
    });

    console.log('─'.repeat(120));
    console.log('\n');

    // Compare
    console.log(`${'='.repeat(120)}`);
    console.log('COMPARISON ANALYSIS');
    console.log(`${'='.repeat(120)}\n`);

    const dbIds = dbMessages.map(m => m.id.toString());
    const domIds = domMessageData.map(m => m.id);

    console.log(`📊 DATABASE: ${dbMessages.length} messages`);
    console.log(`🖥️ DOM:      ${domMessages.length} message elements\n`);

    // Find missing messages
    const missingFromDOM = dbMessages.filter(dbMsg => {
        return !domIds.includes(dbMsg.id.toString());
    });

    console.log(`❌ MISSING FROM DOM: ${missingFromDOM.length} messages\n`);

    if (missingFromDOM.length > 0) {
        console.log('Missing Message IDs and Roles:');
        console.log('─'.repeat(80));
        missingFromDOM.forEach(msg => {
            console.log(`  Message ID: ${msg.id} | Role: ${msg.role.toUpperCase()}`);
        });
        console.log('─'.repeat(80));
        console.log('\n');
    }

    // Count by role
    const dbUserCount = dbMessages.filter(m => m.role === 'user').length;
    const dbAssistantCount = dbMessages.filter(m => m.role === 'assistant').length;
    const domUserCount = domMessageData.filter(m => m.role === 'USER').length;
    const domAssistantCount = domMessageData.filter(m => m.role === 'ASSISTANT').length;

    console.log('ROLE BREAKDOWN:');
    console.log('─'.repeat(80));
    console.log(`DATABASE:   ${dbUserCount} USER, ${dbAssistantCount} ASSISTANT`);
    console.log(`DOM:        ${domUserCount} USER, ${domAssistantCount} ASSISTANT`);
    console.log('─'.repeat(80));
    console.log('\n');

    console.log(`❌ MISSING FROM DOM: ${dbAssistantCount - domAssistantCount} ASSISTANT messages`);
    console.log(`❌ MISSING FROM DOM: ${dbUserCount - domUserCount} USER messages`);

    console.log(`\n${'='.repeat(120)}\n`);

    // Return data for inspection
    return {
        database: dbMessages,
        dom: domMessageData,
        missing: missingFromDOM
    };
})();
