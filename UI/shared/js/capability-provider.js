/**
 * FILE: UI/shared/js/capability-provider.js
 * PURPOSE: Centralized capability provider system for module extended features
 * 
 * ARCHITECTURE:
 * - Provides WebSocket, WebRTC, AI, Media capabilities to modules
 * - Modules declare what they need in manifest
 * - System provides infrastructure automatically
 * - No need for modules to implement low-level protocols
 * 
 * CAPABILITIES PROVIDED:
 * 1. Communication: REST, WebSocket, WebRTC, SSE
 * 2. Data Modes: Real-time, Batch, Streaming
 * 3. AI/ML: Inference, Embeddings, STT, TTS
 * 4. Media: Audio, Video, File handling
 * 5. Storage: Local, Database, Object storage, Cache
 * 
 * EXPORTS:
 * - CapabilityProvider (singleton)
 * - getCapability(type) - Get capability provider
 * - registerModule(moduleId, manifest) - Register module capabilities
 * 
 * USED BY:
 * - module_loader.js (registers modules)
 * - Individual modules (request capabilities)
 * 
 * LAST MODIFIED: 2025-11-29 - Initial capability provider implementation
 */

class CapabilityProvider {
    constructor() {
        if (CapabilityProvider.instance) {
            return CapabilityProvider.instance;
        }

        this.providers = new Map(); // capability type → provider instance
        this.moduleCapabilities = new Map(); // moduleId → registered capabilities
        this.initialized = false;

        CapabilityProvider.instance = this;
    }

    /**
     * Initialize all capability providers
     */
    async initialize() {
        if (this.initialized) {
            console.warn('[CapabilityProvider] Already initialized');
            return;
        }

        console.log('[CapabilityProvider] Initializing capability providers...');

        // Initialize core providers
        this.providers.set('websocket', new WebSocketProvider());
        this.providers.set('webrtc', new WebRTCProvider());
        this.providers.set('ai', new AIProvider());
        this.providers.set('media', new MediaProvider());
        this.providers.set('storage', new StorageProvider());

        this.initialized = true;
        console.log('[CapabilityProvider] ✅ All providers initialized');
    }

    /**
     * Register module capabilities from manifest
     * 
     * @param {string} moduleId - Module identifier
     * @param {object} manifest - Module manifest with capabilities
     */
    registerModule(moduleId, manifest) {
        console.log(`[CapabilityProvider] Registering capabilities for: ${moduleId}`);

        const capabilities = {
            communication: manifest.communication || {},
            data_modes: manifest.data_modes || {},
            ai_capabilities: manifest.ai_capabilities || {},
            media_capabilities: manifest.media_capabilities || {},
            storage: manifest.storage || {}
        };

        this.moduleCapabilities.set(moduleId, capabilities);

        // Auto-initialize required providers
        this._initializeRequiredProviders(moduleId, capabilities);

        console.log(`[CapabilityProvider] ✅ Registered ${moduleId}`);
    }

    /**
     * Initialize providers required by module
     * 
     * @param {string} moduleId
     * @param {object} capabilities
     */
    _initializeRequiredProviders(moduleId, capabilities) {
        // WebSocket provider
        if (capabilities.communication.protocols?.includes('websocket')) {
            const wsConfig = capabilities.communication.websocket;
            this.providers.get('websocket').configureForModule(moduleId, wsConfig);
        }

        // WebRTC provider
        if (capabilities.communication.protocols?.includes('webrtc')) {
            const rtcConfig = capabilities.communication.webrtc;
            this.providers.get('webrtc').configureForModule(moduleId, rtcConfig);
        }

        // AI provider
        if (capabilities.ai_capabilities?.inference?.enabled) {
            const aiConfig = capabilities.ai_capabilities.inference;
            this.providers.get('ai').configureForModule(moduleId, aiConfig);
        }

        // Media provider
        if (capabilities.media_capabilities?.audio?.enabled || 
            capabilities.media_capabilities?.video?.enabled) {
            const mediaConfig = capabilities.media_capabilities;
            this.providers.get('media').configureForModule(moduleId, mediaConfig);
        }
    }

    /**
     * Get capability provider for module
     * 
     * @param {string} type - Capability type (websocket, webrtc, ai, media, storage)
     * @returns {object} Provider instance
     */
    getCapability(type) {
        const provider = this.providers.get(type);
        if (!provider) {
            console.error(`[CapabilityProvider] Unknown capability type: ${type}`);
            return null;
        }
        return provider;
    }

    /**
     * Get module-specific capability config
     * 
     * @param {string} moduleId
     * @param {string} capabilityType
     * @returns {object} Capability configuration
     */
    getModuleCapability(moduleId, capabilityType) {
        const capabilities = this.moduleCapabilities.get(moduleId);
        if (!capabilities) {
            console.warn(`[CapabilityProvider] Module not registered: ${moduleId}`);
            return null;
        }

        return capabilities[capabilityType] || null;
    }
}

// ==================== WEBSOCKET PROVIDER ====================

class WebSocketProvider {
    constructor() {
        this.connections = new Map(); // moduleId → WebSocket connection
        this.reconnectAttempts = new Map(); // moduleId → attempt count
        this.maxReconnectAttempts = 5;
    }

    /**
     * Configure WebSocket for module
     * 
     * @param {string} moduleId
     * @param {object} config - { url, reconnect, heartbeat_interval }
     */
    configureForModule(moduleId, config) {
        console.log(`[WebSocketProvider] Configuring for ${moduleId}:`, config);

        if (!config?.url) {
            console.error('[WebSocketProvider] Missing WebSocket URL');
            return;
        }

        // Store config
        this.connections.set(moduleId, {
            config: config,
            socket: null,
            connected: false
        });
    }

    /**
     * Connect WebSocket for module
     * 
     * @param {string} moduleId
     * @param {function} onMessage - Callback for messages
     * @param {function} onError - Callback for errors
     * @returns {WebSocket} WebSocket instance
     */
    connect(moduleId, onMessage, onError) {
        const connection = this.connections.get(moduleId);
        if (!connection) {
            console.error(`[WebSocketProvider] No config for module: ${moduleId}`);
            return null;
        }

        const { config } = connection;
        const socket = new WebSocket(config.url);

        socket.onopen = () => {
            console.log(`[WebSocketProvider] ✅ Connected: ${moduleId}`);
            connection.connected = true;
            this.reconnectAttempts.set(moduleId, 0);

            // Start heartbeat if configured
            if (config.heartbeat_interval) {
                this._startHeartbeat(moduleId, socket, config.heartbeat_interval);
            }
        };

        socket.onmessage = (event) => {
            if (onMessage) onMessage(event.data);
        };

        socket.onerror = (error) => {
            console.error(`[WebSocketProvider] Error for ${moduleId}:`, error);
            if (onError) onError(error);
        };

        socket.onclose = () => {
            console.warn(`[WebSocketProvider] Disconnected: ${moduleId}`);
            connection.connected = false;

            // Auto-reconnect if enabled
            if (config.reconnect) {
                this._attemptReconnect(moduleId, onMessage, onError);
            }
        };

        connection.socket = socket;
        return socket;
    }

    /**
     * Start heartbeat ping
     */
    _startHeartbeat(moduleId, socket, interval) {
        const heartbeat = setInterval(() => {
            if (socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({ type: 'ping' }));
            } else {
                clearInterval(heartbeat);
            }
        }, interval);
    }

    /**
     * Attempt reconnection with exponential backoff
     */
    _attemptReconnect(moduleId, onMessage, onError) {
        const attempts = this.reconnectAttempts.get(moduleId) || 0;
        
        if (attempts >= this.maxReconnectAttempts) {
            console.error(`[WebSocketProvider] Max reconnect attempts reached for ${moduleId}`);
            return;
        }

        const delay = Math.min(1000 * Math.pow(2, attempts), 30000);
        console.log(`[WebSocketProvider] Reconnecting ${moduleId} in ${delay}ms...`);

        setTimeout(() => {
            this.reconnectAttempts.set(moduleId, attempts + 1);
            this.connect(moduleId, onMessage, onError);
        }, delay);
    }

    /**
     * Send message through WebSocket
     */
    send(moduleId, data) {
        const connection = this.connections.get(moduleId);
        if (!connection?.socket || !connection.connected) {
            console.error(`[WebSocketProvider] Cannot send, not connected: ${moduleId}`);
            return false;
        }

        connection.socket.send(JSON.stringify(data));
        return true;
    }

    /**
     * Disconnect WebSocket
     */
    disconnect(moduleId) {
        const connection = this.connections.get(moduleId);
        if (connection?.socket) {
            connection.socket.close();
            connection.connected = false;
        }
    }
}

// ==================== WEBRTC PROVIDER ====================

class WebRTCProvider {
    constructor() {
        this.connections = new Map(); // moduleId → RTCPeerConnection
        this.mediaStreams = new Map(); // moduleId → MediaStream
    }

    /**
     * Configure WebRTC for module
     */
    configureForModule(moduleId, config) {
        console.log(`[WebRTCProvider] Configuring for ${moduleId}:`, config);
        
        this.connections.set(moduleId, {
            config: config,
            peerConnection: null,
            localStream: null,
            remoteStream: null
        });
    }

    /**
     * Initialize peer connection
     */
    async initializePeerConnection(moduleId) {
        const connection = this.connections.get(moduleId);
        if (!connection) {
            console.error(`[WebRTCProvider] No config for: ${moduleId}`);
            return null;
        }

        const { config } = connection;
        const rtcConfig = {
            iceServers: config.ice_servers || [
                { urls: 'stun:stun.l.google.com:19302' }
            ]
        };

        const pc = new RTCPeerConnection(rtcConfig);
        connection.peerConnection = pc;

        console.log(`[WebRTCProvider] ✅ Peer connection created for ${moduleId}`);
        return pc;
    }

    /**
     * Get user media (audio/video)
     */
    async getUserMedia(moduleId, constraints) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.mediaStreams.set(moduleId, stream);
            console.log(`[WebRTCProvider] ✅ Media stream obtained for ${moduleId}`);
            return stream;
        } catch (error) {
            console.error(`[WebRTCProvider] Failed to get media for ${moduleId}:`, error);
            throw error;
        }
    }

    /**
     * Add media stream to peer connection
     */
    addMediaTracks(moduleId, stream) {
        const connection = this.connections.get(moduleId);
        if (!connection?.peerConnection) {
            console.error(`[WebRTCProvider] No peer connection for: ${moduleId}`);
            return;
        }

        stream.getTracks().forEach(track => {
            connection.peerConnection.addTrack(track, stream);
        });

        connection.localStream = stream;
        console.log(`[WebRTCProvider] ✅ Media tracks added for ${moduleId}`);
    }

    /**
     * Create offer
     */
    async createOffer(moduleId) {
        const connection = this.connections.get(moduleId);
        if (!connection?.peerConnection) {
            throw new Error('No peer connection');
        }

        const offer = await connection.peerConnection.createOffer();
        await connection.peerConnection.setLocalDescription(offer);
        return offer;
    }

    /**
     * Set remote description
     */
    async setRemoteDescription(moduleId, description) {
        const connection = this.connections.get(moduleId);
        if (!connection?.peerConnection) {
            throw new Error('No peer connection');
        }

        await connection.peerConnection.setRemoteDescription(description);
    }

    /**
     * Close connection
     */
    closeConnection(moduleId) {
        const connection = this.connections.get(moduleId);
        if (connection?.peerConnection) {
            connection.peerConnection.close();
        }

        const stream = this.mediaStreams.get(moduleId);
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            this.mediaStreams.delete(moduleId);
        }

        console.log(`[WebRTCProvider] ✅ Connection closed for ${moduleId}`);
    }
}

// ==================== AI PROVIDER ====================

class AIProvider {
    constructor() {
        this.modelEndpoints = new Map(); // model type → API endpoint
        this.activeRequests = new Map(); // moduleId → active requests
    }

    /**
     * Configure AI capabilities for module
     */
    configureForModule(moduleId, config) {
        console.log(`[AIProvider] Configuring for ${moduleId}:`, config);
        
        if (config.models) {
            config.models.forEach(model => {
                console.log(`[AIProvider] Model registered: ${model.id} (${model.type})`);
            });
        }
    }

    /**
     * Run inference
     * 
     * @param {string} moduleId
     * @param {string} modelId - Model identifier
     * @param {object} input - Input data
     * @param {boolean} streaming - Stream response?
     * @returns {Promise} Inference result
     */
    async runInference(moduleId, modelId, input, streaming = false) {
        console.log(`[AIProvider] Running inference for ${moduleId}, model: ${modelId}`);

        try {
            // Use AI Agents platform inference endpoint
            const response = await fetch('/api/agent/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: input.text || input.prompt,
                    user_id: window.currentUserId || 14,
                    model_id: modelId,
                    streaming: streaming
                })
            });

            if (!response.ok) {
                throw new Error(`Inference failed: ${response.statusText}`);
            }

            const result = await response.json();
            console.log(`[AIProvider] ✅ Inference complete for ${moduleId}`);
            return result;

        } catch (error) {
            console.error(`[AIProvider] Inference error for ${moduleId}:`, error);
            throw error;
        }
    }

    /**
     * Speech-to-text
     */
    async speechToText(moduleId, audioBlob, language = 'en-US') {
        console.log(`[AIProvider] STT for ${moduleId}, language: ${language}`);

        const formData = new FormData();
        formData.append('audio', audioBlob);
        formData.append('language', language);

        try {
            const response = await fetch('/api/ai/speech-to-text', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`STT failed: ${response.statusText}`);
            }

            const result = await response.json();
            return result.text;

        } catch (error) {
            console.error(`[AIProvider] STT error:`, error);
            throw error;
        }
    }

    /**
     * Text-to-speech
     */
    async textToSpeech(moduleId, text, voice = 'default') {
        console.log(`[AIProvider] TTS for ${moduleId}`);

        try {
            const response = await fetch('/api/ai/text-to-speech', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, voice })
            });

            if (!response.ok) {
                throw new Error(`TTS failed: ${response.statusText}`);
            }

            const audioBlob = await response.blob();
            return audioBlob;

        } catch (error) {
            console.error(`[AIProvider] TTS error:`, error);
            throw error;
        }
    }
}

// ==================== MEDIA PROVIDER ====================

class MediaProvider {
    constructor() {
        this.recorders = new Map(); // moduleId → MediaRecorder
        this.recordings = new Map(); // moduleId → Blob[]
    }

    /**
     * Configure media capabilities
     */
    configureForModule(moduleId, config) {
        console.log(`[MediaProvider] Configuring for ${moduleId}:`, config);
    }

    /**
     * Start audio recording
     */
    async startAudioRecording(moduleId, constraints = { audio: true }) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            const recorder = new MediaRecorder(stream);
            const chunks = [];

            recorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    chunks.push(event.data);
                }
            };

            recorder.onstop = () => {
                const blob = new Blob(chunks, { type: 'audio/webm' });
                this.recordings.set(moduleId, blob);
            };

            this.recorders.set(moduleId, recorder);
            recorder.start();

            console.log(`[MediaProvider] ✅ Recording started for ${moduleId}`);
            return recorder;

        } catch (error) {
            console.error(`[MediaProvider] Recording failed:`, error);
            throw error;
        }
    }

    /**
     * Stop recording
     */
    stopAudioRecording(moduleId) {
        const recorder = this.recorders.get(moduleId);
        if (!recorder) {
            console.warn(`[MediaProvider] No recorder for: ${moduleId}`);
            return null;
        }

        recorder.stop();
        recorder.stream.getTracks().forEach(track => track.stop());

        console.log(`[MediaProvider] ✅ Recording stopped for ${moduleId}`);
        return this.recordings.get(moduleId);
    }

    /**
     * Play audio
     */
    playAudio(audioBlob) {
        const url = URL.createObjectURL(audioBlob);
        const audio = new Audio(url);
        audio.play();
        return audio;
    }
}

// ==================== STORAGE PROVIDER ====================

class StorageProvider {
    constructor() {
        this.caches = new Map(); // moduleId → cache Map
    }

    /**
     * Store in local storage
     */
    setLocal(moduleId, key, value) {
        const storageKey = `module_${moduleId}_${key}`;
        localStorage.setItem(storageKey, JSON.stringify(value));
    }

    /**
     * Get from local storage
     */
    getLocal(moduleId, key) {
        const storageKey = `module_${moduleId}_${key}`;
        const value = localStorage.getItem(storageKey);
        return value ? JSON.parse(value) : null;
    }

    /**
     * Store in cache (in-memory)
     */
    setCache(moduleId, key, value, ttl = 300) {
        if (!this.caches.has(moduleId)) {
            this.caches.set(moduleId, new Map());
        }

        const cache = this.caches.get(moduleId);
        cache.set(key, {
            value: value,
            expires: Date.now() + (ttl * 1000)
        });
    }

    /**
     * Get from cache
     */
    getCache(moduleId, key) {
        const cache = this.caches.get(moduleId);
        if (!cache) return null;

        const item = cache.get(key);
        if (!item) return null;

        // Check expiry
        if (Date.now() > item.expires) {
            cache.delete(key);
            return null;
        }

        return item.value;
    }
}

// ==================== GLOBAL INSTANCE ====================

// Create global singleton
window.capabilityProvider = new CapabilityProvider();

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.capabilityProvider.initialize();
    });
} else {
    window.capabilityProvider.initialize();
}

console.log('[CapabilityProvider] ✅ Module loaded and ready');
