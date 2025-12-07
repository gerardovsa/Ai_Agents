
        // ==================== SYNERGY SIDEBAR ====================
        // ALL SYNERGY JAVASCRIPT MOVED TO: UI/external/modules/synergy/ (Nov 2025)
        // - synergy-sidebar-controller.js (main controller)
        // - synergy-sidebar-renderer.js (rendering logic)
        // - synergy-card-renderer.js (card rendering)
        // - synergy-milestone-renderer.js (milestone UI)
        // - synergy-milestone-interactions.js (interactions)
        // The controller is exposed as window.SynergySidebar singleton

        // ========== SYNERGY BOARD (Main Dashboard) ==========
        // MOVED TO: Line 38707 (complete implementation with all methods)
        // This stub was causing "initializeLinkInterception is not a function" error
        // The real synergyBoard is declared in <script> section after styles

        /*
        const synergyBoard = {
            async toggleTileEdit(sessionId) {
                try {
                    console.log('[SYNERGY SIDEBAR] Lazy loading sessions with batch endpoint...');
                    const startTime = performance.now();

                    // Use batch endpoint for optimized loading
                    const response = await fetch(`${API_BASE_URL}/api/synergy/sessions/batch`);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const result = await response.json();
                    if (result.success) {
                        this.sessions = result.sessions || [];
                        this.sessionsLoaded = true;
                        const endTime = performance.now();
                        const loadTime = (endTime - startTime).toFixed(0);
                        console.log(`? [SYNERGY SIDEBAR] Batch loaded ${this.sessions.length} sessions in ${loadTime}ms`);
                    } else {
                        throw new Error(result.error || 'Batch load failed');
                    }

                    // Load pinned sessions from localStorage
                    const stored = localStorage.getItem('synergy_pinned');
                    if (stored) {
                        this.pinnedSessions = new Set(JSON.parse(stored));
                    }

                    this.renderSessions();
                } catch (error) {
                    console.error('? [SYNERGY SIDEBAR] Failed to load sessions:', error);
                    showNotification('Failed to load Synergy sessions', 'error');
                }
            },

            renderSessions() {
                const listView = document.getElementById('synergy-list-view');
                const pinnedView = document.getElementById('synergy-pinned-view');

                // Clear both views
                listView.innerHTML = '';
                pinnedView.innerHTML = '';

                // Filter sessions
                let filtered = this.getFilteredSessions(this.sessions);

                // Render to appropriate view
                if (this.currentView === 'list') {
                    filtered.forEach(session => {
                        listView.appendChild(this.createSessionItem(session));
                    });
                } else {
                    // Pinned view - only show pinned sessions
                    const pinned = filtered.filter(s => this.pinnedSessions.has(s.session_id));
                    if (pinned.length === 0) {
                        pinnedView.innerHTML = `
                            <div style="text-align: center; padding: 40px 20px; color: var(--text-muted);">
                                <i class="fas fa-thumbtack" style="font-size: 48px; opacity: 0.3; margin-bottom: 16px;"></i>
                                <p>No pinned sessions yet</p>
                                <p style="font-size: 12px;">Pin sessions from list view to access them here</p>
                            </div>
                        `;
                    } else {
                        pinned.forEach(session => {
                            pinnedView.appendChild(this.createSessionItem(session, true));
                        });
                    }
                }
            },

            filterSessions(sessions) {
                return sessions.filter(session => {
                    // Category filter
                    if (this.currentFilter !== 'all' && session.kanban_column !== this.currentFilter) {
                        return false;
                    }

                    // Search filter
                    if (this.searchQuery) {
                        const query = this.searchQuery.toLowerCase();
                        const title = (session.title || '').toLowerCase();
                        const description = (session.description || '').toLowerCase();
                        if (!title.includes(query) && !description.includes(query)) {
                            return false;
                        }
                    }

                    return true;
                });
            },

            createSessionItem(session, showCollapsed = false) {
                // Use external renderer module
                if (!this.renderer) {
                    this.init(); // Initialize if not already done
                }

                if (!this.renderer) {
                    console.error('[SYNERGY SIDEBAR] Renderer not available');
                    const item = document.createElement('div');
                    item.innerHTML = '<div style="padding: 16px; color: #dc2626;">Error: Renderer module not loaded</div>';
                    return item;
                }

                // Delegate to external renderer
                const item = this.renderer.createSessionItem(session, this.expandedSessions, this.pinnedSessions);

                // Add event listeners for interactive elements
                this.attachEventListeners(item, session.session_id);

                return item;
            },

            attachEventListeners(itemElement, sessionId) {
                // Header click to expand/collapse
                const header = itemElement.querySelector('.synergy-card-header');
                if (header) {
                    header.addEventListener('click', (e) => {
                        // Ignore clicks on buttons
                        if (e.target.closest('.synergy-pin-btn') || e.target.closest('.synergy-open-btn') || e.target.closest('.synergy-edit-btn')) {
                            return;
                        }
                        this.toggleSessionExpand(sessionId);
                    });
                }

                // Edit button - toggle inline edit mode
                const editBtn = itemElement.querySelector('.synergy-edit-btn');
                if (editBtn) {
                    editBtn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        this.toggleEditMode(itemElement, sessionId);
                    });
                }

                // Pin button
                const pinBtn = itemElement.querySelector('.synergy-pin-btn');
                if (pinBtn) {
                    pinBtn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        this.togglePin(sessionId);
                    });
                }

                // Open button
                const openBtn = itemElement.querySelector('.synergy-open-btn');
                if (openBtn) {
                    openBtn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        this.openInPopup(sessionId);
                    });
                }

                // Milestone checkboxes
                const milestoneCheckboxes = itemElement.querySelectorAll('.milestone-checkbox');
                milestoneCheckboxes.forEach(checkbox => {
                    checkbox.addEventListener('change', async (e) => {
                        const milestoneId = e.target.dataset.milestoneId;
                        await this.toggleMilestone(sessionId, milestoneId);
                    });
                });

                // Task checkboxes
                const taskCheckboxes = itemElement.querySelectorAll('.task-checkbox');
                taskCheckboxes.forEach(checkbox => {
                    checkbox.addEventListener('change', async (e) => {
                        const taskId = e.target.dataset.taskId;
                        await this.toggleTask(sessionId, taskId);
                    });
                });

                // Subtask checkboxes
                const subtaskCheckboxes = itemElement.querySelectorAll('.subtask-checkbox');
                subtaskCheckboxes.forEach(checkbox => {
                    checkbox.addEventListener('change', async (e) => {
                        const subtaskId = e.target.dataset.subtaskId;
                        await this.toggleSubtask(sessionId, subtaskId);
                    });
                });
            },

            toggleSessionExpand(sessionId) {
                if (this.expandedSessions.has(sessionId)) {
                    this.expandedSessions.delete(sessionId);
                } else {
                    this.expandedSessions.add(sessionId);
                }
                this.renderSessions();
            },

            parseJsonField(field, fallback = []) {
                if (!field) return fallback;
                if (typeof field === 'string') {
                    try {
                        return JSON.parse(field);
                    } catch (e) {
                        return fallback;
                    }
                }
                if (Array.isArray(field)) return field;
                return fallback;
            },

            escapeHtml(text) {
                if (!text) return '';
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            },

            // === TOGGLE FUNCTIONS FOR MILESTONES/TASKS/SUBTASKS ===

            async toggleMilestone(sessionId, milestoneId) {
                try {
                    const response = await fetch(`${window.API_BASE_URL}/api/synergy/${sessionId}/milestones/${milestoneId}/toggle`, {
                        method: 'POST'
                    });
                    if (response.ok) {
                        // Refresh the card (context-aware for sidebar)
                        const item = document.querySelector(`[data-context="sidebar"] [data-session-id="${sessionId}"]`);
                        if (item && this.renderer) {
                            await this.renderer.loadAndRenderFullCard(sessionId, item);
                            this.attachEventListeners(item, sessionId);
                        }
                    }
                } catch (error) {
                    console.error('[SYNERGY SIDEBAR] Error toggling milestone:', error);
                }
            },

            async toggleTask(sessionId, taskId) {
                try {
                    const response = await fetch(`${window.API_BASE_URL}/api/synergy/${sessionId}/tasks/${taskId}/toggle`, {
                        method: 'POST'
                    });
                    if (response.ok) {
                        const item = document.querySelector(`[data-context="sidebar"] [data-session-id="${sessionId}"]`);
                        if (item && this.renderer) {
                            await this.renderer.loadAndRenderFullCard(sessionId, item);
                            this.attachEventListeners(item, sessionId);
                        }
                    }
                } catch (error) {
                    console.error('[SYNERGY SIDEBAR] Error toggling task:', error);
                }
            },

            async toggleSubtask(sessionId, subtaskId) {
                try {
                    const response = await fetch(`${window.API_BASE_URL}/api/synergy/${sessionId}/subtasks/${subtaskId}/toggle`, {
                        method: 'POST'
                    });
                    if (response.ok) {
                        const item = document.querySelector(`[data-context="sidebar"] [data-session-id="${sessionId}"]`);
                        if (item && this.renderer) {
                            await this.renderer.loadAndRenderFullCard(sessionId, item);
                            this.attachEventListeners(item, sessionId);
                        }
                    }
                } catch (error) {
                    console.error('[SYNERGY SIDEBAR] Error toggling subtask:', error);
                }
            },

            togglePin(sessionId) {
                if (this.pinnedSessions.has(sessionId)) {
                    this.pinnedSessions.delete(sessionId);
                } else {
                    this.pinnedSessions.add(sessionId);
                }

                // Save to localStorage
                localStorage.setItem('synergy_pinned', JSON.stringify([...this.pinnedSessions]));

                // Update UI
                this.renderSessions();
                showNotification(this.pinnedSessions.has(sessionId) ? 'Session pinned' : 'Session unpinned', 'success');
            },

            // === INLINE EDIT MODE FUNCTIONS ===

            toggleEditMode(itemElement, sessionId) {
                const toolbar = itemElement.querySelector('.synergy-edit-toolbar');
                const editBtn = itemElement.querySelector('.synergy-edit-btn');

                if (!toolbar) {
                    console.error('[SYNERGY] Edit toolbar not found');
                    return;
                }

                const isEditing = toolbar.style.display === 'flex';

                if (isEditing) {
                    // Exit edit mode
                    this.exitEditMode(itemElement);
                } else {
                    // Enter edit mode
                    this.enterEditMode(itemElement, sessionId);
                }
            },

            enterEditMode(itemElement, sessionId) {
                const toolbar = itemElement.querySelector('.synergy-edit-toolbar');
                const editBtn = itemElement.querySelector('.synergy-edit-btn');

                // Show toolbar
                toolbar.style.display = 'flex';

                // Highlight edit button
                editBtn.style.color = 'var(--accent-primary)';
                editBtn.style.opacity = '1';

                // Show all input fields, hide displays
                const metadataInputs = itemElement.querySelectorAll('.metadata-input');
                const metadataDisplays = itemElement.querySelectorAll('.metadata-display');
                const descriptionInput = itemElement.querySelector('.description-input');
                const descriptionDisplay = itemElement.querySelector('.description-display');

                metadataInputs.forEach(input => input.style.display = 'block');
                metadataDisplays.forEach(display => display.style.display = 'none');

                if (descriptionInput) descriptionInput.style.display = 'block';
                if (descriptionDisplay) descriptionDisplay.style.display = 'none';

                // Attach save/cancel handlers
                const saveBtn = toolbar.querySelector('.synergy-edit-save');
                const cancelBtn = toolbar.querySelector('.synergy-edit-cancel');

                if (saveBtn && !saveBtn.dataset.listenerAttached) {
                    saveBtn.addEventListener('click', () => this.saveEditMode(itemElement, sessionId));
                    saveBtn.dataset.listenerAttached = 'true';
                }

                if (cancelBtn && !cancelBtn.dataset.listenerAttached) {
                    cancelBtn.addEventListener('click', () => this.exitEditMode(itemElement));
                    cancelBtn.dataset.listenerAttached = 'true';
                }

                console.log('[SYNERGY] Entered edit mode for', sessionId);
            },

            exitEditMode(itemElement) {
                const toolbar = itemElement.querySelector('.synergy-edit-toolbar');
                const editBtn = itemElement.querySelector('.synergy-edit-btn');

                // Hide toolbar
                toolbar.style.display = 'none';

                // Reset edit button
                editBtn.style.color = 'var(--text-tertiary)';
                editBtn.style.opacity = '0.7';

                // Hide all input fields, show displays
                const metadataInputs = itemElement.querySelectorAll('.metadata-input');
                const metadataDisplays = itemElement.querySelectorAll('.metadata-display');
                const descriptionInput = itemElement.querySelector('.description-input');
                const descriptionDisplay = itemElement.querySelector('.description-display');

                metadataInputs.forEach(input => input.style.display = 'none');
                metadataDisplays.forEach(display => display.style.display = 'block');

                if (descriptionInput) descriptionInput.style.display = 'none';
                if (descriptionDisplay) descriptionDisplay.style.display = 'block';

                console.log('[SYNERGY] Exited edit mode');
            },

            async saveEditMode(itemElement, sessionId) {
                try {
                    // Collect edited values
                    const metadataSection = itemElement.querySelector('.synergy-metadata-section');
                    const descriptionSection = itemElement.querySelector('.synergy-description-section');

                    const updates = {};

                    // Get assignees
                    const assigneesInput = metadataSection?.querySelector('[data-field="assignees"] .metadata-input');
                    if (assigneesInput) {
                        const assigneeNames = assigneesInput.value.split(',').map(name => name.trim()).filter(n => n);
                        updates.assignees = JSON.stringify(assigneeNames.map(name => ({ name })));
                    }

                    // Get due date
                    const dueDateInput = metadataSection?.querySelector('[data-field="due_date"] .metadata-input');
                    if (dueDateInput && dueDateInput.value) {
                        updates.due_date = dueDateInput.value;
                    }

                    // Get description
                    const descriptionInput = descriptionSection?.querySelector('.description-input');
                    if (descriptionInput) {
                        updates.description = descriptionInput.value;
                    }

                    console.log('[SYNERGY] Saving updates:', updates);

                    // Send PATCH request to update session
                    const userId = window.currentUserId || window.UserAuth?.user?.id || 14;
                    const response = await fetch(`${window.API_BASE_URL}/api/synergy/${sessionId}?user_id=${userId}`, {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(updates)
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }

                    // Success - reload card and exit edit mode
                    showNotification('Session updated successfully', 'success');
                    this.exitEditMode(itemElement);

                    // Refresh the card
                    if (this.renderer) {
                        await this.renderer.loadAndRenderFullCard(sessionId, itemElement);
                        this.attachEventListeners(itemElement, sessionId);
                    }

                } catch (error) {
                    console.error('[SYNERGY] Error saving updates:', error);
                    showNotification('Failed to save changes: ' + error.message, 'error');
                }
            },

            switchView(view) {
                this.currentView = view;

                // Update tab UI
                document.querySelectorAll('.synergy-view-tab').forEach(tab => {
                    if (tab.dataset.view === view) {
                        tab.classList.add('active');
                    } else {
                        tab.classList.remove('active');
                    }
                });

                // Show/hide views
                const listView = document.getElementById('synergy-list-view');
                const pinnedView = document.getElementById('synergy-pinned-view');

                if (view === 'list') {
                    listView.style.display = 'block';
                    pinnedView.style.display = 'none';
                } else if (view === 'pinned') {
                    listView.style.display = 'none';
                    pinnedView.style.display = 'block';
                }

                this.renderSessions();
            },

            filterByCategory(category) {
                this.currentFilter = category;

                // Update chip UI
                document.querySelectorAll('.synergy-category-chip').forEach(chip => {
                    if (typeof a === 'string') return this.escapeHtml(a);
                    if (a && typeof a === 'object') return this.escapeHtml(a.name || a.id || 'Unknown');
                    return 'Unknown';
                }).filter(n => n && n !== 'Unknown').join(', ');

                // Parse due date properly
                let dueDateHTML = '';
                if (session.due_date) {
                    const dueDate = new Date(session.due_date);
                    if (dueDate.getFullYear() > 1970) {
                        const isOverdue = dueDate < new Date();
                        dueDateHTML = `
                            <span style="background: ${isOverdue ? '#dc2626' : 'var(--bg-quaternary)'}; color: ${isOverdue ? 'white' : 'var(--text-primary)'}; padding: 3px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;">
                                <i class="fas fa-calendar" style="font-size: 11px;"></i> Due: ${dueDate.toLocaleDateString()}
                            </span>
                        `;
                    }
                }

                let html = `
                    <div class="session-header" style="display: flex; justify-content: space-between; align-items: center; padding: 12px; cursor: pointer; border-bottom: 1px solid var(--border-secondary);">
                        <div style="flex: 1;">
                            <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">${session.title}</div>
                            <div style="font-size: 11px; color: var(--text-secondary);">
                                <span style="background: ${priorityColors[session.priority] || '#6b7280'}; color: white; padding: 2px 8px; border-radius: 10px; font-weight: 600;">${session.priority?.toUpperCase() || 'MEDIUM'}</span>
                                <span style="margin-left: 8px;">${session.status || 'active'}</span>
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px; align-items: center;">
                            <button class="pin-button" style="background: none; border: none; color: var(--text-secondary); cursor: pointer; font-size: 14px;">
                                <i class="fas fa-thumbtack"></i>
                            </button>
                            <button class="open-button" style="background: var(--accent-primary); color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px;">
                                Open
                            </button>
                        </div>
                    </div>

                    <div class="session-content" style="padding: 12px;">
                `;

                // Metadata section
                if (assigneeNames || dueDateHTML) {
                    html += `<div class="card-meta" style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; font-size: 12px;">`;
                    if (assigneeNames) {
                        html += `
                            <span style="background: var(--bg-quaternary); color: var(--text-primary); padding: 2px 10px; border-radius: 12px; font-size: 10px; font-weight: 500; display: inline-flex; align-items: center; gap: 4px;">
                                <i class="fas fa-users" style="font-size: 8px;"></i> ${assigneeNames}
                            </span>
                        `;
                    }
                    html += dueDateHTML;
                    html += `</div>`;
                }

                // Milestone placeholder (will be filled by loadAndRenderMilestones if expanded)
                html += `<div class="milestone-placeholder" style="color: var(--text-secondary); font-size: 12px; margin-bottom: 12px;">
                    <i class="fas fa-tasks"></i> Click to load milestones...
                </div>`;

                // Documents section
                if (documents.length > 0) {
                    html += `
                        <div style="margin-top: 12px;">
                            <div style="font-weight: 600; font-size: 12px; color: var(--text-primary); margin-bottom: 8px;">
                                <i class="fas fa-folder-open"></i> Project Documents (${documents.length})
                            </div>
                    `;
                    documents.forEach(doc => {
                        html += `<div style="font-size: 11px; color: var(--text-secondary); padding: 4px 0;">� ${doc.title || doc.name || 'Untitled'}</div>`;
                    });
                    html += `</div>`;
                }

                // Links section
                if (links.length > 0) {
                    html += `
                        <div style="margin-top: 12px;">
                            <div style="font-weight: 600; font-size: 12px; color: var(--text-primary); margin-bottom: 8px;">
                                <i class="fas fa-external-link-alt"></i> Project Links (${links.length})
                            </div>
                    `;
                    links.forEach(link => {
                        html += `<div style="font-size: 11px; color: var(--accent-primary); padding: 4px 0;">� <a href="${link.url}" target="_blank">${link.title || link.url}</a></div>`;
                    });
                    html += `</div>`;
                }

                // Tags section
                if (tags.length > 0) {
                    html += `<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px;">`;
                    tags.forEach(tag => {
                        html += `<span style="background: var(--bg-quaternary); color: var(--text-primary); padding: 4px 10px; border-radius: 12px; font-size: 11px;">#${tag}</span>`;
                    });
                    html += `</div>`;
                }

                html += `</div>`; // Close session-content

                return html;
            },

            async loadAndRenderMilestones(sessionId, itemElement) {
                try {
                    console.log(`[SYNERGY SIDEBAR] Loading milestones for: ${sessionId}`);
                    const placeholder = itemElement.querySelector('.milestone-placeholder');
                    if (!placeholder) {
                        console.error('[SYNERGY SIDEBAR] Milestone placeholder not found in DOM');
                        return;
                    }

                    placeholder.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';

                    const url = `${window.API_BASE_URL}/api/synergy/${sessionId}/milestones`;
                    console.log(`[SYNERGY SIDEBAR] Fetching: ${url}`);

                    const response = await fetch(url);
                    console.log(`[SYNERGY SIDEBAR] Response status: ${response.status}`);

                    if (!response.ok) {
                        const errorText = await response.text();
                        console.error(`[SYNERGY SIDEBAR] API error: ${response.status} - ${errorText}`);
                        throw new Error(`HTTP ${response.status}: ${errorText}`);
                    }

                    const data = await response.json();
                    const milestones = data.milestones || [];
                    console.log(`[SYNERGY SIDEBAR] Loaded ${milestones.length} milestones`);

                    if (milestones.length === 0) {
                        placeholder.innerHTML = '<div style="padding: 8px; background: var(--bg-quaternary); border-radius: 6px; color: var(--text-tertiary); font-size: 11px; text-align: center;">No milestones yet</div>';
                    } else {
                        const completedCount = milestones.filter(m => m.completed).length;
                        const milestonesHTML = milestones.map((m, idx) => {
                            const taskCount = m.tasks?.length || 0;
                            const completedTasks = m.tasks?.filter(t => t.completed).length || 0;
                            const progress = taskCount > 0 ? Math.round((completedTasks / taskCount) * 100) : 0;
                            return `
                                <div style="padding: 8px; border-left: 3px solid ${m.completed ? '#22c55e' : '#6b7280'}; margin-bottom: 8px; background: ${m.completed ? 'rgba(34, 197, 94, 0.1)' : 'transparent'};">
                                    <div style="font-size: 11px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">
                                        ${m.completed ? '?' : '?'} <strong>M${idx + 1}:</strong> ${this.escapeHtml(m.title)}
                                    </div>
                                    <div style="font-size: 10px; color: var(--text-secondary);">
                                        ${completedTasks}/${taskCount} tasks (${progress}%)
                                    </div>
                                </div>
                            `;
                        }).join('');

                        placeholder.innerHTML = `
                            <div style="background: var(--bg-quaternary); border-radius: 6px; padding: 10px; margin-bottom: 12px;">
                                <div style="font-weight: 600; font-size: 12px; color: var(--text-primary); margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
                                    <i class="fas fa-tasks" style="color: var(--accent-primary);"></i> 
                                    <span>Milestones: ${completedCount}/${milestones.length} completed</span>
                                </div>
                                ${milestonesHTML}
                            </div>
                        `;
                    }
                } catch (error) {
                    console.error('? [SYNERGY SIDEBAR] Failed to load milestones:', error);
                    const placeholder = itemElement.querySelector('.milestone-placeholder');
                    if (placeholder) {
                        placeholder.innerHTML = `
                            <div style="padding: 8px; background: rgba(220, 38, 38, 0.1); border-left: 3px solid #dc2626; border-radius: 4px; color: #dc2626; font-size: 11px;">
                                <strong>Failed to load milestones</strong><br>
                                <span style="font-size: 10px; opacity: 0.8;">${this.escapeHtml(error.message || 'Unknown error')}</span>
                            </div>
                        `;
                    }
                }
            },

            toggleSessionExpand(sessionId) {
                if (this.expandedSessions.has(sessionId)) {
                    this.expandedSessions.delete(sessionId);
                } else {
                    this.expandedSessions.add(sessionId);
                }
                this.renderSessions();
            },

            parseJsonField(field, fallback = []) {
                if (!field) return fallback;
                if (typeof field === 'string') {
                    try {
                        return JSON.parse(field);
                    } catch (e) {
                        return fallback;
                    }
                }
                if (Array.isArray(field)) return field;
                return fallback;
            },

            escapeHtml(text) {
                if (!text) return '';
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            },

            toggleExpand(event, sessionId) {
                // Don't toggle if clicking on interactive elements
                if (event.target.closest('.synergy-item-btn') ||
                    event.target.closest('.synergy-expand-btn') ||
                    event.target.tagName === 'INPUT' ||
                    event.target.tagName === 'A' ||
                    event.target.tagName === 'BUTTON' ||
                    event.target.closest('a') ||
                    event.target.closest('button') ||
                    event.target.closest('input')) {
                    return;
                }

                const item = document.querySelector(`[data-context="sidebar"] .synergy-session-item[data-session-id="${sessionId}"]`);
                if (!item) {
                    console.warn(`[SYNERGY SIDEBAR] Item not found: ${sessionId}`);
                    return;
                }

                // Toggle expanded state
                if (this.expandedSessions.has(sessionId)) {
                    this.expandedSessions.delete(sessionId);
                    item.classList.remove('expanded');
                    console.log(`[SYNERGY SIDEBAR] Collapsed: ${sessionId}`);
                } else {
                    this.expandedSessions.add(sessionId);
                    item.classList.add('expanded');
                    console.log(`[SYNERGY SIDEBAR] Expanded: ${sessionId}`);

                    // Scroll into view
                    setTimeout(() => {
                        item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 100);
                }
            },

            togglePin(sessionId) {

                // Calculate stats
                const completedSteps = nextSteps.filter(s => s && s.completed).length;
                const totalSteps = nextSteps.length;
                const completedChecklist = checklist.filter(c => c && c.completed).length;
                const totalChecklist = checklist.length;

                let html = '';

                // Card Meta (assignees and due date only - tags moved to bottom)
                if (assignees.length > 0 || session.due_date) {
                    html += `<div class="card-meta" style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; font-size: 12px;">`;

                    if (assignees.length > 0) {
                        html += `
                            <span style="background: var(--bg-quaternary); color: var(--text-primary); padding: 2px 10px; border-radius: 12px; font-size: 10px; font-weight: 500; display: inline-flex; align-items: center; gap: 4px;">
                                <i class="fas fa-users" style="font-size: 8px;"></i> ${assignees.join(', ')}
                            </span>
                        `;
                    }

                    if (session.due_date) {
                        const dueDate = new Date(session.due_date);
                        const isOverdue = dueDate < new Date();
                        html += `
                            <span style="background: ${isOverdue ? '#dc2626' : 'var(--bg-quaternary)'}; color: ${isOverdue ? 'white' : 'var(--text-primary)'}; padding: 3px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;">
                                <i class="fas fa-calendar" style="font-size: 11px;"></i> Due: ${dueDate.toLocaleDateString()}
                            </span>
                        `;
                    }

                    html += `</div>`;
                }

                // Card Stats
                html += `
                    <div class="card-stats" style="display: flex; gap: 16px; margin-bottom: 16px; padding: 12px; background: var(--bg-quaternary); border-radius: 6px; font-size: 12px;">
                        <span style="display: flex; align-items: center; gap: 6px;">
                            <i class="fas fa-comments" style="color: var(--accent-primary);"></i> 
                            <span>${session.message_count || 0}</span>
                        </span>
                        <span style="display: flex; align-items: center; gap: 6px;">
                            <i class="fas fa-file" style="color: var(--accent-primary);"></i> 
                            <span>${documents.length}</span>
                        </span>
                        <span style="display: flex; align-items: center; gap: 6px;">
                            <i class="fas fa-tasks" style="color: var(--accent-primary);"></i> 
                            <span>${completedSteps}/${totalSteps}</span>
                        </span>
                        <span style="display: flex; align-items: center; gap: 6px;">
                            <i class="fas fa-check-square" style="color: var(--accent-primary);"></i> 
                            <span>${completedChecklist}/${totalChecklist}</span>
                        </span>
                    </div>
                `;

                // Description - FULL, no truncation
                if (session.description) {
                    const descriptionHtml = typeof marked !== 'undefined'
                        ? marked.parse(session.description)
                        : this.escapeHtml(session.description).replace(/\n/g, '<br>');

                    html += `
                        <div class="synergy-card-section" style="margin-bottom: 16px;">
                            <div class="synergy-card-section-title" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                                <i class="fas fa-align-left"></i>
                                Description
                            </div>
                            <div class="synergy-card-description" style="font-size: 13px; line-height: 1.6; color: var(--text-primary);">${descriptionHtml}</div>
                        </div>
                    `;
                }

                // Documents - ALWAYS SHOW (even if empty)
                html += `
                    <div class="synergy-card-section" style="margin-bottom: 16px;">
                        <div class="synergy-card-section-title" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                            <i class="fas fa-folder-open"></i>
                            Project Documents ${documents.length > 0 ? `(${documents.length})` : ''}
                        </div>
                        <div style="font-size: 13px;">
                            ${documents.length > 0 ? documents.map((doc, idx) => {
                    const displayNumber = idx + 1;
                    if (doc.type === 'internal_doc') {
                        return `
                                        <div style="display: flex; align-items: center; gap: 8px; padding: 8px; margin-bottom: 4px; background: var(--bg-quaternary); border-radius: 4px; cursor: pointer;"
                                            onclick="event.stopPropagation(); window.internalDocsManager.openInternalDocPopup('${doc.doc_id}', '${session.session_id}');">                                            <span style="display: inline-flex; align-items: center; justify-content: center; min-width: 28px; height: 22px; background: linear-gradient(135deg, #58a6ff 0%, #4a8fe7 100%); color: white; font-weight: 700; border-radius: 4px; font-size: 10px; padding: 0 6px; white-space: nowrap;">D${displayNumber}</span>
                                            <i class="fas fa-${doc.doc_type === 'spreadsheet' ? 'table' : 'file-alt'}" style="color: var(--accent-primary);"></i>
                                            <span style="flex: 1;">${this.escapeHtml(doc.title)}</span>
                                            <span style="font-size: 11px; color: var(--text-muted);">${doc.doc_type === 'spreadsheet' ? 'Spreadsheet' : 'Document'} v${doc.version || 1}</span>
                                        </div>
                                    `;
                    } else {
                        return `
                                        <div style="display: flex; align-items: center; gap: 8px; padding: 8px; margin-bottom: 4px; background: var(--bg-quaternary); border-radius: 4px;">                                            <span style="display: inline-flex; align-items: center; justify-content: center; min-width: 28px; height: 22px; background: linear-gradient(135deg, #58a6ff 0%, #4a8fe7 100%); color: white; font-weight: 700; border-radius: 4px; font-size: 10px; padding: 0 6px;">D${displayNumber}</span>
                                            <i class="fas fa-file" style="color: var(--accent-primary);"></i>
                                            <span style="flex: 1;">${this.escapeHtml(doc.title || doc.name)}</span>
                                            ${doc.url ? `<a href="${this.escapeHtml(doc.url)}" target="_blank" style="color: var(--accent-primary); text-decoration: none;"
                                                onclick="event.stopPropagation();">
                                                <i class="fas fa-external-link-alt"></i>
                                            </a>` : ''}
                                        </div>
                                    `;
                    }
                }).join('') : '<div style="opacity: 0.6; font-style: italic; padding: 8px;">No documents added</div>'}
                        </div>
                    </div>
                `;

                // Links - ALWAYS SHOW (even if empty)
                html += `
                    <div class="synergy-card-section" style="margin-bottom: 16px;">
                        <div class="synergy-card-section-title" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                            <i class="fas fa-external-link-alt"></i>
                            Project Links ${links.length > 0 ? `(${links.length})` : ''}
                        </div>
                        <div style="font-size: 13px;">
                            ${links.length > 0 ? links.map((link, idx) => {
                    const displayNumber = idx + 1;
                    return `
                                <div style="display: flex; align-items: center; gap: 8px; padding: 8px; margin-bottom: 4px; background: var(--bg-quaternary); border-radius: 4px;">                                    <span style="display: inline-flex; align-items: center; justify-content: center; min-width: 28px; height: 22px; background: linear-gradient(135deg, #58a6ff 0%, #4a8fe7 100%); color: white; font-weight: 700; border-radius: 4px; font-size: 10px; padding: 0 6px;">L${displayNumber}</span>
                                    <i class="fas fa-external-link-alt" style="color: var(--accent-primary);"></i>
                                    <a href="${this.escapeHtml(link.url)}" target="_blank" 
                                        style="flex: 1; color: var(--accent-primary); text-decoration: none;"
                                        onclick="event.stopPropagation();">
                                        ${this.escapeHtml(link.title)}
                                    </a>
                                    <span style="font-size: 11px; color: var(--text-muted);">${link.type || 'external'}</span>
                                </div>
                            `;
                }).join('') : '<div style="opacity: 0.6; font-style: italic; padding: 8px;">No links added</div>'}
                        </div>
                    </div>
                `;

                // Milestones - ALWAYS SHOW (even if empty) - Tiered structure
                const milestones = this.parseJsonField(session.milestones, []);
                const completedMilestones = milestones.filter(m => m && m.completed).length;
                const totalMilestones = milestones.length;
                
                html += `
                    <div class="synergy-card-section" style="margin-bottom: 16px;">
                        <div class="synergy-card-section-title" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                            <i class="fas fa-flag-checkered"></i>
                            Milestones ${milestones.length > 0 ? `(${completedMilestones}/${totalMilestones})` : ''}
                        </div>
                        <div style="font-size: 13px;">
                            ${milestones.length > 0 ? milestones.map((milestone, idx) => {
                    const displayNumber = idx + 1;
                    const milestoneTitle = milestone.title || milestone.name || 'Untitled Milestone';
                    const milestoneDesc = milestone.description || '';
                    const tasks = milestone.tasks || [];
                    const completedTasks = tasks.filter(t => t.completed).length;
                    const tier = milestone.tier || 1; // Tier 1, 2, or 3
                    
                    // Tier colors
                    const tierColors = {
                        1: { bg: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)', text: 'Critical' },
                        2: { bg: 'linear-gradient(135deg, #ffd93d 0%, #f6c700 100%)', text: 'Important' },
                        3: { bg: 'linear-gradient(135deg, #6bcf7f 0%, #51b368 100%)', text: 'Standard' }
                    };
                    const tierStyle = tierColors[tier] || tierColors[3];
                    
                    let milestoneHtml = `
                                <div style="margin-bottom: 12px; border: 1px solid var(--border-color); border-radius: 6px; overflow: hidden; background: var(--bg-tertiary);">
                                    <!-- Milestone Header -->
                                    <div style="display: flex; align-items: center; gap: 8px; padding: 10px; background: var(--bg-quaternary); border-bottom: 1px solid var(--border-color);">
                                        <span style="display: inline-flex; align-items: center; justify-content: center; min-width: 32px; height: 24px; background: ${tierStyle.bg}; color: white; font-weight: 700; border-radius: 4px; font-size: 10px; padding: 0 8px;">M${displayNumber}</span>
                                        <input type="checkbox" 
                                            ${milestone.completed ? 'checked' : ''}
                                            onchange="event.stopPropagation(); window.synergyBoard.toggleMilestone('${session.session_id}', ${idx});"
                                            style="cursor: pointer;">
                                        <div style="flex: 1;">
                                            <div style="font-weight: 600; ${milestone.completed ? 'text-decoration: line-through; opacity: 0.6;' : ''}">
                                                ${this.escapeHtml(milestoneTitle)}
                                            </div>
                                            ${milestoneDesc ? `<div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">${this.escapeHtml(milestoneDesc)}</div>` : ''}
                                        </div>
                                        <span style="font-size: 10px; padding: 2px 8px; background: ${tierStyle.bg}; color: white; border-radius: 12px; font-weight: 600;">${tierStyle.text}</span>
                                        ${milestone.due_date ? `<span style="font-size: 11px; color: var(--text-muted);"><i class="fas fa-calendar"></i> ${new Date(milestone.due_date).toLocaleDateString()}</span>` : ''}
                                    </div>
                                    
                                    <!-- Tasks under milestone -->
                                    ${tasks.length > 0 ? `
                                    <div style="padding: 8px;">
                                        <div style="font-size: 11px; color: var(--text-muted); margin-bottom: 6px; font-weight: 600;">
                                            <i class="fas fa-tasks"></i> Tasks (${completedTasks}/${tasks.length})
                                        </div>
                                        ${tasks.map((task, taskIdx) => {
                const taskNumber = `${displayNumber}.${taskIdx + 1}`;
                const taskText = task.title || task.description || task.text || 'Untitled Task';
                return `
                                            <div style="display: flex; align-items: flex-start; gap: 6px; padding: 6px 8px; margin-bottom: 4px; background: var(--bg-secondary); border-radius: 4px; font-size: 12px;">
                                                <span style="display: inline-block; min-width: 38px; padding: 2px 6px; background: #f0f0f0; border: 1px solid #ddd; border-radius: 3px; font-family: 'Courier New', monospace; font-size: 9px; color: #666; text-align: center; font-weight: 600;">T${taskNumber}</span>
                                                <input type="checkbox" 
                                                    ${task.completed ? 'checked' : ''}
                                                    onchange="event.stopPropagation(); window.synergyBoard.toggleMilestoneTask('${session.session_id}', ${idx}, ${taskIdx});"
                                                    style="margin-top: 2px; cursor: pointer;">
                                                <span style="flex: 1; ${task.completed ? 'text-decoration: line-through; opacity: 0.6;' : ''}">
                                                    ${this.escapeHtml(taskText)}
                                                </span>
                                                ${task.assignee ? `<span style="font-size: 10px; color: var(--text-muted);"><i class="fas fa-user"></i> ${this.escapeHtml(task.assignee)}</span>` : ''}
                                            </div>
                                        `;
                                    }).join('')}
                                    </div>
                                    ` : ''}
                                </div>
                            `;
                    return milestoneHtml;
                }).join('') : '<div style="opacity: 0.6; font-style: italic; padding: 8px;"><i class="fas fa-info-circle"></i> No milestones added</div>'}
                        </div>
                    </div>
                `;

        // Links section removed from here (now appears earlier)
        if (false) {
            html += `
                        <div class="synergy-card-section" style="margin-bottom: 16px;">
                            <div class="synergy-card-section-title" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                                <i class="fas fa-link"></i>
                                Links (${links.length})
                            </div>
                            <div style="font-size: 13px;">
                                ${links.map(link => `
                                    <div style="display: flex; align-items: center; gap: 8px; padding: 8px; margin-bottom: 4px; background: var(--bg-quaternary); border-radius: 4px;">
                                        <i class="fas fa-external-link-alt" style="color: var(--accent-primary);"></i>
                                        <a href="${this.escapeHtml(link.url)}" target="_blank" 
                                            style="flex: 1; color: var(--accent-primary); text-decoration: none;"
                                            onclick="event.stopPropagation();">
                                            ${this.escapeHtml(link.title)}
                                        </a>
                                        <span style="font-size: 11px; color: var(--text-muted);">${link.type || 'external'}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
        }

        // Linked Threads - ALWAYS SHOW (even if empty) - Use same rendering as dashboard
        const threadIds = this.parseJsonField(session.thread_ids, []);
        html += `
                    <div class="synergy-card-section" style="margin-bottom: 16px;" id="sidebar-threads-section-${session.session_id}">
                        <div class="synergy-card-section-title" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                            <i class="fas fa-comments"></i>
                            Linked Threads ${threadIds.length > 0 ? `(${threadIds.length})` : ''}
                        </div>
                        <div class="sidebar-thread-list-loading" style="font-size: 13px;">
                            ${threadIds.length > 0 ? '<i class="fas fa-spinner fa-spin"></i> Loading linked threads...' : '<div style="opacity: 0.6; font-style: italic; padding: 8px;">No linked threads</div>'}
                        </div>
                    </div>
                `;

        // Load thread info cards asynchronously (same as dashboard)
        if (threadIds.length > 0 && window.synergyBoard) {
            setTimeout(() => {
                const threadsSection = document.getElementById(`sidebar-threads-section-${session.session_id}`);
                const loadingDiv = threadsSection ? threadsSection.querySelector('.sidebar-thread-list-loading') : null;

                if (threadsSection && loadingDiv) {
                    window.synergyBoard.renderLinkedThreads(threadIds).then(threadsHTML => {
                        if (loadingDiv) {
                            loadingDiv.outerHTML = threadsHTML;
                        }
                    }).catch(err => {
                        console.warn('[SIDEBAR] Failed to load linked threads', err);
                        if (loadingDiv) {
                            loadingDiv.innerHTML = '<div style="opacity: 0.6; font-style: italic; padding: 8px;"><i class="fas fa-exclamation-circle"></i> Failed to load threads</div>';
                        }
                    });
                }
            }, 100);
        }

        // Assigned Agents section removed - redundant with Linked Threads section

        // Notes - ALWAYS SHOW (even if empty)
        html += `
                    <div class="synergy-card-section" style="margin-bottom: 16px;">
                        <div class="synergy-card-section-title" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                            <i class="fas fa-sticky-note"></i>
                            Notes
                        </div>
                        <div style="font-size: 13px;">
                            ${session.notes ? `<div style="padding: 8px;">${this.escapeHtml(session.notes)}</div>` : '<div style="opacity: 0.6; font-style: italic; padding: 8px;">No notes added</div>'}
                        </div>
                    </div>
                `;

        // Activity Log - ALWAYS SHOW (even if empty)
        const recentActivity = this.parseJsonField(session.recent_activity, []);
        html += `
                    <div class="synergy-card-section" style="margin-bottom: 16px;">
                        <div class="synergy-card-section-title" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                            <i class="fas fa-history"></i>
                            Activity Log
                        </div>
                        <div style="font-size: 12px; color: var(--text-secondary);">
                            ${recentActivity.length > 0 ? recentActivity.slice(0, 5).map(activity => `
                                <div style="padding: 6px 0; border-bottom: 1px solid var(--border-muted);">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <span>${this.escapeHtml(activity.action || activity.description || 'Activity')}</span>
                                        <span style="font-size: 10px; color: var(--text-muted);">${activity.timestamp ? new Date(activity.timestamp).toLocaleString() : ''}</span>
                                    </div>
                                </div>
                            `).join('') : '<div style="opacity: 0.6; font-style: italic; padding: 8px;">No activity yet</div>'}
                            ${recentActivity.length > 5 ? `<div style="text-align: center; padding: 8px; color: var(--text-muted); font-size: 11px;">...and ${recentActivity.length - 5} more activities</div>` : ''}
                        </div>
                    </div>
                `;

        // Tags at the BOTTOM
        if (tags.length > 0) {
            html += `
                        <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; padding-top: 8px; border-top: 1px solid var(--border-muted);">
                            ${tags.map(tag => `
                                <span style="background: var(--accent-primary); color: white; padding: 2px 10px; border-radius: 12px; font-size: 10px; font-weight: 500; display: inline-flex; align-items: center; gap: 4px;">
                                    <i class="fas fa-tag" style="font-size: 8px;"></i> ${this.escapeHtml(tag)}
                                </span>
                            `).join('')}
                        </div>
                    `;
        }

        // Optional: View Full Card button (now redundant but can keep for popup)
        html += `
                    <button class="synergy-expand-btn" onclick="event.stopPropagation(); SynergySidebar.openInPopup('${session.session_id}'); return false;"
                        style="width: 100%; margin-top: 16px; padding: 10px; background: var(--bg-quaternary); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary); cursor: pointer; font-size: 13px; display: flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s;">
                        <i class="fas fa-external-link-alt"></i>
                        Open in Popup Window
                    </button>
                `;

            return html;
        },

        parseJsonField(field, fallback = []) {
            if (field === null || field === undefined) return fallback;
            if (Array.isArray(field)) return field;
            if (typeof field === 'object' && field !== null) return field;
            if (typeof field === 'string' && field.trim()) {
                try {
                    return JSON.parse(field);
                } catch (e) {
                    return fallback;
                }
            }
            return fallback;
        },

        toggleExpand(event, sessionId) {
            // Don't toggle if clicking on interactive elements
            if (event.target.closest('.synergy-item-btn') ||
                event.target.closest('.synergy-expand-btn') ||
                event.target.tagName === 'INPUT' ||
                event.target.tagName === 'A' ||
                event.target.tagName === 'BUTTON' ||
                event.target.closest('a') ||
                event.target.closest('button') ||
                event.target.closest('input')) {
                return;
            }

            const item = document.querySelector(`[data-context="sidebar"] .synergy-session-item[data-session-id="${sessionId}"]`);
            if (!item) {
                console.warn(`[SYNERGY SIDEBAR] Item not found: ${sessionId}`);
                return;
            }

            // Toggle expanded state
            if (this.expandedSessions.has(sessionId)) {
                this.expandedSessions.delete(sessionId);
                item.classList.remove('expanded');
                console.log(`[SYNERGY SIDEBAR] Collapsed: ${sessionId}`);
            } else {
                this.expandedSessions.add(sessionId);
                item.classList.add('expanded');
                console.log(`[SYNERGY SIDEBAR] Expanded: ${sessionId}`);

                // Scroll into view
                setTimeout(() => {
                    item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }, 100);
            }
        },

        togglePin(sessionId) {
            if (this.pinnedSessions.has(sessionId)) {
                this.pinnedSessions.delete(sessionId);
            } else {
                this.pinnedSessions.add(sessionId);
            }

            // Save to localStorage
            localStorage.setItem('synergy_pinned', JSON.stringify([...this.pinnedSessions]));

            // Update UI
            this.renderSessions();
            showNotification(this.pinnedSessions.has(sessionId) ? 'Session pinned' : 'Session unpinned', 'success');
        },

        switchView(view) {
            this.currentView = view;

            // Update tab UI
            document.querySelectorAll('.synergy-view-tab').forEach(tab => {
                if (tab.dataset.view === view) {
                    tab.classList.add('active');
                } else {
                    tab.classList.remove('active');
                }
            });

            // Show/hide views
            const listView = document.getElementById('synergy-list-view');
            const pinnedView = document.getElementById('synergy-pinned-view');

            if (view === 'list') {
                listView.classList.add('active');
                listView.style.display = 'block';
                pinnedView.classList.remove('active');
                pinnedView.style.display = 'none';
            } else {
                listView.classList.remove('active');
                listView.style.display = 'none';
                pinnedView.classList.add('active');
                pinnedView.style.display = 'block';
            }

            this.renderSessions();
        },

        filterByCategory(category) {
            this.currentFilter = category;

            // Update chip UI
            document.querySelectorAll('.synergy-category-chip').forEach(chip => {
                if (chip.dataset.category === category) {
                    chip.classList.add('active');
                } else {
                    chip.classList.remove('active');
                }
            });

            this.renderSessions();
        },

        getFilteredSessions(sessions) {
            // Apply search query filter
            let filtered = sessions;
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase();
                filtered = filtered.filter(s =>
                    s.title?.toLowerCase().includes(query) ||
                    s.description?.toLowerCase().includes(query) ||
                    s.kanban_column?.toLowerCase().includes(query)
                );
            }

            // Apply category filter
            if (this.currentFilter !== 'all') {
                filtered = filtered.filter(s => s.kanban_column === this.currentFilter);
            }

            return filtered;
        },

        filterSessions(value) {
            this.searchQuery = value;
            this.renderSessions();
        },

        // DEPRECATED: Old toggleSidebar method (keeping for backward compatibility)
        // The new method above handles lazy loading
        toggleSidebar_OLD() {
            const sidebar = document.getElementById('synergy-sidebar');
            const toggle = document.getElementById('synergy-sidebar-toggle');
            const container = document.querySelector('.platform-container');
            const side = sidebar.getAttribute('data-side') || 'left';

            if (sidebar.classList.contains('collapsed')) {
                sidebar.classList.remove('collapsed');
                toggle.style.display = 'none';
                container.setAttribute('data-synergy-side', side);
                // Lazy load sessions on first open
                if (!this.sessionsLoaded) {
                    this.loadSessions();
                }
            } else {
                sidebar.classList.add('collapsed');
                toggle.style.display = 'flex';
                container.removeAttribute('data-synergy-side');
            }
        },

        initDraggableToggle() {
            const toggle = document.getElementById('synergy-sidebar-toggle');
            const sidebar = document.getElementById('synergy-sidebar');
            let isDragging = false;
            let startX = 0;

            // Load saved side preference
            const savedSide = localStorage.getItem('synergy-sidebar-side') || 'left';
            this.setSidebarSide(savedSide);

            toggle.addEventListener('mousedown', (e) => {
                isDragging = true;
                startX = e.clientX;
                toggle.classList.add('dragging');
                e.preventDefault();
            });

            document.addEventListener('mousemove', (e) => {
                if (!isDragging) return;

                const deltaX = e.clientX - startX;
                if (Math.abs(deltaX) > 10) {
                    // Only toggle side if dragged significantly
                    const currentSide = sidebar.getAttribute('data-side') || 'left';
                    const newSide = e.clientX < window.innerWidth / 2 ? 'left' : 'right';

                    if (newSide !== currentSide) {
                        this.setSidebarSide(newSide);
                    }
                }
            });

            document.addEventListener('mouseup', () => {
                if (isDragging) {
                    isDragging = false;
                    toggle.classList.remove('dragging');

                    // Save preference
                    const side = sidebar.getAttribute('data-side') || 'left';
                    localStorage.setItem('synergy-sidebar-side', side);
                }
            });
        },

        setSidebarSide(side) {
            const sidebar = document.getElementById('synergy-sidebar');
            const toggle = document.getElementById('synergy-sidebar-toggle');
            const container = document.querySelector('.platform-container');

            sidebar.setAttribute('data-side', side);
            toggle.setAttribute('data-side', side);

            // Update container margin only if sidebar is open
            if (!sidebar.classList.contains('collapsed')) {
                container.setAttribute('data-synergy-side', side);
            }
        },

            async refreshSessions() {
            await this.loadSessions();
            showNotification('Sessions refreshed', 'success');
        },

        openInPopup(sessionId) {
            console.log('[SYNERGY SIDEBAR] Opening popup for session:', sessionId);

            try {
                // Check if synergyBoard exists
                if (typeof window.synergyBoard === 'undefined') {
                    console.error('[SYNERGY SIDEBAR] window.synergyBoard not found');
                    showNotification('Synergy board not initialized', 'error');
                    return;
                }

                console.log('[SYNERGY SIDEBAR] synergyBoard found, checking methods...');
                console.log('[SYNERGY SIDEBAR] Available methods:', Object.keys(window.synergyBoard));

                // Check for ensureInitialized
                if (typeof window.synergyBoard.ensureInitialized === 'function') {
                    console.log('[SYNERGY SIDEBAR] Calling ensureInitialized...');
                    window.synergyBoard.ensureInitialized().then(() => {
                        console.log('[SYNERGY SIDEBAR] Initialization complete, calling popOutCard...');
                        this._doPopOut(sessionId);
                    }).catch(err => {
                        console.error('[SYNERGY SIDEBAR] Initialization failed:', err);
                        this._doPopOut(sessionId); // Try anyway
                    });
                } else {
                    console.log('[SYNERGY SIDEBAR] No ensureInitialized, calling popOutCard directly...');
                    this._doPopOut(sessionId);
                }
            } catch (error) {
                console.error('[SYNERGY SIDEBAR] Error in openInPopup:', error);
                showNotification('Error opening card: ' + error.message, 'error');
            }
        },

        _doPopOut(sessionId) {
            if (typeof window.synergyBoard.popOutCard === 'function') {
                console.log('[SYNERGY SIDEBAR] Calling popOutCard for:', sessionId);
                window.synergyBoard.popOutCard(sessionId);
            } else {
                console.error('[SYNERGY SIDEBAR] popOutCard method not found');
                console.log('[SYNERGY SIDEBAR] Available methods:', Object.keys(window.synergyBoard));
                showNotification('Unable to open card popup - method not found', 'error');
            }
        },

        renderTile(session) {
            const container = document.getElementById('synergy-tiles-container');

            const tile = document.createElement('div');
            tile.className = 'synergy-tile';
            tile.id = `synergy-tile-${session.session_id}`;

            const priorityColors = {
                'critical': '#dc2626',
                'high': '#ef4444',
                'medium': '#fbbf24',
                'low': '#22c55e'
            };

            tile.innerHTML = `
                    <div class="synergy-tile-header">
                        <div class="synergy-tile-title">
                            <i class="fas fa-circle" style="color: ${priorityColors[session.priority]};"></i>
                            <span>${this.escapeHtml(session.title)}</span>
                        </div>
                        <div class="synergy-tile-controls">
                            <button class="synergy-tile-btn edit" onclick="SynergySidebar.toggleTileEdit('${session.session_id}')" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="synergy-tile-btn" onclick="SynergySidebar.openInPopup('${session.session_id}')" title="Open in popup">
                                <i class="fas fa-external-link-alt"></i>
                            </button>
                            <button class="synergy-tile-btn close" onclick="SynergySidebar.closeTile('${session.session_id}')" title="Close">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    <div class="synergy-tile-content" id="synergy-tile-content-${session.session_id}">
                        <div style="margin-bottom: 16px;">
                            <strong>Project:</strong> ${this.escapeHtml(session.project_name || 'No Project')}
                        </div>
                        ${session.description ? `
                            <div style="margin-bottom: 16px;">
                                <strong>Description:</strong>
                                <div style="margin-top: 8px; padding: 12px; background: var(--bg-secondary); border-radius: 6px;">
                                    ${this.escapeHtml(session.description)}
                                </div>
                            </div>
                        ` : ''}
                        <div style="margin-bottom: 12px;">
                            <strong>Status:</strong> <span style="padding: 4px 8px; background: var(--bg-secondary); border-radius: 4px;">${session.status}</span>
                        </div>
                        <div style="margin-bottom: 12px;">
                            <strong>Priority:</strong> <span style="padding: 4px 8px; background: var(--bg-secondary); border-radius: 4px; color: ${priorityColors[session.priority]};">${session.priority}</span>
                        </div>
                        ${session.notes ? `
                            <div style="margin-bottom: 16px;">
                                <strong>Notes:</strong>
                                <div style="margin-top: 8px; padding: 12px; background: var(--bg-secondary); border-radius: 6px; font-style: italic;">
                                    ${this.escapeHtml(session.notes)}
                                </div>
                            </div>
                        ` : ''}
                        <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border-default);">
                            <small style="color: var(--text-muted);">Session ID: ${session.session_id}</small>
                        </div>
                    </div>
                `;

            container.appendChild(tile);

            // Scroll to new tile
            setTimeout(() => {
                tile.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        },

        closeTile(sessionId) {
            const tile = document.getElementById(`synergy-tile-${sessionId}`);
            if (tile) {
                tile.remove();
            }

            // Remove from open tiles
            this.openTiles = this.openTiles.filter(id => id !== sessionId);

            // If no tiles left, show list
            if (this.openTiles.length === 0) {
                document.getElementById('synergy-session-list').style.display = 'block';
                document.getElementById('synergy-tiles-container').style.display = 'none';
            }
        },

        toggleTileEdit(sessionId) {
            const tile = document.getElementById(`synergy-tile-${sessionId}`);
            if (!tile) return;

            // For now, just open in popup edit mode
            this.openInPopup(sessionId, true);
        },

        openInPopup(sessionId, editMode = false) {
            if (typeof synergyBoard !== 'undefined') {
                synergyBoard.popOutCard(sessionId);

                if (editMode) {
                    setTimeout(() => {
                        const popout = Array.from(document.querySelectorAll('.popout-card-window'))
                            .find(w => w.dataset.sessionId === sessionId);
                        if (popout) {
                            synergyBoard.togglePopupEdit(popout.id, sessionId);
                        }
                    }, 200);
                }
            }
        },

        scrollToTile(sessionId) {
            const tile = document.getElementById(`synergy-tile-${sessionId}`);
            if (tile) {
                tile.scrollIntoView({ behavior: 'smooth', block: 'start' });

                // Pulse effect
                tile.style.borderColor = 'var(--accent-primary)';
                setTimeout(() => {
                    tile.style.borderColor = 'var(--border-default)';
                }, 1000);
            }
        }
        }; // End of stub synergyBoard
        */

        // Stub removed - real synergyBoard declared at line 38707
        // window.synergyBoard is exposed there