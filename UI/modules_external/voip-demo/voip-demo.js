/**
 * FILE: UI/modules_external/voip-demo/voip-demo.js
 * PURPOSE: VoIP demonstration module using WebRTC and AI transcription
 * 
 * ARCHITECTURE:
 * - Uses CapabilityProvider for WebRTC, WebSocket, AI
 * - Demonstrates real-time audio streaming
 * - Shows AI-powered transcription
 * - Simple call management interface
 * 
 * CAPABILITIES USED:
 * - WebRTC: Audio streaming
 * - WebSocket: Signaling
 * - AI: Speech-to-text transcription
 * - Media: Audio recording
 * - Storage: Call history caching
 * 
 * DEPENDENCIES:
 * - capability-provider.js (provides all features)
 * - module_loader.js (loads module)
 * 
 * LAST MODIFIED: 2025-11-29 - Initial VoIP demo implementation
 */

// BaseModule polyfill (required since module-base.js is not globally loaded)
class BaseModule {
    constructor(moduleId) {
        this.moduleId = moduleId;
        this.manifest = null;
        this.backendUrl = window.API_BASE_URL || 'http://localhost:5001';
        console.log(`✅ BaseModule constructor - moduleId: ${moduleId}`);
    }

    async initialize() {
        console.log(`✅ BaseModule.initialize() called for ${this.moduleId}`);
        try {
            const response = await fetch(`${this.backendUrl}/api/modules/${this.moduleId}`);
            if (response.ok) {
                this.manifest = await response.json();
                console.log(`✅ Manifest loaded for ${this.moduleId}:`, this.manifest);
            }
        } catch (error) {
            console.warn(`⚠️ Failed to load manifest for ${this.moduleId}:`, error);
        }
    }
}

class VoIPDemoModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);
        this.connected = false;
        this.inCall = false;
        this.callStartTime = null;
        this.timerInterval = null;
        this.transcriptionEnabled = false;
        this.audioMuted = false;

        // Get capability providers (if available)
        this.webrtc = window.capabilityProvider?.getCapability?.('webrtc') || null;
        this.websocket = window.capabilityProvider?.getCapability?.('websocket') || null;
        this.ai = window.capabilityProvider?.getCapability?.('ai') || null;
        this.media = window.capabilityProvider?.getCapability?.('media') || null;
        this.storage = window.capabilityProvider?.getCapability?.('storage') || null;

        this.callHistory = [];
    }

    /**
     * Initialize module
     */
    async initialize() {
        console.log('[VoIPDemo] Initializing VoIP Demo module...');

        // Wait for capability provider
        if (!window.capabilityProvider.initialized) {
            console.log('[VoIPDemo] Waiting for capability provider...');
            await new Promise(resolve => setTimeout(resolve, 500));
        }

        // Setup event listeners
        this.setupEventListeners();

        // Load call history from storage
        this.loadCallHistory();

        console.log('[VoIPDemo] ✅ Module initialized');
    }

    /**
     * Setup event listeners for UI
     */
    setupEventListeners() {
        // Dashboard controls
        document.getElementById('voip-connect')?.addEventListener('click', () => this.connect());
        document.getElementById('voip-start-call')?.addEventListener('click', () => this.startCall());
        document.getElementById('voip-end-call')?.addEventListener('click', () => this.endCall());
        document.getElementById('voip-mute-audio')?.addEventListener('click', () => this.toggleMute());
        document.getElementById('voip-toggle-transcription')?.addEventListener('click', () => this.toggleTranscription());
        document.getElementById('voip-test-audio')?.addEventListener('click', () => this.testAudio());

        // Sidebar controls
        document.getElementById('voip-sidebar-start-call')?.addEventListener('click', () => this.startCall());
        document.getElementById('voip-sidebar-view-dashboard')?.addEventListener('click', () => this.openDashboard());
        document.getElementById('voip-sidebar-settings')?.addEventListener('click', () => this.openSettings());

        console.log('[VoIPDemo] Event listeners setup complete');
    }

    /**
     * Connect to VoIP server
     */
    async connect() {
        console.log('[VoIPDemo] Connecting to VoIP server...');

        try {
            // Connect WebSocket for signaling
            this.websocket.connect(
                this.moduleId,
                (message) => this.handleSignalingMessage(message),
                (error) => this.handleConnectionError(error)
            );

            // Initialize WebRTC peer connection
            const pc = await this.webrtc.initializePeerConnection(this.moduleId);

            if (!pc) {
                throw new Error('Failed to initialize peer connection');
            }

            // Get user media (audio only)
            const stream = await this.webrtc.getUserMedia(this.moduleId, { audio: true, video: false });

            // Add media tracks to peer connection
            this.webrtc.addMediaTracks(this.moduleId, stream);

            // Update UI
            this.updateConnectionStatus(true);
            this.connected = true;

            console.log('[VoIPDemo] ✅ Connected successfully');

            // Show success notification
            this.showNotification('Connected to VoIP server', 'success');

        } catch (error) {
            console.error('[VoIPDemo] Connection failed:', error);
            this.showNotification('Connection failed: ' + error.message, 'error');
        }
    }

    /**
     * Start call
     */
    async startCall() {
        if (!this.connected) {
            this.showNotification('Please connect to server first', 'warning');
            return;
        }

        if (this.inCall) {
            this.showNotification('Already in a call', 'warning');
            return;
        }

        console.log('[VoIPDemo] Starting call...');

        try {
            // Create WebRTC offer
            const offer = await this.webrtc.createOffer(this.moduleId);

            // Send offer through signaling
            this.websocket.send(this.moduleId, {
                type: 'call-offer',
                offer: offer
            });

            // Update state
            this.inCall = true;
            this.callStartTime = Date.now();

            // Start call timer
            this.startCallTimer();

            // Start audio level monitoring
            this.startAudioLevelMonitoring();

            // Update UI
            this.updateCallStatus('In Call');
            const startBtn = document.getElementById('voip-start-call');
            const endBtn = document.getElementById('voip-end-call');
            const muteBtn = document.getElementById('voip-mute-audio');
            const transcriptBtn = document.getElementById('voip-toggle-transcription');

            if (startBtn) startBtn.disabled = true;
            if (endBtn) endBtn.disabled = false;
            if (muteBtn) muteBtn.disabled = false;
            if (transcriptBtn) transcriptBtn.disabled = false;

            console.log('[VoIPDemo] ✅ Call started');
            this.showNotification('Call started', 'success');

        } catch (error) {
            console.error('[VoIPDemo] Failed to start call:', error);
            this.showNotification('Failed to start call', 'error');
        }
    }

    /**
     * End call
     */
    endCall() {
        if (!this.inCall) return;

        console.log('[VoIPDemo] Ending call...');

        // Stop call timer
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }

        // Calculate call duration
        const duration = Date.now() - this.callStartTime;

        // Save to call history
        this.addToCallHistory({
            timestamp: new Date().toISOString(),
            duration: Math.floor(duration / 1000),
            status: 'completed'
        });

        // Update state
        this.inCall = false;
        this.callStartTime = null;

        // Update UI
        this.updateCallStatus('Call Ended');
        const startBtn = document.getElementById('voip-start-call');
        const endBtn = document.getElementById('voip-end-call');
        const muteBtn = document.getElementById('voip-mute-audio');
        const transcriptBtn = document.getElementById('voip-toggle-transcription');
        const timerEl = document.getElementById('voip-call-timer');

        if (startBtn) startBtn.disabled = false;
        if (endBtn) endBtn.disabled = true;
        if (muteBtn) muteBtn.disabled = true;
        if (transcriptBtn) transcriptBtn.disabled = true;
        if (timerEl) timerEl.style.display = 'none';

        // Stop transcription if enabled
        if (this.transcriptionEnabled) {
            this.toggleTranscription();
        }

        console.log('[VoIPDemo] ✅ Call ended');
        this.showNotification('Call ended', 'info');
    }

    /**
     * Toggle audio mute
     */
    toggleMute() {
        this.audioMuted = !this.audioMuted;

        const btn = document.getElementById('voip-mute-audio');
        if (this.audioMuted) {
            btn.innerHTML = '<i class="fas fa-microphone-slash"></i> Unmute';
            btn.classList.add('muted');
        } else {
            btn.innerHTML = '<i class="fas fa-microphone"></i> Mute';
            btn.classList.remove('muted');
        }

        console.log(`[VoIPDemo] Audio ${this.audioMuted ? 'muted' : 'unmuted'}`);
    }

    /**
     * Toggle transcription
     */
    async toggleTranscription() {
        this.transcriptionEnabled = !this.transcriptionEnabled;

        const outputDiv = document.getElementById('voip-transcription-output');
        const btn = document.getElementById('voip-toggle-transcription');

        if (this.transcriptionEnabled) {
            outputDiv.style.display = 'block';
            btn.innerHTML = '<i class="fas fa-eye-slash"></i> Hide';

            // Start transcription
            this.startTranscription();
            console.log('[VoIPDemo] Transcription enabled');

        } else {
            outputDiv.style.display = 'none';
            btn.innerHTML = '<i class="fas fa-eye"></i> Show';
            console.log('[VoIPDemo] Transcription disabled');
        }
    }

    /**
     * Start real-time transcription
     */
    async startTranscription() {
        // Start audio recording for transcription
        try {
            const recorder = await this.media.startAudioRecording(this.moduleId, { audio: true });

            // Process audio chunks for transcription
            setInterval(async () => {
                if (!this.transcriptionEnabled) return;

                // Get recorded audio
                const audioBlob = this.media.stopAudioRecording(this.moduleId);

                if (!audioBlob) return;

                // Send to AI for transcription
                const text = await this.ai.speechToText(this.moduleId, audioBlob);

                if (text) {
                    this.appendTranscription(text);
                }

                // Restart recording for next chunk
                await this.media.startAudioRecording(this.moduleId, { audio: true });

            }, 5000); // Transcribe every 5 seconds

        } catch (error) {
            console.error('[VoIPDemo] Transcription error:', error);
            this.showNotification('Transcription unavailable', 'warning');
        }
    }

    /**
     * Append transcription text
     */
    appendTranscription(text) {
        const outputDiv = document.querySelector('#voip-transcription-output .transcription-content');

        // Remove placeholder
        const placeholder = outputDiv.querySelector('.placeholder-text');
        if (placeholder) {
            placeholder.remove();
        }

        // Add transcription line
        const line = document.createElement('p');
        line.className = 'transcription-line';
        line.innerHTML = `<span class="timestamp">[${new Date().toLocaleTimeString()}]</span> ${text}`;
        outputDiv.appendChild(line);

        // Auto-scroll to bottom
        outputDiv.scrollTop = outputDiv.scrollHeight;
    }

    /**
     * Start call timer
     */
    startCallTimer() {
        const timerDiv = document.getElementById('voip-call-timer');
        const displaySpan = document.getElementById('voip-timer-display');

        timerDiv.style.display = 'block';

        this.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.callStartTime) / 1000);
            const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
            const seconds = (elapsed % 60).toString().padStart(2, '0');
            displaySpan.textContent = `${minutes}:${seconds}`;
        }, 1000);
    }

    /**
     * Start audio level monitoring
     */
    startAudioLevelMonitoring() {
        // Simulate audio level (in production, get from actual audio stream)
        setInterval(() => {
            if (!this.inCall) return;

            const level = Math.random() * 100; // 0-100
            const levelDiv = document.getElementById('voip-audio-level');
            if (levelDiv) {
                levelDiv.style.width = level + '%';
            }
        }, 100);
    }

    /**
     * Test audio playback
     */
    async testAudio() {
        console.log('[VoIPDemo] Testing audio...');

        // Play a test tone
        const audioContext = new AudioContext();
        const oscillator = audioContext.createOscillator();
        oscillator.type = 'sine';
        oscillator.frequency.value = 440; // A note
        oscillator.connect(audioContext.destination);
        oscillator.start();

        setTimeout(() => {
            oscillator.stop();
            this.showNotification('Audio test complete', 'info');
        }, 1000);
    }

    /**
     * Handle signaling messages
     */
    handleSignalingMessage(message) {
        console.log('[VoIPDemo] Received signaling message:', message);

        const data = JSON.parse(message);

        switch (data.type) {
            case 'call-answer':
                this.webrtc.setRemoteDescription(this.moduleId, data.answer);
                break;
            case 'ice-candidate':
                // Handle ICE candidate
                break;
            case 'call-ended':
                this.endCall();
                break;
        }
    }

    /**
     * Handle connection error
     */
    handleConnectionError(error) {
        console.error('[VoIPDemo] Connection error:', error);
        this.updateConnectionStatus(false);
        this.showNotification('Connection error', 'error');
    }

    /**
     * Update connection status UI
     */
    updateConnectionStatus(connected) {
        const statusDot = document.querySelector('#voip-connection-status .status-dot');
        const statusText = document.querySelector('#voip-connection-status .status-text');
        const sidebarStatus = document.getElementById('voip-sidebar-status');

        if (connected) {
            statusDot?.classList.remove('disconnected');
            statusDot?.classList.add('connected');
            if (statusText) statusText.textContent = 'Connected';
            if (sidebarStatus) sidebarStatus.textContent = 'Connected';

            // Enable call button
            const startBtn = document.getElementById('voip-start-call');
            if (startBtn) startBtn.disabled = false;
            document.getElementById('voip-sidebar-start-call')?.setAttribute('disabled', false);

        } else {
            statusDot?.classList.remove('connected');
            statusDot?.classList.add('disconnected');
            if (statusText) statusText.textContent = 'Disconnected';
            if (sidebarStatus) sidebarStatus.textContent = 'Disconnected';

            // Disable call button
            const startBtn = document.getElementById('voip-start-call');
            if (startBtn) startBtn.disabled = true;
            document.getElementById('voip-sidebar-start-call')?.setAttribute('disabled', true);
        }
    }

    /**
     * Update call status UI
     */
    updateCallStatus(status) {
        const statusDiv = document.querySelector('#voip-call-status .status-indicator span');
        if (statusDiv) {
            statusDiv.textContent = status;
        }
    }

    /**
     * Load call history from storage
     */
    loadCallHistory() {
        const history = this.storage.getLocal(this.moduleId, 'call_history');
        if (history) {
            this.callHistory = history;
            this.renderCallHistory();
        }
    }

    /**
     * Add to call history
     */
    addToCallHistory(call) {
        this.callHistory.unshift(call);
        if (this.callHistory.length > 10) {
            this.callHistory = this.callHistory.slice(0, 10);
        }

        // Save to storage
        this.storage.setLocal(this.moduleId, 'call_history', this.callHistory);

        // Update UI
        this.renderCallHistory();
    }

    /**
     * Render call history
     */
    renderCallHistory() {
        const historyDiv = document.getElementById('voip-call-history');
        const sidebarList = document.getElementById('voip-sidebar-call-list');

        if (!historyDiv) return;

        if (this.callHistory.length === 0) {
            historyDiv.innerHTML = '<p class="placeholder-text">No call history yet</p>';
            if (sidebarList) sidebarList.innerHTML = '<p class="placeholder-text">No recent calls</p>';
            return;
        }

        // Render full history in dashboard
        historyDiv.innerHTML = this.callHistory.map(call => `
            <div class="call-history-item">
                <div class="call-icon">
                    <i class="fas fa-phone"></i>
                </div>
                <div class="call-info">
                    <div class="call-time">${new Date(call.timestamp).toLocaleString()}</div>
                    <div class="call-duration">${call.duration} seconds</div>
                </div>
                <div class="call-status ${call.status}">${call.status}</div>
            </div>
        `).join('');

        // Render compact list in sidebar
        if (sidebarList) {
            sidebarList.innerHTML = this.callHistory.slice(0, 5).map(call => `
                <div class="call-item-compact">
                    <i class="fas fa-phone"></i>
                    <span>${new Date(call.timestamp).toLocaleTimeString()}</span>
                    <span>${call.duration}s</span>
                </div>
            `).join('');
        }

        // Update active calls count
        const activeCount = this.inCall ? 1 : 0;
        const countSpan = document.getElementById('voip-active-calls-count');
        if (countSpan) {
            countSpan.textContent = activeCount;
        }
    }

    /**
     * Open dashboard
     */
    openDashboard() {
        // Use module loader to open dashboard
        if (window.moduleLoader) {
            window.moduleLoader.openModule(this.moduleId);
        }
    }

    /**
     * Open settings
     */
    openSettings() {
        this.showNotification('Settings coming soon', 'info');
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        console.log(`[VoIPDemo] ${type.toUpperCase()}: ${message}`);

        // In production, use actual notification system
        // For now, use console
    }

    /**
     * Cleanup on module unload
     */
    destroy() {
        console.log('[VoIPDemo] Cleaning up...');

        // End call if active
        if (this.inCall) {
            this.endCall();
        }

        // Disconnect
        if (this.connected) {
            this.websocket.disconnect(this.moduleId);
            this.webrtc.closeConnection(this.moduleId);
        }

        console.log('[VoIPDemo] ✅ Cleanup complete');
    }
}

// Register module (backward compatibility)
if (typeof window !== 'undefined') {
    if (!window.ModuleRegistry) {
        window.ModuleRegistry = {};
    }
    window.ModuleRegistry['voip-demo'] = VoIPDemoModule;
}

console.log('[VoIPDemo] ✅ Module script loaded');

// ES6 Export
export default VoIPDemoModule;
