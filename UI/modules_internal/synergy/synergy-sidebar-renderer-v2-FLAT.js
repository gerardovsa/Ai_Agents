/**
 * FILE: UI/external/modules/synergy/synergy-sidebar-renderer-v2-FLAT.js
 * PURPOSE: FLAT SPACING RENDERER - Optimized for 350px width containers
 * 
 * CRITICAL CHANGES FROM V1:
 * - ZERO nested indentation (no margin-left on tasks/subtasks)
 * - Container padding ONLY: 8px left/right (16px total = 4.6% loss)
 * - Visual hierarchy via: Badge prefixes ([M1], [T1.1], [S1.1.1])
 * - Visual hierarchy via: Left border colors (milestone=3px blue, task=2px gray)
 * - Visual hierarchy via: Font size cascade (17px → 15px → 14px)
 * - Section separators: 1px border-top + 8px padding-top
 * 
 * SPACE EFFICIENCY:
 * - Old: 350px → 88px lost (25%) → 262px usable (75%)
 * - New: 350px → 16px lost (4.6%) → 334px usable (95.4%)
 * - Gain: +72px usable width (+27% more space)
 * 
 * DEPENDENCIES:
 * - synergy-flat-spacing.css (new CSS file)
 * 
 * USED BY:
 * - Sidebar expanded cards
 * - Popup modal
 * - Dashboard kanban cards
 * 
 * LAST MODIFIED: 2025-11-24 - Complete flat spacing rewrite
 */

console.log('[SYNERGY V2] ========================================');
console.log('[SYNERGY V2] Starting renderer module load...');
console.log('[SYNERGY V2] ========================================');

class SynergySidebarRendererV2 {
    constructor() {
        this.API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
        console.log('[SYNERGY RENDERER V2] Instance created');
    }

    /**
     * Create session card item (same as V1)
     */
    createSessionItem(session, expandedSessions, pinnedSessions) {
        const isPinned = pinnedSessions.has(session.session_id);
        const isExpanded = expandedSessions.has(session.session_id);

        const item = document.createElement('div');
        item.className = 'synergy-session-item';
        item.setAttribute('data-session-id', session.session_id);
        item.setAttribute('data-context', 'sidebar');
        if (isPinned) item.classList.add('pinned');
        if (isExpanded) item.classList.add('expanded');

        // Fix #3: Restore width state from controller
        if (window.SynergySidebar && window.SynergySidebar.getWidthState) {
            const widthState = window.SynergySidebar.getWidthState(session.session_id);
            if (widthState === 'wide') {
                item.classList.add('synergy-wide');
            } else if (widthState === 'extra-wide') {
                item.classList.add('synergy-extra-wide');
            }
        }

        item.innerHTML = this.renderSimpleListItem(session);

        // Fix #3: Update icon to match restored width state
        if (window.SynergySidebar && window.SynergySidebar.getWidthState) {
            const widthState = window.SynergySidebar.getWidthState(session.session_id);
            const icon = item.querySelector('.synergy-width-toggle-btn i');
            if (icon && widthState === 'wide') {
                icon.className = 'fas fa-angle-double-right';
            } else if (icon && widthState === 'extra-wide') {
                icon.className = 'fas fa-chevron-left';
            }
        }

        if (isExpanded) {
            this.loadAndRenderFullCard(session.session_id, item);
        }

        return item;
    }

    /**
     * Render collapsed card (same as V1)
     */
    renderSimpleListItem(session) {
        const priority = session.priority || 'medium';
        const status = session.status || 'active';
        const title = session.title || 'Untitled';
        const desc = session.description || 'No description';
        const tags = Array.isArray(session.tags) ? session.tags :
            (typeof session.tags === 'string' ? JSON.parse(session.tags || '[]') : []);
        const lastActive = session.last_active ? new Date(session.last_active).toLocaleDateString() : 'Never';
        const dueDate = session.due_date ? new Date(session.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : null;
        const projectName = session.project_name || title;

        const statusBadges = {
            'active': { icon: 'check-circle', color: 'var(--accent-success)' },
            'completed': { icon: 'check-circle', color: 'var(--accent-primary)' },
            'blocked': { icon: 'exclamation-triangle', color: 'var(--accent-error)' },
            'paused': { icon: 'pause-circle', color: 'var(--accent-warning)' }
        };
        const statusBadge = statusBadges[status] || statusBadges['active'];

        const counts = this.calculateSessionCounts(session);
        const progress = counts.milestones > 0 ? Math.round((counts.tasksDone / counts.totalTasks) * 100) || 0 : 0;

        return `
            <div class="synergy-session-header-new">
                <div class="synergy-title-row">
                    <div class="synergy-title-text">${this.escapeHtml(title)}</div>
                </div>

                <div class="synergy-row-1">
                    <span class="priority-badge priority-${priority}">${priority.toUpperCase()}</span>
                    <span class="status-badge status-${status}">
                        <i class="fas fa-${statusBadge.icon}"></i> ${status}
                    </span>
                    <div class="synergy-actions">
                        <!-- Width toggle removed - now in kanban column header -->
                        <button class="synergy-icon-btn ${session.is_pinned ? 'pinned' : ''}" title="Pin" onclick="event.stopPropagation(); SynergySidebar.togglePin('${session.session_id}')">
                            <i class="fas fa-thumbtack"></i>
                        </button>
                        <button class="synergy-icon-btn" title="Open Popup" onclick="event.stopPropagation(); SynergySidebar.openInPopup('${session.session_id}')">
                            <i class="fas fa-external-link-alt"></i>
                        </button>
                        <button class="synergy-icon-btn synergy-chevron" title="Expand/Collapse" onclick="event.stopPropagation(); SynergySidebar.toggleCardExpand('${session.session_id}')">
                            <i class="fas fa-chevron-down"></i>
                        </button>
                    </div>
                </div>

                <div class="synergy-row-2">
                    <div class="synergy-description">${this.escapeHtml(desc)}</div>
                </div>

                <div class="synergy-row-3">
                    ${dueDate ? `<div class="synergy-stat" title="Due: ${this.getFormattedDateTime(session.due_date)}"><i class="fas fa-calendar"></i> ${dueDate}</div>` : ''}
                    ${counts.milestones > 0 ? `<div class="synergy-stat" title="${counts.milestones} milestone${counts.milestones > 1 ? 's' : ''} in session"><i class="fas fa-flag-checkered"></i> ${counts.milestones} MS</div>` : ''}
                    ${counts.totalTasks > 0 ? `<div class="synergy-stat" title="${counts.tasksDone} completed out of ${counts.totalTasks} total tasks"><i class="fas fa-tasks"></i> ${counts.tasksDone}/${counts.totalTasks}</div>` : ''}
                    ${counts.docs > 0 ? `<div class="synergy-stat" title="${counts.docs} document${counts.docs > 1 ? 's' : ''} attached"><i class="fas fa-file"></i> ${counts.docs}</div>` : ''}
                    ${counts.links > 0 ? `<div class="synergy-stat" title="${counts.links} external link${counts.links > 1 ? 's' : ''}"><i class="fas fa-link"></i> ${counts.links}</div>` : ''}
                </div>

                <div class="synergy-row-4">
                    <div class="synergy-progress-bar">
                        <div class="synergy-progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <div class="synergy-footer">
                        <div class="synergy-footer-row-1">
                            <span class="synergy-project">${this.escapeHtml(projectName)}</span>
                            <div class="synergy-updated" title="Last updated: ${this.getFormattedDateTime(session.updated_at || session.last_active)}">
                                <i class="fas fa-clock"></i> ${this.getRelativeTime(session.updated_at || session.last_active)}
                            </div>
                        </div>
                        ${tags.length > 0 ? `
                            <div class="synergy-footer-row-2">
                                <div class="synergy-tags">
                                    ${tags.slice(0, 3).map(tag => `<span class="synergy-tag">${this.escapeHtml(tag)}</span>`).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>

            <div class="synergy-card-expanded-content" style="display: none;">
                <div class="loading-placeholder">
                    <i class="fas fa-spinner fa-spin"></i>
                    <div class="loading-text">Loading session details...</div>
                </div>
            </div>
        `;
    }

    /**
     * Load and render full card content (expanded view)
     */
    async loadAndRenderFullCard(sessionId, cardElement) {
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}/milestones`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            if (!data.success) throw new Error(data.error || 'Unknown error');

            const expandedContent = cardElement.querySelector('.synergy-card-expanded-content');
            if (!expandedContent) return;

            expandedContent.innerHTML = this.renderExpandedCardContent(data.session, data.milestones, sessionId);
            expandedContent.style.display = 'block';

            // Load linked threads asynchronously (don't block card rendering)
            setTimeout(() => this.loadLinkedThreads(sessionId), 100);

        } catch (error) {
            console.error('[SYNERGY V2] Error loading card:', error);
            const expandedContent = cardElement.querySelector('.synergy-card-expanded-content');
            if (expandedContent) {
                expandedContent.innerHTML = `
                    <div style="padding: 20px; text-align: center; color: var(--accent-error);">
                        <i class="fas fa-exclamation-triangle"></i>
                        <div>Error loading session: ${error.message}</div>
                    </div>
                `;
                expandedContent.style.display = 'block';
            }
        }
    }

    /**
     * ========================================
     * FLAT EXPANDED CARD CONTENT
     * CRITICAL: 8px container padding ONLY
     * ========================================
     */
    renderExpandedCardContent(session, milestones, sessionId) {
        return `
            <div class="synergy-flat-container" data-session-id="${sessionId}">
                ${this.renderMetadataSection(session)}
                ${this.renderDescriptionSection(session.description)}
                ${this.renderMilestonesSection(milestones, sessionId)}
                ${this.renderDocumentsSection(session.documents, sessionId)}
                ${this.renderLinkedThreadsSection(sessionId)}
                ${this.renderLinksSection(session.links)}
                ${this.renderTagsSection(session.tags)}
            </div>
        `;
    }

    /**
     * METADATA SECTION - FLAT
     * Border-top separator, 8px padding, NO indentation
     */
    renderMetadataSection(session) {
        // Safely parse assignees - handle string, array, or null
        let assignees = session.assignees || [];
        if (typeof assignees === 'string') {
            try {
                assignees = JSON.parse(assignees);
            } catch (e) {
                assignees = [];
            }
        }
        if (!Array.isArray(assignees)) {
            assignees = [];
        }

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
                    <div class="synergy-flat-pill" style="background: ${isOverdue ? '#dc2626' : 'var(--bg-quaternary)'}; color: ${isOverdue ? 'white' : 'var(--text-primary)'};">
                        <i class="fas fa-calendar"></i>
                        ${isOverdue ? 'OVERDUE: ' : 'Due: '}${dueDate.toLocaleDateString()}
                    </div>
                `;
            }
        }

        return `
            <div class="synergy-flat-section">
                <div class="synergy-flat-section-header">
                    <b>Metadata</b>
                </div>
                ${assigneeNames ? `
                    <div style="margin-bottom: 8px;">
                        <div class="synergy-flat-label"><i class="fas fa-users"></i> Assigned to</div>
                        <div class="synergy-flat-value">${this.escapeHtml(assigneeNames)}</div>
                    </div>
                ` : ''}
                ${session.team_id ? `
                    <div style="margin-bottom: 8px;">
                        <div class="synergy-flat-label"><i class="fas fa-users-cog"></i> Team ID</div>
                        <div class="synergy-flat-value">
                            <span class="team-id-tag" 
                                  onclick="event.stopPropagation(); filterByTeamId('${session.team_id}')"
                                  title="Click to filter by Team ID: ${session.team_id}">
                                <i class="fas fa-users"></i>
                                ${this.escapeHtml(session.team_id)}
                            </span>
                        </div>
                    </div>
                ` : ''}
                ${dueDateHTML ? `<div style="margin-bottom: 8px;">${dueDateHTML}</div>` : ''}
                <div class="synergy-flat-stats">
                    <span><i class="fas fa-comments"></i> ${session.message_count || 0} messages</span>
                    <span><i class="fas fa-clock"></i> ${this.formatTimeAgo(session.updated_at)}</span>
                </div>
            </div>
        `;
    }

    /**
     * DESCRIPTION SECTION - FLAT
     */
    renderDescriptionSection(description) {
        const hasDescription = description && description.trim().length > 0;

        return `
            <div class="synergy-flat-section" data-section="description">
                <div class="synergy-flat-section-header">
                    <b>Description</b>
                    <div class="synergy-flat-header-right">
                        <button class="synergy-flat-action-btn synergy-edit-description-btn" title="Edit Description"><i class="fas fa-pen"></i></button>
                    </div>
                </div>
                <div class="synergy-flat-description-container" data-editing="false">
                    ${hasDescription ? `
                        <div class="synergy-flat-description" contenteditable="false" data-field="description">${this.renderMarkdown(description)}</div>
                    ` : `
                        <div class="synergy-flat-description synergy-flat-empty-editable" contenteditable="false" data-field="description" data-placeholder="Click edit to add a description">
                            <i class="fas fa-align-left"></i>
                            <div>No description provided</div>
                        </div>
                    `}
                    <div class="synergy-flat-edit-actions" style="display: none;">
                        <button class="synergy-flat-action-btn synergy-save-description-btn">Save</button>
                        <button class="synergy-flat-action-btn synergy-cancel-description-btn">Cancel</button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * MILESTONES SECTION - FLAT
     * NO nested indentation - all at same level
     * Visual hierarchy via badges: [M1], [T1.1], [S1.1.1]
     * Visual hierarchy via borders: M=3px blue, T=2px gray
     * Visual hierarchy via fonts: 17px → 15px → 14px
     */
    renderMilestonesSection(milestones, sessionId) {
        // ✅ Type guard: Ensure milestones is always an array
        if (!Array.isArray(milestones)) {
            console.warn('[SYNERGY V2] Milestones is not an array, converting:', milestones);
            milestones = [];
        }

        if (!milestones || milestones.length === 0) {
            return `
                <div class="synergy-flat-section">
                    <div class="synergy-flat-section-header">
                        <b>Project milestones</b>
                    </div>
                    <div class="synergy-flat-empty">
                        <i class="fas fa-flag-checkered"></i>
                        <div>No milestones defined</div>
                        <div class="synergy-flat-empty-hint">Add milestones to track progress</div>
                    </div>
                </div>
            `;
        }

        const completedCount = milestones.filter(m => m.completed).length;
        const totalCount = milestones.length;
        const progress = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

        let html = `
            <div class="synergy-flat-section" data-section="milestones">
                <div class="synergy-flat-section-header">
                    <b>Project milestones</b>
                    <span style="font-size: 15px; color: var(--text-secondary);">${completedCount}/${totalCount} (${progress}%)</span>
                    <div class="synergy-flat-header-right">
                        <button class="synergy-flat-action-btn synergy-link-btn" title="Link" onclick="window.synergySidebarRendererV2?.linkSession('${sessionId}', event)"><i class="fas fa-external-link-alt"></i></button>
                        <button class="synergy-flat-action-btn synergy-add-milestone-btn" title="Add Milestone"><i class="fas fa-plus"></i></button>
                    </div>
                </div>
        `;

        milestones.forEach((milestone, mIdx) => {
            html += this.renderMilestone(milestone, mIdx + 1, sessionId);
        });

        html += `</div>`;
        return html;
    }

    /**
     * SINGLE MILESTONE - TWO-ROW STRUCTURE
     * Row 1: Checkbox + Index + Priority + Actions
     * Row 2: Title (full width, 17px, editable)
     */
    renderMilestone(milestone, milestoneNum, sessionId) {
        const tasks = milestone.tasks || [];
        const completedTasks = tasks.filter(t => t.completed).length;
        const taskProgress = tasks.length > 0 ? Math.round((completedTasks / tasks.length) * 100) : 0;
        const isCompleted = milestone.completed;
        const milestoneId = milestone.milestone_id || `temp_${milestoneNum}`;

        return `
            <div class="synergy-flat-milestone" data-milestone-id="${milestoneId}" data-editing="false">
                <!-- ROW 1: Controls -->
                <div class="synergy-flat-milestone-header">
                    <div class="synergy-flat-header-left">
                        <input type="checkbox" ${isCompleted ? 'checked' : ''} class="synergy-flat-checkbox">
                        <span class="synergy-flat-index">M${milestoneNum}</span>
                        <span class="synergy-priority-display">${milestone.priority ? `<span class="priority-badge priority-${milestone.priority}">${milestone.priority.toUpperCase()}</span>` : ''}</span>
                        <select class="synergy-priority-select" data-field="priority" style="display: none;">
                            <option value="low" ${milestone.priority === 'low' ? 'selected' : ''}>Low</option>
                            <option value="medium" ${!milestone.priority || milestone.priority === 'medium' ? 'selected' : ''}>Medium</option>
                            <option value="high" ${milestone.priority === 'high' ? 'selected' : ''}>High</option>
                            <option value="critical" ${milestone.priority === 'critical' ? 'selected' : ''}>Critical</option>
                        </select>
                    </div>
                    <div class="synergy-flat-header-right">
                        <button class="synergy-flat-action-btn synergy-edit-btn" title="Edit"><i class="fas fa-pen"></i></button>
                        <button class="synergy-flat-expand-btn" onclick="window.synergySidebarRendererV2?.toggleMilestone('${milestoneId}', event)" title="Expand/Collapse">
                            <i class="fas fa-chevron-right"></i>
                        </button>
                    </div>
                </div>

                <!-- ROW 2: Task Title (Editable) -->
                <div class="synergy-flat-milestone-title" contenteditable="false" data-field="milestone">
                    ${this.escapeHtml(milestone.milestone || 'Untitled Milestone')}
                </div>

                <!-- Save/Cancel/Delete buttons (hidden by default) -->
                <div class="synergy-flat-edit-actions" style="display: none;">
                    <button class="synergy-flat-action-btn synergy-save-btn" title="Save"><i class="fas fa-save"></i></button>
                    <button class="synergy-flat-action-btn synergy-cancel-btn" title="Cancel"><i class="fas fa-times"></i></button>
                    <button class="synergy-flat-action-btn synergy-delete-btn" title="Delete"><i class="fas fa-trash"></i></button>
                </div>

                <!-- Milestone Description -->
                ${milestone.description ? `
                    <div class="synergy-flat-milestone-desc" contenteditable="false" data-field="description">
                        ${this.escapeHtml(milestone.description)}
                    </div>
                ` : ''}

                <!-- Milestone Metadata -->
                <div class="synergy-flat-milestone-meta">
                    ${milestone.due_date ? `<span><i class="fas fa-calendar"></i> ${new Date(milestone.due_date).toLocaleDateString()}</span>` : ''}
                    ${milestone.estimated_hours ? `<span><i class="fas fa-clock"></i> ${milestone.estimated_hours}h</span>` : ''}
                    ${milestone.assigned_to ? `<span><i class="fas fa-user"></i> ${this.escapeHtml(milestone.assigned_to)}</span>` : ''}
                </div>

                <!-- Collapsible Tasks Section -->
                <div class="synergy-flat-milestone-tasks collapsed">
                    <hr class="synergy-flat-section-divider">
                    
                    <!-- Tasks Header Row: Label + Add Button -->
                    <div class="synergy-flat-section-header">
                        <span class="synergy-flat-section-label">Tasks:</span>
                        <button class="synergy-flat-action-btn synergy-add-task-btn" data-milestone-id="${milestoneId}" title="Add Task">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                    
                    <!-- Progress Bar Row -->
                    ${tasks.length > 0 ? `
                        <div class="synergy-flat-progress-section">
                            <span class="synergy-flat-progress-label">${completedTasks}/${tasks.length} (${taskProgress}%)</span>
                            <div class="synergy-flat-progress-bar">
                                <div class="synergy-flat-progress-fill" style="width: ${taskProgress}%"></div>
                            </div>
                        </div>
                    ` : ''}

                    <!-- Tasks (FLAT - NO INDENT) -->
                    ${tasks.map((task, tIdx) => this.renderTask(task, milestoneNum, tIdx + 1, sessionId)).join('')}
                </div>
            </div>
        `;
    }

    /**
     * SINGLE TASK - TWO-ROW STRUCTURE
     * Row 1: Checkbox + Index + Priority + Actions
     * Row 2: Title (full width, 15px, editable)
     */
    renderTask(task, milestoneNum, taskNum, sessionId) {
        const subtasks = task.subtasks || [];
        const completedSubtasks = subtasks.filter(s => s.completed).length;
        const subtaskProgress = subtasks.length > 0 ? Math.round((completedSubtasks / subtasks.length) * 100) : 0;
        const isBlocked = task.blocked || task.status === 'blocked';
        const isCompleted = task.completed;
        const taskId = task.task_id || `temp_${milestoneNum}_${taskNum}`;

        return `
            <div class="synergy-flat-task" data-task-id="${taskId}" data-editing="false">
                <!-- ROW 1: Controls -->
                <div class="synergy-flat-task-header">
                    <div class="synergy-flat-header-left">
                        <input type="checkbox" ${isCompleted ? 'checked' : ''} ${isBlocked ? 'disabled' : ''} class="synergy-flat-checkbox">
                        <span class="synergy-flat-index">T${milestoneNum}.${taskNum}</span>
                        <span class="synergy-priority-display">${task.priority ? `<span class="priority-badge priority-${task.priority}">${task.priority.toUpperCase()}</span>` : ''}</span>
                        <select class="synergy-priority-select" data-field="priority" style="display: none;">
                            <option value="low" ${task.priority === 'low' ? 'selected' : ''}>Low</option>
                            <option value="medium" ${!task.priority || task.priority === 'medium' ? 'selected' : ''}>Medium</option>
                            <option value="high" ${task.priority === 'high' ? 'selected' : ''}>High</option>
                            <option value="critical" ${task.priority === 'critical' ? 'selected' : ''}>Critical</option>
                        </select>
                        ${isBlocked ? `<span class="synergy-flat-blocked-badge">BLOCKED</span>` : ''}
                    </div>
                    <div class="synergy-flat-header-right">
                        <button class="synergy-flat-action-btn synergy-edit-btn" title="Edit"><i class="fas fa-pen"></i></button>
                        ${subtasks.length > 0 ? `
                            <button class="synergy-flat-expand-btn" onclick="window.synergySidebarRendererV2?.toggleTask('${taskId}', event)" title="Expand/Collapse">
                                <i class="fas fa-chevron-right"></i>
                            </button>
                        ` : ''}
                    </div>
                </div>

                <!-- ROW 2: Title (Editable) -->
                <div class="synergy-flat-task-title" contenteditable="false" data-field="task">
                    ${this.escapeHtml(task.task || 'Untitled Task')}
                </div>

                <!-- Save/Cancel/Delete buttons (hidden by default) -->
                <div class="synergy-flat-edit-actions" style="display: none;">
                    <button class="synergy-flat-action-btn synergy-save-btn" title="Save"><i class="fas fa-save"></i></button>
                    <button class="synergy-flat-action-btn synergy-cancel-btn" title="Cancel"><i class="fas fa-times"></i></button>
                    <button class="synergy-flat-action-btn synergy-delete-btn" title="Delete"><i class="fas fa-trash"></i></button>
                </div>

                <!-- Task Metadata -->
                <div class="synergy-flat-task-meta">
                    ${task.assigned_to ? `<span><i class="fas fa-user"></i> ${this.escapeHtml(task.assigned_to)}</span>` : ''}
                    ${task.estimated_hours ? `<span><i class="fas fa-clock"></i> ${task.estimated_hours}h</span>` : ''}
                    ${task.actual_hours ? `<span><i class="fas fa-stopwatch"></i> ${task.actual_hours}h</span>` : ''}
                </div>

                <!-- Blocker Info -->
                ${isBlocked ? `
                    <div class="synergy-flat-blocker">
                        <div class="synergy-flat-blocker-header">
                            <i class="fas fa-ban"></i> BLOCKED${task.blocker_type ? ` (${task.blocker_type})` : ''}
                        </div>
                        <div>${this.escapeHtml(task.blocker_reason || 'No reason provided')}</div>
                        ${task.blocked_since ? `<div class="synergy-flat-blocker-since">Since: ${this.getFormattedDateTime(task.blocked_since)}</div>` : ''}
                    </div>
                ` : ''}

                <!-- Collapsible Subtasks Section -->
                <div class="synergy-flat-task-subtasks collapsed">
                    <hr class="synergy-flat-section-divider">
                    
                    <!-- Subtasks Header Row: Label + Add Button -->
                    <div class="synergy-flat-section-header">
                        <span class="synergy-flat-section-label">Subtasks:</span>
                        <button class="synergy-flat-action-btn synergy-add-subtask-btn" data-task-id="${taskId}" title="Add Subtask">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                    
                    <!-- Progress Bar Row -->
                    ${subtasks.length > 0 ? `
                        <div class="synergy-flat-progress-section">
                            <span class="synergy-flat-progress-label">${completedSubtasks}/${subtasks.length} (${subtaskProgress}%)</span>
                            <div class="synergy-flat-progress-bar">
                                <div class="synergy-flat-progress-fill" style="width: ${subtaskProgress}%"></div>
                            </div>
                        </div>
                    ` : ''}
                    
                    <!-- Subtasks (FLAT - NO INDENT) -->
                    ${subtasks.map((subtask, sIdx) => this.renderSubtask(subtask, milestoneNum, taskNum, sIdx + 1, sessionId)).join('')}
                </div>
            </div>
        `;
    }

    /**
     * SINGLE SUBTASK - TWO-ROW STRUCTURE
     * Row 1: Checkbox + Index + Priority + Actions
     * Row 2: Title (full width, 14px, editable)
     */
    renderSubtask(subtask, milestoneNum, taskNum, subtaskNum, sessionId) {
        const isCompleted = subtask.completed;
        const subtaskId = subtask.subtask_id || `temp_${milestoneNum}_${taskNum}_${subtaskNum}`;

        return `
            <div class="synergy-flat-subtask" data-subtask-id="${subtaskId}" data-editing="false">
                <!-- ROW 1: Controls -->
                <div class="synergy-flat-subtask-header">
                    <div class="synergy-flat-header-left">
                        <input type="checkbox" ${isCompleted ? 'checked' : ''} class="synergy-flat-checkbox">
                        <span class="synergy-flat-index">S${milestoneNum}.${taskNum}.${subtaskNum}</span>
                    </div>
                    <div class="synergy-flat-header-right">
                        <span class="synergy-priority-display">${subtask.priority ? `<span class="priority-badge priority-${subtask.priority}">${subtask.priority.toUpperCase()}</span>` : ''}</span>
                        <select class="synergy-priority-select" data-field="priority" style="display: none;">
                            <option value="low" ${subtask.priority === 'low' ? 'selected' : ''}>Low</option>
                            <option value="medium" ${!subtask.priority || subtask.priority === 'medium' ? 'selected' : ''}>Medium</option>
                            <option value="high" ${subtask.priority === 'high' ? 'selected' : ''}>High</option>
                            <option value="critical" ${subtask.priority === 'critical' ? 'selected' : ''}>Critical</option>
                        </select>
                        ${subtask.estimated_hours ? `<span class="synergy-flat-subtask-hours">${subtask.estimated_hours}h</span>` : ''}
                        <button class="synergy-flat-action-btn synergy-edit-btn" title="Edit"><i class="fas fa-pen"></i></button>
                        <button class="synergy-flat-action-btn synergy-delete-btn" title="Delete"><i class="fas fa-trash"></i></button>
                    </div>
                </div>

                <!-- ROW 2: Subtask Text (Editable) -->
                <div class="synergy-flat-subtask-title" contenteditable="false" data-field="subtask">
                    ${this.escapeHtml(subtask.subtask || 'Untitled Subtask')}
                </div>

                <!-- Save/Cancel buttons (hidden by default) -->
                <div class="synergy-flat-edit-actions" style="display: none;">
                    <button class="synergy-flat-action-btn synergy-save-btn" title="Save"><i class="fas fa-check"></i></button>
                    <button class="synergy-flat-action-btn synergy-cancel-btn" title="Cancel"><i class="fas fa-times"></i></button>
                </div>
            </div>
        `;
    }

    /**
     * DOCUMENTS SECTION - FLAT
     */
    renderDocumentsSection(documents, sessionId) {
        let docs = this.parseJsonField(documents, []);

        // ✅ Type guard: Ensure docs is always an array
        if (!Array.isArray(docs)) {
            console.warn('[SYNERGY V2] Documents is not an array, converting:', docs);
            docs = [];
        }

        return `
            <div class="synergy-flat-section">
                <div class="synergy-flat-section-header">
                    <b>Documents</b>
                    <span style="font-size: 14px; color: var(--text-secondary);">${docs.length} files</span>
                    <div class="synergy-flat-header-right">
                        <button class="synergy-flat-action-btn synergy-add-document-btn" title="Add Document"><i class="fas fa-plus"></i></button>
                    </div>
                </div>
                ${docs.length > 0 ? `
                    <div class="synergy-flat-docs-list">
                        ${docs.map((doc, idx) => {
            const docId = doc.id || `doc_${idx + 1}`;
            return `
                            <div class="synergy-flat-doc-item" data-doc-id="${docId}" data-session-id="${sessionId}" data-editing="false">
                                <!-- ROW 1: Index + Actions -->
                                <div class="synergy-flat-doc-header">
                                    <span class="synergy-flat-index">PD${idx + 1}</span>
                                    <div class="synergy-flat-header-right">
                                        <button class="synergy-flat-action-btn synergy-edit-doc-btn" title="Edit"><i class="fas fa-pen"></i></button>
                                        <button class="synergy-flat-action-btn synergy-delete-doc-btn" title="Delete"><i class="fas fa-trash"></i></button>
                                        <button class="synergy-flat-action-btn synergy-open-doc-btn" title="Open">🔗</button>
                                    </div>
                                </div>
                                <!-- ROW 2: Filename (Editable) -->
                                <div class="synergy-flat-doc-title" contenteditable="false" data-field="document">
                                    <i class="fas fa-file-alt"></i>
                                    <span>${this.escapeHtml(doc.name || doc.title || 'Untitled')}</span>
                                    ${doc.type ? `<span class="synergy-flat-doc-type">${doc.type}</span>` : ''}
                                </div>
                                <!-- Save/Cancel buttons (hidden by default) -->
                                <div class="synergy-flat-edit-actions" style="display: none;">
                                    <button class="synergy-flat-action-btn synergy-save-doc-btn">Save</button>
                                    <button class="synergy-flat-action-btn synergy-cancel-doc-btn">Cancel</button>
                                </div>
                            </div>
                        `}).join('')}
                    </div>
                ` : `
                    <div class="synergy-flat-empty">
                        <i class="fas fa-file"></i>
                        <div>No documents attached</div>
                        <div class="synergy-flat-empty-hint">Upload documents to share with team</div>
                    </div>
                `}
            </div>
        `;
    }

    /**
     * LINKED THREADS SECTION - FLAT
     * Shows all threads linked to this synergy session
     * Drop zone for drag-and-drop thread linking
     */
    renderLinkedThreadsSection(sessionId) {
        return `
            <div class="synergy-flat-section" data-section="linked-threads" id="synergy-linked-threads-${sessionId}">
                <div class="synergy-flat-section-header">
                    <b>Linked Threads</b>
                    <span style="font-size: 14px; color: var(--text-secondary);" class="linked-threads-count">Loading...</span>
                    <div class="synergy-flat-header-right">
                        <button class="synergy-flat-action-btn synergy-open-thread-history-btn" title="Open Thread History"><i class="fas fa-plus"></i></button>
                    </div>
                </div>
                <div class="synergy-linked-threads-container" data-session-id="${sessionId}">
                    <div class="synergy-flat-loading">
                        <i class="fas fa-spinner fa-spin"></i>
                        <div>Loading linked threads...</div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Load and render linked threads dynamically
     * Called after card expansion and after thread linking
     */
    async loadLinkedThreads(sessionId) {
        console.log('[SYNERGY] 🔄 Loading linked threads for session:', sessionId);

        // Escape session ID for querySelector (handles special chars like &, :, etc.)
        const escapedId = CSS.escape(sessionId);
        console.log('[SYNERGY] 🔍 Escaped ID:', escapedId);

        const container = document.querySelector(`#synergy-linked-threads-${escapedId} .synergy-linked-threads-container`);
        const countSpan = document.querySelector(`#synergy-linked-threads-${escapedId} .linked-threads-count`);

        console.log('[SYNERGY] 🔍 Container found:', !!container);
        console.log('[SYNERGY] 🔍 Count span found:', !!countSpan);

        if (!container) {
            console.error('[SYNERGY] ❌ Linked threads container not found for session', sessionId);
            return;
        }

        try {
            const url = `${this.API_BASE_URL}/api/synergy/${sessionId}/linked-threads`;
            console.log('[SYNERGY] 🌐 Fetching from:', url);

            const response = await fetch(url);
            console.log('[SYNERGY] 📡 Response status:', response.status);

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            console.log('[SYNERGY] 📦 Response data:', data);

            if (!data.success) throw new Error(data.error || 'Unknown error');

            const threads = data.threads || [];

            // Update count
            if (countSpan) {
                countSpan.textContent = `${threads.length} thread${threads.length !== 1 ? 's' : ''}`;
            }

            if (threads.length === 0) {
                container.innerHTML = `
                    <div class="synergy-flat-empty synergy-drop-zone-hint">
                        <i class="fas fa-comments"></i>
                        <div>No linked threads</div>
                        <div class="synergy-flat-empty-hint">
                            Drag and drop a thread card here to link it
                        </div>
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <div class="synergy-linked-threads-list">
                        ${threads.map(thread => `
                            <div class="synergy-linked-thread-card" 
                                 data-thread-id="${thread.thread_id}"
                                 onclick="ThreadManager.switchThread('${thread.thread_id}', '${thread.agent_id}')"
                                 title="Click to open thread in ${thread.agent_id === 'prime' ? 'Prime' : 'Agent ' + thread.agent_id}">
                                <div class="thread-card-header">
                                    <span class="thread-agent-badge ${thread.agent_id === 'prime' ? 'prime-badge' : 'agent-badge'}">
                                        <i class="fas fa-${thread.agent_id === 'prime' ? 'star' : 'robot'}"></i>
                                        ${thread.agent_id === 'prime' ? 'Prime' : 'Agent ' + thread.agent_id}
                                    </span>
                                    <span class="thread-message-count" title="Message count">
                                        <i class="fas fa-comment"></i>
                                        ${thread.message_count || 0}
                                    </span>
                                </div>
                                <div class="thread-card-title">
                                    ${this.escapeHtml(thread.title || 'Untitled Thread')}
                                </div>
                                <div class="thread-card-meta">
                                    <span class="thread-created" title="Created">
                                        <i class="fas fa-clock"></i>
                                        ${this.formatTimeAgo(thread.created_at)}
                                    </span>
                                    ${thread.last_activity ? `
                                        <span class="thread-activity" title="Last activity">
                                            <i class="fas fa-bolt"></i>
                                            ${this.formatTimeAgo(thread.last_activity)}
                                        </span>
                                    ` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
        } catch (error) {
            console.error('[SYNERGY] Error loading linked threads:', error);
            if (countSpan) countSpan.textContent = 'Error';
            container.innerHTML = `
                <div class="synergy-flat-empty" style="color: var(--accent-error);">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div>Error loading threads</div>
                    <div class="synergy-flat-empty-hint">${error.message}</div>
                </div>
            `;
        }
    }

    /**
     * Refresh linked threads section (called after thread linking)
     */
    async refreshLinkedThreadsSection(sessionId) {
        console.log('[SYNERGY] Refreshing linked threads for session', sessionId);
        await this.loadLinkedThreads(sessionId);
    }

    /**
     * LINKS SECTION - FLAT
     */
    renderLinksSection(links) {
        let linkArray = this.parseJsonField(links, []);

        // ✅ Type guard: Ensure linkArray is always an array
        if (!Array.isArray(linkArray)) {
            console.warn('[SYNERGY V2] Links is not an array, converting:', linkArray);
            linkArray = [];
        }

        return `
            <div class="synergy-flat-section" data-section="links">
                <div class="synergy-flat-section-header">
                    <b>Links</b>
                    <span style="font-size: 14px; color: var(--text-secondary);">${linkArray.length} links</span>
                    <div class="synergy-flat-header-right">
                        <button class="synergy-flat-action-btn synergy-add-link-btn" title="Add Link"><i class="fas fa-plus"></i></button>
                    </div>
                </div>
                ${linkArray.length > 0 ? `
                    <div class="synergy-flat-links-list">
                        ${linkArray.map((link, idx) => `
                            <div class="synergy-flat-link-item-wrapper">
                                <a href="${this.escapeHtml(link.url || link)}" target="_blank" class="synergy-flat-link-item">
                                    <i class="fas fa-external-link-alt"></i>
                                    <span>${this.escapeHtml(link.title || link.url || link)}</span>
                                </a>
                                <button class="synergy-flat-action-btn synergy-remove-link-btn" data-link-index="${idx}" title="Remove Link">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                ` : `
                    <div class="synergy-flat-empty">
                        <i class="fas fa-link"></i>
                        <div>No links added</div>
                        <div class="synergy-flat-empty-hint">Click 'Add Link' to add external references</div>
                    </div>
                `}
            </div>
        `;
    }

    /**
     * TAGS SECTION - FLAT
     */
    renderTagsSection(tags) {
        let tagArray = this.parseJsonField(tags, []);

        // ✅ Type guard: Ensure tagArray is always an array
        if (!Array.isArray(tagArray)) {
            console.warn('[SYNERGY V2] Tags is not an array, converting:', tagArray);
            tagArray = [];
        }

        return `
            <div class="synergy-flat-section" data-section="tags">
                <div class="synergy-flat-section-header">
                    <b>Tags</b>
                    <span style="font-size: 14px; color: var(--text-secondary);">${tagArray.length} tags</span>
                    <div class="synergy-flat-header-right">
                        <button class="synergy-flat-action-btn synergy-add-tag-btn" title="Add Tag"><i class="fas fa-plus"></i></button>
                    </div>
                </div>
                ${tagArray.length > 0 ? `
                    <div class="synergy-flat-tags-list">
                        ${tagArray.map(tag => `
                            <span class="synergy-flat-tag-editable">
                                <span class="synergy-flat-tag-text">${this.escapeHtml(tag)}</span>
                                <button class="synergy-flat-tag-remove synergy-remove-tag-btn" data-tag-name="${this.escapeHtml(tag)}" title="Remove Tag">
                                    <i class="fas fa-times"></i>
                                </button>
                            </span>
                        `).join('')}
                    </div>
                ` : `
                    <div class="synergy-flat-empty">
                        <i class="fas fa-tags"></i>
                        <div>No tags</div>
                        <div class="synergy-flat-empty-hint">Click 'Add Tag' to organize this session</div>
                    </div>
                `}
            </div>
        `;
    }

    // ========================================
    // HELPER METHODS (unchanged from V1)
    // ========================================

    calculateSessionCounts(session) {
        const milestones = this.parseJsonField(session.milestones, []);
        let totalTasks = 0;
        let tasksDone = 0;
        let totalSubtasks = 0;
        let subtasksDone = 0;

        milestones.forEach(m => {
            const tasks = m.tasks || [];
            totalTasks += tasks.length;
            tasksDone += tasks.filter(t => t.completed).length;

            tasks.forEach(t => {
                const subtasks = t.subtasks || [];
                totalSubtasks += subtasks.length;
                subtasksDone += subtasks.filter(s => s.completed).length;
            });
        });

        const docs = this.parseJsonField(session.documents, []);
        const links = this.parseJsonField(session.links, []);

        return {
            milestones: milestones.length,
            totalTasks,
            tasksDone,
            totalSubtasks,
            subtasksDone,
            docs: docs.length,
            links: links.length
        };
    }

    parseJsonField(field, defaultValue = []) {
        if (!field) return defaultValue;
        if (Array.isArray(field)) return field;
        if (typeof field === 'string') {
            try {
                let parsed = JSON.parse(field);

                // Handle double-stringified JSON (when data was JSON.stringify'd twice)
                if (typeof parsed === 'string') {
                    try {
                        parsed = JSON.parse(parsed);
                    } catch (e2) {
                        // If second parse fails, keep the first parsed result
                    }
                }

                // ✅ Ensure parsed value is an array if defaultValue is an array
                if (Array.isArray(defaultValue) && !Array.isArray(parsed)) {
                    console.warn('[SYNERGY V2] parseJsonField: Expected array but got', typeof parsed, parsed);
                    return defaultValue;
                }
                return parsed;
            } catch (e) {
                return defaultValue;
            }
        }
        // ✅ If field is an object but not an array, return defaultValue
        if (typeof field === 'object' && !Array.isArray(field)) {
            console.warn('[SYNERGY V2] parseJsonField: Field is object but not array', field);
            return defaultValue;
        }
        return defaultValue;
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Render markdown formatting (simple implementation)
     * Supports: **bold**, *italic*, [links](url), `code`, lists, headers
     */
    renderMarkdown(text) {
        if (!text) return '';

        // Escape HTML first for safety
        let html = this.escapeHtml(text);

        // Headers (# H1, ## H2, etc.)
        html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
        html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

        // Bold **text**
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

        // Italic *text*
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

        // Inline code `code`
        html = html.replace(/`(.+?)`/g, '<code>$1</code>');

        // Links [text](url)
        html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

        // Unordered lists (- item or * item)
        html = html.replace(/^[\-\*] (.+)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

        // Ordered lists (1. item)
        html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

        // Line breaks
        html = html.replace(/\n/g, '<br>');

        return html;
    }

    getRelativeTime(dateString) {
        if (!dateString) return 'Never';
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays}d ago`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
        });
    }

    getFormattedDateTime(dateString) {
        if (!dateString) return 'No date';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        }) + ' at ' + date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }

    formatTimeAgo(dateString) {
        return this.getRelativeTime(dateString);
    }

    /**
     * Toggle Synergy card width (3-stage cycle: 350px → 500px → 700px → 350px)
     * Matches Agent column width toggle pattern with same icon flow
     */
    toggleSynergyCardWidth(sessionId, event) {
        if (event) {
            event.stopPropagation();
            event.preventDefault();
        }

        // Find the session card - ONLY in sidebar context to avoid dashboard conflicts
        const card = document.querySelector(`.synergy-session-item[data-session-id="${sessionId}"][data-context="sidebar"]`);
        if (!card) {
            console.warn(`[Synergy Width Toggle] Card not found in sidebar: ${sessionId}`);
            return;
        }

        // Find the button and icon
        const button = card.querySelector('.synergy-width-toggle-btn');
        const icon = button?.querySelector('i');
        if (!icon) {
            console.warn(`[Synergy Width Toggle] Icon not found for: ${sessionId}`);
            return;
        }

        // Check current state
        const hasWide = card.classList.contains('synergy-wide');
        const hasExtraWide = card.classList.contains('synergy-extra-wide');

        // Cycle through 3 stages
        if (!hasWide && !hasExtraWide) {
            // Stage 1 → Stage 2: 350px → 500px
            card.classList.add('synergy-wide');
            icon.className = 'fas fa-angle-double-right'; // ⏩
            console.log(`[Synergy Width Toggle] ${sessionId}: 350px → 500px`);
            // Fix #3: Persist state
            if (window.SynergySidebar && window.SynergySidebar.setWidthState) {
                window.SynergySidebar.setWidthState(sessionId, 'wide');
            }
        } else if (hasWide && !hasExtraWide) {
            // Stage 2 → Stage 3: 500px → 700px
            card.classList.remove('synergy-wide');
            card.classList.add('synergy-extra-wide');
            icon.className = 'fas fa-chevron-left'; // ◀
            console.log(`[Synergy Width Toggle] ${sessionId}: 500px → 700px`);
            // Fix #3: Persist state
            if (window.SynergySidebar && window.SynergySidebar.setWidthState) {
                window.SynergySidebar.setWidthState(sessionId, 'extra-wide');
            }
        } else {
            // Stage 3 → Stage 1: 700px → 350px
            card.classList.remove('synergy-extra-wide');
            icon.className = 'fas fa-chevron-right'; // ▶
            console.log(`[Synergy Width Toggle] ${sessionId}: 700px → 350px`);
            // Fix #3: Persist state
            if (window.SynergySidebar && window.SynergySidebar.setWidthState) {
                window.SynergySidebar.setWidthState(sessionId, null);
            }
        }
    }

    /**
     * Toggle milestone expand/collapse
     */
    toggleMilestone(milestoneId, event) {
        if (event) {
            event.stopPropagation();
            event.preventDefault();
        }

        console.log('[SYNERGY] toggleMilestone called for:', milestoneId);
        const milestoneEl = document.querySelector(`[data-milestone-id="${milestoneId}"]`);
        if (!milestoneEl) {
            console.error('[SYNERGY] Milestone element not found:', milestoneId);
            return;
        }

        const tasksContainer = milestoneEl.querySelector('.synergy-flat-milestone-tasks');
        const chevron = milestoneEl.querySelector('.synergy-flat-expand-btn i');

        console.log('[SYNERGY] Found:', { tasksContainer: !!tasksContainer, chevron: !!chevron });
        if (!tasksContainer || !chevron) {
            console.error('[SYNERGY] Missing elements - tasksContainer:', !!tasksContainer, 'chevron:', !!chevron);
            return;
        }

        const isCollapsed = tasksContainer.classList.contains('collapsed');

        if (isCollapsed) {
            // Expand
            tasksContainer.classList.remove('collapsed');
            tasksContainer.classList.add('expanded');
            chevron.classList.remove('fa-chevron-right');
            chevron.classList.add('fa-chevron-down');
        } else {
            // Collapse
            tasksContainer.classList.remove('expanded');
            tasksContainer.classList.add('collapsed');
            chevron.classList.remove('fa-chevron-down');
            chevron.classList.add('fa-chevron-right');
        }
    }

    /**
     * Toggle task expand/collapse
     */
    toggleTask(taskId, event) {
        if (event) {
            event.stopPropagation();
            event.preventDefault();
        }

        const taskEl = document.querySelector(`[data-task-id="${taskId}"]`);
        if (!taskEl) return;

        const subtasksContainer = taskEl.querySelector('.synergy-flat-task-subtasks');
        const chevron = taskEl.querySelector('.synergy-flat-expand-btn i');

        if (!subtasksContainer || !chevron) return;

        const isCollapsed = subtasksContainer.classList.contains('collapsed');

        if (isCollapsed) {
            // Expand
            subtasksContainer.classList.remove('collapsed');
            subtasksContainer.classList.add('expanded');
            chevron.classList.remove('fa-chevron-right');
            chevron.classList.add('fa-chevron-down');
        } else {
            // Collapse
            subtasksContainer.classList.remove('expanded');
            subtasksContainer.classList.add('collapsed');
            chevron.classList.remove('fa-chevron-down');
            chevron.classList.add('fa-chevron-right');
        }
    }

    linkSession(sessionId, event) {
        if (event) {
            event.stopPropagation();
            event.preventDefault();
        }

        console.log('[SYNERGY] linkSession called for:', sessionId);

        // Copy session ID to clipboard
        navigator.clipboard.writeText(sessionId).then(() => {
            console.log('[SYNERGY] Session ID copied to clipboard');

            // Show temporary toast notification
            const toast = document.createElement('div');
            toast.style.cssText = 'position: fixed; top: 20px; right: 20px; background: var(--synergy-action); color: white; padding: 12px 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 10000; font-size: 14px;';
            toast.innerHTML = '<i class="fas fa-check"></i> Session ID copied to clipboard';
            document.body.appendChild(toast);

            setTimeout(() => {
                toast.style.transition = 'opacity 0.3s';
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 300);
            }, 2000);
        }).catch(err => {
            console.error('[SYNERGY] Failed to copy session ID:', err);
        });
    }
}

// Export to global scope
console.log('[SYNERGY V2] Exporting to window object...');
window.SynergySidebarRendererV2 = SynergySidebarRendererV2;

// Create GLOBAL SINGLETON instance for onclick handlers
// This allows HTML like: onclick="window.synergySidebarRendererV2.toggleMilestone(...)"
window.synergySidebarRendererV2 = new SynergySidebarRendererV2();
console.log('[SYNERGY V2] ✅ window.SynergySidebarRendererV2 (class) =', typeof window.SynergySidebarRendererV2);
console.log('[SYNERGY V2] ✅ window.synergySidebarRendererV2 (instance) =', typeof window.synergySidebarRendererV2);

// ❌ REMOVED: Do NOT overwrite window.SynergySidebarRenderer
// This breaks popup-modal, inline-edit, and board-init which expect original renderer
// window.SynergySidebarRenderer = SynergySidebarRendererV2;  // DANGEROUS!
console.log('[SYNERGY V2] ⚠️  NOT overwriting window.SynergySidebarRenderer (prevents module crashes)');

console.log('[SYNERGY V2] ========================================');
console.log('[SYNERGY V2] FLAT spacing renderer loaded with GLOBAL INSTANCE');
console.log('[SYNERGY V2] ========================================');
