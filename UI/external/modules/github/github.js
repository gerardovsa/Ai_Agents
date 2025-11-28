/**
 * GitHub Repository Management Module
 * ====================================
 * 
 * Personal GitHub integration using user-specific Personal Access Tokens.
 * Each user connects their own GitHub account via Account Settings.
 * 
 * Features:
 * - Create repositories
 * - Commit files
 * - Create pull requests
 * - List issues
 * 
 * Backend: tools/implementations/github.py
 * Credential: GitHub Personal Access Token (ghp_...)
 */

class GitHubModule {
    constructor() {
        this.moduleId = 'github';
        this.apiBase = window.API_BASE_URL || 'http://localhost:5001';
        this.initialized = false;
        this.hasCredentials = false;
    }

    /**
     * Initialize the GitHub module
     */
    async initialize() {
        console.log('🔧 Initializing GitHub Module...');
        
        try {
            // Check if user has GitHub credentials
            await this.checkCredentials();
            
            // Set up event listeners
            this.setupEventListeners();
            
            this.initialized = true;
            console.log('✅ GitHub Module initialized successfully');
            
            return true;
        } catch (error) {
            console.error('❌ Failed to initialize GitHub Module:', error);
            throw error;
        }
    }

    /**
     * Check if user has GitHub credentials
     */
    async checkCredentials() {
        try {
            const response = await fetch(`${this.apiBase}/api/connections`, {
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
                
                const banner = document.getElementById('github-credential-status');
                if (banner) {
                    banner.classList.toggle('hidden', this.hasCredentials);
                }
                
                console.log(`🔑 GitHub credentials: ${this.hasCredentials ? 'Found' : 'Not found'}`);
            }
        } catch (error) {
            console.error('❌ Failed to check GitHub credentials:', error);
        }
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Action card buttons
        document.querySelector('#github-create-repo-card .btn-action')?.addEventListener('click', () => {
            this.openModal('github-create-repo-modal');
        });

        document.querySelector('#github-commit-file-card .btn-action')?.addEventListener('click', () => {
            this.openModal('github-commit-file-modal');
        });

        document.querySelector('#github-create-pr-card .btn-action')?.addEventListener('click', () => {
            this.openModal('github-create-pr-modal');
        });

        document.querySelector('#github-list-issues-card .btn-action')?.addEventListener('click', () => {
            this.openModal('github-list-issues-modal');
        });

        // Modal submit buttons
        document.getElementById('github-create-repo-submit')?.addEventListener('click', () => {
            this.createRepository();
        });

        document.getElementById('github-commit-file-submit')?.addEventListener('click', () => {
            this.commitFile();
        });

        document.getElementById('github-create-pr-submit')?.addEventListener('click', () => {
            this.createPullRequest();
        });

        document.getElementById('github-list-issues-submit')?.addEventListener('click', () => {
            this.listIssues();
        });

        // Header buttons
        document.getElementById('github-refresh-btn')?.addEventListener('click', () => {
            this.checkCredentials();
        });

        document.getElementById('github-add-token-btn')?.addEventListener('click', () => {
            // Open Account Settings -> Connections tab
            window.location.hash = '#settings';
            setTimeout(() => {
                const connectionsTab = document.querySelector('[data-tab="connections"]');
                if (connectionsTab) connectionsTab.click();
            }, 100);
        });

        document.getElementById('github-clear-results')?.addEventListener('click', () => {
            this.clearResults();
        });

        // Modal close buttons
        document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                if (modal) this.closeModal(modal.id);
            });
        });
    }

    /**
     * Open modal
     */
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    /**
     * Close modal
     */
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    /**
     * Create GitHub repository
     */
    async createRepository() {
        const name = document.getElementById('repo-name').value.trim();
        const description = document.getElementById('repo-description').value.trim();
        const isPrivate = document.getElementById('repo-private').checked;

        if (!name) {
            this.showError('Repository name is required');
            return;
        }

        try {
            this.showLoading('Creating repository...');

            const response = await fetch(`${this.apiBase}/api/agent/execute-tool`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({
                    tool_name: 'github_create_repo',
                    parameters: {
                        name: name,
                        description: description || undefined,
                        private: isPrivate
                    }
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccess('Repository Created', `
                    <div class="repo-result">
                        <h3>${result.data.full_name}</h3>
                        <p><strong>Owner:</strong> ${result.data.owner}</p>
                        <p><strong>URL:</strong> <a href="${result.data.html_url}" target="_blank">${result.data.html_url}</a></p>
                        <p><strong>Clone URL:</strong> <code>${result.data.clone_url}</code></p>
                        <p><strong>Private:</strong> ${result.data.private ? 'Yes' : 'No'}</p>
                    </div>
                `);
                this.closeModal('github-create-repo-modal');
            } else {
                this.showError(result.error || 'Failed to create repository');
            }
        } catch (error) {
            console.error('❌ Error creating repository:', error);
            this.showError('Failed to create repository: ' + error.message);
        }
    }

    /**
     * Commit file to repository
     */
    async commitFile() {
        const repo = document.getElementById('commit-repo').value.trim();
        const filePath = document.getElementById('commit-file-path').value.trim();
        const content = document.getElementById('commit-content').value;
        const message = document.getElementById('commit-message').value.trim();

        if (!repo || !filePath || !content || !message) {
            this.showError('All fields are required');
            return;
        }

        try {
            this.showLoading('Committing file...');

            const response = await fetch(`${this.apiBase}/api/agent/execute-tool`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({
                    tool_name: 'github_commit_file',
                    parameters: {
                        repo: repo,
                        file_path: filePath,
                        content: content,
                        message: message
                    }
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccess('File Committed', `
                    <div class="commit-result">
                        <p><strong>File:</strong> ${result.data.path}</p>
                        <p><strong>Commit SHA:</strong> <code>${result.data.commit_sha}</code></p>
                        <p><strong>Status:</strong> ✅ Committed</p>
                    </div>
                `);
                this.closeModal('github-commit-file-modal');
            } else {
                this.showError(result.error || 'Failed to commit file');
            }
        } catch (error) {
            console.error('❌ Error committing file:', error);
            this.showError('Failed to commit file: ' + error.message);
        }
    }

    /**
     * Create pull request
     */
    async createPullRequest() {
        const repo = document.getElementById('pr-repo').value.trim();
        const title = document.getElementById('pr-title').value.trim();
        const head = document.getElementById('pr-head').value.trim();
        const base = document.getElementById('pr-base').value.trim();
        const body = document.getElementById('pr-body').value.trim();

        if (!repo || !title || !head || !base) {
            this.showError('Repository, title, head, and base branches are required');
            return;
        }

        try {
            this.showLoading('Creating pull request...');

            const response = await fetch(`${this.apiBase}/api/agent/execute-tool`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({
                    tool_name: 'github_create_pr',
                    parameters: {
                        repo: repo,
                        title: title,
                        head: head,
                        base: base,
                        body: body || undefined
                    }
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccess('Pull Request Created', `
                    <div class="pr-result">
                        <h3>#${result.data.number}: ${result.data.title}</h3>
                        <p><strong>URL:</strong> <a href="${result.data.html_url}" target="_blank">${result.data.html_url}</a></p>
                        <p><strong>State:</strong> ${result.data.state}</p>
                    </div>
                `);
                this.closeModal('github-create-pr-modal');
            } else {
                this.showError(result.error || 'Failed to create pull request');
            }
        } catch (error) {
            console.error('❌ Error creating PR:', error);
            this.showError('Failed to create pull request: ' + error.message);
        }
    }

    /**
     * List issues from repository
     */
    async listIssues() {
        const repo = document.getElementById('issues-repo').value.trim();
        const state = document.getElementById('issues-state').value;
        const limit = parseInt(document.getElementById('issues-limit').value);

        if (!repo) {
            this.showError('Repository is required');
            return;
        }

        try {
            this.showLoading('Fetching issues...');

            const response = await fetch(`${this.apiBase}/api/agent/execute-tool`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({
                    tool_name: 'github_get_issues',
                    parameters: {
                        repo: repo,
                        state: state,
                        limit: limit
                    }
                })
            });

            const result = await response.json();

            if (result.success) {
                const issues = result.data.issues;
                const issuesHtml = issues.map(issue => `
                    <div class="issue-item">
                        <h4>#${issue.number}: ${issue.title}</h4>
                        <p><strong>State:</strong> <span class="badge badge-${issue.state}">${issue.state}</span></p>
                        <p><strong>URL:</strong> <a href="${issue.html_url}" target="_blank">${issue.html_url}</a></p>
                        <p><strong>Created:</strong> ${new Date(issue.created_at).toLocaleDateString()}</p>
                    </div>
                `).join('');

                this.showSuccess(`Issues (${result.data.count} found)`, issuesHtml);
                this.closeModal('github-list-issues-modal');
            } else {
                this.showError(result.error || 'Failed to fetch issues');
            }
        } catch (error) {
            console.error('❌ Error fetching issues:', error);
            this.showError('Failed to fetch issues: ' + error.message);
        }
    }

    /**
     * Show loading state
     */
    showLoading(message) {
        const resultsContainer = document.getElementById('github-results');
        const resultsContent = document.getElementById('github-results-content');
        
        resultsContainer.classList.remove('hidden');
        resultsContent.innerHTML = `
            <div class="loading-state">
                <i class="fas fa-spinner fa-spin"></i>
                <p>${message}</p>
            </div>
        `;
    }

    /**
     * Show success result
     */
    showSuccess(title, content) {
        const resultsContainer = document.getElementById('github-results');
        const resultsTitle = document.getElementById('github-results-title');
        const resultsContent = document.getElementById('github-results-content');
        
        resultsContainer.classList.remove('hidden');
        resultsTitle.textContent = title;
        resultsContent.innerHTML = `
            <div class="success-state">
                <i class="fas fa-check-circle"></i>
                ${content}
            </div>
        `;
    }

    /**
     * Show error
     */
    showError(message) {
        const resultsContainer = document.getElementById('github-results');
        const resultsTitle = document.getElementById('github-results-title');
        const resultsContent = document.getElementById('github-results-content');
        
        resultsContainer.classList.remove('hidden');
        resultsTitle.textContent = 'Error';
        resultsContent.innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-circle"></i>
                <p>${message}</p>
            </div>
        `;
    }

    /**
     * Clear results
     */
    clearResults() {
        const resultsContainer = document.getElementById('github-results');
        resultsContainer.classList.add('hidden');
        document.getElementById('github-results-content').innerHTML = '';
    }
}

// Module Registry Registration
window.ModuleRegistry = window.ModuleRegistry || {};
window.ModuleRegistry['github'] = {
    instance: null,

    init: async () => {
        console.log('📦 Initializing GitHub Module...');
        try {
            const module = new GitHubModule();
            await module.initialize();

            // Store instance in registry
            window.ModuleRegistry['github'].instance = module;

            console.log('✅ GitHub Module initialized successfully');
            return module;
        } catch (error) {
            console.error('❌ Failed to initialize GitHub Module:', error);
            throw error;
        }
    }
};

console.log('📦 GitHub Module script loaded');
