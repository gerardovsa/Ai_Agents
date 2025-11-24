/**
 * Database Visualizer Module
 * Explore SQLite databases, schemas, tables, and data
 */
class DatabaseVisualizerModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);

        this.databases = [];
        this.selectedDb = null;
        this.selectedTable = null;
        this.schema = {};
        this.tabulatorTable = null;
        this.schemaTabulatorTable = null;
    }

    async initialize() {
        console.log('🔧 Initializing Database Visualizer module...');

        // Apply module colors
        this.applyModuleColors();

        // Initialize UI
        await super.initialize();

        // Load available databases
        await this.loadDatabases();

        console.log('Database Visualizer module ready');
    }

    // ==================== COLOR APPLICATION ====================

    applyModuleColors() {
        const colors = (this.manifest && this.manifest.colors) ? this.manifest.colors : null;
        const tabContainer = document.getElementById(`tab-${this.moduleId}`);

        if (tabContainer && colors) {
            tabContainer.style.setProperty('--module-primary', colors.primary);
            tabContainer.style.setProperty('--module-secondary', colors.secondary);
            tabContainer.style.setProperty('--module-hover', colors.hover);
        }
    }

    // ==================== TAB INITIALIZATION ====================

    initializeSubTabs() {
        this.initializeDatabases();
        this.initializeSchema();
        this.initializeQuery();
    }

    // ==================== TAB 1: DATABASES LIST ====================

    initializeDatabases() {
        const container = this.getSubTabContainer('databases');
        const primaryColor = (this.manifest && this.manifest.colors && this.manifest.colors.primary) ? this.manifest.colors.primary : (this.manifest && this.manifest.color) ? this.manifest.color : 'var(--accent-primary)';

        container.innerHTML = `
            <div class="module-header" style="border-bottom: 2px solid ${primaryColor};">
                <div class="module-header-left">
                    <h2 class="module-title">
                        <i class="fas fa-database" style="color: ${primaryColor};"></i>
                        Available Databases
                    </h2>
                    <p class="module-description">Discover .db files in your project</p>
                </div>
                <div class="module-header-right">
                    <button class="btn-secondary" id="refresh-databases-btn">
                        <i class="fas fa-sync"></i> Refresh
                    </button>
                </div>
            </div>
            
            <!-- Database Stats -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px;">
                <div class="stat-card" style="border-left: 3px solid ${primaryColor};">
                    <div class="stat-icon" style="background: ${this.lightenColor(primaryColor, 0.1)}; color: ${primaryColor};">
                        <i class="fas fa-database"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-label">Total Databases</div>
                        <div class="stat-value" id="stat-total-dbs">0</div>
                    </div>
                </div>
                <div class="stat-card" style="border-left: 3px solid ${primaryColor};">
                    <div class="stat-icon" style="background: ${this.lightenColor(primaryColor, 0.1)}; color: ${primaryColor};">
                        <i class="fas fa-table"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-label">Total Tables</div>
                        <div class="stat-value" id="stat-total-tables">0</div>
                    </div>
                </div>
                <div class="stat-card" style="border-left: 3px solid ${primaryColor};">
                    <div class="stat-icon" style="background: ${this.lightenColor(primaryColor, 0.1)}; color: ${primaryColor};">
                        <i class="fas fa-folder"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-label">Total Size</div>
                        <div class="stat-value" id="stat-total-size">0 MB</div>
                    </div>
                </div>
                <div class="stat-card" style="border-left: 3px solid ${primaryColor};">
                    <div class="stat-icon" style="background: ${this.lightenColor(primaryColor, 0.1)}; color: ${primaryColor};">
                        <i class="fas fa-clock"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-label">Last Scanned</div>
                        <div class="stat-value" id="stat-last-scan">Never</div>
                    </div>
                </div>
            </div>
            
            <!-- Databases Grid -->
            <div class="dashboard-card">
                <div class="dashboard-card-header">
                    <i class="fas fa-list dashboard-card-icon" style="color: ${primaryColor};"></i>
                    <span class="dashboard-card-title">Database Files</span>
                </div>
                <div id="databases-grid" style="padding: 16px;"></div>
            </div>
        `;

        // Attach event listener to refresh button
        const refreshBtn = container.querySelector('#refresh-databases-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadDatabases());
        }
    }

    // ==================== TAB 2: SCHEMA EXPLORER ====================

    initializeSchema() {
        const container = this.getSubTabContainer('schema');
        const primaryColor = (this.manifest && this.manifest.colors && this.manifest.colors.primary) ? this.manifest.colors.primary : (this.manifest && this.manifest.color) ? this.manifest.color : 'var(--accent-primary)';

        container.innerHTML = `
            <div class="module-header" style="border-bottom: 2px solid ${primaryColor};">
                <div class="module-header-left">
                    <h2 class="module-title">
                        <i class="fas fa-sitemap" style="color: ${primaryColor};"></i>
                        Schema Explorer
                    </h2>
                    <p class="module-description">Explore database structure and relationships</p>
                </div>
                <div class="module-header-right">
                    <select id="schema-db-selector" class="form-control" style="width: 300px; margin-right: 8px;">
                        <option value="">Select Database...</option>
                    </select>
                    <button class="btn-primary" id="export-schema-btn" style="background: ${primaryColor}; border-color: ${primaryColor};">
                        <i class="fas fa-download"></i> Export Schema
                    </button>
                </div>
            </div>
            
            <!-- Schema View -->
            <div style="display: grid; grid-template-columns: 300px 1fr; gap: 16px; height: calc(100vh - 280px);">
                <!-- Tables List -->
                <div class="dashboard-card" style="height: 100%; overflow-y: auto; display: flex; flex-direction: column;">
                    <div class="dashboard-card-header" style="flex-shrink: 0;">
                        <button id="back-to-databases-btn" class="btn-sm" style="background: transparent; border: 1px solid ${primaryColor}; color: ${primaryColor}; padding: 4px 8px; font-size: 11px; margin-right: 8px;" title="Back to Databases">
                            <i class="fas fa-arrow-left"></i>
                        </button>
                        <i class="fas fa-table dashboard-card-icon" style="color: ${primaryColor};"></i>
                        <span class="dashboard-card-title">Tables</span>
                    </div>
                    <div id="schema-tables-list" style="padding: 8px; flex: 1; overflow-y: auto;"></div>
                </div>
                
                <!-- Right Panel with Fixed Toggle Buttons -->
                <div style="display: flex; flex-direction: column; height: 100%;">
                    <!-- Fixed Toggle Buttons (always visible when table selected) -->
                    <div id="schema-view-controls" style="display: none; padding: 12px; background: var(--bg-secondary); border-radius: 8px; margin-bottom: 16px;">
                        <div style="display: flex; gap: 8px; justify-content: center;">
                            <button id="view-structure-btn" class="btn-sm" style="background: ${primaryColor}; border-color: ${primaryColor}; color: white;">
                                <i class="fas fa-columns"></i> Structure
                            </button>
                            <button id="view-data-btn" class="btn-sm btn-secondary">
                                <i class="fas fa-table"></i> Data
                            </button>
                        </div>
                    </div>
                    
                    <!-- Scrollable Cards Container -->
                    <div style="flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 16px;">
                        <!-- Table Structure Card -->
                        <div id="schema-structure-card" class="dashboard-card" style="display: none;">
                            <div class="dashboard-card-header">
                                <i class="fas fa-columns dashboard-card-icon" style="color: ${primaryColor};"></i>
                                <span class="dashboard-card-title">Table Structure</span>
                            </div>
                            <div id="schema-table-details" style="padding: 16px;">
                                <p class="text-secondary" style="text-align: center; padding: 40px;">
                                    Select a table to view its structure
                                </p>
                            </div>
                        </div>
                        
                        <!-- Table Data Card -->
                        <div id="schema-data-card" class="dashboard-card" style="display: none;">
                            <div class="dashboard-card-header">
                                <i class="fas fa-table dashboard-card-icon" style="color: ${primaryColor};"></i>
                                <span class="dashboard-card-title">Table Data</span>
                                <div style="margin-left: auto;">
                                    <span class="text-secondary" style="font-size: 12px;">
                                        <span id="schema-data-row-count">0</span> rows
                                    </span>
                                </div>
                            </div>
                            <div id="schema-table-data" style="padding: 16px;"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Attach event listeners
        const schemaDbSelector = container.querySelector('#schema-db-selector');
        const exportSchemaBtn = container.querySelector('#export-schema-btn');
        const structureBtn = container.querySelector('#view-structure-btn');
        const dataBtn = container.querySelector('#view-data-btn');
        const backToDatabasesBtn = container.querySelector('#back-to-databases-btn');

        if (schemaDbSelector) {
            schemaDbSelector.addEventListener('change', (e) => this.loadSchema(e.target.value));
        }

        if (exportSchemaBtn) {
            exportSchemaBtn.addEventListener('click', () => this.exportSchema());
        }

        // Back to databases button - switch to databases tab
        if (backToDatabasesBtn) {
            backToDatabasesBtn.addEventListener('click', () => {
                // Switch to databases tab
                this.switchTab('databases');
            });
        }

        // Toggle structure card
        if (structureBtn) {
            structureBtn.addEventListener('click', () => this.toggleSchemaCard('structure'));
        }

        // Toggle data card
        if (dataBtn) {
            dataBtn.addEventListener('click', () => this.toggleSchemaCard('data'));
        }

        // Populate the selector
        this.populateDbSelectors();
    }

    // ==================== TAB 3: DATA VIEWER ====================


    initializeQuery() {
        const container = this.getSubTabContainer('query');
        const primaryColor = (this.manifest && this.manifest.colors && this.manifest.colors.primary) ? this.manifest.colors.primary : (this.manifest && this.manifest.color) ? this.manifest.color : 'var(--accent-primary)';

        container.innerHTML = `
            <div class="module-header" style="border-bottom: 2px solid ${primaryColor};">
                <div class="module-header-left">
                    <h2 class="module-title">
                        <i class="fas fa-table" style="color: ${primaryColor};"></i>
                        Data Viewer
                    </h2>
                    <p class="module-description">Browse table data with Tabulator</p>
                </div>
                <div class="module-header-right">
                    <select id="query-db-selector" class="form-control" style="width: 250px; margin-right: 8px;">
                        <option value="">Select Database...</option>
                    </select>
                    <select id="query-table-selector" class="form-control" style="width: 250px; margin-right: 8px;">
                        <option value="">Select Table...</option>
                    </select>
                    <button class="btn-primary" id="export-table-btn" style="background: ${primaryColor}; border-color: ${primaryColor};">
                        <i class="fas fa-download"></i> Export CSV
                    </button>
                </div>
            </div>
            
            <!-- Data Table -->
            <div class="dashboard-card" style="margin-bottom: 16px;">
                <div class="dashboard-card-header">
                    <i class="fas fa-table dashboard-card-icon" style="color: ${primaryColor};"></i>
                    <span class="dashboard-card-title">Table Data</span>
                    <div style="margin-left: auto; display: flex; gap: 8px; align-items: center;">
                        <input type="text" id="table-search" class="form-control" placeholder="Search..." style="width: 200px;">
                        <span class="text-secondary" style="font-size: 12px; margin-left: 8px;">
                            <span id="table-row-count">0</span> rows
                        </span>
                    </div>
                </div>
                <div id="tabulator-container" style="min-height: 400px;"></div>
            </div>
        `;

        // Attach event listeners
        const queryDbSelector = container.querySelector('#query-db-selector');
        const queryTableSelector = container.querySelector('#query-table-selector');
        const exportTableBtn = container.querySelector('#export-table-btn');

        if (queryDbSelector) {
            queryDbSelector.addEventListener('change', (e) => this.onQueryDbChange(e.target.value));
        }

        if (queryTableSelector) {
            queryTableSelector.addEventListener('change', (e) => this.loadTableData(e.target.value));
        }

        if (exportTableBtn) {
            exportTableBtn.addEventListener('click', () => this.exportTableData());
        }

        // Populate the selectors
        this.populateDbSelectors();
    }


    // ==================== DATA LOADING ====================

    async loadDatabases() {
        try {
            console.log('🔍 Discovering databases...');

            const response = await fetch('/api/database-visualizer/list-databases');

            if (!response.ok) {
                throw new Error(`Failed to load databases: ${response.statusText}`);
            }

            const result = await response.json();
            this.databases = result.databases || [];

            console.log(`Found ${this.databases.length} databases`);

            // Update stats
            this.updateDatabaseStats();

            // Render database grid
            this.renderDatabaseGrid();

            // Populate selectors
            this.populateDbSelectors();

        } catch (error) {
            console.error(' Failed to load databases:', error);
            // FIX: Pass container element as first argument
            const container = document.getElementById('databases-grid');
            if (container) {
                this.showError(container, error.message);
            }
        }
    }

    async loadSchema(dbPath) {
        if (!dbPath) return;

        try {
            console.log(`🔍 Loading schema for: ${dbPath}`);

            const response = await fetch(`/api/database-visualizer/schema?db_path=${encodeURIComponent(dbPath)}`);

            if (!response.ok) {
                throw new Error(`Failed to load schema: ${response.statusText}`);
            }

            const result = await response.json();
            this.schema = result.schema || {};
            this.selectedDb = dbPath;

            console.log(`Loaded schema: ${Object.keys(this.schema).length} tables`);

            // Render tables list
            this.renderSchemaTablesList();

        } catch (error) {
            console.error(' Failed to load schema:', error);
            this.showError('Failed to load schema');
        }
    }

    async loadTableData(tableName) {
        if (!this.selectedDb || !tableName) return;

        try {
            console.log(`🔍 Loading data from table: ${tableName}`);

            const response = await fetch(`/api/database-visualizer/table-data?db_path=${encodeURIComponent(this.selectedDb)}&table=${encodeURIComponent(tableName)}`);

            if (!response.ok) {
                throw new Error(`Failed to load table data: ${response.statusText}`);
            }

            const result = await response.json();
            this.selectedTable = tableName;

            console.log(`Loaded ${result.data.length} rows from ${tableName}`);

            // Render with Tabulator
            this.renderTabulatorTable(result.data, result.columns);

            // Update row count
            document.getElementById('table-row-count').textContent = result.data.length;

        } catch (error) {
            console.error(' Failed to load table data:', error);
            this.showError('Failed to load table data');
        }
    }

    // ==================== RENDERING ====================

    updateDatabaseStats() {
        const totalDbs = this.databases.length;
        const totalTables = this.databases.reduce((sum, db) => sum + (db.table_count || 0), 0);
        const totalSize = this.databases.reduce((sum, db) => sum + (db.size_bytes || 0), 0);
        const totalSizeMB = (totalSize / (1024 * 1024)).toFixed(2);

        document.getElementById('stat-total-dbs').textContent = totalDbs;
        document.getElementById('stat-total-tables').textContent = totalTables;
        document.getElementById('stat-total-size').textContent = `${totalSizeMB} MB`;
        document.getElementById('stat-last-scan').textContent = new Date().toLocaleTimeString();
    }

    renderDatabaseGrid() {
        const container = document.getElementById('databases-grid');
        const primaryColor = (this.manifest && this.manifest.colors && this.manifest.colors.primary)
            ? this.manifest.colors.primary
            : 'var(--accent-primary)';

        if (this.databases.length === 0) {
            container.innerHTML = '<p class="text-secondary" style="text-align: center; padding: 40px;">No database files found</p>';
            return;
        }

        // Create HTML without onclick handlers
        const gridHTML = this.databases.map(db => `
            <div class="database-card" style="background: rgba(139, 92, 246, 0.05); border: 1px solid ${primaryColor}; border-radius: 8px; padding: 16px; margin-bottom: 12px; cursor: pointer; transition: all 0.2s;" 
                data-db-path="${db.path}"
                onmouseover="this.style.background='rgba(139, 92, 246, 0.1)'" 
                onmouseout="this.style.background='rgba(139, 92, 246, 0.05)'">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                            <i class="fas fa-database" style="color: ${primaryColor}; font-size: 24px;"></i>
                            <div>
                                <h3 style="margin: 0; font-size: 16px; font-weight: 600;">${db.name}</h3>
                                <p style="margin: 4px 0 0 0; font-size: 11px; color: var(--text-secondary); font-family: monospace;">${db.relative_path}</p>
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 12px;">
                            <div>
                                <div style="font-size: 10px; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 4px;">Tables</div>
                                <div style="font-size: 14px; font-weight: 600; color: ${primaryColor};">${db.table_count || 0}</div>
                            </div>
                            <div>
                                <div style="font-size: 10px; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 4px;">Size</div>
                                <div style="font-size: 14px; font-weight: 600;">${this.formatFileSize(db.size_bytes || 0)}</div>
                            </div>
                            <div>
                                <div style="font-size: 10px; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 4px;">Modified</div>
                                <div style="font-size: 14px; font-weight: 600;">${this.formatDate(db.modified_at)}</div>
                            </div>
                        </div>
                    </div>
                    <button class="btn-sm btn-primary database-explore-btn">
                        <i class="fas fa-search"></i> Explore
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = gridHTML;

        // Attach event listeners AFTER rendering
        container.querySelectorAll('.database-card').forEach(card => {
            const dbPath = card.getAttribute('data-db-path');

            card.addEventListener('click', (e) => {
                if (!e.target.closest('.database-explore-btn')) {
                    this.selectDatabase(dbPath);
                }
            });

            card.querySelector('.database-explore-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectDatabase(dbPath);
            });
        });
    }



    renderSchemaTablesList() {
        const container = document.getElementById('schema-tables-list');
        const primaryColor = (this.manifest && this.manifest.colors && this.manifest.colors.primary)
            ? this.manifest.colors.primary
            : 'var(--accent-primary)';

        const tables = Object.keys(this.schema);

        if (tables.length === 0) {
            container.innerHTML = '<p class="text-secondary" style="padding: 16px; font-size: 12px;">No tables found</p>';
            return;
        }

        const tablesHTML = tables.map(tableName => {
            const columns = this.schema[tableName];
            const pkColumns = columns.filter(c => c.pk).length;

            return `
                <div class="table-list-item" data-table-name="${tableName}" style="padding: 12px; margin-bottom: 8px; background: rgba(139, 92, 246, 0.05); border: 1px solid ${primaryColor}; border-radius: 6px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='rgba(139, 92, 246, 0.1)'" onmouseout="this.style.background='rgba(139, 92, 246, 0.05)'">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                        <i class="fas fa-table" style="color: ${primaryColor};"></i>
                        <span style="font-weight: 600; font-size: 13px;">${tableName}</span>
                    </div>
                    <div style="font-size: 11px; color: var(--text-secondary);">
                        ${columns.length} columns ${pkColumns > 0 ? `• ${pkColumns} PK` : ''}
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = tablesHTML;

        // Attach event listeners to table items
        container.querySelectorAll('.table-list-item').forEach(item => {
            item.addEventListener('click', () => {
                // Remove active class from all items
                container.querySelectorAll('.table-list-item').forEach(i => {
                    i.classList.remove('active');
                    i.style.background = 'rgba(139, 92, 246, 0.05)';
                    i.style.borderColor = primaryColor;
                    i.style.borderWidth = '1px';
                });

                // Add active class to clicked item
                item.classList.add('active');
                item.style.background = 'rgba(139, 92, 246, 0.2)';
                item.style.borderColor = primaryColor;
                item.style.borderWidth = '2px';
                item.style.boxShadow = `0 0 8px ${primaryColor}40`;

                const tableName = item.getAttribute('data-table-name');
                this.selectSchemaTable(tableName);
            });
        });
    }

    selectSchemaTable(tableName) {
        const container = document.getElementById('schema-table-details');
        const primaryColor = (this.manifest && this.manifest.colors && this.manifest.colors.primary)
            ? this.manifest.colors.primary
            : 'var(--accent-primary)';

        const columns = this.schema[tableName];

        if (!columns || columns.length === 0) {
            container.innerHTML = '<p class="text-secondary" style="text-align: center; padding: 40px;">No column information available</p>';
            return;
        }

        const columnsHTML = `
            <h3 style="margin-bottom: 16px; font-size: 16px; color: ${primaryColor};">
                <i class="fas fa-table"></i> ${tableName}
            </h3>
            
            <div style="background: rgba(0,0,0,0.2); border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
                    <div>
                        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px;">Total Columns</div>
                        <div style="font-size: 20px; font-weight: 600;">${columns.length}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px;">Primary Keys</div>
                        <div style="font-size: 20px; font-weight: 600;">${columns.filter(c => c.pk).length}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px;">Not Null</div>
                        <div style="font-size: 20px; font-weight: 600;">${columns.filter(c => c.notnull).length}</div>
                    </div>
                </div>
            </div>
            
            <table class="data-table" style="width: 100%;">
                <thead>
                    <tr>
                        <th>Column Name</th>
                        <th>Data Type</th>
                        <th>Constraints</th>
                    </tr>
                </thead>
                <tbody>
                    ${columns.map(col => `
                        <tr>
                            <td>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    ${col.pk ? `<i class="fas fa-key" style="color: ${primaryColor};" title="Primary Key"></i>` : ''}
                                    <span style="font-family: monospace; font-weight: ${col.pk ? '600' : '400'};">${col.name}</span>
                                </div>
                            </td>
                            <td><span class="badge" style="background: rgba(139, 92, 246, 0.2); color: ${primaryColor};">${col.type || 'TEXT'}</span></td>
                            <td>
                                ${col.notnull ? '<span class="badge" style="background: rgba(239, 68, 68, 0.2); color: #f87171;">NOT NULL</span>' : ''}
                                ${col.pk ? '<span class="badge" style="background: rgba(34, 197, 94, 0.2); color: #4ade80;">PRIMARY KEY</span>' : ''}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = columnsHTML;

        // Store selected table for toggle functionality
        this.selectedTable = tableName;

        // Show control buttons when a table is selected
        const controlsDiv = document.getElementById('schema-view-controls');
        if (controlsDiv) {
            controlsDiv.style.display = 'block';
        }
    }

    // ==================== SCHEMA VIEW TOGGLE ====================

    toggleSchemaCard(view) {
        const primaryColor = (this.manifest && this.manifest.colors && this.manifest.colors.primary)
            ? this.manifest.colors.primary
            : 'var(--accent-primary)';

        const structureCard = document.getElementById('schema-structure-card');
        const dataCard = document.getElementById('schema-data-card');
        const structureBtn = document.getElementById('view-structure-btn');
        const dataBtn = document.getElementById('view-data-btn');

        if (view === 'structure') {
            // Toggle structure card
            const isVisible = structureCard.style.display === 'block';
            structureCard.style.display = isVisible ? 'none' : 'block';

            // Update button style
            if (isVisible) {
                structureBtn.className = 'btn-sm btn-secondary';
                structureBtn.style.background = '';
                structureBtn.style.borderColor = '';
                structureBtn.style.color = '';
            } else {
                structureBtn.className = 'btn-sm';
                structureBtn.style.background = primaryColor;
                structureBtn.style.borderColor = primaryColor;
                structureBtn.style.color = 'white';
            }

        } else if (view === 'data') {
            // Toggle data card
            const isVisible = dataCard.style.display === 'block';
            dataCard.style.display = isVisible ? 'none' : 'block';

            // Update button style
            if (isVisible) {
                dataBtn.className = 'btn-sm btn-secondary';
                dataBtn.style.background = '';
                dataBtn.style.borderColor = '';
                dataBtn.style.color = '';

                // Destroy Tabulator instance if exists
                if (this.schemaTabulatorTable) {
                    this.schemaTabulatorTable.destroy();
                    this.schemaTabulatorTable = null;
                }
            } else {
                dataBtn.className = 'btn-sm';
                dataBtn.style.background = primaryColor;
                dataBtn.style.borderColor = primaryColor;
                dataBtn.style.color = 'white';

                // Load table data if we have a selected table
                if (this.selectedTable && this.selectedDb) {
                    this.loadSchemaTableData(this.selectedTable);
                } else {
                    const dataContainer = document.getElementById('schema-table-data');
                    dataContainer.innerHTML = '<p class="text-secondary" style="text-align: center; padding: 40px;">Select a table to view data</p>';
                }
            }
        }
    }

    async loadSchemaTableData(tableName) {
        const container = document.getElementById('schema-table-data');
        container.innerHTML = '<div style="text-align: center; padding: 40px;"><i class="fas fa-spinner fa-spin" style="font-size: 24px;"></i><p>Loading data...</p></div>';

        try {
            const response = await fetch(`/api/database-visualizer/table-data?db_path=${encodeURIComponent(this.selectedDb)}&table=${encodeURIComponent(tableName)}&limit=100`);
            const result = await response.json();

            if (result.success && result.data) {
                // Update row count
                const rowCountSpan = document.getElementById('schema-data-row-count');
                if (rowCountSpan) {
                    rowCountSpan.textContent = result.data.length;
                }

                // Create Tabulator table in schema view
                this.renderSchemaTabulator(result.data, result.columns);
            } else {
                container.innerHTML = `<p class="text-danger" style="text-align: center; padding: 40px;">Failed to load data: ${result.error || 'Unknown error'}</p>`;
            }
        } catch (error) {
            console.error('Error loading schema table data:', error);
            container.innerHTML = `<p class="text-danger" style="text-align: center; padding: 40px;">Error: ${error.message}</p>`;
        }
    }

    renderSchemaTabulator(data, columns) {
        const container = document.getElementById('schema-table-data');
        const primaryColor = (this.manifest && this.manifest.colors && this.manifest.colors.primary)
            ? this.manifest.colors.primary
            : 'var(--accent-primary)';

        // Destroy existing schema tabulator if it exists
        if (this.schemaTabulatorTable) {
            this.schemaTabulatorTable.destroy();
        }

        // Create container for Tabulator
        container.innerHTML = '<div id="schema-tabulator-table"></div>';

        // Prepare columns with collapse functionality
        const tabulatorColumns = columns.map(col => ({
            title: col,
            field: col,
            headerFilter: 'input',
            headerFilterPlaceholder: `Filter ${col}...`,
            maxWidth: 200,  // Default max width
            minWidth: 30,   // Allow collapsing to narrow column
            formatter: 'textarea',
            variableHeight: true,
            headerMenu: [
                {
                    label: "<i class='fas fa-compress'></i> Collapse Column",
                    action: function (e, column) {
                        const currentWidth = column.getWidth();
                        if (currentWidth > 40) {
                            // Collapse column
                            column.setWidth(30);
                            column.updateDefinition({
                                titleFormatter: function (cell) {
                                    return `<div style="writing-mode: vertical-rl; transform: rotate(180deg); white-space: nowrap; height: 100%; display: flex; align-items: center; justify-content: center;">${cell.getValue()}</div>`;
                                }
                            });
                        } else {
                            // Expand column
                            column.setWidth(200);
                            column.updateDefinition({
                                titleFormatter: undefined
                            });
                        }
                    }
                },
                {
                    label: "<i class='fas fa-expand'></i> Expand Column",
                    action: function (e, column) {
                        column.setWidth(200);
                        column.updateDefinition({
                            titleFormatter: undefined
                        });
                    }
                }
            ]
        }));

        // Initialize Tabulator
        this.schemaTabulatorTable = new Tabulator('#schema-tabulator-table', {
            data: data,
            columns: tabulatorColumns,
            layout: 'fitDataStretch',
            pagination: true,
            paginationSize: 50,
            paginationSizeSelector: [25, 50, 100, 200],
            movableColumns: true,
            resizableRows: true,
            resizableColumns: true,
            headerSort: true,
            headerSortTristate: true,
            responsiveLayout: 'collapse',
            height: '500px'
        });
    }

    renderTabulatorTable(data, columns) {
        const container = document.getElementById('tabulator-container');
        const primaryColor = (this.manifest && this.manifest.colors && this.manifest.colors.primary)
            ? this.manifest.colors.primary
            : 'var(--accent-primary)';

        // Destroy existing table
        if (this.tabulatorTable) {
            this.tabulatorTable.destroy();
        }

        // Build column definitions
        const columnDefs = columns.map(col => ({
            title: col,
            field: col,
            headerFilter: "input",
            headerFilterPlaceholder: `Filter ${col}...`,
            formatter: (cell) => {
                const value = cell.getValue();
                if (value === null) return '<span style="color: #666; font-style: italic;">NULL</span>';
                if (typeof value === 'boolean') return value ? '✓' : '✗';
                return value;
            }
        }));

        // Initialize Tabulator
        this.tabulatorTable = new Tabulator(container, {
            data: data,
            columns: columnDefs,
            layout: "fitDataFill",
            height: "500px",
            pagination: true,
            paginationSize: 50,
            paginationSizeSelector: [25, 50, 100, 200, 500],
            movableColumns: true,
            resizableColumns: true,
            tooltips: true,
            headerSort: true,
            headerSortTristate: true,
            placeholder: "No Data Available",
        });

        // Search functionality
        const searchInput = document.getElementById('table-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.tabulatorTable.setFilter([
                    columns.map(col => ({
                        field: col,
                        type: 'like',
                        value: e.target.value
                    }))
                ]);
            });
        }
    }

    // ==================== ACTIONS ====================

    selectDatabase(dbPath) {
        this.selectedDb = dbPath;
        console.log(`📂 Selected database: ${dbPath}`);

        this.switchSubTab('schema');  // CORRECT METHOD NAME

        document.getElementById('schema-db-selector').value = dbPath;
        this.loadSchema(dbPath);
    }

    exploreDatabase(dbPath) {
        this.selectedDb = dbPath;

        this.switchSubTab('schema');  // CORRECT METHOD NAME

        document.getElementById('schema-db-selector').value = dbPath;
        this.loadSchema(dbPath);
    }

    onQueryDbChange(dbPath) {
        if (!dbPath) return;

        this.selectedDb = dbPath;
        this.loadSchema(dbPath).then(() => {
            // Populate table selector
            const tableSelector = document.getElementById('query-table-selector');
            const tables = Object.keys(this.schema);

            tableSelector.innerHTML = '<option value="">Select Table...</option>' +
                tables.map(t => `<option value="${t}">${t}</option>`).join('');
        });
    }

    populateDbSelectors() {
        const selectors = ['schema-db-selector', 'query-db-selector'];

        selectors.forEach(selectorId => {
            const selector = document.getElementById(selectorId);
            if (selector) {
                selector.innerHTML = '<option value="">Select Database...</option>' +
                    this.databases.map(db => `<option value="${db.path}">${db.name}</option>`).join('');
            }
        });
    }

    exportSchema() {
        if (!this.schema || Object.keys(this.schema).length === 0) {
            alert('No schema loaded');
            return;
        }

        const schemaText = JSON.stringify(this.schema, null, 2);
        const blob = new Blob([schemaText], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `schema_${this.selectedDb.split('/').pop()}.json`;
        a.click();

        URL.revokeObjectURL(url);
    }

    exportTableData() {
        if (!this.tabulatorTable) {
            alert('No table data loaded');
            return;
        }

        this.tabulatorTable.download("csv", `${this.selectedTable}_data.csv`);
    }

    // ==================== UTILITIES ====================

    lightenColor(color, opacity) {
        const hex = color.replace('#', '');
        const r = parseInt(hex.substr(0, 2), 16);
        const g = parseInt(hex.substr(2, 2), 16);
        const b = parseInt(hex.substr(4, 2), 16);
        return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }
}

// Register module
window.ModuleRegistry['database-visualizer'] = DatabaseVisualizerModule;
