/**
 * FILE: UI/modules/thread-manager/thread-manager-interactions.js
 * PURPOSE: User interactions - drag/drop, clicks, modals
 * 
 * DEPENDENCIES:
 * - UI/modules/thread-manager/thread-manager-core.js (must load first)
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
        if (!forceSwitch && thread.location && thread.location !== 'prime') {
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

        // CRITICAL: Set thread location to 'prime-loaded' (only ONE thread can be prime-loaded at a time)
        await this.assignThread(threadId, 'prime-loaded', true);
        console.log(`✅ [Interactions] Thread assigned to prime-loaded: ${threadId}`);

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
            console.log(`📋 [Interactions] Rendering ${thread.messages.length} messages...`);
            let renderedCount = 0;
            let skippedCount = 0;

            thread.messages.forEach((msg, idx) => {
                // Only render user and assistant messages
                // Skip: tool_use, tool_result (internal API mechanics)
                if (msg.role === 'user' || msg.role === 'assistant') {
                    // Check if message has actual text content
                    const hasTextContent = checkMessageHasTextContent(msg.content);

                    if (hasTextContent && typeof addChatMessage === 'function') {
                        addChatMessage(msg.role, msg.content);
                        renderedCount++;
                    } else {
                        if (window.DEBUG_TWO_RULE) {
                            console.log(`[Interactions] Skipping message ${idx + 1} (role: ${msg.role}, content type: ${typeof msg.content})`);
                        }
                        skippedCount++;
                    }
                } else {
                    // Skip tool messages
                    skippedCount++;
                }
            });

            console.log(`✅ [Interactions] Rendered ${renderedCount} messages, skipped ${skippedCount}`);
        }

        /**
         * Check if message content has actual text to display
         * @param {string|object|array} content - Message content
         * @returns {boolean} True if message has displayable text
         */
        function checkMessageHasTextContent(content) {
            if (typeof content === 'string' && content.trim()) {
                return true;
            }

            if (Array.isArray(content)) {
                // Check if any block has text or thinking
                return content.some(block =>
                    (block.type === 'text' && block.text && block.text.trim()) ||
                    (block.type === 'thinking' && block.thinking)
                );
            }

            if (content && typeof content === 'object') {
                if (content.type === 'text' && content.text && content.text.trim()) {
                    return true;
                }
                if (content.type === 'thinking' && content.thinking) {
                    return true;
                }
            }

            return false;
        }

        // Update AppState
        if (typeof AppState !== 'undefined') {
            // Ensure thread.messages is an array before spreading
            AppState.chatMessages = Array.isArray(thread.messages) ? [...thread.messages] : [];
            AppState.sessionId = threadId;
        }

        // Assign to Prime location (use 'prime-loaded' for page reload restoration)
        if (typeof this.assignThread === 'function') {
            await this.assignThread(threadId, 'prime-loaded');
        }

        // Update UI
        if (typeof this.updatePrimeHeader === 'function') {
            this.updatePrimeHeader(threadId);
        }
        if (typeof this.syncAppState === 'function') {
            this.syncAppState(threadId);
        }
        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList();
        }

        // Show input wrapper
        const primeInputWrapper = document.querySelector('.ai-chat-input-wrapper');
        if (primeInputWrapper) {
            primeInputWrapper.style.display = 'flex';
        }

        // Enable send button
        const primeSendBtn = document.querySelector('.send-btn');
        if (primeSendBtn) {
            primeSendBtn.disabled = false;
            primeSendBtn.style.opacity = '1';
        }

        console.log(`✅ [Interactions] Thread loaded in Prime: ${threadId}`);

        // Close thread menu
        this.closeThreadMenu();
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
                await this.assignThread(threadId, 'prime-loaded');
                await this.switchThread(threadId, true);
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
                await this.assignThread(threadId, 'prime-loaded');

                if (agentId && typeof MultiAgent !== 'undefined') {
                    MultiAgent.clearAgentThread?.(parseInt(agentId));
                }

                await this.loadThreadsFromBackend();
                await this.renderThreadList();

                if (typeof showNotification === 'function') {
                    showNotification('Thread unloaded from agent', 'success');
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

        const currentLocation = thread.location || 'prime';

        if (currentLocation === 'prime') {
            if (typeof showNotification === 'function') {
                showNotification('Thread is already in Prime', 'info');
            }
            return;
        }

        if (typeof showConfirmation === 'function') {
            showConfirmation(
                'Unload Thread?',
                `Move "${thread.title}" from ${currentLocation} back to Prime?`,
                async () => {
                    // CRITICAL FIX (Dec 12, 2025): Unload to 'prime' NOT 'prime-loaded'
                    // Unload means remove from agent and return to unassigned pool (prime)
                    // 'prime-loaded' is reserved for the ONE thread actively loaded in Prime panel
                    await this.assignThread(threadId, 'prime');

                    // Clear from agent - BOTH thread info AND messages
                    // CRITICAL FIX (Dec 15, 2025): Extract agentId from currentLocation and ALWAYS clear
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
                            agentBadge.className = 'thread-item-agent-badge prime';
                            agentBadge.innerHTML = '<i class="fas fa-crown"></i> Prime';
                        }

                        const unloadBtn = threadCard.querySelector('.thread-action-btn.unload');
                        if (unloadBtn) {
                            unloadBtn.remove();
                        }
                    }

                    await this.loadThreadsFromBackend();

                    if (typeof showNotification === 'function') {
                        showNotification('Thread moved to Prime', 'success');
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
        event.dataTransfer.setData('application/x-source-location', threadElement.dataset.currentLocation || 'prime');
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

        // Validate drop target - only allow drops in Prime or agent columns
        const validDropZone = event.target.closest('.agent-column, #ai-chat-panel');
        if (!validDropZone) {
            console.log('🚫 [Drop] Dropped outside valid zones (e.g., thread history) - no action');
            // Clear all drag-over states
            document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
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
        if (sourceLocation === targetLocation && targetLocation !== 'prime') {
            console.log('🔄 [Drop] Same location - no change needed');
            if (typeof showNotification === 'function') {
                showNotification('Thread already in this location', 'info');
            }
            return;
        }

        if (targetLocation === 'prime') {
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

            // Load in Prime using loadThreadInPrime (this will set prime-loaded internally)
            await this.loadThreadInPrime(threadId);

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
     * Setup drop zones for agent columns
     * Call this after creating new agent columns dynamically
     */
    setupAgentDropZones() {
        console.log('[ThreadManager] Setting up agent drop zones...');

        document.querySelectorAll('.agent-column').forEach(agentColumn => {
            // Skip if already has handler
            if (agentColumn.dataset.dropZoneConfigured === 'true') {
                return;
            }

            const agentId = parseInt(agentColumn.dataset.agentId);

            agentColumn.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.stopPropagation();
                e.dataTransfer.dropEffect = 'move';
                agentColumn.classList.add('drag-over');
            });

            agentColumn.addEventListener('dragleave', (e) => {
                // Only remove highlight if actually leaving container (not entering child element)
                // relatedTarget is where the mouse is going
                if (!agentColumn.contains(e.relatedTarget)) {
                    agentColumn.classList.remove('drag-over');
                }
            });

            agentColumn.addEventListener('drop', async (e) => {
                e.preventDefault();
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
     */
    setupPrimeDropZone() {
        console.log('[ThreadManager] Setting up Prime drop zone...');

        // Use the entire ai-chat-panel as drop zone (no visual overlay)
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

        primeContainer.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            e.dataTransfer.dropEffect = 'move';
            // NO visual drag-over class - just allow the drop
        });

        primeContainer.addEventListener('drop', async (e) => {
            e.preventDefault();

            const threadId = e.dataTransfer.getData('application/x-thread-id');
            if (!threadId) return;

            console.log(`📍 [Drop] Thread ${threadId} dropped on Prime`);

            // Call handleDrop with 'prime' location
            await this.handleDrop(e, 'prime');
        });

        primeContainer.dataset.dropZoneConfigured = 'true';
        console.log('✅ [Drop Zone] Prime configured (entire panel is drop area, no visual overlay)');
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
     * Show new chat modal
     */
    async showNewChatModal(location = 'prime', buttonElement = null) {
        console.log(`➕ [Interactions] Opening new chat modal for ${location}`);

        const locationName = location === 'prime' ? 'Prime Agent' :
            (location.startsWith('agent-') ? `Agent ${location.split('-')[1]}` : location);

        // Calculate modal position if button element provided
        let positionStyle = '';
        let overlayClass = '';
        if (buttonElement) {
            const rect = buttonElement.getBoundingClientRect();
            const modalWidth = 450;
            const modalHeight = 500;

            // Try to position to the right of button first
            let top = Math.max(10, rect.top);  // Keep at least 10px from top
            let left = rect.right + 12;  // Position to right with 12px gap

            // If modal would go off-screen to the right, position to the left
            if (left + modalWidth > window.innerWidth - 20) {
                left = rect.left - modalWidth - 12;
            }

            // If still off-screen, use center positioning
            if (left < 10) {
                left = (window.innerWidth - modalWidth) / 2;
            }

            // Adjust top if modal would go below viewport
            if (top + modalHeight > window.innerHeight - 20) {
                top = Math.max(10, window.innerHeight - modalHeight - 20);
            }

            positionStyle = `style="top: ${top}px; left: ${left}px; position: fixed;"`;
            overlayClass = 'positioned';
        }

        const modalHTML = `
            <div class="modal-overlay ${overlayClass}" id="newChatModalOverlay" onclick="if(event.target.id === 'newChatModalOverlay') { const modal = document.getElementById('newChatModalOverlay'); if (modal) modal.remove(); }">
                <div class="new-chat-modal" ${positionStyle} onclick="event.stopPropagation()">
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
                const newThreadId = await this.createThreadWithMetadata(title, allTags, location);

                // Close modal
                const modalOverlay = document.getElementById('newChatModalOverlay');
                if (modalOverlay) {
                    modalOverlay.remove();
                }

                // Load thread
                if (location === 'prime') {
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
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            console.error('❌ [Interactions] Thread not found:', threadId);
            if (typeof showNotification === 'function') {
                showNotification('Thread not found', 'error');
            }
            return;
        }

        // Fetch full messages if not loaded
        if (!thread.messages || thread.messages.length === 0) {
            console.log('📥 [Interactions] Fetching messages for thread:', threadId);
            const messages = await this.loadMessagesForThread(threadId);
            if (messages && messages.length > 0) {
                thread.messages = messages;
            } else {
                console.warn('⚠️ [Interactions] No messages found for thread');
                if (typeof showNotification === 'function') {
                    showNotification('No messages to copy', 'warning');
                }
                return;
            }
        }

        // Format the conversation
        let formattedText = '';
        formattedText += `THREAD: ${thread.title || 'Untitled'}\n`;
        formattedText += `ID: ${thread.id}\n`;
        formattedText += `DATE: ${new Date(thread.created_at || Date.now()).toLocaleString()}\n`;
        formattedText += `MESSAGES: ${thread.messages.length}\n`;
        formattedText += `${'='.repeat(80)}\n\n`;

        thread.messages.forEach((msg, index) => {
            if (msg.role === 'user') {
                formattedText += this._formatUserMessage(msg, index + 1);
            } else if (msg.role === 'assistant') {
                formattedText += this._formatAssistantMessage(msg, index + 1);
            }
        });

        // Copy to clipboard
        try {
            await navigator.clipboard.writeText(formattedText);
            console.log('✅ [Interactions] Copied full conversation:', threadId);
            if (typeof showNotification === 'function') {
                showNotification('Full conversation copied to clipboard', 'success', 2000);
            }
            // Close the menu
            this.toggleCopyMenu(threadId);
        } catch (err) {
            console.error('❌ [Interactions] Failed to copy conversation:', err);
            if (typeof showNotification === 'function') {
                showNotification('Failed to copy conversation', 'error');
            }
        }
    },

    /**
     * Format user message for copying
     * @private
     */
    _formatUserMessage(msg, index) {
        let output = `[${index}] USER MESSAGE:\n`;
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
    _formatAssistantMessage(msg, index) {
        let output = `[${index}] AI RESPONSE:\n`;
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
            const response = await fetch(`${this.apiBaseUrl}/api/synergy-sessions/list`, {
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to fetch Synergy sessions');

            const data = await response.json();
            const sessions = data.sessions || [];

            if (sessions.length === 0) {
                alert('No Synergy sessions found. Create a session first in the Synergy Dashboard.');
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
            const response = await fetch(`${this.apiBaseUrl}/api/automation/workflows/list`, {
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to fetch workflows');

            const workflows = await response.json();

            if (!workflows || workflows.length === 0) {
                alert(`No ${tagType}s found. Create one first in the Automation tab.`);
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
            // Fetch internal docs from Synergy docs
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-docs/list`, {
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to fetch internal docs');

            const docs = await response.json();

            if (!docs || docs.length === 0) {
                alert('No internal documents found. Create one first in Synergy Docs.');
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
            if (response.status === 404) {
                alert('Email selector not yet implemented. Please use generic "emails" tag or link email manually.');
                return;
            }

            if (!response.ok) throw new Error('Failed to fetch emails');

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