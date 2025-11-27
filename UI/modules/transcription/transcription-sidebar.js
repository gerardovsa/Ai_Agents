/**
 * SHARED TRANSCRIPTION STATE MANAGER
 * 
 * Purpose: Global state manager for transcription recording
 * Pattern: Singleton - ensures both chat button and sidebar button control same recording
 * 
 * Usage:
 *   window.SharedTranscriptionState.startRecording() - From any button
 *   window.SharedTranscriptionState.stopRecording() - From any button
 *   window.SharedTranscriptionState.isRecording - Check current state
 */
class SharedTranscriptionState {
    constructor() {
        this.isRecording = false;
        this.browserRecognition = null;
        this.audioRecorder = null;
        this.audioChunks = [];
        this.currentInterimElement = null;
        this.recordingSource = null; // 'chat' or 'sidebar'
        this.callbacks = {
            onStart: [],
            onStop: [],
            onTranscript: [],
            onError: []
        };
        
        console.log('[SHARED STATE] Transcription state manager initialized');
    }
    
    // Register callback functions
    on(event, callback) {
        if (this.callbacks[event]) {
            this.callbacks[event].push(callback);
        }
    }
    
    // Trigger callbacks
    trigger(event, ...args) {
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(cb => cb(...args));
        }
    }
    
    // Start recording (called by either button)
    async startRecording(source = 'sidebar') {
        if (this.isRecording) {
            console.warn('[SHARED STATE] Already recording');
            return;
        }
        
        this.recordingSource = source;
        console.log(`[SHARED STATE] Starting recording from ${source}...`);
        
        try {
            // ✅ REMOVED: MediaRecorder (was causing audio-capture error)
            // Browser Web Speech API needs exclusive microphone access
            // MediaRecorder was blocking browserRecognition from starting
            
            // Reset audio chunks (no longer using MediaRecorder)
            this.audioChunks = [];
            this.audioRecorder = null;
            
            // Start browser speech recognition
            if (!this.browserRecognition && 'webkitSpeechRecognition' in window) {
                this.browserRecognition = new webkitSpeechRecognition();
                this.browserRecognition.continuous = true;
                this.browserRecognition.interimResults = true;
                this.browserRecognition.lang = 'en-US';
                
                this.browserRecognition.onresult = (event) => {
                    // ✅ FIX: Extract interim and final text BEFORE triggering event
                    let interimTranscript = '';
                    let finalTranscript = '';
                    let avgConfidence = 0;
                    let confidenceCount = 0;
                    
                    for (let i = event.resultIndex; i < event.results.length; i++) {
                        const result = event.results[i];
                        const transcript = result[0].transcript;
                        
                        if (result.isFinal) {
                            finalTranscript += transcript + ' ';
                            avgConfidence += result[0].confidence;
                            confidenceCount++;
                        } else {
                            interimTranscript += transcript;
                        }
                    }
                    
                    const confidence = confidenceCount > 0 ? avgConfidence / confidenceCount : 0;
                    
                    console.log('[SHARED STATE] Browser STT result:', {
                        interim: interimTranscript.substring(0, 50),
                        final: finalTranscript.substring(0, 50),
                        confidence: confidence.toFixed(2)
                    });
                    
                    this.trigger('onTranscript', {
                        interim: interimTranscript,
                        final: finalTranscript,
                        confidence: confidence
                    }, this.recordingSource);
                };
                
                this.browserRecognition.onerror = (event) => {
                    console.warn('[SHARED STATE] Recognition error:', event.error);
                    
                    // Non-fatal errors
                    if (event.error === 'no-speech') {
                        console.log('[SHARED STATE] No speech detected, continuing...');
                        return;
                    }
                    
                    // ✅ FIXED: audio-capture is now fatal (no MediaRecorder fallback)
                    // This error means Browser STT can't access microphone
                    console.error('[SHARED STATE] Fatal STT error:', event.error);
                    this.trigger('onError', event.error);
                };
                
                this.browserRecognition.onend = () => {
                    console.log('[SHARED STATE] Recognition ended');
                    if (this.isRecording) {
                        // Restart if still supposed to be recording
                        try {
                            this.browserRecognition.start();
                        } catch (e) {
                            console.error('[SHARED STATE] Failed to restart recognition:', e);
                        }
                    }
                };
            }
            
            if (this.browserRecognition) {
                try {
                    this.browserRecognition.start();
                    console.log('[SHARED STATE] Browser recognition started');
                } catch (err) {
                    console.warn('[SHARED STATE] Browser STT failed (non-fatal, Whisper will handle):', err);
                    // Continue recording with Whisper only
                }
            }
            
            this.isRecording = true;
            this.trigger('onStart', this.recordingSource);
            console.log(`[SHARED STATE] ✅ Recording started successfully from ${this.recordingSource}`);
            
        } catch (error) {
            console.error('[SHARED STATE] Failed to start recording:', error);
            this.trigger('onError', error.message);
            throw error;
        }
    }
    
    // Stop recording (called by either button)
    stopRecording() {
        if (!this.isRecording) {
            console.warn('[SHARED STATE] Not recording');
            return;
        }
        
        console.log('[SHARED STATE] Stopping recording...');
        
        // Stop browser recognition
        if (this.browserRecognition) {
            try {
                this.browserRecognition.stop();
                console.log('[SHARED STATE] Browser recognition stopped');
            } catch (e) {
                console.error('[SHARED STATE] Failed to stop recognition:', e);
            }
        }
        
        // ✅ REMOVED: MediaRecorder stop (no longer using it)
        // Trigger onStop manually since we removed MediaRecorder.onstop
        this.trigger('onStop');
        
        this.isRecording = false;
        const source = this.recordingSource;
        this.recordingSource = null;
        console.log(`[SHARED STATE] ✅ Recording stopped (was from ${source})`);
    }
    
    // ✅ REMOVED: getAudioBlob (no longer using MediaRecorder/Whisper)
    // Browser Web Speech API provides transcription directly
    getAudioBlob() {
        console.warn('[SHARED STATE] getAudioBlob called but MediaRecorder removed (Browser STT only)');
        return null;
    }
}

// Create global singleton instance
if (!window.SharedTranscriptionState) {
    window.SharedTranscriptionState = new SharedTranscriptionState();
}

/**
 * TRANSCRIPTION SIDEBAR CONTROLLER
 * 
 * Purpose: Main controller for transcription settings sidebar
 * Pattern: Similar to SynergySidebarController (450px width, tabbed interface)
 * 
 * Dependencies:
 * - stt-module.js (STTModule)
 * - tts-module.js (TTSModule)
 * - transcription-sidebar.html (HTML structure)
 * - transcription-sidebar.css (styling)
 * 
 * Features:
 * - Settings management (STT/TTS configuration)
 * - Transcript collection and export
 * - Status monitoring
 * - Browser support detection
 * 
 * LAST MODIFIED: 2025-11-25
 */

class TranscriptionSidebarController {
    constructor() {
        this.sttModule = null;
        this.ttsModule = null;
        this.recordingStartTime = null;
        this.recordingInterval = null;
        this.statistics = {
            totalChunks: 0,
            totalUtterances: 0,
            totalRecordingTime: 0,
            totalWords: 0
        };
        this.sttTranscripts = [];
        this.ttsTranscripts = [];
        
        // ✅ Use shared state manager
        this.sharedState = window.SharedTranscriptionState;
        this.currentInterimElement = null;
        
        // ✅ Register callbacks for shared state events
        this.sharedState.on('onStart', (source) => this.handleRecordingStart(source));
        this.sharedState.on('onStop', () => this.handleRecordingStop());
        this.sharedState.on('onTranscript', (event, source) => this.handleBrowserTranscript(event, source));
        this.sharedState.on('onError', (error) => this.handleRecordingError(error));
        
        console.log('[TRANSCRIPTION SIDEBAR] Controller initialized with shared state');
    }

    /**
     * Initialize sidebar - load settings, check support, initialize modules
     */
    async init() {
        console.log('[TRANSCRIPTION SIDEBAR] Initializing...');

        // Show auto-detected backend URL hint
        if (window.TranscriptionConfig) {
            const hint = document.getElementById('backend-url-hint');
            const input = document.getElementById('transcription-whisper-endpoint');
            const detectedUrl = window.TranscriptionConfig.getEndpoint('transcribe');
            const config = window.TranscriptionConfig.getConfig();
            const env = config.environment === 'local' ? 'Local (localhost:5001)' : 'Production (Render)';
            
            if (hint) {
                hint.textContent = `${env} (auto-detected): ${detectedUrl}`;
            }
            
            // Set placeholder to show auto-detected URL
            if (input && !input.value) {
                input.placeholder = detectedUrl;
            }
        }

        // Load saved settings
        this.loadSettings();

        // Check browser support
        this.checkBrowserSupport();

        // Initialize STT and TTS modules if available
        this.initializeModules();

        // Setup event listeners
        this.setupEventListeners();

        // Test backend connection
        await this.testBackendConnection();

        console.log('[TRANSCRIPTION SIDEBAR] Initialization complete');
    }

    /**
     * Initialize STT and TTS modules
     */
    initializeModules() {
        console.log('[TRANSCRIPTION SIDEBAR] Initializing modules...');
        console.log('[TRANSCRIPTION SIDEBAR] STTModule available:', typeof STTModule !== 'undefined');
        console.log('[TRANSCRIPTION SIDEBAR] Button exists:', !!document.getElementById('transcription-record-toggle'));
        
        // ✅ NEW: Initialize Web Speech API for instant streaming (parallel to Whisper)
        this.initializeWebSpeechAPI();
        
        // Check if modules are available globally
        if (typeof STTModule !== 'undefined') {
            const settings = this.getSTTSettings();
            console.log('[TRANSCRIPTION SIDEBAR] STT Settings:', settings);
            
            this.sttModule = new STTModule({
                recordButton: 'transcription-record-toggle',
                transcriptDisplay: 'stt-transcript-collection',
                statusIndicator: null, // Use sidebar status instead
                insertTarget: 'ai-chat-input', // Needs to be set to actual chat input ID
                insertMode: settings.insertMode,
                whisperEndpoint: settings.whisperEndpoint,
                apiKey: settings.apiKey || null,
                timeSlice: settings.chunkSize,
                sampleRate: settings.sampleRate,
                
                onStart: () => this.handleSTTStart(),
                onStop: () => this.handleSTTStop(),
                onTranscript: (event) => this.handleSTTTranscript(event),
                onError: (event) => this.handleSTTError(event),
                onChunkSent: () => this.handleSTTChunkSent()
            });
            
            console.log('[TRANSCRIPTION SIDEBAR] STT module initialized:', !!this.sttModule);
        } else {
            console.warn('[TRANSCRIPTION SIDEBAR] STTModule not available');
        }

        if (typeof TTSModule !== 'undefined') {
            const settings = this.getTTSSettings();
            
            this.ttsModule = new TTSModule({
                transcriptContainer: 'tts-transcript-collection',
                statusIndicator: null, // Use sidebar status instead
                voice: settings.voice,
                rate: settings.rate,
                pitch: settings.pitch,
                volume: settings.volume / 100,
                
                onStart: () => this.handleTTSStart(),
                onEnd: () => this.handleTTSEnd(),
                onError: (event) => this.handleTTSError(event)
            });
            
            // Populate voice select
            this.populateVoiceSelect();
            
            console.log('[TRANSCRIPTION SIDEBAR] TTS module initialized');
        } else {
            console.warn('[TRANSCRIPTION SIDEBAR] TTSModule not available');
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Range sliders
        const rateSlider = document.getElementById('transcription-rate');
        if (rateSlider) {
            rateSlider.addEventListener('input', (e) => {
                document.getElementById('transcription-rate-value').textContent = `${e.target.value}x`;
                if (this.ttsModule) {
                    this.ttsModule.setRate(parseFloat(e.target.value));
                }
            });
        }

        const pitchSlider = document.getElementById('transcription-pitch');
        if (pitchSlider) {
            pitchSlider.addEventListener('input', (e) => {
                document.getElementById('transcription-pitch-value').textContent = `${e.target.value}x`;
                if (this.ttsModule) {
                    this.ttsModule.setPitch(parseFloat(e.target.value));
                }
            });
        }

        const volumeSlider = document.getElementById('transcription-volume');
        if (volumeSlider) {
            volumeSlider.addEventListener('input', (e) => {
                document.getElementById('transcription-volume-value').textContent = `${e.target.value}%`;
                if (this.ttsModule) {
                    this.ttsModule.setVolume(parseInt(e.target.value) / 100);
                }
            });
        }

        // Voice select
        const voiceSelect = document.getElementById('transcription-voice-select');
        if (voiceSelect) {
            voiceSelect.addEventListener('change', (e) => {
                if (this.ttsModule) {
                    this.ttsModule.setVoice(parseInt(e.target.value));
                    this.updateVoiceInfo();
                }
            });
        }
    }

    /**
     * Toggle sidebar visibility
     */
    toggleSidebar() {
        const sidebar = document.getElementById('transcription-sidebar');
        if (sidebar) {
            sidebar.classList.toggle('collapsed');
            console.log(`[TRANSCRIPTION SIDEBAR] Sidebar ${sidebar.classList.contains('collapsed') ? 'closed' : 'opened'}`);
        }
    }

    /**
     * Switch tabs (Updated for new tab names: recording, tts, transcripts, settings)
     */
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.transcription-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        
        // Update tab content
        document.querySelectorAll('.transcription-tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}-tab`);
        });

        console.log(`[TRANSCRIPTION SIDEBAR] Switched to tab: ${tabName}`);
    }

    /**
     * ✅ NEW: Initialize Web Speech API for instant interim results
     */
    initializeWebSpeechAPI() {
        // Check browser support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.warn('[TRANSCRIPTION SIDEBAR] Web Speech API not supported');
            return;
        }
        
        this.browserRecognition = new SpeechRecognition();
        this.browserRecognition.continuous = true;
        this.browserRecognition.interimResults = true; // ✅ CRITICAL: Enable streaming
        this.browserRecognition.lang = 'en-US';
        
        // Handle interim and final results
        this.browserRecognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const result = event.results[i];
                const transcript = result[0].transcript;
                
                if (result.isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }
            
            // Send to display handler
            this.handleBrowserTranscript({
                final: finalTranscript,
                interim: interimTranscript,
                confidence: event.results[event.resultIndex]?.[0]?.confidence || 0
            });
        };
        
        this.browserRecognition.onerror = (event) => {
            console.error('[TRANSCRIPTION SIDEBAR] Speech recognition error:', event.error);
            if (event.error === 'audio-capture') {
                console.warn('[TRANSCRIPTION SIDEBAR] Microphone already in use - using Whisper backend only');
            }
            this.browserRecognitionActive = false;
        };
        
        this.browserRecognition.onend = () => {
            console.log('[TRANSCRIPTION SIDEBAR] Browser recognition ended');
            this.browserRecognitionActive = false;
        };
        
        console.log('[TRANSCRIPTION SIDEBAR] Web Speech API initialized');
    }
    
    /**
     * ✅ NEW: Stream transcript to chat input field (for chat button)
     */
    streamToChatInput(final, interim) {
        const chatInput = document.getElementById('ai-chat-input');
        if (!chatInput) {
            console.warn('[TRANSCRIPTION SIDEBAR] Chat input not found');
            return;
        }
        
        // For chat input, only show final results (not interim)
        // This prevents jumpy text updates while typing
        if (final && final.trim()) {
            const currentText = chatInput.value;
            
            // Append final text with space separator if there's existing content
            if (currentText && !currentText.endsWith(' ')) {
                chatInput.value = currentText + ' ' + final.trim();
            } else {
                chatInput.value = currentText + final.trim();
            }
            
            // Auto-resize textarea if it has auto-resize functionality
            if (typeof chatInput.style.height !== 'undefined') {
                chatInput.style.height = 'auto';
                chatInput.style.height = chatInput.scrollHeight + 'px';
            }
            
            // Trigger input event for any listeners
            chatInput.dispatchEvent(new Event('input', { bubbles: true }));
            
            console.log('[TRANSCRIPTION SIDEBAR] Streamed to chat input:', final.trim());
        }
    }
    
    /**
     * ✅ Handle recording start (called by SharedTranscriptionState)
     */
    handleRecordingStart() {
        console.log('[TRANSCRIPTION SIDEBAR] Recording started callback');
        this.handleSTTStart();
    }
    
    /**
     * ✅ Handle recording stop (called by SharedTranscriptionState)
     */
    handleRecordingStop() {
        console.log('[TRANSCRIPTION SIDEBAR] Recording stopped callback');
        this.handleSTTStop();
        
        // Send audio to Whisper
        this.sendAudioToWhisper();
    }
    
    /**
     * ✅ Handle recording error (called by SharedTranscriptionState)
     */
    handleRecordingError(error) {
        console.error('[TRANSCRIPTION SIDEBAR] Recording error:', error);
        
        // ✅ FIX: Stop timer on error (was continuing after error)
        if (this.recordingInterval) {
            clearInterval(this.recordingInterval);
            this.recordingInterval = null;
            console.log('[TRANSCRIPTION SIDEBAR] Timer stopped due to error');
        }
        
        // Reset UI
        const recordBtn = document.getElementById('transcription-record-toggle');
        if (recordBtn) {
            recordBtn.innerHTML = '<i class="fas fa-microphone"></i><span>Start Recording</span>';
            recordBtn.classList.remove('recording');
        }
        
        // Update status
        const stateElement = document.getElementById('stt-state');
        if (stateElement) {
            stateElement.textContent = 'Error';
            stateElement.style.color = '#ef4444';
        }
    }
    
    /**
     * ✅ NEW: Send recorded audio to Whisper backend
     */
    async sendAudioToWhisper() {
        const audioBlob = this.sharedState.getAudioBlob();
        
        if (!audioBlob) {
            console.warn('[TRANSCRIPTION SIDEBAR] No audio to send');
            return;
        }
        
        console.log('[TRANSCRIPTION SIDEBAR] Sending audio to Whisper:', {
            size: audioBlob.size,
            type: audioBlob.type,
            chunks: this.sharedState.audioChunks.length
        });
        
        // Get settings
        const settings = this.getSTTSettings();
        
        // Create FormData
        const formData = new FormData();
        formData.append('file', audioBlob, `recording_${Date.now()}.webm`);
        formData.append('session_id', `sidebar_${Date.now()}`);
        
        try {
            // Send to Whisper backend
            const response = await fetch(settings.whisperEndpoint, {
                method: 'POST',
                headers: settings.apiKey ? { 'X-API-Key': settings.apiKey } : {},
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Whisper API error: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('[TRANSCRIPTION SIDEBAR] Whisper result:', result);
            
            // Add to transcript collection
            if (result.transcript || result.text) {
                this.addSTTTranscript(result.transcript || result.text);
                console.log('[TRANSCRIPTION SIDEBAR] Whisper transcript saved to collection');
            }
            
            // Update statistics
            this.statistics.totalChunks++;
            this.updateStatistics();
            
        } catch (error) {
            console.error('[TRANSCRIPTION SIDEBAR] Failed to send audio to Whisper:', error);
            // Non-fatal - browser transcript is already displayed
        }
    }
    
    /**
     * ✅ NEW: Handle browser speech recognition results (instant streaming)
     * Routes to TranscriptionStreaming component with confidence-based styling
     */
    handleBrowserTranscript(event, source) {
        // Extract data (handle both formats)
        let interim = '';
        let final = '';
        let confidence = 0;
        
        // Format 1: {final, interim, confidence} (from initializeWebSpeechAPI)
        if (event.final !== undefined) {
            interim = event.interim || '';
            final = event.final || '';
            confidence = event.confidence || 0;
        } 
        // Format 2: SpeechRecognitionEvent (from SharedTranscriptionState)
        else if (event.results) {
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const result = event.results[i];
                const transcript = result[0].transcript;
                
                if (result.isFinal) {
                    final += transcript + ' ';
                    confidence = result[0].confidence || 0;
                } else {
                    interim += transcript;
                }
            }
        }
        
        // Route to TranscriptionStreaming component (styled display)
        if (window.TranscriptionStreaming) {
            // Show interim results (gray, italic, pulsing with typing cursor)
            if (interim && interim.trim()) {
                window.TranscriptionStreaming.streamText(
                    interim.trim(), 
                    false,  // isFinal = false
                    'unknown',  // confidence (interim doesn't have it)
                    'browser-stt'  // source
                );
            }
            
            // Show final results (colored by confidence with blue dot)
            if (final && final.trim()) {
                const confidenceLevel = confidence >= 0.8 ? 'high' : 
                                       confidence >= 0.5 ? 'medium' : 
                                       confidence > 0 ? 'low' : 'unknown';
                
                window.TranscriptionStreaming.streamText(
                    final.trim(), 
                    true,  // isFinal = true
                    confidenceLevel,
                    'browser-stt'
                );
            }
        }
        
        // Also route to chat input for backwards compatibility (final text only)
        if (source === 'chat' && final && final.trim()) {
            this.streamToChatInput(final, '');
        }
        
        // Optional: Also show in sidebar live display if not from chat
        if (source !== 'chat') {
            const liveDisplay = document.getElementById('transcription-live-display');
            if (!liveDisplay) return;
            
            // Update interim segment (gray italic)
            if (interim && interim.trim()) {
                if (this.currentInterimElement) {
                    this.currentInterimElement.textContent = interim.trim();
                } else {
                    const interimDiv = document.createElement('div');
                    interimDiv.className = 'interim';
                    interimDiv.style.cssText = `
                        color: #8b949e;
                        font-style: italic;
                        opacity: 0.85;
                        padding: 4px 0;
                    `;
                    interimDiv.textContent = interim.trim();
                    liveDisplay.appendChild(interimDiv);
                    this.currentInterimElement = interimDiv;
                }
                liveDisplay.scrollTop = liveDisplay.scrollHeight;
            }
            
            // Finalize segment
            if (final && final.trim()) {
                if (this.currentInterimElement) {
                    this.currentInterimElement.className = 'final';
                    this.currentInterimElement.style.cssText = `
                        color: var(--text-primary, #c9d1d9);
                        font-style: normal;
                        padding: 4px 0;
                    `;
                    this.currentInterimElement.textContent = final.trim();
                    this.currentInterimElement = null;
                } else {
                    const finalDiv = document.createElement('div');
                    finalDiv.className = 'final';
                    finalDiv.style.cssText = `
                        color: var(--text-primary, #c9d1d9);
                        padding: 4px 0;
                    `;
                    finalDiv.textContent = final.trim();
                    liveDisplay.appendChild(finalDiv);
                }
                liveDisplay.scrollTop = liveDisplay.scrollHeight;
            }
        }
    }
    
    /**
     * Toggle recording (uses SharedTranscriptionState - connected to chat button)
     */
    toggleRecording() {
        console.log('[TRANSCRIPTION SIDEBAR] toggleRecording called', {
            isRecording: this.sharedState.isRecording
        });
        
        if (this.sharedState.isRecording) {
            console.log('[TRANSCRIPTION SIDEBAR] Stopping recording via shared state...');
            this.sharedState.stopRecording();
        } else {
            console.log('[TRANSCRIPTION SIDEBAR] Starting recording via shared state...');
            
            // Clear previous segments
            this.currentInterimElement = null;
            const liveDisplay = document.getElementById('transcription-live-display');
            if (liveDisplay) {
                liveDisplay.innerHTML = '';
            }
            
            this.sharedState.startRecording('sidebar')
                .catch(error => {
                    console.error('[TRANSCRIPTION SIDEBAR] Failed to start:', error);
                    alert('Could not start recording: ' + error.message);
                });
        }
    }

    /**
     * STT event handlers
     */
    handleSTTStart() {
        console.log('[TRANSCRIPTION SIDEBAR] STT recording started');
        
        // Update UI
        const recordBtn = document.getElementById('transcription-record-toggle');
        if (recordBtn) {
            recordBtn.classList.add('recording');
            recordBtn.innerHTML = '<i class="fas fa-stop"></i><span>Stop Recording</span>';
        }

        document.getElementById('stt-state').textContent = 'Recording';
        document.getElementById('stt-state').style.color = '#ef4444';

        // ✅ FIX: Clear any existing timer before starting new one
        if (this.recordingInterval) {
            clearInterval(this.recordingInterval);
            this.recordingInterval = null;
            console.log('[TRANSCRIPTION SIDEBAR] Cleared old timer before starting new one');
        }

        // Start duration timer
        this.recordingStartTime = Date.now();
        this.recordingInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.recordingStartTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            document.getElementById('stt-duration').textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    handleSTTStop() {
        console.log('[TRANSCRIPTION SIDEBAR] STT recording stopped');
        
        // Update UI
        const recordBtn = document.getElementById('transcription-record-toggle');
        if (recordBtn) {
            recordBtn.classList.remove('recording');
            recordBtn.innerHTML = '<i class="fas fa-microphone"></i><span>Start Recording</span>';
        }

        document.getElementById('stt-state').textContent = 'Processing';
        document.getElementById('stt-state').style.color = '#58a6ff';

        // Stop duration timer
        if (this.recordingInterval) {
            clearInterval(this.recordingInterval);
            this.recordingInterval = null;
            
            // Add to total recording time
            const elapsed = Math.floor((Date.now() - this.recordingStartTime) / 1000);
            this.statistics.totalRecordingTime += elapsed;
            this.updateStatistics();
        }
        
        // Add action buttons below live transcript
        const liveDisplay = document.getElementById('transcription-live-display');
        if (liveDisplay && liveDisplay.textContent.trim()) {
            // Check if actions already exist
            if (!liveDisplay.querySelector('.live-transcript-actions')) {
                const actionsDiv = document.createElement('div');
                actionsDiv.className = 'live-transcript-actions';
                actionsDiv.style.cssText = `
                    display: flex;
                    gap: 8px;
                    padding: 12px 0;
                    border-top: 1px solid var(--border-primary, #30363d);
                    margin-top: 12px;
                `;
                
                actionsDiv.innerHTML = `
                    <button onclick="TranscriptionSidebar.sendLiveTranscriptToChat()" 
                            style="flex: 1; padding: 8px 12px; background: #238636; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; display: flex; align-items: center; justify-content: center; gap: 6px;"
                            onmouseover="this.style.background='#2ea043'"
                            onmouseout="this.style.background='#238636'">
                        <i class="fas fa-paper-plane"></i>
                        <span>Send to Chat</span>
                    </button>
                    <button onclick="TranscriptionSidebar.copyLiveTranscript()" 
                            style="padding: 8px 12px; background: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; cursor: pointer; font-size: 13px;"
                            onmouseover="this.style.background='#30363d'"
                            onmouseout="this.style.background='#21262d'"
                            title="Copy">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button onclick="TranscriptionSidebar.clearLiveTranscript()" 
                            style="padding: 8px 12px; background: #21262d; color: #f85149; border: 1px solid #30363d; border-radius: 6px; cursor: pointer; font-size: 13px;"
                            onmouseover="this.style.background='#30363d'"
                            onmouseout="this.style.background='#21262d'"
                            title="Clear">
                        <i class="fas fa-eraser"></i>
                    </button>
                `;
                
                liveDisplay.appendChild(actionsDiv);
                liveDisplay.scrollTop = liveDisplay.scrollHeight;
            }
        }
    }

    handleSTTTranscript(event) {
        console.log('[TRANSCRIPTION SIDEBAR] STT transcript received (Whisper chunk):', event.transcript);
        console.log('[TRANSCRIPTION SIDEBAR] Event data:', event);
        
        // ✅ FILTER: Reject error messages (Whisper backend errors)
        if (event.transcript && event.transcript.includes('[Error:')) {
            console.warn('[TRANSCRIPTION SIDEBAR] Rejected error message from Whisper backend:', event.transcript.substring(0, 100));
            return; // Don't process error messages as transcripts
        }
        
        // ✅ FILTER: Reject Whisper disabled message
        if (event.transcript && event.transcript.includes('Whisper backend disabled')) {
            console.log('[TRANSCRIPTION SIDEBAR] Ignored Whisper disabled message');
            return; // Don't process disabled message
        }
        
        // Update UI
        const stateElement = document.getElementById('stt-state');
        if (stateElement) {
            stateElement.textContent = 'Processing';
            stateElement.style.color = '#58a6ff';
        }

        // ✅ NOTE: Live display is handled by browser speech recognition (instant)
        // Whisper chunks are just for backend storage and accuracy verification
        console.log('[TRANSCRIPTION SIDEBAR] Whisper chunk saved for storage (live display via browser API)');

        // Add to transcript collection
        this.addSTTTranscript(event.transcript);

        // Update word count
        const words = event.transcript.trim().split(/\s+/).length;
        this.statistics.totalWords += words;
        this.updateStatistics();
    }

    handleSTTError(event) {
        console.error('[TRANSCRIPTION SIDEBAR] STT error:', event);
        
        document.getElementById('stt-state').textContent = 'Error';
        document.getElementById('stt-state').style.color = '#ef4444';
    }

    handleSTTChunkSent() {
        const chunks = parseInt(document.getElementById('stt-chunks').textContent) + 1;
        document.getElementById('stt-chunks').textContent = chunks;
        
        this.statistics.totalChunks++;
        this.updateStatistics();
    }

    /**
     * TTS event handlers
     */
    handleTTSStart() {
        console.log('[TRANSCRIPTION SIDEBAR] TTS started');
        
        document.getElementById('tts-state').textContent = 'Speaking';
        document.getElementById('tts-state').style.color = '#58a6ff';
    }

    handleTTSEnd() {
        console.log('[TRANSCRIPTION SIDEBAR] TTS ended');
        
        document.getElementById('tts-state').textContent = 'Complete';
        document.getElementById('tts-state').style.color = '#10b981';

        const utterances = parseInt(document.getElementById('tts-utterances').textContent) + 1;
        document.getElementById('tts-utterances').textContent = utterances;
        
        this.statistics.totalUtterances++;
        this.updateStatistics();
    }

    handleTTSError(event) {
        console.error('[TRANSCRIPTION SIDEBAR] TTS error:', event);
        
        document.getElementById('tts-state').textContent = 'Error';
        document.getElementById('tts-state').style.color = '#ef4444';
    }

    /**
     * Add STT transcript to collection
     */
    addSTTTranscript(text) {
        const transcript = {
            timestamp: Date.now(),
            text: text,
            type: 'stt'
        };
        
        this.sttTranscripts.push(transcript);
        
        // Update UI
        const container = document.getElementById('stt-transcript-collection');
        if (container) {
            // Remove empty state if present
            const emptyState = container.querySelector('.transcription-empty-state');
            if (emptyState) {
                emptyState.remove();
            }

            // Add transcript entry
            const entry = this.createTranscriptEntry(transcript);
            container.appendChild(entry);
            
            // Scroll to bottom
            container.scrollTop = container.scrollHeight;
        }
    }

    /**
     * Add TTS transcript to collection
     */
    addTTSTranscript(text) {
        const transcript = {
            timestamp: Date.now(),
            text: text,
            type: 'tts'
        };
        
        this.ttsTranscripts.push(transcript);
        
        // Update UI
        const container = document.getElementById('tts-transcript-collection');
        if (container) {
            // Remove empty state if present
            const emptyState = container.querySelector('.transcription-empty-state');
            if (emptyState) {
                emptyState.remove();
            }

            // Add transcript entry
            const entry = this.createTranscriptEntry(transcript);
            container.appendChild(entry);
            
            // Scroll to bottom
            container.scrollTop = container.scrollHeight;
        }
    }

    /**
     * Create transcript entry HTML element
     */
    createTranscriptEntry(transcript) {
        const entry = document.createElement('div');
        entry.className = 'transcription-transcript-entry';
        
        const time = new Date(transcript.timestamp).toLocaleTimeString();
        
        entry.innerHTML = `
            <div class="transcription-transcript-header">
                <span class="transcription-transcript-time">${time}</span>
                <div class="transcription-transcript-actions">
                    <button onclick="TranscriptionSidebar.sendTranscriptToChat(${transcript.timestamp})" title="Send to Chat">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                    <button onclick="TranscriptionSidebar.copyTranscript(${transcript.timestamp})" title="Copy">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button onclick="TranscriptionSidebar.deleteTranscript(${transcript.timestamp})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="transcription-transcript-text">${transcript.text}</div>
        `;
        
        return entry;
    }

    /**
     * Send transcript to chat input
     */
    sendTranscriptToChat(timestamp) {
        const transcript = [...this.sttTranscripts, ...this.ttsTranscripts]
            .find(t => t.timestamp === timestamp);
        
        if (transcript) {
            const chatInput = document.getElementById('ai-chat-input');
            if (chatInput) {
                // Check insert mode from settings
                const insertMode = this.config.insertMode || 'append';
                
                if (insertMode === 'replace') {
                    chatInput.value = transcript.text;
                } else if (insertMode === 'append') {
                    const currentText = chatInput.value.trim();
                    chatInput.value = currentText ? currentText + ' ' + transcript.text : transcript.text;
                }
                
                // Focus the input and trigger input event
                chatInput.focus();
                chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                
                console.log('[TRANSCRIPTION SIDEBAR] Transcript sent to chat input');
                
                // Optional: Show success feedback
                const btn = event?.target?.closest('button');
                if (btn) {
                    const icon = btn.querySelector('i');
                    if (icon) {
                        icon.className = 'fas fa-check';
                        setTimeout(() => {
                            icon.className = 'fas fa-paper-plane';
                        }, 1000);
                    }
                }
            } else {
                console.error('[TRANSCRIPTION SIDEBAR] Chat input not found (id: ai-chat-input)');
                alert('Chat input not found. Please make sure you\'re on the chat page.');
            }
        }
    }

    /**
     * Copy transcript to clipboard
     */
    copyTranscript(timestamp) {
        const transcript = [...this.sttTranscripts, ...this.ttsTranscripts]
            .find(t => t.timestamp === timestamp);
        
        if (transcript) {
            navigator.clipboard.writeText(transcript.text)
                .then(() => {
                    console.log('[TRANSCRIPTION SIDEBAR] Transcript copied to clipboard');
                    // Could show toast notification here
                })
                .catch(err => {
                    console.error('[TRANSCRIPTION SIDEBAR] Failed to copy transcript:', err);
                });
        }
    }

    /**
     * Send transcript to chat input
     */
    sendTranscriptToChat(timestamp) {
        const transcript = [...this.sttTranscripts, ...this.ttsTranscripts]
            .find(t => t.timestamp === timestamp);
        
        if (transcript) {
            const chatInput = document.getElementById('ai-chat-input');
            if (chatInput) {
                // Check insert mode from settings
                const insertMode = this.config.insertMode || 'append';
                
                if (insertMode === 'replace') {
                    chatInput.value = transcript.text;
                } else if (insertMode === 'append') {
                    const currentText = chatInput.value.trim();
                    chatInput.value = currentText ? currentText + ' ' + transcript.text : transcript.text;
                }
                
                // Focus the input and trigger input event
                chatInput.focus();
                chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                
                console.log('[TRANSCRIPTION SIDEBAR] Transcript sent to chat input');
                
                // Optional: Show success feedback
                const btn = event?.target?.closest('button');
                if (btn) {
                    const icon = btn.querySelector('i');
                    if (icon) {
                        icon.className = 'fas fa-check';
                        setTimeout(() => {
                            icon.className = 'fas fa-paper-plane';
                        }, 1000);
                    }
                }
            } else {
                console.error('[TRANSCRIPTION SIDEBAR] Chat input not found (id: ai-chat-input)');
                alert('Chat input not found. Please make sure you\'re on the chat page.');
            }
        }
    }

    /**
     * Delete transcript
     */
    deleteTranscript(timestamp) {
        // Remove from arrays
        this.sttTranscripts = this.sttTranscripts.filter(t => t.timestamp !== timestamp);
        this.ttsTranscripts = this.ttsTranscripts.filter(t => t.timestamp !== timestamp);
        
        // Remove from UI - find and remove the entry
        const containers = [
            document.getElementById('stt-transcript-collection'),
            document.getElementById('tts-transcript-collection')
        ];
        
        containers.forEach(container => {
            if (container) {
                const entries = container.querySelectorAll('.transcription-transcript-entry');
                entries.forEach(entry => {
                    const timeText = entry.querySelector('.transcription-transcript-time').textContent;
                    const entryTime = new Date(timestamp).toLocaleTimeString();
                    if (timeText === entryTime) {
                        entry.remove();
                    }
                });
            }
        });
    }

    /**
     * Send live transcript to chat input
     */
    sendLiveTranscriptToChat() {
        const liveDisplay = document.getElementById('transcription-live-display');
        if (!liveDisplay) return;
        
        // Get all final text segments (not interim, not action buttons)
        const textSegments = Array.from(liveDisplay.querySelectorAll('.final'))
            .map(el => el.textContent.trim())
            .filter(text => text.length > 0);
        
        const fullText = textSegments.join(' ');
        
        if (fullText) {
            const chatInput = document.getElementById('ai-chat-input');
            if (chatInput) {
                const insertMode = this.config.insertMode || 'append';
                
                if (insertMode === 'replace') {
                    chatInput.value = fullText;
                } else if (insertMode === 'append') {
                    const currentText = chatInput.value.trim();
                    chatInput.value = currentText ? currentText + ' ' + fullText : fullText;
                }
                
                chatInput.focus();
                chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                
                console.log('[TRANSCRIPTION SIDEBAR] Live transcript sent to chat input');
                
                // Show success feedback
                const btn = event?.target?.closest('button');
                if (btn) {
                    const icon = btn.querySelector('i');
                    const span = btn.querySelector('span');
                    if (icon) icon.className = 'fas fa-check';
                    if (span) span.textContent = 'Sent!';
                    setTimeout(() => {
                        if (icon) icon.className = 'fas fa-paper-plane';
                        if (span) span.textContent = 'Send to Chat';
                    }, 1500);
                }
            } else {
                console.error('[TRANSCRIPTION SIDEBAR] Chat input not found');
                alert('Chat input not found. Please make sure you\'re on the chat page.');
            }
        }
    }

    /**
     * Copy live transcript to clipboard
     */
    copyLiveTranscript() {
        const liveDisplay = document.getElementById('transcription-live-display');
        if (!liveDisplay) return;
        
        const textSegments = Array.from(liveDisplay.querySelectorAll('.final'))
            .map(el => el.textContent.trim())
            .filter(text => text.length > 0);
        
        const fullText = textSegments.join(' ');
        
        if (fullText) {
            navigator.clipboard.writeText(fullText)
                .then(() => {
                    console.log('[TRANSCRIPTION SIDEBAR] Live transcript copied');
                    const btn = event?.target?.closest('button');
                    if (btn) {
                        const icon = btn.querySelector('i');
                        if (icon) {
                            icon.className = 'fas fa-check';
                            setTimeout(() => {
                                icon.className = 'fas fa-copy';
                            }, 1000);
                        }
                    }
                })
                .catch(err => {
                    console.error('[TRANSCRIPTION SIDEBAR] Failed to copy:', err);
                });
        }
    }

    /**
     * Clear live transcript display
     */
    clearLiveTranscript() {
        const liveDisplay = document.getElementById('transcription-live-display');
        if (liveDisplay) {
            liveDisplay.innerHTML = '';
            console.log('[TRANSCRIPTION SIDEBAR] Live transcript cleared');
        }
    }

    /**
     * Clear all transcripts
     */
    clearAllTranscripts() {
        if (!confirm('Clear all transcripts? This cannot be undone.')) {
            return;
        }

        this.sttTranscripts = [];
        this.ttsTranscripts = [];
        
        const sttContainer = document.getElementById('stt-transcript-collection');
        const ttsContainer = document.getElementById('tts-transcript-collection');
        
        if (sttContainer) {
            sttContainer.innerHTML = `
                <div class="transcription-empty-state">
                    <i class="fas fa-microphone-slash"></i>
                    <p>No STT transcripts yet</p>
                    <small>Start recording to see transcripts here</small>
                </div>
            `;
        }
        
        if (ttsContainer) {
            ttsContainer.innerHTML = `
                <div class="transcription-empty-state">
                    <i class="fas fa-volume-mute"></i>
                    <p>No TTS transcripts yet</p>
                    <small>AI responses will appear here when spoken</small>
                </div>
            `;
        }
        
        console.log('[TRANSCRIPTION SIDEBAR] All transcripts cleared');
    }

    /**
     * Export transcripts
     */
    exportTranscripts(format) {
        const allTranscripts = [...this.sttTranscripts, ...this.ttsTranscripts]
            .sort((a, b) => a.timestamp - b.timestamp);
        
        if (allTranscripts.length === 0) {
            alert('No transcripts to export');
            return;
        }

        let content = '';
        let filename = '';
        let mimeType = '';

        if (format === 'txt') {
            content = allTranscripts.map(t => {
                const time = new Date(t.timestamp).toLocaleString();
                const type = t.type.toUpperCase();
                return `[${time}] [${type}]\n${t.text}\n`;
            }).join('\n');
            filename = `transcripts_${Date.now()}.txt`;
            mimeType = 'text/plain';
        } else if (format === 'json') {
            content = JSON.stringify(allTranscripts, null, 2);
            filename = `transcripts_${Date.now()}.json`;
            mimeType = 'application/json';
        }

        // Create download
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log(`[TRANSCRIPTION SIDEBAR] Transcripts exported as ${format}`);
    }

    /**
     * Update statistics display
     */
    updateStatistics() {
        document.getElementById('stat-total-chunks').textContent = this.statistics.totalChunks;
        document.getElementById('stat-total-utterances').textContent = this.statistics.totalUtterances;
        document.getElementById('stat-total-words').textContent = this.statistics.totalWords;
        
        const minutes = Math.floor(this.statistics.totalRecordingTime / 60);
        const seconds = this.statistics.totalRecordingTime % 60;
        document.getElementById('stat-total-recording-time').textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    /**
     * Reset statistics
     */
    resetStatistics() {
        if (!confirm('Reset all statistics? This cannot be undone.')) {
            return;
        }

        this.statistics = {
            totalChunks: 0,
            totalUtterances: 0,
            totalRecordingTime: 0,
            totalWords: 0
        };
        
        document.getElementById('stt-chunks').textContent = '0';
        document.getElementById('tts-utterances').textContent = '0';
        document.getElementById('stt-duration').textContent = '0:00';
        
        this.updateStatistics();
        
        console.log('[TRANSCRIPTION SIDEBAR] Statistics reset');
    }

    /**
     * Populate voice select dropdown
     */
    populateVoiceSelect() {
        if (!this.ttsModule) return;

        const select = document.getElementById('transcription-voice-select');
        if (!select) return;

        const voices = this.ttsModule.getVoices();
        
        if (voices.length === 0) {
            // Voices not loaded yet, try again in 100ms
            setTimeout(() => this.populateVoiceSelect(), 100);
            return;
        }

        select.innerHTML = '';
        voices.forEach((voice, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = `${voice.name} (${voice.lang})`;
            
            if (voice === this.ttsModule.options.voice) {
                option.selected = true;
            }
            
            select.appendChild(option);
        });

        this.updateVoiceInfo();
    }

    /**
     * Update voice info display
     */
    updateVoiceInfo() {
        if (!this.ttsModule) return;

        const voice = this.ttsModule.options.voice;
        const infoElement = document.getElementById('transcription-voice-info');
        
        if (voice && infoElement) {
            infoElement.textContent = `Language: ${voice.lang} | ${voice.localService ? 'Local' : 'Remote'}`;
        }
    }

    /**
     * Check browser support
     */
    checkBrowserSupport() {
        // MediaRecorder API
        const mediaRecorderSupported = typeof MediaRecorder !== 'undefined';
        const mediaRecorderElement = document.getElementById('support-mediarecorder');
        if (mediaRecorderElement) {
            mediaRecorderElement.textContent = mediaRecorderSupported ? '✓ Supported' : '✗ Not Supported';
            mediaRecorderElement.classList.add(mediaRecorderSupported ? 'supported' : 'not-supported');
        }

        // Web Speech API (TTS)
        const speechSynthesisSupported = 'speechSynthesis' in window;
        const speechSynthesisElement = document.getElementById('support-speechsynthesis');
        if (speechSynthesisElement) {
            speechSynthesisElement.textContent = speechSynthesisSupported ? '✓ Supported' : '✗ Not Supported';
            speechSynthesisElement.classList.add(speechSynthesisSupported ? 'supported' : 'not-supported');
        }

        // Microphone access (check permission)
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                stream.getTracks().forEach(track => track.stop());
                const micElement = document.getElementById('support-microphone');
                if (micElement) {
                    micElement.textContent = '✓ Granted';
                    micElement.classList.add('supported');
                }
            })
            .catch(err => {
                const micElement = document.getElementById('support-microphone');
                if (micElement) {
                    micElement.textContent = '✗ Denied';
                    micElement.classList.add('not-supported');
                }
            });
    }

    /**
     * Test backend connection
     */
    async testBackendConnection() {
        const settings = this.getSTTSettings();
        const endpoint = settings.whisperEndpoint.replace('/transcribe', '/system/check');
        
        const statusDot = document.getElementById('backend-status-dot');
        const statusText = document.getElementById('backend-status-text');
        const statusDetail = document.getElementById('backend-status-detail');
        
        try {
            const response = await fetch(endpoint);
            
            if (response.ok) {
                if (statusDot) {
                    statusDot.classList.add('online');
                }
                if (statusText) {
                    statusText.textContent = 'Online';
                    statusText.style.color = '#10b981';
                }
                if (statusDetail) {
                    statusDetail.textContent = 'Backend is reachable and healthy';
                }
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            if (statusDot) {
                statusDot.classList.add('offline');
            }
            if (statusText) {
                statusText.textContent = 'Offline';
                statusText.style.color = '#ef4444';
            }
            if (statusDetail) {
                statusDetail.textContent = `Cannot connect: ${error.message}`;
            }
        }
    }

    /**
     * Refresh status
     */
    async refreshStatus() {
        console.log('[TRANSCRIPTION SIDEBAR] Refreshing status...');
        await this.testBackendConnection();
        this.checkBrowserSupport();
    }

    /**
     * TTS control methods
     */
    pauseTTS() {
        if (this.ttsModule) {
            this.ttsModule.togglePause();
        }
    }

    stopTTS() {
        if (this.ttsModule) {
            this.ttsModule.stop();
        }
    }

    clearTTSTranscript() {
        if (this.ttsModule) {
            this.ttsModule.clearTranscript();
        }
    }

    /**
     * Test methods
     */
    async testSTT() {
        alert('Start recording and speak to test STT. Your speech will be sent to the Whisper backend.');
    }

    testTTS() {
        if (this.ttsModule) {
            this.ttsModule.speak('This is a test of the text to speech system.');
        }
    }

    /**
     * Backend configuration helpers
     */
    detectBackendUrl() {
        if (!window.TranscriptionConfig) {
            alert('TranscriptionConfig not loaded. Please ensure config.js is included.');
            return;
        }
        
        const detectedUrl = window.TranscriptionConfig.getEndpoint('transcribe');
        const input = document.getElementById('transcription-whisper-endpoint');
        if (input) {
            input.value = detectedUrl;
        }
        
        // Update hint
        const hint = document.getElementById('backend-url-hint');
        if (hint) {
            const config = window.TranscriptionConfig.getConfig();
            const env = config.environment === 'local' ? 'Local (localhost:5001)' : 'Production (Render)';
            hint.textContent = `${env}: ${detectedUrl}`;
        }
        
        const config = window.TranscriptionConfig.getConfig();
        const envLabel = config.environment === 'local' ? 'Local Development' : 'Production (Render)';
        console.log('[TRANSCRIPTION SIDEBAR] Auto-detected backend URL:', detectedUrl);
        alert(`Detected ${envLabel} backend:\n${detectedUrl}\n\nUsing global API_BASE_URL: ${config.globalApiBaseUrl}`);
    }

    /**
     * Settings management
     */
    getSTTSettings() {
        // Get default endpoint from centralized config
        const defaultEndpoint = window.TranscriptionConfig ? 
            window.TranscriptionConfig.getEndpoint('transcribe') : 
            'http://localhost:5001/api/transcribe';
        
        return {
            whisperEndpoint: document.getElementById('transcription-whisper-endpoint')?.value || defaultEndpoint,
            apiKey: document.getElementById('transcription-api-key')?.value || null,
            insertMode: document.getElementById('transcription-insert-mode')?.value || 'append',
            chunkSize: parseInt(document.getElementById('transcription-chunk-size')?.value || 5000),
            sampleRate: parseInt(document.getElementById('transcription-sample-rate')?.value || 16000)
        };
    }

    getTTSSettings() {
        return {
            voice: null, // Will be set by voice select
            rate: parseFloat(document.getElementById('transcription-rate')?.value || 1.0),
            pitch: parseFloat(document.getElementById('transcription-pitch')?.value || 1.0),
            volume: parseInt(document.getElementById('transcription-volume')?.value || 100)
        };
    }

    saveSTTSettings() {
        const settings = this.getSTTSettings();
        localStorage.setItem('transcription-stt-settings', JSON.stringify(settings));
        console.log('[TRANSCRIPTION SIDEBAR] STT settings saved:', settings);
        
        // Reinitialize STT module with new settings
        if (this.sttModule) {
            this.sttModule.options.whisperEndpoint = settings.whisperEndpoint;
            this.sttModule.options.apiKey = settings.apiKey;
            this.sttModule.options.insertMode = settings.insertMode;
            this.sttModule.options.timeSlice = settings.chunkSize;
            this.sttModule.options.sampleRate = settings.sampleRate;
        }
        
        alert('STT settings saved successfully');
    }

    saveTTSSettings() {
        const settings = this.getTTSSettings();
        localStorage.setItem('transcription-tts-settings', JSON.stringify(settings));
        console.log('[TRANSCRIPTION SIDEBAR] TTS settings saved:', settings);
        
        alert('TTS settings saved successfully');
    }

    loadSettings() {
        // Load STT settings
        const sttSettings = localStorage.getItem('transcription-stt-settings');
        if (sttSettings) {
            try {
                const settings = JSON.parse(sttSettings);
                document.getElementById('transcription-whisper-endpoint').value = settings.whisperEndpoint;
                document.getElementById('transcription-api-key').value = settings.apiKey || '';
                document.getElementById('transcription-insert-mode').value = settings.insertMode;
                document.getElementById('transcription-chunk-size').value = settings.chunkSize;
                document.getElementById('transcription-sample-rate').value = settings.sampleRate;
        
                // Update hint with loaded URL
                const hint = document.getElementById('backend-url-hint');
                if (hint) {
                    hint.textContent = `Saved: ${settings.whisperEndpoint}`;
                }
            } catch (error) {
                console.error('[TRANSCRIPTION SIDEBAR] Failed to load STT settings:', error);
            }
        }

        // Load TTS settings
        const ttsSettings = localStorage.getItem('transcription-tts-settings');
        if (ttsSettings) {
            try {
                const settings = JSON.parse(ttsSettings);
                document.getElementById('transcription-rate').value = settings.rate;
                document.getElementById('transcription-rate-value').textContent = `${settings.rate}x`;
                document.getElementById('transcription-pitch').value = settings.pitch;
                document.getElementById('transcription-pitch-value').textContent = `${settings.pitch}x`;
                document.getElementById('transcription-volume').value = settings.volume;
                document.getElementById('transcription-volume-value').textContent = `${settings.volume}%`;
            } catch (error) {
                console.error('[TRANSCRIPTION SIDEBAR] Failed to load TTS settings:', error);
            }
        }
    }
}

// Export as singleton
window.TranscriptionSidebar = new TranscriptionSidebarController();

console.log('[TRANSCRIPTION SIDEBAR] Exported to window.TranscriptionSidebar');
