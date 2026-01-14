/**
 * FILE: UI/modules/agent-status-indicator.js
 * PURPOSE: Isolated status indicator system for Prime AI and individual agents
 * 
 * DEPENDENCIES:
 * - None (standalone module)
 * 
 * EXPORTS:
 * - AgentStatusIndicator.update(status, agentId) - Update status for specific agent
 * - AgentStatusIndicator.clear(agentId) - Clear status for specific agent
 * - AgentStatusIndicator.clearAll() - Clear all status indicators
 * 
 * USED BY:
 * - business-ai-platform-v2.html (Prime AI chat)
 * - MultiAgent system (agent columns)
 * 
 * NOTES:
 * - Supports isolated status per agent (prevents all icons glowing at once)
 * - Status types: thinking, tool-running, tool-success, writing
 * - agentId null = Prime AI, agentId number = specific agent
 * 
 * LAST MODIFIED: 2025-11-21 - Initial creation
 */

const AgentStatusIndicator = {
    /**
     * Status types supported
     */
    STATUS_TYPES: {
        THINKING: 'thinking',
        TOOL_RUNNING: 'tool-running',
        TOOL_SUCCESS: 'tool-success',
        WRITING: 'writing'
    },

    /**
     * All status classes for removal
     */
    ALL_STATUS_CLASSES: [
        'status-thinking',
        'status-tool-running',
        'status-tool-success',
        'status-writing'
    ],

    /**
     * Update status indicator for specific agent or Prime AI
     * @param {string} status - Status type (thinking, tool-running, tool-success, writing)
     * @param {number|null} agentId - Agent ID (null for Prime AI)
     */
    update(status, agentId = null) {
        if (agentId === null) {
            // Update Prime AI icon only
            this._updatePrimeIcon(status);
        } else {
            // Update specific agent icon only
            this._updateAgentIcon(status, agentId);
        }
    },

    /**
     * Clear status indicator for specific agent or Prime AI
     * @param {number|null} agentId - Agent ID (null for Prime AI)
     */
    clear(agentId = null) {
        this.update(null, agentId);
    },

    /**
     * Clear all status indicators (Prime + all agents)
     */
    clearAll() {
        // Clear Prime
        this._updatePrimeIcon(null);

        // Clear all agent icons (try both new and old structure)
        const agentIcons = document.querySelectorAll('.agent-title-wrapper i, .agent-header h2 i');
        agentIcons.forEach(icon => {
            icon.classList.remove(...this.ALL_STATUS_CLASSES);
        });

        // ✨ NEW: Clear all quick-nav-badge status classes
        const badges = document.querySelectorAll('.agent-quick-nav-badge');
        badges.forEach(badge => {
            badge.classList.remove(...this.ALL_STATUS_CLASSES);
        });

        console.log('[STATUS] All indicators cleared (icons + badges)');
    },

    /**
     * Update Prime AI icon status
     * @private
     */
    _updatePrimeIcon(status) {
        const primeIcon = document.querySelector('.ai-chat-title .ai-icon');
        if (!primeIcon) {
            console.warn('[STATUS] Prime AI icon not found');
            return;
        }

        // Remove all status classes
        primeIcon.classList.remove(...this.ALL_STATUS_CLASSES);

        // Add new status class if provided
        if (status) {
            primeIcon.classList.add(`status-${status}`);
            console.log(`[STATUS] Prime AI: ${status}`);
        } else {
            console.log('[STATUS] Prime AI: idle');
        }
    },

    /**
     * Update specific agent icon status
     * @private
     */
    _updateAgentIcon(status, agentId) {
        // Try multiple selector strategies to find the agent icon
        let agentIcon = document.querySelector(`#agent-${agentId} .agent-title-wrapper i`);

        if (!agentIcon) {
            // Fallback: try finding by data attribute
            const agentColumn = document.querySelector(`.agent-column[data-agent-id="${agentId}"]`);
            if (agentColumn) {
                agentIcon = agentColumn.querySelector('.agent-title-wrapper i');
            }
        }

        if (!agentIcon) {
            // Fallback: old structure (h2 i)
            agentIcon = document.querySelector(`#agent-${agentId} .agent-header h2 i`);
        }

        if (!agentIcon) {
            console.warn(`[STATUS] Agent ${agentId} icon not found`);
            return;
        }

        // Remove all status classes from icon
        agentIcon.classList.remove(...this.ALL_STATUS_CLASSES);

        // Add new status class to icon if provided
        if (status) {
            agentIcon.classList.add(`status-${status}`);
            // console.log(`[STATUS] Agent ${agentId}: ${status}`);
        } else {
            // console.log(`[STATUS] Agent ${agentId}: idle`);
        }

        // ✨ NEW: Also update the quick-nav-badge with the same status
        this._updateQuickNavBadge(agentId, status);
    },

    /**
     * Update quick-nav-badge status indicator
     * @private
     */
    _updateQuickNavBadge(agentId, status) {
        const badge = document.querySelector(`.agent-quick-nav-badge[data-agent-id="${agentId}"]`);

        if (!badge) {
            // Badge might not exist yet (agent just created)
            return;
        }

        // Remove all status classes from badge
        badge.classList.remove(...this.ALL_STATUS_CLASSES);

        // Add new status class to badge if provided
        if (status) {
            badge.classList.add(`status-${status}`);
            // console.log(`[STATUS] Quick-nav badge ${agentId}: ${status}`);
        }
    },

    /**
     * Get current status of an agent
     * @param {number|null} agentId - Agent ID (null for Prime AI)
     * @returns {string|null} - Current status or null if idle
     */
    getStatus(agentId = null) {
        let icon;

        if (agentId === null) {
            icon = document.querySelector('.ai-chat-title .ai-icon');
        } else {
            icon = document.querySelector(`#agent-${agentId} .agent-title-wrapper i`);
            if (!icon) {
                const agentColumn = document.querySelector(`.agent-column[data-agent-id="${agentId}"]`);
                if (agentColumn) {
                    icon = agentColumn.querySelector('.agent-title-wrapper i');
                }
            }
            if (!icon) {
                // Fallback: old structure
                icon = document.querySelector(`#agent-${agentId} .agent-header h2 i`);
            }
        }

        if (!icon) return null;

        // Check which status class is active
        for (const statusClass of this.ALL_STATUS_CLASSES) {
            if (icon.classList.contains(statusClass)) {
                return statusClass.replace('status-', '');
            }
        }

        return null; // Idle
    },

    /**
     * Initialize module (verify CSS is loaded)
     */
    init() {
        console.log('[STATUS] AgentStatusIndicator module initialized');

        // Verify Prime icon exists
        const primeIcon = document.querySelector('.ai-chat-title .ai-icon');
        if (primeIcon) {
            console.log('[STATUS] Prime AI icon found');
        } else {
            console.warn('[STATUS] Prime AI icon not found - will retry on first update');
        }

        // Count agent icons
        const agentIcons = document.querySelectorAll('.agent-header h2 i');
        console.log(`[STATUS] ${agentIcons.length} agent icon(s) found`);
    }
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => AgentStatusIndicator.init());
} else {
    AgentStatusIndicator.init();
}
