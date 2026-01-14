/**
 * FILE: UI/modules/transcription/tts-module.js
 * PURPOSE: Text-to-Speech module with streaming transcript display
 * 
 * DEPENDENCIES:
 * - Web Speech API (speechSynthesis) - Browser native TTS
 * 
 * EXPORTS:
 * - TTSModule class - Main TTS controller with streaming transcript
 * 
 * USED BY:
 * - business-ai-platform-v2.html (main AI chat interface)
 * 
 * RELATED FILES:
 * - tts-module.css - Styling for transcript container
 * 
 * NOTES:
 * - Inspired by V7_MustCare voiceModule.js but for TTS only
 * - Transcript streams to separate container (not chat input)
 * - Uses Web Speech API for native TTS
 * - Supports pause/resume, speed control, voice selection
 * - Visual feedback similar to V7_MustCare (processing/success/error states)
 * 
 * LAST MODIFIED: 2025-01-XX - Initial creation for AI_agents project
 */

class TTSModule {
    constructor(options = {}) {
        this.options = {
            // TTS Settings
            rate: options.rate || 1.0,          // Speech speed (0.1 - 10)
            pitch: options.pitch || 1.0,        // Voice pitch (0 - 2)
            volume: options.volume || 1.0,      // Volume (0 - 1)
            voice: options.voice || null,       // SpeechSynthesisVoice object
            language: options.language || 'en-US',
            
            // Transcript Display
            transcriptContainer: options.transcriptContainer || 'tts-transcript-container',
            autoScroll: options.autoScroll !== false,
            showTimestamps: options.showTimestamps !== false,
            
            // Visual Feedback
            statusIndicator: options.statusIndicator || 'tts-status-indicator',
            
            // Chunking for streaming effect
            chunkSize: options.chunkSize || 50,  // Characters per visual chunk
            chunkDelay: options.chunkDelay || 30, // ms between chunks
            
            // Callbacks
            onStart: options.onStart || (() => {}),
            onEnd: options.onEnd || (() => {}),
            onError: options.onError || (() => {}),
            onPause: options.onPause || (() => {}),
            onResume: options.onResume || (() => {})
        };

        // State
        this.synthesis = window.speechSynthesis;
        this.currentUtterance = null;
        this.speaking = false;
        this.paused = false;
        this.transcript = [];
        this.currentChunkIndex = 0;
        
        // DOM Elements
        this.transcriptContainer = null;
        this.statusIndicator = null;
        
        // Verify browser support
        this.initialize();
    }

    /**
     * Initialize TTS module and check browser support
     */
    initialize() {
        console.log('🎙️ Initializing TTS Module...');

        // Check browser support
        if (!window.speechSynthesis) {
            console.error('❌ Web Speech API (speechSynthesis) not supported in this browser');
            this.showError('Text-to-Speech not supported in this browser');
            return false;
        }

        // Get DOM elements
        this.transcriptContainer = document.getElementById(this.options.transcriptContainer);
        this.statusIndicator = document.getElementById(this.options.statusIndicator);

        if (!this.transcriptContainer) {
            console.error(`❌ Transcript container not found: ${this.options.transcriptContainer}`);
            return false;
        }

        // Load available voices
        this.loadVoices();
        
        // Listen for voice list changes (Chrome loads voices async)
        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = () => this.loadVoices();
        }

        console.log('✅ TTS Module initialized');
        return true;
    }

    /**
     * Load available voices and set default
     */
    loadVoices() {
        const voices = this.synthesis.getVoices();
        console.log(`🔍 Found ${voices.length} voices`);

        if (voices.length === 0) {
            console.warn('⚠️ No voices available yet');
            return;
        }

        // Set default voice if not already set
        if (!this.options.voice) {
            // Prefer Google UK English Female if available
            const preferredVoice = voices.find(v => 
                v.name.includes('Google') && 
                v.lang.startsWith('en') && 
                v.name.toLowerCase().includes('female')
            );

            this.options.voice = preferredVoice || voices.find(v => v.lang === this.options.language) || voices[0];
            console.log(`✅ Default voice: ${this.options.voice.name}`);
        }
    }

    /**
     * Speak text with streaming transcript display
     * @param {string} text - Text to speak
     * @param {object} options - Override default options
     */
    async speak(text, options = {}) {
        if (!text || text.trim() === '') {
            console.warn('⚠️ No text to speak');
            return;
        }

        console.log(`📢 Speaking: "${text.substring(0, 50)}${text.length > 50 ? '...' : ''}"`);

        // Stop any ongoing speech
        this.stop();

        // Merge options
        const speakOptions = { ...this.options, ...options };

        // Create utterance
        this.currentUtterance = new SpeechSynthesisUtterance(text);
        this.currentUtterance.voice = speakOptions.voice;
        this.currentUtterance.rate = speakOptions.rate;
        this.currentUtterance.pitch = speakOptions.pitch;
        this.currentUtterance.volume = speakOptions.volume;
        this.currentUtterance.lang = speakOptions.language;

        // Set up event handlers
        this.currentUtterance.onstart = () => this.handleStart(text);
        this.currentUtterance.onend = () => this.handleEnd();
        this.currentUtterance.onerror = (event) => this.handleError(event);
        this.currentUtterance.onpause = () => this.handlePause();
        this.currentUtterance.onresume = () => this.handleResume();
        this.currentUtterance.onboundary = (event) => this.handleBoundary(event);

        // Start streaming transcript display
        this.startTranscriptStream(text);

        // Speak
        this.synthesis.speak(this.currentUtterance);
        this.speaking = true;
    }

    /**
     * Start streaming transcript display (visual chunking effect)
     */
    async startTranscriptStream(text) {
        // Create transcript entry
        const entry = this.createTranscriptEntry(text);
        this.transcript.push(entry);
        this.transcriptContainer.appendChild(entry.element);

        // Get content element for streaming
        const contentElement = entry.element.querySelector('.tts-transcript-content');
        contentElement.textContent = ''; // Clear initial text

        // Stream text in chunks for visual effect
        const chunks = this.chunkText(text, this.options.chunkSize);
        
        for (let i = 0; i < chunks.length; i++) {
            contentElement.textContent += chunks[i];
            
            // Auto-scroll if enabled
            if (this.options.autoScroll) {
                this.scrollToBottom();
            }

            // Delay between chunks (unless it's the last chunk)
            if (i < chunks.length - 1) {
                await this.delay(this.options.chunkDelay);
            }
        }
    }

    /**
     * Chunk text into smaller pieces for streaming effect
     */
    chunkText(text, size) {
        const chunks = [];
        for (let i = 0; i < text.length; i += size) {
            chunks.push(text.slice(i, i + size));
        }
        return chunks;
    }

    /**
     * Create transcript entry element
     */
    createTranscriptEntry(text) {
        const entry = document.createElement('div');
        entry.className = 'tts-transcript-entry tts-processing';
        
        const timestamp = new Date();
        const timeString = timestamp.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
        });

        entry.innerHTML = `
            <div class="tts-transcript-header">
                <span class="tts-transcript-icon">
                    <i class="fas fa-volume-up"></i>
                </span>
                ${this.options.showTimestamps ? `<span class="tts-transcript-time">${timeString}</span>` : ''}
                <span class="tts-transcript-status">Speaking</span>
            </div>
            <div class="tts-transcript-content">${text}</div>
            <div class="tts-transcript-actions">
                <button class="tts-action-btn tts-pause-btn" title="Pause">
                    <i class="fas fa-pause"></i>
                </button>
                <button class="tts-action-btn tts-stop-btn" title="Stop">
                    <i class="fas fa-stop"></i>
                </button>
                <button class="tts-action-btn tts-copy-btn" title="Copy text">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
        `;

        // Add event listeners to action buttons
        const pauseBtn = entry.querySelector('.tts-pause-btn');
        const stopBtn = entry.querySelector('.tts-stop-btn');
        const copyBtn = entry.querySelector('.tts-copy-btn');

        pauseBtn.addEventListener('click', () => this.togglePause());
        stopBtn.addEventListener('click', () => this.stop());
        copyBtn.addEventListener('click', () => this.copyToClipboard(text));

        return {
            element: entry,
            text: text,
            timestamp: timestamp,
            status: 'speaking'
        };
    }

    /**
     * Handle speech start event
     */
    handleStart(text) {
        console.log('📢 Speech started');
        this.speaking = true;
        this.updateStatus('speaking', 'Speaking...');
        this.options.onStart({ text, timestamp: Date.now() });
    }

    /**
     * Handle speech end event
     */
    handleEnd() {
        console.log('✅ Speech ended');
        this.speaking = false;
        this.paused = false;
        this.updateStatus('success', 'Completed');
        
        // Update last transcript entry
        if (this.transcript.length > 0) {
            const lastEntry = this.transcript[this.transcript.length - 1];
            lastEntry.element.classList.remove('tts-processing', 'tts-paused');
            lastEntry.element.classList.add('tts-success');
            lastEntry.element.querySelector('.tts-transcript-status').textContent = 'Completed';
            lastEntry.status = 'completed';
        }

        this.options.onEnd({ timestamp: Date.now() });
    }

    /**
     * Handle speech error event
     */
    handleError(event) {
        console.error('❌ Speech error:', event.error);
        this.speaking = false;
        this.updateStatus('error', `Error: ${event.error}`);
        
        // Update last transcript entry
        if (this.transcript.length > 0) {
            const lastEntry = this.transcript[this.transcript.length - 1];
            lastEntry.element.classList.remove('tts-processing', 'tts-paused');
            lastEntry.element.classList.add('tts-error');
            lastEntry.element.querySelector('.tts-transcript-status').textContent = `Error: ${event.error}`;
            lastEntry.status = 'error';
        }

        this.options.onError({ error: event.error, timestamp: Date.now() });
    }

    /**
     * Handle speech pause event
     */
    handlePause() {
        console.log('⏸️ Speech paused');
        this.paused = true;
        this.updateStatus('paused', 'Paused');
        
        // Update last transcript entry
        if (this.transcript.length > 0) {
            const lastEntry = this.transcript[this.transcript.length - 1];
            lastEntry.element.classList.add('tts-paused');
            lastEntry.element.querySelector('.tts-transcript-status').textContent = 'Paused';
            
            // Update pause button icon
            const pauseBtn = lastEntry.element.querySelector('.tts-pause-btn');
            pauseBtn.innerHTML = '<i class="fas fa-play"></i>';
            pauseBtn.title = 'Resume';
        }

        this.options.onPause({ timestamp: Date.now() });
    }

    /**
     * Handle speech resume event
     */
    handleResume() {
        console.log('▶️ Speech resumed');
        this.paused = false;
        this.updateStatus('speaking', 'Speaking...');
        
        // Update last transcript entry
        if (this.transcript.length > 0) {
            const lastEntry = this.transcript[this.transcript.length - 1];
            lastEntry.element.classList.remove('tts-paused');
            lastEntry.element.querySelector('.tts-transcript-status').textContent = 'Speaking';
            
            // Update pause button icon
            const pauseBtn = lastEntry.element.querySelector('.tts-pause-btn');
            pauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
            pauseBtn.title = 'Pause';
        }

        this.options.onResume({ timestamp: Date.now() });
    }

    /**
     * Handle word boundary events (for highlighting current word)
     */
    handleBoundary(event) {
        // Optional: Implement word highlighting during speech
        // event.charIndex, event.charLength provide position info
    }

    /**
     * Pause or resume speech
     */
    togglePause() {
        if (!this.speaking) {
            console.warn('⚠️ No speech to pause/resume');
            return;
        }

        if (this.paused) {
            console.log('▶️ Resuming speech...');
            this.synthesis.resume();
        } else {
            console.log('⏸️ Pausing speech...');
            this.synthesis.pause();
        }
    }

    /**
     * Stop speech synthesis
     */
    stop() {
        if (!this.speaking && !this.paused) {
            console.log('ℹ️ No speech to stop');
            return;
        }

        console.log('🛑 Stopping speech...');
        this.synthesis.cancel();
        this.speaking = false;
        this.paused = false;
        this.updateStatus('idle', 'Stopped');

        // Update last transcript entry if interrupted
        if (this.transcript.length > 0) {
            const lastEntry = this.transcript[this.transcript.length - 1];
            if (lastEntry.status === 'speaking' || lastEntry.status === 'paused') {
                lastEntry.element.classList.remove('tts-processing', 'tts-paused');
                lastEntry.element.classList.add('tts-stopped');
                lastEntry.element.querySelector('.tts-transcript-status').textContent = 'Stopped';
                lastEntry.status = 'stopped';
            }
        }
    }

    /**
     * Clear all transcript entries
     */
    clearTranscript() {
        console.log('🧹 Clearing transcript...');
        this.transcript = [];
        if (this.transcriptContainer) {
            this.transcriptContainer.innerHTML = '';
        }
    }

    /**
     * Update status indicator
     */
    updateStatus(status, message) {
        if (!this.statusIndicator) return;

        this.statusIndicator.className = `tts-status-indicator tts-status-${status}`;
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
     * Copy transcript text to clipboard
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            console.log('✅ Text copied to clipboard');
            this.showToast('Copied to clipboard', 'success');
        } catch (error) {
            console.error('❌ Failed to copy text:', error);
            this.showToast('Failed to copy text', 'error');
        }
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        // Simple toast implementation
        const toast = document.createElement('div');
        toast.className = `tts-toast tts-toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.add('tts-toast-fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Show error message in UI
     */
    showError(message) {
        this.updateStatus('error', message);
        this.showToast(message, 'error');
    }

    /**
     * Auto-scroll transcript container to bottom
     */
    scrollToBottom() {
        if (this.transcriptContainer) {
            this.transcriptContainer.scrollTop = this.transcriptContainer.scrollHeight;
        }
    }

    /**
     * Delay helper for async operations
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Get available voices
     */
    getVoices() {
        return this.synthesis.getVoices();
    }

    /**
     * Set voice by name or index
     */
    setVoice(voiceIdentifier) {
        const voices = this.getVoices();
        
        if (typeof voiceIdentifier === 'number') {
            // Set by index
            if (voiceIdentifier >= 0 && voiceIdentifier < voices.length) {
                this.options.voice = voices[voiceIdentifier];
                console.log(`✅ Voice set to: ${this.options.voice.name}`);
            } else {
                console.error(`❌ Voice index ${voiceIdentifier} out of range (0-${voices.length - 1})`);
            }
        } else if (typeof voiceIdentifier === 'string') {
            // Set by name
            const voice = voices.find(v => v.name.toLowerCase().includes(voiceIdentifier.toLowerCase()));
            if (voice) {
                this.options.voice = voice;
                console.log(`✅ Voice set to: ${this.options.voice.name}`);
            } else {
                console.error(`❌ Voice not found: ${voiceIdentifier}`);
            }
        }
    }

    /**
     * Set speech rate
     */
    setRate(rate) {
        if (rate >= 0.1 && rate <= 10) {
            this.options.rate = rate;
            console.log(`✅ Speech rate set to: ${rate}`);
        } else {
            console.error('❌ Rate must be between 0.1 and 10');
        }
    }

    /**
     * Set speech pitch
     */
    setPitch(pitch) {
        if (pitch >= 0 && pitch <= 2) {
            this.options.pitch = pitch;
            console.log(`✅ Speech pitch set to: ${pitch}`);
        } else {
            console.error('❌ Pitch must be between 0 and 2');
        }
    }

    /**
     * Set speech volume
     */
    setVolume(volume) {
        if (volume >= 0 && volume <= 1) {
            this.options.volume = volume;
            console.log(`✅ Speech volume set to: ${volume}`);
        } else {
            console.error('❌ Volume must be between 0 and 1');
        }
    }

    /**
     * Get current state
     */
    getState() {
        return {
            speaking: this.speaking,
            paused: this.paused,
            transcriptLength: this.transcript.length,
            options: { ...this.options }
        };
    }

    /**
     * Destroy module and cleanup
     */
    destroy() {
        console.log('🧹 Destroying TTS Module...');
        this.stop();
        this.clearTranscript();
        this.transcriptContainer = null;
        this.statusIndicator = null;
        console.log('✅ TTS Module destroyed');
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TTSModule;
}

// Global window access
window.TTSModule = TTSModule;
