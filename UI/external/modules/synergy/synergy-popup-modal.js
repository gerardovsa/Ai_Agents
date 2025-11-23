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
        // Create modal HTML if it doesn't exist
        if (!document.getElementById('synergy-popup-modal')) {
            const modalHTML = `
                <div id="synergy-popup-modal" class="synergy-popup-modal" data-edit-mode="false">
                    <div class="synergy-popup-container">
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
                                    <span>Close</span>
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
    }

    /**
     * Bind modal event listeners
     */
    bindEvents() {
        const modal = document.getElementById('synergy-popup-modal');
        const closeBtn = document.getElementById('synergy-popup-close-btn');
        const editBtn = document.getElementById('synergy-popup-edit-btn');

        // Close button
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }

        // Edit mode toggle removed - using inline editing per field

        // Close on overlay click (not container)
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.close();
                }
            });
        }

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal && modal.classList.contains('active')) {
                this.close();
            }
        });
    }

    /**
     * Open popup modal with session ID
     * @param {string} sessionId - Session ID to display
     */
    async open(sessionId) {
        this.currentSessionId = sessionId;
        const modal = document.getElementById('synergy-popup-modal');
        const content = document.getElementById('synergy-popup-content');
        const title = document.getElementById('synergy-popup-session-title');

        if (!modal || !content) {
            console.error('[SYNERGY POPUP] Modal elements not found');
            return;
        }

        // Show modal
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling

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
     * Close popup modal
     */
    close() {
        const modal = document.getElementById('synergy-popup-modal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = ''; // Restore scrolling
        }

        // Reset edit mode
        this.isEditMode = false;
        if (modal) {
            modal.setAttribute('data-edit-mode', 'false');
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
        const modal = document.getElementById('synergy-popup-modal');
        const editBtn = document.getElementById('synergy-popup-edit-btn');

        if (modal) {
            modal.setAttribute('data-edit-mode', this.isEditMode ? 'true' : 'false');
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
