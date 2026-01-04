/**
 * DIAGNOSTIC: Compare Database Messages vs UI Rendering
 * Run this in browser console to see exact differences
 */

async function compareDatabaseVsUI(threadId) {
    console.log(`\n🔍 DIAGNOSTIC: Comparing Database vs UI for thread ${threadId}\n`);

    // ========================================
    // 1. FETCH FROM DATABASE (via API)
    // ========================================
    console.log('📡 Step 1: Fetching from DATABASE via API...\n');

    const apiResponse = await fetch(`http://localhost:5001/api/threads/messages/get?thread_id=${threadId}`);
    const apiData = await apiResponse.json();
    const dbMessages = apiData?.data?.messages || [];

    console.log(`📊 DATABASE: ${dbMessages.length} messages found\n`);
    console.log('='.repeat(80));

    dbMessages.forEach((msg, i) => {
        // Extract first 50 chars of content
        let preview = '';
        if (typeof msg.content === 'string') {
            preview = msg.content.substring(0, 50);
        } else if (Array.isArray(msg.content)) {
            const textBlocks = msg.content.filter(b => b.type === 'text' || b.text);
            if (textBlocks.length > 0) {
                const firstText = textBlocks[0].text || textBlocks[0].content || '';
                preview = firstText.substring(0, 50);
            } else {
                preview = `[${msg.content.length} blocks: ${msg.content.map(b => b.type).join(', ')}]`;
            }
        } else {
            preview = JSON.stringify(msg.content).substring(0, 50);
        }

        console.log(`${(i + 1).toString().padStart(3)}. [ID:${msg.id}] ${msg.role.toUpperCase().padEnd(10)} | ${preview}...`);
    });

    // ========================================
    // 2. CHECK MESSAGESTORE
    // ========================================
    console.log('\n' + '='.repeat(80));
    console.log('📦 Step 2: Checking MessageStore (in-memory cache)...\n');

    const storeMessages = window.MessageStore?.getMessages(threadId) || [];

    console.log(`📊 MESSAGESTORE: ${storeMessages.length} messages cached\n`);
    console.log('='.repeat(80));

    storeMessages.forEach((msg, i) => {
        let preview = '';
        if (typeof msg.content === 'string') {
            preview = msg.content.substring(0, 50);
        } else if (Array.isArray(msg.content)) {
            const textBlocks = msg.content.filter(b => b.type === 'text' || b.text);
            if (textBlocks.length > 0) {
                const firstText = textBlocks[0].text || textBlocks[0].content || '';
                preview = firstText.substring(0, 50);
            } else {
                preview = `[${msg.content.length} blocks: ${msg.content.map(b => b.type).join(', ')}]`;
            }
        } else {
            preview = JSON.stringify(msg.content).substring(0, 50);
        }

        console.log(`${(i + 1).toString().padStart(3)}. [ID:${msg.id}] ${msg.role.toUpperCase().padEnd(10)} | ${preview}...`);
    });

    // ========================================
    // 3. CHECK DOM RENDERING
    // ========================================
    console.log('\n' + '='.repeat(80));
    console.log('🎨 Step 3: Checking DOM (what user sees)...\n');

    // Find agent column for this thread
    let container = null;
    for (let i = 1; i <= 8; i++) {
        const agentContainer = document.querySelector(`#agent-messages-${i}`);
        if (agentContainer && window.MultiAgent?.sessions[i] === threadId) {
            container = agentContainer;
            console.log(`Found in Agent ${i}`);
            break;
        }
    }

    if (!container) {
        // Check Prime
        const primeContainer = document.getElementById('ai-chat-messages');
        if (primeContainer && window.AppState?.sessionId === threadId) {
            container = primeContainer;
            console.log('Found in AI Prime');
        }
    }

    if (!container) {
        console.error('❌ Thread not currently displayed in any column!');
        return;
    }

    const domMessages = container.querySelectorAll('.ai-message');

    console.log(`📊 DOM: ${domMessages.length} messages rendered\n`);
    console.log('='.repeat(80));

    domMessages.forEach((msgEl, i) => {
        const role = msgEl.classList.contains('user') ? 'USER' : 'ASSISTANT';
        const contentEl = msgEl.querySelector('.ai-message-content');
        const preview = contentEl ? contentEl.textContent.substring(0, 50) : '[no content]';

        console.log(`${(i + 1).toString().padStart(3)}. ${role.padEnd(10)} | ${preview}...`);
    });

    // ========================================
    // 4. COMPARISON ANALYSIS
    // ========================================
    console.log('\n' + '='.repeat(80));
    console.log('🔍 Step 4: COMPARISON ANALYSIS\n');

    console.log(`Database:     ${dbMessages.length} messages`);
    console.log(`MessageStore: ${storeMessages.length} messages`);
    console.log(`DOM Rendered: ${domMessages.length} messages\n`);

    // Find missing messages
    const dbIds = new Set(dbMessages.map(m => m.id));
    const storeIds = new Set(storeMessages.map(m => m.id));
    const domCount = domMessages.length;

    // Messages in DB but not in MessageStore
    const missingInStore = dbMessages.filter(m => !storeIds.has(m.id));
    if (missingInStore.length > 0) {
        console.log(`❌ ${missingInStore.length} messages in DATABASE but NOT in MessageStore:`);
        missingInStore.forEach(m => {
            let preview = typeof m.content === 'string' ? m.content.substring(0, 50) : '[complex]';
            console.log(`   [ID:${m.id}] ${m.role}: ${preview}...`);
        });
    } else {
        console.log('✅ All database messages are in MessageStore');
    }

    console.log('');

    // Check DOM vs MessageStore count
    const skippedCount = storeMessages.length - domCount;
    if (skippedCount > 0) {
        console.log(`⚠️  ${skippedCount} messages in MessageStore but NOT rendered in DOM`);
        console.log('    (Likely tool_result-only messages - this is EXPECTED)');
    } else if (skippedCount < 0) {
        console.log(`❌ DOM has MORE messages than MessageStore (${Math.abs(skippedCount)} extra)`);
    } else {
        console.log('✅ DOM message count matches MessageStore');
    }

    // ========================================
    // 5. IDENTIFY PROBLEM MESSAGES
    // ========================================
    if (missingInStore.length > 0) {
        console.log('\n' + '='.repeat(80));
        console.log('🚨 PROBLEM IDENTIFIED: Messages not loaded into MessageStore\n');
        console.log('Missing message details:');

        missingInStore.forEach((msg, i) => {
            console.log(`\n${i + 1}. Message ID: ${msg.id}`);
            console.log(`   Role: ${msg.role}`);
            console.log(`   Content type: ${typeof msg.content}`);
            if (Array.isArray(msg.content)) {
                console.log(`   Content blocks: ${msg.content.map(b => b.type).join(', ')}`);
                msg.content.forEach((block, j) => {
                    if (block.type === 'text' && block.text) {
                        console.log(`   Block ${j} text: "${block.text.substring(0, 100)}..."`);
                    }
                });
            }
        });
    }

    console.log('\n' + '='.repeat(80));
    console.log('✅ Diagnostic complete!\n');
}

// Auto-run for thread in Agent 3 (or specify thread ID)
const threadId = window.MultiAgent?.sessions[3] || '1767424131479';
console.log(`Running diagnostic for thread: ${threadId}`);
compareDatabaseVsUI(threadId);
