/**
 * FILE: UI/modules/agents/agent-ui.js
 * PURPOSE: Main orchestrator for agent UI system - coordinates column creation, input handling, messaging
 * 
 * FEATURES:
 * - Initialize agent columns with all components
 * - Coordinate between AgentColumn and AgentInput modules
 * - Provide unified API for agent management
 * - Handle agent lifecycle (create, destroy, reset)
 * 
 * DEPENDENCIES:
 * - agent-column.js (column management)
 * - agent-input.js (input handling)
 * - agent-ui.css (styling)
 * - ThreadManager (global, optional)
 * - MultiAgent (global, optional)
 * 
 * EXPORTS:
 * - AgentUI.initialize() - Initialize the agent UI system
 * - AgentUI.createAgent(agentId, agentName) - Create new agent
 * - AgentUI.removeAgent(agentId) - Remove agent
 * - AgentUI.getAgentInput(agentId) - Get input value
 * - AgentUI.setAgentInput(agentId, value) - Set input value
 * - AgentUI.focusAgent(agentId) - Focus agent input
 * - AgentUI.clearAgentInput(agentId) - Clear input and files
 * 
 * USED BY:
 * - business-ai-platform-v2.html (multi-agent section)
 * - MultiAgent system
 * 
 * LAST MODIFIED: 2025-11-15 - Initial extraction from monolithic HTML
 */

const AgentUI = (function () {
    'use strict';

    // Track initialized agents
    const initializedAgents = new Set();

    /**
     * Initialize the agent UI system
     */
    function initialize() {
        console.log('[AgentUI] Initializing agent UI system...');

        // Check if dependencies are loaded
        if (typeof AgentColumn === 'undefined') {
            console.error('[AgentUI] AgentColumn module not loaded');
            return false;
        }
        if (typeof AgentInput === 'undefined') {
            console.error('[AgentUI] AgentInput module not loaded');
            return false;
        }

        // Make modules available globally
        if (typeof window !== 'undefined') {
            window.AgentColumn = AgentColumn;
            window.AgentInput = AgentInput;
        }

        console.log('[AgentUI] Agent UI system ready');
        return true;
    }

    /**
     * Create a new agent column with full initialization
     * @param {number} agentId - Agent ID
     * @param {string} agentName - Agent display name (optional)
     * @param {HTMLElement} container - Container element (optional, uses default)
     * @returns {HTMLElement} Created column element
     */
    function createAgent(agentId, agentName = null, container = null) {
        // Prevent duplicate initialization
        if (initializedAgents.has(agentId)) {
            console.warn(`[AgentUI] Agent ${agentId} already initialized`);
            return document.getElementById(`agent-column-${agentId}`);
        }

        // Get or create container
        if (!container) {
            container = document.getElementById('multi-agent-columns');
            if (!container) {
                console.error('[AgentUI] No container found for agent columns');
                return null;
            }
        }

        // Create column using AgentColumn module
        const column = AgentColumn.create(agentId, agentName);

        // Insert before add-agent-bar (if exists), otherwise append
        const addAgentBar = container.querySelector('.add-agent-bar');
        if (addAgentBar) {
            container.insertBefore(column, addAgentBar);
        } else {
            container.appendChild(column);
        }

        // Initialize input handlers using AgentInput module
        AgentInput.init(agentId);

        // Mark as initialized
        initializedAgents.add(agentId);

        console.log(`[AgentUI] Created and initialized agent ${agentId} (${agentName || AgentColumn.getName(agentId)})`);

        return column;
    }

    /**
     * Remove an agent column
     * @param {number} agentId - Agent ID
     */
    function removeAgent(agentId) {
        AgentColumn.remove(agentId);
        initializedAgents.delete(agentId);
        console.log(`[AgentUI] Removed agent ${agentId}`);
    }

    /**
     * Get agent input value
     * @param {number} agentId - Agent ID
     * @returns {string} Input value
     */
    function getAgentInput(agentId) {
        return AgentInput.getValue(agentId);
    }

    /**
     * Set agent input value
     * @param {number} agentId - Agent ID
     * @param {string} value - New value
     */
    function setAgentInput(agentId, value) {
        AgentInput.setValue(agentId, value);
    }

    /**
     * Focus agent input
     * @param {number} agentId - Agent ID
     */
    function focusAgent(agentId) {
        AgentInput.focus(agentId);
    }

    /**
     * Clear agent input and attached files
     * @param {number} agentId - Agent ID
     */
    function clearAgentInput(agentId) {
        AgentInput.setValue(agentId, '');
        AgentInput.clearFiles(agentId);
    }

    /**
     * Get attached files for an agent
     * @param {number} agentId - Agent ID
     * @returns {File[]} Array of attached files
     */
    function getAttachedFiles(agentId) {
        return AgentInput.getFiles(agentId);
    }

    /**
     * Update agent thread info
     * @param {number} agentId - Agent ID
     * @param {Object} threadData - Thread data
     */
    function updateThreadInfo(agentId, threadData) {
        AgentColumn.updateThreadInfo(agentId, threadData);
    }

    /**
     * Collapse agent column
     * @param {number} agentId - Agent ID
     */
    function collapseAgent(agentId) {
        AgentColumn.collapse(agentId);
    }

    /**
     * Expand agent column
     * @param {number} agentId - Agent ID
     */
    function expandAgent(agentId) {
        AgentColumn.expand(agentId);
    }

    /**
     * Toggle agent column width
     * @param {number} agentId - Agent ID
     */
    function toggleAgentWidth(agentId) {
        AgentColumn.toggleWidth(agentId);
    }

    /**
     * Check if agent is initialized
     * @param {number} agentId - Agent ID
     * @returns {boolean} True if initialized
     */
    function isInitialized(agentId) {
        return initializedAgents.has(agentId);
    }

    /**
     * Get list of initialized agent IDs
     * @returns {number[]} Array of agent IDs
     */
    function getInitializedAgents() {
        return Array.from(initializedAgents);
    }

    /**
     * Reset agent (clear messages and input)
     * @param {number} agentId - Agent ID
     */
    function resetAgent(agentId) {
        // Clear input
        clearAgentInput(agentId);

        // Clear messages container
        const messagesContainer = document.getElementById(`messages-${agentId}`);
        if (messagesContainer) {
            const agentName = AgentColumn.getName(agentId);
            messagesContainer.innerHTML = `
                <div class="empty-state" style="padding-top: 60%; text-align: center;">
                    <div style="line-height: 1.8; padding: 0 20px; max-width: 500px; margin: 0 auto;">
                        <div style="font-size: 2em; margin-bottom: 15px;">👋</div>
                        <div style="font-size: 1.2em; margin-bottom: 12px; font-weight: 600; color: var(--text-primary);">
                            ${agentName} Ready
                        </div>
                        <div style="margin-bottom: 20px; opacity: 0.8; font-size: 0.95em; color: var(--text-secondary);">
                            No active thread, start a new chat or load from history
                        </div>
                    </div>
                </div>
            `;
        }

        console.log(`[AgentUI] Reset agent ${agentId}`);
    }

    // Public API
    return {
        initialize,
        createAgent,
        removeAgent,
        getAgentInput,
        setAgentInput,
        focusAgent,
        clearAgentInput,
        getAttachedFiles,
        updateThreadInfo,
        collapseAgent,
        expandAgent,
        toggleAgentWidth,
        isInitialized,
        getInitializedAgents,
        resetAgent
    };
})();

// Auto-initialize when DOM is ready
if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            AgentUI.initialize();
        });
    } else {
        AgentUI.initialize();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AgentUI;
}
