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
     * CRITICAL FIX (Dec 13, 2025):
     * - Uses event.target.closest() to find the ACTUAL clicked card
     * - Prevents querySelector() from returning wrong card when same thread in multiple locations
     * - Ensures expansion happens in correct location (History vs Agent vs Prime)
     * 
     * @param {Event} event - Click event (for stopPropagation)
     * @param {string} threadId - Thread ID to toggle
     */
    toggleCard(event, threadId) {
        // CRITICAL: Prevent event bubbling (don't trigger double-click or parent handlers)
        if (event) {
            if (typeof event.stopPropagation === 'function') {
                event.stopPropagation();
            }
            if (typeof event.preventDefault === 'function') {
                event.preventDefault();
            }
            // Only call stopImmediatePropagation if it exists (not all event objects have it)
            if (typeof event.stopImmediatePropagation === 'function') {
                event.stopImmediatePropagation();
            }
        }

        // ✅ FIX: Use event.target to find the ACTUAL clicked card (location-aware)
        // This prevents querySelector() from finding the wrong card when same thread is in multiple locations
        let card = null;
        if (event && event.target) {
            card = event.target.closest('.ai-chat-header-info, .agent-thread-card');
        }

        // Fallback to old method if event.target didn't work
        if (!card) {
            card = this.findCardElement(threadId);
        }

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
        const location = card.dataset.location || 'unknown';
        console.log(`[ThreadCardExpansion] Toggling ${threadId} at ${location}: ${isExpanded ? 'collapse' : 'expand'}`);

        if (isExpanded) {
            this.collapseCard(threadId, card);
        } else {
            this.expandCard(threadId, card);
        }
    },

    /**
     * Expand a specific thread card
     * 
     * @param {string} threadId - Thread ID to expand
     * @param {HTMLElement} card - Optional: Card element (for location-aware expansion)
     */
    expandCard(threadId, card = null) {
        // Use provided card or find it
        if (!card) {
            card = this.findCardElement(threadId);
        }
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
     * @param {HTMLElement} card - Optional: Card element (for location-aware collapse)
     */
    collapseCard(threadId, card = null) {
        // Use provided card or find it
        if (!card) {
            card = this.findCardElement(threadId);
        }
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
     * Searches across all locations (prime, agent-1 through agent-26, thread-history, synergy, etc.)
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
     * - Prime: The #prime-thread-info container
     * - Agent columns: The #thread-info-N container
     * 
     * CRITICAL FIX (Dec 12, 2025):
     * Check ACTUAL parent container in DOM, NOT data-location attribute!
     * Thread History cards can have data-location="prime" or "agent-1" but physically live in .thread-list
     * 
     * BUG FIXED: Previous logic used closest() which would traverse UP and find containers that
     * the card isn't actually inside. Now we check if card is DIRECTLY CONTAINED within the container.
     * 
     * @param {HTMLElement} card - The thread card element
     * @returns {HTMLElement|null} Element to add .expanded class to
     */
    getExpandableElement(card) {
        if (!card) return null;

        // CRITICAL: Check DIRECT containment, not just closest() match
        // Order matters: check most specific containers first

        // 1. Check if card is inside .thread-list (Thread History sidebar)
        const parentThreadList = card.closest('.thread-list');
        if (parentThreadList && parentThreadList.contains(card)) {
            // Card is in Thread History → expand the CARD ITSELF
            console.log(`[ThreadCardExpansion] Expandable: card itself (in .thread-list)`);
            return card;
        }

        // 2. Check if card is inside #prime-thread-info (Prime panel)
        // CRITICAL FIX (Dec 13, 2025): For Prime, expand the CARD ITSELF not the container
        // CSS selectors expect: #prime-thread-info .ai-chat-header-info.expanded
        // This means the .expanded class must be on the card, not the container
        const cardLocation = card.dataset.location;
        if (cardLocation === 'unassigned' || cardLocation === 'prime') {
            const parentPrimeContainer = card.closest('#prime-thread-info');
            if (parentPrimeContainer && parentPrimeContainer.contains(card)) {
                // Card is inside #prime-thread-info container → expand the CARD ITSELF
                // (NOT the container - the CSS selector requires .expanded on the card)
                console.log(`[ThreadCardExpansion] Expandable: card itself (in #prime-thread-info)`);
                return card;
            } else {
                // Card has prime location but no container (direct in panel) → expand card itself
                console.log(`[ThreadCardExpansion] Expandable: card itself (prime location, no container)`);
                return card;
            }
        }

        // 3. Check if card is inside agent column (#thread-info-1, #thread-info-2, etc.)
        const parentAgentContainer = card.closest('[id^="thread-info-"]');
        if (parentAgentContainer && parentAgentContainer.contains(card)) {
            // Card is in Agent column → expand the CARD ITSELF (not the container)
            // The container is the entire agent column, we only want to expand this specific card
            console.log(`[ThreadCardExpansion] Expandable: card itself (in ${parentAgentContainer.id})`);
            return card;
        }

        // Fallback: expand the card itself
        console.warn(`[ThreadCardExpansion] No known container found, using card itself`);
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
