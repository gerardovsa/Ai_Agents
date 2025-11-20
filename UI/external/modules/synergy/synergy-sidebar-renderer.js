/**
 * Synergy Sidebar Renderer Module
 * 
 * Professional rendering module for Synergy session cards in sidebar
 * Displays complete hierarchy: Milestones → Tasks → Subtasks
 * Plus: Documents, Links, Tags, Assignees, Dates, Status
 * 
 * @module SynergySidebarRenderer
 * @version 2.0.0
 * @date 2025-11-19
 */

class SynergySidebarRenderer {
    constructor() {
        this.API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
        console.log('[SYNERGY SIDEBAR RENDERER] Module loaded');
    }

    /**
     * Create complete session card item for sidebar
     * @param {Object} session - Session data from API
     * @param {Set} expandedSessions - Set of expanded session IDs
     * @param {Set} pinnedSessions - Set of pinned session IDs
     * @returns {HTMLElement} Complete session card element
     */
    createSessionItem(session, expandedSessions, pinnedSessions) {
        const isPinned = pinnedSessions.has(session.session_id);
        const isExpanded = expandedSessions.has(session.session_id);

        const item = document.createElement('div');
        item.className = 'synergy-session-item';
        item.setAttribute('data-session-id', session.session_id);
        if (isPinned) item.classList.add('pinned');
        if (isExpanded) item.classList.add('expanded');

        // Render collapsed card
        item.innerHTML = this.renderCollapsedCard(session);

        // If expanded, load and render full content
        if (isExpanded) {
            this.loadAndRenderFullCard(session.session_id, item);
        }

        return item;
    }

    /**
     * Render COMPACT card (icon-only for 80px sidebar)
     * Shows: First letter icon + priority dot + hover tooltip
     */
    renderCompactCard(session) {
        const priorityColors = {
            'critical': '#dc2626',
            'high': '#ef4444',
            'medium': '#fbbf24',
            'low': '#22c55e'
        };

        const priorityColor = priorityColors[session.priority] || '#6b7280';
        const firstLetter = session.title ? session.title.charAt(0).toUpperCase() : 'S';

        // Generate background gradient from priority color
        const bgGradient = `linear-gradient(135deg, ${priorityColor} 0%, ${priorityColor}dd 100%)`;

        return `
            <div class="synergy-compact-icon" style="background: ${bgGradient};">
                ${firstLetter}
                <div class="synergy-compact-priority-dot" style="background: ${priorityColor};"></div>
                <div class="synergy-compact-tooltip">
                    <div class="synergy-compact-tooltip-title">${this.escapeHtml(session.title)}</div>
                    <div class="synergy-compact-tooltip-meta">
                        <span class="priority-badge" style="background: ${priorityColor};">${session.priority || 'MEDIUM'}</span>
                        <span style="color: var(--text-tertiary);">${session.status || 'active'}</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render collapsed card (header + basic info)
     * Clean HTML with CSS classes only - NO inline styles
     */
    renderCollapsedCard(session) {
        return `
            ${this.renderCompactCard(session)}
            <div class="synergy-card-header" onclick="SynergySidebar.toggleCardExpand('${session.session_id}')">
                <div class="synergy-card-header-left">
                    <div class="synergy-card-title">${this.escapeHtml(session.title)}</div>
                    <div class="synergy-card-badges">
                        <span class="priority-badge priority-${session.priority || 'medium'}">${session.priority || 'medium'}</span>
                        <span class="status-badge status-${session.status || 'active'}">${session.status || 'active'}</span>
                    </div>
                </div>
                <div class="synergy-card-header-right">
                    <button class="synergy-card-btn edit-btn" onclick="event.stopPropagation(); SynergySidebar.editCard('${session.session_id}')" title="Edit session">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="synergy-card-btn pin-btn ${session.is_pinned ? 'pinned' : ''}" onclick="event.stopPropagation(); SynergySidebar.togglePin('${session.session_id}')" title="Pin session">
                        <i class="fas fa-thumbtack"></i>
                    </button>
                    <button class="synergy-card-btn open-btn" onclick="event.stopPropagation(); SynergySidebar.openInPopup('${session.session_id}')" title="Open in popup">
                        <i class="fas fa-external-link-alt"></i> Open
                    </button>
                </div>
            </div>
            <div class="synergy-card-content collapsed">
                <div class="loading-placeholder">
                    <i class="fas fa-spinner fa-spin"></i>
                    <div class="loading-text">Loading session data...</div>
                </div>
            </div>
        `;
    }

    /**
     * Load and render COMPLETE expanded card with all data
     */
    async loadAndRenderFullCard(sessionId, itemElement) {
        try {
            console.log(`[SYNERGY SIDEBAR] Loading full data for: ${sessionId}`);

            const contentArea = itemElement.querySelector('.synergy-card-content');
            if (!contentArea) {
                console.error('[SYNERGY SIDEBAR] Content area not found');
                return;
            }

            // Show content area
            contentArea.style.display = 'block';

            // Fetch milestones with full hierarchy
            const url = `${this.API_BASE_URL}/api/synergy/${sessionId}/milestones`;
            console.log(`[SYNERGY SIDEBAR] Fetching: ${url}`);

            const response = await fetch(url);

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            const data = await response.json();
            const milestones = data.milestones || [];

            console.log(`[SYNERGY SIDEBAR] Loaded ${milestones.length} milestones`);

            // Get session data for documents/links
            const session = data.session || {};

            // Render complete expanded card
            contentArea.innerHTML = this.renderExpandedCardContent(session, milestones, sessionId);

        } catch (error) {
            console.error('[SYNERGY SIDEBAR] Error loading full card:', error);
            const contentArea = itemElement.querySelector('.synergy-card-content');
            if (contentArea) {
                contentArea.innerHTML = `
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
            }
        }
    }

    /**
     * Render COMPLETE expanded card content with ALL elements
     */
    renderExpandedCardContent(session, milestones, sessionId) {
        let html = '';

        // === EDIT MODE TOOLBAR (shown when editing) ===
        html += this.renderEditModeToolbar(session, sessionId);

        // === SECTION 1: SESSION METADATA ===
        html += this.renderMetadataSection(session);

        // === SECTION 2: DESCRIPTION ===
        if (session.description) {
            html += this.renderDescriptionSection(session.description);
        }

        // === SECTION 3: MILESTONES + TASKS + SUBTASKS (FULL HIERARCHY) ===
        if (milestones && milestones.length > 0) {
            html += this.renderMilestonesSection(milestones, sessionId);
        } else {
            html += `
                <div style="
                    padding: 24px;
                    text-align: center;
                    background: var(--bg-quaternary);
                    border-radius: 8px;
                    margin-bottom: 16px;
                ">
                    <i class="fas fa-tasks" style="font-size: 32px; color: var(--text-tertiary); margin-bottom: 8px;"></i>
                    <div style="color: var(--text-secondary); font-size: 13px;">No milestones yet</div>
                </div>
            `;
        }

        // === SECTION 4: DOCUMENTS ===
        html += this.renderDocumentsSection(session.documents);

        // === SECTION 5: LINKS ===
        html += this.renderLinksSection(session.links);

        // === SECTION 6: TAGS ===
        html += this.renderTagsSection(session.tags);

        return html;
    }

    /**
     * Render edit mode toolbar with save/cancel buttons
     */
    renderEditModeToolbar(session, sessionId) {
        return `
            <div class="synergy-edit-toolbar" style="
                display: none;
                padding: 12px 16px;
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                color: white;
                margin-bottom: 16px;
                border-radius: 8px;
                align-items: center;
                justify-content: space-between;
            " data-session-id="${sessionId}">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <i class="fas fa-edit" style="font-size: 18px;"></i>
                    <div>
                        <div style="font-weight: 700; font-size: 14px;">Edit Mode</div>
                        <div style="font-size: 11px; opacity: 0.9;">Make changes below, then click Save</div>
                    </div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button class="synergy-edit-cancel" style="
                        background: rgba(255, 255, 255, 0.2);
                        border: 1px solid rgba(255, 255, 255, 0.4);
                        color: white;
                        padding: 8px 16px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 12px;
                        font-weight: 600;
                        transition: all 0.2s;
                    ">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                    <button class="synergy-edit-save" style="
                        background: white;
                        border: none;
                        color: #2563eb;
                        padding: 8px 16px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 12px;
                        font-weight: 700;
                        transition: all 0.2s;
                    ">
                        <i class="fas fa-save"></i> Save Changes
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Render metadata section (assignees, dates, stats)
     */
    renderMetadataSection(session) {
        const assignees = this.parseJsonField(session.assignees, []);
        const assigneeNames = assignees
            .map(a => (typeof a === 'object' ? a.name : a))
            .filter(n => n)
            .join(', ');

        let dueDateHTML = '';
        if (session.due_date) {
            const dueDate = new Date(session.due_date);
            if (dueDate.getFullYear() > 1970) {
                const isOverdue = dueDate < new Date();
                dueDateHTML = `
                    <div style="
                        background: ${isOverdue ? '#dc2626' : 'var(--bg-quaternary)'};
                        color: ${isOverdue ? 'white' : 'var(--text-primary)'};
                        padding: 6px 12px;
                        border-radius: 8px;
                        font-size: 12px;
                        font-weight: 600;
                        display: inline-flex;
                        align-items: center;
                        gap: 6px;
                    ">
                        <i class="fas fa-calendar"></i>
                        ${isOverdue ? 'OVERDUE: ' : 'Due: '}${dueDate.toLocaleDateString()}
                    </div>
                `;
            }
        }

        return `
            <div style="
                padding: 16px;
                background: var(--bg-quaternary);
                border-radius: 8px;
                margin-bottom: 16px;
                border: 1px solid var(--border-secondary);
            ">
                ${assigneeNames ? `
                    <div style="margin-bottom: 12px;">
                        <div style="font-size: 11px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 6px;">
                            <i class="fas fa-users"></i> Assigned To
                        </div>
                        <div style="font-size: 13px; color: var(--text-primary); font-weight: 500;">
                            ${this.escapeHtml(assigneeNames)}
                        </div>
                    </div>
                ` : ''}
                ${dueDateHTML ? `
                    <div style="margin-bottom: 12px;">
                        ${dueDateHTML}
                    </div>
                ` : ''}
                <div style="display: flex; gap: 16px; font-size: 12px; color: var(--text-secondary);">
                    <span><i class="fas fa-comments"></i> ${session.message_count || 0} messages</span>
                    <span><i class="fas fa-clock"></i> ${this.formatTimeAgo(session.updated_at)}</span>
                </div>
            </div>
        `;
    }

    /**
     * Render description section
     */
    renderDescriptionSection(description) {
        return `
            <div style="
                padding: 16px;
                background: var(--bg-tertiary);
                border-left: 4px solid var(--accent-primary);
                border-radius: 4px;
                margin-bottom: 16px;
            ">
                <div style="font-weight: 700; font-size: 12px; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 8px;">
                    <i class="fas fa-align-left"></i> Description
                </div>
                <div style="font-size: 13px; line-height: 1.6; color: var(--text-primary);">
                    ${this.escapeHtml(description)}
                </div>
            </div>
        `;
    }

    /**
     * Render COMPLETE milestones section with tasks and subtasks
     */
    renderMilestonesSection(milestones, sessionId) {
        const completedCount = milestones.filter(m => m.completed).length;
        const totalCount = milestones.length;
        const progress = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

        let html = `
            <div style="margin-bottom: 16px;">
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 12px 16px;
                    background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
                    border-radius: 8px;
                    margin-bottom: 12px;
                ">
                    <div style="color: white; font-weight: 700; font-size: 14px;">
                        <i class="fas fa-tasks"></i> Project Milestones
                    </div>
                    <div style="color: white; font-size: 13px; font-weight: 600;">
                        ${completedCount}/${totalCount} Complete (${progress}%)
                    </div>
                </div>
        `;

        // Render each milestone with full hierarchy
        milestones.forEach((milestone, mIdx) => {
            html += this.renderMilestone(milestone, mIdx + 1, sessionId);
        });

        html += `</div>`;
        return html;
    }

    /**
     * Render single milestone with ALL tasks and subtasks
     */
    renderMilestone(milestone, milestoneNum, sessionId) {
        const tasks = milestone.tasks || [];
        const completedTasks = tasks.filter(t => t.completed).length;
        const taskProgress = tasks.length > 0 ? Math.round((completedTasks / tasks.length) * 100) : 0;

        const isCompleted = milestone.completed;
        const borderColor = isCompleted ? '#22c55e' : '#6b7280';
        const bgColor = isCompleted ? 'rgba(34, 197, 94, 0.1)' : 'var(--bg-tertiary)';

        let html = `
            <div style="
                border: 2px solid ${borderColor};
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 16px;
                background: ${bgColor};
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            ">
                <!-- Milestone Header -->
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 16px;
                    padding-bottom: 12px;
                    border-bottom: 1px solid var(--border-secondary);
                ">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                            <span style="
                                background: ${borderColor};
                                color: white;
                                padding: 4px 10px;
                                border-radius: 6px;
                                font-size: 11px;
                                font-weight: 700;
                            ">M${milestoneNum}</span>
                            <span style="font-size: 18px;">${isCompleted ? '✅' : '⭕'}</span>
                            <span style="font-weight: 700; font-size: 15px; color: var(--text-primary);">
                                ${this.escapeHtml(milestone.title)}
                            </span>
                        </div>
                        ${milestone.description ? `
                            <div style="font-size: 12px; color: var(--text-secondary); margin-left: 45px;">
                                ${this.escapeHtml(milestone.description)}
                            </div>
                        ` : ''}
                    </div>
                    <label style="cursor: pointer;">
                        <input type="checkbox" 
                            ${isCompleted ? 'checked' : ''}
                            data-milestone-id="${milestone.milestone_id}"
                            data-session-id="${sessionId}"
                            class="milestone-checkbox"
                            style="width: 20px; height: 20px; cursor: pointer;">
                    </label>
                </div>

                <!-- Tasks Progress Bar -->
                <div style="
                    background: var(--bg-quaternary);
                    border-radius: 8px;
                    padding: 12px;
                    margin-bottom: 16px;
                ">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="font-size: 12px; font-weight: 600; color: var(--text-secondary);">
                            <i class="fas fa-list-check"></i> Task Progress
                        </span>
                        <span style="font-size: 12px; font-weight: 700; color: var(--text-primary);">
                            ${completedTasks}/${tasks.length} (${taskProgress}%)
                        </span>
                    </div>
                    <div style="
                        background: var(--bg-secondary);
                        border-radius: 4px;
                        height: 8px;
                        overflow: hidden;
                    ">
                        <div style="
                            background: linear-gradient(90deg, #22c55e 0%, #16a34a 100%);
                            height: 100%;
                            width: ${taskProgress}%;
                            transition: width 0.3s;
                        "></div>
                    </div>
                </div>

                <!-- Tasks List -->
                ${tasks.length > 0 ? `
                    <div style="margin-left: 20px;">
                        ${tasks.map((task, tIdx) => this.renderTask(task, milestoneNum, tIdx + 1, sessionId)).join('')}
                    </div>
                ` : `
                    <div style="
                        text-align: center;
                        padding: 16px;
                        color: var(--text-tertiary);
                        font-size: 12px;
                        font-style: italic;
                    ">
                        No tasks defined for this milestone
                    </div>
                `}
            </div>
        `;

        return html;
    }

    /**
     * Render single task with ALL subtasks
     */
    renderTask(task, milestoneNum, taskNum, sessionId) {
        const subtasks = task.subtasks || [];
        const completedSubtasks = subtasks.filter(s => s.completed).length;
        const isBlocked = task.status === 'blocked';
        const isCompleted = task.completed;

        const taskColor = isBlocked ? '#ef4444' : (isCompleted ? '#22c55e' : '#6b7280');

        let html = `
            <div style="
                border-left: 3px solid ${taskColor};
                padding: 12px;
                padding-left: 16px;
                margin-bottom: 12px;
                background: var(--bg-quaternary);
                border-radius: 4px;
            ">
                <!-- Task Header -->
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                            <span style="
                                background: ${taskColor};
                                color: white;
                                padding: 2px 8px;
                                border-radius: 4px;
                                font-size: 10px;
                                font-weight: 700;
                            ">T${milestoneNum}.${taskNum}</span>
                            ${isBlocked ? `
                                <span style="
                                    background: #ef4444;
                                    color: white;
                                    padding: 2px 8px;
                                    border-radius: 4px;
                                    font-size: 10px;
                                    font-weight: 700;
                                ">🚫 BLOCKED</span>
                            ` : ''}
                            <span style="font-size: 14px;">${isCompleted ? '✅' : '⭕'}</span>
                            <span style="font-weight: 600; font-size: 13px; color: var(--text-primary);">
                                ${this.escapeHtml(task.title)}
                            </span>
                        </div>
                        ${task.description ? `
                            <div style="font-size: 11px; color: var(--text-secondary); margin-left: 45px;">
                                ${this.escapeHtml(task.description)}
                            </div>
                        ` : ''}
                        ${isBlocked && task.blocked_reason ? `
                            <div style="
                                margin-left: 45px;
                                margin-top: 6px;
                                padding: 6px 10px;
                                background: rgba(239, 68, 68, 0.1);
                                border-left: 3px solid #ef4444;
                                border-radius: 4px;
                                font-size: 11px;
                                color: #ef4444;
                            ">
                                <strong>Blocked:</strong> ${this.escapeHtml(task.blocked_reason)}
                            </div>
                        ` : ''}
                    </div>
                    <label style="cursor: pointer;">
                        <input type="checkbox"
                            ${isCompleted ? 'checked' : ''}
                            ${isBlocked ? 'disabled' : ''}
                            data-task-id="${task.task_id}"
                            data-session-id="${sessionId}"
                            class="task-checkbox"
                            style="width: 18px; height: 18px; cursor: ${isBlocked ? 'not-allowed' : 'pointer'};">
                    </label>
                </div>

                <!-- Subtasks -->
                ${subtasks.length > 0 ? `
                    <div style="margin-left: 20px; margin-top: 8px;">
                        <div style="font-size: 10px; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; margin-bottom: 6px;">
                            Subtasks (${completedSubtasks}/${subtasks.length})
                        </div>
                        ${subtasks.map((subtask, sIdx) => this.renderSubtask(subtask, milestoneNum, taskNum, sIdx + 1, sessionId)).join('')}
                    </div>
                ` : ''}
            </div>
        `;

        return html;
    }

    /**
     * Render single subtask
     */
    renderSubtask(subtask, milestoneNum, taskNum, subtaskNum, sessionId) {
        const isCompleted = subtask.completed;

        return `
            <div style="
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 6px 10px;
                margin-bottom: 4px;
                background: var(--bg-tertiary);
                border-radius: 4px;
            ">
                <label style="cursor: pointer; display: flex; align-items: center; gap: 8px; flex: 1;">
                    <input type="checkbox"
                        ${isCompleted ? 'checked' : ''}
                        data-subtask-id="${subtask.subtask_id}"
                        data-session-id="${sessionId}"
                        class="subtask-checkbox"
                        style="width: 16px; height: 16px; cursor: pointer;">
                    <span style="
                        background: ${isCompleted ? '#22c55e' : '#6b7280'};
                        color: white;
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-size: 9px;
                        font-weight: 700;
                    ">S${milestoneNum}.${taskNum}.${subtaskNum}</span>
                    <span style="
                        font-size: 12px;
                        color: var(--text-primary);
                        ${isCompleted ? 'text-decoration: line-through; opacity: 0.7;' : ''}
                    ">
                        ${this.escapeHtml(subtask.title)}
                    </span>
                </label>
            </div>
        `;
    }

    /**
     * Render documents section
     */
    renderDocumentsSection(documents) {
        const docs = this.parseJsonField(documents, []);

        if (docs.length === 0) return '';

        let html = `
            <div style="
                padding: 16px;
                background: var(--bg-tertiary);
                border-radius: 8px;
                margin-bottom: 16px;
                border: 1px solid var(--border-secondary);
            ">
                <div style="font-weight: 700; font-size: 13px; color: var(--text-primary); margin-bottom: 12px;">
                    <i class="fas fa-file-alt" style="color: var(--accent-primary);"></i> Documents (${docs.length})
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px;">
        `;

        docs.forEach((doc, idx) => {
            html += `
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    padding: 10px;
                    background: var(--bg-quaternary);
                    border-radius: 6px;
                    border: 1px solid var(--border-secondary);
                    transition: background 0.2s;
                ">
                    <span style="
                        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                        color: white;
                        padding: 6px 10px;
                        border-radius: 6px;
                        font-size: 11px;
                        font-weight: 700;
                    ">D${idx + 1}</span>
                    <i class="fas fa-file-${doc.doc_type === 'spreadsheet' ? 'excel' : 'alt'}" style="color: var(--accent-primary); font-size: 16px;"></i>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 12px; color: var(--text-primary);">
                            ${this.escapeHtml(doc.title || doc.name || 'Untitled Document')}
                        </div>
                        ${doc.doc_type ? `
                            <div style="font-size: 10px; color: var(--text-tertiary);">
                                ${doc.doc_type} ${doc.version ? `v${doc.version}` : ''}
                            </div>
                        ` : ''}
                    </div>
                    ${doc.url ? `
                        <a href="${this.escapeHtml(doc.url)}" target="_blank" style="
                            color: var(--accent-primary);
                            text-decoration: none;
                            padding: 6px;
                        ">
                            <i class="fas fa-external-link-alt"></i>
                        </a>
                    ` : ''}
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;

        return html;
    }

    /**
     * Render links section
     */
    renderLinksSection(links) {
        const linkList = this.parseJsonField(links, []);

        if (linkList.length === 0) return '';

        let html = `
            <div style="
                padding: 16px;
                background: var(--bg-tertiary);
                border-radius: 8px;
                margin-bottom: 16px;
                border: 1px solid var(--border-secondary);
            ">
                <div style="font-weight: 700; font-size: 13px; color: var(--text-primary); margin-bottom: 12px;">
                    <i class="fas fa-link" style="color: var(--accent-primary);"></i> Links (${linkList.length})
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px;">
        `;

        linkList.forEach((link, idx) => {
            html += `
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    padding: 10px;
                    background: var(--bg-quaternary);
                    border-radius: 6px;
                    border: 1px solid var(--border-secondary);
                ">
                    <span style="
                        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                        color: white;
                        padding: 6px 10px;
                        border-radius: 6px;
                        font-size: 11px;
                        font-weight: 700;
                    ">L${idx + 1}</span>
                    <i class="fas fa-external-link-alt" style="color: var(--accent-primary); font-size: 14px;"></i>
                    <a href="${this.escapeHtml(link.url)}" target="_blank" style="
                        flex: 1;
                        font-weight: 600;
                        font-size: 12px;
                        color: var(--accent-primary);
                        text-decoration: none;
                    ">
                        ${this.escapeHtml(link.title || link.url)}
                    </a>
                    ${link.type ? `
                        <span style="
                            background: var(--bg-tertiary);
                            color: var(--text-tertiary);
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-size: 10px;
                        ">${link.type}</span>
                    ` : ''}
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;

        return html;
    }

    /**
     * Render tags section
     */
    renderTagsSection(tags) {
        const tagList = this.parseJsonField(tags, []);

        if (tagList.length === 0) return '';

        return `
            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px;">
                ${tagList.map(tag => `
                    <span style="
                        background: var(--accent-primary);
                        color: white;
                        padding: 6px 12px;
                        border-radius: 16px;
                        font-size: 11px;
                        font-weight: 600;
                        display: inline-flex;
                        align-items: center;
                        gap: 4px;
                    ">
                        <i class="fas fa-tag" style="font-size: 9px;"></i>
                        ${this.escapeHtml(tag)}
                    </span>
                `).join('')}
            </div>
        `;
    }

    // === UTILITY FUNCTIONS ===

    parseJsonField(field, fallback = []) {
        if (!field) return fallback;
        if (Array.isArray(field)) return field;
        if (typeof field === 'object') return field;
        if (typeof field === 'string') {
            try {
                return JSON.parse(field);
            } catch (e) {
                return fallback;
            }
        }
        return fallback;
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatTimeAgo(dateString) {
        if (!dateString) return 'unknown';
        const date = new Date(dateString);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);

        if (seconds < 60) return 'just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
        return date.toLocaleDateString();
    }
}

// Export for use in main application
window.SynergySidebarRenderer = SynergySidebarRenderer;
console.log('[SYNERGY SIDEBAR RENDERER] Module exported to window.SynergySidebarRenderer');
