/**
 * ====================================================================
 * DEV-TOOLS MODULE - External Module Architecture
 * ====================================================================
 * 
 * A reusable, portable module creation and verification system
 * 
 * FEATURES:
 * - Class-based singleton pattern for global instance management
 * - Monaco Editor integration (VS Code in browser)
 * - Multi-file tab management (HTML/JS/CSS/Routes/Manifest)
 * - Live preview with real UI CSS injection
 * - Credential testing system integration
 * - WebSocket for real-time file synchronization
 * - Auto-save (Ctrl+S) and code formatting (Alt+Shift+F)
 * - Module validation and verification
 * - Template system for quick module scaffolding
 * - Auto-plugin system for dashboard/sidebar integration
 * 
 * USAGE:
 * ```javascript
 * // Initialize dev-tools module
 * const devTools = DevToolsModule.getInstance();
 * 
 * // Initialize workspace
 * devTools.initialize('#dev-tools-container');
 * 
 * // Create new module
 * devTools.createModule({
 *     id: 'my-module',
 *     name: 'My Module',
 *     type: 'dashboard'
 * });
 * 
 * // Load existing module
 * devTools.loadModule('existing-module-id');
 * ```
 * 
 * @module DevToolsModule
 * @version 3.0.0
 * @author Valor AI
 */

const DevToolsModule = (function () {
    'use strict';

    // ========================================
    // SINGLETON INSTANCE
    // ========================================
    let instance = null;

    // ========================================
    // DEFAULT CONFIGURATION
    // ========================================
    const DEFAULT_CONFIG = {
        apiBase: window.location.origin.includes('5001')
            ? window.location.origin
            : 'http://localhost:5001',
        monacoPath: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs',
        enableWebSocket: true,
        enableAutoSave: true,
        autoSaveInterval: 30000, // 30 seconds
        enableCredentialTesting: true,
        theme: 'vs-dark',
        enableLivePreview: true,
        previewUpdateDelay: 1000 // 1 second debounce
    };

    // ========================================
    // FILE TEMPLATES
    // ========================================
    const FILE_TEMPLATES = {
        html: `<!-- ${'{MODULE_NAME}'} Module HTML -->
<div class="module-container">
    <div class="module-header">
        <h2><i class="fas ${'{MODULE_ICON}'}"></i> ${'{MODULE_NAME}'}</h2>
        <p class="module-description">${'{MODULE_DESCRIPTION}'}</p>
    </div>
    
    <div class="module-content">
        <div class="content-section">
            <h3>Main Content</h3>
            <p>Your module content goes here...</p>
        </div>
    </div>
</div>`,

        js: `/**
 * ${'{MODULE_NAME}'} Module
 * Version: ${'{MODULE_VERSION}'}
 */

(function() {
    'use strict';
    
    // Module initialization
    function init() {
        console.log('${'{MODULE_NAME}'} initialized');
        
        // Your initialization code here
        setupEventListeners();
        loadData();
    }
    
    function setupEventListeners() {
        // Event listeners setup
    }
    
    function loadData() {
        // Data loading logic
    }
    
    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();`,

        css: `/* ${'{MODULE_NAME}'} Module Styles */

.module-container {
    padding: 20px;
    background: var(--bg-secondary, #1f2937);
    border-radius: 12px;
    max-width: 1200px;
    margin: 0 auto;
}

.module-header {
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-color, rgba(75, 85, 99, 0.6));
}

.module-header h2 {
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary, #e5e7eb);
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 0 8px 0;
}

.module-header h2 i {
    color: var(--accent-primary, #667eea);
}

.module-description {
    color: var(--text-secondary, #9ca3af);
    font-size: 14px;
    margin: 0;
}

.module-content {
    /* Your module content styles */
}

.content-section {
    background: var(--bg-primary, rgba(31, 41, 55, 0.6));
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 16px;
}

.content-section h3 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary, #e5e7eb);
    margin: 0 0 12px 0;
}`,

        routes: `/**
 * ${'{MODULE_NAME}'} Backend Routes
 */

from flask import Blueprint, request, jsonify

# Create blueprint
${'{MODULE_ID}'}_bp = Blueprint('${'{MODULE_ID}'}', __name__, url_prefix='/api/${'{MODULE_ID}'}')

@${'{MODULE_ID}'}_bp.route('/status', methods=['GET'])
def get_status():
    """Get module status"""
    return jsonify({
        'status': 'ok',
        'module': '${'{MODULE_NAME}'}',
        'version': '${'{MODULE_VERSION}'}'
    })

@${'{MODULE_ID}'}_bp.route('/data', methods=['GET'])
def get_data():
    """Get module data"""
    # Your data retrieval logic here
    return jsonify({
        'data': []
    })

@${'{MODULE_ID}'}_bp.route('/save', methods=['POST'])
def save_data():
    """Save module data"""
    data = request.json
    # Your save logic here
    return jsonify({
        'success': True,
        'message': 'Data saved successfully'
    })

# Export blueprint
__all__ = ['${'{MODULE_ID}'}_bp']`,

        manifest: `{
  "id": "${'{MODULE_ID}'}",
  "name": "${'{MODULE_NAME}'}",
  "version": "${'{MODULE_VERSION}'}",
  "description": "${'{MODULE_DESCRIPTION}'}",
  "icon": "${'{MODULE_ICON}'}",
  "author": "Valor AI",
  "type": "${'{MODULE_TYPE}'}",
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
  "permissions": {
    "api_access": true,
    "database_access": false,
    "file_access": false
  },
  "dependencies": [],
  "api_endpoints": [
    "/api/${'{MODULE_ID}'}/status",
    "/api/${'{MODULE_ID}'}/data",
    "/api/${'{MODULE_ID}'}/save"
  ],
  "created": "${'{TIMESTAMP}'}",
  "updated": "${'{TIMESTAMP}'}"
}`
    };

    // ========================================
    // MODULE TYPES
    // ========================================
    const MODULE_TYPES = {
        dashboard: {
            name: 'Dashboard Module',
            icon: 'fa-table-columns',
            description: 'Full-width dashboard component',
            template: 'dashboard'
        },
        sidebar: {
            name: 'Sidebar Module',
            icon: 'fa-sidebar',
            description: 'Collapsible sidebar panel',
            template: 'sidebar'
        },
        combo: {
            name: 'Dashboard + Sidebar',
            icon: 'fa-layer-group',
            description: 'Combined dashboard and sidebar',
            template: 'combo'
        },
        utility: {
            name: 'Utility Module',
            icon: 'fa-tools',
            description: 'Background service or utility',
            template: 'utility'
        }
    };

    // ========================================
    // DEV TOOLS CLASS
    // ========================================
    class DevTools {
        constructor(config = {}) {
            if (instance) {
                console.warn('[DevToolsModule] Instance already exists, returning existing instance');
                return instance;
            }

            this.config = { ...DEFAULT_CONFIG, ...config };
            this.editors = {
                html: null,
                js: null,
                css: null,
                routes: null,
                manifest: null
            };

            this.currentFile = 'html';
            this.moduleData = null;
            this.socket = null;
            this.autoSaveTimer = null;
            this.previewDebounce = null;
            this.initialized = false;
            this.container = null;

            // Credential testing integration
            this.testCredentials = new Map();

            instance = this;
        }

        /**
         * Get singleton instance
         * @static
         * @param {Object} config - Configuration object
         * @returns {DevTools} Singleton instance
         */
        static getInstance(config = {}) {
            if (!instance) {
                instance = new DevTools(config);
            }
            return instance;
        }

        /**
         * Initialize dev-tools workspace
         * @param {string|HTMLElement} containerSelector - Container selector or element
         * @returns {Promise<void>}
         */
        async initialize(containerSelector) {
            if (this.initialized) {
                console.warn('[DevToolsModule] Already initialized');
                return;
            }

            console.log('[DevToolsModule] Initializing workspace...');

            // Get container
            this.container = typeof containerSelector === 'string'
                ? document.querySelector(containerSelector)
                : containerSelector;

            if (!this.container) {
                throw new Error('[DevToolsModule] Container not found');
            }

            // Build workspace UI
            this._buildWorkspaceUI();

            // Load Monaco Editor
            await this._loadMonacoEditor();

            // Setup WebSocket if enabled
            if (this.config.enableWebSocket) {
                this._setupWebSocket();
            }

            // Setup auto-save if enabled
            if (this.config.enableAutoSave) {
                this._setupAutoSave();
            }

            // Setup keyboard shortcuts
            this._setupKeyboardShortcuts();

            this.initialized = true;
            console.log('[DevToolsModule] ✅ Workspace initialized');

            // Emit event
            this._emit('workspace:initialized', { container: this.container });
        }

        /**
         * Build workspace UI structure
         * @private
         */
        _buildWorkspaceUI() {
            this.container.innerHTML = `
                <div class="dev-tools-workspace">
                    <!-- Header -->
                    <div class="dev-tools-header">
                        <div class="header-left">
                            <h1><i class="fas fa-code"></i> Module Creator</h1>
                        </div>
                        <div class="header-actions">
                            <button id="ai-generate-btn" class="btn btn-ai" title="Generate code with AI">
                                <i class="fas fa-magic"></i> AI Generate
                            </button>
                            <button id="new-module-btn" class="btn btn-primary">
                                <i class="fas fa-plus"></i> New Module
                            </button>
                            <button id="load-module-btn" class="btn btn-secondary">
                                <i class="fas fa-folder-open"></i> Load
                            </button>
                            <button id="save-module-btn" class="btn btn-success">
                                <i class="fas fa-save"></i> Save
                            </button>
                            <button id="validate-btn" class="btn btn-info">
                                <i class="fas fa-check-circle"></i> Validate
                            </button>
                        </div>
                    </div>

                    <!-- Main Content -->
                    <div class="dev-tools-content">
                        <!-- Config Panel (Left) -->
                        <div class="config-panel">
                            <div class="panel-header">
                                <h3>Configuration</h3>
                            </div>
                            <div class="panel-content" id="config-form">
                                <!-- Config form will be injected here -->
                            </div>
                        </div>

                        <!-- Editor Panel (Center) -->
                        <div class="editor-panel">
                            <!-- File Tabs -->
                            <div class="file-tabs" id="file-tabs">
                                <div class="tab active" data-file="html">
                                    <i class="fab fa-html5"></i> HTML
                                </div>
                                <div class="tab" data-file="js">
                                    <i class="fab fa-js"></i> JavaScript
                                </div>
                                <div class="tab" data-file="css">
                                    <i class="fab fa-css3-alt"></i> CSS
                                </div>
                                <div class="tab" data-file="routes">
                                    <i class="fas fa-route"></i> Routes
                                </div>
                                <div class="tab" data-file="manifest">
                                    <i class="fas fa-file-code"></i> Manifest
                                </div>
                            </div>

                            <!-- Monaco Editor Container -->
                            <div id="monaco-container" class="monaco-container"></div>
                        </div>

                        <!-- Preview Panel (Right) -->
                        <div class="preview-panel">
                            <div class="panel-header">
                                <h3>Live Preview</h3>
                                <button id="refresh-preview-btn" class="btn-icon">
                                    <i class="fas fa-sync-alt"></i>
                                </button>
                            </div>
                            <div class="preview-content">
                                <iframe id="preview-iframe" sandbox="allow-scripts allow-same-origin"></iframe>
                            </div>
                        </div>
                    </div>

                    <!-- Console/Output Panel (Bottom) -->
                    <div class="console-panel">
                        <div class="console-header">
                            <h4><i class="fas fa-terminal"></i> Console Output</h4>
                            <button id="clear-console-btn" class="btn-icon">
                                <i class="fas fa-eraser"></i>
                            </button>
                        </div>
                        <div class="console-content" id="console-output"></div>
                    </div>
                </div>
            `;

            // Attach event listeners
            this._attachEventListeners();
        }

        /**
         * Attach event listeners to UI elements
         * @private
         */
        _attachEventListeners() {
            // Header buttons
            document.getElementById('ai-generate-btn')?.addEventListener('click', () => this.showAIPrompt());
            document.getElementById('new-module-btn')?.addEventListener('click', () => this.createNewModule());
            document.getElementById('load-module-btn')?.addEventListener('click', () => this.showLoadDialog());
            document.getElementById('save-module-btn')?.addEventListener('click', () => this.saveModule());
            document.getElementById('validate-btn')?.addEventListener('click', () => this.validateModule());

            // File tabs
            const tabs = document.querySelectorAll('.file-tabs .tab');
            tabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    const file = tab.dataset.file;
                    this.switchToFile(file);
                });
            });

            // Preview refresh
            document.getElementById('refresh-preview-btn')?.addEventListener('click', () => this.refreshPreview());

            // Console clear
            document.getElementById('clear-console-btn')?.addEventListener('click', () => this.clearConsole());
        }

        /**
         * Load Monaco Editor
         * @private
         * @returns {Promise<void>}
         */
        async _loadMonacoEditor() {
            return new Promise((resolve, reject) => {
                if (window.monaco) {
                    console.log('[DevToolsModule] Monaco already loaded');
                    this._initializeEditors();
                    resolve();
                    return;
                }

                const loader = document.createElement('script');
                loader.src = `${this.config.monacoPath}/loader.js`;
                loader.onload = () => {
                    require.config({ paths: { vs: this.config.monacoPath } });
                    require(['vs/editor/editor.main'], () => {
                        console.log('[DevToolsModule] ✅ Monaco Editor loaded');
                        this._initializeEditors();
                        resolve();
                    });
                };
                loader.onerror = () => {
                    console.error('[DevToolsModule] Failed to load Monaco Editor');
                    reject(new Error('Failed to load Monaco Editor'));
                };
                document.head.appendChild(loader);
            });
        }

        /**
         * Initialize Monaco editor instances
         * @private
         */
        _initializeEditors() {
            const container = document.getElementById('monaco-container');
            if (!container) return;

            // Create editor for HTML (visible by default)
            this.editors.html = monaco.editor.create(container, {
                value: FILE_TEMPLATES.html,
                language: 'html',
                theme: this.config.theme,
                automaticLayout: true,
                minimap: { enabled: false },
                fontSize: 14,
                wordWrap: 'on',
                formatOnPaste: true,
                formatOnType: true
            });

            // Listen to content changes for live preview
            this.editors.html.onDidChangeModelContent(() => {
                this._schedulePreviewUpdate();
            });

            console.log('[DevToolsModule] ✅ Monaco editors initialized');
        }

        /**
         * Switch to different file tab
         * @param {string} fileName - File name (html, js, css, routes, manifest)
         */
        switchToFile(fileName) {
            if (this.currentFile === fileName) return;

            console.log(`[DevToolsModule] Switching to ${fileName}`);

            // Update tab UI
            document.querySelectorAll('.file-tabs .tab').forEach(tab => {
                tab.classList.toggle('active', tab.dataset.file === fileName);
            });

            // Save current editor content
            if (this.editors[this.currentFile]) {
                const content = this.editors[this.currentFile].getValue();
                if (this.moduleData) {
                    this.moduleData.content = this.moduleData.content || {};
                    this.moduleData.content[this.currentFile] = content;
                }
            }

            // Switch editor or create if needed
            const container = document.getElementById('monaco-container');
            if (!container) return;

            // Dispose current editor if different language
            const languages = {
                html: 'html',
                js: 'javascript',
                css: 'css',
                routes: 'python',
                manifest: 'json'
            };

            if (!this.editors[fileName]) {
                // Create new editor for this file
                const content = this.moduleData?.content?.[fileName] || FILE_TEMPLATES[fileName] || '';
                this.editors[fileName] = monaco.editor.create(container, {
                    value: content,
                    language: languages[fileName],
                    theme: this.config.theme,
                    automaticLayout: true,
                    minimap: { enabled: false },
                    fontSize: 14,
                    wordWrap: 'on'
                });

                // Listen to changes
                this.editors[fileName].onDidChangeModelContent(() => {
                    if (fileName === 'html' || fileName === 'css' || fileName === 'js') {
                        this._schedulePreviewUpdate();
                    }
                });
            }

            // Hide all editors, show current
            Object.entries(this.editors).forEach(([key, editor]) => {
                if (editor) {
                    editor.getDomNode().style.display = key === fileName ? 'block' : 'none';
                }
            });

            this.currentFile = fileName;
            this._emit('file:switched', { fileName });
        }

        /**
         * Schedule preview update with debounce
         * @private
         */
        _schedulePreviewUpdate() {
            if (!this.config.enableLivePreview) return;

            clearTimeout(this.previewDebounce);
            this.previewDebounce = setTimeout(() => {
                this.refreshPreview();
            }, this.config.previewUpdateDelay);
        }

        /**
         * Refresh live preview
         */
        refreshPreview() {
            const iframe = document.getElementById('preview-iframe');
            if (!iframe) return;

            const html = this.editors.html?.getValue() || '';
            const css = this.editors.css?.getValue() || '';
            const js = this.editors.js?.getValue() || '';

            const previewContent = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1f2937;
            --text-primary: #e5e7eb;
            --text-secondary: #9ca3af;
            --accent-primary: #667eea;
            --border-color: rgba(75, 85, 99, 0.6);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            padding: 20px;
        }
        ${css}
    </style>
</head>
<body>
    ${html}
    <script>${js}</script>
</body>
</html>
            `;

            iframe.srcdoc = previewContent;
            this.log('Preview updated', 'info');
        }

        /**
         * Create new module
         */
        createNewModule() {
            // Show new module dialog
            const moduleId = prompt('Enter module ID (lowercase, no spaces):');
            if (!moduleId) return;

            const moduleName = prompt('Enter module name:');
            if (!moduleName) return;

            const moduleType = prompt('Enter module type (dashboard/sidebar/combo/utility):', 'dashboard');

            this.moduleData = {
                id: moduleId,
                name: moduleName,
                version: '1.0.0',
                description: `${moduleName} module`,
                icon: 'fas fa-cube',
                type: moduleType,
                files: {
                    html: true,
                    js: true,
                    css: true,
                    routes: false
                },
                content: {}
            };

            // Load templates with module data
            this._loadTemplates();
            this.log(`Created new module: ${moduleName}`, 'success');
            this._emit('module:created', { moduleData: this.moduleData });
        }

        /**
         * Load templates for current module
         * @private
         */
        _loadTemplates() {
            if (!this.moduleData) return;

            const replacements = {
                '{MODULE_ID}': this.moduleData.id,
                '{MODULE_NAME}': this.moduleData.name,
                '{MODULE_VERSION}': this.moduleData.version,
                '{MODULE_DESCRIPTION}': this.moduleData.description,
                '{MODULE_ICON}': this.moduleData.icon,
                '{MODULE_TYPE}': this.moduleData.type,
                '{TIMESTAMP}': new Date().toISOString()
            };

            Object.entries(FILE_TEMPLATES).forEach(([fileName, template]) => {
                let content = template;
                Object.entries(replacements).forEach(([key, value]) => {
                    content = content.replace(new RegExp(key, 'g'), value);
                });

                if (this.editors[fileName]) {
                    this.editors[fileName].setValue(content);
                }
                this.moduleData.content = this.moduleData.content || {};
                this.moduleData.content[fileName] = content;
            });

            this.refreshPreview();
        }

        /**
         * Save module
         */
        async saveModule() {
            if (!this.moduleData) {
                this.log('No module to save', 'error');
                return;
            }

            // Collect current content
            Object.entries(this.editors).forEach(([fileName, editor]) => {
                if (editor) {
                    this.moduleData.content = this.moduleData.content || {};
                    this.moduleData.content[fileName] = editor.getValue();
                }
            });

            try {
                const response = await fetch(`${this.config.apiBase}/api/dev-tools/save-module`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.moduleData)
                });

                const result = await response.json();

                if (result.success) {
                    this.log('Module saved successfully', 'success');
                    this._emit('module:saved', { moduleData: this.moduleData });
                } else {
                    this.log(`Save failed: ${result.error}`, 'error');
                }
            } catch (error) {
                this.log(`Save error: ${error.message}`, 'error');
            }
        }

        /**
         * Validate module
         */
        async validateModule() {
            if (!this.moduleData) {
                this.log('No module to validate', 'error');
                return;
            }

            this.log('Validating module...', 'info');

            const validationResults = {
                passed: true,
                errors: [],
                warnings: []
            };

            // Validate manifest
            try {
                const manifestContent = this.editors.manifest?.getValue();
                if (manifestContent) {
                    JSON.parse(manifestContent);
                }
            } catch (e) {
                validationResults.passed = false;
                validationResults.errors.push('Invalid manifest JSON');
            }

            // Validate HTML
            const htmlContent = this.editors.html?.getValue() || '';
            if (!htmlContent.includes('module-container')) {
                validationResults.warnings.push('HTML should include .module-container class');
            }

            // Validate JS
            const jsContent = this.editors.js?.getValue() || '';
            if (!jsContent.includes('function') && !jsContent.includes('=>')) {
                validationResults.warnings.push('JavaScript file appears empty');
            }

            // Output results
            if (validationResults.passed) {
                this.log('✅ Module validation passed', 'success');
            } else {
                this.log('❌ Module validation failed', 'error');
            }

            validationResults.errors.forEach(err => this.log(`  - ${err}`, 'error'));
            validationResults.warnings.forEach(warn => this.log(`  - ${warn}`, 'warn'));

            this._emit('module:validated', validationResults);
        }

        /**
         * Show AI prompt dialog for code generation
         */
        showAIPrompt() {
            // Replace modal with chat input area below console
            const existingChat = document.getElementById('ai-chat-area');
            if (existingChat) {
                existingChat.style.display = 'block';
                document.getElementById('ai-chat-input')?.focus();
                return;
            }

            const chatHtml = `
                <div id="ai-chat-area" class="ai-chat-area">
                    <div class="ai-chat-header">
                        <h4><i class="fas fa-robot"></i> AI Code Generator</h4>
                        <button class="btn-icon" onclick="document.getElementById('ai-chat-area').style.display='none'" title="Close">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="ai-input-group">
                        <textarea 
                            id="ai-chat-input" 
                            placeholder="Describe what you want to build: e.g., 'Create a task management dashboard with kanban board...'"
                            rows="3"
                        ></textarea>
                        <button id="ai-send-btn" class="btn btn-primary">
                            <i class="fas fa-paper-plane"></i> Generate
                        </button>
                    </div>
                    <div class="ai-options">
                        <label>
                            <input type="checkbox" id="ai-include-context" checked>
                            <span>Include current module context</span>
                        </label>
                        <label>
                            <input type="checkbox" id="ai-show-thinking" checked>
                            <span>Show AI thinking</span>
                        </label>
                    </div>
                </div>
            `;

            // Insert after console panel
            const consolePanel = document.querySelector('.console-panel');
            if (consolePanel) {
                consolePanel.insertAdjacentHTML('afterend', chatHtml);

                // Focus textarea
                setTimeout(() => document.getElementById('ai-chat-input')?.focus(), 100);

                // Handle send button
                document.getElementById('ai-send-btn')?.addEventListener('click', () => {
                    this.generateWithAI();
                });

                // Handle Enter key (Shift+Enter for new line)
                document.getElementById('ai-chat-input')?.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        this.generateWithAI();
                    }
                });
            }
        }

        /**
         * Generate code using AI
         */
        async generateWithAI() {
            const prompt = document.getElementById('ai-chat-input')?.value.trim();
            const includeContext = document.getElementById('ai-include-context')?.checked;
            const showThinking = document.getElementById('ai-show-thinking')?.checked;

            if (!prompt) {
                this.log('⚠️ Please enter a prompt describing what you want to build', 'warning');
                return;
            }

            // Clear input
            const input = document.getElementById('ai-chat-input');
            if (input) input.value = '';

            // Disable send button during generation
            const sendBtn = document.getElementById('ai-send-btn');
            if (sendBtn) {
                sendBtn.disabled = true;
                sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            }

            // Build context
            let fullPrompt = prompt;
            if (includeContext && this.currentModule) {
                fullPrompt = `${prompt}

Current Module Context:
- ID: ${this.currentModule.id}
- Name: ${this.currentModule.name}
- Type: ${this.currentModule.type}
- Icon: ${this.currentModule.icon}
- Description: ${this.currentModule.description}

Generate complete code files (HTML, JavaScript, CSS, Python routes, and manifest.json).`;
            }

            this.log('🤖 AI is generating code...', 'info');
            this.log(`Prompt: ${prompt}`, 'info');

            try {
                const response = await fetch(`${this.config.apiBase}/api/agent/stream`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'text/event-stream'
                    },
                    body: JSON.stringify({
                        agent_id: 'dev_tools_agent',
                        message: fullPrompt,
                        stream: true,
                        enable_thinking: showThinking
                    })
                });

                if (!response.ok) {
                    throw new Error(`AI request failed: ${response.status} ${response.statusText}`);
                }

                // Stream response
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                let accumulatedCode = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop() || '';

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));

                                if (data.type === 'thinking' && showThinking) {
                                    this.log(`💭 ${data.content}`, 'thinking');
                                } else if (data.type === 'tool_use') {
                                    this.log(`🔧 Using tool: ${data.tool_name}`, 'tool');
                                } else if (data.type === 'text' || data.type === 'content') {
                                    const text = data.content || data.text || '';
                                    accumulatedCode += text;
                                    // Append to current editor
                                    this._appendToEditor(text);
                                } else if (data.type === 'done') {
                                    this.log('✅ AI code generation complete!', 'success');
                                }
                            } catch (e) {
                                // Ignore JSON parse errors
                            }
                        }
                    }
                }

                this.log('✅ Code generation finished. Review and edit as needed.', 'success');

            } catch (error) {
                this.log(`❌ AI generation failed: ${error.message}`, 'error');
                this.log('Make sure Flask backend is running on http://localhost:5001', 'warning');
            } finally {
                // Re-enable send button
                const sendBtn = document.getElementById('ai-send-btn');
                if (sendBtn) {
                    sendBtn.disabled = false;
                    sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Generate';
                }
            }
        }

        /**
         * Append text to current editor
         * @private
         */
        _appendToEditor(text) {
            if (!this.editor) return;

            const model = this.editor.getModel();
            if (!model) return;

            const lastLine = model.getLineCount();
            const lastColumn = model.getLineMaxColumn(lastLine);

            // Insert text at end
            this.editor.executeEdits('ai-generation', [{
                range: new monaco.Range(lastLine, lastColumn, lastLine, lastColumn),
                text: text
            }]);

            // Scroll to bottom
            this.editor.revealLine(model.getLineCount());
        }

        /**
         * Show load module dialog
         */
        async showLoadDialog() {
            try {
                // Fetch list of available modules from UI/modules_external
                this.log('Fetching module list from API...', 'info');
                const response = await fetch(`${this.config.apiBase}/api/modules/list`);

                if (!response.ok) {
                    this.log(`API returned ${response.status}: ${response.statusText}`, 'error');
                    // Fallback: show manual input if API not available
                    this._showManualLoadDialog();
                    return;
                }

                const data = await response.json();
                const modules = data.modules || data;
                this.log(`Found ${modules.length} modules`, 'success');

                // Build module selection dialog
                const dialogHtml = `
                    <div class="modal-overlay" id="load-module-overlay">
                        <div class="modal-dialog">
                            <div class="modal-header">
                                <h3><i class="fas fa-folder-open"></i> Load Existing Module</h3>
                                <button class="modal-close" onclick="document.getElementById('load-module-overlay').remove()">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                            <div class="modal-body">
                                <div class="module-list">
                                    ${modules.map(mod => `
                                        <div class="module-item" data-module-id="${mod.id}">
                                            <div class="module-icon">
                                                <i class="fas ${mod.icon || 'fa-cube'}"></i>
                                            </div>
                                            <div class="module-info">
                                                <div class="module-name">${mod.name}</div>
                                                <div class="module-type">${mod.type}</div>
                                                <div class="module-desc">${mod.description || 'No description'}</div>
                                            </div>
                                            <button class="btn btn-primary btn-sm" onclick="window.devToolsLoadModule('${mod.id}')">
                                                <i class="fas fa-download"></i> Load
                                            </button>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button class="btn btn-secondary" onclick="document.getElementById('load-module-overlay').remove()">
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                `;

                // Inject dialog into page
                document.body.insertAdjacentHTML('beforeend', dialogHtml);

                // Store reference for load function
                window.devToolsLoadModule = (moduleId) => {
                    this._loadModuleById(moduleId);
                    document.getElementById('load-module-overlay').remove();
                };

            } catch (error) {
                this.log(`Failed to load module list: ${error.message}`, 'error');
                // Fallback to manual input
                this._showManualLoadDialog();
            }
        }

        /**
         * Show manual module ID input dialog
         * @private
         */
        _showManualLoadDialog() {
            const moduleId = prompt('Enter module ID to load (e.g., "inhouse-kanban"):');
            if (moduleId && moduleId.trim()) {
                this._loadModuleById(moduleId.trim());
            }
        }

        /**
         * Load module by ID from server
         * @private
         */
        async _loadModuleById(moduleId) {
            try {
                this.log(`Loading module: ${moduleId}...`, 'info');

                const response = await fetch(`${this.config.apiBase}/api/modules/${moduleId}/files`);

                if (!response.ok) {
                    throw new Error(`Module not found: ${moduleId}`);
                }

                const moduleData = await response.json();

                // Load module data into editor
                this.currentModule = {
                    id: moduleId,
                    name: moduleData.name || moduleId,
                    type: moduleData.type || 'dashboard',
                    icon: moduleData.icon || 'fa-cube',
                    description: moduleData.description || '',
                    version: moduleData.version || '1.0.0'
                };

                // Update config panel
                document.getElementById('module-id').value = this.currentModule.id;
                document.getElementById('module-name').value = this.currentModule.name;
                document.getElementById('module-type').value = this.currentModule.type;
                document.getElementById('module-icon').value = this.currentModule.icon;
                document.getElementById('module-description').value = this.currentModule.description;

                // Load file contents into tabs
                if (moduleData.files) {
                    // Load HTML
                    if (moduleData.files.html) {
                        this.files['html'].content = moduleData.files.html;
                        if (this.activeFile === 'html' && this.editor) {
                            this.editor.setValue(moduleData.files.html);
                        }
                    }

                    // Load JavaScript
                    if (moduleData.files.js) {
                        this.files['js'].content = moduleData.files.js;
                        if (this.activeFile === 'js' && this.editor) {
                            this.editor.setValue(moduleData.files.js);
                        }
                    }

                    // Load CSS
                    if (moduleData.files.css) {
                        this.files['css'].content = moduleData.files.css;
                        if (this.activeFile === 'css' && this.editor) {
                            this.editor.setValue(moduleData.files.css);
                        }
                    }

                    // Load Routes
                    if (moduleData.files.routes) {
                        this.files['routes'].content = moduleData.files.routes;
                        if (this.activeFile === 'routes' && this.editor) {
                            this.editor.setValue(moduleData.files.routes);
                        }
                    }

                    // Load Manifest
                    if (moduleData.files.manifest) {
                        this.files['manifest'].content = moduleData.files.manifest;
                        if (this.activeFile === 'manifest' && this.editor) {
                            this.editor.setValue(moduleData.files.manifest);
                        }
                    }
                }

                // Update preview
                this.updatePreview();

                this.log(`✅ Module loaded: ${moduleData.name}`, 'success');

            } catch (error) {
                this.log(`❌ Failed to load module: ${error.message}`, 'error');
            }
        }

        /**
         * Setup WebSocket connection
         * @private
         */
        _setupWebSocket() {
            // TODO: Implement WebSocket for real-time sync
            console.log('[DevToolsModule] WebSocket support - coming soon');
        }

        /**
         * Setup auto-save timer
         * @private
         */
        _setupAutoSave() {
            this.autoSaveTimer = setInterval(() => {
                if (this.moduleData) {
                    this.saveModule();
                }
            }, this.config.autoSaveInterval);

            console.log('[DevToolsModule] Auto-save enabled');
        }

        /**
         * Setup keyboard shortcuts
         * @private
         */
        _setupKeyboardShortcuts() {
            document.addEventListener('keydown', (e) => {
                // Ctrl+S / Cmd+S - Save
                if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                    e.preventDefault();
                    this.saveModule();
                }

                // Alt+Shift+F - Format
                if (e.altKey && e.shiftKey && e.key === 'F') {
                    e.preventDefault();
                    this.formatCode();
                }

                // Ctrl+P - Preview
                if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
                    e.preventDefault();
                    this.refreshPreview();
                }
            });

            console.log('[DevToolsModule] Keyboard shortcuts enabled');
        }

        /**
         * Format current editor code
         */
        formatCode() {
            const editor = this.editors[this.currentFile];
            if (editor) {
                editor.getAction('editor.action.formatDocument').run();
                this.log('Code formatted', 'success');
            }
        }

        /**
         * Log message to console
         * @param {string} message - Message text
         * @param {string} type - Log type (info/success/warn/error)
         */
        log(message, type = 'info') {
            const consoleOutput = document.getElementById('console-output');
            if (!consoleOutput) return;

            const timestamp = new Date().toLocaleTimeString();
            const icons = {
                info: 'fa-info-circle',
                success: 'fa-check-circle',
                warn: 'fa-exclamation-triangle',
                error: 'fa-times-circle'
            };

            const colors = {
                info: '#3b82f6',
                success: '#10b981',
                warn: '#f59e0b',
                error: '#ef4444'
            };

            const entry = document.createElement('div');
            entry.className = 'console-entry';
            entry.innerHTML = `
                <span class="timestamp">[${timestamp}]</span>
                <i class="fas ${icons[type]}" style="color: ${colors[type]}"></i>
                <span class="message">${message}</span>
            `;

            consoleOutput.appendChild(entry);
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        }

        /**
         * Clear console output
         */
        clearConsole() {
            const consoleOutput = document.getElementById('console-output');
            if (consoleOutput) {
                consoleOutput.innerHTML = '';
            }
        }

        /**
         * Emit custom event
         * @private
         * @param {string} eventName - Event name
         * @param {Object} detail - Event detail data
         */
        _emit(eventName, detail) {
            const event = new CustomEvent(eventName, { detail });
            document.dispatchEvent(event);
        }

        /**
         * Destroy instance and clean up
         */
        destroy() {
            // Dispose Monaco editors
            Object.values(this.editors).forEach(editor => {
                if (editor) editor.dispose();
            });

            // Clear timers
            if (this.autoSaveTimer) {
                clearInterval(this.autoSaveTimer);
            }
            if (this.previewDebounce) {
                clearTimeout(this.previewDebounce);
            }

            // Close WebSocket
            if (this.socket) {
                this.socket.close();
            }

            this.initialized = false;
            instance = null;

            console.log('[DevToolsModule] Destroyed');
        }
    }

    // ========================================
    // PUBLIC API
    // ========================================
    return {
        getInstance: DevTools.getInstance,
        MODULE_TYPES,
        FILE_TEMPLATES
    };
})();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DevToolsModule;
}

// Make globally available
window.DevToolsModule = DevToolsModule;
