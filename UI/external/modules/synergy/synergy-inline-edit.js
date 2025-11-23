/**
 * FILE: UI/external/modules/synergy/synergy-inline-edit.js
 * PURPOSE: Inline editing for synergy milestones/tasks/subtasks/documents
 * 
 * FEATURES:
 * - Edit directly in expanded card (NO popup)
 * - ContentEditable fields for immediate editing
 * - Save/Cancel buttons appear when editing
 * - API integration for persistence
 * 
 * ARCHITECTURE FIX (Nov 24, 2025):
 * - CRITICAL: Instance created IMMEDIATELY (not at bottom of file)
 * - Prevents "SynergyInlineEdit.editMilestone is not a function" errors
 * - Ensures global availability before any HTML injection
 * 
 * LAST MODIFIED: 2025-11-24 - Fixed timing issue with immediate registration
 */

class SynergyInlineEditClass {
    constructor() {
        this.API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
        this.originalContent = {};
        console.log('[SYNERGY INLINE EDIT] Instance created');
    }

    // ==================== MILESTONE EDITING ====================

    editMilestone(sessionId, milestoneId) {
        const container = document.querySelector(`[data-milestone-id="${milestoneId}"]`);
        if (!container) return;

        // Store original content
        const titleEl = container.querySelector('.synergy-flat-milestone-title');
        const descEl = container.querySelector('.synergy-flat-milestone-desc');
        
        this.originalContent[milestoneId] = {
            title: titleEl ? titleEl.textContent : '',
            description: descEl ? descEl.textContent : ''
        };

        // Enable editing
        container.setAttribute('data-editing', 'true');
        if (titleEl) {
            titleEl.setAttribute('contenteditable', 'true');
            titleEl.focus();
        }
        if (descEl) descEl.setAttribute('contenteditable', 'true');

        // Show save/cancel, hide edit/delete
        this.toggleEditMode(container, true);
    }

    async saveMilestone(sessionId, milestoneId) {
        const container = document.querySelector(`[data-milestone-id="${milestoneId}"]`);
        if (!container) return;

        const titleEl = container.querySelector('.synergy-flat-milestone-title');
        const descEl = container.querySelector('.synergy-flat-milestone-desc');

        const data = {
            milestone: titleEl ? titleEl.textContent.trim() : '',
            description: descEl ? descEl.textContent.trim() : ''
        };

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/milestone/${milestoneId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) throw new Error('Save failed');

            // Disable editing
            container.setAttribute('data-editing', 'false');
            if (titleEl) titleEl.setAttribute('contenteditable', 'false');
            if (descEl) descEl.setAttribute('contenteditable', 'false');
            this.toggleEditMode(container, false);
            delete this.originalContent[milestoneId];

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Save error:', error);
            alert('Failed to save milestone. Please try again.');
        }
    }

    cancelEdit(sessionId, itemId) {
        const container = document.querySelector(`[data-milestone-id="${itemId}"], [data-task-id="${itemId}"], [data-subtask-id="${itemId}"]`);
        if (!container) return;

        // Restore original content
        if (this.originalContent[itemId]) {
            const titleEl = container.querySelector('[contenteditable]');
            if (titleEl && this.originalContent[itemId].title) {
                titleEl.textContent = this.originalContent[itemId].title;
            }
        }

        // Disable editing
        container.setAttribute('data-editing', 'false');
        container.querySelectorAll('[contenteditable]').forEach(el => {
            el.setAttribute('contenteditable', 'false');
        });
        this.toggleEditMode(container, false);
        delete this.originalContent[itemId];
    }

    async deleteMilestone(sessionId, milestoneId) {
        if (!confirm('Delete this milestone? This cannot be undone.')) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/milestone/${milestoneId}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Delete failed');

            // Remove from DOM
            const container = document.querySelector(`[data-milestone-id="${milestoneId}"]`);
            if (container) container.remove();

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Delete error:', error);
            alert('Failed to delete milestone.');
        }
    }

    linkMilestone(sessionId, milestoneId) {
        // TODO: Implement milestone linking functionality
        console.log('[SYNERGY INLINE EDIT] Link milestone:', milestoneId);
    }

    async toggleMilestoneComplete(sessionId, milestoneId, completed) {
        try {
            await fetch(`${this.API_BASE_URL}/api/synergy/milestone/${milestoneId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ completed })
            });
        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Toggle error:', error);
        }
    }

    // ==================== SESSION-LEVEL EDITING ====================

    editSessionTitle(sessionId) {
        const titleEl = document.querySelector('.synergy-session-title-editable');
        if (!titleEl) return;

        this.originalContent['session_title'] = titleEl.textContent;
        titleEl.setAttribute('contenteditable', 'true');
        titleEl.focus();
        
        // Select all text
        const range = document.createRange();
        range.selectNodeContents(titleEl);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
    }

    async saveSessionTitle(sessionId) {
        const titleEl = document.querySelector('.synergy-session-title-editable');
        if (!titleEl) return;

        const newTitle = titleEl.textContent.trim();
        if (!newTitle) {
            alert('Title cannot be empty');
            return;
        }

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: newTitle })
            });

            if (!response.ok) throw new Error('Save failed');

            titleEl.setAttribute('contenteditable', 'false');
            delete this.originalContent['session_title'];
            
        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Save title error:', error);
            alert('Failed to save title');
        }
    }

    editDescription(sessionId) {
        const section = document.querySelector('[data-section="description"]');
        if (!section) return;

        const container = section.querySelector('.synergy-flat-description-container');
        const descEl = section.querySelector('.synergy-flat-description');
        
        if (!descEl) return;

        this.originalContent['description'] = descEl.textContent;
        container.setAttribute('data-editing', 'true');
        descEl.setAttribute('contenteditable', 'true');
        descEl.focus();

        // Show save/cancel buttons
        const actions = section.querySelector('.synergy-flat-edit-actions');
        if (actions) actions.style.display = 'flex';
    }

    async saveDescription(sessionId) {
        const section = document.querySelector('[data-section="description"]');
        if (!section) return;

        const container = section.querySelector('.synergy-flat-description-container');
        const descEl = section.querySelector('.synergy-flat-description');
        const newDesc = descEl.textContent.trim();

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description: newDesc })
            });

            if (!response.ok) throw new Error('Save failed');

            container.setAttribute('data-editing', 'false');
            descEl.setAttribute('contenteditable', 'false');
            delete this.originalContent['description'];

            // Hide save/cancel buttons
            const actions = section.querySelector('.synergy-flat-edit-actions');
            if (actions) actions.style.display = 'none';

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Save description error:', error);
            alert('Failed to save description');
        }
    }

    cancelDescription() {
        const section = document.querySelector('[data-section="description"]');
        if (!section) return;

        const container = section.querySelector('.synergy-flat-description-container');
        const descEl = section.querySelector('.synergy-flat-description');

        if (this.originalContent['description']) {
            descEl.textContent = this.originalContent['description'];
        }

        container.setAttribute('data-editing', 'false');
        descEl.setAttribute('contenteditable', 'false');
        delete this.originalContent['description'];

        // Hide save/cancel buttons
        const actions = section.querySelector('.synergy-flat-edit-actions');
        if (actions) actions.style.display = 'none';
    }

    // Add/Edit Tags
    async addTag(sessionId) {
        const tagName = prompt('Enter tag name:');
        if (!tagName) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}/tags`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tag: tagName.trim() })
            });

            if (!response.ok) throw new Error('Add tag failed');

            // Reload card to show new tag
            await this.reloadCard(sessionId);

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Add tag error:', error);
            alert('Failed to add tag');
        }
    }

    async removeTag(sessionId, tagName) {
        if (!confirm(`Remove tag "${tagName}"?`)) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}/tags/${encodeURIComponent(tagName)}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Remove tag failed');

            // Reload card to update UI
            await this.reloadCard(sessionId);

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Remove tag error:', error);
            alert('Failed to remove tag');
        }
    }

    // Add/Edit Links
    async addLink(sessionId) {
        const url = prompt('Enter link URL:');
        if (!url) return;

        const title = prompt('Enter link title (optional):', url);

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}/links`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, title: title || url })
            });

            if (!response.ok) throw new Error('Add link failed');

            // Reload card
            await this.reloadCard(sessionId);

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Add link error:', error);
            alert('Failed to add link');
        }
    }

    async removeLink(sessionId, linkIndex) {
        if (!confirm('Remove this link?')) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}/links/${linkIndex}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Remove link failed');

            // Reload card
            await this.reloadCard(sessionId);

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Remove link error:', error);
            alert('Failed to remove link');
        }
    }

    // Add Milestone
    async addMilestone(sessionId) {
        const milestoneName = prompt('Enter milestone name:');
        if (!milestoneName) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}/milestones`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    milestone_name: milestoneName.trim(),
                    description: '',
                    priority: 'medium'
                })
            });

            if (!response.ok) throw new Error('Add milestone failed');

            // Reload card
            await this.reloadCard(sessionId);

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Add milestone error:', error);
            alert('Failed to add milestone');
        }
    }

    // Add Task to Milestone
    async addTask(sessionId, milestoneId) {
        const taskName = prompt('Enter task name:');
        if (!taskName) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/milestone/${milestoneId}/tasks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    task: taskName.trim(),
                    priority: 'medium'
                })
            });

            if (!response.ok) throw new Error('Add task failed');

            // Reload card
            await this.reloadCard(sessionId);

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Add task error:', error);
            alert('Failed to add task');
        }
    }

    // Add Subtask to Task
    async addSubtask(sessionId, taskId) {
        const subtaskName = prompt('Enter subtask name:');
        if (!subtaskName) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/task/${taskId}/subtasks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    task: subtaskName.trim(),
                    priority: 'medium'
                })
            });

            if (!response.ok) throw new Error('Add subtask failed');

            // Reload card
            await this.reloadCard(sessionId);

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Add subtask error:', error);
            alert('Failed to add subtask');
        }
    }

    // Reload card helper
    async reloadCard(sessionId) {
        const cardElement = document.querySelector(`[data-session-id="${sessionId}"]`);
        if (!cardElement) return;

        // Use renderer to reload
        if (window.SynergySidebarRenderer) {
            await window.SynergySidebarRenderer.loadAndRenderFullCard(sessionId, cardElement);
        }
    }

    // ==================== TASK EDITING ====================

    editTask(sessionId, taskId) {
        const container = document.querySelector(`[data-task-id="${taskId}"]`);
        if (!container) return;

        const titleEl = container.querySelector('.synergy-flat-task-title');
        this.originalContent[taskId] = {
            title: titleEl ? titleEl.textContent : ''
        };

        container.setAttribute('data-editing', 'true');
        if (titleEl) {
            titleEl.setAttribute('contenteditable', 'true');
            titleEl.focus();
        }
        this.toggleEditMode(container, true);
    }

    async saveTask(sessionId, taskId) {
        const container = document.querySelector(`[data-task-id="${taskId}"]`);
        if (!container) return;

        const titleEl = container.querySelector('.synergy-flat-task-title');
        const data = { task: titleEl ? titleEl.textContent.trim() : '' };

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/task/${taskId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) throw new Error('Save failed');

            container.setAttribute('data-editing', 'false');
            if (titleEl) titleEl.setAttribute('contenteditable', 'false');
            this.toggleEditMode(container, false);
            delete this.originalContent[taskId];

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Save error:', error);
            alert('Failed to save task.');
        }
    }

    async deleteTask(sessionId, taskId) {
        if (!confirm('Delete this task?')) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/task/${taskId}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Delete failed');

            const container = document.querySelector(`[data-task-id="${taskId}"]`);
            if (container) container.remove();

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Delete error:', error);
            alert('Failed to delete task.');
        }
    }

    linkTask(sessionId, taskId) {
        console.log('[SYNERGY INLINE EDIT] Link task:', taskId);
    }

    async toggleTaskComplete(sessionId, taskId, completed) {
        try {
            await fetch(`${this.API_BASE_URL}/api/synergy/task/${taskId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ completed })
            });
        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Toggle error:', error);
        }
    }

    // ==================== SUBTASK EDITING ====================

    editSubtask(sessionId, subtaskId) {
        const container = document.querySelector(`[data-subtask-id="${subtaskId}"]`);
        if (!container) return;

        const titleEl = container.querySelector('.synergy-flat-subtask-title');
        this.originalContent[subtaskId] = {
            title: titleEl ? titleEl.textContent : ''
        };

        container.setAttribute('data-editing', 'true');
        if (titleEl) {
            titleEl.setAttribute('contenteditable', 'true');
            titleEl.focus();
        }
        this.toggleEditMode(container, true);
    }

    async saveSubtask(sessionId, subtaskId) {
        const container = document.querySelector(`[data-subtask-id="${subtaskId}"]`);
        if (!container) return;

        const titleEl = container.querySelector('.synergy-flat-subtask-title');
        const data = { subtask: titleEl ? titleEl.textContent.trim() : '' };

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/subtask/${subtaskId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) throw new Error('Save failed');

            container.setAttribute('data-editing', 'false');
            if (titleEl) titleEl.setAttribute('contenteditable', 'false');
            this.toggleEditMode(container, false);
            delete this.originalContent[subtaskId];

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Save error:', error);
            alert('Failed to save subtask.');
        }
    }

    async deleteSubtask(sessionId, subtaskId) {
        if (!confirm('Delete this subtask?')) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/subtask/${subtaskId}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Delete failed');

            const container = document.querySelector(`[data-subtask-id="${subtaskId}"]`);
            if (container) container.remove();

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Delete error:', error);
            alert('Failed to delete subtask.');
        }
    }

    async toggleSubtaskComplete(sessionId, subtaskId, completed) {
        try {
            await fetch(`${this.API_BASE_URL}/api/synergy/subtask/${subtaskId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ completed })
            });
        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Toggle error:', error);
        }
    }

    // ==================== DOCUMENT EDITING ====================

    editDoc(sessionId, docId) {
        console.log('[SYNERGY INLINE EDIT] Edit document:', docId);
        // TODO: Implement document editing
    }

    deleteDoc(sessionId, docId) {
        console.log('[SYNERGY INLINE EDIT] Delete document:', docId);
        // TODO: Implement document deletion
    }

    openDoc(sessionId, docId) {
        console.log('[SYNERGY INLINE EDIT] Open document:', docId);
        // TODO: Implement document opening
    }

    // ==================== HELPER METHODS ====================

    toggleEditMode(container, isEditing) {
        // Toggle button visibility
        const editActions = container.querySelector('.synergy-flat-edit-actions');
        const headerRight = container.querySelector('.synergy-flat-header-right');

        if (isEditing) {
            if (editActions) editActions.style.display = 'flex';
            if (headerRight) {
                const editBtn = headerRight.querySelector('.synergy-edit-btn');
                const deleteBtn = headerRight.querySelector('.synergy-delete-btn');
                if (editBtn) editBtn.style.display = 'none';
                if (deleteBtn) deleteBtn.style.display = 'none';
            }
        } else {
            if (editActions) editActions.style.display = 'none';
            if (headerRight) {
                const editBtn = headerRight.querySelector('.synergy-edit-btn');
                const deleteBtn = headerRight.querySelector('.synergy-delete-btn');
                if (editBtn) editBtn.style.display = 'inline-block';
                if (deleteBtn) deleteBtn.style.display = 'inline-block';
            }
        }
    }
}

// ==================== EVENT DELEGATION SETUP (RECOMMENDED PATTERN) ====================
// Use event delegation instead of inline onclick handlers for better performance and reliability
// This eliminates timing issues and reduces HTML bloat

// Create global instance
window.SynergyInlineEdit = new SynergyInlineEditClass();
console.log('[SYNERGY INLINE EDIT] ✅ Instance created with event delegation');

// Setup event delegation on document level
document.addEventListener('click', function(e) {
    const target = e.target;
    
    // Edit button clicked
    if (target.classList.contains('synergy-edit-btn')) {
        const container = target.closest('[data-milestone-id], [data-task-id], [data-subtask-id]');
        if (!container) return;
        
        const milestoneId = container.getAttribute('data-milestone-id');
        const taskId = container.getAttribute('data-task-id');
        const subtaskId = container.getAttribute('data-subtask-id');
        const sessionId = container.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        
        if (milestoneId) window.SynergyInlineEdit.editMilestone(sessionId, milestoneId);
        else if (taskId) window.SynergyInlineEdit.editTask(sessionId, taskId);
        else if (subtaskId) window.SynergyInlineEdit.editSubtask(sessionId, subtaskId);
        return;
    }
    
    // Save button clicked
    if (target.classList.contains('synergy-save-btn')) {
        const container = target.closest('[data-milestone-id], [data-task-id], [data-subtask-id]');
        if (!container) return;
        
        const milestoneId = container.getAttribute('data-milestone-id');
        const taskId = container.getAttribute('data-task-id');
        const subtaskId = container.getAttribute('data-subtask-id');
        const sessionId = container.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        
        if (milestoneId) window.SynergyInlineEdit.saveMilestone(sessionId, milestoneId);
        else if (taskId) window.SynergyInlineEdit.saveTask(sessionId, taskId);
        else if (subtaskId) window.SynergyInlineEdit.saveSubtask(sessionId, subtaskId);
        return;
    }
    
    // Cancel button clicked
    if (target.classList.contains('synergy-cancel-btn')) {
        const container = target.closest('[data-milestone-id], [data-task-id], [data-subtask-id]');
        if (!container) return;
        
        const milestoneId = container.getAttribute('data-milestone-id');
        const taskId = container.getAttribute('data-task-id');
        const subtaskId = container.getAttribute('data-subtask-id');
        const sessionId = container.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        
        const itemId = milestoneId || taskId || subtaskId;
        window.SynergyInlineEdit.cancelEdit(sessionId, itemId);
        return;
    }
    
    // Delete button clicked
    if (target.classList.contains('synergy-delete-btn')) {
        const container = target.closest('[data-milestone-id], [data-task-id], [data-subtask-id]');
        if (!container) return;
        
        const milestoneId = container.getAttribute('data-milestone-id');
        const taskId = container.getAttribute('data-task-id');
        const subtaskId = container.getAttribute('data-subtask-id');
        const sessionId = container.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        
        if (milestoneId) window.SynergyInlineEdit.deleteMilestone(sessionId, milestoneId);
        else if (taskId) window.SynergyInlineEdit.deleteTask(sessionId, taskId);
        else if (subtaskId) window.SynergyInlineEdit.deleteSubtask(sessionId, subtaskId);
        return;
    }
    
    // Link button clicked
    if (target.classList.contains('synergy-link-btn')) {
        const container = target.closest('[data-milestone-id], [data-task-id]');
        if (!container) return;
        
        const milestoneId = container.getAttribute('data-milestone-id');
        const taskId = container.getAttribute('data-task-id');
        const sessionId = container.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        
        if (milestoneId) window.SynergyInlineEdit.linkMilestone(sessionId, milestoneId);
        else if (taskId) window.SynergyInlineEdit.linkTask(sessionId, taskId);
        return;
    }
    
    // SESSION-LEVEL EDITING BUTTONS
    
    // Edit description button
    if (target.classList.contains('synergy-edit-description-btn')) {
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        window.SynergyInlineEdit.editDescription(sessionId);
        return;
    }
    
    // Save description button
    if (target.classList.contains('synergy-save-description-btn')) {
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        window.SynergyInlineEdit.saveDescription(sessionId);
        return;
    }
    
    // Cancel description button
    if (target.classList.contains('synergy-cancel-description-btn')) {
        window.SynergyInlineEdit.cancelDescription();
        return;
    }
    
    // Add milestone button
    if (target.classList.contains('synergy-add-milestone-btn')) {
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        window.SynergyInlineEdit.addMilestone(sessionId);
        return;
    }
    
    // Add task button
    if (target.classList.contains('synergy-add-task-btn')) {
        const milestoneId = target.getAttribute('data-milestone-id') || target.closest('[data-milestone-id]')?.getAttribute('data-milestone-id');
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        if (milestoneId) {
            window.SynergyInlineEdit.addTask(sessionId, milestoneId);
        }
        return;
    }
    
    // Add subtask button
    if (target.classList.contains('synergy-add-subtask-btn')) {
        const taskId = target.getAttribute('data-task-id') || target.closest('[data-task-id]')?.getAttribute('data-task-id');
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        if (taskId) {
            window.SynergyInlineEdit.addSubtask(sessionId, taskId);
        }
        return;
    }
    
    // Add tag button
    if (target.classList.contains('synergy-add-tag-btn')) {
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        window.SynergyInlineEdit.addTag(sessionId);
        return;
    }
    
    // Remove tag button
    if (target.classList.contains('synergy-remove-tag-btn')) {
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        const tagName = target.getAttribute('data-tag-name');
        if (tagName) {
            window.SynergyInlineEdit.removeTag(sessionId, tagName);
        }
        return;
    }
    
    // Add link button
    if (target.classList.contains('synergy-add-link-btn')) {
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        window.SynergyInlineEdit.addLink(sessionId);
        return;
    }
    
    // Remove link button
    if (target.classList.contains('synergy-remove-link-btn')) {
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        const linkIndex = target.getAttribute('data-link-index');
        if (linkIndex !== null) {
            window.SynergyInlineEdit.removeLink(sessionId, parseInt(linkIndex));
        }
        return;
    }
    
    // Edit session title (double-click on title)
    if (target.classList.contains('synergy-session-title-editable')) {
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        window.SynergyInlineEdit.editSessionTitle(sessionId);
        return;
    }
});

// Setup checkbox change delegation
document.addEventListener('change', function(e) {
    const target = e.target;
    
    // Checkbox toggle for milestone/task/subtask completion
    if (target.classList.contains('synergy-flat-checkbox')) {
        const container = target.closest('[data-milestone-id], [data-task-id], [data-subtask-id]');
        if (!container) return;
        
        const milestoneId = container.getAttribute('data-milestone-id');
        const taskId = container.getAttribute('data-task-id');
        const subtaskId = container.getAttribute('data-subtask-id');
        const sessionId = container.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        const checked = target.checked;
        
        if (milestoneId) window.SynergyInlineEdit.toggleMilestoneComplete(sessionId, milestoneId, checked);
        else if (taskId) window.SynergyInlineEdit.toggleTaskComplete(sessionId, taskId, checked);
        else if (subtaskId) window.SynergyInlineEdit.toggleSubtaskComplete(sessionId, subtaskId, checked);
    }
});

console.log('[SYNERGY INLINE EDIT] ✅ Event delegation initialized (no inline handlers needed)');
