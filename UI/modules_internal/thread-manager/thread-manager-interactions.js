/**
 * FILE: UI/modules/thread-manager/thread-manager-interactions.js
 * PURPOSE: User interactions - drag/drop, clicks, modals
 * 
 * DEPENDENCIES:
 * - UI/modules/thread-manager/thread-manager-core.js (must load first)
 * - DocumentService (shared utility)
 * 
 * EXPORTS:
 * - Extends window.ThreadManager with interaction methods
 * 
 * USED BY:
 * - UI/business-ai-platform-v2.html (main application)
 * - UI/modules/thread-manager/thread-manager-ui.js (event binding)
 * 
 * RELATED FILES:
 * - UI/modules/thread-manager/thread-manager-core.js (core object)
 * - UI/modules/thread-manager/thread-manager-ui.js (UI updates)
 * - UI/modules/thread-manager/thread-manager-crud.js (CRUD operations)
 * 
 * NOTES:
 * - Handles all user interaction events
 * - Drag and drop functionality
 * - Click handlers, modal interactions
 * - Event delegation and bubbling
 * 
 * LAST MODIFIED: 2025-11-20 - Initial file creation
 */

// Interaction methods will be defined here
// ==================== THREAD MANAGER - INTERACTIONS MODULE ====================
/**
 * User Interactions
 * Handles clicks, drag/drop, modals, and user actions
 */

// Ensure ThreadManager exists before extending
if (typeof window.ThreadManager === 'undefined') {
    console.error('❌ [Interactions] window.ThreadManager not found! Core module must load first.');
    throw new Error('ThreadManager core module not loaded');
}

Object.assign(window.ThreadManager, {
    /**
     * Switch to a thread
     */
    async switchThread(threadId, forceSwitch = false) {
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            console.warn('⚠️ [Interactions] Thread not found:', threadId);
            return;
        }

        console.log(`🔄 [Interactions] Switching to thread: ${thread.title}`);

        // Check if thread is in an agent (unless forcing)
        if (!forceSwitch && thread.location && thread.location !== 'unassigned') {
            console.log(`ℹ️ [Interactions] Thread in ${thread.location}, showing options`);

            const agentId = parseInt(thread.location.replace('agent-', ''));
            const threadItem = document.querySelector(`[data-thread-id="${threadId}"]`);

            if (threadItem && typeof this.showThreadAssignmentOptions === 'function') {
                this.showThreadAssignmentOptions(threadId, agentId, threadItem);
            }
            return;
        }

        // Load in Prime
        await this.loadThreadInPrime(threadId);
    },

    /**
     * Load thread in Prime panel
     */
    async loadThreadInPrime(threadId) {
        // SAFETY CHECK: Ensure UnifiedMessageRenderer is loaded before proceeding
        if (typeof UnifiedMessageRenderer === 'undefined') {
            console.error('[loadThreadInPrime] UnifiedMessageRenderer not loaded yet - deferring load');
            setTimeout(() => this.loadThreadInPrime(threadId), 100);
            return;
        }

        // GUARD: Prevent concurrent loads of same thread in Prime
        if (!this._loadingThreads) {
            this._loadingThreads = new Map();
        }

        const loadState = this._loadingThreads.get(threadId) || { prime: false, agents: new Set() };
        if (loadState.prime) {
            console.warn(`⚠️ [Interactions] Thread ${threadId} already loading in Prime, skipping duplicate load`);
            return;
        }

        loadState.prime = true;
        this._loadingThreads.set(threadId, loadState);

        try {
            const thread = this.threads.find(t => t.id === threadId);
            if (!thread) {
                console.error('❌ [Interactions] Thread not found:', threadId);
                return;
            }

            console.log(`📖 [Interactions] Loading thread in Prime: ${thread.title}`);

            // Check if thread is in an agent and clear it
            if (typeof MultiAgent !== 'undefined') {
                const currentLocation = MultiAgent.getThreadCurrentLocation?.(threadId);
                if (currentLocation && currentLocation.startsWith('agent-')) {
                    const agentId = parseInt(currentLocation.replace('agent-', ''));
                    MultiAgent.clearAgentThread?.(agentId);
                    console.log(`✅ [Interactions] Cleared thread from ${currentLocation}`);
                }
            }

            // CRITICAL: Set thread location to 'prime' (main AI sidebar)
            await this.assignThread(threadId, 'prime', true);
            console.log(`✅ [Interactions] Thread assigned to prime: ${threadId}`);

            // Update global Prime thread ID for lock system
            window._primeThreadId = threadId;
            console.log(`✅ [Interactions] Updated window._primeThreadId: ${threadId}`);

            // Notify ThreadPresence: announce viewer badge for this user
            if (window.ThreadPresence) { window.ThreadPresence.joinThread(threadId); }

            this.currentThreadId = threadId;

            // ✅ FIX: Sync AppState.currentThreadId so autoLoadPrimeThread() knows thread is loaded
            if (typeof this.syncAppState === 'function') {
                this.syncAppState(threadId);
                console.log(`✅ [Interactions] AppState synced with thread: ${threadId}`);
            } else if (typeof AppState !== 'undefined') {
                // Fallback if syncAppState not loaded yet
                AppState.currentThreadId = threadId;
                console.log(`✅ [Interactions] AppState.currentThreadId set: ${threadId}`);
            }

            // Clear attached files
            if (window.clearChatAttachedFiles) {
                window.clearChatAttachedFiles();
            }

            // Clear messages container (preserve scroll controls)
            const messagesContainer = document.getElementById('ai-chat-messages');
            if (messagesContainer) {
                // Remove only message elements, keep scroll controls and other UI
                const messages = messagesContainer.querySelectorAll('.ai-message');
                messages.forEach(msg => msg.remove());
            }

            // Hide welcome container
            const welcomeContainer = document.getElementById('prime-welcome-container');
            if (welcomeContainer) {
                welcomeContainer.style.display = 'none';
            }

            // Load messages
            if (!Array.isArray(thread.messages)) {
                thread.messages = [];
            }

            if (thread.messages.length === 0 && thread.message_count > 0) {
                console.log(`📥 [Interactions] Loading ${thread.message_count} messages from backend...`);
                // AI Prime loads ALL messages (no pagination) - pass null for limit
                const result = await this.loadMessagesForThread(threadId, null, 0);
                const messages = result?.messages || (Array.isArray(result) ? result : []);
                thread.messages = Array.isArray(messages) ? messages : [];
            }

            // Ensure messages is always an array before iteration
            if (!Array.isArray(thread.messages)) {
                console.warn(`⚠️ [Interactions] thread.messages is not an array, resetting to []`);
                thread.messages = [];
            }

            // Render messages (skip tool_use/tool_result messages - they're internal only)
            if (thread.messages.length > 0 && messagesContainer) {
                console.log(`📋 [Interactions] Rendering ${thread.messages.length} messages in BATCHES...`);

                // CRITICAL FIX (Jan 4, 2026): FORCE SEQUENTIAL RENDERING WITH BATCHING
                // Same fix as agent-js.js - prevent DOM overload from rapid TwoRuleStreamProcessor calls
                const BATCH_SIZE = 10;
                const BATCH_DELAY_MS = 100;
                const MESSAGE_DELAY_MS = 10;

                // Add sticky loading indicator to Prime chat (position:sticky keeps it visible as messages render above)
                const loadingIndicator = document.createElement('div');
                loadingIndicator.id = 'prime-render-progress';
                // Sits as a sibling BELOW #ai-chat-messages — always visible, no sticky needed
                loadingIndicator.style.cssText = [
                    'background: var(--bg-primary, #0d1117)',
                    'border-top: 1px solid var(--border-color, #30363d)',
                    'padding: 8px 16px',
                    'display: flex',
                    'align-items: center',
                    'gap: 10px',
                    'font-size: 12px',
                    'color: var(--text-secondary, #8b949e)',
                    'z-index: 10',
                    'user-select: none',
                    'box-sizing: border-box',
                    'flex-shrink: 0',
                ].join('; ');
                loadingIndicator.innerHTML = `
                    <i class="fas fa-spinner fa-spin" style="color:var(--accent-primary,#58a6ff);font-size:11px;flex-shrink:0;"></i>
                    <span id="prime-load-progress-text">Loading messages\u2026 0 of ${thread.messages.length}</span>
                    <div style="flex:1;height:3px;background:var(--border-color,#30363d);border-radius:2px;overflow:hidden;min-width:40px;">
                        <div id="prime-load-progress-bar" style="height:100%;width:0%;background:var(--accent-primary,#58a6ff);transition:width 0.15s ease;border-radius:2px;"></div>
                    </div>
                `;
                // Insert AFTER the messages container, not inside it
                messagesContainer.insertAdjacentElement('afterend', loadingIndicator);

                let renderedCount = 0;
                let skippedCount = 0;

                for (let batchStart = 0; batchStart < thread.messages.length; batchStart += BATCH_SIZE) {
                    const batchEnd = Math.min(batchStart + BATCH_SIZE, thread.messages.length);
                    const batchNum = Math.floor(batchStart / BATCH_SIZE) + 1;
                    const totalBatches = Math.ceil(thread.messages.length / BATCH_SIZE);

                    console.log(`[PRIME-LOAD] 📦 Batch ${batchNum}/${totalBatches}: Rendering messages ${batchStart + 1}-${batchEnd}`);

                    for (let idx = batchStart; idx < batchEnd; idx++) {
                        const msg = thread.messages[idx];

                        try {
                            console.log(`[PRIME-LOAD] 🎯 Message ${idx + 1}/${thread.messages.length} (${msg.role}) - RENDER START`);

                            // Only render user and assistant messages
                            // Skip: tool_use, tool_result (internal API mechanics)
                            if (msg.role === 'user' || msg.role === 'assistant') {
                                if (typeof addChatMessage === 'function') {
                                    const rendered = await addChatMessage(msg.role, msg.content, false, false);  // isThinking=false, checkDuplicates=false
                                    if (rendered) {
                                        renderedCount++;
                                        console.log(`[PRIME-LOAD] ✅ Message ${idx + 1} RENDERED SUCCESSFULLY`);
                                    } else {
                                        // Message was skipped (empty content, tool_result-only, etc.)
                                        skippedCount++;
                                        console.log(`[PRIME-LOAD] ⏭️ Message ${idx + 1} SKIPPED (no renderable content)`);
                                    }

                                    // FORCE DOM UPDATE: Tiny delay to ensure message appears in correct order
                                    await new Promise(resolve => setTimeout(resolve, MESSAGE_DELAY_MS));

                                } else {
                                    console.warn(`[PRIME-LOAD] addChatMessage not available`);
                                }
                            } else {
                                // Skip tool/system/other messages
                                skippedCount++;
                            }

                            // Update sticky progress indicator (text + fill bar)
                            const _ppt = document.getElementById('prime-load-progress-text');
                            const _ppb = document.getElementById('prime-load-progress-bar');
                            if (_ppt) _ppt.textContent = `Loading messages\u2026 ${idx + 1} of ${thread.messages.length}`;
                            if (_ppb) _ppb.style.width = `${Math.round(((idx + 1) / thread.messages.length) * 100)}%`;

                        } catch (renderError) {
                            console.error(`❌ [PRIME-LOAD] Failed to render message ${idx + 1} (ID: ${msg.id}):`, renderError);
                            console.error('[PRIME-LOAD]   Message role:', msg.role);
                            console.error('[PRIME-LOAD]   Content type:', Array.isArray(msg.content) ? `array[${msg.content.length}]` : typeof msg.content);

                            // Create error placeholder so user knows a message failed
                            if (messagesContainer && typeof addChatMessage === 'function') {
                                try {
                                    await addChatMessage('assistant', `⚠️ **Message Rendering Error**\n\nMessage #${idx + 1} (ID: ${msg.id}) failed to render. Check console for details.`, false, false);
                                } catch (e) {
                                    console.error('❌ [PRIME-LOAD] Failed to add error placeholder:', e);
                                }
                            }

                            skippedCount++;
                            // Continue with next message instead of stopping the loop
                            console.log('[PRIME-LOAD] Continuing with next message...');
                        }
                    } // End of batch message loop

                    // BATCH DELAY: Give DOM time to settle before next batch
                    if (batchEnd < thread.messages.length) {
                        console.log(`[PRIME-LOAD] 🛑 Batch ${batchNum} complete. Pausing ${BATCH_DELAY_MS}ms before next batch...`);
                        await new Promise(resolve => setTimeout(resolve, BATCH_DELAY_MS));
                    }

                } // End of batch loop

                // Remove loading indicator
                loadingIndicator.remove();
                console.log(`[PRIME-LOAD] ✅ ALL ${thread.messages.length} messages processed in ${Math.ceil(thread.messages.length / BATCH_SIZE)} batches`);
                console.log(`✅ [Interactions] Rendered ${renderedCount} messages, skipped ${skippedCount}`);
            }

            // Update Prime header with thread info
            this.updatePrimeHeader(threadId);

            // CRITICAL: Show input container when thread is loaded (expandable Prime-style input system)
            const inputContainer = document.querySelector('.ai-chat-input-container');
            if (inputContainer) {
                inputContainer.style.display = 'block';
                console.log('[Interactions] Showed Prime input container (thread loaded)');
            }

        } finally {
            // Release load lock
            loadState.prime = false;
            this._loadingThreads.set(threadId, loadState);
        }
    },

    /**
     * Show thread assignment options (when thread is in agent)
     */
    showThreadAssignmentOptions(threadId, agentId, threadItem) {
        // Close other expanded cards
        document.querySelectorAll('.thread-item.show-options').forEach(item => {
            if (item.dataset.threadId !== threadId) {
                item.classList.remove('show-options');
            }
        });

        // Toggle options
        const isExpanded = threadItem.classList.contains('show-options');

        if (isExpanded) {
            threadItem.classList.remove('show-options');
        } else {
            threadItem.classList.add('show-options');
            threadItem.dataset.currentAgentId = agentId;
            threadItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    },

    /**
     * Handle thread assignment option selection
     */
    async handleThreadAssignmentOption(threadId, option) {
        const threadItem = document.querySelector(`[data-thread-id="${threadId}"]`);
        const agentId = threadItem?.dataset.currentAgentId;

        console.log(`🎯 [Interactions] Option selected: ${option} for thread ${threadId}`);

        switch (option) {
            case 'move-to-prime':
                await this.assignThread(threadId, 'prime');
                await this.switchThread(threadId, true);

                // Open AI Prime sidebar to show the thread
                if (window.AIPrime?.open) {
                    window.AIPrime.open({
                        threadSlug: threadId,
                        agent: 'communication-agent'
                    });
                }
                break;

            case 'view-in-agent':
                // Switch to Multi-Agent tab
                if (typeof switchTab === 'function') {
                    switchTab('multi-agent');
                }

                // Load in agent
                if (agentId && typeof MultiAgent !== 'undefined') {
                    const thread = this.threads.find(t => t.id === threadId);
                    if (thread && MultiAgent.loadThreadIntoAgent) {
                        MultiAgent.loadThreadIntoAgent(parseInt(agentId), thread);
                    }
                }
                break;

            case 'unload-only':
                if (agentId && typeof MultiAgent !== 'undefined') {
                    MultiAgent.clearAgentThread?.(parseInt(agentId));
                }

                // Load thread in Prime properly (this sets prime location and loads messages)
                await this.loadThreadInPrime(threadId);

                // Open AI Prime sidebar to show the thread
                if (window.AIPrime?.open) {
                    window.AIPrime.open({
                        threadSlug: threadId,
                        agent: 'communication-agent'
                    });
                }

                await this.loadThreadsFromBackend();
                await this.renderThreadList();

                if (typeof showNotification === 'function') {
                    showNotification('Thread unloaded from agent and loaded in Prime', 'success');
                }
                break;
        }

        // Collapse options
        if (threadItem) {
            threadItem.classList.remove('show-options');
        }
    },

    /**
     * Handle double-click on thread
     * 
     * BEHAVIOR (Dec 12, 2025):
     * - Thread History sidebar: Just expand/collapse card (do NOT auto-load into Prime)
     * - Prime/Agent panels: Refresh/reload the thread in place
     * 
     * To load a thread from Thread History → Prime, use drag-and-drop instead
     */
    async handleThreadDoubleClick(threadId, currentLocation) {
        console.log(`🖱️ [Interactions] Double-clicked thread ${threadId} at ${currentLocation}`);

        // Find the thread
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            console.error('❌ [Interactions] Thread not found for double-click:', threadId);
            return;
        }

        // Thread History: Load into Prime on double-click
        if (currentLocation === 'thread-history') {
            console.log(`📋 [Interactions] Thread History double-click - loading into Prime`);
            await this.loadThreadInPrime(threadId);
            if (typeof showNotification === 'function') {
                showNotification('Thread loaded in Prime', 'success');
            }
            return;
        }

        // For Prime or Agent panels: Just expand the card (refresh moved to menu)
        console.log(`🎴 [Interactions] Expanding card for ${currentLocation}`);
        const card = document.querySelector(`[data-thread-id="${threadId}"][data-location="${currentLocation}"]`);
        if (card && typeof ThreadCardExpansion !== 'undefined') {
            const fakeEvent = { stopPropagation: () => { }, preventDefault: () => { } };
            ThreadCardExpansion.toggleCard(fakeEvent, threadId);
        }
    },

    /**
     * Unload thread from agent
     */
    async unloadThread(threadId) {
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) return;

        const currentLocation = thread.location || 'unassigned';

        // If thread is already unassigned, nothing to do
        if (currentLocation === 'unassigned') {
            if (typeof showNotification === 'function') {
                showNotification('Thread is already unassigned', 'info');
            }
            return;
        }

        if (typeof showConfirmation === 'function') {
            showConfirmation(
                'Unload Thread?',
                `Move "${thread.title}" from ${currentLocation} back to Prime?`,
                async () => {
                    // Update thread location to 'unassigned' (unassigned pool)
                    await this.assignThread(threadId, 'unassigned');

                    // Handle Prime AI panel unload
                    if (currentLocation === 'prime') {
                        console.log(`🧹 [unloadThread] Unloading from Prime AI panel`);

                        // Call PrimeAI.unloadThread() to clear UI
                        if (typeof PrimeAI !== 'undefined' && typeof PrimeAI.unloadThread === 'function') {
                            PrimeAI.unloadThread();
                            console.log(`✅ [unloadThread] Called PrimeAI.unloadThread()`);
                        } else {
                            console.warn(`⚠️ [unloadThread] PrimeAI.unloadThread not available`);
                        }
                    }

                    // Handle Agent column unload
                    if (currentLocation && currentLocation.startsWith('agent-')) {
                        const match = currentLocation.match(/agent-(\d+)/);
                        if (match) {
                            const agentId = parseInt(match[1]);
                            console.log(`🧹 [unloadThread] Clearing agent-${agentId} (was ${currentLocation})`);

                            // ALWAYS call AgentColumn.unloadThread() to clear messages + thread info
                            if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.unloadThread === 'function') {
                                AgentColumn.unloadThread(agentId);
                                console.log(`✅ [unloadThread] Called AgentColumn.unloadThread(${agentId})`);
                            } else {
                                console.warn(`⚠️ [unloadThread] AgentColumn.unloadThread not available`);

                                // Fallback: Clear manually
                                const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
                                if (messagesContainer) {
                                    messagesContainer.innerHTML = '';
                                    console.log(`🧹 [unloadThread] Cleared messages for agent-${agentId} (fallback)`);
                                }

                                const threadInfoContainer = document.getElementById(`thread-info-${agentId}`);
                                if (threadInfoContainer) {
                                    threadInfoContainer.innerHTML = '';
                                    console.log(`🧹 [unloadThread] Reset thread info for agent-${agentId} (fallback)`);
                                }
                            }

                            // Clear MultiAgent tracking if available
                            if (typeof MultiAgent !== 'undefined' && typeof MultiAgent.clearAgentThread === 'function') {
                                MultiAgent.clearAgentThread(agentId);
                            }
                        }
                    }

                    // Update UI inline (don't close panel)
                    const threadCard = document.querySelector(`[data-thread-id="${threadId}"]`);
                    if (threadCard) {
                        const agentBadge = threadCard.querySelector('.thread-item-agent-badge');
                        if (agentBadge) {
                            agentBadge.className = 'thread-item-agent-badge unassigned';
                            agentBadge.innerHTML = '<i class="fas fa-inbox"></i> Unassigned';
                        }

                        const unloadBtn = threadCard.querySelector('.thread-action-btn.unload');
                        if (unloadBtn) {
                            unloadBtn.remove();
                        }
                    }

                    await this.loadThreadsFromBackend();

                    if (typeof showNotification === 'function') {
                        showNotification('Thread unassigned', 'success');
                    }
                }
            );
        }
    },

    /**
     * Drag and drop handlers
     */
    handleDragStart(event) {
        event.stopPropagation(); // Prevent parent elements from dragging

        // Find the closest element with data-thread-id attribute
        const threadElement = event.target.closest('[data-thread-id]');
        if (!threadElement) {
            console.error('❌ [Drag] No element with data-thread-id found');
            return;
        }

        // Get thread ID from data attribute and sanitize it
        let threadId = threadElement.dataset.threadId;

        // Remove any whitespace, newlines, or carriage returns
        if (threadId) {
            threadId = threadId.trim().replace(/[\r\n]/g, '');
        }

        // Validate thread ID (should be numeric or timestamp format)
        if (!threadId || threadId.length > 20 || /[^\d]/.test(threadId.replace(/[_-]/g, ''))) {
            console.error(`❌ [Drag] Invalid thread ID: "${threadId?.substring(0, 50)}..."`);
            return;
        }

        console.log(`🔵 [Drag] Started dragging thread: "${threadId}" (length: ${threadId?.length})`);

        // Set thread data using custom MIME types (NOT text/plain to avoid browser including visible text)
        event.dataTransfer.setData('application/x-thread-id', threadId);  // Primary format
        // Read source location from either data-current-location (fallback template) or data-location (compact card template)
        const sourceLocation = threadElement.dataset.currentLocation || threadElement.dataset.location || 'unassigned';
        event.dataTransfer.setData('application/x-source-location', sourceLocation);
        event.dataTransfer.effectAllowed = 'move';

        // Prevent browser from including text content by clearing selection
        if (window.getSelection) {
            window.getSelection().removeAllRanges();
        }

        threadElement.classList.add('dragging');
    },

    handleDragEnd(event) {
        // Find the closest element with data-thread-id attribute
        const threadElement = event.target.closest('[data-thread-id]');
        if (threadElement) {
            threadElement.classList.remove('dragging');
        }

        // Clear drag-over from ALL possible drop zones
        document.querySelectorAll('.drag-over').forEach(element => {
            element.classList.remove('drag-over');
        });
    },

    handleDragOver(event) {
        event.preventDefault();
        event.stopPropagation();
        event.dataTransfer.dropEffect = 'move';
        const dropZone = event.currentTarget;
        if (!dropZone.classList.contains('drag-over')) {
            dropZone.classList.add('drag-over');
        }
    },

    handleDragLeave(event) {
        // Only remove if actually leaving the drop zone (not entering a child)
        const rect = event.currentTarget.getBoundingClientRect();
        const x = event.clientX;
        const y = event.clientY;

        // Check if mouse is still within the drop zone boundaries
        if (x < rect.left || x >= rect.right || y < rect.top || y >= rect.bottom) {
            event.currentTarget.classList.remove('drag-over');
        }
    },

    async handleDrop(event, targetLocation) {
        event.preventDefault();
        event.stopPropagation();

        // Guard: targetLocation must be provided by the drop zone listener (always trusted)
        if (!targetLocation) {
            console.warn('🚫 [Drop] No targetLocation provided - ignoring drop');
            return;
        }

        const dropZone = event.currentTarget;
        dropZone.classList.remove('drag-over');

        // Get thread ID from custom MIME types (NOT text/plain which includes visible text)
        let threadId = event.dataTransfer.getData('application/x-thread-id');
        const sourceLocation = event.dataTransfer.getData('application/x-source-location');

        if (!threadId) {
            console.warn('⚠️ [Interactions] No thread ID in drop event');
            return;
        }

        console.log(`📍 [Drop] Thread ${threadId} from ${sourceLocation || 'unknown'} → ${targetLocation}`);

        // Remove any whitespace, newlines, or carriage returns
        threadId = threadId.trim().replace(/[\r\n]/g, '');

        // Validate thread ID (should be numeric timestamp format, not HTML text)
        if (threadId.length > 20 || threadId.includes(' ') || threadId.includes('\n')) {
            console.error(`❌ [Drop] Invalid thread ID detected (contains HTML text): "${threadId.substring(0, 100)}..."`);
            if (typeof showNotification === 'function') {
                showNotification('Drag and drop error: Invalid thread ID', 'error');
            }
            return;
        }

        console.log(`📍 [Interactions] Thread "${threadId}" (length: ${threadId.length}) dropped on ${targetLocation}`);

        // NEW: Check ThreadCardRegistry for registered MIME type handlers
        // This enables workflow slugs, automation slugs, documents, etc. to be dropped
        if (window.ThreadCardRegistry && window.ThreadCardRegistry.initialized) {
            const handled = await window.ThreadCardRegistry.handleDrop(event, threadId, targetLocation);
            if (handled) {
                console.log('✅ [Drop] Handled by ThreadCardRegistry');
                // Refresh thread card to show new badge
                if (typeof this.refreshThreadCard === 'function') {
                    this.refreshThreadCard(threadId);
                }
                return;
            }
        }

        // Check if dropping in same location - no action needed (EXCEPT for Prime)
        // Prime should always load the thread when dropped, even if already marked as in Prime
        if (sourceLocation === targetLocation && targetLocation !== 'unassigned' && targetLocation !== 'prime') {
            console.log('🔄 [Drop] Same location - no change needed');
            if (typeof showNotification === 'function') {
                showNotification('Thread already in this location', 'info');
            }
            return;
        }

        // === OCCUPANCY CHECK: If the target is a single-thread location (prime or
        // agent-N) and another thread is already there, prompt the user before
        // displacing it. Without this check, drops silently overwrite the existing
        // assignment — surprising and hard to recover from. ===
        const targetIsOccupiable = targetLocation === 'prime' || targetLocation.startsWith('agent-');
        if (targetIsOccupiable) {
            const existingThread = this.threads.find(
                t => t.location === targetLocation && t.id !== threadId
            );
            const sourceThread = this.threads.find(t => t.id === threadId);

            if (existingThread && sourceThread) {
                console.log(`⚠️ [Drop] Target ${targetLocation} occupied by ${existingThread.id} - showing confirmation`);

                const choice = await new Promise((resolve) => {
                    this.showAssignmentConfirmation({
                        sourceThread,
                        sourceLocation,
                        targetLocation,
                        existingThread,
                        onChoose: resolve
                    });
                });

                if (choice.action === 'cancel') {
                    console.log('🚫 [Drop] User cancelled the swap/unassign dialog');
                    return;
                }

                if (targetLocation === 'prime') {
                    // Prime flow: existing local-render path doesn't write to DB.
                    // We must explicitly move the existing prime thread out of the
                    // way so a refresh doesn't put it back. The new thread is then
                    // loaded locally via loadThreadInPrime.
                    if (choice.action === 'unassign_existing') {
                        await this.assignThread(existingThread.id, null);
                        await this.loadThreadsFromBackend();
                    } else if (choice.action === 'swap') {
                        // Swap for prime: move existing prime → where source came from
                        // (source may have come from unassigned; if so, swap collapses
                        // to unassign-existing because previous_location is 'unassigned').
                        const swapTarget = sourceLocation || 'unassigned';
                        await this.assignThread(existingThread.id, swapTarget);
                        await this.loadThreadsFromBackend();
                    }
                    await this.loadThreadInPrime(threadId);
                    if (typeof this.renderThreadInfoContainer === 'function') {
                        this.renderThreadInfoContainer('prime', threadId, true);
                    }
                    this.closeThreadMenu();
                    if (typeof showNotification === 'function') {
                        const t = this.threads.find(x => x.id === threadId);
                        showNotification(
                            `Thread ${this.formatThreadTitle(t)} loaded in Prime`,
                            'success'
                        );
                    }
                    return;
                }

                // agent-N flow: use assignThread with the swap flag so the backend
                // routes the displaced thread to the correct destination.
                const swap = choice.action === 'swap';
                const targetAgentId = parseInt(targetLocation.replace('agent-', ''), 10);

                // FIX (Jul 23, 2026, 3rd pass): COORDINATED SWAP FLOW.
                //
                // The previous sequence was:
                //   1. assignThread (DB write)
                //   2. loadThreadsFromBackend (refresh state)
                //   3. _cascadeThreadAssignment called STEP 3b which also tried
                //      to load the displaced thread's messages
                //   4. handleDrop's defensive block then loaded the displaced
                //      thread AGAIN, causing doubled messages and the chat
                //      panel to flash empty between the two loads.
                //
                // The new sequence is atomic from the user's perspective:
                //   1. Clear BOTH columns (no empty state, no "No thread loaded")
                //   2. assignThread — DB write
                //   3. loadThreadsFromBackend — refresh state
                //   4. Load source thread INTO target agent (single load)
                //   5. Load displaced thread INTO its destination (single load)
                //   6. Render thread-info cards for both legs
                //
                // The user sees a brief blank state during the swap, then both
                // threads appear in their new columns with messages intact.

                // STEP 1: Clear both columns WITHOUT empty state.
                // Always clear the target agent (the displaced thread is leaving).
                this._clearAgentColumnForSwap(targetAgentId);
                // Clear the source if it is a rendered location (Prime or agent).
                if (sourceLocation === 'prime') {
                    this._clearPrimePanelForSwap();
                } else if (sourceLocation && sourceLocation.startsWith('agent-')) {
                    const sourceAgentId = parseInt(sourceLocation.replace('agent-', ''), 10);
                    if (!Number.isNaN(sourceAgentId) && sourceAgentId !== targetAgentId) {
                        this._clearAgentColumnForSwap(sourceAgentId);
                    }
                }
                // (sourceLocation === 'unassigned' / 'thread-history' — nothing to clear.)

                // STEP 2: DB assign. The backend returns the displaced thread info
                // for swaps so we can route it to its new home.
                const assignmentResult = await this.assignThread(threadId, targetLocation, { swap });

                // STEP 3: Refresh local state from DB.
                await this.loadThreadsFromBackend();

                const refreshedThread = this.threads.find(t => t.id === threadId);
                if (!refreshedThread) {
                    console.error(`❌ [Drop] Thread ${threadId} not found after reload`);
                    return;
                }

                // STEP 4: Load the source thread into the target agent's chat panel.
                if (typeof MultiAgent !== 'undefined' && typeof MultiAgent.loadThreadIntoAgent === 'function') {
                    await MultiAgent.loadThreadIntoAgent(targetAgentId, refreshedThread);
                }

                // STEP 5: Load the displaced thread into its destination (single load).
                const displaced = assignmentResult?.assignment?.displaced_thread;
                const displacedDest = assignmentResult?.assignment?.displaced_new_location;
                let displacedDestAgentId = null;
                if (displaced && displacedDest) {
                    const dispThread = this.threads.find(t => t.id === displaced);
                    if (dispThread) {
                        if (displacedDest === 'prime') {
                            if (typeof this.loadThreadInPrime === 'function') {
                                try {
                                    await this.loadThreadInPrime(displaced);
                                    console.log(`✅ [Drop] Swap: displaced thread ${displaced} into Prime`);
                                } catch (e) {
                                    console.warn(`[Drop] Swap load into Prime failed for ${displaced}:`, e);
                                }
                            }
                        } else if (typeof displacedDest === 'string' && displacedDest.startsWith('agent-')) {
                            displacedDestAgentId = parseInt(displacedDest.replace('agent-', ''), 10);
                            if (typeof window !== 'undefined' &&
                                typeof window.MultiAgent !== 'undefined' &&
                                typeof window.MultiAgent.loadThreadIntoAgent === 'function') {
                                try {
                                    await window.MultiAgent.loadThreadIntoAgent(displacedDestAgentId, dispThread);
                                    console.log(`✅ [Drop] Swap: displaced thread ${displaced} into ${displacedDest}`);
                                } catch (e) {
                                    console.warn(`[Drop] Swap load into ${displacedDest} failed for ${displaced}:`, e);
                                }
                            }
                        }
                        // displacedDest === 'unassigned' (or anything else): displaced
                        // thread is back in the catalogue — no chat load needed.
                    }
                }

                // STEP 6: Render thread-info cards for BOTH legs of the swap.
                const targetInfoContainer = document.getElementById(`thread-info-${targetAgentId}`);
                if (targetInfoContainer && typeof this.renderThreadInfoContainer === 'function') {
                    targetInfoContainer.innerHTML = this.renderThreadInfoContainer(targetLocation, threadId, true);
                }
                if (displaced && displacedDest) {
                    if (displacedDest === 'prime') {
                        const primeInfo = document.getElementById('thread-info-prime');
                        if (primeInfo && typeof this.renderThreadInfoContainer === 'function') {
                            primeInfo.innerHTML = this.renderThreadInfoContainer('prime', displaced, true);
                        }
                    } else if (displacedDestAgentId !== null && !Number.isNaN(displacedDestAgentId)) {
                        const destInfo = document.getElementById(`thread-info-${displacedDestAgentId}`);
                        if (destInfo && typeof this.renderThreadInfoContainer === 'function') {
                            destInfo.innerHTML = this.renderThreadInfoContainer(displacedDest, displaced, true);
                        }
                    }
                }

                // STEP 7: Re-render the catalogue so the new locations show.
                if (typeof this.renderThreadList === 'function') {
                    this.renderThreadList();
                }

                // STEP 8: Notification.
                if (typeof showNotification === 'function') {
                    const agentDisplay = this.formatLocationName(targetLocation);
                    const action = swap ? 'Swapped with' : 'Replaced existing thread at';
                    showNotification(
                        `${action} ${agentDisplay}`,
                        'success'
                    );
                }
                return;
            }
        }

        if (targetLocation === 'unassigned' || targetLocation === 'prime') {
            console.log(`🎯 [Drop] Loading thread ${threadId} in Prime`);

            // Find the thread
            const thread = this.threads.find(t => t.id === threadId);
            if (!thread) {
                console.error('❌ [Drop] Thread not found:', threadId);
                if (typeof showNotification === 'function') {
                    showNotification('Thread not found', 'error');
                }
                return;
            }

            // Load in Prime using loadThreadInPrime (this will set prime location internally)
            await this.loadThreadInPrime(threadId);

            // Open AI Prime sidebar to show the thread
            if (window.AIPrime?.open) {
                window.AIPrime.open({
                    threadSlug: threadId,
                    agent: 'communication-agent'
                });
            }

            // Update thread info card
            if (typeof this.renderThreadInfoContainer === 'function') {
                this.renderThreadInfoContainer('prime', threadId, true);
            }

            // Close thread menu
            this.closeThreadMenu();

            if (typeof showNotification === 'function') {
                showNotification(`Thread "${thread.title}" loaded in Prime`, 'success');
            }
        } else if (targetLocation.startsWith('agent-')) {
            const agentId = parseInt(targetLocation.replace('agent-', ''));

            if (typeof MultiAgent !== 'undefined') {
                // Assign thread first
                await this.assignThread(threadId, targetLocation);

                // Reload threads from backend to get fresh data
                await this.loadThreadsFromBackend();

                // Find the thread with fresh data
                const thread = this.threads.find(t => t.id === threadId);
                if (!thread) {
                    console.error(`❌ [Drop] Thread ${threadId} not found after reload`);
                    return;
                }

                console.log(`✅ [Drop] Found thread after reload:`, thread.title);

                // Load thread into agent
                if (MultiAgent.loadThreadIntoAgent) {
                    await MultiAgent.loadThreadIntoAgent(agentId, thread);
                }

                // Ensure thread info card is displayed
                const threadInfoContainer = document.getElementById(`thread-info-${agentId}`);
                if (threadInfoContainer && typeof this.renderThreadInfoContainer === 'function') {
                    threadInfoContainer.innerHTML = this.renderThreadInfoContainer(targetLocation, threadId, true);
                    console.log(`✅ [Drop] Updated thread info card for agent-${agentId}`);
                } else {
                    console.error(`❌ [Drop] Thread info container not found for agent-${agentId}`);
                }

                if (typeof showNotification === 'function') {
                    const agentName = MultiAgent.getAgentName?.(agentId) || `Agent ${agentId}`;
                    showNotification(`Thread assigned to ${agentName}`, 'success');
                }
            }
        }

        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList();
        }
    },

    /**
     * Toggle thread menu
     */
    async toggleThreadMenu() {
        const menu = document.getElementById('thread-menu');
        if (!menu) {
            console.error('❌ [Interactions] Thread menu not found');
            return;
        }

        const wasActive = menu.classList.contains('active');
        menu.classList.toggle('active');

        // Toggle button visual state
        const threadsBtn = document.getElementById('threads-btn');
        if (threadsBtn) {
            if (!wasActive) {
                threadsBtn.classList.add('thread-menu-open');
            } else {
                threadsBtn.classList.remove('thread-menu-open');
            }
        }

        if (!wasActive) {
            // Opening menu - load threads
            console.log('📂 [Interactions] Opening thread menu...');
            await this.loadThreadsFromBackend();
            await this.renderThreadList();

            // Populate dynamic dropdowns
            if (typeof this.populateAgentDropdown === 'function') {
                this.populateAgentDropdown();
            }
            if (typeof this.populateTagsDropdown === 'function') {
                this.populateTagsDropdown();
            }

            console.log(`✅ [Interactions] Thread menu opened with ${this.threads.length} threads`);
        }
    },

    /**
     * Get a human-friendly agent display name in the format "Agent-N NATO".
     * Distinct from MultiAgent.getAgentName (which returns "NATO-N") so both
     * formats remain available — column headers keep NATO-first; toasts and
     * the swap modal use Agent-first per the product spec.
     *
     * @param {number|string} agentId
     * @returns {string} e.g. "Agent-3 Charlie"
     */
    getAgentDisplayName(agentId) {
        const id = parseInt(agentId, 10);
        if (!id || id < 1 || id > 26) return `Agent ${agentId}`;
        const natoNames = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot',
            'Golf', 'Hotel', 'India', 'Juliet', 'Kilo', 'Lima', 'Mike', 'November',
            'Oscar', 'Papa', 'Quebec', 'Romeo', 'Sierra', 'Tango', 'Uniform',
            'Victor', 'Whiskey', 'X-ray', 'Yankee', 'Zulu'];
        const nato = natoNames[id - 1] || `Agent`;
        return `Agent-${id} ${nato}`;
    },

    /**
     * Format a DB location string for human display. Used by toasts and
     * the swap modal so users never see raw values like "agent-3".
     *
     * @param {string} location - DB value (unassigned | prime | agent-N | thread-history | synergy)
     * @returns {string} human display string
     */
    formatLocationName(location) {
        if (!location) return 'Unassigned';
        if (location === 'unassigned') return 'Catalogue';
        if (location === 'thread-history') return 'Catalogue';
        if (location === 'prime') return 'Prime';
        if (location === 'synergy') return 'Synergy';
        if (location.startsWith('agent-')) {
            const id = parseInt(location.replace('agent-', ''), 10);
            return this.getAgentDisplayName(id);
        }
        return location;
    },

    /**
     * Format a thread title for display, with truncation for safety.
     *
     * @param {object} thread
     * @param {number} maxLen
     * @returns {string}
     */
    formatThreadTitle(thread, maxLen = 40) {
        const title = thread?.title || 'Untitled';
        if (title.length <= maxLen) return `"${title}"`;
        return `"${title.slice(0, maxLen - 1)}…"`;
    },

    /**
     * Show a confirmation modal when a thread drop would displace another
     * thread. Three branches:
     *   - source = prime | agent-N AND target occupied: Swap | Unassign existing | Cancel
     *   - source = unassigned (catalogue) AND target occupied: Unassign existing | Cancel
     *     (swap collapses to unassign because source has no real previous location)
     *   - source = unassigned AND target empty: handled silently by caller
     *
     * @param {object} params
     * @param {object} params.sourceThread     - Thread being dragged
     * @param {string} params.sourceLocation   - DB location of the source thread
     * @param {string} params.targetLocation   - DB location being dropped onto
     * @param {object} params.existingThread   - Thread currently at the target location
     * @param {function} params.onChoose       - ({ action: 'swap' | 'unassign_existing' | 'cancel' }) => void
     */
    showAssignmentConfirmation({ sourceThread, sourceLocation, targetLocation, existingThread, onChoose }) {
        const sourceTitle = this.formatThreadTitle(sourceThread);
        const existingTitle = this.formatThreadTitle(existingThread);
        const targetDisplay = this.formatLocationName(targetLocation);
        const isFromCatalogue = sourceLocation === 'unassigned' || sourceLocation === 'thread-history';

        // Build modal content
        // FIX (Jul 23, 2026): Add 'active' class so CSS `display: flex` applies.
        // The overlay defaults to `display: none` and only becomes visible when
        // `.active` is present (matches the .message-popup-overlay pattern).
        const overlay = document.createElement('div');
        overlay.className = 'thread-confirm-overlay active';
        overlay.innerHTML = `
            <div class="thread-confirm-modal">
                <div class="thread-confirm-header">
                    <i class="fas fa-exchange-alt"></i>
                    <h3>${isFromCatalogue ? 'Replace thread at this location?' : 'Swap or unassign?'}</h3>
                </div>
                <div class="thread-confirm-body">
                    ${isFromCatalogue
                        ? `<p><strong>${targetDisplay}</strong> already has ${existingTitle} loaded.</p>
                           <p>Assigning ${sourceTitle} here will move ${existingTitle} to the Thread Catalogue.</p>`
                        : `<p><strong>${targetDisplay}</strong> already has ${existingTitle} loaded.</p>
                           <p>You can <em>swap</em> ${sourceTitle} with ${existingTitle}, or move ${existingTitle} to the Thread Catalogue and assign ${sourceTitle} here.</p>`
                    }
                </div>
                <div class="thread-confirm-actions">
                    <button class="thread-confirm-btn thread-confirm-cancel" data-action="cancel">
                        Cancel
                    </button>
                    <button class="thread-confirm-btn thread-confirm-unassign" data-action="unassign_existing">
                        <i class="fas fa-folder-open"></i>
                        Move existing to catalogue
                    </button>
                    ${isFromCatalogue ? '' : `
                    <button class="thread-confirm-btn thread-confirm-swap" data-action="swap">
                        <i class="fas fa-exchange-alt"></i>
                        Swap
                    </button>
                    `}
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        // Wire buttons
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.remove();
                onChoose({ action: 'cancel' });
                return;
            }
            const action = e.target.closest('[data-action]')?.dataset.action;
            if (!action) return;
            overlay.remove();
            onChoose({ action });
        });

        // Escape to cancel
        const onKey = (e) => {
            if (e.key === 'Escape') {
                overlay.remove();
                document.removeEventListener('keydown', onKey);
                onChoose({ action: 'cancel' });
            }
        };
        document.addEventListener('keydown', onKey);
    },

    /**
     * Setup drop zones for agent columns
     * Call this after creating new agent columns dynamically
     *
     * Uses dragenter/dragleave depth-counter pattern to avoid the flicker that
     * the previous dragover-adds-class approach suffered from when crossing
     * child elements (which fire their own dragenter/leave events).
     */
    setupAgentDropZones() {
        console.log('[ThreadManager] Setting up agent drop zones...');

        document.querySelectorAll('.agent-column').forEach(agentColumn => {
            // Skip if already has handler
            if (agentColumn.dataset.dropZoneConfigured === 'true') {
                return;
            }

            const agentId = parseInt(agentColumn.dataset.agentId);
            let dragDepth = 0;  // Counter for nested dragenter/dragleave events

            agentColumn.addEventListener('dragenter', (e) => {
                e.preventDefault();
                if (dragDepth++ === 0) {
                    agentColumn.classList.add('drag-over');
                }
            });

            agentColumn.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.stopPropagation();
                e.dataTransfer.dropEffect = 'move';
            });

            agentColumn.addEventListener('dragleave', () => {
                if (--dragDepth <= 0) {
                    dragDepth = 0;
                    agentColumn.classList.remove('drag-over');
                }
            });

            agentColumn.addEventListener('drop', async (e) => {
                e.preventDefault();
                dragDepth = 0;
                agentColumn.classList.remove('drag-over');

                const threadId = e.dataTransfer.getData('application/x-thread-id');
                if (!threadId) return;

                console.log(`📍 [Drop] Thread ${threadId} dropped on agent-${agentId}`);

                // Call handleDrop with proper location
                await this.handleDrop(e, `agent-${agentId}`);
            });

            // Mark as configured
            agentColumn.dataset.dropZoneConfigured = 'true';
            console.log(`✅ [Drop Zone] Agent ${agentId} configured (entire column is drop area)`);
        });

        // Also setup drop zone for multi-agent-container (for new agents)
        const multiAgentContainer = document.getElementById('multi-agent-container');
        if (multiAgentContainer && multiAgentContainer.dataset.dropZoneConfigured !== 'true') {
            multiAgentContainer.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
            });
            multiAgentContainer.dataset.dropZoneConfigured = 'true';
            console.log('✅ [Drop Zone] Multi-agent container configured');
        }
    },

    /**
     * Setup drop zone for Prime chat container
     * Call this when ThreadManager initializes
     *
     * Uses the same dragenter depth-counter pattern as agent columns, but with
     * a subtle outline class (`prime-drag-over`) so the user sees the drop
     * target without obscuring the chat header content.
     */
    setupPrimeDropZone() {
        console.log('[ThreadManager] Setting up Prime drop zone...');

        // Use the entire ai-chat-panel as drop zone
        const primeContainer = document.getElementById('ai-chat-panel');
        if (!primeContainer) {
            console.error('❌ [ThreadManager] Prime chat panel not found');
            return;
        }

        // Skip if already configured
        if (primeContainer.dataset.dropZoneConfigured === 'true') {
            console.log('⚠️ [ThreadManager] Prime drop zone already configured');
            return;
        }

        let dragDepth = 0;  // Counter for nested dragenter/dragleave events

        primeContainer.addEventListener('dragenter', (e) => {
            e.preventDefault();
            if (dragDepth++ === 0) {
                primeContainer.classList.add('prime-drag-over');
            }
        });

        primeContainer.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            e.dataTransfer.dropEffect = 'move';
        });

        primeContainer.addEventListener('dragleave', () => {
            if (--dragDepth <= 0) {
                dragDepth = 0;
                primeContainer.classList.remove('prime-drag-over');
            }
        });

        primeContainer.addEventListener('drop', async (e) => {
            e.preventDefault();
            dragDepth = 0;
            primeContainer.classList.remove('prime-drag-over');

            const threadId = e.dataTransfer.getData('application/x-thread-id');
            if (!threadId) return;

            console.log(`📍 [Drop] Thread ${threadId} dropped on Prime`);

            // Call handleDrop with 'prime' location
            await this.handleDrop(e, 'prime');
        });

        primeContainer.dataset.dropZoneConfigured = 'true';
        console.log('✅ [Drop Zone] Prime configured (entire panel is drop area)');
    },

    /**
     * Setup drop zone for the Thread Catalogue sidebar (#thread-menu).
     *
     * Only enabled when the catalogue has the `.active` class — when the
     * sidebar is collapsed/hidden, the drop zone is bypassed entirely so a
     * stray drag onto the (invisible) panel doesn't silently move a thread.
     *
     * On drop, the source thread is moved to `unassigned` (i.e. added to the
     * catalogue) via assignThread(threadId, null).
     */
    setupCatalogueDropZone() {
        console.log('[ThreadManager] Setting up Catalogue drop zone...');

        const catalogue = document.getElementById('thread-menu');
        if (!catalogue) {
            console.error('❌ [ThreadManager] Thread catalogue sidebar not found');
            return;
        }

        // Skip if already configured
        if (catalogue.dataset.dropZoneConfigured === 'true') {
            console.log('⚠️ [ThreadManager] Catalogue drop zone already configured');
            return;
        }

        let dragDepth = 0;  // Counter for nested dragenter/dragleave events

        catalogue.addEventListener('dragenter', (e) => {
            e.preventDefault();
            // Disabled when the catalogue sidebar is not currently visible
            if (!catalogue.classList.contains('active')) return;
            if (dragDepth++ === 0) {
                catalogue.classList.add('drag-over');
            }
        });

        catalogue.addEventListener('dragover', (e) => {
            e.preventDefault();
            // Drop effect only matters when sidebar is visible
            if (!catalogue.classList.contains('active')) return;
            e.dataTransfer.dropEffect = 'move';
        });

        catalogue.addEventListener('dragleave', () => {
            if (--dragDepth <= 0) {
                dragDepth = 0;
                catalogue.classList.remove('drag-over');
            }
        });

        catalogue.addEventListener('drop', async (e) => {
            e.preventDefault();
            dragDepth = 0;
            catalogue.classList.remove('drag-over');

            // Guard: if sidebar is not active, ignore the drop
            if (!catalogue.classList.contains('active')) {
                console.log('🚫 [Drop] Catalogue sidebar not active - drop ignored');
                return;
            }

            const threadId = e.dataTransfer.getData('application/x-thread-id');
            const sourceLocation = e.dataTransfer.getData('application/x-source-location');
            if (!threadId) return;

            // Already in catalogue? No-op
            if (sourceLocation === 'unassigned' || sourceLocation === 'thread-history') {
                console.log('🔄 [Drop] Thread already in catalogue - no change needed');
                if (typeof showNotification === 'function') {
                    showNotification('Thread already in catalogue', 'info');
                }
                return;
            }

            console.log(`📍 [Drop] Thread ${threadId} dropped on Thread Catalogue (from ${sourceLocation})`);

            const thread = this.threads.find(t => t.id === threadId);
            const threadTitle = thread?.title || 'Untitled';

            // Move to unassigned (catalogue). assignThread(null) handles the
            // null-location -> 'unassigned' mapping on the frontend side.
            await this.assignThread(threadId, null);

            if (typeof showNotification === 'function') {
                showNotification(`Thread "${threadTitle}" moved to catalogue`, 'success');
            }
        });

        catalogue.dataset.dropZoneConfigured = 'true';
        console.log('✅ [Drop Zone] Thread Catalogue configured (active-only)');
    },

    /**
     * Close thread menu
     */
    closeThreadMenu() {
        const menu = document.getElementById('thread-menu');
        if (menu) {
            menu.classList.remove('active');
        }

        const threadsBtn = document.getElementById('threads-btn');
        if (threadsBtn) {
            threadsBtn.classList.remove('active');
        }
    },

    /**
     * Toggle thread menu collapse state (full close/open like threads-btn)
     */
    async toggleThreadMenuCollapse() {
        const menu = document.getElementById('thread-menu');

        if (!menu) {
            console.error('❌ [Interactions] Thread menu not found');
            return;
        }

        const wasActive = menu.classList.contains('active');
        menu.classList.toggle('active');

        if (!wasActive) {
            // Opening menu - load threads
            console.log('📂 [Interactions] Opening thread menu via collapse button...');
            await this.loadThreadsFromBackend();
            await this.renderThreadList();
            console.log(`✅ [Interactions] Thread menu opened with ${this.threads.length} threads`);
        } else {
            console.log('📐 [Interactions] Thread menu closed via collapse button');
        }
    },

    /**
     * Show new chat modal.
     *
     * Always opens centered with a blurred backdrop. The overlay is a flex
     * container, so CSS handles centering and viewport scaling — the modal
     * fits any window size via max-width / max-height on .new-chat-modal.
     *
     * Earlier revisions anchored near the trigger button and clipped on
     * short viewports; this is the simpler, more robust path now that the
     * UI is targeting mobile layouts.
     */
    async showNewChatModal(location = 'unassigned') {
        console.log(`➕ [Interactions] Opening new chat modal for ${location}`);

        // Use the agent NATO label (e.g. "Yankee-25") when the location is a
        // per-agent slot so the title matches what the empty-state heading
        // already shows. Falls back to the raw "Agent N" form if MultiAgent
        // isn't loaded.
        const locationName = location === 'unassigned' ? 'Unassigned' :
            (location.startsWith('agent-')
                ? (typeof MultiAgent !== 'undefined' && typeof MultiAgent.getAgentName === 'function'
                    ? MultiAgent.getAgentName(parseInt(location.split('-')[1], 10))
                    : `Agent ${location.split('-')[1]}`)
                : location);

        const modalHTML = `
            <div class="modal-overlay" id="newChatModalOverlay" onclick="if(event.target.id === 'newChatModalOverlay') { const modal = document.getElementById('newChatModalOverlay'); if (modal) modal.remove(); }">
                <div class="new-chat-modal" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h3><i class="fas fa-plus-circle"></i> Start New Chat in ${locationName}</h3>
                        <button class="modal-close" onclick="const modal = document.getElementById('newChatModalOverlay'); if (modal) modal.remove();">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <form id="newChatForm">
                            <div class="form-group">
                                <label for="threadTitle">Thread Title <span style="color: var(--accent-error);">*</span></label>
                                <input type="text" id="threadTitle" class="form-control" placeholder="Enter thread title..." required autofocus>
                            </div>
                            <div class="platform-tags-section">
                                <label>Platform Tags (Select one or more)</label>
                                <div class="platform-tags-grid">
                                    <button type="button" class="platform-tag-btn" data-tag="synergy">
                                        <i class="fas fa-handshake"></i>
                                        <span>Synergy</span>
                                    </button>
                                    <button type="button" class="platform-tag-btn" data-tag="synergy-docs">
                                        <i class="fas fa-file-alt"></i>
                                        <span>Synergy Docs</span>
                                    </button>
                                    <button type="button" class="platform-tag-btn" data-tag="emails">
                                        <i class="fas fa-envelope"></i>
                                        <span>Emails</span>
                                    </button>
                                    <button type="button" class="platform-tag-btn" data-tag="automation">
                                        <i class="fas fa-robot"></i>
                                        <span>Automation</span>
                                    </button>
                                    <button type="button" class="platform-tag-btn" data-tag="workflow">
                                        <i class="fas fa-project-diagram"></i>
                                        <span>Workflow</span>
                                    </button>
                                    <button type="button" class="platform-tag-btn" data-tag="general">
                                        <i class="fas fa-comments"></i>
                                        <span>General</span>
                                    </button>
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="threadTags">Additional Tags (comma-separated)</label>
                                <input type="text" id="threadTags" class="form-control" placeholder="e.g., urgent, research, client-work">
                            </div>
                            <div class="form-group">
                                <label>Thread Visibility</label>
                                <div style="display:flex;gap:16px;margin-top:6px;">
                                    <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-weight:400;">
                                        <input type="radio" name="threadVisibility" value="personal" checked> Personal
                                    </label>
                                    <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-weight:400;">
                                        <input type="radio" name="threadVisibility" value="team"> Team
                                    </label>
                                    <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-weight:400;">
                                        <input type="radio" name="threadVisibility" value="restricted"> Restricted
                                    </label>
                                </div>
                                <small style="color:var(--text-tertiary);font-size:11px;margin-top:4px;display:block;">Personal = only you &bull; Team = all org members &bull; Restricted = invited members only</small>
                            </div>
                            <div class="modal-actions">
                                <button type="button" class="btn btn-secondary" onclick="const modal = document.getElementById('newChatModalOverlay'); if (modal) modal.remove();">
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-plus"></i> Create Thread
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('newChatModalOverlay');
        if (existingModal) existingModal.remove();

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // The overlay is a flex container with align-items: center and
        // justify-content: center, so the modal lands dead-center on every
        // viewport. .new-chat-modal's max-width / max-height CSS handles
        // short windows automatically.

        // Setup platform tag button interactions with resource selection
        const platformTagBtns = document.querySelectorAll('.platform-tag-btn');
        platformTagBtns.forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                const tagType = btn.dataset.tag;

                // If already selected, deselect and remove specific ID
                if (btn.classList.contains('selected')) {
                    btn.classList.remove('selected');
                    delete btn.dataset.specificId;
                    const tagLabel = btn.querySelector('.tag-specific-label');
                    if (tagLabel) tagLabel.remove();
                    return;
                }

                // Show resource selector for specific tag types
                if (tagType === 'synergy') {
                    await this.showSynergySessionSelector(btn);
                } else if (tagType === 'automation' || tagType === 'workflow') {
                    await this.showWorkflowSelector(btn, tagType);
                } else if (tagType === 'synergy-docs') {
                    await this.showInternalDocSelector(btn);
                } else if (tagType === 'emails') {
                    await this.showEmailSelector(btn);
                } else {
                    // General tag - just toggle
                    btn.classList.add('selected');
                }
            });
        });

        // Handle form submission
        const form = document.getElementById('newChatForm');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const title = document.getElementById('threadTitle').value.trim();
            const tagsStr = document.getElementById('threadTags').value.trim();
            const visibility = document.querySelector('input[name="threadVisibility"]:checked')?.value || 'personal';

            // Collect selected platform tags (with specific IDs if available)
            const selectedPlatformTags = Array.from(document.querySelectorAll('.platform-tag-btn.selected'))
                .map(btn => {
                    // If button has specificId (e.g., "synergy:session-123"), use that
                    // Otherwise, use generic tag (e.g., "synergy")
                    return btn.dataset.specificId || btn.dataset.tag;
                });

            // Combine platform tags with additional tags
            const additionalTags = tagsStr ? tagsStr.split(',').map(t => t.trim()).filter(t => t) : [];
            const allTags = [...selectedPlatformTags, ...additionalTags];

            if (!title) {
                alert('Please enter a thread title');
                return;
            }

            try {
                // Create thread with metadata
                const newThreadId = await this.createThreadWithMetadata(title, allTags, location, visibility);

                // Close modal
                const modalOverlay = document.getElementById('newChatModalOverlay');
                if (modalOverlay) {
                    modalOverlay.remove();
                }

                // Load thread
                if (location === 'unassigned' || location === 'prime') {
                    await this.loadThreadInPrime(newThreadId);
                } else if (location.startsWith('agent-')) {
                    const agentId = parseInt(location.replace('agent-', ''));
                    if (typeof MultiAgent !== 'undefined' && MultiAgent.loadThreadIntoAgent) {
                        const thread = this.threads.find(t => t.id === newThreadId);
                        if (thread) {
                            MultiAgent.loadThreadIntoAgent(agentId, thread);
                        }
                    }
                }

                if (typeof showNotification === 'function') {
                    showNotification(`Thread "${title}" created successfully`, 'success');
                }

                console.log(`✅ [Interactions] Thread created: ${newThreadId}`);

            } catch (error) {
                console.error('❌ [Interactions] Failed to create thread:', error);
                alert('Failed to create thread. Please try again.');
            }
        });
    },

    /**
     * Copy thread ID to clipboard
     */
    copyThreadId(threadId) {
        navigator.clipboard.writeText(threadId).then(() => {
            if (typeof showNotification === 'function') {
                showNotification('Thread ID copied to clipboard', 'success');
            }
            console.log('📋 [Interactions] Thread ID copied:', threadId);
        }).catch(err => {
            console.error('❌ [Interactions] Failed to copy:', err);
        });
    },

    /**
     * Toggle copy menu dropdown
     */
    toggleCopyMenu(threadId) {
        const menu = document.getElementById(`copy-menu-${threadId}`);
        if (menu) {
            const isVisible = menu.style.display === 'block';
            // Close all other copy menus first
            document.querySelectorAll('.copy-dropdown-menu').forEach(m => {
                m.style.display = 'none';
            });
            menu.style.display = isVisible ? 'none' : 'block';
        }
    },

    /**
     * Copy full thread conversation with formatting
     * Formats the entire conversation for pasting into documents
     */
    async copyThreadConversation(threadId) {
        console.log('📋 [Copy Thread] Starting copy operation for thread:', threadId);

        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            console.error('❌ [Copy Thread] Thread not found:', threadId);
            if (typeof showNotification === 'function') {
                showNotification('Thread not found', 'error');
            }
            return;
        }

        console.log('📋 [Copy Thread] Found thread:', thread.title || 'Untitled');

        // Fetch full messages if not loaded
        if (!thread.messages || thread.messages.length === 0) {
            console.log('📥 [Copy Thread] Fetching messages for thread:', threadId);
            if (typeof showNotification === 'function') {
                showNotification('Loading thread messages...', 'info', 1500);
            }

            const messages = await this.loadMessagesForThread(threadId);
            if (messages && messages.length > 0) {
                thread.messages = messages;
                console.log('✅ [Copy Thread] Loaded', messages.length, 'messages');
            } else {
                console.warn('⚠️ [Copy Thread] No messages found for thread');
                if (typeof showNotification === 'function') {
                    showNotification('No messages to copy', 'warning');
                }
                return;
            }
        } else {
            console.log('📋 [Copy Thread] Using cached messages:', thread.messages.length, 'messages');
        }

        // Format the conversation
        let formattedText = '';
        formattedText += `THREAD: ${thread.title || 'Untitled'}\n`;
        formattedText += `ID: ${thread.id}\n`;
        formattedText += `DATE: ${new Date(thread.created_at || Date.now()).toLocaleString()}\n`;
        formattedText += `MESSAGES: ${thread.messages.length}\n`;
        formattedText += `${'='.repeat(80)}\n\n`;

        // Track statistics
        const stats = {
            userMessages: 0,
            aiResponses: 0,
            toolResults: 0,
            toolsExecuted: {},
            totalDuration: 0,
            firstTimestamp: null,
            lastTimestamp: null
        };

        thread.messages.forEach((msg, index) => {
            const timestamp = msg.created_at ? new Date(msg.created_at) : null;

            if (timestamp) {
                if (!stats.firstTimestamp) stats.firstTimestamp = timestamp;
                stats.lastTimestamp = timestamp;
            }

            if (msg.role === 'user') {
                // Check if it's a tool result or user input
                const isToolResult = Array.isArray(msg.content) &&
                    msg.content.some(block => block.type === 'tool_result');

                if (isToolResult) {
                    stats.toolResults++;
                } else {
                    stats.userMessages++;
                }

                formattedText += this._formatUserMessage(msg, index + 1, timestamp, thread.messages[index - 1]);
            } else if (msg.role === 'assistant') {
                stats.aiResponses++;

                // Track tool usage
                if (Array.isArray(msg.content)) {
                    msg.content.filter(b => b.type === 'tool_use').forEach(tool => {
                        stats.toolsExecuted[tool.name] = (stats.toolsExecuted[tool.name] || 0) + 1;
                    });
                }

                formattedText += this._formatAssistantMessage(msg, index + 1, timestamp, thread.messages[index - 1]);
            }
        });

        // Calculate total duration
        if (stats.firstTimestamp && stats.lastTimestamp) {
            stats.totalDuration = Math.floor((stats.lastTimestamp - stats.firstTimestamp) / 1000);
        }

        // Add conversation summary
        formattedText += `\n${'='.repeat(80)}\n`;
        formattedText += `CONVERSATION STATISTICS\n`;
        formattedText += `${'='.repeat(80)}\n`;
        formattedText += `Total Messages: ${thread.messages.length}\n`;
        formattedText += `  User Messages: ${stats.userMessages}\n`;
        formattedText += `  AI Responses: ${stats.aiResponses}\n`;
        formattedText += `  Tool Results: ${stats.toolResults}\n\n`;

        if (Object.keys(stats.toolsExecuted).length > 0) {
            formattedText += `Tools Executed: ${Object.values(stats.toolsExecuted).reduce((a, b) => a + b, 0)}\n`;
            Object.entries(stats.toolsExecuted)
                .sort((a, b) => b[1] - a[1])
                .forEach(([tool, count]) => {
                    formattedText += `  - ${tool}: ${count}x\n`;
                });
            formattedText += `\n`;
        }

        if (stats.totalDuration > 0) {
            const minutes = Math.floor(stats.totalDuration / 60);
            const seconds = stats.totalDuration % 60;
            formattedText += `Total Duration: ${minutes}m ${seconds}s\n`;
        }

        formattedText += `${'='.repeat(80)}\n`;
        formattedText += `\n${'='.repeat(80)}\n`;
        formattedText += `END OF CONVERSATION\n`;
        formattedText += `${'='.repeat(80)}\n`;

        // Copy to clipboard
        console.log('📋 [Copy Thread] Formatted text ready, copying to clipboard...');
        console.log('📋 [Copy Thread] Text length:', formattedText.length, 'characters');

        try {
            await navigator.clipboard.writeText(formattedText);
            console.log('✅ [Copy Thread] Successfully copied full conversation');
            console.log('✅ [Copy Thread] Thread:', thread.title || 'Untitled');
            console.log('✅ [Copy Thread] Messages:', thread.messages.length);
            console.log('✅ [Copy Thread] Characters:', formattedText.length);

            if (typeof showNotification === 'function') {
                showNotification(`Copied ${thread.messages.length} messages to clipboard`, 'success', 3000);
            }

            // Close the menu
            this.toggleCopyMenu(threadId);
        } catch (err) {
            console.error('❌ [Copy Thread] Failed to copy conversation:', err);
            if (typeof showNotification === 'function') {
                showNotification('Failed to copy conversation: ' + err.message, 'error');
            }
        }
    },

    /**
     * Format user message for copying
     * @private
     */
    _formatUserMessage(msg, index, timestamp, prevMsg) {
        const isToolResult = Array.isArray(msg.content) &&
            msg.content.some(block => block.type === 'tool_result');

        const messageType = isToolResult ? 'USER MESSAGE (Tool Result)' : 'USER MESSAGE';
        let output = `[${index}] ${messageType}:\n`;

        // Add timestamp and duration
        if (timestamp) {
            output += `Timestamp: ${timestamp.toLocaleString()}\n`;

            if (prevMsg && prevMsg.created_at) {
                const prevTime = new Date(prevMsg.created_at);
                const duration = Math.floor((timestamp - prevTime) / 1000);
                if (duration > 0) {
                    const mins = Math.floor(duration / 60);
                    const secs = duration % 60;
                    if (mins > 0) {
                        output += `Latency: ${mins}m ${secs}s\n`;
                    } else {
                        output += `Latency: ${secs}s\n`;
                    }
                }
            }
        }

        output += `${'-'.repeat(80)}\n`;

        if (typeof msg.content === 'string') {
            output += msg.content + '\n';
        } else if (Array.isArray(msg.content)) {
            msg.content.forEach(block => {
                if (block.type === 'text' && block.text) {
                    output += block.text + '\n';
                } else if (block.type === 'tool_result') {
                    output += `[TOOL RESULT: ${block.tool_use_id || 'unknown'}]\n`;
                    output += JSON.stringify(block.content, null, 2) + '\n';
                }
            });
        }

        output += '\n';
        return output;
    },

    /**
     * Format assistant message for copying
     * @private
     */
    _formatAssistantMessage(msg, index, timestamp, prevMsg) {
        let output = `[${index}] AI RESPONSE:\n`;

        // Add timestamp and duration
        if (timestamp) {
            output += `Timestamp: ${timestamp.toLocaleString()}\n`;

            if (prevMsg && prevMsg.created_at) {
                const prevTime = new Date(prevMsg.created_at);
                const duration = Math.floor((timestamp - prevTime) / 1000);
                if (duration > 0) {
                    const mins = Math.floor(duration / 60);
                    const secs = duration % 60;
                    if (mins > 0) {
                        output += `Duration: ${mins}m ${secs}s\n`;
                    } else {
                        output += `Duration: ${secs}s\n`;
                    }
                }
            }
        }

        output += `${'-'.repeat(80)}\n`;

        if (typeof msg.content === 'string') {
            output += msg.content + '\n';
        } else if (Array.isArray(msg.content)) {
            // Separate by block type
            const textBlocks = msg.content.filter(b => b.type === 'text');
            const thinkingBlocks = msg.content.filter(b => b.type === 'thinking');
            const toolUseBlocks = msg.content.filter(b => b.type === 'tool_use');

            // Show thinking first (if any)
            if (thinkingBlocks.length > 0) {
                output += `\n[AI THINKING]:\n`;
                thinkingBlocks.forEach(block => {
                    output += block.thinking + '\n';
                });
                output += '\n';
            }

            // Show text content
            if (textBlocks.length > 0) {
                output += `[AI TEXT]:\n`;
                textBlocks.forEach(block => {
                    output += (block.text || block.content || '') + '\n';
                });
                output += '\n';
            }

            // Show tool usage
            if (toolUseBlocks.length > 0) {
                output += `[AI TOOL USE]:\n`;
                toolUseBlocks.forEach(block => {
                    output += `Tool: ${block.name}\n`;
                    output += `ID: ${block.id}\n`;
                    if (block.input) {
                        output += `Input: ${JSON.stringify(block.input, null, 2)}\n`;
                    }
                    output += '\n';
                });
            }
        }

        output += '\n';
        return output;
    },



    // ==================== ADD TO thread-manager-interactions.js ====================

    /**
     * Copy session ID to clipboard
     */
    copySessionId(sessionId, buttonElement) {
        navigator.clipboard.writeText(sessionId).then(() => {
            console.log('📋 [Interactions] Session ID copied:', sessionId);

            // Visual feedback
            const icon = buttonElement.querySelector('i');
            const originalClass = icon.className;
            icon.className = 'fas fa-check';
            buttonElement.classList.add('copied');

            if (typeof showNotification === 'function') {
                showNotification('Session ID copied to clipboard', 'success', 2000);
            }

            // Reset after 2 seconds
            setTimeout(() => {
                icon.className = originalClass;
                buttonElement.classList.remove('copied');
            }, 2000);
        }).catch(err => {
            console.error('❌ [Interactions] Failed to copy session ID:', err);
            if (typeof showNotification === 'function') {
                showNotification('Failed to copy session ID', 'error', 2000);
            }
        });
    },

    /**
     * Open thread in Prime (simpler version - just switches tab)
     */
    openThreadInPrime(threadId) {
        console.log('📖 [Interactions] Opening thread in Prime AI:', threadId);

        const primeTab = document.querySelector('[data-chat-id="prime"]');
        if (primeTab) primeTab.click();

        this.switchThread(threadId, true); // Force switch
        this.closeThreadMenu();

        if (typeof showNotification === 'function') {
            showNotification('Thread opened in Prime AI', 'success', 2000);
        }
    },

    /**
     * Start rename (inline editing - different from startInlineTitleEdit)
     */
    startRename(threadId) {
        const titleSpan = document.getElementById(`thread-title-${threadId}`);
        if (!titleSpan) return;

        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) return;

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'thread-item-title-input';
        input.value = thread.title;

        titleSpan.replaceWith(input);
        input.focus();
        input.select();

        const saveRename = async () => {
            const newTitle = input.value.trim();
            if (newTitle && newTitle !== thread.title) {
                thread.title = newTitle;
                thread.updated = new Date().toISOString();

                // Save to backend
                try {
                    await fetch(`${this.apiBaseUrl}/api/threads/${threadId}/update`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name: newTitle })
                    });
                    console.log('✅ [Interactions] Thread renamed to:', newTitle);
                } catch (error) {
                    console.error('❌ [Interactions] Failed to save rename:', error);
                }
            }

            if (typeof this.renderThreadList === 'function') {
                this.renderThreadList();
            }
        };

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                saveRename();
            } else if (e.key === 'Escape') {
                e.preventDefault();
                if (typeof this.renderThreadList === 'function') {
                    this.renderThreadList();
                }
            }
        });

        input.addEventListener('blur', saveRename);
    },

    /**
     * Show Synergy Session selector dropdown
     */
    async showSynergySessionSelector(buttonElement) {
        try {
            // Fetch Synergy sessions
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/list`, {
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                console.warn('Synergy sessions API not available, using generic tag');
                // Just mark as selected without specific ID
                buttonElement.classList.add('selected');
                return;
            }

            const data = await response.json();
            // Handle different response formats
            let sessions = [];
            if (Array.isArray(data)) {
                sessions = data;
            } else if (data && data.success && Array.isArray(data.sessions)) {
                sessions = data.sessions;
            } else if (data && Array.isArray(data.sessions)) {
                sessions = data.sessions;
            }

            if (sessions.length === 0) {
                console.log('No Synergy sessions found, using generic tag');
                buttonElement.classList.add('selected');
                return;
            }

            // Create dropdown selector
            const dropdownHTML = sessions.map(session => `
                <div class="resource-selector-item" data-id="${session.session_id}">
                    <div class="resource-title">${session.title || session.session_id}</div>
                    <div class="resource-meta">${session.status || 'N/A'} • ${session.priority || 'Normal'}</div>
                </div>
            `).join('');

            const dropdown = document.createElement('div');
            dropdown.className = 'resource-selector-dropdown';
            dropdown.innerHTML = `
                <div class="resource-selector-header">Select Synergy Session</div>
                <div class="resource-selector-list">${dropdownHTML}</div>
            `;

            // Position dropdown below button
            const rect = buttonElement.getBoundingClientRect();
            dropdown.style.position = 'absolute';
            dropdown.style.top = `${rect.bottom + 5}px`;
            dropdown.style.left = `${rect.left}px`;
            dropdown.style.zIndex = '10000';

            document.body.appendChild(dropdown);

            // Handle selection
            dropdown.querySelectorAll('.resource-selector-item').forEach(item => {
                item.addEventListener('click', () => {
                    const sessionId = item.dataset.id;
                    const sessionTitle = item.querySelector('.resource-title').textContent;

                    // Mark button as selected with specific ID
                    buttonElement.classList.add('selected');
                    buttonElement.dataset.specificId = `synergy:${sessionId}`;

                    // Add label to show selected session
                    let label = buttonElement.querySelector('.tag-specific-label');
                    if (!label) {
                        label = document.createElement('div');
                        label.className = 'tag-specific-label';
                        buttonElement.appendChild(label);
                    }
                    label.textContent = sessionTitle.substring(0, 20);

                    dropdown.remove();
                });
            });

            // Close on outside click
            setTimeout(() => {
                document.addEventListener('click', function closeDropdown(e) {
                    if (!dropdown.contains(e.target) && e.target !== buttonElement) {
                        dropdown.remove();
                        document.removeEventListener('click', closeDropdown);
                    }
                });
            }, 100);

        } catch (error) {
            console.error('Failed to load Synergy sessions:', error);
            alert('Error loading Synergy sessions');
        }
    },

    /**
     * Show Workflow/Automation selector dropdown
     */
    async showWorkflowSelector(buttonElement, tagType) {
        try {
            // Fetch workflows/automations
            const response = await fetch(`${this.apiBaseUrl}/api/automation/list`, {
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                console.warn('Workflows API not available, using generic tag');
                buttonElement.classList.add('selected');
                return;
            }

            const data = await response.json();

            // Handle different response formats
            let workflows = [];
            if (Array.isArray(data)) {
                workflows = data;
            } else if (data && data.success && Array.isArray(data.workflows)) {
                workflows = data.workflows;
            } else if (data && Array.isArray(data.workflows)) {
                workflows = data.workflows;
            } else if (data && Array.isArray(data.automations)) {
                workflows = data.automations;
            }

            if (!workflows || workflows.length === 0) {
                console.log(`No ${tagType}s found, using generic tag`);
                buttonElement.classList.add('selected');
                return;
            }

            // Create dropdown selector
            const dropdownHTML = workflows.map(workflow => `
                <div class="resource-selector-item" data-slug="${workflow.slug}">
                    <div class="resource-title">${workflow.title || workflow.slug}</div>
                    <div class="resource-meta">${workflow.status || 'Inactive'} • ${workflow.trigger_type || 'Manual'}</div>
                </div>
            `).join('');

            const dropdown = document.createElement('div');
            dropdown.className = 'resource-selector-dropdown';
            dropdown.innerHTML = `
                <div class="resource-selector-header">Select ${tagType === 'automation' ? 'Automation' : 'Workflow'}</div>
                <div class="resource-selector-list">${dropdownHTML}</div>
            `;

            // Position dropdown
            const rect = buttonElement.getBoundingClientRect();
            dropdown.style.position = 'absolute';
            dropdown.style.top = `${rect.bottom + 5}px`;
            dropdown.style.left = `${rect.left}px`;
            dropdown.style.zIndex = '10000';

            document.body.appendChild(dropdown);

            // Handle selection
            dropdown.querySelectorAll('.resource-selector-item').forEach(item => {
                item.addEventListener('click', () => {
                    const slug = item.dataset.slug;
                    const title = item.querySelector('.resource-title').textContent;

                    buttonElement.classList.add('selected');
                    buttonElement.dataset.specificId = `${tagType}:${slug}`;

                    let label = buttonElement.querySelector('.tag-specific-label');
                    if (!label) {
                        label = document.createElement('div');
                        label.className = 'tag-specific-label';
                        buttonElement.appendChild(label);
                    }
                    label.textContent = title.substring(0, 20);

                    dropdown.remove();
                });
            });

            setTimeout(() => {
                document.addEventListener('click', function closeDropdown(e) {
                    if (!dropdown.contains(e.target) && e.target !== buttonElement) {
                        dropdown.remove();
                        document.removeEventListener('click', closeDropdown);
                    }
                });
            }, 100);

        } catch (error) {
            console.error('Failed to load workflows:', error);
            alert('Error loading workflows');
        }
    },

    /**
     * Show Internal Doc selector dropdown
     */
    async showInternalDocSelector(buttonElement) {
        try {
            // Fetch internal docs from Synergy docs using DocumentService
            const data = await documentService.fetchAllDocuments();

            // Handle different response formats
            let docs = [];
            if (Array.isArray(data)) {
                docs = data;
            } else if (data && data.success && Array.isArray(data.docs)) {
                docs = data.docs;
            } else if (data && Array.isArray(data.docs)) {
                docs = data.docs;
            }

            if (!docs || docs.length === 0) {
                console.log('No internal documents found, using generic tag');
                buttonElement.classList.add('selected');
                return;
            }

            const dropdownHTML = docs.map(doc => `
                <div class="resource-selector-item" data-slug="${doc.slug}">
                    <div class="resource-title">${doc.title || doc.slug}</div>
                    <div class="resource-meta">${doc.type || 'Document'}</div>
                </div>
            `).join('');

            const dropdown = document.createElement('div');
            dropdown.className = 'resource-selector-dropdown';
            dropdown.innerHTML = `
                <div class="resource-selector-header">Select Internal Document</div>
                <div class="resource-selector-list">${dropdownHTML}</div>
            `;

            const rect = buttonElement.getBoundingClientRect();
            dropdown.style.position = 'absolute';
            dropdown.style.top = `${rect.bottom + 5}px`;
            dropdown.style.left = `${rect.left}px`;
            dropdown.style.zIndex = '10000';

            document.body.appendChild(dropdown);

            dropdown.querySelectorAll('.resource-selector-item').forEach(item => {
                item.addEventListener('click', () => {
                    const slug = item.dataset.slug;
                    const title = item.querySelector('.resource-title').textContent;

                    buttonElement.classList.add('selected');
                    buttonElement.dataset.specificId = `internal-doc:${slug}`;

                    let label = buttonElement.querySelector('.tag-specific-label');
                    if (!label) {
                        label = document.createElement('div');
                        label.className = 'tag-specific-label';
                        buttonElement.appendChild(label);
                    }
                    label.textContent = title.substring(0, 20);

                    dropdown.remove();
                });
            });

            setTimeout(() => {
                document.addEventListener('click', function closeDropdown(e) {
                    if (!dropdown.contains(e.target) && e.target !== buttonElement) {
                        dropdown.remove();
                        document.removeEventListener('click', closeDropdown);
                    }
                });
            }, 100);

        } catch (error) {
            console.error('Failed to load internal docs:', error);
            alert('Error loading internal documents');
        }
    },

    /**
     * Show Email selector dropdown
     */
    async showEmailSelector(buttonElement) {
        try {
            // Fetch recent emails from Communication Hub
            const response = await fetch(`${this.apiBaseUrl}/api/emails/recent?limit=20`, {
                headers: { 'Content-Type': 'application/json' }
            });

            // Check if endpoint exists (may not be implemented yet)
            if (response.status === 404 || !response.ok) {
                console.warn('Email API not available, using generic tag');
                buttonElement.classList.add('selected');
                return;
            }

            const emails = await response.json();

            if (!emails || emails.length === 0) {
                alert('No recent emails found. Check Communication Hub.');
                return;
            }

            const dropdownHTML = emails.map(email => `
                <div class="resource-selector-item" data-id="${email.id}">
                    <div class="resource-title">${email.subject || 'No Subject'}</div>
                    <div class="resource-meta">${email.from || 'Unknown'} • ${email.date || ''}</div>
                </div>
            `).join('');

            const dropdown = document.createElement('div');
            dropdown.className = 'resource-selector-dropdown';
            dropdown.innerHTML = `
                <div class="resource-selector-header">Select Email Thread</div>
                <div class="resource-selector-list">${dropdownHTML}</div>
            `;

            const rect = buttonElement.getBoundingClientRect();
            dropdown.style.position = 'absolute';
            dropdown.style.top = `${rect.bottom + 5}px`;
            dropdown.style.left = `${rect.left}px`;
            dropdown.style.zIndex = '10000';

            document.body.appendChild(dropdown);

            dropdown.querySelectorAll('.resource-selector-item').forEach(item => {
                item.addEventListener('click', () => {
                    const emailId = item.dataset.id;
                    const subject = item.querySelector('.resource-title').textContent;

                    buttonElement.classList.add('selected');
                    buttonElement.dataset.specificId = `email:${emailId}`;

                    let label = buttonElement.querySelector('.tag-specific-label');
                    if (!label) {
                        label = document.createElement('div');
                        label.className = 'tag-specific-label';
                        buttonElement.appendChild(label);
                    }
                    label.textContent = subject.substring(0, 20);

                    dropdown.remove();
                });
            });

            setTimeout(() => {
                document.addEventListener('click', function closeDropdown(e) {
                    if (!dropdown.contains(e.target) && e.target !== buttonElement) {
                        dropdown.remove();
                        document.removeEventListener('click', closeDropdown);
                    }
                });
            }, 100);

        } catch (error) {
            console.error('Failed to load emails:', error);
            alert('Error loading emails');
        }
    }





});

console.log('✅ ThreadManager-Interactions module loaded');