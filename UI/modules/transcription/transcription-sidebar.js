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
        
        console.log('[TRANSCRIPTION SIDEBAR] Controller initialized');
    }

    /**
     * Initialize sidebar - load settings, check support, initialize modules
     */
    async init() {
        console.log('[TRANSCRIPTION SIDEBAR] Initializing...');

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
        // Check if modules are available globally
        if (typeof STTModule !== 'undefined') {
            const settings = this.getSTTSettings();
            
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
            
            console.log('[TRANSCRIPTION SIDEBAR] STT module initialized');
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
     * Switch tabs
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
     * Toggle recording
     */
    toggleRecording() {
        if (!this.sttModule) {
            alert('STT module not initialized');
            return;
        }

        if (this.sttModule.recording) {
            this.sttModule.stopRecording();
        } else {
            this.sttModule.startRecording();
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
    }

    handleSTTTranscript(event) {
        console.log('[TRANSCRIPTION SIDEBAR] STT transcript received:', event.transcript);
        
        // Update UI
        document.getElementById('stt-state').textContent = 'Complete';
        document.getElementById('stt-state').style.color = '#10b981';

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
     * Settings management
     */
    getSTTSettings() {
        return {
            whisperEndpoint: document.getElementById('transcription-whisper-endpoint')?.value || 'http://localhost:3001/api/v1/transcribe',
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
