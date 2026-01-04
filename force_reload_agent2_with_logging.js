/**
 * 🔍 FORCE RELOAD AGENT 2 (BRAVO) WITH THREAD 2112 - CONSOLE LOGGER
 * 
 * Paste this into the browser console on the main app page.
 * It will:
 * 1. Clear any existing logs
 * 2. Capture all console output
 * 3. Force reload thread 2112 into Agent 2 (Bravo)
 * 4. Display captured logs with statistics
 */

(async function () {
    // ============================================================
    // SETUP CONSOLE CAPTURE
    // ============================================================
    const capturedLogs = [];
    let renderCount = 0;
    let assistantMessageCount = 0;
    let userMessageCount = 0;
    let skipCount = 0;
    let duplicateCount = 0;

    // Backup original console methods
    const originalLog = console.log;
    const originalWarn = console.warn;
    const originalError = console.error;

    // Intercept console.log
    console.log = function (...args) {
        const message = args.map(a =>
            typeof a === 'object' ? JSON.stringify(a, null, 2) : String(a)
        ).join(' ');

        capturedLogs.push({ type: 'LOG', message, timestamp: new Date().toISOString() });

        // Track statistics
        if (message.includes('Rendering message') || message.includes('Rendered')) renderCount++;
        if (message.includes('role=assistant') || message.includes("role: 'assistant'")) assistantMessageCount++;
        if (message.includes('role=user') || message.includes("role: 'user'")) userMessageCount++;
        if (message.includes('skipped') || message.includes('SKIPPED')) skipCount++;
        if (message.includes('duplicate') || message.includes('Duplicate')) duplicateCount++;

        originalLog.apply(console, args);
    };

    // Intercept console.warn
    console.warn = function (...args) {
        const message = args.map(a =>
            typeof a === 'object' ? JSON.stringify(a, null, 2) : String(a)
        ).join(' ');

        capturedLogs.push({ type: 'WARN', message, timestamp: new Date().toISOString() });
        originalWarn.apply(console, args);
    };

    // Intercept console.error
    console.error = function (...args) {
        const message = args.map(a =>
            typeof a === 'object' ? JSON.stringify(a, null, 2) : String(a)
        ).join(' ');

        capturedLogs.push({ type: 'ERROR', message, timestamp: new Date().toISOString() });
        originalError.apply(console, args);
    };

    console.log('%c🔍 CONSOLE CAPTURE ACTIVE', 'color: lime; font-size: 16px; font-weight: bold;');
    console.log('Capturing all logs during Agent 2 (Bravo) thread reload...\n');

    // ============================================================
    // FORCE RELOAD AGENT 2 WITH THREAD 2112
    // ============================================================

    const agentId = 2; // Agent 2 = Bravo
    const threadId = 2112; // "In House Tool Guide"

    console.log(`%c📍 TARGET: Agent ${agentId} (Bravo) | Thread ${threadId}`, 'color: cyan; font-size: 14px; font-weight: bold;');
    console.log('');

    // Step 1: Clear MessageStore for thread 2112
    if (typeof window.MessageStore !== 'undefined') {
        console.log('🗑️ Clearing MessageStore for thread 2112...');
        window.MessageStore.clearThread(threadId);
        console.log('✅ MessageStore cleared');
    } else {
        console.warn('⚠️ MessageStore not available');
    }

    // Step 2: Clear Agent 2 UI
    console.log('🗑️ Clearing Agent 2 message container...');
    const messagesDiv = document.querySelector(`#agent-column-${agentId} .agent-messages-container`);
    if (messagesDiv) {
        messagesDiv.innerHTML = '';
        console.log('✅ Agent 2 messages cleared');
    } else {
        console.error(`❌ Agent ${agentId} message container not found!`);
        console.log('Trying alternative selector...');
        const altDiv = document.querySelector(`#agent-column-${agentId}`);
        if (altDiv) {
            console.log('Found agent column, searching for messages container inside...');
            const container = altDiv.querySelector('.agent-messages-container');
            console.log('Container found:', container);
        }
        return;
    }

    // Step 3: Skip metadata fetch, go straight to loading messages
    console.log('📡 Skipping metadata fetch, loading messages directly...');

    // Step 4: Load messages from backend
    console.log('📡 Loading messages from backend via ThreadManager...');

    if (typeof window.ThreadManager === 'undefined') {
        console.error('❌ ThreadManager not available!');
        return;
    }

    try {
        const result = await window.ThreadManager.loadMessagesForThread(threadId, null, 0);
        console.log('✅ Backend fetch complete:', {
            fetched_messages: result?.messages?.length || 0,
            total: result?.pagination?.total || result?.messages?.length || 0,
            result_type: typeof result,
            result_keys: result ? Object.keys(result) : []
        });

        console.log('📦 Raw result from ThreadManager:', result);

        // Step 5: Get messages from MessageStore
        const loadedMessages = window.MessageStore.getMessages(threadId);
        console.log(`📦 MessageStore now contains: ${loadedMessages.length} messages`);
        console.log('  User messages:', loadedMessages.filter(m => m.role === 'user').length);
        console.log('  Assistant messages:', loadedMessages.filter(m => m.role === 'assistant').length);

        // If MessageStore is empty, manually add messages
        if (loadedMessages.length === 0 && result?.messages?.length > 0) {
            console.warn('⚠️ MessageStore is empty but result has messages! Manually adding...');
            result.messages.forEach(msg => {
                window.MessageStore.addMessage(threadId, msg, { checkDuplicates: false, silent: true });
            });
            const recheck = window.MessageStore.getMessages(threadId);
            console.log(`✅ Manually added ${recheck.length} messages to MessageStore`);
        }

        // Get final message list
        const messagesToRender = window.MessageStore.getMessages(threadId);

        if (messagesToRender.length === 0) {
            console.error('❌ No messages to render! MessageStore is still empty.');
            return;
        }

        // Step 6: Render messages using UnifiedMessageRenderer
        console.log('\n🎨 Starting render loop with UnifiedMessageRenderer...');
        console.log('='.repeat(60));

        for (const [index, msg] of messagesToRender.entries()) {
            console.log(`\n[RENDER ${index + 1}/${loadedMessages.length}] Role: ${msg.role}`);

            if (typeof window.UnifiedMessageRenderer !== 'undefined') {
                const rendered = await window.UnifiedMessageRenderer.render(
                    messagesDiv,
                    msg.role,
                    msg.content,
                    {
                        threadId: threadId,
                        syncToBackend: false,
                        scrollToBottom: false,
                        checkDuplicates: false  // Historical load
                    }
                );

                if (rendered) {
                    console.log(`  ✅ Rendered successfully`);
                } else {
                    console.log(`  ⚠️ Render returned NULL (skipped)`);
                }
            } else {
                console.error('  ❌ UnifiedMessageRenderer not available!');
                break;
            }
        }

        console.log('='.repeat(60));
        console.log('🎨 Render loop complete\n');

        // Step 7: Verify DOM
        const renderedElements = messagesDiv.querySelectorAll('.ai-message');
        console.log(`📊 DOM verification: ${renderedElements.length} message elements in DOM`);
        console.log('  User elements:', messagesDiv.querySelectorAll('.ai-message.user').length);
        console.log('  Assistant elements:', messagesDiv.querySelectorAll('.ai-message.assistant, .ai-message.ai').length);

    } catch (error) {
        console.error('❌ Error during reload:', error);
        console.error(error.stack);
    }

    // ============================================================
    // DISPLAY CAPTURED LOGS SUMMARY
    // ============================================================

    console.log('\n\n');
    console.log('%c═══════════════════════════════════════════════════════════', 'color: cyan; font-weight: bold;');
    console.log('%c📊 CAPTURED LOGS SUMMARY', 'color: lime; font-size: 16px; font-weight: bold;');
    console.log('%c═══════════════════════════════════════════════════════════', 'color: cyan; font-weight: bold;');
    console.log('');
    console.log(`%c📝 Total Logs Captured: ${capturedLogs.length}`, 'color: white; font-size: 14px;');
    console.log(`%c🎨 Render Operations: ${renderCount}`, 'color: #4ec9b0; font-size: 14px;');
    console.log(`%c👤 User Messages: ${userMessageCount}`, 'color: #58a6ff; font-size: 14px;');
    console.log(`%c🤖 Assistant Messages: ${assistantMessageCount}`, 'color: #9cdcfe; font-size: 14px;');
    console.log(`%c⚠️ Skipped Messages: ${skipCount}`, 'color: #dcdcaa; font-size: 14px;');
    console.log(`%c🔄 Duplicate Detections: ${duplicateCount}`, 'color: #ce9178; font-size: 14px;');
    console.log('');

    // Show errors/warnings
    const errors = capturedLogs.filter(l => l.type === 'ERROR');
    const warnings = capturedLogs.filter(l => l.type === 'WARN');

    if (errors.length > 0) {
        console.log(`%c❌ Errors: ${errors.length}`, 'color: #f48771; font-size: 14px; font-weight: bold;');
        errors.forEach((e, i) => {
            console.log(`  ${i + 1}. ${e.message}`);
        });
        console.log('');
    }

    if (warnings.length > 0) {
        console.log(`%c⚠️ Warnings: ${warnings.length}`, 'color: #dcdcaa; font-size: 14px; font-weight: bold;');
        warnings.forEach((w, i) => {
            console.log(`  ${i + 1}. ${w.message}`);
        });
        console.log('');
    }

    // Filter for important messages
    const importantLogs = capturedLogs.filter(l =>
        l.message.includes('UnifiedMessageRenderer') ||
        l.message.includes('MessageStore') ||
        l.message.includes('assistant') ||
        l.message.includes('Rendered') ||
        l.message.includes('skipped') ||
        l.message.includes('duplicate')
    );

    console.log(`%c🔍 Important Messages (${importantLogs.length}):`, 'color: cyan; font-size: 14px; font-weight: bold;');
    importantLogs.forEach((log, i) => {
        const color = log.type === 'ERROR' ? '#f48771' : log.type === 'WARN' ? '#dcdcaa' : '#d4d4d4';
        console.log(`%c  ${i + 1}. [${log.type}] ${log.message}`, `color: ${color};`);
    });

    console.log('');
    console.log('%c═══════════════════════════════════════════════════════════', 'color: cyan; font-weight: bold;');
    console.log('');

    // Make logs available globally for inspection
    window.capturedLogs = capturedLogs;
    console.log('%c💾 Full logs saved to: window.capturedLogs', 'color: lime; font-size: 12px;');
    console.log('%c   Access with: window.capturedLogs', 'color: gray; font-size: 12px;');
    console.log('');

    // Restore original console methods
    console.log('🔄 Restoring original console methods...');
    console.log = originalLog;
    console.warn = originalWarn;
    console.error = originalError;
    console.log('✅ Console capture complete!');

})();
