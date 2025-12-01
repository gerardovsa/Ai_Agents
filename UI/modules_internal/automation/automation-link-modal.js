/**
 * AUTOMATION LINK MODAL
 * Modal interface for linking Visual Workflows (visual_automations) to threads
 * Matches synergy-sync-modal structure for consistency
 * Color theme: Blue (#3b82f6)
 */

window.ThreadManager = window.ThreadManager || {};

// Ensure a global wrapper exists early so integrations can call it before full init
window.AutomationLinkModal = window.AutomationLinkModal || {
    open: function (threadId) {
        window.__modalCallQueue = window.__modalCallQueue || [];
        window.__modalCallQueue.push({ method: 'openAutomationLinkModal', args: [threadId] });
        if (!window.__modalCallQueue._polling) {
            window.__modalCallQueue._polling = true;
            const poll = setInterval(() => {
                if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.openAutomationLinkModal === 'function') {
                    try {
                        while (window.__modalCallQueue.length > 0) {
                            const job = window.__modalCallQueue.shift();
                            if (typeof ThreadManager[job.method] === 'function') {
                                ThreadManager[job.method].apply(ThreadManager, job.args);
                            }
                        }
                    } catch (e) {
                        console.error('[AutomationLinkModal] Error flushing queue', e);
                    }
                    clearInterval(poll);
                    window.__modalCallQueue._polling = false;
                }
            }, 200);
        }
    }
};

/**
 * Open the automation link modal for a specific thread
 * @param {number} threadId - Thread ID to link automation to
 */
ThreadManager.openAutomationLinkModal = async function (threadId) {
    // Store thread ID for later use
    window._automationLinkThreadId = threadId;

    // Get thread title for display
    const threadCard = document.querySelector(`[data-thread-id="${threadId}"]`);
    const threadTitle = threadCard ?
        (threadCard.querySelector('.thread-title')?.textContent || 'Unknown Thread') :
        'Unknown Thread';

    // Fetch available automations
    let automations = [];
    try {
        const response = await fetch('/api/visual-automations', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
        });

        if (response.ok) {
            const data = await response.json();
            automations = data.automations || [];
            window._automations = automations; // Store for filtering
        }
    } catch (error) {
        console.error('Failed to fetch automations:', error);
    }

    // Generate modal HTML
    const modalHTML = `
        <div class="modal-overlay" onclick="ThreadManager.closeAutomationLinkModal(event)">
            <div class="automation-link-modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3><i class="fas fa-project-diagram"></i> Link Workflow</h3>
                    <button class="modal-close" onclick="ThreadManager.closeAutomationLinkModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="modal-body">
                    <div class="automation-link-thread-info">
                        Linking to thread: <strong>${threadTitle}</strong>
                    </div>
                    
                    <!-- Tab Navigation -->
                    <div class="automation-link-tabs">
                        <button class="automation-link-tab active" 
                                onclick="ThreadManager.switchAutomationLinkTab('existing')">
                            <i class="fas fa-link"></i> Link Existing
                        </button>
                        <button class="automation-link-tab" 
                                onclick="ThreadManager.switchAutomationLinkTab('quick')">
                            <i class="fas fa-plus-circle"></i> Quick Create
                        </button>
                        <button class="automation-link-tab" 
                                onclick="ThreadManager.switchAutomationLinkTab('full')">
                            <i class="fas fa-project-diagram"></i> Full Create
                        </button>
                    </div>
                    
                    <!-- Tab 1: Link Existing Automation -->
                    <div id="automationLinkTabExisting" class="automation-link-tab-content active">
                        <div class="automation-link-controls">
                            <div class="automation-link-search">
                                <i class="fas fa-search"></i>
                                <input type="text" id="automationLinkSearch" 
                                       placeholder="Search workflows..." 
                                       oninput="ThreadManager.filterAutomationList()">
                            </div>
                            <select id="automationLinkSort" onchange="ThreadManager.filterAutomationList()">
                                <option value="recent">Most Recent</option>
                                <option value="name">Name (A-Z)</option>
                                <option value="runs">Most Runs</option>
                                <option value="status">By Status</option>
                            </select>
                        </div>
                        
                        <div class="automation-link-list" id="automationLinkList">
                            ${ThreadManager.renderAutomationList(automations)}
                        </div>
                    </div>
                    
                    <!-- Tab 2: Quick Create -->
                    <div id="automationLinkTabQuick" class="automation-link-tab-content">
                        <div class="automation-quick-create">
                            <div class="form-group">
                                <label for="quickAutomationTitle">Workflow Name</label>
                                <input type="text" id="quickAutomationTitle" 
                                       placeholder="e.g., Daily Report Generator">
                            </div>
                            
                            <div class="form-group">
                                <label for="quickAutomationDesc">Description (Optional)</label>
                                <textarea id="quickAutomationDesc" 
                                          placeholder="Brief description of what this workflow does..."></textarea>
                            </div>
                            
                            <button class="btn btn-primary" 
                                    onclick="ThreadManager.quickCreateAutomationAndLink(${threadId})">
                                <i class="fas fa-plus-circle"></i> Create & Link Workflow
                            </button>
                        </div>
                    </div>
                    
                    <!-- Tab 3: Full Create -->
                    <div id="automationLinkTabFull" class="automation-link-tab-content">
                        <div class="automation-full-create">
                            <p>Open the full workflow builder with drag-and-drop canvas for complex automations.</p>
                            <button class="btn btn-primary" 
                                    onclick="ThreadManager.fullCreateAutomationAndLink(${threadId})">
                                <i class="fas fa-project-diagram"></i> Open Workflow Builder
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Inject modal into DOM
    const existingModal = document.querySelector('.modal-overlay');
    if (existingModal) {
        existingModal.remove();
    }

    document.body.insertAdjacentHTML('beforeend', modalHTML);
};

/**
 * Render list of automation items
 * @param {Array} automations - Array of automation objects
 * @returns {string} HTML string
 */
ThreadManager.renderAutomationList = function (automations) {
    if (!automations || automations.length === 0) {
        return `
            <div class="automation-link-empty">
                <i class="fas fa-project-diagram"></i>
                <p><strong>No Workflows Found</strong></p>
                <p>Create your first workflow using the Quick Create or Full Create tabs.</p>
            </div>
        `;
    }

    return automations.map(automation => {
        const statusClass = automation.is_active ? 'status-active' : 'status-inactive';
        const statusText = automation.is_active ? 'Active' : 'Inactive';

        const formattedDate = automation.created_at ?
            new Date(automation.created_at).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            }) : 'Unknown';

        return `
            <div class="automation-item" 
                 onclick="ThreadManager.linkToExistingAutomation('${automation.automation_id}')"
                 data-automation-id="${automation.automation_id}"
                 data-automation-name="${automation.title}"
                 data-automation-status="${automation.is_active ? 'active' : 'inactive'}">
                <div class="automation-header">
                    <div class="automation-title">${automation.title}</div>
                    <div class="automation-status ${statusClass}">${statusText}</div>
                </div>
                
                ${automation.description ? `
                    <div class="automation-desc">${automation.description}</div>
                ` : ''}
                
                <div class="automation-meta">
                    <span>
                        <i class="fas fa-calendar-alt"></i>
                        ${formattedDate}
                    </span>
                    ${automation.total_runs ? `
                        <span>
                            <i class="fas fa-play-circle"></i>
                            ${automation.total_runs} runs
                        </span>
                    ` : ''}
                    ${automation.action_count ? `
                        <span>
                            <i class="fas fa-tasks"></i>
                            ${automation.action_count} actions
                        </span>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
};

/**
 * Switch between tabs in the automation link modal
 * @param {string} tabName - 'existing', 'quick', or 'full'
 */
ThreadManager.switchAutomationLinkTab = function (tabName) {
    // Update tab buttons
    document.querySelectorAll('.automation-link-tab').forEach(tab => {
        tab.classList.remove('active');
    });

    const tabMap = {
        'existing': 0,
        'quick': 1,
        'full': 2
    };

    const activeTab = document.querySelectorAll('.automation-link-tab')[tabMap[tabName]];
    if (activeTab) {
        activeTab.classList.add('active');
    }

    // Update tab content
    document.querySelectorAll('.automation-link-tab-content').forEach(content => {
        content.classList.remove('active');
    });

    const contentMap = {
        'existing': 'automationLinkTabExisting',
        'quick': 'automationLinkTabQuick',
        'full': 'automationLinkTabFull'
    };

    const activeContent = document.getElementById(contentMap[tabName]);
    if (activeContent) {
        activeContent.classList.add('active');
    }
};

/**
 * Filter and sort automation list based on search and sort inputs
 */
ThreadManager.filterAutomationList = function () {
    const searchTerm = document.getElementById('automationLinkSearch')?.value.toLowerCase() || '';
    const sortBy = document.getElementById('automationLinkSort')?.value || 'recent';

    let filteredAutomations = window._automations || [];

    // Apply search filter
    if (searchTerm) {
        filteredAutomations = filteredAutomations.filter(automation => {
            return (automation.title?.toLowerCase().includes(searchTerm) ||
                automation.description?.toLowerCase().includes(searchTerm));
        });
    }

    // Apply sorting
    filteredAutomations = [...filteredAutomations].sort((a, b) => {
        switch (sortBy) {
            case 'name':
                return (a.title || '').localeCompare(b.title || '');

            case 'runs':
                return (b.total_runs || 0) - (a.total_runs || 0);

            case 'status':
                if (a.is_active === b.is_active) return 0;
                return a.is_active ? -1 : 1;

            case 'recent':
            default:
                return new Date(b.created_at || 0) - new Date(a.created_at || 0);
        }
    });

    // Re-render list
    const listContainer = document.getElementById('automationLinkList');
    if (listContainer) {
        listContainer.innerHTML = ThreadManager.renderAutomationList(filteredAutomations);
    }
};

/**
 * Link an existing automation to the current thread
 * @param {string} automationId - Automation ID to link
 */
ThreadManager.linkToExistingAutomation = async function (automationId) {
    const threadId = window._automationLinkThreadId;
    if (!threadId) {
        console.error('No thread ID stored for linking');
        return;
    }

    try {
        const response = await fetch(`/api/threads/${threadId}/link-automation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify({ automation_id: automationId })
        });

        if (response.ok) {
            console.log('Automation linked successfully');

            // Close modal
            ThreadManager.closeAutomationLinkModal();

            // Refresh thread card to show new badge
            if (ThreadManager.refreshThreadCard) {
                ThreadManager.refreshThreadCard(threadId);
            }

            // Show success notification
            if (window.showNotification) {
                window.showNotification('Workflow linked successfully', 'success');
            }
        } else {
            console.error('Failed to link automation');
            if (window.showNotification) {
                window.showNotification('Failed to link workflow', 'error');
            }
        }
    } catch (error) {
        console.error('Error linking automation:', error);
        if (window.showNotification) {
            window.showNotification('Error linking workflow', 'error');
        }
    }
};

/**
 * Quick create a new automation and link it to the thread
 * @param {number} threadId - Thread ID to link to
 */
ThreadManager.quickCreateAutomationAndLink = async function (threadId) {
    const title = document.getElementById('quickAutomationTitle')?.value.trim();
    const description = document.getElementById('quickAutomationDesc')?.value.trim();

    if (!title) {
        if (window.showNotification) {
            window.showNotification('Please enter a workflow name', 'warning');
        }
        return;
    }

    try {
        // Create automation via API
        const response = await fetch('/api/visual-automations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify({
                title,
                description,
                trigger: { type: 'manual' },
                actions: []
            })
        });

        if (response.ok) {
            const data = await response.json();
            const automationId = data.automation_id;

            // Link to thread
            await ThreadManager.linkToExistingAutomation(automationId);

            console.log('Automation created and linked:', automationId);
        } else {
            console.error('Failed to create automation');
            if (window.showNotification) {
                window.showNotification('Failed to create workflow', 'error');
            }
        }
    } catch (error) {
        console.error('Error creating automation:', error);
        if (window.showNotification) {
            window.showNotification('Error creating workflow', 'error');
        }
    }
};

/**
 * Open the full automation builder and link to thread after creation
 * @param {number} threadId - Thread ID to link to
 */
ThreadManager.fullCreateAutomationAndLink = function (threadId) {
    // Store thread ID for linking after creation
    sessionStorage.setItem('pendingAutomationLink', threadId);

    // Close modal
    ThreadManager.closeAutomationLinkModal();

    // Open automation builder (adjust selector as needed)
    const builderTab = document.querySelector('[data-tab="automations"]');
    if (builderTab) {
        builderTab.click();
    }

    // Show notification
    if (window.showNotification) {
        window.showNotification('Opening workflow builder...', 'info');
    }
};

/**
 * Close the automation link modal
 * @param {Event} event - Optional click event
 */
ThreadManager.closeAutomationLinkModal = function (event) {
    if (event && event.target.classList.contains('automation-link-modal')) {
        return; // Don't close if clicking inside modal content
    }

    const modal = document.querySelector('.modal-overlay');
    if (modal) {
        modal.remove();
    }

    // Clean up stored data
    delete window._automationLinkThreadId;
    delete window._automations;
};

/**
 * Global wrapper for integration files
 * Makes AutomationLinkModal available as window.AutomationLinkModal
 * MUST be at end after ThreadManager.openAutomationLinkModal is defined
 */
window.AutomationLinkModal = {
    open: function (threadId) {
        // Try immediate call
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.openAutomationLinkModal === 'function') {
            return ThreadManager.openAutomationLinkModal(threadId);
        }

        // Fallback: queue the request until ThreadManager is ready
        window.__modalCallQueue = window.__modalCallQueue || [];
        window.__modalCallQueue.push({ method: 'openAutomationLinkModal', args: [threadId] });

        // Start polling once to flush queue when available
        if (!window.__modalCallQueue._polling) {
            window.__modalCallQueue._polling = true;
            const poll = setInterval(() => {
                if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.openAutomationLinkModal === 'function') {
                    try {
                        while (window.__modalCallQueue.length > 0) {
                            const job = window.__modalCallQueue.shift();
                            if (typeof ThreadManager[job.method] === 'function') {
                                ThreadManager[job.method].apply(ThreadManager, job.args);
                            }
                        }
                    } catch (e) {
                        console.error('[AutomationLinkModal] Error flushing queue', e);
                    }
                    clearInterval(poll);
                    window.__modalCallQueue._polling = false;
                }
            }, 200);
        }
    }
};

// Persistence helper: ensure main modal function stays attached to ThreadManager
// even if ThreadManager is reassigned by other scripts
(function ensureAutomationMethodsAttached() {
    // Capture the main open function (others are helper methods, not on ThreadManager)
    const openModalFn = ThreadManager.openAutomationLinkModal;

    if (typeof openModalFn !== 'function') {
        console.warn('[AutomationLinkModal] openAutomationLinkModal not yet defined, will retry');
    }

    let attempts = 0;
    const maxAttempts = 60; // ~12 seconds
    const iv = setInterval(() => {
        attempts += 1;
        if (typeof window.ThreadManager !== 'undefined' && typeof openModalFn === 'function') {
            try {
                window.ThreadManager.openAutomationLinkModal = openModalFn;
                console.debug('[AutomationLinkModal] Attached openAutomationLinkModal to window.ThreadManager');
                clearInterval(iv);
                return;
            } catch (e) {
                console.warn('[AutomationLinkModal] attach attempt failed, will retry', e);
            }
        }

        if (attempts >= maxAttempts) {
            clearInterval(iv);
            console.warn('[AutomationLinkModal] Giving up attaching after 12 seconds');
        }
    }, 200);
})();

console.log('✅ [Automation Link Modal] Initialized with global wrapper: window.AutomationLinkModal');
