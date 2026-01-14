
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
                        onclick="AutomationsSidebar.openSettingsPanel(${JSON.stringify(automation).replace(/"/g, '&quot;')})">
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
            const API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
            const response = await fetch(`${API_BASE_URL}/api/automation/${slug}`, {
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
                data-category="${automation.category || 'workflow'}"
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

    /**
     * Open settings panel for an automation
     * @param {Object} automation - Automation data
     */
    async openSettingsPanel(automation) {
        try {
            console.log('[AUTOMATIONS] Opening settings panel for:', automation.slug);

            // Load settings into sync manager
            await AutomationSettingsSync.loadSettings(automation.slug);

            // Subscribe to settings changes
            if (this.settingsSyncUnsubscribe) {
                this.settingsSyncUnsubscribe();
            }
            this.settingsSyncUnsubscribe = AutomationSettingsSync.subscribe((eventType, data) => {
                if (eventType === 'update' || eventType === 'save') {
                    // Re-render settings panel with updated data
                    this.refreshSettingsPanel();
                }
            });

            // Render settings panel
            const content = document.getElementById('automations-content');
            content.innerHTML = this.createSettingsPanel(AutomationSettingsSync.getCurrentAutomation());

        } catch (error) {
            console.error('[AUTOMATIONS] Failed to open settings panel:', error);
            showNotification(`Failed to open settings: ${error.message}`, 'error');
        }
    },

    /**
     * Close settings panel and return to automation list
     */
    closeSettingsPanel() {
        console.log('[AUTOMATIONS] Closing settings panel');

        // Check for unsaved changes
        if (AutomationSettingsSync.hasUnsavedChanges()) {
            const confirmed = confirm('You have unsaved changes. Do you want to save before closing?');
            if (confirmed) {
                AutomationSettingsSync.save();
            }
        }

        // Unsubscribe from settings sync
        if (this.settingsSyncUnsubscribe) {
            this.settingsSyncUnsubscribe();
            this.settingsSyncUnsubscribe = null;
        }

        // Return to automation list
        this.renderAutomations();
    },

    /**
     * Refresh settings panel with current data
     */
    refreshSettingsPanel() {
        const automation = AutomationSettingsSync.getCurrentAutomation();
        if (!automation) return;

        const content = document.getElementById('automations-content');
        if (content && content.querySelector('.automation-settings-panel')) {
            content.innerHTML = this.createSettingsPanel(automation);
        }
    },

    /**
     * Create settings panel HTML
     * @param {Object} automation - Automation data
     * @returns {string} HTML string
     */
    createSettingsPanel(automation) {
        const isDraft = AutomationSettingsSync.isDraft();

        return `
            <div class="automation-settings-panel">
                <div class="settings-panel-header">
                    <button class="settings-back-btn" onclick="AutomationsSidebar.closeSettingsPanel()">
                        <i class="fas fa-arrow-left"></i> Back to List
                    </button>
                    <div class="settings-panel-title">
                        <h3>${this.escapeHtml(automation.name)}</h3>
                        <span class="automation-status-badge ${automation.enabled ? 'enabled' : 'disabled'}">
                            ${automation.enabled ? 'ENABLED' : 'DISABLED'}
                        </span>
                    </div>
                    <div class="settings-panel-slug">${automation.slug}</div>
                </div>

                ${isDraft ? `
                    <div class="draft-mode-banner">
                        <i class="fas fa-info-circle"></i>
                        <div>
                            <strong>Draft Mode</strong>
                            <p>This workflow is in draft mode. Automation settings are disabled until you convert it to an automation.</p>
                        </div>
                        <button class="btn-promote" onclick="AutomationCanvas.promoteToAutomation('${automation.slug}')">
                            <i class="fas fa-rocket"></i> Convert to Automation
                        </button>
                    </div>
                ` : ''}

                <div class="settings-panel-content">
                    <!-- Scheduling Section -->
                    <div class="settings-section">
                        <div class="settings-section-header">
                            <i class="fas fa-calendar-alt"></i>
                            <h4>Scheduling</h4>
                        </div>
                        ${this.renderSchedulingSettings(automation, isDraft)}
                    </div>

                    <!-- Trigger Section -->
                    <div class="settings-section">
                        <div class="settings-section-header">
                            <i class="fas fa-bolt"></i>
                            <h4>Trigger</h4>
                        </div>
                        ${this.renderTriggerSettings(automation, isDraft)}
                    </div>

                    <!-- Execution Options -->
                    <div class="settings-section">
                        <div class="settings-section-header">
                            <i class="fas fa-cogs"></i>
                            <h4>Execution Options</h4>
                        </div>
                        ${this.renderExecutionSettings(automation, isDraft)}
                    </div>

                    <!-- Notifications -->
                    <div class="settings-section">
                        <div class="settings-section-header">
                            <i class="fas fa-bell"></i>
                            <h4>Notifications</h4>
                        </div>
                        ${this.renderNotificationSettings(automation, isDraft)}
                    </div>

                    <!-- Execution History -->
                    <div class="settings-section">
                        <div class="settings-section-header">
                            <i class="fas fa-history"></i>
                            <h4>Recent Executions</h4>
                        </div>
                        ${this.renderExecutionHistory(automation)}
                    </div>
                </div>

                <div class="settings-panel-footer">
                    ${AutomationSettingsSync.hasUnsavedChanges() ? `
                        <button class="btn-secondary" onclick="AutomationSettingsSync.revert()">
                            <i class="fas fa-undo"></i> Revert Changes
                        </button>
                    ` : ''}
                    <button class="btn-secondary" onclick="AutomationsSidebar.openInCanvas('${automation.slug}')">
                        <i class="fas fa-edit"></i> Edit in Canvas
                    </button>
                    <button class="btn-primary" onclick="AutomationSettingsSync.save()" ${isDraft ? 'disabled' : ''}>
                        <i class="fas fa-save"></i> Save Changes
                    </button>
                </div>
            </div>
        `;
    },

    /**
     * Render scheduling settings section
     */
    renderSchedulingSettings(automation, isDraft) {
        const schedule = automation.schedule || { type: 'manual' };

        return `
            <div class="settings-form ${isDraft ? 'settings-disabled' : ''}">
                <div class="form-group">
                    <label>Schedule Type</label>
                    <select id="schedule-type" ${isDraft ? 'disabled' : ''}
                        onchange="AutomationSettingsSync.updateSetting('schedule.type', this.value)">
                        <option value="manual" ${schedule.type === 'manual' ? 'selected' : ''}>Manual (Run on demand)</option>
                        <option value="cron" ${schedule.type === 'cron' ? 'selected' : ''}>Cron Expression</option>
                        <option value="interval" ${schedule.type === 'interval' ? 'selected' : ''}>Interval</option>
                        <option value="one-time" ${schedule.type === 'one-time' ? 'selected' : ''}>One-Time</option>
                    </select>
                </div>

                ${schedule.type === 'cron' ? `
                    <div class="form-group">
                        <label>Cron Expression</label>
                        <input type="text" id="schedule-cron" value="${schedule.cron || ''}"
                            ${isDraft ? 'disabled' : ''}
                            onchange="AutomationSettingsSync.updateSetting('schedule.cron', this.value)"
                            placeholder="0 9 * * * (Daily at 9am)">
                        <small class="form-hint">
                            Examples: <code>0 9 * * *</code> (9am daily), <code>0 */2 * * *</code> (every 2 hours)
                        </small>
                    </div>
                    <div class="form-group">
                        <label>Timezone</label>
                        <select id="schedule-timezone" ${isDraft ? 'disabled' : ''}
                            onchange="AutomationSettingsSync.updateSetting('schedule.timezone', this.value)">
                            <option value="UTC" ${schedule.timezone === 'UTC' ? 'selected' : ''}>UTC</option>
                            <option value="America/New_York" ${schedule.timezone === 'America/New_York' ? 'selected' : ''}>America/New_York</option>
                            <option value="America/Los_Angeles" ${schedule.timezone === 'America/Los_Angeles' ? 'selected' : ''}>America/Los_Angeles</option>
                            <option value="Europe/London" ${schedule.timezone === 'Europe/London' ? 'selected' : ''}>Europe/London</option>
                            <option value="Australia/Sydney" ${schedule.timezone === 'Australia/Sydney' ? 'selected' : ''}>Australia/Sydney</option>
                        </select>
                    </div>
                ` : ''}

                ${schedule.type === 'interval' ? `
                    <div class="form-group">
                        <label>Interval</label>
                        <div class="interval-input">
                            <input type="number" id="schedule-interval-value" value="${schedule.interval_value || 1}"
                                min="1" ${isDraft ? 'disabled' : ''}
                                onchange="AutomationSettingsSync.updateSetting('schedule.interval_value', parseInt(this.value))">
                            <select id="schedule-interval-unit" ${isDraft ? 'disabled' : ''}
                                onchange="AutomationSettingsSync.updateSetting('schedule.interval_unit', this.value)">
                                <option value="minutes" ${schedule.interval_unit === 'minutes' ? 'selected' : ''}>Minutes</option>
                                <option value="hours" ${schedule.interval_unit === 'hours' ? 'selected' : ''}>Hours</option>
                                <option value="days" ${schedule.interval_unit === 'days' ? 'selected' : ''}>Days</option>
                            </select>
                        </div>
                    </div>
                ` : ''}

                ${schedule.type === 'one-time' ? `
                    <div class="form-group">
                        <label>Run Date & Time</label>
                        <input type="datetime-local" id="schedule-datetime" value="${schedule.run_at || ''}"
                            ${isDraft ? 'disabled' : ''}
                            onchange="AutomationSettingsSync.updateSetting('schedule.run_at', this.value)">
                    </div>
                ` : ''}
            </div>
        `;
    },

    /**
     * Render trigger settings section
     */
    renderTriggerSettings(automation, isDraft) {
        const trigger = automation.trigger || { type: 'manual' };

        return `
            <div class="settings-form ${isDraft ? 'settings-disabled' : ''}">
                <div class="form-group">
                    <label>Trigger Type</label>
                    <select id="trigger-type" ${isDraft ? 'disabled' : ''}
                        onchange="AutomationSettingsSync.updateSetting('trigger.type', this.value)">
                        <option value="manual" ${trigger.type === 'manual' ? 'selected' : ''}>Manual</option>
                        <option value="schedule" ${trigger.type === 'schedule' ? 'selected' : ''}>Schedule</option>
                        <option value="webhook" ${trigger.type === 'webhook' ? 'selected' : ''}>Webhook</option>
                        <option value="event" ${trigger.type === 'event' ? 'selected' : ''}>Platform Event</option>
                    </select>
                </div>

                ${trigger.type === 'webhook' ? `
                    <div class="form-group">
                        <label>Webhook URL</label>
                        <div class="webhook-url-container">
                            <input type="text" class="webhook-url-input" readonly
                                value="${window.location.origin}/api/webhook/${automation.slug}" />
                            <button class="btn-copy" title="Copy webhook URL"
                                onclick="navigator.clipboard.writeText(this.previousElementSibling.value); showNotification('Webhook URL copied', 'success')">
                                <i class="fas fa-copy"></i>
                            </button>
                        </div>
                        <small class="form-hint">POST requests to this URL will trigger the automation</small>
                    </div>
                ` : ''}

                ${trigger.type === 'event' ? `
                    <div class="form-group">
                        <label>Event Type</label>
                        <select id="trigger-event" ${isDraft ? 'disabled' : ''}
                            onchange="AutomationSettingsSync.updateSetting('trigger.event_type', this.value)">
                            <option value="gmail_new_message" ${trigger.event_type === 'gmail_new_message' ? 'selected' : ''}>Gmail - New Message</option>
                            <option value="shopify_new_order" ${trigger.event_type === 'shopify_new_order' ? 'selected' : ''}>Shopify - New Order</option>
                            <option value="google_drive_new_file" ${trigger.event_type === 'google_drive_new_file' ? 'selected' : ''}>Google Drive - New File</option>
                            <option value="stripe_payment_success" ${trigger.event_type === 'stripe_payment_success' ? 'selected' : ''}>Stripe - Payment Success</option>
                        </select>
                    </div>
                ` : ''}
            </div>
        `;
    },

    /**
     * Render execution options section
     */
    renderExecutionSettings(automation, isDraft) {
        const execution = automation.execution_options || {
            retry_policy: 'none',
            max_retries: 3,
            timeout: 300,
            error_handling: 'stop',
            allow_concurrent: false
        };

        return `
            <div class="settings-form ${isDraft ? 'settings-disabled' : ''}">
                <div class="form-group">
                    <label>Retry Policy</label>
                    <select id="execution-retry-policy" ${isDraft ? 'disabled' : ''}
                        onchange="AutomationSettingsSync.updateSetting('execution_options.retry_policy', this.value)">
                        <option value="none" ${execution.retry_policy === 'none' ? 'selected' : ''}>No Retry</option>
                        <option value="exponential" ${execution.retry_policy === 'exponential' ? 'selected' : ''}>Exponential Backoff</option>
                        <option value="fixed" ${execution.retry_policy === 'fixed' ? 'selected' : ''}>Fixed Interval</option>
                    </select>
                    <small class="form-hint">Handle transient failures automatically</small>
                </div>

                ${execution.retry_policy !== 'none' ? `
                    <div class="form-group">
                        <label>Max Retries</label>
                        <input type="number" id="execution-max-retries" value="${execution.max_retries || 3}"
                            min="1" max="10" ${isDraft ? 'disabled' : ''}
                            onchange="AutomationSettingsSync.updateSetting('execution_options.max_retries', parseInt(this.value))">
                        <small class="form-hint">Maximum number of retry attempts</small>
                    </div>
                ` : ''}

                <div class="form-group">
                    <label>Timeout (seconds)</label>
                    <input type="number" id="execution-timeout" value="${execution.timeout || 300}"
                        min="10" max="3600" ${isDraft ? 'disabled' : ''}
                        onchange="AutomationSettingsSync.updateSetting('execution_options.timeout', parseInt(this.value))">
                    <small class="form-hint">Prevent infinite loops (10-3600 seconds)</small>
                </div>

                <div class="form-group">
                    <label>Error Handling</label>
                    <select id="execution-error-handling" ${isDraft ? 'disabled' : ''}
                        onchange="AutomationSettingsSync.updateSetting('execution_options.error_handling', this.value)">
                        <option value="stop" ${execution.error_handling === 'stop' ? 'selected' : ''}>Stop on First Error</option>
                        <option value="continue" ${execution.error_handling === 'continue' ? 'selected' : ''}>Continue on Error</option>
                        <option value="rollback" ${execution.error_handling === 'rollback' ? 'selected' : ''}>Rollback on Error</option>
                    </select>
                </div>

                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="execution-allow-concurrent"
                            ${execution.allow_concurrent ? 'checked' : ''}
                            ${isDraft ? 'disabled' : ''}
                            onchange="AutomationSettingsSync.updateSetting('execution_options.allow_concurrent', this.checked)">
                        <span>Allow Concurrent Executions</span>
                    </label>
                    <small class="form-hint">Allow multiple instances to run simultaneously</small>
                </div>
            </div>
        `;
    },

    /**
     * Render notification settings section
     */
    renderNotificationSettings(automation, isDraft) {
        const notifications = automation.notifications || {
            on_success: false,
            on_failure: true,
            channels: [],
            emails: '',
            daily_summary: false
        };

        return `
            <div class="settings-form ${isDraft ? 'settings-disabled' : ''}">
                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="notify-on-success"
                            ${notifications.on_success ? 'checked' : ''}
                            ${isDraft ? 'disabled' : ''}
                            onchange="AutomationSettingsSync.updateSetting('notifications.on_success', this.checked)">
                        <span>Notify on Success</span>
                    </label>
                </div>

                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="notify-on-failure"
                            ${notifications.on_failure ? 'checked' : ''}
                            ${isDraft ? 'disabled' : ''}
                            onchange="AutomationSettingsSync.updateSetting('notifications.on_failure', this.checked)">
                        <span>Notify on Failure</span>
                    </label>
                </div>

                ${(notifications.on_success || notifications.on_failure) ? `
                    <div class="form-group">
                        <label>Notification Channels</label>
                        <div class="checkbox-group">
                            <label class="checkbox-label">
                                <input type="checkbox" ${notifications.channels?.includes('email') ? 'checked' : ''}
                                    ${isDraft ? 'disabled' : ''}
                                    onchange="AutomationSettingsSync.toggleNotificationChannel('email', this.checked)">
                                <span><i class="fas fa-envelope"></i> Email</span>
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" ${notifications.channels?.includes('slack') ? 'checked' : ''}
                                    ${isDraft ? 'disabled' : ''}
                                    onchange="AutomationSettingsSync.toggleNotificationChannel('slack', this.checked)">
                                <span><i class="fab fa-slack"></i> Slack</span>
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" ${notifications.channels?.includes('webhook') ? 'checked' : ''}
                                    ${isDraft ? 'disabled' : ''}
                                    onchange="AutomationSettingsSync.toggleNotificationChannel('webhook', this.checked)">
                                <span><i class="fas fa-link"></i> Webhook</span>
                            </label>
                        </div>
                    </div>

                    ${notifications.channels?.includes('email') ? `
                        <div class="form-group">
                            <label>Email Recipients</label>
                            <input type="text" id="notify-emails" value="${notifications.emails || ''}"
                                ${isDraft ? 'disabled' : ''}
                                onchange="AutomationSettingsSync.updateSetting('notifications.emails', this.value)"
                                placeholder="user@example.com, team@example.com">
                            <small class="form-hint">Comma-separated email addresses</small>
                        </div>
                    ` : ''}
                ` : ''}

                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="notify-daily-summary"
                            ${notifications.daily_summary ? 'checked' : ''}
                            ${isDraft ? 'disabled' : ''}
                            onchange="AutomationSettingsSync.updateSetting('notifications.daily_summary', this.checked)">
                        <span>Daily Summary Report</span>
                    </label>
                    <small class="form-hint">Receive a daily summary of all executions</small>
                </div>
            </div>
        `;
    },

    /**
     * Render execution history section
     */
    renderExecutionHistory(automation) {
        // TODO: Fetch execution history from backend
        return `
            <div class="execution-history-placeholder">
                <div class="execution-stat-card">
                    <i class="fas fa-play-circle"></i>
                    <div>
                        <strong>${automation.run_count || 0}</strong>
                        <span>Total Runs</span>
                    </div>
                </div>
                <div class="execution-stat-card success">
                    <i class="fas fa-check-circle"></i>
                    <div>
                        <strong>${automation.success_count || 0}</strong>
                        <span>Successful</span>
                    </div>
                </div>
                <div class="execution-stat-card error">
                    <i class="fas fa-exclamation-circle"></i>
                    <div>
                        <strong>${automation.error_count || 0}</strong>
                        <span>Errors</span>
                    </div>
                </div>
                <div class="execution-stat-card">
                    <i class="fas fa-clock"></i>
                    <div>
                        <strong>${automation.last_run_at ? new Date(automation.last_run_at).toLocaleString() : 'Never'}</strong>
                        <span>Last Run</span>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Open automation in canvas editor
     */
    async openInCanvas(slug) {
        await this.openAutomation(slug);
        this.closeSettingsPanel();
    },

    cleanup() {
        // Unsubscribe from realtime channels when needed
        if (this.realtimeChannel) {
            this.supabaseClient.removeChannel(this.realtimeChannel);
        }
        if (this.executionsChannel) {
            this.supabaseClient.removeChannel(this.executionsChannel);
        }
        
        // Unsubscribe from settings sync
        if (this.settingsSyncUnsubscribe) {
            this.settingsSyncUnsubscribe();
            this.settingsSyncUnsubscribe = null;
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