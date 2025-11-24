
// ========== AUTOMATIONS SIDEBAR ==========
const AutomationsSidebar = {
    automations: [],
    executions: new Map(),
    automationsLoaded: false,
    currentFilter: 'all',
    searchQuery: '',
    realtimeChannel: null,
    executionsChannel: null,
    supabaseClient: null,

    async initSupabase() {
        if (this.supabaseClient) return true; // Already initialized

        // Ensure Supabase config is loaded first
        if (!window.SUPABASE_CONFIG_LOADED) {
            console.log('[AUTOMATIONS] Waiting for Supabase config...');
            await window.loadSupabaseConfig();
        }

        // Check if config loaded successfully
        if (!window.SUPABASE_ANON_KEY || !window.SUPABASE_URL) {
            console.error('? [AUTOMATIONS] Supabase config not available');
            showNotification('Supabase configuration not available', 'error');
            return false;
        }

        try {
            // NOTE: SUPABASE_CLIENT is set by SupabaseConnectionManager
            if (!window.SUPABASE_CLIENT) {
                console.error('? [AUTOMATIONS] Supabase connection manager not initialized yet');
                showNotification('Supabase connection manager not ready', 'error');
                return false;
            }

            this.supabaseClient = window.SUPABASE_CLIENT;
            console.log('? [AUTOMATIONS] Using shared Supabase client from connection manager');
            return true;
        } catch (error) {
            console.error('? [AUTOMATIONS] Failed to initialize Supabase:', error);
            showNotification('Failed to connect to Supabase', 'error');
            return false;
        }
    },

    async toggleSidebar() {
        console.log('[AUTOMATIONS] Toggle clicked');

        // Initialize Supabase first
        if (!this.supabaseClient) {
            const initialized = await this.initSupabase();
            if (!initialized) {
                console.error('? [AUTOMATIONS] Cannot open sidebar - Supabase not initialized');
                return;
            }
        }

        // Lazy load automations on first sidebar open
        if (!this.automationsLoaded) {
            console.log('? [AUTOMATIONS] First use - lazy loading automations...');
            await this.loadAutomations();
            this.initRealtimeSubscription();
        }

        // Toggle sidebar visibility
        const sidebar = document.getElementById('automations-sidebar');
        const toggle = document.getElementById('automations-sidebar-toggle');
        const container = document.querySelector('.platform-container');

        if (sidebar) {
            const side = sidebar.getAttribute('data-side') || 'right';
            sidebar.classList.toggle('collapsed');
            const isOpen = !sidebar.classList.contains('collapsed');

            // Keep toggle visible at all times
            // (removed toggle.style.display logic to keep it always visible)

            // Update container margin based on side
            if (container) {
                if (isOpen) {
                    container.setAttribute('data-automations-side', side);
                } else {
                    container.removeAttribute('data-automations-side');
                }
            }

            console.log(`${isOpen ? '??' : '??'} [AUTOMATIONS] Sidebar ${isOpen ? 'opened' : 'closed'} on ${side} side`);
        }
    },

    async loadAutomations() {
        try {
            console.log('[AUTOMATIONS] Loading automations from API...');
            const startTime = performance.now();

            // Use backend API instead of direct Supabase
            const response = await fetch('/api/automation/list', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token') || ''}`
                }
            });

            console.log('[AUTOMATIONS] API response status:', response.status);

            if (!response.ok) {
                console.error('[AUTOMATIONS] API request failed with status:', response.status);
                const errorText = await response.text();
                console.error('[AUTOMATIONS] Error response:', errorText);
                this.automations = [];
                this.automationsLoaded = true;
                this.renderAutomations();
                return;
            }

            const data = await response.json();
            console.log('[AUTOMATIONS] API response data:', data);

            if (!data.success) {
                console.error('[AUTOMATIONS] API error:', data.error);
                this.automations = [];
                this.automationsLoaded = true;
                this.renderAutomations();
                return;
            }

            // Backend returns 'workflows' array with UI-compatible format
            this.automations = data.workflows || [];
            this.automationsLoaded = true;

            const endTime = performance.now();
            const loadTime = (endTime - startTime).toFixed(0);
            console.log(`[AUTOMATIONS] Loaded ${this.automations.length} automations in ${loadTime}ms`);

            this.updateStats();
            this.renderAutomations();
        } catch (error) {
            console.error('[AUTOMATIONS] Failed to load:', error);
            this.automations = [];
            this.automationsLoaded = true;
            this.renderAutomations();
        }
    },

    initRealtimeSubscription() {
        if (!window.SUPABASE_REALTIME_ENABLED) {
            // Realtime not enabled, skip silently
            return;
        }

        console.log('[AUTOMATIONS] Initializing Realtime subscriptions...');

        // Subscribe to automation_workflows changes
        this.realtimeChannel = this.supabaseClient
            .channel('automation-workflows-changes')
            .on('postgres_changes', {
                event: '*',
                schema: 'public',
                table: 'automation_workflows'
            }, (payload) => {
                console.log('[REALTIME] Automation change:', payload);
                this.handleAutomationChange(payload);
            })
            .subscribe((status) => {
                if (status === 'SUBSCRIBED') {
                    console.log('? [REALTIME] Automations subscription active');
                    this.updateRealtimeStatus(true);
                }
                // Silently ignore errors - already warned in ThreadManager
            });

        // Subscribe to workflow_executions changes
        this.executionsChannel = this.supabaseClient
            .channel('workflow-executions-changes')
            .on('postgres_changes', {
                event: '*',
                schema: 'public',
                table: 'workflow_executions'
            }, (payload) => {
                console.log('[REALTIME] Execution change:', payload);
                this.handleExecutionChange(payload);
            })
            .subscribe((status) => {
                if (status === 'SUBSCRIBED') {
                    console.log('? [REALTIME] Executions subscription active');
                }
                // Silently ignore errors - already warned in ThreadManager
            });
    },

    handleAutomationChange(payload) {
        const { eventType, new: newRecord, old: oldRecord } = payload;

        if (eventType === 'INSERT') {
            console.log('? [REALTIME] New automation:', newRecord.name);
            this.automations.unshift(newRecord);
            showNotification(`New automation created: ${newRecord.name}`, 'success');
        } else if (eventType === 'UPDATE') {
            console.log('[REALTIME] Automation updated:', newRecord.name);
            const index = this.automations.findIndex(a => a.workflow_id === newRecord.workflow_id);
            if (index !== -1) {
                this.automations[index] = newRecord;
            }
            showNotification(`Automation updated: ${newRecord.name}`, 'info');
        } else if (eventType === 'DELETE') {
            console.log('?[REALTIME] Automation deleted:', oldRecord.name);
            this.automations = this.automations.filter(a => a.workflow_id !== oldRecord.workflow_id);
            showNotification(`Automation deleted: ${oldRecord.name}`, 'warning');
        }

        this.updateStats();
        this.renderAutomations();
    },

    handleExecutionChange(payload) {
        const { eventType, new: newRecord } = payload;

        if (eventType === 'INSERT' || eventType === 'UPDATE') {
            this.executions.set(newRecord.execution_id, newRecord);

            // Update run counts for the automation
            const automation = this.automations.find(a => a.workflow_id === newRecord.workflow_id);
            if (automation) {
                // Refresh automation data to get updated counts
                this.refreshAutomation(automation.workflow_id);
            }
        }

        this.updateStats();
    },

    async refreshAutomation(workflowId) {
        try {
            const { data, error } = await this.supabaseClient
                .from('automation_workflows')
                .select('*')
                .eq('workflow_id', workflowId)
                .single();

            if (error) throw error;

            const index = this.automations.findIndex(a => a.workflow_id === workflowId);
            if (index !== -1) {
                this.automations[index] = data;
                this.renderAutomations();
            }
        } catch (error) {
            console.error('? [AUTOMATIONS] Failed to refresh automation:', error);
        }
    },

    updateRealtimeStatus(connected) {
        const indicator = document.getElementById('automation-realtime-status');
        if (indicator) {
            if (connected) {
                indicator.innerHTML = '<span class="pulse-dot"></span>LIVE';
                indicator.style.background = 'rgba(34, 197, 94, 0.1)';
                indicator.style.color = 'var(--success, #22c55e)';
            } else {
                indicator.innerHTML = '<i class="fas fa-circle"></i>OFFLINE';
                indicator.style.background = 'rgba(239, 68, 68, 0.1)';
                indicator.style.color = 'var(--error, #ef4444)';
            }
        }
    },

    updateStats() {
        const total = this.automations.length;
        const enabled = this.automations.filter(a => a.enabled).length;
        const running = Array.from(this.executions.values()).filter(e => e.status === 'running').length;

        document.getElementById('automations-total').textContent = total;
        document.getElementById('automations-enabled').textContent = enabled;
        document.getElementById('automations-running').textContent = running;
    },

    setFilter(filter) {
        console.log('[AUTOMATIONS] Filter changed:', filter);
        this.currentFilter = filter;

        // Update active state on filter chips
        document.querySelectorAll('.automation-filter-chip').forEach(chip => {
            if (chip.dataset.filter === filter) {
                chip.classList.add('active');
            } else {
                chip.classList.remove('active');
            }
        });

        this.renderAutomations();
    },

    filterAutomations() {
        this.searchQuery = document.getElementById('automations-search').value.toLowerCase();
        this.renderAutomations();
    },

    getFilteredAutomations() {
        let filtered = [...this.automations];

        // Apply status filter
        if (this.currentFilter === 'enabled') {
            filtered = filtered.filter(a => a.enabled);
        } else if (this.currentFilter === 'disabled') {
            filtered = filtered.filter(a => !a.enabled);
        } else if (this.currentFilter === 'recent') {
            filtered = filtered.filter(a => {
                const lastRun = new Date(a.last_run_at);
                const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
                return lastRun > dayAgo;
            });
        } else if (this.currentFilter === 'scheduled') {
            // Would need to check workflow_schedules table
            // For now, just show all
        }

        // Apply search filter
        if (this.searchQuery) {
            filtered = filtered.filter(a => {
                const searchableText = `${a.name} ${a.slug} ${a.description || ''} ${a.category || ''}`.toLowerCase();
                return searchableText.includes(this.searchQuery);
            });
        }

        return filtered;
    },

    renderAutomations() {
        const container = document.getElementById('automations-content');
        const filtered = this.getFilteredAutomations();

        if (filtered.length === 0) {
            container.innerHTML = `
                        <div class="automation-empty-state">
                            <i class="fa-solid fa-robot"></i>
                            <p>${this.searchQuery ? 'No automations match your search' : 'No automations found'}</p>
                            <p>${this.searchQuery ? 'Try a different search term' : 'Create your first automation in the workflow canvas'}</p>
                        </div>
                    `;
            return;
        }

        container.innerHTML = filtered.map(automation => this.createAutomationItem(automation)).join('');
    },

    createAutomationItem(automation) {
        const lastRun = automation.last_run_at ? new Date(automation.last_run_at) : null;
        const created = new Date(automation.created_at);
        const updated = new Date(automation.updated_at);

        const timeAgo = (date) => {
            if (!date) return 'Never';
            const seconds = Math.floor((new Date() - date) / 1000);
            if (seconds < 60) return `${seconds}s ago`;
            if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
            if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
            return `${Math.floor(seconds / 86400)}d ago`;
        };

        return `
                    <div class="automation-item ${automation.enabled ? 'enabled' : 'disabled'}" 
                        onclick="AutomationsSidebar.openAutomation('${automation.slug}')">
                        <div class="automation-item-header">
                            <div>
                                <div class="automation-item-title">${this.escapeHtml(automation.name)}</div>
                                <div class="automation-item-slug">${automation.slug}</div>
                            </div>
                            <span class="automation-status-badge ${automation.enabled ? 'enabled' : 'disabled'}">
                                ${automation.enabled ? 'ENABLED' : 'DISABLED'}
                            </span>
                        </div>
                        
                        ${automation.description ? `
                            <div class="automation-item-description">
                                ${this.escapeHtml(automation.description)}
                            </div>
                        ` : ''}
                        
                        <div class="automation-item-meta">
                            ${automation.category ? `
                                <div class="automation-meta-item">
                                    <i class="fas fa-tag"></i>
                                    ${automation.category}
                                </div>
                            ` : ''}
                            <div class="automation-meta-item">
                                <i class="fas fa-clock"></i>
                                Updated ${timeAgo(updated)}
                            </div>
                            <div class="automation-meta-item">
                                <i class="fas fa-calendar-plus"></i>
                                Created ${created.toLocaleDateString()}
                            </div>
                        </div>
                        
                        <div class="automation-item-stats">
                            <div class="automation-stat-mini">
                                <i class="fas fa-play-circle"></i>
                                <strong>${automation.run_count || 0}</strong> runs
                            </div>
                            <div class="automation-stat-mini">
                                <i class="fas fa-check-circle" style="color: var(--success);"></i>
                                <strong>${automation.success_count || 0}</strong> success
                            </div>
                            <div class="automation-stat-mini">
                                <i class="fas fa-exclamation-circle" style="color: var(--error);"></i>
                                <strong>${automation.error_count || 0}</strong> errors
                            </div>
                            <div class="automation-stat-mini">
                                <i class="fas fa-bolt"></i>
                                Last: ${lastRun ? timeAgo(lastRun) : 'Never'}
                            </div>
                        </div>
                    </div>
                `;
    },

    async refreshAutomations() {
        console.log('[AUTOMATIONS] Manual refresh triggered');
        await this.loadAutomations();
        showNotification('Automations refreshed', 'success');
    },

    async openAutomation(slug) {
        try {
            console.log('[AUTOMATIONS] Opening workflow:', slug);

            // Fetch workflow details from backend API
            const response = await fetch(`/api/automation/${slug}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token') || ''}`
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch workflow: ${response.status}`);
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to load workflow');
            }

            const workflow = data.automation || data.workflow;

            // Check if automation canvas exists
            if (typeof automationCanvas !== 'undefined' && automationCanvas) {
                // Switch to automation workflows tab FIRST
                const automationTab = document.querySelector('[data-module-id="automation-workflows"]');
                if (automationTab) {
                    console.log('[AUTOMATIONS] Switching to automation tab');
                    automationTab.click();
                } else {
                    // Try alternative selector
                    const altTab = document.querySelector('[data-tab="automation"]');
                    if (altTab) {
                        console.log('[AUTOMATIONS] Switching to automation tab (alt selector)');
                        altTab.click();
                    }
                }

                // Load workflow into canvas with longer delay to ensure tab switch completes
                setTimeout(() => {
                    if (automationCanvas.loadWorkflowFromList) {
                        console.log('[AUTOMATIONS] Loading workflow into canvas:', workflow);
                        automationCanvas.loadWorkflowFromList(workflow);
                        // Show workflow library with loaded workflow highlighted
                        this.showWorkflowInLibrary(workflow);
                    } else {
                        console.warn('[AUTOMATIONS] Canvas loadWorkflowFromList not available');
                    }
                }, 300);
            } else {
                console.error('[AUTOMATIONS] Automation canvas not initialized');
                if (typeof showNotification !== 'undefined') {
                    showNotification('Automation canvas module not loaded. Please refresh the page.', 'error');
                }
            }
        } catch (error) {
            console.error('[AUTOMATIONS] Failed to open workflow:', error);
            showNotification(`Failed to open workflow: ${error.message}`, 'error');
        }
    },

    showWorkflowInLibrary(workflow) {
        // Populate floating workflow library with workflow cards
        const library = document.getElementById('workflow-library-content');
        if (!library) return;

        // Render all workflows using the same automation-item structure from the sidebar
        library.innerHTML = this.automations.map(auto => {
            const isActive = auto.slug === workflow.slug;
            return this.createAutomationItemForLibrary(auto, isActive);
        }).join('');

        // Show library panel
        const panel = document.getElementById('workflow-library-panel');
        if (panel) {
            panel.style.display = 'flex';
            panel.style.maxHeight = '600px';
        }
    },

    createAutomationItemForLibrary(automation, isActive = false) {
        // Same structure as createAutomationItem but with active state highlighting
        const lastRun = automation.last_run_at ? new Date(automation.last_run_at) : null;
        const created = new Date(automation.created_at);
        const updated = new Date(automation.updated_at);

        const timeAgo = (date) => {
            if (!date) return 'Never';
            const seconds = Math.floor((new Date() - date) / 1000);
            if (seconds < 60) return `${seconds}s ago`;
            if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
            if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
            return `${Math.floor(seconds / 86400)}d ago`;
        };

        return `
            <div class="automation-item ${automation.enabled ? 'enabled' : 'disabled'} ${isActive ? 'library-active' : ''}" 
                onclick="AutomationsSidebar.loadWorkflowInCanvas('${automation.slug}')"
                style="${isActive ? 'background: var(--accent-primary-alpha); border-left: 3px solid var(--accent-primary);' : ''}">
                <div class="automation-item-header">
                    <div>
                        <div class="automation-item-title">${this.escapeHtml(automation.name)}</div>
                        <div class="automation-item-slug">${automation.slug}</div>
                    </div>
                    <span class="automation-status-badge ${automation.enabled ? 'enabled' : 'disabled'}">
                        ${automation.enabled ? 'ENABLED' : 'DISABLED'}
                    </span>
                </div>
                
                ${automation.description ? `
                    <div class="automation-item-description">
                        ${this.escapeHtml(automation.description)}
                    </div>
                ` : ''}
                
                <div class="automation-item-meta">
                    ${automation.category ? `
                        <div class="automation-meta-item">
                            <i class="fas fa-tag"></i>
                            ${automation.category}
                        </div>
                    ` : ''}
                    <div class="automation-meta-item">
                        <i class="fas fa-clock"></i>
                        Updated ${timeAgo(updated)}
                    </div>
                    <div class="automation-meta-item">
                        <i class="fas fa-calendar-plus"></i>
                        Created ${created.toLocaleDateString()}
                    </div>
                </div>
                
                <div class="automation-item-stats">
                    <div class="automation-stat-mini">
                        <i class="fas fa-play-circle"></i>
                        <strong>${automation.run_count || 0}</strong> runs
                    </div>
                    <div class="automation-stat-mini">
                        <i class="fas fa-check-circle" style="color: var(--success);"></i>
                        <strong>${automation.success_count || 0}</strong> success
                    </div>
                    <div class="automation-stat-mini">
                        <i class="fas fa-exclamation-circle" style="color: var(--error);"></i>
                        <strong>${automation.error_count || 0}</strong> errors
                    </div>
                    <div class="automation-stat-mini">
                        <i class="fas fa-bolt"></i>
                        Last: ${lastRun ? timeAgo(lastRun) : 'Never'}
                    </div>
                </div>
            </div>
        `;
    },

    async loadWorkflowInCanvas(slug) {
        // Reuse openAutomation logic
        await this.openAutomation(slug);
    },

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    cleanup() {
        // Unsubscribe from realtime channels when needed
        if (this.realtimeChannel) {
            this.supabaseClient.removeChannel(this.realtimeChannel);
        }
        if (this.executionsChannel) {
            this.supabaseClient.removeChannel(this.executionsChannel);
        }
    }
};

// Expose globally
window.AutomationsSidebar = AutomationsSidebar;

// Safe wrapper function for onclick handlers
window.toggleAutomationsSidebar = function () {
    if (window.AutomationsSidebar && typeof window.AutomationsSidebar.toggleSidebar === 'function') {
        window.AutomationsSidebar.toggleSidebar();
    } else {
        console.error('❌ [AUTOMATIONS] AutomationsSidebar not loaded yet');
    }
};