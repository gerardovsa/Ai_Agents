# 🏗️ Module Architecture V2 - AI-Integrated Modules

**Created:** October 30, 2025  
**Status:** Architecture Design  
**Version:** 2.0.0

---

## 🎯 Core Requirements

### 1. **Per-Module Color System**
Each module has its own **pastel primary color** with **gradient secondary**:

```javascript
// Module manifest.json
{
  "id": "woocommerce",
  "name": "WooCommerce",
  "colors": {
    "primary": "#b4a7d6",      // Pastel purple
    "secondary": "#d4c4f9",    // Lighter gradient of primary
    "hover": "#9f8fc9"         // Darker on hover
  }
}
```

**Color Palette Suggestions:**
- **WooCommerce**: `#b4a7d6` (Pastel Purple)
- **Salesforce**: `#7fb3d5` (Pastel Blue)
- **Asana**: `#f4a5ae` (Pastel Pink)
- **HubSpot**: `#ffb347` (Pastel Orange)
- **Shopify**: `#96d8a2` (Pastel Green)
- **Jira**: `#6fb3e0` (Pastel Light Blue)

### 2. **Module Structure with Tools**

```
UI/external/modules/
└── woocommerce/
    ├── manifest.json           # Module config + colors
    ├── woocommerce.js          # UI implementation
    ├── woocommerce.css         # Custom styles (optional)
    │
    └── tools/                  # AI-callable tools
        ├── manifest.json       # Tool registry
        ├── products.json       # Product tools schema
        ├── orders.json         # Order tools schema
        ├── customers.json      # Customer tools schema
        └── analytics.json      # Analytics tools schema
```

### 3. **AI Chat Integration Architecture**

Every module must provide:
1. **Tool schemas** - AI-callable functions
2. **Data export methods** - Package current view into JSON
3. **Smart-tool orchestration** - Multi-step workflows

---

## 📋 Tool Integration Pattern

### Tool Schema Format (AI-Compatible)

**File:** `modules/woocommerce/tools/products.json`

```json
{
  "tools": [
    {
      "name": "woocommerce_get_products",
      "description": "Get WooCommerce products with filtering and pagination",
      "category": "woocommerce",
      "platform": "woocommerce",
      "is_smart_tool": false,
      "parameters": {
        "type": "object",
        "properties": {
          "status": {
            "type": "string",
            "enum": ["publish", "draft", "pending"],
            "description": "Product status filter"
          },
          "search": {
            "type": "string",
            "description": "Search products by name or SKU"
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
        },
        "required": []
      },
      "returns": {
        "type": "object",
        "properties": {
          "products": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "sku": {"type": "string"},
                "price": {"type": "string"},
                "stock_quantity": {"type": "integer"},
                "status": {"type": "string"}
              }
            }
          },
          "total": {"type": "integer"},
          "pages": {"type": "integer"}
        }
      }
    },
    {
      "name": "woocommerce_create_product",
      "description": "Create a new WooCommerce product",
      "category": "woocommerce",
      "platform": "woocommerce",
      "is_smart_tool": false,
      "parameters": {
        "type": "object",
        "properties": {
          "name": {"type": "string", "description": "Product name"},
          "regular_price": {"type": "string", "description": "Regular price"},
          "description": {"type": "string", "description": "Product description"},
          "sku": {"type": "string", "description": "Product SKU"},
          "stock_quantity": {"type": "integer", "description": "Stock quantity"}
        },
        "required": ["name", "regular_price"]
      }
    },
    {
      "name": "woocommerce_update_product",
      "description": "Update an existing WooCommerce product",
      "category": "woocommerce",
      "platform": "woocommerce",
      "is_smart_tool": false,
      "parameters": {
        "type": "object",
        "properties": {
          "product_id": {"type": "integer", "description": "Product ID to update"},
          "name": {"type": "string", "description": "New product name"},
          "regular_price": {"type": "string", "description": "New regular price"},
          "stock_quantity": {"type": "integer", "description": "New stock quantity"}
        },
        "required": ["product_id"]
      }
    },
    {
      "name": "woocommerce_delete_product",
      "description": "Delete a WooCommerce product",
      "category": "woocommerce",
      "platform": "woocommerce",
      "is_smart_tool": false,
      "parameters": {
        "type": "object",
        "properties": {
          "product_id": {"type": "integer", "description": "Product ID to delete"}
        },
        "required": ["product_id"]
      }
    }
  ]
}
```

### Smart-Tool Example (Multi-Tool Orchestration)

**File:** `modules/woocommerce/tools/smart-tools.json`

```json
{
  "smart_tools": [
    {
      "name": "woocommerce_smart_inventory_report",
      "description": "Generate comprehensive inventory report with low stock alerts",
      "category": "woocommerce",
      "is_smart_tool": true,
      "orchestration": [
        {
          "step": 1,
          "tool": "woocommerce_get_products",
          "params": {
            "status": "publish",
            "limit": 1000
          },
          "output_var": "all_products"
        },
        {
          "step": 2,
          "tool": "woocommerce_get_orders",
          "params": {
            "status": "completed",
            "date_after": "30_days_ago"
          },
          "output_var": "recent_orders"
        },
        {
          "step": 3,
          "action": "analyze",
          "description": "Calculate low stock items and reorder recommendations",
          "inputs": ["all_products", "recent_orders"]
        }
      ],
      "parameters": {
        "type": "object",
        "properties": {
          "low_stock_threshold": {
            "type": "integer",
            "default": 10,
            "description": "Stock level considered low"
          }
        }
      }
    }
  ]
}
```

---

## 🔧 Module Implementation with Tools

### Module Class with Tool Integration

```javascript
class WooCommerceModule extends BaseModule {
    constructor(config) {
        super(config);
        this.tools = null;  // Tool definitions
        this.toolImplementations = {}; // Actual functions
    }
    
    async initialize() {
        // Load module tools
        await this.loadTools();
        
        // Register tools with AI system
        this.registerToolsWithAI();
        
        // Continue with standard initialization
        await super.initialize();
    }
    
    /**
     * Load tool schemas from module/tools/ folder
     */
    async loadTools() {
        console.log('🔧 Loading WooCommerce tools...');
        
        try {
            // Load tool manifest
            const manifestResponse = await fetch('external/modules/woocommerce/tools/manifest.json');
            const manifest = await manifestResponse.json();
            
            this.tools = [];
            
            // Load each tool schema file
            for (const schemaFile of manifest.schemas) {
                const response = await fetch(`external/modules/woocommerce/tools/${schemaFile}`);
                const toolSchema = await response.json();
                this.tools.push(...toolSchema.tools);
                
                if (toolSchema.smart_tools) {
                    this.tools.push(...toolSchema.smart_tools);
                }
            }
            
            console.log(` Loaded ${this.tools.length} WooCommerce tools`);
            
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
            'woocommerce_get_products': this.getProducts.bind(this),
            'woocommerce_create_product': this.createProduct.bind(this),
            'woocommerce_update_product': this.updateProduct.bind(this),
            'woocommerce_delete_product': this.deleteProduct.bind(this),
            'woocommerce_get_orders': this.getOrders.bind(this),
            'woocommerce_export_dashboard': this.exportDashboardData.bind(this)
        };
    }
    
    /**
     * Register tools with global AI system
     */
    registerToolsWithAI() {
        if (!window.ModuleToolRegistry) {
            window.ModuleToolRegistry = {};
        }
        
        window.ModuleToolRegistry['woocommerce'] = {
            tools: this.tools,
            execute: this.executeTool.bind(this)
        };
        
        console.log(' WooCommerce tools registered with AI system');
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
            console.log(` Tool executed successfully: ${toolName}`);
            return result;
        } catch (error) {
            console.error(` Tool execution failed: ${toolName}`, error);
            throw error;
        }
    }
    
    /**
     * Tool Implementation: Get Products
     */
    async getProducts(params = {}) {
        const { status = 'publish', search = '', limit = 20, offset = 0 } = params;
        
        // Call backend API
        const response = await fetch(`/api/woocommerce/products?status=${status}&search=${search}&limit=${limit}&offset=${offset}`);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch products: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        return {
            products: data.products,
            total: data.total,
            pages: Math.ceil(data.total / limit),
            current_page: Math.floor(offset / limit) + 1
        };
    }
    
    /**
     * Tool Implementation: Create Product
     */
    async createProduct(params) {
        const { name, regular_price, description, sku, stock_quantity } = params;
        
        const response = await fetch('/api/woocommerce/products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name,
                regular_price,
                description,
                sku,
                stock_quantity
            })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to create product: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * Tool Implementation: Export Dashboard Data
     * Packages current dashboard view into JSON for AI consumption
     */
    async exportDashboardData(params = {}) {
        const { subtab = 'all' } = params;
        
        const dashboardData = {
            module: 'woocommerce',
            timestamp: new Date().toISOString(),
            subtab: subtab,
            data: {}
        };
        
        // Export based on active sub-tab
        switch (subtab) {
            case 'products':
            case 'all':
                dashboardData.data.products = await this.getProducts({ limit: 100 });
                if (subtab !== 'all') break;
                
            case 'orders':
            case 'all':
                dashboardData.data.orders = await this.getOrders({ limit: 100 });
                if (subtab !== 'all') break;
                
            case 'customers':
            case 'all':
                dashboardData.data.customers = await this.getCustomers({ limit: 100 });
                if (subtab !== 'all') break;
                
            case 'analytics':
            case 'all':
                dashboardData.data.analytics = await this.getAnalytics();
                break;
        }
        
        return dashboardData;
    }
    
    /**
     * Initialize Products Sub-Tab
     */
    initializeProducts() {
        const container = document.getElementById('subtab-products');
        
        // Create UI with module's primary color
        const primaryColor = this.config.colors.primary;
        const secondaryColor = this.config.colors.secondary;
        
        container.innerHTML = `
            <div class="module-header" style="border-bottom-color: ${primaryColor};">
                <div class="module-header-left">
                    <h2 class="module-title">
                        <i class="fab fa-wordpress" style="color: ${primaryColor};"></i>
                        WooCommerce Products
                    </h2>
                    <p class="module-description">Manage your WooCommerce product catalog</p>
                </div>
                <div class="module-header-right">
                    <button class="btn-primary" style="background: ${primaryColor}; border-color: ${primaryColor};" onclick="window.ModuleRegistry['woocommerce'].createProductDialog()">
                        <i class="fas fa-plus"></i> New Product
                    </button>
                    <button class="btn-secondary" onclick="window.ModuleRegistry['woocommerce'].loadProducts()">
                        <i class="fas fa-sync"></i> Refresh
                    </button>
                </div>
            </div>
            
            <!-- Products table will be rendered here -->
            <div id="products-table-container"></div>
        `;
        
        // Load products data
        this.loadProducts();
    }
    
    async loadProducts() {
        try {
            const result = await this.executeTool('woocommerce_get_products', { limit: 50 });
            this.renderProductsTable(result);
        } catch (error) {
            console.error('Failed to load products:', error);
            this.showError('Failed to load products');
        }
    }
}

// Register module
window.ModuleRegistry['woocommerce'] = WooCommerceModule;
```

---

## 🗂️ Tool Auto-Discovery System

### Tool Manifest (Per Module)

**File:** `modules/woocommerce/tools/manifest.json`

```json
{
  "module": "woocommerce",
  "version": "1.0.0",
  "schemas": [
    "products.json",
    "orders.json",
    "customers.json",
    "analytics.json",
    "smart-tools.json"
  ],
  "auto_register": true,
  "dependencies": []
}
```

### Global Tool Loader

**File:** `UI/js/module-tool-loader.js`

```javascript
class ModuleToolLoader {
    constructor() {
        this.loadedModuleTools = new Map();
        this.globalToolRegistry = [];
    }
    
    /**
     * Load tools for all enabled modules
     */
    async loadAllModuleTools() {
        console.log('🔧 Loading module tools...');
        
        // Get all enabled modules
        const modulesResponse = await fetch('external/modules/manifest.json');
        const modulesManifest = await modulesResponse.json();
        
        for (const moduleEntry of modulesManifest.modules) {
            if (!moduleEntry.enabled) continue;
            
            await this.loadModuleTools(moduleEntry.id);
        }
        
        console.log(` Loaded tools for ${this.loadedModuleTools.size} modules`);
        this.exportToAISystem();
    }
    
    /**
     * Load tools for a specific module
     */
    async loadModuleTools(moduleId) {
        try {
            // Check if module has tools folder
            const toolManifestUrl = `external/modules/${moduleId}/tools/manifest.json`;
            const response = await fetch(toolManifestUrl);
            
            if (!response.ok) {
                console.log(`ℹ️  Module ${moduleId} has no tools`);
                return;
            }
            
            const toolManifest = await response.json();
            const moduleTools = [];
            
            // Load each schema file
            for (const schemaFile of toolManifest.schemas) {
                const schemaResponse = await fetch(`external/modules/${moduleId}/tools/${schemaFile}`);
                const schema = await schemaResponse.json();
                
                if (schema.tools) {
                    moduleTools.push(...schema.tools);
                }
                
                if (schema.smart_tools) {
                    moduleTools.push(...schema.smart_tools);
                }
            }
            
            this.loadedModuleTools.set(moduleId, {
                tools: moduleTools,
                manifest: toolManifest
            });
            
            console.log(` Loaded ${moduleTools.length} tools for ${moduleId}`);
            
        } catch (error) {
            console.error(` Failed to load tools for ${moduleId}:`, error);
        }
    }
    
    /**
     * Export tools to AI system
     */
    exportToAISystem() {
        // Build global tool list for AI consumption
        this.globalToolRegistry = [];
        
        for (const [moduleId, moduleData] of this.loadedModuleTools) {
            for (const tool of moduleData.tools) {
                this.globalToolRegistry.push({
                    ...tool,
                    module: moduleId,
                    execute: (params) => {
                        return window.ModuleToolRegistry[moduleId].execute(tool.name, params);
                    }
                });
            }
        }
        
        // Make available globally
        window.AI_MODULE_TOOLS = this.globalToolRegistry;
        
        console.log(` Exported ${this.globalToolRegistry.length} tools to AI system`);
    }
    
    /**
     * Get tools for AI chat
     */
    getToolsForAI() {
        return this.globalToolRegistry.map(tool => ({
            name: tool.name,
            description: tool.description,
            parameters: tool.parameters,
            category: tool.category,
            platform: tool.platform,
            is_smart_tool: tool.is_smart_tool || false
        }));
    }
    
    /**
     * Execute tool by name
     */
    async executeToolByName(toolName, params) {
        const tool = this.globalToolRegistry.find(t => t.name === toolName);
        
        if (!tool) {
            throw new Error(`Tool not found: ${toolName}`);
        }
        
        return await tool.execute(params);
    }
}

// Initialize on page load
window.ModuleToolLoader = new ModuleToolLoader();

document.addEventListener('DOMContentLoaded', async () => {
    await window.ModuleToolLoader.loadAllModuleTools();
});
```

---

## 🎨 Module Color System Implementation

### CSS Variable Generation (Per Module)

```javascript
class BaseModule {
    initialize() {
        // Apply module colors as CSS variables
        this.applyModuleColors();
        
        // Continue with initialization
        this.createModuleStructure();
    }
    
    applyModuleColors() {
        const colors = this.config.colors;
        const tabContainer = document.getElementById(`tab-${this.config.id}`);
        
        if (tabContainer && colors) {
            tabContainer.style.setProperty('--module-primary', colors.primary);
            tabContainer.style.setProperty('--module-secondary', colors.secondary);
            tabContainer.style.setProperty('--module-hover', colors.hover);
            tabContainer.style.setProperty('--module-primary-light', this.lightenColor(colors.primary, 0.9));
        }
    }
    
    lightenColor(color, opacity) {
        // Convert hex to rgba with opacity
        const hex = color.replace('#', '');
        const r = parseInt(hex.substr(0, 2), 16);
        const g = parseInt(hex.substr(2, 2), 16);
        const b = parseInt(hex.substr(4, 2), 16);
        return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }
}
```

### CSS Using Module Colors

```css
/* Module-specific primary color */
#tab-woocommerce .module-header {
    border-bottom: 2px solid var(--module-primary);
}

#tab-woocommerce .module-title i {
    color: var(--module-primary);
}

#tab-woocommerce .module-subtab-btn.active {
    color: var(--module-primary);
    border-bottom-color: var(--module-primary);
}

#tab-woocommerce .btn-primary {
    background: var(--module-primary);
    border-color: var(--module-primary);
}

#tab-woocommerce .btn-primary:hover {
    background: var(--module-hover);
    border-color: var(--module-hover);
}

#tab-woocommerce .stat-card {
    border-left-color: var(--module-primary);
}

#tab-woocommerce .stat-icon {
    background: var(--module-primary-light);
    color: var(--module-primary);
}

/* Secondary color for gradients (if desired) */
#tab-woocommerce .gradient-bg {
    background: linear-gradient(135deg, var(--module-primary) 0%, var(--module-secondary) 100%);
}
```

---

## 🔗 AI Chat Integration Flow

### User Asks Question → AI Uses Module Tools

```javascript
// AI Chat Handler
async function handleAIChatMessage(userMessage) {
    // 1. Send message to AI backend
    const response = await fetch('/api/v3/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: userMessage,
            user_id: currentUserId,
            available_tools: window.ModuleToolLoader.getToolsForAI() // Include module tools!
        })
    });
    
    const result = await response.json();
    
    // 2. If AI wants to call a tool
    if (result.tool_calls) {
        for (const toolCall of result.tool_calls) {
            const toolResult = await window.ModuleToolLoader.executeToolByName(
                toolCall.name,
                toolCall.parameters
            );
            
            // Send tool result back to AI
            await sendToolResultToAI(toolCall.id, toolResult);
        }
    }
    
    // 3. Display AI response
    displayAIResponse(result.response);
}
```

### Example Conversation

**User:** "Show me my WooCommerce products that are low in stock"

**AI Backend:**
1. Identifies tools: `woocommerce_get_products`
2. Calls tool with params: `{ status: 'publish', limit: 100 }`
3. Filters results where `stock_quantity < 10`
4. Returns formatted response

**User:** "Create a new product called 'Test Product' priced at $29.99"

**AI Backend:**
1. Identifies tool: `woocommerce_create_product`
2. Calls tool with params: `{ name: 'Test Product', regular_price: '29.99' }`
3. Confirms creation
4. Returns success message

---

## 📁 Complete Module Structure Example

```
UI/external/modules/woocommerce/
├── manifest.json              # Module config + colors
├── woocommerce.js             # UI implementation with tool integration
├── woocommerce.css            # Custom styles (pastel colors)
│
└── tools/                     # AI-callable tools
    ├── manifest.json          # Tool registry
    ├── products.json          # Product CRUD tools
    ├── orders.json            # Order management tools
    ├── customers.json         # Customer tools
    ├── analytics.json         # Analytics/reporting tools
    └── smart-tools.json       # Multi-tool orchestration
```

---

##  Implementation Checklist

### Phase 1: Extract WooCommerce Module
- [ ] Create `modules/woocommerce/` folder structure
- [ ] Extract WooCommerce HTML from main file → `woocommerce.js`
- [ ] Create `manifest.json` with pastel purple colors
- [ ] Test module loads correctly

### Phase 2: Add Tool Support
- [ ] Create `modules/woocommerce/tools/` folder
- [ ] Write tool schemas (products.json, orders.json, etc.)
- [ ] Implement tool functions in module class
- [ ] Test tools execute correctly

### Phase 3: AI Integration
- [ ] Create `module-tool-loader.js` for auto-discovery
- [ ] Register module tools with AI system
- [ ] Update AI chat to include module tools
- [ ] Test AI can call module tools

### Phase 4: Smart-Tools
- [ ] Create `smart-tools.json` schema
- [ ] Implement orchestration logic
- [ ] Test multi-tool workflows

### Phase 5: Repeat for Other Modules
- [ ] Salesforce (pastel blue)
- [ ] Asana (pastel pink)
- [ ] HubSpot (pastel orange)
- [ ] Shopify (pastel green)

---

## 🎯 Next Steps

1. **I need to see the WooCommerce code** in `business-ai-platform-v2.html`
2. **Extract it into module structure**
3. **Create tool schemas**
4. **Implement tool loader**
5. **Test AI integration**

Should I proceed with extracting WooCommerce from the HTML file?

---

**Last Updated:** October 30, 2025  
**Version:** 2.0.0  
**Status:** 🚧 Architecture Design
