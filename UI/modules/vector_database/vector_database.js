/**
 * Vector Database Sidebar Controller
 * 
 * PURPOSE: Main controller for vector database management sidebar
 * - Credential management (Pinecone + OpenAI)
 * - Document upload and processing
 * - Vector database operations
 * - 450px width sidebar matching Synergy structure
 * 
 * DEPENDENCIES:
 * - vector_database.css (styling)
 * - vector_database.html (DOM structure)
 * 
 * EXPORTS:
 * - window.vectorDbSidebar (main singleton)
 * 
 * LAST MODIFIED: 2025-11-25
 */

class VectorDatabaseSidebarController {
    constructor() {
        this.API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
        this.currentTab = 'credentials';
        this.uploadedFiles = [];
        this.isConnected = false;
        this.stats = {
            documents: 0,
            vectors: 0,
            namespaces: 0
        };

        console.log('[VECTOR DB SIDEBAR] Initialized');
    }

    /**
     * Initialize sidebar
     */
    async init() {
        console.log('[VECTOR DB SIDEBAR] Initializing...');

        // Load saved credentials
        await this.loadCredentials();

        // Setup event listeners
        this.setupEventListeners();

        // Load stats if connected
        if (this.isConnected) {
            await this.loadStats();
        }

        console.log('[VECTOR DB SIDEBAR] Initialization complete');
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Credential form submission
        const credForm = document.getElementById('credential-form');
        if (credForm) {
            credForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveCredentials();
            });
        }

        // File upload zone
        const uploadZone = document.getElementById('upload-zone');
        const fileInput = document.getElementById('file-input');

        if (uploadZone && fileInput) {
            uploadZone.addEventListener('click', () => fileInput.click());

            uploadZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadZone.classList.add('drag-over');
            });

            uploadZone.addEventListener('dragleave', () => {
                uploadZone.classList.remove('drag-over');
            });

            uploadZone.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadZone.classList.remove('drag-over');
                const files = Array.from(e.dataTransfer.files);
                this.handleFileSelect(files);
            });

            fileInput.addEventListener('change', (e) => {
                const files = Array.from(e.target.files);
                this.handleFileSelect(files);
            });
        }
    }

    /**
     * Toggle sidebar visibility
     */
    async toggleSidebar() {
        const sidebar = document.getElementById('vector-db-sidebar');
        if (!sidebar) return;

        const isExpanded = sidebar.classList.contains('expanded');

        if (isExpanded) {
            sidebar.classList.remove('expanded');
            console.log('[VECTOR DB SIDEBAR] Closed');
        } else {
            // Auto-initialize on first open
            if (!this.initialized) {
                await this.init();
                this.initialized = true;
            }
            sidebar.classList.add('expanded');
            console.log('[VECTOR DB SIDEBAR] Opened');
        }
    }

    /**
     * Switch tab
     */
    switchTab(tabName) {
        this.currentTab = tabName;

        // Update tab buttons
        document.querySelectorAll('.vector-db-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`.vector-db-tab[data-tab="${tabName}"]`)?.classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = 'none';
        });
        document.getElementById(`${tabName}-tab`)?.style.display = 'block';

        // Load data for specific tabs
        if (tabName === 'documents') {
            this.loadDocuments();
        }

        console.log(`[VECTOR DB SIDEBAR] Switched to ${tabName} tab`);
    }

    /**
     * Save credentials to backend
     */
    async saveCredentials() {
        const apiKey = document.getElementById('api-key').value.trim();
        const indexName = document.getElementById('index-name').value.trim();
        const environment = document.getElementById('environment').value.trim();
        const namespace = document.getElementById('namespace').value.trim();

        if (!apiKey || !indexName || !environment) {
            this.showMessage('Please fill all required fields', 'error');
            return;
        }

        try {
            this.showMessage('Saving credentials...', 'loading');

            const response = await fetch(`${this.API_BASE_URL}/api/vector-db/credentials/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: window.currentUserId || 1,
                    api_key: apiKey,
                    index_name: indexName,
                    environment: environment,
                    namespace: namespace || ''
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage('Credentials saved successfully', 'success');
                this.isConnected = true;
                this.updateConnectionStatus(true);
                await this.loadStats();
            } else {
                this.showMessage(`Error: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('[VECTOR DB SIDEBAR] Save credentials error:', error);
            this.showMessage('Failed to save credentials', 'error');
        }
    }

    /**
     * Load saved credentials
     */
    async loadCredentials() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/vector-db/credentials/get?user_id=${window.currentUserId || 1}`);
            const data = await response.json();

            if (data.success && data.credentials) {
                const creds = data.credentials;
                document.getElementById('index-name').value = creds.index_name || '';
                document.getElementById('environment').value = creds.environment || '';
                document.getElementById('namespace').value = creds.namespace || '';
                
                this.isConnected = true;
                this.updateConnectionStatus(true);
                console.log('[VECTOR DB SIDEBAR] Credentials loaded');
            }
        } catch (error) {
            console.error('[VECTOR DB SIDEBAR] Load credentials error:', error);
        }
    }

    /**
     * Test connection to Pinecone
     */
    async testConnection() {
        try {
            this.showMessage('Testing connection...', 'loading');

            const response = await fetch(`${this.API_BASE_URL}/api/vector-db/test-connection`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: window.currentUserId || 1
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage(`Connected! ${data.message}`, 'success');
                this.isConnected = true;
                this.updateConnectionStatus(true);
                await this.loadStats();
            } else {
                this.showMessage(`Connection failed: ${data.error}`, 'error');
                this.isConnected = false;
                this.updateConnectionStatus(false);
            }
        } catch (error) {
            console.error('[VECTOR DB SIDEBAR] Test connection error:', error);
            this.showMessage('Connection test failed', 'error');
            this.isConnected = false;
            this.updateConnectionStatus(false);
        }
    }

    /**
     * Update connection status UI
     */
    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('connection-status');
        if (statusEl) {
            if (connected) {
                statusEl.textContent = 'Connected';
                statusEl.className = 'credential-status connected';
            } else {
                statusEl.textContent = 'Disconnected';
                statusEl.className = 'credential-status disconnected';
            }
        }
    }

    /**
     * Save OpenAI embedding configuration
     */
    async saveEmbeddingConfig() {
        const apiKey = document.getElementById('openai-api-key').value.trim();
        const model = document.getElementById('embedding-model').value;

        if (!apiKey) {
            this.showMessage('Please enter OpenAI API key', 'error');
            return;
        }

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/vector-db/embedding-config/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: window.currentUserId || 1,
                    api_key: apiKey,
                    model: model
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage('Embedding configuration saved', 'success');
            } else {
                this.showMessage(`Error: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('[VECTOR DB SIDEBAR] Save embedding config error:', error);
            this.showMessage('Failed to save configuration', 'error');
        }
    }

    /**
     * Handle file selection
     */
    handleFileSelect(files) {
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = ['.pdf', '.txt', '.md', '.docx'];

        files.forEach(file => {
            // Check file size
            if (file.size > maxSize) {
                this.showMessage(`File ${file.name} exceeds 10MB limit`, 'error');
                return;
            }

            // Check file type
            const ext = '.' + file.name.split('.').pop().toLowerCase();
            if (!allowedTypes.includes(ext)) {
                this.showMessage(`File ${file.name} has unsupported format`, 'error');
                return;
            }

            // Add to uploaded files
            this.uploadedFiles.push(file);
        });

        this.renderUploadedFiles();
        
        // Show process button
        const processBtn = document.getElementById('process-btn');
        if (processBtn && this.uploadedFiles.length > 0) {
            processBtn.style.display = 'block';
        }
    }

    /**
     * Render uploaded files list
     */
    renderUploadedFiles() {
        const container = document.getElementById('uploaded-files');
        if (!container) return;

        container.innerHTML = '';

        this.uploadedFiles.forEach((file, index) => {
            const fileEl = document.createElement('div');
            fileEl.className = 'uploaded-file';
            fileEl.innerHTML = `
                <div class="file-info">
                    <div class="file-icon">
                        <i class="fas fa-file-${this.getFileIcon(file.name)}"></i>
                    </div>
                    <div class="file-details">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${this.formatFileSize(file.size)}</div>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="file-action-btn delete" onclick="window.vectorDbSidebar.removeFile(${index})" title="Remove">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            container.appendChild(fileEl);
        });
    }

    /**
     * Remove file from upload list
     */
    removeFile(index) {
        this.uploadedFiles.splice(index, 1);
        this.renderUploadedFiles();

        const processBtn = document.getElementById('process-btn');
        if (processBtn && this.uploadedFiles.length === 0) {
            processBtn.style.display = 'none';
        }
    }

    /**
     * Process and upload files to vector DB
     */
    async processFiles() {
        if (this.uploadedFiles.length === 0) {
            this.showMessage('No files to process', 'error');
            return;
        }

        if (!this.isConnected) {
            this.showMessage('Please connect to Pinecone first', 'error');
            this.switchTab('credentials');
            return;
        }

        const chunkSize = parseInt(document.getElementById('chunk-size').value) || 800;
        const chunkOverlap = parseInt(document.getElementById('chunk-overlap').value) || 20;
        const namespace = document.getElementById('upload-namespace').value.trim();

        const progressContainer = document.getElementById('upload-progress');
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        const processBtn = document.getElementById('process-btn');

        try {
            processBtn.disabled = true;
            progressContainer.style.display = 'block';

            for (let i = 0; i < this.uploadedFiles.length; i++) {
                const file = this.uploadedFiles[i];
                const progress = ((i + 1) / this.uploadedFiles.length) * 100;

                progressFill.style.width = `${progress}%`;
                progressText.textContent = `Processing ${file.name} (${i + 1}/${this.uploadedFiles.length})...`;

                const formData = new FormData();
                formData.append('file', file);
                formData.append('user_id', window.currentUserId || 1);
                formData.append('chunk_size', chunkSize);
                formData.append('chunk_overlap', chunkOverlap);
                formData.append('namespace', namespace || '');

                const response = await fetch(`${this.API_BASE_URL}/api/vector-db/upload-document`, {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (!data.success) {
                    throw new Error(data.error || 'Upload failed');
                }

                console.log(`[VECTOR DB SIDEBAR] Processed ${file.name}: ${data.vectors_uploaded} vectors`);
            }

            progressText.textContent = 'Processing complete!';
            this.showMessage(`Successfully processed ${this.uploadedFiles.length} files`, 'success');

            // Clear files and refresh
            this.uploadedFiles = [];
            this.renderUploadedFiles();
            processBtn.style.display = 'none';
            await this.loadStats();

            // Switch to documents tab
            setTimeout(() => {
                this.switchTab('documents');
                progressContainer.style.display = 'none';
            }, 2000);

        } catch (error) {
            console.error('[VECTOR DB SIDEBAR] Process files error:', error);
            this.showMessage(`Processing failed: ${error.message}`, 'error');
            progressContainer.style.display = 'none';
        } finally {
            processBtn.disabled = false;
        }
    }

    /**
     * Load vector database statistics
     */
    async loadStats() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/vector-db/stats?user_id=${window.currentUserId || 1}`);
            const data = await response.json();

            if (data.success && data.stats) {
                this.stats = data.stats;
                this.updateStatsUI();
            }
        } catch (error) {
            console.error('[VECTOR DB SIDEBAR] Load stats error:', error);
        }
    }

    /**
     * Update stats UI
     */
    updateStatsUI() {
        document.getElementById('stat-documents').textContent = this.stats.documents || 0;
        document.getElementById('stat-vectors').textContent = this.formatNumber(this.stats.vectors || 0);
        document.getElementById('stat-namespaces').textContent = this.stats.namespaces || 0;
    }

    /**
     * Load documents list
     */
    async loadDocuments() {
        const container = document.getElementById('documents-list');
        if (!container) return;

        try {
            container.innerHTML = '<div class="loading-state"><div class="spinner"></div></div>';

            const response = await fetch(`${this.API_BASE_URL}/api/vector-db/documents?user_id=${window.currentUserId || 1}`);
            const data = await response.json();

            if (data.success && data.documents && data.documents.length > 0) {
                container.innerHTML = '';
                data.documents.forEach(doc => {
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
            console.error('[VECTOR DB SIDEBAR] Load documents error:', error);
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <div class="empty-text">Failed to load documents</div>
                </div>
            `;
        }
    }

    /**
     * Create document card element
     */
    createDocumentCard(doc) {
        const card = document.createElement('div');
        card.className = 'document-card';
        card.innerHTML = `
            <div class="document-header">
                <div class="document-title">${doc.name}</div>
                <button class="file-action-btn delete" onclick="window.vectorDbSidebar.deleteDocument('${doc.id}')" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            <div class="document-meta">
                <span><i class="fas fa-vector-square"></i> ${doc.vector_count} vectors</span>
                <span><i class="fas fa-calendar"></i> ${this.formatDate(doc.created_at)}</span>
            </div>
        `;
        return card;
    }

    /**
     * Delete document from vector DB
     */
    async deleteDocument(docId) {
        if (!confirm('Are you sure you want to delete this document?')) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/vector-db/document/${docId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: window.currentUserId || 1 })
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage('Document deleted successfully', 'success');
                await this.loadDocuments();
                await this.loadStats();
            } else {
                this.showMessage(`Error: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('[VECTOR DB SIDEBAR] Delete document error:', error);
            this.showMessage('Failed to delete document', 'error');
        }
    }

    /**
     * Refresh sidebar data
     */
    async refresh() {
        await this.loadStats();
        if (this.currentTab === 'documents') {
            await this.loadDocuments();
        }
        this.showMessage('Refreshed', 'success');
    }

    /**
     * Show message to user
     */
    showMessage(message, type) {
        const msgEl = document.getElementById('credential-message');
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
    }

    /**
     * Open help documentation
     */
    openHelp() {
        window.open('https://docs.pinecone.io', '_blank');
    }

    /**
     * Utility: Get file icon based on extension
     */
    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const icons = {
            'pdf': 'pdf',
            'txt': 'alt',
            'md': 'alt',
            'docx': 'word'
        };
        return icons[ext] || 'alt';
    }

    /**
     * Utility: Format file size
     */
    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    /**
     * Utility: Format number with commas
     */
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    /**
     * Utility: Format date
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        return date.toLocaleDateString();
    }
}

// Initialize and expose globally
window.vectorDbSidebar = new VectorDatabaseSidebarController();

console.log('[VECTOR DB SIDEBAR] Controller loaded');
