/**
 * AUTOMATION CANVAS EXTENSIONS
 * Additional methods for AutomationCanvas class
 * Pan, drag-select, copy/paste, resize, recenter, minimap
 */

// Add these methods to the AutomationCanvas class

// ==================== CANVAS INTERACTION ====================

function handleCanvasMouseDown(e) {
    if (e.target.id === 'automation-canvas' || e.target.id === 'automation-canvas-wrapper') {
        // Start panning with middle mouse or space+click
        if (e.button === 1 || (e.button === 0 && e.spaceKey)) {
            this.isPanning = true;
            this.panStart = { x: e.clientX - e.currentTarget.scrollLeft, y: e.clientY - e.currentTarget.scrollTop };
            e.currentTarget.classList.add('grabbing');
            e.preventDefault();
        }
        // Start drag selection with left click
        else if (e.button === 0 && !e.ctrlKey) {
            this.isSelecting = true;
            const rect = e.currentTarget.getBoundingClientRect();
            this.selectionStart = {
                x: e.clientX - rect.left + e.currentTarget.scrollLeft,
                y: e.clientY - rect.top + e.currentTarget.scrollTop
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

function handleCanvasMouseMove(e) {
    const canvas = e.currentTarget;

    // Handle panning
    if (this.isPanning) {
        const x = e.clientX - this.panStart.x;
        const y = e.clientY - this.panStart.y;
        canvas.scrollLeft = -x;
        canvas.scrollTop = -y;
        e.preventDefault();
    }

    // Handle drag selection
    if (this.isSelecting && this.selectionRect) {
        const rect = canvas.getBoundingClientRect();
        const currentX = e.clientX - rect.left + canvas.scrollLeft;
        const currentY = e.clientY - rect.top + canvas.scrollTop;

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

function handleCanvasMouseUp(e) {
    const canvas = e.currentTarget;

    if (this.isPanning) {
        this.isPanning = false;
        canvas.classList.remove('grabbing');
    }

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

function updateShapeSelection(left, top, width, height) {
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

// ==================== COPY/PASTE ====================

function copyShapes() {
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

function pasteShapes() {
    if (!this.clipboard || this.clipboard.length === 0) return;

    // Clear selection
    this.selectedShapes = [];
    if (this.selectedShape) {
        document.getElementById(this.selectedShape)?.classList.remove('selected');
        this.selectedShape = null;
    }

    // Paste shapes with offset
    const pasteOffset = 30;
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

    console.log(`Pasted ${this.clipboard.length} shape(s)`);

    // Hide empty state
    const emptyState = document.getElementById('automation-empty-state');
    if (emptyState) emptyState.style.display = 'none';
}

// ==================== RESIZE ====================

function addResizeHandles(shapeEl, shape) {
    const positions = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'];

    positions.forEach(pos => {
        const handle = document.createElement('div');
        handle.className = `resize-handle ${pos}`;
        handle.dataset.position = pos;

        handle.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            this.startResize(e, shape, pos);
        });

        shapeEl.appendChild(handle);
    });
}

function startResize(e, shape, position) {
    this.isResizing = true;
    this.resizeHandle = position;
    this.resizeStart = {
        x: e.clientX,
        y: e.clientY,
        width: shape.width,
        height: shape.height,
        shapeX: shape.x,
        shapeY: shape.y
    };
    this.resizingShape = shape;

    document.addEventListener('mousemove', this.handleResize.bind(this));
    document.addEventListener('mouseup', this.endResize.bind(this));

    e.preventDefault();
}

function handleResize(e) {
    if (!this.isResizing || !this.resizingShape) return;

    const deltaX = e.clientX - this.resizeStart.x;
    const deltaY = e.clientY - this.resizeStart.y;
    const shape = this.resizingShape;
    const shapeEl = document.getElementById(shape.id);

    // Calculate new dimensions based on handle position
    switch (this.resizeHandle) {
        case 'e': // East
            shape.width = Math.max(100, this.resizeStart.width + deltaX);
            break;
        case 'w': // West
            shape.width = Math.max(100, this.resizeStart.width - deltaX);
            shape.x = this.resizeStart.shapeX + deltaX;
            break;
        case 's': // South
            shape.height = Math.max(60, this.resizeStart.height + deltaY);
            break;
        case 'n': // North
            shape.height = Math.max(60, this.resizeStart.height - deltaY);
            shape.y = this.resizeStart.shapeY + deltaY;
            break;
        case 'se': // Southeast
            shape.width = Math.max(100, this.resizeStart.width + deltaX);
            shape.height = Math.max(60, this.resizeStart.height + deltaY);
            break;
        case 'sw': // Southwest
            shape.width = Math.max(100, this.resizeStart.width - deltaX);
            shape.height = Math.max(60, this.resizeStart.height + deltaY);
            shape.x = this.resizeStart.shapeX + deltaX;
            break;
        case 'ne': // Northeast
            shape.width = Math.max(100, this.resizeStart.width + deltaX);
            shape.height = Math.max(60, this.resizeStart.height - deltaY);
            shape.y = this.resizeStart.shapeY + deltaY;
            break;
        case 'nw': // Northwest
            shape.width = Math.max(100, this.resizeStart.width - deltaX);
            shape.height = Math.max(60, this.resizeStart.height - deltaY);
            shape.x = this.resizeStart.shapeX + deltaX;
            shape.y = this.resizeStart.shapeY + deltaY;
            break;
    }

    // Update shape element
    shapeEl.style.width = `${shape.width}px`;
    shapeEl.style.height = `${shape.height}px`;
    shapeEl.style.left = `${shape.x}px`;
    shapeEl.style.top = `${shape.y}px`;

    // Update connections
    this.renderConnections();
}

function endResize() {
    this.isResizing = false;
    this.resizeHandle = null;
    this.resizingShape = null;

    document.removeEventListener('mousemove', this.handleResize);
    document.removeEventListener('mouseup', this.endResize);
}

// ==================== RECENTER ====================

function recenterToShapes() {
    if (this.shapes.length === 0) return;

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

// ==================== MINIMAP ====================

function updateMinimap() {
    const minimapContent = document.getElementById('minimap-content');
    if (!minimapContent) return;

    // Clear existing minimap shapes
    const existing = minimapContent.querySelectorAll('.minimap-shape');
    existing.forEach(el => el.remove());

    // Calculate scale factor
    const canvas = document.getElementById('automation-canvas');
    const canvasWrapper = document.getElementById('automation-canvas-wrapper');
    const scale = 200 / canvasWrapper.offsetWidth; // Minimap is 200px wide

    // Render shapes on minimap
    this.shapes.forEach(shape => {
        const minimapShape = document.createElement('div');
        minimapShape.className = 'minimap-shape';
        minimapShape.style.left = `${shape.x * scale}px`;
        minimapShape.style.top = `${shape.y * scale}px`;
        minimapShape.style.width = `${shape.width * scale}px`;
        minimapShape.style.height = `${shape.height * scale}px`;
        minimapShape.style.background = shape.color || this.currentColor;
        minimapContent.appendChild(minimapShape);
    });

    // Update viewport indicator
    const viewport = document.getElementById('minimap-viewport');
    if (viewport) {
        const viewportWidth = canvas.offsetWidth * scale;
        const viewportHeight = canvas.offsetHeight * scale;
        const scrollLeft = canvas.scrollLeft * scale;
        const scrollTop = canvas.scrollTop * scale;

        viewport.style.left = `${scrollLeft}px`;
        viewport.style.top = `${scrollTop}px`;
        viewport.style.width = `${viewportWidth}px`;
        viewport.style.height = `${viewportHeight}px`;
    }
}

// Call updateMinimap after shape operations
// this.updateMinimap();
