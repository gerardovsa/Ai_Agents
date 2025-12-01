/**
 * FILE: UI/modules/transcription/stt-module-dual.js
 * PURPOSE: Dual-mode Speech-to-Text with Browser Web Speech API + Whisper Backend
 * 
 * ARCHITECTURE:
 * - Browser Web Speech API → Instant interim results (real-time streaming during speech)
 * - MediaRecorder + Whisper → High-quality final transcription (background processing)
 * 
 * DEPENDENCIES:
 * - Web Speech API (webkitSpeechRecognition) - Browser native real-time STT
 * - MediaRecorder API - Audio capture for Whisper
 * - Whisper Backend API - Server-side high-quality transcription
 * 
 * EXPORTS:
 * - STTModuleDual class - Complete dual-mode STT controller
 * 
 * USED BY:
 * - business-ai-platform-v2.html (main AI chat interface)
 * - transcription-sidebar.html (sidebar transcription UI)
 * 
 * RELATED FILES:
 * - stt-module.js (original backend-only version)
 * - transcription-streaming-container.js (UI display controller)
 * - config.js (API endpoint configuration)
 * 
 * MIGRATION FROM V7_MustCare:
 * - Based on voiceModule.js dual recognition system
 * - Adapted for AI_agents Flask backend architecture
 * - Unified with existing TranscriptionStreamingController
 * 
 * LAST MODIFIED: 2025-11-27 - Created dual-mode system with instant streaming
 */

class STTModuleDual {
    constructor(options = {}) {
        this.options = {
            // Recording Settings
            sampleRate: options.sampleRate || 16000,
            mimeType: options.mimeType || 'audio/webm',
            timeSlice: options.timeSlice || 1000, // 1 second chunks for real-time
            
            // Backend Settings
            whisperEndpoint: options.whisperEndpoint || (window.TranscriptionConfig ? 
                window.TranscriptionConfig.getEndpoint('transcribe') : 
                'http://localhost:5001/api/transcribe'),
            apiKey: options.apiKey || null,
            
            // Browser Speech API Settings
            useBrowserSTT: options.useBrowserSTT !== false, // Enable by default
            browserLanguage: options.browserLanguage || 'en-US',
            browserContinuous: options.browserContinuous !== false,
            browserInterimResults: options.browserInterimResults !== false,
            
            // UI Elements
            recordButton: options.recordButton || 'stt-record-btn',
            transcriptDisplay: options.transcriptDisplay || 'stt-transcript-display',
            statusIndicator: options.statusIndicator || 'stt-status-indicator',
            
            // Transcript Insertion
            insertTarget: options.insertTarget || 'ai-chat-input',
            insertMode: options.insertMode || 'append', // 'append' | 'replace' | 'none'
            
            // Feature Flags
            enableIdempotency: options.enableIdempotency !== false,
            maxRetries: options.maxRetries || 3,
            retryDelay: options.retryDelay || 1000,
            showVisualFeedback: options.showVisualFeedback !== false,
            autoScroll: options.autoScroll !== false,
            
            // Callbacks
            onStart: options.onStart || (() => {}),
            onStop: options.onStop || (() => {}),
            onInterimTranscript: options.onInterimTranscript || (() => {}), // NEW: Interim results
            onTranscript: options.onTranscript || (() => {}), // Final results
            onError: options.onError || (() => {}),
            onChunkSent: options.onChunkSent || (() => {})
        };

        // State
        this.recording = false;
        this.processing = false;
        this.sessionId = this.generateSessionId();
        
        // MediaRecorder state (Whisper backend)
        this.mediaRecorder = null;
        this.audioStream = null;
        this.audioChunks = [];
        this.chunkCount = 0;
        this.chunkRequestInterval = null;
        
        // Browser Speech Recognition state (instant streaming)
        this.recognition = null;
        this.browserSTTActive = false;
        this.interimTranscript = '';
        this.finalTranscript = '';
        
        // Idempotency tracking
        this.processedChunks = new Map();
        this.cleanupInterval = null;
        
        // DOM Elements
        this.recordButton = null;
        this.transcriptDisplay = null;
        this.statusIndicator = null;
        this.insertTarget = null;
        
        // Initialize
        this.initialize();
    }

    /**
     * Initialize STT module and check browser support
     */
    initialize() {
        console.log('🎤 [Dual STT] Initializing...');

        // Check MediaRecorder support (required for Whisper)
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            console.error('❌ getUserMedia not supported');
            this.showError('Microphone access not supported in this browser');
            return false;
        }

        if (!window.MediaRecorder) {
            console.error('❌ MediaRecorder not supported');
            this.showError('Audio recording not supported in this browser');
            return false;
        }

        // Check Browser Speech API support (optional for instant streaming)
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition && this.options.useBrowserSTT) {
            console.log('✅ Browser Speech API available (instant streaming enabled)');
            this.initializeBrowserSTT();
        } else {
            console.warn('⚠️ Browser Speech API not available (using Whisper only)');
            this.options.useBrowserSTT = false;
        }

        // Get DOM elements
        this.recordButton = document.getElementById(this.options.recordButton);
        this.transcriptDisplay = document.getElementById(this.options.transcriptDisplay);
        this.statusIndicator = document.getElementById(this.options.statusIndicator);
        this.insertTarget = document.getElementById(this.options.insertTarget);

        if (!this.recordButton) {
            console.error(`❌ Record button not found: ${this.options.recordButton}`);
            return false;
        }

        // Setup record button event
        this.recordButton.addEventListener('click', () => this.toggleRecording());

        // Setup idempotency cleanup
        if (this.options.enableIdempotency) {
            this.cleanupInterval = setInterval(() => this.cleanupProcessedChunks(), 5 * 60 * 1000);
        }

        console.log('✅ [Dual STT] Initialized successfully');
        console.log('   • Browser STT:', this.options.useBrowserSTT ? 'ENABLED' : 'DISABLED');
        console.log('   • Whisper Backend:', 'ENABLED');
        return true;
    }

    /**
     * Initialize Browser Speech Recognition (instant streaming)
     */
    initializeBrowserSTT() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = this.options.browserContinuous;
        this.recognition.interimResults = this.options.browserInterimResults;
        this.recognition.lang = this.options.browserLanguage;
        this.recognition.maxAlternatives = 1;

        // Event handlers
        this.recognition.onstart = () => {
            console.log('🎤 [Browser STT] Started');
            this.browserSTTActive = true;
        };

        this.recognition.onresult = (event) => {
            this.handleBrowserSTTResult(event);
        };

        this.recognition.onerror = (event) => {
            console.warn('[Browser STT] Error:', event.error);
            
            // Non-fatal errors (continue with Whisper)
            if (event.error === 'no-speech' || event.error === 'audio-capture') {
                console.log('[Browser STT] Non-fatal error, continuing with Whisper only');
                return;
            }
            
            // Fatal errors
            console.error('[Browser STT] Fatal error:', event.error);
            this.browserSTTActive = false;
        };

        this.recognition.onend = () => {
            console.log('🎤 [Browser STT] Ended');
            this.browserSTTActive = false;
            
            // Auto-restart if still recording (continuous mode)
            if (this.recording && this.options.browserContinuous) {
                try {
                    console.log('🔄 [Browser STT] Restarting...');
                    this.recognition.start();
                } catch (err) {
                    console.warn('[Browser STT] Restart failed:', err);
                }
            }
        };

        console.log('✅ [Browser STT] Initialized');
    }

    /**
     * Handle Browser Speech Recognition result (INSTANT STREAMING)
     */
    handleBrowserSTTResult(event) {
        let interimTranscript = '';
        let finalTranscript = '';

        // Process all results
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            const confidence = event.results[i][0].confidence;

            if (event.results[i].isFinal) {
                // Final result from browser STT
                finalTranscript += transcript + ' ';
                
                console.log(`📝 [Browser STT] Final: "${transcript}" (confidence: ${(confidence * 100).toFixed(1)}%)`);
                
                // Store final transcript
                this.finalTranscript += transcript + ' ';
                
                // Emit final transcript callback
                this.options.onTranscript({
                    transcript: transcript.trim(),
                    isFinal: true,
                    confidence: confidence,
                    source: 'browser-speech-api',
                    timestamp: Date.now()
                });
                
                // Display final (if TranscriptionStreaming available)
                if (window.TranscriptionStreaming) {
                    window.TranscriptionStreaming.streamText(
                        transcript.trim(),
                        true, // isFinal
                        this.getConfidenceLevel(confidence),
                        'browser-stt'
                    );
                }
                
                // Insert into target
                if (this.options.insertMode !== 'none') {
                    this.insertTranscript(transcript.trim());
                }
                
            } else {
                // Interim result (STREAMING)
                interimTranscript += transcript;
                
                console.log(`💭 [Browser STT] Interim: "${transcript}"`);
                
                // Emit interim transcript callback
                this.options.onInterimTranscript({
                    transcript: interimTranscript,
                    isFinal: false,
                    confidence: confidence,
                    source: 'browser-speech-api',
                    timestamp: Date.now()
                });
                
                // Display interim (if TranscriptionStreaming available)
                if (window.TranscriptionStreaming) {
                    window.TranscriptionStreaming.streamText(
                        interimTranscript,
                        false, // not final
                        this.getConfidenceLevel(confidence),
                        'browser-stt'
                    );
                }
                
                // Update input field with interim (for live preview)
                if (this.insertTarget && this.options.insertMode === 'append') {
                    const currentValue = this.insertTarget.value || '';
                    const baseText = this.finalTranscript;
                    this.insertTarget.value = (currentValue.replace(this.interimTranscript, '') + baseText + interimTranscript).trim();
                }
            }
        }

        // Store current interim text
        this.interimTranscript = interimTranscript;
    }

    /**
     * Get confidence level string from numeric confidence
     */
    getConfidenceLevel(confidence) {
        if (!confidence) return 'unknown';
        if (confidence >= 0.8) return 'high';
        if (confidence >= 0.5) return 'medium';
        return 'low';
    }

    /**
     * Toggle recording on/off
     */
    async toggleRecording() {
        if (this.recording) {
            this.stopRecording();
        } else {
            await this.startRecording();
        }
    }

    /**
     * Start dual-mode recording
     */
    async startRecording() {
        console.log('🎤 [Dual STT] Starting recording...');

        try {
            // Request microphone access
            this.audioStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: this.options.sampleRate,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            });
            
            console.log('✅ Microphone stream obtained');

            // === INSTANT PATH: Start Browser Speech Recognition ===
            if (this.recognition && this.options.useBrowserSTT) {
                try {
                    this.recognition.start();
                    console.log('✅ [Browser STT] Started (instant streaming active)');
                } catch (err) {
                    console.warn('[Browser STT] Start failed (non-fatal):', err);
                }
            }

            // === QUALITY PATH: Start MediaRecorder for Whisper ===
            const mimeType = this.getSupportedMimeType();
            this.mediaRecorder = new MediaRecorder(this.audioStream, { mimeType });

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    console.log(`📦 [MediaRecorder] Chunk: ${event.data.size} bytes`);
                    this.handleAudioChunk(event);
                }
            };

            this.mediaRecorder.onstop = () => {
                console.log('🛑 [MediaRecorder] Stopped');
                this.handleRecordingStop();
            };

            this.mediaRecorder.onerror = (event) => {
                console.error('❌ [MediaRecorder] Error:', event.error);
                this.handleRecordingError(event);
            };

            // Start recording with 1-second chunks (real-time)
            this.mediaRecorder.start(this.options.timeSlice);
            console.log(`✅ [MediaRecorder] Started (${this.options.timeSlice}ms chunks)`);

            // Backup: Manually request data (some browsers don't fire ondataavailable reliably)
            this.chunkRequestInterval = setInterval(() => {
                if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
                    this.mediaRecorder.requestData();
                }
            }, this.options.timeSlice);

            // Update state
            this.recording = true;
            this.audioChunks = [];
            this.chunkCount = 0;
            this.sessionId = this.generateSessionId();
            this.interimTranscript = '';
            this.finalTranscript = '';

            // Update UI
            this.updateRecordButton(true);
            this.updateStatus('recording', '🔴 Recording...');

            // Callback
            this.options.onStart({ 
                timestamp: Date.now(), 
                sessionId: this.sessionId,
                browserSTT: this.browserSTTActive
            });

            console.log('✅ [Dual STT] Recording started successfully');
            console.log('   • Browser STT:', this.browserSTTActive ? 'ACTIVE' : 'INACTIVE');
            console.log('   • Whisper Backend:', 'ACTIVE');

        } catch (error) {
            console.error('❌ Failed to start recording:', error);
            this.showError(`Microphone access denied: ${error.message}`);
            this.options.onError({ error: 'start-failed', message: error.message });
        }
    }

    /**
     * Stop dual-mode recording
     */
    stopRecording() {
        console.log('🛑 [Dual STT] Stopping recording...');

        if (!this.recording) {
            console.warn('⚠️ No recording to stop');
            return;
        }

        // Stop Browser Speech Recognition
        if (this.recognition && this.browserSTTActive) {
            try {
                this.recognition.stop();
                console.log('✅ [Browser STT] Stopped');
            } catch (err) {
                console.warn('[Browser STT] Stop failed:', err);
            }
        }

        // Stop MediaRecorder
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
            console.log('✅ [MediaRecorder] Stopped');
        }

        // Stop audio stream
        if (this.audioStream) {
            this.audioStream.getTracks().forEach(track => track.stop());
            this.audioStream = null;
        }
        
        // Clear chunk request interval
        if (this.chunkRequestInterval) {
            clearInterval(this.chunkRequestInterval);
            this.chunkRequestInterval = null;
        }

        // Update state
        this.recording = false;
        this.browserSTTActive = false;

        // Update UI
        this.updateRecordButton(false);
        this.updateStatus('processing', 'Processing final chunks...');

        console.log('✅ [Dual STT] Recording stopped');
    }

    /**
     * Handle audio chunk from MediaRecorder (send to Whisper)
     */
    async handleAudioChunk(event) {
        if (event.data.size === 0) return;

        this.audioChunks.push(event.data);
        this.chunkCount++;

        // Send to Whisper backend
        await this.sendChunkToWhisper(event.data);
    }

    /**
     * Send audio chunk to Whisper backend
     */
    async sendChunkToWhisper(blob) {
        const chunkId = `${this.sessionId}_${this.chunkCount}_${Date.now()}`;

        // Check idempotency
        if (this.options.enableIdempotency && this.processedChunks.has(chunkId)) {
            console.log(`⏭️ Skipping duplicate chunk: ${chunkId}`);
            return this.processedChunks.get(chunkId);
        }

        console.log(`📤 [Whisper] Sending chunk: ${chunkId}`);
        this.updateStatus('processing', `Processing chunk ${this.chunkCount}...`);

        try {
            const formData = new FormData();
            formData.append('file', blob, `audio_${chunkId}.webm`);
            formData.append('chunk_id', chunkId);
            formData.append('session_id', this.sessionId);
            formData.append('chunk_number', this.chunkCount.toString());

            const result = await this.sendWithRetry(formData, chunkId);

            // Store for idempotency
            if (this.options.enableIdempotency) {
                this.processedChunks.set(chunkId, result);
            }

            // Display Whisper transcript (higher quality backup)
            if (result.transcript && result.transcript.trim()) {
                console.log(`✅ [Whisper] Transcribed: "${result.transcript}"`);
                
                // Emit final transcript callback
                this.options.onTranscript({
                    transcript: result.transcript.trim(),
                    isFinal: true,
                    confidence: 1.0, // Whisper doesn't provide confidence
                    source: 'whisper-backend',
                    timestamp: Date.now(),
                    chunkId: chunkId
                });
                
                // Display in streaming container (if available)
                if (window.TranscriptionStreaming) {
                    window.TranscriptionStreaming.streamText(
                        result.transcript.trim(),
                        true, // isFinal
                        'high', // Whisper is typically high quality
                        'whisper'
                    );
                }
            }

            this.updateStatus('success', '✅ Transcription successful');

            this.options.onChunkSent({ chunkId, success: true });

            return result;

        } catch (error) {
            console.error(`❌ [Whisper] Chunk ${chunkId} failed:`, error);
            this.showError(`Transcription failed: ${error.message}`);
            this.options.onChunkSent({ chunkId, success: false, error: error.message });
            throw error;
        }
    }

    /**
     * Send chunk with retry logic
     */
    async sendWithRetry(formData, chunkId, attempt = 1) {
        try {
            const headers = {};
            if (this.options.apiKey) {
                headers['X-API-Key'] = this.options.apiKey;
            }

            const response = await fetch(this.options.whisperEndpoint, {
                method: 'POST',
                headers: headers,
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`HTTP ${response.status}: ${errorData.message || response.statusText}`);
            }

            return await response.json();

        } catch (error) {
            console.error(`❌ Attempt ${attempt} failed:`, error);

            if (this.isRetryableError(error) && attempt < this.options.maxRetries) {
                const delay = this.options.retryDelay * Math.pow(2, attempt - 1);
                console.log(`⏳ Retrying in ${delay}ms...`);
                
                await this.delay(delay);
                return this.sendWithRetry(formData, chunkId, attempt + 1);
            }

            throw error;
        }
    }

    /**
     * Check if error is retryable
     */
    isRetryableError(error) {
        const retryableErrors = [
            'Failed to fetch',
            'NetworkError',
            'HTTP 500',
            'HTTP 502',
            'HTTP 503',
            'HTTP 504'
        ];
        return retryableErrors.some(msg => error.message.includes(msg));
    }

    /**
     * Insert transcript into target element
     */
    insertTranscript(transcript) {
        if (!this.insertTarget) return;

        if (this.options.insertMode === 'append') {
            const currentText = this.insertTarget.value || '';
            const separator = currentText && !currentText.endsWith(' ') ? ' ' : '';
            this.insertTarget.value = currentText + separator + transcript;
        } else if (this.options.insertMode === 'replace') {
            this.insertTarget.value = transcript;
        }

        this.insertTarget.dispatchEvent(new Event('input', { bubbles: true }));
        this.insertTarget.focus();
    }

    /**
     * Update record button UI
     */
    updateRecordButton(recording) {
        if (!this.recordButton) return;

        if (recording) {
            this.recordButton.classList.add('stt-recording');
            this.recordButton.innerHTML = '<i class="fas fa-stop"></i>';
            this.recordButton.title = 'Stop Recording';
        } else {
            this.recordButton.classList.remove('stt-recording');
            this.recordButton.innerHTML = '<i class="fas fa-microphone"></i>';
            this.recordButton.title = 'Start Recording';
        }
    }

    /**
     * Update status indicator
     */
    updateStatus(status, message) {
        if (!this.statusIndicator) return;

        this.statusIndicator.className = `stt-status-indicator stt-status-${status}`;
        this.statusIndicator.textContent = message;
        this.statusIndicator.style.display = 'flex';

        if (status === 'success' || status === 'error') {
            setTimeout(() => {
                if (this.statusIndicator) {
                    this.statusIndicator.style.display = 'none';
                }
            }, 3000);
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        console.error('❌', message);
        this.updateStatus('error', message);
    }

    /**
     * Get supported MIME type
     */
    getSupportedMimeType() {
        const types = [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/ogg;codecs=opus',
            'audio/mp4'
        ];

        for (const type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
                console.log(`✅ Using MIME type: ${type}`);
                return type;
            }
        }

        console.warn('⚠️ No supported MIME type found');
        return '';
    }

    /**
     * Generate unique session ID
     */
    generateSessionId() {
        return `dual_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Cleanup old processed chunks
     */
    cleanupProcessedChunks() {
        const now = Date.now();
        const maxAge = 5 * 60 * 1000; // 5 minutes

        for (const [chunkId, result] of this.processedChunks.entries()) {
            const parts = chunkId.split('_');
            const timestamp = parseInt(parts[parts.length - 1]);

            if (now - timestamp > maxAge) {
                this.processedChunks.delete(chunkId);
            }
        }
    }

    /**
     * Delay helper
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Handle recording stop
     */
    handleRecordingStop() {
        this.options.onStop({ 
            timestamp: Date.now(), 
            sessionId: this.sessionId,
            totalChunks: this.chunkCount,
            finalTranscript: this.finalTranscript.trim()
        });
    }

    /**
     * Handle recording error
     */
    handleRecordingError(event) {
        console.error('❌ Recording error:', event.error);
        this.showError(`Recording error: ${event.error}`);
        this.stopRecording();
        this.options.onError({ error: 'recording-error', message: event.error });
    }

    /**
     * Clear transcript display
     */
    clearTranscript() {
        if (this.transcriptDisplay) {
            this.transcriptDisplay.innerHTML = '';
        }
        this.interimTranscript = '';
        this.finalTranscript = '';
    }

    /**
     * Get current state
     */
    getState() {
        return {
            recording: this.recording,
            browserSTTActive: this.browserSTTActive,
            processing: this.processing,
            sessionId: this.sessionId,
            chunkCount: this.chunkCount,
            processedChunksCount: this.processedChunks.size,
            finalTranscript: this.finalTranscript
        };
    }

    /**
     * Destroy module and cleanup
     */
    destroy() {
        console.log('🧹 [Dual STT] Destroying...');

        if (this.recording) {
            this.stopRecording();
        }

        if (this.cleanupInterval) {
            clearInterval(this.cleanupInterval);
        }

        if (this.chunkRequestInterval) {
            clearInterval(this.chunkRequestInterval);
        }

        this.processedChunks.clear();

        this.recordButton = null;
        this.transcriptDisplay = null;
        this.statusIndicator = null;
        this.insertTarget = null;
        this.recognition = null;

        console.log('✅ [Dual STT] Destroyed');
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = STTModuleDual;
}

window.STTModuleDual = STTModuleDual;
