/**
 * Synergy Card Renderer Module
 * 
 * Handles rendering of Synergy session cards in sidebar and dashboard views
 * Supports current structure: next_steps + checklist
 * 
 * Usage:
 *   const renderer = new SynergyCardRenderer();
 *   const cardHTML = renderer.renderCollapsedCard(sessionData);
 */

class SynergyCardRenderer {
    constructor() {
        this.priorityColors = {
            'critical': '#dc2626',
            'high': '#ef4444',
            'medium': '#fbbf24',
            'low': '#22c55e'
        };
    }

    /**
     * Parse JSON field safely
     */
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
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Create session list item with NEW 4-ROW header structure and collapsed card
     */
    createSessionItem(session, expandedSessions = new Set(), pinnedSessions = new Set()) {
        const item = document.createElement('div');
        item.className = 'synergy-session-item';
        if (expandedSessions.has(session.session_id)) {
            item.classList.add('expanded');
        }
        item.dataset.sessionId = session.session_id;

        const isPinned = pinnedSessions.has(session.session_id);
        const documents = this.parseJsonField(session.documents, []);
        const links = this.parseJsonField(session.links, []);
        const nextSteps = this.parseJsonField(session.next_steps, []);

        // Calculate milestone counts
        let completedMilestones = 0;
        let totalMilestones = 0;
        if (session.uses_milestones && session.milestones) {
            totalMilestones = session.milestones.length;
            completedMilestones = session.milestones.filter(m => m.completed).length;
        } else {
            // Legacy: use next_steps as fallback
            totalMilestones = nextSteps.length;
            completedMilestones = nextSteps.filter(s => s && s.completed).length;
        }

        // Calculate task counts (from all milestones)
        let completedTasks = 0;
        let totalTasks = 0;
        if (session.uses_milestones && session.milestones) {
            session.milestones.forEach(milestone => {
                if (milestone.tasks) {
                    totalTasks += milestone.tasks.length;
                    completedTasks += milestone.tasks.filter(t => t.completed).length;
                }
            });
        }

        // Calculate progress percentage
        const progressPercent = totalTasks > 0
            ? Math.round((completedTasks / totalTasks) * 100)
            : (totalMilestones > 0 ? Math.round((completedMilestones / totalMilestones) * 100) : 0);

        // Get relative time
        const relativeTime = this.getRelativeTime(session.updated_at);

        // Truncate description to 100 characters
        const description = session.description
            ? (session.description.length > 100 ? session.description.substring(0, 100) + '...' : session.description)
            : 'No description';

        // Format tags
        const tags = this.parseJsonField(session.tags, []);
        const tagsHtml = tags.length > 0
            ? tags.slice(0, 3).map(tag => `<span class="synergy-tag">${this.escapeHtml(tag)}</span>`).join('')
            : '';

        item.innerHTML = `
            <div class="synergy-session-header-new" onclick="SynergySidebar.toggleExpand(event, '${session.session_id}')">
                
                <!-- TITLE ROW (separate line) -->
                <div class="synergy-title-row">
                    <div class="synergy-title-text">${this.escapeHtml(session.title)}</div>
                </div>

                <!-- ROW 1: Priority Badge + Status Badge + Actions -->
                <div class="synergy-row-1">
                    <span class="priority-badge priority-${session.priority.toLowerCase()}">${session.priority}</span>
                    <span class="status-badge status-${session.status.toLowerCase().replace(/\s+/g, '-')}">${session.status}</span>
                    
                    <div class="synergy-actions">
                        <button class="synergy-icon-btn ${isPinned ? 'pinned' : ''}" 
                            onclick="event.stopPropagation(); SynergySidebar.togglePin('${session.session_id}')" 
                            title="${isPinned ? 'Unpin' : 'Pin'} session">
                            <i class="fas fa-thumbtack"></i>
                        </button>
                        <button class="synergy-icon-btn" 
                            onclick="event.stopPropagation(); SynergySidebar.openInPopup('${session.session_id}'); return false;" 
                            title="Pop out">
                            <i class="fas fa-external-link-alt"></i>
                        </button>
                        <button class="synergy-icon-btn synergy-chevron">
                            <i class="fas fa-chevron-down"></i>
                        </button>
                    </div>
                </div>

                <!-- ROW 2: Description -->
                <div class="synergy-row-2">
                    <div class="synergy-description">${this.escapeHtml(description)}</div>
                </div>

                <!-- ROW 3: Metadata Stats -->
                <div class="synergy-row-3">
                    ${session.created_at ? `
                    <div class="synergy-stat" title="Created ${new Date(session.created_at).toLocaleDateString()}">
                        <i class="fas fa-clock"></i>
                        <span>Created ${this.getRelativeTime(session.created_at)}</span>
                    </div>
                    ` : ''}
                    ${session.due_date ? `
                    <div class="synergy-stat">
                        <i class="fas fa-calendar-alt"></i>
                        <span>${new Date(session.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                    </div>
                    ` : ''}
                    ${session.completed_at ? `
                    <div class="synergy-stat" title="Completed">
                        <i class="fas fa-check-circle"></i>
                        <span>✅ ${new Date(session.completed_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                    </div>
                    ` : ''}
                    <div class="synergy-stat">
                        <i class="fas fa-flag"></i>
                        <span>${completedMilestones}/${totalMilestones}</span>
                    </div>
                    <div class="synergy-stat">
                        <i class="fas fa-tasks"></i>
                        <span>${completedTasks}/${totalTasks}</span>
                    </div>
                    <div class="synergy-stat">
                        <i class="fas fa-file-alt"></i>
                        <span>${documents.length}</span>
                    </div>
                    <div class="synergy-stat">
                        <i class="fas fa-link"></i>
                        <span>${links.length}</span>
                    </div>
                </div>

                <!-- ROW 4: Progress Bar + Footer -->
                <div class="synergy-row-4">
                    <div class="synergy-progress-bar">
                        <div class="synergy-progress-fill" style="width: ${progressPercent}%"></div>
                    </div>
                    <div class="synergy-footer">
                        <div class="synergy-footer-row-1">
                            <div class="synergy-project">${this.escapeHtml(session.project_name || 'General')}</div>
                            <div class="synergy-updated">${relativeTime}</div>
                        </div>
                        ${session.assignees ? `
                            <div class="synergy-footer-row-2">
                                <div class="synergy-assignees">
                                    <i class="fas fa-users"></i>
                                    ${this.parseJsonField(session.assignees, []).map(assignee => `<span class="synergy-assignee">${this.escapeHtml(assignee)}</span>`).join(', ')}
                                </div>
                            </div>
                        ` : ''}
                        ${session.platforms_involved ? `
                            <div class="synergy-footer-row-2">
                                <div class="synergy-platforms">
                                    <i class="fas fa-tools"></i> ${this.escapeHtml(session.platforms_involved)}
                                </div>
                            </div>
                        ` : ''}
                        ${tagsHtml ? `
                            <div class="synergy-footer-row-2">
                                <div class="synergy-tags">${tagsHtml}</div>
                            </div>
                        ` : ''}
                        ${session.notes ? `
                            <div class="synergy-footer-row-2">
                                <div class="synergy-notes" style="font-size: 12px; color: #666; font-style: italic;">
                                    <i class="fas fa-sticky-note"></i> ${this.escapeHtml(session.notes.length > 100 ? session.notes.substring(0, 100) + '...' : session.notes)}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
            
            <div class="synergy-card-collapsed">
                ${this.renderCollapsedCard(session)}
            </div>
        `;

        return item;
    }

    /**
     * Format timestamp to relative time (e.g., "2h ago", "3d ago")
     */
    getRelativeTime(dateString) {
        if (!dateString) return 'Unknown';

        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 30) return `${diffDays}d ago`;
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }

    /**
     * Render the full collapsed card content
     */
    renderCollapsedCard(session) {
        // Parse JSON fields
        const documents = this.parseJsonField(session.documents, []);
        const links = this.parseJsonField(session.links, []);
        const nextSteps = this.parseJsonField(session.next_steps, []);
        const checklist = this.parseJsonField(session.checklist, []);
        const tags = this.parseJsonField(session.tags, []);
        const assignees = this.parseJsonField(session.assignees, []);

        // Calculate milestone stats
        let completedMilestones = 0;
        let totalMilestones = 0;
        let estimatedHours = 0;

        if (session.uses_milestones && session.milestones) {
            totalMilestones = session.milestones.length;
            completedMilestones = session.milestones.filter(m => m.completed).length;
            estimatedHours = session.milestones
                .filter(m => !m.completed && m.estimated_hours)
                .reduce((sum, m) => sum + parseFloat(m.estimated_hours || 0), 0);
        } else {
            // Legacy: use next_steps + checklist
            const completedSteps = nextSteps.filter(s => s && s.completed).length;
            const totalSteps = nextSteps.length;
            const completedChecklist = checklist.filter(c => c && c.completed).length;
            const totalChecklist = checklist.length;
            totalMilestones = totalSteps + totalChecklist;
            completedMilestones = completedSteps + completedChecklist;
        }

        let html = '';

        // Card Meta (assignees and due date)
        html += this.renderCardMeta(assignees, session.due_date);

        // Card Stats
        html += this.renderCardStats(session.message_count, documents.length, completedMilestones, totalMilestones, estimatedHours);

        // Description
        if (session.description) {
            html += this.renderDescription(session.description);
        }

        // Documents
        html += this.renderDocuments(documents, session.session_id);

        // Links
        html += this.renderLinks(links);

        // Tasks Section (supports both milestone and legacy structures)
        html += this.renderTasksSection(session);

        // Linked Threads
        html += this.renderLinkedThreads(session);

        // Notes
        html += this.renderNotes(session.notes);

        // Activity Log
        html += this.renderActivityLog(session);

        // Tags
        if (tags.length > 0) {
            html += this.renderTags(tags);
        }

        // Popup button
        html += this.renderPopupButton(session.session_id);

        return html;
    }

    renderCardMeta(assignees, dueDate) {
        if (assignees.length === 0 && !dueDate) return '';

        let html = '<div class="card-meta">';

        if (assignees.length > 0) {
            html += `
                <span>
                    👥 Assignees: ${assignees.join(', ')}
                </span>
            `;
        }

        if (dueDate) {
            const dueDateObj = new Date(dueDate);
            const isOverdue = dueDateObj < new Date();
            html += `
                <span style="${isOverdue ? 'color: #dc2626; font-weight: 600;' : ''}">
                    📅 Due Date: ${dueDateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                    ${isOverdue ? ' (OVERDUE)' : ''}
                </span>
            `;
        }

        html += '</div>';
        return html;
    }

    renderCardStats(messageCount, docsCount, completedMilestones, totalMilestones, estimatedHours) {
        return `
            <div class="card-stats">
                <span>💬 Messages: ${messageCount || 0}</span>
                <span>📄 Documents: ${docsCount}</span>
                <span>🎯 Milestones: ${completedMilestones}/${totalMilestones}</span>
                ${estimatedHours ? `<span>⏰ Est. ${estimatedHours} hrs remaining</span>` : ''}
            </div>
        `;
    }

    renderDescription(description) {
        const descriptionHtml = typeof marked !== 'undefined'
            ? marked.parse(description)
            : this.escapeHtml(description).replace(/\n/g, '<br>');

        return `
            <div class="synergy-card-section" style="margin-bottom: 16px;">
                <div class="synergy-card-section-title" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                    <i class="fas fa-align-left"></i>
                    Description
                </div>
                <div class="synergy-card-description" style="font-size: 13px; line-height: 1.6; color: var(--text-primary);">${descriptionHtml}</div>
            </div>
        `;
    }

    renderDocuments(documents, sessionId) {
        let html = `
            <div class="synergy-card-section" style="margin-bottom: 16px;">
                <div class="synergy-card-section-title" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                    <i class="fas fa-file-alt"></i>
                    Documents ${documents.length > 0 ? `(${documents.length})` : ''}
                </div>
                <div style="font-size: 13px;">
        `;

        if (documents.length > 0) {
            html += documents.map((doc, idx) => {
                const displayNumber = idx + 1;
                if (doc.type === 'internal_doc') {
                    return `
                        <div style="display: flex; align-items: center; gap: 8px; padding: 8px; margin-bottom: 4px; background: var(--bg-quaternary); border-radius: 4px; cursor: pointer;"
                            onclick="event.stopPropagation(); window.internalDocsManager.openInternalDocPopup('${doc.doc_id}', '${sessionId}');">
                            <span style="display: inline-flex; align-items: center; justify-content: center; min-width: 28px; height: 22px; background: linear-gradient(135deg, #58a6ff 0%, #4a8fe7 100%); color: white; font-weight: 700; border-radius: 4px; font-size: 10px; padding: 0 6px; white-space: nowrap;">D${displayNumber}</span>
                            <i class="fas fa-${doc.doc_type === 'spreadsheet' ? 'table' : 'file-alt'}" style="color: var(--accent-primary);"></i>
                            <span style="flex: 1;">${this.escapeHtml(doc.title)}</span>
                            <span style="font-size: 11px; color: var(--text-muted);">${doc.doc_type === 'spreadsheet' ? 'Spreadsheet' : 'Document'} v${doc.version || 1}</span>
                        </div>
                    `;
                } else {
                    return `
                        <div style="display: flex; align-items: center; gap: 8px; padding: 8px; margin-bottom: 4px; background: var(--bg-quaternary); border-radius: 4px;">
                            <span style="display: inline-flex; align-items: center; justify-content: center; min-width: 28px; height: 22px; background: linear-gradient(135deg, #58a6ff 0%, #4a8fe7 100%); color: white; font-weight: 700; border-radius: 4px; font-size: 10px; padding: 0 6px;">D${displayNumber}</span>
                            <i class="fas fa-file" style="color: var(--accent-primary);"></i>
                            <span style="flex: 1;">${this.escapeHtml(doc.title || doc.name)}</span>
                            ${doc.url ? `<a href="${this.escapeHtml(doc.url)}" target="_blank" style="color: var(--accent-primary); text-decoration: none;"
                                onclick="event.stopPropagation();">
                                <i class="fas fa-external-link-alt"></i>
                            </a>` : ''}
                        </div>
                    `;
                }
            }).join('');
        } else {
            html += '<div style="opacity: 0.6; font-style: italic; padding: 8px;">No documents added</div>';
        }

        html += '</div></div>';
        return html;
    }

    renderLinks(links) {
        let html = `
            <div class="synergy-card-section" style="margin-bottom: 16px;">
                <div class="synergy-card-section-title" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                    <i class="fas fa-link"></i>
                    Links ${links.length > 0 ? `(${links.length})` : ''}
                </div>
                <div style="font-size: 13px;">
        `;

        if (links.length > 0) {
            html += links.map((link, idx) => {
                const displayNumber = idx + 1;
                return `
                    <div style="display: flex; align-items: center; gap: 8px; padding: 8px; margin-bottom: 4px; background: var(--bg-quaternary); border-radius: 4px;">
                        <span style="display: inline-flex; align-items: center; justify-content: center; min-width: 28px; height: 22px; background: linear-gradient(135deg, #58a6ff 0%, #4a8fe7 100%); color: white; font-weight: 700; border-radius: 4px; font-size: 10px; padding: 0 6px;">L${displayNumber}</span>
                        <i class="fas fa-external-link-alt" style="color: var(--accent-primary);"></i>
                        <a href="${this.escapeHtml(link.url)}" target="_blank" 
                            style="flex: 1; color: var(--accent-primary); text-decoration: none;"
                            onclick="event.stopPropagation();">
                            ${this.escapeHtml(link.title)}
                        </a>
                        <span style="font-size: 11px; color: var(--text-muted);">${link.type || 'external'}</span>
                    </div>
                `;
            }).join('');
        } else {
            html += '<div style="opacity: 0.6; font-style: italic; padding: 8px;">No links added</div>';
        }

        html += '</div></div>';
        return html;
    }

    renderNextSteps(nextSteps, sessionId, completedSteps, totalSteps) {
        let html = `
            <div class="synergy-card-section" style="margin-bottom: 16px;">
                <div class="synergy-card-section-title" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                    <i class="fas fa-tasks"></i>
                    Next Steps ${nextSteps.length > 0 ? `(${completedSteps}/${totalSteps})` : ''}
                </div>
                <div style="font-size: 13px;">
        `;

        if (nextSteps.length > 0) {
            html += nextSteps.map((step, idx) => {
                const displayNumber = idx + 1;
                return `
                    <div style="display: flex; align-items: flex-start; gap: 8px; padding: 8px; margin-bottom: 4px; background: var(--bg-quaternary); border-radius: 4px;">
                        <span style="display: inline-flex; align-items: center; justify-content: center; min-width: 28px; height: 22px; background: linear-gradient(135deg, #58a6ff 0%, #4a8fe7 100%); color: white; font-weight: 700; border-radius: 4px; font-size: 10px; padding: 0 6px;">N${displayNumber}</span>
                        <input type="checkbox" 
                            ${step.completed ? 'checked' : ''}
                            onchange="event.stopPropagation(); window.synergyBoard.toggleStep('${sessionId}', ${idx});"
                            style="margin-top: 3px; cursor: pointer;">
                        <span style="flex: 1; ${step.completed ? 'text-decoration: line-through; opacity: 0.6;' : ''}">
                            ${this.escapeHtml(step.description)}
                        </span>
                        ${step.due_date ? `<span style="font-size: 11px; color: var(--text-muted);"><i class="fas fa-calendar"></i> ${new Date(step.due_date).toLocaleDateString()}</span>` : ''}
                    </div>
                `;
            }).join('');
        } else {
            html += '<div style="opacity: 0.6; font-style: italic; padding: 8px;">No next steps added</div>';
        }

        html += '</div></div>';
        return html;
    }

    renderChecklist(checklist, sessionId, completedChecklist, totalChecklist) {
        let html = `
            <div class="synergy-card-section" style="margin-bottom: 16px;">
                <div class="synergy-card-section-title" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                    <i class="fas fa-check-square"></i>
                    Checklist ${checklist.length > 0 ? `(${completedChecklist}/${totalChecklist})` : ''}
                </div>
                <div style="font-size: 13px;">
        `;

        if (checklist.length > 0) {
            html += checklist.map((item, idx) => {
                const displayNumber = idx + 1;
                const taskText = item.task || item.item || item.text;
                const subtasks = item.subtasks || [];

                let itemHtml = `
                    <div style="display: flex; align-items: flex-start; gap: 8px; padding: 8px; margin-bottom: 4px; background: var(--bg-quaternary); border-radius: 4px;">
                        <span style="display: inline-flex; align-items: center; justify-content: center; min-width: 28px; height: 22px; background: linear-gradient(135deg, #58a6ff 0%, #4a8fe7 100%); color: white; font-weight: 700; border-radius: 4px; font-size: 10px; padding: 0 6px;">C${displayNumber}</span>
                        <input type="checkbox" 
                            ${item.completed ? 'checked' : ''}
                            onchange="event.stopPropagation(); window.synergyBoard.toggleChecklistItem('${sessionId}', ${idx});"
                            style="margin-top: 3px; cursor: pointer;">
                        <span style="flex: 1; ${item.completed ? 'text-decoration: line-through; opacity: 0.6;' : ''}">
                            ${this.escapeHtml(taskText)}
                        </span>
                    </div>
                `;

                if (subtasks.length > 0) {
                    itemHtml += '<div style="margin-left: 32px; margin-top: 4px;">';
                    itemHtml += subtasks.map((subtask, subIdx) => {
                        const subDisplayNumber = `${displayNumber}.${subIdx + 1}`;
                        const subtaskText = subtask.task || subtask.item || subtask.text;
                        return `
                            <div style="display: flex; align-items: flex-start; gap: 6px; padding: 6px 8px; margin-bottom: 2px; background: var(--bg-secondary); border-radius: 4px; font-size: 11px;">
                                <span style="display: inline-block; min-width: 36px; padding: 2px 6px; background: #fafafa; border: 1px solid #e0e0e0; border-radius: 3px; font-family: 'Courier New', monospace; font-size: 9px; color: #666; text-align: center; font-weight: 600;">C${subDisplayNumber}</span>
                                <input type="checkbox" 
                                    ${subtask.completed ? 'checked' : ''}
                                    onchange="event.stopPropagation(); window.synergyBoard.toggleChecklistSubtask('${sessionId}', ${idx}, ${subIdx});"
                                    style="margin-top: 2px; cursor: pointer;">
                                <span style="flex: 1; ${subtask.completed ? 'text-decoration: line-through; opacity: 0.6;' : ''}">
                                    ${this.escapeHtml(subtaskText)}
                                </span>
                            </div>
                        `;
                    }).join('');
                    itemHtml += '</div>';
                }

                return itemHtml;
            }).join('');
        } else {
            html += '<div style="opacity: 0.6; font-style: italic; padding: 8px;">No checklist items added</div>';
        }

        html += '</div></div>';
        return html;
    }

    renderLinkedThreads(session) {
        const threadIds = this.parseJsonField(session.thread_ids, []);
        let html = `
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

        // Load thread info cards asynchronously
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
                        console.warn('[SYNERGY CARD] Failed to load linked threads', err);
                        if (loadingDiv) {
                            loadingDiv.innerHTML = '<div style="opacity: 0.6; font-style: italic; padding: 8px;"><i class="fas fa-exclamation-circle"></i> Failed to load threads</div>';
                        }
                    });
                }
            }, 100);
        }

        return html;
    }

    renderNotes(notes) {
        return `
            <div class="synergy-card-section" style="margin-bottom: 16px;">
                <div class="synergy-card-section-title" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                    <i class="fas fa-sticky-note"></i>
                    Notes
                </div>
                <div style="font-size: 13px;">
                    ${notes ? `<div style="padding: 8px;">${this.escapeHtml(notes)}</div>` : '<div style="opacity: 0.6; font-style: italic; padding: 8px;">No notes added</div>'}
                </div>
            </div>
        `;
    }

    renderActivityLog(session) {
        const recentActivity = this.parseJsonField(session.recent_activity, []);
        let html = `
            <div class="synergy-card-section" style="margin-bottom: 16px;">
                <div class="synergy-card-section-title" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                    <i class="fas fa-history"></i>
                    Activity Log
                </div>
                <div style="font-size: 12px; color: var(--text-secondary);">
        `;

        if (recentActivity.length > 0) {
            html += recentActivity.slice(0, 5).map(activity => `
                <div style="padding: 6px 0; border-bottom: 1px solid var(--border-muted);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span>${this.escapeHtml(activity.action || activity.description || 'Activity')}</span>
                        <span style="font-size: 10px; color: var(--text-muted);">${activity.timestamp ? new Date(activity.timestamp).toLocaleString() : ''}</span>
                    </div>
                </div>
            `).join('');

            if (recentActivity.length > 5) {
                html += `<div style="text-align: center; padding: 8px; color: var(--text-muted); font-size: 11px;">...and ${recentActivity.length - 5} more activities</div>`;
            }
        } else {
            html += '<div style="opacity: 0.6; font-style: italic; padding: 8px;">No activity yet</div>';
        }

        html += '</div></div>';
        return html;
    }

    renderTags(tags) {
        return `
            <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; padding-top: 8px; border-top: 1px solid var(--border-muted);">
                ${tags.map(tag => `
                    <span style="background: var(--accent-primary); color: white; padding: 2px 10px; border-radius: 12px; font-size: 10px; font-weight: 500; display: inline-flex; align-items: center; gap: 4px;">
                        <i class="fas fa-tag" style="font-size: 8px;"></i> ${this.escapeHtml(tag)}
                    </span>
                `).join('')}
            </div>
        `;
    }

    renderPopupButton(sessionId) {
        return `
            <button class="synergy-expand-btn" onclick="event.stopPropagation(); SynergySidebar.openInPopup('${sessionId}'); return false;"
                style="width: 100%; margin-top: 16px; padding: 10px; background: var(--bg-quaternary); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary); cursor: pointer; font-size: 13px; display: flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s;">
                <i class="fas fa-external-link-alt"></i>
                Open in Popup Window
            </button>
        `;
    }

    /**
     * Render tasks section - supports BOTH legacy (next_steps + checklist) and new (milestones)
     * 
     * @param {Object} session - Session object
     * @returns {string} HTML for tasks section
     */
    renderTasksSection(session) {
        // Check if session uses new milestone structure
        if (session.uses_milestones && session.milestones && session.milestones.length > 0) {
            // Use new milestone renderer
            if (window.SynergyMilestoneRenderer) {
                return window.SynergyMilestoneRenderer.renderMilestones(session.milestones, session.session_id);
            }
        }

        // Fallback to legacy rendering (next_steps + checklist)
        const nextSteps = this.parseJsonField(session.next_steps, []);
        const checklist = this.parseJsonField(session.checklist, []);

        const completedSteps = nextSteps.filter(s => s && s.completed).length;
        const totalSteps = nextSteps.length;

        const completedChecklist = checklist.reduce((count, item) => {
            if (item.completed) count++;
            if (item.subtasks) {
                count += item.subtasks.filter(s => s.completed).length;
            }
            return count;
        }, 0);

        const totalChecklist = checklist.reduce((count, item) => {
            count++;
            if (item.subtasks) count += item.subtasks.length;
            return count;
        }, 0);

        let html = '';
        html += this.renderNextSteps(nextSteps, session.session_id, completedSteps, totalSteps);
        html += this.renderChecklist(checklist, session.session_id, completedChecklist, totalChecklist);

        return html;
    }
}

// Export for use in main HTML
if (typeof window !== 'undefined') {
    window.SynergyCardRenderer = SynergyCardRenderer;
}
