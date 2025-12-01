/**
 * Quote Calculator Module
 * 
 * InHouse Print quote generation and pricing tools
 * Provides AI-callable tools for calculating quotes on business cards,
 * flyers, perfect bound books, booklets, and letterheads.
 * 
 * @version 1.0.0
 * @author InHouse Print
 * @extends BaseModule
 */

class QuoteCalculatorModule extends BaseModule {
    constructor(moduleId) {
        // Module ID matches folder name: 'quote-calculator'
        super(moduleId, 'quote-calculator');

        // Module configuration
        this.apiBaseUrl = '/api/quote-calculator';
        this.tools = null;
        this.toolImplementations = {};

        // Module state
        this.quotes = [];
        this.stockList = [];
        this.queryResults = {};

        // Cache settings
        this.cacheStockList = true;
        this.stockListTTL = 3600; // 1 hour
        this.stockListCache = null;
        this.stockListCacheTime = null;

        console.log('Quote Calculator module constructed');
    }

    /**
     * Initialize the module
     * Called by module system after construction
     */
    async initialize() {
        console.log('🔧 Quote Calculator initializing...');

        try {
            // Call parent initialization (creates UI structure)
            await super.initialize();

            // Load and register tools (Tasks 3)
            await this.loadTools();
            this.bindToolImplementations();
            this.registerToolsWithAI();

            // Apply module colors
            this.applyModuleColors();

            // Load CSS stylesheet
            this.loadStylesheet();

            // Initialize sub-tabs (Task 4)
            this.initializeSubTabs();

            console.log('✅ Quote Calculator ready');
        } catch (error) {
            console.error('❌ Quote Calculator initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load module CSS stylesheet
     */
    loadStylesheet() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'external/modules/quote-calculator/quote-calculator.css';
        link.id = 'quote-calculator-styles';
        document.head.appendChild(link);
        console.log('[OK] Quote Calculator stylesheet loaded');
    }

    /**
     * Apply module color scheme
     * Uses pastel orange (#ffb347) for printing/manufacturing theme
     */
    applyModuleColors() {
        // CRITICAL: Safe null-checking for manifest colors
        // Manifest is loaded asynchronously, may not be available immediately
        const primaryColor = (this.manifest && this.manifest.colors && this.manifest.colors.primary)
            ? this.manifest.colors.primary
            : (this.manifest && this.manifest.color)
                ? this.manifest.color
                : '#ffb347'; // Fallback to pastel orange

        // Apply to module header if exists
        const moduleHeader = document.querySelector('.module-header');
        if (moduleHeader) {
            moduleHeader.style.borderBottomColor = primaryColor;
        }

        // Apply to buttons
        const buttons = document.querySelectorAll('.btn-primary');
        buttons.forEach(button => {
            button.style.backgroundColor = primaryColor;
            button.style.borderColor = primaryColor;
        });
    }

    /**
     * Initialize all sub-tabs
     * Creates UI for each calculator type
     */
    initializeSubTabs() {
        console.log('Initializing sub-tabs...');

        // Business Cards tab (Task 4 - NEXT)
        this.initializeBusinessCards();

        // Placeholder for other tabs
        this.initializePlaceholder('flyers', 'Flyers', 'fas fa-file-alt', 'Requires database export');
        this.initializePlaceholder('perfect-bound-books', 'Perfect Bound Books', 'fas fa-book', 'Requires database export');
        this.initializePlaceholder('booklets', 'Booklets', 'fas fa-book-open', 'Requires database export');
        this.initializeAdvancedPlaceholder();
    }

    /**
     * Initialize Business Cards calculator tab
     * TASK 4: Create Business Cards UI
     */
    initializeBusinessCards() {
        const container = document.getElementById(`${this.moduleId}-subtab-business-cards`);
        if (!container) {
            console.warn(`Business Cards container not found: ${this.moduleId}-subtab-business-cards`);
            return;
        }

        const primaryColor = (this.config && this.config.colors && this.config.colors.primary) ? this.config.colors.primary : '#ffb347';

        container.innerHTML = `
            <div class="module-header" style="border-bottom-color: ${primaryColor};">
                <div class="module-header-left">
                    <h2 class="module-title">
                        <i class="fas fa-id-card" style="color: ${primaryColor};"></i>
                        Business Card Quote Calculator
                    </h2>
                    <p class="module-description">Calculate accurate quotes for business card printing (1,000 - 10,000 cards)</p>
                </div>
            </div>
            
            <div class="dashboard-card">
                <div class="dashboard-card-header">
                    <i class="fas fa-edit dashboard-card-icon" style="color: ${primaryColor};"></i>
                    <span class="dashboard-card-title">Quote Configuration</span>
                </div>
                <div class="dashboard-card-content">
                    <form id="bc-form" onsubmit="return false;">
                        <div class="form-group">
                            <label for="bc-qty">Quantity</label>
                            <select id="bc-qty" class="form-control">
                                <option value="1000">1,000 cards</option>
                                <option value="2000">2,000 cards</option>
                                <option value="3000">3,000 cards</option>
                                <option value="5000" selected>5,000 cards</option>
                                <option value="10000">10,000 cards</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="bc-stock">Paper Stock</label>
                            <select id="bc-stock" class="form-control">
                                <option value="350gsm_satin" selected>350gsm Satin (Most Popular)</option>
                                <option value="400gsm_uncoated">400gsm Uncoated</option>
                                <option value="350gsm_gloss">350gsm Gloss</option>
                            </select>
                            <small class="form-text">Satin finish provides premium look and feel</small>
                        </div>
                        
                        <div class="form-group">
                            <label for="bc-finish">Cellophane Finish</label>
                            <select id="bc-finish" class="form-control">
                                <option value="none">No Cellophane</option>
                                <option value="gloss_cello" selected>Gloss Cellophane (Recommended)</option>
                                <option value="matt_cello">Matt Cellophane</option>
                            </select>
                            <small class="form-text">Cellophane adds durability and professional finish</small>
                        </div>
                        
                        <div class="form-group">
                            <label for="bc-print-sides">Printing</label>
                            <select id="bc-print-sides" class="form-control">
                                <option value="double" selected>Double Sided</option>
                                <option value="single">Single Sided</option>
                            </select>
                        </div>
                        
                        <button type="button" class="btn btn-primary" 
                            style="background: ${primaryColor}; border-color: ${primaryColor}; width: 100%;"
                            onclick="window.ModuleRegistry['quote-calculator'].calculateQuote()">
                            <i class="fas fa-calculator"></i> Calculate Quote
                        </button>
                    </form>
                </div>
            </div>
            
            <div class="dashboard-card" style="margin-top: 20px;">
                <div class="dashboard-card-header">
                    <i class="fas fa-file-invoice-dollar dashboard-card-icon" style="color: ${primaryColor};"></i>
                    <span class="dashboard-card-title">Quote Result</span>
                </div>
                <div class="dashboard-card-content" id="bc-result">
                    <p class="text-secondary" style="text-align: center; padding: 40px 20px;">
                        <i class="fas fa-arrow-up" style="font-size: 24px; color: ${primaryColor}; margin-bottom: 10px;"></i><br>
                        Configure options above and click "Calculate Quote" to see pricing
                    </p>
                </div>
            </div>
        `;

        console.log('✓ Business Cards UI initialized');
    }

    /**
     * Create placeholder for tabs requiring database
     */
    initializePlaceholder(tabId, title, icon, message) {
        const container = document.getElementById(`${this.moduleId}-subtab-${tabId}`);
        if (!container) return;

        const primaryColor = (this.config && this.config.colors && this.config.colors.primary) ? this.config.colors.primary : '#ffb347';

        container.innerHTML = `
            <div class="module-header" style="border-bottom-color: ${primaryColor};">
                <h2 class="module-title">
                    <i class="${icon}" style="color: ${primaryColor};"></i>
                    ${title}
                </h2>
            </div>
            
            <div class="dashboard-card">
                <div class="dashboard-card-content" style="text-align: center; padding: 60px 20px;">
                    <i class="fas fa-database" style="font-size: 48px; color: #ccc; margin-bottom: 20px;"></i>
                    <h3 style="color: #666;">Coming Soon</h3>
                    <p class="text-secondary">${message}</p>
                    <p class="text-secondary" style="margin-top: 15px;">
                        <small>Database export from In_House_SQL SQL Server required</small>
                    </p>
                </div>
            </div>
        `;
    }

    /**
     * Create placeholder for Advanced/Query Library tab
     */
    initializeAdvancedPlaceholder() {
        const container = document.getElementById(`${this.moduleId}-subtab-advanced`);
        if (!container) return;

        const primaryColor = (this.config && this.config.colors && this.config.colors.primary) ? this.config.colors.primary : '#ffb347';

        container.innerHTML = `
            <div class="module-header" style="border-bottom-color: ${primaryColor};">
                <h2 class="module-title">
                    <i class="fas fa-chart-line" style="color: ${primaryColor};"></i>
                    Query Library
                </h2>
            </div>
            
            <div class="dashboard-card">
                <div class="dashboard-card-content" style="text-align: center; padding: 60px 20px;">
                    <i class="fas fa-database" style="font-size: 48px; color: #ccc; margin-bottom: 20px;"></i>
                    <h3 style="color: #666;">50+ Pre-built Queries</h3>
                    <p class="text-secondary">Historical quote analysis, customer analytics, production planning</p>
                    <p class="text-secondary" style="margin-top: 15px;">
                        <small>Database export from In_House_SQL SQL Server required</small>
                    </p>
                </div>
            </div>
        `;
    }

    // ==================== TASK 5: Calculator Methods ====================

    /**
     * Calculate business card quote (UI button handler)
     * Reads values from form and calls API
     */
    async calculateQuote() {
        console.log('Calculating business card quote...');

        const params = {
            quantity: parseInt(document.getElementById('bc-qty').value),
            stock_type: document.getElementById('bc-stock').value,
            finish: document.getElementById('bc-finish').value,
            print_sides: document.getElementById('bc-print-sides').value
        };

        const resultDiv = document.getElementById('bc-result');
        const primaryColor = (this.config && this.config.colors && this.config.colors.primary) ? this.config.colors.primary : '#ffb347';

        // Show loading state
        resultDiv.innerHTML = `
            <div style="text-align: center; padding: 40px 20px;">
                <div class="loading-spinner" style="color: ${primaryColor};">
                    <i class="fas fa-spinner fa-spin" style="font-size: 32px;"></i>
                    <p style="margin-top: 15px;">Calculating quote...</p>
                </div>
            </div>
        `;

        try {
            const result = await this.calculateBusinessCards(params);

            if (result.success) {
                this.renderQuoteResult(result, resultDiv);
            } else {
                throw new Error(result.error || 'Quote calculation failed');
            }
        } catch (error) {
            console.error('Quote calculation error:', error);
            resultDiv.innerHTML = `
                <div class="error-message" style="padding: 20px; background: #fee; border-left: 4px solid #e55; color: #c33;">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Error:</strong> ${error.message}
                    <p style="margin-top: 10px; font-size: 0.9em;">
                        Please check that the Flask server is running and the calculator endpoint is available.
                    </p>
                </div>
            `;
        }
    }

    /**
     * Render quote result in UI
     */
    renderQuoteResult(result, container) {
        const primaryColor = (this.config && this.config.colors && this.config.colors.primary) ? this.config.colors.primary : '#ffb347';

        container.innerHTML = `
            <div class="quote-result" style="border-left: 4px solid ${primaryColor}; padding: 20px; background: #f9f9f9; border-radius: 4px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid ${primaryColor};">
                    <div>
                        <div style="color: #666; font-size: 0.9em; margin-bottom: 5px;">Total (inc GST)</div>
                        <div style="font-size: 2em; font-weight: bold; color: #333;">$${result.total_inc_gst.toFixed(2)}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #666; font-size: 0.9em; margin-bottom: 5px;">Per Card</div>
                        <div style="font-size: 1.5em; font-weight: bold; color: ${primaryColor};">$${result.price_per_unit.toFixed(3)}</div>
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; gap: 10px; padding: 12px; background: white; border-radius: 4px; margin-bottom: 20px;">
                    <i class="fas fa-clock" style="color: ${primaryColor}; font-size: 1.2em;"></i>
                    <span style="color: #666;"><strong>Turnaround:</strong> ${result.turnaround}</span>
                </div>
                
                ${result.breakdown ? `
                <div>
                    <h4 style="margin-bottom: 10px; color: #333;">Cost Breakdown</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid #ddd;">
                            <td style="padding: 8px; color: #666;">Subtotal</td>
                            <td style="padding: 8px; text-align: right; font-weight: bold;">$${result.breakdown.subtotal.toFixed(2)}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #ddd;">
                            <td style="padding: 8px; color: #666;">GST (10%)</td>
                            <td style="padding: 8px; text-align: right; font-weight: bold;">$${result.breakdown.gst.toFixed(2)}</td>
                        </tr>
                        <tr style="background: #f5f5f5;">
                            <td style="padding: 12px; color: #333; font-weight: bold;">Total</td>
                            <td style="padding: 12px; text-align: right; font-weight: bold; color: ${primaryColor}; font-size: 1.2em;">$${result.total_inc_gst.toFixed(2)}</td>
                        </tr>
                    </table>
                </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Calculate business card quote (AI tool version)
     * Called by AI when user requests business card quote
     * 
     * @param {Object} params - Quote parameters
     * @param {number} params.quantity - Number of cards (1000-10000)
     * @param {string} params.stock_type - Stock type (350gsm_satin, etc.)
     * @param {string} params.finish - Finish type (none, gloss_cello, matt_cello)
     * @param {string} params.print_sides - single or double
     * @returns {Promise<Object>} Quote result
     */
    async calculateBusinessCards(params) {
        console.log('API call: calculateBusinessCards', params);

        const response = await fetch(`${this.apiBaseUrl}/business-cards`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    }

    // ==================== TASK 3: Tool System ====================

    /**
     * Load tool definitions from manifest
     */
    async loadTools() {
        console.log('Loading tool definitions...');

        try {
            const response = await fetch('/external/modules/quote-calculator/tools/manifest.json');
            if (!response.ok) {
                throw new Error(`Failed to load tools manifest: ${response.statusText}`);
            }

            this.tools = await response.json();
            console.log(`✓ Loaded ${this.tools.totalTools} tool definitions`);
        } catch (error) {
            console.error('Failed to load tools:', error);
            this.tools = { totalTools: 0, categories: [] };
        }
    }

    /**
     * Bind tool names to implementation methods
     */
    bindToolImplementations() {
        console.log('Binding tool implementations...');

        this.toolImplementations = {
            // Calculator tools (7)
            'quote_calc_business_cards': this.calculateBusinessCards.bind(this),
            'quote_calc_flyers': this.calculateFlyers.bind(this),
            'quote_calc_perfect_bound_books': this.calculatePerfectBoundBooks.bind(this),
            'quote_calc_booklets': this.calculateBooklets.bind(this),
            'quote_calc_letterheads': this.calculateLetterheads.bind(this),
            'quote_get_stock_list': this.getStockList.bind(this),
            'quote_get_calculator_requirements': this.getCalculatorRequirements.bind(this)

            // Query library tools (15) - TODO: Task 14
            // Smart bundled tools (5) - TODO: Task 15
        };

        console.log(`✓ Bound ${Object.keys(this.toolImplementations).length} tool implementations`);
    }

    /**
     * Register tools with global AI system
     */
    registerToolsWithAI() {
        console.log('Registering tools with AI...');

        if (!window.ModuleToolRegistry) {
            window.ModuleToolRegistry = {};
            console.log('Created ModuleToolRegistry');
        }

        let registeredCount = 0;
        Object.entries(this.toolImplementations).forEach(([name, impl]) => {
            window.ModuleToolRegistry[name] = impl;
            registeredCount++;
        });

        console.log(`✓ Registered ${registeredCount} tools with AI system`);
    }

    // ==================== Placeholder Calculator Methods ====================

    async calculateFlyers(params) {
        throw new Error('Flyers calculator requires database export (not yet implemented)');
    }

    async calculatePerfectBoundBooks(params) {
        throw new Error('Perfect Bound Books calculator requires database export (not yet implemented)');
    }

    async calculateBooklets(params) {
        throw new Error('Booklets calculator requires database export (not yet implemented)');
    }

    async calculateLetterheads(params) {
        throw new Error('Letterheads calculator requires database export (not yet implemented)');
    }

    async getStockList(params) {
        // TODO: Implement when database available
        return {
            success: true,
            stocks: [
                { stock_id: 1, stock_name: '350gsm Satin', category: 'digital' },
                { stock_id: 2, stock_name: '400gsm Uncoated', category: 'digital' },
                { stock_id: 3, stock_name: '350gsm Gloss', category: 'digital' }
            ],
            total: 3
        };
    }

    async getCalculatorRequirements(params) {
        // Hardcoded requirements for business cards
        if (params.calculator === 'business_cards') {
            return {
                success: true,
                calculator: 'business_cards',
                requirements: {
                    quantity_range: { min: 1000, max: 10000, suggested: [1000, 2000, 5000, 10000] },
                    valid_stocks: ['350gsm_satin', '400gsm_uncoated', '350gsm_gloss'],
                    valid_finishes: ['none', 'gloss_cello', 'matt_cello'],
                    valid_print_sides: ['single', 'double'],
                    required_parameters: ['quantity'],
                    optional_parameters: ['stock_type', 'finish', 'print_sides']
                }
            };
        }

        throw new Error(`Requirements not available for calculator: ${params.calculator}`);
    }
}

// ==================== Module Registration ====================

// Ensure ModuleRegistry exists
if (!window.ModuleRegistry) {
    window.ModuleRegistry = {};
    console.log('Created ModuleRegistry');
}

// Register this module with initialization
window.ModuleRegistry['quote_calculator'] = {
    class: QuoteCalculatorModule,
    instance: null,

    init: async function () {
        console.log('🔧 Initializing Quote Calculator...');

        // Check if sidebar element exists
        const sidebar = document.getElementById('quote_calculator-sidebar');
        if (!sidebar) {
            console.error('❌ Quote Calculator sidebar element not found!');
            return;
        }

        // Initialize sub-tabs
        const subTabs = sidebar.querySelectorAll('.module-sub-tab');
        const tabContents = sidebar.querySelectorAll('.module-sub-tab-content');

        subTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                subTabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));

                tab.classList.add('active');
                const tabId = tab.dataset.tab;
                const content = document.getElementById(tabId);
                if (content) {
                    content.classList.add('active');
                }
            });
        });

        // Set up calculator button handlers
        this.setupBusinessCardsCalculator();
        this.setupFlyersCalculator();
        this.setupBookletsCalculator();
        this.setupPerfectBoundCalculator();
        this.setupCorfluteCalculator();
        this.setupStockListLoader();

        console.log('✅ Quote Calculator ready');
    },

    setupBusinessCardsCalculator: function () {
        const btn = document.getElementById('bc-calculate-btn');
        if (btn) {
            btn.addEventListener('click', async () => {
                const quantity = parseInt(document.getElementById('bc-quantity').value);
                const stock = document.getElementById('bc-stock').value;
                const sides = document.getElementById('bc-sides').value;
                const finish = document.getElementById('bc-finish').value;

                const resultDiv = document.getElementById('bc-result');
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Calculating...</div>';

                try {
                    const result = await fetch('/api/calculator/business-cards', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            quantity,
                            stock_type: stock,
                            sided: sides,
                            finish: finish
                        })
                    }).then(r => r.json());

                    resultDiv.innerHTML = `
                        <h4><i class="fas fa-check-circle"></i> Quote Result</h4>
                        <div class="result-details">
                            <div class="result-row">
                                <span class="result-label">Total Price:</span>
                                <span class="result-value">$${result.total_price || 'N/A'}</span>
                            </div>
                            <div class="result-row">
                                <span class="result-label">Per Card:</span>
                                <span class="result-value">$${result.per_unit_price || 'N/A'}</span>
                            </div>
                            <div class="result-row">
                                <span class="result-label">Turnaround:</span>
                                <span class="result-value">${result.turnaround_days || 'N/A'} days</span>
                            </div>
                        </div>
                    `;
                } catch (error) {
                    resultDiv.innerHTML = `<div class="error"><i class="fas fa-exclamation-circle"></i> Error: ${error.message}</div>`;
                }
            });
        }
    },

    setupFlyersCalculator: function () {
        const btn = document.getElementById('fl-calculate-btn');
        if (btn) {
            btn.addEventListener('click', () => {
                const resultDiv = document.getElementById('fl-result');
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<div class="info"><i class="fas fa-info-circle"></i> Flyers calculator coming soon...</div>';
            });
        }
    },

    setupBookletsCalculator: function () {
        const btn = document.getElementById('bk-calculate-btn');
        if (btn) {
            btn.addEventListener('click', () => {
                const resultDiv = document.getElementById('bk-result');
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<div class="info"><i class="fas fa-info-circle"></i> Booklets calculator coming soon...</div>';
            });
        }
    },

    setupPerfectBoundCalculator: function () {
        const btn = document.getElementById('pb-calculate-btn');
        if (btn) {
            btn.addEventListener('click', () => {
                const resultDiv = document.getElementById('pb-result');
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<div class="info"><i class="fas fa-info-circle"></i> Perfect Bound Books calculator coming soon...</div>';
            });
        }
    },

    setupCorfluteCalculator: function () {
        const btn = document.getElementById('cs-calculate-btn');
        if (btn) {
            btn.addEventListener('click', () => {
                const resultDiv = document.getElementById('cs-result');
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<div class="info"><i class="fas fa-info-circle"></i> Corflute Signs calculator coming soon...</div>';
            });
        }
    },

    setupStockListLoader: function () {
        const btn = document.getElementById('stocks-load-btn');
        if (btn) {
            btn.addEventListener('click', () => {
                const resultDiv = document.getElementById('stocks-result');
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<div class="info"><i class="fas fa-info-circle"></i> Stock list coming soon...</div>';
            });
        }
    }
};

console.log('✓ Quote Calculator module registered as quote_calculator');
