/**
 * SMOKE TEST SUITE: Message Rendering Fixes
 * Tests all three critical fixes for message bubble rendering
 */

console.log('\n' + '='.repeat(100));
console.log('🧪 SMOKE TEST SUITE: Message Rendering Fixes');
console.log('='.repeat(100) + '\n');

// Test 1: Verify UnifiedMessageRenderer exists and has render method
console.log('Test 1: UnifiedMessageRenderer availability');
if (typeof UnifiedMessageRenderer === 'undefined') {
    console.error('❌ FAIL: UnifiedMessageRenderer not found');
} else if (typeof UnifiedMessageRenderer.render !== 'function') {
    console.error('❌ FAIL: UnifiedMessageRenderer.render is not a function');
} else {
    console.log('✅ PASS: UnifiedMessageRenderer.render available');
}

// Test 2: Array content with thinking + tool_use renders
console.log('\nTest 2: Array content (thinking + tool_use) renders to DOM');
(async () => {
    try {
        // Create test container
        const testContainer = document.createElement('div');
        testContainer.id = 'smoke-test-container';
        document.body.appendChild(testContainer);

        // Test content: thinking + text (single space) + tool_use
        const arrayContent = [
            { type: 'thinking', thinking: 'Processing request...' },
            { type: 'text', text: ' ' },  // Single space (edge case)
            { type: 'tool_use', name: 'test_tool', id: 'toolu_123', input: { param: 'value' } }
        ];

        // Render
        const result = await UnifiedMessageRenderer.render(
            testContainer,
            'assistant',
            arrayContent,
            {
                threadId: 'test-thread',
                checkDuplicates: false,
                messageId: 'test-5555'
            }
        );

        // Verify DOM element created
        const messages = testContainer.querySelectorAll('.ai-message');
        if (messages.length !== 1) {
            console.error(`❌ FAIL: Expected 1 message, found ${messages.length}`);
        } else if (!result) {
            console.error('❌ FAIL: render() returned null/undefined');
        } else {
            console.log('✅ PASS: Array content message rendered to DOM');

            // Verify message ID set
            const messageId = messages[0].dataset.messageId;
            if (messageId !== 'test-5555') {
                console.error(`❌ FAIL: Expected messageId='test-5555', got '${messageId}'`);
            } else {
                console.log('✅ PASS: Message ID correctly set on DOM element');
            }

            // Verify thinking icon present
            const thinkingIcons = messages[0].querySelectorAll('.thinking-icon');
            if (thinkingIcons.length === 0) {
                console.error('❌ FAIL: Thinking icon not rendered');
            } else {
                console.log('✅ PASS: Thinking icon rendered');
            }

            // Verify tool icon present
            const toolIcons = messages[0].querySelectorAll('.tool-icon');
            if (toolIcons.length === 0) {
                console.error('❌ FAIL: Tool icon not rendered');
            } else {
                console.log('✅ PASS: Tool icon rendered');
            }
        }

        // Cleanup
        testContainer.remove();
    } catch (err) {
        console.error('❌ FAIL: Exception thrown:', err);
    }
})();

// Test 3: String content still renders
console.log('\nTest 3: String content renders (regression test)');
(async () => {
    try {
        const testContainer = document.createElement('div');
        testContainer.id = 'smoke-test-string';
        document.body.appendChild(testContainer);

        const stringContent = 'This is a normal text message';

        const result = await UnifiedMessageRenderer.render(
            testContainer,
            'assistant',
            stringContent,
            {
                threadId: 'test-thread',
                checkDuplicates: false,
                messageId: 'test-6666'
            }
        );

        const messages = testContainer.querySelectorAll('.ai-message');
        if (messages.length !== 1) {
            console.error(`❌ FAIL: Expected 1 message, found ${messages.length}`);
        } else if (!result) {
            console.error('❌ FAIL: render() returned null/undefined');
        } else {
            console.log('✅ PASS: String content message rendered');

            const messageId = messages[0].dataset.messageId;
            if (messageId !== 'test-6666') {
                console.error(`❌ FAIL: Expected messageId='test-6666', got '${messageId}'`);
            } else {
                console.log('✅ PASS: Message ID set for string content');
            }
        }

        testContainer.remove();
    } catch (err) {
        console.error('❌ FAIL: Exception thrown:', err);
    }
})();

// Test 4: User messages with tool_result correctly skipped
console.log('\nTest 4: User messages with tool_result are skipped');
(async () => {
    try {
        const testContainer = document.createElement('div');
        testContainer.id = 'smoke-test-tool-result';
        document.body.appendChild(testContainer);

        const toolResultContent = [
            { type: 'tool_result', tool_use_id: 'toolu_123', content: 'Result data', is_error: false }
        ];

        const result = await UnifiedMessageRenderer.render(
            testContainer,
            'user',
            toolResultContent,
            {
                threadId: 'test-thread',
                checkDuplicates: false,
                messageId: 'test-7777'
            }
        );

        const messages = testContainer.querySelectorAll('.ai-message');
        if (messages.length !== 0) {
            console.error(`❌ FAIL: Expected 0 messages, found ${messages.length}`);
        } else if (result !== null) {
            console.error('❌ FAIL: render() should return null for tool_result-only messages');
        } else {
            console.log('✅ PASS: tool_result user message correctly skipped');
        }

        testContainer.remove();
    } catch (err) {
        console.error('❌ FAIL: Exception thrown:', err);
    }
})();

// Test 5: Message without messageId parameter (backwards compatibility)
console.log('\nTest 5: Message without messageId (backwards compatibility)');
(async () => {
    try {
        const testContainer = document.createElement('div');
        testContainer.id = 'smoke-test-no-id';
        document.body.appendChild(testContainer);

        const result = await UnifiedMessageRenderer.render(
            testContainer,
            'user',
            'Test message without ID',
            {
                threadId: 'test-thread',
                checkDuplicates: false
                // No messageId parameter
            }
        );

        const messages = testContainer.querySelectorAll('.ai-message');
        if (messages.length !== 1) {
            console.error(`❌ FAIL: Expected 1 message, found ${messages.length}`);
        } else {
            console.log('✅ PASS: Message rendered without messageId parameter');

            const messageId = messages[0].dataset.messageId;
            if (messageId && messageId !== 'undefined') {
                console.warn(`⚠️  WARN: messageId should be undefined, got '${messageId}'`);
            } else {
                console.log('✅ PASS: No messageId set when parameter omitted');
            }
        }

        testContainer.remove();
    } catch (err) {
        console.error('❌ FAIL: Exception thrown:', err);
    }
})();

console.log('\n' + '='.repeat(100));
console.log('🧪 SMOKE TEST SUITE COMPLETE');
console.log('='.repeat(100) + '\n');
