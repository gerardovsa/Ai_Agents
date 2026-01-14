/**
 * Thread ID System Analysis and Test
 * 
 * FINDINGS:
 * ========
 * 
 * DATABASE STRUCTURE:
 * - threads table has TWO ID columns:
 *   1. id (INTEGER, PRIMARY KEY, auto-increment) - Database internal ID
 *   2. thread_slug (TEXT) - Frontend-facing timestamp ID
 * 
 * - messages table has:
 *   - thread_id (INTEGER, FOREIGN KEY to threads.id)
 * 
 * BACKEND BEHAVIOR:
 * ================
 * 
 * 1. SAVE MESSAGES (/api/threads/messages/save):
 *    - Receives: thread_id = "1763557233913" (thread_slug)
 *    - Queries: WHERE thread_slug = '1763557233913'
 *    - Gets: internal ID (e.g., 125)
 *    - Inserts: INTO messages (thread_id=125, ...)
 *    - Result: Messages saved with correct internal ID
 * 
 * 2. GET MESSAGES (/api/threads/messages/get):
 *    - Receives: thread_id = "1763557233913" (thread_slug)
 *    - Queries: 
 *      SELECT m.* FROM messages m
 *      JOIN threads t ON m.thread_id = t.id
 *      WHERE t.thread_slug = '1763557233913'
 *    - Result: Should return all messages
 * 
 * SYSTEM IS CORRECT:
 * ==================
 * Both endpoints use the same pattern:
 * - Frontend sends thread_slug (e.g., "1763557233913")
 * - Backend converts to internal ID via JOIN
 * - Operations use internal ID for foreign keys
 * 
 * THE ISSUE:
 * ==========
 * The logs show "messages_saved": 1 instead of 4+
 * This means the SAVE logic is skipping existing messages correctly,
 * but the frontend might be sending duplicate save requests.
 * 
 * VERIFICATION NEEDED:
 * ===================
 * 1. Check if messages are actually in database
 * 2. Check if GET query returns all messages
 * 3. Verify message deduplication logic
 */

const axios = require('axios');

const BASE_URL = 'http://localhost:5001';
const TEST_USER_ID = 14;

async function testThreadIdSystem() {
    console.log('\n=== THREAD ID SYSTEM TEST ===\n');

    try {
        // 1. Create a new thread
        console.log('1. Creating new thread...');
        const createResponse = await axios.post(`${BASE_URL}/api/threads/create`, {
            user_id: TEST_USER_ID,
            title: 'Thread ID System Test',
            agent_id: 'prime'
        });

        const thread = createResponse.data.thread;
        const threadSlug = thread.id; // This is the thread_slug (timestamp)
        console.log(`   ✅ Created thread: ${threadSlug}`);
        console.log(`   Thread object:`, JSON.stringify(thread, null, 2));

        // 2. Save first batch of messages
        console.log('\n2. Saving first batch (2 messages)...');
        const messages1 = [
            { role: 'user', content: 'Hello, this is message 1' },
            { role: 'assistant', content: 'This is response 1' }
        ];

        const saveResponse1 = await axios.post(`${BASE_URL}/api/threads/messages/save`, {
            thread_id: threadSlug,
            user_id: TEST_USER_ID,
            messages: messages1
        });

        console.log(`   ✅ Save response:`, saveResponse1.data);
        console.log(`   Expected: messages_saved = 2`);
        console.log(`   Actual: messages_saved = ${saveResponse1.data.messages_saved}`);

        // 3. Get messages after first save
        console.log('\n3. Getting messages after first save...');
        const getResponse1 = await axios.get(`${BASE_URL}/api/threads/messages/get`, {
            params: { thread_id: threadSlug }
        });

        console.log(`   ✅ Retrieved ${getResponse1.data.count} messages`);
        console.log(`   Expected: 2 messages`);
        console.log(`   Messages:`, JSON.stringify(getResponse1.data.messages, null, 2));

        // 4. Save second batch (should append, not duplicate)
        console.log('\n4. Saving second batch (4 total messages, 2 new)...');
        const messages2 = [
            { role: 'user', content: 'Hello, this is message 1' }, // Duplicate
            { role: 'assistant', content: 'This is response 1' },   // Duplicate
            { role: 'user', content: 'Hello, this is message 2' },  // NEW
            { role: 'assistant', content: 'This is response 2' }    // NEW
        ];

        const saveResponse2 = await axios.post(`${BASE_URL}/api/threads/messages/save`, {
            thread_id: threadSlug,
            user_id: TEST_USER_ID,
            messages: messages2
        });

        console.log(`   ✅ Save response:`, saveResponse2.data);
        console.log(`   Expected: messages_saved = 2 (only new messages)`);
        console.log(`   Actual: messages_saved = ${saveResponse2.data.messages_saved}`);

        // 5. Get messages after second save
        console.log('\n5. Getting messages after second save...');
        const getResponse2 = await axios.get(`${BASE_URL}/api/threads/messages/get`, {
            params: { thread_id: threadSlug }
        });

        console.log(`   ✅ Retrieved ${getResponse2.data.count} messages`);
        console.log(`   Expected: 4 messages total`);
        console.log(`   Messages:`, JSON.stringify(getResponse2.data.messages.map(m => ({
            role: m.role,
            content: m.content.substring(0, 50)
        })), null, 2));

        // 6. Verify thread_slug vs internal ID
        console.log('\n6. Verifying ID mapping...');
        console.log(`   thread_slug (frontend ID): ${threadSlug}`);
        console.log(`   Database query uses: WHERE t.thread_slug = '${threadSlug}'`);
        console.log(`   Messages linked via: m.thread_id = t.id (internal integer ID)`);

        // 7. Test with wrong thread_slug (should return empty)
        console.log('\n7. Testing with invalid thread_slug...');
        const getResponse3 = await axios.get(`${BASE_URL}/api/threads/messages/get`, {
            params: { thread_id: '9999999999999' }
        });

        console.log(`   ✅ Retrieved ${getResponse3.data.count} messages (should be 0)`);

        // SUMMARY
        console.log('\n=== TEST SUMMARY ===');
        console.log(`✅ Thread created with slug: ${threadSlug}`);
        console.log(`✅ First save: ${saveResponse1.data.messages_saved} messages (expected: 2)`);
        console.log(`✅ Second save: ${saveResponse2.data.messages_saved} messages (expected: 2)`);
        console.log(`✅ Final count: ${getResponse2.data.count} messages (expected: 4)`);

        const pass1 = saveResponse1.data.messages_saved === 2;
        const pass2 = saveResponse2.data.messages_saved === 2;
        const pass3 = getResponse2.data.count === 4;

        if (pass1 && pass2 && pass3) {
            console.log('\n🎉 ALL TESTS PASSED! System working correctly.');
        } else {
            console.log('\n⚠️ SOME TESTS FAILED:');
            if (!pass1) console.log('   ❌ First save: expected 2, got', saveResponse1.data.messages_saved);
            if (!pass2) console.log('   ❌ Second save: expected 2, got', saveResponse2.data.messages_saved);
            if (!pass3) console.log('   ❌ Final count: expected 4, got', getResponse2.data.count);
        }

    } catch (error) {
        console.error('\n❌ TEST FAILED:', error.message);
        if (error.response) {
            console.error('   Response:', error.response.data);
        }
    }
}

// Run the test
testThreadIdSystem();
