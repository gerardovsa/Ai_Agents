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
    initPromise: null, // Track initialization promise to avoid duplicate inits

    // Safe wrapper for methods that require initialization
    async ensureInitialized() {
        if (this.initialized) {
            return; // Already initialized
        }
        if (this.initPromise) {
            console.log('⏳ [SYNERGY] Waiting for ongoing initialization...');
            await this.initPromise; // Wait for ongoing initialization
            return;
        }
        console.log('⏳ [SYNERGY] Auto-initializing synergyBoard...');
        this.initPromise = this.init();
        await this.initPromise;
        this.initPromise = null;
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
     * Fallback renderer for expanded content when SynergySidebarRenderer is not available
     */
    renderExpandedContentFallback(session, milestones, sessionId) {
        return `
            <div class="synergy-flat-container" data-session-id="${sessionId}" style="padding: 16px; background: var(--bg-secondary); border-radius: 8px;">
                <div style="font-size: 14px; color: var(--text-secondary); margin-bottom: 12px;">
                    <i class="fas fa-info-circle"></i> Synergy Renderer Loading...
                </div>
                <div style="font-size: 13px; color: var(--text-tertiary);">
                    ${milestones.length} milestone(s) found
                </div>
                ${milestones.length > 0 ? `
                    <div style="margin-top: 16px;">
                        ${milestones.map(m => `
                            <div style="
                                padding: 12px;
                                background: var(--bg-primary);
                                border-left: 3px solid var(--accent-primary);
                                border-radius: 6px;
                                margin-bottom: 8px;
                            ">
                                <div style="font-size: 15px; color: var(--text-primary); margin-bottom: 4px;">
                                    ${this.escapeHtml(m.milestone || 'Untitled Milestone')}
                                </div>
                                ${m.description ? `
                                    <div style="font-size: 13px; color: var(--text-secondary);">
                                        ${this.escapeHtml(m.description)}
                                    </div>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    },

    /**
     * Handle drag start for Synergy cards
     */
    handleDragStart(event) {
        const card = event.currentTarget;
        const sessionId = card.dataset.sessionId;

        console.log('[SYNERGY DRAG] Started dragging session:', sessionId);

        // Set drag data
        event.dataTransfer.effectAllowed = 'move';
        event.dataTransfer.setData('text/plain', sessionId);
        event.dataTransfer.setData('synergy-session', sessionId);

        // Add visual feedback
        card.classList.add('dragging');
        card.style.opacity = '0.5';
    },

    /**
     * Handle drag end for Synergy cards
     */
    handleDragEnd(event) {
        const card = event.currentTarget;
        const sessionId = card.dataset.sessionId;

        console.log('[SYNERGY DRAG] Ended dragging session:', sessionId);

        // Remove visual feedback
        card.classList.remove('dragging');
        card.style.opacity = '1';

        // Remove drag-over class from all columns
        document.querySelectorAll('.kanban-column').forEach(col => {
            col.classList.remove('drag-over');
        });
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

        // Create card element - using synergy-session-item class for shared styling
        const card = document.createElement('div');
        card.className = 'synergy-session-item kanban-card';
        card.dataset.sessionId = session.session_id;
        card.dataset.column = htmlColumn;
        card.dataset.context = 'dashboard';

        // Enable drag and drop for card reordering
        card.draggable = true;
        card.addEventListener('dragstart', (e) => this.handleDragStart(e));
        card.addEventListener('dragend', (e) => this.handleDragEnd(e));

        // Enable thread drop zone (for linking threads to synergy sessions)
        card.addEventListener('dragover', (e) => this.handleThreadDragOver(e));
        card.addEventListener('dragleave', (e) => this.handleThreadDragLeave(e));
        card.addEventListener('drop', (e) => this.handleThreadDrop(e, session.session_id));

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
                        <button class="synergy-icon-btn" onclick="event.stopPropagation(); synergyBoard.openCardMenu('${session.session_id}', event)" title="Menu">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                    </div>
                </div>

                <!-- ROW 2: Description (truncated, hover for full) -->
                <div class="synergy-row-2">
                    <div class="synergy-description" title="${session.description ? this.escapeHtml(session.description) : 'No description'}">
                        ${session.description ? (session.description.length > 100 ? this.escapeHtml(session.description.substring(0, 100)) + '...' : this.escapeHtml(session.description)) : 'No description'}
                    </div>
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
                        <div class="synergy-footer-row-1">
                            <div class="synergy-project">${this.escapeHtml(session.project_name || 'General')}</div>
                            <div class="synergy-updated">${timeAgo}</div>
                        </div>
                        ${session.tags && session.tags.length > 0 ? `
                            <div class="synergy-footer-row-2">
                                <div class="synergy-tags">
                                    ${session.tags.slice(0, 3).map(tag => `<span class="synergy-tag">${this.escapeHtml(tag)}</span>`).join('')}
                                </div>
                            </div>
                        ` : ''}
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
     * Now uses unified rendering with full milestone/task/subtask hierarchy
     */
    async toggleCardExpand(sessionId, event = null) {
        // Stop event propagation to prevent multiple triggers from nested elements
        if (event) {
            event.stopPropagation();
            event.preventDefault();
        }

        const card = document.querySelector(`.synergy-session-item[data-session-id="${sessionId}"][data-context="dashboard"]`);
        if (!card) return;

        // Prevent race conditions from rapid clicks
        if (card.dataset.processing === 'true') {
            console.log(`[SYNERGY] Card ${sessionId} already processing, ignoring click`);
            return;
        }

        const isExpanded = card.dataset.expanded === 'true';

        if (isExpanded) {
            // Collapse - hide expanded content
            card.dataset.expanded = 'false';
            card.classList.remove('expanded');
            const expandedContent = card.querySelector('.synergy-card-expanded-content');
            if (expandedContent) {
                expandedContent.style.display = 'none';
            }
            // Update chevron
            const chevron = card.querySelector('.synergy-chevron i');
            if (chevron) chevron.className = 'fas fa-chevron-down';
            console.log(`[SYNERGY] Collapsed card: ${sessionId}`);
        } else {
            // Mark as processing to prevent concurrent expand operations
            card.dataset.processing = 'true';
            // Expand - load and show full milestones hierarchy
            card.dataset.expanded = 'true';
            card.classList.add('expanded');
            console.log(`[SYNERGY] Expanded card: ${sessionId}`);

            // Load milestones if not already loaded
            let expandedContent = card.querySelector('.synergy-card-expanded-content');
            if (!expandedContent) {
                // Create expanded content container
                expandedContent = document.createElement('div');
                expandedContent.className = 'synergy-card-expanded-content';
                expandedContent.style.display = 'block';
                expandedContent.innerHTML = '<div class="loading-placeholder"><i class="fas fa-spinner fa-spin"></i> Loading session data...</div>';
                card.querySelector('.synergy-session-header-new').appendChild(expandedContent);

                try {
                    // Fetch milestones with full hierarchy
                    const response = await fetch(`http://localhost:5001/api/synergy/${sessionId}/milestones`);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }

                    const data = await response.json();
                    const milestones = data.milestones || [];
                    const session = data.session || {};

                    console.log(`[SYNERGY] Loaded ${milestones.length} milestones for ${sessionId}`);

                    // Use unified renderer from SynergySidebarRenderer
                    if (window.SynergySidebarRenderer) {
                        const renderer = new window.SynergySidebarRenderer();
                        expandedContent.innerHTML = renderer.renderExpandedCardContent(session, milestones, sessionId);
                    } else {
                        // Fallback to basic rendering if renderer not available
                        expandedContent.innerHTML = this.renderExpandedContentFallback(session, milestones, sessionId);
                    }

                    // Update chevron
                    const chevron = card.querySelector('.synergy-chevron i');
                    if (chevron) chevron.className = 'fas fa-chevron-up';
                } catch (error) {
                    console.error('[SYNERGY] Error loading milestones:', error);
                    expandedContent.innerHTML = `
                        <div style="
                            padding: 16px;
                            background: rgba(220, 38, 38, 0.1);
                            border: 2px solid #dc2626;
                            border-radius: 8px;
                            color: #dc2626;
                        ">
                            <div style="font-weight: 700; margin-bottom: 8px;">
                                <i class="fas fa-exclamation-triangle"></i> Error Loading Session
                            </div>
                            <div style="font-size: 12px; opacity: 0.9;">
                                ${this.escapeHtml(error.message)}
                            </div>
                        </div>
                    `;
                } finally {
                    // Clear processing flag after DOM updates complete
                    setTimeout(() => {
                        card.dataset.processing = 'false';
                    }, 100);
                }
            } else {
                // Expanded content already exists, just show it
                expandedContent.style.display = 'block';
                const chevron = card.querySelector('.synergy-chevron i');
                if (chevron) chevron.className = 'fas fa-chevron-up';

                // Clear processing flag immediately since no async work needed
                card.dataset.processing = 'false';
            }
        }
    },

    /**
     * Open card menu (edit, delete, archive)
     */
    openCardMenu(sessionId, event) {
        console.log('[SYNERGY] Opening card menu for:', sessionId);

        // Close any existing menus
        const existingMenu = document.querySelector('.synergy-card-dropdown-menu');
        if (existingMenu) {
            existingMenu.remove();
        }

        // Get button position for menu placement
        const button = event ? event.target.closest('.synergy-icon-btn') : null;
        if (!button) return;

        const rect = button.getBoundingClientRect();

        // Create dropdown menu
        const menu = document.createElement('div');
        menu.className = 'synergy-card-dropdown-menu';
        menu.style.cssText = `
            position: fixed;
            top: ${rect.bottom + 5}px;
            left: ${rect.left - 150}px;
            background: var(--bg-primary);
            border: 1px solid var(--border-secondary);
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 10000;
            min-width: 180px;
            padding: 8px 0;
        `;

        menu.innerHTML = `
            <button class="synergy-dropdown-item" onclick="synergyBoard.editCardFromMenu('${sessionId}'); this.closest('.synergy-card-dropdown-menu').remove();">
                <i class="fas fa-edit" style="width: 20px; color: #3b82f6;"></i>
                <span>Edit Session</span>
            </button>
            <button class="synergy-dropdown-item" onclick="synergyBoard.archiveCard('${sessionId}'); this.closest('.synergy-card-dropdown-menu').remove();">
                <i class="fas fa-archive" style="width: 20px; color: #f59e0b;"></i>
                <span>Archive</span>
            </button>
            <div style="height: 1px; background: var(--border-secondary); margin: 8px 0;"></div>
            <button class="synergy-dropdown-item danger" onclick="synergyBoard.deleteCard('${sessionId}'); this.closest('.synergy-card-dropdown-menu').remove();">
                <i class="fas fa-trash" style="width: 20px; color: #ef4444;"></i>
                <span>Delete Session</span>
            </button>
        `;

        document.body.appendChild(menu);

        // Close menu when clicking outside
        setTimeout(() => {
            document.addEventListener('click', function closeMenu(e) {
                if (!menu.contains(e.target) && !button.contains(e.target)) {
                    menu.remove();
                    document.removeEventListener('click', closeMenu);
                }
            });
        }, 10);
    },

    /**
     * Edit card from menu
     */
    async editCardFromMenu(sessionId) {
        console.log('[SYNERGY] Editing session:', sessionId);

        // Use popup modal if available
        if (window.synergyPopupModal) {
            await window.synergyPopupModal.open(sessionId);
            setTimeout(() => {
                window.synergyPopupModal.toggleEditMode();
            }, 500);
        } else {
            alert('Edit functionality requires popup modal. Please enable it.');
        }
    },

    /**
     * Archive card
     */
    async archiveCard(sessionId) {
        if (!confirm('Archive this session? You can restore it later from archived sessions.')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/${sessionId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: 'archived' })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            console.log('[SYNERGY] Archived session:', sessionId);

            // Remove card from board
            const card = document.querySelector(`.synergy-session-item[data-session-id="${sessionId}"]`);
            if (card) {
                card.style.transition = 'opacity 0.3s, transform 0.3s';
                card.style.opacity = '0';
                card.style.transform = 'scale(0.9)';
                setTimeout(() => card.remove(), 300);
            }

            // Refresh board
            await this.fetchAndRenderAllSessions();

        } catch (error) {
            console.error('[SYNERGY] Failed to archive session:', error);
            alert('Failed to archive session. Please try again.');
        }
    },

    /**
     * Delete card permanently
     */
    async deleteCard(sessionId) {
        if (!confirm('⚠️ PERMANENTLY DELETE this session?\n\nThis action CANNOT be undone!\n\nAll milestones, tasks, and data will be lost.')) {
            return;
        }

        // Double confirmation for safety
        if (!confirm('Are you absolutely sure? This will delete ALL data for this session.')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/${sessionId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            console.log('[SYNERGY] Deleted session:', sessionId);

            // Remove card from board with animation
            const card = document.querySelector(`.synergy-session-item[data-session-id="${sessionId}"]`);
            if (card) {
                card.style.transition = 'opacity 0.3s, transform 0.3s';
                card.style.opacity = '0';
                card.style.transform = 'scale(0.8)';
                setTimeout(() => card.remove(), 300);
            }

            // Refresh board
            await this.fetchAndRenderAllSessions();

        } catch (error) {
            console.error('[SYNERGY] Failed to delete session:', error);
            alert('Failed to delete session. Please try again.');
        }
    },

    /**
     * Pop out card in modal window (same as expanded content)
     */
    async popOutCard(sessionId) {
        console.log('[SYNERGY] Opening session in popup:', sessionId);

        try {
            // Fetch session data and milestones
            const sessionResponse = await fetch(`http://localhost:5001/api/synergy/${sessionId}`);
            if (!sessionResponse.ok) {
                throw new Error(`Failed to load session: ${sessionResponse.status}`);
            }
            const sessionData = await sessionResponse.json();
            const session = sessionData.session || {};

            const milestonesResponse = await fetch(`http://localhost:5001/api/synergy/${sessionId}/milestones`);
            if (!milestonesResponse.ok) {
                throw new Error(`Failed to load milestones: ${milestonesResponse.status}`);
            }
            const milestonesData = await milestonesResponse.json();
            const milestones = milestonesData.milestones || [];

            // Create modal overlay
            const modal = document.createElement('div');
            modal.className = 'synergy-popup-overlay';
            modal.innerHTML = `
                <div class="synergy-popup-modal">
                    <div class="synergy-popup-header">
                        <div>
                            <h2 style="margin: 0; font-size: 20px; color: var(--text-primary);">${this.escapeHtml(session.title || 'Untitled Session')}</h2>
                            <div style="font-size: 13px; color: var(--text-secondary); margin-top: 4px;">
                                Session ID: ${sessionId}
                            </div>
                        </div>
                        <button class="synergy-popup-close" onclick="this.closest('.synergy-popup-overlay').remove()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="synergy-popup-body">
                        ${milestones.length === 0 ?
                    '<div style="padding: 32px; text-align: center; color: var(--text-secondary);">No milestones yet</div>' :
                    milestones.map(m => {
                        const completedTasks = m.tasks ? m.tasks.filter(t => t.completed).length : 0;
                        const totalTasks = m.tasks ? m.tasks.length : 0;
                        const progress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

                        return `
                                    <div class="milestone-compact ${m.completed ? 'completed' : ''} ${m.blocked ? 'blocked' : ''}">
                                        <div class="milestone-header-compact">
                                            <div class="milestone-badge">M${m.milestone_number || '?'}</div>
                                            <div class="milestone-name-compact">${this.escapeHtml(m.milestone_name || 'Untitled Milestone')}</div>
                                            ${totalTasks > 0 ? `<div class="milestone-progress-compact">${progress}%</div>` : ''}
                                            ${m.due_date ? `<div class="milestone-due-date"><i class="fas fa-calendar"></i> ${new Date(m.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</div>` : ''}
                                        </div>
                                        ${m.description ? `<div class="milestone-description-compact">${this.escapeHtml(m.description)}</div>` : ''}
                                        ${totalTasks > 0 ? `
                                            <div class="milestone-stats-compact">
                                                <span><i class="fas fa-tasks"></i> ${completedTasks}/${totalTasks} tasks</span>
                                                ${m.estimated_hours ? `<span><i class="fas fa-clock"></i> ${m.estimated_hours}h estimated</span>` : ''}
                                            </div>
                                        ` : ''}
                                    </div>
                                `;
                    }).join('')
                }
                    </div>
                </div>
            `;

            // Close on overlay click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.remove();
                }
            });

            document.body.appendChild(modal);

        } catch (error) {
            console.error('[SYNERGY] Error opening popup:', error);
            alert(`Failed to open session: ${error.message}`);
        }
    },

    /**
     * Show real-time diagnostics modal
     * Displays WebSocket connection status, heartbeat info, and connection history
     */
    showRealtimeDiagnostics() {
        console.log('[SYNERGY] Opening real-time diagnostics...');

        // Get connection status from SynergyRealtime
        const isConnected = window.SynergyRealtime?.isConnected() || false;
        const socketId = window.SynergyRealtime?.socket?.id || 'Not connected';
        const connectionStatus = isConnected ? '🟢 Connected' : '🔴 Disconnected';

        // Create modal
        const modal = document.createElement('div');
        modal.className = 'edit-card-modal';
        modal.innerHTML = `
            <div class="modal-overlay"></div>
            <div class="modal-content" style="max-width: 600px;">
                <div class="modal-header">
                    <h3><i class="fas fa-signal"></i> Real-Time Diagnostics</h3>
                    <button class="modal-close-btn" onclick="this.closest('.edit-card-modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div style="display: flex; flex-direction: column; gap: 16px;">
                        <!-- Connection Status -->
                        <div style="
                            padding: 16px;
                            background: ${isConnected ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)'};
                            border: 2px solid ${isConnected ? '#22c55e' : '#ef4444'};
                            border-radius: 8px;
                        ">
                            <div style="font-weight: 700; font-size: 16px; margin-bottom: 8px;">
                                ${connectionStatus}
                            </div>
                            <div style="font-size: 13px; color: var(--text-secondary);">
                                Socket ID: <code style="
                                    background: var(--bg-tertiary);
                                    padding: 2px 6px;
                                    border-radius: 4px;
                                    font-family: monospace;
                                ">${socketId}</code>
                            </div>
                        </div>

                        <!-- Connection Details -->
                        <div style="
                            padding: 16px;
                            background: var(--bg-tertiary);
                            border-radius: 8px;
                        ">
                            <div style="font-weight: 700; margin-bottom: 12px;">
                                <i class="fas fa-info-circle"></i> Connection Details
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 8px; font-size: 13px;">
                                <div><strong>Namespace:</strong> /ws/synergy</div>
                                <div><strong>Room:</strong> synergy_board</div>
                                <div><strong>Transport:</strong> ${window.SynergyRealtime?.socket?.io?.engine?.transport?.name || 'Unknown'}</div>
                                <div><strong>Reconnect Attempts:</strong> ${window.SynergyRealtime?.reconnectAttempts || 0}</div>
                            </div>
                        </div>

                        <!-- Events Subscribed -->
                        <div style="
                            padding: 16px;
                            background: var(--bg-tertiary);
                            border-radius: 8px;
                        ">
                            <div style="font-weight: 700; margin-bottom: 12px;">
                                <i class="fas fa-plug"></i> Subscribed Events
                            </div>
                            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                                <span class="status-badge status-active">session_created</span>
                                <span class="status-badge status-active">session_updated</span>
                                <span class="status-badge status-active">session_deleted</span>
                                <span class="status-badge status-active">column_changed</span>
                                <span class="status-badge status-active">pong</span>
                            </div>
                        </div>

                        <!-- Actions -->
                        <div style="
                            padding: 16px;
                            background: var(--bg-tertiary);
                            border-radius: 8px;
                        ">
                            <div style="font-weight: 700; margin-bottom: 12px;">
                                <i class="fas fa-wrench"></i> Actions
                            </div>
                            <div style="display: flex; gap: 8px;">
                                <button class="btn-secondary" onclick="
                                    if (window.SynergyRealtime) {
                                        window.SynergyRealtime.ping();
                                        alert('Ping sent! Check console for response.');
                                    }
                                ">
                                    <i class="fas fa-heartbeat"></i> Send Ping
                                </button>
                                <button class="btn-secondary" onclick="
                                    if (window.SynergyRealtime) {
                                        window.SynergyRealtime.disconnect();
                                        setTimeout(() => window.SynergyRealtime.connect(), 1000);
                                        alert('Reconnecting...');
                                    }
                                ">
                                    <i class="fas fa-sync-alt"></i> Reconnect
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="this.closest('.edit-card-modal').remove()">
                        Close
                    </button>
                </div>
            </div>
        `;

        // Close on overlay click
        modal.querySelector('.modal-overlay').addEventListener('click', () => {
            modal.remove();
        });

        document.body.appendChild(modal);
    },

    /**
     * THREAD DRAG-AND-DROP HANDLERS
     * Handle threads being dropped onto synergy cards to link them
     */

    handleThreadDragOver(event) {
        // Check if dragging a thread (not a synergy card)
        const types = Array.from(event.dataTransfer.types);
        const isThread = types.includes('text/plain'); // Thread cards set 'text/plain' with thread ID

        if (isThread) {
            event.preventDefault();
            event.stopPropagation();
            event.dataTransfer.dropEffect = 'link';

            // Add visual feedback
            event.currentTarget.classList.add('drag-over');
        }
    },

    handleThreadDragLeave(event) {
        event.currentTarget.classList.remove('drag-over');
    },

    async handleThreadDrop(event, synergySessionId) {
        event.preventDefault();
        event.stopPropagation();
        event.currentTarget.classList.remove('drag-over');

        // Get dropped thread ID
        const threadId = event.dataTransfer.getData('text/plain');
        if (!threadId) {
            console.warn('[SYNERGY] No thread ID in drop event');
            return;
        }

        console.log(`[SYNERGY] Thread ${threadId} dropped on synergy session ${synergySessionId}`);

        try {
            // Call backend to link thread to synergy session
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/${synergySessionId}/link-thread`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    thread_id: threadId
                })
            });

            const result = await response.json();

            if (result.success) {
                console.log(`✅ [SYNERGY] Thread ${threadId} linked to synergy session ${synergySessionId}`);

                // Show notification
                if (window.showNotification) {
                    window.showNotification('Thread linked to Synergy session', 'success');
                }

                // Refresh the linked threads section in the synergy card/sidebar
                await this.refreshLinkedThreads(synergySessionId);
            } else {
                console.error('[SYNERGY] Failed to link thread:', result.error);
                if (window.showNotification) {
                    window.showNotification('Failed to link thread: ' + result.error, 'error');
                }
            }
        } catch (error) {
            console.error('[SYNERGY] Error linking thread:', error);
            if (window.showNotification) {
                window.showNotification('Error linking thread', 'error');
            }
        }
    },

    async refreshLinkedThreads(sessionId) {
        console.log(`[SYNERGY] Refreshing linked threads for session ${sessionId}`);

        // If sidebar is open for this session, refresh it
        if (typeof SynergySidebar !== 'undefined') {
            await SynergySidebar.refreshLinkedThreadsSection(sessionId);
        }
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
