// ==================== THREAD MANAGER - SYNC MODULE ====================
/**
 * Master Synchronization System
 * Orchestrates all UI updates across the application
 * CRITICAL: This is the master coordinator for location changes
 */

window.ThreadManagerSync = {
    /**
     * Master sync function - updates thread location everywhere
     * Cascades updates to: database, UI, AppState, agent headers, sidebar
     */
    async syncThreadLocationEverywhere(threadId, frontendLocation, options = {}) {
        console.log(`🔄 [syncThreadLocationEverywhere] Syncing thread ${threadId} to ${frontendLocation}`);

        // Determine backend location mapping
        const backendLocation = frontendLocation === 'main' ? 'prime' : frontendLocation;

        // STEP 1: Update thread object in memory
        const thread = this.threads.find(t => t.id === threadId);
        if (thread) {
            thread.location = backendLocation;
            thread.agent = frontendLocation === 'main' ? null : frontendLocation;
            thread.updated = new Date().toISOString();

            // Handle metadata updates (synergy, workflow, tags)
            if (options.synergySessionId !== undefined) {
                thread.synergy_card_id = options.synergySessionId;
                thread.synergy_card_name = options.synergySessionName || null;
            }
            if (options.workflowId !== undefined) {
                thread.workflow_id = options.workflowId;
                thread.workflow_name = options.workflowName || null;
            }

            // Remove linkages if requested
            if (options.removeLinks) {
                if (options.removeLinks.includes('synergy')) {
                    thread.synergy_card_id = null;
                    thread.synergy_card_name = null;
                }
                if (options.removeLinks.includes('workflow')) {
                    thread.workflow_id = null;
                    thread.workflow_name = null;
                }
            }
        }

        // STEP 2: Update backend (ensure database sync)
        if (typeof this.assignThread === 'function') {
            await this.assignThread(threadId, backendLocation);
        }

        // STEP 3: Refresh ALL thread-info cards (agent columns, Prime, Synergy cards)
        if (typeof this.refreshAllThreadInfoCards === 'function') {
            this.refreshAllThreadInfoCards(threadId);
        }

        // STEP 4: Refresh sidebar (updates agent badge + UI pills)
        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList();
        }

        // STEP 5: Update Prime header if this is current thread
        if (this.currentThreadId === threadId && frontendLocation === 'main') {
            if (typeof this.updatePrimeHeader === 'function') {
                this.updatePrimeHeader(threadId);
            }
        }

        // STEP 6: Sync AppState
        if (typeof this.syncAppState === 'function') {
            this.syncAppState(threadId);
        }

        // STEP 7: Notify user
        const locationName = frontendLocation === 'main' ? 'Prime AI' :
            frontendLocation.startsWith('agent-') ? `Agent ${frontendLocation.replace('agent-', '')}` :
                frontendLocation;
        console.log(`✅ [syncThreadLocationEverywhere] Thread ${threadId} synced to ${locationName}`);

        return { success: true, location: frontendLocation };
    },

    /**
     * Refresh all thread-info cards for a specific thread across the entire UI
     * Also updates UI pills (Synergy, Workflow, etc.)
     */
    refreshAllThreadInfoCards(threadId) {
        console.log(`🔄 [refreshAllThreadInfoCards] Refreshing all cards for thread ${threadId}`);

        // Find all thread-info cards with this thread ID
        const threadCards = document.querySelectorAll(`[data-thread-id="${threadId}"]`);

        threadCards.forEach(card => {
            // Get the location from the card's context
            const location = card.getAttribute('data-location') || 'prime';

            // Re-render the card with updated agent info AND UI pills
            if (typeof this.renderThreadInfoContainer === 'function') {
                const newCardHTML = this.renderThreadInfoContainer(location, threadId, card.classList.contains('compact'));
                card.outerHTML = newCardHTML;
            }

            console.log(`✅ [refreshAllThreadInfoCards] Updated thread-info card at ${location}`);
        });

        // Also update sidebar thread items (shows UI pills)
        const thread = this.threads.find(t => t.id === threadId);
        if (thread) {
            const sidebarItem = document.querySelector(`[data-thread-id="${threadId}"].thread-item`);
            if (sidebarItem && typeof this.updateThreadPills === 'function') {
                this.updateThreadPills(sidebarItem, thread);
            }
        }
    },

    /**
     * Update UI pills on a thread item (Synergy=green, Workflow=orange, etc.)
     */
    updateThreadPills(threadElement, thread) {
        // Find or create pills container
        let pillsContainer = threadElement.querySelector('.thread-ui-pills');
        if (!pillsContainer) {
            pillsContainer = document.createElement('div');
            pillsContainer.className = 'thread-ui-pills';
            pillsContainer.style.cssText = 'display: flex; gap: 6px; margin-top: 6px; flex-wrap: wrap;';
            threadElement.appendChild(pillsContainer);
        }

        // Clear existing pills
        pillsContainer.innerHTML = '';

        // Add Synergy pill (green)
        if (thread.synergy_card_id) {
            const synergyPill = document.createElement('span');
            synergyPill.className = 'thread-pill thread-pill-synergy';
            synergyPill.style.cssText = 'background: #10b981; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; display: flex; align-items: center; gap: 4px;';
            synergyPill.innerHTML = `<i class="fas fa-link" style="font-size: 10px;"></i> Synergy`;
            synergyPill.title = thread.synergy_card_name || thread.synergy_card_id;
            pillsContainer.appendChild(synergyPill);
        }

        // Add Workflow pill (purple)
        if (thread.workflow_id) {
            const workflowPill = document.createElement('span');
            workflowPill.className = 'thread-pill thread-pill-workflow';
            workflowPill.style.cssText = 'background: #8b5cf6; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; display: flex; align-items: center; gap: 4px;';
            workflowPill.innerHTML = `<i class="fas fa-robot" style="font-size: 10px;"></i> Workflow`;
            workflowPill.title = thread.workflow_name || thread.workflow_id;
            pillsContainer.appendChild(workflowPill);
        }

        // Add Custom pills (extensible for future link types)
        if (thread.custom_links && Array.isArray(thread.custom_links)) {
            thread.custom_links.forEach(link => {
                const customPill = document.createElement('span');
                customPill.className = `thread-pill thread-pill-${link.type}`;
                customPill.style.cssText = `background: ${link.color || '#6366f1'}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; display: flex; align-items: center; gap: 4px;`;
                customPill.innerHTML = `<i class="fas ${link.icon || 'fa-link'}" style="font-size: 10px;"></i> ${link.label}`;
                customPill.title = link.description || link.id;
                pillsContainer.appendChild(customPill);
            });
        }
    },

    /**
     * Sync AppState with current thread
     */
    syncAppState(threadId) {
        const thread = this.threads.find(t => t.id === threadId);

        if (!thread) {
            if (typeof AppState !== 'undefined') {
                AppState.sessionId = null;
                AppState.chatMessages = [];
                AppState.threadTitle = null;
            }
            return;
        }

        if (typeof AppState !== 'undefined') {
            AppState.sessionId = thread.id;
            AppState.chatMessages = [...(thread.messages || [])];
            AppState.threadTitle = thread.title;
            AppState.currentLocation = thread.agent || 'main';
            console.log('✅ [syncAppState] Synced with thread:', thread.id);
        }
    }
};

console.log('✅ ThreadManager-Sync module loaded');