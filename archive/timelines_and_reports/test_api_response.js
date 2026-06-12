// TEST: Fetch messages for thread 2112 directly from API
// Run this in browser console to see EXACT response

const threadId = 2112;
const url = `http://localhost:5001/api/threads/messages/get?thread_id=${threadId}`;

console.log(`🔍 Fetching: ${url}`);

fetch(url)
    .then(response => response.json())
    .then(data => {
        console.log('\n📦 API RESPONSE:');
        console.log(data);

        const messages = data?.data?.messages || [];
        console.log(`\n📊 STATISTICS:`);
        console.log(`Total messages: ${messages.length}`);

        const userCount = messages.filter(m => m.role === 'user').length;
        const assistantCount = messages.filter(m => m.role === 'assistant').length;
        console.log(`User messages: ${userCount}`);
        console.log(`Assistant messages: ${assistantCount}`);

        console.log(`\n📝 MESSAGE IDS:`);
        messages.forEach(msg => {
            console.log(`  [${msg.id}] ${msg.role}`);
        });

        console.log(`\n✅ Full API response saved to window._testResponse`);
        window._testResponse = data;
    })
    .catch(error => {
        console.error('❌ ERROR:', error);
    });
