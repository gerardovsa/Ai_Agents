
// ==================== WOOCOMMERCE DIRECT API FUNCTIONS ====================

// Global variable to store current orders for filtering
let currentWooCommerceOrders = [];

async function wcLoadOrders() {
    const contentDiv = document.getElementById('wc-orders-content');
    contentDiv.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);"><i class="fas fa-spinner fa-spin" style="font-size: 32px;"></i><br><br>Loading orders...</div>';

    try {
        console.log(' Fetching WooCommerce orders via direct API...');

        // Get active filter
        const activeFilter = document.querySelector('.wc-filter-btn.active');
        const statusFilter = activeFilter ? activeFilter.dataset.filter : 'any';

        // Get limit from dropdown
        const limitSelect = document.getElementById('wc-orders-limit');
        const limit = limitSelect ? limitSelect.value : 50;

        // Direct programmatic API call (no AI)
        const response = await fetch(`${API_BASE_URL}/api/woocommerce/orders?status=${statusFilter}&limit=${limit}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.success && data.orders) {
            currentWooCommerceOrders = data.orders; // Store for filtering

            if (data.orders.length > 0) {
                renderOrdersTable(data.orders, contentDiv);
                updateOrderCount(data.orders.length, statusFilter);
                showNotification(`Loaded ${data.orders.length} orders`, 'success');
            } else {
                contentDiv.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);">No orders found matching the criteria.</div>';
                updateOrderCount(0, statusFilter);
                showNotification('No orders found', 'info');
            }
        } else {
            throw new Error(data.error || 'Failed to load orders');
        }

    } catch (error) {
        console.error(' Failed to load orders:', error);
        contentDiv.innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div style="color: var(--accent-error); font-size: 48px; margin-bottom: var(--space-3);">[WARN]</div>
                    <p style="color: var(--text-secondary);">Failed to load orders: ${error.message}</p>
                    <p style="color: var(--text-muted); font-size: 12px; margin-top: var(--space-2);">Make sure WooCommerce API is configured and the backend is running.</p>
                    <button class="btn btn-primary" onclick="wcLoadOrders()" style="margin-top: var(--space-4); padding: 10px 20px; background: var(--accent-primary); border: none; border-radius: 6px; color: white; font-weight: 600; cursor: pointer;">
                        <i class="fas fa-redo"></i> Try Again
                    </button>
                </div>
                `;
        showNotification('Failed to load orders', 'error');
    }
}

function wcFilterOrders(status) {
    console.log(`[SEARCH] Filtering orders by status: ${status}`);

    // Update active filter button
    document.querySelectorAll('.wc-filter-btn').forEach(btn => {
        if (btn.dataset.filter === status) {
            btn.classList.add('active');
            btn.style.background = 'var(--accent-primary)';
            btn.style.color = 'white';
        } else {
            btn.classList.remove('active');
            btn.style.background = 'var(--bg-tertiary)';
            btn.style.color = 'var(--text-secondary)';
        }
    });

    // Reload orders with new filter
    wcLoadOrders();
}

function updateOrderCount(count, status) {
    const countText = document.getElementById('wc-orders-count-text');
    if (countText) {
        const statusLabel = status === 'any' ? 'All' : status.charAt(0).toUpperCase() + status.slice(1);
        countText.textContent = `Showing ${count} ${statusLabel} order${count !== 1 ? 's' : ''}`;
    }
}

function createPrintLabel(order) {
    // Create print label - shipping address and items only (no customer name)
    const parts = [];

    // Shipping address (without customer name)
    if (order.shipping_address) {
        parts.push(order.shipping_address.replace(/\n/g, '\n'));
    }

    // Contact info
    const contactParts = [];
    if (order.customer_phone) contactParts.push(` ${order.customer_phone}`);
    if (order.customer_email) contactParts.push(` ${order.customer_email}`);
    if (contactParts.length > 0) {
        parts.push(contactParts.join('\n'));
    }

    // Items with quantities (no SKU codes)
    if (order.line_items && order.line_items.length > 0) {
        parts.push('\n--- ITEMS ---');
        order.line_items.forEach(item => {
            parts.push(`${item.quantity}x ${item.name}`);
        });
    }

    return parts.join('\n');
}

function renderOrdersTable(orders, container) {
    console.log(`[CHART] Rendering ${orders.length} orders in Tabulator table`);

    // Destroy existing Tabulator table if present
    if (window.wooOrdersTable) {
        window.wooOrdersTable.destroy();
    }

    // Clear container and reset display style for Tabulator
    container.style.display = 'block';
    container.style.alignItems = '';
    container.style.justifyContent = '';
    container.innerHTML = '';

    // Currency symbols map (matching Google Apps Script)
    const currencySymbols = {
        'USD': '$', 'CAD': 'C$', 'AUD': 'A$', 'EUR': '€', 'GBP': '£',
        'NZD': 'NZ$', 'SGD': 'S$', 'JPY': '¥', 'CHF': 'CHF'
    };

    // Status color map - Brighter text on colored backgrounds
    const statusColors = {
        'pending': { bg: '#f59e0b', text: '#fffbeb' },
        'processing': { bg: '#3b82f6', text: '#eff6ff' },
        'completed': { bg: '#10b981', text: '#ecfdf5' },
        'on-hold': { bg: '#6b7280', text: '#f9fafb' },
        'cancelled': { bg: '#ef4444', text: '#fef2f2' },
        'refunded': { bg: '#8b5cf6', text: '#f5f3ff' },
        'failed': { bg: '#dc2626', text: '#fef2f2' }
    };

    // Initialize Tabulator table
    window.wooOrdersTable = new Tabulator(container, {
        data: orders,
        layout: "fitDataStretch",
        pagination: "local",
        paginationSize: 25,
        paginationSizeSelector: [10, 25, 50, 100],
        movableColumns: true,
        resizableColumns: true,
        placeholder: "No orders found",
        selectable: true,
        selectableRangeMode: "click",
        columns: [
            {
                formatter: "rowSelection",
                titleFormatter: "rowSelection",
                hozAlign: "center",
                headerSort: false,
                width: 40,
                frozen: true,
                cellClick: function (e, cell) {
                    cell.getRow().toggleSelect();
                }
            },
            {
                title: "#",
                formatter: "rownum",
                hozAlign: "center",
                width: 50,
                frozen: true
            },
            {
                title: "Tag",
                field: "_tag",
                width: 60,
                hozAlign: "center",
                headerSort: false,
                frozen: true,
                formatter: function (cell) {
                    const rowId = cell.getRow().getData().id;
                    const tags = JSON.parse(localStorage.getItem('wc_order_tags') || '{}');
                    const tag = tags[rowId] || 'none';
                    const colors = {
                        green: '#10b981',
                        orange: '#f59e0b',
                        red: '#ef4444',
                        none: '#6b7280'
                    };
                    return `<button onclick="wcToggleTag(${rowId}, event)" style="background: ${colors[tag]}; border: none; padding: 6px; border-radius: 4px; cursor: pointer; width: 40px; height: 28px;" title="Tag: ${tag}"><i class="fas fa-tag" style="color: white; font-size: 12px;"></i></button>`;
                }
            },
            {
                title: "Order ID",
                field: "id",
                width: 120,
                headerSort: true,
                headerFilter: "input",
                headerFilterPlaceholder: "Search...",
                formatter: function (cell) {
                    return `<span style="font-weight: 600; color: #ffffff;">#${cell.getValue()}</span>`;
                }
            },
            {
                title: "Date",
                field: "date_created",
                width: 120,
                headerSort: true,
                sorter: "datetime",
                headerFilter: "input",
                headerFilterPlaceholder: "Search...",
                formatter: function (cell) {
                    const date = new Date(cell.getValue());
                    return `<span style="color: #ffffff;">${date.toLocaleDateString('en-GB', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric'
                    }).replace(/\//g, '-')}</span>`;
                }
            },
            {
                title: "Time",
                field: "date_created",
                width: 100,
                headerSort: false,
                headerFilter: "input",
                headerFilterPlaceholder: "Search...",
                formatter: function (cell) {
                    const date = new Date(cell.getValue());
                    return `<span style="color: #ffffff;">${date.toLocaleTimeString('en-GB', {
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit'
                    })}</span>`;
                }
            },
            {
                title: "Status",
                field: "status",
                width: 130,
                headerSort: true,
                headerFilter: "input",
                headerFilterPlaceholder: "Search...",
                formatter: function (cell) {
                    const status = cell.getValue();
                    const colors = statusColors[status.toLowerCase()] || { bg: '#6b7280', text: '#f9fafb' };
                    return `<span style="display: inline-block; padding: 6px 14px; border-radius: 12px; font-size: 12px; font-weight: 700; background: ${colors.bg}; color: ${colors.text}; text-transform: capitalize; letter-spacing: 0.3px;">
                    ${status.replace('-', ' ')}
                </span>`;
                }
            },
            {
                title: "Customer Name",
                field: "customer_name",
                width: 180,
                headerSort: true,
                headerFilter: "input",
                headerFilterPlaceholder: "Search...",
                formatter: function (cell) {
                    const name = cell.getValue();
                    return name ? `<div style="font-weight: 600; color: #ffffff;">${name}</div>` : '<span style="color: #ffffff;">N/A</span>';
                }
            },
            {
                title: "Shipping Address",
                field: "shipping_address",
                width: 250,
                headerSort: false,
                headerFilter: "input",
                headerFilterPlaceholder: "Search...",
                formatter: function (cell) {
                    const address = cell.getValue();
                    if (!address) return '<div style="color: #ffffff;">No address</div>';

                    const addressLines = address.split('\n').filter(line => line.trim());
                    return `<div style="line-height: 1.5; color: #ffffff;">${addressLines.join('<br>')}</div>`;
                }
            },
            {
                title: "Contact",
                field: "customer_email",
                width: 200,
                headerSort: false,
                headerFilter: "input",
                headerFilterPlaceholder: "Search...",
                formatter: function (cell) {
                    const row = cell.getRow().getData();
                    return `
                <div>
                    <div style="margin-bottom: 4px; color: #ffffff;">
                        <i class="fas fa-envelope" style="margin-right: 4px; color: #ffffff;"></i>${row.customer_email || 'N/A'}
                    </div>
                    <div style="color: #ffffff;">
                        <i class="fas fa-phone" style="margin-right: 4px; color: #ffffff;"></i>${row.customer_phone || 'N/A'}
                    </div>
                </div>
                `;
                }
            },
            {
                title: "Items",
                field: "line_items",
                width: 250,
                headerSort: false,
                headerFilter: "input",
                headerFilterPlaceholder: "Search...",
                formatter: function (cell) {
                    const items = cell.getValue();
                    if (!items || items.length === 0) return '<span style="color: #ffffff;">No items</span>';

                    const itemsList = items.map(item => {
                        const sku = item.sku ? ` - ${item.sku}` : '';
                        return `${item.quantity} x ${item.name}${sku}`;
                    }).join('<br>');

                    return `<div style="line-height: 1.6; color: #ffffff;">${itemsList}</div>`;
                }
            },
            {
                title: "Print Label",
                field: "id",
                width: 300,
                headerSort: false,
                headerFilter: "input",
                headerFilterPlaceholder: "Search...",
                headerFilterFunc: function (headerValue, rowValue, rowData, filterParams) {
                    const printLabel = createPrintLabel(rowData);
                    return printLabel.toLowerCase().includes(headerValue.toLowerCase());
                },
                formatter: function (cell) {
                    const row = cell.getRow().getData();
                    const printLabel = createPrintLabel(row);
                    return `<div style="line-height: 1.5; white-space: pre-wrap; font-family: monospace; background: var(--bg-primary); border-left: 3px solid var(--woocommerce-purple); padding: 8px; max-width: 300px; color: #ffffff;">${printLabel.replace(/\n/g, '<br>')}</div>`;
                }
            },
            {
                title: "Total",
                field: "total",
                width: 130,
                headerSort: true,
                hozAlign: "right",
                sorter: "number",
                headerFilter: "input",
                headerFilterPlaceholder: "Search...",
                formatter: function (cell) {
                    const row = cell.getRow().getData();
                    const currencySymbol = currencySymbols[row.currency] || row.currency;
                    return `<span style="font-weight: 600; color: #ffffff;">${currencySymbol}${parseFloat(row.total).toFixed(2)} (${row.currency})</span>`;
                }
            },
            {
                title: "Actions",
                field: "id",
                width: 140,
                headerSort: false,
                hozAlign: "center",
                formatter: function (cell) {
                    const orderId = cell.getValue();
                    return `
                    <button onclick="wcViewOrder(${orderId})" style="padding: 6px 12px; background: var(--woocommerce-purple); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px; margin-right: 4px;" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button onclick="wcPrintOrder(${orderId})" style="padding: 6px 12px; background: var(--accent-success); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px;" title="Print Label">
                        <i class="fas fa-print"></i>
                    </button>
                    `;
                }
            }
        ]
    });

    // Row selection event
    window.wooOrdersTable.on("rowSelectionChanged", function(data, rows) {
        const count = rows.length;
        console.log(`Selected ${count} orders`);
        // Update bulk action button
        const bulkBtn = document.getElementById('wc-bulk-actions-btn');
        if (bulkBtn) {
            bulkBtn.innerHTML = `<i class="fas fa-tasks"></i> Bulk Actions${count > 0 ? ' (' + count + ')' : ''}`;
            bulkBtn.disabled = count === 0;
            bulkBtn.style.opacity = count > 0 ? '1' : '0.5';
        }
        // Update selection counter
        const counter = document.getElementById('wc-selection-count');
        if (counter) {
            counter.textContent = `${count} selected`;
            counter.style.color = count > 0 ? 'var(--accent-primary)' : 'var(--text-secondary)';
            counter.style.fontWeight = count > 0 ? '600' : '400';
        }
    });

    // Double-click cell to show popup
    window.wooOrdersTable.on("cellDblClick", function(e, cell) {
        const field = cell.getColumn().getField();
        const value = cell.getValue();
        const rowData = cell.getRow().getData();
        wcShowCellPopup(field, value, rowData);
    });

    // Load existing tags
    wcApplyRowTags();

    console.log('Tabulator table initialized successfully');
}

function wcViewOrder(orderId) {
    console.log(`?� View order details for: ${orderId}`);
    showNotification(`Opening order #${orderId}...`, 'info');
    // TODO: Implement order detail modal or redirect
}

function wcPrintOrder(orderId) {
    console.log(`?� Print shipping label for order: ${orderId}`);
    showNotification(`Preparing print label for order #${orderId}...`, 'info');
    // TODO: Implement print label generation matching Google Sheets format
}

function wcExportOrders() {
    console.log('[LOAD] Export orders to Excel');

    if (window.wooOrdersTable) {
        // Use Tabulator's built-in XLSX export
        window.wooOrdersTable.download("xlsx", "woocommerce-orders.xlsx", {
            sheetName: "WooCommerce Orders"
        });
        showNotification('Orders exported to Excel successfully', 'success');
    } else {
        showNotification('No orders loaded to export', 'error');
    }
}

// Row Tagging System
function wcToggleTag(orderId, event) {
    event.stopPropagation();
    const tags = JSON.parse(localStorage.getItem('wc_order_tags') || '{}');
    const current = tags[orderId] || 'none';
    const cycle = { none: 'green', green: 'orange', orange: 'red', red: 'none' };
    tags[orderId] = cycle[current];
    localStorage.setItem('wc_order_tags', JSON.stringify(tags));
    
    // Refresh table to show new tag
    if (window.wooOrdersTable) {
        window.wooOrdersTable.redraw();
        wcApplyRowTags();
    }
}

function wcApplyRowTags() {
    const tags = JSON.parse(localStorage.getItem('wc_order_tags') || '{}');
    if (!window.wooOrdersTable) return;
    
    window.wooOrdersTable.getRows().forEach(row => {
        const orderId = row.getData().id;
        const tag = tags[orderId];
        const element = row.getElement();
        
        // Remove all tag classes
        element.classList.remove('tagged-row-green', 'tagged-row-orange', 'tagged-row-red');
        
        // Add new tag class
        if (tag && tag !== 'none') {
            element.classList.add(`tagged-row-${tag}`);
        }
    });
}

// Cell Popup Modal
function wcShowCellPopup(field, value, rowData) {
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'cell-popup';
    modal.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 80%;
        max-width: 800px;
        max-height: 80vh;
        background: var(--bg-secondary);
        border: 2px solid var(--border-default);
        border-radius: 12px;
        padding: var(--space-5);
        z-index: 10000;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        overflow-y: auto;
    `;

    // Format value for display
    let displayValue = value;
    if (typeof value === 'object') {
        displayValue = JSON.stringify(value, null, 2);
    } else if (field === 'line_items' && Array.isArray(value)) {
        displayValue = value.map(item => `${item.quantity} x ${item.name} - ${item.sku || 'N/A'}`).join('\n');
    }

    modal.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); border-bottom: 2px solid var(--border-default); padding-bottom: var(--space-3);">
            <h3 style="color: var(--text-primary); font-size: 18px; font-weight: 600;">
                <i class="fas fa-info-circle" style="color: var(--accent-primary); margin-right: 8px;"></i>
                Order #${rowData.id} - ${field.replace(/_/g, ' ').toUpperCase()}
            </h3>
            <button onclick="wcCloseCellPopup()" style="background: transparent; border: none; color: var(--text-secondary); cursor: pointer; font-size: 24px; padding: 0; width: 32px; height: 32px;">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div style="background: var(--bg-primary); border: 1px solid var(--border-default); border-radius: 8px; padding: var(--space-4); white-space: pre-wrap; font-family: monospace; color: var(--text-primary); font-size: 14px; line-height: 1.6; max-height: 60vh; overflow-y: auto;">
            ${displayValue || 'No data'}
        </div>
        <div style="margin-top: var(--space-4); display: flex; gap: var(--space-2);">
            <button onclick="navigator.clipboard.writeText('${String(displayValue).replace(/'/g, "\\'")}'')" style="padding: 10px 20px; background: var(--accent-primary); border: none; border-radius: 6px; color: white; font-weight: 600; cursor: pointer;">
                <i class="fas fa-copy"></i> Copy
            </button>
            <button onclick="wcCloseCellPopup()" style="padding: 10px 20px; background: var(--bg-tertiary); border: none; border-radius: 6px; color: var(--text-primary); font-weight: 600; cursor: pointer;">
                Close
            </button>
        </div>
    `;

    // Add backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'cell-popup-backdrop';
    backdrop.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        z-index: 9999;
    `;
    backdrop.onclick = wcCloseCellPopup;

    document.body.appendChild(backdrop);
    document.body.appendChild(modal);
}

function wcCloseCellPopup() {
    document.querySelectorAll('.cell-popup, .cell-popup-backdrop').forEach(el => el.remove());
}

// Bulk Actions
function wcShowBulkActions() {
    if (!window.wooOrdersTable) return;
    const selected = window.wooOrdersTable.getSelectedRows();
    if (selected.length === 0) {
        showNotification('No orders selected', 'info');
        return;
    }

    const orderIds = selected.map(row => row.getData().id).join(', ');
    const actions = [
        { label: 'Export Selected', icon: 'fa-download', action: 'export' },
        { label: 'Mark as Processing', icon: 'fa-cog', action: 'processing' },
        { label: 'Mark as Completed', icon: 'fa-check', action: 'completed' },
        { label: 'Tag Green', icon: 'fa-tag', action: 'tag-green' },
        { label: 'Tag Orange', icon: 'fa-tag', action: 'tag-orange' },
        { label: 'Tag Red', icon: 'fa-tag', action: 'tag-red' }
    ];

    let html = `<div style="margin-bottom: var(--space-3); padding: var(--space-3); background: var(--bg-tertiary); border-radius: 6px; color: var(--text-primary);">
        <strong>${selected.length} orders selected:</strong> #${orderIds}
    </div><div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-2);">`;

    actions.forEach(act => {
        html += `<button onclick="wcExecuteBulkAction('${act.action}')" style="padding: 12px; background: var(--bg-hover); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary); cursor: pointer; text-align: left; transition: all 0.2s;" onmouseover="this.style.borderColor='var(--accent-primary)'" onmouseout="this.style.borderColor='var(--border-default)'">
            <i class="fas ${act.icon}" style="margin-right: 8px; color: var(--accent-primary);"></i>${act.label}
        </button>`;
    });

    html += `</div>`;
    
    showModalDialog('Bulk Actions', html);
}

function wcExecuteBulkAction(action) {
    if (!window.wooOrdersTable) return;
    const selected = window.wooOrdersTable.getSelectedRows();
    const tags = JSON.parse(localStorage.getItem('wc_order_tags') || '{}');

    selected.forEach(row => {
        const orderId = row.getData().id;
        
        if (action.startsWith('tag-')) {
            const color = action.replace('tag-', '');
            tags[orderId] = color;
        } else if (action === 'export') {
            // Export selected rows
            window.wooOrdersTable.download("xlsx", "woocommerce-selected-orders.xlsx", {
                sheetName: "Selected Orders"
            }, "selected");
        }
    });

    if (action.startsWith('tag-')) {
        localStorage.setItem('wc_order_tags', JSON.stringify(tags));
        window.wooOrdersTable.redraw();
        wcApplyRowTags();
        showNotification(`Tagged ${selected.length} orders`, 'success');
    }

    closeModal();
}

// Column Visibility Toggle
function wcToggleColumn(field) {
    if (!window.wooOrdersTable) return;
    const column = window.wooOrdersTable.getColumn(field);
    if (column) {
        if (column.isVisible()) {
            column.hide();
            showNotification(`${field} column hidden`, 'info');
        } else {
            column.show();
            showNotification(`${field} column shown`, 'info');
        }
    }
}

// Clear All Tags
function wcClearAllTags() {
    if (confirm('Clear all order tags?')) {
        localStorage.removeItem('wc_order_tags');
        if (window.wooOrdersTable) {
            window.wooOrdersTable.redraw();
            wcApplyRowTags();
        }
        showNotification('All tags cleared', 'success');
    }
}

// Font size control for WooCommerce table
let wcTableFontSize = 13; // Default font size

function wcChangeFontSize(delta) {
    wcTableFontSize += delta;

    // Limit font size between 10px and 20px
    if (wcTableFontSize < 10) wcTableFontSize = 10;
    if (wcTableFontSize > 20) wcTableFontSize = 20;

    // Update CSS variable
    document.documentElement.style.setProperty('--wc-table-font-size', `${wcTableFontSize}px`);

    // Update display
    const display = document.getElementById('wc-font-size-display');
    if (display) {
        display.textContent = `${wcTableFontSize}px`;
    }

    // Redraw table to apply new font size
    if (window.wooOrdersTable) {
        window.wooOrdersTable.redraw(true);
    }

    console.log(` Font size changed to ${wcTableFontSize}px`);
}

async function wcLoadProducts() {
    const contentDiv = document.getElementById('wc-products-content');
    contentDiv.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);"><i class="fas fa-spinner fa-spin" style="font-size: 32px;"></i><br><br>Loading products...</div>';

    try {
        const message = 'Get my WooCommerce products with details including name, SKU, price, stock status, and categories. Display in a formatted table.';

        // Use agent 1 for WooCommerce queries
        const response = await fetch(`${API_BASE_URL}/api/agent/agent/1/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                context: { tab: 'woocommerce', action: 'load_products', tools_enabled: true }
            })
        });

        const data = await response.json();
        contentDiv.innerHTML = `<div style="padding: var(--space-4); background: var(--bg-secondary); border-radius: 8px;">${renderBasicMarkdown(data.response)}</div>`;
        showNotification('Products loaded successfully', 'success');
    } catch (error) {
        console.error(' Failed to load products:', error);
        contentDiv.innerHTML = `<div style="text-align: center; padding: 40px; color: var(--accent-error);">Failed to load products: ${error.message}</div>`;
        showNotification('Failed to load products', 'error');
    }
}

async function wcLoadCustomers() {
    const contentDiv = document.getElementById('wc-customers-content');
    contentDiv.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);"><i class="fas fa-spinner fa-spin" style="font-size: 32px;"></i><br><br>Loading customers...</div>';

    try {
        const message = 'Get my WooCommerce customers with details including name, email, total orders, and total spent. Display in a formatted table.';

        // Use agent 1 for WooCommerce queries
        const response = await fetch(`${API_BASE_URL}/api/agent/agent/1/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                context: { tab: 'woocommerce', action: 'load_customers', tools_enabled: true }
            })
        });

        const data = await response.json();
        contentDiv.innerHTML = `<div style="padding: var(--space-4); background: var(--bg-secondary); border-radius: 8px;">${renderBasicMarkdown(data.response)}</div>`;
        showNotification('Customers loaded successfully', 'success');
    } catch (error) {
        console.error(' Failed to load customers:', error);
        contentDiv.innerHTML = `<div style="text-align: center; padding: 40px; color: var(--accent-error);">Failed to load customers: ${error.message}</div>`;
        showNotification('Failed to load customers', 'error');
    }
}

async function wcLoadFinance() {
    const contentDiv = document.getElementById('wc-finance-content');
    contentDiv.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);"><i class="fas fa-spinner fa-spin" style="font-size: 32px;"></i><br><br>Loading financial data...</div>';

    try {
        const message = 'Get my WooCommerce refunds and coupons with details. Show active coupons and recent refunds in a formatted display.';

        // Use agent 1 for WooCommerce queries
        const response = await fetch(`${API_BASE_URL}/api/agent/agent/1/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                context: { tab: 'woocommerce', action: 'load_finance', tools_enabled: true }
            })
        });

        const data = await response.json();
        contentDiv.innerHTML = `<div style="padding: var(--space-4); background: var(--bg-secondary); border-radius: 8px;">${renderBasicMarkdown(data.response)}</div>`;
        showNotification('Financial data loaded successfully', 'success');
    } catch (error) {
        console.error(' Failed to load financial data:', error);
        contentDiv.innerHTML = `<div style="text-align: center; padding: 40px; color: var(--accent-error);">Failed to load financial data: ${error.message}</div>`;
        showNotification('Failed to load financial data', 'error');
    }
}

async function wcLoadReports() {
    console.log('[CHART] Loading WooCommerce analytics...');

    // Hide loading state
    const loadingDiv = document.getElementById('wc-reports-loading');
    if (loadingDiv) loadingDiv.style.display = 'none';

    // Show loading indicators in stat cards
    document.getElementById('wc-stat-sales').innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    document.getElementById('wc-stat-orders').innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    document.getElementById('wc-stat-avg').innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    document.getElementById('wc-stat-customers').innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    try {
        // Get period from dropdown
        const period = parseInt(document.getElementById('wc-report-period').value);

        // Fetch orders for analysis
        const response = await fetch(`${API_BASE_URL}/api/woocommerce/orders?status=any&limit=200`);
        const data = await response.json();

        if (!data.success || !data.orders) {
            throw new Error('Failed to fetch orders');
        }

        const orders = data.orders;
        console.log(`Fetched ${orders.length} orders for analysis`);

        // Calculate statistics
        const stats = wcCalculateStats(orders, period);

        // Update stat cards
        document.getElementById('wc-stat-sales').textContent = `$${stats.totalSales.toFixed(2)}`;
        document.getElementById('wc-stat-orders').textContent = stats.totalOrders;
        document.getElementById('wc-stat-avg').textContent = `$${stats.avgOrderValue.toFixed(2)}`;
        document.getElementById('wc-stat-customers').textContent = stats.uniqueCustomers;

        // Generate charts
        wcCreateSalesTrendChart(orders, period);
        wcCreateStatusPieChart(orders);
        wcCreateTopProductsChart(orders);
        wcCreateDayRevenueChart(orders);
        wcCreateValueDistChart(orders);
        wcCreateStatusTrendChart(orders, period);

        showNotification('Analytics generated successfully', 'success');

    } catch (error) {
        console.error(' Failed to generate reports:', error);
        showNotification('Failed to generate analytics', 'error');
    }
}

// Calculate statistics from orders
function wcCalculateStats(orders, period) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - period);

    const filteredOrders = orders.filter(order => {
        const orderDate = new Date(order.date_created);
        return orderDate >= cutoffDate;
    });

    const totalSales = filteredOrders.reduce((sum, order) => sum + parseFloat(order.total || 0), 0);
    const totalOrders = filteredOrders.length;
    const avgOrderValue = totalOrders > 0 ? totalSales / totalOrders : 0;

    const uniqueCustomers = new Set(filteredOrders.map(order => order.customer_email)).size;

    return { totalSales, totalOrders, avgOrderValue, uniqueCustomers };
}

// Chart 1: Sales Trend Over Time
function wcCreateSalesTrendChart(orders, period) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - period);

    const filteredOrders = orders.filter(order => {
        const orderDate = new Date(order.date_created);
        return orderDate >= cutoffDate;
    });

    // Group by date
    const salesByDate = {};
    filteredOrders.forEach(order => {
        const date = new Date(order.date_created).toISOString().split('T')[0];
        if (!salesByDate[date]) {
            salesByDate[date] = { sales: 0, count: 0 };
        }
        salesByDate[date].sales += parseFloat(order.total || 0);
        salesByDate[date].count += 1;
    });

    const dates = Object.keys(salesByDate).sort();
    const sales = dates.map(date => salesByDate[date].sales);
    const counts = dates.map(date => salesByDate[date].count);

    const trace1 = {
        x: dates,
        y: sales,
        name: 'Sales ($)',
        type: 'scatter',
        mode: 'lines+markers',
        marker: { color: '#8b5cf6', size: 8 },
        line: { width: 3, color: '#8b5cf6' }
    };

    const trace2 = {
        x: dates,
        y: counts,
        name: 'Orders',
        type: 'scatter',
        mode: 'lines+markers',
        marker: { color: '#10b981', size: 8 },
        line: { width: 3, color: '#10b981' },
        yaxis: 'y2'
    };

    const layout = {
        paper_bgcolor: '#161b22',
        plot_bgcolor: '#0d1117',
        font: { color: '#c9d1d9', size: 12 },
        xaxis: {
            title: 'Date',
            gridcolor: '#30363d',
            showgrid: true
        },
        yaxis: {
            title: 'Sales ($)',
            gridcolor: '#30363d',
            showgrid: true
        },
        yaxis2: {
            title: 'Number of Orders',
            overlaying: 'y',
            side: 'right',
            showgrid: false
        },
        margin: { t: 30, b: 50, l: 60, r: 60 },
        hovermode: 'x unified',
        showlegend: true,
        legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(22, 27, 34, 0.8)' }
    };

    Plotly.newPlot('wc-chart-sales-trend', [trace1, trace2], layout, { responsive: true });
}

// Chart 2: Order Status Distribution
function wcCreateStatusPieChart(orders) {
    const statusCounts = {};
    orders.forEach(order => {
        const status = order.status || 'unknown';
        statusCounts[status] = (statusCounts[status] || 0) + 1;
    });

    const colors = {
        'pending': '#f59e0b',
        'processing': '#3b82f6',
        'completed': '#10b981',
        'on-hold': '#6b7280',
        'cancelled': '#ef4444',
        'refunded': '#8b5cf6',
        'failed': '#dc2626'
    };

    const trace = {
        labels: Object.keys(statusCounts).map(s => s.replace('-', ' ').toUpperCase()),
        values: Object.values(statusCounts),
        type: 'pie',
        marker: {
            colors: Object.keys(statusCounts).map(s => colors[s] || '#6b7280')
        },
        textinfo: 'label+percent',
        textfont: { size: 14 },
        hoverinfo: 'label+value+percent'
    };

    const layout = {
        paper_bgcolor: '#161b22',
        plot_bgcolor: '#0d1117',
        font: { color: '#c9d1d9', size: 12 },
        margin: { t: 30, b: 30, l: 30, r: 30 },
        showlegend: true,
        legend: { x: 1.05, y: 0.5, bgcolor: 'rgba(22, 27, 34, 0.8)' }
    };

    Plotly.newPlot('wc-chart-status-pie', [trace], layout, { responsive: true });
}

// Chart 3: Top Selling Products
function wcCreateTopProductsChart(orders) {
    const productSales = {};

    orders.forEach(order => {
        if (order.line_items) {
            order.line_items.forEach(item => {
                const name = item.name || 'Unknown Product';
                if (!productSales[name]) {
                    productSales[name] = { quantity: 0, revenue: 0 };
                }
                productSales[name].quantity += item.quantity || 0;
                productSales[name].revenue += (item.quantity || 0) * parseFloat(order.total || 0) / order.line_items.length;
            });
        }
    });

    const sortedProducts = Object.entries(productSales)
        .sort((a, b) => b[1].quantity - a[1].quantity)
        .slice(0, 10);

    const trace = {
        x: sortedProducts.map(([name]) => name),
        y: sortedProducts.map(([, data]) => data.quantity),
        type: 'bar',
        marker: {
            color: '#8b5cf6',
            line: { color: '#c4b5fd', width: 1.5 }
        },
        text: sortedProducts.map(([, data]) => `${data.quantity} units`),
        textposition: 'outside',
        hovertemplate: '<b>%{x}</b><br>Quantity: %{y}<br>Revenue: $%{customdata:.2f}<extra></extra>',
        customdata: sortedProducts.map(([, data]) => data.revenue)
    };

    const layout = {
        paper_bgcolor: '#161b22',
        plot_bgcolor: '#0d1117',
        font: { color: '#c9d1d9', size: 12 },
        xaxis: {
            title: 'Product',
            gridcolor: '#30363d',
            tickangle: -45
        },
        yaxis: {
            title: 'Units Sold',
            gridcolor: '#30363d',
            showgrid: true
        },
        margin: { t: 30, b: 120, l: 60, r: 30 }
    };

    Plotly.newPlot('wc-chart-top-products', [trace], layout, { responsive: true });
}

// Chart 4: Revenue by Day of Week
function wcCreateDayRevenueChart(orders) {
    const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const revenueByDay = Array(7).fill(0);
    const countsByDay = Array(7).fill(0);

    orders.forEach(order => {
        const date = new Date(order.date_created);
        const dayOfWeek = date.getDay();
        revenueByDay[dayOfWeek] += parseFloat(order.total || 0);
        countsByDay[dayOfWeek] += 1;
    });

    const trace = {
        x: daysOfWeek,
        y: revenueByDay,
        type: 'bar',
        marker: {
            color: ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4'],
            line: { color: '#ffffff', width: 1.5 }
        },
        text: revenueByDay.map(rev => `$${rev.toFixed(2)}`),
        textposition: 'outside',
        hovertemplate: '<b>%{x}</b><br>Revenue: $%{y:.2f}<br>Orders: %{customdata}<extra></extra>',
        customdata: countsByDay
    };

    const layout = {
        paper_bgcolor: '#161b22',
        plot_bgcolor: '#0d1117',
        font: { color: '#c9d1d9', size: 12 },
        xaxis: {
            title: 'Day of Week',
            gridcolor: '#30363d'
        },
        yaxis: {
            title: 'Total Revenue ($)',
            gridcolor: '#30363d',
            showgrid: true
        },
        margin: { t: 30, b: 60, l: 60, r: 30 }
    };

    Plotly.newPlot('wc-chart-day-revenue', [trace], layout, { responsive: true });
}

// Chart 5: Order Value Distribution
function wcCreateValueDistChart(orders) {
    const orderValues = orders.map(order => parseFloat(order.total || 0));

    const trace = {
        x: orderValues,
        type: 'histogram',
        nbinsx: 30,
        marker: {
            color: '#3b82f6',
            line: { color: '#60a5fa', width: 1 }
        },
        hovertemplate: 'Order Value: $%{x:.2f}<br>Count: %{y}<extra></extra>'
    };

    const layout = {
        paper_bgcolor: '#161b22',
        plot_bgcolor: '#0d1117',
        font: { color: '#c9d1d9', size: 12 },
        xaxis: {
            title: 'Order Value ($)',
            gridcolor: '#30363d'
        },
        yaxis: {
            title: 'Number of Orders',
            gridcolor: '#30363d',
            showgrid: true
        },
        margin: { t: 30, b: 60, l: 60, r: 30 },
        bargap: 0.05
    };

    Plotly.newPlot('wc-chart-value-dist', [trace], layout, { responsive: true });
}

// Chart 6: Orders by Status Over Time
function wcCreateStatusTrendChart(orders, period) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - period);

    const filteredOrders = orders.filter(order => {
        const orderDate = new Date(order.date_created);
        return orderDate >= cutoffDate;
    });

    // Group by date and status
    const statusByDate = {};
    filteredOrders.forEach(order => {
        const date = new Date(order.date_created).toISOString().split('T')[0];
        const status = order.status || 'unknown';

        if (!statusByDate[date]) {
            statusByDate[date] = {};
        }
        statusByDate[date][status] = (statusByDate[date][status] || 0) + 1;
    });

    const dates = Object.keys(statusByDate).sort();
    const statuses = ['completed', 'processing', 'pending', 'cancelled', 'on-hold'];
    const colors = {
        'completed': '#10b981',
        'processing': '#3b82f6',
        'pending': '#f59e0b',
        'cancelled': '#ef4444',
        'on-hold': '#6b7280'
    };

    const traces = statuses.map(status => ({
        x: dates,
        y: dates.map(date => statusByDate[date][status] || 0),
        name: status.replace('-', ' ').toUpperCase(),
        type: 'scatter',
        mode: 'lines+markers',
        stackgroup: 'one',
        marker: { color: colors[status], size: 6 },
        line: { width: 2, color: colors[status] }
    }));

    const layout = {
        paper_bgcolor: '#161b22',
        plot_bgcolor: '#0d1117',
        font: { color: '#c9d1d9', size: 12 },
        xaxis: {
            title: 'Date',
            gridcolor: '#30363d'
        },
        yaxis: {
            title: 'Number of Orders',
            gridcolor: '#30363d',
            showgrid: true
        },
        margin: { t: 30, b: 60, l: 60, r: 30 },
        hovermode: 'x unified',
        showlegend: true,
        legend: { x: 1.05, y: 0.5, bgcolor: 'rgba(22, 27, 34, 0.8)' }
    };

    Plotly.newPlot('wc-chart-status-trend', traces, layout, { responsive: true });
}

async function wcExportReport() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/woocommerce/orders?status=any&limit=200`);

        const data = await response.json();
        contentDiv.innerHTML = `<div style="padding: var(--space-4); background: var(--bg-secondary); border-radius: 8px;">${renderBasicMarkdown(data.response)}</div>`;
        showNotification('Reports generated successfully', 'success');
    } catch (error) {
        console.error(' Failed to generate reports:', error);
        contentDiv.innerHTML = `<div style="text-align: center; padding: 40px; color: var(--accent-error);">Failed to generate reports: ${error.message}</div>`;
        showNotification('Failed to load reports', 'error');
    }
}

async function wcLoadSettings() {
    const contentDiv = document.getElementById('wc-settings-content');
    contentDiv.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);"><i class="fas fa-spinner fa-spin" style="font-size: 32px;"></i><br><br>Loading settings...</div>';

    try {
        const message = 'Get my WooCommerce store settings including shipping zones, payment gateways, and system status. Display in an organized format.';

        // Use agent 1 for WooCommerce queries
        const response = await fetch(`${API_BASE_URL}/api/agent/agent/1/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                context: { tab: 'woocommerce', action: 'load_settings', tools_enabled: true }
            })
        });

        const data = await response.json();
        contentDiv.innerHTML = `<div style="padding: var(--space-4); background: var(--bg-secondary); border-radius: 8px;">${renderBasicMarkdown(data.response)}</div>`;
        showNotification('Settings loaded successfully', 'success');
    } catch (error) {
        console.error(' Failed to load settings:', error);
        contentDiv.innerHTML = `<div style="text-align: center; padding: 40px; color: var(--accent-error);">Failed to load settings: ${error.message}</div>`;
        showNotification('Failed to load settings', 'error');
    }
}

// Action button functions
function wcCreateOrder() { showNotification('Order creation dialog coming soon...', 'info'); }
function wcRefreshOrders() {
    event?.preventDefault();
    wcLoadOrders();
    return false;
}
function wcCreateProduct() { showNotification('Product creation dialog coming soon...', 'info'); }
function wcManageCategories() { showNotification('Category management coming soon...', 'info'); }
function wcCreateCustomer() { showNotification('Customer creation dialog coming soon...', 'info'); }
function wcExportCustomers() { showNotification('Export functionality coming soon...', 'info'); }
function wcCreateCoupon() { showNotification('Coupon creation dialog coming soon...', 'info'); }
function wcProcessRefund() { showNotification('Refund processing dialog coming soon...', 'info'); }
function wcExportReport() { showNotification('Report export coming soon...', 'info'); }
function wcSaveSettings() { showNotification('Settings save functionality coming soon...', 'info'); }
