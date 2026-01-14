/**
 * FILE: UI/modules_internal/thread-cards/email-thread-integration.js
 * PURPOSE: Email thread badge rendering for ThreadInfo cards
 * 
 * DEPENDENCIES:
 * - ThreadCardRegistry (badge registration)
 * - ThreadManager (thread data)
 * 
 * EXPORTS:
 * - window.EmailThreadIntegration.renderThreadBadge() - Render email badge
 * - window.EmailThreadIntegration.openEmailThread() - Open email in Communication Hub
 * - window.EmailThreadIntegration.unlinkEmailThread() - Unlink email from thread
 * 
 * USED BY:
 * - ThreadCardRegistry (badge rendering system)
 * - Thread info cards (UI links row)
 * 
 * NOTES:
 * - Registers with ThreadCardRegistry on load
 * - Amber badge color (#f59e0b) for email threads
 * - Supports drag-and-drop email thread IDs onto threads
 * 
 * LAST MODIFIED: 2025-12-01 - Initial creation for email thread placeholders
 */

console.log('📦 [EMAIL-THREAD] Loading email thread integration module...');

window.EmailThreadIntegration = {
    /**
     * Render email thread badge for ThreadInfo card
     * 
     * @param {Object} thread - Thread object with email_thread_id field
     * @param {Object} config - Badge configuration {icon, color, label}
     * @returns {string} HTML string for email badge
     */
    renderThreadBadge(thread, config) {
        if (!thread.email_thread_id) {
            return '';
        }

        const emailSubject = thread.email_subject || 'Email Thread';
        const participants = thread.email_participants ?
            (typeof thread.email_participants === 'string' ?
                JSON.parse(thread.email_participants) : thread.email_participants) : [];

        const participantCount = participants.length;
        const icon = config?.icon || 'fa-envelope';
        const color = config?.color || '#f59e0b'; // Amber

        return `
            <div class="thread-link-row email-thread-row" data-email-thread-id="${thread.email_thread_id}">
                <button class="email-badge" 
                        style="background: linear-gradient(135deg, ${color} 0%, #d97706 100%); color: white; border: none; padding: 8px 14px; border-radius: 8px; display: flex; align-items: center; gap: 10px; font-size: 13px; font-weight: 500; cursor: pointer; flex: 1; box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3); transition: all 0.2s ease; position: relative; overflow: hidden;"
                        onclick="EmailThreadIntegration.openEmailThread('${thread.email_thread_id}', event)"
                        title="Open email thread in Communication Hub">
                    <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%); pointer-events: none;"></div>
                    <i class="fas ${icon}" style="font-size: 14px; position: relative; z-index: 1;"></i>
                    <span class="email-badge-title" style="letter-spacing: 0.01em; position: relative; z-index: 1; flex: 1; text-align: left; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${emailSubject}</span>
                    ${participantCount > 0 ? `<span style="background: rgba(255,255,255,0.3); padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; position: relative; z-index: 1;">${participantCount}</span>` : ''}
                </button>
                <button class="thread-email-unlink" 
                        style="background: rgba(239, 68, 68, 0.1); color: #dc2626; border: 1px solid rgba(239, 68, 68, 0.3); padding: 8px 12px; border-radius: 8px; cursor: pointer; transition: all 0.2s ease;"
                        onclick="EmailThreadIntegration.unlinkEmailThread('${thread.id}', '${thread.email_thread_id}', event)"
                        title="Unlink email thread">
                    <i class="fas fa-unlink"></i>
                </button>
            </div>
        `;
    },

    /**
     * Open email thread in Communication Hub module
     * 
     * @param {string} emailThreadId - Email thread identifier
     * @param {Event} event - Click event
     */
    openEmailThread(emailThreadId, event) {
        if (event) {
            event.stopPropagation();
        }

        console.log(`[EMAIL-THREAD] Opening email thread: ${emailThreadId}`);

        // Check if Communication Hub module exists
        if (typeof window.loadModuleBySlug === 'function') {
            // Load Communication Hub module with email thread filter
            window.loadModuleBySlug('communication-hub', {
                email_thread_id: emailThreadId,
                auto_filter: true
            });
        } else if (typeof SidebarManager !== 'undefined' && typeof SidebarManager.loadModule === 'function') {
            // Alternative: Use SidebarManager if available
            SidebarManager.loadModule('communication-hub', {
                email_thread_id: emailThreadId,
                auto_filter: true
            });
        } else {
            console.warn('[EMAIL-THREAD] Communication Hub module loader not found');
            alert('Communication Hub module not available. Please open it manually from the sidebar.');
        }
    },

    /**
     * Unlink email thread from conversation thread
     * 
     * @param {string} threadId - Thread slug
     * @param {string} emailThreadId - Email thread identifier
     * @param {Event} event - Click event
     */
    async unlinkEmailThread(threadId, emailThreadId, event) {
        if (event) {
            event.stopPropagation();
        }

        if (!confirm('Unlink this email thread? The conversation thread will remain intact.')) {
            return;
        }

        console.log(`[EMAIL-THREAD] Unlinking email thread ${emailThreadId} from ${threadId}`);

        try {
            const userId = localStorage.getItem('user_id') || '1';
            const apiUrl = window.API_BASE_URL || 'http://localhost:5001';

            const response = await fetch(`${apiUrl}/api/thread-assignments/email/unlink`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    thread_slug: threadId
                })
            });

            if (!response.ok) {
                throw new Error('Failed to unlink email thread');
            }

            // Refresh thread card
            if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.syncThreadLocationEverywhere === 'function') {
                ThreadManager.syncThreadLocationEverywhere(threadId);
            }

            console.log('[EMAIL-THREAD] Email thread unlinked successfully');

        } catch (error) {
            console.error('[EMAIL-THREAD] Unlink failed:', error);
            alert('Failed to unlink email thread');
        }
    },

    /**
     * Setup drag-and-drop for email thread IDs on thread info cards
     * Called during initialization
     */
    setupDragDropHandlers() {
        console.log('[EMAIL-THREAD] Setting up drag-and-drop handlers...');

        // Listen for custom drag events (from Communication Hub)
        document.addEventListener('email-thread-drag-start', (e) => {
            console.log('[EMAIL-THREAD] Email thread drag started:', e.detail);
        });

        document.addEventListener('email-thread-drag-end', (e) => {
            console.log('[EMAIL-THREAD] Email thread drag ended');
        });

        console.log('[EMAIL-THREAD] Drag-and-drop handlers ready');
    }
};

// Register badge with ThreadCardRegistry (when available)
if (window.ThreadCardRegistry && typeof window.ThreadCardRegistry.registerBadgeRenderer === 'function') {
    window.ThreadCardRegistry.registerBadgeRenderer('email_threads', {
        condition: 'thread.email_thread_id !== null',
        renderFunction: 'window.EmailThreadIntegration.renderThreadBadge',
        config: {
            icon: 'fa-envelope',
            color: '#f59e0b',
            label: 'Email',
            priority: 40  // After synergy(10), workflow(20), automation(30), before internal_docs(50)
        }
    });
    console.log('✅ [EMAIL-THREAD] Badge renderer registered with ThreadCardRegistry');
} else {
    console.warn('⚠️ [EMAIL-THREAD] ThreadCardRegistry not found - will register on DOMContentLoaded');

    // Retry registration after DOM loads
    document.addEventListener('DOMContentLoaded', () => {
        if (window.ThreadCardRegistry && typeof window.ThreadCardRegistry.registerBadgeRenderer === 'function') {
            window.ThreadCardRegistry.registerBadgeRenderer('email_threads', {
                condition: 'thread.email_thread_id !== null',
                renderFunction: 'window.EmailThreadIntegration.renderThreadBadge',
                config: {
                    icon: 'fa-envelope',
                    color: '#f59e0b',
                    label: 'Email',
                    priority: 40
                }
            });
            console.log('✅ [EMAIL-THREAD] Badge renderer registered (deferred)');
        }
    });
}

// Setup drag-and-drop handlers
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.EmailThreadIntegration.setupDragDropHandlers();
    });
} else {
    window.EmailThreadIntegration.setupDragDropHandlers();
}

console.log('✅ [EMAIL-THREAD] Email thread integration module loaded');
