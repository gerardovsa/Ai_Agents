/**
 * FILE: UI/external/modules/synergy-milestone-renderer.js
 * PURPOSE: Renders milestone-based task hierarchy (milestone → task → subtask)
 * 
 * DEPENDENCIES:
 * - synergy-milestone-interactions.js (completion handlers)
 * - synergy-milestone-styles.css (styling)
 * 
 * EXPORTS:
 * - SynergyMilestoneRenderer class with renderMilestones() method
 * 
 * USED BY:
 * - synergy-card-renderer.js (integrated into card rendering)
 * 
 * NOTES:
 * - Replaces legacy renderNextSteps() + renderChecklist() methods
 * - Supports hierarchical expansion/collapse
 * - Auto-completion cascade (subtask → task → milestone)
 * - Progress percentage calculation
 * 
 * LAST MODIFIED: 2025-11-19 - Initial creation
 */

class SynergyMilestoneRenderer {
    constructor() {
        // Track expansion state
        this.expandedMilestones = new Set();
        this.expandedTasks = new Set();

        // Priority colors
        this.priorityColors = {
            'critical': '#dc2626',
            'high': '#ef4444',
            'medium': '#fbbf24',
            'low': '#22c55e'
        };
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
     * Get priority badge HTML
     */
    getPriorityBadge(priority) {
        if (!priority || priority === 'medium') return ''; // Don't show badge for default priority

        const badges = {
            'critical': '<span class="priority-badge priority-critical" title="Critical Priority">🔴 CRITICAL</span>',
            'high': '<span class="priority-badge priority-high" title="High Priority">🟠 HIGH</span>',
            'low': '<span class="priority-badge priority-low" title="Low Priority">🟢 LOW</span>'
        };

        return badges[priority] || '';
    }

    /**
     * Main render method - replaces renderNextSteps() + renderChecklist()
     * 
     * @param {Array} milestones - Array of milestone objects with tasks and subtasks
     * @param {string} sessionId - Session ID for event handlers
     * @returns {string} HTML string for milestones section
     */
    renderMilestones(milestones, sessionId) {
        if (!milestones || milestones.length === 0) {
            return `
                <div class="synergy-card-section milestones-section">
                    <div class="synergy-card-section-title">
                        <i class="fas fa-bullseye"></i>
                        Milestones
                    </div>
                    <div style="opacity: 0.6; font-style: italic; padding: 8px; font-size: 13px;">
                        No milestones added yet
                    </div>
                </div>
            `;
        }

        // Calculate totals
        const completedCount = milestones.filter(m => m.completed).length;
        const totalCount = milestones.length;

        let html = `
            <div class="synergy-card-section milestones-section">
                <div class="synergy-card-section-title">
                    <i class="fas fa-bullseye"></i>
                    Milestones (${completedCount}/${totalCount})
                </div>
                <div class="milestones-container">
        `;

        milestones.forEach(milestone => {
            html += this.renderMilestone(milestone, sessionId);
        });

        html += `
                </div>
            </div>
        `;

        return html;
    }

    /**
     * Render single milestone with header and collapsible body
     */
    renderMilestone(milestone, sessionId) {
        const progress = this.calculateMilestoneProgress(milestone);
        const isExpanded = this.isMilestoneExpanded(milestone.milestone_id);
        const expandIcon = isExpanded ? 'fa-chevron-down' : 'fa-chevron-right';

        // Determine milestone status color
        let statusColor = '#3b82f6'; // Default blue
        if (milestone.completed) {
            statusColor = '#22c55e'; // Green
        } else if (progress > 50) {
            statusColor = '#2563eb'; // Darker blue (in progress)
        }

        return `
            <div class="milestone-item ${milestone.completed ? 'completed' : ''}" 
                 data-milestone-id="${milestone.milestone_id}">
                
                <!-- Milestone Header -->
                <div class="milestone-header" 
                     style="background: linear-gradient(135deg, ${statusColor} 0%, ${this.darkenColor(statusColor)} 100%);"
                     onclick="SynergyMilestoneInteractions.toggleMilestone('${milestone.milestone_id}', event)">
                    
                    <button class="milestone-expand-btn">
                        <i class="fas ${expandIcon}"></i>
                    </button>
                    
                    <span class="milestone-number">M${milestone.milestone_number}</span>
                    
                    <input type="checkbox" 
                           ${milestone.completed ? 'checked' : ''}
                           ${milestone.blocked ? 'disabled' : ''}
                           onclick="event.stopPropagation(); SynergyMilestoneInteractions.completeMilestone('${sessionId}', '${milestone.milestone_id}')" />
                    
                    <span class="milestone-name">${this.escapeHtml(milestone.title || milestone.milestone_name)}</span>
                    
                    ${this.getPriorityBadge(milestone.priority)}
                    
                    ${milestone.blocked ? `
                        <span class="blocker-badge" title="${this.escapeHtml(milestone.blocker_reason || 'Blocked')}">
                            <i class="fas fa-ban"></i> BLOCKED
                            ${milestone.blocked_since ? ` (${new Date(milestone.blocked_since).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })})` : ''}
                        </span>
                    ` : ''}
                    
                    <span class="milestone-progress">${milestone.completed ? '✅ ' : ''}${progress}%</span>
                    
                    ${milestone.start_date && !milestone.completed ? `
                        <span class="milestone-start">
                            🚀 Started ${new Date(milestone.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                        </span>
                    ` : ''}
                    
                    ${milestone.due_date ? `
                        <span class="milestone-due">
                            📅 Due ${new Date(milestone.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                        </span>
                    ` : ''}
                    
                    ${milestone.completed_at ? `
                        <span class="milestone-completed-at">
                            ✅ Completed ${new Date(milestone.completed_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                        </span>
                    ` : ''}
                    
                    ${milestone.estimated_hours || milestone.actual_hours ? `
                        <span class="milestone-hours">
                            ⏱️ ${milestone.actual_hours ? `${milestone.actual_hours}h` : ''}${milestone.estimated_hours && milestone.actual_hours ? '/' : ''}${milestone.estimated_hours ? `${milestone.estimated_hours}h` : ''}
                        </span>
                    ` : ''}
                    
                    ${milestone.predicted_completion && !milestone.completed ? `
                        <span class="milestone-prediction">
                            📅 Est. ${new Date(milestone.predicted_completion).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                            ${milestone.prediction_confidence ? ` (${milestone.prediction_confidence}% confident)` : ''}
                        </span>
                    ` : ''}
                    
                    ${milestone.depends_on_milestone_id && !milestone.completed ? `
                        <span class="milestone-depends">
                            ⛓️ Depends on M${milestone.depends_on_number || '?'}
                        </span>
                    ` : ''}
                </div>
                
                <!-- Milestone Body (collapsible) -->
                <div class="milestone-body ${isExpanded ? 'expanded' : 'collapsed'}">
                    ${milestone.description ? `
                        <div class="milestone-description">
                            ${this.escapeHtml(milestone.description)}
                        </div>
                    ` : ''}
                    
                    ${milestone.tags ? `
                        <div class="milestone-tags">
                            ${JSON.parse(milestone.tags).map(tag => `<span class="milestone-tag">${this.escapeHtml(tag)}</span>`).join('')}
                        </div>
                    ` : ''}
                    
                    <!-- Tasks -->
                    <div class="milestone-tasks">
                        ${milestone.tasks && milestone.tasks.length > 0
                ? milestone.tasks.map(task => this.renderTask(task, milestone, sessionId)).join('')
                : '<div style="opacity: 0.6; font-style: italic; padding: 8px; font-size: 12px;">No tasks added yet</div>'
            }
                    </div>
                    
                    <!-- Documents & Links -->
                    ${this.renderMilestoneDocuments(milestone, milestone.milestone_number)}
                    ${this.renderMilestoneLinks(milestone, milestone.milestone_number)}
                    
                    <!-- Milestone Footer -->
                    ${this.renderMilestoneFooter(milestone, sessionId)}
                </div>
            </div>
        `;
    }

    /**
     * Render single task with optional subtasks
     */
    renderTask(task, milestone, sessionId) {
        const hasSubtasks = task.subtasks && task.subtasks.length > 0;
        const isExpanded = hasSubtasks && this.isTaskExpanded(task.task_id);
        const expandIcon = isExpanded ? 'fa-chevron-down' : 'fa-chevron-right';

        return `
            <div class="task-item ${task.completed ? 'completed' : ''} ${task.blocked ? 'blocked' : ''}"
                 data-task-id="${task.task_id}">
                
                ${hasSubtasks ? `
                    <button class="task-expand-btn" 
                            onclick="event.stopPropagation(); SynergyMilestoneInteractions.toggleTask('${task.task_id}', event)">
                        <i class="fas ${expandIcon}"></i>
                    </button>
                ` : '<span style="width: 20px;"></span>'}
                
                <span class="task-number">T${milestone.milestone_number}.${task.task_order}</span>
                
                <input type="checkbox" 
                       ${task.completed ? 'checked' : ''}
                       ${task.blocked ? 'disabled' : ''}
                       onclick="SynergyMilestoneInteractions.completeTask('${sessionId}', '${task.task_id}')" />
                
                <span class="task-name ${task.completed ? 'task-completed' : ''}">
                    ${this.escapeHtml(task.title || task.task)}
                </span>
                
                ${this.getPriorityBadge(task.priority)}
                
                ${task.assigned_to ? `
                    <span class="task-assignee" title="Assigned to ${this.escapeHtml(task.assigned_to)}">
                        <i class="fas fa-user"></i> ${this.escapeHtml(task.assigned_to)}
                    </span>
                ` : ''}
                
                ${task.due_date ? `
                    <span class="task-due" title="Due date">
                        📅 ${new Date(task.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </span>
                ` : ''}
                
                ${task.estimated_hours || task.actual_hours ? `
                    <span class="task-hours" title="${task.actual_hours ? 'Actual' : 'Estimated'} hours">
                        ⏱️ ${task.actual_hours || task.estimated_hours}h
                    </span>
                ` : ''}
                
                ${task.blocked ? `
                    <span class="blocker-badge" title="${this.escapeHtml(task.blocker_reason)}">
                        <i class="fas fa-exclamation-triangle"></i> BLOCKED
                        ${task.blocker_type ? `<span class="blocker-type">${task.blocker_type}</span>` : ''}
                        ${task.blocked_since ? ` (${new Date(task.blocked_since).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })})` : ''}
                    </span>
                ` : ''}
                
                ${task.description ? `
                    <div class="task-description" style="grid-column: 3 / -1; padding-left: 40px; font-size: 12px; color: #666; margin-top: 4px;">
                        ${this.escapeHtml(task.description)}
                    </div>
                ` : ''}
                
                ${task.tags ? `
                    <div class="task-tags" style="grid-column: 3 / -1; padding-left: 40px; margin-top: 4px;">
                        ${JSON.parse(task.tags).map(tag => `<span class="task-tag" style="font-size: 10px; padding: 2px 6px; background: #e5e7eb; border-radius: 3px; margin-right: 4px;">${this.escapeHtml(tag)}</span>`).join('')}
                    </div>
                ` : ''}
                
                <!-- Subtasks (collapsible) -->
                ${hasSubtasks ? `
                    <div class="task-subtasks ${isExpanded ? 'expanded' : 'collapsed'}">
                        ${task.subtasks.map(subtask =>
            this.renderSubtask(subtask, task, milestone, sessionId)
        ).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Render single subtask
     */
    renderSubtask(subtask, task, milestone, sessionId) {
        return `
            <div class="subtask-item ${subtask.completed ? 'completed' : ''}"
                 data-subtask-id="${subtask.subtask_id}">
                
                <span class="subtask-number">S${milestone.milestone_number}.${task.task_order}.${subtask.subtask_order}</span>
                
                <input type="checkbox" 
                       ${subtask.completed ? 'checked' : ''}
                       onclick="SynergyMilestoneInteractions.completeSubtask('${sessionId}', '${subtask.subtask_id}')" />
                
                <span class="subtask-name ${subtask.completed ? 'subtask-completed' : ''}">
                    ${this.escapeHtml(subtask.title || subtask.task)}
                </span>
                
                ${this.getPriorityBadge(subtask.priority)}
                
                ${subtask.assigned_to ? `
                    <span class="subtask-assignee" title="Assigned to ${this.escapeHtml(subtask.assigned_to)}">
                        <i class="fas fa-user"></i> ${this.escapeHtml(subtask.assigned_to)}
                    </span>
                ` : ''}
                
                ${subtask.due_date ? `
                    <span class="subtask-due" title="Due date">
                        📅 ${new Date(subtask.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </span>
                ` : ''}
                
                ${subtask.estimated_hours || subtask.actual_hours ? `
                    <span class="subtask-hours" title="${subtask.actual_hours ? 'Actual' : 'Estimated'} hours">
                        ⏱️ ${subtask.actual_hours || subtask.estimated_hours}h
                    </span>
                ` : ''}
                
                ${subtask.description ? `
                    <div class="subtask-description" style="grid-column: 3 / -1; padding-left: 60px; font-size: 11px; color: #666; margin-top: 2px;">
                        ${this.escapeHtml(subtask.description)}
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Render milestone footer with stats and actions
     */
    renderMilestoneFooter(milestone, sessionId) {
        const totalTasks = milestone.tasks ? milestone.tasks.length : 0;
        const completedTasks = milestone.tasks ? milestone.tasks.filter(t => t.completed).length : 0;
        const blockedTasks = milestone.tasks ? milestone.tasks.filter(t => t.blocked).length : 0;

        const totalSubtasks = milestone.tasks
            ? milestone.tasks.reduce((sum, t) => sum + (t.subtasks ? t.subtasks.length : 0), 0)
            : 0;
        const completedSubtasks = milestone.tasks
            ? milestone.tasks.reduce((sum, t) => sum + (t.subtasks ? t.subtasks.filter(s => s.completed).length : 0), 0)
            : 0;

        return `
            <div class="milestone-footer">
                <div class="milestone-footer-stats">
                    <span title="Tasks completed">
                        <i class="fas fa-tasks"></i> ${completedTasks}/${totalTasks}
                    </span>
                    ${totalSubtasks > 0 ? `
                        <span title="Subtasks completed">
                            <i class="fas fa-check-circle"></i> ${completedSubtasks}/${totalSubtasks}
                        </span>
                    ` : ''}
                    ${blockedTasks > 0 ? `
                        <span style="color: #dc2626;" title="Blocked tasks">
                            <i class="fas fa-exclamation-triangle"></i> ${blockedTasks}
                        </span>
                    ` : ''}
                    ${milestone.estimated_hours ? `
                        <span title="Estimated hours">
                            <i class="fas fa-clock"></i> ${milestone.estimated_hours}h
                        </span>
                    ` : ''}
                </div>
                <div class="milestone-footer-actions">
                    <button class="milestone-comment-btn" 
                            onclick="SynergyMilestoneInteractions.addComment('${sessionId}', '${milestone.milestone_id}')"
                            title="Add comment">
                        <i class="fas fa-comment"></i> Comment
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Calculate milestone progress percentage
     */
    calculateMilestoneProgress(milestone) {
        if (!milestone.tasks || milestone.tasks.length === 0) {
            return milestone.completed ? 100 : 0;
        }

        const totalTasks = milestone.tasks.length;
        const completedTasks = milestone.tasks.filter(t => t.completed).length;

        const totalSubtasks = milestone.tasks.reduce((sum, t) =>
            sum + (t.subtasks ? t.subtasks.length : 0), 0);
        const completedSubtasks = milestone.tasks.reduce((sum, t) =>
            sum + (t.subtasks ? t.subtasks.filter(s => s.completed).length : 0), 0);

        const totalItems = totalTasks + totalSubtasks;
        const completedItems = completedTasks + completedSubtasks;

        return totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0;
    }

    /**
     * Check if milestone is expanded
     */
    isMilestoneExpanded(milestoneId) {
        return this.expandedMilestones.has(milestoneId);
    }

    /**
     * Check if task is expanded
     */
    isTaskExpanded(taskId) {
        return this.expandedTasks.has(taskId);
    }

    /**
     * Toggle milestone expansion state
     */
    toggleMilestoneExpansion(milestoneId) {
        if (this.expandedMilestones.has(milestoneId)) {
            this.expandedMilestones.delete(milestoneId);
            return false;
        } else {
            this.expandedMilestones.add(milestoneId);
            return true;
        }
    }

    /**
     * Toggle task expansion state
     */
    toggleTaskExpansion(taskId) {
        if (this.expandedTasks.has(taskId)) {
            this.expandedTasks.delete(taskId);
            return false;
        } else {
            this.expandedTasks.add(taskId);
            return true;
        }
    }

    /**
     * Darken color for gradient effect
     */
    darkenColor(color) {
        // Simple darkening by reducing brightness
        const hex = color.replace('#', '');
        const r = Math.max(0, parseInt(hex.substr(0, 2), 16) - 30);
        const g = Math.max(0, parseInt(hex.substr(2, 2), 16) - 30);
        const b = Math.max(0, parseInt(hex.substr(4, 2), 16) - 30);
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }

    /**
     * Render milestone-level documents with badge numbering
     * Badge format: D1.1, D1.2 (Milestone 1), D2.1 (Milestone 2)
     */
    renderMilestoneDocuments(milestone, milestoneNumber) {
        const documents = milestone.documents ? JSON.parse(milestone.documents) : [];

        if (!documents || documents.length === 0) {
            return '';
        }

        let html = `
            <div class="milestone-documents">
                <div class="milestone-subsection-title">
                    <i class="fas fa-file-alt"></i> Documents (${documents.length})
                </div>
                <div class="document-list">
        `;

        documents.forEach((doc, index) => {
            const badge = `D${milestoneNumber}.${index + 1}`;
            const isInternal = doc.type === 'internal';
            const icon = this.getDocumentIcon(doc.type);

            html += `
                <div class="doc-item" data-doc-id="${doc.id || `doc_${index}`}">
                    <span class="doc-badge">${badge}</span>
                    ${isInternal ? '<span class="internal-badge">Internal</span>' : ''}
                    <i class="fas ${icon}"></i>
                    <a href="${doc.url}" target="_blank" class="doc-link editable" 
                       data-field="name" data-original="${this.escapeHtml(doc.name)}">
                        ${this.escapeHtml(doc.name)}
                    </a>
                    <button class="btn-icon btn-delete" onclick="SynergyMilestoneInteractions.deleteDocument('${milestone.milestone_id}', '${doc.id || `doc_${index}`}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
        });

        html += `
                </div>
                <button class="btn-add-item" onclick="SynergyMilestoneInteractions.addDocument('${milestone.milestone_id}')">
                    <i class="fas fa-plus"></i> Add Document
                </button>
            </div>
        `;

        return html;
    }

    /**
     * Render milestone-level links with badge numbering
     * Badge format: L1.1, L1.2 (Milestone 1), L2.1 (Milestone 2)
     */
    renderMilestoneLinks(milestone, milestoneNumber) {
        const links = milestone.links ? JSON.parse(milestone.links) : [];

        if (!links || links.length === 0) {
            return '';
        }

        let html = `
            <div class="milestone-links">
                <div class="milestone-subsection-title">
                    <i class="fas fa-link"></i> Links (${links.length})
                </div>
                <div class="link-list">
        `;

        links.forEach((link, index) => {
            const badge = `L${milestoneNumber}.${index + 1}`;

            html += `
                <div class="link-item" data-link-id="${link.id || `link_${index}`}">
                    <span class="link-badge">${badge}</span>
                    <i class="fas fa-external-link-alt"></i>
                    <a href="${link.url}" target="_blank" class="link-text editable" 
                       data-field="name" data-original="${this.escapeHtml(link.name)}">
                        ${this.escapeHtml(link.name)}
                    </a>
                    <button class="btn-icon btn-delete" onclick="SynergyMilestoneInteractions.deleteLink('${milestone.milestone_id}', '${link.id || `link_${index}`}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
        });

        html += `
                </div>
                <button class="btn-add-item" onclick="SynergyMilestoneInteractions.addLink('${milestone.milestone_id}')">
                    <i class="fas fa-plus"></i> Add Link
                </button>
            </div>
        `;

        return html;
    }

    /**
     * Get icon for document type
     */
    getDocumentIcon(type) {
        const icons = {
            'google_doc': 'fa-file-word',
            'google_sheet': 'fa-file-excel',
            'pdf': 'fa-file-pdf',
            'internal': 'fa-file-alt',
            'document': 'fa-file'
        };
        return icons[type] || 'fa-file';
    }

    /**
     * Make element editable on double-click (inline editing)
     * Saves on Enter or blur, cancels on Escape
     */
    makeEditable(element, saveCallback) {
        element.addEventListener('dblclick', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const originalText = element.textContent.trim();
            const field = element.dataset.field;

            // Create input
            const input = document.createElement('input');
            input.type = 'text';
            input.value = originalText;
            input.className = 'inline-edit-input';
            input.dataset.field = field;
            input.dataset.original = originalText;

            // Replace element with input
            element.style.display = 'none';
            element.parentNode.insertBefore(input, element.nextSibling);
            input.focus();
            input.select();

            // Save on Enter or blur
            const save = async () => {
                const newValue = input.value.trim();
                if (newValue && newValue !== originalText) {
                    const success = await saveCallback(field, newValue);
                    if (success) {
                        element.textContent = newValue;
                    }
                }
                input.remove();
                element.style.display = '';
            };

            // Cancel on Escape
            const cancel = () => {
                input.remove();
                element.style.display = '';
            };

            input.addEventListener('blur', save);
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    save();
                } else if (e.key === 'Escape') {
                    cancel();
                }
            });
        });
    }

    /**
     * Initialize inline editing for all editable elements in a container
     */
    initializeInlineEditing(container, milestoneId) {
        const editableElements = container.querySelectorAll('.editable');

        editableElements.forEach(element => {
            this.makeEditable(element, async (field, value) => {
                try {
                    const response = await fetch(`/api/synergy/milestone/${milestoneId}/update`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ field, value })
                    });

                    const result = await response.json();
                    if (result.success) {
                        window.showNotification?.('Updated successfully', 'success');
                        return true;
                    } else {
                        window.showNotification?.('Failed to update: ' + result.error, 'error');
                        return false;
                    }
                } catch (error) {
                    console.error('Failed to save edit:', error);
                    window.showNotification?.('Failed to save changes', 'error');
                    return false;
                }
            });
        });
    }
}

// Create global instance
if (typeof window !== 'undefined') {
    window.SynergyMilestoneRenderer = window.SynergyMilestoneRenderer || new SynergyMilestoneRenderer();
}
