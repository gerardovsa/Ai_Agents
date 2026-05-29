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

        // Audio level detection
        this.audioContext = null;
        this.audioAnalyzer = null;
        this.audioLevelInterval = null;
        this.previewStream = null; // Separate stream for pre-recording preview
        this.previewSource = null; // 'system' or 'microphone'

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
    async startRecording(source = 'sidebar', transcriptCallback = null) {
        if (this.isRecording) {
            console.warn('[SHARED STATE] Already recording');
            return;
        }

        // Route to selected live engine
        try {
            const sttStored = localStorage.getItem('transcription-stt-settings');
            const sttParsed = sttStored ? JSON.parse(sttStored) : {};
            const liveEngine = sttParsed.liveEngine || 'browser';
            if (liveEngine !== 'browser') {
                this.recordingSource = source;
                this.customTranscriptCallback = transcriptCallback;
                if (liveEngine === 'assemblyai')      return await this.startAssemblyAIRecording(source, transcriptCallback);
                if (liveEngine === 'deepgram')        return await this.startDeepgramRecording(source, transcriptCallback);
                if (liveEngine === 'openai-realtime') return await this.startOpenAIRealtimeRecording(source, transcriptCallback);
                if (liveEngine === 'speechmatics')   return await this.startSpeechmaticsRecording(source, transcriptCallback);
            }
        } catch (e) {
            console.warn('[SHARED STATE] Engine preference check failed, using browser STT:', e);
        }

        this.recordingSource = source;
        this.customTranscriptCallback = transcriptCallback; // Store custom callback for agent-specific routing
        console.log(`[SHARED STATE] Starting recording from ${source}${transcriptCallback ? ' with custom callback' : ''}...`);

        try {
            // If we already have a preview stream, use it for recording
            let audioStream = null;
            let audioSource = 'unknown';

            if (this.previewStream && this.previewSource) {
                console.log(`[SHARED STATE] Using existing preview stream (${this.previewSource})`);
                audioStream = this.previewStream;
                audioSource = this.previewSource;
            } else {
                // 🔊 PRIORITY 1: Try to capture system audio (desktop/tab audio)
                // This is what users usually want - transcribe meetings, videos, calls they're listening to

                try {
                    console.log('[SHARED STATE] Attempting to capture system audio...');
                    audioStream = await navigator.mediaDevices.getDisplayMedia({
                        video: false,
                        audio: {
                            channelCount: 1,
                            echoCancellation: true,
                            noiseSuppression: true,
                            autoGainControl: true,
                            sampleRate: 16000
                        }
                    });
                    audioSource = 'system';
                    console.log('[SHARED STATE] ✅ System audio captured (desktop/tab audio)');
                } catch (systemError) {
                    console.log('[SHARED STATE] System audio not available (user cancelled or not supported):', systemError.message);

                    // 🎤 FALLBACK: Use microphone if system audio fails
                    try {
                        console.log('[SHARED STATE] Falling back to microphone...');
                        audioStream = await navigator.mediaDevices.getUserMedia({
                            audio: {
                                channelCount: 1,
                                echoCancellation: true,
                                noiseSuppression: true,
                                autoGainControl: true,
                                sampleRate: 16000
                            }
                        });
                        audioSource = 'microphone';
                        console.log('[SHARED STATE] ✅ Microphone captured');
                    } catch (micError) {
                        console.error('[SHARED STATE] Failed to access any audio source:', micError);
                        throw new Error('No audio source available. Please allow audio access.');
                    }
                }
            } // End of if/else for preview stream check

            // Store audio stream for cleanup
            this.audioStream = audioStream;
            this.currentAudioSource = audioSource;

            // Start audio level monitoring
            this.startAudioLevelMonitoring(audioStream);

            // Reset audio chunks (no longer using MediaRecorder for Whisper)
            this.audioChunks = [];
            this.audioRecorder = null;

            // ✅ FIX: Stop any existing browser recognition before starting new one
            if (this.browserRecognition) {
                try {
                    this.browserRecognition.stop();
                    console.log('[SHARED STATE] Stopped previous browser recognition before starting new one');
                } catch (err) {
                    console.log('[SHARED STATE] No previous recognition to stop:', err.message);
                }
                // Reset to null to force recreation
                this.browserRecognition = null;
            }

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

                    // Call custom callback if provided (for agent-specific routing)
                    if (this.customTranscriptCallback) {
                        this.customTranscriptCallback(finalTranscript, interimTranscript);
                    }

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

        // Clean up AssemblyAI WebSocket if active
        if (this.assemblyWS) {
            try { this.assemblyWS.send(JSON.stringify({ type: 'Terminate' })); } catch (e) {}
            try { this.assemblyWS.close(); } catch (e) {}
            this.assemblyWS = null;
        }
        if (this.assemblyAudioProcessor) {
            const { processor, source_node, audioContext } = this.assemblyAudioProcessor;
            try { processor.disconnect(); } catch (e) {}
            try { source_node.disconnect(); } catch (e) {}
            try { audioContext.close(); } catch (e) {}
            this.assemblyAudioProcessor = null;
        }
        // Clean up Deepgram WebSocket if active
        if (this.deepgramWS) {
            try { this.deepgramWS.send(JSON.stringify({ type: 'CloseStream' })); } catch (e) {}
            try { this.deepgramWS.close(); } catch (e) {}
            this.deepgramWS = null;
        }
        if (this.deepgramAudioProcessor) {
            const { processor, source_node, audioContext } = this.deepgramAudioProcessor;
            try { processor.disconnect(); } catch (e) {}
            try { source_node.disconnect(); } catch (e) {}
            try { audioContext.close(); } catch (e) {}
            this.deepgramAudioProcessor = null;
        }
        // Clean up OpenAI Realtime WebSocket if active
        if (this.openaiRealtimeWS) {
            try { this.openaiRealtimeWS.send(JSON.stringify({ type: 'session.delete' })); } catch (e) {}
            try { this.openaiRealtimeWS.close(); } catch (e) {}
            this.openaiRealtimeWS = null;
        }
        if (this.openaiRealtimeAudioProcessor) {
            const { processor, source_node, audioContext } = this.openaiRealtimeAudioProcessor;
            try { processor.disconnect(); } catch (e) {}
            try { source_node.disconnect(); } catch (e) {}
            try { audioContext.close(); } catch (e) {}
            this.openaiRealtimeAudioProcessor = null;
        }
        // Clean up Speechmatics WebSocket if active
        if (this.speechmaticsWS) {
            try { this.speechmaticsWS.send(JSON.stringify({ message: 'EndOfStream', last_seq_no: 0 })); } catch (e) {}
            try { this.speechmaticsWS.close(); } catch (e) {}
            this.speechmaticsWS = null;
        }
        if (this.speechmaticsAudioProcessor) {
            const { processor, source_node, audioContext } = this.speechmaticsAudioProcessor;
            try { processor.disconnect(); } catch (e) {}
            try { source_node.disconnect(); } catch (e) {}
            try { audioContext.close(); } catch (e) {}
            this.speechmaticsAudioProcessor = null;
        }

        // Stop browser recognition
        if (this.browserRecognition) {
            try {
                this.browserRecognition.stop();
                console.log('[SHARED STATE] Browser recognition stopped');
            } catch (e) {
                console.error('[SHARED STATE] Failed to stop recognition:', e);
            }
        }

        // Stop recording audio stream but keep preview stream active
        if (this.audioStream) {
            try {
                this.audioStream.getTracks().forEach(track => {
                    track.stop();
                    console.log(`[SHARED STATE] Stopped ${track.kind} track (${track.label})`);
                });
                this.audioStream = null;
            } catch (e) {
                console.error('[SHARED STATE] Failed to stop audio stream:', e);
            }
        }

        // Restart preview monitoring after recording stops
        setTimeout(() => {
            if (!this.isRecording && !this.previewStream) {
                this.startAudioPreview();
            }
        }, 500);

        // Trigger onStop callback
        this.trigger('onStop');

        this.isRecording = false;
        const source = this.recordingSource;
        const audioSource = this.currentAudioSource || 'unknown';
        this.recordingSource = null;
        this.currentAudioSource = null;
        this.customTranscriptCallback = null; // Clear custom callback
        console.log(`[SHARED STATE] ✅ Recording stopped (was from ${source}, audio: ${audioSource})`);
    }

    // ✅ REMOVED: getAudioBlob (no longer using MediaRecorder/Whisper)
    // Browser Web Speech API provides transcription directly
    getAudioBlob() {
        console.warn('[SHARED STATE] getAudioBlob called but MediaRecorder removed (Browser STT only)');
        return null;
    }

    /**
     * AssemblyAI real-time streaming recording.
     * Gets a short-lived token from the backend then opens a WebSocket to
     * AssemblyAI and streams raw PCM16 chunks from the microphone.
     */
    async startAssemblyAIRecording(source, transcriptCallback) {
        console.log('[SHARED STATE] Starting AssemblyAI recording...');
        try {
            // 1. Fetch a short-lived streaming token from our backend
            const tokenResp = await fetch('/api/transcription/assemblyai-token', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` }
            });
            const tokenData = await tokenResp.json();
            if (!tokenData.token) {
                const msg = tokenData.error || 'AssemblyAI not configured for this organisation';
                this.trigger('onError', msg);
                throw new Error(msg);
            }

            // 2. Capture microphone at 16kHz
            const audioStream = await navigator.mediaDevices.getUserMedia({
                audio: { sampleRate: 16000, channelCount: 1, echoCancellation: true, noiseSuppression: true }
            });
            this.audioStream = audioStream;
            this.currentAudioSource = 'microphone';
            this.startAudioLevelMonitoring(audioStream);

            // 3. Open WebSocket to AssemblyAI
            const wsUrl = `wss://streaming.assemblyai.com/v3/ws?speech_model=u3-rt-pro&sample_rate=16000&token=${encodeURIComponent(tokenData.token)}`;
            const ws = new WebSocket(wsUrl);
            this.assemblyWS = ws;

            // 4. Stream PCM16 via ScriptProcessorNode (800 frames = 50ms at 16kHz)
            const audioCtx = new AudioContext({ sampleRate: 16000 });
            const sourceNode = audioCtx.createMediaStreamSource(audioStream);
            const processor = audioCtx.createScriptProcessor(800, 1, 1);

            processor.onaudioprocess = (e) => {
                if (!this.isRecording || ws.readyState !== WebSocket.OPEN) return;
                const float32 = e.inputBuffer.getChannelData(0);
                const int16 = new Int16Array(float32.length);
                for (let i = 0; i < float32.length; i++) {
                    int16[i] = Math.max(-32768, Math.min(32767, Math.round(float32[i] * 32767)));
                }
                ws.send(int16.buffer);
            };

            sourceNode.connect(processor);
            processor.connect(audioCtx.destination);
            this.assemblyAudioProcessor = { processor, source_node: sourceNode, audioContext: audioCtx };

            // 5. Handle WebSocket events
            ws.onopen = () => {
                console.log('[SHARED STATE] AssemblyAI WebSocket connected');
                this.isRecording = true;
                this.trigger('onStart', source);
                console.log('[SHARED STATE] ✅ AssemblyAI recording started');
            };

            ws.onmessage = (evt) => {
                try {
                    const data = JSON.parse(evt.data);
                    if (data.type === 'Turn') {
                        const text = data.transcript || '';
                        const isFinal = data.end_of_turn === true;
                        if (this.customTranscriptCallback) {
                            this.customTranscriptCallback(isFinal ? text : '', isFinal ? '' : text);
                        }
                        this.trigger('onTranscript', {
                            final: isFinal ? text : '',
                            interim: isFinal ? '' : text,
                            confidence: 0.95
                        }, source);
                    } else if (data.type === 'Begin') {
                        console.log('[SHARED STATE] AssemblyAI session started:', data.id);
                    } else if (data.type === 'Termination') {
                        console.log('[SHARED STATE] AssemblyAI session terminated. Duration:', data.session_duration_seconds, 's');
                    }
                } catch (e) {
                    console.warn('[SHARED STATE] AssemblyAI message parse error:', e);
                }
            };

            ws.onerror = (e) => {
                console.error('[SHARED STATE] AssemblyAI WebSocket error:', e);
                this.trigger('onError', 'AssemblyAI connection error');
            };

            ws.onclose = (e) => {
                console.log('[SHARED STATE] AssemblyAI WebSocket closed. Code:', e.code);
                if (this.isRecording) {
                    this.stopRecording();
                }
            };

        } catch (error) {
            console.error('[SHARED STATE] AssemblyAI recording failed:', error);
            this.trigger('onError', error.message);
            throw error;
        }
    }

    /**
     * Deepgram Nova-3 real-time streaming.
     * GDPR/EU-friendly (EU data residency), built-in speaker diarization, fastest WER.
     * Gets a short-lived temporary key from our backend, then streams PCM16 to Deepgram's WebSocket.
     */
    async startDeepgramRecording(source, transcriptCallback) {
        console.log('[SHARED STATE] Starting Deepgram recording...');
        try {
            const tokenResp = await fetch('/api/transcription/deepgram-token', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` }
            });
            const tokenData = await tokenResp.json();
            if (!tokenData.token) {
                const msg = tokenData.error || 'Deepgram not configured for this organisation';
                this.trigger('onError', msg);
                throw new Error(msg);
            }

            const audioStream = await navigator.mediaDevices.getUserMedia({
                audio: { sampleRate: 16000, channelCount: 1, echoCancellation: true, noiseSuppression: true }
            });
            this.audioStream = audioStream;
            this.currentAudioSource = 'microphone';
            this.startAudioLevelMonitoring(audioStream);

            const params = new URLSearchParams({
                model: 'nova-3', smart_format: 'true', diarize: 'true',
                punctuate: 'true', encoding: 'linear16', sample_rate: '16000', channels: '1'
            });
            const ws = new WebSocket(`wss://api.deepgram.com/v1/listen?${params}`, ['token', tokenData.token]);
            this.deepgramWS = ws;

            const audioCtx = new AudioContext({ sampleRate: 16000 });
            const sourceNode = audioCtx.createMediaStreamSource(audioStream);
            const processor = audioCtx.createScriptProcessor(4096, 1, 1);
            processor.onaudioprocess = (e) => {
                if (!this.isRecording || ws.readyState !== WebSocket.OPEN) return;
                const float32 = e.inputBuffer.getChannelData(0);
                const int16 = new Int16Array(float32.length);
                for (let i = 0; i < float32.length; i++) {
                    int16[i] = Math.max(-32768, Math.min(32767, Math.round(float32[i] * 32767)));
                }
                ws.send(int16.buffer);
            };
            sourceNode.connect(processor);
            processor.connect(audioCtx.destination);
            this.deepgramAudioProcessor = { processor, source_node: sourceNode, audioContext: audioCtx };

            ws.onopen = () => {
                this.isRecording = true;
                this.trigger('onStart', source);
                console.log('[SHARED STATE] ✅ Deepgram recording started');
            };
            ws.onmessage = (evt) => {
                try {
                    const data = JSON.parse(evt.data);
                    if (data.type === 'Results') {
                        const alt = data.channel?.alternatives?.[0];
                        const text = alt?.transcript || '';
                        const isFinal = data.is_final === true;
                        if (text) {
                            if (this.customTranscriptCallback) this.customTranscriptCallback(isFinal ? text : '', isFinal ? '' : text);
                            this.trigger('onTranscript', { final: isFinal ? text : '', interim: isFinal ? '' : text, confidence: alt?.confidence || 0.9 }, source);
                        }
                    }
                } catch (e) { console.warn('[SHARED STATE] Deepgram parse error:', e); }
            };
            ws.onerror = (e) => { console.error('[SHARED STATE] Deepgram WS error:', e); this.trigger('onError', 'Deepgram connection error'); };
            ws.onclose = () => { if (this.isRecording) this.stopRecording(); };
        } catch (error) {
            console.error('[SHARED STATE] Deepgram recording failed:', error);
            this.trigger('onError', error.message);
            throw error;
        }
    }

    /**
     * OpenAI Realtime API — GPT-4o quality transcription + full dialogue capability.
     * Exchanges org's OpenAI key for a short-lived ephemeral token, then opens the Realtime WebSocket.
     * Base64-encodes PCM16 audio chunks as JSON messages (OpenAI Realtime protocol).
     */
    async startOpenAIRealtimeRecording(source, transcriptCallback) {
        console.log('[SHARED STATE] Starting OpenAI Realtime recording...');
        try {
            const tokenResp = await fetch('/api/transcription/openai-realtime-token', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` }
            });
            const tokenData = await tokenResp.json();
            if (!tokenData.token) {
                const msg = tokenData.error || 'OpenAI not configured for this organisation';
                this.trigger('onError', msg);
                throw new Error(msg);
            }

            const audioStream = await navigator.mediaDevices.getUserMedia({
                audio: { sampleRate: 24000, channelCount: 1, echoCancellation: true, noiseSuppression: true }
            });
            this.audioStream = audioStream;
            this.currentAudioSource = 'microphone';
            this.startAudioLevelMonitoring(audioStream);

            const model = tokenData.model || 'gpt-4o-realtime-preview';
            const ws = new WebSocket(
                `wss://api.openai.com/v1/realtime?model=${model}`,
                ['realtime', `openai-insecure-api-key.${tokenData.token}`, 'openai-beta.realtime-v1']
            );
            this.openaiRealtimeWS = ws;

            const audioCtx = new AudioContext({ sampleRate: 24000 });
            const sourceNode = audioCtx.createMediaStreamSource(audioStream);
            const processor = audioCtx.createScriptProcessor(4096, 1, 1);
            processor.onaudioprocess = (e) => {
                if (!this.isRecording || ws.readyState !== WebSocket.OPEN) return;
                const float32 = e.inputBuffer.getChannelData(0);
                const int16 = new Int16Array(float32.length);
                for (let i = 0; i < float32.length; i++) {
                    int16[i] = Math.max(-32768, Math.min(32767, Math.round(float32[i] * 32767)));
                }
                const bytes = new Uint8Array(int16.buffer);
                let binary = '';
                for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
                ws.send(JSON.stringify({ type: 'input_audio_buffer.append', audio: btoa(binary) }));
            };
            sourceNode.connect(processor);
            processor.connect(audioCtx.destination);
            this.openaiRealtimeAudioProcessor = { processor, source_node: sourceNode, audioContext: audioCtx };

            ws.onopen = () => {
                // Configure session for transcription mode
                ws.send(JSON.stringify({
                    type: 'session.update',
                    session: {
                        modalities: ['text'],
                        input_audio_transcription: { model: 'whisper-1' },
                        turn_detection: { type: 'server_vad', silence_duration_ms: 500 }
                    }
                }));
                this.isRecording = true;
                this.trigger('onStart', source);
                console.log('[SHARED STATE] ✅ OpenAI Realtime recording started');
            };
            ws.onmessage = (evt) => {
                try {
                    const data = JSON.parse(evt.data);
                    if (data.type === 'conversation.item.input_audio_transcription.completed') {
                        const text = data.transcript || '';
                        if (this.customTranscriptCallback) this.customTranscriptCallback(text, '');
                        this.trigger('onTranscript', { final: text, interim: '', confidence: 0.97 }, source);
                    } else if (data.type === 'input_audio_buffer.speech_started') {
                        this.trigger('onTranscript', { final: '', interim: '\u2026', confidence: 0 }, source);
                    }
                } catch (e) {}
            };
            ws.onerror = (e) => { console.error('[SHARED STATE] OpenAI Realtime error:', e); this.trigger('onError', 'OpenAI Realtime connection error'); };
            ws.onclose = () => { if (this.isRecording) this.stopRecording(); };
        } catch (error) {
            console.error('[SHARED STATE] OpenAI Realtime recording failed:', error);
            this.trigger('onError', error.message);
            throw error;
        }
    }

    /**
     * Speechmatics real-time streaming. EU WebSocket endpoint — GDPR-native.
     * UK/EU company, best accuracy on accented English, speaker diarization built-in.
     * Creates a short-lived JWT from our backend, then streams raw PCM16 to eu2.rt.speechmatics.com.
     */
    async startSpeechmaticsRecording(source, transcriptCallback) {
        console.log('[SHARED STATE] Starting Speechmatics recording...');
        try {
            const tokenResp = await fetch('/api/transcription/speechmatics-token', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` }
            });
            const tokenData = await tokenResp.json();
            if (!tokenData.token) {
                const msg = tokenData.error || 'Speechmatics not configured for this organisation';
                this.trigger('onError', msg);
                throw new Error(msg);
            }

            const audioStream = await navigator.mediaDevices.getUserMedia({
                audio: { sampleRate: 16000, channelCount: 1, echoCancellation: true, noiseSuppression: true }
            });
            this.audioStream = audioStream;
            this.currentAudioSource = 'microphone';
            this.startAudioLevelMonitoring(audioStream);

            // EU endpoint — data stays in UK/EU for GDPR compliance
            const ws = new WebSocket(`wss://eu2.rt.speechmatics.com/v2?jwt=${encodeURIComponent(tokenData.token)}`);
            this.speechmaticsWS = ws;

            const audioCtx = new AudioContext({ sampleRate: 16000 });
            const sourceNode = audioCtx.createMediaStreamSource(audioStream);
            const processor = audioCtx.createScriptProcessor(4096, 1, 1);
            processor.onaudioprocess = (e) => {
                if (!this.isRecording || ws.readyState !== WebSocket.OPEN) return;
                const float32 = e.inputBuffer.getChannelData(0);
                const int16 = new Int16Array(float32.length);
                for (let i = 0; i < float32.length; i++) {
                    int16[i] = Math.max(-32768, Math.min(32767, Math.round(float32[i] * 32767)));
                }
                ws.send(int16.buffer);
            };
            sourceNode.connect(processor);
            processor.connect(audioCtx.destination);
            this.speechmaticsAudioProcessor = { processor, source_node: sourceNode, audioContext: audioCtx };

            ws.onopen = () => {
                ws.send(JSON.stringify({
                    message: 'StartRecognition',
                    audio_format: { type: 'raw', encoding: 'pcm_s16le', sample_rate: 16000 },
                    transcription_config: {
                        language: 'en',
                        enable_partials: true,
                        speaker_diarization_config: { max_speakers: 10 }
                    }
                }));
                this.isRecording = true;
                this.trigger('onStart', source);
                console.log('[SHARED STATE] ✅ Speechmatics recording started');
            };
            ws.onmessage = (evt) => {
                try {
                    const data = JSON.parse(evt.data);
                    if (data.message === 'AddTranscript') {
                        const text = data.metadata?.transcript || '';
                        if (text && this.customTranscriptCallback) this.customTranscriptCallback(text, '');
                        if (text) this.trigger('onTranscript', { final: text, interim: '', confidence: 0.92 }, source);
                    } else if (data.message === 'AddPartialTranscript') {
                        const text = data.metadata?.transcript || '';
                        if (text) this.trigger('onTranscript', { final: '', interim: text, confidence: 0 }, source);
                    }
                } catch (e) { console.warn('[SHARED STATE] Speechmatics parse error:', e); }
            };
            ws.onerror = (e) => { console.error('[SHARED STATE] Speechmatics error:', e); this.trigger('onError', 'Speechmatics connection error'); };
            ws.onclose = () => { if (this.isRecording) this.stopRecording(); };
        } catch (error) {
            console.error('[SHARED STATE] Speechmatics recording failed:', error);
            this.trigger('onError', error.message);
            throw error;
        }
    }

    // Start audio preview BEFORE recording (tries system audio first, then microphone)
    async startAudioPreview() {
        if (this.previewStream) {
            console.log('[SHARED STATE] Audio preview already active');
            return;
        }

        console.log('[SHARED STATE] Starting audio preview...');

        try {
            let stream = null;
            let source = null;

            // 🔊 TRY 1: System audio (preferred)
            try {
                console.log('[SHARED STATE] Attempting system audio preview...');
                stream = await navigator.mediaDevices.getDisplayMedia({
                    video: false,
                    audio: {
                        channelCount: 1,
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true,
                        sampleRate: 16000
                    }
                });
                source = 'system';
                console.log('[SHARED STATE] ✅ System audio preview active');
            } catch (systemError) {
                console.log('[SHARED STATE] System audio not available, trying microphone...');

                // 🎤 FALLBACK: Microphone
                try {
                    stream = await navigator.mediaDevices.getUserMedia({
                        audio: {
                            channelCount: 1,
                            echoCancellation: true,
                            noiseSuppression: true,
                            autoGainControl: true,
                            sampleRate: 16000
                        }
                    });
                    source = 'microphone';
                    console.log('[SHARED STATE] ✅ Microphone preview active');
                } catch (micError) {
                    console.error('[SHARED STATE] No audio source available for preview:', micError);
                    // Show message in UI
                    const levelDisplay = document.getElementById('audio-level-value');
                    if (levelDisplay) {
                        levelDisplay.textContent = 'No audio access';
                        levelDisplay.style.color = '#da3633';
                    }
                    return;
                }
            }

            // Store preview stream
            this.previewStream = stream;
            this.previewSource = source;

            // Update UI to show audio source
            const sourceLabel = document.getElementById('audio-source-label');
            if (sourceLabel) {
                sourceLabel.textContent = `Source: ${source === 'system' ? '🖥️ System Audio' : '🎤 Microphone'}`;
                sourceLabel.style.color = source === 'system' ? '#58a6ff' : '#f0883e';
            }

            // Start monitoring with preview stream
            this.startAudioLevelMonitoring(stream, true);

        } catch (error) {
            console.error('[SHARED STATE] Failed to start audio preview:', error);
        }
    }

    // Stop audio preview
    stopAudioPreview() {
        if (this.previewStream) {
            try {
                this.previewStream.getTracks().forEach(track => track.stop());
                this.previewStream = null;
                this.previewSource = null;
                console.log('[SHARED STATE] Audio preview stopped');
            } catch (e) {
                console.error('[SHARED STATE] Failed to stop preview stream:', e);
            }
        }
    }

    // Start audio level monitoring
    startAudioLevelMonitoring(audioStream, isPreview = false) {
        try {
            // Create Web Audio API context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const source = this.audioContext.createMediaStreamSource(audioStream);

            // Create analyzer node
            this.audioAnalyzer = this.audioContext.createAnalyser();
            this.audioAnalyzer.fftSize = 256;
            this.audioAnalyzer.smoothingTimeConstant = 0.8;

            source.connect(this.audioAnalyzer);

            // Show equalizer section
            const eqSection = document.getElementById('audio-level-section');
            if (eqSection) {
                eqSection.style.display = 'block';
                // Update title based on mode
                const title = eqSection.querySelector('h3');
                if (title) {
                    title.innerHTML = isPreview ?
                        '<i class="fas fa-signal"></i> Audio Detection (Preview)' :
                        '<i class="fas fa-signal"></i> Audio Level (Recording)';
                }
            }

            // Start monitoring loop
            this.updateAudioLevels();

            console.log(`[SHARED STATE] Audio level monitoring started (${isPreview ? 'preview' : 'recording'})`);
        } catch (error) {
            console.error('[SHARED STATE] Failed to start audio monitoring:', error);
        }
    }

    // Update audio level visualization
    updateAudioLevels() {
        if (!this.audioAnalyzer || !this.isRecording) {
            return;
        }

        const dataArray = new Uint8Array(this.audioAnalyzer.frequencyBinCount);
        this.audioAnalyzer.getByteFrequencyData(dataArray);

        // Calculate average level
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        const normalizedLevel = average / 255; // 0 to 1

        // Update equalizer bars
        const bars = document.querySelectorAll('.eq-bar');
        bars.forEach((bar, index) => {
            // Each bar represents a frequency range
            const binStart = Math.floor((index / bars.length) * dataArray.length);
            const binEnd = Math.floor(((index + 1) / bars.length) * dataArray.length);
            const binAverage = dataArray.slice(binStart, binEnd).reduce((a, b) => a + b, 0) / (binEnd - binStart);

            // Set bar height (10% to 100%)
            const height = Math.max(10, (binAverage / 255) * 100);
            bar.style.height = `${height}%`;

            // Add active class for visual feedback
            if (binAverage > 30) {
                bar.classList.add('active');
            } else {
                bar.classList.remove('active');
            }
        });

        // Update peak level display (convert to dB)
        const peakValue = Math.max(...dataArray);
        const dbLevel = peakValue > 0 ? 20 * Math.log10(peakValue / 255) : -60;

        // Determine color based on level
        let color = '#8b949e'; // Gray (too quiet)
        if (dbLevel > -10) {
            color = '#da3633'; // Red (too loud)
        } else if (dbLevel > -20) {
            color = '#f0883e'; // Orange (good)
        } else if (dbLevel > -40) {
            color = '#2ea043'; // Green (optimal)
        }

        // Update badge in compact header
        this.updateAudioBadge(`${dbLevel.toFixed(1)} dB`, color);

        // Continue monitoring (during recording OR preview)
        if (this.isRecording || this.previewStream) {
            requestAnimationFrame(() => this.updateAudioLevels());
        }
    }

    // Stop audio level monitoring
    stopAudioLevelMonitoring(hideUI = false) {
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
            this.audioAnalyzer = null;
        }

        // Only hide UI if explicitly requested (not during preview mode)
        if (hideUI) {
            const eqSection = document.getElementById('audio-level-section');
            if (eqSection) {
                eqSection.style.display = 'none';
            }
        }

        console.log('[SHARED STATE] Audio level monitoring stopped');
    }

    // Update audio badge in compact header
    updateAudioBadge(text, color = null) {
        const badge = document.getElementById('audio-level-badge');
        if (badge) {
            badge.textContent = text;
            if (color) {
                badge.style.color = color;
            }
        }
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

        // Initialize state flags
        this.isPaused = false;
        this.shouldSaveOnStop = true; // Can be set to false by delete button

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

        // Start audio preview (shows before recording to detect sound)
        setTimeout(() => {
            if (this.sharedState && !this.sharedState.isRecording) {
                this.sharedState.startAudioPreview();
            }
        }, 1000); // Small delay to ensure DOM is ready

        // Check browser support
        this.checkBrowserSupport();

        // Initialize STT and TTS modules if available
        this.initializeModules();

        // Setup event listeners
        this.setupEventListeners();

        // Setup drag-and-drop drop zones
        this.setupDropZones();

        // Test backend connection
        await this.testBackendConnection();

        console.log('[TRANSCRIPTION SIDEBAR] Initialization complete');
    }

    /**
     * Switch between tabs
     * @param {string} tabName - Tab name ('recording', 'upload', 'tts', 'transcripts', 'settings')
     */
    switchTab(tabName) {
        console.log(`[TRANSCRIPTION SIDEBAR] Switching to tab: ${tabName}`);

        // Remove active class from all tabs and tab contents
        document.querySelectorAll('.transcription-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.transcription-tab-content').forEach(content => {
            content.classList.remove('active');
        });

        // Add active class to clicked tab and corresponding content
        const activeTab = document.querySelector(`.transcription-tab[data-tab="${tabName}"]`);
        const activeContent = document.getElementById(`${tabName}-tab`);

        if (activeTab) {
            activeTab.classList.add('active');
        } else {
            console.warn(`[TRANSCRIPTION SIDEBAR] Tab button not found: ${tabName}`);
        }

        if (activeContent) {
            activeContent.classList.add('active');
        } else {
            console.warn(`[TRANSCRIPTION SIDEBAR] Tab content not found: ${tabName}-tab`);
        }
    }

    /**
     * Toggle recording on/off
     */
    async toggleRecording() {
        if (this.sharedState.isRecording) {
            // Stop recording
            await this.sharedState.stopRecording();
        } else {
            // Start recording
            await this.sharedState.startRecording('sidebar');
        }
    }

    /**
     * Toggle pause/resume recording
     */
    togglePause() {
        if (!this.sharedState.isRecording) {
            console.warn('[TRANSCRIPTION SIDEBAR] Not recording, cannot pause');
            return;
        }

        this.isPaused = !this.isPaused;
        const pauseBtn = document.getElementById('transcription-pause-btn');

        if (this.isPaused) {
            // Pause audio recorder
            if (this.sharedState.audioRecorder && this.sharedState.audioRecorder.state === 'recording') {
                this.sharedState.audioRecorder.pause();
            }

            // Update button
            if (pauseBtn) {
                pauseBtn.innerHTML = '<i class="fas fa-play"></i>';
                pauseBtn.title = 'Resume Recording';
            }

            console.log('[TRANSCRIPTION SIDEBAR] Recording paused');
        } else {
            // Resume audio recorder
            if (this.sharedState.audioRecorder && this.sharedState.audioRecorder.state === 'paused') {
                this.sharedState.audioRecorder.resume();
            }

            // Update button
            if (pauseBtn) {
                pauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
                pauseBtn.title = 'Pause Recording';
            }

            console.log('[TRANSCRIPTION SIDEBAR] Recording resumed');
        }
    }

    /**
     * Delete current recording without saving
     */
    async deleteCurrent() {
        if (!this.sharedState.isRecording) {
            console.warn('[TRANSCRIPTION SIDEBAR] Not recording, nothing to delete');
            return;
        }

        if (confirm('Delete current recording without saving?')) {
            this.shouldSaveOnStop = false;
            await this.sharedState.stopRecording();
            this.shouldSaveOnStop = true; // Reset for next recording

            // Clear live transcript display
            const liveDisplay = document.getElementById('transcription-live-display');
            if (liveDisplay) {
                liveDisplay.innerHTML = `
                    <div class="transcription-placeholder">
                        <i class="fas fa-microphone-slash" style="font-size: 48px; color: #6e7681; margin-bottom: 12px;"></i>
                        <p style="color: #8b949e; text-align: center;">Recording deleted. Click "Start Recording" to begin again.</p>
                    </div>
                `;
            }

            console.log('[TRANSCRIPTION SIDEBAR] Recording deleted');
        }
    }

    /**
     * Toggle audio section collapse/expand
     */
    toggleAudioSection() {
        const content = document.getElementById('audio-section-content');
        const icon = document.getElementById('audio-section-toggle');

        if (content && icon) {
            const isCollapsed = content.classList.contains('collapsed');

            if (isCollapsed) {
                content.classList.remove('collapsed');
                icon.classList.add('rotated');
            } else {
                content.classList.add('collapsed');
                icon.classList.remove('rotated');
            }
        }
    }

    /**
     * Select audio source (system or microphone)
     * @param {string} source - 'system' or 'microphone'
     */
    async selectAudioSource(source) {
        console.log(`[TRANSCRIPTION SIDEBAR] Selecting audio source: ${source}`);

        // Update button states
        const systemBtn = document.getElementById('system-audio-btn');
        const micBtn = document.getElementById('microphone-btn');

        if (systemBtn && micBtn) {
            systemBtn.classList.remove('active');
            micBtn.classList.remove('active');

            if (source === 'system' && systemBtn) {
                systemBtn.classList.add('active');
            } else if (source === 'microphone' && micBtn) {
                micBtn.classList.add('active');
            }
        }

        // If currently previewing or recording, restart with new source
        if (this.sharedState.previewStream || this.sharedState.isRecording) {
            // Stop current preview
            this.sharedState.stopAudioPreview();

            // Restart preview with selected source
            // Note: Browser may show permission dialog again
            await this.sharedState.startAudioPreview();
        }
    }

    /**
     * Setup drag-and-drop drop zones for AI Prime and agent columns
     */
    setupDropZones() {
        // AI Prime input drop zone
        const primeInput = document.getElementById('ai-chat-input');
        if (primeInput) {
            this.makeDropZone(primeInput, 'AI Prime');
        }

        // Agent column inputs - setup observer for dynamically created agents
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        const agentInput = node.querySelector?.('.agent-column-input');
                        if (agentInput) {
                            const titleEl = node.querySelector('.agent-column-title');
                            const agentName = titleEl ? titleEl.textContent.trim() : 'Agent';
                            this.makeDropZone(agentInput, agentName);
                        }
                    }
                });
            });
        });

        // Observe agent workspace for new columns
        const workspace = document.getElementById('agent-workspace-container');
        if (workspace) {
            observer.observe(workspace, { childList: true, subtree: true });
        }

        // Setup existing agent inputs
        document.querySelectorAll('.agent-column-input').forEach((input, index) => {
            this.makeDropZone(input, `Agent ${index + 1}`);
        });

        console.log('[TRANSCRIPTION] Drop zones setup complete');
    }

    /**
     * Make an input element a drop zone for transcript cards
     */
    makeDropZone(element, name) {
        element.addEventListener('dragover', (e) => {
            e.preventDefault();
            element.style.background = 'rgba(88, 166, 255, 0.1)';
            element.style.borderColor = '#58a6ff';
        });

        element.addEventListener('dragleave', (e) => {
            element.style.background = '';
            element.style.borderColor = '';
        });

        element.addEventListener('drop', (e) => {
            e.preventDefault();
            element.style.background = '';
            element.style.borderColor = '';

            // Get transcript data
            const transcriptJson = e.dataTransfer.getData('application/transcript');
            if (transcriptJson) {
                const transcript = JSON.parse(transcriptJson);

                // Insert text
                const insertMode = this.config.insertMode || 'append';
                if (insertMode === 'replace') {
                    element.value = transcript.text;
                } else {
                    const currentText = element.value.trim();
                    element.value = currentText ? currentText + ' ' + transcript.text : transcript.text;
                }

                // Focus and trigger events
                element.focus();
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));

                console.log(`[TRANSCRIPTION] Transcript dropped into ${name}:`, transcript.text.substring(0, 50));

                // Show notification
                if (window.showNotification) {
                    window.showNotification(`Transcript inserted to ${name}`, 'success');
                }
            }
        });
    }

    /**
     * File upload handlers
     */
    handleDragOver(event) {
        event.preventDefault();
        event.stopPropagation();
        const zone = document.getElementById('transcription-upload-zone');
        if (zone) {
            zone.style.borderColor = '#58a6ff';
            zone.style.background = 'rgba(88, 166, 255, 0.05)';
        }
    }

    handleDragLeave(event) {
        event.preventDefault();
        event.stopPropagation();
        const zone = document.getElementById('transcription-upload-zone');
        if (zone) {
            zone.style.borderColor = '';
            zone.style.background = '';
        }
    }

    handleFileDrop(event) {
        event.preventDefault();
        event.stopPropagation();
        const zone = document.getElementById('transcription-upload-zone');
        if (zone) {
            zone.style.borderColor = '';
            zone.style.background = '';
        }

        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.processUploadedFile(files[0]);
        }
    }

    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        if (files.length > 0) {
            console.log(`[TRANSCRIPTION SIDEBAR] Processing ${files.length} file(s)`);
            this.processMultipleFiles(files);
        }
    }

    async processMultipleFiles(files) {
        const panel = document.getElementById('upload-status-panel');
        const queueDiv = document.getElementById('upload-file-queue');

        if (panel) panel.style.display = 'block';

        // Show file queue
        if (queueDiv) {
            queueDiv.innerHTML = files.map((f, i) => `
                <div id="file-queue-${i}" style="padding: 6px; background: #161b22; border-radius: 4px; margin-bottom: 4px; font-size: 12px;">
                    <i class="fas fa-file-audio" style="color: #58a6ff;"></i>
                    <span style="color: #c9d1d9;">${f.name}</span>
                    <span style="color: #6e7681; float: right;" id="file-queue-status-${i}">Waiting...</span>
                </div>
            `).join('');
        }

        // Process files sequentially
        for (let i = 0; i < files.length; i++) {
            const statusSpan = document.getElementById(`file-queue-status-${i}`);
            if (statusSpan) statusSpan.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing';

            try {
                await this.processUploadedFile(files[i], i + 1, files.length);
                if (statusSpan) statusSpan.innerHTML = '<i class="fas fa-check" style="color: #3fb950;"></i> Done';
            } catch (error) {
                if (statusSpan) statusSpan.innerHTML = '<i class="fas fa-times" style="color: #f85149;"></i> Error';
            }
        }

        // Clear queue after delay
        setTimeout(() => {
            if (queueDiv) queueDiv.innerHTML = '';
            if (panel) panel.style.display = 'none';
        }, 3000);
    }

    async processUploadedFile(file, currentFile = 1, totalFiles = 1) {
        console.log(`[TRANSCRIPTION SIDEBAR] Processing file ${currentFile}/${totalFiles}:`, file.name, file.type, file.size);

        // Validate file type
        if (!file.type.startsWith('audio/') && !file.type.startsWith('video/')) {
            alert('Invalid file type. Please upload an audio or video file.');
            throw new Error('Invalid file type');
        }

        // Validate file size (25MB limit)
        const maxSize = 25 * 1024 * 1024;
        if (file.size > maxSize) {
            alert('File too large. Maximum size is 25MB.');
            throw new Error('File too large');
        }

        // Show progress
        const progressDiv = document.getElementById('upload-status-panel');
        const statusSpan = document.getElementById('upload-status');
        const progressBar = document.getElementById('upload-progress-bar');
        const progressText = document.getElementById('upload-progress-text');
        const languageDisplay = document.getElementById('upload-language-display');
        const durationDisplay = document.getElementById('upload-duration-display');

        if (progressDiv) progressDiv.style.display = 'block';
        if (statusSpan) statusSpan.textContent = `Processing ${currentFile}/${totalFiles}: ${file.name}`;
        if (progressBar) progressBar.style.width = '10%';
        if (progressText) progressText.textContent = '10%';

        const startTime = Date.now();

        try {
            // Extract audio if video file
            let audioBlob = file;
            if (file.type.startsWith('video/')) {
                if (statusSpan) statusSpan.textContent = 'Extracting audio from video...';
                audioBlob = await this.extractAudioFromVideo(file);
                if (progressBar) progressBar.style.width = '30%';
                if (progressText) progressText.textContent = '30%';
            }

            // Get duration
            const duration = await this.getAudioDuration(audioBlob);
            if (durationDisplay) {
                durationDisplay.style.display = 'block';
                const durationSpan = document.getElementById('audio-duration');
                if (durationSpan) durationSpan.textContent = this.formatDuration(duration);
            }

            // Send to selected engine
            const uploadEngine = document.querySelector('input[name="upload-engine"]:checked')?.value || 'local';
            const engineLabels = {
                'local': 'Local Whisper', 'openai': 'OpenAI gpt-4o-transcribe',
                'deepgram': 'Deepgram Nova-3', 'assemblyai-async': 'AssemblyAI', 'speechmatics': 'Speechmatics'
            };
            if (statusSpan) statusSpan.textContent = `Transcribing with ${engineLabels[uploadEngine] || uploadEngine}...`;
            if (progressBar) progressBar.style.width = '50%';
            if (progressText) progressText.textContent = '50%';

            const result = await this.sendFileForTranscription(uploadEngine, audioBlob, file.name);

            if (progressBar) progressBar.style.width = '90%';
            if (progressText) progressText.textContent = '90%';

            // Display detected language
            if (result.language && languageDisplay) {
                languageDisplay.style.display = 'block';
                const langSpan = document.getElementById('detected-language');
                if (langSpan) langSpan.textContent = this.getLanguageName(result.language);
            }

            const processingTime = ((Date.now() - startTime) / 1000).toFixed(1);

            // Display transcript with metadata
            if (result.transcript && result.transcript.trim()) {
                this.displayFileTranscript(result.transcript, file.name, {
                    language: result.language,
                    duration: duration,
                    processingTime: processingTime,
                    confidence: result.confidence
                });

                this.addSTTTranscript(result.transcript, 'file-upload');

                // Save to server with full metadata
                try {
                    await this.saveTranscriptionToServer({
                        transcript: result.transcript,
                        source_type: 'upload',
                        file_info: {
                            filename: file.name,
                            size: file.size,
                            format: file.name.split('.').pop(),
                            mime_type: file.type
                        },
                        model_used: 'whisper-base',
                        confidence: result.confidence,
                        language: result.language,
                        duration_seconds: duration,
                        metadata: {
                            origin: 'upload',
                            processing_time: processingTime
                        }
                    });
                } catch (err) {
                    console.warn('[TRANSCRIPTION] Failed to save uploaded transcription:', err);
                }

                if (statusSpan) statusSpan.textContent = `Complete! (${processingTime}s)`;
                if (progressBar) progressBar.style.width = '100%';
                if (progressText) progressText.textContent = '100%';

                if (totalFiles === 1) {
                    setTimeout(() => {
                        if (progressDiv) progressDiv.style.display = 'none';
                        if (progressBar) progressBar.style.width = '0%';
                        if (languageDisplay) languageDisplay.style.display = 'none';
                        if (durationDisplay) durationDisplay.style.display = 'none';
                    }, 2000);
                }
            } else {
                throw new Error('No transcript received from Whisper');
            }

        } catch (error) {
            console.error('[TRANSCRIPTION SIDEBAR] File processing error:', error);
            if (statusSpan) statusSpan.textContent = 'Error: ' + error.message;
            if (progressBar) progressBar.style.width = '0%';
            if (progressText) progressText.textContent = 'Failed';

            if (totalFiles === 1) {
                alert('Failed to transcribe file: ' + error.message);
                setTimeout(() => {
                    if (progressDiv) progressDiv.style.display = 'none';
                }, 3000);
            }

            throw error; // Re-throw for queue handling
        }

        // Reset file input
        const fileInput = document.getElementById('transcription-file-input');
        if (fileInput && totalFiles === currentFile) fileInput.value = '';
    }

    async extractAudioFromVideo(videoFile) {
        return new Promise((resolve, reject) => {
            const video = document.createElement('video');
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();

            video.src = URL.createObjectURL(videoFile);
            video.muted = false;

            video.onloadedmetadata = async () => {
                try {
                    const audioSource = audioContext.createMediaElementSource(video);
                    const destination = audioContext.createMediaStreamDestination();
                    audioSource.connect(destination);

                    const mediaRecorder = new MediaRecorder(destination.stream);
                    const chunks = [];

                    mediaRecorder.ondataavailable = (e) => {
                        if (e.data.size > 0) chunks.push(e.data);
                    };

                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
                        URL.revokeObjectURL(video.src);
                        audioContext.close();
                        resolve(audioBlob);
                    };

                    mediaRecorder.start();
                    await video.play();

                    video.onended = () => {
                        mediaRecorder.stop();
                    };
                } catch (error) {
                    URL.revokeObjectURL(video.src);
                    audioContext.close();
                    reject(error);
                }
            };

            video.onerror = () => {
                URL.revokeObjectURL(video.src);
                reject(new Error('Failed to load video'));
            };
        });
    }

    async sendFileForTranscription(engine, audioBlob, filename) {
        const endpoint = '/api/transcribe';
        const formData = new FormData();
        formData.append('file', audioBlob, filename);
        formData.append('engine', engine);

        const diarizeCheckbox = document.getElementById('transcription-speaker-diarization');
        if (diarizeCheckbox?.checked) formData.append('diarize', 'true');

        const languageSelect = document.getElementById('whisper-language-select');
        if (languageSelect && languageSelect.value !== 'auto') {
            formData.append('language', languageSelect.value);
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` },
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Transcription error (${engine}): ${response.status} - ${errorText}`);
        }

        const result = await response.json();
        return {
            transcript: result.transcript || result.text || '',
            language: result.language || 'unknown',
            confidence: result.confidence || null,
            duration: result.duration || null,
            speakers: result.speakers || null
        };
    }

    async sendFileToWhisper(audioBlob, filename) {
        const settings = this.getSTTSettings();
        const endpoint = settings.whisperEndpoint || '/api/transcribe';

        const formData = new FormData();
        formData.append('file', audioBlob, filename);

        // Add language preference if set (Whisper supports 50+ languages)
        const languageSelect = document.getElementById('whisper-language-select');
        if (languageSelect && languageSelect.value !== 'auto') {
            formData.append('language', languageSelect.value);
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Whisper API error: ${response.status} - ${errorText}`);
        }

        const result = await response.json();

        // Return full result with metadata (transcript, language, confidence)
        return {
            transcript: result.transcript || result.text || '',
            language: result.language || 'unknown',
            confidence: result.confidence || null,
            duration: result.duration || null
        };
    }

    displayFileTranscript(transcript, filename, metadata = {}) {
        const liveDisplay = document.getElementById('transcription-live-display');
        if (!liveDisplay) return;

        // Clear placeholder
        const placeholder = liveDisplay.querySelector('.transcription-placeholder');
        if (placeholder) placeholder.remove();

        // Add file header with metadata badges
        const headerDiv = document.createElement('div');
        headerDiv.style.cssText = `
            padding: 12px;
            background: linear-gradient(135deg, rgba(88, 166, 255, 0.1), rgba(88, 166, 255, 0.05));
            border-left: 3px solid #58a6ff;
            border-radius: 6px;
            margin-bottom: 12px;
        `;

        let badgesHTML = '';
        if (metadata.language) {
            badgesHTML += `<span style="background: #238636; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-left: 8px;">
                <i class="fas fa-language"></i> ${this.getLanguageName(metadata.language)}
            </span>`;
        }
        if (metadata.duration) {
            badgesHTML += `<span style="background: #1f6feb; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-left: 8px;">
                <i class="fas fa-clock"></i> ${this.formatDuration(metadata.duration)}
            </span>`;
        }
        if (metadata.processingTime) {
            badgesHTML += `<span style="background: #8957e5; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-left: 8px;">
                <i class="fas fa-bolt"></i> ${metadata.processingTime}s
            </span>`;
        }

        headerDiv.innerHTML = `
            <div style="font-size: 13px; color: #58a6ff; margin-bottom: 6px;">
                <i class="fas fa-file-audio"></i> ${filename}
            </div>
            <div>${badgesHTML}</div>
        `;
        liveDisplay.appendChild(headerDiv);

        // Add transcript with better formatting
        const transcriptDiv = document.createElement('div');
        transcriptDiv.className = 'final';
        transcriptDiv.style.cssText = `
            color: var(--text-primary, #c9d1d9);
            padding: 12px;
            line-height: 1.8;
            white-space: pre-wrap;
            background: rgba(13, 17, 23, 0.5);
            border-radius: 6px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        `;
        transcriptDiv.textContent = transcript;
        liveDisplay.appendChild(transcriptDiv);

        // Add action buttons
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
            <button id="send-to-chat-btn" onclick="TranscriptionSidebar.showAgentSelectorDropdown(event)" 
                    style="flex: 1; padding: 10px 16px; background: #238636; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px;"
                    onmouseover="this.style.background='#2ea043'"
                    onmouseout="this.style.background='#238636'">
                <i class="fas fa-paper-plane"></i>
                <span>Send to Chat</span>
                <i class="fas fa-chevron-down" style="font-size: 10px; margin-left: 4px;"></i>
            </button>
            <button onclick="TranscriptionSidebar.copyLiveTranscript()" 
                    style="padding: 10px 16px; background: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; cursor: pointer; font-size: 13px;"
                    onmouseover="this.style.background='#30363d'"
                    onmouseout="this.style.background='#21262d'"
                    title="Copy to clipboard">
                <i class="fas fa-copy"></i>
            </button>
            <button onclick="TranscriptionSidebar.downloadTranscript('${filename}')" 
                    style="padding: 10px 16px; background: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; cursor: pointer; font-size: 13px;"
                    onmouseover="this.style.background='#30363d'"
                    onmouseout="this.style.background='#21262d'"
                    title="Download as text file">
                <i class="fas fa-download"></i>
            </button>
            <button onclick="TranscriptionSidebar.clearLiveTranscript()" 
                    style="padding: 10px 16px; background: #21262d; color: #f85149; border: 1px solid #30363d; border-radius: 6px; cursor: pointer; font-size: 13px;"
                    onmouseover="this.style.background='#30363d'"
                    onmouseout="this.style.background='#21262d'"
                    title="Clear transcript">
                <i class="fas fa-eraser"></i>
            </button>
        `;

        liveDisplay.appendChild(actionsDiv);
        liveDisplay.scrollTop = liveDisplay.scrollHeight;

        console.log('[TRANSCRIPTION SIDEBAR] File transcript displayed with metadata:', metadata);
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
     * Toggle pause/resume recording
     */
    togglePause() {
        if (!this.sharedState.isRecording) {
            console.warn('[TRANSCRIPTION SIDEBAR] Not recording, cannot pause');
            return;
        }

        this.isPaused = !this.isPaused;
        const pauseBtn = document.getElementById('transcription-pause-btn');
        const stateEl = document.getElementById('stt-state');

        if (this.isPaused) {
            // Pause recording
            if (this.sharedState.browserRecognition) {
                this.sharedState.browserRecognition.stop();
            }

            // Stop timer
            if (this.recordingInterval) {
                clearInterval(this.recordingInterval);
                this.recordingInterval = null;
            }

            if (pauseBtn) {
                pauseBtn.classList.add('paused');
                pauseBtn.querySelector('i').className = 'fas fa-play';
                pauseBtn.title = 'Resume Recording';
            }
            if (stateEl) stateEl.textContent = 'Paused';

            console.log('[TRANSCRIPTION SIDEBAR] Recording paused');
        } else {
            // Resume recording
            if (this.sharedState.browserRecognition) {
                try {
                    this.sharedState.browserRecognition.start();
                } catch (e) {
                    console.warn('[TRANSCRIPTION SIDEBAR] Failed to resume:', e);
                }
            }

            // Restart timer
            this.recordingInterval = setInterval(() => {
                const elapsed = Date.now() - this.recordingStartTime;
                const duration = this.formatDuration(elapsed);
                const durationEl = document.getElementById('stt-duration');
                if (durationEl) durationEl.textContent = duration;
            }, 1000);

            if (pauseBtn) {
                pauseBtn.classList.remove('paused');
                pauseBtn.querySelector('i').className = 'fas fa-pause';
                pauseBtn.title = 'Pause Recording';
            }
            if (stateEl) stateEl.textContent = 'Recording';

            console.log('[TRANSCRIPTION SIDEBAR] Recording resumed');
        }
    }

    /**
     * Delete current recording and discard transcript
     */
    deleteCurrent() {
        if (!this.sharedState.isRecording) {
            console.warn('[TRANSCRIPTION SIDEBAR] Not recording, nothing to delete');
            return;
        }

        if (confirm('Delete this recording? The transcript will not be saved.')) {
            this.shouldSaveOnStop = false;
            this.sharedState.stopRecording();
            console.log('[TRANSCRIPTION SIDEBAR] Recording deleted, will not save');
        }
    }

    /**
     * Toggle sidebar visibility
     */
    toggleSidebar() {
        const sidebar = document.getElementById('transcription-sidebar');
        if (sidebar) {
            const isClosing = !sidebar.classList.contains('collapsed');
            sidebar.classList.toggle('collapsed');

            // Stop audio preview when closing sidebar
            if (isClosing && this.sharedState && !this.sharedState.isRecording) {
                this.sharedState.stopAudioPreview();
                this.sharedState.stopAudioLevelMonitoring(true);
            }

            // Start audio preview when opening sidebar
            if (!isClosing && this.sharedState && !this.sharedState.isRecording) {
                setTimeout(() => {
                    this.sharedState.startAudioPreview();
                }, 500);
            }

            console.log(`[TRANSCRIPTION SIDEBAR] Sidebar ${isClosing ? 'closed' : 'opened'}`);
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
        // If user opened Upload tab, load persistent history
        if (tabName === 'upload') {
            try {
                this.loadTranscriptionHistory();
            } catch (e) {
                console.warn('[TRANSCRIPTION SIDEBAR] Failed to load history:', e);
            }
        }
        // Check all engine key statuses whenever settings tab opens
        if (tabName === 'settings') {
            this.checkEnginesStatus();
        }
    }

    /**
     * Toggle audio detection section
     */
    toggleAudioSection() {
        const content = document.getElementById('audio-section-content');
        const icon = document.getElementById('audio-section-toggle');

        if (content && icon) {
            content.classList.toggle('collapsed');
            icon.classList.toggle('expanded');
        }
    }

    /**
     * Toggle upload section
     */
    toggleUploadSection() {
        const content = document.getElementById('upload-section-content');
        const icon = document.getElementById('upload-section-toggle');

        if (content && icon) {
            content.classList.toggle('collapsed');
            icon.classList.toggle('expanded');
        }
    }

    /**
     * Select audio source (system or microphone)
     */
    async selectAudioSource(source) {
        console.log(`[TRANSCRIPTION SIDEBAR] Selecting audio source: ${source}`);

        // Update button states
        const systemBtn = document.getElementById('system-audio-btn');
        const micBtn = document.getElementById('microphone-btn');

        if (source === 'system') {
            systemBtn?.classList.add('active');
            micBtn?.classList.remove('active');
        } else {
            systemBtn?.classList.remove('active');
            micBtn?.classList.add('active');
        }

        // Stop current preview
        if (this.sharedState) {
            this.sharedState.stopAudioPreview();
            this.sharedState.stopAudioLevelMonitoring(false);

            // Start preview with selected source
            await this.sharedState.startAudioPreview(source);
        }
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

        // ✅ NEW: Save live transcript to collection before clearing
        const liveDisplay = document.getElementById('transcription-live-display');
        if (liveDisplay && liveDisplay.textContent.trim()) {
            const transcriptText = liveDisplay.textContent.trim();
            const source = this.sharedState.recordingSource || 'unknown';

            console.log(`[TRANSCRIPTION SIDEBAR] Auto-saving transcript from ${source}:`, transcriptText.substring(0, 50) + '...');
            this.addSTTTranscript(transcriptText, source);
        }

        this.handleSTTStop();

        // Send audio to Whisper (disabled, will do nothing)
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

        // Update UI - Record button
        const recordBtn = document.getElementById('transcription-record-toggle');
        if (recordBtn) {
            recordBtn.classList.add('recording');
            recordBtn.querySelector('i').className = 'fas fa-stop';
            recordBtn.title = 'Stop Recording';
        }

        // Enable pause and delete buttons
        const pauseBtn = document.getElementById('transcription-pause-btn');
        const deleteBtn = document.getElementById('transcription-delete-btn');
        if (pauseBtn) pauseBtn.disabled = false;
        if (deleteBtn) deleteBtn.disabled = false;

        // Update state with audio source indicator
        const stateEl = document.getElementById('stt-state');
        if (stateEl) {
            const audioSource = this.sharedState.currentAudioSource || 'unknown';
            const sourceIcon = audioSource === 'system' ? '🔊' : audioSource === 'microphone' ? '🎤' : '🎙️';
            const sourceText = audioSource === 'system' ? 'System Audio' : audioSource === 'microphone' ? 'Microphone' : 'Recording';
            stateEl.innerHTML = `${sourceIcon} ${sourceText}`;
            stateEl.style.color = '#ef4444';
            stateEl.title = audioSource === 'system'
                ? 'Recording desktop/tab audio'
                : audioSource === 'microphone'
                    ? 'Recording from microphone'
                    : 'Recording active';
        }

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
            const durationEl = document.getElementById('stt-duration');
            if (durationEl) durationEl.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    handleSTTStop() {
        console.log('[TRANSCRIPTION SIDEBAR] STT recording stopped');

        // Update UI - Record button
        const recordBtn = document.getElementById('transcription-record-toggle');
        if (recordBtn) {
            recordBtn.classList.remove('recording');
            recordBtn.querySelector('i').className = 'fas fa-microphone';
            recordBtn.title = 'Start Recording';
        }

        // Disable pause and delete buttons
        const pauseBtn = document.getElementById('transcription-pause-btn');
        const deleteBtn = document.getElementById('transcription-delete-btn');
        if (pauseBtn) {
            pauseBtn.disabled = true;
            pauseBtn.classList.remove('paused');
            pauseBtn.querySelector('i').className = 'fas fa-pause';
        }
        if (deleteBtn) deleteBtn.disabled = true;

        const stateEl = document.getElementById('stt-state');
        if (stateEl) {
            stateEl.textContent = 'Processing';
            stateEl.style.color = '#58a6ff';
        }

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
                    <button onclick="TranscriptionSidebar.showAgentSelectorDropdown(event)" 
                            style="flex: 1; padding: 8px 12px; background: #238636; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; display: flex; align-items: center; justify-content: center; gap: 6px;"
                            onmouseover="this.style.background='#2ea043'"
                            onmouseout="this.style.background='#238636'">
                        <i class="fas fa-paper-plane"></i>
                        <span>Send to Chat</span>
                        <i class="fas fa-chevron-down" style="font-size: 10px; margin-left: 4px;"></i>
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
    addSTTTranscript(text, source = null) {
        const transcript = {
            timestamp: Date.now(),
            text: text,
            type: 'stt',
            source: source || this.sharedState.recordingSource || 'unknown', // 'sidebar' | 'chat' | 'unknown'
            audioSource: this.sharedState.currentAudioSource || 'unknown' // 'system' | 'microphone' | 'unknown'
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

        // Save to server in background for persistence
        try {
            this.saveTranscriptionToServer({
                transcript: text,
                source_type: transcript.source,
                file_info: null,
                model_used: null,
                confidence: null,
                language: null,
                duration_seconds: null,
                metadata: { audioSource: transcript.audioSource }
            });
        } catch (err) {
            console.warn('[TRANSCRIPTION SIDEBAR] Failed to enqueue save to server:', err);
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
     * Save transcription record to server for persistence
     */
    async saveTranscriptionToServer(payload) {
        try {
            const resp = await fetch('/api/transcriptions/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!resp.ok) {
                console.warn('[TRANSCRIPTION] Save API responded with', resp.status);
                return null;
            }

            const data = await resp.json();
            return data;
        } catch (err) {
            console.error('[TRANSCRIPTION] Failed to save transcription to server:', err);
            return null;
        }
    }

    /**
     * Load transcription history from server and render in Upload tab
     */
    async loadTranscriptionHistory() {
        try {
            const container = document.getElementById('transcription-history-list');
            if (!container) return;
            container.innerHTML = '<div style="color:#8b949e">Loading...</div>';

            const q = document.getElementById('transcription-history-search')?.value || '';
            const resp = await fetch(`/api/transcriptions/history?limit=100`);
            if (!resp.ok) {
                container.innerHTML = `<div style="color:#f85149">Failed to load history (${resp.status})</div>`;
                return;
            }

            const json = await resp.json();
            if (!json.success) {
                container.innerHTML = `<div style="color:#f85149">${json.error || 'Failed to load history'}</div>`;
                return;
            }

            let items = json.history || [];
            if (q) {
                const ql = q.toLowerCase();
                items = items.filter(i => (i.transcript || '').toLowerCase().includes(ql) || (i.model_used || '').toLowerCase().includes(ql));
            }

            if (items.length === 0) {
                container.innerHTML = '<div style="color:#8b949e">No transcriptions yet.</div>';
                return;
            }

            container.innerHTML = '';
            items.forEach(it => {
                const div = document.createElement('div');
                div.style.cssText = 'padding:8px; border-bottom:1px solid rgba(48,54,61,0.6);';
                const dt = new Date(it.created_at);
                div.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:8px;">
                        <div style="font-size:13px; color:var(--text-primary);">${(it.transcript || '').slice(0, 200)}</div>
                        <div style="font-size:11px; color:#8b949e; text-align:right; min-width:120px;">${it.model_used || ''}<br>${dt.toLocaleString()}</div>
                    </div>
                `;
                div.addEventListener('click', () => {
                    // Show full transcript in live display
                    this.displayFileTranscript(it.transcript || '', `Transcript ${it.id}`);
                });
                container.appendChild(div);
            });

        } catch (err) {
            console.error('[TRANSCRIPTION] loadTranscriptionHistory error:', err);
        }
    }

    /**
     * Create transcript entry HTML element
     */
    createTranscriptEntry(transcript) {
        const entry = document.createElement('div');
        entry.className = 'transcription-transcript-entry';
        entry.dataset.source = transcript.source || 'unknown';
        entry.dataset.timestamp = transcript.timestamp;
        entry.dataset.text = transcript.text;

        // Make draggable
        entry.draggable = true;
        entry.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', transcript.text);
            e.dataTransfer.setData('application/transcript', JSON.stringify(transcript));
            entry.classList.add('dragging');
            console.log('[TRANSCRIPTION] Drag started:', transcript.text.substring(0, 50));
        });
        entry.addEventListener('dragend', (e) => {
            entry.classList.remove('dragging');
        });

        const time = new Date(transcript.timestamp).toLocaleTimeString();
        const date = new Date(transcript.timestamp).toLocaleDateString();

        // Source badge with color coding
        const sourceBadge = transcript.source === 'sidebar'
            ? '<span class="transcript-source-badge sidebar" title="Recorded in sidebar"><i class="fas fa-sidebar"></i> Sidebar</span>'
            : transcript.source === 'chat'
                ? '<span class="transcript-source-badge chat" title="Recorded via chat button"><i class="fas fa-comments"></i> Chat</span>'
                : '<span class="transcript-source-badge unknown"><i class="fas fa-question"></i> Unknown</span>';

        // Audio source badge
        const audioSource = transcript.audioSource || 'unknown';
        const audioBadge = audioSource === 'system'
            ? '<span class="transcript-audio-badge system" title="Desktop/Tab audio"><i class="fas fa-desktop"></i> System</span>'
            : audioSource === 'microphone'
                ? '<span class="transcript-audio-badge microphone" title="Microphone input"><i class="fas fa-microphone"></i> Mic</span>'
                : '';

        entry.innerHTML = `
            <div class="transcription-transcript-header">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="transcription-transcript-time">${time}</span>
                    ${sourceBadge}
                    ${audioBadge}
                </div>
                <div class="transcription-transcript-actions" style="position: relative;">
                    <button class="send-to-chat-btn" data-timestamp="${transcript.timestamp}" title="Send to Chat">
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

        // Add click handler for send button to show dropdown
        const sendBtn = entry.querySelector('.send-to-chat-btn');
        if (sendBtn) {
            sendBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.showDestinationDropdown(sendBtn, transcript);
            });
        }

        // Add inline styles for source badges (only once)
        const style = document.createElement('style');
        if (!document.getElementById('transcript-source-badge-styles')) {
            style.id = 'transcript-source-badge-styles';
            style.textContent = `
                .transcript-source-badge {
                    display: inline-flex;
                    align-items: center;
                    gap: 4px;
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                .transcript-source-badge.sidebar {
                    background: rgba(56, 139, 253, 0.15);
                    color: #58a6ff;
                    border: 1px solid rgba(56, 139, 253, 0.3);
                }
                .transcript-source-badge.chat {
                    background: rgba(35, 134, 54, 0.15);
                    color: #3fb950;
                    border: 1px solid rgba(35, 134, 54, 0.3);
                }
                .transcript-source-badge.unknown {
                    background: rgba(255, 255, 255, 0.05);
                    color: #8b949e;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
                .transcript-audio-badge {
                    display: inline-flex;
                    align-items: center;
                    gap: 4px;
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                .transcript-audio-badge.system {
                    background: rgba(168, 85, 247, 0.15);
                    color: #a855f7;
                    border: 1px solid rgba(168, 85, 247, 0.3);
                }
                .transcript-audio-badge.microphone {
                    background: rgba(249, 115, 22, 0.15);
                    color: #f97316;
                    border: 1px solid rgba(249, 115, 22, 0.3);
                }
            `;
            document.head.appendChild(style);
        }

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
     * Show dropdown to choose destination (AI Prime or specific agent)
     */
    showDestinationDropdown(button, transcript) {
        // Remove any existing dropdown
        document.querySelectorAll('.transcript-destination-dropdown').forEach(d => d.remove());

        const dropdown = document.createElement('div');
        dropdown.className = 'transcript-destination-dropdown show';

        // Get available agents
        const agents = [];

        // Add AI Prime option
        agents.push({
            id: 'ai-prime',
            name: 'AI Prime',
            icon: 'fas fa-crown',
            inputId: 'ai-chat-input'
        });

        // Get active agent columns (same logic as showAgentSelectorDropdown)
        document.querySelectorAll('.agent-column').forEach(column => {
            const messagesDiv = column.querySelector('[id^="agent-messages-"]');
            if (messagesDiv) {
                const agentId = messagesDiv.id.replace('agent-messages-', '');
                const nameElement = column.querySelector('.agent-name');
                const agentName = nameElement ? nameElement.textContent.trim() : `Agent ${agentId}`;
                const inputId = `input-${agentId}`;

                agents.push({
                    id: `agent-${agentId}`,
                    name: agentName,
                    icon: 'fas fa-robot',
                    inputId: inputId
                });
            }
        });

        // Build dropdown HTML
        let html = '';
        agents.forEach((agent, index) => {
            if (index > 0) html += '<div class="transcript-destination-divider"></div>';
            html += `
                <div class="transcript-destination-option" data-input-id="${agent.inputId}">
                    <i class="${agent.icon}"></i>
                    <span>${agent.name}</span>
                </div>
            `;
        });

        dropdown.innerHTML = html;

        // Add click handlers
        dropdown.querySelectorAll('.transcript-destination-option').forEach(option => {
            option.addEventListener('click', () => {
                const inputId = option.dataset.inputId;
                this.insertTranscriptToInput(transcript, inputId, button);
                dropdown.remove();
            });
        });

        // Position dropdown
        button.parentElement.style.position = 'relative';
        button.parentElement.appendChild(dropdown);

        // Close on outside click
        setTimeout(() => {
            document.addEventListener('click', function closeDropdown(e) {
                if (!dropdown.contains(e.target) && e.target !== button) {
                    dropdown.remove();
                    document.removeEventListener('click', closeDropdown);
                }
            });
        }, 100);

        console.log(`[TRANSCRIPTION] Showing destination dropdown with ${agents.length} options`);
    }

    /**
     * Insert transcript to specific input element
     */
    insertTranscriptToInput(transcript, inputId, button) {
        const insertMode = this.config.insertMode || 'append';

        // Check if it's an agent input (use AgentInput module)
        if (inputId.startsWith('input-')) {
            const agentId = inputId.replace('input-', '');

            if (window.AgentInput && typeof window.AgentInput.setValue === 'function') {
                const currentValue = window.AgentInput.getValue(agentId) || '';

                if (insertMode === 'replace') {
                    window.AgentInput.setValue(agentId, transcript.text);
                } else {
                    const newValue = currentValue.trim() ? currentValue + ' ' + transcript.text : transcript.text;
                    window.AgentInput.setValue(agentId, newValue);
                }

                window.AgentInput.focus(agentId);

                // Visual feedback
                const icon = button.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-check';
                    setTimeout(() => {
                        icon.className = 'fas fa-paper-plane';
                    }, 1000);
                }

                console.log(`[TRANSCRIPTION] Transcript inserted to agent ${agentId}`);
                return;
            }
        }

        // Fallback: Direct input element manipulation
        const input = document.getElementById(inputId);
        if (!input) {
            console.error(`[TRANSCRIPTION] Input not found: ${inputId}`);
            alert('Target input not found. Please make sure the chat is visible.');
            return;
        }

        // Insert text
        if (insertMode === 'replace') {
            input.value = transcript.text;
        } else {
            const currentText = input.value.trim();
            input.value = currentText ? currentText + ' ' + transcript.text : transcript.text;
        }

        // Focus and trigger events
        input.focus();
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));

        // Visual feedback
        const icon = button.querySelector('i');
        if (icon) {
            icon.className = 'fas fa-check';
            setTimeout(() => {
                icon.className = 'fas fa-paper-plane';
            }, 1000);
        }

        console.log(`[TRANSCRIPTION] Transcript inserted to ${inputId}`);
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
    /**
     * Show agent selector dropdown (similar to Communication Hub pattern)
     */
    showAgentSelectorDropdown(event) {
        event.stopPropagation();
        const button = event.currentTarget;

        // Remove any existing dropdown
        const existingDropdown = document.getElementById('transcript-agent-dropdown');
        if (existingDropdown) {
            existingDropdown.remove();
            return;
        }

        // Get transcript text
        const liveDisplay = document.getElementById('transcription-live-display');
        if (!liveDisplay) return;

        const textSegments = Array.from(liveDisplay.querySelectorAll('.final'))
            .map(el => el.textContent.trim())
            .filter(text => text.length > 0);

        const fullText = textSegments.join(' ');

        if (!fullText) {
            alert('No transcript text to send');
            return;
        }

        // Get list of active agents (from MultiAgent system)
        const agents = [];

        // Check for active agent columns
        document.querySelectorAll('.agent-column').forEach(column => {
            const messagesDiv = column.querySelector('[id^="agent-messages-"]');
            if (messagesDiv) {
                const agentId = messagesDiv.id.replace('agent-messages-', '');
                const nameElement = column.querySelector('.agent-name');
                const agentName = nameElement ? nameElement.textContent.trim() : `Agent ${agentId}`;
                agents.push({ id: agentId, name: agentName });
            }
        });

        // Create dropdown
        const dropdown = document.createElement('div');
        dropdown.id = 'transcript-agent-dropdown';
        dropdown.style.cssText = `
            position: fixed;
            background: #1c1f26;
            border: 1px solid #30363d;
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            z-index: 10000;
            min-width: 250px;
            max-width: 300px;
            overflow: hidden;
        `;

        // Position dropdown below button
        const rect = button.getBoundingClientRect();
        dropdown.style.top = `${rect.bottom + 5}px`;
        dropdown.style.left = `${rect.left}px`;

        // Build dropdown HTML
        let html = '<div style="padding: 8px 0;">';

        // Header
        html += `
            <div style="padding: 8px 12px; border-bottom: 1px solid #30363d; margin-bottom: 4px;">
                <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px;">Send Transcript To</div>
                <div style="font-size: 10px; color: #6b7280; margin-top: 2px;">${fullText.substring(0, 50)}...</div>
            </div>
        `;

        // AI Prime option
        html += `
            <div class="agent-option" data-target="prime"
                 style="padding: 10px 12px; cursor: pointer; display: flex; align-items: center; gap: 10px;"
                 onmouseover="this.style.background='rgba(99, 102, 241, 0.1)'" 
                 onmouseout="this.style.background='transparent'">
                <i class="fas fa-crown" style="color: #fbbf24; width: 20px; text-align: center; font-size: 16px;"></i>
                <div style="flex: 1;">
                    <div style="font-size: 13px; color: #f0f6fc; font-weight: 600;">AI Prime</div>
                    <div style="font-size: 10px; color: #8b949e; margin-top: 2px;">Main chat interface</div>
                </div>
            </div>
        `;

        // Agent options
        if (agents.length > 0) {
            html += '<div style="border-top: 1px solid #21262d; margin: 4px 0;"></div>';
            agents.forEach(agent => {
                html += `
                    <div class="agent-option" data-target="agent-${agent.id}"
                         style="padding: 10px 12px; cursor: pointer; display: flex; align-items: center; gap: 10px;"
                         onmouseover="this.style.background='rgba(99, 102, 241, 0.1)'" 
                         onmouseout="this.style.background='transparent'">
                        <i class="fas fa-robot" style="color: #6366f1; width: 20px; text-align: center; font-size: 16px;"></i>
                        <div style="flex: 1;">
                            <div style="font-size: 13px; color: #f0f6fc; font-weight: 500;">${agent.name}</div>
                        </div>
                    </div>
                `;
            });
        } else {
            html += `
                <div style="padding: 20px; text-align: center; color: #8b949e;">
                    <i class="fas fa-robot" style="font-size: 24px; margin-bottom: 8px; display: block; opacity: 0.5;"></i>
                    <div style="font-size: 12px;">No agents available</div>
                </div>
            `;
        }

        html += '</div>';
        dropdown.innerHTML = html;

        // Append to body
        document.body.appendChild(dropdown);

        // Add click handlers for agent options
        dropdown.querySelectorAll('.agent-option').forEach(option => {
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                const target = option.dataset.target;
                dropdown.remove();
                this.sendLiveTranscriptToChat(target, fullText);
            });
        });

        // Close on outside click
        setTimeout(() => {
            const closeHandler = (e) => {
                if (!dropdown.contains(e.target) && !button.contains(e.target)) {
                    dropdown.remove();
                    document.removeEventListener('click', closeHandler);
                }
            };
            document.addEventListener('click', closeHandler);
        }, 100);
    }

    /**
     * Send live transcript to specific chat target
     * @param {string} target - Target ID ('prime' or 'agent-{id}')
     * @param {string} text - Transcript text (optional, will extract if not provided)
     */
    sendLiveTranscriptToChat(target = 'prime', text = null) {
        // Get transcript text if not provided
        if (!text) {
            const liveDisplay = document.getElementById('transcription-live-display');
            if (!liveDisplay) return;

            const textSegments = Array.from(liveDisplay.querySelectorAll('.final'))
                .map(el => el.textContent.trim())
                .filter(t => t.length > 0);

            text = textSegments.join(' ');
        }

        if (!text) {
            console.error('[TRANSCRIPTION SIDEBAR] No transcript text to send');
            return;
        }

        let chatInput = null;
        let targetName = '';

        // Route to appropriate target
        if (target === 'prime') {
            chatInput = document.getElementById('ai-chat-input');
            targetName = 'AI Prime';
        } else if (target.startsWith('agent-')) {
            const agentId = target.replace('agent-', '');
            chatInput = document.getElementById(`input-${agentId}`);
            targetName = `Agent ${agentId}`;

            // Also use AgentInput module if available
            if (window.AgentInput && typeof window.AgentInput.setValue === 'function') {
                const insertMode = this.config.insertMode || 'append';
                const currentValue = window.AgentInput.getValue(agentId) || '';

                if (insertMode === 'replace') {
                    window.AgentInput.setValue(agentId, text);
                } else {
                    const newValue = currentValue.trim() ? currentValue + ' ' + text : text;
                    window.AgentInput.setValue(agentId, newValue);
                }

                window.AgentInput.focus(agentId);
                console.log(`[TRANSCRIPTION SIDEBAR] Transcript sent to ${targetName}`);
                this.showSuccessFeedback(`Sent to ${targetName}`);
                return;
            }
        }

        if (chatInput) {
            const insertMode = this.config.insertMode || 'append';

            if (insertMode === 'replace') {
                chatInput.value = text;
            } else if (insertMode === 'append') {
                const currentText = chatInput.value.trim();
                chatInput.value = currentText ? currentText + ' ' + text : text;
            }

            chatInput.focus();
            chatInput.dispatchEvent(new Event('input', { bubbles: true }));

            console.log(`[TRANSCRIPTION SIDEBAR] Transcript sent to ${targetName}`);
            this.showSuccessFeedback(`Sent to ${targetName}`);
        } else {
            console.error(`[TRANSCRIPTION SIDEBAR] Chat input not found for target: ${target}`);
            alert(`Could not find chat input for ${targetName}`);
        }
    }

    /**
     * Show success feedback message
     */
    showSuccessFeedback(message) {
        // Try to use global notification system
        if (typeof showNotification === 'function') {
            showNotification(message, 'success');
        } else {
            // Fallback: Show temporary message
            const feedback = document.createElement('div');
            feedback.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #238636;
                color: white;
                padding: 12px 20px;
                border-radius: 6px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                z-index: 10001;
                font-size: 14px;
                font-weight: 600;
            `;
            feedback.innerHTML = `<i class="fas fa-check-circle" style="margin-right: 8px;"></i>${message}`;
            document.body.appendChild(feedback);

            setTimeout(() => {
                feedback.style.opacity = '0';
                feedback.style.transition = 'opacity 0.3s';
                setTimeout(() => feedback.remove(), 300);
            }, 2000);
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
     * Helper: Get language name from code
     */
    getLanguageName(code) {
        const languages = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
            'it': 'Italian', 'pt': 'Portuguese', 'nl': 'Dutch', 'ru': 'Russian',
            'zh': 'Chinese', 'ja': 'Japanese', 'ko': 'Korean', 'ar': 'Arabic',
            'hi': 'Hindi', 'pl': 'Polish', 'tr': 'Turkish', 'vi': 'Vietnamese',
            'th': 'Thai', 'sv': 'Swedish', 'no': 'Norwegian', 'da': 'Danish',
            'fi': 'Finnish', 'uk': 'Ukrainian', 'el': 'Greek', 'cs': 'Czech'
        };
        return languages[code] || code.toUpperCase();
    }

    /**
     * Helper: Format duration in seconds to MM:SS
     */
    formatDuration(seconds) {
        if (!seconds || isNaN(seconds)) return '--';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    /**
     * Helper: Get audio duration from blob
     */
    async getAudioDuration(audioBlob) {
        return new Promise((resolve) => {
            const audio = new Audio();
            audio.addEventListener('loadedmetadata', () => {
                resolve(audio.duration);
            });
            audio.addEventListener('error', () => {
                resolve(null);
            });
            audio.src = URL.createObjectURL(audioBlob);
        });
    }

    /**
     * Helper: Download transcript as text file
     */
    downloadTranscript(filename) {
        const liveDisplay = document.getElementById('transcription-live-display');
        if (!liveDisplay) return;

        const transcripts = liveDisplay.querySelectorAll('.final');
        if (transcripts.length === 0) {
            alert('No transcript to download');
            return;
        }

        let text = '';
        transcripts.forEach(t => {
            text += t.textContent + '\n\n';
        });

        const blob = new Blob([text.trim()], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename.replace(/\.[^.]+$/, '') + '_transcript.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log('[TRANSCRIPTION SIDEBAR] Transcript downloaded:', a.download);
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

    getAdvancedSettings() {
        return {
            wordTimestamps: document.getElementById('transcription-word-timestamps')?.checked || false,
            speakerDiarization: document.getElementById('transcription-speaker-diarization')?.checked || false,
            qualityMetrics: document.getElementById('transcription-quality-metrics')?.checked || false,
            languageDetection: document.getElementById('transcription-language-detection')?.checked || false,
            vadPreprocessing: document.getElementById('transcription-vad-preprocessing')?.checked || false,
            exportFormat: document.getElementById('transcription-export-format')?.value || 'text',
            minSpeakers: parseInt(document.getElementById('transcription-min-speakers')?.value || 1),
            maxSpeakers: parseInt(document.getElementById('transcription-max-speakers')?.value || 5)
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

    saveEngineSettings() {
        const selected = document.querySelector('input[name="live-engine"]:checked')?.value || 'browser';
        const stored = localStorage.getItem('transcription-stt-settings');
        const settings = stored ? JSON.parse(stored) : {};
        settings.liveEngine = selected;
        localStorage.setItem('transcription-stt-settings', JSON.stringify(settings));
        console.log('[TRANSCRIPTION SIDEBAR] Engine settings saved:', selected);
        const labels = {
            'browser': 'Browser STT', 'assemblyai': 'AssemblyAI Streaming',
            'openai-realtime': 'OpenAI Realtime', 'deepgram': 'Deepgram Nova-3', 'speechmatics': 'Speechmatics'
        };
        alert(`Engine saved: ${labels[selected] || selected}`);
    }

    async checkEnginesStatus() {
        try {
            const resp = await fetch('/api/transcription/engines-status', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` }
            });
            if (!resp.ok) return;
            const data = await resp.json();
            const engines = data.engines || {};

            // Map: platform key → live engine status element + upload chip id
            const statusMap = [
                { key: 'assemblyai',   elId: 'assemblyai-key-status',       radioId: 'engine-assemblyai',      uploadId: 'upload-engine-assemblyai', name: 'AssemblyAI',       fallbackEngine: 'browser' },
                { key: 'openai',       elId: 'openai-realtime-key-status',  radioId: 'engine-openai-realtime', uploadId: 'upload-engine-openai',     name: 'OpenAI Realtime',  fallbackEngine: 'browser' },
                { key: 'deepgram',     elId: 'deepgram-key-status',         radioId: 'engine-deepgram',        uploadId: 'upload-engine-deepgram',   name: 'Deepgram',         fallbackEngine: 'browser' },
                { key: 'speechmatics', elId: 'speechmatics-key-status',     radioId: 'engine-speechmatics',    uploadId: 'upload-engine-speechmatics', name: 'Speechmatics',   fallbackEngine: 'browser' },
            ];

            const stored = localStorage.getItem('transcription-stt-settings');
            const settings = stored ? JSON.parse(stored) : {};

            for (const entry of statusMap) {
                const el = document.getElementById(entry.elId);
                const radio = document.getElementById(entry.radioId);
                const uploadRadio = document.getElementById(entry.uploadId);
                const uploadLabel = uploadRadio ? uploadRadio.closest('label') : null;
                const hasKey = engines[entry.key]?.available === true;

                // Live engine status badge
                if (el) {
                    el.innerHTML = hasKey
                        ? '<i class="fas fa-check-circle" style="color:#3fb950"></i> API key configured'
                        : `<i class="fas fa-times-circle" style="color:#e3b341"></i> No key &mdash; add ${entry.name} in Org Connections`;
                }

                // Disable live engine radio if no key
                if (radio) radio.disabled = !hasKey;

                // Grey out upload chip if no key; fall back to local if selected
                if (uploadRadio) {
                    uploadRadio.disabled = !hasKey;
                    if (uploadLabel) {
                        uploadLabel.style.opacity = hasKey ? '' : '0.45';
                        uploadLabel.style.cursor = hasKey ? '' : 'not-allowed';
                        uploadLabel.title = hasKey ? uploadLabel.title : `${entry.name} — no API key configured`;
                    }
                    if (!hasKey && uploadRadio.checked) {
                        const localRadio = document.getElementById('upload-engine-local');
                        if (localRadio) localRadio.checked = true;
                    }
                }

                // Fall back to browser if selected live engine lost its key
                if (!hasKey && settings.liveEngine === (radio ? radio.value : '')) {
                    const browserRadio = document.getElementById('engine-browser');
                    if (browserRadio) browserRadio.checked = true;
                }
            }

            // Update upload engine status hint
            const uploadStatusEl = document.getElementById('upload-engine-status');
            if (uploadStatusEl) {
                const localAvail = engines.local_whisper?.available === true;
                uploadStatusEl.innerHTML = localAvail
                    ? '<i class="fas fa-check-circle" style="color:#3fb950"></i> Local Whisper ready'
                    : '<i class="fas fa-info-circle" style="color:#e3b341"></i> Local Whisper may be limited on this server &mdash; API engines available above';
            }
        } catch (e) {
            console.warn('[TRANSCRIPTION SIDEBAR] Engine status check failed:', e);
        }
    }

    async checkAssemblyAIKey() {
        const statusEl = document.getElementById('assemblyai-key-status');
        if (!statusEl) return;
        statusEl.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Checking&hellip;';
        try {
            const resp = await fetch('/api/transcription/assemblyai-status', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` }
            });
            if (!resp.ok) {
                statusEl.innerHTML = '<i class="fas fa-times-circle" style="color:#f85149"></i> Error checking key';
                return;
            }
            const data = await resp.json();
            if (data.has_key) {
                statusEl.innerHTML = '<i class="fas fa-check-circle" style="color:#3fb950"></i> API key configured';
                document.getElementById('engine-assemblyai').disabled = false;
            } else {
                statusEl.innerHTML = '<i class="fas fa-times-circle" style="color:#e3b341"></i> No key &mdash; add AssemblyAI in Org Connections';
                document.getElementById('engine-assemblyai').disabled = true;
                // Fall back to browser if assemblyai was selected but no key
                const stored = localStorage.getItem('transcription-stt-settings');
                const settings = stored ? JSON.parse(stored) : {};
                if (settings.liveEngine === 'assemblyai') {
                    const browserRadio = document.getElementById('engine-browser');
                    if (browserRadio) browserRadio.checked = true;
                }
            }
        } catch (e) {
            statusEl.innerHTML = '<i class="fas fa-times-circle" style="color:#f85149"></i> Error checking key';
        }
    }

    saveTTSSettings() {
        const settings = this.getTTSSettings();
        localStorage.setItem('transcription-tts-settings', JSON.stringify(settings));
        console.log('[TRANSCRIPTION SIDEBAR] TTS settings saved:', settings);

        alert('TTS settings saved successfully');
    }

    saveAdvancedSettings() {
        const settings = this.getAdvancedSettings();
        localStorage.setItem('transcription-advanced-settings', JSON.stringify(settings));
        console.log('[TRANSCRIPTION SIDEBAR] Advanced settings saved:', settings);

        // Show features status
        const features = [];
        if (settings.wordTimestamps) features.push('Word Timestamps');
        if (settings.speakerDiarization) features.push('Speaker Diarization');
        if (settings.qualityMetrics) features.push('Quality Metrics');
        if (settings.languageDetection) features.push('Language Detection');
        if (settings.vadPreprocessing) features.push('VAD Preprocessing');

        const message = features.length > 0
            ? `Advanced settings saved!\n\nEnabled features:\n- ${features.join('\n- ')}`
            : 'Advanced settings saved (all features disabled)';

        alert(message);
    }

    loadAdvancedSettings() {
        const settingsJson = localStorage.getItem('transcription-advanced-settings');
        if (settingsJson) {
            try {
                const settings = JSON.parse(settingsJson);
                if (document.getElementById('transcription-word-timestamps')) {
                    document.getElementById('transcription-word-timestamps').checked = settings.wordTimestamps ?? true;
                }
                if (document.getElementById('transcription-speaker-diarization')) {
                    document.getElementById('transcription-speaker-diarization').checked = settings.speakerDiarization ?? false;
                }
                if (document.getElementById('transcription-quality-metrics')) {
                    document.getElementById('transcription-quality-metrics').checked = settings.qualityMetrics ?? true;
                }
                if (document.getElementById('transcription-language-detection')) {
                    document.getElementById('transcription-language-detection').checked = settings.languageDetection ?? true;
                }
                if (document.getElementById('transcription-vad-preprocessing')) {
                    document.getElementById('transcription-vad-preprocessing').checked = settings.vadPreprocessing ?? false;
                }
                if (document.getElementById('transcription-export-format')) {
                    document.getElementById('transcription-export-format').value = settings.exportFormat || 'text';
                }
                if (document.getElementById('transcription-min-speakers')) {
                    document.getElementById('transcription-min-speakers').value = settings.minSpeakers || 1;
                }
                if (document.getElementById('transcription-max-speakers')) {
                    document.getElementById('transcription-max-speakers').value = settings.maxSpeakers || 5;
                }
                console.log('[TRANSCRIPTION SIDEBAR] Advanced settings loaded:', settings);
            } catch (error) {
                console.error('[TRANSCRIPTION SIDEBAR] Failed to load advanced settings:', error);
            }
        }
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

                // Restore saved engine selection
                const savedEngine = settings.liveEngine || 'browser';
                const engineRadio = document.getElementById(`engine-${savedEngine}`);
                if (engineRadio) engineRadio.checked = true;

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

        // Load advanced settings
        this.loadAdvancedSettings();

        // Check all engine key statuses (async, non-blocking)
        this.checkEnginesStatus();
    }
}

// Export as singleton
window.TranscriptionSidebar = new TranscriptionSidebarController();

console.log('[TRANSCRIPTION SIDEBAR] Exported to window.TranscriptionSidebar');
