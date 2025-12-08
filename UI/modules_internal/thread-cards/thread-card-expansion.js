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

        // Get the element that should have .expanded class (card or container)
        const expandableElement = this.getExpandableElement(card);
        if (!expandableElement) {
            console.warn(`[ThreadCardExpansion] Expandable element not found for ID: ${threadId}`);
            return;
        }

        const isExpanded = expandableElement.classList.contains('expanded');
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

        // Get the element that should receive the .expanded class
        const expandableElement = this.getExpandableElement(card);
        if (!expandableElement) return;

        expandableElement.classList.add('expanded');

        // Update aria label on button (search from the card, not the container)
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

        // Get the element that has the .expanded class
        const expandableElement = this.getExpandableElement(card);
        if (!expandableElement) return;

        expandableElement.classList.remove('expanded');

        // Update aria label on button (search from the card, not the container)
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
     * CRITICAL BEHAVIOR (Dec 9, 2025 - FIXED):
     * - ALWAYS returns the CARD element itself (the element with data-thread-id)
     * - Expansion logic handles finding the correct parent container if needed
     * - This ensures the button inside the card can be found
     * 
     * @param {string} threadId - Thread ID to find
     * @returns {HTMLElement|null} Thread card element (always the .ai-chat-header-info element)
     */
    findCardElement(threadId) {
        // Search by data-thread-id attribute (works for ALL card types)
        const card = document.querySelector(`.ai-chat-header-info[data-thread-id="${threadId}"]`);
        if (card) {
            const location = card.dataset.location || 'unknown';
            console.log(`[ThreadCardExpansion] Found card by data-thread-id: ${threadId} at location: ${location}`);
            return card;
        }

        // Fallback: Search by agent-thread-card class
        const agentCard = document.querySelector(`.agent-thread-card[data-thread-id="${threadId}"]`);
        if (agentCard) {
            console.log(`[ThreadCardExpansion] Found card by agent-thread-card class: ${threadId}`);
            return agentCard;
        }

        console.warn(`[ThreadCardExpansion] Card not found for thread ID: ${threadId}`);
        return null;
    },

    /**
     * Get the element that should have the .expanded class added
     * - Thread History: The card itself
     * - Prime/Prime-Loaded: The #prime-thread-info container
     * - Agent columns: The #thread-info-N container
     * 
     * @param {HTMLElement} card - The thread card element
     * @returns {HTMLElement|null} Element to add .expanded class to
     */
    getExpandableElement(card) {
        if (!card) return null;

        // Check actual parent container to determine location
        // (don't trust data-location, as cards can have prime-loaded but be in thread history)
        const isInThreadHistory = card.closest('.thread-history-panel');
        const isInPrimeContainer = card.closest('#prime-thread-info');
        const agentContainer = card.closest('[id^="thread-info-"]');

        // Thread History: expand the card itself
        if (isInThreadHistory) {
            console.log(`[ThreadCardExpansion] Expandable element: card itself (in thread-history panel)`);
            return card;
        }

        // Prime/Prime-Loaded: expand the container
        if (isInPrimeContainer) {
            console.log(`[ThreadCardExpansion] Expandable element: #prime-thread-info container`);
            return isInPrimeContainer;
        }

        // Agent columns: expand the parent container
        if (agentContainer) {
            console.log(`[ThreadCardExpansion] Expandable element: container ${agentContainer.id}`);
            return agentContainer;
        }

        // Fallback: expand the card itself
        console.warn(`[ThreadCardExpansion] No container found, using card itself`);
        return card;
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
