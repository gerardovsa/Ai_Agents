// ==================== THREAD MANAGER - SYNERGY MODULE ====================
/**
 * Synergy Integration
 * Handles all Synergy session linking, creation, and management
 */

window.ThreadManagerSynergy = {
    /**
     * Create a new Synergy session and link it to the thread in one action
     */
    async createAndLinkSynergy(threadId) {
        try {
            const thread = this.threads.find(t => t.id === threadId);
            const title = thread && thread.title ? `${thread.title} (linked)` : `Linked from thread ${threadId}`;

            // Create session
            const resp = await fetch(`${this.apiBaseUrl}/api/synergy/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title,
                    description: `Auto-created from thread ${threadId}`,
                    created_by: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 'user'
                })
            });

            const data = await resp.json();
            if (!data || !data.success || !data.session_id) {
                console.error('[createAndLinkSynergy] Failed to create session', data);
                if (typeof showNotification === 'function') {
                    showNotification('Failed to create Synergy session', 'error');
                }
                return null;
            }

            const sessionId = data.session_id;

            // Link to thread via thread update endpoint
            const updateResp = await fetch(`${this.apiBaseUrl}/api/threads/${threadId}/update`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: thread.title, synergy_card_id: sessionId })
            });

            const updateData = await updateResp.json();
            if (updateData && updateData.success) {
                // Update local thread state
                if (thread) {
                    thread.synergy_card_id = sessionId;
                    thread.updated = new Date().toISOString();
                    thread.synergy_card_name = title;
                    thread.synergy_card_desc = `Auto-created from thread ${threadId}`;
                }

                // Preload the new session into cache
                try {
                    const sresp = await fetch(`${this.apiBaseUrl}/api/synergy?ids=${encodeURIComponent(sessionId)}`);
                    if (sresp.ok) {
                        const sdata = await sresp.json();
                        if (sdata && sdata.success && sdata.sessions && sdata.sessions[sessionId]) {
                            if (!window._synergySessionCache) window._synergySessionCache = {};
                            window._synergySessionCache[sessionId] = sdata.sessions[sessionId];

                            // Update thread with fetched metadata
                            if (thread) {
                                thread.synergy_card_name = sdata.sessions[sessionId].title;
                                thread.synergy_card_desc = sdata.sessions[sessionId].description;
                                thread.synergy_card_priority = sdata.sessions[sessionId].priority;
                            }
                        }
                    }
                } catch (e) {
                    console.warn('[createAndLinkSynergy] Failed to preload new session', e);
                }

                // Refresh ALL thread info displays
                if (typeof this.renderThreadList === 'function') {
                    this.renderThreadList();
                }
                if (typeof this.refreshAllThreadInfoCards === 'function') {
                    this.refreshAllThreadInfoCards(threadId);
                }

                if (typeof showNotification === 'function') {
                    showNotification('Synergy session created and linked', 'success');
                }
                return sessionId;
            } else {
                console.error('[createAndLinkSynergy] Failed to link session to thread', updateData);
                if (typeof showNotification === 'function') {
                    showNotification('Failed to link Synergy session', 'error');
                }
                return null;
            }
        } catch (err) {
            console.error('[createAndLinkSynergy] Exception:', err);
            if (typeof showNotification === 'function') {
                showNotification('Error creating/linking Synergy session', 'error');
            }
            return null;
        }
    },

    /**
     * Unlink a synergy session from a thread
     */
    async unlinkSynergy(threadId, sessionId) {
        try {
            const resp = await fetch(`${this.apiBaseUrl}/api/threads/${threadId}/update`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: this.threads.find(t => t.id === threadId)?.title || '',
                    synergy_card_id: null
                })
            });

            const data = await resp.json();
            if (data && data.success) {
                const thread = this.threads.find(t => t.id === threadId);
                if (thread) {
                    thread.synergy_card_id = null;
                    thread.synergy_card_name = null;
                    thread.updated = new Date().toISOString();
                }

                // Use master sync to update all UI components (preserves workflow pill)
                if (typeof this.syncThreadLocationEverywhere === 'function') {
                    await this.syncThreadLocationEverywhere(threadId, thread.agent || 'main', {
                        removeLinks: ['synergy'],
                        preserveLinks: true
                    });
                }

                if (typeof showNotification === 'function') {
                    showNotification('Synergy session unlinked', 'success');
                }
                return true;
            } else {
                console.error('[unlinkSynergy] Failed:', data);
                if (typeof showNotification === 'function') {
                    showNotification('Failed to unlink Synergy session', 'error');
                }
                return false;
            }
        } catch (err) {
            console.error('[unlinkSynergy] Exception:', err);
            if (typeof showNotification === 'function') {
                showNotification('Error unlinking Synergy session', 'error');
            }
            return false;
        }
    },

    /**
     * Open Synergy Sync Modal with three options
     */
    async openSynergySyncModal(threadId) {
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            if (typeof showNotification === 'function') {
                showNotification('Thread not found', 'error');
            }
            return;
        }

        // Fetch all Synergy sessions
        let synergySessions = [];
        try {
            let resp = await fetch(`${this.apiBaseUrl}/api/synergy/list`);
            if (!resp.ok) {
                resp = await fetch(`${this.apiBaseUrl}/api/synergy`);
            }

            const data = await resp.json();
            console.log('[openSynergySyncModal] Fetched sessions:', data);

            // Handle multiple response formats
            if (Array.isArray(data)) {
                synergySessions = data;
            } else if (data && data.success && Array.isArray(data.sessions)) {
                synergySessions = data.sessions;
            } else if (data && Array.isArray(data.sessions)) {
                synergySessions = data.sessions;
            }

            console.log('[openSynergySyncModal] Parsed sessions:', synergySessions.length, 'sessions');
        } catch (err) {
            console.error('[openSynergySyncModal] Failed to fetch sessions:', err);
        }

        const modalHTML = `
            <div class="modal-overlay" id="synergySyncModalOverlay" onclick="if(event.target.id === 'synergySyncModalOverlay') document.getElementById('synergySyncModalOverlay').remove()">
                <div class="synergy-sync-modal" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h3><i class="fas fa-link"></i> Link to Synergy Session</h3>
                        <button class="modal-close" onclick="document.getElementById('synergySyncModalOverlay').remove()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <div class="modal-body">
                        <!-- Thread Info -->
                        <div class="synergy-sync-thread-info">
                            <strong>Thread:</strong> ${thread.title || 'Untitled'}
                        </div>

                        <!-- Tab Navigation -->
                        <div class="synergy-sync-tabs">
                            <button class="synergy-sync-tab active" data-tab="link" onclick="ThreadManager.switchSynergySyncTab('link')">
                                <i class="fas fa-link"></i> Link to Existing
                            </button>
                            <button class="synergy-sync-tab" data-tab="quick" onclick="ThreadManager.switchSynergySyncTab('quick')">
                                <i class="fas fa-bolt"></i> Quick Create
                            </button>
                            <button class="synergy-sync-tab" data-tab="full" onclick="ThreadManager.switchSynergySyncTab('full')">
                                <i class="fas fa-plus-circle"></i> Full Create
                            </button>
                        </div>

                        <!-- Tab Content: Link to Existing -->
                        <div class="synergy-sync-tab-content active" data-tab-content="link">
                            ${synergySessions.length === 0 ? `
                                <div class="synergy-sync-empty">
                                    <i class="fas fa-inbox"></i>
                                    <p>No Synergy sessions available</p>
                                    <p style="font-size: 12px; color: var(--text-muted);">Create one using Quick Create or Full Create tabs</p>
                                </div>
                            ` : `
                                <!-- Search and Sort -->
                                <div class="synergy-sync-controls">
                                    <div class="synergy-sync-search">
                                        <i class="fas fa-search"></i>
                                        <input type="text" id="synergySyncSearch" placeholder="Search sessions...">
                                    </div>
                                    <select id="synergySyncSort" onchange="ThreadManager.filterSynergySessions()">
                                        <option value="recent">Recent</option>
                                        <option value="priority">Priority</option>
                                        <option value="title">Title</option>
                                        <option value="status">Status</option>
                                    </select>
                                </div>

                                <!-- Session List -->
                                <div class="synergy-sync-list" id="synergySyncList">
                                    ${this.renderSynergySessionList(synergySessions)}
                                </div>
                            `}
                        </div>

                        <!-- Tab Content: Quick Create -->
                        <div class="synergy-sync-tab-content" data-tab-content="quick">
                            <div class="synergy-quick-create">
                                <div class="form-group">
                                    <label for="synergyQuickTitle">Session Title <span style="color: var(--accent-error);">*</span></label>
                                    <input type="text" id="synergyQuickTitle" placeholder="Enter session title..." value="${thread.title || ''}" autofocus>
                                </div>
                                <div class="form-group">
                                    <label for="synergyQuickDesc">Description <span style="color: var(--text-muted); font-weight: normal;">(optional)</span></label>
                                    <textarea id="synergyQuickDesc" placeholder="Brief description..." rows="3"></textarea>
                                </div>
                                <button class="btn-primary" onclick="ThreadManager.quickCreateAndLink('${threadId}')">
                                    <i class="fas fa-bolt"></i> Create & Link
                                </button>
                            </div>
                        </div>

                        <!-- Tab Content: Full Create -->
                        <div class="synergy-sync-tab-content" data-tab-content="full">
                            <div class="synergy-full-create">
                                <p style="margin-bottom: 16px; color: var(--text-secondary);">
                                    <i class="fas fa-info-circle"></i> Opens the full Synergy session creation interface with all options.
                                </p>
                                <button class="btn-primary" onclick="ThreadManager.fullCreateAndLink('${threadId}')">
                                    <i class="fas fa-plus-circle"></i> Open Full Creator
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Add search listener
        const searchInput = document.getElementById('synergySyncSearch');
        if (searchInput) {
            searchInput.addEventListener('input', () => this.filterSynergySessions());
        }

        // Store thread ID for later use
        window._synergySyncThreadId = threadId;
        window._synergySessions = synergySessions;
    },

    /**
     * Render session list for linking
     */
    renderSynergySessionList(sessions) {
        if (!sessions || sessions.length === 0) {
            return '<div class="synergy-sync-empty"><i class="fas fa-inbox"></i><p>No sessions found</p></div>';
        }

        return sessions.map(session => {
            const priority = session.priority || 'medium';
            const status = session.status || 'active';
            const title = session.title || 'Untitled';
            const desc = session.description || 'No description';
            const tags = Array.isArray(session.tags) ? session.tags :
                (typeof session.tags === 'string' ? JSON.parse(session.tags || '[]') : []);
            const lastActive = session.last_active ? new Date(session.last_active).toLocaleDateString() : 'Never';

            return `
                <div class="synergy-session-item" 
                     data-session-id="${session.session_id}" 
                     data-title="${title.toLowerCase()}" 
                     data-tags="${tags.join(',').toLowerCase()}"
                     data-priority="${priority}"
                     data-status="${status}"
                     onclick="ThreadManager.linkToExistingSession('${session.session_id}')">
                    <div class="synergy-session-header">
                        <span class="synergy-session-title">${title}</span>
                        <span class="synergy-session-priority priority-${priority}">${priority}</span>
                    </div>
                    <div class="synergy-session-desc">${desc}</div>
                    <div class="synergy-session-meta">
                        <span><i class="fas fa-circle" style="color: ${status === 'active' ? 'var(--accent-success)' : 'var(--text-muted)'}; font-size: 8px;"></i> ${status}</span>
                        <span><i class="fas fa-clock"></i> ${lastActive}</span>
                        ${tags.length > 0 ? `<span><i class="fas fa-tags"></i> ${tags.slice(0, 2).join(', ')}${tags.length > 2 ? '...' : ''}</span>` : ''}
                    </div>
                </div>
            `;
        }).join('');
    },

    /**
     * Switch tabs in modal
     */
    switchSynergySyncTab(tabName) {
        document.querySelectorAll('.synergy-sync-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        document.querySelectorAll('.synergy-sync-tab-content').forEach(content => {
            content.classList.toggle('active', content.dataset.tabContent === tabName);
        });
    },

    /**
     * Filter sessions based on search and sort
     */
    filterSynergySessions() {
        const searchTerm = document.getElementById('synergySyncSearch')?.value?.toLowerCase() || '';
        const sortBy = document.getElementById('synergySyncSort')?.value || 'recent';
        const sessionItems = document.querySelectorAll('.synergy-session-item');

        // Filter
        sessionItems.forEach(item => {
            const title = item.dataset.title || '';
            const tags = item.dataset.tags || '';
            const matches = title.includes(searchTerm) || tags.includes(searchTerm);
            item.style.display = matches ? 'block' : 'none';
        });

        // Sort visible items
        const visibleItems = Array.from(sessionItems).filter(item => item.style.display !== 'none');
        const container = document.getElementById('synergySyncList');

        if (sortBy === 'title') {
            visibleItems.sort((a, b) => (a.dataset.title || '').localeCompare(b.dataset.title || ''));
        } else if (sortBy === 'priority') {
            const priorityOrder = { high: 0, medium: 1, low: 2 };
            visibleItems.sort((a, b) => priorityOrder[a.dataset.priority] - priorityOrder[b.dataset.priority]);
        } else if (sortBy === 'status') {
            visibleItems.sort((a, b) => (a.dataset.status || '').localeCompare(b.dataset.status || ''));
        }

        // Re-append in sorted order
        visibleItems.forEach(item => container.appendChild(item));
    },

    /**
     * Link to existing session
     */
    async linkToExistingSession(sessionId) {
        const threadId = window._synergySyncThreadId;
        if (!threadId) {
            if (typeof showNotification === 'function') {
                showNotification('Thread ID not found', 'error');
            }
            return;
        }

        try {
            const thread = this.threads.find(t => t.id === threadId);
            const resp = await fetch(`${this.apiBaseUrl}/api/threads/${threadId}/update`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: thread?.title || '', synergy_card_id: sessionId })
            });

            const data = await resp.json();

            if (data && data.success) {
                // Update local thread state
                if (thread) {
                    thread.synergy_card_id = sessionId;
                    thread.updated = new Date().toISOString();
                }

                // Preload session into cache
                try {
                    const sresp = await fetch(`${this.apiBaseUrl}/api/synergy?ids=${encodeURIComponent(sessionId)}`);
                    if (sresp.ok) {
                        const sdata = await sresp.json();
                        if (sdata && sdata.success && sdata.sessions && sdata.sessions[sessionId]) {
                            if (!window._synergySessionCache) window._synergySessionCache = {};
                            window._synergySessionCache[sessionId] = sdata.sessions[sessionId];

                            // Update thread with synergy metadata
                            if (thread) {
                                thread.synergy_card_name = sdata.sessions[sessionId].title;
                                thread.synergy_card_desc = sdata.sessions[sessionId].description;
                                thread.synergy_card_priority = sdata.sessions[sessionId].priority;
                            }
                        }
                    }
                } catch (e) {
                    console.warn('[linkToExistingSession] Failed to preload session', e);
                }

                // Refresh ALL thread info displays
                if (typeof this.renderThreadList === 'function') {
                    this.renderThreadList();
                }
                if (typeof this.refreshAllThreadInfoCards === 'function') {
                    this.refreshAllThreadInfoCards(threadId);
                }

                document.getElementById('synergySyncModalOverlay')?.remove();

                if (typeof showNotification === 'function') {
                    showNotification('Linked to Synergy session', 'success');
                }
            } else {
                if (typeof showNotification === 'function') {
                    showNotification('Failed to link session', 'error');
                }
            }
        } catch (err) {
            console.error('[linkToExistingSession] Exception:', err);
            if (typeof showNotification === 'function') {
                showNotification('Error linking session', 'error');
            }
        }
    },

    /**
     * Quick create and link
     */
    async quickCreateAndLink(threadId) {
        const title = document.getElementById('synergyQuickTitle')?.value?.trim();
        const description = document.getElementById('synergyQuickDesc')?.value?.trim();

        if (!title) {
            if (typeof showNotification === 'function') {
                showNotification('Please enter a session title', 'error');
            }
            return;
        }

        try {
            // Create session
            const resp = await fetch(`${this.apiBaseUrl}/api/synergy/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title,
                    description: description || `Linked from thread: ${this.threads.find(t => t.id === threadId)?.title || threadId}`,
                    created_by: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 'user'
                })
            });

            const data = await resp.json();

            if (!data || !data.success || !data.session_id) {
                if (typeof showNotification === 'function') {
                    showNotification('Failed to create Synergy session', 'error');
                }
                return;
            }

            const sessionId = data.session_id;

            // Link to thread
            const thread = this.threads.find(t => t.id === threadId);
            const updateResp = await fetch(`${this.apiBaseUrl}/api/threads/${threadId}/update`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: thread?.title || '', synergy_card_id: sessionId })
            });

            const updateData = await updateResp.json();

            if (updateData && updateData.success) {
                // Update local thread state
                if (thread) {
                    thread.synergy_card_id = sessionId;
                    thread.updated = new Date().toISOString();
                    thread.synergy_card_name = title;
                    thread.synergy_card_desc = description || `Linked from thread: ${thread.title || threadId}`;
                }

                // Preload session
                try {
                    const sresp = await fetch(`${this.apiBaseUrl}/api/synergy?ids=${encodeURIComponent(sessionId)}`);
                    if (sresp.ok) {
                        const sdata = await sresp.json();
                        if (sdata && sdata.success && sdata.sessions && sdata.sessions[sessionId]) {
                            if (!window._synergySessionCache) window._synergySessionCache = {};
                            window._synergySessionCache[sessionId] = sdata.sessions[sessionId];

                            if (thread) {
                                thread.synergy_card_name = sdata.sessions[sessionId].title;
                                thread.synergy_card_desc = sdata.sessions[sessionId].description;
                                thread.synergy_card_priority = sdata.sessions[sessionId].priority;
                            }
                        }
                    }
                } catch (e) {
                    console.warn('[quickCreateAndLink] Failed to preload session', e);
                }

                // Refresh ALL thread info displays
                if (typeof this.renderThreadList === 'function') {
                    this.renderThreadList();
                }
                if (typeof this.refreshAllThreadInfoCards === 'function') {
                    this.refreshAllThreadInfoCards(threadId);
                }

                document.getElementById('synergySyncModalOverlay')?.remove();

                if (typeof showNotification === 'function') {
                    showNotification('Session created and linked', 'success');
                }
            } else {
                if (typeof showNotification === 'function') {
                    showNotification('Session created but failed to link', 'error');
                }
            }
        } catch (err) {
            console.error('[quickCreateAndLink] Exception:', err);
            if (typeof showNotification === 'function') {
                showNotification('Error creating/linking session', 'error');
            }
        }
    },

    /**
     * Full create and link
     */
    async fullCreateAndLink(threadId) {
        // Close the Synergy Sync modal
        document.getElementById('synergySyncModalOverlay')?.remove();

        // Switch to Synergy tab
        if (typeof switchTab === 'function') {
            switchTab('synergy');
        }

        // Store thread ID for auto-linking after creation
        window._pendingLinkThreadId = threadId;

        // Wait for tab to load, then open the edit modal
        setTimeout(() => {
            const thread = this.threads.find(t => t.id === threadId);
            const newSession = {
                session_id: null,
                title: thread?.title || 'New Synergy Session',
                description: `Linked from thread: ${thread?.title || threadId}`,
                project_name: '',
                priority: 'medium',
                status: 'active',
                kanban_column: 'backlog',
                tags: [],
                assignees: [],
                documents: [],
                links: [],
                next_steps: [],
                checklist: [],
                thread_ids: [threadId],
                assigned_agents: [],
                notes: '',
                due_date: null
            };

            // Open the edit modal
            if (typeof synergyBoard !== 'undefined' && synergyBoard.openEditModal) {
                synergyBoard.openEditModal(newSession);
                if (typeof showNotification === 'function') {
                    showNotification('Create your Synergy session', 'info');
                }
            } else {
                if (typeof showNotification === 'function') {
                    showNotification('Synergy board not loaded yet. Please try again.', 'error');
                }
            }
        }, 500);
    },

    /**
     * Copy Synergy info to clipboard
     */
    copySynergyInfo(synergyId, synergyName) {
        const text = `Session ID: ${synergyId}\nName: ${synergyName}`;
        navigator.clipboard.writeText(text).then(() => {
            console.log('Synergy info copied:', synergyId, synergyName);
            if (typeof showNotification === 'function') {
                showNotification('Synergy session info copied!', 'success', 2000);
            }
        }).catch(err => {
            console.error('Failed to copy Synergy info:', err);
            if (typeof showNotification === 'function') {
                showNotification('Failed to copy Synergy info', 'error', 2000);
            }
        });
    }
};

// Merge into main ThreadManager object
Object.assign(window.ThreadManager, window.ThreadManagerSynergy);

console.log('✅ ThreadManager-Synergy module loaded and merged');