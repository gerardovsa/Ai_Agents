/**
 * Kanban Supabase UI Components
 * 
 * Visual interface components for displaying Supabase time tracking data:
 * - Enhanced Kanban cards with time metrics
 * - Production log viewer/editor
 * - Job details modal with all Supabase data
 * - Time tracking controls
 * - Analytics dashboard integration
 * 
 * @created 2025-11-29
 * @version 1.0.0
 */

class KanbanSupabaseUI {
    constructor() {
        this.integration = window.KanbanSupabaseIntegration;
        this.initialized = false;
    }

    /**
     * Initialize UI components
     */
    async initialize() {
        if (this.initialized) return;
        
        // Ensure integration is ready
        if (!this.integration) {
            console.warn('⚠️ KanbanSupabaseIntegration not loaded');
            return false;
        }
        
        await this.integration.initialize();
        this.initialized = true;
        
        console.log('✅ Kanban Supabase UI initialized');
        return true;
    }

    /**
     * Enhance Kanban card with time metrics badge
     * @param {HTMLElement} cardElement - Card DOM element
     * @param {number} ticketId - Job ticket ID
     */
    async enhanceCard(cardElement, ticketId) {
        if (!this.initialized) return;
        
        try {
            const metrics = await this.integration.getJobTimeMetrics(ticketId);
            
            if (!metrics) return;
            
            // Create metrics badge
            const metricsBadge = document.createElement('div');
            metricsBadge.className = 'supabase-metrics-badge';
            metricsBadge.innerHTML = `
                <div class="metrics-badge-content">
                    ${this._renderTimeMetricsBadge(metrics)}
                </div>
            `;
            
            // Insert after card-stage-time section
            const stageTimeSection = cardElement.querySelector('.card-stage-time');
            if (stageTimeSection) {
                stageTimeSection.after(metricsBadge);
            } else {
                cardElement.appendChild(metricsBadge);
            }
            
        } catch (error) {
            console.error(`❌ Failed to enhance card ${ticketId}:`, error);
        }
    }

    /**
     * Render time metrics badge HTML
     * @private
     */
    _renderTimeMetricsBadge(metrics) {
        const currentStageHours = metrics.current_stage_hours !== null 
            ? metrics.current_stage_hours.toFixed(1) 
            : '-';
        
        const totalHours = metrics.total_hours !== null 
            ? metrics.total_hours.toFixed(1) 
            : '-';
        
        const transitions = metrics.total_transitions || 0;
        
        return `
            <div style="display: flex; gap: 12px; padding: 8px 12px; background: rgba(59, 130, 246, 0.1); border-radius: 4px; font-size: 11px;">
                <span style="color: #60a5fa;" title="Time in current stage">
                    <i class="fas fa-hourglass-half"></i> ${currentStageHours}h
                </span>
                <span style="color: #34d399;" title="Total time in system">
                    <i class="fas fa-clock"></i> ${totalHours}h
                </span>
                <span style="color: #fbbf24;" title="Stage transitions">
                    <i class="fas fa-exchange-alt"></i> ${transitions}
                </span>
            </div>
        `;
    }

    /**
     * Show job details modal with full Supabase data
     * @param {number} ticketId - Job ticket ID
     * @param {Object} job - Job data from SQL Server
     */
    async showJobDetailsModal(ticketId, job) {
        if (!this.initialized) {
            await this.initialize();
        }
        
        // Fetch all Supabase data
        const [metrics, productionLog] = await Promise.all([
            this.integration.getJobTimeMetrics(ticketId),
            this.integration.getJobProductionLog(ticketId)
        ]);
        
        // Create modal
        const modal = document.createElement('div');
        modal.className = 'supabase-job-modal';
        modal.id = `job-modal-${ticketId}`;
        
        modal.innerHTML = `
            <div class="modal-backdrop" onclick="this.parentElement.remove()"></div>
            <div class="modal-container">
                <div class="modal-header">
                    <h3>
                        <i class="fas fa-file-alt"></i> Job Details - ${ticketId}
                    </h3>
                    <button class="modal-close-btn" onclick="this.closest('.supabase-job-modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="modal-body">
                    <!-- Job Info Section -->
                    ${this._renderJobInfoSection(job)}
                    
                    <!-- Time Metrics Section -->
                    ${this._renderTimeMetricsSection(metrics)}
                    
                    <!-- Production Log Section -->
                    ${this._renderProductionLogSection(productionLog, ticketId)}
                    
                    <!-- Time Tracking Controls -->
                    ${this._renderTimeTrackingControls(ticketId)}
                    
                    <!-- Performance Metrics Form -->
                    ${this._renderPerformanceForm(ticketId)}
                </div>
                
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.supabase-job-modal').remove()">
                        Close
                    </button>
                </div>
            </div>
        `;
        
        // Add modal styles
        this._injectModalStyles();
        
        // Append to body
        document.body.appendChild(modal);
        
        // Setup event listeners
        this._setupModalEventListeners(modal, ticketId);
    }

    /**
     * Render job info section
     * @private
     */
    _renderJobInfoSection(job) {
        return `
            <section class="modal-section">
                <h4><i class="fas fa-info-circle"></i> Job Information</h4>
                <div class="info-grid">
                    <div class="info-item">
                        <label>Client:</label>
                        <span>${job.ClientName || '-'}</span>
                    </div>
                    <div class="info-item">
                        <label>Order ID:</label>
                        <span>${job.OrderID || '-'}</span>
                    </div>
                    <div class="info-item">
                        <label>Description:</label>
                        <span>${job.ShortJobDesc || '-'}</span>
                    </div>
                    <div class="info-item">
                        <label>Stage:</label>
                        <span>${job.StageDescription || '-'}</span>
                    </div>
                    <div class="info-item">
                        <label>Quantity:</label>
                        <span>${job.Qty || '-'}</span>
                    </div>
                    <div class="info-item">
                        <label>Cost:</label>
                        <span>$${job.Cost ? job.Cost.toFixed(2) : '-'}</span>
                    </div>
                    <div class="info-item">
                        <label>Priority:</label>
                        <span class="priority-badge priority-${job.Priority || 5}">${job.PriorityLabel || 'Normal'}</span>
                    </div>
                    <div class="info-item">
                        <label>Days in System:</label>
                        <span>${job.DaysInSystem || 0} days</span>
                    </div>
                </div>
            </section>
        `;
    }

    /**
     * Render time metrics section
     * @private
     */
    _renderTimeMetricsSection(metrics) {
        if (!metrics) {
            return `
                <section class="modal-section">
                    <h4><i class="fas fa-clock"></i> Time Metrics</h4>
                    <p style="color: #9ca3af;">No time tracking data available yet.</p>
                </section>
            `;
        }
        
        const currentStageHours = metrics.current_stage_hours !== null 
            ? metrics.current_stage_hours.toFixed(2) 
            : 'N/A';
        
        const totalHours = metrics.total_hours !== null 
            ? metrics.total_hours.toFixed(2) 
            : 'N/A';
        
        const businessHours = metrics.total_business_hours !== null 
            ? metrics.total_business_hours.toFixed(2) 
            : 'N/A';
        
        return `
            <section class="modal-section">
                <h4><i class="fas fa-clock"></i> Time Metrics</h4>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-icon" style="background: rgba(59, 130, 246, 0.2); color: #3b82f6;">
                            <i class="fas fa-hourglass-half"></i>
                        </div>
                        <div class="metric-info">
                            <label>Current Stage</label>
                            <span class="metric-value">${currentStageHours}h</span>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon" style="background: rgba(16, 185, 129, 0.2); color: #10b981;">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="metric-info">
                            <label>Total Time</label>
                            <span class="metric-value">${totalHours}h</span>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon" style="background: rgba(251, 191, 36, 0.2); color: #fbbf24;">
                            <i class="fas fa-business-time"></i>
                        </div>
                        <div class="metric-info">
                            <label>Business Hours</label>
                            <span class="metric-value">${businessHours}h</span>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon" style="background: rgba(168, 85, 247, 0.2); color: #a855f7;">
                            <i class="fas fa-exchange-alt"></i>
                        </div>
                        <div class="metric-info">
                            <label>Transitions</label>
                            <span class="metric-value">${metrics.total_transitions || 0}</span>
                        </div>
                    </div>
                </div>
            </section>
        `;
    }

    /**
     * Render production log section
     * @private
     */
    _renderProductionLogSection(productionLog, ticketId) {
        const logEntries = productionLog && productionLog.length > 0
            ? productionLog.map(entry => this._renderLogEntry(entry)).join('')
            : '<p style="color: #9ca3af; padding: 12px;">No production log entries yet.</p>';
        
        return `
            <section class="modal-section">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <h4><i class="fas fa-clipboard-list"></i> Production Log</h4>
                    <button class="btn btn-sm btn-primary" onclick="window.kanbanSupabaseUI.showAddLogEntryForm(${ticketId})">
                        <i class="fas fa-plus"></i> Add Entry
                    </button>
                </div>
                
                <div class="production-log-list" id="production-log-list-${ticketId}">
                    ${logEntries}
                </div>
            </section>
        `;
    }

    /**
     * Render single log entry
     * @private
     */
    _renderLogEntry(entry) {
        const date = new Date(entry.created_at);
        const formattedDate = date.toLocaleString();
        
        const typeIcons = {
            'note': 'fas fa-sticky-note',
            'wastage': 'fas fa-trash-alt',
            'stock_change': 'fas fa-boxes',
            'delay': 'fas fa-clock',
            'notification': 'fas fa-bell',
            'time_tracking': 'fas fa-stopwatch'
        };
        
        const typeColors = {
            'note': '#60a5fa',
            'wastage': '#ef4444',
            'stock_change': '#fbbf24',
            'delay': '#f97316',
            'notification': '#8b5cf6',
            'time_tracking': '#10b981'
        };
        
        const icon = typeIcons[entry.entry_type] || 'fas fa-file-alt';
        const color = typeColors[entry.entry_type] || '#9ca3af';
        
        return `
            <div class="log-entry">
                <div class="log-entry-icon" style="color: ${color};">
                    <i class="${icon}"></i>
                </div>
                <div class="log-entry-content">
                    <div class="log-entry-header">
                        <span class="log-entry-type" style="color: ${color};">${entry.entry_type}</span>
                        <span class="log-entry-time">${formattedDate}</span>
                    </div>
                    <div class="log-entry-text">${entry.note_text || ''}</div>
                    ${entry.created_by_user ? `<div class="log-entry-user">by ${entry.created_by_user}</div>` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Render time tracking controls
     * @private
     */
    _renderTimeTrackingControls(ticketId) {
        const hasActiveTimer = this.integration.getJobTimer(ticketId) !== null;
        
        return `
            <section class="modal-section">
                <h4><i class="fas fa-stopwatch"></i> Time Tracking</h4>
                <div class="time-tracking-controls" id="time-tracking-${ticketId}">
                    ${hasActiveTimer ? `
                        <button class="btn btn-danger btn-block" onclick="window.kanbanSupabaseUI.stopTimer(${ticketId})">
                            <i class="fas fa-stop"></i> Stop Timer
                        </button>
                        <p style="color: #10b981; margin-top: 8px; text-align: center;">
                            <i class="fas fa-circle" style="animation: pulse 2s infinite;"></i> Timer running...
                        </p>
                    ` : `
                        <button class="btn btn-success btn-block" onclick="window.kanbanSupabaseUI.startTimer(${ticketId})">
                            <i class="fas fa-play"></i> Start Timer
                        </button>
                    `}
                </div>
            </section>
        `;
    }

    /**
     * Render performance metrics form
     * @private
     */
    _renderPerformanceForm(ticketId) {
        return `
            <section class="modal-section">
                <h4><i class="fas fa-chart-bar"></i> Performance Metrics</h4>
                <form class="performance-form" id="performance-form-${ticketId}" onsubmit="event.preventDefault(); window.kanbanSupabaseUI.submitPerformance(${ticketId});">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Estimated Hours</label>
                            <input type="number" step="0.1" name="estimated_hours" class="form-control" placeholder="0.0">
                        </div>
                        <div class="form-group">
                            <label>Actual Hours</label>
                            <input type="number" step="0.1" name="actual_hours" class="form-control" placeholder="0.0">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Quality Score (0-100)</label>
                            <input type="number" min="0" max="100" name="quality_score" class="form-control" placeholder="95">
                        </div>
                        <div class="form-group">
                            <label>Rework Hours</label>
                            <input type="number" step="0.1" name="rework_hours" class="form-control" placeholder="0.0">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Material Cost ($)</label>
                            <input type="number" step="0.01" name="material_cost" class="form-control" placeholder="0.00">
                        </div>
                        <div class="form-group">
                            <label>Labor Cost ($)</label>
                            <input type="number" step="0.01" name="labor_cost" class="form-control" placeholder="0.00">
                        </div>
                    </div>
                    
                    <button type="submit" class="btn btn-primary btn-block">
                        <i class="fas fa-save"></i> Save Performance Metrics
                    </button>
                </form>
            </section>
        `;
    }

    /**
     * Setup modal event listeners
     * @private
     */
    _setupModalEventListeners(modal, ticketId) {
        // Close on backdrop click
        modal.querySelector('.modal-backdrop').addEventListener('click', () => {
            modal.remove();
        });
        
        // Close on Escape key
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
    }

    /**
     * Show add log entry form
     */
    async showAddLogEntryForm(ticketId) {
        const formHtml = `
            <div class="log-entry-form" style="background: #1f2937; padding: 16px; border-radius: 6px; margin-top: 12px;">
                <h5 style="color: #f3f4f6; margin: 0 0 12px 0;">Add Production Log Entry</h5>
                <form onsubmit="event.preventDefault(); window.kanbanSupabaseUI.submitLogEntry(${ticketId});" id="log-entry-form-${ticketId}">
                    <div class="form-group">
                        <label>Entry Type</label>
                        <select name="entry_type" class="form-control" required>
                            <option value="note">Note</option>
                            <option value="wastage">Wastage</option>
                            <option value="stock_change">Stock Change</option>
                            <option value="delay">Delay</option>
                            <option value="notification">Notification</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Description</label>
                        <textarea name="note_text" class="form-control" rows="3" required placeholder="Enter details..."></textarea>
                    </div>
                    
                    <div class="form-row">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-plus"></i> Add Entry
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="this.closest('.log-entry-form').remove()">
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        const logList = document.getElementById(`production-log-list-${ticketId}`);
        if (logList) {
            const existingForm = logList.querySelector('.log-entry-form');
            if (existingForm) {
                existingForm.remove();
            }
            logList.insertAdjacentHTML('beforeend', formHtml);
        }
    }

    /**
     * Submit log entry
     */
    async submitLogEntry(ticketId) {
        const form = document.getElementById(`log-entry-form-${ticketId}`);
        if (!form) return;
        
        const formData = new FormData(form);
        
        const entry = {
            ticket_id: ticketId,
            entry_type: formData.get('entry_type'),
            note_text: formData.get('note_text'),
            created_by_user: window.currentUserInitials || 'USER'
        };
        
        const result = await this.integration.addProductionLogEntry(entry);
        
        if (result && result.success) {
            console.log('✅ Log entry added');
            // Refresh log list
            const productionLog = await this.integration.getJobProductionLog(ticketId);
            const logList = document.getElementById(`production-log-list-${ticketId}`);
            if (logList) {
                const logEntries = productionLog.map(e => this._renderLogEntry(e)).join('');
                logList.innerHTML = logEntries;
            }
            form.closest('.log-entry-form').remove();
        } else {
            alert('Failed to add log entry');
        }
    }

    /**
     * Start timer for job
     */
    async startTimer(ticketId) {
        const job = window.inhouseKanbanModule?.jobs?.find(j => j.TicketID === ticketId);
        const stageId = job?.StageID || 1;
        
        this.integration.startJobTimer(ticketId, stageId);
        
        // Refresh time tracking controls
        const controls = document.getElementById(`time-tracking-${ticketId}`);
        if (controls) {
            controls.innerHTML = `
                <button class="btn btn-danger btn-block" onclick="window.kanbanSupabaseUI.stopTimer(${ticketId})">
                    <i class="fas fa-stop"></i> Stop Timer
                </button>
                <p style="color: #10b981; margin-top: 8px; text-align: center;">
                    <i class="fas fa-circle" style="animation: pulse 2s infinite;"></i> Timer running...
                </p>
            `;
        }
        
        console.log(`⏱️ Timer started for job ${ticketId}`);
    }

    /**
     * Stop timer for job
     */
    async stopTimer(ticketId) {
        const result = await this.integration.stopJobTimer(ticketId, 'Work session complete');
        
        if (result) {
            console.log(`⏱️ Timer stopped: ${result.duration_hours.toFixed(2)} hours`);
            
            // Refresh time tracking controls
            const controls = document.getElementById(`time-tracking-${ticketId}`);
            if (controls) {
                controls.innerHTML = `
                    <button class="btn btn-success btn-block" onclick="window.kanbanSupabaseUI.startTimer(${ticketId})">
                        <i class="fas fa-play"></i> Start Timer
                    </button>
                    <p style="color: #10b981; margin-top: 8px; text-align: center;">
                        Last session: ${result.duration_hours.toFixed(2)}h (${result.duration_minutes} min)
                    </p>
                `;
            }
            
            // Refresh metrics
            const metrics = await this.integration.getJobTimeMetrics(ticketId);
            // Update metrics section if modal is still open
        }
    }

    /**
     * Submit performance metrics
     */
    async submitPerformance(ticketId) {
        const form = document.getElementById(`performance-form-${ticketId}`);
        if (!form) return;
        
        const formData = new FormData(form);
        
        const performance = {
            ticket_id: ticketId,
            estimated_hours: parseFloat(formData.get('estimated_hours')) || null,
            actual_hours: parseFloat(formData.get('actual_hours')) || null,
            quality_score: parseFloat(formData.get('quality_score')) || null,
            rework_hours: parseFloat(formData.get('rework_hours')) || null,
            material_cost: parseFloat(formData.get('material_cost')) || null,
            labor_cost: parseFloat(formData.get('labor_cost')) || null
        };
        
        // Calculate total cost and profit margin
        if (performance.material_cost && performance.labor_cost) {
            performance.total_cost = performance.material_cost + performance.labor_cost;
        }
        
        const result = await this.integration.recordJobPerformance(performance);
        
        if (result && result.success) {
            console.log('✅ Performance metrics saved');
            alert('Performance metrics saved successfully!');
            form.reset();
        } else {
            alert('Failed to save performance metrics');
        }
    }

    /**
     * Inject modal styles
     * @private
     */
    _injectModalStyles() {
        if (document.getElementById('supabase-modal-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'supabase-modal-styles';
        styles.textContent = `
            .supabase-job-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .modal-backdrop {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.7);
                backdrop-filter: blur(4px);
            }
            
            .modal-container {
                position: relative;
                background: #161b22;
                border: 1px solid #30363d;
                border-radius: 12px;
                max-width: 900px;
                max-height: 90vh;
                width: 90%;
                display: flex;
                flex-direction: column;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            }
            
            .modal-header {
                padding: 20px 24px;
                border-bottom: 1px solid #30363d;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .modal-header h3 {
                color: #f3f4f6;
                margin: 0;
                font-size: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .modal-close-btn {
                background: none;
                border: none;
                color: #9ca3af;
                font-size: 20px;
                cursor: pointer;
                padding: 4px 8px;
                border-radius: 4px;
                transition: all 0.2s;
            }
            
            .modal-close-btn:hover {
                background: #30363d;
                color: #f3f4f6;
            }
            
            .modal-body {
                padding: 24px;
                overflow-y: auto;
                flex: 1;
            }
            
            .modal-section {
                margin-bottom: 32px;
            }
            
            .modal-section h4 {
                color: #f3f4f6;
                font-size: 16px;
                margin: 0 0 16px 0;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .info-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 12px;
            }
            
            .info-item {
                display: flex;
                flex-direction: column;
                gap: 4px;
            }
            
            .info-item label {
                color: #9ca3af;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .info-item span {
                color: #f3f4f6;
                font-size: 14px;
            }
            
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 12px;
            }
            
            .metric-card {
                background: #0d1117;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 16px;
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .metric-icon {
                width: 48px;
                height: 48px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
            }
            
            .metric-info {
                display: flex;
                flex-direction: column;
                gap: 4px;
            }
            
            .metric-info label {
                color: #9ca3af;
                font-size: 11px;
                font-weight: 600;
            }
            
            .metric-value {
                color: #f3f4f6;
                font-size: 18px;
                font-weight: 700;
            }
            
            .production-log-list {
                max-height: 300px;
                overflow-y: auto;
            }
            
            .log-entry {
                display: flex;
                gap: 12px;
                padding: 12px;
                background: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                margin-bottom: 8px;
            }
            
            .log-entry-icon {
                font-size: 18px;
                width: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .log-entry-content {
                flex: 1;
            }
            
            .log-entry-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 6px;
            }
            
            .log-entry-type {
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
            }
            
            .log-entry-time {
                color: #9ca3af;
                font-size: 11px;
            }
            
            .log-entry-text {
                color: #f3f4f6;
                font-size: 13px;
                margin-bottom: 4px;
            }
            
            .log-entry-user {
                color: #9ca3af;
                font-size: 11px;
                font-style: italic;
            }
            
            .time-tracking-controls {
                text-align: center;
            }
            
            .performance-form .form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
                margin-bottom: 12px;
            }
            
            .performance-form .form-group {
                display: flex;
                flex-direction: column;
                gap: 6px;
            }
            
            .performance-form label {
                color: #9ca3af;
                font-size: 12px;
                font-weight: 600;
            }
            
            .form-control {
                background: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px 12px;
                color: #f3f4f6;
                font-size: 14px;
            }
            
            .form-control:focus {
                outline: none;
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            .btn {
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                display: inline-flex;
                align-items: center;
                gap: 6px;
            }
            
            .btn-primary {
                background: #3b82f6;
                color: white;
            }
            
            .btn-primary:hover {
                background: #2563eb;
            }
            
            .btn-secondary {
                background: #4b5563;
                color: white;
            }
            
            .btn-secondary:hover {
                background: #374151;
            }
            
            .btn-success {
                background: #10b981;
                color: white;
            }
            
            .btn-success:hover {
                background: #059669;
            }
            
            .btn-danger {
                background: #ef4444;
                color: white;
            }
            
            .btn-danger:hover {
                background: #dc2626;
            }
            
            .btn-block {
                width: 100%;
                justify-content: center;
            }
            
            .btn-sm {
                padding: 6px 12px;
                font-size: 12px;
            }
            
            .modal-footer {
                padding: 16px 24px;
                border-top: 1px solid #30363d;
                display: flex;
                justify-content: flex-end;
                gap: 12px;
            }
            
            .priority-badge {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 600;
            }
            
            .priority-1, .priority-2 {
                background: #ef4444;
                color: white;
            }
            
            .priority-3, .priority-4 {
                background: #f97316;
                color: white;
            }
            
            .priority-5, .priority-6 {
                background: #fbbf24;
                color: #1f2937;
            }
            
            .priority-7, .priority-8 {
                background: #10b981;
                color: white;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
        `;
        
        document.head.appendChild(styles);
    }

    /**
     * Render analytics tab content for sidebar
     * @param {HTMLElement} container - Analytics tab container
     */
    async renderAnalyticsTab(container) {
        if (!this.initialized) {
            await this.initialize();
        }
        
        container.innerHTML = `
            <div class="analytics-tab-content">
                <div class="analytics-header">
                    <h4><i class="fas fa-chart-line"></i> Time Tracking Analytics</h4>
                    <button class="btn btn-sm btn-primary" onclick="window.kanbanSupabaseUI.refreshAnalytics()">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                </div>
                
                <div id="analytics-summary-cards" class="analytics-summary">
                    Loading analytics...
                </div>
            </div>
        `;
        
        // Load and display analytics
        this.refreshAnalytics();
    }

    /**
     * Refresh analytics display
     */
    async refreshAnalytics() {
        // This would aggregate metrics across all jobs
        // For now, show placeholder
        const summaryContainer = document.getElementById('analytics-summary-cards');
        if (summaryContainer) {
            summaryContainer.innerHTML = `
                <p style="color: #9ca3af; padding: 20px; text-align: center;">
                    Analytics dashboard coming soon...
                </p>
            `;
        }
    }
}

// Export singleton instance
window.kanbanSupabaseUI = new KanbanSupabaseUI();

console.log('✅ Kanban Supabase UI components loaded');
