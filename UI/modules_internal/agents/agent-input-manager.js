/**
 * FILE: UI/modules/agents/agent-input-manager.js
 * PURPOSE: Manage expandable input containers for agent columns (Prime-style)
 * 
 * FEATURES:
 * - 4-state sliding input system (collapsed bar → hover → focus → expanded)
 * - Per-agent feedback areas
 * - Per-agent voice transcription
 * - Per-agent auto-scroll toggle
 * - Prompt library integration
 * - Complete column-specific isolation (no cross-contamination)
 * 
 * DEPENDENCIES:
 * - SharedTranscriptionState (global transcription manager)
 * - MultiAgent (agent orchestration)
 * - ThreadManager (thread management)
 * - agent-ui.css (styling)
 * 
 * EXPORTS:
 * - AgentInput.initState(agentId) - Initialize agent input state
 * - AgentInput.expand(agentId) - Expand input area
 * - AgentInput.collapse(agentId) - Collapse input area
 * - AgentInput.toggleFeedback(agentId) - Toggle feedback container
 * - AgentInput.sendFeedback(agentId) - Send feedback to AI
 * - AgentInput.insertQuickFeedback(agentId, type) - Insert quick feedback
 * - AgentInput.toggleTranscription(agentId) - Start/stop voice recording
 * - AgentInput.toggleAutoScroll(agentId) - Toggle auto-scroll
 * - AgentInput.showPromptLibrary(agentId) - Show prompt library
 * - AgentInput.showFileDialog(agentId) - Show file picker
 * - AgentInput.setupHandlers(agentId) - Setup event handlers
 * - AgentInput.cleanupHandlers(agentId) - Cleanup event handlers
 * 
 * USED BY:
 * - agent-js.js (MultiAgent system)
 * - agent-column.js (column creation)
 * 
 * LAST MODIFIED: 2025-12-01 - Initial creation for expandable input
 */

const AgentInput = (function () {
    'use strict';

    // Global state object for all agents (column-specific isolation)
    const states = {};

    // Event handler storage for cleanup
    const handlers = {};

    // Configuration for file attachments
    const FILE_CONFIG = {
        maxPdfSize: 32 * 1024 * 1024,        // 32MB
        maxImageSize: 5 * 1024 * 1024,       // 5MB
        maxExtractableSize: 20 * 1024 * 1024  // 20MB
    };

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
        'docx','doc','xlsx','xls','pptx','ppt','txt','csv','md','html','htm','css',
        'json','xml','js','ts','py','sh','rb','java','cpp','c','cs','go','rs','rtf'
    ]);

    function getFileIcon(filename) {
        const ext = (filename.split('.').pop() || '').toLowerCase();
        if (['doc','docx','rtf'].includes(ext)) return 'fa-file-word';
        if (['xls','xlsx','csv'].includes(ext)) return 'fa-file-excel';
        if (['ppt','pptx'].includes(ext)) return 'fa-file-powerpoint';
        if (['js','ts','py','sh','rb','java','cpp','c','cs','go','rs','json','xml','html','htm','css'].includes(ext)) return 'fa-file-code';
        return 'fa-file-alt';
    }

    /**
     * Initialize state for specific agent
     * @param {number} agentId - Agent ID
     */
    function initState(agentId) {
        if (!states[agentId]) {
            states[agentId] = {
                isExpanded: false,
                isFeedbackOpen: false,
                isRecording: false,
                isAutoScrollEnabled: true,
                feedbackText: '',
                transcriptionActive: false,
                attachedFiles: []
            };
            console.log(`[AgentInput] Initialized state for Agent-${agentId}`);
        }
    }

    /**
     * Get state for specific agent
     * @param {number} agentId - Agent ID
     * @returns {Object} Agent state
     */
    function getState(agentId) {
        if (!states[agentId]) {
            initState(agentId);
        }
        return states[agentId];
    }

    /**
     * Expand input area for specific agent
     * @param {number} agentId - Agent ID
     */
    function expand(agentId) {
        const state = getState(agentId);
        const container = document.querySelector(`#agent-column-${agentId} .agent-input-container`);

        console.log(`[AgentInput] expand() called for agent-${agentId}:`, {
            containerFound: !!container,
            currentlyExpanded: state.isExpanded,
            containerClasses: container?.className,
            containerHeight: container?.offsetHeight
        });

        if (!container) {
            console.error(`❌ [AgentInput] Container not found for agent-${agentId}`);
            return;
        }

        if (state.isExpanded) {
            console.warn(`⚠️ [AgentInput] Agent-${agentId} already expanded`);
            return;
        }

        state.isExpanded = true;
        container.classList.add('expanded');

        console.log(`✅ [AgentInput] Agent-${agentId} expanded - classes:`, container.className);

        // Focus textarea
        const textarea = document.getElementById(`agent-input-${agentId}`);
        if (textarea) {
            setTimeout(() => {
                textarea.focus();
                console.log(`[AgentInput] Focused textarea for agent-${agentId}`);
            }, 100);
        } else {
            console.warn(`⚠️ [AgentInput] Textarea not found for agent-${agentId}`);
        }

        // ALWAYS scroll to bottom when expanding (compensate for lost message space)
        // This is separate from auto-scroll toggle - expansion changes viewport
        setTimeout(() => {
            const messagesContainer = document.getElementById(`messages-${agentId}`);
            if (messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                console.log(`[AgentInput] Scrolled messages to bottom after expand for agent-${agentId}`);
            }
        }, 100);
    }

    /**
     * Collapse input area for specific agent
     * @param {number} agentId - Agent ID
     */
    function collapse(agentId) {
        const state = getState(agentId);
        const container = document.querySelector(`#agent-column-${agentId} .agent-input-container`);

        if (!container || !state.isExpanded) return;

        state.isExpanded = false;
        container.classList.remove('expanded');

        console.log(`[AgentInput] Agent-${agentId} collapsed`);
    }

    /**
     * Toggle feedback container for specific agent
     * @param {number} agentId - Agent ID
     */
    function toggleFeedback(agentId) {
        const state = getState(agentId);
        const container = document.getElementById(`agent-feedback-${agentId}`);
        const btn = document.getElementById(`agent-feedback-btn-${agentId}`);

        if (!container) return;

        state.isFeedbackOpen = !state.isFeedbackOpen;
        container.classList.toggle('active', state.isFeedbackOpen);

        if (btn) {
            btn.classList.toggle('active', state.isFeedbackOpen);
        }

        // Focus feedback textarea if opening
        if (state.isFeedbackOpen) {
            const textarea = document.getElementById(`agent-feedback-text-${agentId}`);
            if (textarea) {
                setTimeout(() => textarea.focus(), 100);
            }
        }

        console.log(`[AgentInput] Agent-${agentId} feedback ${state.isFeedbackOpen ? 'opened' : 'closed'}`);
    }

    /**
     * Insert quick feedback for specific agent
     * @param {number} agentId - Agent ID
     * @param {string} type - Feedback type ('pause', 'stop', 'explain')
     */
    function insertQuickFeedback(agentId, type) {
        const textarea = document.getElementById(`agent-feedback-text-${agentId}`);
        if (!textarea) return;

        const messages = {
            'pause': 'Please pause and wait for my instructions.',
            'stop': 'Please stop the current task.',
            'explain': 'Can you explain what you are doing?'
        };

        textarea.value = messages[type] || '';
        textarea.focus();

        console.log(`[AgentInput] Agent-${agentId} quick feedback: ${type}`);
    }

    /**
     * Send feedback for specific agent
     * @param {number} agentId - Agent ID
     */
    function sendFeedback(agentId) {
        const textarea = document.getElementById(`agent-feedback-text-${agentId}`);
        if (!textarea || !textarea.value.trim()) {
            console.warn(`[AgentInput] Agent-${agentId} feedback empty, not sending`);
            return;
        }

        const feedbackText = textarea.value.trim();

        // Send feedback as message to this specific agent (with feedback flag)
        if (typeof MultiAgent !== 'undefined' && typeof MultiAgent.sendMessage === 'function') {
            MultiAgent.sendMessage(agentId, feedbackText, { isFeedback: true });
        } else if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.sendMessage === 'function') {
            AgentColumn.sendMessage(agentId, feedbackText);
        } else {
            console.error(`[AgentInput] Agent-${agentId} cannot send feedback - no send function available`);
        }

        // Clear feedback and close
        textarea.value = '';
        toggleFeedback(agentId);

        console.log(`[AgentInput] Agent-${agentId} feedback sent: "${feedbackText}"`);
    }

    /**
     * Toggle transcription for specific agent
     * @param {number} agentId - Agent ID
     */
    function toggleTranscription(agentId) {
        const state = getState(agentId);
        const micBtn = document.getElementById(`agent-mic-${agentId}`);

        if (!micBtn) {
            console.error(`[AgentInput] Agent-${agentId} mic button not found`);
            return;
        }

        if (state.isRecording) {
            // Stop recording
            if (window.SharedTranscriptionState && typeof window.SharedTranscriptionState.stopRecording === 'function') {
                window.SharedTranscriptionState.stopRecording();
            }
            micBtn.classList.remove('recording');
            micBtn.querySelector('i').className = 'fas fa-microphone';
            micBtn.title = 'Start voice transcription';
            state.isRecording = false;
            console.log(`[AgentInput] Agent-${agentId} transcription stopped`);
        } else {
            // ✅ AUTO-EXPAND: Expand input area when starting transcription
            expand(agentId);

            // Start recording (target this agent's input)
            if (window.SharedTranscriptionState && typeof window.SharedTranscriptionState.startRecording === 'function') {
                // Pass target selector so transcription knows where to route text
                const targetInput = document.getElementById(`agent-input-${agentId}`);

                if (!targetInput) {
                    console.error(`[AgentInput] Agent-${agentId} input textarea not found`);
                    return;
                }

                // Start recording with target callback
                window.SharedTranscriptionState.startRecording(null, (finalTranscript, interimTranscript) => {
                    // Route transcript to THIS agent's input
                    if (finalTranscript) {
                        targetInput.value += finalTranscript + ' ';
                        console.log(`[AgentInput] Agent-${agentId} received transcript: "${finalTranscript}"`);

                        // Auto-expand textarea if needed (dispatch input event)
                        targetInput.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                })
                    .then(() => {
                        micBtn.classList.add('recording');
                        micBtn.querySelector('i').className = 'fas fa-stop';
                        micBtn.title = 'Stop recording';
                        state.isRecording = true;
                        console.log(`[AgentInput] Agent-${agentId} transcription started and input expanded`);
                    })
                    .catch(error => {
                        console.error(`[AgentInput] Agent-${agentId} transcription failed:`, error);
                        alert(`Could not start recording for Agent ${agentId}: ` + error.message);
                    });
            } else {
                console.error(`[AgentInput] Agent-${agentId} SharedTranscriptionState not available`);
                alert('Voice transcription is not available');
            }
        }
    }

    /**
     * Toggle auto-scroll for specific agent
     * @param {number} agentId - Agent ID
     */
    function toggleAutoScroll(agentId) {
        const state = getState(agentId);
        const btn = document.getElementById(`agent-autoscroll-${agentId}`);

        if (!btn) return;

        state.isAutoScrollEnabled = !state.isAutoScrollEnabled;
        btn.classList.toggle('active', state.isAutoScrollEnabled);

        console.log(`[AgentInput] Agent-${agentId} auto-scroll ${state.isAutoScrollEnabled ? 'enabled' : 'disabled'}`);
    }

    /**
     * Show prompt library for specific agent
     * @param {number} agentId - Agent ID
     */
    function showPromptLibrary(agentId) {
        console.log(`[AgentInput] Agent-${agentId} prompt library (Instruction Catalog) requested`);

        // Get agent name for display
        const agentName = getAgentName(agentId);
        
        // Open the prompt library sidebar with agent context
        if (window.openInstructionCatalog && typeof window.openInstructionCatalog === 'function') {
            window.openInstructionCatalog(agentId, agentName);
        } else {
            console.error('[AgentInput] Instruction Catalog not available - prompt-library.js may not be loaded');
            alert(`Instruction Catalog for ${agentName}\n\n(Module not loaded - check console)`);
        }
    }

    /**
     * Get agent display name
     * @param {number} agentId - Agent ID
     * @returns {string} Agent display name
     */
    function getAgentName(agentId) {
        // Special case for Prime AI
        if (agentId === 1 || agentId === '1') {
            return 'Prime AI';
        }
        
        // Try to get from MultiAgent if available
        if (window.MultiAgent && window.MultiAgent.agents && window.MultiAgent.agents[agentId]) {
            return window.MultiAgent.agents[agentId].name || `Agent ${agentId}`;
        }
        
        // Fallback to generic name
        return `Agent ${agentId}`;
    }

    /**
     * Show file dialog for specific agent
     * @param {number} agentId - Agent ID
     */
    function showFileDialog(agentId, event) {
        // Prevent event bubbling to avoid double trigger
        if (event) {
            event.stopPropagation();
            event.preventDefault();
        }

        const fileInput = document.getElementById(`agent-file-input-${agentId}`);
        if (fileInput) {
            fileInput.click();
        } else {
            console.error(`[AgentInput] Agent-${agentId} file input not found`);
        }
    }

    /**
     * Setup event handlers for agent input area
     * @param {number} agentId - Agent ID
     */
    function setupHandlers(agentId) {
        // Prevent duplicate handler setup
        if (handlers[agentId]) {
            console.log(`[AgentInput] Handlers already initialized for agent-${agentId}, skipping`);
            return;
        }

        initState(agentId);

        const container = document.querySelector(`#agent-column-${agentId} .agent-input-container`);
        const textarea = document.getElementById(`agent-input-${agentId}`);
        const fileInput = document.getElementById(`agent-file-input-${agentId}`);

        if (!container || !textarea) {
            console.warn(`[AgentInput] Agent-${agentId} elements not found for handler setup`);
            console.log(`  Container found: ${!!container}, Textarea found: ${!!textarea}`);
            return;
        }

        console.log(`[AgentInput] Setting up handlers for agent-${agentId}...`);

        // Store handlers for cleanup
        handlers[agentId] = {};

        // Click collapsed bar to expand (CRITICAL: Must work when clicking visible 30px bar)
        handlers[agentId].containerClick = (e) => {
            const state = getState(agentId);

            // Debug logging
            console.log(`[AgentInput] Click detected on agent-${agentId}:`, {
                isExpanded: state.isExpanded,
                containerHeight: container.offsetHeight,
                hasExpandedClass: container.classList.contains('expanded'),
                target: e.target.className,
                currentTarget: e.currentTarget.className,
                computedHeight: window.getComputedStyle(container).height
            });

            // Only expand if currently collapsed
            // Check both state and class to ensure consistency
            if (!state.isExpanded && !container.classList.contains('expanded')) {
                e.preventDefault();
                e.stopPropagation();
                expand(agentId);
                console.log(`✅ [AgentInput] Agent-${agentId} expanded via click`);
            } else {
                console.log(`[AgentInput] Agent-${agentId} already expanded, ignoring click`);
            }
        };
        // Use capture phase to intercept clicks before they reach child elements
        container.addEventListener('click', handlers[agentId].containerClick, true);

        // Focus textarea to expand
        handlers[agentId].textareaFocus = () => {
            expand(agentId);
        };
        textarea.addEventListener('focus', handlers[agentId].textareaFocus);

        // Blur to collapse (if empty and no active elements)
        handlers[agentId].textareaBlur = () => {
            setTimeout(() => {
                // Check if focus moved to another element within the container
                const activeElement = document.activeElement;
                const isWithinContainer = container.contains(activeElement);
                const isEmpty = textarea.value.trim() === '';

                if (!isWithinContainer && isEmpty) {
                    collapse(agentId);
                }
            }, 200); // Delay to allow button clicks
        };
        textarea.addEventListener('blur', handlers[agentId].textareaBlur);

        // Enter to send (Shift+Enter for new line)
        handlers[agentId].textareaKeydown = (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.sendMessage === 'function') {
                    AgentColumn.sendMessage(agentId);
                } else if (typeof MultiAgent !== 'undefined' && typeof MultiAgent.sendMessage === 'function') {
                    MultiAgent.sendMessage(agentId);
                }
            }
        };
        textarea.addEventListener('keydown', handlers[agentId].textareaKeydown);

        // File input change handler
        if (fileInput) {
            handlers[agentId].fileChange = (e) => {
                const files = Array.from(e.target.files);
                console.log(`[AgentInput] Agent-${agentId} files selected:`, files.length);

                // Use attachFiles function for validation and UI update
                attachFiles(agentId, files);

                // Call MultiAgent handler if available (for backward compatibility)
                if (typeof MultiAgent !== 'undefined' && typeof MultiAgent.handleFileAttachment === 'function') {
                    MultiAgent.handleFileAttachment(agentId, files);
                }
            };
            fileInput.addEventListener('change', handlers[agentId].fileChange);
        }

        // Drag-and-drop handlers
        handlers[agentId].dragOver = (e) => {
            e.preventDefault();
            e.stopPropagation();
            // For thread drops, highlight the agent column instead of the input container
            if (e.dataTransfer.types.includes('application/x-thread-id')) {
                const agentColumn = document.getElementById(`agent-column-${agentId}`);
                if (agentColumn) agentColumn.classList.add('drag-over');
            } else {
                container.classList.add('drag-over');
            }
        };

        handlers[agentId].dragLeave = (e) => {
            e.preventDefault();
            e.stopPropagation();
            container.classList.remove('drag-over');
            const agentColumn = document.getElementById(`agent-column-${agentId}`);
            if (agentColumn) agentColumn.classList.remove('drag-over');
        };

        handlers[agentId].drop = (e) => {
            e.preventDefault();
            e.stopPropagation();
            container.classList.remove('drag-over');
            const agentColumn = document.getElementById(`agent-column-${agentId}`);
            if (agentColumn) agentColumn.classList.remove('drag-over');

            // Thread card drop — delegate to ThreadManager instead of processing as file
            const threadId = e.dataTransfer.getData('application/x-thread-id');
            if (threadId) {
                console.log(`[AgentInput] Thread drop detected on agent-${agentId} input area, delegating to ThreadManager`);
                if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.handleDrop === 'function') {
                    ThreadManager.handleDrop(e, `agent-${agentId}`);
                }
                return;
            }

            const files = Array.from(e.dataTransfer.files);
            if (files.length > 0) {
                console.log(`[AgentInput] Agent-${agentId} files dropped:`, files.length);
                attachFiles(agentId, files);

                // Call MultiAgent handler if available
                if (typeof MultiAgent !== 'undefined' && typeof MultiAgent.handleFileAttachment === 'function') {
                    MultiAgent.handleFileAttachment(agentId, files);
                }
            }
        };

        container.addEventListener('dragover', handlers[agentId].dragOver);
        container.addEventListener('dragleave', handlers[agentId].dragLeave);
        container.addEventListener('drop', handlers[agentId].drop);

        console.log(`[AgentInput] Agent-${agentId} handlers initialized (with drag-drop)`);
    }

    /**
     * Cleanup event handlers for agent
     * @param {number} agentId - Agent ID
     */
    function cleanupHandlers(agentId) {
        if (!handlers[agentId]) return;

        const container = document.querySelector(`#agent-column-${agentId} .agent-input-container`);
        const textarea = document.getElementById(`agent-input-${agentId}`);
        const fileInput = document.getElementById(`agent-file-input-${agentId}`);

        const agentHandlers = handlers[agentId];

        if (container) {
            if (agentHandlers.containerClick) {
                container.removeEventListener('click', agentHandlers.containerClick);
            }
            if (agentHandlers.dragOver) {
                container.removeEventListener('dragover', agentHandlers.dragOver);
            }
            if (agentHandlers.dragLeave) {
                container.removeEventListener('dragleave', agentHandlers.dragLeave);
            }
            if (agentHandlers.drop) {
                container.removeEventListener('drop', agentHandlers.drop);
            }
        }

        if (textarea) {
            if (agentHandlers.textareaFocus) {
                textarea.removeEventListener('focus', agentHandlers.textareaFocus);
            }
            if (agentHandlers.textareaBlur) {
                textarea.removeEventListener('blur', agentHandlers.textareaBlur);
            }
            if (agentHandlers.textareaKeydown) {
                textarea.removeEventListener('keydown', agentHandlers.textareaKeydown);
            }
        }

        if (fileInput && agentHandlers.fileChange) {
            fileInput.removeEventListener('change', agentHandlers.fileChange);
        }

        delete handlers[agentId];
        delete states[agentId];

        console.log(`[AgentInput] Agent-${agentId} handlers cleaned up`);
    }

    // ==================== FILE ATTACHMENT FUNCTIONS ====================

    /**
     * Handle file selection for agent
     * @param {number} agentId - Agent ID
     * @param {File[]} files - Array of files to attach
     */
    function attachFiles(agentId, files) {
        const state = getState(agentId);

        for (const file of files) {
            // Validate file type
            const _ext = (file.name.split('.').pop() || '').toLowerCase();
            const _isNative = NATIVE_TYPES.has(file.type);
            const _isExtractable = EXTRACTABLE_TYPES.has(file.type) || EXTRACTABLE_EXTENSIONS.has(_ext);
            if (!_isNative && !_isExtractable) {
                console.warn(`[AgentInput] Unsupported file type for agent-${agentId}:`, file.name);
                if (typeof window.showNotification === 'function') {
                    window.showNotification(
                        `Unsupported file type: ${file.name}. Supported: PDF, images, Word, Excel, PowerPoint, text and code files.`,
                        'error'
                    );
                }
                continue;
            }

            // Validate file size
            let maxSize;
            if (file.type === 'application/pdf') { maxSize = FILE_CONFIG.maxPdfSize; }
            else if (_isNative && file.type.startsWith('image/')) { maxSize = FILE_CONFIG.maxImageSize; }
            else { maxSize = FILE_CONFIG.maxExtractableSize; }
            if (file.size > maxSize) {
                const maxSizeMB = (maxSize / 1024 / 1024).toFixed(0);
                console.warn(`[AgentInput] File too large for agent-${agentId}:`, file.name);
                if (typeof window.showNotification === 'function') {
                    window.showNotification(
                        `File too large: ${file.name}. Max size: ${maxSizeMB}MB`,
                        'error'
                    );
                }
                continue;
            }

            // Add to attached files
            state.attachedFiles.push(file);
        }

        // ✅ BRIDGE: Sync with legacy window.agentAttachedFiles for sendAgentMessage compatibility
        if (!window.agentAttachedFiles) {
            window.agentAttachedFiles = {};
        }
        window.agentAttachedFiles[agentId] = state.attachedFiles;

        // Update UI
        updateAttachedFilesUI(agentId);

        console.log(`[AgentInput] Agent-${agentId} attached ${files.length} file(s), synced to window.agentAttachedFiles`);
    }

    /**
     * Update attached files UI display
     * @param {number} agentId - Agent ID
     */
    function updateAttachedFilesUI(agentId) {
        const state = getState(agentId);
        const container = document.getElementById(`agent-attached-files-${agentId}`);

        if (!container) {
            console.warn(`[AgentInput] Agent-${agentId} attached files container not found`);
            return;
        }

        const files = state.attachedFiles || [];
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
                state.attachedFiles.splice(index, 1);

                // ✅ BRIDGE: Sync with legacy window.agentAttachedFiles
                if (window.agentAttachedFiles && window.agentAttachedFiles[agentId]) {
                    window.agentAttachedFiles[agentId] = state.attachedFiles;
                }

                updateAttachedFilesUI(agentId);
            });

            container.appendChild(chip);
        });
    }

    /**
     * Clear attached files for agent
     * @param {number} agentId - Agent ID
     */
    function clearFiles(agentId) {
        const state = getState(agentId);
        state.attachedFiles = [];

        // ✅ BRIDGE: Sync with legacy window.agentAttachedFiles
        if (window.agentAttachedFiles && window.agentAttachedFiles[agentId]) {
            window.agentAttachedFiles[agentId] = [];
        }

        updateAttachedFilesUI(agentId);
        console.log(`[AgentInput] Agent-${agentId} cleared attached files`);
    }

    /**
     * Get attached files for agent
     * @param {number} agentId - Agent ID
     * @returns {File[]} Array of attached files
     */
    function getFiles(agentId) {
        const state = getState(agentId);
        return state.attachedFiles || [];
    }

    /**
     * Get textarea value for agent
     * @param {number} agentId - Agent ID
     * @returns {string} Textarea value
     */
    function getValue(agentId) {
        const textarea = document.getElementById(`agent-input-${agentId}`);
        return textarea ? textarea.value : '';
    }

    /**
     * Set textarea value for agent
     * @param {number} agentId - Agent ID
     * @param {string} value - New value
     */
    function setValue(agentId, value) {
        const textarea = document.getElementById(`agent-input-${agentId}`);
        if (textarea) {
            textarea.value = value;
            // Trigger input event for any listeners
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    /**
     * Render attached prompts UI (similar to file attachments)
     * @param {number} agentId - Agent ID
     */
    function renderAttachedPrompts(agentId) {
        const key = `agent_${agentId}_pending_prompts`;
        const stored = sessionStorage.getItem(key);
        
        // Find or create container (same area as file attachments)
        let container = document.getElementById(`agent-attached-prompts-${agentId}`);
        if (!container) {
            // Create container below files area
            const filesContainer = document.getElementById(`agent-attached-files-${agentId}`);
            if (filesContainer) {
                container = document.createElement('div');
                container.id = `agent-attached-prompts-${agentId}`;
                container.className = 'agent-attached-prompts';
                filesContainer.parentNode.insertBefore(container, filesContainer.nextSibling);
            }
        }
        
        if (!container) {
            console.warn(`[AgentInput] Cannot find container for Agent-${agentId} prompts`);
            return;
        }
        
        if (!stored) {
            container.innerHTML = '';
            container.style.display = 'none';
            return;
        }
        
        try {
            const prompts = JSON.parse(stored);
            if (prompts.length === 0) {
                container.innerHTML = '';
                container.style.display = 'none';
                return;
            }
            
            // Render prompt chips with drag & drop support
            container.style.display = 'flex';
            container.innerHTML = prompts.map((p, index) => `
                <div class="attached-prompt-chip" 
                     data-prompt-id="${p.id}"
                     data-prompt-index="${index}"
                     draggable="true"
                     ondragstart="AgentInput.handlePromptDragStart(event, ${agentId})"
                     ondragover="AgentInput.handlePromptDragOver(event)"
                     ondrop="AgentInput.handlePromptDrop(event, ${agentId})"
                     ondragend="AgentInput.handlePromptDragEnd(event)"
                     title="${p.prompt_text.replace(/"/g, '&quot;').substring(0, 200)}${p.prompt_text.length > 200 ? '...' : ''}">
                    <i class="fas fa-grip-vertical" style="color: #999; cursor: grab; margin-right: 4px; font-size: 10px;"></i>
                    <i class="fas fa-bolt" style="color: #ffa500;"></i>
                    <span class="prompt-name">${p.name}</span>
                    <span class="prompt-type-badge">${p.type === 'quick_action' ? 'Quick' : 'Full'}</span>
                    <button class="remove-prompt-btn" onclick="AgentInput.removePrompt(${agentId}, ${p.id})" title="Remove prompt">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `).join('');
            
            // Add tooltips for full prompt preview
            setupPromptTooltips(agentId);
            
            console.log(`[AgentInput] Rendered ${prompts.length} prompt(s) for Agent-${agentId} (drag & drop enabled)`);
        } catch (error) {
            console.error(`[AgentInput] Failed to render prompts for Agent-${agentId}:`, error);
            container.innerHTML = '';
            container.style.display = 'none';
        }
    }
    
    /**
     * Setup interactive tooltips for prompt preview
     * @param {number} agentId - Agent ID
     */
    function setupPromptTooltips(agentId) {
        const container = document.getElementById(`agent-attached-prompts-${agentId}`);
        if (!container) return;
        
        const chips = container.querySelectorAll('.attached-prompt-chip');
        chips.forEach(chip => {
            chip.addEventListener('mouseenter', (e) => {
                const promptId = parseInt(chip.dataset.promptId);
                const prompts = getPendingPrompts(agentId);
                const prompt = prompts.find(p => p.id === promptId);
                
                if (prompt && prompt.prompt_text) {
                    showPromptTooltip(e.currentTarget, prompt);
                }
            });
            
            chip.addEventListener('mouseleave', () => {
                hidePromptTooltip();
            });
        });
    }
    
    /**
     * Show tooltip with full prompt text
     * @param {HTMLElement} element - Element to attach tooltip to
     * @param {Object} prompt - Prompt object
     */
    function showPromptTooltip(element, prompt) {
        // Remove existing tooltip
        hidePromptTooltip();
        
        const tooltip = document.createElement('div');
        tooltip.id = 'prompt-preview-tooltip';
        tooltip.className = 'prompt-preview-tooltip';
        tooltip.innerHTML = `
            <div class="tooltip-header">
                <strong>${prompt.name}</strong>
                <span class="tooltip-type">${prompt.type === 'quick_action' ? 'Quick Action' : 'Full Prompt'}</span>
            </div>
            <div class="tooltip-content">${prompt.prompt_text}</div>
        `;
        
        document.body.appendChild(tooltip);
        
        // Position tooltip
        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        let top = rect.top - tooltipRect.height - 10;
        let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        
        // Keep tooltip within viewport
        if (top < 10) {
            top = rect.bottom + 10;
        }
        if (left < 10) {
            left = 10;
        }
        if (left + tooltipRect.width > window.innerWidth - 10) {
            left = window.innerWidth - tooltipRect.width - 10;
        }
        
        tooltip.style.top = `${top}px`;
        tooltip.style.left = `${left}px`;
        tooltip.style.opacity = '1';
    }
    
    /**
     * Hide prompt tooltip
     */
    function hidePromptTooltip() {
        const tooltip = document.getElementById('prompt-preview-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }
    
    // Drag & Drop State
    let draggedPromptIndex = null;
    
    /**
     * Handle drag start
     * @param {DragEvent} event - Drag event
     * @param {number} agentId - Agent ID
     */
    function handlePromptDragStart(event, agentId) {
        const chip = event.currentTarget;
        draggedPromptIndex = parseInt(chip.dataset.promptIndex);
        
        chip.classList.add('dragging');
        event.dataTransfer.effectAllowed = 'move';
        event.dataTransfer.setData('text/plain', draggedPromptIndex);
        
        hidePromptTooltip();
        console.log(`[AgentInput] Drag started: prompt index ${draggedPromptIndex}`);
    }
    
    /**
     * Handle drag over
     * @param {DragEvent} event - Drag event
     */
    function handlePromptDragOver(event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
        
        const chip = event.currentTarget;
        if (!chip.classList.contains('dragging')) {
            chip.classList.add('drag-over');
        }
    }
    
    /**
     * Handle drop
     * @param {DragEvent} event - Drag event
     * @param {number} agentId - Agent ID
     */
    function handlePromptDrop(event, agentId) {
        event.preventDefault();
        
        const chip = event.currentTarget;
        chip.classList.remove('drag-over');
        
        const dropIndex = parseInt(chip.dataset.promptIndex);
        
        if (draggedPromptIndex !== null && draggedPromptIndex !== dropIndex) {
            // Reorder prompts
            const prompts = getPendingPrompts(agentId);
            const [movedPrompt] = prompts.splice(draggedPromptIndex, 1);
            prompts.splice(dropIndex, 0, movedPrompt);
            
            // Save reordered prompts
            const key = `agent_${agentId}_pending_prompts`;
            sessionStorage.setItem(key, JSON.stringify(prompts));
            
            // Re-render
            renderAttachedPrompts(agentId);
            
            console.log(`[AgentInput] Reordered: moved prompt from ${draggedPromptIndex} to ${dropIndex}`);
        }
    }
    
    /**
     * Handle drag end
     * @param {DragEvent} event - Drag event
     */
    function handlePromptDragEnd(event) {
        const chip = event.currentTarget;
        chip.classList.remove('dragging');
        
        // Remove drag-over from all chips
        document.querySelectorAll('.attached-prompt-chip').forEach(c => {
            c.classList.remove('drag-over');
        });
        
        draggedPromptIndex = null;
    }
    
    /**
     * Remove a specific prompt
     * @param {number} agentId - Agent ID
     * @param {number} promptId - Prompt ID to remove
     */
    function removePrompt(agentId, promptId) {
        const key = `agent_${agentId}_pending_prompts`;
        const stored = sessionStorage.getItem(key);
        
        if (!stored) return;
        
        try {
            let prompts = JSON.parse(stored);
            prompts = prompts.filter(p => p.id !== promptId);
            
            if (prompts.length > 0) {
                sessionStorage.setItem(key, JSON.stringify(prompts));
            } else {
                sessionStorage.removeItem(key);
            }
            
            renderAttachedPrompts(agentId);
            console.log(`[AgentInput] Removed prompt ${promptId} from Agent-${agentId}`);
        } catch (error) {
            console.error(`[AgentInput] Failed to remove prompt:`, error);
        }
    }
    
    /**
     * Clear all prompts for agent
     * @param {number} agentId - Agent ID
     */
    function clearPrompts(agentId) {
        const key = `agent_${agentId}_pending_prompts`;
        sessionStorage.removeItem(key);
        renderAttachedPrompts(agentId);
        console.log(`[AgentInput] Cleared all prompts for Agent-${agentId}`);
    }
    
    /**
     * Get pending prompts for agent
     * @param {number} agentId - Agent ID
     * @returns {Array} Array of prompt objects
     */
    function getPendingPrompts(agentId) {
        const key = `agent_${agentId}_pending_prompts`;
        const stored = sessionStorage.getItem(key);
        
        if (!stored) return [];
        
        try {
            return JSON.parse(stored);
        } catch (error) {
            console.error(`[AgentInput] Failed to parse prompts:`, error);
            return [];
        }
    }

    /**
     * Assign prompts to specific agent
     * Called from prompt library when user confirms assignment
     * @param {number} agentId - Agent ID
     * @param {Array} prompts - Array of prompt objects
     */
    async function assignPrompts(agentId, prompts) {
        console.log(`[AgentInput] Assigning ${prompts.length} prompts to Agent-${agentId}`);
        
        try {
            // Store in sessionStorage for next message send
            const key = `agent_${agentId}_pending_prompts`;
            const promptData = prompts.map(p => ({
                id: p.id,
                name: p.name,
                type: p.type,
                prompt_text: p.prompt_text
            }));
            
            sessionStorage.setItem(key, JSON.stringify(promptData));
            console.log(`[AgentInput] Stored ${prompts.length} prompts for Agent-${agentId}`);
            
            // Render visual display immediately
            renderAttachedPrompts(agentId);
            
            // Show visual confirmation
            const agentName = getAgentName(agentId);
            const promptNames = prompts.map(p => p.name).join(', ');
            console.log(`[AgentInput] ✓ Prompts assigned to ${agentName}: ${promptNames}`);
            
            return true;
        } catch (error) {
            console.error(`[AgentInput] Failed to assign prompts to Agent-${agentId}:`, error);
            throw error;
        }
    }

    // Public API
    return {
        initState,
        expand,
        collapse,
        toggleFeedback,
        sendFeedback,
        insertQuickFeedback,
        toggleTranscription,
        toggleAutoScroll,
        showPromptLibrary,
        assignPrompts,
        removePrompt,
        clearPrompts,
        getPendingPrompts,
        renderAttachedPrompts,
        // Drag & drop handlers
        handlePromptDragStart,
        handlePromptDragOver,
        handlePromptDrop,
        handlePromptDragEnd,
        showFileDialog,
        setupHandlers,
        cleanupHandlers,
        // File attachment functions
        attachFiles,
        clearFiles,
        getFiles,
        getValue,
        setValue
    };
})();

// Expose to window for HTML onclick handlers
window.AgentInput = AgentInput;
