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
        item.setAttribute('data-context', 'sidebar');
        if (isPinned) item.classList.add('pinned');
        if (isExpanded) item.classList.add('expanded');

        // Render simple list item (like sync list)
        item.innerHTML = this.renderSimpleListItem(session);

        // If expanded, load and render full content
        if (isExpanded) {
            this.loadAndRenderFullCard(session.session_id, item);
        }

        return item;
    }

    /**
     * Render 4-ROW COLLAPSED CARD
     * NEW STRUCTURE (Nov 2025):
     * - Title row (separate)
     * - ROW 1: Priority + Status + Actions (pin, popup, chevron)
     * - ROW 2: Description (truncated)
     * - ROW 3: Metadata stats (due date, milestones, tasks, files, links)
     * - ROW 4: Progress bar + footer (project, tags, updated)
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

        // Status badge styles
        const statusBadges = {
            'active': { icon: 'check-circle', color: 'var(--accent-success)' },
            'completed': { icon: 'check-circle', color: 'var(--accent-primary)' },
            'blocked': { icon: 'exclamation-triangle', color: 'var(--accent-error)' },
            'paused': { icon: 'pause-circle', color: 'var(--accent-warning)' }
        };
        const statusBadge = statusBadges[status] || statusBadges['active'];

        // Calculate counts and progress
        const counts = this.calculateSessionCounts(session);
        const progress = counts.milestones > 0 ? Math.round((counts.tasksDone / counts.totalTasks) * 100) || 0 : 0;

        return `
            <div class="synergy-session-header-new">
                <!-- TITLE ROW -->
                <div class="synergy-title-row">
                    <div class="synergy-title-text">${this.escapeHtml(title)}</div>
                </div>

                <!-- ROW 1: Priority + Status + Actions -->
                <div class="synergy-row-1">
                    <span class="priority-badge priority-${priority}">${priority.toUpperCase()}</span>
                    <span class="status-badge status-${status}">
                        <i class="fas fa-${statusBadge.icon}"></i> ${status}
                    </span>
                    <div class="synergy-actions">
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

                <!-- ROW 2: Description (truncated) -->
                <div class="synergy-row-2">
                    <div class="synergy-description">${this.escapeHtml(desc)}</div>
                </div>

                <!-- ROW 3: Metadata Stats (IMPROVED with tooltips) -->
                <div class="synergy-row-3">
                    ${dueDate ? `<div class="synergy-stat" title="Due: ${this.getFormattedDateTime(session.due_date)}"><i class="fas fa-calendar"></i> ${dueDate}</div>` : ''}
                    ${counts.milestones > 0 ? `<div class="synergy-stat" title="${counts.milestones} milestone${counts.milestones > 1 ? 's' : ''} in session"><i class="fas fa-flag-checkered"></i> ${counts.milestones} MS</div>` : ''}
                    ${counts.totalTasks > 0 ? `<div class="synergy-stat" title="${counts.tasksDone} completed out of ${counts.totalTasks} total tasks"><i class="fas fa-tasks"></i> ${counts.tasksDone}/${counts.totalTasks}</div>` : ''}
                    ${counts.docs > 0 ? `<div class="synergy-stat" title="${counts.docs} document${counts.docs > 1 ? 's' : ''} attached"><i class="fas fa-file"></i> ${counts.docs}</div>` : ''}
                    ${counts.links > 0 ? `<div class="synergy-stat" title="${counts.links} external link${counts.links > 1 ? 's' : ''}"><i class="fas fa-link"></i> ${counts.links}</div>` : ''}
                </div>

                <!-- ROW 4: Progress Bar + Footer -->
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

            <!-- EXPANDED CONTENT (hidden by default) -->
            <div class="synergy-card-expanded-content" style="display: none;">
                <div class="loading-placeholder">
                    <i class="fas fa-spinner fa-spin"></i>
                    <div class="loading-text">Loading session details...</div>
                </div>
            </div>
        `;
    }

    /**
     * Get relative time string (e.g., "2h ago", "3 days ago")
     * IMPROVED: Better formatting with exact timestamps on hover
     */
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

    /**
     * Format full date/time for display
     * Returns formatted string like "Dec 23, 2025 at 3:45 PM"
     */
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

    /**
     * Calculate counts from session data
     * Returns: { milestones, totalTasks, tasksDone, totalSubtasks, subtasksDone, docs, links }
     */
    calculateSessionCounts(session) {
        const counts = {
            milestones: session.milestone_count || 0,
            totalTasks: session.task_count || 0,
            tasksDone: session.tasks_done || 0,
            totalSubtasks: session.subtask_count || 0,
            subtasksDone: session.subtasks_done || 0,
            docs: 0,
            links: 0
        };

        // Count documents (both internal_docs and documents array)
        if (session.internal_docs_count) {
            counts.docs += session.internal_docs_count;
        }
        if (session.documents) {
            const docs = Array.isArray(session.documents) ? session.documents :
                (typeof session.documents === 'string' ? JSON.parse(session.documents || '[]') : []);
            counts.docs += docs.length;
        }

        // Count links
        if (session.links) {
            const links = Array.isArray(session.links) ? session.links :
                (typeof session.links === 'string' ? JSON.parse(session.links || '[]') : []);
            counts.links = links.length;
        }

        return counts;
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

            const contentArea = itemElement.querySelector('.synergy-card-expanded-content');
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
                        padding: 10px 10px;
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

        // === SECTION 2: DESCRIPTION (ALWAYS SHOW) ===
        html += this.renderDescriptionSection(session.description || '');

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
                padding: 10px;
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                color: white;
                margin-bottom: 16px;
                border-radius: 8px;
                align-items: center;
                justify-content: space-between;
            " data-session-id="${sessionId}">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <i class="fas fa-edit" style="font-size: 20px;"></i>
                    <div>
                        <div style="font-size: 16px;"><b>Edit Mode</b></div>
                        <div style="font-size: 13px; opacity: 0.9;">Make changes below, then click Save</div>
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
                padding: 10px;
                background: var(--bg-quaternary);
                border-radius: 8px;
                margin-bottom: 16px;
                border: 1px solid var(--border-secondary);
            ">
                ${assigneeNames ? `
                    <div style="margin-bottom: 12px;">
                        <div style="font-size: 14px; color: var(--text-primary); margin-bottom: 6px;">
                            <i class="fas fa-users"></i> <b>Assigned To</b>
                        </div>
                        <div style="font-size: 15px; color: var(--text-primary);">
                            ${this.escapeHtml(assigneeNames)}
                        </div>
                    </div>
                ` : ''}
                ${dueDateHTML ? `
                    <div style="margin-bottom: 12px;">
                        ${dueDateHTML}
                    </div>
                ` : ''}
                <div style="display: flex; gap: 16px; font-size: 14px; color: var(--text-secondary);">
                    <span><i class="fas fa-comments"></i> ${session.message_count || 0} messages</span>
                    <span><i class="fas fa-clock"></i> ${this.formatTimeAgo(session.updated_at)}</span>
                </div>
            </div>
        `;
    }

    /**
     * Render description section
     * ALWAYS SHOWS - Including empty state
     */
    renderDescriptionSection(description) {
        const hasDescription = description && description.trim().length > 0;

        return `
            <div style="
                padding: 12px;
                background: var(--bg-tertiary);
                border-left: 4px solid var(--accent-primary);
                border-radius: 4px;
                margin-bottom: 16px;
            ">
                <div style="
                    font-size: 16px; 
                    color: var(--text-primary); 
                    margin-bottom: 12px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                ">
                    <i class="fas fa-align-left" style="color: var(--accent-primary); font-size: 20px;"></i> 
                    <b>DESCRIPTION</b>
                </div>
                ${hasDescription ? `
                    <div class="synergy-description" style="font-size: 14px; line-height: 1.7; color: var(--text-primary); white-space: pre-wrap;">
                        ${this.escapeHtml(description)}
                    </div>
                ` : `
                    <div style="
                        text-align: center;
                        padding: 20px;
                        background: var(--bg-quaternary);
                        border-radius: 6px;
                        border: 2px dashed var(--border-default);
                    ">
                        <i class="fas fa-align-left" style="font-size: 28px; color: var(--text-tertiary); margin-bottom: 8px; display: block;"></i>
                        <div style="color: var(--text-secondary); font-size: 13px; font-weight: 500;">No description provided</div>
                        <div style="color: var(--text-tertiary); font-size: 12px; margin-top: 4px;">Click edit to add a description</div>
                    </div>
                `}
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
                    padding: 10px;
                    background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
                    border-radius: 8px;
                    margin-bottom: 12px;
                ">
                    <div style="color: white; font-size: 16px;">
                        <i class="fas fa-tasks" style="font-size: 20px;"></i> <b>PROJECT MILESTONES</b>
                    </div>
                    <div style="color: white; font-size: 15px;">
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
     * Render single milestone with ALL DATABASE FIELDS
     * Shows: dates, hours, blocking, dependencies, priority, documents, links, comments, history
     */
    renderMilestone(milestone, milestoneNum, sessionId) {
        const tasks = milestone.tasks || [];
        const completedTasks = tasks.filter(t => t.completed).length;
        const taskProgress = tasks.length > 0 ? Math.round((completedTasks / tasks.length) * 100) : 0;

        const isCompleted = milestone.completed;
        const isBlocked = milestone.blocked || false;
        const borderColor = isBlocked ? '#dc2626' : (isCompleted ? '#22c55e' : '#6b7280');
        const bgColor = isBlocked ? 'rgba(220, 38, 38, 0.1)' : (isCompleted ? 'rgba(34, 197, 94, 0.1)' : 'var(--bg-tertiary)');

        // Parse milestone-specific documents/links
        const milestoneDocs = this.parseJsonField(milestone.documents, []);
        const milestoneLinks = this.parseJsonField(milestone.links, []);

        let html = `
            <div style="
                border: 2px solid ${borderColor};
                border-radius: 12px;
                padding: 12px;
                margin-bottom: 16px;
                background: ${bgColor};
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            ">
                <!-- Milestone Header -->
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 12px;
                    padding-bottom: 12px;
                    border-bottom: 1px solid var(--border-secondary);
                ">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap;">
                            <span style="
                                background: ${borderColor};
                                color: white;
                                padding: 4px 10px;
                                border-radius: 6px;
                                font-size: 13px;
                            "><b>M${milestoneNum}</b></span>
                            <span style="font-size: 18px;">${isBlocked ? '🚫' : (isCompleted ? '✅' : '⭕')}</span>
                            <span style="font-size: 17px; color: var(--text-primary);">
                                <b>${this.escapeHtml(milestone.milestone_name || 'Untitled Milestone')}</b>
                            </span>
                            ${milestone.priority ? `
                                <span class="priority-badge priority-${milestone.priority}" style="
                                    padding: 3px 8px;
                                    border-radius: 10px;
                                    font-size: 10px;
                                    font-weight: 700;
                                    text-transform: uppercase;
                                ">
                                    ${milestone.priority}
                                </span>
                            ` : ''}
                        </div>
                        ${milestone.description ? `
                            <div style="font-size: 14px; color: var(--text-primary); margin-left: 10px; line-height: 1.5;">
                                ${this.escapeHtml(milestone.description)}
                            </div>
                        ` : ''}
                        
                        <!-- MILESTONE METADATA: Due Date, Hours, Dates -->
                        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; margin-left: 10px; font-size: 13px;">
                            ${milestone.due_date ? `
                                <span style="background: var(--bg-quaternary); padding: 4px 8px; border-radius: 6px; color: var(--text-secondary);">
                                    <i class="fas fa-calendar"></i> Due: ${this.getFormattedDateTime(milestone.due_date)}
                                </span>
                            ` : ''}
                            ${milestone.estimated_hours ? `
                                <span style="background: var(--bg-quaternary); padding: 4px 8px; border-radius: 6px; color: var(--text-secondary);">
                                    <i class="fas fa-clock"></i> Est: ${milestone.estimated_hours}h
                                </span>
                            ` : ''}
                            ${milestone.actual_hours ? `
                                <span style="background: var(--bg-quaternary); padding: 4px 8px; border-radius: 6px; color: var(--text-secondary);">
                                    <i class="fas fa-stopwatch"></i> Actual: ${milestone.actual_hours}h
                                </span>
                            ` : ''}
                            ${milestone.completed_at ? `
                                <span style="background: #22c55e; padding: 4px 8px; border-radius: 6px; color: white;">
                                    <i class="fas fa-check-circle"></i> Completed: ${this.getFormattedDateTime(milestone.completed_at)}
                                </span>
                            ` : ''}
                        </div>

                        <!-- BLOCKING INFO -->
                        ${isBlocked ? `
                            <div style="
                                background: rgba(220, 38, 38, 0.15);
                                border: 1px solid #dc2626;
                                border-radius: 8px;
                                padding: 10px;
                                margin-top: 10px;
                                margin-left: 10px;
                            ">
                                <div style="color: #dc2626; font-size: 15px; margin-bottom: 4px;">
                                    <i class="fas fa-exclamation-triangle"></i> <b>BLOCKED</b>
                                </div>
                                <div style="font-size: 14px; color: var(--text-primary);">
                                    ${milestone.blocker_reason || 'No reason provided'}
                                </div>
                                ${milestone.blocked_since ? `
                                    <div style="font-size: 13px; color: var(--text-secondary); margin-top: 4px;">
                                        Since: ${this.getFormattedDateTime(milestone.blocked_since)}
                                    </div>
                                ` : ''}
                            </div>
                        ` : ''}

                        <!-- DEPENDENCIES -->
                        ${milestone.depends_on_milestone_id ? `
                            <div style="margin-top: 10px; margin-left: 10px; font-size: 14px; color: var(--text-primary);">
                                <i class="fas fa-link"></i> Depends on: <b>${milestone.depends_on_milestone_id}</b>
                            </div>
                        ` : ''}

                        <!-- MILESTONE DOCUMENTS -->
                        ${milestoneDocs.length > 0 ? `
                            <div style="margin-top: 12px; margin-left: 10px;">
                                <div style="font-size: 16px; color: var(--text-primary); margin-bottom: 8px;">
                                    <i class="fas fa-file-alt" style="font-size: 20px;"></i> <b>MILESTONE DOCUMENTS (${milestoneDocs.length})</b>
                                </div>
                                <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                                    ${milestoneDocs.map(doc => `
                                        <a href="${doc.url || '#'}" target="_blank" style="
                                            background: var(--accent-primary);
                                            color: white;
                                            padding: 4px 8px;
                                            border-radius: 6px;
                                            font-size: 11px;
                                            text-decoration: none;
                                        ">
                                            <i class="fas fa-file"></i> ${this.escapeHtml(doc.title || doc.name || 'Doc')}
                                        </a>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}

                        <!-- MILESTONE LINKS -->
                        ${milestoneLinks.length > 0 ? `
                            <div style="margin-top: 12px; margin-left: 10px;">
                                <div style="font-size: 16px; color: var(--text-primary); margin-bottom: 8px;">
                                    <i class="fas fa-external-link-alt" style="font-size: 20px;"></i> <b>MILESTONE LINKS (${milestoneLinks.length})</b>
                                </div>
                                <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                                    ${milestoneLinks.map(link => `
                                        <a href="${link.url || '#'}" target="_blank" style="
                                            background: #10b981;
                                            color: white;
                                            padding: 4px 8px;
                                            border-radius: 6px;
                                            font-size: 11px;
                                            text-decoration: none;
                                        ">
                                            <i class="fas fa-link"></i> ${this.escapeHtml(link.title || 'Link')}
                                        </a>
                                    `).join('')}
                                </div>
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
                    padding: 10px;
                    margin-bottom: 16px;
                ">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="font-size: 16px; color: var(--text-primary);">
                            <i class="fas fa-list-check" style="font-size: 20px;"></i> <b>TASK PROGRESS</b>
                        </span>
                        <span style="font-size: 15px; color: var(--text-primary);">
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
                    <div style="margin-left: 10px;">
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
     * Render single task with ALL DATABASE FIELDS
     * Shows: blocking info, hours, assignment, dates, priority
     */
    renderTask(task, milestoneNum, taskNum, sessionId) {
        const subtasks = task.subtasks || [];
        const completedSubtasks = subtasks.filter(s => s.completed).length;
        const isBlocked = task.blocked || task.status === 'blocked';
        const isCompleted = task.completed;

        const taskColor = isBlocked ? '#ef4444' : (isCompleted ? '#22c55e' : '#6b7280');

        let html = `
            <div class="synergy-task-item-wrapper" style="
                border-left: 3px solid ${taskColor};
                padding: 8px 12px;
                margin-bottom: 12px;
                background: var(--bg-quaternary);
                border-radius: 6px;
            ">
                <!-- Task Header -->
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap;">
                            <span style="
                                background: ${taskColor};
                                color: white;
                                padding: 3px 8px;
                                border-radius: 4px;
                                font-size: 13px;
                            "><b>T${milestoneNum}.${taskNum}</b></span>
                            ${task.priority ? `
                                <span class="priority-badge priority-${task.priority}" style="
                                    padding: 2px 6px;
                                    border-radius: 8px;
                                    font-size: 9px;
                                    font-weight: 700;
                                    text-transform: uppercase;
                                ">
                                    ${task.priority}
                                </span>
                            ` : ''}
                            ${isBlocked ? `
                                <span style="
                                    background: #ef4444;
                                    color: white;
                                    padding: 2px 8px;
                                    border-radius: 4px;
                                    font-size: 13px;
                                "><b>🚫 BLOCKED</b></span>
                            ` : ''}
                            <span style="font-size: 14px;">${isCompleted ? '✅' : '⭕'}</span>
                            <span style="font-size: 15px; color: var(--text-primary);">
                                ${this.escapeHtml(task.task || 'Untitled Task')}
                            </span>
                        </div>

                        <!-- TASK METADATA: Assignment, Hours, Dates -->
                        <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-left: 10px; font-size: 13px;">
                            ${task.assigned_to ? `
                                <span style="background: var(--accent-primary); color: white; padding: 3px 8px; border-radius: 6px;">
                                    <i class="fas fa-user"></i> ${this.escapeHtml(task.assigned_to)}
                                </span>
                            ` : ''}
                            ${task.estimated_hours ? `
                                <span style="background: var(--bg-primary); padding: 3px 8px; border-radius: 6px; color: var(--text-secondary);">
                                    <i class="fas fa-clock"></i> Est: ${task.estimated_hours}h
                                </span>
                            ` : ''}
                            ${task.actual_hours ? `
                                <span style="background: var(--bg-primary); padding: 3px 8px; border-radius: 6px; color: var(--text-secondary);">
                                    <i class="fas fa-stopwatch"></i> Actual: ${task.actual_hours}h
                                </span>
                            ` : ''}
                            ${task.completed_at ? `
                                <span style="background: #22c55e; padding: 3px 8px; border-radius: 6px; color: white;">
                                    <i class="fas fa-check"></i> ${this.getFormattedDateTime(task.completed_at)}
                                </span>
                            ` : ''}
                        </div>
                    </div>
                    <label style="cursor: pointer; flex-shrink: 0;">
                        <input type="checkbox"
                            ${isCompleted ? 'checked' : ''}
                            ${isBlocked ? 'disabled' : ''}
                            data-task-id="${task.task_id}"
                            data-session-id="${sessionId}"
                            class="task-checkbox"
                            style="width: 18px; height: 18px; cursor: ${isBlocked ? 'not-allowed' : 'pointer'};">
                    </label>
                </div>

                <!-- BLOCKING INFO (Enhanced) -->
                ${isBlocked ? `
                    <div style="
                        margin: 0 0 10px 10px;
                        padding: 8px 12px;
                        background: rgba(239, 68, 68, 0.15);
                        border: 1px solid #ef4444;
                        border-left: 4px solid #ef4444;
                        border-radius: 6px;
                        font-size: 12px;
                    ">
                        <div style="color: #ef4444; font-size: 15px; margin-bottom: 4px;">
                            <i class="fas fa-ban"></i> <b>BLOCKED</b>
                            ${task.blocker_type ? `<span style="font-size: 13px; opacity: 0.8;"> (${task.blocker_type})</span>` : ''}
                        </div>
                        <div style="color: var(--text-primary); font-size: 14px;">
                            ${this.escapeHtml(task.blocker_reason || 'No reason provided')}
                        </div>
                        ${task.blocked_since ? `
                            <div style="font-size: 13px; color: var(--text-secondary); margin-top: 4px;">
                                Since: ${this.getFormattedDateTime(task.blocked_since)}
                            </div>
                        ` : ''}
                    </div>
                ` : ''}

                <!-- Subtasks -->
                ${subtasks.length > 0 ? `
                    <div style="padding: 0 10px; margin-top: 8px;">
                        <div style="font-size: 16px; color: var(--text-primary); margin-bottom: 8px;">
                            <i class="fas fa-list" style="font-size: 20px;"></i> <b>SUBTASKS (${completedSubtasks}/${subtasks.length})</b>
                        </div>
                        ${subtasks.map((subtask, sIdx) => this.renderSubtask(subtask, milestoneNum, taskNum, sIdx + 1, sessionId)).join('')}
                    </div>
                ` : ''}
            </div>
        `;

        return html;
    }

    /**
     * Render single subtask with ALL DATABASE FIELDS
     * Shows: priority, hours, completion date
     */
    renderSubtask(subtask, milestoneNum, taskNum, subtaskNum, sessionId) {
        const isCompleted = subtask.completed;

        return `
            <div style="
                padding: 8px 12px;
                margin-bottom: 6px;
                background: var(--bg-tertiary);
                border-radius: 6px;
                border-left: 3px solid ${isCompleted ? '#22c55e' : '#6b7280'};
            ">
                <div style="display: flex; align-items: flex-start; gap: 8px;">
                    <label style="cursor: pointer; display: flex; align-items: center; gap: 8px; flex: 1;">
                        <input type="checkbox"
                            ${isCompleted ? 'checked' : ''}
                            data-subtask-id="${subtask.subtask_id}"
                            data-session-id="${sessionId}"
                            class="subtask-checkbox"
                            style="width: 16px; height: 16px; cursor: pointer; flex-shrink: 0;">
                        <div style="flex: 1;">
                            <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 4px;">
                                <span style="
                                    background: ${isCompleted ? '#22c55e' : '#6b7280'};
                                    color: white;
                                    padding: 2px 6px;
                                    border-radius: 3px;
                                    font-size: 11px;
                                "><b>S${milestoneNum}.${taskNum}.${subtaskNum}</b></span>
                                ${subtask.priority ? `
                                    <span class="priority-badge priority-${subtask.priority}" style="
                                        padding: 2px 5px;
                                        border-radius: 6px;
                                        font-size: 8px;
                                        font-weight: 700;
                                        text-transform: uppercase;
                                    ">
                                        ${subtask.priority}
                                    </span>
                                ` : ''}
                                <span style="
                                    font-size: 14px;
                                    color: var(--text-primary);
                                    ${isCompleted ? 'text-decoration: line-through; opacity: 0.7;' : ''}
                                ">
                                    ${this.escapeHtml(subtask.task || 'Untitled Subtask')}
                                </span>
                            </div>
                            
                            <!-- SUBTASK METADATA: Hours, Dates -->
                            ${(subtask.estimated_hours || subtask.actual_hours || subtask.completed_at || subtask.created_at || subtask.updated_at) ? `
                                <div style="display: flex; flex-wrap: wrap; gap: 4px; font-size: 12px; margin-left: 20px;">
                                    ${subtask.estimated_hours ? `
                                        <span style="background: var(--bg-quaternary); padding: 2px 6px; border-radius: 4px; color: var(--text-secondary);">
                                            <i class="fas fa-clock"></i> Est: ${subtask.estimated_hours}h
                                        </span>
                                    ` : ''}
                                    ${subtask.actual_hours ? `
                                        <span style="background: var(--bg-quaternary); padding: 2px 6px; border-radius: 4px; color: var(--text-secondary);">
                                            <i class="fas fa-stopwatch"></i> Actual: ${subtask.actual_hours}h
                                        </span>
                                    ` : ''}
                                    ${subtask.completed_at ? `
                                        <span style="background: #22c55e; padding: 2px 6px; border-radius: 4px; color: white;">
                                            <i class="fas fa-check"></i> ${this.getFormattedDateTime(subtask.completed_at)}
                                        </span>
                                    ` : ''}
                                    ${subtask.created_at ? `
                                        <span style="background: var(--bg-quaternary); padding: 2px 6px; border-radius: 4px; color: var(--text-secondary);">
                                            Created: ${this.getFormattedDateTime(subtask.created_at)}
                                        </span>
                                    ` : ''}
                                    ${subtask.updated_at && subtask.updated_at !== subtask.created_at ? `
                                        <span style="background: var(--bg-quaternary); padding: 2px 6px; border-radius: 4px; color: var(--text-secondary);">
                                            Updated: ${this.getFormattedDateTime(subtask.updated_at)}
                                        </span>
                                    ` : ''}
                                </div>
                            ` : ''}
                        </div>
                    </label>
                </div>
            </div>
        `;
    }

    /**
     * Render documents section
     * ALWAYS SHOWS - Including empty state
     */
    renderDocumentsSection(documents) {
        const docs = this.parseJsonField(documents, []);

        let html = `
            <div style="
                padding: 12px;
                background: var(--bg-tertiary);
                border-radius: 8px;
                margin-bottom: 16px;
                border: 1px solid var(--border-secondary);
            ">
                <div style="
                    font-size: 16px; 
                    color: var(--text-primary); 
                    margin-bottom: 12px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                ">
                    <i class="fas fa-file-alt" style="color: var(--accent-primary); font-size: 20px;"></i> 
                    <b>DOCUMENTS</b> 
                    <span style="
                        background: var(--bg-quaternary);
                        color: var(--text-secondary);
                        padding: 2px 8px;
                        border-radius: 10px;
                        font-size: 13px;
                    ">${docs.length}</span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px;">
        `;

        if (docs.length === 0) {
            html += `
                <div style="
                    text-align: center;
                    padding: 24px;
                    background: var(--bg-quaternary);
                    border-radius: 6px;
                    border: 2px dashed var(--border-default);
                ">
                    <i class="fas fa-file-alt" style="font-size: 32px; color: var(--text-tertiary); margin-bottom: 8px; display: block;"></i>
                    <div style="color: var(--text-secondary); font-size: 13px; font-weight: 500;">No documents attached yet</div>
                    <div style="color: var(--text-tertiary); font-size: 12px; margin-top: 4px;">Click edit to add documents</div>
                </div>
            `;
        } else {
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
                            <div style="font-size: 14px; color: var(--text-primary);">
                                <b>${this.escapeHtml(doc.title || doc.name || 'Untitled Document')}</b>
                            </div>
                            ${doc.doc_type ? `
                                <div style="font-size: 13px; color: var(--text-secondary);">
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
        }

        html += `
                </div>
            </div>
        `;

        return html;
    }

    /**
     * Render links section
     * ALWAYS SHOWS - Including empty state
     */
    renderLinksSection(links) {
        const linkList = this.parseJsonField(links, []);

        let html = `
            <div style="
                padding: 12px;
                background: var(--bg-tertiary);
                border-radius: 8px;
                margin-bottom: 16px;
                border: 1px solid var(--border-secondary);
            ">
                <div style="
                    font-size: 16px; 
                    color: var(--text-primary); 
                    margin-bottom: 12px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                ">
                    <i class="fas fa-link" style="color: var(--accent-primary); font-size: 20px;"></i> 
                    <b>EXTERNAL LINKS</b> 
                    <span style="
                        background: var(--bg-quaternary);
                        color: var(--text-secondary);
                        padding: 2px 8px;
                        border-radius: 10px;
                        font-size: 13px;
                    ">${linkList.length}</span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px;">
        `;

        if (linkList.length === 0) {
            html += `
                <div style="
                    text-align: center;
                    padding: 24px;
                    background: var(--bg-quaternary);
                    border-radius: 6px;
                    border: 2px dashed var(--border-default);
                ">
                    <i class="fas fa-link" style="font-size: 32px; color: var(--text-tertiary); margin-bottom: 8px; display: block;"></i>
                    <div style="color: var(--text-secondary); font-size: 13px; font-weight: 500;">No external links yet</div>
                    <div style="color: var(--text-tertiary); font-size: 12px; margin-top: 4px;">Click edit to add links</div>
                </div>
            `;
        } else {
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
                            font-size: 14px;
                            color: var(--accent-primary);
                            text-decoration: none;
                        ">
                            <b>${this.escapeHtml(link.title || link.url)}</b>
                        </a>
                        ${link.type ? `
                            <span style="
                                background: var(--bg-tertiary);
                                color: var(--text-secondary);
                                padding: 4px 8px;
                                border-radius: 4px;
                                font-size: 13px;
                            ">${link.type}</span>
                        ` : ''}
                    </div>
                `;
            });
        }

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
