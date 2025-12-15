/**
 * Multi-Modal Interaction Handlers
 * Mouse, Touch, Voice, and Gesture input for CAD
 */

class CADInteractionHandler {
    constructor(cadClient, canvas) {
        this.client = cadClient;
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        // Interaction mode
        this.mode = 'select'; // 'select', 'move', 'rotate', 'draw-beam', 'draw-connector'

        // Mouse state
        this.mousePos = { x: 0, y: 0 };
        this.mouseDown = false;
        this.dragStart = null;
        this.dragObject = null;
        this.hoveredObject = null;

        // Gesture state
        this.gesturePoints = [];
        this.isDrawingGesture = false;

        // Voice control
        this.voiceController = null;

        // Setup event listeners
        this.setupMouseEvents();
        this.setupTouchEvents();
        this.setupKeyboardEvents();

        console.log('[INTERACTION] Handler initialized');
    }

    /**
     * Mouse/Pointer Events
     */
    setupMouseEvents() {
        this.canvas.addEventListener('mousedown', this.onMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.onMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.onMouseUp.bind(this));
        this.canvas.addEventListener('wheel', this.onWheel.bind(this));
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());
    }

    onMouseDown(event) {
        const point = this.getCanvasPoint(event);
        this.mousePos = point;
        this.mouseDown = true;

        if (this.mode === 'select') {
            // Hit test to find object
            const object = this.hitTest(point);

            if (object) {
                // Select object
                this.client.selectedObjects = [object.id];
                this.dragObject = object;
                this.dragStart = point;

                // Notify server of selection
                this.client.send({
                    type: 'OBJECT_SELECT',
                    object_ids: [object.id]
                });

                this.client.render();
            } else {
                // Deselect
                this.client.selectedObjects = [];
                this.client.render();
            }
        }
        else if (this.mode === 'draw-beam') {
            // Start drawing beam
            this.dragStart = point;
        }
        else if (this.mode === 'gesture') {
            // Start gesture
            this.isDrawingGesture = true;
            this.gesturePoints = [point];
        }
    }

    onMouseMove(event) {
        const point = this.getCanvasPoint(event);
        this.mousePos = point;

        // Send cursor position to server
        this.sendCursorUpdate(point);

        if (!this.mouseDown) {
            // Hover detection
            const hoveredObject = this.hitTest(point);
            if (hoveredObject !== this.hoveredObject) {
                this.hoveredObject = hoveredObject;
                this.canvas.style.cursor = hoveredObject ? 'pointer' : 'default';
            }
            return;
        }

        if (this.mode === 'select' && this.dragObject) {
            // Drag object
            const delta = {
                x: point.x - this.dragStart.x,
                y: point.y - this.dragStart.y
            };

            // Update object position with patch
            const scale = 2; // Inverse of render scale (0.5)
            this.client.modifyObject(this.dragObject.id, {
                position: {
                    x: this.dragObject.position.x + delta.x * scale,
                    y: this.dragObject.position.y + delta.y * scale,
                    z: this.dragObject.position.z
                }
            });

            this.dragStart = point;
        }
        else if (this.mode === 'draw-beam' && this.dragStart) {
            // Preview beam while drawing
            this.drawBeamPreview(this.dragStart, point);
        }
        else if (this.mode === 'gesture' && this.isDrawingGesture) {
            // Collect gesture points
            this.gesturePoints.push(point);
            this.drawGesturePath();
        }
    }

    onMouseUp(event) {
        const point = this.getCanvasPoint(event);
        this.mouseDown = false;

        if (this.mode === 'draw-beam' && this.dragStart) {
            // Create beam
            const length = this.distance(this.dragStart, point);
            if (length > 50) {
                this.createBeam(this.dragStart, point);
            }
            this.dragStart = null;
        }
        else if (this.mode === 'gesture' && this.isDrawingGesture) {
            // Recognize gesture
            this.recognizeGesture();
            this.isDrawingGesture = false;
            this.gesturePoints = [];
        }

        this.dragObject = null;
        this.client.render();
    }

    onWheel(event) {
        event.preventDefault();

        // Zoom functionality
        const delta = event.deltaY > 0 ? 0.9 : 1.1;
        // TODO: Implement zoom
        console.log('[INTERACTION] Zoom:', delta);
    }

    /**
     * Touch Events (for tablets/mobile)
     */
    setupTouchEvents() {
        this.canvas.addEventListener('touchstart', this.onTouchStart.bind(this));
        this.canvas.addEventListener('touchmove', this.onTouchMove.bind(this));
        this.canvas.addEventListener('touchend', this.onTouchEnd.bind(this));
    }

    onTouchStart(event) {
        event.preventDefault();
        const touch = event.touches[0];
        const mouseEvent = new MouseEvent('mousedown', {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        this.onMouseDown(mouseEvent);
    }

    onTouchMove(event) {
        event.preventDefault();
        const touch = event.touches[0];
        const mouseEvent = new MouseEvent('mousemove', {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        this.onMouseMove(mouseEvent);
    }

    onTouchEnd(event) {
        event.preventDefault();
        const mouseEvent = new MouseEvent('mouseup', {});
        this.onMouseUp(mouseEvent);
    }

    /**
     * Keyboard Events
     */
    setupKeyboardEvents() {
        document.addEventListener('keydown', this.onKeyDown.bind(this));
        document.addEventListener('keyup', this.onKeyUp.bind(this));
    }

    onKeyDown(event) {
        // Mode switching
        if (event.key === 's') {
            this.setMode('select');
        }
        else if (event.key === 'd') {
            this.setMode('draw-beam');
        }
        else if (event.key === 'g') {
            this.setMode('gesture');
        }

        // Delete selected objects
        else if (event.key === 'Delete' || event.key === 'Backspace') {
            for (const objectId of this.client.selectedObjects) {
                this.client.deleteObject(objectId);
            }
            this.client.selectedObjects = [];
        }

        // Undo (Ctrl+Z)
        else if (event.ctrlKey && event.key === 'z') {
            console.log('[INTERACTION] Undo');
            // TODO: Implement undo
        }

        // Ask AI (Ctrl+Space)
        else if (event.ctrlKey && event.key === ' ') {
            this.promptAIQuestion();
        }
    }

    onKeyUp(event) {
        // Nothing for now
    }

    /**
     * Set interaction mode
     */
    setMode(mode) {
        this.mode = mode;
        console.log('[INTERACTION] Mode:', mode);

        // Update cursor
        this.canvas.style.cursor = {
            'select': 'default',
            'move': 'move',
            'draw-beam': 'crosshair',
            'gesture': 'crosshair'
        }[mode] || 'default';

        // Update UI
        this.updateModeUI();
    }

    updateModeUI() {
        // Highlight active mode button
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        const activeBtn = document.querySelector(`[data-mode="${this.mode}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
    }

    /**
     * Hit testing
     */
    hitTest(point) {
        if (!this.client.sceneGraph || !this.client.sceneGraph.objects) {
            return null;
        }

        // Test objects in reverse order (top to bottom)
        const objects = Object.entries(this.client.sceneGraph.objects).reverse();

        for (const [objectId, object] of objects) {
            if (object._bounds) {
                const b = object._bounds;
                if (point.x >= b.x && point.x <= b.x + b.w &&
                    point.y >= b.y && point.y <= b.y + b.h) {
                    return { id: objectId, ...object };
                }
            }
        }

        return null;
    }

    /**
     * Create beam from two points
     */
    createBeam(start, end) {
        const length = this.distance(start, end);
        const scale = 2; // Inverse of render scale

        const beamData = {
            type: 't-slot-beam',
            profile: '40x40_standard',
            position: {
                x: (start.x - 100) * scale,
                y: (start.y - 100) * scale,
                z: 0
            },
            length: Math.round(length * scale),
            rotation: { x: 0, y: 0, z: 0 },
            material: '6061-T6',
            color: '#A0A0A0',
            visible: true,
            locked: false,
            created_by: 'human'
        };

        this.client.addObject(beamData);
        console.log('[INTERACTION] Created beam, length:', beamData.length, 'mm');
    }

    /**
     * Draw beam preview
     */
    drawBeamPreview(start, end) {
        const ctx = this.ctx;

        ctx.save();
        ctx.strokeStyle = '#2196F3';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);

        ctx.beginPath();
        ctx.moveTo(start.x, start.y);
        ctx.lineTo(end.x, end.y);
        ctx.stroke();

        // Show length
        const length = this.distance(start, end) * 2; // Scale
        const midX = (start.x + end.x) / 2;
        const midY = (start.y + end.y) / 2;

        ctx.fillStyle = '#2196F3';
        ctx.font = '14px sans-serif';
        ctx.fillText(`${Math.round(length)}mm`, midX + 10, midY - 10);

        ctx.restore();
    }

    /**
     * Gesture Recognition
     */
    recognizeGesture() {
        if (this.gesturePoints.length < 3) {
            return;
        }

        const gesture = this.classifyGesture(this.gesturePoints);
        console.log('[INTERACTION] Gesture recognized:', gesture.type);

        if (gesture.type === 'line') {
            // Draw beam
            this.createBeam(gesture.start, gesture.end);
        }
        else if (gesture.type === 'circle') {
            // Create connector
            this.createConnector(gesture.center);
        }
        else if (gesture.type === 'cross') {
            // Delete object at location
            const object = this.hitTest(gesture.center);
            if (object) {
                this.client.deleteObject(object.id);
            }
        }
        else if (gesture.type === 'check') {
            // Ask AI to validate design
            this.client.askAI('Is this design structurally sound?');
        }
    }

    classifyGesture(points) {
        const start = points[0];
        const end = points[points.length - 1];
        const distance = this.distance(start, end);

        // Straight line
        if (this.isLinear(points) && distance > 50) {
            return {
                type: 'line',
                start: start,
                end: end,
                length: distance
            };
        }

        // Circle
        if (this.isCircular(points)) {
            return {
                type: 'circle',
                center: this.getCenter(points),
                radius: this.getRadius(points)
            };
        }

        // Cross (X shape)
        if (this.isCrossShape(points)) {
            return {
                type: 'cross',
                center: this.getCenter(points)
            };
        }

        // Checkmark
        if (this.isCheckmark(points)) {
            return {
                type: 'check',
                center: this.getCenter(points)
            };
        }

        return { type: 'unknown' };
    }

    isLinear(points) {
        // Check if points form roughly a straight line
        if (points.length < 3) return true;

        const start = points[0];
        const end = points[points.length - 1];
        const lineLength = this.distance(start, end);

        let maxDeviation = 0;
        for (const point of points) {
            const deviation = this.pointToLineDistance(point, start, end);
            maxDeviation = Math.max(maxDeviation, deviation);
        }

        return maxDeviation < lineLength * 0.1; // 10% tolerance
    }

    isCircular(points) {
        // Check if points form roughly a circle
        const center = this.getCenter(points);
        const avgRadius = this.getRadius(points);

        let maxDeviation = 0;
        for (const point of points) {
            const radius = this.distance(point, center);
            const deviation = Math.abs(radius - avgRadius);
            maxDeviation = Math.max(maxDeviation, deviation);
        }

        return maxDeviation < avgRadius * 0.2; // 20% tolerance
    }

    isCrossShape(points) {
        // Simplified: Check for two intersecting lines
        // TODO: Implement proper cross detection
        return false;
    }

    isCheckmark(points) {
        // Simplified: Check for V shape
        // TODO: Implement proper checkmark detection
        return false;
    }

    drawGesturePath() {
        const ctx = this.ctx;

        if (this.gesturePoints.length < 2) return;

        ctx.save();
        ctx.strokeStyle = '#FF9800';
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';

        ctx.beginPath();
        ctx.moveTo(this.gesturePoints[0].x, this.gesturePoints[0].y);

        for (let i = 1; i < this.gesturePoints.length; i++) {
            ctx.lineTo(this.gesturePoints[i].x, this.gesturePoints[i].y);
        }

        ctx.stroke();
        ctx.restore();
    }

    /**
     * Create connector
     */
    createConnector(position) {
        const scale = 2;

        const connectorData = {
            type: 'corner-bracket',
            part_number: 'CB-40-90',
            position: {
                x: (position.x - 100) * scale,
                y: (position.y - 100) * scale,
                z: 0
            },
            angle: 90,
            connected_beams: []
        };

        this.client.addObject(connectorData);
        console.log('[INTERACTION] Created connector at:', position);
    }

    /**
     * Send cursor position to server
     */
    sendCursorUpdate(position) {
        if (!this.cursorUpdateThrottle) {
            this.cursorUpdateThrottle = true;

            this.client.send({
                type: 'CURSOR_MOVE',
                position: position
            });

            setTimeout(() => {
                this.cursorUpdateThrottle = false;
            }, 100); // Throttle to 10Hz
        }
    }

    /**
     * Prompt AI question
     */
    promptAIQuestion() {
        const question = prompt('Ask AI about your design:');
        if (question) {
            this.client.askAI(question);
        }
    }

    /**
     * Utility functions
     */
    getCanvasPoint(event) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top
        };
    }

    distance(p1, p2) {
        const dx = p2.x - p1.x;
        const dy = p2.y - p1.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    pointToLineDistance(point, lineStart, lineEnd) {
        const A = point.x - lineStart.x;
        const B = point.y - lineStart.y;
        const C = lineEnd.x - lineStart.x;
        const D = lineEnd.y - lineStart.y;

        const dot = A * C + B * D;
        const lenSq = C * C + D * D;
        const param = lenSq !== 0 ? dot / lenSq : -1;

        let xx, yy;

        if (param < 0) {
            xx = lineStart.x;
            yy = lineStart.y;
        } else if (param > 1) {
            xx = lineEnd.x;
            yy = lineEnd.y;
        } else {
            xx = lineStart.x + param * C;
            yy = lineStart.y + param * D;
        }

        const dx = point.x - xx;
        const dy = point.y - yy;
        return Math.sqrt(dx * dx + dy * dy);
    }

    getCenter(points) {
        let sumX = 0, sumY = 0;
        for (const p of points) {
            sumX += p.x;
            sumY += p.y;
        }
        return {
            x: sumX / points.length,
            y: sumY / points.length
        };
    }

    getRadius(points) {
        const center = this.getCenter(points);
        let sumRadius = 0;
        for (const p of points) {
            sumRadius += this.distance(p, center);
        }
        return sumRadius / points.length;
    }
}


/**
 * Voice Control for CAD
 */
class VoiceCADController {
    constructor(cadClient) {
        this.client = cadClient;
        this.recognition = null;
        this.isListening = false;

        // Initialize speech recognition
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';

            this.recognition.onresult = this.onResult.bind(this);
            this.recognition.onerror = this.onError.bind(this);
            this.recognition.onend = this.onEnd.bind(this);

            console.log('[VOICE] Controller initialized');
        } else {
            console.warn('[VOICE] Speech recognition not supported');
        }
    }

    start() {
        if (this.recognition && !this.isListening) {
            this.recognition.start();
            this.isListening = true;
            console.log('[VOICE] Listening...');
        }
    }

    stop() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.isListening = false;
            console.log('[VOICE] Stopped');
        }
    }

    onResult(event) {
        const results = event.results[event.results.length - 1];
        const transcript = results[0].transcript.trim().toLowerCase();
        const isFinal = results.isFinal;

        console.log('[VOICE]', isFinal ? 'FINAL:' : 'Interim:', transcript);

        if (isFinal) {
            this.processCommand(transcript);
        }
    }

    onError(event) {
        console.error('[VOICE] Error:', event.error);
    }

    onEnd() {
        if (this.isListening) {
            // Restart if we want continuous listening
            this.recognition.start();
        }
    }

    processCommand(command) {
        console.log('[VOICE] Processing command:', command);

        // Command patterns
        const patterns = {
            move: /move (.*?) (up|down|left|right) (?:by )?(\d+)/i,
            resize: /make (.*?) (longer|shorter|bigger|smaller) (?:by )?(\d+)/i,
            add: /add (?:a )?(.+?) (?:at|to) (.+)/i,
            delete: /delete (.*)/i,
            select: /select (.*)/i,
            ask: /(?:hey ai|ai|copilot) (.+)/i,
            validate: /(?:check|validate|analyze) (?:the )?design/i,
            undo: /undo/i
        };

        // Try to match command
        for (const [type, pattern] of Object.entries(patterns)) {
            const match = command.match(pattern);
            if (match) {
                this.executeCommand(type, match);
                return;
            }
        }

        // If no pattern matches, send to AI
        this.client.askAI(command);
    }

    executeCommand(type, match) {
        if (type === 'move') {
            const [, objectName, direction, amount] = match;
            // TODO: Find object by name and move it
            console.log(`[VOICE] Move ${objectName} ${direction} by ${amount}mm`);
        }
        else if (type === 'resize') {
            const [, objectName, operation, amount] = match;
            console.log(`[VOICE] Resize ${objectName}: ${operation} by ${amount}mm`);
        }
        else if (type === 'ask') {
            const [, question] = match;
            this.client.askAI(question);
        }
        else if (type === 'validate') {
            this.client.askAI('Please analyze this design for structural integrity');
        }
        else if (type === 'undo') {
            // TODO: Undo last action
            console.log('[VOICE] Undo');
        }
    }
}


// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CADInteractionHandler,
        VoiceCADController
    };
}
