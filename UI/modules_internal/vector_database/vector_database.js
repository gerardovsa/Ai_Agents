/**
 * Vector Database Sidebar - Modern Framework Edition
 * 
 * PURPOSE: Vector database management with Pinecone cloud integration
 * FRAMEWORK: Pre-loaded script pattern (like Synergy module)
 * PATTERN: Window assignment (not ES6 export - must work with <script> tags)
 * 
 * FEATURES:
 * - Credential management (Pinecone + OpenAI + Voyager)
 * - Document upload and processing (PDF, DOCX, TXT, MD)
 * - Vector database operations (query, upsert, delete)
 * - AI-controlled semantic search
 * - Namespace isolation
 * 
 * DEPENDENCIES:
 * - Utilities: dom, api, storage, events, log (injected)
 * - Backend: /api/vector-db/* endpoints
 * - AI Tools: 8 Pinecone tools via registry
 * 
 * LAST MODIFIED: 2025-12-08 - Removed ES6 export, using window assignment
 */

window.VectorDatabaseModule = {
    // ==================== STATE ====================
    state: {
        API_BASE_URL: window.API_BASE_URL || 'http://localhost:5001',
        currentTab: 'credentials',
        uploadedFiles: [],
        isConnected: false,
        selectedProvider: 'pinecone', // pinecone, voyager, pgvector, qdrant
        qdrantDeploymentType: 'customer-server', // customer-server, valor-cloud, qdrant-cloud
        qdrantConnection: { host: 'localhost', port: 6333, api_key: '' },
        multiModalEnabled: false, // Image+Text+Audio+Video embeddings
        quantizationEnabled: false, // Binary/Scalar/Product quantization (4-32x compression)
        hybridSearchEnabled: false, // Dense+Sparse BM25 hybrid search
        stats: {
            documents: 0,
            vectors: 0,
            namespaces: 0,
            collections: 0,
            indexed_vectors: 0
        },
        loading: false,
        error: null,
        initialized: false
    },

    // ==================== LIFECYCLE HOOKS ====================

    /**
     * Called once when module first loads
     */
    async onLoad(utilities) {
        Object.assign(this, utilities);
        this.log.info('[VECTOR DB] Module loading...');

        // Load saved preferences
        const savedTab = this.storage.get('vector_db_current_tab');
        if (savedTab) {
            this.state.currentTab = savedTab;
        }

        this.state.initialized = true;
        this.log.info('[VECTOR DB] Module loaded successfully');
    },

    /**
     * Called when sidebar is opened
     */
    async onSidebarLoad(utilities) {
        Object.assign(this, utilities);
        this.log.info('[VECTOR DB] Sidebar loading...');

        // Get container
        this.container = this.dom.getContainer();

        if (!this.container) {
            this.log.error('[VECTOR DB] Container not found');
            return;
        }

        // Load HTML template if container is empty
        if (!this.container.innerHTML || this.container.innerHTML.trim() === '' ||
            this.container.innerHTML.includes('Content loaded dynamically')) {
            try {
                const htmlPath = '/modules_internal/vector_database/vector_database.html';
                const response = await fetch(htmlPath);
                if (response.ok) {
                    const html = await response.text();
                    this.container.innerHTML = html;
                    this.log.info('[VECTOR DB] HTML template loaded');
                } else {
                    this.log.error('[VECTOR DB] Failed to load HTML template');
                    return;
                }
            } catch (error) {
                this.log.error('[VECTOR DB] Error loading HTML template:', error);
                return;
            }
        }

        // Setup event listeners (tracked automatically by framework)
        this.setupEventListeners();

        // Load saved credentials and check connection status
        await this.loadCredentials();
        await this.checkConnectionStatus();

        // Load stats if connected
        if (this.state.isConnected) {
            await this.loadStats();
        }

        // Switch to saved tab
        this.switchTab(this.state.currentTab);

        this.log.info('[VECTOR DB] Sidebar loaded successfully');
    },

    /**
     * Called when sidebar is opened (after initial load)
     */
    async onOpen(utilities) {
        Object.assign(this, utilities);
        this.log.info('[VECTOR DB] Sidebar opened');
        
        // Refresh data when sidebar opens
        await this.refresh();
    },

    /**
     * Called when module is unloaded
     */
    onUnload(utilities) {
        Object.assign(this, utilities);
        this.log.info('[VECTOR DB] Module unloading...');

        // Save current tab
        this.storage.set('vector_db_current_tab', this.state.currentTab);

        // Framework automatically cleans up tracked event listeners
        this.log.info('[VECTOR DB] Module unloaded successfully');
    },

    // ==================== EVENT LISTENERS ====================

    setupEventListeners() {
        // Credential form submission
        this.dom.on(this.container, 'submit', '#credential-form', (e) => {
            e.preventDefault();
            this.saveCredentials();
        });

        // File upload zone click
        this.dom.on(this.container, 'click', '#upload-zone', (e) => {
            if (e.target.id !== 'file-input') {
                document.getElementById('file-input')?.click();
            }
        });

        // Drag and drop
        this.dom.on(this.container, 'dragover', '#upload-zone', (e) => {
            e.preventDefault();
            e.currentTarget.classList.add('drag-over');
        });

        this.dom.on(this.container, 'dragleave', '#upload-zone', (e) => {
            e.currentTarget.classList.remove('drag-over');
        });

        this.dom.on(this.container, 'drop', '#upload-zone', (e) => {
            e.preventDefault();
            e.currentTarget.classList.remove('drag-over');
            const files = Array.from(e.dataTransfer.files);
            this.handleFileSelect(files);
        });

        // File input change
        this.dom.on(this.container, 'change', '#file-input', (e) => {
            const files = Array.from(e.target.files);
            this.handleFileSelect(files);
        });

        // Tab switching
        this.dom.on(this.container, 'click', '.vector-db-tab', (e) => {
            const tabName = e.currentTarget.dataset.tab;
            if (tabName) {
                this.switchTab(tabName);
            }
        });

        // Test connection button
        this.dom.on(this.container, 'click', '[data-action="test-connection"]', () => {
            this.testConnection();
        });

        // Process files button
        this.dom.on(this.container, 'click', '[data-action="process-files"]', () => {
            this.processFiles();
        });

        // Refresh button
        this.dom.on(this.container, 'click', '[data-action="refresh"]', () => {
            this.refresh();
        });

        // Embedding provider change
        this.dom.on(this.container, 'change', '#embedding-provider', () => {
            this.onEmbeddingProviderChange();
        });

        // Provider selector change (Pinecone/Qdrant/etc)
        this.dom.on(this.container, 'change', '#provider-selector', (e) => {
            this.onProviderChange(e);
        });

        // Qdrant deployment type change
        this.dom.on(this.container, 'change', '#qdrant-deployment-type', (e) => {
            this.onQdrantDeploymentTypeChange(e);
        });

        // Deploy Qdrant Docker button
        this.dom.on(this.container, 'click', '#deploy-docker-btn', () => {
            this.deployQdrantDocker();
        });

        // Test Qdrant connection button
        this.dom.on(this.container, 'click', '#test-qdrant-connection-btn', () => {
            this.testQdrantConnection();
        });

        // Advanced feature toggles
        this.dom.on(this.container, 'change', '#multi-modal-toggle', (e) => {
            this.onMultiModalToggle(e);
        });

        this.dom.on(this.container, 'change', '#quantization-toggle', (e) => {
            this.onQuantizationToggle(e);
        });

        this.dom.on(this.container, 'change', '#hybrid-search-toggle', (e) => {
            this.onHybridSearchToggle(e);
        });

        // Save embedding config button
        this.dom.on(this.container, 'click', '[data-action="save-embedding-config"]', () => {
            this.saveEmbeddingConfig();
        });

        this.log.info('[VECTOR DB] Event listeners setup complete');
    },

    // ==================== CREDENTIAL MANAGEMENT ====================

    async saveCredentials() {
        const apiKey = this.container.querySelector('#api-key')?.value.trim();
        const indexName = this.container.querySelector('#index-name')?.value.trim();
        const environment = this.container.querySelector('#environment')?.value.trim();
        const namespace = this.container.querySelector('#namespace')?.value.trim();

        if (!apiKey || !indexName || !environment) {
            this.showMessage('Please fill all required fields', 'error');
            return;
        }

        try {
            this.showMessage('Saving credentials...', 'loading');

            const response = await this.api.post(`${this.state.API_BASE_URL}/api/vector-db/credentials/save`, {
                api_key: apiKey,
                index_name: indexName,
                environment: environment,
                namespace: namespace || ''
            });

            if (response.success) {
                this.showMessage('Credentials saved successfully', 'success');
                this.state.isConnected = true;
                this.updateConnectionStatus(true);
                await this.loadStats();
            } else {
                this.showMessage(`Error: ${response.error}`, 'error');
            }
        } catch (error) {
            this.log.error('[VECTOR DB] Save credentials error:', error);
            this.showMessage('Failed to save credentials', 'error');
        }
    },

    async loadCredentials() {
        try {
            const provider = this.state.selectedProvider;
            const response = await this.api.get(
                `${this.state.API_BASE_URL}/api/vector-db/credentials/load?provider=${provider}`
            );

            if (response.success && response.credentials) {
                const creds = response.credentials[provider];
                
                if (creds) {
                    const indexInput = this.container.querySelector('#index-name');
                    const envInput = this.container.querySelector('#environment');
                    const nsInput = this.container.querySelector('#namespace');

                    if (indexInput) indexInput.value = creds.index_name || '';
                    if (envInput) envInput.value = creds.environment || '';
                    if (nsInput) nsInput.value = creds.namespace || '';

                    this.state.isConnected = true;
                    this.updateConnectionStatus(true);
                    this.showConnectedBanner(creds);
                    this.log.info(`[VECTOR DB] ${provider} credentials loaded`);
                } else {
                    this.state.isConnected = false;
                    this.updateConnectionStatus(false);
                    this.showNotConfiguredBanner();
                }
            } else {
                this.state.isConnected = false;
                this.updateConnectionStatus(false);
                this.showNotConfiguredBanner();
            }

            // Load embedding configuration
            await this.loadEmbeddingConfig();
        } catch (error) {
            this.log.error('[VECTOR DB] Load credentials error:', error);
            this.state.isConnected = false;
            this.updateConnectionStatus(false);
            this.showNotConfiguredBanner();
        }
    },

    async checkConnectionStatus() {
        try {
            const provider = this.state.selectedProvider;
            this.log.info(`[VECTOR DB] Testing ${provider} connection...`);
            
            const response = await this.api.get(
                `${this.state.API_BASE_URL}/api/vector-db/credentials/status?provider=${provider}`
            );

            if (response.success && response.connected) {
                this.state.isConnected = true;
                
                // Update stats if provider returned them
                if (response.stats) {
                    this.state.stats.vectors = response.stats.total_vectors || 0;
                    this.state.stats.namespaces = response.stats.namespaces || 0;
                    this.updateStatsUI();
                }
                
                this.showConnectedBanner({
                    index_name: response.index_name,
                    environment: response.environment,
                    provider: provider
                });
                
                this.log.info(`[VECTOR DB] ${provider} connected successfully`);
            } else {
                this.state.isConnected = false;
                this.showNotConfiguredBanner();
                this.log.warn(`[VECTOR DB] ${provider} not connected: ${response.error}`);
            }
        } catch (error) {
            this.log.error('[VECTOR DB] Check connection status error:', error);
            this.state.isConnected = false;
            this.showNotConfiguredBanner();
        }
    },

    showConnectedBanner(credentials) {
        const connectedBanner = this.container.querySelector('#credential-connected-banner');
        const notConfiguredBanner = this.container.querySelector('#credential-status-banner');

        if (connectedBanner) connectedBanner.style.display = 'block';
        if (notConfiguredBanner) notConfiguredBanner.style.display = 'none';

        // Populate banner fields
        const indexName = this.container.querySelector('#banner-index-name');
        const environment = this.container.querySelector('#banner-environment');
        const embeddingProvider = this.container.querySelector('#banner-embedding-provider');
        const embeddingModel = this.container.querySelector('#banner-embedding-model');

        const provider = credentials.provider || this.state.selectedProvider;
        const providerDisplay = provider.charAt(0).toUpperCase() + provider.slice(1);

        if (indexName) indexName.textContent = credentials.index_name || '-';
        if (environment) environment.textContent = credentials.environment || '-';
        if (embeddingProvider) embeddingProvider.textContent = providerDisplay;
        if (embeddingModel) embeddingModel.textContent = credentials.model || credentials.embedding_model || 'ada-002';
    },

    showNotConfiguredBanner() {
        const connectedBanner = this.container.querySelector('#credential-connected-banner');
        const notConfiguredBanner = this.container.querySelector('#credential-status-banner');

        if (connectedBanner) connectedBanner.style.display = 'none';
        if (notConfiguredBanner) notConfiguredBanner.style.display = 'block';
    },

    async loadEmbeddingConfig() {
        try {
            const response = await this.api.get(
                `${this.state.API_BASE_URL}/api/vector-db/embedding-config/get`
            );

            if (response.success && response.config) {
                const config = response.config;
                const provider = config.provider || '';

                const providerSelect = this.container.querySelector('#embedding-provider');
                if (providerSelect) {
                    providerSelect.value = provider;
                    this.onEmbeddingProviderChange();
                }

                if (provider === 'voyager' && config.model) {
                    const modelSelect = this.container.querySelector('#voyager-model');
                    if (modelSelect) modelSelect.value = config.model;
                } else if (provider === 'openai' && config.model) {
                    const modelSelect = this.container.querySelector('#openai-model');
                    if (modelSelect) modelSelect.value = config.model;
                }

                this.log.info('[VECTOR DB] Embedding config loaded:', provider);
            }
        } catch (error) {
            this.log.error('[VECTOR DB] Load embedding config error:', error);
        }
    },

    async testConnection() {
        try {
            this.showMessage('Testing connection...', 'loading');

            const response = await this.api.post(`${this.state.API_BASE_URL}/api/vector-db/test-connection`, {});

            if (response.success) {
                this.showMessage(`Connected! ${response.message}`, 'success');
                this.state.isConnected = true;
                this.updateConnectionStatus(true);
                await this.loadStats();
            } else {
                this.showMessage(`Connection failed: ${response.error}`, 'error');
                this.state.isConnected = false;
                this.updateConnectionStatus(false);
            }
        } catch (error) {
            this.log.error('[VECTOR DB] Test connection error:', error);
            this.showMessage('Connection test failed', 'error');
            this.state.isConnected = false;
            this.updateConnectionStatus(false);
        }
    },

    updateConnectionStatus(connected) {
        const statusEl = this.container.querySelector('#connection-status');
        if (statusEl) {
            if (connected) {
                statusEl.textContent = 'Connected';
                statusEl.className = 'credential-status connected';
            } else {
                statusEl.textContent = 'Disconnected';
                statusEl.className = 'credential-status disconnected';
            }
        }
    },

    // ==================== EMBEDDING CONFIGURATION ====================

    onEmbeddingProviderChange() {
        const provider = this.container.querySelector('#embedding-provider')?.value;

        const voyagerConfig = this.container.querySelector('#voyager-config');
        const openaiConfig = this.container.querySelector('#openai-config');

        if (voyagerConfig) voyagerConfig.style.display = 'none';
        if (openaiConfig) openaiConfig.style.display = 'none';

        if (provider === 'voyager' && voyagerConfig) {
            voyagerConfig.style.display = 'block';
        } else if (provider === 'openai' && openaiConfig) {
            openaiConfig.style.display = 'block';
        }

        this.log.info('[VECTOR DB] Embedding provider changed:', provider);
    },

    async saveEmbeddingConfig() {
        const provider = this.container.querySelector('#embedding-provider')?.value;

        if (!provider) {
            this.showEmbeddingMessage('Please select an embedding provider', 'error');
            return;
        }

        let apiKey, model, platform;

        if (provider === 'voyager') {
            apiKey = this.container.querySelector('#voyager-api-key')?.value.trim();
            model = this.container.querySelector('#voyager-model')?.value;
            platform = 'voyager';

            if (!apiKey) {
                this.showEmbeddingMessage('Please enter Voyager API key', 'error');
                return;
            }
        } else if (provider === 'openai') {
            apiKey = this.container.querySelector('#openai-api-key')?.value.trim();
            model = this.container.querySelector('#openai-model')?.value;
            platform = 'openai_embeddings';

            if (!apiKey) {
                this.showEmbeddingMessage('Please enter OpenAI API key', 'error');
                return;
            }
        }

        try {
            this.showEmbeddingMessage('Saving embedding configuration...', 'loading');

            const response = await this.api.post(`${this.state.API_BASE_URL}/api/vector-db/embedding-config/save`, {
                provider: provider,
                platform: platform,
                api_key: apiKey,
                model: model,
                metadata: {
                    provider: provider,
                    model: model,
                    dimensions: provider === 'voyager' ? 1536 : this.getOpenAIDimensions(model)
                }
            });

            if (response.success) {
                this.showEmbeddingMessage(
                    `${provider === 'voyager' ? 'Voyager' : 'OpenAI'} configuration saved successfully`,
                    'success'
                );
            } else {
                this.showEmbeddingMessage(`Error: ${response.error}`, 'error');
            }
        } catch (error) {
            this.log.error('[VECTOR DB] Save embedding config error:', error);
            this.showEmbeddingMessage('Failed to save configuration', 'error');
        }
    },

    getOpenAIDimensions(model) {
        switch (model) {
            case 'text-embedding-3-large':
                return 3072;
            case 'text-embedding-3-small':
            case 'text-embedding-ada-002':
            default:
                return 1536;
        }
    },

    showEmbeddingMessage(message, type) {
        const messageEl = this.container.querySelector('#embedding-message');
        if (!messageEl) return;

        messageEl.textContent = message;
        messageEl.className = `message-${type}`;
        messageEl.style.display = 'block';

        if (type !== 'loading') {
            setTimeout(() => {
                messageEl.style.display = 'none';
            }, 4000);
        }
    },

    // ==================== FILE UPLOAD ====================

    handleFileSelect(files) {
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = ['.pdf', '.txt', '.md', '.docx'];

        files.forEach(file => {
            if (file.size > maxSize) {
                this.showMessage(`File ${file.name} exceeds 10MB limit`, 'error');
                return;
            }

            const ext = '.' + file.name.split('.').pop().toLowerCase();
            if (!allowedTypes.includes(ext)) {
                this.showMessage(`File ${file.name} has unsupported format`, 'error');
                return;
            }

            this.state.uploadedFiles.push(file);
        });

        this.renderUploadedFiles();

        const processBtn = this.container.querySelector('#process-btn');
        if (processBtn && this.state.uploadedFiles.length > 0) {
            processBtn.style.display = 'block';
        }
    },

    renderUploadedFiles() {
        const container = this.container.querySelector('#uploaded-files');
        if (!container) return;

        container.innerHTML = '';

        this.state.uploadedFiles.forEach((file, index) => {
            const fileEl = document.createElement('div');
            fileEl.className = 'uploaded-file';
            fileEl.innerHTML = `
                <div class="file-info">
                    <div class="file-icon">
                        <i class="fas fa-file-${this.getFileIcon(file.name)}"></i>
                    </div>
                    <div class="file-details">
                        <div class="file-name">${this.escapeHtml(file.name)}</div>
                        <div class="file-size">${this.formatFileSize(file.size)}</div>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="file-action-btn delete" data-action="remove-file" data-index="${index}" title="Remove">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            container.appendChild(fileEl);
        });

        // Add listener for remove buttons
        this.dom.on(container, 'click', '[data-action="remove-file"]', (e) => {
            const index = parseInt(e.currentTarget.dataset.index);
            this.removeFile(index);
        });
    },

    removeFile(index) {
        this.state.uploadedFiles.splice(index, 1);
        this.renderUploadedFiles();

        const processBtn = this.container.querySelector('#process-btn');
        if (processBtn && this.state.uploadedFiles.length === 0) {
            processBtn.style.display = 'none';
        }
    },

    async processFiles() {
        if (this.state.uploadedFiles.length === 0) {
            this.showMessage('No files to process', 'error');
            return;
        }

        if (!this.state.isConnected) {
            this.showMessage('Please connect to Pinecone first', 'error');
            this.switchTab('credentials');
            return;
        }

        const chunkSize = parseInt(this.container.querySelector('#chunk-size')?.value) || 800;
        const chunkOverlap = parseInt(this.container.querySelector('#chunk-overlap')?.value) || 20;
        const namespace = this.container.querySelector('#upload-namespace')?.value.trim();
        const category = this.container.querySelector('#upload-category')?.value || 'general';
        const tagsInput = this.container.querySelector('#upload-tags')?.value || '';
        const tags = tagsInput.split(',').map(t => t.trim()).filter(t => t);
        const visibility = this.container.querySelector('#upload-visibility')?.value || 'user';

        const progressContainer = this.container.querySelector('#upload-progress');
        const progressFill = this.container.querySelector('#progress-fill');
        const progressText = this.container.querySelector('#progress-text');
        const processBtn = this.container.querySelector('#process-btn');

        try {
            if (processBtn) processBtn.disabled = true;
            if (progressContainer) progressContainer.style.display = 'block';

            for (let i = 0; i < this.state.uploadedFiles.length; i++) {
                const file = this.state.uploadedFiles[i];
                const progress = ((i + 1) / this.state.uploadedFiles.length) * 100;

                if (progressFill) progressFill.style.width = `${progress}%`;
                if (progressText) progressText.textContent = `Processing ${file.name} (${i + 1}/${this.state.uploadedFiles.length})...`;

                const formData = new FormData();
                formData.append('file', file);
                formData.append('chunk_size', chunkSize);
                formData.append('chunk_overlap', chunkOverlap);
                formData.append('namespace', namespace || '');
                formData.append('category', category);
                formData.append('tags', JSON.stringify(tags));
                formData.append('visibility', visibility);
                formData.append('include_cloud_metadata', 'true');
                formData.append('enable_ai_retrieval', 'true');
                formData.append('file_type', file.type || 'application/octet-stream');
                formData.append('upload_timestamp', new Date().toISOString());

                const response = await fetch(`${this.state.API_BASE_URL}/api/vector-db/upload-document`, {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (!data.success) {
                    throw new Error(data.error || 'Upload failed');
                }

                this.log.info(`[VECTOR DB] Processed ${file.name}: ${data.vectors_uploaded} vectors`);
            }

            if (progressText) progressText.textContent = 'Processing complete!';
            this.showMessage(`Successfully processed ${this.state.uploadedFiles.length} files`, 'success');

            this.state.uploadedFiles = [];
            this.renderUploadedFiles();
            if (processBtn) processBtn.style.display = 'none';
            await this.loadStats();

            setTimeout(() => {
                this.switchTab('documents');
                if (progressContainer) progressContainer.style.display = 'none';
            }, 2000);

        } catch (error) {
            this.log.error('[VECTOR DB] Process files error:', error);
            this.showMessage(`Processing failed: ${error.message}`, 'error');
            if (progressContainer) progressContainer.style.display = 'none';
        } finally {
            if (processBtn) processBtn.disabled = false;
        }
    },

    // ==================== STATISTICS & DOCUMENTS ====================

    async loadStats() {
        try {
            const response = await this.api.get(
                `${this.state.API_BASE_URL}/api/vector-db/stats`
            );

            if (response.success && response.stats) {
                this.state.stats = response.stats;
                this.updateStatsUI();
            }
        } catch (error) {
            this.log.error('[VECTOR DB] Load stats error:', error);
        }
    },

    updateStatsUI() {
        const docsEl = this.container.querySelector('#stat-documents');
        const vectorsEl = this.container.querySelector('#stat-vectors');
        const namespacesEl = this.container.querySelector('#stat-namespaces');

        if (docsEl) docsEl.textContent = this.state.stats.documents || 0;
        if (vectorsEl) vectorsEl.textContent = this.formatNumber(this.state.stats.vectors || 0);
        if (namespacesEl) namespacesEl.textContent = this.state.stats.namespaces || 0;
    },

    async loadNamespaces() {
        const container = this.container.querySelector('#namespaces-list');
        if (!container) return;

        try {
            container.innerHTML = '<div class="loading-state"><div class="spinner"></div><div>Loading folders...</div></div>';

            const response = await this.api.get(
                `${this.state.API_BASE_URL}/api/vector-db/namespaces?include_stats=true`
            );

            if (response.success && response.namespaces && response.namespaces.length > 0) {
                container.innerHTML = '';
                response.namespaces.forEach(ns => {
                    const card = this.createNamespaceCard(ns);
                    container.appendChild(card);
                });

                // Update search dropdown
                this.updateSearchNamespaceOptions(response.namespaces);
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon"><i class="fas fa-folder"></i></div>
                        <div class="empty-text">No folders created yet</div>
                        <div class="empty-hint">Upload documents to create folders</div>
                    </div>
                `;
            }
        } catch (error) {
            this.log.error('[VECTOR DB] Load namespaces error:', error);
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <div class="empty-text">Failed to load folders</div>
                    <div class="empty-hint">${error.message}</div>
                </div>
            `;
        }
    },

    createNamespaceCard(ns) {
        const card = document.createElement('div');
        card.className = 'namespace-card';
        card.style.cssText = 'padding: 12px; margin-bottom: 12px; background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px;';
        card.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="font-size: 24px;">📂</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; font-size: 14px; color: #1F2937;">${this.escapeHtml(ns.display_name)}</div>
                    <div style="font-size: 12px; color: #6B7280; margin-top: 4px;">
                        <i class="fas fa-vector-square"></i> ${ns.vector_count || 0} vectors
                    </div>
                </div>
                <button class="file-action-btn delete" data-action="delete-namespace" data-namespace="${this.escapeHtml(ns.name)}" title="Delete folder">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        // Add delete listener
        const deleteBtn = card.querySelector('[data-action="delete-namespace"]');
        if (deleteBtn) {
            this.dom.on(deleteBtn, 'click', () => {
                this.deleteNamespace(ns.name, ns.display_name);
            });
        }

        return card;
    },

    updateSearchNamespaceOptions(namespaces) {
        const select = this.container.querySelector('#search-namespaces');
        if (!select) return;

        // Keep "All Folders" option
        select.innerHTML = '<option value="all" selected>All Folders</option>';

        // Add namespace options
        namespaces.forEach(ns => {
            const option = document.createElement('option');
            option.value = ns.name;
            option.textContent = `📂 ${ns.display_name} (${ns.vector_count || 0})`;
            select.appendChild(option);
        });
    },

    async deleteNamespace(namespace, displayName) {
        if (!confirm(`Are you sure you want to delete the folder "${displayName}"? This will remove all vectors in this folder.`)) {
            return;
        }

        if (!confirm('This action cannot be undone. Type DELETE to confirm.')) {
            return;
        }

        try {
            const response = await this.api.delete(
                `${this.state.API_BASE_URL}/api/vector-db/namespaces/${namespace}?confirm=DELETE`
            );

            if (response.success) {
                this.showMessage(`Folder "${displayName}" deleted successfully`, 'success');
                await this.loadNamespaces();
                await this.loadStats();
            } else {
                this.showMessage(`Error: ${response.error}`, 'error');
            }
        } catch (error) {
            this.log.error('[VECTOR DB] Delete namespace error:', error);
            this.showMessage('Failed to delete folder', 'error');
        }
    },

    async performSearch() {
        const query = this.container.querySelector('#search-query')?.value.trim();
        if (!query) {
            this.showMessage('Enter a search query', 'error');
            return;
        }

        const namespacesSelect = this.container.querySelector('#search-namespaces');
        const selectedNamespaces = Array.from(namespacesSelect.selectedOptions)
            .map(opt => opt.value)
            .filter(v => v !== 'all');

        const category = this.container.querySelector('#search-category')?.value;

        const filter = {};
        if (category) filter.category = { $eq: category };

        const resultsContainer = this.container.querySelector('#search-results');

        try {
            this.showMessage('Searching...', 'loading');
            if (resultsContainer) {
                resultsContainer.innerHTML = '<div class="loading-state"><div class="spinner"></div><div>Searching...</div></div>';
            }

            const response = await this.api.post(`${this.state.API_BASE_URL}/api/vector-db/query-namespaces`, {
                query_text: query,
                namespaces: selectedNamespaces.length > 0 ? selectedNamespaces : [],
                top_k: 10,
                filter: filter,
                include_metadata: true
            });

            if (response.success) {
                const matches = response.matches || [];
                this.showMessage(`Found ${matches.length} results`, 'success');
                this.renderSearchResults(matches);
            } else {
                this.showMessage(`Search failed: ${response.error}`, 'error');
                if (resultsContainer) {
                    resultsContainer.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-icon"><i class="fas fa-exclamation-triangle"></i></div>
                            <div class="empty-text">Search failed</div>
                            <div class="empty-hint">${response.error}</div>
                        </div>
                    `;
                }
            }
        } catch (error) {
            this.log.error('[VECTOR DB] Search error:', error);
            this.showMessage('Search failed', 'error');
            if (resultsContainer) {
                resultsContainer.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon"><i class="fas fa-exclamation-triangle"></i></div>
                        <div class="empty-text">Search failed</div>
                        <div class="empty-hint">${error.message}</div>
                    </div>
                `;
            }
        }
    },

    renderSearchResults(matches) {
        const container = this.container.querySelector('#search-results');
        if (!container) return;

        if (matches.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon"><i class="fas fa-search"></i></div>
                    <div class="empty-text">No results found</div>
                    <div class="empty-hint">Try different keywords or filters</div>
                </div>
            `;
            return;
        }

        container.innerHTML = '';

        matches.forEach((match, index) => {
            const resultCard = document.createElement('div');
            resultCard.style.cssText = 'padding: 12px; margin-bottom: 12px; background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px;';
            
            const metadata = match.metadata || {};
            const score = (match.score * 100).toFixed(1);
            const text = metadata.text || 'No text available';
            const truncatedText = text.length > 200 ? text.substring(0, 200) + '...' : text;
            const category = metadata.category || 'general';
            const document = metadata.document || 'Unknown';

            resultCard.innerHTML = `
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 13px; color: #1F2937;">
                            ${index + 1}. ${this.escapeHtml(document)}
                        </div>
                        <div style="font-size: 11px; color: #6B7280; margin-top: 2px;">
                            Category: ${this.escapeHtml(category)} • Score: ${score}%
                        </div>
                    </div>
                    <div style="padding: 4px 8px; background: #10B981; color: white; border-radius: 4px; font-size: 11px; font-weight: 600;">
                        ${score}%
                    </div>
                </div>
                <div style="font-size: 12px; color: #4B5563; line-height: 1.5;">
                    ${this.escapeHtml(truncatedText)}
                </div>
            `;

            container.appendChild(resultCard);
        });
    },

    async loadDocuments() {
        const container = this.container.querySelector('#documents-list');
        if (!container) return;

        try {
            container.innerHTML = '<div class="loading-state"><div class="spinner"></div></div>';

            const response = await this.api.get(
                `${this.state.API_BASE_URL}/api/vector-db/documents?include_metadata=true&include_cloud_links=true`
            );

            if (response.success && response.documents && response.documents.length > 0) {
                container.innerHTML = '';
                response.documents.forEach(doc => {
                    const docEl = this.createDocumentCard(doc);
                    container.appendChild(docEl);
                });
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon"><i class="fas fa-database"></i></div>
                        <div class="empty-text">No documents indexed yet</div>
                        <div class="empty-hint">Upload documents to get started</div>
                    </div>
                `;
            }
        } catch (error) {
            this.log.error('[VECTOR DB] Load documents error:', error);
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <div class="empty-text">Failed to load documents</div>
                </div>
            `;
        }
    },

    createDocumentCard(doc) {
        const card = document.createElement('div');
        card.className = 'document-card';
        card.innerHTML = `
            <div class="document-header">
                <div class="document-title">${this.escapeHtml(doc.name)}</div>
                <button class="file-action-btn delete" data-action="delete-document" data-id="${doc.id}" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            <div class="document-meta">
                <span><i class="fas fa-vector-square"></i> ${doc.vector_count} vectors</span>
                <span><i class="fas fa-calendar"></i> ${this.formatDate(doc.created_at)}</span>
            </div>
        `;

        // Add delete listener
        const deleteBtn = card.querySelector('[data-action="delete-document"]');
        if (deleteBtn) {
            this.dom.on(deleteBtn, 'click', () => {
                this.deleteDocument(doc.id);
            });
        }

        return card;
    },

    async deleteDocument(docId) {
        if (!confirm('Are you sure you want to delete this document?')) return;

        try {
            const response = await this.api.delete(
                `${this.state.API_BASE_URL}/api/vector-db/document/${docId}`
            );

            if (response.success) {
                this.showMessage('Document deleted successfully', 'success');
                await this.loadDocuments();
                await this.loadStats();
            } else {
                this.showMessage(`Error: ${response.error}`, 'error');
            }
        } catch (error) {
            this.log.error('[VECTOR DB] Delete document error:', error);
            this.showMessage('Failed to delete document', 'error');
        }
    },

    // ==================== TAB MANAGEMENT ====================

    switchTab(tabName) {
        // Safety check - ensure container exists
        const container = this.container || document.getElementById('vector-database');
        if (!container) {
            console.error('[VECTOR DB] Container not found in switchTab');
            return;
        }

        this.state.currentTab = tabName;

        // Update tab buttons
        const tabs = container.querySelectorAll('.vector-db-tab');
        tabs.forEach(tab => {
            tab.classList.remove('active');
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active');
            }
        });

        // Update tab content
        const contents = container.querySelectorAll('.tab-content');
        contents.forEach(content => {
            content.style.display = 'none';
        });

        const activeContent = container.querySelector(`#${tabName}-tab`);
        if (activeContent) {
            activeContent.style.display = 'block';
        }

        // Load data for specific tabs
        if (tabName === 'documents') {
            this.loadDocuments();
        } else if (tabName === 'namespaces') {
            this.loadNamespaces();
        } else if (tabName === 'search') {
            // Pre-load namespace options for search
            this.loadNamespaces();
        }

        this.log.info(`[VECTOR DB] Switched to ${tabName} tab`);
    },

    // ==================== QDRANT PROVIDER ====================

    onProviderChange(event) {
        const provider = event.target.value;
        this.state.selectedProvider = provider;
        this.storage.set('selectedProvider', provider);

        // Update provider info
        const infoEl = this.container.querySelector('#provider-info');
        const providerInfoMap = {
            'pinecone': '🌲 <strong>Pinecone</strong> - Cloud hosted, $70/mo, 150ms latency',
            'qdrant': '⚡ <strong>Qdrant</strong> - FREE self-hosted, 1-5ms latency, unlimited storage',
            'voyager': '🚀 <strong>Voyager</strong> - Pay-per-use, 120ms latency',
            'pgvector': '🐘 <strong>pgvector</strong> - FREE Supabase, 20ms latency'
        };
        if (infoEl) infoEl.innerHTML = providerInfoMap[provider] || '';

        // Show/hide Qdrant configuration tab
        const qdrantTab = this.container.querySelector('.tab-btn[data-tab="qdrant-config"]');
        const qdrantContent = this.container.querySelector('#qdrant-config-content');
        if (provider === 'qdrant') {
            if (qdrantTab) qdrantTab.style.display = 'inline-block';
            if (qdrantContent) qdrantContent.style.display = 'block';
        } else {
            if (qdrantTab) qdrantTab.style.display = 'none';
            if (qdrantContent) qdrantContent.style.display = 'none';
        }

        this.log.info(`[VECTOR DB] Provider changed to: ${provider}`);
        
        // Reload credentials for new provider
        this.loadCredentials();
        this.checkConnectionStatus();
    },

    onQdrantDeploymentTypeChange(event) {
        const deploymentType = event.target.value;
        this.state.qdrantDeploymentType = deploymentType;
        this.storage.set('qdrantDeploymentType', deploymentType);

        // Show/hide Docker wizard for customer-server deployment
        const dockerWizard = this.container.querySelector('#docker-wizard');
        if (dockerWizard) {
            dockerWizard.style.display = deploymentType === 'customer-server' ? 'block' : 'none';
        }

        this.log.info(`[VECTOR DB] Qdrant deployment type: ${deploymentType}`);
    },

    async deployQdrantDocker() {
        const isWindows = navigator.userAgent.includes('Windows');
        const commands = isWindows ? this.getWindowsDockerCommands() : this.getLinuxDockerCommands();

        const output = this.container.querySelector('#docker-commands-output');
        if (output) {
            output.textContent = commands;
            output.style.display = 'block';
        }

        this.showMessage('Docker commands generated! Copy and run in terminal', 'success');
        this.log.info('[VECTOR DB] Generated Docker deployment commands');
    },

    getWindowsDockerCommands() {
        return `# Windows PowerShell Commands
# Step 1: Pull Qdrant Docker image
docker pull qdrant/qdrant:latest

# Step 2: Create data directory
New-Item -ItemType Directory -Force -Path "$HOME\\qdrant_data"

# Step 3: Start Qdrant container
docker run -d \\
  --name qdrant \\
  -p 6333:6333 \\
  -p 6334:6334 \\
  -v "$HOME/qdrant_data:/qdrant/storage" \\
  qdrant/qdrant:latest

# Step 4: Verify container is running
docker ps | Select-String "qdrant"

# Step 5: Test API endpoint
Invoke-WebRequest -Uri "http://localhost:6333/" -Method GET

# Step 6 (Optional): Enable authentication
$apiKey = "your-secure-api-key-here"
docker stop qdrant
docker rm qdrant
docker run -d \\
  --name qdrant \\
  -p 6333:6333 \\
  -p 6334:6334 \\
  -v "$HOME/qdrant_data:/qdrant/storage" \\
  -e QDRANT__SERVICE__API_KEY="$apiKey" \\
  qdrant/qdrant:latest`;
    },

    getLinuxDockerCommands() {
        return `# Linux Bash Commands
# Step 1: Pull Qdrant Docker image
docker pull qdrant/qdrant:latest

# Step 2: Create data directory
mkdir -p ~/qdrant_data

# Step 3: Start Qdrant container
docker run -d \\
  --name qdrant \\
  -p 6333:6333 \\
  -p 6334:6334 \\
  -v ~/qdrant_data:/qdrant/storage \\
  qdrant/qdrant:latest

# Step 4: Verify container is running
docker ps | grep qdrant

# Step 5: Test API endpoint
curl http://localhost:6333/

# Step 6 (Optional): Enable authentication
API_KEY="your-secure-api-key-here"
docker stop qdrant
docker rm qdrant
docker run -d \\
  --name qdrant \\
  -p 6333:6333 \\
  -p 6334:6334 \\
  -v ~/qdrant_data:/qdrant/storage \\
  -e QDRANT__SERVICE__API_KEY="$API_KEY" \\
  qdrant/qdrant:latest`;
    },

    async testQdrantConnection() {
        const host = this.container.querySelector('#qdrant-host')?.value || 'localhost';
        const port = this.container.querySelector('#qdrant-port')?.value || '6333';
        const apiKey = this.container.querySelector('#qdrant-api-key')?.value || '';

        this.state.qdrantConnection = { host, port, api_key: apiKey };
        this.storage.set('qdrantConnection', this.state.qdrantConnection);

        const statusEl = this.container.querySelector('#qdrant-connection-status');
        if (statusEl) {
            statusEl.style.display = 'block';
            statusEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testing connection...';
            statusEl.style.background = 'rgba(88, 166, 255, 0.15)';
            statusEl.style.color = '#58a6ff';
        }

        try {
            const response = await this.api.post('/api/qdrant/connect', {
                host,
                port: parseInt(port),
                api_key: apiKey
            });

            if (response.success) {
                if (statusEl) {
                    statusEl.innerHTML = `<i class="fas fa-check-circle"></i> Connected successfully! Version: ${response.version || 'Unknown'}`;
                    statusEl.style.background = 'rgba(63, 185, 80, 0.15)';
                    statusEl.style.color = '#3fb950';
                }
                this.showMessage('Qdrant connection successful', 'success');
                await this.loadQdrantStats();
            } else {
                throw new Error(response.error || 'Connection failed');
            }
        } catch (error) {
            if (statusEl) {
                statusEl.innerHTML = `<i class="fas fa-times-circle"></i> Connection failed: ${error.message}`;
                statusEl.style.background = 'rgba(248, 81, 73, 0.15)';
                statusEl.style.color = '#f85149';
            }
            this.showMessage(`Connection failed: ${error.message}`, 'error');
            this.log.error('[VECTOR DB] Qdrant connection failed:', error);
        }
    },

    async loadQdrantStats() {
        try {
            const response = await this.api.get('/api/qdrant/stats');
            if (response.success) {
                this.state.stats.collections = response.stats.collections_count || 0;
                this.state.stats.indexed_vectors = response.stats.total_vectors || 0;
                this.updateStatsDisplay();
            }
        } catch (error) {
            this.log.error('[VECTOR DB] Failed to load Qdrant stats:', error);
        }
    },

    onMultiModalToggle(event) {
        this.state.multiModalEnabled = event.target.checked;
        this.storage.set('multiModalEnabled', this.state.multiModalEnabled);
        this.log.info(`[VECTOR DB] Multi-modal embeddings: ${this.state.multiModalEnabled}`);
    },

    onQuantizationToggle(event) {
        this.state.quantizationEnabled = event.target.checked;
        this.storage.set('quantizationEnabled', this.state.quantizationEnabled);
        this.log.info(`[VECTOR DB] Quantization: ${this.state.quantizationEnabled}`);
    },

    onHybridSearchToggle(event) {
        this.state.hybridSearchEnabled = event.target.checked;
        this.storage.set('hybridSearchEnabled', this.state.hybridSearchEnabled);
        this.log.info(`[VECTOR DB] Hybrid search: ${this.state.hybridSearchEnabled}`);
    },

    // ==================== UTILITIES ====================

    async refresh() {
        await this.loadStats();
        if (this.state.currentTab === 'documents') {
            await this.loadDocuments();
        }
        this.showMessage('Refreshed', 'success');
    },

    showMessage(message, type) {
        const msgEl = this.container.querySelector('#credential-message');
        if (!msgEl) return;

        msgEl.style.display = 'block';
        msgEl.textContent = message;
        msgEl.style.padding = '8px 12px';
        msgEl.style.borderRadius = '6px';
        msgEl.style.fontSize = '12px';

        if (type === 'success') {
            msgEl.style.background = 'rgba(63, 185, 80, 0.15)';
            msgEl.style.color = '#3fb950';
        } else if (type === 'error') {
            msgEl.style.background = 'rgba(248, 81, 73, 0.15)';
            msgEl.style.color = '#f85149';
        } else if (type === 'loading') {
            msgEl.style.background = 'rgba(88, 166, 255, 0.15)';
            msgEl.style.color = '#58a6ff';
        }

        if (type !== 'loading') {
            setTimeout(() => {
                msgEl.style.display = 'none';
            }, 3000);
        }
    },

    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const icons = {
            'pdf': 'pdf',
            'txt': 'alt',
            'md': 'alt',
            'docx': 'word'
        };
        return icons[ext] || 'alt';
    },

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    },

    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },

    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        return date.toLocaleDateString();
    },

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Window assignment complete - Module available as window.VectorDatabaseModule
console.log('✅ [VECTOR DB] Module script loaded (window.VectorDatabaseModule available)');
