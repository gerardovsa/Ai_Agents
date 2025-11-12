# 🤖 AI Prompt - Convert Code to AI-Integrated Module Format

**Purpose:** Convert existing HTML/JavaScript/Dashboard code into the modular architecture format with AI tool integration  
**Version:** 3.0.0  
**Last Updated:** November 3, 2025  
**Status:** ✅ Updated with November 2025 standards

---

## 📚 Before Using This Prompt

**IMPORTANT:** Read these first for context:
1. **[README.md](README.md)** - Documentation overview
2. **[MODULE_BEST_PRACTICES.md](MODULE_BEST_PRACTICES.md)** - The Four Commandments
3. **[Instructions.md](Instructions.md)** - Technical reference

**Reference Implementation:** Study `UI/external/modules/stock-management/` ⭐
- 1,375+ lines of production code
- Backend integration (Flask routes)
- AI features (invoice processing)
- Comprehensive documentation (8+ files)
- This is the gold standard!

---

## How to Use This Prompt

1. **Study existing modules** in `UI/external/modules/` (salesforce, database-visualizer, stock-management)
2. **Copy this entire prompt** to your AI assistant (ChatGPT, Claude, etc.)
3. **Provide your code** as context
4. **Receive** converted module-ready code with AI tool integration
5. **Validate** with `python scripts/maintenance/validate_modules.py`

---

## AI PROMPT STARTS HERE

---

### Context: AI-Integrated Modular Architecture System

You are helping convert existing dashboard/platform code into a modular plugin format for the Business AI Platform. The system uses:

- **ModuleManager**: Handles dynamic module registration and loading
- **BaseModule**: Base class that all modules extend
- **Auto-Discovery**: Modules are automatically detected from `external/modules/manifest.json`
- **Consistent Styling**: All modules inherit global CSS variables with per-module pastel colors
- **AI Integration**: Each module provides tools that AI can call to interact with data
- **Smart Tools**: Multi-operation bundled tools for efficiency

### System Architecture

```
UI/external/modules/
├── manifest.json              ← Registry of all modules
│
└── [module-id]/              ← Each module in its own folder
    ├── manifest.json         ← Module configuration (REQUIRED)
    ├── [module-id].js        ← Module implementation (REQUIRED)
    ├── [module-id].css       ← Optional custom styles
    ├── README.md             ← Module documentation (RECOMMENDED)
    │
    ├── [module-id]-enhanced.js    ← Optional enhanced features
    ├── [module_id]_routes.py      ← Optional Flask backend routes
    ├── database-config.json       ← Optional database config
    │
    └── docs/                 ← Optional documentation folder
        ├── IMPLEMENTATION_COMPLETE.md
        ├── INTEGRATION_GUIDE.md
        └── TEST_*.html       ← Test/demo files
```

**CRITICAL RULES (The Four Commandments):**
1. **Folder name MUST match module ID** (calculator-module/ ≠ quote-calculator = 404!)
2. **File names MUST match module ID** (module-id.js, module-id.css)
3. **Class name = PascalCase(ID) + "Module"** (StockManagementModule)
4. **MUST extend BaseModule** (class MyModule extends BaseModule)

**Validation:** Run `python scripts/maintenance/validate_modules.py` before deployment

### Module Structure Requirements

Every module must:
1. **Extend `BaseModule` class** - Inherit common functionality
2. **Register itself:** `window.ModuleRegistry['module-id'] = ModuleClass;`
3. **Have `manifest.json`** - Configuration with color scheme
4. **Folder name = Module ID** - CRITICAL: Exact match required (see quote-calculator example)
5. **File naming:** `module-id.js`, `module-id.css` (or list CSS in manifest dependencies)
6. **Class naming:** PascalCase(ID) + "Module" (e.g., `StockManagementModule`)
7. **Module ID format:** lowercase-with-hyphens (e.g., `stock-management`, `quote-calculator`)
8. **Constructor pattern:** `constructor(moduleId) { super(moduleId); }`
9. **Initialize method:** `async initialize() { await super.initialize(); }`

**Optional but Recommended:**
- Backend routes: `[module_id]_routes.py` (Flask Blueprint pattern)
- Enhanced features: `[module-id]-enhanced.js`
- Documentation: `README.md`, implementation guides
- Test files: `TEST_*.html`, `USAGE_EXAMPLE.html`

**Reference:** Study `UI/external/modules/stock-management/` for complete example

---

## Your Task

I have existing code (HTML/JavaScript/CSS) that I want to convert into a module. Please:

1. **Analyze the existing code structure**
2. **Identify main sections** (these become sub-tabs)
3. **Extract data loading logic** (becomes module methods)
4. **Convert UI components** to use BaseModule utilities
5. **Generate module files** (manifest.json + module.js + optional CSS)

---

## 🔍 Analysis Questions

Before converting, please answer:

1. **What platform is this for?** (e.g., Salesforce, WooCommerce, Asana, Custom Dashboard)
2. **What are the main sections?** (these become sub-tabs)
3. **What data does it display?** (tables, charts, stats, lists)
4. **What APIs does it call?** (endpoints for data loading)
5. **What actions can users take?** (buttons, forms, interactions)
6. **NEW: What granular operations exist?** (CRUD: create, read, update, delete)
7. **NEW: What batch operations would be useful?** (bulk updates, multi-step workflows)
8. **NEW: What analytics/reports are needed?** (inventory reports, performance analysis)

---

## 🎨 Module Color System (NEW!)

Each module has its own **pastel color scheme**:

**Recommended Pastel Colors:**
- WooCommerce: `#b4a7d6` (Pastel Purple)
- Salesforce: `#7fb3d5` (Pastel Blue)
- Asana: `#f4a5ae` (Pastel Pink)
- HubSpot: `#ffb347` (Pastel Orange)
- Shopify: `#96d8a2` (Pastel Green)
- Jira: `#6fb3e0` (Pastel Light Blue)

**Color Usage:**
- **Primary**: Main brand color (borders, active states, icons)
- **Secondary**: Lighter gradient of primary (backgrounds, accents)
- **Hover**: Slightly darker than primary

**Example Manifest Colors:**
```json
{
  "colors": {
    "primary": "#b4a7d6",
    "secondary": "#d4c4f9",
    "hover": "#9f8fc9"
  }
}
```

---

## 🔧 AI Tool Integration (NEW!)

### Tool Types

Every module needs **TWO types of tools**:

#### 1. Granular API Tools (Basic Operations)
- Direct 1:1 mapping to platform APIs
- Single operation per tool
- CRUD operations: Create, Read, Update, Delete
- Count: ~10-15 per platform

**Examples:**
- `[module]_get_products` - List/search products
- `[module]_create_product` - Create single product
- `[module]_update_product` - Update single product
- `[module]_delete_product` - Delete single product

#### 2. Smart Bundled Tools (Multi-Operation)
- Multiple API calls bundled into ONE tool call
- Efficiency: 90-95% reduction in calls
- Complex workflows automated
- Count: ~3-5 per platform

**Examples:**
- `[module]_smart_bulk_update_prices` - Update 50 prices in 1 call
- `[module]_smart_inventory_report` - Analyze all products + recommendations
- `[module]_smart_process_bulk_orders` - Process 20 orders in 1 call
- `[module]_export_dashboard_data` - Export current view for AI

### Smart Tool Patterns

**Pattern 1: Batch Operations**
```json
{
  "name": "module_smart_bulk_update",
  "description": "🤖 SMART TOOL: Update multiple items in ONE call",
  "category": "smart_bundled",
  "efficiency": "90% reduction (10 calls → 1 call)"
}
```

**Pattern 2: Analysis + Recommendations**
```json
{
  "name": "module_smart_inventory_report",
  "description": "🤖 SMART TOOL: Analyze inventory with low stock alerts",
  "category": "SMART Tools",
  "efficiency": "Analyzes 1000+ items in seconds"
}
```

**Pattern 3: AI + API Execution**
```json
{
  "name": "module_ai_smart_generate",
  "description": "🤖 SMART TOOL: AI generates content then executes API",
  "category": "smart_bundled",
  "efficiency": "99% faster (2 hours → 10 seconds)"
}
```

**Pattern 4: Dashboard Export**
```json
{
  "name": "module_export_dashboard_data",
  "description": "Export current dashboard view for AI consumption",
  "parameters": {
    "subtab": {
      "enum": ["tab1", "tab2", "all"]
    }
  }
}
```

---

## 📦 Required Outputs

Please generate the following files:

### 1. Module Manifest (`manifest.json`)

```json
{
  "id": "module-id",
  "name": "Display Name",
  "version": "1.0.0",
  "description": "Brief description of functionality",
  "icon": "fas fa-icon-name",
  "colors": {
    "primary": "#b4a7d6",
    "secondary": "#d4c4f9",
    "hover": "#9f8fc9"
  },
  "scriptPath": "external/modules/module-id/module-id.js",
  "tabs": [
    {
      "id": "tab-id",
      "name": "Tab Display Name",
      "icon": "fas fa-icon",
      "default": true
    }
  ]
}
```

### 2. Tool Manifest (`tools/manifest.json`)

```json
{
  "module": "module-id",
  "version": "1.0.0",
  "schemas": [
    "category1.json",
    "category2.json",
    "smart-tools.json"
  ],
  "auto_register": true,
  "dependencies": []
}
```

### 3. Granular Tool Schema (`tools/[category].json`)

```json
{
  "platform": "module-id",
  "description": "Module API - Brief description",
  "tools": [
    {
      "name": "module_get_items",
      "description": "Get/list items with filtering and pagination",
      "platform": "module-id",
      "category": "data_retrieval",
      "parameters": {
        "status": {
          "type": "string",
          "enum": ["active", "inactive"],
          "description": "Filter by status",
          "required": false
        },
        "search": {
          "type": "string",
          "description": "Search by name or ID",
          "required": false
        },
        "limit": {
          "type": "integer",
          "default": 20,
          "description": "Number of items to return",
          "required": false
        }
      },
      "returns": {
        "type": "object",
        "properties": {
          "items": {"type": "array"},
          "total": {"type": "integer"},
          "pages": {"type": "integer"}
        }
      }
    },
    {
      "name": "module_create_item",
      "description": "Create a new item",
      "platform": "module-id",
      "parameters": {
        "name": {"type": "string", "required": true},
        "description": {"type": "string", "required": false}
      }
    },
    {
      "name": "module_update_item",
      "description": "Update an existing item",
      "platform": "module-id",
      "parameters": {
        "item_id": {"type": "string", "required": true},
        "name": {"type": "string", "required": false}
      }
    },
    {
      "name": "module_delete_item",
      "description": "Delete an item",
      "platform": "module-id",
      "parameters": {
        "item_id": {"type": "string", "required": true}
      }
    }
  ]
}
```

### 4. Smart Tools Schema (`tools/smart-tools.json`)

```json
{
  "platform": "module-id",
  "smart_tools": [
    {
      "name": "module_smart_bulk_update",
      "description": "🤖 SMART TOOL: Update multiple items in ONE call",
      "platform": "module-id",
      "category": "smart_bundled",
      "parameters": {
        "updates": {
          "type": "array",
          "description": "Array of {item_id, field, value}",
          "required": true
        }
      },
      "returns": {
        "total_updated": "integer",
        "successful": "array",
        "failed": "array"
      },
      "efficiency": "90% reduction (10 updates → 1 call)"
    },
    {
      "name": "module_smart_analysis_report",
      "description": "🤖 SMART TOOL: Generate comprehensive analysis with recommendations",
      "platform": "module-id",
      "category": "SMART Tools",
      "parameters": {
        "analysis_type": {
          "type": "string",
          "enum": ["inventory", "sales", "performance"],
          "required": true
        }
      },
      "returns": {
        "summary": "object",
        "issues": "array",
        "recommendations": "array",
        "metrics": "object"
      },
      "efficiency": "Analyzes 1000+ items in seconds"
    },
    {
      "name": "module_export_dashboard_data",
      "description": "Export current dashboard view as JSON for AI consumption",
      "platform": "module-id",
      "parameters": {
        "subtab": {
          "type": "string",
          "enum": ["tab1", "tab2", "all"],
          "default": "all"
        }
      },
      "returns": {
        "module": "string",
        "timestamp": "string",
        "subtab": "string",
        "data": "object"
      }
    }
  ]
}
```

### 5. Module JavaScript (`[module-id].js`) - WITH TOOL INTEGRATION

```javascript
/**
 * [ModuleName] Module
 * AI-Integrated module with tool support
 * 
 * Features:
 * - Sub-tab navigation
 * - Data visualization
 * - AI-callable tools
 * - Dashboard data export
 */
class [ModuleName]Module extends BaseModule {
    constructor(config) {
        super(config);
        
        // Module data
        this.data = {
            items: [],
            stats: {}
        };
        
        // Tool system
        this.tools = null;
        this.toolImplementations = {};
    }
    
    /**
     * Initialize module
     * Load tools, register with AI, create UI
     */
    async initialize() {
        console.log('🔧 Initializing [ModuleName] module...');
        
        // Load and register tools
        await this.loadTools();
        this.registerToolsWithAI();
        
        // Apply module colors
        this.applyModuleColors();
        
        // Create UI structure
        await super.initialize();
        
        console.log('[ModuleName] module ready');
    }
    
    // ==================== TOOL SYSTEM ====================
    
    /**
     * Load tool schemas from module/tools/ folder
     */
    async loadTools() {
        console.log('🔧 Loading [ModuleName] tools...');
        
        try {
            // Load tool manifest
            const manifestResponse = await fetch('external/modules/[module-id]/tools/manifest.json');
            const manifest = await manifestResponse.json();
            
            this.tools = [];
            
            // Load each tool schema file
            for (const schemaFile of manifest.schemas) {
                const response = await fetch(`external/modules/[module-id]/tools/${schemaFile}`);
                const toolSchema = await response.json();
                
                if (toolSchema.tools) {
                    this.tools.push(...toolSchema.tools);
                }
                
                if (toolSchema.smart_tools) {
                    this.tools.push(...toolSchema.smart_tools);
                }
            }
            
            console.log(`Loaded ${this.tools.length} [ModuleName] tools`);
            
            // Bind tool implementations
            this.bindToolImplementations();
            
        } catch (error) {
            console.error(' Failed to load tools:', error);
        }
    }
    
    /**
     * Bind tool schemas to actual implementation functions
     */
    bindToolImplementations() {
        this.toolImplementations = {
            // Granular tools
            '[module]_get_items': this.getItems.bind(this),
            '[module]_create_item': this.createItem.bind(this),
            '[module]_update_item': this.updateItem.bind(this),
            '[module]_delete_item': this.deleteItem.bind(this),
            
            // Smart tools
            '[module]_smart_bulk_update': this.smartBulkUpdate.bind(this),
            '[module]_smart_analysis_report': this.smartAnalysisReport.bind(this),
            '[module]_export_dashboard_data': this.exportDashboardData.bind(this)
        };
    }
    
    /**
     * Register tools with global AI system
     */
    registerToolsWithAI() {
        if (!window.ModuleToolRegistry) {
            window.ModuleToolRegistry = {};
        }
        
        window.ModuleToolRegistry['[module-id]'] = {
            tools: this.tools,
            execute: this.executeTool.bind(this)
        };
        
        console.log('[ModuleName] tools registered with AI system');
    }
    
    /**
     * Execute a tool by name
     */
    async executeTool(toolName, params) {
        const implementation = this.toolImplementations[toolName];
        
        if (!implementation) {
            throw new Error(`Tool not found: ${toolName}`);
        }
        
        console.log(`🔧 Executing tool: ${toolName}`, params);
        
        try {
            const result = await implementation(params);
            console.log(`Tool executed successfully: ${toolName}`);
            return result;
        } catch (error) {
            console.error(` Tool execution failed: ${toolName}`, error);
            throw error;
        }
    }
    
    // ==================== TOOL IMPLEMENTATIONS ====================
    
    /**
     * Granular Tool: Get Items
     */
    async getItems(params = {}) {
        const { status, search = '', limit = 20, offset = 0 } = params;
        
        // Call backend API
        const response = await fetch(`/api/[module]/items?status=${status}&search=${search}&limit=${limit}&offset=${offset}`);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch items: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        return {
            items: data.items,
            total: data.total,
            pages: Math.ceil(data.total / limit),
            current_page: Math.floor(offset / limit) + 1
        };
    }
    
    /**
     * Granular Tool: Create Item
     */
    async createItem(params) {
        const { name, description } = params;
        
        const response = await fetch('/api/[module]/items', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to create item: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * Granular Tool: Update Item
     */
    async updateItem(params) {
        const { item_id, name, description } = params;
        
        const response = await fetch(`/api/[module]/items/${item_id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to update item: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * Granular Tool: Delete Item
     */
    async deleteItem(params) {
        const { item_id } = params;
        
        const response = await fetch(`/api/[module]/items/${item_id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error(`Failed to delete item: ${response.statusText}`);
        }
        
        return { success: true, item_id };
    }
    
    /**
     * Smart Tool: Bulk Update
     * Updates multiple items in ONE call
     */
    async smartBulkUpdate(params) {
        const { updates } = params;
        
        const results = {
            total_updated: updates.length,
            successful: [],
            failed: []
        };
        
        // Process each update
        for (const update of updates) {
            try {
                const result = await this.updateItem(update);
                results.successful.push(result);
            } catch (error) {
                results.failed.push({
                    item_id: update.item_id,
                    error: error.message
                });
            }
        }
        
        return results;
    }
    
    /**
     * Smart Tool: Analysis Report
     * Generates comprehensive analysis with recommendations
     */
    async smartAnalysisReport(params) {
        const { analysis_type } = params;
        
        // Fetch all data
        const itemsResult = await this.getItems({ limit: 1000 });
        
        const report = {
            analysis_type,
            timestamp: new Date().toISOString(),
            summary: {},
            issues: [],
            recommendations: [],
            metrics: {}
        };
        
        // Analyze based on type
        switch (analysis_type) {
            case 'inventory':
                // Check for low stock
                const lowStock = itemsResult.items.filter(item => item.stock < 10);
                if (lowStock.length > 0) {
                    report.issues.push(`${lowStock.length} items with low stock`);
                    report.recommendations.push('Reorder low stock items');
                }
                report.metrics = {
                    total_items: itemsResult.total,
                    low_stock_count: lowStock.length
                };
                break;
                
            case 'sales':
                // Sales analysis logic
                break;
                
            case 'performance':
                // Performance analysis logic
                break;
        }
        
        return report;
    }
    
    /**
     * Tool: Export Dashboard Data
     * Packages current dashboard view into JSON for AI consumption
     */
    async exportDashboardData(params = {}) {
        const { subtab = 'all' } = params;
        
        const dashboardData = {
            module: '[module-id]',
            timestamp: new Date().toISOString(),
            subtab: subtab,
            data: {}
        };
        
        // Export based on active sub-tab
        switch (subtab) {
            case 'tab1':
            case 'all':
                dashboardData.data.tab1 = await this.getItems({ limit: 100 });
                if (subtab !== 'all') break;
                
            case 'tab2':
            case 'all':
                // Export tab2 data
                break;
        }
        
        return dashboardData;
    }
    
    // ==================== UI INITIALIZATION ====================
    
    /**
     * Apply module-specific colors as CSS variables
     */
    applyModuleColors() {
        const colors = this.config.colors;
        const tabContainer = document.getElementById(`tab-${this.config.id}`);
        
        if (tabContainer && colors) {
            tabContainer.style.setProperty('--module-primary', colors.primary);
            tabContainer.style.setProperty('--module-secondary', colors.secondary);
            tabContainer.style.setProperty('--module-hover', colors.hover);
            tabContainer.style.setProperty('--module-primary-light', this.lightenColor(colors.primary, 0.1));
        }
    }
    
    /**
     * Lighten color for backgrounds
     */
    lightenColor(color, opacity) {
        const hex = color.replace('#', '');
        const r = parseInt(hex.substr(0, 2), 16);
        const g = parseInt(hex.substr(2, 2), 16);
        const b = parseInt(hex.substr(4, 2), 16);
        return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }
    
    /**
     * Initialize sub-tabs (called by BaseModule)
     */
    initializeSubTabs() {
        // Get sub-tabs from config
        const subTabs = this.config.tabs || [];
        
        // Initialize each sub-tab
        for (const tab of subTabs) {
            const methodName = `initialize${this.capitalize(tab.id)}`;
            if (typeof this[methodName] === 'function') {
                this[methodName]();
            }
        }
    }
    
    /**
     * Initialize first sub-tab
     */
    initializeTab1() {
        const container = document.getElementById('subtab-tab1');
        const primaryColor = this.config.colors.primary;
        
        container.innerHTML = `
            <div class="module-header" style="border-bottom-color: ${primaryColor};">
                <div class="module-header-left">
                    <h2 class="module-title">
                        <i class="fas fa-icon" style="color: ${primaryColor};"></i>
                        Tab 1 Title
                    </h2>
                    <p class="module-description">Tab 1 description</p>
                </div>
                <div class="module-header-right">
                    <button class="btn-primary" style="background: ${primaryColor}; border-color: ${primaryColor};" 
                            onclick="window.ModuleRegistry['[module-id]'].handleNewItem()">
                        <i class="fas fa-plus"></i> New Item
                    </button>
                    <button class="btn-secondary" onclick="window.ModuleRegistry['[module-id]'].loadData()">
                        <i class="fas fa-sync"></i> Refresh
                    </button>
                </div>
            </div>
            
            <!-- Stats Cards -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px;">
                ${this.createStatCard('Total Items', '0', 'fas fa-box', primaryColor)}
                ${this.createStatCard('Active', '0', 'fas fa-check-circle', primaryColor)}
                ${this.createStatCard('Pending', '0', 'fas fa-clock', primaryColor)}
                ${this.createStatCard('Completed', '0', 'fas fa-check', primaryColor)}
            </div>
            
            <!-- Data Table -->
            <div class="dashboard-card">
                <div class="dashboard-card-header">
                    <i class="fas fa-list dashboard-card-icon" style="color: ${primaryColor};"></i>
                    <span class="dashboard-card-title">Recent Items</span>
                </div>
                <div id="items-table-container"></div>
            </div>
        `;
        
        // Load data
        this.loadData();
    }
    
    /**
     * Create stat card HTML
     */
    createStatCard(label, value, icon, color) {
        return `
            <div class="stat-card" style="border-left-color: ${color};">
                <div class="stat-icon" style="background: ${this.lightenColor(color, 0.1)}; color: ${color};">
                    <i class="${icon}"></i>
                </div>
                <div class="stat-content">
                    <div class="stat-label">${label}</div>
                    <div class="stat-value">${value}</div>
                </div>
            </div>
        `;
    }
    
    /**
     * Load data from API
     */
    async loadData() {
        try {
            const result = await this.executeTool('[module]_get_items', { limit: 50 });
            this.data.items = result.items;
            this.renderTable(result.items);
        } catch (error) {
            console.error('Failed to load data:', error);
            this.showError('Failed to load data');
        }
    }
    
    /**
     * Render data table
     */
    renderTable(items) {
        const container = document.getElementById('items-table-container');
        
        if (!items || items.length === 0) {
            container.innerHTML = '<p class="text-secondary">No items found</p>';
            return;
        }
        
        const tableHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Status</th>
                        <th>Date</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${items.map(item => `
                        <tr>
                            <td>${item.name}</td>
                            <td><span class="status-badge status-${item.status}">${item.status}</span></td>
                            <td>${new Date(item.date).toLocaleDateString()}</td>
                            <td>
                                <button class="btn-sm btn-primary" onclick="window.ModuleRegistry['[module-id]'].viewItem('${item.id}')">
                                    <i class="fas fa-eye"></i> View
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        container.innerHTML = tableHTML;
    }
    
    /**
     * Handle new item button
     */
    handleNewItem() {
        // Show create dialog
        console.log('Create new item');
    }
    
    /**
     * View item details
     */
    viewItem(itemId) {
        console.log('View item:', itemId);
    }
    
    /**
     * Capitalize first letter
     */
    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}

// Register module
window.ModuleRegistry['[module-id]'] = [ModuleName]Module;
```

**Key Features:**
- Tool loading and registration
- Granular tool implementations (CRUD)
- Smart tool implementations (bulk operations, analysis)
- Dashboard data export
- Module-specific color application
- Data visualization (stats, tables)
- User interactions (buttons, forms)
        this.apiEndpoint = null;
    }

    async initialize() {
        await super.initialize();
        // Custom initialization
        console.log(`${this.moduleId} initialized`);
        
        // Load initial data
        await this.loadInitialData();
    }

    async loadInitialData() {
        // Load data for default tab
        if (this.activeSubTab === 'default-tab-id') {
            await this.loadDefaultTabData();
        }
    }

    initializeSubTabs() {
        // Initialize each sub-tab
        this.initializeTab1();
        this.initializeTab2();
        // ... more tabs
    }

    /**
     * TAB 1: [Tab Name]
     */
    initializeTab1() {
        const tab1 = this.getSubTabContainer('tab1');
        tab1.innerHTML = `
            <div class="module-dashboard">
                <!-- Stats cards -->
                <div class="stats-grid">
                    ${this.renderStatCards()}
                </div>
                
                <!-- Main content -->
                <div class="dashboard-card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <i class="fas fa-icon"></i> Section Title
                        </h3>
                        <div class="card-actions">
                            <button class="btn btn-primary" onclick="[action]">
                                <i class="fas fa-plus"></i> New Item
                            </button>
                        </div>
                    </div>
                    <div class="card-content">
                        <div id="tab1-content"></div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadTab1Data() {
        const container = document.getElementById('tab1-content');
        this.showLoading(container, 'Loading data...');

        try {
            const response = await fetch('/api/endpoint');
            this.data = await response.json();
            this.renderTab1Content();
        } catch (error) {
            this.showError(container, 'Failed to load data');
        }
    }

    renderTab1Content() {
        // Render data (table, chart, etc.)
    }

    /**
     * Called when module tab is activated
     */
    onActivate() {
        console.log(`${this.moduleId} activated`);
        // Refresh data if needed
    }

    /**
     * Called when sub-tab is switched
     */
    onSubTabActivate(subTabId) {
        console.log(`Sub-tab ${subTabId} activated`);
        
        // Load data for active sub-tab
        switch(subTabId) {
            case 'tab1':
                this.loadTab1Data();
                break;
            case 'tab2':
                this.loadTab2Data();
                break;
        }
    }

    /**
     * Refresh button handler
     */
    onRefresh() {
        console.log('Refreshing data...');
        // Reload current tab data
        this.onSubTabActivate(this.activeSubTab);
    }

    /**
     * Cleanup
     */
    destroy() {
        console.log(`${this.moduleId} destroyed`);
        // Clear data, intervals, etc.
        this.data = [];
    }
}

// Register module
window.ModuleRegistry['module-id'] = [ModuleName]Module;
```

**Guidelines:**
- Extract all data loading into separate methods
- Use `this.showLoading()`, `this.showError()`, `this.showEmpty()` utilities
- Convert tables to use `.data-table` class
- Convert stat cards to use `.stat-card` structure
- Use `this.createCard()` and `this.createStatCard()` helpers when possible

### 3. Main Manifest Entry

```json
{
  "id": "module-id",
  "name": "Display Name",
  "icon": "fas fa-icon",
  "color": "#HEX-COLOR",
  "description": "Brief description",
  "manifestPath": "external/modules/module-id/manifest.json",
  "scriptPath": "external/modules/module-id/module-id.js",
  "enabled": true
}
```

This goes in `UI/external/modules/manifest.json` in the `"modules"` array.

### 4. Optional: Custom CSS (`module-id.css`)

Only if module-specific styling is needed:

```css
/* Module-specific overrides */
#tab-module-id .custom-class {
    /* Custom styles */
}

/* Use CSS variables for consistency */
#tab-module-id .module-card {
    background: var(--bg-secondary);
    border-left: 4px solid var(--accent-primary);
}
```

**Guidelines:**
- Prefix all selectors with `#tab-module-id` to avoid conflicts
- Use CSS variables: `var(--bg-primary)`, `var(--text-primary)`, etc.
- Only include truly custom styles (most styling is inherited)

---

## Available UI Components

Use these BaseModule utilities and classes:

### Stat Cards
```javascript
// Method 1: HTML structure
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-icon primary">
            <i class="fas fa-icon"></i>
        </div>
        <div class="stat-content">
            <div class="stat-label">Label</div>
            <div class="stat-value">100</div>
            <div class="stat-change">Description</div>
        </div>
    </div>
</div>

// Method 2: Helper method
const card = this.createStatCard('Label', '100', 'fas fa-icon', 'primary', 'Description');
```

### Dashboard Cards
```javascript
// Method 1: HTML structure
<div class="dashboard-card">
    <div class="card-header">
        <h3 class="card-title">
            <i class="fas fa-icon"></i> Title
        </h3>
        <div class="card-actions">
            <button class="btn btn-primary">Action</button>
        </div>
    </div>
    <div class="card-content">
        Content here
    </div>
</div>

// Method 2: Helper method
const card = this.createCard('Title', 'fas fa-icon', 'Content', '<button>Action</button>');
```

### Data Tables
```html
<table class="data-table">
    <thead>
        <tr>
            <th>Column 1</th>
            <th>Column 2</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Data 1</td>
            <td>Data 2</td>
            <td>
                <button class="btn btn-sm">
                    <i class="fas fa-eye"></i> View
                </button>
            </td>
        </tr>
    </tbody>
</table>
```

### Status Badges
```html
<span class="status-badge status-new">New</span>
<span class="status-badge status-qualified">Qualified</span>
<span class="status-badge status-working">Working</span>
<span class="status-badge status-unqualified">Unqualified</span>
```

### Loading/Error/Empty States
```javascript
// Show loading
this.showLoading(container, 'Loading data...');

// Show error
this.showError(container, 'Error message');

// Show empty state
this.showEmpty(container, 'No data available', 'fas fa-inbox');
```

---

## 🔧 Conversion Patterns

### Pattern 1: Convert Static HTML to Dynamic

**Before:**
```html
<div id="mySection">
    <h2>My Section</h2>
    <div class="content">Static content</div>
</div>
```

**After:**
```javascript
initializeTab() {
    const tab = this.getSubTabContainer('tab-id');
    tab.innerHTML = `
        <div class="module-dashboard">
            <div class="dashboard-card">
                <div class="card-header">
                    <h3 class="card-title">
                        <i class="fas fa-icon"></i> My Section
                    </h3>
                </div>
                <div class="card-content">
                    Dynamic content
                </div>
            </div>
        </div>
    `;
}
```

### Pattern 2: Convert Data Fetching

**Before:**
```javascript
fetch('/api/data')
    .then(response => response.json())
    .then(data => {
        document.getElementById('table').innerHTML = 
            data.map(item => `<tr><td>${item.name}</td></tr>`).join('');
    });
```

**After:**
```javascript
async loadData() {
    const container = document.getElementById('table-container');
    this.showLoading(container, 'Loading...');
    
    try {
        const response = await fetch('/api/data');
        this.data = await response.json();
        this.renderTable();
    } catch (error) {
        console.error('Failed to load data:', error);
        this.showError(container, 'Failed to load data');
    }
}

renderTable() {
    const tbody = document.getElementById('table-body');
    tbody.innerHTML = this.data
        .map(item => `<tr><td>${item.name}</td></tr>`)
        .join('');
}
```

### Pattern 3: Convert Event Handlers

**Before:**
```javascript
document.getElementById('myButton').addEventListener('click', () => {
    alert('Clicked!');
});
```

**After:**
```javascript
initializeTab() {
    const tab = this.getSubTabContainer('tab-id');
    tab.innerHTML = `
        <button class="btn btn-primary" id="${this.moduleId}-action-btn">
            <i class="fas fa-plus"></i> Action
        </button>
    `;
    
    // Add event listener
    document.getElementById(`${this.moduleId}-action-btn`)
        .addEventListener('click', () => this.handleAction());
}

handleAction() {
    console.log('Action clicked');
    // Your logic here
}
```

---

## 📋 Conversion Checklist

Please ensure the converted module includes:

- [ ] Proper module ID (lowercase-hyphen format)
- [ ] Class extends BaseModule
- [ ] Module registered: `window.ModuleRegistry['module-id'] = ModuleClass;`
- [ ] All sub-tabs identified and implemented
- [ ] Data loading methods extracted
- [ ] UI uses consistent classes (`.data-table`, `.stat-card`, etc.)
- [ ] Loading/error states handled
- [ ] Event handlers properly bound
- [ ] `onActivate()` and `onSubTabActivate()` implemented
- [ ] `onRefresh()` reloads current data
- [ ] `destroy()` cleans up resources
- [ ] Comments explain complex logic
- [ ] Console.log statements for debugging

---

## Example: Full Conversion

### INPUT: Existing Code

```html
<!-- existing-dashboard.html -->
<div id="myDashboard">
    <h1>Sales Dashboard</h1>
    
    <div class="stats">
        <div class="stat">
            <span class="label">Total Sales</span>
            <span class="value" id="totalSales">$0</span>
        </div>
        <div class="stat">
            <span class="label">Orders</span>
            <span class="value" id="orderCount">0</span>
        </div>
    </div>
    
    <table id="ordersTable">
        <thead>
            <tr><th>Order ID</th><th>Customer</th><th>Amount</th></tr>
        </thead>
        <tbody id="ordersBody"></tbody>
    </table>
    
    <button id="refreshBtn">Refresh</button>
</div>

<script>
async function loadOrders() {
    const response = await fetch('/api/orders');
    const orders = await response.json();
    
    // Update stats
    document.getElementById('totalSales').textContent = 
        '$' + orders.reduce((sum, o) => sum + o.amount, 0);
    document.getElementById('orderCount').textContent = orders.length;
    
    // Update table
    document.getElementById('ordersBody').innerHTML = orders
        .map(o => `<tr><td>${o.id}</td><td>${o.customer}</td><td>$${o.amount}</td></tr>`)
        .join('');
}

document.getElementById('refreshBtn').addEventListener('click', loadOrders);
loadOrders();
</script>
```

### OUTPUT: Module Format

**1. manifest.json**
```json
{
  "id": "sales-dashboard",
  "name": "Sales Dashboard",
  "version": "1.0.0",
  "description": "Sales orders and revenue tracking",
  "icon": "fas fa-chart-line",
  "color": "#10B981",
  "scriptPath": "external/modules/sales-dashboard/sales-dashboard.js",
  "tabs": [
    {
      "id": "orders",
      "name": "Orders",
      "icon": "fas fa-shopping-cart",
      "default": true
    }
  ]
}
```

**2. sales-dashboard.js**
```javascript
/**
 * Sales Dashboard Module
 * Tracks sales orders and revenue
 */
class SalesDashboardModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);
        this.orders = [];
        this.totalSales = 0;
    }

    async initialize() {
        await super.initialize();
        console.log('Sales Dashboard initialized');
        await this.loadOrders();
    }

    initializeSubTabs() {
        this.initializeOrdersTab();
    }

    /**
     * ORDERS TAB
     */
    initializeOrdersTab() {
        const ordersTab = this.getSubTabContainer('orders');
        ordersTab.innerHTML = `
            <div class="module-dashboard">
                <!-- Stats Cards -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon success">
                            <i class="fas fa-dollar-sign"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Total Sales</div>
                            <div class="stat-value" id="total-sales">$0</div>
                            <div class="stat-change">All time</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon primary">
                            <i class="fas fa-shopping-cart"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Orders</div>
                            <div class="stat-value" id="order-count">0</div>
                            <div class="stat-change">Total orders</div>
                        </div>
                    </div>
                </div>

                <!-- Orders Table -->
                <div class="dashboard-card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <i class="fas fa-list"></i> Recent Orders
                        </h3>
                        <div class="card-actions">
                            <button class="btn btn-primary" onclick="alert('Create order feature')">
                                <i class="fas fa-plus"></i> New Order
                            </button>
                        </div>
                    </div>
                    <div class="card-content">
                        <div id="orders-table-container"></div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadOrders() {
        const container = document.getElementById('orders-table-container');
        if (!container) return;
        
        this.showLoading(container, 'Loading orders...');

        try {
            const response = await fetch('/api/orders');
            this.orders = await response.json();
            
            this.renderOrdersTable();
            this.updateStats();
            
            console.log(`Loaded ${this.orders.length} orders`);
        } catch (error) {
            console.error('Failed to load orders:', error);
            this.showError(container, 'Failed to load orders');
        }
    }

    renderOrdersTable() {
        const container = document.getElementById('orders-table-container');
        
        const table = document.createElement('table');
        table.className = 'data-table';
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Order ID</th>
                    <th>Customer</th>
                    <th>Amount</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${this.orders.map(order => `
                    <tr>
                        <td><strong>#${order.id}</strong></td>
                        <td>${order.customer}</td>
                        <td><strong>$${order.amount.toFixed(2)}</strong></td>
                        <td>
                            <button class="btn btn-sm" onclick="alert('View order ${order.id}')">
                                <i class="fas fa-eye"></i> View
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        `;
        
        container.innerHTML = '';
        container.appendChild(table);
    }

    updateStats() {
        // Calculate total sales
        this.totalSales = this.orders.reduce((sum, order) => sum + order.amount, 0);
        
        // Update UI
        document.getElementById('total-sales').textContent = 
            '$' + this.totalSales.toFixed(2);
        document.getElementById('order-count').textContent = this.orders.length;
    }

    onActivate() {
        console.log('Sales Dashboard activated');
        this.loadOrders(); // Refresh data
    }

    onSubTabActivate(subTabId) {
        console.log(`Sales Dashboard sub-tab ${subTabId} activated`);
        if (subTabId === 'orders') {
            this.loadOrders();
        }
    }

    onRefresh() {
        console.log('Refreshing sales data...');
        this.loadOrders();
    }

    destroy() {
        console.log('Sales Dashboard destroyed');
        this.orders = [];
        this.totalSales = 0;
    }
}

// Register module
window.ModuleRegistry['sales-dashboard'] = SalesDashboardModule;
```

**3. Main manifest entry**
```json
{
  "id": "sales-dashboard",
  "name": "Sales Dashboard",
  "icon": "fas fa-chart-line",
  "color": "#10B981",
  "description": "Sales orders and revenue tracking",
  "manifestPath": "external/modules/sales-dashboard/manifest.json",
  "scriptPath": "external/modules/sales-dashboard/sales-dashboard.js",
  "enabled": true
}
```

---

## Conversion Workflow

### Step 1: Analyze Existing Code

**Identify Module Boundaries:**
1. Find main sections/features in HTML
2. Identify logical groupings (e.g., "Products", "Orders", "Analytics")
3. Determine sub-tabs needed

**Example Analysis:**
```html
<!-- BEFORE: Monolithic HTML -->
<div id="woocommerce-section">
    <div class="products-tab">...</div>  <!-- Sub-tab 1 -->
    <div class="orders-tab">...</div>    <!-- Sub-tab 2 -->
    <div class="customers-tab">...</div> <!-- Sub-tab 3 -->
</div>
```

**Analysis Result:**
- **Module ID**: `woocommerce`
- **Module Name**: WooCommerce Manager
- **Sub-tabs**: Products, Orders, Customers
- **Primary Color**: `#b4a7d6` (pastel purple)
- **API Operations Needed**: 18 granular + 4 smart tools

---

### Step 2: Identify Tool Requirements

**For Each Sub-Tab:**
1. List all data operations (Get, Create, Update, Delete)
2. Identify batch operations that could be "smart tools"
3. Determine analytics/reporting needs

**Example Tool Mapping:**

**Products Tab:**
- **Granular**: get_products, create_product, update_product, delete_product, get_categories
- **Smart**: smart_bulk_update_prices, smart_inventory_report

**Orders Tab:**
- **Granular**: get_orders, update_order_status, get_order_details
- **Smart**: smart_process_multiple_orders, smart_sales_report

**Customers Tab:**
- **Granular**: get_customers, create_customer, update_customer
- **Smart**: smart_customer_segmentation_report

**Dashboard Export:**
- `export_dashboard_data` (always include for AI integration)

---

### Step 3: Extract HTML Structure

**Extract Main Container:**
```html
<!-- OLD LOCATION: In main HTML file -->
<div id="woocommerce-section" class="platform-section">
    <!-- Entire section content -->
</div>
```

**NEW LOCATION: Move to module class**
```javascript
// In woocommerce.js
initializeProducts() {
    const container = this.getSubTabContainer('products');
    container.innerHTML = `
        <!-- Same HTML structure, now in module -->
    `;
}
```

---

### Step 4: Extract JavaScript Logic

**Identify Functions to Move:**
```javascript
// OLD: Global functions
function loadWooCommerceProducts() { ... }
function createWooCommerceProduct() { ... }
```

**NEW: Module methods**
```javascript
class WooCommerceModule extends BaseModule {
    async loadProducts() { ... }
    async createProduct() { ... }
}
```

**Convert API Calls to Tool Implementations:**
```javascript
// OLD: Direct API call
async function loadProducts() {
    const response = await fetch('/api/woocommerce/products');
    return await response.json();
}

// NEW: Tool implementation
async getProducts(params = {}) {
    const { status, limit = 20, offset = 0 } = params;
    const response = await fetch(`/api/woocommerce/products?status=${status}&limit=${limit}&offset=${offset}`);
    
    if (!response.ok) {
        throw new Error(`Failed to fetch products: ${response.statusText}`);
    }
    
    return await response.json();
}
```

---

### Step 5: Create Tool Schemas

**For Each Operation, Create Tool Schema:**

**Granular Tool Example (products.json):**
```json
{
    "name": "woocommerce_get_products",
    "description": "Retrieve WooCommerce products with filtering",
    "parameters": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["all", "published", "draft", "pending"],
                "description": "Filter by product status"
            },
            "limit": {
                "type": "integer",
                "default": 20,
                "description": "Number of products to return"
            },
            "offset": {
                "type": "integer",
                "default": 0,
                "description": "Pagination offset"
            }
        }
    },
    "returns": {
        "type": "object",
        "properties": {
            "products": {
                "type": "array",
                "description": "Array of product objects"
            },
            "total": {
                "type": "integer",
                "description": "Total products matching filter"
            }
        }
    }
}
```

**Smart Tool Example (smart-tools.json):**
```json
{
    "name": "woocommerce_smart_bulk_update_prices",
    "description": "🤖 Smart bulk price update - Updates prices for multiple products with percentage increase/decrease",
    "category": "smart_bundled",
    "efficiency": "90% reduction (10 update calls → 1 smart call)",
    "use_cases": [
        "Apply 10% discount to entire category",
        "Increase prices by 5% for inflation",
        "Set sale prices for multiple products"
    ],
    "parameters": {
        "type": "object",
        "properties": {
            "product_ids": {
                "type": "array",
                "items": { "type": "integer" },
                "description": "Array of product IDs to update"
            },
            "price_adjustment": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["percentage", "fixed"],
                        "description": "Adjustment type"
                    },
                    "value": {
                        "type": "number",
                        "description": "Amount to adjust (positive or negative)"
                    }
                }
            }
        },
        "required": ["product_ids", "price_adjustment"]
    }
}
```

---

### Step 6: Wire Tool Implementations

**In Module Class:**
```javascript
bindToolImplementations() {
    this.toolImplementations = {
        // Map tool names to methods
        'woocommerce_get_products': this.getProducts.bind(this),
        'woocommerce_create_product': this.createProduct.bind(this),
        'woocommerce_update_product': this.updateProduct.bind(this),
        'woocommerce_delete_product': this.deleteProduct.bind(this),
        
        // Smart tools
        'woocommerce_smart_bulk_update_prices': this.smartBulkUpdatePrices.bind(this),
        'woocommerce_smart_inventory_report': this.smartInventoryReport.bind(this),
        
        // Dashboard export
        'woocommerce_export_dashboard_data': this.exportDashboardData.bind(this)
    };
}
```

---

### Step 7: Apply Module Colors

**Choose Pastel Color for Module:**
```javascript
// In manifest.json
"colors": {
    "primary": "#b4a7d6",     // Pastel purple for WooCommerce
    "secondary": "#d4c4f9",   // Lighter gradient
    "hover": "#9f8fc9"        // Darker for hover
}
```

**Apply to UI Elements:**
```javascript
initializeProducts() {
    const container = this.getSubTabContainer('products');
    const primaryColor = this.config.colors.primary;
    
    container.innerHTML = `
        <div class="module-header" style="border-bottom-color: ${primaryColor};">
            <h2 class="module-title">
                <i class="fab fa-wordpress" style="color: ${primaryColor};"></i>
                Products
            </h2>
            <button class="btn-primary" style="background: ${primaryColor}; border-color: ${primaryColor};">
                <i class="fas fa-plus"></i> New Product
            </button>
        </div>
    `;
}
```

---

### Step 8: Test Integration

**Testing Checklist:**

**Module Loading:**
- [ ] Module appears in sidebar
- [ ] Module icon and name correct
- [ ] Module color applied to UI elements
- [ ] Sub-tabs appear and switch correctly

**Tool System:**
- [ ] Tools loaded from `tools/` folder
- [ ] Tools registered in `window.ModuleToolRegistry`
- [ ] Tool count matches expected (e.g., 18 granular + 4 smart = 22)
- [ ] `executeTool()` routes to correct method

**Data Flow:**
- [ ] API calls work from tool implementations
- [ ] Data renders in UI correctly
- [ ] Loading states appear during fetch
- [ ] Error handling shows user-friendly messages

**AI Integration:**
- [ ] User can ask: "Show me WooCommerce products"
- [ ] AI calls `woocommerce_get_products` tool
- [ ] Tool executes and returns data
- [ ] AI presents data to user

**Smart Tools:**
- [ ] Smart tool executes multiple operations
- [ ] Results include success/failure breakdown
- [ ] Efficiency improvement visible (e.g., 10 calls → 1 call)

---

## Validation Checklist

### Module Structure
- [ ] Module ID is lowercase-hyphen format (e.g., `woocommerce`)
- [ ] Class name is PascalCase + "Module" (e.g., `WooCommerceModule`)
- [ ] Module registered in `window.ModuleRegistry['module-id']`
- [ ] Manifest includes all required fields (id, name, icon, colors, tabs)
- [ ] Tool manifest lists all tool schema files
- [ ] Folder structure matches: `modules/[id]/{manifest.json, [id].js, tools/}`

### Color System
- [ ] Primary color is pastel shade
- [ ] Secondary color is lighter gradient of primary
- [ ] Hover color is darker shade of primary
- [ ] Colors applied to: borders, icons, buttons, active states
- [ ] Color variables set in `applyModuleColors()`

### Tool Integration
- [ ] Tool schemas in `tools/*.json` (products, orders, smart-tools, etc.)
- [ ] Each tool has: name, description, parameters, returns
- [ ] Smart tools have: 🤖 prefix, category, efficiency, use_cases
- [ ] `loadTools()` loads all tool files
- [ ] `bindToolImplementations()` maps tools to methods
- [ ] `registerToolsWithAI()` adds to global registry
- [ ] `executeTool()` routes execution correctly
- [ ] `exportDashboardData()` packages current view

### Tool Implementations
- [ ] All granular CRUD operations implemented (Get, Create, Update, Delete)
- [ ] Smart tools combine multiple operations efficiently
- [ ] Error handling with try/catch blocks
- [ ] Success/failure results clearly structured
- [ ] Console logging for debugging (🔧 processing, success,  error)

### UI & UX
- [ ] All data fetching uses async/await
- [ ] Loading states shown during data fetching
- [ ] Error messages user-friendly
- [ ] UI uses consistent classes from base CSS
- [ ] Event handlers properly bound (use `.bind(this)` or arrow functions)
- [ ] Font Awesome icons (no emojis except colored circles)
- [ ] Stat cards show key metrics
- [ ] Tables/charts display data clearly

### Code Quality
- [ ] Comments explain complex logic
- [ ] Method names descriptive (verb + noun pattern)
- [ ] No hardcoded values (use config/params)
- [ ] Consistent code style (indentation, naming)
- [ ] No console errors or warnings

### AI Integration Testing
- [ ] Module tools appear in global `ModuleToolRegistry`
- [ ] AI chat includes module tools in available_tools
- [ ] User question triggers correct tool execution
- [ ] Tool returns properly formatted response
- [ ] Dashboard export provides complete context

---

## Complete Conversion Example

### BEFORE: Monolithic Code

```html
<!-- In main HTML file -->
<div id="woocommerce-section" class="platform-section" style="display:none;">
    <h2>WooCommerce Products</h2>
    <button onclick="loadProducts()">Load Products</button>
    <div id="products-container"></div>
</div>

<script>
async function loadProducts() {
    const response = await fetch('/api/woocommerce/products');
    const products = await response.json();
    
    const container = document.getElementById('products-container');
    container.innerHTML = products.map(p => `
        <div>${p.name} - $${p.price}</div>
    `).join('');
}
</script>
```

---

### AFTER: Modular Structure

**File: `modules/woocommerce/manifest.json`**
```json
{
    "id": "woocommerce",
    "name": "WooCommerce",
    "icon": "fab fa-wordpress",
    "version": "1.0.0",
    "description": "WooCommerce product and order management",
    "colors": {
        "primary": "#b4a7d6",
        "secondary": "#d4c4f9",
        "hover": "#9f8fc9"
    },
    "tabs": [
        {
            "id": "products",
            "label": "Products",
            "icon": "fas fa-box",
            "default": true
        }
    ]
}
```

**File: `modules/woocommerce/tools/manifest.json`**
```json
{
    "module_id": "woocommerce",
    "version": "1.0.0",
    "schemas": [
        "products.json",
        "smart-tools.json"
    ]
}
```

**File: `modules/woocommerce/tools/products.json`**
```json
{
    "tools": [
        {
            "name": "woocommerce_get_products",
            "description": "Retrieve WooCommerce products",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": { "type": "integer", "default": 20 }
                }
            },
            "returns": {
                "type": "object",
                "properties": {
                    "products": { "type": "array" },
                    "total": { "type": "integer" }
                }
            }
        }
    ]
}
```

**File: `modules/woocommerce/woocommerce.js`**
```javascript
class WooCommerceModule extends BaseModule {
    constructor(config) {
        super(config);
        this.tools = null;
        this.toolImplementations = {};
    }
    
    async initialize() {
        await this.loadTools();
        this.registerToolsWithAI();
        this.applyModuleColors();
        await super.initialize();
    }
    
    async loadTools() {
        const manifestResponse = await fetch('external/modules/woocommerce/tools/manifest.json');
        const manifest = await manifestResponse.json();
        
        this.tools = [];
        for (const schemaFile of manifest.schemas) {
            const response = await fetch(`external/modules/woocommerce/tools/${schemaFile}`);
            const toolSchema = await response.json();
            if (toolSchema.tools) this.tools.push(...toolSchema.tools);
        }
        
        this.bindToolImplementations();
    }
    
    bindToolImplementations() {
        this.toolImplementations = {
            'woocommerce_get_products': this.getProducts.bind(this)
        };
    }
    
    registerToolsWithAI() {
        if (!window.ModuleToolRegistry) window.ModuleToolRegistry = {};
        window.ModuleToolRegistry['woocommerce'] = {
            tools: this.tools,
            execute: this.executeTool.bind(this)
        };
    }
    
    async executeTool(toolName, params) {
        const implementation = this.toolImplementations[toolName];
        if (!implementation) throw new Error(`Tool not found: ${toolName}`);
        return await implementation(params);
    }
    
    async getProducts(params = {}) {
        const { limit = 20 } = params;
        const response = await fetch(`/api/woocommerce/products?limit=${limit}`);
        if (!response.ok) throw new Error('Failed to fetch products');
        return await response.json();
    }
    
    initializeSubTabs() {
        this.initializeProducts();
    }
    
    initializeProducts() {
        const container = this.getSubTabContainer('products');
        const primaryColor = this.config.colors.primary;
        
        container.innerHTML = `
            <div class="module-header" style="border-bottom-color: ${primaryColor};">
                <h2 class="module-title">
                    <i class="fab fa-wordpress" style="color: ${primaryColor};"></i>
                    WooCommerce Products
                </h2>
                <button class="btn-primary" style="background: ${primaryColor}; border-color: ${primaryColor};" 
                        onclick="window.ModuleRegistry['woocommerce'].loadProducts()">
                    <i class="fas fa-sync"></i> Load Products
                </button>
            </div>
            <div id="products-container"></div>
        `;
    }
    
    async loadProducts() {
        try {
            const result = await this.executeTool('woocommerce_get_products', { limit: 50 });
            const container = document.getElementById('products-container');
            container.innerHTML = result.products.map(p => `
                <div class="product-item">
                    ${p.name} - $${p.price}
                </div>
            `).join('');
        } catch (error) {
            console.error('Failed to load products:', error);
        }
    }
}

window.ModuleRegistry['woocommerce'] = WooCommerceModule;
```

---

## Ready to Convert!

**To use this prompt:**

1. Copy everything from "AI PROMPT STARTS HERE" onwards
2. Paste into your AI assistant
3. Provide your existing code
4. Receive converted module files with full AI integration

**Example prompt:**
```
[Paste this entire AI prompt]

Here is my existing code to convert:

[Paste your HTML/JS/CSS here]

Please convert this into an AI-integrated module following the patterns above.
Include:
- Module manifest with pastel colors
- Tool schemas (granular + smart)
- Complete class with tool implementations
- Dashboard export capability
```

---

**Last Updated:** January 25, 2025  
**Version:** 2.0.0  
**Status:** Complete with AI Integration
