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
        selectedProvider: 'pgvector', // pgvector (free default), pinecone, qdrant
        embeddingProvider: 'local',    // 'local' | 'voyager' | 'openai' — persisted in localStorage
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
        // Re-capture at runtime: this script loads before window.API_BASE_URL is set (static <script> tag)
        this.state.API_BASE_URL = window.API_BASE_URL || window.location.origin;
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

                    // Wait for DOM to update before setting up event listeners
                    await new Promise(resolve => requestAnimationFrame(resolve));
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
        this._listenersSetUp = true;  // guard so we only attach listeners once

        // Load saved credentials and check connection status
        await this.loadCredentials();
        await this.checkConnectionStatus();

        // Load stats if connected
        if (this.state.isConnected) {
            await this.loadStats();
        }

        // Restore saved embedding model preference (default: 'local' = free BGE)
        const savedEmb = localStorage.getItem('vdb_embedding_provider') || 'local';
        this.state.embeddingProvider = savedEmb;
        const embSelector = this.container.querySelector('#embedding-model-selector');
        if (embSelector) {
            embSelector.value = savedEmb;
            this._updateEmbeddingModelInfo(savedEmb);
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
        // Re-capture at runtime in case API_BASE_URL was not set when this script first loaded
        this.state.API_BASE_URL = window.API_BASE_URL || window.location.origin;
        this.log.info('[VECTOR DB] Sidebar opened');

        // onSidebarLoad sets up the container reference and attaches ALL event listeners
        // (upload zone click, drag-drop, tab switching, etc).  It is guarded by
        // this._listenersSetUp so it only runs its heavy setup once, then is a no-op.
        if (!this._listenersSetUp) {
            await this.onSidebarLoad(utilities);
        } else {
            await this.refresh();
        }
    },

    /**
     * Called when module is unloaded
     */
    openHelp() {
        // Remove any existing help modal
        const existing = document.getElementById('vdb-help-modal');
        if (existing) { existing.remove(); return; }

        const modal = document.createElement('div');
        modal.id = 'vdb-help-modal';
        modal.style.cssText = [
            'position:fixed', 'top:80px', 'left:50%', 'transform:translateX(-50%)',
            'width:640px', 'max-width:96vw', 'max-height:82vh',
            'background:var(--bg-primary,#161b22)', 'color:var(--text-primary,#e6edf3)',
            'border:1px solid var(--border-default,#30363d)', 'border-radius:12px',
            'box-shadow:0 24px 64px rgba(0,0,0,.55)', 'z-index:99999',
            'display:flex', 'flex-direction:column', 'overflow:hidden', 'user-select:none'
        ].join(';');

        modal.innerHTML = `
<div id="vdb-help-drag" style="
    padding:14px 18px; background:var(--bg-secondary,#21262d);
    border-bottom:1px solid var(--border-default,#30363d);
    display:flex; align-items:center; justify-content:space-between;
    cursor:move; flex-shrink:0;">
    <div style="display:flex;align-items:center;gap:10px;">
        <i class="fas fa-database" style="color:#58a6ff;font-size:16px;"></i>
        <span style="font-weight:700;font-size:15px;">Vector Database — Help Guide</span>
    </div>
    <button id="vdb-help-close" style="
        background:none;border:none;color:var(--text-muted,#8b949e);
        font-size:18px;cursor:pointer;padding:2px 6px;border-radius:4px;
        line-height:1;" title="Close">&times;</button>
</div>
<div style="overflow-y:auto;padding:20px 22px;flex:1;line-height:1.65;font-size:13px;">

<style>
  #vdb-help-modal h3 {
    font-size:13px;font-weight:700;color:#58a6ff;
    margin:18px 0 6px;display:flex;align-items:center;gap:7px;
  }
  #vdb-help-modal h3:first-child{margin-top:0}
  #vdb-help-modal p{margin:0 0 8px;color:var(--text-secondary,#c9d1d9);}
  #vdb-help-modal table{width:100%;border-collapse:collapse;margin:8px 0 14px;font-size:12px;}
  #vdb-help-modal th{text-align:left;padding:6px 8px;
    background:var(--bg-secondary,#21262d);color:#58a6ff;
    border-bottom:1px solid var(--border-default,#30363d);}
  #vdb-help-modal td{padding:6px 8px;vertical-align:top;
    border-bottom:1px solid var(--border-default,#30363d);
    color:var(--text-secondary,#c9d1d9);}
  #vdb-help-modal td:first-child{white-space:nowrap;font-weight:600;color:#e6edf3;}
  #vdb-help-modal .tip{padding:8px 12px;
    background:rgba(88,166,255,.1);border-left:3px solid #58a6ff;
    border-radius:0 6px 6px 0;margin:8px 0 14px;font-size:12px;
    color:var(--text-secondary,#c9d1d9);}
  #vdb-help-modal .warn{padding:8px 12px;
    background:rgba(255,193,7,.08);border-left:3px solid #ffc107;
    border-radius:0 6px 6px 0;margin:8px 0 14px;font-size:12px;
    color:var(--text-secondary,#c9d1d9);}
  #vdb-help-modal .good{padding:8px 12px;
    background:rgba(16,185,129,.08);border-left:3px solid #10b981;
    border-radius:0 6px 6px 0;margin:8px 0 14px;font-size:12px;
    color:var(--text-secondary,#c9d1d9);}
  #vdb-help-modal hr{border:none;border-top:1px solid var(--border-default,#30363d);margin:16px 0;}
</style>

<h3><i class="fas fa-info-circle"></i> What is the Vector Database?</h3>
<p>The Vector Database lets you upload documents so the AI can search them intelligently. Instead of keyword matching, it understands <em>meaning</em> — ask &ldquo;What is our refund policy?&rdquo; and it finds the right paragraph even if those exact words never appear in the document.</p>
<div class="tip"><i class="fas fa-robot"></i> <strong>Tip:</strong> Once documents are indexed the AI searches them automatically when you ask relevant questions. No special command needed.</div>

<hr>
<h3><i class="fas fa-chart-bar"></i> Stats Bar (top of panel)</h3>
<table>
  <tr><th>Stat</th><th>What it means</th></tr>
  <tr><td>Documents</td><td>Number of files you have indexed.</td></tr>
  <tr><td>Vectors</td><td>Total text chunks stored. One document splits into many chunks, each stored as one vector.</td></tr>
  <tr><td>Org Scope</td><td>Your organisation&rsquo;s isolated namespace in the pgvector store. All your documents live here, invisible to other orgs.</td></tr>
</table>

<hr>
<h3><i class="fas fa-upload"></i> Upload Tab</h3>
<p><strong>Upload Zone</strong> — Drag files directly onto the dashed area, or click anywhere inside it to open a file picker. Multiple files can be selected at once.</p>
<p>Supported formats include PDF, Word (.docx/.doc), Excel (.xlsx), PowerPoint (.pptx), Markdown, HTML, JSON, CSV, XML, RTF, EPUB, LaTeX, YAML and more. Maximum 10 MB per file.</p>
<p>After selecting files a <strong>Process &amp; Upload to Vector DB</strong> button appears. Any errors are shown directly below that button in red.</p>

<table>
  <tr><th>Setting</th><th>What it does</th><th>Recommendation</th></tr>
  <tr><td>Chunk Size</td><td>Characters per text chunk when splitting the document.</td><td>800 for most docs. 400&ndash;600 for dense reference material; 1200+ for long narrative text.</td></tr>
  <tr><td>Chunk Overlap</td><td>Characters shared between adjacent chunks so context is never cut at a hard boundary.</td><td>100 (roughly 12% of chunk size). Do not set to 0.</td></tr>
  <tr><td>Target Namespace</td><td>Optional folder name for this upload. Leave blank to use your org&rsquo;s default.</td><td>Use project names, e.g. <em>contracts-2024</em> or <em>hr-handbook</em>.</td></tr>
  <tr><td>Category</td><td>Department tag for filtered searching.</td><td>Pick the closest match; General is fine if unsure.</td></tr>
  <tr><td>Tags</td><td>Comma-separated labels for finer filtering.</td><td>E.g. <em>draft, Q3, confidential</em></td></tr>
  <tr><td>Visibility</td><td>Who can find this document when searching.</td><td>Organisation (your whole team) is the most useful default.</td></tr>
</table>

<table>
  <tr><th>Visibility</th><th>Who sees it</th></tr>
  <tr><td>Private</td><td>Only you.</td></tr>
  <tr><td>Organisation</td><td>Everyone in your organisation.</td></tr>
  <tr><td>Team</td><td>Specific team members only.</td></tr>
  <tr><td>Global</td><td>All users on the platform.</td></tr>
</table>

<hr>
<h3><i class="fas fa-folder"></i> Folders Tab</h3>
<p>Lists every namespace (folder) that contains indexed documents, with document and vector counts per folder.</p>
<div class="warn"><i class="fas fa-exclamation-triangle"></i> <strong>Delete namespace</strong> permanently removes the folder and <em>all</em> vectors inside it. This cannot be undone.</div>

<hr>
<h3><i class="fas fa-file-alt"></i> Documents Tab</h3>
<p>Shows every indexed file with its metadata: name, size, upload date, and chunk count. Click a document row to see full metadata and a preview of its first chunk. Use <strong>Refresh</strong> to reload after a new upload.</p>

<hr>
<h3><i class="fas fa-search"></i> Search Tab</h3>
<p>Run a semantic search directly from the panel, independent of the AI chat.</p>
<table>
  <tr><th>Field</th><th>What it does</th></tr>
  <tr><td>Search Query</td><td>Type a natural-language question or keywords.</td></tr>
  <tr><td>Search In</td><td>One or more folders. Hold Ctrl/Cmd to multi-select. &ldquo;All Folders&rdquo; searches everything.</td></tr>
  <tr><td>Category Filter</td><td>Narrow results to a single document category.</td></tr>
</table>
<p>Results show the most relevant text excerpts with a cosine-similarity score (0&ndash;1; closer to 1 is better).</p>

<hr>
<h3><i class="fas fa-cog"></i> Settings Tab</h3>
<p><strong>Vector Database Provider</strong></p>
<table>
  <tr><th>Provider</th><th>Cost</th><th>Notes</th></tr>
  <tr><td>pgvector (Supabase)</td><td>Free</td><td>Default. Built into your Supabase database — zero setup, data never leaves your DB, org-isolated by Row Level Security.</td></tr>
  <tr><td>Pinecone</td><td>~$70/mo</td><td>Cloud-managed, ~150 ms latency, enterprise scale. Requires a Pinecone API key in Organisation Settings &rarr; Connections.</td></tr>
  <tr><td>Qdrant</td><td>Free (self-hosted)</td><td>Deploy on your own server via Docker for maximum control and lowest latency.</td></tr>
</table>

<p><strong>Embedding Model</strong> — determines how text is converted into vectors. All three options produce 768-dimensional vectors, so you can switch at any time without re-uploading existing documents (future uploads will just use the new model).</p>
<table>
  <tr><th>Model</th><th>Cost</th><th>Quality</th><th>Notes</th></tr>
  <tr><td>Local BGE (default)</td><td>Free</td><td>Good &mdash; MTEB 63.6</td><td>BAAI/bge-base-en-v1.5 runs on the server. No API key needed. First upload takes ~30&ndash;60 s to download the model (~440 MB); subsequent uploads are instant. Model is cached to persistent disk and survives redeploys.</td></tr>
  <tr><td>Voyage AI</td><td>Pay-per-use</td><td>Excellent &mdash; MTEB 70+</td><td>Uses voyage-4. Add a Voyage AI key in Organisation Settings &rarr; Connections (platform: <em>voyager</em>).</td></tr>
  <tr><td>OpenAI</td><td>Pay-per-use</td><td>Very good &mdash; MTEB 62+</td><td>Uses text-embedding-3-small. Add an OpenAI key in Organisation Settings &rarr; Connections.</td></tr>
</table>
<div class="good"><i class="fas fa-server"></i> <strong>Local BGE is recommended</strong> for getting started. It costs nothing, works immediately, and produces high-quality retrieval results. Upgrade to Voyage AI when you want the best possible search quality.</div>
<div class="warn"><i class="fas fa-exclamation-triangle"></i> <strong>Mixing embedding models:</strong> Documents indexed with one model are not comparable to documents indexed with a different model. If you switch models, re-upload your documents to rebuild all vectors with the new model.</div>

<table>
  <tr><th>Feature</th><th>What it does</th></tr>
  <tr><td>Hybrid Search</td><td>Combines semantic (meaning-based) search with BM25 keyword search. Improves results on short or exact-phrase queries. Recommended for most use cases.</td></tr>
  <tr><td>Multi-Modal Embeddings</td><td>Experimental. Enables indexing of images and audio alongside text.</td></tr>
  <tr><td>Open Platform Connections</td><td>Opens the credential vault to add or update your Voyage AI, OpenAI, or Pinecone API keys.</td></tr>
</table>

<hr>
<h3><i class="fas fa-mouse-pointer"></i> Quick-Start Checklist</h3>
<table>
  <tr><td>1.</td><td>Check the green <em>Connected</em> banner at the top. pgvector is always available — no setup required.</td></tr>
  <tr><td>2.</td><td>In Settings, confirm <strong>Embedding Model</strong> is set to <em>Local BGE &mdash; FREE</em> (the default). No API key needed.</td></tr>
  <tr><td>3.</td><td>Go to the <strong>Upload</strong> tab. Drag a PDF or click the upload zone to pick files.</td></tr>
  <tr><td>4.</td><td>Optionally adjust Chunk Size / Overlap, then click <strong>Process &amp; Upload to Vector DB</strong>.</td></tr>
  <tr><td>5.</td><td>Wait for the progress bar to complete. If there is an error it appears in red below the button.</td></tr>
  <tr><td>6.</td><td>Go to <strong>Documents</strong> to confirm the file is listed.</td></tr>
  <tr><td>7.</td><td>Open an AI chat and ask a question about your document — the AI will find and cite it automatically.</td></tr>
</table>
<div class="tip"><i class="fas fa-clock"></i> <strong>First upload only:</strong> If you see &ldquo;Processing&rdquo; for 30&ndash;60 seconds on the very first upload after a server restart, the BGE model is being downloaded to the server&rsquo;s persistent disk. Every subsequent upload is near-instant.</div>

</div>`;

        document.body.appendChild(modal);

        // Close button
        modal.querySelector('#vdb-help-close').addEventListener('click', () => modal.remove());

        // Click outside to close
        document.addEventListener('click', function outsideClick(e) {
            if (!modal.contains(e.target)) {
                modal.remove();
                document.removeEventListener('click', outsideClick);
            }
        }, { capture: true });

        // Draggable via header bar
        const dragHandle = modal.querySelector('#vdb-help-drag');
        let dragging = false, startX, startY, origLeft, origTop;
        dragHandle.addEventListener('mousedown', (e) => {
            dragging = true;
            const rect = modal.getBoundingClientRect();
            startX = e.clientX; startY = e.clientY;
            origLeft = rect.left; origTop = rect.top;
            modal.style.transform = 'none';
            modal.style.left = origLeft + 'px';
            modal.style.top  = origTop + 'px';
            e.preventDefault();
        });
        document.addEventListener('mousemove', (e) => {
            if (!dragging) return;
            modal.style.left = (origLeft + e.clientX - startX) + 'px';
            modal.style.top  = (origTop  + e.clientY - startY) + 'px';
        });
        document.addEventListener('mouseup', () => { dragging = false; });
    },

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
            this.log.info('[VECTOR DB] Upload zone clicked');
            if (e.target.id !== 'file-input') {
                const fileInput = this.container.querySelector('#file-input');
                if (fileInput) {
                    this.log.info('[VECTOR DB] Triggering file input click');
                    fileInput.click();
                } else {
                    this.log.error('[VECTOR DB] File input not found');
                }
            }
        });

        // Drag and drop
        // NOTE: e.currentTarget is the delegated container (this.container), NOT the upload-zone.
        // Use e.target.closest('#upload-zone') to reliably reference the drop target.
        this.dom.on(this.container, 'dragenter', '#upload-zone', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const zone = e.target.closest('#upload-zone');
            if (zone) zone.classList.add('drag-over');
        });

        this.dom.on(this.container, 'dragover', '#upload-zone', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const zone = e.target.closest('#upload-zone');
            if (zone) zone.classList.add('drag-over');
        });

        this.dom.on(this.container, 'dragleave', '#upload-zone', (e) => {
            e.stopPropagation();
            // Only remove when leaving the zone itself, not a child element
            const zone = e.target.closest('#upload-zone');
            if (zone && !zone.contains(e.relatedTarget)) {
                zone.classList.remove('drag-over');
            }
        });

        this.dom.on(this.container, 'drop', '#upload-zone', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const zone = e.target.closest('#upload-zone');
            if (zone) zone.classList.remove('drag-over');
            const files = Array.from(e.dataTransfer.files);
            this.log.info(`[VECTOR DB] Drop event: ${files.length} file(s) dropped`);
            this.handleFileSelect(files);
        });

        // File input change
        this.dom.on(this.container, 'change', '#file-input', (e) => {
            const files = Array.from(e.target.files);
            this.log.info(`[VECTOR DB] File input changed: ${files.length} file(s) selected`);
            this.handleFileSelect(files);
        });

        // Tab switching
        // NOTE: use e.target.closest() — e.currentTarget is the delegated container, not the tab button.
        this.dom.on(this.container, 'click', '.vector-db-tab', (e) => {
            const tabBtn = e.target.closest('.vector-db-tab');
            const tabName = tabBtn?.dataset.tab;
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

        // Embedding model selector (Settings tab)
        this.dom.on(this.container, 'change', '#embedding-model-selector', (e) => {
            this.onEmbeddingModelChange(e.target.value);
        });

        this.log.info('[VECTOR DB] Event listeners setup complete');
    },

    // ==================== CREDENTIAL MANAGEMENT ====================

    async saveCredentials() {
        // GAP-V5: Credentials are managed in Organisation Settings → Connections (org vault).
        // This method is retained for compatibility but redirects to the correct location.
        this.showMessage(
            'Credentials are managed in Organisation Settings \u2192 Connections. Add your Pinecone API key there.',
            'info'
        );
        if (typeof window.openOrgSettingsPanel === 'function') {
            window.openOrgSettingsPanel('connections');
        }
    },

    async loadCredentials() {
        // GAP-V5: Legacy credential endpoints retired. Use checkConnectionStatus() which
        // resolves credentials directly from the org vault via the authenticated backend.
        try {
            await this.checkConnectionStatus();
        } catch (error) {
            this.log.error('[VECTOR DB] Connection check error:', error);
            this.state.isConnected = false;
            this.updateConnectionStatus(false);
            this.showNotConfiguredBanner();
        }

        // Load embedding configuration (uses authenticated org-vault endpoint)
        await this.loadEmbeddingConfig();
    },

    async checkConnectionStatus() {
        try {
            const provider = this.state.selectedProvider;
            this.log.info(`[VECTOR DB] Testing ${provider} connection...`);

            // pgvector is always available — built into Supabase, no external API key required
            if (provider === 'pgvector') {
                this.state.isConnected = true;
                this.showConnectedBanner({ provider: 'pgvector' });
                this.log.info('[VECTOR DB] pgvector: always connected (Supabase built-in)');
                return;
            }

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
                    provider: response.detected_provider || provider,
                    emb_provider: response.emb_provider,
                    emb_model: response.emb_model
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

        const provider = credentials.provider || this.state.selectedProvider;
        const isPgvector = provider === 'pgvector';

        const providerDisplayMap = {
            'pinecone': 'Pinecone',
            'pgvector': 'pgvector (Supabase)',
            'qdrant': 'Qdrant'
        };
        const providerDisplay = providerDisplayMap[provider] || provider;

        const providerName = this.container.querySelector('#banner-provider-name');
        const embeddingProvider = this.container.querySelector('#banner-embedding-provider');
        const embeddingModel = this.container.querySelector('#banner-embedding-model');

        if (providerName) providerName.textContent = providerDisplay;

        // Show the user's actual selected embedding model, not a hardcoded default.
        const embMap = {
            local:   { label: 'Local BGE',  model: 'bge-base-en-v1.5' },
            voyager: { label: 'Voyage AI',  model: 'voyage-4' },
            openai:  { label: 'OpenAI',     model: 'text-embedding-3-small' },
        };
        const embInfo = embMap[this.state.embeddingProvider || 'local'];
        if (embeddingProvider) embeddingProvider.textContent =
            credentials.emb_provider || credentials.embedding_provider || embInfo.label;
        if (embeddingModel) embeddingModel.textContent =
            credentials.model || credentials.embedding_model || credentials.emb_model || embInfo.model;
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

    onEmbeddingModelChange(value) {
        this.state.embeddingProvider = value;
        localStorage.setItem('vdb_embedding_provider', value);
        this._updateEmbeddingModelInfo(value);
        // Refresh banner so it shows the newly-selected model
        this.showConnectedBanner({ provider: this.state.selectedProvider });
        this.log.info('[VECTOR DB] Embedding model set to:', value);
    },

    _updateEmbeddingModelInfo(value) {
        const infoEl = this.container?.querySelector('#embedding-model-info');
        if (!infoEl) return;
        const infos = {
            local:   '<i class="fas fa-server"></i> <strong>Local BGE:</strong> Free, runs on-server, 768-dim, MIT — no API key required',
            voyager: '<i class="fas fa-cloud"></i> <strong>Voyage AI:</strong> voyage-4, high quality — add Voyage API key in Org Connections',
            openai:  '<i class="fas fa-cloud"></i> <strong>OpenAI:</strong> text-embedding-3-small — add OpenAI API key in Org Connections',
        };
        infoEl.innerHTML = infos[value] || '';
    },

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
        // GAP-V5: Embedding credentials are now managed via Organisation Settings > Connections.
        // This form is retired — redirect the user to the org vault instead.
        this.showEmbeddingMessage(
            'Embedding credentials are now managed in Organisation Settings > Connections. ' +
            'Add a Voyage AI or OpenAI credential there.',
            'info'
        );
        if (typeof openOrgSettingsPanel === 'function') {
            setTimeout(() => openOrgSettingsPanel('connections'), 1200);
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
        this.log.info(`[VECTOR DB] handleFileSelect called with ${files.length} file(s)`);
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = [
            // Documents
            '.pdf', '.txt', '.md', '.docx', '.doc', '.rtf', '.odt',
            // Web & Markup
            '.html', '.htm', '.xml', '.json', '.csv', '.tsv',
            // Office
            '.xlsx', '.xls', '.pptx', '.ppt', '.pages', '.key', '.numbers',
            // Publishing
            '.epub', '.tex', '.latex', '.rst', '.adoc', '.org', '.fountain',
            // Config & Data
            '.yml', '.yaml', '.toml', '.ini', '.cfg', '.log',
            // Email
            '.eml', '.msg'
        ];

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
        this.log.info(`[VECTOR DB] Process button lookup: ${processBtn ? 'found' : 'NOT FOUND'}`);
        this.log.info(`[VECTOR DB] Files in state: ${this.state.uploadedFiles.length}`);
        if (processBtn && this.state.uploadedFiles.length > 0) {
            processBtn.style.display = 'block';
            this.log.info('[VECTOR DB] Process button shown');
        } else {
            this.log.warn(`[VECTOR DB] Process button NOT shown - button: ${!!processBtn}, files: ${this.state.uploadedFiles.length}`);
        }
    },

    renderUploadedFiles() {
        const container = this.container.querySelector('#uploaded-files');
        if (!container) {
            this.log.error('[VECTOR DB] uploaded-files container not found');
            return;
        }
        this.log.info(`[VECTOR DB] Rendering ${this.state.uploadedFiles.length} file(s)`);

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
        this.log.info('[VECTOR DB] processFiles() called');
        this.log.info(`[VECTOR DB] Files to process: ${this.state.uploadedFiles.length}`);
        this.log.info(`[VECTOR DB] Connection status: ${this.state.isConnected}`);

        if (this.state.uploadedFiles.length === 0) {
            this.showMessage('No files to process', 'error');
            return;
        }

        if (!this.state.isConnected) {
            this.showMessage('Please configure a vector database provider first', 'error');
            this.switchTab('credentials');
            return;
        }

        const chunkSize = parseInt(this.container.querySelector('#chunk-size')?.value) || 800;
        const chunkOverlap = parseInt(this.container.querySelector('#chunk-overlap')?.value) || 100;
        const namespace = this.container.querySelector('#upload-namespace')?.value.trim();
        const category = this.container.querySelector('#upload-category')?.value || 'general';
        const tagsInput = this.container.querySelector('#upload-tags')?.value || '';
        const tags = tagsInput.split(',').map(t => t.trim()).filter(t => t);
        const visibility = this.container.querySelector('#upload-visibility')?.value || 'private';

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

                // Get actual logged-in user ID for ownership tracking
                const ownerUserId = (window.UserAuth && window.UserAuth.user &&
                    (window.UserAuth.user.id || window.UserAuth.user.user_id)) || 1;
                formData.append('owner_user_id', ownerUserId);

                // Get team ID (username for sub-users) if visibility is team
                if (visibility === 'team' && window.UserAuth && window.UserAuth.user) {
                    // For team visibility: use username as team_id (for sub-users)
                    const teamId = window.UserAuth.user.username;
                    if (teamId) formData.append('team_id', teamId);
                }

                formData.append('include_cloud_metadata', 'true');
                formData.append('enable_ai_retrieval', 'true');
                formData.append('file_type', file.type || 'application/octet-stream');
                formData.append('upload_timestamp', new Date().toISOString());
                // Tell the backend which provider the user has selected.
                // Without this the backend auto-detects from org vault and may pick
                // Pinecone even when the user has pgvector selected in the UI.
                formData.append('provider', this.state.selectedProvider || 'pgvector');
                // Tell the backend which embedding model to use.
                // 'local' → bypass org-vault credential lookup, use free on-server BGE.
                formData.append('embedding_provider', this.state.embeddingProvider || 'local');

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
            // Show persistent inline success below the button
            const resultElOk = this.container?.querySelector('#upload-result-message');
            if (resultElOk) {
                resultElOk.style.display = 'block';
                resultElOk.style.background = 'rgba(63,185,80,0.12)';
                resultElOk.style.border = '1px solid rgba(63,185,80,0.4)';
                resultElOk.style.color = '#3fb950';
                resultElOk.innerHTML = `<strong><i class="fas fa-check-circle"></i> Upload complete</strong> — ${this.state.uploadedFiles.length} file(s) processed successfully`;
                setTimeout(() => { resultElOk.style.display = 'none'; }, 5000);
            }

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
            // Show a persistent inline error below the upload button
            const resultEl = this.container?.querySelector('#upload-result-message');
            if (resultEl) {
                resultEl.style.display = 'block';
                resultEl.style.background = 'rgba(248,81,73,0.12)';
                resultEl.style.border = '1px solid rgba(248,81,73,0.4)';
                resultEl.style.color = '#f85149';
                resultEl.innerHTML = `<strong><i class="fas fa-exclamation-circle"></i> Upload failed</strong><br>${this.escapeHtml(error.message)}`;
            }
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
        const namespacesLabelEl = this.container.querySelector('#stat-namespaces-label');

        if (docsEl) docsEl.textContent = this.state.stats.documents || 0;
        if (vectorsEl) vectorsEl.textContent = this.formatNumber(this.state.stats.vectors || 0);
        if (namespacesEl) namespacesEl.textContent = this.state.stats.namespaces || 0;
        if (namespacesLabelEl) {
            namespacesLabelEl.textContent = this.state.selectedProvider === 'pgvector' ? 'Org Scope' : 'Namespaces';
        }
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
                <div style="font-size: 24px; color: var(--accent-primary);"><i class="fas fa-folder"></i></div>
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
            option.innerHTML = `<i class="fas fa-folder"></i> ${ns.display_name} (${ns.vector_count || 0})`;
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

        // Map folders to namespaces for compatibility
        const actualTabName = tabName === 'folders' ? 'namespaces' : tabName;
        this.state.currentTab = actualTabName;

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

        // Find tab content (try both namespaces-tab and folders-tab)
        let activeContent = container.querySelector(`#${tabName}-tab`);
        if (!activeContent && tabName === 'folders') {
            activeContent = container.querySelector(`#namespaces-tab`);
        }
        if (activeContent) {
            activeContent.style.display = 'block';
        }

        // Load data for specific tabs
        if (tabName === 'documents') {
            this.loadDocuments();
        } else if (tabName === 'namespaces' || tabName === 'folders') {
            this.loadNamespaces();
        } else if (tabName === 'search') {
            // Pre-load namespace options for search
            this.loadNamespaces();
        } else if (tabName === 'settings') {
            // Show/hide Qdrant settings based on selected provider
            this.updateSettingsView();
        }

        this.log.info(`[VECTOR DB] Switched to ${tabName} tab`);
    },

    updateSettingsView() {
        const provider = this.state.selectedProvider;
        const qdrantSection = this.container.querySelector('#qdrant-settings-section');
        if (qdrantSection) {
            qdrantSection.style.display = provider === 'qdrant' ? 'block' : 'none';
        }
    },

    toggleQdrantAdvanced() {
        const advancedConfig = this.container.querySelector('#qdrant-advanced-config');
        if (advancedConfig) {
            const isHidden = advancedConfig.style.display === 'none' || !advancedConfig.style.display;
            advancedConfig.style.display = isHidden ? 'block' : 'none';

            // If showing, load the full Qdrant tab content into it
            if (isHidden) {
                const qdrantTab = this.container.querySelector('#qdrant-tab');
                if (qdrantTab) {
                    advancedConfig.innerHTML = qdrantTab.innerHTML;
                }
            }
        }
    },

    // ==================== QDRANT PROVIDER ====================

    onProviderChange(event) {
        const provider = event.target.value;
        this.state.selectedProvider = provider;
        this.storage.set('selectedProvider', provider);

        // Update provider info with Font Awesome icons
        const infoEl = this.container.querySelector('#provider-info');
        const providerInfoMap = {
            'pinecone': '<i class="fas fa-cloud"></i> <strong>Pinecone</strong> — Cloud-managed, $70/mo, ~150ms latency, enterprise-grade',
            'qdrant': '<i class="fas fa-bolt"></i> <strong>Qdrant</strong> — FREE self-hosted, 1–5ms latency, unlimited storage',
            'pgvector': '<i class="fas fa-elephant"></i> <strong>pgvector (Supabase)</strong> — FREE, built-in, org-isolated, always available'
        };
        if (infoEl) infoEl.innerHTML = providerInfoMap[provider] || '';

        // Update tooltip visibility based on selected provider
        const allTooltips = this.container.querySelectorAll('.provider-pricing-tooltip');
        allTooltips.forEach(tooltip => {
            if (tooltip.dataset.provider === provider) {
                tooltip.classList.add('active-provider');
            } else {
                tooltip.classList.remove('active-provider');
            }
        });

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

        // Update settings view if on settings tab
        if (this.state.currentTab === 'settings') {
            this.updateSettingsView();
        }

        // Reload credentials for new provider
        this.loadCredentials();
        this.checkConnectionStatus();
    }, onQdrantDeploymentTypeChange(event) {
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
        try {
            await this.loadStats();
            if (this.state.currentTab === 'documents') {
                await this.loadDocuments();
            }
            this.showMessage('Refreshed', 'success');
        } catch (error) {
            this.log?.error('[VECTOR DB] Refresh error:', error);
        }
    },

    showMessage(message, type) {
        if (!this.container) return;  // guard: container may not be set yet
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
