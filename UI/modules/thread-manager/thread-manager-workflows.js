// ==================== THREAD MANAGER - WORKFLOWS MODULE ====================
/**
 * Workflow Automation Integration
 * Handles all workflow linking, filtering, and management
 */

window.ThreadManagerWorkflows = {
    /**
     * Link thread to workflow automation (orange pill)
     */
    async linkWorkflow(threadId, workflowId, workflowName) {
        try {
            const thread = this.threads.find(t => t.id === threadId);
            if (!thread) {
                if (typeof showNotification === 'function') {
                    showNotification('Thread not found', 'error');
                }
                return false;
            }

            // Update thread metadata in backend
            const resp = await fetch(`${this.apiBaseUrl}/api/threads/${threadId}/update`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: thread.title || '',
                    workflow_id: workflowId,
                    workflow_name: workflowName
                })
            });

            const data = await resp.json();
            if (data && data.success) {
                thread.workflow_id = workflowId;
                thread.workflow_name = workflowName;
                thread.updated = new Date().toISOString();

                // Use master sync to update all UI components
                if (typeof this.syncThreadLocationEverywhere === 'function') {
                    await this.syncThreadLocationEverywhere(threadId, thread.agent || 'main', {
                        addLinks: ['workflow'],
                        workflowId: workflowId,
                        workflowName: workflowName
                    });
                }

                // Refresh all thread info cards to show workflow pill
                if (typeof this.refreshAllThreadInfoCards === 'function') {
                    this.refreshAllThreadInfoCards(threadId);
                    console.log('[linkWorkflow] Refreshed thread info cards for thread:', threadId);
                }

                // CRITICAL: Also refresh agent column cards (thread-info-1, thread-info-2, thread-info-3)
                for (let i = 1; i <= 3; i++) {
                    const agentCard = document.getElementById(`thread-info-${i}`);
                    if (agentCard && agentCard.dataset.threadId === String(threadId)) {
                        const agentLocation = `agent-${i}`;
                        const newCardHTML = this.renderThreadInfoContainer(agentLocation, threadId, false);
                        if (newCardHTML) {
                            agentCard.outerHTML = newCardHTML;
                            console.log(`[linkWorkflow] Refreshed agent card thread-info-${i}`);
                        }
                    }
                }

                if (typeof showNotification === 'function') {
                    showNotification(`Linked to workflow: ${workflowName}`, 'success');
                }
                return true;
            } else {
                console.error('[linkWorkflow] Failed:', data);
                if (typeof showNotification === 'function') {
                    showNotification('Failed to link workflow', 'error');
                }
                return false;
            }
        } catch (err) {
            console.error('[linkWorkflow] Exception:', err);
            if (typeof showNotification === 'function') {
                showNotification('Error linking workflow', 'error');
            }
            return false;
        }
    },

    /**
     * Unlink workflow automation from thread
     */
    async unlinkWorkflow(threadId, workflowId) {
        try {
            const thread = this.threads.find(t => t.id === threadId);
            if (!thread) {
                if (typeof showNotification === 'function') {
                    showNotification('Thread not found', 'error');
                }
                return false;
            }

            const resp = await fetch(`${this.apiBaseUrl}/api/threads/${threadId}/update`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: thread.title || '',
                    workflow_id: null,
                    workflow_name: null
                })
            });

            const data = await resp.json();
            if (data && data.success) {
                thread.workflow_id = null;
                thread.workflow_name = null;
                thread.workflow_slug = null;
                thread.workflow_title = null;
                thread.updated = new Date().toISOString();

                // IMMEDIATE UI UPDATE: Remove badge without full re-render
                this.updateWorkflowBadgeRemove(threadId);

                // Use master sync to update all UI components
                if (typeof this.syncThreadLocationEverywhere === 'function') {
                    await this.syncThreadLocationEverywhere(threadId, thread.agent || 'main', {
                        removeLinks: ['workflow']
                    });
                }

                if (typeof showNotification === 'function') {
                    showNotification('Workflow unlinked', 'success');
                }
                return true;
            } else {
                console.error('[unlinkWorkflow] Failed:', data);
                if (typeof showNotification === 'function') {
                    showNotification('Failed to unlink workflow', 'error');
                }
                return false;
            }
        } catch (err) {
            console.error('[unlinkWorkflow] Exception:', err);
            if (typeof showNotification === 'function') {
                showNotification('Error unlinking workflow', 'error');
            }
            return false;
        }
    },

    /**
     * IMMEDIATE UI UPDATE: Remove workflow badge (no full re-render)
     */
    updateWorkflowBadgeRemove(threadId) {
        // Find thread item in DOM
        const threadCard = document.querySelector(`[data-thread-id="${threadId}"]`);
        if (!threadCard) {
            console.warn(`[WORKFLOW] Thread card not found for ${threadId}`);
            return;
        }

        // Find the workflow section
        const workflowSection = threadCard.querySelector('.thread-item-workflow');
        if (!workflowSection) {
            console.warn(`[WORKFLOW] Workflow section not found in thread card`);
            return;
        }

        // Check if currently showing linked badge
        const isLinked = workflowSection.classList.contains('thread-item-workflow-linked');
        
        if (isLinked) {
            // Replace linked badge with unlinked state
            workflowSection.classList.remove('thread-item-workflow-linked');
            workflowSection.classList.add('thread-item-workflow-unlinked');
            workflowSection.removeAttribute('data-workflow-id');
            
            // Update HTML to show "Link Workflow" button
            workflowSection.innerHTML = `
                <i class="fas fa-robot"></i>
                <span>Link Workflow</span>
            `;
            
            // Re-add click handler
            workflowSection.onclick = (e) => {
                e.stopPropagation();
                this.openWorkflowLinkModal(threadId);
            };
            
            console.log(`✅ [WORKFLOW] Badge removed immediately for thread ${threadId}`);
        }
    },

    /**
     * Open workflow linking modal (shows available workflows)
     */
    async openWorkflowLinkModal(threadId) {
        console.log('[openWorkflowLinkModal] Opening for thread:', threadId);

        // Get thread data
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            console.error('[openWorkflowLinkModal] Thread not found:', threadId);
            if (typeof showNotification === 'function') {
                showNotification('Thread not found', 'error');
            }
            return;
        }

        // Fetch available workflows from automation API
        let workflows = [];
        try {
            const response = await fetch('/api/automation/list', {
                headers: {
                    'Authorization': `Bearer ${UserAuth.token || ''}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                workflows = data.workflows || [];
                console.log('[openWorkflowLinkModal] Fetched workflows:', workflows.length);
            } else {
                console.error('[openWorkflowLinkModal] Failed to fetch workflows:', response.status);
            }
        } catch (err) {
            console.error('[openWorkflowLinkModal] Error fetching workflows:', err);
        }

        const modalHTML = `
            <div class="modal-overlay" id="workflowLinkModalOverlay" onclick="if(event.target.id === 'workflowLinkModalOverlay') document.getElementById('workflowLinkModalOverlay').remove()">
                <div class="synergy-sync-modal" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h3><i class="fas fa-robot"></i> Link to Workflow</h3>
                        <button class="modal-close" onclick="document.getElementById('workflowLinkModalOverlay').remove()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <div class="modal-body">
                        <!-- Thread Info -->
                        <div class="synergy-sync-thread-info">
                            <strong>Thread:</strong> ${thread.title || 'Untitled'}
                        </div>

                        ${workflows.length === 0 ? `
                            <div class="synergy-sync-empty">
                                <i class="fas fa-inbox"></i>
                                <p>No workflows available</p>
                                <p style="font-size: 12px; color: var(--text-muted);">Create a workflow in the Visual Automation Canvas first</p>
                            </div>
                        ` : `
                            <!-- Search and Sort -->
                            <div class="synergy-sync-controls">
                                <div class="synergy-sync-search">
                                    <i class="fas fa-search"></i>
                                    <input type="text" id="workflowLinkSearch" placeholder="Search workflows...">
                                </div>
                                <select id="workflowLinkSort" onchange="ThreadManager.filterWorkflows()">
                                    <option value="recent">Recent</option>
                                    <option value="title">Title</option>
                                    <option value="status">Status</option>
                                    <option value="category">Category</option>
                                </select>
                            </div>

                            <!-- Workflow List -->
                            <div class="synergy-sync-list" id="workflowLinkList">
                                ${this.renderWorkflowLinkList(workflows)}
                            </div>
                        `}
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Add search listener
        const searchInput = document.getElementById('workflowLinkSearch');
        if (searchInput) {
            searchInput.addEventListener('input', () => this.filterWorkflows());
        }

        // Store thread ID and workflows for later use
        window._workflowLinkThreadId = threadId;
        window._workflows = workflows;
    },

    /**
     * Render workflow list for linking
     */
    renderWorkflowLinkList(workflows) {
        if (!workflows || workflows.length === 0) {
            return '<div class="synergy-sync-empty"><i class="fas fa-inbox"></i><p>No workflows found</p></div>';
        }

        return workflows.map(workflow => {
            const status = workflow.status || 'draft';
            const category = workflow.category || 'other';
            const statusColors = {
                'draft': '#6B7280',
                'active': '#10B981',
                'paused': '#F59E0B',
                'archived': '#EF4444'
            };
            const statusColor = statusColors[status] || '#6B7280';
            const updatedDate = workflow.updated_at ? new Date(workflow.updated_at).toLocaleDateString() : 'Never';
            const shapeCount = workflow.ui_json?.shapes?.length || 0;

            return `
                <div class="synergy-session-item" onclick="ThreadManager.selectWorkflowToLink('${workflow.slug}', '${workflow.id || workflow.slug}', '${(workflow.title || 'Untitled').replace(/'/g, "\\'")}')">
                    <div class="synergy-session-item-header">
                        <div class="synergy-session-item-icon" style="background: #f97316;">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="synergy-session-item-title">
                            ${workflow.title || 'Untitled Workflow'}
                        </div>
                        <div class="synergy-session-item-badge" style="background: ${statusColor};">
                            ${status}
                        </div>
                    </div>
                    <div class="synergy-session-item-meta">
                        <span><i class="fas fa-shapes"></i> ${shapeCount} shapes</span>
                        <span><i class="fas fa-folder"></i> ${category}</span>
                        <span><i class="fas fa-clock"></i> ${updatedDate}</span>
                    </div>
                    <div class="synergy-session-item-slug">
                        <i class="fas fa-hashtag"></i> ${workflow.slug}
                    </div>
                    ${workflow.description ? `<div class="synergy-session-item-desc">${workflow.description}</div>` : ''}
                </div>
            `;
        }).join('');
    },

    /**
     * Select workflow to link to thread
     */
    async selectWorkflowToLink(workflowSlug, workflowId, workflowTitle) {
        const threadId = window._workflowLinkThreadId;
        if (!threadId) {
            console.error('[selectWorkflowToLink] No thread ID stored');
            return;
        }

        console.log('[selectWorkflowToLink] Linking:', { threadId, workflowSlug, workflowId, workflowTitle });

        // Close modal
        document.getElementById('workflowLinkModalOverlay')?.remove();

        // Link workflow
        await this.linkWorkflow(threadId, workflowId, workflowTitle);
    },

    /**
     * Filter workflows in link modal
     */
    filterWorkflows() {
        const searchInput = document.getElementById('workflowLinkSearch');
        const sortSelect = document.getElementById('workflowLinkSort');
        const listContainer = document.getElementById('workflowLinkList');

        if (!searchInput || !sortSelect || !listContainer) return;

        let workflows = window._workflows || [];
        const searchTerm = searchInput.value.toLowerCase();
        const sortBy = sortSelect.value;

        // Filter by search term
        if (searchTerm) {
            workflows = workflows.filter(workflow => {
                const title = (workflow.title || '').toLowerCase();
                const description = (workflow.description || '').toLowerCase();
                const slug = (workflow.slug || '').toLowerCase();
                const category = (workflow.category || '').toLowerCase();

                return title.includes(searchTerm) ||
                    description.includes(searchTerm) ||
                    slug.includes(searchTerm) ||
                    category.includes(searchTerm);
            });
        }

        // Sort workflows
        workflows.sort((a, b) => {
            switch (sortBy) {
                case 'title':
                    return (a.title || '').localeCompare(b.title || '');
                case 'status':
                    return (a.status || '').localeCompare(b.status || '');
                case 'category':
                    return (a.category || '').localeCompare(b.category || '');
                case 'recent':
                default:
                    return new Date(b.updated_at || 0) - new Date(a.updated_at || 0);
            }
        });

        // Re-render list
        listContainer.innerHTML = this.renderWorkflowLinkList(workflows);
    },

    /**
     * Open workflow details (shows workflow configuration)
     */
    openWorkflowDetails(workflowId) {
        // TODO: Implement workflow details modal
        if (typeof showNotification === 'function') {
            showNotification(`Opening workflow: ${workflowId}`, 'info');
        }
        console.log(`[WorkflowDetails] Opening workflow ${workflowId}`);
    }
};

// Merge into main ThreadManager object
Object.assign(window.ThreadManager, window.ThreadManagerWorkflows);

console.log('✅ ThreadManager-Workflows module loaded and merged');