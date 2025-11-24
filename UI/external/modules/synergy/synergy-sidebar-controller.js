/**
 * Synergy Sidebar Controller
 * 
 * PURPOSE: Main controller class for Synergy sidebar
 * - Coordinates renderer, API calls, state management
 * - Handles expand/collapse, pin, filter, search
 * - 450px width sidebar matching Automations structure
 * 
 * DEPENDENCIES:
 * - synergy-sidebar-renderer.js (rendering)
 * - synergy-card-renderer.js (card rendering)
 * - synergy-milestone-renderer.js (milestone rendering)
 * - synergy-sidebar.css (styling)
 * 
 * EXPORTS:
 * - window.SynergySidebar (main singleton)
 * 
 * LAST MODIFIED: 2025-11-20
 */

class SynergySidebarController {
    constructor() {
        this.API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
        this.sessions = [];
        this.expandedSessions = new Set();
        this.pinnedSessions = new Set();
        this.currentView = 'list'; // 'list' or 'pinned'
        this.currentFilter = 'all'; // 'all', 'backlog', 'in_progress', 'review', 'done'
        this.searchQuery = '';

        // Renderer instance - check for V2 first, then fallback
        this.renderer = null;
        if (window.SynergySidebarRendererV2) {
            this.renderer = new window.SynergySidebarRendererV2();
            console.log('[SYNERGY SIDEBAR CONTROLLER] Using V2 renderer');
        } else if (window.SynergySidebarRenderer) {
            this.renderer = new window.SynergySidebarRenderer();
            console.log('[SYNERGY SIDEBAR CONTROLLER] Using legacy renderer');
        } else {
            console.error('[SYNERGY SIDEBAR CONTROLLER] No renderer available!');
        }

        console.log('[SYNERGY SIDEBAR CONTROLLER] Initialized');
    }

    /**
     * Initialize sidebar
     */
    async init() {
        console.log('[SYNERGY SIDEBAR] Initializing...');

        // Load sessions
        await this.loadSessions();

        // Render initial view
        this.render();

        console.log('[SYNERGY SIDEBAR] Initialization complete');
    }

    /**
     * Load sessions from API
     */
    async loadSessions() {
        try {
            console.log('[SYNERGY SIDEBAR] Loading sessions...');

            // Use /sessions/batch endpoint to get sessions with counts
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/sessions/batch`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.sessions = data.sessions || [];

            console.log(`[SYNERGY SIDEBAR] Loaded ${this.sessions.length} sessions`);

            return this.sessions;
        } catch (error) {
            console.error('[SYNERGY SIDEBAR] Failed to load sessions:', error);
            this.sessions = [];
            return [];
        }
    }

    /**
     * Render sidebar content
     */
    render() {
        if (!this.renderer) {
            console.error('[SYNERGY SIDEBAR] Renderer not available');
            return;
        }

        const listView = document.getElementById('synergy-list-view');
        const pinnedView = document.getElementById('synergy-pinned-view');

        if (!listView || !pinnedView) {
            console.error('[SYNERGY SIDEBAR] View containers not found');
            return;
        }

        // Filter sessions
        const filteredSessions = this.getFilteredSessions();

        // Render based on current view
        if (this.currentView === 'list') {
            listView.innerHTML = '';
            filteredSessions.forEach(session => {
                const item = this.renderer.createSessionItem(session, this.expandedSessions, this.pinnedSessions);
                listView.appendChild(item);
            });
        } else if (this.currentView === 'pinned') {
            pinnedView.innerHTML = '';
            const pinnedSessions = filteredSessions.filter(s => this.pinnedSessions.has(s.session_id));

            if (pinnedSessions.length === 0) {
                pinnedView.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--text-tertiary);">No pinned sessions</div>';
            } else {
                pinnedSessions.forEach(session => {
                    const item = this.renderer.createSessionItem(session, this.expandedSessions, this.pinnedSessions);
                    pinnedView.appendChild(item);
                });
            }
        }
    }

    /**
     * Get filtered sessions based on current filter and search
     */
    getFilteredSessions() {
        let filtered = [...this.sessions];

        // Apply category filter
        if (this.currentFilter !== 'all') {
            filtered = filtered.filter(s => s.kanban_column === this.currentFilter);
        }

        // Apply search filter
        if (this.searchQuery) {
            const query = this.searchQuery.toLowerCase();
            filtered = filtered.filter(s =>
                (s.title && s.title.toLowerCase().includes(query)) ||
                (s.description && s.description.toLowerCase().includes(query)) ||
                (s.session_id && s.session_id.toLowerCase().includes(query))
            );
        }

        return filtered;
    }

    /**
     * Toggle sidebar visibility
     */
    async toggleSidebar() {
        const sidebar = document.getElementById('synergy-sidebar');
        if (!sidebar) return;

        // Auto-initialize on first open
        if (sidebar.classList.contains('collapsed') && this.sessions.length === 0) {
            console.log('[SYNERGY SIDEBAR] First open - initializing...');
            await this.init();
        }

        sidebar.classList.toggle('expanded');
        sidebar.classList.toggle('collapsed');

        const isExpanded = sidebar.classList.contains('expanded');
        console.log(`[SYNERGY SIDEBAR] ${isExpanded ? 'Opened' : 'Closed'}`);
    }

    /**
     * Switch view (list/pinned)
     */
    switchView(viewName) {
        this.currentView = viewName;

        // Update tab buttons
        document.querySelectorAll('.synergy-view-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`.synergy-view-tab[data-view="${viewName}"]`)?.classList.add('active');

        // Update view containers
        document.querySelectorAll('.synergy-list-view, .synergy-pinned-view').forEach(view => {
            view.classList.remove('active');
        });
        document.getElementById(`synergy-${viewName}-view`)?.classList.add('active');

        // Re-render
        this.render();

        console.log(`[SYNERGY SIDEBAR] Switched to ${viewName} view`);
    }

    /**
     * Filter by category
     */
    filterByCategory(category) {
        this.currentFilter = category;

        // Update filter chips
        document.querySelectorAll('.synergy-category-chip').forEach(chip => {
            chip.classList.remove('active');
        });
        document.querySelector(`.synergy-category-chip[data-category="${category}"]`)?.classList.add('active');

        // Re-render
        this.render();

        console.log(`[SYNERGY SIDEBAR] Filtered by category: ${category}`);
    }

    /**
     * Filter by search query
     */
    filterSessions(query) {
        this.searchQuery = query;
        this.render();
    }

    /**
     * Toggle card expand/collapse (SIDEBAR ONLY)
     * Only affects cards in sidebar context
     */
    async toggleCardExpand(sessionId) {
        const isExpanded = this.expandedSessions.has(sessionId);

        if (isExpanded) {
            this.expandedSessions.delete(sessionId);
        } else {
            this.expandedSessions.add(sessionId);
        }

        // Update DOM - ONLY SIDEBAR CONTEXT
        const item = document.querySelector(`.synergy-session-item[data-session-id="${sessionId}"][data-context="sidebar"]`);
        if (item) {
            item.classList.toggle('expanded', !isExpanded);

            const expandedContent = item.querySelector('.synergy-card-expanded-content');
            const chevron = item.querySelector('.synergy-chevron i');

            if (expandedContent) {
                if (!isExpanded) {
                    // Expanding - show content and load data
                    expandedContent.style.display = 'block';
                    if (chevron) chevron.className = 'fas fa-chevron-up';
                    if (this.renderer) {
                        await this.renderer.loadAndRenderFullCard(sessionId, item);
                    }
                } else {
                    // Collapsing - hide content
                    expandedContent.style.display = 'none';
                    if (chevron) chevron.className = 'fas fa-chevron-down';
                }
            }
        }

        console.log(`[SYNERGY SIDEBAR] ${isExpanded ? 'Collapsed' : 'Expanded'} session: ${sessionId}`);
    }

    /**
     * Toggle pin status
     */
    togglePin(sessionId) {
        const isPinned = this.pinnedSessions.has(sessionId);

        if (isPinned) {
            this.pinnedSessions.delete(sessionId);
        } else {
            this.pinnedSessions.add(sessionId);
        }

        // Update DOM
        const item = document.querySelector(`.synergy-session-item[data-session-id="${sessionId}"]`);
        if (item) {
            item.classList.toggle('pinned', !isPinned);
        }

        const btn = item?.querySelector('.pin-btn');
        if (btn) {
            btn.classList.toggle('pinned', !isPinned);
        }

        console.log(`[SYNERGY SIDEBAR] ${isPinned ? 'Unpinned' : 'Pinned'} session: ${sessionId}`);
    }

    /**
     * Open session in popup
     * Uses new SynergyPopupModal for full-screen view
     */
    openInPopup(sessionId) {
        console.log(`[SYNERGY SIDEBAR] Opening session in popup: ${sessionId}`);

        // Use new popup modal if available
        if (window.synergyPopupModal) {
            window.synergyPopupModal.open(sessionId);
        }
        // Fallback to old popup if exists
        else if (window.synergyBoard && typeof window.synergyBoard.popOutCard === 'function') {
            window.synergyBoard.popOutCard(sessionId);
        } else {
            console.warn('[SYNERGY SIDEBAR] Popup function not available');
            alert('Popup modal not loaded. Please refresh the page.');
        }
    }

    /**
     * Edit session
     * Opens popup in edit mode
     */
    async editCard(sessionId) {
        console.log(`[SYNERGY SIDEBAR] Editing session: ${sessionId}`);

        // Open in new popup modal with edit mode
        if (window.synergyPopupModal) {
            await window.synergyPopupModal.open(sessionId);
            // Wait for content to load, then enable edit mode
            setTimeout(() => {
                window.synergyPopupModal.toggleEditMode();
            }, 500);
        } else {
            // Fallback to old edit behavior
            this.openInPopup(sessionId);
            setTimeout(() => {
                if (window.synergyBoard && typeof window.synergyBoard.togglePopupEdit === 'function') {
                    const popout = Array.from(document.querySelectorAll('.popout-card-window'))
                        .find(w => w.dataset.sessionId === sessionId);
                    if (popout) {
                        window.synergyBoard.togglePopupEdit(popout.id, sessionId);
                    }
                }
            }, 100);
        }
    }

    /**
     * Refresh sessions
     */
    async refreshSessions() {
        console.log('[SYNERGY SIDEBAR] Refreshing sessions...');
        await this.loadSessions();
        this.render();
    }
}

// Export as singleton
window.SynergySidebar = new SynergySidebarController();

console.log('[SYNERGY SIDEBAR CONTROLLER] Exported to window.SynergySidebar');
