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

        // Clear panel status classes on every agent column.
        // (Prime panel is cleared implicitly above via
        //  _updatePrimeIcon(null) -> _updatePanel(null).)
        const agentPanels = document.querySelectorAll('.agent-column[data-agent-id]');
        agentPanels.forEach(panel => {
            panel.classList.remove(...this.ALL_STATUS_CLASSES);
        });

        console.log('[STATUS] All indicators cleared (icons + badges + panels)');
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

        // Mirror status onto the wrapping Prime panel so the border-pulse CSS
        // (.ai-chat-panel.status-X) fires in lock-step with the icon ring.
        this._updatePanel(status);
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

        // Mirror status onto the wrapping agent column so the border-pulse
        // CSS (.agent-column.status-X) fires in lock-step with the icon ring.
        this._updatePanel(status, agentId);
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
     * Update the wrapping panel (Prime or agent column) with the same status
     * class so the panel-border pulse system (CSS @keyframes panelStatusPulse)
     * fires in lock-step with the icon ring. Pass status=null to clear.
     *
     * Public consumers can read this state via isPanelBusy() to, e.g., reject
     * drop-while-busy at the drag/drop handler.
     *
     * @param {string|null} status - Status type or null to clear
     * @param {number|null} agentId - null for Prime AI; agent ID for an agent column
     * @private
     */
    _updatePanel(status, agentId = null) {
        let panel = null;

        if (agentId === null) {
            // Prime AI panel — only ever one of these in the DOM.
            panel = document.querySelector('.ai-chat-panel');
        } else {
            // Try the new agent-column attribute first, then fall back to the
            // legacy #agent-{id} element lookup so we survive the column rewrite.
            panel = document.querySelector(`.agent-column[data-agent-id="${agentId}"]`);
            if (!panel) {
                const agentEl = document.getElementById(`agent-${agentId}`);
                if (agentEl) {
                    panel = agentEl.closest('.agent-column') || agentEl;
                }
            }
        }

        if (!panel) {
            // Panel not in the DOM yet (e.g. agent not rendered). Silent no-op.
            return;
        }

        // Clear previous status, then apply new one (or none).
        panel.classList.remove(...this.ALL_STATUS_CLASSES);
        if (status) {
            panel.classList.add(`status-${status}`);
        }
    },

    /**
     * Public helper: returns true when the given panel element is currently
     * pulsing in any active status (thinking / tool-running / tool-success /
     * writing). Used by drop handlers to reject drops onto a busy AI panel.
     *
     * @param {Element|null} panelEl - .ai-chat-panel or .agent-column
     * @returns {boolean}
     */
    isPanelBusy(panelEl) {
        if (!panelEl || !panelEl.classList) return false;
        return this.ALL_STATUS_CLASSES.some(c => panelEl.classList.contains(c));
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

        // Verify panel targets exist for the border-pulse system. If this logs
        // "0 + 0", the agent-column rewrite hasn't run yet — _updatePanel will
        // silently no-op until panels appear, which is safe.
        const primePanel = document.querySelector('.ai-chat-panel');
        const agentPanels = document.querySelectorAll('.agent-column[data-agent-id]');
        console.log(
            `[STATUS] Panel targets: ${primePanel ? 1 : 0} Prime + ${agentPanels.length} agent(s)`
        );
    }
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => AgentStatusIndicator.init());
} else {
    AgentStatusIndicator.init();
}
