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
        maxPdfSize: 32 * 1024 * 1024,    // 32MB
        maxImageSize: 5 * 1024 * 1024,   // 5MB
        validTypes: [
            'application/pdf',
            'image/png',
            'image/jpeg',
            'image/jpg',
            'image/gif',
            'image/webp'
        ]
    };

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
        console.log(`[AgentInput] Agent-${agentId} prompt library requested`);

        // TODO: Integrate with actual prompt library system
        // Should filter prompts relevant to agent's thread/context
        // For now, show placeholder alert
        alert(`Prompt library for Agent ${agentId}\n\n(Feature coming soon - will show curated prompts)`);
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
            container.classList.add('drag-over');
        };

        handlers[agentId].dragLeave = (e) => {
            e.preventDefault();
            e.stopPropagation();
            container.classList.remove('drag-over');
        };

        handlers[agentId].drop = (e) => {
            e.preventDefault();
            e.stopPropagation();
            container.classList.remove('drag-over');

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
            if (!FILE_CONFIG.validTypes.includes(file.type)) {
                console.warn(`[AgentInput] Invalid file type for agent-${agentId}:`, file.name);
                if (typeof window.showNotification === 'function') {
                    window.showNotification(
                        `Invalid file type: ${file.name}. Only PDF and images are supported.`,
                        'error'
                    );
                }
                continue;
            }

            // Validate file size
            const maxSize = file.type === 'application/pdf' ? FILE_CONFIG.maxPdfSize : FILE_CONFIG.maxImageSize;
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

            const icon = file.type === 'application/pdf' ? 'fa-file-pdf' : 'fa-image';
            const size = (file.size / 1024).toFixed(1);

            chip.innerHTML = `
                <i class="fas ${icon}"></i>
                <span>${file.name} (${size}KB)</span>
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
