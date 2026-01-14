/**
 * FILE: UI/modules_internal/synergy/synergy-thread-drag-drop.js
 * PURPOSE: Drag-and-drop functionality for linking threads to Synergy sessions
 * 
 * FEATURES:
 * - Make thread-info cards draggable
 * - Drop zones in Synergy linked threads container
 * - Visual feedback during drag
 * - Backend API call to link thread to session
 * - Real-time UI updates after linking
 * 
 * DEPENDENCIES:
 * - ThreadManager (for thread data)
 * - SynergySidebarRendererV2FLAT (for re-rendering linked threads)
 * 
 * LAST MODIFIED: 2025-12-15 - Initial implementation
 */

class SynergyThreadDragDrop {
    constructor(apiBaseUrl = window.API_BASE_URL || window.location.origin) {
        this.apiBaseUrl = apiBaseUrl;
        this.draggedThreadId = null;
        this.draggedThreadSlug = null;
        this.draggedThreadName = null;

        console.log('🎯 SynergyThreadDragDrop initialized');
        this.init();
    }

    init() {
        // Initialize drag-and-drop on page load
        this.initDragAndDrop();

        // Re-initialize when new content is loaded
        document.addEventListener('thread-cards-loaded', () => {
            console.log('🔄 Re-initializing drag-drop after thread cards loaded');
            this.initDragAndDrop();
        });

        document.addEventListener('synergy-card-expanded', () => {
            console.log('🔄 Re-initializing drop zones after synergy card expanded');
            this.initDropZones();
        });
    }

    /**
     * Initialize drag-and-drop for all thread cards and drop zones
     */
    initDragAndDrop() {
        this.initThreadCardDrag();
        this.initDropZones();
    }

    /**
     * Make all thread-info cards draggable
     */
    initThreadCardDrag() {
        const threadCards = document.querySelectorAll('.thread-info-card, .thread-card-item');

        threadCards.forEach(card => {
            // Skip if already made draggable
            if (card.hasAttribute('draggable')) return;

            card.setAttribute('draggable', 'true');
            card.style.cursor = 'grab';

            card.addEventListener('dragstart', (e) => {
                console.log('🎯 Drag start:', card);

                // Get thread data from card
                this.draggedThreadId = card.dataset.threadId || card.dataset.id;
                this.draggedThreadSlug = card.dataset.threadSlug || card.dataset.slug;
                this.draggedThreadName = card.dataset.threadName || card.querySelector('.thread-name, .thread-title')?.textContent?.trim() || 'Untitled Thread';

                // Visual feedback
                card.style.opacity = '0.5';
                card.style.cursor = 'grabbing';

                // Set drag data
                e.dataTransfer.effectAllowed = 'link';
                e.dataTransfer.setData('text/plain', JSON.stringify({
                    threadId: this.draggedThreadId,
                    threadSlug: this.draggedThreadSlug,
                    threadName: this.draggedThreadName
                }));

                // Add dragging class to body for global styling
                document.body.classList.add('dragging-thread');
            });

            card.addEventListener('dragend', (e) => {
                console.log('🎯 Drag end');
                card.style.opacity = '1';
                card.style.cursor = 'grab';
                document.body.classList.remove('dragging-thread');
            });
        });

        console.log(`🎯 Made ${threadCards.length} thread cards draggable`);
    }

    /**
     * Initialize drop zones in Synergy linked threads containers
     */
    initDropZones() {
        const dropZones = document.querySelectorAll('.synergy-linked-threads-container, .synergy-drop-zone, .synergy-flat-empty');

        dropZones.forEach(zone => {
            // Skip if already initialized
            if (zone.hasAttribute('data-drop-initialized')) return;
            zone.setAttribute('data-drop-initialized', 'true');

            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'link';

                // Visual feedback
                zone.classList.add('drag-over');
            });

            zone.addEventListener('dragleave', (e) => {
                zone.classList.remove('drag-over');
            });

            zone.addEventListener('drop', async (e) => {
                e.preventDefault();
                zone.classList.remove('drag-over');

                // Get session ID from container
                const sessionId = zone.dataset.sessionId ||
                    zone.closest('[data-session-id]')?.dataset?.sessionId ||
                    zone.closest('.synergy-linked-threads-container')?.dataset?.sessionId;

                if (!sessionId) {
                    console.error('❌ No session ID found for drop zone');
                    this.showNotification('Error: Cannot determine Synergy session', 'error');
                    return;
                }

                // Get thread data
                let threadData;
                try {
                    threadData = JSON.parse(e.dataTransfer.getData('text/plain'));
                } catch (err) {
                    console.error('❌ Failed to parse drag data:', err);
                    this.showNotification('Error: Invalid thread data', 'error');
                    return;
                }

                const { threadId, threadSlug, threadName } = threadData;

                if (!threadId && !threadSlug) {
                    console.error('❌ No thread ID or slug in drop data');
                    this.showNotification('Error: Missing thread identifier', 'error');
                    return;
                }

                console.log('🎯 Dropped thread onto session:', {
                    threadId,
                    threadSlug,
                    threadName,
                    sessionId
                });

                // Link thread to session
                await this.linkThreadToSession(sessionId, threadId, threadSlug, threadName);
            });
        });

        console.log(`🎯 Initialized ${dropZones.length} drop zones`);
    }

    /**
     * Link a thread to a Synergy session
     * Updates both backend (sessions.threads.synergy_card_id) and Synergy session (thread_ids array)
     */
    async linkThreadToSession(sessionId, threadId, threadSlug, threadName) {
        try {
            this.showNotification(`Linking "${threadName}" to Synergy session...`, 'info');

            // Call backend API to link thread
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/${sessionId}/link-thread`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    thread_id: threadId,
                    thread_slug: threadSlug,
                    thread_name: threadName
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Unknown error linking thread');
            }

            console.log('✅ Thread linked successfully:', data);
            this.showNotification(`Thread "${threadName}" linked successfully!`, 'success');

            // Reload linked threads section to show the newly linked thread
            if (window.synergySidebar && window.synergySidebar.loadLinkedThreads) {
                await window.synergySidebar.loadLinkedThreads(sessionId);
            }

            // Refresh thread card badges to show synergy link
            document.dispatchEvent(new CustomEvent('thread-linked-to-synergy', {
                detail: { threadId, sessionId, sessionName: data.session_name }
            }));

        } catch (error) {
            console.error('❌ Error linking thread to session:', error);
            this.showNotification(`Error: ${error.message}`, 'error');
        }
    }

    /**
     * Show notification toast
     */
    showNotification(message, type = 'info') {
        // Use existing notification system if available
        if (window.showNotification) {
            window.showNotification(message, type);
            return;
        }

        // Fallback simple toast
        const toast = document.createElement('div');
        toast.className = `synergy-toast synergy-toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        toast.style.cssText = `
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 14px;
            font-weight: 500;
            z-index: 99999;
            animation: slideInUp 0.3s ease;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOutDown 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.synergyThreadDragDrop = new SynergyThreadDragDrop();
    });
} else {
    window.synergyThreadDragDrop = new SynergyThreadDragDrop();
}

// Export for module usage
window.SynergyThreadDragDrop = SynergyThreadDragDrop;
