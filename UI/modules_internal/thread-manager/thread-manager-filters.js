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
    },

    /**
     * NEW: Filter threads by Team ID(s) with backend authorization
     * Supports single or multiple Team IDs (multi-select)
     * @param {string|string[]} teamIds - Team ID(s) to filter by
     */
    async filterByTeamId(teamIds) {
        const teamIdArray = Array.isArray(teamIds) ? teamIds : [teamIds];
        const teamIdParam = teamIdArray.join(',');

        console.log(`👥 [Filters] Filtering by Team ID(s): ${teamIdParam}`);

        try {
            // Store active Team ID filter
            this.teamIdFilter = teamIdArray;

            // Show loading state
            const filterLabel = teamIdArray.length === 1 ? teamIdArray[0] : `${teamIdArray.length} teams`;
            this.showFilterIndicator('Team ID', `${filterLabel} (loading...)`);

            // SECURITY: Use backend filtering endpoint with authorization
            const userId = window.UserAuth?.user?.id || window.currentUserId;

            if (!userId) {
                throw new Error('User not authenticated');
            }

            const response = await fetch(
                `/api/threads/filter-by-team?team_ids=${encodeURIComponent(teamIdParam)}&user_id=${userId}`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (!response.ok) {
                if (response.status === 403) {
                    throw new Error(`Access denied: You do not have permission to view one or more Team IDs`);
                } else if (response.status === 404) {
                    throw new Error(`One or more Team IDs not found`);
                } else {
                    throw new Error(`Failed to filter threads: ${response.statusText}`);
                }
            }

            const data = await response.json();

            // Update ThreadManager with filtered threads
            if (window.ThreadManager && data.threads) {
                // Store original threads if not already stored
                if (!this.originalThreads) {
                    this.originalThreads = [...(window.ThreadManager.threads || [])];
                }

                // Replace threads array with filtered results
                window.ThreadManager.threads = data.threads;

                // Apply color coding to threads based on Team ID
                this.applyTeamIdColors(data.threads);

                // Update UI to show filter is active
                const finalLabel = teamIdArray.length === 1 ? teamIdArray[0] : `${teamIdArray.length} teams`;
                this.showFilterIndicator('Team ID', `${finalLabel} (${data.threads.length} threads)`);

                // Re-render thread list
                if (typeof this.renderThreadList === 'function') {
                    this.renderThreadList();
                }

                // Update URL with filter parameter
                const url = new URL(window.location);
                url.searchParams.set('team_id', teamIdParam);
                window.history.pushState({}, '', url);

                // Show notification
                if (typeof showNotification === 'function') {
                    showNotification(
                        `Showing ${data.threads.length} threads for ${finalLabel}`,
                        'success'
                    );
                }
            }

        } catch (error) {
            console.error(`[Filters] Team ID filter error:`, error);

            // Show error notification
            if (typeof showNotification === 'function') {
                showNotification(error.message || 'Failed to filter by Team ID', 'error');
            }

            // Clear filter on error
            this.clearTeamIdFilter();
        }
    },

    /**
     * NEW: Apply color coding to threads based on Team ID
     * @param {Array} threads - Threads to colorize
     */
    applyTeamIdColors(threads) {
        if (!threads || !window.getTeamIdColor) return;

        // Add color property to each thread based on team_id
        threads.forEach(thread => {
            if (thread.team_id) {
                thread._teamColor = window.getTeamIdColor(thread.team_id);
            }
        });
    },

    /**
     * NEW: Clear Team ID filter and restore original threads
     */
    clearTeamIdFilter() {
        console.log(`👥 [Filters] Clearing Team ID filter`);

        this.teamIdFilter = null;
        this.hideFilterIndicator();

        // Restore original threads if they were stored
        if (this.originalThreads && window.ThreadManager) {
            window.ThreadManager.threads = [...this.originalThreads];
            this.originalThreads = null;
        }

        // Re-render thread list
        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList();
        }

        // Update URL
        const url = new URL(window.location);
        url.searchParams.delete('team_id');
        window.history.pushState({}, '', url);
    },

    /**
     * NEW: Show filter indicator bar
     * @param {string} filterType - Type of filter (e.g., 'Team ID')
     * @param {string} filterValue - Value being filtered
     */
    showFilterIndicator(filterType, filterValue) {
        let indicator = document.getElementById('active-filter-indicator');

        // Create indicator if it doesn't exist
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'active-filter-indicator';
            indicator.className = 'active-filter-bar';

            // Insert at top of thread list container
            const threadListContainer = document.querySelector('.thread-list-container') ||
                document.querySelector('#thread-cards-container');
            if (threadListContainer) {
                threadListContainer.insertBefore(indicator, threadListContainer.firstChild);
            }
        }

        // Update indicator content
        indicator.innerHTML = `
            <div class="filter-indicator-content">
                <i class="fas fa-filter"></i>
                <span class="filter-label">Filtered by ${filterType}:</span>
                <span class="filter-value">${filterValue}</span>
                <button class="filter-clear-btn" onclick="ThreadManager.clearTeamIdFilter()" title="Clear filter">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        indicator.style.display = 'flex';
    },

    /**
     * NEW: Hide filter indicator bar
     */
    hideFilterIndicator() {
        const indicator = document.getElementById('active-filter-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    },

    /**
     * NEW: Get filtered threads based on all active filters
     * @returns {Array} Filtered thread array
     */
    getFilteredThreads() {
        const threads = window.ThreadManager?.threads || [];
        let filtered = [...threads];

        // Apply Team ID filter if active
        if (this.teamIdFilter) {
            filtered = filtered.filter(t => t.team_id === this.teamIdFilter);
        }

        // Apply location filter if active
        if (this.locationFilter && this.locationFilter !== 'all') {
            filtered = filtered.filter(t => t.location === this.locationFilter);
        }

        // Apply search query if active
        if (this.searchQuery) {
            filtered = filtered.filter(t => {
                const title = (t.title || '').toLowerCase();
                const description = (t.description || '').toLowerCase();
                return title.includes(this.searchQuery) || description.includes(this.searchQuery);
            });
        }

        return filtered;
    }
};

console.log('✅ ThreadManager-Filters module loaded');