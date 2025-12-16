/**
 * Workflow Link Modal
 * Implements the modal interface for linking threads to Automated Workflows (automation_workflows table)
 * 
 * Structure matches synergy-sync-modal for consistency:
 * - Three-tab interface (Link Existing / Quick Create / Full Create)
 * - Search and filter controls
 * - Rich workflow item cards with metadata
 * - Professional dark theme styling
 * 
 * Database: automation_workflows table (workflow_id UUID, slug unique)
 */

(function () {
    'use strict';

    // Initialize ThreadManager if not available
    window.ThreadManager = window.ThreadManager || {};

    // Ensure a global wrapper exists early so integrations can call it
    window.WorkflowLinkModal = window.WorkflowLinkModal || {
        open: function (threadId) {
            window.__modalCallQueue = window.__modalCallQueue || [];
            window.__modalCallQueue.push({ method: 'openWorkflowLinkModal', args: [threadId] });
            if (!window.__modalCallQueue._polling) {
                window.__modalCallQueue._polling = true;
                const poll = setInterval(() => {
                    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.openWorkflowLinkModal === 'function') {
                        try {
                            while (window.__modalCallQueue.length > 0) {
                                const job = window.__modalCallQueue.shift();
                                if (typeof ThreadManager[job.method] === 'function') {
                                    ThreadManager[job.method].apply(ThreadManager, job.args);
                                }
                            }
                        } catch (e) {
                            console.error('[WorkflowLinkModal] Error flushing queue', e);
                        }
                        clearInterval(poll);
                        window.__modalCallQueue._polling = false;
                    }
                }, 200);
            }
        }
    };

    /**
     * Open Automated Workflow Link Modal
     * @param {string} threadId - Thread ID to link workflow to
     */
    window.ThreadManager.openWorkflowLinkModal = async function (threadId) {
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            if (typeof showNotification === 'function') {
                showNotification('Thread not found', 'error');
            }
            return;
        }

        // Fetch all automation workflows
        let workflows = [];
        try {
            // Backend exposes production workflows at `/api/automation/workflows/list`
            const resp = await fetch(`${this.apiBaseUrl}/api/automation/workflows/list`);
            const data = await resp.json();
            console.log('[Workflow Link Modal] Fetched workflows:', data);

            if (Array.isArray(data)) {
                workflows = data;
            } else if (data && data.success && Array.isArray(data.workflows)) {
                workflows = data.workflows;
            } else if (data && Array.isArray(data.workflows)) {
                workflows = data.workflows;
            }

            console.log('[Workflow Link Modal] Parsed workflows:', workflows.length, 'workflows');
        } catch (err) {
            console.error('[Workflow Link Modal] Failed to fetch workflows:', err);
        }

        const modalHTML = `
            <div class="modal-overlay" id="workflowLinkModalOverlay" onclick="if(event.target.id === 'workflowLinkModalOverlay') { event.stopPropagation(); document.getElementById('workflowLinkModalOverlay').remove(); }">
                <div class="workflow-link-modal" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h3><i class="fas fa-robot"></i> Link to Automated Workflow</h3>
                        <button class="modal-close" onclick="event.stopPropagation(); event.preventDefault(); const overlay = document.getElementById('workflowLinkModalOverlay'); if(overlay) overlay.remove();">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <div class="modal-body">
                        <!-- Thread Info -->
                        <div class="workflow-link-thread-info">
                            <strong>Thread:</strong> ${thread.title || 'Untitled'}
                        </div>

                        <!-- Tab Navigation -->
                        <div class="workflow-link-tabs">
                            <button class="workflow-link-tab active" data-tab="link" onclick="ThreadManager.switchWorkflowLinkTab('link')">
                                <i class="fas fa-link"></i> Link to Existing
                            </button>
                            <button class="workflow-link-tab" data-tab="quick" onclick="ThreadManager.switchWorkflowLinkTab('quick')">
                                <i class="fas fa-bolt"></i> Quick Create
                            </button>
                            <button class="workflow-link-tab" data-tab="full" onclick="ThreadManager.switchWorkflowLinkTab('full')">
                                <i class="fas fa-plus-circle"></i> Full Create
                            </button>
                        </div>

                        <!-- Tab Content: Link to Existing -->
                        <div class="workflow-link-tab-content active" data-tab-content="link">
                            ${workflows.length === 0 ? `
                                <div class="workflow-link-empty">
                                    <i class="fas fa-inbox"></i>
                                    <p>No automated workflows available</p>
                                    <p style="font-size: 12px; color: var(--text-muted);">Create one using Quick Create or Full Create tabs</p>
                                </div>
                            ` : `
                                <!-- Search and Sort -->
                                <div class="workflow-link-controls">
                                    <div class="workflow-link-search">
                                        <i class="fas fa-search"></i>
                                        <input type="text" id="workflowLinkSearch" placeholder="Search workflows...">
                                    </div>
                                    <select id="workflowLinkSort" onchange="ThreadManager.filterWorkflowList()">
                                        <option value="recent">Recent</option>
                                        <option value="name">Name</option>
                                        <option value="status">Status</option>
                                    </select>
                                </div>

                                <!-- Workflow List -->
                                <div class="workflow-link-list" id="workflowLinkList">
                                    ${this.renderWorkflowList(workflows)}
                                </div>
                            `}
                        </div>

                        <!-- Tab Content: Quick Create -->
                        <div class="workflow-link-tab-content" data-tab-content="quick">
                            <div class="workflow-quick-create">
                                <div class="form-group">
                                    <label for="workflowQuickName">Workflow Name <span style="color: var(--accent-error);">*</span></label>
                                    <input type="text" id="workflowQuickName" placeholder="Enter workflow name..." value="${thread.title || ''}" autofocus>
                                </div>
                                <div class="form-group">
                                    <label for="workflowQuickDesc">Description <span style="color: var(--text-muted); font-weight: normal;">(optional)</span></label>
                                    <textarea id="workflowQuickDesc" placeholder="Brief description..." rows="3"></textarea>
                                </div>
                                <button class="btn-primary" onclick="ThreadManager.quickCreateWorkflowAndLink('${threadId}')">
                                    <i class="fas fa-bolt"></i> Create & Link
                                </button>
                            </div>
                        </div>

                        <!-- Tab Content: Full Create -->
                        <div class="workflow-link-tab-content" data-tab-content="full">
                            <div class="workflow-full-create">
                                <p style="margin-bottom: 16px; color: var(--text-secondary);">
                                    <i class="fas fa-info-circle"></i> Opens the full Automated Workflow creation interface with all options.
                                </p>
                                <button class="btn-primary" onclick="ThreadManager.fullCreateWorkflowAndLink('${threadId}')">
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
        const searchInput = document.getElementById('workflowLinkSearch');
        if (searchInput) {
            searchInput.addEventListener('input', () => this.filterWorkflowList());
        }

        // Store thread ID and workflows for later use
        window._workflowLinkThreadId = threadId;
        window._workflows = workflows;
    };

    /**
     * Render workflow list for linking
     */
    window.ThreadManager.renderWorkflowList = function (workflows) {
        if (!workflows || workflows.length === 0) {
            return '<div class="workflow-link-empty"><i class="fas fa-inbox"></i><p>No workflows found</p></div>';
        }

        return workflows.map(workflow => {
            const name = workflow.name || workflow.title || 'Untitled';
            const desc = workflow.description || 'No description';
            const status = workflow.status || 'active';
            const slug = workflow.slug || workflow.workflow_id;
            const lastRun = workflow.last_run ? new Date(workflow.last_run).toLocaleDateString() : 'Never';
            const runCount = workflow.run_count || 0;
            const successRate = workflow.success_rate ? `${(workflow.success_rate * 100).toFixed(0)}%` : 'N/A';

            return `
                <div class="workflow-item" 
                     data-workflow-id="${workflow.workflow_id}" 
                     data-name="${name.toLowerCase()}"
                     data-status="${status}"
                     onclick="ThreadManager.linkToExistingWorkflow('${workflow.workflow_id}')">
                    <div class="workflow-header">
                        <span class="workflow-name">${name}</span>
                        <span class="workflow-status status-${status}">${status}</span>
                    </div>
                    <div class="workflow-desc">${desc}</div>
                    <div class="workflow-meta">
                        <span><i class="fas fa-circle" style="color: ${status === 'active' ? 'var(--accent-success)' : 'var(--text-muted)'}; font-size: 8px;"></i> ${status}</span>
                        <span><i class="fas fa-clock"></i> ${lastRun}</span>
                        ${runCount > 0 ? `<span title="${runCount} executions"><i class="fas fa-play-circle"></i> ${runCount}</span>` : ''}
                        ${successRate !== 'N/A' ? `<span title="Success rate"><i class="fas fa-check-circle"></i> ${successRate}</span>` : ''}
                        <span title="Slug: ${slug}"><i class="fas fa-tag"></i> ${slug}</span>
                    </div>
                </div>
            `;
        }).join('');
    };

    /**
     * Switch tabs in modal
     */
    window.ThreadManager.switchWorkflowLinkTab = function (tabName) {
        document.querySelectorAll('.workflow-link-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        document.querySelectorAll('.workflow-link-tab-content').forEach(content => {
            content.classList.toggle('active', content.dataset.tabContent === tabName);
        });
    };

    /**
     * Filter workflows based on search and sort
     */
    window.ThreadManager.filterWorkflowList = function () {
        const searchTerm = document.getElementById('workflowLinkSearch')?.value?.toLowerCase() || '';
        const sortBy = document.getElementById('workflowLinkSort')?.value || 'recent';
        const workflowItems = document.querySelectorAll('.workflow-item');

        // Filter
        workflowItems.forEach(item => {
            const name = item.dataset.name || '';
            const matches = name.includes(searchTerm);
            item.style.display = matches ? 'block' : 'none';
        });

        // Sort visible items
        const visibleItems = Array.from(workflowItems).filter(item => item.style.display !== 'none');
        const container = document.getElementById('workflowLinkList');

        if (sortBy === 'name') {
            visibleItems.sort((a, b) => (a.dataset.name || '').localeCompare(b.dataset.name || ''));
        } else if (sortBy === 'status') {
            visibleItems.sort((a, b) => (a.dataset.status || '').localeCompare(b.dataset.status || ''));
        }

        // Re-append sorted items
        visibleItems.forEach(item => container.appendChild(item));
    };

    /**
     * Link to existing workflow
     */
    window.ThreadManager.linkToExistingWorkflow = async function (workflowId) {
        const threadId = window._workflowLinkThreadId;
        if (!threadId) {
            console.error('[Workflow Link Modal] No thread ID stored');
            return;
        }

        try {
            const resp = await fetch(`${this.apiBaseUrl}/api/threads/${threadId}/link-workflow`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ workflow_id: workflowId })
            });

            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

            const data = await resp.json();
            console.log('[Workflow Link Modal] Linked successfully:', data);

            if (typeof showNotification === 'function') {
                showNotification('Workflow linked successfully', 'success');
            }

            // Close modal
            document.getElementById('workflowLinkModalOverlay')?.remove();

            // Refresh thread display
            if (this.loadThreads) {
                await this.loadThreads();
            }
        } catch (err) {
            console.error('[Workflow Link Modal] Failed to link workflow:', err);
            if (typeof showNotification === 'function') {
                showNotification('Failed to link workflow: ' + err.message, 'error');
            }
        }
    };

    /**
     * Quick create workflow and link
     */
    window.ThreadManager.quickCreateWorkflowAndLink = async function (threadId) {
        const name = document.getElementById('workflowQuickName')?.value?.trim();
        const description = document.getElementById('workflowQuickDesc')?.value?.trim();

        if (!name) {
            if (typeof showNotification === 'function') {
                showNotification('Workflow name is required', 'error');
            }
            return;
        }

        try {
            // Create workflow
            // Create via the compatible save endpoint
            const createResp = await fetch(`${this.apiBaseUrl}/api/automation/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description })
            });

            if (!createResp.ok) throw new Error(`HTTP ${createResp.status}`);

            const workflow = await createResp.json();
            console.log('[Workflow Link Modal] Created workflow:', workflow);

            // Link to thread - check multiple possible ID field names
            const workflowId = workflow.workflow_id || workflow.automation_id || workflow.id || workflow.slug;
            if (!workflowId) {
                console.error('[Workflow Link Modal] No valid ID in response:', workflow);
                throw new Error('Server response missing workflow ID');
            }

            await this.linkToExistingWorkflow(workflowId);
        } catch (err) {
            console.error('[Workflow Link Modal] Failed to quick create:', err);
            if (typeof showNotification === 'function') {
                showNotification('Failed to create workflow: ' + err.message, 'error');
            }
        }
    };

    /**
     * Full create workflow and link
     */
    window.ThreadManager.fullCreateWorkflowAndLink = function (threadId) {
        // Store thread ID for later linking
        window._workflowLinkThreadId = threadId;

        // Close modal
        document.getElementById('workflowLinkModalOverlay')?.remove();

        // Open full workflow creator (implement based on your app's workflow creation UI)
        if (typeof showNotification === 'function') {
            showNotification('Full workflow creator not yet implemented', 'info');
        }

        console.log('[Workflow Link Modal] Full create requested for thread:', threadId);
    };

    /**
     * Global wrapper for integration files
     * Makes WorkflowLinkModal available as window.WorkflowLinkModal
     * MUST be at end after ThreadManager.openWorkflowLinkModal is defined
     */
    window.WorkflowLinkModal = {
        open: function (threadId) {
            // Try immediate call
            if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.openWorkflowLinkModal === 'function') {
                return ThreadManager.openWorkflowLinkModal(threadId);
            }

            // Fallback: queue until available
            window.__modalCallQueue = window.__modalCallQueue || [];
            window.__modalCallQueue.push({ method: 'openWorkflowLinkModal', args: [threadId] });

            if (!window.__modalCallQueue._polling) {
                window.__modalCallQueue._polling = true;
                const poll = setInterval(() => {
                    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.openWorkflowLinkModal === 'function') {
                        try {
                            while (window.__modalCallQueue.length > 0) {
                                const job = window.__modalCallQueue.shift();
                                if (typeof ThreadManager[job.method] === 'function') {
                                    ThreadManager[job.method].apply(ThreadManager, job.args);
                                }
                            }
                        } catch (e) {
                            console.error('[WorkflowLinkModal] Error flushing queue', e);
                        }
                        clearInterval(poll);
                        window.__modalCallQueue._polling = false;
                    }
                }, 200);
            }
        }
    };

    console.log('✅ [Workflow Link Modal] Initialized with global wrapper: window.WorkflowLinkModal');
})();
