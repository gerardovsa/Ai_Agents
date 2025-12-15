/**
 * Module Creator & Verifier - Development Tool
 * ============================================
 * 
 * PURPOSE:
 * - Rapid module prototyping without touching production code
 * - Live preview of module UI
 * - API endpoint testing
 * - Real-time console logging
 * - Manifest validation
 * - No database impact (read-only mode)
 * 
 * ARCHITECTURE:
 * - Standalone HTML page (dev-tools/module-creator.html)
 * - Connects to live Flask backend (port 5001)
 * - Uses ModuleRegistry API for validation
 * - Sandboxed iframe for module preview
 * - WebSocket for real-time logs (optional)
 */

class ModuleCreator {
    constructor() {
        this.API_BASE = window.location.origin.includes('5001')
            ? window.location.origin
            : 'http://localhost:5001';

        this.moduleData = {
            id: '',
            name: '',
            version: '1.0.0',
            description: '',
            icon: 'fas fa-cube',
            files: {
                html: true,
                js: true,
                css: true,
                routes: false
            },
            features: {
                requires_auth: true,
                show_in_sidebar: true,
                auto_load: false,
                main_tab: false
            },
            required_platforms: []
        };

        this.consoleMessages = [];
        this.networkCalls = [];
        this.autoScroll = true;

        this.init();
    }

    /**
     * Initialize the module creator
     */
    async init() {
        this.log('Initializing Module Creator...', 'info');

        // Bind UI events
        this.bindEvents();

        // Check backend connection
        await this.checkBackendStatus();

        // Load available platforms
        await this.loadPlatforms();

        // Load existing modules
        await this.loadExistingModules();

        this.log('Module Creator ready', 'info');
    }

    /**
     * Bind all UI event listeners
     */
    bindEvents() {
        // Module type selection
        document.querySelectorAll('[data-type]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('[data-type]').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                const type = e.target.dataset.type;
                document.getElementById('existing-module-section').style.display =
                    type === 'existing' ? 'block' : 'none';
            });
        });

        // Form inputs
        document.getElementById('module-id').addEventListener('input', (e) => {
            this.moduleData.id = e.target.value;
            this.updateManifestPreview();
        });

        document.getElementById('module-name').addEventListener('input', (e) => {
            this.moduleData.name = e.target.value;
            this.updateManifestPreview();
        });

        document.getElementById('module-description').addEventListener('input', (e) => {
            this.moduleData.description = e.target.value;
            this.updateManifestPreview();
        });

        document.getElementById('module-version').addEventListener('input', (e) => {
            this.moduleData.version = e.target.value;
            this.updateManifestPreview();
        });

        document.getElementById('module-icon').addEventListener('input', (e) => {
            this.moduleData.icon = e.target.value;
            this.updateManifestPreview();
        });

        // Checkboxes
        document.getElementById('include-html').addEventListener('change', (e) => {
            this.moduleData.files.html = e.target.checked;
        });

        document.getElementById('include-js').addEventListener('change', (e) => {
            this.moduleData.files.js = e.target.checked;
        });

        document.getElementById('include-css').addEventListener('change', (e) => {
            this.moduleData.files.css = e.target.checked;
        });

        document.getElementById('include-routes').addEventListener('change', (e) => {
            this.moduleData.files.routes = e.target.checked;
        });

        // Feature checkboxes
        document.getElementById('requires-auth').addEventListener('change', (e) => {
            this.moduleData.features.requires_auth = e.target.checked;
            this.updateManifestPreview();
        });

        document.getElementById('show-in-sidebar').addEventListener('change', (e) => {
            this.moduleData.features.show_in_sidebar = e.target.checked;
            this.updateManifestPreview();
        });

        document.getElementById('auto-load').addEventListener('change', (e) => {
            this.moduleData.features.auto_load = e.target.checked;
            this.updateManifestPreview();
        });

        document.getElementById('main-tab').addEventListener('change', (e) => {
            this.moduleData.features.main_tab = e.target.checked;
            this.updateManifestPreview();
        });

        // Add platform
        document.getElementById('add-platform').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.target.value.trim()) {
                this.addPlatform(e.target.value.trim());
                e.target.value = '';
            }
        });

        // Action buttons
        document.getElementById('create-module').addEventListener('click', () => this.createModule());
        document.getElementById('validate-manifest').addEventListener('click', () => this.validateManifest());
        document.getElementById('generate-manifest').addEventListener('click', () => this.downloadManifest());

        // Tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tabName = e.target.closest('.tab-btn').dataset.tab;
                this.switchTab(tabName);
            });
        });

        // API Tester
        document.getElementById('send-request').addEventListener('click', () => this.sendAPIRequest());

        // Console controls
        document.getElementById('clear-console').addEventListener('click', () => this.clearConsole());
        document.getElementById('toggle-autoscroll').addEventListener('click', () => {
            this.autoScroll = !this.autoScroll;
            this.log(`Auto-scroll ${this.autoScroll ? 'enabled' : 'disabled'}`, 'info');
        });

        // Console filters
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.filterConsole(e.target.dataset.level);
            });
        });

        // Manifest controls
        document.getElementById('copy-manifest').addEventListener('click', () => this.copyManifest());
        document.getElementById('download-manifest').addEventListener('click', () => this.downloadManifest());
        document.getElementById('save-manifest').addEventListener('click', () => this.saveManifest());

        // Preview refresh
        document.getElementById('refresh-preview').addEventListener('click', () => this.refreshPreview());

        // Load existing module
        document.getElementById('load-module').addEventListener('click', () => this.loadModule());
    }

    /**
     * Check if Flask backend is accessible
     */
    async checkBackendStatus() {
        try {
            const response = await fetch(`${this.API_BASE}/api/pool/health`, {
                method: 'GET',
                timeout: 5000
            });

            if (response.ok) {
                const data = await response.json();
                this.updateStatus('backend', 'connected', 'Connected');
                this.updateStatus('db', 'connected', data.database_status || 'Connected');
                this.log(`Backend connected: ${this.API_BASE}`, 'info');
                return true;
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            this.updateStatus('backend', 'disconnected', 'Offline');
            this.updateStatus('db', 'unknown', 'Unknown');
            this.log(`Backend connection failed: ${error.message}`, 'error');
            return false;
        }
    }

    /**
     * Update status indicator
     */
    updateStatus(type, status, text) {
        const element = document.getElementById(`${type}-status`);
        const textElement = document.getElementById(`${type}-status-text`);

        element.className = `status-indicator ${status}`;
        textElement.textContent = text;
    }

    /**
     * Load available platforms from backend
     */
    async loadPlatforms() {
        try {
            const response = await fetch(`${this.API_BASE}/api/modules/platforms`, {
                method: 'GET'
            });

            if (response.ok) {
                const data = await response.json();
                const platforms = data.platforms || [
                    'openai', 'anthropic', 'pinecone', 'supabase', 'shopify',
                    'xero', 'kajabi', 'stripe', 'twilio', 'github'
                ];

                this.renderPlatformsList(platforms);
                this.log(`Loaded ${platforms.length} available platforms`, 'info');
            }
        } catch (error) {
            this.log(`Failed to load platforms: ${error.message}`, 'warn');
            // Use fallback platforms
            this.renderPlatformsList([
                'openai', 'anthropic', 'pinecone', 'supabase', 'shopify',
                'xero', 'kajabi', 'stripe', 'twilio', 'github'
            ]);
        }
    }

    /**
     * Render platforms list
     */
    renderPlatformsList(availablePlatforms) {
        const container = document.getElementById('platforms-list');
        container.innerHTML = availablePlatforms.map(platform => `
            <label class="platform-tag">
                <input type="checkbox" value="${platform}" 
                       ${this.moduleData.required_platforms.includes(platform) ? 'checked' : ''}>
                <span>${platform}</span>
            </label>
        `).join('');

        // Bind checkbox events
        container.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.addPlatform(e.target.value);
                } else {
                    this.removePlatform(e.target.value);
                }
            });
        });
    }

    /**
     * Add platform to required list
     */
    addPlatform(platform) {
        if (!this.moduleData.required_platforms.includes(platform)) {
            this.moduleData.required_platforms.push(platform);
            this.updateManifestPreview();
            this.log(`Added platform: ${platform}`, 'log');
        }
    }

    /**
     * Remove platform from required list
     */
    removePlatform(platform) {
        this.moduleData.required_platforms = this.moduleData.required_platforms.filter(p => p !== platform);
        this.updateManifestPreview();
        this.log(`Removed platform: ${platform}`, 'log');
    }

    /**
     * Load existing modules from backend
     */
    async loadExistingModules() {
        try {
            const response = await fetch(`${this.API_BASE}/api/modules`, {
                method: 'GET'
            });

            if (response.ok) {
                const data = await response.json();
                const modules = data.modules || [];

                const select = document.getElementById('existing-modules');
                select.innerHTML = '<option value="">-- Select a module --</option>' +
                    modules.map(m => `<option value="${m.id}">${m.name} (${m.id})</option>`).join('');

                this.log(`Loaded ${modules.length} existing modules`, 'info');
            }
        } catch (error) {
            this.log(`Failed to load existing modules: ${error.message}`, 'warn');
        }
    }

    /**
     * Load module from backend
     */
    async loadModule() {
        const moduleId = document.getElementById('existing-modules').value;
        if (!moduleId) {
            this.log('Please select a module', 'warn');
            return;
        }

        try {
            const response = await fetch(`${this.API_BASE}/api/modules/${moduleId}`, {
                method: 'GET'
            });

            if (response.ok) {
                const manifest = await response.json();
                this.populateFormFromManifest(manifest);
                this.log(`Loaded module: ${manifest.name}`, 'info');
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            this.log(`Failed to load module: ${error.message}`, 'error');
        }
    }

    /**
     * Populate form from manifest
     */
    populateFormFromManifest(manifest) {
        document.getElementById('module-id').value = manifest.id || '';
        document.getElementById('module-name').value = manifest.name || '';
        document.getElementById('module-description').value = manifest.description || '';
        document.getElementById('module-version').value = manifest.version || '1.0.0';
        document.getElementById('module-icon').value = manifest.icon || 'fas fa-cube';

        // Update module data
        this.moduleData.id = manifest.id;
        this.moduleData.name = manifest.name;
        this.moduleData.description = manifest.description;
        this.moduleData.version = manifest.version;
        this.moduleData.icon = manifest.icon;
        this.moduleData.required_platforms = manifest.required_platforms || [];

        // Update checkboxes
        document.getElementById('requires-auth').checked = manifest.requires_auth !== false;
        document.getElementById('show-in-sidebar').checked = manifest.show_in_sidebar !== false;
        document.getElementById('auto-load').checked = manifest.auto_load === true;
        document.getElementById('main-tab').checked = manifest.main_tab === true;

        this.moduleData.features = {
            requires_auth: manifest.requires_auth !== false,
            show_in_sidebar: manifest.show_in_sidebar !== false,
            auto_load: manifest.auto_load === true,
            main_tab: manifest.main_tab === true
        };

        // Refresh platform checkboxes
        this.loadPlatforms();

        this.updateManifestPreview();
    }

    /**
     * Update manifest JSON preview
     */
    updateManifestPreview() {
        const manifest = {
            id: this.moduleData.id || 'my-module',
            name: this.moduleData.name || 'My Module',
            version: this.moduleData.version,
            description: this.moduleData.description || 'Module description',
            icon: this.moduleData.icon,
            scriptPath: `external/modules/${this.moduleData.id || 'my-module'}/${this.moduleData.id || 'my-module'}.js`,
            stylePath: `external/modules/${this.moduleData.id || 'my-module'}/${this.moduleData.id || 'my-module'}.css`,
            requires_auth: this.moduleData.features.requires_auth,
            show_in_sidebar: this.moduleData.features.show_in_sidebar,
            auto_load: this.moduleData.features.auto_load,
            main_tab: this.moduleData.features.main_tab,
            required_platforms: this.moduleData.required_platforms,
            tabs: [
                {
                    id: 'main',
                    name: 'Main',
                    icon: 'fas fa-home',
                    default: true
                }
            ]
        };

        document.getElementById('manifest-preview').textContent = JSON.stringify(manifest, null, 2);
    }

    /**
     * Validate manifest structure
     */
    async validateManifest() {
        const manifestText = document.getElementById('manifest-preview').textContent;

        try {
            const manifest = JSON.parse(manifestText);

            // Send to backend for validation
            const response = await fetch(`${this.API_BASE}/api/dev-tools/validate-manifest`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ manifest })
            });

            if (response.ok) {
                const result = await response.json();
                if (result.valid) {
                    this.log('✅ Manifest is valid', 'info');
                    alert('Manifest is valid!');
                } else {
                    this.log(`❌ Manifest validation failed: ${result.errors.join(', ')}`, 'error');
                    alert(`Validation errors:\n${result.errors.join('\n')}`);
                }
            } else {
                // Fallback: client-side validation
                this.clientSideValidation(manifest);
            }
        } catch (error) {
            this.log(`Invalid JSON: ${error.message}`, 'error');
            alert(`Invalid JSON: ${error.message}`);
        }
    }

    /**
     * Client-side manifest validation
     */
    clientSideValidation(manifest) {
        const errors = [];

        if (!manifest.id) errors.push('Missing required field: id');
        if (!manifest.name) errors.push('Missing required field: name');
        if (!manifest.version) errors.push('Missing required field: version');
        if (!/^[a-z0-9-]+$/.test(manifest.id)) errors.push('Invalid id format (use lowercase, numbers, hyphens)');

        if (errors.length > 0) {
            this.log(`❌ Validation failed: ${errors.join(', ')}`, 'error');
            alert(`Validation errors:\n${errors.join('\n')}`);
        } else {
            this.log('✅ Manifest is valid (client-side check)', 'info');
            alert('Manifest is valid (client-side check)!');
        }
    }

    /**
     * Create module files (via backend)
     */
    async createModule() {
        if (!this.moduleData.id) {
            alert('Please enter a Module ID');
            return;
        }

        const manifestText = document.getElementById('manifest-preview').textContent;
        const manifest = JSON.parse(manifestText);

        try {
            this.log(`Creating module: ${this.moduleData.id}...`, 'info');

            const response = await fetch(`${this.API_BASE}/api/dev-tools/create-module`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    manifest,
                    files: this.moduleData.files
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.log(`✅ Module created successfully at: ${result.path}`, 'info');
                alert(`Module created successfully!\n\nPath: ${result.path}\n\nFiles created:\n${result.files.join('\n')}`);
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Failed to create module');
            }
        } catch (error) {
            this.log(`❌ Failed to create module: ${error.message}`, 'error');
            alert(`Failed to create module: ${error.message}`);
        }
    }

    /**
     * Send API request (tester)
     */
    async sendAPIRequest() {
        const method = document.getElementById('http-method').value;
        const endpoint = document.getElementById('api-endpoint').value;
        const bodyText = document.getElementById('request-body').value;

        if (!endpoint) {
            alert('Please enter an API endpoint');
            return;
        }

        const url = endpoint.startsWith('http') ? endpoint : `${this.API_BASE}${endpoint}`;

        try {
            const startTime = Date.now();

            const options = {
                method,
                headers: { 'Content-Type': 'application/json' }
            };

            if (method !== 'GET' && bodyText.trim()) {
                options.body = bodyText;
            }

            this.log(`${method} ${endpoint}`, 'info');
            this.logNetworkRequest(method, endpoint, 'pending');

            const response = await fetch(url, options);
            const responseTime = Date.now() - startTime;

            const responseData = await response.json();

            // Update UI
            document.getElementById('response-status').textContent = `${response.status} ${response.statusText}`;
            document.getElementById('response-status').className = `status-badge ${response.ok ? 'success' : 'error'}`;
            document.getElementById('response-time').textContent = `${responseTime}ms`;
            document.getElementById('response-body').textContent = JSON.stringify(responseData, null, 2);

            this.log(`Response ${response.status} in ${responseTime}ms`, response.ok ? 'info' : 'error');
            this.logNetworkRequest(method, endpoint, response.ok ? 'success' : 'error', responseTime);
            this.updateAPICount();

        } catch (error) {
            document.getElementById('response-status').textContent = 'Error';
            document.getElementById('response-status').className = 'status-badge error';
            document.getElementById('response-body').textContent = error.message;

            this.log(`API Error: ${error.message}`, 'error');
            this.logNetworkRequest(method, endpoint, 'error');
        }
    }

    /**
     * Log network request
     */
    logNetworkRequest(method, endpoint, status, time = null) {
        const networkLog = document.getElementById('network-log');
        const entry = document.createElement('div');
        entry.className = `network-entry ${status}`;
        entry.innerHTML = `
            <span class="network-method">${method}</span>
            <span class="network-endpoint">${endpoint}</span>
            <span class="network-status">${status}</span>
            ${time ? `<span class="network-time">${time}ms</span>` : ''}
        `;
        networkLog.appendChild(entry);
        networkLog.scrollTop = networkLog.scrollHeight;

        this.networkCalls.push({ method, endpoint, status, time });
    }

    /**
     * Switch tab
     */
    switchTab(tabName) {
        // Update buttons
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.getElementById(`${tabName}-tab`).classList.add('active');

        this.log(`Switched to ${tabName} tab`, 'log');
    }

    /**
     * Refresh preview iframe
     */
    refreshPreview() {
        const iframe = document.getElementById('module-preview');
        iframe.src = iframe.src; // Reload iframe
        this.log('Preview refreshed', 'log');
    }

    /**
     * Copy manifest to clipboard
     */
    copyManifest() {
        const manifestText = document.getElementById('manifest-preview').textContent;
        navigator.clipboard.writeText(manifestText).then(() => {
            this.log('Manifest copied to clipboard', 'info');
            alert('Manifest copied to clipboard!');
        }).catch(err => {
            this.log(`Failed to copy: ${err.message}`, 'error');
        });
    }

    /**
     * Download manifest as file
     */
    downloadManifest() {
        const manifestText = document.getElementById('manifest-preview').textContent;
        const blob = new Blob([manifestText], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'manifest.json';
        a.click();
        URL.revokeObjectURL(url);

        this.log('Manifest downloaded', 'info');
    }

    /**
     * Save manifest to module directory (via backend)
     */
    async saveManifest() {
        const manifestText = document.getElementById('manifest-preview').textContent;
        const manifest = JSON.parse(manifestText);

        try {
            const response = await fetch(`${this.API_BASE}/api/dev-tools/save-manifest`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ manifest })
            });

            if (response.ok) {
                this.log(`✅ Manifest saved successfully`, 'info');
                alert('Manifest saved successfully!');
            } else {
                throw new Error('Failed to save manifest');
            }
        } catch (error) {
            this.log(`❌ Failed to save manifest: ${error.message}`, 'error');
            alert(`Failed to save manifest: ${error.message}`);
        }
    }

    /**
     * Log message to console
     */
    log(message, level = 'log') {
        const timestamp = new Date().toLocaleTimeString();
        const consoleOutput = document.getElementById('console-output');

        const entry = document.createElement('div');
        entry.className = `console-line ${level}`;
        entry.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="level">[${level.toUpperCase()}]</span>
            <span class="message">${this.escapeHTML(message)}</span>
        `;

        consoleOutput.appendChild(entry);

        if (this.autoScroll) {
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        }

        this.consoleMessages.push({ timestamp, level, message });
        this.updateConsoleCount();

        if (level === 'error') {
            this.updateErrorCount();
        }

        // Also log to browser console
        console[level](message);
    }

    /**
     * Clear console
     */
    clearConsole() {
        document.getElementById('console-output').innerHTML = '';
        this.consoleMessages = [];
        this.updateConsoleCount();
        this.log('Console cleared', 'info');
    }

    /**
     * Filter console by level
     */
    filterConsole(level) {
        const lines = document.querySelectorAll('.console-line');
        lines.forEach(line => {
            if (level === 'all' || line.classList.contains(level)) {
                line.style.display = 'flex';
            } else {
                line.style.display = 'none';
            }
        });
    }

    /**
     * Update console message count
     */
    updateConsoleCount() {
        document.getElementById('console-count').textContent = this.consoleMessages.length;
    }

    /**
     * Update API call count
     */
    updateAPICount() {
        document.getElementById('api-count').textContent = this.networkCalls.length;
    }

    /**
     * Update error count
     */
    updateErrorCount() {
        const errorCount = this.consoleMessages.filter(m => m.level === 'error').length;
        document.getElementById('error-count').textContent = errorCount;
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHTML(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.moduleCreator = new ModuleCreator();
});
