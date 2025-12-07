/**
 * FILE: UI/external/modules/thread-cards/thread-card-expansion.js
 * PURPOSE: Click-based expansion controller for thread cards (replaces hover behavior)
 * 
 * DEPENDENCIES:
 * - ThreadManager (from business-ai-platform-v2.html)
 * - thread-card-styles.css (for .expanded class)
 * 
 * EXPORTS:
 * - ThreadCardExpansion.toggleCard(event, threadId) - Toggle expansion on click
 * - ThreadCardExpansion.expandCard(threadId) - Expand specific card
 * - ThreadCardExpansion.collapseCard(threadId) - Collapse specific card
 * - ThreadCardExpansion.collapseAll() - Collapse all cards
 * 
 * USED BY:
 * - thread-card-templates.js (chevron button onclick)
 * 
 * RELATED FILES:
 * - thread-card-templates.js (HTML templates with chevron buttons)
 * - thread-card-styles.css (expansion animations)
 * 
 * NOTES:
 * - Replaced hover-based expansion (Nov 24, 2025)
 * - Allows multiple cards to be expanded simultaneously
 * - Chevron rotates 180deg when expanded
 * - Click outside does NOT collapse (user-controlled state)
 * - Double-click on title still loads thread into Prime
 * 
 * LAST MODIFIED: 2025-11-24 - Created to replace hover expansion
 */

window.ThreadCardExpansion = {

    /**
     * Toggle expansion state of a thread card
     * Called by chevron button click
     * 
     * @param {Event} event - Click event (for stopPropagation)
     * @param {string} threadId - Thread ID to toggle
     */
    toggleCard(event, threadId) {
        // CRITICAL: Prevent event bubbling (don't trigger double-click or parent handlers)
        if (event) {
            event.stopPropagation();
            event.preventDefault();
            event.stopImmediatePropagation(); // Stop ALL handlers on this element
        }

        const card = this.findCardElement(threadId);
        if (!card) {
            console.warn(`[ThreadCardExpansion] Card not found for ID: ${threadId}`);
            return;
        }

        const isExpanded = card.classList.contains('expanded');
        console.log(`[ThreadCardExpansion] Toggling ${threadId}: ${isExpanded ? 'collapse' : 'expand'}`);

        if (isExpanded) {
            this.collapseCard(threadId);
        } else {
            this.expandCard(threadId);
        }
    },

    /**
     * Expand a specific thread card
     * 
     * @param {string} threadId - Thread ID to expand
     */
    expandCard(threadId) {
        const card = this.findCardElement(threadId);
        if (!card) return;

        card.classList.add('expanded');

        // Update aria label
        const btn = card.querySelector('.thread-card-expand-btn');
        if (btn) {
            btn.setAttribute('aria-label', 'Collapse details');
            btn.setAttribute('title', 'Click to collapse details');
        }
    },

    /**
     * Collapse a specific thread card
     * 
     * @param {string} threadId - Thread ID to collapse
     */
    collapseCard(threadId) {
        const card = this.findCardElement(threadId);
        if (!card) return;

        card.classList.remove('expanded');

        // Update aria label
        const btn = card.querySelector('.thread-card-expand-btn');
        if (btn) {
            btn.setAttribute('aria-label', 'Expand details');
            btn.setAttribute('title', 'Click to expand details');
        }
    },

    /**
     * Collapse all expanded thread cards
     * Useful for "reset view" functionality
     */
    collapseAll() {
        const expandedCards = document.querySelectorAll('.ai-chat-header-info.expanded');
        expandedCards.forEach(card => {
            const threadId = card.dataset.threadId;
            if (threadId) {
                this.collapseCard(threadId);
            }
        });
    },

    /**
     * Find thread card element by thread ID
     * Searches across all locations (prime, agent-1, agent-2, agent-3, thread-history, prime-loaded, etc.)
     * 
     * @param {string} threadId - Thread ID to find
     * @returns {HTMLElement|null} Thread card element or null
     */
    findCardElement(threadId) {
        // PRIORITY 1: Search by data-thread-id attribute (works for ALL card types)
        // This includes thread-history, prime-loaded, and agent cards
        const cardByData = document.querySelector(`.ai-chat-header-info[data-thread-id="${threadId}"]`);
        if (cardByData) {
            console.log(`[ThreadCardExpansion] Found card by data-thread-id: ${threadId}`);
            return cardByData;
        }

        // PRIORITY 2: Search by agent-thread-card class (for agent panel cards)
        const agentCard = document.querySelector(`.agent-thread-card[data-thread-id="${threadId}"]`);
        if (agentCard) {
            console.log(`[ThreadCardExpansion] Found card by agent-thread-card class: ${threadId}`);
            return agentCard;
        }

        // PRIORITY 3: Try all possible static location IDs (legacy fallback)
        const locations = [
            'prime-thread-info',       // Prime panel
            'prime-loaded-thread-info', // Prime-Loaded panel
            'thread-history-thread-info', // Thread History panel
            'thread-info-1',           // Agent 1
            'thread-info-2',           // Agent 2
            'thread-info-3',           // Agent 3
            'thread-info-4',           // Agent 4
            'thread-info-5',           // Agent 5
            'thread-info-6',           // Agent 6
            'thread-info-7',           // Agent 7
        ];

        for (const locationId of locations) {
            const card = document.getElementById(locationId);
            if (card && card.dataset.threadId === threadId) {
                console.log(`[ThreadCardExpansion] Found card by static ID: ${locationId}`);
                return card;
            }
        }

        console.warn(`[ThreadCardExpansion] Card not found for thread ID: ${threadId}`);
        return null;
    },

    /**
     * Check if a card is currently expanded
     * 
     * @param {string} threadId - Thread ID to check
     * @returns {boolean} True if expanded
     */
    isExpanded(threadId) {
        const card = this.findCardElement(threadId);
        return card ? card.classList.contains('expanded') : false;
    },

    /**
     * Expand card by location ID (for backward compatibility)
     * 
     * @param {string} locationId - Location ID (e.g., "prime-thread-info")
     */
    expandByLocation(locationId) {
        const card = document.getElementById(locationId);
        if (card && card.dataset.threadId) {
            this.expandCard(card.dataset.threadId);
        }
    },

    /**
     * Collapse card by location ID (for backward compatibility)
     * 
     * @param {string} locationId - Location ID (e.g., "prime-thread-info")
     */
    collapseByLocation(locationId) {
        const card = document.getElementById(locationId);
        if (card && card.dataset.threadId) {
            this.collapseCard(card.dataset.threadId);
        }
    }

};

// Auto-initialize (no setup needed)
console.log('[Thread Card Expansion] Click-based expansion loaded');
