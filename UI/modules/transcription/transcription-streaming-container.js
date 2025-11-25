/**
 * TRANSCRIPTION STREAMING CONTAINER CONTROLLER
 * 
 * Purpose: Real-time streaming transcript display matching V7_MustCare pattern
 * Features:
 * - Streams transcription in real-time (doesn't auto-insert)
 * - Copy/Insert/Send buttons
 * - Auto-clear toggle
 * - Collapsible
 * - Real-time status indicators
 * 
 * LAST MODIFIED: 2025-11-25
 */

class TranscriptionStreamingController {
    constructor() {
        this.container = null;
        this.textDisplay = null;
        this.statusIndicator = null;
        this.autoClearEnabled = true;
        this.currentTranscript = '';
        this.isCollapsed = false;
        
        console.log('[TRANSCRIPTION STREAMING] Controller initialized');
    }

    /**
     * Initialize the streaming container
     */
    init() {
        console.log('[TRANSCRIPTION STREAMING] Initializing...');
        
        // Get DOM elements
        this.container = document.getElementById('ai-transcription-container');
        this.textDisplay = document.getElementById('ai-transcription-text');
        this.statusIndicator = document.getElementById('ai-transcription-status');
        
        if (!this.container || !this.textDisplay) {
            console.warn('[TRANSCRIPTION STREAMING] Container elements not found');
            return false;
        }
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load settings
        this.loadSettings();
        
        console.log('[TRANSCRIPTION STREAMING] Initialized successfully');
        return true;
    }

    /**
     * Setup event listeners for buttons
     */
    setupEventListeners() {
        // Copy button
        const copyBtn = document.getElementById('ai-transcription-copy-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.copyTranscript());
        }
        
        // Insert button
        const insertBtn = document.getElementById('ai-transcription-insert-btn');
        if (insertBtn) {
            insertBtn.addEventListener('click', () => this.insertTranscript());
        }
        
        // Send button
        const sendBtn = document.getElementById('ai-transcription-send-btn');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendTranscript());
        }
        
        // Auto-clear toggle
        const autoClearToggle = document.getElementById('ai-transcription-autoclear-toggle');
        if (autoClearToggle) {
            autoClearToggle.addEventListener('click', () => this.toggleAutoClear());
        }
        
        // Clear button
        const clearBtn = document.getElementById('ai-transcription-clear-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearTranscript());
        }
        
        // Collapse button
        const collapseBtn = document.getElementById('ai-transcription-collapse-btn');
        if (collapseBtn) {
            collapseBtn.addEventListener('click', () => this.toggleCollapse());
        }
    }

    /**
     * Show the container
     */
    show() {
        if (this.container) {
            this.container.classList.remove('hidden');
            this.container.classList.add('show');
            console.log('[TRANSCRIPTION STREAMING] Container shown');
        }
    }

    /**
     * Hide the container
     */
    hide() {
        if (this.container) {
            this.container.classList.add('hidden');
            this.container.classList.remove('show');
            console.log('[TRANSCRIPTION STREAMING] Container hidden');
        }
    }

    /**
     * Toggle collapse state
     */
    toggleCollapse() {
        this.isCollapsed = !this.isCollapsed;
        
        if (this.container) {
            this.container.classList.toggle('collapsed', this.isCollapsed);
        }
        
        // Update collapse button icon
        const collapseBtn = document.getElementById('ai-transcription-collapse-btn');
        if (collapseBtn) {
            const icon = collapseBtn.querySelector('i');
            if (icon) {
                icon.className = this.isCollapsed ? 'fas fa-chevron-up' : 'fas fa-chevron-down';
            }
        }
        
        console.log(`[TRANSCRIPTION STREAMING] Container ${this.isCollapsed ? 'collapsed' : 'expanded'}`);
    }

    /**
     * Update status indicator
     * @param {string} state - 'ready' | 'recording' | 'processing'
     * @param {string} message - Status message
     */
    updateStatus(state, message = '') {
        if (!this.statusIndicator) return;
        
        // Remove all state classes
        this.statusIndicator.classList.remove('recording', 'processing');
        
        // Add new state class
        if (state === 'recording' || state === 'processing') {
            this.statusIndicator.classList.add(state);
        }
        
        // Update icon and text
        const icon = this.statusIndicator.querySelector('i');
        const text = message || this.getDefaultStatusText(state);
        
        if (icon) {
            icon.className = this.getStatusIcon(state);
        }
        
        // Update text node (preserve icon)
        const textNode = Array.from(this.statusIndicator.childNodes)
            .find(node => node.nodeType === Node.TEXT_NODE);
        
        if (textNode) {
            textNode.textContent = ' ' + text;
        } else {
            this.statusIndicator.appendChild(document.createTextNode(' ' + text));
        }
    }

    /**
     * Get status icon class
     */
    getStatusIcon(state) {
        const icons = {
            'ready': 'fas fa-circle',
            'recording': 'fas fa-circle',
            'processing': 'fas fa-spinner'
        };
        return icons[state] || 'fas fa-circle';
    }

    /**
     * Get default status text
     */
    getDefaultStatusText(state) {
        const texts = {
            'ready': 'Ready',
            'recording': 'Recording',
            'processing': 'Processing'
        };
        return texts[state] || 'Ready';
    }

    /**
     * Stream transcript text (called by STT module)
     * @param {string} text - Text to append
     * @param {boolean} isFinal - Is this final or interim result
     * @param {number} confidence - Confidence score (0-1)
     */
    streamText(text, isFinal = false, confidence = null) {
        if (!this.textDisplay) return;
        
        // Remove placeholder if present
        const placeholder = this.textDisplay.querySelector('.ai-transcription-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        
        if (isFinal) {
            // Final transcript - append permanently
            this.currentTranscript += text + ' ';
            
            // Create final text element
            const span = document.createElement('span');
            span.className = 'ai-transcript-final';
            span.textContent = text + ' ';
            
            // Add confidence indicator if available
            if (confidence !== null) {
                const confidenceBadge = document.createElement('span');
                confidenceBadge.className = `ai-transcript-confidence ${this.getConfidenceLevel(confidence)}`;
                confidenceBadge.textContent = `${Math.round(confidence * 100)}%`;
                span.appendChild(confidenceBadge);
            }
            
            this.textDisplay.appendChild(span);
            
            // Remove any interim text
            const interimElements = this.textDisplay.querySelectorAll('.ai-transcript-interim');
            interimElements.forEach(el => el.remove());
        } else {
            // Interim transcript - show but don't commit
            // Remove previous interim
            const oldInterim = this.textDisplay.querySelector('.ai-transcript-interim');
            if (oldInterim) {
                oldInterim.remove();
            }
            
            // Add new interim
            const span = document.createElement('span');
            span.className = 'ai-transcript-interim';
            span.textContent = text + ' ';
            this.textDisplay.appendChild(span);
        }
        
        // Auto-scroll to bottom
        this.textDisplay.scrollTop = this.textDisplay.scrollHeight;
    }

    /**
     * Get confidence level class
     */
    getConfidenceLevel(confidence) {
        if (confidence >= 0.8) return 'high';
        if (confidence >= 0.5) return 'medium';
        return 'low';
    }

    /**
     * Copy transcript to clipboard
     */
    copyTranscript() {
        if (!this.currentTranscript) {
            console.warn('[TRANSCRIPTION STREAMING] No transcript to copy');
            return;
        }
        
        navigator.clipboard.writeText(this.currentTranscript.trim())
            .then(() => {
                console.log('[TRANSCRIPTION STREAMING] Transcript copied to clipboard');
                this.showToast('Transcript copied to clipboard', 'success');
            })
            .catch(err => {
                console.error('[TRANSCRIPTION STREAMING] Failed to copy:', err);
                this.showToast('Failed to copy transcript', 'error');
            });
    }

    /**
     * Insert transcript into chat input (doesn't send)
     */
    insertTranscript() {
        if (!this.currentTranscript) {
            console.warn('[TRANSCRIPTION STREAMING] No transcript to insert');
            return;
        }
        
        const chatInput = document.getElementById('ai-chat-input');
        if (!chatInput) {
            console.error('[TRANSCRIPTION STREAMING] Chat input not found');
            return;
        }
        
        // Append to existing text
        const currentValue = chatInput.value;
        const separator = currentValue && !currentValue.endsWith('\n') ? '\n' : '';
        chatInput.value = currentValue + separator + this.currentTranscript.trim();
        
        // Trigger input event for auto-resize
        chatInput.dispatchEvent(new Event('input', { bubbles: true }));
        
        // Focus input
        chatInput.focus();
        
        console.log('[TRANSCRIPTION STREAMING] Transcript inserted into chat input');
        this.showToast('Transcript inserted', 'success');
        
        // Auto-clear if enabled
        if (this.autoClearEnabled) {
            this.clearTranscript();
        }
    }

    /**
     * Insert transcript and send message
     */
    sendTranscript() {
        if (!this.currentTranscript) {
            console.warn('[TRANSCRIPTION STREAMING] No transcript to send');
            return;
        }
        
        // Insert transcript
        this.insertTranscript();
        
        // Trigger send button
        setTimeout(() => {
            const sendBtn = document.getElementById('ai-chat-send-btn');
            if (sendBtn) {
                sendBtn.click();
                console.log('[TRANSCRIPTION STREAMING] Transcript sent');
            }
        }, 100);
    }

    /**
     * Toggle auto-clear setting
     */
    toggleAutoClear() {
        this.autoClearEnabled = !this.autoClearEnabled;
        
        const toggle = document.getElementById('ai-transcription-autoclear-toggle');
        if (toggle) {
            toggle.setAttribute('data-enabled', this.autoClearEnabled.toString());
            
            const icon = toggle.querySelector('i');
            if (icon) {
                icon.className = this.autoClearEnabled ? 'fas fa-toggle-on' : 'fas fa-toggle-off';
            }
            
            const title = this.autoClearEnabled 
                ? 'Auto-clear after insert/send (ON)' 
                : 'Auto-clear after insert/send (OFF)';
            toggle.setAttribute('title', title);
        }
        
        // Save setting
        this.saveSettings();
        
        console.log(`[TRANSCRIPTION STREAMING] Auto-clear ${this.autoClearEnabled ? 'enabled' : 'disabled'}`);
    }

    /**
     * Clear transcript
     */
    clearTranscript() {
        this.currentTranscript = '';
        
        if (this.textDisplay) {
            this.textDisplay.innerHTML = `
                <div class="ai-transcription-placeholder">
                    <i class="fas fa-microphone-slash"></i>
                    <p>Click the microphone button and start speaking to begin transcription</p>
                </div>
            `;
        }
        
        console.log('[TRANSCRIPTION STREAMING] Transcript cleared');
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        // You can implement a toast notification system here
        // For now, just console log
        console.log(`[TRANSCRIPTION STREAMING] Toast (${type}): ${message}`);
    }

    /**
     * Save settings to localStorage
     */
    saveSettings() {
        const settings = {
            autoClearEnabled: this.autoClearEnabled,
            isCollapsed: this.isCollapsed
        };
        
        localStorage.setItem('ai-transcription-streaming-settings', JSON.stringify(settings));
    }

    /**
     * Load settings from localStorage
     */
    loadSettings() {
        const savedSettings = localStorage.getItem('ai-transcription-streaming-settings');
        if (!savedSettings) return;
        
        try {
            const settings = JSON.parse(savedSettings);
            
            if (typeof settings.autoClearEnabled === 'boolean') {
                this.autoClearEnabled = settings.autoClearEnabled;
                const toggle = document.getElementById('ai-transcription-autoclear-toggle');
                if (toggle) {
                    toggle.setAttribute('data-enabled', this.autoClearEnabled.toString());
                }
            }
            
            if (typeof settings.isCollapsed === 'boolean' && settings.isCollapsed) {
                this.toggleCollapse();
            }
            
            console.log('[TRANSCRIPTION STREAMING] Settings loaded');
        } catch (error) {
            console.error('[TRANSCRIPTION STREAMING] Failed to load settings:', error);
        }
    }

    /**
     * Get current transcript text
     */
    getTranscript() {
        return this.currentTranscript.trim();
    }

    /**
     * Check if container is visible
     */
    isVisible() {
        return this.container && !this.container.classList.contains('hidden');
    }
}

// Export as singleton
window.TranscriptionStreaming = new TranscriptionStreamingController();

console.log('[TRANSCRIPTION STREAMING] Exported to window.TranscriptionStreaming');
