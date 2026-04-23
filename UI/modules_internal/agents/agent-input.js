/**
 * FILE: UI/modules/agents/agent-input.js
 * PURPOSE: Handle agent input area interactions - typing, file attachments, auto-expand
 * 
 * FEATURES:
 * - Textarea auto-expand (80px to 200px)
 * - File attachment handling (PDF, images)
 * - Drag-and-drop file support
 * - File validation (type, size)
 * - Keyboard shortcuts (Enter to send, Shift+Enter for newline)
 * 
 * DEPENDENCIES:
 * - agent-ui.css (styling)
 * - Global notification system (showNotification)
 * 
 * EXPORTS:
 * - AgentInput.init(agentId) - Initialize input handlers
 * - AgentInput.attachFile(agentId, files) - Handle file attachment
 * - AgentInput.clearFiles(agentId) - Clear attached files
 * - AgentInput.getValue(agentId) - Get textarea value
 * - AgentInput.setValue(agentId, value) - Set textarea value
 * - AgentInput.focus(agentId) - Focus textarea
 * 
 * USED BY:
 * - agent-ui.js (main agent UI builder)
 * - MultiAgent system
 * 
 * LAST MODIFIED: 2025-11-15 - Initial extraction from monolithic HTML
 */

const AgentInput = (function () {
    'use strict';

    // Storage for attached files per agent
    const attachedFiles = {};

    // Configuration
    const NATIVE_TYPES = new Set([
        'application/pdf',
        'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'
    ]);

    const EXTRACTABLE_TYPES = new Set([
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/msword', 'application/vnd.ms-excel', 'application/vnd.ms-powerpoint',
        'text/plain', 'text/csv', 'text/markdown', 'text/html', 'text/css',
        'application/json', 'application/xml', 'text/xml',
        'application/javascript', 'text/javascript', 'text/x-python',
        'application/x-python', 'application/x-sh', 'text/x-sh',
        'application/rtf', 'text/rtf'
    ]);

    const EXTRACTABLE_EXTENSIONS = new Set([
        'docx','doc','xlsx','xls','pptx','ppt',
        'txt','csv','md','html','htm','css',
        'json','xml','js','ts','py','sh','rb',
        'java','cpp','c','cs','go','rs','rtf'
    ]);

    function getFileIcon(filename) {
        const ext = (filename.split('.').pop() || '').toLowerCase();
        if (['doc','docx','rtf'].includes(ext)) return 'fa-file-word';
        if (['xls','xlsx','csv'].includes(ext)) return 'fa-file-excel';
        if (['ppt','pptx'].includes(ext)) return 'fa-file-powerpoint';
        if (['js','ts','py','sh','rb','java','cpp','c','cs','go','rs','json','xml','html','htm','css'].includes(ext)) return 'fa-file-code';
        if (['txt','md'].includes(ext)) return 'fa-file-alt';
        return 'fa-file-alt';
    }

    const CONFIG = {
        maxPdfSize: 32 * 1024 * 1024,        // 32MB
        maxImageSize: 5 * 1024 * 1024,       // 5MB
        maxExtractableSize: 20 * 1024 * 1024, // 20MB
        minHeight: 80,
        maxHeight: 200
    };

    /**
     * Initialize input handlers for an agent
     * @param {number} agentId - Agent ID
     */
    function init(agentId) {
        const textarea = document.getElementById(`input-${agentId}`);
        const attachBtn = document.getElementById(`attach-${agentId}`);
        const fileInput = document.getElementById(`file-input-${agentId}`);

        if (!textarea || !attachBtn || !fileInput) {
            console.warn(`[AgentInput] Missing elements for agent ${agentId}`);
            return;
        }

        // Initialize file storage
        if (!attachedFiles[agentId]) {
            attachedFiles[agentId] = [];
        }

        // Auto-expand textarea on input
        textarea.addEventListener('input', handleTextareaInput);

        // Keyboard shortcuts
        textarea.addEventListener('keydown', (e) => handleKeypress(e, agentId));

        // File attachment button
        attachBtn.addEventListener('click', () => {
            fileInput.click();
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelection(agentId, Array.from(e.target.files));
            }
        });

        // Drag and drop
        textarea.addEventListener('dragover', handleDragOver);
        textarea.addEventListener('dragleave', handleDragLeave);
        textarea.addEventListener('drop', (e) => handleDrop(e, agentId));

        console.log(`[AgentInput] Initialized for agent ${agentId}`);
    }

    /**
     * Handle textarea input - auto-expand
     * @param {Event} e - Input event
     */
    function handleTextareaInput(e) {
        const textarea = e.target;
        textarea.style.height = 'auto';
        const newHeight = Math.min(Math.max(textarea.scrollHeight, CONFIG.minHeight), CONFIG.maxHeight);
        textarea.style.height = `${newHeight}px`;
    }

    /**
     * Handle keypress events
     * @param {KeyboardEvent} e - Keyboard event
     * @param {number} agentId - Agent ID
     */
    function handleKeypress(e, agentId) {
        // Enter without Shift = Send message
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();

            // Trigger send (assumes sendAgentMessage function exists globally)
            if (typeof sendAgentMessage === 'function') {
                sendAgentMessage(agentId);
            } else {
                console.warn('[AgentInput] sendAgentMessage function not found');
            }
        }

        // Shift + Enter = New line (default behavior)
    }

    /**
     * Handle file selection
     * @param {number} agentId - Agent ID
     * @param {File[]} files - Array of files
     */
    function handleFileSelection(agentId, files) {
        for (const file of files) {
            // Validate file type
            const ext = (file.name.split('.').pop() || '').toLowerCase();
            const isNative = NATIVE_TYPES.has(file.type);
            const isExtractable = EXTRACTABLE_TYPES.has(file.type) || EXTRACTABLE_EXTENSIONS.has(ext);
            if (!isNative && !isExtractable) {
                showNotification(
                    `Unsupported file type: ${file.name}. Supported: PDF, images, Word, Excel, PowerPoint, text and code files.`,
                    'error'
                );
                continue;
            }

            // Validate file size
            let maxSize;
            if (file.type === 'application/pdf') {
                maxSize = CONFIG.maxPdfSize;
            } else if (NATIVE_TYPES.has(file.type) && file.type.startsWith('image/')) {
                maxSize = CONFIG.maxImageSize;
            } else {
                maxSize = CONFIG.maxExtractableSize;
            }
            if (file.size > maxSize) {
                const maxSizeMB = (maxSize / 1024 / 1024).toFixed(0);
                showNotification(
                    `File too large: ${file.name}. Max size: ${maxSizeMB}MB`,
                    'error'
                );
                continue;
            }

            // Add to attached files
            attachedFiles[agentId].push(file);
        }

        // Update UI
        updateAttachedFilesUI(agentId);

        // Reset file input
        const fileInput = document.getElementById(`file-input-${agentId}`);
        if (fileInput) {
            fileInput.value = '';
        }
    }

    /**
     * Update attached files UI
     * @param {number} agentId - Agent ID
     */
    function updateAttachedFilesUI(agentId) {
        const container = document.getElementById(`agent-attached-files-${agentId}`);
        if (!container) return;

        const files = attachedFiles[agentId] || [];
        container.innerHTML = '';

        files.forEach((file, index) => {
            const chip = document.createElement('div');
            chip.className = 'agent-file-chip';

            const icon = file.type === 'application/pdf' ? 'fa-file-pdf' :
                         (file.type.startsWith('image/') ? 'fa-image' : getFileIcon(file.name));
            const sizeKB = file.size / 1024;
            const sizeStr = sizeKB >= 1024 ? `${(sizeKB / 1024).toFixed(1)}MB` : `${sizeKB.toFixed(1)}KB`;

            chip.innerHTML = `
                <i class="fas ${icon}"></i>
                <span>${file.name} (${sizeStr})</span>
                <button class="agent-file-chip-remove" data-index="${index}" aria-label="Remove file">×</button>
            `;

            // Remove file on click
            chip.querySelector('.agent-file-chip-remove').addEventListener('click', () => {
                attachedFiles[agentId].splice(index, 1);
                updateAttachedFilesUI(agentId);
            });

            container.appendChild(chip);
        });
    }

    /**
     * Handle drag over event
     * @param {DragEvent} e - Drag event
     */
    function handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        e.target.classList.add('drag-over');
    }

    /**
     * Handle drag leave event
     * @param {DragEvent} e - Drag event
     */
    function handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        e.target.classList.remove('drag-over');
    }

    /**
     * Handle drop event
     * @param {DragEvent} e - Drag event
     * @param {number} agentId - Agent ID
     */
    function handleDrop(e, agentId) {
        e.preventDefault();
        e.stopPropagation();
        e.target.classList.remove('drag-over');

        const files = Array.from(e.dataTransfer.files);
        if (files.length > 0) {
            handleFileSelection(agentId, files);
        }
    }

    /**
     * Get attached files for an agent
     * @param {number} agentId - Agent ID
     * @returns {File[]} Array of attached files
     */
    function getFiles(agentId) {
        return attachedFiles[agentId] || [];
    }

    /**
     * Clear attached files for an agent
     * @param {number} agentId - Agent ID
     */
    function clearFiles(agentId) {
        attachedFiles[agentId] = [];
        updateAttachedFilesUI(agentId);
    }

    /**
     * Get textarea value
     * @param {number} agentId - Agent ID
     * @returns {string} Textarea value
     */
    function getValue(agentId) {
        const textarea = document.getElementById(`input-${agentId}`);
        return textarea ? textarea.value : '';
    }

    /**
     * Set textarea value
     * @param {number} agentId - Agent ID
     * @param {string} value - New value
     */
    function setValue(agentId, value) {
        const textarea = document.getElementById(`input-${agentId}`);
        if (textarea) {
            textarea.value = value;
            // Trigger input event to update height
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    /**
     * Focus textarea
     * @param {number} agentId - Agent ID
     */
    function focus(agentId) {
        const textarea = document.getElementById(`input-${agentId}`);
        if (textarea) {
            textarea.focus();
        }
    }

    /**
     * Show notification (uses global notification system)
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, warning, info)
     */
    function showNotification(message, type = 'info') {
        // Check if global notification function exists
        if (typeof window.showNotification === 'function') {
            window.showNotification(message, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }

    // Public API
    return {
        init,
        getFiles,
        clearFiles,
        getValue,
        setValue,
        focus,
        attachFile: handleFileSelection
    };
})();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AgentInput;
}
