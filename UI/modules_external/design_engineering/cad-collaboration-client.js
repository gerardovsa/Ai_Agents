/**
 * CAD Collaboration Client
 * Real-time collaboration between humans and AI
 */

class CADCollaborationClient {
    constructor(sessionId, canvasElement) {
        this.sessionId = sessionId;
        this.canvas = canvasElement;
        this.ctx = canvasElement.getContext('2d');

        // WebSocket connection
        this.ws = null;
        this.participantId = null;
        this.isConnected = false;

        // Scene state
        this.sceneGraph = null;
        this.version = 0;

        // UI state
        this.selectedObjects = [];
        this.hoveredObject = null;
        this.isDragging = false;
        this.dragStart = null;
        this.dragObject = null;

        // Collaboration state
        this.participants = new Map(); // participant_id -> {cursor, selection, type}
        this.aiCursorPosition = null;
        this.aiFocusedObjects = [];
        this.aiThinking = null;

        // Pending patches (for optimistic updates)
        this.pendingPatches = [];

        // Event handlers
        this.onStateUpdate = null;
        this.onAISuggestion = null;
        this.onError = null;

        console.log('[CAD CLIENT] Initialized for session:', sessionId);
    }

    /**
     * Connect to collaboration server
     */
    async connect() {
        const wsUrl = `ws://localhost:8000/ws/cad/${this.sessionId}`;
        console.log('[CAD CLIENT] Connecting to:', wsUrl);

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('[CAD CLIENT] Connected');
            this.isConnected = true;
            this.startHeartbeat();
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };

        this.ws.onerror = (error) => {
            console.error('[CAD CLIENT] WebSocket error:', error);
            if (this.onError) {
                this.onError(error);
            }
        };

        this.ws.onclose = () => {
            console.log('[CAD CLIENT] Disconnected');
            this.isConnected = false;
            this.stopHeartbeat();
        };
    }

    /**
     * Disconnect from server
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    /**
     * Send heartbeat to keep connection alive
     */
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected) {
                this.send({ type: 'PING' });
            }
        }, 30000); // Every 30 seconds
    }

    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }
    }

    /**
     * Send message to server
     */
    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.warn('[CAD CLIENT] Not connected, cannot send message');
        }
    }

    /**
     * Handle incoming messages
     */
    handleMessage(message) {
        console.log('[CAD CLIENT] Received:', message.type);

        switch (message.type) {
            case 'INITIAL_STATE':
                this.handleInitialState(message);
                break;

            case 'PATCH':
                this.handlePatch(message);
                break;

            case 'PATCH_APPLIED':
                this.handlePatchApplied(message);
                break;

            case 'PATCH_REJECTED':
                this.handlePatchRejected(message);
                break;

            case 'AI_SUGGESTION':
                this.handleAISuggestion(message);
                break;

            case 'AI_ANALYZING':
                this.showAIThinking(message.message);
                break;

            case 'AI_RESPONSE':
                this.handleAIResponse(message);
                break;

            case 'AI_CURSOR':
                this.handleAICursor(message);
                break;

            case 'PARTICIPANT_JOINED':
                this.handleParticipantJoined(message);
                break;

            case 'PARTICIPANT_LEFT':
                this.handleParticipantLeft(message);
                break;

            case 'PARTICIPANT_CURSOR':
                this.handleParticipantCursor(message);
                break;

            case 'PARTICIPANT_SELECTION':
                this.handleParticipantSelection(message);
                break;

            case 'PONG':
                // Heartbeat response
                break;

            default:
                console.warn('[CAD CLIENT] Unknown message type:', message.type);
        }
    }

    /**
     * Handle initial state from server
     */
    handleInitialState(message) {
        this.sceneGraph = message.data;
        this.version = message.data.metadata.version;
        this.participantId = message.participant_id;

        console.log('[CAD CLIENT] Received initial state, version:', this.version);

        this.render();

        if (this.onStateUpdate) {
            this.onStateUpdate(this.sceneGraph);
        }
    }

    /**
     * Handle patch from other participant or AI
     */
    handlePatch(message) {
        const patch = message.patch;

        console.log(`[CAD CLIENT] Applying patch from ${message.from_participant}:`, patch.path);

        // Apply patch to local state
        this.applyPatchToLocal(patch);
        this.version = message.version;

        // Show AI explanation if available
        if (patch.actor === 'ai' && patch.reason) {
            this.showAIExplanation(patch.reason, patch);
        }

        // Re-render
        this.render();

        if (this.onStateUpdate) {
            this.onStateUpdate(this.sceneGraph);
        }
    }

    /**
     * Handle patch applied confirmation
     */
    handlePatchApplied(message) {
        // Remove from pending patches
        this.pendingPatches = this.pendingPatches.filter(
            p => p.patch_id !== message.patch_id
        );

        this.version = message.version;
        console.log('[CAD CLIENT] Patch applied, new version:', this.version);
    }

    /**
     * Handle patch rejected
     */
    handlePatchRejected(message) {
        console.error('[CAD CLIENT] Patch rejected:', message.error);

        // Remove from pending
        const rejectedPatch = this.pendingPatches.find(
            p => p.patch_id === message.patch_id
        );
        this.pendingPatches = this.pendingPatches.filter(
            p => p.patch_id !== message.patch_id
        );

        // Revert optimistic update
        if (rejectedPatch) {
            this.revertPatch(rejectedPatch);
            this.render();
        }

        // Show error to user
        this.showError(`Change rejected: ${message.error}`);
    }

    /**
     * Handle AI suggestion
     */
    handleAISuggestion(message) {
        console.log('[CAD CLIENT] AI suggestion:', message.explanation);

        this.aiThinking = null;

        if (this.onAISuggestion) {
            this.onAISuggestion({
                patches: message.patches,
                explanation: message.explanation,
                previewSvg: message.preview_svg
            });
        }

        this.render();
    }

    /**
     * Handle AI response to question
     */
    handleAIResponse(message) {
        console.log('[CAD CLIENT] AI response:', message.answer);

        // Show AI response in UI
        this.showAIResponse(message);
    }

    /**
     * Handle AI cursor update
     */
    handleAICursor(message) {
        this.aiFocusedObjects = message.object_ids;
        this.render();
    }

    /**
     * Handle participant events
     */
    handleParticipantJoined(message) {
        console.log('[CAD CLIENT] Participant joined:', message.participant_id);
        this.participants.set(message.participant_id, {
            type: message.participant_type,
            cursor: null,
            selection: []
        });
    }

    handleParticipantLeft(message) {
        console.log('[CAD CLIENT] Participant left:', message.participant_id);
        this.participants.delete(message.participant_id);
        this.render();
    }

    handleParticipantCursor(message) {
        const participant = this.participants.get(message.participant_id);
        if (participant) {
            participant.cursor = message.position;
            this.render();
        }
    }

    handleParticipantSelection(message) {
        const participant = this.participants.get(message.participant_id);
        if (participant) {
            participant.selection = message.object_ids;
            this.render();
        }
    }

    /**
     * Apply patch to local scene graph
     */
    applyPatchToLocal(patch) {
        const parts = patch.path.split('/').filter(p => p);

        if (patch.op === 'add' || patch.op === 'replace') {
            // Navigate to parent
            let current = this.sceneGraph;
            for (let i = 0; i < parts.length - 1; i++) {
                current = current[parts[i]];
            }
            // Set value
            current[parts[parts.length - 1]] = patch.value;
        }
        else if (patch.op === 'remove') {
            // Navigate to parent
            let current = this.sceneGraph;
            for (let i = 0; i < parts.length - 1; i++) {
                current = current[parts[i]];
            }
            // Delete value
            delete current[parts[parts.length - 1]];
        }
    }

    /**
     * Revert a patch (for rejected optimistic updates)
     */
    revertPatch(patch) {
        // TODO: Implement proper patch reversal
        // For now, just log
        console.warn('[CAD CLIENT] Reverting patch:', patch.path);
    }

    /**
     * User creates a patch
     */
    emitPatch(op, path, value, reason = null) {
        const patch = {
            op: op,
            path: path,
            value: value,
            actor: 'human',
            timestamp: new Date().toISOString(),
            reason: reason,
            patch_id: this.generateUUID()
        };

        // Optimistic update
        this.applyPatchToLocal(patch);
        this.pendingPatches.push(patch);
        this.render();

        // Send to server
        this.send({
            type: 'PATCH',
            patch: patch
        });

        return patch;
    }

    /**
     * User modifies object
     */
    modifyObject(objectId, changes) {
        const object = this.sceneGraph.objects[objectId];
        if (!object) {
            console.error('[CAD CLIENT] Object not found:', objectId);
            return;
        }

        for (const [key, value] of Object.entries(changes)) {
            this.emitPatch(
                'replace',
                `/objects/${objectId}/${key}`,
                value,
                `User modified ${key}`
            );
        }
    }

    /**
     * User adds new object
     */
    addObject(objectData) {
        const objectId = objectData.id || `obj_${this.generateUUID()}`;

        this.emitPatch(
            'add',
            `/objects/${objectId}`,
            objectData,
            'User added new object'
        );

        return objectId;
    }

    /**
     * User deletes object
     */
    deleteObject(objectId) {
        this.emitPatch(
            'remove',
            `/objects/${objectId}`,
            null,
            'User deleted object'
        );
    }

    /**
     * Ask AI a question
     */
    askAI(question) {
        const context = {
            scene_graph: this.sceneGraph,
            svg_snapshot: this.generateSVGSnapshot(),
            selected_objects: this.selectedObjects
        };

        this.send({
            type: 'AI_REQUEST',
            question: question,
            context: context
        });

        this.showAIThinking(`Analyzing: ${question}`);
    }

    /**
     * Accept AI suggestion
     */
    acceptAISuggestion(patchIds) {
        this.send({
            type: 'APPLY_AI_SUGGESTION',
            patch_ids: patchIds
        });
    }

    /**
     * Render the scene
     */
    render() {
        const ctx = this.ctx;
        const canvas = this.canvas;

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw grid
        this.drawGrid(ctx);

        // Draw objects
        if (this.sceneGraph && this.sceneGraph.objects) {
            for (const [objectId, object] of Object.entries(this.sceneGraph.objects)) {
                this.drawObject(ctx, objectId, object);
            }
        }

        // Draw AI focus highlights
        this.drawAIFocus(ctx);

        // Draw other participants' cursors
        this.drawParticipantCursors(ctx);

        // Draw AI thinking indicator
        if (this.aiThinking) {
            this.drawAIThinking(ctx);
        }

        // Draw selection outlines
        this.drawSelections(ctx);
    }

    /**
     * Draw grid
     */
    drawGrid(ctx) {
        ctx.save();
        ctx.strokeStyle = '#e0e0e0';
        ctx.lineWidth = 1;

        const gridSize = 50;
        for (let x = 0; x < this.canvas.width; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, this.canvas.height);
            ctx.stroke();
        }

        for (let y = 0; y < this.canvas.height; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(this.canvas.width, y);
            ctx.stroke();
        }

        ctx.restore();
    }

    /**
     * Draw object
     */
    drawObject(ctx, objectId, object) {
        if (!object.visible && object.visible !== undefined) {
            return;
        }

        ctx.save();

        // Different rendering based on type
        if (object.type === 't-slot-beam') {
            this.drawBeam(ctx, objectId, object);
        }
        else if (object.type === 'corner-bracket') {
            this.drawBracket(ctx, objectId, object);
        }

        ctx.restore();
    }

    /**
     * Draw T-slot beam
     */
    drawBeam(ctx, objectId, beam) {
        const pos = beam.position;
        const length = beam.length;
        const profileSize = parseInt(beam.profile.split('x')[0]) || 40;

        // Scale to canvas (1mm = 0.5px for now)
        const scale = 0.5;
        const x = pos.x * scale + 100;
        const y = pos.y * scale + 100;
        const w = length * scale;
        const h = profileSize * scale;

        // Draw beam rectangle
        ctx.fillStyle = beam.color || '#A0A0A0';
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 2;

        ctx.fillRect(x, y, w, h);
        ctx.strokeRect(x, y, w, h);

        // Draw T-slots
        ctx.fillStyle = '#666';
        const slotCount = Math.floor(length / 200);
        for (let i = 1; i <= slotCount; i++) {
            const slotX = x + (w * i / (slotCount + 1));
            ctx.fillRect(slotX - 2, y + 2, 4, h - 4);
        }

        // Label
        ctx.fillStyle = '#000';
        ctx.font = '12px sans-serif';
        ctx.fillText(`${length}mm`, x + w / 2 - 20, y - 5);

        // Store bounds for hit testing
        beam._bounds = { x, y, w, h };
    }

    /**
     * Draw bracket
     */
    drawBracket(ctx, objectId, bracket) {
        const pos = bracket.position;
        const scale = 0.5;
        const x = pos.x * scale + 100;
        const y = pos.y * scale + 100;

        ctx.fillStyle = '#888';
        ctx.beginPath();
        ctx.arc(x, y, 8, 0, 2 * Math.PI);
        ctx.fill();
        ctx.stroke();

        bracket._bounds = { x: x - 8, y: y - 8, w: 16, h: 16 };
    }

    /**
     * Draw AI focus highlights
     */
    drawAIFocus(ctx) {
        if (this.aiFocusedObjects.length === 0) return;

        ctx.save();
        ctx.strokeStyle = '#4CAF50';
        ctx.lineWidth = 3;
        ctx.setLineDash([5, 5]);

        for (const objectId of this.aiFocusedObjects) {
            const object = this.sceneGraph.objects[objectId];
            if (object && object._bounds) {
                const b = object._bounds;
                ctx.strokeRect(b.x - 5, b.y - 5, b.w + 10, b.h + 10);
            }
        }

        ctx.restore();
    }

    /**
     * Draw participant cursors
     */
    drawParticipantCursors(ctx) {
        for (const [pid, participant] of this.participants.entries()) {
            if (participant.cursor) {
                this.drawCursor(ctx, participant.cursor, participant.type, pid);
            }
        }

        // Draw AI cursor
        if (this.aiCursorPosition) {
            this.drawCursor(ctx, this.aiCursorPosition, 'ai', 'AI');
        }
    }

    /**
     * Draw cursor
     */
    drawCursor(ctx, position, type, label) {
        const color = type === 'ai' ? '#4CAF50' : '#2196F3';

        ctx.save();
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(position.x, position.y, 8, 0, 2 * Math.PI);
        ctx.fill();

        // Label
        ctx.fillStyle = 'white';
        ctx.font = '12px sans-serif';
        ctx.fillText(type === 'ai' ? '🤖 AI' : `👤 ${label}`, position.x + 15, position.y + 5);
        ctx.restore();
    }

    /**
     * Draw AI thinking indicator
     */
    drawAIThinking(ctx) {
        const dots = '.'.repeat((Math.floor(Date.now() / 500) % 3) + 1);

        ctx.save();
        ctx.fillStyle = 'rgba(76, 175, 80, 0.9)';
        ctx.fillRect(10, 10, 350, 50);

        ctx.fillStyle = 'white';
        ctx.font = '14px sans-serif';
        ctx.fillText(`🤖 ${this.aiThinking}${dots}`, 20, 35);
        ctx.restore();
    }

    /**
     * Draw selection outlines
     */
    drawSelections(ctx) {
        ctx.save();
        ctx.strokeStyle = '#2196F3';
        ctx.lineWidth = 2;

        for (const objectId of this.selectedObjects) {
            const object = this.sceneGraph.objects[objectId];
            if (object && object._bounds) {
                const b = object._bounds;
                ctx.strokeRect(b.x - 3, b.y - 3, b.w + 6, b.h + 6);
            }
        }

        ctx.restore();
    }

    /**
     * UI helpers
     */
    showAIThinking(message) {
        this.aiThinking = message;
        this.render();
    }

    showAIExplanation(reason, patch) {
        console.log('[AI EXPLANATION]', reason);
        // TODO: Show in UI toast/notification
    }

    showAIResponse(response) {
        console.log('[AI RESPONSE]', response.answer);
        // TODO: Show in chat panel
    }

    showError(message) {
        console.error('[ERROR]', message);
        // TODO: Show error toast
    }

    /**
     * Generate SVG snapshot for AI
     */
    generateSVGSnapshot() {
        // TODO: Generate SVG from current scene
        return '<svg>...</svg>';
    }

    /**
     * Utility
     */
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
}


// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CADCollaborationClient;
}
