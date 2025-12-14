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

        // ✅ LOAD STORED WORKSPACE SETTINGS (localStorage)
        if (typeof WorkspaceManager !== 'undefined') {
            // Load column width
            const storedWidth = WorkspaceManager.load(agentId, 'columnWidth', 400);
            if (storedWidth && storedWidth !== 400) {
                column.style.minWidth = `${storedWidth}px`;
                column.style.maxWidth = `${storedWidth}px`;
                column.dataset.customWidth = storedWidth;
            }

            // Load collapsed state
            const isCollapsed = WorkspaceManager.load(agentId, 'columnCollapsed', false);
            if (isCollapsed) {
                column.classList.add('collapsed');
            }

            // Load view mode (will apply after DOM ready)
            const storedViewMode = WorkspaceManager.load(agentId, 'viewMode', 'all-expanded');
            viewModes[agentId] = storedViewMode;
            console.log(`📂 [AgentColumn] Loaded settings for agent ${agentId}: width=${storedWidth}px, viewMode=${storedViewMode}`);
        }

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
                <!-- Header Top Row: [Left: Collapse + View Mode] [Center: Agent Title] [Right: Popout + Width Toggle + Hamburger] -->
                <div class="agent-header-top">
                    <!-- Left Controls -->
                    <div class="agent-header-left">
                        <button class="collapse-btn" onclick="event.stopPropagation(); AgentColumn.collapse(${agentId})" title="Collapse column" aria-label="Collapse column">
                            <i class="fas fa-chevron-down"></i>
                        </button>
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
                    </div>
                    
                    <!-- Center Title -->
                    <div class="agent-title-wrapper">
                        <h2><i class="fas ${icon}"></i> ${name}</h2>
                    </div>
                    
                    <!-- Right Controls -->
                    <div class="agent-header-controls">
                        <button class="agent-popout-btn" 
                                onclick="event.stopPropagation(); AgentColumn.popOut(${agentId})" 
                                title="Pop out agent window" 
                                aria-label="Pop out agent">
                            <i class="fas fa-external-link-alt"></i>
                        </button>
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
                    <div class="agent-menu-item" onclick="event.stopPropagation(); AgentColumn.newThread(${agentId}, event)">
                        <i class="fas fa-plus"></i> New Thread
                    </div>
                    <div class="agent-menu-item" onclick="event.stopPropagation(); AgentColumn.refreshThread(${agentId})">
                        <i class="fas fa-sync-alt"></i> Refresh Thread
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
                <!-- Scroll Controls (Fixed Top-Right - Visible only when messages exist) -->
                <div class="agent-scroll-controls" id="scroll-controls-${agentId}">
                    <button class="agent-scroll-top-btn" 
                            onclick="event.stopPropagation(); AgentColumn.scrollToTop(${agentId})" 
                            title="Scroll to top message" 
                            aria-label="Scroll to top">
                        <i class="fa fa-angle-double-up"></i>
                    </button>
                    <button class="agent-scroll-bottom-btn" 
                            onclick="event.stopPropagation(); AgentColumn.scrollToBottom(${agentId}); AgentColumn.scrollColumnIntoView(${agentId})" 
                            title="Scroll to bottom message and column" 
                            aria-label="Scroll to bottom">
                        <i class="fa fa-angle-double-down"></i>
                    </button>
                    <button class="agent-autoscroll-btn active" 
                            id="agent-autoscroll-${agentId}" 
                            onclick="event.stopPropagation(); AgentColumn.toggleAutoScroll(${agentId})" 
                            title="Toggle auto-scroll" 
                            aria-label="Toggle auto-scroll">
                        <i class="fas fa-step-forward" style="transform: rotate(90deg);"></i>
                    </button>
                </div>
                ${renderEmptyState(agentId, name)}
            </div>
            
            <!-- Resize Handle (right edge) -->
            <div class="agent-resize-handle" 
                 data-agent-id="${agentId}"
                 title="Drag to resize column"
                 aria-label="Resize column"></div>
            
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

        // ✅ SETUP MUTATION OBSERVER TO TRACK MESSAGE CHANGES
        // This allows us to show/hide scroll controls based on whether messages exist
        setTimeout(() => {
            const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
            if (messagesContainer) {
                const observer = new MutationObserver(() => {
                    // Check if messages were added or removed
                    updateScrollControlsVisibility(agentId);
                });

                // Watch for changes to the messages container
                observer.observe(messagesContainer, {
                    childList: true,           // Watch for added/removed children
                    subtree: true,             // Watch nested elements too
                    characterData: false,      // Don't watch text changes
                    attributes: false          // Don't watch attribute changes
                });

                console.log(`👁️ [AgentColumn] Setup scroll-controls visibility observer for agent ${agentId}`);
            }

            // Setup auto-scroll observer
            setupAutoScrollObserver(agentId);
        }, 100);

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
            <div class="empty-state" style="display: flex; align-items: center; justify-content: center; min-height: 50vh; text-align: center;">
                <div style="line-height: 1.8; max-width: 500px;">
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
                                onclick="event.stopPropagation(); AgentColumn.newThread(${agentId}, event)" 
                                style="display: flex; align-items: center; gap: 8px; font-size: 14px; line-height: 1; background-color: var(--accent-primary, #58a6ff); border-color: var(--accent-primary, #58a6ff);">
                            <i class="fas fa-plus" style="font-size: 14px; margin: 0;"></i>
                            Start New Chat
                        </button>
                        <button class="btn btn-secondary" 
                                onclick="event.stopPropagation(); AgentColumn.showHistory(${agentId})" 
                                style="display: flex; align-items: center; gap: 8px; font-size: 14px; line-height: 1;">
                            <i class="fas fa-history" style="font-size: 14px; margin: 0;"></i>
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

            // ✅ SAVE COLLAPSED STATE TO STORAGE
            if (typeof WorkspaceManager !== 'undefined') {
                WorkspaceManager.save(agentId, 'columnCollapsed', true);
            }

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

            // ✅ SAVE COLLAPSED STATE TO STORAGE
            if (typeof WorkspaceManager !== 'undefined') {
                WorkspaceManager.save(agentId, 'columnCollapsed', false);
            }

            console.log(`[AgentColumn] Expanded agent ${agentId}`);
        }
    }

    // Track popout windows
    let nextZIndex = 11000;
    let popoutCount = 0;
    const popoutWindows = new Map(); // agentId -> window element

    /**
     * Pop out agent column into floating window
     * @param {number} agentId - Agent ID
     */
    function popOut(agentId) {
        // Check if already popped out
        if (popoutWindows.has(agentId)) {
            console.warn(`[AgentColumn] Agent ${agentId} already popped out`);
            const existingWindow = popoutWindows.get(agentId);
            existingWindow.style.zIndex = nextZIndex++;
            existingWindow.classList.add('pulse');
            setTimeout(() => existingWindow.classList.remove('pulse'), 300);
            return;
        }

        const column = document.getElementById(`agent-column-${agentId}`);
        if (!column) {
            console.error(`[AgentColumn] Column not found: ${agentId}`);
            return;
        }

        popoutCount++;
        const name = AGENT_NAMES[agentId] || `Agent ${agentId}`;
        const icon = AGENT_ICONS[agentId] || 'fa-robot';

        // 💾 SAVE CURRENT STATE (width & scroll position)
        const currentWidth = column.offsetWidth;
        const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
        const currentScrollTop = messagesContainer ? messagesContainer.scrollTop : 0;

        console.log(`[AgentColumn] Saving state - Width: ${currentWidth}px, Scroll: ${currentScrollTop}px`);

        // Create floating window
        const floatingWindow = document.createElement('div');
        floatingWindow.className = 'agent-popout-window';
        floatingWindow.id = `agent-popout-${agentId}`;
        floatingWindow.style.zIndex = nextZIndex++;
        floatingWindow.dataset.agentId = agentId;

        // 🔧 RESTORE WIDTH from column (preserve user's width preference)
        floatingWindow.style.width = `${currentWidth}px`;

        // Position with cascade
        const offset = (popoutCount - 1) * 40;
        floatingWindow.style.left = `${100 + offset}px`;
        floatingWindow.style.top = `${80 + offset}px`;

        // Store scroll position in dataset for restoration
        floatingWindow.dataset.savedScrollTop = currentScrollTop;

        floatingWindow.innerHTML = `
            <div class="agent-popout-content"></div>
        `;

        // Move the actual column into popout (not clone - preserves event handlers)
        const contentDiv = floatingWindow.querySelector('.agent-popout-content');
        const originalParent = column.parentElement;
        const originalNextSibling = column.nextSibling;

        // Store original position for restoration
        floatingWindow.dataset.originalParent = originalParent ? originalParent.id : '';

        // Store reference to original sibling for precise restoration
        if (originalNextSibling && originalNextSibling.id) {
            floatingWindow.dataset.originalSibling = originalNextSibling.id;
        }

        // Create a collapsed placeholder that stays in the Command Centre
        const placeholder = document.createElement('div');
        placeholder.className = 'agent-column collapsed popped-out-placeholder';
        placeholder.id = `agent-placeholder-${agentId}`;
        placeholder.dataset.agentId = agentId;

        // Clone the collapsed bar from original column
        const originalCollapsedBar = column.querySelector('.collapsed-column-bar');
        if (originalCollapsedBar) {
            const placeholderBar = originalCollapsedBar.cloneNode(true);
            placeholderBar.onclick = null; // Remove expand handler
            placeholderBar.style.cursor = 'default';
            placeholder.appendChild(placeholderBar);
        }

        // Add return button to placeholder
        const returnIndicator = document.createElement('button');
        returnIndicator.className = 'collapsed-return-btn';
        returnIndicator.innerHTML = '<i class="fas fa-arrow-left"></i><span>Return to Command Centre</span>';
        returnIndicator.title = 'Return to Command Centre';
        returnIndicator.onclick = (e) => {
            e.stopPropagation();
            returnToMain();
        };
        placeholder.appendChild(returnIndicator);

        // Replace original column with placeholder in dashboard
        originalParent.replaceChild(placeholder, column);

        // Update the popout button in the REAL column's header to return button
        const popoutBtn = column.querySelector('.agent-popout-btn');
        if (popoutBtn) {
            popoutBtn.innerHTML = '<i class="fas fa-arrow-left"></i>';
            popoutBtn.title = 'Return to Command Centre';
            popoutBtn.setAttribute('aria-label', 'Return to Command Centre');
            // Update onclick to return function
            popoutBtn.onclick = (e) => {
                e.stopPropagation();
                returnToMain();
            };
        }

        // Ensure column is expanded (remove collapsed class if present)
        column.classList.remove('collapsed');
        column.classList.remove('popped-out-placeholder');

        // Style column for popout
        column.style.border = 'none';
        column.style.margin = '0';
        column.style.height = '100%';
        column.dataset.poppedOut = 'true';
        contentDiv.appendChild(column);

        // Add to body
        document.body.appendChild(floatingWindow);
        popoutWindows.set(agentId, floatingWindow);

        // Re-enable all interactive elements by triggering a reflow
        // This ensures onclick handlers work properly in the new context
        requestAnimationFrame(() => {
            // Force reflow
            void column.offsetHeight;

            // Debug: Check if buttons exist and are clickable
            const buttons = column.querySelectorAll('button[onclick]');
            console.log(`[AgentColumn] Found ${buttons.length} onclick buttons in popped out agent`);

            // Ensure all onclick attributes are properly bound
            buttons.forEach((btn, idx) => {
                const onclickAttr = btn.getAttribute('onclick');
                if (onclickAttr && !btn.onclick) {
                    // Re-compile onclick if needed
                    try {
                        btn.onclick = new Function('event', onclickAttr);
                        console.log(`[AgentColumn] Re-bound onclick for button ${idx}`);
                    } catch (e) {
                        console.error(`[AgentColumn] Failed to bind onclick:`, e);
                    }
                }
            });

            // 📜 RESTORE SCROLL POSITION after DOM settles
            setTimeout(() => {
                const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
                const savedScroll = floatingWindow.dataset.savedScrollTop;
                if (messagesContainer && savedScroll) {
                    messagesContainer.scrollTop = parseInt(savedScroll);
                    console.log(`[AgentColumn] ✅ Restored scroll position to ${savedScroll}px`);
                }
            }, 100);

            // Dispatch custom event to notify other systems
            const popoutEvent = new CustomEvent('agent-popped-out', {
                detail: { agentId, windowElement: floatingWindow }
            });
            document.dispatchEvent(popoutEvent);
        });

        // Get elements
        const columnHeader = column.querySelector('.agent-header-top');

        // Return to main view
        const returnToMain = () => {
            console.log(`[AgentColumn] Returning agent ${agentId} to main view...`);

            // 💾 SAVE CURRENT SCROLL POSITION before returning
            const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
            if (messagesContainer) {
                const currentScroll = messagesContainer.scrollTop;
                floatingWindow.dataset.savedScrollTop = currentScroll;
                console.log(`[AgentColumn] Saved scroll position: ${currentScroll}px`);
            }

            // Find the placeholder in the dashboard
            const placeholder = document.getElementById(`agent-placeholder-${agentId}`);
            console.log(`[AgentColumn] Placeholder found:`, placeholder ? 'YES' : 'NO');

            // Restore column styles
            column.style.border = '';
            column.style.margin = '';
            column.style.height = '';
            delete column.dataset.poppedOut;

            // Ensure column is not collapsed
            column.classList.remove('collapsed');
            column.classList.remove('popped-out-placeholder');

            // Restore popout button
            const popoutBtn = column.querySelector('.agent-popout-btn');
            if (popoutBtn) {
                popoutBtn.innerHTML = '<i class="fas fa-external-link-alt"></i>';
                popoutBtn.title = 'Pop out agent window';
                popoutBtn.setAttribute('aria-label', 'Pop out agent');
                // Restore original onclick
                popoutBtn.onclick = (e) => {
                    e.stopPropagation();
                    popOut(agentId);
                };
            }

            // Replace placeholder with original column in dashboard
            if (placeholder && placeholder.parentElement) {
                console.log(`[AgentColumn] Replacing placeholder with column`);
                placeholder.parentElement.replaceChild(column, placeholder);
            } else {
                // Fallback: try to find parent and restore position
                console.log(`[AgentColumn] Placeholder not found, using fallback`);
                const parentId = floatingWindow.dataset.originalParent;
                const parent = document.getElementById(parentId);

                if (parent) {
                    // Try to restore original position using sibling reference
                    const siblingId = floatingWindow.dataset.originalSibling;
                    const sibling = siblingId ? document.getElementById(siblingId) : null;

                    if (sibling && sibling.parentElement === parent) {
                        parent.insertBefore(column, sibling);
                        console.log(`[AgentColumn] Restored to original position before sibling`);
                    } else {
                        parent.appendChild(column);
                        console.log(`[AgentColumn] Appended to parent (no sibling reference)`);
                    }
                } else {
                    console.error(`[AgentColumn] Could not find parent container: ${parentId}`);
                }
            }

            // 📜 RESTORE SCROLL POSITION after returning to dashboard
            setTimeout(() => {
                if (messagesContainer) {
                    const savedScroll = floatingWindow.dataset.savedScrollTop;
                    if (savedScroll) {
                        messagesContainer.scrollTop = parseInt(savedScroll);
                        console.log(`[AgentColumn] ✅ Restored scroll position to ${savedScroll}px`);
                    }
                }
            }, 100);

            // Remove window
            floatingWindow.classList.add('closing');
            setTimeout(() => {
                floatingWindow.remove();
                popoutWindows.delete(agentId);
            }, 200);

            console.log(`[AgentColumn] Agent ${agentId} returned to main view`);
        };

        // Close window (also returns to main)
        const closeWindow = () => {
            returnToMain();
        };

        // Bring to front on click
        floatingWindow.addEventListener('mousedown', () => {
            floatingWindow.style.zIndex = nextZIndex++;
        });

        // Make draggable via column header
        let isDragging = false;
        let dragOffsetX = 0;
        let dragOffsetY = 0;

        if (columnHeader) {
            columnHeader.addEventListener('mousedown', (e) => {
                if (e.target.closest('button')) return;
                isDragging = true;
                const rect = floatingWindow.getBoundingClientRect();
                dragOffsetX = e.clientX - rect.left;
                dragOffsetY = e.clientY - rect.top;
                columnHeader.style.cursor = 'grabbing';
                e.preventDefault();
            });
        }

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const x = e.clientX - dragOffsetX;
            const y = e.clientY - dragOffsetY;
            const maxX = window.innerWidth - 200;
            const maxY = window.innerHeight - 50;
            floatingWindow.style.left = `${Math.max(0, Math.min(x, maxX))}px`;
            floatingWindow.style.top = `${Math.max(0, Math.min(y, maxY))}px`;
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                if (columnHeader) columnHeader.style.cursor = '';
            }
        });

        // Make resizable from all edges and corners (Windows-style)
        let isResizing = false;
        let resizeEdge = null;
        let startX = 0;
        let startY = 0;
        let startWidth = 0;
        let startHeight = 0;
        let startLeft = 0;
        let startTop = 0;

        const RESIZE_MARGIN = 8; // Pixels from edge to detect resize

        // Detect which edge/corner is being hovered
        const getResizeEdge = (e) => {
            const rect = floatingWindow.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const isLeft = x < RESIZE_MARGIN;
            const isRight = x > rect.width - RESIZE_MARGIN;
            const isTop = y < RESIZE_MARGIN;
            const isBottom = y > rect.height - RESIZE_MARGIN;

            // Corners
            if (isTop && isLeft) return 'nw';
            if (isTop && isRight) return 'ne';
            if (isBottom && isLeft) return 'sw';
            if (isBottom && isRight) return 'se';

            // Edges
            if (isTop) return 'n';
            if (isBottom) return 's';
            if (isLeft) return 'w';
            if (isRight) return 'e';

            return null;
        };

        // Update cursor based on edge
        const updateCursor = (edge) => {
            const cursorMap = {
                'n': 'ns-resize',
                's': 'ns-resize',
                'e': 'ew-resize',
                'w': 'ew-resize',
                'ne': 'nesw-resize',
                'sw': 'nesw-resize',
                'nw': 'nwse-resize',
                'se': 'nwse-resize'
            };
            floatingWindow.style.cursor = edge ? cursorMap[edge] : '';
        };

        // Mouse move to detect resize zones
        floatingWindow.addEventListener('mousemove', (e) => {
            if (isResizing || isDragging) return;
            const edge = getResizeEdge(e);
            updateCursor(edge);
        });

        // Start resize
        floatingWindow.addEventListener('mousedown', (e) => {
            const edge = getResizeEdge(e);
            if (edge && !e.target.closest('button')) {
                isResizing = true;
                resizeEdge = edge;
                startX = e.clientX;
                startY = e.clientY;
                const rect = floatingWindow.getBoundingClientRect();
                startWidth = rect.width;
                startHeight = rect.height;
                startLeft = rect.left;
                startTop = rect.top;
                e.preventDefault();
                e.stopPropagation();
            }
        });

        // Perform resize
        const resizeMouseMove = (e) => {
            if (!isResizing) return;

            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;

            let newWidth = startWidth;
            let newHeight = startHeight;
            let newLeft = startLeft;
            let newTop = startTop;

            // Handle horizontal resize
            if (resizeEdge.includes('e')) {
                newWidth = Math.max(400, startWidth + deltaX);
            } else if (resizeEdge.includes('w')) {
                newWidth = Math.max(400, startWidth - deltaX);
                if (newWidth > 400) {
                    newLeft = startLeft + deltaX;
                }
            }

            // Handle vertical resize
            if (resizeEdge.includes('s')) {
                newHeight = Math.max(300, startHeight + deltaY);
            } else if (resizeEdge.includes('n')) {
                newHeight = Math.max(300, startHeight - deltaY);
                if (newHeight > 300) {
                    newTop = startTop + deltaY;
                }
            }

            floatingWindow.style.width = `${newWidth}px`;
            floatingWindow.style.height = `${newHeight}px`;
            floatingWindow.style.left = `${newLeft}px`;
            floatingWindow.style.top = `${newTop}px`;
        };

        document.addEventListener('mousemove', resizeMouseMove);

        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                resizeEdge = null;
                floatingWindow.style.cursor = '';
            }
        });

        // Animate in
        requestAnimationFrame(() => floatingWindow.classList.add('visible'));

        console.log(`[AgentColumn] Agent ${agentId} popped out`);
    }

    /**
     * Toggle column width (3-stage cycle: 400px > 600px > 800px > 400px)
     * @param {number} agentId - Agent ID
     */
    function toggleWidth(agentId) {
        const column = document.getElementById(`agent-column-${agentId}`);
        const icon = document.getElementById(`width-icon-${agentId}`);

        if (column && icon) {
            const hasWide = column.classList.contains('wide');
            const hasExtraWide = column.classList.contains('extra-wide');
            let newWidth = 400;

            if (!hasWide && !hasExtraWide) {
                // Stage 1 -> 2: 400px to 600px (icon: >)
                column.classList.add('wide');
                icon.className = 'fas fa-angle-double-right'; // >>
                icon.style.transform = 'none';
                newWidth = 600;
                console.log(`[AgentColumn] Width for agent ${agentId}: 400px -> 600px`);
            } else if (hasWide && !hasExtraWide) {
                // Stage 2 -> 3: 600px to 800px (icon: >>)
                column.classList.remove('wide');
                column.classList.add('extra-wide');
                icon.className = 'fas fa-chevron-left'; // <
                icon.style.transform = 'none';
                newWidth = 800;
                console.log(`[AgentColumn] Width for agent ${agentId}: 600px -> 800px`);
            } else {
                // Stage 3 -> 1: 800px back to 400px (icon: <)
                column.classList.remove('extra-wide');
                icon.className = 'fas fa-chevron-right'; // >
                icon.style.transform = 'none';
                newWidth = 400;
                console.log(`[AgentColumn] Width for agent ${agentId}: 800px -> 400px`);
            }

            // ✅ SAVE COLUMN WIDTH TO STORAGE (localStorage + database)
            if (typeof WorkspaceManager !== 'undefined') {
                WorkspaceManager.save(agentId, 'columnWidth', newWidth);
            }
        }
    }

    /**
     * Scroll messages container to top
     * @param {number} agentId - Agent ID
     */
    function scrollToTop(agentId) {
        const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
        if (messagesContainer) {
            messagesContainer.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
            console.log(`[AgentColumn] Scrolled agent ${agentId} to top`);
        }
    }

    /**
     * Scroll messages container to bottom
     * @param {number} agentId - Agent ID
     */
    function scrollToBottom(agentId) {
        const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
        if (messagesContainer) {
            messagesContainer.scrollTo({
                top: messagesContainer.scrollHeight + 50,
                behavior: 'smooth'
            });
            console.log(`[AgentColumn] Scrolled agent ${agentId} to bottom`);
        }
    }

    // Auto-scroll state tracking (per agent)
    const autoScrollState = {};

    /**
     * Initialize auto-scroll state for an agent
     * @param {number} agentId - Agent ID
     */
    function initAutoScrollState(agentId) {
        if (!autoScrollState[agentId]) {
            autoScrollState[agentId] = {
                enabled: true,  // Default: auto-scroll enabled
                observer: null
            };
        }
    }

    /**
     * Toggle auto-scroll functionality
     * @param {number} agentId - Agent ID
     */
    function toggleAutoScroll(agentId) {
        initAutoScrollState(agentId);

        const state = autoScrollState[agentId];
        state.enabled = !state.enabled;

        const btn = document.getElementById(`agent-autoscroll-${agentId}`);
        if (btn) {
            if (state.enabled) {
                btn.classList.add('active');
                btn.setAttribute('title', 'Auto-scroll enabled - Click to disable');
                scrollToBottom(agentId);
                console.log(`[AgentColumn] Agent ${agentId} auto-scroll: ENABLED`);
            } else {
                btn.classList.remove('active');
                btn.setAttribute('title', 'Auto-scroll disabled - Click to enable');
                console.log(`[AgentColumn] Agent ${agentId} auto-scroll: DISABLED`);
            }
        }
    }

    /**
     * Perform auto-scroll if enabled (called when messages are added)
     * @param {number} agentId - Agent ID
     */
    function performAutoScroll(agentId) {
        initAutoScrollState(agentId);

        if (!autoScrollState[agentId].enabled) {
            return;
        }

        const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
        if (messagesContainer) {
            setTimeout(() => {
                messagesContainer.scrollTop = messagesContainer.scrollHeight + 50;
            }, 50);
        }
    }

    /**
     * Setup auto-scroll observer for message additions
     * @param {number} agentId - Agent ID
     */
    function setupAutoScrollObserver(agentId) {
        initAutoScrollState(agentId);

        const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
        if (!messagesContainer) return;

        // Clean up existing observer
        if (autoScrollState[agentId].observer) {
            autoScrollState[agentId].observer.disconnect();
        }

        // Create new observer to watch for message additions
        const observer = new MutationObserver((mutations) => {
            // Check if messages were added
            const messagesAdded = mutations.some(mutation =>
                mutation.type === 'childList' && mutation.addedNodes.length > 0
            );

            if (messagesAdded && autoScrollState[agentId].enabled) {
                performAutoScroll(agentId);
            }
        });

        observer.observe(messagesContainer, {
            childList: true,
            subtree: true
        });

        autoScrollState[agentId].observer = observer;
        console.log(`👁️ [AgentColumn] Auto-scroll observer setup for agent ${agentId}`);
    }

    /**
     * Scroll the UI viewport to bring this column into view
     * @param {number} agentId - Agent ID
     */
    function scrollColumnIntoView(agentId) {
        const column = document.getElementById(`agent-column-${agentId}`);
        if (column) {
            column.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest',
                inline: 'center'
            });
            console.log(`[AgentColumn] Scrolled UI to show agent ${agentId}`);
        }
    }

    /**
     * Update scroll controls visibility based on whether messages exist
     * @param {number} agentId - Agent ID
     */
    function updateScrollControlsVisibility(agentId) {
        const messagesContainer = document.getElementById(`agent-messages-${agentId}`);

        if (!messagesContainer) {
            return;
        }

        // Check if any messages exist - check multiple selectors for compatibility with different renderers
        const messageBubbles = messagesContainer.querySelectorAll('.ai-message, .message-bubble, .message-row');
        const hasMessages = messageBubbles.length > 0;

        // Toggle 'has-messages' class to show/hide scroll controls via CSS
        if (hasMessages) {
            messagesContainer.classList.add('has-messages');
            console.log(`[AgentColumn] Showing scroll controls for agent ${agentId} (${messageBubbles.length} messages)`);
        } else {
            messagesContainer.classList.remove('has-messages');
            console.log(`[AgentColumn] Hiding scroll controls for agent ${agentId} (no messages)`);
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
        if (!column) {
            console.warn(`[AgentColumn] Column ${agentId} not found for removal`);
            return;
        }

        console.log(`[AgentColumn] Removing agent ${agentId}...`);

        // STEP 1: Clear the messages container (preserve scroll controls)
        const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
        if (messagesContainer) {
            // Remove only message elements, keep scroll controls
            const messages = messagesContainer.querySelectorAll('.ai-message');
            messages.forEach(msg => msg.remove());
            console.log(`[AgentColumn] Cleared messages for agent ${agentId}`);
        }

        // STEP 2: Clear thread info container
        const threadInfoContainer = document.getElementById(`thread-info-${agentId}`);
        if (threadInfoContainer) {
            threadInfoContainer.innerHTML = `
                <div class="thread-info-wrapper">
                </div>
            `;
            console.log(`[AgentColumn] Cleared thread info for agent ${agentId}`);
        }

        // STEP 3: Reset input area
        const inputTextarea = document.getElementById(`agent-input-${agentId}`);
        if (inputTextarea) {
            inputTextarea.value = '';
        }

        const attachedFilesContainer = document.getElementById(`agent-attached-files-${agentId}`);
        if (attachedFilesContainer) {
            attachedFilesContainer.innerHTML = '';
        }

        // STEP 4: Notify MultiAgent system if available
        if (typeof MultiAgent !== 'undefined' && typeof MultiAgent.unloadAgent === 'function') {
            MultiAgent.unloadAgent(agentId);
            console.log(`[AgentColumn] Notified MultiAgent to unload agent ${agentId}`);
        }

        // STEP 5: Clear any active streaming connections
        if (typeof window.abortController !== 'undefined' && window.abortController[agentId]) {
            try {
                window.abortController[agentId].abort();
                delete window.abortController[agentId];
                console.log(`[AgentColumn] Aborted active stream for agent ${agentId}`);
            } catch (e) {
                console.warn(`[AgentColumn] Failed to abort stream:`, e);
            }
        }

        // STEP 6: Close any popout windows
        if (popoutWindows.has(agentId)) {
            const popoutWindow = popoutWindows.get(agentId);
            popoutWindow.remove();
            popoutWindows.delete(agentId);
            popoutCount--;
            console.log(`[AgentColumn] Closed popout window for agent ${agentId}`);
        }

        // STEP 7: Remove from DOM with animation
        column.style.opacity = '0';
        column.style.transform = 'scale(0.95)';

        setTimeout(() => {
            column.remove();
            console.log(`[AgentColumn] ✅ Agent ${agentId} fully removed and cleaned up`);

            // STEP 8: Dispatch cleanup event
            const cleanupEvent = new CustomEvent('agent-removed', {
                detail: { agentId }
            });
            document.dispatchEvent(cleanupEvent);
        }, 300);
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
     * @param {Event} event - Optional click event to get button position
     */
    function newThread(agentId, event = null) {
        // Don't toggle menu - just open the new chat modal directly
        // toggleMenu(agentId); // REMOVED - was causing menu to open unintentionally

        // Get button element for positioning
        let buttonElement = null;
        if (event && event.target) {
            buttonElement = event.target.closest('button');
        }

        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.showNewChatModal === 'function') {
            ThreadManager.showNewChatModal(`agent-${agentId}`, buttonElement);
        } else {
            console.warn('[AgentColumn] ThreadManager not available');
        }
    }

    /**
     * Refresh current thread in agent column
     * @param {number} agentId - Agent ID
     */
    function refreshThread(agentId) {
        toggleMenu(agentId); // Close menu

        // Find the thread currently loaded in this agent column
        const threadInfo = document.querySelector(`#thread-info-${agentId} [data-thread-id]`);
        if (!threadInfo) {
            console.warn(`[AgentColumn] No thread loaded in agent-${agentId}`);
            if (typeof showNotification === 'function') {
                showNotification('No thread loaded to refresh', 'warning');
            }
            return;
        }

        const threadId = threadInfo.dataset.threadId;
        console.log(`🔄 [AgentColumn] Refreshing thread ${threadId} in agent-${agentId}`);

        // Reload the thread messages
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadThreadInAgent === 'function') {
            ThreadManager.loadThreadInAgent(threadId, agentId);
            if (typeof showNotification === 'function') {
                showNotification('Thread refreshed', 'success');
            }
        } else {
            console.warn('[AgentColumn] ThreadManager.loadThreadInAgent not available');
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
                                            <div class="thread-item-agent-badge main" style="background: #238636; cursor: pointer;" ondblclick="event.stopPropagation(); AgentColumn.loadThreadIntoPrime('${thread.id}'); return false;" title="Double-click to load into Prime Chat">
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
                            <button class="btn-create-thread" onclick="AgentColumn.newThread(${agentId}, event); AgentColumn.hideThreadSelector(${agentId});">
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
                            <button class="btn-create-thread" onclick="AgentColumn.newThread(${agentId}, event); AgentColumn.hideThreadSelector(${agentId});">
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

        // ✅ SAVE VIEW MODE TO STORAGE (localStorage + database)
        if (typeof WorkspaceManager !== 'undefined') {
            WorkspaceManager.save(agentId, 'viewMode', mode);
        }

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
     * Apply view mode to a single message bubble (called when new message arrives)
     * @param {number} agentId - Agent ID
     * @param {HTMLElement} message - The message element to apply view mode to
     */
    function applyViewModeToMessage(agentId, message) {
        const mode = viewModes[agentId] || 'all-expanded'; // Default to all-expanded

        if (!message || !message.classList) return;

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

        console.log(`📐 [AgentColumn] Applied view mode '${mode}' to new message`, message.className);
    }

    /**
     * Legacy function - now just calls cycleExpandMode
     * @param {number} agentId - Agent ID
     */
    function toggleThinkingToolBubbles(agentId) {
        // For backward compatibility, just cycle to next mode
        cycleExpandMode(agentId);
    }

    /**
     * Unload thread from agent without removing the agent column
     * @param {number} agentId - Agent ID
     */
    function unloadThread(agentId) {
        console.log(`[AgentColumn] Unloading thread from agent ${agentId}...`);

        // STEP 1: Clear messages
        const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
        if (messagesContainer) {
            const agentName = getName(agentId);
            messagesContainer.innerHTML = renderEmptyState(agentId, agentName);
            console.log(`[AgentColumn] Cleared messages and showed empty state for agent ${agentId}`);

            // Hide scroll controls when messages cleared
            updateScrollControlsVisibility(agentId);
        }

        // STEP 2: Clear thread info and show "No thread loaded"
        const threadInfoContainer = document.getElementById(`thread-info-${agentId}`);
        if (threadInfoContainer) {
            threadInfoContainer.innerHTML = `
                <div class="thread-info-wrapper">
                </div>
            `;
            console.log(`[AgentColumn] Reset thread info for agent ${agentId}`);
        }

        // STEP 3: Clear collapsed thread info
        const collapsedStatus = document.getElementById(`collapsed-status-${agentId}`);
        if (collapsedStatus) {
            collapsedStatus.textContent = 'No Thread';
        }

        const collapsedTimestamp = document.getElementById(`collapsed-timestamp-${agentId}`);
        if (collapsedTimestamp) {
            collapsedTimestamp.textContent = '';
        }

        // STEP 4: Reset input area
        const inputTextarea = document.getElementById(`agent-input-${agentId}`);
        if (inputTextarea) {
            inputTextarea.value = '';
        }

        const attachedFilesContainer = document.getElementById(`agent-attached-files-${agentId}`);
        if (attachedFilesContainer) {
            attachedFilesContainer.innerHTML = '';
        }

        // STEP 5: Notify MultiAgent system if available
        if (typeof MultiAgent !== 'undefined' && typeof MultiAgent.unloadThreadFromAgent === 'function') {
            MultiAgent.unloadThreadFromAgent(agentId);
            console.log(`[AgentColumn] Notified MultiAgent to unload thread from agent ${agentId}`);
        }

        // STEP 6: Clear any active streaming connections
        if (typeof window.abortController !== 'undefined' && window.abortController[agentId]) {
            try {
                window.abortController[agentId].abort();
                delete window.abortController[agentId];
                console.log(`[AgentColumn] Aborted active stream for agent ${agentId}`);
            } catch (e) {
                console.warn(`[AgentColumn] Failed to abort stream:`, e);
            }
        }

        // STEP 7: Dispatch unload event
        const unloadEvent = new CustomEvent('thread-unloaded', {
            detail: { agentId, location: `agent-${agentId}` }
        });
        document.dispatchEvent(unloadEvent);

        console.log(`[AgentColumn] ✅ Thread unloaded from agent ${agentId}`);
    }

    // Public API
    return {
        create,
        collapse,
        expand,
        popOut,
        toggleWidth,
        scrollToTop,
        scrollToBottom,
        scrollColumnIntoView,
        updateScrollControlsVisibility,
        toggleAutoScroll,
        performAutoScroll,
        toggleMenu,
        remove,
        unloadThread,
        updateThreadInfo,
        newThread,
        refreshThread,
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
        setViewMode,
        applyViewModeToMessage  // ✅ NEW: Apply view mode to single message
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
