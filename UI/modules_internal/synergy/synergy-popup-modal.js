/**
 * Synergy Popup Modal Module
 * 
 * Full-screen popup for viewing/editing synergy sessions
 * Integrates with SynergySidebarRenderer for content rendering
 * 
 * @module SynergyPopupModal
 * @version 1.0.0
 * @date 2025-11-23
 */

class SynergyPopupModal {
    constructor() {
        this.API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
        this.renderer = new window.SynergySidebarRenderer();
        this.currentSessionId = null;
        this.isEditMode = false;
        this.init();
        console.log('[SYNERGY POPUP] Module loaded');
    }

    /**
     * Initialize modal HTML and event listeners
     */
    init() {
        // Create popup HTML if it doesn't exist
        if (!document.querySelector('.synergy-popup-container')) {
            const modalHTML = `
                <div class="synergy-popup-container" data-edit-mode="false">
                        <!-- Header -->
                        <div class="synergy-popup-header">
                            <div class="synergy-popup-title">
                                <i class="fas fa-project-diagram"></i>
                                <span id="synergy-popup-session-title">Session Details</span>
                            </div>
                            <div class="synergy-popup-actions">
                                <!-- Edit button removed - each field has its own Edit button inline -->
                                <button class="synergy-popup-btn synergy-popup-close" id="synergy-popup-close-btn" title="Close">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        </div>

                        <!-- Content -->
                        <div class="synergy-popup-content" id="synergy-popup-content">
                            <div class="loading-placeholder">
                                <i class="fas fa-spinner fa-spin"></i>
                                <div class="loading-text">Loading session...</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHTML);
        }

        // Bind event listeners
        this.bindEvents();

        // Make popup draggable
        this.makeDraggable();
    }

    /**
     * Make popup container draggable by header
     * Allows dragging ANYWHERE on screen (no modal bounds)
     */
    makeDraggable() {
        const container = document.querySelector('.synergy-popup-container');
        const header = document.querySelector('.synergy-popup-header');

        if (!container || !header) return;

        let isDragging = false;
        let offsetX = 0;
        let offsetY = 0;

        header.addEventListener('mousedown', (e) => {
            // Don't drag if clicking buttons
            if (e.target.closest('button')) return;

            isDragging = true;
            
            // Calculate offset from mouse to container top-left
            const rect = container.getBoundingClientRect();
            offsetX = e.clientX - rect.left;
            offsetY = e.clientY - rect.top;
            
            header.style.cursor = 'grabbing';
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;

            e.preventDefault();
            
            // Calculate new position (mouse position - offset)
            const newLeft = e.clientX - offsetX;
            const newTop = e.clientY - offsetY;

            // Apply position directly - NO BOUNDS CHECKING
            // User can drag it anywhere, even partially off-screen
            container.style.left = newLeft + 'px';
            container.style.top = newTop + 'px';
            container.style.transform = 'none'; // Override centered transform
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                header.style.cursor = 'move';
            }
        });
    }

    /**
     * Bind modal event listeners
     */
    bindEvents() {
        const container = document.querySelector('.synergy-popup-container');
        const closeBtn = document.getElementById('synergy-popup-close-btn');
        const editBtn = document.getElementById('synergy-popup-edit-btn');

        // Close button ONLY - no click outside, no ESC (user must explicitly close)
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }

        // Edit mode toggle removed - using inline editing per field

        // NO ESC KEY - popup persists until X is clicked
        // NO CLICK OUTSIDE - popup is standalone, no overlay to click
    }

    /**
     * Open popup modal with session ID
     * @param {string} sessionId - Session ID to display
     */
    async open(sessionId) {
        this.currentSessionId = sessionId;
        const container = document.querySelector('.synergy-popup-container');
        const content = document.getElementById('synergy-popup-content');
        const title = document.getElementById('synergy-popup-session-title');

        if (!container || !content) {
            console.error('[SYNERGY POPUP] Popup elements not found');
            return;
        }

        // Show popup
        container.classList.add('active');
        // Don't prevent background scrolling - popup is floating, user can still work on page

        // Show loading state
        content.innerHTML = `
            <div class="loading-placeholder">
                <i class="fas fa-spinner fa-spin"></i>
                <div class="loading-text">Loading session data...</div>
            </div>
        `;

        try {
            // Fetch full session data
            const url = `${this.API_BASE_URL}/api/synergy/${sessionId}/milestones`;
            console.log(`[SYNERGY POPUP] Fetching: ${url}`);

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${await response.text()}`);
            }

            const data = await response.json();
            const session = data.session || {};
            const milestones = data.milestones || [];

            // Update title
            if (title) {
                title.textContent = session.title || 'Synergy Session';
            }

            // Render full content using renderer
            content.innerHTML = this.renderer.renderExpandedCardContent(session, milestones, sessionId);

            // Load linked threads after content is rendered
            this.loadLinkedThreadsInPopup(sessionId);

            console.log(`[SYNERGY POPUP] Loaded session: ${sessionId}`);

        } catch (error) {
            console.error('[SYNERGY POPUP] Error loading session:', error);
            content.innerHTML = `
                <div style="
                    padding: 40px;
                    text-align: center;
                    background: rgba(220, 38, 38, 0.1);
                    border: 2px solid #dc2626;
                    border-radius: 12px;
                    color: #dc2626;
                ">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; margin-bottom: 16px;"></i>
                    <div style="font-weight: 700; font-size: 18px; margin-bottom: 8px;">
                        Error Loading Session
                    </div>
                    <div style="font-size: 14px; opacity: 0.9;">
                        ${error.message}
                    </div>
                </div>
            `;
        }
    }

    /**
     * Load linked threads and render them as thread info cards
     */
    async loadLinkedThreadsInPopup(sessionId) {
        const container = document.querySelector('.synergy-linked-threads-container');
        if (!container) {
            console.warn('[SYNERGY POPUP] Linked threads container not found');
            return;
        }

        try {
            // Fetch linked threads
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}/linked-threads`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            if (!data.success) throw new Error(data.error || 'Failed to load linked threads');

            const threads = data.threads || [];

            if (threads.length === 0) {
                container.innerHTML = `
                    <div class="synergy-flat-empty">
                        <i class="fas fa-comments"></i>
                        <div>No linked threads</div>
                    </div>
                `;
                return;
            }

            // Fetch full thread details for each linked thread
            const threadDetailsPromises = threads.map(async (thread) => {
                try {
                    const resp = await fetch(`${this.API_BASE_URL}/api/threads/${thread.thread_id}`);
                    if (resp.ok) {
                        const threadData = await resp.json();
                        return threadData.thread || thread;
                    }
                } catch (err) {
                    console.warn('[SYNERGY POPUP] Failed to fetch thread details for', thread.thread_id, err);
                }
                return thread;
            });

            const fullThreads = await Promise.all(threadDetailsPromises);

            // Render thread info cards using ThreadCardTemplates
            if (typeof ThreadCardTemplates !== 'undefined' && typeof ThreadCardTemplates.compactCard === 'function') {
                container.innerHTML = fullThreads.map(thread => 
                    ThreadCardTemplates.compactCard(thread, 'synergy')
                ).join('');
            } else {
                // Fallback: simple thread list
                container.innerHTML = fullThreads.map(thread => `
                    <div class="thread-card-compact" 
                         data-thread-id="${thread.id}"
                         onclick="ThreadManager.switchThread('${thread.id}')">
                        <div class="thread-card-title">${this.escapeHtml(thread.title || 'Untitled Thread')}</div>
                        <div class="thread-card-meta">
                            <span><i class="fas fa-comment"></i> ${thread.message_count || 0}</span>
                            <span><i class="fas fa-clock"></i> ${new Date(thread.created_at).toLocaleDateString()}</span>
                        </div>
                    </div>
                `).join('');
            }

            console.log(`[SYNERGY POPUP] Loaded ${threads.length} linked thread(s)`);

        } catch (error) {
            console.error('[SYNERGY POPUP] Error loading linked threads:', error);
            container.innerHTML = `
                <div class="synergy-flat-empty" style="color: #dc2626;">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div>Failed to load linked threads</div>
                </div>
            `;
        }
    }

    /**
     * Escape HTML for safe rendering
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Close popup modal
     */
    close() {
        const container = document.querySelector('.synergy-popup-container');
        if (container) {
            container.classList.remove('active');
            // Reset position to center for next time
            container.style.left = '';
            container.style.top = '';
            container.style.transform = '';
        }

        // Reset edit mode
        this.isEditMode = false;
        if (container) {
            container.setAttribute('data-edit-mode', 'false');
        }

        const editBtn = document.getElementById('synergy-popup-edit-btn');
        if (editBtn) {
            editBtn.classList.remove('edit-mode-active');
            editBtn.querySelector('span').textContent = 'Edit';
        }

        console.log('[SYNERGY POPUP] Closed');
    }

    /**
     * Toggle edit mode
     */
    toggleEditMode() {
        this.isEditMode = !this.isEditMode;
        const container = document.querySelector('.synergy-popup-container');
        const editBtn = document.getElementById('synergy-popup-edit-btn');

        if (container) {
            container.setAttribute('data-edit-mode', this.isEditMode ? 'true' : 'false');
        }

        if (editBtn) {
            if (this.isEditMode) {
                editBtn.classList.add('edit-mode-active');
                editBtn.querySelector('span').textContent = 'View';
                editBtn.querySelector('i').className = 'fas fa-eye';
            } else {
                editBtn.classList.remove('edit-mode-active');
                editBtn.querySelector('span').textContent = 'Edit';
                editBtn.querySelector('i').className = 'fas fa-edit';
            }
        }

        // Show edit toolbar
        const toolbar = document.querySelector('.synergy-edit-toolbar');
        if (toolbar) {
            toolbar.style.display = this.isEditMode ? 'flex' : 'none';
        }

        // Make fields editable
        const editableFields = document.querySelectorAll('.editable-field');
        editableFields.forEach(field => {
            field.contentEditable = this.isEditMode;
            field.style.position = 'relative';
        });

        console.log(`[SYNERGY POPUP] Edit mode: ${this.isEditMode ? 'ON' : 'OFF'}`);
    }

    /**
     * Save changes (placeholder for future implementation)
     */
    async saveChanges() {
        if (!this.currentSessionId) return;

        // TODO: Implement save logic
        console.log('[SYNERGY POPUP] Saving changes for session:', this.currentSessionId);

        // Show success notification
        alert('Save functionality coming soon!');
    }
}

// Export to window for global access
window.SynergyPopupModal = SynergyPopupModal;

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    window.synergyPopupModal = new SynergyPopupModal();
    console.log('✅ [SYNERGY POPUP] Module initialized');
});
