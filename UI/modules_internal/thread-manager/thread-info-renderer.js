/**
 * FILE: UI/modules_internal/thread-manager/thread-info-renderer.js
 * PURPOSE: Render thread info cards with action buttons (unload, move to prime)
 * 
 * FEATURES:
 * - Thread info card rendering
 * - Unload thread button
 * - Move to Prime button
 * - Thread metadata display
 * 
 * EXPORTS:
 * - renderThreadInfoContainer(location, threadId, includeButtons)
 * 
 * USED BY:
 * - AgentColumn.updateThreadInfo()
 * - MultiAgent system
 * - Prime AI chat
 * 
 * LAST MODIFIED: 2025-12-08 - Created to fix unload button functionality
 */

(function () {
    'use strict';

    /**
     * Render thread info container with action buttons
     * @param {string} location - Location ID (e.g., 'prime', 'agent-1')
     * @param {string|null} threadId - Thread ID to display
     * @param {boolean} includeButtons - Whether to show action buttons
     * @returns {string} HTML for thread info container
     */
    function renderThreadInfoContainer(location, threadId, includeButtons = true) {
        // If no thread loaded, show empty state
        // FIX (Jul 23, 2026): Prime (location === 'unassigned') no longer renders
        // the clickable "No thread loaded" dropdown trigger. Prime's empty state
        // is just the bare drop-target wrapper so the drag-over highlight is
        // unambiguous. Agent columns keep their clickable selector so a manual
        // load via dropdown still works for agent slots.
        if (!threadId) {
            if (location === 'unassigned') {
                return `
                    <div class="thread-info-wrapper"></div>
                `;
            }
            return `
                <div class="thread-info-wrapper">
                    <div class="no-thread-message clickable"
                         onclick="AgentColumn.showThreadSelector(${location.replace('agent-', '')})">
                        <i class="fas fa-comment-slash" style="opacity: 0.5; margin-right: 8px;"></i>
                        <span>No thread loaded</span>
                        <i class="fas fa-chevron-down" style="margin-left: 8px; font-size: 0.9em;"></i>
                    </div>
                </div>
            `;
        }

        // Get thread data
        const thread = getThreadData(threadId);
        if (!thread) {
            console.warn(`[ThreadInfoRenderer] Thread ${threadId} not found`);
            return renderThreadInfoContainer(location, null, includeButtons);
        }

        // Calculate metadata
        const messageCount = thread.messages?.length || 0;
        const lastUpdated = formatRelativeTime(thread.updated_at || thread.updatedAt);
        const hasFiles = thread.has_files || false;

        // Determine location info
        const isAgent = location.startsWith('agent-');
        const agentId = isAgent ? location.replace('agent-', '') : null;

        // Build action buttons HTML
        let buttonsHTML = '';
        if (includeButtons) {
            if (isAgent) {
                // Agent location: Show "Move to Prime" and "Unload" buttons
                buttonsHTML = `
                    <div class="thread-info-actions">
                        <button class="btn btn-sm btn-secondary" 
                                onclick="event.stopPropagation(); moveToPrime(${agentId})"
                                title="Move thread to Prime AI">
                            <i class="fas fa-arrow-left"></i>
                            To Prime
                        </button>
                        <button class="btn btn-sm btn-danger" 
                                onclick="event.stopPropagation(); AgentColumn.unloadThread(${agentId})"
                                title="Unload to Threads Catalogue">
                            <i class="fas fa-eject"></i>
                            Unload to Threads Catalogue
                        </button>
                    </div>
                `;
            } else if (location === 'unassigned') {
                // Prime location: Show only "Unload" button
                buttonsHTML = `
                    <div class="thread-info-actions">
                        <button class="btn btn-sm btn-danger" 
                                onclick="event.stopPropagation(); PrimeAI.unloadThread()"
                                title="Unload to Threads Catalogue">
                            <i class="fas fa-eject"></i>
                            Unload to Threads Catalogue
                        </button>
                    </div>
                `;
            }
        }

        // Build complete HTML
        return `
            <div class="thread-info-wrapper active">
                <div class="thread-info-card">
                    <!-- Header -->
                    <div class="thread-info-header">
                        <div class="thread-info-title">
                            <i class="fas fa-comment-dots"></i>
                            <span title="${escapeHtml(thread.title || thread.name || 'Untitled')}">${truncate(thread.title || thread.name || 'Untitled', 30)}</span>
                        </div>
                        ${includeButtons ? `
                            <button class="btn-close-thread" 
                                    onclick="event.stopPropagation(); ${isAgent ? `AgentColumn.unloadThread(${agentId})` : `PrimeAI.unloadThread()`}"
                                    title="Unload to Threads Catalogue" 
                                    aria-label="Unload to Threads Catalogue">
                                <i class="fas fa-times"></i>
                            </button>
                        ` : ''}
                    </div>

                    <!-- Metadata Grid -->
                    <div class="thread-info-metadata">
                        <div class="metadata-item">
                            <span class="metadata-label">Messages:</span>
                            <span class="metadata-value">${messageCount}</span>
                        </div>
                        <div class="metadata-item">
                            <span class="metadata-label">Updated:</span>
                            <span class="metadata-value">${lastUpdated}</span>
                        </div>
                        ${hasFiles ? `
                            <div class="metadata-item">
                                <span class="metadata-label">Has Files:</span>
                                <span class="metadata-value">
                                    <i class="fas fa-paperclip" style="color: var(--accent-primary);"></i>
                                </span>
                            </div>
                        ` : ''}
                        <div class="metadata-item full-width">
                            <span class="metadata-label">Thread ID:</span>
                            <span class="metadata-value" 
                                  title="${thread.id}" 
                                  style="font-family: monospace; font-size: 0.85em;">
                                ${truncate(thread.id, 16)}
                            </span>
                        </div>
                        ${thread.team_id ? `
                            <div class="metadata-item full-width">
                                <span class="metadata-label">Team ID:</span>
                                <span class="metadata-value team-id-tag" 
                                      onclick="event.stopPropagation(); filterByTeamId('${thread.team_id}')"
                                      title="Click to filter by Team ID: ${thread.team_id}">
                                    <i class="fas fa-users"></i>
                                    ${thread.team_id}
                                </span>
                            </div>
                        ` : ''}
                    </div>

                    <!-- Action Buttons -->
                    ${buttonsHTML}
                </div>
            </div>
        `;
    }

    /**
     * Get thread data from ThreadManager
     * @param {string} threadId - Thread ID
     * @returns {Object|null} Thread data
     */
    function getThreadData(threadId) {
        if (typeof ThreadManager !== 'undefined' && ThreadManager.threads) {
            return ThreadManager.threads.find(t => t.id === threadId);
        }
        return null;
    }

    /**
     * Format timestamp as relative time
     * @param {string} timestamp - ISO timestamp
     * @returns {string} Formatted relative time
     */
    function formatRelativeTime(timestamp) {
        if (!timestamp) return 'Unknown';

        try {
            const date = new Date(timestamp);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);

            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffHours < 24) return `${diffHours}h ago`;
            if (diffDays < 7) return `${diffDays}d ago`;
            return date.toLocaleDateString();
        } catch (e) {
            return 'Unknown';
        }
    }

    /**
     * Truncate text with ellipsis
     * @param {string} text - Text to truncate
     * @param {number} maxLength - Maximum length
     * @returns {string} Truncated text
     */
    function truncate(text, maxLength) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    }

    /**
     * Escape HTML special characters
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Move thread to Prime AI
     * @param {number} agentId - Source agent ID
     */
    function moveToPrime(agentId) {
        console.log(`[ThreadInfoRenderer] Moving thread from agent ${agentId} to Prime`);

        // Get loaded thread from agent
        if (typeof MultiAgent !== 'undefined' && typeof MultiAgent.getLoadedThread === 'function') {
            const threadInfo = MultiAgent.getLoadedThread(agentId);
            if (threadInfo && typeof PrimeAI !== 'undefined' && typeof PrimeAI.loadThread === 'function') {
                PrimeAI.loadThread(threadInfo.threadId);
                AgentColumn.unloadThread(agentId);
                console.log(`✅ [ThreadInfoRenderer] Moved thread to Prime`);
            } else {
                console.error('[ThreadInfoRenderer] Unable to move thread - PrimeAI not available');
            }
        } else {
            console.error('[ThreadInfoRenderer] Unable to move thread - MultiAgent not available');
        }
    }

    /**
     * Filter threads by Team ID
     * @param {string} teamId - Team ID to filter by
     */
    function filterByTeamId(teamId) {
        console.log(`[ThreadInfoRenderer] Filtering by Team ID: ${teamId}`);

        // Check if ThreadManager has filtering capability
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.filterByTeamId === 'function') {
            ThreadManager.filterByTeamId(teamId);
        } else {
            // Fallback: Show notification
            if (typeof showNotification === 'function') {
                showNotification(`Filtering by Team ID: ${teamId}`, 'info');
            } else {
                console.info(`Team ID filter: ${teamId} (filtering not yet implemented)`);
            }
        }
    }

    // Export to ThreadManager
    if (typeof ThreadManager !== 'undefined') {
        ThreadManager.renderThreadInfoContainer = renderThreadInfoContainer;
        console.log('✅ [ThreadInfoRenderer] Registered renderThreadInfoContainer with ThreadManager');
    } else {
        // Wait for ThreadManager to be available
        let attempts = 0;
        const maxAttempts = 50;
        const checkInterval = setInterval(() => {
            attempts++;
            if (typeof ThreadManager !== 'undefined') {
                clearInterval(checkInterval);
                ThreadManager.renderThreadInfoContainer = renderThreadInfoContainer;
                console.log('✅ [ThreadInfoRenderer] Registered renderThreadInfoContainer with ThreadManager (delayed)');
            } else if (attempts >= maxAttempts) {
                clearInterval(checkInterval);
                console.warn('⚠️ [ThreadInfoRenderer] ThreadManager not available after 5 seconds');
            }
        }, 100);
    }

    // Make globally available for debugging
    window.ThreadInfoRenderer = {
        renderThreadInfoContainer,
        moveToPrime,
        filterByTeamId
    };

    // Also make filterByTeamId globally available for onclick handlers
    window.filterByTeamId = filterByTeamId;

    console.log('✅ [ThreadInfoRenderer] Module loaded');
})();
