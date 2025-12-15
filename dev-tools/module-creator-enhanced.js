/**
 * Module Creator & Verifier - ENHANCED VERSION
 * ============================================
 * 
 * NEW FEATURES:
 * ✅ Monaco Editor (VS Code's editor in browser)
 * ✅ Multi-file tabs (HTML/JS/CSS/Routes/Manifest)
 * ✅ Live preview with REAL UI CSS injection
 * ✅ WebSocket for real-time file sync
 * ✅ Auto-save (Ctrl+S)
 * ✅ Code formatting (Alt+Shift+F)
 * ✅ Syntax highlighting
 * ✅ IntelliSense autocomplete
 * ✅ Error detection
 */

class ModuleCreatorEnhanced {
    constructor() {
        this.API_BASE = window.location.origin.includes('5001')
            ? window.location.origin
            : 'http://localhost:5001';

        // Monaco Editor instances
        this.editors = {
            html: null,
            js: null,
            css: null,
            routes: null,
            manifest: null
        };

        this.currentFile = 'html';
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

        // File contents
        this.fileContents = {
            html: '',
            js: '',
            css: '',
            routes: '',
            manifest: ''
        };

        // Real UI CSS URLs
        this.uiCssFiles = [
            '../UI/modules_internal/agents/agent-ui.css',
            // Add more global CSS files from your UI
        ];

        this.consoleMessages = [];
        this.networkCalls = [];
        this.autoScroll = true;
        this.autoRefresh = true;
        this.socket = null;

        // Credential storage (browser memory only)
        this.testCredentials = new Map(); // platform -> {credentials, status, lastTested}

        this.init();
    }

    async init() {
        this.log('Initializing Enhanced Module Creator...', 'info');

        try {
            // Initialize Monaco Editor
            await this.initMonaco();

            // Initialize WebSocket
            this.initWebSocket();

            // Check backend
            await this.checkBackendStatus();

            // Bind events
            this.bindEvents();

            // Load default templates
            this.loadDefaultTemplates();

            this.log('Module Creator initialized successfully!', 'info');
        } catch (error) {
            this.log(`Initialization failed: ${error.message}`, 'error');
        }
    }

    /**
     * Initialize Monaco Editor (VS Code's editor)
     */
    async initMonaco() {
        return new Promise((resolve, reject) => {
            require.config({
                paths: {
                    vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs'
                }
            });

            require(['vs/editor/editor.main'], () => {
                this.log('Monaco Editor loaded', 'info');

                const container = document.getElementById('monaco-editor-container');

                // Create editors for each file type
                const editorOptions = {
                    theme: 'vs-dark',
                    automaticLayout: true,
                    minimap: { enabled: true },
                    fontSize: 13,
                    lineNumbers: 'on',
                    roundedSelection: true,
                    scrollBeyondLastLine: false,
                    readOnly: false,
                    wordWrap: 'on',
                    suggestOnTriggerCharacters: true,
                    quickSuggestions: true,
                    formatOnPaste: true,
                    formatOnType: true
                };

                // Create single editor instance (we'll swap models)
                this.mainEditor = monaco.editor.create(container, {
                    ...editorOptions,
                    language: 'html',
                    value: this.getDefaultContent('html')
                });

                // Create models for each file type
                this.models = {
                    html: monaco.editor.createModel(
                        this.getDefaultContent('html'),
                        'html'
                    ),
                    js: monaco.editor.createModel(
                        this.getDefaultContent('js'),
                        'javascript'
                    ),
                    css: monaco.editor.createModel(
                        this.getDefaultContent('css'),
                        'css'
                    ),
                    routes: monaco.editor.createModel(
                        this.getDefaultContent('routes'),
                        'python'
                    ),
                    manifest: monaco.editor.createModel(
                        this.getDefaultContent('manifest'),
                        'json'
                    )
                };

                // Set initial model
                this.mainEditor.setModel(this.models.html);

                // Listen for content changes
                Object.keys(this.models).forEach(fileType => {
                    this.models[fileType].onDidChangeContent(() => {
                        this.fileContents[fileType] = this.models[fileType].getValue();

                        // Auto-refresh preview if enabled
                        if (this.autoRefresh && fileType === 'html') {
                            this.updateLivePreview();
                        }
                    });
                });

                // Keyboard shortcuts
                this.mainEditor.addCommand(
                    monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_S,
                    () => this.saveAllFiles()
                );

                this.mainEditor.addCommand(
                    monaco.KeyMod.Alt | monaco.KeyMod.Shift | monaco.KeyCode.KEY_F,
                    () => this.formatCode()
                );

                resolve();
            });
        });
    }

    /**
     * Initialize WebSocket for real-time file sync
     */
    initWebSocket() {
        try {
            // Connect to /ws/dev-tools namespace
            this.socket = io(`${this.API_BASE}/ws/dev-tools`);

            this.socket.on('connect', () => {
                this.log('WebSocket connected', 'info');
                this.updateSyncStatus('connected');
            });

            this.socket.on('disconnect', () => {
                this.log('WebSocket disconnected', 'warn');
                this.updateSyncStatus('disconnected');
            });

            // Listen for file updates from other tabs/users
            this.socket.on('file_updated', (data) => {
                this.log(`File updated: ${data.file_type}`, 'info');

                if (this.models[data.file_type]) {
                    this.models[data.file_type].setValue(data.content);
                }

                if (data.file_type === 'html') {
                    this.updateLivePreview();
                }
            });

            // Listen for module creation events
            this.socket.on('module_created', (data) => {
                this.log(`Module created: ${data.module_id}`, 'info');
            });

            // Handle pong responses (keep-alive)
            this.socket.on('pong', (data) => {
                this.log('Server responded to ping', 'debug');
            });

            // Send periodic pings to keep connection alive
            setInterval(() => {
                if (this.socket && this.socket.connected) {
                    this.socket.emit('ping');
                }
            }, 30000); // Every 30 seconds

        } catch (error) {
            this.log(`WebSocket initialization failed: ${error.message}`, 'warn');
        }
    }

    /**
     * Get default content for each file type
     */
    getDefaultContent(fileType) {
        const templates = {
            html: `<!-- Module HTML Template -->
<div class="module-container">
    <div class="module-header">
        <h2><i class="fas fa-cube"></i> My Module</h2>
        <p class="module-description">Module description goes here</p>
    </div>
    
    <div class="module-content">
        <!-- Your module content here -->
        <p>Start building your module!</p>
    </div>
</div>

<style>
.module-container {
    padding: 20px;
}

.module-header h2 {
    font-size: 24px;
    margin-bottom: 8px;
}

.module-content {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>`,

            js: `/**
 * Module JavaScript Controller
 */

class MyModule {
    constructor() {
        this.API_BASE = 'http://localhost:5001';
        this.init();
    }
    
    async init() {
        console.log('[Module] Initializing...');
        try {
            await this.loadData();
            this.bindEvents();
            console.log('[Module] Ready!');
        } catch (error) {
            console.error('[Module] Init failed:', error);
        }
    }
    
    async loadData() {
        const response = await fetch(`${ this.API_BASE }/api/modules / list`);
        const data = await response.json();
        console.log('[Module] Data loaded:', data);
        return data;
    }
    
    bindEvents() {
        // Bind your event listeners here
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.myModule = new MyModule();
});`,

            css: `/**
 * Module Stylesheet
 */

.module-container {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.module-header {
    margin-bottom: 20px;
}

.module-content {
    /* Your styles here */
}`,

                routes: `"""
Module Flask Routes
"""

from flask import Blueprint, jsonify, request

# Create blueprint
module_bp = Blueprint('my_module', __name__, url_prefix='/api/my-module')


@module_bp.route('/data', methods=['GET'])
def get_data():
    """Get module data"""
    try:
        data = {
            'success': True,
            'data': []
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@module_bp.route('/action', methods=['POST'])
def perform_action():
    """Perform module action"""
    try:
        payload = request.get_json()
        result = {
            'success': True,
            'message': 'Action completed'
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500`,

                    manifest: `{
  "id": "my_module",
  "name": "My Module",
  "version": "1.0.0",
  "description": "Module description",
  "icon": "fas fa-cube",
  "files": {
    "html": true,
    "js": true,
    "css": true,
    "routes": false
  },
  "features": {
    "requires_auth": true,
    "show_in_sidebar": true,
    "auto_load": false,
    "main_tab": false
  },
  "required_platforms": []
}`
    };

        return templates[fileType] || '';
    }

/**
 * Switch between file tabs
 */
switchFile(fileType) {
    if (!this.models[fileType]) return;

    this.currentFile = fileType;
    this.mainEditor.setModel(this.models[fileType]);

    // Update active tab
    document.querySelectorAll('.editor-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.file === fileType);
    });

    this.log(`Switched to ${fileType.toUpperCase()} editor`, 'log');
}

    /**
     * Update live preview with REAL UI CSS
     */
    async updateLivePreview() {
    const iframe = document.getElementById('module-preview');
    const htmlContent = this.models.html.getValue();

    // Load real UI CSS files
    let cssLinks = '';
    for (const cssFile of this.uiCssFiles) {
        cssLinks += `<link rel="stylesheet" href="${cssFile}">\n`;
    }

    // Include module CSS
    const moduleCSS = this.models.css.getValue();

    // Build complete HTML with real UI CSS
    const fullHTML = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Module Preview</title>
    
    <!-- Real UI Global CSS -->
    ${cssLinks}
    
    <!-- Module-specific CSS -->
    <style>
    ${moduleCSS}
    </style>
</head>
<body>
    ${htmlContent}
    
    <!-- Module JavaScript -->
    <script>
    ${this.models.js.getValue()}
    </script>
</body>
</html>`;

    iframe.srcdoc = fullHTML;
    this.log('Preview updated with real UI CSS', 'info');
}

    /**
     * Save all files to backend
     */
    async saveAllFiles() {
    if (!this.moduleData.id) {
        this.log('Cannot save: No module ID', 'error');
        return;
    }

    this.updateSyncStatus('syncing');
    this.log('Saving all files...', 'info');

    try {
        const filesToSave = Object.keys(this.models).map(fileType => ({
            file_type: fileType,
            content: this.models[fileType].getValue()
        }));

        const response = await fetch(`${this.API_BASE}/api/dev-tools/save-files`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                module_id: this.moduleData.id,
                files: filesToSave
            })
        });

        if (!response.ok) throw new Error('Save failed');

        const data = await response.json();
        this.log(`Saved ${data.files_saved || 0} files`, 'info');
        this.updateSyncStatus('connected');

        // Update last saved time
        document.getElementById('last-saved').textContent = new Date().toLocaleTimeString();

        // Emit to other tabs via WebSocket
        if (this.socket) {
            filesToSave.forEach(file => {
                this.socket.emit('file_saved', {
                    module_id: this.moduleData.id,
                    file_type: file.file_type,
                    content: file.content
                });
            });
        }

    } catch (error) {
        this.log(`Save failed: ${error.message}`, 'error');
        this.updateSyncStatus('error');
    }
}

/**
 * Format code in current editor
 */
formatCode() {
    this.mainEditor.getAction('editor.action.formatDocument').run();
    this.log('Code formatted', 'log');
}

/**
 * Load default templates based on module config
 */
loadDefaultTemplates() {
    const moduleId = this.moduleData.id || 'my_module';
    const moduleName = this.moduleData.name || 'My Module';

    // Update templates with module info
    Object.keys(this.models).forEach(fileType => {
        let content = this.models[fileType].getValue();
        content = content.replace(/my_module/g, moduleId);
        content = content.replace(/My Module/g, moduleName);
        this.models[fileType].setValue(content);
    });

    this.updateLivePreview();
}

    /**
     * Create new module
     */
    async createModule() {
    // Validate form
    const moduleId = document.getElementById('module-id').value.trim();
    const moduleName = document.getElementById('module-name').value.trim();

    if (!moduleId || !moduleName) {
        this.log('Module ID and Name are required', 'error');
        return;
    }

    this.moduleData.id = moduleId;
    this.moduleData.name = moduleName;
    this.moduleData.version = document.getElementById('module-version').value;
    this.moduleData.icon = document.getElementById('module-icon').value;
    this.moduleData.description = document.getElementById('module-description').value;

    // Get file selections
    this.moduleData.files.html = document.getElementById('file-html').checked;
    this.moduleData.files.js = document.getElementById('file-js').checked;
    this.moduleData.files.css = document.getElementById('file-css').checked;
    this.moduleData.files.routes = document.getElementById('file-routes').checked;

    // Get features
    this.moduleData.features.requires_auth = document.getElementById('feature-auth').checked;
    this.moduleData.features.show_in_sidebar = document.getElementById('feature-sidebar').checked;
    this.moduleData.features.auto_load = document.getElementById('feature-autoload').checked;
    this.moduleData.features.main_tab = document.getElementById('feature-maintab').checked;

    this.log(`Creating module: ${moduleName}`, 'info');

    try {
        // Build manifest
        const manifest = this.moduleData;

        // Update manifest editor
        this.models.manifest.setValue(JSON.stringify(manifest, null, 2));

        // Send to backend
        const response = await fetch(`${this.API_BASE}/api/dev-tools/create-module`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ...manifest,
                file_contents: {
                    html: this.models.html.getValue(),
                    js: this.models.js.getValue(),
                    css: this.models.css.getValue(),
                    routes: this.models.routes.getValue()
                }
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Creation failed');
        }

        const data = await response.json();
        this.log(`✅ Module created: ${data.path}`, 'info');
        this.log(`Files created: ${data.files_created.join(', ')}`, 'info');

        // Update templates with new module data
        this.loadDefaultTemplates();

    } catch (error) {
        this.log(`❌ Creation failed: ${error.message}`, 'error');
    }
}

/**
 * Bind event listeners
 */
bindEvents() {
    // File tabs
    document.querySelectorAll('.editor-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            this.switchFile(tab.dataset.file);
        });
    });

    // Save button
    document.getElementById('save-all')?.addEventListener('click', () => {
        this.saveAllFiles();
    });

    // Format button
    document.getElementById('format-code')?.addEventListener('click', () => {
        this.formatCode();
    });

    // Create module button
    document.getElementById('create-module')?.addEventListener('click', () => {
        this.createModule();
    });

    // Auto-refresh toggle
    document.getElementById('auto-refresh')?.addEventListener('change', (e) => {
        this.autoRefresh = e.target.checked;
        if (this.autoRefresh) {
            this.updateLivePreview();
        }
    });

    // Console filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.toggle('active');
            this.filterConsole();
        });
    });

    // Clear console
    document.getElementById('clear-console')?.addEventListener('click', () => {
        this.clearConsole();
    });

    // Credential panel toggle
    document.getElementById('toggle-credentials')?.addEventListener('click', () => {
        this.toggleCredentialPanel();
    });

    // Test credential button
    document.getElementById('test-credential')?.addEventListener('click', () => {
        this.testCredential();
    });

    // Save credential button
    document.getElementById('save-credential')?.addEventListener('click', () => {
        this.saveTestCredential();
    });

    // Platform selection - update fields dynamically
    document.getElementById('credential-platform')?.addEventListener('change', (e) => {
        this.updateCredentialFields(e.target.value);
    });

    this.log('Event listeners bound', 'log');
}

/**
 * Update credential input fields based on platform
 */
updateCredentialFields(platform) {
    const fieldsContainer = document.getElementById('credential-fields');

    // Platform-specific fields
    const platformFields = {
        'custom': ['API Key'],
        'openai': ['API Key'],
        'anthropic': ['API Key'],
        'pinecone': ['API Key'],
        'stripe': ['Secret Key'],
        'shopify': ['API Key', 'Shop Domain'],
        'twilio': ['Account SID', 'Auth Token'],
        'sendgrid': ['API Key'],
        'supabase': ['URL', 'Anon Key']
    };

    const fields = platformFields[platform] || ['API Key'];

    fieldsContainer.innerHTML = fields.map(fieldName => {
        const fieldId = fieldName.toLowerCase().replace(/\s/g, '-');
        return `
                <div class="form-group">
                    <label>${fieldName}</label>
                    <input type="password" id="credential-${fieldId}" class="dev-input" placeholder="${fieldName}">
                </div>
            `;
    }).join('');
}

    /**
     * Check backend connection
     */
    async checkBackendStatus() {
    try {
        const response = await fetch(`${this.API_BASE}/api/pool/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            document.getElementById('backend-status').classList.add('connected');
            document.getElementById('backend-status-text').textContent = 'Connected';
            this.log('Backend connected', 'info');
        }
    } catch (error) {
        document.getElementById('backend-status').classList.add('disconnected');
        document.getElementById('backend-status-text').textContent = 'Disconnected';
        this.log('Backend disconnected', 'warn');
    }
}

/**
 * Update sync status indicator
 */
updateSyncStatus(status) {
    const indicator = document.getElementById('sync-status');
    const text = document.getElementById('sync-text');

    indicator.className = 'sync-indicator';

    switch (status) {
        case 'connected':
            indicator.classList.add('connected');
            text.textContent = 'Synced';
            break;
        case 'syncing':
            indicator.classList.add('syncing');
            text.textContent = 'Saving...';
            break;
        case 'disconnected':
            text.textContent = 'Offline';
            break;
        case 'error':
            text.textContent = 'Error';
            break;
    }
}

/**
 * Console logging
 */
log(message, level = 'log') {
    const timestamp = new Date().toLocaleTimeString();
    this.consoleMessages.push({ timestamp, message, level });

    const consoleOutput = document.getElementById('console-output');
    const line = document.createElement('div');
    line.className = `console-line ${level}`;
    line.innerHTML = `
            <span class="timestamp">${timestamp}</span>
            <span class="level">${level.toUpperCase()}</span>
            <span class="message">${message}</span>
        `;

    consoleOutput.appendChild(line);

    if (this.autoScroll) {
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }

    // Update stats
    document.getElementById('console-count').textContent = this.consoleMessages.length;
    if (level === 'error') {
        const errorCount = this.consoleMessages.filter(m => m.level === 'error').length;
        document.getElementById('error-count').textContent = errorCount;
    }
}

clearConsole() {
    this.consoleMessages = [];
    document.getElementById('console-output').innerHTML = '';
    document.getElementById('console-count').textContent = '0';
    document.getElementById('error-count').textContent = '0';
}

filterConsole() {
    const activeFilters = Array.from(document.querySelectorAll('.filter-btn.active'))
        .map(btn => btn.dataset.level);

    document.querySelectorAll('.console-line').forEach(line => {
        const level = line.classList[1];
        line.style.display = activeFilters.includes('all') || activeFilters.includes(level)
            ? 'flex'
            : 'none';
    });
}

/**
 * Credential Management
 */
toggleCredentialPanel() {
    const panel = document.getElementById('credentials-panel');
    const icon = document.querySelector('#toggle-credentials i');

    if (panel.style.display === 'none') {
        panel.style.display = 'block';
        icon.className = 'fas fa-chevron-up';
    } else {
        panel.style.display = 'none';
        icon.className = 'fas fa-chevron-down';
    }
}

    async saveTestCredential() {
    const platform = document.getElementById('credential-platform').value;
    const apiKey = document.getElementById('credential-api-key').value;

    if (!platform) {
        this.log('Please select a platform', 'warn');
        return;
    }

    if (!apiKey) {
        this.log('Please enter API key', 'warn');
        return;
    }

    // Store in memory (Map)
    this.testCredentials.set(platform, {
        credentials: { API_KEY: apiKey },
        status: 'untested',
        lastTested: null
    });

    this.log(`Credential saved for ${platform}`, 'info');
    this.renderSavedCredentials();

    // Clear input
    document.getElementById('credential-api-key').value = '';
}

    async testCredential() {
    const platform = document.getElementById('credential-platform').value;
    const apiKey = document.getElementById('credential-api-key').value;

    if (!platform || !apiKey) {
        this.log('Platform and API key required', 'warn');
        return;
    }

    const resultDiv = document.getElementById('credential-test-result');
    resultDiv.style.display = 'block';
    resultDiv.className = 'testing';
    resultDiv.textContent = `Testing ${platform} credentials...`;

    this.log(`Testing ${platform} credentials...`, 'info');

    try {
        const response = await fetch(`${this.API_BASE}/api/auth/credentials/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token') || 'dev_test_token'}`
            },
            body: JSON.stringify({
                platform: platform,
                credentials: { API_KEY: apiKey },
                settings: {}
            })
        });

        const result = await response.json();

        if (result.success) {
            resultDiv.className = 'success';
            resultDiv.innerHTML = `
                    <strong>✅ Connection Successful</strong><br>
                    ${result.message}<br>
                    ${result.details ? `<small>${JSON.stringify(result.details, null, 2)}</small>` : ''}
                `;
            this.log(`Credential test passed for ${platform}`, 'info');

            // Update stored credential status
            if (this.testCredentials.has(platform)) {
                const cred = this.testCredentials.get(platform);
                cred.status = 'success';
                cred.lastTested = new Date().toISOString();
                this.renderSavedCredentials();
            }
        } else {
            resultDiv.className = 'error';
            resultDiv.innerHTML = `
                    <strong>❌ Connection Failed</strong><br>
                    ${result.message || result.error}
                `;
            this.log(`Credential test failed for ${platform}: ${result.message}`, 'error');

            // Update stored credential status
            if (this.testCredentials.has(platform)) {
                const cred = this.testCredentials.get(platform);
                cred.status = 'error';
                cred.lastTested = new Date().toISOString();
                this.renderSavedCredentials();
            }
        }

    } catch (error) {
        resultDiv.className = 'error';
        resultDiv.innerHTML = `
                <strong>❌ Test Failed</strong><br>
                ${error.message}
            `;
        this.log(`Credential test error: ${error.message}`, 'error');
    }
}

renderSavedCredentials() {
    const container = document.getElementById('saved-credentials');
    container.innerHTML = '';

    if (this.testCredentials.size === 0) {
        container.innerHTML = '<small style="color: var(--text-muted);">No saved credentials</small>';
        return;
    }

    this.testCredentials.forEach((data, platform) => {
        const item = document.createElement('div');
        item.className = 'credential-item';

        const maskedKey = data.credentials.API_KEY.substring(0, 8) + '...';

        item.innerHTML = `
                <div class="credential-info">
                    <div class="credential-platform">${platform}</div>
                    <div class="credential-key">${maskedKey}</div>
                </div>
                <span class="credential-status ${data.status}">${data.status}</span>
                <div class="credential-actions">
                    <button class="btn-icon" onclick="window.moduleCreator.injectCredentialToPreview('${platform}')" title="Inject to preview">
                        <i class="fas fa-syringe"></i>
                    </button>
                    <button class="btn-icon" onclick="window.moduleCreator.deleteCredential('${platform}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;

        container.appendChild(item);
    });
}

deleteCredential(platform) {
    this.testCredentials.delete(platform);
    this.log(`Deleted credential for ${platform}`, 'info');
    this.renderSavedCredentials();
}

injectCredentialToPreview(platform) {
    if (!this.testCredentials.has(platform)) {
        this.log(`No credential found for ${platform}`, 'warn');
        return;
    }

    const iframe = document.getElementById('module-preview');
    const cred = this.testCredentials.get(platform);

    // Inject credential into iframe's window object
    if (iframe && iframe.contentWindow) {
        iframe.contentWindow.postMessage({
            type: 'INJECT_CREDENTIAL',
            platform: platform,
            credentials: cred.credentials
        }, '*');

        this.log(`Injected ${platform} credentials into preview iframe`, 'info');
    }
}

getAllTestCredentials() {
    // Convert Map to object for easy access
    const obj = {};
    this.testCredentials.forEach((data, platform) => {
        obj[platform] = data.credentials;
    });
    return obj;
}
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.moduleCreator = new ModuleCreatorEnhanced();
});
