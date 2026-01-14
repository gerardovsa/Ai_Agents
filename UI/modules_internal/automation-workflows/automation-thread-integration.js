/**
 * FILE: UI/modules_internal/automation-workflows/automation-thread-integration.js
 * PURPOSE: Automation badge rendering and drag-and-drop integration for thread cards
 * 
 * DEPENDENCIES:
 * - thread-card-registry.js (ThreadCardRegistry global)
 * - thread-manager-ui.js (ThreadManager global)
 * 
 * EXPORTS:
 * - window.AutomationThreadIntegration.renderThreadBadge() - Render linked automation badge
 * - window.AutomationThreadIntegration.openAutomation() - Open automation details
 * - window.AutomationThreadIntegration.unlinkAutomation() - Unlink automation from thread
 * - window.AutomationThreadIntegration.openLinkModal() - Show modal to link automation
 * 
 * USED BY:
 * - ThreadCardRegistry (badge rendering system)
 * - Thread info cards (UI links row)
 * 
 * NOTES:
 * - Registers with ThreadCardRegistry on load
 * - Blue badge color (#3b82f6) for automation
 * - Supports drag-and-drop automation slugs onto threads
 * 
 * LAST MODIFIED: 2025-11-29 - Created module for automation badge integration
 */

window.AutomationThreadIntegration = {
    /**
     * Render linked automation badge for thread card
     * 
     * @param {Object} thread - Thread object with automation_slug field
     * @param {Object} config - Badge configuration {icon, color, label}
     * @returns {string} HTML string for automation badge
     */
    renderThreadBadge(thread, config) {
        if (!thread.automation_slug) return '';

        const safeEscape = window.safeEscape || ((str) => String(str).replace(/[&<>"']/g, ''));
        const automationTitle = thread.automation_title || thread.automation_slug;

        return `
            <div class="thread-item-automation thread-item-automation-linked" 
                 data-automation-id="${safeEscape(thread.automation_slug)}"
                 style="display: flex; align-items: center; gap: 8px;">
                <button class="automation-badge" 
                        style="background: ${config.color}; color: white; border: none; padding: 6px 12px; border-radius: 6px; display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer; flex: 1;"
                        onclick="event.stopPropagation(); window.AutomationThreadIntegration.openAutomation('${safeEscape(thread.automation_slug)}')"
                        title="${safeEscape(automationTitle)}">
                    <i class="fas ${config.icon}"></i>
                    <span class="automation-badge-title">${safeEscape(automationTitle)}</span>
                </button>
                <button class="automation-unlink" 
                        style="background: #ef4444; color: white; border: none; padding: 6px 8px; border-radius: 4px; cursor: pointer;" 
                        title="Unlink automation" 
                        onclick="event.stopPropagation(); window.AutomationThreadIntegration.unlinkAutomation('${thread.id}', '${safeEscape(thread.automation_slug)}')">
                    <i class="fas fa-unlink"></i>
                </button>
            </div>
        `;
    },

    /**
     * Open automation details modal
     * 
     * @param {string} slug - Automation slug identifier
     */
    openAutomation(slug) {
        console.log('[AutomationThreadIntegration] Opening automation:', slug);

        // TODO: Implement automation details modal
        if (window.showNotification) {
            window.showNotification(`Automation: ${slug}`, 'info');
        }

        // Placeholder - open automation details in modal or side panel
        alert(`TODO: Open automation details for ${slug}`);
    },

    /**
     * Unlink automation from thread
     * 
     * @param {string} threadId - Thread ID
     * @param {string} slug - Automation slug to unlink
     */
    async unlinkAutomation(threadId, slug) {
        console.log('[AutomationThreadIntegration] Unlinking automation:', { threadId, slug });

        try {
            const response = await fetch(`${window.API_BASE_URL || ''}/api/automation/${slug}/unlink-thread`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ thread_id: threadId })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || 'Failed to unlink automation');
            }

            console.log('[AutomationThreadIntegration] Unlink successful');

            if (window.showNotification) {
                window.showNotification('Automation unlinked successfully', 'success');
            }

            // Refresh thread card to show placeholder
            if (window.ThreadManager?.refreshThreadCard) {
                window.ThreadManager.refreshThreadCard(threadId);
            }
        } catch (error) {
            console.error('[AutomationThreadIntegration] Unlink failed:', error);

            if (window.showNotification) {
                window.showNotification(`Failed to unlink automation: ${error.message}`, 'error');
            }
        }
    },

    /**
     * Open modal to link automation to thread
     * 
     * @param {string} threadId - Thread ID to link automation to
     */
    openLinkModal(threadId) {
        console.log('[AutomationThreadIntegration] Opening link modal for thread:', threadId);

        // Open the new Automation Link Modal UI
        if (window.AutomationLinkModal && typeof window.AutomationLinkModal.open === 'function') {
            window.AutomationLinkModal.open(threadId);
        } else {
            console.error('[AutomationThreadIntegration] AutomationLinkModal not available');
            if (window.showNotification) {
                window.showNotification('Automation modal not loaded', 'error');
            }
        }
    },

    /**
     * Link automation to thread
     * 
     * @param {string} threadId - Thread ID
     * @param {string} slug - Automation slug to link
     */
    async linkAutomation(threadId, slug) {
        console.log('[AutomationThreadIntegration] Linking automation:', { threadId, slug });

        try {
            const response = await fetch(`${window.API_BASE_URL || ''}/api/automation/${slug}/link-thread`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ thread_id: threadId })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || 'Failed to link automation');
            }

            console.log('[AutomationThreadIntegration] Link successful');

            if (window.showNotification) {
                window.showNotification('Automation linked successfully', 'success');
            }

            // Refresh thread card to show badge
            if (window.ThreadManager?.refreshThreadCard) {
                window.ThreadManager.refreshThreadCard(threadId);
            }
        } catch (error) {
            console.error('[AutomationThreadIntegration] Link failed:', error);

            if (window.showNotification) {
                window.showNotification(`Failed to link automation: ${error.message}`, 'error');
            }
        }
    }
};

// Register with ThreadCardRegistry when ready
if (window.ThreadCardRegistry && typeof window.ThreadCardRegistry.registerBadgeRenderer === 'function') {
    window.ThreadCardRegistry.registerBadgeRenderer('automation', {
        condition: 'thread.automation_slug !== null',
        renderFunction: 'window.AutomationThreadIntegration.renderThreadBadge',
        config: {
            icon: 'fa-cogs',
            color: '#3b82f6',
            label: 'Automation',
            priority: 3
        },
        placeholderClick: 'window.AutomationThreadIntegration.openLinkModal'
    });
    console.log('[AutomationThreadIntegration] Registered with ThreadCardRegistry');
} else {
    console.warn('[AutomationThreadIntegration] ThreadCardRegistry not available yet');

    // Retry on DOMContentLoaded
    document.addEventListener('DOMContentLoaded', () => {
        if (window.ThreadCardRegistry && typeof window.ThreadCardRegistry.registerBadgeRenderer === 'function') {
            window.ThreadCardRegistry.registerBadgeRenderer('automation', {
                condition: 'thread.automation_slug !== null',
                renderFunction: 'window.AutomationThreadIntegration.renderThreadBadge',
                config: {
                    icon: 'fa-cogs',
                    color: '#3b82f6',
                    label: 'Automation',
                    priority: 3
                },
                placeholderClick: 'window.AutomationThreadIntegration.openLinkModal'
            });
            console.log('[AutomationThreadIntegration] Registered with ThreadCardRegistry (deferred)');
        }
    });
}

console.log('[AutomationThreadIntegration] Module loaded');
