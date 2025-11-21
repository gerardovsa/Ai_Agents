/**
 * FILE: UI/modules/agents/agent-column.js
 * PURPOSE: Manage agent column state - collapse/expand, width toggle, menu interactions
 * 
 * FEATURES:
 * - Column collapse/expand animations
 * - Width toggle (normal/wide)
 * - Hamburger menu dropdown
 * - Thread info display
 * - Empty state rendering
 * 
 * DEPENDENCIES:
 * - agent-ui.css (styling)
 * - ThreadManager (global thread management)
 * 
 * EXPORTS:
 * - AgentColumn.create(agentId, agentName) - Create new agent column
 * - AgentColumn.collapse(agentId) - Collapse column
 * - AgentColumn.expand(agentId) - Expand column
 * - AgentColumn.toggleWidth(agentId) - Toggle column width
 * - AgentColumn.toggleMenu(agentId) - Toggle hamburger menu
 * - AgentColumn.remove(agentId) - Remove column
 * - AgentColumn.updateThreadInfo(agentId, threadData) - Update thread display
 * 
 * USED BY:
 * - MultiAgent system
 * - agent-ui.js
 * 
 * LAST MODIFIED: 2025-11-15 - Initial extraction from monolithic HTML
 */

const AgentColumn = (function () {
    'use strict';

    // Agent icon mapping
    const AGENT_ICONS = {
        1: 'fa-robot',
        2: 'fa-wand-magic-sparkles',
        3: 'fa-brain',
        4: 'fa-flask',
        5: 'fa-code',
        6: 'fa-chart-line',
        7: 'fa-database',
        8: 'fa-shield-halved'
    };

    // Agent name mapping
    const AGENT_NAMES = {
        1: 'Alpha',
        2: 'Bravo',
        3: 'Charlie',
        4: 'Delta',
        5: 'Echo',
        6: 'Foxtrot',
        7: 'Golf',
        8: 'Hotel'
    };

    /**
     * Create a new agent column
     * @param {number} agentId - Agent ID
     * @param {string} agentName - Agent display name (optional, defaults to phonetic)
     * @returns {HTMLElement} Created column element
     */
    function create(agentId, agentName = null) {
        const name = agentName || AGENT_NAMES[agentId] || `Agent ${agentId}`;
        const icon = AGENT_ICONS[agentId] || 'fa-robot';

        const column = document.createElement('div');
        column.className = 'agent-column';
        column.id = `agent-column-${agentId}`;
        column.dataset.agentId = agentId;

        // Get thread info if exists (assumes MultiAgent.getLoadedThread exists)
        let threadInfoHtml = `
            <div class="no-thread-message clickable" onclick="AgentColumn.showThreadSelector(${agentId})">
                <i class="fas fa-inbox"></i> 
                <span>Click to select a thread</span>
                <i class="fas fa-chevron-down" style="margin-left: auto; font-size: 10px;"></i>
            </div>
            <div class="thread-selector-dropdown" id="thread-selector-${agentId}" style="display: none;"></div>
        `;

        if (typeof MultiAgent !== 'undefined' && typeof MultiAgent.getLoadedThread === 'function') {
            const loadedThread = MultiAgent.getLoadedThread(agentId);
            if (loadedThread && typeof ThreadManager !== 'undefined' && typeof ThreadManager.renderThreadInfoContainer === 'function') {
                threadInfoHtml = ThreadManager.renderThreadInfoContainer(`agent-${agentId}`, loadedThread.threadId, true);
            }
        }

        column.innerHTML = `
            <!-- Collapsed Column Bar (hidden by default) -->
            <div class="collapsed-column-bar" onclick="AgentColumn.expand(${agentId})">
                <button class="expand-btn" title="Expand column" aria-label="Expand column">
                    <i class="fas fa-chevron-right"></i>
                </button>
                <div class="agent-name-vertical">${name}</div>
                <div class="thread-info-vertical">
                    <div class="thread-status-vertical" id="collapsed-status-${agentId}">No Thread</div>
                    <div class="thread-timestamp-vertical" id="collapsed-timestamp-${agentId}"></div>
                </div>
            </div>

            <!-- Expanded Column Content -->
            <div class="agent-header">
                <!-- Header Top Row: [Collapse] [Agent Title] [Width Toggle] [Hamburger] -->
                <div class="agent-header-top">
                    <button class="collapse-btn" onclick="event.stopPropagation(); AgentColumn.collapse(${agentId})" title="Collapse column" aria-label="Collapse column">
                        <i class="fas fa-chevron-down"></i>
                    </button>
                    
                    <div class="agent-title-wrapper">
                        <h2><i class="fas ${icon}"></i> ${name}</h2>
                    </div>
                    
                    <div class="agent-header-controls">
                        <button class="width-toggle-btn" onclick="event.stopPropagation(); AgentColumn.toggleWidth(${agentId})" title="Toggle column width" aria-label="Toggle column width">
                            <i class="fas fa-chevron-right" id="width-icon-${agentId}"></i>
                        </button>
                        <button class="agent-hamburger-button" onclick="event.stopPropagation(); AgentColumn.toggleMenu(${agentId})" aria-label="Agent menu">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                    </div>
                </div>

                <!-- Hamburger Menu Dropdown -->
                <div class="agent-menu-dropdown" id="menu-${agentId}">
                    <div class="agent-menu-item" onclick="event.stopPropagation(); AgentColumn.newThread(${agentId})">
                        <i class="fas fa-plus"></i> New Thread
                    </div>
                    <div class="agent-menu-divider"></div>
                    <div class="agent-menu-item" onclick="event.stopPropagation(); AgentColumn.showHistory(${agentId})">
                        <i class="fas fa-history"></i> Thread History
                    </div>
                    <div class="agent-menu-divider"></div>
                    <div class="agent-menu-item close-agent" onclick="event.stopPropagation(); AgentColumn.remove(${agentId})">
                        <i class="fas fa-times"></i> Close Agent
                    </div>
                </div>

                <!-- Thread Info Container -->
                <div id="thread-info-${agentId}">
                    ${threadInfoHtml}
                </div>
            </div>
            
            <!-- Messages Container -->
            <div class="agent-messages-container" id="messages-${agentId}">
                ${renderEmptyState(agentId, name)}
            </div>
            
            <!-- Input Area -->
            <div class="agent-input-area">
                <!-- File attachment preview -->
                <div id="agent-attached-files-${agentId}" class="agent-attached-files"></div>
                
                <div class="agent-input-group">
                    <!-- Center: Textarea -->
                    <div class="agent-input-center">
                        <textarea id="input-${agentId}" 
                                  placeholder="Type your message..." 
                                  aria-label="Message input"
                                  rows="3"></textarea>
                    </div>

                    <!-- Right: Action buttons -->
                    <div class="agent-input-right-buttons">
                        <button id="attach-${agentId}" 
                                class="agent-attach-btn" 
                                title="Attach files"
                                aria-label="Attach files">
                            <i class="fas fa-paperclip"></i>
                        </button>
                        <button id="send-${agentId}" 
                                class="agent-send-btn" 
                                onclick="AgentColumn.sendMessage(${agentId})"
                                aria-label="Send message">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>

                    <input type="file" 
                           id="file-input-${agentId}" 
                           class="agent-file-input" 
                           multiple 
                           accept="application/pdf,image/*" 
                           style="display: none;">
                </div>
            </div>
        `;

        return column;
    }

    /**
     * Render empty state for agent
     * @param {number} agentId - Agent ID
     * @param {string} agentName - Agent name
     * @returns {string} HTML for empty state
     */
    function renderEmptyState(agentId, agentName) {
        return `
            <div class="empty-state" style="padding-top: 60%; text-align: center;">
                <div style="line-height: 1.8; padding: 0 20px; max-width: 500px; margin: 0 auto;">
                    <div style="font-size: 2em; margin-bottom: 15px;">
                        👋
                    </div>
                    <div style="font-size: 1.2em; margin-bottom: 12px; font-weight: 600; color: var(--text-primary, #e5e7eb);">
                        ${agentName} Ready
                    </div>
                    <div style="margin-bottom: 20px; opacity: 0.8; font-size: 0.95em; color: var(--text-secondary, #9ca3af);">
                        No active thread, start a new chat or load from history
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.05); padding: 14px; border-radius: 8px; border-left: 3px solid var(--accent-primary, #667eea); margin-bottom: 20px; text-align: left;">
                        <div style="font-weight: 600; margin-bottom: 8px; font-size: 0.9em; color: var(--text-primary, #e5e7eb);">💡 Quick Tip</div>
                        <div style="opacity: 0.85; font-size: 0.85em; line-height: 1.6; color: var(--text-secondary, #9ca3af);">
                            <strong>Drag & drop threads</strong> from the sidebar to move conversations between agents. 
                            All formatting, context, and history stays intact!
                        </div>
                    </div>
                    <div style="display: flex; gap: 12px; margin-top: 24px; justify-content: center;">
                        <button class="btn btn-primary" 
                                onclick="event.stopPropagation(); AgentColumn.newThread(${agentId})" 
                                style="display: flex; align-items: center; gap: 8px; font-size: 14px;">
                            <i class="fas fa-plus" style="font-size: 12px;"></i>
                            Start New Chat
                        </button>
                        <button class="btn btn-secondary" 
                                onclick="event.stopPropagation(); AgentColumn.showHistory(${agentId})" 
                                style="display: flex; align-items: center; gap: 8px; font-size: 14px;">
                            <i class="fas fa-history" style="font-size: 12px;"></i>
                            Thread History
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Collapse agent column
     * @param {number} agentId - Agent ID
     */
    function collapse(agentId) {
        const column = document.getElementById(`agent-column-${agentId}`);
        if (column) {
            column.classList.add('collapsed');
            console.log(`[AgentColumn] Collapsed agent ${agentId}`);
        }
    }

    /**
     * Expand agent column
     * @param {number} agentId - Agent ID
     */
    function expand(agentId) {
        const column = document.getElementById(`agent-column-${agentId}`);
        if (column) {
            column.classList.remove('collapsed');
            console.log(`[AgentColumn] Expanded agent ${agentId}`);
        }
    }

    /**
     * Toggle column width (normal/wide)
     * @param {number} agentId - Agent ID
     */
    function toggleWidth(agentId) {
        const column = document.getElementById(`agent-column-${agentId}`);
        const icon = document.getElementById(`width-icon-${agentId}`);

        if (column && icon) {
            const isWide = column.classList.toggle('wide');
            icon.className = isWide ? 'fas fa-chevron-left' : 'fas fa-chevron-right';
            console.log(`[AgentColumn] Toggled width for agent ${agentId}: ${isWide ? 'wide' : 'normal'}`);
        }
    }

    /**
     * Toggle hamburger menu
     * @param {number} agentId - Agent ID
     */
    function toggleMenu(agentId) {
        const menu = document.getElementById(`menu-${agentId}`);
        if (menu) {
            menu.classList.toggle('show');

            // Close other open menus
            document.querySelectorAll('.agent-menu-dropdown.show').forEach(otherMenu => {
                if (otherMenu !== menu) {
                    otherMenu.classList.remove('show');
                }
            });
        }
    }

    /**
     * Remove agent column
     * @param {number} agentId - Agent ID
     */
    function remove(agentId) {
        const column = document.getElementById(`agent-column-${agentId}`);
        if (column) {
            // Add fade-out animation
            column.style.opacity = '0';
            column.style.transform = 'scale(0.95)';

            setTimeout(() => {
                column.remove();
                console.log(`[AgentColumn] Removed agent ${agentId}`);
            }, 300);
        }
    }

    /**
     * Update thread info display
     * @param {number} agentId - Agent ID
     * @param {Object} threadData - Thread data object
     */
    function updateThreadInfo(agentId, threadData) {
        const container = document.getElementById(`thread-info-${agentId}`);
        if (!container) return;

        if (threadData && typeof ThreadManager !== 'undefined' && typeof ThreadManager.renderThreadInfoContainer === 'function') {
            container.innerHTML = ThreadManager.renderThreadInfoContainer(`agent-${agentId}`, threadData.threadId, true);
        } else {
            container.innerHTML = `
                <div class="no-thread-message clickable" onclick="AgentColumn.showThreadSelector(${agentId})">
                    <i class="fas fa-inbox"></i> 
                    <span>Click to select a thread</span>
                    <i class="fas fa-chevron-down" style="margin-left: auto; font-size: 10px;"></i>
                </div>
                <div class="thread-selector-dropdown" id="thread-selector-${agentId}" style="display: none;"></div>
            `;
        }
    }

    /**
     * Show thread selector dropdown (REMOVED - Duplicate of async version below)
     * Using async version at line 821+ with thread loading logic
     */

    /**
     * Hide thread selector dropdown (REMOVED - Duplicate of async version below)
     * Using async version at line 821+ with thread loading logic
     */

    /**
     * Load selected thread into agent (REMOVED - Duplicate of async version below)
     * Using async version at line 821+ with thread loading logic
     */

    /**
     * Show thread selector dropdown
     * @param {number} agentId - Agent ID
     */
    function showThreadSelector(agentId) {
        const dropdown = document.getElementById(`thread-selector-${agentId}`);
        if (!dropdown) return;

        // Close any other open dropdowns
        document.querySelectorAll('.thread-selector-dropdown').forEach(d => {
            if (d.id !== `thread-selector-${agentId}`) {
                d.style.display = 'none';
            }
        });

        // Toggle dropdown
        const isVisible = dropdown.style.display === 'block';
        dropdown.style.display = isVisible ? 'none' : 'block';

        if (!isVisible) {
            // Load threads from ThreadManager
            if (typeof ThreadManager !== 'undefined' && ThreadManager.threads) {
                const threads = ThreadManager.threads.filter(t => !t.location || t.location === 'prime');

                if (threads.length === 0) {
                    dropdown.innerHTML = `
                        <div class="thread-selector-empty">
                            <i class="fas fa-inbox"></i>
                            <p>No available threads</p>
                            <button class="btn-create-thread" onclick="AgentColumn.newThread(${agentId}); AgentColumn.hideThreadSelector(${agentId});">
                                <i class="fas fa-plus"></i> Create New Thread
                            </button>
                        </div>
                    `;
                } else {
                    const threadItems = threads.map(thread => {
                        const date = new Date(thread.updated || thread.created);
                        const timeStr = date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
                        const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

                        return `
                            <div class="thread-selector-item" onclick="AgentColumn.loadThreadIntoAgent(${agentId}, '${thread.id}')">
                                <div class="thread-item-icon">
                                    <i class="fas fa-comments"></i>
                                </div>
                                <div class="thread-item-content">
                                    <div class="thread-item-title">${thread.title || 'Untitled Thread'}</div>
                                    <div class="thread-item-meta">
                                        <span><i class="fas fa-message"></i> ${thread.message_count || 0}</span>
                                        <span>${dateStr} ${timeStr}</span>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('');

                    dropdown.innerHTML = `
                        <div class="thread-selector-header">
                            <span>Select a Thread</span>
                            <button class="btn-close-dropdown" onclick="AgentColumn.hideThreadSelector(${agentId})">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <div class="thread-selector-list">
                            ${threadItems}
                        </div>
                        <div class="thread-selector-footer">
                            <button class="btn-create-thread" onclick="AgentColumn.newThread(${agentId}); AgentColumn.hideThreadSelector(${agentId});">
                                <i class="fas fa-plus"></i> Create New Thread
                            </button>
                        </div>
                    `;
                }
            }
        }

        // Close dropdown when clicking outside
        setTimeout(() => {
            document.addEventListener('click', function closeDropdown(e) {
                if (!e.target.closest(`#thread-selector-${agentId}`) &&
                    !e.target.closest('.no-thread-message')) {
                    dropdown.style.display = 'none';
                    document.removeEventListener('click', closeDropdown);
                }
            });
        }, 100);
    }

    /**
     * Hide thread selector dropdown
     * @param {number} agentId - Agent ID
     */
    function hideThreadSelector(agentId) {
        const dropdown = document.getElementById(`thread-selector-${agentId}`);
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    }

    /**
     * Load selected thread into agent
     * @param {number} agentId - Agent ID
     * @param {string} threadId - Thread ID to load
     */
    async function loadThreadIntoAgent(agentId, threadId) {
        hideThreadSelector(agentId);

        // Get the thread object from ThreadManager
        const thread = ThreadManager && ThreadManager.threads ?
            ThreadManager.threads.find(t => t.id === threadId) : null;

        if (!thread) {
            console.error('[AgentColumn] Thread not found:', threadId);
            return;
        }

        // Use MultiAgent.loadThreadIntoAgent (correct method)
        if (typeof MultiAgent !== 'undefined' && typeof MultiAgent.loadThreadIntoAgent === 'function') {
            await MultiAgent.loadThreadIntoAgent(agentId, thread);
            console.log(`✅ [AgentColumn] Loaded thread "${thread.title}" into Agent ${agentId}`);
        } else {
            console.error('[AgentColumn] MultiAgent.loadThreadIntoAgent not available');
        }
    }

    /**
     * Start new thread (delegates to ThreadManager)
     * @param {number} agentId - Agent ID
     */
    function newThread(agentId) {
        toggleMenu(agentId); // Close menu

        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.showNewChatModal === 'function') {
            ThreadManager.showNewChatModal(`agent-${agentId}`);
        } else {
            console.warn('[AgentColumn] ThreadManager not available');
        }
    }

    /**
     * Show thread history (delegates to ThreadManager)
     * @param {number} agentId - Agent ID
     */
    function showHistory(agentId) {
        toggleMenu(agentId); // Close menu

        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.toggleThreadMenu === 'function') {
            ThreadManager.toggleThreadMenu();
        } else {
            console.warn('[AgentColumn] ThreadManager not available');
        }
    }

    /**
     * Send message (delegates to global function)
     * @param {number} agentId - Agent ID
     */
    function sendMessage(agentId) {
        if (typeof sendAgentMessage === 'function') {
            sendAgentMessage(agentId);
        } else {
            console.warn('[AgentColumn] sendAgentMessage function not found');
        }
    }

    /**
     * Get agent icon by ID
     * @param {number} agentId - Agent ID
     * @returns {string} Font Awesome icon class
     */
    function getIcon(agentId) {
        return AGENT_ICONS[agentId] || 'fa-robot';
    }

    /**
     * Get agent name by ID
     * @param {number} agentId - Agent ID
     * @returns {string} Agent display name
     */
    function getName(agentId) {
        return AGENT_NAMES[agentId] || `Agent ${agentId}`;
    }

    // Close menus when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.agent-hamburger-button') && !e.target.closest('.agent-menu-dropdown')) {
            document.querySelectorAll('.agent-menu-dropdown.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });

    /**
     * Show Prime thread selector dropdown
     */
    async function showPrimeThreadSelector() {
        const dropdown = document.getElementById('thread-selector-prime');
        if (!dropdown) {
            console.warn('Prime dropdown not found');
            return;
        }

        // Close any other open dropdowns
        document.querySelectorAll('.thread-selector-dropdown').forEach(d => {
            if (d.id !== 'thread-selector-prime') {
                d.style.display = 'none';
            }
        });

        // Toggle dropdown
        const isVisible = dropdown.style.display === 'block';
        dropdown.style.display = isVisible ? 'none' : 'block';

        if (!isVisible) {
            // Ensure threads are loaded first
            if (typeof ThreadManager !== 'undefined') {
                if (!ThreadManager.threads || ThreadManager.threads.length === 0) {
                    console.log('🔄 [AgentColumn] Threads not loaded for Prime, loading now...');
                    dropdown.innerHTML = '<div class="thread-selector-loading"><i class="fas fa-spinner fa-spin"></i> Loading threads...</div>';
                    await ThreadManager.loadThreadsForUser();
                }
            }

            // Load threads from ThreadManager
            if (typeof ThreadManager !== 'undefined' && ThreadManager.threads) {
                const threads = ThreadManager.threads.filter(t => !t.location || t.location === 'prime');

                if (threads.length === 0) {
                    dropdown.innerHTML = `
                        <div class="thread-selector-empty">
                            <i class="fas fa-inbox"></i>
                            <p>No available threads</p>
                            <button class="btn-create-thread" onclick="ThreadManager.showNewChatModal('prime'); AgentColumn.hidePrimeThreadSelector();">
                                <i class="fas fa-plus"></i> Create New Thread
                            </button>
                        </div>
                    `;
                } else {
                    const threadItems = threads.map(thread => {
                        const date = new Date(thread.updated || thread.created);
                        const timeStr = date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
                        const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

                        return `
                            <div class="thread-selector-item" onclick="AgentColumn.loadThreadIntoPrime('${thread.id}')">
                                <div class="thread-item-icon">
                                    <i class="fas fa-comments"></i>
                                </div>
                                <div class="thread-item-content">
                                    <div class="thread-item-title">${thread.title || 'Untitled Thread'}</div>
                                    <div class="thread-item-meta">
                                        <span><i class="fas fa-message"></i> ${thread.message_count || 0}</span>
                                        <span>${dateStr} ${timeStr}</span>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('');

                    dropdown.innerHTML = `
                        <div class="thread-selector-header">
                            <span>Select a Thread</span>
                            <button class="btn-close-dropdown" onclick="AgentColumn.hidePrimeThreadSelector()">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <div class="thread-selector-list">
                            ${threadItems}
                        </div>
                        <div class="thread-selector-footer">
                            <button class="btn-create-thread" onclick="ThreadManager.showNewChatModal('prime'); AgentColumn.hidePrimeThreadSelector();">
                                <i class="fas fa-plus"></i> Create New Thread
                            </button>
                        </div>
                    `;
                }
            }
        }

        // Close dropdown when clicking outside
        setTimeout(() => {
            document.addEventListener('click', function closeDropdown(e) {
                if (!e.target.closest('#thread-selector-prime') &&
                    !e.target.closest('#prime-no-thread')) {
                    dropdown.style.display = 'none';
                    document.removeEventListener('click', closeDropdown);
                }
            });
        }, 100);
    }

    /**
     * Hide Prime thread selector dropdown
     */
    function hidePrimeThreadSelector() {
        const dropdown = document.getElementById('thread-selector-prime');
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    }

    /**
     * Load a thread into Prime
     */
    async function loadThreadIntoPrime(threadId) {
        try {
            hidePrimeThreadSelector();

            // Find the thread object
            if (typeof ThreadManager !== 'undefined' && ThreadManager.threads) {
                const thread = ThreadManager.threads.find(t => t.id === threadId);
                if (thread && typeof ThreadManager.loadThread === 'function') {
                    await ThreadManager.loadThread(threadId, 'prime');
                } else {
                    console.error(`Thread not found or ThreadManager.loadThread not available: ${threadId}`);
                }
            }
        } catch (error) {
            console.error(`Error loading thread into Prime:`, error);
        }
    }

    /**
     * Refresh all existing agent columns AND Prime to update no-thread-message with clickable version
     * Call this after page load to update any existing agents
     */
    function refreshAllAgentThreadInfos() {
        console.log('🔄 [AgentColumn] Refreshing thread selectors for all agents and Prime...');

        // Update Prime first
        const primeContainer = document.getElementById('prime-thread-info');
        if (primeContainer) {
            const hasThread = primeContainer.querySelector('.thread-info-card:not(.empty)');
            if (!hasThread) {
                primeContainer.innerHTML = `
                    <div class="no-thread-message clickable" id="prime-no-thread" onclick="AgentColumn.showPrimeThreadSelector()" style="cursor: pointer !important;">
                        <i class="fas fa-inbox"></i>
                        <span>Click to select a thread</span>
                        <i class="fas fa-chevron-down" style="margin-left: auto; font-size: 10px;"></i>
                    </div>
                    <div class="thread-selector-dropdown" id="thread-selector-prime" style="display: none;"></div>
                `;
            }
        }

        // Update all agents 1-9
        for (let i = 1; i <= 9; i++) {
            const container = document.getElementById(`thread-info-${i}`);
            if (container) {
                const hasThread = container.querySelector('.thread-info-card:not(.empty)');
                if (!hasThread) {
                    // Update with clickable version
                    container.innerHTML = `
                        <div class="no-thread-message clickable" onclick="AgentColumn.showThreadSelector(${i})">
                            <i class="fas fa-inbox"></i> 
                            <span>Click to select a thread</span>
                            <i class="fas fa-chevron-down" style="margin-left: auto; font-size: 10px;"></i>
                        </div>
                        <div class="thread-selector-dropdown" id="thread-selector-${i}" style="display: none;"></div>
                    `;
                }
            }
        }
    }

    /**
     * Show thread selector dropdown
     * @param {number} agentId - Agent ID
     */
    async function showThreadSelector(agentId) {
        console.log(`🔷 [AgentColumn] showThreadSelector called for agent-${agentId}`);

        const dropdown = document.getElementById(`thread-selector-${agentId}`);
        if (!dropdown) {
            console.error(`❌ [AgentColumn] Dropdown not found: thread-selector-${agentId}`);
            console.log(`🔍 [AgentColumn] Available dropdowns:`, Array.from(document.querySelectorAll('.thread-selector-dropdown')).map(d => d.id));
            return;
        }

        console.log(`✅ [AgentColumn] Dropdown found: ${dropdown.id}`);

        // Close any other open dropdowns
        document.querySelectorAll('.thread-selector-dropdown').forEach(d => {
            if (d.id !== `thread-selector-${agentId}`) {
                d.style.display = 'none';
            }
        });

        // Toggle dropdown
        const isVisible = dropdown.style.display === 'block';
        dropdown.style.display = isVisible ? 'none' : 'block';
        console.log(`🔷 [AgentColumn] Dropdown display set to: ${dropdown.style.display}`);

        if (!isVisible) {
            // Ensure threads are loaded first
            if (typeof ThreadManager !== 'undefined') {
                if (!ThreadManager.threads || ThreadManager.threads.length === 0) {
                    console.log('🔄 [AgentColumn] Threads not loaded, loading now...');
                    dropdown.innerHTML = '<div class="thread-selector-loading"><i class="fas fa-spinner fa-spin"></i> Loading threads...</div>';
                    await ThreadManager.loadThreadsForUser();
                }
            }

            // Load threads from ThreadManager
            if (typeof ThreadManager !== 'undefined' && ThreadManager.threads) {
                const threads = ThreadManager.threads.filter(t => !t.location || t.location === 'prime');

                if (threads.length === 0) {
                    dropdown.innerHTML = `
                        <div class="thread-selector-empty">
                            <i class="fas fa-inbox"></i>
                            <p>No available threads</p>
                            <button class="btn-create-thread" onclick="AgentColumn.newThread(${agentId}); AgentColumn.hideThreadSelector(${agentId});">
                                <i class="fas fa-plus"></i> Create New Thread
                            </button>
                        </div>
                    `;
                } else {
                    const threadItems = threads.map(thread => {
                        const date = new Date(thread.updated || thread.created);
                        const timeStr = date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
                        const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

                        return `
                            <div class="thread-selector-item" onclick="AgentColumn.loadThreadIntoAgent(${agentId}, '${thread.id}')">
                                <div class="thread-item-icon">
                                    <i class="fas fa-comments"></i>
                                </div>
                                <div class="thread-item-content">
                                    <div class="thread-item-title">${thread.title || 'Untitled Thread'}</div>
                                    <div class="thread-item-meta">
                                        <span><i class="fas fa-message"></i> ${thread.message_count || 0}</span>
                                        <span>${dateStr} ${timeStr}</span>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('');

                    dropdown.innerHTML = `
                        <div class="thread-selector-header">
                            <span>Select a Thread</span>
                            <button class="btn-close-dropdown" onclick="AgentColumn.hideThreadSelector(${agentId})">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <div class="thread-selector-list">
                            ${threadItems}
                        </div>
                        <div class="thread-selector-footer">
                            <button class="btn-create-thread" onclick="AgentColumn.newThread(${agentId}); AgentColumn.hideThreadSelector(${agentId});">
                                <i class="fas fa-plus"></i> Create New Thread
                            </button>
                        </div>
                    `;
                }
            }
        }

        // Close dropdown when clicking outside
        setTimeout(() => {
            document.addEventListener('click', function closeDropdown(e) {
                if (!e.target.closest(`#thread-selector-${agentId}`) &&
                    !e.target.closest('.no-thread-message')) {
                    dropdown.style.display = 'none';
                    document.removeEventListener('click', closeDropdown);
                }
            });
        }, 100);
    }

    /**
     * Hide thread selector dropdown
     * @param {number} agentId - Agent ID
     */
    function hideThreadSelector(agentId) {
        const dropdown = document.getElementById(`thread-selector-${agentId}`);
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    }

    /**
     * Load a thread into an agent
     * @param {number} agentId - Agent ID
     * @param {string} threadId - Thread ID to load
     */
    async function loadThreadIntoAgent(agentId, threadId) {
        try {
            // Hide the dropdown
            hideThreadSelector(agentId);

            // Find the thread object
            if (typeof ThreadManager !== 'undefined' && ThreadManager.threads) {
                const thread = ThreadManager.threads.find(t => t.id === threadId);
                if (thread && typeof MultiAgent !== 'undefined' && typeof MultiAgent.loadThreadIntoAgent === 'function') {
                    await MultiAgent.loadThreadIntoAgent(agentId, thread);
                } else {
                    console.error(`Thread not found or MultiAgent not available: ${threadId}`);
                }
            }
        } catch (error) {
            console.error(`Error loading thread into agent ${agentId}:`, error);
        }
    }

    // Public API
    return {
        create,
        collapse,
        expand,
        toggleWidth,
        toggleMenu,
        remove,
        updateThreadInfo,
        newThread,
        showHistory,
        sendMessage,
        getIcon,
        getName,
        showThreadSelector,
        hideThreadSelector,
        loadThreadIntoAgent,
        showPrimeThreadSelector,
        hidePrimeThreadSelector,
        loadThreadIntoPrime,
        refreshAllAgentThreadInfos
    };
})();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AgentColumn;
}

// Make globally available for debugging
window.AgentColumn = AgentColumn;

// Add helper command for manual refresh
window.refreshThreadSelectors = function () {
    console.log('🔄 Manual refresh triggered...');
    if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.refreshAllAgentThreadInfos === 'function') {
        AgentColumn.refreshAllAgentThreadInfos();
        console.log('✅ Thread selectors refreshed!');
    }
};

// Auto-refresh on page load to update existing agent columns
if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            // Delay to let MultiAgent initialize first
            setTimeout(() => AgentColumn.refreshAllAgentThreadInfos(), 1500);
        });
    } else {
        // Already loaded, refresh immediately
        setTimeout(() => AgentColumn.refreshAllAgentThreadInfos(), 1500);
    }

    // Multiple refresh attempts to catch late-initialized agents
    setTimeout(() => AgentColumn.refreshAllAgentThreadInfos(), 3000);
    setTimeout(() => AgentColumn.refreshAllAgentThreadInfos(), 5000);
    setTimeout(() => AgentColumn.refreshAllAgentThreadInfos(), 7000);
    setTimeout(() => AgentColumn.refreshAllAgentThreadInfos(), 10000);

    // Watch for agent column creation using MutationObserver
    const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.addedNodes.length > 0) {
                // Check if any agent columns were added
                const agentColumnsAdded = Array.from(mutation.addedNodes).some(node =>
                    node.classList && node.classList.contains('agent-column')
                );
                if (agentColumnsAdded) {
                    console.log('🔄 [AgentColumn] New agent detected, refreshing thread selectors...');
                    setTimeout(() => AgentColumn.refreshAllAgentThreadInfos(), 500);
                }
            }
        }
    });

    // Start observing the multi-agent container
    setTimeout(() => {
        const container = document.getElementById('multi-agent-container');
        if (container) {
            observer.observe(container, { childList: true, subtree: true });
            console.log('👁️ [AgentColumn] Watching for new agent columns...');
        }
    }, 1000);

    // Event delegation for clickable no-thread-message (backup for onclick)
    document.addEventListener('click', (e) => {
        const noThreadMsg = e.target.closest('.no-thread-message.clickable');
        if (noThreadMsg) {
            // Check if it's Prime
            if (noThreadMsg.id === 'prime-no-thread') {
                AgentColumn.showPrimeThreadSelector();
                return;
            }

            // Extract agent ID from parent thread-info div
            const threadInfoDiv = noThreadMsg.closest('[id^="thread-info-"]');
            if (threadInfoDiv) {
                const agentId = parseInt(threadInfoDiv.id.replace('thread-info-', ''));
                if (!isNaN(agentId)) {
                    AgentColumn.showThreadSelector(agentId);
                }
            }
        }
    });
}
