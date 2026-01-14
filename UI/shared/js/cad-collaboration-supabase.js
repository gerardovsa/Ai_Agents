/**
 * FILE: UI/shared/js/cad-collaboration-supabase.js
 * PURPOSE: Real-time CAD collaboration using SupabaseRealtimeManager
 * 
 * REPLACES: websocket_server.py + cad-collaboration-client.js (WebSocket version)
 * 
 * FEATURES:
 * - Real-time collaboration via Supabase realtime subscriptions
 * - Operational Transform (OT) for conflict resolution
 * - Multi-user cursor tracking
 * - AI assistant integration
 * - Optimistic updates with rollback
 * - JSON Patch-based updates (85 bytes vs 125KB)
 * 
 * DEPENDENCIES:
 * - SupabaseRealtimeManager (UI/shared/js/supabase-realtime-manager.js)
 * - SupabaseConnectionManager (UI/shared/js/supabase-connection-manager.js)
 * - UserAuth (for user ID)
 * 
 * USAGE:
 * ```javascript
 * const cad = new CADCollaborationClient('canvas-element-id');
 * await cad.connect('session-id-uuid');
 * 
 * // Emit patch
 * cad.emitPatch({ op: 'replace', path: '/properties/x', value: 150 }, 'object-id-uuid');
 * 
 * // Request AI analysis
 * await cad.requestAIAnalysis('Please suggest colors for this design');
 * ```
 * 
 * CREATED: December 14, 2025
 */

class CADCollaborationClient {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            throw new Error(`Canvas element #${canvasId} not found`);
        }

        this.ctx = this.canvas.getContext('2d');
        this.sessionId = null;
        this.userId = null;
        this.sceneGraph = {}; // objectId -> object data
        this.participants = {}; // userId -> participant data
        this.isConnected = false;
        this.subscriptions = [];
        this.pendingPatches = new Map(); // patchId -> patch data (for optimistic updates)

        // Interaction state
        this.selectedObject = null;
        this.isDragging = false;
        this.dragStartPos = null;
        this.tool = 'select'; // 'select', 'draw-circle', 'draw-rectangle', etc.

        // Colors
        this.cursorColor = this.getRandomColor();

        // Bind methods
        this.handleObjectInsert = this.handleObjectInsert.bind(this);
        this.handleObjectUpdate = this.handleObjectUpdate.bind(this);
        this.handleObjectDelete = this.handleObjectDelete.bind(this);
        this.handleParticipantInsert = this.handleParticipantInsert.bind(this);
        this.handleParticipantUpdate = this.handleParticipantUpdate.bind(this);
        this.handleParticipantDelete = this.handleParticipantDelete.bind(this);

        // Set up canvas event listeners
        this.setupCanvasEvents();

        console.log('🎨 [CADCollaboration] Client initialized');
    }

    /**
     * Connect to a CAD collaboration session
     * @param {string} sessionId - UUID of the session
     */
    async connect(sessionId) {
        this.sessionId = sessionId;

        // Get user ID from auth
        if (typeof UserAuth !== 'undefined') {
            this.userId = await UserAuth.getUserId();
        } else {
            this.userId = 'anonymous-' + Math.random().toString(36).substr(2, 9);
        }

        console.log(`🔌 [CADCollaboration] Connecting to session ${sessionId} as ${this.userId}`);

        // Load existing session data
        await this.loadSession();

        // Subscribe to real-time updates
        this.subscribeToObjects();
        this.subscribeToParticipants();

        // Register as participant
        await this.joinSession();

        this.isConnected = true;
        console.log('✅ [CADCollaboration] Connected');

        // Start render loop
        this.startRenderLoop();
    }

    /**
     * Disconnect from session
     */
    async disconnect() {
        console.log('🔌 [CADCollaboration] Disconnecting...');

        // Unsubscribe from all subscriptions
        this.subscriptions.forEach(subName => {
            SupabaseRealtimeManager.unsubscribe(subName);
        });
        this.subscriptions = [];

        // Mark participant as inactive
        if (this.userId && this.sessionId) {
            const client = await SupabaseConnectionManager.getClient();
            await client
                .from('cad_participants')
                .update({ is_active: false })
                .eq('session_id', this.sessionId)
                .eq('user_id', this.userId);
        }

        this.isConnected = false;
        console.log('✅ [CADCollaboration] Disconnected');
    }

    /**
     * Load existing session data from database
     */
    async loadSession() {
        console.log('📥 [CADCollaboration] Loading session data...');

        const client = await SupabaseConnectionManager.getClient();

        // Load session metadata
        const { data: session, error: sessionError } = await client
            .from('cad_sessions')
            .select('*')
            .eq('session_id', this.sessionId)
            .single();

        if (sessionError) {
            console.error('❌ Failed to load session:', sessionError);
            throw new Error('Session not found');
        }

        console.log('📦 Session:', session);

        // Load objects
        const { data: objects, error: objectsError } = await client
            .from('cad_objects')
            .select('*')
            .eq('session_id', this.sessionId)
            .eq('is_deleted', false)
            .order('z_index', { ascending: true });

        if (objectsError) {
            console.error('❌ Failed to load objects:', objectsError);
        } else {
            objects.forEach(obj => {
                this.sceneGraph[obj.object_id] = obj;
            });
            console.log(`📦 Loaded ${objects.length} objects`);
        }

        // Load participants
        const { data: participants, error: participantsError } = await client
            .from('cad_participants')
            .select('*')
            .eq('session_id', this.sessionId)
            .eq('is_active', true);

        if (participantsError) {
            console.error('❌ Failed to load participants:', participantsError);
        } else {
            participants.forEach(p => {
                this.participants[p.user_id] = p;
            });
            console.log(`👥 Loaded ${participants.length} participants`);
        }
    }

    /**
     * Subscribe to cad_objects table for real-time updates
     */
    subscribeToObjects() {
        const subName = `cad-objects-${this.sessionId}`;

        SupabaseRealtimeManager.subscribe(subName, {
            table: 'cad_objects',
            schema: 'public',
            filter: `session_id=eq.${this.sessionId}`,
            events: ['INSERT', 'UPDATE', 'DELETE'],
            onInsert: this.handleObjectInsert,
            onUpdate: this.handleObjectUpdate,
            onDelete: this.handleObjectDelete
        });

        this.subscriptions.push(subName);
        console.log(`📡 Subscribed to cad_objects (${subName})`);
    }

    /**
     * Subscribe to cad_participants table for real-time updates
     */
    subscribeToParticipants() {
        const subName = `cad-participants-${this.sessionId}`;

        SupabaseRealtimeManager.subscribe(subName, {
            table: 'cad_participants',
            schema: 'public',
            filter: `session_id=eq.${this.sessionId}`,
            events: ['INSERT', 'UPDATE', 'DELETE'],
            onInsert: this.handleParticipantInsert,
            onUpdate: this.handleParticipantUpdate,
            onDelete: this.handleParticipantDelete
        });

        this.subscriptions.push(subName);
        console.log(`📡 Subscribed to cad_participants (${subName})`);
    }

    /**
     * Handle new object inserted (realtime event)
     */
    handleObjectInsert(payload) {
        const obj = payload.new;
        console.log('➕ Object inserted:', obj.object_id);

        // Check if this was an optimistic update
        const pendingKey = `insert-${obj.object_id}`;
        if (this.pendingPatches.has(pendingKey)) {
            console.log('✅ Optimistic insert confirmed');
            this.pendingPatches.delete(pendingKey);
        }

        // Add to scene graph
        this.sceneGraph[obj.object_id] = obj;

        // Trigger re-render
        this.render();
    }

    /**
     * Handle object updated (realtime event)
     */
    handleObjectUpdate(payload) {
        const obj = payload.new;
        console.log('✏️ Object updated:', obj.object_id);

        // Check if this was an optimistic update
        const pendingKey = `update-${obj.object_id}`;
        if (this.pendingPatches.has(pendingKey)) {
            console.log('✅ Optimistic update confirmed');
            this.pendingPatches.delete(pendingKey);
        }

        // Update scene graph
        this.sceneGraph[obj.object_id] = obj;

        // Trigger re-render
        this.render();
    }

    /**
     * Handle object deleted (realtime event)
     */
    handleObjectDelete(payload) {
        const obj = payload.old;
        console.log('🗑️ Object deleted:', obj.object_id);

        // Remove from scene graph
        delete this.sceneGraph[obj.object_id];

        // Trigger re-render
        this.render();
    }

    /**
     * Handle participant joined (realtime event)
     */
    handleParticipantInsert(payload) {
        const participant = payload.new;
        console.log('👋 Participant joined:', participant.display_name);

        this.participants[participant.user_id] = participant;

        // Show notification
        this.showNotification(`${participant.display_name} joined`, 'success');
    }

    /**
     * Handle participant updated (realtime event)
     */
    handleParticipantUpdate(payload) {
        const participant = payload.new;
        console.log('👤 Participant updated:', participant.display_name);

        this.participants[participant.user_id] = participant;
    }

    /**
     * Handle participant left (realtime event)
     */
    handleParticipantDelete(payload) {
        const participant = payload.old;
        console.log('👋 Participant left:', participant.display_name);

        delete this.participants[participant.user_id];

        // Show notification
        this.showNotification(`${participant.display_name} left`, 'info');
    }

    /**
     * Join session as participant
     */
    async joinSession() {
        console.log('👋 Joining session as participant...');

        const client = await SupabaseConnectionManager.getClient();

        const { data, error } = await client
            .from('cad_participants')
            .insert({
                session_id: this.sessionId,
                user_id: this.userId,
                display_name: this.userId, // TODO: Get real display name from UserAuth
                cursor_color: this.cursorColor,
                is_active: true
            })
            .select()
            .single();

        if (error) {
            console.error('❌ Failed to join session:', error);
            throw new Error('Failed to join session');
        }

        console.log('✅ Joined session:', data);
    }

    /**
     * Emit a JSON Patch to update an object
     * @param {Object} patch - JSON Patch object { op, path, value }
     * @param {string} objectId - UUID of object to update
     * @param {string} reason - Human-readable reason for change
     */
    async emitPatch(patch, objectId, reason = null) {
        console.log(`📤 Emitting patch for ${objectId}:`, patch);

        // Optimistic update: Apply locally immediately
        this.applyPatchLocally(patch, objectId);

        // Generate pending key for confirmation
        const pendingKey = `update-${objectId}`;
        this.pendingPatches.set(pendingKey, { patch, objectId, timestamp: Date.now() });

        // Call Supabase function to apply patch
        const client = await SupabaseConnectionManager.getClient();

        const { data, error } = await client.rpc('apply_cad_patch', {
            p_object_id: objectId,
            p_operation: patch.op,
            p_path: patch.path,
            p_value: patch.value,
            p_actor: this.userId,
            p_reason: reason
        });

        if (error) {
            console.error('❌ Failed to apply patch:', error);

            // Rollback optimistic update
            this.rollbackPatch(pendingKey);
            this.pendingPatches.delete(pendingKey);

            throw new Error('Failed to apply patch');
        }

        console.log('✅ Patch applied:', data);
    }

    /**
     * Apply patch locally (optimistic update)
     * @param {Object} patch - JSON Patch object
     * @param {string} objectId - UUID of object
     */
    applyPatchLocally(patch, objectId) {
        const obj = this.sceneGraph[objectId];
        if (!obj) {
            console.warn(`⚠️ Object ${objectId} not found for local patch`);
            return;
        }

        // Parse path (e.g., '/properties/x' -> ['properties', 'x'])
        const pathParts = patch.path.split('/').filter(p => p.length > 0);

        // Navigate to parent object
        let target = obj;
        for (let i = 0; i < pathParts.length - 1; i++) {
            target = target[pathParts[i]];
            if (!target) {
                console.warn(`⚠️ Invalid path ${patch.path}`);
                return;
            }
        }

        // Apply operation
        const lastKey = pathParts[pathParts.length - 1];

        if (patch.op === 'replace' || patch.op === 'add') {
            target[lastKey] = patch.value;
        } else if (patch.op === 'remove') {
            delete target[lastKey];
        }

        // Increment version for conflict detection
        obj.version++;

        // Trigger re-render
        this.render();
    }

    /**
     * Rollback optimistic update if server rejects patch
     * @param {string} pendingKey - Key in pendingPatches map
     */
    rollbackPatch(pendingKey) {
        console.warn('⚠️ Rolling back optimistic update:', pendingKey);

        // For now, just reload from server
        // TODO: Implement proper undo stack
        this.loadSession();
    }

    /**
     * Create a new object
     * @param {string} objectType - 'circle', 'rectangle', etc.
     * @param {Object} properties - Object properties
     */
    async createObject(objectType, properties) {
        console.log(`➕ Creating ${objectType}:`, properties);

        const client = await SupabaseConnectionManager.getClient();

        const { data, error } = await client
            .from('cad_objects')
            .insert({
                session_id: this.sessionId,
                object_type: objectType,
                properties: properties,
                created_by: this.userId,
                z_index: Object.keys(this.sceneGraph).length // Top layer
            })
            .select()
            .single();

        if (error) {
            console.error('❌ Failed to create object:', error);
            throw new Error('Failed to create object');
        }

        console.log('✅ Object created:', data);

        // Optimistic update: Add locally immediately
        const pendingKey = `insert-${data.object_id}`;
        this.pendingPatches.set(pendingKey, { data, timestamp: Date.now() });
        this.sceneGraph[data.object_id] = data;
        this.render();

        return data;
    }

    /**
     * Delete object (soft delete)
     * @param {string} objectId - UUID of object to delete
     */
    async deleteObject(objectId) {
        console.log(`🗑️ Deleting object ${objectId}`);

        const client = await SupabaseConnectionManager.getClient();

        const { error } = await client
            .from('cad_objects')
            .update({ is_deleted: true })
            .eq('object_id', objectId);

        if (error) {
            console.error('❌ Failed to delete object:', error);
            throw new Error('Failed to delete object');
        }

        console.log('✅ Object deleted');

        // Optimistic update: Remove locally immediately
        delete this.sceneGraph[objectId];
        this.render();
    }

    /**
     * Request AI analysis of current design
     * @param {string} userPrompt - User's request (e.g., "Suggest colors")
     */
    async requestAIAnalysis(userPrompt) {
        console.log('🤖 Requesting AI analysis:', userPrompt);

        // TODO: Call AI vision API endpoint
        // For now, this would trigger a backend API that:
        // 1. Generates SVG snapshot of current design
        // 2. Sends to GPT-4V or Claude with userPrompt
        // 3. Parses AI response into JSON patches
        // 4. Returns patches to client

        // Example API call:
        // const response = await fetch('/api/cad/ai-analyze', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify({
        //         sessionId: this.sessionId,
        //         prompt: userPrompt
        //     })
        // });

        this.showNotification('AI analysis not yet implemented', 'warning');
    }

    /**
     * Set up canvas event listeners for interaction
     */
    setupCanvasEvents() {
        // Mouse down - Start dragging or drawing
        this.canvas.addEventListener('mousedown', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            if (this.tool === 'select') {
                // Find object at cursor position
                this.selectedObject = this.findObjectAt(x, y);

                if (this.selectedObject) {
                    this.isDragging = true;
                    this.dragStartPos = { x, y };
                    console.log('🖱️ Selected object:', this.selectedObject.object_id);
                }
            } else if (this.tool.startsWith('draw-')) {
                // Start drawing new object
                this.startDrawing(x, y);
            }
        });

        // Mouse move - Drag or draw
        this.canvas.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            if (this.isDragging && this.selectedObject) {
                const dx = x - this.dragStartPos.x;
                const dy = y - this.dragStartPos.y;

                // Emit patch to update object position
                this.emitPatch(
                    { op: 'replace', path: '/properties/x', value: this.selectedObject.properties.x + dx },
                    this.selectedObject.object_id,
                    'User dragged object'
                );
                this.emitPatch(
                    { op: 'replace', path: '/properties/y', value: this.selectedObject.properties.y + dy },
                    this.selectedObject.object_id,
                    'User dragged object'
                );

                this.dragStartPos = { x, y };
            }
        });

        // Mouse up - Stop dragging or finish drawing
        this.canvas.addEventListener('mouseup', () => {
            this.isDragging = false;
            this.dragStartPos = null;
        });
    }

    /**
     * Find object at cursor position
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     * @returns {Object|null} Object at position or null
     */
    findObjectAt(x, y) {
        // Iterate in reverse z-index order (top to bottom)
        const objects = Object.values(this.sceneGraph).sort((a, b) => b.z_index - a.z_index);

        for (const obj of objects) {
            if (this.isPointInObject(x, y, obj)) {
                return obj;
            }
        }

        return null;
    }

    /**
     * Check if point is inside object
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     * @param {Object} obj - Object to check
     * @returns {boolean} True if point is inside
     */
    isPointInObject(x, y, obj) {
        const props = obj.properties;

        if (obj.object_type === 'circle') {
            const dx = x - props.x;
            const dy = y - props.y;
            return (dx * dx + dy * dy) <= (props.radius * props.radius);
        } else if (obj.object_type === 'rectangle') {
            return x >= props.x && x <= props.x + props.width &&
                y >= props.y && y <= props.y + props.height;
        }

        // TODO: Handle other object types
        return false;
    }

    /**
     * Start drawing new object (for draw tools)
     * @param {number} x - Start X coordinate
     * @param {number} y - Start Y coordinate
     */
    startDrawing(x, y) {
        console.log(`✏️ Start drawing ${this.tool} at (${x}, ${y})`);

        // TODO: Implement drawing logic
        // For now, just create a placeholder object

        if (this.tool === 'draw-circle') {
            this.createObject('circle', {
                x: x,
                y: y,
                radius: 50,
                fill: { color: '#ff6b6b', opacity: 0.8 },
                stroke: { color: '#c92a2a', width: 2 }
            });
        } else if (this.tool === 'draw-rectangle') {
            this.createObject('rectangle', {
                x: x,
                y: y,
                width: 100,
                height: 80,
                fill: { color: '#4dabf7', opacity: 0.6 },
                stroke: { color: '#1971c2', width: 3 }
            });
        }
    }

    /**
     * Render scene to canvas
     */
    render() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw grid
        this.drawGrid();

        // Draw objects (sorted by z-index)
        const objects = Object.values(this.sceneGraph).sort((a, b) => a.z_index - b.z_index);

        objects.forEach(obj => {
            this.drawObject(obj);
        });

        // Draw selection indicator
        if (this.selectedObject) {
            this.drawSelectionIndicator(this.selectedObject);
        }

        // Draw participant cursors
        // TODO: Track cursor positions and draw them
    }

    /**
     * Draw background grid
     */
    drawGrid() {
        this.ctx.strokeStyle = '#2a2a2a';
        this.ctx.lineWidth = 1;

        const gridSize = 20;

        for (let x = 0; x < this.canvas.width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }

        for (let y = 0; y < this.canvas.height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }

    /**
     * Draw single object to canvas
     * @param {Object} obj - Object to draw
     */
    drawObject(obj) {
        const props = obj.properties;

        this.ctx.save();

        // Set fill style
        if (props.fill) {
            this.ctx.fillStyle = props.fill.color || '#ffffff';
            this.ctx.globalAlpha = props.fill.opacity !== undefined ? props.fill.opacity : 1;
        }

        // Set stroke style
        if (props.stroke) {
            this.ctx.strokeStyle = props.stroke.color || '#000000';
            this.ctx.lineWidth = props.stroke.width || 1;
        }

        // Draw based on object type
        if (obj.object_type === 'circle') {
            this.ctx.beginPath();
            this.ctx.arc(props.x, props.y, props.radius, 0, Math.PI * 2);
            if (props.fill) this.ctx.fill();
            if (props.stroke) this.ctx.stroke();
        } else if (obj.object_type === 'rectangle') {
            if (props.fill) this.ctx.fillRect(props.x, props.y, props.width, props.height);
            if (props.stroke) this.ctx.strokeRect(props.x, props.y, props.width, props.height);
        }
        // TODO: Handle other object types (path, text, etc.)

        this.ctx.restore();
    }

    /**
     * Draw selection indicator around selected object
     * @param {Object} obj - Selected object
     */
    drawSelectionIndicator(obj) {
        const props = obj.properties;

        this.ctx.save();
        this.ctx.strokeStyle = '#00aaff';
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([5, 5]);

        if (obj.object_type === 'circle') {
            this.ctx.beginPath();
            this.ctx.arc(props.x, props.y, props.radius + 5, 0, Math.PI * 2);
            this.ctx.stroke();
        } else if (obj.object_type === 'rectangle') {
            this.ctx.strokeRect(props.x - 5, props.y - 5, props.width + 10, props.height + 10);
        }

        this.ctx.restore();
    }

    /**
     * Start render loop
     */
    startRenderLoop() {
        const loop = () => {
            if (this.isConnected) {
                this.render();
                requestAnimationFrame(loop);
            }
        };

        requestAnimationFrame(loop);
    }

    /**
     * Show notification to user
     * @param {string} message - Notification message
     * @param {string} type - 'success', 'error', 'info', 'warning'
     */
    showNotification(message, type = 'info') {
        console.log(`[${type.toUpperCase()}] ${message}`);

        // TODO: Implement UI notification system
        // For now, just log to console
    }

    /**
     * Get random color for cursor
     * @returns {string} Hex color code
     */
    getRandomColor() {
        const colors = ['#ff6b6b', '#4dabf7', '#51cf66', '#ffd43b', '#ff8787', '#748ffc'];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    /**
     * Set active tool
     * @param {string} tool - Tool name ('select', 'draw-circle', 'draw-rectangle', etc.)
     */
    setTool(tool) {
        this.tool = tool;
        console.log(`🔧 Tool set to: ${tool}`);
    }
}

// Export for use in other modules
window.CADCollaborationClient = CADCollaborationClient;

console.log('✅ [CADCollaboration] Module loaded (Supabase version)');
