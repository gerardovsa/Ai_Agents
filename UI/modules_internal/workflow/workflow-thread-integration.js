/**
 * FILE: UI/modules/workflow/workflow-thread-integration.js
 * PURPOSE: Workflow thread card integration (badge rendering, linking)
 * 
 * EXPORTS:
 * - ThreadManager.renderWorkflowBadge() - Render workflow badge HTML
 * - ThreadManager.openWorkflowLinkModal() - Open workflow linking modal
 * - ThreadManager.openWorkflowDetails() - Open workflow details
 * 
 * LAST MODIFIED: 2025-11-29 - Created for ThreadCardRegistry integration
 */

// Wait for ThreadManager to be available
function initWorkflowThreadIntegration() {
    if (typeof ThreadManager === 'undefined') {
        console.warn('[Workflow Thread Integration] ThreadManager not yet loaded, will retry...');
        return false;
    }

    /**
     * Render workflow badge for thread card
     * @param {Object} thread - Thread object with workflow_id and workflow_name
     * @param {Object} config - Badge configuration from manifest
     * @returns {string} HTML for workflow badge
     */
    ThreadManager.renderWorkflowBadge = function (thread, config) {
        const workflowId = thread.workflow_id;
        const workflowName = thread.workflow_name || workflowId;
        const safeEscape = window.safeEscape || ((str) => String(str).replace(/[&<>"']/g, ''));

        return `
            <div class="thread-item-workflow thread-item-workflow-linked" data-workflow-id="${safeEscape(workflowId)}">
                <button class="workflow-badge" 
                    style="background: ${config.color || '#f97316'}; color: white; border: none; padding: 6px 12px; border-radius: 6px; display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer; flex: 1;"
                    onclick="event.stopPropagation(); ThreadManager.openWorkflowDetails('${safeEscape(workflowId)}')"
                    title="${safeEscape(workflowName)}">
                    <i class="fas ${config.icon || 'fa-robot'}"></i>
                    <span class="workflow-badge-title">${safeEscape(workflowName)}</span>
                </button>
                <button class="thread-workflow-unlink" 
                    title="Unlink workflow" 
                    onclick="event.stopPropagation(); ThreadManager.unlinkWorkflow('${thread.id}', '${safeEscape(workflowId)}')">
                    <i class="fas fa-unlink"></i>
                </button>
            </div>
        `;
    };

    /**
     * Open workflow linking modal
     * NOTE: Implementation is in workflow-link-modal.js
     * This integration file provides drag-and-drop support only
     */

    /**
     * Open workflow details
     * @param {string} workflowId - Workflow ID to show details for
     */
    ThreadManager.openWorkflowDetails = function (workflowId) {
        console.log('[Workflow] Opening details for workflow:', workflowId);
        // TODO: Implement workflow details view
        alert(`Workflow details for ${workflowId} not yet implemented. Coming soon!`);
    };

    /**
     * Unlink workflow from thread
     * @param {string} threadId - Thread ID
     * @param {string} workflowId - Workflow ID to unlink
     */
    ThreadManager.unlinkWorkflow = function (threadId, workflowId) {
        console.log('[Workflow] Unlinking workflow', workflowId, 'from thread', threadId);
        // TODO: Implement workflow unlinking
        alert('Workflow unlinking not yet implemented. Coming soon!');
    };

    /**
     * Link workflow to thread
     * @param {string} workflowSlug - Workflow slug from drag event
     * @param {string} threadId - Thread ID to link to
     * @param {string} location - Drop location
     */
    ThreadManager.linkWorkflowToThread = async function (workflowSlug, threadId, location) {
        console.log('[Workflow] Linking workflow', workflowSlug, 'to thread', threadId, 'at', location);
        // TODO: Implement workflow linking via drag-drop
        alert('Workflow drag-drop linking not yet implemented. Coming soon!');
    };

    console.log('[Workflow Thread Integration] Loaded successfully');
    return true;
}

// Try to initialize immediately
if (!initWorkflowThreadIntegration()) {
    // If ThreadManager not ready, wait for it
    console.log('[Workflow Thread Integration] Waiting for ThreadManager...');

    // Check every 100ms for up to 5 seconds
    let attempts = 0;
    const maxAttempts = 50;

    const checkInterval = setInterval(() => {
        attempts++;

        if (initWorkflowThreadIntegration()) {
            console.log('[Workflow Thread Integration] Initialized after', attempts * 100, 'ms');
            clearInterval(checkInterval);
        } else if (attempts >= maxAttempts) {
            console.error('[Workflow Thread Integration] ThreadManager never loaded - timeout after 5 seconds');
            clearInterval(checkInterval);
        }
    }, 100);
}
