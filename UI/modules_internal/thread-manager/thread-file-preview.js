/**
 * Synergy Files Preview Modal
 * Gap #4 Enhancement: Show file list when clicking file count badge
 * 
 * Created: December 9, 2025
 * Purpose: Display synergy internal docs in modal with preview/download options
 * 
 * UPDATED: December 21, 2025 - Integrated with DocumentService
 */

import { documentService } from '../shared/document-service.js';

window.ThreadFilePreview = {
    /**
     * Show synergy files modal for a session
     * @param {string} sessionId - Synergy session ID
     */
    async showSynergyFiles(sessionId) {
        try {
            console.log(`[FilePreview] Loading files for session: ${sessionId}`);

            // Fetch session details with files using DocumentService
            const files = await documentService.fetchSessionDocuments(sessionId);

            // Get session title (simplified - we only need files for display)
            const response = await fetch(`/api/synergy/sessions/${sessionId}`);
            if (!response.ok) {
                throw new Error(`Failed to fetch session: ${response.statusText}`);
            }
            const data = await response.json();
            const session = data.session || data;

            console.log(`[FilePreview] Found ${files.length} files for ${session.title}`);

            // Create modal HTML
            const modalHtml = this._buildModal(session, files);

            // Inject modal into DOM
            let modalContainer = document.getElementById('synergy-files-modal-container');
            if (!modalContainer) {
                modalContainer = document.createElement('div');
                modalContainer.id = 'synergy-files-modal-container';
                document.body.appendChild(modalContainer);
            }
            modalContainer.innerHTML = modalHtml;

            // Show modal
            const modal = document.getElementById('synergy-files-modal');
            modal.style.display = 'flex';

            // Setup event listeners
            this._setupEventListeners(sessionId, files);

        } catch (error) {
            console.error('[FilePreview] Error loading files:', error);
            alert(`Failed to load files: ${error.message}`);
        }
    },

    /**
     * Build modal HTML
     * @private
     */
    _buildModal(session, files) {
        const fileListHtml = files.length > 0
            ? files.map((file, index) => this._buildFileCard(file, index)).join('')
            : '<div class="no-files-message">📭 No files in this session yet</div>';

        return `
            <div id="synergy-files-modal" class="synergy-files-modal">
                <div class="synergy-files-modal-content">
                    <div class="synergy-files-header">
                        <div class="header-content">
                            <h2>📁 ${this._escapeHtml(session.title || 'Synergy Session')}</h2>
                            <p>${files.length} file${files.length !== 1 ? 's' : ''}</p>
                        </div>
                        <button class="close-modal-btn" onclick="ThreadFilePreview.closeModal()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <div class="synergy-files-list">
                        ${fileListHtml}
                    </div>
                    
                    <div class="synergy-files-footer">
                        <button class="btn-secondary" onclick="ThreadFilePreview.closeModal()">Close</button>
                        ${files.length > 0 ? `
                        <button class="btn-primary" onclick="ThreadFilePreview.downloadAllFiles('${session.session_id}')">
                            <i class="fas fa-download"></i> Download All
                        </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Build file card HTML
     * @private
     */
    _buildFileCard(file, index) {
        const iconClass = file.doc_type === 'spreadsheet' ? 'fa-table' : 'fa-file-alt';
        const typeLabel = file.doc_type === 'spreadsheet' ? 'Sheet' : 'Doc';
        const updatedDate = file.updated_at ? new Date(file.updated_at).toLocaleDateString() : 'N/A';

        return `
            <div class="file-card" data-doc-id="${file.doc_id}">
                <div class="file-icon">
                    <i class="fas ${iconClass}"></i>
                </div>
                <div class="file-info">
                    <div class="file-title">${this._escapeHtml(file.title)}</div>
                    <div class="file-meta">
                        <span class="file-type-badge">${typeLabel}</span>
                        <span class="file-version">v${file.version || 1}</span>
                        <span class="file-date">${updatedDate}</span>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="file-action-btn" 
                            onclick="ThreadFilePreview.openFile('${file.doc_id}')"
                            title="Open file">
                        <i class="fas fa-external-link-alt"></i>
                    </button>
                    <button class="file-action-btn" 
                            onclick="ThreadFilePreview.downloadFile('${file.doc_id}', '${this._escapeHtml(file.title)}')"
                            title="Download file">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="file-action-btn" 
                            onclick="ThreadFilePreview.copyShareLink('${file.share_url || ''}')"
                            title="Copy share link">
                        <i class="fas fa-link"></i>
                    </button>
                </div>
            </div>
        `;
    },

    /**
     * Setup event listeners
     * @private
     */
    _setupEventListeners(sessionId, files) {
        // Close on background click
        const modal = document.getElementById('synergy-files-modal');
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });

        // Close on ESC key
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    },

    /**
     * Close modal
     */
    closeModal() {
        const modal = document.getElementById('synergy-files-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    },

    /**
     * Open file in new tab
     */
    openFile(docId) {
        window.open(`/api/synergy/internal-docs/${docId}`, '_blank');
    },

    /**
     * Download file
     */
    async downloadFile(docId, title) {
        try {
            // Use DocumentService for download
            await documentService.downloadDocument(docId, title);
            console.log(`[FilePreview] Downloaded: ${title}`);
        } catch (error) {
            console.error('[FilePreview] Download error:', error);
            alert(`Failed to download file: ${error.message}`);
        }
    },

    /**
     * Copy share link to clipboard
     */
    async copyShareLink(shareUrl) {
        if (!shareUrl) {
            alert('No share link available');
            return;
        }

        try {
            await navigator.clipboard.writeText(shareUrl);
            alert('✅ Share link copied to clipboard!');
        } catch (error) {
            console.error('[FilePreview] Copy error:', error);
            alert('Failed to copy link');
        }
    },

    /**
     * Download all files as ZIP
     */
    async downloadAllFiles(sessionId) {
        try {
            const response = await fetch(`/api/synergy/sessions/${sessionId}/download-all`);
            if (!response.ok) {
                throw new Error('Download failed');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `synergy-session-${sessionId}-files.zip`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            console.log(`[FilePreview] Downloaded all files for session: ${sessionId}`);
        } catch (error) {
            console.error('[FilePreview] Download all error:', error);
            alert(`Failed to download files: ${error.message}`);
        }
    },

    /**
     * Escape HTML to prevent XSS
     * @private
     */
    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
};

// Add to ThreadManager for easy access
if (window.ThreadManager) {
    window.ThreadManager.showSynergyFiles = function (sessionId) {
        window.ThreadFilePreview.showSynergyFiles(sessionId);
    };
}

console.log('✅ [ThreadFilePreview] Module loaded successfully');
