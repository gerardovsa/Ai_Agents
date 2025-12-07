/**
 * FILE: UI/external/modules/synergy-milestone-interactions.js
 * PURPOSE: Handles milestone interactions (expand/collapse, completion, blocking)
 * 
 * DEPENDENCIES:
 * - synergy-milestone-renderer.js (state management)
 * - Flask backend /api/synergy/milestone/* endpoints
 * 
 * EXPORTS:
 * - SynergyMilestoneInteractions class with interaction handlers
 * 
 * USED BY:
 * - synergy-milestone-renderer.js (onclick handlers)
 * - business-ai-platform-v2.html (global event handlers)
 * 
 * NOTES:
 * - Auto-completion cascade (subtask → task → milestone)
 * - Real-time UI updates without full page refresh
 * - Error handling with user notifications
 * 
 * LAST MODIFIED: 2025-11-19 - Initial creation
 */

class SynergyMilestoneInteractions {
    constructor() {
        this.apiBaseUrl = window.API_BASE_URL || 'http://localhost:5001';
    }

    /**
     * Toggle milestone expansion (show/hide tasks)
     */
    toggleMilestone(milestoneId, event) {
        // Determine context from event target
        const target = event ? event.target : null;
        const contextRoot = target ? (target.closest('[data-context]') || document) : document;
        const milestoneEl = contextRoot.querySelector(`[data-milestone-id="${milestoneId}"]`);
        if (!milestoneEl) return;

        const body = milestoneEl.querySelector('.milestone-body');
        const btn = milestoneEl.querySelector('.milestone-expand-btn i');

        const renderer = window.SynergyMilestoneRenderer;
        const isExpanded = renderer.toggleMilestoneExpansion(milestoneId);

        if (isExpanded) {
            body.classList.remove('collapsed');
            body.classList.add('expanded');
            btn.classList.remove('fa-chevron-right');
            btn.classList.add('fa-chevron-down');
        } else {
            body.classList.remove('expanded');
            body.classList.add('collapsed');
            btn.classList.remove('fa-chevron-down');
            btn.classList.add('fa-chevron-right');
        }
    }

    /**
     * Toggle task expansion (show/hide subtasks)
     */
    toggleTask(taskId, event) {
        // Determine context from event target
        const target = event ? event.target : null;
        const contextRoot = target ? (target.closest('[data-context]') || document) : document;
        const taskEl = contextRoot.querySelector(`[data-task-id="${taskId}"]`);
        if (!taskEl) return;

        const subtasksEl = taskEl.querySelector('.task-subtasks');
        const btn = taskEl.querySelector('.task-expand-btn i');

        if (!subtasksEl) return;

        const renderer = window.SynergyMilestoneRenderer;
        const isExpanded = renderer.toggleTaskExpansion(taskId);

        if (isExpanded) {
            subtasksEl.classList.remove('collapsed');
            subtasksEl.classList.add('expanded');
            btn.classList.remove('fa-chevron-right');
            btn.classList.add('fa-chevron-down');
        } else {
            subtasksEl.classList.remove('expanded');
            subtasksEl.classList.add('collapsed');
            btn.classList.remove('fa-chevron-down');
            btn.classList.add('fa-chevron-right');
        }
    }

    /**
     * Complete milestone (auto-completes all tasks/subtasks)
     */
    async completeMilestone(sessionId, milestoneId) {
        try {
            const checkbox = event.target;
            const completed = checkbox.checked;

            // Optimistic UI update (context-aware)
            const target = event ? event.target : null;
            const contextRoot = target ? (target.closest('[data-context]') || document) : document;
            const milestoneEl = contextRoot.querySelector(`[data-milestone-id="${milestoneId}"]`);
            if (milestoneEl) {
                if (completed) {
                    milestoneEl.classList.add('completed');
                } else {
                    milestoneEl.classList.remove('completed');
                }
            }

            const response = await fetch(`${this.apiBaseUrl}/api/synergy/milestone/${milestoneId}/complete`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ completed })
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification(
                    `Milestone ${completed ? 'completed' : 'reopened'} (${result.tasks_completed} tasks, ${result.subtasks_completed} subtasks)`,
                    'success'
                );
                // Refresh card to show updated state
                await this.refreshCard(sessionId);
            } else {
                // Revert on failure
                if (completed) {
                    milestoneEl.classList.remove('completed');
                } else {
                    milestoneEl.classList.add('completed');
                }
                checkbox.checked = !completed;
                this.showNotification('Failed to update milestone', 'error');
            }
        } catch (error) {
            console.error('Error completing milestone:', error);
            this.showNotification('Error updating milestone', 'error');
        }
    }

    /**
     * Complete task (auto-completes all subtasks)
     */
    async completeTask(sessionId, taskId) {
        try {
            const checkbox = event.target;
            const completed = checkbox.checked;

            // Optimistic UI update (context-aware)
            const contextRoot = checkbox.closest('[data-context]') || document;
            const taskEl = contextRoot.querySelector(`[data-task-id="${taskId}"]`);
            if (taskEl) {
                if (completed) {
                    taskEl.classList.add('completed');
                } else {
                    taskEl.classList.remove('completed');
                }
            }

            const response = await fetch(`${this.apiBaseUrl}/api/synergy/task/${taskId}/complete`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ completed })
            });

            const result = await response.json();

            if (result.success) {
                let message = `Task ${completed ? 'completed' : 'reopened'}`;
                if (result.auto_completed_subtasks > 0) {
                    message += ` (${result.auto_completed_subtasks} subtasks auto-completed)`;
                }
                if (result.milestone_completed) {
                    message += ' - Milestone auto-completed!';
                }
                this.showNotification(message, 'success');

                // Refresh card to show updated state
                await this.refreshCard(sessionId);
            } else {
                // Revert on failure
                if (completed) {
                    taskEl.classList.remove('completed');
                } else {
                    taskEl.classList.add('completed');
                }
                checkbox.checked = !completed;
                this.showNotification('Failed to update task', 'error');
            }
        } catch (error) {
            console.error('Error completing task:', error);
            this.showNotification('Error updating task', 'error');
        }
    }

    /**
     * Complete subtask (auto-completes parent task if all done)
     */
    async completeSubtask(sessionId, subtaskId) {
        try {
            const checkbox = event.target;
            const completed = checkbox.checked;

            // Optimistic UI update (context-aware)
            const contextRoot = checkbox.closest('[data-context]') || document;
            const subtaskEl = contextRoot.querySelector(`[data-subtask-id="${subtaskId}"]`);
            if (subtaskEl) {
                if (completed) {
                    subtaskEl.classList.add('completed');
                } else {
                    subtaskEl.classList.remove('completed');
                }
            }

            const response = await fetch(`${this.apiBaseUrl}/api/synergy/subtask/${subtaskId}/complete`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ completed })
            });

            const result = await response.json();

            if (result.success) {
                let message = `Subtask ${completed ? 'completed' : 'reopened'}`;
                if (result.task_auto_completed) {
                    message += ' - Task auto-completed';
                }
                if (result.milestone_auto_completed) {
                    message += ' - Milestone auto-completed!';
                }
                this.showNotification(message, 'success');

                // Refresh card to show updated state
                await this.refreshCard(sessionId);
            } else {
                // Revert on failure
                if (completed) {
                    subtaskEl.classList.remove('completed');
                } else {
                    subtaskEl.classList.add('completed');
                }
                checkbox.checked = !completed;
                this.showNotification('Failed to update subtask', 'error');
            }
        } catch (error) {
            console.error('Error completing subtask:', error);
            this.showNotification('Error updating subtask', 'error');
        }
    }

    /**
     * Add comment to milestone or task
     */
    async addComment(sessionId, milestoneId, taskId = null) {
        const comment = prompt('Enter your comment:');
        if (!comment || !comment.trim()) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/milestone/${milestoneId}/comment`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    task_id: taskId,
                    author: 'user',
                    comment_text: comment,
                    comment_type: 'note'
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification('Comment added', 'success');
            } else {
                this.showNotification('Failed to add comment', 'error');
            }
        } catch (error) {
            console.error('Error adding comment:', error);
            this.showNotification('Error adding comment', 'error');
        }
    }

    /**
     * Block/unblock task
     */
    async blockTask(sessionId, taskId, blocked = true, reason = null, type = 'external') {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/task/${taskId}/block`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    blocked,
                    blocker_reason: reason,
                    blocker_type: type
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification(
                    blocked ? 'Task marked as blocked' : 'Task unblocked',
                    'success'
                );
                await this.refreshCard(sessionId);
            } else {
                this.showNotification('Failed to update task', 'error');
            }
        } catch (error) {
            console.error('Error blocking task:', error);
            this.showNotification('Error updating task', 'error');
        }
    }

    /**
     * Refresh entire card to show updated state
     */
    async refreshCard(sessionId) {
        try {
            // Check if SynergySidebar exists (in sidebar view)
            if (window.SynergySidebar && typeof window.SynergySidebar.loadSessions === 'function') {
                await window.SynergySidebar.loadSessions();
                return;
            }

            // Check if synergyBoard exists (in main board view)
            if (window.synergyBoard && typeof window.synergyBoard.loadSessions === 'function') {
                await window.synergyBoard.loadSessions();
                return;
            }

            // Fallback: fetch session data directly
            const userId = window.currentUserId || window.UserAuth?.user?.id || 14;
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/${sessionId}?user_id=${userId}`);
            const result = await response.json();

            if (result.success) {
                // Update UI manually if needed
                console.log('Session data refreshed:', result.session);
            }
        } catch (error) {
            console.error('Error refreshing card:', error);
        }
    }

    /**
     * Show notification to user
     */
    showNotification(message, type = 'info') {
        // Check if notification system exists
        if (window.showNotification && typeof window.showNotification === 'function') {
            window.showNotification(message, type);
            return;
        }

        // Fallback: console log
        const emoji = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
        console.log(`${emoji} ${message}`);

        // Simple toast notification
        const toast = document.createElement('div');
        toast.className = 'milestone-toast';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#dc2626' : '#3b82f6'};
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Add document to milestone
     */
    async addDocument(milestoneId) {
        const name = prompt('Document name:');
        if (!name) return;

        const url = prompt('Document URL:');
        if (!url) return;

        const type = prompt('Document type (google_doc, google_sheet, pdf, internal):') || 'document';

        try {
            // Get current documents
            const milestone = await this.getMilestone(milestoneId);
            const documents = milestone.documents ? JSON.parse(milestone.documents) : [];

            // Add new document
            documents.push({
                id: `doc_${Date.now()}`,
                name,
                url,
                type,
                created_at: new Date().toISOString()
            });

            // Save
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/milestone/${milestoneId}/documents`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ documents })
            });

            const result = await response.json();
            if (result.success) {
                this.showNotification('Document added successfully', 'success');
                this.refreshCard(milestone.session_id);
            } else {
                this.showNotification('Failed to add document: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error adding document:', error);
            this.showNotification('Failed to add document', 'error');
        }
    }

    /**
     * Delete document from milestone
     */
    async deleteDocument(milestoneId, docId) {
        if (!confirm('Delete this document?')) return;

        try {
            const milestone = await this.getMilestone(milestoneId);
            let documents = milestone.documents ? JSON.parse(milestone.documents) : [];

            // Remove document
            documents = documents.filter(d => d.id !== docId);

            // Save
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/milestone/${milestoneId}/documents`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ documents })
            });

            const result = await response.json();
            if (result.success) {
                this.showNotification('Document deleted', 'success');
                this.refreshCard(milestone.session_id);
            } else {
                this.showNotification('Failed to delete document: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error deleting document:', error);
            this.showNotification('Failed to delete document', 'error');
        }
    }

    /**
     * Add link to milestone
     */
    async addLink(milestoneId) {
        const name = prompt('Link name:');
        if (!name) return;

        const url = prompt('Link URL:');
        if (!url) return;

        try {
            const milestone = await this.getMilestone(milestoneId);
            const links = milestone.links ? JSON.parse(milestone.links) : [];

            // Add new link
            links.push({
                id: `link_${Date.now()}`,
                name,
                url,
                created_at: new Date().toISOString()
            });

            // Save
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/milestone/${milestoneId}/links`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ links })
            });

            const result = await response.json();
            if (result.success) {
                this.showNotification('Link added successfully', 'success');
                this.refreshCard(milestone.session_id);
            } else {
                this.showNotification('Failed to add link: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error adding link:', error);
            this.showNotification('Failed to add link', 'error');
        }
    }

    /**
     * Delete link from milestone
     */
    async deleteLink(milestoneId, linkId) {
        if (!confirm('Delete this link?')) return;

        try {
            const milestone = await this.getMilestone(milestoneId);
            let links = milestone.links ? JSON.parse(milestone.links) : [];

            // Remove link
            links = links.filter(l => l.id !== linkId);

            // Save
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/milestone/${milestoneId}/links`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ links })
            });

            const result = await response.json();
            if (result.success) {
                this.showNotification('Link deleted', 'success');
                this.refreshCard(milestone.session_id);
            } else {
                this.showNotification('Failed to delete link: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error deleting link:', error);
            this.showNotification('Failed to delete link', 'error');
        }
    }

    /**
     * Get milestone data
     */
    async getMilestone(milestoneId) {
        const response = await fetch(`${this.apiBaseUrl}/api/synergy/milestone/${milestoneId}`);
        const result = await response.json();
        if (result.success) {
            return result.milestone;
        } else {
            throw new Error(result.error || 'Failed to get milestone');
        }
    }
}

// Create global instance
if (typeof window !== 'undefined') {
    window.SynergyMilestoneInteractions = window.SynergyMilestoneInteractions || new SynergyMilestoneInteractions();
}
