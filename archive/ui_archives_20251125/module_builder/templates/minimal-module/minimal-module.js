/**
 * FILE: UI/module_builder/templates/minimal-module/minimal-module.js
 * PURPOSE: Minimal module template with basic UI and essential features only
 * 
 * TEMPLATE TYPE: Starter/Lightweight
 * USE CASE: Simple modules with minimal UI requirements, quick prototypes
 * 
 * FEATURES:
 * - Single view layout
 * - Basic buttons and cards
 * - Toast notifications
 * - Modal integration (alerts/confirmations)
 * - Minimal styling
 * 
 * DEPENDENCIES:
 * - ui-components.js (required)
 * - design-tokens.css (required)
 * - modal-system.js (optional)
 * 
 * EXPORTS:
 * - MinimalModule class - Main module class
 * 
 * LAST MODIFIED: 2025-11-12 - Initial template creation
 */

class MinimalModule {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.data = [];

        if (!this.container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        this.init();
    }

    /**
     * Initialize the module
     */
    init() {
        this.render();
        this.attachEventListeners();
        this.loadData();
    }

    /**
     * Render the module UI
     */
    render() {
        this.container.innerHTML = `
            <div class="minimal-module">
                <!-- Header -->
                <div class="module-header">
                    <h2 class="module-title">
                        <span class="module-icon">📄</span>
                        Minimal Module
                    </h2>
                    <div class="header-actions">
                        <button class="btn-icon" id="refreshBtn" title="Refresh">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"/>
                                <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"/>
                            </svg>
                        </button>
                        <button class="btn-icon" id="settingsBtn" title="Settings">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z"/>
                                <path d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319z"/>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <!-- Content -->
                <div class="module-content">
                    <!-- Stats Cards -->
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-label">Total Items</div>
                            <div class="stat-value" id="totalItems">0</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Active</div>
                            <div class="stat-value" id="activeItems">0</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Pending</div>
                            <div class="stat-value" id="pendingItems">0</div>
                        </div>
                    </div>
                    
                    <!-- Actions -->
                    <div class="action-bar">
                        <button class="btn btn-primary" id="addItemBtn">
                            <span>➕</span> Add Item
                        </button>
                        <button class="btn btn-secondary" id="clearAllBtn">
                            <span>🗑️</span> Clear All
                        </button>
                    </div>
                    
                    <!-- Data List -->
                    <div class="data-section">
                        <h3 class="section-title">Items</h3>
                        <div id="itemsList" class="items-list">
                            <div class="empty-state">
                                <div class="empty-icon">📭</div>
                                <div class="empty-text">No items yet</div>
                                <button class="btn btn-secondary btn-sm" onclick="this.closest('.minimal-module').querySelector('#addItemBtn').click()">
                                    Add your first item
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="module-footer">
                    <span class="footer-text">Minimal Module Template v1.0.0</span>
                </div>
            </div>
        `;
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const refreshBtn = this.container.querySelector('#refreshBtn');
        const settingsBtn = this.container.querySelector('#settingsBtn');
        const addItemBtn = this.container.querySelector('#addItemBtn');
        const clearAllBtn = this.container.querySelector('#clearAllBtn');

        refreshBtn?.addEventListener('click', () => this.handleRefresh());
        settingsBtn?.addEventListener('click', () => this.handleSettings());
        addItemBtn?.addEventListener('click', () => this.handleAddItem());
        clearAllBtn?.addEventListener('click', () => this.handleClearAll());
    }

    /**
     * Load data (mock data for template)
     */
    async loadData() {
        const loader = UIComponents.showLoading({
            title: 'Loading',
            message: 'Please wait...'
        });

        try {
            // Simulate API call
            await this.delay(1000);

            // Mock data
            this.data = [
                { id: 1, title: 'Sample Item 1', status: 'active', created: new Date().toISOString() },
                { id: 2, title: 'Sample Item 2', status: 'pending', created: new Date().toISOString() }
            ];

            this.updateUI();
            loader.hide();

            UIComponents.showToast('Data loaded successfully', 'success');
        } catch (error) {
            loader.hide();
            UIComponents.showAlert({
                title: 'Error',
                message: `Failed to load data: ${error.message}`,
                variant: 'error'
            });
        }
    }

    /**
     * Update UI with current data
     */
    updateUI() {
        // Update stats
        const totalItems = this.data.length;
        const activeItems = this.data.filter(item => item.status === 'active').length;
        const pendingItems = this.data.filter(item => item.status === 'pending').length;

        this.container.querySelector('#totalItems').textContent = totalItems;
        this.container.querySelector('#activeItems').textContent = activeItems;
        this.container.querySelector('#pendingItems').textContent = pendingItems;

        // Update list
        const itemsList = this.container.querySelector('#itemsList');

        if (this.data.length === 0) {
            itemsList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📭</div>
                    <div class="empty-text">No items yet</div>
                    <button class="btn btn-secondary btn-sm" onclick="document.getElementById('addItemBtn').click()">
                        Add your first item
                    </button>
                </div>
            `;
            return;
        }

        itemsList.innerHTML = this.data.map(item => `
            <div class="item-card" data-id="${item.id}">
                <div class="item-header">
                    <h4 class="item-title">${this.escapeHtml(item.title)}</h4>
                    <span class="item-status status-${item.status}">${item.status}</span>
                </div>
                <div class="item-meta">
                    Created: ${new Date(item.created).toLocaleDateString()}
                </div>
                <div class="item-actions">
                    <button class="btn-icon" onclick="minimalModule.handleEditItem(${item.id})" title="Edit">
                        ✏️
                    </button>
                    <button class="btn-icon" onclick="minimalModule.handleDeleteItem(${item.id})" title="Delete">
                        🗑️
                    </button>
                </div>
            </div>
        `).join('');
    }

    /**
     * Handle refresh
     */
    async handleRefresh() {
        UIComponents.showToast('Refreshing...', 'info');
        await this.loadData();
    }

    /**
     * Handle settings
     */
    handleSettings() {
        UIComponents.showAlert({
            title: 'Settings',
            message: 'Settings panel would open here. Customize this to show your module-specific settings.',
            variant: 'info'
        });
    }

    /**
     * Handle add item
     */
    handleAddItem() {
        UIComponents.showForm({
            title: 'Add New Item',
            size: 'md',
            fields: [
                {
                    name: 'title',
                    label: 'Title',
                    type: 'text',
                    required: true,
                    placeholder: 'Enter item title'
                },
                {
                    name: 'status',
                    label: 'Status',
                    type: 'select',
                    required: true,
                    options: [
                        { value: 'active', label: 'Active' },
                        { value: 'pending', label: 'Pending' }
                    ]
                }
            ],
            onSubmit: (formData) => {
                const newItem = {
                    id: this.data.length + 1,
                    title: formData.title,
                    status: formData.status,
                    created: new Date().toISOString()
                };

                this.data.push(newItem);
                this.updateUI();

                UIComponents.showToast('Item added successfully', 'success');
            }
        });
    }

    /**
     * Handle edit item
     */
    handleEditItem(itemId) {
        const item = this.data.find(i => i.id === itemId);
        if (!item) return;

        UIComponents.showForm({
            title: 'Edit Item',
            size: 'md',
            fields: [
                {
                    name: 'title',
                    label: 'Title',
                    type: 'text',
                    required: true,
                    value: item.title
                },
                {
                    name: 'status',
                    label: 'Status',
                    type: 'select',
                    required: true,
                    value: item.status,
                    options: [
                        { value: 'active', label: 'Active' },
                        { value: 'pending', label: 'Pending' }
                    ]
                }
            ],
            onSubmit: (formData) => {
                item.title = formData.title;
                item.status = formData.status;
                this.updateUI();

                UIComponents.showToast('Item updated successfully', 'success');
            }
        });
    }

    /**
     * Handle delete item
     */
    handleDeleteItem(itemId) {
        const item = this.data.find(i => i.id === itemId);
        if (!item) return;

        UIComponents.showConfirmation({
            title: 'Delete Item?',
            message: `Are you sure you want to delete "${item.title}"? This action cannot be undone.`,
            variant: 'danger',
            confirmLabel: 'Delete',
            onConfirm: () => {
                this.data = this.data.filter(i => i.id !== itemId);
                this.updateUI();
                UIComponents.showToast('Item deleted successfully', 'success');
            }
        });
    }

    /**
     * Handle clear all
     */
    handleClearAll() {
        if (this.data.length === 0) {
            UIComponents.showToast('No items to clear', 'info');
            return;
        }

        UIComponents.showConfirmation({
            title: 'Clear All Items?',
            message: `Are you sure you want to delete all ${this.data.length} items? This action cannot be undone.`,
            variant: 'danger',
            confirmLabel: 'Clear All',
            onConfirm: () => {
                this.data = [];
                this.updateUI();
                UIComponents.showToast('All items cleared', 'success');
            }
        });
    }

    /**
     * Utility: Delay helper
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Utility: Escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global instance (optional - can also be instantiated manually)
let minimalModule;

// Auto-initialize if container exists
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('minimalModuleContainer');
    if (container) {
        minimalModule = new MinimalModule('minimalModuleContainer');
    }
});
