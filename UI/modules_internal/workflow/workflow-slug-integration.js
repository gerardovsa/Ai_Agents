/**
 * Workflow Slug Integration Module
 * 
 * Handles drag-and-drop linking of automation workflows to threads,
 * system prompt injection, and UI interactions.
 * 
 * Usage: Include this script after ThreadManager is defined
 */

// Global object for ThreadCardRegistry integration
window.WorkflowThreadIntegration = {
    /**
     * Render workflow badge for thread card (called by ThreadCardRegistry)
     * 
     * @param {Object} thread - Thread object with workflow_id field
     * @param {Object} config - Badge configuration {icon, color, label}
     * @returns {string} HTML string for workflow badge
     */
    renderThreadBadge(thread, config) {
        if (!thread.workflow_id) return '';

        const safeEscape = window.safeEscape || ((str) => String(str).replace(/[&<>"']/g, ''));
        const workflowTitle = thread.workflow_name || thread.workflow_title || thread.workflow_id;

        return `
            <div class="thread-item-workflow thread-item-workflow-linked" 
                 data-workflow-id="${safeEscape(thread.workflow_id)}"
                 style="display: flex; align-items: center; gap: 8px;">
                <button class="workflow-badge" 
                    style="background: #8b5cf6; color: white; border: none; padding: 6px 12px; border-radius: 6px; display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer; flex: 1;"
                        onclick="event.stopPropagation(); ThreadManager.openWorkflowDetails('${safeEscape(thread.workflow_id)}')"
                        title="${safeEscape(workflowTitle)}">
                    <i class="fas ${config.icon}"></i>
                    <span class="workflow-badge-title">${safeEscape(workflowTitle)}</span>
                </button>
                <button class="workflow-unlink" 
                        style="background: #ef4444; color: white; border: none; padding: 6px 8px; border-radius: 4px; cursor: pointer;" 
                        title="Unlink workflow" 
                        onclick="event.stopPropagation(); ThreadManager.unlinkWorkflow('${thread.id}', '${safeEscape(thread.workflow_id)}')">
                    <i class="fas fa-unlink"></i>
                </button>
            </div>
        `;
    }
};

(function () {
    'use strict';

    // API Base URL (environment-aware)
    // Reference API_BASE_URL from global scope (declared in main HTML)
    // Use window.API_BASE_URL directly (declared in main HTML)
    // No local declaration needed - access via window.API_BASE_URL    // ============================================================
    // WORKFLOW SLUG LINKING
    // ============================================================

    /**
     * Link workflow to thread (ENHANCED: Immediate badge update)
     */
    async function linkWorkflowToThread(threadId, workflowSlug, workflowId) {
        try {
            console.log(`[WORKFLOW] Linking workflow ${workflowSlug} to thread ${threadId}`);

            // Fetch workflow title from backend
            const workflowResponse = await fetch(`${API_BASE_URL}/api/automation/list?slug=${encodeURIComponent(workflowSlug)}`);
            if (!workflowResponse.ok) {
                throw new Error('Failed to fetch workflow details');
            }
            const workflowData = await workflowResponse.json();
            const workflow = workflowData.workflows && workflowData.workflows[0];
            const workflowTitle = workflow?.title || workflowSlug;

            // Find thread
            const thread = window.ThreadManager.threads.find(t => t.id === threadId);
            if (!thread) {
                console.error(`[WORKFLOW] Thread ${threadId} not found`);
                return;
            }

            // Update thread object with BOTH slug and id (for compatibility)
            thread.workflow_slug = workflowSlug;
            thread.workflow_title = workflowTitle;
            thread.workflow_id = workflowId;  // NEW: Add workflow_id for badge compatibility
            thread.workflow_name = workflowTitle;  // NEW: Add workflow_name for badge compatibility
            thread.updated = new Date().toISOString();

            // IMMEDIATE UI UPDATE: Update badge without full re-render
            updateWorkflowBadgeUI(threadId, workflowId, workflowTitle);

            // Save to backend database (async, doesn't block UI)
            saveThreadMetadata(threadId, {
                workflow_slug: workflowSlug,
                workflow_title: workflowTitle,
                workflow_id: workflowId,
                workflow_name: workflowTitle
            });

            console.log('[WORKFLOW] Successfully linked workflow to thread (badge updated immediately)');

            // Show success notification
            showNotification(`Workflow "${workflowTitle}" linked to thread`, 'success');
        } catch (error) {
            console.error('[WORKFLOW] Error linking workflow:', error);
            showNotification('Failed to link workflow', 'error');
        }
    }

    /**
     * IMMEDIATE UI update for workflow badge (no full re-render)
     */
    function updateWorkflowBadgeUI(threadId, workflowId, workflowTitle) {
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

        // Check if currently showing "Link Workflow" button
        const isUnlinked = workflowSection.classList.contains('thread-item-workflow-unlinked');

        if (isUnlinked) {
            // Replace unlinked state with linked badge
            workflowSection.classList.remove('thread-item-workflow-unlinked');
            workflowSection.classList.add('thread-item-workflow-linked');
            workflowSection.setAttribute('data-workflow-id', workflowId);

            // Update HTML to show badge
            workflowSection.innerHTML = `
                <button class="workflow-badge" style="background: #8b5cf6; color: white; border: none; padding: 6px 12px; border-radius: 6px; display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer; flex: 1;"
                    onclick="event.stopPropagation(); ThreadManager.openWorkflowDetails('${workflowId}')"
                    title="${workflowTitle}">
                    <i class="fas fa-robot"></i>
                    <span class="workflow-badge-title">${workflowTitle}</span>
                </button>
                <button class="thread-workflow-unlink" title="Unlink workflow" onclick="event.stopPropagation(); ThreadManager.unlinkWorkflow('${threadId}', '${workflowId}')">
                    <i class="fas fa-unlink"></i>
                </button>
            `;

            console.log(`✅ [WORKFLOW] Badge updated immediately for thread ${threadId}`);
        } else {
            // Already linked, just update title
            const badgeTitle = workflowSection.querySelector('.workflow-badge-title');
            if (badgeTitle) {
                badgeTitle.textContent = workflowTitle;
            }
        }
    }

    /**
     * Save thread metadata (workflow_slug, workflow_title, etc.) to backend
     */
    async function saveThreadMetadata(threadId, metadata) {
        try {
            const thread = window.ThreadManager.threads.find(t => t.id === threadId);
            if (!thread) return;

            // Merge new metadata
            Object.assign(thread, metadata);

            // Save to backend - use UPDATE endpoint
            const response = await fetch(`${API_BASE_URL}/api/threads/metadata/update`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    thread_slug: threadId,
                    workflow_slug: metadata.workflow_slug || null,
                    workflow_title: metadata.workflow_title || null,
                    internal_doc_slug: metadata.internal_doc_slug || null,
                    internal_doc_title: metadata.internal_doc_title || null
                })
            });

            const data = await response.json();
            if (!data.success) {
                console.error('[WORKFLOW] Failed to save metadata:', data.error);
            }
        } catch (error) {
            console.error('[WORKFLOW] Error saving metadata:', error);
        }
    }

    /**
     * Setup drag-drop for workflow slugs on thread info cards
     */
    function setupWorkflowSlugDropTargets() {
        // Dragover event - show drop indicator
        document.addEventListener('dragover', (e) => {
            const threadInfoCard = e.target.closest('.thread-info-container');
            const workflowSlug = e.dataTransfer.types.includes('workflow-slug');

            if (threadInfoCard && workflowSlug) {
                e.preventDefault();
                threadInfoCard.classList.add('workflow-drag-over');
            }
        });

        // Dragleave event - hide drop indicator
        document.addEventListener('dragleave', (e) => {
            const threadInfoCard = e.target.closest('.thread-info-container');
            if (threadInfoCard && !threadInfoCard.contains(e.relatedTarget)) {
                threadInfoCard.classList.remove('workflow-drag-over');
            }
        });

        // Drop event - link workflow to thread
        document.addEventListener('drop', async (e) => {
            const threadInfoCard = e.target.closest('.thread-info-container');
            const workflowSlug = e.dataTransfer.getData('workflow-slug');
            const workflowId = e.dataTransfer.getData('workflow-id');

            if (threadInfoCard && workflowSlug) {
                e.preventDefault();
                threadInfoCard.classList.remove('workflow-drag-over');

                // Extract thread ID from card
                const threadId = threadInfoCard.dataset.threadId;
                if (!threadId) {
                    console.error('[WORKFLOW] No thread ID found on thread info card');
                    return;
                }

                // Link workflow to thread
                await linkWorkflowToThread(threadId, workflowSlug, workflowId);
            }
        });

        console.log('✅ [WORKFLOW] Drag-drop handlers initialized');
    }

    // ============================================================
    // WORKFLOW ACTIONS (Open/Unlink)
    // ============================================================

    /**
     * Open workflow in automation canvas
     */
    window.openWorkflowInCanvas = async function (workflowSlug) {
        try {
            console.log(`[WORKFLOW] Opening workflow ${workflowSlug} in canvas`);

            // Switch to Automation tab
            const automationTab = document.querySelector('[data-tab="automation"]');
            if (automationTab) {
                automationTab.click();
            }

            // Wait for automation canvas to load
            setTimeout(() => {
                if (window.automationCanvas) {
                    // Load workflow by slug
                    window.automationCanvas.loadWorkflowBySlug(workflowSlug);
                } else {
                    console.error('[WORKFLOW] Automation canvas not initialized');
                    showNotification('Automation canvas not ready', 'error');
                }
            }, 500);
        } catch (error) {
            console.error('[WORKFLOW] Error opening workflow:', error);
            showNotification('Failed to open workflow', 'error');
        }
    };

    /**
     * Unlink workflow from thread
     */
    window.unlinkWorkflowFromThread = async function (threadId) {
        try {
            const thread = window.ThreadManager.threads.find(t => t.id === threadId);
            if (!thread) return;

            // Clear workflow fields
            thread.workflow_slug = null;
            thread.workflow_title = null;
            thread.updated = new Date().toISOString();

            // Save to backend
            await saveThreadMetadata(threadId, {
                workflow_slug: null,
                workflow_title: null
            });

            // Update UI
            const location = thread.location || 'prime';
            const threadInfoContainer = document.querySelector(`#thread-info-${location.replace('agent-', '')}`);
            if (threadInfoContainer) {
                threadInfoContainer.innerHTML = window.ThreadManager.renderThreadInfoContainer(
                    location,
                    threadId,
                    false
                );
            }

            showNotification('Workflow unlinked from thread', 'success');
        } catch (error) {
            console.error('[WORKFLOW] Error unlinking workflow:', error);
            showNotification('Failed to unlink workflow', 'error');
        }
    };

    // ============================================================
    // SYSTEM PROMPT SLUG INJECTION
    // ============================================================

    /**
     * Build slug context for thread to inject into system prompt
     */
    window.buildSlugContextForThread = function (thread) {
        if (!thread) return '';

        let slugContext = '';

        // 1. Synergy Session Context
        if (thread.synergy_card_id) {
            const synergyTitle = thread.synergy_card_name || thread.synergy_card_id;
            const synergyDesc = thread.synergy_card_desc || '';
            const synergyPriority = thread.synergy_card_priority || '';

            slugContext += `\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 SYNERGY PROJECT CONTEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This thread is part of a Synergy project:

**Project:** ${synergyTitle}
**Project ID:** ${thread.synergy_card_id}
${synergyDesc ? `**Description:** ${synergyDesc}` : ''}
${synergyPriority ? `**Priority:** ${synergyPriority}` : ''}

This means:
- User is working on this specific project
- Context from other threads in this project may be relevant
- Your responses should consider project goals and constraints
- Use tools: synergy_get_session(), synergy_list_threads() to access project context

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`;
        }

        // 2. Workflow Automation Context
        if (thread.workflow_slug) {
            const workflowTitle = thread.workflow_title || thread.workflow_slug;

            slugContext += `\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ AUTOMATION WORKFLOW CONTEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This thread has a linked automation workflow:

**Workflow:** ${workflowTitle}
**Workflow Slug:** ${thread.workflow_slug}

This means:
- User is discussing or working on this specific workflow
- You can access workflow details using: automation_get_workflow_by_slug('${thread.workflow_slug}')
- You can open workflow in canvas using: automation_open_workflow_in_canvas('${thread.workflow_slug}', 'Opening your workflow...')
- You can suggest improvements, debug issues, or help configure the workflow
- Use tools: automation_get_workflow_by_slug(), automation_execute_workflow(), automation_schedule_workflow()

If user asks to "show the workflow" or "open the automation", use automation_open_workflow_in_canvas().

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`;
        }

        // 3. Internal Documents Context
        if (thread.internal_doc_slug) {
            const docTitle = thread.internal_doc_title || thread.internal_doc_slug;

            slugContext += `\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 INTERNAL DOCUMENT CONTEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This thread has a linked internal document:

**Document:** ${docTitle}
**Document Slug:** ${thread.internal_doc_slug}

This means:
- User is discussing or working on this specific document
- You can access document content using: synergy_get_internal_doc('${thread.internal_doc_slug}')
- You can update document using: synergy_update_internal_doc()
- Provide answers based on document content when relevant

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`;
        }

        return slugContext;
    };

    // ============================================================
    // UPDATE THREADMANAGER TO INCLUDE NEW FIELDS
    // ============================================================

    /**
     * Enhance ThreadManager.loadThreadsFromBackend to include workflow fields
     * NOTE: As of Nov 2025, workflow fields are now included directly in loadThreadsFromBackend
     * This enhancement is kept for backward compatibility but may not be needed
     */
    if (window.ThreadManager && typeof window.ThreadManager.loadThreadsFromBackend === 'function') {
        const originalLoadThreadsFromBackend = window.ThreadManager.loadThreadsFromBackend;

        // Only enhance if the original method exists
        if (originalLoadThreadsFromBackend) {
            window.ThreadManager.loadThreadsFromBackend = async function () {
                const result = await originalLoadThreadsFromBackend.call(this);

                // Add workflow and document fields to loaded threads (if not already present)
                this.threads = this.threads.map(thread => ({
                    ...thread,
                    workflow_slug: thread.workflow_slug || null,
                    workflow_title: thread.workflow_title || null,
                    internal_doc_slug: thread.internal_doc_slug || null,
                    internal_doc_title: thread.internal_doc_title || null
                }));

                return result;
            };

            console.log('✅ [WORKFLOW] ThreadManager.loadThreadsFromBackend enhanced');
        } else {
            console.log('ℹ️ [WORKFLOW] ThreadManager.loadThreadsFromBackend already includes workflow fields');
        }
    } else {
        console.warn('⚠️ [WORKFLOW] ThreadManager.loadThreadsFromBackend not available yet - workflow fields included in base implementation');
    }

    // ============================================================
    // INITIALIZATION
    // ============================================================

    // Setup on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setupWorkflowSlugDropTargets();
        });
    } else {
        setupWorkflowSlugDropTargets();
    }

    console.log('✅ [WORKFLOW] Workflow slug integration module loaded');

    // Register with ThreadCardRegistry when ready
    if (window.ThreadCardRegistry && typeof window.ThreadCardRegistry.registerBadgeRenderer === 'function') {
        window.ThreadCardRegistry.registerBadgeRenderer('workflow_automation', {
            condition: 'thread.workflow_slug !== null',  // Fixed: Use workflow_slug column
            renderFunction: 'window.WorkflowThreadIntegration.renderThreadBadge',
            config: {
                icon: 'fa-robot',
                color: '#8b5cf6',  // PURPLE badge color (matches user request)
                label: 'Workflow',
                priority: 2
            },
            placeholderClick: 'ThreadManager.openWorkflowLinkModal'
        });
        console.log('[WorkflowSlugIntegration] Registered with ThreadCardRegistry');
    } else {
        console.warn('[WorkflowSlugIntegration] ThreadCardRegistry not available yet');

        // Retry on DOMContentLoaded
        document.addEventListener('DOMContentLoaded', () => {
            if (window.ThreadCardRegistry && typeof window.ThreadCardRegistry.registerBadgeRenderer === 'function') {
                window.ThreadCardRegistry.registerBadgeRenderer('workflow_automation', {
                    condition: 'thread.workflow_slug !== null',
                    renderFunction: 'window.WorkflowThreadIntegration.renderThreadBadge',
                    config: {
                        icon: 'fa-robot',
                        color: '#8b5cf6',
                        label: 'Workflow',
                        priority: 2
                    },
                    placeholderClick: 'ThreadManager.openWorkflowLinkModal'
                });
                console.log('[WorkflowSlugIntegration] Registered with ThreadCardRegistry (deferred)');
            }
        });
    }

})();
