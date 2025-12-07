// BaseModule polyfill (required since module-base.js is not globally loaded)
class BaseModule {
    constructor(moduleId) {
        this.moduleId = moduleId;
        this.manifest = null;
        this.backendUrl = window.API_BASE_URL || 'http://localhost:5001';
        console.log(` BaseModule constructor - moduleId: ${moduleId}`);
    }

    async initialize() {
        console.log(` BaseModule.initialize() called for ${this.moduleId}`);
        try {
            const response = await fetch(`${this.backendUrl}/api/modules/${this.moduleId}`);
            if (response.ok) {
                this.manifest = await response.json();
                console.log(` Manifest loaded for ${this.moduleId}:`, this.manifest);
            }
        } catch (error) {
            console.warn(` Failed to load manifest for ${this.moduleId}:`, error);
        }
    }
}
/**
 * Render Management Module
 * 
 * Provides comprehensive Render cloud management:
 * - Service inventory and status
 * - Deployment management
 * - Real-time logs viewer
 * - Metrics visualization
 * - Database management
 */

class RenderManagementModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);
        this.services = [];
        this.deploys = [];
        this.selectedService = null;
        this.refreshInterval = null;
        this.logUpdateInterval = null;
    }

    async initialize() {
        await super.initialize();
        console.log('🔧 Initializing Render Management module...');
        await this.loadServices();
        console.log('✅ Render Management module initialized');
    }

    initializeSubTabs() {
        this.initializeServicesTab();
        this.initializeDeploymentsTab();
        this.initializeLogsTab();
        this.initializeMetricsTab();
        this.initializeDatabasesTab();
    }

    // ===== SERVICES TAB =====
    initializeServicesTab() {
        const container = this.getSubTabContainer('services');
        const primaryColor = this.getPrimaryColor();

        container.innerHTML = `
            <div class="render-services-container">
                <!-- Header -->
                <div class="module-header" style="border-bottom: 2px solid ${primaryColor};">
                    <h2><i class="fas fa-server"></i> Render Services</h2>
                    <button id="refresh-services-btn" class="btn-primary">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                </div>

                <!-- Filter Bar -->
                <div class="filter-bar">
                    <input type="text" id="service-search" placeholder="Search services..." class="search-input">
                    <select id="service-type-filter" class="filter-select">
                        <option value="">All Types</option>
                        <option value="web_service">Web Services</option>
                        <option value="private_service">Private Services</option>
                        <option value="background_worker">Workers</option>
                        <option value="cron_job">Cron Jobs</option>
                    </select>
                    <select id="service-status-filter" class="filter-select">
                        <option value="">All Status</option>
                        <option value="live">Live</option>
                        <option value="suspended">Suspended</option>
                        <option value="failed">Failed</option>
                    </select>
                </div>

                <!-- Services Grid -->
                <div id="services-grid" class="services-grid">
                    <div class="loading-spinner">
                        <i class="fas fa-spinner fa-spin"></i>
                        <p>Loading services...</p>
                    </div>
                </div>
            </div>
        `;

        // Attach event listeners
        document.getElementById('refresh-services-btn').addEventListener('click', () => {
            this.loadServices();
        });

        document.getElementById('service-search').addEventListener('input', (e) => {
            this.filterServices();
        });

        document.getElementById('service-type-filter').addEventListener('change', () => {
            this.filterServices();
        });

        document.getElementById('service-status-filter').addEventListener('change', () => {
            this.filterServices();
        });
    }

    async loadServices() {
        try {
            const response = await fetch('/api/render/services');
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Failed to load services');
            }

            this.services = result.data || [];
            this.renderServices();
        } catch (error) {
            console.error('❌ Failed to load services:', error);
            this.showError('services-grid', 'Failed to load services. Ensure Render CLI is configured.');
        }
    }

    renderServices() {
        const grid = document.getElementById('services-grid');
        const filteredServices = this.getFilteredServices();

        if (filteredServices.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-server" style="font-size: 48px; color: var(--text-secondary);"></i>
                    <p>No services found</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = filteredServices.map(service => this.createServiceCard(service)).join('');

        // Attach action listeners
        filteredServices.forEach(service => {
            const card = document.getElementById(`service-${service.service_id}`);
            
            card.querySelector('.deploy-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                this.deployService(service.service_id);
            });

            card.querySelector('.logs-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                this.viewLogs(service.service_id);
            });

            card.querySelector('.restart-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                this.restartService(service.service_id);
            });
        });
    }

    createServiceCard(service) {
        const primaryColor = this.getPrimaryColor();
        const statusColor = this.getStatusColor(service.status);
        const statusIcon = this.getStatusIcon(service.status);
        const typeIcon = this.getTypeIcon(service.type);

        return `
            <div id="service-${service.service_id}" class="service-card" style="border-color: ${primaryColor};">
                <div class="service-header">
                    <div class="service-title">
                        <i class="${typeIcon}"></i>
                        <h3>${service.name}</h3>
                    </div>
                    <span class="status-badge" style="background: ${statusColor};">
                        <i class="${statusIcon}"></i> ${service.status}
                    </span>
                </div>

                <div class="service-info">
                    <div class="info-item">
                        <i class="fas fa-tag"></i>
                        <span>${service.type.replace('_', ' ')}</span>
                    </div>
                    ${service.url ? `
                        <div class="info-item">
                            <i class="fas fa-link"></i>
                            <a href="${service.url}" target="_blank">${service.url}</a>
                        </div>
                    ` : ''}
                    <div class="info-item">
                        <i class="fas fa-clock"></i>
                        <span>Updated: ${this.formatDate(service.updated_at)}</span>
                    </div>
                </div>

                <div class="service-actions">
                    <button class="deploy-btn" style="background: ${primaryColor};">
                        <i class="fas fa-rocket"></i> Deploy
                    </button>
                    <button class="logs-btn" style="background: var(--accent-secondary);">
                        <i class="fas fa-file-alt"></i> Logs
                    </button>
                    <button class="restart-btn" style="background: var(--warning);">
                        <i class="fas fa-redo"></i> Restart
                    </button>
                </div>
            </div>
        `;
    }

    getFilteredServices() {
        const search = document.getElementById('service-search').value.toLowerCase();
        const typeFilter = document.getElementById('service-type-filter').value;
        const statusFilter = document.getElementById('service-status-filter').value;

        return this.services.filter(service => {
            const matchesSearch = service.name.toLowerCase().includes(search);
            const matchesType = !typeFilter || service.type === typeFilter;
            const matchesStatus = !statusFilter || service.status === statusFilter;
            return matchesSearch && matchesType && matchesStatus;
        });
    }

    filterServices() {
        this.renderServices();
    }

    // ===== DEPLOYMENTS TAB =====
    initializeDeploymentsTab() {
        const container = this.getSubTabContainer('deployments');
        const primaryColor = this.getPrimaryColor();

        container.innerHTML = `
            <div class="render-deployments-container">
                <div class="module-header" style="border-bottom: 2px solid ${primaryColor};">
                    <h2><i class="fas fa-rocket"></i> Deployments</h2>
                    <select id="deploy-service-select" class="service-select">
                        <option value="">Select a service...</option>
                    </select>
                </div>

                <div id="deployments-list" class="deployments-list">
                    <div class="empty-state">
                        <i class="fas fa-rocket" style="font-size: 48px;"></i>
                        <p>Select a service to view deployments</p>
                    </div>
                </div>
            </div>
        `;

        // Populate service selector
        this.populateServiceSelect('deploy-service-select');

        document.getElementById('deploy-service-select').addEventListener('change', (e) => {
            this.loadDeployments(e.target.value);
        });
    }

    async loadDeployments(serviceId) {
        if (!serviceId) return;

        const listContainer = document.getElementById('deployments-list');
        listContainer.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i><p>Loading deployments...</p></div>';

        try {
            const response = await fetch(`/api/render/deploys?service_id=${serviceId}&limit=20`);
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error);
            }

            this.deploys = result.data || [];
            this.renderDeployments();
        } catch (error) {
            console.error('❌ Failed to load deployments:', error);
            this.showError('deployments-list', 'Failed to load deployments');
        }
    }

    renderDeployments() {
        const listContainer = document.getElementById('deployments-list');

        if (this.deploys.length === 0) {
            listContainer.innerHTML = '<div class="empty-state"><i class="fas fa-rocket"></i><p>No deployments found</p></div>';
            return;
        }

        listContainer.innerHTML = this.deploys.map(deploy => this.createDeploymentItem(deploy)).join('');
    }

    createDeploymentItem(deploy) {
        const statusColor = this.getStatusColor(deploy.status);
        const statusIcon = this.getStatusIcon(deploy.status);
        const duration = this.calculateDuration(deploy.created_at, deploy.finished_at);

        return `
            <div class="deployment-item">
                <div class="deployment-header">
                    <span class="status-badge" style="background: ${statusColor};">
                        <i class="${statusIcon}"></i> ${deploy.status}
                    </span>
                    <span class="deploy-id">#${deploy.deploy_id}</span>
                </div>
                <div class="deployment-info">
                    ${deploy.commit ? `
                        <div class="info-item">
                            <i class="fas fa-code-branch"></i>
                            <span>${deploy.commit.substring(0, 7)}</span>
                        </div>
                    ` : ''}
                    ${deploy.commit_message ? `
                        <div class="commit-message">${deploy.commit_message}</div>
                    ` : ''}
                    <div class="info-item">
                        <i class="fas fa-clock"></i>
                        <span>${this.formatDate(deploy.created_at)}</span>
                    </div>
                    ${duration ? `
                        <div class="info-item">
                            <i class="fas fa-hourglass-half"></i>
                            <span>${duration}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    // ===== LOGS TAB =====
    initializeLogsTab() {
        const container = this.getSubTabContainer('logs');
        const primaryColor = this.getPrimaryColor();

        container.innerHTML = `
            <div class="render-logs-container">
                <div class="module-header" style="border-bottom: 2px solid ${primaryColor};">
                    <h2><i class="fas fa-file-alt"></i> Service Logs</h2>
                    <div class="logs-controls">
                        <select id="logs-service-select" class="service-select">
                            <option value="">Select a service...</option>
                        </select>
                        <input type="text" id="logs-filter" placeholder="Filter logs..." class="search-input">
                        <button id="refresh-logs-btn" class="btn-primary">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                        <button id="auto-refresh-logs-btn" class="btn-secondary">
                            <i class="fas fa-clock"></i> Auto-Refresh: OFF
                        </button>
                    </div>
                </div>

                <div id="logs-viewer" class="logs-viewer">
                    <div class="empty-state">
                        <i class="fas fa-file-alt" style="font-size: 48px;"></i>
                        <p>Select a service to view logs</p>
                    </div>
                </div>
            </div>
        `;

        this.populateServiceSelect('logs-service-select');

        document.getElementById('logs-service-select').addEventListener('change', (e) => {
            this.loadLogs(e.target.value);
        });

        document.getElementById('refresh-logs-btn').addEventListener('click', () => {
            const serviceId = document.getElementById('logs-service-select').value;
            if (serviceId) this.loadLogs(serviceId);
        });

        document.getElementById('auto-refresh-logs-btn').addEventListener('click', (e) => {
            this.toggleAutoRefreshLogs(e.target);
        });

        document.getElementById('logs-filter').addEventListener('input', () => {
            this.filterLogs();
        });
    }

    async loadLogs(serviceId) {
        if (!serviceId) return;

        const viewer = document.getElementById('logs-viewer');
        viewer.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i><p>Loading logs...</p></div>';

        try {
            const response = await fetch(`/api/render/logs?service_id=${serviceId}&tail=100`);
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error);
            }

            this.selectedService = serviceId;
            this.renderLogs(result.data || []);
        } catch (error) {
            console.error('❌ Failed to load logs:', error);
            this.showError('logs-viewer', 'Failed to load logs');
        }
    }

    renderLogs(logs) {
        const viewer = document.getElementById('logs-viewer');
        const filter = document.getElementById('logs-filter').value.toLowerCase();

        const filteredLogs = filter 
            ? logs.filter(log => log.message && log.message.toLowerCase().includes(filter))
            : logs;

        if (filteredLogs.length === 0) {
            viewer.innerHTML = '<div class="empty-state"><i class="fas fa-file-alt"></i><p>No logs found</p></div>';
            return;
        }

        viewer.innerHTML = `
            <div class="logs-content">
                ${filteredLogs.map(log => `
                    <div class="log-entry ${log.level || 'info'}">
                        <span class="log-timestamp">${this.formatDate(log.timestamp)}</span>
                        <span class="log-level">[${log.level || 'INFO'}]</span>
                        <span class="log-message">${this.escapeHtml(log.message || log.toString())}</span>
                    </div>
                `).join('')}
            </div>
        `;

        // Auto-scroll to bottom
        viewer.scrollTop = viewer.scrollHeight;
    }

    filterLogs() {
        // Re-render with current logs (filtered)
        if (this.selectedService) {
            this.loadLogs(this.selectedService);
        }
    }

    toggleAutoRefreshLogs(button) {
        if (this.logUpdateInterval) {
            clearInterval(this.logUpdateInterval);
            this.logUpdateInterval = null;
            button.innerHTML = '<i class="fas fa-clock"></i> Auto-Refresh: OFF';
            button.classList.remove('active');
        } else {
            this.logUpdateInterval = setInterval(() => {
                const serviceId = document.getElementById('logs-service-select').value;
                if (serviceId) this.loadLogs(serviceId);
            }, 5000); // 5 seconds
            button.innerHTML = '<i class="fas fa-clock"></i> Auto-Refresh: ON';
            button.classList.add('active');
        }
    }

    // ===== METRICS TAB =====
    initializeMetricsTab() {
        const container = this.getSubTabContainer('metrics');
        const primaryColor = this.getPrimaryColor();

        container.innerHTML = `
            <div class="render-metrics-container">
                <div class="module-header" style="border-bottom: 2px solid ${primaryColor};">
                    <h2><i class="fas fa-chart-line"></i> Service Metrics</h2>
                    <select id="metrics-service-select" class="service-select">
                        <option value="">Select a service...</option>
                    </select>
                </div>

                <div id="metrics-dashboard" class="metrics-dashboard">
                    <div class="empty-state">
                        <i class="fas fa-chart-line" style="font-size: 48px;"></i>
                        <p>Select a service to view metrics</p>
                        <p class="text-secondary" style="font-size: 14px; margin-top: 8px;">
                            Note: Enable metrics streaming in Render Dashboard for detailed metrics
                        </p>
                    </div>
                </div>
            </div>
        `;

        this.populateServiceSelect('metrics-service-select');

        document.getElementById('metrics-service-select').addEventListener('change', (e) => {
            this.loadMetrics(e.target.value);
        });
    }

    async loadMetrics(serviceId) {
        if (!serviceId) return;

        const dashboard = document.getElementById('metrics-dashboard');
        dashboard.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i><p>Loading metrics...</p></div>';

        try {
            const response = await fetch(`/api/render/metrics?service_id=${serviceId}`);
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error);
            }

            this.renderMetrics(result.data);
        } catch (error) {
            console.error('❌ Failed to load metrics:', error);
            dashboard.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-chart-line" style="font-size: 48px; color: var(--warning);"></i>
                    <p>Metrics not available</p>
                    <p class="text-secondary" style="font-size: 14px;">
                        ${error.message || 'Setup metrics streaming in Render Dashboard for detailed metrics'}
                    </p>
                </div>
            `;
        }
    }

    renderMetrics(metrics) {
        const dashboard = document.getElementById('metrics-dashboard');

        dashboard.innerHTML = `
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-icon"><i class="fas fa-server"></i></div>
                    <div class="metric-value">${metrics.status || 'Unknown'}</div>
                    <div class="metric-label">Status</div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon"><i class="fas fa-memory"></i></div>
                    <div class="metric-value">N/A</div>
                    <div class="metric-label">Memory Usage</div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon"><i class="fas fa-microchip"></i></div>
                    <div class="metric-value">N/A</div>
                    <div class="metric-label">CPU Usage</div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon"><i class="fas fa-tachometer-alt"></i></div>
                    <div class="metric-value">N/A</div>
                    <div class="metric-label">Request Rate</div>
                </div>
            </div>

            <div class="metric-note">
                <i class="fas fa-info-circle"></i>
                <span>Enable metrics streaming in Render Dashboard → Integrations → Observability for detailed metrics</span>
            </div>
        `;
    }

    // ===== DATABASES TAB =====
    initializeDatabasesTab() {
        const container = this.getSubTabContainer('databases');
        const primaryColor = this.getPrimaryColor();

        container.innerHTML = `
            <div class="render-databases-container">
                <div class="module-header" style="border-bottom: 2px solid ${primaryColor};">
                    <h2><i class="fas fa-database"></i> PostgreSQL Databases</h2>
                    <button id="refresh-databases-btn" class="btn-primary">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                </div>

                <div id="databases-grid" class="databases-grid">
                    <div class="empty-state">
                        <i class="fas fa-database" style="font-size: 48px;"></i>
                        <p>Database management coming soon</p>
                        <p class="text-secondary">Trigger backups, view connections, monitor performance</p>
                    </div>
                </div>
            </div>
        `;
    }

    // ===== ACTION METHODS =====
    async deployService(serviceId) {
        if (!confirm('Deploy this service to latest commit?')) return;

        try {
            const response = await fetch('/api/render/deploy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ service_id: serviceId, wait: true })
            });

            const result = await response.json();

            if (result.success) {
                alert(`Deployment started! Deploy ID: ${result.deploy_id}`);
                this.loadServices(); // Refresh services
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            alert(`Deployment failed: ${error.message}`);
        }
    }

    async restartService(serviceId) {
        if (!confirm('Restart this service? This will trigger a new deployment.')) return;

        try {
            const response = await fetch('/api/render/restart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ service_id: serviceId })
            });

            const result = await response.json();

            if (result.success) {
                alert('Service restart initiated!');
                this.loadServices();
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            alert(`Restart failed: ${error.message}`);
        }
    }

    viewLogs(serviceId) {
        // Switch to logs tab and load logs for this service
        this.switchSubTab('logs');
        document.getElementById('logs-service-select').value = serviceId;
        this.loadLogs(serviceId);
    }

    // ===== UTILITY METHODS =====
    getPrimaryColor() {
        return (this.manifest && this.manifest.colors && this.manifest.colors.primary)
            ? this.manifest.colors.primary
            : (this.manifest && this.manifest.color)
            ? this.manifest.color
            : '#6C5CE7';
    }

    getStatusColor(status) {
        const colors = {
            'live': '#00B894',
            'suspended': '#FDCB6E',
            'failed': '#D63031',
            'building': '#0984E3',
            'deploying': '#0984E3'
        };
        return colors[status] || '#A29BFE';
    }

    getStatusIcon(status) {
        const icons = {
            'live': 'fas fa-check-circle',
            'suspended': 'fas fa-pause-circle',
            'failed': 'fas fa-times-circle',
            'building': 'fas fa-spinner fa-spin',
            'deploying': 'fas fa-spinner fa-spin'
        };
        return icons[status] || 'fas fa-circle';
    }

    getTypeIcon(type) {
        const icons = {
            'web_service': 'fas fa-globe',
            'private_service': 'fas fa-lock',
            'background_worker': 'fas fa-cog',
            'cron_job': 'fas fa-clock'
        };
        return icons[type] || 'fas fa-server';
    }

    populateServiceSelect(selectId) {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Select a service...</option>' +
            this.services.map(s => `<option value="${s.service_id}">${s.name}</option>`).join('');
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString();
    }

    calculateDuration(start, end) {
        if (!start || !end) return null;
        const duration = new Date(end) - new Date(start);
        const minutes = Math.floor(duration / 60000);
        const seconds = Math.floor((duration % 60000) / 1000);
        return `${minutes}m ${seconds}s`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showError(containerId, message) {
        const container = document.getElementById(containerId);
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: var(--danger);"></i>
                <p style="color: var(--danger);">${message}</p>
            </div>
        `;
    }

    // ===== CLEANUP =====
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        if (this.logUpdateInterval) {
            clearInterval(this.logUpdateInterval);
        }
    }
}

// Register module
window.ModuleRegistry['render-management'] = RenderManagementModule;


// ES6 Export
export default RenderManagementModule;
