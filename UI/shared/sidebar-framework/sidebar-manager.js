/**
 * Universal Sidebar Manager
 * 
 * PURPOSE: Centralized framework for managing module sidebars with consistent behavior
 * - Automatic registration of module sidebars
 * - Consistent toggle behavior (left/right based on button position)
 * - Draggable toggle buttons with repositioning
 * - Z-index management to prevent conflicts
 * - State persistence (remember which sidebars are open)
 * 
 * USAGE:
 * // Register a sidebar
 * SidebarManager.register({
 *     id: 'synergy-sidebar',
 *     side: 'left',
 *     toggleButtonId: 'synergy-sidebar-toggle',
 *     width: '450px',
 *     icon: 'fa-hexagon-nodes-bolt',
 *     title: 'Synergy Sessions',
 *     onOpen: () => { ... },
 *     onClose: () => { ... }
 * });
 * 
 * EXPORTS:
 * - window.SidebarManager (singleton)
 * 
 * DEPENDENCIES:
 * - sidebar-manager.css (styling)
 * 
 * LAST MODIFIED: 2025-11-28
 */

class UniversalSidebarManager {
    constructor() {
        this.sidebars = new Map();
        this.activeSidebars = new Set();
        this.toggleButtons = new Map();
        this.baseZIndex = 9000;
        this.initialized = false;

        console.log('[SIDEBAR MANAGER] Initialized');
    }

    /**
     * Initialize the sidebar manager
     */
    init() {
        if (this.initialized) return;

        // Load saved state from localStorage
        this.loadState();

        // Initialize drag-and-drop for toggle buttons
        this.initDragAndDrop();

        this.initialized = true;
        console.log('[SIDEBAR MANAGER] Ready');
    }

    /**
     * Register a new sidebar
     * 
     * @param {Object} config - Sidebar configuration
     * @param {string} config.id - Sidebar element ID
     * @param {string} config.side - 'left' or 'right'
     * @param {string} config.toggleButtonId - Toggle button element ID
     * @param {string} config.width - Sidebar width (e.g., '450px')
     * @param {string} config.icon - Font Awesome icon class
     * @param {string} config.title - Sidebar title
     * @param {Function} config.onOpen - Callback when sidebar opens
     * @param {Function} config.onClose - Callback when sidebar closes
     * @param {Function} config.onInit - Callback when sidebar first opens (lazy load)
     * @param {number} config.zIndex - Optional custom z-index
     * @param {boolean} config.allowMultiple - Allow multiple sidebars open at once
     */
    register(config) {
        const {
            id,
            side,
            toggleButtonId,
            width = '450px',
            icon = 'fa-bars',
            title = 'Sidebar',
            onOpen = null,
            onClose = null,
            onInit = null,
            zIndex = null,
            allowMultiple = false
        } = config;

        if (this.sidebars.has(id)) {
            console.warn(`[SIDEBAR MANAGER] Sidebar '${id}' already registered`);
            return;
        }

        // Calculate z-index
        const assignedZIndex = zIndex || (this.baseZIndex + this.sidebars.size * 100);

        const sidebarConfig = {
            id,
            side,
            toggleButtonId,
            width,
            icon,
            title,
            onOpen,
            onClose,
            onInit,
            zIndex: assignedZIndex,
            allowMultiple,
            isOpen: false,
            initialized: false,
            element: null,
            toggleButton: null
        };

        this.sidebars.set(id, sidebarConfig);

        // Initialize the sidebar if elements exist
        this.initializeSidebar(id);

        console.log(`[SIDEBAR MANAGER] Registered: ${id} (${side} side, z-index: ${assignedZIndex})`);
    }

    /**
     * Initialize a specific sidebar (setup elements and event listeners)
     */
    initializeSidebar(sidebarId) {
        const config = this.sidebars.get(sidebarId);
        if (!config) return;

        // Get elements
        const sidebar = document.getElementById(config.id);
        const toggleButton = document.getElementById(config.toggleButtonId);

        if (!sidebar) {
            // If DOM isn't ready yet, try again once DOMContentLoaded fires
            console.warn(`[SIDEBAR MANAGER] Sidebar element '${config.id}' not found - will retry on DOMContentLoaded`);
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    // Retry initialization once after DOM is available
                    try {
                        this.initializeSidebar(sidebarId);
                    } catch (e) {
                        console.error(`[SIDEBAR MANAGER] Retry initialize failed for ${sidebarId}:`, e);
                    }
                }, { once: true });
            }
            return;
        }

        if (!toggleButton) {
            console.warn(`[SIDEBAR MANAGER] Toggle button '${config.toggleButtonId}' not found - sidebar can still be controlled programmatically`);
            // Don't return - allow sidebar to be controlled via SidebarManager.open/close
        }

        config.element = sidebar;
        config.toggleButton = toggleButton;

        // Apply standard classes and styles
        this.applySidebarStyles(sidebar, config);

        // Setup toggle button click handler (if button exists)
        if (toggleButton) {
            toggleButton.onclick = () => this.toggle(sidebarId);
        }

        // Add data attribute for tracking
        sidebar.setAttribute('data-sidebar-id', sidebarId);
        sidebar.setAttribute('data-sidebar-side', config.side);

        if (toggleButton) {
            toggleButton.setAttribute('data-sidebar-id', sidebarId);
            toggleButton.setAttribute('data-side', config.side);

            // Make toggle button draggable
            this.makeButtonDraggable(toggleButton, config);
        }

        console.log(`[SIDEBAR MANAGER] Initialized: ${sidebarId}`);
    }

    /**
     * Apply standard styles to sidebar element
     */
    applySidebarStyles(sidebar, config) {
        // Base styles
        sidebar.style.position = 'fixed';
        sidebar.style.top = '60px';
        sidebar.style.height = 'calc(100vh - 60px)';
        sidebar.style.width = config.width;
        sidebar.style.zIndex = config.zIndex;
        sidebar.style.display = 'flex';
        sidebar.style.flexDirection = 'column';

        // Remove old side classes
        sidebar.classList.remove('sidebar-left', 'sidebar-right');

        // Clear ALL positioning properties to prevent conflicts
        sidebar.style.removeProperty('left');
        sidebar.style.removeProperty('right');
        sidebar.style.removeProperty('transform');
        sidebar.style.removeProperty('border-left');
        sidebar.style.removeProperty('border-right');

        // Side-specific positioning - Use transform-based animations for ALL sidebars
        if (config.side === 'left') {
            // LEFT SIDE: Anchor to left edge, transform pushes/pulls from there
            sidebar.style.left = '0';
            sidebar.style.right = 'auto';  // Explicitly clear right positioning
            sidebar.style.borderRight = '1px solid var(--border-default)';
            sidebar.style.boxShadow = '4px 0 24px rgba(0, 0, 0, 0.3)';
            sidebar.style.transform = 'translateX(-100%)';  // Start hidden off-screen LEFT
            sidebar.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease';
        } else {
            // RIGHT SIDE: Anchor to right edge, transform pushes/pulls from there
            sidebar.style.right = '0';
            sidebar.style.left = 'auto';  // Explicitly clear left positioning
            sidebar.style.borderLeft = '1px solid var(--border-default)';
            sidebar.style.boxShadow = '-4px 0 24px rgba(0, 0, 0, 0.3)';
            sidebar.style.transform = 'translateX(100%)';  // Start hidden off-screen RIGHT
            sidebar.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease';
        }

        // Add standard classes
        sidebar.classList.add('universal-sidebar');
        sidebar.classList.add(`sidebar-${config.side}`);

        if (!sidebar.classList.contains('collapsed')) {
            sidebar.classList.add('collapsed');
        }
    }

    /**
     * Make toggle button draggable for repositioning
     * Dynamically determines left/right side based on button position
     */
    makeButtonDraggable(button, config) {
        let isDragging = false;
        let startX, startY, startLeft, startTop;

        button.style.cursor = 'move';
        button.draggable = true;

        button.addEventListener('dragstart', (e) => {
            isDragging = true;
            const rect = button.getBoundingClientRect();
            startX = e.clientX;
            startY = e.clientY;
            startLeft = rect.left;
            startTop = rect.top;

            // Set drag image to a small transparent element
            const dragImage = document.createElement('div');
            dragImage.style.width = '1px';
            dragImage.style.height = '1px';
            e.dataTransfer.setDragImage(dragImage, 0, 0);
        });

        button.addEventListener('drag', (e) => {
            if (!isDragging || e.clientX === 0 && e.clientY === 0) return;

            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;

            const newLeft = startLeft + deltaX;
            const newTop = startTop + deltaY;

            button.style.left = newLeft + 'px';
            button.style.top = newTop + 'px';
            button.style.right = 'auto';  // Clear right positioning
        });

        button.addEventListener('dragend', (e) => {
            isDragging = false;

            // Determine which side based on button position
            const windowWidth = window.innerWidth;
            const buttonRect = button.getBoundingClientRect();
            const buttonCenterX = buttonRect.left + (buttonRect.width / 2);

            // If button is in left half of screen, use left side; otherwise right side
            const newSide = buttonCenterX < (windowWidth / 2) ? 'left' : 'right';

            // Update config and sidebar if side changed
            if (newSide !== config.side) {
                console.log(`[SIDEBAR MANAGER] Toggle moved to ${newSide} side for ${config.id}`);

                const wasOpen = config.isOpen;
                const oldSide = config.side;
                config.side = newSide;

                // Update button data attribute
                button.setAttribute('data-side', newSide);

                // Update sidebar element data attribute
                if (config.element) {
                    config.element.setAttribute('data-sidebar-side', newSide);
                }

                // Update sidebar positioning
                if (config.element) {
                    // If sidebar was open, close it from old side first
                    if (wasOpen) {
                        config.element.classList.remove('expanded');
                        config.element.classList.add('collapsed');
                        if (oldSide === 'right') {
                            config.element.style.transform = 'translateX(100%)';
                        } else {
                            config.element.style.transform = 'translateX(-100%)';
                        }
                        config.isOpen = false;
                    }

                    // Apply new side styles
                    this.applySidebarStyles(config.element, config);

                    // Re-open on new side if it was open
                    if (wasOpen) {
                        setTimeout(() => {
                            config.element.classList.remove('collapsed');
                            config.element.classList.add('expanded');
                            if (newSide === 'right') {
                                config.element.style.transform = 'translateX(-60px)';
                            } else {
                                config.element.style.transform = 'translateX(60px)';
                            }
                            config.isOpen = true;
                        }, 50);
                    }
                }
            }

            // Save button position and side
            this.saveButtonPosition(config.toggleButtonId, {
                left: button.style.left,
                top: button.style.top,
                side: newSide
            });

            console.log(`[SIDEBAR MANAGER] Button ${config.toggleButtonId} positioned at (${button.style.left}, ${button.style.top}) on ${newSide} side`);
        });

        // Restore saved position and side
        const savedPosition = this.getButtonPosition(config.toggleButtonId);
        if (savedPosition) {
            button.style.position = 'fixed';
            button.style.left = savedPosition.left;
            button.style.top = savedPosition.top;
            button.style.right = 'auto';

            // Update side if it was saved
            if (savedPosition.side && savedPosition.side !== config.side) {
                config.side = savedPosition.side;
                button.setAttribute('data-side', savedPosition.side);
                if (config.element) {
                    this.applySidebarStyles(config.element, config);
                }
            }
        }
    }

    /**
     * Toggle a sidebar open/closed
     */
    toggle(sidebarId) {
        const config = this.sidebars.get(sidebarId);
        if (!config) {
            console.error(`[SIDEBAR MANAGER] Sidebar '${sidebarId}' not found`);
            return;
        }

        if (!config.element) {
            console.error(`[SIDEBAR MANAGER] Sidebar '${sidebarId}' not initialized`);
            return;
        }

        const isOpen = config.isOpen;

        if (isOpen) {
            this.close(sidebarId);
        } else {
            this.open(sidebarId);
        }
    }

    /**
     * Open a sidebar
     */
    async open(sidebarId) {
        const config = this.sidebars.get(sidebarId);
        if (!config || !config.element) return;

        // Close other sidebars on the same side if not allowing multiple
        if (!config.allowMultiple) {
            this.activeSidebars.forEach(activeSidebarId => {
                const activeConfig = this.sidebars.get(activeSidebarId);
                if (activeConfig && activeConfig.side === config.side) {
                    this.close(activeSidebarId);
                }
            });
        }

        // First-time initialization
        if (!config.initialized && config.onInit) {
            console.log(`[SIDEBAR MANAGER] First open - initializing ${sidebarId}...`);
            await config.onInit();
            config.initialized = true;
        }

        // Open the sidebar using transform
        config.element.classList.remove('collapsed');
        config.element.classList.add('expanded');
        // Use transform-based open animation for both sides
        if (config.side === 'right') {
            // Slide in from right to -60px (past the static sidebar)
            config.element.style.transform = 'translateX(-60px)';
        } else {
            // Slide in from left to 60px (past the static sidebar)
            config.element.style.transform = 'translateX(60px)';
        }
        config.isOpen = true;
        this.activeSidebars.add(sidebarId);

        // Active state on button
        if (config.toggleButton) {
            config.toggleButton.classList.add('active');
        }

        // Callback
        if (config.onOpen) {
            config.onOpen();
        }

        // Save state
        this.saveState();

        console.log(`[SIDEBAR MANAGER] Opened: ${sidebarId}`);
    }

    /**
     * Close a sidebar
     */
    close(sidebarId) {
        const config = this.sidebars.get(sidebarId);
        if (!config || !config.element) return;

        // Slide sidebar off-screen using transform
        config.element.classList.remove('expanded');
        config.element.classList.add('collapsed');
        if (config.side === 'right') {
            // Slide off-screen to the right
            config.element.style.transform = 'translateX(100%)';
        } else {
            // Slide off-screen to the left
            config.element.style.transform = 'translateX(-100%)';
        }
        config.isOpen = false;
        this.activeSidebars.delete(sidebarId);

        // Remove active state from button
        if (config.toggleButton) {
            config.toggleButton.classList.remove('active');
        }

        // Callback
        if (config.onClose) {
            config.onClose();
        }

        // Save state
        this.saveState();

        console.log(`[SIDEBAR MANAGER] Closed: ${sidebarId}`);
    }

    /**
     * Check if a sidebar is open
     */
    isOpen(sidebarId) {
        const config = this.sidebars.get(sidebarId);
        return config ? config.isOpen : false;
    }

    /**
     * Get all registered sidebars
     */
    getAll() {
        return Array.from(this.sidebars.values());
    }

    /**
     * Get sidebars by side
     */
    getBySide(side) {
        return Array.from(this.sidebars.values()).filter(config => config.side === side);
    }

    /**
     * Save sidebar states to localStorage
     */
    saveState() {
        const state = {};
        this.sidebars.forEach((config, id) => {
            state[id] = {
                isOpen: config.isOpen,
                initialized: config.initialized
            };
        });
        localStorage.setItem('sidebarManagerState', JSON.stringify(state));
    }

    /**
     * Load sidebar states from localStorage
     */
    loadState() {
        try {
            const savedState = localStorage.getItem('sidebarManagerState');
            if (!savedState) return;

            const state = JSON.parse(savedState);
            Object.keys(state).forEach(id => {
                const config = this.sidebars.get(id);
                if (config) {
                    config.isOpen = state[id].isOpen || false;
                    // Restore the initialized flag so onInit runs once per
                    // browser (matching what saveState persists) instead of
                    // re-running on every page load. The HTML fetch in
                    // transcription's onInit is expensive enough that running
                    // it on every navigation was the user-visible regression.
                    config.initialized = state[id].initialized || false;
                }
            });

            console.log('[SIDEBAR MANAGER] State loaded from localStorage');
        } catch (error) {
            console.error('[SIDEBAR MANAGER] Failed to load state:', error);
        }
    }

    /**
     * Save toggle button position
     */
    saveButtonPosition(buttonId, position) {
        try {
            const positions = JSON.parse(localStorage.getItem('sidebarButtonPositions') || '{}');
            positions[buttonId] = position;
            localStorage.setItem('sidebarButtonPositions', JSON.stringify(positions));
        } catch (error) {
            console.error('[SIDEBAR MANAGER] Failed to save button position:', error);
        }
    }

    /**
     * Get toggle button position
     */
    getButtonPosition(buttonId) {
        try {
            const positions = JSON.parse(localStorage.getItem('sidebarButtonPositions') || '{}');
            return positions[buttonId] || null;
        } catch (error) {
            console.error('[SIDEBAR MANAGER] Failed to load button position:', error);
            return null;
        }
    }

    /**
     * Initialize drag-and-drop functionality
     */
    initDragAndDrop() {
        // This method can be extended for more complex drag-and-drop features
        console.log('[SIDEBAR MANAGER] Drag-and-drop initialized');
    }

    /**
     * Unregister a sidebar (cleanup)
     */
    unregister(sidebarId) {
        const config = this.sidebars.get(sidebarId);
        if (!config) return;

        if (config.isOpen) {
            this.close(sidebarId);
        }

        this.sidebars.delete(sidebarId);
        console.log(`[SIDEBAR MANAGER] Unregistered: ${sidebarId}`);
    }

    /**
     * Close all sidebars
     */
    closeAll() {
        this.activeSidebars.forEach(sidebarId => {
            this.close(sidebarId);
        });
    }
}

// Create singleton instance
window.SidebarManager = new UniversalSidebarManager();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.SidebarManager.init();
    });
} else {
    window.SidebarManager.init();
}

console.log('[SIDEBAR MANAGER] Module loaded');
