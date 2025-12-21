/**
 * FILE: UI/shared/utilities/result-modal.js
 * PURPOSE: Universal floating modal system for displaying search results
 * 
 * FEATURES:
 * - Non-blocking floating windows
 * - Draggable by header
 * - Resizable from corner
 * - Multiple windows with z-index stacking
 * - Cascade positioning
 * - "Open in Dashboard" action
 * - Dynamic content loading
 * 
 * USAGE:
 *   ResultModal.open({
 *     id: '123',
 *     source: 'threads',
 *     title: 'Customer Support Thread',
 *     data: resultObject
 *   });
 * 
 * Created: December 22, 2025
 */

window.ResultModal = (() => {
    // Track z-index for stacking windows
    let nextZIndex = 10000;
    let windowCount = 0;
    const openWindows = new Map();

    /**
     * Open result in floating modal window
     * @param {Object} config - Configuration object
     * @param {string} config.id - Result ID
     * @param {string} config.source - Source type (threads, gmail, documents, etc.)
     * @param {string} config.title - Window title
     * @param {Object} config.data - Result data object
     */
    function open(config) {
        const { id, source, title, data } = config;
        
        windowCount++;
        const windowId = `result-modal-${source}-${id}`;

        // Check if window already open
        if (openWindows.has(windowId)) {
            const existingWindow = openWindows.get(windowId);
            existingWindow.style.zIndex = nextZIndex++;
            existingWindow.classList.add('pulse');
            setTimeout(() => existingWindow.classList.remove('pulse'), 300);
            console.log(`[ResultModal] Window already open: ${windowId}`);
            return;
        }

        // Create floating window
        const floatingWindow = document.createElement('div');
        floatingWindow.className = 'result-modal-window';
        floatingWindow.id = windowId;
        floatingWindow.style.zIndex = nextZIndex++;
        floatingWindow.dataset.source = source;
        floatingWindow.dataset.resultId = id;

        // Position with cascade offset
        const offset = (windowCount - 1) * 40;
        floatingWindow.style.left = `${100 + offset}px`;
        floatingWindow.style.top = `${80 + offset}px`;

        // Get source icon and color
        const sourceInfo = getSourceInfo(source);

        floatingWindow.innerHTML = `
            <div class="result-modal-header">
                <div class="result-modal-title">
                    <i class="${sourceInfo.icon}" style="color: ${sourceInfo.color};"></i>
                    <span>${title || 'Result Preview'}</span>
                    <span class="result-modal-source-badge" style="background: ${sourceInfo.color};">${sourceInfo.label}</span>
                </div>
                <div class="result-modal-controls">
                    <button class="result-modal-open-btn" title="Open in Dashboard">
                        <i class="fas fa-external-link-alt"></i>
                    </button>
                    <button class="result-modal-copy-btn" title="Copy content">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button class="result-modal-close-btn" title="Close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div class="result-modal-content">
                <div class="result-modal-loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    <span>Loading content...</span>
                </div>
            </div>
            <div class="result-modal-resize-handle"></div>
        `;

        // Add to body
        document.body.appendChild(floatingWindow);
        openWindows.set(windowId, floatingWindow);

        // Get elements
        const header = floatingWindow.querySelector('.result-modal-header');
        const content = floatingWindow.querySelector('.result-modal-content');
        const closeBtn = floatingWindow.querySelector('.result-modal-close-btn');
        const copyBtn = floatingWindow.querySelector('.result-modal-copy-btn');
        const openBtn = floatingWindow.querySelector('.result-modal-open-btn');
        const resizeHandle = floatingWindow.querySelector('.result-modal-resize-handle');

        // Close window
        const closeWindow = () => {
            floatingWindow.classList.add('closing');
            setTimeout(() => {
                floatingWindow.remove();
                openWindows.delete(windowId);
            }, 200);
        };

        closeBtn.addEventListener('click', closeWindow);

        // Open in dashboard
        openBtn.addEventListener('click', () => {
            openInDashboard(id, source, data);
        });

        // Copy functionality
        copyBtn.addEventListener('click', () => {
            const text = content.innerText;
            navigator.clipboard.writeText(text).then(() => {
                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                }, 1500);
            }).catch(err => {
                console.error('[ResultModal] Copy failed:', err);
            });
        });

        // Bring to front on click
        floatingWindow.addEventListener('mousedown', () => {
            floatingWindow.style.zIndex = nextZIndex++;
        });

        // Make draggable
        makeDraggable(floatingWindow, header);

        // Make resizable
        makeResizable(floatingWindow, resizeHandle);

        // Load content
        loadContent(content, source, id, data);

        // Animate in
        requestAnimationFrame(() => floatingWindow.classList.add('visible'));

        console.log(`[ResultModal] Window opened: ${windowId}`);
    }

    /**
     * Make element draggable
     */
    function makeDraggable(element, handle) {
        let isDragging = false;
        let dragOffsetX = 0;
        let dragOffsetY = 0;

        handle.addEventListener('mousedown', (e) => {
            // Don't drag if clicking buttons
            if (e.target.closest('button')) return;

            isDragging = true;
            const rect = element.getBoundingClientRect();
            dragOffsetX = e.clientX - rect.left;
            dragOffsetY = e.clientY - rect.top;
            handle.style.cursor = 'grabbing';
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;

            const x = e.clientX - dragOffsetX;
            const y = e.clientY - dragOffsetY;

            // Keep within viewport bounds
            const maxX = window.innerWidth - 100;
            const maxY = window.innerHeight - 50;

            element.style.left = `${Math.max(0, Math.min(x, maxX))}px`;
            element.style.top = `${Math.max(0, Math.min(y, maxY))}px`;
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                handle.style.cursor = 'grab';
            }
        });
    }

    /**
     * Make element resizable
     */
    function makeResizable(element, handle) {
        let isResizing = false;
        let startX = 0;
        let startY = 0;
        let startWidth = 0;
        let startHeight = 0;

        handle.addEventListener('mousedown', (e) => {
            isResizing = true;
            startX = e.clientX;
            startY = e.clientY;
            const rect = element.getBoundingClientRect();
            startWidth = rect.width;
            startHeight = rect.height;
            e.preventDefault();
            e.stopPropagation();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;

            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;

            const newWidth = Math.max(400, startWidth + deltaX);
            const newHeight = Math.max(300, startHeight + deltaY);

            element.style.width = `${newWidth}px`;
            element.style.height = `${newHeight}px`;
        });

        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
            }
        });
    }

    /**
     * Load content based on source type
     */
    async function loadContent(container, source, id, data) {
        try {
            let html = '';

            switch (source) {
                case 'threads':
                    html = await renderThread(id, data);
                    break;
                case 'messages':
                    html = await renderMessage(id, data);
                    break;
                case 'documents':
                    html = await renderDocument(id, data);
                    break;
                case 'gmail':
                case 'outlook':
                    html = renderEmail(data);
                    break;
                case 'synergy':
                    html = await renderSynergy(id, data);
                    break;
                case 'xero':
                    html = renderXero(data);
                    break;
                case 'google-drive':
                case 'onedrive':
                case 'sharepoint':
                    html = renderCloudFile(data);
                    break;
                default:
                    html = renderGeneric(data);
            }

            container.innerHTML = html;
        } catch (error) {
            console.error('[ResultModal] Failed to load content:', error);
            container.innerHTML = `
                <div class="result-modal-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Failed to Load Content</h3>
                    <p>${error.message}</p>
                </div>
            `;
        }
    }

    /**
     * Render thread content
     */
    async function renderThread(threadId, data) {
        try {
            const response = await fetch(`/api/threads/${threadId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const thread = await response.json();

            return `
                <div class="result-modal-thread">
                    <div class="thread-meta">
                        <span><i class="fas fa-calendar"></i> ${formatDate(thread.created_at)}</span>
                        ${thread.location ? `<span><i class="fas fa-robot"></i> ${thread.location}</span>` : ''}
                        ${thread.tags ? `<span><i class="fas fa-tags"></i> ${thread.tags.join(', ')}</span>` : ''}
                    </div>
                    <div class="thread-messages">
                        ${thread.messages ? thread.messages.slice(0, 5).map(msg => `
                            <div class="thread-message ${msg.role}">
                                <div class="message-role">${msg.role === 'user' ? '👤 User' : '🤖 AI'}</div>
                                <div class="message-content">${escapeHtml(msg.content.substring(0, 500))}${msg.content.length > 500 ? '...' : ''}</div>
                            </div>
                        `).join('') : '<p>No messages available</p>'}
                        ${thread.messages && thread.messages.length > 5 ? `<p class="more-messages">+ ${thread.messages.length - 5} more messages</p>` : ''}
                    </div>
                </div>
            `;
        } catch (error) {
            return `<p class="error">Failed to load thread: ${error.message}</p>`;
        }
    }

    /**
     * Render email content
     */
    function renderEmail(data) {
        return `
            <div class="result-modal-email">
                <div class="email-header">
                    <div class="email-from">
                        <strong>From:</strong> ${escapeHtml(data.from_name || data.from || 'Unknown')}
                        ${data.from ? `<span class="email-address">&lt;${escapeHtml(data.from)}&gt;</span>` : ''}
                    </div>
                    <div class="email-date">
                        <i class="fas fa-clock"></i> ${formatDate(data.received || data.receivedDateTime || data.date)}
                    </div>
                </div>
                <div class="email-body">
                    ${escapeHtml(data.preview || data.bodyPreview || data.snippet || 'No preview available')}
                </div>
                ${data.has_attachments || data.hasAttachments ? `
                    <div class="email-attachments">
                        <i class="fas fa-paperclip"></i> Has attachments
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Render document content
     */
    async function renderDocument(docId, data) {
        return `
            <div class="result-modal-document">
                <div class="doc-meta">
                    <span><i class="fas fa-file"></i> ${data.file_type || 'Document'}</span>
                    <span><i class="fas fa-calendar"></i> ${formatDate(data.created_at || data.date)}</span>
                    ${data.file_size ? `<span><i class="fas fa-hdd"></i> ${formatFileSize(data.file_size)}</span>` : ''}
                </div>
                <div class="doc-preview">
                    ${data.snippet || data.content ? escapeHtml((data.snippet || data.content).substring(0, 1000)) : 'No preview available'}
                </div>
            </div>
        `;
    }

    /**
     * Render Synergy session/doc
     */
    async function renderSynergy(id, data) {
        if (data.type === 'document') {
            return `
                <div class="result-modal-synergy-doc">
                    <div class="synergy-meta">
                        <span><i class="fas fa-brain"></i> ${data.session_title || 'Synergy Session'}</span>
                        <span><i class="fas fa-file"></i> ${data.doc_type === 'richtext' ? 'Document' : 'Spreadsheet'}</span>
                    </div>
                    <div class="synergy-preview">
                        ${data.snippet || 'No preview available'}
                    </div>
                </div>
            `;
        } else {
            return `
                <div class="result-modal-synergy">
                    <div class="synergy-meta">
                        <span><i class="fas fa-users"></i> ${data.agent_count || 0} agents</span>
                        <span><i class="fas fa-calendar"></i> ${formatDate(data.date)}</span>
                    </div>
                    <div class="synergy-preview">
                        Click "Open in Dashboard" to view this Synergy session
                    </div>
                </div>
            `;
        }
    }

    /**
     * Render Xero record
     */
    function renderXero(data) {
        return `
            <div class="result-modal-xero">
                <div class="xero-meta">
                    <span><i class="fas fa-file-invoice"></i> ${data.type || 'Record'}</span>
                    ${data.business_name ? `<span><i class="fas fa-building"></i> ${escapeHtml(data.business_name)}</span>` : ''}
                </div>
                <div class="xero-details">
                    ${data.amount ? `<p><strong>Amount:</strong> $${data.amount}</p>` : ''}
                    ${data.status ? `<p><strong>Status:</strong> ${data.status}</p>` : ''}
                    ${data.date ? `<p><strong>Date:</strong> ${formatDate(data.date)}</p>` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Render cloud file
     */
    function renderCloudFile(data) {
        return `
            <div class="result-modal-cloud-file">
                <div class="file-icon">
                    <i class="fas fa-file fa-3x"></i>
                </div>
                <div class="file-meta">
                    <p><strong>Name:</strong> ${escapeHtml(data.name)}</p>
                    ${data.mime_type || data.mimeType ? `<p><strong>Type:</strong> ${data.mime_type || data.mimeType}</p>` : ''}
                    ${data.size ? `<p><strong>Size:</strong> ${formatFileSize(data.size)}</p>` : ''}
                    ${data.modified || data.modifiedTime ? `<p><strong>Modified:</strong> ${formatDate(data.modified || data.modifiedTime)}</p>` : ''}
                    ${data.owner ? `<p><strong>Owner:</strong> ${escapeHtml(data.owner)}</p>` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Render generic result
     */
    function renderGeneric(data) {
        return `
            <div class="result-modal-generic">
                <pre>${JSON.stringify(data, null, 2)}</pre>
            </div>
        `;
    }

    /**
     * Open result in appropriate dashboard
     */
    function openInDashboard(id, source, data) {
        console.log('[ResultModal] Opening in dashboard:', { id, source });

        switch (source) {
            case 'threads':
            case 'messages':
                if (window.switchTab) {
                    window.switchTab('home');
                    setTimeout(() => {
                        if (window.ThreadManager && window.ThreadManager.loadThreadIntoPrime) {
                            const threadId = source === 'messages' ? data.thread_id : id;
                            window.ThreadManager.loadThreadIntoPrime(threadId);
                        }
                    }, 300);
                }
                break;

            case 'documents':
                if (window.DocumentService) {
                    window.DocumentService.openDocument(id);
                } else if (window.switchTab) {
                    window.switchTab('documents');
                }
                break;

            case 'synergy':
                const sessionId = data.session_id || id;
                const docId = data.doc_id;
                if (window.switchTab) {
                    window.switchTab('synergy');
                    setTimeout(() => {
                        if (docId) {
                            window.location.hash = `#/synergy/${sessionId}/doc/${docId}`;
                        } else {
                            window.location.hash = `#/synergy/${sessionId}`;
                        }
                    }, 300);
                }
                break;

            case 'xero':
                if (window.switchTab) {
                    window.switchTab('xero');
                }
                break;

            case 'gmail':
            case 'outlook':
            case 'google-drive':
            case 'onedrive':
            case 'sharepoint':
                const link = data.link || data.webLink || data.webUrl || data.webViewLink;
                if (link) {
                    window.open(link, '_blank');
                }
                break;

            default:
                console.warn('[ResultModal] Unknown source type:', source);
        }
    }

    /**
     * Get source information (icon, color, label)
     */
    function getSourceInfo(source) {
        const sources = {
            documents: { icon: 'fas fa-file-alt', color: '#3b82f6', label: 'Documents' },
            threads: { icon: 'fas fa-comments', color: '#8b5cf6', label: 'Threads' },
            messages: { icon: 'fas fa-envelope', color: '#ec4899', label: 'Messages' },
            gmail: { icon: 'fab fa-google', color: '#ea4335', label: 'Gmail' },
            outlook: { icon: 'fas fa-envelope-open', color: '#0078d4', label: 'Outlook' },
            synergy: { icon: 'fas fa-brain', color: '#10b981', label: 'Synergy' },
            xero: { icon: 'fas fa-file-invoice', color: '#13b5ea', label: 'Xero' },
            'google-drive': { icon: 'fab fa-google-drive', color: '#4285f4', label: 'Google Drive' },
            onedrive: { icon: 'fas fa-cloud', color: '#0078d4', label: 'OneDrive' },
            sharepoint: { icon: 'fas fa-share-alt', color: '#0078d4', label: 'SharePoint' },
            'vector-database': { icon: 'fas fa-database', color: '#6366f1', label: 'Vector DB' }
        };
        return sources[source] || { icon: 'fas fa-question-circle', color: '#6b7280', label: source };
    }

    /**
     * Utility: Format date
     */
    function formatDate(dateString) {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;

        if (diff < 3600000) {
            const mins = Math.floor(diff / 60000);
            return `${mins} min${mins !== 1 ? 's' : ''} ago`;
        }
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
        }
        if (diff < 604800000) {
            const days = Math.floor(diff / 86400000);
            return `${days} day${days !== 1 ? 's' : ''} ago`;
        }
        return date.toLocaleDateString();
    }

    /**
     * Utility: Format file size
     */
    function formatFileSize(bytes) {
        if (!bytes) return 'Unknown';
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
    }

    /**
     * Utility: Escape HTML
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Close all open windows
     */
    function closeAll() {
        openWindows.forEach((window) => {
            window.classList.add('closing');
            setTimeout(() => window.remove(), 200);
        });
        openWindows.clear();
        console.log('[ResultModal] All windows closed');
    }

    // Public API
    return {
        open,
        closeAll
    };
})();

console.log('[ResultModal] Loaded successfully');
