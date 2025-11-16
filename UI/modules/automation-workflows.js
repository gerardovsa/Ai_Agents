/**
 * AUTOMATION WORKFLOWS MODULE - JAVASCRIPT
 * 
 * Visual automation canvas with drag-and-drop flow builder
 * AI-interpretable visual workflow creation system
 * Drag workflow slugs to AI chat to activate AI Workflow Designer mode
 * 
 * NO EMOJIS - Font Awesome icons only
 */

class AutomationCanvas {
    constructor() {
        this.shapes = [];
        this.connections = [];
        this.selectedShape = null;
        this.selectedShapes = []; // Multi-select
        this.currentColor = '#58a6ff'; // Default: accent-primary
        this.currentShapeType = 'rectangle';
        this.isDragging = false;
        this.isConnecting = false;
        this.connectionStart = null;
        this.dragOffset = { x: 0, y: 0 };
        this.nextShapeId = 1;
        this.nextConnectionId = 1;

        // Workflow management
        this.workflows = [];
        this.currentWorkflow = null;
        this.workflowSlug = null;
        this.workflowTitle = 'Untitled Workflow';
        this.workflowDescription = '';
        this.workflowStatus = 'draft'; // draft, active, inactive

        // Canvas interaction
        this.isPanning = false;
        this.isSelecting = false;
        this.panStart = { x: 0, y: 0 };
        this.selectionStart = { x: 0, y: 0 };
        this.selectionRect = null;

        // Resize
        this.isResizing = false;
        this.resizeHandle = null;
        this.resizeStart = { x: 0, y: 0, width: 0, height: 0 };

        // Clipboard
        this.clipboard = null;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadWorkflows();
    }

    setupEventListeners() {
        // Shape palette drag-and-drop (floating palette)
        document.querySelectorAll('.floating-shape-item').forEach(item => {
            item.addEventListener('dragstart', (e) => this.handleShapeDragStart(e));
        });

        // Color swatch selection
        document.querySelectorAll('.color-swatch').forEach(swatch => {
            swatch.addEventListener('click', (e) => this.selectColor(e.target.dataset.color));
        });

        // Canvas drop zone
        const canvasWrapper = document.getElementById('automation-canvas-wrapper');
        if (canvasWrapper) {
            canvasWrapper.addEventListener('dragover', (e) => e.preventDefault());
            canvasWrapper.addEventListener('drop', (e) => this.handleCanvasDrop(e));
            canvasWrapper.addEventListener('click', (e) => this.handleCanvasClick(e));
        }

        // Toolbar buttons
        document.getElementById('new-workflow-btn')?.addEventListener('click', () => this.openWorkflowModal());
        document.getElementById('load-workflow-btn')?.addEventListener('click', () => this.showLoadWorkflowDialog());
        document.getElementById('save-workflow-btn')?.addEventListener('click', () => this.saveWorkflow());
        document.getElementById('export-workflow-btn')?.addEventListener('click', () => this.exportToJSON());
        document.getElementById('automation-send-ai-btn')?.addEventListener('click', () => this.sendToAI());

        // Modal buttons
        document.getElementById('close-workflow-modal')?.addEventListener('click', () => this.closeWorkflowModal());
        document.getElementById('cancel-workflow-btn')?.addEventListener('click', () => this.closeWorkflowModal());
        document.getElementById('save-workflow-modal-btn')?.addEventListener('click', () => this.saveWorkflowFromModal());
        document.getElementById('add-category-btn')?.addEventListener('click', () => this.addNewCategory());

        // Modal overlay close on click outside
        document.getElementById('workflow-modal-overlay')?.addEventListener('click', (e) => {
            if (e.target.id === 'workflow-modal-overlay') {
                this.closeWorkflowModal();
            }
        });

        // Title input auto-generate slug
        document.getElementById('workflow-title-input')?.addEventListener('input', (e) => {
            const title = e.target.value;
            const slug = this.generateSlug(title);
            document.getElementById('workflow-slug-input').value = slug ? `workflow_${slug}` : '';
        });

        // Workflow card click to edit
        document.getElementById('workflow-list')?.addEventListener('click', (e) => {
            const card = e.target.closest('.workflow-card');
            if (card && !e.target.closest('.workflow-card-actions')) {
                const workflowId = card.dataset.workflowId;
                this.openWorkflowModal(workflowId);
            }
        });

        // Zoom controls
        document.getElementById('zoom-in-btn')?.addEventListener('click', () => this.zoomIn());
        document.getElementById('zoom-out-btn')?.addEventListener('click', () => this.zoomOut());
        document.getElementById('zoom-reset-btn')?.addEventListener('click', () => this.zoomReset());
        document.getElementById('recenter-btn')?.addEventListener('click', () => this.recenterToShapes());

        // Canvas panning and selection
        const canvas = document.getElementById('automation-canvas');
        if (canvas) {
            canvas.addEventListener('mousedown', (e) => this.handleCanvasMouseDown(e));
            canvas.addEventListener('mousemove', (e) => this.handleCanvasMouseMove(e));
            canvas.addEventListener('mouseup', (e) => this.handleCanvasMouseUp(e));
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Delete
            if (e.key === 'Delete' && (this.selectedShape || this.selectedShapes.length > 0)) {
                e.preventDefault();
                if (this.selectedShapes.length > 0) {
                    this.selectedShapes.forEach(shape => this.deleteShape(shape));
                    this.selectedShapes = [];
                } else if (this.selectedShape) {
                    this.deleteShape(this.selectedShape);
                }
            }
            // Copy (Ctrl+C)
            if (e.ctrlKey && e.key === 'c' && (this.selectedShape || this.selectedShapes.length > 0)) {
                e.preventDefault();
                this.copyShapes();
            }
            // Paste (Ctrl+V)
            if (e.ctrlKey && e.key === 'v' && this.clipboard) {
                e.preventDefault();
                this.pasteShapes();
            }
            // Zoom shortcuts
            if (e.ctrlKey && e.key === '=') {
                e.preventDefault();
                this.zoomIn();
            }
            if (e.ctrlKey && e.key === '-') {
                e.preventDefault();
                this.zoomOut();
            }
            if (e.ctrlKey && e.key === '0') {
                e.preventDefault();
                this.zoomReset();
            }
        });

        // Initialize zoom
        this.currentZoom = 1.0;
        this.updateZoomDisplay();
    }

    handleShapeDragStart(e) {
        const shapeItem = e.target.closest('.floating-shape-item');
        if (!shapeItem) return;
        const shapeType = shapeItem.dataset.shape;
        e.dataTransfer.setData('shapeType', shapeType);
        e.dataTransfer.effectAllowed = 'copy';
    }

    handleCanvasDrop(e) {
        e.preventDefault();
        const shapeType = e.dataTransfer.getData('shapeType');
        if (!shapeType) return;

        const canvas = document.getElementById('automation-canvas-wrapper');
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left - 75; // Center shape
        const y = e.clientY - rect.top - 40;

        this.createShape(shapeType, x, y);
    }

    createShape(type, x, y, text = '', color = null, id = null) {
        const shapeId = id || `shape_${this.nextShapeId++}`;
        const shapeColor = color || this.currentColor;

        const shape = {
            id: shapeId,
            type: type,
            x: x,
            y: y,
            width: 150,
            height: 80,
            text: text,
            color: shapeColor
        };

        this.shapes.push(shape);
        this.renderShape(shape);
        return shape;
    }

    renderShape(shape) {
        const canvas = document.getElementById('automation-canvas-wrapper');
        const shapeEl = document.createElement('div');
        shapeEl.className = `automation-shape ${shape.type}`;
        shapeEl.id = shape.id;
        shapeEl.style.left = `${shape.x}px`;
        shapeEl.style.top = `${shape.y}px`;
        shapeEl.style.width = `${shape.width}px`;
        shapeEl.style.height = `${shape.height}px`;
        shapeEl.style.borderColor = shape.color;
        shapeEl.draggable = true;

        // Type label (above shape)
        const typeLabel = document.createElement('div');
        typeLabel.className = 'shape-type-label';
        typeLabel.textContent = this.getShapeTypeLabel(shape.type);

        // Text input
        const textInput = document.createElement('textarea');
        textInput.className = 'shape-text-input';
        textInput.placeholder = 'Enter text...';
        textInput.value = shape.text;
        textInput.addEventListener('input', (e) => {
            shape.text = e.target.value;
            this.autoResizeShape(shape, shapeEl);
        });
        textInput.addEventListener('click', (e) => e.stopPropagation());

        // Shape controls
        const controls = document.createElement('div');
        controls.className = 'shape-controls';
        controls.innerHTML = `
            <button class="shape-control-btn" title="Change color" onclick="automationCanvas.showColorPicker('${shape.id}')">
                <i class="fas fa-palette"></i>
            </button>
            <button class="shape-control-btn" title="Change shape" onclick="automationCanvas.showShapePicker('${shape.id}')">
                <i class="fas fa-shapes"></i>
            </button>
            <button class="shape-control-btn delete" title="Delete" onclick="automationCanvas.deleteShape('${shape.id}')">
                <i class="fas fa-trash"></i>
            </button>
        `;

        // Resize handle
        const resizeHandle = document.createElement('div');
        resizeHandle.className = 'shape-resize-handle';
        resizeHandle.addEventListener('mousedown', (e) => this.startResize(e, shape, shapeEl));

        // Connection points
        const connectionPoints = ['top', 'right', 'bottom', 'left'].map(pos => {
            const point = document.createElement('div');
            point.className = `connection-point ${pos}`;
            point.addEventListener('mousedown', (e) => this.startConnection(e, shape, pos));
            return point;
        });

        shapeEl.appendChild(typeLabel);
        shapeEl.appendChild(textInput);
        shapeEl.appendChild(controls);
        shapeEl.appendChild(resizeHandle);
        connectionPoints.forEach(p => shapeEl.appendChild(p));

        // Dragging
        shapeEl.addEventListener('dragstart', (e) => this.startDragShape(e, shape));
        shapeEl.addEventListener('drag', (e) => this.dragShape(e, shape));
        shapeEl.addEventListener('dragend', (e) => this.endDragShape(e, shape));

        // Selection
        shapeEl.addEventListener('click', (e) => {
            e.stopPropagation();
            this.selectShape(shape.id);
        });

        canvas.appendChild(shapeEl);
    }

    autoResizeShape(shape, shapeEl) {
        const textInput = shapeEl.querySelector('.shape-text-input');
        if (!textInput) return;

        // Calculate required size based on text
        const lines = textInput.value.split('\n').length;
        const minHeight = Math.max(80, (lines * 20) + 40);
        const minWidth = Math.max(150, textInput.value.length * 8);

        shape.height = minHeight;
        shape.width = Math.min(minWidth, 400);

        shapeEl.style.height = `${shape.height}px`;
        shapeEl.style.width = `${shape.width}px`;
    }

    selectShape(shapeId) {
        // Deselect previous
        if (this.selectedShape) {
            document.getElementById(this.selectedShape)?.classList.remove('selected');
        }

        // Select new
        this.selectedShape = shapeId;
        document.getElementById(shapeId)?.classList.add('selected');
    }

    deleteShape(shapeId) {
        // Remove from shapes array
        this.shapes = this.shapes.filter(s => s.id !== shapeId);

        // Remove connections
        this.connections = this.connections.filter(c =>
            c.from !== shapeId && c.to !== shapeId
        );

        // Remove from DOM
        document.getElementById(shapeId)?.remove();

        // Clear selection
        if (this.selectedShape === shapeId) {
            this.selectedShape = null;
        }

        this.renderConnections();
    }

    startDragShape(e, shape) {
        const shapeEl = document.getElementById(shape.id);
        const rect = shapeEl.getBoundingClientRect();
        this.dragOffset = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
        shapeEl.classList.add('dragging');
        this.isDragging = true;
    }

    dragShape(e, shape) {
        if (!this.isDragging || e.clientX === 0) return;

        const canvas = document.getElementById('automation-canvas-wrapper');
        const rect = canvas.getBoundingClientRect();

        shape.x = e.clientX - rect.left - this.dragOffset.x;
        shape.y = e.clientY - rect.top - this.dragOffset.y;

        const shapeEl = document.getElementById(shape.id);
        shapeEl.style.left = `${shape.x}px`;
        shapeEl.style.top = `${shape.y}px`;

        this.renderConnections();
    }

    endDragShape(e, shape) {
        document.getElementById(shape.id)?.classList.remove('dragging');
        this.isDragging = false;
    }

    startResize(e, shape, shapeEl) {
        e.stopPropagation();
        e.preventDefault();

        const startX = e.clientX;
        const startY = e.clientY;
        const startWidth = shape.width;
        const startHeight = shape.height;

        const handleMouseMove = (e) => {
            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;

            shape.width = Math.max(100, startWidth + deltaX);
            shape.height = Math.max(60, startHeight + deltaY);

            shapeEl.style.width = `${shape.width}px`;
            shapeEl.style.height = `${shape.height}px`;

            this.renderConnections();
        };

        const handleMouseUp = () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    }

    startConnection(e, shape, position) {
        e.stopPropagation();
        e.preventDefault();

        this.isConnecting = true;
        this.connectionStart = { shape: shape.id, position: position };

        // Visual feedback
        const canvas = document.getElementById('automation-canvas-wrapper');
        const tempLine = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        tempLine.id = 'temp-connection-line';
        tempLine.style.position = 'absolute';
        tempLine.style.top = '0';
        tempLine.style.left = '0';
        tempLine.style.width = '100%';
        tempLine.style.height = '100%';
        tempLine.style.pointerEvents = 'none';
        tempLine.style.zIndex = '100';
        canvas.appendChild(tempLine);

        const handleMouseMove = (e) => {
            if (!this.isConnecting) return;

            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            const startPoint = this.getConnectionPoint(shape, position);
            tempLine.innerHTML = `
                <line x1="${startPoint.x}" y1="${startPoint.y}" 
                      x2="${mouseX}" y2="${mouseY}" 
                      stroke="#58a6ff" stroke-width="2" stroke-dasharray="5,5"/>
            `;
        };

        const handleMouseUp = (e) => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);

            // Check if dropped on another shape
            const target = e.target.closest('.automation-shape');
            if (target && target.id !== shape.id) {
                this.createConnection(shape.id, target.id);
            }

            this.isConnecting = false;
            this.connectionStart = null;
            document.getElementById('temp-connection-line')?.remove();
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    }

    createConnection(fromId, toId) {
        // Check if connection already exists
        const exists = this.connections.some(c =>
            (c.from === fromId && c.to === toId) ||
            (c.from === toId && c.to === fromId)
        );

        if (exists) return;

        const connection = {
            id: `conn_${this.nextConnectionId++}`,
            from: fromId,
            to: toId
        };

        this.connections.push(connection);
        this.renderConnections();
    }

    getConnectionPoint(shape, position) {
        const shapeEl = document.getElementById(shape.id);
        if (!shapeEl) return { x: 0, y: 0 };

        const rect = shapeEl.getBoundingClientRect();
        const canvas = document.getElementById('automation-canvas-wrapper');
        const canvasRect = canvas.getBoundingClientRect();

        const relX = rect.left - canvasRect.left;
        const relY = rect.top - canvasRect.top;

        switch (position) {
            case 'top':
                return { x: relX + shape.width / 2, y: relY };
            case 'right':
                return { x: relX + shape.width, y: relY + shape.height / 2 };
            case 'bottom':
                return { x: relX + shape.width / 2, y: relY + shape.height };
            case 'left':
                return { x: relX, y: relY + shape.height / 2 };
            default:
                return { x: relX + shape.width / 2, y: relY + shape.height / 2 };
        }
    }

    renderConnections() {
        // Remove existing SVG
        document.getElementById('connections-svg')?.remove();

        if (this.connections.length === 0) return;

        // Create new SVG
        const canvas = document.getElementById('automation-canvas-wrapper');
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.id = 'connections-svg';
        svg.style.position = 'absolute';
        svg.style.top = '0';
        svg.style.left = '0';
        svg.style.width = '100%';
        svg.style.height = '100%';
        svg.style.pointerEvents = 'none';
        svg.style.zIndex = '1';

        // Define arrowhead marker
        svg.innerHTML = `
            <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="10" 
                        refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
                    <path d="M0,0 L0,6 L9,3 z" fill="#58a6ff" />
                </marker>
            </defs>
        `;

        // Draw connections
        this.connections.forEach(conn => {
            const fromShape = this.shapes.find(s => s.id === conn.from);
            const toShape = this.shapes.find(s => s.id === conn.to);

            if (!fromShape || !toShape) return;

            const from = this.getConnectionPoint(fromShape, 'bottom');
            const to = this.getConnectionPoint(toShape, 'top');

            // Calculate adjusted endpoint - stop arrow 15px before shape edge
            const arrowOffset = 15;
            const dx = to.x - from.x;
            const dy = to.y - from.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            const adjustedToX = to.x - (dx / distance) * arrowOffset;
            const adjustedToY = to.y - (dy / distance) * arrowOffset;

            const line = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            const midY = (from.y + adjustedToY) / 2;

            line.setAttribute('d', `
                M ${from.x} ${from.y}
                C ${from.x} ${midY}, ${adjustedToX} ${midY}, ${adjustedToX} ${adjustedToY}
            `);
            line.setAttribute('stroke', '#58a6ff');
            line.setAttribute('stroke-width', '2');
            line.setAttribute('fill', 'none');
            line.setAttribute('marker-end', 'url(#arrowhead)');
            line.classList.add('connection-line');

            svg.appendChild(line);
        });

        canvas.insertBefore(svg, canvas.firstChild);
    }

    selectColor(color) {
        this.currentColor = color;

        // Update swatch UI - remove selected from all, add to clicked
        document.querySelectorAll('.color-swatch').forEach(swatch => {
            swatch.classList.toggle('selected', swatch.dataset.color === color);
        });

        // Update selected shape if any
        if (this.selectedShape) {
            const shape = this.shapes.find(s => s.id === this.selectedShape);
            if (shape) {
                shape.color = color;
                document.getElementById(shape.id).style.borderColor = color;
            }
        }
    }

    clearCanvas() {
        if (!confirm('Are you sure you want to clear the canvas? This cannot be undone.')) {
            return;
        }

        this.shapes = [];
        this.connections = [];
        this.selectedShape = null;

        const canvas = document.getElementById('automation-canvas-wrapper');
        canvas.innerHTML = '';

        this.automationId = null;
        this.automationTitle = 'Untitled Automation';
    }

    exportToJSON() {
        const automation = {
            automation_id: this.automationId || `auto_${Date.now()}`,
            title: this.automationTitle,
            created_at: new Date().toISOString(),
            shapes: this.shapes.map(s => ({
                id: s.id,
                type: s.type,
                position: { x: s.x, y: s.y },
                size: { width: s.width, height: s.height },
                text: s.text,
                color: s.color
            })),
            connections: this.connections.map(c => ({
                id: c.id,
                from: c.from,
                to: c.to
            }))
        };

        // Download JSON
        const blob = new Blob([JSON.stringify(automation, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `automation_${automation.automation_id}.json`;
        a.click();
        URL.revokeObjectURL(url);

        console.log('Automation exported:', automation);
    }

    importFromJSON(json) {
        try {
            const automation = typeof json === 'string' ? JSON.parse(json) : json;

            this.clearCanvas();
            this.automationId = automation.automation_id;
            this.automationTitle = automation.title || 'Untitled Automation';

            // Recreate shapes
            automation.shapes.forEach(s => {
                this.createShape(
                    s.type,
                    s.position.x,
                    s.position.y,
                    s.text,
                    s.color,
                    s.id
                );

                // Update size
                const shape = this.shapes.find(sh => sh.id === s.id);
                if (shape) {
                    shape.width = s.size.width;
                    shape.height = s.size.height;
                    const shapeEl = document.getElementById(s.id);
                    shapeEl.style.width = `${s.size.width}px`;
                    shapeEl.style.height = `${s.size.height}px`;
                }
            });

            // Recreate connections
            automation.connections.forEach(c => {
                this.connections.push(c);
            });

            this.renderConnections();

            console.log('Automation imported:', automation);
        } catch (error) {
            console.error('Failed to import automation:', error);
            alert('Failed to import automation. Please check the JSON format.');
        }
    }

    async saveAutomation() {
        const title = prompt('Enter automation title:', this.automationTitle);
        if (!title) return;

        this.automationTitle = title;

        const automation = {
            automation_id: this.automationId || `auto_${Date.now()}`,
            title: this.automationTitle,
            visual_flow_json: JSON.stringify({
                shapes: this.shapes,
                connections: this.connections
            }),
            created_at: new Date().toISOString()
        };

        try {
            // TODO: Save to backend via API
            console.log('Saving automation:', automation);

            // For now, save to localStorage
            const saved = JSON.parse(localStorage.getItem('automations') || '[]');
            const existing = saved.findIndex(a => a.automation_id === automation.automation_id);

            if (existing >= 0) {
                saved[existing] = automation;
            } else {
                saved.push(automation);
            }

            localStorage.setItem('automations', JSON.stringify(saved));
            this.automationId = automation.automation_id;

            alert(`Automation "${title}" saved successfully!`);
            this.loadSavedAutomations();
        } catch (error) {
            console.error('Failed to save automation:', error);
            alert('Failed to save automation. Please try again.');
        }
    }

    loadSavedAutomations() {
        const saved = JSON.parse(localStorage.getItem('automations') || '[]');
        const list = document.getElementById('automation-list');

        if (!list) return;

        if (saved.length === 0) {
            list.innerHTML = `
                <div style="text-align: center; padding: var(--space-4); color: var(--text-muted);">
                    <i class="fas fa-inbox" style="font-size: 32px; opacity: 0.3; margin-bottom: var(--space-2);"></i>
                    <p style="font-size: 13px;">No saved automations yet</p>
                </div>
            `;
            return;
        }

        list.innerHTML = saved.map(auto => `
            <div class="automation-list-item" onclick="automationCanvas.loadAutomation('${auto.automation_id}')">
                <div class="automation-list-item-header">
                    <span class="automation-list-item-title">${auto.title}</span>
                    <span class="automation-list-item-badge">SAVED</span>
                </div>
                <div class="automation-list-item-meta">
                    <i class="fas fa-calendar"></i>
                    <span>${new Date(auto.created_at).toLocaleDateString()}</span>
                </div>
            </div>
        `).join('');
    }

    loadAutomation(automationId) {
        const saved = JSON.parse(localStorage.getItem('automations') || '[]');
        const automation = saved.find(a => a.automation_id === automationId);

        if (!automation) {
            alert('Automation not found');
            return;
        }

        const visualFlow = JSON.parse(automation.visual_flow_json);
        this.importFromJSON({
            automation_id: automation.automation_id,
            title: automation.title,
            shapes: visualFlow.shapes,
            connections: visualFlow.connections
        });
    }

    sendToAI() {
        const automation = {
            automation_id: this.automationId || `auto_${Date.now()}`,
            title: this.automationTitle,
            shapes: this.shapes,
            connections: this.connections
        };

        // Create automation slug
        const slug = {
            type: 'automation_slug',
            data: automation
        };

        // Insert into AI chat input
        const chatInput = document.getElementById('user-input');
        if (chatInput) {
            const slugText = `[AUTOMATION: ${automation.title} (${automation.automation_id})]`;
            chatInput.value = (chatInput.value + ' ' + slugText).trim();
            chatInput.focus();

            // Store slug data for AI
            window.currentAutomationSlug = slug;

            alert(`Automation "${automation.title}" added to AI chat!\n\nClick Send to have the AI analyze and refine your workflow.`);
        }
    }

    handleCanvasClick(e) {
        if (e.target.id === 'automation-canvas-wrapper') {
            this.selectShape(null);
        }
    }

    showColorPicker(shapeId) {
        // TODO: Implement color picker modal
        console.log('Show color picker for', shapeId);
    }

    showShapePicker(shapeId) {
        // TODO: Implement shape picker modal
        console.log('Show shape picker for', shapeId);
    }

    // ==================== WORKFLOW MANAGEMENT METHODS ====================

    async loadWorkflows() {
        try {
            const response = await fetch('/api/automation/list', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                }
            });

            if (!response.ok) throw new Error('Failed to load workflows');

            const data = await response.json();
            this.workflows = data.workflows || [];
            this.renderWorkflowList();
        } catch (error) {
            console.error('Error loading workflows:', error);
            // Show empty state if no workflows or error
            this.workflows = [];
            this.renderWorkflowList();
        }
    }

    renderWorkflowList() {
        const listContainer = document.getElementById('workflow-list');
        const emptyState = document.getElementById('workflow-list-empty');

        if (!listContainer) return;

        if (this.workflows.length === 0) {
            if (emptyState) emptyState.style.display = 'block';
            return;
        }

        if (emptyState) emptyState.style.display = 'none';

        // Clear existing items except empty state
        const items = listContainer.querySelectorAll('.workflow-item');
        items.forEach(item => item.remove());

        this.workflows.forEach(workflow => {
            const item = this.createWorkflowListItem(workflow);
            listContainer.appendChild(item);
        });
    }

    createWorkflowListItem(workflow) {
        const item = document.createElement('div');
        item.className = 'workflow-item';
        if (this.currentWorkflow && this.currentWorkflow.slug === workflow.slug) {
            item.classList.add('selected');
        }

        // Status badge
        const statusClass = workflow.status || 'draft';
        const statusIcon = statusClass === 'active' ? 'fa-circle' : statusClass === 'inactive' ? 'fa-circle-pause' : 'fa-circle-dot';

        // Format updated date
        const updatedDate = workflow.updated_at ? new Date(workflow.updated_at).toLocaleDateString() : 'Never';

        item.innerHTML = `
            <div class=\"workflow-header\">
                <div class=\"workflow-icon\">
                    <i class=\"fas fa-project-diagram\"></i>
                </div>
                <div class=\"workflow-details\">
                    <div class=\"workflow-title\">${workflow.title || 'Untitled Workflow'}</div>
                    <div class=\"workflow-description\">${workflow.description || 'No description'}</div>
                </div>
            </div>
            <div class=\"workflow-slug-pill\" draggable=\"true\" data-slug=\"${workflow.slug}\" data-workflow-id=\"${workflow.id || ''}\" title=\"Drag to AI chat to activate Workflow Designer mode\">
                <i class=\"fas fa-hashtag\"></i>${workflow.slug}
            </div>
            <div class=\"workflow-meta\">
                <span class=\"workflow-status-badge ${statusClass}\">
                    <i class=\"fas ${statusIcon}\"></i>
                    ${statusClass}
                </span>
                <span class=\"workflow-updated\">${updatedDate}</span>
            </div>
            <div class=\"workflow-actions\">
                <button class=\"workflow-action-btn\" data-action=\"load\" data-workflow-id=\"${workflow.id || workflow.slug}\" title=\"Load workflow\">
                    <i class=\"fas fa-folder-open\"></i> Load
                </button>
                <button class=\"workflow-action-btn\" data-action=\"duplicate\" data-workflow-id=\"${workflow.id || workflow.slug}\" title=\"Duplicate\">
                    <i class=\"fas fa-copy\"></i> Duplicate
                </button>
                <button class=\"workflow-action-btn danger\" data-action=\"delete\" data-workflow-id=\"${workflow.id || workflow.slug}\" title=\"Delete\">
                    <i class=\"fas fa-trash\"></i> Delete
                </button>
            </div>
        `;

        // Add event listeners
        const slugPill = item.querySelector('.workflow-slug-pill');
        slugPill.addEventListener('dragstart', (e) => this.handleSlugDragStart(e));

        const loadBtn = item.querySelector('[data-action=\"load\"]');
        loadBtn?.addEventListener('click', () => this.loadWorkflow(workflow.id || workflow.slug));

        const duplicateBtn = item.querySelector('[data-action=\"duplicate\"]');
        duplicateBtn?.addEventListener('click', () => this.duplicateWorkflow(workflow.id || workflow.slug));

        const deleteBtn = item.querySelector('[data-action=\"delete\"]');
        deleteBtn?.addEventListener('click', () => this.deleteWorkflow(workflow.id || workflow.slug));

        return item;
    }

    handleSlugDragStart(e) {
        const slug = e.target.dataset.slug;
        const workflowId = e.target.dataset.workflowId;

        // Set drag data
        e.dataTransfer.setData('text/plain', `[${slug}]`);
        e.dataTransfer.setData('workflow-slug', slug);
        e.dataTransfer.setData('workflow-id', workflowId);
        e.dataTransfer.effectAllowed = 'copy';

        console.log('Dragging workflow slug:', slug);
    }

    async createNewWorkflow() {
        // Generate slug from timestamp
        const timestamp = Date.now();
        const slug = `workflow-${timestamp}`;

        // Create new workflow object
        const newWorkflow = {
            slug: slug,
            title: 'New Workflow',
            description: 'Describe your automation workflow',
            status: 'draft',
            ui_json: {
                shapes: [],
                connections: []
            },
            execution_json: {
                steps: []
            }
        };

        // Clear canvas
        this.clearCanvas();

        // Set as current workflow
        this.currentWorkflow = newWorkflow;
        this.workflowSlug = slug;
        this.workflowTitle = 'New Workflow';
        this.workflowDescription = 'Describe your automation workflow';
        this.workflowStatus = 'draft';

        console.log('Created new workflow:', slug);

        // Add to workflows list temporarily (will be saved when user saves)
        this.workflows.unshift(newWorkflow);
        this.renderWorkflowList();
    }

    async loadWorkflow(workflowId) {
        try {
            const response = await fetch(`/api/automation/${workflowId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                }
            });

            if (!response.ok) throw new Error('Failed to load workflow');

            const data = await response.json();
            const workflow = data.workflow;

            // Set as current workflow
            this.currentWorkflow = workflow;
            this.workflowSlug = workflow.slug;
            this.workflowTitle = workflow.title;
            this.workflowDescription = workflow.description;
            this.workflowStatus = workflow.status;

            // Load UI JSON to canvas
            if (workflow.ui_json) {
                this.importFromJSON(workflow.ui_json);
            }

            console.log('Loaded workflow:', workflow.slug);
            this.renderWorkflowList();
        } catch (error) {
            console.error('Error loading workflow:', error);
            alert('Failed to load workflow. Please try again.');
        }
    }

    async saveWorkflow() {
        if (!this.currentWorkflow) {
            alert('Please create a new workflow first');
            return;
        }

        // Export current canvas state
        const ui_json = {
            shapes: this.shapes,
            connections: this.connections
        };

        // Prepare workflow data
        const workflowData = {
            slug: this.workflowSlug,
            title: this.workflowTitle,
            description: this.workflowDescription,
            status: this.workflowStatus,
            ui_json: ui_json,
            execution_json: this.currentWorkflow.execution_json || { steps: [] }
        };

        try {
            const response = await fetch('/api/automation/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                },
                body: JSON.stringify(workflowData)
            });

            if (!response.ok) throw new Error('Failed to save workflow');

            const data = await response.json();
            console.log('Workflow saved:', data);
            alert('Workflow saved successfully!');

            // Reload workflows list
            await this.loadWorkflows();
        } catch (error) {
            console.error('Error saving workflow:', error);
            alert('Failed to save workflow. Please try again.');
        }
    }

    async duplicateWorkflow(workflowId) {
        if (!confirm('Create a copy of this workflow?')) return;

        try {
            const response = await fetch(`/api/automation/${workflowId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                }
            });

            if (!response.ok) throw new Error('Failed to load workflow');

            const data = await response.json();
            const original = data.workflow;

            // Create duplicate with new slug
            const timestamp = Date.now();
            const newSlug = `${original.slug}-copy-${timestamp}`;

            const duplicate = {
                slug: newSlug,
                title: `${original.title} (Copy)`,
                description: original.description,
                status: 'draft',
                ui_json: original.ui_json,
                execution_json: original.execution_json
            };

            // Save duplicate
            const saveResponse = await fetch('/api/automation/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                },
                body: JSON.stringify(duplicate)
            });

            if (!saveResponse.ok) throw new Error('Failed to save duplicate');

            console.log('Workflow duplicated:', newSlug);
            alert('Workflow duplicated successfully!');

            // Reload workflows list
            await this.loadWorkflows();
        } catch (error) {
            console.error('Error duplicating workflow:', error);
            alert('Failed to duplicate workflow. Please try again.');
        }
    }

    getShapeTypeLabel(type) {
        const labels = {
            'rectangle': 'ACTION',
            'rounded': 'PROMPT',
            'hexagon': 'DECISION',
            'circle': 'TRIGGER',
            'diamond': 'CONDITION'
        };
        return labels[type] || 'SHAPE';
    }

    async deleteWorkflow(workflowId) {
        if (!confirm('Are you sure you want to delete this workflow? This cannot be undone.')) return;

        try {
            const response = await fetch(`/api/automation/${workflowId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                }
            });

            if (!response.ok) throw new Error('Failed to delete workflow');

            console.log('Workflow deleted:', workflowId);
            alert('Workflow deleted successfully!');

            // Clear canvas if this was the current workflow
            if (this.currentWorkflow && (this.currentWorkflow.id === workflowId || this.currentWorkflow.slug === workflowId)) {
                this.clearCanvas();
                this.currentWorkflow = null;
            }

            // Reload workflows list
            await this.loadWorkflows();
        } catch (error) {
            console.error('Error deleting workflow:', error);
            alert('Failed to delete workflow. Please try again.');
        }
    }

    // ==================== ZOOM METHODS ====================

    zoomIn() {
        this.currentZoom = Math.min(this.currentZoom + 0.1, 2.0); // Max 200%
        this.applyZoom();
    }

    zoomOut() {
        this.currentZoom = Math.max(this.currentZoom - 0.1, 0.5); // Min 50%
        this.applyZoom();
    }

    zoomReset() {
        this.currentZoom = 1.0;
        this.applyZoom();
    }

    applyZoom() {
        const wrapper = document.getElementById('automation-canvas-wrapper');
        if (wrapper) {
            wrapper.style.transform = `scale(${this.currentZoom})`;
            wrapper.style.transformOrigin = 'top left';
        }
        this.updateZoomDisplay();
    }

    updateZoomDisplay() {
        const zoomLevel = document.getElementById('zoom-level');
        if (zoomLevel) {
            zoomLevel.textContent = `${Math.round(this.currentZoom * 100)}%`;
        }
    }

    // ==================== SEND TO AI (Enhanced) ====================

    sendToAI() {
        if (!this.currentWorkflow) {
            alert('Please create or load a workflow first');
            return;
        }

        // Export current canvas state
        const workflowData = this.exportToJSON();

        // Store in global variable for agent access
        window.currentAutomationSlug = this.workflowSlug;

        // Get the active agent (look for visible agent column or use agent 1)
        let targetAgentId = 1; // Default to Prime agent
        const agentColumns = document.querySelectorAll('.agent-column');
        agentColumns.forEach((col, index) => {
            if (col.style.display !== 'none') {
                // Get agent ID from column
                const inputId = col.querySelector('textarea')?.id;
                if (inputId) {
                    const match = inputId.match(/input-(\d+)/);
                    if (match) {
                        targetAgentId = parseInt(match[1]);
                    }
                }
            }
        });

        // Add workflow slug to AI thread info area
        this.addWorkflowSlugToThreadInfo(targetAgentId);

        // Add user message with workflow slug
        if (typeof addAgentMessage === 'function') {
            const message = `<div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(210, 153, 34, 0.15); border: 1px solid #d29922; border-radius: 12px; padding: 6px 12px;">
                <i class="fas fa-project-diagram" style="color: #d29922;"></i>
                <span style="color: #d29922; font-weight: 600; font-size: 13px;">Workflow: ${this.workflowSlug}</span>
            </div>`;
            addAgentMessage(targetAgentId, 'user', message);
        }

        console.log(`Workflow [${this.workflowSlug}] sent to Agent ${targetAgentId}`);
        alert(`Workflow sent to AI Agent ${targetAgentId}!\n\nThe AI Workflow Designer mode is now active.`);
    }

    addWorkflowSlugToThreadInfo(agentId) {
        // Find the thread info area for this agent
        const threadInfoSelector = agentId === 1
            ? '.ai-chat-thread-info'
            : `#agent-${agentId} .agent-thread-info`;

        const threadInfo = document.querySelector(threadInfoSelector);
        if (!threadInfo) {
            console.warn('Thread info area not found for agent', agentId);
            return;
        }

        // Remove existing workflow pill if present
        const existingPill = threadInfo.querySelector('.workflow-info-pill');
        if (existingPill) {
            existingPill.remove();
        }

        // Create workflow pill
        const pill = document.createElement('div');
        pill.className = 'workflow-info-pill';
        pill.innerHTML = `
            <i class="fas fa-project-diagram"></i>
            <span>Workflow: ${this.workflowSlug}</span>
        `;
        pill.style.cssText = `
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(210, 153, 34, 0.15);
            border: 1px solid #d29922;
            border-radius: 12px;
            padding: 6px 12px;
            margin: 8px 0;
            color: #d29922;
            font-size: 12px;
            font-weight: 600;
        `;

        // Insert at the top of thread info
        threadInfo.insertBefore(pill, threadInfo.firstChild);

        console.log(`Workflow pill added to agent ${agentId} thread info`);
    }

    // ==================== NEW INTERACTION METHODS ====================

    recenterToShapes() {
        if (this.shapes.length === 0) {
            console.log('No shapes to center on');
            return;
        }

        // Calculate bounding box of all shapes
        let minX = Infinity, minY = Infinity;
        let maxX = -Infinity, maxY = -Infinity;

        this.shapes.forEach(shape => {
            minX = Math.min(minX, shape.x);
            minY = Math.min(minY, shape.y);
            maxX = Math.max(maxX, shape.x + shape.width);
            maxY = Math.max(maxY, shape.y + shape.height);
        });

        // Calculate center point
        const centerX = (minX + maxX) / 2;
        const centerY = (minY + maxY) / 2;

        // Scroll canvas to center
        const canvas = document.getElementById('automation-canvas');
        const canvasRect = canvas.getBoundingClientRect();

        canvas.scrollLeft = centerX - (canvasRect.width / 2);
        canvas.scrollTop = centerY - (canvasRect.height / 2);

        console.log('Recentered to shapes');
    }

    handleCanvasMouseDown(e) {
        if (e.target.id === 'automation-canvas' || e.target.id === 'automation-canvas-wrapper') {
            // Start drag selection with left click
            if (e.button === 0 && !e.ctrlKey) {
                this.isSelecting = true;
                const rect = e.currentTarget.getBoundingClientRect();
                const scrollLeft = e.currentTarget.scrollLeft || 0;
                const scrollTop = e.currentTarget.scrollTop || 0;

                this.selectionStart = {
                    x: e.clientX - rect.left + scrollLeft,
                    y: e.clientY - rect.top + scrollTop
                };

                // Create selection rectangle
                this.selectionRect = document.createElement('div');
                this.selectionRect.className = 'selection-rect';
                this.selectionRect.style.left = `${this.selectionStart.x}px`;
                this.selectionRect.style.top = `${this.selectionStart.y}px`;
                document.getElementById('automation-canvas-wrapper').appendChild(this.selectionRect);

                e.currentTarget.classList.add('selecting');
            }
        }
    }

    handleCanvasMouseMove(e) {
        const canvas = e.currentTarget;

        // Handle drag selection
        if (this.isSelecting && this.selectionRect) {
            const rect = canvas.getBoundingClientRect();
            const scrollLeft = canvas.scrollLeft || 0;
            const scrollTop = canvas.scrollTop || 0;

            const currentX = e.clientX - rect.left + scrollLeft;
            const currentY = e.clientY - rect.top + scrollTop;

            const width = Math.abs(currentX - this.selectionStart.x);
            const height = Math.abs(currentY - this.selectionStart.y);
            const left = Math.min(currentX, this.selectionStart.x);
            const top = Math.min(currentY, this.selectionStart.y);

            this.selectionRect.style.width = `${width}px`;
            this.selectionRect.style.height = `${height}px`;
            this.selectionRect.style.left = `${left}px`;
            this.selectionRect.style.top = `${top}px`;

            // Highlight shapes within selection
            this.updateShapeSelection(left, top, width, height);
        }
    }

    handleCanvasMouseUp(e) {
        const canvas = e.currentTarget;

        if (this.isSelecting) {
            this.isSelecting = false;
            canvas.classList.remove('selecting');

            // Remove selection rectangle
            if (this.selectionRect) {
                this.selectionRect.remove();
                this.selectionRect = null;
            }
        }
    }

    updateShapeSelection(left, top, width, height) {
        this.selectedShapes = [];

        this.shapes.forEach(shape => {
            const shapeRight = shape.x + shape.width;
            const shapeBottom = shape.y + shape.height;
            const selectionRight = left + width;
            const selectionBottom = top + height;

            // Check if shape intersects with selection
            const intersects = !(
                shape.x > selectionRight ||
                shapeRight < left ||
                shape.y > selectionBottom ||
                shapeBottom < top
            );

            const shapeEl = document.getElementById(shape.id);
            if (intersects) {
                this.selectedShapes.push(shape.id);
                shapeEl?.classList.add('selected');
            } else {
                shapeEl?.classList.remove('selected');
            }
        });
    }

    copyShapes() {
        if (this.selectedShapes.length > 0) {
            // Copy multiple shapes
            this.clipboard = this.selectedShapes.map(id => {
                const shape = this.shapes.find(s => s.id === id);
                return shape ? JSON.parse(JSON.stringify(shape)) : null;
            }).filter(s => s !== null);
        } else if (this.selectedShape) {
            // Copy single shape
            const shape = this.shapes.find(s => s.id === this.selectedShape);
            if (shape) {
                this.clipboard = [JSON.parse(JSON.stringify(shape))];
            }
        }

        if (this.clipboard && this.clipboard.length > 0) {
            console.log(`Copied ${this.clipboard.length} shape(s) to clipboard`);
        }
    }

    pasteShapes() {
        if (!this.clipboard || this.clipboard.length === 0) return;

        // Clear selection
        this.selectedShapes = [];
        if (this.selectedShape) {
            document.getElementById(this.selectedShape)?.classList.remove('selected');
            this.selectedShape = null;
        }

        // Paste shapes with offset (to the side)
        const pasteOffset = 40;
        this.clipboard.forEach(shape => {
            const newShape = {
                ...shape,
                id: `shape_${this.nextShapeId++}`,
                x: shape.x + pasteOffset,
                y: shape.y + pasteOffset
            };

            this.shapes.push(newShape);
            this.renderShape(newShape);
            this.selectedShapes.push(newShape.id);
        });

        console.log(`Pasted ${this.clipboard.length} shape(s) with offset`);
    }

    // Modal Management
    openWorkflowModal(workflowId = null) {
        const overlay = document.getElementById('workflow-modal-overlay');
        const modalTitle = document.getElementById('modal-title-text');
        const titleInput = document.getElementById('workflow-title-input');
        const slugInput = document.getElementById('workflow-slug-input');
        const timestampInput = document.getElementById('workflow-timestamp-input');
        const categorySelect = document.getElementById('workflow-category-select');
        const descriptionInput = document.getElementById('workflow-description-input');

        if (workflowId) {
            // Edit existing workflow
            const workflow = this.workflows.find(w => w.id === workflowId);
            if (workflow) {
                modalTitle.textContent = 'Edit Workflow';
                titleInput.value = workflow.title || '';
                slugInput.value = workflow.slug || '';
                timestampInput.value = workflow.created_at || new Date().toISOString();
                categorySelect.value = workflow.category || '';
                descriptionInput.value = workflow.description || '';
                this.editingWorkflowId = workflowId;
            }
        } else {
            // New workflow
            modalTitle.textContent = 'New Workflow';
            titleInput.value = '';
            slugInput.value = '';
            timestampInput.value = new Date().toISOString();
            categorySelect.value = '';
            descriptionInput.value = '';
            this.editingWorkflowId = null;
        }

        overlay.style.display = 'flex';
        setTimeout(() => titleInput.focus(), 100);
    }

    closeWorkflowModal() {
        const overlay = document.getElementById('workflow-modal-overlay');
        overlay.style.display = 'none';
        this.editingWorkflowId = null;
    }

    saveWorkflowFromModal() {
        const titleInput = document.getElementById('workflow-title-input');
        const slugInput = document.getElementById('workflow-slug-input');
        const timestampInput = document.getElementById('workflow-timestamp-input');
        const categorySelect = document.getElementById('workflow-category-select');
        const descriptionInput = document.getElementById('workflow-description-input');

        const title = titleInput.value.trim();
        if (!title) {
            alert('Please enter a workflow title');
            titleInput.focus();
            return;
        }

        const workflowData = {
            title: title,
            slug: slugInput.value || `workflow_${this.generateSlug(title)}`,
            created_at: timestampInput.value || new Date().toISOString(),
            category: categorySelect.value || 'other',
            description: descriptionInput.value.trim(),
            ui_json: {
                shapes: this.shapes,
                connections: this.connections,
                zoom: this.currentZoom
            },
            execution_json: {},
            status: 'draft'
        };

        if (this.editingWorkflowId) {
            // Update existing
            const index = this.workflows.findIndex(w => w.id === this.editingWorkflowId);
            if (index !== -1) {
                workflowData.id = this.editingWorkflowId;
                this.workflows[index] = { ...this.workflows[index], ...workflowData };
            }
        } else {
            // Create new
            workflowData.id = `workflow_${Date.now()}`;
            this.workflows.push(workflowData);
        }

        this.saveWorkflow();
        this.loadWorkflows();
        this.closeWorkflowModal();
    }

    generateSlug(title) {
        return title
            .toLowerCase()
            .replace(/[^a-z0-9\s-]/g, '')
            .replace(/\s+/g, '_')
            .replace(/_+/g, '_')
            .substring(0, 50);
    }

    addNewCategory() {
        const categoryName = prompt('Enter new category name:');
        if (categoryName && categoryName.trim()) {
            const select = document.getElementById('workflow-category-select');
            const slug = this.generateSlug(categoryName);

            // Check if category already exists
            const exists = Array.from(select.options).some(opt => opt.value === slug);
            if (!exists) {
                const option = document.createElement('option');
                option.value = slug;
                option.textContent = categoryName.trim();
                select.insertBefore(option, select.lastElementChild); // Insert before "Other"
                select.value = slug;
            } else {
                alert('Category already exists');
            }
        }
    }

    showLoadWorkflowDialog() {
        // With floating palette, workflows are managed through API
        // For now, show simple message - can be enhanced to show modal with workflow list
        alert('Load Workflow:\n\nSaved workflows can be accessed through the API.\nUse the "New" button to create a new workflow or check the backend /api/automation/list endpoint for saved workflows.');

        // TODO: Future enhancement - show modal with workflow list from /api/automation/list
        // this.openWorkflowModal('load');
    }
}

// Initialize when DOM is ready
let automationCanvas;

document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if automation dashboard exists
    if (document.getElementById('automation-canvas-wrapper')) {
        automationCanvas = new AutomationCanvas();
        console.log('Automation Canvas initialized');
    }
});

// Export for global access
window.automationCanvas = automationCanvas;
