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

    // Message visibility state tracking (per agent)
    // Combined view modes:
    // 1. 'all-collapsed': Show all - tools collapsed
    // 2. 'all-expanded': Show all - expand all
    // 3. 'ai-collapsed': Show AI only - collapsed tools
    // 4. 'ai-expanded': Show AI only - expanded tools
    // 5. 'ai-user': Show AI and user - no tools/no tool results
    const viewModes = {}; // Tracks current view mode per agent

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
        // Keep thread-info-wrapper EMPTY when no thread is loaded
        let threadInfoHtml = `
            <div class="thread-info-wrapper">
            </div>
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
                        <button class="view-mode-btn" 
                                id="view-mode-btn-${agentId}"
                                onclick="event.stopPropagation(); AgentColumn.toggleViewModeMenu(${agentId})" 
                                title="Change view mode" 
                                aria-label="Change view mode">
                            <i class="fas fa-expand-alt" id="view-mode-icon-${agentId}"></i>
                        </button>
                        <div class="view-mode-dropdown" id="view-mode-menu-${agentId}">
                            <div class="view-mode-item active" data-mode="all-expanded" onclick="event.stopPropagation(); AgentColumn.setViewMode(${agentId}, 'all-expanded')">
                                <i class="fas fa-expand-alt"></i>
                                <span>All Expanded</span>
                            </div>
                            <div class="view-mode-item" data-mode="all-collapsed" onclick="event.stopPropagation(); AgentColumn.setViewMode(${agentId}, 'all-collapsed')">
                                <i class="fas fa-list"></i>
                                <span>All Collapsed</span>
                            </div>
                            <div class="view-mode-item" data-mode="ai-expanded" onclick="event.stopPropagation(); AgentColumn.setViewMode(${agentId}, 'ai-expanded')">
                                <i class="fas fa-bolt"></i>
                                <span>AI + Tools Expanded</span>
                            </div>
                            <div class="view-mode-item" data-mode="ai-collapsed" onclick="event.stopPropagation(); AgentColumn.setViewMode(${agentId}, 'ai-collapsed')">
                                <i class="fas fa-robot"></i>
                                <span>AI + Tools Collapsed</span>
                            </div>
                            <div class="view-mode-item" data-mode="ai-user" onclick="event.stopPropagation(); AgentColumn.setViewMode(${agentId}, 'ai-user')">
                                <i class="fas fa-users"></i>
                                <span>AI + User Only</span>
                            </div>
                        </div>
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
            <div class="agent-messages-container" id="agent-messages-${agentId}">
                ${renderEmptyState(agentId, name)}
            </div>
            
            <!-- Expandable Input Container (Prime-style, column-specific isolation) -->
            <div class="agent-input-container" 
                 data-agent-id="${agentId}" 
                 style="display: none;">
                
                <!-- Feedback Area (Per-Agent) -->
                <div id="agent-feedback-${agentId}" class="agent-feedback-container">
                    <div class="feedback-header">
                        <div class="feedback-header-left">
                            <i class="fas fa-comment-dots"></i>
                            <span class="feedback-header-text">Provide guidance to AI</span>
                        </div>
                        <button class="feedback-close-btn" 
                                onclick="event.stopPropagation(); AgentInput.toggleFeedback(${agentId})"
                                aria-label="Close feedback area">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="feedback-body">
                        <textarea id="agent-feedback-text-${agentId}" 
                                  class="feedback-textarea"
                                  placeholder="Type instructions or guidance for ${name}..."
                                  rows="3"
                                  aria-label="Feedback text"></textarea>
                        <div class="feedback-quick-buttons">
                            <button onclick="event.stopPropagation(); AgentInput.insertQuickFeedback(${agentId}, 'pause')"
                                    title="Ask AI to pause"
                                    aria-label="Pause AI">
                                <i class="fas fa-pause"></i>
                            </button>
                            <button onclick="event.stopPropagation(); AgentInput.insertQuickFeedback(${agentId}, 'stop')"
                                    title="Ask AI to stop"
                                    aria-label="Stop AI">
                                <i class="fas fa-stop"></i>
                            </button>
                            <button onclick="event.stopPropagation(); AgentInput.insertQuickFeedback(${agentId}, 'explain')"
                                    title="Ask AI to explain"
                                    aria-label="Explain">
                                <i class="fas fa-question-circle"></i>
                            </button>
                            <button class="feedback-send-btn"
                                    onclick="event.stopPropagation(); AgentInput.sendFeedback(${agentId})"
                                    title="Send feedback"
                                    aria-label="Send feedback">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Input Wrapper (Per-Agent) -->
                <div class="agent-input-wrapper">
                    <!-- File attachment preview -->
                    <div id="agent-attached-files-${agentId}" class="agent-attached-files"></div>
                    
                    <div class="agent-input-controls">
                        <!-- Center: Textarea -->
                        <div class="agent-input-center">
                            <textarea id="agent-input-${agentId}" 
                                      class="agent-input-textarea"
                                      placeholder="Type your message to ${name}..." 
                                      aria-label="Message input for ${name}"
                                      rows="3"></textarea>
                        </div>

                        <!-- Right: 6-Button Stack -->
                        <div class="agent-input-right-buttons">
                            <button class="agent-prompt-library-btn" 
                                    id="agent-prompt-library-${agentId}"
                                    onclick="event.stopPropagation(); AgentInput.showPromptLibrary(${agentId})"
                                    title="Browse Prompt Library"
                                    aria-label="Prompt library">
                                <i class="fas fa-bolt"></i>
                            </button>
                            <button class="agent-autoscroll-btn active" 
                                    id="agent-autoscroll-${agentId}"
                                    onclick="event.stopPropagation(); AgentInput.toggleAutoScroll(${agentId})"
                                    title="Toggle auto-scroll"
                                    aria-label="Toggle auto-scroll">
                                <i class="fas fa-angle-double-down"></i>
                            </button>
                            <button class="agent-feedback-btn" 
                                    id="agent-feedback-btn-${agentId}"
                                    onclick="event.stopPropagation(); AgentInput.toggleFeedback(${agentId})"
                                    title="Give feedback to AI"
                                    aria-label="Give feedback">
                                <i class="fas fa-comment-dots"></i>
                            </button>
                            <button class="agent-mic-btn" 
                                    id="agent-mic-${agentId}"
                                    onclick="event.stopPropagation(); AgentInput.toggleTranscription(${agentId})"
                                    title="Start voice transcription"
                                    aria-label="Voice transcription">
                                <i class="fas fa-microphone"></i>
                            </button>
                            <button class="agent-attach-btn" 
                                    id="agent-attach-${agentId}"
                                    onclick="event.stopPropagation(); AgentInput.showFileDialog(${agentId})"
                                    title="Attach files"
                                    aria-label="Attach files">
                                <i class="fas fa-paperclip"></i>
                            </button>
                            <button class="agent-send-btn" 
                                    id="agent-send-${agentId}"
                                    onclick="event.stopPropagation(); AgentColumn.sendMessage(${agentId})"
                                    title="Send message"
                                    aria-label="Send message">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                    </div>

                    <input type="file" 
                           id="agent-file-input-${agentId}" 
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
                                style="display: flex; align-items: center; gap: 8px; font-size: 14px; line-height: 1;">
                            <i class="fas fa-plus" style="font-size: 14px;"></i>
                            Start New Chat
                        </button>
                        <button class="btn btn-secondary" 
                                onclick="event.stopPropagation(); AgentColumn.showHistory(${agentId})" 
                                style="display: flex; align-items: center; gap: 8px; font-size: 14px; line-height: 1;">
                            <i class="fas fa-history" style="font-size: 14px;"></i>
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
            // Keep thread-info-wrapper EMPTY when no thread is loaded
            container.innerHTML = `
                <div class="thread-info-wrapper">
                </div>
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

    // DEPRECATED showThreadSelector function removed - using async version below

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
        // Close hamburger menus
        if (!e.target.closest('.agent-hamburger-button') && !e.target.closest('.agent-menu-dropdown')) {
            document.querySelectorAll('.agent-menu-dropdown.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }

        // Close view mode dropdowns
        if (!e.target.closest('.view-mode-btn') && !e.target.closest('.view-mode-dropdown')) {
            document.querySelectorAll('.view-mode-dropdown.show').forEach(dropdown => {
                dropdown.classList.remove('show');
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
                        const slug = thread.id.substring(0, 8);

                        return `
                            <div class="thread-selector-item" onclick="AgentColumn.loadThreadIntoPrime('${thread.id}')">
                                <div class="thread-item-header">
                                    <div class="thread-item-content">
                                        <div class="thread-item-title">
                                            <span>${thread.title || 'Untitled Thread'}</span>
                                            <div class="thread-item-agent-badge" style="background: #238636;">
                                                <i class="fas fa-star"></i>
                                                <span>Prime</span>
                                            </div>
                                        </div>
                                        <div class="thread-item-meta">
                                            <span><i class="fas fa-message"></i> ${thread.message_count || 0} messages</span>
                                            <span><i class="fas fa-calendar"></i> ${dateStr}</span>
                                            <span><i class="fas fa-clock"></i> ${timeStr}</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="thread-item-badges">
                                    <div class="thread-item-id">
                                        <i class="fas fa-hashtag"></i>
                                        <span>${slug}</span>
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
        // CRITICAL: setTimeout prevents same click that opened from closing it
        setTimeout(() => {
            const closeDropdown = (e) => {
                if (!e.target.closest('#thread-selector-prime') &&
                    !e.target.closest('#prime-no-thread')) {
                    dropdown.style.display = 'none';
                    document.removeEventListener('click', closeDropdown);
                    console.log(`🔷 [AgentColumn] Prime dropdown closed (clicked outside)`);
                }
            };
            document.addEventListener('click', closeDropdown);
        }, 300); // Increased from 200ms to 300ms
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
     * 
     * DISABLED: This was interfering with thread loading. Threads now auto-populate during initMultiAgent()
     */
    function refreshAllAgentThreadInfos() {
        // DISABLED: Don't inject empty states - let threads load naturally
        console.log('🔄 [AgentColumn] refreshAllAgentThreadInfos called but DISABLED - threads load via initMultiAgent()');
        return;

        // Don't refresh during CASCADE operations - it interferes with UI updates
        if (window.ThreadManager && window.ThreadManager.cascadeInProgress) {
            console.log('⏸️ [AgentColumn] Skipping refresh - CASCADE in progress');
            return;
        }

        console.log('🔄 [AgentColumn] Refreshing thread selectors for all agents and Prime...');

        // Update Prime first - Check if it has a thread loaded
        const primeContainer = document.getElementById('prime-thread-info');
        if (primeContainer) {
            const hasThread = primeContainer.querySelector('.thread-info-card:not(.empty)');
            if (!hasThread) {
                // Prime with no thread: Show thread selector (not welcome message)
                // Check if there's an existing thread selector
                const hasSelector = primeContainer.querySelector('.no-thread-message');
                if (!hasSelector) {
                    // Show thread selector using ThreadCardTemplates.noThreadMessage()
                    if (typeof ThreadCardTemplates !== 'undefined') {
                        // Use noThreadMessage() for Prime (same as agents)
                        primeContainer.innerHTML = ThreadCardTemplates.noThreadMessage('Prime', 'fa-star', null);
                    } else {
                        // Fallback to thread selector (no inline onclick - event delegation handles it)
                        primeContainer.innerHTML = `
                            <div class="thread-info-wrapper">
                                <div class="no-thread-message clickable" id="prime-no-thread" style="cursor: pointer !important;">
                                    <i class="fas fa-inbox"></i>
                                    <span>Click to select a thread</span>
                                    <i class="fas fa-chevron-down" style="margin-left: auto; font-size: 10px;"></i>
                                </div>
                                <div class="thread-selector-dropdown" id="thread-selector-prime" style="display: none;"></div>
                            </div>
                        `;
                    }
                }
            }
        }

        // Update all agents 1-9
        for (let i = 1; i <= 9; i++) {
            const container = document.getElementById(`thread-info-${i}`);
            if (container) {
                const hasThread = container.querySelector('.thread-info-card:not(.empty)');
                if (!hasThread) {
                    // Keep thread-info-wrapper EMPTY when no thread is loaded
                    container.innerHTML = `
                        <div class="thread-info-wrapper">
                        </div>
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
        console.log(`   Stack trace:`, new Error().stack.split('\n').slice(1, 4).join('\n'));

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
        const newDisplay = isVisible ? 'none' : 'block';
        dropdown.style.display = newDisplay;
        console.log(`🔷 [AgentColumn] Dropdown toggled: ${isVisible ? 'visible → hidden' : 'hidden → visible'} (display: ${newDisplay})`);

        if (newDisplay === 'block') {
            // Ensure threads are loaded first
            console.log(`📋 [AgentColumn] Loading threads for dropdown...`);
            if (typeof ThreadManager !== 'undefined') {
                console.log(`   ThreadManager.threads:`, ThreadManager.threads?.length || 0, 'total threads');
                if (!ThreadManager.threads || ThreadManager.threads.length === 0) {
                    console.log('🔄 [AgentColumn] Threads not loaded, loading now...');
                    dropdown.innerHTML = '<div class="thread-selector-loading"><i class="fas fa-spinner fa-spin"></i> Loading threads...</div>';
                    await ThreadManager.loadThreadsForUser();
                    console.log(`   After load:`, ThreadManager.threads?.length || 0, 'threads');
                }
            }

            // Load threads from ThreadManager
            if (typeof ThreadManager !== 'undefined' && ThreadManager.threads) {
                const allThreads = ThreadManager.threads;
                console.log(`   All threads:`, allThreads.map(t => `${t.id} (${t.location || 'prime'})`));
                const threads = allThreads.filter(t => !t.location || t.location === 'prime');
                console.log(`   Filtered threads (prime only):`, threads.length);

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
                        const slug = thread.id.substring(0, 8);

                        // Determine agent info based on thread location
                        let agentName = 'Prime';
                        let agentIcon = 'fa-star';
                        let agentColor = '#238636';

                        const location = thread.location || 'prime';
                        if (location === 'synergy') {
                            agentName = 'Synergy';
                            agentIcon = 'fa-users';
                            agentColor = '#8B5CF6';
                        } else if (location.startsWith('agent-')) {
                            const match = location.match(/agent-(\d+)/);
                            if (match && typeof MultiAgent !== 'undefined') {
                                const aid = parseInt(match[1]);
                                agentName = MultiAgent.getAgentName(aid);
                                agentIcon = MultiAgent.getAgentIcon(aid);
                                agentColor = '#3B82F6';
                            }
                        }

                        return `
                            <div class="thread-selector-item" onclick="AgentColumn.loadThreadIntoAgent(${agentId}, '${thread.id}')">
                                <div class="thread-item-header">
                                    <div class="thread-item-content">
                                        <div class="thread-item-title">
                                            <span>${thread.title || 'Untitled Thread'}</span>
                                            <div class="thread-item-agent-badge" style="background: ${agentColor};">
                                                <i class="fas ${agentIcon}"></i>
                                                <span>${agentName}</span>
                                            </div>
                                        </div>
                                        <div class="thread-item-meta">
                                            <span><i class="fas fa-message"></i> ${thread.message_count || 0} messages</span>
                                            <span><i class="fas fa-calendar"></i> ${dateStr}</span>
                                            <span><i class="fas fa-clock"></i> ${timeStr}</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="thread-item-badges">
                                    <div class="thread-item-id">
                                        <i class="fas fa-hashtag"></i>
                                        <span>${slug}</span>
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

        // Close dropdown when clicking outside (delay to avoid catching opening click)
        setTimeout(() => {
            document.addEventListener('click', function closeDropdown(e) {
                if (!e.target.closest(`#thread-selector-${agentId}`) &&
                    !e.target.closest('.no-thread-message')) {
                    dropdown.style.display = 'none';
                    document.removeEventListener('click', closeDropdown);
                    console.log(`🔷 [AgentColumn] Dropdown closed (clicked outside)`);
                }
            });
        }, 300);
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

    /**
     * Toggle view mode dropdown menu
     * @param {number} agentId - Agent ID
     */
    function toggleViewModeMenu(agentId) {
        const menu = document.getElementById(`view-mode-menu-${agentId}`);
        if (!menu) return;

        // Close any other open dropdowns
        document.querySelectorAll('.view-mode-dropdown.show').forEach(dropdown => {
            if (dropdown.id !== `view-mode-menu-${agentId}`) {
                dropdown.classList.remove('show');
            }
        });

        // Toggle this dropdown
        menu.classList.toggle('show');
    }

    /**
     * Set view mode (called from dropdown menu)
     * @param {number} agentId - Agent ID
     * @param {string} mode - View mode to set
     */
    function setViewMode(agentId, mode) {
        viewModes[agentId] = mode;

        // Update button icon and title
        const btn = document.getElementById(`view-mode-btn-${agentId}`);
        const icon = document.getElementById(`view-mode-icon-${agentId}`);
        if (icon) {
            const modeIcons = {
                'all-collapsed': 'fa-list',
                'all-expanded': 'fa-expand-alt',
                'ai-collapsed': 'fa-robot',
                'ai-expanded': 'fa-bolt',
                'ai-user': 'fa-users'
            };
            icon.className = `fas ${modeIcons[mode]}`;
        }

        // Update hover text with current mode
        if (btn) {
            const modeNames = {
                'all-collapsed': 'All Collapsed',
                'all-expanded': 'All Expanded',
                'ai-collapsed': 'AI + Tools Collapsed',
                'ai-expanded': 'AI + Tools Expanded',
                'ai-user': 'AI + User Only'
            };
            btn.title = `Change View Mode\nCurrent: ${modeNames[mode]}`;
        }

        // Update active state in menu
        const menu = document.getElementById(`view-mode-menu-${agentId}`);
        if (menu) {
            menu.querySelectorAll('.view-mode-item').forEach(item => {
                if (item.dataset.mode === mode) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });
        }

        // Close dropdown
        if (menu) {
            menu.classList.remove('show');
        }

        // Apply view mode to all messages in this column
        applyViewModeToColumn(agentId, mode);

        console.log(`📐 [AgentColumn] View mode for agent ${agentId}: ${mode}`);
    }

    /**
     * Legacy function - cycle through view modes (for backward compatibility)
     * @param {number} agentId - Agent ID
     */
    function cycleExpandMode(agentId) {
        const modes = ['all-collapsed', 'all-expanded', 'ai-collapsed', 'ai-expanded', 'ai-user'];
        const currentMode = viewModes[agentId] || 'all-expanded';
        const currentIndex = modes.indexOf(currentMode);
        const nextIndex = (currentIndex + 1) % modes.length;
        const nextMode = modes[nextIndex];

        setViewMode(agentId, nextMode);
    }

    /**
     * Apply view mode to messages
     * @param {number} agentId - Agent ID
     * @param {string} mode - View mode
     */
    function applyViewModeToColumn(agentId, mode) {
        const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
        if (!messagesContainer) return;

        const messages = messagesContainer.querySelectorAll('.ai-message');

        messages.forEach(message => {
            const isAI = message.classList.contains('assistant');
            const isUser = message.classList.contains('user');
            const isThinking = message.classList.contains('thinking-bubble');
            const isTool = message.classList.contains('tool-bubble') || message.classList.contains('tool');

            // Reset classes and visibility
            message.classList.remove('expanded', 'collapsed');
            message.style.display = '';

            switch (mode) {
                case 'all-collapsed':
                    // Show all - tools collapsed
                    message.classList.add('collapsed');
                    break;

                case 'all-expanded':
                    // Show all - expand all
                    message.classList.add('expanded');
                    break;

                case 'ai-collapsed':
                    // Show AI only - collapsed tools
                    if (isAI) {
                        message.classList.add('expanded');
                    } else if (isTool) {
                        message.classList.add('collapsed');
                    } else if (isUser || isThinking) {
                        message.style.display = 'none';
                    }
                    break;

                case 'ai-expanded':
                    // Show AI only - expanded tools
                    if (isAI || isTool) {
                        message.classList.add('expanded');
                    } else if (isUser || isThinking) {
                        message.style.display = 'none';
                    }
                    break;

                case 'ai-user':
                    // Show AI and user - no tools/no tool results
                    if (isAI || isUser) {
                        message.classList.add('expanded');
                    } else if (isTool || isThinking) {
                        message.style.display = 'none';
                    }
                    break;
            }
        });
    }

    /**
     * Legacy function - now just calls cycleExpandMode
     * @param {number} agentId - Agent ID
     */
    function toggleThinkingToolBubbles(agentId) {
        // For backward compatibility, just cycle to next mode
        cycleExpandMode(agentId);
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
        refreshAllAgentThreadInfos,
        cycleExpandMode,
        toggleThinkingToolBubbles,
        toggleViewModeMenu,
        setViewMode
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
            // CRITICAL: Stop propagation to prevent dropdown from closing immediately
            e.stopPropagation();

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
