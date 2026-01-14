/**
 * GitHub Management Module - v2.0.0
 * ===================================
 * 
 * Personal GitHub integration with sidebar and main dashboard.
 * Architecture 2: Inline HTML-in-JS for dynamic UI generation.
 * 
 * Features:
 * - Sidebar: Repository list, quick actions, recent activity
 * - Dashboard: Repository stats, commit history, issue tracking, PR management
 * - User-specific Personal Access Token integration
 * 
 * Backend: tools/implementations/github.py
 * Credential: GitHub Personal Access Token (ghp_...)
 * 
 * @class GitHubModule
 * @extends BaseModule
 * @created 2025-11-28
 */

console.log('🔷 GitHub Module Loading - VERSION 2.0.0 - Sidebar + Dashboard');

// BaseModule polyfill
class BaseModule {
    constructor(moduleId) {
        this.moduleId = moduleId;
        this.manifest = null;
        this.backendUrl = window.API_BASE_URL || 'http://localhost:5001';
        console.log(`✅ BaseModule constructor - moduleId: ${moduleId}`);
    }

    async initialize() {
        console.log(`✅ BaseModule.initialize() called for ${this.moduleId}`);
        try {
            const response = await fetch(`${this.backendUrl}/api/modules/${this.moduleId}`);
            if (response.ok) {
                this.manifest = await response.json();
                console.log(`✅ Manifest loaded for ${this.moduleId}:`, this.manifest);
            }
        } catch (error) {
            console.warn(`⚠️ Failed to load manifest for ${this.moduleId}:`, error);
        }
    }
}

class GitHubModule extends BaseModule {
    constructor() {
        super('github');

        console.log('🔷 GitHubModule constructor called');

        // Configuration
        this.API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
        this.apiEndpoint = '/api/agent/execute-tool';

        // State management
        this.initialized = false;
        this.hasCredentials = false;
        this.repositories = [];
        this.recentActivity = [];
        this.selectedRepo = null;
        this.currentView = 'dashboard';

        // UI References
        this.container = null;
        this.sidebarContainer = null;

        // Refresh interval
        this.refreshTimer = null;
    }

    /**
     * CRITICAL: Get container element for main dashboard
     */
    getMainContainer() {
        const tabContainer = document.getElementById(`tab-${this.moduleId}`);
        if (!tabContainer) {
            console.error(`❌ Main tab container not found: tab-${this.moduleId}`);
            return null;
        }
        return tabContainer;
    }

    /**
     * CRITICAL: Get container element for sidebar
     */
    getSidebarContainer() {
        const sidebar = document.getElementById(`${this.moduleId}-sidebar`);
        if (!sidebar) {
            console.error(`❌ Sidebar container not found: ${this.moduleId}-sidebar`);
            return null;
        }
        return sidebar;
    }

    /**
     * Initialize module - CRITICAL: This method MUST be called!
     */
    async initialize() {
        console.log('🔧 Initializing GitHub Module...');

        try {
            // Call parent initialize
            await super.initialize();

            // Store reference for event handlers
            window.currentGitHubModule = this;

            // CRITICAL: Inject CSS styles
            this.injectCriticalStyles();

            // Get containers
            this.container = this.getMainContainer();
            this.sidebarContainer = this.getSidebarContainer();

            if (!this.container) {
                throw new Error('Main container not found');
            }

            // Check credentials
            await this.checkCredentials();

            // CRITICAL: Generate dashboard HTML
            this.initializeDashboard();

            // CRITICAL: Generate sidebar HTML (if container exists)
            if (this.sidebarContainer) {
                this.initializeSidebar();
            }

            // Set up event listeners
            this.setupEventListeners();

            // Load initial data if credentials exist
            if (this.hasCredentials) {
                await this.refreshData();
            }

            this.initialized = true;
            console.log('✅ GitHub Module initialized successfully');

            return true;
        } catch (error) {
            console.error('❌ Failed to initialize GitHub Module:', error);
            this.showError('Failed to initialize module: ' + error.message);
            return false;
        }
    }

    /**
     * CRITICAL: Inject CSS styles inline
     */
    injectCriticalStyles() {
        const existingStyles = document.getElementById('github-critical-styles');
        if (existingStyles) {
            existingStyles.remove();
        }

        const styleSheet = document.createElement('style');
        styleSheet.id = 'github-critical-styles';
        styleSheet.textContent = `
            /* GitHub Module Container */
            #tab-github.active {
                display: block !important;
                width: 100%;
                height: 100%;
                overflow: auto;
                background: #f6f8fa;
            }

            /* Dashboard Layout */
            .github-dashboard {
                padding: 20px;
                max-width: 1400px;
                margin: 0 auto;
            }

            /* Header */
            .github-header {
                background: white;
                padding: 20px;
                border-radius: 6px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .github-header-left {
                display: flex;
                align-items: center;
                gap: 15px;
            }

            .github-header-left i {
                font-size: 32px;
                color: #24292e;
            }

            .github-header h1 {
                font-size: 24px;
                color: #24292e;
                margin: 0;
            }

            .github-header-right {
                display: flex;
                gap: 10px;
            }

            /* Credential Banner */
            .github-credential-banner {
                background: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 6px;
                padding: 15px;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 15px;
            }

            .github-credential-banner.hidden {
                display: none;
            }

            .github-credential-banner i {
                color: #ff9800;
                font-size: 24px;
            }

            .github-credential-banner span {
                flex: 1;
                color: #856404;
            }

            /* Stats Grid */
            .github-stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }

            .github-stat-card {
                background: white;
                padding: 20px;
                border-radius: 6px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }

            .github-stat-card h3 {
                font-size: 14px;
                color: #586069;
                margin: 0 0 10px 0;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .github-stat-card .stat-value {
                font-size: 32px;
                font-weight: bold;
                color: #24292e;
                margin-bottom: 5px;
            }

            .github-stat-card .stat-label {
                font-size: 14px;
                color: #586069;
            }

            /* Content Sections */
            .github-content-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }

            .github-section {
                background: white;
                padding: 20px;
                border-radius: 6px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }

            .github-section h2 {
                font-size: 18px;
                color: #24292e;
                margin: 0 0 15px 0;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .github-section h2 i {
                color: #0366d6;
            }

            /* Repository List */
            .github-repo-list {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }

            .github-repo-item {
                padding: 12px;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.2s;
            }

            .github-repo-item:hover {
                border-color: #0366d6;
                background: #f6f8fa;
            }

            .github-repo-item-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 5px;
            }

            .github-repo-name {
                font-weight: bold;
                color: #0366d6;
                font-size: 14px;
            }

            .github-repo-private {
                background: #fef9e7;
                color: #d4ac0d;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
            }

            .github-repo-desc {
                color: #586069;
                font-size: 13px;
                margin-bottom: 8px;
            }

            .github-repo-stats {
                display: flex;
                gap: 15px;
                font-size: 12px;
                color: #586069;
            }

            .github-repo-stats span {
                display: flex;
                align-items: center;
                gap: 5px;
            }

            /* Activity Feed */
            .github-activity-feed {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }

            .github-activity-item {
                padding: 12px;
                border-left: 3px solid #0366d6;
                background: #f6f8fa;
                border-radius: 4px;
            }

            .github-activity-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 5px;
            }

            .github-activity-type {
                font-weight: bold;
                color: #24292e;
                font-size: 13px;
            }

            .github-activity-time {
                color: #586069;
                font-size: 12px;
            }

            .github-activity-message {
                color: #586069;
                font-size: 13px;
            }

            /* Quick Actions */
            .github-quick-actions {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }

            .github-action-btn {
                padding: 12px;
                background: white;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.2s;
                text-align: center;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 8px;
            }

            .github-action-btn:hover {
                border-color: #0366d6;
                background: #f6f8fa;
            }

            .github-action-btn i {
                font-size: 24px;
                color: #0366d6;
            }

            .github-action-btn span {
                font-size: 13px;
                color: #24292e;
                font-weight: 500;
            }

            /* Sidebar */
            #github-sidebar {
                display: none;
                position: fixed;
                right: 0;
                top: 0;
                width: 400px;
                height: 100vh;
                background: white;
                box-shadow: -2px 0 10px rgba(0,0,0,0.1);
                z-index: 9999;
                overflow-y: auto;
            }

            #github-sidebar.active {
                display: flex !important;
                flex-direction: column;
            }

            .github-sidebar-header {
                padding: 20px;
                background: #24292e;
                color: white;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .github-sidebar-header h2 {
                margin: 0;
                font-size: 18px;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .github-sidebar-close {
                background: none;
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
                padding: 0;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .github-sidebar-close:hover {
                background: rgba(255,255,255,0.1);
                border-radius: 4px;
            }

            .github-sidebar-content {
                padding: 20px;
                flex: 1;
            }

            .github-sidebar-section {
                margin-bottom: 25px;
            }

            .github-sidebar-section h3 {
                font-size: 14px;
                color: #586069;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin: 0 0 15px 0;
            }

            /* Buttons */
            .btn-primary {
                background: #2ea44f;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: background 0.2s;
            }

            .btn-primary:hover {
                background: #2c974b;
            }

            .btn-secondary {
                background: white;
                color: #24292e;
                border: 1px solid #e1e4e8;
                padding: 8px 16px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.2s;
            }

            .btn-secondary:hover {
                border-color: #0366d6;
                color: #0366d6;
            }

            .btn-icon {
                background: none;
                border: none;
                color: #586069;
                cursor: pointer;
                padding: 8px;
                border-radius: 6px;
                transition: all 0.2s;
            }

            .btn-icon:hover {
                background: #f6f8fa;
                color: #24292e;
            }

            /* Loading State */
            .github-loading {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 40px;
                color: #586069;
            }

            .github-loading i {
                font-size: 48px;
                margin-bottom: 15px;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }

            /* Empty State */
            .github-empty {
                text-align: center;
                padding: 40px;
                color: #586069;
            }

            .github-empty i {
                font-size: 48px;
                margin-bottom: 15px;
                color: #d1d5da;
            }
        `;

        document.head.appendChild(styleSheet);
        console.log('✅ GitHub critical styles injected');
    }

    /**
     * CRITICAL: Generate dashboard HTML - MUST BE CALLED in initialize()
     */
    initializeDashboard() {
        console.log('🔧 Generating GitHub dashboard HTML...');

        if (!this.container) {
            console.error('❌ Cannot generate dashboard - container is null');
            return;
        }

        const html = `
            <div class="github-dashboard">
                <!-- Header -->
                <div class="github-header">
                    <div class="github-header-left">
                        <i class="fab fa-github"></i>
                        <h1>GitHub Management</h1>
                    </div>
                    <div class="github-header-right">
                        <button class="btn-icon" data-action="refresh" title="Refresh">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                        <button class="btn-icon" data-action="toggle-sidebar" title="Toggle Sidebar">
                            <i class="fas fa-bars"></i>
                        </button>
                    </div>
                </div>

                <!-- Credential Status Banner -->
                <div class="github-credential-banner ${this.hasCredentials ? 'hidden' : ''}" id="github-credential-banner">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>GitHub Personal Access Token required. Add your token in Account Settings → Connections.</span>
                    <button class="btn-primary" data-action="add-token">Add Token</button>
                </div>

                <!-- Stats Grid -->
                <div class="github-stats-grid" id="github-stats-grid">
                    ${this.renderStatsCards()}
                </div>

                <!-- Content Grid -->
                <div class="github-content-grid">
                    <!-- Repositories Section -->
                    <div class="github-section">
                        <h2>
                            <i class="fas fa-book"></i>
                            Repositories
                        </h2>
                        <div class="github-repo-list" id="github-repo-list">
                            ${this.renderRepositoryList()}
                        </div>
                    </div>

                    <!-- Recent Activity Section -->
                    <div class="github-section">
                        <h2>
                            <i class="fas fa-history"></i>
                            Recent Activity
                        </h2>
                        <div class="github-activity-feed" id="github-activity-feed">
                            ${this.renderActivityFeed()}
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.container.innerHTML = html;
        console.log('✅ GitHub dashboard HTML generated');
    }

    /**
     * CRITICAL: Generate sidebar HTML - MUST BE CALLED in initialize()
     */
    initializeSidebar() {
        console.log('🔧 Generating GitHub sidebar HTML...');

        if (!this.sidebarContainer) {
            console.error('❌ Cannot generate sidebar - container is null');
            return;
        }

        const html = `
            <!-- Sidebar Header -->
            <div class="github-sidebar-header">
                <h2>
                    <i class="fab fa-github"></i>
                    Quick Actions
                </h2>
                <button class="github-sidebar-close" data-action="close-sidebar">
                    <i class="fas fa-times"></i>
                </button>
            </div>

            <!-- Sidebar Content -->
            <div class="github-sidebar-content">
                <!-- Quick Actions Section -->
                <div class="github-sidebar-section">
                    <h3>Actions</h3>
                    <div class="github-quick-actions">
                        <div class="github-action-btn" data-action="create-repo">
                            <i class="fas fa-plus-circle"></i>
                            <span>Create Repo</span>
                        </div>
                        <div class="github-action-btn" data-action="commit-file">
                            <i class="fas fa-file-code"></i>
                            <span>Commit File</span>
                        </div>
                        <div class="github-action-btn" data-action="create-pr">
                            <i class="fas fa-code-branch"></i>
                            <span>Create PR</span>
                        </div>
                        <div class="github-action-btn" data-action="list-issues">
                            <i class="fas fa-exclamation-circle"></i>
                            <span>View Issues</span>
                        </div>
                    </div>
                </div>

                <!-- Recent Repos Section -->
                <div class="github-sidebar-section">
                    <h3>Recent Repositories</h3>
                    <div id="github-sidebar-repos">
                        ${this.renderSidebarRepos()}
                    </div>
                </div>
            </div>
        `;

        this.sidebarContainer.innerHTML = html;
        console.log('✅ GitHub sidebar HTML generated');
    }

    /**
     * Render stats cards
     */
    renderStatsCards() {
        if (!this.hasCredentials) {
            return `
                <div class="github-stat-card">
                    <h3>Repositories</h3>
                    <div class="stat-value">--</div>
                    <div class="stat-label">Connect GitHub to view</div>
                </div>
                <div class="github-stat-card">
                    <h3>Commits</h3>
                    <div class="stat-value">--</div>
                    <div class="stat-label">Connect GitHub to view</div>
                </div>
                <div class="github-stat-card">
                    <h3>Issues</h3>
                    <div class="stat-value">--</div>
                    <div class="stat-label">Connect GitHub to view</div>
                </div>
                <div class="github-stat-card">
                    <h3>Pull Requests</h3>
                    <div class="stat-value">--</div>
                    <div class="stat-label">Connect GitHub to view</div>
                </div>
            `;
        }

        return `
            <div class="github-stat-card">
                <h3>Repositories</h3>
                <div class="stat-value">${this.repositories.length}</div>
                <div class="stat-label">Total repositories</div>
            </div>
            <div class="github-stat-card">
                <h3>Commits</h3>
                <div class="stat-value">0</div>
                <div class="stat-label">This month</div>
            </div>
            <div class="github-stat-card">
                <h3>Issues</h3>
                <div class="stat-value">0</div>
                <div class="stat-label">Open issues</div>
            </div>
            <div class="github-stat-card">
                <h3>Pull Requests</h3>
                <div class="stat-value">0</div>
                <div class="stat-label">Open PRs</div>
            </div>
        `;
    }

    /**
     * Render repository list
     */
    renderRepositoryList() {
        if (!this.hasCredentials) {
            return `
                <div class="github-empty">
                    <i class="fas fa-book"></i>
                    <p>Connect your GitHub account to view repositories</p>
                </div>
            `;
        }

        if (this.repositories.length === 0) {
            return `
                <div class="github-empty">
                    <i class="fas fa-book"></i>
                    <p>No repositories found. Create your first repository!</p>
                </div>
            `;
        }

        return this.repositories.slice(0, 5).map(repo => `
            <div class="github-repo-item" data-repo="${repo.name}">
                <div class="github-repo-item-header">
                    <span class="github-repo-name">${repo.name}</span>
                    ${repo.private ? '<span class="github-repo-private">Private</span>' : ''}
                </div>
                <div class="github-repo-desc">${repo.description || 'No description'}</div>
                <div class="github-repo-stats">
                    <span><i class="fas fa-star"></i> ${repo.stars || 0}</span>
                    <span><i class="fas fa-code-branch"></i> ${repo.forks || 0}</span>
                    <span><i class="fas fa-circle"></i> ${repo.language || 'Unknown'}</span>
                </div>
            </div>
        `).join('');
    }

    /**
     * Render activity feed
     */
    renderActivityFeed() {
        if (!this.hasCredentials) {
            return `
                <div class="github-empty">
                    <i class="fas fa-history"></i>
                    <p>Connect your GitHub account to view activity</p>
                </div>
            `;
        }

        if (this.recentActivity.length === 0) {
            return `
                <div class="github-empty">
                    <i class="fas fa-history"></i>
                    <p>No recent activity</p>
                </div>
            `;
        }

        return this.recentActivity.map(activity => `
            <div class="github-activity-item">
                <div class="github-activity-header">
                    <span class="github-activity-type">${activity.type}</span>
                    <span class="github-activity-time">${activity.time}</span>
                </div>
                <div class="github-activity-message">${activity.message}</div>
            </div>
        `).join('');
    }

    /**
     * Render sidebar repos
     */
    renderSidebarRepos() {
        if (!this.hasCredentials) {
            return '<p style="color: #586069; text-align: center;">No credentials</p>';
        }

        if (this.repositories.length === 0) {
            return '<p style="color: #586069; text-align: center;">No repositories</p>';
        }

        return this.repositories.slice(0, 5).map(repo => `
            <div class="github-repo-item" data-repo="${repo.name}" style="margin-bottom: 10px;">
                <div class="github-repo-item-header">
                    <span class="github-repo-name">${repo.name}</span>
                </div>
                <div class="github-repo-desc" style="font-size: 12px;">${repo.description || 'No description'}</div>
            </div>
        `).join('');
    }

    /**
     * Set up event listeners - CRITICAL: Use event delegation
     */
    setupEventListeners() {
        console.log('🔧 Setting up GitHub event listeners...');

        // Dashboard event delegation
        if (this.container) {
            this.container.addEventListener('click', (e) => {
                const action = e.target.closest('[data-action]')?.dataset.action;

                if (action === 'refresh') {
                    this.refreshData();
                } else if (action === 'toggle-sidebar') {
                    this.toggleSidebar();
                } else if (action === 'add-token') {
                    this.navigateToAccountSettings();
                }
            });
        }

        // Sidebar event delegation
        if (this.sidebarContainer) {
            this.sidebarContainer.addEventListener('click', (e) => {
                const action = e.target.closest('[data-action]')?.dataset.action;

                if (action === 'close-sidebar') {
                    this.closeSidebar();
                } else if (action === 'create-repo') {
                    this.showCreateRepoModal();
                } else if (action === 'commit-file') {
                    this.showCommitFileModal();
                } else if (action === 'create-pr') {
                    this.showCreatePRModal();
                } else if (action === 'list-issues') {
                    this.showListIssuesModal();
                }
            });
        }

        console.log('✅ Event listeners set up');
    }

    /**
     * Check if user has GitHub credentials
     */
    async checkCredentials() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/connections`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                const githubConnection = data.credentials?.find(c => c.platform === 'github');

                this.hasCredentials = !!githubConnection;

                console.log(`🔑 GitHub credentials: ${this.hasCredentials ? 'Found' : 'Not found'}`);
            }
        } catch (error) {
            console.error('❌ Failed to check GitHub credentials:', error);
        }
    }

    /**
     * Refresh all data
     */
    async refreshData() {
        if (!this.hasCredentials) {
            console.log('⚠️ Cannot refresh - no credentials');
            return;
        }

        console.log('🔄 Refreshing GitHub data...');

        try {
            // Show loading state
            this.showLoading();

            // Fetch repositories (placeholder - implement actual API call)
            this.repositories = [
                {
                    name: 'example-repo',
                    description: 'Example repository',
                    private: false,
                    stars: 5,
                    forks: 2,
                    language: 'JavaScript'
                }
            ];

            // Fetch recent activity (placeholder)
            this.recentActivity = [
                {
                    type: 'Commit',
                    time: '2 hours ago',
                    message: 'Updated README.md'
                }
            ];

            // Re-render UI
            this.initializeDashboard();
            if (this.sidebarContainer) {
                this.initializeSidebar();
            }

            // Re-attach event listeners
            this.setupEventListeners();

            console.log('✅ Data refreshed successfully');
        } catch (error) {
            console.error('❌ Failed to refresh data:', error);
            this.showError('Failed to refresh data: ' + error.message);
        }
    }

    /**
     * Toggle sidebar visibility
     */
    toggleSidebar() {
        if (!this.sidebarContainer) {
            console.warn('⚠️ Sidebar container not found');
            return;
        }

        this.sidebarContainer.classList.toggle('active');
        console.log('🔄 Sidebar toggled');
    }

    /**
     * Close sidebar
     */
    closeSidebar() {
        if (!this.sidebarContainer) {
            return;
        }

        this.sidebarContainer.classList.remove('active');
        console.log('🔄 Sidebar closed');
    }

    /**
     * Navigate to account settings
     */
    navigateToAccountSettings() {
        console.log('🔄 Navigating to account settings...');
        // TODO: Implement navigation to account settings page
        alert('Please go to Account Settings → Connections to add your GitHub Personal Access Token');
    }

    /**
     * Show modals (placeholder methods)
     */
    showCreateRepoModal() {
        console.log('🔄 Opening Create Repository modal...');
        alert('Create Repository modal - To be implemented');
    }

    showCommitFileModal() {
        console.log('🔄 Opening Commit File modal...');
        alert('Commit File modal - To be implemented');
    }

    showCreatePRModal() {
        console.log('🔄 Opening Create Pull Request modal...');
        alert('Create Pull Request modal - To be implemented');
    }

    showListIssuesModal() {
        console.log('🔄 Opening List Issues modal...');
        alert('List Issues modal - To be implemented');
    }

    /**
     * Show loading state
     */
    showLoading() {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="github-loading">
                <i class="fas fa-spinner"></i>
                <p>Loading GitHub data...</p>
            </div>
        `;
    }

    /**
     * Show error message
     */
    showError(message) {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="github-empty">
                <i class="fas fa-exclamation-triangle" style="color: #d32f2f;"></i>
                <p style="color: #d32f2f;">${message}</p>
            </div>
        `;
    }

    /**
     * Cleanup method - remove styles and timers
     */
    cleanup() {
        console.log('🧹 Cleaning up GitHub module...');

        const styles = document.getElementById('github-critical-styles');
        if (styles) {
            styles.remove();
        }

        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }

        console.log('✅ GitHub module cleaned up');
    }
}

// REQUIRED: Register module in global registry
window.ModuleRegistry = window.ModuleRegistry || {};
window.ModuleRegistry['github'] = {
    instance: null,
    init: async function () {
        console.log('🚀 Initializing GitHub module from registry...');

        if (!this.instance) {
            this.instance = new GitHubModule();
        }

        const success = await this.instance.initialize();

        if (!success) {
            console.error('❌ GitHub module initialization failed');
            return false;
        }

        return true;
    }
};

console.log('✅ GitHub module registered in window.ModuleRegistry');
