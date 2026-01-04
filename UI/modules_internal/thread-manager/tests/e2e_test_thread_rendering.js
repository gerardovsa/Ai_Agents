/**
 * END-TO-END TEST: Full Thread Load and Render
 * Tests complete flow from database → MessageStore → DOM
 */

console.log('\n' + '='.repeat(100));
console.log('🔄 END-TO-END TEST: Thread Load and Render');
console.log('='.repeat(100) + '\n');

(async function runE2ETest() {
    const testThreadId = '2111'; // Thread with known structure

    console.log(`Testing Thread ID: ${testThreadId}\n`);

    // Step 1: Fetch from database
    console.log('Step 1: Fetching messages from database...');
    try {
        const response = await fetch(`http://localhost:5001/api/threads/messages/get?thread_id=${testThreadId}`);
        if (!response.ok) {
            console.error(`❌ FAIL: API returned status ${response.status}`);
            return;
        }

        const data = await response.json();
        const dbMessages = data?.data?.messages || [];
        console.log(`✅ PASS: Fetched ${dbMessages.length} messages from database`);

        if (dbMessages.length === 0) {
            console.error('❌ FAIL: No messages returned from database');
            return;
        }

        // Step 2: Load into MessageStore
        console.log('\nStep 2: Loading messages into MessageStore...');
        if (typeof window.MessageStore === 'undefined') {
            console.error('❌ FAIL: MessageStore not available');
            return;
        }

        for (const msg of dbMessages) {
            await window.MessageStore.addMessage(testThreadId, msg, {
                checkDuplicates: false,
                silent: true
            });
        }

        const storedMessages = window.MessageStore.getMessages(testThreadId);
        console.log(`✅ PASS: Loaded ${storedMessages.length} messages into MessageStore`);

        if (storedMessages.length !== dbMessages.length) {
            console.error(`❌ FAIL: MessageStore count mismatch (DB: ${dbMessages.length}, Store: ${storedMessages.length})`);
            return;
        }

        // Step 3: Render to DOM
        console.log('\nStep 3: Rendering messages to DOM...');
        const testContainer = document.createElement('div');
        testContainer.id = 'e2e-test-container';
        testContainer.style.cssText = 'position: absolute; top: -9999px; left: -9999px;';
        document.body.appendChild(testContainer);

        let renderedCount = 0;
        let skippedCount = 0;
        let errorCount = 0;

        for (const [index, msg] of storedMessages.entries()) {
            try {
                const rendered = await UnifiedMessageRenderer.render(
                    testContainer,
                    msg.role,
                    msg.content,
                    {
                        threadId: testThreadId,
                        syncToBackend: false,
                        scrollToBottom: false,
                        createdAt: msg.created_at,
                        checkDuplicates: false,
                        messageId: msg.id
                    }
                );

                if (rendered) {
                    renderedCount++;
                } else {
                    skippedCount++;
                }
            } catch (err) {
                console.error(`Error rendering message ${index + 1}:`, err);
                errorCount++;
            }
        }

        const domMessages = testContainer.querySelectorAll('.ai-message');
        console.log(`✅ PASS: Rendered ${renderedCount} messages, skipped ${skippedCount}, errors ${errorCount}`);
        console.log(`✅ PASS: Found ${domMessages.length} DOM elements`);

        if (renderedCount !== domMessages.length) {
            console.error(`❌ FAIL: Mismatch between rendered count (${renderedCount}) and DOM elements (${domMessages.length})`);
        }

        // Step 4: Verify message IDs in DOM
        console.log('\nStep 4: Verifying message IDs...');
        let missingIdCount = 0;
        let correctIdCount = 0;

        domMessages.forEach((elem, i) => {
            const msgId = elem.dataset.messageId;
            if (!msgId || msgId === 'undefined') {
                missingIdCount++;
                console.error(`❌ DOM element ${i + 1} missing messageId`);
            } else {
                correctIdCount++;
            }
        });

        if (missingIdCount === 0) {
            console.log(`✅ PASS: All ${correctIdCount} DOM elements have message IDs`);
        } else {
            console.error(`❌ FAIL: ${missingIdCount} DOM elements missing message IDs`);
        }

        // Step 5: Verify message order
        console.log('\nStep 5: Verifying message order...');
        const renderedMessages = storedMessages.filter(msg => {
            // Skip tool_result user messages (they're not rendered)
            if (msg.role === 'user' && Array.isArray(msg.content)) {
                return !msg.content.every(b => b.type === 'tool_result');
            }
            return true;
        });

        if (domMessages.length === renderedMessages.length) {
            console.log(`✅ PASS: DOM count matches expected rendered count`);
        } else {
            console.error(`❌ FAIL: Expected ${renderedMessages.length} rendered, found ${domMessages.length} in DOM`);
        }

        // Step 6: Forward trace (input → render)
        console.log('\nStep 6: FORWARD TRACE (Database → MessageStore → DOM)...');
        console.log('─'.repeat(100));
        console.log('| DB MSG ID | ROLE      | CONTENT TYPE | IN STORE? | RENDERED? | DOM ID MATCH? |');
        console.log('─'.repeat(100));

        dbMessages.slice(0, 10).forEach(dbMsg => {
            const inStore = storedMessages.find(m => m.id === dbMsg.id);
            const inDom = Array.from(domMessages).find(elem => elem.dataset.messageId === dbMsg.id.toString());

            const dbId = dbMsg.id.toString().padEnd(9);
            const role = dbMsg.role.toUpperCase().padEnd(9);
            const contentType = (Array.isArray(dbMsg.content) ? 'Array' : 'String').padEnd(12);
            const inStoreStr = (inStore ? '✓' : '✗').padEnd(9);
            const renderedStr = (inDom ? '✓' : '✗').padEnd(9);
            const idMatch = (inDom && inDom.dataset.messageId === dbMsg.id.toString() ? '✓' : '✗').padEnd(13);

            console.log(`| ${dbId} | ${role} | ${contentType} | ${inStoreStr} | ${renderedStr} | ${idMatch} |`);
        });
        console.log('─'.repeat(100));

        // Step 7: Backward trace (DOM → MessageStore → Database)
        console.log('\nStep 7: BACKWARD TRACE (DOM → MessageStore → Database)...');
        console.log('─'.repeat(100));
        console.log('| DOM INDEX | DOM MSG ID | IN STORE? | IN DB?    | ROLE      |');
        console.log('─'.repeat(100));

        Array.from(domMessages).slice(0, 10).forEach((elem, i) => {
            const domId = elem.dataset.messageId;
            const inStore = storedMessages.find(m => m.id.toString() === domId);
            const inDb = dbMessages.find(m => m.id.toString() === domId);

            const index = (i + 1).toString().padEnd(9);
            const id = (domId || 'NO-ID').padEnd(10);
            const inStoreStr = (inStore ? '✓' : '✗').padEnd(9);
            const inDbStr = (inDb ? '✓' : '✗').padEnd(9);
            const role = (elem.classList.contains('user') ? 'USER' : 'ASSISTANT').padEnd(9);

            console.log(`| ${index} | ${id} | ${inStoreStr} | ${inDbStr} | ${role} |`);
        });
        console.log('─'.repeat(100));

        // Cleanup
        testContainer.remove();

        // Final summary
        console.log('\n' + '='.repeat(100));
        console.log('📊 FINAL SUMMARY:');
        console.log('─'.repeat(100));
        console.log(`Database Messages:    ${dbMessages.length}`);
        console.log(`MessageStore:         ${storedMessages.length}`);
        console.log(`Rendered to DOM:      ${renderedCount}`);
        console.log(`Skipped (expected):   ${skippedCount}`);
        console.log(`DOM Elements:         ${domMessages.length}`);
        console.log(`With Message IDs:     ${correctIdCount}`);
        console.log(`Missing IDs:          ${missingIdCount}`);
        console.log('─'.repeat(100));

        if (errorCount === 0 && missingIdCount === 0 && renderedCount === domMessages.length) {
            console.log('✅ END-TO-END TEST: PASSED');
        } else {
            console.log('❌ END-TO-END TEST: FAILED');
        }
        console.log('='.repeat(100) + '\n');

    } catch (err) {
        console.error('❌ FATAL ERROR in E2E test:', err);
    }
})();
