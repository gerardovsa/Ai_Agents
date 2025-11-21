/**
 * FILE: UI/modules/thread-manager/thread-manager-filters.js
 * PURPOSE: Search, filter, and sort functionality for threads
 * 
 * DEPENDENCIES:
 * - UI/modules/thread-manager/thread-manager-core.js (must load first)
 * 
 * EXPORTS:
 * - Extends window.ThreadManager with filter/search methods
 * 
 * USED BY:
 * - UI/business-ai-platform-v2.html (main application)
 * - UI/modules/thread-manager/thread-manager-ui.js (filtered rendering)
 * 
 * RELATED FILES:
 * - UI/modules/thread-manager/thread-manager-core.js (core object)
 * - UI/modules/thread-manager/thread-manager-ui.js (UI updates)
 * 
 * NOTES:
 * - Handles search functionality
 * - Filter by agent, status, date
 * - Sort by various criteria
 * - Query and display logic
 * 
 * LAST MODIFIED: 2025-11-20 - Initial file creation
 */

// Filter and search methods will be defined here
// Awaiting code paste from user


// ==================== THREAD MANAGER - FILTERS MODULE ====================
/**
 * Search and Filtering
 * Handles all thread filtering, sorting, and search operations
 */

window.ThreadManagerFilters = {
    /**
     * Set filter (active/archived)
     */
    setFilter(filter, event) {
        console.log(`🔍 [Filters] Setting filter: ${filter}`);
        this.currentFilter = filter;

        // Update active tab
        document.querySelectorAll('.thread-filter-tab, .thread-view-tab').forEach(tab => {
            tab.classList.remove('active');
        });

        if (event) {
            const clickedTab = event.target.closest('.thread-filter-tab') ||
                event.target.closest('.thread-view-tab');
            if (clickedTab) {
                clickedTab.classList.add('active');
            }
        }

        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList();
        }
    },

    /**
     * Filter threads by search query
     */
    filterThreads(searchQuery) {
        console.log(`🔍 [Filters] Search query: "${searchQuery}"`);
        this.searchQuery = searchQuery.toLowerCase().trim();

        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList();
        }
    },

    /**
     * Filter by location
     */
    filterByLocation(location) {
        console.log(`📍 [Filters] Location filter: ${location}`);
        this.locationFilter = location;

        // Update active chip
        document.querySelectorAll('.thread-filter-chip').forEach(chip => {
            chip.classList.toggle('active', chip.dataset.filter === location);
        });

        // Sync dropdown if exists
        const agentSelect = document.getElementById('agent-select');
        if (agentSelect && agentSelect.value !== location) {
            agentSelect.value = location;
        }

        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList();
        }
    },

    /**
     * Set sort order (updated/created)
     */
    setSortOrder(order, event) {
        console.log(`🔄 [Filters] Setting sort order: ${order}`);
        this.sortOrder = order;

        // Update active button
        document.querySelectorAll('.thread-sort-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.sort === order);
        });

        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList();
        }
    },

    /**
     * Filter by tag
     */
    filterByTag(tag) {
        console.log(`🏷️ [Filters] Tag filter: ${tag}`);

        // Toggle tag filter
        if (this.activeTagFilter === tag) {
            this.activeTagFilter = null;
        } else {
            this.activeTagFilter = tag;
        }

        // Update active chip
        document.querySelectorAll('[data-filter="synergy"], [data-filter="automation"]').forEach(chip => {
            chip.classList.remove('active');
        });

        if (this.activeTagFilter) {
            const activeChip = document.querySelector(`[data-filter="${tag}"]`);
            if (activeChip) {
                activeChip.classList.add('active');
            }
        }

        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList();
        }
    },

    /**
     * Filter by date range
     */
    filterByDateRange(range) {
        console.log(`📅 [Filters] Date range: ${range}`);

        const now = new Date();
        let startDate = null;

        switch (range) {
            case 'today':
                startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                break;
            case 'yesterday':
                startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
                break;
            case '3days':
                startDate = new Date(now.getTime() - (3 * 24 * 60 * 60 * 1000));
                break;
            case 'week':
                startDate = new Date(now.getTime() - (7 * 24 * 60 * 60 * 1000));
                break;
            case 'month':
                startDate = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());
                break;
            case 'all':
            default:
                startDate = null;
                break;
        }

        this.dateRangeFilter = { range, startDate };

        // Sync dropdown if exists
        const dateSelect = document.getElementById('date-range-select');
        if (dateSelect && dateSelect.value !== range) {
            dateSelect.value = range;
        }

        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList();
        }
    },

    /**
     * Get date label for grouping
     */
    getDateLabel(date) {
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        const lastWeek = new Date(today);
        lastWeek.setDate(lastWeek.getDate() - 7);

        const threadDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

        if (threadDate.getTime() === today.getTime()) {
            return 'Today';
        } else if (threadDate.getTime() === yesterday.getTime()) {
            return 'Yesterday';
        } else if (threadDate >= lastWeek) {
            return 'Last 7 Days';
        } else if (threadDate.getMonth() === now.getMonth() && threadDate.getFullYear() === now.getFullYear()) {
            return 'This Month';
        } else if (threadDate.getFullYear() === now.getFullYear()) {
            return date.toLocaleDateString('en-US', { month: 'long' });
        } else {
            return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
        }
    },

    /**
     * Clear all filters
     */
    clearAllFilters() {
        console.log('🧹 [Filters] Clearing all filters');

        this.searchQuery = '';
        this.locationFilter = 'all';
        this.activeTagFilter = null;
        this.dateRangeFilter = { range: 'all', startDate: null };

        // Clear search input
        const searchInput = document.getElementById('thread-search-input');
        if (searchInput) {
            searchInput.value = '';
        }

        // Clear active chips
        document.querySelectorAll('.thread-filter-chip').forEach(chip => {
            chip.classList.remove('active');
        });

        // Reset to "all" location
        const allChip = document.querySelector('[data-filter="all"]');
        if (allChip) {
            allChip.classList.add('active');
        }

        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList();
        }
    }
};

console.log('✅ ThreadManager-Filters module loaded');