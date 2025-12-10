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

        // Set tag filter (or clear if "all")
        if (tag === 'all') {
            this.activeTagFilter = null;
        } else {
            this.activeTagFilter = tag;
        }

        // Sync dropdown if exists
        const tagsSelect = document.getElementById('tags-select');
        if (tagsSelect && tagsSelect.value !== tag) {
            tagsSelect.value = tag;
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

        // Show/hide custom date picker
        if (range === 'custom') {
            this.toggleCustomDateRange(true);
            return; // Don't apply filter yet - wait for user to apply custom range
        } else {
            this.toggleCustomDateRange(false);
        }

        const now = new Date();
        let startDate = null;
        let endDate = null;

        switch (range) {
            case 'today':
                startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);
                break;
            case 'yesterday':
                startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
                endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1, 23, 59, 59);
                break;
            case '3days':
                startDate = new Date(now.getTime() - (3 * 24 * 60 * 60 * 1000));
                endDate = now;
                break;
            case 'week':
                startDate = new Date(now.getTime() - (7 * 24 * 60 * 60 * 1000));
                endDate = now;
                break;
            case 'month':
                startDate = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());
                endDate = now;
                break;
            case 'all':
            default:
                startDate = null;
                endDate = null;
                break;
        }

        this.dateRangeFilter = { range, startDate, endDate };

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
        this.dateRangeFilter = { range: 'all', startDate: null, endDate: null };

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
    },

    /**
     * NEW: Populate agent dropdown with dynamic agents from threads.location
     */
    populateAgentDropdown() {
        const agentSelect = document.getElementById('agent-select');
        if (!agentSelect) return;

        // Get unique agent locations from threads
        const threads = window.ThreadManager?.threads || [];
        const uniqueLocations = new Set();

        threads.forEach(thread => {
            if (thread.location) {
                uniqueLocations.add(thread.location);
            }
        });

        // Clear existing options (except "All Locations")
        agentSelect.innerHTML = '<option value="all">All Locations</option>';

        // Add Prime if it exists
        if (uniqueLocations.has('prime')) {
            agentSelect.innerHTML += '<option value="prime">Prime</option>';
            uniqueLocations.delete('prime');
        }

        // Add agent options (sorted)
        const agentLocations = Array.from(uniqueLocations)
            .filter(loc => loc.startsWith('agent-'))
            .sort();

        if (agentLocations.length > 0) {
            agentSelect.innerHTML += '<optgroup label="Agents">';
            agentLocations.forEach(location => {
                const agentNumber = location.replace('agent-', '');
                agentSelect.innerHTML += `<option value="${location}">Agent-${agentNumber}</option>`;
            });
            agentSelect.innerHTML += '</optgroup>';
        }

        console.log(`✅ [Filters] Populated agent dropdown with ${uniqueLocations.size + 1} locations`);
    },

    /**
     * NEW: Populate tags dropdown with dynamic tags from threads
     */
    populateTagsDropdown() {
        const tagsSelect = document.getElementById('tags-select');
        if (!tagsSelect) return;

        // Get unique tags from threads
        const threads = window.ThreadManager?.threads || [];
        const uniqueTags = new Set();

        threads.forEach(thread => {
            // Check for Synergy
            if (thread.synergy_card_id) {
                uniqueTags.add('synergy');
            }
            // Check for Automation
            if (thread.automation_workflow_id) {
                uniqueTags.add('automation');
            }
            // Add other tags if they exist
            if (thread.tags && Array.isArray(thread.tags)) {
                thread.tags.forEach(tag => uniqueTags.add(tag));
            }
        });

        // Clear existing options (except "All Tags")
        tagsSelect.innerHTML = '<option value="all">All Tags</option>';

        // Add tag options
        if (uniqueTags.size > 0) {
            Array.from(uniqueTags).sort().forEach(tag => {
                // Skip null/undefined tags
                if (!tag) return;

                const tagIcon = tag === 'synergy' ? '🔄' :
                    tag === 'automation' ? '⚡' : '🏷️';
                const tagLabel = tag.charAt(0).toUpperCase() + tag.slice(1);
                tagsSelect.innerHTML += `<option value="${tag}">${tagIcon} ${tagLabel}</option>`;
            });
        }

        console.log(`✅ [Filters] Populated tags dropdown with ${uniqueTags.size} tags`);
    },

    /**
     * NEW: Handle custom date range selection
     */
    applyCustomDateRange() {
        const startInput = document.getElementById('date-range-start');
        const endInput = document.getElementById('date-range-end');
        const customRangeDiv = document.getElementById('thread-custom-date-range');

        if (!startInput || !endInput) {
            console.error('❌ [Filters] Date range inputs not found');
            return;
        }

        const startDate = startInput.value ? new Date(startInput.value) : null;
        const endDate = endInput.value ? new Date(endInput.value) : null;

        if (!startDate && !endDate) {
            console.warn('⚠️ [Filters] No custom date range specified');
            return;
        }

        // Validate date range
        if (startDate && endDate && startDate > endDate) {
            alert('Start date must be before end date');
            return;
        }

        // Store custom range
        this.dateRangeFilter = {
            range: 'custom',
            startDate: startDate,
            endDate: endDate
        };

        console.log(`📅 [Filters] Custom date range: ${startDate?.toLocaleDateString()} - ${endDate?.toLocaleDateString()}`);

        // Hide custom range picker
        if (customRangeDiv) {
            customRangeDiv.style.display = 'none';
        }

        // Re-render thread list
        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList();
        }
    },

    /**
     * NEW: Show/hide custom date range picker
     */
    toggleCustomDateRange(show) {
        const customRangeDiv = document.getElementById('thread-custom-date-range');
        if (customRangeDiv) {
            customRangeDiv.style.display = show ? 'block' : 'none';
        }
    }
};

console.log('✅ ThreadManager-Filters module loaded');