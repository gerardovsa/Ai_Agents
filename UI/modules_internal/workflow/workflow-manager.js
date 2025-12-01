/**
 * FILE: UI/modules_internal/workflow/workflow-manager.js
 * PURPOSE: Central manager for Workflow and Automation integration
 * 
 * EXPORTS:
 * - WorkflowManager (class) - Manages workflow and automation integration with threads
 * 
 * DEPENDENCIES:
 * - Workflow module scripts (must be loaded first)
 * 
 * LAST MODIFIED: 2025-12-01 - Created to resolve WorkflowManager initialization
 */

class WorkflowManager {
    constructor() {
        this.initialized = false;
        this.activeWorkflows = new Map();
        this.activeAutomations = new Map();
        this.init();
    }

    async init() {
        if (this.initialized) {
            console.debug('[WorkflowManager] Already initialized');
            return;
        }

        console.log('[WorkflowManager] Initializing workflow integration...');

        // Initialize workflow thread integration if available
        if (typeof window.initializeWorkflowThreadIntegration === 'function') {
            try {
                window.initializeWorkflowThreadIntegration();
                console.log('[WorkflowManager] Thread integration initialized');
            } catch (error) {
                console.debug('[WorkflowManager] Thread integration skipped:', error.message);
            }
        }

        // Initialize automation thread integration if available
        if (typeof window.initializeAutomationThreadIntegration === 'function') {
            try {
                window.initializeAutomationThreadIntegration();
                console.log('[WorkflowManager] Automation integration initialized');
            } catch (error) {
                console.debug('[WorkflowManager] Automation integration skipped:', error.message);
            }
        }

        this.initialized = true;
        console.log('✅ [WorkflowManager] Initialization complete');
    }

    // Link workflow to thread
    linkWorkflowToThread(workflowId, threadSlug) {
        this.activeWorkflows.set(threadSlug, workflowId);
        console.log(`[WorkflowManager] Linked workflow ${workflowId} to thread ${threadSlug}`);
    }

    // Link automation to thread
    linkAutomationToThread(automationId, threadSlug) {
        this.activeAutomations.set(threadSlug, automationId);
        console.log(`[WorkflowManager] Linked automation ${automationId} to thread ${threadSlug}`);
    }

    // Get linked workflow for thread
    getLinkedWorkflow(threadSlug) {
        return this.activeWorkflows.get(threadSlug);
    }

    // Get linked automation for thread
    getLinkedAutomation(threadSlug) {
        return this.activeAutomations.get(threadSlug);
    }

    // Check if thread has linked workflow
    hasLinkedWorkflow(threadSlug) {
        return this.activeWorkflows.has(threadSlug);
    }

    // Check if thread has linked automation
    hasLinkedAutomation(threadSlug) {
        return this.activeAutomations.has(threadSlug);
    }

    // Unlink workflow from thread
    unlinkWorkflowFromThread(threadSlug) {
        const workflowId = this.activeWorkflows.get(threadSlug);
        this.activeWorkflows.delete(threadSlug);
        console.log(`[WorkflowManager] Unlinked workflow from thread ${threadSlug}`);
        return workflowId;
    }

    // Unlink automation from thread
    unlinkAutomationFromThread(threadSlug) {
        const automationId = this.activeAutomations.get(threadSlug);
        this.activeAutomations.delete(threadSlug);
        console.log(`[WorkflowManager] Unlinked automation from thread ${threadSlug}`);
        return automationId;
    }

    // Get all active workflows
    getActiveWorkflows() {
        return Array.from(this.activeWorkflows.entries());
    }

    // Get all active automations
    getActiveAutomations() {
        return Array.from(this.activeAutomations.entries());
    }
}

// Export to global scope
window.WorkflowManager = WorkflowManager;
console.log('📦 [WorkflowManager] Class loaded');
