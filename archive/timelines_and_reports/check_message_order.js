// DIAGNOSTIC: Check exact order of messages from API vs DOM
console.log('🔍 CHECKING MESSAGE ORDER FOR THREAD 2112...\n');

const threadId = 2112;

// Step 1: Fetch from API
fetch(`http://localhost:5001/api/threads/messages/get?thread_id=${threadId}`)
    .then(response => response.json())
    .then(data => {
        const apiMessages = data?.data?.messages || [];

        console.log('📡 API ORDER (first 40 messages):');
        apiMessages.slice(0, 40).forEach((msg, i) => {
            console.log(`  ${i + 1}. [ID:${msg.id}] ${msg.role.toUpperCase()}`);
        });

        // Step 2: Check MessageStore
        console.log('\n📦 MessageStore ORDER:');
        const storeMessages = window.MessageStore?.getMessages(threadId) || [];
        storeMessages.slice(0, 40).forEach((msg, i) => {
            console.log(`  ${i + 1}. [ID:${msg.id}] ${msg.role.toUpperCase()}`);
        });

        // Step 3: Check DOM rendering order
        console.log('\n🎨 DOM RENDER ORDER:');
        const container = document.querySelector('#agent-column-2 .agent-messages-container');
        const domMessages = container?.querySelectorAll('.ai-message') || [];
        Array.from(domMessages).forEach((msg, i) => {
            const isUser = msg.classList.contains('user');
            const isAssistant = msg.classList.contains('assistant');
            const role = isUser ? 'USER' : isAssistant ? 'ASSISTANT' : 'UNKNOWN';
            console.log(`  ${i + 1}. ${role}`);
        });

        // Step 4: Compare
        console.log('\n🔍 ANALYSIS:');
        console.log(`API messages: ${apiMessages.length}`);
        console.log(`MessageStore: ${storeMessages.length}`);
        console.log(`DOM rendered: ${domMessages.length}`);

        // Check if orders match
        let apiOrder = apiMessages.slice(0, 35).map(m => m.role).join(',');
        let storeOrder = storeMessages.slice(0, 35).map(m => m.role).join(',');
        let domOrder = Array.from(domMessages).map(msg => {
            return msg.classList.contains('user') ? 'user' : 'assistant';
        }).join(',');

        console.log('\n📊 ORDER COMPARISON (first 35):');
        console.log('API:   ', apiOrder);
        console.log('Store: ', storeOrder);
        console.log('DOM:   ', domOrder);

        if (apiOrder === storeOrder && storeOrder === domOrder) {
            console.log('\n✅ All orders MATCH!');
        } else {
            console.log('\n❌ ORDER MISMATCH DETECTED!');
            if (apiOrder !== storeOrder) {
                console.log('   ⚠️ MessageStore is reordering messages!');
            }
            if (storeOrder !== domOrder) {
                console.log('   ⚠️ DOM rendering is reordering messages!');
            }
        }
    })
    .catch(error => {
        console.error('❌ ERROR:', error);
    });
