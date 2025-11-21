/**
 * SYNERGY BOARD INITIALIZATION
 * Core synergyBoard object that manages Synergy sessions
 * 
 * EXTRACTED FROM: thread_manager_additional.js (lines 6599-12682)
 * DATE: November 20, 2025
 * 
 * This file contains the main synergyBoard controller that:
 * - Creates window.synergyBoard global object
 * - Initializes Kanban board with drag-drop
 * - Manages session loading and rendering
 * - Handles real-time updates via Supabase
 * - Integrates with ThreadManager for thread linking
 */

console.log('📦 [SYNERGY] Starting synergyBoard initialization...');

window.synergyBoard = {
    drake: null,
    sessions: [],
    apiBaseUrl: window.API_BASE_URL || 'http://localhost:5001',
    initialized: false,

    // Safe wrapper for methods that require initialization
    async ensureInitialized() {
        if (!this.initialized) {
            console.log('⏳ [SYNERGY] Auto-initializing synergyBoard...');
            await this.init();
        }
    },

    async init() {
        if (this.initialized) {
            console.log('✅ [SYNERGY] Already initialized');
            return;
        }
        console.log('🚀 Initializing Synergy Dashboard...');

        // Load sessions from API
        await this.loadSessions();

        // Render cards to the board
        this.renderAllCards();
        this.updateStats();

        // Initialize WebSocket for real-time updates
        if (typeof SynergyRealtime !== 'undefined') {
            try {
                await SynergyRealtime.connect();
                console.log('🔌 [SYNERGY] Real-time WebSocket connected');
            } catch (error) {
                console.error('❌ [SYNERGY] Failed to connect WebSocket:', error);
            }
        }

        this.initialized = true;
        console.log('✅ Synergy Dashboard initialized - Board rendered with real-time updates');
    },

    // Escape text for use in JavaScript strings (onclick handlers)
    escapeJs(text) {
        if (!text) return '';
        return text
            .replace(/\\/g, '\\\\')  // Escape backslashes first
            .replace(/'/g, "\\'")     // Escape single quotes
            .replace(/"/g, '\\"')     // Escape double quotes
            .replace(/\n/g, '\\n')    // Escape newlines
            .replace(/\r/g, '\\r');   // Escape carriage returns
    },

    // Escape text for use in HTML (prevents XSS)
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Load sessions from API (with DataLoader caching)
     */
    async loadSessions() {
        try {
            console.log('[SYNERGY] Loading sessions with DataLoader (cached + batched)...');
            const startTime = performance.now();

            // Use DataLoader for caching and batching
            if (typeof DataLoader !== 'undefined' && DataLoader.synergy) {
                this.sessions = await DataLoader.synergy.loadAll();
                const endTime = performance.now();
                const loadTime = (endTime - startTime).toFixed(0);
                console.log(`[SYNERGY] ✅ Loaded ${this.sessions.length} sessions via DataLoader in ${loadTime}ms`);
            } else {
                // Fallback: Direct API call if DataLoader not available
                console.warn('[SYNERGY] DataLoader not available, using direct API call');
                const response = await fetch(`${this.apiBaseUrl}/api/synergy/sessions/batch`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });

                if (!response.ok) {
                    throw new Error(`API error: ${response.status}`);
                }

                const data = await response.json();
                if (data.success) {
                    this.sessions = data.sessions || [];
                    const endTime = performance.now();
                    const loadTime = (endTime - startTime).toFixed(0);
                    console.log(`[SYNERGY] ✅ Batch loaded ${this.sessions.length} sessions in ${loadTime}ms`);
                } else {
                    throw new Error(data.error || 'Batch load failed');
                }
            }

            // Calculate total internal docs
            const totalDocs = this.sessions.reduce((sum, s) => sum + (s.internal_docs_count || 0), 0);
            console.log(`[SYNERGY] 📄 Total internal docs: ${totalDocs}`);

        } catch (error) {
            console.warn('[SYNERGY] API unavailable, using mock data:', error.message);
            // Fallback to mock data if API is unavailable
            this.sessions = this.getMockSessions();
            console.log('[SYNERGY] Mock sessions loaded:', this.sessions.length);
        }
    },

    /**
     * Initialize link interception for Synergy session IDs
     * Detects sess_XXXXX patterns in chat and makes them clickable
     */
    initializeLinkInterception() {
        document.addEventListener('click', (e) => {
            const link = e.target.closest('.synergy-internal-link');
            if (!link) return;

            e.preventDefault();
            e.stopPropagation();

            const sessionId = link.dataset.sessionId;
            if (!sessionId) {
                console.warn('[LINK INTERCEPTION] No session ID found on link:', link);
                return;
            }

            console.log('[LINK INTERCEPTION] Opening Synergy session:', sessionId);

            if (typeof SynergySidebar !== 'undefined') {
                SynergySidebar.toggleSidebar();
                setTimeout(() => {
                    SynergySidebar.expandSessionAsTile(sessionId);
                }, 200);
            } else if (typeof synergyBoard !== 'undefined') {
                synergyBoard.popOutCard(sessionId);
            } else {
                console.warn('[LINK INTERCEPTION] No Synergy interface available');
            }
        });

        console.log('[LINK INTERCEPTION] ✅ Initialized link interception for Synergy sessions');
    },

    /**
     * Open a thread in the appropriate agent column
     */
    openThread(threadId, agentId) {
        console.log(`[SYNERGY] Opening thread ${threadId} in agent ${agentId}`);

        // Switch to AI Agents tab
        const agentsTab = document.querySelector('[data-tab="agents"]');
        if (agentsTab) {
            agentsTab.click();
        }

        // Load thread in the agent column
        if (window.ThreadManager && typeof window.ThreadManager.loadThread === 'function') {
            window.ThreadManager.loadThread(threadId, agentId);
        } else {
            alert(`Would open thread: ${threadId} in agent: ${agentId}\n(ThreadManager integration pending)`);
        }
    },

    /**
     * Handle thread drop onto Synergy card
     * Links a thread to a Synergy session when dropped
     */
    async handleThreadDrop(event, synergyId) {
        event.preventDefault();
        event.stopPropagation();
        event.currentTarget.classList.remove('drag-over');

        // Get dropped thread ID
        const threadId = event.dataTransfer.getData('text/plain');
        if (!threadId) {
            console.warn('[SYNERGY] No thread ID in drop event');
            return;
        }

        console.log(`[SYNERGY] Thread ${threadId} dropped on session ${synergyId}`);

        // Hide welcome container when thread is dropped into Prime
        const welcomeContainer = document.getElementById('prime-welcome-container');
        if (welcomeContainer) {
            welcomeContainer.style.display = 'none';
            console.log('[WELCOME] Hidden - thread dropped into chat');
        }

        try {
            // Link thread to synergy card
            const userId = (window.UserAuth && window.UserAuth.user && (window.UserAuth.user.id || window.UserAuth.user.user_id)) || 1;
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/${synergyId}/link-thread`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    thread_id: threadId,
                    user_id: userId
                })
            });

            const result = await response.json();

            if (result.success) {
                console.log('[SYNERGY] ✅ Thread linked successfully');
                if (window.showNotification) {
                    window.showNotification('Thread linked to Synergy card', 'success');
                }

                // Refresh the specific card's linked threads section
                await this.refreshCardThreads(synergyId);
            } else {
                console.error('[SYNERGY] Failed to link thread:', result.error);
                if (window.showNotification) {
                    window.showNotification('Failed to link thread: ' + (result.error || 'Unknown error'), 'error');
                }
            }
        } catch (error) {
            console.error('[SYNERGY] Error linking thread:', error);
            if (window.showNotification) {
                window.showNotification('Error linking thread', 'error');
            }
        }
    },

    /**
     * Render linked threads for a session
     * Fetches threads linked to this Synergy card and displays them
     */
    async renderLinkedThreads(sessionId) {
        try {
            // Fetch threads linked to this session
            const userId = (window.UserAuth && window.UserAuth.user && (window.UserAuth.user.id || window.UserAuth.user.user_id)) || 1;
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/${sessionId}/threads?user_id=${userId}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch threads: ${response.status}`);
            }

            const result = await response.json();
            const threads = result.threads || [];

            if (threads.length === 0) {
                return `
                    <div class="no-threads-message">
                        <i class="fas fa-inbox"></i>
                        <p>No threads linked yet</p>
                        <small>Drag threads from sidebar to link them</small>
                    </div>
                `;
            }

            // Batch fetch Synergy metadata for all linked threads (if they have synergy_card_id)
            const cache = {};
            const synergyIds = [...new Set(threads.filter(t => t.synergy_card_id).map(t => t.synergy_card_id))];
            if (synergyIds.length > 0) {
                try {
                    const batchResponse = await fetch(`${this.apiBaseUrl}/api/synergy/sessions/batch?ids=${synergyIds.join(',')}`, {
                        method: 'GET',
                        headers: { 'Content-Type': 'application/json' }
                    });
                    if (batchResponse.ok) {
                        const batchData = await batchResponse.json();
                        if (batchData.success && Array.isArray(batchData.sessions)) {
                            batchData.sessions.forEach(s => {
                                cache[s.session_id] = s;
                            });
                        }
                    }
                } catch (err) {
                    console.warn('[SYNERGY] Failed to fetch synergy metadata:', err);
                }
            }

            // Build unified thread-info containers for each thread
            const threadsHTML = threads.map(thread => {
                // Get synergy metadata from cache
                const synergyMeta = thread.synergy_card_id ? cache[thread.synergy_card_id] : null;
                const synergyTitle = synergyMeta ? (synergyMeta.title || thread.synergy_card_id) : (thread.synergy_card_name || thread.synergy_card_id || 'Unknown Session');
                const synergyPriority = synergyMeta ? (synergyMeta.priority || '') : '';
                const synergyDesc = synergyMeta ? (synergyMeta.description || '') : '';
                const synergyUsers = synergyMeta ? (Array.isArray(synergyMeta.assignees) ? synergyMeta.assignees.join(', ') : '') : '';
                const synergyUpdated = synergyMeta ? (synergyMeta.last_active ? new Date(synergyMeta.last_active).toLocaleString() : '') : '';

                // Normalize thread object structure for ThreadManager
                const normalizedThread = {
                    id: thread.thread_slug || thread.id,
                    title: thread.name || thread.thread_slug || thread.id,
                    created: thread.created_at || thread.created,
                    updated: thread.updated_at || thread.updated,
                    message_count: thread.message_count || 0,
                    messages: [],
                    tags: thread.tags || [],
                    synergy_card_id: thread.synergy_card_id,
                    synergy_card_name: synergyTitle,
                    synergy_card_desc: synergyDesc,
                    synergy_card_users: synergyUsers,
                    synergy_card_updated: synergyUpdated,
                    synergy_card_priority: synergyPriority,
                    agent: thread.agent_id || 'prime'
                };

                // Temporarily add to ThreadManager.threads if not exists (for rendering)
                const existingThread = window.ThreadManager.threads.find(t => t.id === normalizedThread.id);
                if (!existingThread) {
                    window.ThreadManager.threads.push(normalizedThread);
                }

                // Render unified container
                const threadInfoHTML = window.ThreadManager.renderThreadInfoContainer(
                    'synergy',
                    normalizedThread.id,
                    true  // compact mode
                );

                return `
                    <div class="synergy-linked-thread-wrapper" 
                         data-thread-id="${normalizedThread.id}"
                         draggable="true"
                         ondragstart="ThreadManager.handleDragStart(event)"
                         onclick="synergyBoard.openThread('${normalizedThread.id}', '${thread.agent_id || 'prime'}')">
                        ${threadInfoHTML}
                    </div>
                `;
            }).join('');

            return `
                <div class="linked-threads-container">
                    <div class="linked-threads-list">
                        ${threadsHTML}
                    </div>
                </div>
            `;

        } catch (error) {
            console.error('[SYNERGY] Error rendering linked threads:', error);
            return `<div class="threads-error"><i class="fas fa-exclamation-triangle"></i> Error loading threads</div>`;
        }
    },

    /**
     * Refresh card threads section without full card re-render
     */
    async refreshCardThreads(sessionId) {
        const card = document.querySelector(`[data-session-id="${sessionId}"]`);
        if (!card) return;

        const threadsSection = card.querySelector('.linked-threads-section');
        if (threadsSection) {
            const threadsHTML = await this.renderLinkedThreads(sessionId);
            const threadsContent = threadsSection.querySelector('.section-content');
            if (threadsContent) {
                threadsContent.innerHTML = threadsHTML;
            }
        }
    },

    /**
     * Refresh the entire board - reload sessions and re-render
     */
    async refreshBoard() {
        await this.ensureInitialized();
        console.log('🔄 Refreshing board...');

        await this.loadSessions();
        this.renderAllCards();
        this.updateStats();

        console.log('✅ Board refreshed');
    },

    /**
     * Render all cards on the board
     */
    renderAllCards() {
        console.log(`[SYNERGY] Rendering ${this.sessions.length} cards...`);

        // Save expanded states before clearing
        const expandedCards = new Set();
        document.querySelectorAll('.kanban-card[data-expanded="true"]').forEach(card => {
            expandedCards.add(card.dataset.sessionId);
        });

        // Clear all kanban columns
        ['backlog', 'in_progress', 'review', 'done'].forEach(column => {
            const container = document.getElementById(`${column}-cards`);
            if (container) {
                container.innerHTML = '';
            }
        });

        // Render each session
        this.sessions.forEach(session => {
            this.renderCard(session);
        });

        // Restore expanded states
        expandedCards.forEach(sessionId => {
            const card = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
            if (card) {
                card.dataset.expanded = 'true';
            }
        });

        console.log(`✅ [SYNERGY] Rendered ${this.sessions.length} cards`);
    },

    /**
     * Render a single session card to its kanban column
     */
    renderCard(session) {
        // Map database column names to HTML container IDs
        const columnMapping = {
            'in-progress': 'in_progress',
            'in_progress': 'in_progress',
            'backlog': 'backlog',
            'review': 'review',
            'done': 'done'
        };

        const dbColumn = session.kanban_column || 'backlog';
        const htmlColumn = columnMapping[dbColumn] || dbColumn;
        const container = document.getElementById(`${htmlColumn}-cards`);

        if (!container) {
            console.warn(`[SYNERGY] Container not found for column: ${dbColumn} (mapped to ${htmlColumn})`);
            return;
        }

        // Create card element
        const card = document.createElement('div');
        card.className = 'kanban-card';
        card.dataset.sessionId = session.session_id;
        card.dataset.column = htmlColumn;

        // Enable drag and drop
        card.draggable = true;
        card.addEventListener('dragstart', (e) => this.handleDragStart(e));
        card.addEventListener('dragend', (e) => this.handleDragEnd(e));

        // Priority emoji
        const priorityEmoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }[session.priority || 'medium'];

        // Time ago
        const createdDate = new Date(session.created_at);
        const timeAgo = this.getTimeAgo(createdDate);

        // Calculate progress
        const totalMilestones = session.total_milestones || 0;
        const completedMilestones = session.completed_milestones || 0;
        const totalTasks = session.total_tasks || 0;
        const completedTasks = session.completed_tasks || 0;
        const progressPercent = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

        // Status badge
        const statusClass = (session.status || 'active').toLowerCase().replace(/\s+/g, '-');

        // Card HTML with 4-row structure
        card.innerHTML = `
            <div class="synergy-session-header-new">
                
                <!-- TITLE ROW - Clickable for expand -->
                <div class="synergy-title-row" onclick="synergyBoard.toggleCardExpand('${session.session_id}')" style="cursor: pointer;">
                    <div class="synergy-title-text">${this.escapeHtml(session.title || 'Untitled Session')}</div>
                    <button class="synergy-icon-btn synergy-chevron" style="pointer-events: none;">
                        <i class="fas fa-chevron-down"></i>
                    </button>
                </div>

                <!-- ROW 1: Priority + Status + Actions -->
                <div class="synergy-row-1">
                    <span class="priority-badge priority-${(session.priority || 'medium').toLowerCase()}">${session.priority || 'Medium'}</span>
                    <span class="status-badge status-${statusClass}">${session.status || 'Active'}</span>
                    
                    <div class="synergy-actions">
                        <button class="synergy-icon-btn" onclick="event.stopPropagation(); synergyBoard.openCardMenu('${session.session_id}')" title="Menu">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                    </div>
                </div>

                <!-- ROW 2: Description -->
                <div class="synergy-row-2">
                    <div class="synergy-description">${session.description ? (session.description.length > 100 ? this.escapeHtml(session.description.substring(0, 100)) + '...' : this.escapeHtml(session.description)) : 'No description'}</div>
                </div>

                <!-- ROW 3: Stats -->
                <div class="synergy-row-3">
                    ${session.due_date ? `<div class="synergy-stat"><i class="fas fa-calendar-alt"></i><span>${new Date(session.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span></div>` : ''}
                    <div class="synergy-stat"><i class="fas fa-flag"></i><span>${completedMilestones}/${totalMilestones}</span></div>
                    <div class="synergy-stat"><i class="fas fa-tasks"></i><span>${completedTasks}/${totalTasks}</span></div>
                    <div class="synergy-stat"><i class="fas fa-file-alt"></i><span>${session.internal_docs_count || 0}</span></div>
                </div>

                <!-- ROW 4: Progress + Footer -->
                <div class="synergy-row-4">
                    <div class="synergy-progress-bar">
                        <div class="synergy-progress-fill" style="width: ${progressPercent}%"></div>
                    </div>
                    <div class="synergy-footer">
                        <div class="synergy-project">${this.escapeHtml(session.project_name || 'General')}</div>
                        <div class="synergy-updated">${timeAgo}</div>
                    </div>
                </div>
            </div>
        `;

        container.appendChild(card);
    },

    /**
     * Update column statistics
     */
    updateStats() {
        ['backlog', 'in_progress', 'review', 'done'].forEach(column => {
            const container = document.getElementById(`${column}-cards`);
            const countBadge = document.querySelector(`[data-column="${column}"] .column-count`);

            if (container && countBadge) {
                const count = container.children.length;
                countBadge.textContent = count;
            }
        });
    },

    /**
     * Format time ago string
     */
    getTimeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);

        if (seconds < 60) return 'just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
        return date.toLocaleDateString();
    },

    /**
     * Toggle card expansion (show/hide details)
     */
    async toggleCardExpand(sessionId) {
        const card = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
        if (!card) return;

        const isExpanded = card.dataset.expanded === 'true';

        if (isExpanded) {
            // Collapse - remove expanded content
            card.dataset.expanded = 'false';
            card.classList.remove('expanded');
            const expandedContent = card.querySelector('.synergy-card-expanded-content');
            if (expandedContent) {
                expandedContent.remove();
            }
            console.log(`[SYNERGY] Collapsed card: ${sessionId}`);
        } else {
            // Expand - load and show milestones
            card.dataset.expanded = 'true';
            card.classList.add('expanded');
            console.log(`[SYNERGY] Expanded card: ${sessionId}`);

            // Load milestones if not already loaded
            let expandedContent = card.querySelector('.synergy-card-expanded-content');
            if (!expandedContent) {
                // Create expanded content container
                expandedContent = document.createElement('div');
                expandedContent.className = 'synergy-card-expanded-content';
                expandedContent.innerHTML = '<div class="loading-placeholder"><i class="fas fa-spinner fa-spin"></i> Loading milestones...</div>';
                card.querySelector('.synergy-session-header-new').appendChild(expandedContent);

                try {
                    // Fetch milestones
                    const response = await fetch(`http://localhost:5001/api/synergy/${sessionId}/milestones`);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }

                    const data = await response.json();
                    const milestones = data.milestones || [];

                    // Render milestones
                    if (milestones.length === 0) {
                        expandedContent.innerHTML = '<div style="padding: 16px; text-align: center; color: var(--text-secondary);">No milestones yet</div>';
                    } else {
                        expandedContent.innerHTML = milestones.map(m => `
                            <div class="milestone-card" style="padding: 12px; margin: 8px 0; background: var(--bg-secondary); border-radius: 8px; border-left: 3px solid ${m.completed ? 'var(--accent-success)' : 'var(--accent-primary)'};">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <div style="font-weight: 600; color: var(--text-primary);">
                                        <i class="fas ${m.completed ? 'fa-check-circle' : 'fa-circle'}" style="color: ${m.completed ? 'var(--accent-success)' : 'var(--text-tertiary)'}; margin-right: 8px;"></i>
                                        ${this.escapeHtml(m.milestone_name)}
                                    </div>
                                    ${m.due_date ? `<div style="font-size: 12px; color: var(--text-secondary);">${new Date(m.due_date).toLocaleDateString()}</div>` : ''}
                                </div>
                                ${m.description ? `<div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 8px;">${this.escapeHtml(m.description)}</div>` : ''}
                                ${m.tasks && m.tasks.length > 0 ? `
                                    <div style="font-size: 12px; color: var(--text-tertiary); margin-top: 8px;">
                                        <i class="fas fa-tasks"></i> ${m.tasks.filter(t => t.completed).length}/${m.tasks.length} tasks completed
                                    </div>
                                ` : ''}
                            </div>
                        `).join('');
                    }
                } catch (error) {
                    expandedContent.innerHTML = `
                        <div style="padding: 16px; background: rgba(220, 38, 38, 0.1); border: 2px solid #dc2626; border-radius: 8px; color: #dc2626; margin: 8px;">
                            <i class="fas fa-exclamation-triangle"></i> Failed to load milestones: ${error.message}
                        </div>
                    `;
                }
            }
        }
    },

    /**
     * Open card menu (edit, delete, etc.)
     */
    openCardMenu(sessionId) {
        console.log('[SYNERGY] Opening card menu for:', sessionId);
        // TODO: Implement context menu
        alert(`Card menu for ${sessionId}\n\nOptions:\n- Edit\n- Delete\n- Move to column\n- Archive`);
    }
};

// Initialize Synergy Dashboard when tab is activated
document.addEventListener('DOMContentLoaded', () => {
    const synergyTab = document.querySelector('.sidebar-icon-btn[data-tab="synergy"]');
    if (synergyTab) {
        let initialized = false;
        synergyTab.addEventListener('click', async () => {
            if (!initialized) {
                // Ensure Supabase config is loaded before initializing
                if (window.loadSupabaseConfig) {
                    await window.loadSupabaseConfig();
                }
                await synergyBoard.init();
                // Initialize sidebar renderer
                if (typeof SynergySidebar !== 'undefined') {
                    SynergySidebar.init();
                }
                initialized = true;
            }
        });
    }

    // Initialize link interception for Synergy sessions
    if (typeof synergyBoard !== 'undefined') {
        synergyBoard.initializeLinkInterception();
    }
});

console.log('✅ [SYNERGY] synergy-board-init.js loaded successfully');
