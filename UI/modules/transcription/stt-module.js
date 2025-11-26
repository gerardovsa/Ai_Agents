/**
 * FILE: UI/modules/transcription/stt-module.js
 * PURPOSE: Speech-to-Text module with Whisper backend integration
 * 
 * DEPENDENCIES:
 * - Web Speech API (MediaRecorder) - Browser native audio recording
 * - Whisper Backend API - Server-side transcription
 * 
 * EXPORTS:
 * - STTModule class - Main STT controller with audio recording
 * 
 * USED BY:
 * - business-ai-platform-v2.html (main AI chat interface)
 * 
 * RELATED FILES:
 * - stt-module.css - Styling for audio controls
 * - tts-module.js - TTS counterpart
 * 
 * NOTES:
 * - Inspired by V7_MustCare voiceModule.js + whisperIntegration.js
 * - Records audio via MediaRecorder API
 * - Sends chunks to Whisper backend for transcription
 * - Displays transcript in real-time as it arrives
 * - Idempotency protection via chunk IDs
 * - Retry logic with exponential backoff
 * - Visual feedback (recording/processing/success/error)
 * 
 * LAST MODIFIED: 2025-01-XX - Initial creation for AI_agents project
 */

class STTModule {
    constructor(options = {}) {
        this.options = {
            // Recording Settings
            sampleRate: options.sampleRate || 16000,
            mimeType: options.mimeType || 'audio/webm',
            timeSlice: options.timeSlice || 5000, // 5 seconds per chunk
            
            // Backend Settings
            whisperEndpoint: options.whisperEndpoint || 'http://localhost:3001/api/v1/transcribe',
            apiKey: options.apiKey || null, // X-API-Key header
            
            // UI Elements
            recordButton: options.recordButton || 'stt-record-btn',
            transcriptDisplay: options.transcriptDisplay || 'stt-transcript-display',
            statusIndicator: options.statusIndicator || 'stt-status-indicator',
            
            // Transcript Insertion
            insertTarget: options.insertTarget || 'ai-chat-input', // Where to insert transcript
            insertMode: options.insertMode || 'append', // 'append' | 'replace' | 'none'
            
            // Idempotency & Retry
            enableIdempotency: options.enableIdempotency !== false,
            maxRetries: options.maxRetries || 3,
            retryDelay: options.retryDelay || 1000, // ms
            
            // Visual Feedback
            showVisualFeedback: options.showVisualFeedback !== false,
            autoScroll: options.autoScroll !== false,
            
            // Callbacks
            onStart: options.onStart || (() => {}),
            onStop: options.onStop || (() => {}),
            onTranscript: options.onTranscript || (() => {}),
            onError: options.onError || (() => {}),
            onChunkSent: options.onChunkSent || (() => {})
        };

        // State
        this.recording = false;
        this.processing = false;
        this.mediaRecorder = null;
        this.audioStream = null;
        this.audioChunks = [];
        this.chunkCount = 0;
        this.sessionId = this.generateSessionId();
        
        // Idempotency tracking
        this.processedChunks = new Map(); // chunkId -> result
        this.cleanupInterval = null;
        
        // DOM Elements
        this.recordButton = null;
        this.transcriptDisplay = null;
        this.statusIndicator = null;
        this.insertTarget = null;
        
        // Verify browser support
        this.initialize();
    }

    /**
     * Initialize STT module and check browser support
     */
    initialize() {
        console.log('🎤 Initializing STT Module...');

        // Check browser support
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            console.error('❌ getUserMedia not supported in this browser');
            this.showError('Microphone access not supported in this browser');
            return false;
        }

        if (!window.MediaRecorder) {
            console.error('❌ MediaRecorder not supported in this browser');
            this.showError('Audio recording not supported in this browser');
            return false;
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

        // Setup idempotency cleanup (every 5 minutes)
        if (this.options.enableIdempotency) {
            this.cleanupInterval = setInterval(() => this.cleanupProcessedChunks(), 5 * 60 * 1000);
        }

        console.log('✅ STT Module initialized');
        return true;
    }

    /**
     * Toggle recording on/off
     */
    async toggleRecording() {
        console.log('🎤 toggleRecording called, current state:', {
            recording: this.recording,
            mediaRecorder: this.mediaRecorder?.state,
            audioStream: !!this.audioStream
        });
        
        if (this.recording) {
            this.stopRecording();
        } else {
            await this.startRecording();
        }
    }

    /**
     * Start audio recording
     */
    async startRecording() {
        console.log('🎤 Starting recording...');

        try {
            // Request microphone access
            this.audioStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: this.options.sampleRate,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                } 
            });
            
            console.log('🎤 Microphone stream obtained:', {
                active: this.audioStream.active,
                tracks: this.audioStream.getTracks().length,
                trackSettings: this.audioStream.getTracks()[0]?.getSettings()
            });

            // Create MediaRecorder
            const mimeType = this.getSupportedMimeType();
            this.mediaRecorder = new MediaRecorder(this.audioStream, {
                mimeType: mimeType
            });

            // Event handlers
            this.mediaRecorder.ondataavailable = (event) => {
                console.log('🎧 ondataavailable fired:', event.data.size, 'bytes');
                this.handleAudioChunk(event);
            };
            this.mediaRecorder.onstop = () => {
                console.log('🎧 onstop fired');
                this.handleRecordingStop();
            };
            this.mediaRecorder.onerror = (event) => {
                console.log('🎧 onerror fired:', event.error);
                this.handleRecordingError(event);
            };

            // Start recording with time slices
            console.log('🎧 Starting MediaRecorder with timeSlice:', this.options.timeSlice, 'ms');
            this.mediaRecorder.start(this.options.timeSlice);
            
            // WORKAROUND: Some browsers don't reliably fire ondataavailable with timeSlice
            // Manually request data as a backup
            this.chunkRequestInterval = setInterval(() => {
                if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
                    console.log('⏰ Manually requesting data from MediaRecorder...');
                    this.mediaRecorder.requestData();
                }
            }, this.options.timeSlice);

            // Update state
            this.recording = true;
            this.audioChunks = [];
            this.chunkCount = 0;
            this.sessionId = this.generateSessionId();

            // Update UI
            this.updateRecordButton(true);
            this.updateStatus('recording', 'Recording...');

            // Callback
            this.options.onStart({ timestamp: Date.now(), sessionId: this.sessionId });

            console.log('✅ Recording started');

        } catch (error) {
            console.error('❌ Failed to start recording:', error);
            this.showError(`Microphone access denied: ${error.message}`);
            this.options.onError({ error: 'start-failed', message: error.message });
        }
    }

    /**
     * Stop audio recording
     */
    stopRecording() {
        console.log('🛑 Stopping recording...', {
            recording: this.recording,
            mediaRecorderState: this.mediaRecorder?.state,
            chunkCount: this.chunkCount
        });

        if (!this.recording || !this.mediaRecorder) {
            console.warn('⚠️ No recording to stop');
            return;
        }

        // Stop MediaRecorder
        if (this.mediaRecorder.state !== 'inactive') {
            console.log('🛑 Calling mediaRecorder.stop()...');
            this.mediaRecorder.stop();
        }

        // Stop audio stream tracks
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

        // Update UI
        this.updateRecordButton(false);
        this.updateStatus('processing', 'Processing final chunk...');

        console.log('✅ Recording stopped');
    }

    /**
     * Handle audio chunk available
     */
    async handleAudioChunk(event) {
        if (event.data.size > 0) {
            console.log(`📦 Audio chunk received: ${event.data.size} bytes`);

            // Store chunk
            this.audioChunks.push(event.data);
            this.chunkCount++;

            // Send chunk to backend
            await this.sendChunkToWhisper(event.data);
        }
    }

    /**
     * Handle recording stop
     */
    handleRecordingStop() {
        console.log('🛑 Recording stopped (MediaRecorder)');
        this.options.onStop({ 
            timestamp: Date.now(), 
            sessionId: this.sessionId,
            totalChunks: this.chunkCount 
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
     * Send audio chunk to Whisper backend
     */
    async sendChunkToWhisper(blob) {
        // Generate chunk ID for idempotency
        const chunkId = `${this.sessionId}_${this.chunkCount}_${Date.now()}`;

        // Check if already processed
        if (this.options.enableIdempotency && this.processedChunks.has(chunkId)) {
            console.log(`⏭️ Skipping already processed chunk: ${chunkId}`);
            return this.processedChunks.get(chunkId);
        }

        console.log(`📤 Sending chunk to Whisper: ${chunkId}`);
        this.updateStatus('processing', `Processing chunk ${this.chunkCount}...`);

        try {
            // Convert blob to FormData
            const formData = new FormData();
            formData.append('file', blob, `audio_${chunkId}.webm`);
            formData.append('chunk_id', chunkId);
            formData.append('session_id', this.sessionId);
            formData.append('chunk_number', this.chunkCount.toString());

            // Send to backend with retry logic
            const result = await this.sendWithRetry(formData, chunkId);

            // Store result for idempotency
            if (this.options.enableIdempotency) {
                this.processedChunks.set(chunkId, result);
            }

            // Display transcript
            this.displayTranscript(result.transcript);

            // Insert into target (chat input)
            if (this.options.insertMode !== 'none') {
                this.insertTranscript(result.transcript);
            }

            // Callback (all Whisper transcripts are final, not interim)
            this.options.onTranscript({ 
                transcript: result.transcript, 
                chunkId: chunkId,
                timestamp: Date.now(),
                isFinal: true
            });

            // Update status
            this.updateStatus('success', 'Transcription successful');

            // Callback
            this.options.onChunkSent({ chunkId: chunkId, success: true });

            return result;

        } catch (error) {
            console.error(`❌ Failed to send chunk ${chunkId}:`, error);
            this.showError(`Transcription failed: ${error.message}`);
            this.options.onChunkSent({ chunkId: chunkId, success: false, error: error.message });
            throw error;
        }
    }

    /**
     * Send chunk with retry logic (exponential backoff)
     */
    async sendWithRetry(formData, chunkId, attempt = 1) {
        try {
            // Build headers
            const headers = {};
            if (this.options.apiKey) {
                headers['X-API-Key'] = this.options.apiKey;
            }

            // Send request
            const response = await fetch(this.options.whisperEndpoint, {
                method: 'POST',
                headers: headers,
                body: formData
            });

            // Handle response
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`HTTP ${response.status}: ${errorData.message || response.statusText}`);
            }

            const result = await response.json();
            console.log(`✅ Chunk ${chunkId} transcribed: "${result.transcript}"`);
            return result;

        } catch (error) {
            console.error(`❌ Attempt ${attempt} failed:`, error);

            // Check if retryable
            const isRetryable = this.isRetryableError(error);
            
            if (isRetryable && attempt < this.options.maxRetries) {
                // Calculate delay (exponential backoff)
                const delay = this.options.retryDelay * Math.pow(2, attempt - 1);
                console.log(`⏳ Retrying in ${delay}ms (attempt ${attempt + 1}/${this.options.maxRetries})...`);
                
                // Wait and retry
                await this.delay(delay);
                return this.sendWithRetry(formData, chunkId, attempt + 1);
            }

            // Max retries exceeded or non-retryable error
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
            'TypeError: Failed to fetch',
            'HTTP 500',
            'HTTP 502',
            'HTTP 503',
            'HTTP 504'
        ];

        return retryableErrors.some(msg => error.message.includes(msg));
    }

    /**
     * Display transcript in transcript display area
     */
    displayTranscript(transcript) {
        if (!this.transcriptDisplay) return;

        // Create transcript entry
        const entry = document.createElement('div');
        entry.className = 'stt-transcript-entry stt-fade-in';
        
        const timestamp = new Date().toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
        });

        entry.innerHTML = `
            <span class="stt-transcript-time">${timestamp}</span>
            <span class="stt-transcript-text">${transcript}</span>
        `;

        this.transcriptDisplay.appendChild(entry);

        // Auto-scroll
        if (this.options.autoScroll) {
            this.transcriptDisplay.scrollTop = this.transcriptDisplay.scrollHeight;
        }
    }

    /**
     * Insert transcript into target element (chat input)
     */
    insertTranscript(transcript) {
        if (!this.insertTarget) return;

        if (this.options.insertMode === 'append') {
            // Append to existing text
            const currentText = this.insertTarget.value || '';
            const separator = currentText && !currentText.endsWith(' ') ? ' ' : '';
            this.insertTarget.value = currentText + separator + transcript;
        } else if (this.options.insertMode === 'replace') {
            // Replace existing text
            this.insertTarget.value = transcript;
        }

        // Trigger input event (for frameworks)
        this.insertTarget.dispatchEvent(new Event('input', { bubbles: true }));

        // Focus input
        this.insertTarget.focus();
    }

    /**
     * Update record button appearance
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

        // Auto-hide after success/error
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
        this.showToast(message, 'error');
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `stt-toast stt-toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('stt-toast-fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Get supported MIME type for MediaRecorder
     */
    getSupportedMimeType() {
        const types = [
            'audio/webm',
            'audio/webm;codecs=opus',
            'audio/ogg;codecs=opus',
            'audio/mp4'
        ];

        for (const type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
                console.log(`✅ Using MIME type: ${type}`);
                return type;
            }
        }

        console.warn('⚠️ No supported MIME type found, using default');
        return '';
    }

    /**
     * Generate unique session ID
     */
    generateSessionId() {
        return `stt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Cleanup old processed chunks (older than 5 minutes)
     */
    cleanupProcessedChunks() {
        const now = Date.now();
        const maxAge = 5 * 60 * 1000; // 5 minutes

        for (const [chunkId, result] of this.processedChunks.entries()) {
            // Extract timestamp from chunk ID
            const parts = chunkId.split('_');
            const timestamp = parseInt(parts[parts.length - 1]);

            if (now - timestamp > maxAge) {
                this.processedChunks.delete(chunkId);
            }
        }

        if (this.processedChunks.size > 0) {
            console.log(`🧹 Cleaned up old chunks. Remaining: ${this.processedChunks.size}`);
        }
    }

    /**
     * Clear transcript display
     */
    clearTranscript() {
        if (this.transcriptDisplay) {
            this.transcriptDisplay.innerHTML = '';
        }
    }

    /**
     * Delay helper
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Get current state
     */
    getState() {
        return {
            recording: this.recording,
            processing: this.processing,
            sessionId: this.sessionId,
            chunkCount: this.chunkCount,
            processedChunksCount: this.processedChunks.size,
            options: { ...this.options }
        };
    }

    /**
     * Destroy module and cleanup
     */
    destroy() {
        console.log('🧹 Destroying STT Module...');

        // Stop recording if active
        if (this.recording) {
            this.stopRecording();
        }

        // Clear idempotency cleanup interval
        if (this.cleanupInterval) {
            clearInterval(this.cleanupInterval);
            this.cleanupInterval = null;
        }

        // Clear processed chunks
        this.processedChunks.clear();

        // Remove DOM references
        this.recordButton = null;
        this.transcriptDisplay = null;
        this.statusIndicator = null;
        this.insertTarget = null;

        console.log('✅ STT Module destroyed');
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = STTModule;
}

// Global window access
window.STTModule = STTModule;
