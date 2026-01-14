/**
 * FILE: UI/modules_internal/messages/add-expand-buttons-to-loaded-messages.js
 * PURPOSE: Retrofit expand buttons to message bubbles loaded from database
 * 
 * PROBLEM:
 * - Expand buttons are added during streaming (prime_ai_chat.js, agent-js.js)
 * - But when loading threads from database, messages don't have expand buttons
 * 
 * SOLUTION:
 * - Call addExpandButtonsToLoadedMessages() after loading a thread
 * - Scans all message bubbles and adds expand buttons if missing
 * 
 * USAGE:
 * - Called after ThreadManager.loadThreadInPrime() or similar
 * - window.addExpandButtonsToLoadedMessages();
 * 
 * LAST MODIFIED: 2025-12-07 - Created to fix missing expand buttons on loaded messages
 */

console.log('📦 [EXPAND BUTTONS] Loading retrofit module...');

window.addExpandButtonsToLoadedMessages = function () {
    console.log('[EXPAND BUTTONS] Scanning for messages without expand buttons...');

    let addedCount = 0;

    // Find all AI message bubbles (thinking, tool, text)
    const messageBubbles = document.querySelectorAll('.ai-message-bubble, .thinking-bubble, .tool-bubble, .tool-result-bubble, .server-tool-bubble');

    messageBubbles.forEach(bubble => {
        // Check if this bubble already has actions div
        let actionsDiv = bubble.querySelector('.ai-message-actions');

        // If no actions div exists, create one
        if (!actionsDiv) {
            // Create actions div
            actionsDiv = document.createElement('div');
            actionsDiv.className = 'ai-message-actions';

            // Insert at the beginning of the bubble (header area)
            const headerDiv = bubble.querySelector('.ai-message-header, .thinking-header, .tool-header');
            if (headerDiv) {
                headerDiv.appendChild(actionsDiv);
            } else {
                // No header, prepend to bubble
                bubble.prepend(actionsDiv);
            }
        }

        // Check if expand button already exists
        const existingExpandBtn = Array.from(actionsDiv.querySelectorAll('button')).find(btn =>
            btn.querySelector('.fa-expand-alt')
        );

        if (existingExpandBtn) {
            // Button already exists, skip
            return;
        }

        // Create expand button
        const expandBtn = document.createElement('button');
        expandBtn.className = 'ai-message-copy-btn';
        expandBtn.innerHTML = '<i class="fas fa-expand-alt"></i>';
        expandBtn.title = 'Expand message fullscreen';
        expandBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (typeof window.openMessageFullscreen === 'function') {
                window.openMessageFullscreen(bubble);
            } else {
                console.warn('[EXPAND BUTTONS] window.openMessageFullscreen not available');
            }
        });

        // Append to actions div
        actionsDiv.appendChild(expandBtn);
        addedCount++;
    });

    console.log(`[EXPAND BUTTONS] ✅ Added ${addedCount} expand buttons to loaded messages`);
    return addedCount;
};

// Auto-run on page load (after DOM ready)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Wait a bit for messages to load
        setTimeout(() => {
            window.addExpandButtonsToLoadedMessages();
        }, 1000);
    });
} else {
    // DOM already loaded, run after short delay
    setTimeout(() => {
        window.addExpandButtonsToLoadedMessages();
    }, 1000);
}

console.log('✅ [EXPAND BUTTONS] Retrofit module loaded');
