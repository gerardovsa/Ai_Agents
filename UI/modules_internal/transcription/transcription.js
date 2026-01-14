/**
 * Voice Transcription Module - Modern Framework Edition
 * Framework: ModuleLoaderV4
 * Pattern: Composition-based (no inheritance)
 * Version: 2.0.0 - Aligned with Modern Module Loading Framework
 * 
 * Features:
 * - Speech-to-Text (STT) with Whisper backend
 * - Text-to-Speech (TTS) with Web Speech API
 * - Real-time streaming transcription
 * - System audio capture (desktop/tab audio)
 * - Microphone fallback
 * - Sidebar integration for recording controls
 * 
 * Dependencies:
 * - SharedTranscriptionState (transcription-sidebar.js)
 * - STTModule (stt-module.js)
 * - TTSModule (tts-module.js)
 */

export default {
    // ==================== STATE ====================
    state: {
        // Recording state
        isRecording: false,
        currentAudioSource: null, // 'system' or 'microphone'
        recordingSource: null, // 'sidebar' or 'chat'

        // Transcription state
        currentTranscript: '',
        interimTranscript: '',
        finalTranscript: '',
        confidence: 0,

        // TTS state
        isSpeaking: false,
        currentVoice: null,
        availableVoices: [],

        // UI state
        sidebarVisible: false,
        streamingContainerVisible: false,
        autoClearEnabled: false,

        // Modules (loaded dynamically)
        sharedState: null,
        sttModule: null,
        ttsModule: null,

        // Settings
        settings: {
            audioSource: 'auto', // 'auto', 'system', 'microphone'
            sampleRate: 16000,
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            voiceName: null,
            rate: 1.0,
            pitch: 1.0,
            volume: 1.0
        }
    },

    // ==================== LIFECYCLE: SIDEBAR ====================

    /**
     * Called when sidebar loads
     * Replaces: initialize() from BaseModule pattern
     * @param {Object} utilities - Injected utilities { dom, api, storage, events, log }
     */
    async onSidebarLoad(utilities) {
        // Inject utilities explicitly
        Object.assign(this, utilities);

        this.log.info('Transcription sidebar loading...');

        // Get sidebar container
        this.sidebarContainer = this.dom.getContainer();

        // NOTE: HTML and JS files are loaded automatically by ModuleLoaderV4 via manifest.json
        // The framework injects transcription-sidebar.html and loads transcription-sidebar.js
        // which creates window.TranscriptionSidebar singleton

        // Wait for TranscriptionSidebar to be available (loaded by framework)
        await this.waitForTranscriptionSidebar();

        // Load saved settings
        await this.loadSettings();

        // Load advanced settings via TranscriptionSidebar controller
        if (window.TranscriptionSidebar) {
            window.TranscriptionSidebar.loadSettings();
        }

        // Initialize shared transcription state
        await this.initializeSharedState();

        // Subscribe to global events
        this.subscribeToEvents();

        this.state.sidebarVisible = true;
        this.log.info('Transcription sidebar loaded successfully with advanced features');
    },

    /**
     * Called when sidebar is unloaded
     * Replaces: cleanup() from BaseModule pattern
     * @param {Object} utilities - Injected utilities
     */
    onUnload(utilities) {
        Object.assign(this, utilities);
        this.log.info('Transcription module unloading...');

        // Stop any active recording
        if (this.state.isRecording) {
            this.stopRecording();
        }

        // Stop any active TTS
        if (this.state.isSpeaking) {
            this.stopSpeaking();
        }

        // Save settings
        this.saveSettings();

        // Framework automatically cleans up tracked event listeners
        this.log.info('Transcription module unloaded successfully');
    },

    // ==================== INITIALIZATION ====================

    /**
     * Wait for TranscriptionSidebar to be loaded by framework
     */
    async waitForTranscriptionSidebar() {
        const maxAttempts = 50; // 5 seconds max wait
        let attempts = 0;

        while (!window.TranscriptionSidebar && attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }

        if (window.TranscriptionSidebar) {
            this.log.info('TranscriptionSidebar controller ready');
        } else {
            this.log.warn('TranscriptionSidebar controller not found after 5 seconds');
        }
    },

    /**
     * Initialize SharedTranscriptionState singleton
     * Uses existing global state if available
     */
    async initializeSharedState() {
        try {
            // Check if SharedTranscriptionState already exists (loaded by sidebar.js)
            if (window.SharedTranscriptionState) {
                this.state.sharedState = window.SharedTranscriptionState;
                this.log.info('Using existing SharedTranscriptionState');
            } else {
                // Load transcription-sidebar.js dynamically
                await this.loadScript('modules_internal/transcription/transcription-sidebar.js');
                this.state.sharedState = window.SharedTranscriptionState;
                this.log.info('SharedTranscriptionState initialized');
            }

            // Register callbacks with shared state
            this.state.sharedState.on('onStart', () => {
                this.state.isRecording = true;
            });

            this.state.sharedState.on('onStop', () => {
                this.state.isRecording = false;
            });

            this.state.sharedState.on('onTranscript', (transcript, isFinal, confidence) => {
                this.handleTranscript(transcript, isFinal, confidence);
            });

            this.state.sharedState.on('onError', (error) => {
                this.handleError(error);
            });

        } catch (error) {
            this.log.error('Failed to initialize SharedTranscriptionState:', error);
            throw error;
        }
    },



    /**
     * Load TTS voices
     */
    async loadTTSVoices() {
        try {
            const voices = window.speechSynthesis.getVoices();
            this.state.availableVoices = voices;

            // Set default voice if not already set
            if (!this.state.settings.voiceName && voices.length > 0) {
                this.state.settings.voiceName = voices[0].name;
            }

            this.log.info(`Loaded ${voices.length} TTS voices`);
        } catch (error) {
            this.log.error('Failed to load TTS voices:', error);
        }
    },

    // ==================== EVENT LISTENERS ====================

    setupSidebarListeners() {
        // STT controls
        this.dom.on(this.sidebarContainer, 'click', '[data-action="start-recording"]', () => {
            this.startRecording();
        });

        this.dom.on(this.sidebarContainer, 'click', '[data-action="stop-recording"]', () => {
            this.stopRecording();
        });

        this.dom.on(this.sidebarContainer, 'click', '[data-action="copy-transcript"]', () => {
            this.copyTranscript();
        });

        this.dom.on(this.sidebarContainer, 'click', '[data-action="clear-transcript"]', () => {
            this.clearTranscript();
        });

        // TTS controls
        this.dom.on(this.sidebarContainer, 'click', '[data-action="speak-text"]', () => {
            const text = this.sidebarContainer.querySelector('[data-tts-input]')?.value || '';
            this.speakText(text);
        });

        this.dom.on(this.sidebarContainer, 'click', '[data-action="stop-speaking"]', () => {
            this.stopSpeaking();
        });

        // Settings
        this.dom.on(this.sidebarContainer, 'change', '[data-setting="audio-source"]', (e) => {
            this.state.settings.audioSource = e.target.value;
            this.saveSettings();
        });

        this.dom.on(this.sidebarContainer, 'change', '[data-setting="voice"]', (e) => {
            this.state.settings.voiceName = e.target.value;
            this.saveSettings();
        });

        this.dom.on(this.sidebarContainer, 'input', '[data-setting="rate"]', (e) => {
            this.state.settings.rate = parseFloat(e.target.value);
            this.updateSettingsDisplay();
        });

        this.dom.on(this.sidebarContainer, 'input', '[data-setting="pitch"]', (e) => {
            this.state.settings.pitch = parseFloat(e.target.value);
            this.updateSettingsDisplay();
        });

        this.dom.on(this.sidebarContainer, 'input', '[data-setting="volume"]', (e) => {
            this.state.settings.volume = parseFloat(e.target.value);
            this.updateSettingsDisplay();
        });

        // Auto-clear toggle
        this.dom.on(this.sidebarContainer, 'change', '[data-setting="auto-clear"]', (e) => {
            this.state.autoClearEnabled = e.target.checked;
            this.saveSettings();
        });
    },

    subscribeToEvents() {
        // Listen for transcript events from chat interface
        this.events.on('chat:message-sent', () => {
            if (this.state.autoClearEnabled) {
                this.clearTranscript();
            }
        });

        // Listen for voice availability changes
        if ('speechSynthesis' in window) {
            speechSynthesis.addEventListener('voiceschanged', () => {
                this.loadTTSVoices();
                this.renderSidebar();
            });
        }
    },

    // ==================== STT ACTIONS ====================

    async startRecording() {
        try {
            this.log.info('Starting transcription recording...');

            if (!this.state.sharedState) {
                throw new Error('SharedTranscriptionState not initialized');
            }

            await this.state.sharedState.startRecording('sidebar');

            this.state.isRecording = true;
            this.renderSidebar();

            this.log.info('Recording started successfully');
        } catch (error) {
            this.log.error('Failed to start recording:', error);
            this.handleError(error);
        }
    },

    stopRecording() {
        try {
            this.log.info('Stopping transcription recording...');

            if (!this.state.sharedState) {
                throw new Error('SharedTranscriptionState not initialized');
            }

            this.state.sharedState.stopRecording();

            this.state.isRecording = false;
            this.renderSidebar();

            this.log.info('Recording stopped successfully');
        } catch (error) {
            this.log.error('Failed to stop recording:', error);
            this.handleError(error);
        }
    },

    handleTranscript(transcript, isFinal, confidence) {
        if (isFinal) {
            this.state.finalTranscript += transcript + ' ';
            this.state.interimTranscript = '';
            this.log.info(`Final transcript (confidence: ${(confidence * 100).toFixed(1)}%): ${transcript}`);
        } else {
            this.state.interimTranscript = transcript;
        }

        this.state.currentTranscript = this.state.finalTranscript + this.state.interimTranscript;
        this.state.confidence = confidence;

        // Update transcript display
        this.updateTranscriptDisplay();

        // Emit event for other components
        this.events.emit('transcription:updated', {
            transcript: this.state.currentTranscript,
            isFinal,
            confidence
        });
    },

    copyTranscript() {
        const text = this.state.currentTranscript.trim();
        if (!text) {
            this.log.warn('No transcript to copy');
            return;
        }

        navigator.clipboard.writeText(text)
            .then(() => {
                this.log.info('Transcript copied to clipboard');
                this.showNotification('Copied to clipboard!', 'success');
            })
            .catch(error => {
                this.log.error('Failed to copy transcript:', error);
                this.showNotification('Failed to copy', 'error');
            });
    },

    clearTranscript() {
        this.state.currentTranscript = '';
        this.state.finalTranscript = '';
        this.state.interimTranscript = '';
        this.state.confidence = 0;

        this.updateTranscriptDisplay();
        this.log.info('Transcript cleared');
    },

    // ==================== TTS ACTIONS ====================

    speakText(text) {
        if (!text || text.trim().length === 0) {
            this.log.warn('No text to speak');
            return;
        }

        try {
            // Stop any current speech
            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);

            // Apply settings
            utterance.rate = this.state.settings.rate;
            utterance.pitch = this.state.settings.pitch;
            utterance.volume = this.state.settings.volume;

            // Set voice
            const selectedVoice = this.state.availableVoices.find(v => v.name === this.state.settings.voiceName);
            if (selectedVoice) {
                utterance.voice = selectedVoice;
            }

            // Event handlers
            utterance.onstart = () => {
                this.state.isSpeaking = true;
                this.renderSidebar();
                this.log.info('TTS started');
            };

            utterance.onend = () => {
                this.state.isSpeaking = false;
                this.renderSidebar();
                this.log.info('TTS ended');
            };

            utterance.onerror = (error) => {
                this.log.error('TTS error:', error);
                this.state.isSpeaking = false;
                this.renderSidebar();
            };

            // Speak
            window.speechSynthesis.speak(utterance);

        } catch (error) {
            this.log.error('Failed to speak text:', error);
            this.handleError(error);
        }
    },

    stopSpeaking() {
        window.speechSynthesis.cancel();
        this.state.isSpeaking = false;
        this.renderSidebar();
        this.log.info('TTS stopped');
    },

    // ==================== UI RENDERING ====================

    renderSidebar() {
        if (!this.sidebarContainer) {
            this.log.warn('Sidebar container not found');
            return;
        }

        this.sidebarContainer.innerHTML = this.generateSidebarHTML();
    },

    generateSidebarHTML() {
        return `
            <div class="transcription-sidebar">
                ${this.renderHeader()}
                ${this.renderSTTSection()}
                ${this.renderTTSSection()}
                ${this.renderSettings()}
            </div>
        `;
    },

    renderHeader() {
        return `
            <div class="sidebar-header">
                <div class="header-title">
                    <i class="fas fa-microphone"></i>
                    <h3>Voice Transcription</h3>
                </div>
            </div>
        `;
    },

    renderSTTSection() {
        const isRecording = this.state.isRecording;
        const hasTranscript = this.state.currentTranscript.trim().length > 0;

        return `
            <div class="sidebar-section">
                <div class="section-title">
                    <i class="fas fa-microphone-alt"></i>
                    <h4>Speech-to-Text</h4>
                </div>
                
                <div class="recording-controls">
                    ${isRecording ? `
                        <button 
                            data-action="stop-recording" 
                            class="btn-recording btn-recording-active"
                        >
                            <i class="fas fa-stop"></i>
                            Stop Recording
                        </button>
                    ` : `
                        <button 
                            data-action="start-recording" 
                            class="btn-recording"
                        >
                            <i class="fas fa-microphone"></i>
                            Start Recording
                        </button>
                    `}
                </div>
                
                ${isRecording ? `
                    <div class="recording-indicator">
                        <span class="recording-dot"></span>
                        Recording... (Source: ${this.state.currentAudioSource || 'waiting'})
                    </div>
                ` : ''}
                
                <div class="transcript-display">
                    <div class="transcript-header">
                        <span>Transcript</span>
                        ${this.state.confidence > 0 ? `
                            <span class="confidence-badge">
                                ${(this.state.confidence * 100).toFixed(1)}%
                            </span>
                        ` : ''}
                    </div>
                    <div class="transcript-text" data-transcript-display>
                        ${this.state.currentTranscript || '<span class="transcript-placeholder">Transcript will appear here...</span>'}
                    </div>
                    ${hasTranscript ? `
                        <div class="transcript-actions">
                            <button data-action="copy-transcript" class="btn-icon" title="Copy to clipboard">
                                <i class="fas fa-copy"></i>
                            </button>
                            <button data-action="clear-transcript" class="btn-icon" title="Clear transcript">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    },

    renderTTSSection() {
        const isSpeaking = this.state.isSpeaking;

        return `
            <div class="sidebar-section">
                <div class="section-title">
                    <i class="fas fa-volume-up"></i>
                    <h4>Text-to-Speech</h4>
                </div>
                
                <div class="tts-input-area">
                    <textarea 
                        data-tts-input 
                        placeholder="Enter text to speak..."
                        rows="4"
                        ${isSpeaking ? 'disabled' : ''}
                    ></textarea>
                </div>
                
                <div class="tts-controls">
                    ${isSpeaking ? `
                        <button data-action="stop-speaking" class="btn-tts btn-tts-active">
                            <i class="fas fa-stop"></i>
                            Stop Speaking
                        </button>
                    ` : `
                        <button data-action="speak-text" class="btn-tts">
                            <i class="fas fa-play"></i>
                            Speak
                        </button>
                    `}
                </div>
                
                <div class="tts-voice-selector">
                    <label>Voice:</label>
                    <select data-setting="voice">
                        ${this.state.availableVoices.map(voice => `
                            <option 
                                value="${this.escapeHtml(voice.name)}"
                                ${voice.name === this.state.settings.voiceName ? 'selected' : ''}
                            >
                                ${this.escapeHtml(voice.name)} (${voice.lang})
                            </option>
                        `).join('')}
                    </select>
                </div>
            </div>
        `;
    },

    renderSettings() {
        return `
            <div class="sidebar-section settings-section">
                <div class="section-title">
                    <i class="fas fa-cog"></i>
                    <h4>Settings</h4>
                </div>
                
                <div class="setting-group">
                    <label>Audio Source:</label>
                    <select data-setting="audio-source">
                        <option value="auto" ${this.state.settings.audioSource === 'auto' ? 'selected' : ''}>Auto (System → Mic)</option>
                        <option value="system" ${this.state.settings.audioSource === 'system' ? 'selected' : ''}>System Audio Only</option>
                        <option value="microphone" ${this.state.settings.audioSource === 'microphone' ? 'selected' : ''}>Microphone Only</option>
                    </select>
                </div>
                
                <div class="setting-group">
                    <label>Speech Rate: <span data-rate-value>${this.state.settings.rate.toFixed(1)}</span></label>
                    <input 
                        type="range" 
                        data-setting="rate" 
                        min="0.5" 
                        max="2.0" 
                        step="0.1" 
                        value="${this.state.settings.rate}"
                    />
                </div>
                
                <div class="setting-group">
                    <label>Pitch: <span data-pitch-value>${this.state.settings.pitch.toFixed(1)}</span></label>
                    <input 
                        type="range" 
                        data-setting="pitch" 
                        min="0.5" 
                        max="2.0" 
                        step="0.1" 
                        value="${this.state.settings.pitch}"
                    />
                </div>
                
                <div class="setting-group">
                    <label>Volume: <span data-volume-value>${this.state.settings.volume.toFixed(1)}</span></label>
                    <input 
                        type="range" 
                        data-setting="volume" 
                        min="0" 
                        max="1" 
                        step="0.1" 
                        value="${this.state.settings.volume}"
                    />
                </div>
                
                <div class="setting-group">
                    <label class="checkbox-label">
                        <input 
                            type="checkbox" 
                            data-setting="auto-clear"
                            ${this.state.autoClearEnabled ? 'checked' : ''}
                        />
                        Auto-clear transcript after insert
                    </label>
                </div>
            </div>
        `;
    },

    updateTranscriptDisplay() {
        const displayEl = this.sidebarContainer?.querySelector('[data-transcript-display]');
        if (displayEl) {
            if (this.state.currentTranscript) {
                displayEl.innerHTML = this.escapeHtml(this.state.currentTranscript);
            } else {
                displayEl.innerHTML = '<span class="transcript-placeholder">Transcript will appear here...</span>';
            }
        }
    },

    updateSettingsDisplay() {
        const rateDisplay = this.sidebarContainer?.querySelector('[data-rate-value]');
        if (rateDisplay) {
            rateDisplay.textContent = this.state.settings.rate.toFixed(1);
        }

        const pitchDisplay = this.sidebarContainer?.querySelector('[data-pitch-value]');
        if (pitchDisplay) {
            pitchDisplay.textContent = this.state.settings.pitch.toFixed(1);
        }

        const volumeDisplay = this.sidebarContainer?.querySelector('[data-volume-value]');
        if (volumeDisplay) {
            volumeDisplay.textContent = this.state.settings.volume.toFixed(1);
        }
    },

    // ==================== STORAGE ====================

    async loadSettings() {
        try {
            const savedSettings = this.storage.get('transcription_settings');
            if (savedSettings) {
                this.state.settings = { ...this.state.settings, ...savedSettings };
            }

            const autoClear = this.storage.get('transcription_auto_clear');
            if (autoClear !== null) {
                this.state.autoClearEnabled = autoClear;
            }

            this.log.info('Settings loaded');
        } catch (error) {
            this.log.error('Failed to load settings:', error);
        }
    },

    saveSettings() {
        try {
            this.storage.set('transcription_settings', this.state.settings);
            this.storage.set('transcription_auto_clear', this.state.autoClearEnabled);
            this.log.info('Settings saved');
        } catch (error) {
            this.log.error('Failed to save settings:', error);
        }
    },

    // ==================== UTILITIES ====================

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    showNotification(message, type = 'info') {
        // Emit notification event for global notification system
        this.events.emit('notification:show', { message, type });

        // Simple fallback if no notification system exists
        if (console[type]) {
            console[type](`[Transcription] ${message}`);
        }
    },

    handleError(error) {
        this.log.error('Transcription error:', error);
        this.showNotification(error.message || 'An error occurred', 'error');
    },

    async loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
};
